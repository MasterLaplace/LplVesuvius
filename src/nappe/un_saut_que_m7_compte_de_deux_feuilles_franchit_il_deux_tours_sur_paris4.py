"""Sur PHercParis4, les sauts que m7 compte de deux feuilles, rognés ou non, franchissent-ils deux tours publiés ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES TOURS DES SURFACES ROGNÉES NE SOIENT LUS SUR LES SEIZE CÔTÉS. Ce qui était vu avant d'écrire : tout ce
que `296` à `402` publient, dont **`R4-F580`** (`394` : sur les côtés moins, 88 sauts de `385` sont jugés, 87 franchissent une feuille et un
tour, et le seul autre est le sixième saut de la suivie de la graine 7, que `m7` compte de 2 feuilles quand les tours en disent 3),
**`R4-F587`** (`401` : rognée, cette suivie descend d'un tour à chaque saut) et **`R4-F588`** (`402` : sur PHerc0358, les chaînes rognées
font plus de sauts de plusieurs feuilles). En préparant la tranche, une seule ligne de plus : les comptes de `400` et les tours de `379` du
côté de la graine 5, moins, où le huitième saut rogné de la suivie compte 2 feuilles et sa surface non rognée ne retrouve aucun tour. ⚠ La
famille de `385` est donc déjà connue : un seul de ses sauts jugés compte plusieurs feuilles, et il est faux. Ce que la tranche ajoute, ce
sont les chaînes rognées.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P200`. Sur PHerc0358, le rognage ajoute des sauts de plusieurs feuilles. Là où il n'y a pas de
tours, on ne sait pas si la chaîne rognée saute une feuille ou si `m7` compte de travers ; PHercParis4 a des tours.

## Ce qui est fait

- **Deux familles de chaînes**, sur les seize côtés de PHercParis4 : celles de `385`, dont les tours sont ceux que `379` publie et les
  comptes ceux que `385` publie ; et les chaînes rognées de `400`, relancées, dont chaque surface est lue contre les tours publiés et chaque
  saut compté par `m7` comme `385` le compte.
- **Un saut jugé**, comme `401` le juge : ses deux surfaces (la nappe pour le premier) retrouvent chacune un seul tour ; les tours qu'il
  franchit sont leur écart, dans le sens du côté ; il est **juste** si `m7` y dit autant de feuilles.
- **Les sauts de plusieurs feuilles** : les sauts jugés où `m7` dit au moins 2 feuilles. Un saut des chaînes rognées que rien ne distingue
  d'un saut de `385` (même côté, même chaîne, même rang, mêmes comptes point par point) n'est compté qu'une fois.
- **Le contrôle** : les chaînes rognées relancées redonnent, côté par côté, les statuts de `400`.
- **La règle** : si tous les sauts de plusieurs feuilles franchissent autant de tours, **oui** ; si moins de la moitié, **non** ; sinon,
  **en partie**. Indécidable sous 5 sauts de plusieurs feuilles, si une lecture échoue, ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **j des n sauts jugés que `m7` compte de plusieurs feuilles franchissent autant de tours publiés (deux feuilles :
j2 sur n2)**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Pour chaque famille, les sauts jugés rangés par feuilles de `m7` et par tours franchis ; et à l'envers, les sauts jugés qui franchissent au
moins deux tours, avec ce que `m7` en dit.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut un saut de plusieurs feuilles sur PHerc0358, qui n'a pas de tours.

Usage :
    uv run python src/nappe/un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.py --verifier
    uv run python src/nappe/un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.py \\
        --json docs/mesures/un_saut_que_m7_compte_de_deux_feuilles_franchit_il_deux_tours_sur_paris4.json
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
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4 as m385  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402
import des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4 as m400  # noqa: E402
import quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4 as m401  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
CE_QUE_385_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"
CE_QUE_400_A_PUBLIE = LES_MESURES / "des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LES_FAMILLES = ("385", "rognees")
LE_MINIMUM = 5
PLUSIEURS = 2


def la_cle(rang: int, cote: str, chaine: str, saut: dict) -> tuple:
    """Ce qui fait qu'un saut rogné est le même qu'un saut de `385` : même côté, même chaîne, même rang, mêmes comptes point par point."""
    return rang, cote, chaine, saut["le_saut"], json.dumps({str(k): v for k, v in saut["les_comptes"].items()}, sort_keys=True)


def les_plusieurs(cotes: list[dict]) -> list[dict]:
    """Les sauts jugés que `m7` compte d'au moins deux feuilles, chacun une fois, avec les familles où il apparaît."""
    vus: dict[tuple, dict] = {}
    for c in cotes:
        for f in LES_FAMILLES:
            for x in LES_CHAINES:
                for s in c[f][x]["les_sauts"]:
                    n = s["le_nombre_de_feuilles"]
                    if s["dit"] is None or n is None or n < PLUSIEURS:
                        continue
                    cle = la_cle(c["le_rang"], c["le_cote"], x, s)
                    if cle not in vus:
                        vus[cle] = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_chaine": x, "le_saut": s["le_saut"],
                                    "le_nombre_de_feuilles": n, "les_tours": s["les_tours"], "dit": s["dit"],
                                    "la_part_majoritaire": s["la_part_majoritaire"], "a_cheval": s["a_cheval"], "les_familles": []}
                    vus[cle]["les_familles"].append(f)
    return list(vus.values())


def le_tableau(cotes: list[dict], famille: str) -> dict[str, int]:
    """Les sauts jugés d'une famille, rangés par « feuilles de `m7` | tours franchis »."""
    out: dict[str, int] = {}
    for c in cotes:
        for x in LES_CHAINES:
            for s in c[famille][x]["les_sauts"]:
                if s["dit"] is not None:
                    k = f"{s['le_nombre_de_feuilles']}|{s['les_tours']}"
                    out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_400"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rognées ne redonnent pas 400"}
    p = d["les_sauts_de_plusieurs_feuilles"]
    justes = sum(x["dit"] == "juste" for x in p)
    deux = [x for x in p if x["le_nombre_de_feuilles"] == PLUSIEURS]
    tete = (f"{justes} des {len(p)} sauts jugés que m7 compte de plusieurs feuilles franchissent autant de tours publiés (deux feuilles : "
            f"{sum(x['dit'] == 'juste' for x in deux)} sur {len(deux)})")
    if len(p) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"{tete} ; indécidable, moins de {LE_MINIMUM}"}
    suite = "oui" if justes == len(p) else "non" if justes < len(p) / 2 else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m379._LES_TROIS.clear()
    m397._LES_ROGNAGES.clear()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=m379.le_chaineur(enchainer=m400.enchainer4))
    d379, d385, d400 = (json.loads(x.read_text()) for x in (CE_QUE_379_A_PUBLIE, CE_QUE_385_A_PUBLIE, CE_QUE_400_A_PUBLIE))
    cotes_d331 = [(g["le_rang"], cote) for g in d331["les_graines"]["PHercParis4"] for cote in g["les_cotes"]]
    redonne = len(cotes_d331) == len(m379._LES_TROIS) == len(d379["les_cotes"]) == len(d385["les_cotes"]) == len(d400["les_cotes"])
    cotes = []
    for (rang, cote), trois, c379, c385, c400 in zip(cotes_d331, m379._LES_TROIS, d379["les_cotes"], d385["les_cotes"], d400["les_cotes"]):
        redonne &= all((c["le_rang"], c["le_cote"]) == (rang, cote) for c in (c379, c385, c400))
        sens = m344.LE_SENS[cote]
        rognees = {x: trois["les_relances"][x] for x in LES_CHAINES}
        pts = {x: [m367.les_points(s) for s in rognees[x]] for x in LES_CHAINES}
        nap = {x: m367.les_points(trois["les_nappes"][x]) for x in LES_CHAINES}
        retrouves = {x: [m379.les_retrouves(trois["les_nappes"][x], tours)] + [m379.les_retrouves(s, tours) for s in rognees[x]]
                     for x in LES_CHAINES}
        nombres = {x: m385.les_nombres(trois["les_nappes"][x], rognees[x], lv["m7"]) for x in LES_CHAINES}
        corriges = {x: m379.les_comptes(nap[x], pts[x]) for x in LES_CHAINES}
        m7 = {x: m385.les_comptes_de_m7(corriges[x], [n["le_nombre_de_feuilles"] for n in nombres[x]]) for x in LES_CHAINES}
        paires = {f"{a}|{b}": m379.les_paires(pts[a], pts[b]) for a, b in m379.LES_COUPLES}
        surfaces = m379.le_cote(paires, m7, {x: m379.la_verite(retrouves[x], m7[x], sens) for x in LES_CHAINES})
        redonne &= ([[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"], s["lue"], s["sur_le_bon_tour"]] for s in surfaces]
                    == c400["rognees"]["les_surfaces"])
        cote_out = {"le_rang": rang, "le_cote": cote,
                    "385": {x: {"les_tours": c379["les_retrouves"][x],
                                "les_sauts": m401.les_sauts_juges(c379["les_retrouves"][x], c385["les_sauts"][x], sens)} for x in LES_CHAINES},
                    "rognees": {x: {"les_tours": retrouves[x], "les_sauts": m401.les_sauts_juges(retrouves[x], nombres[x], sens)}
                                for x in LES_CHAINES}}
        cotes.append(cote_out)
        print(json.dumps({"le_rang": rang, "le_cote": cote, "redonne_400": bool(redonne),
                          "plusieurs": len(les_plusieurs([cote_out]))}, ensure_ascii=False), flush=True)
    p = les_plusieurs(cotes)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_minimum": LE_MINIMUM, "plusieurs": PLUSIEURS},
         "les_pannes": list(d331["les_pannes"]), "la_lecture_de_m7": d331["la_lecture_de_m7"], "redonne_400": bool(redonne),
         "les_cotes": cotes, "les_sauts_de_plusieurs_feuilles": p,
         "les_tableaux": {f: le_tableau(cotes, f) for f in LES_FAMILLES}}
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

    s_ = lambda n, c: {"le_nombre_de_feuilles": n, "les_comptes": c}  # noqa: E731
    vides = {x: {"les_tours": [], "les_sauts": []} for x in LES_CHAINES}

    def cote_(rang, cote, suivie_385, suivie_rognee):
        return {"le_rang": rang, "le_cote": cote,
                "385": {**vides, "suivie": {"les_tours": suivie_385[0], "les_sauts": m401.les_sauts_juges(*suivie_385, -1)}},
                "rognees": {**vides, "suivie": {"les_tours": suivie_rognee[0], "les_sauts": m401.les_sauts_juges(*suivie_rognee, -1)}}}

    a = cote_(7, "moins", ([[0], [-1], [-4]], [s_(1, {"1": 9}), s_(2, {"2": 105, "3": 60})]),
              ([[0], [-1], [-3], []], [s_(1, {"1": 9}), s_(2, {"2": 40}), s_(2, {"2": 30})]))
    p = les_plusieurs([a])
    v("★★★★ un saut de plusieurs feuilles est jugé, compté une fois par famille où il diffère, et pas s'il n'est pas jugé",
      [(x["le_saut"], x["les_tours"], x["dit"], x["les_familles"]) for x in p] == [(2, 3, "pas_assez", ["385"]), (2, 2, "juste", ["rognees"])],
      str([(x["le_saut"], x["les_tours"], x["dit"], x["les_familles"]) for x in p]))
    b = cote_(5, "moins", ([[0], [-2]], [s_(2, {"2": 50})]), ([[0], [-2]], [s_(2, {"2": 50})]))
    v("★★★★ un saut rogné que rien ne distingue de celui de 385 n'est compté qu'une fois",
      [x["les_familles"] for x in les_plusieurs([b])] == [["385", "rognees"]])
    c = cote_(4, "moins", ([[0], [-1]], [s_(1, {"1": 50})]), ([[0], [0]], [s_(0, {"0": 50})]))
    v("★★★ un saut d'une feuille ou nul n'est pas de plusieurs feuilles", les_plusieurs([c]) == [])
    v("★★★ le tableau range les sauts jugés par feuilles et par tours",
      le_tableau([a, b, c], "385") == {"1|1": 2, "2|2": 1, "2|3": 1} and le_tableau([a], "rognees") == {"1|1": 1, "2|2": 1},
      str(le_tableau([a, b, c], "385")))

    def d_(dits, ok=True, n=2):
        return {"redonne_400": ok, "les_pannes": [], "les_sauts_de_plusieurs_feuilles":
                [{"le_nombre_de_feuilles": n, "dit": x} for x in dits]}
    v("★★★★ la règle : tous justes, oui ; moins de la moitié, non ; sinon, en partie",
      le_verdict(d_(["juste"] * 5))["lissue"].endswith("; oui")
      and le_verdict(d_(["juste"] * 2 + ["pas_assez"] * 3))["lissue"].endswith("; non")
      and le_verdict(d_(["juste"] * 3 + ["de_trop"] * 3))["lissue"].endswith("; en partie"))
    v("★★★★ l'issue dit les justes, et ceux de deux feuilles à part",
      le_verdict(d_(["juste"] * 4 + ["de_trop"]))["lissue"]
      == "4 des 5 sauts jugés que m7 compte de plusieurs feuilles franchissent autant de tours publiés (deux feuilles : 4 sur 5) ; en partie")
    v("★★★★ indécidable sous 5 sauts, sans redonne, ou sur une panne",
      not le_verdict(d_(["juste"] * 4))["decidable"] and not le_verdict(d_(["juste"] * 5, ok=False))["decidable"]
      and not le_verdict({**d_(["juste"] * 5), "les_pannes": ["x"]})["decidable"])

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
