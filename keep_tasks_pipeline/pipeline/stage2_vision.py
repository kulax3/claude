"""Stage 2: Vision analysis for images attached to Google Keep notes.

Uses Claude's vision capability to:
- Perform OCR (read text inside images)
- Describe image content
- Generate visual tags

Google Tasks has no images, so this stage is skipped for TaskItem.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field

import anthropic

from sources.google_keep import KeepNote
from sources.google_tasks import TaskItem

Item = KeepNote | TaskItem


@dataclass
class VisionResult:
    ocr_text: str = ""
    description: str = ""
    visual_tags: list[str] = field(default_factory=list)


_VISION_PROMPT = """\
この画像を分析してください。以下の情報を日本語でJSONで返してください：
{
  "ocr_text": "画像内のテキストをすべて抽出（なければ空文字）",
  "description": "画像の内容を1〜2文で説明",
  "visual_tags": ["タグ1", "タグ2", ...]  // 最大20個の検索用タグ
}
JSONのみ返してください。説明不要。"""


def analyze_images(item: Item, client: anthropic.Anthropic) -> VisionResult:
    """Run vision analysis on all images in a KeepNote. TaskItem returns empty result."""
    if not isinstance(item, KeepNote) or not item.images:
        return VisionResult()

    combined_ocr: list[str] = []
    combined_desc: list[str] = []
    combined_tags: set[str] = set()

    for img_bytes in item.images:
        b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
        # Detect image type from magic bytes
        mime = _detect_mime(img_bytes)

        try:
            resp = client.messages.create(
                model=_get_model(),
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": _VISION_PROMPT},
                    ],
                }],
            )
            import json
            data = json.loads(resp.content[0].text)
            if data.get("ocr_text"):
                combined_ocr.append(data["ocr_text"])
            if data.get("description"):
                combined_desc.append(data["description"])
            combined_tags.update(data.get("visual_tags", []))
        except Exception:
            pass  # Skip failed image silently

    return VisionResult(
        ocr_text="\n".join(combined_ocr),
        description="\n".join(combined_desc),
        visual_tags=sorted(combined_tags),
    )


def _detect_mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"  # fallback


def _get_model() -> str:
    import os
    return os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
