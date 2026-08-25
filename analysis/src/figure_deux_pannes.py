#!/usr/bin/env python3
"""α mesuré contre α de plafond : là où le verdict cesse de distinguer deux pannes.

⚠⚠ **Ce que la figure établit.** Un profil plat n'a pas de pic, donc l'écart rapporté est le
**bord de la fenêtre** — et le rapport de deux bords vaut le rapport des fenêtres, donc
α ≈ 1 **par identité arithmétique**. Chaque série est placée sur son α **mesuré** contre l'α
qu'elle aurait si chaque lecture était son propre bord. Une série posée **sur la diagonale**
est une série dont α ne peut pas dire s'il y avait un pic.

⭐ Et la moitié rassurante se voit d'un coup : l'α de plafond vaut toujours ~1, donc les
séries qui **convergent** sont dans le coin bas-gauche, à une demi-largeur de figure de la
diagonale. **Aucun verdict positif n'est concerné**, et ça se lit sans lire un chiffre.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python analysis/src/figure_deux_pannes.py \\
        --json docs/audit_profils.json --sortie docs/images/49_deux_pannes.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, HAUTEUR = 1000, 660
MARGE = 70
# ⚠ Le cadre du nuage s'arrête au-dessus du bandeau de légende : sans cette
# réserve, les points et les étiquettes d'axe se posent sur le texte.
BAS = 150
A_MIN, A_MAX = -0.2, 1.6

ANGLAIS = {
    "Là où α cesse de distinguer deux pannes":
        "Where α stops telling two failures apart",
    "α mesuré": "measured α",
    "α si chaque lecture était le bord de sa fenêtre":
        "α if every reading were its own window edge",
    "une série ici ne peut pas dire s'il y avait un pic":
        "a series here cannot say whether there was a peak",
    "indiscernable du plafond": "indistinguishable from the ceiling",
    "discriminante": "discriminating",
    "converge": "converges",
    "séries jugées": "series judged",
    "bande d'indiscernabilité, largeur = la résolution déclarée de α":
        "indistinguishability band, width = α's declared resolution",
    " sur ": " of ",
    " séries indiscernables, ": " series indistinguishable, ",
    "0 parmi celles qui convergent": "0 among those that converge",
}

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (150, 150, 150)
LOIN, PRES, CONVERGE = (60, 110, 170), (200, 45, 45), (40, 110, 60)
BANDE = (250, 232, 232)


def place(a: float, lo: float, hi: float, taille: int, marge: int) -> int:
    """Une valeur d'α sur un axe, écrêtée au cadre."""
    v = min(max(a, lo), hi)
    return marge + int((v - lo) / (hi - lo) * (taille - 2 * marge))


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("l'axe est croissant",
      place(0.0, 0, 2, 400, 40) < place(1.0, 0, 2, 400, 40) < place(2.0, 0, 2, 400, 40))
    v("... et linéaire",
      abs((place(1.0, 0, 2, 400, 40) - place(0.0, 0, 2, 400, 40))
          - (place(2.0, 0, 2, 400, 40) - place(1.0, 0, 2, 400, 40))) <= 1)
    v("le minimum touche la marge", place(0.0, 0, 2, 400, 40) == 40)
    v("le maximum touche l'autre marge", place(2.0, 0, 2, 400, 40) == 360)
    v("une valeur sous la borne reste dans le cadre", place(-9.0, 0, 2, 400, 40) == 40)
    v("... et au-dessus aussi", place(9.0, 0, 2, 400, 40) == 360)
    # ⚠ Deux valeurs distinctes doivent donner deux positions distinctes, sinon la figure
    # n'a aucun pouvoir de separation -- c'est le controle que les bornes seules ne font pas.
    v("deux α distincts sont à deux endroits distincts",
      place(0.42, A_MIN, A_MAX, 800, 70) != place(0.87, A_MIN, A_MAX, 800, 70))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=Path("../docs/audit_profils.json"))
    ap.add_argument("--sortie", type=Path, default=Path("../docs/images/49_deux_pannes.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import langue

    if not a.json.is_file():
        print(f"absent : {a.json} — lancer d'abord audit_profils_plats.py", file=sys.stderr)
        return 1
    d = json.loads(a.json.read_text(encoding="utf-8"))
    juges = d.get("jugees") or {}
    if not juges:
        print("aucune série jugée dans le JSON — relancer l'audit", file=sys.stderr)
        return 1
    res = d.get("resolution_alpha") or 0.2
    ind = set(d.get("series_indiscernables_du_plafond") or {})

    def police(t, gras=False):
        c = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if gras
             else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        try:
            return ImageFont.truetype(c, t)
        except OSError:
            return ImageFont.load_default()

    f_t, f_n, f_p = police(21, True), police(14), police(12)
    img = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    def X(v):
        return place(v, A_MIN, A_MAX, LARGEUR, MARGE + 40)

    def Y(v):
        return (HAUTEUR - BAS) - place(v, A_MIN, A_MAX, HAUTEUR - BAS, MARGE) + MARGE

    # ⚠⚠ La BANDE d'indiscernabilité est dessinée AVANT les points, et sa largeur est la
    # résolution déclarée — pas un choix d'affichage. Un lecteur voit ainsi que « proche de
    # la diagonale » a une largeur définie, au lieu de la juger à l'œil.
    poly = [(X(A_MIN), Y(A_MIN - res)), (X(A_MAX), Y(A_MAX - res)),
            (X(A_MAX), Y(A_MAX + res)), (X(A_MIN), Y(A_MIN + res))]
    g.polygon(poly, fill=BANDE)
    g.line([X(A_MIN), Y(A_MIN), X(A_MAX), Y(A_MAX)], fill=(220, 150, 150), width=1)

    for t in (0.0, 0.5, 1.0, 1.5):
        g.line([X(t), Y(A_MIN), X(t), Y(A_MAX)], fill=(238, 238, 238))
        g.line([X(A_MIN), Y(t), X(A_MAX), Y(t)], fill=(238, 238, 238))
        g.text((X(t) - 10, Y(A_MIN) + 8), f"{t:.1f}".replace(".", ","), font=f_p, fill=DOUX)
        g.text((X(A_MIN) - 34, Y(t) - 7), f"{t:.1f}".replace(".", ","), font=f_p, fill=DOUX)

    n_conv = 0
    for nom, j in sorted(juges.items()):
        am, ap_ = j.get("alpha_mesure"), j.get("alpha_si_tout_au_plafond")
        if am is None or ap_ is None:
            continue
        if am < 0.5:
            coul, n_conv = CONVERGE, n_conv + 1
        elif nom in ind:
            coul = PRES
        else:
            coul = LOIN
        g.ellipse([X(am) - 4, Y(ap_) - 4, X(am) + 4, Y(ap_) + 4], fill=coul)

    g.text((MARGE, 22), "Là où α cesse de distinguer deux pannes", font=f_t, fill=TEXTE)
    g.text((MARGE - 30, 52), "α si chaque lecture était le bord de sa fenêtre",
           font=f_n, fill=TEXTE)
    g.text((LARGEUR - 220, Y(A_MIN) + 26), "α mesuré", font=f_n, fill=TEXTE)

    # ── le bandeau, sous le cadre et jamais dessus ──────────────────────────────────
    y = Y(A_MIN) + 52
    x = MARGE
    # ⚠ L'espacement suit la LARGEUR RÉELLE du libellé traduit, pas un pas fixe : l'anglais
    # est plus long que le français, et un pas de 210 px suffisait à l'un et faisait
    # chevaucher l'autre. Une mise en page calée sur une seule langue casse dans la seconde.
    dessin = ImageDraw.Draw(img)
    for coul, lib in ((CONVERGE, "converge"), (PRES, "indiscernable du plafond"),
                      (LOIN, "discriminante")):
        g.ellipse([x, y + 3, x + 8, y + 11], fill=coul)
        g.text((x + 14, y), lib, font=f_p, fill=coul)
        trad = lib if not a.anglais else ANGLAIS.get(lib, lib)
        x += 14 + int(dessin.textlength(trad, font=f_p)) + 40
    g.rectangle([MARGE, y + 24, MARGE + 8, y + 32], fill=BANDE, outline=(220, 150, 150))
    g.text((MARGE + 14, y + 22),
           "bande d'indiscernabilité, largeur = la résolution déclarée de α",
           font=f_p, fill=DOUX)
    g.text((MARGE, y + 46),
           f"{len(ind)} sur {len(juges)} séries indiscernables, "
           f"0 parmi celles qui convergent", font=f_n, fill=PRES)
    g.text((MARGE, y + 66),
           "une série ici ne peut pas dire s'il y avait un pic", font=f_p, fill=DOUX)

    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{HAUTEUR})  {len(juges)} séries, "
          f"{n_conv} convergentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
