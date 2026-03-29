"""Export knowledge base to CSV, JSON, or ZIP."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

from storage.database import get_all_items


def export_json(output_path: str) -> int:
    rows = get_all_items()
    data = [dict(row) for row in rows]
    Path(output_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data)


def export_csv(output_path: str) -> int:
    rows = get_all_items()
    if not rows:
        return 0

    fieldnames = ["id", "source", "source_id", "title", "summary", "sentiment",
                  "tags", "categories", "created_at", "indexed_at"]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    return len(rows)


def export_zip(output_path: str) -> int:
    rows = get_all_items()

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Full JSON dump
        json_data = json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)
        zf.writestr("knowledge_base.json", json_data)

        # CSV summary
        buf = io.StringIO()
        fieldnames = ["id", "source", "title", "summary", "tags", "categories"]
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})
        zf.writestr("summary.csv", buf.getvalue())

        # Per-source markdown summaries
        keep_notes = [r for r in rows if r["source"] == "google_keep"]
        tasks = [r for r in rows if r["source"] == "google_tasks"]

        if keep_notes:
            md = _to_markdown(keep_notes, "Google Keep ノート")
            zf.writestr("google_keep.md", md)
        if tasks:
            md = _to_markdown(tasks, "Google Tasks")
            zf.writestr("google_tasks.md", md)

    return len(rows)


def _to_markdown(rows: list, title: str) -> str:
    lines = [f"# {title}\n", f"合計: {len(rows)} 件\n"]
    for row in rows:
        lines.append(f"## {row['title'] or '(無題)'}")
        if row["summary"]:
            lines.append(f"> {row['summary']}")
        tags = json.loads(row["tags"] or "[]")
        if tags:
            lines.append(f"タグ: {', '.join(tags[:10])}")
        cats = json.loads(row["categories"] or "[]")
        if cats:
            cat_str = ", ".join(f"{c['name']}({c.get('confidence', 0):.0%})" for c in cats)
            lines.append(f"カテゴリ: {cat_str}")
        lines.append("")
    return "\n".join(lines)
