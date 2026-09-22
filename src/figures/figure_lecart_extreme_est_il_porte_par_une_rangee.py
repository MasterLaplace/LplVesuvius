"""L'écart extrême est-il porté par une rangée : les deux colonnes, l'épreuve, l'étalon, l'échelle.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, OÙ TOMBENT LES EXTRÊMES : les trois
paires de `217` n'en ont que deux colonnes, et à chacune une rangée s'écarte pendant que les deux
autres s'accordent — la forme exacte d'un saut. En haut à droite, L'ÉPREUVE : le nuage des cent cinq
colonnes, énergie contre forme, et les colonnes fortes n'y pointent pas vers un axe plus que le
rebrassage. En bas à gauche, L'ÉTALON, qui tient — et la règle que la porte prescrivait, qui ne tient
pas. En bas à droite, L'ÉCHELLE EN RANGÉES, et c'est le panneau qui conclut : trois rangées ne voient
pas des sauts de cette taille, cinq les voient tous.

  uv run python src/figures/figure_lecart_extreme_est_il_porte_par_une_rangee.py \\
      --json docs/mesures/lecart_extreme_est_il_porte_par_une_rangee.json \\
      --sortie docs/images/218_lecart_extreme_est_il_porte_par_une_rangee.png
"""
from __future__ import annotations

import argparse
import json
import re
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
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `lecart_extreme_est_il_porte_par_une_rangee.py`.

    ⚠⚠⚠ LES REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Sans l'étalon, un
    silence de l'épreuve ne dirait pas s'il vient de la matière ou de l'instrument ; sans les
    colonnes, le nuage serait un résumé ; sans le détail des extrêmes, la figure ne dirait pas OÙ.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    if not (d.get("letalon") or {}).get("decidable"):
        raise SystemExit("l'étalon manque — un silence sans étalon ne dit rien")
    for cle in ("lepreuve", "par_colonne", "le_detail_des_extremes", "la_regle_de_la_porte",
                "le_verdict"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    if not (d["lepreuve"] or {}).get("decidable"):
        raise SystemExit("l'épreuve est indécidable")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v.get("letalon_est_valide"):
        return "L'ÉTALON NE TIENT PAS : AUCUN VERDICT"
    if v.get("lepreuve_voit"):
        return "L'ÉCART EXTRÊME EST PORTÉ PAR UNE RANGÉE À LA FOIS"
    if v.get("trois_rangees_suffisent_au_nombre_observe"):
        return "L'ÉCART EXTRÊME EST PORTÉ PAR LA COLONNE, PAS PAR UNE RANGÉE"
    k = v.get("le_plus_petit_nombre_de_rangees_qui_voit")
    return ("TROIS RANGÉES NE DÉCIDENT PAS " + (f"— IL EN FAUT {k}" if k is not None
                                                  else "— ET L'ÉCHELLE N'EN PORTE PAS ASSEZ"))


def dessiner(d: dict, sortie: Path):
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    points: list[tuple[float, float]] = []
    nuage: list[tuple[float, float]] = []
    longueurs: dict[str, float] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, y, largeur_max, part, hauteur, coul, cle=None):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if cle:
            longueurs[cle] = bout - x
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    lu, ep, po = d["ce_que_211_a_rendu"], d["lepreuve"], d["la_regle_de_la_porte"]
    et, ve, det = d["letalon"], d["le_verdict"], d["le_detail_des_extremes"]
    pc = d["par_colonne"]

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"{len(lu['les_rangees'])} rangées {', '.join(str(r) for r in lu['les_rangees'])} de "
           f"`211` · {lu['combien_de_colonnes']} colonnes communes ({lu['la_premiere_colonne']} à "
           f"{lu['la_derniere_colonne']}) · les paires publiées sont la différence des rangées · "
           f"aucune lecture neuve du volume", petit, GRIS)

    # ── PANNEAU 1 · OU TOMBENT LES EXTREMES ─────────────────────────────────────────────────
    panneau(50, 88, 660, 404, "OÙ TOMBENT LES EXTRÊMES · trois paires, et seulement deux colonnes")
    par_col: dict[int, list[str]] = {}
    for nom, x in sorted(det.items()):
        if x.get("dans_le_recouvrement"):
            par_col.setdefault(int(x["la_colonne"]), []).append(nom)
    vals = [abs(v_) for nom, x in det.items() if x.get("dans_le_recouvrement")
            for v_ in x["les_anomalies_en_voxels"].values()]
    ech = max(vals) * 1.15 if vals else 1.0
    cx, demi = 400, 150
    y = 124
    for col, noms in sorted(par_col.items()):
        x = det[noms[0]]
        ecrire(66, y, f"colonne {col} · extrême de {' et '.join(noms)}", 0, ENCRE)
        y += 20
        for r, a in x["les_anomalies_en_voxels"].items():
            fautive = int(r) == int(x["la_rangee_que_la_direction_designe"])
            coul = ALERTE if fautive else CONTRE
            ecrire(90, y - 1, f"rangée {r}", 0, ENCRE if fautive else GRIS)
            bout = cx + demi * float(a) / ech
            art.rectangle([min(cx, bout), y, max(cx, bout), y + 10], fill=coul)
            points.append((bout, y + 10))
            barres.append((abs(bout - cx), demi))
            ecrire(560, y - 1, f"{_fr(a, 2)} vx", 0, coul)
            y += 18
        ecrire(90, y,
               f"les deux autres s'accordent à {_fr(x['le_desaccord_des_deux_autres_en_ecarts_types'], 2)}"
               f" écart-type de leur paire · rang d'énergie {x['le_rang_de_lenergie']}", 0, BON)
        y += 30
    art.line([cx, 140, cx, y - 26], fill=TRAIT, width=1)
    hors = [nom for nom, x in det.items() if not x.get("dans_le_recouvrement")]
    ecrire(66, 362,
           "⚠ deux paires partagent une colonne par TÉLESCOPAGE : c'est une identité, pas un résultat",
           0, ALERTE)
    ecrire(66, 380,
           ("toutes les paires ont leur extrême dans le recouvrement des trois rangées" if not hors
            else f"hors du recouvrement : {', '.join(hors)}"), 0, GRIS)

    # ── PANNEAU 2 · L'EPREUVE ────────────────────────────────────────────────────────────────
    panneau(700, 88, 1310, 404, "L'ÉPREUVE · la forme des colonnes contre leur énergie")
    e_, p_ = pc["les_energies"], pc["les_proximites"]
    seuil = float(ep["le_seuil_denergie"])
    emax = max(max(e_), seuil) * 1.08
    pmin = min(p_) - 0.005
    gx0, gx1, gy0, gy1 = 760, 1280, 126, 296

    def px(e):
        return gx0 + (gx1 - gx0) * float(e) / emax

    def py(p):
        return gy1 - (gy1 - gy0) * (float(p) - pmin) / (1.0 - pmin)

    art.line([gx0, gy1, gx1, gy1], fill=TRAIT, width=1)
    art.line([gx0, gy0, gx0, gy1], fill=TRAIT, width=1)
    xs = px(seuil)
    art.line([xs, gy0, xs, gy1], fill=ENCRE, width=1)
    ecrire(xs + 4, gy1 + 4, f"le maximum gaussien 2·ln n = {_fr(seuil, 2)}", 0, ENCRE)
    fortes = []
    for c, e, p in zip(pc["les_colonnes"], e_, p_):
        x_, y_ = px(e), py(p)
        coul = ALERTE if e > seuil else GRIS
        art.ellipse([x_ - 2, y_ - 2, x_ + 2, y_ + 2], fill=coul)
        nuage.append((x_, y_))
        points.append((x_, y_))
        if e > seuil:
            fortes.append((x_, y_, c))
    for x_, y_, c in fortes:
        ecrire(x_ + 5, y_ - 6, str(c), 0, ALERTE)
    ecrire(gx0 - 44, gy0 - 4, "forme", 0, GRIS)
    ecrire(gx0 - 20, gy1 - 6, _fr(pmin, 2), 0, GRIS)
    ecrire(gx1 - 90, gy1 + 4, "énergie blanchie", 0, GRIS)
    ecrire(716, 318,
           f"{ep['combien_de_colonnes_fortes']} colonnes fortes · proximité moyenne "
           f"{_fr(ep['la_proximite_observee'], 4)} contre {_fr(ep['la_proximite_du_nul_mediane'], 4)} "
           f"pour le rebrassage médian", 0, ENCRE)
    ecrire(716, 336,
           f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']} rebrassages au moins aussi forts"
           f" : l'épreuve ne voit pas", 0, (ALERTE if ep["elle_voit"] else BON))
    ecrire(716, 354,
           f"la règle de la porte, portée comme contrôle : {po.get('les_tirages_au_moins_aussi_forts')}"
           f"/{po.get('tirages')}", 0, GRIS)
    ecrire(716, 380,
           "une forme proche de un veut dire qu'une rangée s'écarte seule", 0, GRIS)

    # ── PANNEAU 3 · L'ETALON ─────────────────────────────────────────────────────────────────
    panneau(50, 428, 660, 762, "L'ÉTALON · il tient, et la règle de la porte ne tient pas")
    ecrire(66, 462,
           f"matières de {et['les_colonnes_par_matiere']} colonnes aux bruits propres mesurés · "
           f"{et['le_compte_decisif']} tirages par ligne", 0, GRIS)
    # ⚠⚠ UNE SEULE ECHELLE POUR TOUT LE PANNEAU : une premiere version tracait le face-a-face sur
    # une echelle de zero a un et les taux au-dessus sur zero a quatre dixiemes, donc la regle
    # declaree paraissait plus faible que la porte sur du bruit alors qu'elle tire plus.
    tmax = 1.2 * max(float(t_["le_taux"]) for t_ in (
        et["le_faux"], et["le_piege"], et["la_queue_propre"], et["la_regle_de_la_porte_sur_du_bruit"],
        et["la_regle_declaree_sur_les_memes_sauts"], et["la_regle_de_la_porte_sur_des_sauts"],
        {"le_taux": 2.0 * float(d["la_garantie_du_nul"])}))
    tx, tw = 330, 220
    lignes = [("bruit gaussien", et["le_faux"], CONTRE),
              (f"PIÈGE : queues partagées, κ = {_fr(et['laplatissement_du_piege'], 2)}",
               et["le_piege"], CONTRE),
              ("queue propre à une rangée (nommé)", et["la_queue_propre"], TRAIT),
              ("règle de la porte, sur du bruit", et["la_regle_de_la_porte_sur_du_bruit"], ALERTE)]
    yy = 490
    for nom, t, coul in lignes:
        ecrire(66, yy, nom, 0, ENCRE)
        barre(tx, yy, tw, t["le_taux"] / tmax, 10, coul, cle=nom)
        ecrire(tx + tw + 10, yy - 1, f"{t['les_vus']}/{t['sur']}", 0, GRIS)
        yy += 26
    xg = tx + tw * (2.0 * float(d["la_garantie_du_nul"])) / tmax
    art.line([xg, 484, xg, yy - 10], fill=BON, width=2)
    ecrire(xg - 60, yy - 6, "deux fois la garantie", 0, BON)
    yy += 20
    fa = et["les_sauts_du_face_a_face"]
    ecrire(66, yy, f"sur les mêmes matières à {fa} sauts de "
                   f"{_fr(et['lamplitude_des_sauts_en_voxels'], 2)} vx :", 0, ENCRE)
    yy += 22
    ecrire(66, yy, "règle déclarée", 0, ENCRE)
    barre(tx, yy, tw, et["la_regle_declaree_sur_les_memes_sauts"]["le_taux"] / tmax, 10, CONTRE,
          cle="déclarée sur les sauts")
    ecrire(tx + tw + 10, yy - 1, f"{et['la_regle_declaree_sur_les_memes_sauts']['les_vus']}/"
                                 f"{et['la_regle_declaree_sur_les_memes_sauts']['sur']}", 0, GRIS)
    yy += 24
    ecrire(66, yy, "règle de la porte", 0, ALERTE)
    barre(tx, yy, tw, et["la_regle_de_la_porte_sur_des_sauts"]["le_taux"] / tmax, 10, ALERTE)
    ecrire(tx + tw + 10, yy - 1, f"{et['la_regle_de_la_porte_sur_des_sauts']['les_vus']}/"
                                 f"{et['la_regle_de_la_porte_sur_des_sauts']['sur']}", 0, GRIS)
    ecrire(66, 730,
           "⚠ rebrasser par rangée des anomalies qui somment à zéro tire sur le bruit et rate les sauts",
           0, ALERTE)

    # ── PANNEAU 4 · L'ECHELLE ────────────────────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "L'ÉCHELLE · combien de rangées rendent la question décidable")
    ecrire(716, 462,
           f"{et['les_sauts_de_lechelle_en_rangees']} sauts de "
           f"{_fr(et['lamplitude_des_sauts_en_voxels'], 2)} vx, autant que de colonnes fortes, et le "
           f"plus petit extrême de `217`", 0, GRIS)
    rx, rw = 900, 250
    yy = 490
    for x in et["lechelle_en_rangees"]:
        ok = x["les_vus"] == x["sur"]
        ecrire(716, yy, f"{x['combien_de_rangees']} rangées", 0, ENCRE)
        barre(rx, yy, rw, x["les_vus"] / float(x["sur"]), 11, BON if ok else ALERTE)
        ecrire(rx + rw + 10, yy - 1, f"{x['les_vus']}/{x['sur']}", 0, GRIS)
        ecrire(800, yy, f"piège {_fr(x['le_taux_sur_le_piege'], 3)}", 0, GRIS)
        yy += 26
    yy += 12
    ecrire(716, yy, "à trois rangées, selon le nombre de sauts :", 0, ENCRE)
    yy += 22
    for x in et["lechelle_en_sauts"]:
        ecrire(716, yy, f"{x['combien_de_sauts']} saut{'s' if x['combien_de_sauts'] > 1 else ''}",
               0, GRIS)
        barre(rx, yy, rw, x["les_vus"] / float(x["sur"]), 9, TRAIT)
        ecrire(rx + rw + 10, yy - 2, f"{x['les_vus']}/{x['sur']}", 0, GRIS)
        yy += 20
    ecrire(716, 712,
           "★ trois axes à soixante degrés couvrent le plan : une direction quelconque passe souvent",
           0, ENCRE)
    ecrire(716, 728, "pour une rangée fautive, et un saut vrai ne s'en distingue qu'à peine", 0,
           ENCRE)
    if not et.get("lechelle_en_sauts_est_monotone"):
        ecrire(716, 746,
               "⚠ l'échelle en sauts n'est pas monotone : douze réplicats pour une puissance si basse",
               0, ALERTE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    designees = sorted({r for e, r in zip(e_, pc["les_rangees_designees"]) if e > seuil})
    ecrire(50, 842,
           f"★ les {ep['combien_de_colonnes_fortes']} colonnes fortes désignent les rangées "
           f"{', '.join(str(r) for r in designees)} : aux deux plus fortes, une rangée s'écarte "
           f"seule, la forme exacte d'un saut.", moyen, ENCRE)
    ecrire(50, 866,
           "     Mais trois rangées fabriquent cette forme par hasard assez souvent pour que le "
           "rebrassage l'égale.", moyen, ENCRE)
    ecrire(50, 900,
           f"★ la question devient une lecture précise : {ve['le_plus_petit_nombre_de_rangees_qui_voit']}"
           f" rangées voisines sur les mêmes colonnes, et l'épreuve déclarée ici s'y applique sans "
           f"retouche.", moyen, ENCRE)
    ecrire(50, 934,
           "⚠ ce qui n'est PAS établi : qu'un saut se distingue d'une queue propre à une rangée. Pour "
           "un vote de voisines, c'est la même chose.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, barres, points, nuage, longueurs


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_218.png"
    _, poses, cadres, barres, points, nuage, longueurs = dessiner(d, tmp)

    def _v(valide, voit, trois, k):
        return {"le_verdict": {"letalon_est_valide": valide, "lepreuve_voit": voit,
                               "trois_rangees_suffisent_au_nombre_observe": trois,
                               "le_plus_petit_nombre_de_rangees_qui_voit": k}}

    v("★★★★ les titres possibles sont DISTINCTS, et un étalon invalide prime",
      len({le_titre(_v(a, b, c, 5)) for a in (True, False) for b in (True, False)
           for c in (True, False)}) == 4
      and le_titre(_v(False, True, True, 5)) == le_titre(_v(False, False, False, None)))
    v("★★★ le titre LIT le verdict au lieu de le recalculer",
      ("NE DÉCIDENT PAS" in le_titre(d))
      == (d["le_verdict"]["letalon_est_valide"] and not d["le_verdict"]["lepreuve_voit"]
          and not d["le_verdict"]["trois_rangees_suffisent_au_nombre_observe"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, 1360),
      str(textes_debordants(poses, 1360))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ aucune barre ne déborde de sa piste", all(b <= p + 1e-6 for b, p in barres),
      str([x for x in barres if x[0] > x[1] + 1e-6])[:160])
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= 1360 and 0 <= y <= 980 for x, y in points))
    v("★★★★ le nuage trace CHAQUE colonne, pas un résumé",
      len(nuage) == len(d["par_colonne"]["les_colonnes"]) == d["lepreuve"]["combien_de_colonnes"])
    v("★★★★ et chaque point du nuage reste dans son panneau",
      all(700 <= x <= 1310 and 88 <= y <= 404 for x, y in nuage))

    txt = " ".join(t for _, _, t, _ in poses)
    det = d["le_detail_des_extremes"]
    v("★★★★ elle porte chaque colonne d'extrême et la rangée que la direction y désigne",
      all(f"colonne {x['la_colonne']}" in txt for x in det.values() if x["dans_le_recouvrement"])
      and all(f"rangée {x['la_rangee_que_la_direction_designe']}" in txt
              for x in det.values() if x["dans_le_recouvrement"]))
    v("★★★★ elle porte les trois paires de `217`, et dit que le partage d'une colonne est une "
      "IDENTITÉ", all(n in txt for n in det) and "TÉLESCOPAGE" in txt and "identité" in txt)
    v("★★★★ elle porte l'accord des deux autres rangées à chaque colonne",
      all(_fr(x["le_desaccord_des_deux_autres_en_ecarts_types"], 2) in txt
          for x in det.values() if x["dans_le_recouvrement"]))
    ep = d["lepreuve"]
    v("★★★★ elle porte le compte de l'épreuve ET celui de la règle de la porte",
      f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']}" in txt
      and f"{d['la_regle_de_la_porte']['les_tirages_au_moins_aussi_forts']}/"
          f"{d['la_regle_de_la_porte']['tirages']}" in txt)
    v("★★★★ elle porte le seuil dérivé et le nombre de colonnes fortes",
      _fr(ep["le_seuil_denergie"], 2) in txt and f"{ep['combien_de_colonnes_fortes']} colonnes fortes"
      in txt)
    et = d["letalon"]
    v("★★★★ elle porte le taux de faux, le PIÈGE et la règle de la porte sur du bruit",
      all(f"{t['les_vus']}/{t['sur']}" in txt for t in
          (et["le_faux"], et["le_piege"], et["la_regle_de_la_porte_sur_du_bruit"])))
    v("★★★★ tout le panneau de l'étalon est sur UNE échelle : les longueurs suivent les taux",
      abs(longueurs["déclarée sur les sauts"] / longueurs["règle de la porte, sur du bruit"]
          - et["la_regle_declaree_sur_les_memes_sauts"]["le_taux"]
          / et["la_regle_de_la_porte_sur_du_bruit"]["le_taux"]) < 0.02, str(longueurs))
    v("★★★★ elle porte le face-à-face des deux règles sur les mêmes sauts",
      f"{et['la_regle_de_la_porte_sur_des_sauts']['les_vus']}/" in txt
      and f"{et['la_regle_declaree_sur_les_memes_sauts']['les_vus']}/" in txt)
    v("★★★★ elle porte CHAQUE barreau de l'échelle en rangées, avec son piège",
      all(f"{x['combien_de_rangees']} rangées" in txt and f"{x['les_vus']}/{x['sur']}" in txt
          for x in et["lechelle_en_rangees"]))
    v("★★★★ elle dit combien de rangées il faut",
      f"{d['le_verdict']['le_plus_petit_nombre_de_rangees_qui_voit']} rangées voisines" in txt)
    v("★★★★ elle dit ce qui n'est PAS établi — un saut contre une queue propre à une rangée",
      "n'est PAS établi" in txt and "queue propre" in txt)
    v("★★★ elle dit qu'aucune lecture neuve du volume n'a eu lieu",
      "aucune lecture neuve du volume" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])

    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "lecart_extreme_est_il_porte_par_une_rangee.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "218_lecart_extreme_est_il_porte_par_une_rangee.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
