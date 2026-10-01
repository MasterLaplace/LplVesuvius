"""Sur PHercParis4, là où l'arrivée d'un saut d'une feuille parti du tour −6 est lue, sa surface de départ est-elle sur le tour −6 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE DE DÉPART NE SOIT LUE. Ce qui était vu avant d'écrire : tout ce que `296` à `405`
publient, dont **`R4-F591`** (`405` : là où le tour d'arrivée est retrouvé, la lecture au même endroit donne un tour à 156 des 162 sauts
d'une feuille jugés justes ; relu au même endroit, le témoin du tour −6 ne vaut pas, 2 sur 20 ; sur les graines 4 à 6, le tour −7 y est
à 0,43-0,56 pas du tour −6 et les arrivées à 1,58-1,74) et **`R4-C49`**. `403` à `405` ne lisent que les surfaces d'arrivée : aucun
écart d'une surface de départ n'a été publié.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P203`. Une bissection par frontière : un saut va d'une surface de départ à une surface
d'arrivée, et la lecture les rapporte au tour −6 et au tour −7. La surface de départ retrouve le tour −6 sur l'ensemble de ses sommets en
face, mais rien ne dit qu'elle est sur lui là où l'arrivée est lue. Deux hypothèses restent ouvertes :
- **H1, le départ n'y est pas sur le tour −6** : son écart au tour −6, au même endroit, dépasse un quart de pas, et le saut lui-même,
  de la surface de départ à celle d'arrivée, est plus court que l'écart de l'arrivée au tour −6.
- **H2, le départ y est sur le tour −6** : son écart y tient dans un quart de pas, et c'est le saut lui-même qui va à 1,58-1,74 pas. La
  faute est alors au tour −7 publié, trop près, ou au compte de `m7`.

## Ce qui est fait

- **Les chaînes** : les deux familles de `403` à `405`, relancées sur les seize côtés. Le contrôle : les tours retrouvés redonnent ceux
  de `403` surface par surface, et la lecture au même endroit de `405` redonne, saut par saut, celle que `405` publie.
- **Les sauts lus** : ceux de `405`. **Le témoin** : les sauts d'une feuille que `403` juge justes, du tour k au tour k − 1. **La
  cible** : les sauts d'une feuille partis du seul tour −6.
- **Le même endroit** : les sommets du tour de départ, dans la boîte de l'arrivée, qui font face à la fois à la surface d'arrivée, au
  tour suivant et à la surface de départ, au moins 50. Sur eux : l'écart médian de la surface de départ, celui de la surface d'arrivée,
  celui du tour suivant, et la médiane de l'écart d'arrivée moins l'écart de départ, **le saut en pas**.
- **Un départ est sur son tour** si son écart médian au même endroit tient dans un quart de pas nominal.
- **La règle** : le témoin vaut si au moins 5 de ses sauts sont lus et qu'au moins 80 % de leurs départs sont sur leur tour. S'il vaut :
  au moins 80 % des départs de la cible sur le tour −6, **oui** (H2) ; moins de 50 %, **non** (H1) ; sinon, **en partie**. Indécidable si
  le témoin ne vaut pas, sous 5 sauts de la cible lus, si une lecture de `m7` échoue ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **départs sur le tour −6 au même endroit : k sur n ; témoin : w sur t sur leur tour**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Le saut en pas, pour le témoin et pour la cible ; pour chaque saut lu, ses trois écarts en pas nominaux ; les sauts de deux feuilles
partis du tour −6, lus de même.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si `H2` vaut, lequel du tour −7 publié ou du compte de `m7` se trompe ; rien sur PHerc0358.

Usage :
    uv run python src/nappe/le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.py --verifier
    uv run python src/nappe/le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.py \\
        --json docs/mesures/le_depart_dun_saut_parti_du_tour_moins_six_est_il_sur_ce_tour_sur_paris4.json
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

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4 as m404  # noqa: E402
import la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4 as m405  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_403_A_PUBLIE = m404.CE_QUE_403_A_PUBLIE
CE_QUE_405_A_PUBLIE = LES_MESURES / "la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LES_FAMILLES = m404.LES_FAMILLES
LE_MINIMUM_EN_FACE = m321.LE_MINIMUM
LE_QUART_EN_PAS = m321.LE_QUART / m321.LE_PAS_L0
LA_PART, LA_MOITIE = 0.8, 0.5
LE_MINIMUM = 5


def la_lecture(depart_pts: np.ndarray, arrivee_pts: np.ndarray, tours: dict, depart: int, suivant: int) -> dict:
    """Au même endroit, sur les sommets du tour de départ qui font face à l'arrivée, au tour suivant et à la surface de départ : les
    écarts médians des deux surfaces et du tour suivant, et la médiane du saut d'une surface à l'autre, en pas nominaux."""
    ref, ref_n = m329.les_sommets_proches(tours[depart], arrivee_pts)
    ta = m321.les_ecarts(ref, ref_n, arrivee_pts)
    proches, _ = m329.les_sommets_proches(tours[suivant], arrivee_pts)
    s = m321.les_ecarts(ref, ref_n, proches)
    td = m321.les_ecarts(ref, ref_n, depart_pts)
    m = np.isfinite(ta) & np.isfinite(s) & np.isfinite(td)
    out = {"en_face": int(m.sum())}
    if m.sum() < LE_MINIMUM_EN_FACE:
        return {**out, "lue": False}
    en_pas = lambda x: round(float(np.median(x)) / m321.LE_PAS_L0, 3)  # noqa: E731
    e = {"lecart_du_depart_en_pas": en_pas(td[m]), "lecart_de_larrivee_en_pas": en_pas(ta[m]), "lecart_du_suivant_en_pas": en_pas(s[m]),
         "le_saut_en_pas": en_pas(ta[m] - td[m])}
    return {**out, "lue": True, **e, "sur_son_tour": abs(e["lecart_du_depart_en_pas"]) <= LE_QUART_EN_PAS}


def les_lus(sauts: list[dict]) -> list[dict]:
    return [x for x in sauts if x["au_depart"]["lue"]]


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les chaînes relancées ne redonnent pas 403 et 405"}
    temoin = les_lus(d["les_sauts_justes"])
    cible = [x for x in les_lus(d["les_sauts_de_moins_six"]) if x["le_nombre_de_feuilles"] == 1]
    w, k = sum(x["au_depart"]["sur_son_tour"] for x in temoin), sum(x["au_depart"]["sur_son_tour"] for x in cible)
    tete = f"départs sur le tour −6 au même endroit : {k} sur {len(cible)} ; témoin : {w} sur {len(temoin)} sur leur tour"
    if len(temoin) < LE_MINIMUM or w < LA_PART * len(temoin):
        return {"decidable": False, "lissue": f"{tete} ; indécidable, le témoin ne vaut pas"}
    if len(cible) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, moins de {LE_MINIMUM} sauts de la cible lus"}
    suite = "oui" if k >= LA_PART * len(cible) else "non" if k < LA_MOITIE * len(cible) else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    d403 = json.loads(CE_QUE_403_A_PUBLIE.read_text())
    d405 = json.loads(CE_QUE_405_A_PUBLIE.read_text())
    lus405 = {(c["le_rang"], c["le_cote"], f, s["la_chaine"], s["le_saut"]): s["au_meme_endroit"]
              for c in d405["les_cotes"] for f in LES_FAMILLES for s in c[f]}
    vus405 = set()
    cotes = [{"le_rang": c["le_rang"], "le_cote": c["le_cote"], **{f: [] for f in LES_FAMILLES}} for c in d403["les_cotes"]]
    controle, pannes = True, []
    for f, enchainer in LES_FAMILLES.items():
        d331, trois_, cotes_d331, _ = m404.une_famille(enchainer)
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
                    depart, arrivee = retrouves[h - 1], retrouves[h]
                    juste = s403["dit"] == "juste" and s403["le_nombre_de_feuilles"] == 1 and s403["les_tours"] == 1
                    de_moins_six = depart == [m404.LE_DEPART] and s403["le_nombre_de_feuilles"] in m404.LES_FEUILLES
                    if not (juste or de_moins_six):
                        continue
                    k = depart[0]
                    avant, apres = m379.les_points_lus(surfaces[h - 1]), m379.les_points_lus(surfaces[h])
                    cle = (rang, cote, f, x, h)
                    vus405.add(cle)
                    controle &= lus405.get(cle) == m405.la_lecture(apres, tours, k, k - 1)
                    c_out[f].append({"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": s403["le_nombre_de_feuilles"],
                                     "les_comptes": s403["les_comptes"], "le_depart": k, "larrivee": arrivee, "juste": juste,
                                     "de_moins_six": de_moins_six, "au_depart": la_lecture(avant, apres, tours, k, k - 1)})
            print(json.dumps({"la_famille": f, "le_rang": rang, "le_cote": cote, "controle": bool(controle),
                              "lus": len(c_out[f])}, ensure_ascii=False), flush=True)
    controle &= vus405 == set(lus405)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum_en_face": LE_MINIMUM_EN_FACE, "le_quart_en_pas": round(LE_QUART_EN_PAS, 3), "la_part": LA_PART,
                            "la_moitie": LA_MOITIE, "le_minimum": LE_MINIMUM, "le_pas_l0": round(m321.LE_PAS_L0, 3)},
         "les_pannes": pannes, "le_controle": bool(controle), "les_cotes": cotes,
         "les_sauts_justes": m405.les_sauts(cotes, "juste"), "les_sauts_de_moins_six": m405.les_sauts(cotes, "de_moins_six")}
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
    plan = lambda z, m=None: np.column_stack([g, np.full(len(g), z)])[m if m is not None else slice(None)]  # noqa: E731
    haut = np.tile([0.0, 0.0, 1.0], (len(g), 1))
    p = m321.LE_PAS_L0
    tours = {-2: {"points": plan(0.0), "normales": haut}, -3: {"points": plan(p), "normales": haut}}
    sur, loin = la_lecture(plan(0.0), plan(p), tours, -2, -3), la_lecture(plan(40.0), plan(80.0), tours, -2, -3)
    v("★★★★ un départ posé sur le tour est sur son tour, et le saut d'un pas mesure un pas",
      sur["sur_son_tour"] and sur["lecart_du_depart_en_pas"] == 0.0 and sur["le_saut_en_pas"] == 1.0, str(sur))
    v("★★★★ un départ loin du tour n'y est pas, et le saut se mesure depuis lui, pas depuis le tour",
      loin["lue"] and not loin["sur_son_tour"] and loin["lecart_du_depart_en_pas"] == round(40.0 / p, 3)
      and loin["le_saut_en_pas"] == round(40.0 / p, 3) and loin["lecart_de_larrivee_en_pas"] == round(80.0 / p, 3), str(loin))
    v("★★★★ la borne est un quart de pas, incluse",
      la_lecture(plan(0.25 * p), plan(p), tours, -2, -3)["sur_son_tour"]
      and not la_lecture(plan(0.26 * p), plan(p), tours, -2, -3)["sur_son_tour"])
    gauche = g[:, 0] >= 250.0
    v("★★★★ un départ qui ne fait pas face aux sommets où l'arrivée est lue n'est pas lu",
      not la_lecture(plan(0.0, gauche), plan(p, g[:, 0] <= 150.0), tours, -2, -3)["lue"])

    def d_(temoin, cible, ok=True):
        lu = lambda s: {"le_nombre_de_feuilles": 1, "au_depart": {"lue": True, "sur_son_tour": s}}  # noqa: E731
        return {"le_controle": ok, "les_pannes": [], "les_sauts_justes": [lu(s) for s in temoin],
                "les_sauts_de_moins_six": [lu(s) for s in cible] + [{"le_nombre_de_feuilles": 2, "au_depart": {"lue": True, "sur_son_tour": True}}]}
    t5 = [True] * 4 + [False]
    v("★★★★ la règle : témoin valable, 80 % sur le tour −6, oui ; moins de 50 %, non ; sinon, en partie",
      le_verdict(d_(t5, [True] * 5))["lissue"].endswith("; oui") and le_verdict(d_(t5, [True] * 2 + [False] * 3))["lissue"].endswith("; non")
      and le_verdict(d_(t5, [True] * 3 + [False] * 2))["lissue"].endswith("; en partie"))
    v("★★★★ l'issue dit les deux comptes, sans les sauts de deux feuilles",
      le_verdict(d_(t5, [True] * 3 + [False] * 2))["lissue"]
      == "départs sur le tour −6 au même endroit : 3 sur 5 ; témoin : 4 sur 5 sur leur tour ; en partie")
    v("★★★★ le témoin ne vaut pas sous 80 % ou sous 5 sauts",
      not le_verdict(d_([True] * 3 + [False] * 2, [True] * 5))["decidable"] and not le_verdict(d_([True] * 4, [True] * 5))["decidable"])
    v("★★★ indécidable sous 5 sauts de la cible, ou sans contrôle",
      not le_verdict(d_(t5, [True] * 4))["decidable"] and not le_verdict(d_(t5, [True] * 5, ok=False))["decidable"])

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
