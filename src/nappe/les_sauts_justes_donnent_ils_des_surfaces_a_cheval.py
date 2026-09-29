"""Parmi les sauts que la lecture stricte dit justes sur les graines 4 à 8, combien donnent une surface à cheval sur le tour attendu et son voisin, et le compte de 345 le voit-il ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL POINT D'UNE SURFACE DONNÉE PAR UN SAUT JUSTE NE SOIT RAPPORTÉ AUX TOURS VOISINS DU TOUR
ATTENDU. Ce qui était vu avant d'écrire : tout ce que `296` à `348` publient, dont `R4-F533` et `R4-F534` (la surface que donne le
troisième saut de la chaîne bornée, graine 8, que la lecture stricte dit juste et que `328` et `345` tiennent, est sur `5753_-1` là où
la surface suivante est sur `5753_-2` : elle est à cheval sur deux tours voisins sans en retrouver qu'un). Le compte de `345` y trouvait
32 points restés sur la feuille de départ sur 871.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P145`. La lecture stricte ne voit une surface à cheval que lorsqu'elle retrouve les deux
tours. Si d'autres sauts justes donnent des surfaces à cheval sans le dire, les bilans de `344` et `345` comptent comme justes des sauts
qui ne le sont qu'en partie ; et si le compte de `345`, point par point, voit les points restés en arrière ou partis trop loin, un rouleau
sans tracé peut refuser une surface à cheval au moment où elle naît.

## Ce qui est fait

- **Les chaînes et le compte** : ceux de `347`, rejoués par sa mesure ; ils doivent redonner ce que `344` et `345` publient, sans quoi la
  tranche est indécidable.
- **Les sauts** : ceux que `344` dit justes, sur les graines 4 à 8. Le tour de départ est le seul que retrouve la surface d'avant, le tour
  attendu son voisin du côté du saut, le tour d'au-delà le voisin suivant.
- **Les points** : ceux du compte de `345`, au plus 1200 points posés de la surface que donne le saut. Un point est posé sur un tour
  publié si le sommet de ce tour le plus proche est en face de lui, le long de sa normale, à au plus un quart de pas, par la comparaison
  de `321`. Un point est **resté** s'il est posé sur le tour de départ et pas sur le tour attendu ; **au-delà** s'il est posé sur le tour
  d'au-delà et pas sur le tour attendu.
- **Une surface à cheval** : au moins 50 points restés, ou au moins 50 points au-delà.
- **Le compte le voit** sous une surface à cheval si, dans chaque groupe d'au moins 50 points, les trois quarts sont comptés comme la
  place le veut : aucune feuille franchie pour un point resté, deux ou plus pour un point au-delà. Un point non compté ne l'est pas comme
  la place le veut.
- **Le contrôle** : sous au moins les trois quarts des surfaces justes qui ont au moins 50 points posés sur un tour, au moins la moitié
  de ces points doivent être posés sur le tour attendu ; sinon la mesure ne lit pas les tours sous les surfaces et la tranche est
  indécidable.
- **La règle** : si aucune surface juste n'est à cheval, **aucun saut juste n'est à cheval** ; sinon, si le compte les voit toutes, **il
  les voit toutes** ; aucune, **il n'en voit aucune** ; sinon, **il en voit certaines**.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, n des N sauts justes donnent une surface à cheval sur le tour attendu et son voisin**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Chaque surface juste, ses points restés et au-delà ; la surface du troisième saut de la chaîne bornée, graine 8, celle de `348` ; les
mêmes lectures sur les graines 1 à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface à cheval l'est par elle-même ou parce qu'un tour publié est mal posé ; et ce que
vaut tout ceci sur PHerc0358.

Usage :
    uv run python src/nappe/les_sauts_justes_donnent_ils_des_surfaces_a_cheval.py --verifier
    uv run python src/nappe/les_sauts_justes_donnent_ils_des_surfaces_a_cheval.py \\
        --json docs/mesures/les_sauts_justes_donnent_ils_des_surfaces_a_cheval.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402

LE_MINIMUM_DE_POINTS = 50
LA_PART_VUE = 0.75
LA_PART_DU_CONTROLE = 0.75
LA_PART_SUR_LATTENDU = 0.5
LA_SURFACE_DE_348 = {"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins", "le_saut": 3}


def le_groupe(comptes: list, voulu) -> dict:
    """Des points d'un groupe : combien, leurs comptes, et la part comptée comme `voulu(c)` le veut, None sous `LE_MINIMUM_DE_POINTS`."""
    n = Counter("non compté" if c is None else str(c) for c in comptes)
    return {"les_points": len(comptes), "les_comptes": dict(sorted(n.items())),
            "la_part_vue": round(sum(1 for c in comptes if c is not None and voulu(c)) / len(comptes), 4)
            if len(comptes) >= LE_MINIMUM_DE_POINTS else None}


def la_lecture(avant: dict, en_plus: dict | None, sens: int) -> dict | None:
    """Sous la surface d'un saut dont la surface d'avant retrouve un seul tour : les points posés sur le tour attendu, restés sur le tour de
    départ, partis au-delà ; si la surface est à cheval, et si le compte le voit. None sans surface d'avant à un tour ou sans points."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1 or en_plus is None or "les_poses" not in en_plus:
        return None
    w0 = r0[0]
    wa, wd = w0 + sens, w0 + 2 * sens
    paires = list(zip(en_plus["les_comptes"], en_plus["les_poses"]))
    restes = le_groupe([c for c, w in paires if w0 in w and wa not in w], lambda c: c == 0)
    dela = le_groupe([c for c, w in paires if wd in w and wa not in w], lambda c: c >= 2)
    groupes = [g for g in (restes, dela) if g["les_points"] >= LE_MINIMUM_DE_POINTS]
    return {"le_tour_de_depart": w0, "le_tour_attendu": wa, "le_tour_dau_dela": wd, "les_points": len(paires),
            "les_points_poses": sum(1 for _, w in paires if w), "sur_le_tour_attendu": sum(1 for _, w in paires if wa in w),
            "restes": restes, "au_dela": dela, "a_cheval": bool(groupes),
            "vu": (all(g["la_part_vue"] >= LA_PART_VUE for g in groupes) if groupes else None)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344") or not d.get("redonne_345"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344 et 345"}
    justes = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_justesse"] == "juste"]
    lues = [s["la_surface"] for s in justes if s["la_surface"] is not None and s["la_surface"]["les_points_poses"] >= LE_MINIMUM_DE_POINTS]
    bien = sum(1 for a in lues if a["sur_le_tour_attendu"] >= LA_PART_SUR_LATTENDU * a["les_points_poses"])
    if not lues or bien < LA_PART_DU_CONTROLE * len(lues):
        return {"decidable": False, "lissue": "indécidable : la mesure ne lit pas les tours sous les surfaces justes"}
    cheval = [s for s in justes if s["la_surface"] is not None and s["la_surface"]["a_cheval"]]
    tete = (f"sur les graines 4 à 8, {len(cheval)} des {len(justes)} sauts justes donnent une surface à cheval sur le tour attendu et "
            f"son voisin")
    if not cheval:
        return {"decidable": True, "n": 0, "N": len(justes), "k": 0, "lissue": f"{tete} ; aucun saut juste n'est à cheval"}
    k = sum(1 for s in cheval if s["la_surface"]["vu"])
    suite = "le compte les voit toutes" if k == len(cheval) else "il n'en voit aucune" if k == 0 else "il en voit certaines"
    return {"decidable": True, "n": len(cheval), "N": len(justes), "k": k, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}

    def garder(dep, arr, lv):
        r = m345.les_comptes_point_par_point(dep, arr, lv, m321.LE_PAS_L2)
        out = {"les_feuilles": m345.le_resume(r)}
        if arr is None or not arr["valide"].any():
            return out
        lect = m329.les_lectures(arr["la_nappe"][arr["valide"]] * m321.LE_FACTEUR, tours)
        out["les_retrouves"] = sorted((t for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)
        if r is not None:
            out["les_comptes"] = r["les_comptes"]
            out["les_poses"] = m347.les_poses(r["les_points"] * m321.LE_FACTEUR, r["les_normales"], tours)
        return out

    d344 = m344.mesurer(en_plus=garder)
    publie344 = json.loads(m345.CE_QUE_344_A_PUBLIE.read_text())
    surfaces, redonne345, saccordent = m347.les_surfaces_rejouees(d344, la_lecture, quels=("juste", "faux : deux tours",
                                                                                              "faux : un autre tour", "faux : le tour manqué"))
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum_de_points": LE_MINIMUM_DE_POINTS, "la_part_vue": LA_PART_VUE,
                            "la_part_du_controle": LA_PART_DU_CONTROLE, "la_part_sur_lattendu": LA_PART_SUR_LATTENDU,
                            "la_surface_de_348": LA_SURFACE_DE_348, "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(m345.sans_le_compte(d344["les_chaines"]))) == publie344["les_chaines"]
                             and d344["le_verdict"] == publie344["le_verdict"] and d344["redonne_328"]),
         "redonne_345": redonne345, "les_lectures_saccordent": saccordent, "les_surfaces": surfaces}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
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

    g = le_groupe([0] * 40 + [1] * 5 + [None] * 5, lambda c: c == 0)
    v("★★★★ un point non compté n'est pas vu", g["la_part_vue"] == 0.8 and g["les_comptes"] == {"0": 40, "1": 5, "non compté": 5}, str(g))
    v("★★★ sous 50 points : pas de part", le_groupe([0] * 49, lambda c: c == 0)["la_part_vue"] is None)
    v("★★★ au-delà, deux feuilles ou plus sont ce que la place veut",
      le_groupe([2] * 30 + [3] * 20 + [1] * 50, lambda c: c >= 2)["la_part_vue"] == 0.5)

    R, N = "retrouve", "ne retrouve pas"
    en_plus = {"les_comptes": [1] * 300 + [0] * 60 + [1] * 20 + [2] * 50,
               "les_poses": [[-3]] * 300 + [[-2]] * 80 + [[-4]] * 50}
    a = la_lecture({"-2": R, "-1": N}, en_plus, -1)
    v("★★★★ côté moins : resté sur w, attendu w - 1, au-delà w - 2 ; 80 restés dont 60 comptés à zéro : à cheval, vu",
      a is not None and (a["le_tour_de_depart"], a["le_tour_attendu"], a["le_tour_dau_dela"]) == (-2, -3, -4)
      and a["restes"]["les_points"] == 80 and a["restes"]["la_part_vue"] == 0.75 and a["au_dela"]["la_part_vue"] == 1.0
      and a["a_cheval"] and a["vu"] is True and a["sur_le_tour_attendu"] == 300 and a["les_points_poses"] == 430, str(a))
    moins = dict(en_plus, les_comptes=[1] * 300 + [0] * 59 + [1] * 21 + [2] * 50)
    v("★★★ un peu sous les trois quarts de restés comptés à zéro : pas vu", la_lecture({"-2": R}, moins, -1)["vu"] is False)
    recouvre = {"les_comptes": [1] * 300 + [0] * 80, "les_poses": [[-3]] * 300 + [[-2, -3]] * 80}
    a = la_lecture({"-2": R}, recouvre, -1)
    v("★★★★ un point posé sur le tour de départ ET sur le tour attendu n'est pas resté", a["restes"]["les_points"] == 0
      and not a["a_cheval"] and a["vu"] is None, str(a))
    loin = {"les_comptes": [1] * 300 + [1] * 60 + [None] * 10, "les_poses": [[-3]] * 300 + [[-4]] * 60 + [[]] * 10}
    a = la_lecture({"-2": R}, loin, -1)
    v("★★★★ au-delà, des points qui ne franchissent qu'une feuille ne sont pas vus ; un point sans tour n'est pas posé",
      a["a_cheval"] and a["vu"] is False and a["au_dela"]["la_part_vue"] == 0.0 and a["les_points_poses"] == 360
      and a["les_points"] == 370, str(a))
    peu = {"les_comptes": [1] * 300 + [0] * 49, "les_poses": [[-3]] * 300 + [[-2]] * 49}
    v("★★★ 49 points restés : pas à cheval", not la_lecture({"-2": R}, peu, -1)["a_cheval"])
    a = la_lecture({"-3": R}, en_plus, 1)
    v("★★★ côté plus, le tour attendu est w + 1", (a["le_tour_attendu"], a["le_tour_dau_dela"]) == (-2, -1)
      and a["restes"]["les_points"] == 300, str(a))
    v("★★★ une surface d'avant à deux tours, ou sans points : rien à lire",
      la_lecture({"-1": R, "-2": R}, en_plus, -1) is None and la_lecture({"-2": R}, {"les_feuilles": {}}, -1) is None)

    def s_(rang, j, cheval, vu, poses=400, att=300):
        return {"le_rang": rang, "la_justesse": j, "la_surface": {"a_cheval": cheval, "vu": vu, "les_points_poses": poses,
                                                                  "sur_le_tour_attendu": att}}
    base = lambda ss: {"les_pannes": [], "redonne_344": True, "redonne_345": True, "les_surfaces": ss}  # noqa: E731
    J = "juste"
    v("★★★★ aucune surface juste à cheval : aucun saut juste ne l'est",
      le_verdict(base([s_(5, J, False, None)] * 4)).get("lissue", "").endswith("aucun saut juste n'est à cheval"))
    v("★★★★ toutes vues : le compte les voit toutes",
      le_verdict(base([s_(5, J, False, None)] * 3 + [s_(6, J, True, True)] * 2)).get("lissue", "").endswith("les voit toutes"))
    v("★★★★ aucune vue", le_verdict(base([s_(5, J, False, None)] * 3 + [s_(6, J, True, False)])).get("lissue", "").endswith("aucune"))
    v("★★★★ certaines", le_verdict(base([s_(6, J, True, True), s_(6, J, True, False)] + [s_(5, J, False, None)] * 3))
      .get("lissue", "").endswith("en voit certaines"))
    v("★★★★ seuls les sauts justes des graines 4 à 8 comptent",
      le_verdict(base([s_(5, J, False, None)] * 3 + [s_(2, J, True, False), s_(5, "faux : deux tours", True, False)])).get("n") == 0)
    v("★★★ le compte : n sur N sauts justes", le_verdict(base([s_(5, J, False, None)] * 3 + [s_(6, J, True, True)])).get("N") == 4)
    v("★★★★ le contrôle : des surfaces où la mesure ne voit pas le tour attendu, indécidable",
      not le_verdict(base([s_(5, J, False, None, att=100)] * 3 + [s_(5, J, False, None)]))["decidable"]
      and le_verdict(base([s_(5, J, False, None, att=200)] * 3 + [s_(5, J, False, None, att=0)]))["decidable"])
    v("★★★ les surfaces de moins de 50 points posés ne comptent pas au contrôle",
      le_verdict(base([s_(5, J, False, None, poses=49, att=0)] * 5 + [s_(5, J, False, None)]))["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 344 ou 345 : indécidable",
      not le_verdict(dict(base([s_(5, J, False, None)]), redonne_345=False))["decidable"]
      and not le_verdict(dict(base([s_(5, J, False, None)]), redonne_344=False))["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
