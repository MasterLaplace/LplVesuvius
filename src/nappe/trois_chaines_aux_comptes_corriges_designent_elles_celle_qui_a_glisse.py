"""Sur PHerc0358, avec une graine tierce posée ailleurs là où la nappe n'a pas d'autre direction à 15 mailles, et les comptes corrigés de `369`, le vote de trois chaînes désigne-t-il sur chaque côté en désaccord celle qui a glissé ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE TIERCE NE SOIT LANCÉE SUR LA GRAINE 8. Ce qui était vu avant d'écrire : tout ce que `296` à `372`
publient, dont `R4-F555` (corrigés des sauts nuls au quart de pas et doubles au pas et demi, les comptes de la suivie et de la compagne
tiennent sous 38 paires sur 41 de la graine 6, côté moins, 9 sur 22 de la graine 7, côté plus, 9 sur 10 de la graine 7, côté moins, 21
sur 35 de la graine 8, côté plus, et 13 sur 26 de la graine 8, côté moins) et `R4-F558` (à 15 mailles, la nappe de la graine 8 n'a de
point à normale connue que du côté de la compagne ; sur la graine 7, côté plus, le vote désigne la suivie).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P170`. Le vote de `372` ne s'est tenu que sur un côté : il manquait une tierce sur la graine 8,
et les sauts nuls rompaient les comptes bruts de la graine 6.

## Ce qui est fait

- **Les chaînes** : la suivie et la compagne de `369`, rejouées, dont les paires redonnent celles de `368` et les sauts ceux de `369`.
- **La tierce** : la graine de `372` là où elle existe ; sinon, à 11 mailles du centre en diagonale, la diagonale la plus opposée à la
  compagne d'abord ; sinon à 10 mailles sur un axe autre que celui de la compagne, l'opposé d'abord. La même chaîne d'une maille en part.
- **Les comptes** : chaque saut des trois chaînes compté comme dans `369`, 0 s'il est nul, 2 s'il est double, 1 sinon, depuis sa nappe de
  départ. Une paire tient les comptes si « même feuille » et « même compte corrigé » disent la même chose.
- **Les couples et le vote** : ceux de `372`, sur les comptes corrigés ; un côté est **en désaccord** si la suivie et la compagne n'y
  tiennent pas les comptes corrigés.
- **La règle**, sur les côtés en désaccord : si le vote y désigne la suivie ou la compagne partout, **oui** ; nulle part, **non** ; sinon,
  **en partie**. Indécidable sous deux côtés en désaccord, ou sans tierce sur l'un d'eux.

## Les issues

L'issue de la tranche : **sur n côtés en désaccord sous les comptes corrigés, le vote désigne l'une des deux sur a**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Le vote sur les comptes bruts, côté par côté ; où chaque tierce est posée.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si la chaîne désignée a glissé plutôt que les deux autres ensemble, ni où tombe son glissement.

Usage :
    uv run python src/nappe/trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.py --verifier
    uv run python src/nappe/trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.py \\
        --json docs/mesures/trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json
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
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358 as m372  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_372_A_PUBLIE = LES_MESURES / "une_troisieme_chaine_dit_elle_laquelle_a_glisse_sur_pherc0358.json"
SUIVIE, COMPAGNE, TIERCE = m372.SUIVIE, m372.COMPAGNE, m372.TIERCE
LES_COUPLES = m372.LES_COUPLES
LES_DIAGONALES = ((1, 1), (1, -1), (-1, 1), (-1, -1))
LE_DECALAGE_DIAGONAL = 11
LE_DECALAGE_PROCHE = 10
_LES_TIERCES: list = []


def la_graine_tierce(nappe: dict, graine=None) -> tuple | None:
    """La graine de `372` ; sinon à 11 mailles en diagonale, la plus opposée à la compagne d'abord ; sinon à 10 mailles sur un autre axe
    que la compagne, l'opposé d'abord. Rend la graine et où elle est posée ; None sans compagne ou sans point à normale connue."""
    graine = graine or m368.la_graine_compagne
    g = m372.la_graine_tierce(nappe, graine)
    if g is not None:
        return g, "à l'opposé"
    u = next((x for x in m368.LES_DIRECTIONS if graine(nappe, directions=(x,)) is not None), None)
    if u is None:
        return None
    diagonales = tuple(sorted(LES_DIAGONALES, key=lambda x: x[0] * u[0] + x[1] * u[1]))
    g = graine(nappe, decalage=LE_DECALAGE_DIAGONAL, directions=diagonales)
    if g is not None:
        return g, "en diagonale"
    oppose = (-u[0], -u[1])
    axes = (oppose,) + tuple(x for x in m368.LES_DIRECTIONS if x not in (u, oppose))
    g = graine(nappe, decalage=LE_DECALAGE_PROCHE, directions=axes)
    return (g, "plus près") if g is not None else None


def le_chaineur(enchainer=None):
    """Le chaîneur de `369`, qui fait partir en plus la même chaîne de la graine tierce et en garde la nappe et les surfaces."""
    base = m369.le_chaineur()
    enchainer = enchainer or m366.la_chaine_dune_maille_de_0358

    def chainer(nappe, relancer, sauter, lire_valeurs):
        suivie = base(nappe, relancer, sauter, lire_valeurs)
        r = la_graine_tierce(nappe)
        tierce, depart = [], None
        if r is not None:
            depart = m305.la_nappe_croissante(tuple(r[0][0]), tuple(r[0][1]), lire_valeurs)
            tierce = enchainer(depart, relancer, sauter, lire_valeurs)
        _LES_TIERCES.append({"la_graine_tierce": None if r is None else [round(float(x), 2) for x in r[0][0]],
                             "ou": None if r is None else r[1], "la_nappe": m367.les_points(depart), "tierce": m368.les_surfaces(tierce)})
        return suivie
    return chainer


def tient(p: dict, a: list[dict], b: list[dict]) -> bool:
    """Une paire d'un couple tient les comptes corrigés : même feuille exactement au même compte corrigé."""
    return bool(p["meme_feuille"] == (a[p["le_saut_suivi"] - 1]["le_compte_corrige"] == b[p["le_saut_compagnon"] - 1]["le_compte_corrige"]))


def le_couple(paires: list[dict], a: list[dict], b: list[dict]) -> dict:
    return m372.le_couple([{"tient_les_comptes": tient(p, a, b)} for p in paires])


def le_bilan(cotes: list[dict]) -> dict:
    en_desaccord = [c for c in cotes if not c["les_couples"][f"{SUIVIE}|{COMPAGNE}"]["tient"]]
    return {"les_cotes": len(cotes), "en_desaccord": len(en_desaccord),
            "designent": sum(c["le_vote"] in (SUIVIE, COMPAGNE) for c in en_desaccord),
            "sans_tierce": sum(not c["la_tierce"] for c in en_desaccord),
            "les_votes": {f"{c['le_rang']} {c['le_cote']}": c["le_vote"] for c in cotes},
            "les_votes_bruts": {f"{c['le_rang']} {c['le_cote']}": c["le_vote_brut"] for c in cotes}}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas celles de 368, 369 et 372"}
    b = d["le_bilan"]
    if b["en_desaccord"] < 2 or b["sans_tierce"]:
        return {"decidable": False, "lissue": f"indécidable : {b['en_desaccord']} côtés en désaccord, dont {b['sans_tierce']} sans tierce"}
    tete = f"sur {b['en_desaccord']} côtés en désaccord sous les comptes corrigés, le vote désigne l'une des deux sur {b['designent']}"
    suite = ("oui, trois chaînes désignent celle qui a glissé" if b["designent"] == b["en_desaccord"] else "non" if not b["designent"]
             else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    m369._LES_CHAINES.clear()
    _LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=le_chaineur())
    p368, p369, p372 = (json.loads(x.read_text()) for x in (CE_QUE_368_A_PUBLIE, CE_QUE_369_A_PUBLIE, CE_QUE_372_A_PUBLIE))
    cotes, redonne = [], True
    for c, pc, nap, pt, q8, q9, q2 in zip(chaines, m368._LES_PAIRES_DE_CHAINES, m369._LES_CHAINES, _LES_TIERCES, p368["les_cotes"],
                                          p369["les_cotes"], p372["les_cotes"]):
        surfaces = {SUIVIE: pc["suivie"], COMPAGNE: pc["compagne"], TIERCE: pt["tierce"]}
        sauts = {SUIVIE: m369.les_sauts(nap["la_nappe"], pc["suivie"]), COMPAGNE: m369.les_sauts(nap["la_nappe_compagne"], pc["compagne"]),
                 TIERCE: m369.les_sauts(pt["la_nappe"], pt["tierce"])}
        paires = {"|".join(k): m368.les_paires(surfaces[k[0]], surfaces[k[1]]) for k in LES_COUPLES}
        redonne &= (paires[f"{SUIVIE}|{COMPAGNE}"] == q8["les_paires"] and sauts[SUIVIE] == q9["suivie"] and sauts[COMPAGNE] == q9["compagne"]
                    and (q2["la_graine_tierce"] is None or q2["la_graine_tierce"] == pt["la_graine_tierce"]))
        couples = {"|".join(k): le_couple(paires["|".join(k)], sauts[k[0]], sauts[k[1]]) for k in LES_COUPLES}
        bruts = {k: m372.le_couple(p) for k, p in paires.items()}
        cote = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_graine_tierce": pt["la_graine_tierce"], "ou": pt["ou"],
                "la_tierce": bool(pt["tierce"]), "les_sauts_de_la_tierce": sauts[TIERCE], "les_couples": couples,
                "les_couples_bruts": bruts, "le_vote": m372.le_vote(couples), "le_vote_brut": m372.le_vote(bruts),
                "les_paires": {k: p for k, p in paires.items() if k != f"{SUIVIE}|{COMPAGNE}"}}
        cotes.append(cote)
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "ou": pt["ou"], "le_vote": cote["le_vote"],
                          "couples": {k: (v["tiennent"], v["les_paires"]) for k, v in couples.items()}}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_decalage_diagonal": LE_DECALAGE_DIAGONAL, "le_decalage_proche": LE_DECALAGE_PROCHE, "la_part": m372.LA_PART,
                            "le_minimum_par_couple": m372.LE_MINIMUM_PAR_COUPLE},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne": bool(redonne and len(cotes) == len(p368["les_cotes"])), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
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

    appels = []

    def graine(nappe, decalage=15, directions=()):
        appels.append((decalage, directions))
        return next((("g", decalage, u) for u in directions if (decalage, u) in nappe), None)
    v("★★★★ la tierce : celle de 372 à 15 mailles, sinon en diagonale à 11, sinon à 10 sur un autre axe",
      lambda: la_graine_tierce({(15, (0, 1)), (15, (0, -1))}, graine) == (("g", 15, (0, -1)), "à l'opposé")
      and la_graine_tierce({(15, (0, 1)), (11, (1, 1)), (11, (1, -1))}, graine) == (("g", 11, (1, -1)), "en diagonale")
      and la_graine_tierce({(15, (0, 1)), (10, (0, 1)), (10, (1, 0))}, graine) == (("g", 10, (1, 0)), "plus près")
      and la_graine_tierce({(15, (0, 1)), (10, (0, 1))}, graine) is None and la_graine_tierce({(11, (1, 1))}, graine) is None)
    appels.clear()
    la_graine_tierce({(15, (1, 0)), (10, (0, 1)), (10, (-1, 0))}, graine)
    diag = [d_ for dc, d_ in appels if dc == 11]
    proche = [d_ for dc, d_ in appels if dc == 10]
    v("★★★ les diagonales opposées à la compagne d'abord, puis l'axe opposé d'abord, jamais celui de la compagne",
      diag and diag[0][:2] in (((-1, 1), (-1, -1)), ((-1, -1), (-1, 1))) and proche and proche[0][0] == (-1, 0)
      and (1, 0) not in proche[0], str(appels))
    s_ = lambda *w: [{"le_compte_corrige": x} for x in w]  # noqa: E731
    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    a, b = s_(1, 1, 2, 3), s_(1, 2, 3, 4)
    v("★★★★ tenir les comptes corrigés : même feuille exactement au même compte corrigé",
      tient(p(3, 2, True), a, b) and not tient(p(2, 2, True), a, b) and tient(p(2, 2, False), a, b) and not tient(p(4, 3, False), a, b))
    c = le_couple([p(3, 2, True)] * 9 + [p(2, 2, True)], a, b)
    v("★★★★ un couple sur les comptes corrigés : 90 % et 5 paires, comme dans 372",
      c["tient"] and c["tiennent"] == 9 and not le_couple([p(3, 2, True)] * 4, a, b)["compte"], str(c))
    k_ = lambda sc, st, ct: {"suivie|compagne": {"tient": sc}, "suivie|tierce": {"tient": st}, "compagne|tierce": {"tient": ct}}  # noqa: E731
    c_ = lambda r, sc, vote, tierce=True: {"le_rang": r, "le_cote": "plus", "les_couples": k_(sc, False, False), "le_vote": vote,  # noqa: E731
                                           "le_vote_brut": None, "la_tierce": tierce}
    bb = le_bilan([c_(6, True, None), c_(7, False, SUIVIE), c_(8, False, TIERCE), c_(9, False, COMPAGNE, tierce=False)])
    v("★★★★ le bilan : les côtés en désaccord sous les comptes corrigés, ceux qu'il désigne, ceux sans tierce",
      (bb["en_desaccord"], bb["designent"], bb["sans_tierce"]) == (3, 2, 1), str(bb))

    def d_(n, a_, sans=0, ok=True):
        return {"les_pannes": [], "redonne": ok, "le_bilan": {"en_desaccord": n, "designent": a_, "sans_tierce": sans}}
    v("★★★★ la règle : partout, oui ; nulle part, non ; sinon en partie",
      le_verdict(d_(3, 3))["lissue"].endswith("désignent celle qui a glissé") and le_verdict(d_(3, 0))["lissue"].endswith("; non")
      and le_verdict(d_(3, 2))["lissue"].endswith("en partie"))
    v("★★★ indécidable sous deux côtés, sans tierce, ou sans les chaînes de 368, 369 et 372",
      not le_verdict(d_(1, 1))["decidable"] and not le_verdict(d_(3, 3, sans=1))["decidable"]
      and not le_verdict(d_(3, 3, ok=False))["decidable"])
    v("★★★ les décalages : 11 mailles en diagonale, 10 sur un axe", (LE_DECALAGE_DIAGONAL, LE_DECALAGE_PROCHE) == (11, 10))

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
