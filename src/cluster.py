"""Cluster assets into Scene-sized groups.

Two signals: visual similarity (CLIP embedding, with a deterministic color-
histogram fallback for environments where open_clip isn't installed), and
EXIF time proximity — assets within `TIME_GAP_SEC` of each other are pulled
into the same cluster regardless of visual distance.

Clustering uses sklearn AgglomerativeClustering on a precomputed distance
matrix:
    d(i, j) = cos_dist(emb_i, emb_j)         if time_gap(i, j) ≤ 4h
            = cos_dist(emb_i, emb_j) + 1.0   otherwise

The +1.0 bias means time-distant pairs only merge when nothing closer is
available, but it's not infinity — so a season-long set with no temporal
overlap still resolves to k clusters instead of n.
"""

from __future__ import annotations

import functools
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .store import Asset

if TYPE_CHECKING:  # pragma: no cover
    pass

TIME_GAP_SEC = 4 * 60 * 60  # 4 hours
EMB_DIM_FALLBACK = 48  # 16 bins × 3 channels — small, fast, deterministic


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------


def compute_embedding(path: str) -> bytes:
    """Return a float32 vector as raw bytes for the image at `path`.

    Uses open_clip if available, otherwise a normalised RGB color histogram.
    The fallback is deterministic and good enough for time-aware clustering
    on small (≤50) photo sets — which is the demo's scale.
    """
    if os.environ.get("DARKROOM_EMBED_FALLBACK") == "1":
        vec = _hist_embedding(path)
    else:
        try:
            vec = _clip_embedding(path)
        except Exception:
            vec = _hist_embedding(path)
    return vec.astype(np.float32).tobytes()


def _clip_embedding(path: str) -> np.ndarray:
    import open_clip  # type: ignore[import-not-found]
    import torch  # type: ignore[import-not-found]
    from PIL import Image

    model, _, preprocess = _load_clip()
    img = preprocess(Image.open(path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        feats = model.encode_image(img)
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy().reshape(-1)


@functools.lru_cache(maxsize=1)
def _load_clip():
    import open_clip  # type: ignore[import-not-found]

    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    model.eval()
    return model, None, preprocess


def _hist_embedding(path: str) -> np.ndarray:
    from PIL import Image

    img = Image.open(path).convert("RGB").resize((64, 64))
    arr = np.asarray(img, dtype=np.float32)  # (64, 64, 3)
    bins = 16
    vec = np.zeros(bins * 3, dtype=np.float32)
    for c in range(3):
        hist, _ = np.histogram(arr[..., c], bins=bins, range=(0, 256))
        vec[c * bins : (c + 1) * bins] = hist
    n = np.linalg.norm(vec) or 1.0
    return vec / n


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------


def cluster_assets(assets: list[Asset], k: int = 6) -> list[list[str]]:
    """Group asset IDs into ≤k clusters by visual + time proximity.

    Assets without embeddings get one computed on the fly.
    Assets without ``taken_at`` participate visually but don't get any
    time-bonus — they merge wherever colour says they belong.

    Returns deduplicated groups — each asset ID appears at most once.
    """
    if not assets:
        return []
    if len(assets) == 1:
        return [[assets[0]["id"]]]
    if len(assets) > 500:
        raise ValueError(f"too many assets ({len(assets)}); maximum supported is 500")

    embs = [_get_or_compute_emb(a) for a in assets]
    times = [a.get("taken_at") for a in assets]
    n = len(assets)
    target_k = max(1, min(k, n))

    # Pairwise distances. Cosine distance in [0, 2]; time penalty pushes
    # cross-day pairs above the within-day band.
    D = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        for j in range(i + 1, n):
            cos = 1.0 - float(np.dot(embs[i], embs[j]))
            cos = max(0.0, min(2.0, cos))
            if not _within_window(times[i], times[j]):
                cos += 1.0
            D[i, j] = D[j, i] = cos

    if target_k == 1:
        labels = np.zeros(n, dtype=int)
    else:
        from sklearn.cluster import AgglomerativeClustering  # local import

        model = AgglomerativeClustering(
            n_clusters=target_k, metric="precomputed", linkage="average"
        )
        labels = model.fit_predict(D)

    groups: dict[int, list[tuple[int, str]]] = {}
    for idx, label in enumerate(labels):
        groups.setdefault(int(label), []).append((idx, assets[idx]["id"]))

    # Order groups by their earliest taken_at (so book reads chronologically)
    def _sort_key(g: list[tuple[int, str]]) -> datetime:
        for idx, _ in g:
            t = times[idx]
            if isinstance(t, datetime):
                return t
        return datetime.max

    ordered = sorted(groups.values(), key=_sort_key)
    return [[aid for _, aid in g] for g in ordered]


def _get_or_compute_emb(asset: Asset) -> np.ndarray:
    blob = asset.get("embedding")
    if blob:
        return _unpack(blob)
    if asset.get("path") and Path(asset["path"]).exists():
        return _unpack(compute_embedding(asset["path"]))
    # No path, no embedding — return a zero vector; it'll cluster with
    # whatever else is similarly empty.
    return np.zeros(EMB_DIM_FALLBACK, dtype=np.float32)


def _unpack(blob: bytes) -> np.ndarray:
    vec = np.frombuffer(blob, dtype=np.float32).copy()
    n = np.linalg.norm(vec)
    return vec / n if n else vec


def _within_window(t1, t2) -> bool:
    if not isinstance(t1, datetime) or not isinstance(t2, datetime):
        return False
    return abs((t1 - t2).total_seconds()) <= TIME_GAP_SEC
