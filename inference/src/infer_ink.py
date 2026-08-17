#!/usr/bin/env python3
"""Detection d'encre par fenetre glissante, sur CPU, a partir des couches publiees.

Reprend EXACTEMENT la convention d'accumulation de la soumission gagnante 2023 :
la sortie 4x4 du modele est remontee en 64x64 par interpolation bilineaire, cumulee
dans une carte, avec un compteur de recouvrement, puis divisee. Toute autre
convention produirait une carte qui n'est comparable a rien de publie.

Le pas de balayage est un PARAMETRE et non une constante, parce que c'est le seul
reglage qui echange du temps contre de la resolution : la reference utilise
tile_size // 3 = 21, une variante publiee utilise 32, et l'ecart entre les deux
n'est chiffre nulle part.

Ne demande aucun GPU.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import tifffile
import torch
import torch.nn.functional as F

TILE = 64
"""Cote de la fenetre, impose par le modele (`window_size` de sa config)."""

FRAMES = 26
"""Nombre de couches attendu par le modele (`num_frames`)."""


class InferenceError(RuntimeError):
    """Leve quand une precondition n'est pas tenue."""


def load_layer_stack(layers_dir: Path, start: int, crop: tuple[int, int, int, int]) -> np.ndarray:
    """Charge FRAMES couches consecutives sur une fenetre, en (frames, h, w).

    Les couches sont lues par fenetre et non en entier : une couche fait 6655 x
    35653 en uint16, soit 474 Mo, donc les 26 tiendraient 12 Go pour une region
    qui en demande quelques dizaines de mebioctets.
    """
    top, left, height, width = crop
    stack = np.zeros((FRAMES, height, width), dtype=np.float32)
    for index in range(FRAMES):
        path = layers_dir / f"{start + index:02d}.tif"
        if not path.is_file():
            raise InferenceError(f"couche absente : {path}")
        with tifffile.TiffFile(path) as handle:
            page = handle.pages[0]
            full = page.asarray()
            stack[index] = full[top : top + height, left : left + width].astype(np.float32)
            del full
    # Le modele a ete entraine sur des entrees normalisees a [0, 1] depuis du
    # uint16 ; garder l'echelle brute donnerait des activations hors domaine.
    return stack / 65535.0


def infer(
    stack: np.ndarray,
    model,
    stride: int,
    batch_size: int,
    threads: int,
    device: str = "cpu",
) -> tuple[np.ndarray, int, float]:
    """Balaie la fenetre et rend (carte d'encre, nombre de fenetres, secondes).

    Le peripherique est un parametre : l'iGPU Arc rend le meme resultat que le CPU
    a 4.9e-6 pres (bruit fp32, verifie) pour 4.5 fois moins de temps. La
    synchronisation explicite avant de chronometrer n'est pas cosmetique -- sans
    elle on mesure le temps de mise en file, pas celui du calcul.
    """
    torch.set_num_threads(threads)
    _, height, width = stack.shape
    if height < TILE or width < TILE:
        raise InferenceError(f"fenetre {height}x{width} plus petite que la tuile {TILE}")

    prediction = np.zeros((height, width), dtype=np.float32)
    overlap = np.zeros((height, width), dtype=np.float32)

    positions = [
        (y, x)
        for y in range(0, height - TILE + 1, stride)
        for x in range(0, width - TILE + 1, stride)
    ]

    if device == "xpu":
        torch.xpu.synchronize()
    started = time.perf_counter()
    with torch.no_grad():
        for begin in range(0, len(positions), batch_size):
            chunk = positions[begin : begin + batch_size]
            batch = np.stack([stack[:, y : y + TILE, x : x + TILE] for y, x in chunk])
            tensor = torch.from_numpy(batch).unsqueeze(1).to(device)
            output = model(tensor)
            upscaled = (
                F.interpolate(output.float(), scale_factor=16, mode="bilinear")
                .squeeze(1)
                .cpu()
                .numpy()
            )
            for (y, x), tile in zip(chunk, upscaled):
                prediction[y : y + TILE, x : x + TILE] += tile
                overlap[y : y + TILE, x : x + TILE] += 1.0
    if device == "xpu":
        torch.xpu.synchronize()
    elapsed = time.perf_counter() - started

    prediction /= np.clip(overlap, 1.0, None)
    # Les bords que le balayage n'atteint jamais restent a zero et sont ecartes :
    # une moyenne qui les inclurait melangerait « pas d'encre » et « pas regarde ».
    prediction[overlap == 0] = np.nan
    return prediction, len(positions), elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detection d'encre CPU sur une region, a partir des couches rendues.",
    )
    parser.add_argument("layers", type=Path, help="repertoire contenant NN.tif")
    parser.add_argument("--model", type=Path, required=True, help="repertoire du modele")
    parser.add_argument("--start-layer", type=int, default=15, help="premiere couche (defaut: 15)")
    parser.add_argument("--top", type=int, required=True)
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--stride", type=int, default=21, help="pas de balayage (defaut: 21)")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--device", default="cpu", choices=("cpu", "xpu"))
    parser.add_argument("--out", type=Path, required=True, help="sortie .npy")
    args = parser.parse_args()

    from transformers import AutoModel

    try:
        stack = load_layer_stack(
            args.layers, args.start_layer, (args.top, args.left, args.height, args.width)
        )
    except InferenceError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    model = AutoModel.from_pretrained(str(args.model), trust_remote_code=True).eval()
    model = model.to(args.device)
    prediction, windows, elapsed = infer(
        stack, model, args.stride, args.batch_size, args.threads, args.device
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.out, prediction)
    covered = np.isfinite(prediction)
    print(f"pas de balayage   : {args.stride}")
    print(f"fenetres          : {windows}")
    print(f"duree             : {elapsed:.1f} s  ({elapsed / max(windows, 1) * 1000:.0f} ms/fenetre)")
    print(f"pixels couverts   : {int(covered.sum())} / {prediction.size}")
    print(f"encre  min/med/max: {np.nanmin(prediction):.3f} / "
          f"{np.nanmedian(prediction):.3f} / {np.nanmax(prediction):.3f}")
    print(f"sortie            : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
