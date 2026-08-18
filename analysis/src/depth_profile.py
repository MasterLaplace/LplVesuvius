#!/usr/bin/env python3
"""Ou se trouve la SURFACE dans la pile de couches, et est-elle au meme endroit ?

⚠⚠ Ne on de la premiere cause candidate a l'echec du detecteur sur Scroll 4
(`docs/09` §12). Le modele GP-2023 lit **26 couches** d'une pile qui en compte
davantage -- ici les couches 15 a 40. Rien ne garantit que la surface du papyrus tombe
a la meme profondeur d'un rouleau a l'autre : si elle est **decentree** dans la
fenetre, le modele regarde a cote, et il rendrait exactement ce qu'on observe -- une
carte aplatie, sans structure de trait.

C'est la cause la moins chere a tester, et elle se teste **sans rien telecharger** :
la reponse est deja dans les couches qu'on a.

**Deux profils, parce qu'ils echouent differemment.**

- L'**intensite moyenne** dit ou est la matiere. Elle suffit a voir une surface qui
  sort de la fenetre, pas a la localiser finement : le papyrus est epais.
- Le **contraste local** (ecart-type d'un passe-haut) dit ou est la STRUCTURE. Il pique
  la ou les fibres et l'encre sont nettes, c'est-a-dire a la surface. C'est celui qui
  localise.

⚠ **Chaque profil est normalise dans sa propre pile.** Deux campagnes de scan n'ont ni
la meme dynamique ni le meme gain, donc comparer des niveaux bruts comparerait les
scanners. Ce qui se compare est la **forme** : ou est le pic, et la fenetre le
contient-elle.

⚠ Mesure sur une **fenetre** et non sur la couche entiere : une couche fait ~500 Mo, la
pile 13 Go, et un profil de profondeur n'a pas besoin de toute la surface. La fenetre
est prise au centre de la zone couverte, la ou il y a de la matiere.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def layer_files(folder: Path, first: int = 0, last: int = 10**9) -> list[Path]:
    """Couches triees par indice numerique, pas par ordre alphabetique.

    ⚠ Un tri alphabetique met `10.tif` avant `9.tif` : le profil de profondeur
    sortirait melange, et un pic au bon endroit apparaitrait au mauvais.
    """
    # ⚠ Le filtre n'est pas un confort : deux segments telecharges avec des plages
    # differentes (26 couches ici, 38 la) ont des « tiers centraux » de largeurs
    # differentes, donc leurs pourcentages ne se comparent pas. Restreindre a une plage
    # commune est la condition pour que le chiffre veuille dire la meme chose.
    files = [p for p in folder.iterdir()
             if p.suffix == ".tif" and first <= int(p.stem) <= last]
    return sorted(files, key=lambda p: int(p.stem))


def profile(folder: Path, top: int, left: int, size: int) -> dict:
    import tifffile

    files = layer_files(folder)
    if not files:
        raise RuntimeError(f"aucune couche dans {folder}")
    means, contrasts, indices = [], [], []
    for path in files:
        with tifffile.TiffFile(path) as handle:
            page = handle.pages[0]
            window = page.asarray()[top:top + size, left:left + size]
        patch = window.astype(np.float32)
        if patch.size == 0:
            continue
        means.append(float(patch.mean()))
        # Passe-haut a la main : la difference a une moyenne 3x3 obtenue par decalage.
        # ⚠ Sans dependance a scipy : ce fichier doit tourner la ou tifffile suffit.
        blur = (patch[:-2, 1:-1] + patch[2:, 1:-1] + patch[1:-1, :-2]
                + patch[1:-1, 2:] + patch[1:-1, 1:-1]) / 5.0
        contrasts.append(float((patch[1:-1, 1:-1] - blur).std()))
        indices.append(int(path.stem))
    return {"layers": indices, "mean": means, "contrast": contrasts}


def grid_profiles(folder: Path, size: int, step: int, floor: float,
                  first: int = 0, last: int = 10**9) -> dict:
    """Le pic de contraste tombe-t-il au MEME endroit partout sur le segment ?

    ⚠⚠ **C'est une mesure de qualite de TRACE, et elle ne demande ni verite terrain, ni
    modele d'encre, ni juge.** Une trace bien posee suit la feuille : la surface tombe
    alors a la meme profondeur d'un bout a l'autre, et le pic de contraste est au meme
    indice partout. Une trace qui derive, saute de spire ou s'enfonce dans le vide fait
    voyager ce pic -- et c'est visible dans les couches elles-memes, sans rien d'autre.

    Trouve en cherchant pourquoi le detecteur echoue sur Scroll 4 : deux fenetres du
    MEME segment ont rendu leur pic aux deux bords opposes de la pile (couche 40 d'un
    cote, couche 15 de l'autre). Sur le segment de Scroll 1 qui donne l'AUC 0,925, le
    pic tombe au centre.

    ⚠ **Les couches sont lues une seule fois chacune, toutes fenetres confondues.** Une
    couche fait ~500 Mo et `asarray()` la decode entiere : boucler sur les fenetres a
    l'exterieur relirait la pile autant de fois qu'il y a de fenetres.

    ⚠ Une fenetre sans matiere n'a pas de surface. Celles dont l'intensite maximale
    reste sous `floor` fois le maximum global sont **ecartees et comptees**, pas
    creditees d'un pic arbitraire.
    """
    import tifffile

    files = layer_files(folder, first, last)
    if not files:
        raise RuntimeError(f"aucune couche dans {folder} entre {first} et {last}")
    with tifffile.TiffFile(files[0]) as handle:
        rows, cols = handle.pages[0].shape
    windows = [(t, l) for t in range(0, rows - size + 1, step)
               for l in range(0, cols - size + 1, step)]
    if not windows:
        raise RuntimeError(f"{rows}x{cols} : trop petit pour des fenetres de {size}")

    contrast = np.zeros((len(files), len(windows)))
    peak_value = np.zeros(len(windows))
    for depth, path in enumerate(files):
        with tifffile.TiffFile(path) as handle:
            plane = handle.pages[0].asarray()
        for index, (top, left) in enumerate(windows):
            patch = plane[top:top + size, left:left + size].astype(np.float32)
            blur = (patch[:-2, 1:-1] + patch[2:, 1:-1] + patch[1:-1, :-2]
                    + patch[1:-1, 2:] + patch[1:-1, 1:-1]) / 5.0
            contrast[depth, index] = float((patch[1:-1, 1:-1] - blur).std())
            peak_value[index] = max(peak_value[index], float(patch.max()))

    alive = peak_value >= floor * peak_value.max()
    peaks = np.argmax(contrast[:, alive], axis=0)
    at_edge = ((peaks == 0) | (peaks == len(files) - 1))
    # ⚠ La grandeur qui separe les deux segments n'est ni la mediane ni l'ecart
    # interquartile -- toutes deux se laissent tirer par une distribution BIMODALE, et
    # c'est justement la forme qu'on observe. Ce qui se lit sans ambiguite, c'est la
    # part des fenetres dont le pic tombe dans le TIERS CENTRAL de ce qui est lu : la
    # surface est dedans, ou elle ne l'est pas.
    low, high = len(files) // 3, 2 * len(files) // 3
    inside = ((peaks >= low) & (peaks < high))
    return {"windows": len(windows), "avec_matiere": int(alive.sum()),
            "tiers_central": float(inside.mean()),
            "layers": [int(p.stem) for p in files],
            "peaks": [int(v) for v in peaks],
            "peak_median": float(np.median(peaks)),
            "peak_iqr": float(np.percentile(peaks, 75) - np.percentile(peaks, 25)),
            "au_bord": float(at_edge.mean())}


def normalise(values: list[float]) -> np.ndarray:
    """Ramene un profil a [0, 1] DANS SA PROPRE pile — voir l'en-tete."""
    array = np.asarray(values, dtype=float)
    span = array.max() - array.min()
    return (array - array.min()) / span if span > 0 else np.zeros_like(array)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profil de profondeur : la surface est-elle dans la fenetre lue ?",
        epilog="Compare la FORME des profils, jamais les niveaux bruts.",
    )
    parser.add_argument("folders", type=Path, nargs="+", help="repertoires de couches")
    parser.add_argument("--top", type=int, default=2000)
    parser.add_argument("--left", type=int, default=2000)
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--grid", action="store_true",
                        help="balayer le segment entier au lieu d'une seule fenetre")
    parser.add_argument("--step", type=int, default=1024, help="pas du balayage")
    parser.add_argument("--from-layer", type=int, default=0,
                        help="premiere couche retenue -- a poser quand les piles "
                             "n'ont pas la meme profondeur, sinon les tiers centraux "
                             "n'ont pas la meme largeur et ne se comparent pas")
    parser.add_argument("--to-layer", type=int, default=10**9)
    parser.add_argument("--floor", type=float, default=0.5,
                        help="une fenetre dont l'intensite max reste sous cette fraction "
                             "du max global n'a pas de matiere : ecartee et comptee")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.grid:
        report = []
        for folder in args.folders:
            data = grid_profiles(folder, args.size, args.step, args.floor,
                                 args.from_layer, args.to_layer)
            names = data["layers"]
            print(f"\n=== {folder.name} — {data['avec_matiere']} fenetres avec matiere "
                  f"sur {data['windows']} ===")
            counts = np.bincount(data["peaks"], minlength=len(names))
            for i, name in enumerate(names):
                bar = "#" * int(round(counts[i] / max(1, counts.max()) * 40))
                if counts[i]:
                    print(f"  pic a la couche {name:3d}  {counts[i]:4d}  {bar}")
            print(f"  mediane du pic : couche {names[int(data['peak_median'])]} "
                  f"| ecart interquartile : {data['peak_iqr']:.1f} couches")
            print(f"  ⭐ pic dans le TIERS CENTRAL : {data['tiers_central'] * 100:.0f} %"
                  f"   | au bord de la fenetre : {data['au_bord'] * 100:.0f} %")
            report.append({"folder": folder.name, **data})
        if args.out:
            args.out.write_text(json.dumps(report, indent=2) + "\n")
            print(f"\necrit : {args.out}")
        return 0

    report = []
    for folder in args.folders:
        try:
            data = profile(folder, args.top, args.left, args.size)
        except (RuntimeError, ValueError) as error:
            print(f"{folder.name} : {error}", file=sys.stderr)
            continue
        contrast = normalise(data["contrast"])
        mean = normalise(data["mean"])
        peak = int(np.argmax(contrast))
        # ⚠ Ce qui tranche n'est pas la valeur du pic mais SA POSITION dans la fenetre.
        # Un pic au bord veut dire que la surface est probablement DEHORS, et qu'on ne
        # voit que le flanc de sa montee.
        edge = peak == 0 or peak == len(contrast) - 1
        print(f"\n=== {folder.name} — {len(contrast)} couches "
              f"({data['layers'][0]} a {data['layers'][-1]}) ===")
        for i, index in enumerate(data["layers"]):
            bar = "#" * int(round(contrast[i] * 40))
            print(f"  couche {index:3d}  contraste {contrast[i]:5.3f} "
                  f"moyenne {mean[i]:5.3f}  {bar}")
        print(f"  pic de contraste : couche {data['layers'][peak]} "
              f"(position {peak + 1}/{len(contrast)})"
              + ("   ⚠ AU BORD — la surface est probablement hors fenetre" if edge else ""))
        report.append({"folder": folder.name, "layers": data["layers"],
                       "contrast": data["contrast"], "mean": data["mean"],
                       "peak_layer": data["layers"][peak], "peak_position": peak,
                       "peak_at_edge": edge})

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
