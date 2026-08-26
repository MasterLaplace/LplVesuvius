#!/usr/bin/env python3
"""Mesure la proximite anormale entre regions NON ADJACENTES d'une trace aplatie.

Une trace `tifxyz` est deja la parametrisation 2D : chaque cellule de grille porte
sa position 3D. Deux cellules eloignees dans l'image mais voisines dans l'espace
decrivent donc deux parties du rouleau qui se frolent -- ce qui est le symptome
geometrique du saut de spire.

LA REGLE QUI FAIT LA METRIQUE : une proximite ne veut rien dire dans l'absolu.
Mesure sur une trace reelle, l'ecart typique entre parties non adjacentes vaut
177 um en mediane mais s'etale de 61 um (p1) a 303 um (p90), parce que le tassement
varie le long d'un rouleau. 100 um est donc banal la ou les couches sont a 120 um,
et alarmant la ou elles sont a 400 um. On normalise par l'espacement LOCAL, jamais
par une constante -- une constante avait deja produit une conclusion fausse.

Ne demande ni volume, ni modele, ni etiquette : la trace seule suffit.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tifffile

MISSING = -1.0


class ProximityError(RuntimeError):
    """Leve quand la trace ne permet pas la mesure."""


def load_trace(mesh_dir: Path, decimate: int = 1):
    """Charge une trace et rend (positions 3D, lignes, colonnes) des cellules valides.

    ⚠ `decimate` garde une cellule sur N dans CHAQUE direction de la grille. Il existe
    parce qu'un maillage converti depuis le `.ppm` d'un segment entier fait 21 M de
    cellules -- 55x le maillage median du corpus windcheck et 7x le plus gros -- et
    que le cKDTree y consomme plusieurs gigaoctets. La decimation porte sur la GRILLE
    et non sur les points : un tirage aleatoire detruirait la structure de la
    parametrisation, et le seuil `apart`, qui compte des colonnes, ne voudrait plus
    rien dire. ⚠ Le biais introduit se MESURE (voir docs/06 §3.8).
    """
    planes = []
    for axis in ("x", "y", "z"):
        path = mesh_dir / f"{axis}.tif"
        if not path.is_file():
            raise ProximityError(f"plan absent : {path}")
        planes.append(tifffile.imread(path))
    x, y, z = planes
    if decimate > 1:
        x = x[::decimate, ::decimate]
        y = y[::decimate, ::decimate]
        z = z[::decimate, ::decimate]
    valid = (x != MISSING) & (y != MISSING) & (z != MISSING)
    if not valid.any():
        raise ProximityError(f"aucune cellule valide dans {mesh_dir}")
    rows, cols = np.nonzero(valid)
    return np.column_stack([x[valid], y[valid], z[valid]]), rows, cols


def nearest_non_adjacent(
    points: np.ndarray,
    cols: np.ndarray,
    sample: np.ndarray,
    apart: int,
    search_radius: float,
):
    """Distance de chaque cellule echantillonnee a la partie NON ADJACENTE la plus proche.

    « Non adjacente » se juge dans la PARAMETRISATION, pas dans l'espace : deux
    cellules voisines dans l'image sont censees etre voisines en 3D, et les compter
    noierait le signal sous la continuite ordinaire de la surface.

    Rend NaN quand rien de non adjacent n'est dans le rayon de recherche -- une
    absence de mesure, a ne pas confondre avec une grande distance.
    """
    from scipy.spatial import cKDTree

    tree = cKDTree(points)
    neighbourhoods = tree.query_ball_point(points[sample], r=search_radius)
    distances = np.full(sample.size, np.nan)
    for index, (cell, neighbours) in enumerate(zip(sample, neighbourhoods)):
        candidates = np.asarray(neighbours, dtype=np.int64)
        if candidates.size == 0:
            continue
        far = candidates[np.abs(cols[candidates] - cols[cell]) >= apart]
        if far.size == 0:
            continue
        distances[index] = np.sqrt(((points[far] - points[cell]) ** 2).sum(axis=1)).min()
    return distances


def local_baseline(cols: np.ndarray, sample: np.ndarray, distances: np.ndarray, window: int):
    """Espacement typique AUTOUR de chaque cellule, en colonnes de la parametrisation.

    La mediane, et non la moyenne : la grandeur qu'on cherche est justement une
    queue basse, et une moyenne se laisse tirer par ce qu'on veut detecter.
    """
    order = np.argsort(cols[sample])
    sorted_cols = cols[sample][order]
    sorted_distance = distances[order]
    baseline = np.full(sample.size, np.nan)
    for position in range(sorted_cols.size):
        lo = np.searchsorted(sorted_cols, sorted_cols[position] - window, side="left")
        hi = np.searchsorted(sorted_cols, sorted_cols[position] + window, side="right")
        window_values = sorted_distance[lo:hi]
        window_values = window_values[~np.isnan(window_values)]
        if window_values.size >= 8:
            baseline[position] = np.median(window_values)
    restored = np.full(sample.size, np.nan)
    restored[order] = baseline
    return restored


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Proximite anormale entre regions non adjacentes d'une trace.",
        epilog="Ne demande ni volume ni modele. Voir docs/05_le_predicat_est_trop_etroit.md.",
    )
    parser.add_argument("mesh", type=Path, help="repertoire .tifxyz")
    parser.add_argument("--sample", type=int, default=20000, help="cellules tirees (defaut: 20000)")
    parser.add_argument(
        "--decimate", type=int, default=1,
        help="ne garder qu'une cellule sur N dans CHAQUE direction de la grille "
             "(defaut: 1 = tout). ⚠ Un maillage converti depuis un .ppm de segment "
             "entier fait 21 M de cellules, soit 55x le maillage median du corpus "
             "windcheck et 7x le plus gros : le cKDTree et query_ball_point y "
             "consomment plusieurs Go et ont fait tomber la machine deux fois. "
             "Decimer ramene le cout dans la plage ou l'outil a ete valide -- au prix "
             "d'un biais qu'il faut MESURER et non supposer",
    )
    parser.add_argument(
        "--apart", type=int, default=200,
        help="ecart minimal en colonnes pour dire « non adjacent » (defaut: 200)",
    )
    parser.add_argument(
        "--sheet-pitch-um", type=float, default=142.8,
        help="pas inter-feuilles en micrometres (defaut: 142,8, MESURE sur PHerc0172, "
             "cv 1,8 %%). Le rayon de recherche en est derive : c'est la seule facon "
             "que le parametre veuille dire la meme chose d'une campagne de scan a "
             "l'autre",
    )
    parser.add_argument(
        "--search-radius", type=float, default=0.0,
        help="rayon de recherche 3D en VOXELS. 0 = derive de --sheet-pitch-um et "
             "--voxel-um. ⚠ Ne le poser a la main que pour un balayage : la valeur "
             "physique est justifiee, une valeur en voxels ne l'est pas",
    )
    parser.add_argument(
        "--window", type=int, default=150,
        help="demi-largeur en colonnes de la fenetre de reference locale (defaut: 150)",
    )
    parser.add_argument("--voxel-um", type=float, default=7.91, help="taille du voxel en um")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label", default="", help="etiquette portee par la sortie")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        points, _, cols = load_trace(args.mesh, args.decimate)
    except ProximityError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    # ⚠⚠ LE RAYON VIENT DE LA PHYSIQUE, PAS D'UN BALAYAGE. La valeur en vigueur
    # jusqu'au 2026-08-18 etait 80 voxels, soit 633 µm a 7,91 µm et 749 µm a 9,362 µm --
    # c'est-a-dire PLUSIEURS ecarts inter-feuilles. Un tel rayon trouve la spire
    # voisine, qui est de la geometrie parfaitement normale, et noie l'anomalie dedans.
    # Mesure (`07` §9) : a 749 µm, rho +0,284 sur PHerc0139 ; a 142,8 µm, rho +0,666.
    # Et sur Scroll 1, le rayon issu du pas physique (+0,840) bat le meilleur rayon
    # trouve par balayage (+0,829) -- donc ce n'est pas un reglage.
    if args.search_radius <= 0.0:
        args.search_radius = args.sheet_pitch_um / args.voxel_um
        print(f"rayon derive : {args.sheet_pitch_um:.1f} µm / {args.voxel_um:.3f} µm "
              f"= {args.search_radius:.1f} voxels", file=sys.stderr)

    generator = np.random.default_rng(args.seed)
    take = min(args.sample, points.shape[0])
    sample = generator.choice(points.shape[0], take, replace=False)

    distances = nearest_non_adjacent(points, cols, sample, args.apart, args.search_radius)
    measured = ~np.isnan(distances)
    if measured.sum() < 100:
        # ⚠⚠ CE N'EST PAS UNE PANNE, C'EST LE DOMAINE DE DEFINITION. La metrique cherche
        # deux parties eloignees dans la parametrisation et proches en 3D ; une trace qui
        # ne fait pas UN TOUR ne repasse jamais au-dessus d'elle-meme, donc il n'existe
        # aucune paire de ce genre. Mesure (`07` §7) : sur les 53 traces de Scroll 5, les
        # 44 qui rendent zero cellule couvrent 0,50 a 1,00 tour, et les 9 qui mesurent en
        # couvrent 2,99 a 9,07. La coupure est nette.
        #
        # Le dire ici plutot que de rendre « 0 cellule mesuree » : ce message-la ressemble
        # a un outil casse, et c'est ce qui a failli faire conclure que la metrique
        # « marchait moins bien » sur un second rouleau alors qu'elle ne s'y applique pas.
        print(
            f"erreur : {int(measured.sum())} cellules mesurees sur {take} tirees.\n"
            "  La trace ne se recouvre pas : aucune partie non adjacente n'est a moins\n"
            f"  de {args.search_radius:.0f} voxels d'une autre. C'est le cas d'une trace\n"
            "  qui couvre moins d'un tour -- HORS DU DOMAINE de cette metrique, pas une\n"
            "  panne. Verifier `covering_span_rev` dans l'index publie.",
            file=sys.stderr,
        )
        return 3

    baseline = local_baseline(cols, sample, distances, args.window)
    usable = measured & ~np.isnan(baseline) & (baseline > 0)
    ratio = distances[usable] / baseline[usable]

    report = {
        "label": args.label or args.mesh.parent.parent.name,
        "cells": int(points.shape[0]),
        "sampled": int(take),
        "measured": int(measured.sum()),
        "usable": int(usable.sum()),
        "spacing_um_median": float(np.median(distances[measured]) * args.voxel_um),
        "spacing_um_p5": float(np.percentile(distances[measured], 5) * args.voxel_um),
        # La grandeur qui compte : la queue basse du rapport au voisinage local.
        "ratio_p1": float(np.percentile(ratio, 1)),
        "ratio_p5": float(np.percentile(ratio, 5)),
        "ratio_median": float(np.median(ratio)),
        "fraction_below_half": float((ratio < 0.5).mean()),
        "fraction_below_third": float((ratio < 1 / 3).mean()),
        # SANS SEUIL. Le rapport vaut 1 quand une cellule est a l'espacement typique
        # de son voisinage, donc « anormalement proche » se lit directement comme un
        # deficit sous 1. La moyenne de ce deficit utilise TOUTE la queue basse et
        # pondere chaque cellule par son ecart -- il n'y a aucune coupure a choisir,
        # donc aucune prise pour ajuster le resultat apres l'avoir vu.
        "shortfall": float(np.maximum(0.0, 1.0 - ratio).mean()),
        # Meme grandeur, restreinte au dixieme le plus proche : dit si le deficit
        # vient d'un affaissement general ou d'une minorite de sites tres proches.
        # Deux traces peuvent partager un shortfall et differer ici.
        "shortfall_worst_decile": float(
            np.maximum(0.0, 1.0 - np.sort(ratio)[: max(1, ratio.size // 10)]).mean()
        ),
        # Balayage du seuil. Un seuil unique se defend mal ; ce qui se defend, c'est
        # un PLATEAU -- si la correlation tient sur toute une plage, le choix n'est
        # pas critique, et s'il pique sur une valeur, c'est du sur-ajustement.
        **{
            f"below_{int(round(t * 100)):03d}": float((ratio < t).mean())
            for t in (0.15, 0.20, 0.25, 0.30, 1 / 3, 0.40, 0.50, 0.60, 0.70)
        },
    }

    if args.as_json:
        json.dump(report, sys.stdout)
        sys.stdout.write("\n")
        return 0

    for key, value in report.items():
        print(f"{key:24} {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
