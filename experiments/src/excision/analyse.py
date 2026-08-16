#!/usr/bin/env python3
"""Compare la distribution d'intensite CT des cellules excisees et des temoins.

Repond a l'hypothese nulle posee dans docs/04_experience_excision.md :

    H0 : les cellules excisees ont la meme distribution d'intensite que les
         cellules retenues appariees.

Ce module REFUSE de conclure sur un echantillon vide ou desequilibre au point de
ne rien pouvoir discriminer, et rapporte une TAILLE D'EFFET a cote de la valeur p.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


class AnalysisError(RuntimeError):
    """Leve quand l'echantillon ne permet pas de conclure."""


UNSAMPLED = -1
"""Valeur rendue par l'echantillonneur quand un point tombe hors du volume."""


def load(path: Path) -> dict[str, dict[str, list[int]]]:
    """Charge les mesures, groupees par segment puis par population."""
    grouped: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            value = int(row["intensity"])
            if value == UNSAMPLED:
                continue
            grouped[row["segment"]][row["population"]].append(value)
    return grouped


def cliffs_delta(first: np.ndarray, second: np.ndarray) -> float:
    """Taille d'effet non parametrique, dans [-1, 1].

    Probabilite qu'un tirage de `first` depasse un tirage de `second`, moins la
    probabilite inverse. On la rapporte parce qu'une valeur p ne dit QUE si un
    ecart est distinguable du hasard : avec assez de points, un ecart sans
    importance devient « significatif ». La taille d'effet dit s'il compte.

    Calculee par rangs, en O(n log n), et non par la double boucle en O(n*m) :
    la definition naive sur 10^4 points de chaque cote ferait 10^8 comparaisons.
    """
    if first.size == 0 or second.size == 0:
        raise AnalysisError("taille d'effet indefinie sur une population vide")
    from scipy.stats import rankdata

    pooled = np.concatenate([first, second])
    ranks = rankdata(pooled)
    rank_sum_first = ranks[: first.size].sum()
    # U de Mann-Whitney, puis normalisation en delta de Cliff.
    u_first = rank_sum_first - first.size * (first.size + 1) / 2.0
    return float(2.0 * u_first / (first.size * second.size) - 1.0)


def describe(values: np.ndarray) -> dict:
    """Statistiques de position et de dispersion d'une population."""
    return {
        "n": int(values.size),
        "moyenne": float(values.mean()),
        "mediane": float(np.median(values)),
        "q1": float(np.percentile(values, 25)),
        "q3": float(np.percentile(values, 75)),
        "ecart_type": float(values.std(ddof=1)) if values.size > 1 else float("nan"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare cellules excisees et temoins appariees (hypothese nulle H0).",
        epilog="Voir docs/04_experience_excision.md pour la conception et les controles.",
    )
    parser.add_argument("samples", type=Path, help="TSV produit par excision.measure")
    parser.add_argument(
        "--min-excised", type=int, default=30,
        help="refuse de conclure sous ce nombre de cellules excisees (defaut: 30)",
    )
    args = parser.parse_args()

    grouped = load(args.samples)
    if not grouped:
        print("erreur : aucune mesure lue", file=sys.stderr)
        return 2

    excised = np.array(
        [v for seg in grouped.values() for v in seg.get("excised", [])], dtype=np.int64
    )
    control = np.array(
        [v for seg in grouped.values() for v in seg.get("control", [])], dtype=np.int64
    )

    segments_with_excised = sum(1 for seg in grouped.values() if seg.get("excised"))

    print(f"segments mesures            : {len(grouped)}")
    print(f"segments avec cellules excisees : {segments_with_excised}")
    print()

    # Le denominateur silencieux : une comparaison sur zero cellule serait verte
    # et ne dirait rien. On refuse, on ne rapporte pas « pas de difference ».
    if excised.size == 0 or control.size == 0:
        print("erreur : une des deux populations est VIDE, rien a comparer", file=sys.stderr)
        return 2

    print(f"{'':12} {'n':>7} {'moyenne':>9} {'mediane':>8} {'Q1':>6} {'Q3':>6} {'ecart-type':>11}")
    for label, values in (("excisees", excised), ("temoins", control)):
        s = describe(values)
        print(
            f"{label:12} {s['n']:>7} {s['moyenne']:>9.1f} {s['mediane']:>8.1f} "
            f"{s['q1']:>6.0f} {s['q3']:>6.0f} {s['ecart_type']:>11.1f}"
        )
    print()

    if excised.size < args.min_excised:
        print(
            f"REFUS DE CONCLURE : {excised.size} cellules excisees, seuil {args.min_excised}.\n"
            "Un test sur un echantillon aussi petit rendrait un nombre, pas un resultat.",
            file=sys.stderr,
        )
        return 3

    from scipy.stats import mannwhitneyu

    statistic, p_value = mannwhitneyu(excised, control, alternative="two-sided")
    delta = cliffs_delta(excised.astype(float), control.astype(float))
    magnitude = (
        "negligeable" if abs(delta) < 0.147
        else "petite" if abs(delta) < 0.33
        else "moyenne" if abs(delta) < 0.474
        else "grande"
    )

    print(f"Mann-Whitney U      : {statistic:.0f}")
    print(f"valeur p            : {p_value:.3g}")
    print(f"delta de Cliff      : {delta:+.3f}  ({magnitude})")
    print(f"ecart des medianes  : {np.median(excised) - np.median(control):+.1f} niveaux de gris")
    print()
    if p_value >= 0.05:
        print("H0 NON REJETEE : rien ne distingue les cellules excisees des temoins.")
    else:
        sense = "PLUS SOMBRES" if delta < 0 else "PLUS CLAIRES"
        print(f"H0 REJETEE : les cellules excisees sont {sense} que les temoins appariees.")
        if magnitude == "negligeable":
            print(
                "  ATTENTION : l'ecart est distinguable du hasard mais sa taille d'effet\n"
                "  est negligeable. Avec assez de points, tout ecart devient significatif."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
