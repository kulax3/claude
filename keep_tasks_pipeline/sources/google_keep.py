"""Google Keep source connector.

Two modes:
  1. gkeepapi   – real-time sync via unofficial Google Keep API (default)
  2. takeout    – parse a Google Takeout export directory (fallback / safer option)

Usage:
  items = fetch_keep_notes(mode="gkeepapi", email="you@gmail.com", master_token="...")
  items = fetch_keep_notes(mode="takeout", takeout_dir="/path/to/Takeout/Keep")
"""

from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class KeepNote:
    source: str = "google_keep"
    source_id: str = ""
    title: str = ""
    text: str = ""
    labels: list[str] = field(default_factory=list)
    color: str = ""
    is_pinned: bool = False
    is_archived: bool = False
    is_trashed: bool = False
    images: list[bytes] = field(default_factory=list)   # raw bytes for vision stage
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def full_text(self) -> str:
        parts = []
        if self.title:
            parts.append(self.title)
        if self.text:
            parts.append(self.text)
        if self.labels:
            parts.append("ラベル: " + ", ".join(self.labels))
        if self.color and self.color not in ("DEFAULT", "WHITE"):
            parts.append(f"色: {self.color}")
        if self.is_pinned:
            parts.append("[ピン留め]")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# gkeepapi mode
# ---------------------------------------------------------------------------

def _fetch_via_gkeepapi(email: str, master_token: str) -> list[KeepNote]:
    try:
        import gkeepapi
    except ImportError:
        raise ImportError("gkeepapi is not installed. Run: pip install gkeepapi")

    keep = gkeepapi.Keep()
    keep.resume(email, master_token)
    keep.sync()

    notes: list[KeepNote] = []
    for node in keep.all():
        if node.trashed:
            continue

        images: list[bytes] = []
        text_body = ""

        if hasattr(node, "text"):
            text_body = node.text or ""
        elif hasattr(node, "items"):
            # List note – join items
            text_body = "\n".join(
                f"{'[x]' if item.checked else '[ ]'} {item.text}"
                for item in node.items
            )

        # Collect blob images
        for blob in getattr(node, "blobs", []):
            if hasattr(blob, "save") and callable(blob.save):
                try:
                    raw = blob.save()
                    if raw:
                        images.append(raw)
                except Exception:
                    pass

        note = KeepNote(
            source_id=node.id,
            title=node.title or "",
            text=text_body,
            labels=[lbl.name for lbl in node.labels.all()],
            color=str(node.color).split(".")[-1] if node.color else "DEFAULT",
            is_pinned=node.pinned,
            is_archived=node.archived,
            is_trashed=node.trashed,
            images=images,
            created_at=node.timestamps.created.isoformat() if node.timestamps.created else None,
            updated_at=node.timestamps.updated.isoformat() if node.timestamps.updated else None,
        )
        notes.append(note)

    return notes


# ---------------------------------------------------------------------------
# Takeout mode
# ---------------------------------------------------------------------------

def _fetch_via_takeout(takeout_dir: str) -> list[KeepNote]:
    """Parse a Google Takeout Keep export directory (JSON + HTML files)."""
    keep_path = Path(takeout_dir)
    if not keep_path.exists():
        raise FileNotFoundError(f"Takeout directory not found: {takeout_dir}")

    notes: list[KeepNote] = []

    for json_file in sorted(keep_path.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        if data.get("isTrashed"):
            continue

        # Text content
        text_body = data.get("textContent", "")
        # List notes
        list_items = data.get("listContent", [])
        if list_items:
            text_body = "\n".join(
                f"{'[x]' if item.get('isChecked') else '[ ]'} {item.get('text', '')}"
                for item in list_items
            )

        labels = [lbl.get("name", "") for lbl in data.get("labels", [])]
        color = data.get("color", "DEFAULT")

        # Inline images (base64 in attachments)
        images: list[bytes] = []
        for att in data.get("attachments", []):
            mime = att.get("mimetype", "")
            if mime.startswith("image/"):
                # Look for matching image file beside the JSON
                img_filename = att.get("filePath", "")
                img_path = keep_path / img_filename
                if img_path.exists():
                    images.append(img_path.read_bytes())

        note = KeepNote(
            source_id=json_file.stem,
            title=data.get("title", ""),
            text=text_body,
            labels=labels,
            color=color,
            is_pinned=data.get("isPinned", False),
            is_archived=data.get("isArchived", False),
            is_trashed=data.get("isTrashed", False),
            images=images,
            created_at=_ms_to_iso(data.get("userEditedTimestampUsec")),
            updated_at=_ms_to_iso(data.get("userEditedTimestampUsec")),
        )
        notes.append(note)

    return notes


def _ms_to_iso(usec: Optional[int]) -> Optional[str]:
    if usec is None:
        return None
    import datetime
    dt = datetime.datetime.fromtimestamp(usec / 1_000_000, tz=datetime.timezone.utc)
    return dt.isoformat()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def fetch_keep_notes(
    mode: str = "takeout",
    email: str = "",
    master_token: str = "",
    takeout_dir: str = "",
) -> list[KeepNote]:
    """Fetch Google Keep notes.

    Args:
        mode: "gkeepapi" or "takeout"
        email: Google account email (gkeepapi mode only)
        master_token: gkeepapi master token (gkeepapi mode only)
        takeout_dir: path to Takeout/Keep directory (takeout mode only)
    """
    if mode == "gkeepapi":
        if not email or not master_token:
            raise ValueError("email and master_token required for gkeepapi mode")
        return _fetch_via_gkeepapi(email, master_token)
    elif mode == "takeout":
        if not takeout_dir:
            raise ValueError("takeout_dir required for takeout mode")
        return _fetch_via_takeout(takeout_dir)
    else:
        raise ValueError(f"Unknown mode: {mode}. Choose 'gkeepapi' or 'takeout'.")
