"""Au saut où le retard naît, un seuil de points que le compte de 345 dit à zéro feuille refuse-t-il ces sauts sans refuser les sauts justes qui ne sont pas à cheval ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE NOMBRE DE POINTS COMPTÉS À ZÉRO NE SOIT RAPPROCHÉ, SAUT PAR SAUT, DE LA NAISSANCE DU RETARD. Ce
qui était vu avant d'écrire : tout ce que `296` à `350` publient, dont `R4-F535` (60 des 104 sauts justes des graines 4 à 8 donnent une
surface à cheval, et des 8963 points restés sous elles 2275 sont comptés à zéro par `345`) et `R4-F536` (le retard naît au premier saut à
cheval de chaque chaîne et de chaque graine, puis il s'hérite). Les comptes de `345` sont publiés saut par saut ; ceux de la chaîne
bornée, graine 8, ont été lus en passant pour `348` (32 points à zéro au deuxième et au troisième saut, 49 au quatrième).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P147`. Là où le retard naît, un morceau de la surface reste sur la feuille de départ, et
le compte de `345` peut le voir comme des points qui ne franchissent aucune feuille. Le critère de `345` ne le voit pas : il demande que
les trois quarts des points comptés franchissent une feuille, et un morceau resté en arrière n'en fait qu'une petite part. Un seuil sur le
**nombre** de points restés, lui, ne dépend pas de la taille de la surface, et un rouleau sans tracé peut le compter.

## Ce qui est fait

- **Aucune mesure neuve** : tout vient de ce que `345`, `349` et `350` publient, rapproché saut par saut par la chaîne, la graine, le
  côté et le numéro du saut.
- **Les points à zéro d'un saut** : le nombre de ses points que le compte de `345` dit ne franchir aucune feuille.
- **Le critère** : un saut est **refusé** s'il a au moins 50 points à zéro, le même nombre qui, par le référent, fait une surface à cheval
  dans `349` ; il est tenu sinon.
- **Les naissances** : le premier saut à cheval de chaque chaîne et de chaque graine des graines 4 à 8, que `350` publie.
- **Les sauts sains** : les sauts justes des graines 4 à 8 que `349` lit et ne dit pas à cheval.
- **Le contrôle** : sous chaque surface que `349` lit, les points restés que `349` dit à zéro sont des points à zéro du saut ; leur nombre
  ne doit jamais dépasser celui que `345` publie pour le saut, et chaque saut cherché doit être trouvé dans `345` ; sinon la tranche est
  indécidable.
- **La règle** : celle de `344`, avec les naissances à la place des sauts faux : si le critère refuse au moins 75 % des naissances et au
  plus 25 % des sauts sains, **il les sépare** ; si l'écart entre les deux parts est sous 25 points, **il ne les sépare pas** ; sinon,
  **en partie**. Indécidable sous 5 naissances ou 5 sauts sains.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, un seuil de 50 points à zéro refuse a des n naissances du retard et b des m sauts justes
sains**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La même chose pour d'autres seuils, de 10 à 150 points ; les sauts justes à cheval qui ne sont pas des naissances ; les sauts faux ; et,
sous les naissances, la part des points restés que `349` dit à zéro.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut le seuil sur PHerc0358, où une surface peut être plus grande ou plus petite ; et si un
saut refusé à sa naissance aurait donné, relancé, une surface qui n'est pas à cheval.

Usage :
    uv run python src/nappe/un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.py --verifier
    uv run python src/nappe/un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.py \\
        --json docs/mesures/un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.json
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
CE_QUE_350_A_PUBLIE = LES_MESURES / "le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.json"

LE_SEUIL = 50
LES_SEUILS_RAPPORTES = (10, 20, 30, 40, 50, 75, 100, 150)
LA_TENUE_DES_NAISSANCES = 0.75
LA_TENUE_DES_SAINS = 0.25
LECART_MINIMAL = 0.25
LE_MINIMUM = 5


def les_zeros(d345: dict) -> dict:
    """Pour chaque saut que `345` publie, par (chaîne, graine, côté, saut), le nombre de ses points que le compte dit à zéro feuille."""
    return {(n, g["le_rang"], c, s["le_saut"]): s["les_feuilles"]["les_comptes"].get("0", 0)
            for n, ch in d345["les_chaines"].items() for g in ch["les_graines"] for c, x in g["les_cotes"].items() for s in x["les_sauts"]}


def la_cle(s: dict) -> tuple:
    return (s["la_chaine"], s["le_rang"], s["le_cote"], s["le_saut"])


def les_groupes(d349: dict, d350: dict) -> dict:
    """Les naissances du retard, les sauts justes sains, les sauts justes à cheval hérités, et les sauts faux, sur les graines 4 à 8."""
    naissances = {(p["la_chaine"], p["le_rang"], p["le_cote"], p["le_premier_saut"]) for p in d350["les_premiers"] if p["le_rang"] >= 4}
    lus = [s for s in d349["les_surfaces"] if s["le_rang"] >= 4 and s["la_surface"] is not None]
    return {"les_naissances": sorted(naissances),
            "les_sains": sorted(la_cle(s) for s in lus if s["la_justesse"] == "juste" and not s["la_surface"]["a_cheval"]),
            "les_herites": sorted(la_cle(s) for s in lus if s["la_justesse"] == "juste" and s["la_surface"]["a_cheval"]
                                  and la_cle(s) not in naissances),
            "les_faux": sorted(la_cle(s) for s in lus if s["la_justesse"].startswith("faux"))}


def le_bilan(cles: list, zeros: dict, seuil: int = LE_SEUIL) -> dict:
    refus = sum(1 for k in cles if zeros[k] >= seuil)
    return {"les_sauts": len(cles), "les_refuses": refus, "la_part": round(refus / len(cles), 4) if cles else None}


def le_controle(d349: dict, zeros: dict, groupes: dict) -> bool:
    """Chaque saut cherché est dans `345`, et sous chaque surface de `349` les points restés à zéro ne dépassent pas les points à zéro."""
    if any(k not in zeros for g in groupes.values() for k in g):
        return False
    return all(s["la_surface"]["restes"]["les_comptes"].get("0", 0) <= zeros.get(la_cle(s), -1)
               for s in d349["les_surfaces"] if s["la_surface"] is not None)


def le_verdict(d: dict) -> dict:
    if not d["le_controle"]:
        return {"decidable": False, "lissue": "indécidable : les sauts de 349 et 350 ne se retrouvent pas dans 345"}
    n, s = d["les_bilans"]["les_naissances"], d["les_bilans"]["les_sains"]
    if n["les_sauts"] < LE_MINIMUM or s["les_sauts"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {n['les_sauts']} naissances et {s['les_sauts']} sauts sains"}
    tete = (f"sur les graines 4 à 8, un seuil de {LE_SEUIL} points à zéro refuse {n['les_refuses']} des {n['les_sauts']} naissances du "
            f"retard et {s['les_refuses']} des {s['les_sauts']} sauts justes sains")
    if n["la_part"] >= LA_TENUE_DES_NAISSANCES and s["la_part"] <= LA_TENUE_DES_SAINS:
        suite = "il les sépare"
    elif n["la_part"] - s["la_part"] < LECART_MINIMAL:
        suite = "il ne les sépare pas"
    else:
        suite = "il ne les sépare qu'en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d345, d349, d350 = (json.loads(p.read_text()) for p in (CE_QUE_345_A_PUBLIE, CE_QUE_349_A_PUBLIE, CE_QUE_350_A_PUBLIE))
    zeros = les_zeros(d345)
    groupes = les_groupes(d349, d350)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_seuil": LE_SEUIL, "la_tenue_des_naissances": LA_TENUE_DES_NAISSANCES,
                            "la_tenue_des_sains": LA_TENUE_DES_SAINS, "lecart_minimal": LECART_MINIMAL, "le_minimum": LE_MINIMUM},
         "le_controle": le_controle(d349, zeros, groupes),
         "les_groupes": {k: [list(x) for x in v] for k, v in groupes.items()}}
    if d["le_controle"]:
        d["les_bilans"] = {k: le_bilan(v, zeros) for k, v in groupes.items()}
        d["par_seuil"] = {str(t): {k: le_bilan(v, zeros, t) for k, v in groupes.items()} for t in LES_SEUILS_RAPPORTES}
        d["les_zeros"] = {k: [zeros[x] for x in v] for k, v in groupes.items()}
        nes = [s for s in d349["les_surfaces"] if la_cle(s) in set(groupes["les_naissances"]) and s["la_surface"] is not None]
        d["les_restes_des_naissances"] = {"les_points": sum(s["la_surface"]["restes"]["les_points"] for s in nes),
                                          "a_zero": sum(s["la_surface"]["restes"]["les_comptes"].get("0", 0) for s in nes)}
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

    def saut(k, z, j="juste"):
        return {"le_saut": k, "la_justesse": j, "les_feuilles": {"les_comptes": {"0": z, "1": 500} if z else {"1": 500}}}
    d345 = {"les_chaines": {"bornée": {"les_graines": [{"le_rang": 8, "les_cotes": {"moins": {"les_sauts": [
        saut(1, 0), saut(2, 80), saut(3, 10), saut(4, 60, "faux : deux tours")]}}}]}}}
    z = les_zeros(d345)
    v("★★★★ les points à zéro, saut par saut, et zéro quand le compte n'en dit aucun",
      z == {("bornée", 8, "moins", 1): 0, ("bornée", 8, "moins", 2): 80, ("bornée", 8, "moins", 3): 10, ("bornée", 8, "moins", 4): 60}, str(z))

    def surf(k, j, cheval, zr=0, rang=8):
        return {"la_chaine": "bornée", "le_rang": rang, "le_cote": "moins", "le_saut": k, "la_justesse": j,
                "la_surface": {"a_cheval": cheval, "restes": {"les_comptes": {"0": zr}}}}
    d349 = {"les_surfaces": [surf(1, "juste", False), surf(2, "juste", True, 20), surf(3, "juste", True), surf(4, "faux : deux tours", True),
                             surf(2, "juste", True, rang=2), {**surf(5, "juste", False), "la_surface": None}]}
    d350 = {"les_premiers": [{"la_chaine": "bornée", "le_rang": 8, "le_cote": "moins", "le_premier_saut": 2},
                             {"la_chaine": "bornée", "le_rang": 2, "le_cote": "moins", "le_premier_saut": 2}]}
    g = les_groupes(d349, d350)
    v("★★★★ naissance, sains, hérités et faux, sur les graines 4 à 8 seulement, sans les surfaces non lues",
      g == {"les_naissances": [("bornée", 8, "moins", 2)], "les_sains": [("bornée", 8, "moins", 1)],
            "les_herites": [("bornée", 8, "moins", 3)], "les_faux": [("bornée", 8, "moins", 4)]}, str(g))
    v("★★★★ le critère : au moins 50 points à zéro, borne comprise",
      le_bilan([("bornée", 8, "moins", 2), ("bornée", 8, "moins", 3)], z) == {"les_sauts": 2, "les_refuses": 1, "la_part": 0.5}
      and le_bilan([("x",)], {("x",): 50})["les_refuses"] == 1 and le_bilan([("x",)], {("x",): 49})["les_refuses"] == 0)
    v("★★★ le contrôle tient quand les restés à zéro ne dépassent pas les points à zéro du saut", le_controle(
        {"les_surfaces": [s for s in d349["les_surfaces"] if s["le_rang"] >= 4]}, z, g))
    trop = {"les_surfaces": [surf(3, "juste", True, 11)]}
    v("★★★★ des restés à zéro plus nombreux que les points à zéro du saut : le contrôle tombe", not le_controle(trop, z, g))
    v("★★★★ un saut cherché absent de 345 : le contrôle tombe",
      not le_controle({"les_surfaces": []}, z, dict(g, les_sains=[("bornée", 8, "moins", 9)])))

    def d_(pn, ps, n=8, s_=40, ctl=True):
        return {"le_controle": ctl, "les_bilans": {"les_naissances": {"les_sauts": n, "les_refuses": round(pn * n), "la_part": pn},
                                                   "les_sains": {"les_sauts": s_, "les_refuses": round(ps * s_), "la_part": ps}}}
    v("★★★★ les trois quarts des naissances et un quart des sains : il les sépare, bornes comprises",
      le_verdict(d_(0.75, 0.25))["lissue"].endswith("il les sépare"))
    v("★★★★ un écart sous 25 points : il ne les sépare pas", le_verdict(d_(0.6, 0.4))["lissue"].endswith("il ne les sépare pas"))
    v("★★★ sinon : en partie", le_verdict(d_(0.7, 0.2))["lissue"].endswith("qu'en partie")
      and le_verdict(d_(0.9, 0.3))["lissue"].endswith("qu'en partie"))
    v("★★★ moins de 5 naissances ou de 5 sains : indécidable", not le_verdict(d_(1.0, 0.0, n=4))["decidable"]
      and not le_verdict(d_(1.0, 0.0, s_=4))["decidable"] and le_verdict(d_(1.0, 0.0, n=5, s_=5))["decidable"])
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
