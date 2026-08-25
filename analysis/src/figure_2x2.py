#!/usr/bin/env python3
"""Le 2×2 croisé : chaque tirage, la bande de bruit, et ce qui ne se plote pas.

⚠⚠ **Ce que la figure établit.** Quatre cellules — deux prédictions × deux graines — et
plusieurs tirages par cellule, parce que le traceur *est* un tirage. Un écart entre cellules
plus petit que la dispersion à l'intérieur d'une cellule ne dit rien, et la bande grise le
montre au lieu de le faire calculer.

⚠⚠ **Une cellule indécidable n'a PAS d'α**, donc elle n'a pas de place sur l'axe. La porter
à zéro, ou l'omettre en silence, sont deux façons de mentir : elle est comptée à part, en
marge. C'est la même règle que l'instrument applique — « je n'ai rien mesuré » n'est pas une
valeur.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python analysis/src/figure_2x2.py \\
        --json docs/paris4_2x2.json --sortie docs/images/48_2x2.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR = 1040
MARGE = 60
LIGNE = 74
A_MIN, A_MAX = -0.1, 1.6

ANGLAIS = {
    "Deux prédictions, deux graines, plusieurs tirages":
        "Two predictions, two seeds, several draws",
    "prédiction ": "prediction ",
    " · graine de ": " · seed of ",
    "exposant α": "α exponent",
    "indécidable": "undecidable",
    " tirage(s)": " draw(s)",
    "bande de bruit : ": "noise band: ",
    "l'écart entre prédictions vaut ": "the gap between predictions is ",
    ", le bruit ": ", the noise ",
    "profil plat — pas d'α à placer": "flat profile — no α to place",
}

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (150, 150, 150)
POINT, BANDE, PLAT = (60, 110, 170), (240, 240, 240), (200, 45, 45)


def x_de(a: float, x0: int, larg: int) -> int:
    """Position d'un α sur l'axe, écrêtée au cadre.

    ⚠ `round` et non `int` : la troncature biaise chaque position d'un pixel vers la gauche,
    et le milieu exact de l'axe y tombe du mauvais côté quand la division ne se ferme pas en
    binaire — mesuré, 0,85/1,7 vaut 0,4999… donc `int` rendait 299 au lieu de 300. Placer un
    point sur un axe est un arrondi ; le témoin de linéarité le dit, à un pixel près.
    """
    return x0 + round((min(max(a, A_MIN), A_MAX) - A_MIN) / (A_MAX - A_MIN) * larg)


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("l'axe est croissant", x_de(0.0, 100, 600) < x_de(0.8, 100, 600) < x_de(1.5, 100, 600))
    v("... et linéaire",
      abs((x_de(0.75, 100, 600) - x_de(A_MIN, 100, 600))
          - (x_de(A_MAX, 100, 600) - x_de(0.75, 100, 600))) <= 1)
    v("le minimum touche l'origine", x_de(A_MIN, 100, 600) == 100)
    v("le maximum touche le bord", x_de(A_MAX, 100, 600) == 700)
    v("une valeur hors bornes reste dans le cadre",
      100 <= x_de(-9.0, 100, 600) <= 700 and 100 <= x_de(9.0, 100, 600) <= 700)
    # ⚠ Deux α distincts a deux endroits distincts, sinon la figure ne separe rien.
    v("deux α distincts sont séparés", x_de(0.94, 100, 600) != x_de(1.09, 100, 600))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=Path("../docs/paris4_2x2.json"))
    ap.add_argument("--sortie", type=Path, default=Path("../docs/images/48_2x2.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import langue

    if not a.json.is_file():
        print(f"absent : {a.json} — lancer d'abord comparer_predictions.py", file=sys.stderr)
        return 1
    d = json.loads(a.json.read_text(encoding="utf-8"))
    cases = d.get("cases") or []
    if not cases:
        print("aucune cellule dans le JSON", file=sys.stderr)
        return 1
    bruit = d.get("bruit_retenu") or 0.2

    def police(t, gras=False):
        c = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if gras
             else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        try:
            return ImageFont.truetype(c, t)
        except OSError:
            return ImageFont.load_default()

    f_t, f_n, f_p = police(21, True), police(14), police(12)
    hauteur = MARGE + 40 + LIGNE * len(cases) + 40 + 3 * 20 + MARGE
    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    g.text((MARGE, MARGE - 26), "Deux prédictions, deux graines, plusieurs tirages",
           font=f_t, fill=TEXTE)
    x0, larg = MARGE + 250, LARGEUR - MARGE - 250 - 290
    y = MARGE + 26

    # ⚠⚠ La bande de bruit est centrée sur la MÉDIANE GLOBALE des α mesurés, et sa
    # demi-largeur est le bruit retenu. Elle ne dit pas « la vérité est là » — elle dit
    # « tout ce qui tombe là-dedans est indistinguable ».
    mesures = [x for t in cases for x in (t.get("alphas") or [])]
    if mesures:
        centre = sorted(mesures)[len(mesures) // 2]
        g.rectangle([x_de(centre - bruit / 2, x0, larg), y - 6,
                     x_de(centre + bruit / 2, x0, larg), y + LIGNE * len(cases) - 10],
                    fill=BANDE)

    for t in (0.0, 0.5, 1.0, 1.5):
        xx = x_de(t, x0, larg)
        g.line([xx, y - 6, xx, y + LIGNE * len(cases) - 10], fill=(225, 225, 225))
        g.text((xx - 10, y + LIGNE * len(cases) - 4), f"{t:.1f}".replace(".", ","),
               font=f_p, fill=DOUX)

    for i, t in enumerate(cases):
        yy = y + i * LIGNE + LIGNE // 2 - 10
        g.text((MARGE, yy - 14), f"prédiction {t['prediction']}", font=f_n, fill=TEXTE)
        g.text((MARGE, yy + 4), f" · graine de {t['graine']}", font=f_p, fill=DOUX)
        alphas = t.get("alphas") or []
        for A in alphas:
            xx = x_de(A, x0, larg)
            g.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], fill=POINT)
        if t.get("alpha_median") is not None:
            xm = x_de(t["alpha_median"], x0, larg)
            g.line([xm, yy - 14, xm, yy + 14], fill=(30, 60, 110), width=2)
        # ⚠ Les indecidables sont hors axe, a droite, et comptees : les mettre a zero ou les
        # omettre sont deux facons de mentir.
        if t.get("indecidables"):
            g.text((x0 + larg + 16, yy - 7),
                   f"{t['indecidables']} indécidable", font=f_p, fill=PLAT)
            g.text((x0 + larg + 16, yy + 7), "profil plat — pas d'α à placer",
                   font=f_p, fill=DOUX)
        elif alphas:
            g.text((x0 + larg + 16, yy - 7), f"{len(alphas)} tirage(s)", font=f_p, fill=DOUX)

    y += LIGNE * len(cases) + 24
    g.text((MARGE, y), "exposant α", font=f_n, fill=TEXTE)
    g.rectangle([MARGE + 110, y + 2, MARGE + 128, y + 14], fill=BANDE)
    g.text((MARGE + 134, y), f"bande de bruit : {bruit:.2f}".replace(".", ","),
           font=f_p, fill=DOUX)
    e = (d.get("effet_prediction") or {}).get("max")
    if e is not None:
        g.text((MARGE, y + 22),
               f"l'écart entre prédictions vaut {e:.2f}".replace(".", ",")
               + f", le bruit {bruit:.2f}".replace(".", ","),
               font=f_n, fill=TEXTE if e >= bruit else PLAT)

    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})  {len(cases)} cellules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
