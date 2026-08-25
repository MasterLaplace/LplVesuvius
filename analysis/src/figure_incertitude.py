#!/usr/bin/env python3
"""Les treize rouleaux du prix, avec l'incertitude que `16` n'affichait pas.

⚠⚠ **Ce que cette figure etablit.** `16` classe les treize sur la part de fenetres
indissociables -- 4 % a 24 % contre 0 % pour le temoin -- et en tire une designation. La
figure de `16` montre ces parts comme des barres, c'est-a-dire comme des points. Ce sont
des proportions sur **15 a 35 fenetres**.

Ici chaque rouleau est un **intervalle**, pas un point. Et la forme se lit d'un coup :
**ils se recouvrent tous**, y compris avec celui du temoin -- dont le zero est compatible
avec un taux reel allant jusqu'a 14 %. C'est la raison pour laquelle aucune des 78 paires
n'est separee, et elle n'a pas besoin d'un test pour etre vue.

⚠ La barre du temoin est dessinee en PREMIER et en pleine largeur derriere les autres :
c'est le seul moyen de montrer qu'un rouleau « a 24 % » et le temoin « a 0 % » partagent
du domaine. Une figure qui les mettrait cote a cote sans les superposer rendrait le
recouvrement invisible, ce qui est exactement l'erreur de lecture qu'elle corrige.

⚠ La ligne des 10 % est INDICATIVE : le prix tolere « less than 10 % » de patches
sautes, en fraction de **surface de recto** ; la part mesuree ici est une fraction de
**fenetres sondees**. Elle est tracee en pointille pour cette raison, et l'annotation le
dit.

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python analysis/src/figure_incertitude.py \\
        --entree docs/incertitude_carte.json --sortie docs/images/33_incertitude.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARGE_G, MARGE_H, LIGNE, LARGEUR = 150, 96, 28, 1120
X0, LARG = 210, 700          # origine et largeur de l'axe des parts
PART_MAX = 0.55              # borne de l'axe : au-dela aucun IC ne monte


def x_de(part: float) -> int:
    return X0 + int(min(part, PART_MAX) / PART_MAX * LARG)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/incertitude_carte.json")
    ap.add_argument("--sortie", type=Path,
                    default=Path(__file__).resolve().parents[2] / "docs/images/33_incertitude.png")
    a = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord incertitude_carte.py --json",
              file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    lignes = sorted(d["lignes"], key=lambda r: r["part"])
    temoin = d["temoin"]

    hauteur = MARGE_H + len(lignes) * LIGNE + 118
    im = Image.new("RGB", (LARGEUR, hauteur), (255, 255, 255))
    art = ImageDraw.Draw(im)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "Part de fenêtres indissociables — avec son incertitude",
             fill=(20, 20, 20), font=f_t)
    art.text((14, 42),
             f"{d['paires_separees']} des {d['paires']} paires de rouleaux sont réellement "
             f"séparées ; {len(d['distinguables_holm'])} des {len(lignes)} se distinguent du témoin.",
             fill=(150, 90, 20), font=f_n)

    bas = MARGE_H + len(lignes) * LIGNE
    # La bande du temoin, en premier et sur toute la hauteur : c'est ce qui rend le
    # recouvrement visible au lieu de le laisser deduire.
    art.rectangle([x_de(temoin["ic95"][0]), MARGE_H - 10, x_de(temoin["ic95"][1]), bas + 4],
                  fill=(232, 243, 234))
    art.line([x_de(temoin["ic95"][1]), MARGE_H - 10, x_de(temoin["ic95"][1]), bas + 4],
             fill=(120, 175, 135))
    art.text((x_de(temoin["ic95"][1]) + 6, MARGE_H - 26),
             f"borne haute du témoin : {temoin['ic95'][1]:.0%}", fill=(60, 130, 80), font=f_p)

    # Graduations, puis la ligne des 10 % en pointillé (grandeur différente).
    for t in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        x = x_de(t)
        art.line([x, bas + 6, x, bas + 12], fill=(180, 180, 180))
        art.text((x - 10, bas + 15), f"{t:.0%}", fill=(120, 120, 120), font=f_p)
    x10 = x_de(0.10)
    for y in range(MARGE_H - 10, bas + 4, 7):
        art.line([x10, y, x10, y + 3], fill=(170, 120, 200))

    for i, r in enumerate(lignes):
        y = MARGE_H + i * LIGNE
        art.text((14, y + 4), r["rouleau"], fill=(40, 40, 40), font=f_n)
        art.text((104, y + 5), f"{r['k']}/{r['n']}", fill=(130, 130, 130), font=f_p)
        b, h = x_de(r["ic95"][0]), x_de(r["ic95"][1])
        art.line([b, y + 11, h, y + 11], fill=(190, 90, 40), width=2)
        art.line([b, y + 6, b, y + 16], fill=(190, 90, 40))
        art.line([h, y + 6, h, y + 16], fill=(190, 90, 40))
        px = x_de(r["part"])
        art.ellipse([px - 4, y + 7, px + 4, y + 15], fill=(150, 60, 20))
        art.text((X0 + LARG + 22, y + 4), f"{r['part']:.0%}", fill=(120, 120, 120), font=f_p)

    art.text((14, bas + 40),
             f"Point : la part mesurée. Barre : intervalle de confiance exact à 95 % "
             f"(Clopper–Pearson, n = 15 à 35 fenêtres).",
             fill=(70, 70, 70), font=f_n)
    art.text((14, bas + 60),
             f"Bande verte : l'intervalle du témoin PHerc0139, à {temoin['k']}/{temoin['n']}. "
             f"Son zéro est compatible avec un taux réel jusqu'à {temoin['ic95'][1]:.0%}.",
             fill=(60, 130, 80), font=f_n)
    art.text((14, bas + 80),
             "Trait violet : les 10 % que le prix tolère — INDICATIF, c'est une part de "
             "surface, pas de fenêtres.",
             fill=(140, 100, 170), font=f_n)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x{hauteur}, {len(lignes)} rouleaux)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
