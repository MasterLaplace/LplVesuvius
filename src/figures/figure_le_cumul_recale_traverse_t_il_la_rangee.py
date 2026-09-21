"""Le cumul recalé sur seize rangées traverse-t-il son tronçon ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la TRACE elle-même, avec la bande du
demi-feuillet en travers : c'est la seule chose qu'un œil peut juger, et elle répond à la question
d'un coup. En bas à gauche, les tronçons — pourquoi la marche ne traverse qu'un morceau de la
rangée. Au centre, la prédiction posée avant la mesure, et la même à la longueur de la rangée
entière. À droite, l'épreuve de `199` reprise, et l'étalon.

  uv run python src/figures/figure_le_cumul_recale_traverse_t_il_la_rangee.py \\
      --json docs/mesures/le_cumul_recale_traverse_t_il_la_rangee.json \\
      --sortie docs/images/207_le_cumul_recale_traverse_t_il_la_rangee.png
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
    """Le JSON de `le_cumul_recale_traverse_t_il_la_rangee.py`.

    ⚠⚠⚠ REFUSE UNE MESURE SANS TRACE, SANS PRÉDICTION À LA RANGÉE ENTIÈRE, UNE DONT L'ÉTALON NE
    SÉPARE PAS, ET UNE QUI DÉCLARE PLUS D'UNE ÉPREUVE SANS EN DIVISER LA GARANTIE. La prédiction à
    la rangée est exigée parce que le plus long tronçon N'EST PAS la rangée : sans elle, le verdict
    se lirait comme portant sur toute la ligne.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "lexcursion", "lepreuve", "le_verdict", "letalon",
                "la_prediction", "la_prediction_a_la_rangee",
                "la_prediction_au_meilleur_lecteur"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("lexcursion", "lepreuve", "le_verdict", "letalon", "la_prediction",
                "la_prediction_a_la_rangee", "la_prediction_au_meilleur_lecteur"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    if len(d.get("le_cumul_en_voxels") or []) < 2:
        raise ValueError(f"{chemin} : la trace du cumul est absente")
    if len(d["le_cumul_en_voxels"]) != int(d["les_pas_du_cumul"]) + 1:
        raise ValueError(f"{chemin} : la trace ne porte pas un point de plus que de pas")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if not ve.get("elle_traverse_sous_le_demi_pli"):
        return ("Le cumul recalé — il sort du feuillet avant d'avoir traversé son tronçon")
    if ve.get("ca_saccumule"):
        return ("Le cumul recalé — il traverse son tronçon, mais les pas s'ADDITIONNENT")
    return ("Le cumul recalé — il traverse son tronçon sans quitter le feuillet, et les pas se "
            "compensent")


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

    lg, ex, ep = d["la_ligne"], d["lexcursion"], d["lepreuve"]
    ve, e = d["le_verdict"], d["letalon"]
    pr, prr = d["la_prediction"], d["la_prediction_a_la_rangee"]
    pm = d["la_prediction_au_meilleur_lecteur"]
    cumul = [float(x) for x in d["le_cumul_en_voxels"]]
    demi = float(d["le_demi_pli_en_voxels"])
    tr = d.get("le_plus_long_troncon") or [0, 0, 0]

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · {len(lg['les_rangees_lues'])} rangées · "
           f"tronçon {tr[0]}–{tr[1]} · {d['les_pas_du_cumul']} pas · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : la trace, avec la bande du demi-feuillet
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la marche elle-même, et la bande du demi-feuillet qu'elle ne doit pas quitter",
           moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 16, pw - 400, 236
    haut = max(demi, max(abs(v) for v in cumul)) * 1.12
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
    n = max(1, len(cumul) - 1)
    prec = None
    for i, val in enumerate(cumul):
        px = gx0 + gw * i / n
        py = gy0 + gh * (1.0 - (val / haut + 1.0) / 2.0)
        if prec is not None:
            art.line([prec[0], prec[1], px, py], fill=CONTRE, width=2)
        points.append((px, py))
        prec = (px, py)
    ecrire(gx0 + gw / 2 - 66, gy0 + gh + 10,
           f"les {d['les_pas_du_cumul']} coutures du tronçon", 0, GRIS)
    lx = x0 + pw - 326
    traverse = bool(ve["elle_traverse_sous_le_demi_pli"])
    ecrire(lx, y0 + 16,
           f"{'★' if traverse else '✗'} ELLE RESTE DANS LE FEUILLET : {traverse}", moyen,
           BON if traverse else ALERTE)
    for k, (nom, val) in enumerate((
            ("excursion", f"{_fr(ex['lexcursion_en_voxels'], 4)} vx"),
            ("… en plis", _fr(ex["lexcursion_en_plis"], 6)),
            ("… en demi-feuillets", _fr(ve["lexcursion_en_demi_plis"], 4)),
            ("le plus loin du départ", f"{_fr(ex['le_plus_loin_en_voxels'], 4)} vx"),
            ("déplacement net", f"{_fr(ex['le_deplacement_net_en_voxels'], 4)} vx"))):
        yy = y0 + 46 + k * 20
        ecrire(lx, yy, nom, 0, GRIS)
        ecrire(lx + 216, yy, val, 0, ENCRE)
    ecrire(lx, y0 + 156,
           f"`199` en donnait {_fr(ve['lexcursion_de_199_en_plis'], 6)} pli,", petit, ENCRE)
    ecrire(lx, y0 + 170,
           f"soit un rapport de {_fr(ve['le_rapport_a_199'], 4)}.", petit, ENCRE)
    ecrire(lx, y0 + 194, "★ C'EST L'AMPLITUDE QUI COÛTE UN FEUILLET,", petit, GRIS)
    ecrire(lx, y0 + 208, "pas le point d'arrivée : une marche qui part", petit, GRIS)
    ecrire(lx, y0 + 222, "loin et revient a déjà sauté en chemin, et", petit, GRIS)
    ecrire(lx, y0 + 236, "son déplacement net vaut zéro.", petit, GRIS)
    ecrire(lx, y0 + 258, "⚠⚠ Le tronçon N'EST PAS la rangée — voir le", petit, GRIS)
    ecrire(lx, y0 + 272, "panneau des tronçons.", petit, GRIS)

    # ---- panneau 2 : les tronçons
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les tronçons — pourquoi ce n'est pas la rangée", moyen, ENCRE)
    troncons = d.get("les_troncons") or []
    for k, (nom, val) in enumerate((
            ("chunks lus", f"{lg['colonnes_lues']} sur {lg['colonnes_demandees']}"),
            ("tronçons", f"{len(troncons)}"),
            ("le plus long", f"{tr[0]}–{tr[1]}, {tr[2]} chunks"),
            ("ses coutures", f"{d['les_pas_du_cumul']}"),
            ("coutures de tous", f"{d['les_coutures_de_tous_les_troncons']}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 240, yy, val, 0, ENCRE)
    if troncons:
        plus_grand = max(t[2] for t in troncons)
        for k, t_ in enumerate(troncons[:6]):
            barre(x0 + 12, y0 + 120 + k * 14, 372, float(t_[2]) / float(plus_grand), 8,
                  BON if t_[2] == tr[2] else GRIS)
    ecrire(x0 + 12, y0 + 208,
           "⚠⚠⚠ Un cumul ne se construit que sur des chunks", petit, GRIS)
    ecrire(x0 + 12, y0 + 222,
           "CONTIGUS : deux chunks séparés par un trou n'ont", petit, GRIS)
    ecrire(x0 + 12, y0 + 236,
           "pas de couture commune — la règle de `199`.", petit, GRIS)

    # ---- panneau 3 : la prédiction
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la prédiction, posée AVANT la mesure", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("dispersion de `204`", f"{_fr(pr['la_dispersion_de_204_en_voxels'], 4)} vx"),
            ("coutures du tronçon", f"{pr['les_coutures']}"),
            ("écart attendu", f"{_fr(pr['lecart_attendu_en_voxels'], 4)} vx"),
            ("observé sur attendu", _fr(ve["le_rapport_observe_sur_attendu"], 4)),
            ("plancher, dérive seule",
             f"{_fr(pm['lecart_attendu_en_voxels'], 4)} vx"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 252, yy, val, 0, ENCRE)
    hautP = max(float(pr["lecart_attendu_en_voxels"]),
                float(prr["lecart_attendu_en_voxels"]),
                float(ex["lexcursion_en_voxels"]), demi) * 1.12
    for k, (nom, val, coul) in enumerate((
            ("attendu sur le tronçon", pr["lecart_attendu_en_voxels"], GRIS),
            ("mesuré", ex["lexcursion_en_voxels"], CONTRE),
            ("le demi-feuillet", demi, ALERTE),
            ("plancher, dérive seule", pm["lecart_attendu_en_voxels"], BON),
            ("attendu sur la rangée", prr["lecart_attendu_en_voxels"], ENCRE))):
        yy = y0 + 116 + k * 24
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 280, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 14, 372, float(val) / hautP, 6, coul)
    tient = bool(prr["il_tient_sous_le_demi_pli"])
    ecrire(x0 + 12, y0 + 236,
           f"{'★' if tient else '✗'} À {prr['les_coutures']} COUTURES, LA PRÉDICTION TIENT : "
           f"{tient}", 0, BON if tient else ALERTE)

    # ---- panneau 4 : l'épreuve et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve de `199`, reprise, et l'étalon", moyen, ENCRE)
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
    ecrire(x0 + 12, y0 + 124, "l'étalon — deux faces, sur réplicats", 0, GRIS)
    for k, (nom, val) in enumerate((
            ("biais posé (celui de `199`)", f"{_fr(e['le_biais_pose_en_voxels'], 2)} vx"),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("net, face positive",
             f"{_fr(e['le_net_median_sur_la_face_positive_en_voxels'], 4)} vx"),
            ("net, face négative",
             f"{_fr(e['le_net_median_sur_la_face_negative_en_voxels'], 4)} vx"),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"))):
        yy = y0 + 142 + k * 19
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
           f"{'★' if traverse else '✗'}  LA MARCHE TRAVERSE SON TRONÇON SANS QUITTER LE FEUILLET : "
           f"excursion {_fr(ex['lexcursion_en_voxels'], 4)} voxels, soit "
           f"{_fr(ve['lexcursion_en_demi_plis'], 4)} demi-feuillet.", moyen,
           BON if traverse else ALERTE)
    ecrire(78, y + 46,
           f"     `199` lisait {_fr(ve['lexcursion_de_199_en_plis'], 6)} pli sur la même rangée "
           f"avec une seule rangée de coupe ; ici {_fr(ex['lexcursion_en_plis'], 6)}, un rapport "
           f"de {_fr(ve['le_rapport_a_199'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"★  ET LA PRÉDICTION TENAIT : {_fr(pr['la_dispersion_de_204_en_voxels'], 4)} voxels de "
           f"dispersion sur {pr['les_coutures']} coutures annonçaient "
           f"{_fr(pr['lecart_attendu_en_voxels'], 4)} voxels ; la mesure en donne "
           f"{_fr(ex['lexcursion_en_voxels'], 4)}, un rapport de "
           f"{_fr(ve['le_rapport_observe_sur_attendu'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 106,
           f"{'✗' if accumule else '★'}  ET LES PAS NE S'ADDITIONNENT PAS : déplacement net "
           f"{_fr(ep['le_deplacement_net_en_voxels'], 4)} voxels contre "
           f"{_fr(ep['le_deplacement_du_nul_median_en_voxels'], 4)} au nul par tirage de signes — "
           f"{_fr(ep['combien_de_marches_au_hasard'], 4)} marche au hasard,", moyen,
           ALERTE if accumule else BON)
    ecrire(78, y + 128,
           f"     {ep['les_tirages_au_moins_aussi_loin']} tirages sur {ep['tirages']} au moins "
           f"aussi loin.", moyen, ALERTE if accumule else BON)
    ecrire(78, y + 152,
           f"⚠⚠⚠ MAIS LE TRONÇON N'EST PAS LA RANGÉE : le filtre du producteur écarte des "
           f"chunks, et chacun COUPE la ligne — {len(troncons)} tronçons, le plus long de "
           f"{tr[2]} chunks sur {lg['colonnes_lues']} lus.", moyen, GRIS)
    ecrire(78, y + 174,
           f"     À {prr['les_coutures']} coutures, soit toutes celles que la rangée porte, la même "
           f"prédiction annonce {_fr(prr['lecart_attendu_en_voxels'], 4)} voxels = "
           f"{_fr(prr['lecart_attendu_en_plis'], 6)} pli : sous le demi-feuillet "
           f"{prr['il_tient_sous_le_demi_pli']}.", moyen, GRIS)
    plancher = bool(pm["il_tient_sous_le_demi_pli"])
    ecrire(78, y + 200,
           f"{'★' if plancher else '✗'} ET LE PLANCHER QUE LA MATIÈRE IMPOSE : avec la dérive "
           f"seule, {_fr(pm['la_dispersion_de_204_en_voxels'], 4)} voxels, un lecteur PARFAIT "
           f"donnerait {_fr(pm['lecart_attendu_en_voxels'], 4)} voxels sur cette rangée — "
           f"{_fr(pm['lecart_attendu_en_plis'], 6)} pli, sous le demi-feuillet {plancher}.",
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
      (_fr(36.0, 0), _fr(0.05, 2), _fr(2.4587, 4)) == ("36", "0,05", "2,4587"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(2.4587, 4))}")
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

    # ★★★★ LA TRACE DESSINEE EST CELLE DE LA MESURE, POINT PAR POINT.
    for k in (0, len(d["le_cumul_en_voxels"]) // 2, len(d["le_cumul_en_voxels"]) - 1):
        faux = copy.deepcopy(d)
        faux["le_cumul_en_voxels"][k] = float(d["le_cumul_en_voxels"][k]) + 7.7
        _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le point {k} de la trace vient de la mesure",
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
            (("lexcursion", "lexcursion_en_voxels"), 41.4141, 4, 3),
            (("lexcursion", "lexcursion_en_plis"), 0.515151, 6, 2),
            (("lexcursion", "le_deplacement_net_en_voxels"), -7.4747, 4, 1),
            (("lexcursion", "le_plus_loin_en_voxels"), 13.1313, 4, 1),
            (("le_verdict", "lexcursion_en_demi_plis"), 0.6161, 4, 2),
            (("le_verdict", "le_rapport_observe_sur_attendu"), 1.9191, 4, 2),
            (("le_verdict", "lexcursion_de_199_en_plis"), 2.121212, 6, 2),
            (("le_verdict", "le_rapport_a_199"), 0.3131, 4, 2),
            (("lepreuve", "le_deplacement_net_en_voxels"), 21.2121, 4, 2),
            (("lepreuve", "le_deplacement_du_nul_median_en_voxels"), 33.1313, 4, 2),
            (("lepreuve", "combien_de_marches_au_hasard"), 0.7171, 4, 2),
            (("la_prediction", "lecart_attendu_en_voxels"), 51.5151, 4, 3),
            (("la_prediction", "la_dispersion_de_204_en_voxels"), 9.6969, 4, 2),
            (("la_prediction_a_la_rangee", "lecart_attendu_en_voxels"), 61.6161, 4, 2),
            (("la_prediction_a_la_rangee", "lecart_attendu_en_plis"), 0.818181, 6, 1),
            (("letalon", "le_biais_pose_en_voxels"), 7.5, 2, 1),
            (("letalon", "le_net_median_sur_la_face_positive_en_voxels"), 171.7171, 4, 1),
            (("letalon", "le_net_median_sur_la_face_negative_en_voxels"), 31.3131, 4, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1),
            (("la_prediction_au_meilleur_lecteur", "lecart_attendu_en_voxels"), 71.7171, 4, 3),
            (("la_prediction_au_meilleur_lecteur", "lecart_attendu_en_plis"), 0.919191, 6, 1),
            (("la_prediction_au_meilleur_lecteur", "la_dispersion_de_204_en_voxels"),
             8.1818, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LE TRONCON N'EST PAS LA RANGEE, ET LA FIGURE LE DIT.
    faux = copy.deepcopy(d)
    faux["les_coutures_de_tous_les_troncons"] = 414
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de coutures de tous les tronçons est écrit",
      sum(1 for _x, _y, t, _f in p3 if "414" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["le_plus_long_troncon"] = [11, 77, 67]
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le plus long tronçon est écrit, bornes et longueur",
      sum(1 for _x, _y, t, _f in p4 if "11" in t and "77" in t) >= 1
      and sum(1 for _x, _y, t, _f in p4 if "67" in t) >= 2)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elle_traverse_sous_le_demi_pli"] = False
    v("★★★★ une marche qui sort du feuillet change le titre",
      "il sort du feuillet" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elle_traverse_sous_le_demi_pli"] = True
    faux["le_verdict"]["ca_saccumule"] = True
    v("★★★★ des pas qui s'additionnent le disent autrement",
      "les pas s'ADDITIONNENT" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["ca_saccumule"] = False
    v("★★★ et l'observé dit que les pas se compensent",
      "les pas se compensent" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["lexcursion"].__setitem__("decidable", False),
             "à l'excursion indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["la_prediction"].__setitem__("decidable", False),
             "à la prédiction indécidable"),
            (lambda x: x["la_prediction_a_la_rangee"].__setitem__("decidable", False),
             "sans prédiction à la rangée entière"),
            (lambda x: x["la_prediction_au_meilleur_lecteur"].__setitem__("decidable", False),
             "sans le plancher que la matière impose"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x.__setitem__("le_cumul_en_voxels", [1.0]),
             "sans trace du cumul"),
            (lambda x: x.__setitem__("les_pas_du_cumul", 3),
             "dont la trace ne suit pas le compte de pas"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_le_cumul_recale_traverse_t_il_la_rangee.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_cumul_recale_traverse_t_il_la_rangee.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "207_le_cumul_recale_traverse_t_il_la_rangee.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
