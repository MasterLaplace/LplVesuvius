"""Sur PHerc0358, les sauts des chaînes de la graine 8 sont-ils à cheval, un quart au moins de leurs points à plus d'un demi-pas de l'écart médian du saut, plus souvent que ceux des graines 6 et 7 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT NE SOIT JUGÉ À CHEVAL. Ce qui était vu avant d'écrire : tout ce que `296` à `377` publient,
dont `R4-F563` (sur la graine 8, la nappe de départ de la tierce, regrandie depuis un point de la nappe de la suivie, est à cheval : 44 %
des points de la suivie en face d'elle au loin ; la suivie et la compagne partent de la même feuille et leurs comptes s'écartent quand
même). Et, lu dans ce que `369` publie : sur la graine 8, côté moins, le deuxième saut de la compagne est nul, 0,751 voxel, et son
huitième double, 32,052 voxels ; côté plus, son cinquième s'écarte de 26,579 voxels.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P175`. Chaque surface d'une chaîne est regrandie à chaque saut. Si une nappe regrandie peut se
mettre à cheval sur deux feuilles, une surface aussi : une part de ses points sur la feuille suivante, une autre restée ou passée plus
loin. Le compte d'un saut est lu sur sa médiane ; une surface à cheval fait prendre à la chaîne suivante un départ mêlé.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373`, rejouées par sa fonction ; l'écart médian de chacun de leurs sauts doit redonner celui que
  `369` publie pour la suivie et la compagne, et `373` pour la tierce.
- **Chaque saut** : les points de sa surface qui ont en face la surface d'où il part, la nappe pour le premier, au latéral de `368` et à
  trois pas au plus, comme `369` ; lu si 50 points au moins sont en face. Sa **part à cheval** est la part de ces points dont l'écart
  s'éloigne de plus d'un demi-pas, 10 voxels, de l'écart médian du saut. Le saut est **à cheval** si cette part atteint un quart.
- **Les groupes** : les sauts lus de la graine 8, sur ses deux côtés, et ceux des graines 6 et 7.
- **La règle** : si au moins la moitié des sauts lus de la graine 8 sont à cheval et au plus 10 % de ceux des graines 6 et 7, **oui** ; si
  la part de la graine 8 ne dépasse pas celle des graines 6 et 7, **non** ; sinon, **en partie**. Indécidable sous 10 sauts lus dans l'un
  des groupes, ou si les écarts médians ne redonnent pas `369` et `373`.

## Les issues

L'issue de la tranche : **n des m sauts lus de la graine 8 sont à cheval, contre n' des m' sur les graines 6 et 7**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Chaîne par chaîne et côté par côté, les sauts à cheval et leur part à cheval.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, sur une surface, elle passe d'une feuille à l'autre, ni si retirer les sauts à cheval ferait
s'accorder les chaînes de la graine 8.

Usage :
    uv run python src/nappe/les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.py --verifier
    uv run python src/nappe/les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.py \\
        --json docs/mesures/les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.json
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
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_373_A_PUBLIE = LES_MESURES / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
LE_DEMI_PAS = m368.LE_PAS / 2.0
LA_PORTEE = m369.LA_PORTEE
LE_MINIMUM_EN_FACE = m368.LE_MINIMUM_EN_FACE
LA_PART_A_CHEVAL = 0.25
LE_MINIMUM = 10
LA_GRAINE = 8


def le_saut(surface, depart, lateral: float = m368.LE_LATERAL, portee: float = LA_PORTEE) -> dict:
    """Les points de la surface qui ont en face celle d'où elle part, leur écart médian absolu comme `369` le mesure, la part de ceux qui
    s'en éloignent de plus d'un demi-pas, et si le saut est à cheval ; non lu sous le minimum de points en face."""
    import numpy as np

    if surface is None or depart is None or not len(surface[0]) or not len(depart[0]):
        return {"en_face": 0, "lecart_median": None, "la_part_a_cheval": None, "a_cheval": None}
    e = m321.les_ecarts(surface[0], surface[1], depart[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= portee)
    x = np.abs(e[vus])
    med = round(float(np.median(x)), 3) if len(x) else None
    if len(x) < LE_MINIMUM_EN_FACE:
        return {"en_face": int(len(x)), "lecart_median": med, "la_part_a_cheval": None, "a_cheval": None}
    part = round(float((np.abs(x - np.median(x)) > LE_DEMI_PAS).mean()), 4)
    return {"en_face": int(len(x)), "lecart_median": med, "la_part_a_cheval": part, "a_cheval": bool(part >= LA_PART_A_CHEVAL)}


def les_sauts(nappe, surfaces: list, mesurer_=le_saut) -> list[dict]:
    """Chaque saut d'une chaîne, depuis la nappe pour le premier, depuis la surface précédente ensuite."""
    out, avant = [], nappe
    for h, s in enumerate(surfaces, 1):
        out.append({"le_saut": h, **mesurer_(s, avant)})
        avant = s
    return out


def le_bilan(cotes: list[dict]) -> dict:
    def compte(garder):
        lus = [s for c in cotes if garder(c["le_rang"]) for x in c["les_chaines"].values() for s in x if s["a_cheval"] is not None]
        return {"lus": len(lus), "a_cheval": sum(s["a_cheval"] for s in lus)}
    return {"la_graine_8": compte(lambda r: r == LA_GRAINE), "les_temoins": compte(lambda r: r != LA_GRAINE)}


def le_verdict(d: dict) -> dict:
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les écarts médians des sauts ne redonnent pas 369 et 373"}
    b = d["le_bilan"]
    g, t = b["la_graine_8"], b["les_temoins"]
    if g["lus"] < LE_MINIMUM or t["lus"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {g['lus']} sauts lus sur la graine 8 et {t['lus']} sur les graines 6 et 7"}
    tete = f"{g['a_cheval']} des {g['lus']} sauts lus de la graine 8 sont à cheval, contre {t['a_cheval']} des {t['lus']} sur les graines 6 et 7"
    p8, pt = g["a_cheval"] / g["lus"], t["a_cheval"] / t["lus"]
    suite = "oui" if p8 >= 0.5 and pt <= 0.1 else "non" if p8 <= pt else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    m369._LES_CHAINES.clear()
    m373._LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m373.le_chaineur())
    p369, p373 = json.loads(CE_QUE_369_A_PUBLIE.read_text()), json.loads(CE_QUE_373_A_PUBLIE.read_text())
    cotes, redonne = [], True
    for c, pc, nap, pt, q9, q3 in zip(chaines, m368._LES_PAIRES_DE_CHAINES, m369._LES_CHAINES, m373._LES_TIERCES, p369["les_cotes"],
                                      p373["les_cotes"]):
        redonne &= (c["le_rang"], c["le_cote"]) == (q9["le_rang"], q9["le_cote"]) == (q3["le_rang"], q3["le_cote"])
        ch = {SUIVIE: les_sauts(nap["la_nappe"], pc["suivie"]), COMPAGNE: les_sauts(nap["la_nappe_compagne"], pc["compagne"]),
              TIERCE: les_sauts(pt["la_nappe"], pt["tierce"])}
        pub = {SUIVIE: q9["suivie"], COMPAGNE: q9["compagne"], TIERCE: q3["les_sauts_de_la_tierce"]}
        for k in ch:
            redonne &= [s["lecart_median"] for s in ch[k]] == [s["lecart_median"] for s in pub[k]]
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_chaines": ch})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne),
                          "a_cheval": {k: [s["le_saut"] for s in v if s["a_cheval"]] for k, v in ch.items()}}), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_demi_pas": LE_DEMI_PAS, "la_portee": LA_PORTEE, "le_minimum_en_face": LE_MINIMUM_EN_FACE,
                            "la_part_a_cheval": LA_PART_A_CHEVAL, "le_minimum": LE_MINIMUM},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne": bool(redonne) and len(cotes) == 5, "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
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

    g = np.stack(np.meshgrid(np.arange(0.0, 400.0, 40.0), np.arange(0.0, 400.0, 40.0)), -1).reshape(-1, 2)
    plan = lambda z: (np.c_[g, z if np.ndim(z) else np.full(len(g), z)], np.tile([0.0, 0.0, 1.0], (len(g), 1)))  # noqa: E731
    haut = np.full(len(g), 15.0)
    haut[g[:, 0] < 120.0] = 30.0
    r = le_saut(plan(0.0), plan(haut), lateral=0.5)
    v("★★★★ un saut à cheval : 30 % des points à un pas de plus que la médiane",
      r == {"en_face": 100, "lecart_median": 15.0, "la_part_a_cheval": 0.3, "a_cheval": True}, str(r))
    h2 = np.full(len(g), 15.0)
    h2[g[:, 0] < 80.0] = 24.0
    v("★★★★ un écart de 9 voxels à la médiane n'est pas à cheval, et un quart pile l'est",
      lambda: le_saut(plan(0.0), plan(h2), lateral=0.5)["la_part_a_cheval"] == 0.0
      and le_saut(plan(0.0), plan(np.where(np.arange(len(g)) < 25, 2.0, 15.0)), lateral=0.5)["a_cheval"] is True
      and le_saut(plan(0.0), plan(np.where(np.arange(len(g)) < 24, 2.0, 15.0)), lateral=0.5)["a_cheval"] is False)
    v("★★★★ vu à trois pas, pas au-delà",
      lambda: le_saut(plan(0.0), plan(55.0), lateral=0.5)["lecart_median"] == 55.0
      and le_saut(plan(0.0), plan(65.0), lateral=0.5)["a_cheval"] is None)
    peu = (plan(0.0)[0][:49], plan(0.0)[1][:49])
    v("★★★ non lu sous 50 points en face, mais son écart médian gardé ; rien sans surface",
      lambda: le_saut(peu, plan(15.0), lateral=0.5) == {"en_face": 49, "lecart_median": 15.0, "la_part_a_cheval": None, "a_cheval": None}
      and le_saut(None, plan(1.0))["a_cheval"] is None)
    ss = les_sauts("n", ["a", "b", "c"], mesurer_=lambda s, d: {"de": d, "a": s})
    v("★★★★ les sauts : le premier depuis la nappe, les suivants depuis la surface précédente",
      [(x["le_saut"], x["de"], x["a"]) for x in ss] == [(1, "n", "a"), (2, "a", "b"), (3, "b", "c")], str(ss))
    s_ = lambda *xs: [{"a_cheval": x} for x in xs]  # noqa: E731
    c_ = lambda r, **k: {"le_rang": r, "les_chaines": k}  # noqa: E731
    b_ = lambda: le_bilan([c_(8, suivie=s_(True, None, False), compagne=s_(True)), c_(6, suivie=s_(False, True)),  # noqa: E731
                           c_(7, tierce=s_(None, False))])
    v("★★★★ le bilan : sauts lus et à cheval sur la graine 8 et sur les graines 6 et 7",
      lambda: b_() == {"la_graine_8": {"lus": 3, "a_cheval": 2}, "les_temoins": {"lus": 3, "a_cheval": 1}})

    def d_(n8, l8, nt, lt, ok=True):
        return {"redonne": ok, "le_bilan": {"la_graine_8": {"lus": l8, "a_cheval": n8}, "les_temoins": {"lus": lt, "a_cheval": nt}}}
    v("★★★★ la règle : la moitié à la graine 8 et 10 % aux témoins oui ; pas plus qu'aux témoins non ; sinon en partie",
      le_verdict(d_(10, 20, 2, 20))["lissue"].endswith("; oui") and le_verdict(d_(10, 20, 3, 20))["lissue"].endswith("; en partie")
      and le_verdict(d_(9, 20, 2, 20))["lissue"].endswith("; en partie") and le_verdict(d_(4, 20, 4, 20))["lissue"].endswith("; non")
      and le_verdict(d_(5, 20, 4, 20))["lissue"].endswith("; en partie"))
    v("★★★ indécidable sous 10 sauts lus dans un groupe, ou sans redonne",
      not le_verdict(d_(5, 9, 1, 20))["decidable"] and not le_verdict(d_(5, 20, 1, 9))["decidable"]
      and not le_verdict(d_(10, 20, 1, 20, ok=False))["decidable"] and le_verdict(d_(5, 10, 1, 10))["decidable"])

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
