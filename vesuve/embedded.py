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
