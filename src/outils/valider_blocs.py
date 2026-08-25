#!/usr/bin/env python3
"""Le decoupage en blocs 3D donne-t-il la MEME chose que l'arbre global ?

⚠ Une reimplementation qui change le resultat n'est pas une reimplementation, c'est
une autre mesure. Ce controle la compare a `excision.proximity` sur un maillage assez
petit pour que les deux passent -- le seul endroit ou la comparaison est possible, et
donc le seul endroit ou elle a de la valeur.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

import numpy as np

sys.path[:0] = [str(x) for x in Path(__file__).resolve().parents[1].iterdir() if x.is_dir()]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "src"))

from proximity_vs_ink import tile_proximity  # noqa: E402


def main() -> int:
    mesh = Path(sys.argv[1])
    reference = float(sys.argv[2]) if len(sys.argv) > 2 else None

    out = tile_proximity(mesh, tile=100000, sample=20000, apart=200,
                         search_radius=80.0, seed=42, block=500.0)
    blocks = out.pop("_blocks", 0)
    measured = out.pop("_measured", 0)
    if not out:
        print("erreur : aucune tuile exploitable", file=sys.stderr)
        return 3
    # tile=100000 force UNE seule tuile : on retrouve donc la grandeur globale,
    # directement comparable a ce que `excision.proximity` rapporte pour la trace.
    only = next(iter(out.values()))
    print(f"blocs 3D utilises : {blocks}   cellules mesurees : {measured}")
    print(f"below_030 (blocs) : {only['below_030']:.5f}")
    if reference is not None:
        ecart = abs(only["below_030"] - reference)
        rel = ecart / max(reference, 1e-9)
        print(f"below_030 (arbre global, publie) : {reference:.5f}")
        print(f"ecart : {ecart:.5f} soit {rel * 100:.1f} %")
        # 10 % de tolerance : les deux tirent le meme nombre de cellules avec la meme
        # graine, mais l'ordre de parcours differe, donc les ex aequo ne tombent pas
        # au meme endroit. Au-dela, ce n'est plus la meme mesure.
        print("ALL PASS (0 failures, 1 checks)" if rel <= 0.10
              else f"ECHEC : {rel * 100:.1f} % d'ecart, ce n'est plus la meme mesure")
        return 0 if rel <= 0.10 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
