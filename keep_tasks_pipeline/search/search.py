"""Natural language search over the knowledge base.

Two modes:
  1. FTS5 keyword search  – fast, no API cost
  2. Claude reranking     – semantic relevance scoring on top of FTS5 results
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

import anthropic

from config import DB_PATH


@dataclass
class SearchResult:
    id: int
    source: str
    source_id: str
    title: str
    summary: str
    tags: list[str]
    categories: list[dict]
    score: float = 1.0
    snippet: str = ""


def fts_search(query: str, limit: int = 20) -> list[SearchResult]:
    """Fast FTS5 full-text search with LIKE fallback for short Japanese queries.

    The trigram tokenizer requires at least 3 characters. For shorter queries
    we fall back to a LIKE scan on the items table directly.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        # Trigram needs 3+ chars. For short queries use LIKE fallback.
        if len(query.replace(" ", "")) < 3:
            like_pat = f"%{query}%"
            rows = conn.execute("""
                SELECT id, source, source_id, title, summary, tags, categories,
                       '' AS snippet
                FROM items
                WHERE title LIKE ? OR full_text LIKE ? OR summary LIKE ? OR tags LIKE ?
                LIMIT ?
            """, (like_pat, like_pat, like_pat, like_pat, limit)).fetchall()
        else:
            safe_query = query.replace('"', '""')
            rows = conn.execute("""
                SELECT i.id, i.source, i.source_id, i.title, i.summary, i.tags, i.categories,
                       snippet(items_fts, 1, '<b>', '</b>', '...', 20) AS snippet
                FROM items_fts
                JOIN items i ON items_fts.rowid = i.id
                WHERE items_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (safe_query, limit)).fetchall()

        return [
            SearchResult(
                id=row["id"],
                source=row["source"],
                source_id=row["source_id"],
                title=row["title"],
                summary=row["summary"],
                tags=json.loads(row["tags"] or "[]"),
                categories=json.loads(row["categories"] or "[]"),
                snippet=row["snippet"] or "",
            )
            for row in rows
        ]
    except Exception:
        return []
    finally:
        conn.close()


_RERANK_PROMPT = """\
ユーザーのクエリ「{query}」に対して、以下の検索結果を関連度順に並べ替えてください。

検索結果:
{results}

各結果のIDと関連スコア(0.0〜1.0)をJSONで返してください：
{{"ranked": [{{"id": 1, "score": 0.95}}, ...]}}

JSONのみ返してください。"""


def semantic_search(
    query: str,
    client: anthropic.Anthropic,
    limit: int = 10,
) -> list[SearchResult]:
    """FTS5 search + Claude reranking for semantic relevance."""
    candidates = fts_search(query, limit=limit * 2)
    if not candidates:
        return []
    if len(candidates) <= 3:
        return candidates[:limit]

    results_text = "\n".join(
        f"ID:{r.id} タイトル:{r.title} 要約:{r.summary} タグ:{','.join(r.tags[:5])}"
        for r in candidates
    )
    prompt = _RERANK_PROMPT.format(query=query, results=results_text)

    try:
        resp = client.messages.create(
            model=_get_model(),
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(resp.content[0].text)
        score_map = {item["id"]: item["score"] for item in data.get("ranked", [])}
        for r in candidates:
            r.score = score_map.get(r.id, 0.0)
        candidates.sort(key=lambda r: r.score, reverse=True)
    except Exception:
        pass  # Fall back to FTS order

    return candidates[:limit]


def _get_model() -> str:
    import os
    return os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
