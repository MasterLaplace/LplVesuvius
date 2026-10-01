"""Sur PHercParis4, la lecture de 404 donne-t-elle un tour aux sauts d'une feuille jugés justes, là où le tour d'arrivée est retrouvé ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE DISTANCE NE SOIT MESURÉE SUR UN SAUT JUGÉ. Ce qui était vu avant d'écrire : tout ce que
`296` à `404` publient, dont **`R4-F590`** (`404` : partis du tour −6, 1 seul des 23 sauts d'une feuille lus franchit entre 0,5 et 1,5
tour ; le tour −7 y est lu à 0,42-4,58 pas nominaux du tour −6) et **`R4-F589`** (`403` : les sauts jugés des deux familles, leurs tours
et leurs comptes). Les écarts de `404` ne portent que sur les sauts partis du tour −6.

⚠⚠⚠ UN DÉFAUT DE `404`, VU EN PRÉPARANT CETTE TRANCHE. `404` dit lire l'écart du tour −7 « au même endroit » que l'arrivée. Son code
prend la médiane des écarts de l'arrivée sur les sommets du tour −6 qui lui font face, mais celle du tour −7 sur **tous** les sommets du
tour −6 de la boîte qui font face au tour −7, en face de l'arrivée ou non. Les deux médianes ne sont pas prises au même endroit.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P202`. Au tour −6, le témoin de `404` ne vaut pas. La faute peut être au tour −7 publié ou à
la lecture. Là où un saut d'une feuille est jugé juste, du tour k au tour k − 1, les deux tours sont publiés et l'arrivée retrouve le
second : une lecture qui vaut doit y donner un tour.

## Ce qui est fait

- **Les chaînes** : les deux familles de `403` et `404`, relancées sur les seize côtés. Le contrôle : les tours retrouvés redonnent ceux de
  `403` surface par surface, et la lecture de `404` redonne, saut par saut, celle que `404` publie.
- **Les sauts jugés justes** : ceux que `403` juge justes d'une feuille pour un tour, du tour k au tour k − 1. Un saut rogné que rien ne
  distingue d'un saut de `385` n'est lu qu'une fois.
- **Deux lectures de chaque saut**, avec le tour k pour départ et le tour k − 1 pour suivant. **Au même endroit** : les deux médianes sur
  les seuls sommets du tour k qui font face à la fois à l'arrivée et au tour k − 1, au moins 50. **La lecture de `404`**, telle qu'elle
  est publiée.
- **La règle**, la même pour chacune des deux lectures : au moins 80 % des sauts lus entre 0,5 et 1,5 tour, **oui** ; moins de 50 %,
  **non** ; sinon, **en partie**. Indécidable sous 5 sauts lus, si une lecture de `m7` échoue ou si le contrôle échoue.

⚠⚠ CE QUE LE TEST VAUT. Une arrivée qui retrouve le tour k − 1 est à un quart de pas de lui en médiane : là où les deux tours sont
parallèles, une lecture juste ne peut guère donner autre chose qu'un tour. Le test ne peut échouer que si la lecture se trompe de
géométrie. C'est ce qu'il cherche.

## Les issues

L'issue de la tranche : **sauts d'une feuille jugés justes : au même endroit, a sur n entre 0,5 et 1,5 tour ; lecture de 404, b sur m**,
puis ce que dit la règle pour chacune.

## Rapporté à côté, qui ne décide rien

- **La relecture du tour −6** : les sauts de `404`, partis du tour −6 et comptés d'une ou deux feuilles, lus au même endroit et jugés par
  la règle de `404`. ⚠ Une relecture : les écarts de leurs arrivées ont été vus dans `404`.
- Pour chaque saut lu, son tour de départ, ses deux écarts en pas nominaux et ses tours franchis par les deux lectures.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un saut de deux feuilles en franchit deux, ni rien sur PHerc0358.

Usage :
    uv run python src/nappe/la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.py --verifier
    uv run python src/nappe/la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.py \\
        --json docs/mesures/la_lecture_de_404_donne_t_elle_un_tour_aux_sauts_justes_dune_feuille_sur_paris4.json
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
import un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4 as m403  # noqa: E402
import un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4 as m404  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_403_A_PUBLIE = m404.CE_QUE_403_A_PUBLIE
CE_QUE_404_A_PUBLIE = LES_MESURES / "un_saut_de_deux_feuilles_parti_du_tour_moins_six_finit_il_au_dela_du_suivant_sur_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LES_FAMILLES = m404.LES_FAMILLES
LE_MINIMUM_EN_FACE = m321.LE_MINIMUM
LE_BAS, LE_HAUT = m404.LE_BAS, m404.LE_HAUT
LA_PART, LA_MOITIE = 0.8, 0.5
LE_MINIMUM = 5


def la_lecture(arrivee_pts: np.ndarray, tours: dict, depart: int, suivant: int) -> dict:
    """Les tours que franchit une surface d'arrivée depuis le tour `depart`, lus au même endroit : sur les seuls sommets du tour de
    départ qui font face à la fois à l'arrivée et au tour `suivant`, l'écart médian de l'arrivée rapporté à celui du tour suivant."""
    ref, ref_n = m329.les_sommets_proches(tours[depart], arrivee_pts)
    t = m321.les_ecarts(ref, ref_n, arrivee_pts)
    proches, _ = m329.les_sommets_proches(tours[suivant], arrivee_pts)
    s = m321.les_ecarts(ref, ref_n, proches)
    m = np.isfinite(t) & np.isfinite(s)
    out = {"en_face": int(m.sum())}
    if m.sum() < LE_MINIMUM_EN_FACE:
        return {**out, "lue": False, "les_tours_franchis": None}
    et, es = float(np.median(t[m])), float(np.median(s[m]))
    return {**out, "lue": es != 0.0, "lecart_au_depart_en_pas": round(et / m321.LE_PAS_L0, 3),
            "lecart_du_suivant_en_pas": round(es / m321.LE_PAS_L0, 3), "les_tours_franchis": round(et / es, 3) if es else None}


def la_lecture_de_404(arrivee_pts: np.ndarray, tours: dict, depart: int, suivant: int) -> dict:
    """La lecture de `404`, telle qu'elle est publiée, avec `depart` et `suivant` à la place des tours −6 et −7."""
    return m404.la_lecture(arrivee_pts, {m404.LE_DEPART: tours[depart], m404.LE_SUIVANT: tours[suivant]})


def les_sauts(cotes: list[dict], partie: str) -> list[dict]:
    """Les sauts d'une partie (`juste` ou `de_moins_six`), chacun une fois, avec les familles où il apparaît."""
    vus: dict[tuple, dict] = {}
    for c in cotes:
        for f in LES_FAMILLES:
            for s in c[f]:
                if not s[partie]:
                    continue
                cle = m403.la_cle(c["le_rang"], c["le_cote"], s["la_chaine"], s)
                if cle not in vus:
                    vus[cle] = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], **s, "les_familles": []}
                vus[cle]["les_familles"].append(f)
    return list(vus.values())


def la_part(ks: list[float]) -> int:
    return sum(LE_BAS <= k < LE_HAUT for k in ks)


def le_dit(ks: list[float]) -> str:
    n = la_part(ks)
    return "oui" if n >= LA_PART * len(ks) else "non" if n < LA_MOITIE * len(ks) else "en partie"


def les_lus(sauts: list[dict], lecture: str) -> list[float]:
    return [x[lecture]["les_tours_franchis"] for x in sauts if x[lecture]["lue"]]


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les chaînes relancées ne redonnent pas 403 et 404"}
    a, b = les_lus(d["les_sauts_justes"], "au_meme_endroit"), les_lus(d["les_sauts_justes"], "la_lecture_de_404")
    tete = (f"sauts d'une feuille jugés justes : au même endroit, {la_part(a)} sur {len(a)} entre {LE_BAS:g} et {LE_HAUT:g} tour ; "
            f"lecture de 404, {la_part(b)} sur {len(b)}").replace(".", ",")
    if len(a) < LE_MINIMUM or len(b) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, moins de {LE_MINIMUM} sauts lus"}
    return {"decidable": True, "lissue": f"{tete} ; au même endroit : {le_dit(a)} ; lecture de 404 : {le_dit(b)}"}


def la_relecture(d: dict) -> dict:
    """Rapporté, ne décide rien : les sauts de `404` lus au même endroit, jugés par la règle de `404`."""
    return m404.le_verdict({"les_pannes": d["les_pannes"], "le_controle": d["le_controle"],
                            "les_sauts": [{"le_nombre_de_feuilles": x["le_nombre_de_feuilles"], "la_lecture": x["au_meme_endroit"]}
                                          for x in d["les_sauts_de_moins_six"]]})


def mesurer() -> dict:
    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    d403 = json.loads(CE_QUE_403_A_PUBLIE.read_text())
    d404 = json.loads(CE_QUE_404_A_PUBLIE.read_text())
    lus404 = {(c["le_rang"], c["le_cote"], f, s["la_chaine"], s["le_saut"]): s["la_lecture"]
              for c in d404["les_cotes"] for f in LES_FAMILLES for s in c[f]}
    vus404 = set()
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
                    controle &= not juste or arrivee == [k - 1]
                    pts = m379.les_points_lus(surfaces[h])
                    e = {"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": s403["le_nombre_de_feuilles"],
                         "les_comptes": s403["les_comptes"], "le_depart": k, "larrivee": arrivee, "juste": juste,
                         "de_moins_six": de_moins_six, "au_meme_endroit": la_lecture(pts, tours, k, k - 1),
                         "la_lecture_de_404": la_lecture_de_404(pts, tours, k, k - 1)}
                    if de_moins_six:
                        cle = (rang, cote, f, x, h)
                        vus404.add(cle)
                        controle &= lus404.get(cle) == e["la_lecture_de_404"]
                    c_out[f].append(e)
            print(json.dumps({"la_famille": f, "le_rang": rang, "le_cote": cote, "controle": bool(controle),
                              "lus": len(c_out[f])}, ensure_ascii=False), flush=True)
    controle &= vus404 == set(lus404)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum_en_face": LE_MINIMUM_EN_FACE, "le_bas": LE_BAS, "le_haut": LE_HAUT, "la_part": LA_PART,
                            "la_moitie": LA_MOITIE, "le_minimum": LE_MINIMUM, "le_pas_l0": round(m321.LE_PAS_L0, 3)},
         "les_pannes": pannes, "le_controle": bool(controle), "les_cotes": cotes,
         "les_sauts_justes": les_sauts(cotes, "juste"), "les_sauts_de_moins_six": les_sauts(cotes, "de_moins_six")}
    d["le_verdict"] = le_verdict(d)
    d["la_relecture"] = la_relecture(d)
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
    haut = lambda m=None: np.tile([0.0, 0.0, 1.0], (len(g), 1))[m if m is not None else slice(None)]  # noqa: E731
    tours = {-2: {"points": plan(0.0), "normales": haut()}, -3: {"points": plan(50.0), "normales": haut()}}
    l1, l2 = la_lecture(plan(50.0), tours, -2, -3), la_lecture(plan(100.0), tours, -2, -3)
    v("★★★★ une arrivée sur le tour suivant franchit un tour, une arrivée à deux écarts en franchit deux",
      l1["les_tours_franchis"] == 1.0 and l2["les_tours_franchis"] == 2.0, f"{l1} {l2}")
    gauche, droite = g[:, 0] <= 150.0, g[:, 0] >= 250.0
    ailleurs = {-2: tours[-2], -3: {"points": plan(50.0, droite), "normales": haut(droite)}}
    v("★★★★ un tour suivant qui n'est pas en face de l'arrivée n'est pas lu au même endroit, alors que la lecture de 404 le lit",
      not la_lecture(plan(50.0, gauche), ailleurs, -2, -3)["lue"] and la_lecture_de_404(plan(50.0, gauche), ailleurs, -2, -3)["lue"],
      f"{la_lecture(plan(50.0, gauche), ailleurs, -2, -3)} {la_lecture_de_404(plan(50.0, gauche), ailleurs, -2, -3)}")
    etroite, sous = g[:, 0] <= 30.0, np.where(g[:, 0] <= 30.0, 50.0, 60.0)
    marche = {-2: tours[-2], -3: {"points": np.column_stack([g, sous]), "normales": haut()}}
    v("★★★★ au même endroit, le tour suivant pris hors de la face de l'arrivée ne compte pas ; dans la lecture de 404, il compte",
      la_lecture(plan(50.0, etroite), marche, -2, -3)["les_tours_franchis"] == 1.0
      and la_lecture_de_404(plan(50.0, etroite), marche, -2, -3)["les_tours_franchis"] == round(50.0 / 55.0, 3),
      f"{la_lecture(plan(50.0, etroite), marche, -2, -3)} {la_lecture_de_404(plan(50.0, etroite), marche, -2, -3)}")
    v("★★★★ la lecture de 404 est celle que 404 publie, aux tours près",
      la_lecture_de_404(plan(100.0), tours, -2, -3) == m404.la_lecture(plan(100.0), {-6: tours[-2], -7: tours[-3]}))

    e_ = lambda x, h, n, c, j, s6: {"la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": n, "les_comptes": c,  # noqa: E731
                                    "juste": j, "de_moins_six": s6}
    cotes = [{"le_rang": 4, "le_cote": "moins", "385": [e_("suivie", 2, 1, {"1": 9}, True, False), e_("suivie", 8, 1, {"1": 7}, False, True)],
              "rognees": [e_("suivie", 2, 1, {"1": 9}, True, False), e_("tierce", 3, 1, {"1": 5}, True, False)]}]
    v("★★★★ un saut juste lu une fois quand rien ne le distingue d'une famille à l'autre ; les parties ne se mêlent pas",
      [x["les_familles"] for x in les_sauts(cotes, "juste")] == [["385", "rognees"], ["rognees"]]
      and [x["le_saut"] for x in les_sauts(cotes, "de_moins_six")] == [8])

    def d_(a, b, ok=True):
        lu = lambda k: {"lue": True, "les_tours_franchis": k}  # noqa: E731
        return {"le_controle": ok, "les_pannes": [], "les_sauts_justes": [{"au_meme_endroit": lu(x), "la_lecture_de_404": lu(y)}
                                                                          for x, y in zip(a, b)]}
    v("★★★★ la règle : 80 % entre 0,5 et 1,5, oui ; moins de 50 %, non ; sinon, en partie",
      le_verdict(d_([1.0] * 4 + [3.0], [1.0] * 2 + [3.0] * 3))["lissue"].endswith("au même endroit : oui ; lecture de 404 : non")
      and le_verdict(d_([1.0] * 3 + [3.0] * 2, [1.0] * 5))["lissue"].endswith("au même endroit : en partie ; lecture de 404 : oui"))
    v("★★★★ l'issue dit les deux comptes",
      le_verdict(d_([1.0] * 4 + [3.0], [1.0] * 2 + [0.2] * 3))["lissue"]
      == "sauts d'une feuille jugés justes : au même endroit, 4 sur 5 entre 0,5 et 1,5 tour ; lecture de 404, 2 sur 5 ; "
         "au même endroit : oui ; lecture de 404 : non")
    v("★★★★ la borne haute est exclue, la borne basse incluse", la_part([0.5, 1.5, 1.49, 0.49]) == 2)
    v("★★★ indécidable sous 5 sauts lus, ou sans contrôle",
      not le_verdict(d_([1.0] * 4, [1.0] * 4))["decidable"] and not le_verdict(d_([1.0] * 5, [1.0] * 5, ok=False))["decidable"])
    rel = la_relecture({"les_pannes": [], "le_controle": True, "les_sauts_de_moins_six":
                        [{"le_nombre_de_feuilles": 1, "au_meme_endroit": {"lue": True, "les_tours_franchis": 1.0}}] * 5
                        + [{"le_nombre_de_feuilles": 2, "au_meme_endroit": {"lue": True, "les_tours_franchis": 2.0}}] * 2})
    v("★★★ la relecture est jugée par la règle de 404, sur la lecture au même endroit", rel["lissue"].endswith("; oui"), str(rel))

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
    print(json.dumps(d["la_relecture"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
