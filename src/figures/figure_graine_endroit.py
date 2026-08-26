#!/usr/bin/env python3
"""Les deux graines du 2×2, sondées dans le volume scanné — et l'écart est de SEPT SPIRES.

⚠⚠ **Ce que cette figure établit.** [`54`](../../docs/54_cinq_rendus_vides.md) laisse la cause
« la graine, c'est-à-dire l'endroit » **ouverte** : le 2×2 croisé tenait un *nombre* constant
et non un *endroit*, donc il n'était pas en position de conclure. Six sondes le referment d'un
cran : la graine `ps256` désigne de la matière **dans les deux repères** dès qu'on la convertit
correctement, la graine `m7` n'en désigne **dans aucun**.

⭐ Et le chiffre qui compte n'est pas « oui / non » mais **à quelle distance** : ≈ 7 spires.
Ce n'est ni une erreur d'arrondi — qui se corrigerait par un calcul — ni le vide
interplanétaire. C'est un endroit qui rate la feuille de sept épaisseurs de papyrus.

⚠ L'unité est la **spire**, pas le micromètre, parce que c'est elle qui rend le nombre lisible :
l'espacement inter-spires médian du rouleau est de 173 µm (`16`). Un lecteur à qui l'on dit
« 1229 µm » ne sait pas si c'est beaucoup.

⚠ Les distances sont des **majorants** : la recherche s'arrête au premier bloc publié, et un
bloc fait 128 voxels de côté. « ≤ 7 spires » veut dire « au plus », jamais « exactement ».

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    ./src/campagnes/campagne_graines_endroit.sh
    uv run python src/figures/figure_graine_endroit.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR = 1020
FOND, ENCRE, GRIS = (255, 255, 255), (25, 25, 28), (150, 150, 155)
AMBRE, BLEU, PALE, ROUGE = (214, 141, 40), (44, 90, 160), (222, 226, 232), (168, 52, 44)

GLYPHES_ABSENTS = ("\u2b50", "\u2705", "\u274c")
"""Caractères que la police du dépôt (DejaVuSans) ne rend pas : ils sortent en carré vide, et
un carré dans une figure est du bruit qu'un lecteur prend pour une donnée. ⚠ Ils sont écrits en
séquences d'échappement, sinon ce fichier contiendrait précisément ce qu'il refuse."""

LEGENDE = (
    "ps256 désigne de la matière DANS LES DEUX REPÈRES ; m7 n'en désigne dans AUCUN.",
    "⚠ Ce n'est ni une erreur d'arrondi — qui se corrigerait par un calcul — ni le vide : "
    "c'est un endroit",
    "qui rate la feuille de sept épaisseurs de papyrus. Et lire une coordonnée dans le "
    "mauvais repère (en rouge) ne",
    "rend pas une erreur : ça rend un autre endroit, ou rien, avec le même aplomb.",
)
"""⚠⚠ La prose tracée est une DONNÉE, pas une chaîne perdue dans `main`. C'est ce qui rend le
contrôle de police capable de porter sur ce qui est réellement dessiné : les deux versions
précédentes cherchaient un motif dans le fichier source, et ce fichier contient le motif — le
contrôle se comptait lui-même et refusait sa propre docstring."""

ORDRE = [
    ("ps256_dans_son_repere", "ps256, son repère (niveau 0)", BLEU),
    ("ps256_converti_en_L2", "ps256, converti en niveau 2", BLEU),
    ("ps256_lu_en_L2_sans_conversion", "ps256 lu en niveau 2 SANS conversion", ROUGE),
    ("m7_dans_son_repere", "m7, son repère (niveau 2)", AMBRE),
    ("m7_converti_en_L0", "m7, converti en niveau 0", AMBRE),
    ("m7_lu_en_L0_sans_conversion", "m7 lu en niveau 0 SANS conversion", ROUGE),
]


def lire(rapport: dict) -> list[tuple[str, str, tuple, float | None, str]]:
    """Chaque sonde : son libellé, sa couleur, sa distance en spires, et son verdict en mots.

    ⚠ Une sonde absente du rapport n'est pas une distance nulle : elle est **absente**, et le
    dire est la différence entre « on a mesuré zéro » et « on n'a pas mesuré ».
    """
    sondes = rapport.get("sondes", {})
    out = []
    for cle, libelle, couleur in ORDRE:
        d = sondes.get(cle)
        if not d:
            out.append((libelle, couleur, None, "pas de mesure"))
        elif d.get("trouve"):
            sp = d.get("distance_spires_max")
            out.append((libelle, couleur, sp,
                        "matière au point" if d["distance_blocs"] == 0
                        else f"≤ {sp:.1f} spires"))
        else:
            out.append((libelle, couleur, None,
                        f"rien dans {d.get('rayon_regarde')} blocs"))
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    faux = {"espacement_um": 173.0, "sondes": {
        "ps256_dans_son_repere": {"trouve": True, "distance_blocs": 0, "distance_spires_max": 0.0},
        "m7_dans_son_repere": {"trouve": True, "distance_blocs": 1, "distance_spires_max": 7.1},
        "m7_converti_en_L0": {"trouve": False, "rayon_regarde": 8},
    }}
    L = lire(faux)
    v("les six sondes sont toujours listées", len(L) == 6)
    v("une distance nulle se dit « matière au point »", L[0][3] == "matière au point")
    v("une distance non nulle se dit en SPIRES", "spires" in L[3][3] and "7.1" in L[3][3])
    v("une sonde sans matière dit jusqu'où elle a regardé", "8 blocs" in L[4][3])
    # ⚠⚠ Une sonde ABSENTE n'est pas une distance nulle. Les confondre ferait lire « on a
    # mesuré zéro » là où il faut lire « on n'a pas mesuré » -- la panne que ce dépôt nomme.
    v("une sonde absente se dit « pas de mesure », pas zéro",
      L[1][3] == "pas de mesure" and L[1][2] is None)
    v("un rapport vide ne fait pas planter", len(lire({})) == 6)
    # ⚠⚠ La police du dépôt (DejaVuSans) n'a pas ⭐ : il rend un carré vide, et un carré dans
    # une figure est du bruit qu'un lecteur prend pour une donnée. ⚠ Le contrôle porte sur ce
    # qui est TRACÉ (`d.text`), pas sur le fichier : la première version attrapait le ⭐ de la
    # docstring, qui n'atteint jamais l'image — un contrôle qui refuse ce qu'il devrait laisser
    # passer finit par être neutralisé plutôt que corrigé.
    v("aucun caractère absent de la police n'est TRACÉ",
      not any(g in "".join(LEGENDE) for g in GLYPHES_ABSENTS))
    v("la légende tracée est bien une donnée, pas une chaîne perdue", len(LEGENDE) == 4)
    v("les couleurs distinguent les trois familles",
      len({c for _, c, _, _ in L}) == 3)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    racine = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path, default=racine / "docs/mesures/graines_endroit.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/54_graines_endroit.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer src/campagnes/campagne_graines_endroit.sh",
              file=sys.stderr)
        return 1
    rapport = json.loads(a.entree.read_text(encoding="utf-8"))
    L = lire(rapport)

    from PIL import Image, ImageDraw, ImageFont

    def police(t):
        for n in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(n, t)
            except OSError:
                continue
        return ImageFont.load_default()

    marge, tete, ligne = 380, 122, 50
    hauteur = tete + ligne * len(L) + 118
    im = Image.new("RGB", (LARGEUR, hauteur), FOND)
    d = ImageDraw.Draw(im)
    f_t, f_x, f_p = police(21), police(14), police(12)

    maxi = max([s for _, _, s, _ in L if s is not None] + [8.0])
    utile = LARGEUR - marge - 150
    par_spire = utile / maxi

    d.text((40, 26), "Où commence la matière scannée, sous chaque graine du 2×2",
           font=f_t, fill=ENCRE)
    d.text((40, 56), f"Unité : la spire — {rapport.get('espacement_um', 173):.0f} µm "
                     "d'espacement inter-spires. Les distances sont des MAJORANTS.",
           font=f_x, fill=GRIS)

    # L'axe, gradué en spires.
    y0 = tete - 18
    for s in range(0, int(maxi) + 1, 2):
        x = marge + s * par_spire
        d.line([x, y0, x, y0 + ligne * len(L) + 8], fill=(238, 240, 244), width=1)
        d.text((x - 4, y0 - 16), str(s), font=f_p, fill=GRIS)
    d.text((marge + utile / 2 - 30, y0 - 34), "spires", font=f_p, fill=GRIS)

    y = tete
    for libelle, couleur, spires, verdict in L:
        d.text((40, y + 8), libelle, font=f_x, fill=ENCRE)
        if spires is None:
            d.text((marge, y + 8), verdict, font=f_p, fill=ROUGE)
        elif spires == 0:
            d.ellipse([marge - 7, y + 8, marge + 7, y + 22], fill=couleur)
            d.text((marge + 16, y + 8), verdict, font=f_p, fill=couleur)
        else:
            d.rectangle([marge, y + 10, marge + spires * par_spire, y + 22], fill=couleur)
            d.text((marge + spires * par_spire + 10, y + 8), verdict, font=f_p, fill=couleur)
        y += ligne

    y += 16
    for i, l in enumerate(LEGENDE):
        d.text((40, y + 20 * i), l, font=f_x if i == 0 else f_p,
               fill=ENCRE if i == 0 else GRIS)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"{len(L)} sondes  →  {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
