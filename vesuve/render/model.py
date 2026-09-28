"""The model's ink: the 2023 Grand Prize TimeSformer, swept over a stack of 26 layers (optional).

Port of `src/xpu/infer_ink.py` on the `experimental` branch (`load_layer_stack`, `fenetres_avec_matiere`,
`infer`). Three rules kept, each one paid for by the research:

- the stack is normalised by the maximum of ITS type (a hard-coded `/ 65535` divided a uint8 stack 257 times too
  much, and the model returned a constant on black);
- a window without a single non-zero voxel is skipped, and its pixels stay uncovered (NaN): "no papyrus" and "no
  ink" stop being the same value;
- the edges never swept are NaN, never zero.

⚠ At the regime of the thirteen scrolls, the published model does not separate the sheet from the void
(`R1-F20`): its output there is a view, not evidence, and the pipeline says so next to each map.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import tifffile

from vesuve.render.layers import layer_files

TILE, LAYERS = 64, 26
MINIMUM_FULL_SCALE = 1.0 / 64.0


class InkUnavailable(RuntimeError):
    """torch or the model is missing here: the model's ink cannot be computed, and that is said."""


def ink_stack(folder: Path, start: int, window, step: int = 1) -> np.ndarray:
    """26 layers `start + i × step` over `(r0, c0, h, w)`, as float32 normalised by the stack's type."""
    fs = {int(re.search(r"(\d+)", p.stem).group(1)): p for p in layer_files(folder)}
    r0, c0, h, w = window
    out = np.zeros((LAYERS, h, w), dtype=np.float32)
    kind = None
    for i in range(LAYERS):
        n = start + i * step
        if n not in fs:
            raise InkUnavailable(f"layer {n} missing from {folder}")
        a = tifffile.imread(fs[n])
        if kind is not None and a.dtype != kind:
            raise InkUnavailable(f"layer {n} is {a.dtype}, the stack is {kind}")
        kind = a.dtype
        out[i] = a[r0:r0 + h, c0:c0 + w].astype(np.float32)
    out /= float(np.iinfo(kind).max)
    if float(out.max()) < MINIMUM_FULL_SCALE:
        raise InkUnavailable(f"stack almost black (max {out.max():.4g}): the model would return a constant")
    return out


def load(model_folder: Path):
    try:
        import torch  # noqa: F401
        from transformers import AutoModel
    except ImportError as e:
        raise InkUnavailable(f"{e.name} is missing: `uv sync --extra ink`") from e
    if not (Path(model_folder) / "config.json").exists():
        raise InkUnavailable(f"no model under {model_folder}")
    return AutoModel.from_pretrained(str(model_folder), trust_remote_code=True).eval()


def infer(stack_: np.ndarray, model, step: int = 21, batch: int = 4, threads: int = 16) -> tuple[np.ndarray, int]:
    """(the ink map in logits, NaN outside what is seen; the number of windows swept)."""
    import torch
    import torch.nn.functional as F
    torch.set_num_threads(threads)
    _, h, w = stack_.shape
    if h < TILE or w < TILE:
        raise InkUnavailable(f"window {h}×{w} smaller than the tile {TILE}")
    ink, coverage = np.zeros((h, w), dtype=np.float32), np.zeros((h, w), dtype=np.float32)
    positions = [(y, x) for y in range(0, h - TILE + 1, step) for x in range(0, w - TILE + 1, step)
                 if stack_[:, y:y + TILE, x:x + TILE].any()]
    with torch.no_grad():
        for first in range(0, len(positions), batch):
            part = positions[first:first + batch]
            x_ = torch.from_numpy(np.stack([stack_[:, y:y + TILE, x:x + TILE] for y, x in part])).unsqueeze(1)
            output = F.interpolate(model(x_).float(), scale_factor=16, mode="bilinear").squeeze(1).numpy()
            for (y, x), tile in zip(part, output):
                ink[y:y + TILE, x:x + TILE] += tile
                coverage[y:y + TILE, x:x + TILE] += 1.0
    ink /= np.clip(coverage, 1.0, None)
    ink[coverage == 0] = np.nan
    return ink, len(positions)
