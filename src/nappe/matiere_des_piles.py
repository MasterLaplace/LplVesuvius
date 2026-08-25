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
    allumes = total = illisibles = 0
    for f in lues:
        # ⚠⚠ Une couche ILLISIBLE n'est pas une couche noire, et laisser l'exception
        # remonter ferait mourir un audit de trois cents piles sur la premiere qui est en
        # cours d'ecriture. Le moteur de rendu pre-alloue ses sorties puis les remplit bande
        # par bande : entre les deux, un `.tif` existe et n'a aucune page.
        try:
            a = tifffile.imread(str(f))
        except Exception:
            illisibles += 1
            continue
        if a.size == 0:
            illisibles += 1
            continue
        pic = max(pic, int(a.max()))
        allumes += int((a > 0).sum())
        total += int(a.size)
    if total == 0:
        # ⚠⚠ UN TROISIEME ETAT, et le confondre avec « vide » serait la meme faute que celle
        # que ce fichier existe pour attraper. Des fichiers .tif qui existent mais ne
        # contiennent AUCUNE page, c'est un rendu en cours d'ecriture : le moteur pre-alloue
        # ses sorties puis les remplit bande par bande. « il n'y a rien dedans » et « il n'y
        # a rien ENCORE » ne veulent pas dire la meme chose, et la premiere lecture ferait
        # condamner un rendu parfaitement sain qu'on a seulement regarde trop tot.
        return {"pile": str(dossier), "couches": len(fichiers), "lues": len(lues),
                "illisibles": illisibles, "max": None, "part_allumee": None, "vide": None,
                "refus": "aucune page lisible — rendu probablement en cours"}
    return {"pile": str(dossier), "couches": len(fichiers), "lues": len(lues),
            "illisibles": illisibles, "max": pic,
            "part_allumee": (allumes / total) if total else None, "vide": pic == 0}


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

    # ⚠⚠ Le troisieme etat : des fichiers qui existent et n'ont aucune page.
    encours = racine / "encours"
    encours.mkdir()
    # ⚠ Un en-tete tronque, pas un fichier vide : c'est ce qu'un moteur laisse derriere lui
    # entre la pre-allocation et le remplissage, et c'est ce que le lecteur doit encaisser.
    for i in range(4):
        (encours / f"{i:03d}.tif").write_bytes(b"II*\x00")
    r = matiere(encours, pas=1)
    v("un rendu en cours n'est pas dit vide", r["vide"] is None, str(r["vide"]))
    v("... et il est nomme", "en cours" in (r.get("refus") or ""), str(r.get("refus")))
    v("... et il ne pretend pas mesurer", r["max"] is None and r["part_allumee"] is None)

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
            n = r.get("couches", 0)
            print(f"{etiquette(d):38s} {n:7d} {'—':>5s} {'—':>8s}  ⚠ {r['refus']}")
            continue
        part = f"{100 * r['part_allumee']:.1f} %"
        verdict = "⚠⚠ VIDE — rien n'a ete rendu" if r["vide"] else "matiere"
        print(f"{etiquette(d):38s} {r['couches']:7d} {r['max']:5d} {part:>8s}  {verdict}")

    encours = [r for r in lignes if r.get("vide") is None and r.get("couches")]
    if encours:
        print(f"\n⚠ {len(encours)} pile(s) illisibles — rendu en cours, pas un verdict.")
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
