#!/usr/bin/env python3
"""Pourquoi rendre n=161 donne déjà n=81, n=41 et n=31 — la géométrie du raccourci.

⚠⚠ **Ce que cette figure établit.** Un rendu de N couches est une pile centrée sur la surface :
la tranche d'indice `N // 2` est la surface elle-même, et les autres s'en éloignent
symétriquement. Deux fenêtres rendues **au même endroit** partagent donc toutes les tranches de
la plus étroite — ce ne sont pas des images qui se ressemblent, c'est **le même fichier**.

⭐ Mesuré : 31 tranches sur 31 identiques octet pour octet entre `rendu_31` et les tranches
25 à 55 de `rendu_81`, et le profil de profondeur qui en sort est identique sur **23 mesures
sur 23**.

⚠ La condition, et c'est elle que la figure doit rendre visible : les deux largeurs doivent
avoir la **même parité**. Le dépôt indexe le centre à `N // 2` ; deux piles de parités
différentes ont leurs centres décalés d'une demi-tranche, et aucun découpage entier ne les fait
coïncider. Dériver quand même rendrait un profil décalé — pire qu'un rendu de plus.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_sous_fenetre.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "depot"))

LARGEUR = 1020
FOND, ENCRE, GRIS = (255, 255, 255), (25, 25, 28), (150, 150, 155)
AMBRE, BLEU, PALE = (214, 141, 40), (44, 90, 160), (222, 226, 232)
SERIE = [161, 81, 41, 31]


def verifier() -> int:
    from sous_fenetre import arguments_sous_fenetre, plan_de_campagne
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # ⭐ La figure ne réinvente aucune arithmétique : elle DEMANDE au module. Une seconde
    # formule ici finirait par ne plus s'accorder avec celle qui décide vraiment.
    plan = plan_de_campagne(SERIE)
    v("la série dessinée ne rend qu'une fenêtre", plan["rendues"] == [161])
    v("... et en dérive trois", plan["economie"] == 3)
    v("la série est ordonnée du plus large au plus étroit", SERIE == sorted(SERIE, reverse=True))
    # Le dessin place chaque pile par son décalage : il doit être croissant quand la fenêtre
    # rétrécit, sinon les rectangles ne s'emboîtent pas et la figure ment sur la géométrie.
    dec = [arguments_sous_fenetre(161, n)["from_layer"] for n in SERIE[1:]]
    v("les décalages croissent quand la fenêtre rétrécit", dec == sorted(dec))
    v("chaque sous-fenêtre est centrée sur la même tranche",
      all(arguments_sous_fenetre(161, n)["from_layer"] + n // 2 == 161 // 2 for n in SERIE[1:]))
    v("toutes les sous-fenêtres tiennent dans la large",
      all(arguments_sous_fenetre(161, n)["to_layer"] <= 160 for n in SERIE[1:]))
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    racine = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/56_sous_fenetre.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from sous_fenetre import arguments_sous_fenetre
    from PIL import Image, ImageDraw, ImageFont

    def police(t):
        for n in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(n, t)
            except OSError:
                continue
        return ImageFont.load_default()

    marge, haut_tete, ligne = 150, 118, 62
    hauteur = haut_tete + ligne * len(SERIE) + 132
    im = Image.new("RGB", (LARGEUR, hauteur), FOND)
    d = ImageDraw.Draw(im)
    f_t, f_x, f_p = police(21), police(14), police(12)

    d.text((40, 26), "Rendre n=161 produit déjà n=81, n=41 et n=31 — ce sont les mêmes fichiers",
           font=f_t, fill=ENCRE)
    d.text((40, 56), "Un rendu de N couches est une pile CENTRÉE sur la surface : la tranche "
                     "N//2 est la surface elle-même.", font=f_x, fill=GRIS)

    large = SERIE[0]
    utile = LARGEUR - marge - 60
    par_tranche = utile / large
    y = haut_tete

    # L'axe : les indices de tranche de la pile large.
    d.text((marge, y - 24), "tranche 0", font=f_p, fill=GRIS)
    d.text((marge + utile - 54, y - 24), f"tranche {large - 1}", font=f_p, fill=GRIS)
    centre_x = marge + (large // 2 + 0.5) * par_tranche

    for i, n in enumerate(SERIE):
        args = {"from_layer": 0, "to_layer": large - 1} if n == large else arguments_sous_fenetre(large, n)
        x0 = marge + args["from_layer"] * par_tranche
        x1 = marge + (args["to_layer"] + 1) * par_tranche
        couleur = BLEU if n == large else AMBRE
        d.rectangle([x0, y, x1, y + 30], fill=couleur if n == large else PALE,
                    outline=couleur, width=2)
        d.text((40, y + 7), f"n = {n}", font=f_x, fill=ENCRE)
        if n == large:
            d.text((x1 + 10, y + 8), "RENDU", font=f_p, fill=BLEU)
        else:
            d.text((x1 + 10, y + 8),
                   f"--from-layer {args['from_layer']} --to-layer {args['to_layer']}",
                   font=f_p, fill=GRIS)
        y += ligne

    # ⭐ La ligne du centre : c'est elle qui explique tout. Sans elle, les rectangles emboîtés
    # ne disent pas POURQUOI ce sont les mêmes fichiers.
    d.line([centre_x, haut_tete - 12, centre_x, y - ligne + 34], fill=ENCRE, width=1)
    d.text((centre_x + 6, y - ligne + 38), "la surface — tranche N//2 de chaque pile",
           font=f_p, fill=ENCRE)

    y += 22
    d.text((40, y),
           "Mesuré : 31 tranches sur 31 identiques octet pour octet, et le profil de "
           "profondeur identique sur 23 mesures / 23.", font=f_x, fill=ENCRE)
    d.text((40, y + 24),
           "⚠ La condition : les deux largeurs doivent avoir la MÊME PARITÉ. Sinon les centres "
           "sont décalés d'une demi-tranche et", font=f_p, fill=GRIS)
    d.text((40, y + 44),
           "aucun découpage entier ne les fait coïncider — le profil dérivé serait décalé, ce "
           "qui est pire qu'un rendu de plus.", font=f_p, fill=GRIS)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"série {SERIE} — 1 rendu, {len(SERIE) - 1} dérivées  →  {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
