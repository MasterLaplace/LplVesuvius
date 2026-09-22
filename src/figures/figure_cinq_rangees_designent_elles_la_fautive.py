"""Cinq rangées désignent-elles la fautive : les deux colonnes, l'épreuve, l'étalon, l'attribution.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LES DEUX COLONNES DE `218`, lues à
cinq : la même rangée s'y écarte seule, et quatre voisines s'accordent au lieu de deux. En haut à
droite, L'ÉPREUVE : le nuage des colonnes communes, et cette fois les colonnes fortes pointent vers un
axe plus que tout rebrassage. En bas à gauche, L'ÉTALON, qui tient — et dit que la règle voit aussi une
queue propre à une rangée. En bas à droite, L'ATTRIBUTION, et c'est le panneau qui conclut : ce sont
les RANGÉES qui ont fait la différence, pas les colonnes.

  uv run python src/figures/figure_cinq_rangees_designent_elles_la_fautive.py \\
      --json docs/mesures/cinq_rangees_designent_elles_la_fautive.json \\
      --sortie docs/images/219_cinq_rangees_designent_elles_la_fautive.png
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
    """Le JSON de `cinq_rangees_designent_elles_la_fautive.py`.

    ⚠⚠⚠ LES REFUS SONT CEUX QUI FERAIENT LIRE UNE AUTRE TRANCHE SOUS CE NOM. Sans la relecture de
    `211`, cinq rangées lues aujourd'hui ne seraient pas comparables à trois lues hier ; sans le
    contrôle à trois rangées, le gain ne serait attribué à rien.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    if not (d.get("letalon") or {}).get("decidable"):
        raise SystemExit("l'étalon manque — un verdict sans étalon ne dit rien")
    for cle in ("la_reproduction", "lepreuve", "par_colonne", "le_detail_aux_colonnes_de_218",
                "sur_les_colonnes_de_218", "les_trois_rangees_de_211_sur_toutes_leurs_colonnes",
                "la_regle_de_la_porte", "le_verdict"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    k = v.get("le_nombre_de_rangees_lues")
    if not v.get("letalon_est_valide"):
        return "L'ÉTALON NE TIENT PAS : AUCUN VERDICT"
    if v.get("lepreuve_voit"):
        return f"{k} RANGÉES DÉSIGNENT LA FAUTIVE : L'ÉCART EXTRÊME EST PORTÉ PAR UNE RANGÉE"
    if v.get("elles_suffisent_au_nombre_observe"):
        return "L'ÉCART EXTRÊME EST PORTÉ PAR LA COLONNE, ET UN VOTE N'Y PEUT RIEN"
    return f"MÊME {k} RANGÉES NE DÉCIDENT PAS"


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

    ep, po, et, ve = d["lepreuve"], d["la_regle_de_la_porte"], d["letalon"], d["le_verdict"]
    det, pc, rep = d["le_detail_aux_colonnes_de_218"], d["par_colonne"], d["la_reproduction"]
    c218, t3, p218 = (d["sur_les_colonnes_de_218"],
                      d["les_trois_rangees_de_211_sur_toutes_leurs_colonnes"],
                      d["ce_que_218_a_rendu"])

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"rangées {', '.join(str(r) for r in d['les_rangees'])} relues ensemble · "
           f"{d['combien_de_colonnes']} colonnes communes · les trois de `211` retombent sur ses pas "
           f"(écart {', '.join(_fr(x, 4) for x in rep['les_ecarts_les_plus_grands'].values())} vx)",
           petit, GRIS)

    # ── PANNEAU 1 · LES DEUX COLONNES DE 218, A CINQ ────────────────────────────────────────
    panneau(50, 88, 660, 404, "LES DEUX COLONNES DE `218`, LUES À CINQ RANGÉES")
    lues = {c: x for c, x in det.items() if x.get("lue_par_les_cinq")}
    vals = [abs(a) for x in lues.values() for a in x["les_anomalies_en_voxels"].values()]
    ech = max(vals) * 1.15 if vals else 1.0
    cx, demi = 400, 140
    y = 124
    for col, x in sorted(lues.items()):
        ecrire(66, y, f"colonne {col} · `218` désignait la rangée {x['la_rangee_designee_par_218']}",
               0, ENCRE)
        y += 18
        for r, a in x["les_anomalies_en_voxels"].items():
            fautive = int(r) == int(x["la_rangee_designee"])
            coul = ALERTE if fautive else CONTRE
            ecrire(90, y - 1, f"rangée {r}", 0, ENCRE if fautive else GRIS)
            bout = cx + demi * float(a) / ech
            art.rectangle([min(cx, bout), y, max(cx, bout), y + 9], fill=coul)
            points.append((bout, y + 9))
            barres.append((abs(bout - cx), demi))
            ecrire(560, y - 1, f"{_fr(a, 2)} vx", 0, coul)
            y += 15
        ecrire(90, y + 2,
               f"désigne {x['la_rangee_designee']} · proximité {_fr(x['la_proximite'], 4)} · rang "
               f"d'énergie {x['le_rang_de_lenergie']}", 0, BON if x["la_meme_rangee_que_218"] else ALERTE)
        y += 30
    art.line([cx, 140, cx, y - 28], fill=TRAIT, width=1)
    ecrire(66, 380, "la même rangée s'écarte seule, et quatre voisines s'accordent au lieu de deux",
           0, ENCRE)

    # ── PANNEAU 2 · L'EPREUVE ────────────────────────────────────────────────────────────────
    panneau(700, 88, 1310, 404, "L'ÉPREUVE · la forme des colonnes contre leur énergie")
    e_, p_ = pc["les_energies"], pc["les_proximites"]
    seuil = float(ep["le_seuil_denergie"])
    emax = max(max(e_), seuil) * 1.06
    pmin = min(p_) - 0.01
    gx0, gx1, gy0, gy1 = 760, 1280, 126, 280

    def px(e):
        return gx0 + (gx1 - gx0) * float(e) / emax

    def py(p):
        return gy1 - (gy1 - gy0) * (float(p) - pmin) / (1.0 - pmin)

    art.line([gx0, gy1, gx1, gy1], fill=TRAIT, width=1)
    art.line([gx0, gy0, gx0, gy1], fill=TRAIT, width=1)
    xs = px(seuil)
    art.line([xs, gy0, xs, gy1], fill=ENCRE, width=1)
    ecrire(xs + 4, gy1 + 4, f"le maximum gaussien = {_fr(seuil, 2)}", 0, ENCRE)
    for e, p in zip(e_, p_):
        x_, y_ = px(e), py(p)
        art.ellipse([x_ - 2, y_ - 2, x_ + 2, y_ + 2], fill=ALERTE if e > seuil else GRIS)
        nuage.append((x_, y_))
        points.append((x_, y_))
    ecrire(gx0 - 44, gy0 - 4, "forme", 0, GRIS)
    ecrire(gx0 - 22, gy1 - 6, _fr(pmin, 2), 0, GRIS)
    ecrire(gx1 - 90, gy1 + 4, "énergie blanchie", 0, GRIS)
    ecrire(716, 302,
           f"{ep['combien_de_colonnes_fortes']} colonnes fortes · proximité moyenne "
           f"{_fr(ep['la_proximite_observee'], 4)} contre {_fr(ep['la_proximite_du_nul_mediane'], 4)}"
           f" pour le rebrassage médian", 0, ENCRE)
    ecrire(716, 320,
           f"et {_fr(ep['la_proximite_du_nul_la_plus_forte'], 4)} pour le plus fort : "
           f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']} rebrassages au moins aussi "
           f"forts, l'épreuve voit", 0, BON if ep["elle_voit"] else ALERTE)
    ecrire(716, 344,
           f"la règle de la porte, portée comme contrôle : "
           f"{po.get('les_tirages_au_moins_aussi_forts')}/{po.get('tirages')}", 0, GRIS)
    designees = sorted({r for e, r in zip(e_, pc["les_rangees_designees"]) if e > seuil})
    ecrire(716, 362, f"les colonnes fortes désignent les rangées "
                     f"{', '.join(str(r) for r in designees)}", 0, GRIS)
    ecrire(716, 380, "⚠ pas toutes : les plus énergiques ne pointent pas toutes vers un axe", 0,
           ALERTE)

    # ── PANNEAU 3 · L'ETALON ─────────────────────────────────────────────────────────────────
    panneau(50, 428, 660, 762, "L'ÉTALON · il tient, et il voit aussi une queue propre")
    ecrire(66, 462,
           f"matières de {et['les_colonnes_par_matiere']} colonnes aux cinq bruits propres mesurés · "
           f"{et['le_compte_decisif']} tirages par ligne", 0, GRIS)
    lignes = [("bruit gaussien", et["le_faux"], CONTRE),
              (f"PIÈGE : queues partagées, κ = {_fr(et['laplatissement_du_piege'], 2)}",
               et["le_piege"], CONTRE),
              ("queue propre à une rangée (nommé)", et["la_queue_propre"], TRAIT),
              ("règle de la porte, sur du bruit", et["la_regle_de_la_porte_sur_du_bruit"], ALERTE)]
    tx, tw = 330, 220
    yy = 490
    for nom, t, coul in lignes:
        ecrire(66, yy, nom, 0, ENCRE)
        barre(tx, yy, tw, t["le_taux"], 10, coul, cle=nom)
        ecrire(tx + tw + 10, yy - 1, f"{t['les_vus']}/{t['sur']}", 0, GRIS)
        yy += 26
    xg = tx + tw * 2.0 * float(d["la_garantie_du_nul"])
    art.line([xg, 484, xg, yy - 10], fill=BON, width=2)
    ecrire(xg - 20, yy - 6, "deux fois la garantie", 0, BON)
    yy += 20
    fa = et["les_sauts_du_face_a_face"]
    ecrire(66, yy, f"sur les mêmes matières à {fa} sauts de "
                   f"{_fr(et['lamplitude_des_sauts_en_voxels'], 2)} vx :", 0, ENCRE)
    yy += 22
    ecrire(66, yy, "règle déclarée", 0, ENCRE)
    barre(tx, yy, tw, et["la_regle_declaree_sur_les_memes_sauts"]["le_taux"], 10, CONTRE,
          cle="déclarée sur les sauts")
    ecrire(tx + tw + 10, yy - 1, f"{et['la_regle_declaree_sur_les_memes_sauts']['les_vus']}/"
                                 f"{et['la_regle_declaree_sur_les_memes_sauts']['sur']}", 0, GRIS)
    yy += 24
    ecrire(66, yy, "règle de la porte", 0, ALERTE)
    barre(tx, yy, tw, et["la_regle_de_la_porte_sur_des_sauts"]["le_taux"], 10, ALERTE)
    ecrire(tx + tw + 10, yy - 1, f"{et['la_regle_de_la_porte_sur_des_sauts']['les_vus']}/"
                                 f"{et['la_regle_de_la_porte_sur_des_sauts']['sur']}", 0, GRIS)
    ecrire(66, 712, "⚠ une queue lourde propre à une rangée est localisée elle aussi : la règle la",
           0, ALERTE)
    ecrire(66, 728, "voit, et c'est la même chose pour un vote — saut et queue propre restent confondus",
           0, ALERTE)

    # ── PANNEAU 4 · L'ATTRIBUTION ────────────────────────────────────────────────────────────
    panneau(700, 428, 1310, 762, "L'ATTRIBUTION · ce sont les rangées, pas les colonnes")
    ecrire(716, 462, "la même épreuve, quatre matières :", 0, GRIS)
    cas = [(f"trois rangées, {p218['les_colonnes_de_lepreuve_de_218']} colonnes (`218`)",
            p218["les_tirages_de_218_au_moins_aussi_forts"], ep["tirages"], False),
           (f"trois rangées, {t3['combien_de_colonnes_communes']} colonnes (relues)",
            t3["les_tirages_au_moins_aussi_forts"], t3["tirages"], bool(t3["elle_voit"])),
           (f"cinq rangées, {c218['combien_de_colonnes_communes']} colonnes de `218`",
            c218["les_tirages_au_moins_aussi_forts"], c218["tirages"], bool(c218["elle_voit"])),
           (f"cinq rangées, {d['combien_de_colonnes']} colonnes",
            ep["les_tirages_au_moins_aussi_forts"], ep["tirages"], bool(ep["elle_voit"]))]
    yy = 490
    for nom, au, tir, voit in cas:
        ecrire(716, yy, nom, 0, ENCRE)
        ecrire(1060, yy, f"{au}/{tir}", 0, GRIS)
        ecrire(1120, yy, "voit" if voit else "ne voit pas", 0, BON if voit else ALERTE)
        yy += 24
    yy += 16
    ecrire(716, yy, f"l'étalon, à {et['les_sauts_de_lechelle_en_rangees']} sauts de "
                    f"{_fr(et['lamplitude_des_sauts_en_voxels'], 2)} vx :", 0, ENCRE)
    yy += 22
    rx, rw = 900, 250
    for x in et["lechelle_en_rangees"]:
        ok = x["les_vus"] == x["sur"]
        ecrire(716, yy, f"{x['combien_de_rangees']} rangées", 0, ENCRE)
        barre(rx, yy, rw, x["les_vus"] / float(x["sur"]), 10, BON if ok else ALERTE)
        ecrire(rx + rw + 10, yy - 1, f"{x['les_vus']}/{x['sur']}", 0, GRIS)
        ecrire(800, yy, f"piège {_fr(x['le_taux_sur_le_piege'], 3)}", 0, GRIS)
        yy += 22
    ecrire(716, 728, "★ trois rangées ne voient pas, même sur plus de colonnes ; cinq voient, même",
           0, ENCRE)
    ecrire(716, 744, "sur les colonnes de `218`", 0, ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"CE QUI RESTE À MESURER : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    ecrire(50, 842,
           "★ aux deux colonnes où tombent les extrêmes de `217`, la rangée que trois voisines "
           "désignaient est celle que cinq désignent.", moyen, ENCRE)
    ecrire(50, 866,
           "     Un vote de cinq voisines désigne donc la rangée qui casse : la moitié de ce qui "
           "remplace l'humain, l'autre étant de la corriger.", moyen, ENCRE)
    ecrire(50, 900,
           "★ la suite : corrigé par ce vote, deux rangées voisines restent-elles sur le même feuillet ?",
           moyen, ENCRE)
    ecrire(50, 934,
           "⚠ ce qui n'est PAS établi : qu'un saut se distingue d'une queue propre à une rangée, ni "
           "que toutes les colonnes fortes soient votables.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_219.png"
    _, poses, cadres, barres, points, nuage, longueurs = dessiner(d, tmp)

    def _v(valide, voit, suff):
        return {"le_verdict": {"letalon_est_valide": valide, "lepreuve_voit": voit,
                               "elles_suffisent_au_nombre_observe": suff,
                               "le_nombre_de_rangees_lues": 5}}

    v("★★★★ les titres possibles sont DISTINCTS, et un étalon invalide prime",
      len({le_titre(_v(a, b, c)) for a in (True, False) for b in (True, False)
           for c in (True, False)}) == 4 and le_titre(_v(False, True, True)) == le_titre(
          _v(False, False, False)))
    v("★★★ le titre LIT le verdict au lieu de le recalculer",
      ("DÉSIGNENT LA FAUTIVE" in le_titre(d))
      == (d["le_verdict"]["letalon_est_valide"] and d["le_verdict"]["lepreuve_voit"]))
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
      len(nuage) == len(d["par_colonne"]["les_colonnes"]) == d["combien_de_colonnes"])
    v("★★★★ et chaque point du nuage reste dans son panneau",
      all(700 <= x <= 1310 and 88 <= y <= 404 for x, y in nuage))
    v("★★★★ tout le panneau de l'étalon est sur UNE échelle : les longueurs suivent les taux",
      abs(longueurs["déclarée sur les sauts"] / longueurs["règle de la porte, sur du bruit"]
          - d["letalon"]["la_regle_declaree_sur_les_memes_sauts"]["le_taux"]
          / d["letalon"]["la_regle_de_la_porte_sur_du_bruit"]["le_taux"]) < 0.02, str(longueurs))

    txt = " ".join(t for _, _, t, _ in poses)
    det = {c: x for c, x in d["le_detail_aux_colonnes_de_218"].items() if x.get("lue_par_les_cinq")}
    v("★★★★ elle porte chaque colonne de `218`, la rangée qu'il désignait et celle que cinq désignent",
      all(f"colonne {c}" in txt and f"désignait la rangée {x['la_rangee_designee_par_218']}" in txt
          and f"désigne {x['la_rangee_designee']}" in txt for c, x in det.items()))
    v("★★★★ elle porte les anomalies des CINQ rangées à chaque colonne",
      all(f"{_fr(a, 2)} vx" in txt for x in det.values() for a in x["les_anomalies_en_voxels"].values()))
    ep = d["lepreuve"]
    v("★★★★ elle porte le compte de l'épreuve et celui de la règle de la porte",
      f"{ep['les_tirages_au_moins_aussi_forts']}/{ep['tirages']}" in txt
      and f"{d['la_regle_de_la_porte']['les_tirages_au_moins_aussi_forts']}/" in txt)
    v("★★★★ elle porte les QUATRE matières de l'attribution avec leurs comptes",
      f"{d['les_trois_rangees_de_211_sur_toutes_leurs_colonnes']['les_tirages_au_moins_aussi_forts']}/"
      in txt and f"{d['ce_que_218_a_rendu']['les_tirages_de_218_au_moins_aussi_forts']}/" in txt
      and f"{d['sur_les_colonnes_de_218']['combien_de_colonnes_communes']} colonnes de `218`" in txt)
    et = d["letalon"]
    v("★★★★ elle porte le taux de faux, le PIÈGE, la queue propre et la porte sur du bruit",
      all(f"{t['les_vus']}/{t['sur']}" in txt for t in
          (et["le_faux"], et["le_piege"], et["la_queue_propre"],
           et["la_regle_de_la_porte_sur_du_bruit"])))
    v("★★★★ elle porte chaque barreau de l'échelle en rangées",
      all(f"{x['combien_de_rangees']} rangées" in txt and f"{x['les_vus']}/{x['sur']}" in txt
          for x in et["lechelle_en_rangees"]))
    v("★★★★ elle porte la relecture de `211`, qui rend les cinq rangées comparables",
      all(_fr(x, 4) in txt for x in d["la_reproduction"]["les_ecarts_les_plus_grands"].values())
      and "retombent sur ses pas" in txt)
    v("★★★★ elle dit ce qui n'est PAS établi — saut contre queue propre, et les colonnes non votables",
      "n'est PAS établi" in txt and "queue propre" in txt and "votables" in txt)
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
                   / "cinq_rangees_designent_elles_la_fautive.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "219_cinq_rangees_designent_elles_la_fautive.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
