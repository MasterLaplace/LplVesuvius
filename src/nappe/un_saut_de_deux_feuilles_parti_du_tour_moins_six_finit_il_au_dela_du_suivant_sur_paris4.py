"""Sur PHercParis4, les sauts de deux feuilles de m7 qui partent du tour −6 finissent-ils un tour au-delà du tour −7, ou sur lui ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE DISTANCE AUX TOURS −6 ET −7 NE SOIT MESURÉE. Ce qui était vu avant d'écrire : tout ce que
`296` à `403` publient, dont **`R4-F589`** (`403` : des sauts de plusieurs feuilles partent du tour −6 sur les graines 5 et 6, côté
moins, et leur surface d'arrivée ne retrouve aucun tour ; une seule surface de chaque famille retrouve le tour −7), **`R4-F522`** (le tour
−7 est à 3-6 voxels du niveau 2 des plages de `m7`, contre 0,5-2 pour le tour −6) et **`R4-F523`** (deux tours publiés consécutifs sont
à 0,53-0,93 pas nominal l'un de l'autre autour des graines). La mesure de `403` donne déjà les sauts et leurs comptes ; aucune distance n'y
est publiée.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P201`. Aucun tour −8 n'est publié, donc un saut qui franchit deux tours depuis le tour −6 ne
peut retrouver aucun tour. Mais sa distance au tour −6 se mesure, et l'écart entre les tours −6 et −7 au même endroit donne l'unité :
leur rapport compte les tours franchis sans qu'un tour soit retrouvé.

## Ce qui est fait

- **Les chaînes** : les deux familles de `403`, celles de `385` (chaîne d'une maille de `379`) et les chaînes rognées de `400`, relancées
  sur les seize côtés de PHercParis4. Le contrôle : leurs tours retrouvés redonnent, surface par surface, ceux que `403` publie, et le
  compte de `m7` de chaque saut lu redonne celui de `403`.
- **Les sauts lus** : ceux dont la surface de départ retrouve le seul tour −6, et que `m7` compte d'une feuille (**le témoin**) ou de deux.
  Un saut rogné que rien ne distingue d'un saut de `385` (même côté, même chaîne, même rang, mêmes comptes) n'est lu qu'une fois.
- **La lecture d'un saut** : les sommets du tour −6 en face de la surface d'arrivée, à 40 voxels de côté au plus ; l'écart médian de la
  surface le long de leurs normales, et celui du tour −7 au même endroit. Leur rapport est **le nombre de tours franchis**. Une lecture
  exige 50 sommets en face pour chacun des deux écarts.
- **La règle** : le témoin vaut si au moins 5 de ses sauts sont lus et qu'au moins 80 % d'entre eux franchissent entre 0,5 et 1,5 tour.
  S'il vaut : tous les sauts de deux feuilles lus à au moins 1,5 tour, **oui** ; tous en dessous, **non** ; sinon, **en partie**.
  Indécidable si le témoin ne vaut pas, si moins de 2 sauts de deux feuilles sont lus, si une lecture de `m7` échoue ou si le contrôle
  échoue.

## Les issues

L'issue de la tranche : **sauts de deux feuilles partis du tour −6 : k sur n à au moins 1,5 tour ; témoin : w sur t entre 0,5 et 1,5**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Pour chaque saut lu, l'écart de sa surface au tour −6 et celui du tour −7, en pas nominaux, et les tours franchis ; les sauts qui partent du
tour −6 sans être lus, et pourquoi.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut un saut de deux feuilles ailleurs qu'au tour −6, ni sur PHerc0358.

Usage :
    uv run python src/nappe/un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.py --verifier
    uv run python src/nappe/un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.py \\
        --json docs/mesures/un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4 as m385  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402
import des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4 as m400  # noqa: E402
import un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4 as m403  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_403_A_PUBLIE = LES_MESURES / "un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LES_FAMILLES = {"385": None, "rognees": m400.enchainer4}
LE_DEPART, LE_SUIVANT = -6, -7
LES_FEUILLES = (1, 2)
LE_MINIMUM_EN_FACE = m321.LE_MINIMUM
LE_TEMOIN_MINIMUM, LA_PART_DU_TEMOIN = 5, 0.8
LE_BAS, LE_HAUT = 0.5, 1.5
LE_MINIMUM_DE_DEUX = 2


def la_lecture(arrivee_pts: np.ndarray, tours: dict) -> dict:
    """Les tours que franchit une surface d'arrivée depuis le tour −6 : son écart médian au tour −6 le long des normales de ses sommets
    en face, rapporté à celui du tour −7 au même endroit."""
    ref, ref_n = m329.les_sommets_proches(tours[LE_DEPART], arrivee_pts)
    t = m321.les_ecarts(ref, ref_n, arrivee_pts)
    suivant, _ = m329.les_sommets_proches(tours[LE_SUIVANT], arrivee_pts)
    s = m321.les_ecarts(ref, ref_n, suivant)
    t, s = t[np.isfinite(t)], s[np.isfinite(s)]
    out = {"en_face": int(len(t)), "en_face_du_suivant": int(len(s))}
    if len(t) < LE_MINIMUM_EN_FACE or len(s) < LE_MINIMUM_EN_FACE:
        return {**out, "lue": False, "les_tours_franchis": None}
    et, es = float(np.median(t)), float(np.median(s))
    return {**out, "lue": es != 0.0, "lecart_au_depart_en_pas": round(et / m321.LE_PAS_L0, 3),
            "lecart_du_suivant_en_pas": round(es / m321.LE_PAS_L0, 3), "les_tours_franchis": round(et / es, 3) if es else None}


def les_sauts_lus(cotes: list[dict]) -> list[dict]:
    """Les sauts partis du seul tour −6 que `m7` compte d'une ou deux feuilles, chacun une fois, avec les familles où il apparaît."""
    vus: dict[tuple, dict] = {}
    for c in cotes:
        for f in LES_FAMILLES:
            for s in c[f]:
                if s["le_nombre_de_feuilles"] not in LES_FEUILLES:
                    continue
                cle = m403.la_cle(c["le_rang"], c["le_cote"], s["la_chaine"], s)
                if cle not in vus:
                    vus[cle] = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], **s, "les_familles": []}
                vus[cle]["les_familles"].append(f)
    return list(vus.values())


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les chaînes relancées ne redonnent pas 403"}
    lus = [x for x in d["les_sauts"] if x["la_lecture"]["lue"]]
    temoin = [x["la_lecture"]["les_tours_franchis"] for x in lus if x["le_nombre_de_feuilles"] == 1]
    deux = [x["la_lecture"]["les_tours_franchis"] for x in lus if x["le_nombre_de_feuilles"] == 2]
    w = sum(LE_BAS <= k < LE_HAUT for k in temoin)
    k2 = sum(k >= LE_HAUT for k in deux)
    tete = f"sauts de deux feuilles partis du tour −6 : {k2} sur {len(deux)} à au moins {LE_HAUT:g} tour ; témoin : {w} sur {len(temoin)} entre {LE_BAS:g} et {LE_HAUT:g}"
    tete = tete.replace(".", ",")
    if len(temoin) < LE_TEMOIN_MINIMUM or w < LA_PART_DU_TEMOIN * len(temoin):
        return {"decidable": False, "lissue": f"{tete} ; indécidable, le témoin ne vaut pas"}
    if len(deux) < LE_MINIMUM_DE_DEUX:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, moins de {LE_MINIMUM_DE_DEUX} sauts de deux feuilles lus"}
    suite = "oui" if k2 == len(deux) else "non" if k2 == 0 else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def une_famille(enchainer) -> tuple[dict, list, list, object]:
    m379._LES_TROIS.clear()
    m397._LES_ROGNAGES.clear()
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=m379.le_chaineur(enchainer=enchainer))
    cotes = [(g["le_rang"], cote) for g in d331["les_graines"]["PHercParis4"] for cote in g["les_cotes"]]
    return d331, list(m379._LES_TROIS), cotes, lv["m7"]


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    d403 = json.loads(CE_QUE_403_A_PUBLIE.read_text())
    cotes = [{"le_rang": c["le_rang"], "le_cote": c["le_cote"], **{f: [] for f in LES_FAMILLES}} for c in d403["les_cotes"]]
    controle, pannes, ecartes = True, [], []
    for f, enchainer in LES_FAMILLES.items():
        d331, trois_, cotes_d331, lv = une_famille(enchainer)
        pannes += list(d331["les_pannes"])
        controle &= len(cotes_d331) == len(trois_) == len(d403["les_cotes"])
        for (rang, cote), trois, c403, c_out in zip(cotes_d331, trois_, d403["les_cotes"], cotes):
            controle &= (rang, cote) == (c403["le_rang"], c403["le_cote"])
            for x in LES_CHAINES:
                surfaces = [trois["les_nappes"][x]] + list(trois["les_relances"][x])
                retrouves = [m379.les_retrouves(s, tours) for s in surfaces]
                controle &= retrouves == c403[f][x]["les_tours"]
                for s403 in c403[f][x]["les_sauts"]:
                    h = s403["le_saut"]
                    if retrouves[h - 1] != [LE_DEPART] or s403["le_nombre_de_feuilles"] not in LES_FEUILLES:
                        continue
                    avant, apres = surfaces[h - 1], surfaces[h]
                    r = m345.les_comptes_point_par_point(avant, apres, lv, m385.LE_PAS)
                    comptes = m345.le_resume(r)["les_comptes"]
                    controle &= comptes == s403["les_comptes"] and m383.le_nombre_de_feuilles(comptes) == s403["le_nombre_de_feuilles"]
                    lecture = la_lecture(m379.les_points_lus(apres), tours)
                    c_out[f].append({"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": s403["le_nombre_de_feuilles"],
                                     "les_comptes": comptes, "le_tour_darrivee": retrouves[h], "la_lecture": lecture})
                    if not lecture["lue"]:
                        ecartes.append({"la_famille": f, "le_rang": rang, "le_cote": cote, "la_chaine": x, "le_saut": h, **lecture})
            print(json.dumps({"la_famille": f, "le_rang": rang, "le_cote": cote, "controle": bool(controle),
                              "lus": len(c_out[f])}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_depart": LE_DEPART, "le_suivant": LE_SUIVANT, "le_minimum_en_face": LE_MINIMUM_EN_FACE,
                            "le_temoin_minimum": LE_TEMOIN_MINIMUM, "la_part_du_temoin": LA_PART_DU_TEMOIN, "le_bas": LE_BAS,
                            "le_haut": LE_HAUT, "le_minimum_de_deux": LE_MINIMUM_DE_DEUX, "le_pas_l0": round(m321.LE_PAS_L0, 3)},
         "les_pannes": pannes, "le_controle": bool(controle), "les_cotes": cotes, "les_sauts": les_sauts_lus(cotes),
         "les_ecartes": ecartes}
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

    g = np.stack(np.meshgrid(np.arange(0.0, 400.0, 10.0), np.arange(0.0, 400.0, 10.0)), -1).reshape(-1, 2)
    plan = lambda z: np.column_stack([g, np.full(len(g), z)])  # noqa: E731
    haut = np.tile([0.0, 0.0, 1.0], (len(g), 1))
    tours = {LE_DEPART: {"points": plan(0.0), "normales": haut}, LE_SUIVANT: {"points": plan(50.0), "normales": haut}}
    l2, l1 = la_lecture(plan(100.0), tours), la_lecture(plan(52.0), tours)
    v("★★★★ une surface à deux écarts de tour du tour −6 franchit deux tours, une surface près du tour −7 en franchit un",
      l2["les_tours_franchis"] == 2.0 and abs(l1["les_tours_franchis"] - 1.04) < 1e-9, f"{l2} {l1}")
    v("★★★★ l'unité est l'écart local des deux tours, pas le pas nominal",
      la_lecture(plan(100.0), {**tours, LE_SUIVANT: {"points": plan(25.0), "normales": haut}})["les_tours_franchis"] == 4.0)
    loin = {**tours, LE_SUIVANT: {"points": plan(50.0) + [1000.0, 0.0, 0.0], "normales": haut}}
    v("★★★ sans assez de sommets en face d'un des deux tours, le saut n'est pas lu",
      not la_lecture(plan(100.0), loin)["lue"] and la_lecture(plan(100.0), loin)["en_face_du_suivant"] == 0, str(la_lecture(plan(100.0), loin)))

    s_ = lambda x, h, n, c: {"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": n, "les_comptes": c}  # noqa: E731
    cotes = [{"le_rang": 5, "le_cote": "moins", "385": [s_("suivie", 8, 2, {"2": 9})], "rognees": [s_("suivie", 8, 2, {"2": 9})]},
             {"le_rang": 6, "le_cote": "moins", "385": [s_("suivie", 7, 2, {"2": 9})], "rognees": [s_("suivie", 7, 2, {"2": 8}),
                                                                                                   s_("tierce", 3, 3, {"3": 9})]}]
    v("★★★★ un saut lu une fois quand rien ne le distingue d'une famille à l'autre, deux fois sinon ; trois feuilles ne sont pas lues",
      [x["les_familles"] for x in les_sauts_lus(cotes)] == [["385", "rognees"], ["385"], ["rognees"]])

    def d_(temoin, deux, ok=True):
        lu = lambda n, k: {"le_nombre_de_feuilles": n, "la_lecture": {"lue": True, "les_tours_franchis": k}}  # noqa: E731
        return {"le_controle": ok, "les_pannes": [], "les_sauts": [lu(1, k) for k in temoin] + [lu(2, k) for k in deux]}
    t5 = [1.0, 0.9, 1.1, 0.7, 1.3]
    v("★★★★ la règle : témoin valable, tous à 1,5 au moins, oui ; aucun, non ; sinon, en partie",
      le_verdict(d_(t5, [2.0, 1.6]))["lissue"].endswith("; oui") and le_verdict(d_(t5, [1.0, 1.4]))["lissue"].endswith("; non")
      and le_verdict(d_(t5, [2.0, 1.0]))["lissue"].endswith("; en partie"))
    v("★★★★ l'issue dit les deux comptes",
      le_verdict(d_(t5, [2.0, 1.0]))["lissue"]
      == "sauts de deux feuilles partis du tour −6 : 1 sur 2 à au moins 1,5 tour ; témoin : 5 sur 5 entre 0,5 et 1,5 ; en partie")
    v("★★★★ le témoin ne vaut pas sous 5 sauts ou sous 80 % entre 0,5 et 1,5",
      not le_verdict(d_(t5[:4], [2.0, 2.0]))["decidable"] and not le_verdict(d_([1.0, 1.0, 1.0, 1.6, 0.4], [2.0, 2.0]))["decidable"]
      and le_verdict(d_([1.0, 1.0, 1.0, 1.0, 1.6], [2.0, 2.0]))["decidable"])
    v("★★★ indécidable sous 2 sauts de deux feuilles, ou sans contrôle",
      not le_verdict(d_(t5, [2.0]))["decidable"] and not le_verdict(d_(t5, [2.0, 2.0], ok=False))["decidable"])

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
