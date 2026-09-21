"""Jusqu'où une nappe tient-elle ? Les deux budgets, et celui qui lie.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, L'ÉQUATION DE CONCEPTION DESSINÉE : l'écart
attendu croît comme la racine du nombre de coutures, une courbe par budget, et la bande du
demi-feuillet les coupe. L'abscisse du croisement EST la longueur tenable, et la largeur d'une rangée
entière est tracée en travers — l'œil voit d'un coup lesquels passent et lesquels non. En bas à
gauche, le triangle des bruits propres contre la décomposition de `208`. Au centre, la part d'une
rangée que chaque budget couvre. À droite, le verdict et ce qui reste à mesurer.

  uv run python src/figures/figure_le_budget_de_la_nappe.py \\
      --json docs/mesures/le_budget_de_la_nappe.json \\
      --sortie docs/images/212_le_budget_de_la_nappe.png
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
    « 9 ». Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_budget_de_la_nappe.py`.

    ⚠⚠⚠ LE REFUS QUI COMPTE EST CELUI D'UNE TRANCHE QUI DÉCLARERAIT UNE ÉPREUVE. Celle-ci ne tire
    aucun échantillon : elle relit des mesures publiées et en tire une conséquence arithmétique.
    Déclarer une épreuve lui ferait payer une part de la garantie pour un tirage qui n'existe pas,
    et la figure donnerait à lire un test là où il n'y en a aucun.

    ⚠⚠ ET UN MODÈLE RÉFUTÉ EST REFUSÉ : si une variance propre sort négative, le triangle dit que
    le modèle ne tient pas, et tout ce que la figure dessine au-dessus cesse d'avoir un sens.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("les_budgets", "le_triangle", "ce_quune_rangee_demande", "la_nappe_entiere",
                "le_verdict", "le_triangle_contre_208", "ce_que_210_a_rendu",
                "ce_que_211_a_rendu"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("les_budgets", "le_triangle", "ce_quune_rangee_demande", "la_nappe_entiere",
                "le_verdict"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if d.get("les_epreuves_declarees"):
        raise ValueError(f"{chemin} : une épreuve est déclarée alors qu'aucun échantillon "
                         f"n'est tiré")
    if not d["le_triangle"].get("le_modele_tient"):
        raise ValueError(f"{chemin} : le triangle RÉFUTE le modèle — variances négatives "
                         f"{d['le_triangle'].get('les_variances_negatives')}")
    b = d["les_budgets"]
    if not (b.get("traverser") or {}) or not (b.get("saccorder") or {}):
        raise ValueError(f"{chemin} : un des deux budgets est vide")
    for nom in ("la_moyenne_des_rangees", "une_rangee_seule", "le_plancher_de_la_matiere"):
        x = (b["traverser"] or {}).get(nom)
        if not x or not x.get("decidable"):
            raise ValueError(f"{chemin} : le budget de traversée « {nom} » manque")
    if len(b["saccorder"]) < 3:
        raise ValueError(f"{chemin} : moins de trois paires budgétées")
    if b.get("le_budget_qui_lie") not in ("traverser", "s'accorder"):
        raise ValueError(f"{chemin} : le budget qui lie n'est pas nommé")
    if len(d["le_triangle"].get("les_bruits_propres") or {}) != 3:
        raise ValueError(f"{chemin} : le triangle ne porte pas trois rangées")
    if d["ce_quune_rangee_demande"].get("les_coutures_dune_rangee") is None:
        raise ValueError(f"{chemin} : la largeur d'une rangée entière manque")
    if not (d["la_nappe_entiere"].get("ce_qui_reste_a_mesurer") or "").strip():
        raise ValueError(f"{chemin} : la nappe ne nomme pas ce qui reste à mesurer")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    v = d["le_verdict"]
    if v.get("le_budget_qui_lie") == "traverser":
        return "Le budget de la nappe — c'est TRAVERSER qui lie, et s'accorder est gratuit"
    if v.get("une_rangee_entiere_saccorde"):
        return "Le budget de la nappe — une rangée entière tient dans les deux budgets"
    return ("Le budget de la nappe — c'est S'ACCORDER qui lie, et une rangée entière n'y tient "
            "pas")


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

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    b, tri, q = d["les_budgets"], d["le_triangle"], d["ce_quune_rangee_demande"]
    ve, na = d["le_verdict"], d["la_nappe_entiere"]
    c208 = d["le_triangle_contre_208"]
    p210, p211 = d["ce_que_210_a_rendu"], d["ce_que_211_a_rendu"]
    demi = float(d["le_demi_pli_en_voxels"])
    cibles = int(q["les_coutures_dune_rangee"])
    lie_accord = ve.get("le_budget_qui_lie") == "s'accorder"

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"demi-feuillet {_fr(demi, 0)} voxels · pli {_fr(d['le_pas_dun_pli_en_voxels'], 4)} · "
           f"une rangée porte {cibles} coutures · {p210.get('les_rangees_moyennees')} rangées "
           f"moyennées · aucune épreuve déclarée, aucun échantillon tiré", petit, GRIS)

    # ---- panneau 1 : l'équation de conception, dessinée
    x0, y0, pw, ph = 56, 122, 1248, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "l'écart attendu croît comme la racine des coutures — le croisement EST la longueur "
           "tenable", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 54, y0 + 18, pw - 404, 232
    courbes = []
    for nom, etiquette, coul in (
            ("le_plancher_de_la_matiere", "plancher de la matière", GRIS),
            ("une_rangee_seule", "une rangée seule", GRIS),
            ("la_moyenne_des_rangees",
             f"la moyenne de {p210.get('les_rangees_moyennees')} rangées", CONTRE)):
        x = b["traverser"][nom]
        courbes.append((etiquette, float(x["la_dispersion_en_voxels"]),
                        float(x["la_longueur_tenable_en_coutures"]), coul))
    for cle in sorted(b["saccorder"]):
        x = b["saccorder"][cle]
        courbes.append((f"désaccord {cle}", float(x["la_dispersion_en_voxels"]),
                        float(x["la_longueur_tenable_en_coutures"]), ALERTE))
    n_haut = max(max(n for _e, _s, n, _c in courbes), float(cibles)) * 1.14
    # ⚠⚠⚠ L'ECHELLE VERTICALE SUIT LES COURBES ET NON LE DEMI-FEUILLET. Une premiere version
    # posait `y_haut = demi * 1.55`, donc la bande du demi-feuillet retombait TOUJOURS au meme
    # pixel quelle que soit la constante publiee — une garde qui ne pouvait pas echouer, et c'est
    # la sonde qui l'a dit.
    y_haut = max(demi * 1.25,
                 max(s_ for _e, s_, _n, _c in courbes) * (n_haut ** 0.5))
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 44, yy - 6, _fr(y_haut * (1.0 - k / 4.0), 0), 0, GRIS)
    yb = gy0 + gh * (1.0 - demi / y_haut)
    for s in range(0, int(gw), 12):
        art.line([gx0 + s, yb, gx0 + min(s + 6, int(gw)), yb], fill=ALERTE, width=2)
    traits.append((gx0, yb, gx0 + gw))
    ecrire(gx0 + 6, yb - 16, f"le demi-feuillet : {_fr(demi, 0)} voxels", 0, ALERTE)
    xr = gx0 + gw * float(cibles) / n_haut
    art.line([xr, gy0, xr, gy0 + gh], fill=ENCRE, width=2)
    traits.append((gy0, xr, gy0 + gh))
    ecrire(xr - 96, gy0 + gh + 10, f"une rangée entière : {cibles} coutures", 0, ENCRE)
    for etiquette, sigma, n_max, coul in courbes:
        prec = None
        for i in range(0, 121):
            n = n_haut * i / 120.0
            px = gx0 + gw * n / n_haut
            py = gy0 + gh * (1.0 - min(sigma * (n ** 0.5), y_haut) / y_haut)
            if prec is not None:
                art.line([prec[0], prec[1], px, py], fill=coul, width=2)
            points.append((px, py))
            prec = (px, py)
        cx = gx0 + gw * min(n_max, n_haut) / n_haut
        art.ellipse([cx - 4, yb - 4, cx + 4, yb + 4], fill=coul)
        points.append((cx, yb))
    # ⚠⚠ LES DEUX FAMILLES SONT NOMMEES DANS LE GRAPHE, sinon l'oeil voit six courbes et ne peut
    # en rattacher aucune a un budget : la legende de droite donne les nombres, pas la forme. Vu
    # en REGARDANT l'image, par aucune garde. Les deux hauteurs sont DERIVEES des dispersions
    # tracees, donc elles suivent la mesure au lieu d'etre posees en pixels.
    n_lab = n_haut * 0.62
    s_acc = max(float(b["saccorder"][c]["la_dispersion_en_voxels"]) for c in b["saccorder"])
    s_tra = min(float(b["traverser"][c]["la_dispersion_en_voxels"]) for c in b["traverser"])
    y_acc = gy0 + gh * (1.0 - min(s_acc * (n_lab ** 0.5) * 1.10, y_haut) / y_haut)
    y_tra = gy0 + gh * (1.0 - (s_tra * (n_lab ** 0.5) * 0.78) / y_haut)
    ecrire(gx0 + gw * 0.62, y_acc - 14, "S'ACCORDER — deux rangées", 0, ALERTE)
    ecrire(gx0 + gw * 0.62, y_tra, "TRAVERSER — une nappe", 0, CONTRE)
    ecrire(gx0 + gw / 2 - 74, gy0 + gh + 24, "les coutures d'une marche", 0, GRIS)
    lx = x0 + pw - 330
    ecrire(lx, y0 + 16, "LA LONGUEUR TENABLE, PAR BUDGET", moyen, ENCRE)
    for k, (etiquette, sigma, n_max, coul) in enumerate(courbes):
        yy = y0 + 44 + k * 20
        ecrire(lx, yy, etiquette, 0, coul)
        ecrire(lx + 176, yy, f"{_fr(sigma, 4)} vx", 0, coul)
        ecrire(lx + 244, yy, f"{_fr(n_max, 2)}", 0, coul)
    ecrire(lx, y0 + 180, "★ L'ÉQUATION NE PORTE AUCUNE CONSTANTE : poser", petit, GRIS)
    ecrire(lx, y0 + 194, "l'écart attendu de `207` égal au demi-feuillet et", petit, GRIS)
    ecrire(lx, y0 + 208, "résoudre rend le carré du rapport. Le demi-feuillet", petit, GRIS)
    ecrire(lx, y0 + 222, "n'est pas un seuil : c'est la distance à laquelle la", petit, GRIS)
    ecrire(lx, y0 + 236, "surface saute au feuillet voisin.", petit, GRIS)
    ecrire(lx, y0 + 258, "⚠ Une longueur tenable est une ÉCHELLE, pas une", petit, ALERTE)
    ecrire(lx, y0 + 272, "promesse : à cette longueur, la moitié des courses", petit, ALERTE)
    ecrire(lx, y0 + 286, "sortent déjà.", petit, ALERTE)

    # ---- panneau 2 : le triangle des bruits propres
    x0, y0, pw, ph = 56, 474, 400, 238
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le triangle des bruits propres, et `208`", moyen, ENCRE)
    bruits = tri["les_bruits_propres"]
    haut_b = max(float(x["le_bruit_propre_en_voxels"]) for x in bruits.values()) * 1.3
    for k, r in enumerate(sorted(bruits, key=int)):
        x = bruits[r]
        yy = y0 + 12 + k * 30
        ecrire(x0 + 12, yy, f"rangée {r}", 0, ENCRE)
        ecrire(x0 + 96, yy, f"{_fr(x['le_bruit_propre_en_voxels'], 4)} vx", 0, CONTRE)
        cmp_ = (c208.get("les_rangees_comparees") or {}).get(r)
        if cmp_:
            ecrire(x0 + 190, yy,
                   f"`208` en donnait {_fr(cmp_['selon_208_en_voxels'], 4)}", 0, GRIS)
        barre(x0 + 12, yy + 14, 372, float(x["le_bruit_propre_en_voxels"]) / haut_b, 6, CONTRE)
    ecrire(x0 + 12, y0 + 106,
           f"★ LE MODÈLE TIENT : {tri['le_modele_tient']}", moyen, BON)
    ecrire(x0 + 12, y0 + 130, "Trois désaccords, trois inconnues : le système est", petit, GRIS)
    ecrire(x0 + 12, y0 + 144, "exactement déterminé, et rien ne garantit que sa", petit, GRIS)
    ecrire(x0 + 12, y0 + 158, "solution soit faite de variances positives. Une seule", petit, GRIS)
    ecrire(x0 + 12, y0 + 172, "négative réfute — c'est une inégalité sur la matière.", petit, GRIS)
    ecrire(x0 + 12, y0 + 194,
           f"⚠⚠ Mais il ne recoupe pas `208` : écart jusqu'à", petit, ALERTE)
    ecrire(x0 + 12, y0 + 208,
           f"{_fr(c208.get('le_plus_grand_ecart_en_voxels'), 4)} voxel. La décomposition d'une "
           f"paire", petit, ALERTE)
    ecrire(x0 + 12, y0 + 222, "suppose ce que le triangle n'a pas à supposer.", petit, ALERTE)

    # ---- panneau 3 : ce qu'une rangée entière demande
    x0, y0, pw, ph = 480, 474, 400, 238
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, f"ce qu'une rangée de {cibles} coutures demande", moyen, ENCRE)
    for k, (nom, part, coul) in enumerate((
            ("en traversant", q["la_part_couverte_en_traversant"], CONTRE),
            ("en s'accordant", q["la_part_couverte_en_saccordant"], ALERTE))):
        yy = y0 + 14 + k * 46
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 140, yy, f"{_fr(part, 4)} de la rangée", 0, coul)
        barre(x0 + 12, yy + 16, 372, float(part), 10, coul)
        art.line([x0 + 12 + 372, yy + 14, x0 + 12 + 372, yy + 30], fill=ENCRE, width=2)
        traits.append((yy + 14, x0 + 12 + 372, yy + 30))
    ecrire(x0 + 12, y0 + 112,
           f"{'★' if q['une_rangee_entiere_traverse'] else '✗'} une rangée entière TRAVERSE : "
           f"{q['une_rangee_entiere_traverse']}", moyen,
           BON if q["une_rangee_entiere_traverse"] else ALERTE)
    ecrire(x0 + 12, y0 + 136,
           f"{'★' if q['une_rangee_entiere_saccorde'] else '✗'} une rangée entière S'ACCORDE : "
           f"{q['une_rangee_entiere_saccorde']}", moyen,
           BON if q["une_rangee_entiere_saccorde"] else ALERTE)
    ecrire(x0 + 12, y0 + 166,
           f"il manque {_fr(q['les_coutures_qui_manquent_pour_saccorder'], 2)} coutures pour "
           f"qu'elle", petit, ENCRE)
    ecrire(x0 + 12, y0 + 180, "s'accorde d'un bout à l'autre.", petit, ENCRE)
    ecrire(x0 + 12, y0 + 202, "⚠ Et le PLANCHER de la matière ne suffit pas non", petit, GRIS)
    ecrire(x0 + 12, y0 + 216,
           f"plus : {_fr(b['traverser']['le_plancher_de_la_matiere']['la_longueur_tenable_en_coutures'], 2)} "
           f"coutures pour un lecteur PARFAIT.", petit, GRIS)

    # ---- panneau 4 : le verdict
    x0, y0, pw, ph = 904, 474, 400, 238
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "lequel des deux lie, et de combien", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 12,
           f"{'✗' if lie_accord else '★'} LE BUDGET QUI LIE : {ve['le_budget_qui_lie']}", moyen,
           ALERTE if lie_accord else BON)
    for k, (nom, valeur) in enumerate((
            ("en traversant",
             f"{_fr(ve['la_longueur_tenable_en_traversant_en_coutures'], 2)} coutures"),
            ("en s'accordant",
             f"{_fr(ve['la_longueur_tenable_en_saccordant_en_coutures'], 2)} coutures"),
            ("la pire paire", str(ve["la_pire_paire"])),
            ("le rapport des deux", _fr(ve["le_rapport_des_deux_budgets"], 4)),
            ("ce que le liant coûte",
             f"{_fr(ve['ce_que_le_budget_liant_coute_en_coutures'], 2)} coutures"))):
        yy = y0 + 42 + k * 18
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 184, yy, valeur, 0, ENCRE)
    ecrire(x0 + 12, y0 + 142,
           f"★ LA HAUTEUR EST GRATUITE : "
           f"{na['la_hauteur_est_gratuite_sous_le_modele']}", moyen, BON)
    ecrire(x0 + 12, y0 + 166, "Le désaccord de la première et de la dernière", petit, GRIS)
    ecrire(x0 + 12, y0 + 180, "rangée d'une bande ne fait intervenir que ces", petit, GRIS)
    ecrire(x0 + 12, y0 + 194, "deux-là : les rangées du milieu n'y entrent pas.", petit, GRIS)
    ecrire(x0 + 12, y0 + 206, "⚠⚠ Sous le MODÈLE, et il reste à le mettre à", petit, ALERTE)
    ecrire(x0 + 12, y0 + 220, "l'épreuve sur des rangées ÉLOIGNÉES.", petit, ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{'✗' if lie_accord else '★'}  C'EST S'ACCORDER QUI LIE, ET PAS TRAVERSER : "
           f"{_fr(ve['la_longueur_tenable_en_saccordant_en_coutures'], 2)} coutures contre "
           f"{_fr(ve['la_longueur_tenable_en_traversant_en_coutures'], 2)}, soit un rapport de "
           f"{_fr(ve['le_rapport_des_deux_budgets'], 4)}.", moyen, ALERTE if lie_accord else BON)
    ecrire(78, y + 40,
           f"     Donc améliorer la traversée n'achète RIEN tant que l'accord n'a pas bougé : "
           f"le budget liant coûte "
           f"{_fr(ve['ce_que_le_budget_liant_coute_en_coutures'], 2)} coutures de nappe.", moyen,
           ENCRE)
    ecrire(78, y + 70,
           f"★  L'ÉQUATION DE CONCEPTION EST L'INVERSE DE LA CONVENTION DE `207` : une marche de "
           f"n coutures s'écarte de sigma fois la racine de n, donc elle quitte", moyen, BON)
    ecrire(78, y + 92,
           f"     le feuillet à n = (demi-feuillet / sigma) au carré. Aucune constante, aucun "
           f"seuil choisi — et un seul nombre par budget, comparable à une rangée.", moyen, ENCRE)
    ecrire(78, y + 122,
           f"{'★' if q['une_rangee_entiere_traverse'] else '✗'}  UNE RANGÉE ENTIÈRE TRAVERSE "
           f"({_fr(q['la_part_couverte_en_traversant'], 4)} de couverture) MAIS NE S'ACCORDE PAS "
           f"({_fr(q['la_part_couverte_en_saccordant'], 4)}) : il lui manque", moyen,
           BON if q["une_rangee_entiere_traverse"] else ALERTE)
    ecrire(78, y + 144,
           f"     {_fr(q['les_coutures_qui_manquent_pour_saccorder'], 2)} coutures. Et le "
           f"plancher de la matière n'y suffirait pas non plus : "
           f"{_fr(b['traverser']['le_plancher_de_la_matiere']['la_longueur_tenable_en_coutures'], 2)} "
           f"coutures pour un lecteur PARFAIT.", moyen, ENCRE)
    ecrire(78, y + 174,
           f"★  LE TRIANGLE NE RÉFUTE PAS LE MODÈLE — les trois variances propres sortent "
           f"positives — DONC LA HAUTEUR EST GRATUITE :", moyen, BON)
    ecrire(78, y + 196,
           f"     une nappe entière ne s'écarte pas plus qu'une paire. ⚠⚠ Sous le modèle, et il "
           f"reste à mesurer {na['ce_qui_reste_a_mesurer']}.", moyen, GRIS)

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

    import copy  # noqa: PLC0415

    def _refuse(base, out, casse):
        faux_ = copy.deepcopy(base)
        casse(faux_)
        tmp_ = out.with_name(out.stem + "_sonde.json")
        tmp_.write_text(json.dumps(faux_), encoding="utf-8")
        try:
            lire(tmp_)
            return False
        except ValueError:
            return True
        finally:
            tmp_.unlink(missing_ok=True)

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(36.0, 0), _fr(0.05, 2), _fr(2.7138, 4)) == ("36", "0,05", "2,7138"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(2.7138, 4))}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:200])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:200])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("★★★★ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:200])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ★★★★ CHAQUE COURBE VIENT DE SA DISPERSION, ET SON CROISEMENT DE SA LONGUEUR TENABLE.
    for nom in ("la_moyenne_des_rangees", "une_rangee_seule", "le_plancher_de_la_matiere"):
        faux = copy.deepcopy(d)
        faux["les_budgets"]["traverser"][nom]["la_dispersion_en_voxels"] = 7.7777
        _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la courbe de « {nom} » vient de SA dispersion",
          [(round(x, 2), round(y, 2)) for x, y in ptk]
          != [(round(x, 2), round(y, 2)) for x, y in points])
        dessiner(d, sortie)
    for cle in sorted(d["les_budgets"]["saccorder"]):
        faux = copy.deepcopy(d)
        faux["les_budgets"]["saccorder"][cle]["la_longueur_tenable_en_coutures"] = 31.31
        _c, pk, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la longueur tenable de la paire {cle} est écrite",
          sum(1 for _x, _y, t, _f in pk if "31,31" in t) >= 1)
        dessiner(d, sortie)

    # ★★★★ LA BANDE DU DEMI-FEUILLET ET LA LARGEUR D'UNE RANGEE SONT TRACEES DEPUIS LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_demi_pli_en_voxels"] = 12
    _c, _p, _cd, _pt, _b, tr_c = dessiner(faux, sortie)
    v("★★★★ la bande du demi-feuillet suit la constante que la mesure publie",
      [round(y, 2) for _a, y, _b in tr_c] != [round(y, 2) for _a, y, _b in traits],
      f"{len(tr_c)} traits")
    faux = copy.deepcopy(d)
    faux["ce_quune_rangee_demande"]["les_coutures_dune_rangee"] = 717
    _c, pr_, _cd, _pt, _b, trr = dessiner(faux, sortie)
    v("★★★★ la largeur d'une rangée entière est TRACÉE et écrite",
      sum(1 for _x, _y, t, _f in pr_ if "717" in t) >= 2
      and [round(y, 2) for _a, y, _b in trr] != [round(y, 2) for _a, y, _b in traits])
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, valeur, dec_, combien in (
            (("le_verdict", "la_longueur_tenable_en_traversant_en_coutures"), 414.14, 2, 2),
            (("le_verdict", "la_longueur_tenable_en_saccordant_en_coutures"), 161.61, 2, 2),
            (("le_verdict", "le_rapport_des_deux_budgets"), 0.3131, 4, 2),
            (("le_verdict", "ce_que_le_budget_liant_coute_en_coutures"), 191.91, 2, 2),
            (("ce_quune_rangee_demande", "la_part_couverte_en_traversant"), 1.7171, 4, 2),
            (("ce_quune_rangee_demande", "la_part_couverte_en_saccordant"), 0.4141, 4, 2),
            (("ce_quune_rangee_demande", "les_coutures_qui_manquent_pour_saccorder"),
             131.31, 2, 2),
            (("le_triangle_contre_208", "le_plus_grand_ecart_en_voxels"), 0.8181, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = valeur
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2 if _fr(valeur, dec_) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LE TRIANGLE EST DESSINE RANGEE PAR RANGEE, AVEC CE QUE `208` EN DISAIT.
    for r in sorted(d["le_triangle"]["les_bruits_propres"], key=int):
        faux = copy.deepcopy(d)
        faux["le_triangle"]["les_bruits_propres"][r]["le_bruit_propre_en_voxels"] = 6.1616
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le bruit propre de la rangée {r} est écrit",
          sum(1 for _x, _y, t, _f in p3 if "6,1616" in t) >= 1)
        dessiner(d, sortie)
    r0 = sorted(d["le_triangle_contre_208"]["les_rangees_comparees"], key=int)[0]
    faux = copy.deepcopy(d)
    faux["le_triangle_contre_208"]["les_rangees_comparees"][r0]["selon_208_en_voxels"] = 5.1515
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ ce que `208` donnait est écrit à côté, sinon l'écart ne se lit pas",
      sum(1 for _x, _y, t, _f in p4 if "5,1515" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ CE QUI RESTE A MESURER EST DESSINE : une conclusion trop belle qui ne nommerait pas
    # sa condition serait la faute que cette tranche existe pour éviter.
    faux = copy.deepcopy(d)
    faux["la_nappe_entiere"]["ce_qui_reste_a_mesurer"] = "un sanglier bleu"
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ ce qui reste à mesurer est ÉCRIT dans la figure",
      sum(1 for _x, _y, t, _f in p5 if "un sanglier bleu" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_budget_qui_lie"] = "traverser"
    v("★★★★ un budget de traversée qui lie change le titre",
      "c'est TRAVERSER qui lie" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["le_budget_qui_lie"] = "s'accorder"
    faux["le_verdict"]["une_rangee_entiere_saccorde"] = True
    v("★★★★ une rangée qui tient dans les deux le dit autrement",
      "tient dans les deux budgets" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["une_rangee_entiere_saccorde"] = False
    v("★★★ et une rangée qui n'y tient pas le dit encore autrement",
      "n'y tient pas" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x.__setitem__("les_epreuves_declarees", ["une épreuve"]),
             "qui déclare une épreuve alors qu'aucun échantillon n'est tiré"),
            (lambda x: x["le_triangle"].__setitem__("le_modele_tient", False),
             "dont le triangle RÉFUTE le modèle"),
            (lambda x: x["le_triangle"].__setitem__("les_bruits_propres", {"1": {}}),
             "dont le triangle ne porte pas trois rangées"),
            (lambda x: x["les_budgets"].__setitem__("decidable", False),
             "aux budgets indécidables"),
            (lambda x: x["les_budgets"].__setitem__("saccorder", {}),
             "sans aucune paire budgétée"),
            (lambda x: x["les_budgets"].__setitem__(
                "saccorder", {"1-2": {"decidable": True}}),
             "avec moins de trois paires budgétées"),
            (lambda x: x["les_budgets"]["traverser"]["le_plancher_de_la_matiere"].__setitem__(
                "decidable", False),
             "sans le plancher que la matière impose"),
            (lambda x: x["les_budgets"].__setitem__("le_budget_qui_lie", "je ne sais pas"),
             "dont le budget qui lie n'est pas nommé"),
            (lambda x: x["ce_quune_rangee_demande"].__setitem__(
                "les_coutures_dune_rangee", None),
             "sans la largeur d'une rangée entière"),
            (lambda x: x["la_nappe_entiere"].__setitem__("ce_qui_reste_a_mesurer", "  "),
             "qui ne nomme pas ce qui reste à mesurer"),
            (lambda x: x["le_verdict"].__setitem__("decidable", False),
             "au verdict indécidable"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_le_budget_de_la_nappe.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_budget_de_la_nappe.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "212_le_budget_de_la_nappe.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
