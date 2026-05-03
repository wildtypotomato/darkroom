"""SQLite asset store for Memory Book.

Stdlib sqlite3 only — no ORM. Tables: assets, scenes, artifacts.
Schema is intentionally narrow; richer joins are computed in Python.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, TypedDict

AssetKind = Literal["photo", "voice", "text", "link"]


class Asset(TypedDict):
    id: str
    path: str
    kind: AssetKind
    taken_at: datetime | None
    lat: float | None
    lon: float | None
    embedding: bytes | None
    tags: list[str]


class Scene(TypedDict):
    id: str
    title: str
    caption: str
    hero_asset_id: str
    asset_ids: list[str]
    mood: str


class ArtifactManifest(TypedDict, total=False):
    id: str
    template: str
    scenes: list[Scene]
    pdf_path: str
    mp4_path: str
    score_path: str
    critique: dict


def home() -> Path:
    return Path(os.environ.get("MEMORY_BOOK_HOME", str(Path.home() / ".memory_book")))


def _db_path() -> Path:
    return home() / "memory_book.db"


@contextmanager
def _connect():
    home().mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if missing. Safe to call repeatedly."""
    with _connect() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS assets (
              id          TEXT PRIMARY KEY,
              path        TEXT NOT NULL,
              kind        TEXT NOT NULL,
              taken_at    TEXT,
              lat         REAL,
              lon         REAL,
              embedding   BLOB,
              tags        TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS scenes (
              id            TEXT PRIMARY KEY,
              title         TEXT NOT NULL,
              caption       TEXT NOT NULL,
              hero_asset_id TEXT NOT NULL,
              asset_ids     TEXT NOT NULL,
              mood          TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS artifacts (
              id          TEXT PRIMARY KEY,
              template    TEXT NOT NULL,
              scenes      TEXT NOT NULL,
              pdf_path    TEXT NOT NULL,
              mp4_path    TEXT NOT NULL,
              score_path  TEXT NOT NULL
            );
            """
        )


def add_asset(asset: Asset) -> str:
    """Insert an asset row. Returns the asset id (generated if blank)."""
    asset_id = asset.get("id") or uuid.uuid4().hex
    taken = asset.get("taken_at")
    taken_iso = taken.isoformat() if isinstance(taken, datetime) else None
    with _connect() as c:
        c.execute(
            "INSERT INTO assets (id, path, kind, taken_at, lat, lon, embedding, tags) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                asset_id,
                asset["path"],
                asset["kind"],
                taken_iso,
                asset.get("lat"),
                asset.get("lon"),
                asset.get("embedding"),
                json.dumps(asset.get("tags") or []),
            ),
        )
    return asset_id


def get_assets(criteria: dict[str, Any] | None = None) -> list[Asset]:
    """Return assets matching simple equality filters (kind, id)."""
    f = criteria or {}
    where: list[str] = []
    params: list[Any] = []
    for key in ("id", "kind"):
        if key in f:
            where.append(f"{key} = ?")
            params.append(f[key])
    sql = "SELECT * FROM assets"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY COALESCE(taken_at, '') ASC"
    with _connect() as c:
        rows = c.execute(sql, params).fetchall()
    return [_row_to_asset(r) for r in rows]


def update_embedding(asset_id: str, blob: bytes) -> None:
    with _connect() as c:
        c.execute("UPDATE assets SET embedding = ? WHERE id = ?", (blob, asset_id))


def _row_to_asset(row: sqlite3.Row) -> Asset:
    taken_iso = row["taken_at"]
    taken_at = datetime.fromisoformat(taken_iso) if taken_iso else None
    return Asset(
        id=row["id"],
        path=row["path"],
        kind=row["kind"],
        taken_at=taken_at,
        lat=row["lat"],
        lon=row["lon"],
        embedding=row["embedding"],
        tags=json.loads(row["tags"] or "[]"),
    )
