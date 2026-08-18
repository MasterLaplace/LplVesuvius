#!/usr/bin/env python3
"""Nos instruments de trace predisent-ils ce qu'un recensement INDEPENDANT recense ?

⚠⚠ C'est le seul controle dont on dispose qui ne demande ni verite terrain, ni encre,
ni juge : `windcheck` publie, pour chaque segment, un nombre de **croisements** obtenus
par une methode entierement differente de la notre. Si un de nos instruments corrèle
avec ce compte, il mesure quelque chose de reel ; s'il ne corrèle avec rien, il mesure
son propre bruit.

⚠ **La puissance est rapportee avec le resultat**, toujours. « Pas de correlation » ne
veut rien dire sans le rho que la taille d'echantillon permettait de detecter -- c'est
la regle nº 7 du depot, apprise en tranchant la tache D.

⚠ Rangs de Spearman et non Pearson : les comptes de croisements sont tres asymetriques
(quelques traces en portent des centaines, la plupart aucune).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load_index(path: Path) -> dict:
    return {r["segment"]: r for r in json.loads(path.read_text())}


def detectable_rho(n: int, power: float = 0.80, alpha: float = 0.05) -> float:
    """Le rho que n observations detectent a `power`, par l'approximation de Fisher.

    Rapporte a cote d'un zero, il transforme « on n'a rien vu » en « on aurait vu ceci ».
    """
    from scipy.stats import norm

    if n < 6:
        return float("nan")
    z = (norm.ppf(1 - alpha / 2) + norm.ppf(power)) / np.sqrt(n - 3)
    return float(np.tanh(z))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correler nos instruments de trace aux croisements publies.",
        epilog="Un zero se rapporte avec la puissance qui l'accompagne.",
    )
    parser.add_argument("index", type=Path, help="results/index.json de windcheck")
    parser.add_argument("mesures", type=Path, nargs="+",
                        help="JSON de zarr_depth.py ou fiber_orientation.py")
    parser.add_argument("--champs", nargs="*", default=[],
                        help="grandeurs a correler (defaut: toutes les numeriques)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from scipy.stats import spearmanr

    published = load_index(args.index)
    rows = []
    for path in args.mesures:
        for entry in json.loads(path.read_text()):
            if entry.get("segment") in published:
                rows.append((path.name, entry))
    if len(rows) < 6:
        print(f"erreur : {len(rows)} segments communs avec l'index publie, "
              "trop peu pour une correlation", file=sys.stderr)
        return 2

    by_file: dict[str, list] = {}
    for name, entry in rows:
        by_file.setdefault(name, []).append(entry)

    report = []
    for name, entries in by_file.items():
        events = np.array([published[e["segment"]]["events"] for e in entries], float)
        span = np.array([published[e["segment"]]["covering_span_rev"] for e in entries], float)
        fields = args.champs or sorted(
            k for k, v in entries[0].items()
            if isinstance(v, (int, float)) and not isinstance(v, bool))
        n = len(entries)
        print(f"\n=== {name} — {n} segments communs avec l'index ===")
        print(f"⚠ a n = {n}, la mesure detecte un rho de "
              f"{detectable_rho(n):.2f} a 80 % de puissance")
        print(f"  {'grandeur':32} {'rho ~ croisements':>18} {'p':>10} {'rho ~ tours':>12}")
        for field in fields:
            values = np.array([e.get(field, np.nan) for e in entries], float)
            keep = np.isfinite(values)
            if keep.sum() < 6 or np.ptp(values[keep]) == 0:
                continue
            rho, p = spearmanr(values[keep], events[keep])
            rho_span, _ = spearmanr(values[keep], span[keep])
            flag = " ⭐" if p < 0.05 else ""
            print(f"  {field:32} {rho:>+18.3f} {p:>10.3f} {rho_span:>+12.3f}{flag}")
            report.append({"fichier": name, "grandeur": field, "n": int(keep.sum()),
                           "rho_croisements": float(rho), "p": float(p),
                           "rho_tours": float(rho_span),
                           "rho_detectable": detectable_rho(int(keep.sum()))})

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
