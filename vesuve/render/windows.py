"""Choosing a window without looking at the ink: by papyrus coverage alone.

⚠⚠ Choosing the window where the ink looks strongest, then showing it as evidence, would select on the result:
any noise would make letters there. The window and the held-out region are therefore chosen on what does not
depend on the ink, the share of rendered papyrus, and the rule is written before seeing anything.
"""
from __future__ import annotations

import numpy as np


def _integral(mask: np.ndarray) -> np.ndarray:
    return np.pad(np.cumsum(np.cumsum(mask.astype(np.int64), axis=0), axis=1), ((1, 0), (1, 0)))


def best_window(mask: np.ndarray, side: int, step: int = 16, forbidden=None) -> dict | None:
    """The square window of `side` pixels most covered by papyrus, on a grid of `step`; the first in reading order
    (top, then left) on a tie. `forbidden`: a window this one must not overlap."""
    h, w = mask.shape
    if side > h or side > w:
        return None
    I = _integral(mask)
    best = None
    for r in range(0, h - side + 1, step):
        for c in range(0, w - side + 1, step):
            if forbidden is not None:
                ir, ic, ih, iw = forbidden["r0"], forbidden["c0"], forbidden["side"], forbidden["side"]
                if r < ir + ih and ir < r + side and c < ic + iw and ic < c + side:
                    continue
            n = int(I[r + side, c + side] - I[r, c + side] - I[r + side, c] + I[r, c])
            if best is None or n > best["papyrus"]:
                best = {"r0": r, "c0": c, "side": side, "papyrus": n}
    if best is not None:
        best["papyrus_share"] = round(best["papyrus"] / (side * side), 4)
    return best


def held_out_window(mask: np.ndarray, side: int, window: dict, step: int = 16) -> dict | None:
    """The best window of the same side that does not overlap the first; otherwise the largest that fits, and
    that is said (`side_reduced`)."""
    for c in range(side, 63, -64):
        x = best_window(mask, c, step, forbidden=window)
        if x is not None and x["papyrus_share"] >= 0.5:
            x["side_reduced"] = c != side
            return x
    return None
