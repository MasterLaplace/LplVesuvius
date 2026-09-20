"""Le creux de cohérence borne-t-il la marche ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la trace absolue : la couche du creux,
colonne après colonne, avec la bande qu'un tirage au hasard remplirait. En bas à gauche, ce que
cette dispersion vaut contre l'uniforme. En bas au centre, les sauts d'un pli — le creux dit qu'il y
a une frontière, pas LAQUELLE. En bas à droite, la comparaison déclarée avec la marche de `199`, et
l'étalon.

  uv run python src/figures/figure_le_creux_borne_t_il_la_marche.py \\
      --json docs/mesures/le_creux_borne_t_il_la_marche.json \\
      --sortie docs/images/200_le_creux_borne_t_il_la_marche.png
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
    """Le JSON de `le_creux_borne_t_il_la_marche.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, ET UNE OÙ LA PROFONDEUR DU CUBE EST NULLE :
    sans la première, un silence rendu par un lecteur aveugle passerait pour un résultat ; sans la
    seconde, la borne de l'uniforme serait indéfinie et la dispersion observée ne se lirait pas. Ce
    second refus vient d'un défaut réel — la profondeur avait d'abord été lue dans une clef que le
    lecteur ne porte pas, et la mesure a rendu zéro.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_trace_absolue", "ce_que_199_a_rendu", "le_verdict", "letalon"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    t = d["la_trace_absolue"]
    if not t.get("decidable"):
        raise ValueError(f"{chemin} : la trace est indécidable")
    if not t.get("les_couches_du_cube") or not t.get("lecart_type_si_uniforme_en_voxels"):
        raise ValueError(f"{chemin} : la profondeur du cube est nulle, donc la borne de "
                         "l'uniforme est indéfinie")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : le verdict est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    if len(t["la_trace_en_couches"]) != len(t["les_colonnes"]):
        raise ValueError(f"{chemin} : la trace et ses colonnes ne sont pas de même longueur")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if d["le_verdict"].get("le_creux_borne_la_marche"):
        return "Le creux borne-t-il la marche ? — OUI, et il tient mieux que le voisinage"
    return ("Le creux borne-t-il la marche ? — il dit qu'il y a une frontière, "
            "jamais LAQUELLE")


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

    lg, t = d["la_ligne"], d["la_trace_absolue"]
    ve, d9, e = d["le_verdict"], d["ce_que_199_a_rendu"], d["letalon"]
    pli = float(d["le_pas_dun_pli_en_voxels"])
    prof = int(t["les_couches_du_cube"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · {lg['les_reperes_lisibles']} repères LISIBLES · "
           f"cube de {prof} couches · pli {_fr(pli, 4)} voxels · plancher de cohérence "
           f"{_fr(d['le_plancher_de_coherence'], 2)}", petit, GRIS)

    # ---- panneau 1 : la trace
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la couche du creux, colonne après colonne — lue dans chaque chunk SEUL", moyen,
           ENCRE)
    cols, trace = t["les_colonnes"], t["la_trace_en_couches"]
    gx0, gy0, gw, gh = x0 + 46, y0 + 16, pw - 92, 206
    cmin, cmax = float(min(cols)), float(max(cols))
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 40, yy - 6, f"{int(prof * (1.0 - k / 4.0))}", 0, GRIS)
    for c, v_ in zip(cols, trace):
        px = gx0 + gw * (float(c) - cmin) / max(1.0, cmax - cmin)
        py = gy0 + gh * (1.0 - float(v_) / max(1.0, float(prof)))
        art.ellipse([px - 2, py - 2, px + 2, py + 2], fill=CONTRE)
        points.append((px, py))
    ecrire(gx0, gy0 + gh + 8, f"colonne {int(cmin)}", 0, GRIS)
    ecrire(gx0 + gw - 80, gy0 + gh + 8, f"colonne {int(cmax)}", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 30,
           f"⚠⚠⚠ Les points remplissent la profondeur du cube : l'écart-type vaut "
           f"{_fr(t['lecart_type_en_voxels'], 4)} voxels quand un tirage AU HASARD dans "
           f"{prof} couches en donnerait {_fr(t['lecart_type_si_uniforme_en_voxels'], 4)}.",
           petit, ALERTE)

    # ---- panneau 2 : contre l'uniforme
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que cette dispersion vaut", moyen, ENCRE)
    hautU = max(float(t["lecart_type_en_voxels"]),
                float(t["lecart_type_si_uniforme_en_voxels"]), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("écart-type observé", t["lecart_type_en_voxels"], CONTRE),
             ("si la couche était tirée au hasard",
              t["lecart_type_si_uniforme_en_voxels"], GRIS))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, _fr(val, 4), 0, coul)
        barre(x0 + 12, yy + 16, 372, float(val) / hautU, 10, coul)
    ecrire(x0 + 12, y0 + 98,
           f"rapport à l'uniforme : {_fr(t['le_rapport_a_luniforme'], 4)}", moyen, ALERTE)
    ecrire(x0 + 12, y0 + 124,
           f"repères lisibles : {lg['les_reperes_lisibles']} sur {lg['colonnes_lues']} chunks lus",
           0, ENCRE)
    ecrire(x0 + 12, y0 + 150,
           "★ LE REPÈRE EXISTE PRESQUE PARTOUT — c'est la première", petit, ENCRE)
    ecrire(x0 + 12, y0 + 164,
           "moitié de ce que la porte demandait, et elle tient.", petit, ENCRE)
    ecrire(x0 + 12, y0 + 188,
           "⚠⚠⚠ MAIS SA COUCHE EST PRESQUE AUSSI DISPERSÉE QU'UN", petit, ALERTE)
    ecrire(x0 + 12, y0 + 202,
           "TIRAGE AU HASARD : il porte la PRÉSENCE d'une frontière,", petit, ALERTE)
    ecrire(x0 + 12, y0 + 216, "essentiellement pas sa POSITION.", petit, ALERTE)

    # ---- panneau 3 : les sauts
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les sauts — une frontière, mais laquelle ?", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("sauts de plus d'un demi-pli", f"{t['les_sauts_de_plus_dun_demi_pli']}"),
            ("sur des paires voisines", f"{t['les_reperes'] - 1}"),
            ("soit une part de", f"{_fr(t['la_part_qui_saute'], 6)}"),
            ("pas quadratique", f"{_fr(t['le_pas_quadratique_en_voxels'], 4)} voxels"),
            ("excursion de la trace", f"{t['lexcursion_en_voxels']} voxels"),
            ("… soit", f"{_fr(t['lexcursion_en_plis'], 6)} pli"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 250, yy, val, 0, ENCRE)
    barre(x0 + 12, y0 + 140, 372, float(t["la_part_qui_saute"]), 12, ALERTE)
    ecrire(x0 + 12, y0 + 162,
           "⚠⚠⚠ UN CREUX DÉSIGNE UNE FRONTIÈRE, PAS LAQUELLE. Deux", petit, ALERTE)
    ecrire(x0 + 12, y0 + 176,
           "chunks voisins peuvent se caler sur deux frontières", petit, ALERTE)
    ecrire(x0 + 12, y0 + 190,
           "séparées d'un pli, et plus d'un tiers des paires le font.", petit, ALERTE)
    ecrire(x0 + 12, y0 + 214,
           "⚠ Ces sauts sont COMPTÉS, jamais lissés : les replier", petit, GRIS)
    ecrire(x0 + 12, y0 + 228,
           "modulo un pli inventerait une continuité non mesurée.", petit, GRIS)

    # ---- panneau 4 : le verdict et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la comparaison déclarée avec `199`", moyen, ENCRE)
    hautV = max(float(ve["lexcursion_absolue_en_plis"]),
                float(ve["lexcursion_differentielle_en_plis"]), 0.1) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("excursion ABSOLUE (ce fichier)", ve["lexcursion_absolue_en_plis"], ALERTE),
             ("excursion différentielle (`199`)",
              ve["lexcursion_differentielle_en_plis"], CONTRE))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 310, yy, _fr(val, 6), 0, coul)
        barre(x0 + 12, yy + 16, 372, float(val) / hautV, 10, coul)
    borne = bool(ve["le_creux_borne_la_marche"])
    ecrire(x0 + 12, y0 + 98, f"rapport {_fr(ve['le_rapport'], 4)}", 0, ENCRE)
    ecrire(x0 + 12, y0 + 120,
           f"{'★' if borne else '✗'} LE CREUX "
           f"{'BORNE' if borne else 'NE BORNE PAS'} LA MARCHE.", moyen,
           BON if borne else ALERTE)
    ecrire(x0 + 12, y0 + 148, "l'étalon — deux faces, sur réplicats", 0, GRIS)
    for k, pt in enumerate(e["la_courbe"]):
        yy = y0 + 166 + k * 16
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 12, yy, f"bruit {_fr(pt['le_bruit'], 2)}", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 110, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 160, yy + 2, 220, part, 6, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 12, y0 + 234,
           f"★ sépare : {e['letalon_separe']} · faux {_fr(e['le_taux_de_faux'], 3)} pour "
           f"{_fr(e['la_garantie'], 2)}", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LE REPÈRE ABSOLU EXISTE, ET IL EST LISIBLE PRESQUE PARTOUT : "
           f"{lg['les_reperes_lisibles']} chunks sur {lg['colonnes_lues']} portent un creux que "
           f"leurs mélanges ne rendent pas.", moyen, ENCRE)
    ecrire(78, y + 46,
           "     C'était la première moitié de ce que `R4-P48` demandait, et elle tient.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  MAIS IL NE BORNE RIEN : son excursion vaut "
           f"{_fr(ve['lexcursion_absolue_en_plis'], 6)} pli contre "
           f"{_fr(ve['lexcursion_differentielle_en_plis'], 6)} pour la marche de proche en proche, "
           f"soit un rapport de {_fr(ve['le_rapport'], 4)} — il fait", moyen, ALERTE)
    ecrire(78, y + 106,
           f"     donc LÉGÈREMENT PIRE. Et sa couche est dispersée à "
           f"{_fr(t['le_rapport_a_luniforme'], 4)} de ce qu'un tirage au hasard dans "
           f"{prof} couches donnerait.", moyen, ALERTE)
    ecrire(78, y + 138,
           f"★★★★ LA RAISON EST MESURÉE, PAS SUPPOSÉE : un creux dit qu'il y a une frontière, "
           f"jamais LAQUELLE. {t['les_sauts_de_plus_dun_demi_pli']} paires voisines sur "
           f"{t['les_reperes'] - 1} se calent sur deux", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     frontières séparées d'un pli. Ce qui manque n'est donc pas un repère EN "
           f"PROFONDEUR — il est là — c'est de savoir COMPTER LES PLIS : un ordinal, pas une "
           f"position.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ Et {lg['refuses'].get('trop peu texturé', 0)} chunks sont écartés par le filtre du "
           f"producteur, {lg['refuses'].get('absent du dépôt', 0)} n'ont aucune surface : la "
           f"lecture porte sur ce qui reste.", petit, GRIS)

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

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(0.377049, 6), _fr(29.1153, 4)) == ("90", "0,377049", "29,1153"),
      f"{(_fr(90.0, 0), _fr(0.377049, 6), _fr(29.1153, 4))}")
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

    # ★★★★ LA TRACE DESSINEE VIENT DE LA MESURE, POINT PAR POINT.
    for k in (0, 100, len(d["la_trace_absolue"]["la_trace_en_couches"]) - 1):
        faux = copy.deepcopy(d)
        faux["la_trace_absolue"]["la_trace_en_couches"][k] = 3
        _c, _p, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le point {k} de la trace vient de la mesure", chemin.read_bytes() != octets)
        dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("la_trace_absolue", "lecart_type_en_voxels"), 13.75, 4, 2),
            (("la_trace_absolue", "lecart_type_si_uniforme_en_voxels"), 41.4141, 4, 2),
            (("la_trace_absolue", "le_rapport_a_luniforme"), 0.4242, 4, 2),
            (("la_trace_absolue", "les_sauts_de_plus_dun_demi_pli"), 177, 0, 2),
            (("la_trace_absolue", "lexcursion_en_plis"), 3.131313, 6, 1),
            (("le_verdict", "lexcursion_absolue_en_plis"), 2.727272, 6, 2),
            (("le_verdict", "lexcursion_differentielle_en_plis"), 1.818181, 6, 2),
            (("le_verdict", "le_rapport"), 7.4747, 4, 2)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n >= combien, f"{n} mentions pour {combien}")

    # ★★★★ LE COMPTE DE REPERES LISIBLES EST DESSINE DES DEUX COTES : c'est la moitie qui TIENT.
    faux = copy.deepcopy(d)
    faux["la_ligne"]["les_reperes_lisibles"] = 133
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de repères lisibles est lu des deux côtés",
      sum(1 for _x, _y, t, _f in p3 if "133" in t) >= 2)

    # ★★★ CHAQUE BARREAU DE L'ETALON PORTE SA PART.
    for k in (0, 3):
        faux = copy.deepcopy(d)
        faux["letalon"]["la_courbe"][k]["part_des_replicats"] = 0.6464 + k / 1e4
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part",
          any(_fr(0.6464 + k / 1e4, 3) in t for _x, _y, t, _f in p4))

    # ★★★★ LE TITRE SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_creux_borne_la_marche"] = True
    v("★★★★ un creux qui borne change le titre", "OUI, et il tient" in le_titre(faux),
      le_titre(faux))
    v("★★★ et l'observé dit l'inverse", "jamais LAQUELLE" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_trace_absolue"].__setitem__("les_couches_du_cube", 0),
             "dont la profondeur du cube est nulle"),
            (lambda x: x["la_trace_absolue"].__setitem__("decidable", False),
             "à la trace indécidable"),
            (lambda x: x["la_trace_absolue"]["les_colonnes"].pop(),
             "dont la trace et ses colonnes diffèrent"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        faux = copy.deepcopy(d)
        casse(faux)
        tmp = sortie.with_name(sortie.stem + "_sonde.json")
        tmp.write_text(json.dumps(faux), encoding="utf-8")
        refuse = False
        try:
            lire(tmp)
        except ValueError:
            refuse = True
        v(f"une mesure {quoi} est refusée", refuse)
        tmp.unlink(missing_ok=True)

    print(f"figure_le_creux_borne_t_il_la_marche.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_creux_borne_t_il_la_marche.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "200_le_creux_borne_t_il_la_marche.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
