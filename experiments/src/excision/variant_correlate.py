#!/usr/bin/env python3
"""Chaque definition de reference locale corrige-t-elle quelque chose ?

⚠⚠ **Ce fichier existe pour ne PAS choisir apres avoir vu.** `06` §3.2 a etabli que la
reference « locale » de `proximity.py` couvre 96,9 % d'un tour, donc qu'elle n'est pas
locale. Le correctif se justifie **avant** toute correlation : une reference qui
melange 59,5 % de l'etendue radiale ne peut pas normaliser un espacement qui depend du
rayon. Ce qui reste a savoir est ce que le correctif change, et la reponse honnete
exige de montrer **toute la famille**, l'ancienne definition comprise.

Ce qu'on lit dans le tableau, et dans cet ordre :

1. **Un plateau** -- plusieurs definitions voisines donnent le meme rho. Alors le choix
   n'est pas critique et la mesure est robuste. C'est ce que §3.7 a etabli pour le
   seuil (0,15 a 0,40, rho 0,759 a 0,779).
2. **Un pic** -- une seule definition sort du lot. Alors c'est du sur-ajustement, et le
   chiffre ne vaut pas mieux que celui d'avant.
3. **Rien ne bouge** -- la reference n'etait pas le facteur limitant, et il faut le
   dire plutot que de chercher une autre variante jusqu'a en trouver une qui monte.

⚠ La couverture est rapportee a cote du rho : une reference tres etroite laisse des
cellules sans voisins, donc sans reference. Un rho calcule sur moitie moins de
cellules n'est pas comparable a un rho calcule sur toutes, et l'omettre ferait passer
une perte de donnees pour un gain de qualite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from excision.correlate import load_published, spearman  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Correler chaque variante de reference locale aux croisements publies.",
        epilog="Montre TOUTE la famille : un plateau se defend, un pic non.",
    )
    parser.add_argument("sweep", type=Path, help="JSONL de baseline_sweep.py")
    parser.add_argument("published", type=Path, help="results/index.json de windcheck")
    parser.add_argument("--corpus", default="Scroll 1")
    parser.add_argument("--field", default="fraction_below_third")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    published = load_published(args.published, args.corpus)
    records = [json.loads(line) for line in args.sweep.read_text().splitlines() if line.strip()]
    measured = {r["label"]: r for r in records}
    common = sorted(set(published) & set(measured))
    if len(common) < 5:
        print(f"erreur : {len(common)} traces communes", file=sys.stderr)
        return 2

    events = np.array([published[s]["events"] for s in common], dtype=float)
    span = np.array([published[s]["covering_span_rev"] for s in common], dtype=float)
    variants = sorted({name for r in records for name in r["variants"]})

    print(f"corpus {args.corpus} — {len(common)} traces communes, grandeur {args.field}")
    print(f"{'variante':16} {'rho croisements':>16} {'p':>10} {'rho longueur':>13} "
          f"{'couverture':>11}")
    rows = []
    for variant in variants:
        values, keep = [], []
        for index, label in enumerate(common):
            entry = measured[label]["variants"].get(variant, {})
            if args.field in entry:
                values.append(entry[args.field])
                keep.append(index)
        if len(values) < 5:
            print(f"{variant:16} {'trop peu de traces':>16}")
            continue
        keep = np.asarray(keep)
        rho, p = spearman(np.asarray(values), events[keep])
        rho_span, _ = spearman(np.asarray(values), span[keep])
        # ⚠ La couverture est la part des cellules qui ont RECU une reference, moyennee
        # sur les traces : c'est ce qui dit si une variante etroite a paye son gain en
        # perdant des donnees.
        cover = float(np.mean([measured[common[i]]["variants"][variant]["usable"]
                               / max(1, measured[common[i]]["measured"]) for i in keep]))
        print(f"{variant:16} {rho:>+16.3f} {p:>10.2e} {rho_span:>+13.3f} "
              f"{cover * 100:>10.1f} %")
        rows.append({"variant": variant, "traces": len(values), "rho_events": rho,
                     "p": p, "rho_span": rho_span, "coverage": cover})

    if rows:
        best = max(rows, key=lambda r: r["rho_events"])
        old = next((r for r in rows if r["variant"] == "colonnes_150"), None)
        print()
        if old is not None:
            gain = best["rho_events"] - old["rho_events"]
            print(f"ancienne definition (colonnes_150) : rho {old['rho_events']:+.3f}")
            print(f"meilleure de la famille ({best['variant']}) : rho {best['rho_events']:+.3f} "
                  f"soit {gain:+.3f}")
            spread = max(r["rho_events"] for r in rows) - min(r["rho_events"] for r in rows)
            print(f"etendue des rho sur la famille : {spread:.3f} — "
                  f"{'plateau' if spread < 0.05 else 'les variantes different reellement'}")
    if args.out:
        args.out.write_text(json.dumps(rows, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
