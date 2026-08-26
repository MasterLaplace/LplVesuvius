#!/usr/bin/env python3
"""La faible dispersion des rouleaux « stables » est-elle une TRONCATURE ?

⚠⚠ **La question que `29` N3 pose, et pourquoi elle compte.** [`35`](../docs/35_le_tirage_sur_douze_rouleaux.md)
mesure que la dispersion d'aire vaut 0,5 % chez les rouleaux dont les six tirages butent sur
le plafond de generations, contre 19,9 % chez les autres — un facteur 40. Deux lectures
s'opposent et rien ne les separait : soit ces rouleaux sont **reellement plus stables**,
soit leur dispersion est **ecrasee par une troncature commune** — six traces coupees au
meme endroit ont forcement la meme aire, quoi qu'elles fassent.

⭐ La mesure qui tranche est bon marche : **relever le plafond et rejouer**. Si la
dispersion monte, la stabilite etait un artefact du budget ; si elle reste basse, ces
rouleaux sont vraiment plus stables.

⚠ Cet outil ne fait que **confronter deux campagnes** — celle d'origine et celle a plafond
releve — rouleau par rouleau. Il ne trace rien et ne juge rien : les deux tables sont
produites par `table_tirages.py`, qui reste la seule source des chiffres.

⚠⚠ **Un rouleau dont les traces butent AUSSI sur le nouveau plafond est ecarte du verdict,
pas moyenne dedans.** Comparer une troncature a une autre troncature ne dit rien, et
l'inclure ferait baisser l'effet mesure sans qu'aucune ligne ne le signale.

Usage :
    cd experiments && uv run python ../src/graine/comparer_plafond.py \\
        ../docs/mesures/table_tirages.json ../docs/mesures/table_tirages_plafond.json \\
        --json ../docs/mesures/comparaison_plafond.json
    python3 src/graine/comparer_plafond.py --verifier
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


def confronter(origine: dict, releve: dict) -> dict:
    """Rouleau par rouleau : ce que le plafond releve change.

    ⚠ Ne garde que les rouleaux presents des DEUX cotes. Un rouleau tracé d'un seul côté
    n'a pas de comparaison, et le compter ferait une moyenne sur des lignes qui ne
    parlent pas de la même chose.
    """
    par_nom = {l["rouleau"]: l for l in origine.get("lignes", [])}
    lignes, satures = [], []
    for r in releve.get("lignes", []):
        a = par_nom.get(r["rouleau"])
        if a is None:
            continue
        # ⚠⚠ Le nouveau plafond est-il atteint lui aussi ? Si oui, la comparaison oppose
        # deux troncatures et ne mesure rien. On le DIT au lieu de le noyer.
        # ⚠⚠ Le test porte sur le BUDGET demande, jamais sur le maximum atteint : compare
        # au maximum, le rouleau qui va le plus loin « sature » toujours, par definition.
        # Les deux notions ont failli porter le meme nom, et le test aurait ete trivial.
        budget = r.get("budget_generations") or releve.get("budget_generations")
        sature = budget is not None and r["generations_max"] >= budget
        # ⚠⚠ ET un rouleau a MOINS DE DEUX tirages d'un cote a une dispersion nulle PAR
        # CONSTRUCTION -- un seul nombre ne se disperse pas. L'inclure dans une mediane de
        # dispersions tire le resultat vers le bas sans qu'aucune ligne ne le signale,
        # c'est-a-dire AFFAIBLIT l'effet mesure pour une raison etrangere au phenomene.
        # `table_tirages.py` applique deja cette regle a « reproductible » et « bascule ».
        # Le cas s'est presente : la campagne a ete arretee au premier tirage de son
        # troisieme rouleau.
        assez = min(a["n"], r["n"]) >= 2
        ligne = {
            "rouleau": r["rouleau"],
            "gen_avant": [a["generations_min"], a["generations_max"]],
            "gen_apres": [r["generations_min"], r["generations_max"]],
            "aire_mediane_avant": a["aire_mediane"],
            "aire_mediane_apres": r["aire_mediane"],
            "dispersion_avant": a["etendue_relative"],
            "dispersion_apres": r["etendue_relative"],
            "bascule_avant": a["verdict_bascule"],
            "bascule_apres": r["verdict_bascule"],
            "propres_avant": a["propres"],
            "propres_apres": r["propres"],
            "n_avant": a["n"], "n_apres": r["n"],
            "sature_au_nouveau_plafond": sature,
            "trop_peu_de_tirages": not assez,
        }
        (lignes if (assez and not sature) else satures).append(ligne)

    jugeables = lignes
    return {
        "plafond_avant": origine.get("budget_generations"),
        "plafond_apres": releve.get("budget_generations"),
        "rouleaux_compares": len(jugeables),
        "rouleaux_satures_ecartes": [l["rouleau"] for l in satures
                                     if l["sature_au_nouveau_plafond"]],
        "rouleaux_trop_peu_de_tirages": [l["rouleau"] for l in satures
                                         if l["trop_peu_de_tirages"]],
        "dispersion_mediane_avant": (statistics.median(
            [l["dispersion_avant"] for l in jugeables]) if jugeables else None),
        "dispersion_mediane_apres": (statistics.median(
            [l["dispersion_apres"] for l in jugeables]) if jugeables else None),
        "lignes": jugeables + satures,
    }


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def ligne(nom, gmin, gmax, med, disp, bascule=False, propres=6, n=6):
        return {"rouleau": nom, "generations_min": gmin, "generations_max": gmax,
                "aire_mediane": med, "etendue_relative": disp, "n": n,
                "verdict_bascule": bascule, "propres": propres}

    avant = {"budget_generations": 120,
             "lignes": [ligne("A", 118, 118, 19.8, 0.003),
                        ligne("B", 118, 118, 16.9, 0.004),
                        ligne("Z", 90, 104, 12.0, 0.30)]}
    apres = {"budget_generations": 400,
             "lignes": [ligne("A", 230, 333, 110.0, 1.10),
                        ligne("B", 400, 400, 88.0, 0.002),
                        ligne("Z", 220, 260, 40.0, 0.35),
                        ligne("INCONNU", 200, 210, 50.0, 0.5)]}
    d = confronter(avant, apres)

    v("un rouleau absent d'un côté n'est pas comparé",
      all(l["rouleau"] != "INCONNU" for l in d["lignes"]))
    v("un rouleau tracé des deux côtés est comparé",
      any(l["rouleau"] == "A" for l in d["lignes"]))
    # ⚠⚠ LA sonde : « B » bute sur le NOUVEAU plafond, donc sa dispersion de 0,2 % ne dit
    # rien -- c'est encore une troncature. L'inclure ferait tomber la mediane « apres »
    # de 110 % a ~55 % et affaiblirait l'effet mesure sans qu'aucune ligne ne le signale.
    v("un rouleau qui sature au nouveau plafond est ÉCARTÉ du verdict",
      d["rouleaux_satures_ecartes"] == ["B"], str(d["rouleaux_satures_ecartes"]))
    v("... et il reste dans les lignes, nommé", any(
        l["rouleau"] == "B" and l["sature_au_nouveau_plafond"] for l in d["lignes"]))
    v("le verdict ne porte que sur les rouleaux jugeables",
      d["rouleaux_compares"] == 2, str(d["rouleaux_compares"]))
    v("la dispersion médiane monte quand la troncature tombe",
      d["dispersion_mediane_apres"] > d["dispersion_mediane_avant"],
      f"{d['dispersion_mediane_avant']} → {d['dispersion_mediane_apres']}")
    # ⚠ Le controle du controle : si aucune dispersion ne montait, l'outil doit le dire
    # aussi -- sinon il ne peut rendre qu'une seule reponse.
    plat = confronter(avant, {"budget_generations": 400,
                              "lignes": [ligne("A", 200, 210, 19.9, 0.002),
                                         ligne("Z", 200, 210, 12.1, 0.28)]})
    v("... et elle ne monte pas quand les tirages restent groupés",
      plat["dispersion_mediane_apres"] <= plat["dispersion_mediane_avant"],
      f"{plat['dispersion_mediane_avant']} → {plat['dispersion_mediane_apres']}")
    # ⚠⚠ La seconde sonde : un rouleau a UN SEUL tirage a une dispersion nulle par
    # construction. L'inclure ferait tomber la mediane « apres » et affaiblirait l'effet
    # pour une raison qui n'a rien a voir avec le phenomene mesure.
    seul = confronter(avant, {"budget_generations": 400,
                              "lignes": [ligne("A", 230, 333, 110.0, 1.10),
                                         ligne("Z", 220, 260, 40.0, 0.35),
                                         ligne("B", 200, 210, 60.0, 0.0, n=1)]})
    v("un rouleau à un seul tirage est ÉCARTÉ du verdict",
      seul["rouleaux_trop_peu_de_tirages"] == ["B"],
      str(seul["rouleaux_trop_peu_de_tirages"]))
    v("... et ne tire pas la dispersion médiane vers le bas",
      seul["dispersion_mediane_apres"] > 0.3, str(seul["dispersion_mediane_apres"]))
    v("... mais il reste dans les lignes, nommé",
      any(l["rouleau"] == "B" and l["trop_peu_de_tirages"] for l in seul["lignes"]))

    v("deux campagnes vides ne rendent aucun verdict",
      confronter({}, {})["dispersion_mediane_apres"] is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origine", nargs="?")
    ap.add_argument("releve", nargs="?")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.origine or not a.releve:
        ap.error("nommer les deux tables, ou --verifier")

    d = confronter(json.loads(Path(a.origine).read_text()),
                   json.loads(Path(a.releve).read_text()))
    print(f"  plafond {d['plafond_avant']} → {d['plafond_apres']} générations, "
          f"{d['rouleaux_compares']} rouleau(x) comparable(s)\n")
    entete = (f"  {'rouleau':<12} {'gen avant':>10} {'gen après':>10} "
              f"{'aire méd. avant':>16} {'aire méd. après':>16} "
              f"{'disp. avant':>12} {'disp. après':>12}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))
    for l in d["lignes"]:
        marque = ("  ⚠ sature au nouveau plafond" if l["sature_au_nouveau_plafond"]
                  else f"  ⚠ {min(l['n_avant'], l['n_apres'])} tirage(s) seulement"
                  if l["trop_peu_de_tirages"] else "")
        print(f"  {l['rouleau']:<12} "
              f"{l['gen_avant'][0]:>4}–{l['gen_avant'][1]:<5} "
              f"{l['gen_apres'][0]:>4}–{l['gen_apres'][1]:<5} "
              f"{l['aire_mediane_avant']:>16.2f} {l['aire_mediane_apres']:>16.2f} "
              f"{l['dispersion_avant']:>11.2%} {l['dispersion_apres']:>11.2%}{marque}")

    if d["dispersion_mediane_avant"] is not None:
        print(f"\n  dispersion médiane : {d['dispersion_mediane_avant']:.2%} → "
              f"{d['dispersion_mediane_apres']:.2%}")
        if d["dispersion_mediane_apres"] > d["dispersion_mediane_avant"]:
            print("  ⭐⭐ La stabilité de ces rouleaux était une TRONCATURE : le budget")
            print("      coupait les six tirages au même endroit, donc leurs aires ne")
            print("      pouvaient pas différer. Elle n'était pas une propriété du rouleau.")
        else:
            print("  ⚠ La dispersion ne monte pas : sur ces rouleaux la faible dispersion")
            print("    n'était PAS un effet du plafond, et l'hypothèse tombe.")
    if d["rouleaux_satures_ecartes"]:
        print(f"\n  ⚠ écartés du verdict, car ils butent aussi sur le nouveau plafond : "
              f"{', '.join(d['rouleaux_satures_ecartes'])} — comparer une troncature à une "
              f"autre ne dit rien")
    if d["rouleaux_trop_peu_de_tirages"]:
        print(f"\n  ⚠ écartés du verdict, car moins de deux tirages d'un côté : "
              f"{', '.join(d['rouleaux_trop_peu_de_tirages'])} — un seul nombre ne se "
              f"disperse pas, l'inclure baisserait la médiane sans rien mesurer")

    if a.json:
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
