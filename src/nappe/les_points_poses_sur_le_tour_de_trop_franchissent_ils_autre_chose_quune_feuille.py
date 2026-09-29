"""Là où une surface tenue à tort sur les graines 4 à 8 est posée sur son tour de trop, les points du compte de 345 y franchissent-ils autre chose qu'une feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL POINT DU COMPTE DE `345` NE SOIT RAPPORTÉ AU TOUR PUBLIÉ SUR LEQUEL IL EST POSÉ. Ce qui était vu
avant d'écrire : tout ce que `296` à `346` publient, dont `R4-F531` (le compte tient trois des quatre sauts à deux tours des graines 4 à
8, qui ne passent qu'une feuille sur 75 à 89 % de leurs points comptés) et `R4-F532` (sous les surfaces à deux tours des graines 4 à 8,
aucun sommet d'un tour publié posé sur la surface n'a l'autre tour à un quart de pas : celles qui sont lues sont à cheval sur deux
feuilles). Deux des trois surfaces tenues retrouvent un tour de trop à plusieurs tours de celui d'où part le saut, la troisième le tour
même d'où il part.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P143`. Une surface à cheval est sur la feuille suivante ici et sur une autre là. Si les
points posés sur le tour de trop passent, pour le compte, autre chose qu'une feuille, le compte voit l'endroit où la surface change de
feuille, et un critère sans référent qui l'exige partout sur la surface peut refuser ces sauts. Sinon, il faut autre chose.

## Ce qui est fait

- **Les chaînes** : celles de `344`, rejouées par sa mesure ; elles doivent redonner ce que `344` publie, et le compte de chaque saut ce
  que `345` publie, sans quoi la tranche est indécidable.
- **Les points** : ceux du compte de `345`, au plus 1200 points posés de la surface que donne le saut, chacun avec le nombre de feuilles
  de `m7` qu'il passe, ou non compté. Pour chaque tour publié que la surface retrouve, un point y est **posé** si le sommet de ce tour le
  plus proche est en face de lui, le long de sa normale, à au plus un quart de pas nominal, par la comparaison de `321`.
- **Les surfaces** : celles des sauts que `344` dit faux parce qu'ils retrouvent deux tours ; leur tour attendu est le voisin, du côté du
  saut, du seul tour que retrouve la surface d'avant, leur tour de trop les autres.
- **La lecture sous une surface** : parmi les points posés sur un tour de trop, la part que le compte dit franchir exactement une feuille,
  un point non compté n'en franchissant pas une ; de même parmi les points posés sur le tour attendu. Le compte **voit le changement**
  si la première part est d'au plus un quart et la seconde d'au moins les trois quarts ; il **ne le voit pas** sinon. Non lue si moins de
  50 points sont posés sur le tour de trop ou sur le tour attendu.
- **Le contrôle** : sous chaque surface à deux tours des graines 4 à 8 que `345` refuse et qui est lue, la part des points du tour de
  trop qui passent une feuille doit être plus petite que celle des points du tour attendu ; au moins une doit être lue. Sinon, la tranche
  est indécidable.
- **La règle** : sur les surfaces que `345` tient à tort aux graines 4 à 8 et qui sont lues, indécidable s'il y en a moins de deux. Si le
  compte voit le changement sous toutes, **il voit où la surface change de feuille** ; sous aucune, **il ne le voit pas** ; sinon, **il
  le voit sous certaines seulement**.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, le compte voit le changement de tour sous k des n surfaces tenues à tort qui sont
lues**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les points posés sur les deux tours à la fois ; chaque surface des graines 1 à 3 ; et, pour tous les sauts jugés des graines 4 à 8, la
part de tous les points du compte, et non des seuls points comptés, qui franchissent exactement une feuille, avec ce qu'elle tient au
seuil des trois quarts.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut, sur les sauts justes, un critère qui exige la même chose partout sur la surface ; et
ce que vaut tout ceci sur PHerc0358.

Usage :
    uv run python src/nappe/les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.py --verifier
    uv run python src/nappe/les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.py \\
        --json docs/mesures/les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.json
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

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_345_A_PUBLIE = LES_MESURES / "les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.json"
LA_PART_AU_PLUS = 0.25
LA_PART_AU_MOINS = 0.75
LE_MINIMUM_DE_POINTS = 50
VOIT, NE_VOIT_PAS, NON_LUE = "le compte voit le changement", "le compte ne le voit pas", "non lue"


def les_poses(pts: np.ndarray, normales: np.ndarray, tours: dict) -> list[list[int]]:
    """Pour chaque point, les tours publiés dont le sommet le plus proche est en face de lui à au plus un quart de pas."""
    out: list[list[int]] = [[] for _ in range(len(pts))]
    for t, tour in tours.items():
        u = m321.les_ecarts(pts, normales, m329.les_sommets_proches(tour, pts)[0])
        for i in np.flatnonzero(np.isfinite(u) & (np.abs(u) <= m321.LE_QUART)):
            out[i].append(t)
    return out


def le_groupe(comptes: list) -> dict:
    """Des points et de leurs comptes, combien en franchissent chaque nombre de feuilles, et la part qui en franchit exactement une ;
    un point non compté n'en franchit pas une, et la part est None sous `LE_MINIMUM_DE_POINTS` points."""
    n = Counter("non compté" if c is None else str(c) for c in comptes)
    return {"les_points": len(comptes), "les_comptes": dict(sorted(n.items())),
            "la_part_dune_feuille": round(n["1"] / len(comptes), 4) if len(comptes) >= LE_MINIMUM_DE_POINTS else None}


def la_lecture(avant: dict, en_plus: dict | None, sens: int) -> dict | None:
    """Sous une surface qui retrouve le tour attendu et d'autres : les points posés sur le tour attendu, sur un tour de trop, sur les deux,
    et ce que dit le compte ; None si la surface d'avant ne retrouve pas un seul tour, ou si la surface ne retrouve pas le tour attendu
    et un autre."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1 or en_plus is None or len(en_plus.get("les_retrouves", [])) < 2:
        return None
    attendu = r0[0] + sens
    if attendu not in en_plus["les_retrouves"]:
        return None
    de_trop = [t for t in en_plus["les_retrouves"] if t != attendu]
    paires = list(zip(en_plus["les_comptes"], en_plus["les_poses"]))
    ga = le_groupe([c for c, w in paires if attendu in w])
    gt = le_groupe([c for c, w in paires if any(t in w for t in de_trop)])
    pa, pt = ga["la_part_dune_feuille"], gt["la_part_dune_feuille"]
    lecture = NON_LUE if pa is None or pt is None else (VOIT if pt <= LA_PART_AU_PLUS and pa >= LA_PART_AU_MOINS else NE_VOIT_PAS)
    return {"le_tour_attendu": attendu, "les_tours_de_trop": de_trop, "sur_le_tour_attendu": ga, "sur_un_tour_de_trop": gt,
            "sur_les_deux": sum(1 for _, w in paires if attendu in w and any(t in w for t in de_trop)), "la_lecture": lecture}


def la_part_sur_tous(r: dict | None) -> float | None:
    """La part de tous les points du compte, comptés ou non, qui franchissent exactement une feuille."""
    if r is None or len(r["les_comptes"]) < LE_MINIMUM_DE_POINTS:
        return None
    return round(sum(c == 1 for c in r["les_comptes"]) / len(r["les_comptes"]), 4)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344"}
    if not d.get("redonne_345"):
        return {"decidable": False, "lissue": "indécidable : le compte rejoué ne redonne pas 345"}
    propres = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_surface"] is not None]
    ctl = [s["la_surface"] for s in propres if not s["tient_par_345"] and s["la_surface"]["la_lecture"] != NON_LUE]
    if not ctl:
        return {"decidable": False, "lissue": "indécidable : le contrôle n'est pas lu"}
    if any(c["sur_un_tour_de_trop"]["la_part_dune_feuille"] >= c["sur_le_tour_attendu"]["la_part_dune_feuille"] for c in ctl):
        return {"decidable": False, "lissue": "indécidable : sous une surface que 345 refuse, la mesure ne sépare pas les deux tours"}
    lues = [s for s in propres if s["tient_par_345"] and s["la_surface"]["la_lecture"] != NON_LUE]
    if len(lues) < 2:
        return {"decidable": False, "lissue": f"indécidable : {len(lues)} surface tenue à tort est lue"}
    k = sum(s["la_surface"]["la_lecture"] == VOIT for s in lues)
    tete = f"sur les graines 4 à 8, le compte voit le changement de tour sous {k} des {len(lues)} surfaces tenues à tort qui sont lues"
    suite = ("il voit où la surface change de feuille" if k == len(lues)
             else "il ne le voit pas" if k == 0 else "il le voit sous certaines seulement")
    return {"decidable": True, "k": k, "n": len(lues), "lissue": f"{tete} ; {suite}"}


def sur_tous_les_points(chaines: dict, graines: tuple) -> dict:
    """Rapporté à côté : un saut tient si les trois quarts de tous les points de son compte franchissent exactement une feuille."""
    recodees = {"les_chaines": {n: {"les_graines": [
        {"le_rang": g["le_rang"], "les_cotes": {c: {"les_sauts": [
            {"la_justesse": s["la_justesse"], "tient": bool(s["en_plus"] is not None and s["en_plus"]["la_part_sur_tous"] is not None
                                                            and s["en_plus"]["la_part_sur_tous"] >= LA_PART_AU_MOINS)}
            for s in x["les_sauts"]]} for c, x in g["les_cotes"].items()}} for g in ch["les_graines"]]} for n, ch in chaines.items()}}
    return m344.le_bilan(m344.les_sauts_de(recodees, graines))


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}

    def garder(dep, arr, lv):
        r = m345.les_comptes_point_par_point(dep, arr, lv, m321.LE_PAS_L2)
        out = {"les_feuilles": m345.le_resume(r), "la_part_sur_tous": la_part_sur_tous(r)}
        if arr is None or not arr["valide"].any():
            return out
        lect = m329.les_lectures(arr["la_nappe"][arr["valide"]] * m321.LE_FACTEUR, tours)
        out["les_retrouves"] = sorted((t for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)
        if len(out["les_retrouves"]) >= 2 and r is not None:
            out["les_comptes"] = r["les_comptes"]
            out["les_poses"] = les_poses(r["les_points"] * m321.LE_FACTEUR, r["les_normales"],
                                         {t: tours[t] for t in out["les_retrouves"]})
        return out

    d344 = m344.mesurer(en_plus=garder)
    publie344 = json.loads(m345.CE_QUE_344_A_PUBLIE.read_text())
    publie345 = json.loads(CE_QUE_345_A_PUBLIE.read_text())
    publiees = {n: json.loads((LES_MESURES / f).read_text()) for n, f in m340.LES_CHAINES.items()}
    nappes = {g["le_rang"]: {t: x["la_lecture"] for t, x in g["la_nappe"].items()} for g in publiees["sans relance"]["les_graines"]}
    surfaces, saccordent, redonne345 = [], True, True
    for n, ch in d344["les_chaines"].items():
        for g in ch["les_graines"]:
            t345 = next(y for y in publie345["les_chaines"][n]["les_graines"] if y["le_rang"] == g["le_rang"])
            for cote, x in g["les_cotes"].items():
                lect = m340.les_surfaces(n, publiees[n], nappes, g["le_rang"], cote)
                sauts345 = t345["les_cotes"][cote]["les_sauts"]
                redonne345 &= len(sauts345) == len(x["les_sauts"])
                for s, s345 in zip(x["les_sauts"], sauts345):
                    e = s["en_plus"]
                    redonne345 &= e is not None and e["les_feuilles"] == s345["les_feuilles"] and s["le_saut"] == s345["le_saut"]
                    if e is not None and "les_retrouves" in e:
                        saccordent &= e["les_retrouves"] == m340.les_retrouves(lect[s["le_saut"]])
                    if s["la_justesse"] != "faux : deux tours":
                        continue
                    surfaces.append({"la_chaine": n, "le_rang": g["le_rang"], "le_cote": cote, "le_saut": s["le_saut"],
                                     "tient_par_345": s345["tient"],
                                     "la_surface": la_lecture(lect[s["le_saut"] - 1], e, m344.LE_SENS[cote])})
                    print(json.dumps(surfaces[-1], ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part_au_plus": LA_PART_AU_PLUS, "la_part_au_moins": LA_PART_AU_MOINS,
                            "le_minimum_de_points": LE_MINIMUM_DE_POINTS, "le_quart_voxels": round(m321.LE_QUART, 3)},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(m345.sans_le_compte(d344["les_chaines"]))) == publie344["les_chaines"]
                             and d344["le_verdict"] == publie344["le_verdict"] and d344["redonne_328"]),
         "redonne_345": bool(redonne345), "les_lectures_saccordent": bool(saccordent), "les_surfaces": surfaces,
         "sur_tous_les_points": {"graines_4_a_8": sur_tous_les_points(d344["les_chaines"], m344.LES_GRAINES_PROPRES),
                                 "graines_1_a_3": sur_tous_les_points(d344["les_chaines"], (1, 2, 3))}}
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

    def tour(z, x0=0.0, x1=200.0):
        xs, ys = np.meshgrid(np.arange(x0, x1, 10.0), np.arange(0.0, 200.0, 10.0))
        p = np.stack([xs.ravel(), ys.ravel(), np.full(xs.size, float(z))], axis=1)
        return {"points": p, "normales": np.tile([0.0, 0.0, 1.0], (len(p), 1))}

    pts = np.concatenate([tour(100.0, 0.0, 100.0)["points"], tour(170.0, 100.0, 200.0)["points"]])
    nrm = np.tile([0.0, 0.0, 1.0], (len(pts), 1))
    p = les_poses(pts, nrm, {-3: tour(100.0), -2: tour(170.0)})
    v("★★★★ une surface à cheval : chaque point est posé sur le tour qu'il touche, et seulement lui",
      [w for w in p[:200]] == [[-3]] * 200 and [w for w in p[200:]] == [[-2]] * 200, str(p[:2] + p[-2:]))
    p = les_poses(pts, nrm, {-3: tour(100.0 + m321.LE_QUART + 1.0)})
    v("★★★★ un tour à un peu plus d'un quart de pas : aucun point n'y est posé", all(w == [] for w in p))
    p = les_poses(pts, nrm, {-3: tour(100.0 + m321.LE_QUART - 1.0)})
    v("★★★ un tour à un peu moins d'un quart de pas : les points en face y sont posés", sum(w == [-3] for w in p) == 200)
    g = le_groupe([1] * 30 + [0] * 10 + [None] * 10)
    v("★★★★ un point non compté ne franchit pas une feuille", g["la_part_dune_feuille"] == 0.6
      and g["les_comptes"] == {"0": 10, "1": 30, "non compté": 10}, str(g))
    v("★★★ moins de 50 points : pas de part", le_groupe([1] * 49)["la_part_dune_feuille"] is None
      and le_groupe([1] * 50)["la_part_dune_feuille"] == 1.0)

    R, N = "retrouve", "ne retrouve pas"
    en_plus = {"les_retrouves": [-2, -3], "les_comptes": [1] * 100 + [0] * 80 + [None] * 20 + [1] * 5,
               "les_poses": [[-3]] * 100 + [[-2]] * 100 + [[-2, -3]] * 5}
    s = la_lecture({"-2": R, "-1": N}, en_plus, -1)
    v("★★★★ côté moins, le tour attendu est w - 1 ; les points du tour de trop ne passent pas une feuille : le compte voit le changement",
      s is not None and s["le_tour_attendu"] == -3 and s["les_tours_de_trop"] == [-2] and s["la_lecture"] == VOIT
      and s["sur_un_tour_de_trop"]["la_part_dune_feuille"] == round(5 / 105, 4)
      and s["sur_le_tour_attendu"]["la_part_dune_feuille"] == 1.0 and s["sur_les_deux"] == 5, str(s))
    s = la_lecture({"-3": R}, en_plus, 1)
    v("★★★★ côté plus, le tour attendu est w + 1 : les rôles s'inversent, et il ne le voit pas",
      s is not None and s["le_tour_attendu"] == -2 and s["les_tours_de_trop"] == [-3] and s["la_lecture"] == NE_VOIT_PAS, str(s))
    pareil = dict(en_plus, les_comptes=[1] * 205)
    v("★★★★ les points du tour de trop passent une feuille comme les autres : il ne le voit pas",
      la_lecture({"-2": R}, pareil, -1)["la_lecture"] == NE_VOIT_PAS)
    net = {"les_retrouves": [-2, -3], "les_poses": [[-3]] * 100 + [[-2]] * 100}
    bord = dict(net, les_comptes=[1] * 100 + [1] * 25 + [0] * 75)
    v("★★★ un quart juste sur le tour de trop : il le voit", la_lecture({"-2": R}, bord, -1)["la_lecture"] == VOIT)
    juste = dict(net, les_comptes=[1] * 75 + [0] * 25 + [0] * 100)
    v("★★★ les trois quarts justes sur le tour attendu : il le voit", la_lecture({"-2": R}, juste, -1)["la_lecture"] == VOIT)
    mou = dict(net, les_comptes=[1] * 74 + [0] * 26 + [0] * 100)
    v("★★★ sous les trois quarts sur le tour attendu : il ne le voit pas", la_lecture({"-2": R}, mou, -1)["la_lecture"] == NE_VOIT_PAS)
    peu = {"les_retrouves": [-2, -3], "les_comptes": [1] * 100 + [0] * 40, "les_poses": [[-3]] * 100 + [[-2]] * 40}
    v("★★★ moins de 50 points sur le tour de trop : non lue", la_lecture({"-2": R}, peu, -1)["la_lecture"] == NON_LUE)
    tri = {"les_retrouves": [0, -3, -6], "les_comptes": [1] * 100 + [None] * 60 + [2] * 60,
           "les_poses": [[-3]] * 100 + [[0]] * 60 + [[-6]] * 60}
    s = la_lecture({"-2": R}, tri, -1)
    v("★★★ plusieurs tours de trop : leurs points sont pris ensemble", s["sur_un_tour_de_trop"]["les_points"] == 120
      and s["la_lecture"] == VOIT, str(s))
    v("★★★ une surface d'avant à deux tours, ou sans le tour attendu : rien à lire",
      la_lecture({"-1": R, "-2": R}, en_plus, -1) is None and la_lecture({"-5": R}, en_plus, -1) is None
      and la_lecture({"-2": R}, {"les_retrouves": [-3]}, -1) is None)
    v("★★★ la part sur tous les points : les non comptés pèsent", la_part_sur_tous({"les_comptes": [1] * 60 + [None] * 40}) == 0.6
      and la_part_sur_tous({"les_comptes": [1] * 49}) is None and la_part_sur_tous(None) is None)

    def s_(rang, tient_, lecture, pt=0.1, pa=0.9):
        return {"le_rang": rang, "tient_par_345": tient_,
                "la_surface": {"la_lecture": lecture, "sur_un_tour_de_trop": {"la_part_dune_feuille": pt},
                               "sur_le_tour_attendu": {"la_part_dune_feuille": pa}}}
    ctl = [s_(7, False, VOIT)]
    base = lambda ss: {"les_pannes": [], "redonne_344": True, "redonne_345": True, "les_surfaces": ctl + ss}  # noqa: E731
    v("★★★★ sous toutes les tenues lues : il voit où la surface change de feuille",
      le_verdict(base([s_(5, True, VOIT)] * 3)).get("lissue", "").endswith("change de feuille"))
    v("★★★★ sous aucune : il ne le voit pas", le_verdict(base([s_(5, True, NE_VOIT_PAS)] * 2)).get("lissue", "").endswith("ne le voit pas"))
    v("★★★★ sous certaines : seulement", le_verdict(base([s_(5, True, VOIT), s_(8, True, NE_VOIT_PAS)])).get("lissue", "")
      .endswith("certaines seulement"))
    v("★★★★ une tenue non lue est laissée ; deux lues suffisent",
      le_verdict(base([s_(5, True, VOIT)] * 2 + [s_(8, True, NON_LUE)])).get("n") == 2)
    v("★★★★ une seule tenue lue : indécidable", not le_verdict(base([s_(5, True, VOIT), s_(8, True, NON_LUE)]))["decidable"])
    v("★★★★ les surfaces des graines 1 à 3 ne comptent pas",
      le_verdict(base([s_(5, True, VOIT)] * 2 + [s_(2, True, NE_VOIT_PAS)])).get("lissue", "").endswith("change de feuille"))
    v("★★★★ le contrôle non lu : indécidable",
      not le_verdict({"les_pannes": [], "redonne_344": True, "redonne_345": True,
                      "les_surfaces": [s_(7, False, NON_LUE)] + [s_(5, True, VOIT)] * 3})["decidable"])
    v("★★★★ le contrôle qui ne sépare pas les deux tours : indécidable",
      not le_verdict({"les_pannes": [], "redonne_344": True, "redonne_345": True,
                      "les_surfaces": [s_(7, False, NE_VOIT_PAS, 0.8, 0.8)] + [s_(5, True, VOIT)] * 3})["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 344, ou un compte qui ne redonne pas 345 : indécidable",
      not le_verdict(dict(base([s_(5, True, VOIT)] * 3), redonne_344=False))["decidable"]
      and not le_verdict(dict(base([s_(5, True, VOIT)] * 3), redonne_345=False))["decidable"])

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
