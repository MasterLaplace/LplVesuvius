#!/usr/bin/env python3
"""Trouver un point de départ pour `vc_grow_seg_from_seed`, à distance.

Le traceur part d'**une** coordonnée posée sur une prédiction de surface. Dans VC3D on la
pose à la souris ; ici on la cherche dans le zarr publié, sans rien télécharger.

⚠⚠ **L'ordre des axes est le piège de ce fichier, et il échoue en silence.** Le zarr est
indexé `(z, y, x)` — son `.zattrs` le dit — alors que `vc_grow_seg_from_seed -s` attend
**`x y z`**. Inverser ne produit aucune erreur : ça pose la graine ailleurs dans le
rouleau, et le traceur part sur ce qu'il trouve là. La conversion est donc faite **une
fois**, ici, et la sortie est écrite dans l'ordre de l'outil.

⚠ Une graine n'est pas n'importe quel voxel au-dessus du seuil. Le traceur optimise une
surface : il lui faut un endroit où la prédiction est **forte ET étendue**. On classe donc
les candidats par la valeur de leur **voisinage**, pas par leur propre valeur — un pic
isolé est du bruit, et c'est précisément ce qu'un `argmax` choisirait.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def lire_chunk(url: str, level: int, meta: dict, cz: int, cy: int, cx: int,
               timeout: float):
    dz, dy, dx = meta["chunks"]
    raw = get(f"{url}/{chunk_key(meta, level, cy, cx, cz)}", timeout)
    if raw is None:
        return None
    data = decode(raw, meta, dz * dy * dx)
    if data is None:
        return None
    return np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(dz, dy, dx)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chercher une graine sur une prediction de surface publiee.",
        epilog="La sortie est dans l'ordre x y z, celui de vc_grow_seg_from_seed.")
    parser.add_argument("zarr", help="cle S3 de la prediction de surface")
    parser.add_argument("--level", type=int, default=2,
                        help="niveau de recherche. ⚠ Les coordonnees sont converties au "
                             "NIVEAU 0, seul repere que le traceur comprend")
    parser.add_argument("--z-fraction", type=float, default=0.5,
                        help="hauteur relative ou chercher (0 = bas, 1 = haut)")
    parser.add_argument("--chunks", type=int, default=24, help="chunks sondes")
    parser.add_argument("--candidats", type=int, default=8)
    parser.add_argument("--voisinage", type=int, default=5,
                        help="cote du cube dont on moyenne la valeur. ⚠ C'est lui qui "
                             "distingue une surface d'un pic de bruit")
    parser.add_argument("--fils", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    url = args.zarr if args.zarr.startswith("http") else f"{BUCKET}/{args.zarr}"
    meta = array_meta(url, args.level, args.timeout)
    dz, dy, dx = meta["chunks"]
    nz, ny, nx = meta["shape"]
    facteur = 2 ** args.level

    gz, gy, gx = -(-nz // dz), -(-ny // dy), -(-nx // dx)
    cz = min(gz - 1, max(0, int(round(args.z_fraction * (gz - 1)))))

    # Balayage REGULIER du plan de chunks a cette hauteur : deux executions doivent rendre
    # la meme graine, sinon on ne peut pas reprendre un trace la ou on l'a laisse.
    par_axe = max(1, int(np.sqrt(args.chunks)))
    points = sorted({(int(y), int(x))
                     for y in np.linspace(0, gy - 1, par_axe)
                     for x in np.linspace(0, gx - 1, par_axe)})

    print(f"niveau {args.level} · grille {gz}x{gy}x{gx} chunks de {dz}x{dy}x{dx} · "
          f"plan z={cz} · {len(points)} chunks sondes")

    with cf.ThreadPoolExecutor(max_workers=args.fils) as pool:
        blocs = list(pool.map(
            lambda p: lire_chunk(url, args.level, meta, cz, p[0], p[1], args.timeout),
            points))

    k = args.voisinage
    candidats = []
    vides = 0
    for (cy, cx), bloc in zip(points, blocs):
        if bloc is None or bloc.max() == 0:
            vides += 1
            continue
        # ⚠ Moyenne de voisinage par sommes cumulees : un pic isole tombe, une nappe
        # ressort. Le pas de k evite de rendre huit voisins du meme point.
        f = bloc.astype(np.float32)
        reduit = f[: dz - dz % k, : dy - dy % k, : dx - dx % k]
        reduit = reduit.reshape(dz // k, k, dy // k, k, dx // k, k).mean(axis=(1, 3, 5))
        iz, iy, ix = np.unravel_index(int(np.argmax(reduit)), reduit.shape)
        score = float(reduit[iz, iy, ix])
        if score <= 0:
            continue
        # centre du bloc de cote k, en voxels du niveau demande, puis au NIVEAU 0
        z = (cz * dz + iz * k + k // 2) * facteur
        y = (cy * dy + iy * k + k // 2) * facteur
        x = (cx * dx + ix * k + k // 2) * facteur
        candidats.append({"score": score, "x": int(x), "y": int(y), "z": int(z)})

    if not candidats:
        print(f"aucune surface trouvee ({vides} chunks vides sur {len(points)})",
              file=sys.stderr)
        return 1

    candidats.sort(key=lambda c: -c["score"])
    candidats = candidats[: args.candidats]
    print(f"{vides} chunks vides · {len(candidats)} candidats\n")
    print(f"{'score':>8}  {'-s x y z (niveau 0)':<30}")
    for c in candidats:
        print(f"{c['score']:>8.1f}  {c['x']} {c['y']} {c['z']}")
    print(f"\n⚠ ordre x y z, celui de vc_grow_seg_from_seed — le zarr, lui, est (z,y,x)")

    if args.out:
        args.out.write_text(json.dumps(
            {"zarr": args.zarr, "level": args.level, "shape_zyx": list(meta["shape"]),
             "candidats": candidats}, indent=2) + "\n")
        print(f"ecrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
