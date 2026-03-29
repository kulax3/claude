#!/usr/bin/env python3
"""
Keep & Tasks Knowledge Base
============================
Google Keep / Google Tasks を4段階AIパイプラインで分析し、
ローカルSQLiteナレッジベースに変換するCLIツール。

使い方:
  python main.py init                        -- DBを初期化
  python main.py sync tasks                  -- Google Tasksを同期
  python main.py sync keep --mode takeout --takeout-dir ~/Downloads/Takeout/Keep
  python main.py sync keep --mode gkeepapi --email you@gmail.com --token YOUR_TOKEN
  python main.py process                     -- AIパイプラインを実行
  python main.py search "機械学習の勉強メモ"  -- 自然言語検索
  python main.py export --format json        -- エクスポート
  python main.py stats                       -- 統計表示
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

# Ensure the package root is in sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from auth.claude_auth import get_claude_api_key
from config import DB_PATH
from export.exporter import export_csv, export_json, export_zip
from pipeline.stage1_entity import extract_entities
from pipeline.stage2_vision import analyze_images
from pipeline.stage3_tagging import generate_tags
from pipeline.stage4_categorize import categorize
from search.search import fts_search, semantic_search
from sources.google_keep import fetch_keep_notes
from sources.google_tasks import fetch_all_tasks
from storage.database import (
    get_all_items,
    get_stats,
    init_db,
    set_job_status,
    update_pipeline_result,
    upsert_item,
)

console = Console()


# ─────────────────────────────────────────────
# CLI root
# ─────────────────────────────────────────────

@click.group()
def cli():
    """Google Keep & Tasks → AI ナレッジベース変換ツール"""


# ─────────────────────────────────────────────
# init
# ─────────────────────────────────────────────

@cli.command()
def init():
    """データベースを初期化します。"""
    init_db()
    console.print(f"[green]✓[/green] DB を初期化しました: {DB_PATH}")


# ─────────────────────────────────────────────
# sync
# ─────────────────────────────────────────────

@cli.group()
def sync():
    """データソースからアイテムを取得・保存します。"""


@sync.command("tasks")
def sync_tasks():
    """Google Tasks を同期します（公式API）。"""
    init_db()
    console.print("[bold]Google Tasks[/bold] を同期中...")
    try:
        items = fetch_all_tasks()
    except FileNotFoundError as e:
        console.print(f"[red]エラー:[/red] {e}")
        return
    except Exception as e:
        console.print(f"[red]認証エラー:[/red] {e}")
        return

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task(f"保存中 ({len(items)} 件)...", total=len(items))
        for item in items:
            metadata = {
                "task_list_id": item.task_list_id,
                "task_list_title": item.task_list_title,
                "status": item.status,
                "due": item.due,
                "completed_at": item.completed_at,
                "parent_id": item.parent_id,
                "links": item.links,
            }
            upsert_item(
                source=item.source,
                source_id=item.source_id,
                title=item.title,
                full_text=item.full_text,
                metadata=metadata,
                created_at=item.updated,
                updated_at=item.updated,
            )
            progress.advance(task)

    console.print(f"[green]✓[/green] {len(items)} 件を保存しました。")


@sync.command("keep")
@click.option("--mode", type=click.Choice(["takeout", "gkeepapi"]), default="takeout",
              show_default=True, help="取得モード")
@click.option("--takeout-dir", default="", help="Google Takeout の Keep ディレクトリパス")
@click.option("--email", default="", help="Googleアカウントのメールアドレス（gkeepapi用）")
@click.option("--token", default="", help="gkeepapi マスタートークン")
def sync_keep(mode, takeout_dir, email, token):
    """Google Keep を同期します。"""
    init_db()
    console.print(f"[bold]Google Keep[/bold] を同期中（モード: {mode}）...")
    try:
        notes = fetch_keep_notes(
            mode=mode,
            email=email,
            master_token=token,
            takeout_dir=takeout_dir,
        )
    except (FileNotFoundError, ValueError, ImportError) as e:
        console.print(f"[red]エラー:[/red] {e}")
        return

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task(f"保存中 ({len(notes)} 件)...", total=len(notes))
        for note in notes:
            metadata = {
                "labels": note.labels,
                "color": note.color,
                "is_pinned": note.is_pinned,
                "is_archived": note.is_archived,
                "has_images": len(note.images) > 0,
            }
            upsert_item(
                source=note.source,
                source_id=note.source_id,
                title=note.title,
                full_text=note.full_text,
                metadata=metadata,
                created_at=note.created_at,
                updated_at=note.updated_at,
            )
            progress.advance(task)

    console.print(f"[green]✓[/green] {len(notes)} 件を保存しました。")


# ─────────────────────────────────────────────
# process  (run AI pipeline)
# ─────────────────────────────────────────────

@cli.command()
@click.option("--skip-vision", is_flag=True, help="Vision分析をスキップ（コスト削減）")
def process(skip_vision):
    """4段階AIパイプラインを実行します。"""
    init_db()
    try:
        api_key = get_claude_api_key()
    except EnvironmentError as e:
        console.print(f"[red]エラー:[/red] {e}")
        return

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    rows = get_all_items()
    console.print(f"[bold]{len(rows)} 件[/bold] のアイテムを処理します...")

    # Reload source objects for vision stage (need raw bytes)
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("AIパイプライン処理中...", total=len(rows))

        for row in rows:
            source = row["source"]
            source_id = row["source_id"]

            # Build a lightweight proxy object with full_text
            class _Proxy:
                def __init__(self, r):
                    self.source = r["source"]
                    self.source_id = r["source_id"]
                    self.full_text = r["full_text"]
                    self.images = []  # images not stored in DB; re-fetch if needed

            item = _Proxy(row)

            try:
                # Stage 1
                set_job_status(source, source_id, 1, "pending")
                entities = extract_entities(item)
                set_job_status(source, source_id, 1, "done")

                # Stage 2 (Keep only, skip if flag set)
                vision_result = None
                if not skip_vision and source == "google_keep":
                    set_job_status(source, source_id, 2, "pending")
                    from pipeline.stage2_vision import VisionResult
                    vision_result = VisionResult()  # no raw images in DB pass
                    set_job_status(source, source_id, 2, "done")
                else:
                    from pipeline.stage2_vision import VisionResult
                    vision_result = VisionResult()

                # Stage 3
                set_job_status(source, source_id, 3, "pending")
                tags = generate_tags(item, entities, vision_result, client)
                set_job_status(source, source_id, 3, "done")

                # Stage 4
                set_job_status(source, source_id, 4, "pending")
                cats = categorize(item, tags, client)
                set_job_status(source, source_id, 4, "done")

                # Persist
                update_pipeline_result(
                    source=source,
                    source_id=source_id,
                    entities=dataclasses.asdict(entities),
                    vision=dataclasses.asdict(vision_result),
                    tags=tags.tags,
                    summary=tags.summary,
                    sentiment=tags.sentiment,
                    categories=cats.categories,
                )
            except Exception as e:
                set_job_status(source, source_id, 0, "error", str(e))
                console.print(f"[yellow]警告:[/yellow] {source_id} の処理中にエラー: {e}")

            progress.advance(task)

    console.print("[green]✓[/green] パイプライン処理が完了しました。")


# ─────────────────────────────────────────────
# search
# ─────────────────────────────────────────────

@cli.command()
@click.argument("query")
@click.option("--semantic", is_flag=True, help="Claudeによる意味検索を使用")
@click.option("--limit", default=10, show_default=True)
def search(query, semantic, limit):
    """ナレッジベースを検索します。"""
    if semantic:
        try:
            api_key = get_claude_api_key()
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            results = semantic_search(query, client, limit=limit)
        except Exception as e:
            console.print(f"[yellow]意味検索失敗、キーワード検索にフォールバック:[/yellow] {e}")
            results = fts_search(query, limit=limit)
    else:
        results = fts_search(query, limit=limit)

    if not results:
        console.print("[yellow]結果なし[/yellow]")
        return

    table = Table(title=f'検索結果: "{query}" ({len(results)} 件)')
    table.add_column("ソース", style="cyan", width=12)
    table.add_column("タイトル", style="bold", width=30)
    table.add_column("要約", width=40)
    table.add_column("カテゴリ", width=15)

    for r in results:
        cats = ", ".join(c["name"] for c in r.categories[:1]) if r.categories else "-"
        table.add_row(r.source.replace("google_", ""), r.title or "(無題)",
                      r.summary or r.snippet or "-", cats)

    console.print(table)


# ─────────────────────────────────────────────
# export
# ─────────────────────────────────────────────

@cli.command()
@click.option("--format", "fmt", type=click.Choice(["json", "csv", "zip"]),
              default="json", show_default=True)
@click.option("--output", default="", help="出力ファイルパス（省略時は自動生成）")
def export(fmt, output):
    """ナレッジベースをエクスポートします。"""
    if not output:
        output = f"knowledge_base.{fmt}"
    if fmt == "json":
        n = export_json(output)
    elif fmt == "csv":
        n = export_csv(output)
    else:
        n = export_zip(output)
    console.print(f"[green]✓[/green] {n} 件を {output} にエクスポートしました。")


# ─────────────────────────────────────────────
# stats
# ─────────────────────────────────────────────

@cli.command()
def stats():
    """ナレッジベースの統計を表示します。"""
    init_db()
    s = get_stats()
    table = Table(title="ナレッジベース統計")
    table.add_column("項目", style="cyan")
    table.add_column("値", justify="right")
    table.add_row("総アイテム数", str(s["total"]))
    for source, cnt in s.get("by_source", {}).items():
        table.add_row(f"  {source.replace('google_', '')}", str(cnt))
    console.print(table)


# ─────────────────────────────────────────────

if __name__ == "__main__":
    cli()
