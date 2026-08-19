#!/usr/bin/env python3
"""Combien coûte notre mesure sur 53 rouleaux, et sur les 800 de la villa ?

⚠⚠ **Contrainte posée par l'auteur, et elle est architecturale, pas cosmétique.** Un
instrument qui demande de télécharger un rouleau ne passe pas à l'échelle : la
collection publiée en compte 45, la villa en recèlerait ~800, et un volume pèse 2 Tio.

Ce fichier chiffre le coût **réel** de ce qui a été mesuré ici, à partir des tailles
observées, et l'extrapole. Il ne fait aucune hypothèse sur du matériel : il compte des
octets et des secondes déjà payés.

⚠ Le chiffre qui compte n'est pas la vitesse mais le **rapport** : ce que l'instrument
lit divisé par ce que le rouleau pèse. C'est lui qui dit si l'approche tient à 800.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Mesures relevees pendant les campagnes du 2026-08-18.
OBSERVE = {
    "chunk de volume de surface": {"octets": 1_785_856, "secondes": 1.03},
    "chunk de prediction (compresse)": {"octets": 1_200_000, "secondes": 0.35},
    "chunk de volume CT (niveau 1)": {"octets": 2_097_152, "secondes": 0.40},
}

CAMPAGNES = {
    "profondeur (qualite de trace)": {"chunks_par_segment": 25, "segments_typiques": 20},
    "separabilite (qualite de scan)": {"chunks_par_rouleau": 27},
    "ecart entre spires (geometrie)": {"chunks_par_rouleau": 27},
}

VOLUME_ROULEAU_TIO = 2.1
"""Taille d'un volume complet au niveau 0, mesuree en `02` : ~2,1 Tio."""


ACCELERATION_16_FILS = 8.35
"""Accélération réellement obtenue à 16 requêtes simultanées, mesurée le 2026-08-19.

⚠⚠ **Mesurée, pas déduite du nombre de fils.** 16 fenêtres d'un vrai segment :
**21,80 s** en série, **2,61 s** à 16 fils, et la sortie est **bit pour bit identique**
(`tools/temoins.sh`, batterie « champ de correction »). Le reste est la latence que le
serveur, la connexion et le décodage imposent — c'est-à-dire tout ce qu'un parallélisme
n'enlève pas.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cout de nos instruments a 1, 53 et 800 rouleaux.",
        epilog="Le rapport lu/total est ce qui dit si l'approche tient a l'echelle.",
    )
    parser.add_argument("--rouleaux", type=int, nargs="*", default=[1, 13, 53, 800])
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    # Un passage complet par rouleau : separabilite + ecart entre spires, plus la
    # profondeur sur les segments s'il y en a. Sur un rouleau NON trace il n'y a pas de
    # segment, donc les deux premieres seules -- et c'est le cas des 800.
    par_rouleau_non_trace = 27 * 2
    par_rouleau_trace = par_rouleau_non_trace + 25 * 20
    octets = 1_800_000
    secondes = 0.6

    print("Coût d'un passage complet, par rouleau")
    print(f"  rouleau NON trace (les 13 du prix, les ~800 de la villa) : "
          f"{par_rouleau_non_trace} chunks = "
          f"{par_rouleau_non_trace * octets / 1e6:.0f} Mo, "
          f"{par_rouleau_non_trace * secondes / 60:.1f} min")
    print(f"  rouleau trace (20 segments) : {par_rouleau_trace} chunks = "
          f"{par_rouleau_trace * octets / 1e9:.1f} Go, "
          f"{par_rouleau_trace * secondes / 60:.0f} min")
    print()
    print(f"{'rouleaux':>9} {'donnee lue':>13} {'temps 1 fil':>13} "
          f"{'temps 16 fils':>14} {'du volume total':>16}")
    report = []
    for n in args.rouleaux:
        lus = n * par_rouleau_non_trace * octets
        total = n * VOLUME_ROULEAU_TIO * 1024 ** 4
        heures = n * par_rouleau_non_trace * secondes / 3600
        print(f"{n:>9} {lus / 1e9:>10.1f} Go {heures:>10.1f} h "
              f"{heures / ACCELERATION_16_FILS:>11.1f} h "
              f"{lus / total * 100:>14.5f} %")
        report.append({"rouleaux": n, "octets_lus": lus, "heures_1_fil": heures,
                       "part_du_volume_pct": lus / total * 100})

    print()
    print("⚠ Ce qui rend ça possible tient en une phrase : un chunk OME-Zarr contient")
    print("  TOUTE la colonne de profondeur d'une fenetre, et les chunks se lisent")
    print("  independamment par HTTP. On ne telecharge jamais un rouleau.")
    print()
    print(f"⚠ L'acceleration a 16 fils est MESUREE ({ACCELERATION_16_FILS}), pas supposee.")
    print("  La version initiale de ce modele divisait par 16 -- un parallelisme parfait,")
    print("  donc un chiffre optimiste d'un facteur 1,9. Un modele de cout qui se flatte")
    print("  n'est pas un modele de cout.")
    print()
    print("⚠ Ce qui NE passe PAS a l'echelle, et qu'il faut dire : la detection d'encre")
    print("  (42 min par segment sur cet iGPU) et le TRACAGE lui-meme, qui reste")
    print("  semi-manuel. Nos instruments jugent vite ce que la production fait lentement.")

    if args.out:
        args.out.write_text(json.dumps(
            {"observe": OBSERVE, "par_rouleau_non_trace": par_rouleau_non_trace,
             "extrapolation": report}, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
