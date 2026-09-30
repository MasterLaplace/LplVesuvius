"""Sur PHerc0358, un glissement que l'accord de deux chaînes révèle se voit-il dans la chaîne seule, comme un saut qui garde la même feuille ou qui en saute une ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT NE SOIT COMPARÉ À LA SURFACE D'OÙ IL PART. Ce qui était vu avant d'écrire : tout ce que
`296` à `368` publient, dont `R4-F554` (une chaîne suivie et sa compagne, parties de la même nappe, ne tiennent les comptes que sous 77 de
leurs 134 paires ; sur trois côtés, l'une prend un saut d'avance ou de retard qu'elle garde). ⚠ Dans les paires de `368`, sur la graine 6,
côté moins, la surface du premier saut de chaque chaîne est sur la même feuille que la surface du deuxième saut de l'autre : un saut qui ne
change pas de feuille existe.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P166`. Si le glissement vient de sauts qui gardent la même feuille ou en sautent une, et que
ces sauts se voient en comparant une surface à celle d'où elle part, une chaîne peut les compter juste seule, sans compagne ni tracé.

## Ce qui est fait

- **Les chaînes** : celles de `368`, la suivie et la compagne sur chacun des cinq côtés, rejouées par sa fonction, qui gagne pour cela de
  quoi garder aussi les deux nappes de départ.
- **Chaque saut** : sa surface gardée comparée à la surface d'où il part, la nappe pour le premier : la médiane des écarts absolus de ses
  points en face, à trois pas au plus. Un saut est **nul** si elle est d'au plus un quart de pas, **double** si elle dépasse un pas et demi,
  **simple** sinon ; sans 50 points en face, il est compté simple.
- **Le compte corrigé** d'une surface : la somme, jusqu'à elle, de 0 par saut nul, 2 par saut double et 1 par saut simple.
- **Les paires** : celles de `368`, qui doivent être redonnées ; une paire tient le compte corrigé si « même feuille » et « même compte
  corrigé » disent la même chose.
- **La règle** : si au moins 90 % des paires tiennent le compte corrigé, **oui, le glissement se voit dans la chaîne seule** ; si pas plus
  qu'avec les comptes bruts de `368`, **non** ; sinon, **en partie**.

## Les issues

L'issue de la tranche : **corrigés des sauts nuls et doubles, a des n paires tiennent les comptes, contre a' sans correction**, puis ce que
dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts nuls et doubles, chaîne par chaîne ; les écarts des sauts simples.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un saut simple est sur la bonne feuille, ni ce que valent ces seuils sur PHercParis4.

Usage :
    uv run python src/nappe/le_glissement_se_voit_il_dans_la_chaine_seule.py --verifier
    uv run python src/nappe/le_glissement_se_voit_il_dans_la_chaine_seule.py \\
        --json docs/mesures/le_glissement_se_voit_il_dans_la_chaine_seule.json
"""
from __future__ import annotations

import argparse
import json
import statistics
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
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
LE_PAS = m368.LE_PAS
LA_PORTEE = 3.0 * LE_PAS
NUL, SIMPLE, DOUBLE = "nul", "simple", "double"
LES_PAS = {NUL: 0, SIMPLE: 1, DOUBLE: 2}
_LES_CHAINES: list = []


def lecart_du_saut(surface, depart, lateral: float = m368.LE_LATERAL) -> dict:
    """La médiane des écarts absolus des points de la surface qui ont la surface de départ en face, à trois pas au plus."""
    import numpy as np

    import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321

    if not len(surface[0]) or not len(depart[0]):
        return {"en_face": 0, "lecart_median": None}
    e = m321.les_ecarts(surface[0], surface[1], depart[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= LA_PORTEE)
    return {"en_face": int(vus.sum()), "lecart_median": round(float(np.median(np.abs(e[vus]))), 3) if vus.any() else None}


def le_genre(c: dict) -> str:
    if c["en_face"] < m368.LE_MINIMUM_EN_FACE or c["lecart_median"] is None:
        return SIMPLE
    return NUL if c["lecart_median"] <= m368.LE_QUART else DOUBLE if c["lecart_median"] > 1.5 * LE_PAS else SIMPLE


def les_sauts(nappe, surfaces: list, comparer=lecart_du_saut) -> list[dict]:
    """Chaque saut d'une chaîne, comparé à la surface d'où il part, et le compte corrigé de sa surface."""
    out, compte, avant = [], 0, nappe
    for h, s in enumerate(surfaces, 1):
        c = comparer(s, avant)
        g = le_genre(c)
        compte += LES_PAS[g]
        out.append({"le_saut": h, **c, "le_genre": g, "le_compte_corrige": compte})
        avant = s
    return out


def le_chaineur():
    """Le chaîneur de `368`, qui garde aussi les deux nappes de départ."""
    base = m368.le_chaineur()

    def chainer(nappe, relancer, sauter, lire_valeurs):
        suivie = base(nappe, relancer, sauter, lire_valeurs)
        g = m368.la_graine_compagne(nappe)
        compagne = None if g is None else m305.la_nappe_croissante(tuple(g[0]), tuple(g[1]), lire_valeurs)
        _LES_CHAINES.append({"la_nappe": m367.les_points(nappe), "la_nappe_compagne": m367.les_points(compagne)})
        return suivie
    return chainer


def tient_le_compte(p: dict, suivie: list[dict], compagne: list[dict]) -> bool:
    ws = suivie[p["le_saut_suivi"] - 1]["le_compte_corrige"]
    wc = compagne[p["le_saut_compagnon"] - 1]["le_compte_corrige"]
    return bool(p["meme_feuille"] == (ws == wc))


def le_bilan(cotes: list[dict]) -> dict:
    paires = [(p, c) for c in cotes for p in c["les_paires"]]
    genres = {g: sum(s["le_genre"] == g for c in cotes for k in ("suivie", "compagne") for s in c[k]) for g in LES_PAS}
    return {"les_paires": len(paires), "tiennent_brut": sum(p["tient_les_comptes"] for p, _ in paires),
            "tiennent_corrige": sum(tient_le_compte(p, c["suivie"], c["compagne"]) for p, c in paires), "les_genres": genres}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_368"):
        return {"decidable": False, "lissue": "indécidable : les paires rejouées ne redonnent pas celles de 368"}
    b = d["le_bilan"]
    if not b["les_paires"]:
        return {"decidable": False, "lissue": "indécidable : aucune paire"}
    tete = (f"corrigés des sauts nuls et doubles, {b['tiennent_corrige']} des {b['les_paires']} paires tiennent les comptes, contre "
            f"{b['tiennent_brut']} sans correction")
    if b["tiennent_corrige"] >= 0.9 * b["les_paires"]:
        suite = "oui, le glissement se voit dans la chaîne seule"
    elif b["tiennent_corrige"] <= b["tiennent_brut"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    _LES_CHAINES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=le_chaineur())
    publie = json.loads(CE_QUE_368_A_PUBLIE.read_text())
    cotes, redonne = [], True
    for c, pc, nap, pub in zip(chaines, m368._LES_PAIRES_DE_CHAINES, _LES_CHAINES, publie["les_cotes"]):
        paires = m368.les_paires(pc["suivie"], pc["compagne"])
        redonne &= paires == pub["les_paires"] and (c["le_rang"], c["le_cote"]) == (pub["le_rang"], pub["le_cote"])
        cote = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "suivie": les_sauts(nap["la_nappe"], pc["suivie"]),
                "compagne": les_sauts(nap["la_nappe_compagne"], pc["compagne"]), "les_paires": paires}
        cotes.append(cote)
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"]}, ensure_ascii=False),
              [(s["le_genre"][0], s["lecart_median"]) for s in cote["suivie"]], [(s["le_genre"][0], s["lecart_median"]) for s in cote["compagne"]],
              flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_portee": LA_PORTEE, "le_quart": m368.LE_QUART, "le_double": 1.5 * LE_PAS},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_368": bool(redonne and len(cotes) == len(publie["les_cotes"])), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
    simples = [s["lecart_median"] for c in cotes for k in ("suivie", "compagne") for s in c[k]
               if s["le_genre"] == SIMPLE and s["lecart_median"] is not None]
    d["lecart_median_des_sauts_simples"] = round(statistics.median(simples), 3) if simples else None
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

    c_ = lambda e, n=60: {"en_face": n, "lecart_median": e}  # noqa: E731
    v("★★★★ le genre : nul au quart de pas, double au-delà d'un pas et demi, simple entre les deux et sans 50 points en face",
      [le_genre(c_(x)) for x in (0.3, 5.0, 5.1, 20.0, 30.0, 30.1)] == [NUL, NUL, SIMPLE, SIMPLE, SIMPLE, DOUBLE]
      and le_genre(c_(0.3, n=49)) == SIMPLE and le_genre(c_(None)) == SIMPLE)
    ecarts = {("s1", "n"): 20.0, ("s2", "s1"): 0.4, ("s3", "s2"): 41.0, ("s4", "s3"): 19.0}
    vus = []

    def comparer(s, avant):
        vus.append((s, avant))
        return c_(ecarts[(s, avant)])
    v("★★★★ chaque saut comparé à la surface d'où il part, la nappe pour le premier ; le compte corrigé : 0, 1 ou 2 par saut",
      lambda: [(s["le_genre"], s["le_compte_corrige"]) for s in les_sauts("n", ["s1", "s2", "s3", "s4"], comparer)]
      == [(SIMPLE, 1), (NUL, 1), (DOUBLE, 3), (SIMPLE, 4)] and vus == [("s1", "n"), ("s2", "s1"), ("s3", "s2"), ("s4", "s3")], str(vus))
    suivie = [{"le_compte_corrige": w} for w in (1, 1, 2, 3)]
    compagne = [{"le_compte_corrige": w} for w in (1, 2, 3, 4)]
    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m, "tient_les_comptes": m == (h == k)}  # noqa: E731
    v("★★★★ tenir le compte corrigé : même feuille exactement au même compte corrigé",
      tient_le_compte(p(3, 2, True), suivie, compagne) and not tient_le_compte(p(2, 2, True), suivie, compagne)
      and tient_le_compte(p(2, 2, False), suivie, compagne) and tient_le_compte(p(4, 3, True), suivie, compagne))
    cote = {"suivie": suivie + [{"le_compte_corrige": 4}], "compagne": compagne, "les_paires": [p(3, 2, True), p(2, 2, True), p(4, 3, True)]}
    for s, g in zip(cote["suivie"], (SIMPLE, NUL, SIMPLE, SIMPLE, DOUBLE)):
        s["le_genre"] = g
    for s in cote["compagne"]:
        s["le_genre"] = SIMPLE
    b = le_bilan([cote])
    v("★★★★ le bilan : les paires qui tiennent, brutes et corrigées, et les genres de sauts des deux chaînes",
      b == {"les_paires": 3, "tiennent_brut": 1, "tiennent_corrige": 2, "les_genres": {NUL: 1, SIMPLE: 7, DOUBLE: 1}}, str(b))

    def d_(brut, corr, n=100, ok=True):
        return {"les_pannes": [], "redonne_368": ok, "le_bilan": {"les_paires": n, "tiennent_brut": brut, "tiennent_corrige": corr}}
    v("★★★★ la règle : 90 % corrigés, oui ; pas mieux qu'en brut, non ; sinon en partie",
      le_verdict(d_(57, 90))["lissue"].endswith("dans la chaîne seule") and le_verdict(d_(57, 57))["lissue"].endswith("; non")
      and le_verdict(d_(57, 50))["lissue"].endswith("; non") and le_verdict(d_(57, 89))["lissue"].endswith("en partie"))
    v("★★★ des paires qui ne redonnent pas 368 : indécidable", not le_verdict(d_(57, 95, ok=False))["decidable"])
    v("★★★ la portée d'un saut : trois pas de PHerc0358", LA_PORTEE == 60.0)

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
