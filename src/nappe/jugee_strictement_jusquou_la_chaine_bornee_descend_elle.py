"""Jugée strictement, une surface n'étant juste que si elle retrouve le seul tour publié attendu, jusqu'où la chaîne bornée de 335 descend-elle, et reste-t-elle devant la chaîne sans relance ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE DESCENTE NE SOIT RECOMPTÉE STRICTEMENT. Ce qui était vu avant d'écrire : tout ce que `296` à
`339` publient, dont `R4-F521` (bornée à deux mailles de ses semis, la chaîne relancée depuis sa spire descend six tours publiés sur les huit
graines sans un saut faux), `R4-F523` (la lecture sépare toujours deux tours voisins par leur écart) et `R4-F525` (douze des quarante-huit
surfaces que cette descente compte justes retrouvent deux tours, sans traverser la couture).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P136`. La descente de `330` compte juste une surface qui retrouve le tour attendu, même avec un
autre. Une surface qui en retrouve deux sans traverser la couture n'est pas là où un tour publié est seul : la compter juste peut gonfler une
descente. Rien n'est remesuré ici : les lectures que `330`, `331`, `333` et `336` ont publiées sont relues avec une règle plus stricte.

## Ce qui est fait

- **Les chaînes** : sur PHercParis4, côté par côté, la suite des lectures publiées de la nappe puis de chaque surface ; la nappe est lue
  dans `330`, les surfaces dans `330` (sans relance), `331` (relancée depuis un point), `333` (relancée depuis la spire) et `336` (la chaîne
  bornée de `335`, qu'elle redonne). La descente de `330` recomptée sur ces lectures doit redonner celle que chaque tranche publie, sans quoi
  la tranche est indécidable.
- **La descente stricte** : celle de `330`, partie de la première surface qui retrouve un seul tour, où une surface n'est juste que si elle
  retrouve le tour attendu et lui seul ; une surface qui retrouve le tour attendu et un autre arrête la descente sur « deux tours ».
- **La descente d'une graine** : la plus longue de ses deux côtés ; les graines dont aucune surface ne touche un tour ne comptent pas.

## Les issues

L'issue de la tranche : **jugée strictement, la chaîne bornée descend h tours publiés en médiane, contre h0 pour la chaîne sans relance** ;
et, déclaré avant : **elle garde ses six tours** si h ≥ 6 ; **elle reste devant la chaîne sans relance** si h < 6 et h > h0 ; **elle ne
descend pas plus loin que la chaîne sans relance** sinon.

## Rapporté à côté, qui ne décide rien

Les descentes strictes des chaînes relancées depuis un point (`331`) et depuis la spire (`333`), et ce qui arrête chaque descente stricte.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où sont posées les surfaces à deux tours.

Usage :
    uv run python src/nappe/jugee_strictement_jusquou_la_chaine_bornee_descend_elle.py --verifier
    uv run python src/nappe/jugee_strictement_jusquou_la_chaine_bornee_descend_elle.py \\
        --json docs/mesures/jugee_strictement_jusquou_la_chaine_bornee_descend_elle.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
LES_CHAINES = {"sans relance": "jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.json",
               "relancée depuis un point": "une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.json",
               "relancée depuis la spire": "la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.json",
               "bornée": "pourquoi_aucune_chaine_ne_retrouve_t_elle_le_septieme_tour.json"}


def les_retrouves(lectures: dict) -> list[int]:
    return sorted((int(t) for t, x in lectures.items() if x == "retrouve"), reverse=True)


def la_descente_stricte(surfaces: list[dict]) -> dict:
    """La descente de `330` où une surface n'est juste que si elle retrouve le seul tour attendu ; les surfaces comme {tour : lecture}."""
    k0 = next((k for k, s in enumerate(surfaces) if len(les_retrouves(s)) == 1), None)
    if k0 is None:
        return {"le_tour_de_depart": None, "la_descente": 0, "larret": "aucun tour touché"}
    depart = les_retrouves(surfaces[k0])[0]
    attendu, h = depart - 1, 0
    for s in surfaces[k0 + 1:]:
        if attendu < m330.LE_DERNIER:
            return {"le_tour_de_depart": depart, "la_descente": h, "larret": "le bout des tours chargés"}
        r = les_retrouves(s)
        if r == [attendu]:
            h += 1
            attendu -= 1
            continue
        if attendu in r:
            larret = "deux tours"
        elif r:
            larret = "un saut faux"
        else:
            larret = "un tour manqué" if any(x != "non lue" for x in s.values()) else "non lue"
        return {"le_tour_de_depart": depart, "la_descente": h, "larret": larret}
    larret = "le bout des tours chargés" if attendu < m330.LE_DERNIER else "le bout de la chaîne"
    return {"le_tour_de_depart": depart, "la_descente": h, "larret": larret}


def les_surfaces(nom: str, d: dict, nappes: dict, rang: int, cote: str) -> list[dict]:
    """La suite des lectures d'un côté d'une chaîne publiée, la nappe en tête, chacune comme {tour : lecture}."""
    tous = [str(t) for t in m330.LES_TOURS]
    if nom == "sans relance":
        g = next(x for x in d["les_graines"] if x["le_rang"] == rang)
        suite = [{t: x["la_lecture"] for t, x in s["les_tours"].items()} for s in g["les_cotes"][cote]["les_spires"]]
    else:
        g = next(x for x in d["les_graines"]["PHercParis4"] if x["le_rang"] == rang)
        suite = [dict(s["les_tours"]) if "les_tours" in s else {t: "non lue" for t in tous} for s in g["les_cotes"][cote]["les_surfaces"]]
    return [nappes[rang]] + suite


def les_graines_de(nom: str, d: dict) -> list[dict]:
    return d["les_graines"] if nom == "sans relance" else d["les_graines"]["PHercParis4"]


def juger(nom: str, d: dict, nappes: dict) -> dict:
    """Pour une chaîne publiée, graine par graine, la descente de `330` recomptée et la descente stricte, et si la première redonne celle
    que la tranche publie."""
    graines, redonne = [], True
    for g in les_graines_de(nom, d):
        cotes = {}
        for cote in g["les_cotes"]:
            surf = [{int(t): x for t, x in s.items()} for s in les_surfaces(nom, d, nappes, g["le_rang"], cote)]
            souple = m330.la_descente(surf)
            redonne &= (souple["la_descente"], souple["larret"]) == (g["les_cotes"][cote]["la_descente"], g["les_cotes"][cote]["larret"])
            cotes[cote] = {"souple": souple, "stricte": la_descente_stricte([{str(t): x for t, x in s.items()} for s in surf])}
        touche = any(c["stricte"]["le_tour_de_depart"] is not None for c in cotes.values())
        graines.append({"le_rang": g["le_rang"], "les_cotes": cotes, "le_tour_touche": touche,
                        "la_descente_souple": max(c["souple"]["la_descente"] for c in cotes.values()),
                        "la_descente_stricte": max(c["stricte"]["la_descente"] for c in cotes.values()),
                        "larret_strict": max(cotes.values(), key=lambda c: (c["stricte"]["la_descente"],
                                                                             c["stricte"]["le_tour_de_depart"] is not None))["stricte"]["larret"]})
    ds = [g["la_descente_stricte"] for g in graines if g["le_tour_touche"]]
    return {"redonne": bool(redonne), "les_graines": graines, "la_mediane_stricte": float(np.median(ds)) if ds else None}


def le_verdict(d: dict) -> dict:
    if not all(c["redonne"] for c in d["les_chaines"].values()):
        faux = [n for n, c in d["les_chaines"].items() if not c["redonne"]]
        return {"decidable": False, "lissue": f"indécidable : la descente recomptée ne redonne pas celle publiée ({faux[0]})"}
    h, h0 = d["les_chaines"]["bornée"]["la_mediane_stricte"], d["les_chaines"]["sans relance"]["la_mediane_stricte"]
    if h is None or h0 is None:
        return {"decidable": False, "lissue": "indécidable : aucune graine ne touche un tour"}
    f_ = lambda x: f"{x:g}".replace(".", ",") + (" tour publié" if x <= 1 else " tours publiés")  # noqa: E731
    tete = f"jugée strictement, la chaîne bornée descend {f_(h)} en médiane, contre {f_(h0)} pour la chaîne sans relance"
    suite = ("elle garde ses six tours" if h >= 6 else "elle reste devant la chaîne sans relance" if h > h0
             else "elle ne descend pas plus loin que la chaîne sans relance")
    return {"decidable": True, "h": h, "h0": h0, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    publiees = {n: json.loads((LES_MESURES / f).read_text()) for n, f in LES_CHAINES.items()}
    nappes = {g["le_rang"]: {t: x["la_lecture"] for t, x in g["la_nappe"].items()} for g in publiees["sans relance"]["les_graines"]}
    b = publiees["bornée"]["les_graines"]["PHercParis4"]
    d = {"la_question": __doc__.splitlines()[0], "les_sources": LES_CHAINES,
         "les_nappes_saccordent": all(g["les_cotes"][c]["les_tours_de_la_nappe"] == nappes[g["le_rang"]] for g in b for c in g["les_cotes"]),
         "les_chaines": {n: juger(n, x, nappes) for n, x in publiees.items()}}
    d["le_verdict"] = le_verdict(d)
    if not d["les_nappes_saccordent"]:
        d["le_verdict"] = {"decidable": False, "lissue": "indécidable : la nappe de 330 n'est pas celle que 336 a lue"}
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

    t_ = lambda *r: {str(x): ("retrouve" if x in r else "ne retrouve pas") for x in range(0, -8, -1)}  # noqa: E731
    nl = {str(x): "non lue" for x in range(0, -8, -1)}
    surf = [t_(), t_(0), t_(-1), t_(-2, -3), t_(-3), t_(-4)]
    st = la_descente_stricte(surf)
    so = m330.la_descente([{int(k): x for k, x in s.items()} for s in surf])
    v("★★★★★ une surface qui retrouve le tour attendu et un autre arrête la descente stricte, pas la descente de 330",
      (st["la_descente"], st["larret"]) == (1, "deux tours") and so["la_descente"] == 4, f"{st} {so}")
    v("★★★★ la descente stricte part de la première surface qui retrouve un seul tour",
      la_descente_stricte([t_(0, -1), t_(-1), t_(-2)])["le_tour_de_depart"] == -1)
    v("★★★★ un saut faux, un tour manqué, une surface non lue",
      la_descente_stricte([t_(0), t_(-3)])["larret"] == "un saut faux" and la_descente_stricte([t_(0), t_()])["larret"] == "un tour manqué"
      and la_descente_stricte([t_(0), nl])["larret"] == "non lue")
    v("★★★ sans surface qui retrouve un seul tour, aucun tour touché", la_descente_stricte([t_(), t_(0, -1)])["larret"] == "aucun tour touché")
    tout = [t_(-k) for k in range(0, 8)]
    v("★★★ au bout des tours chargés", la_descente_stricte(tout + [t_()])["larret"] == "le bout des tours chargés"
      and la_descente_stricte(tout)["la_descente"] == 7)

    nappes = {1: t_()}
    d331 = {"les_graines": {"PHercParis4": [{"le_rang": 1, "les_cotes": {"moins": {"les_surfaces": [
        {"les_tours": t_(0)}, {"les_tours": t_(-1)}, {"la_part_relancee": None}], "la_descente": 1, "larret": "non lue"}}}]}}
    j = juger("relancée depuis un point", d331, nappes)
    v("★★★★ une relance absente est lue « non lue », et la descente recomptée redonne celle publiée",
      j["redonne"] and j["les_graines"][0]["les_cotes"]["moins"]["stricte"]["larret"] == "non lue", str(j))
    d331["les_graines"]["PHercParis4"][0]["les_cotes"]["moins"]["larret"] = "un tour manqué"
    v("★★★★ un arrêt publié que le recompte ne redonne pas est signalé", not juger("relancée depuis un point", d331, nappes)["redonne"])
    d331["les_graines"]["PHercParis4"][0]["les_cotes"]["moins"].update(larret="non lue", la_descente=2)
    v("★★★★ une descente publiée que le recompte ne redonne pas est signalée", not juger("relancée depuis un point", d331, nappes)["redonne"])
    d330 = {"les_graines": [{"le_rang": 1, "les_cotes": {"moins": {"les_spires": [{"les_tours": {k: {"la_lecture": x} for k, x in t_(0).items()}},
                                                                                   {"les_tours": {k: {"la_lecture": x} for k, x in t_(-1).items()}}],
                                                                   "la_descente": 1, "larret": "le bout de la chaîne"}}}]}
    v("★★★ les lectures de 330 sont lues dans leurs dictionnaires", juger("sans relance", d330, nappes)["redonne"])
    d2 = {"les_graines": [{"le_rang": 1, "les_cotes": {
        "plus": {"les_spires": [{"les_tours": {k: {"la_lecture": x} for k, x in t_().items()}}], "la_descente": 0,
                 "larret": "aucun tour touché"},
        "moins": {"les_spires": [{"les_tours": {k: {"la_lecture": x} for k, x in t_(0).items()}},
                                 {"les_tours": {k: {"la_lecture": x} for k, x in t_(-1, -2).items()}}], "la_descente": 1,
                  "larret": "le bout de la chaîne"}}}]}
    g = juger("sans relance", d2, nappes)["les_graines"][0]
    v("★★★ à égalité de descente, l'arrêt rapporté est celui du côté qui a touché un tour",
      g["la_descente_stricte"] == 0 and g["larret_strict"] == "deux tours", str(g["larret_strict"]))

    ch = lambda h, r=True: {"redonne": r, "la_mediane_stricte": h}  # noqa: E731
    vd = le_verdict({"les_chaines": {"sans relance": ch(4.0), "bornée": ch(6.0)}})
    v("★★★★ h ≥ 6 : elle garde ses six tours", vd["lissue"].endswith("elle garde ses six tours"), vd["lissue"])
    vd = le_verdict({"les_chaines": {"sans relance": ch(3.0), "bornée": ch(4.5)}})
    v("★★★★ h < 6 et h > h0 : elle reste devant", vd["lissue"].endswith("elle reste devant la chaîne sans relance"))
    vd = le_verdict({"les_chaines": {"sans relance": ch(4.5), "bornée": ch(4.5)}})
    v("★★★★ h ≤ h0 : elle ne descend pas plus loin", vd["lissue"].endswith("elle ne descend pas plus loin que la chaîne sans relance"))
    v("★★★★ une chaîne que le recompte ne redonne pas rend la tranche indécidable",
      not le_verdict({"les_chaines": {"sans relance": ch(4.0, False), "bornée": ch(6.0)}})["decidable"])

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
