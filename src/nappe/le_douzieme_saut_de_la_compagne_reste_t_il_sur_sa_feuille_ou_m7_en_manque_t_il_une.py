"""Sur la graine 4, côté moins, de PHerc0358, le douzième saut de la compagne, que m7 compte nul, la laisse-t-il sur la feuille de sa onzième surface, ou m7 manque-t-il la feuille qu'il franchit ?

⚠⚠⚠ CE FICHIER EST ÉCRIT APRÈS AVOIR LU LES PAIRES QUE `389` PUBLIE AUTOUR DE CE SAUT, ET AVANT D'EN TIRER UN COMPTE. Ce qui était vu avant
d'écrire : tout ce que `296` à `390` publient, dont `R4-F576` (sur la graine 4, côté moins, le vote désigne la compagne, dont les
contradictions s'installent à partir de son douzième saut) ; les nombres de feuilles de `389` (le douzième saut de la compagne est le seul
de ses seize que `m7` compte nul) ; et la liste des paires même feuille de la compagne avec la suivie et la tierce entre leurs dixième et
seizième surfaces.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P188`. Si le saut est resté sur la feuille, la compagne compte juste et le glissement est
ailleurs ; si `m7` a manqué la feuille franchie, la compagne compte un tour de moins à partir de là, et la limite de `389` tient au compte, pas
à la chaîne.

## Ce qui est fait

- **Le compte des voisines** d'une surface de la compagne : sur ses paires même feuille avec la suivie et avec la tierce, les comptes de `m7`
  que portent ces surfaces voisines ; le compte des voisines est le plus fréquent, le plus petit à égalité ; aucun sans paire même feuille.
- **L'avance** du douzième saut : le compte des voisines de la douzième surface moins celui de la onzième.
- **La règle** : une avance d'un tour, **non, la compagne a franchi une feuille que `m7` ne compte pas** ; une avance nulle, **oui, elle est
  restée sur la feuille** ; sinon, indécidable, comme si l'une des deux surfaces n'a pas de compte des voisines.

## Les issues

L'issue de la tranche : **les voisines placent la onzième surface à c11 tours et la douzième à c12**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les surfaces voisines de la onzième et de la douzième surface, et l'avance des sauts voisins de la compagne, du dixième au seizième.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi `m7` compte ce saut nul ; elle ne lit pas `m7`, seulement les paires et les comptes de `389`.

Usage :
    uv run python src/nappe/le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.py --verifier
    uv run python src/nappe/le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.py \\
        --json docs/mesures/le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
LE_COTE = (4, "moins")
LA_CHAINE = "compagne"
LE_SAUT = 12


def les_voisines(paires: dict, comptes: dict, x: str, h: int) -> list[tuple[str, int, int]]:
    """Les surfaces des deux autres chaînes sur la même feuille que la surface `h` de `x` : la chaîne, son saut et son compte."""
    out = []
    for k, ps in paires.items():
        a, b = k.split("|")
        if x not in (a, b):
            continue
        y = b if a == x else a
        for p, q, m in ps:
            hx, hy = (p, q) if a == x else (q, p)
            if m and hx == h:
                out.append((y, hy, comptes[y][hy - 1]))
    return sorted(out)


def le_compte_des_voisines(voisines: list[tuple]) -> int | None:
    """Le compte le plus fréquent des surfaces voisines, le plus petit à égalité ; None sans voisine."""
    if not voisines:
        return None
    n = Counter(w for _, _, w in voisines)
    haut = max(n.values())
    return min(w for w, m in n.items() if m == haut)


def le_verdict(d: dict) -> dict:
    c11, c12 = d["le_compte_des_voisines"][str(LE_SAUT - 1)], d["le_compte_des_voisines"][str(LE_SAUT)]
    if c11 is None or c12 is None:
        return {"decidable": False, "lissue": "indécidable : une des deux surfaces n'a pas de surface voisine sur sa feuille"}
    tete = f"les voisines placent la onzième surface de la compagne à {c11} tours et la douzième à {c12}"
    a = c12 - c11
    if a == 1:
        suite = "non, la compagne a franchi une feuille que m7 ne compte pas"
    elif a == 0:
        suite = "oui, elle est restée sur la feuille"
    else:
        return {"decidable": False, "lissue": f"indécidable : {tete}, une avance de {a}"}
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d389 = json.loads(CE_QUE_389_A_PUBLIE.read_text())
    c = next(x for x in d389["les_cotes"] if (x["le_rang"], x["le_cote"]) == LE_COTE)
    sauts = range(10, len(c["les_comptes"][LA_CHAINE]) + 1)
    voisines = {str(h): les_voisines(c["les_paires"], c["les_comptes"], LA_CHAINE, h) for h in sauts}
    comptes = {h: le_compte_des_voisines(v) for h, v in voisines.items()}
    d = {"la_question": __doc__.splitlines()[0], "le_cote": list(LE_COTE), "la_chaine": LA_CHAINE, "le_saut": LE_SAUT,
         "le_nombre_de_feuilles_de_m7": c["les_nombres"][LA_CHAINE][LE_SAUT - 1],
         "les_comptes_de_la_compagne": c["les_comptes"][LA_CHAINE], "les_voisines": voisines, "le_compte_des_voisines": comptes,
         "les_avances": {str(h): (None if comptes[str(h)] is None or comptes[str(h - 1)] is None else comptes[str(h)] - comptes[str(h - 1)])
                         for h in sauts if str(h - 1) in comptes}}
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

    paires = {"suivie|compagne": [[11, 11, True], [12, 11, True], [12, 12, True], [11, 12, False]],
              "compagne|tierce": [[11, 12, True], [12, 13, True], [12, 12, False]], "suivie|tierce": [[1, 1, True]]}
    comptes = {"suivie": list(range(1, 17)), "compagne": list(range(1, 12)) + list(range(11, 16)), "tierce": [1, 2, 3, 4] + list(range(4, 16))}
    v("★★★★ les voisines : les surfaces même feuille des deux autres chaînes, avec leurs comptes, quel que soit l'ordre de la paire",
      les_voisines(paires, comptes, "compagne", 11) == [("suivie", 11, 11), ("suivie", 12, 12), ("tierce", 12, 11)]
      and les_voisines(paires, comptes, "compagne", 12) == [("suivie", 12, 12), ("tierce", 13, 12)], str(les_voisines(paires, comptes, "compagne", 11)))
    v("★★★★ le compte des voisines : le plus fréquent, le plus petit à égalité ; aucun sans voisine",
      le_compte_des_voisines([("s", 1, 11), ("s", 2, 12), ("t", 3, 11)]) == 11 and le_compte_des_voisines([("s", 1, 11), ("s", 2, 12)]) == 11
      and le_compte_des_voisines([]) is None)
    v("★★★ les paires d'autres feuilles ne font pas de voisines", ("suivie", 12, 12) not in les_voisines({"suivie|compagne": [[12, 11, False]]},
                                                                                                        comptes, "compagne", 11))

    def d_(a, b):
        return {"le_compte_des_voisines": {"11": a, "12": b}}
    v("★★★★ la règle : une avance d'un tour, non ; nulle, oui ; sinon ou sans voisine, indécidable",
      le_verdict(d_(11, 12))["lissue"].endswith("que m7 ne compte pas") and le_verdict(d_(11, 11))["lissue"].endswith("restée sur la feuille")
      and not le_verdict(d_(11, 13))["decidable"] and not le_verdict(d_(None, 12))["decidable"]
      and "la onzième surface de la compagne à 11 tours et la douzième à 12" in le_verdict(d_(11, 12))["lissue"])

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
