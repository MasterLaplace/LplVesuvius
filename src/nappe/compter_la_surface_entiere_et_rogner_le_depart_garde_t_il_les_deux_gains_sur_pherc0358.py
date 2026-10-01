"""Sur PHerc0358, des chaînes rognées dont chaque saut est compté sur sa surface entière, avant rognage, gardent-elles les contradictions défaites par 397 sans perdre ses validées ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE ROGNÉE NE SOIT COMPTÉE SUR SES SURFACES ENTIÈRES. Ce qui était vu avant d'écrire : tout ce que
`296` à `398` publient, dont `R4-F583` (rognées, les chaînes ont 53 mélanges au lieu de 96, 131 contredites au lieu de 161 et 75 validées au
lieu de 89) et `R4-F584` (sur la graine 6, côté moins, le rognage ne déplace pas les chaînes, il change leurs comptes : la compagne rognée
compte une feuille de trop).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P196`. Le rognage fait deux choses à la fois : il change le départ du saut suivant, et il change
la surface que l'on compte et que l'on apparie. Compter et apparier la surface entière, et ne rogner que le départ du saut suivant, sépare
les deux effets.

## Ce qui est fait

- **Les chaînes** : celles de `397`, rognées de la même façon ; leurs surfaces rognées comptées comme `397` les compte doivent redonner ses
  nombres de feuilles. Chaque surface gardée garde aussi sa forme entière, d'avant rognage.
- **Le compte et l'appariement** : chaque saut est compté par `m7` de la surface d'où il part (la surface rognée du saut précédent, la nappe
  pour le premier) à sa surface **entière** ; les paires de `368`, le genre de `369` et l'accord de `374` se font sur les surfaces entières.
- **La règle** : si les contredites sont au plus les 131 de `397` et les validées au moins les 89 de `389`, **oui, les deux gains tiennent** ;
  si les contredites sont au moins les 161 de `389`, ou les validées au plus les 75 de `397`, **non** ; sinon, **en partie**. Indécidable si
  une lecture échoue, ou si les surfaces rognées ne redonnent pas `397`.

## Les issues

L'issue de la tranche : **comptées entières, les chaînes rognées ont c contredites et v validées, contre 161 et 89 pour `389` et 131 et 75
pour `397`**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les mélanges ; côté par côté, les validées et les contredites des trois manières.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés.

Usage :
    uv run python src/nappe/compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.py --verifier
    uv run python src/nappe/compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.py \\
        --json docs/mesures/compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.json
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
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402
import rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358 as m395  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_397_A_PUBLIE = LES_MESURES / "une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.json"
LES_CHAINES = m374.LES_CHAINES


def rogner_en_gardant(depart: dict, garde: dict) -> dict:
    """La surface rognée de `397`, qui garde sous `valide_entier` le masque de la surface d'avant rognage."""
    return {**m397.rogner(depart, garde), "valide_entier": garde["valide"]}


def enchainer(nappe, relancer, sauter, lire_valeurs):
    """La chaîne de `397`, dont chaque surface gardée se souvient de sa forme entière."""
    return m366.la_chaine_dune_maille_de_0358(nappe, relancer, sauter, lire_valeurs, sauts=m389.LES_SAUTS, rogner=rogner_en_gardant)


def entiere(rl: dict | None) -> dict | None:
    """La surface entière d'une surface gardée, d'avant rognage."""
    if rl is None:
        return None
    return {"la_nappe": rl["la_nappe"], "valide": rl.get("valide_entier", rl["valide"])}


def les_sauts_entiers(nappe: dict, chaine: list[dict], compter, ecart) -> list[dict]:
    """Chaque saut d'une chaîne, compté de la surface d'où il part (rognée) à sa surface entière, avec le genre de `369` pris de même."""
    out, avant = [], nappe
    for h, k in enumerate(chaine, 1):
        rl = k.get("la_relance")
        arrivee = entiere(rl)
        f = compter(avant, arrivee)
        c = ecart(arrivee, avant)
        out.append({"le_saut": h, "le_genre": m369.le_genre(c), "le_nombre_de_feuilles": f["le_nombre_de_feuilles"],
                    "les_mesures": f["les_mesures"], "les_comptes": f["les_comptes"]})
        avant = rl
    return out


def le_bilan(cotes: list[dict]) -> dict:
    return {"validee": sum(c["les_statuts"][m374.VALIDEE] for c in cotes), "contredite": sum(c["les_statuts"][m374.CONTREDITE] for c in cotes),
            "les_melanges": sum(c["les_melanges"] for c in cotes)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_397"):
        return {"decidable": False, "lissue": "indécidable : les surfaces rognées ne redonnent pas 397"}
    b, a, r = d["le_bilan"], d["389"], d["397"]
    tete = (f"comptées entières, les chaînes rognées ont {b['contredite']} contredites et {b['validee']} validées, contre {a['contredite']} et "
            f"{a['validee']} pour 389 et {r['contredite']} et {r['validee']} pour 397")
    suite = ("oui, les deux gains tiennent" if b["contredite"] <= r["contredite"] and b["validee"] >= a["validee"]
             else "non" if b["contredite"] >= a["contredite"] or b["validee"] <= r["validee"] else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    m397._LES_ROGNAGES.clear()
    d397 = json.loads(CE_QUE_397_A_PUBLIE.read_text())
    tous = [(c["le_rang"], c["le_cote"]) for c in d397["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(enchainer), cotes=set(tous))
    redonne, cotes = len(chaines) == len(tous), []
    compter = lambda a, b: m383.le_compte(a, b, lv0)  # noqa: E731
    ecart = lambda s, a: m369.lecart_du_saut(m367.les_points(s), m367.les_points(a))  # noqa: E731
    for c, e, c397 in zip(chaines, m383._LES_CHAINES_ENTIERES, d397["les_cotes"]):
        rognes = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
        redonne &= ((c["le_rang"], c["le_cote"]) == (c397["le_rang"], c397["le_cote"])
                    and all([s["le_nombre_de_feuilles"] for s in rognes[x]] == [s["le_nombre_de_feuilles"] for s in c397["les_sauts"][x]]
                            for x in LES_CHAINES))
        sauts = {x: les_sauts_entiers(e["les_nappes"][x], e["les_chaines"][x], compter, ecart) for x in LES_CHAINES}
        surf = {x: [m367.les_points(entiere(k.get("la_relance"))) for k in e["les_chaines"][x]] for x in LES_CHAINES}
        paires = {"|".join(k): m368.les_paires(surf[k[0]], surf[k[1]]) for k in m373.LES_COUPLES}
        cote = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: m384.les_comptes_de_m7(sauts[x]) for x in LES_CHAINES})
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts, "les_statuts": m395.les_statuts(cote),
                      "les_melanges": sum(m395.est_un_melange(s) for x in LES_CHAINES for s in sauts[x]),
                      "les_paires": {k: [[p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]] for p in v] for k, v in paires.items()},
                      "les_surfaces": [[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"]] for s in cote["les_surfaces"]]})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne), "statuts": cotes[-1]["les_statuts"]},
                         ensure_ascii=False), flush=True)
    b397 = d397["le_bilan"]
    d = {"la_question": __doc__.splitlines()[0], "les_pannes": list(stats0["pannes"]),
         "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"}, "redonne_397": bool(redonne),
         "389": dict(d397["la_reference"]), "397": {"validee": b397["validee"], "contredite": b397["contredite"],
                                                    "les_melanges": b397["les_melanges"]},
         "les_statuts_389": d397["la_reference_par_cote"],
         "les_statuts_397": {f"{c['le_rang']} {c['le_cote']}": c["les_statuts"] for c in d397["les_cotes"]}, "les_cotes": cotes}
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

    ii, jj = np.meshgrid(np.arange(12, dtype=float), np.arange(12, dtype=float), indexing="ij")
    plan = {"la_nappe": np.stack([jj, ii, np.zeros_like(ii)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    marche = {"la_nappe": np.stack([jj, ii, np.where(jj < 6, 0.0, 12.0)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    r = rogner_en_gardant(plan, marche)
    v("★★★★ la surface rognée garde son masque entier", r["valide_entier"].all() and not r["valide"].all()
      and entiere(r)["valide"].all() and entiere(None) is None and entiere(plan)["valide"] is plan["valide"])
    a1 = {"la_nappe": plan["la_nappe"], "valide": np.ones((12, 12), dtype=bool), "valide_entier": np.ones((12, 12), dtype=bool)}
    a1["valide"][:, :6] = False
    a2 = {"la_nappe": plan["la_nappe"], "valide": np.ones((12, 12), dtype=bool)}
    vus = []

    def compter(dep, arr):
        vus.append((int(dep["valide"].sum()), int(arr["valide"].sum())))
        return {"le_nombre_de_feuilles": 1, "les_mesures": 5, "les_comptes": {"1": 5}}
    sa = les_sauts_entiers(plan, [{"la_relance": a1}, {"la_relance": a2}], compter, lambda s, a: {"en_face": 0, "lecart_median": None})
    v("★★★★ chaque saut est compté de la surface rognée d'où il part à sa surface entière",
      vus == [(144, 144), (72, 144)] and [s["le_genre"] for s in sa] == ["simple", "simple"], str(vus))

    def d_(c, v_, ok=True):
        return {"redonne_397": ok, "les_pannes": [], "le_bilan": {"contredite": c, "validee": v_},
                "389": {"contredite": 161, "validee": 89}, "397": {"contredite": 131, "validee": 75}}
    v("★★★★ la règle : contredites au plus 131 et validées au moins 89, oui ; contredites au moins 161 ou validées au plus 75, non ; sinon, en partie",
      le_verdict(d_(131, 89))["lissue"].endswith("tiennent") and le_verdict(d_(161, 100))["lissue"].endswith("; non")
      and le_verdict(d_(120, 75))["lissue"].endswith("; non") and le_verdict(d_(140, 85))["lissue"].endswith("; en partie")
      and le_verdict(d_(130, 80))["lissue"].endswith("; en partie")
      and "ont 140 contredites et 85 validées, contre 161 et 89 pour 389 et 131 et 75 pour 397" in le_verdict(d_(140, 85))["lissue"])
    v("★★★ indécidable sans redonne", not le_verdict(d_(120, 95, ok=False))["decidable"])

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
