"""Sur PHercParis4, les surfaces tenues de deux chaînes d'une maille parties de graines différentes se recouvrent-elles, et là où elles se recouvrent, sont-elles sur la même feuille exactement quand elles sont sur le même tour publié ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PAIRE DE SURFACES NE SOIT COMPARÉE. Ce qui était vu avant d'écrire : tout ce que `296` à `366`
publient, dont `R4-F551` (sur PHercParis4, la chaîne d'une maille est juste sous ses 24 sauts jugés des graines 4, 5, 6 et 8, sans cheval)
et `R4-F552` (sur PHerc0358, elle avance, mais rien n'y dit si ses surfaces sont sur leur feuille). Les graines de PHercParis4 vont par
paquets : les graines 4, 5 et 6 sont à 51 à 169 voxels du niveau 2 les unes des autres, les graines 7 et 8 à 192, et les paquets à plus de
3000 ; un plan fait 650 voxels de côté, donc deux chaînes d'un même paquet se recouvrent.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P164`. Deux chaînes indépendantes qui arrivent au même endroit ne se trompent pas ensemble
par hasard : si elles posent leurs surfaces sur la même feuille là, et seulement là où les tours publiés disent le même tour, leur accord
est un juge qui ne demande aucun tracé, et qui s'applique à PHerc0358.

## Ce qui est fait

- **Les chaînes** : la chaîne d'une maille de `365` sur PHercParis4, graines 4 à 8, côtés moins, rejouée par la fonction de `357`, qui
  dit pour cela à la lecture de chaque saut quelle graine, quel côté et quel saut elle lit.
- **Les surfaces** : pour chaque saut juste, la surface gardée, au plus 1200 points à normale connue pris comme le compte de `345` les
  prend ; son tour publié est le tour de départ du saut décalé d'un tour dans le sens du côté.
- **Les paires** : deux surfaces justes de deux graines différentes dont les tours sont les mêmes ou voisins. Pour chaque point de la
  première, l'écart signé, le long de sa normale, au point de la seconde le plus proche, s'il est en face à la portée latérale de `345` ;
  les deux **se recouvrent** si au moins 50 points ont un écart d'au plus un pas et demi.
- **Même feuille** : la médiane des écarts absolus des points en face est d'au plus un quart de pas nominal.
- **La règle** : parmi les paires qui se recouvrent, la part où « même feuille » et « même tour » disent la même chose. Au moins 90 %,
  **oui, l'accord de deux chaînes dit le tour** ; moins de 75 %, **non** ; sinon, **en partie**. Indécidable sous 10 paires sur le même
  tour ou sous 10 sur des tours voisins.

## Les issues

L'issue de la tranche : **sur n paires de surfaces qui se recouvrent, la même feuille et le même tour s'accordent sous a**, puis ce que
dit la règle.

## Rapporté à côté, qui ne décide rien

La table des quatre cas ; la médiane des écarts sur le même tour et sur des tours voisins.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si l'accord tient là où deux chaînes héritent du même décalage ; ni ce qu'il vaut sur PHerc0358.

Usage :
    uv run python src/nappe/deux_chaines_qui_se_croisent_disent_elles_le_tour.py --verifier
    uv run python src/nappe/deux_chaines_qui_se_croisent_disent_elles_le_tour.py \\
        --json docs/mesures/deux_chaines_qui_se_croisent_disent_elles_le_tour.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_dune_seule_maille_evite_il_le_decalage as m365  # noqa: E402

LE_MINIMUM_EN_FACE = 50
LE_QUART = m321.LE_PAS_L2 / 4.0
LA_PORTEE = 1.5 * m321.LE_PAS_L2
LE_MINIMUM = 10
_LES_SURFACES: dict = {}


def les_points(surface: dict | None) -> tuple[np.ndarray, np.ndarray]:
    """Au plus `m326.LE_MAXIMUM_DE_POINTS` points de la surface à normale connue, pris comme le compte de `345` les prend, et leurs
    normales."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    if surface is None or not surface["valide"].any():
        return np.zeros((0, 3)), np.zeros((0, 3))
    nn, nok = les_normales(surface["la_nappe"], surface["valide"])
    m = surface["valide"] & nok
    q, nq = surface["la_nappe"][m], nn[m]
    if len(q) > m345.m326.LE_MAXIMUM_DE_POINTS:
        k = np.linspace(0, len(q) - 1, m345.m326.LE_MAXIMUM_DE_POINTS).round().astype(int)
        q, nq = q[k], nq[k]
    return q, nq


def garder(k: dict, lire_valeurs) -> dict:
    """Garde en mémoire, sous la graine, le côté et le saut en cours de lecture, les points de la surface gardée."""
    q, nq = les_points(k.get("la_relance"))
    _LES_SURFACES[(m357.LE_SAUT_OBSERVE["le_rang"], m357.LE_SAUT_OBSERVE["le_cote"], m357.LE_SAUT_OBSERVE["le_saut"])] = (q, nq)
    return {"les_points_gardes": int(len(q))}


def la_comparaison(a: tuple[np.ndarray, np.ndarray], b: tuple[np.ndarray, np.ndarray], lateral: float = m345.LE_LATERAL_L2) -> dict:
    """Les points de `a` qui ont `b` en face à un pas et demi au plus, et la médiane de leurs écarts absolus."""
    e = m321.les_ecarts(a[0], a[1], b[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= LA_PORTEE)
    return {"en_face": int(vus.sum()), "lecart_median": round(float(np.median(np.abs(e[vus]))), 3) if vus.any() else None}


def les_surfaces_justes(cotes: list[dict]) -> list[dict]:
    """Les surfaces des sauts justes des côtés moins des graines 4 à 8, avec leur tour publié."""
    out = []
    for c in cotes:
        if c["le_rang"] not in m344.LES_GRAINES_PROPRES or c["le_cote"] != "moins":
            continue
        for s in c["les_sauts"]:
            if s["la_justesse"] == "juste" and s.get("le_tour_de_depart") is not None:
                out.append({"le_rang": c["le_rang"], "le_saut": s["le_saut"], "le_tour": s["le_tour_de_depart"] + m344.LE_SENS["moins"]})
    return out


def les_paires(surfaces: list[dict], points: dict, comparer=la_comparaison) -> list[dict]:
    out = []
    for x, y in combinations(surfaces, 2):
        if x["le_rang"] == y["le_rang"] or abs(x["le_tour"] - y["le_tour"]) > 1:
            continue
        c = comparer(points[(x["le_rang"], "moins", x["le_saut"])], points[(y["le_rang"], "moins", y["le_saut"])])
        if c["en_face"] < LE_MINIMUM_EN_FACE:
            continue
        meme_feuille = c["lecart_median"] <= LE_QUART
        out.append({"a": [x["le_rang"], x["le_saut"], x["le_tour"]], "b": [y["le_rang"], y["le_saut"], y["le_tour"]], **c,
                    "meme_tour": x["le_tour"] == y["le_tour"], "meme_feuille": bool(meme_feuille)})
    return out


def le_bilan(paires: list[dict]) -> dict:
    t = {f"{'meme' if mt else 'voisin'}_{'meme' if mf else 'autre'}": sum(p["meme_tour"] == mt and p["meme_feuille"] == mf for p in paires)
         for mt in (True, False) for mf in (True, False)}
    ecarts = {k: [p["lecart_median"] for p in paires if p["meme_tour"] == mt] for k, mt in (("meme_tour", True), ("tours_voisins", False))}
    return {"les_paires": len(paires), "daccord": t["meme_meme"] + t["voisin_autre"], "la_table": t,
            "lecart_median": {k: (round(float(np.median(v)), 3) if v else None) for k, v in ecarts.items()},
            "sur_le_meme_tour": t["meme_meme"] + t["meme_autre"], "sur_des_tours_voisins": t["voisin_meme"] + t["voisin_autre"]}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les nappes de départ ne sont pas celles que 340 publie"}
    b = d["le_bilan"]
    if b["sur_le_meme_tour"] < LE_MINIMUM or b["sur_des_tours_voisins"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {b['sur_le_meme_tour']} paires sur le même tour et "
                                              f"{b['sur_des_tours_voisins']} sur des tours voisins"}
    tete = f"sur {b['les_paires']} paires de surfaces qui se recouvrent, la même feuille et le même tour s'accordent sous {b['daccord']}"
    p = b["daccord"] / b["les_paires"]
    suite = "oui, l'accord de deux chaînes dit le tour" if p >= 0.9 else "non" if p < 0.75 else "en partie"
    return {"decidable": True, "p": round(p, 4), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    _LES_SURFACES.clear()
    r = m357.la_chaine_jugee(chainer=m365.la_chaine_dune_maille, en_plus=garder)
    surfaces = les_surfaces_justes(r["les_cotes"])
    paires = les_paires(surfaces, _LES_SURFACES)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_quart": round(LE_QUART, 3), "la_portee": round(LA_PORTEE, 3), "le_minimum_en_face": LE_MINIMUM_EN_FACE,
                            "le_minimum": LE_MINIMUM},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": r["le_controle"],
         "les_surfaces": surfaces, "les_paires": paires, "le_bilan": le_bilan(paires)}
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

    def plan(z, n=30, dx=0.0):
        g = np.zeros((n, n, 3))
        g[..., 0], g[..., 1] = np.meshgrid(np.arange(n) * 3.0 + dx, np.arange(n) * 3.0)
        g[..., 2] = z
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    a, b, c = les_points(plan(0.0)), les_points(plan(2.0, dx=1.0)), les_points(plan(12.0))
    ab, ac = la_comparaison(a, b, lateral=5.0), la_comparaison(a, c, lateral=5.0)
    v("★★★★ la comparaison : les points en face, et la médiane de leurs écarts absolus",
      ab["en_face"] == 28 * 28 and abs(ab["lecart_median"] - 2.0) < 1e-6 and abs(ac["lecart_median"] - 12.0) < 1e-6, str((ab, ac)))
    avant = m321.les_ecarts
    m321.les_ecarts = lambda r_, n_, nuage, lateral=0.0: np.array([-2.0] * 60 + [9.0] * 40 + [np.nan] * 5)
    try:
        signe = la_comparaison((np.zeros((105, 3)), np.zeros((105, 3))), (np.zeros((1, 3)), None))
    finally:
        m321.les_ecarts = avant
    v("★★★★ la médiane des écarts absolus, ni la moyenne ni le signe", signe == {"en_face": 100, "lecart_median": 2.0}, str(signe))
    loin = la_comparaison(a, les_points(plan(40.0)), lateral=5.0)
    v("★★★ au-delà d'un pas et demi, pas en face", loin["en_face"] == 0 and loin["lecart_median"] is None, str(loin))
    k = {"la_relance": plan(0.0)}
    m357.LE_SAUT_OBSERVE.update({"le_rang": 5, "le_cote": "moins", "le_saut": 3})
    _LES_SURFACES.clear()
    g_ = garder(k, "m7")
    v("★★★ garder : les points de la surface gardée, sous la graine, le côté et le saut lus", g_ == {"les_points_gardes": 28 * 28}
      and list(_LES_SURFACES) == [(5, "moins", 3)])
    cotes = [{"le_rang": 5, "le_cote": "moins", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "le_tour_de_depart": 0},
                                                              {"le_saut": 2, "la_justesse": "faux : deux tours", "le_tour_de_depart": -1}]},
             {"le_rang": 5, "le_cote": "plus", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "le_tour_de_depart": 0}]},
             {"le_rang": 2, "le_cote": "moins", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "le_tour_de_depart": 0}]}]
    v("★★★★ les surfaces : les sauts justes des côtés moins des graines 4 à 8, au tour de départ décalé d'un tour vers l'intérieur",
      les_surfaces_justes(cotes) == [{"le_rang": 5, "le_saut": 1, "le_tour": -1}])
    surf = [{"le_rang": 4, "le_saut": 1, "le_tour": -1}, {"le_rang": 5, "le_saut": 1, "le_tour": -1},
            {"le_rang": 5, "le_saut": 2, "le_tour": -2}, {"le_rang": 6, "le_saut": 3, "le_tour": -4}, {"le_rang": 4, "le_saut": 2, "le_tour": -2},
            {"le_rang": 7, "le_saut": 2, "le_tour": -2}]
    faux = {"(4, 1)(5, 1)": {"en_face": 60, "lecart_median": 1.0}, "(4, 1)(5, 2)": {"en_face": 60, "lecart_median": 12.0},
            "(5, 1)(4, 2)": {"en_face": 40, "lecart_median": 12.0}, "(5, 2)(4, 2)": {"en_face": 60, "lecart_median": 3.0},
            "(4, 2)(7, 2)": {"en_face": 60, "lecart_median": 6.0}}
    vus = []

    def comparer(x, y):
        vus.append((x, y))
        return faux.get(f"{x}{y}", {"en_face": 0, "lecart_median": None})
    pts = {(s["le_rang"], "moins", s["le_saut"]): (s["le_rang"], s["le_saut"]) for s in surf}
    p = les_paires(surf, pts, comparer)
    v("★★★★ les paires : deux graines différentes, des tours mêmes ou voisins, 50 points en face ; même feuille à un quart de pas",
      [(tuple(x["a"][:2]), tuple(x["b"][:2]), x["meme_tour"], x["meme_feuille"]) for x in p]
      == [((4, 1), (5, 1), True, True), ((4, 1), (5, 2), False, False), ((5, 2), (4, 2), True, True), ((4, 2), (7, 2), True, False)]
      and ((4, 1), (6, 3)) not in vus and ((4, 1), (4, 2)) not in vus, str(p))
    b_ = le_bilan(p + [{"meme_tour": False, "meme_feuille": True, "lecart_median": 4.0}])
    v("★★★★ le bilan : la table des quatre cas, et l'accord", b_["daccord"] == 3 and b_["la_table"] == {"meme_meme": 2, "meme_autre": 1,
                                                                                                    "voisin_meme": 1, "voisin_autre": 1}
      and b_["sur_le_meme_tour"] == 3 and b_["sur_des_tours_voisins"] == 2, str(b_))

    def d_(accord, n=40, meme=20, voisins=20, ok=True):
        return {"les_pannes": [], "le_controle": ok, "le_bilan": {"les_paires": n, "daccord": accord, "sur_le_meme_tour": meme,
                                                                   "sur_des_tours_voisins": voisins}}
    v("★★★★ la règle : 90 %, oui ; sous 75 %, non ; entre les deux, en partie",
      le_verdict(d_(36))["lissue"].endswith("dit le tour") and le_verdict(d_(29))["lissue"].endswith("; non")
      and le_verdict(d_(30))["lissue"].endswith("en partie") and le_verdict(d_(35))["lissue"].endswith("en partie"))
    v("★★★ sous 10 paires sur le même tour ou sur des tours voisins, un contrôle tombé : indécidable",
      not le_verdict(d_(36, meme=9))["decidable"] and not le_verdict(d_(36, voisins=9))["decidable"]
      and not le_verdict(d_(36, ok=False))["decidable"] and le_verdict(d_(36, meme=10, voisins=10))["decidable"])

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
