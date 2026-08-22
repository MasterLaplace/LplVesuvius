#!/usr/bin/env python3
"""Que produit un détecteur d'encre sur un substrat dont on SAIT qu'il n'en porte pas ?

⚠⚠ **Le contrôle négatif que le domaine n'a pas.** Le papier fondateur d'EduceLab rapporte
un taux de faux positifs de 0,051 — mais sur des images qui contiennent de l'encre partout
autour. Il ne mesure jamais ce que le détecteur produit sur un substrat **connu sans
encre**. Le témoin parfait était pourtant dans leur scan — la feuille de papier de support
sur laquelle les fragments sont montés, imagée dans la même session, au même voxel — et le
nettoyage manuel le supprime : *« These are removed manually. »*

⭐⭐ **Le nôtre est meilleur, et il est déjà mesuré.** Une de nos traces sort à α = +1,01 :
sa distance à la matière **suit la fenêtre de rendu**, donc il n'y a aucune feuille à
portée — la surface est posée *en travers* de l'empilement. Ce n'est pas une supposition
sur la nature d'un substrat, c'est une **preuve géométrique** qu'il n'y a pas de face de
papyrus là. Toute « encre » que le modèle y rapporte est un faux positif par construction.

⚠ Ce fichier ne fait que **comparer deux prédictions**. Il ne juge ni l'une ni l'autre :
c'est la campagne qui garantit que les deux viennent du même volume, du même modèle, de la
même région et du même pas. Sans cette garantie, la comparaison ne voudrait rien dire, et
elle n'est pas vérifiable ici.

⚠⚠ **Ce que ce contrôle NE peut pas faire, et il faut le dire avant de le lire.** La région
rendue fait 1100 px de côté et le pas de balayage 8, donc la carte de prédiction fait
~137 px : **deux ordres de grandeur trop petite** pour que l'instrument typographique de
[`45`] y voie un interligne, qui demande des fenêtres de 512 px. On compare donc ce qu'une
carte de cette taille porte réellement — le **niveau** et la **dispersion** de la
prédiction — et pas sa typographie. Prétendre le contraire serait mesurer du bruit.

Usage :
    cd inference && uv run python ../analysis/src/temoin_negatif.py \\
        --positif ../data/temoin_negatif/sur_sa_feuille.npy \\
        --negatif ../data/temoin_negatif/en_travers.npy \\
        --json ../docs/temoin_negatif.json
    python3 ../analysis/src/temoin_negatif.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def decrire(carte) -> dict:
    """Ce qu'une carte de prédiction porte, sans jamais supposer qu'elle porte du texte.

    ⭐ `sigma` est la grandeur qui compte, et `36` §5bis l'a déjà utilisée : un modèle qui
    ne trouve rien ne rend pas zéro, il rend une **constante**. C'est l'écart-type qui
    l'attrape, pas la moyenne — une constante haute et une prédiction riche ont la même
    moyenne et des dispersions incomparables.
    """
    import numpy as np
    a = np.asarray(carte, dtype=np.float64).ravel()
    a = a[np.isfinite(a)]
    if a.size < 16:
        return {"n": int(a.size), "raison": "carte trop petite"}
    q = np.percentile(a, [5, 50, 95])
    return {"n": int(a.size), "moyenne": float(a.mean()), "sigma": float(a.std()),
            "p05": float(q[0]), "mediane": float(q[1]), "p95": float(q[2]),
            "contraste_p95_p50": float(q[2] - q[1]),
            # ⚠ La part de la carte au-dessus de son propre milieu de plage : sur une
            # prediction constante elle s'effondre ou explose, sur une prediction
            # structuree elle reste dans une plage etroite.
            "part_haute": float((a > (a.min() + a.max()) / 2).mean())}


def comparer(positif, negatif) -> dict:
    """Le rapport des dispersions, et ce qu'il veut dire.

    ⚠⚠ Le verdict porte sur un RAPPORT, pas sur un seuil absolu. Un écart-type dépend de
    l'échelle de sortie du modèle, qui n'est pas la même d'un modèle à l'autre ; le rapport
    entre deux prédictions du **même** modèle, lui, est comparable. C'est la même raison qui
    fait que le test de convergence de `38` lit un exposant plutôt qu'une distance.
    """
    p, n = decrire(positif), decrire(negatif)
    if "raison" in p or "raison" in n:
        return {"positif": p, "negatif": n, "raison": "une des cartes est trop petite"}
    rapport = (p["sigma"] / n["sigma"]) if n["sigma"] > 0 else float("inf")
    return {"positif": p, "negatif": n, "rapport_sigma": rapport,
            "rapport_contraste": ((p["contraste_p95_p50"] / n["contraste_p95_p50"])
                                  if n["contraste_p95_p50"] > 0 else float("inf"))}


def verifier() -> int:
    import numpy as np
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    rng = np.random.default_rng(0)
    riche = rng.normal(0.5, 0.20, size=(120, 120)).clip(0, 1)
    plate = np.full((120, 120), 0.5) + rng.normal(0, 0.002, size=(120, 120))

    d = decrire(riche)
    v("une carte structurée a une dispersion", d["sigma"] > 0.1, f"{d['sigma']:.4f}")
    v("... et un contraste p95−p50", d["contraste_p95_p50"] > 0.1)
    dp = decrire(plate)
    v("une carte CONSTANTE a une dispersion effondrée", dp["sigma"] < 0.01,
      f"{dp['sigma']:.5f}")

    c = comparer(riche, plate)
    v("le rapport des sigmas sépare les deux", c["rapport_sigma"] > 20,
      f"{c['rapport_sigma']:.1f}")
    # ⚠⚠ LA sonde : deux cartes ÉQUIVALENTES doivent donner un rapport proche de 1. Sans
    # ce controle, un instrument qui rendrait toujours un grand rapport passerait pour un
    # discriminant alors qu'il ne discriminerait rien.
    autre = rng.normal(0.5, 0.20, size=(120, 120)).clip(0, 1)
    c2 = comparer(riche, autre)
    v("... et ne sépare PAS deux cartes équivalentes",
      0.8 < c2["rapport_sigma"] < 1.25, f"{c2['rapport_sigma']:.3f}")
    # ⚠ La moyenne, elle, ne discrimine pas : les deux cartes de synthese ont la meme.
    # C'est pourquoi le verdict porte sur sigma et non sur le niveau.
    v("la moyenne ne distingue pas une constante d'une prédiction riche",
      abs(decrire(riche)["moyenne"] - dp["moyenne"]) < 0.02,
      f"{decrire(riche)['moyenne']:.3f} contre {dp['moyenne']:.3f}")

    v("une carte trop petite est REFUSÉE, pas décrite",
      "raison" in decrire(np.zeros(4)))
    v("... et la comparaison refuse aussi",
      "raison" in comparer(np.zeros(4), riche))
    v("une carte strictement constante ne divise pas par zéro",
      comparer(riche, np.full((50, 50), 0.5))["rapport_sigma"] == float("inf"))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--positif", type=Path, help="prédiction sur la surface qui CONVERGE")
    ap.add_argument("--negatif", type=Path, help="prédiction sur la surface EN TRAVERS")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.positif or not a.negatif:
        ap.error("nommer les deux cartes, ou --verifier")

    import numpy as np
    for f in (a.positif, a.negatif):
        if not f.is_file():
            print(f"absent : {f} — lancer d'abord tools/campagne_temoin_negatif.sh",
                  file=sys.stderr)
            return 1
    d = comparer(np.load(a.positif), np.load(a.negatif))
    if "raison" in d:
        print(f"⚠ {d['raison']}", file=sys.stderr)
        return 1

    print(f"\n  {'':<22} {'n':>7} {'moyenne':>9} {'sigma':>9} {'p95−p50':>9} "
          f"{'part haute':>11}")
    print("  " + "-" * 72)
    for nom, k in (("sur sa feuille  α=+0,00", "positif"),
                   ("en travers      α=+1,01", "negatif")):
        x = d[k]
        print(f"  {nom:<22} {x['n']:>7} {x['moyenne']:>9.4f} {x['sigma']:>9.4f} "
              f"{x['contraste_p95_p50']:>9.4f} {x['part_haute']:>11.3f}")

    print(f"\n  rapport des écarts-types : ×{d['rapport_sigma']:.1f}")
    print(f"  rapport des contrastes   : ×{d['rapport_contraste']:.1f}")
    if d["rapport_sigma"] >= 3.0:
        print("\n  ⭐⭐ Le détecteur se TAIT là où la géométrie prouve qu'il n'y a pas de")
        print("      feuille. C'est le contrôle négatif que le papier fondateur n'a pas :")
        print("      un substrat connu sans encre, dans le même volume et le même modèle.")
    elif d["rapport_sigma"] <= 1.5:
        print("\n  ⚠⚠ Le détecteur produit AUTANT de structure sur une surface dont on a la")
        print("      preuve géométrique qu'elle n'est pas une feuille. Ce qu'il rapporte")
        print("      là est un faux positif par construction — et rien ne le distinguait.")
    else:
        print("\n  ⚠ Écart intermédiaire : le détecteur est plus discret sur le témoin, sans")
        print("    s'y taire. À ne pas lire comme une validation.")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
