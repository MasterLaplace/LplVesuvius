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
    uv run python src/figures/figure_plafond.py \\
        --origine docs/mesures/table_tirages.json --releve docs/mesures/table_tirages_plafond.json \\
        --sortie docs/images/35_plafond.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

LARGEUR = 1120
X0, LARG = 210, 700          # origine et largeur de l'axe des aires
BLOC = 62                    # hauteur d'un rouleau (deux lignes)
CM2_MIN, CM2_MAX = 8.0, 300.0

# ⚠ La table de traduction de CETTE figure. Elle vit a cote du dessin plutot que dans
# `langue.py` : une table partagee entre figures obligerait a formuler les libelles pareil
# partout, ce qui contraindrait la figure au lieu de la servir.
ANGLAIS = {
    "Le même rouleau, le même appel — seul le budget de générations change":
        "The same scroll, the same call — only the generation budget changes",
    "un point = un tirage ; rouge = la trace s'auto-intersecte ; ":
        "one dot = one run; red = the trace self-intersects; ",
    "générations": "generations",
    "gén.": "gen.",
    "aire atteinte (cm², échelle log)": "area reached (cm², log scale)",
    "dispersion d'aire : ": "area dispersion: ",
    "% à ": "% to ",
    " au plafond d'origine, ": " at the original budget, ",
    " une fois relevé": " once raised",
    "tirages qui s'auto-intersectent : ": "self-intersecting runs: ",
    " contre ": " against ",
    "la stabilité ET la propreté étaient des effets du budget, ":
        "stability AND cleanliness were effects of the budget, ",
    "pas des propriétés du rouleau": "not properties of the scroll",
    "hors du verdict, dessinés quand même : ": "outside the verdict, drawn anyway: ",
    "moins de deux tirages, ou ": "fewer than two runs, or ",
    "buté sur le nouveau plafond": "hit the new budget",
    " sale": " dirty",
}

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


def jugeables(origine: dict, releve: dict) -> set[str]:
    """Les rouleaux que le VERDICT retient, décidés par `comparer_plafond`.

    ⚠⚠ Importé plutôt que réécrit. Qui compte dans le verdict est une règle — écarter
    ceux qui butent aussi sur le nouveau plafond, écarter ceux qui n'ont pas deux tirages
    des deux côtés — et deux implémentations d'une même règle finissent par ne pas
    s'accorder. La figure afficherait alors une moyenne que le tableau ne donne pas, sans
    qu'aucune ligne ne dise laquelle est la bonne.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    from comparer_plafond import confronter
    d = confronter(origine, releve)
    ecartes = set(d["rouleaux_satures_ecartes"]) | set(d["rouleaux_trop_peu_de_tirages"])
    return {l["rouleau"] for l in d["lignes"]} - ecartes


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
    # ⚠⚠ La regle « qui compte » est IMPORTEE, pas reecrite : la sonde verifie que la
    # figure ecarte exactement ce que le tableau ecarte. Deux definitions divergeraient,
    # et la figure afficherait une moyenne que le tableau ne donne pas.
    def l(nom, n, disp, gmax=250):
        return {"rouleau": nom, "generations_min": 200, "generations_max": gmax,
                "aire_mediane": 50.0, "etendue_relative": disp, "n": n,
                "verdict_bascule": False, "propres": n}
    av = {"budget_generations": 120,
          "lignes": [l("A", 6, 0.003, 118), l("B", 6, 0.004, 118)]}
    ap = {"budget_generations": 400, "lignes": [l("A", 6, 1.10), l("B", 1, 0.0)]}
    v("la figure retient ce que le tableau retient",
      jugeables(av, ap) == {"A"}, str(jugeables(av, ap)))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--origine", type=Path, default=racine / "docs/mesures/table_tirages.json")
    ap.add_argument("--releve", type=Path,
                    default=racine / "docs/mesures/table_tirages_plafond.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/35_plafond.png")
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--anglais", action="store_true",
                    help="écrire la figure en anglais (pour l'article)")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    from langue import Traduisant

    for f in (a.origine, a.releve):
        if not f.is_file():
            print(f"absent : {f} — lancer d'abord table_tirages.py --json", file=sys.stderr)
            return 1
    o, r = json.loads(a.origine.read_text()), json.loads(a.releve.read_text())
    paires = apparier(o, r)
    if not paires:
        print("aucun rouleau tracé des deux côtés", file=sys.stderr)
        return 1

    hauteur = 130 + len(paires) * BLOC + 130
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    # ⭐ UNE ligne : tout ce qui s'ecrit passe par `g.text`, donc envelopper l'objet de
    # dessin suffit a traduire la figure entiere.
    g = Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)
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
            # ⚠ Une decimale sous 10 % : « 0 % » se lit comme une egalite exacte alors
            # que la dispersion vaut 0,31 % — et c'est justement la petitesse de ce
            # nombre qui est le resultat, donc l'arrondir a zero l'efface.
            d = l["etendue_relative"]
            txt = (f"{d:.1%}" if d < 0.10 else f"{d:.0%}").replace(".", ",")
            g.text((X0 + LARG + 12, y - 7),
                   txt.rjust(6) + f"  {sales}/{len(l['aires'])} sale", font=f_p,
                   fill=SALE if sales > len(l["aires"]) / 2 else (110, 110, 110))

    yb = y0 + len(paires) * BLOC + 44
    retenus = jugeables(o, r)
    juges = [(av, ap_) for av, ap_ in paires if ap_["rouleau"] in retenus]
    ecartes = [ap_["rouleau"] for _, ap_ in paires if ap_["rouleau"] not in retenus]
    disp_av = [av["etendue_relative"] for av, _ in juges]
    disp_ap = [ap_["etendue_relative"] for _, ap_ in juges]
    sales_av = sum(1 for av, _ in juges for c in av["croisements"] if c)
    sales_ap = sum(1 for _, ap_ in juges for c in ap_["croisements"] if c)
    n_av = sum(len(av["aires"]) for av, _ in juges)
    n_ap = sum(len(ap_["aires"]) for _, ap_ in juges)
    if not juges:
        print("aucun rouleau ne passe le filtre du verdict", file=sys.stderr)
        return 1
    for i, t in enumerate((
            f"dispersion d'aire : {min(disp_av):.1%} à {max(disp_av):.1%} au plafond "
            f"d'origine, {min(disp_ap):.0%} à {max(disp_ap):.0%} une fois relevé"
            .replace(".", ","),
            f"tirages qui s'auto-intersectent : {sales_av}/{n_av} contre "
            f"{sales_ap}/{n_ap}",
            "⚠⚠ la stabilité ET la propreté étaient des effets du budget, "
            "pas des propriétés du rouleau")):
        g.text((40, yb + i * 20), t, font=f_n, fill=SALE if i == 2 else TEXTE)

    if ecartes:
        g.text((40, yb + 3 * 20), f"⚠ hors du verdict, dessinés quand même : "
                                  f"{', '.join(ecartes)} — moins de deux tirages, ou "
                                  f"buté sur le nouveau plafond", font=f_n,
               fill=(120, 120, 120))

    # ⚠⚠ Une figure a moitie traduite a l'air traduite. On REFUSE de l'ecrire.
    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})  {len(paires)} rouleau(x), "
          f"{len(juges)} au verdict")
    return 0


if __name__ == "__main__":
    sys.exit(main())
