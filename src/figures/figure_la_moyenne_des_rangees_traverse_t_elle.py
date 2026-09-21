"""La marche construite sur la moyenne des rangées du treillis traverse-t-elle vraiment ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LES DEUX TRACES SUPERPOSÉES — la marche
moyennée et celle d'une rangée seule sur LES MÊMES coutures — avec la bande du demi-feuillet en
travers. Le contrôle est apparié, donc l'œil voit le gain sans qu'aucune correction de longueur
n'entre. En bas à gauche, ce que la moyenne a retiré : la dispersion mesurée contre les deux bornes
posées d'avance. Au centre, les excursions prédites à la MÊME longueur. À droite, l'épreuve de
`199` et l'étalon.

  uv run python src/figures/figure_la_moyenne_des_rangees_traverse_t_elle.py \\
      --json docs/mesures/la_moyenne_des_rangees_traverse_t_elle.json \\
      --sortie docs/images/210_la_moyenne_des_rangees_traverse_t_elle.png
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
    """Le JSON de `la_moyenne_des_rangees_traverse_t_elle.py`.

    ⚠⚠⚠ LA REFUS QUI COMPTE EST CELUI DES DEUX TRACES DE LONGUEURS DIFFÉRENTES. Tout ce que cette
    tranche revendique tient à ce que le contrôle soit APPARIÉ : la rangée seule doit franchir
    EXACTEMENT les coutures que la marche moyennée franchit. Deux traces de longueurs différentes
    rendraient un gain qui mêle le bénéfice de la moyenne et la différence de longueur, et
    l'illustration le donnerait à lire comme un seul nombre.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_marche", "lepreuve", "le_verdict", "letalon", "la_prediction",
                "la_dispersion_predite", "ce_que_la_moyenne_a_retire",
                "les_predictions_a_la_meme_longueur", "les_rangees_du_treillis"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_marche", "lepreuve", "le_verdict", "letalon", "la_prediction",
                "la_dispersion_predite", "ce_que_la_moyenne_a_retire"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    m = d["la_marche"]
    a = m.get("le_cumul_moyenne_en_voxels") or []
    b = m.get("le_cumul_dune_rangee_seule_en_voxels") or []
    if len(a) < 2 or len(b) < 2:
        raise ValueError(f"{chemin} : une des deux traces est absente")
    if len(a) != len(b):
        raise ValueError(f"{chemin} : les deux traces n'ont pas la même longueur — le contrôle "
                         f"n'est pas apparié")
    if len(a) != int(m["les_coutures_du_troncon"]) + 1:
        raise ValueError(f"{chemin} : la trace ne porte pas un point de plus que de coutures")
    # ⚠⚠⚠ LE CONTROLE DOIT MARCHER SUR LA RANGEE DECLAREE, ET C'EST UN REFUS PARCE QUE LE DEFAUT
    # A EU LIEU : une premiere mesure a fait marcher la VOISINE `197` sous le nom de la rangee
    # seule, parce qu'un `sorted(...)[0]` rendait la plus petite clef. La figure aurait dessine le
    # bon trace sous la mauvaise legende, et c'est le recoupement avec `207` qui l'a dit.
    if int(m.get("la_rangee_seule", -1)) != int(d["les_rangees_du_treillis"]["la_mediane"]):
        raise ValueError(f"{chemin} : le contrôle marche sur la rangée "
                         f"{m.get('la_rangee_seule')} et non sur la médiane déclarée "
                         f"{d['les_rangees_du_treillis']['la_mediane']}")
    if d["ce_que_la_moyenne_a_retire"].get("lerreur_dechantillonnage_en_voxels") is None:
        raise ValueError(f"{chemin} : l'erreur d'échantillonnage de la dispersion est absente")
    if d["letalon"].get("le_plancher_de_202") is None:
        raise ValueError(f"{chemin} : l'étalon ne dit pas le plancher de `202` qu'il dépasse")
    for nom in ("loptimiste_de_208", "la_realiste_a_trois_lectures", "une_rangee_seule",
                "le_plancher_de_la_matiere"):
        x = (d["les_predictions_a_la_meme_longueur"] or {}).get(nom)
        if not x or not x.get("decidable"):
            raise ValueError(f"{chemin} : la prédiction « {nom} » manque")
    # ⚠⚠⚠ ET LES PREDICTIONS A TOUTES LES COUTURES SONT EXIGEES, PARCE QUE LE TRONCON N'EST PAS
    # LA RANGEE : une figure qui ne montrerait que le troncon donnerait le verdict a lire comme
    # portant sur toute la ligne. C'est la regle que `207` a posee, et sa raison.
    for nom in ("la_moyenne_mesuree", "une_rangee_seule", "le_plancher_de_la_matiere"):
        x = (d.get("les_predictions_a_toutes_les_coutures") or {}).get(nom)
        if not x or not x.get("decidable"):
            raise ValueError(f"{chemin} : la prédiction « {nom} » à toutes les coutures manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if not ve.get("elle_traverse_sous_le_demi_pli"):
        return "La moyenne des rangées — elle sort du feuillet avant d'avoir traversé"
    if ve.get("la_projection_de_208_est_atteinte"):
        return "La moyenne des rangées — elle traverse, et la projection de `208` est ATTEINTE"
    return ("La moyenne des rangées — elle traverse, mais la projection de `208` reste une borne "
            "OPTIMISTE")


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

    m, ep, ve, e = d["la_marche"], d["lepreuve"], d["le_verdict"], d["letalon"]
    q, pr = d["ce_que_la_moyenne_a_retire"], d["la_dispersion_predite"]
    ac = d["les_predictions_a_la_meme_longueur"]
    at = d["les_predictions_a_toutes_les_coutures"]
    ec_t = d["les_rangees_du_treillis"]
    lignes = d.get("les_lignes") or {}
    une = lignes.get(str(ec_t.get("la_mediane"))) or next(iter(lignes.values()), {})
    moy = [float(x) for x in m["le_cumul_moyenne_en_voxels"]]
    seul = [float(x) for x in m["le_cumul_dune_rangee_seule_en_voxels"]]
    demi = float(d["le_demi_pli_en_voxels"])
    tr = m["le_plus_long_troncon"]
    traverse = bool(ve["elle_traverse_sous_le_demi_pli"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {une.get('segment')} · rangées {ec_t.get('les_rangees')} · "
           f"{d['les_coutures_communes']} coutures communes · tronçon {tr[0]}–{tr[1]}, "
           f"{m['les_coutures_du_troncon']} coutures · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : les DEUX traces, appariées, et la bande du demi-feuillet
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "les deux marches sur les MÊMES coutures — la moyennée et la rangée seule", moyen,
           ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 16, pw - 400, 236
    haut = max(demi, max(abs(v) for v in moy + seul)) * 1.12
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 46, yy - 6, _fr(haut * (1.0 - k / 2.0), 0), 0, GRIS)
    for signe in (1.0, -1.0):
        yb = gy0 + gh * (1.0 - (signe * demi / haut + 1.0) / 2.0)
        for s in range(0, int(gw), 12):
            art.line([gx0 + s, yb, gx0 + min(s + 6, int(gw)), yb], fill=ALERTE, width=2)
        traits.append((gx0, yb, gx0 + gw))
    ecrire(gx0 + 6, gy0 + gh * (1.0 - (demi / haut + 1.0) / 2.0) - 16,
           f"le demi-feuillet : ± {_fr(demi, 0)} voxels", 0, ALERTE)
    n = max(1, len(moy) - 1)
    # ⚠⚠ LA LEGENDE EST DANS LE GRAPHE, ET LES DEUX EPAISSEURS DIFFERENT : a un pixel chacune
    # les deux marches se confondaient, et la seule chose que ce panneau existe pour montrer —
    # que l'une a la moitie de l'amplitude de l'autre — ne se voyait pas. Vu en REGARDANT
    # l'image, par aucune garde.
    ecrire(gx0 + 6, gy0 + 32, f"— la moyenne des {len(d['les_pas_par_rangee'])} rangées",
           0, CONTRE)
    ecrire(gx0 + 6, gy0 + 46, f"— la rangée {m['la_rangee_seule']} seule", 0, GRIS)
    for trace, coul, epais in ((seul, GRIS, 2), (moy, CONTRE, 3)):
        prec = None
        for i, val in enumerate(trace):
            px = gx0 + gw * i / n
            py = gy0 + gh * (1.0 - (val / haut + 1.0) / 2.0)
            if prec is not None:
                art.line([prec[0], prec[1], px, py], fill=coul, width=epais)
            points.append((px, py))
            prec = (px, py)
    ecrire(gx0 + gw / 2 - 86, gy0 + gh + 10,
           f"les {m['les_coutures_du_troncon']} coutures du tronçon commun", 0, GRIS)
    lx = x0 + pw - 326
    ecrire(lx, y0 + 16,
           f"{'★' if traverse else '✗'} ELLE RESTE DANS LE FEUILLET : {traverse}", moyen,
           BON if traverse else ALERTE)
    for k, (nom, val, coul) in enumerate((
            ("moyennée", f"{_fr(ve['lexcursion_moyennee_en_voxels'], 4)} vx", CONTRE),
            ("… en plis", _fr(ve["lexcursion_moyennee_en_plis"], 6), CONTRE),
            ("… en demi-feuillets", _fr(ve["lexcursion_moyennee_en_demi_plis"], 4), CONTRE),
            (f"rangée {m['la_rangee_seule']} seule, mêmes coutures",
             f"{_fr(ve['lexcursion_dune_rangee_seule_en_voxels'], 4)} vx", GRIS),
            ("le gain mesuré", _fr(ve["le_gain_mesure_sur_lexcursion"], 4), ENCRE))):
        yy = y0 + 46 + k * 20
        ecrire(lx, yy, nom, 0, coul)
        ecrire(lx + 216, yy, val, 0, coul)
    ecrire(lx, y0 + 156,
           f"`207` lisait {_fr(ve['lexcursion_de_207_en_voxels'], 4)} voxels", petit, ENCRE)
    ecrire(lx, y0 + 170,
           f"sur {ve['les_coutures_de_207']} coutures — un rapport de longueurs", petit, ENCRE)
    ecrire(lx, y0 + 184,
           f"de {_fr(ve['le_rapport_des_longueurs_a_207'], 4)}.", petit, ENCRE)
    ecrire(lx, y0 + 208, "★ LE CONTRÔLE EST APPARIÉ : les deux marches", petit, GRIS)
    ecrire(lx, y0 + 222, "partent du même endroit et franchissent les", petit, GRIS)
    ecrire(lx, y0 + 236, "mêmes coutures, donc leur rapport ne contient", petit, GRIS)
    ecrire(lx, y0 + 250, "aucune correction de longueur.", petit, GRIS)
    ecrire(lx, y0 + 266, "⚠ Une excursion reste une SEULE réalisation.", petit, GRIS)

    # ---- panneau 2 : ce que la moyenne a retiré
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que la moyenne a retiré, et les deux bornes", moyen, ENCRE)
    hautQ = max(float(q["la_dispersion_mediane_dune_rangee_en_voxels"]),
                float(q["la_dispersion_du_pas_moyenne_en_voxels"]),
                float(pr["ce_quune_rangee_seule_porte_en_voxels"])) * 1.12
    for k, (nom, val, coul) in enumerate((
            ("borne optimiste (`208`)", q["la_borne_optimiste_en_voxels"], BON),
            ("MESURÉE, pas moyenné", q["la_dispersion_du_pas_moyenne_en_voxels"], CONTRE),
            ("borne réaliste, 3 lectures", q["la_borne_realiste_en_voxels"], ENCRE),
            ("une rangée seule", q["la_dispersion_mediane_dune_rangee_en_voxels"], GRIS))):
        yy = y0 + 10 + k * 27
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 284, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 13, 372, float(val) / hautQ, 6, coul)
    for k, (nom, val) in enumerate((
            ("dérive partagée (`208`)",
             f"{_fr(pr['la_derive_partagee_en_voxels'], 4)} vx"),
            ("bruit propre (`208`)", f"{_fr(pr['le_bruit_propre_en_voxels'], 4)} vx"),
            ("rapport à l'optimiste", _fr(q["le_rapport_a_la_borne_optimiste"], 4)),
            ("rapport à la réaliste", _fr(q["le_rapport_a_la_borne_realiste"], 4)),
            ("erreur d'échantillonnage",
             f"± {_fr(q['lerreur_dechantillonnage_en_voxels'], 4)} vx"),
            ("écart à la réaliste",
             f"{_fr(q['lecart_a_la_borne_realiste_en_erreurs'], 4)} erreur"),
            ("sur combien de coutures", f"{q['les_coutures']}"))):
        yy = y0 + 126 + k * 16
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 284, yy, val, 0, ENCRE)
    atteinte = bool(q["la_projection_de_208_est_atteinte"])
    accord = bool(q["elle_saccorde_a_la_borne_realiste"])
    ecrire(x0 + 12, y0 + 232,
           f"{'★' if accord else '✗'} ACCORD À LA BORNE RÉALISTE : {accord}", 0,
           BON if accord else ALERTE)

    # ---- panneau 3 : les excursions prédites, à la MÊME longueur
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les excursions prédites, à la MÊME longueur", moyen, ENCRE)
    entrees = (("`208` projetait", ac["loptimiste_de_208"], BON),
               ("trois lectures", ac["la_realiste_a_trois_lectures"], ENCRE),
               ("MESURÉE", {"lecart_attendu_en_voxels":
                            ve["lexcursion_moyennee_en_voxels"]}, CONTRE),
               ("une rangée seule", ac["une_rangee_seule"], GRIS),
               ("le plancher matière", ac["le_plancher_de_la_matiere"], ALERTE))
    hautP = max(float(x["lecart_attendu_en_voxels"]) for _n, x, _c in entrees)
    hautP = max(hautP, demi) * 1.12
    for k, (nom, x_, coul) in enumerate(entrees):
        yy = y0 + 12 + k * 30
        val = float(x_["lecart_attendu_en_voxels"])
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 284, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 14, 372, val / hautP, 7, coul)
    yd = y0 + 12 + 5 * 30
    ecrire(x0 + 12, yd, "le demi-feuillet", 0, ALERTE)
    ecrire(x0 + 284, yd, f"{_fr(demi, 0)} vx", 0, ALERTE)
    barre(x0 + 12, yd + 14, 372, demi / hautP, 7, ALERTE)
    ecrire(x0 + 12, y0 + 206,
           f"sur {ac['loptimiste_de_208']['les_coutures']} coutures — celles du tronçon "
           f"COMMUN", 0, GRIS)
    ecrire(x0 + 12, y0 + 224,
           "⚠⚠ Une marche qui traverse un tronçon plus court", petit, GRIS)
    ecrire(x0 + 12, y0 + 236, "n'a pas traversé davantage.", petit, GRIS)

    # ---- panneau 4 : l'épreuve et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve de `199`, posée sur le pas MOYENNÉ", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("déplacement net", f"{_fr(ep['le_deplacement_net_en_voxels'], 4)} vx"),
            ("le nul médian", f"{_fr(ep['le_deplacement_du_nul_median_en_voxels'], 4)} vx"),
            ("tirages aussi loin",
             f"{ep['les_tirages_au_moins_aussi_loin']} sur {ep['tirages']}"),
            ("marches au hasard", _fr(ep["combien_de_marches_au_hasard"], 4)))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 252, yy, val, 0, ENCRE)
    accumule = bool(ep["ca_saccumule"])
    ecrire(x0 + 12, y0 + 96,
           f"{'✗' if accumule else '★'} ÇA S'ACCUMULE : {accumule}", moyen,
           ALERTE if accumule else BON)
    ecrire(x0 + 12, y0 + 124, "l'étalon — fabrique, MOYENNE, puis tire les signes", 0, GRIS)
    for k, (nom, val) in enumerate((
            ("biais posé (celui de `199`)", f"{_fr(e['le_biais_pose_en_voxels'], 2)} vx"),
            ("rangées moyennées", f"{e['les_rangees_moyennees']}"),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("net, face positive",
             f"{_fr(e['le_net_median_sur_la_face_positive_en_voxels'], 4)} vx"),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"),
            ("le plancher de `202`",
             f"{e['le_plancher_de_202']}, raté {_fr(e['la_chance_de_rater_au_plancher'], 4)}"))):
        yy = y0 + 140 + k * 17
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 252, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 236,
           f"★ sépare : {e['letalon_separe']} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{'★' if traverse else '✗'}  LA MARCHE MOYENNÉE TRAVERSE SON TRONÇON : excursion "
           f"{_fr(ve['lexcursion_moyennee_en_voxels'], 4)} voxels sur "
           f"{ve['les_coutures_du_troncon']} coutures, soit "
           f"{_fr(ve['lexcursion_moyennee_en_demi_plis'], 4)} demi-feuillet.", moyen,
           BON if traverse else ALERTE)
    ecrire(78, y + 46,
           f"     Sur les MÊMES coutures, la rangée seule en donne "
           f"{_fr(ve['lexcursion_dune_rangee_seule_en_voxels'], 4)} voxels : un gain mesuré de "
           f"{_fr(ve['le_gain_mesure_sur_lexcursion'], 4)}, sans aucune correction de longueur.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"{'★' if atteinte else '✗'}  MAIS LA PROJECTION DE `208` RESTE UNE BORNE : elle "
           f"annonçait {_fr(q['la_borne_optimiste_en_voxels'], 4)} voxels de dispersion, trois "
           f"lectures en promettent {_fr(q['la_borne_realiste_en_voxels'], 4)},", moyen,
           BON if atteinte else ALERTE)
    ecrire(78, y + 100,
           f"     et la mesure en donne {_fr(q['la_dispersion_du_pas_moyenne_en_voxels'], 4)} "
           f"± {_fr(q['lerreur_dechantillonnage_en_voxels'], 4)} sur {q['les_coutures']} "
           f"coutures : un rapport de {_fr(q['le_rapport_a_la_borne_optimiste'], 4)} à "
           f"l'optimiste, et {_fr(q['lecart_a_la_borne_realiste_en_erreurs'], 4)} erreur de la "
           f"réaliste.", moyen, BON if atteinte else ALERTE)
    ecrire(78, y + 128,
           f"{'✗' if accumule else '★'}  ET LES PAS MOYENNÉS NE S'ADDITIONNENT PAS : déplacement "
           f"net {_fr(ep['le_deplacement_net_en_voxels'], 4)} voxels contre "
           f"{_fr(ep['le_deplacement_du_nul_median_en_voxels'], 4)} au nul par tirage de signes, "
           f"{ep['les_tirages_au_moins_aussi_loin']} tirages sur {ep['tirages']}.", moyen,
           ALERTE if accumule else BON)
    tient = bool(at["la_moyenne_mesuree"]["il_tient_sous_le_demi_pli"])
    ecrire(78, y + 178,
           f"{'★' if tient else '✗'}  ET À {at['la_moyenne_mesuree']['les_coutures']} COUTURES, "
           f"toutes celles que les trois rangées partagent, le pas moyenné annonce "
           f"{_fr(at['la_moyenne_mesuree']['lecart_attendu_en_voxels'], 4)} voxels — sous le "
           f"demi-feuillet de {_fr(demi, 0)} — là où une rangée seule en", moyen,
           BON if tient else ALERTE)
    ecrire(78, y + 200,
           f"     annonce {_fr(at['une_rangee_seule']['lecart_attendu_en_voxels'], 4)}, "
           f"AU-DESSUS, et où le plancher que la matière impose à un lecteur PARFAIT en laisse "
           f"encore {_fr(at['le_plancher_de_la_matiere']['lecart_attendu_en_voxels'], 4)}.",
           moyen, BON if tient else ALERTE)
    ecrire(78, y + 154,
           f"⚠⚠ LE PIÈGE N'A MORDU QU'À MOITIÉ : "
           f"{ve['les_coutures_communes_en_tout']} coutures partagées contre "
           f"{ve['les_coutures_de_toute_la_rangee_de_207']} pour une rangée seule, mais leur "
           f"plus long tronçon en fait {ve['les_coutures_du_troncon']} — exactement celui de "
           f"`207`.", moyen, GRIS)

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
      (_fr(36.0, 0), _fr(0.05, 2), _fr(1.5129, 4)) == ("36", "0,05", "1,5129"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(1.5129, 4))}")
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

    # ★★★★ LES DEUX TRACES VIENNENT DE LA MESURE, CHACUNE, POINT PAR POINT. Une sonde qui n'en
    # eprouverait qu'une laisserait l'autre libre d'etre dessinee depuis n'importe quoi — et c'est
    # justement l'APPARIEMENT des deux qui porte le gain publie.
    for cle in ("le_cumul_moyenne_en_voxels", "le_cumul_dune_rangee_seule_en_voxels"):
        trace = d["la_marche"][cle]
        for k in (0, len(trace) // 2, len(trace) - 1):
            faux = copy.deepcopy(d)
            faux["la_marche"][cle][k] = float(trace[k]) + 7.7
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            v(f"★★★★ le point {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ LA BANDE DU DEMI-FEUILLET EST TRACEE DEPUIS LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_demi_pli_en_voxels"] = 12
    _c, _p, _cd, _pt, _b, tr_c = dessiner(faux, sortie)
    v("★★★★ la bande du demi-feuillet suit la constante que la mesure publie",
      [round(y, 2) for _a, y, _b in tr_c] != [round(y, 2) for _a, y, _b in traits],
      f"{len(tr_c)} traits")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "lexcursion_moyennee_en_voxels"), 41.4141, 4, 3),
            (("le_verdict", "lexcursion_moyennee_en_plis"), 0.515151, 6, 1),
            (("le_verdict", "lexcursion_moyennee_en_demi_plis"), 0.6161, 4, 2),
            (("le_verdict", "lexcursion_dune_rangee_seule_en_voxels"), 57.5757, 4, 2),
            (("le_verdict", "le_gain_mesure_sur_lexcursion"), 1.9191, 4, 2),
            (("le_verdict", "lexcursion_de_207_en_voxels"), 28.3131, 4, 1),
            (("le_verdict", "le_rapport_des_longueurs_a_207"), 0.7171, 4, 1),
            (("ce_que_la_moyenne_a_retire", "la_dispersion_du_pas_moyenne_en_voxels"),
             9.6969, 4, 2),
            (("ce_que_la_moyenne_a_retire", "la_borne_optimiste_en_voxels"), 5.1515, 4, 2),
            (("ce_que_la_moyenne_a_retire", "la_borne_realiste_en_voxels"), 6.3131, 4, 2),
            (("ce_que_la_moyenne_a_retire", "la_dispersion_mediane_dune_rangee_en_voxels"),
             7.4747, 4, 1),
            (("ce_que_la_moyenne_a_retire", "le_rapport_a_la_borne_optimiste"), 2.1212, 4, 2),
            (("ce_que_la_moyenne_a_retire", "le_rapport_a_la_borne_realiste"), 0.3131, 4, 1),
            (("la_dispersion_predite", "la_derive_partagee_en_voxels"), 8.1818, 4, 1),
            (("la_dispersion_predite", "le_bruit_propre_en_voxels"), 3.6363, 4, 1),
            (("lepreuve", "le_deplacement_net_en_voxels"), 21.2121, 4, 2),
            (("lepreuve", "le_deplacement_du_nul_median_en_voxels"), 33.1313, 4, 2),
            (("lepreuve", "combien_de_marches_au_hasard"), 0.7171, 4, 1),
            (("letalon", "le_biais_pose_en_voxels"), 7.5, 2, 1),
            (("letalon", "le_net_median_sur_la_face_positive_en_voxels"), 171.7171, 4, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1),
            (("ce_que_la_moyenne_a_retire", "lerreur_dechantillonnage_en_voxels"),
             0.2121, 4, 2),
            (("ce_que_la_moyenne_a_retire", "lecart_a_la_borne_realiste_en_erreurs"),
             1.3131, 4, 2),
            (("letalon", "la_chance_de_rater_au_plancher"), 0.4141, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LES QUATRE PREDICTIONS A LA MEME LONGUEUR SONT DESSINEES, CHACUNE.
    for nom, val in (("loptimiste_de_208", 11.1111),
                     ("la_realiste_a_trois_lectures", 22.2222),
                     ("une_rangee_seule", 44.4444),
                     ("le_plancher_de_la_matiere", 55.5555)):
        faux = copy.deepcopy(d)
        faux["les_predictions_a_la_meme_longueur"][nom]["lecart_attendu_en_voxels"] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la prédiction « {nom} » est écrite",
          sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LES TROIS PREDICTIONS A TOUTES LES COUTURES SONT DESSINEES — sans elles, le verdict
    # se lirait comme portant sur la rangee entiere alors qu'il porte sur un troncon.
    for nom, val in (("la_moyenne_mesuree", 66.6666),
                     ("une_rangee_seule", 77.7777),
                     ("le_plancher_de_la_matiere", 88.8888)):
        faux = copy.deepcopy(d)
        faux["les_predictions_a_toutes_les_coutures"][nom]["lecart_attendu_en_voxels"] = val
        _c, pt2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la prédiction « {nom} » à toutes les coutures est écrite",
          sum(1 for _x, _y, t, _f in pt2 if _fr(val, 4) in t) >= 1)
    faux = copy.deepcopy(d)
    faux["les_predictions_a_toutes_les_coutures"]["la_moyenne_mesuree"]["les_coutures"] = 515
    _c, pt3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de coutures de la rangée entière est écrit",
      sum(1 for _x, _y, t, _f in pt3 if "515" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["le_verdict"]["les_coutures_de_toute_la_rangee_de_207"] = 616
    _c, pt4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de coutures d'une rangée seule chez `207` est écrit",
      sum(1 for _x, _y, t, _f in pt4 if "616" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LA LONGUEUR DU TRONCON EST ECRITE, PARCE QUE C'EST LE PIEGE DE LA TRANCHE.
    faux = copy.deepcopy(d)
    faux["la_marche"]["le_plus_long_troncon"] = [11, 77, 67]
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ les bornes du plus long tronçon commun sont écrites",
      sum(1 for _x, _y, t, _f in p4 if "11" in t and "77" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["le_verdict"]["les_coutures_du_troncon"] = 414
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de coutures du tronçon commun est écrit au moins deux fois",
      sum(1 for _x, _y, t, _f in p5 if "414" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p5 if '414' in t)} mentions")
    faux = copy.deepcopy(d)
    faux["le_verdict"]["les_coutures_de_207"] = 313
    _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de coutures de `207` est écrit, sinon la longueur ne se compare pas",
      sum(1 for _x, _y, t, _f in p6 if "313" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LA RANGEE DU CONTROLE EST NOMMEE DANS LE DESSIN, sinon un trace juste sous une
    # mauvaise legende passerait — et c'est exactement ce qui a eu lieu a la premiere mesure.
    faux = copy.deepcopy(d)
    faux["la_marche"]["la_rangee_seule"] = int(d["les_rangees_du_treillis"]["la_mediane"])
    _c, p7, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la rangée sur laquelle le contrôle marche est ÉCRITE",
      sum(1 for _x, _y, t, _f in p7
          if f"rangée {d['les_rangees_du_treillis']['la_mediane']} seule" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["letalon"]["les_replicats_du_refus"] = 313
    _c, p8, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de réplicats du refus de l'étalon est écrit",
      sum(1 for _x, _y, t, _f in p8 if "313" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["letalon"]["le_plancher_de_202"] = 414
    _c, p9, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le plancher de `202` que l'étalon dépasse est écrit",
      sum(1 for _x, _y, t, _f in p9 if "414" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elle_traverse_sous_le_demi_pli"] = False
    v("★★★★ une marche qui sort du feuillet change le titre",
      "elle sort du feuillet" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elle_traverse_sous_le_demi_pli"] = True
    faux["le_verdict"]["la_projection_de_208_est_atteinte"] = True
    v("★★★★ une projection atteinte le dit autrement",
      "est ATTEINTE" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["la_projection_de_208_est_atteinte"] = False
    v("★★★ et une projection non atteinte reste une borne optimiste",
      "borne OPTIMISTE" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_marche"].__setitem__("decidable", False),
             "à la marche indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["ce_que_la_moyenne_a_retire"].__setitem__("decidable", False),
             "sans ce que la moyenne a retiré"),
            (lambda x: x["la_dispersion_predite"].__setitem__("decidable", False),
             "sans les deux bornes posées d'avance"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_marche"].__setitem__("le_cumul_moyenne_en_voxels", [1.0]),
             "sans trace moyennée"),
            (lambda x: x["la_marche"].__setitem__(
                "le_cumul_dune_rangee_seule_en_voxels",
                x["la_marche"]["le_cumul_dune_rangee_seule_en_voxels"][:-1]),
             "dont les deux traces n'ont PAS la même longueur"),
            (lambda x: x["la_marche"].__setitem__("les_coutures_du_troncon", 3),
             "dont la trace ne suit pas le compte de coutures"),
            (lambda x: x["les_predictions_a_la_meme_longueur"]["une_rangee_seule"].__setitem__(
                "decidable", False),
             "sans la prédiction d'une rangée seule"),
            (lambda x: x["les_predictions_a_la_meme_longueur"].__setitem__(
                "le_plancher_de_la_matiere", None),
             "sans le plancher que la matière impose"),
            (lambda x: x["la_marche"].__setitem__("la_rangee_seule", 4242),
             "dont le contrôle marche sur une AUTRE rangée que la médiane déclarée"),
            (lambda x: x["ce_que_la_moyenne_a_retire"].__setitem__(
                "lerreur_dechantillonnage_en_voxels", None),
             "sans l'erreur d'échantillonnage de la dispersion"),
            (lambda x: x["letalon"].__setitem__("le_plancher_de_202", None),
             "dont l'étalon ne dit pas le plancher qu'il dépasse"),
            (lambda x: x["les_predictions_a_toutes_les_coutures"][
                "la_moyenne_mesuree"].__setitem__("decidable", False),
             "sans la prédiction du pas moyenné à toutes les coutures"),
            (lambda x: x["les_predictions_a_toutes_les_coutures"].__setitem__(
                "le_plancher_de_la_matiere", None),
             "sans le plancher de la matière à toutes les coutures"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_la_moyenne_des_rangees_traverse_t_elle.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_moyenne_des_rangees_traverse_t_elle.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "210_la_moyenne_des_rangees_traverse_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
