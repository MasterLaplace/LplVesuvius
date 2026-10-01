"""Sur la graine 8 de PHerc0358, où l'accord de trois chaînes aux comptes de m7 ne valide toujours rien, les paires qui se contredisent le font-elles dès le premier saut, ou à partir d'un saut que m7 compte deux ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES PAIRES DE LA GRAINE 8 NE SOIENT RELUES AUX COMPTES DE `m7`. Ce qui était vu avant d'écrire : tout ce
que `296` à `385` publient, dont `R4-F570` (aux comptes de `m7`, l'accord valide sur six côtés de PHerc0358, aucun sur la graine 8 ; les
nombres de feuilles de chaque saut, dont, sur la graine 8, côté plus, deux sauts simples de `369` à deux feuilles, au cinquième saut de la
suivie et de la compagne, et des sauts à zéro feuille sur le côté moins), `R4-F561` (sur la graine 8, les paires même feuille à plusieurs
tours d'écart sont sur la même feuille, ce sont les comptes qui s'écartent) et `R4-F563`, `R4-F564`. ⚠ Cette tranche ne lit pas `m7` :
elle relit les paires que `380` publie et les nombres de feuilles que `384` publie.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P183`. Une contradiction qui naît dès le premier saut dit que les chaînes partent de feuilles
différentes ou que leur premier saut se trompe ; une contradiction qui naît après un saut que `m7` compte deux dit que ce saut, compté
juste, sépare les chaînes. Les deux ne se corrigent pas de la même façon.

## Ce qui est fait

- **Les paires et les comptes** : les paires des trois couples de la graine 8, côté plus et côté moins, que `380` publie ; les comptes de
  `m7` de `384` (chaque saut ajoute le nombre de feuilles qu'il franchit, là où il est dit, ce que `369` lui donne ailleurs).
- **Une paire contredit** si « même feuille » et « même compte » ne disent pas la même chose, comme `373` la juge.
- **La naissance** d'un couple : sa première paire qui contredit, dans l'ordre du plus petit des deux sauts, puis du plus grand. Elle est
  **au premier saut** si l'un des deux sauts est le premier ; **après un saut de deux** si, sur l'un des deux chemins qui y mènent, un saut
  franchit deux feuilles de `m7` ou plus ; un couple peut être les deux. Un couple sans paire qui contredit n'a pas de naissance.
- **La règle**, sur les couples qui ont une naissance : si au moins les deux tiers naissent au premier saut, **dès le premier saut** ; si au
  moins les deux tiers naissent après un saut de deux, **à partir d'un saut de deux** ; si les deux, **les deux** ; sinon, **ni l'un ni
  l'autre partout**. Indécidable sous trois couples avec une naissance.

## Les issues

L'issue de la tranche : **sur n couples de la graine 8 qui se contredisent, p naissent au premier saut et q après un saut de deux**, puis
ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Couple par couple, la paire où il naît, l'écart des comptes à sa naissance, et comment cet écart évolue sur les paires même feuille qui
suivent.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : laquelle des chaînes se trompe, ni si les feuilles de la graine 8 se touchent.

Usage :
    uv run python src/nappe/les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.py --verifier
    uv run python src/nappe/les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.py \\
        --json docs/mesures/les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.json
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

import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
CE_QUE_384_A_PUBLIE = LES_MESURES / "les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.json"
LA_GRAINE = 8
LES_COUPLES = ("suivie|compagne", "suivie|tierce", "compagne|tierce")
LA_PART = 2 / 3
LE_MINIMUM = 3


def contredit(p: dict, ca: list[int], cb: list[int]) -> bool:
    """Une paire contredit si « même feuille » et « même compte » ne disent pas la même chose."""
    return bool(p["meme_feuille"] != (ca[p["le_saut_suivi"] - 1] == cb[p["le_saut_compagnon"] - 1]))


def la_naissance(paires: list[dict], ca: list[int], cb: list[int], na: list, nb: list) -> dict | None:
    """La première paire qui contredit, dans l'ordre du plus petit des deux sauts puis du plus grand ; au premier saut si l'un des deux
    est le premier, après un saut de deux si un saut des chemins qui y mènent franchit deux feuilles ou plus. None sans contradiction."""
    ordre = sorted(paires, key=lambda p: (min(p["le_saut_suivi"], p["le_saut_compagnon"]), max(p["le_saut_suivi"], p["le_saut_compagnon"]),
                                          p["le_saut_suivi"]))
    p = next((x for x in ordre if contredit(x, ca, cb)), None)
    if p is None:
        return None
    h, k = p["le_saut_suivi"], p["le_saut_compagnon"]
    deux = [("a", j + 1) for j, n in enumerate(na[:h]) if n is not None and n >= 2] + [("b", j + 1) for j, n in enumerate(nb[:k]) if n is not None and n >= 2]
    return {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": p["meme_feuille"], "lecart_des_comptes": ca[h - 1] - cb[k - 1],
            "au_premier_saut": min(h, k) == 1, "apres_un_saut_de_deux": bool(deux), "les_sauts_de_deux": deux}


def les_ecarts_ensuite(paires: list[dict], ca: list[int], cb: list[int]) -> list[list[int]]:
    """Sur les paires même feuille, dans l'ordre des sauts, les sauts et l'écart des comptes."""
    ms = sorted((p for p in paires if p["meme_feuille"]), key=lambda p: (p["le_saut_suivi"], p["le_saut_compagnon"]))
    return [[p["le_saut_suivi"], p["le_saut_compagnon"], ca[p["le_saut_suivi"] - 1] - cb[p["le_saut_compagnon"] - 1]] for p in ms]


def le_bilan(couples: list[dict]) -> dict:
    nes = [c for c in couples if c["la_naissance"] is not None]
    return {"les_couples": len(couples), "avec_une_naissance": len(nes),
            "au_premier_saut": sum(c["la_naissance"]["au_premier_saut"] for c in nes),
            "apres_un_saut_de_deux": sum(c["la_naissance"]["apres_un_saut_de_deux"] for c in nes)}


def le_verdict(d: dict) -> dict:
    b = d["le_bilan"]
    n = b["avec_une_naissance"]
    if n < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {n} couples de la graine 8 se contredisent, moins de {LE_MINIMUM}"}
    p, q = b["au_premier_saut"], b["apres_un_saut_de_deux"]
    tete = f"sur {n} couples de la graine 8 qui se contredisent, {p} naissent au premier saut et {q} après un saut de deux"
    a, c = p >= LA_PART * n, q >= LA_PART * n
    suite = "les deux" if a and c else "dès le premier saut" if a else "à partir d'un saut de deux" if c else "ni l'un ni l'autre partout"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d380, d384 = (json.loads(x.read_text()) for x in (CE_QUE_380_A_PUBLIE, CE_QUE_384_A_PUBLIE))
    p380 = {(c["le_rang"], c["le_cote"]): c["les_paires"] for c in d380["les_cotes"]}
    couples = []
    for c in d384["les_cotes"]:
        if c["le_rang"] != LA_GRAINE:
            continue
        comptes = {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(c["les_sauts"][x])] for x in c["les_sauts"]}
        nombres = {x: [s["le_nombre_de_feuilles"] for s in c["les_sauts"][x]] for x in c["les_sauts"]}
        for k in LES_COUPLES:
            a, b = k.split("|")
            ps = p380[(c["le_rang"], c["le_cote"])][k]
            couples.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "le_couple": k, "les_paires": len(ps),
                            "contredisent": sum(contredit(p, comptes[a], comptes[b]) for p in ps),
                            "la_naissance": la_naissance(ps, comptes[a], comptes[b], nombres[a], nombres[b]),
                            "les_ecarts_ensuite": les_ecarts_ensuite(ps, comptes[a], comptes[b]),
                            "les_comptes": {a: comptes[a], b: comptes[b]}, "les_nombres": {a: nombres[a], b: nombres[b]}})
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part": round(LA_PART, 4), "le_minimum": LE_MINIMUM},
         "les_couples": couples}
    d["le_bilan"] = le_bilan(couples)
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
    v("★★★★ une paire contredit : même feuille à un autre compte, ou autre feuille au même compte",
      contredit(p(1, 1, True), [1], [2]) and contredit(p(1, 1, False), [1], [1]) and not contredit(p(1, 1, True), [1], [1])
      and not contredit(p(1, 1, False), [1], [2]))
    ca, cb = [1, 2, 4, 5], [1, 2, 3, 4]
    n = la_naissance([p(4, 4, True), p(3, 3, True), p(1, 1, True), p(2, 2, True)], ca, cb, [1, 1, 2, 1], [1, 1, 1, 1])
    v("★★★★ la naissance : la première paire qui contredit dans l'ordre des sauts, après un saut de deux de la première chaîne",
      n is not None and (n["le_saut_suivi"], n["le_saut_compagnon"]) == (3, 3) and n["apres_un_saut_de_deux"] and not n["au_premier_saut"]
      and n["les_sauts_de_deux"] == [("a", 3)] and n["lecart_des_comptes"] == 1, str(n))
    n1 = la_naissance([p(2, 2, True), p(1, 2, True)], [1, 2], [1, 2], [1, 1], [1, 1])
    v("★★★★ au premier saut si l'un des deux sauts est le premier",
      lambda: n1["au_premier_saut"] and (n1["le_saut_suivi"], n1["le_saut_compagnon"]) == (1, 2) and not n1["apres_un_saut_de_deux"])
    v("★★★★ l'ordre : le plus petit des deux sauts, puis le plus grand",
      lambda: (lambda x: (x["le_saut_suivi"], x["le_saut_compagnon"]))(
          la_naissance([p(1, 3, True), p(2, 1, True)], [1, 2], [3, 2, 4], [1, 1], [1, 1, 1])) == (2, 1))
    v("★★★★ un saut de deux après la paire ne compte pas", lambda: la_naissance([p(2, 2, True)], [1, 3, 4], [1, 2, 3], [1, 1, 2], [1, 1, 1])
      ["apres_un_saut_de_deux"] is False)
    v("★★★★ un saut au nombre absent n'est pas un saut de deux, un saut de trois l'est",
      la_naissance([p(2, 2, True)], [1, 2], [1, 3], [None, None], [1, 3])["les_sauts_de_deux"] == [("b", 2)])
    v("★★★★ pas de naissance sans contradiction", la_naissance([p(1, 1, True), p(2, 2, True)], [1, 2], [1, 2], [1, 1], [1, 1]) is None)
    v("★★★ les écarts ensuite : les paires même feuille et l'écart des comptes",
      les_ecarts_ensuite([p(2, 3, True), p(1, 1, True), p(2, 2, False)], [1, 3], [1, 2, 3]) == [[1, 1, 0], [2, 3, 0]])
    nn = lambda pr, dx: {"au_premier_saut": pr, "apres_un_saut_de_deux": dx}  # noqa: E731
    b = le_bilan([{"la_naissance": nn(True, False)}, {"la_naissance": nn(True, True)}, {"la_naissance": None}])
    v("★★★★ le bilan", b == {"les_couples": 3, "avec_une_naissance": 2, "au_premier_saut": 2, "apres_un_saut_de_deux": 1}, str(b))

    def d_(n_, p_, q_):
        return {"le_bilan": {"avec_une_naissance": n_, "au_premier_saut": p_, "apres_un_saut_de_deux": q_}}
    v("★★★★ la règle : deux tiers au premier saut, deux tiers après un saut de deux, les deux, ou ni l'un ni l'autre",
      le_verdict(d_(6, 4, 1))["lissue"].endswith("dès le premier saut") and le_verdict(d_(6, 1, 4))["lissue"].endswith("saut de deux")
      and le_verdict(d_(6, 4, 4))["lissue"].endswith("; les deux") and le_verdict(d_(6, 3, 3))["lissue"].endswith("partout")
      and "sur 6 couples de la graine 8 qui se contredisent, 4 naissent au premier saut et 1 après" in le_verdict(d_(6, 4, 1))["lissue"])
    v("★★★ indécidable sous trois couples", not le_verdict(d_(2, 2, 2))["decidable"] and le_verdict(d_(3, 2, 0))["decidable"])

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
