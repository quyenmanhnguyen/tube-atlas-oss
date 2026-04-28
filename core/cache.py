"""SQLite cache layer cho YouTube Data API responses.

TTL mặc định 6 giờ. Cache key = JSON-serialized params. Tiết kiệm quota
khi user mở đi mở lại cùng kênh / search cùng từ khoá.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

CACHE_PATH = Path.home() / ".tube_atlas_cache.sqlite"
DEFAULT_TTL = 6 * 3600  # 6 hours


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(CACHE_PATH))
    c.execute(
        """CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            expires_at INTEGER NOT NULL
        )"""
    )
    return c


def get(key: str) -> Any | None:
    with _conn() as c:
        row = c.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
    if not row:
        return None
    value, expires_at = row
    if expires_at < int(time.time()):
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def set_(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    expires_at = int(time.time()) + ttl
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, default=str), expires_at),
        )


def make_key(prefix: str, **kwargs: Any) -> str:
    payload = json.dumps(kwargs, sort_keys=True, default=str)
    return f"{prefix}::{payload}"


def stats() -> dict[str, int]:
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        active = c.execute(
            "SELECT COUNT(*) FROM cache WHERE expires_at > ?", (int(time.time()),)
        ).fetchone()[0]
    return {"total": total, "active": active, "expired": total - active}


def clear() -> int:
    with _conn() as c:
        n = c.execute("DELETE FROM cache").rowcount
    return n
