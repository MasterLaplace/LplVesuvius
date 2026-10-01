"""Sur PHercParis4, là où le vote désigne une chaîne, recompter d'un tour le seul saut qui fait tenir ses deux couples met-il ses surfaces sur le bon tour publié ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT NE SOIT RECOMPTÉ SUR PHERCPARIS4, ET AVANT QUE LE VOTE N'Y SOIT CALCULÉ. Ce qui était vu
avant d'écrire : tout ce que `296` à `381` publient, dont `R4-F565` (sur PHercParis4, la règle de `374` ne valide que des surfaces sur le
bon tour publié, 46 sur 46 lues ; 3 des 14 surfaces contredites lues ne le sont pas, des surfaces de suivies dont un saut a été compté
double, sur les graines 1 et 3, côtés moins) et `R4-F567` (sur la graine 4, côté plus, de PHerc0358, recompter double le premier saut de
la suivie que le vote désigne fait tenir ses deux couples, 27 paires sur 27 et 24 sur 24). ⚠ Cette tranche ne lit pas `m7` : elle relit
les paires, les comptes et les tours retrouvés que `379` et `380` publient.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P179`. Dans `381`, le saut à recompter a été choisi parce que `380` l'avait nommé. Une règle
qui cherche seule ce saut ne vaut que si elle est éprouvée là où une vérité existe.

## Ce qui est fait

- **Les côtés** : les seize côtés de PHercParis4 de `379`, avec leurs paires, leurs comptes corrigés et les tours que chaque nappe et chaque
  surface retrouvent ; à côté, les seize côtés de PHerc0358 de `380`.
- **Le vote** : celui de `372`, sur les couples de `373`. Là où il désigne une chaîne, les **recomptes candidats** sont chaque saut de cette
  chaîne compté un tour de plus ou de moins (nul en simple, simple en nul ou en double, double en simple), un seul à la fois.
- **La règle de recompte** : un candidat **fait tenir** la chaîne si, recomptée, ses deux couples tiennent. Le recompte n'est retenu que si
  un seul candidat fait tenir la chaîne ; sinon, rien n'est recompté.
- **La vérité** : celle de `379`, recalculée avec les comptes recomptés. Une surface est jugée si elle est lue, sur le bon tour si son tour
  s'écarte de celui de sa référence d'autant que son compte. ⚠ Un recompte n'est **jugeable** que si la référence de sa chaîne précède le
  saut recompté : un saut recompté avant la référence décale d'autant la référence et les surfaces, et les tours publiés n'en disent rien.
- **Le contrôle** : sur PHerc0358, la règle retrouve seule le recompte de `381`, le premier saut de la suivie de la graine 4, côté plus,
  compté double, et lui seul.
- **La règle de la tranche** : parmi les surfaces de chaînes recomptées, sur les recomptes jugeables, que le recompte fait valider et qui
  sont lues, au moins 90 % sur le bon tour, **oui** ; moins de 75 %, **non** ; sinon, **en partie**. Indécidable sous 5 surfaces lues, ou
  si le contrôle échoue.

## Les issues

L'issue de la tranche : **sur PHercParis4, le vote désigne une chaîne sur v côtés, la règle en recompte r, et a des n surfaces que le
recompte fait valider et qui sont lues sont sur le bon tour**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté : la chaîne désignée, les candidats qui la font tenir, le recompte retenu, et ce que deviennent les surfaces des deux autres
chaînes que la chaîne désignée contredisait.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la règle là où le vote ne désigne personne, ni si un saut recompté a franchi le nombre de
feuilles que son nouveau compte dit ; seul `m7` le dirait.

Usage :
    uv run python src/nappe/recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.py --verifier
    uv run python src/nappe/recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.py \\
        --json docs/mesures/recompter_le_saut_de_la_chaine_designee_la_met_il_sur_le_bon_tour_de_paris4.json
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
import une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358 as m372  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LES_CHAINES = m374.LES_CHAINES
LE_RECOMPTE_DE_381 = {"le_rang": 4, "le_cote": "plus", "la_chaine": SUIVIE, "le_saut": 1, "de": 1, "a": 2}
LE_MINIMUM = 5
LA_PART, LA_PART_BASSE = 0.9, 0.75


def les_increments(comptes: list[int]) -> list[int]:
    """Ce que chaque saut ajoute au compte corrigé : 0 s'il est nul, 1 s'il est simple, 2 s'il est double."""
    return [b - a for a, b in zip([0] + list(comptes[:-1]), comptes)]


def recompter(comptes: list[int], h: int, nouveau: int) -> list[int]:
    """Les comptes corrigés d'une chaîne dont le saut `h` ajoute `nouveau` au lieu de ce qu'il ajoutait."""
    inc = les_increments(comptes)
    inc[h - 1] = nouveau
    out, w = [], 0
    for x in inc:
        w += x
        out.append(w)
    return out


def les_couples(paires: dict, comptes: dict) -> dict:
    sa = lambda cs: [{"le_compte_corrige": w} for w in cs]  # noqa: E731
    return {k: m373.le_couple(p, sa(comptes[k.split("|")[0]]), sa(comptes[k.split("|")[1]])) for k, p in paires.items()}


def les_candidats(paires: dict, comptes: dict, x: str) -> list[dict]:
    """Chaque saut de la chaîne `x` compté un tour de plus ou de moins, et si ses deux couples tiennent alors."""
    out = []
    for h, d in enumerate(les_increments(comptes[x]), 1):
        for n in (d - 1, d + 1):
            if not 0 <= n <= 2:
                continue
            c = {**comptes, x: recompter(comptes[x], h, n)}
            couples = les_couples(paires, c)
            tient = all(v["tient"] for k, v in couples.items() if x in k.split("|"))
            out.append({"le_saut": h, "de": d, "a": n, "fait_tenir": bool(tient),
                        "les_couples": {k: [v["tiennent"], v["les_paires"]] for k, v in couples.items() if x in k.split("|")}})
    return out


def le_recompte(paires: dict, comptes: dict) -> dict:
    """La chaîne que le vote désigne, ses candidats, et le recompte retenu : le seul candidat qui la fait tenir, sinon aucun."""
    vote = m372.le_vote(les_couples(paires, comptes))
    if vote is None:
        return {"la_chaine": None, "les_candidats": [], "le_retenu": None}
    cands = les_candidats(paires, comptes, vote)
    tiennent = [c for c in cands if c["fait_tenir"]]
    return {"la_chaine": vote, "les_candidats": cands, "le_retenu": tiennent[0] if len(tiennent) == 1 else None}


def le_cote(rang: int, cote: str, paires: dict, comptes: dict, retrouves: dict | None, sens: int | None) -> dict:
    """Un côté avant et après le recompte retenu : statuts de `374`, et vérité de `379` là où des tours sont retrouvés."""
    r = le_recompte(paires, comptes)
    apres = comptes
    if r["le_retenu"] is not None:
        k = r["le_retenu"]
        apres = {**comptes, r["la_chaine"]: recompter(comptes[r["la_chaine"]], k["le_saut"], k["a"])}

    def statuts(cs):
        ver = ({x: m379.la_verite(retrouves[x], cs[x], sens) for x in LES_CHAINES} if retrouves is not None
               else {x: [{"le_saut": h, "lue": False, "sur_le_bon_tour": None, "le_tour": None} for h in range(1, len(cs[x]) + 1)]
                     for x in LES_CHAINES})
        return m379.le_cote(paires, cs, ver)
    ref = None if retrouves is None or r["la_chaine"] is None else m379.la_reference(retrouves[r["la_chaine"]])
    jugeable = bool(r["le_retenu"] is not None and ref is not None and ref < r["le_retenu"]["le_saut"])
    return {"le_rang": rang, "le_cote": cote, **r, "la_reference": ref, "jugeable": jugeable, "avant": statuts(comptes),
            "apres": statuts(apres)}


def les_nouvelles(c: dict, seulement_la_chaine: bool) -> list[dict]:
    """Les surfaces que le recompte fait valider : validées après, pas avant ; de la chaîne recomptée seulement, ou de toutes."""
    avant = {(s["la_chaine"], s["le_saut"]): s["le_statut"] for s in c["avant"]}
    return [s for s in c["apres"] if s["le_statut"] == m374.VALIDEE and avant[(s["la_chaine"], s["le_saut"])] != m374.VALIDEE
            and (not seulement_la_chaine or s["la_chaine"] == c["la_chaine"])]


def le_bilan(cotes: list[dict]) -> dict:
    recomptes = [c for c in cotes if c["le_retenu"] is not None]
    siennes = [s for c in recomptes if c["jugeable"] for s in les_nouvelles(c, True)]
    toutes = [s for c in recomptes if c["jugeable"] for s in les_nouvelles(c, False)]
    lit = lambda ss: {"les_surfaces": len(ss), "lues": sum(s["lue"] for s in ss),  # noqa: E731
                      "sur_le_bon_tour": sum(bool(s["sur_le_bon_tour"]) for s in ss if s["lue"])}
    return {"les_cotes": len(cotes), "designees": sum(c["la_chaine"] is not None for c in cotes), "recomptes": len(recomptes),
            "jugeables": sum(c["jugeable"] for c in recomptes),
            "les_recomptes": [f"{c['le_rang']} {c['le_cote']} : {c['la_chaine']}, saut {c['le_retenu']['le_saut']}, "
                              f"{c['le_retenu']['de']} en {c['le_retenu']['a']}" for c in recomptes],
            "les_surfaces_de_la_chaine": lit(siennes), "les_surfaces_des_trois": lit(toutes)}


def le_controle(cotes_0358: list[dict]) -> bool:
    """Sur PHerc0358, le seul recompte retenu est celui de `381`."""
    retenus = [(c["le_rang"], c["le_cote"], c["la_chaine"], c["le_retenu"]["le_saut"], c["le_retenu"]["de"], c["le_retenu"]["a"])
               for c in cotes_0358 if c["le_retenu"] is not None]
    r = LE_RECOMPTE_DE_381
    return retenus == [(r["le_rang"], r["le_cote"], r["la_chaine"], r["le_saut"], r["de"], r["a"])]


def le_verdict(d: dict) -> dict:
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : sur PHerc0358, la règle ne retrouve pas le seul recompte de 381"}
    b = d["le_bilan"]
    s = b["les_surfaces_de_la_chaine"]
    if s["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {s['lues']} surfaces recomptées validées lues, moins de {LE_MINIMUM}"}
    tete = (f"sur PHercParis4, le vote désigne une chaîne sur {b['designees']} côtés, la règle en recompte {b['recomptes']}, et "
            f"{s['sur_le_bon_tour']} des {s['lues']} surfaces que le recompte fait valider et qui sont lues sont sur le bon tour")
    p = s["sur_le_bon_tour"] / s["lues"]
    suite = ("oui, le recompte met la chaîne désignée sur le bon tour" if p >= LA_PART else "non" if p < LA_PART_BASSE else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def les_cotes_de_379(d379: dict) -> list[dict]:
    return [le_cote(c["le_rang"], c["le_cote"], c["les_paires"], c["les_comptes"], c["les_retrouves"], m344.LE_SENS[c["le_cote"]])
            for c in d379["les_cotes"]]


def les_cotes_de_380(d380: dict) -> list[dict]:
    return [le_cote(c["le_rang"], c["le_cote"], c["les_paires"], {x: [s["le_compte_corrige"] for s in c["les_sauts"][x]] for x in LES_CHAINES},
                    None, None) for c in d380["les_cotes"]]


def le_resume(c: dict) -> dict:
    st = lambda ss: {k: sum(s["le_statut"] == k for s in ss) for k in (m374.VALIDEE, m374.EN_PARTIE, m374.CONTREDITE, m374.SEULE)}  # noqa: E731
    return {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_chaine": c["la_chaine"],
            "les_candidats_qui_font_tenir": [k for k in c["les_candidats"] if k["fait_tenir"]], "le_retenu": c["le_retenu"],
            "la_reference": c["la_reference"], "jugeable": c["jugeable"],
            "avant": st(c["avant"]), "apres": st(c["apres"]), "les_nouvelles": les_nouvelles(c, False), "les_surfaces": c["apres"]}


def mesurer() -> dict:
    d379, d380 = (json.loads(x.read_text()) for x in (CE_QUE_379_A_PUBLIE, CE_QUE_380_A_PUBLIE))
    c4, c0 = les_cotes_de_379(d379), les_cotes_de_380(d380)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_minimum": LE_MINIMUM, "la_part": LA_PART,
                                                                    "la_part_basse": LA_PART_BASSE},
         "le_controle": le_controle(c0), "les_cotes_de_paris4": [le_resume(c) for c in c4],
         "les_cotes_de_0358": [le_resume(c) for c in c0]}
    d["le_bilan"] = le_bilan(c4)
    d["le_bilan_de_0358"] = le_bilan(c0)
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

    v("★★★★ les incréments : ce que chaque saut ajoute au compte", les_increments([1, 3, 3, 4]) == [1, 2, 0, 1])
    v("★★★★ le recompte : un seul saut change, la suite est décalée", recompter([1, 2, 3, 4], 2, 2) == [1, 3, 4, 5]
      and recompter([2, 3, 4], 1, 1) == [1, 2, 3] and recompter([1, 2, 2, 3], 3, 1) == [1, 2, 3, 4])

    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    paires = {k: [p(h, h, True) for h in range(1, 6)] for k in (f"{SUIVIE}|{COMPAGNE}", f"{SUIVIE}|{TIERCE}", f"{COMPAGNE}|{TIERCE}")}
    bons = [2, 3, 4, 5, 6]
    cs = {SUIVIE: [1, 2, 3, 4, 5], COMPAGNE: bons, TIERCE: bons}
    r = le_recompte(paires, cs)
    v("★★★★ le vote désigne la suivie ; le seul candidat qui la fait tenir est son premier saut compté double",
      r["la_chaine"] == SUIVIE and {k: v for k, v in r["le_retenu"].items() if k != "les_couples"} == {"le_saut": 1, "de": 1, "a": 2, "fait_tenir": True}
      and r["le_retenu"]["les_couples"] == {f"{SUIVIE}|{COMPAGNE}": [5, 5], f"{SUIVIE}|{TIERCE}": [5, 5]}
      and sum(c["fait_tenir"] for c in r["les_candidats"]) == 1, str(r["le_retenu"]))
    v("★★★★ les candidats : un tour de plus ou de moins à chaque saut, jamais sous nul ni au-delà du double",
      lambda: [(c["le_saut"], c["de"], c["a"]) for c in les_candidats(paires, {**cs, SUIVIE: [0, 2, 3, 4, 5]}, SUIVIE)][:3]
      == [(1, 0, 1), (2, 2, 1), (3, 1, 0)])
    v("★★★★ aucun recompte sans chaîne désignée", lambda: le_recompte(paires, {x: bons for x in LES_CHAINES})["le_retenu"] is None
      and le_recompte(paires, {x: bons for x in LES_CHAINES})["la_chaine"] is None)
    ambigu = {k: [p(2, 2, True)] * 5 for k in paires}
    v("★★★★ deux candidats qui font tenir la chaîne : rien n'est recompté",
      lambda: (lambda rr: rr["la_chaine"] == SUIVIE and rr["le_retenu"] is None and sum(c["fait_tenir"] for c in rr["les_candidats"]) == 2)(
          le_recompte(ambigu, {SUIVIE: [1, 2], COMPAGNE: [1, 3], TIERCE: [1, 3]})))
    ret = {x: [[], [-1], [-2], [-3], [-4], [-5]] for x in LES_CHAINES}
    c_ = le_cote(1, "moins", paires, cs, ret, -1)
    vu = {(s["la_chaine"], s["le_saut"]): (s["le_statut"], s["sur_le_bon_tour"]) for s in c_["apres"]}
    v("★★★★ après le recompte, la vérité est recalculée avec les nouveaux comptes",
      vu[(SUIVIE, 2)] == (m374.VALIDEE, True) and c_["avant"][1]["sur_le_bon_tour"] is True, str(vu))
    v("★★★★ les nouvelles : validées après et pas avant ; celles de la chaîne recomptée, ou de toutes",
      lambda: len(les_nouvelles(c_, True)) == 5 and len(les_nouvelles(c_, False)) == 15)
    sauf = {f"{SUIVIE}|{COMPAGNE}": [p(h, h, True) for h in range(1, 6)], f"{SUIVIE}|{TIERCE}": [p(h, h, False) for h in range(1, 6)],
            f"{COMPAGNE}|{TIERCE}": [p(h, h, True) for h in range(1, 6)]}
    v("★★★★ un candidat ne fait tenir la chaîne que si ses DEUX couples tiennent",
      lambda: next(c for c in les_candidats(sauf, cs, SUIVIE) if (c["le_saut"], c["a"]) == (1, 2))["fait_tenir"] is False)
    tard = [[], [-1], [-2], [-4], [-5], [-6]]
    c3 = le_cote(1, "moins", paires, {SUIVIE: [1, 2, 3, 4, 5], COMPAGNE: [1, 2, 4, 5, 6], TIERCE: [1, 2, 4, 5, 6]},
                 {x: tard for x in LES_CHAINES}, -1)
    v3 = lambda t: {(s["la_chaine"], s["le_saut"]): s for s in c3[t]}  # noqa: E731
    v("★★★★ un saut recompté après la référence change la vérité des surfaces qui le suivent",
      lambda: c3["le_retenu"]["le_saut"] == 3 and v3("avant")[(SUIVIE, 3)]["sur_le_bon_tour"] is False
      and v3("apres")[(SUIVIE, 3)]["sur_le_bon_tour"] is True and v3("apres")[(SUIVIE, 3)]["le_statut"] == m374.VALIDEE)
    v("★★★★ une surface déjà validée avant le recompte n'est pas nouvelle",
      lambda: v3("avant")[(SUIVIE, 2)]["le_statut"] == m374.VALIDEE and [s["le_saut"] for s in les_nouvelles(c3, True)] == [3, 4, 5])
    v("★★★★ un recompte avant la référence n'est pas jugeable ; après, il l'est",
      c_["la_reference"] == 1 and c_["jugeable"] is False and c3["la_reference"] == 1 and c3["jugeable"] is True)
    b = le_bilan([c3, c_, le_cote(2, "moins", paires, {x: bons for x in LES_CHAINES}, ret, -1)])
    v("★★★★ le bilan : côtés désignés, recomptés, jugeables, et surfaces lues sur le bon tour des seuls recomptes jugeables",
      (b["designees"], b["recomptes"], b["jugeables"]) == (2, 2, 1) and b["les_surfaces_de_la_chaine"]["lues"] == 3
      and b["les_surfaces_de_la_chaine"]["sur_le_bon_tour"] == 3, str(b))
    ok0 = [{"le_rang": 4, "le_cote": "plus", "la_chaine": SUIVIE, "le_retenu": {"le_saut": 1, "de": 1, "a": 2}},
           {"le_rang": 7, "le_cote": "plus", "la_chaine": SUIVIE, "le_retenu": None}]
    v("★★★★ le contrôle : sur PHerc0358, le seul recompte retenu est celui de 381",
      le_controle(ok0) and not le_controle(ok0 + [{"le_rang": 7, "le_cote": "moins", "la_chaine": TIERCE,
                                                    "le_retenu": {"le_saut": 2, "de": 1, "a": 0}}])
      and not le_controle([{**ok0[0], "le_retenu": {"le_saut": 2, "de": 1, "a": 2}}]) and not le_controle([]))

    def d_(t, n, ctl=True):
        return {"le_controle": ctl, "le_bilan": {"designees": 4, "recomptes": 2, "les_surfaces_de_la_chaine": {"lues": n, "sur_le_bon_tour": t}}}
    v("★★★★ la règle : 90 % oui, sous 75 % non, sinon en partie",
      le_verdict(d_(9, 10))["lissue"].endswith("sur le bon tour") and le_verdict(d_(8, 10))["lissue"].endswith("; en partie")
      and le_verdict(d_(7, 10))["lissue"].endswith("; non") and "le vote désigne une chaîne sur 4 côtés, la règle en recompte 2" in le_verdict(d_(9, 10))["lissue"])
    v("★★★ indécidable sous 5 surfaces lues, ou si le contrôle échoue",
      not le_verdict(d_(4, 4))["decidable"] and not le_verdict(d_(9, 10, ctl=False))["decidable"] and le_verdict(d_(5, 5))["decidable"])

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
