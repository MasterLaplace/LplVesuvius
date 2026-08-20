#!/usr/bin/env python3
"""Que voit le traceur A CET ENDROIT ? -- la prediction de surface autour d'un point.

⚠⚠ Pourquoi ce fichier existe. `38` etablit que nos traces ne suivent aucune feuille, et
`tools/sens_de_la_normale.sh` montre que leur profil de profondeur est plat a **100 %**
dans les deux sens de normale. `25` dit ce que veut dire un profil plat : la surface longe
l'empilement au lieu de le traverser.

⭐ Or nous avons rejoue **LA GRAINE D'UN SEGMENT OFFICIEL** -- celui-la meme qui converge
chez eux -- et notre trace en part quand meme a plat. La difference ne peut donc pas venir
de l'endroit choisi. Elle vient de ce que le traceur LIT la : eux ont utilise un cache EDT
prive, nous lisons la prediction de surface publiee.

Cette sonde repond a la question directement : autour de ce point, la prediction publiee
a-t-elle une structure de feuille -- ou est-elle saturee ?

  occupation ~ 1  : tout est « surface », donc aucun gradient a suivre. Un traceur y part
                    dans n'importe quelle direction, et rien ne le ramene.
  occupation ~ 0  : rien a suivre non plus.
  planarite basse : de la matiere, mais pas organisee en nappe.

⚠ Les seuils par defaut sont ceux de `trouver_graine.py` (0,02 et 0,80) parce que ce sont
ceux qui ont servi a CHOISIR nos graines : les reutiliser rend la sonde comparable a la
selection, au lieu d'introduire une troisieme echelle.

Usage :
    uv run python analysis/src/sonder_point.py <cle S3 .zarr> --xyz 4682 2740 13350 \\
        --level 0 --bloc 8
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trouver_graine import lire_chunk, scores_du_chunk  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zarr", help="clé S3 de la prédiction de surface")
    ap.add_argument("--xyz", type=float, nargs=3, required=True,
                    help="le point, en voxels du NIVEAU 0")
    ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--bloc", type=int, default=8)
    ap.add_argument("--lissage", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--json")
    a = ap.parse_args()

    url = f"{BUCKET}/{a.zarr.strip('/')}"
    meta = array_meta(url, a.level, a.timeout)
    dz, dy, dx = meta["chunks"]
    # ⚠ Les coordonnees sont donnees au niveau 0 : on les descend au niveau demande avant
    # de chercher le chunk. Les melanger placerait la sonde a un facteur 2^level du point.
    f = 2 ** a.level
    x, y, z = (v / f for v in a.xyz)
    cz, cy, cx = int(z // dz), int(y // dy), int(x // dx)
    bloc = lire_chunk(url, a.level, meta, cz, cy, cx, a.timeout)
    if bloc is None:
        print(f"chunk absent — le point n'est pas couvert par la prédiction "
              f"(chunk z{cz} y{cy} x{cx})")
        return 1

    s = scores_du_chunk(bloc, a.bloc, a.lissage)
    if s is None:
        print("bloc illisible ou vide")
        return 1

    # ⚠ `scores_du_chunk` rend ses grilles APLATIES, avec la forme 3D dans s["forme"].
    # La premiere version lisait `.shape` -- donc une forme 1D -- et levait un ValueError
    # a l'unpacking. Un plantage ici serait passe pour « le point n'est pas couvert ».
    forme = s["forme"]
    iz, iy, ix = (int((v % d) // a.bloc) for v, d in ((z, dz), (y, dy), (x, dx)))
    iz, iy, ix = (min(i, n - 1) for i, n in zip((iz, iy, ix), forme))
    plat = (iz * forme[1] + iy) * forme[2] + ix
    occ = float(s["occupation"][plat])
    pla = float(s["planarite"][plat])

    print(f"point ({a.xyz[0]:.0f}, {a.xyz[1]:.0f}, {a.xyz[2]:.0f}) "
          f"— niveau {a.level}, bloc {a.bloc}³\n")
    print(f"  occupation de la cellule : {occ:.3f}")
    print(f"  planarité de la cellule  : {pla:.3f}")
    print(f"  occupation du chunk      : médiane {float(np.median(s['occupation'])):.3f}, "
          f"part saturée (>0,80) {float((s['occupation'] > 0.80).mean()):.1%}")
    print(f"  planarité du chunk       : médiane {float(np.median(s['planarite'])):.3f}")

    if occ > 0.80:
        print("\n  ⚠⚠ La cellule est SATURÉE : tout y est prédit « surface », donc il n'y a")
        print("     aucun gradient à suivre. Un traceur qui part de là n'a rien qui le")
        print("     ramène vers une feuille — il avance dans le plan.")
    elif occ < 0.02:
        print("\n  ⚠ La cellule est VIDE : rien à suivre non plus.")
    elif pla < 0.5:
        print("\n  ⚠ De la matière, mais peu organisée en nappe (planarité basse).")
    else:
        print("\n  ✅ Occupation et planarité dans la plage utilisable — la prédiction")
        print("     porte bien une structure de feuille à cet endroit.")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "zarr": a.zarr, "xyz": a.xyz, "level": a.level, "bloc": a.bloc,
            "occupation": occ, "planarite": pla,
            "occupation_mediane_chunk": float(np.median(s["occupation"])),
            "part_saturee_chunk": float((s["occupation"] > 0.80).mean()),
            "planarite_mediane_chunk": float(np.median(s["planarite"])),
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
