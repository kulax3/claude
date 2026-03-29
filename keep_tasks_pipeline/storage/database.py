"""SQLite database layer with FTS5 full-text search.

Schema:
  items          – main table (one row per Keep note / Task)
  items_fts      – FTS5 virtual table for full-text search
  pipeline_jobs  – tracks processing state per item
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                source        TEXT NOT NULL,          -- 'google_keep' | 'google_tasks'
                source_id     TEXT NOT NULL,
                title         TEXT DEFAULT '',
                full_text     TEXT DEFAULT '',
                summary       TEXT DEFAULT '',
                sentiment     TEXT DEFAULT 'neutral',
                tags          TEXT DEFAULT '[]',      -- JSON array
                categories    TEXT DEFAULT '[]',      -- JSON array of {name, confidence}
                entities      TEXT DEFAULT '{}',      -- JSON: urls, hashtags, tools ...
                vision        TEXT DEFAULT '{}',      -- JSON: ocr_text, description, visual_tags
                metadata      TEXT DEFAULT '{}',      -- source-specific extra fields
                created_at    TEXT,
                updated_at    TEXT,
                indexed_at    TEXT DEFAULT (datetime('now')),
                UNIQUE(source, source_id)
            );

            CREATE TABLE IF NOT EXISTS items_fts (
                content       TEXT,
                tokenize      TEXT DEFAULT 'trigram'
            ) USING fts5(
                title,
                full_text,
                summary,
                tags,
                content=items,
                content_rowid=id
            ) ;

            -- Triggers to keep FTS in sync
            CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
                INSERT INTO items_fts(rowid, title, full_text, summary, tags)
                VALUES (new.id, new.title, new.full_text, new.summary, new.tags);
            END;

            CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
                INSERT INTO items_fts(items_fts, rowid, title, full_text, summary, tags)
                VALUES ('delete', old.id, old.title, old.full_text, old.summary, old.tags);
                INSERT INTO items_fts(rowid, title, full_text, summary, tags)
                VALUES (new.id, new.title, new.full_text, new.summary, new.tags);
            END;

            CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
                INSERT INTO items_fts(items_fts, rowid, title, full_text, summary, tags)
                VALUES ('delete', old.id, old.title, old.full_text, old.summary, old.tags);
            END;

            CREATE TABLE IF NOT EXISTS pipeline_jobs (
                source_id     TEXT NOT NULL,
                source        TEXT NOT NULL,
                stage         INTEGER NOT NULL,      -- 1-4
                status        TEXT NOT NULL DEFAULT 'pending',  -- pending|done|error
                error_msg     TEXT,
                updated_at    TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (source_id, source, stage)
            );
        """)


def upsert_item(
    source: str,
    source_id: str,
    title: str,
    full_text: str,
    metadata: dict,
    created_at: Optional[str] = None,
    updated_at: Optional[str] = None,
) -> int:
    """Insert or update an item. Returns the row id."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO items (source, source_id, title, full_text, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, source_id) DO UPDATE SET
                title      = excluded.title,
                full_text  = excluded.full_text,
                metadata   = excluded.metadata,
                updated_at = excluded.updated_at
        """, (source, source_id, title, full_text, json.dumps(metadata), created_at, updated_at))
        row = conn.execute(
            "SELECT id FROM items WHERE source=? AND source_id=?", (source, source_id)
        ).fetchone()
        return row["id"]


def update_pipeline_result(
    source: str,
    source_id: str,
    entities: dict,
    vision: dict,
    tags: list[str],
    summary: str,
    sentiment: str,
    categories: list[dict],
) -> None:
    with get_db() as conn:
        conn.execute("""
            UPDATE items
            SET entities  = ?,
                vision    = ?,
                tags      = ?,
                summary   = ?,
                sentiment = ?,
                categories = ?
            WHERE source=? AND source_id=?
        """, (
            json.dumps(entities, ensure_ascii=False),
            json.dumps(vision, ensure_ascii=False),
            json.dumps(tags, ensure_ascii=False),
            summary,
            sentiment,
            json.dumps(categories, ensure_ascii=False),
            source,
            source_id,
        ))


def set_job_status(source: str, source_id: str, stage: int, status: str, error: str = "") -> None:
    with get_db() as conn:
        conn.execute("""
            INSERT INTO pipeline_jobs (source_id, source, stage, status, error_msg, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(source_id, source, stage) DO UPDATE SET
                status     = excluded.status,
                error_msg  = excluded.error_msg,
                updated_at = excluded.updated_at
        """, (source_id, source, stage, status, error))


def get_all_items() -> list[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute("SELECT * FROM items ORDER BY indexed_at DESC").fetchall()


def get_stats() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        by_source = conn.execute(
            "SELECT source, COUNT(*) as cnt FROM items GROUP BY source"
        ).fetchall()
        return {
            "total": total,
            "by_source": {row["source"]: row["cnt"] for row in by_source},
        }
