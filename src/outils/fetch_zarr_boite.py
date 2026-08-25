#!/usr/bin/env python3
"""Récupérer une BOÎTE d'un tableau OME-Zarr distant, en gardant ses coordonnées absolues.

⭐ **On ne télécharge pas le volume.** Un zarr rend sa valeur de remplissage pour les chunks
absents : en copiant le `.zarray` tel quel et en ne peuplant que les chunks de la boîte, on
obtient un tableau **de la taille d'origine**, donc lisible par n'importe quel outil sans
la moindre translation de coordonnées, et qui ne pèse que la boîte.

⚠ Ce que ça change pour l'outil qui lit : hors de la boîte il voit du **vide**, pas une
erreur. C'est le comportement voulu — « pas de donnée ici » — mais il faut le savoir avant
de conclure qu'une région est effectivement vide dans le rouleau.

⚠ **Reprenable** : un chunk déjà présent et non vide est sauté. Un 404 est **normal** (hors
du volume) et compté à part, jamais traité comme une panne.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from telecharger import obtenir  # noqa: E402

HOTE = "vesuvius-challenge-open-data.s3.amazonaws.com"


def cle_chunk(meta: dict, cz: int, cy: int, cx: int) -> str:
    """⚠ Le séparateur est celui que le tableau DÉCLARE, pas `/` par défaut.

    Un même corpus mélange les deux, et le coder en dur ne produit pas une erreur : ça
    produit une requête vers une clé inexistante, donc un « chunk vide » silencieux.
    """
    sep = meta.get("dimension_separator", ".")
    return sep.join((str(cz), str(cy), str(cx)))


def recuperer(prefixe: str, dest: Path, niveau: int, boite: tuple, fils: int) -> int:
    base = "/" + prefixe.strip("/")
    brut = obtenir(HOTE, f"{base}/{niveau}/.zarray")
    if brut is None:
        print(f"pas de .zarray au niveau {niveau} sous {prefixe}", file=sys.stderr)
        return 1
    meta = json.loads(brut)
    dz, dy, dx = meta["chunks"]
    racine = dest / str(niveau)
    racine.mkdir(parents=True, exist_ok=True)
    (racine / ".zarray").write_bytes(brut)
    # ⚠ Le .zattrs du GROUPE porte l'echelle OME ; sans lui certains lecteurs refusent.
    zattrs = obtenir(HOTE, f"{base}/.zattrs")
    if zattrs is not None:
        (dest / ".zattrs").write_bytes(zattrs)
    zgroup = obtenir(HOTE, f"{base}/.zgroup")
    if zgroup is not None:
        (dest / ".zgroup").write_bytes(zgroup)

    x0, x1, y0, y1, z0, z1 = boite
    coords = [(cz, cy, cx)
              for cz in range(z0 // dz, z1 // dz + 1)
              for cy in range(y0 // dy, y1 // dy + 1)
              for cx in range(x0 // dx, x1 // dx + 1)]
    print(f"{len(coords)} chunks · chunks {dz}x{dy}x{dx} · forme {meta['shape']} · "
          f"separateur « {meta.get('dimension_separator', '.')} » · {fils} fils")

    sep = meta.get("dimension_separator", ".")
    debut = time.monotonic()
    faits = absents = deja = 0
    octets = 0

    def un(c):
        cz, cy, cx = c
        f = racine.joinpath(*(str(v) for v in c)) if sep == "/" \
            else racine / cle_chunk(meta, cz, cy, cx)
        if f.exists() and f.stat().st_size > 0:
            return "deja", 0
        corps = obtenir(HOTE, f"{base}/{niveau}/{cle_chunk(meta, cz, cy, cx)}")
        if corps is None:
            return "absent", 0
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(corps)
        return "fait", len(corps)

    with cf.ThreadPoolExecutor(max_workers=fils) as pool:
        for etat, n in pool.map(un, coords):
            octets += n
            faits += etat == "fait"
            absents += etat == "absent"
            deja += etat == "deja"
    duree = max(1e-9, time.monotonic() - debut)
    print(f"  {faits} recuperes, {deja} deja la, {absents} absents (hors volume) · "
          f"{octets / 1e9:.2f} Go · {len(coords) / duree:.0f} chunks/s")
    print(f"boite prete : {dest}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Recuperer une boite d'un OME-Zarr distant, coordonnees absolues.")
    p.add_argument("prefixe", help="prefixe S3 du .zarr")
    p.add_argument("dest", type=Path)
    p.add_argument("--niveau", type=int, default=0)
    p.add_argument("--boite", type=int, nargs=6, required=True,
                   metavar=("X0", "X1", "Y0", "Y1", "Z0", "Z1"),
                   help="bornes en voxels DU NIVEAU demande")
    p.add_argument("--fils", type=int, default=24)
    a = p.parse_args()
    return recuperer(a.prefixe, a.dest, a.niveau, tuple(a.boite), a.fils)


if __name__ == "__main__":
    sys.exit(main())
