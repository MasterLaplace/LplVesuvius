"""The prizes, their eligible scrolls and their volumes: what a pipeline checks before spending anything.

Sources: the rules of `https://scrollprize.org/prizes` downloaded on 2026-09-11 (`docs/rapports/PRIX.md` on the
`experimental` branch), and the public bucket's `metadata.min.json` index of 2026-08-29 for pixel size and energy.
⚠ The lists change: First Letters went from 13 to 23 scrolls between August 16 and September 11.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Volume:
    scroll: str
    volume: str
    pixel_um: float
    energy_kev: float
    distance_m: float = 1.2


# Grand Prize 2027: thirteen volumes, identified by their timestamp (PRIX.md §1).
GRAND_PRIZE = tuple(Volume(*v) for v in (
    ("PHerc0125", "20250821151825", 9.362, 113.0), ("PHerc0191", "20250821151635", 9.362, 113.0),
    ("PHerc0211", "20250821151803", 9.362, 113.0), ("PHerc0257", "20250821151750", 9.362, 113.0),
    ("PHerc0268", "20251110183117", 8.64, 116.0), ("PHerc0358", "20250821151737", 9.362, 113.0),
    ("PHerc0800", "20250521135224", 8.64, 116.0), ("PHerc0813", "20250821151723", 9.362, 113.0),
    ("PHerc0826", "20250821151701", 9.362, 113.0), ("PHerc1203", "20250820131727", 9.362, 113.0),
    ("PHerc1218", "20250521120456", 8.64, 116.0), ("PHerc1447", "20250521151220", 8.64, 116.0),
    ("PHerc1545", "20250821151648", 9.362, 113.0),
))

# First Letters: the thirteen of the Grand Prize and ten more "where no text has been read yet" (PRIX.md §0, §2).
FIRST_LETTERS = GRAND_PRIZE + tuple(Volume(*v) for v in (
    ("PHerc0175A", "20250521115057", 8.64, 116.0), ("PHerc0175B", "20250521125822", 8.64, 116.0),
    ("PHerc0306B", "20250521133212", 8.64, 116.0), ("PHerc0343", "20250521140437", 8.64, 116.0),
    ("PHerc0483A", "20250521140913", 8.64, 116.0), ("PHerc0483B", "20251124083638", 8.64, 116.0),
    ("PHerc0490A", "20250521151210", 8.64, 116.0), ("PHerc0490B", "20250521151215", 8.64, 116.0),
    ("PHerc0846A", "20250728152254", 9.362, 113.0), ("PHerc0846B", "20250804142305", 9.362, 113.0),
))

# The title of PHerc. Paris 4: every volume of Scroll 1, high resolution included (PRIX.md §3).
PARIS4_VOLUMES = tuple(Volume("PHercParis4", *v) for v in (
    ("20260411134726", 2.4, 78.0, 0.2), ("20260323153942", 2.4, 137.0, 0.2), ("20260608103018", 1.129, 78.0, 0.2),
))

# The production regime: what the published ink models saw in training (R6-F08).
PRODUCTION = Volume("production", "-", 2.4, 78.0, 0.2)

RULES = {
    "grand-prize": ("100 % of the recto unrolled (disconnected outer patches under 10 % may be skipped); 70 % of "
                    "the characters legible per column; a fully automated pipeline, at most 8 documented hours of "
                    "human input; integrated in VC3D; a Docker image; one mesh per column, `column_NN.tifxyz` in "
                    "the order of the windings; no data from a higher-resolution scan of the same volume; seeds "
                    "fixed and reported."),
    "first-letters": ("10 letters in a 4 cm² area of one of the 23 scrolls; a tifxyz and its flattening; a static "
                      "programmatic image, a 1 cm scale bar, named after its mesh, rows annotated, ink on a render "
                      "where the fibres show; show the text is not hallucinated (plausible letters on a held-out "
                      "region); no overlap between training and prediction; a human in the loop is allowed."),
    "paris4-title": ("an image of the title of Scroll 1 that papyrologists can read; any volume of Scroll 1, 2.4 µm "
                     "included; a tifxyz and its flattening; the ink in the context of the title search; "
                     "validation on a held-out region."),
    "progress": ("tools, results, NEGATIVE results and audits; the judges favour what detects failure cases of "
                 "existing methods on real scroll data."),
}


def _volumes(prize: str):
    return {"grand-prize": GRAND_PRIZE, "first-letters": FIRST_LETTERS, "paris4-title": PARIS4_VOLUMES}.get(prize)


def is_eligible(prize: str, scroll: str, volume: str | None = None) -> bool:
    volumes = _volumes(prize)
    if volumes is None:
        return True
    return any(v.scroll == scroll and (volume is None or v.volume == volume) for v in volumes)


def volume_of(prize: str, scroll: str) -> Volume | None:
    return next((v for v in (_volumes(prize) or ()) if v.scroll == scroll), None)
