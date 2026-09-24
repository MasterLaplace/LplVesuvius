"""Choisir une fenêtre sans regarder l'encre : par la seule couverture de papyrus.

⚠⚠ Choisir la fenêtre là où l'encre paraît la plus forte, puis la montrer comme preuve, serait sélectionner
sur le résultat : n'importe quel bruit y fabriquerait des lettres. La fenêtre et la région tenue à l'écart se
choisissent donc sur ce qui ne dépend pas de l'encre, la part de papyrus rendu, et la règle est écrite avant
de voir quoi que ce soit.
"""
from __future__ import annotations

import numpy as np


def _integrale(masque: np.ndarray) -> np.ndarray:
    return np.pad(np.cumsum(np.cumsum(masque.astype(np.int64), axis=0), axis=1), ((1, 0), (1, 0)))


def la_meilleure_fenetre(masque: np.ndarray, cote: int, pas: int = 16, interdite=None) -> dict | None:
    """La fenêtre carrée de `cote` pixels la plus couverte de papyrus, au pas de `pas` ; la première en
    lecture (haut, puis gauche) à égalité. `interdite` : une fenêtre que celle-ci ne doit pas chevaucher."""
    h, w = masque.shape
    if cote > h or cote > w:
        return None
    I = _integrale(masque)
    meilleure = None
    for r in range(0, h - cote + 1, pas):
        for c in range(0, w - cote + 1, pas):
            if interdite is not None:
                ir, ic, ih, iw = interdite["r0"], interdite["c0"], interdite["cote"], interdite["cote"]
                if r < ir + ih and ir < r + cote and c < ic + iw and ic < c + cote:
                    continue
            n = int(I[r + cote, c + cote] - I[r, c + cote] - I[r + cote, c] + I[r, c])
            if meilleure is None or n > meilleure["papyrus"]:
                meilleure = {"r0": r, "c0": c, "cote": cote, "papyrus": n}
    if meilleure is not None:
        meilleure["la_part_de_papyrus"] = round(meilleure["papyrus"] / (cote * cote), 4)
    return meilleure


def la_fenetre_tenue_a_lecart(masque: np.ndarray, cote: int, fenetre: dict, pas: int = 16) -> dict | None:
    """La meilleure fenêtre de même côté qui ne chevauche pas la première ; sinon la plus grande qui tienne,
    et c'est dit (`le_cote_reduit`)."""
    for c in range(cote, 63, -64):
        x = la_meilleure_fenetre(masque, c, pas, interdite=fenetre)
        if x is not None and x["la_part_de_papyrus"] >= 0.5:
            x["le_cote_reduit"] = c != cote
            return x
    return None
