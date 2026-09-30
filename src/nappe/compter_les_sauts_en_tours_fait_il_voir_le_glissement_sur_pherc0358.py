"""Sur PHerc0358, un saut compté en tours au seuil que `370` étalonne, rapporté aux sauts de sa chaîne, fait-il voir dans la chaîne seule le glissement que l'accord de deux chaînes révèle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT NE SOIT RECOMPTÉ, MAIS APRÈS AVOIR LU LES ÉCARTS QUE `369` PUBLIE. Ce qui était vu avant
d'écrire : tout ce que `296` à `370` publient, dont `R4-F555` (sur PHerc0358, corrigés des sauts nuls au quart de pas et doubles au pas et
demi, 90 des 134 paires d'une chaîne suivie et de sa compagne tiennent les comptes, contre 77 ; sur la graine 7, côté plus, le saut où
tombe le glissement s'écarte de 23,438 voxels quand les sauts simples s'écartent de 15,667 en médiane) et `R4-F556` (sur PHercParis4,
rapportés à la médiane des écarts à un tour de leur chaîne, les écarts à un tour vont de 0,9023 à 1,1633, à deux tours de 1,7655 à
2,1899, à trois tours de 2,6201 à 3,0883). ⚠ Cette tranche ne lit pas `m7` : elle recompte les sauts que `369` publie.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P168`. Le seuil d'un pas et demi de `369` était trop haut ; sur PHercParis4, un saut à
deux tours s'écarte deux fois plus qu'un saut à un tour. Rapporté aux sauts de sa propre chaîne, le seuil ne dépend plus du pas de chaque
rouleau.

## Ce qui est fait

- **Les sauts** : ceux des chaînes suivies et compagnes de `369`, sur les cinq côtés, avec l'écart que `369` publie de chacun à la
  surface d'où il part.
- **La référence d'une chaîne** : la médiane des écarts de ses sauts qui ont 50 points en face et ne sont pas nuls.
- **Les tours d'un saut** : 0 s'il est nul, au quart de pas comme dans `369` ; 1 sans 50 points en face ; sinon, rapporté à la référence
  de sa chaîne, 1 au plus au seuil de `370` entre un et deux tours, 2 au plus au milieu des rapports à deux et à trois tours de `370`, 3
  au-delà. **Le compte** d'une surface : la somme des tours de ses sauts, jusqu'à elle.
- **Les paires** : celles de `368`, que `369` publie ; une paire tient les comptes si « même feuille » et « même compte » disent la même
  chose.
- **La règle** : si au moins 90 % des paires tiennent les comptes, **oui, compté en tours, le glissement se voit dans la chaîne seule** ;
  si pas plus qu'avec les comptes corrigés de `369`, **non** ; sinon, **en partie**.

## Les issues

L'issue de la tranche : **comptés en tours, a des n paires tiennent les comptes, contre a' sous les comptes corrigés de `369`**, puis ce
que dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts par nombre de tours ; les paires qui tiennent les comptes au seuil de `370` en pas, sans rapporter à la chaîne.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un saut compté à deux tours en franchit vraiment deux, ni laquelle des deux chaînes a raison là
où elles ne tiennent toujours pas les comptes.

Usage :
    uv run python src/nappe/compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.py --verifier
    uv run python src/nappe/compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.py \\
        --json docs/mesures/compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_369_A_PUBLIE = LES_MESURES / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
CE_QUE_370_A_PUBLIE = LES_MESURES / "lecart_dun_saut_separe_t_il_un_tour_de_deux_sur_paris4.json"
LE_PAS = m368.LE_PAS
LE_QUART = m368.LE_QUART


def les_seuils(d370: dict) -> dict:
    """Les deux seuils que `370` étalonne, rapportés à la chaîne : entre un et deux tours, et entre deux et trois tours, au milieu ; et les
    mêmes en pas, sans rapporter."""
    b, p, pas = d370["le_bilan"], d370["le_bilan"]["par_tours"], d370["les_constantes"]["le_pas"]
    return {"deux": b["le_seuil_rapporte"], "trois": round((p["2"]["rapporte_plus_grand"] + p["3"]["rapporte_plus_petit"]) / 2, 4),
            "deux_en_pas": round(b["le_seuil"] / pas, 4),
            "trois_en_pas": round((p["2"]["le_plus_grand"] + p["3"]["le_plus_petit"]) / 2 / pas, 4)}


def lisible(s: dict) -> bool:
    return s["en_face"] >= m368.LE_MINIMUM_EN_FACE and s["lecart_median"] is not None


def la_reference(sauts: list[dict]) -> float | None:
    """La médiane des écarts des sauts lisibles et non nuls de la chaîne."""
    e = [s["lecart_median"] for s in sauts if lisible(s) and s["lecart_median"] > LE_QUART]
    return statistics.median(e) if e else None


def les_tours(s: dict, reference: float | None, seuils: dict) -> int:
    if not lisible(s):
        return 1
    if s["lecart_median"] <= LE_QUART:
        return 0
    if reference is None:
        return 1
    r = s["lecart_median"] / reference
    return 1 if r <= seuils["deux"] else 2 if r <= seuils["trois"] else 3


def recompter(sauts: list[dict], seuils: dict, reference: float | None = None) -> list[dict]:
    """Chaque saut de la chaîne, ses tours et le compte de sa surface ; la référence est celle de la chaîne, sauf si elle est donnée."""
    ref = la_reference(sauts) if reference is None else reference
    out, compte = [], 0
    for s in sauts:
        t = les_tours(s, ref, seuils)
        compte += t
        out.append({"le_saut": s["le_saut"], "lecart_median": s["lecart_median"],
                    "le_rapport": round(s["lecart_median"] / ref, 4) if lisible(s) and ref else None, "les_tours": t, "le_compte": compte})
    return out


def tient(p: dict, suivie: list[dict], compagne: list[dict]) -> bool:
    return bool(p["meme_feuille"] == (suivie[p["le_saut_suivi"] - 1]["le_compte"] == compagne[p["le_saut_compagnon"] - 1]["le_compte"]))


def le_cote(c: dict, seuils: dict) -> dict:
    """Un côté de `369` recompté en tours, rapporté à chaque chaîne, et au seuil en pas sans rapporter."""
    suivie, compagne = recompter(c["suivie"], seuils), recompter(c["compagne"], seuils)
    en_pas = {"deux": seuils["deux_en_pas"], "trois": seuils["trois_en_pas"]}
    su, co = recompter(c["suivie"], en_pas, reference=LE_PAS), recompter(c["compagne"], en_pas, reference=LE_PAS)
    return {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "suivie": suivie, "compagne": compagne,
            "les_paires": len(c["les_paires"]), "tiennent": sum(tient(p, suivie, compagne) for p in c["les_paires"]),
            "tiennent_369": sum(m369.tient_le_compte(p, c["suivie"], c["compagne"]) for p in c["les_paires"]),
            "tiennent_brut": sum(p["tient_les_comptes"] for p in c["les_paires"]),
            "tiennent_en_pas": sum(tient(p, su, co) for p in c["les_paires"])}


def le_bilan(cotes: list[dict]) -> dict:
    tours = {str(k): sum(s["les_tours"] == k for c in cotes for n in ("suivie", "compagne") for s in c[n]) for k in (0, 1, 2, 3)}
    return {**{k: sum(c[k] for c in cotes) for k in ("les_paires", "tiennent", "tiennent_369", "tiennent_brut", "tiennent_en_pas")},
            "les_sauts_par_tours": tours}


def le_verdict(d: dict) -> dict:
    if not d.get("369_decidable"):
        return {"decidable": False, "lissue": "indécidable : 369 n'a pas conclu"}
    if not d.get("redonne_369"):
        return {"decidable": False, "lissue": "indécidable : les comptes corrigés relus ne redonnent pas ceux que 369 publie"}
    b = d["le_bilan"]
    if not b["les_paires"]:
        return {"decidable": False, "lissue": "indécidable : aucune paire"}
    tete = (f"comptés en tours, {b['tiennent']} des {b['les_paires']} paires tiennent les comptes, contre {b['tiennent_369']} sous les "
            f"comptes corrigés de 369")
    if b["tiennent"] >= 0.9 * b["les_paires"]:
        suite = "oui, compté en tours, le glissement se voit dans la chaîne seule"
    elif b["tiennent"] <= b["tiennent_369"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d369, d370 = json.loads(CE_QUE_369_A_PUBLIE.read_text()), json.loads(CE_QUE_370_A_PUBLIE.read_text())
    seuils = les_seuils(d370)
    cotes = [le_cote(c, seuils) for c in d369["les_cotes"]]
    d = {"la_question": __doc__.splitlines()[0], "les_seuils": seuils, "le_quart": LE_QUART, "le_pas": LE_PAS,
         "369_decidable": bool(d369["le_verdict"].get("decidable")), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
    d["redonne_369"] = d["le_bilan"]["tiennent_369"] == d369["le_bilan"]["tiennent_corrige"] and \
        d["le_bilan"]["tiennent_brut"] == d369["le_bilan"]["tiennent_brut"]
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

    d370 = {"le_bilan": {"le_seuil": 17.0, "le_seuil_rapporte": 1.46,
                         "par_tours": {"2": {"rapporte_plus_grand": 2.2, "le_plus_grand": 24.0},
                                       "3": {"rapporte_plus_petit": 2.6, "le_plus_petit": 30.0}}}, "les_constantes": {"le_pas": 18.0}}
    v("★★★★ les seuils de 370 : un et deux tours, deux et trois tours au milieu, rapportés et en pas",
      les_seuils(d370) == {"deux": 1.46, "trois": 2.4, "deux_en_pas": 0.9444, "trois_en_pas": 1.5}, str(les_seuils(d370)))
    s_ = lambda h, e, n=60: {"le_saut": h, "lecart_median": e, "en_face": n}  # noqa: E731
    sauts = [s_(1, 14.0), s_(2, 0.5), s_(3, 16.0), s_(4, 23.0), s_(5, 40.0, n=49), s_(6, 40.0), s_(7, 15.0)]
    v("★★★★ la référence : la médiane des sauts lisibles et non nuls",
      la_reference(sauts) == 16.0 and la_reference([s_(1, 5.0), s_(2, 40.0, n=10)]) is None, str(la_reference(sauts)))
    seuils = {"deux": 1.46, "trois": 2.4, "deux_en_pas": 0.9444, "trois_en_pas": 1.5}
    r = recompter(sauts, seuils)
    v("★★★★ les tours : 0 au quart de pas, 1 illisible, puis 1, 2 ou 3 au rapport à la référence ; le compte cumule",
      [x["les_tours"] for x in r] == [1, 0, 1, 1, 1, 3, 1] and [x["le_compte"] for x in r] == [1, 1, 2, 3, 4, 7, 8], str(r))
    v("★★★★ aux bornes : 1 au seuil de deux tours compris, 2 au seuil de trois compris, 0 au quart de pas compris",
      [les_tours(s_(0, e), 100.0, seuils) for e in (146.0, 146.01, 240.0, 240.01, LE_QUART)] == [1, 2, 2, 3, 0])
    v("★★★★ une référence donnée remplace celle de la chaîne",
      [x["les_tours"] for x in recompter([s_(1, 20.0), s_(2, 40.0)], seuils, reference=20.0)] == [1, 2])
    sv = [{"le_compte": w} for w in (1, 1, 2, 3)]
    cp = [{"le_compte": w} for w in (1, 2, 3, 4)]
    p = lambda h, k, m: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    v("★★★★ tenir les comptes : même feuille exactement au même compte",
      tient(p(3, 2, True), sv, cp) and not tient(p(2, 2, True), sv, cp) and tient(p(2, 2, False), sv, cp))
    c = {"le_rang": 7, "le_cote": "plus",
         "suivie": [{**s_(1, 10.0), "le_compte_corrige": 1}, {**s_(2, 16.0), "le_compte_corrige": 2}, {**s_(3, 9.0), "le_compte_corrige": 3}],
         "compagne": [{**s_(1, 10.0), "le_compte_corrige": 1}, {**s_(2, 11.0), "le_compte_corrige": 2}, {**s_(3, 9.0), "le_compte_corrige": 3}],
         "les_paires": [{**p(1, 1, True), "tient_les_comptes": True}, {**p(2, 3, True), "tient_les_comptes": False}]}
    cote = le_cote(c, seuils)
    v("★★★★ un côté : le glissement d'un saut double se voit compté en tours, pas sous les comptes corrigés ni en pas",
      (cote["tiennent"], cote["tiennent_369"], cote["tiennent_brut"], cote["tiennent_en_pas"]) == (2, 1, 1, 1)
      and [x["les_tours"] for x in cote["suivie"]] == [1, 2, 1], str(cote))
    b = le_bilan([cote])
    v("★★★★ le bilan somme les côtés et compte les sauts par tours",
      b == {"les_paires": 2, "tiennent": 2, "tiennent_369": 1, "tiennent_brut": 1, "tiennent_en_pas": 1,
            "les_sauts_par_tours": {"0": 0, "1": 5, "2": 1, "3": 0}}, str(b))

    def d_(t, t369, n=100, ok=True):
        return {"369_decidable": True, "redonne_369": ok, "le_bilan": {"les_paires": n, "tiennent": t, "tiennent_369": t369}}
    v("★★★★ la règle : 90 %, oui ; pas plus que 369, non ; sinon en partie",
      le_verdict(d_(90, 67))["lissue"].endswith("dans la chaîne seule") and le_verdict(d_(67, 67))["lissue"].endswith("; non")
      and le_verdict(d_(89, 67))["lissue"].endswith("en partie") and le_verdict(d_(60, 67))["lissue"].endswith("; non"))
    v("★★★ indécidable si les comptes relus ne redonnent pas 369", not le_verdict(d_(95, 67, ok=False))["decidable"])

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
