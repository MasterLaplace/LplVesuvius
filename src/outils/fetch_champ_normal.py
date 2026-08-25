#!/usr/bin/env python3
"""Assembler un `direction_fields` local pour `vc_grow_seg_from_seed`.

⚠⚠ **Le contrat n'est documenté nulle part** ; il a été **dérivé** des exceptions du
binaire, clé par clé :

    "direction_fields": [{"zarr": "<base>", "dir": "normal", "scale": 2.0}]

et l'outil ouvre alors `<base>/x/2`, `<base>/y/2`, `<base>/z/2`. Directions valides :
`normal`, `horizontal`, `vertical`.

⚠⚠ **L'encodage des uint8 n'est pas documenté non plus, il est MESURÉ.**
`src/nappe/valider_champ_normal.py` compare le champ publié à la normale que notre
tenseur de structure calcule sur la prédiction, et balaye l'hypothèse de zéro : pic net à
**128** (6,6° d'écart) contre 37 à 53° partout ailleurs. Conséquence directe : la
composante **z**, que le rouleau ne publie pas, se remplit de **128** et non de 0 — zéro
voudrait dire −1, c'est-à-dire une normale verticale partout.

⭐ **On ne télécharge pas le rouleau.** Un zarr rend sa valeur de remplissage pour les
chunks absents, donc seule la boîte autour de la trace est récupérée ; ailleurs, le champ
dit « pas de contrainte ».

⚠⚠ **Une connexion réutilisée, pas un processus par requête.** La première version
appelait `curl` une fois par chunk : une poignée de main TLS par chunk, **mesuré à
7 chunks/s**. Ce qui coûte ici est la **latence**, pas le débit. Un pool de connexions
persistantes — une par fil, gardée ouverte sur des milliers de requêtes — est le même
remède que `libcurl` face au binaire `curl`, sans ajouter de dépendance. **Mesuré : 195 à
209 chunks/s**, soit ×28.

⚠ Ma première mesure du gain annonçait ×6,8 — prise **pendant que les `curl` de l'ancienne
version tournaient encore**. Un chiffre mesuré sous contention n'est pas le chiffre.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import time
from pathlib import Path

HOTE = "vesuvius-challenge-open-data.s3.amazonaws.com"

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from telecharger import obtenir as _obtenir  # noqa: E402


def obtenir(chemin: str) -> bytes | None:
    return _obtenir(HOTE, chemin)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Assembler un direction_fields local depuis les nx/ny publies.")
    p.add_argument("lasagna", help="prefixe S3 du dossier lasagna")
    p.add_argument("rouleau", help="prefixe des fichiers, ex. PHerc0358")
    p.add_argument("dest", type=Path)
    p.add_argument("--niveau", type=int, required=True)
    p.add_argument("--boite", type=int, nargs=6, required=True,
                   metavar=("X0", "X1", "Y0", "Y1", "Z0", "Z1"),
                   help="bornes en voxels DU NIVEAU demande")
    p.add_argument("--fils", type=int, default=16)
    args = p.parse_args()

    base = f"/{args.lasagna.strip('/')}"
    ref = obtenir(f"{base}/{args.rouleau}_nx.ome.zarr/{args.niveau}/.zarray")
    if ref is None:
        print(f"pas de .zarray au niveau {args.niveau}", file=sys.stderr)
        return 1
    meta = json.loads(ref)
    dz, dy, dx = meta["chunks"]
    sep = meta.get("dimension_separator", ".")

    for axe in ("x", "y"):
        d = args.dest / axe / str(args.niveau)
        d.mkdir(parents=True, exist_ok=True)
        (d / ".zarray").write_bytes(ref)
    # ⚠ La composante z est fabriquee VIDE : fill_value 128 vaut exactement zero une fois
    # decode, et ne coute pas un octet.
    dz_ = args.dest / "z" / str(args.niveau)
    dz_.mkdir(parents=True, exist_ok=True)
    mz = dict(meta, fill_value=128, compressor=None)
    (dz_ / ".zarray").write_text(json.dumps(mz))

    x0, x1, y0, y1, z0, z1 = args.boite
    coords = [(cz, cy, cx)
              for cz in range(z0 // dz, z1 // dz + 1)
              for cy in range(y0 // dy, y1 // dy + 1)
              for cx in range(x0 // dx, x1 // dx + 1)]
    print(f"{len(coords)} chunks par composante · chunks {dz}x{dy}x{dx} · "
          f"separateur « {sep} » · {args.fils} fils")

    total_octets = 0
    for comp, axe in (("nx", "x"), ("ny", "y")):
        racine = args.dest / axe / str(args.niveau)
        debut = time.monotonic()
        faits = absents = deja = 0
        octets = 0

        def un(c):
            cz, cy, cx = c
            f = racine.joinpath(*(str(v) for v in c)) if sep == "/" \
                else racine / sep.join(str(v) for v in c)
            if f.exists() and f.stat().st_size > 0:
                return "deja", 0
            corps = obtenir(f"{base}/{args.rouleau}_{comp}.ome.zarr/{args.niveau}/"
                            + sep.join(str(v) for v in c))
            if corps is None:
                return "absent", 0
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(corps)
            return "fait", len(corps)

        with cf.ThreadPoolExecutor(max_workers=args.fils) as pool:
            for etat, n in pool.map(un, coords):
                octets += n
                if etat == "fait":
                    faits += 1
                elif etat == "absent":
                    absents += 1
                else:
                    deja += 1
        duree = max(1e-9, time.monotonic() - debut)
        total_octets += octets
        print(f"  {comp}: {faits} recuperes, {deja} deja la, {absents} absents (hors "
              f"rouleau) · {octets / 1e6:.1f} Mo · {len(coords) / duree:.0f} chunks/s")

    print(f"champ pret : {args.dest}  ({total_octets / 1e6:.1f} Mo, z vide a 128)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
