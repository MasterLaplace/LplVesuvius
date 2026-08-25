#!/usr/bin/env python3
"""La marche de phase prédit-elle les croisements recensés ?

⚠ Le référent est l'index publié de `windcheck` : un recensement obtenu par une méthode
entièrement différente (auto-intersection d'un maillage) de la nôtre (discontinuité de
la phase d'enroulement lue dans le volume). S'ils corrèlent, les deux voient le même
défaut ; sinon, l'un des deux mesure autre chose.

⚠⚠ **La puissance est rapportée avec le résultat.** Sur 8 traces, les quatre statistiques
donnaient rho +0,44 à +0,52 et aucune n'était significative — à n = 8 seul un rho de
0,85 est détectable. C'est exactement la position où la mesure des fibres se trouvait à
n = 12, et où le signe s'est **inversé** en montant à n = 54.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def detectable(n: int, power: float = 0.80, alpha: float = 0.05) -> float:
    from scipy.stats import norm

    if n < 6:
        return float("nan")
    return float(np.tanh((norm.ppf(1 - alpha / 2) + norm.ppf(power)) / np.sqrt(n - 3)))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Marche de phase contre croisements publies.",
    )
    parser.add_argument("dossier", type=Path)
    parser.add_argument("index", type=Path)
    parser.add_argument("--corpus", default="PHerc0139")
    args = parser.parse_args()

    from scipy.stats import spearmanr

    published = {r["segment"]: r for r in json.loads(args.index.read_text())
                 if r["corpus"] == args.corpus}
    rows = []
    for path in sorted(args.dossier.glob("*.json")):
        d = json.loads(path.read_text())
        seg = path.stem
        if seg in published:
            rows.append((seg, d, published[seg]))
    if len(rows) < 6:
        print(f"erreur : {len(rows)} traces communes", file=sys.stderr)
        return 2

    events = np.array([p["events"] for _, _, p in rows], float)
    span = np.array([p["covering_span_rev"] for _, _, p in rows], float)
    n = len(rows)
    print(f"{args.corpus} — {n} traces mesurees et publiees")
    print(f"⚠ a n = {n}, la mesure detecte un rho de {detectable(n):.2f} a 80 % de puissance")
    print(f"  croisements : {int(events.min())} a {int(events.max())}, "
          f"{int((events == 0).sum())} traces a zero")
    print()
    print(f"  {'grandeur':22} {'rho ~ croisements':>18} {'p':>9} {'rho ~ tours':>13}")
    for key, label in (("marche_mediane", "marche mediane"),
                       ("marche_p95", "p95"),
                       ("marche_p99", "p99"),
                       ("marche_max", "max")):
        values = np.array([d.get(key, np.nan) for _, d, _ in rows], float)
        keep = np.isfinite(values)
        if keep.sum() < 6:
            continue
        r = spearmanr(values[keep], events[keep])
        rs = spearmanr(values[keep], span[keep])
        flag = " ⭐" if r.pvalue < 0.05 else ""
        print(f"  {label:22} {r.statistic:>+18.3f} {r.pvalue:>9.3f} "
              f"{rs.statistic:>+13.3f}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
