#!/usr/bin/env python3
"""L'onde radiale : compter les feuilles depuis l'axe, et deplier la coupe.

Idee de l'auteur : *« c'est envoyer une onde traversant toutes les couches depuis le
centre »*. Chaque mur franchi le long d'un rayon est une feuille. Ca se mesure
**directement dans le volume**, donc sans dependre d'aucun tracage -- ce qui en fait
la verite contre laquelle juger les tracages, et non un resultat de plus a comparer.

⚠⚠ **Ce fichier existe parce qu'il n'existait pas.** La premiere version de cette
mesure a ete ecrite en `python -c` inline : le resultat (158 feuilles, 11,2 m de
papyrus) est parti dans un document, et **le code qui l'a produit n'etait nulle part**.
Un chiffre publie dont le calcul n'est pas dans l'arbre n'est pas un resultat, c'est
une anecdote. La regle qui en decoule est dans `06` §5.

Trois sous-commandes, du meme acces au volume et du meme centre :

    centre    derive l'axe du rouleau depuis une trace, et l'ECRIT dans le depot
    compter   l'onde radiale : feuilles par rayon, espacement, longueur estimee
    deplier   la coupe en coordonnees polaires -- les spires deviennent des lignes
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

VOXEL_UM = 7.91
"""Taille du voxel en micrometres, pour les volumes 7,910 um de la campagne 2024."""

SHEET_UM = 40.0
"""Epaisseur typique d'une feuille de papyrus. Sert a fixer le lissage : on lisse a
l'echelle d'une feuille pour ne pas compter le grain du materiau comme des murs."""

CACHE = Path(__file__).resolve().parents[3] / "data" / "axes"
"""Ou vivent les centres derives. ⚠ PAS /tmp : la version inline y ecrivait, donc la
mesure devenait irreproductible des que la machine redemarrait."""


class RadialError(RuntimeError):
    """Leve quand la geometrie ou l'acces ne permet pas la mesure."""


def open_volume(url: str, level: str = "0"):
    """Ouvrir un volume OME-Zarr distant sans le telecharger.

    Le niveau est un parametre : le rouleau entier en pleine resolution fait des
    teraoctets, et une coupe unique suffit a l'onde radiale.
    """
    import fsspec
    import zarr

    group = zarr.open(fsspec.get_mapper(url, anon=True), mode="r")
    return group[level]


def derive_centre(mesh_dir: Path, sample: int = 15000, seed: int = 0) -> tuple:
    """L'axe du rouleau, DERIVE d'une trace et non lu dans un fichier.

    Une trace de rouleau EST une spirale autour de son axe : le seul centre pour
    lequel l'angle croit regulierement le long du deroulement est le bon. On le
    cherche donc par cette propriete, **qu'on peut ensuite verifier**, plutot que de
    faire confiance a l'ombilic publie par ThaumatoAnakalyptor -- qui est dans un
    repere ne correspondant pas a ces traces.
    """
    import tifffile
    from scipy.optimize import minimize
    from scipy.stats import spearmanr

    planes = []
    for axis in "xyz":
        found = sorted(mesh_dir.glob(f"{axis}.tif"))
        if not found:
            raise RadialError(f"plan absent : {mesh_dir}/{axis}.tif")
        planes.append(tifffile.imread(found[0]))
    x, y, z = planes
    valid = (x != -1) & (y != -1) & (z != -1)
    if not valid.any():
        raise RadialError(f"aucune cellule valide dans {mesh_dir}")
    _, cols = np.nonzero(valid)
    X, Y, Z = x[valid], y[valid], z[valid]

    generator = np.random.default_rng(seed)
    take = generator.choice(X.size, min(sample, X.size), replace=False)
    xs, ys, cs = X[take], Y[take], cols[take]
    order = np.argsort(cs)

    def cost(centre):
        angle = np.unwrap(np.arctan2(ys - centre[1], xs - centre[0])[order])
        return -abs(spearmanr(np.arange(angle.size), angle).statistic)

    best = None
    for gx in np.linspace(X.min(), X.max(), 4):
        for gy in np.linspace(Y.min(), Y.max(), 4):
            found = minimize(cost, [gx, gy], method="Nelder-Mead",
                             options={"maxiter": 250, "xatol": 5, "fatol": 1e-4})
            if best is None or found.fun < best.fun:
                best = found
    return float(best.x[0]), float(best.x[1]), float(Z.min()), float(Z.max()), float(-best.fun)


def ray_profile(plane: np.ndarray, cx: float, cy: float, degrees: float,
                reach: float, step: float = 1.0) -> np.ndarray:
    """Intensites le long d'un rayon partant du centre."""
    height, width = plane.shape
    theta = np.deg2rad(degrees)
    radii = np.arange(0.0, reach, step)
    xs = np.rint(cx + radii * np.cos(theta)).astype(np.int64)
    ys = np.rint(cy + radii * np.sin(theta)).astype(np.int64)
    inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
    return plane[ys[inside], xs[inside]].astype(np.float32)


def count_sheets(profile: np.ndarray, prominence: float, min_gap: int) -> tuple:
    """Nombre de feuilles franchies le long d'un profil, et leur espacement.

    Le lissage est fixe par l'EPAISSEUR D'UNE FEUILLE et non regle a la main : sans
    lui on compte le grain du materiau, avec un noyau plus large on fusionne deux
    spires voisines. Cinq voxels a 7,91 um font 40 um, soit une feuille.
    """
    from scipy.signal import find_peaks

    window = max(3, int(round(SHEET_UM / VOXEL_UM)))
    smoothed = np.convolve(profile, np.ones(window) / window, mode="same")
    peaks, _ = find_peaks(smoothed, prominence=prominence, distance=min_gap)
    spacing = float(np.diff(peaks).mean() * VOXEL_UM) if peaks.size > 2 else float("nan")
    return peaks, spacing, smoothed


def unwrap_polar(plane: np.ndarray, cx: float, cy: float, reach: float,
                 angular: int | None = None) -> np.ndarray:
    """Deplier la coupe en (rayon, angle) : les spires deviennent des LIGNES.

    C'est l'idee C2, et son interet n'est pas cosmetique. Dans la coupe cartesienne
    une spire est un arc dont la courbure change avec le rayon, donc la suivre demande
    un modele de spirale. Depliee, la meme spire est une ligne quasi horizontale, et
    « suivre une feuille » redevient du traitement d'image ordinaire -- ce qui est
    exactement ce qui manquait a la localisation des fusions par comptage, qui avait
    echoue en traitant chaque angle independamment.

    ⚠ **L'echantillonnage angulaire est fixe par la circonference EXTERIEURE.** A un
    rayon r, un degre couvre r*pi/180 pixels : choisir un pas angulaire confortable
    pour le coeur perdrait de la matiere au bord, et une fusion manquee au bord est
    precisement ce qu'on cherche. Sur-echantillonner le coeur ne coute qu'un peu de
    memoire et n'invente rien.
    """
    if angular is None:
        angular = int(np.ceil(2.0 * np.pi * reach))
    height, width = plane.shape
    thetas = np.linspace(0.0, 2.0 * np.pi, angular, endpoint=False)
    radii = np.arange(0.0, reach, 1.0)
    xs = np.rint(cx + np.outer(radii, np.cos(thetas))).astype(np.int64)
    ys = np.rint(cy + np.outer(radii, np.sin(thetas))).astype(np.int64)
    inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
    out = np.zeros(xs.shape, dtype=plane.dtype)
    out[inside] = plane[ys[inside], xs[inside]]
    return out


def spiral_length_mm(turns: int, outer_radius_mm: float) -> float:
    """Longueur d'une spirale d'Archimede : la somme des circonferences.

    ⚠ C'est une borne SUPERIEURE du nombre de spires et donc de la longueur : deux
    feuilles fondues ensemble sont comptees pour une, jamais pour deux.
    """
    return sum(2.0 * np.pi * (outer_radius_mm * (i + 0.5) / turns) for i in range(turns))


def cmd_centre(args) -> int:
    mesh = Path(args.mesh)
    if mesh.is_dir() and not (mesh / "x.tif").is_file():
        found = glob.glob(str(mesh / "**" / "*.tifxyz"), recursive=True)
        if found:
            mesh = Path(found[0])
    cx, cy, z0, z1, quality = derive_centre(mesh, args.sample, args.seed)
    # Un centre mal derive rendrait tout le reste sans valeur : on refuse plutot que
    # de rapporter des comptes qui ne mesureraient que le mauvais centre.
    if quality < 0.9:
        print(f"erreur : centre peu fiable (monotonie {quality:.3f} < 0.9)", file=sys.stderr)
        return 3
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{args.name}.json"
    out.write_text(json.dumps(
        {"name": args.name, "mesh": str(mesh), "cx": cx, "cy": cy,
         "z_min": z0, "z_max": z1, "spiral_monotonicity": quality}, indent=2) + "\n")
    print(f"centre {args.name} : x={cx:.0f} y={cy:.0f}  (monotonie {quality:.3f})")
    print(f"trace : z de {z0:.0f} a {z1:.0f}")
    print(f"ecrit : {out}")
    return 0


def load_centre(name: str) -> dict:
    path = CACHE / f"{name}.json"
    if not path.is_file():
        raise RadialError(f"centre absent : {path} -- lancer d'abord la sous-commande 'centre'")
    return json.loads(path.read_text())


def cmd_count(args) -> int:
    centre = load_centre(args.name)
    array = open_volume(args.volume, args.level)
    z = args.slice if args.slice >= 0 else int((centre["z_min"] + centre["z_max"]) / 2)
    plane = array[z]
    print(f"volume {array.shape} | tranche z={z} | centre ({centre['cx']:.0f}, {centre['cy']:.0f})")

    counts, radii, spacings = [], [], []
    for degrees in range(0, 360, args.step_deg):
        profile = ray_profile(plane, centre["cx"], centre["cy"], degrees, args.reach)
        if profile.size < 500:
            continue
        peaks, spacing, smoothed = count_sheets(profile, args.prominence, args.min_gap)
        # Le rayon utile s'arrete ou il n'y a plus de matiere : compter au-dela
        # ajouterait du bruit de fond au nombre de feuilles.
        body = np.flatnonzero(smoothed > args.body_threshold)
        outer = int(body.max()) if body.size else 0
        counts.append(int((peaks <= outer).sum()) if outer else len(peaks))
        radii.append(outer)
        spacings.append(spacing)

    counts = np.asarray(counts)
    radii = np.asarray(radii)
    if counts.size == 0:
        print("erreur : aucun rayon exploitable", file=sys.stderr)
        return 3
    outer_mm = float(np.median(radii) * VOXEL_UM / 1000.0)
    turns = int(np.median(counts))
    length_m = spiral_length_mm(turns, outer_mm) / 1000.0

    print()
    print(f"rayons exploites           : {counts.size}")
    print(f"rayon exterieur du rouleau : {outer_mm:.1f} mm (median)")
    print(f"feuilles par rayon         : median {turns}  (min {counts.min()}, max {counts.max()})")
    print(f"dispersion                 : ecart-type/moyenne = {counts.std() / counts.mean():.2f}")
    print(f"espacement entre feuilles  : {np.nanmedian(spacings):.0f} um (median)")
    print()
    print(f"LONGUEUR estimee du papyrus : {length_m:.1f} m "
          f"(spirale de {turns} spires sur {outer_mm:.1f} mm de rayon)")
    print()
    print("⚠ borne SUPERIEURE : chaque feuille fondue a sa voisine est comptee une")
    print("   fois, donc le vrai nombre de spires est >= ce compte. Et une tranche")
    print("   unique ne dit rien de la variation le long du rouleau.")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "name": args.name, "slice": z, "rays": int(counts.size),
            "outer_radius_mm": outer_mm, "turns_median": turns,
            "turns_min": int(counts.min()), "turns_max": int(counts.max()),
            "spacing_um_median": float(np.nanmedian(spacings)),
            "length_m": length_m,
        }, indent=2) + "\n")
    return 0


def cmd_unwrap(args) -> int:
    centre = load_centre(args.name)
    array = open_volume(args.volume, args.level)
    z = args.slice if args.slice >= 0 else int((centre["z_min"] + centre["z_max"]) / 2)
    plane = array[z]
    polar = unwrap_polar(plane, centre["cx"], centre["cy"], args.reach, args.angular)
    np.save(args.out, polar)
    print(f"coupe {plane.shape} -> polaire {polar.shape}  (rayon x angle)")
    print(f"echantillonnage angulaire : {polar.shape[1]} colonnes "
          f"= {polar.shape[1] / 360.0:.1f} par degre")
    print(f"ecrit : {args.out}")
    if args.png:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        view = polar.astype(np.float32)
        lo, hi = np.quantile(view[view > 0], [0.02, 0.995]) if (view > 0).any() else (0, 1)
        grey = np.clip((view - lo) / max(hi - lo, 1e-6), 0, 1)
        Image.fromarray((255 * grey).astype(np.uint8)).save(args.png)
        print(f"apercu : {args.png}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="L'onde radiale : compter les feuilles, et deplier la coupe.",
        epilog="Le centre est DERIVE et verifie, jamais lu dans un fichier suppose juste.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("centre", help="deriver l'axe du rouleau depuis une trace")
    c.add_argument("name")
    c.add_argument("mesh", help="repertoire .tifxyz (ou un parent)")
    c.add_argument("--sample", type=int, default=15000)
    c.add_argument("--seed", type=int, default=0)
    c.set_defaults(func=cmd_centre)

    n = sub.add_parser("compter", help="onde radiale : feuilles, espacement, longueur")
    n.add_argument("name")
    n.add_argument("volume")
    n.add_argument("--level", default="0")
    n.add_argument("--slice", type=int, default=-1, help="-1 = milieu de la trace")
    n.add_argument("--reach", type=float, default=4500.0, help="portee du rayon, en voxels")
    n.add_argument("--step-deg", type=int, default=10)
    n.add_argument("--prominence", type=float, default=8.0)
    n.add_argument("--min-gap", type=int, default=10, help="ecart minimal entre deux murs, en voxels")
    n.add_argument("--body-threshold", type=float, default=12.0)
    n.add_argument("--json")
    n.set_defaults(func=cmd_count)

    u = sub.add_parser("deplier", help="coupe -> coordonnees polaires (spires = lignes)")
    u.add_argument("name")
    u.add_argument("volume")
    u.add_argument("out", help="sortie .npy")
    u.add_argument("--level", default="0")
    u.add_argument("--slice", type=int, default=-1)
    u.add_argument("--reach", type=float, default=3000.0)
    u.add_argument("--angular", type=int, default=None,
                   help="colonnes angulaires (defaut: la circonference exterieure)")
    u.add_argument("--png", help="apercu PNG")
    u.set_defaults(func=cmd_unwrap)

    args = parser.parse_args()
    try:
        return args.func(args)
    except RadialError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
