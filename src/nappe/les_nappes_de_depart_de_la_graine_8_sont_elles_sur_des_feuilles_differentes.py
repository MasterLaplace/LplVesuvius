"""Sur PHerc0358, graine 8, les nappes de départ des trois chaînes sont-elles sur des feuilles différentes, à autant de tours que l'écart de leurs comptes au premier saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE NAPPE NE SOIT COMPARÉE À UNE AUTRE. Ce qui était vu avant d'écrire : tout ce que `296` à
`376` publient, dont `R4-F562` (là où les comptes des chaînes de la graine 8 s'écartent, la somme des écarts de leurs sauts s'écarte avec
eux, toujours dans leur sens ; sur la graine 8, côté moins, la deuxième et la troisième surface de la suivie sont toutes deux sur la même
feuille que la première de la compagne). Et, lu dans ce que `368` et `373` publient : les graines compagne et tierce d'une graine sont les
mêmes pour ses deux côtés ; sur la graine 8, la compagne part de (5166,53 ; 4753,32 ; 11267,7) et la tierce, posée en diagonale, de
(5101,53 ; 4775,67 ; 11541,96).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P174`. La graine compagne et la graine tierce sont des points de la nappe de la suivie, mais
leurs nappes sont regrandies depuis ces points. Si l'une a glissé sur une autre feuille en grandissant, sa chaîne compte ses tours depuis
une autre feuille, et ses comptes s'écartent de ceux de la suivie dès le premier saut, sans qu'aucun saut ne soit faux.

## Ce qui est fait

- **Les nappes** : celles des trois chaînes de `373`, rejouées par sa fonction ; les graines compagne et tierce doivent redonner celles que
  `368` et `373` publient, et les comptes corrigés de la tierce ceux de `373`.
- **Chaque couple de nappes** d'une graine, la suivie et la compagne, la suivie et la tierce, la compagne et la tierce : les points de la
  première qui ont la seconde en face, au latéral de `368` et à trois pas au plus, comme `369` mesure ses sauts ; la médiane de leurs écarts
  absolus et la part de ceux à plus d'un demi-pas. Lu si 50 points au moins sont en face ; **sur des feuilles différentes** si la médiane
  dépasse le quart de pas de `368`, 5 voxels, comme le juge de feuille de `367`.
- **Le contrôle** : sur les graines 6 et 7, où les trois chaînes tiennent la plupart de leurs comptes, chaque couple lu de nappes est sur
  la même feuille, et chaque graine en a au moins un de lu.
- **La règle** : si au moins 2 des 3 couples de nappes de la graine 8 sont sur des feuilles différentes, **oui** ; si 1, **en partie** ;
  si aucun, **non**. Indécidable sous 2 couples lus sur la graine 8, si le contrôle échoue, si les deux côtés d'une graine ne partent pas
  des mêmes nappes, ou si les graines et la tierce ne redonnent pas `368` et `373`.

## Les issues

L'issue de la tranche : **sur la graine 8, n des c couples de nappes lus sont sur des feuilles différentes, contre n' des c' sur les
graines 6 et 7**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Couple par couple, l'écart médian des nappes en sauts simples médians de `369`, et, côté par côté, l'écart de comptes de la première
paire « même feuille » que `375` publie pour ce couple.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, sur une nappe, elle passe d'une feuille à l'autre, ni si les surfaces des chaînes sont à cheval
sur deux feuilles.

Usage :
    uv run python src/nappe/les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.py --verifier
    uv run python src/nappe/les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.py \\
        --json docs/mesures/les_nappes_de_depart_de_la_graine_8_sont_elles_sur_des_feuilles_differentes.json
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
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_373_A_PUBLIE = LES_MESURES / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
CE_QUE_375_A_PUBLIE = LES_MESURES / "les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.json"
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
LES_COUPLES = ((SUIVIE, COMPAGNE), (SUIVIE, TIERCE), (COMPAGNE, TIERCE))
LE_QUART = m368.LE_QUART
LE_DEMI_PAS = m368.LE_PAS / 2.0
LA_PORTEE = m369.LA_PORTEE
LE_MINIMUM_EN_FACE = m368.LE_MINIMUM_EN_FACE
LE_MINIMUM_DE_COUPLES = 2
LES_TEMOINS = (6, 7)
LA_GRAINE = 8


def la_comparaison(a, b, lateral: float = m368.LE_LATERAL, portee: float = LA_PORTEE) -> dict:
    """Les points de la nappe `a` qui ont la nappe `b` en face, la médiane de leurs écarts absolus, la part de ceux à plus d'un demi-pas,
    et si les deux sont sur des feuilles différentes ; non lue sous le minimum de points en face."""
    import numpy as np

    if a is None or b is None or not len(a[0]) or not len(b[0]):
        return {"en_face": 0, "lecart_median": None, "la_part_lointaine": None, "differentes": None}
    e = m321.les_ecarts(a[0], a[1], b[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= portee)
    x = np.abs(e[vus])
    if len(x) < LE_MINIMUM_EN_FACE:
        return {"en_face": int(len(x)), "lecart_median": None, "la_part_lointaine": None, "differentes": None}
    med = round(float(np.median(x)), 3)
    return {"en_face": int(len(x)), "lecart_median": med, "la_part_lointaine": round(float((x > LE_DEMI_PAS).mean()), 4),
            "differentes": bool(med > LE_QUART)}


def les_couples(nappes: dict, comparer=la_comparaison) -> dict:
    return {f"{a}|{b}": comparer(nappes[a], nappes[b]) for a, b in LES_COUPLES}


def la_premiere_paire(paires: list[dict], rang: int, cote: str, couple: str) -> dict | None:
    """La paire « même feuille » de `375` de ce couple, sur ce côté, aux sauts les plus proches de la nappe."""
    ps = [p for p in paires if (p["le_rang"], p["le_cote"], p["le_couple"]) == (rang, cote, couple)]
    return min(ps, key=lambda p: (sum(p["les_sauts"]), p["les_sauts"]), default=None)


def le_bilan(graines: dict) -> dict:
    def compte(rangs):
        lus = [c for r in rangs for c in graines.get(r, {}).values() if c["differentes"] is not None]
        return {"lus": len(lus), "differentes": sum(c["differentes"] for c in lus)}

    temoins = compte(LES_TEMOINS)
    controle = temoins["differentes"] == 0 and all(compte((r,))["lus"] >= 1 for r in LES_TEMOINS)
    return {"la_graine_8": compte((LA_GRAINE,)), "les_temoins": temoins, "le_controle": bool(controle)}


def le_verdict(d: dict) -> dict:
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les graines ou la tierce ne redonnent pas 368 et 373"}
    if not d.get("les_memes_nappes"):
        return {"decidable": False, "lissue": "indécidable : les deux côtés d'une graine ne partent pas des mêmes nappes"}
    b = d["le_bilan"]
    g, t = b["la_graine_8"], b["les_temoins"]
    if g["lus"] < LE_MINIMUM_DE_COUPLES:
        return {"decidable": False, "lissue": f"indécidable : {g['lus']} couples de nappes lus sur la graine 8"}
    if not b["le_controle"]:
        return {"decidable": False, "lissue": f"indécidable : sur les graines 6 et 7, {t['differentes']} des {t['lus']} couples de nappes "
                                              "lus sont sur des feuilles différentes, le contrôle échoue"}
    tete = (f"sur la graine 8, {g['differentes']} des {g['lus']} couples de nappes lus sont sur des feuilles différentes, contre "
            f"{t['differentes']} des {t['lus']} sur les graines 6 et 7")
    n = g["differentes"]
    return {"decidable": True, "lissue": f"{tete} ; {'oui' if n >= 2 else 'en partie' if n == 1 else 'non'}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    m369._LES_CHAINES.clear()
    m373._LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m373.le_chaineur())
    p368, p369, p373, p375 = (json.loads(x.read_text()) for x in (CE_QUE_368_A_PUBLIE, CE_QUE_369_A_PUBLIE, CE_QUE_373_A_PUBLIE,
                                                                   CE_QUE_375_A_PUBLIE))
    saut = p369["lecart_median_des_sauts_simples"]
    cotes, graines, redonne, memes = [], {}, True, True
    for c, pc, nap, pt, q3, q8 in zip(chaines, m368._LES_PAIRES_DE_CHAINES, m369._LES_CHAINES, m373._LES_TIERCES, p373["les_cotes"],
                                      p368["les_cotes"]):
        redonne &= (c["le_rang"], c["le_cote"]) == (q3["le_rang"], q3["le_cote"]) == (q8["le_rang"], q8["le_cote"])
        redonne &= pc["la_graine_compagne"] == q8["la_graine_compagne"] and pt["la_graine_tierce"] == q3["la_graine_tierce"]
        redonne &= [s["le_compte_corrige"] for s in m369.les_sauts(pt["la_nappe"], pt["tierce"])] == \
            [s["le_compte_corrige"] for s in q3["les_sauts_de_la_tierce"]]
        nappes = {SUIVIE: nap["la_nappe"], COMPAGNE: nap["la_nappe_compagne"], TIERCE: pt["la_nappe"]}
        couples = les_couples(nappes)
        for cle, v in couples.items():
            v["en_sauts"] = None if v["lecart_median"] is None else round(v["lecart_median"] / saut, 3)
            q = la_premiere_paire(p375["les_paires"], c["le_rang"], c["le_cote"], cle)
            v["la_premiere_paire"] = None if q is None else {"les_sauts": q["les_sauts"], "lecart_de_comptes": q["lecart_de_comptes"]}
        if c["le_rang"] in graines:
            avant = graines[c["le_rang"]]
            memes &= all({k: v[k] for k in ("en_face", "lecart_median")} == {k: avant[cle][k] for k in ("en_face", "lecart_median")}
                         for cle, v in couples.items())
        else:
            graines[c["le_rang"]] = couples
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_couples": couples})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne),
                          "differentes": {k: v["differentes"] for k, v in couples.items()}}), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_quart": LE_QUART, "le_demi_pas": LE_DEMI_PAS, "la_portee": LA_PORTEE, "le_saut": saut,
                            "le_minimum_en_face": LE_MINIMUM_EN_FACE, "le_minimum_de_couples": LE_MINIMUM_DE_COUPLES},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne": bool(redonne) and len(cotes) == 5, "les_memes_nappes": bool(memes), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(graines)
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
    nappe = lambda z: (np.c_[g, np.full(len(g), z)], np.tile([0.0, 0.0, 1.0], (len(g), 1)))  # noqa: E731
    haut = np.full(len(g), 16.0)
    haut[g[:, 0] < 160.0] = 1.0
    a, b = nappe(0.0), (np.c_[g, haut], None)
    r = la_comparaison(a, b, lateral=0.5)
    v("★★★★ la comparaison : médiane au-delà du quart de pas, 60 % au loin, sur des feuilles différentes",
      r == {"en_face": 100, "lecart_median": 16.0, "la_part_lointaine": 0.6, "differentes": True}, str(r))
    v("★★★★ une nappe à 45 voxels est vue à trois pas, pas à un pas et demi",
      lambda: la_comparaison(a, nappe(45.0), lateral=0.5)["lecart_median"] == 45.0
      and la_comparaison(a, nappe(45.0), lateral=0.5, portee=30.0)["differentes"] is None)
    v("★★★ la part lointaine compte au-delà d'un demi-pas, pas au-delà du quart",
      lambda: la_comparaison(a, nappe(7.0), lateral=0.5)["la_part_lointaine"] == 0.0
      and la_comparaison(a, nappe(10.5), lateral=0.5)["la_part_lointaine"] == 1.0)
    v("★★★★ au quart de pas exactement, sur la même feuille ; au-delà, différentes",
      lambda: la_comparaison(a, nappe(5.0), lateral=0.5)["differentes"] is False
      and la_comparaison(a, nappe(5.001), lateral=0.5)["differentes"] is True)
    peu = (a[0][:49], a[1][:49])
    v("★★★ non lue sous 50 points en face, ou sans nappe", lambda: la_comparaison(peu, nappe(1.0), lateral=0.5)["differentes"] is None
      and la_comparaison(a, nappe(1.0), lateral=0.5)["en_face"] == 100
      and la_comparaison(None, nappe(1.0))["differentes"] is None)
    cs = les_couples({SUIVIE: 1, COMPAGNE: 2, TIERCE: 3}, comparer=lambda x, y: (x, y))
    v("★★★ les couples : la suivie et la compagne, la suivie et la tierce, la compagne et la tierce",
      cs == {"suivie|compagne": (1, 2), "suivie|tierce": (1, 3), "compagne|tierce": (2, 3)}, str(cs))
    ps = [{"le_rang": 8, "le_cote": "moins", "le_couple": "suivie|compagne", "les_sauts": s, "lecart_de_comptes": e}
          for s, e in (([3, 1], 2), ([2, 1], 1), ([1, 3], 2), ([8, 7], 2))]
    v("★★★ la première paire : les sauts les plus proches de la nappe, égalités à la première suivie",
      la_premiere_paire(ps, 8, "moins", "suivie|compagne")["les_sauts"] == [2, 1]
      and la_premiere_paire(ps[:1] + ps[2:], 8, "moins", "suivie|compagne")["les_sauts"] == [1, 3]
      and la_premiere_paire(ps, 8, "plus", "suivie|compagne") is None)
    c_ = lambda *ds: {f"k{i}": {"differentes": x} for i, x in enumerate(ds)}  # noqa: E731
    b_ = lambda: le_bilan({6: c_(False, False, None), 7: c_(False, True, False), 8: c_(True, None, False)})  # noqa: E731
    v("★★★★ le bilan : couples lus et différents sur la graine 8, sur les témoins, et le contrôle",
      lambda: b_() == {"la_graine_8": {"lus": 2, "differentes": 1}, "les_temoins": {"lus": 5, "differentes": 1}, "le_controle": False}
      and le_bilan({6: c_(False), 7: c_(False, False), 8: c_(True)})["le_controle"]
      and not le_bilan({6: c_(None), 7: c_(False), 8: c_(True)})["le_controle"])

    def d_(n, lus=3, ctl=True, ok=True, memes=True):
        return {"redonne": ok, "les_memes_nappes": memes,
                "le_bilan": {"la_graine_8": {"lus": lus, "differentes": n}, "les_temoins": {"lus": 6, "differentes": 0}, "le_controle": ctl}}
    v("★★★★ la règle : deux couples différents oui, un en partie, aucun non",
      le_verdict(d_(2))["lissue"].endswith("; oui") and le_verdict(d_(1))["lissue"].endswith("; en partie")
      and le_verdict(d_(0))["lissue"].endswith("; non") and le_verdict(d_(3))["lissue"].endswith("; oui"))
    v("★★★ indécidable sous 2 couples lus, si le contrôle échoue, sans les mêmes nappes ou sans redonne",
      not le_verdict(d_(1, lus=1))["decidable"] and not le_verdict(d_(2, ctl=False))["decidable"]
      and not le_verdict(d_(2, memes=False))["decidable"] and not le_verdict(d_(2, ok=False))["decidable"]
      and le_verdict(d_(0, lus=2))["decidable"])

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
