"""The digest of a chunk: everything the reading of the step looks at, and nothing else.

A surface chunk is 109 × 128 × 128 bytes (1.78 MB). The step only looks at its edges: sixteen cuts, sixteen
voxels wide, on all four sides. The digest keeps those edges as integer SUMS (4 × 16 × 109 × 2 bytes = 14 KB),
the verdict of the texture filter and the depth profile. A sum divided by sixteen gives exactly the research
mean, so no number moves; and a chunk read once is never read again, whichever band asks for it.
"""
from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from vesuve import core
from vesuve.remote_zarr import UNREADABLE
from vesuve.transport import ABSENT

CHUNK_SIDE = 128
CUTS = tuple(CHUNK_SIDE * (2 * i + 1) // (2 * 16) for i in range(16))  # 4, 12, …, 124 (`204`:69)
EDGE_WIDTH = 16          # `199`:67, derived from a median meander of 5 voxels
COHERENCE_FLOOR = 0.15   # `la_recette_posee_sur_le_rouleau.py:62`
EMPTY, TOO_LITTLE_TEXTURE = "empty", "too little texture"
CACHE_FORMAT = "2"       # 0.1.0 wrote French field names; a digest cache of that version is not read


@dataclass(frozen=True)
class Digest:
    cy: int
    cx: int
    reason: str | None  # None: kept
    retries: int = 0
    right: np.ndarray | None = None   # (16, depth) uint16
    left: np.ndarray | None = None
    bottom: np.ndarray | None = None
    top: np.ndarray | None = None
    depth: np.ndarray | None = None   # (depth,) mean per layer

    @property
    def kept(self) -> bool:
        return self.reason is None

    def profile(self, side: str) -> np.ndarray:
        """The sixteen profiles of an edge, as MEANS: the shape the research's `un_pas` receives."""
        return getattr(self, side).astype(np.float64) / EDGE_WIDTH


def digest_chunk(cy: int, cx: int, block: np.ndarray | None, reason: str | None, retries: int = 0) -> Digest:
    """The research filter, in its order: absent, empty, too little texture, then the edges."""
    if block is None:
        return Digest(cy, cx, reason, retries)
    if int(block.max()) <= 0:
        return Digest(cy, cx, EMPTY, retries)
    _, kept = core.texture_filter(block, COHERENCE_FLOOR)
    if not kept:
        return Digest(cy, cx, TOO_LITTLE_TEXTURE, retries)
    edges = core.edge_profiles(block, CUTS, EDGE_WIDTH)
    return Digest(cy, cx, None, retries, depth=core.depth_profile(block), **edges)


class DigestCache:
    """One digest per file, under one folder per volume. ⚠ A network failure is never cached: it says
    something about the wire, not about the chunk."""

    def __init__(self, root: Path, volume_url: str):
        key = hashlib.sha1(f"{volume_url}|{CACHE_FORMAT}".encode()).hexdigest()[:16]
        self.folder = Path(root) / key
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "VOLUME").write_text(volume_url + "\n")

    def _path(self, cy: int, cx: int) -> Path:
        return self.folder / f"{cy}_{cx}.npz"

    def read(self, cy: int, cx: int) -> Digest | None:
        p = self._path(cy, cx)
        if not p.exists():
            return None
        with np.load(p, allow_pickle=False) as z:
            reason = str(z["reason"]) or None
            if reason is not None:
                return Digest(cy, cx, reason)
            return Digest(cy, cx, None, 0, *(z[k] for k in ("right", "left", "bottom", "top", "depth")))

    def write(self, d: Digest) -> None:
        if d.reason is not None and d.reason not in (EMPTY, TOO_LITTLE_TEXTURE, ABSENT, UNREADABLE):
            return
        buffer = io.BytesIO()
        fields = {"reason": np.array(d.reason or "")}
        if d.kept:
            fields.update({k: getattr(d, k) for k in ("right", "left", "bottom", "top", "depth")})
        np.savez_compressed(buffer, **fields)
        tmp = self._path(d.cy, d.cx).with_suffix(".tmp")
        tmp.write_bytes(buffer.getvalue())
        tmp.replace(self._path(d.cy, d.cx))
