"""Sur PHerc0358, quelles surfaces l'accord de trois chaînes valide-t-il, sur la même feuille et au même compte corrigé que des surfaces des deux autres chaînes, et jusqu'à combien de sauts de la nappe de départ ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SURFACE NE SOIT VALIDÉE, MAIS APRÈS AVOIR LU LES PAIRES QUE `368` ET `373` PUBLIENT. Ce qui
était vu avant d'écrire : tout ce que `296` à `373` publient, dont `R4-F559` (sous les comptes corrigés, les trois chaînes de la graine 6,
côté moins, tiennent les comptes deux à deux ; le vote désigne la suivie de la graine 7, côté plus ; sur la graine 8, aucun couple ne
tient). ⚠ Cette tranche ne lit pas `m7` : elle relit les paires, les sauts et les comptes que `368`, `369` et `373` publient.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P171`, ET `#5`. Sur un rouleau sans tracé, une surface que trois chaînes parties de trois
graines mettent sur la même feuille au même compte est ce qui validerait une première surface.

## Ce qui est fait

- **Les surfaces** : chaque surface gardée des trois chaînes de `373`, sur les cinq côtés, avec son compte corrigé.
- **Les témoins** : pour une surface d'une chaîne et une autre chaîne, les paires qu'elles forment. L'autre chaîne la **confirme** si une
  de ses surfaces est sur la même feuille au même compte corrigé ; elle la **contredit** si une de ses surfaces est sur la même feuille à un
  autre compte, ou au même compte sur une autre feuille.
- **Validée** : confirmée par les deux autres chaînes et contredite par aucune. Son compte corrigé est le nombre de tours qui la sépare de
  la nappe de départ.
- **Le contrôle** : sur chaque côté où `373` désigne une chaîne qui a glissé, cette chaîne a une surface contredite par les deux autres, et
  aucune de ses surfaces n'est validée à partir de la première qui l'est.
- **La règle** : si des surfaces sont validées sur au moins deux côtés, **oui, l'accord de trois chaînes valide des surfaces sans
  tracé** ; sur un seul, **en partie** ; sur aucun, **non**. Indécidable si le contrôle échoue ou si `373` n'a pas redonné ses chaînes.

## Les issues

L'issue de la tranche : **l'accord de trois chaînes valide n surfaces sur m, sur c côtés, jusqu'à t tours de la nappe de départ**, puis ce
que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté, les surfaces validées, contredites, et celles qu'aucune autre chaîne ne voit.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée est sur la bonne feuille, ni si trois chaînes peuvent glisser ensemble.

Usage :
    uv run python src/nappe/quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.py --verifier
    uv run python src/nappe/quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.py \\
        --json docs/mesures/quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_373_A_PUBLIE = LES_MESURES / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
LES_CHAINES = (SUIVIE, COMPAGNE, TIERCE)
VALIDEE, CONTREDITE, SEULE, EN_PARTIE = "validée", "contredite", "sans témoin", "confirmée une fois"


def les_liens(paires: dict) -> list[tuple]:
    """Chaque paire d'un côté, dans les deux sens : (chaîne, saut, autre chaîne, son saut, même feuille)."""
    out = []
    for cle, ps in paires.items():
        a, b = cle.split("|")
        for p in ps:
            out.append((a, p["le_saut_suivi"], b, p["le_saut_compagnon"], p["meme_feuille"]))
            out.append((b, p["le_saut_compagnon"], a, p["le_saut_suivi"], p["meme_feuille"]))
    return out


def le_statut(x: str, h: int, liens: list[tuple], comptes: dict) -> dict:
    """Ce que les deux autres chaînes disent de la surface `h` de la chaîne `x`."""
    w = comptes[x][h - 1]
    confirme, contredit = set(), set()
    for a, i, b, k, meme in liens:
        if (a, i) != (x, h):
            continue
        egal = comptes[b][k - 1] == w
        if meme and egal:
            confirme.add(b)
        elif meme != egal:
            contredit.add(b)
    autres = [y for y in LES_CHAINES if y != x]
    statut = (CONTREDITE if contredit else VALIDEE if all(y in confirme for y in autres) else EN_PARTIE if confirme else SEULE)
    return {"la_chaine": x, "le_saut": h, "le_compte": w, "le_statut": statut, "confirmee_par": sorted(confirme),
            "contredite_par": sorted(contredit)}


def le_controle(surfaces: list[dict], designee: str | None) -> bool | None:
    """Sur un côté où une chaîne est désignée : elle a une surface contredite par les deux autres, et aucune surface validée à partir de la
    première ; None sans chaîne désignée."""
    if designee is None:
        return None
    siennes = sorted((s for s in surfaces if s["la_chaine"] == designee), key=lambda s: s["le_saut"])
    premiere = next((s["le_saut"] for s in siennes if len(s["contredite_par"]) == 2), None)
    return premiere is not None and not any(s["le_statut"] == VALIDEE and s["le_saut"] >= premiere for s in siennes)


def le_cote(c373: dict, c368: dict, c369: dict) -> dict:
    comptes = {SUIVIE: [s["le_compte_corrige"] for s in c369["suivie"]], COMPAGNE: [s["le_compte_corrige"] for s in c369["compagne"]],
               TIERCE: [s["le_compte_corrige"] for s in c373["les_sauts_de_la_tierce"]]}
    paires = {f"{SUIVIE}|{COMPAGNE}": c368["les_paires"], **c373["les_paires"]}
    liens = les_liens(paires)
    surfaces = [le_statut(x, h, liens, comptes) for x in LES_CHAINES for h in range(1, len(comptes[x]) + 1)]
    return {"le_rang": c373["le_rang"], "le_cote": c373["le_cote"], "le_vote": c373["le_vote"], "les_surfaces": surfaces,
            "le_controle": le_controle(surfaces, c373["le_vote"])}


def le_bilan(cotes: list[dict]) -> dict:
    toutes = [s for c in cotes for s in c["les_surfaces"]]
    validees = [s for s in toutes if s["le_statut"] == VALIDEE]
    return {"les_surfaces": len(toutes), "validees": len(validees),
            "les_cotes_valides": sum(any(s["le_statut"] == VALIDEE for s in c["les_surfaces"]) for c in cotes),
            "le_plus_loin": max((s["le_compte"] for s in validees), default=None),
            "par_statut": {k: sum(s["le_statut"] == k for s in toutes) for k in (VALIDEE, EN_PARTIE, CONTREDITE, SEULE)},
            "les_controles": {f"{c['le_rang']} {c['le_cote']}": c["le_controle"] for c in cotes if c["le_controle"] is not None}}


def le_verdict(d: dict) -> dict:
    if not d.get("redonne_373"):
        return {"decidable": False, "lissue": "indécidable : 373 n'a pas redonné ses chaînes"}
    b = d["le_bilan"]
    if not b["les_controles"] or not all(b["les_controles"].values()):
        return {"decidable": False, "lissue": "indécidable : le contrôle sur la chaîne que 373 désigne échoue ou ne s'applique pas"}
    tete = f"l'accord de trois chaînes valide {b['validees']} surfaces sur {b['les_surfaces']}, sur {b['les_cotes_valides']} côtés"
    if b["validees"]:
        tete += f", jusqu'à {b['le_plus_loin']} tours de la nappe de départ"
    n = b["les_cotes_valides"]
    suite = "oui, l'accord de trois chaînes valide des surfaces sans tracé" if n >= 2 else "en partie" if n == 1 else "non"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d368, d369, d373 = (json.loads(x.read_text()) for x in (CE_QUE_368_A_PUBLIE, CE_QUE_369_A_PUBLIE, CE_QUE_373_A_PUBLIE))
    cotes = [le_cote(a, b, c) for a, b, c in zip(d373["les_cotes"], d368["les_cotes"], d369["les_cotes"])]
    d = {"la_question": __doc__.splitlines()[0], "redonne_373": bool(d373.get("redonne")), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
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
    liens = les_liens({"suivie|compagne": [p(1, 2, True)]})
    v("★★★★ les liens : chaque paire dans les deux sens", liens == [(SUIVIE, 1, COMPAGNE, 2, True), (COMPAGNE, 2, SUIVIE, 1, True)], str(liens))
    comptes = {SUIVIE: [1, 2, 3], COMPAGNE: [1, 1, 2], TIERCE: [1, 2, 3]}
    lk = les_liens({"suivie|compagne": [p(2, 3, True), p(3, 3, True)], "suivie|tierce": [p(2, 2, True), p(3, 2, False), p(1, 1, True)],
                    "compagne|tierce": [p(3, 2, True), p(1, 1, True)]})
    st = {(x, h): le_statut(x, h, lk, comptes)["le_statut"] for x in LES_CHAINES for h in (1, 2, 3)}
    v("★★★★ validée par les deux autres ; contredite à un autre compte sur la même feuille ; une fois ; sans témoin",
      (st[(SUIVIE, 2)], st[(SUIVIE, 3)], st[(SUIVIE, 1)], st[(COMPAGNE, 2)], st[(TIERCE, 3)])
      == (VALIDEE, CONTREDITE, EN_PARTIE, SEULE, SEULE), str(st))
    lk2 = les_liens({"suivie|compagne": [p(2, 3, True)], "suivie|tierce": [p(2, 2, True), p(2, 3, False)]})
    comptes2 = {SUIVIE: [1, 2], COMPAGNE: [1, 1, 2], TIERCE: [1, 2, 2]}
    v("★★★★ contredite aussi au même compte sur une autre feuille, même confirmée par ailleurs",
      le_statut(SUIVIE, 2, lk2, comptes2)["le_statut"] == CONTREDITE
      and le_statut(SUIVIE, 2, lk2, comptes2)["contredite_par"] == [TIERCE])
    s_ = lambda h, st_, contre=(): {"la_chaine": SUIVIE, "le_saut": h, "le_statut": st_, "contredite_par": list(contre)}  # noqa: E731
    v("★★★★ le contrôle : une surface de la désignée contredite par les deux autres, aucune validée à partir d'elle",
      lambda: le_controle([s_(1, VALIDEE), s_(2, CONTREDITE, (COMPAGNE, TIERCE)), s_(3, CONTREDITE, (TIERCE,))], SUIVIE) is True
      and le_controle([s_(1, EN_PARTIE), s_(2, CONTREDITE, (COMPAGNE, TIERCE)), s_(3, VALIDEE)], SUIVIE) is False
      and le_controle([s_(1, VALIDEE), s_(2, CONTREDITE, (TIERCE,))], SUIVIE) is False and le_controle([s_(1, VALIDEE)], None) is None)
    c_ = lambda r, sts, ctl=None: {"le_rang": r, "le_cote": "moins", "le_controle": ctl,  # noqa: E731
                                   "les_surfaces": [{"le_statut": x, "le_compte": w} for x, w in sts]}
    b = le_bilan([c_(6, [(VALIDEE, 1), (VALIDEE, 4), (SEULE, 5)]), c_(7, [(CONTREDITE, 2), (EN_PARTIE, 3)], True), c_(8, [(VALIDEE, 2)])])
    v("★★★★ le bilan : surfaces validées, côtés, la plus loin, par statut, contrôles",
      (b["les_surfaces"], b["validees"], b["les_cotes_valides"], b["le_plus_loin"]) == (6, 3, 2, 4)
      and b["par_statut"] == {VALIDEE: 3, EN_PARTIE: 1, CONTREDITE: 1, SEULE: 1} and b["les_controles"] == {"7 moins": True}, str(b))

    def d_(n, ctl=None, ok=True):
        return {"redonne_373": ok, "le_bilan": {"validees": 5, "les_surfaces": 9, "les_cotes_valides": n, "le_plus_loin": 4,
                                                "les_controles": {"7 plus": True} if ctl is None else ctl}}
    v("★★★★ la règle : deux côtés, oui ; un, en partie ; aucun, non",
      le_verdict(d_(2))["lissue"].endswith("valide des surfaces sans tracé") and le_verdict(d_(1))["lissue"].endswith("; en partie")
      and le_verdict(d_(0))["lissue"].endswith("; non") and "jusqu'à 4 tours" in le_verdict(d_(2))["lissue"])
    v("★★★ indécidable si le contrôle échoue, ne s'applique pas, ou sans les chaînes de 373",
      not le_verdict(d_(2, ctl={"7 plus": False}))["decidable"] and not le_verdict(d_(2, ctl={}))["decidable"]
      and not le_verdict(d_(2, ok=False))["decidable"])

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
