"""Les rangées traversées indépendamment s'accordent-elles entre elles ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LE DÉSACCORD DES CUMULS, recalé sur une
origine commune, avec la bande du demi-feuillet en travers : c'est la seule chose neuve de la
tranche, et l'œil doit voir si les deux marches restent dans le même feuillet. En bas à gauche, les
TRONÇONS PROPRES des trois rangées posés sur les colonnes du rouleau — ils ne couvrent pas la même
portion, et c'est le piège. Au centre, le désaccord par couture contre `208` et contre la
prédiction, puis ce qu'il annonce à l'échelle de la rangée. À droite, l'épreuve et l'étalon avec son
contrôle aveugle.

  uv run python src/figures/figure_les_rangees_saccordent_elles_entre_elles.py \\
      --json docs/mesures/les_rangees_saccordent_elles_entre_elles.json \\
      --sortie docs/images/211_les_rangees_saccordent_elles_entre_elles.png
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
    """Le JSON de `les_rangees_saccordent_elles_entre_elles.py`.

    ⚠⚠⚠ LE REFUS QUI COMPTE EST CELUI D'UN DÉSACCORD QUI NE PART PAS DE ZÉRO. Tout ce que cette
    tranche revendique tient au RECALAGE sur une origine commune : un désaccord cumulé dont le
    premier point n'est pas nul mesure une distance parcourue avant la rencontre, et non une
    divergence. La figure le dessinerait quand même, et l'œil ne verrait pas la différence.

    ⚠⚠ ET UN VERDICT QUI NE PORTE PAS SUR LA PAIRE DÉCLARÉE EST REFUSÉ : la clef sous laquelle une
    paire est rangée et le nom qu'on lui donne doivent désigner la même chose, faute de quoi la
    figure légende une paire avec les nombres d'une autre.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("le_verdict", "lepreuve", "letalon", "le_desaccord_predit",
                "les_marches_separees", "les_desaccords", "ce_que_les_desaccords_valent",
                "les_decalages_dorigine", "les_rangees_du_treillis", "la_paire_declaree"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("le_verdict", "lepreuve", "letalon", "le_desaccord_predit"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    if not d["letalon"].get("un_biais_partage_reste_invisible"):
        raise ValueError(f"{chemin} : l'étalon voit un biais PARTAGÉ, qui doit s'annuler")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    paire = d["la_paire_declaree"]
    cle_d = f"{paire[0]}-{paire[1]}"
    if cle_d not in d["les_desaccords"]:
        raise ValueError(f"{chemin} : la paire déclarée {paire} n'est pas parmi les désaccords")
    if d["le_verdict"].get("la_paire") != list(paire):
        raise ValueError(f"{chemin} : le verdict porte sur {d['le_verdict'].get('la_paire')} et "
                         f"non sur la paire déclarée {paire}")
    des = d["les_desaccords"][cle_d]
    if not des.get("decidable"):
        raise ValueError(f"{chemin} : le désaccord de la paire déclarée est indécidable")
    trace = des.get("le_desaccord_cumule_en_voxels") or []
    if len(trace) < 2:
        raise ValueError(f"{chemin} : la trace du désaccord est absente")
    if abs(float(trace[0])) > 1e-9:
        raise ValueError(f"{chemin} : le désaccord cumulé ne part pas de zéro — il n'est pas "
                         f"recalé sur une origine commune")
    if len(trace) != int(des["les_coutures_du_troncon"]) + 1:
        raise ValueError(f"{chemin} : la trace ne porte pas un point de plus que de coutures")
    for r in d["les_rangees_du_treillis"]["les_rangees"]:
        m = (d["les_marches_separees"] or {}).get(str(r))
        if not m or not m.get("decidable"):
            raise ValueError(f"{chemin} : la marche propre de la rangée {r} manque")
    val = (d["ce_que_les_desaccords_valent"] or {}).get(cle_d) or {}
    if val.get("lerreur_dechantillonnage_en_voxels") is None:
        raise ValueError(f"{chemin} : l'erreur d'échantillonnage du désaccord est absente")
    if val.get("ce_que_208_a_mesure_en_voxels") is None:
        raise ValueError(f"{chemin} : le désaccord des pas de `208` n'est pas relu")
    if not (val.get("ce_quelle_annonce_a_toutes_les_communes") or {}).get("decidable"):
        raise ValueError(f"{chemin} : ce que le désaccord annonce à la rangée manque")
    dec = (d["les_decalages_dorigine"] or {}).get(cle_d) or {}
    if dec.get("le_decalage_dorigine_en_voxels") is None:
        raise ValueError(f"{chemin} : la règle réfutée n'est pas portée — le décalage d'origine "
                         f"de la paire déclarée manque")
    if d["letalon"].get("les_replicats_du_refus") is None:
        raise ValueError(f"{chemin} : l'étalon ne dit pas son compte de réplicats du refus")
    # ⚠⚠⚠ LE CONTROLE AVEUGLE SE JUGE SUR UN TAUX, DONC LA FIGURE EXIGE CE TAUX : une figure qui
    # n'aurait lu que le drapeau laisserait croire qu'un contrôle a tiré zéro fois alors qu'il
    # tire à la garantie de l'épreuve comme toute face négative.
    if d["letalon"].get("le_taux_du_controle_aveugle") is None:
        raise ValueError(f"{chemin} : l'étalon ne dit pas le taux de son contrôle aveugle")
    if d["letalon"].get("les_replicats_du_controle_aveugle") is None:
        raise ValueError(f"{chemin} : l'étalon ne dit pas le compte de son contrôle aveugle")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if ve.get("deux_rangees_finissent_sur_des_feuillets_differents"):
        return ("Les rangées entre elles — à l'échelle de la rangée, deux voisines finissent sur "
                "DEUX feuillets")
    if not ve.get("le_troncon_reste_sous_le_demi_pli"):
        return "Les rangées entre elles — elles se séparent avant la fin de leur tronçon commun"
    return ("Les rangées entre elles — leur désaccord reste DANS le feuillet, même à l'échelle de "
            "la rangée")


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

    ve, ep, e = d["le_verdict"], d["lepreuve"], d["letalon"]
    pr = d["le_desaccord_predit"]
    ec_t = d["les_rangees_du_treillis"]
    paire = d["la_paire_declaree"]
    cle_d = f"{paire[0]}-{paire[1]}"
    des = d["les_desaccords"][cle_d]
    val = d["ce_que_les_desaccords_valent"][cle_d]
    dec = d["les_decalages_dorigine"][cle_d]
    a_la_rangee = val["ce_quelle_annonce_a_toutes_les_communes"]
    lignes = d.get("les_lignes") or {}
    une = lignes.get(str(ec_t.get("la_mediane"))) or next(iter(lignes.values()), {})
    demi = float(d["le_demi_pli_en_voxels"])
    trace = [float(x) for x in des["le_desaccord_cumule_en_voxels"]]
    tient_troncon = bool(val["le_troncon_reste_sous_le_demi_pli"])
    tient_rangee = bool(val["la_rangee_entiere_reste_sous_le_demi_pli"])
    accumule = bool(ve["ca_saccumule"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {une.get('segment')} · rangées {ec_t.get('les_rangees')} · paire déclarée "
           f"{paire} · {des['les_coutures_communes']} coutures communes · tronçon "
           f"{des['le_plus_long_troncon'][0]}–{des['le_plus_long_troncon'][1]}, "
           f"{des['les_coutures_du_troncon']} coutures · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : le désaccord des cumuls, recalé, contre la bande du demi-feuillet
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"le désaccord des deux cumuls, recalé sur une origine commune — rangées {paire}",
           moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 16, pw - 400, 236
    haut = max(demi, max(abs(v) for v in trace)) * 1.12
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
    n = max(1, len(trace) - 1)
    prec = None
    for i, v_ in enumerate(trace):
        px = gx0 + gw * i / n
        py = gy0 + gh * (1.0 - (v_ / haut + 1.0) / 2.0)
        if prec is not None:
            art.line([prec[0], prec[1], px, py], fill=CONTRE, width=3)
        points.append((px, py))
        prec = (px, py)
    # ⚠⚠ LA LEGENDE EST DESCENDUE SOUS LA TRACE : posee en haut du graphe elle etait TRAVERSEE
    # par la marche, donc illisible exactement la ou l'oeil la cherche. Vu en REGARDANT l'image,
    # par aucune garde — les mots ne se recouvraient pas, c'est le TRACE qui passait dessus.
    ecrire(gx0 + 6, gy0 + gh - 30,
           f"— la rangée {paire[0]} moins la rangée {paire[1]}, couture par couture", 0, CONTRE)
    ecrire(gx0 + gw / 2 - 96, gy0 + gh + 10,
           f"les {des['les_coutures_du_troncon']} coutures du tronçon commun aux deux", 0, GRIS)
    lx = x0 + pw - 326
    ecrire(lx, y0 + 16,
           f"{'★' if tient_troncon else '✗'} SUR CE TRONÇON, DANS LE FEUILLET : {tient_troncon}",
           moyen, BON if tient_troncon else ALERTE)
    for k, (nom, valeur, coul) in enumerate((
            ("séparation la plus grande",
             f"{_fr(ve['la_separation_la_plus_grande_en_voxels'], 4)} vx", CONTRE),
            ("… en demi-feuillets", _fr(ve["la_separation_en_demi_plis"], 4), CONTRE),
            ("désaccord au bout", f"{_fr(ve['le_desaccord_final_en_voxels'], 4)} vx", CONTRE),
            ("excursion du désaccord",
             f"{_fr(ve['lexcursion_du_desaccord_en_voxels'], 4)} vx", GRIS),
            ("une marche au hasard donnerait",
             f"{_fr(ve['ce_quune_marche_au_hasard_donnerait_en_voxels'], 4)} vx", GRIS),
            ("le rapport", _fr(ve["le_rapport_a_la_marche_au_hasard"], 4), ENCRE))):
        yy = y0 + 46 + k * 20
        ecrire(lx, yy, nom, 0, coul)
        ecrire(lx + 232, yy, valeur, 0, coul)
    ecrire(lx, y0 + 176, "★ LE RECALAGE EST DANS LA CONSTRUCTION : le", petit, GRIS)
    ecrire(lx, y0 + 190, "désaccord est le cumul des DIFFÉRENCES de pas,", petit, GRIS)
    ecrire(lx, y0 + 204, "donc il part de zéro à la première couture", petit, GRIS)
    ecrire(lx, y0 + 218, "commune, par définition même.", petit, GRIS)
    ecrire(lx, y0 + 240,
           f"⚠ Sans lui, un décalage d'origine de", petit, ALERTE)
    ecrire(lx, y0 + 254,
           f"{_fr(dec['le_decalage_dorigine_en_voxels'], 4)} voxels s'ajouterait à la séparation.",
           petit, ALERTE)

    # ---- panneau 2 : les tronçons PROPRES des trois rangées, sur les colonnes du rouleau
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "chaque rangée sur SON tronçon — le piège", moyen, ENCRE)
    sep = d["les_marches_separees"]
    bornes = [sep[str(r)]["le_plus_long_troncon"] for r in ec_t["les_rangees"]]
    bornes.append(des["le_plus_long_troncon"])
    gauche = min(b[0] for b in bornes)
    droite = max(b[1] for b in bornes)
    etendue = max(1, droite - gauche)
    for k, r in enumerate(ec_t["les_rangees"]):
        m = sep[str(r)]
        b = m["le_plus_long_troncon"]
        yy = y0 + 18 + k * 34
        ecrire(x0 + 12, yy, f"rangée {r}", 0, ENCRE)
        ecrire(x0 + 84, yy, f"{b[2]} coutures, {b[0]}–{b[1]}", 0, GRIS)
        ecrire(x0 + 262, yy,
               f"excursion {_fr((m['lexcursion'] or {}).get('lexcursion_en_voxels'), 2)}", 0, GRIS)
        gx = x0 + 12 + (pw - 40) * (b[0] - gauche) / etendue
        gb = x0 + 12 + (pw - 40) * (b[1] - gauche) / etendue
        art.rectangle([gx, yy + 15, max(gb, gx + 2), yy + 22], fill=CONTRE)
        barres.append((max(gb, gx + 2), x0 + 12 + (pw - 40)))
        points.append((gb, yy + 22))
    b = des["le_plus_long_troncon"]
    yy = y0 + 18 + 3 * 34
    ecrire(x0 + 12, yy, f"commun {paire}", 0, ALERTE)
    ecrire(x0 + 148, yy, f"{b[2]} coutures, {b[0]}–{b[1]}", 0, ALERTE)
    gx = x0 + 12 + (pw - 40) * (b[0] - gauche) / etendue
    gb = x0 + 12 + (pw - 40) * (b[1] - gauche) / etendue
    art.rectangle([gx, yy + 15, max(gb, gx + 2), yy + 22], fill=ALERTE)
    barres.append((max(gb, gx + 2), x0 + 12 + (pw - 40)))
    ecrire(x0 + 12, y0 + 160, "⚠⚠ LES TROIS RANGÉES N'ONT PAS LES MÊMES TROUS,", petit, GRIS)
    ecrire(x0 + 12, y0 + 174, "donc leurs tronçons ne commencent ni ne finissent", petit, GRIS)
    ecrire(x0 + 12, y0 + 188, "aux mêmes colonnes. Le désaccord ne se lit que", petit, GRIS)
    ecrire(x0 + 12, y0 + 202, "là où les DEUX cumuls existent.", petit, GRIS)
    ecrire(x0 + 12, y0 + 222,
           f"★ L'excursion est insensible au décalage : "
           f"{dec['lexcursion_est_insensible_au_decalage']}", petit, BON)
    ecrire(x0 + 12, y0 + 236,
           f"✗ La séparation y est sensible : "
           f"{_fr(dec['la_separation_sans_recalage_en_voxels'], 4)} brute pour "
           f"{_fr(ve['la_separation_la_plus_grande_en_voxels'], 4)} recalée", petit, ALERTE)

    # ---- panneau 3 : le désaccord par couture, et ce qu'il annonce à la rangée
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le désaccord par couture, et à l'échelle de la rangée", moyen, ENCRE)
    mesure = float(val["le_desaccord_par_couture_mesure_en_voxels"])
    hautD = max(mesure, float(val["ce_que_208_a_mesure_en_voxels"]),
                float(pr["le_desaccord_par_couture_en_voxels"]),
                float(pr["ce_que_racine_de_deux_donnerait_en_voxels"])) * 1.12
    for k, (nom, valeur, coul) in enumerate((
            ("MESURÉ ici, par couture", mesure, CONTRE),
            ("`208` sur les mêmes pas", val["ce_que_208_a_mesure_en_voxels"], ENCRE),
            ("prédit : les deux bruits propres",
             pr["le_desaccord_par_couture_en_voxels"], BON),
            ("« racine de deux fois le bruit »",
             pr["ce_que_racine_de_deux_donnerait_en_voxels"], GRIS))):
        yy = y0 + 10 + k * 27
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, f"{_fr(valeur, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 13, 372, float(valeur) / hautD, 6, coul)
    for k, (nom, valeur) in enumerate((
            ("erreur d'échantillonnage",
             f"± {_fr(val['lerreur_dechantillonnage_en_voxels'], 4)} vx sur "
             f"{val['les_coutures_communes']}"),
            ("écart à `208`", f"{_fr(val['lecart_a_208_en_erreurs'], 4)} erreur"),
            ("il recoupe `208`", str(val["il_recoupe_208"])),
            ("bruits propres de `208`",
             f"{_fr(pr['le_bruit_propre_de_lune_en_voxels'], 4)} et "
             f"{_fr(pr['le_bruit_propre_de_lautre_en_voxels'], 4)} vx"))):
        yy = y0 + 128 + k * 17
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 202, yy, valeur, 0, ENCRE)
    ecrire(x0 + 12, y0 + 204,
           f"{'★' if tient_rangee else '✗'} À {a_la_rangee['les_coutures']} COUTURES IL ANNONCE "
           f"{_fr(a_la_rangee['lecart_attendu_en_voxels'], 4)} VX", moyen,
           BON if tient_rangee else ALERTE)
    ecrire(x0 + 12, y0 + 228,
           f"contre un demi-feuillet de {_fr(demi, 0)} — la traversée de `210` en", petit, ENCRE)
    ecrire(x0 + 12, y0 + 240,
           f"demandait {_fr(ve['ce_que_la_moyenne_de_210_annonce_a_la_rangee_en_voxels'], 4)}.",
           petit, ENCRE)

    # ---- panneau 4 : l'épreuve et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve déclarée, et l'étalon à trois faces", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 10,
           f"{'✗' if accumule else '★'} ÇA S'ACCUMULE : {accumule}", moyen,
           ALERTE if accumule else BON)
    for k, (nom, valeur) in enumerate((
            ("déplacement net", f"{_fr(ep['le_deplacement_net_en_voxels'], 4)} vx"),
            ("le nul médian", f"{_fr(ep['le_deplacement_du_nul_median_en_voxels'], 4)} vx"),
            ("tirages au moins aussi loin",
             f"{ep['les_tirages_au_moins_aussi_loin']} sur {ep['tirages']}"),
            ("en marches au hasard", _fr(ep["combien_de_marches_au_hasard"], 4)))):
        yy = y0 + 38 + k * 17
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 228, yy, valeur, 0, ENCRE)
    ecrire(x0 + 12, y0 + 118, "L'ÉTALON", petit, ENCRE)
    for k, (nom, valeur, coul) in enumerate((
            ("biais PROPRE, vu",
             f"{e['les_vus']} sur {e['replicats']} (net "
             f"{_fr(e['le_net_median_sur_la_face_positive_en_voxels'], 2)})", BON),
            ("sans biais, faux",
             f"{e['les_faux']} sur {e['les_replicats_du_refus']} = "
             f"{_fr(e['le_taux_de_faux'], 4)}", ENCRE),
            ("biais PARTAGÉ, vu",
             f"{e['les_biais_partages_vus']} sur {e['les_replicats_du_controle_aveugle']} = "
             f"{_fr(e['le_taux_du_controle_aveugle'], 4)}", BON),
            ("le plancher de `202`",
             f"{e['le_plancher_de_202']}, raté "
             f"{_fr(e['la_chance_de_rater_au_plancher'], 4)}", GRIS),
            ("le biais posé", f"{_fr(e['le_biais_propre_pose_en_voxels'], 2)} vx", GRIS))):
        yy = y0 + 138 + k * 17
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 172, yy, valeur, 0, coul)
    ecrire(x0 + 12, y0 + 232,
           f"★ sépare : {e['letalon_separe']} · un biais partagé reste invisible : "
           f"{e['un_biais_partage_reste_invisible']}", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{'★' if tient_troncon else '✗'}  SUR LEUR TRONÇON COMMUN, LES DEUX RANGÉES RESTENT "
           f"DANS LE FEUILLET : séparation "
           f"{_fr(ve['la_separation_la_plus_grande_en_voxels'], 4)} voxels sur "
           f"{ve['les_coutures_du_troncon']} coutures,", moyen,
           BON if tient_troncon else ALERTE)
    ecrire(78, y + 40,
           f"     soit {_fr(ve['la_separation_en_demi_plis'], 4)} demi-feuillet, pour une "
           f"excursion de {_fr(ve['lexcursion_du_desaccord_en_voxels'], 4)} là où une marche au "
           f"hasard de même pas en donnerait "
           f"{_fr(ve['ce_quune_marche_au_hasard_donnerait_en_voxels'], 4)}.", moyen, ENCRE)
    ecrire(78, y + 70,
           f"{'✗' if not tient_rangee else '★'}  MAIS À {a_la_rangee['les_coutures']} COUTURES, "
           f"TOUTES CELLES QUE LES DEUX RANGÉES PARTAGENT, LE DÉSACCORD ANNONCE "
           f"{_fr(a_la_rangee['lecart_attendu_en_voxels'], 4)} VOXELS,", moyen,
           BON if tient_rangee else ALERTE)
    ecrire(78, y + 92,
           f"     contre un demi-feuillet de {_fr(demi, 0)} : deux rangées voisines traversées "
           f"chacune pour elle-même finissent sur deux feuillets DIFFÉRENTS, alors que la "
           f"traversée", moyen, BON if tient_rangee else ALERTE)
    ecrire(78, y + 114,
           f"     de `210` n'en demandait que "
           f"{_fr(ve['ce_que_la_moyenne_de_210_annonce_a_la_rangee_en_voxels'], 4)}. Moyenner "
           f"aide à TRAVERSER et n'aide en RIEN à S'ACCORDER — ce sont deux quantités "
           f"différentes.", moyen, BON if tient_rangee else ALERTE)
    ecrire(78, y + 144,
           f"★  ET LE DÉSACCORD PAR COUTURE RECOUPE `208` : "
           f"{_fr(val['le_desaccord_par_couture_mesure_en_voxels'], 4)} ± "
           f"{_fr(val['lerreur_dechantillonnage_en_voxels'], 4)} voxels ici contre "
           f"{_fr(val['ce_que_208_a_mesure_en_voxels'], 4)} là-bas, soit "
           f"{_fr(val['lecart_a_208_en_erreurs'], 4)} erreur — deux courses du dépôt.", moyen,
           BON)
    ecrire(78, y + 172,
           f"⚠⚠ LA PRÉDICTION DÉRIVÉE N'EST PAS UN RECOUPEMENT : "
           f"{_fr(pr['le_desaccord_par_couture_en_voxels'], 4)} voxels sortent des deux bruits "
           f"propres de `208`, que `208` avait lui-même tirés de", moyen, GRIS)
    ecrire(78, y + 194,
           f"     son désaccord des pas — identité, pas confirmation. Et l'écriture « racine de "
           f"deux fois le bruit » en donnerait "
           f"{_fr(pr['ce_que_racine_de_deux_donnerait_en_voxels'], 4)}, soit "
           f"{_fr(pr['lecart_entre_les_deux_ecritures_en_voxels'], 4)} voxel d'écart.",
           moyen, GRIS)

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
    paire = d["la_paire_declaree"]
    cle_d = f"{paire[0]}-{paire[1]}"
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

    # ★★★★ LA TRACE DU DESACCORD VIENT DE LA MESURE, POINT PAR POINT.
    trace = d["les_desaccords"][cle_d]["le_desaccord_cumule_en_voxels"]
    for k in (1, len(trace) // 2, len(trace) - 1):
        faux = copy.deepcopy(d)
        faux["les_desaccords"][cle_d]["le_desaccord_cumule_en_voxels"][k] = \
            float(trace[k]) + 7.7
        _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le point {k} du désaccord cumulé vient de la mesure",
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

    # ★★★★ LES TRONCONS PROPRES DES TROIS RANGEES SONT DESSINES, CHACUN, ET LEURS BORNES AUSSI.
    for r in d["les_rangees_du_treillis"]["les_rangees"]:
        faux = copy.deepcopy(d)
        faux["les_marches_separees"][str(r)]["le_plus_long_troncon"] = [11, 313, 303]
        _c, pr_, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le tronçon propre de la rangée {r} est écrit avec ses bornes",
          sum(1 for _x, _y, t, _f in pr_ if "303 coutures, 11–313" in t) >= 1)
        dessiner(d, sortie)
    for r in d["les_rangees_du_treillis"]["les_rangees"]:
        faux = copy.deepcopy(d)
        faux["les_marches_separees"][str(r)]["lexcursion"]["lexcursion_en_voxels"] = 31.31
        _c, pe_, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ l'excursion propre de la rangée {r} est écrite",
          sum(1 for _x, _y, t, _f in pe_ if "31,31" in t) >= 1)
        dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, valeur, dec_, combien in (
            (("le_verdict", "la_separation_la_plus_grande_en_voxels"), 41.4141, 4, 3),
            (("le_verdict", "la_separation_en_demi_plis"), 0.6161, 4, 2),
            (("le_verdict", "le_desaccord_final_en_voxels"), 13.1313, 4, 1),
            (("le_verdict", "lexcursion_du_desaccord_en_voxels"), 57.5757, 4, 2),
            (("le_verdict", "ce_quune_marche_au_hasard_donnerait_en_voxels"), 44.4141, 4, 2),
            (("le_verdict", "le_rapport_a_la_marche_au_hasard"), 1.9191, 4, 1),
            (("le_verdict", "ce_que_la_moyenne_de_210_annonce_a_la_rangee_en_voxels"),
             29.1313, 4, 2),
            (("lepreuve", "le_deplacement_net_en_voxels"), 21.2121, 4, 1),
            (("lepreuve", "le_deplacement_du_nul_median_en_voxels"), 33.1313, 4, 1),
            (("lepreuve", "combien_de_marches_au_hasard"), 0.7171, 4, 1),
            (("le_desaccord_predit", "le_desaccord_par_couture_en_voxels"), 7.4747, 4, 2),
            (("le_desaccord_predit", "ce_que_racine_de_deux_donnerait_en_voxels"), 8.1818, 4, 2),
            (("le_desaccord_predit", "lecart_entre_les_deux_ecritures_en_voxels"), 0.3131, 4, 1),
            (("le_desaccord_predit", "le_bruit_propre_de_lune_en_voxels"), 3.6363, 4, 1),
            (("le_desaccord_predit", "le_bruit_propre_de_lautre_en_voxels"), 5.1515, 4, 1),
            (("letalon", "le_biais_propre_pose_en_voxels"), 7.5, 2, 1),
            (("letalon", "le_net_median_sur_la_face_positive_en_voxels"), 171.71, 2, 1),
            (("letalon", "le_taux_de_faux"), 0.1111, 4, 1),
            (("letalon", "la_chance_de_rater_au_plancher"), 0.4141, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = valeur
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2 if _fr(valeur, dec_) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    faux = copy.deepcopy(d)
    faux["les_decalages_dorigine"][cle_d]["la_separation_sans_recalage_en_voxels"] = 66.6161
    _c, p11, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la séparation SANS recalage est écrite à côté de la recalée",
      sum(1 for _x, _y, t, _f in p11 if "66,6161" in t) >= 1)
    dessiner(d, sortie)

    for cle2, valeur, dec_, combien in (
            ("le_desaccord_par_couture_mesure_en_voxels", 9.6969, 4, 2),
            ("ce_que_208_a_mesure_en_voxels", 6.3131, 4, 2),
            ("lerreur_dechantillonnage_en_voxels", 0.2121, 4, 2),
            ("lecart_a_208_en_erreurs", 1.3131, 4, 2)):
        faux = copy.deepcopy(d)
        faux["ce_que_les_desaccords_valent"][cle_d][cle2] = valeur
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n3 = sum(1 for _x, _y, t, _f in p3 if _fr(valeur, dec_) in t)
        v(f"★★★★ ce_que_les_desaccords_valent.{cle2} est lu autant de fois qu'il le faut",
          n3 >= combien, f"{n3} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ CE QUE LE DESACCORD ANNONCE A LA RANGEE EST LE NOMBRE QUI PORTE LA TRANCHE.
    faux = copy.deepcopy(d)
    faux["ce_que_les_desaccords_valent"][cle_d][
        "ce_quelle_annonce_a_toutes_les_communes"]["lecart_attendu_en_voxels"] = 42.4242
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ ce que le désaccord annonce à toute la rangée est écrit deux fois",
      sum(1 for _x, _y, t, _f in p4 if "42,4242" in t) >= 2)
    faux = copy.deepcopy(d)
    faux["ce_que_les_desaccords_valent"][cle_d][
        "ce_quelle_annonce_a_toutes_les_communes"]["les_coutures"] = 313
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ et le compte de coutures sur lequel il l'annonce l'est aussi",
      sum(1 for _x, _y, t, _f in p5 if "313" in t) >= 2)
    dessiner(d, sortie)

    # ★★★★ LA REGLE REFUTEE EST PORTEE DANS LE DESSIN, avec son ecart mesure.
    faux = copy.deepcopy(d)
    faux["les_decalages_dorigine"][cle_d]["le_decalage_dorigine_en_voxels"] = 81.8181
    _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le décalage d'origine que le recalage supprime est ÉCRIT",
      sum(1 for _x, _y, t, _f in p6 if "81,8181" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LA PAIRE SUR LAQUELLE LE VERDICT PORTE EST NOMMEE, sinon une paire juste sous une
    # mauvaise legende passerait — et la mesure a deja failli le faire par une clef rebatie.
    v("★★★★ la paire déclarée est nommée dans le dessin",
      sum(1 for _x, _y, t, _f in poses if str(paire) in t) >= 1, str(paire))
    faux = copy.deepcopy(d)
    faux["letalon"]["les_replicats_du_refus"] = 313
    _c, p7, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de réplicats du refus de l'étalon est écrit",
      sum(1 for _x, _y, t, _f in p7 if "313" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["letalon"]["le_plancher_de_202"] = 414
    _c, p8, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le plancher de `202` que l'étalon dépasse est écrit",
      sum(1 for _x, _y, t, _f in p8 if "414" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["letalon"]["les_biais_partages_vus"] = 7
    _c, p9, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le contrôle aveugle de l'étalon est dessiné, avec son compte",
      sum(1 for _x, _y, t, _f in p9 if "7 sur" in t) >= 1)
    faux = copy.deepcopy(d)
    faux["letalon"]["le_taux_du_controle_aveugle"] = 0.3131
    _c, p10, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ et son TAUX est écrit, parce que c'est lui qui le juge et non un zéro",
      sum(1 for _x, _y, t, _f in p10 if "0,3131" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["deux_rangees_finissent_sur_des_feuillets_differents"] = True
    v("★★★★ deux feuillets différents changent le titre",
      "DEUX feuillets" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["deux_rangees_finissent_sur_des_feuillets_differents"] = False
    faux["le_verdict"]["le_troncon_reste_sous_le_demi_pli"] = False
    v("★★★★ une séparation dès le tronçon le dit autrement",
      "avant la fin de leur tronçon" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["le_troncon_reste_sous_le_demi_pli"] = True
    v("★★★ et un désaccord qui tient partout le dit encore autrement",
      "reste DANS le feuillet" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["letalon"].__setitem__("un_biais_partage_reste_invisible", False),
             "dont l'étalon VOIT un biais partagé, qui doit s'annuler"),
            (lambda x: x["letalon"].__setitem__("les_replicats_du_refus", None),
             "dont l'étalon ne dit pas son compte de réplicats du refus"),
            (lambda x: x["letalon"].__setitem__("le_taux_du_controle_aveugle", None),
             "dont l'étalon ne dit pas le taux de son contrôle aveugle"),
            (lambda x: x["letalon"].__setitem__("les_replicats_du_controle_aveugle", None),
             "dont l'étalon ne dit pas le compte de son contrôle aveugle"),
            (lambda x: x["le_verdict"].__setitem__("decidable", False),
             "au verdict indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["le_desaccord_predit"].__setitem__("decidable", False),
             "sans la prédiction posée d'avance"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["les_desaccords"][cle_d].__setitem__(
                "le_desaccord_cumule_en_voxels",
                [4.2] + x["les_desaccords"][cle_d]["le_desaccord_cumule_en_voxels"][1:]),
             "dont le désaccord ne part PAS de zéro — donc n'est pas recalé"),
            (lambda x: x["les_desaccords"][cle_d].__setitem__(
                "le_desaccord_cumule_en_voxels", [0.0]),
             "sans trace du désaccord"),
            (lambda x: x["les_desaccords"][cle_d].__setitem__("les_coutures_du_troncon", 3),
             "dont la trace ne suit pas le compte de coutures"),
            (lambda x: x["les_desaccords"][cle_d].__setitem__("decidable", False),
             "dont le désaccord de la paire déclarée est indécidable"),
            (lambda x: x["le_verdict"].__setitem__("la_paire", [4242, 4243]),
             "dont le verdict porte sur une AUTRE paire que la déclarée"),
            (lambda x: x.__setitem__("la_paire_declaree", [4242, 4243]),
             "dont la paire déclarée n'a pas été mesurée"),
            (lambda x: x["les_marches_separees"][
                str(d["les_rangees_du_treillis"]["les_rangees"][1])].__setitem__(
                "decidable", False),
             "sans la marche propre d'une des rangées"),
            (lambda x: x["ce_que_les_desaccords_valent"][cle_d].__setitem__(
                "lerreur_dechantillonnage_en_voxels", None),
             "sans l'erreur d'échantillonnage du désaccord"),
            (lambda x: x["ce_que_les_desaccords_valent"][cle_d].__setitem__(
                "ce_que_208_a_mesure_en_voxels", None),
             "qui ne relit pas le désaccord des pas de `208`"),
            (lambda x: x["ce_que_les_desaccords_valent"][cle_d][
                "ce_quelle_annonce_a_toutes_les_communes"].__setitem__("decidable", False),
             "sans ce que le désaccord annonce à la rangée"),
            (lambda x: x["les_decalages_dorigine"][cle_d].__setitem__(
                "le_decalage_dorigine_en_voxels", None),
             "qui ne porte pas la règle réfutée du décalage d'origine"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_les_rangees_saccordent_elles_entre_elles.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "les_rangees_saccordent_elles_entre_elles.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "211_les_rangees_saccordent_elles_entre_elles.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
