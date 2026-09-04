#!/usr/bin/env python3
"""Dans quel sens comptent les indices de spire, et ce qu'un pas d'indice mesure.

Deux panneaux, parce que la mesure répond à deux questions qu'il ne faut pas mélanger :

- **à gauche, le SENS.** Pour chaque paire de spires consécutives, la part de cellules
  (hauteur, angle) où `w_{k+1}` est plus loin de l'axe. ⚠ La ligne des 50 % est tracée parce
  qu'elle est le vrai zéro de la question : un indice qui ne voudrait rien dire y resterait
  collé. Sans elle, un nuage de points à 95 % ressemble à un nuage de points.
- **à droite, l'UNITÉ.** L'écart radial médian contre l'écart d'indice. La droite passant par
  l'origine n'est pas ajustée, elle est **construite sur le seul point Δw = 1** : elle demande
  donc « les autres tombent-ils dessus ? », ce qu'une régression ne demanderait pas puisqu'elle
  passerait au mieux par tous.

⚠ Dessiné avec PIL, comme toutes les figures du dépôt (`figure_commune.py`) : matplotlib est
absent de cet environnement et l'ajouter pour deux nuages ferait dépendre une figure d'une pile
graphique entière.

Usage :
    uv run python src/figures/figure_sens_des_indices.py \\
        --json docs/mesures/le_sens_des_indices.json \\
        --sortie docs/article/figures/sens_des_indices.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
from figure_commune import police  # noqa: E402

LARGEUR, HAUTEUR = 470, 300
MARGE_G, MARGE_D, MARGE_H, MARGE_B = 62, 18, 40, 46

VERT = (31, 111, 67)
BRIQUE = (140, 58, 18)
GRIS = (150, 150, 150)
ENCRE = (40, 40, 40)


def _cadre(art, titre, sous_titre, f_titre, f_petit):
    art.text((MARGE_G - 46, 10), titre, fill=ENCRE, font=f_titre)
    art.text((MARGE_G - 46, 26), sous_titre, fill=(110, 110, 110), font=f_petit)
    art.rectangle([MARGE_G, MARGE_H, LARGEUR - MARGE_D, HAUTEUR - MARGE_B], outline=(205, 205, 205))


def panneau_sens(r: dict):
    """
    @brief La part de cellules où la spire suivante est plus loin de l'axe, spire par spire.
    """
    from PIL import Image, ImageDraw

    f_titre, f_petit = police(13, 10)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), "white")
    art = ImageDraw.Draw(img)
    _cadre(art, "le sens des indices", f"{r['rouleau']} — {r['cellules_comparees']} cellules "
           f"(hauteur, angle)", f_titre, f_petit)

    c = r["consecutives"]
    xs = [x["de"] for x in c]
    x0, x1 = min(xs), max(xs)
    px = lambda w: MARGE_G + (w - x0) * (LARGEUR - MARGE_G - MARGE_D) / max(1, x1 - x0)  # noqa: E731
    py = lambda v: HAUTEUR - MARGE_B - (v / 100.0) * (HAUTEUR - MARGE_H - MARGE_B)  # noqa: E731

    # ⚠ La ligne des 50 % AVANT les points : c'est la reference, pas une annotation. Un lecteur
    # doit voir contre quoi 95 % se lit, sinon le nuage ne dit rien.
    for xx in range(MARGE_G, LARGEUR - MARGE_D, 7):
        art.line([xx, py(50), xx + 3, py(50)], fill=GRIS)
    art.text((MARGE_G + 4, py(50) - 13), "50 % — un indice qui ne voudrait rien dire",
             fill=(130, 130, 130), font=f_petit)

    for a, b in zip(c, c[1:]):
        art.line([px(a["de"]), py(a["part_vers_l_exterieur"] * 100),
                  px(b["de"]), py(b["part_vers_l_exterieur"] * 100)], fill=VERT, width=1)
    for x in c:
        cx, cy = px(x["de"]), py(x["part_vers_l_exterieur"] * 100)
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=VERT)

    for v in (0, 50, 100):
        art.text((MARGE_G - 30, py(v) - 6), f"{v} %", fill=(90, 90, 90), font=f_petit)
    art.text((MARGE_G, HAUTEUR - 30), f"spire w{x0:03d}", fill=(90, 90, 90), font=f_petit)
    art.text((LARGEUR - MARGE_D - 46, HAUTEUR - 30), f"w{x1:03d}", fill=(90, 90, 90), font=f_petit)
    art.text((MARGE_G, HAUTEUR - 17),
             f"vers l'extérieur dans {r['part_vers_l_exterieur'] * 100:.1f} % des cellules",
             fill=VERT, font=f_petit)
    return img


def panneau_unite(r: dict):
    """
    @brief L'écart radial contre l'écart d'indice — un pas d'indice est-il une unité ?
    """
    from PIL import Image, ImageDraw

    f_titre, f_petit = police(13, 10)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), "white")
    art = ImageDraw.Draw(img)
    _cadre(art, "un pas d'indice est une unité",
           f"voxel {r['voxel_um']:.3f} µm, décodé de l'aire", f_titre, f_petit)

    vox = r["voxel_um"]
    pts = [(p["saut"], p["median_vx"] * vox) for p in r["par_pas"]]
    smax = max(s for s, _ in pts)
    vmax = max(v for _, v in pts) * 1.12
    px = lambda s: MARGE_G + s * (LARGEUR - MARGE_G - MARGE_D) / (smax * 1.08)  # noqa: E731
    py = lambda v: HAUTEUR - MARGE_B - v * (HAUTEUR - MARGE_H - MARGE_B) / vmax  # noqa: E731

    # ⚠⚠ La droite est CONSTRUITE sur le seul point Δw = 1, pas ajustee sur les quatre. Une
    # regression passerait au mieux par tous et ne pourrait donc pas les contredire ; celle-ci
    # pose une prediction que les trois autres points confirment ou non.
    unite = pts[0][1] / pts[0][0]
    art.line([px(0), py(0), px(smax * 1.06), py(unite * smax * 1.06)], fill=GRIS, width=1)
    art.text((px(smax * 0.42), py(unite * smax * 0.42) - 15),
             f"proportionnel — {unite:.0f} µm par pas", fill=(120, 120, 120), font=f_petit)

    for s, v in pts:
        cx, cy = px(s), py(v)
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=BRIQUE)
        art.text((cx + 7, cy - 6), f"{v:.0f} µm", fill=BRIQUE, font=f_petit)

    art.text((MARGE_G - 52, MARGE_H - 2), "µm", fill=(90, 90, 90), font=f_petit)
    art.text((LARGEUR - MARGE_D - 92, HAUTEUR - 30), "écart d'indice |Δw|",
             fill=(90, 90, 90), font=f_petit)
    art.text((MARGE_G, HAUTEUR - 17),
             f"écart par pas : {r['ecart_median_um']:.0f} µm "
             f"(p25 {r['ecart_p25_um']:.0f}, p75 {r['ecart_p75_um']:.0f})",
             fill=BRIQUE, font=f_petit)
    return img


def dessiner(r: dict, sortie: Path) -> None:
    from PIL import Image

    g, d = panneau_sens(r), panneau_unite(r)
    img = Image.new("RGB", (LARGEUR * 2 + 12, HAUTEUR), "white")
    img.paste(g, (0, 0))
    img.paste(d, (LARGEUR + 12, 0))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    print(f"écrit : {sortie}  ({img.width}×{img.height})")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=Path("docs/mesures/le_sens_des_indices.json"))
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/article/figures/sens_des_indices.png"))
    a = p.parse_args()
    if not a.json.is_file():
        raise SystemExit(
            f"mesure absente : {a.json}\n"
            f"  la produire :  uv run python src/excision/le_sens_des_indices.py --json {a.json}")
    dessiner(json.loads(a.json.read_text(encoding="utf-8")), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
