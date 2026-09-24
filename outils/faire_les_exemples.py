"""Copier une démo dans `exemples/` : les rapports tels quels, les images en aperçus d'au plus 1600 px.

Les sorties d'un pipeline ne sont pas versionnées (elles se refont, et la surface certifiée pèse 55 Mo) ; les
exemples le sont, pour qu'on voie sur GitHub ce que chaque prix rend, et ils disent de quelle commande ils
viennent.

    uv run vesuve demo --donnees <data/ de LplVesuvius> --sortie sorties/demo
    uv run python outils/faire_les_exemples.py sorties/demo
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ICI = Path(__file__).resolve().parents[1]


def main() -> int:
    source, cible = Path(sys.argv[1]), ICI / "exemples"
    for prix in sorted(p for p in source.iterdir() if (p / "rapport.json").exists()):
        d = cible / prix.name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for f in sorted(prix.iterdir()):
            if f.is_file() and f.suffix in (".md", ".json") and f.stat().st_size < 400_000:
                shutil.copy2(f, d / f.name)
            elif f.is_file() and f.suffix in (".png", ".jpg"):
                im = Image.open(f).convert("RGB")
                im.thumbnail((1600, 1600))
                im.save(d / f"{f.stem}.jpg", quality=85, optimize=True)
        print(f"{prix.name} : {len(list(d.iterdir()))} fichiers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
