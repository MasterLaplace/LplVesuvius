#!/usr/bin/env python3
"""La résolution du champ de phase explique-t-elle l'échec de `docs/17` ?

`17` s'est conclu par un échec — l'effet fond quand n monte — et a laissé **une seule**
suspicion : au niveau 3 (19,2 µm), huit cellules d'un maillage à 2,4 µm partagent un
voxel de phase, donc *« la plupart des marches valent zéro par construction »*.

⚠⚠ **La suspicion n'est pas testable comme elle était formulée.** Le volume `cos` du
`lasagna` n'est publié qu'aux niveaux **3, 4 et 5** — vérifié sur le bucket, et le
`.zattrs` le confirme (`datasets: ["3", "4", "5"]`). Le niveau 3 n'était donc pas un
choix : c'est **la résolution la plus fine qui existe**. « Refaire au niveau 0 ou 1 »
n'a pas d'objet.

Mais sa **conséquence** se mesure sur ce qui est déjà calculé. Si la quantification
écrasait le signal, la distribution des marches serait dominée par le zéro. Ce fichier
regarde, au lieu de supposer.

⚠ C'est la règle nº 4 du dépôt : *mesurer d'abord, expliquer ensuite*. La lecture du
code a produit une hypothèse fausse chaque fois qu'elle a précédé l'instrument.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La quantification du champ de phase ecrase-t-elle les marches ?")
    parser.add_argument("dossier", type=Path, help="repertoire des JSON de saut_de_spire")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    lignes = [json.loads(f.read_text()) for f in sorted(args.dossier.glob("*.json"))]
    if not lignes:
        print(f"aucun resultat dans {args.dossier}", file=sys.stderr)
        return 1

    med = np.array([r["marche_mediane"] for r in lignes], dtype=float)
    p95 = np.array([r["marche_p95"] for r in lignes], dtype=float)
    mx = np.array([r["marche_max"] for r in lignes], dtype=float)
    marches = np.array([r["marches"] for r in lignes], dtype=float)

    print(f"{len(lignes)} traces, {int(marches.sum())} marches au total\n")
    print(f"{'grandeur':>22} {'min':>8} {'mediane':>9} {'max':>8}")
    for nom, v in (("marche mediane", med), ("marche p95", p95), ("marche max", mx)):
        print(f"{nom:>22} {v.min():>8.1f} {float(np.median(v)):>9.1f} {v.max():>8.1f}")

    # ⚠ LE TEST. Si huit cellules de maillage partageaient reellement un voxel et que
    # ca ecrasait le signal, la marche MEDIANE d'une trace serait nulle -- c'est la
    # definition de « la plupart des marches valent zero ». Une mediane a 10 sur une
    # echelle de 0 a 255 dit le contraire : le champ VARIE entre cellules adjacentes.
    nulles = int((med == 0).sum())
    print(f"\ntraces dont la marche mediane est NULLE : {nulles} / {len(lignes)}")
    verdict = ("la quantification n'ecrase PAS le signal"
               if nulles == 0 else
               f"{nulles} traces ecrasees : la suspicion tient en partie")
    print(f"⇒ {verdict}")

    # ⚠ Et la dynamique disponible : si les marches occupaient trois valeurs, on serait
    # dans un regime quantifie meme sans zeros. On compte les valeurs DISTINCTES.
    distinctes = len(set(med.tolist()))
    print(f"valeurs distinctes de marche mediane : {distinctes} sur {len(lignes)} traces")

    rapport = {
        "traces": len(lignes), "marches_totales": int(marches.sum()),
        "marche_mediane_min": float(med.min()),
        "marche_mediane_mediane": float(np.median(med)),
        "marche_mediane_max": float(med.max()),
        "traces_a_marche_nulle": nulles,
        "valeurs_distinctes": distinctes,
        "verdict": verdict,
    }
    if args.out:
        args.out.write_text(json.dumps(rapport, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
