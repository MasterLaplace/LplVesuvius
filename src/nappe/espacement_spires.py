#!/usr/bin/env python3
"""Où ce rouleau est-il difficile à tracer ? Mesuré sur les prédictions de surface.

⚠⚠ **Ce fichier vise les rouleaux du Grand Prize, qui n'ont AUCUNE trace.** Nos autres
instruments jugent une trace contre le volume ; sur un rouleau non tracé ils n'ont rien
à mesurer. Vérifié : `PHerc0358/segments/` est vide. Mais tout le reste y est publié —
le volume, le winding `lasagna`, et les **prédictions de surface** nnUNet.

**Ce qui se mesure sans trace : l'écart entre spires.** `docs/00` §1 nomme la difficulté
centrale en une phrase — *« Deux spires voisines sont à 300 µm ; une feuille fait 40 µm.
Là où le rouleau est comprimé, cet écart tombe à zéro. »* Un rouleau n'est donc pas
difficile *en général* : il l'est **par endroits**, et savoir lesquels est de
l'information actionnable.

**L'estimateur, et pourquoi il n'a pas besoin de l'ombilic.** Une ligne qui traverse les
spires obliquement voit un écart **plus grand** que le vrai ; seule la perpendiculaire
voit le vrai. On mesure donc l'écart le long de x **et** de y, et on garde le **plus
petit** des deux — c'est celui dont la direction est la plus proche de la normale aux
feuilles. Ça évite d'avoir à connaître l'axe d'enroulement, que `06` §2.3 n'a toujours
pas établi.

⚠ **Au niveau 2 de la pyramide**, pour la raison mesurée en `06` §3.5 : il conserve 89 %
des murs pour 1/64 de la donnée. Un chunk y pèse **1,2 Mo compressé** au lieu de 7 Mo,
et une carte de rouleau devient une affaire de minutes.

⚠ La prédiction est une **probabilité de surface**, pas la surface : un seuil est
inévitable. Il est **balayé** et le résultat rapporté pour plusieurs valeurs, parce
qu'un chiffre qui dépend d'un seuil choisi seul ne se défend pas (`07` §8).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def spacings_along(line: np.ndarray, threshold: float) -> np.ndarray:
    """Écarts entre surfaces successives le long d'une ligne, en voxels.

    ⚠ Une « surface » est un GROUPE de voxels au-dessus du seuil, pas un voxel : à
    37 µm par voxel une feuille en fait un ou deux, et compter chaque voxel donnerait
    des écarts de 1 partout, c'est-à-dire une mesure de la résolution et non du rouleau.
    """
    hot = line >= threshold
    if hot.sum() < 2:
        return np.empty(0)
    edges = np.flatnonzero(np.diff(hot.astype(np.int8)) == 1) + 1
    starts = np.r_[0, edges] if hot[0] else edges
    return np.diff(starts).astype(float) if starts.size >= 2 else np.empty(0)


def survey_chunk(block: np.ndarray, threshold: float, sample: int = 24) -> float:
    """Écart médian entre spires dans un chunk, direction la plus perpendiculaire.

    ⚠ On garde le **minimum** des deux directions : une ligne oblique surestime l'écart,
    jamais l'inverse. Sans ce choix la mesure dirait surtout dans quel secteur du rouleau
    le chunk se trouve.
    """
    mid = block.shape[0] // 2
    plane = block[mid].astype(np.float32) / 255.0
    rows = np.linspace(4, plane.shape[0] - 5, sample).astype(int)
    cols = np.linspace(4, plane.shape[1] - 5, sample).astype(int)
    along_x = np.concatenate([spacings_along(plane[r], threshold) for r in rows] or [np.empty(0)])
    along_y = np.concatenate([spacings_along(plane[:, c], threshold) for c in cols] or [np.empty(0)])
    got = [np.median(a) for a in (along_x, along_y) if a.size >= 8]
    return float(min(got)) if got else float("nan")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Carte de difficulté : ou les spires se touchent-elles ?",
        epilog="Sur un rouleau NON trace, c'est la seule chose qui se mesure.",
    )
    parser.add_argument("zarr", help="cle S3 du .zarr de predictions de surface")
    parser.add_argument("--level", type=int, default=2)
    parser.add_argument("--voxel-um", type=float, default=9.362,
                        help="voxel du NIVEAU 0 ; le niveau lu le multiplie par 2^level")
    parser.add_argument("--chunks", type=int, default=24, help="chunks sondes")
    parser.add_argument("--seuils", type=float, nargs="*", default=[0.5],
                        help="⚠ Sur les predictions PUBLIEES le seuil est deja applique "
                             "(`th0.2` figure dans le nom du .zarr) : la donnee ne "
                             "contient que 0 et 255, donc balayer le seuil rend N fois "
                             "la meme ligne. Verifie plutot que suppose")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    url = args.zarr if args.zarr.startswith("http") else f"{BUCKET}/{args.zarr}"
    try:
        meta = array_meta(url, args.level, args.timeout)
    except RuntimeError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2
    depth, hy, hx = meta["chunks"]
    zs, rows, cols = meta["shape"]
    grid = (-(-zs // depth), -(-rows // hy), -(-cols // hx))
    voxel = args.voxel_um * (2 ** args.level)
    print(f"{args.zarr.split('/')[0]} niveau {args.level} : grille {grid}, "
          f"voxel {voxel:.1f} µm")

    # ⚠⚠ Le balayage couvre TOUTE l'etendue en x/y, pas seulement le milieu. Une
    # premiere version sondait la moitie centrale, et sa propre limite nº 2 disait
    # pourquoi c'etait insuffisant : **c'est au coeur qu'un rouleau s'effondre**, et un
    # sondage qui l'evite rend un rouleau plus facile qu'il n'est.
    steps = max(2, int(round(args.chunks ** (1 / 3))) + 1)
    picks = sorted({(int(z), int(y), int(x))
                    for z in np.linspace(grid[0] * 0.25, grid[0] * 0.75, max(2, steps - 1))
                    for y in np.linspace(0, grid[1] - 1, steps + 2)
                    for x in np.linspace(0, grid[2] - 1, steps + 2)})

    blocks, absent = [], 0
    for cz, cy, cx in picks:
        raw = get(f"{url}/{chunk_key(meta, args.level, cy, cx, cz)}", args.timeout)
        if raw is None:
            absent += 1
            continue
        data = decode(raw, meta, depth * hy * hx)
        if data is None:
            absent += 1
            continue
        block = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(depth, hy, hx)
        if block.max() == 0:
            absent += 1
            continue
        blocks.append(((cz, cy, cx), block))
    print(f"  {len(blocks)} chunks avec de la matiere sur {len(picks)} sondes "
          f"({absent} vides ou absents)")
    if not blocks:
        print("erreur : aucun chunk exploitable", file=sys.stderr)
        return 3

    # ⚠ On DIT si la donnee est binaire, au lieu de laisser un balayage de seuil
    # produire des lignes identiques qui ressemblent a une robustesse.
    echantillon = np.unique(blocks[0][1])
    binaire = echantillon.size <= 2
    if binaire:
        print(f"  ⚠ prediction BINAIRE (valeurs {echantillon.tolist()}) : "
              f"le seuil est deja applique a la publication, le balayer ne dit rien")
    report = {"zarr": args.zarr, "level": args.level, "voxel_um": voxel,
              "binaire": bool(binaire), "seuils": {}, "par_rayon": []}

    # ⚠ Le « rayon » est la distance au centre de la GRILLE de chunks, en chunks. Le
    # volume est masque, donc le rouleau y est grossierement centre -- c'est une
    # approximation assumee, et elle suffit a distinguer « coeur » de « bord », qui est
    # la seule question posee ici. Elle ne remplace pas un ombilic (`06` §2.3).
    centre = (grid[1] / 2.0, grid[2] / 2.0)
    radial: dict[int, list[float]] = {}
    for (cz, cy, cx), block in blocks:
        r = int(round(np.hypot(cy + 0.5 - centre[0], cx + 0.5 - centre[1])))
        value = survey_chunk(block, args.seuils[0])
        if np.isfinite(value):
            radial.setdefault(r, []).append(value * voxel)
    if radial:
        print(f"\n  ecart selon la position, du coeur vers le bord :")
        print(f"  {'rayon':>8} {'chunks':>7} {'ecart median':>14}")
        for r in sorted(radial):
            vals = radial[r]
            print(f"  {r:>5} ch {len(vals):>7} {np.median(vals):>11.0f} µm")
            report["par_rayon"].append({"rayon_chunks": r, "chunks": len(vals),
                                        "median_um": float(np.median(vals))})
    print(f"\n  {'seuil':>6} {'ecart median':>14} {'p10':>9} {'minimum':>10} "
          f"{'sous 150 um':>12}")
    for threshold in args.seuils:
        values = np.array([survey_chunk(b, threshold) for _, b in blocks])
        values = values[np.isfinite(values)] * voxel
        if values.size < 3:
            print(f"  {threshold:>6.2f}   trop peu de chunks exploitables")
            continue
        tight = float((values < 150.0).mean())
        print(f"  {threshold:>6.2f} {np.median(values):>11.0f} µm "
              f"{np.percentile(values, 10):>7.0f} µm {values.min():>7.0f} µm "
              f"{tight * 100:>10.0f} %")
        report["seuils"][str(threshold)] = {
            "chunks": int(values.size), "median_um": float(np.median(values)),
            "p10_um": float(np.percentile(values, 10)), "min_um": float(values.min()),
            "part_sous_150um": tight,
        }
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
