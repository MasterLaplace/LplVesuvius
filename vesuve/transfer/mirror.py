"""A local mirror of the raw scan: the only chunks a render reads, downloaded once and checked.

`vc_render_tifxyz` reads the raw volume of PHercParis4 over the network chunk by chunk, with no disk cache. A block
of 16 × 16 surface chunks rendered that way pulled about 6 GB for the 891 chunks of 2 MB it really reads. From a
local mirror of those chunks the same block renders in about 24 s, identical voxel for voxel
(`le_miroir_du_volume.py` on the `experimental` branch, whose `les_chunks_dun_cadre` this ports).

⚠⚠ A chunk missing from the mirror reads as empty, WITHOUT an error: the margin around the surface is wide, and a chunk
the bucket declares absent is recorded as such, so that "absent from the scan" and "not downloaded" stay two facts.

⚠⚠ A chunk written but not flushed when the machine went down comes back truncated. The research paid for it on
2026-09-26: 14 piles failed on chunks whose decoded size no longer matched a chunk. The raw volume stores its chunks
uncompressed, so a chunk file has exactly one right size, and the mirror refuses to hand out any other.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from vesuve.transport import ABSENT, Transport

METAS = (".zgroup", ".zattrs", "0/.zarray", "0/.zattrs")
HALF_THICKNESS = 54   # the 109 layers of a render, either side of the surface
MARGIN = 32           # voxels, along each axis, around each carried point
ABSENT_MARK = ".absent"


def chunks_of_crop(points: np.ndarray, spacing: float, crop: dict, chunk: int = 128, half: int = HALF_THICKNESS,
                   margin: int = MARGIN, step: int = 16, layer_step: int = 6) -> set[tuple[int, int, int]]:
    """The chunks `(z, y, x)` of the volume that rendering the crop reads.

    The points of the surface, bilinear between those of the grid, every `step` pixels, carried along the normal from
    `-half` to `half`, each with a margin of `margin` voxels on every axis. `points` is the tifxyz grid `(h, w, 3)` in
    `(x, y, z)`, `spacing` its spacing in render pixels.
    """
    s = 1.0 / float(spacing)
    u = np.arange(crop["x"], crop["x"] + crop["width"] + 1, step) * s
    v = np.arange(crop["y"], crop["y"] + crop["height"] + 1, step) * s
    V, U = np.meshgrid(v, u, indexing="ij")
    i0 = np.clip(np.floor(V).astype(int), 0, points.shape[0] - 2)
    j0 = np.clip(np.floor(U).astype(int), 0, points.shape[1] - 2)
    fv, fu = (V - i0)[..., None], (U - j0)[..., None]

    def bilinear(a):
        return ((1 - fv) * (1 - fu) * a[i0, j0] + (1 - fv) * fu * a[i0, j0 + 1]
                + fv * (1 - fu) * a[i0 + 1, j0] + fv * fu * a[i0 + 1, j0 + 1])

    p = bilinear(points)
    n = np.cross(bilinear(np.gradient(points, axis=1)), bilinear(np.gradient(points, axis=0)))
    with np.errstate(invalid="ignore", divide="ignore"):
        n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    good = np.isfinite(p).all(axis=-1) & np.isfinite(n).all(axis=-1) & (p > -1.0).all(axis=-1)
    p, n = p[good], n[good]
    out: set[tuple[int, int, int]] = set()
    shifts = np.array([[dx, dy, dz] for dx in (-margin, margin) for dy in (-margin, margin) for dz in (-margin, margin)])
    for k in list(range(-half, half + 1, layer_step)) + [half]:
        q = p + k * n
        for d in shifts:
            c = np.floor((q + d) / chunk).astype(int)
            out.update(map(tuple, c[:, ::-1].tolist()))
    return {c for c in out if min(c) >= 0}


class Mirror:
    """A folder that `vc_render_tifxyz -v` opens as the volume, holding only the chunks asked for."""

    def __init__(self, folder: Path, source: str, transport=None, journal=None):
        self.folder, self.source = Path(folder), source.rstrip("/")
        # More patience than a single read: one failed name resolution stopped the research render of the segment.
        self.transport, self.journal = transport or Transport(retries=7, pause=1.0, journal=journal), journal
        self._chunk_bytes: int | None = None

    def path(self, c: tuple[int, int, int]) -> Path:
        return self.folder / "0" / str(c[0]) / str(c[1]) / str(c[2])

    def prepare(self) -> None:
        """The metadata of the volume, copied as they are: that is what makes the folder a volume the renderer opens."""
        for name in METAS:
            p = self.folder / name
            if p.is_file():
                continue
            r = self.transport.get(f"{self.source}/{name}")
            if r.body is None:
                raise RuntimeError(f"{self.source}/{name}: {r.reason}")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(r.body)

    @property
    def chunk_bytes(self) -> int | None:
        """The size every chunk file must have, or None when the volume compresses its chunks (then no size is right)."""
        if self._chunk_bytes is None:
            z = json.loads((self.folder / "0" / ".zarray").read_text())
            if z.get("compressor") is None and not z.get("filters"):
                self._chunk_bytes = int(np.prod(z["chunks"])) * np.dtype(z["dtype"]).itemsize
            else:
                self._chunk_bytes = 0
        return self._chunk_bytes or None

    def is_sound(self, c: tuple[int, int, int]) -> bool:
        """The chunk is there at its one right size, or the bucket declared it absent."""
        p = self.path(c)
        if p.with_suffix(ABSENT_MARK).is_file():
            return True
        if not p.is_file():
            return False
        size = self.chunk_bytes
        return size is None or p.stat().st_size == size

    def fill(self, chunks: set, threads: int = 16) -> dict:
        """The chunks the mirror lacks, or holds at a wrong size, downloaded; a sound chunk is not fetched again.

        ⚠ Written to a temporary file, flushed to the disk, then renamed: a download cut short, or a machine going down,
        never leaves a chunk that reads as complete.
        """
        self.prepare()
        wrong = [c for c in chunks if self.path(c).is_file() and not self.is_sound(c)]
        missing = sorted(c for c in chunks if not self.is_sound(c))
        start = time.monotonic()

        def one(c):
            r = self.transport.get(f"{self.source}/0/{c[0]}/{c[1]}/{c[2]}")
            f = self.path(c)
            f.parent.mkdir(parents=True, exist_ok=True)
            if r.body is None:
                if r.reason == ABSENT:
                    f.with_suffix(ABSENT_MARK).write_text("absent from the bucket\n")
                    return 0, None
                return 0, r.reason
            size = self.chunk_bytes
            if size is not None and len(r.body) != size:
                return 0, f"a chunk of {len(r.body)} bytes where the volume says {size}"
            tmp = f.with_suffix(".tmp")
            with open(tmp, "wb") as fh:
                fh.write(r.body)
                fh.flush()
                os.fsync(fh.fileno())
            tmp.replace(f)
            return len(r.body), None

        with ThreadPoolExecutor(max_workers=int(threads)) as pool:
            got = list(pool.map(one, missing))
        seconds = time.monotonic() - start
        failed = {f"{c[0]}/{c[1]}/{c[2]}": why for c, (_, why) in zip(missing, got) if why}
        read = sum(n for n, _ in got)
        return {"chunks": len(chunks), "downloaded": len(missing) - len(failed), "failed": failed,
                "replaced_at_a_wrong_size": len(wrong), "bytes": int(read), "seconds": round(seconds, 1),
                "mb_per_s": round(read / 1e6 / seconds, 1) if seconds > 0 and missing else None}

    def empty(self, keep: set) -> int:
        """The chunks nothing asks for any more, removed. Returns how many."""
        root = self.folder / "0"
        if not root.is_dir():
            return 0
        n = 0
        for f in root.glob("*/*/*"):
            if f.suffix == ".tmp" or f.name.startswith("."):
                continue
            c = (int(f.parent.parent.name), int(f.parent.name), int(f.name.split(".")[0]))
            if c not in keep:
                f.unlink()
                n += 1
        return n
