#!/usr/bin/env python3
"""Rendre le profil de profondeur en image — la preuve visuelle que le concours réclame.

⚠ La page `Prizes` insiste partout sur la preuve visuelle : *« show visually that
papyrus fibers are visible on your output surface, and it doesn't jump across sheets in
cross-section »*. Un tableau de rho ne remplace pas une image qu'on regarde.

⚠ **Tracé à la main avec PIL, sans matplotlib** : il est absent de cet environnement, et
l'ajouter pour dessiner deux courbes ferait dépendre une figure d'une pile graphique
entière. Ce que le tracé doit montrer tient en trois traits — la courbe, la couche
tracée, et la bande de matière.

⚠ **Les deux panneaux partagent leur échelle verticale** (chacun normalisé dans sa
propre pile, comme partout ici) et leur échelle horizontale n'est comparable que si les
piles ont le même nombre de couches — sinon le rapport est écrit sous chaque panneau
plutôt que laissé à l'œil.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

MARGIN, WIDTH, HEIGHT = 54, 460, 240


def draw(panel, curve, traced: int, title: str, subtitle: str, colour,
         first_layer: int, last_layer: int):
    from PIL import ImageDraw

    art = ImageDraw.Draw(panel)
    n = len(curve)
    x = lambda i: MARGIN + i * (WIDTH - 2 * MARGIN) / max(1, n - 1)
    y = lambda v: HEIGHT - MARGIN - v * (HEIGHT - 2 * MARGIN)

    art.rectangle([MARGIN, MARGIN, WIDTH - MARGIN, HEIGHT - MARGIN], outline=(190, 190, 190))
    # ⚠ La couche tracee est un TRAIT, pas une annotation en legende : c'est la
    # reference par rapport a laquelle tout l'instrument se lit.
    tx = x(traced)
    for yy in range(MARGIN, HEIGHT - MARGIN, 6):
        art.line([tx, yy, tx, yy + 3], fill=(200, 60, 60), width=2)
    art.text((tx + 4, MARGIN + 2), "trace", fill=(200, 60, 60))

    art.line([(x(i), y(v)) for i, v in enumerate(curve)], fill=colour, width=2)
    peak = int(np.argmax(curve))
    art.ellipse([x(peak) - 4, y(curve[peak]) - 4, x(peak) + 4, y(curve[peak]) + 4],
                outline=colour, width=2)
    art.text((MARGIN, 12), title, fill=(20, 20, 20))
    art.text((MARGIN, 28), subtitle, fill=(90, 90, 90))
    # ⚠ L'axe porte les NUMEROS DE COUCHE reels, pas l'indice dans la fenetre lue :
    # une fenetre 15-40 affichant « 0 » et « 25 » se lit comme une pile de 26 couches
    # commencant a zero, ce qui est faux et rend la couche tracee (32) inexplicable.
    art.text((MARGIN, HEIGHT - MARGIN + 8), f"couche {first_layer}", fill=(120, 120, 120))
    art.text((WIDTH - MARGIN - 46, HEIGHT - MARGIN + 8), f"{last_layer}", fill=(120, 120, 120))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deux profils de profondeur côte à côte, en image.",
        epilog="Un rho ne remplace pas une image qu'on regarde.",
    )
    parser.add_argument("profils", type=Path, nargs="+",
                        help="JSON de depth_profile.py (mode fenêtre unique)")
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    from PIL import Image

    entries = []
    for path in args.profils:
        for entry in json.loads(path.read_text()):
            entries.append(entry)
    if not entries:
        print("erreur : aucun profil", file=sys.stderr)
        return 2

    panels = []
    for entry in entries:
        mean = np.asarray(entry["mean"], float)
        span = mean.max() - mean.min()
        curve = (mean - mean.min()) / span if span > 0 else mean * 0
        layers = entry["layers"]
        traced = 32 - layers[0] if layers[0] <= 32 <= layers[-1] else len(curve) // 2
        peak = layers[int(np.argmax(curve))]
        gap = abs(peak - 32) * 7.91
        panel = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        colour = (40, 110, 190) if gap <= 50 else (190, 90, 20)
        draw(panel, curve, max(0, min(len(curve) - 1, traced)),
             entry["folder"][:34],
             f"pic couche {peak} / ecart a la trace {gap:.0f} um",
             colour, layers[0], layers[-1])
        panels.append(panel)

    sheet = Image.new("RGB", (WIDTH * len(panels), HEIGHT), (255, 255, 255))
    for index, panel in enumerate(panels):
        sheet.paste(panel, (index * WIDTH, 0))
    sheet.save(args.out)
    print(f"{args.out}  {sheet.size[0]} x {sheet.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
