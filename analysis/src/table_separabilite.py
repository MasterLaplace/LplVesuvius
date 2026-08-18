#!/usr/bin/env python3
"""Tableau de séparabilité des rouleaux, avec son témoin.

⚠ Le témoin est `PHerc0139` : **tracé, et son titre retrouvé**, avec le protocole exact
des 13 rouleaux du prix (9,362 µm / 1,2 m / 113 keV). Comparer à lui, c'est comparer à
un rouleau qu'on sait traitable **à qualité de scan égale**.

⚠⚠ Ce d′ ne compare que des scans à **résolution égale** — voir l'en-tête de
`separabilite_scan.py` : résoudre plus de structure abaisse mécaniquement l'indice.
Les 13 sont à 8,640–9,362 µm et le témoin à 9,362 : la comparaison est licite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TEMOIN = "_TEMOIN_PHerc0139"


def main() -> int:
    parser = argparse.ArgumentParser(description="Separabilite : prix contre temoin.")
    parser.add_argument("dossier", type=Path)
    args = parser.parse_args()

    rows = []
    for path in sorted(args.dossier.glob("*.json")):
        d = json.loads(path.read_text())
        if "d_prime_median" not in d:
            continue
        rows.append((path.stem, d))
    if not rows:
        print("erreur : aucune mesure", file=sys.stderr)
        return 2

    control = next((r for r in rows if r[0] == TEMOIN), None)
    others = sorted((r for r in rows if r[0] != TEMOIN),
                    key=lambda r: -r[1]["d_prime_median"])

    print(f"{'rouleau':16} {'d′ median':>10} {'p10':>8} {'min':>8} "
          f"{'sous 1,0':>10} {'chunks':>8}")
    print("-" * 64)
    for name, d in others:
        print(f"{name:16} {d['d_prime_median']:>10.2f} {d['d_prime_p10']:>8.2f} "
              f"{d['d_prime_min']:>8.2f} {d['part_sous_1'] * 100:>8.0f} % "
              f"{d['chunks']:>8}")
    if control:
        name, d = control
        print("-" * 64)
        print(f"{'PHerc0139':16} {d['d_prime_median']:>10.2f} {d['d_prime_p10']:>8.2f} "
              f"{d['d_prime_min']:>8.2f} {d['part_sous_1'] * 100:>8.0f} % "
              f"{d['chunks']:>8}   ⭐ TEMOIN — trace, titre retrouve")
        better = [n for n, x in others if x["d_prime_median"] >= d["d_prime_median"]]
        print()
        print(f"⚠ {len(better)} rouleaux du prix sur {len(others)} ont une separabilite "
              f"EGALE OU MEILLEURE que le temoin :")
        print(f"   {', '.join(better) or '—'}")
        print()
        print("> Un rouleau aussi separable que celui qu'on a su tracer et lire n'a pas")
        print("> d'excuse de qualite de scan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
