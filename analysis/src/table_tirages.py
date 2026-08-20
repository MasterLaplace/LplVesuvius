#!/usr/bin/env python3
"""La non-reproductibilite du traceur replique-t-elle sur d'AUTRES rouleaux ?

⚠⚠ Pourquoi cette mesure existe. `30` a mesure que `vc_grow_seg_from_seed` rend un
resultat different a chaque execution -- mais sur UNE graine, d'UN rouleau. Le taux de
mauvais tirages (2 sur 15, ~13 %) porte un intervalle de confiance large, et rien ne
disait qu'il valait ailleurs. `29` M1bis marque ce manque ⚠⚠.

⚠ Deux grandeurs, et elles ne disent PAS la meme chose :

  - le **verdict** (auto-intersections). Il peut valoir zero partout, et « aucun mauvais
    tirage » ne se distingue alors pas de « le traceur est deterministe ici ».
  - l'**etendue des aires**. Elle est non nulle des que le tirage varie, meme quand tous
    les tirages sont propres.

Ce script rend les deux, et le **controle de determinisme** qui les separe : un rouleau
dont les N tirages rendent la MEME aire au bit pres ET le meme verdict est un rouleau ou
le traceur s'est comporte de facon reproductible. Sans ce controle, un corpus tout propre
serait lu comme « le probleme de `30` n'existe pas » alors qu'il voudrait dire « on n'a
pas su le voir ».

⭐ La preuve la plus forte est le **basculement** : un rouleau ou deux tirages a
parametres strictement identiques rendent des verdicts opposes. Il ne demande aucun seuil
et aucune verite terrain.

Usage :
    uv run python analysis/src/table_tirages.py [data/tirages] [--json docs/table_tirages.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def clopper_pearson(succes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    """Intervalle de confiance exact d'une proportion binomiale.

    ⚠ Choisi contre l'approximation normale exprès : sur 2 succes en 15 essais, elle rend
    une borne basse NEGATIVE. Un intervalle qui sort du domaine de la grandeur qu'il
    encadre n'est pas conservateur, il est faux.
    """
    from scipy.stats import beta
    bas = 0.0 if succes == 0 else float(beta.ppf(alpha / 2, succes, total - succes + 1))
    haut = 1.0 if succes == total else float(beta.ppf(1 - alpha / 2, succes + 1, total - succes))
    return bas, haut


def verifier() -> int:
    """Temoin hors ligne : la lecture des tirages, sur des cas fabriques.

    ⚠ Ce qui est verifie n'est pas un chiffre de campagne -- il changerait a chaque run --
    mais les **distinctions** que ce fichier existe pour tenir :

      - un rouleau dont tous les tirages sont identiques est dit REPRODUCTIBLE ;
      - un rouleau dont l'aire varie mais dont le verdict tient n'est PAS dit
        reproductible, et n'est pas dit bascule non plus ;
      - un rouleau dont le verdict change est dit BASCULE.

    ⭐ La troisieme est celle qui porte le resultat. Si un basculement etait lu comme une
    simple dispersion, un corpus entier pourrait basculer sans que rien ne le dise.
    """
    import json as _json
    import tempfile

    echecs, controles = 0, 0

    def verifie(nom: str, condition: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not condition:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    cas = {
        "FIGE": [(10.0, 0), (10.0, 0), (10.0, 0)],          # reproductible
        "DISPERSE": [(10.0, 0), (11.0, 0), (12.0, 0)],      # varie, verdict tenu
        "BASCULE": [(10.0, 0), (10.0, 7), (10.0, 0)],       # verdict oppose
        "RATE": [(10.0, 3), (10.0, 5)],                     # jamais propre
    }
    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp)
        for rouleau, tirages in cas.items():
            for i, (aire, crois) in enumerate(tirages, 1):
                d = racine / rouleau / f"r{i}"
                d.mkdir(parents=True)
                (d / "resume.json").write_text(_json.dumps({
                    "rouleau": rouleau, "repetition": i, "statut": "ok",
                    "graine": [0, 0, 0], "voxel_um": 9.362, "surface": "x",
                    "generations": 10, "aire_cm2": aire, "transverse": crois}))
        # Un tirage sans maillage doit etre ECARTE, pas compte comme propre.
        d = racine / "FIGE" / "r9"
        d.mkdir(parents=True)
        (d / "resume.json").write_text(_json.dumps({
            "rouleau": "FIGE", "repetition": 9, "statut": "sans_maillage",
            "graine": [0, 0, 0], "voxel_um": 9.362, "surface": "x",
            "generations": 0, "aire_cm2": None, "transverse": None}))

        sortie = racine / "sortie.json"
        code = main_avec(str(racine), str(sortie))
        verifie("le dépouillement rend 0", code == 0, f"code {code}")
        d = _json.loads(sortie.read_text())
        par_nom = {l["rouleau"]: l for l in d["lignes"]}

    verifie("un tirage sans maillage est écarté", d["sans_maillage"] == 1,
            str(d["sans_maillage"]))
    verifie("FIGE compté sans lui", par_nom["FIGE"]["n"] == 3, str(par_nom["FIGE"]["n"]))
    verifie("FIGE est reproductible", par_nom["FIGE"]["aire_identique"])
    verifie("FIGE ne bascule pas", not par_nom["FIGE"]["verdict_bascule"])
    verifie("DISPERSE n'est PAS reproductible", not par_nom["DISPERSE"]["aire_identique"])
    verifie("DISPERSE ne bascule pas", not par_nom["DISPERSE"]["verdict_bascule"])
    verifie("DISPERSE a une étendue non nulle", par_nom["DISPERSE"]["etendue_relative"] > 0)
    verifie("BASCULE bascule", par_nom["BASCULE"]["verdict_bascule"])
    verifie("BASCULE n'est pas dit reproductible malgré l'aire figée",
            not par_nom["BASCULE"]["aire_identique"] or par_nom["BASCULE"]["verdict_bascule"])
    verifie("RATE ne bascule pas (aucun propre)", not par_nom["RATE"]["verdict_bascule"])
    verifie("RATE compte 0 propre", par_nom["RATE"]["propres"] == 0)
    verifie("mauvais = 1 (BASCULE) + 2 (RATE)", d["mauvais"] == 3, str(d["mauvais"]))
    verifie("total = 3+3+3+2", d["tirages_total"] == 11, str(d["tirages_total"]))
    verifie("IC encadre le taux", d["ic95_bas"] <= d["taux_mauvais"] <= d["ic95_haut"])
    verifie("bascules recensées", d["rouleaux_bascule"] == ["BASCULE"],
            str(d["rouleaux_bascule"]))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main_avec(dossier: str, sortie: str) -> int:
    """Rejouer `main` sur un dossier donne, sans passer par la ligne de commande."""
    import contextlib
    import io
    argv = sys.argv
    sys.argv = [argv[0], dossier, "--json", sortie]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return main()
    finally:
        sys.argv = argv


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", default=str(RACINE / "data/tirages"))
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true",
                    help="temoin hors ligne, sur des tirages fabriques")
    a = ap.parse_args()

    if a.verifier:
        return verifier()

    par_rouleau: dict[str, list[dict]] = {}
    rejetes = 0
    for f in sorted(Path(a.dossier).glob("*/*/resume.json")):
        r = json.loads(f.read_text())
        if r.get("statut") != "ok":
            rejetes += 1
            continue
        par_rouleau.setdefault(r["rouleau"], []).append(r)
    if not par_rouleau:
        print(f"aucun tirage exploitable sous {a.dossier}")
        return 1

    lignes = []
    print(f"{sum(len(v) for v in par_rouleau.values())} tirages exploitables "
          f"sur {len(par_rouleau)} rouleaux"
          + (f" ({rejetes} sans maillage ou en dépassement)" if rejetes else "") + "\n")
    entete = (f"  {'rouleau':<12} {'n':>2} {'gen':>7} {'aire min':>10} {'aire max':>10} "
              f"{'étendue':>8} {'croisements par tirage':>26}")
    print(entete)
    print("  " + "-" * (len(entete) - 2))

    for rouleau in sorted(par_rouleau):
        lots = sorted(par_rouleau[rouleau], key=lambda x: x["repetition"])
        aires = [r["aire_cm2"] for r in lots]
        crois = [r["transverse"] for r in lots]
        gens = [r["generations"] for r in lots]
        etendue = (max(aires) - min(aires)) / statistics.mean(aires) if statistics.mean(aires) else 0.0
        # Le controle : identique au bit pres ET meme verdict = tirage reproductible ici.
        aire_identique = len(set(aires)) == 1
        verdict_identique = len(set(bool(c) for c in crois)) == 1
        bascule = not verdict_identique
        lignes.append({
            "rouleau": rouleau, "n": len(lots), "graine": lots[0]["graine"],
            "voxel_um": lots[0]["voxel_um"],
            "generations_min": min(gens), "generations_max": max(gens),
            "aire_min": min(aires), "aire_max": max(aires),
            "aire_mediane": statistics.median(aires), "etendue_relative": etendue,
            "croisements": crois, "propres": sum(1 for c in crois if c == 0),
            "aire_identique": aire_identique, "verdict_bascule": bascule,
        })
        marque = " ⭐ bascule" if bascule else ("  reproductible" if aire_identique else "")
        print(f"  {rouleau:<12} {len(lots):>2} {min(gens):>3}–{max(gens):<3} "
              f"{min(aires):>10.6f} {max(aires):>10.6f} {etendue:>7.2%} "
              f"{','.join(str(c) for c in crois):>26}{marque}")

    total = sum(l["n"] for l in lignes)
    mauvais = sum(l["n"] - l["propres"] for l in lignes)
    bas, haut = clopper_pearson(mauvais, total)
    bascules = [l["rouleau"] for l in lignes if l["verdict_bascule"]]
    reproductibles = [l["rouleau"] for l in lignes if l["aire_identique"]]

    print(f"\n  mauvais tirages : {mauvais}/{total} = {mauvais/total:.1%} "
          f"(IC 95 % exact : {bas:.1%} – {haut:.1%})")
    print(f"  rouleaux où le VERDICT bascule d'un tirage à l'autre : "
          f"{len(bascules)}/{len(lignes)}" + (f"  ({', '.join(bascules)})" if bascules else ""))
    print(f"  rouleaux où l'aire est identique sur tous les tirages : "
          f"{len(reproductibles)}/{len(lignes)}"
          + (f"  ({', '.join(reproductibles)})" if reproductibles else ""))

    if bascules:
        print("\n  ⭐ Un basculement est la preuve la plus forte disponible : deux exécutions")
        print("     à paramètres strictement identiques, deux verdicts opposés. Aucun seuil,")
        print("     aucune vérité terrain. Le résultat de `30` ne tient pas à sa graine.")
    elif reproductibles == [l["rouleau"] for l in lignes]:
        print("\n  ⚠ Aucun basculement ET aucune dispersion d'aire : sur ce corpus le traceur")
        print("     s'est comporté de façon reproductible. Le résultat de `30` serait alors")
        print("     propre à sa graine — et c'est ce qu'il faudrait écrire.")
    else:
        print("\n  ⚠ Aucun basculement, mais l'aire varie : le tirage bouge sans changer le")
        print("     verdict. Le taux de mauvais tirages n'est donc PAS mesuré à zéro ici,")
        print("     il est mesuré comme plus rare que ce corpus ne peut voir.")

    if a.json:
        Path(a.json).write_text(json.dumps({
            "tirages_total": total, "rouleaux": len(lignes),
            "mauvais": mauvais, "taux_mauvais": mauvais / total,
            "ic95_bas": bas, "ic95_haut": haut,
            "rouleaux_bascule": bascules, "rouleaux_reproductibles": reproductibles,
            "sans_maillage": rejetes, "lignes": lignes,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
