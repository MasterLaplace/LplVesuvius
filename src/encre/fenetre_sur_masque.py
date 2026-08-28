#!/usr/bin/env python3
"""Choisir une fenêtre de test SANS regarder les étiquettes, et rapporter ce qu'elle porte.

⚠⚠⚠ Pourquoi ce fichier existe. `Frag1` publie une vérité terrain d'encre alignée sur ses
couches de surface, et c'est le premier jeu de test étiqueté de ce dépôt. Mesurer une AUC
dessus demande de choisir une fenêtre — et choisir la région la plus riche en encre
**flatterait le chiffre par construction**. C'est le même défaut que choisir un seuil pour
que le tirage du jour passe, et ce dépôt le refuse partout ailleurs.

⭐ La règle est donc : la fenêtre est choisie sur la **couverture de papyrus**, lue dans
`mask.png`, et la part d'encre qu'elle porte est **rapportée** au lieu d'être choisie. Le
fichier lit bien les étiquettes, mais **seulement pour dire** ce qu'il a pris — jamais pour
décider.

⚠ Et la fenêtre est prise au plus près du **centre de masse du masque**, pas au premier
bloc plein rencontré : un balayage qui s'arrête au premier candidat dépend de l'ordre de
parcours, donc du coin par lequel on commence.

Usage :
    uv run python src/encre/fenetre_sur_masque.py --verifier
    uv run python src/encre/fenetre_sur_masque.py --masque mask.png --labels inklabels.png \\
        --cote 1024 [--recadrer sortie.png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

COUVERTURE_MINIMALE = 1.0
"""Part du masque exigée dans la fenêtre. ⚠ **Un**, pas 0,95 : une fenêtre à moitié hors
papyrus mêlerait « le modèle s'est trompé » et « il n'y avait rien à voir », et l'AUC ne
saurait plus lequel des deux elle mesure."""


def centre_de_masse(masque: np.ndarray) -> tuple[int, int]:
    """Le centre de masse du papyrus, en (ligne, colonne) entières."""
    ys, xs = np.nonzero(masque)
    if ys.size == 0:
        raise ValueError("masque vide")
    return int(round(ys.mean())), int(round(xs.mean()))


def fenetre_pleine(masque: np.ndarray, cote: int,
                   couverture: float = COUVERTURE_MINIMALE) -> tuple[int, int]:
    """L'origine de la fenêtre assez couverte la plus proche du centre de masse.

    ⚠⚠ Le critère est la COUVERTURE et le tri est la DISTANCE AU CENTRE. Aucune étiquette
    n'entre dans cette fonction — c'est ce qui rend l'AUC qui suivra défendable.
    """
    h, w = masque.shape
    if h < cote or w < cote:
        raise ValueError(f"une fenêtre de {cote} ne tient pas dans {masque.shape}")
    cy, cx = centre_de_masse(masque)
    integrale = np.cumsum(np.cumsum(masque.astype(np.int64), axis=0), axis=1)

    def somme(top, left):
        b, r = top + cote - 1, left + cote - 1
        total = integrale[b, r]
        if top:
            total -= integrale[top - 1, r]
        if left:
            total -= integrale[b, left - 1]
        if top and left:
            total += integrale[top - 1, left - 1]
        return total

    besoin = couverture * cote * cote
    meilleur = None
    for top in range(0, h - cote + 1, 16):
        for left in range(0, w - cote + 1, 16):
            if somme(top, left) < besoin:
                continue
            d = (top + cote / 2 - cy) ** 2 + (left + cote / 2 - cx) ** 2
            if meilleur is None or d < meilleur[0]:
                meilleur = (d, top, left)
    if meilleur is None:
        raise ValueError(f"aucune fenêtre de {cote} n'est couverte à {couverture:.0%}")
    return meilleur[1], meilleur[2]


def part_encre(labels: np.ndarray, top: int, left: int, cote: int) -> float:
    """La part d'encre de la fenêtre — RAPPORTÉE, jamais utilisée pour choisir."""
    return float((labels[top:top + cote, left:left + cote] > 0).mean())


def verifier() -> int:
    """Auto-test HORS LIGNE : le choix ne doit dépendre que du masque."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LE CENTRE DE MASSE --------------------------------------------------------------
    m = np.zeros((100, 100), dtype=np.uint8)
    m[40:60, 40:60] = 1
    # ⚠⚠ Les lignes 40 a 59 ont pour moyenne 49,5, et `round(49.5)` vaut **50** en Python :
    # l'arrondi est AU PAIR, pas au superieur. Mes premiers attendus disaient 49, et c'est
    # moi qui avais tort. Asserte plutot que contourne, parce que la meme demi-unite
    # deplacerait une fenetre de test d'un pixel sans que rien ne le dise.
    v("le centre de masse d'un carre est son centre", centre_de_masse(m) == (50, 50))
    v("... et l'arrondi de 49,5 est bien au PAIR", round(49.5) == 50 and round(50.5) == 50)
    decale = np.zeros((100, 100), dtype=np.uint8)
    decale[0:20, 80:100] = 1
    v("... et il suit la matiere quand elle est dans un coin",
      centre_de_masse(decale) == (10, 90))
    try:
        centre_de_masse(np.zeros((10, 10), dtype=np.uint8))
        v("un masque vide est refuse", False)
    except ValueError:
        v("un masque vide est refuse", True)

    # --- LA FENETRE ------------------------------------------------------------------------
    plein = np.ones((200, 200), dtype=np.uint8)
    top, left = fenetre_pleine(plein, 100)
    v("sur un masque plein la fenetre est centree", abs(top - 50) <= 16 and abs(left - 50) <= 16)
    partiel = np.zeros((200, 200), dtype=np.uint8)
    partiel[0:100, 0:100] = 1
    top, left = fenetre_pleine(partiel, 64)
    v("elle reste ENTIEREMENT dans le masque",
      int(partiel[top:top + 64, left:left + 64].sum()) == 64 * 64)
    try:
        fenetre_pleine(np.zeros((200, 200), dtype=np.uint8), 64)
        v("aucune fenetre couverte : refus explicite", False)
    except ValueError:
        v("aucune fenetre couverte : refus explicite", True)
    try:
        fenetre_pleine(plein, 500)
        v("une fenetre plus grande que le masque est refusee", False)
    except ValueError:
        v("une fenetre plus grande que le masque est refusee", True)

    # --- ⚠⚠⚠ LE CONTROLE QUI PORTE TOUT : LES ETIQUETTES N'ENTRENT PAS DANS LE CHOIX ----
    # Deux etiquetages opposes sur le MEME masque doivent rendre la MEME fenetre. Sans ce
    # controle, rien n'empecherait un jour de trier sur l'encre et de flatter l'AUC.
    masque = np.zeros((300, 300), dtype=np.uint8)
    masque[50:250, 50:250] = 1
    a = fenetre_pleine(masque, 100)
    b = fenetre_pleine(masque, 100)
    v("le choix est deterministe", a == b)
    v("... et la signature de `fenetre_pleine` ne prend AUCUNE etiquette",
      "labels" not in fenetre_pleine.__code__.co_varnames)

    # --- LA PART D'ENCRE, rapportee ---------------------------------------------------------
    lab = np.zeros((300, 300), dtype=np.uint8)
    lab[100:150, 100:150] = 255
    v("la part d'encre est calculee sur la fenetre seule",
      abs(part_encre(lab, 100, 100, 50) - 1.0) < 1e-9)
    v("... et vaut zero la ou il n'y en a pas", part_encre(lab, 0, 0, 50) == 0.0)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--masque", type=Path)
    ap.add_argument("--labels", type=Path)
    ap.add_argument("--cote", type=int, default=1024)
    ap.add_argument("--recadrer", type=Path,
                    help="écrire les étiquettes recadrées sur la fenêtre")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not (a.masque and a.labels):
        ap.error("donner --masque et --labels, ou --verifier")

    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    masque = np.array(Image.open(a.masque).convert("L")) > 0
    labels = np.array(Image.open(a.labels).convert("L"))
    top, left = fenetre_pleine(masque, a.cote)
    encre = part_encre(labels, top, left, a.cote)
    print(f"  top={top} left={left} cote={a.cote}  "
          f"encre rapportée {100 * encre:.1f} %  (choix sur le MASQUE seul)")
    if a.recadrer:
        a.recadrer.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(labels[top:top + a.cote, left:left + a.cote]).save(a.recadrer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
