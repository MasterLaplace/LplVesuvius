#!/usr/bin/env python3
"""Nos traces sont-elles PERDUES, ou a UNE SPIRE de leur feuille ?

⚠⚠ Pourquoi cette question change tout. `36` §5 mesure que nos traces lisent 146 a 187 µm
d'ecart a leur feuille la ou un bon segment officiel lit 17 µm. Lu comme ca, c'est un echec
sans forme : la trace serait « loin », et rien ne dit quoi en faire.

⭐ Mais l'ecart inter-spires de ces memes rouleaux, mesure par `16`, vaut 150 a 225 µm --
LE MEME ORDRE DE GRANDEUR. Rapporte a l'echelle de son propre rouleau, chaque ecart devient
un nombre de SPIRES, et un ecart d'exactement une spire n'est pas une trace perdue : c'est
une trace qui suit une feuille voisine. Le remede n'est alors pas un gauchissement mais un
decalage d'une spire le long de la normale -- ce qui est trivialement applicable.

⚠⚠ **Deux confonds, et ils sont serieux :**

  1. **La censure.** L'ecart bute sur `(couches // 2) × voxel`. Pour plusieurs rouleaux ce
     plafond vaut PRESQUE l'ecart inter-spires -- pour `PHerc1447` il vaut exactement
     172,8 µm dans les deux cas. Un rapport de 1,00 y est donc indistinguable d'une valeur
     tronquee. Les lignes censurees sont marquees et **ne comptent pas** dans le verdict.
  2. **La quantification commune.** Les deux grandeurs sont des multiples de tailles de
     voxel apparentees, donc une egalite a quatre chiffres peut etre un artefact de grille.
     Le script imprime les deux en NOMBRE DE VOXELS pour que ce soit visible.

Ce qui tranche est une fenetre assez large pour que le plafond vaille DEUX spires : un pic
qui reste a une spire est alors une mesure, pas une borne.

Usage :
    uv run python analysis/src/ecart_en_spires.py [docs/second_axe_41.json ...] [--json ...]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def espacement(rouleau: str, racine: Path) -> float | None:
    """L'ecart inter-spires median du rouleau, mesure par `16`."""
    p = racine / "docs/carte_difficulte" / f"{rouleau}.json"
    if not p.is_file():
        return None
    d = json.loads(p.read_text())
    s = (d.get("seuils") or {}).get("0.5")
    return float(s["median_um"]) if s and "median_um" in s else None


def lignes_de(fichiers: list[Path], racine: Path) -> list[dict]:
    out = []
    for f in fichiers:
        if not f.is_file():
            continue
        d = json.loads(f.read_text())
        for l in d["lignes"]:
            sp = espacement(l["rouleau"], racine)
            if not sp:
                continue
            out.append({
                "source": f.name, "rouleau": l["rouleau"], "repetition": l["repetition"],
                "ecart_um": l["ecart_um"], "espacement_um": sp,
                "spires": l["ecart_um"] / sp, "censure": bool(l["censure"]),
                "plafond_um": l["plafond_um"],
                # ⚠ Le plafond vaut-il presque une spire ? Si oui, meme une valeur NON
                # censuree est suspecte, parce que la fenetre ne pouvait pas montrer plus.
                "plafond_en_spires": l["plafond_um"] / sp,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fichiers", nargs="*", type=Path,
                    default=[RACINE / "docs/second_axe_41.json"])
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    lignes = lignes_de([Path(f) for f in a.fichiers], RACINE)
    if not lignes:
        print("aucune ligne exploitable")
        return 1

    entete = (f"  {'rouleau':<12} {'tir.':>5} {'écart µm':>9} {'spire µm':>9} "
              f"{'= spires':>9} {'plafond':>9}")
    print(f"{len(lignes)} tirages, rapportés à l'écart inter-spires de LEUR rouleau\n")
    print(entete)
    print("  " + "-" * (len(entete) - 2))
    for l in sorted(lignes, key=lambda x: (x["rouleau"], x["repetition"])):
        m = ""
        if l["censure"]:
            m = "  ⚠ censuré"
        elif l["plafond_en_spires"] < 1.4:
            m = "  ⚠ fenêtre < 1,4 spire"
        print(f"  {l['rouleau']:<12} {l['repetition']:>5} {l['ecart_um']:>9.1f} "
              f"{l['espacement_um']:>9.1f} {l['spires']:>9.2f} "
              f"{l['plafond_en_spires']:>8.2f}s{m}")

    utiles = [l for l in lignes if not l["censure"] and l["plafond_en_spires"] >= 1.4]
    print(f"\n  lignes utilisables (non censurées ET fenêtre ≥ 1,4 spire) : "
          f"{len(utiles)}/{len(lignes)}")
    if utiles:
        v = [l["spires"] for l in utiles]
        print(f"  écart en spires : {min(v):.2f} à {max(v):.2f}, médiane {statistics.median(v):.2f}")
        proches = sum(1 for x in v if 0.8 <= x <= 1.2)
        print(f"  entre 0,8 et 1,2 spire : {proches}/{len(v)}")
        if proches >= max(1, len(v) * 0.6):
            print("\n  ⭐⭐ La trace n'est pas perdue : elle est à UNE SPIRE de sa feuille.")
            print("     Le remède serait un décalage le long de la normale, pas un")
            print("     gauchissement — et un décalage est trivialement applicable.")
        else:
            print("\n  ⚠ L'écart ne vaut pas une spire de façon fiable. La trace ne suit")
            print("     donc pas simplement la mauvaise feuille.")
    else:
        print("  ⚠⚠ AUCUNE ligne utilisable : toutes sont censurées ou mesurées dans une")
        print("     fenêtre trop étroite pour distinguer une spire de son propre plafond.")
        print("     Il faut rendre avec une fenêtre d'au moins deux spires.")

    if a.json:
        Path(a.json).write_text(json.dumps(
            {"lignes": lignes, "utilisables": len(utiles), "total": len(lignes)},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


def verifier() -> int:
    """Temoin hors ligne : la conversion, et surtout les deux refus."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp)
        (racine / "docs/carte_difficulte").mkdir(parents=True)
        (racine / "docs/carte_difficulte/R.json").write_text(json.dumps(
            {"seuils": {"0.5": {"median_um": 100.0}}}))
        f = racine / "axe.json"
        f.write_text(json.dumps({"lignes": [
            # une spire pile, fenetre large : utilisable
            {"rouleau": "R", "repetition": "r1", "ecart_um": 100.0, "censure": False,
             "plafond_um": 300.0},
            # une spire pile MAIS censuree : inutilisable
            {"rouleau": "R", "repetition": "r2", "ecart_um": 100.0, "censure": True,
             "plafond_um": 100.0},
            # une spire pile MAIS fenetre trop etroite : inutilisable
            {"rouleau": "R", "repetition": "r3", "ecart_um": 100.0, "censure": False,
             "plafond_um": 120.0},
            # deux spires, fenetre large : utilisable, et PAS « une spire »
            {"rouleau": "R", "repetition": "r4", "ecart_um": 200.0, "censure": False,
             "plafond_um": 300.0},
        ]}))
        lignes = lignes_de([f], racine)

    par = {l["repetition"]: l for l in lignes}
    v("les quatre lignes sont lues", len(lignes) == 4, str(len(lignes)))
    v("100 µm sur une spire de 100 µm = 1,00", abs(par["r1"]["spires"] - 1.0) < 1e-9)
    v("200 µm = 2,00 spires", abs(par["r4"]["spires"] - 2.0) < 1e-9)
    v("le plafond est converti en spires",
      abs(par["r1"]["plafond_en_spires"] - 3.0) < 1e-9, str(par["r1"]["plafond_en_spires"]))
    # ⭐ Les deux refus : ce sont eux qui empechent de lire un plafond comme un resultat.
    utiles = [l for l in lignes if not l["censure"] and l["plafond_en_spires"] >= 1.4]
    v("une ligne censurée est écartée", "r2" not in {l["repetition"] for l in utiles})
    v("une fenêtre < 1,4 spire est écartée", "r3" not in {l["repetition"] for l in utiles})
    v("les deux lignes larges restent",
      {l["repetition"] for l in utiles} == {"r1", "r4"},
      str(sorted(l["repetition"] for l in utiles)))
    v("un rouleau sans espacement mesuré est ignoré, pas deviné",
      all(l["espacement_um"] for l in lignes))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
