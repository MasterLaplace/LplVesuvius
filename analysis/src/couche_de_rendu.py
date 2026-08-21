#!/usr/bin/env python3
"""Extraire UNE couche d'une pile rendue, en image regardable — et l'index qui va avec.

⚠⚠ Pourquoi ce fichier existe. Une pile rendue par `vc_render_tifxyz` est faite de couches
`NN.tif` en niveaux de gris brut : la surface tracee est **au milieu** de la pile, et telle
quelle l'image est presque noire, parce que la dynamique utile occupe une petite part de la
plage. `10` avait fait cette extraction a la main ; la refaire a la main a chaque campagne
est exactement le genre de commande de terminal qui se perd.

⚠ L'ETIREMENT EST PAR IMAGE, et il faut le dire : deux bandes etirees separement ne sont
plus comparables en intensite. C'est le bon choix pour REGARDER (chaque spire a sa propre
exposition) et le mauvais pour MESURER. Aucune mesure de ce depot ne passe par ces PNG.

⚠ La couche prise par defaut est `len // 2` -- la surface. Prendre la premiere ou la
derniere donnerait une image de l'interieur du papyrus voisin, ce qui ressemble aussi a du
papyrus et n'est pas la surface qu'on juge.

Usage :
    uv run python analysis/src/couche_de_rendu.py data/spires/spire00/rendu_81 \\
        --sortie /tmp/spire00.png
    # plusieurs piles + l'index que assembler_mosaique.py sait relire
    uv run python analysis/src/couche_de_rendu.py data/spires/spire*/rendu_81 \\
        --dossier-sortie data/mosaique/chaine --index data/mosaique/chaine/index.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
BAS, HAUT = 1.0, 99.0        # percentiles de l'etirement


def couches(dossier: Path) -> list[Path]:
    """Les `.tif` d'une pile, triees par leur NUMERO et non par leur nom.

    ⚠ Le tri lexicographique met `10.tif` avant `9.tif` des qu'une pile depasse dix
    couches. `10` a paye la meme classe de piege sur la largeur du nom de fichier
    (`15.tif` contre `015.tif`) : ici on extrait le nombre et on trie dessus.
    """
    fs = list(dossier.glob("*.tif"))
    def num(p: Path) -> int:
        m = re.search(r"(\d+)", p.stem)
        return int(m.group(1)) if m else -1
    return sorted(fs, key=num)


def etirer(a: np.ndarray, bas: float = BAS, haut: float = HAUT) -> np.ndarray:
    """Etirer la dynamique entre deux percentiles, en uint8.

    ⚠ Percentiles et non min/max : un seul pixel aberrant suffit a ecraser toute l'image
    si on normalise sur les extremes, et une pile rendue en a toujours (bords, trous).
    """
    fini = a[np.isfinite(a)]
    if fini.size == 0:
        return np.zeros(a.shape, dtype=np.uint8)
    lo, hi = np.percentile(fini, [bas, haut])
    if hi <= lo:
        return np.zeros(a.shape, dtype=np.uint8)
    return np.clip((a - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8)


def extraire(dossier: Path, sortie: Path, couche: int | None = None,
             bas: float = BAS, haut: float = HAUT) -> dict | None:
    from PIL import Image
    import tifffile

    fs = couches(dossier)
    if not fs:
        return None
    idx = len(fs) // 2 if couche is None else max(0, min(couche, len(fs) - 1))
    a = np.asarray(tifffile.imread(str(fs[idx])), dtype=np.float32)
    im = Image.fromarray(etirer(a, bas, haut))
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"pile": str(dossier), "couches": len(fs), "couche": idx,
            "taille": [im.width, im.height], "sortie": str(sortie)}


def verifier() -> int:
    import tempfile
    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de couche_de_rendu")

    # ⚠⚠ Le tri : une pile de douze couches doit rendre `9.tif` AVANT `10.tif`.
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for i in range(12):
            (t / f"{i}.tif").write_bytes(b"")
        noms = [p.stem for p in couches(t)]
        ok(noms == [str(i) for i in range(12)],
           f"les couches sont triées par NUMÉRO, pas par nom ({noms[:4]}…{noms[-2:]})")
        # Sonde : le tri lexicographique se tromperait ici.
        lex = sorted(p.stem for p in t.glob("*.tif"))
        ok(lex != noms, f"le tri lexicographique donnerait autre chose ({lex[:4]}…)")

    # L'étirement : une rampe doit remplir la plage, et un plat doit rendre du noir.
    rampe = np.linspace(1000, 2000, 256, dtype=np.float32).reshape(16, 16)
    e = etirer(rampe)
    ok(int(e.min()) == 0 and int(e.max()) == 255,
       f"une rampe remplit la plage ({e.min()}–{e.max()})")
    plat = np.full((8, 8), 1234.0, dtype=np.float32)
    ok(int(etirer(plat).max()) == 0,
       "une image plate rend du noir plutôt que du bruit amplifié")
    # ⚠ Sonde des percentiles : un pixel aberrant ne doit PAS écraser l'image.
    avec_pic = rampe.copy(); avec_pic[0, 0] = 1e6
    e2 = etirer(avec_pic)
    ok(int(np.median(e2)) > 100,
       f"un pixel aberrant n'écrase pas la dynamique (médiane {np.median(e2):.0f})")
    e3 = etirer(avec_pic, 0.0, 100.0)
    ok(int(np.median(e3)) < 10,
       f"…alors que min/max l'écraserait (médiane {np.median(e3):.0f}) — la sonde")
    ok(etirer(np.array([], dtype=np.float32)).size == 0,
       "une image vide ne casse pas l'étirement")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("piles", nargs="*", type=Path)
    ap.add_argument("--sortie", type=Path, help="une seule pile → une seule image")
    ap.add_argument("--dossier-sortie", type=Path)
    ap.add_argument("--index", type=Path,
                    help="écrire un index que assembler_mosaique.py sait relire")
    ap.add_argument("--couche", type=int, default=None)
    ap.add_argument("--bas", type=float, default=BAS)
    ap.add_argument("--haut", type=float, default=HAUT)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.piles:
        ap.error("donner au moins une pile, ou --verifier")

    if a.sortie and len(a.piles) == 1:
        r = extraire(a.piles[0], a.sortie, a.couche, a.bas, a.haut)
        if r is None:
            print(f"pile vide : {a.piles[0]}", file=sys.stderr)
            return 3
        print(f"{r['pile']} → couche {r['couche']}/{r['couches']} "
              f"({r['taille'][0]}×{r['taille'][1]}) → {r['sortie']}")
        return 0

    if not a.dossier_sortie:
        ap.error("plusieurs piles demandent --dossier-sortie")
    lignes, n = [], 0
    for i, pile in enumerate(a.piles):
        # ⚠ Le rang vient du NOM du dossier parent quand il porte un numéro, pas de l'ordre
        # d'argument : un `*` de shell trie lexicographiquement, donc `spire10` viendrait
        # avant `spire2`. L'ordre EST le sens de la mosaïque.
        m = re.search(r"(\d+)", pile.parent.name)
        rang = int(m.group(1)) if m else i
        cible = a.dossier_sortie / f"{pile.parent.name}.png"
        r = extraire(pile, cible, a.couche, a.bas, a.haut)
        if r is None:
            print(f"  ⚠ pile vide, sautée : {pile}", file=sys.stderr)
            continue
        n += 1
        print(f"  {pile.parent.name} : couche {r['couche']}/{r['couches']} "
              f"{r['taille'][0]}×{r['taille'][1]}")
        lignes.append(f"{rang}\t{pile.parent.name}\t{cible}")
    if not lignes:
        print("aucune image produite", file=sys.stderr)
        return 3
    if a.index:
        a.index.parent.mkdir(parents=True, exist_ok=True)
        a.index.write_text("\n".join(sorted(lignes, key=lambda l: int(l.split("\t")[0])))
                           + "\n", encoding="utf-8")
        print(f"  écrit : {a.index} ({n} bandes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
