#!/usr/bin/env python3
"""Le tableau de difficulté des rouleaux, avec son témoin.

⚠ Un écart en micromètres ne veut rien dire seul. Ce qui le rend lisible est le
**témoin** : `PHercParis4` a été déroulé ET lu, avec la même prédiction de surface et
au même pas physique. Tout rouleau plus lâche que lui n'a pas d'excuse géométrique.

⚠ La ligne du témoin est marquée, jamais mélangée au classement — un contrôle rangé
parmi les cas mesurés cesse d'être un contrôle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TEMOIN = "PHercParis4"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Tableau d'ecart entre spires, rouleaux du prix contre temoin.",
    )
    parser.add_argument("dossier", type=Path)
    parser.add_argument("--seuil", default="0.5")
    args = parser.parse_args()

    rows = []
    for path in sorted(args.dossier.glob("*.json")):
        data = json.loads(path.read_text())
        entry = data.get("seuils", {}).get(args.seuil)
        if not entry:
            print(f"⚠ {path.stem} : pas de mesure au seuil {args.seuil}", file=sys.stderr)
            continue
        rows.append((path.stem, entry, data.get("voxel_um", float("nan"))))
    if not rows:
        print("erreur : aucune mesure", file=sys.stderr)
        return 2

    control = next((r for r in rows if r[0] == TEMOIN), None)
    others = sorted((r for r in rows if r[0] != TEMOIN), key=lambda r: r[1]["median_um"])

    print(f"{'rouleau':14} {'ecart median':>13} {'p10':>8} {'min':>8} "
          f"{'< 150 um':>10} {'voxel lu':>10}")
    print("-" * 68)
    for name, e, v in others:
        print(f"{name:14} {e['median_um']:>10.0f} µm {e['p10_um']:>6.0f} µm "
              f"{e['min_um']:>6.0f} µm {e['part_sous_150um'] * 100:>8.0f} % "
              f"{v:>8.1f} µm")
    if control:
        name, e, v = control
        print("-" * 68)
        print(f"{name:14} {e['median_um']:>10.0f} µm {e['p10_um']:>6.0f} µm "
              f"{e['min_um']:>6.0f} µm {e['part_sous_150um'] * 100:>8.0f} % "
              f"{v:>8.1f} µm   ⭐ TEMOIN — deroule et LU")
        tighter = [n for n, x, _ in others if x["median_um"] < e["median_um"]]
        looser = [n for n, x, _ in others if x["median_um"] >= e["median_um"]]
        print()
        print(f"⚠ {len(looser)} rouleaux du prix sur {len(others)} sont AUSSI LACHES ou "
              f"plus que le temoin :")
        print(f"   {', '.join(looser)}")
        print(f"⚠ {len(tighter)} sont plus serres : {', '.join(tighter) or '—'}")
        print()
        print("> Un rouleau plus lache que celui qu'on a su lire n'a pas d'excuse")
        print("> geometrique. La compression n'est pas ce qui l'a empeche d'etre trace.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
