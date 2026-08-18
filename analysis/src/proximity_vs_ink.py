#!/usr/bin/env python3
"""La geometrie predit-elle la LISIBILITE ? — tache D, `06` §3.8.

⚠⚠ **Ce fichier existe pour l'objectif, pas pour le texte.** Le but du depot est le
DEROULEMENT ; l'encre est la **regle graduee** qui dit si une surface deroulee tient
debout. Cette mesure est donc l'etalonnage de l'une par l'autre, et c'est la seule
question du carnet qui relie les deux moities du travail :

    une trace a forte proximite anormale donne-t-elle une encre moins lisible ?

Si oui, la metrique de `07` cesse d'etre un diagnostic geometrique et devient un
**predicteur de qualite de deroulement** — mesurable sans modele, sans etiquette, et
sur n'importe quelle trace.

**Ce que la mesure compare, par tuile** et non par trace : une trace entiere donne UN
point, donc 46 traces donneraient 46 points dont la plupart sans etiquetage. Decoupee
en tuiles, la meme trace donne des centaines de couples (proximite locale, lisibilite
locale) — et surtout la proximite VARIE le long d'une trace, ce qu'une moyenne par
trace ecrase.

⚠ **Le confond a ecarter en premier : la quantite d'encre.** Une tuile sans texte a une
lisibilite basse pour une raison qui n'a rien a voir avec la geometrie. La correlation
est donc calculee **a l'interieur des tuiles annotees uniquement**, et le controle est
la meme correlation sur les tuiles vides — qui doit, elle, ne rien donner.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

MISSING = -1.0


def load_planes(mesh_dir: Path):
    import tifffile

    planes = []
    for axis in "xyz":
        path = mesh_dir / f"{axis}.tif"
        if not path.is_file():
            raise FileNotFoundError(f"plan absent : {path}")
        planes.append(tifffile.imread(path))
    return planes


def tile_proximity(mesh_dir: Path, tile: int, sample: int, apart: int,
                   search_radius: float, seed: int, block: float = 500.0) -> dict:
    """Proximite anormale par tuile de la parametrisation, calculee par BLOCS 3D.

    Reprend la definition de `excision.proximity` -- distance au plus proche point
    NON ADJACENT dans la parametrisation, rapportee a l'espacement local -- mais
    l'agrege par tuile au lieu de la trace entiere : une trace ne donne qu'UN point,
    et surtout la proximite VARIE le long d'une trace, ce qu'une moyenne ecrase.

    ⚠ « Non adjacent » se juge en COLONNES de la parametrisation : deux points voisins
    sur la meme feuille sont proches par construction et ne disent rien. Le seuil
    `apart` distingue « la meme feuille un peu plus loin » de « la feuille d'a cote ».

    ⚠⚠ **LE DECOUPAGE EST SPATIAL EN 3D, ET C'EST LA SEULE FORME CORRECTE.** Un
    maillage converti depuis le `.ppm` d'un segment entier fait 21 M de cellules, soit
    55x le maillage median du corpus windcheck : un `cKDTree` global avec
    `query_ball_point` y consomme plusieurs gigaoctets et a fait tomber la machine
    trois fois. Deux remedes ont ete ecartes, chacun pour une raison mesuree :

    - **decimer la grille** : mesure, `below_030` tombe de 0,00030 a 0,00012 en
      decimant par 2, soit 60 % du signal perdu -- le signal est dans la queue extreme
      (`06` §3.7) et decimer retire justement la queue ;
    - **tuiler la PARAMETRISATION** : structurellement faux ici. La metrique cherche
      des points LOIN dans la parametrisation mais PROCHES en 3D -- precisement ceux
      qu'une tuile de parametrisation met de l'autre cote de la frontiere.

    Un bloc 3D, lui, contient tous les points physiquement voisins quelle que soit
    leur distance dans la parametrisation, ce qui est exactement ce qu'il faut. La
    **marge** vaut le rayon de recherche : sans elle, un point au bord d'un bloc
    perdrait ses voisins d'en face et sa distance serait surestimee -- une fusion
    manquee a chaque frontiere de bloc.
    """
    from scipy.spatial import cKDTree

    if search_radius > block:
        raise ValueError(
            f"rayon de recherche {search_radius} > cote de bloc {block} : la marge ne "
            "tiendrait plus dans les blocs adjacents et des voisins seraient manques")

    x, y, z = load_planes(mesh_dir)
    valid = (x != MISSING) & (y != MISSING) & (z != MISSING)
    rows, cols = np.nonzero(valid)
    points = np.column_stack([x[valid], y[valid], z[valid]]).astype(np.float32)
    del x, y, z, valid

    generator = np.random.default_rng(seed)
    take = generator.choice(points.shape[0], min(sample, points.shape[0]), replace=False)
    take.sort()
    wanted = np.zeros(points.shape[0], dtype=bool)
    wanted[take] = True

    # Indexation par bloc 3D. Les cles sont des entiers, donc le regroupement est un
    # tri et non une boucle Python sur 21 M de points.
    keys = np.floor(points / block).astype(np.int64)
    span = keys.max(axis=0) - keys.min(axis=0) + 1
    keys -= keys.min(axis=0)
    flat = (keys[:, 0] * span[1] + keys[:, 1]) * span[2] + keys[:, 2]
    order = np.argsort(flat, kind="stable")
    flat_sorted = flat[order]
    starts = np.flatnonzero(np.r_[True, flat_sorted[1:] != flat_sorted[:-1]])
    ends = np.r_[starts[1:], flat_sorted.size]

    distance = np.full(points.shape[0], np.nan, dtype=np.float32)
    blocks_done = 0
    for begin, stop in zip(starts, ends):
        member = order[begin:stop]
        queries = member[wanted[member]]
        if queries.size == 0:
            continue
        # ⚠ Le voisinage se prend dans les 27 blocs adjacents, PAS en rebalayant tout
        # le nuage. Une premiere version faisait `np.flatnonzero(np.all(points >= low
        # ...))` a chaque bloc : invisible sur 288 K points, mais O(n) par bloc, donc
        # 21 M x quelques milliers de blocs -- des heures pour un resultat identique.
        # La marge tient dans un bloc tant que `search_radius <= block`, ce que le
        # garde ci-dessous impose.
        home = keys[member[0]]
        near_parts = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for dk in (-1, 0, 1):
                    nb = home + (di, dj, dk)
                    if np.any(nb < 0) or np.any(nb >= span):
                        continue
                    code = (nb[0] * span[1] + nb[1]) * span[2] + nb[2]
                    lo = np.searchsorted(flat_sorted, code, side="left")
                    hi = np.searchsorted(flat_sorted, code, side="right")
                    if hi > lo:
                        near_parts.append(order[lo:hi])
        near = np.concatenate(near_parts) if near_parts else np.empty(0, dtype=np.int64)
        if near.size < 2:
            continue
        tree = cKDTree(points[near].astype(np.float64))
        neighbourhoods = tree.query_ball_point(points[queries].astype(np.float64),
                                               r=search_radius)
        for index, cell in enumerate(queries):
            candidates = near[np.asarray(neighbourhoods[index], dtype=np.int64)]
            far = candidates[np.abs(cols[candidates] - cols[cell]) >= apart]
            if far.size:
                distance[cell] = np.sqrt(
                    ((points[far].astype(np.float64) - points[cell]) ** 2).sum(axis=1)).min()
        del tree
        blocks_done += 1

    # ⚠ Reference locale par TUILE, locale dans les DEUX directions -- pas la fenetre
    # de +/-150 colonnes de `proximity.py`, dont `06` §3.2 a montre qu'elle couvre
    # 96,9 % d'un tour de spire et n'est donc pas locale en rayon.
    tiles: dict[tuple[int, int], list[float]] = {}
    for cell in take:
        if not np.isfinite(distance[cell]):
            continue
        key = (int(rows[cell] // tile), int(cols[cell] // tile))
        tiles.setdefault(key, []).append(float(distance[cell]))

    out = {}
    for key, values in tiles.items():
        if len(values) < 12:
            continue
        values = np.asarray(values)
        baseline = float(np.median(values))
        if baseline <= 0:
            continue
        ratio = values / baseline
        out[key] = {
            "cells": int(values.size),
            "spacing": baseline,
            # La grandeur de `07` : la fraction de la queue basse. Le signal est dans
            # la queue extreme, pas dans la moyenne (`06` §3.7).
            "below_030": float((ratio < 0.30).mean()),
            "below_050": float((ratio < 0.50).mean()),
            "ratio_p5": float(np.percentile(ratio, 5)),
        }
    out["_blocks"] = blocks_done
    out["_measured"] = int(np.isfinite(distance).sum())
    return out


def tile_legibility(prediction: np.ndarray, labels: np.ndarray, tile: int,
                    threshold: float) -> dict:
    """Lisibilite par tuile : fraction d'encre predite, et accord avec l'humain."""
    height, width = prediction.shape
    out = {}
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            block = prediction[top:top + tile, left:left + tile]
            covered = np.isfinite(block)
            if covered.sum() < tile * tile * 0.5:
                continue
            truth = labels[top:top + tile, left:left + tile]
            predicted = covered & (block >= threshold)
            hit = int((predicted & truth).sum())
            out[(top // tile, left // tile)] = {
                "ink_predicted": float(predicted.sum() / covered.sum()),
                "ink_labelled": float(truth.mean()),
                "agreement": float(hit / max(predicted.sum(), 1)),
            }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La proximite anormale predit-elle une encre moins lisible ?",
        epilog="⚠ Le but est le DEROULEMENT : l'encre est la regle graduee, pas l'ouvrage.",
    )
    parser.add_argument("mesh", type=Path, help="repertoire .tifxyz")
    parser.add_argument("prediction", type=Path, help="carte d'encre .npy")
    parser.add_argument("labels", type=Path, help="PNG d'etiquetage")
    parser.add_argument("--tile", type=int, default=512)
    parser.add_argument("--sample", type=int, default=60000)
    parser.add_argument("--apart", type=int, default=200)
    parser.add_argument("--search-radius", type=float, default=80.0)
    parser.add_argument("--block", type=float, default=500.0,
                        help="cote d'un bloc 3D, en voxels. ⚠ C'est ce qui BORNE la "
                             "memoire : un arbre global sur 21 M de points a fait "
                             "tomber la machine trois fois")
    parser.add_argument("--threshold", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--json")
    args = parser.parse_args()

    from PIL import Image
    from scipy.stats import spearmanr

    Image.MAX_IMAGE_PIXELS = None
    prediction = np.load(args.prediction)
    labels = np.array(Image.open(args.labels))[: prediction.shape[0], : prediction.shape[1]] > 0

    geometry = tile_proximity(args.mesh, args.tile, args.sample, args.apart,
                              args.search_radius, args.seed, args.block)
    blocks = geometry.pop("_blocks", 0)
    measured = geometry.pop("_measured", 0)
    print(f"geometrie : {blocks} blocs 3D, {measured} cellules mesurees")
    ink = tile_legibility(prediction, labels, args.tile, args.threshold)
    shared = sorted(set(geometry) & set(ink))
    print(f"tuiles de {args.tile} px : {len(geometry)} avec geometrie, "
          f"{len(ink)} avec encre, {len(shared)} communes")
    if len(shared) < 20:
        print("erreur : trop peu de tuiles communes pour conclure", file=sys.stderr)
        return 3

    prox = np.array([geometry[k]["below_030"] for k in shared])
    agree = np.array([ink[k]["agreement"] for k in shared])
    labelled = np.array([ink[k]["ink_labelled"] for k in shared])

    # ⚠ LE CONFOND : une tuile sans texte a un accord bas pour une raison qui n'a
    # rien de geometrique. On correle donc SEULEMENT sur les tuiles annotees, et on
    # rapporte les vides a cote comme controle -- elles ne doivent rien donner.
    annotated = labelled > 0.01
    print()
    print(f"{'domaine':<26}{'tuiles':>8}{'rho':>8}{'p':>10}")
    print("-" * 52)
    results = {}
    for name, mask in (("tuiles annotees", annotated),
                       ("CONTROLE tuiles vides", ~annotated)):
        if mask.sum() < 12:
            print(f"{name:<26}{int(mask.sum()):>8}     (trop peu)")
            continue
        r = spearmanr(prox[mask], agree[mask])
        results[name] = {"tiles": int(mask.sum()), "rho": float(r.statistic),
                         "p": float(r.pvalue)}
        print(f"{name:<26}{int(mask.sum()):>8}{r.statistic:>+8.3f}{r.pvalue:>10.2e}")

    print()
    print("Lecture : un rho NEGATIF sur les tuiles annotees veut dire que plus la")
    print("proximite anormale est forte, moins l'encre trouvee s'accorde avec")
    print("l'humain — donc la geometrie predit la qualite du deroulement.")
    print("⚠ Et le controle doit rester plat : s'il correle aussi, ce qu'on mesure")
    print("   n'est pas la geometrie mais la quantite d'encre.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "tile": args.tile, "shared_tiles": len(shared), "results": results,
            "points": [{"row": k[0], "col": k[1],
                        "below_030": geometry[k]["below_030"],
                        "agreement": ink[k]["agreement"],
                        "ink_labelled": ink[k]["ink_labelled"]} for k in shared],
        }, indent=2) + "\n")
        print(f"\necrit : {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
