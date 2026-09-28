"""The window-to-window steps of a block: what the walk of the correction reads from a rendered pile.

A step across a seam is read in short windows chained from the centre of one chunk to the centre of its neighbour:
each window is the mean profile, layer by layer, of 16 columns, and each step between two windows is the shift that
best aligns them, refined by a parabola at the top of the correlation. Short steps see the drift that a step read
at the seam alone misses (`260`, fact `R4-F439`).

A step depends only on the two chunks of its seam, so it is computed ONCE per block: the table of a block holds the
steps of every seam that LEAVES one of its chunks, those inside and, when the neighbour is rendered, those that cross
to the east and to the south. The walk of a neighbourhood is then assembled from the tables of its blocks.

Ported from `le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.py` (`le_pas_fin`, `les_fenetres`, `la_somme_des_pas`) and
`la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py` (`les_pas_dun_bloc`) on the `experimental` branch,
expression for expression: NumPy receives the same operations in the same order, so the tables are the research's
to the last bit.
"""
from __future__ import annotations

import numpy as np

from vesuve import core

CHUNK = 128
BLOCK = 16
WINDOW = 16            # the edge width of `199`, derived and published
HALF_SHEET = 36        # the search range of a step, in voxels
CUT_COUNT = 16
COHERENCE_FLOOR = 0.15
EMPTY, TOO_LITTLE_TEXTURE, OUTSIDE = "empty", "too little texture", "outside the render"


def cuts(side: int = CHUNK, count: int = CUT_COUNT) -> list[int]:
    """The cut rows, spread UNIFORMLY over the chunk: the i-th in the middle of the i-th equal slice, none on an edge."""
    n = max(1, int(count))
    return [int(side) * (2 * i + 1) // (2 * n) for i in range(n)]


def fine_step(a: np.ndarray, b: np.ndarray, reach: int = HALF_SHEET) -> float | None:
    """The shift that aligns `b` on `a`, with the sign of `199`, refined by the parabola at the top of the correlation.

    The correlation is normalised by the energy of the two overlapping windows; None when either has no energy.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    a, b = a - a.mean(), b - b.mean()
    if float(np.dot(a, a)) <= 0.0 or float(np.dot(b, b)) <= 0.0:
        return None
    p = int(min(int(reach), (len(a) - 1) // 2))
    if p < 1:
        return None
    scores = []
    for k in range(-p, p + 1):
        aa = a[max(0, k):len(a) + min(0, k)]
        bb = b[max(0, -k):len(b) + min(0, -k)]
        e = float(np.dot(aa, aa)) * float(np.dot(bb, bb))
        scores.append(float(np.dot(aa, bb)) / (e ** 0.5) if e > 0.0 else -1.0)
    i = int(np.argmax(scores))
    d = 0.0
    if 0 < i < len(scores) - 1:
        y0, y1, y2 = scores[i - 1], scores[i], scores[i + 1]
        den = y0 - 2.0 * y1 + y2
        if den < 0.0:
            d = 0.5 * (y0 - y2) / den
    return -((i + d) - p)


def windows(section: np.ndarray, width: int = WINDOW) -> np.ndarray:
    """The profiles of each window of `width` columns of a cut (layer, column): (layer, window)."""
    n = section.shape[1] // width
    return np.asarray(section[:, :n * width], dtype=float).reshape(section.shape[0], n, width).mean(axis=2)


def chained_step(fa: np.ndarray, fb: np.ndarray) -> float | None:
    """The sum of the window-to-window steps, from the central window of `fa` to that of `fb`, across the seam."""
    f = np.concatenate([fa, fb], axis=1)
    n = fa.shape[1]
    start, end = n // 2, n + n // 2
    total = 0.0
    for j in range(start, end):
        x = fine_step(f[:, j], f[:, j + 1])
        if x is None:
            return None
        total += x
    return total


def kept_chunk(block) -> tuple[np.ndarray | None, str | None]:
    """A chunk passed through the producer's filter, or the reason it is refused: empty, or too little texture."""
    if block is None:
        return None, OUTSIDE
    b = np.asarray(block)
    if float(b.max()) <= 0.0:
        return None, EMPTY
    _, kept = core.texture_filter(b, COHERENCE_FLOOR)
    if not kept:
        return None, TOO_LITTLE_TEXTURE
    return b, None


def chunk_reader(piles: dict[tuple[int, int], np.ndarray], side: int = BLOCK, chunk: int = CHUNK):
    """A reader of chunks over several rendered piles, each of a block aligned on the block step."""
    def read(cy: int, cx: int):
        key = (int(cy) // side * side, int(cx) // side * side)
        p = piles.get(key)
        if p is None:
            return None
        y, x = int(cy) - key[0], int(cx) - key[1]
        b = p[:, y * chunk:(y + 1) * chunk, x * chunk:(x + 1) * chunk]
        return b if b.shape[1:] == (chunk, chunk) else None
    return read


def block_table(read, by: int, bx: int, east: bool, south: bool, side: int = BLOCK,
                count: int = CUT_COUNT) -> dict:
    """The steps of every seam that LEAVES a chunk of the block: those inside and, if the neighbour is rendered, those
    that cross to the east and to the south. The seams to the west and to the north leave the neighbour, which holds
    them.

    Each step is `[mean over the cuts, even cuts minus odd cuts, cuts read]`; a seam with fewer than two cuts read is
    left out.
    """
    rows = cuts(CHUNK, count)
    to_read = [(r, c) for r in range(by, by + side) for c in range(bx, bx + side)]
    to_read += [(r, bx + side) for r in range(by, by + side)] if east else []
    to_read += [(by + side, c) for c in range(bx, bx + side)] if south else []
    wins, refused = {}, {}
    for r, c in to_read:
        b, why = kept_chunk(read(r, c))
        if b is None:
            refused[why] = refused.get(why, 0) + 1
            continue
        b = np.asarray(b, dtype=float)
        wins[(r, c)] = ({int(k): windows(b[:, int(k), :]) for k in rows},
                        {int(k): windows(b[:, :, int(k)]) for k in rows})
    h, v = {}, {}
    for r in range(by, by + side):
        for c in range(bx, bx + side):
            if (r, c) not in wins:
                continue
            along_rows, along_columns = wins[(r, c)]
            for direction, neighbour, mine, d in (("h", (r, c + 1), along_rows, h), ("v", (r + 1, c), along_columns, v)):
                if neighbour not in wins:
                    continue
                other = wins[neighbour][0 if direction == "h" else 1]
                sums = [chained_step(mine[k], other[k]) for k in rows]
                sums = [x for x in sums if x is not None]
                if len(sums) < 2:
                    continue
                d[f"{r}_{c}"] = [float(np.mean(sums)), float(np.mean(sums[0::2]) - np.mean(sums[1::2])), len(sums)]
    return {"row": by, "column": bx, "east": bool(east), "south": bool(south), "h": h, "v": v,
            "kept_chunks": sum(1 for (r, c) in wins if by <= r < by + side and bx <= c < bx + side),
            "refused": refused}
