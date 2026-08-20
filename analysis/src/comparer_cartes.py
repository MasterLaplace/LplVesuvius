#!/usr/bin/env python3
"""Deux campagnes de separabilite, et ce que la seconde fait a l'ordre de la premiere.

⚠⚠ **Ce fichier est ecrit AVANT que la campagne dense ait fini**, et c'est deliberate.
`33` avance une prediction falsifiable : le classement des treize rouleaux de `16` est du
bruit d'echantillonnage, donc **un second echantillonnage ne le reproduira pas**. Une
prediction ecrite apres avoir vu le resultat n'est pas une prediction ; ecrire le
depouilleur d'abord est le seul moyen bon marche de tenir cette distinction.

Trois questions, dans cet ordre :

  1. **Les deux campagnes mesurent-elles la meme chose ?** L'estimation dense doit tomber
     dans l'intervalle de confiance de l'estimation creuse. Si elle en sort
     SYSTEMATIQUEMENT du meme cote, l'echantillonnage creux etait **biaise** et pas
     seulement bruite -- ce qui serait un resultat different, et plus grave.
  2. **L'ordre survit-il ?** Correlation de rang entre les deux campagnes. ⭐ C'est le
     test de la prediction de `33` : un ordre reel se reproduit, un ordre de bruit non.
  3. **Le denombrement suffit-il maintenant ?** Le meme Fisher + Holm que
     `incertitude_carte.py`, sur les nouveaux effectifs.

⚠ Une correlation de rang sur treize points est elle-meme bruitee : son intervalle est
donne, et l'absence de correlation ne se lit pas comme une preuve d'absence d'ordre --
seulement comme l'absence de la preuve qu'il y en a un.

Usage :
    uv run python analysis/src/comparer_cartes.py \\
        docs/carte_separabilite docs/carte_separabilite_dense --json docs/comparaison_cartes.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from incertitude_carte import charger, clopper_pearson, holm  # noqa: E402


def verifier() -> int:
    """Temoin hors ligne : la lecture appariee, et le sens de « hors intervalle »."""
    import tempfile

    echecs, controles = 0, 0

    def verifie(nom: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def campagne(racine: Path, valeurs: dict[str, tuple[int, int]]) -> Path:
        racine.mkdir(parents=True, exist_ok=True)
        for nom, (k, n) in valeurs.items():
            (racine / f"{nom}.json").write_text(json.dumps({
                "zarr": "x", "level": 1, "voxel_um": 9.362, "chunks": n,
                "d_prime_median": 1.5, "d_prime_p10": 1.0, "d_prime_min": 0.9,
                "part_sous_1": k / n}))
        return racine

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        # Ordre parfaitement conserve, effectifs doubles.
        a = campagne(base / "a", {"_TEMOIN_T": (0, 20), "R1": (1, 20), "R2": (3, 20), "R3": (5, 20)})
        b = campagne(base / "b", {"_TEMOIN_T": (0, 40), "R1": (2, 40), "R2": (6, 40), "R3": (10, 40)})
        r = comparer(a, b)
    par = {l["rouleau"]: l for l in r["lignes"]}
    verifie("les trois rouleaux sont appariés", len(r["lignes"]) == 3, str(len(r["lignes"])))
    verifie("une part inchangée reste dans l'intervalle",
            all(l["dense_dans_ic_creux"] for l in r["lignes"]))
    verifie("un ordre conservé donne rho = 1", abs(r["rho"] - 1.0) < 1e-9, str(r["rho"]))
    verifie("aucun rouleau ne change de rang", r["rangs_changes"] == 0, str(r["rangs_changes"]))
    verifie("le témoin est reconnu", r["temoin"]["rouleau"] == "T", str(r["temoin"]))

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        # Ordre exactement inverse : la prediction de `33` ressemblerait a ca.
        a = campagne(base / "a", {"_TEMOIN_T": (0, 20), "R1": (1, 20), "R2": (3, 20), "R3": (5, 20)})
        b = campagne(base / "b", {"_TEMOIN_T": (0, 40), "R1": (10, 40), "R2": (6, 40), "R3": (2, 40)})
        r = comparer(a, b)
    verifie("un ordre inversé donne rho = -1", abs(r["rho"] + 1.0) < 1e-9, str(r["rho"]))
    verifie("l'inversion sort des intervalles",
            sum(1 for l in r["lignes"] if not l["dense_dans_ic_creux"]) >= 1)
    verifie("des rangs changent", r["rangs_changes"] > 0, str(r["rangs_changes"]))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def comparer(creux: Path, dense: Path) -> dict:
    from scipy.stats import fisher_exact, spearmanr

    t_creux, r_creux = charger(creux)
    t_dense, r_dense = charger(dense)
    par_creux = {r["rouleau"]: r for r in r_creux}
    par_dense = {r["rouleau"]: r for r in r_dense}
    communs = sorted(set(par_creux) & set(par_dense), key=lambda n: par_creux[n]["part"])

    lignes = []
    for nom in communs:
        c, d = par_creux[nom], par_dense[nom]
        ic = clopper_pearson(c["k"], c["n"])
        lignes.append({
            "rouleau": nom,
            "creux_k": c["k"], "creux_n": c["n"], "creux_part": c["part"], "creux_ic": ic,
            "dense_k": d["k"], "dense_n": d["n"], "dense_part": d["part"],
            "dense_dans_ic_creux": ic[0] <= d["part"] <= ic[1],
            "ecart": d["part"] - c["part"],
        })

    rangs_creux = {n: i for i, n in enumerate(sorted(communs, key=lambda n: par_creux[n]["part"]))}
    rangs_dense = {n: i for i, n in enumerate(sorted(communs, key=lambda n: par_dense[n]["part"]))}
    rho = float(spearmanr([rangs_creux[n] for n in communs],
                          [rangs_dense[n] for n in communs]).statistic) if len(communs) > 2 else float("nan")
    rangs_changes = sum(1 for n in communs if rangs_creux[n] != rangs_dense[n])

    # Le meme test que `incertitude_carte`, sur les nouveaux effectifs.
    bruts, paires, brutes_p = [], 0, []
    for nom in communs:
        d = par_dense[nom]
        bruts.append(float(fisher_exact(
            [[d["k"], d["n"] - d["k"]], [t_dense["k"], t_dense["n"] - t_dense["k"]]],
            alternative="greater").pvalue))
    holm_temoin = holm(bruts) if bruts else []
    for i, ni in enumerate(communs):
        for nj in communs[i + 1:]:
            paires += 1
            di, dj = par_dense[ni], par_dense[nj]
            brutes_p.append(float(fisher_exact(
                [[dj["k"], dj["n"] - dj["k"]], [di["k"], di["n"] - di["k"]]],
                alternative="two-sided").pvalue))
    separees = sum(1 for q in holm(brutes_p) if q < 0.05) if brutes_p else 0

    return {
        "creux": str(creux), "dense": str(dense), "temoin": t_dense,
        "lignes": lignes, "rho": rho, "rangs_changes": rangs_changes,
        "paires": paires, "paires_separees": separees,
        "distinguables_holm": [n for n, q in zip(communs, holm_temoin) if q < 0.05],
        "hors_intervalle": [l["rouleau"] for l in lignes if not l["dense_dans_ic_creux"]],
        "hors_par_le_haut": [l["rouleau"] for l in lignes
                             if not l["dense_dans_ic_creux"] and l["ecart"] > 0],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("creux", nargs="?", default=str(RACINE / "docs/carte_separabilite"))
    ap.add_argument("dense", nargs="?", default=str(RACINE / "docs/carte_separabilite_dense"))
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    r = comparer(Path(a.creux), Path(a.dense))
    if not r["lignes"]:
        print("aucun rouleau commun aux deux campagnes")
        return 1

    print(f"{len(r['lignes'])} rouleaux mesurés par les deux campagnes\n")
    entete = (f"  {'rouleau':<12} {'creux k/n':>10} {'part':>7} {'IC 95 % creux':>16} "
              f"{'dense k/n':>10} {'part':>7} {'écart':>7}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))
    for l in r["lignes"]:
        marque = "" if l["dense_dans_ic_creux"] else "  ⚠ hors intervalle"
        print(f"  {l['rouleau']:<12} {l['creux_k']:>4}/{l['creux_n']:<5} {l['creux_part']:>6.1%} "
              f"{l['creux_ic'][0]:>6.1%} – {l['creux_ic'][1]:<6.1%} "
              f"{l['dense_k']:>4}/{l['dense_n']:<5} {l['dense_part']:>6.1%} "
              f"{l['ecart']:>+6.1%}{marque}")

    print(f"\n  1. même grandeur ? {len(r['lignes']) - len(r['hors_intervalle'])}"
          f"/{len(r['lignes'])} estimations denses tombent dans l'intervalle creux"
          + (f"  (hors : {', '.join(r['hors_intervalle'])})" if r["hors_intervalle"] else ""))
    if len(r["hors_intervalle"]) > len(r["lignes"]) / 2:
        cote = "haut" if len(r["hors_par_le_haut"]) > len(r["hors_intervalle"]) / 2 else "bas"
        print(f"     ⚠⚠ la majorité sort, et par le {cote} : l'échantillonnage creux était")
        print("        BIAISÉ, pas seulement bruité. C'est un résultat différent et plus grave.")

    print(f"\n  2. l'ordre survit-il ? ⭐ rho de Spearman = {r['rho']:+.3f}, "
          f"{r['rangs_changes']}/{len(r['lignes'])} rouleaux changent de rang")
    if r["rho"] > 0.7:
        print("     → l'ordre se reproduit. La prédiction de `33` est REFUTÉE : le classement")
        print("        portait de l'information que ses intervalles ne montraient pas.")
    elif r["rho"] < 0.3:
        print("     → l'ordre ne se reproduit pas. C'est ce que `33` prédisait, et il faut le")
        print("        lire comme une confirmation, pas comme une surprise.")
    else:
        print("     → ni l'un ni l'autre. Treize points ne tranchent pas un rho intermédiaire.")

    print(f"\n  3. le dénombrement suffit-il ? {r['paires_separees']}/{r['paires']} paires "
          f"séparées, {len(r['distinguables_holm'])} rouleaux distinguables du témoin")
    if r["paires_separees"] == 0:
        print("     ⚠ toujours aucune paire. L'effectif dense ne suffit pas non plus, ou")
        print("        les rouleaux ne diffèrent pas.")

    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
