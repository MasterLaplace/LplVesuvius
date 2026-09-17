"""Plus de profondeur, ou plus de discernement ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les TROIS formes dessinées, toutes
du même tour total : une marche, une dérive, un escalier. En haut à droite, le plancher par largeur —
il descend. En bas à gauche, ce que devient un EMPILEMENT à chaque largeur — il se retourne. En bas à
droite, les deux courbes l'une contre l'autre : c'est un échange, pas un gain.

  uv run python src/figures/figure_plus_de_profondeur_ou_plus_de_discernement.py \\
      --json docs/mesures/plus_de_profondeur_ou_plus_de_discernement.json \\
      --sortie docs/images/178_plus_de_profondeur_ou_plus_de_discernement.png
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

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 », le zéro des dizaines rogné comme s'il était décimal. Défaut payé par `177`, vu en
    REGARDANT l'image et par aucune garde.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `plus_de_profondeur_ou_plus_de_discernement.py`.

    ⚠⚠ Refuse une mesure dont un barreau n'a pas SON contrôle d'escalier. Le résultat de cette
    tranche est un ÉCHANGE : dessiner des planchers sans ce que chaque largeur fait d'un empilement
    ferait lire « le plancher descend » comme un gain, alors que c'est la moitié de l'énoncé.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_barreaux", "le_verdict", "le_rouleau"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for b in d["les_barreaux"]:
        if not b.get("escalier") or not b.get("plancher"):
            raise ValueError(f"{chemin} : le barreau {b.get('largeur')} n'a pas son contrôle")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
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

    v, bx_ = d["le_verdict"], d["les_barreaux"]
    n, pli = int(d["couches"]), int(d["pli_en_couches"])
    tour = float(d["le_quart_de_tour_deg"])
    fr = list(d["frontieres_de_pli"])

    ecrire(28, 20, "Plus de profondeur, ou plus de discernement ? — c'est un échange, pas un gain",
           gros, ENCRE)
    ecrire(28, 46, f"Pli {pli} couches sur {n} · frontières {fr} · {d['permutations']} "
                   f"permutations · {d['graines_par_cellule']} graines par cellule", petit, GRIS)

    # ---- panneau 1 : les TROIS formes, meme tour total
    x0, y0, pw, ph = 56, 122, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois formes — même tour total, répartition différente", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 130, y0 + 30, 430, 112
    art.line([gx, gy, gx, gy + gh], fill=TRAIT, width=1)
    art.line([gx, gy + gh, gx + gw, gy + gh], fill=TRAIT, width=1)
    yb, yh = gy + gh, gy + 6
    xf = gx + gw * 37.0 / float(n - 1)
    segment(gx, yb, xf, yb, BON)
    art.line([xf, yb, xf, yh], fill=BON, width=3)
    points.append((xf, yh))
    segment(xf, yh, gx + gw, yh, BON)
    pas = gw / 12.0
    for k in range(12):
        segment(gx + k * pas, yb - (yb - yh) * k / 12.0,
                gx + (k + 1) * pas, yb - (yb - yh) * (k + 1) / 12.0, CONTRE)
    marches = max(1, len(fr))
    xprec, yprec = gx, yb
    for k, f_ in enumerate(fr, start=1):
        xk = gx + gw * float(f_) / float(n - 1)
        yk = yb - (yb - yh) * float(k) / float(marches)
        segment(xprec, yprec, xk, yprec, ALERTE)
        art.line([xk, yprec, xk, yk], fill=ALERTE, width=3)
        points.append((xk, yk))
        xprec, yprec = xk, yk
    segment(xprec, yprec, gx + gw, yprec, ALERTE)
    ecrire(x0 + 14, yb - 14, "une marche", 0, BON)
    ecrire(x0 + 14, gy + 2, "une dérive", 0, CONTRE)
    ecrire(x0 + 14, gy + 42, "un escalier", 0, ALERTE)
    ecrire(x0 + 14, gy + 60, "de plis", 0, GRIS)
    ecrire(gx + gw + 6, yh - 6, f"{_fr(tour, 1)}°", 0, ENCRE)
    ecrire(gx + gw + 6, yb - 6, "0°", 0, ENCRE)
    ecrire(gx - 4, yb + 14, "0", 0, GRIS)
    ecrire(gx + gw - 18, yb + 14, str(n - 1), 0, GRIS)
    ecrire(gx + gw / 2 - 26, yb + 32, "couche", 0, GRIS)
    ecrire(x0 + 14, y0 + 186,
           "★ L'ESCALIER NE TOURNE PAS : il est constant par morceaux et saute à chaque", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 202,
           "frontière de pli. Un rouleau n'est pas une matière qui pivote, c'est un", petit, GRIS)
    ecrire(x0 + 14, y0 + 218, "empilement — et `175` mesure que la campagne en porte trois plis.",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 242,
           "⚠ Les sauts sont posés aux frontières, et la phase est balayée par les", petit, GRIS)
    ecrire(x0 + 14, y0 + 258, "graines : `175` mesure que la lecture en dépend.", petit, GRIS)

    # ---- panneau 2 : le plancher par largeur
    x0, y0, pw, ph = 712, 122, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le plancher descend avec la largeur", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, "largeur", petit, GRIS)
    ecrire(x0 + 170, y0 + 12, "plancher tenu", petit, ENCRE)
    ecrire(x0 + 330, y0 + 12, "part du quart de tour", petit, GRIS)
    for k, b in enumerate(bx_):
        yy = y0 + 40 + k * 32
        pl = b["plancher"]
        t = pl["le_plus_petit_tour_tenu_deg"]
        ecrire(x0 + 14, yy, f"{b['en_plis']} pli(s) · {b['largeur']} c.", 0, ENCRE)
        ecrire(x0 + 170, yy, f"{_fr(t, 3)}°" if t else "aucun", 0, ENCRE if t else ALERTE)
        if t:
            barre(x0 + 330, yy + 2, 200, float(t) / tour, 12, CONTRE)
            ecrire(x0 + 540, yy, _fr(float(t) / tour, 3), 0, GRIS)
    ecrire(x0 + 14, y0 + 150,
           f"★  le plus bas vaut {_fr(v['le_plancher_le_plus_bas_deg'], 3)}° à "
           f"{v['a_la_largeur']} couches", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 176,
           f"     soit {_fr(v['il_vaut_le_quart_de_tour_fois'], 4)} fois le quart de tour",
           moyen, GRIS)
    ecrire(x0 + 14, y0 + 206,
           f"✗ la bascule du rouleau vaut {_fr(v['la_bascule_du_rouleau_deg'], 3)}° : ce plancher "
           f"vaut", petit, ALERTE)
    ecrire(x0 + 14, y0 + 222,
           f"{_fr(v['le_plancher_le_plus_bas_vaut_la_bascule_fois'], 4)} fois cette bascule, et "
           f"la profondeur est bornée par la campagne.", petit, ALERTE)
    ecrire(x0 + 14, y0 + 244,
           "⚠ Ce qui abaisse le plancher est le tour ACCUMULÉ, et l'accumuler veut", petit, GRIS)
    ecrire(x0 + 14, y0 + 260, "dire traverser des frontières de pli.", petit, GRIS)

    # ---- panneau 3 : ce que devient un EMPILEMENT
    x0, y0, pw, ph = 56, 450, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "et un empilement se retourne en rotation", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, "largeur", petit, GRIS)
    ecrire(x0 + 160, y0 + 12, "lu marche", petit, BON)
    ecrire(x0 + 268, y0 + 12, "lu dérive", petit, ALERTE)
    ecrire(x0 + 380, y0 + 12, "sans verdict", petit, GRIS)
    for k, b in enumerate(bx_):
        yy = y0 + 42 + k * 34
        es = b["escalier"]
        tot = max(1, int(es["lectures"]))
        ecrire(x0 + 14, yy, f"{b['en_plis']} pli(s)", 0, ENCRE)
        for dx, cle, coul in ((160, "lus_marche", BON), (268, "lus_derive", ALERTE),
                              (380, "sans_verdict", GRIS)):
            ecrire(x0 + dx, yy, f"{es[cle]}", 0, coul)
            barre(x0 + dx + 30, yy + 3, 62, float(es[cle]) / float(tot), 10, coul)
        ecrire(x0 + 490, yy,
               "★ empilement" if es["lu_plus_souvent_comme_un_empilement"] else "✗ rotation", 0,
               BON if es["lu_plus_souvent_comme_un_empilement"] else ALERTE)
    ecrire(x0 + 14, y0 + 162,
           "⚠⚠⚠ Rien ne tourne dans un escalier, et le juge dit qu'une rotation l'explique.",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 186,
           "⚠⚠ Ce n'est pas un zéro : même à un pli un empilement passe parfois pour une", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 202,
           "rotation. Ce qui bascule d'une largeur à l'autre est le SENS de la lecture", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 218, "dominante, et la mesure l'a imposé contre ma première rédaction.",
           petit, GRIS)

    # ---- panneau 4 : l'echange
    x0, y0, pw, ph = 712, 450, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux moitiés, l'une contre l'autre", moyen, ENCRE)
    gx2, gy2, gw2, gh2 = x0 + 60, y0 + 24, 460, 120
    art.line([gx2, gy2, gx2, gy2 + gh2], fill=TRAIT, width=1)
    art.line([gx2, gy2 + gh2, gx2 + gw2, gy2 + gh2], fill=TRAIT, width=1)
    m = max(1, len(bx_) - 1)
    prec = None
    for k, b in enumerate(bx_):
        t = b["plancher"]["le_plus_petit_tour_tenu_deg"]
        xk = gx2 + gw2 * k / float(m)
        yk = gy2 + gh2 - gh2 * (float(t) / tour if t else 0.0)
        if prec is not None:
            segment(prec[0], prec[1], xk, yk, CONTRE)
        prec = (xk, yk)
        ecrire(xk - 12, gy2 + gh2 + 8, f"{b['en_plis']}", 0, GRIS)
    prec = None
    for k, b in enumerate(bx_):
        es = b["escalier"]
        part = float(es["lus_marche"]) / max(1, int(es["lectures"]))
        xk = gx2 + gw2 * k / float(m)
        yk = gy2 + gh2 - gh2 * part
        if prec is not None:
            segment(prec[0], prec[1], xk, yk, ALERTE)
        prec = (xk, yk)
    ecrire(gx2 + gw2 + 6, gy2 - 4, "1", 0, GRIS)
    ecrire(gx2 + gw2 + 6, gy2 + gh2 - 8, "0", 0, GRIS)
    ecrire(gx2 - 46, gy2 + gh2 + 24, "plis lus", 0, GRIS)
    ecrire(x0 + 14, y0 + 190, "— plancher, en part du quart de tour", 0, CONTRE)
    ecrire(x0 + 14, y0 + 208, "— un empilement lu comme un empilement", 0, ALERTE)
    ecrire(x0 + 14, y0 + 230,
           "★ les deux courbes descendent ensemble : ce que la profondeur", petit, ENCRE)
    ecrire(x0 + 14, y0 + 246, "achète d'un côté, elle le paie de l'autre.", petit, ENCRE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18, "★  Le plancher DESCEND avec la largeur — la voie que `R4-P31` nommait "
                       "existe.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Le plus bas vaut {_fr(v['le_plancher_le_plus_bas_deg'], 3)}° à "
           f"{v['a_la_largeur']} couches, soit "
           f"{_fr(v['il_vaut_le_quart_de_tour_fois'], 4)} fois le quart de tour.", moyen, ENCRE)
    ecrire(78, y + 78,
           "✗  Mais un EMPILEMENT y devient une rotation, et un rouleau est un empilement.",
           moyen, ALERTE)
    lisibles = v["largeurs_ou_lempilement_reste_lisible"]
    donnent = v["largeurs_qui_donnent_les_deux"]
    ecrire(78, y + 106,
           "     Les largeurs où un empilement reste lisible : "
           + (" et ".join(f"{x} couches" for x in lisibles) if lisibles else "aucune") + ".",
           moyen, ENCRE)
    ecrire(78, y + 138,
           ("⚠⚠⚠ Aucune largeur ne donne les deux."
            if not donnent
            else "⚠⚠⚠ Donnent les deux : "
                 + " et ".join(f"{x} couches" for x in donnent) + ".")
           + " Le plancher le plus bas reste au-dessus de la bascule du rouleau,", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     {_fr(v['la_bascule_du_rouleau_deg'], 3)}° — il en vaut "
           f"{_fr(v['le_plancher_le_plus_bas_vaut_la_bascule_fois'], 4)} fois — et la largeur qui "
           "l'atteindrait a déjà cessé de distinguer un empilement d'une rotation.", petit, GRIS)
    ecrire(78, y + 190,
           "     Ce n'est donc pas un plancher à faire descendre : les deux moitiés sont la même "
           "quantité, le tour accumulé.", petit, GRIS)

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
    v("⭐ un nombre rond n'est pas rogné par la mise en forme",
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

    # ⭐⭐⭐⭐ LE PLANCHER DE CHAQUE LARGEUR EST LU : c'est la moitie de l'echange, et un plancher
    # ecrit en dur en ferait un dessin.
    faux = copy.deepcopy(d)
    faux["les_barreaux"][0]["plancher"]["le_plus_petit_tour_tenu_deg"] = 33.25
    _c, p2, _cd, _pt, b2, _t = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ le plancher de chaque largeur est lu, et sa barre bouge",
      any("33,25" in t for _x, _y, t, _f in p2) and b2 != barres)

    # ⭐⭐⭐⭐ ET L'AUTRE MOITIE AUSSI : ce que chaque largeur fait d'un EMPILEMENT.
    faux2 = copy.deepcopy(d)
    faux2["les_barreaux"][-1]["escalier"]["lus_derive"] = 317
    _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ ce qu'une largeur fait d'un empilement est lu",
      any("317" in t for _x, _y, t, _f in p3) and not any("317" in t for t in tous))

    # ⭐⭐⭐ LES FRONTIERES SONT LUES : l'escalier dessine doit suivre la mesure.
    faux3 = copy.deepcopy(d)
    faux3["frontieres_de_pli"] = [20, 50, 90]
    _c, p4, _cd, pt4, _b, _t = dessiner(faux3, sortie)
    v("⭐⭐⭐ l'escalier est dessiné aux frontières que la mesure porte",
      pt4 != points and any("[20, 50, 90]" in t for _x, _y, t, _f in p4))

    # ⭐⭐⭐⭐ LA BASCULE DU ROULEAU EST LUE DES DEUX COTES : sans elle, un plancher n'a pas d'echelle.
    faux4 = copy.deepcopy(d)
    faux4["le_verdict"]["la_bascule_du_rouleau_deg"] = 41.375
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ la bascule du rouleau est lue des DEUX côtés",
      sum(1 for _x, _y, t, _f in p5 if "41,375" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p5 if '41,375' in t)} mentions")

    # ⭐⭐⭐⭐ LA SECONDE BORNE EST LUE DES DEUX COTES : sans elle, « 22,5° » n'a pas d'echelle et
    # se lirait comme un plancher bas.
    fauxb = copy.deepcopy(d)
    fauxb["le_verdict"]["le_plancher_le_plus_bas_vaut_la_bascule_fois"] = 9.1234
    _c, pb, _cd, _pt, _b, _t = dessiner(fauxb, sortie)
    v("⭐⭐⭐⭐ le rapport du plancher à la bascule est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in pb if "9,1234" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in pb if '9,1234' in t)} mentions")

    faux5 = copy.deepcopy(d)
    faux5["le_verdict"]["largeurs_qui_donnent_les_deux"] = [72]
    _c, p6, _cd, _pt, _b, _t = dessiner(faux5, sortie)
    v("⭐⭐⭐ les largeurs qui donneraient les deux sont LUES, pas écrites",
      any("Donnent les deux : 72 couches" in t for _x, _y, t, _f in p6)
      and any("Aucune largeur ne donne les deux" in t for t in tous))

    creux = copy.deepcopy(d)
    creux["les_barreaux"][1].pop("escalier")
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("un barreau sans son contrôle d'escalier est REFUSÉ", lire_ok)

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
                   / "plus_de_profondeur_ou_plus_de_discernement.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "178_plus_de_profondeur_ou_plus_de_discernement.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
