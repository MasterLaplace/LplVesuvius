"""Sur PHerc0358, graine 8, les deux surfaces d'une paire « même feuille » à deux tours ou plus d'écart sont-elles à la même distance de la nappe, la somme des écarts de leurs sauts, l'une atteinte en plus de sauts que l'autre ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE DISTANCE NE SOIT SOMMÉE, MAIS APRÈS AVOIR LU LES PAIRES QUE `375` PUBLIE ET LES SAUTS QUE
`369` ET `373` PUBLIENT. Ce qui était vu avant d'écrire : tout ce que `296` à `375` publient, dont `R4-F561` (pour 15 des 27 paires
« même feuille » à deux tours ou plus, toutes sur la graine 8, plus des trois quarts des points en face sont à moins d'un demi-pas : les
chaînes sont sur la même feuille et leurs comptes s'écartent). Et, lu dans les paires de `375` : sur la graine 8, côté moins, les paires de
la suivie et de la compagne vont de saut en saut avec un saut d'écart, (3, 2) à (8, 7), toutes à deux tours corrigés ; celles de la suivie
et de la tierce, (1, 2) à (6, 7), à un tour ; celles de la compagne et de la tierce, (2, 4) à (5, 7), à trois tours. Côté plus, les
écarts de sauts les plus fréquents sont 1, 2 et 1, avec des paires à 4 et 5 sauts d'écart. Les sauts publiés de la graine 8 s'écartent de
11 à 27 voxels. ⚠ Cette tranche ne lit pas `m7` : elle relit les paires de `375` et les sauts de `369` et de `373`.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P173`. Deux chaînes sur la même feuille à des comptes différents : ou l'une a compté un
tour pour un saut qui n'en franchissait pas un, et les deux surfaces sont à la même distance de leurs nappes ; ou les deux nappes ne
partent pas de la même feuille, et la distance s'écarte autant que les comptes.

## Ce qui est fait

- **La distance** d'une surface à sa nappe : la somme des écarts médians de ses sauts, de la nappe jusqu'à elle, tels que `369` les publie
  pour la suivie et la compagne et `373` pour la tierce. Illisible si un saut n'a pas d'écart publié.
- **Chaque paire « même feuille »** de `375`, sur les cinq côtés : l'écart signé des distances de ses deux surfaces, rapporté au saut simple
  médian que `369` publie, 15,667 voxels. Elle est **à la même distance** si cet écart vaut moins d'un demi-saut.
- **Le contrôle** : au moins 90 % des paires lues au même compte corrigé sont à la même distance. Sinon, la distance sommée ne dit rien
  des comptes.
- **La règle** : si au moins 90 % des paires lues à deux tours ou plus sont à la même distance, **oui, l'une est atteinte en plus de
  sauts** ; si moins de la moitié, **non** ; sinon, **en partie**. Indécidable sous 5 paires lues à deux tours ou plus, si le contrôle
  échoue, ou si les comptes des sauts ne redonnent pas les écarts de comptes de `375`.

## Les issues

L'issue de la tranche : **a des n paires lues à deux tours ou plus sont à la même distance de la nappe, contre a' des n' au même compte**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Pour les paires à deux tours ou plus, combien ont un écart de distance qui, arrondi en sauts, vaut leur écart de comptes, et combien l'ont
dans le même sens ; et, couple par couple, les écarts de sauts des paires « même feuille ».

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les nappes de la graine 8 sont sur plusieurs feuilles, ni laquelle des chaînes compte mal.

Usage :
    uv run python src/nappe/une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.py --verifier
    uv run python src/nappe/une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.py \\
        --json docs/mesures/une_paire_a_plusieurs_tours_est_elle_a_la_meme_distance_de_la_nappe.json
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_373_A_PUBLIE = LES_MESURES / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
CE_QUE_375_A_PUBLIE = LES_MESURES / "les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.json"
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
MEME, UN, PLUSIEURS = "même compte", "un tour", "deux tours ou plus"
LA_MOITIE = 0.5
LA_PART = 0.9
LE_MINIMUM = 5


def les_sauts(c369: dict, c373: dict) -> dict:
    """Les sauts des trois chaînes d'un côté."""
    return {SUIVIE: c369["suivie"], COMPAGNE: c369["compagne"], TIERCE: c373["les_sauts_de_la_tierce"]}


def la_distance(sauts: list[dict], h: int) -> float | None:
    """La somme des écarts médians des sauts 1 à h ; illisible si l'un manque."""
    if h < 1 or h > len(sauts):
        return None
    ecarts = [s["lecart_median"] for s in sauts[:h]]
    return None if any(e is None for e in ecarts) else round(sum(ecarts), 3)


def la_paire(p: dict, sauts: dict, saut: float) -> dict:
    """Une paire « même feuille » de `375`, ses deux distances, leur écart signé et rapporté au saut simple médian."""
    a, b = p["le_couple"].split("|")
    h, k = p["les_sauts"]
    da, db = la_distance(sauts[a], h), la_distance(sauts[b], k)
    dc = sauts[a][h - 1]["le_compte_corrige"] - sauts[b][k - 1]["le_compte_corrige"]
    out = {key: p[key] for key in ("le_rang", "le_cote", "le_couple", "les_sauts", "lecart_de_comptes", "le_groupe")}
    out.update({"lecart_de_comptes_signe": dc, "la_distance_a": da, "la_distance_b": db, "lecart_de_distance": None, "en_sauts": None,
                "meme_distance": None, "meme_sens": None, "compte_les_tours": None})
    if da is None or db is None:
        return out
    ed = round(da - db, 3)
    r = round(abs(ed) / saut, 3)
    out.update({"lecart_de_distance": ed, "en_sauts": r, "meme_distance": abs(ed) < LA_MOITIE * saut,
                "meme_sens": (ed > 0) == (dc > 0) if dc else None, "compte_les_tours": round(abs(ed) / saut) == abs(dc)})
    return out


def redonne(paires: list[dict]) -> bool:
    """Les comptes des sauts redonnent l'écart de comptes que `375` publie pour chaque paire."""
    return bool(paires) and all(abs(p["lecart_de_comptes_signe"]) == p["lecart_de_comptes"] for p in paires)


def les_decalages(paires: list[dict]) -> dict:
    """Couple par couple, sur chaque côté, combien de paires « même feuille » à chaque écart de sauts."""
    out = collections.defaultdict(collections.Counter)
    for p in paires:
        out[f"{p['le_rang']} {p['le_cote']} {p['le_couple']}"][p["les_sauts"][0] - p["les_sauts"][1]] += 1
    return {k: dict(sorted(v.items())) for k, v in sorted(out.items())}


def le_bilan(paires: list[dict]) -> dict:
    out = {}
    for g in (MEME, UN, PLUSIEURS):
        lues = [p for p in paires if p["le_groupe"] == g and p["meme_distance"] is not None]
        out[g] = {"les_paires": sum(p["le_groupe"] == g for p in paires), "lues": len(lues),
                  "meme_distance": sum(p["meme_distance"] for p in lues),
                  "compte_les_tours": sum(p["compte_les_tours"] for p in lues),
                  "meme_sens": sum(p["meme_sens"] is True for p in lues)}
    m = out[MEME]
    out["le_controle"] = m["lues"] > 0 and m["meme_distance"] >= LA_PART * m["lues"]
    return out


def le_verdict(d: dict) -> dict:
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les comptes des sauts ne redonnent pas les écarts de comptes de 375"}
    b = d["le_bilan"]
    pl, m = b[PLUSIEURS], b[MEME]
    if pl["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {pl['lues']} paires lues à deux tours ou plus, moins de {LE_MINIMUM}"}
    if not b["le_controle"]:
        return {"decidable": False, "lissue": f"indécidable : {m['meme_distance']} des {m['lues']} paires lues au même compte sont à la "
                                              "même distance, le contrôle échoue"}
    tete = (f"{pl['meme_distance']} des {pl['lues']} paires lues à deux tours ou plus sont à la même distance de la nappe, contre "
            f"{m['meme_distance']} des {m['lues']} au même compte")
    part = pl["meme_distance"] / pl["lues"]
    suite = "oui, l'une est atteinte en plus de sauts" if part >= LA_PART else "non" if part < 0.5 else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d369, d373, d375 = (json.loads(x.read_text()) for x in (CE_QUE_369_A_PUBLIE, CE_QUE_373_A_PUBLIE, CE_QUE_375_A_PUBLIE))
    saut = d369["lecart_median_des_sauts_simples"]
    cotes = {(a["le_rang"], a["le_cote"]): les_sauts(a, b) for a, b in zip(d369["les_cotes"], d373["les_cotes"])
             if (a["le_rang"], a["le_cote"]) == (b["le_rang"], b["le_cote"])}
    paires = [la_paire(p, cotes[(p["le_rang"], p["le_cote"])], saut) for p in d375["les_paires"]]
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_saut": saut, "la_moitie": LA_MOITIE, "la_part": LA_PART,
                                                                     "le_minimum": LE_MINIMUM},
         "les_cotes_lus": len(cotes), "redonne": bool(d375.get("redonne")) and len(cotes) == 5 and redonne(paires), "les_paires": paires,
         "les_decalages": les_decalages(paires)}
    d["le_bilan"] = le_bilan(paires)
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

    s_ = lambda *es: [{"lecart_median": e, "le_compte_corrige": c} for e, c in es]  # noqa: E731
    v("★★★★ la distance : la somme des sauts 1 à h, illisible si l'un manque ou au-delà",
      la_distance(s_((10.0, 1), (12.5, 2), (None, 3)), 2) == 22.5 and la_distance(s_((10.0, 1), (None, 1)), 2) is None
      and la_distance(s_((10.0, 1)), 2) is None and la_distance(s_((10.0, 1)), 0) is None)
    sauts = {SUIVIE: s_((10.0, 1), (10.0, 2), (10.0, 3)), COMPAGNE: s_((10.0, 1), (14.9, 2), (5.0, 3)), TIERCE: s_((10.0, 1), (None, 2))}
    p_ = lambda c, h, k, g, e=1: {"le_rang": 8, "le_cote": "plus", "le_couple": c, "les_sauts": [h, k],  # noqa: E731
                                  "lecart_de_comptes": e, "le_groupe": g}
    a = la_paire(p_("suivie|compagne", 3, 2, UN), sauts, 10.0)
    v("★★★★ la paire : l'écart signé des distances, en sauts, le sens et le compte des tours",
      (a["la_distance_a"], a["la_distance_b"], a["lecart_de_distance"], a["en_sauts"], a["lecart_de_comptes_signe"])
      == (30.0, 24.9, 5.1, 0.51, 1) and a["meme_distance"] is False and a["meme_sens"] is True and a["compte_les_tours"] is True, str(a))
    b = la_paire(p_("suivie|compagne", 2, 2, MEME, 0), {SUIVIE: s_((10.0, 1), (10.0, 2)), COMPAGNE: s_((10.0, 1), (14.9, 2))}, 10.0)
    v("★★★★ à la même distance sous un demi-saut strict, sans sens au même compte",
      b["meme_distance"] is True and b["meme_sens"] is None and b["compte_les_tours"] is True, str(b))
    c = la_paire(p_("suivie|compagne", 2, 3, UN), {SUIVIE: s_((10.0, 1), (10.0, 3)), COMPAGNE: s_((10.0, 1), (10.0, 2), (5.0, 2))},
                 10.0)
    v("★★★ le sens : l'écart des distances à l'inverse de celui des comptes",
      c["lecart_de_distance"] == -5.0 and c["lecart_de_comptes_signe"] == 1 and c["meme_sens"] is False and c["meme_distance"] is False,
      str(c))
    e = la_paire(p_("suivie|compagne", 1, 3, PLUSIEURS, 2), sauts, 10.0)
    v("★★★ le sens quand la première surface compte moins que la seconde",
      (e["lecart_de_distance"], e["lecart_de_comptes_signe"], e["meme_sens"], e["compte_les_tours"]) == (-19.9, -2, True, True), str(e))
    n = la_paire(p_("suivie|compagne", 3, 3, UN), {SUIVIE: sauts[SUIVIE], COMPAGNE: s_((10.0, 1), (2.0, 1), (10.0, 2))}, 10.0)
    v("★★★ le compte des tours lu sur les comptes corrigés, pas sur les sauts bruts",
      (n["lecart_de_distance"], n["lecart_de_comptes_signe"], n["compte_les_tours"]) == (8.0, 1, True), str(n))
    t = la_paire(p_("suivie|tierce", 2, 2, MEME, 0), sauts, 10.0)
    v("★★★ une paire dont un saut n'a pas d'écart n'est pas lue", t["meme_distance"] is None and t["lecart_de_distance"] is None)
    v("★★★★ redonne : les comptes des sauts donnent l'écart de comptes de 375, et rien sans paire",
      redonne([a, b]) and not redonne([{**a, "lecart_de_comptes": 2}]) and not redonne([]))
    v("★★★ les décalages : couple par couple, les écarts de sauts",
      les_decalages([a, c, la_paire(p_("suivie|compagne", 3, 2, UN), sauts, 10.0)]) == {"8 plus suivie|compagne": {-1: 1, 1: 2}})
    pa = lambda g, m: {"le_groupe": g, "meme_distance": m, "compte_les_tours": m, "meme_sens": True}  # noqa: E731
    bl = lambda: le_bilan([pa(MEME, True)] * 9 + [pa(MEME, False), pa(MEME, None)]  # noqa: E731
                          + [pa(PLUSIEURS, True)] * 3 + [pa(PLUSIEURS, False)] * 2)
    v("★★★★ le bilan : lues, à la même distance, et le contrôle à 90 % des paires lues au même compte",
      lambda: (bl()[MEME]["les_paires"], bl()[MEME]["lues"], bl()[MEME]["meme_distance"], bl()[PLUSIEURS]["meme_distance"],
               bl()["le_controle"]) == (11, 10, 9, 3, True)
      and not le_bilan([pa(MEME, True)] * 8 + [pa(MEME, False)] * 2)["le_controle"]
      and not le_bilan([pa(PLUSIEURS, True)])["le_controle"])

    def d_(n, lues, ok=True, ctl=True):
        return {"redonne": ok, "le_bilan": {PLUSIEURS: {"lues": lues, "meme_distance": n}, MEME: {"lues": 10, "meme_distance": 9},
                                            "le_controle": ctl}}
    v("★★★★ la règle : 90 % des paires lues oui, moins de la moitié non, sinon en partie",
      le_verdict(d_(9, 10))["lissue"].endswith("en plus de sauts") and le_verdict(d_(8, 10))["lissue"].endswith("; en partie")
      and le_verdict(d_(5, 10))["lissue"].endswith("; en partie") and le_verdict(d_(4, 10))["lissue"].endswith("; non"))
    v("★★★ indécidable sous 5 paires lues, si le contrôle échoue ou sans redonne",
      not le_verdict(d_(4, 4))["decidable"] and not le_verdict(d_(9, 10, ctl=False))["decidable"]
      and not le_verdict(d_(9, 10, ok=False))["decidable"] and le_verdict(d_(5, 5))["decidable"])

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
