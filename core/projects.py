"""My Projects — bookmark kênh / niche / video hay theo dõi.

Lưu local SQLite (cùng file với cache). Không phụ thuộc API, không cần đồng bộ.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DB_PATH = Path.home() / ".tube_atlas_cache.sqlite"


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB_PATH))
    c.execute(
        """CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,          -- channel | niche | video
            label TEXT NOT NULL,
            value TEXT NOT NULL,         -- @handle / topic / video_id
            note TEXT DEFAULT '',
            created_at INTEGER NOT NULL
        )"""
    )
    return c


def add(kind: str, label: str, value: str, note: str = "") -> int:
    """Thêm bookmark. Trả về ID mới. kind ∈ {channel, niche, video}."""
    assert kind in {"channel", "niche", "video"}, kind
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO projects (kind, label, value, note, created_at) VALUES (?, ?, ?, ?, ?)",
            (kind, label.strip(), value.strip(), note.strip(), int(time.time())),
        )
        return int(cur.lastrowid or 0)


def list_all(kind: str | None = None) -> list[dict]:
    q = "SELECT id, kind, label, value, note, created_at FROM projects"
    params: tuple = ()
    if kind:
        q += " WHERE kind = ?"
        params = (kind,)
    q += " ORDER BY created_at DESC"
    with _conn() as c:
        rows = c.execute(q, params).fetchall()
    return [
        {"id": r[0], "kind": r[1], "label": r[2], "value": r[3], "note": r[4], "created_at": r[5]}
        for r in rows
    ]


def delete(project_id: int) -> bool:
    with _conn() as c:
        n = c.execute("DELETE FROM projects WHERE id = ?", (project_id,)).rowcount
    return n > 0


def count() -> int:
    with _conn() as c:
        return int(c.execute("SELECT COUNT(*) FROM projects").fetchone()[0])
