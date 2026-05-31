"""SQLite database with FTS5 for keyword search and BLOB storage for vectors."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from local_rag.config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    modified_at REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    heading TEXT,
    content TEXT NOT NULL,
    token_estimate INTEGER NOT NULL,
    embedding BLOB,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(path);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
"""

_FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    heading,
    content,
    content='chunks',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, heading, content)
    VALUES (new.id, COALESCE(new.heading, ''), new.content);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, heading, content)
    VALUES ('delete', old.id, COALESCE(old.heading, ''), old.content);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, heading, content)
    VALUES ('delete', old.id, COALESCE(old.heading, ''), old.content);
    INSERT INTO chunks_fts(rowid, heading, content)
    VALUES (new.id, COALESCE(new.heading, ''), new.content);
END;
"""


def _ensure_db_dir() -> None:
    Path(settings.sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    _ensure_db_dir()
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=60000")
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create all tables, indexes, and FTS triggers."""
    with get_connection() as conn:
        conn.executescript(_SCHEMA)
        conn.executescript(_FTS_SCHEMA)
        conn.commit()
