"""Moyenner le creux sur les sous-colonnes d'un chunk réduit-il son bruit ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la courbe par découpage avec la CIBLE
tracée en travers : la dérive que `202` a mesurée. L'aléa doit passer dessous, et la figure montre
s'il y arrive. En bas à gauche, la prédiction posée AVANT la mesure — combien de lectures il faut,
combien la géométrie en offre. Au centre, l'épreuve et son nul d'un demi démontré. À droite, les
deux bornes du contrôle croisé et l'étalon.

  uv run python src/figures/figure_moyenner_le_creux_reduit_il_son_bruit.py \\
      --json docs/mesures/moyenner_le_creux_reduit_il_son_bruit.json \\
      --sortie docs/images/205_moyenner_le_creux_reduit_il_son_bruit.png
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
PROFOND = (128, 86, 124)


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
    """Le JSON de `moyenner_le_creux_reduit_il_son_bruit.py`.

    ⚠⚠⚠ REFUSE UNE MESURE SANS PRÉDICTION, UNE DONT L'ÉTALON NE SÉPARE PAS, UNE QUI DÉCLARE PLUS
    D'UNE ÉPREUVE SANS EN DIVISER LA GARANTIE, ET UNE DONT UN BARREAU N'A PAS LA DISPERSION DU PAS :
    `203` a payé qu'un critère aveugle à la dynamique récompense un instrument mort.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_courbe", "lepreuve", "le_verdict", "letalon", "la_prediction",
                "lechelle_des_decoupages"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_courbe", "lepreuve", "le_verdict", "letalon", "la_prediction",
                "lechelle_des_decoupages"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    for b in d["la_courbe"]["les_barreaux"]:
        for cle in ("lalea_en_voxels", "lalea_predit_en_voxels",
                    "la_dispersion_du_pas_en_voxels"):
            if b.get(cle) is None:
                raise ValueError(
                    f"{chemin} : le barreau {b.get('les_sous_colonnes')} n'a pas {cle}")
    if d["le_verdict"].get("la_derive_visee_par_202_en_voxels") is None:
        raise ValueError(f"{chemin} : la dérive visée par `202` est absente")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if ve.get("le_bruit_est_il_passe_sous_la_derive"):
        return ("Moyenner le creux — le bruit passe sous la dérive, le repère absolu devient "
                "utilisable")
    if not ve.get("la_couture_porte_un_pas"):
        return "Moyenner le creux — la couture ne porte toujours aucun pas lisible"
    return "Moyenner le creux — le bruit descend, et pas assez : la voie reste fermée"


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

    lg, cb, ep = d["la_ligne"], d["la_courbe"], d["lepreuve"]
    ve, e, pr = d["le_verdict"], d["letalon"], d["la_prediction"]
    ec, po = d["lechelle_des_decoupages"], d.get("la_portee") or {}
    bar = cb["les_barreaux"]
    cible = float(ve["la_derive_visee_par_202_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · chunk de "
           f"{lg['le_cote_du_chunk_en_pixels']} px de côté · "
           f"{d['les_coutures_voisines']} coutures · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : la courbe par découpage, avec la CIBLE en travers
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "ce que chaque découpage rend — et la cible que `202` a posée", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 14, pw - 396, 210
    haut = max(max(x["la_dispersion_du_pas_en_voxels"] for x in bar),
               max(x["lalea_en_voxels"] for x in bar),
               max(float(x.get("la_dispersion_dans_le_chunk_en_voxels") or 0.0) for x in bar),
               cible, 1.0) * 1.1
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 42, yy - 6, _fr(haut * (1.0 - k / 4.0), 1), 0, GRIS)
    yc = gy0 + gh * (1.0 - cible / haut)
    for s in range(0, int(gw), 12):
        art.line([gx0 + s, yc, gx0 + min(s + 6, int(gw)), yc], fill=BON, width=2)
    traits.append((gx0, yc, gx0 + gw))
    ecrire(gx0 + 6, yc - 16, f"la dérive du creux (`202`) : {_fr(cible, 4)} vx", 0, BON)
    n = max(1, len(bar) - 1)
    for cle, coul, pointille in (("la_dispersion_du_pas_en_voxels", CONTRE, False),
                                 ("la_dispersion_dans_le_chunk_en_voxels", PROFOND, False),
                                 ("lalea_en_voxels", ALERTE, False),
                                 ("lalea_predit_en_voxels", GRIS, True)):
        prec = None
        for i, b in enumerate(bar):
            val = b.get(cle)
            if val is None:
                prec = None
                continue
            px = gx0 + gw * i / n
            py = gy0 + gh * (1.0 - float(val) / haut)
            if prec is not None and not pointille:
                art.line([prec[0], prec[1], px, py], fill=coul, width=2)
            elif prec is not None:
                for s in range(0, 10, 2):
                    a_ = (prec[0] + (px - prec[0]) * s / 10.0,
                          prec[1] + (py - prec[1]) * s / 10.0)
                    b_ = (prec[0] + (px - prec[0]) * (s + 1) / 10.0,
                          prec[1] + (py - prec[1]) * (s + 1) / 10.0)
                    art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=1)
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            points.append((px, py))
            prec = (px, py)
    for i, b in enumerate(bar):
        ecrire(gx0 + gw * i / n - 10, gy0 + gh + 8, str(b["les_sous_colonnes"]), 0, GRIS)
    ecrire(gx0 + gw / 2 - 66, gy0 + gh + 26, "sous-colonnes moyennées", 0, GRIS)
    lx = x0 + pw - 322
    for k, (nom, coul) in enumerate(
            (("la DISPERSION du pas lu", CONTRE),
             ("la dispersion DANS le chunk", PROFOND), ("l'ALÉA mesuré", ALERTE),
             ("l'aléa PRÉDIT en racine de k", GRIS),
             ("la CIBLE : la dérive de `202`", BON))):
        art.rectangle([lx, y0 + 18 + k * 22, lx + 22, y0 + 26 + k * 22], fill=coul)
        ecrire(lx + 30, y0 + 16 + k * 22, nom, 0, coul)
    passe = bool(ve.get("le_bruit_est_il_passe_sous_la_derive"))
    ecrire(lx, y0 + 134,
           f"{'★' if passe else '✗'} L'ALÉA PASSE SOUS LA CIBLE : {passe}", petit,
           BON if passe else ALERTE)
    ecrire(lx, y0 + 148,
           f"à {ve['les_sous_colonnes_de_lepreuve']} sous-colonnes l'aléa vaut "
           f"{_fr(ve['lalea_au_maximum_en_voxels'], 4)} voxels,", petit, ENCRE)
    ecrire(lx, y0 + 162,
           f"soit {_fr(ve['le_rapport_de_lalea_a_la_derive'], 4)} fois la dérive visée ; il part",
           petit, ENCRE)
    ecrire(lx, y0 + 176,
           f"de {_fr(ve['lalea_au_depart_en_voxels'], 4)} à {bar[0]['les_sous_colonnes']} "
           f"sous-colonnes.", petit, ENCRE)
    ecrire(lx, y0 + 198, "⚠⚠ DÉCOUPER N'EST PAS GRATUIT, ET ÇA SE MESURE :", petit, GRIS)
    ecrire(lx, y0 + 212,
           f"la dispersion DANS le chunk MONTE de "
           f"{_fr(bar[0].get('la_dispersion_dans_le_chunk_en_voxels'), 4)}", petit, GRIS)
    ecrire(lx, y0 + 226,
           f"à {_fr(bar[-1].get('la_dispersion_dans_le_chunk_en_voxels'), 4)} voxels pendant que "
           f"l'aléa descend.", petit, GRIS)
    ecrire(lx, y0 + 244, "⚠ La loi en racine de k n'est PAS l'épreuve : c'est", petit, GRIS)
    ecrire(lx, y0 + 258, "l'erreur type d'une moyenne, donc la vérifier serait", petit, GRIS)
    ecrire(lx, y0 + 272, "une vérification incapable d'échouer.", petit, GRIS)

    # ---- panneau 2 : la prédiction, posée AVANT la mesure
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la prédiction, posée AVANT la mesure", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("bruit du creux (`202`)", f"{_fr(pr['le_bruit_du_creux_en_voxels'], 4)} vx"),
            ("dérive commune (`202`)", f"{_fr(pr['la_derive_commune_en_voxels'], 4)} vx"),
            ("leur rapport", _fr(pr["le_rapport_du_bruit_a_la_derive"], 4)),
            ("rapport des variances", _fr(pr["le_rapport_des_variances"], 4)),
            ("lectures requises", f"{pr['les_lectures_requises']}"),
            ("ce que la géométrie offre",
             f"{ec['le_plus_grand_compte_que_la_geometrie_offre']}"),
            ("découpages essayés", str(ec["les_comptes"])),
            ("côtés, en pixels", str(ec["les_cotes_des_sous_colonnes"])))):
        yy = y0 + 12 + k * 19
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 236, yy, val, 0, ENCRE)
    ouverte = bool(ec.get("la_voie_est_ouverte_avant_la_mesure"))
    ecrire(x0 + 12, y0 + 170,
           f"{'★' if ouverte else '✗'} LA VOIE ÉTAIT OUVERTE AVANT DE MESURER : {ouverte}",
           moyen, BON if ouverte else ALERTE)
    ecrire(x0 + 12, y0 + 196,
           "★★★★ Le compte requis est le CARRÉ du rapport, pris", petit, GRIS)
    ecrire(x0 + 12, y0 + 210,
           "par excès : l'écart-type d'une moyenne de k mesures", petit, GRIS)
    ecrire(x0 + 12, y0 + 224,
           "indépendantes vaut le leur divisé par la racine de k.", petit, GRIS)
    ecrire(x0 + 12, y0 + 238,
           "Aucun réglage n'entre là-dedans.", petit, GRIS)

    # ---- panneau 3 : l'épreuve
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve, et son nul d'un demi DÉMONTRÉ", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("sous-colonnes moyennées", f"{ep['les_sous_colonnes']}"),
            ("coutures vues", f"{ep['les_coutures_vues']}"),
            ("coutures informatives", f"{ep['les_coutures_informatives']}"),
            ("qui portent un pas", f"{ep['les_coutures_qui_portent_un_pas']}"),
            ("seuil de la garantie", f"{ep['le_seuil_apparie']}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 300, yy, val, 0, ENCRE)
    part = float(ep["les_coutures_qui_portent_un_pas"]) / max(
        1.0, float(ep["les_coutures_informatives"]))
    barre(x0 + 12, y0 + 118, 372, part, 12, CONTRE)
    ecrire(x0 + 12, y0 + 138,
           f"soit {_fr(part, 4)} pour un nul d'un demi · P = {_fr(ep['la_valeur_p'], 7)}",
           0, ENCRE)
    porte = bool(ep["la_couture_porte_un_pas"])
    ecrire(x0 + 12, y0 + 160,
           f"{'★' if porte else '✗'} LA COUTURE PORTE UN PAS : {porte}", moyen,
           BON if porte else ALERTE)
    ecrire(x0 + 12, y0 + 188,
           "★ Le nul se DÉMONTRE : sans pas à lire, les deux", petit, GRIS)
    ecrire(x0 + 12, y0 + 202,
           "demi-moyennes sont deux tirages de même loi, donc", petit, GRIS)
    ecrire(x0 + 12, y0 + 216,
           "leur SOMME et leur DIFFÉRENCE sont identiquement", petit, GRIS)
    ecrire(x0 + 12, y0 + 230,
           "distribuées. Un demi exactement, sans réglage.", petit, GRIS)

    # ---- panneau 4 : les deux bornes du contrôle croisé, et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux bornes du contrôle croisé, et l'étalon", moyen, ENCRE)
    bornes = [("par le creux (`202`)", ve["la_derive_visee_par_202_en_voxels"], BON),
              ("par les rangées (`204`)", ve["la_derive_par_les_rangees_de_204_en_voxels"],
               CONTRE),
              (f"ici, à {ve['les_sous_colonnes_de_lepreuve']} sous-colonnes",
               ve["la_derive_au_maximum_en_voxels"], ALERTE)]
    hautD = max([abs(float(x[1])) for x in bornes if x[1] is not None] + [1.0]) * 1.15
    for k, (nom, val, coul) in enumerate(bornes):
        yy = y0 + 12 + k * 34
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 16, 372, (0.0 if val is None else abs(float(val)) / hautD), 8, coul)
    ecrire(x0 + 12, y0 + 116, "l'étalon — deux faces, sur réplicats", 0, GRIS)
    for k, (nom, val) in enumerate((
            ("dérive posée", f"{_fr(e['la_derive_posee_en_voxels'], 2)} vx"),
            ("dérive retrouvée", f"{_fr(e['la_derive_retrouvee_en_voxels'], 4)} vx"),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"))):
        yy = y0 + 138 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 232, yy, val, 0, ENCRE)
    barre(x0 + 12, y0 + 222, 372, float(e["la_part_trouvee"]), 10, BON)
    ecrire(x0 + 12, y0 + 236,
           f"★ sépare : {e['letalon_separe']} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    marque, coul = ("★", BON) if passe else ("✗", ALERTE)
    ecrire(78, y + 18,
           f"{marque}  LA PRÉDICTION DEMANDAIT {pr['les_lectures_requises']} LECTURES "
           f"INDÉPENDANTES, et la géométrie d'un chunk en offre "
           f"{ec['le_plus_grand_compte_que_la_geometrie_offre']} : la voie était OUVERTE avant "
           f"qu'un seul chunk ne soit lu.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     À {ve['les_sous_colonnes_de_lepreuve']} sous-colonnes l'aléa vaut "
           f"{_fr(ve['lalea_au_maximum_en_voxels'], 4)} voxels contre "
           f"{_fr(cible, 4)} visés — un rapport de "
           f"{_fr(ve['le_rapport_de_lalea_a_la_derive'], 4)}, donc "
           f"{'la cible est atteinte' if passe else 'la cible N’EST PAS atteinte'}.",
           moyen, coul)
    ecrire(78, y + 78,
           f"⚠⚠ ET LE DÉCOUPAGE SE PAIE : l'aléa part de "
           f"{_fr(ve['lalea_au_depart_en_voxels'], 4)} voxels à "
           f"{bar[0]['les_sous_colonnes']} sous-colonnes, là où la racine de k appliquée au bruit "
           f"de `202` en promettait {_fr(cb.get('ce_que_le_decoupage_coute_au_premier_barreau'), 4)} "
           f"fois moins.", moyen, GRIS)
    ecrire(78, y + 106,
           f"★★★★ ET CE QUI RESTE N'EST PAS UNE DÉRIVE : {_fr(ve['le_bruit_de_chunk_en_voxels'], 4)} "
           f"voxels d'erreur COMMUNE à toutes les sous-colonnes d'un chunk, qu'aucun découpage "
           f"n'atteint. Le bruit du creux", moyen, ENCRE)
    ecrire(78, y + 134,
           f"     tombe de {_fr(ve['le_bruit_de_202_en_voxels'], 4)} à "
           f"{_fr(ve['le_bruit_total_au_maximum_en_voxels'], 4)} voxels : moyenner "
           f"{ve['les_sous_colonnes_de_lepreuve']} sous-colonnes en laisse "
           f"{_fr(ve['ce_qui_reste_du_bruit_de_202'], 4)} en place.", moyen, ENCRE)
    ecrire(78, y + 162,
           f"{'★' if porte else '✗'}  L'ÉPREUVE : "
           f"{ep['les_coutures_qui_portent_un_pas']} coutures sur "
           f"{ep['les_coutures_informatives']} informatives portent un pas, pour un seuil de "
           f"{ep['le_seuil_apparie']} et un nul d'un demi DÉMONTRÉ · P = "
           f"{_fr(ep['la_valeur_p'], 7)}.", moyen, ENCRE)
    ecrire(78, y + 190,
           f"     Le contrôle croisé a deux bornes : {_fr(cible, 4)} voxels par le creux "
           f"(`202`) et {_fr(ve['la_derive_par_les_rangees_de_204_en_voxels'], 4)} par les "
           f"rangées (`204`) ; cette tranche en lit "
           f"{_fr(ve['la_derive_au_maximum_en_voxels'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 212,
           f"⚠ Les sous-colonnes d'un même chunk se calent parfois sur deux frontières séparées "
           f"d'un pli : {bar[-1]['les_sous_colonnes_repliees_dun_pli']} lectures ont dû être "
           f"repliées au plus grand découpage, comptées plutôt que lissées.", petit, GRIS)

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
      (_fr(64.0, 0), _fr(0.05, 2), _fr(3.4585, 4)) == ("64", "0,05", "3,4585"),
      f"{(_fr(64.0, 0), _fr(0.05, 2), _fr(3.4585, 4))}")
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

    # ★★★★ LES TROIS COURBES VIENNENT DE LA MESURE, BARREAU PAR BARREAU.
    for cle in ("lalea_en_voxels", "lalea_predit_en_voxels",
                "la_dispersion_du_pas_en_voxels"):
        for k in (0, len(d["la_courbe"]["les_barreaux"]) - 1):
            faux = copy.deepcopy(d)
            faux["la_courbe"]["les_barreaux"][k][cle] = 3.3131
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            v(f"★★★★ le barreau {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ LA CIBLE EST TRACEE DEPUIS LA MESURE, PAS POSEE DANS LA FIGURE.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["la_derive_visee_par_202_en_voxels"] = 12.3456
    _c, p_c, _cd, _pt, _b, tr_c = dessiner(faux, sortie)
    v("★★★★ la ligne de cible suit la dérive que `202` a publiée",
      [round(y, 2) for _a, y, _b in tr_c] != [round(y, 2) for _a, y, _b in traits],
      f"{len(tr_c)} traits")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "lalea_au_maximum_en_voxels"), 6.1616, 4, 2),
            (("le_verdict", "lalea_au_depart_en_voxels"), 8.1818, 4, 2),
            (("le_verdict", "la_derive_visee_par_202_en_voxels"), 9.6969, 4, 4),
            (("le_verdict", "le_rapport_de_lalea_a_la_derive"), 0.8181, 4, 2),
            (("le_verdict", "la_derive_par_les_rangees_de_204_en_voxels"), 7.4747, 4, 2),
            (("le_verdict", "la_derive_au_maximum_en_voxels"), 5.5151, 4, 2),
            (("lepreuve", "la_valeur_p"), 0.0303, 4, 2),
            (("lepreuve", "les_coutures_informatives"), 191, 0, 2),
            (("lepreuve", "les_coutures_qui_portent_un_pas"), 173, 0, 2),
            (("lepreuve", "le_seuil_apparie"), 111, 0, 2),
            (("la_prediction", "les_lectures_requises"), 77, 0, 2),
            (("la_prediction", "le_rapport_du_bruit_a_la_derive"), 4.2424, 4, 1),
            (("la_prediction", "le_rapport_des_variances"), 31.3131, 4, 1),
            (("le_verdict", "le_bruit_de_chunk_en_voxels"), 11.1717, 4, 1),
            (("le_verdict", "le_bruit_total_au_maximum_en_voxels"), 13.1313, 4, 1),
            (("le_verdict", "le_bruit_de_202_en_voxels"), 21.2121, 4, 1),
            (("letalon", "la_derive_retrouvee_en_voxels"), 7.1717, 4, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    for cle, val, combien in (("le_plus_grand_compte_que_la_geometrie_offre", 4141, 2),):
        faux = copy.deepcopy(d)
        faux["lechelle_des_decoupages"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ lechelle_des_decoupages.{cle} est lu autant de fois qu'il le faut",
          sum(1 for _x, _y, t, _f in p3 if str(val) in t) >= combien)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_bruit_est_il_passe_sous_la_derive"] = True
    v("★★★★ un bruit passé sous la dérive change le titre",
      "le repère absolu devient utilisable" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_bruit_est_il_passe_sous_la_derive"] = False
    faux["le_verdict"]["la_couture_porte_un_pas"] = False
    v("★★★★ une couture sans pas le dit autrement",
      "aucun pas lisible" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_bruit_est_il_passe_sous_la_derive"] = False
    faux["le_verdict"]["la_couture_porte_un_pas"] = True
    v("★★★ un pas lisible sous une cible non atteinte laisse la voie fermée",
      "la voie reste fermée" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_courbe"].__setitem__("decidable", False),
             "à la courbe indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["la_prediction"].__setitem__("decidable", False),
             "à la prédiction indécidable"),
            (lambda x: x["lechelle_des_decoupages"].__setitem__("decidable", False),
             "à l'échelle des découpages indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "la_dispersion_du_pas_en_voxels", None),
             "dont un barreau n'a pas la dispersion du pas"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "lalea_predit_en_voxels", None),
             "dont un barreau n'a pas l'aléa prédit"),
            (lambda x: x["le_verdict"].__setitem__("la_derive_visee_par_202_en_voxels", None),
             "sans la dérive visée par `202`"),
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
    dessiner(d, sortie)

    print(f"figure_moyenner_le_creux_reduit_il_son_bruit.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "moyenner_le_creux_reduit_il_son_bruit.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "205_moyenner_le_creux_reduit_il_son_bruit.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
