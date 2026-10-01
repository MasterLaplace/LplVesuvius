"""Sur PHerc0358, les sauts nuls de m7 qui franchissent une feuille se distinguent-ils des autres par la part de leurs points qui en franchissent une ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES COMPTES DE `m7` POINT PAR POINT NE SOIENT LUS SUR LES SAUTS NULS. Ce qui était vu avant d'écrire :
tout ce que `296` à `392` publient, dont `R4-F578` (des 20 sauts nuls de `m7` dont les voisines disent l'avance, 15 laissent la chaîne sur
sa feuille et 4 en franchissent une : graine 4, moins, compagne 12 ; graine 6, moins, suivie 5 et tierce 10 ; graine 8, moins, compagne 2) et
`R4-F577` (la onzième surface de la compagne de la graine 4, côté moins, est sur la feuille de deux surfaces de la suivie).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P190`. Le nombre de feuilles d'un saut est le compte que porte le plus de points. Si un saut nul
qui franchit une feuille garde une part de points qui en franchissent une plus forte qu'un saut nul qui reste, un seuil sur cette part le
rattrape, sans les voisines.

## Ce qui est fait

- **Les chaînes et les comptes** : les chaînes à seize sauts de `389`, rejouées ; leurs nombres de feuilles et leurs points mesurés doivent
  redonner ceux de `389`. Pour chaque saut, le compte de `383` point par point, gardé en entier.
- **Les deux groupes** : les sauts nuls de `m7` que `392` dit restés, et ceux qu'il dit franchis.
- **La part d'une feuille** d'un saut : ses points mesurés qui franchissent une feuille, sur ses points mesurés.
- **La règle** : si tous les sauts franchis ont une part d'une feuille plus forte que tous les sauts restés, **oui, la part les sépare** ;
  si la médiane des franchis dépasse la plus forte des restés sans les séparer tous, **en partie** ; sinon, **non**. Indécidable si les
  chaînes ne redonnent pas `389` ou si une lecture échoue.

## Les issues

L'issue de la tranche : **les sauts franchis ont une part d'une feuille de a à b, les sauts restés de c à d**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Saut par saut, les points mesurés et leur répartition ; la part d'une feuille des sauts d'une feuille, pour comparaison.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si un seuil trouvé ici vaudrait ailleurs ; quatre sauts franchis ne font pas une règle.

Usage :
    uv run python src/nappe/les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.py --verifier
    uv run python src/nappe/les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.py \\
        --json docs/mesures/les_sauts_nuls_qui_franchissent_une_feuille_se_distinguent_ils_par_leurs_points.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
CE_QUE_392_A_PUBLIE = LES_MESURES / "les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.json"
LES_CHAINES = ("suivie", "compagne", "tierce")


def la_part_dune_feuille(comptes: dict) -> float | None:
    n = sum(comptes.values())
    return round(comptes.get("1", 0) / n, 4) if n else None


def le_bilan(sauts: list[dict]) -> dict:
    """Les parts d'une feuille des sauts nuls franchis et restés, et des sauts d'une feuille."""
    grp = lambda f: sorted(s["la_part_dune_feuille"] for s in sauts if f(s) and s["la_part_dune_feuille"] is not None)  # noqa: E731
    return {"franchis": grp(lambda s: s["le_nombre_de_feuilles"] == 0 and s["lavance"] == 1),
            "restes": grp(lambda s: s["le_nombre_de_feuilles"] == 0 and s["lavance"] == 0),
            "dune_feuille": grp(lambda s: s["le_nombre_de_feuilles"] == 1)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_389"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 389"}
    f, r = d["le_bilan"]["franchis"], d["le_bilan"]["restes"]
    if not f or not r:
        return {"decidable": False, "lissue": "indécidable : un des deux groupes de sauts nuls est vide"}
    v_ = lambda x: f"{x:.2f}".replace(".", ",")  # noqa: E731
    tete = f"les sauts franchis ont une part d'une feuille de {v_(f[0])} à {v_(f[-1])}, les sauts restés de {v_(r[0])} à {v_(r[-1])}"
    suite = ("oui, la part les sépare" if f[0] > r[-1] else "en partie" if statistics.median(f) > r[-1] else "non")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    d389, d392 = (json.loads(x.read_text()) for x in (CE_QUE_389_A_PUBLIE, CE_QUE_392_A_PUBLIE))
    avance = {(s["le_rang"], s["le_cote"], s["la_chaine"], s["le_saut"]): s["lavance"] for s in d392["les_sauts"]}
    tous = [(c["le_rang"], c["le_cote"]) for c in d389["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(m389.enchainer), cotes=set(tous))
    redonne, sauts = len(chaines) == len(tous), []
    for c, e, c389 in zip(chaines, m383._LES_CHAINES_ENTIERES, d389["les_cotes"]):
        for x in LES_CHAINES:
            ns = m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0)
            redonne &= [n["le_nombre_de_feuilles"] for n in ns] == c389["les_nombres"][x]
            for h, n in enumerate(ns, 1):
                if n["le_nombre_de_feuilles"] is None:
                    continue
                sauts.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_chaine": x, "le_saut": h,
                              "le_nombre_de_feuilles": n["le_nombre_de_feuilles"], "les_mesures": n["les_mesures"], "les_comptes": n["les_comptes"],
                              "la_part_dune_feuille": la_part_dune_feuille(n["les_comptes"]),
                              "lavance": avance.get((c["le_rang"], c["le_cote"], x, h))})
    d = {"la_question": __doc__.splitlines()[0], "les_pannes": list(stats0["pannes"]),
         "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"}, "redonne_389": bool(redonne),
         "les_sauts_nuls": [s for s in sauts if s["le_nombre_de_feuilles"] == 0]}
    d["le_bilan"] = le_bilan(sauts)
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

    v("★★★★ la part d'une feuille : les points qui en franchissent une, sur les points mesurés",
      la_part_dune_feuille({"0": 60, "1": 30, "2": 10}) == 0.3 and la_part_dune_feuille({}) is None)
    s_ = lambda n, a, p: {"le_nombre_de_feuilles": n, "lavance": a, "la_part_dune_feuille": p}  # noqa: E731
    b = le_bilan([s_(0, 1, 0.4), s_(0, 1, 0.3), s_(0, 0, 0.1), s_(0, 0, 0.2), s_(0, None, 0.9), s_(1, 1, 0.8), s_(0, -1, 0.5)])
    v("★★★★ le bilan : franchis, restés, et sauts d'une feuille ; une avance inconnue ou un recul n'entrent dans aucun groupe nul",
      b == {"franchis": [0.3, 0.4], "restes": [0.1, 0.2], "dune_feuille": [0.8]}, str(b))

    def d_(f, r, ok=True):
        return {"redonne_389": ok, "les_pannes": [], "le_bilan": {"franchis": f, "restes": r}}
    v("★★★★ la règle : séparés, oui ; médiane au-dessus des restés, en partie ; sinon, non",
      le_verdict(d_([0.4, 0.5], [0.1, 0.3]))["lissue"].endswith("la part les sépare")
      and le_verdict(d_([0.2, 0.4, 0.5], [0.1, 0.3]))["lissue"].endswith("; en partie")
      and le_verdict(d_([0.1, 0.2, 0.5], [0.1, 0.3]))["lissue"].endswith("; non")
      and "de 0,40 à 0,50, les sauts restés de 0,10 à 0,30" in le_verdict(d_([0.4, 0.5], [0.1, 0.3]))["lissue"])
    v("★★★ indécidable sans redonne ou sur un groupe vide", not le_verdict(d_([0.4], [0.1], ok=False))["decidable"]
      and not le_verdict(d_([], [0.1]))["decidable"])

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
