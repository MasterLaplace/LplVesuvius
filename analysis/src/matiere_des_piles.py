#!/usr/bin/env python3
"""Y a-t-il quoi que ce soit dans ces piles rendues ?

⚠⚠ POURQUOI. Cinq piles de 161 couches ont été lues comme « surfaces parfaitement plates »
alors qu'elles étaient **entièrement noires** — voir [`54`](../docs/54_cinq_rendus_vides.md).
Le déclencheur n'a pas été une relecture du code mais une **taille de fichier** : 7,6 Mo
contre 562 Mo pour des images de mêmes dimensions. Ce fichier fait de ce coup d'œil une
mesure, avec sa sortie dans l'arbre, parce qu'un chiffre dont le calcul n'est pas versionné
est une anecdote.

⚠ La question posée ici est **binaire et sans seuil** : le maximum de la pile est-il
strictement positif. Un pixel à zéro n'a pas de matière par définition du format, sans
calibration — donc aucun nombre transporté n'entre dans le verdict. La part de pixels
allumés est **rapportée** à côté, parce que « il y a de la matière » et « la pile est
copieusement remplie » sont deux faits différents, et le second ne se déduit pas du premier.

⚠ L'échantillonnage (`--pas`) ne sert qu'à ne pas relire 562 Mo par pile. Il ne peut pas
transformer une pile vide en pile pleine, mais il **peut** rater une pile dont une seule
couche porte quelque chose : `--pas 1` est le seul réglage qui répond exactement.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def couches(dossier: Path) -> list[Path]:
    """Les couches d'une pile, triées par leur numéro et non par leur nom.

    ⚠ `sorted()` sur les noms range `10.tif` avant `9.tif`. Ici l'ordre n'a pas d'effet sur
    le verdict, mais il en a un sur l'échantillonnage : un pas de 20 sur une liste mal
    ordonnée ne prélève pas ce qu'on croit.
    """
    out = []
    for p in dossier.glob("*.tif"):
        try:
            out.append((int(p.stem), p))
        except ValueError:
            continue
    return [p for _, p in sorted(out)]


def matiere(dossier: Path, pas: int = 20) -> dict:
    """Le maximum et la part de pixels allumés d'une pile."""
    import numpy as np
    import tifffile

    fichiers = couches(dossier)
    if not fichiers:
        return {"pile": str(dossier), "couches": 0, "lues": 0, "max": None,
                "part_allumee": None, "vide": None, "refus": "aucune couche"}
    lues = fichiers[::max(1, pas)]
    pic = 0
    allumes = total = 0
    for f in lues:
        a = tifffile.imread(str(f))
        if a.size == 0:
            continue
        pic = max(pic, int(a.max()))
        allumes += int((a > 0).sum())
        total += int(a.size)
    return {"pile": str(dossier), "couches": len(fichiers), "lues": len(lues),
            "max": pic, "part_allumee": (allumes / total) if total else None,
            "vide": pic == 0}


def verifier() -> int:
    """Les témoins, sur des piles fabriquées ici."""
    import shutil
    import tempfile

    import numpy as np
    import tifffile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {detail}" if detail else ""))

    racine = Path(tempfile.mkdtemp(prefix="matiere_temoins_"))

    def ecrire(nom, faire, n=25):
        d = racine / nom
        d.mkdir()
        for i in range(n):
            tifffile.imwrite(str(d / f"{i:03d}.tif"), faire(i))
        return d

    vide = ecrire("vide", lambda i: np.zeros((40, 40), dtype=np.uint8))
    plein = ecrire("plein", lambda i: np.full((40, 40), 7, dtype=np.uint8))

    def une_seule(i):
        a = np.zeros((40, 40), dtype=np.uint8)
        if i == 7:
            a[0, 0] = 255
        return a

    rare = ecrire("rare", une_seule)

    r = matiere(vide, pas=5)
    v("une pile noire est dite vide", r["vide"] is True)
    v("... son maximum est zero", r["max"] == 0)
    v("... et sa part allumee aussi", r["part_allumee"] == 0.0)

    r = matiere(plein, pas=5)
    v("une pile pleine n'est pas vide", r["vide"] is False)
    v("... son maximum est la valeur ecrite", r["max"] == 7, str(r["max"]))
    v("... et tout est allume", r["part_allumee"] == 1.0)

    # ⚠⚠ LA LIMITE DE L'ECHANTILLONNAGE, sondée plutôt qu'affirmée : une pile dont UNE seule
    # couche porte quelque chose est declaree vide par un pas qui saute cette couche. Le
    # rapporter est honnete ; le taire ferait de `--pas` un reglage qui change le verdict
    # sans le dire.
    v("un pas trop grand rate la couche unique", matiere(rare, pas=5)["vide"] is True)
    v("... et un pas de 1 la trouve", matiere(rare, pas=1)["vide"] is False)

    r = matiere(racine / "inexistante")
    v("un dossier sans couche est signale", r["refus"] == "aucune couche")
    v("... et ne se dit pas vide", r["vide"] is None)

    # ⚠ Les couches sont rangees par NUMERO : `10` apres `9`.
    d = ecrire("ordre", lambda i: np.zeros((4, 4), dtype=np.uint8), n=12)
    noms = [p.stem for p in couches(d)]
    v("les couches sont triees par numero", noms[9:11] == ["009", "010"], str(noms[9:11]))

    shutil.rmtree(racine, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("piles", nargs="*", type=Path)
    p.add_argument("--pas", type=int, default=20, help="ne lire qu'une couche sur N")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.piles:
        p.error("donner au moins une pile, ou --verifier")

    # ⚠ Le nom affiche porte les DEUX derniers composants : toutes les piles s'appellent
    # `rendu_161`, donc n'en montrer qu'un range huit candidats sous le meme nom et la
    # sortie devient illisible au moment precis ou elle compte.
    def etiquette(d: Path) -> str:
        return f"{d.parent.name}/{d.name}" if d.parent.name else d.name

    lignes = []
    print(f"{'pile':38s} {'couches':>7s} {'max':>5s} {'allume':>8s}  verdict")
    for d in a.piles:
        r = matiere(d, a.pas)
        lignes.append(r)
        if r.get("refus"):
            print(f"{etiquette(d):38s} {'—':>7s} {'—':>5s} {'—':>8s}  ⚠ {r['refus']}")
            continue
        part = f"{100 * r['part_allumee']:.1f} %"
        verdict = "⚠⚠ VIDE — rien n'a ete rendu" if r["vide"] else "matiere"
        print(f"{etiquette(d):38s} {r['couches']:7d} {r['max']:5d} {part:>8s}  {verdict}")

    vides = [r for r in lignes if r.get("vide")]
    if vides:
        print(f"\n⚠⚠ {len(vides)} pile(s) sur {len(lignes)} sont ENTIEREMENT NOIRES. Ce n'est "
              f"pas une surface plate, c'est un rendu qui n'a rien produit.")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"pas": a.pas, "piles": lignes}, indent=2),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
