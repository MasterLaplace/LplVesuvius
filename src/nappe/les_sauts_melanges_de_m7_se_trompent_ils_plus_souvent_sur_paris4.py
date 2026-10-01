"""Sur PHercParis4, les sauts dont le compte majoritaire de m7 est porté par moins des deux tiers des points donnent-ils des comptes faux plus souvent que les autres ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES SAUTS DE PHERCPARIS4 NE SOIENT RANGÉS EN MÉLANGES ET EN SAUTS NETS. Ce qui était vu avant d'écrire :
tout ce que `296` à `393` publient, dont `R4-F579` (sur PHerc0358, un saut nul de `m7` est presque toujours un mélange, et le compte
majoritaire s'y trompe parfois) et `R4-F571` (sur PHercParis4, l'accord aux comptes de `m7` valide 58 surfaces lues, toutes sur le bon
tour). ⚠ Cette tranche ne lit pas `m7` : elle relit les comptes point par point que `385` publie et les tours retrouvés que `379` publie.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P191`. Si un saut dont le compte majoritaire est faible se trompe plus souvent, l'accord peut
le tenir pour incertain au lieu de lui faire confiance ; PHercParis4 dit saut par saut si le compte est juste.

## Ce qui est fait

- **Les sauts jugés** : sur les côtés moins de PHercParis4, chaque saut dont `m7` dit le nombre de feuilles, et dont la surface d'arrivée et
  celle de départ (la nappe pour le premier) retrouvent chacune un seul tour publié. Le saut est **juste** si son nombre de feuilles égale le
  nombre de tours entre ces deux tours, dans le sens du côté.
- **Mélange ou net** : un saut est un **mélange** si son compte majoritaire est porté par moins des deux tiers de ses points mesurés.
- **La règle** : si les mélanges sont faux au moins deux fois plus souvent que les sauts nets, **oui** ; s'ils ne le sont pas plus souvent,
  **non** ; sinon, **en partie**. Indécidable sous 10 mélanges jugés.

## Les issues

L'issue de la tranche : **f des m mélanges jugés sont faux, contre f' des n sauts nets**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts faux, avec leur nombre de feuilles, leur nombre de tours et leur répartition de points.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la même règle sur PHerc0358, dont les feuilles s'écartent autrement.

Usage :
    uv run python src/nappe/les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.py --verifier
    uv run python src/nappe/les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.py \\
        --json docs/mesures/les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
CE_QUE_385_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"
LES_CHAINES = ("suivie", "compagne", "tierce")
LA_PART_DU_MELANGE = 2 / 3
LE_RAPPORT, LE_MINIMUM = 2.0, 10


def la_part_majoritaire(comptes: dict) -> float | None:
    n = sum(comptes.values())
    return round(max(comptes.values()) / n, 4) if n else None


def les_sauts(c379: dict, c385: dict) -> list[dict]:
    """Les sauts jugés d'un côté moins : nombre de feuilles, nombre de tours entre les deux lectures, part majoritaire."""
    sens = m344.LE_SENS[c379["le_cote"]]
    out = []
    for x in LES_CHAINES:
        r = c379["les_retrouves"][x]
        for s in c385["les_sauts"][x]:
            h, n = s["le_saut"], s["le_nombre_de_feuilles"]
            if n is None or h >= len(r) or len(r[h]) != 1 or len(r[h - 1]) != 1:
                continue
            tours = sens * (r[h][0] - r[h - 1][0])
            out.append({"le_rang": c379["le_rang"], "la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": n, "les_tours": tours,
                        "juste": n == tours, "la_part_majoritaire": la_part_majoritaire(s["les_comptes"]), "les_comptes": s["les_comptes"]})
    return out


def le_bilan(sauts: list[dict]) -> dict:
    m = [s for s in sauts if s["la_part_majoritaire"] is not None and s["la_part_majoritaire"] < LA_PART_DU_MELANGE]
    n = [s for s in sauts if s["la_part_majoritaire"] is not None and s["la_part_majoritaire"] >= LA_PART_DU_MELANGE]
    return {"melanges": {"juges": len(m), "faux": sum(not s["juste"] for s in m)}, "nets": {"juges": len(n), "faux": sum(not s["juste"] for s in n)}}


def le_verdict(d: dict) -> dict:
    m, n = d["le_bilan"]["melanges"], d["le_bilan"]["nets"]
    if m["juges"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {m['juges']} mélanges jugés, moins de {LE_MINIMUM}"}
    tete = f"{m['faux']} des {m['juges']} mélanges jugés sont faux, contre {n['faux']} des {n['juges']} sauts nets"
    pm = m["faux"] / m["juges"]
    pn = n["faux"] / n["juges"] if n["juges"] else 0.0
    suite = ("oui, les mélanges se trompent plus souvent" if pm >= LE_RAPPORT * pn and pm > pn else "non" if pm <= pn else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d379, d385 = (json.loads(x.read_text()) for x in (CE_QUE_379_A_PUBLIE, CE_QUE_385_A_PUBLIE))
    sauts = []
    for c3, c5 in zip(d379["les_cotes"], d385["les_cotes"]):
        assert (c3["le_rang"], c3["le_cote"]) == (c5["le_rang"], c5["le_cote"])
        if c3["le_cote"] == "moins":
            sauts += les_sauts(c3, c5)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_part_du_melange": round(LA_PART_DU_MELANGE, 4), "le_rapport": LE_RAPPORT, "le_minimum": LE_MINIMUM},
         "les_sauts": sauts}
    d["le_bilan"] = le_bilan(sauts)
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

    v("★★★★ la part majoritaire", la_part_majoritaire({"0": 60, "1": 30, "2": 10}) == 0.6 and la_part_majoritaire({}) is None)
    c3 = {"le_rang": 1, "le_cote": "moins", "les_retrouves": {"suivie": [[0], [-1], [-1, -2], [-3]], "compagne": [[], [0], [-1]],
                                                                "tierce": [[0], [-2]]}}
    c5 = {"les_sauts": {"suivie": [{"le_saut": 1, "le_nombre_de_feuilles": 1, "les_comptes": {"1": 9, "0": 1}},
                                   {"le_saut": 2, "le_nombre_de_feuilles": 1, "les_comptes": {"1": 5}},
                                   {"le_saut": 3, "le_nombre_de_feuilles": 1, "les_comptes": {"1": 5}}],
                        "compagne": [{"le_saut": 1, "le_nombre_de_feuilles": 1, "les_comptes": {"1": 5}},
                                     {"le_saut": 2, "le_nombre_de_feuilles": 0, "les_comptes": {"0": 5, "1": 4}}],
                        "tierce": [{"le_saut": 1, "le_nombre_de_feuilles": 1, "les_comptes": {"1": 5, "0": 5}}]}}
    ss = les_sauts(c3, c5)
    vu = {(s["la_chaine"], s["le_saut"]): (s["les_tours"], s["juste"]) for s in ss}
    v("★★★★ les sauts jugés : deux lectures à un seul tour, le nombre de tours dans le sens du côté, juste s'il égale le nombre de feuilles",
      vu == {("suivie", 1): (1, True), ("compagne", 2): (1, False), ("tierce", 1): (2, False)}, str(vu))
    b = le_bilan(ss)
    v("★★★★ le bilan : mélanges sous les deux tiers, nets au-dessus", b == {"melanges": {"juges": 2, "faux": 2}, "nets": {"juges": 1, "faux": 0}},
      str(b))

    def d_(fm, m, fn, n):
        return {"le_bilan": {"melanges": {"juges": m, "faux": fm}, "nets": {"juges": n, "faux": fn}}}
    v("★★★★ la règle : deux fois plus faux, oui ; pas plus, non ; sinon, en partie",
      le_verdict(d_(4, 10, 10, 100))["lissue"].endswith("plus souvent") and le_verdict(d_(1, 10, 10, 100))["lissue"].endswith("; non")
      and le_verdict(d_(3, 20, 10, 100))["lissue"].endswith("; en partie")
      and "4 des 10 mélanges jugés sont faux, contre 10 des 100 sauts nets" in le_verdict(d_(4, 10, 10, 100))["lissue"])
    v("★★★ indécidable sous 10 mélanges jugés", not le_verdict(d_(4, 9, 10, 100))["decidable"])

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
