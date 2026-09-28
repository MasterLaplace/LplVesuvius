"""A stack of layers rendered around a surface (`NN.tif`), and the views drawn from it."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import tifffile


def layer_files(folder: Path) -> list[Path]:
    """The `.tif` of a stack, sorted by their NUMBER: `10.tif` comes after `9.tif`."""
    fs = [p for p in Path(folder).glob("*.tif") if re.search(r"\d+", p.stem)]
    if not fs:
        raise FileNotFoundError(f"no NN.tif layer in {folder}")
    return sorted(fs, key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))


def layer(path: Path, window=None) -> np.ndarray:
    """One layer, whole or restricted to `(r0, c0, rows, columns)`, memory-mapped when possible."""
    try:
        a = tifffile.memmap(path)
    except (ValueError, OSError):  # compressed: it has to be decoded whole
        a = tifffile.imread(path)
    if window is None:
        return np.asarray(a)
    r0, c0, h, w = window
    return np.asarray(a[r0:r0 + h, c0:c0 + w])


def stack(folder: Path, window=None, indices=None) -> np.ndarray:
    fs = layer_files(folder)
    chosen = fs if indices is None else [fs[i] for i in indices]
    return np.stack([layer(f, window) for f in chosen])


def papyrus(one_layer: np.ndarray) -> np.ndarray:
    """What is rendered: a render sets 0 outside the surface (`typographie.py:87`)."""
    return np.asarray(one_layer) > 0


def maximum_projection(layers: np.ndarray) -> np.ndarray:
    """The maximum along depth: "ink visible in the flattened render, with no model, often bright areas" (the
    First Letters rule). It is not a detector; it is a view."""
    return np.asarray(layers).max(axis=0)
