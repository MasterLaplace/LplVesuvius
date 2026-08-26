#!/usr/bin/env python3
"""Joint les mesures de proximite a l'index publie de `windcheck`.

Repond a une question et une seule : la metrique de proximite dit-elle quelque
chose que le nombre de croisements ne dit pas deja ?

Trois grandeurs, et l'ordre compte :

1. la correlation brute avec le nombre de croisements -- si elle est nulle, la
   metrique ne mesure pas le meme defaut et il faut expliquer pourquoi ;
2. la correlation avec la LONGUEUR (couverture en tours) -- c'est le confond
   identifie en 05, et une metrique qui la suit ne mesure que la taille ;
3. la correlation avec les croisements A LONGUEUR COMPARABLE -- la seule qui
   etablisse que la metrique porte sur la qualite.

Rangs de Spearman et non Pearson : les deux grandeurs sont tres asymetriques
(quelques traces portent des centaines de croisements, la plupart aucun), donc une
correlation lineaire mesurerait surtout la queue.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load_published(index_path: Path, corpus: str) -> dict:
    """Index publie, filtre sur un corpus, indexe par nom de trace."""
    with index_path.open() as handle:
        records = json.load(handle)
    return {r["segment"]: r for r in records if corpus in r["corpus"]}


def load_measured(path: Path) -> dict:
    """Sortie JSON Lines de `excision.proximity`."""
    measured = {}
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("{"):
                continue
            record = json.loads(line)
            measured[record["label"]] = record
    return measured


def spearman(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    from scipy.stats import spearmanr

    result = spearmanr(a, b)
    return float(result.statistic), float(result.pvalue)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La proximite ajoute-t-elle de l'information au compte de croisements ?",
    )
    parser.add_argument("measured", type=Path, help="JSONL produit par excision.proximity")
    parser.add_argument("published", type=Path, help="results/index.json de windcheck")
    parser.add_argument("--corpus", default="Scroll 1", help="filtre de corpus (defaut: Scroll 1)")
    parser.add_argument(
        "--field", default="fraction_below_third",
        help="grandeur de proximite a correler (defaut: fraction_below_third)",
    )
    args = parser.parse_args()

    published = load_published(args.published, args.corpus)
    measured = load_measured(args.measured)
    common = sorted(set(published) & set(measured))
    if len(common) < 5:
        print(
            f"erreur : seulement {len(common)} traces communes, "
            "trop peu pour une correlation",
            file=sys.stderr,
        )
        return 2

    proximity = np.array([measured[s][args.field] for s in common])
    events = np.array([published[s]["events"] for s in common], dtype=float)
    span = np.array([published[s]["covering_span_rev"] for s in common], dtype=float)

    print(f"corpus              : {args.corpus}")
    print(f"traces publiees     : {len(published)}")
    print(f"traces mesurees     : {len(measured)}")
    print(f"traces communes     : {len(common)}")
    print(f"grandeur correlee   : {args.field}")
    print()

    rho_events, p_events = spearman(proximity, events)
    rho_span, p_span = spearman(proximity, span)
    rho_span_events, _ = spearman(span, events)
    print(f"proximite ~ croisements     rho = {rho_events:+.3f}  (p = {p_events:.3g})")
    print(f"proximite ~ longueur        rho = {rho_span:+.3f}  (p = {p_span:.3g})")
    print(f"longueur   ~ croisements    rho = {rho_span_events:+.3f}   <- le confond")
    print()

    # A longueur comparable : on decoupe en tranches de couverture et on correle
    # dedans. C'est la version pauvre d'une correlation partielle, mais elle se lit
    # sans hypothese de linearite, et elle montre OU l'effet tient.
    order = np.argsort(span)
    bins = np.array_split(order, 3)
    print("a longueur comparable (tercile de couverture) :")
    for index, group in enumerate(bins, start=1):
        if group.size < 5:
            print(f"  tercile {index} : {group.size} traces, trop peu")
            continue
        rho, p = spearman(proximity[group], events[group])
        print(
            f"  tercile {index} : n={group.size:2d}  couverture {span[group].min():.2f}"
            f"-{span[group].max():.2f} tours   rho = {rho:+.3f}  (p = {p:.3g})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
