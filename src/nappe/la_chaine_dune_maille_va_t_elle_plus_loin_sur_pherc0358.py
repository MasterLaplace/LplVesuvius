"""Sur PHerc0358, la chaîne qui regrandit sa spire tenue d'une maille tient-elle plus de sauts à la suite que la chaîne mixte, par le critère de 352 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA CHAÎNE D'UNE MAILLE NE TOURNE SUR PHERC0358. Ce qui était vu avant d'écrire : tout ce que `296` à
`365` publient, dont `R4-F551` (sur PHercParis4, regrandie d'une maille, la chaîne garde 1231 mailles en médiane sous ses sauts justes
contre 980,5 pour la chaîne mixte, et le décalage ne naît sur aucun côté) et `R4-F542` (sur PHerc0358, la chaîne mixte tient 1, 1, 3, 3 et 3
sauts à la suite sur ses cinq côtés, 3 en médiane, et ses spires gardées rétrécissent jusqu'à 115 points).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P163`. Sur PHerc0358, rouleau sans tracé, la chaîne mixte s'arrête souvent parce que sa spire
rétrécit ; la chaîne d'une maille, jugée sur PHercParis4, regagne de la surface sans faire naître de décalage. Si elle va plus loin sur
PHerc0358, c'est une chaîne étalonnée qui avance sur un rouleau que personne n'a tracé.

## Ce qui est fait

- **Les graines, les nappes de départ, le saut et la relance** : ceux des chaînes de PHerc0358 que `331` suit, comme dans `356`.
- **La chaîne d'une maille** : la chaîne mixte de `356`, dont chaque spire que le critère de `352` tient est regrandie par la croissance
  bornée de `335` arrêtée à une maille, la surface regrandie gardée si le critère la tient aussi ; le compte, au pas et à la portée de `354`.
- **La suite** : celle de `356`, les sauts à la suite depuis la nappe de départ dont la surface gardée est tenue.
- **Le contrôle** : le premier saut de chaque côté part de la même nappe que dans `355`, et le compte de sa spire redonne ce que `355` publie.
- **La règle** : la médiane des suites des cinq côtés contre celle de la chaîne mixte que `356` publie : plus haute, **elle tient plus de
  sauts à la suite** ; égale, **pas plus** ; plus basse, **moins**.

## Les issues

L'issue de la tranche : **sur PHerc0358, la chaîne d'une maille tient h sauts à la suite en médiane, contre h' pour la chaîne mixte**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts tenus, dont les surfaces regrandies gardées ; la taille des surfaces gardées tenues.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si ces surfaces sont sur leur feuille ; sur PHerc0358, aucun tour publié ne le dit, et c'est
PHercParis4 qui étalonne la chaîne.

Usage :
    uv run python src/nappe/la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.py --verifier
    uv run python src/nappe/la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.py \\
        --json docs/mesures/la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358.json
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
import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402
import sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart as m355  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import regrandir_dune_seule_maille_evite_il_le_decalage as m365  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_356_A_PUBLIE = LES_MESURES / "une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.json"
LA_MARGE = m365.LA_MARGE


def la_chaine_dune_maille_de_0358(nappe: dict, relancer, sauter, lire_valeurs, marge: int = LA_MARGE,
                                  sauts: int = m331.LES_SAUTS, rogner=None) -> list[dict]:
    """La chaîne mixte de `356` sur PHerc0358, dont chaque spire tenue est regrandie à `marge` mailles des mailles semées. Avec `sauts`,
    écrit pour `389`, la chaîne va jusqu'à ce nombre de sauts au lieu de huit ; avec `rogner`, écrit pour `397`, chaque surface gardée est
    rognée comme `356` le fait."""
    regrandir = lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire(s_, o_, tuple(p_), tuple(n_), lire_valeurs, marge=marge)  # noqa: E731
    return m356.la_chaine_mixte(nappe, relancer, sauter, lire_valeurs, sauts=sauts, regrandir=regrandir, rogner=rogner)


def le_cote(c: dict) -> dict:
    sauts = [{"le_saut": h, "depuis": k["depuis"], "le_compte_de_la_spire": k["le_compte_de_la_spire"], "le_compte": k["le_compte"],
              "les_points": k["les_points"], "tenu": bool(k["depuis"] is not None and m355.tenue(k["le_compte"]))}
             for h, k in enumerate(c["la_chaine"], 1)]
    return {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts, "la_suite": m356.la_suite(c["la_chaine"])}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_355"):
        return {"decidable": False, "lissue": "indécidable : les premiers sauts ne redonnent pas 355"}
    u = statistics.median(c["la_suite"] for c in d["les_cotes"])
    m = statistics.median(d["les_suites_de_la_chaine_mixte"])
    f_ = lambda x: f"{x:g}".replace(".", ",") + (" saut" if x <= 1 else " sauts")  # noqa: E731
    tete = f"sur PHerc0358, la chaîne d'une maille tient {f_(u)} à la suite en médiane, contre {f_(m)} pour la chaîne mixte"
    suite = "elle tient plus de sauts à la suite" if u > m else "pas plus" if u == m else "moins"
    return {"decidable": True, "u": u, "m": m, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=la_chaine_dune_maille_de_0358)
    cotes = [le_cote(c) for c in chaines]
    for c in cotes:
        print(json.dumps({x: c[x] for x in ("le_rang", "le_cote", "la_suite")}, ensure_ascii=False),
              [(s["depuis"], s["les_points"], s["tenu"]) for s in c["les_sauts"]], flush=True)
    publie356 = json.loads(CE_QUE_356_A_PUBLIE.read_text())
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_marge_en_mailles": LA_MARGE, "les_sauts": m331.LES_SAUTS},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_355": m356.redonne_355(cotes, json.loads(m356.CE_QUE_355_A_PUBLIE.read_text())), "les_cotes": cotes,
         "les_suites_de_la_chaine_mixte": [c["la_suite"] for c in publie356["les_cotes"]]}
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

    vu, avant = {}, (m356.la_chaine_mixte, m333.la_nappe_de_la_spire)
    m356.la_chaine_mixte = lambda *a, **k: vu.update(k, lv=a[3], rg=k["regrandir"]([1, 2, 3], [0, 0, 1], "s", "o")) or []
    m333.la_nappe_de_la_spire = lambda s_, o_, p_, n_, lv, marge=None: ("croissance", s_, o_, p_, n_, lv, marge)
    try:
        la_chaine_dune_maille_de_0358("nappe", "relancer", "sauter", "m7")
    finally:
        m356.la_chaine_mixte, m333.la_nappe_de_la_spire = avant
    v("★★★★ la chaîne : la mixte de 356 au compte de 355, regrandie d'une maille sur m7, la graine et la normale en tuples",
      "compter" not in vu and vu.get("lv") == "m7" and vu.get("rg") == ("croissance", "s", "o", (1, 2, 3), (0, 0, 1), "m7", 1), str(vu))
    v("★★★ la marge est celle de 365, une maille", LA_MARGE == 1)
    bon = {"les_comptes": {"1": 100}, "les_mesures": 100, "la_part_dune_feuille": 1.0}
    mauvais = {"les_comptes": {"0": 90, "1": 10}, "les_mesures": 100, "la_part_dune_feuille": 0.1}
    c = le_cote({"le_rang": 6, "le_cote": "moins",
                 "la_chaine": [{"depuis": m356.DEPUIS_LA_CROISSANCE, "le_compte_de_la_spire": bon, "le_compte": bon, "les_points": 300},
                               {"depuis": m356.DEPUIS_LA_SPIRE, "le_compte_de_la_spire": bon, "le_compte": bon, "les_points": 200},
                               {"depuis": m356.DEPUIS_LA_RELANCE, "le_compte_de_la_spire": mauvais, "le_compte": mauvais, "les_points": 900},
                               {"depuis": m356.DEPUIS_LA_SPIRE, "le_compte_de_la_spire": bon, "le_compte": bon, "les_points": 100}]})
    v("★★★★ un côté : chaque saut, tenu par le critère, et la suite de 356 depuis la nappe de départ",
      [s["tenu"] for s in c["les_sauts"]] == [True, True, False, True] and c["la_suite"] == 2, str(c))

    def d_(u, m, ok=True):
        return {"les_pannes": [], "redonne_355": ok, "les_cotes": [{"la_suite": x} for x in u], "les_suites_de_la_chaine_mixte": m}
    v("★★★★ la règle : la médiane des suites contre celle de la chaîne mixte",
      le_verdict(d_([1, 4, 4, 5, 6], [1, 1, 3, 3, 3]))["lissue"].endswith("plus de sauts à la suite")
      and le_verdict(d_([1, 2, 3, 5, 6], [1, 1, 3, 3, 3]))["lissue"].endswith("pas plus")
      and le_verdict(d_([0, 1, 2, 9, 9], [1, 1, 3, 3, 3]))["lissue"].endswith("moins"))
    v("★★★ la médiane, pas la moyenne", le_verdict(d_([0, 0, 3, 9, 9], [1, 1, 3, 3, 3]))["lissue"].endswith("pas plus"))
    v("★★★ les premiers sauts qui ne redonnent pas 355 : indécidable", not le_verdict(d_([4], [3], ok=False))["decidable"])

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
