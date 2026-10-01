"""Sur PHerc0358, les sauts que m7 compte nuls laissent-ils les chaînes sur leur feuille, ou les surfaces voisines des deux autres chaînes voient-elles une feuille franchie ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES VOISINES NE SOIENT LUES SUR UN AUTRE SAUT NUL QUE CELUI DE `391`. Ce qui était vu avant d'écrire :
tout ce que `296` à `391` publient, dont `R4-F577` (sur la graine 4, côté moins, le douzième saut de la compagne, compté nul par `m7`, a
franchi une feuille) et `R4-F570` (les 10 sauts nuls de `369` sont à zéro feuille de `m7`, et 6 sauts simples de `369` aussi). ⚠ Cette
tranche ne lit pas `m7` : elle relit les paires et les comptes que `389` publie, avec les fonctions de `391`.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P189`. Un saut nul de `m7` qui franchit une feuille fait perdre un tour à toute la suite de la
chaîne ; s'il y en a d'autres, les comptes de `m7` ont une faiblesse à corriger avant de porter l'accord plus loin.

## Ce qui est fait

- **Les sauts** : sur les seize côtés, à seize sauts, chaque saut à partir du deuxième, de chaque chaîne, dont `m7` dit le nombre de feuilles.
- **L'avance des voisines** d'un saut : le compte des voisines, comme `391` le prend, de la surface où il arrive moins celui de la surface
  d'où il part ; elle n'est dite que si les deux surfaces ont des voisines.
- **Le contrôle** : sur les sauts que `m7` compte d'une feuille, l'avance des voisines vaut un sous au moins 75 % de ceux où elle est dite.
- **La règle**, sur les sauts que `m7` compte nuls et dont l'avance est dite : si au moins 75 % ont une avance nulle, **oui, ils laissent
  les chaînes sur leur feuille** ; au plus 25 %, **non, la plupart franchissent une feuille** ; sinon, **en partie**. Indécidable sous 5 tels
  sauts, ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **sur n sauts nuls de `m7` dont l'avance est dite, z laissent la chaîne sur sa feuille et u en franchissent une**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

L'avance des voisines sur les sauts de deux feuilles ; saut par saut, les sauts nuls et leur avance.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi `m7` compte un saut nul ; ni ce que vaut l'avance là où les voisines elles-mêmes ont un compte
faux.

Usage :
    uv run python src/nappe/les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.py --verifier
    uv run python src/nappe/les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.py \\
        --json docs/mesures/les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.json
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

import le_douzieme_saut_de_la_compagne_reste_t_il_sur_sa_feuille_ou_m7_en_manque_t_il_une as m391  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
LES_CHAINES = ("suivie", "compagne", "tierce")
LA_PART, LA_PART_BASSE, LE_MINIMUM = 0.75, 0.25, 5


def les_sauts(c: dict) -> list[dict]:
    """Chaque saut à partir du deuxième, de chaque chaîne d'un côté, dont `m7` dit le nombre de feuilles, avec l'avance des voisines."""
    out = []
    for x in LES_CHAINES:
        for h in range(2, len(c["les_comptes"][x]) + 1):
            n = c["les_nombres"][x][h - 1]
            if n is None:
                continue
            avant = m391.le_compte_des_voisines(m391.les_voisines(c["les_paires"], c["les_comptes"], x, h - 1))
            apres = m391.le_compte_des_voisines(m391.les_voisines(c["les_paires"], c["les_comptes"], x, h))
            out.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_chaine": x, "le_saut": h, "le_nombre_de_feuilles": n,
                        "lavance": None if avant is None or apres is None else apres - avant})
    return out


def le_bilan(sauts: list[dict]) -> dict:
    out = {}
    for n in sorted({s["le_nombre_de_feuilles"] for s in sauts}):
        dits = [s["lavance"] for s in sauts if s["le_nombre_de_feuilles"] == n and s["lavance"] is not None]
        out[str(n)] = {"les_sauts": sum(s["le_nombre_de_feuilles"] == n for s in sauts), "dits": len(dits),
                       "par_avance": {str(a): dits.count(a) for a in sorted(set(dits))}}
    return out


def le_verdict(d: dict) -> dict:
    b = d["le_bilan"]
    un = b.get("1", {"dits": 0, "par_avance": {}})
    if not un["dits"] or un["par_avance"].get("1", 0) < LA_PART * un["dits"]:
        return {"decidable": False, "lissue": "indécidable : sur les sauts d'une feuille, les voisines n'avancent pas d'un tour aux trois quarts"}
    z = b.get("0", {"dits": 0, "par_avance": {}})
    if z["dits"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {z['dits']} sauts nuls de m7 dont l'avance est dite, moins de {LE_MINIMUM}"}
    reste, franchit = z["par_avance"].get("0", 0), z["par_avance"].get("1", 0)
    tete = f"sur {z['dits']} sauts nuls de m7 dont l'avance est dite, {reste} laissent la chaîne sur sa feuille et {franchit} en franchissent une"
    p = reste / z["dits"]
    suite = ("oui, ils laissent les chaînes sur leur feuille" if p >= LA_PART else "non, la plupart franchissent une feuille"
             if p <= LA_PART_BASSE else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d389 = json.loads(CE_QUE_389_A_PUBLIE.read_text())
    sauts = [s for c in d389["les_cotes"] for s in les_sauts(c)]
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
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

    c = {"le_rang": 4, "le_cote": "moins",
         "les_paires": {"suivie|compagne": [[1, 1, True], [2, 2, True], [3, 2, True], [3, 3, True]], "suivie|tierce": [], "compagne|tierce": []},
         "les_comptes": {"suivie": [1, 2, 3], "compagne": [1, 2, 2], "tierce": []},
         "les_nombres": {"suivie": [1, 1, 1], "compagne": [1, None, 0], "tierce": []}}
    ss = les_sauts(c)
    vu = {(s["la_chaine"], s["le_saut"]): (s["le_nombre_de_feuilles"], s["lavance"]) for s in ss}
    v("★★★★ les sauts : à partir du deuxième, ceux dont m7 dit le nombre, avec l'avance des voisines",
      vu == {("suivie", 2): (1, 1), ("suivie", 3): (1, 0), ("compagne", 3): (0, 1)}, str(vu))
    v("★★★★ une surface sans voisine ne donne pas d'avance",
      les_sauts({**c, "les_paires": {"suivie|compagne": [[1, 1, True]], "suivie|tierce": [], "compagne|tierce": []}})[0]["lavance"] is None)
    b = le_bilan([{"le_nombre_de_feuilles": 0, "lavance": 0}, {"le_nombre_de_feuilles": 0, "lavance": 1}, {"le_nombre_de_feuilles": 0, "lavance": None},
                  {"le_nombre_de_feuilles": 1, "lavance": 1}])
    v("★★★★ le bilan par nombre de feuilles", b == {"0": {"les_sauts": 3, "dits": 2, "par_avance": {"0": 1, "1": 1}},
                                                    "1": {"les_sauts": 1, "dits": 1, "par_avance": {"1": 1}}}, str(b))

    def d_(r, f, un=9, dits1=10):
        return {"le_bilan": {"1": {"dits": dits1, "par_avance": {"1": un}}, "0": {"dits": r + f, "par_avance": {"0": r, "1": f}}}}
    v("★★★★ la règle : 75 % restés, oui ; 25 % au plus, non ; sinon, en partie",
      le_verdict(d_(6, 2))["lissue"].endswith("sur leur feuille") and le_verdict(d_(1, 5))["lissue"].endswith("franchissent une feuille")
      and le_verdict(d_(3, 3))["lissue"].endswith("; en partie") and "sur 6 sauts nuls de m7 dont l'avance est dite, 1 laissent" in le_verdict(d_(1, 5))["lissue"])
    v("★★★ indécidable sous 5 sauts nuls dits, ou si le contrôle échoue",
      not le_verdict(d_(2, 2))["decidable"] and not le_verdict(d_(6, 2, un=7))["decidable"] and le_verdict(d_(4, 1))["decidable"])

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
