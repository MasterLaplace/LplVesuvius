#!/usr/bin/env python3
"""`material` mesure-t-il le segment, ou notre façon de l'échantillonner ?

⚠⚠ **L'objection qu'un relecteur posera en premier.** `docs/19` fait reposer sa règle sur
`avec_matiere` — la part de fenêtres sondées qui contiennent du papyrus. Mais cette part
dépend d'une **grille de sondage**, et un segment dont la bande tombe bien sur la grille
en obtiendrait davantage qu'un autre. Si c'était le cas, la règle trierait des grilles et
non des traces.

Le test ne coûte rien parce que **deux échantillonneurs différents ont déjà mesuré les
mêmes segments**, sans que ce soit prévu :

| outil | grille |
|---|---|
| `zarr_depth.py` | treillis carré `sqrt(windows)` × `min(2·sqrt, cols)`, 36 fenêtres |
| `champ_correction.py` | passe de repérage 10 × 20, soit 200 fenêtres |

Nombre de fenêtres, forme du treillis et densité diffèrent tous. Si les deux s'accordent
sur le classement des segments, la grandeur est une propriété du **segment**.

⚠ On compare des **rangs**, pas des valeurs : les deux grilles n'ont ni le même nombre de
points ni la même couverture, donc leurs fractions absolues n'ont aucune raison d'être
égales. C'est le classement qui porte la règle de `19`, et c'est donc le classement qu'il
faut vérifier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(
        description="La part de matiere est-elle une propriete du segment ou de la grille ?")
    parser.add_argument("profondeur", type=Path,
                        help="JSON de zarr_depth.py, ou repertoire d'un fichier par segment")
    parser.add_argument("champs", type=Path,
                        help="l'autre grille : JSON unique ou repertoire")
    parser.add_argument("--nom-a", default="grille A")
    parser.add_argument("--nom-b", default="grille B")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from scipy.stats import spearmanr

    def charger(chemin: Path) -> dict:
        """Accepte un JSON unique ou un répertoire d'un fichier par segment.

        ⚠ Les deux formes existent dans ce dépôt parce qu'une campagne longue doit être
        reprenable (piège nº 13) alors qu'une courte n'en a pas besoin. Le lecteur
        s'adapte plutôt que d'imposer une conversion à chaque appel.
        """
        fichiers = sorted(chemin.glob("*.json")) if chemin.is_dir() else [chemin]
        out = {}
        for f in fichiers:
            contenu = json.loads(f.read_text())
            for rec in (contenu if isinstance(contenu, list) else [contenu]):
                if rec.get("segment") and rec.get("sondees"):
                    out[rec["segment"]] = rec["avec_matiere"] / rec["sondees"]
        return out

    a = charger(args.profondeur)
    b = charger(args.champs)

    communs = sorted(set(a) & set(b))
    if len(communs) < 8:
        print(f"seulement {len(communs)} segments communs", file=sys.stderr)
        return 1

    x = np.array([a[s] for s in communs])
    y = np.array([b[s] for s in communs])
    rho, p = spearmanr(x, y)

    print(f"{len(communs)} segments mesures par les DEUX echantillonneurs")
    print(f"  {args.nom_a:<38} mediane {np.median(x) * 100:5.1f} %")
    print(f"  {args.nom_b:<38} mediane {np.median(y) * 100:5.1f} %")
    print(f"\n  accord des CLASSEMENTS : rho = {rho:+.3f}  (p = {p:.2e})")

    # ⚠ Le temoin : un classement au hasard sur les memes valeurs. Sans lui, un rho
    # positif pourrait n'etre qu'une propriete de la statistique de rang.
    rng = np.random.default_rng(0)
    nuls = np.array([abs(spearmanr(x, rng.permutation(y))[0]) for _ in range(1000)])
    print(f"  temoin (1000 permutations) : |rho| median {np.median(nuls):.3f}, "
          f"p95 {np.percentile(nuls, 95):.3f}")

    verdict = ("la part de matiere est une propriete du SEGMENT"
               if rho > np.percentile(nuls, 95) else
               "⚠ l'accord ne bat pas le hasard : la grandeur suit la grille")
    print(f"\n⇒ {verdict}")

    if args.out:
        args.out.write_text(json.dumps(
            {"segments": len(communs), "rho": float(rho), "p": float(p),
             "temoin_p95": float(np.percentile(nuls, 95)), "verdict": verdict},
            indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
