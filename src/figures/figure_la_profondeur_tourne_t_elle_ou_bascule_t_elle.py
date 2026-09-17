"""La profondeur tourne-t-elle, ou bascule-t-elle ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les deux formes DESSINÉES :
elles portent le même tour et ne diffèrent que par sa répartition. En haut à droite, les trois
matières construites et l'étalon. En bas à gauche, le DOMAINE — la seule ligne entièrement tenue
est le quart de tour, et la case du rouleau est en bas à droite du tableau. En bas à droite, ce que
l'excédent achète, et le SENS de la panne.

  uv run python src/figures/figure_la_profondeur_tourne_t_elle_ou_bascule_t_elle.py \\
      --json docs/mesures/la_profondeur_tourne_t_elle_ou_bascule_t_elle.json \\
      --sortie docs/images/177_la_profondeur_tourne_t_elle_ou_bascule_t_elle.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE, ET C'EST UN DÉFAUT PAYÉ. Sans ce
    garde, `_fr(90, 0)` rend « 9 » : le zéro des dizaines est rogné comme s'il était décimal, et
    l'axe d'un graphe affiche un angle dix fois trop petit — un nombre juste sous un mauvais nom,
    pire qu'un nombre absent. Il a été vu en REGARDANT l'image, par aucune garde.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_profondeur_tourne_t_elle_ou_bascule_t_elle.py`.

    ⚠⚠ Refuse une mesure sans DOMAINE. Le résultat de cette tranche n'est pas un verdict mais
    l'étendue où ce verdict vaut : dessiner le juge sans son domaine ferait lire « il sépare une
    marche d'une dérive » comme une capacité, alors que c'est une capacité BORNÉE, et que la borne
    exclut justement l'amplitude que le rouleau montre.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_matieres", "la_fixture", "le_domaine", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_domaine"].get("cellules"):
        raise ValueError(f"{chemin} : le domaine n'a aucune cellule")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : {d['le_verdict'].get('raison', 'verdict indécidable')}")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def segment(x1, y1, x2, y2, coul, largeur=3):
        art.line([x1, y1, x2, y2], fill=coul, width=largeur)
        points.append((x1, y1))
        points.append((x2, y2))
        traits.append((min(x1, x2), (y1 + y2) / 2.0, max(x1, x2)))

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    m, fx, dom, v = d["les_matieres"], d["la_fixture"], d["le_domaine"], d["le_verdict"]

    ecrire(28, 20, "La profondeur tourne-t-elle, ou bascule-t-elle ? — le juge existe, "
                   "son domaine exclut le rouleau", gros, ENCRE)
    ecrire(28, 46, f"Deux ajustements lus par le même estimateur, fenêtre d'un pli "
                   f"({d['largeur_en_couches']} couches sur {d['couches']}), "
                   f"{d['permutations']} permutations, {dom['graines_par_cellule']} graines par "
                   f"cellule", petit, GRIS)

    # ---- panneau 1 : les deux formes portent le MEME tour
    x0, y0, pw, ph = 56, 122, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux formes — même tour total, répartition différente", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 130, y0 + 34, 430, 118
    tour = float(d["le_quart_de_tour_deg"])
    n, fr = int(d["couches"]), int(d["frontiere"])
    art.line([gx, gy, gx, gy + gh], fill=TRAIT, width=1)
    art.line([gx, gy + gh, gx + gw, gy + gh], fill=TRAIT, width=1)
    yb, yh = gy + gh, gy + 6
    xf = gx + gw * fr / float(n - 1)
    segment(gx, yb, xf, yb, BON)
    art.line([xf, yb, xf, yh], fill=BON, width=3)
    points.append((xf, yh))
    segment(xf, yh, gx + gw, yh, BON)
    pas = gw / 12.0
    for k in range(12):
        xa, xbb = gx + k * pas, gx + (k + 1) * pas
        ya = yb - (yb - yh) * k / 12.0
        ybb = yb - (yb - yh) * (k + 1) / 12.0
        segment(xa, ya, xbb, ybb, CONTRE)
    ecrire(x0 + 14, gy + gh - 14, "une marche", 0, BON)
    ecrire(x0 + 14, gy + gh + 4, f"à la couche {fr}", 0, GRIS)
    ecrire(x0 + 14, gy + 2, "une dérive", 0, CONTRE)
    ecrire(x0 + 14, gy + 20, "régulière", 0, GRIS)
    ecrire(gx + gw + 6, yh - 6, f"{_fr(tour, 0)}°", 0, ENCRE)
    ecrire(gx + gw + 6, yb - 6, "0°", 0, ENCRE)
    ecrire(gx - 4, yb + 14, "0", 0, GRIS)
    ecrire(gx + gw - 18, yb + 14, str(n - 1), 0, GRIS)
    ecrire(gx + gw / 2 - 26, yb + 30, "couche", 0, GRIS)
    ecrire(x0 + 14, y0 + 200,
           "⚠ Les deux portent exactement le même tour : sans cette égalité, le verdict",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216,
           "mesurerait l'amplitude — que `176` a déjà mesurée — au lieu de la FORME.",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 240,
           "⚠⚠ La fenêtre est désignée par le NUL, jamais par un candidat : les deux",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 256,
           "retenaient sinon une fenêtre homogène, où tous deux atteignent un.", petit, GRIS)

    # ---- panneau 2 : les trois matieres construites, et l'etalon
    x0, y0, pw, ph = 712, 122, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les matières construites — trois réponses différentes", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, "matière", petit, GRIS)
    ecrire(x0 + 150, y0 + 12, "nul", petit, GRIS)
    ecrire(x0 + 225, y0 + 12, "exc. marche", petit, BON)
    ecrire(x0 + 340, y0 + 12, "exc. dérive", petit, CONTRE)
    ecrire(x0 + 455, y0 + 12, "verdict", petit, ENCRE)
    for k, x in enumerate(m["lignes"]):
        yy = y0 + 40 + k * 30
        ma, de = x["la_marche"], x["la_derive"]
        juste = x["le_verdict_est_celui_construit"]
        ecrire(x0 + 14, yy, x["matiere"], 0, ENCRE)
        ecrire(x0 + 150, yy, _fr(x["part_constante"]), 0, GRIS)
        ecrire(x0 + 225, yy, _fr(ma.get("excedent")), 0, BON)
        ecrire(x0 + 340, yy, _fr(de.get("excedent")), 0, CONTRE)
        ecrire(x0 + 455, yy, f"{'★' if juste else '✗'} {x['gagnant'] or 'aucun'}", 0,
               BON if juste else ALERTE)
    ecrire(x0 + 14, y0 + 146,
           f"★  l'étalon : la fixture à deux plis, {fx['marches']}/{fx['cellules']} décalages "
           f"jugés marche", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 174,
           f"     excédents {_fr(fx['excedent_median_de_la_marche'])} contre "
           f"{_fr(fx['excedent_median_de_la_derive'])}", moyen, GRIS)
    ecrire(x0 + 14, y0 + 210,
           "⚠⚠⚠ Sans les trois, un juge dégénéré passerait : celui qui dit toujours", petit, GRIS)
    ecrire(x0 + 14, y0 + 226,
           "« marche », celui qui dit toujours « dérive », celui qui ne dit rien.", petit, GRIS)
    ecrire(x0 + 14, y0 + 244,
           "⚠ Le nul est rendu à côté : une part de un ne dit pas s'il y a quelque", petit, GRIS)
    ecrire(x0 + 14, y0 + 258, "chose à expliquer.", petit, GRIS)

    # ---- panneau 3 : le DOMAINE
    x0, y0, pw, ph = 56, 450, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le domaine — verdicts justes sur "
                        f"{dom['graines_par_cellule']} (marche / dérive)", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "tour °", petit, GRIS)
    ecrire(x0 + 120, y0 + 10, "dispersion par couche, en degrés", petit, GRIS)
    cx = x0 + 150
    for j, disp in enumerate(dom["dispersions"]):
        ecrire(cx + j * 108, y0 + 32, _fr(disp, 2), 0, GRIS)
    for i, t in enumerate(dom["tours"]):
        yy = y0 + 58 + i * 30
        cells = [c for c in dom["cellules"] if c["tour_deg"] == t]
        tenue = all(c["les_deux_formes_sont_rendues"] for c in cells)
        ecrire(x0 + 14, yy, f"{'★' if tenue else ' '} {_fr(t, 3)}", 0, ENCRE if tenue else GRIS)
        for j, c in enumerate(cells):
            plein = c["les_deux_formes_sont_rendues"]
            au_rouleau = (dom["au_tour_du_rouleau"] is not None
                          and c["tour_deg"] == dom["au_tour_du_rouleau"]["tour_deg"]
                          and c["dispersion_deg"] == dom["au_tour_du_rouleau"]["dispersion_deg"])
            marque = "✗ " if au_rouleau else ""
            ecrire(cx + j * 108, yy,
                   f"{marque}{c['marches_justes']}/{c['derives_justes']}", 0,
                   BON if plein else (ALERTE if au_rouleau else GRIS))
    ecrire(x0 + 14, y0 + 218,
           f"✗ la case du rouleau : {_fr(v['la_bascule_du_rouleau_deg'], 3)}° de bascule pour "
           f"{_fr(v['le_temoin_du_rouleau_deg'], 2)}° de témoin", petit, ALERTE)
    ecrire(x0 + 14, y0 + 238,
           "⚠⚠ L'échelle des tours est dérivée : le quart de tour, ses moitiés, puis la bascule "
           "mesurée.", petit, GRIS)

    # ---- panneau 4 : ce que l'excedent achete, et le SENS de la panne
    x0, y0, pw, ph = 712, 450, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que l'excédent achète, et le sens de la panne", moyen, ENCRE)
    total = int(len(dom["tours"]) * len(dom["dispersions"]) * 2 * dom["graines_par_cellule"])
    bx, bw = x0 + 190, 300
    for k, (nom, val, coul) in enumerate(
            (("par l'excédent", v["verdicts_justes_par_lexcedent"], BON),
             ("par la part brute", v["verdicts_justes_par_les_parts_brutes"], CONTRE))):
        yy = y0 + 24 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        barre(bx, yy + 2, bw, val / float(total), 14, coul)
        ecrire(bx + bw + 10, yy, f"{val}/{total}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 98,
           f"★ les deux règles diffèrent sur {v['verdicts_ou_les_deux_regles_different']} "
           f"verdicts", petit, ENCRE)
    ecrire(x0 + 14, y0 + 122, "à la case du rouleau, sur "
           f"{dom['graines_par_cellule']} tirages :", petit, GRIS)
    g = int(dom["graines_par_cellule"])
    for k, (nom, val, coul) in enumerate(
            (("une marche est lue marche", v["marches_justes_au_tour_du_rouleau"], BON),
             ("une dérive est lue dérive", v["derives_justes_au_tour_du_rouleau"], ALERTE))):
        yy = y0 + 146 + k * 30
        ecrire(x0 + 14, yy, nom, 0, coul)
        barre(bx, yy + 2, bw, val / float(g), 12, coul)
        ecrire(bx + bw + 10, yy, f"{val}/{g}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 214,
           "⚠⚠⚠ La panne a un SENS : le juge lit une dérive comme une marche.", petit, ALERTE)
    ecrire(x0 + 14, y0 + 234,
           "Une lecture « marche de six degrés » est exactement ce qu'il rendrait", petit, GRIS)
    ecrire(x0 + 14, y0 + 250, "sur une dérive.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18, "★  Le troisième énoncé existe, et il sépare — au quart de tour.",
           moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Le plus petit tour entièrement tenu vaut {_fr(v['le_plus_petit_tour_tenu_deg'])}°"
           f", soit {_fr(v['il_vaut_le_quart_de_tour_fois'])} fois le quart de tour.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  La bascule que `176` a mesurée sur le rouleau vaut "
           f"{_fr(v['la_bascule_du_rouleau_deg'], 3)}°, soit "
           f"{_fr(v['la_bascule_du_rouleau_vaut_le_plancher_fois'], 4)} fois ce plancher.",
           moyen, ALERTE)
    ecrire(78, y + 106,
           "     Le domaine mesuré ne la couvre pas, donc cette tranche ne pointe PAS le juge sur "
           "la matière — précédent de `174`.", moyen, ENCRE)
    ecrire(78, y + 138,
           "⚠⚠⚠ Et la panne a un sens : au tour du rouleau, une marche est lue juste "
           f"{v['marches_justes_au_tour_du_rouleau']} fois sur {g}, une dérive "
           f"{v['derives_justes_au_tour_du_rouleau']} fois sur {g}.", moyen, ENCRE)
    ecrire(78, y + 166,
           "     Ce que `176` publie — de l'ordre en profondeur d'une amplitude de six degrés — "
           "est donc compatible avec une rotation lente,", petit, GRIS)
    ecrire(78, y + 186,
           "     et rien ici ne permet de l'en séparer. Ce qui est borné, ce n'est pas la "
           "question : c'est l'instrument.", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    # ⚠⚠⚠ UN NOMBRE ROND NE DOIT PAS ETRE ROGNE : `_fr(90, 0)` rendait « 9 » et l'axe du graphe
    # affichait un angle dix fois trop petit. Aucune garde de figure ne voit ca — il a fallu
    # regarder l'image.
    v("⭐⭐⭐⭐ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(20.0, 1), _fr(6.862, 3)) == ("90", "20", "6,862"),
      f"{(_fr(90.0, 0), _fr(20.0, 1), _fr(6.862, 3))}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    def _boite(x, y, texte, f):
        b = f.getbbox(texte)
        return (x + b[0], y + b[1], x + b[2], y + b[3])

    traverses = [(t, round(x1), round(x2)) for x1, ty, x2 in traits
                 for (px, py, t, f) in poses
                 if (lambda b: b[0] < x2 and b[2] > x1 and b[1] <= ty <= b[3])(
                     _boite(px, py, t, f))]
    v("⭐⭐⭐⭐ aucun trait ne traverse un texte", not traverses,
      f"{len(traits)} traits, {traverses}"[:180])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⭐⭐⭐⭐ LE DOMAINE EST LU CASE PAR CASE : c'est le tableau QUI EST le resultat, et une case
    # ecrite en dur en ferait un dessin.
    faux = copy.deepcopy(d)
    faux["le_domaine"]["cellules"][0]["marches_justes"] = 7
    faux["le_domaine"]["cellules"][0]["les_deux_formes_sont_rendues"] = False
    _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ chaque case du domaine est lue",
      any("7/20" in t for _x, _y, t, _f in p2) and not any("7/20" in t for t in tous))

    # ⭐⭐⭐⭐ LA FORME EST DESSINEE DEPUIS LA MESURE : la frontiere deplace le coin de la marche.
    faux2 = copy.deepcopy(d)
    faux2["frontiere"] = 90
    _c, _p, _cd, pt3, _b, _t = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ la marche est dessinée à la frontière que la mesure porte",
      pt3 != points and any("90" in t for _x, _y, t, _f in _p))

    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["le_plus_petit_tour_tenu_deg"] = 33.25
    faux3["le_verdict"]["il_vaut_le_quart_de_tour_fois"] = 0.369
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le plancher du domaine est LU, jamais écrit",
      any("33,25" in t for _x, _y, t, _f in p4) and any("0,369" in t for _x, _y, t, _f in p4))

    # ⭐⭐⭐⭐ LE RAPPORT AU PLANCHER EST L'ARGUMENT, DONC IL EST LU DES DEUX COTES : la bascule du
    # rouleau doit apparaitre dans le tableau ET dans la bande.
    faux4 = copy.deepcopy(d)
    faux4["le_verdict"]["la_bascule_du_rouleau_deg"] = 41.375
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ la bascule du rouleau est lue des DEUX côtés",
      sum(1 for _x, _y, t, _f in p5 if "41,375" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p5 if '41,375' in t)} mentions")

    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["verdicts_justes_par_lexcedent"] = 412
    _c, p6, _cd, _pt, b6, _t = dessiner(faux5, sortie)
    v("⭐⭐⭐ ce que l'excédent achète est lu, et sa barre bouge",
      any("412/" in t for _x, _y, t, _f in p6) and b6 != barres)

    # ⭐⭐⭐ LE SENS DE LA PANNE EST LU DES DEUX COTES : le tableau et la bande.
    faux6 = copy.deepcopy(d)
    faux6["le_verdict"]["derives_justes_au_tour_du_rouleau"] = 17
    _c, p7, _cd, _pt, _b, _t = dessiner(faux6, sortie)
    v("⭐⭐⭐ le compte des dérives justes est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p7 if "17" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p7 if '17' in t)} mentions")

    creux = copy.deepcopy(d)
    creux["le_domaine"] = {}
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans DOMAINE est REFUSÉE, jamais dessinée à moitié", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_profondeur_tourne_t_elle_ou_bascule_t_elle.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "177_la_profondeur_tourne_t_elle_ou_bascule_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
