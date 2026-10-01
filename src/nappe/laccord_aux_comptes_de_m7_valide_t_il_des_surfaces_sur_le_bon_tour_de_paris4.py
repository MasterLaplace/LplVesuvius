"""Sur PHercParis4, l'accord de trois chaînes aux comptes de m7 valide-t-il des surfaces sur le bon tour publié, et autant qu'aux comptes de 369 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES FEUILLES DE `m7` NE SOIENT COMPTÉES SUR LES SAUTS DES TROIS CHAÎNES DE PHERCPARIS4. Ce qui était
vu avant d'écrire : tout ce que `296` à `384` publient, dont `R4-F565` (aux comptes de `369`, l'accord valide 109 surfaces de PHercParis4,
dont 46 lues, toutes sur le bon tour publié ; 3 des 14 contredites lues ne le sont pas, nées d'un saut compté double), `R4-F570` (sur
PHerc0358, 8 des 12 sauts que `369` compte doubles ne franchissent qu'une feuille de `m7`, et l'accord aux comptes de `m7` y valide 78
surfaces contre 50) et `R4-F531` (sur PHercParis4, le compte des feuilles de `345` tient 95 des 104 sauts justes et 3 des 6 faux).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P182`. Sur PHerc0358, les comptes de `m7` changent ce que l'accord valide et à quel compte,
mais rien n'y dit lesquels sont justes. PHercParis4 a des tours publiés : on y rejoue l'accord de `379` aux comptes de `m7`.

## Ce qui est fait

- **Les chaînes, les paires et la vérité** : celles de `379`, rejouées ; aux comptes de `369`, les statuts et la vérité de chaque surface
  doivent redonner ce que `379` publie, sans quoi la tranche est indécidable.
- **Les comptes de `m7`** : chaque saut ajoute le nombre de feuilles de `m7` qu'il franchit, comme `384` le compte, au pas de PHercParis4
  (18,02 voxels) et à la portée latérale de `345` ; là où ce nombre n'est pas dit, ce que `369` lui donne. La vérité de `379` est
  recalculée avec ces comptes.
- **Le contrôle** : là où `369` compte un saut simple, `m7` dit une feuille sous au moins 75 % des sauts dits.
- **La règle** : aux comptes de `m7`, si au moins 90 % des surfaces validées lues sont sur le bon tour et qu'il y a au moins autant de
  surfaces validées lues sur le bon tour qu'aux comptes de `369`, **oui** ; au moins 90 % mais moins de surfaces, **en partie** ; moins de
  75 %, **non** ; sinon, **en partie**. Indécidable sous 10 surfaces validées lues, ou si le contrôle ou la redite échoue.

## Les issues

L'issue de la tranche : **aux comptes de `m7`, a des n surfaces validées lues sont sur le bon tour, contre a' des n' aux comptes de
`369`**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts par genre de `369` et par nombre de feuilles de `m7` ; les surfaces contredites lues et leur vérité aux deux comptes.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut l'accord aux comptes de `m7` sur PHerc0358, dont les feuilles s'écartent autrement ;
seulement si `m7` compte juste là où une vérité existe.

Usage :
    uv run python src/nappe/laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.py --verifier
    uv run python src/nappe/laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.py \\
        --json docs/mesures/laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json
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
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
SUIVIE, COMPAGNE, TIERCE = m379.SUIVIE, m379.COMPAGNE, m379.TIERCE
LES_CHAINES = m379.LES_CHAINES
LE_PAS = m321.LE_PAS_L2
LA_PART, LA_PART_BASSE, LE_MINIMUM = m379.LA_PART, m379.LA_PART_BASSE, m379.LE_MINIMUM
LA_PART_DU_CONTROLE = 0.75
LES_GENRES = {0: "nul", 1: "simple", 2: "double"}


def les_increments(comptes: list[int]) -> list[int]:
    return [b - a for a, b in zip([0] + list(comptes[:-1]), comptes)]


def les_comptes_de_m7(comptes_369: list[int], nombres: list[int | None]) -> list[int]:
    """Les comptes d'une chaîne où chaque saut ajoute le nombre de feuilles de `m7` qu'il franchit, là où il est dit, sinon ce que `369`
    lui donne."""
    out, w = [], 0
    for d, n in zip(les_increments(comptes_369), nombres):
        w += d if n is None else n
        out.append(w)
    return out


def les_nombres(nappe: dict | None, relances: list, lire_valeurs) -> list[dict]:
    """Pour chaque saut d'une chaîne, depuis la nappe pour le premier et la surface précédente ensuite, le compte de `345` au pas de
    PHercParis4 et le nombre de feuilles qu'il dit."""
    out, avant = [], nappe
    for rl in relances:
        r = None if avant is None else m345.les_comptes_point_par_point(avant, rl, lire_valeurs, LE_PAS)
        f = m345.le_resume(r)
        out.append({"les_mesures": f["les_mesures"], "les_comptes": f["les_comptes"],
                    "le_nombre_de_feuilles": m383.le_nombre_de_feuilles(f["les_comptes"])})
        avant = rl
    return out


def les_statuts(surfaces: list[dict]) -> list[tuple]:
    return [(s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"], s["lue"], s["sur_le_bon_tour"]) for s in surfaces]


def le_bilan_des_genres(cotes: list[dict]) -> dict:
    out = {}
    for g in ("nul", "simple", "double"):
        ns = [s["le_nombre_de_feuilles"] for c in cotes for x in LES_CHAINES for s in c["les_sauts"][x] if s["le_genre"] == g]
        dits = [n for n in ns if n is not None]
        out[g] = {"les_sauts": len(ns), "dits": len(dits), "zero": dits.count(0), "une": dits.count(1), "deux": dits.count(2),
                  "plus": sum(n > 2 for n in dits)}
    return out


def le_controle(genres: dict) -> bool:
    s = genres["simple"]
    return bool(s["dits"] and s["une"] >= LA_PART_DU_CONTROLE * s["dits"])


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_379"):
        return {"decidable": False, "lissue": "indécidable : aux comptes de 369, les chaînes rejouées ne redonnent pas 379"}
    if not le_controle(d["les_genres"]):
        return {"decidable": False, "lissue": "indécidable : m7 ne dit pas une feuille sous les trois quarts des sauts simples de 369"}
    a, b = d["avec_m7"][m374.VALIDEE], d["avec_369"][m374.VALIDEE]
    if a["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {a['lues']} surfaces validées lues aux comptes de m7, moins de {LE_MINIMUM}"}
    tete = (f"aux comptes de m7, {a['sur_le_bon_tour']} des {a['lues']} surfaces validées lues sont sur le bon tour, contre "
            f"{b['sur_le_bon_tour']} des {b['lues']} aux comptes de 369")
    p = a["sur_le_bon_tour"] / a["lues"]
    if p >= LA_PART:
        suite = ("oui, l'accord aux comptes de m7 choisit le bon tour, et autant" if a["sur_le_bon_tour"] >= b["sur_le_bon_tour"]
                 else "en partie : le bon tour, mais moins de surfaces")
    else:
        suite = "non" if p < LA_PART_BASSE else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m379._LES_TROIS.clear()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=m379.le_chaineur())
    d379 = json.loads(CE_QUE_379_A_PUBLIE.read_text())
    cotes_d331 = [(g["le_rang"], cote) for g in d331["les_graines"]["PHercParis4"] for cote in g["les_cotes"]]
    redonne = len(cotes_d331) == len(m379._LES_TROIS) == len(d379["les_cotes"])
    cotes, avec369, avecm7 = [], [], []
    for (rang, cote), trois, c379 in zip(cotes_d331, m379._LES_TROIS, d379["les_cotes"]):
        sens = m344.LE_SENS[cote]
        surf = {x: [m367.les_points(r) for r in trois["les_relances"][x]] for x in LES_CHAINES}
        nap = {x: m367.les_points(trois["les_nappes"][x]) for x in LES_CHAINES}
        retrouves = {x: [m379.les_retrouves(trois["les_nappes"][x], tours)] + [m379.les_retrouves(r, tours) for r in trois["les_relances"][x]]
                     for x in LES_CHAINES}
        corriges = {x: m379.les_comptes(nap[x], surf[x]) for x in LES_CHAINES}
        paires = {f"{a}|{b}": m379.les_paires(surf[a], surf[b]) for a, b in m379.LES_COUPLES}
        s369 = m379.le_cote(paires, corriges, {x: m379.la_verite(retrouves[x], corriges[x], sens) for x in LES_CHAINES})
        redonne &= ((rang, cote) == (c379["le_rang"], c379["le_cote"]) and les_statuts(s369) == les_statuts(c379["les_surfaces"]))
        nombres = {x: les_nombres(trois["les_nappes"][x], trois["les_relances"][x], lv["m7"]) for x in LES_CHAINES}
        m7 = {x: les_comptes_de_m7(corriges[x], [n["le_nombre_de_feuilles"] for n in nombres[x]]) for x in LES_CHAINES}
        sm7 = m379.le_cote(paires, m7, {x: m379.la_verite(retrouves[x], m7[x], sens) for x in LES_CHAINES})
        avec369 += s369
        avecm7 += sm7
        sauts = {x: [{"le_saut": h, "le_genre": LES_GENRES.get(dlt, str(dlt)), **n}
                     for h, (dlt, n) in enumerate(zip(les_increments(corriges[x]), nombres[x]), 1)] for x in LES_CHAINES}
        cotes.append({"le_rang": rang, "le_cote": cote, "les_comptes_de_369": corriges, "les_comptes_de_m7": m7, "les_sauts": sauts,
                      "les_surfaces_avec_m7": sm7})
        print(json.dumps({"le_rang": rang, "le_cote": cote, "redonne": bool(redonne),
                          "nombres": {x: [n["le_nombre_de_feuilles"] for n in nombres[x]] for x in LES_CHAINES},
                          "validees": (sum(s["le_statut"] == m374.VALIDEE for s in s369), sum(s["le_statut"] == m374.VALIDEE for s in sm7))},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas": round(LE_PAS, 3), "la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM,
                            "la_part_du_controle": LA_PART_DU_CONTROLE},
         "les_pannes": d331["les_pannes"], "la_lecture_de_m7": d331["la_lecture_de_m7"], "redonne_379": bool(redonne), "les_cotes": cotes}
    d["les_genres"] = le_bilan_des_genres(cotes)
    d["avec_369"] = m379.le_bilan(avec369)
    d["avec_m7"] = m379.le_bilan(avecm7)
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

    v("★★★★ les comptes de m7 : le nombre dit, sinon l'incrément de 369",
      les_comptes_de_m7([2, 3, 3, 4], [1, None, 0, 2]) == [1, 2, 2, 4] and les_comptes_de_m7([1, 2], [0, None]) == [0, 1])
    v("★★★★ le pas de PHercParis4", abs(LE_PAS - 18.02) < 0.01)
    c = [{"les_sauts": {SUIVIE: [{"le_genre": "simple", "le_nombre_de_feuilles": 1}, {"le_genre": "double", "le_nombre_de_feuilles": 1},
                                 {"le_genre": "simple", "le_nombre_de_feuilles": None}],
                        COMPAGNE: [{"le_genre": "nul", "le_nombre_de_feuilles": 0}, {"le_genre": "double", "le_nombre_de_feuilles": 3}],
                        TIERCE: []}}]
    g = le_bilan_des_genres(c)
    v("★★★★ le bilan des genres", g["simple"] == {"les_sauts": 2, "dits": 1, "zero": 0, "une": 1, "deux": 0, "plus": 0}
      and g["double"] == {"les_sauts": 2, "dits": 2, "zero": 0, "une": 1, "deux": 0, "plus": 1} and g["nul"]["zero"] == 1, str(g))
    v("★★★★ le contrôle : une feuille sous au moins 75 % des simples dits",
      le_controle({"simple": {"une": 3, "dits": 4}}) and not le_controle({"simple": {"une": 2, "dits": 4}})
      and not le_controle({"simple": {"une": 0, "dits": 0}}))

    def d_(a, n, b, nb, ok=True, une=9, pannes=()):
        return {"redonne_379": ok, "les_pannes": list(pannes), "les_genres": {"simple": {"une": une, "dits": 10}},
                "avec_m7": {m374.VALIDEE: {"sur_le_bon_tour": a, "lues": n}}, "avec_369": {m374.VALIDEE: {"sur_le_bon_tour": b, "lues": nb}}}
    v("★★★★ la règle : 90 % et autant, oui ; 90 % et moins, en partie ; sous 75 %, non",
      le_verdict(d_(50, 50, 46, 46))["lissue"].endswith("et autant") and le_verdict(d_(46, 50, 46, 46))["lissue"].endswith("et autant")
      and le_verdict(d_(40, 40, 46, 46))["lissue"].endswith("moins de surfaces") and le_verdict(d_(7, 10, 46, 46))["lissue"].endswith("; non")
      and le_verdict(d_(8, 10, 46, 46))["lissue"].endswith("; en partie")
      and "50 des 50 surfaces validées lues sont sur le bon tour, contre 46 des 46" in le_verdict(d_(50, 50, 46, 46))["lissue"])
    v("★★★ indécidable sous 10 lues, sans redite, sans contrôle ou sur une panne",
      not le_verdict(d_(9, 9, 46, 46))["decidable"] and not le_verdict(d_(50, 50, 46, 46, ok=False))["decidable"]
      and not le_verdict(d_(50, 50, 46, 46, une=7))["decidable"] and not le_verdict(d_(50, 50, 46, 46, pannes=("x",)))["decidable"]
      and le_verdict(d_(10, 10, 46, 46))["decidable"])
    s_ = {"la_chaine": SUIVIE, "le_saut": 1, "le_compte": 2, "le_statut": m374.VALIDEE, "lue": True, "sur_le_bon_tour": True, "x": 0}
    v("★★★ la redite compare le compte, le statut et la vérité de chaque surface",
      les_statuts([s_]) == [(SUIVIE, 1, 2, m374.VALIDEE, True, True)])

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
