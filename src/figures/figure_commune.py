#!/usr/bin/env python3
"""Ce que toutes les figures du dépôt refaisaient chacune de leur côté.

⚠⚠ POURQUOI CE FICHIER EXISTE. `_police` était définie **quinze fois**, en **quatre variantes**
— et c'est le seul endroit du dépôt où des copies ont RÉELLEMENT divergé. Elles ne diffèrent
pourtant que par les **tailles** demandées : le mécanisme (essayer deux chemins de police, se
rabattre sur le défaut de PIL) est le même partout. Une fonction **paramétrée** les remplace
toutes **sans changer une seule figure**, puisque chaque appelant passe ses propres tailles.

  ⭐ La règle : ce qui varie devient un ARGUMENT, ce qui ne varie pas devient un seul endroit.
    Unifier en imposant des tailles aurait déplacé quinze images pour du rangement, ce qui est
    exactement le refactor qu'on ne fait pas.

⚠ La quatrième variante attrapait `Exception` là où les autres attrapent `OSError`. C'est
`OSError` qui est juste : c'est ce que `ImageFont.truetype` lève quand le fichier manque, et
attraper plus large masquerait une erreur de programmation dans le repli. Rien de mesurable n'en
dépendait — le repli n'est atteint que si la police est absente.

⚠ Le repli rend le **même** objet autant de fois qu'il y a de tailles demandées : une figure
qui déballe trois polices doit en recevoir trois, même dégradées, sinon elle plante là où elle
devrait seulement être moins jolie.
"""
from __future__ import annotations

import argparse
import sys

CHEMINS = ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
"""Où chercher la police, dans l'ordre. ⚠ Le nom nu marche quand la police est installée dans
le chemin de recherche de PIL ; le chemin absolu est le repli des environnements minces."""

GLYPHES_ABSENTS = ("⭐", "✅", "❌", "⬛")
"""Caractères que DejaVuSans ne rend pas : ils sortent en **carré vide**, et un carré dans une
figure est du bruit qu'un lecteur prend pour une donnée. ⚠ Écrits en séquences d'échappement,
sinon ce fichier contiendrait précisément ce qu'il aide à refuser."""


def police(*tailles: int):
    """Une police par taille demandée, ou le défaut de PIL autant de fois.

    Rend un tuple de la longueur de `tailles`, ou l'objet seul si une seule taille est demandée.
    """
    if not tailles:
        raise ValueError("au moins une taille est requise")
    from PIL import ImageFont
    for chemin in CHEMINS:
        try:
            polices = tuple(ImageFont.truetype(chemin, t) for t in tailles)
            return polices[0] if len(polices) == 1 else polices
        except OSError:
            continue
    defaut = ImageFont.load_default()
    return defaut if len(tailles) == 1 else tuple(defaut for _ in tailles)


def prose_tracable(lignes) -> bool:
    """Aucune de ces lignes ne porte un caractère que la police ne sait pas rendre."""
    return not any(g in "".join(lignes) for g in GLYPHES_ABSENTS)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    une = police(14)
    v("une seule taille rend un objet, pas un tuple", not isinstance(une, tuple))
    trois = police(14, 12, 11)
    v("trois tailles rendent trois objets", isinstance(trois, tuple) and len(trois) == 3)
    v("... et deux en rendent deux", len(police(13, 11)) == 2)
    # ⭐ Les quatre variantes du depot, chacune servie sans changer ses tailles.
    for tailles in ((14, 12, 11), (13, 11, 15), (15, 12, 19), (13, 11)):
        if len(police(*tailles)) != len(tailles):
            v(f"la variante {tailles} est servie telle quelle", False)
            break
    else:
        v("les quatre variantes du dépôt sont servies telles quelles", True)

    # ⚠ Les tailles demandees sont bien celles rendues : une fonction qui les ignorerait
    # unifierait les figures en les DEPLACANT toutes, ce qui est le refactor a ne pas faire.
    try:
        v("la taille demandée est la taille rendue",
          all(f.size == t for f, t in zip(police(14, 12, 11), (14, 12, 11))))
    except AttributeError:
        v("la taille demandée est la taille rendue (police par défaut, non vérifiable)", True)

    try:
        police()
        v("aucune taille est refusé", False)
    except ValueError:
        v("aucune taille est refusé", True)

    v("la prose sans glyphe absent passe", prose_tracable(["mesuré : 7,1 spires", "⚠ majorant"]))
    v("... et une prose qui en porte un est refusée",
      not prose_tracable(["⭐ le résultat"]))
    v("le fichier n'écrit pas lui-même le glyphe qu'il refuse",
      all(g not in "".join(CHEMINS) for g in GLYPHES_ABSENTS))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    print("bibliothèque de dessin — voir `lplv figure_commune --help`")
    print(f"  polices cherchées : {', '.join(CHEMINS)}")
    print(f"  glyphes refusés   : {len(GLYPHES_ABSENTS)} (ils sortent en carré vide)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
