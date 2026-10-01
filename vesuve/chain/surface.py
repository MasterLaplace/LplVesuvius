"""A surface of the chain: its points on a regular grid, and which of them are laid."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

ReadValues = Callable[[np.ndarray], np.ndarray]
"""Reads the prediction at integer indices of shape (..., 3), in (z, y, x), and returns an array of the leading shape.
A sample is a sheet where it is above zero."""


@dataclass(frozen=True)
class Surface:
    points: np.ndarray   # (h, w, 3) voxels, in (x, y, z)
    valid: np.ndarray    # (h, w): the points that are laid


def to_prediction_indices(points: np.ndarray) -> np.ndarray:
    """The (z, y, x) integer indices of points given in (x, y, z)."""
    return np.floor(points[..., ::-1]).astype(np.int64)
