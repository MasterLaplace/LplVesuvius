"""Sur PHerc0358, là où une chaîne suivie et sa compagne ne tiennent pas les comptes, une troisième chaîne, partie d'une autre graine compagne, dit-elle par la majorité laquelle des deux a glissé ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE TROISIÈME CHAÎNE NE SOIT LANCÉE. Ce qui était vu avant d'écrire : tout ce que `296` à `371`
publient, dont `R4-F554` (une chaîne suivie et sa compagne ne tiennent les comptes que sous 77 de leurs 134 paires ; seule la graine 7,
côté moins, les tient à 9 paires sur 10) et `R4-F557` (compter les sauts en tours dans la chaîne seule ne tranche pas sur PHerc0358).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P169`. Deux chaînes qui glissent indépendamment glissent rarement au même saut : deux
chaînes qui tiennent les comptes entre elles, contre une troisième qui ne les tient avec aucune, désignent celle qui a glissé, sans tracé.

## Ce qui est fait

- **Les chaînes** : la suivie et la compagne de `368`, rejouées par sa fonction, dont les paires doivent redonner celles de `368` ; et
  une **tierce**, la même chaîne d'une maille partie d'une graine posée sur la nappe de départ à 15 mailles de son centre, du côté opposé
  à la compagne, ou sinon dans la première autre direction où la nappe a une normale.
- **Les couples** : suivie et compagne, suivie et tierce, compagne et tierce ; leurs paires se forment et tiennent les comptes comme dans
  `368`. Un couple **tient** si au moins 90 % de ses paires tiennent les comptes, et il compte s'il a au moins 5 paires.
- **Le vote**, côté par côté : si un seul des trois couples tient et que les deux autres comptent sans tenir, la chaîne qui n'est pas
  dans ce couple **a glissé**. Sinon, rien n'est désigné.
- **La règle**, sur les côtés où la suivie et la compagne ne tiennent pas les comptes : si le vote y désigne la suivie ou la compagne
  partout, **oui, la troisième chaîne dit laquelle a glissé** ; nulle part, **non** ; sinon, **en partie**. Indécidable sous deux tels
  côtés, ou sans tierce sur l'un d'eux.

## Les issues

L'issue de la tranche : **sur n côtés où la suivie et la compagne ne tiennent pas les comptes, le vote désigne l'une des deux sur a**, puis
ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté, la part des paires qui tiennent les comptes pour chaque couple, et la chaîne désignée, la tierce comprise.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la chaîne désignée a glissé plutôt que les deux autres ensemble ; ni où, dans la chaîne désignée,
le glissement tombe.

Usage :
    uv run python src/nappe/une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358.py --verifier
    uv run python src/nappe/une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358.py \\
        --json docs/mesures/une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358.json
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
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358 as m366  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
LES_COUPLES = ((SUIVIE, COMPAGNE), (SUIVIE, TIERCE), (COMPAGNE, TIERCE))
LA_PART = 0.9
LE_MINIMUM_PAR_COUPLE = 5
_LES_TIERCES: list = []


def la_graine_tierce(nappe: dict, graine=None) -> tuple | None:
    """La graine posée à 15 mailles du centre de la nappe, du côté opposé à la graine compagne, ou sinon dans la première autre direction ;
    None sans compagne ou sans autre point à normale connue."""
    graine = graine or m368.la_graine_compagne
    for u in m368.LES_DIRECTIONS:
        if graine(nappe, directions=(u,)) is not None:
            oppose = (-u[0], -u[1])
            return graine(nappe, directions=(oppose,) + tuple(x for x in m368.LES_DIRECTIONS if x not in (u, oppose)))
    return None


def le_chaineur(enchainer=None, croitre=None):
    """Le chaîneur de `368`, qui fait partir en plus la même chaîne de la graine tierce et en garde les surfaces."""
    base = m368.le_chaineur(croitre=croitre, enchainer=enchainer)
    enchainer = enchainer or m366.la_chaine_dune_maille_de_0358

    def chainer(nappe, relancer, sauter, lire_valeurs):
        suivie = base(nappe, relancer, sauter, lire_valeurs)
        g = la_graine_tierce(nappe)
        tierce = []
        if g is not None:
            grandir = croitre or (lambda p_, n_: m305.la_nappe_croissante(tuple(p_), tuple(n_), lire_valeurs))
            tierce = enchainer(grandir(*g), relancer, sauter, lire_valeurs)
        _LES_TIERCES.append({"la_graine_tierce": None if g is None else [round(float(x), 2) for x in g[0]],
                             "tierce": m368.les_surfaces(tierce)})
        return suivie
    return chainer


def le_couple(paires: list[dict]) -> dict:
    n = len(paires)
    t = sum(p["tient_les_comptes"] for p in paires)
    return {"les_paires": n, "tiennent": t, "compte": n >= LE_MINIMUM_PAR_COUPLE, "tient": n >= LE_MINIMUM_PAR_COUPLE and t >= LA_PART * n}


def le_vote(couples: dict) -> str | None:
    """La chaîne qui a glissé : celle qui n'est pas dans le seul couple qui tient, si les deux autres comptent sans tenir ; sinon None."""
    tiennent = [k for k in LES_COUPLES if couples["|".join(k)]["tient"]]
    if len(tiennent) != 1:
        return None
    autres = [couples["|".join(k)] for k in LES_COUPLES if k != tiennent[0]]
    if not all(c["compte"] and not c["tient"] for c in autres):
        return None
    return next(x for x in (SUIVIE, COMPAGNE, TIERCE) if x not in tiennent[0])


def le_bilan(cotes: list[dict]) -> dict:
    en_desaccord = [c for c in cotes if not c["les_couples"][f"{SUIVIE}|{COMPAGNE}"]["tient"]]
    return {"les_cotes": len(cotes), "en_desaccord": len(en_desaccord),
            "designent": sum(c["le_vote"] in (SUIVIE, COMPAGNE) for c in en_desaccord),
            "sans_tierce": sum(not c["la_tierce"] for c in en_desaccord),
            "les_votes": {f"{c['le_rang']} {c['le_cote']}": c["le_vote"] for c in cotes}}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_368"):
        return {"decidable": False, "lissue": "indécidable : les paires rejouées ne redonnent pas celles de 368"}
    b = d["le_bilan"]
    if b["en_desaccord"] < 2 or b["sans_tierce"]:
        return {"decidable": False, "lissue": f"indécidable : {b['en_desaccord']} côtés en désaccord, dont {b['sans_tierce']} sans tierce"}
    tete = (f"sur {b['en_desaccord']} côtés où la suivie et la compagne ne tiennent pas les comptes, le vote désigne l'une des deux sur "
            f"{b['designent']}")
    suite = ("oui, la troisième chaîne dit laquelle a glissé" if b["designent"] == b["en_desaccord"] else "non" if not b["designent"]
             else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    _LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=le_chaineur())
    publie = json.loads(CE_QUE_368_A_PUBLIE.read_text())
    cotes, redonne = [], True
    for c, pc, pt, pub in zip(chaines, m368._LES_PAIRES_DE_CHAINES, _LES_TIERCES, publie["les_cotes"]):
        surfaces = {SUIVIE: pc["suivie"], COMPAGNE: pc["compagne"], TIERCE: pt["tierce"]}
        paires = {"|".join(k): m368.les_paires(surfaces[k[0]], surfaces[k[1]]) for k in LES_COUPLES}
        redonne &= paires[f"{SUIVIE}|{COMPAGNE}"] == pub["les_paires"] and (c["le_rang"], c["le_cote"]) == (pub["le_rang"], pub["le_cote"])
        couples = {k: le_couple(p) for k, p in paires.items()}
        cote = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_graine_tierce": pt["la_graine_tierce"],
                "la_tierce": bool(pt["tierce"]), "les_sauts_tierces": len(pt["tierce"]), "les_couples": couples,
                "le_vote": le_vote(couples), "les_paires": {k: p for k, p in paires.items() if k != f"{SUIVIE}|{COMPAGNE}"}}
        cotes.append(cote)
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "le_vote": cote["le_vote"],
                          "couples": {k: (v["tiennent"], v["les_paires"]) for k, v in couples.items()}}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part": LA_PART, "le_minimum_par_couple": LE_MINIMUM_PAR_COUPLE},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_368": bool(redonne and len(cotes) == len(publie["les_cotes"])), "les_cotes": cotes}
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

    appels = []

    def graine(nappe, directions):
        appels.append(directions)
        return next((("g", u) for u in directions if u in nappe), None)
    v("★★★★ la graine tierce : à l'opposé de la compagne, sinon la première autre direction",
      lambda: la_graine_tierce({(0, 1), (0, -1), (1, 0)}, graine) == ("g", (0, -1))
      and la_graine_tierce({(1, 0), (0, -1)}, graine) == ("g", (0, -1))
      and la_graine_tierce({(0, 1), (1, 0)}, graine) == ("g", (1, 0)) and la_graine_tierce({(0, 1)}, graine) is None
      and la_graine_tierce(set(), graine) is None)
    appels.clear()
    la_graine_tierce({(1, 0), (0, -1), (-1, 0)}, graine)
    v("★★★ l'opposé essayé d'abord", appels[-1][0] == (-1, 0), str(appels))
    p = lambda t: {"tient_les_comptes": t}  # noqa: E731
    v("★★★★ un couple tient à 90 % de ses paires, et compte à 5 paires",
      le_couple([p(True)] * 9 + [p(False)])["tient"] and not le_couple([p(True)] * 8 + [p(False)] * 2)["tient"]
      and not le_couple([p(True)] * 4)["tient"] and not le_couple([p(True)] * 4)["compte"] and le_couple([p(False)] * 5)["compte"])
    cp = lambda t, n: {"tient": t, "compte": n >= 5}  # noqa: E731
    k = lambda sc, st, ct: {"suivie|compagne": sc, "suivie|tierce": st, "compagne|tierce": ct}  # noqa: E731
    v("★★★★ le vote : la chaîne hors du seul couple qui tient, si les deux autres comptent sans tenir",
      le_vote(k(cp(False, 9), cp(True, 9), cp(False, 9))) == COMPAGNE and le_vote(k(cp(False, 9), cp(False, 9), cp(True, 9))) == SUIVIE
      and le_vote(k(cp(True, 9), cp(False, 9), cp(False, 9))) == TIERCE and le_vote(k(cp(False, 9), cp(True, 9), cp(True, 9))) is None
      and le_vote(k(cp(False, 9), cp(False, 9), cp(False, 9))) is None and le_vote(k(cp(False, 9), cp(True, 9), cp(False, 3))) is None)
    c_ = lambda r, sc, vote, tierce=True: {"le_rang": r, "le_cote": "moins", "les_couples": {"suivie|compagne": {"tient": sc}},  # noqa: E731
                                           "le_vote": vote, "la_tierce": tierce}
    b = le_bilan([c_(6, False, COMPAGNE), c_(7, True, None), c_(8, False, TIERCE), c_(9, False, SUIVIE, tierce=False)])
    v("★★★★ le bilan : les côtés en désaccord, ceux où le vote désigne la suivie ou la compagne, ceux sans tierce",
      (b["en_desaccord"], b["designent"], b["sans_tierce"]) == (3, 2, 1), str(b))

    def d_(n, a, sans=0, ok=True):
        return {"les_pannes": [], "redonne_368": ok, "le_bilan": {"en_desaccord": n, "designent": a, "sans_tierce": sans}}
    v("★★★★ la règle : partout, oui ; nulle part, non ; sinon en partie",
      le_verdict(d_(4, 4))["lissue"].endswith("dit laquelle a glissé") and le_verdict(d_(4, 0))["lissue"].endswith("; non")
      and le_verdict(d_(4, 3))["lissue"].endswith("en partie"))
    v("★★★ indécidable sous deux côtés en désaccord, sans tierce, ou sans les paires de 368",
      not le_verdict(d_(1, 1))["decidable"] and not le_verdict(d_(4, 4, sans=1))["decidable"]
      and not le_verdict(d_(4, 4, ok=False))["decidable"])
    v("★★★ la part et le minimum : 90 % et 5 paires", (LA_PART, LE_MINIMUM_PAR_COUPLE) == (0.9, 5) and np is not None)

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
