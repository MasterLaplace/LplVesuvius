"""Sur PHercParis4, où les tours publiés disent de combien de tours deux surfaces justes d'une même chaîne sont l'une de l'autre, l'écart que `369` mesure à un saut sépare-t-il deux surfaces à un tour de deux surfaces à deux tours, et à quel seuil ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE DEUX SURFACES D'UNE MÊME CHAÎNE NE SOIENT COMPARÉES. Ce qui était vu avant d'écrire : tout ce que
`296` à `369` publient, dont `R4-F555` (sur PHerc0358, un saut nul se voit dans la chaîne seule, mais les sauts simples s'écartent de
15,667 voxels en médiane, moins d'un pas, et un saut qui franchit deux feuilles minces peut rester sous le seuil d'un pas et demi) et
`R4-F553` (sur PHercParis4, deux surfaces sur le même tour sont à 0,244 à 0,317 voxel l'une de l'autre, deux sur des tours voisins à 9,551
à 14,201). ⚠ Sous ses sauts jugés des graines 4 à 8, côtés moins, la chaîne d'une maille ne fait sur PHercParis4 qu'un saut faux
(`R4-F551`) : il n'y a pas assez de sauts doubles pour étalonner. Deux surfaces justes d'une même chaîne, à deux tours l'une de l'autre,
sont ce qu'un saut double aurait à franchir.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P167`. Le seuil d'un pas et demi de `369` a été posé sans étalon ; là où le tour est
connu, l'écart entre deux surfaces à un tour et à deux tours dit à quel seuil une chaîne seule peut voir un saut double.

## Ce qui est fait

- **Les chaînes** : la chaîne d'une maille de `365` sur PHercParis4, rejouée comme `367` la rejoue, qui garde la surface de chaque saut ;
  ses surfaces justes, avec leur tour publié, doivent redonner celles que `367` publie.
- **Les paires** : deux surfaces justes d'une même chaîne, graines 4 à 8, côtés moins, à un, deux ou trois tours publiés l'une de l'autre.
  **L'écart** est celui de `369`, la plus lointaine rapportée à la plus proche : la médiane des écarts absolus de ses points qui ont
  l'autre en face, à la portée latérale de `345` et à trois pas au plus ; une paire compte si au moins 50 points sont en face.
- **Rapporté à la chaîne** : l'écart d'une paire divisé par la médiane des écarts à un tour de la même chaîne.
- **La règle** : si le plus grand écart à un tour est sous le plus petit écart à deux tours, **oui, l'écart sépare**, au seuil de leur
  milieu ; sinon, si rapportés à leur chaîne ils se séparent, **oui, rapporté à la chaîne**, au seuil de leur milieu ; sinon, **non**.
  Indécidable sous 10 paires à un tour ou à deux tours.

## Les issues

L'issue de la tranche : **à un tour, n paires, de a à b voxels ; à deux tours, n' paires, de a' à b'**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les paires à trois tours ; les sauts faux de la chaîne, leur écart à la surface d'où ils partent et le nombre de tours qu'ils franchissent ;
ce que les seuils de `369`, un quart de pas et un pas et demi, font des paires à un et à deux tours.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un vrai saut double garde la surface qu'une chaîne juste garde deux tours plus loin ; ni ce que le
seuil vaut sur PHerc0358.

Usage :
    uv run python src/nappe/lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.py --verifier
    uv run python src/nappe/lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.py \\
        --json docs/mesures/lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from itertools import combinations
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_dune_seule_maille_evite_il_le_decalage as m365  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_367_A_PUBLIE = LES_MESURES / "deux_chaines_qui_se_croisent_disent_elles_le_tour.json"
LE_PAS = m321.LE_PAS_L2
LA_PORTEE = 3.0 * LE_PAS
LE_LATERAL = m345.LE_LATERAL_L2
LE_MINIMUM_EN_FACE = 50
LE_MINIMUM = 10
LES_TOURS = (1, 2, 3)


def lecart(a, b) -> dict:
    """L'écart de `369` de la surface `a` à la surface `b`, à la portée latérale de `345` et à trois pas de PHercParis4."""
    return m369.lecart_du_saut(a, b, lateral=LE_LATERAL, portee=LA_PORTEE)


def les_paires(surfaces: list[dict], points: dict, comparer=lecart) -> list[dict]:
    """Deux surfaces justes d'une même chaîne à un, deux ou trois tours ; la plus lointaine, au saut le plus grand, rapportée à l'autre."""
    out = []
    for x, y in combinations(surfaces, 2):
        tours = abs(x["le_tour"] - y["le_tour"])
        if x["le_rang"] != y["le_rang"] or tours not in LES_TOURS:
            continue
        loin, pres = (x, y) if x["le_saut"] > y["le_saut"] else (y, x)
        c = comparer(points[(loin["le_rang"], "moins", loin["le_saut"])], points[(pres["le_rang"], "moins", pres["le_saut"])])
        if c["en_face"] < LE_MINIMUM_EN_FACE or c["lecart_median"] is None:
            continue
        out.append({"le_rang": loin["le_rang"], "la_plus_lointaine": loin["le_saut"], "la_plus_proche": pres["le_saut"],
                    "les_tours": tours, **c})
    return out


def rapporter(paires: list[dict]) -> list[dict]:
    """Chaque paire, avec son écart divisé par la médiane des écarts à un tour de sa chaîne ; sans paire à un tour, rien."""
    un = {}
    for p in paires:
        if p["les_tours"] == 1:
            un.setdefault(p["le_rang"], []).append(p["lecart_median"])
    return [{**p, "rapporte": (round(p["lecart_median"] / statistics.median(un[p["le_rang"]]), 4) if p["le_rang"] in un else None)}
            for p in paires]


def les_sauts_faux(cotes: list[dict], points: dict, comparer=lecart) -> list[dict]:
    """Les sauts faux des côtés moins des graines 4 à 8 : leur écart à la surface gardée du saut précédent, et les tours qu'ils franchissent,
    lus au tour de départ du saut suivant."""
    out = []
    for c in cotes:
        if c["le_rang"] not in m344.LES_GRAINES_PROPRES or c["le_cote"] != "moins":
            continue
        sauts = c["les_sauts"]
        for i, s in enumerate(sauts):
            if not s["la_justesse"].startswith("faux"):
                continue
            suivant = sauts[i + 1]["le_tour_de_depart"] if i + 1 < len(sauts) else None
            franchis = (abs(suivant - s["le_tour_de_depart"]) if suivant is not None and s["le_tour_de_depart"] is not None else None)
            k, kd = (c["le_rang"], "moins", s["le_saut"]), (c["le_rang"], "moins", s["le_saut"] - 1)
            e = comparer(points[k], points[kd]) if k in points and kd in points else {"en_face": 0, "lecart_median": None}
            out.append({"le_rang": c["le_rang"], "le_saut": s["le_saut"], "la_justesse": s["la_justesse"], "les_tours": franchis, **e})
    return out


def le_bilan(paires: list[dict]) -> dict:
    par = {}
    for t in LES_TOURS:
        e = [p["lecart_median"] for p in paires if p["les_tours"] == t]
        r = [p["rapporte"] for p in paires if p["les_tours"] == t and p["rapporte"] is not None]
        par[str(t)] = {"les_paires": len(e), "le_plus_petit": min(e) if e else None, "le_plus_grand": max(e) if e else None,
                       "la_mediane": round(statistics.median(e), 3) if e else None,
                       "rapporte_plus_petit": min(r) if r else None, "rapporte_plus_grand": max(r) if r else None}
    u, d = par["1"], par["2"]
    b = {"par_tours": par, "separe": False, "le_seuil": None, "separe_rapporte": False, "le_seuil_rapporte": None}
    if u["les_paires"] and d["les_paires"]:
        b["separe"] = u["le_plus_grand"] < d["le_plus_petit"]
        b["le_seuil"] = round((u["le_plus_grand"] + d["le_plus_petit"]) / 2, 3)
    if u["rapporte_plus_grand"] is not None and d["rapporte_plus_petit"] is not None:
        b["separe_rapporte"] = u["rapporte_plus_grand"] < d["rapporte_plus_petit"]
        b["le_seuil_rapporte"] = round((u["rapporte_plus_grand"] + d["rapporte_plus_petit"]) / 2, 4)
    return b


def les_seuils_de_369(paires: list[dict]) -> dict:
    """Rapporté, ne décide rien : les paires à un tour que les seuils de `369` diraient nulles ou doubles, et celles à deux tours qu'ils ne
    diraient pas doubles."""
    quart, double = LE_PAS / 4.0, 1.5 * LE_PAS
    un = [p["lecart_median"] for p in paires if p["les_tours"] == 1]
    deux = [p["lecart_median"] for p in paires if p["les_tours"] == 2]
    return {"le_quart": round(quart, 3), "le_double": round(double, 3), "un_tour_dits_nuls": sum(e <= quart for e in un),
            "un_tour_dits_doubles": sum(e > double for e in un), "deux_tours_pas_dits_doubles": sum(e <= double for e in deux)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_367"):
        return {"decidable": False, "lissue": "indécidable : les surfaces justes ne sont pas celles que 367 publie"}
    b = d["le_bilan"]
    u, t = b["par_tours"]["1"], b["par_tours"]["2"]
    if u["les_paires"] < LE_MINIMUM or t["les_paires"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {u['les_paires']} paires à un tour et {t['les_paires']} à deux tours"}
    virg = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = (f"à un tour, {u['les_paires']} paires, de {virg(u['le_plus_petit'])} à {virg(u['le_plus_grand'])} voxels ; à deux tours, "
            f"{t['les_paires']} paires, de {virg(t['le_plus_petit'])} à {virg(t['le_plus_grand'])}")
    if b["separe"]:
        suite = f"oui, l'écart sépare, au seuil de {virg(b['le_seuil'])} voxels, {virg(round(b['le_seuil'] / LE_PAS, 3))} pas"
    elif b["separe_rapporte"]:
        suite = f"oui, rapporté à la chaîne, au seuil de {virg(b['le_seuil_rapporte'])} fois la médiane de ses écarts à un tour"
    else:
        suite = "non"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m367._LES_SURFACES.clear()
    r = m357.la_chaine_jugee(chainer=m365.la_chaine_dune_maille, en_plus=m367.garder)
    surfaces = m367.les_surfaces_justes(r["les_cotes"])
    publie = json.loads(CE_QUE_367_A_PUBLIE.read_text())
    paires = rapporter(les_paires(surfaces, m367._LES_SURFACES))
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas": round(LE_PAS, 3), "la_portee": round(LA_PORTEE, 3), "le_lateral": LE_LATERAL,
                            "le_minimum_en_face": LE_MINIMUM_EN_FACE, "le_minimum": LE_MINIMUM},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": r["le_controle"],
         "redonne_367": bool(r["le_controle"]) and surfaces == publie["les_surfaces"], "les_surfaces": surfaces, "les_paires": paires,
         "les_sauts_faux": les_sauts_faux(r["les_cotes"], m367._LES_SURFACES)}
    d["le_bilan"] = le_bilan(paires)
    d["les_seuils_de_369"] = les_seuils_de_369(paires)
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

    g = np.stack(np.meshgrid(np.arange(0.0, 40.0, 2.0), np.arange(0.0, 40.0, 2.0)), -1).reshape(-1, 2)
    plan = lambda z: (np.c_[g, np.full(len(g), z)], np.tile([0.0, 0.0, 1.0], (len(g), 1)))  # noqa: E731
    v("★★★★ l'écart de 369 à trois pas de PHercParis4 : un plan à 40 voxels est en face, à 60 il ne l'est plus",
      lambda: lecart(plan(40.0), plan(0.0)) == {"en_face": 400, "lecart_median": 40.0}
      and lecart(plan(60.0), plan(0.0))["en_face"] == 0, str(lecart(plan(40.0), plan(0.0))))
    s_ = lambda r, h, t: {"le_rang": r, "le_saut": h, "le_tour": t}  # noqa: E731
    surfaces = [s_(4, 2, -1), s_(4, 3, -2), s_(4, 4, -3), s_(4, 5, -4), s_(4, 6, -5), s_(5, 2, -1)]
    vus = []

    def comparer(a, b):
        vus.append((a, b))
        return {"en_face": 49 if (a, b) == ("4-5", "4-2") else 60, "lecart_median": 12.0}
    pts = {(r, "moins", h): f"{r}-{h}" for r, h in ((4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, 2))}
    p = les_paires(surfaces, pts, comparer)
    v("★★★★ les paires : une même chaîne, un à trois tours, la plus lointaine rapportée à la plus proche, 50 points en face",
      sorted((q["la_plus_lointaine"], q["la_plus_proche"], q["les_tours"]) for q in p)
      == [(3, 2, 1), (4, 2, 2), (4, 3, 1), (5, 3, 2), (5, 4, 1), (6, 3, 3), (6, 4, 2), (6, 5, 1)]
      and all(a > b for a, b in vus), str(sorted(vus)))
    q_ = lambda r, t, e: {"le_rang": r, "les_tours": t, "lecart_median": e}  # noqa: E731
    rr = rapporter([q_(4, 1, 10.0), q_(4, 1, 14.0), q_(4, 1, 15.0), q_(4, 2, 28.0), q_(5, 2, 20.0)])
    v("★★★★ rapporté à la chaîne : divisé par la médiane de ses écarts à un tour, rien sans elle",
      [x["rapporte"] for x in rr] == [0.7143, 1.0, 1.0714, 2.0, None], str([x["rapporte"] for x in rr]))

    def paires_(un, deux, trois=()):
        return ([{**q_(4, 1, e), "rapporte": r} for e, r in un] + [{**q_(4, 2, e), "rapporte": r} for e, r in deux]
                + [{**q_(4, 3, e), "rapporte": r} for e, r in trois])
    b = le_bilan(paires_([(10.0, 0.8), (14.0, 1.2)], [(18.0, 1.5), (26.0, 2.2)], [(36.0, 3.0)]))
    v("★★★★ le bilan : séparés si le plus grand à un tour est sous le plus petit à deux tours, au seuil du milieu",
      b["separe"] and b["le_seuil"] == 16.0 and b["separe_rapporte"] and b["le_seuil_rapporte"] == 1.35
      and b["par_tours"]["3"]["les_paires"] == 1 and b["par_tours"]["1"]["la_mediane"] == 12.0, str(b))
    b2 = le_bilan(paires_([(10.0, 0.8), (19.0, 1.2)], [(18.0, 1.5), (26.0, 2.2)]))
    b3 = le_bilan(paires_([(10.0, 0.8), (18.0, 1.5)], [(18.0, 1.5), (26.0, 2.2)]))
    v("★★★★ un recouvrement ou une égalité ne sépare pas", not b2["separe"] and b2["separe_rapporte"] and not b3["separe"]
      and not b3["separe_rapporte"], str((b2, b3)))

    def d_(b_, ok=True):
        return {"les_pannes": [], "redonne_367": ok, "le_bilan": b_}
    dix = lambda un, deux, trois=(): le_bilan(paires_(un * 10, deux * 10, trois))  # noqa: E731
    v("★★★★ la règle : l'écart d'abord, rapporté ensuite, sinon non",
      le_verdict(d_(dix([(10.0, 0.8)], [(18.0, 1.5)])))["lissue"].endswith("oui, l'écart sépare, au seuil de 14 voxels, 0,777 pas")
      and le_verdict(d_(dix([(10.0, 0.8), (19.0, 1.2)], [(18.0, 1.5)])))["lissue"].endswith("au seuil de 1,35 fois la médiane de ses "
                                                                                           "écarts à un tour")
      and le_verdict(d_(dix([(19.0, 1.5)], [(18.0, 1.5)])))["lissue"].endswith("; non"))
    v("★★★ indécidable sous dix paires à un tour ou à deux, ou sans les surfaces de 367",
      not le_verdict(d_(le_bilan(paires_([(10.0, 0.8)] * 9, [(18.0, 1.5)] * 10))))["decidable"]
      and not le_verdict(d_(le_bilan(paires_([(10.0, 0.8)] * 10, [(18.0, 1.5)] * 9))))["decidable"]
      and not le_verdict(d_(dix([(10.0, 0.8)], [(18.0, 1.5)]), ok=False))["decidable"])
    cotes = [{"le_rang": 7, "le_cote": "moins", "les_sauts": [
        {"le_saut": 5, "la_justesse": "juste", "le_tour_de_depart": -2}, {"le_saut": 6, "la_justesse": "faux : un autre tour",
                                                                          "le_tour_de_depart": -3},
        {"le_saut": 7, "la_justesse": "non jugé", "le_tour_de_depart": -6}]},
        {"le_rang": 2, "le_cote": "moins", "les_sauts": [{"le_saut": 2, "la_justesse": "faux : deux tours", "le_tour_de_depart": 0}]}]
    lus = []
    f = les_sauts_faux(cotes, {(7, "moins", 6): "a", (7, "moins", 5): "b"},
                       lambda a, b_: lus.append((a, b_)) or {"en_face": 80, "lecart_median": 33.0})
    v("★★★★ un saut faux : graines 4 à 8, son écart à la surface du saut précédent, les tours lus au départ du suivant",
      f == [{"le_rang": 7, "le_saut": 6, "la_justesse": "faux : un autre tour", "les_tours": 3, "en_face": 80, "lecart_median": 33.0}]
      and lus == [("a", "b")], str(f))
    s3 = les_seuils_de_369(paires_([(4.0, 0.3), (12.0, 1.0), (28.0, 2.0)], [(20.0, 1.7), (30.0, 2.5)]))
    v("★★★ les seuils de 369 sur PHercParis4 : un quart de pas et un pas et demi",
      s3 == {"le_quart": 4.505, "le_double": 27.031, "un_tour_dits_nuls": 1, "un_tour_dits_doubles": 1, "deux_tours_pas_dits_doubles": 1},
      str(s3))
    s4 = les_seuils_de_369(paires_([(LE_PAS / 4.0, 0.3), (1.5 * LE_PAS, 2.0)], [(1.5 * LE_PAS, 2.5)]))
    v("★★★ aux bornes : nul au quart de pas compris, double au-delà d'un pas et demi seulement",
      (s4["un_tour_dits_nuls"], s4["un_tour_dits_doubles"], s4["deux_tours_pas_dits_doubles"]) == (1, 0, 1), str(s4))

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
