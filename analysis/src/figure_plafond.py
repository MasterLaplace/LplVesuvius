#!/usr/bin/env python3
"""Deux campagnes, deux plafonds : ce que la troncature cachait.

⚠⚠ **Ce que la figure établit.** [`35`](../docs/35_le_tirage_sur_douze_rouleaux.md) mesure
une dispersion d'aire de 0,5 % chez les rouleaux dont les six tirages butent sur le plafond
de générations, contre 19,9 % chez les autres. Deux lectures s'opposaient : ces rouleaux
sont-ils **réellement stables**, ou leur dispersion est-elle **écrasée par une troncature
commune** ? Six traces coupées au même endroit ont forcément la même aire.

⭐ Chaque rouleau porte **deux lignes** : ses six tirages au plafond d'origine, ses six
tirages au plafond relevé. Un point par tirage, **rouge s'il s'auto-intersecte**. La
question se lit d'un coup — la ligne du bas est-elle plus étalée que celle du haut ?

⚠ L'axe des aires est **logarithmique** : la question couvre un facteur dix, et une échelle
linéaire écraserait la ligne d'origine contre son bord gauche, ce qui la ferait passer pour
un point alors que c'est précisément sa largeur qu'on veut comparer.

⚠⚠ Les croisements sont montrés PARCE QUE la dispersion ne suffit pas à lire le résultat :
sur `PHerc0125` la propreté aussi était une troncature — un tirage sale sur six au plafond
d'origine, cinq sur six une fois relevé. Une figure qui ne montrerait que l'aire laisserait
croire que seul l'étalement change.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    cd inference && uv run python ../analysis/src/figure_plafond.py \\
        --origine ../docs/table_tirages.json --releve ../docs/table_tirages_plafond.json \\
        --sortie ../docs/images/35_plafond.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

LARGEUR = 1120
X0, LARG = 210, 700          # origine et largeur de l'axe des aires
BLOC = 62                    # hauteur d'un rouleau (deux lignes)
CM2_MIN, CM2_MAX = 8.0, 300.0

FOND, TEXTE = (255, 255, 255), (25, 25, 25)
PROPRE, SALE = (60, 110, 170), (200, 45, 45)
AVANT, APRES = (150, 150, 150), (40, 110, 60)


def x_de(cm2: float) -> int:
    """Position d'une aire sur l'axe logarithmique, écrêtée aux bornes."""
    v = min(max(cm2, CM2_MIN), CM2_MAX)
    return X0 + int(math.log10(v / CM2_MIN) / math.log10(CM2_MAX / CM2_MIN) * LARG)


def apparier(origine: dict, releve: dict) -> list[tuple[dict, dict]]:
    """Les rouleaux tracés des DEUX côtés, dans l'ordre du plafond relevé.

    ⚠ Un rouleau tracé d'un seul côté n'a pas de comparaison à montrer : le dessiner
    avec une ligne manquante se lirait comme « ce rouleau n'a rien donné », ce qui est
    faux et pire que de ne pas le dessiner.
    """
    par_nom = {l["rouleau"]: l for l in origine.get("lignes", [])}
    return [(par_nom[l["rouleau"]], l) for l in releve.get("lignes", [])
            if l["rouleau"] in par_nom]


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ Les sondes sont derivees des bornes PAR RATIO GEOMETRIQUE, donc elles tiennent
    # dans le domaine quelle que soit son etendue. Une version anterieure testait la decade
    # `MIN`, `MIN*10`, `MIN*100` -- correct sur un axe qui couvre plus de deux decades,
    # faux sinon : la troisieme sonde sortait du domaine et le temoin mesurait un ECRETAGE
    # en croyant mesurer une echelle. C'est la deuxieme fois que ce piege se paie.
    k = (CM2_MAX / CM2_MIN) ** 0.5
    d1, d2, d3 = CM2_MIN, CM2_MIN * k, CM2_MAX
    v("l'axe est croissant", x_de(d1) < x_de(d2) < x_de(d3))
    v("... et logarithmique : un même rapport fait toujours la même largeur",
      abs((x_de(d2) - x_de(d1)) - (x_de(d3) - x_de(d2))) <= 1,
      f"{x_de(d2) - x_de(d1)} contre {x_de(d3) - x_de(d2)}")
    v("une aire sous la borne reste dans le cadre", X0 <= x_de(0.01) <= X0 + LARG)
    v("... et une aire au-dessus aussi", X0 <= x_de(99999.0) <= X0 + LARG)

    o = {"lignes": [{"rouleau": "A"}, {"rouleau": "B"}]}
    r = {"lignes": [{"rouleau": "B"}, {"rouleau": "SEUL"}]}
    paires = apparier(o, r)
    v("seuls les rouleaux tracés des deux côtés sont appariés",
      [b["rouleau"] for _, b in paires] == ["B"], str([b["rouleau"] for _, b in paires]))
    v("... et l'ordre suit la campagne relevée",
      apparier({"lignes": [{"rouleau": "A"}, {"rouleau": "B"}]},
               {"lignes": [{"rouleau": "B"}, {"rouleau": "A"}]})[0][1]["rouleau"] == "B")
    v("deux campagnes sans recouvrement n'apparient rien",
      apparier({"lignes": [{"rouleau": "A"}]}, {"lignes": [{"rouleau": "Z"}]}) == [])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--origine", type=Path, default=racine / "docs/table_tirages.json")
    ap.add_argument("--releve", type=Path,
                    default=racine / "docs/table_tirages_plafond.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/35_plafond.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont

    for f in (a.origine, a.releve):
        if not f.is_file():
            print(f"absent : {f} — lancer d'abord table_tirages.py --json", file=sys.stderr)
            return 1
    o, r = json.loads(a.origine.read_text()), json.loads(a.releve.read_text())
    paires = apparier(o, r)
    if not paires:
        print("aucun rouleau tracé des deux côtés", file=sys.stderr)
        return 1

    hauteur = 130 + len(paires) * BLOC + 110
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = ImageDraw.Draw(img)
    g.text((40, 26), f"Le même rouleau, le même appel — seul le budget de générations change",
           font=f_t, fill=TEXTE)
    g.text((40, 50), f"un point = un tirage ; rouge = la trace s'auto-intersecte ; "
                     f"{o.get('budget_generations')} contre "
                     f"{r.get('budget_generations')} générations",
           font=f_p, fill=(90, 90, 90))

    y0 = 96
    for cm2 in (10, 30, 100, 300):
        x = x_de(cm2)
        g.line([x, y0 - 6, x, y0 + len(paires) * BLOC - 16], fill=(234, 234, 234))
        g.text((x - 9, y0 + len(paires) * BLOC - 10), f"{cm2}", font=f_p,
               fill=(110, 110, 110))
    g.text((X0 + LARG // 2 - 60, y0 + len(paires) * BLOC + 10),
           "aire atteinte (cm², échelle log)", font=f_n, fill=TEXTE)

    for i, (av, ap_) in enumerate(paires):
        yb = y0 + i * BLOC
        g.text((40, yb + 10), av["rouleau"], font=f_n, fill=TEXTE)
        for k, (l, coul, etiq) in enumerate(((av, AVANT, f"{av['generations_min']}–"
                                                        f"{av['generations_max']} gén."),
                                             (ap_, APRES, f"{ap_['generations_min']}–"
                                                          f"{ap_['generations_max']} gén."))):
            y = yb + 4 + k * 22
            xs = [x_de(c) for c in l["aires"]]
            g.line([min(xs), y, max(xs), y], fill=coul, width=2)
            for c, cr in zip(l["aires"], l["croisements"]):
                x = x_de(c)
                g.ellipse([x - 4, y - 4, x + 4, y + 4],
                          fill=SALE if cr else PROPRE, outline=(255, 255, 255))
            sales = sum(1 for c in l["croisements"] if c)
            g.text((X0 - 118, y - 7), etiq, font=f_p, fill=coul)
            g.text((X0 + LARG + 12, y - 7),
                   f"{l['etendue_relative']:.0%}".rjust(4)
                   + f"  {sales}/{len(l['aires'])} sale", font=f_p,
                   fill=SALE if sales > len(l["aires"]) / 2 else (110, 110, 110))

    yb = y0 + len(paires) * BLOC + 44
    disp_av = [av["etendue_relative"] for av, _ in paires]
    disp_ap = [ap_["etendue_relative"] for _, ap_ in paires]
    sales_av = sum(1 for av, _ in paires for c in av["croisements"] if c)
    sales_ap = sum(1 for _, ap_ in paires for c in ap_["croisements"] if c)
    n_av = sum(len(av["aires"]) for av, _ in paires)
    n_ap = sum(len(ap_["aires"]) for _, ap_ in paires)
    for i, t in enumerate((
            f"dispersion d'aire : {min(disp_av):.1%}–{max(disp_av):.0%} au plafond "
            f"d'origine, {min(disp_ap):.0%}–{max(disp_ap):.0%} une fois relevé",
            f"tirages qui s'auto-intersectent : {sales_av}/{n_av} contre "
            f"{sales_ap}/{n_ap}",
            "⚠⚠ la stabilité ET la propreté étaient des effets du budget, "
            "pas des propriétés du rouleau")):
        g.text((40, yb + i * 20), t, font=f_n, fill=SALE if i == 2 else TEXTE)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})  {len(paires)} rouleau(x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
