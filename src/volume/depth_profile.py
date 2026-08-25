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


def layer_files(folder: Path, first: int = 0, last: int = 10**9,
                step: int = 1) -> list[Path]:
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
    files = sorted(files, key=lambda p: int(p.stem))
    # ⚠ Sous-echantillonner les couches divise le TELECHARGEMENT autant que la lecture :
    # une pile complete fait 32 Go, et valider l'instrument sur une population en
    # demande une dizaine. Le profil n'a besoin que de la FORME de la courbe, pas de
    # chaque couche -- mais c'est une affirmation, donc elle se verifie (voir le temoin
    # « profondeur : sous-echantillonnage » dans src/outils/temoins.sh).
    return files[::step] if step > 1 else files


def profile(folder: Path, top: int, left: int, size: int,
            first: int = 0, last: int = 10**9, layer_step: int = 1) -> dict:
    import tifffile

    files = layer_files(folder, first, last, layer_step)
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
                  first: int = 0, last: int = 10**9, layer_step: int = 1,
                  traced: int = 32, voxel_um: float = 7.91,
                  amplitude_min: float = 0.02) -> dict:
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

    files = layer_files(folder, first, last, layer_step)
    if not files:
        raise RuntimeError(f"aucune couche dans {folder} entre {first} et {last}")
    with tifffile.TiffFile(files[0]) as handle:
        rows, cols = handle.pages[0].shape
    windows = [(t, l) for t in range(0, rows - size + 1, step)
               for l in range(0, cols - size + 1, step)]
    if not windows:
        raise RuntimeError(f"{rows}x{cols} : trop petit pour des fenetres de {size}")

    contrast = np.zeros((len(files), len(windows)))
    density = np.zeros((len(files), len(windows)))
    peak_value = np.zeros(len(windows))
    for depth, path in enumerate(files):
        with tifffile.TiffFile(path) as handle:
            plane = handle.pages[0].asarray()
        for index, (top, left) in enumerate(windows):
            patch = plane[top:top + size, left:left + size].astype(np.float32)
            blur = (patch[:-2, 1:-1] + patch[2:, 1:-1] + patch[1:-1, :-2]
                    + patch[1:-1, 2:] + patch[1:-1, 1:-1]) / 5.0
            contrast[depth, index] = float((patch[1:-1, 1:-1] - blur).std())
            density[depth, index] = float(patch.mean())
            peak_value[index] = max(peak_value[index], float(patch.max()))

    # ⚠⚠ L'AMPLITUDE du profil, et pourquoi elle vient AVANT le pic. Le piege nº 20 du
    # depot dit « afficher la courbe avant de croire son argmax » ; ce bloc l'ecrit dans
    # l'outil. Un profil plat a quand meme un maximum, parfaitement defini, et sa position
    # est du bruit -- mais elle sort en « pic a la couche 0 » exactement comme un vrai pic.
    # Sur une pile de 21 couches ou la surface est au centre, cette confusion est le mode
    # d'echec le plus probable : les deux positions extremes ramassent le bruit des deux
    # bouts et la distribution parait BIMODALE, ce qui ressemble a « la trace est entre
    # deux feuilles ».
    with np.errstate(invalid="ignore", divide="ignore"):
        moyennes = density.mean(axis=0)
        amplitude = np.where(moyennes > 0,
                             (density.max(axis=0) - density.min(axis=0))
                             / np.maximum(moyennes, 1e-9), 0.0)
    # ⚠⚠ LE SEUIL DE MATIERE EST RELATIF, ET UNE PILE VIDE LE SATISFAIT ENTIEREMENT.
    # `peak_value >= floor * peak_value.max()` demande « cette fenetre est-elle claire par
    # rapport a la plus claire d ici ». Sur une pile ENTIEREMENT NOIRE le maximum vaut 0,
    # donc le seuil vaut 0, donc `>= 0` est vrai partout : les 49 fenetres sont declarees
    # « avec matiere » sur une image ou aucun pixel n est allume. C est la vérification
    # incapable d echouer, dans l instrument qui juge tout le reste -- et elle a fait
    # publier « les cinq m7 lisent zero, leur platitude est reelle » sur cinq rendus VIDES.
    # Mesure : max des pixels = 0 sur les 161 couches des cinq piles m7, 255 sur ps256.
    #
    # ⚠ Le correctif n est PAS un seuil absolu choisi -- ce serait un nombre transporte de
    # plus. Un pixel a zero n a pas de matiere par definition du format, sans calibration :
    # il suffit d exiger que le pic soit STRICTEMENT positif.
    pic_global = float(peak_value.max())
    alive = (peak_value >= floor * pic_global) & (peak_value > 0.0)
    # ⚠⚠ Et la pile vide se DIT, au lieu de sortir en statistiques nulles qui ressemblent a
    # une surface plate. « il n y a rien a lire » et « ce que je lis est plat » sont deux
    # faits differents, et les confondre est exactement ce qui vient d etre paye.
    pile_vide = bool(pic_global <= 0.0)
    # ⚠⚠ ON REFUSE, on ne rapporte pas. Laisser passer une pile vide produirait un profil
    # entierement a zero et a nan -- un fichier qui a l air d un resultat, et qui a ete lu
    # comme « surface parfaitement plate ». Le refus nomme le fait mesure (le pic global),
    # donc l appelant sait si le rendu a echoue ou si la surface est reellement sombre.
    if pile_vide:
        raise RuntimeError(
            f"{folder} : la pile est VIDE — pic global = {pic_global:g} sur "
            f"{len(files)} couches. Ce n'est pas une surface plate, c'est un rendu qui n'a "
            f"rien produit. Le seuil de matiere etant relatif au maximum de la pile, une "
            f"pile noire le satisfait entierement : sans ce refus, les "
            f"{len(windows)} fenetres sortiraient « avec matiere ».")
    peaks = np.argmax(contrast[:, alive], axis=0)
    # ⚠⚠ L'INTENSITE est le localisateur robuste, le contraste ne l'est pas. Sur les
    # piles a 7,91 µm les deux coincident ; sur un volume a 2,4 µm qui resout les fibres,
    # le contraste devient un U -- maximal aux DEUX bords, minimal dans la feuille --
    # parce qu'il suit les interfaces et le bruit, pas la matiere. Trouve en affichant la
    # courbe au lieu de faire confiance a son argmax.
    dense_peaks = np.argmax(density[:, alive], axis=0)
    at_edge = ((peaks == 0) | (peaks == len(files) - 1))
    # ⚠⚠ « au bord » N'EST PAS comparable entre deux pas de balayage : avec 9 couches
    # lues au lieu de 65, l'argmax a mecaniquement plus de chances de tomber sur l'une
    # des deux positions extremes. Mesure : 61 % / 67 % / 72 % / 80 % pour les pas
    # 1, 2, 4, 8, sur le MEME segment. C'est le tiers central qu'il faut lire.
    # ⚠ La grandeur qui separe les deux segments n'est ni la mediane ni l'ecart
    # interquartile -- toutes deux se laissent tirer par une distribution BIMODALE, et
    # c'est justement la forme qu'on observe. Ce qui se lit sans ambiguite, c'est la
    # part des fenetres dont le pic tombe dans le TIERS CENTRAL de ce qui est lu : la
    # surface est dedans, ou elle ne l'est pas.
    low, high = len(files) // 3, 2 * len(files) // 3
    inside = ((peaks >= low) & (peaks < high))
    inside_dense = ((dense_peaks >= low) & (dense_peaks < high))
    # ⚠⚠ LA grandeur comparable entre conventions : l'ecart entre le pic de matiere et
    # la SURFACE TRACEE, en micrometres. Un « tiers central » se rapporte a la fenetre
    # lue, or la fenetre 15-40 d'une pile de 65 n'est PAS centree sur la couche 32 --
    # donc ce chiffre ne mesure pas la meme chose ici et sur un volume de surface dont
    # la trace est au milieu. Deux volumes n'ont ni le meme nombre de couches ni la meme
    # taille de voxel ; un ecart en µm, si.
    numbers = np.asarray([int(p.stem) for p in files])
    offsets = np.abs(numbers[dense_peaks] - traced) * voxel_um
    # ⚠ L'ecart interquartile se rapporte en COUCHES, pas en positions echantillonnees :
    # sinon un balayage une couche sur 4 annonce 15 la ou il y en a 61, et deux runs du
    # meme segment a deux pas semblent mesurer deux choses. Mesure : 61,0 / 62,0 / 60,8 /
    # 64,0 pour les pas 1, 2, 4, 8 -- constant une fois remis a l'echelle.
    spread = float(np.percentile(peaks, 75) - np.percentile(peaks, 25)) * layer_step

    # Les memes parts, restreintes aux fenetres dont le profil a REELLEMENT une forme.
    amp_alive = amplitude[alive]
    relief = amp_alive >= amplitude_min
    if relief.any():
        bord_relief = float(((dense_peaks[relief] == 0)
                             | (dense_peaks[relief] == len(files) - 1)).mean())
        centre_relief = float(((dense_peaks[relief] >= low)
                               & (dense_peaks[relief] < high)).mean())
    else:
        bord_relief = centre_relief = float("nan")

    return {"windows": len(windows), "avec_matiere": int(alive.sum()),
            # ⚠ Le pic global voyage AVEC le profil : un lecteur doit pouvoir voir a quel
            # point une pile est proche du vide sans relire les images.
            "pic_global": pic_global, "pile_vide": pile_vide,
            "amplitude_mediane": float(np.median(amp_alive)) if alive.any() else 0.0,
            "amplitude_min": float(amplitude_min),
            "fenetres_avec_relief": int(relief.sum()),
            "part_plates": float(1.0 - relief.mean()) if alive.any() else 1.0,
            "au_bord_relief": bord_relief,
            "tiers_central_relief": centre_relief,
            "tiers_central": float(inside.mean()),
            "tiers_central_intensite": float(inside_dense.mean()),
            "au_bord_intensite": float(((dense_peaks == 0)
                                        | (dense_peaks == len(files) - 1)).mean()),
            "pic_intensite_median": float(np.median(dense_peaks)),
            "ecart_trace_um_median": float(np.median(offsets)),
            "ecart_trace_um_p90": float(np.percentile(offsets, 90)),
            "couche_tracee": int(traced), "voxel_um": float(voxel_um),
            "layers": [int(p.stem) for p in files],
            "peaks": [int(v) for v in peaks],
            "peak_median": float(np.median(peaks)),
            "peak_iqr": spread,
            "layer_step": int(layer_step),
            # ⚠⚠ LA GEOMETRIE DE LECTURE DANS LE PROFIL LUI-MEME. L amplitude depend de
            # l etendue de la fenetre d analyse (exposant mesure -0,83) autant que de la
            # profondeur, donc un profil qui ne dit pas dans quelle fenetre il a ete lu ne
            # se compare a rien. Paye le 2026-08-24 : un seuil, deux taux d erreur et une
            # profondeur transportes hors de leur geometrie, aucun trouve en relisant.
            "size": int(size),
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
    # ⚠ `nargs="*"` et non `"+"` : `--verifier` fabrique ses propres piles et n'a aucun
    # repertoire a recevoir. Un drapeau de verification qui exige un argument de travail est
    # un drapeau que personne ne lance.
    parser.add_argument("folders", type=Path, nargs="*", help="repertoires de couches")
    parser.add_argument("--verifier", action="store_true",
                        help="lancer les temoins hors ligne et sortir")
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
    parser.add_argument("--traced-layer", type=int, default=32,
                        help="indice de la surface tracee dans la pile COMPLETE "
                             "(defaut: 32, soit le milieu des 65 couches de `-r 32`)")
    parser.add_argument("--voxel-um", type=float, default=7.91)
    parser.add_argument("--layer-step", type=int, default=1,
                        help="ne lire qu'une couche sur N : divise d'autant le "
                             "telechargement ET la lecture (defaut: 1 = toutes)")
    parser.add_argument("--floor", type=float, default=0.5,
                        help="une fenetre dont l'intensite max reste sous cette fraction "
                             "du max global n'a pas de matiere : ecartee et comptee")
    parser.add_argument("--amplitude-min", type=float, default=0.02,
                        help="⚠ amplitude relative (max-min)/moyenne en dessous de "
                             "laquelle un profil est PLAT : son argmax est du bruit, et "
                             "le bruit sort aux deux bords, ce qui imite une bimodalite")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    if args.verifier:
        return verifier()
    if not args.folders:
        parser.error("donner au moins un repertoire de couches, ou --verifier")

    if args.grid:
        report = []
        for folder in args.folders:
            data = grid_profiles(folder, args.size, args.step, args.floor,
                                 args.from_layer, args.to_layer, args.layer_step,
                                 args.traced_layer, args.voxel_um)
            names = data["layers"]
            print(f"\n=== {folder.name} — {data['avec_matiere']} fenetres avec matiere "
                  f"sur {data['windows']} ===")
            counts = np.bincount(data["peaks"], minlength=len(names))
            for i, name in enumerate(names):
                bar = "#" * int(round(counts[i] / max(1, counts.max()) * 40))
                if counts[i]:
                    print(f"  pic a la couche {name:3d}  {counts[i]:4d}  {bar}")
            print(f"  mediane du pic : couche {names[int(data['peak_median'])]} "
                  f"| ecart interquartile : {data['peak_iqr']:.1f} couches "
                  f"(pas {data['layer_step']})")
            print(f"  contraste  — tiers central {data['tiers_central'] * 100:5.0f} %"
                  f"   au bord {data['au_bord'] * 100:5.0f} %")
            print(f"  ⭐ INTENSITE — tiers central {data['tiers_central_intensite'] * 100:5.0f} %"
                  f"   au bord {data['au_bord_intensite'] * 100:5.0f} %"
                  f"   pic median couche {names[int(data['pic_intensite_median'])]}")
            print(f"  ⭐⭐ ECART A LA TRACE (couche {data['couche_tracee']}) : "
                  f"median {data['ecart_trace_um_median']:.0f} µm   "
                  f"p90 {data['ecart_trace_um_p90']:.0f} µm")
            plates = data["part_plates"] * 100
            print(f"  ⚠ AMPLITUDE du profil : mediane {data['amplitude_mediane'] * 100:.1f} %"
                  f"   plates {plates:.0f} %"
                  f"   ({data['fenetres_avec_relief']} fenetres avec relief)")
            if data["fenetres_avec_relief"]:
                print(f"     restreint au relief — tiers central "
                      f"{data['tiers_central_relief'] * 100:5.0f} %"
                      f"   au bord {data['au_bord_relief'] * 100:5.0f} %")
            if plates >= 50.0:
                print("  ⚠⚠ plus de la moitie des profils sont PLATS : leur argmax est du "
                      "bruit, et le bruit sort aux deux bords. Les parts « au bord » "
                      "ci-dessus ne decrivent alors pas la trace.")
            report.append({"folder": folder.name, **data})
        if args.out:
            args.out.write_text(json.dumps(report, indent=2) + "\n")
            print(f"\necrit : {args.out}")
        return 0

    report = []
    for folder in args.folders:
        try:
            data = profile(folder, args.top, args.left, args.size,
                       args.from_layer, args.to_layer, args.layer_step)
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


def verifier() -> int:
    """Les temoins de l'instrument qui juge tout le reste.

    ⚠⚠ CE FICHIER N'EN AVAIT AUCUN. Il produit chaque chiffre de relief de ce projet -- donc
    le classement des candidats, la calibration, le contraste des appuis -- et rien ne
    verifiait qu'il sait encore mesurer, ni surtout qu'il sait ECHOUER. Le prix a ete paye :
    son test de matiere etant relatif au maximum de la pile, une pile entierement noire le
    satisfaisait entierement, et cinq rendus VIDES ont ete publies comme « surfaces
    parfaitement plates ».

    Les piles de controle sont fabriquees ici, en memoire puis sur disque, parce que la
    distinction qui compte ne se voit que sur trois cas cote a cote : une pile noire, une
    pile uniformement ECLAIREE, et une pile qui porte une bosse. Les deux premieres sortaient
    le meme verdict ; ce sont deux faits differents.
    """
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

    racine = Path(tempfile.mkdtemp(prefix="depth_profile_temoins_"))

    def pile(nom, faire, couches=21, cote=300):
        d = racine / nom
        d.mkdir(parents=True, exist_ok=True)
        for i in range(couches):
            tifffile.imwrite(str(d / f"{i:03d}.tif"), faire(i, cote))
        return d

    def vide(_i, cote):
        return np.zeros((cote, cote), dtype=np.uint8)

    def uniforme(_i, cote):
        # ⚠ Uniforme mais ECLAIREE, et avec du grain dans le PLAN : sans grain le contraste
        # est nul partout et on testerait un cas degenere qui n'existe pas dans un rendu.
        g = np.zeros((cote, cote), dtype=np.uint8)
        g[::3, ::3] = 200
        g[1::5, 2::5] = 120
        return g + 40

    def bosse(i, cote, centre=10, largeur=3.0):
        # Une vraie surface : l'intensite culmine a la couche `centre`.
        poids = float(np.exp(-((i - centre) ** 2) / (2 * largeur ** 2)))
        return (uniforme(i, cote).astype(np.float64) * (0.2 + 0.8 * poids)).astype(np.uint8)

    d_vide = pile("vide", vide)
    d_plate = pile("plate", uniforme)
    d_bosse = pile("bosse", bosse)

    # ⚠⚠ LE CAS QUI A COUTE : une pile noire est REFUSEE, et le refus nomme le pic global.
    try:
        grid_profiles(d_vide, 128, 100, 0.1, 0, 10**9, 1, 10, 2.4)
        v("une pile vide est refusee", False, "aucune exception")
    except RuntimeError as erreur:
        v("une pile vide est refusee", True)
        v("... et le refus nomme le pic global", "pic global" in str(erreur), str(erreur)[:80])
        v("... et il dit que ce n'est pas une surface plate",
          "plate" in str(erreur), str(erreur)[:80])

    plate = grid_profiles(d_plate, 128, 100, 0.1, 0, 10**9, 1, 10, 2.4)
    v("une pile uniforme ECLAIREE n'est pas refusee", plate["avec_matiere"] > 0)
    v("... son pic global est celui des pixels", plate["pic_global"] > 0.0,
      str(plate["pic_global"]))
    v("... elle n'est pas dite vide", plate["pile_vide"] is False)
    # ⚠ C'est ICI que « plat » veut dire quelque chose : de la matiere, et pas de forme.
    v("... et elle se lit PLATE", plate["part_plates"] == 1.0, str(plate["part_plates"]))
    v("... donc aucune fenetre n'a de relief", plate["fenetres_avec_relief"] == 0)

    forme = grid_profiles(d_bosse, 128, 100, 0.1, 0, 10**9, 1, 10, 2.4)
    v("une pile avec bosse a du relief", forme["fenetres_avec_relief"] > 0,
      str(forme["fenetres_avec_relief"]))
    v("... et son amplitude depasse celle de la plate",
      forme["amplitude_mediane"] > plate["amplitude_mediane"],
      f"{forme['amplitude_mediane']:.4f} contre {plate['amplitude_mediane']:.4f}")
    # ⚠⚠ La position du pic est ce qui distingue une mesure d'un argmax de bruit. La bosse
    # est posee couche 10 sur 21, donc au tiers central.
    v("... et son pic d'intensite tombe sur la bosse",
      abs(forme["pic_intensite_median"] - 10) <= 1, str(forme["pic_intensite_median"]))
    v("... donc dans le tiers central", forme["tiers_central_intensite"] > 0.5,
      str(forme["tiers_central_intensite"]))

    # ⚠ LE CAS NEGATIF DU SEUIL RELATIF, qui reste utile quand la pile n'est pas vide : une
    # fenetre sombre a cote d'une fenetre claire doit etre ECARTEE, pas creditee d'un pic.
    d_mixte = racine / "mixte"
    d_mixte.mkdir()
    # ⚠ L'image est plus large que les autres, et la zone morte assez grande pour qu'une
    # fenetre ENTIERE y tombe : avec 300 px de cote et un pas de 100, toutes les fenetres
    # de 128 px mordent sur la moitie eclairee, donc le controle ne pouvait pas echouer --
    # il rendait « 4 sur 4 » et disait seulement que le decoupage chevauche.
    for i in range(21):
        g = bosse(i, 500)
        g[:, 250:] = 0  # la moitie droite n'a aucune matiere
        tifffile.imwrite(str(d_mixte / f"{i:03d}.tif"), g)
    mixte = grid_profiles(d_mixte, 128, 100, 0.1, 0, 10**9, 1, 10, 2.4)
    v("une moitie sans matiere est ecartee", mixte["avec_matiere"] < mixte["windows"],
      f"{mixte['avec_matiere']} sur {mixte['windows']}")
    v("... mais pas toutes les fenetres", mixte["avec_matiere"] > 0)

    shutil.rmtree(racine, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
