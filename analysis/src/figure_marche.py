#!/usr/bin/env python3
"""Deux facons de suivre une nappe, sur la MEME coupe : le plus proche, et la crete.

⚠⚠ Ce que la figure doit rendre visible : le piege n'est pas que la methode naive
s'egare visiblement, c'est qu'elle reste un chemin CONNEXE ET PLAUSIBLE tout en changeant
de feuille. Rien dans sa forme ne dit qu'elle a change ; seul son RAYON le dit. Les deux
chemins sont donc dessines sur le meme fond et a la meme echelle, et l'ecart au rayon de
depart est imprime a cote.

⚠ L'escalier du chemin naif est un artefact de son pas entier (il saute de voxel en
voxel), pas le symptome recherche : un lisseur le ferait disparaitre sans rien corriger
du changement de feuille.

Les donnees viennent de `suivre_nappe` lui-meme : meme bloc, memes fonctions, memes
reglages que les temoins. Une figure qui re-implementerait la marche illustrerait un
autre programme que celui qui tourne.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from suivre_nappe import _nappe_cylindrique, marcher, marcher_plus_proche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
ECHELLE = 7          # pixels par voxel
N, RAYON, ECART = 96, 28.0, 4.0
FOND = (14, 14, 16)
NAPPE = (150, 150, 156)
NAIF = (232, 96, 72)
NOTRE = (250, 176, 60)


def main() -> int:
    from PIL import Image, ImageDraw

    c = N / 2.0
    bloc = _nappe_cylindrique(N, RAYON, epaisseur=1.0, entre=ECART)
    zz, yy, xx = np.mgrid[0:N, 0:N, 0:N]
    ang = np.arctan2(yy - c, xx - c)
    interne = np.hypot(yy - c, xx - c) < RAYON + ECART / 2
    bloc[(np.abs(ang - 0.6) < 0.30) & interne] = 0.0

    depart = [48.0, c + RAYON * np.sin(-0.8), c + RAYON * np.cos(-0.8)]
    naif = marcher_plus_proche(bloc, depart, n_pas=200)
    notre = marcher(bloc, depart, [0.0, 1.0, 0.0], n_pas=200)

    coupe = bloc[48]
    largeur = hauteur = N * ECHELLE
    im = Image.new("RGB", (largeur, hauteur + 96), FOND)
    d = ImageDraw.Draw(im)

    # Le fond : la coupe, en niveaux de gris, un carré par voxel.
    for y in range(N):
        for x in range(N):
            v = float(coupe[y, x])
            if v > 0.05:
                g = tuple(int(FOND[i] + (NAPPE[i] - FOND[i]) * min(v, 1.0)) for i in range(3))
                d.rectangle([x * ECHELLE, y * ECHELLE + 72,
                             (x + 1) * ECHELLE - 1, (y + 1) * ECHELLE + 71], fill=g)

    def tracer(res, couleur, epaisseur=3):
        pts = np.array(res["points"])
        if pts.ndim != 2 or len(pts) < 2:
            return 0.0
        xy = [(p[2] * ECHELLE + ECHELLE / 2, p[1] * ECHELLE + ECHELLE / 2 + 72) for p in pts]
        d.line(xy, fill=couleur, width=epaisseur, joint="curve")
        r = np.hypot(pts[:, 1] - c, pts[:, 2] - c)
        return float(np.max(np.abs(r - RAYON)))

    e_naif = tracer(naif, NAIF)
    e_notre = tracer(notre, NOTRE)

    # Le départ, commun aux deux.
    dx, dy = depart[2] * ECHELLE + ECHELLE / 2, depart[1] * ECHELLE + ECHELLE / 2 + 72
    d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], outline=(255, 255, 255), width=2)

    d.text((10, 8), "Deux facons de suivre une nappe - meme coupe, meme depart, "
                    f"deux spires a {ECART:.0f} voxels (30 um)", fill=(226, 226, 230))
    d.text((10, 30), f"au plus proche : quitte sa nappe de {e_naif:.1f} voxels "
                     f"- soit au-dela de la spire voisine", fill=NAIF)
    d.text((10, 48), f"sur la crete : reste a {e_notre:.2f} voxel, et s'ARRETE au trou "
                     f"({notre['pas_faits']} pas)", fill=NOTRE)

    sortie = RACINE / "docs" / "images" / "41_deux_marches.png"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    print(f"ecrit : {sortie}  ({im.width}x{im.height})")
    print(f"  naif  : ecart max {e_naif:.2f} voxels, {naif['pas_faits']} pas — {naif['arret']}")
    print(f"  notre : ecart max {e_notre:.2f} voxel, {notre['pas_faits']} pas — {notre['arret']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
