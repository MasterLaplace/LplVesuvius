#!/usr/bin/env python3
"""Une trace suit-elle une feuille ? -- par la CONVERGENCE, sans seuil ni verite terrain.

⚠⚠ Ce fichier est ne de trois hypotheses refutees le 2026-08-20, et c'est la refutation qui
l'a produit. On a d'abord cru que nos traces etaient a une spire de leur feuille, puis a
deux, puis que la difference etait de FORME et non de distance. Les trois fois, la mesure
suivait la fenetre de rendu au lieu de suivre le papyrus.

⭐⭐ Le motif de l'echec EST le test. Sur une surface qui suit sa feuille, la matiere est la,
tout pres, et l'elargissement de la fenetre ne change rien a la distance mesuree. Sur une
surface posee EN TRAVERS de l'empilement, il n'y a aucun pic a trouver : le « pic » est le
plus fort de ce que la fenetre contenait, donc il s'eloigne avec elle.

Mesure appariee, meme rouleau, meme chaine, meme instrument :

    fenetre   segment officiel   notre trace
       21          —               86,4 µm
       31        17,3 µm             —
       41          —              159,8 µm
       81        17,3 µm          311,0 µm
      161          —              682,6 µm

⭐ Ce test a trois proprietes qu'aucun autre instrument de ce depot n'a toutes :
  - **aucun seuil** : on compare une mesure a elle-meme ;
  - **aucune verite terrain** : ni segment de reference, ni carte d'encre ;
  - **aucune echelle** : le rapport est sans dimension, donc il traverse les rouleaux, les
    tailles de voxel et les resolutions sans etre re-etalonne.

⚠ Ce qu'il ne dit PAS : de combien corriger. Une trace qui ne converge pas n'a pas de
distance a sa feuille -- il n'y a pas de feuille a portee. Le test separe « posee a cote »
de « posee en travers », et c'est tout, ce qui est deja ce que rien d'autre ne faisait.

⚠ Il faut au moins DEUX fenetres dans un rapport d'au moins deux. Deux mesures trop proches
rendraient un rapport proche de 1 quelle que soit la surface -- c'est-a-dire un test qui ne
peut pas echouer.

Usage :
    uv run python analysis/src/test_convergence.py --serie "21:86.4,41:159.84,81:311.04" \\
        --nom "notre trace" --json docs/convergence.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
# Une surface qui suit sa feuille garde sa distance ; on tolere le bruit de mesure.
CONVERGE = 1.25
# Doubler la fenetre double la mesure : le pic suit la fenetre, il n'y a pas de feuille.
SUIT_LA_FENETRE = 1.6


def analyser(serie: list[tuple[int, float]]) -> dict:
    """Rendre le verdict d'une serie (couches, ecart) -- ou refuser de le rendre."""
    serie = sorted(serie)
    if len(serie) < 2:
        return {"verdict": "indecidable", "raison": "une seule fenêtre", "serie": serie}
    (n0, e0), (n1, e1) = serie[0], serie[-1]
    if n1 / n0 < 2:
        return {"verdict": "indecidable",
                "raison": f"fenêtres trop proches ({n0} et {n1}, rapport {n1/n0:.2f})",
                "serie": serie}
    if e0 <= 0:
        return {"verdict": "indecidable", "raison": "écart nul dans la fenêtre étroite",
                "serie": serie}

    croissance = e1 / e0
    fenetre = n1 / n0
    # ⚠ On normalise par l'elargissement : comparer une serie 21->81 a une serie 21->41
    # sans ca ferait passer la premiere pour « pire » alors qu'on l'a juste regardee plus
    # loin. L'exposant est celui d'une loi de puissance ecart ∝ fenetre^alpha.
    import math
    alpha = math.log(croissance) / math.log(fenetre)

    if croissance <= CONVERGE:
        verdict, sens = "converge", ("la distance ne bouge pas quand la fenêtre s'élargit — "
                                     "la matière est là, tout près")
    elif alpha >= 0.7:
        verdict, sens = "suit la fenêtre", ("le « pic » s'éloigne avec la fenêtre — il n'y a "
                                            "aucune feuille à portée, la surface est posée "
                                            "en travers de l'empilement")
    else:
        verdict, sens = "intermédiaire", ("la mesure bouge sans suivre la fenêtre — ni "
                                          "convergée ni clairement en travers")
    return {"verdict": verdict, "sens": sens, "serie": serie,
            "croissance": croissance, "elargissement": fenetre, "alpha": alpha}


def verifier() -> int:
    """Temoin hors ligne : les deux verdicts francs, et les trois refus."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # Le cas mesure : notre trace double a chaque doublement.
    r = analyser([(21, 86.4), (41, 159.84), (81, 311.04), (161, 682.56)])
    v("une mesure qui double avec la fenêtre suit la fenêtre",
      r["verdict"] == "suit la fenêtre", r["verdict"])
    v("... avec un exposant proche de 1", abs(r["alpha"] - 1.0) < 0.15, f"{r['alpha']:.3f}")

    # Le cas mesure : le segment officiel ne bouge pas.
    v("une mesure stable converge",
      analyser([(31, 17.28), (81, 17.30)])["verdict"] == "converge")
    v("un petit bruit ne casse pas la convergence",
      analyser([(31, 17.0), (81, 20.0)])["verdict"] == "converge")

    # ⭐ Les trois refus : sans eux le test rendrait un verdict sur rien.
    v("une seule fenêtre est indécidable",
      analyser([(81, 300.0)])["verdict"] == "indecidable")
    v("deux fenêtres trop proches sont indécidables",
      analyser([(41, 100.0), (61, 150.0)])["verdict"] == "indecidable",
      analyser([(41, 100.0), (61, 150.0)])["verdict"])
    v("un écart nul est indécidable, pas convergé",
      analyser([(21, 0.0), (81, 0.0)])["verdict"] == "indecidable")

    # Un cas intermediaire doit etre nomme, pas range de force.
    m = analyser([(21, 100.0), (81, 160.0)])
    v("une croissance lente est dite intermédiaire", m["verdict"] == "intermédiaire",
      f"{m['verdict']} alpha={m['alpha']:.2f}")

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serie", action="append", default=[],
                    help="couches:écart,couches:écart… (répétable)")
    ap.add_argument("--nom", action="append", default=[])
    ap.add_argument("--depuis", action="append", default=[], metavar="JSON[=nom]",
                    help="reprendre les séries d'un verdict déjà écrit (répétable) ; "
                         "« fichier.json=nom » renomme la série")
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    # ⚠⚠ Rassembler des verdicts DÉJÀ écrits plutôt que de recopier leurs nombres à la
    # main. Une figure qui compare trois surfaces a besoin des trois séries dans un seul
    # fichier ; les retaper est le mode de panne que ce dépôt a payé plusieurs fois — un
    # chiffre juste au moment où on le lit et faux dès que la mesure bouge.
    reprises = []
    for spec in a.depuis:
        chemin, _, renomme = spec.partition("=")
        p_json = Path(chemin)
        if not p_json.is_file():
            print(f"⚠ absent, ignoré : {chemin}", file=sys.stderr)
            continue
        for serie in json.loads(p_json.read_text(encoding="utf-8")).get("series", []):
            if renomme:
                serie["nom"] = renomme
            reprises.append(serie)

    if not a.serie and not reprises:
        ap.error("donner au moins une --serie ou un --depuis, ou --verifier")

    sorties = list(reprises)
    for r in reprises:
        pts = "  ".join(f"{n}c→{e:.1f}" for n, e in r["serie"])
        print(f"\n  {r['nom']}  (repris)\n    {pts}\n    α = {r.get('alpha', 0.0):+.2f} "
              f"— {r.get('verdict', '?')}")

    for i, brut in enumerate(a.serie):
        nom = a.nom[i] if i < len(a.nom) else f"série {i + 1}"
        serie = [(int(p.split(":")[0]), float(p.split(":")[1])) for p in brut.split(",")]
        r = analyser(serie)
        r["nom"] = nom
        sorties.append(r)
        pts = "  ".join(f"{n}c→{e:.1f}" for n, e in r["serie"])
        print(f"\n  {nom}\n    {pts}")
        if r["verdict"] == "indecidable":
            print(f"    ⚠ INDÉCIDABLE — {r['raison']}")
        else:
            print(f"    ×{r['croissance']:.2f} pour ×{r['elargissement']:.1f} de fenêtre "
                  f"(α = {r['alpha']:+.2f})")
            marque = {"converge": "✅", "suit la fenêtre": "⚠⚠", "intermédiaire": "⚠"}[r["verdict"]]
            print(f"    {marque} {r['verdict'].upper()} — {r['sens']}")

    if a.json:
        Path(a.json).write_text(json.dumps({"series": sorties}, indent=2,
                                           ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
