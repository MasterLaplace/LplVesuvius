"""Sur les graines 4 à 8 de PHercParis4, le compte des feuilles de m7 qu'un saut franchit, point par point, sépare-t-il les sauts que la lecture stricte dit justes de ceux qu'elle dit faux ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE FEUILLE DE `m7` NE SOIT COMPTÉE ENTRE DEUX SURFACES D'UNE CHAÎNE. Ce qui était vu avant
d'écrire : tout ce que `296` à `344` publient, dont `R4-F523` (les tours publiés consécutifs sont à 0,53 à 0,93 pas nominal l'un de
l'autre), `R4-F527` et `R4-F530` : sur les graines 4 à 8, le critère de `328` tient 98 des 104 sauts justes et 5 des 6 faux ; quatre de
ces cinq faux retrouvent deux tours, le cinquième saute `5753_-5`, et tous posent entre 0,61 et 1,28 pas nominal.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P141`, TOUJOURS LA QUESTION DE `#5`. La fenêtre d'un demi-pas à un pas et demi contient
jusqu'à deux tours publiés : mesurer un saut en pas nominal ne dit pas s'il a franchi une feuille ou deux. Compter les feuilles de `m7`
entre la surface d'où part le saut et celle qu'il donne se passe du pas nominal comme du référent, et un rouleau sans tracé peut le faire.

## Ce qui est fait

- **Les chaînes et la lecture stricte** : celles de `344`, rejouées par sa mesure sans en changer une règle ; ses sauts, leurs lectures
  strictes et la tenue de `328` doivent redonner ce que `344` publie, sans quoi la tranche est indécidable.
- **Le compte, point par point** : pour au plus 1200 points posés de la surface que donne le saut, pris régulièrement, l'écart le long de
  sa normale à la surface d'où part le saut (la lecture de `321`, un point en face à au plus 10 voxels du niveau 2 de côté). Le long de
  cette normale, `m7` au niveau 2 sur trois pas et quart de chaque côté : le compte est le nombre de plages qu'on passe de celle qui
  porte le point à celle qui porte la surface de départ, chacune la plus proche de son bout ; **une feuille** si elles se suivent, zéro
  si c'est la même, deux si une plage est entre elles. Un bout sans plage à un quart de pas n'est pas compté.
- **Le critère** : un saut ne franchit qu'une feuille si au moins 50 de ses points sont comptés et qu'au moins les trois quarts d'entre
  eux ne franchissent qu'une feuille ; un saut sans surface, ou trop peu compté, ne tient pas.
- **La règle** : celle de `344`, sur les sauts jugés des graines 4 à 8 : le compte les sépare s'il tient au moins 75 % des sauts justes et
  au plus 25 % des faux ; il ne les sépare pas si l'écart entre les deux parts est sous 25 points ; il ne les sépare qu'en partie sinon.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, le compte des feuilles de `m7` dit tenir a des nj sauts justes et b des nf sauts faux**,
puis ce que dit la règle ; indécidable s'il y a moins de 5 sauts justes ou 5 sauts faux jugés.

## Rapporté à côté, qui ne décide rien

Le même compte chaîne par chaîne et sur les graines 1 à 3 ; la tenue pour d'autres parts d'une feuille (la moitié à neuf dixièmes) ; le
compte et le critère de `328` ensemble ; pour chaque saut faux, ses comptes de zéro, une, deux feuilles et plus.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut le compte sur PHerc0358 ; et, si `m7` manque une feuille entre deux surfaces, un saut
qui en franchit deux y est compté comme n'en franchissant qu'une.

Usage :
    uv run python src/nappe/les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.py --verifier
    uv run python src/nappe/les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.py \\
        --json docs/mesures/les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.json
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
import la_nappe_plate_est_elle_posee_dans_un_bloc_de_m7 as m326  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402

CE_QUE_344_A_PUBLIE = RACINE / "docs" / "mesures" / "le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.json"
LA_TOLERANCE_EN_PAS = 0.25
LA_PORTEE_EN_PAS = 3.25
LE_LATERAL_L2 = m321.LE_LATERAL / m321.LE_FACTEUR
LA_PART_DUNE_FEUILLE = 0.75
LE_MINIMUM_DE_MESURES = 50
LES_SEUILS_RAPPORTES = (0.5, 0.6, 0.7, 0.8, 0.9)


def le_compte(vu: np.ndarray, t: np.ndarray, d: float, tolerance: float) -> int | None:
    """Le nombre de plages passées le long d'un rayon, de celle qui porte t = 0 à celle qui porte t = d : 1 si elles se suivent, 0 si
    c'est la même ; None si l'un des deux bouts n'a pas de plage à `tolerance`."""
    if not vu.any():
        return None
    bords = np.flatnonzero(np.diff(np.concatenate([[0], vu.astype(np.int8), [0]])))
    plages = [(t[a], t[b - 1]) for a, b in zip(bords[::2], bords[1::2])]

    def laquelle(x):
        ecarts = [0.0 if lo <= x <= hi else min(abs(lo - x), abs(hi - x)) for lo, hi in plages]
        k = int(np.argmin(ecarts))
        return k if ecarts[k] <= tolerance else None

    i, j = laquelle(0.0), laquelle(d)
    return None if i is None or j is None else abs(j - i)


def les_feuilles_franchies(depart: dict, arrivee: dict | None, lire_valeurs, pas: float) -> dict:
    """Pour au plus `m326.LE_MAXIMUM_DE_POINTS` points posés de la surface d'arrivée, le nombre de feuilles de `m7` passées le long de sa
    normale jusqu'à la surface de départ ; et la part des points comptés qui n'en passent qu'une."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    vide = {"les_points": 0, "les_en_face": 0, "les_mesures": 0, "les_comptes": {}, "la_part_dune_feuille": None}
    if arrivee is None or not arrivee["valide"].any() or not depart["valide"].any():
        return vide
    nn, nok = les_normales(arrivee["la_nappe"], arrivee["valide"])
    m = arrivee["valide"] & nok
    q, nq = arrivee["la_nappe"][m], nn[m]
    if not len(q):
        return vide
    if len(q) > m326.LE_MAXIMUM_DE_POINTS:
        k = np.linspace(0, len(q) - 1, m326.LE_MAXIMUM_DE_POINTS).round().astype(int)
        q, nq = q[k], nq[k]
    d = m321.les_ecarts(q, nq, depart["la_nappe"][depart["valide"]], lateral=LE_LATERAL_L2)
    tol = LA_TOLERANCE_EN_PAS * pas
    demi = float(np.ceil(LA_PORTEE_EN_PAS * pas))
    t = np.arange(-demi, demi + 1.0)
    en_face = np.isfinite(d) & (np.abs(d) + tol <= demi)
    comptes = []
    if en_face.any():
        idx = np.floor((q[en_face][:, None, :] + t[None, :, None] * nq[en_face][:, None, :])[..., ::-1]).astype(np.int64)
        vu = lire_valeurs(idx) > 0
        for rayon, dd in zip(vu, d[en_face]):
            c = le_compte(rayon, t, float(dd), tol)
            if c is not None:
                comptes.append(c)
    n = Counter(comptes)
    return {"les_points": int(len(q)), "les_en_face": int(en_face.sum()), "les_mesures": len(comptes),
            "les_comptes": {str(k): v for k, v in sorted(n.items())},
            "la_part_dune_feuille": round(n[1] / len(comptes), 4) if comptes else None}


def tient(f: dict, part: float = LA_PART_DUNE_FEUILLE) -> bool:
    return bool(f["les_mesures"] >= LE_MINIMUM_DE_MESURES and f["la_part_dune_feuille"] is not None
                and f["la_part_dune_feuille"] >= part)


def recoder(s: dict, part: float = LA_PART_DUNE_FEUILLE) -> dict:
    """Un saut de `344`, où « tient » devient ce que dit le compte, et la tenue de `328` est gardée à côté."""
    r = {k: v for k, v in s.items() if k not in ("en_plus", "tient")}
    return {**r, "tient_328": s["tient"], "les_feuilles": s["en_plus"], "tient": tient(s["en_plus"], part)}


def les_chaines_recodees(chaines: dict, part: float = LA_PART_DUNE_FEUILLE, combine: bool = False) -> dict:
    """Les chaînes de `344`, chaque saut recodé ; avec `combine`, un saut ne tient que si le compte et `328` le tiennent tous deux."""
    def un(s):
        r = recoder(s, part)
        if combine:
            r["tient"] = bool(r["tient"] and r["tient_328"])
        return r
    return {n: {"redonne": c["redonne"],
                "les_graines": [{"le_rang": g["le_rang"],
                                 "les_cotes": {cote: {"les_sauts": [un(s) for s in x["les_sauts"]]} for cote, x in g["les_cotes"].items()}}
                                for g in c["les_graines"]]}
            for n, c in chaines.items()}


def sans_le_compte(chaines: dict) -> dict:
    return {n: {"redonne": c["redonne"],
                "les_graines": [{"le_rang": g["le_rang"],
                                 "les_cotes": {cote: {"les_sauts": [{k: v for k, v in s.items() if k != "en_plus"} for s in x["les_sauts"]]}
                                               for cote, x in g["les_cotes"].items()}} for g in c["les_graines"]]}
            for n, c in chaines.items()}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_344"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 344"}
    b = m344.le_bilan(m344.les_sauts_de(d, m344.LES_GRAINES_PROPRES))
    if b["les_justes"] < m344.LE_MINIMUM or b["les_faux"] < m344.LE_MINIMUM:
        return {"decidable": False, **b, "lissue": f"indécidable : {b['les_justes']} sauts justes et {b['les_faux']} sauts faux jugés"}
    tj, tf = b["tj"], b["tf"]
    tete = (f"sur les graines 4 à 8, le compte des feuilles de m7 dit tenir {b['les_justes_qui_tiennent']} des {b['les_justes']} sauts "
            f"justes et {b['les_faux_qui_tiennent']} des {b['les_faux']} sauts faux")
    if tj >= m344.LA_TENUE_DES_JUSTES and tf <= m344.LA_TENUE_DES_FAUX:
        suite, issue = "il les sépare", "sépare"
    elif tj - tf < m344.LECART_MINIMAL:
        suite, issue = "il ne les sépare pas", "ne sépare pas"
    else:
        suite, issue = "il ne les sépare qu'en partie", "en partie"
    return {"decidable": True, **b, "lissue_courte": issue, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    d344 = m344.mesurer(en_plus=lambda dep, arr, lv: les_feuilles_franchies(dep, arr, lv, m321.LE_PAS_L2))
    publie = json.loads(CE_QUE_344_A_PUBLIE.read_text())
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_tolerance_en_pas": LA_TOLERANCE_EN_PAS, "la_portee_en_pas": LA_PORTEE_EN_PAS,
                            "le_lateral_l2": LE_LATERAL_L2, "la_part_dune_feuille": LA_PART_DUNE_FEUILLE,
                            "le_minimum_de_mesures": LE_MINIMUM_DE_MESURES},
         "les_pannes": d344["les_pannes"], "la_lecture_de_m7": d344["la_lecture_de_m7"],
         "redonne_344": bool(json.loads(json.dumps(sans_le_compte(d344["les_chaines"]))) == publie["les_chaines"]
                             and d344["le_verdict"] == publie["le_verdict"] and d344["redonne_328"]),
         "les_chaines": les_chaines_recodees(d344["les_chaines"])}
    d["le_verdict"] = le_verdict(d)
    d["les_bilans"] = {
        "par_chaine": {n: m344.le_bilan(m344.les_sauts_de(d, m344.LES_GRAINES_PROPRES, (n,))) for n in d["les_chaines"]},
        "graines_1_a_3": m344.le_bilan(m344.les_sauts_de(d, (1, 2, 3))),
        "par_seuil": {str(p): m344.le_bilan(m344.les_sauts_de({"les_chaines": les_chaines_recodees(d344["les_chaines"], p)},
                                                              m344.LES_GRAINES_PROPRES)) for p in LES_SEUILS_RAPPORTES},
        "avec_328": m344.le_bilan(m344.les_sauts_de({"les_chaines": les_chaines_recodees(d344["les_chaines"], combine=True)},
                                                    m344.LES_GRAINES_PROPRES))}
    d["les_sauts_faux"] = [{"la_chaine": n, "le_rang": g["le_rang"], "le_cote": c, **s} for n, ch in d["les_chaines"].items()
                           for g in ch["les_graines"] for c, x in g["les_cotes"].items() for s in x["les_sauts"]
                           if s["la_justesse"].startswith("faux")]
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

    t = np.arange(-30.0, 31.0)
    rayon = lambda *zs: np.isin(t, zs)  # noqa: E731
    v("★★★★ deux plages qui se suivent : une feuille", le_compte(rayon(0, 20), t, 20.0, 5.0) == 1)
    v("★★★★ une plage entre les deux : deux feuilles", le_compte(rayon(0, 10, 20), t, 20.0, 5.0) == 2)
    v("★★★★ les deux bouts sur la même plage : zéro", le_compte(np.abs(t) <= 12, t, 10.0, 5.0) == 0)
    v("★★★ vers l'arrière aussi : une feuille", le_compte(rayon(0, -20), t, -20.0, 5.0) == 1)
    v("★★★ une plage à 4 voxels d'un bout le porte ; à 7, non",
      le_compte(rayon(0, 16), t, 20.0, 5.0) == 1 and le_compte(rayon(0, 13), t, 20.0, 5.0) is None)
    v("★★★ un rayon vide n'est pas compté", le_compte(np.zeros_like(t, dtype=bool), t, 20.0, 5.0) is None)

    def plan(z):
        g = np.zeros((11, 11, 3))
        for a in range(11):
            for b in range(11):
                g[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, z)
        return {"la_nappe": g, "valide": np.ones((11, 11), dtype=bool)}
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    f = les_feuilles_franchies(plan(100.0), plan(120.0), feuilles, 20.0)
    v("★★★★ d'une feuille à la suivante : les 81 points à normale connue, comptés, en franchissent une", f["les_mesures"] == 81
      and f["la_part_dune_feuille"] == 1.0 and tient(f), str(f))
    f = les_feuilles_franchies(plan(100.0), plan(140.0), feuilles, 20.0)
    v("★★★★ par-dessus une feuille : aucun point n'en franchit une seule, le saut ne tient pas",
      f["les_mesures"] == 81 and f["les_comptes"] == {"2": 81} and not tient(f), str(f))
    sans_120 = lambda idx: (idx[..., 0] == 100) | (idx[..., 0] == 140)  # noqa: E731
    f = les_feuilles_franchies(plan(100.0), plan(140.0), sans_120, 20.0)
    v("★★★ sans feuille entre les deux, `m7` voit une feuille franchie", f["la_part_dune_feuille"] == 1.0, str(f))
    f = les_feuilles_franchies(plan(120.0), plan(100.0), feuilles, 20.0)
    v("★★★ de l'autre côté, pareil", f["la_part_dune_feuille"] == 1.0, str(f))
    loin = plan(100.0)
    loin["la_nappe"] = loin["la_nappe"] + np.array([200.0, 0.0, 0.0])
    v("★★★★ une surface de départ qui n'est pas en face : rien n'est compté",
      les_feuilles_franchies(loin, plan(120.0), feuilles, 20.0)["les_mesures"] == 0)
    v("★★★ un saut sans surface : rien n'est compté", les_feuilles_franchies(plan(100.0), None, feuilles, 20.0)["les_mesures"] == 0)
    ff = lambda n, p: {"les_mesures": n, "la_part_dune_feuille": p}  # noqa: E731
    v("★★★★ le critère : au moins 50 points comptés et les trois quarts, bornes comprises",
      tient(ff(50, 0.75)) and not tient(ff(49, 1.0)) and not tient(ff(80, 0.74)) and not tient(ff(0, None)))
    s = {"le_saut": 1, "la_justesse": "juste", "tient": False, "en_plus": ff(60, 0.9)}
    r = recoder(s)
    v("★★★★ recodé, le saut tient par le compte, et garde la tenue de 328 à côté", r["tient"] and r["tient_328"] is False
      and "en_plus" not in r and r["les_feuilles"]["les_mesures"] == 60)

    def d_(sauts_propres, sauts_sales=(), **kw):
        g = lambda rg, xs: {"le_rang": rg, "les_cotes": {"moins": {"les_sauts": list(xs)}}}  # noqa: E731
        return dict({"les_pannes": [], "redonne_344": True,
                     "les_chaines": {"bornée": {"redonne": True, "les_graines": [g(4, sauts_propres), g(2, sauts_sales)]}}}, **kw)
    s_ = lambda j, t_: {"la_justesse": j, "tient": t_}  # noqa: E731
    j9, f5 = [s_("juste", True)] * 9 + [s_("juste", False)], [s_("faux : deux tours", False)] * 4 + [s_("faux : un autre tour", True)]
    v("★★★★ 9 justes sur 10 tenus et 1 faux sur 5 : il les sépare", le_verdict(d_(j9 + f5)).get("lissue_courte") == "sépare")
    v("★★★★ 4 faux sur 5 tenus : il ne les sépare pas",
      le_verdict(d_(j9 + [s_("faux : deux tours", True)] * 4 + [s_("faux : deux tours", False)])).get("lissue_courte") == "ne sépare pas")
    v("★★★★ des chaînes qui ne redonnent pas 344 : indécidable", not le_verdict(d_(j9 + f5, redonne_344=False))["decidable"])
    v("★★★ les graines 1 à 3 ne comptent pas", not le_verdict(d_(j9 + f5[:4], [s_("faux : deux tours", False)] * 5))["decidable"])
    ch = {"bornée": {"redonne": True, "les_graines": [{"le_rang": 4, "les_cotes": {"moins": {"les_sauts": [
        {"la_justesse": "juste", "tient": True, "en_plus": ff(60, 0.8)}, {"la_justesse": "juste", "tient": False, "en_plus": ff(60, 0.8)},
        {"la_justesse": "juste", "tient": True, "en_plus": ff(60, 0.6)}]}}}]}}
    v("★★★ avec 328, un saut ne tient que si les deux le tiennent ; le seuil rapporté change la tenue",
      [s["tient"] for s in les_chaines_recodees(ch, combine=True)["bornée"]["les_graines"][0]["les_cotes"]["moins"]["les_sauts"]]
      == [True, False, False]
      and [s["tient"] for s in les_chaines_recodees(ch, 0.5)["bornée"]["les_graines"][0]["les_cotes"]["moins"]["les_sauts"]]
      == [True, True, True])

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
