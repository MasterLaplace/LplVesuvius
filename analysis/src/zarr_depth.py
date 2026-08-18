#!/usr/bin/env python3
"""Profil de profondeur d'un segment, lu **a distance**, un chunk a la fois.

⚠⚠ **Ce fichier existe parce qu'une mesure etait hors de portee et ne l'est plus.**
`docs/12` etablit un instrument de qualite de trace -- la part des fenetres dont le pic
de contraste tombe pres de la surface tracee -- mais ne le valide que sur **trois**
segments, parce qu'une pile de couches `.tif` pese 32 Go et qu'une population en
demande une dizaine.

Le bucket ouvert publie les volumes de surface en **OME-Zarr**, et leur disposition
change tout :

    shape  [109, 21380, 115820]      chunks [109, 128, 128]      dtype u1, sans compression

**Un chunk contient TOUTE la colonne de profondeur d'une fenetre de 128 x 128.** C'est
exactement l'unite dont le profil a besoin, et elle coute **1,78 Mo** au lieu de 32 Go.
Mesure : 1,03 s par chunk. Une trentaine de fenetres par segment, une vingtaine de
segments, et la population devient une affaire de minutes.

⚠ **La surface tracee est au MILIEU de la pile** (`shape[0] // 2`), par construction du
volume de surface -- c'est la meme convention que les 65 couches `.tif` engendrees avec
`-r 32`, verifiee dans le tutoriel officiel (`docs/12` §1). Ici la pile fait 109
couches, donc la surface est la couche **54**.

⚠ **Un volume de surface est majoritairement du remplissage** : le segment est une
bande tordue dans un canevas rectangulaire. Les chunks vides sont **sautes et comptes**,
jamais credites d'un profil -- sans quoi la statistique porterait surtout sur du vide.

⚠ Deux conventions de profondeur coexistent dans le corpus (65 couches a 7,91 µm =
514 µm de profondeur, 109 couches a 2,4 µm = 262 µm). Les fractions se comparent
**dans une convention**, pas entre elles : `--layers` est rapporte a cote de chaque
chiffre pour que le melange se voie.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


def get(url: str, timeout: float) -> bytes | None:
    done = subprocess.run(["curl", "-s", "--fail", "--max-time", str(int(timeout)), url],
                          capture_output=True)
    return done.stdout if done.returncode == 0 else None


def array_meta(zarr_url: str, level: int, timeout: float) -> dict:
    raw = get(f"{zarr_url}/{level}/.zarray", timeout)
    if raw is None:
        raise RuntimeError(f"pas de .zarray au niveau {level} sous {zarr_url}")
    meta = json.loads(raw)
    if meta.get("compressor") is not None:
        raise RuntimeError("chunk compresse : ce lecteur lit du brut uniquement")
    return meta


def chunk_profile(zarr_url: str, level: int, meta: dict, cy: int, cx: int,
                  timeout: float):
    """Profils d'intensite et de contraste d'UN chunk, ou None s'il est vide/absent."""
    depth, hy, hx = meta["chunks"]
    raw = get(f"{zarr_url}/{level}/0/{cy}/{cx}", timeout)
    if raw is None or len(raw) != depth * hy * hx:
        return None
    block = np.frombuffer(raw, dtype=np.dtype(meta["dtype"])).reshape(depth, hy, hx)
    if block.max() == 0:
        return None
    patch = block.astype(np.float32)
    mean = patch.mean(axis=(1, 2))
    blur = (patch[:, :-2, 1:-1] + patch[:, 2:, 1:-1] + patch[:, 1:-1, :-2]
            + patch[:, 1:-1, 2:] + patch[:, 1:-1, 1:-1]) / 5.0
    contrast = (patch[:, 1:-1, 1:-1] - blur).std(axis=(1, 2))
    return mean, contrast


def survey(zarr_url: str, level: int, windows: int, timeout: float, seed: int) -> dict:
    meta = array_meta(zarr_url, level, timeout)
    depth, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    grid_y, grid_x = -(-rows // hy), -(-cols // hx)
    traced = depth // 2

    # ⚠ Balayage REGULIER et non aleatoire : deux runs du meme segment doivent rendre
    # le meme chiffre, sinon la comparaison entre segments melange le tirage et l'objet.
    steps = max(1, int(np.sqrt(windows)))
    picks = [(int(y), int(x))
             for y in np.linspace(0, grid_y - 1, steps)
             for x in np.linspace(0, grid_x - 1, min(steps * 2, grid_x))]

    peaks, contrast_peaks, empty, curves, dense = [], [], 0, [], []
    for cy, cx in picks:
        got = chunk_profile(zarr_url, level, meta, cy, cx, timeout)
        if got is None:
            empty += 1
            continue
        mean, contrast = got
        # ⚠⚠ Le pic retenu est celui de l'INTENSITE, pas du contraste. Le contraste
        # a ete l'instrument jusqu'a ce qu'on affiche sa courbe : sur un volume a
        # 2,4 µm il forme un U, maximal aux deux bords et minimal dans la feuille,
        # parce qu'il suit les interfaces et le bruit. L'intensite dit ou est la
        # matiere, et les deux ne s'accordent que sur les volumes grossiers.
        peaks.append(int(np.argmax(mean)))
        contrast_peaks.append(int(np.argmax(contrast)))
        # ⚠⚠ L'INTENSITE est rapportee a cote du contraste, et pas comme un detail :
        # elle dit sans ambiguite ou est la MATIERE, la ou le contraste dit ou sont les
        # variations -- et les deux ne coincident pas forcement. Sur un volume assez fin
        # pour resoudre les fibres, l'interieur d'une feuille est texture ; sur un volume
        # grossier il est lisse. Lire l'un pour l'autre est une erreur silencieuse.
        span_m = mean.max() - mean.min()
        if span_m > 0:
            dense.append((mean - mean.min()) / span_m)
        # ⚠ Chaque courbe est normalisee AVANT d'etre moyennee : sinon la moyenne est
        # celle des fenetres les plus contrastees, et la forme qu'on croit lire est
        # celle d'une poignee d'entre elles.
        span = contrast.max() - contrast.min()
        if span > 0:
            curves.append((contrast - contrast.min()) / span)
    if not peaks:
        raise RuntimeError("aucune fenetre avec de la matiere")

    peaks = np.asarray(peaks)
    low, high = depth // 3, 2 * depth // 3
    return {
        "zarr": zarr_url.rsplit("/", 1)[-1],
        "layers": int(depth),
        "traced_layer": int(traced),
        "sondees": len(picks), "avec_matiere": int(peaks.size), "vides": empty,
        "tiers_central": float(((peaks >= low) & (peaks < high)).mean()),
        "au_bord": float(((peaks == 0) | (peaks == depth - 1)).mean()),
        "pic_median": int(np.median(peaks)),
        "tiers_central_contraste": float(((np.asarray(contrast_peaks) >= low)
                                          & (np.asarray(contrast_peaks) < high)).mean()),
        "ecart_a_la_trace": float(np.median(np.abs(peaks - traced))),
        "iqr": float(np.percentile(peaks, 75) - np.percentile(peaks, 25)),
        "courbe_moyenne": [float(v) for v in np.mean(curves, axis=0)] if curves else [],
        "courbe_intensite": [float(v) for v in np.mean(dense, axis=0)] if dense else [],
        "pic_intensite": int(np.argmax(np.mean(dense, axis=0))) if dense else -1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profil de profondeur d'un segment, lu a distance chunk par chunk.",
        epilog="Un chunk = une colonne de profondeur entiere, pour 1,78 Mo.",
    )
    parser.add_argument("zarr", nargs="+", help="cles S3 des .zarr (sans le bucket)")
    parser.add_argument("--level", type=int, default=0)
    parser.add_argument("--windows", type=int, default=36)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--courbe", action="store_true",
                        help="afficher la courbe de contraste MOYENNE : une statistique "
                             "resumee se lit mal sans la forme qu'elle resume")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    report = []
    for key in args.zarr:
        url = key if key.startswith("http") else f"{BUCKET}/{key}"
        try:
            data = survey(url, args.level, args.windows, args.timeout, args.seed)
        except RuntimeError as error:
            print(f"{key.split('/')[2] if '/' in key else key} : {error}", file=sys.stderr)
            continue
        segment = key.split("/segments/")[1].split("/")[0] if "/segments/" in key else key
        data["segment"] = segment
        print(f"{segment[:38]:38} {data['layers']:>4} couches  "
              f"tiers central {data['tiers_central'] * 100:5.1f} %  "
              f"au bord {data['au_bord'] * 100:5.1f} %  "
              f"ecart median a la trace {data['ecart_a_la_trace']:5.1f}  "
              f"({data['avec_matiere']}/{data['sondees']} fenetres)", flush=True)
        if args.courbe and data["courbe_moyenne"]:
            courbe = np.asarray(data["courbe_moyenne"])
            dens = np.asarray(data["courbe_intensite"])
            print(f"    {'couche':>6} {'contraste':>10} {'intensite':>10}")
            for k in range(0, len(courbe), max(1, len(courbe) // 24)):
                mark = " <-- trace" if abs(k - data["traced_layer"]) < 2 else ""
                print(f"    {k:>6} {courbe[k]:>10.3f} {dens[k]:>10.3f}  "
                      f"{'#' * int(dens[k] * 34)}{mark}")
            print(f"    pic d'INTENSITE : couche {data['pic_intensite']} "
                  f"(surface tracee : {data['traced_layer']})")
        report.append(data)

    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\necrit : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
