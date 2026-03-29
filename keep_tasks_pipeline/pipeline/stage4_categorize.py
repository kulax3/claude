"""Stage 4: Category assignment with confidence scores.

Assigns 1-3 categories from the default taxonomy to each item.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import anthropic

from config import DEFAULT_CATEGORIES
from pipeline.stage3_tagging import TagResult
from sources.google_keep import KeepNote
from sources.google_tasks import TaskItem


@dataclass
class CategoryResult:
    categories: list[dict] = field(default_factory=list)
    # e.g. [{"name": "技術・IT", "confidence": 0.92}, ...]


_CAT_PROMPT = """\
以下のアイテムを最も適切なカテゴリに分類してください。

--- アイテム要約 ---
{summary}

--- タグ ---
{tags}

--- 利用可能カテゴリ ---
{categories}

JSON出力（1〜3カテゴリ、信頼スコア付き）：
{{
  "categories": [
    {{"name": "カテゴリ名", "confidence": 0.0〜1.0}},
    ...
  ]
}}"""


def categorize(
    item: KeepNote | TaskItem,
    tags: TagResult,
    client: anthropic.Anthropic,
) -> CategoryResult:
    prompt = _CAT_PROMPT.format(
        summary=tags.summary or item.full_text[:500],
        tags=", ".join(tags.tags[:20]),
        categories="\n".join(f"- {c}" for c in DEFAULT_CATEGORIES),
    )

    try:
        resp = client.messages.create(
            model=_get_model(),
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(resp.content[0].text)
        # Clamp confidence to [0, 1]
        cats = [
            {"name": c["name"], "confidence": max(0.0, min(1.0, float(c.get("confidence", 0.5))))}
            for c in data.get("categories", [])
            if c.get("name") in DEFAULT_CATEGORIES
        ]
        return CategoryResult(categories=cats)
    except Exception as e:
        return CategoryResult()


def _get_model() -> str:
    return os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
