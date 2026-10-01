"""Sur PHerc0358, une chaîne qui retire de chaque surface la plage restée sur la surface d'où elle part a-t-elle moins de sauts mélangés, et l'accord s'y contredit-il moins ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE NE SOIT LANCÉE EN ROGNANT SES SURFACES. Ce qui était vu avant d'écrire : tout ce que `296` à
`396` publient, dont `R4-F582` (un mélange de `m7` est une surface à cheval ; dans un mélange de zéro et une feuille, la plage à zéro est à
0,02 pas de la surface de départ, la plage à une feuille à 0,69), `R4-F581` (le compte majoritaire de `m7` reste le meilleur compte connu)
et `R4-F575` (à seize sauts, l'accord valide 89 surfaces et en contredit 161).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P194`. Une plage retombée sur la surface de départ est une part de la surface qui n'a pas sauté.
Si elle reste, le saut suivant part en partie de la feuille d'avant, et le retard s'hérite (`R4-F548`). La retirer scinde la surface au lieu
de corriger son compte.

## Ce qui est fait

- **Les chaînes** : les trois chaînes à seize sauts de `389` sur les seize côtés, rien d'autre ne change que ceci : chaque surface gardée
  est **rognée** avant d'être enregistrée et d'être le départ du saut suivant (le crochet `rogner` de `356`).
- **Le rognage** : pour chaque maille de la surface gardée qui a une normale, son écart à la surface de départ le long de sa normale, comme
  `345` le prend ; la maille est **retombée** si cet écart est dit et sous un quart de pas. Les mailles retombées sont retirées si les
  mailles **parties** (écart dit, d'au moins un quart de pas) sont au moins le tiers des mailles dont l'écart est dit ; sinon la surface est
  gardée entière : une surface presque toute retombée est un saut nul, pas une surface à cheval.
- **Les comptes et l'accord** : les comptes de `m7` de `384`, les paires de `368`, l'accord de `374`, sur les chaînes rognées ; un mélange
  comme `394` le prend.
- **La règle**, contre les chaînes de `389` (89 validées, 161 contredites) : si les chaînes rognées sont moins contredites et valident au
  moins autant, **oui** ; moins contredites mais moins validées, **en partie** ; pas moins contredites, **non**. Indécidable si une lecture
  échoue, ou si aucune surface n'est rognée.

## Les issues

L'issue de la tranche : **rogner r surfaces fait passer les mélanges de m à m', les contredites de c à c' et les validées de v à v'**, puis
ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les mailles retirées ; côté par côté, les validées et les contredites ; les sauts que `m7` compte.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés.

Usage :
    uv run python src/nappe/une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.py --verifier
    uv run python src/nappe/une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.py \\
        --json docs/mesures/une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.json
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

from la_spire_voisine_est_elle_a_un_pas import les_normales  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358 as m366  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus as m380  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402
import rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358 as m395  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_395_A_PUBLIE = LES_MESURES / "rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358.json"
LES_CHAINES = m374.LES_CHAINES
LE_QUART = 0.25
LE_TIERS = 1 / 3
_LES_ROGNAGES: list[dict] = []


def rogner(depart: dict, garde: dict, pas: float = m383.LE_PAS, lateral: float = m383.LE_LATERAL) -> dict:
    """La surface gardée sans sa plage retombée sur la surface de départ, si ce qui est parti en est au moins le tiers ; entière sinon."""
    nn, nok = les_normales(garde["la_nappe"], garde["valide"])
    m = garde["valide"] & nok
    d = m321.les_ecarts(garde["la_nappe"][m], nn[m], depart["la_nappe"][depart["valide"]], lateral=lateral)
    dit = np.isfinite(d)
    tombe = dit & (np.abs(np.where(dit, d, 0.0)) < LE_QUART * pas)
    parti = dit & ~tombe
    rognee = bool(tombe.any() and parti.sum() >= LE_TIERS * dit.sum())
    _LES_ROGNAGES.append({"retombees": int(tombe.sum()), "parties": int(parti.sum()), "rognee": rognee})
    if not rognee:
        return garde
    retire = np.zeros_like(garde["valide"])
    retire[m] = tombe
    return {**garde, "valide": garde["valide"] & ~retire}


def enchainer(nappe, relancer, sauter, lire_valeurs):
    """La chaîne d'une maille de `389`, à seize sauts, dont chaque surface gardée est rognée."""
    return m366.la_chaine_dune_maille_de_0358(nappe, relancer, sauter, lire_valeurs, sauts=m389.LES_SAUTS, rogner=rogner)


def le_bilan(cotes: list[dict], rognages: list[dict]) -> dict:
    return {"validee": sum(c["les_statuts"][m374.VALIDEE] for c in cotes), "contredite": sum(c["les_statuts"][m374.CONTREDITE] for c in cotes),
            "les_melanges": sum(c["les_melanges"] for c in cotes), "les_sauts_comptes": sum(c["les_sauts_comptes"] for c in cotes),
            "les_surfaces_vues": len(rognages), "les_surfaces_rognees": sum(r["rognee"] for r in rognages),
            "les_mailles_retirees": sum(r["retombees"] for r in rognages if r["rognee"])}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    b, a = d["le_bilan"], d["la_reference"]
    if not b["les_surfaces_rognees"]:
        return {"decidable": False, "lissue": "indécidable : aucune surface n'est rognée"}
    tete = (f"rogner {b['les_surfaces_rognees']} surfaces fait passer les mélanges de {a['les_melanges']} à {b['les_melanges']}, les "
            f"contredites de {a['contredite']} à {b['contredite']} et les validées de {a['validee']} à {b['validee']}")
    suite = ("oui" if b["contredite"] < a["contredite"] and b["validee"] >= a["validee"] else "en partie" if b["contredite"] < a["contredite"]
             else "non")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    _LES_ROGNAGES.clear()
    d395 = json.loads(CE_QUE_395_A_PUBLIE.read_text())
    tous = [(c["le_rang"], c["le_cote"]) for c in d395["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(enchainer), cotes=set(tous))
    cotes = []
    for c, e in zip(chaines, m383._LES_CHAINES_ENTIERES):
        surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
        s369 = {x: m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x]) for x in LES_CHAINES}
        nombres = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
        sauts = {x: [{"le_saut": a["le_saut"], "le_genre": a["le_genre"], "le_nombre_de_feuilles": b["le_nombre_de_feuilles"],
                      "les_mesures": b["les_mesures"], "les_comptes": b["les_comptes"]} for a, b in zip(s369[x], nombres[x])] for x in LES_CHAINES}
        paires = {"|".join(k): m368.les_paires(surf[k[0]], surf[k[1]]) for k in m373.LES_COUPLES}
        cote = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: m384.les_comptes_de_m7(sauts[x]) for x in LES_CHAINES})
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts, "les_statuts": m395.les_statuts(cote),
                      "les_melanges": sum(m395.est_un_melange(s) for x in LES_CHAINES for s in sauts[x]),
                      "les_sauts_comptes": sum(s["le_nombre_de_feuilles"] is not None for x in LES_CHAINES for s in sauts[x]),
                      "les_paires": {k: [[p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]] for p in v] for k, v in paires.items()},
                      "les_surfaces": [[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"]] for s in cote["les_surfaces"]]})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "statuts": cotes[-1]["les_statuts"],
                          "melanges": cotes[-1]["les_melanges"]}, ensure_ascii=False), flush=True)
    ref = d395["le_bilan"]
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_quart": LE_QUART, "le_tiers": round(LE_TIERS, 4)},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "la_reference": {"validee": ref["aux_comptes_de_m7"][m374.VALIDEE], "contredite": ref["aux_comptes_de_m7"][m374.CONTREDITE],
                          "les_melanges": ref["les_melanges"],
                          "les_sauts_comptes": sum(s["le_nombre_de_feuilles"] is not None for c in d395["les_cotes"] for x in LES_CHAINES
                                                   for s in c["les_sauts"][x])},
         "la_reference_par_cote": {f"{c['le_rang']} {c['le_cote']}": c["aux_comptes_de_m7"] for c in d395["les_cotes"]},
         "les_rognages": list(_LES_ROGNAGES), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes, _LES_ROGNAGES)
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

    ii, jj = np.meshgrid(np.arange(12, dtype=float), np.arange(12, dtype=float), indexing="ij")
    plan = np.stack([jj, ii, np.zeros_like(ii)], axis=-1)
    depart = {"la_nappe": plan, "valide": np.ones((12, 12), dtype=bool)}
    marche = np.stack([jj, ii, np.where(jj < 6, 0.0, 12.0)], axis=-1)
    garde = {"la_nappe": marche, "valide": np.ones((12, 12), dtype=bool)}
    _LES_ROGNAGES.clear()
    r = rogner(depart, garde, pas=20.0, lateral=3.0)
    retire = garde["valide"] & ~r["valide"]
    v("★★★★ une surface à cheval perd sa plage retombée et garde sa plage partie",
      retire.any() and not retire[:, 6:].any() and r["valide"][1:-1, 7:-1].all() and retire[1:-1, 1:5].all(), str(np.argwhere(retire)[:5]))
    v("★★★★ le rognage est noté", _LES_ROGNAGES[-1]["rognee"] and _LES_ROGNAGES[-1]["retombees"] == int(retire.sum()))
    presque = {"la_nappe": np.stack([jj, ii, np.where(jj < 10, 0.0, 12.0)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    v("★★★★ une surface presque toute retombée est gardée entière", rogner(depart, presque, pas=20.0, lateral=3.0) is presque
      and not _LES_ROGNAGES[-1]["rognee"])
    haute = {"la_nappe": np.stack([jj, ii, np.full_like(ii, 12.0)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    v("★★★★ une surface toute partie est gardée entière", rogner(depart, haute, pas=20.0, lateral=3.0) is haute)

    recus = []

    def sauter(surf, ok):
        recus.append(ok.copy())
        return {"la_spire": surf + np.array([0.0, 0.0, 20.0]), "valide": ok.copy()}

    def compter(dep, arr, lv):
        return {"les_mesures": 1000, "la_part_dune_feuille": 1.0, "les_comptes": {"1": 1000}}

    def coupe(dep, g):
        o = g["valide"].copy()
        o[0, 0] = False
        return {**g, "valide": o}
    ch = m356.la_chaine_mixte({"la_nappe": plan, "valide": np.ones((12, 12), dtype=bool)}, None, sauter, None, sauts=2, compter=compter,
                              rogner=coupe)
    v("★★★★ le crochet de 356 : la surface rognée est enregistrée et elle est le départ du saut suivant",
      len(ch) == 2 and not ch[0]["la_relance"]["valide"][0, 0] and recus[0][0, 0] and not recus[1][0, 0])
    sans = m356.la_chaine_mixte({"la_nappe": plan, "valide": np.ones((12, 12), dtype=bool)}, None, sauter, None, sauts=2, compter=compter)
    v("★★★ sans crochet, rien n'est rogné", sans[1]["la_relance"]["valide"].all())

    def d_(m, c, v_, r=3):
        return {"les_pannes": [], "la_reference": {"validee": 10, "contredite": 20, "les_melanges": 30},
                "le_bilan": {"les_surfaces_rognees": r, "les_melanges": m, "contredite": c, "validee": v_}}
    v("★★★★ la règle : moins contredites et autant validées, oui ; moins contredites mais moins validées, en partie ; sinon, non",
      le_verdict(d_(25, 15, 10))["lissue"].endswith("; oui") and le_verdict(d_(25, 15, 9))["lissue"].endswith("; en partie")
      and le_verdict(d_(25, 20, 12))["lissue"].endswith("; non")
      and "rogner 3 surfaces fait passer les mélanges de 30 à 25, les contredites de 20 à 15 et les validées de 10 à 9"
      in le_verdict(d_(25, 15, 9))["lissue"])
    v("★★★ indécidable si aucune surface n'est rognée", not le_verdict(d_(25, 15, 10, r=0))["decidable"])

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
