"""Stage 1: Entity extraction (no API calls required).

Extracts URLs, dates, hashtags, mentions, and known tool/service names
directly from raw text – free and instant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Union

from sources.google_keep import KeepNote
from sources.google_tasks import TaskItem

Item = Union[KeepNote, TaskItem]

# Known tool/service keywords to detect automatically
KNOWN_TOOLS = {
    "notion", "obsidian", "roam", "logseq", "evernote",
    "todoist", "things", "omnifocus", "ticktick", "asana", "trello",
    "slack", "discord", "zoom", "teams", "meet",
    "github", "gitlab", "jira", "linear", "figma",
    "chatgpt", "claude", "gemini", "copilot", "gpt",
    "python", "javascript", "typescript", "rust", "go", "java",
    "react", "nextjs", "vue", "svelte", "django", "fastapi",
    "aws", "gcp", "azure", "docker", "kubernetes",
    "youtube", "twitter", "instagram", "linkedin",
}

_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
_HASHTAG_RE = re.compile(r"#(\w+)")
_MENTION_RE = re.compile(r"@(\w+)")
_DATE_RE = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}")


@dataclass
class EntityResult:
    urls: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


def extract_entities(item: Item) -> EntityResult:
    text = item.full_text.lower()

    urls = _URL_RE.findall(item.full_text)
    hashtags = _HASHTAG_RE.findall(text)
    mentions = _MENTION_RE.findall(text)
    dates = _DATE_RE.findall(text)
    tools = sorted({t for t in KNOWN_TOOLS if t in text})

    return EntityResult(
        urls=urls,
        hashtags=hashtags,
        mentions=mentions,
        dates=dates,
        tools=tools,
    )
