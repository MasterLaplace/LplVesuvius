#!/usr/bin/env python3
"""Peut-on distinguer deux feuilles voisines ? — une métrique de qualité de scan.

⚠⚠ **Nommée par les organisateurs comme ce qui manque.** Le tableau des goulots de
`2026_open_problems` dit, pour les régions comprimées : *« What would help : **scan-
quality metrics**, and scroll-specific acquisition recipes »*. Et il définit le défaut
dans ses propres mots : *« Some regions lose **effective separability** between
layers »*.

**Ce n'est PAS un problème de géométrie**, et c'est ce que la page a corrigé dans notre
lecture. Une région « comprimée » n'est pas une région où les spires sont serrées : les
fibres carbonisées sont proches du graphite, qui **décohère** le front d'onde X, et le
résultat est un **voile**. Les feuilles s'y devinent derrière la brume. Notre carte
géométrique (`16`) mesure autre chose — utile pour écarter une cause, pas pour répondre
à celle-ci.

**La mesure : un d′, l'indice de discriminabilité.** Le long d'une ligne qui traverse
les spires, l'intensité alterne feuille / interstice. La question « peut-on les
distinguer » est exactement celle qu'un d′ pose :

    d′ = (moyenne des sommets − moyenne des creux) / racine((var_sommets + var_creux)/2)

⚠ **Sans dimension, donc comparable entre campagnes de scan** — c'est toute la raison de
ce choix. Un simple écart d'intensité dépendrait du gain du détecteur et comparerait les
scanners au lieu des rouleaux.

⚠ **Les sommets et les creux sont trouvés dans le signal lui-même**, pas dans la
prédiction de surface : la faire servir d'étiqueteuse confondrait « le scan est voilé »
avec « la prédiction est mauvaise », qui sont les deux choses qu'on veut départager.

⚠ Un lissage léger précède la recherche d'extrema, sinon le bruit du détecteur fournit
un extremum tous les deux voxels et le d′ mesure le bruit.

⚠⚠ **CE QUE CE d′ NE PEUT PAS FAIRE : comparer deux RESOLUTIONS.** Mesuré sur le même
rouleau (PHerc0139), paramètres dérivés du pas physique dans les deux cas :

    9,362 µm natif  → d′ 1,45      2,399 µm natif → d′ 1,24

Le scan **fin** rend un d′ **plus bas**, et ce n'est pas qu'il est moins bon. À 2,4 µm
l'intérieur d'une feuille est **résolu** — fibres, lumens — donc la variance à
l'intérieur d'un sommet augmente, et elle est au **dénominateur** d'un d′. Résoudre plus
de structure abaisse mécaniquement l'indice.

**Cette métrique compare des scans À RÉSOLUTION ET PROTOCOLE ÉGAUX**, ce qui est
exactement le cas des 13 rouleaux du Grand Prize (8,640–9,362 µm, 1,2 m, 110–116 keV) et
du témoin PHerc0139 qui partage ce protocole. Elle ne dit **rien** sur « faut-il scanner
plus fin », et le prétendre serait lire un artefact d'échelle comme un résultat.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402


def smooth(line: np.ndarray, width: int) -> np.ndarray:
    if width <= 1:
        return line
    kernel = np.ones(width, dtype=np.float32) / width
    return np.convolve(line, kernel, mode="same")


def separability(line: np.ndarray, width: int, min_gap: int) -> float:
    """d′ entre les sommets et les creux d'une ligne traversant les spires.

    ⚠ Rend NaN plutot qu'un chiffre quand il y a moins de trois alternances : un d′
    calcule sur deux points est un rapport de deux nombres, pas une mesure.
    """
    soft = smooth(line.astype(np.float32), width)
    if soft.size < 4 * min_gap:
        return float("nan")
    up = np.flatnonzero((soft[1:-1] > soft[:-2]) & (soft[1:-1] >= soft[2:])) + 1
    down = np.flatnonzero((soft[1:-1] < soft[:-2]) & (soft[1:-1] <= soft[2:])) + 1
    # ⚠ On garde les extrema SEPARES d'au moins `min_gap` : sans ca, un plateau bruite
    # fournit une grappe d'extrema voisins qui sont le meme evenement compte dix fois.
    def thin(idx):
        kept = []
        for i in idx:
            if not kept or i - kept[-1] >= min_gap:
                kept.append(int(i))
        return np.asarray(kept, dtype=int)

    up, down = thin(up), thin(down)
    if up.size < 3 or down.size < 3:
        return float("nan")
    peaks, troughs = line[up].astype(np.float32), line[down].astype(np.float32)
    spread = np.sqrt((peaks.var() + troughs.var()) / 2.0)
    if spread <= 0:
        return float("nan")
    return float((peaks.mean() - troughs.mean()) / spread)


def survey_chunk(block: np.ndarray, width: int, min_gap: int, sample: int = 20) -> float:
    """d′ median d'un chunk, direction la plus perpendiculaire aux feuilles.

    ⚠ Meme raison que pour l'ecart entre spires (`16`) : une ligne oblique traverse les
    feuilles plus lentement, donc voit des transitions plus douces et un d′ plus BAS.
    Garder le MAXIMUM des deux directions donne celle qui est le plus proche de la
    normale -- c'est-a-dire la mesure la moins pessimiste, et donc celle qui ne peut pas
    faire passer une geometrie oblique pour un voile.
    """
    mid = block.shape[0] // 2
    plane = block[mid]
    rows = np.linspace(2, plane.shape[0] - 3, sample).astype(int)
    cols = np.linspace(2, plane.shape[1] - 3, sample).astype(int)
    along_x = [separability(plane[r], width, min_gap) for r in rows]
    along_y = [separability(plane[:, c], width, min_gap) for c in cols]
    got = [np.nanmedian(a) for a in (along_x, along_y)
           if np.isfinite(a).sum() >= sample // 3]
    got = [g for g in got if np.isfinite(g)]
    return float(max(got)) if got else float("nan")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Separabilite des feuilles : une metrique de qualite de scan.",
        epilog="Un d′ est sans dimension, donc comparable entre campagnes de scan.",
    )
    parser.add_argument("zarr", help="cle S3 du volume CT (pas la prediction)")
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--voxel-um", type=float, default=9.362)
    parser.add_argument("--chunks", type=int, default=27)
    parser.add_argument("--sheet-pitch-um", type=float, default=170.0,
                        help="pas inter-feuilles en µm. Le lissage et l'ecart minimal "
                             "entre extrema en DERIVENT : ce sont des longueurs, donc "
                             "les figer en voxels ferait mesurer deux choses "
                             "differentes a deux resolutions")
    parser.add_argument("--smooth", type=int, default=0, help="0 = derive du pas")
    parser.add_argument("--min-gap", type=int, default=0, help="0 = derive du pas")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    url = args.zarr if args.zarr.startswith("http") else f"{BUCKET}/{args.zarr}"
    try:
        meta = array_meta(url, args.level, args.timeout)
    except RuntimeError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2
    depth, hy, hx = meta["chunks"]
    zs, rows, cols = meta["shape"]
    grid = (-(-zs // depth), -(-rows // hy), -(-cols // hx))
    voxel = args.voxel_um * (2 ** args.level)
    name = args.zarr.split("/")[0]
    # ⚠⚠ LE PIEGE DU RAYON DE RECHERCHE, REPAYE. Avec `--min-gap 3` fixe, la mesure
    # rendait d′ ≈ 1,7 a 18,7 µm et d′ ≈ 1,0 a 2,4 µm sur le MEME rouleau -- non parce
    # que le scan fin est moins bon, mais parce qu'a 2,4 µm une feuille fait 70 voxels
    # et sa TEXTURE DE FIBRES fournit un extremum tous les 4 a 8 voxels. Le detecteur
    # comptait donc des fibres au lieu de feuilles. Un d′ est sans dimension, mais ses
    # PARAMETRES sont des longueurs, et c'est la que l'echelle rentre.
    pitch_vox = args.sheet_pitch_um / voxel
    if args.min_gap <= 0:
        args.min_gap = max(2, int(round(pitch_vox / 4)))
    if args.smooth <= 0:
        args.smooth = max(1, int(round(pitch_vox / 8)))
    print(f"{name} niveau {args.level} : grille {grid}, voxel {voxel:.1f} µm")
    print(f"  pas suppose {args.sheet_pitch_um:.0f} µm = {pitch_vox:.1f} voxels "
          f"-> lissage {args.smooth}, ecart minimal {args.min_gap}")

    steps = max(2, int(round(args.chunks ** (1 / 3))) + 1)
    picks = sorted({(int(z), int(y), int(x))
                    for z in np.linspace(grid[0] * 0.25, grid[0] * 0.75, max(2, steps - 1))
                    for y in np.linspace(0, grid[1] - 1, steps + 2)
                    for x in np.linspace(0, grid[2] - 1, steps + 2)})

    values, absent = [], 0
    for cz, cy, cx in picks:
        raw = get(f"{url}/{chunk_key(meta, args.level, cy, cx, cz)}", args.timeout)
        if raw is None:
            absent += 1
            continue
        data = decode(raw, meta, depth * hy * hx)
        if data is None:
            absent += 1
            continue
        block = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(depth, hy, hx)
        if block.max() == 0:
            absent += 1
            continue
        value = survey_chunk(block, args.smooth, args.min_gap)
        if np.isfinite(value):
            values.append(value)
    print(f"  {len(values)} chunks mesures sur {len(picks)} sondes ({absent} vides)")
    if len(values) < 3:
        print("erreur : trop peu de chunks exploitables", file=sys.stderr)
        return 3

    values = np.asarray(values)
    report = {"zarr": args.zarr, "level": args.level, "voxel_um": voxel,
              "chunks": int(values.size),
              "d_prime_median": float(np.median(values)),
              "d_prime_p10": float(np.percentile(values, 10)),
              "d_prime_min": float(values.min()),
              "part_sous_1": float((values < 1.0).mean()),
              # ⚠⚠ LES VALEURS PAR FENETRE, et pas seulement leur resume. `64` §1 etablit
              # qu'un resume sans sa dispersion ne peut pas ETABLIR une difference : il y
              # faut 27 tuiles par fragment pour l'ecart observe, et on en avait 10. Sans
              # cette liste, comparer deux medianes de d′ -- ce que H2 fait entre deux
              # echantillonnages -- serait publier un ecart sans intervalle.
              # ⚠ Ajout ADDITIF : les lecteurs existants de `carte_separabilite/` lisent des
              # clefs nommees et ignorent celle-ci.
              "valeurs": [float(x) for x in values]}
    print(f"  d′ median {report['d_prime_median']:.2f}   "
          f"p10 {report['d_prime_p10']:.2f}   min {report['d_prime_min']:.2f}   "
          f"part sous 1,0 : {report['part_sous_1'] * 100:.0f} %")
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"  ecrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
