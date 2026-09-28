"""The certificate of an embedded segment: what the Grand Prize and the Progress audit both replay."""
from __future__ import annotations

import json
from pathlib import Path

from vesuve import embedded
from vesuve.lattice import certificate as cert
from vesuve.research import to_english


def extra_readings(paths) -> dict:
    """Bands read elsewhere (`vesuve … --read`, or the research's `la_couverture_sans_main.py --lire`): `{key: band}`.

    A file written by the research carries French keys; it goes through the research vocabulary, the one
    border where the two languages meet."""
    fresh = {}
    for p in paths or ():
        d = json.loads(Path(p).read_text())
        fresh.update((d.get("bands") or {}) if "bands" in d else to_english(d.get("les_bandes") or {}))
    return fresh


def certify_segment(segment: str, fresh: dict | None = None) -> tuple[dict, dict]:
    """(the embedded segment, the certificate); raises `ReadingRefused` if a fresh band does not fall back."""
    s = embedded.segment(segment)
    return s, cert.certify(s["presence"], s["bands"], s["context"]["procedure"], fresh=fresh, sources=s["sources"])


def published_ink_map_path(ctx: dict) -> str:
    """The bucket path of the segment's published ink map (reduced 8×, on the 2.4 µm volume)."""
    o, s = ctx["scroll"], ctx["segment"]
    return (f"{o}/segments/{s}/ink-detection/downsampled/{o}-{s}-2.4um-0.22m-78keV-volume-20260411134726-"
            f"20260417190342-new_canon_autoresearch_recipe-tile256-stride128-ds8.jpg")
