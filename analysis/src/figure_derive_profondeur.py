#!/usr/bin/env python3
"""Ce qu'un critère mesure quand la plupart des traces butent sur le plafond du rendu.

⚠⚠ **Ce que la figure établit.** La bande du haut porte, pour chaque trace, sa distance à
la matière aux deux profondeurs de rendu, avec les **deux plafonds** tracés en traits pleins.
La question se lit d'un coup : combien de points sont posés SUR la ligne du plafond plutôt
qu'entre les lignes ? Un point au plafond ne rapporte pas la distance de la trace, il
rapporte le réglage — et le plafond double avec la profondeur.

⭐ La bande du bas porte un critère qui, lui, n'a pas de plafond : une fraction, bornée à
[0,1] par construction. Il montre l'autre moitié du problème — il **bouge quand même**, donc
un seuil absolu posé à une profondeur ne juge pas une trace rendue à une autre.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    cd inference && uv run python ../analysis/src/figure_derive_profondeur.py \\
        --json ../docs/derive_profondeur.json --docs ../docs \\
        --sortie ../docs/images/47_derive_profondeur.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ⚠⚠ DEUX PANNEAUX COTE A COTE, et ce n'est pas qu'une question de place. Empiles, les deux
# bandes faisaient 1178 px de haut : dans l'article la figure ne tenait plus sous son texte
# et laissait une demi-page blanche, ce qui se lit comme une page tronquee. Cote a cote,
# elles tiennent -- ET les deux criteres d'une meme trace se retrouvent sur la MEME ligne,
# donc on lit d'un coup qu'une trace collee a son plafond a gauche peut bouger beaucoup a
# droite. La contrainte de mise en page a produit une meilleure figure.
LARGEUR = 1120
X0, LARG = 190, 400          # panneau gauche : la distance
X1, LARG1 = 660, 300         # panneau droit : un critere sans plafond
MARGE = 40
LIGNE = 22

ANGLAIS = {
    "Un critère mesuré à une profondeur ne juge pas une trace rendue à une autre":
        "A criterion measured at one depth does not judge a trace rendered at another",
    "distance à la matière (µm) — ": "distance to matter (µm) — ",
    "plafond du rendu": "render ceiling",
    "au plafond : la valeur est le RÉGLAGE, pas la surface":
        "at the ceiling: the value is the SETTING, not the surface",
    "mesurée entre les deux plafonds": "measured between the two ceilings",
    "part au bord du profil (sans plafond)": "share at the profile edge (no ceiling)",
    "│ = le plafond de CETTE trace": "│ = the ceiling of THIS trace",
    " contre ": " against ",
    "rendu ": "depth ",
    " couches": " layers",
    "traces au plafond : ": "traces at the ceiling: ",
    " en bas, ": " at the shallow depth, ",
    " en haut": " at the deep one",
    "dérive médiane ": "median drift ",
    ", maximum ": ", maximum ",
    "⚠⚠ la question n'est pas « quelle référence » : un seuil absolu compare des plafonds":
        "⚠⚠ the question is not «which reference»: an absolute threshold compares ceilings",
    "un critère doit être lu à DEUX profondeurs, comme l'exposant α":
        "a criterion must be read at TWO depths, like the α exponent",
}

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (150, 150, 150)
BAS, HAUT = (120, 120, 120), (40, 110, 60)
ALERTE = (200, 45, 45)


def x_de(um: float, umax: float) -> int:
    """Position d'une distance sur l'axe linéaire, écrêtée au cadre.

    ⚠ Linéaire et non logarithmique, contrairement à l'axe des aires de `35` : la question
    ici est « ce point est-il SUR la ligne du plafond ? », donc c'est la distance au
    plafond qui doit être lisible, pas un rapport.
    """
    return X0 + int(min(max(um, 0.0), umax) / umax * LARG)


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ Les sondes sont derivees des bornes par RATIO, jamais ecrites en dur : ce depot a
    # deja paye deux fois d'avoir teste un axe hors de son propre domaine.
    umax = 200.0
    v("l'axe est croissant", x_de(0, umax) < x_de(umax / 2, umax) < x_de(umax, umax))
    v("... et linéaire : deux écarts égaux font deux largeurs égales",
      abs((x_de(umax / 2, umax) - x_de(0, umax))
          - (x_de(umax, umax) - x_de(umax / 2, umax))) <= 1)
    v("l'origine de l'axe est à gauche du cadre", x_de(0, umax) == X0)
    v("le maximum est au bord droit", x_de(umax, umax) == X0 + LARG)
    v("une valeur au-delà reste dans le cadre", x_de(umax * 10, umax) == X0 + LARG)
    v("... et une valeur négative aussi", x_de(-5.0, umax) == X0)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=Path("../docs/derive_profondeur.json"))
    ap.add_argument("--docs", type=Path, default=Path("../docs"))
    ap.add_argument("--sortie", type=Path,
                    default=Path("../docs/images/47_derive_profondeur.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import langue
    from derive_avec_profondeur import apparier, charger

    if not a.json.is_file():
        print(f"absent : {a.json} — lancer d'abord derive_avec_profondeur.py",
              file=sys.stderr)
        return 1
    d = json.loads(a.json.read_text(encoding="utf-8"))
    sweeps = charger(a.docs)
    pb, ph = d["profondeur_basse"], d["profondeur_haute"]
    if pb not in sweeps or ph not in sweeps:
        print(f"les balayages {pb} et {ph} ne sont pas dans {a.docs}", file=sys.stderr)
        return 1
    # ⚠⚠ Les paires viennent de l'appariement PAR IDENTITE du module de mesure, importe
    # plutot que reecrit. Deux implementations d'un meme appariement finissent par ne pas
    # s'accorder, et la figure montrerait alors d'autres couples que le tableau.
    paires = apparier(sweeps[pb], sweeps[ph])
    umax = max(d["plafond_haut_um"] * 1.08, 1.0)

    def police(t, gras=False):
        for c in (("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",) if gras
                  else ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",)):
            try:
                return ImageFont.truetype(c, t)
            except OSError:
                pass
        return ImageFont.load_default()

    f_t, f_n, f_p = police(22, True), police(15), police(12)
    hauteur = MARGE + 34 + 30 + LIGNE * len(paires) + 108 + 4 * 20 + MARGE
    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    g.text((MARGE, MARGE - 12),
           "Un critère mesuré à une profondeur ne juge pas une trace rendue à une autre",
           font=f_t, fill=TEXTE)
    y = MARGE + 34

    # ── bande 1 : la distance, et les deux plafonds ──────────────────────────────────
    g.text((MARGE, y), f"distance à la matière (µm) — rendu {pb} contre {ph} couches",
           font=f_n, fill=TEXTE)
    g.text((X1, y), "part au bord du profil (sans plafond)", font=f_n, fill=TEXTE)
    y0 = y + 28

    for um, coul in ((d["plafond_bas_um"], BAS), (d["plafond_haut_um"], HAUT)):
        xx = x_de(um, umax)
        g.text((xx - 10, y0 - 18), f"{um:.0f}".replace(".", ","), font=f_p, fill=coul)
    for t in (0.0, 0.5, 1.0):
        xx = X1 + int(t * LARG1)
        g.line([xx, y0 - 4, xx, y0 + LIGNE * len(paires) + 4], fill=(232, 232, 232))
        g.text((xx - 8, y0 + LIGNE * len(paires) + 6), f"{t:.1f}".replace(".", ","),
               font=f_p, fill=DOUX)

    for i, (x_, y_) in enumerate(paires):
        yy = y0 + i * LIGNE + LIGNE // 2
        g.text((MARGE, yy - 7), f"{x_['rouleau']} {x_['repetition']}", font=f_p, fill=TEXTE)
        # ── gauche : la distance, avec le plafond DE CETTE TRACE ────────────────────
        # ⚠⚠ Le plafond est tracé par trace. La cohorte mélange deux tailles de voxel, donc
        # deux plafonds : une ligne unique ferait passer les traces de l'autre voxel pour
        # des traces SOUS le plafond alors qu'elles sont exactement AU leur, et la moitié
        # de la censure disparaîtrait sans qu'aucun chiffre ne bouge.
        for ligne, coul in ((x_, BAS), (y_, HAUT)):
            if ligne.get("plafond_um") is not None:
                xp = x_de(float(ligne["plafond_um"]), umax)
                g.line([xp, yy - 8, xp, yy + 8], fill=coul, width=1)
            if ligne.get("ecart_um") is None:
                continue
            xx = x_de(float(ligne["ecart_um"]), umax)
            if ligne.get("censure"):
                # ⚠ Une valeur censurée est creuse : pleine, elle se lirait comme une
                # mesure, ce qu'elle n'est pas.
                g.ellipse([xx - 4, yy - 4, xx + 4, yy + 4], outline=ALERTE, width=2)
            else:
                g.ellipse([xx - 3, yy - 3, xx + 3, yy + 3], fill=coul)
        # ── droite : un critère sans plafond, sur la MÊME ligne ─────────────────────
        if x_.get("au_bord") is not None and y_.get("au_bord") is not None:
            xa = X1 + int(float(x_["au_bord"]) * LARG1)
            xb = X1 + int(float(y_["au_bord"]) * LARG1)
            g.line([xa, yy, xb, yy], fill=DOUX, width=2)
            g.ellipse([xa - 3, yy - 3, xa + 3, yy + 3], fill=BAS)
            g.ellipse([xb - 3, yy - 3, xb + 3, yy + 3], fill=HAUT)

    y = y0 + LIGNE * len(paires) + 26
    # ⚠⚠ LE CODE COULEUR ETAIT NULLE PART. Deux points par ligne, gris et vert, et rien ne
    # disait lequel est quelle profondeur -- donc la figure entiere etait illisible pour qui
    # ne l'a pas ecrite. Trouve en la regardant, pas en relisant le code.
    for i, (coul, lib) in enumerate(((BAS, f"rendu {pb} couches"),
                                     (HAUT, f"rendu {ph} couches"))):
        xx = MARGE + i * 160
        g.ellipse([xx, y + 1, xx + 8, y + 9], fill=coul)
        g.text((xx + 14, y - 2), lib, font=f_p, fill=coul)
    y += 20
    g.ellipse([MARGE, y, MARGE + 9, y + 9], outline=ALERTE, width=2)
    g.text((MARGE + 16, y - 2), "au plafond : la valeur est le RÉGLAGE, pas la surface",
           font=f_p, fill=ALERTE)
    # ⚠ La legende du trait vertical appartient au panneau GAUCHE, ou les traits sont --
    # posee a droite, elle designait des traits qui n'y sont pas.
    y += 18
    g.text((MARGE, y - 2), "│ = le plafond de CETTE trace", font=f_p, fill=DOUX)
    y += 24

    ab = next((x for x in d["derives"] if x["critere"] == "au_bord"), None)
    lignes = [f"traces au plafond : {d['censurees_en_bas']}/{d['lignes_en_bas']} en bas, "
              f"{d['censurees_en_haut']}/{d['lignes_en_haut']} en haut"]
    if ab and ab["derive_mediane"] is not None:
        lignes.append(f"dérive médiane {ab['derive_mediane']:.3f}".replace(".", ",")
                      + f", maximum {ab['derive_max']:.3f}".replace(".", ","))
    # ⚠ Pas de ⭐ ici : DejaVu n'a pas ce glyphe et PIL le rend en carré vide, ce qui donne
    # une figure qui a l'air cassée. Les « ⚠ », eux, existent dans la police.
    lignes += ["⚠⚠ la question n'est pas « quelle référence » : un seuil absolu compare "
               "des plafonds",
               "un critère doit être lu à DEUX profondeurs, comme l'exposant α"]
    for i, t in enumerate(lignes):
        g.text((MARGE, y + i * 20), t, font=f_n,
               fill=ALERTE if t.startswith("⚠⚠") else TEXTE)

    # ⚠⚠ Une figure à moitié traduite a l'air traduite. On REFUSE de l'écrire.
    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})  {len(paires)} traces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
