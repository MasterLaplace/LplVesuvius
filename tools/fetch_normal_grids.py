#!/usr/bin/env python3
"""Récupérer une tranche des `normal-grids` publiées, pour `normal_grid_path`.

⚠⚠ **`vc_grow_seg_from_seed` lit bien un `normal_grid_path`** — dérivé, comme le reste,
en sondant le binaire : donner un chemin **valide** fait imprimer
`Loaded normal grid level 0 (coordinate_scale=1, output_spiral_step=20)`. ⚠ Donner un
chemin **inexistant** ne produit **rien du tout** : le chargeur l'ignore en silence, et
c'est ce qui m'a fait conclure à tort que la clé n'existait pas.

Le format attendu est celui que le concours publie tel quel — `metadata.json` plus trois
dossiers `xy/`, `xz/`, `yz/` d'un fichier `.grid` par tranche. Ce sont les sorties de
`vc_gen_normalgrids`.

⚠ **`spiral-step` doit valoir le `step_size` du traceur**, sinon l'outil se plaint d'un
« step_size parameter mismatch ». Les grilles publiées sont à **20,0**, comme le défaut du
traceur.

⭐ **On ne prend pas les 10,4 Go** d'un rouleau : chaque dossier est indexé par un axe —
`xy` par z, `xz` par y, `yz` par x — donc une boîte se traduit en trois intervalles de
tranches, et rien d'autre n'est lu. ⚠ Un fichier manquant n'est pas une erreur : la
contrainte est simplement absente là.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from telecharger import obtenir  # noqa: E402

HOTE = "vesuvius-challenge-open-data.s3.amazonaws.com"
# xy est indexe par z, xz par y, yz par x -- l'axe absent du nom.
AXE = {"xy": 2, "xz": 1, "yz": 0}


def main() -> int:
    p = argparse.ArgumentParser(
        description="Recuperer une tranche des normal-grids publiees.")
    p.add_argument("prefixe", help="prefixe S3 du dossier .normal-grids")
    p.add_argument("dest", type=Path)
    p.add_argument("--boite", type=int, nargs=6, required=True,
                   metavar=("X0", "X1", "Y0", "Y1", "Z0", "Z1"),
                   help="bornes en voxels du NIVEAU 0")
    p.add_argument("--fils", type=int, default=24)
    args = p.parse_args()

    base = "/" + args.prefixe.strip("/")
    meta = obtenir(HOTE, f"{base}/metadata.json")
    if meta is None:
        print(f"pas de metadata.json sous {args.prefixe}", file=sys.stderr)
        return 1
    args.dest.mkdir(parents=True, exist_ok=True)
    (args.dest / "metadata.json").write_bytes(meta)

    bornes = {"xy": (args.boite[4], args.boite[5]),
              "xz": (args.boite[2], args.boite[3]),
              "yz": (args.boite[0], args.boite[1])}
    total = 0
    for d, (a, b) in bornes.items():
        dossier = args.dest / d
        dossier.mkdir(exist_ok=True)
        indices = list(range(max(0, a), b + 1))
        debut = time.monotonic()
        faits = absents = deja = 0
        octets = 0

        def un(i: int):
            f = dossier / f"{i:06d}.grid"
            if f.exists() and f.stat().st_size > 0:
                return "deja", 0
            corps = obtenir(HOTE, f"{base}/{d}/{i:06d}.grid")
            if corps is None:
                return "absent", 0
            f.write_bytes(corps)
            return "fait", len(corps)

        with cf.ThreadPoolExecutor(max_workers=args.fils) as pool:
            for etat, n in pool.map(un, indices):
                octets += n
                faits += etat == "fait"
                absents += etat == "absent"
                deja += etat == "deja"
        duree = max(1e-9, time.monotonic() - debut)
        total += octets
        print(f"  {d}: {faits} recuperes, {deja} deja la, {absents} absents · "
              f"{octets / 1e9:.2f} Go · {len(indices) / duree:.0f} tranches/s")
    print(f"grilles pretes : {args.dest}  ({total / 1e9:.2f} Go)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
