#!/usr/bin/env python3
"""Rogner une nappe etendue en retirant ce qui a pousse EN DERNIER.

⚠⚠ POURQUOI. Une extension (`44`) triple la surface utile en restant sur sa feuille, mais elle
cree **9 % de fenetres dont le pic tombe au bord** — une peripherie qui n'a aucune feuille a
portee. Et cette peripherie empoisonne toute suite : mesure du 2026-08-22, repartir d'une
surface a 12 % de bord donne 20 % au pas suivant et α = +1,806, quand repartir de la source a
0 % donne α = +0,000. **La qualite de la surface dont on repart compte au moins autant que la
taille du pas.**

⭐ D'ou l'idee : retirer la peripherie avant d'enchainer. Et l'information necessaire est deja
dans le maillage — `generations.tif`, le compteur par sommet. La peripherie est exactement ce
qui a pousse en dernier, donc rogner par generation est direct et ne demande aucun rendu.

⚠ Ce que ca ne fait PAS : verifier que « pousse en dernier » et « mal pose » coincident. C'est
plausible (la croissance progresse vers l'exterieur) mais c'est une hypothese, et c'est
precisement ce que le jugement de la surface rognee mesure. L'outil rogne ; il ne conclut pas.

⚠⚠ Le sommet invalide s'ecrit **-1**, pas (0,0,0) — convention de vc, ecrite dans la note de
son rapport de self-intersection (« z <= 0 invalid ») et payee une fois dans ce depot.

Usage :
    uv run python analysis/src/rogner_nappe.py <maillage> <sortie> --generation-max 50
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

INVALIDE = -1.0


def lire_generations(maillage: Path):
    """Le compteur de generations par sommet, ou None s'il est absent."""
    import tifffile

    f = maillage / "generations.tif"
    if not f.is_file():
        return None
    return tifffile.imread(f)


def rogner(maillage: Path, sortie: Path, generation_max: int) -> dict:
    """Ecrire une copie du maillage ou tout sommet au-dela de `generation_max` est invalide.

    ⚠ `meta.json` est recopie AVEC son `area_cm2` RECALCULE : le laisser tel quel ferait lire
    a tout consommateur l'aire d'avant le rognage, ce qui est exactement le genre de chiffre
    perime que ce depot traque. L'aire recalculee est celle des sommets valides, donc du meme
    genre que celle qu'on compare ailleurs.
    """
    import numpy as np
    import tifffile

    gen = lire_generations(maillage)
    if gen is None:
        raise FileNotFoundError(f"{maillage}/generations.tif absent — rien a rogner")

    canaux = {}
    for nom in "xyz":
        canaux[nom] = tifffile.imread(maillage / f"{nom}.tif").astype(np.float32)
    z = canaux["z"]
    valide_avant = (z > 0)
    trop_jeune = gen > generation_max
    a_retirer = valide_avant & trop_jeune
    for nom in "xyz":
        canaux[nom][a_retirer] = INVALIDE

    sortie.mkdir(parents=True, exist_ok=True)
    for nom in "xyz":
        tifffile.imwrite(sortie / f"{nom}.tif", canaux[nom])
    # ⚠ Le canal de generations suit : sans lui, un rognage suivant n'aurait plus de quoi
    # decider, et le traceur perdrait le point de reprise qu'il lit dedans.
    tifffile.imwrite(sortie / "generations.tif", gen)

    pas = 20.0
    meta_src = maillage / "meta.json"
    meta = {}
    if meta_src.is_file():
        meta = json.loads(meta_src.read_text(encoding="utf-8"))
        sc = meta.get("scale")
        if isinstance(sc, list) and sc and float(sc[0]) > 0:
            pas = 1.0 / float(sc[0])
    # ⚠ `z` est `canaux["z"]`, DEJA modifie en place quelques lignes plus haut : compter
    # `(z > 0)` PUIS soustraire les retires les compte deux fois. Bug attrape par le temoin,
    # parce qu'il asserte la VALEUR de l'aire et pas seulement que l'outil a tourne.
    reste = int((canaux["z"] > 0).sum())
    voxel_um = float(meta.get("voxelsize", 8.64) or 8.64)
    meta["area_cm2"] = reste * (pas * voxel_um / 10000.0) ** 2
    meta["rogne_generation_max"] = generation_max
    meta["source_rognee"] = str(maillage)
    (sortie / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    return {"avant": int(valide_avant.sum()), "retires": int(a_retirer.sum()),
            "reste": reste, "generation_max": generation_max,
            "aire_cm2": meta["area_cm2"],
            "generations": [int(gen[valide_avant].min()), int(gen[valide_avant].max())]}


def verifier() -> int:
    """Temoin hors ligne : un maillage synthetique dont on connait les generations."""
    import tempfile

    import numpy as np
    import tifffile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as t:
        src = Path(t) / "src"
        src.mkdir()
        # 10x10, generations 1 a 10 par colonne, toutes valides sauf une colonne deja a -1.
        gen = np.tile(np.arange(1, 11, dtype=np.uint16), (10, 1))
        xyz = np.full((10, 10), 3000.0, dtype=np.float32)
        deja = np.zeros((10, 10), bool)
        deja[:, 0] = True
        xyz2 = xyz.copy()
        xyz2[deja] = INVALIDE
        for nom in "xyz":
            tifffile.imwrite(src / f"{nom}.tif", xyz2)
        tifffile.imwrite(src / "generations.tif", gen)
        (src / "meta.json").write_text('{"scale": [0.05, 0.05], "voxelsize": 8.64, '
                                       '"area_cm2": 999.0}')

        out = Path(t) / "out"
        r = rogner(src, out, generation_max=5)
        v("les sommets au-delà du seuil sont retirés", r["retires"] == 50,
          f"{r['retires']} au lieu de 50")
        v("... et ceux en deçà sont gardés", r["reste"] == 40, f"{r['reste']} au lieu de 40")
        v("un sommet DÉJÀ invalide n'est pas compté comme retiré",
          r["avant"] == 90, f"{r['avant']} au lieu de 90")

        z = tifffile.imread(out / "z.tif")
        v("l'invalidité s'écrit -1, pas 0", float(z[0, 9]) == -1.0, str(z[0, 9]))
        v("un sommet gardé n'est pas touché", float(z[0, 4]) == 3000.0, str(z[0, 4]))
        v("le canal de générations suit la copie", (out / "generations.tif").is_file())

        m = json.loads((out / "meta.json").read_text())
        # ⚠⚠ L'aire DOIT etre recalculee : laisser 999 ferait lire a tout consommateur
        # l'aire d'avant le rognage.
        v("l'aire du meta est RECALCULÉE, pas recopiée", m["area_cm2"] != 999.0,
          str(m["area_cm2"]))
        v("... et elle vaut le compte de sommets restants × la cellule",
          abs(m["area_cm2"] - 40 * (20.0 * 8.64 / 10000.0) ** 2) < 1e-9, str(m["area_cm2"]))
        v("le rognage est tracé dans le meta", m.get("rogne_generation_max") == 5)

        # Rogner au-dela du maximum ne doit RIEN retirer.
        r2 = rogner(src, Path(t) / "out2", generation_max=99)
        v("un seuil au-delà du maximum ne retire rien", r2["retires"] == 0, str(r2["retires"]))
        # ⚠ Temoin du temoin : sans ce controle, un rognage qui retire tout passerait aussi.
        r3 = rogner(src, Path(t) / "out3", generation_max=0)
        v("un seuil à zéro retire TOUT ce qui était valide", r3["reste"] == 0,
          str(r3["reste"]))

        vide = Path(t) / "vide"
        vide.mkdir()
        try:
            rogner(vide, Path(t) / "out4", 5)
            v("un maillage sans generations.tif est refusé", False, "aucune exception")
        except FileNotFoundError:
            v("un maillage sans generations.tif est refusé", True)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("maillage", nargs="?", type=Path)
    ap.add_argument("sortie", nargs="?", type=Path)
    ap.add_argument("--generation-max", type=int, default=50)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.maillage or not a.sortie:
        ap.error("donner un maillage et une sortie, ou --verifier")

    r = rogner(a.maillage, a.sortie, a.generation_max)
    print(f"  générations présentes : {r['generations'][0]} à {r['generations'][1]}")
    print(f"  seuil : ≤ {r['generation_max']}")
    print(f"  sommets : {r['avant']} valides → {r['reste']} gardés "
          f"({r['retires']} retirés, {100 * r['retires'] / max(r['avant'], 1):.0f} %)")
    print(f"  aire recalculée : {r['aire_cm2']:.2f} cm²")
    print(f"  écrit : {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
