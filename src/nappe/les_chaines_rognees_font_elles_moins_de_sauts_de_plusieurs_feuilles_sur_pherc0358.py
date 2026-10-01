"""Sur PHerc0358, à seize sauts, les chaînes rognées font-elles moins de sauts de plus d'une feuille de m7 que les chaînes de 389 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT APRÈS QUE LES RÉPARTITIONS ONT ÉTÉ VUES, ET IL LE DIT. En préparant la tranche, j'ai compté les nombres de feuilles
des sauts dans les mesures de `389`, `397` et `399` avant d'écrire la règle : `389` a 18 sauts de plus d'une feuille, `397` en a 25, `399` 21.
La règle ci-dessous est celle que la porte appelait, et elle n'a pas été choisie pour rendre ce verdict ; mais elle a été écrite en le
connaissant. Cette tranche est donc une relecture, comme `364`, et non une mesure aveugle. Ce qui était vu aussi : tout ce que `296` à `401`
publient, dont `R4-F587` (sur PHercParis4, la suivie rognée de la graine 7 ne fait pas le triple saut de celle de `385`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P199`. Si le rognage évite les sauts de plusieurs feuilles, il doit le faire aussi sur PHerc0358.

## Ce qui est fait

- **Les sauts** : les nombres de feuilles de `m7` de chaque saut des trois chaînes, sur les seize côtés, tels que `389` (non rognées), `397`
  (rognées) et `399` (rognées, comptées entières) les publient.
- **Un saut de plusieurs feuilles** : `m7` y dit au moins deux feuilles ; la part est prise sur les sauts que `m7` compte.
- **La règle**, entre `397` et `389` : si la part des sauts de plusieurs feuilles est au plus la moitié de celle de `389`, **oui** ; si elle
  est au moins celle de `389`, **non** ; sinon, **en partie**. Indécidable sous 10 sauts de plusieurs feuilles dans `389`.

## Les issues

L'issue de la tranche : **les chaînes rognées font m sauts de plusieurs feuilles sur n comptés, contre m' sur n' pour `389`**, puis ce que
dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts nuls ; les mêmes parts pour `399` ; côté par côté, les sauts de plusieurs feuilles.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un saut que `m7` compte de deux feuilles en franchit vraiment deux ; PHerc0358 n'a pas de tours.

Usage :
    uv run python src/nappe/les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.py --verifier
    uv run python src/nappe/les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.py \\
        --json docs/mesures/les_chaines_rognees_font_elles_moins_de_sauts_de_plusieurs_feuilles_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
CE_QUE_397_A_PUBLIE = LES_MESURES / "une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.json"
CE_QUE_399_A_PUBLIE = LES_MESURES / "compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358.json"
LES_CHAINES = ("suivie", "compagne", "tierce")
LA_MOITIE, LE_MINIMUM = 0.5, 10


def le_compte(nombres: list[int | None]) -> dict:
    dits = [n for n in nombres if n is not None]
    return {"comptes": len(dits), "plusieurs": sum(n >= 2 for n in dits), "nuls": sum(n == 0 for n in dits)}


def les_nombres(d: dict, cle: str) -> dict:
    """Par côté, les nombres de feuilles de tous les sauts des trois chaînes."""
    if cle == "389":
        return {f"{c['le_rang']} {c['le_cote']}": [n for x in LES_CHAINES for n in c["les_nombres"][x]] for c in d["les_cotes"]}
    return {f"{c['le_rang']} {c['le_cote']}": [s["le_nombre_de_feuilles"] for x in LES_CHAINES for s in c["les_sauts"][x]] for c in d["les_cotes"]}


def le_verdict(d: dict) -> dict:
    a, r = d["le_bilan"]["389"], d["le_bilan"]["397"]
    if a["plusieurs"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {a['plusieurs']} sauts de plusieurs feuilles dans 389, moins de {LE_MINIMUM}"}
    tete = (f"les chaînes rognées font {r['plusieurs']} sauts de plusieurs feuilles sur {r['comptes']} comptés, contre {a['plusieurs']} sur "
            f"{a['comptes']} pour 389")
    pa, pr = a["plusieurs"] / a["comptes"], r["plusieurs"] / r["comptes"]
    suite = "oui" if pr <= LA_MOITIE * pa else "non" if pr >= pa else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    sources = {"389": CE_QUE_389_A_PUBLIE, "397": CE_QUE_397_A_PUBLIE, "399": CE_QUE_399_A_PUBLIE}
    par = {k: les_nombres(json.loads(p.read_text()), k) for k, p in sources.items()}
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_moitie": LA_MOITIE, "le_minimum": LE_MINIMUM},
         "le_bilan": {k: le_compte([n for v in par[k].values() for n in v]) for k in sources},
         "par_cote": {cote: {k: le_compte(par[k][cote]) for k in sources} for cote in par["389"]}}
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

    v("★★★★ le compte : sauts comptés, de plusieurs feuilles, nuls", le_compte([1, 2, None, 0, 3, 1]) == {"comptes": 5, "plusieurs": 2, "nuls": 1})
    v("★★★★ les nombres de 389 par côté, et ceux des chaînes rognées",
      les_nombres({"les_cotes": [{"le_rang": 4, "le_cote": "moins", "les_nombres": {"suivie": [1, 2], "compagne": [0], "tierce": []}}]}, "389")
      == {"4 moins": [1, 2, 0]}
      and les_nombres({"les_cotes": [{"le_rang": 4, "le_cote": "moins", "les_sauts": {"suivie": [{"le_nombre_de_feuilles": 2}],
                                                                                       "compagne": [], "tierce": []}}]}, "397") == {"4 moins": [2]})

    def d_(m, n, m_, n_):
        return {"le_bilan": {"389": {"plusieurs": m, "comptes": n}, "397": {"plusieurs": m_, "comptes": n_}}}
    v("★★★★ la règle : la moitié de la part de 389 au plus, oui ; au moins la part de 389, non ; sinon, en partie",
      le_verdict(d_(20, 200, 5, 100))["lissue"].endswith("; oui") and le_verdict(d_(20, 200, 10, 100))["lissue"].endswith("; non")
      and le_verdict(d_(20, 200, 8, 100))["lissue"].endswith("; en partie")
      and "font 8 sauts de plusieurs feuilles sur 100 comptés, contre 20 sur 200 pour 389" in le_verdict(d_(20, 200, 8, 100))["lissue"])
    v("★★★ indécidable sous 10 sauts de plusieurs feuilles dans 389", not le_verdict(d_(9, 200, 1, 100))["decidable"])

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
