"""Sur PHercParis4, une surface que l'accord de trois chaînes valide, comme `374` le fait sur PHerc0358, est-elle sur le tour publié que son compte corrigé lui donne ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE NE SOIT VALIDÉE SUR PHERCPARIS4. Ce qui était vu avant d'écrire : tout ce que `296` à
`378` publient, dont `R4-F560` (sur PHerc0358, trois chaînes d'une maille valident 25 des 120 surfaces, jusqu'à 6 tours de la nappe), `R4-F553`
(sur PHercParis4, graines 4 à 8, côtés moins, « même feuille » et « même tour publié » s'accordent sous 56 paires sur 56 pour deux chaînes
parties de graines différentes) et `R4-F556` (sur PHercParis4, deux tours d'écart font 20,978 à 24,527 voxels, sous le pas et demi de `369`,
27,031 voxels : la règle du saut double de `369` ne voit pas un saut de deux tours).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P177` (ISSUE #19). L'accord de trois chaînes est un juge sans tracé, et sur PHerc0358 rien ne
dit s'il est juste. PHercParis4 a des tours publiés : on y rejoue la règle de `374` telle qu'elle est, et on regarde si les surfaces qu'elle
valide sont sur le tour que leur compte annonce.

## Ce qui est fait

- **Les chaînes** : pour chaque côté de graine de PHercParis4 que `331` suit, la chaîne d'une maille de `365` depuis la nappe de la graine,
  la même depuis la graine compagne de `368` (15 mailles du centre de la nappe) et depuis la graine tierce de `373`, chaque nappe regrandie
  par la nappe qui croît de `322`. La suivie doit redonner la justesse que `365` publie saut par saut, sur les seize côtés.
- **Les comptes corrigés** : chaque saut comparé à la surface d'où il part comme `369`, au latéral de `345` et à trois pas au plus ; nul au
  plus à un quart de pas, double au-delà d'un pas et demi, au pas de PHercParis4 (18,02 voxels) ; comptés 0, 2 et 1 sinon.
- **Les paires** : deux surfaces de deux chaînes d'un côté sont **sur la même feuille** si au moins 50 points de la première ont la seconde
  en face, au latéral de `345` et à un pas et demi au plus, et si la médiane de leurs écarts absolus est d'au plus un quart de pas, comme `367`.
- **La validation** : celle de `374`, sans changement. Une autre chaîne confirme une surface si l'une des siennes est sur la même feuille au
  même compte ; elle la contredit si l'une est sur la même feuille à un autre compte, ou au même compte sur une autre feuille. Validée :
  confirmée par les deux autres, contredite par aucune.
- **La vérité** : chaque nappe et chaque surface lues contre les tours publiés `5753_0` à `5753_-7` comme `329`. La référence d'une chaîne est
  la première de sa nappe et de ses surfaces qui retrouve un seul tour. Une surface après sa référence est **lue** si elle retrouve un seul
  tour, et **sur le bon tour** si ce tour s'écarte de celui de la référence d'autant de tours, dans le sens du côté, que son compte corrigé
  s'écarte du compte de la référence.
- **La règle** : si au moins 90 % des surfaces validées lues sont sur le bon tour, et plus souvent que les surfaces contredites lues,
  **oui, l'accord de trois chaînes choisit le bon tour** ; si moins de 75 %, **non** ; sinon, **en partie**. Indécidable sous 10 surfaces
  validées lues, ou si la suivie ne redonne pas `365`.

## Les issues

L'issue de la tranche : **a des n surfaces validées lues sont sur le bon tour, contre a' des n' surfaces contredites lues**, puis ce que dit
la règle.

## Rapporté à côté, qui ne décide rien

Les mêmes parts pour les surfaces confirmées une fois et sans témoin ; et le même jugement si l'on compte chaque saut pour un tour, sans la
correction de `369`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la règle sur PHerc0358, dont les feuilles sont plus inégalement espacées ; ni ce qu'elle
vaudrait avec une règle des sauts doubles juste.

Usage :
    uv run python src/nappe/une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.py --verifier
    uv run python src/nappe/une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.py \\
        --json docs/mesures/une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import regrandir_dune_seule_maille_evite_il_le_decalage as m365  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_365_A_PUBLIE = LES_MESURES / "regrandir_dune_seule_maille_evite_il_le_decalage.json"
SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LES_CHAINES = m374.LES_CHAINES
LES_COUPLES = ((SUIVIE, COMPAGNE), (SUIVIE, TIERCE), (COMPAGNE, TIERCE))
LE_PAS = m321.LE_PAS_L2
LE_QUART = LE_PAS / 4.0
LE_DOUBLE = 1.5 * LE_PAS
LE_LATERAL = m345.LE_LATERAL_L2
LA_PORTEE_DES_PAIRES = 1.5 * LE_PAS
LA_PORTEE_DES_SAUTS = 3.0 * LE_PAS
LE_MINIMUM_EN_FACE = m368.LE_MINIMUM_EN_FACE
LA_PART = 0.9
LA_PART_BASSE = 0.75
LE_MINIMUM = 10
LES_POIDS = {"nul": 0, "simple": 1, "double": 2}
_LES_TROIS: list[dict] = []


def lecart(surface, depart, lateral: float = LE_LATERAL, portee: float = LA_PORTEE_DES_SAUTS) -> dict:
    """L'écart d'un saut comme `369` le mesure, au latéral de `345` et à trois pas de PHercParis4."""
    return m369.lecart_du_saut(surface, depart, lateral=lateral, portee=portee)


def le_genre(c: dict) -> str:
    """Le genre d'un saut au pas de PHercParis4 : nul au plus à un quart de pas, double au-delà d'un pas et demi ; simple s'il n'est pas lu."""
    if c["en_face"] < LE_MINIMUM_EN_FACE or c["lecart_median"] is None:
        return "simple"
    return "nul" if c["lecart_median"] <= LE_QUART else "double" if c["lecart_median"] > LE_DOUBLE else "simple"


def les_comptes(nappe, surfaces: list, mesurer_=lecart, corriger: bool = True) -> list[int]:
    """Le compte corrigé de chaque surface d'une chaîne, ou son rang si `corriger` est faux."""
    out, compte, avant = [], 0, nappe
    for s in surfaces:
        compte += LES_POIDS[le_genre(mesurer_(s, avant))] if corriger else 1
        out.append(compte)
        avant = s
    return out


def la_comparaison(a, b, lateral: float = LE_LATERAL, portee: float = LA_PORTEE_DES_PAIRES) -> dict:
    """Les points de `a` qui ont `b` en face, et la médiane de leurs écarts absolus, comme `367`."""
    import numpy as np

    if a is None or b is None or not len(a[0]) or not len(b[0]):
        return {"en_face": 0, "lecart_median": None}
    e = m321.les_ecarts(a[0], a[1], b[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= portee)
    return {"en_face": int(vus.sum()), "lecart_median": round(float(np.median(np.abs(e[vus]))), 3) if vus.any() else None}


def les_paires(a: list, b: list, comparer=la_comparaison) -> list[dict]:
    """Les paires de surfaces de deux chaînes qui ont au moins 50 points en face, et si elles sont sur la même feuille au quart de pas."""
    out = []
    for h, x in enumerate(a, 1):
        for k, y in enumerate(b, 1):
            c = comparer(x, y)
            if c["en_face"] < LE_MINIMUM_EN_FACE:
                continue
            out.append({"le_saut_suivi": h, "le_saut_compagnon": k, **c, "meme_feuille": bool(c["lecart_median"] <= LE_QUART)})
    return out


def la_reference(retrouves: list[list[int]]) -> int | None:
    """L'indice de la première lecture, la nappe en tête, qui retrouve un seul tour publié."""
    return next((k for k, r in enumerate(retrouves) if len(r) == 1), None)


def la_verite(retrouves: list[list[int]], comptes: list[int], sens: int) -> list[dict]:
    """Pour chaque surface, la nappe en tête des lectures et `comptes` celui des surfaces : lue ou non, et sur le bon tour."""
    k0 = la_reference(retrouves)
    tous = [0] + list(comptes)
    out = []
    for h in range(1, len(retrouves)):
        r = retrouves[h]
        lue = k0 is not None and h > k0 and len(r) == 1
        bon = bool(lue and r[0] - retrouves[k0][0] == sens * (tous[h] - tous[k0]))
        out.append({"le_saut": h, "lue": bool(lue), "sur_le_bon_tour": bon if lue else None, "le_tour": r[0] if len(r) == 1 else None})
    return out


def le_cote(paires: dict, comptes: dict, verites: dict) -> list[dict]:
    """Chaque surface des trois chaînes d'un côté : son statut par `374` et sa vérité."""
    liens = m374.les_liens(paires)
    out = []
    for x in LES_CHAINES:
        for h in range(1, len(comptes[x]) + 1):
            s = m374.le_statut(x, h, liens, comptes)
            out.append({**s, **{k: v for k, v in verites[x][h - 1].items() if k != "le_saut"}})
    return out


def le_bilan(surfaces: list[dict]) -> dict:
    out = {}
    for st in (m374.VALIDEE, m374.CONTREDITE, m374.EN_PARTIE, m374.SEULE):
        lues = [s for s in surfaces if s["le_statut"] == st and s["lue"]]
        out[st] = {"les_surfaces": sum(s["le_statut"] == st for s in surfaces), "lues": len(lues),
                   "sur_le_bon_tour": sum(s["sur_le_bon_tour"] for s in lues)}
    return out


def le_verdict(d: dict) -> dict:
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : la suivie ne redonne pas la justesse que 365 publie"}
    b = d["le_bilan"]
    v, c = b[m374.VALIDEE], b[m374.CONTREDITE]
    if v["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {v['lues']} surfaces validées lues, moins de {LE_MINIMUM}"}
    tete = (f"{v['sur_le_bon_tour']} des {v['lues']} surfaces validées lues sont sur le bon tour, contre {c['sur_le_bon_tour']} des "
            f"{c['lues']} surfaces contredites lues")
    pv = v["sur_le_bon_tour"] / v["lues"]
    pc = c["sur_le_bon_tour"] / c["lues"] if c["lues"] else 0.0
    suite = ("oui, l'accord de trois chaînes choisit le bon tour" if pv >= LA_PART and pv > pc else "non" if pv < LA_PART_BASSE
             else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def le_chaineur(enchainer=None, croitre=None):
    """Le chaîneur à passer à `331` sur PHercParis4 : la chaîne d'une maille de `365` depuis la nappe, la graine compagne et la graine
    tierce, chaque nappe regrandie par `322` ; les nappes et les surfaces des trois sont gardées, dans l'ordre des côtés."""
    enchainer = enchainer or m365.la_chaine_dune_maille

    def chainer(nappe, relancer, sauter, lire_valeurs):
        grandir = croitre or (lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lire_valeurs))
        suivie = enchainer(nappe, relancer, sauter, lire_valeurs)
        g = m368.la_graine_compagne(nappe)
        nc = None if g is None else grandir(g[0], g[1])
        compagne = [] if nc is None else enchainer(nc, relancer, sauter, lire_valeurs)
        t = m373.la_graine_tierce(nappe)
        nt = None if t is None else grandir(t[0][0], t[0][1])
        tierce = [] if nt is None else enchainer(nt, relancer, sauter, lire_valeurs)
        relances = lambda ch: [k.get("la_relance") for k in ch]  # noqa: E731
        _LES_TROIS.append({"ou": None if t is None else t[1],
                           "les_nappes": {SUIVIE: nappe, COMPAGNE: nc, TIERCE: nt},
                           "les_relances": {SUIVIE: relances(suivie), COMPAGNE: relances(compagne), TIERCE: relances(tierce)}})
        return suivie
    return chainer


def les_points_lus(surface: dict | None):
    """Les points posés d'une nappe ou d'une surface, au niveau 0, comme `331` les lit contre les tours publiés."""
    import numpy as np

    if surface is None or not surface["valide"].any():
        return np.zeros((0, 3))
    return surface["la_nappe"][surface["valide"]] * m321.LE_FACTEUR


def les_retrouves(surface, tours: dict) -> list[int]:
    if surface is None or not surface["valide"].any():
        return []
    return m340.les_retrouves({t: x["la_lecture"] for t, x in m329.les_lectures(les_points_lus(surface), tours).items()})


def mesurer() -> dict:
    t0 = time.monotonic()
    _LES_TROIS.clear()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=le_chaineur())
    p365 = {(c["le_rang"], c["le_cote"]): [s["la_justesse"] for s in c["les_sauts"]] for c in json.loads(CE_QUE_365_A_PUBLIE.read_text())["les_cotes"]}
    publiees = json.loads((LES_MESURES / m340.LES_CHAINES["sans relance"]).read_text())
    nappes = {g["le_rang"]: {t: x["la_lecture"] for t, x in g["la_nappe"].items()} for g in publiees["les_graines"]}
    cotes_d331 = [(g["le_rang"], cote, c) for g in d331["les_graines"]["PHercParis4"] for cote, c in g["les_cotes"].items()]
    redonne = len(cotes_d331) == len(_LES_TROIS) == len(p365)
    lectures_egales, cotes, toutes = True, [], []
    for (rang, cote, c), trois in zip(cotes_d331, _LES_TROIS):
        sens = m344.LE_SENS[cote]
        lect = m340.les_surfaces("mixte", d331, nappes, rang, cote)
        justesse = [m344.la_justesse(lect[h - 1], lect[h], sens) for h in range(1, len(lect))]
        redonne &= justesse == p365.get((rang, cote))
        surf = {x: [m367.les_points(r) for r in trois["les_relances"][x]] for x in LES_CHAINES}
        nap = {x: m367.les_points(trois["les_nappes"][x]) for x in LES_CHAINES}
        retrouves = {x: [les_retrouves(trois["les_nappes"][x], tours)] + [les_retrouves(r, tours) for r in trois["les_relances"][x]]
                     for x in LES_CHAINES}
        lectures_egales &= retrouves[SUIVIE][1:] == [m340.les_retrouves(s) for s in lect[1:]]
        corriges = {x: les_comptes(nap[x], surf[x]) for x in LES_CHAINES}
        bruts = {x: les_comptes(nap[x], surf[x], corriger=False) for x in LES_CHAINES}
        paires = {f"{a}|{b}": les_paires(surf[a], surf[b]) for a, b in LES_COUPLES}
        surfaces = le_cote(paires, corriges, {x: la_verite(retrouves[x], corriges[x], sens) for x in LES_CHAINES})
        surfaces_brutes = le_cote(paires, bruts, {x: la_verite(retrouves[x], bruts[x], sens) for x in LES_CHAINES})
        toutes.append((surfaces, surfaces_brutes))
        cotes.append({"le_rang": rang, "le_cote": cote, "ou": trois["ou"], "la_justesse_de_la_suivie": justesse,
                      "les_retrouves": retrouves, "les_comptes": corriges, "les_comptes_bruts": bruts,
                      "les_paires": {k: [{q: p[q] for q in ("le_saut_suivi", "le_saut_compagnon", "en_face", "lecart_median", "meme_feuille")}
                                         for p in v] for k, v in paires.items()},
                      "les_surfaces": surfaces})
        print(json.dumps({"le_rang": rang, "le_cote": cote, "redonne": bool(redonne), "lectures_egales": bool(lectures_egales),
                          "validees": [(s["la_chaine"], s["le_saut"], s["sur_le_bon_tour"]) for s in surfaces
                                       if s["le_statut"] == m374.VALIDEE]}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas": round(LE_PAS, 3), "le_quart": round(LE_QUART, 3), "le_double": round(LE_DOUBLE, 3),
                            "le_lateral": LE_LATERAL, "la_portee_des_paires": round(LA_PORTEE_DES_PAIRES, 3),
                            "la_portee_des_sauts": round(LA_PORTEE_DES_SAUTS, 3), "le_minimum_en_face": LE_MINIMUM_EN_FACE,
                            "la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
         "les_pannes": d331["les_pannes"], "la_lecture_de_m7": d331["la_lecture_de_m7"], "redonne": bool(redonne),
         "les_lectures_redonnent_331": bool(lectures_egales), "les_cotes": cotes}
    d["le_bilan"] = le_bilan([s for a, _ in toutes for s in a])
    d["le_bilan_sans_correction"] = le_bilan([s for _, b in toutes for s in b])
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    import numpy as np

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

    c_ = lambda e, n=100: {"en_face": n, "lecart_median": e}  # noqa: E731
    v("★★★★ le genre au pas de PHercParis4 : nul au quart, double au-delà du pas et demi, simple si non lu",
      [le_genre(c_(x)) for x in (m321.LE_PAS_L2 / 4.0, 4.51, 27.03, 27.04)] == ["nul", "simple", "simple", "double"]
      and le_genre(c_(1.0, 49)) == "simple" and le_genre(c_(None)) == "simple")
    v("★★★★ les comptes corrigés : 1, 0, 2, 1, chaque saut mesuré depuis la surface précédente ; sans correction, le rang",
      lambda: les_comptes(0.0, [15.0, 17.0, 47.0, 63.0], mesurer_=lambda s, d: c_(abs(s - d))) == [1, 1, 3, 4]
      and les_comptes("n", list("abcd"), mesurer_=lambda s, d: c_(2.0), corriger=False) == [1, 2, 3, 4])
    g = np.stack(np.meshgrid(np.arange(0.0, 400.0, 40.0), np.arange(0.0, 400.0, 40.0)), -1).reshape(-1, 2)
    plan = lambda z: (np.c_[g, np.full(len(g), z)], np.tile([0.0, 0.0, 1.0], (len(g), 1)))  # noqa: E731
    v("★★★★ la comparaison : à un pas et demi au plus, au latéral donné",
      lambda: la_comparaison(plan(0.0), plan(4.0), lateral=0.5) == {"en_face": 100, "lecart_median": 4.0}
      and la_comparaison(plan(0.0), plan(28.0), lateral=0.5)["en_face"] == 0)
    ps = les_paires(["a", "b"], ["x", "y"], comparer=lambda p, q: {("a", "x"): c_(4.505), ("a", "y"): c_(4.6), ("b", "x"): c_(1.0, 49),
                                                                   ("b", "y"): c_(20.0)}[(p, q)])
    v("★★★★ les paires : 50 points en face au moins, même feuille au quart de pas de PHercParis4",
      [(p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]) for p in ps] == [(1, 1, True), (1, 2, False), (2, 2, False)], str(ps))
    v("★★★ la référence : la première lecture qui retrouve un seul tour, la nappe comprise",
      la_reference([[0, -1], [], [-2], [-3]]) == 2 and la_reference([[1], [0]]) == 0 and la_reference([[], [0, -1]]) is None)
    vr = la_verite([[], [-1], [-2], [-2, -3], [-4], [-3]], [1, 2, 3, 5, 3], -1)
    v("★★★★ la vérité : lue après la référence, un seul tour ; bonne si l'écart de tours suit celui des comptes dans le sens du côté",
      [(x["lue"], x["sur_le_bon_tour"]) for x in vr] == [(False, None), (True, True), (False, None), (True, False), (True, True)], str(vr))
    vs = la_verite([[], [-1], [0]], [1, 2], -1)
    v("★★★ la vérité dans le sens du côté : un tour remonté n'est pas le bon", vs[1]["sur_le_bon_tour"] is False, str(vs))
    vp = la_verite([[0], [1]], [1], 1)
    v("★★★ la vérité depuis la nappe, du côté plus", [(x["lue"], x["sur_le_bon_tour"]) for x in vp] == [(True, True)], str(vp))
    pa = {"suivie|compagne": [{"le_saut_suivi": 1, "le_saut_compagnon": 1, "meme_feuille": True}],
          "suivie|tierce": [{"le_saut_suivi": 1, "le_saut_compagnon": 1, "meme_feuille": True}],
          "compagne|tierce": [{"le_saut_suivi": 1, "le_saut_compagnon": 1, "meme_feuille": True}]}
    ve = {x: [{"le_saut": 1, "lue": True, "sur_le_bon_tour": True, "le_tour": -1}] for x in LES_CHAINES}
    sc = le_cote(pa, {x: [1] for x in LES_CHAINES}, ve)
    v("★★★★ le côté : le statut de 374 et la vérité de chaque surface",
      [(s["la_chaine"], s["le_statut"], s["sur_le_bon_tour"]) for s in sc] == [(x, m374.VALIDEE, True) for x in LES_CHAINES]
      and le_cote(pa, {SUIVIE: [1], COMPAGNE: [2], TIERCE: [1]}, ve)[0]["le_statut"] == m374.CONTREDITE)
    s_ = lambda st, lue, bon: {"le_statut": st, "lue": lue, "sur_le_bon_tour": bon}  # noqa: E731
    bl = lambda: le_bilan([s_(m374.VALIDEE, True, True), s_(m374.VALIDEE, True, False), s_(m374.VALIDEE, False, None),  # noqa: E731
                           s_(m374.CONTREDITE, True, False)])
    v("★★★★ le bilan : surfaces, lues et sur le bon tour par statut",
      lambda: bl()[m374.VALIDEE] == {"les_surfaces": 3, "lues": 2, "sur_le_bon_tour": 1}
      and bl()[m374.CONTREDITE] == {"les_surfaces": 1, "lues": 1, "sur_le_bon_tour": 0} and bl()[m374.SEULE]["les_surfaces"] == 0)

    def d_(bv, lv_, bc, lc, ok=True):
        return {"redonne": ok, "le_bilan": {m374.VALIDEE: {"lues": lv_, "sur_le_bon_tour": bv}, m374.CONTREDITE: {"lues": lc, "sur_le_bon_tour": bc}}}
    v("★★★★ la règle : 90 % et mieux que les contredites oui ; sous 75 % non ; sinon en partie",
      le_verdict(d_(9, 10, 1, 10))["lissue"].endswith("choisit le bon tour") and le_verdict(d_(9, 10, 10, 10))["lissue"].endswith("en partie")
      and le_verdict(d_(8, 10, 1, 10))["lissue"].endswith("; en partie") and le_verdict(d_(7, 10, 1, 10))["lissue"].endswith("; non")
      and le_verdict(d_(15, 20, 1, 10))["lissue"].endswith("; en partie") and le_verdict(d_(9, 10, 0, 0))["lissue"].endswith("bon tour"))
    v("★★★ indécidable sous 10 validées lues, ou sans redonne",
      not le_verdict(d_(9, 9, 1, 10))["decidable"] and not le_verdict(d_(10, 10, 1, 10, ok=False))["decidable"]
      and le_verdict(d_(10, 10, 1, 10))["decidable"])

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
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
