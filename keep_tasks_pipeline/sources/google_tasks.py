"""Google Tasks source connector using the official Tasks API."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Optional

from googleapiclient.discovery import build

from auth.google_auth import get_google_credentials


@dataclass
class TaskItem:
    source: str = "google_tasks"
    source_id: str = ""
    task_list_id: str = ""
    task_list_title: str = ""
    title: str = ""
    notes: str = ""
    status: str = ""          # "needsAction" | "completed"
    due: Optional[str] = None
    completed_at: Optional[str] = None
    parent_id: Optional[str] = None
    links: list[str] = field(default_factory=list)
    updated: Optional[str] = None

    @property
    def full_text(self) -> str:
        parts = [self.title]
        if self.notes:
            parts.append(self.notes)
        if self.due:
            parts.append(f"期限: {self.due}")
        if self.status == "completed":
            parts.append("[完了]")
        return "\n".join(parts)


def fetch_all_tasks(show_completed: bool = True) -> list[TaskItem]:
    """Fetch every task from all task lists using the official Google Tasks API."""
    creds = get_google_credentials()
    service = build("tasks", "v1", credentials=creds, cache_discovery=False)

    items: list[TaskItem] = []

    # 1. Get all task lists
    lists_response = service.tasklists().list(maxResults=100).execute()
    task_lists = lists_response.get("items", [])

    for tl in task_lists:
        tl_id = tl["id"]
        tl_title = tl.get("title", "")

        # 2. Get tasks in each list
        kwargs: dict = {
            "tasklist": tl_id,
            "maxResults": 100,
            "showHidden": True,
        }
        if show_completed:
            kwargs["showCompleted"] = True

        page_token = None
        while True:
            if page_token:
                kwargs["pageToken"] = page_token
            resp = service.tasks().list(**kwargs).execute()
            for t in resp.get("items", []):
                links = [lnk.get("link", "") for lnk in t.get("links", []) if lnk.get("link")]
                item = TaskItem(
                    source_id=t["id"],
                    task_list_id=tl_id,
                    task_list_title=tl_title,
                    title=t.get("title", ""),
                    notes=t.get("notes", ""),
                    status=t.get("status", ""),
                    due=t.get("due"),
                    completed_at=t.get("completed"),
                    parent_id=t.get("parent"),
                    links=links,
                    updated=t.get("updated"),
                )
                items.append(item)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return items
