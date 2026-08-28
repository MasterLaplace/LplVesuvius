#!/usr/bin/env python3
"""Combien de fenêtres une carte de côté S porte-t-elle au réglage calibré ?

⚠⚠ Pourquoi ce fichier existe, et c'est une erreur à moi. La formule n'est PAS
`S / 8 / 256` : `typographie.par_fenetres` balaye `range(0, dim - taille // 2, taille)`,
donc elle accepte une dernière fenêtre qui dépasse à moitié. J'ai dimensionné l'expérience
décisive de `46` §3 bis sur la mauvaise formule et annoncé « ~2100 × 2100 » là où il faut
**~5200 × 5200** — un facteur deux et demi sur le côté, six sur la surface à rendre.

⭐ Le contrôle qui rend ce fichier fiable est le seul qui vaille : la formule doit retrouver
le compte MESURÉ sur une carte réelle. `20250703034159` fait 3620 × 5220 et a rendu
2 × 3 = 6 candidates dont 4 retenues, ce que la campagne du 2026-08-28 a imprimé.

⚠ Le compte rendu ici est celui des fenêtres CANDIDATES. Combien sont retenues dépend du
masque de papyrus (au moins 50 % de couverture), qui est une propriété de la carte et non de
sa taille — donc ce fichier borne par le haut, et le dit.

Usage :
    uv run python src/encre/fenetres_par_region.py --verifier
    uv run python src/encre/fenetres_par_region.py
"""

from __future__ import annotations

import sys

REDUCTION = 8
"""Facteur de réduction du réglage calibré sur Scroll 1."""

TAILLE = 256
"""Côté de la fenêtre d'analyse, en pixels de carte réduite."""


def positions(dim_reduite: int, taille: int = TAILLE) -> int:
    """Positions de balayage sur un côté réduit, telles que `par_fenetres` les énumère."""
    return len(range(0, dim_reduite - taille // 2, taille))


def fenetres_candidates(cote_natif: int, reduction: int = REDUCTION,
                        taille: int = TAILLE) -> int:
    """Fenêtres candidates d'une carte carrée de `cote_natif` pixels."""
    p = positions(cote_natif // reduction, taille)
    return p * p


def cote_minimal(fenetres_voulues: int, reduction: int = REDUCTION,
                 taille: int = TAILLE) -> int:
    """Le plus petit côté natif qui porte au moins `fenetres_voulues` candidates."""
    cote = reduction
    while fenetres_candidates(cote, reduction, taille) < fenetres_voulues:
        cote += reduction
    return cote


def fisher_unilateral(a: int, b: int, c: int, d: int) -> float:
    """Fisher unilatéral sur un tableau 2×2, dans la direction déclarée.

    ⚠ Recopié de `typographie.fisher_periodicite` sans son refus sous huit fenêtres : ici on
    veut justement savoir ce que le test rendrait AVANT d'avoir les fenêtres, donc la borne
    de puissance ne doit pas court-circuiter le calcul. Une batterie vérifie que les deux
    s'accordent là où les deux répondent.
    """
    from math import comb
    n, lignes, colonnes = a + b + c + d, a + b, a + c
    total = comb(n, colonnes)
    if total == 0:
        return 1.0
    return sum(comb(lignes, k) * comb(n - lignes, colonnes - k) / total
               for k in range(a, min(lignes, colonnes) + 1))


def fenetres_pour_discriminer(part: float, seuil: float = 0.05,
                              plafond: int = 64) -> int:
    """Combien de fenêtres il faut pour qu'un sujet à `part` périodique soit significatif.

    ⚠⚠ C'est la question qu'on doit poser AVANT de rendre, et que je n'ai pas posée. Le
    témoin négatif du 2026-08-28 a rendu **5** fenêtres ; il en fallait **6** pour que le
    test puisse seulement tirer sur un sujet au taux de nos propres cartes. L'expérience a
    donc manqué d'UNE fenêtre, et sa non-significativité n'établit rien.

    ⚠ Le contrôle du mélange est supposé rendre zéro périodique, ce qu'il a fait sur les six
    cartes mesurées à ce jour. Si un jour il n'en rendait plus zéro, ce calcul serait
    optimiste et il faudrait le refaire avec le taux observé.
    """
    for k in range(2, plafond + 1):
        a = round(part * k)
        if fisher_unilateral(a, k - a, 0, k) < seuil:
            return k
    return 0


def verifier() -> int:
    """Auto-test HORS LIGNE : la formule contre un compte réellement mesuré."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # ⭐ LE CONTROLE QUI COMPTE : la formule doit retrouver un compte MESURE, pas
    # s'accorder avec elle-meme.
    v("la carte 3620x5220 rend 2 x 3 candidates, comme la campagne l'a imprime",
      positions(3620 // 8) == 2 and positions(5220 // 8) == 3)
    v("... soit six candidates, dont quatre retenues par le masque",
      positions(3620 // 8) * positions(5220 // 8) == 6)
    # ⚠⚠ L'erreur exacte que ce fichier existe pour empecher.
    v("2100 px ne portent QU'UNE fenetre, pas huit", fenetres_candidates(2100) == 1)
    v("... et 5200 en portent neuf", fenetres_candidates(5200) == 9)
    v("le seuil pour huit fenetres depasse largement 2100", cote_minimal(8) > 2100)
    v("... et tient dans les couches du temoin negatif (5641 px)",
      cote_minimal(8) <= 5641)
    # ⚠ La derniere fenetre a le droit de depasser a moitie : c'est ce que la formule
    # naive rate, et c'est de la que vient le facteur deux et demi.
    # ⚠ A 384 la borne `dim - taille // 2` vaut exactement 256, donc `range` s'arrete
    # avant : il faut DEPASSER 384 pour gagner la seconde position. Ma premiere version
    # de ce controle prenait 384 et echouait — la formule avait raison, pas moi.
    v("a 384 la seconde position n'est PAS encore la", positions(384) == 1)
    v("une derniere fenetre qui depasse a moitie est comptee", positions(400) == 2)
    v("... la ou la formule naive n'en compterait qu'une", 400 // 256 == 1)
    v("un cote plus petit qu'une demi-fenetre n'en porte aucune",
      fenetres_candidates(8 * 100) == 0)
    v("le seuil croit avec le nombre de fenetres voulues",
      cote_minimal(16) > cote_minimal(8) > cote_minimal(1))

    # --- LA PUISSANCE, la question qu'il fallait poser AVANT de rendre -----------------
    # ⭐ Les deux valeurs mesurees le 2026-08-28, qui donnent son sens au reste.
    v("nos quatre cartes, 8 sur 12 contre 0 sur 12, sont significatives",
      abs(fisher_unilateral(8, 4, 0, 12) - 0.000673) < 1e-5)
    v("le temoin negatif, 1 sur 5 contre 0 sur 5, ne l'est pas",
      abs(fisher_unilateral(1, 4, 0, 5) - 0.5) < 1e-9)
    # ⚠⚠⚠ ET LE FAIT QUI DESARME LA CONCLUSION : a cinq fenetres, un temoin se comportant
    # EXACTEMENT comme nos cartes ne serait pas significatif non plus.
    v("a 5 fenetres, un sujet au taux de nos cartes rend p > 0,05",
      fisher_unilateral(3, 2, 0, 5) > 0.05)
    v("... et il en fallait SIX", fenetres_pour_discriminer(0.67) == 6)
    v("le temoin en a rendu cinq, donc une de moins qu'il n'en fallait",
      fenetres_pour_discriminer(0.67) == 6 and 5 < 6)
    # ⚠ Un sujet plus tranche demande moins de fenetres ; un sujet plus tiede en demande plus.
    v("un sujet a 100% demande moins de fenetres qu'un sujet a 67%",
      fenetres_pour_discriminer(1.0) <= fenetres_pour_discriminer(0.67))
    v("un sujet a 30% en demande davantage",
      fenetres_pour_discriminer(0.30) > fenetres_pour_discriminer(0.67))
    v("un sujet a 0% n'est jamais significatif dans cette direction",
      fenetres_pour_discriminer(0.0) == 0)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    if "--verifier" in sys.argv:
        return verifier()
    print(f"  réglage calibré : réduction {REDUCTION}, fenêtre {TAILLE}")
    print(f"  seuil pour 8 fenêtres : {cote_minimal(8)} px de côté\n")
    print("  natif   réduit   positions/côté   fenêtres")
    for s in (1100, 2100, 3620, 4100, 5200, 5641, 6144):
        p = positions(s // REDUCTION)
        print(f"  {s:5d}   {s // REDUCTION:6d}   {p:12d}   {p * p:8d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
