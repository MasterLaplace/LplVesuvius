"""Là où deux chaînes ne posent pas leur première surface sur la même feuille, aligner leurs comptes sur leur première paire même feuille fait-il valider des surfaces sur le bon tour de PHercParis4, et que donne-t-il sur la graine 8 de PHerc0358 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL COMPTE NE SOIT ALIGNÉ. Ce qui était vu avant d'écrire : tout ce que `296` à `386` publient, dont
`R4-F572` (sur la graine 8 de PHerc0358, les contradictions naissent au premier saut, et côté moins les trois chaînes suivent les mêmes
feuilles à des écarts de comptes constants qui s'accordent) et `R4-F571` (sur PHercParis4, aux comptes de `m7`, l'accord valide 160
surfaces, et les 58 lues sont sur le bon tour). ⚠ Cette tranche ne lit pas `m7` : elle relit les paires et les tours retrouvés que `379` et
`380` publient, et les comptes de `m7` de `384` et `385`.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P184`. Compter chaque chaîne depuis sa propre nappe suppose que les trois partent de la même
feuille. Là où ce n'est pas le cas, une paire même feuille dit de combien leurs comptes diffèrent, et l'accord peut alors juger des chaînes
qui suivent les mêmes feuilles sans partir du même endroit.

## Ce qui est fait

- **Les comptes** : ceux de `m7`, de `385` sur PHercParis4 et de `384` sur PHerc0358.
- **L'alignement** : sur chaque côté, la suivie sert de référence. Pour la compagne et pour la tierce, la première paire même feuille avec la
  suivie, dans l'ordre du plus petit des deux sauts puis du plus grand, donne l'écart ; ses comptes en sont décalés. Sans paire même feuille,
  rien n'est décalé.
- **L'accord** : celui de `374`, sur les comptes alignés.
- **La vérité, absolue** : sur un côté où une chaîne retrouve un seul tour publié, sa première telle lecture fixe le tour du compte zéro dans
  le repère de la suivie ; toute autre surface qui retrouve un seul tour est lue, et sur le bon tour si ce tour est celui du compte zéro
  décalé de son compte, dans le sens du côté. Contrairement à la vérité de `379`, elle juge les trois chaînes dans un seul repère, donc un alignement faux s'y voit.
- **La règle**, sur PHercParis4 : sur les comptes alignés, au moins 90 % des surfaces validées lues sur le bon tour, et au moins autant de
  surfaces sur le bon tour que sans alignement, **oui** ; au moins 90 % mais moins, **en partie** ; sous 75 %, **non** ; sinon, **en
  partie**. Indécidable sous 10 surfaces validées lues.

## Les issues

L'issue de la tranche : **alignés, a des n surfaces validées lues sont sur le bon tour de PHercParis4, contre a' des n' sans alignement**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté, l'écart de chaque chaîne ; sur PHerc0358, les surfaces validées avec et sans alignement, dont celles de la graine 8.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si l'origine de la suivie est la bonne ; aligner sur elle donne un repère commun, pas le compte vrai
depuis la nappe.

Usage :
    uv run python src/nappe/aligner_les_comptes_sur_la_premiere_paire_meme_feuille_valide_t_il_sur_le_bon_tour.py --verifier
    uv run python src/nappe/aligner_les_comptes_sur_la_premiere_paire_meme_feuille_valide_t_il_sur_le_bon_tour.py \\
        --json docs/mesures/aligner_les_comptes_sur_la_premiere_paire_meme_feuille_valide_t_il_sur_le_bon_tour.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
CE_QUE_384_A_PUBLIE = LES_MESURES / "les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.json"
CE_QUE_385_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"
SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LES_CHAINES = m374.LES_CHAINES
LA_PART, LA_PART_BASSE, LE_MINIMUM = 0.9, 0.75, 10


def lecart(paires: list[dict], cs: list[int], cx: list[int]) -> int | None:
    """L'écart des comptes de la suivie et d'une autre chaîne sur leur première paire même feuille, dans l'ordre du plus petit des deux
    sauts puis du plus grand ; None sans paire même feuille."""
    ms = sorted((p for p in paires if p["meme_feuille"]),
                key=lambda p: (min(p["le_saut_suivi"], p["le_saut_compagnon"]), max(p["le_saut_suivi"], p["le_saut_compagnon"]), p["le_saut_suivi"]))
    if not ms:
        return None
    p = ms[0]
    return cs[p["le_saut_suivi"] - 1] - cx[p["le_saut_compagnon"] - 1]


def aligner(paires: dict, comptes: dict) -> tuple[dict, dict]:
    """Les comptes de la compagne et de la tierce décalés sur la suivie, et les écarts appliqués."""
    ecarts = {x: lecart(paires[f"{SUIVIE}|{x}"], comptes[SUIVIE], comptes[x]) for x in (COMPAGNE, TIERCE)}
    out = {SUIVIE: list(comptes[SUIVIE])}
    for x in (COMPAGNE, TIERCE):
        out[x] = [c + (ecarts[x] or 0) for c in comptes[x]]
    return out, ecarts


def le_tour_zero(retrouves: dict, comptes: dict, sens: int) -> tuple[int | None, tuple | None]:
    """Le tour publié du compte zéro dans le repère commun, et la lecture qui le fixe : la première qui retrouve un seul tour, de la suivie
    d'abord, puis de la compagne, puis de la tierce ; la nappe a le compte zéro et l'indice zéro. (None, None) sans telle lecture."""
    for x in LES_CHAINES:
        tous = [0] + list(comptes[x])
        k = next((i for i, r in enumerate(retrouves[x]) if len(r) == 1), None)
        if k is not None:
            return retrouves[x][k][0] - sens * tous[k], (x, k)
    return None, None


def les_statuts(paires: dict, comptes: dict, retrouves: dict | None, sens: int | None) -> list[dict]:
    """Chaque surface des trois chaînes : son statut par `374`, et, là où des tours sont retrouvés, si elle est lue et sur le bon tour du
    repère commun."""
    liens = m374.les_liens(paires)
    t0, ref = (None, None) if retrouves is None else le_tour_zero(retrouves, comptes, sens)
    out = []
    for x in LES_CHAINES:
        for h in range(1, len(comptes[x]) + 1):
            s = m374.le_statut(x, h, liens, comptes)
            r = [] if retrouves is None else retrouves[x][h]
            lue = t0 is not None and len(r) == 1 and (x, h) != ref
            out.append({**s, "lue": bool(lue), "sur_le_bon_tour": (r[0] == t0 + sens * comptes[x][h - 1]) if lue else None})
    return out


def le_bilan(surfaces: list[dict]) -> dict:
    out = {}
    for st in (m374.VALIDEE, m374.CONTREDITE, m374.EN_PARTIE, m374.SEULE):
        lues = [s for s in surfaces if s["le_statut"] == st and s["lue"]]
        out[st] = {"les_surfaces": sum(s["le_statut"] == st for s in surfaces), "lues": len(lues),
                   "sur_le_bon_tour": sum(bool(s["sur_le_bon_tour"]) for s in lues)}
    return out


def le_verdict(d: dict) -> dict:
    a, b = d["paris4_alignes"][m374.VALIDEE], d["paris4_sans_alignement"][m374.VALIDEE]
    if a["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {a['lues']} surfaces validées lues, moins de {LE_MINIMUM}"}
    tete = (f"alignés, {a['sur_le_bon_tour']} des {a['lues']} surfaces validées lues sont sur le bon tour de PHercParis4, contre "
            f"{b['sur_le_bon_tour']} des {b['lues']} sans alignement")
    p = a["sur_le_bon_tour"] / a["lues"]
    if p >= LA_PART:
        suite = ("oui, l'alignement fait valider sur le bon tour, et autant" if a["sur_le_bon_tour"] >= b["sur_le_bon_tour"]
                 else "en partie : le bon tour, mais moins de surfaces")
    else:
        suite = "non" if p < LA_PART_BASSE else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d379, d380, d384, d385 = (json.loads(x.read_text()) for x in (CE_QUE_379_A_PUBLIE, CE_QUE_380_A_PUBLIE, CE_QUE_384_A_PUBLIE,
                                                                    CE_QUE_385_A_PUBLIE))
    p4, p4_sans, cotes4 = [], [], []
    for c3, c5 in zip(d379["les_cotes"], d385["les_cotes"]):
        assert (c3["le_rang"], c3["le_cote"]) == (c5["le_rang"], c5["le_cote"])
        sens = m344.LE_SENS[c3["le_cote"]]
        alignes, ecarts = aligner(c3["les_paires"], c5["les_comptes_de_m7"])
        sa = les_statuts(c3["les_paires"], alignes, c3["les_retrouves"], sens)
        ss = les_statuts(c3["les_paires"], c5["les_comptes_de_m7"], c3["les_retrouves"], sens)
        p4 += sa
        p4_sans += ss
        cotes4.append({"le_rang": c3["le_rang"], "le_cote": c3["le_cote"], "les_ecarts": ecarts,
                       "validees": [sum(s["le_statut"] == m374.VALIDEE for s in ss), sum(s["le_statut"] == m374.VALIDEE for s in sa)],
                       "les_surfaces_alignees": sa})
    p380 = {(c["le_rang"], c["le_cote"]): c["les_paires"] for c in d380["les_cotes"]}
    cotes0 = []
    for c in d384["les_cotes"]:
        comptes = {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(c["les_sauts"][x])] for x in LES_CHAINES}
        paires = p380[(c["le_rang"], c["le_cote"])]
        alignes, ecarts = aligner(paires, comptes)
        sa, ss = les_statuts(paires, alignes, None, None), les_statuts(paires, comptes, None, None)
        va = [s for s in sa if s["le_statut"] == m374.VALIDEE]
        cotes0.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_ecarts": ecarts,
                       "validees": [sum(s["le_statut"] == m374.VALIDEE for s in ss), len(va)],
                       "le_plus_loin": max((s["le_compte"] for s in va), default=None),
                       "les_validees_alignees": [[s["la_chaine"], s["le_saut"], s["le_compte"]] for s in va]})
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
         "les_cotes_de_paris4": cotes4, "les_cotes_de_0358": cotes0}
    d["paris4_alignes"] = le_bilan(p4)
    d["paris4_sans_alignement"] = le_bilan(p4_sans)
    d["le_verdict"] = le_verdict(d)
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

    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    v("★★★★ l'écart : la première paire même feuille, par le plus petit saut puis le plus grand",
      lecart([p(1, 3, True), p(2, 1, True), p(1, 1, False)], [1, 2, 3], [5, 6, 7]) == 2 - 5
      and lecart([p(1, 1, False)], [1], [1]) is None)
    paires = {f"{SUIVIE}|{COMPAGNE}": [p(3, 1, True)], f"{SUIVIE}|{TIERCE}": [p(1, 2, True)], f"{COMPAGNE}|{TIERCE}": []}
    al, ec = aligner(paires, {SUIVIE: [1, 2, 3], COMPAGNE: [1, 2, 3], TIERCE: [1, 2, 3]})
    v("★★★★ l'alignement : la compagne et la tierce décalées sur la suivie",
      ec == {COMPAGNE: 2, TIERCE: -1} and al == {SUIVIE: [1, 2, 3], COMPAGNE: [3, 4, 5], TIERCE: [0, 1, 2]}, str((al, ec)))
    al2, ec2 = aligner({**paires, f"{SUIVIE}|{TIERCE}": []}, {SUIVIE: [1, 2, 3], COMPAGNE: [1, 2, 3], TIERCE: [4]})
    v("★★★★ sans paire même feuille, rien n'est décalé", ec2[TIERCE] is None and al2[TIERCE] == [4])
    ret = {SUIVIE: [[], [-1], [-2]], COMPAGNE: [[], [], []], TIERCE: [[], [], []]}
    v("★★★★ le tour du compte zéro : la première lecture à un seul tour, de la suivie d'abord",
      le_tour_zero(ret, {SUIVIE: [1, 2], COMPAGNE: [1, 2], TIERCE: [1, 2]}, -1) == (0, (SUIVIE, 1))
      and le_tour_zero({**ret, SUIVIE: [[], [], []], COMPAGNE: [[3], [], []]}, {SUIVIE: [1, 2], COMPAGNE: [1, 2], TIERCE: [1, 2]}, -1)
      == (3, (COMPAGNE, 0)) and le_tour_zero({x: [[], [], []] for x in LES_CHAINES}, {x: [1, 2] for x in LES_CHAINES}, -1) == (None, None))
    pp = {f"{SUIVIE}|{COMPAGNE}": [p(1, 1, True), p(2, 2, True)], f"{SUIVIE}|{TIERCE}": [p(1, 1, True), p(2, 2, True)],
          f"{COMPAGNE}|{TIERCE}": [p(1, 1, True), p(2, 2, True)]}
    r3 = {SUIVIE: [[], [-1], [-2]], COMPAGNE: [[], [-1], [-2]], TIERCE: [[], [-1], [-3]]}
    st = les_statuts(pp, {x: [1, 2] for x in LES_CHAINES}, r3, -1)
    vu = {(s["la_chaine"], s["le_saut"]): (s["le_statut"], s["lue"], s["sur_le_bon_tour"]) for s in st}
    v("★★★★ la vérité absolue : un seul repère pour les trois chaînes",
      vu[(TIERCE, 2)] == (m374.VALIDEE, True, False) and vu[(COMPAGNE, 2)] == (m374.VALIDEE, True, True)
      and vu[(SUIVIE, 1)] == (m374.VALIDEE, False, None) and vu[(SUIVIE, 2)] == (m374.VALIDEE, True, True), str(vu))
    v("★★★★ sans tours retrouvés, aucune surface n'est lue", not any(s["lue"] for s in les_statuts(pp, {x: [1, 2] for x in LES_CHAINES}, None, None)))
    b = le_bilan(st)
    v("★★★★ le bilan, sans la lecture qui fixe le repère", b[m374.VALIDEE] == {"les_surfaces": 6, "lues": 5, "sur_le_bon_tour": 4}, str(b))

    def d_(a, n, bb, nb):
        return {"paris4_alignes": {m374.VALIDEE: {"sur_le_bon_tour": a, "lues": n}},
                "paris4_sans_alignement": {m374.VALIDEE: {"sur_le_bon_tour": bb, "lues": nb}}}
    v("★★★★ la règle : 90 % et autant, oui ; 90 % et moins, en partie ; sous 75 %, non",
      le_verdict(d_(60, 60, 58, 58))["lissue"].endswith("et autant") and le_verdict(d_(50, 50, 58, 58))["lissue"].endswith("moins de surfaces")
      and le_verdict(d_(7, 10, 58, 58))["lissue"].endswith("; non") and le_verdict(d_(8, 10, 58, 58))["lissue"].endswith("; en partie"))
    v("★★★ indécidable sous 10 surfaces lues", not le_verdict(d_(9, 9, 58, 58))["decidable"] and le_verdict(d_(10, 10, 5, 5))["decidable"])

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
