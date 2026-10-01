"""What the program embeds from the research, per segment, and how to read it back.

The files under `data/segments/<segment>/` are extracted from `docs/mesures/` of the `experimental` branch by
`tools/extract_from_research.py`, and a test requires them to equal a fresh extraction: the embedded data
cannot drift from its source without the suite saying so.
"""
from __future__ import annotations

import gzip
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent / "data" / "segments"


def embedded_segments() -> list[str]:
    return sorted(p.name for p in ROOT.iterdir() if (p / "context.json").exists())


def _read(path: Path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


@lru_cache(maxsize=8)
def segment(name: str) -> dict:
    """{context, presence (boolean A), published bands, control sources} of an embedded segment."""
    d = ROOT / name
    if not (d / "context.json").exists():
        raise FileNotFoundError(f"segment {name} is not embedded; embedded: {embedded_segments()}")
    presence = _read(d / "presence.json.gz")
    A = np.array([[c == "1" for c in r] for r in presence["rows"]], dtype=bool)
    sources = {n: {"domain": {f: {tuple(c) for c in s} for f, s in S["domain"].items()},
                   "steps": {f: {(r, c): p for r, c, p in s} for f, s in S["steps"].items()}}
               for n, S in _read(d / "control_sources.json.gz").items()}
    return {"context": _read(d / "context.json"), "presence": A,
            "bands": _read(d / "published_bands.json.gz")["bands"], "sources": sources}


def _read_array(path: Path) -> np.ndarray:
    import io
    return np.load(io.BytesIO(gzip.decompress(path.read_bytes())), allow_pickle=False)


@lru_cache(maxsize=2)
def rays(name: str):
    """What the transfer to the next winding is computed from on an embedded surface: the prediction's samples along
    the normal of each point of the transfer's mesh (`247`, `248`), read by the research from `m7`."""
    from vesuve.transfer.next_winding import Rays, depths

    d = ROOT / name / "correction"
    if not (d / "rays.json").exists():
        raise FileNotFoundError(f"segment {name} embeds no rays (looked in {d})")
    ctx = _read(d / "rays.json")
    rows, columns = _read_array(d / "rays_grid.npy.gz")
    seen = np.unpackbits(_read_array(d / "rays_seen.npy.gz"), axis=1, count=ctx["samples"]).astype(bool)
    side = 1.0 if ctx["side"] == "plus" else -1.0
    t = depths(side, (ctx["samples"] - 1) * ctx["depth_step_voxels"])
    return Rays(depths=t, seen=seen, rows=rows.astype(np.intp), columns=columns.astype(np.intp),
                grid=tuple(ctx["grid"]), side=side, step=ctx["step_voxels"], half_sheet=ctx["half_sheet_voxels"],
                prediction=ctx["prediction"], path=ctx["path"], level=ctx["level"], factor=ctx["factor"])


@lru_cache(maxsize=2)
def correction(name: str) -> dict:
    """What the hand-free correction reads on an embedded surface: the transfer to the next winding, the judges (for
    scoring only), the step tables of the reference and of the produced winding, the candidate blocks and the slip of
    one winding. Embedded for the segment of `275`, where the correction was validated, and for the band of `281`,
    where it was not."""
    d = ROOT / name / "correction"
    if not (d / "context.json").exists():
        raise FileNotFoundError(f"segment {name} embeds no correction inputs (looked in {d})")
    ctx = _read(d / "context.json")
    tables = {(role, *map(int, k.split("_"))): t for role, by_block in _read(d / "tables.json.gz").items()
              for k, t in by_block.items()}
    return {"context": ctx, "transfer": _read_array(d / "transfer.npy.gz"), "surfaces": ("reference", "produced"),
            "research_corrected": _read_array(d / "research_corrected_transfer.npy.gz"),
            "judges": [_read_array(d / f"judge_{j}.npy.gz") for j in ctx["judges"]],
            "tables": tables, "candidates": {tuple(b) for b in ctx["candidates"]}}
