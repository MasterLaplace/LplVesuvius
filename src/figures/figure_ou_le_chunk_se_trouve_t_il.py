"""Où le chunk se trouve-t-il, et est-ce que ça dit quelque chose ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon mesuré sur des RÉPLICATS
— et la même mesure à la configuration de `191`, qui dit que son étalon à un tirage pouvait passer
par chance. En haut à droite, les douze observables extrinsèques, avec le plancher en travers. En
bas à gauche, les deux nuls : le mélange libre et le mélange DANS chaque segment. En bas à droite,
intrinsèque contre extrinsèque, planchers et maxima côte à côte.

  uv run python src/figures/figure_ou_le_chunk_se_trouve_t_il.py \\
      --json docs/mesures/ou_le_chunk_se_trouve_t_il.json \\
      --sortie docs/images/193_ou_le_chunk_se_trouve_t_il.png
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
    """Le JSON de `ou_le_chunk_se_trouve_t_il.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE VOIT PAS SA COLONNE PORTEUSE À TOUS LES RÉPLICATS. C'est
    la réparation que cette tranche apporte à `191` : un étalon à tirage unique peut passer par
    chance, et le silence qu'il autorise ne veut alors rien dire.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "le_verdict", "le_nul_stratifie"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("letalon_separe_les_deux"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    if float(v.get("la_part_vue_avec_lingredient") or 0.0) < 1.0:
        raise ValueError(f"{chemin} : l'étalon ne voit pas à tous les réplicats")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if v.get("un_observable_separe"):
        nom = (v.get("le_meilleur") or {}).get("nom", "un observable")
        return f"Où le chunk se trouve-t-il ? — « {nom} » sépare"
    return (f"Où le chunk se trouve-t-il ? — AUCUN des {v.get('observables_declares')} observables "
            f"EXTRINSÈQUES ne sépare non plus")


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

    v, e = d["le_verdict"], d["letalon"]
    separe = bool(v.get("un_observable_separe"))
    coul_v = BON if separe else ALERTE
    signe = "★" if separe else "✗"
    meilleur = v.get("le_meilleur") or {}
    plancher = float(v.get("le_plancher_de_detection") or 0.0)
    strat = float(v.get("le_plancher_stratifie") or 0.0)
    figees = v.get("les_colonnes_constantes_par_segment") or []
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46,
           f"{v['chunks_qui_retiennent']} chunks qui retiennent sur {v['chunks_etiquetes']} "
           f"({v['venus_de_190']} de `190`, {v['venus_de_192']} de `192`, "
           f"{v['chunks_comptes_deux_fois']} comptés deux fois) · {v['observables_declares']} "
           f"observables EXTRINSÈQUES déclarés · {d['tirages']} mélanges · plancher "
           f"{_fr(plancher, 4)}", petit, GRIS)

    # ---- panneau 1 : l'étalon et la sensibilité
    x0, y0, pw, ph = 56, 122, 620, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon, mesuré sur des RÉPLICATS et non sur un tirage", moyen, ENCRE)
    for k, (nom, val, coul) in enumerate(
            (("une colonne qui PORTE l'étiquette est vue à",
              _fr(v.get("la_part_vue_avec_lingredient"), 4), BON),
             ("une liste de bruit pur sépare",
              str((e.get("rien_que_du_bruit") or {}).get("un_observable_separe")), GRIS),
             ("son maximum atteint",
              _fr((e.get("rien_que_du_bruit") or {}).get("la_separation_maximale"), 4), GRIS),
             ("pour un plancher de",
              _fr((e.get("rien_que_du_bruit") or {}).get("le_plancher_de_detection"), 4), GRIS))):
        yy = y0 + 14 + k * 20
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 350, yy, val, 0, coul)
    ecrire(x0 + 14, y0 + 106,
           "★ ET LA MÊME MESURE À LA CONFIGURATION DE `191`", moyen, ALERTE)
    for k, (nom, val) in enumerate(
            ((f"{v.get('chunks_de_191')} chunks, "
              f"{v.get('observables_intrinseques_de_191')} observables — vue à",
              _fr(v.get("la_part_vue_a_la_configuration_de_191"), 4)),)):
        ecrire(x0 + 14, y0 + 132, nom, 0, ALERTE)
        ecrire(x0 + 350, y0 + 132, val, 0, ALERTE)
    ecrire(x0 + 14, y0 + 156,
           "⚠⚠⚠ Son étalon était un TIRAGE UNIQUE, et une aire estimée sur six chunks", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 172,
           "contre quinze varie de près d'un dixième : il pouvait tomber du bon côté", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 188,
           "par chance. Cela ne change pas sa conclusion — elle n'avait rien trouvé —", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 204,
           "mais cela dit que son silence était moins lisible qu'il n'en avait l'air.", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 228,
           f"⚠ Le bruit de la porteuse vaut {_fr(e.get('bruit_de_la_porteuse'), 2)}, relu de `191` "
           f"et de `192`, jamais choisi ici.", petit, GRIS)

    # ---- panneau 2 : les observables extrinsèques
    x0, y0, pw, ph = 712, 122, 592, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les douze observables extrinsèques, du plus séparant au moins", moyen,
           ENCRE)
    tous = sorted(v.get("tous") or [], key=lambda y: -y["separation"])
    hautO = max([float(x["separation"]) for x in tous] + [plancher, 0.01]) * 1.12
    for k, x in enumerate(tous):
        yy = y0 + 8 + k * 17
        ecrire(x0 + 10, yy, _fr(x["separation"], 4), 0, ENCRE if k == 0 else GRIS)
        barre(x0 + 62, yy + 2, 96, float(x["separation"]) / hautO, 7,
              ENCRE if k == 0 else CONTRE)
        ecrire(x0 + 166, yy, f"aire {_fr(x['aire'], 4)}", 0, GRIS)
        marque = " (figée)" if x["nom"] in figees else ""
        ecrire(x0 + 250, yy, f"{x['nom']}{marque}"[:50], 0, ENCRE if k == 0 else GRIS)
    art.line([(x0 + 62 + 96 * plancher / hautO, y0 + 4),
              (x0 + 62 + 96 * plancher / hautO, y0 + 8 + 12 * 17)], fill=ALERTE, width=2)
    traits.append((x0 + 62 + 96 * plancher / hautO, y0 + 4, y0 + 8 + 12 * 17))
    ecrire(x0 + 10, y0 + 222,
           f"⚠ La barre verticale est le PLANCHER, {_fr(plancher, 4)} · « figée » = constante dans "
           f"un segment.", petit, ALERTE)

    # ---- panneau 3 : les deux nuls
    x0, y0, pw, ph = 56, 424, 620, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "deux nuls, parce que deux chunks d'un segment ne sont pas étrangers",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12,
           "Une permutation LIBRE suppose les chunks échangeables. Deux chunks d'un même", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 28,
           "segment partagent la matière, donc un second nul mélange l'étiquette DANS", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 44,
           "chaque segment, et il rend zéro pour toute colonne qui y est constante.", petit, ENCRE)
    hautN = max(plancher, strat, float(v.get("la_separation_maximale") or 0.0), 0.01) * 1.25
    for k, (nom, val, coul) in enumerate(
            (("le plancher du mélange LIBRE", plancher, GRIS),
             ("le plancher du mélange DANS chaque segment", strat, CONTRE),
             ("le maximum observé", v.get("la_separation_maximale"), ENCRE))):
        yy = y0 + 78 + k * 40
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 330, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 16, 570, float(val or 0.0) / hautN, 11, coul)
    ecrire(x0 + 14, y0 + 206,
           f"{signe} le maximum observé vaut {_fr(v.get('la_separation_maximale'), 4)}, sous les "
           f"DEUX planchers :", moyen, coul_v)
    ecrire(x0 + 14, y0 + 228,
           "     aucun observable extrinsèque ne sépare." if not separe
           else "     un observable extrinsèque sépare.", moyen, coul_v)
    ecrire(x0 + 14, y0 + 256,
           f"⚠⚠ {len(figees)} des {v['observables_declares']} colonnes sont constantes dans un "
           f"segment : le nul stratifié ne peut rien en dire,", petit, GRIS)
    ecrire(x0 + 14, y0 + 270,
           "et le taire laisserait croire qu'il les a jugées.", petit, GRIS)

    # ---- panneau 4 : intrinsèque contre extrinsèque
    x0, y0, pw, ph = 712, 424, 592, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "intrinsèque contre extrinsèque — deux recherches, deux prix", moyen,
           ENCRE)
    hautP = max(float(v.get("plancher_de_191") or 0.0),
                float(v.get("separation_maximale_de_191") or 0.0),
                plancher, float(v.get("la_separation_maximale") or 0.0), 0.01) * 1.2
    for k, (nom, val, coul) in enumerate(
            ((f"`191`, {v.get('observables_intrinseques_de_191')} observables INTRINSÈQUES sur "
              f"{v.get('chunks_de_191')} chunks — plancher", v.get("plancher_de_191"), ALERTE),
             ("     et son meilleur y atteignait", v.get("separation_maximale_de_191"), GRIS),
             (f"`193`, {v['observables_declares']} observables EXTRINSÈQUES sur "
              f"{v['chunks_etiquetes']} chunks — plancher", plancher, BON),
             ("     et son meilleur y atteint", v.get("la_separation_maximale"), CONTRE))):
        yy = y0 + 12 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 430, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 14, 480, float(val or 0.0) / hautP, 9, coul)
    ecrire(x0 + 14, y0 + 154,
           "★ Le plancher a presque MOITIÉ descendu, parce que le compte a quadruplé", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 170,
           "et que la liste est plus courte — et il n'y a toujours rien à voir.", petit, ENCRE)
    ecrire(x0 + 14, y0 + 194, f"le meilleur ici : « {meilleur.get('nom', '—')} »", 0, CONTRE)
    ecrire(x0 + 14, y0 + 210, f"son aire vaut {_fr(meilleur.get('aire'), 4)}", 0, CONTRE)
    for k, (nom, ok) in enumerate(
            (("l'étalon voit à tous les réplicats",
              float(v.get("la_part_vue_avec_lingredient") or 0.0) >= 1.0),
             ("les deux jeux d'étiquettes ne se recouvrent pas",
              int(v.get("chunks_comptes_deux_fois") or 0) == 0),
             ("un observable extrinsèque sépare", v.get("un_observable_separe")),
             ("et il sépare aussi dans chaque segment",
              v.get("un_observable_separe_aussi_dans_chaque_segment")))):
        yy = y0 + 232 + k * 14
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{signe}  NI L'INTRINSÈQUE NI L'EXTRINSÈQUE : `191` a cherché la texture d'un cube "
           f"parmi {v.get('observables_intrinseques_de_191')} observables et n'a rien trouvé ; "
           f"cette tranche cherche OÙ le cube se trouve,", moyen, coul_v)
    ecrire(78, y + 46,
           f"     là où son meilleur atteignait {_fr(v.get('separation_maximale_de_191'), 4)} "
           f"pour un plancher de {_fr(v.get('plancher_de_191'), 4)}, celui d'ici atteint "
           f"{_fr(v.get('la_separation_maximale'), 4)} pour un plancher de {_fr(plancher, 4)} "
           f"libre et de {_fr(strat, 4)} dans chaque segment.", moyen, coul_v)
    ecrire(78, y + 78,
           f"★  ET L'INSTRUMENT VOIT : une colonne qui porte l'étiquette est retrouvée à "
           f"{_fr(v.get('la_part_vue_avec_lingredient'), 4)} des {e.get('replicats')} réplicats, "
           f"et une liste de bruit pur ne rend rien. Le silence est lisible.", moyen, ENCRE)
    ecrire(78, y + 110,
           f"⚠⚠⚠  ET CELA CORRIGE UN CONTRÔLE DE `191` : à sa configuration — "
           f"{v.get('chunks_de_191')} chunks, {v.get('observables_intrinseques_de_191')} "
           f"observables — le même étalon n'est vu qu'à "
           f"{_fr(v.get('la_part_vue_a_la_configuration_de_191'), 4)} des réplicats.", moyen,
           ALERTE)
    ecrire(78, y + 138,
           "     Son étalon était un TIRAGE UNIQUE et pouvait passer par chance. Sa conclusion "
           "tient — elle n'avait rien trouvé — mais son silence était moins lisible", moyen,
           ALERTE)
    ecrire(78, y + 166,
           "     qu'il n'en avait l'air, et c'est `192`, sur soixante chunks neufs, qui a "
           "réellement tranché la piste qu'elle avait nommée.", moyen, ALERTE)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche ne dit pas : qu'il n'existe rien à mesurer. Elle dit que ni la "
           "texture d'un cube ni son adresse ne suffisent, avec les comptes dont on dispose.",
           petit, GRIS)

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
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(0.6, 2), _fr(0.1631, 4)) == ("90", "0,6", "0,1631"),
      f"{(_fr(90.0, 0), _fr(0.6, 2), _fr(0.1631, 4))}")
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
    # ⚠⚠⚠ UNE GARDE QUE `textes_hors_cadre` NE DONNE PAS : elle ne signale pas un texte qui COMMENCE
    # sous un cadre. Defaut vu en REGARDANT l'image de `190`.
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    v("★ le trait du plancher reste dans son panneau",
      all(712 <= x <= 1304 and 122 <= y0 <= y1 <= 372 for x, y0, y1 in traits), str(traits))
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    # ★★★★ LE MAXIMUM ET LES DEUX PLANCHERS SONT LUS DES DEUX COTES : c'est leur COMPARAISON qui est
    # le resultat, et l'un sans les autres ne dirait rien.
    for cle, val in (("la_separation_maximale", 0.3131), ("le_plancher_de_detection", 0.4646),
                     ("le_plancher_stratifie", 0.3737)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, 4) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ LA SENSIBILITE ET CELLE DE LA CONFIGURATION DE `191` SONT LUES DES DEUX COTES : c'est la
    # correction que la tranche apporte, et une seule mention la perdrait.
    for cle, val in (("la_part_vue_avec_lingredient", 0.9494),
                     ("la_part_vue_a_la_configuration_de_191", 0.1717)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        if cle == "la_part_vue_avec_lingredient":
            faux["le_verdict"]["la_part_vue_avec_lingredient"] = val
        try:
            _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        except Exception:  # noqa: BLE001
            p3 = []
        n = sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★ CE QUE `191` A RENDU EST LU DES DEUX COTES : sans lui, on ne verrait pas que le plancher a
    # descendu.
    for cle, val, dec in (("plancher_de_191", 0.4747, 4),
                          ("separation_maximale_de_191", 0.3838, 4),
                          ("chunks_de_191", 37, 0),
                          ("observables_intrinseques_de_191", 23, 0)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p4
                if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★ CHAQUE OBSERVABLE EST DESSINE AVEC SES DEUX LECTURES.
    for k in range(len(d["le_verdict"]["tous"])):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["tous"][k]["separation"] = 0.8101 + k / 1e4
        faux["le_verdict"]["tous"][k]["aire"] = 0.9101 + k / 1e4
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (0.8101 + k / 1e4, 0.9101 + k / 1e4)
                if any(_fr(m, 4) in t for _x, _y, t, _f in p5))
        v(f"★★★ l'observable {k} est dessiné avec ses deux lectures", n == 2, f"{n} sur 2")

    # ★★★★ UN ETALON QUI NE SEPARE PAS, OU QUI NE VOIT PAS A TOUS LES REPLICATS, FAIT REFUSER.
    import tempfile  # noqa: PLC0415

    for cle, val in (("letalon_separe_les_deux", False),
                     ("la_part_vue_avec_lingredient", 0.9)):
        rouge = copy.deepcopy(d)
        rouge["le_verdict"][cle] = val
        refuse, tmp = False, None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                json.dump(rouge, fh, ensure_ascii=False)
                tmp = Path(fh.name)
            lire(tmp)
        except ValueError:
            refuse = True
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
        v(f"★★★★ « {cle} » à {val} fait REFUSER la mesure", refuse)

    # ★★★★ LES DEUX BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for sep, attendu in ((True, "sépare"), (False, "AUCUN")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["un_observable_separe"] = sep
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p6, 1360) and not textes_hors_cadre(p6, cadres)
          and not textes_qui_se_recouvrent(p6))
    v("★★★★ les deux branches sont distinctes", len(set(branches)) == 2, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_ou_le_chunk_se_trouve_t_il.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "ou_le_chunk_se_trouve_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "193_ou_le_chunk_se_trouve_t_il.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
