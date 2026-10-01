"""Sur PHerc0358, aux comptes de m7, l'accord de trois chaînes valide-t-il encore des surfaces quand les chaînes sont lancées à seize sauts au lieu de huit ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE NE SOIT LANCÉE AU-DELÀ DE HUIT SAUTS AVEC LES COMPTES DE `m7`. Ce qui était vu avant d'écrire :
tout ce que `296` à `388` publient, dont `R4-F570` (aux comptes de `m7`, l'accord valide 78 surfaces sur six côtés de PHerc0358, jusqu'à 7
tours, au bout des huit sauts), `R4-F571` et `R4-F573` (sur PHercParis4, les surfaces qu'il valide sont sur le bon tour, chaîne par chaîne
et dans un repère commun), et `R4-F496` (à seize sauts, la chaîne de `303` tenait 6 côtés sur 10, mais `m7` n'appuyait plus que 15 à 16 % au
seizième saut).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P186`. Le Grand Prize demande un rouleau entier ; une surface validée à 7 tours de sa nappe au
bout de huit sauts ne dit pas jusqu'où l'accord porte. Lancer les chaînes plus loin le dit.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373` sur les seize côtés, la chaîne d'une maille de `366` jusqu'à 16 sauts au lieu de 8 ; rien
  d'autre ne change. Leurs huit premiers sauts doivent redonner les points et les nombres de feuilles de `384`.
- **Les comptes, les paires et l'accord** : les comptes de `m7` de `384`, les paires de `368`, l'accord de `374`, sur toutes les surfaces.
- **La règle** : des surfaces validées au-delà du huitième saut sur au moins deux côtés, **oui, l'accord valide encore au-delà de huit
  sauts** ; sur un seul, **en partie** ; sur aucun, **non**. Indécidable si une lecture échoue ou si les huit premiers sauts ne redonnent
  pas `384`.

## Les issues

L'issue de la tranche : **à seize sauts, l'accord valide v surfaces au-delà du huitième saut, sur c côtés, jusqu'à t tours de la nappe**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté, les surfaces validées en tout et au-delà du huitième saut, le plus grand compte validé, et combien de sauts portent encore
des points.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée au-delà du huitième saut est sur la bonne feuille ; PHercParis4 n'a des tours
publiés que jusqu'à `5753_-7`.

Usage :
    uv run python src/nappe/laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.py --verifier
    uv run python src/nappe/laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.py \\
        --json docs/mesures/laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json
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
import la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358 as m366  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus as m380  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_384_A_PUBLIE = LES_MESURES / "les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.json"
LES_SAUTS = 16
LES_HUIT = m331.LES_SAUTS
LES_CHAINES = m374.LES_CHAINES


def enchainer(nappe, relancer, sauter, lire_valeurs):
    """La chaîne d'une maille de `366`, jusqu'à seize sauts."""
    return m366.la_chaine_dune_maille_de_0358(nappe, relancer, sauter, lire_valeurs, sauts=LES_SAUTS)


def redonne_384(sauts: dict, c384: dict) -> bool:
    """Les huit premiers sauts de chaque chaîne ont les nombres de feuilles et les points mesurés que `384` publie."""
    return all([(s["le_nombre_de_feuilles"], s["les_mesures"]) for s in sauts[x][:LES_HUIT]]
               == [(s["le_nombre_de_feuilles"], s["les_mesures"]) for s in c384["les_sauts"][x]] for x in LES_CHAINES)


def le_resume(cote: dict) -> dict:
    validees = [s for s in cote["les_surfaces"] if s["le_statut"] == m374.VALIDEE]
    au_dela = [s for s in validees if s["le_saut"] > LES_HUIT]
    return {"validees": len(validees), "au_dela": len(au_dela),
            "le_plus_loin": max((s["le_compte"] for s in validees), default=None),
            "le_plus_loin_au_dela": max((s["le_compte"] for s in au_dela), default=None),
            "les_validees": [[s["la_chaine"], s["le_saut"], s["le_compte"]] for s in validees]}


def le_bilan(cotes: list[dict]) -> dict:
    r = [c["le_resume"] for c in cotes]
    return {"validees": sum(x["validees"] for x in r), "au_dela": sum(x["au_dela"] for x in r),
            "les_cotes_au_dela": sum(1 for x in r if x["au_dela"]),
            "le_plus_loin": max((x["le_plus_loin"] for x in r if x["le_plus_loin"] is not None), default=None),
            "le_plus_loin_au_dela": max((x["le_plus_loin_au_dela"] for x in r if x["le_plus_loin_au_dela"] is not None), default=None)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_384"):
        return {"decidable": False, "lissue": "indécidable : les huit premiers sauts ne redonnent pas 384"}
    b = d["le_bilan"]
    tete = f"à seize sauts, l'accord valide {b['au_dela']} surfaces au-delà du huitième saut, sur {b['les_cotes_au_dela']} côtés"
    if b["au_dela"]:
        tete += f", jusqu'à {b['le_plus_loin_au_dela']} tours de la nappe"
    n = b["les_cotes_au_dela"]
    suite = "oui, l'accord valide encore au-delà de huit sauts" if n >= 2 else "en partie" if n == 1 else "non"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    d384 = json.loads(CE_QUE_384_A_PUBLIE.read_text())
    tous = [(c["le_rang"], c["le_cote"]) for c in d384["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(enchainer), cotes=set(tous))
    redonne, cotes = len(chaines) == len(tous), []
    for c, e, c384 in zip(chaines, m383._LES_CHAINES_ENTIERES, d384["les_cotes"]):
        surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
        s369 = {x: m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x]) for x in LES_CHAINES}
        nombres = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
        sauts = {x: [{**a, "le_nombre_de_feuilles": b["le_nombre_de_feuilles"], "les_mesures": b["les_mesures"]}
                     for a, b in zip(s369[x], nombres[x])] for x in LES_CHAINES}
        redonne &= (c["le_rang"], c["le_cote"]) == (c384["le_rang"], c384["le_cote"]) and redonne_384(sauts, c384)
        paires = {"|".join(k): m368.les_paires(surf[k[0]], surf[k[1]]) for k in m373.LES_COUPLES}
        cote = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: m384.les_comptes_de_m7(sauts[x]) for x in LES_CHAINES})
        resume = le_resume(cote)
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "le_resume": resume,
                      "les_sauts_portant_des_points": {x: sum(1 for u in surf[x] if len(u[0])) for x in LES_CHAINES},
                      "les_nombres": {x: [s["le_nombre_de_feuilles"] for s in sauts[x]] for x in LES_CHAINES},
                      "les_comptes": {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(sauts[x])] for x in LES_CHAINES},
                      "les_couples": {k: [v["tiennent"], v["les_paires"]] for k, v in cote["les_couples"].items()},
                      "les_paires": {k: [[p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]] for p in v] for k, v in paires.items()},
                      "les_surfaces": cote["les_surfaces"]})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne),
                          "points": cotes[-1]["les_sauts_portant_des_points"], "resume": {k: v for k, v in resume.items() if k != "les_validees"}},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"les_sauts": LES_SAUTS, "les_huit": LES_HUIT},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_384": bool(redonne), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    import inspect

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

    v("★★★★ seize sauts, et la chaîne de 366 garde huit sauts par défaut",
      LES_SAUTS == 16 and LES_HUIT == 8 and inspect.signature(m366.la_chaine_dune_maille_de_0358).parameters["sauts"].default == 8)
    sa = lambda *ns: [{"le_nombre_de_feuilles": n, "les_mesures": 100} for n in ns]  # noqa: E731
    c384 = {"les_sauts": {x: sa(*([1] * 8)) for x in LES_CHAINES}}
    v("★★★★ redonne 384 : les huit premiers sauts, nombres et points mesurés",
      redonne_384({x: sa(*([1] * 16)) for x in LES_CHAINES}, c384)
      and not redonne_384({**{x: sa(*([1] * 16)) for x in LES_CHAINES}, "tierce": sa(*([1] * 7 + [2] + [1] * 8))}, c384)
      and redonne_384({**{x: sa(*([1] * 16)) for x in LES_CHAINES}, "tierce": sa(*([1] * 8 + [2] * 8))}, c384)
      and not redonne_384({**{x: sa(*([1] * 16)) for x in LES_CHAINES},
                           "suivie": [{"le_nombre_de_feuilles": 1, "les_mesures": 99}] + sa(*([1] * 15))}, c384))
    s_ = lambda h, w, st=m374.VALIDEE: {"la_chaine": "suivie", "le_saut": h, "le_compte": w, "le_statut": st}  # noqa: E731
    r = le_resume({"les_surfaces": [s_(3, 3), s_(9, 9), s_(12, 11), s_(13, 13, m374.CONTREDITE)]})
    v("★★★★ le résumé : les validées, celles au-delà du huitième saut, et leurs plus grands comptes",
      (r["validees"], r["au_dela"], r["le_plus_loin"], r["le_plus_loin_au_dela"]) == (3, 2, 11, 11), str(r))
    v("★★★★ le huitième saut n'est pas au-delà", le_resume({"les_surfaces": [s_(8, 8)]})["au_dela"] == 0)
    b = le_bilan([{"le_resume": r}, {"le_resume": le_resume({"les_surfaces": [s_(2, 2)]})}, {"le_resume": le_resume({"les_surfaces": []})}])
    v("★★★★ le bilan", (b["validees"], b["au_dela"], b["les_cotes_au_dela"], b["le_plus_loin"], b["le_plus_loin_au_dela"]) == (4, 2, 1, 11, 11),
      str(b))

    def d_(n, ok=True, pannes=()):
        return {"redonne_384": ok, "les_pannes": list(pannes),
                "le_bilan": {"au_dela": 7 if n else 0, "les_cotes_au_dela": n, "le_plus_loin_au_dela": 12 if n else None}}
    v("★★★★ la règle : deux côtés, oui ; un, en partie ; aucun, non",
      le_verdict(d_(2))["lissue"].endswith("au-delà de huit sauts") and le_verdict(d_(1))["lissue"].endswith("; en partie")
      and le_verdict(d_(0))["lissue"].endswith("; non") and "jusqu'à 12 tours" in le_verdict(d_(2))["lissue"])
    v("★★★ indécidable sans redonne ou sur une panne", not le_verdict(d_(2, ok=False))["decidable"]
      and not le_verdict(d_(2, pannes=("x",)))["decidable"] and le_verdict(d_(2))["decidable"])

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
