#!/usr/bin/env python3
"""Ou est la surface tracee par rapport a la matiere, sur une pile COMPLETE.

⚠ La surface tracee est la couche **32** d'une pile de 65 (`vc_layers_from_ppm -r 32`,
verifie dans le tutoriel officiel). Une trace posee sur la feuille met donc la matiere
autour de 32 ; une trace qui a glisse la met ailleurs.

⚠⚠ **Ce fichier existe pour ne PAS emprunter un chiffre.** Une premiere lecture avait
conclu « l'ecart vaut une epaisseur de feuille » en important le pas inter-feuilles
mesure sur **PHerc0172** (142,8 µm) vers **PHerc1667**, qui est un autre rouleau avec sa
propre compaction. C'est le piege nº 6 du depot -- un chiffre emprunte n'est pas une
mesure -- et la pile complete l'a demenu : les deux blocs de matiere y sont separes de
plus de 64 voxels, soit plusieurs fois ce pas.

Ce qui se mesure ici sans rien emprunter : **la distance de la couche 32 au sommet de
matiere le plus proche**, dans la pile de ce segment. Un bord atteint sans sommet est
rapporte comme une **borne inferieure**, jamais comme une distance.

⚠ Tout est normalise min-max DANS SA PROPRE pile, comme l'affichage de
`depth_profile.py` : comparer des niveaux bruts comparerait les scanners, et melanger
les deux normalisations donne deux chiffres pour la meme couche (0,896 contre 0,233 --
paye une fois).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

TRACED_LAYER = 32
"""La surface tracee, quand la pile fait 65 couches engendrees avec `-r 32`."""


def normalise(values) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    span = array.max() - array.min()
    return (array - array.min()) / span if span > 0 else np.zeros_like(array)


def describe(layers: list[int], contrast, mean) -> dict:
    """Sommets de matiere, vides, et distance de la couche tracee au sommet le plus proche."""
    c = normalise(contrast)
    m = normalise(mean)
    index = {layer: i for i, layer in enumerate(layers)}
    if TRACED_LAYER not in index:
        raise ValueError(f"la couche {TRACED_LAYER} n'est pas dans la pile fournie")
    here = index[TRACED_LAYER]

    # Sommets internes : strictement plus hauts que leurs deux voisins. Un maximum
    # atteint AU BORD n'est pas un sommet -- c'est le flanc d'un sommet situe dehors,
    # et le confondre transformerait une borne en mesure.
    peaks = [i for i in range(1, len(c) - 1) if c[i] > c[i - 1] and c[i] > c[i + 1]
             and c[i] > 0.5]
    troughs = [i for i in range(1, len(c) - 1) if m[i] < m[i - 1] and m[i] < m[i + 1]
               and m[i] < 0.15]
    rising_at_end = c[-1] > c[-2]
    rising_at_start = c[0] > c[1]

    if peaks:
        nearest = min(peaks, key=lambda i: abs(i - here))
        distance = abs(layers[nearest] - TRACED_LAYER)
        bound = False
    else:
        # Aucun sommet interne : le plus proche est hors pile, donc on ne connait
        # qu'une BORNE INFERIEURE -- la distance au bord le plus proche.
        distance = min(TRACED_LAYER - layers[0], layers[-1] - TRACED_LAYER)
        nearest = None
        bound = True
    return {
        "layers": [layers[0], layers[-1]],
        "sommets": [layers[i] for i in peaks],
        "vides": [layers[i] for i in troughs],
        "contraste_couche_tracee": float(c[here]),
        "intensite_couche_tracee": float(m[here]),
        "distance_au_sommet": int(distance),
        "distance_est_une_borne": bool(bound),
        "monte_encore_au_bord_bas": bool(rising_at_start),
        "monte_encore_au_bord_haut": bool(rising_at_end),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La couche tracee (32) est-elle sur la matiere ?",
        epilog="Un maximum au bord est une BORNE, pas une distance.",
    )
    parser.add_argument("profiles", type=Path, nargs="+",
                        help="JSON produits par depth_profile.py (mode fenetre unique)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    report = []
    for path in args.profiles:
        for entry in json.loads(path.read_text()):
            try:
                summary = describe(entry["layers"], entry["contrast"], entry["mean"])
            except ValueError as error:
                print(f"{entry['folder']} : {error}", file=sys.stderr)
                continue
            print(f"\n=== {entry['folder']} — couches {summary['layers'][0]} a "
                  f"{summary['layers'][1]} ===")
            print(f"  sommets de matiere  : {summary['sommets'] or 'aucun DANS la pile'}")
            print(f"  vides               : {summary['vides'] or 'aucun'}")
            print(f"  a la couche tracee 32 : contraste {summary['contraste_couche_tracee']:.3f}"
                  f"   intensite {summary['intensite_couche_tracee']:.3f}")
            mot = "AU MOINS " if summary["distance_est_une_borne"] else ""
            print(f"  distance au sommet le plus proche : {mot}{summary['distance_au_sommet']} voxels"
                  f"  ({summary['distance_au_sommet'] * 7.91:.0f} µm)")
            if summary["monte_encore_au_bord_bas"] or summary["monte_encore_au_bord_haut"]:
                bords = []
                if summary["monte_encore_au_bord_bas"]:
                    bords.append("bas")
                if summary["monte_encore_au_bord_haut"]:
                    bords.append("haut")
                print(f"  ⚠ le contraste monte encore au bord {' et '.join(bords)} : "
                      f"le coeur de cette matiere est HORS de la pile")
            report.append({"folder": entry["folder"], **summary})

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
