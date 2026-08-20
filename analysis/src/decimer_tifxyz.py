#!/usr/bin/env python3
"""Sous-echantillonner une surface tifxyz, pour mesurer ce qu'un maillage grossier VOIT.

⚠⚠ Pourquoi cet outil existe. `26` §9 conclut que `step_size >= 20` rend une trace
propre, sur la foi de comptes d'auto-intersections nuls. En auditant les rapports bruts de
cette campagne, une asymetrie apparait : le detecteur teste **348 millions** de paires de
quads a pas 5, et **36 149** a pas 40. Un maillage grossier n'est pas seulement une trace
differente, c'est une **description moins fine de la meme surface** -- et un test qui
compare des quads ne peut pas voir un croisement que le maillage ne represente plus.

« Zero croisement a pas 40 » pourrait donc vouloir dire deux choses tres differentes :
la trace est propre, ou le detecteur ne voit plus. Une seule facon de les separer : ⭐
prendre une surface **dont on SAIT qu'elle se croise**, la degrader, et regarder si le
verdict survit.

Cet outil fait la degradation. Il ne trace rien et ne remesure rien : il prend une grille
tifxyz et n'en garde qu'une ligne et une colonne sur k, ce qui est exactement ce qu'un
pas k fois plus grand aurait produit comme densite de maillage -- a ceci pres que la
GEOMETRIE est identique, donc tout changement de verdict vient du maillage seul.

⚠ `scale` est divise par k : c'est le facteur qui relie l'indice de grille au parametre
de surface, et le laisser tel quel ferait croire a l'outil aval que deux sommets voisins
sont k fois plus proches qu'ils ne le sont.

⚠ `area_cm2` est RECOPIE tel quel et le champ `decime_depuis` le dit : l'aire de la
surface n'a pas change, c'est sa description qui a change. Recalculer une aire plus
petite depuis un maillage plus grossier ferait croire a une perte de surface.

Usage :
    uv run python analysis/src/decimer_tifxyz.py entree.tifxyz sortie.tifxyz --facteur 2
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entree", type=Path)
    ap.add_argument("sortie", type=Path)
    ap.add_argument("--facteur", type=int, default=2,
                    help="ne garder qu'une ligne et une colonne sur k")
    a = ap.parse_args()

    import numpy as np
    import tifffile

    if a.facteur < 2:
        print("le facteur doit valoir au moins 2", file=sys.stderr)
        return 2
    meta_p = a.entree / "meta.json"
    if not meta_p.is_file():
        print(f"pas de meta.json dans {a.entree}", file=sys.stderr)
        return 2
    meta = json.loads(meta_p.read_text())

    a.sortie.mkdir(parents=True, exist_ok=True)
    formes = {}
    for nom in ("x", "y", "z", "generations"):
        src = a.entree / f"{nom}.tif"
        if not src.is_file():
            continue
        g = tifffile.imread(src)
        petit = g[::a.facteur, ::a.facteur]
        formes[nom] = (g.shape, petit.shape)
        tifffile.imwrite(a.sortie / f"{nom}.tif", petit)

    meta = dict(meta)
    meta["scale"] = [s / a.facteur for s in meta.get("scale", [1.0, 1.0])]
    meta["decime_depuis"] = {
        "source": str(a.entree), "facteur": a.facteur,
        "note": ("grille sous-echantillonnee ; la GEOMETRIE est inchangee, seule sa "
                 "description est plus grossiere. area_cm2 est celle de l'original."),
    }
    (a.sortie / "meta.json").write_text(json.dumps(meta, indent=4) + "\n")
    for nom, (avant, apres) in formes.items():
        print(f"  {nom}.tif : {avant[0]}×{avant[1]} → {apres[0]}×{apres[1]}")
    print(f"écrit : {a.sortie}  (facteur {a.facteur}, "
          f"scale {meta['scale'][0]:.6f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
