"""Telegram photo ingestion.

The Hermes gateway pre-downloads attachments and hands the skill a host path.
We copy that file into our managed asset directory, parse EXIF, and insert
a row into the SQLite store.
"""
from __future__ import annotations

import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from PIL import ExifTags, Image

from . import store
from .store import Asset, home


def _assets_dir() -> Path:
    p = home() / "assets"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ingest_photo(file_path: str) -> str:
    """Copy `file_path` into the asset store and record a row. Returns asset id."""
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(file_path)

    asset_id = uuid.uuid4().hex
    suffix = src.suffix.lower() or ".jpg"
    dst = _assets_dir() / f"{asset_id}{suffix}"
    shutil.copy2(src, dst)

    taken_at, lat, lon = _parse_exif(dst)

    store.add_asset(
        Asset(
            id=asset_id,
            path=str(dst),
            kind="photo",
            taken_at=taken_at,
            lat=lat,
            lon=lon,
            embedding=None,
            tags=[f"src:{src.stem}"],
        )
    )
    return asset_id


def _parse_exif(path: Path) -> tuple[datetime | None, float | None, float | None]:
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return None, None, None
            exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            gps_raw = exif.get_ifd(ExifTags.IFD.GPSInfo)
    except Exception:
        return None, None, None

    exif_tags = {ExifTags.TAGS.get(k, k): v for k, v in exif_ifd.items()}
    taken_at = _parse_datetime(exif_tags.get("DateTimeOriginal"))
    lat, lon = _parse_gps(gps_raw)
    return taken_at, lat, lon


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def _parse_gps(gps: object) -> tuple[float | None, float | None]:
    if not isinstance(gps, dict):
        return None, None
    named = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps.items()}
    try:
        lat = _dms_to_float(named["GPSLatitude"], named.get("GPSLatitudeRef", "N"))
        lon = _dms_to_float(named["GPSLongitude"], named.get("GPSLongitudeRef", "E"))
        return lat, lon
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None, None


def _dms_to_float(dms, ref: str) -> float:
    deg, minutes, seconds = (float(x) for x in dms)
    val = deg + minutes / 60.0 + seconds / 3600.0
    if ref in ("S", "W"):
        val = -val
    return val
