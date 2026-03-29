"""Stage 3: Semantic tag generation.

Combines all available context (text, entities, vision) and asks Claude
to produce 20-30 searchable Japanese tags per item.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Union

import anthropic

from pipeline.stage1_entity import EntityResult
from pipeline.stage2_vision import VisionResult
from sources.google_keep import KeepNote
from sources.google_tasks import TaskItem

Item = Union[KeepNote, TaskItem]


@dataclass
class TagResult:
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    sentiment: str = ""  # positive / negative / neutral


_TAG_PROMPT = """\
以下のコンテンツを分析して、JSONで返してください：

--- コンテンツ ---
{content}

--- 補足情報 ---
{extra}
---

出力フォーマット（JSONのみ）：
{{
  "tags": ["タグ1", "タグ2", ...],   // 20〜30個の検索用キーワード（日本語・英語混在可）
  "summary": "内容を1文で要約（日本語）",
  "sentiment": "positive|negative|neutral"
}}"""


def generate_tags(
    item: Item,
    entities: EntityResult,
    vision: VisionResult,
    client: anthropic.Anthropic,
) -> TagResult:
    content = item.full_text[:2000]  # truncate to stay within token budget

    extra_parts: list[str] = []
    if entities.tools:
        extra_parts.append(f"検出ツール: {', '.join(entities.tools)}")
    if entities.urls:
        extra_parts.append(f"URL数: {len(entities.urls)}")
    if entities.hashtags:
        extra_parts.append(f"ハッシュタグ: {', '.join(entities.hashtags)}")
    if vision.ocr_text:
        extra_parts.append(f"画像内テキスト: {vision.ocr_text[:300]}")
    if vision.description:
        extra_parts.append(f"画像説明: {vision.description[:200]}")
    if vision.visual_tags:
        extra_parts.append(f"ビジュアルタグ: {', '.join(vision.visual_tags[:10])}")
    if isinstance(item, KeepNote) and item.labels:
        extra_parts.append(f"既存ラベル: {', '.join(item.labels)}")
    if isinstance(item, TaskItem):
        extra_parts.append(f"タスクリスト: {item.task_list_title}")
        extra_parts.append(f"ステータス: {item.status}")

    prompt = _TAG_PROMPT.format(
        content=content,
        extra="\n".join(extra_parts) if extra_parts else "(なし)",
    )

    try:
        resp = client.messages.create(
            model=_get_model(),
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(resp.content[0].text)
        return TagResult(
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            sentiment=data.get("sentiment", "neutral"),
        )
    except Exception as e:
        return TagResult(summary=f"[タグ生成エラー: {e}]")


def _get_model() -> str:
    return os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
