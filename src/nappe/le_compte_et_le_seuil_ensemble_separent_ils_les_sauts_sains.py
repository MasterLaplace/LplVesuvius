"""Le compte des feuilles de 345, auquel s'ajoute le seuil de 50 points à zéro, sépare-t-il sur les graines 4 à 8 les sauts justes qui ne sont pas à cheval de tous les autres ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES DEUX CRITÈRES NE SOIENT PRIS ENSEMBLE SUR UN SEUL SAUT. Ce qui était vu avant d'écrire : tout ce
que `296` à `351` publient, dont `R4-F531` (le compte de `345` tient 95 des 104 sauts justes et 3 des 6 faux), `R4-F535` (`345` tient 53
des 60 sauts justes à cheval) et `R4-F537` (le seuil de 50 points à zéro refuse 3 des 44 sauts justes sains, 37 des 60 sauts à cheval et
4 des 6 faux). Ce qui n'était pas vu : combien de sauts les deux critères refusent ensemble, puisque ceux que l'un refuse peuvent être ceux
que l'autre refuse déjà.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P148`. `345` refuse les sauts qui passent par-dessus un tour ; le seuil refuse une part des
surfaces à cheval. S'ils se complètent, leur conjonction est le critère sans référent à porter sur PHerc0358 pour `#5`. Aucun des deux
n'est retouché : `345` à ses trois quarts d'une feuille sur au moins 50 points comptés, le seuil à ses 50 points à zéro.

## Ce qui est fait

- **Aucune mesure neuve** : `345` et `349` rapprochés saut par saut, par la chaîne, la graine, le côté et le numéro du saut.
- **Le critère** : un saut **tient** si `345` le tient et s'il a moins de 50 points que le compte dit à zéro feuille.
- **Les sauts sains** : les sauts justes des graines 4 à 8 que `349` lit et ne dit pas à cheval. **Les autres** : les sauts justes des
  graines 4 à 8 que `349` dit à cheval, et les sauts faux des graines 4 à 8 que `349` lit.
- **Le contrôle** : chaque saut cherché est dans `345`, et la justesse que `349` lui donne est celle que `345` publie ; sinon, la
  tranche est indécidable.
- **La règle** : celle de `344`, les autres à la place des sauts faux : si le critère tient au moins 75 % des sauts sains et au plus 25 % des
  autres, **il les sépare** ; si l'écart entre les deux parts est sous 25 points, **il ne les sépare pas** ; sinon, **en partie**.
  Indécidable sous 5 sauts d'un côté.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, le compte et le seuil ensemble tiennent a des n sauts justes sains et b des m autres**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Chacun des deux critères seul, sur les mêmes groupes ; la part des sauts tenus qui sont sains ; les sauts à cheval et les sauts faux
séparément ; les mêmes bilans sur les graines 1 à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut le critère sur PHerc0358 ; et ce qu'une chaîne qui refuse les sauts qu'il refuse
aurait fait ensuite.

Usage :
    uv run python src/nappe/le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.py --verifier
    uv run python src/nappe/le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.py \\
        --json docs/mesures/le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_345_A_PUBLIE = LES_MESURES / "les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux.json"
CE_QUE_349_A_PUBLIE = LES_MESURES / "les_sauts_justes_donnent_ils_des_surfaces_a_cheval.json"

LE_SEUIL = 50
LA_TENUE_DES_SAINS = 0.75
LA_TENUE_DES_AUTRES = 0.25
LECART_MINIMAL = 0.25
LE_MINIMUM = 5
LES_CRITERES = ("les_deux", "345_seul", "le_seuil_seul")


def les_sauts_345(d345: dict) -> dict:
    """Pour chaque saut que `345` publie : sa justesse, si `345` le tient, et ses points à zéro."""
    return {(n, g["le_rang"], c, s["le_saut"]): {"la_justesse": s["la_justesse"], "tient_345": bool(s["tient"]),
                                                  "les_zeros": s["les_feuilles"]["les_comptes"].get("0", 0)}
            for n, ch in d345["les_chaines"].items() for g in ch["les_graines"] for c, x in g["les_cotes"].items() for s in x["les_sauts"]}


def tient(saut: dict, critere: str = "les_deux") -> bool:
    peu = saut["les_zeros"] < LE_SEUIL
    return {"les_deux": saut["tient_345"] and peu, "345_seul": saut["tient_345"], "le_seuil_seul": peu}[critere]


def les_groupes(d349: dict, graines: tuple) -> dict:
    """Les sauts sains, les sauts justes à cheval et les sauts faux que `349` lit, sur les graines données."""
    lus = [s for s in d349["les_surfaces"] if s["le_rang"] in graines and s["la_surface"] is not None]
    cle = lambda s: (s["la_chaine"], s["le_rang"], s["le_cote"], s["le_saut"])  # noqa: E731
    return {"les_sains": sorted(cle(s) for s in lus if s["la_justesse"] == "juste" and not s["la_surface"]["a_cheval"]),
            "les_a_cheval": sorted(cle(s) for s in lus if s["la_justesse"] == "juste" and s["la_surface"]["a_cheval"]),
            "les_faux": sorted(cle(s) for s in lus if s["la_justesse"].startswith("faux"))}


def le_controle(d349: dict, sauts: dict) -> bool:
    for s in d349["les_surfaces"]:
        k = (s["la_chaine"], s["le_rang"], s["le_cote"], s["le_saut"])
        if k not in sauts or sauts[k]["la_justesse"] != s["la_justesse"]:
            return False
    return True


def le_bilan(groupes: dict, sauts: dict, critere: str = "les_deux") -> dict:
    """Pour chaque groupe, combien de sauts et combien le critère en tient ; les autres sont les sauts à cheval et les faux ensemble."""
    b = {k: {"les_sauts": len(v), "les_tenus": sum(tient(sauts[x], critere) for x in v)} for k, v in groupes.items()}
    b["les_autres"] = {"les_sauts": b["les_a_cheval"]["les_sauts"] + b["les_faux"]["les_sauts"],
                       "les_tenus": b["les_a_cheval"]["les_tenus"] + b["les_faux"]["les_tenus"]}
    for x in b.values():
        x["la_part"] = round(x["les_tenus"] / x["les_sauts"], 4) if x["les_sauts"] else None
    t = b["les_sains"]["les_tenus"] + b["les_autres"]["les_tenus"]
    b["la_part_des_tenus_qui_sont_sains"] = round(b["les_sains"]["les_tenus"] / t, 4) if t else None
    return b


def le_verdict(d: dict) -> dict:
    if not d["le_controle"]:
        return {"decidable": False, "lissue": "indécidable : les sauts de 349 ne se retrouvent pas dans 345"}
    b = d["les_bilans"]["graines_4_a_8"]["les_deux"]
    s, a = b["les_sains"], b["les_autres"]
    if s["les_sauts"] < LE_MINIMUM or a["les_sauts"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {s['les_sauts']} sauts sains et {a['les_sauts']} autres"}
    tete = (f"sur les graines 4 à 8, le compte et le seuil ensemble tiennent {s['les_tenus']} des {s['les_sauts']} sauts justes sains et "
            f"{a['les_tenus']} des {a['les_sauts']} autres")
    if s["la_part"] >= LA_TENUE_DES_SAINS and a["la_part"] <= LA_TENUE_DES_AUTRES:
        suite = "ils les séparent"
    elif s["la_part"] - a["la_part"] < LECART_MINIMAL:
        suite = "ils ne les séparent pas"
    else:
        suite = "ils ne les séparent qu'en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d345, d349 = (json.loads(p.read_text()) for p in (CE_QUE_345_A_PUBLIE, CE_QUE_349_A_PUBLIE))
    sauts = les_sauts_345(d345)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_seuil": LE_SEUIL, "la_tenue_des_sains": LA_TENUE_DES_SAINS, "la_tenue_des_autres": LA_TENUE_DES_AUTRES,
                            "lecart_minimal": LECART_MINIMAL, "le_minimum": LE_MINIMUM},
         "le_controle": le_controle(d349, sauts)}
    if d["le_controle"]:
        g48, g13 = les_groupes(d349, (4, 5, 6, 7, 8)), les_groupes(d349, (1, 2, 3))
        d["les_groupes"] = {k: [list(x) for x in v] for k, v in g48.items()}
        d["les_bilans"] = {"graines_4_a_8": {c: le_bilan(g48, sauts, c) for c in LES_CRITERES},
                           "graines_1_a_3": {c: le_bilan(g13, sauts, c) for c in LES_CRITERES}}
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

    def saut(k, j, t, z):
        return {"le_saut": k, "la_justesse": j, "tient": t, "tient_328": not t,
                "les_feuilles": {"les_comptes": {"0": z, "1": 400} if z else {"1": 400}}}
    d345 = {"les_chaines": {"bornée": {"les_graines": [{"le_rang": 8, "les_cotes": {"moins": {"les_sauts": [
        saut(1, "juste", True, 10), saut(2, "juste", True, 60), saut(3, "juste", False, 0), saut(4, "faux : deux tours", True, 49)]}}}]}}}
    s = les_sauts_345(d345)
    k = lambda n: ("bornée", 8, "moins", n)  # noqa: E731
    v("★★★★ les sauts de 345 : justesse, tenue et points à zéro, zéro quand le compte n'en dit aucun",
      s[k(1)] == {"la_justesse": "juste", "tient_345": True, "les_zeros": 10} and s[k(3)]["les_zeros"] == 0, str(s))
    v("★★★★ les deux ensemble : tenu par 345 et moins de 50 points à zéro, borne comprise",
      [tient(s[k(i)]) for i in (1, 2, 3, 4)] == [True, False, False, True]
      and tient({"tient_345": True, "les_zeros": 50}) is False and tient({"tient_345": True, "les_zeros": 49}) is True)
    v("★★★ chaque critère seul", [tient(s[k(i)], "345_seul") for i in (1, 2, 3, 4)] == [True, True, False, True]
      and [tient(s[k(i)], "le_seuil_seul") for i in (1, 2, 3, 4)] == [True, False, True, True])

    def surf(n, j, cheval, rang=8):
        return {"la_chaine": "bornée", "le_rang": rang, "le_cote": "moins", "le_saut": n, "la_justesse": j, "la_surface": {"a_cheval": cheval}}
    d349 = {"les_surfaces": [surf(1, "juste", False), surf(2, "juste", True), surf(3, "juste", False), surf(4, "faux : deux tours", True),
                             {**surf(1, "juste", False, rang=2)}, {**surf(5, "juste", False), "la_surface": None}]}
    try:
        g = les_groupes(d349, (4, 5, 6, 7, 8))
    except Exception as exc:  # noqa: BLE001
        g = {"levée": str(exc)}
    attendu = {"les_sains": [k(1), k(3)], "les_a_cheval": [k(2)], "les_faux": [k(4)]}
    v("★★★★ sains, à cheval et faux : graines 4 à 8, surfaces lues seulement", g == attendu, str(g))
    g = attendu
    b = le_bilan(g, s)
    v("★★★★ les autres sont les sauts à cheval et les faux ensemble",
      b["les_sains"] == {"les_sauts": 2, "les_tenus": 1, "la_part": 0.5} and b["les_autres"] == {"les_sauts": 2, "les_tenus": 1, "la_part": 0.5}
      and b["la_part_des_tenus_qui_sont_sains"] == 0.5, str(b))
    v("★★★ le contrôle tient quand chaque saut de 349 est dans 345 avec la même justesse",
      le_controle({"les_surfaces": d349["les_surfaces"][:4]}, s))
    v("★★★★ une justesse qui diffère, ou un saut absent : le contrôle tombe",
      not le_controle({"les_surfaces": [surf(3, "faux : deux tours", False)]}, s)
      and not le_controle({"les_surfaces": [surf(9, "juste", False)]}, s))

    def d_(ps, pa, ns=40, na=40, ctl=True):
        b_ = {"les_sains": {"les_sauts": ns, "les_tenus": round(ps * ns), "la_part": ps},
              "les_autres": {"les_sauts": na, "les_tenus": round(pa * na), "la_part": pa}}
        return {"le_controle": ctl, "les_bilans": {"graines_4_a_8": {"les_deux": b_}}}
    v("★★★★ les trois quarts des sains et un quart des autres : ils les séparent, bornes comprises",
      le_verdict(d_(0.75, 0.25))["lissue"].endswith("ils les séparent"))
    v("★★★★ un écart sous 25 points : ils ne les séparent pas", le_verdict(d_(0.7, 0.5))["lissue"].endswith("ils ne les séparent pas"))
    v("★★★ sinon : en partie", le_verdict(d_(0.9, 0.3))["lissue"].endswith("qu'en partie")
      and le_verdict(d_(0.7, 0.2))["lissue"].endswith("qu'en partie"))
    v("★★★ moins de 5 d'un côté : indécidable", not le_verdict(d_(1.0, 0.0, ns=4))["decidable"]
      and not le_verdict(d_(1.0, 0.0, na=4))["decidable"] and le_verdict(d_(1.0, 0.0, 5, 5))["decidable"])
    v("★★★ le contrôle tombé : indécidable", not le_verdict(d_(1.0, 0.0, ctl=False))["decidable"])

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
