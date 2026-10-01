"""The seeds a chain starts from: vertices of the segment's mesh, taken on a regular grid of rows and columns, with a known
normal, away from the edge (`R4-F531`: seeds 1 to 8 of PHercParis4).

Ported from `la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4.py` (slice `321`, `les_graines`) on the `experimental`
branch.
"""
from __future__ import annotations

import numpy as np

SEEDS = 8
EDGE = 8                    # mesh vertices kept between a seed and the edge of the mesh
DIVISIONS = range(3, 12)    # the grid is made finer until it holds enough seeds


def choose_seeds(valid: np.ndarray, has_normal: np.ndarray, count: int = SEEDS) -> list[tuple[int, int]]:
    """Valid vertices with a known normal, on a regular grid of rows and columns, taken in order and at least `EDGE` vertices from
    the edge of the mesh; as many as `count`, spread over the candidates. Empty if no grid holds `count` of them."""
    h, w = valid.shape
    usable = valid & has_normal
    inside = np.zeros_like(usable)
    inside[EDGE:-EDGE, EDGE:-EDGE] = True
    usable &= inside
    for divisions in DIVISIONS:
        rows = np.linspace(EDGE, h - EDGE - 1, divisions).round().astype(int)
        columns = np.linspace(EDGE, w - EDGE - 1, divisions).round().astype(int)
        candidates = [(int(r), int(c)) for r in rows for c in columns if usable[r, c]]
        if len(candidates) >= count:
            spacing = len(candidates) / count
            return [candidates[int(k * spacing)] for k in range(count)]
    return []
