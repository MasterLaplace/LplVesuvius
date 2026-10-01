"""Sur PHerc0358, les sauts que 369 compte doubles franchissent-ils deux feuilles de m7, et que deviennent les comptes des surfaces que l'accord de trois chaînes valide ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES FEUILLES DE `m7` NE SOIENT COMPTÉES AILLEURS QUE SUR LA GRAINE 4, CÔTÉ PLUS. Ce qui était vu avant
d'écrire : tout ce que `296` à `383` publient, dont `R4-F569` (sur la graine 4, côté plus, les trois premiers sauts franchissent une feuille
de `m7`, dont deux de 1,67 et 1,76 pas que `369` compte doubles), `R4-F566` (sur les graines 4, côté moins, et 6, côté plus, `380` valide 25
surfaces dont chaque chaîne commence par un saut compté double, entre 1,67 et 1,93 pas) et la liste des sauts de `380` : 12 sauts comptés
doubles sur les seize côtés, dont 10 premiers sauts.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P181`. Les surfaces que l'accord valide portent un compte : le nombre de tours qui les sépare
de la nappe. Si la règle des sauts doubles de `369` compte un tour de trop là où les feuilles s'écartent, tous les comptes qui suivent un tel
saut sont faux d'autant, et l'accord valide des surfaces sur la bonne feuille au mauvais compte.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373` sur les seize côtés, rejouées comme `380` ; leurs surfaces redonnent les points, et leurs sauts
  les écarts, que `380` publie, et les statuts qu'elles donnent aux comptes de `369` sont ceux de `380`.
- **Le compte** : celui de `383`, pour chaque saut de chaque chaîne : le nombre de feuilles de `m7` que porte le plus de points mesurés, au
  moins 50, sans égal.
- **Les comptes de `m7`** : chaque saut ajoute au compte le nombre de feuilles qu'il franchit, là où ce nombre est dit ; ailleurs, ce que
  `369` lui donne. L'accord de `374` est relu avec ces comptes, sur les mêmes paires.
- **Le contrôle** : là où `369` compte un saut simple, `m7` doit dire une feuille sous au moins 75 % des sauts dont le nombre est dit ; sans
  quoi le compte de `m7` ne mesure pas les sauts de PHerc0358 et la tranche est indécidable.
- **La règle** : parmi les sauts que `369` compte doubles et dont le nombre est dit, si au moins 75 % franchissent deux feuilles, **oui** ;
  au plus 25 %, **non, la plupart n'en franchissent qu'une** ; sinon, **en partie**. Indécidable sous 5 sauts doubles dits.

## Les issues

L'issue de la tranche : **sur PHerc0358, d des n sauts que `369` compte doubles franchissent deux feuilles de `m7`**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Les sauts nuls de `369` et ce que `m7` en dit ; côté par côté, les surfaces que l'accord valide aux comptes de `369` et aux comptes de `m7`,
et le plus grand compte validé.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée aux comptes de `m7` est sur la bonne feuille, ni si `m7` manque une feuille
entre deux surfaces.

Usage :
    uv run python src/nappe/les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.py --verifier
    uv run python src/nappe/les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.py \\
        --json docs/mesures/les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358.json
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
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus as m380  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
LES_CHAINES = m374.LES_CHAINES
LA_PART, LA_PART_BASSE = 0.75, 0.25
LE_MINIMUM = 5
LES_PAS = m369.LES_PAS


def les_comptes_de_m7(sauts: list[dict]) -> list[dict]:
    """Les sauts d'une chaîne recomptés : chacun ajoute le nombre de feuilles de `m7` qu'il franchit, là où il est dit, sinon ce que `369`
    lui donne."""
    out, w = [], 0
    for s in sauts:
        n = s["le_nombre_de_feuilles"]
        w += LES_PAS[s["le_genre"]] if n is None else n
        out.append({**s, "le_compte_corrige": w})
    return out


def le_bilan_des_genres(cotes: list[dict]) -> dict:
    """Par genre de `369`, les sauts, ceux dont le nombre est dit, et combien franchissent zéro, une, deux feuilles et plus."""
    out = {}
    for g in (m369.NUL, m369.SIMPLE, m369.DOUBLE):
        ss = [s for c in cotes for x in LES_CHAINES for s in c["les_sauts"][x] if s["le_genre"] == g]
        dits = [s["le_nombre_de_feuilles"] for s in ss if s["le_nombre_de_feuilles"] is not None]
        out[g] = {"les_sauts": len(ss), "dits": len(dits), "zero": dits.count(0), "une": dits.count(1), "deux": dits.count(2),
                  "plus": sum(n > 2 for n in dits)}
    return out


def le_controle(genres: dict) -> bool:
    s = genres[m369.SIMPLE]
    return bool(s["dits"] and s["une"] >= LA_PART * s["dits"])


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_380"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 380"}
    g = d["les_genres"]
    if not le_controle(g):
        return {"decidable": False, "lissue": "indécidable : m7 ne dit pas une feuille sous les trois quarts des sauts simples de 369"}
    dd = g[m369.DOUBLE]
    if dd["dits"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {dd['dits']} sauts doubles dits, moins de {LE_MINIMUM}"}
    tete = f"sur PHerc0358, {dd['deux']} des {dd['dits']} sauts que 369 compte doubles franchissent deux feuilles de m7"
    p = dd["deux"] / dd["dits"]
    suite = ("oui, ils franchissent deux feuilles" if p >= LA_PART else "non, la plupart n'en franchissent qu'une" if p <= LA_PART_BASSE
             else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def le_resume(cote: dict) -> dict:
    validees = [s for s in cote["les_surfaces"] if s["le_statut"] == m374.VALIDEE]
    return {"validees": len(validees), "le_plus_loin": max((s["le_compte"] for s in validees), default=None),
            "les_validees": [[s["la_chaine"], s["le_saut"], s["le_compte"]] for s in validees]}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    d380 = json.loads(CE_QUE_380_A_PUBLIE.read_text())
    tous = [(c["le_rang"], c["le_cote"]) for c in d380["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(), cotes=set(tous))
    redonne, cotes = len(chaines) == len(tous), []
    for c, e, c380 in zip(chaines, m383._LES_CHAINES_ENTIERES, d380["les_cotes"]):
        surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
        points = {x: [int(len(u[0])) for u in surf[x]] for x in LES_CHAINES}
        s369 = {x: m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x]) for x in LES_CHAINES}
        paires = {"|".join(k): m368.les_paires(surf[k[0]], surf[k[1]]) for k in m373.LES_COUPLES}
        avant = m380.le_cote(c["le_rang"], c["le_cote"], paires, s369)
        redonne &= ((c["le_rang"], c["le_cote"]) == (c380["le_rang"], c380["le_cote"])
                    and m383.redonne_380(points, {x: [s["lecart_median"] for s in s369[x]] for x in LES_CHAINES}, c380)
                    and m380.les_statuts(avant) == m380.les_statuts(c380))
        comptes = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
        sauts = {x: [{**a, "le_nombre_de_feuilles": b["le_nombre_de_feuilles"], "les_comptes_de_m7": b["les_comptes"],
                      "les_mesures": b["les_mesures"]} for a, b in zip(s369[x], comptes[x])] for x in LES_CHAINES}
        apres = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: les_comptes_de_m7(sauts[x]) for x in LES_CHAINES})
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "suivi_par_324": c380["suivi_par_324"],
                      "les_sauts": {x: [{q: s[q] for q in ("le_saut", "lecart_median", "le_genre", "le_compte_corrige", "le_nombre_de_feuilles",
                                                             "les_comptes_de_m7", "les_mesures")} for s in sauts[x]] for x in LES_CHAINES},
                      "avec_369": le_resume(avant), "avec_m7": le_resume(apres), "les_surfaces_avec_m7": apres["les_surfaces"]})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne),
                          "nombres": {x: [s["le_nombre_de_feuilles"] for s in sauts[x]] for x in LES_CHAINES},
                          "validees": (cotes[-1]["avec_369"]["validees"], cotes[-1]["avec_m7"]["validees"])}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_380": bool(redonne), "les_cotes": cotes}
    d["les_genres"] = le_bilan_des_genres(cotes)
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

    sa = lambda *xs: [{"le_saut": h, "le_genre": g, "le_nombre_de_feuilles": n} for h, (g, n) in enumerate(xs, 1)]  # noqa: E731
    r = les_comptes_de_m7(sa((m369.DOUBLE, 1), (m369.SIMPLE, 1), (m369.NUL, None), (m369.SIMPLE, None), (m369.DOUBLE, 2)))
    v("★★★★ les comptes de m7 : le nombre de feuilles là où il est dit, le genre de 369 ailleurs",
      [s["le_compte_corrige"] for s in r] == [1, 2, 2, 3, 5], str([s["le_compte_corrige"] for s in r]))
    v("★★★★ un nombre de zéro feuille est un compte de zéro, pas un nombre absent",
      [s["le_compte_corrige"] for s in les_comptes_de_m7(sa((m369.SIMPLE, 0), (m369.SIMPLE, 1)))] == [0, 1])
    cc = [{"les_sauts": {"suivie": sa((m369.DOUBLE, 1), (m369.DOUBLE, 2), (m369.SIMPLE, 1), (m369.SIMPLE, None), (m369.NUL, 0)),
                         "compagne": sa((m369.DOUBLE, 3), (m369.SIMPLE, 2)), "tierce": []}}]
    g = le_bilan_des_genres(cc)
    v("★★★★ le bilan des genres : sauts, dits, et zéro, une, deux feuilles et plus",
      g[m369.DOUBLE] == {"les_sauts": 3, "dits": 3, "zero": 0, "une": 1, "deux": 1, "plus": 1}
      and g[m369.SIMPLE] == {"les_sauts": 3, "dits": 2, "zero": 0, "une": 1, "deux": 1, "plus": 0}
      and g[m369.NUL] == {"les_sauts": 1, "dits": 1, "zero": 1, "une": 0, "deux": 0, "plus": 0}, str(g))
    gs = lambda une, dits: {m369.SIMPLE: {"une": une, "dits": dits}}  # noqa: E731
    v("★★★★ le contrôle : une feuille sous au moins 75 % des sauts simples dits",
      le_controle(gs(75, 100)) and not le_controle(gs(74, 100)) and not le_controle(gs(0, 0)))

    def d_(deux, dits, ok=True, une_s=90, pannes=()):
        return {"redonne_380": ok, "les_pannes": list(pannes),
                "les_genres": {m369.SIMPLE: {"une": une_s, "dits": 100}, m369.DOUBLE: {"deux": deux, "dits": dits}}}
    v("★★★★ la règle : 75 % oui, 25 % au plus non, sinon en partie",
      le_verdict(d_(9, 12))["lissue"].endswith("franchissent deux feuilles") and le_verdict(d_(3, 12))["lissue"].endswith("qu'une")
      and le_verdict(d_(6, 12))["lissue"].endswith("; en partie") and le_verdict(d_(4, 12))["lissue"].endswith("; en partie")
      and "3 des 12 sauts que 369 compte doubles" in le_verdict(d_(3, 12))["lissue"])
    v("★★★ indécidable sous 5 doubles dits, sans contrôle, sans redonne, ou sur une panne",
      not le_verdict(d_(4, 4))["decidable"] and not le_verdict(d_(9, 12, une_s=70))["decidable"]
      and not le_verdict(d_(9, 12, ok=False))["decidable"] and not le_verdict(d_(9, 12, pannes=("x",)))["decidable"]
      and le_verdict(d_(5, 5))["decidable"])
    cote = {"les_surfaces": [{"la_chaine": "suivie", "le_saut": 1, "le_compte": 2, "le_statut": m374.VALIDEE},
                             {"la_chaine": "tierce", "le_saut": 3, "le_compte": 4, "le_statut": m374.VALIDEE},
                             {"la_chaine": "tierce", "le_saut": 4, "le_compte": 9, "le_statut": m374.CONTREDITE}]}
    v("★★★ le résumé : les validées et le plus grand compte validé",
      le_resume(cote) == {"validees": 2, "le_plus_loin": 4, "les_validees": [["suivie", 1, 2], ["tierce", 3, 4]]})

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
