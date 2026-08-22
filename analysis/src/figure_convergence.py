#!/usr/bin/env python3
"""Deux surfaces, la meme mesure, des fenetres de plus en plus larges.

⚠⚠ **Ce que cette figure etablit.** Chaque point est la distance mesuree entre une surface
et la matiere la plus proche, dans une fenetre de rendu de N couches. Une surface qui suit
sa feuille a sa matiere tout pres : elargir la fenetre ne change rien, la courbe est PLATE.
Une surface posee en travers de l'empilement n'a aucun pic a trouver, donc le « pic » mesure
est le plus fort de ce que la fenetre contenait -- et il s'eloigne AVEC elle.

⭐ Les axes sont LOGARITHMIQUES tous les deux, et c'est ce qui rend le resultat lisible d'un
coup : une pente nulle est une convergence, une pente de 1 est une mesure qui suit son
propre reglage. La droite grise de pente 1 est tracee pour qu'on n'ait pas a l'estimer a
l'oeil.

⚠ Les deux surfaces sont sur le MEME rouleau, par la MEME chaine, avec le MEME instrument.
Sans cet appariement, un ecart entre deux courbes melangerait la surface et le reglage --
c'est l'erreur que ce depot a faite trois fois le 2026-08-20 avant d'arriver a cette figure.

⚠ Trace avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    cd inference && uv run python ../analysis/src/figure_convergence.py
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

LARGEUR, HAUTEUR = 940, 600
X0, X1, Y0, Y1 = 130, 780, 470, 110      # cadre du graphe

# ⚠ La table de traduction de cette figure. Les cles matchent le texte SOURCE.
ANGLAIS = {
    "Élargir la fenêtre : ce qui bouge, et ce qui ne bouge pas":
        "Widening the window: what moves, and what does not",
    "Distance mesurée à la matière la plus proche, en fonction de la profondeur ":
        "Measured distance to the nearest material, against the rendered ",
    "rendue. Axes logarithmiques.": "depth. Logarithmic axes.",
    "couches rendues (fenêtre)": "rendered layers (window)",
    "pente 1 : suit la fenêtre": "slope 1: follows the window",
    "segment officiel PHerc1447 (bonne surface)":
        "published PHerc1447 segment (good surface)",
    "notre trace PHerc1447 r2": "our own PHerc1447 trace, run 2",
    "— Pente nulle : la matière est là, tout près. La mesure ne dépend pas du ":
        "— Zero slope: the material is right there. The measurement does not depend on the ",
    "réglage — c'est une distance.": "setting — it is a distance.",
    "!! Pente 1 : le « pic » s'éloigne avec la fenêtre. Il n'y a aucune feuille à ":
        "!! Slope 1: the “peak” recedes with the window. There is no sheet within ",
    "portée — la surface est posée EN TRAVERS.":
        "reach — the surface lies ACROSS the stack.",
    "Même rouleau, même chaîne, même instrument. Aucun seuil, aucune vérité ":
        "Same scroll, same chain, same instrument. No threshold, no ground ",
    "terrain, aucune échelle : on compare une mesure à elle-même.":
        "truth, no scale: a measurement is compared to itself.",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--entree", type=Path, default=racine / "docs/convergence.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/38_convergence.png")
    ap.add_argument("--anglais", action="store_true",
                    help="écrire la figure en anglais (pour l'article)")
    a = ap.parse_args()
    anglais = a.anglais

    from PIL import Image, ImageDraw, ImageFont
    from langue import Traduisant

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer test_convergence.py --json", file=sys.stderr)
        return 1
    series = json.loads(a.entree.read_text())["series"]
    pts = [(n, e) for s in series for n, e in s["serie"]]
    nx = [n for n, _ in pts]
    ny = [e for _, e in pts if e > 0]
    lx0, lx1 = math.log10(min(nx) * 0.8), math.log10(max(nx) * 1.25)
    ly0, ly1 = math.log10(min(ny) * 0.6), math.log10(max(ny) * 1.6)

    def px(n): return X0 + int((math.log10(n) - lx0) / (lx1 - lx0) * (X1 - X0))
    def py(e): return Y0 + int((math.log10(e) - ly0) / (ly1 - ly0) * (Y1 - Y0))

    im = Image.new("RGB", (LARGEUR, HAUTEUR), (255, 255, 255))
    # ⭐ Tout ce qui s'ecrit passe par `.text` : envelopper suffit a traduire la figure.
    art = Traduisant(ImageDraw.Draw(im), ANGLAIS if anglais else None)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    art.text((14, 20), "Élargir la fenêtre : ce qui bouge, et ce qui ne bouge pas",
             fill=(20, 20, 20), font=f_t)
    art.text((14, 42),
             "Distance mesurée à la matière la plus proche, en fonction de la profondeur "
             "rendue. Axes logarithmiques.",
             fill=(110, 110, 110), font=f_n)

    art.rectangle([X0, Y1, X1, Y0], outline=(225, 225, 225))
    for n in (21, 31, 41, 81, 161):
        x = px(n)
        art.line([x, Y0, x, Y0 + 5], fill=(180, 180, 180))
        art.text((x - 10, Y0 + 9), str(n), fill=(120, 120, 120), font=f_p)
    art.text(((X0 + X1) // 2 - 74, Y0 + 30), "couches rendues (fenêtre)",
             fill=(120, 120, 120), font=f_p)
    for e in (20, 50, 100, 200, 500):
        if not (min(ny) * 0.6 <= e <= max(ny) * 1.6):
            continue
        y = py(e)
        art.line([X0 - 5, y, X0, y], fill=(180, 180, 180))
        art.text((X0 - 46, y - 7), f"{e} µm", fill=(120, 120, 120), font=f_p)

    # ⭐ La droite de pente 1 : « la mesure double quand la fenêtre double ».
    n_a, n_b = min(nx), max(nx)
    e_ref = min(ny) * 1.2
    art.line([px(n_a), py(e_ref), px(n_b), py(e_ref * n_b / n_a)], fill=(215, 215, 215))
    art.text((px(n_b) - 130, py(e_ref * n_b / n_a) - 18), "pente 1 : suit la fenêtre",
             fill=(170, 170, 170), font=f_p)

    # ⚠⚠ Une palette de TROIS couleurs pour SEPT series rend la legende inutilisable : le
    # lecteur ne peut pas relier une ligne a son nom, et une figure qu'on ne peut pas lire
    # ne prouve rien. Paye sur `43` (la chaine de spires).
    # ⚠⚠ La deuxieme version epinglait HUIT teintes en disant « le cycle ne recommence
    # qu'au-dela ». Il a recommence : une chaine de NEUF spires a donne a la spire 8
    # (α = +1,32, la pire) la couleur exacte de la spire 0 (le controle, α = 0) -- les deux
    # series les plus opposees de la figure, indistinguables. La palette est donc ENGENDREE
    # depuis le nombre de series : elle ne peut plus cycler, quel qu'il soit.
    import colorsys
    n_s = max(len(series), 1)
    couleurs = []
    for i in range(n_s):
        # Teintes reparties sur la roue ; la valeur alterne legerement pour que deux teintes
        # voisines se separent aussi en clarte et pas seulement en couleur.
        h = (i / n_s + 0.30) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.62, 0.58 + 0.10 * (i % 2))
        couleurs.append((int(r * 255), int(g * 255), int(b * 255)))

    # ⚠ Les etiquettes α se chevauchaient encore : un decalage par RANG suppose que deux
    # series de rangs eloignes finissent loin l'une de l'autre, ce qui est faux. On place
    # donc par y CROISSANT avec un ecart minimal impose -- une vraie de-collision.
    fins = sorted(range(len(series)), key=lambda i: py(sorted(series[i]["serie"])[-1][1]))
    y_etiquette, precedent = {}, None
    for i in fins:
        vise = py(sorted(series[i]["serie"])[-1][1]) - 7
        pose = vise if precedent is None else max(vise, precedent + 15)
        y_etiquette[i] = pose
        precedent = pose

    for i, s in enumerate(series):
        c = couleurs[i % len(couleurs)]
        serie = sorted(s["serie"])
        for (na, ea), (nb, eb) in zip(serie, serie[1:]):
            art.line([px(na), py(ea), px(nb), py(eb)], fill=c, width=3)
        for n, e in serie:
            art.ellipse([px(n) - 5, py(e) - 5, px(n) + 5, py(e) + 5], fill=c)
        nf, ef = serie[-1]
        art.text((px(nf) + 12, y_etiquette[i]), f"α = {s['alpha']:+.2f}", fill=c, font=f_n)
        art.text((14, 86 + i * 20), f"■ {s['nom']}", fill=c, font=f_n)

    bas = Y0 + 56
    art.text((14, bas),
             "— Pente nulle : la matière est là, tout près. La mesure ne dépend pas du "
             "réglage — c'est une distance.",
             fill=(60, 130, 90), font=f_n)
    art.text((14, bas + 20),
             "!! Pente 1 : le « pic » s'éloigne avec la fenêtre. Il n'y a aucune feuille à "
             "portée — la surface est posée EN TRAVERS.",
             fill=(190, 85, 40), font=f_n)
    art.text((14, bas + 44),
             "Même rouleau, même chaîne, même instrument. Aucun seuil, aucune vérité "
             "terrain, aucune échelle : on compare une mesure à elle-même.",
             fill=(120, 120, 120), font=f_p)

    # ⚠⚠ Une figure a moitie traduite a l'air traduite. On REFUSE de l'ecrire.
    if anglais and art.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for _t in art.intraduits():
            print(f"    « {_t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}x{HAUTEUR}, {len(series)} séries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
