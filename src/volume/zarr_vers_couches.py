#!/usr/bin/env python3
"""Ecrire une fenetre d'un volume de surface publie en couches TIFF numerotees.

⚠⚠ Pourquoi ce pont existe. Le detecteur d'encre lit un repertoire de `NN.tif` -- c'est ce
que `10` a fait sur Scroll 1, dont les segments publient un dossier `layers/`. Les rouleaux
du GRAND PRIZE, eux, ne publient QUE des `surface-volumes/*.zarr`. Sans ce pont, les huit
volumes de surface deja publies sur les trois rouleaux du prix qui ont des segments
(PHerc1447 4, PHerc0800 2, PHerc1203 2) sont hors de portee du modele -- alors qu'ils ne
demandent ni tracage ni rendu.

⭐ Et c'est la voie la plus courte vers First Letters : dix lettres dans une zone de 4 cm²
sur un rouleau du prix. Ces surfaces sont deja faites, par l'equipe du concours.

⚠ Un chunk d'un volume de surface contient TOUTE la profondeur (ici 31 × 128 × 128), donc
une fenetre de 1024² se lit en 64 requetes et non en 64 × 31. C'est la propriete que `12`
avait relevee, et elle rend l'operation bon marche.

⚠ La largeur du nom de fichier est un PARAMETRE, pas une constante : `10` a paye qu'un
rouleau ecrit `15.tif` et un autre `015.tif`, et qu'un mauvais choix rend un 404 qui
ressemble a « ce segment n'a pas de couches ».

⚠ Les couches sont ecrites TELLES QUELLES, sans normalisation : le modele a ete entraine
sur des `uint8` bruts, et remettre a l'echelle ici changerait silencieusement ce qu'il voit.

Usage :
    uv run python src/volume/zarr_vers_couches.py <cle S3 .zarr> --sortie data/couches/X \\
        --top 900 --left 900 --hauteur 1200 --largeur 1200
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def ecrire(zarr: str, sortie: Path, top: int, left: int, hauteur: int, largeur: int,
           level: int, largeur_nom: int, timeout: float) -> int:
    import tifffile

    url = f"{BUCKET}/{zarr.strip('/')}"
    meta = array_meta(url, level, timeout)
    nz, ny, nx = meta["shape"]
    dz, dy, dx = meta["chunks"]
    if dz != nz:
        print(f"⚠ ce volume n'a pas toute sa profondeur dans un chunk ({dz} sur {nz}) — "
              f"la lecture reste correcte mais coûte {nz // dz}× plus de requêtes",
              file=sys.stderr)

    hauteur = min(hauteur, ny - top)
    largeur = min(largeur, nx - left)
    if hauteur <= 0 or largeur <= 0:
        print(f"fenêtre hors du volume ({ny}×{nx})", file=sys.stderr)
        return 2

    pile = np.zeros((nz, hauteur, largeur), dtype=np.dtype(meta["dtype"]))
    vus = manquants = 0
    for cy in range(top // dy, (top + hauteur - 1) // dy + 1):
        for cx in range(left // dx, (left + largeur - 1) // dx + 1):
            raw = get(f"{url}/{chunk_key(meta, level, cy, cx, 0)}", timeout)
            if raw is None:
                manquants += 1
                continue
            data = decode(raw, meta, dz * dy * dx)
            if data is None:
                manquants += 1
                continue
            bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(dz, dy, dx)
            y0, x0 = cy * dy, cx * dx
            # Intersection du chunk et de la fenêtre, dans les deux repères.
            sy0, sy1 = max(top, y0), min(top + hauteur, y0 + dy)
            sx0, sx1 = max(left, x0), min(left + largeur, x0 + dx)
            if sy0 >= sy1 or sx0 >= sx1:
                continue
            pile[:, sy0 - top:sy1 - top, sx0 - left:sx1 - left] = \
                bloc[:, sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0]
            vus += 1

    sortie.mkdir(parents=True, exist_ok=True)
    for i in range(nz):
        tifffile.imwrite(sortie / f"{i:0{largeur_nom}d}.tif", pile[i])
    couvert = float((pile > 0).any(axis=0).mean())
    print(f"{nz} couches {hauteur}×{largeur} → {sortie}")
    print(f"  chunks lus {vus}, absents {manquants} · couverture {couvert:.1%}")
    if couvert < 0.05:
        print("  ⚠⚠ presque rien n'est couvert : la fenêtre tombe dans le vide du canevas.")
        print("     Un volume de surface est majoritairement du remplissage (piège nº 27) —")
        print("     il faut TROUVER la matière avant de la sonder.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zarr")
    ap.add_argument("--sortie", type=Path, required=True)
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--left", type=int, default=0)
    ap.add_argument("--hauteur", type=int, default=1024)
    ap.add_argument("--largeur", type=int, default=1024)
    ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--largeur-nom", type=int, default=2,
                    help="largeur du nom de fichier : 2 donne 05.tif, 3 donne 005.tif")
    ap.add_argument("--timeout", type=float, default=120.0)
    a = ap.parse_args()
    return ecrire(a.zarr, a.sortie, a.top, a.left, a.hauteur, a.largeur, a.level,
                  a.largeur_nom, a.timeout)


if __name__ == "__main__":
    sys.exit(main())
