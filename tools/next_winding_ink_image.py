"""The picture of slice 296 for the submission: the ink read on the produced winding, over the ink the segment carries there.

Slice 296 of the research reads the ink of the winding the transfer produces with the team's 2.4 µm model, and compares it
with the published ink map where the segment itself passes over that winding one turn further along its surface. This
draws, for the strip of row 176, our reading above the published ink at the counterpart, and a thin band marking where
the segment passes within half a sheet, the only place where the comparison judges anything: the brighter the band, the
larger the share of the column that is judged. The picture carries no text: its caption lives in the page that shows it.

    VESUVE_RESEARCH=<working copy of experimental> uv run python tools/next_winding_ink_image.py [--out <file>]

The data (`data/encre_du_tour_voisin/`) is not versioned: this runs where the research ran slice 296.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
WIDTH, STRIP, BAND, GAP = 2400, 400, 18, 12
AMBER = (214, 168, 74)
GROUND = (0, 0, 0)


def grey(a: np.ndarray, top: float) -> Image.Image:
    a = np.nan_to_num(np.asarray(a, dtype=float), nan=0.0)
    return Image.fromarray((np.clip(a / top, 0, 1) * 255).astype(np.uint8)).convert("RGB")


def draw(research: Path, out: Path) -> Path:
    data = np.load(research / "data" / "encre_du_tour_voisin" / "partie_a_pour_la_figure.npz")
    ours, theirs, near = data["lue"], data["au_vis_a_vis"], data["proche"]
    share = near.astype(float).mean(axis=0)
    band = (share[None, :, None] * np.array(AMBER, dtype=float)[None, None, :]).astype(np.uint8)
    picture = Image.new("RGB", (WIDTH, 2 * STRIP + BAND + 2 * GAP), GROUND)
    picture.paste(grey(ours, 1.0).resize((WIDTH, STRIP), Image.LANCZOS), (0, 0))
    picture.paste(Image.fromarray(band).resize((WIDTH, BAND), Image.BILINEAR), (0, STRIP + GAP))
    picture.paste(grey(theirs, 255.0).resize((WIDTH, STRIP), Image.LANCZOS), (0, STRIP + BAND + 2 * GAP))
    out.parent.mkdir(parents=True, exist_ok=True)
    picture.save(out, quality=86, optimize=True)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = os.environ.get("VESUVE_RESEARCH")
    p.add_argument("--research", type=Path, required=root is None, default=root)
    p.add_argument("--out", type=Path, default=HERE / "examples" / "grand-prize-render" / "next_winding_ink.jpg")
    a = p.parse_args()
    print(draw(Path(a.research).resolve(), a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
