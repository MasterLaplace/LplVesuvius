#!/usr/bin/env python3
"""La prédiction de `docs/12` tient-elle ? — *écart médian > ~50 µm ⇒ pas d'encre lisible*

⚠⚠ **C'est une prédiction POSÉE AVANT la mesure**, et son auteur en a écrit la faiblesse
sur place : *« le seuil est le milieu de l'intervalle observé à n = 3, donc provisoire par
construction »*. La tester est la seule façon de savoir si c'était une intuition ou un
nombre choisi pour que trois points passent.

Trois questions, dans cet ordre, parce que la troisième n'a de sens que si les deux
premières répondent :

1. **Le seuil sépare-t-il ?** Les segments au-delà de 50 µm ont-ils moins d'encre ?
2. **Ce seuil-là a-t-il quelque chose de particulier ?** On balaye toute la plage : si
   50 µm n'est pas meilleur que 30 ou que 90, ce n'était pas un seuil, c'était une
   coordonnée.
3. **Et la prédiction forte** — *pas d'encre lisible*, pas *moins d'encre* — demande que
   les segments au-delà tombent sous ce que rend un segment vierge. On ne l'a pas ; ce qui
   s'en approche est la comparaison au **premier décile** du corpus.

⚠ La règle nº 1 du dépôt interdit les seuils absolus sur une grandeur physique. Ce fichier
ne l'enfreint pas : il **teste** un seuil proposé ailleurs, et rapporter qu'il ne tient pas
est précisément ce qui fait respecter la règle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from croiser_instruments import detectable_rho  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Tester la prediction de docs/12 sur un corpus.")
    parser.add_argument("rapport", type=Path, help="sortie de croiser_encre.py")
    parser.add_argument("--voxel-um", type=float, default=2.4)
    parser.add_argument("--seuil-um", type=float, default=50.0)
    parser.add_argument("--cible", default="encre_contraste_p90_p50")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    from scipy.stats import mannwhitneyu

    lignes = json.loads(args.rapport.read_text())["segments"]
    ecart = np.array([l["ecart_a_la_trace"] * args.voxel_um for l in lignes], dtype=float)
    encre = np.array([l[args.cible] for l in lignes], dtype=float)
    bon = np.isfinite(ecart) & np.isfinite(encre)
    ecart, encre = ecart[bon], encre[bon]
    n = ecart.size

    print(f"{n} segments · ecart median {np.median(ecart):.1f} um "
          f"(p10 {np.percentile(ecart, 10):.1f}, p90 {np.percentile(ecart, 90):.1f})")
    print(f"⚠ a n = {n}, rho detectable {detectable_rho(n):.2f}\n")

    # --- 1. le seuil propose separe-t-il ?
    haut = ecart > args.seuil_um
    if haut.sum() < 4 or (~haut).sum() < 4:
        print(f"⚠ le seuil de {args.seuil_um:.0f} um laisse {int(haut.sum())} segments "
              f"d'un cote : rien a comparer")
        return 1
    u, p = mannwhitneyu(encre[haut], encre[~haut], alternative="less")
    print(f"seuil propose de {args.seuil_um:.0f} um : "
          f"{int(haut.sum())} au-dessus, {int((~haut).sum())} au-dessous")
    print(f"  encre mediane au-dessus  {np.median(encre[haut]):.3f}")
    print(f"  encre mediane au-dessous {np.median(encre[~haut]):.3f}")
    print(f"  Mann-Whitney unilateral  p = {p:.4f}"
          f"{'  *' if p < 0.05 else '   (non significatif)'}")

    # --- 2. ce seuil-la a-t-il quelque chose de particulier ?
    # ⚠ S'il ne bat pas ses voisins, ce n'etait pas un seuil mais une coordonnee. Le
    # balayage est la seule facon de le savoir, et c'est le meme critere que le plateau
    # qui a defendu le seuil d'un tiers de `07` §8.
    print(f"\n{'seuil um':>9} {'au-dessus':>10} {'p':>9}")
    balayage = []
    for seuil in np.arange(20.0, 121.0, 10.0):
        h = ecart > seuil
        if h.sum() < 4 or (~h).sum() < 4:
            continue
        _, pv = mannwhitneyu(encre[h], encre[~h], alternative="less")
        balayage.append({"seuil_um": float(seuil), "au_dessus": int(h.sum()),
                         "p": float(pv)})
        marque = " *" if pv < 0.05 else ""
        cible = " <- propose par `12`" if abs(seuil - args.seuil_um) < 5 else ""
        print(f"{seuil:>9.0f} {int(h.sum()):>10} {pv:>9.4f}{marque}{cible}")

    if balayage:
        meilleur = min(balayage, key=lambda b: b["p"])
        print(f"\nmeilleur seuil du balayage : {meilleur['seuil_um']:.0f} um "
              f"(p = {meilleur['p']:.4f})")

    # --- 3. la prediction FORTE : « pas d'encre lisible », pas « moins d'encre ».
    plancher = float(np.percentile(encre, 10))
    sous = float((encre[haut] <= plancher).mean())
    print(f"\nprediction FORTE — « pas d'encre lisible » :")
    print(f"  premier decile du corpus : {plancher:.3f}")
    print(f"  part des segments au-dessus du seuil qui y tombent : {sous * 100:.0f} %")
    print(f"  (attendu si le seuil ne disait rien : 10 %)")

    rapport = {"n": n, "seuil_um": args.seuil_um,
               "p_seuil_propose": float(p),
               "encre_au_dessus": float(np.median(encre[haut])),
               "encre_au_dessous": float(np.median(encre[~haut])),
               "balayage": balayage,
               "part_sous_premier_decile": sous}
    if args.out:
        args.out.write_text(json.dumps(rapport, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
