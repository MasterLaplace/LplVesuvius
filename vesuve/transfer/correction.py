"""Correct the transfer from one winding to the next, without a judge.

A chain that transfers a surface to the next winding gets most points right and some on the wrong winding. The
procedure of `265`, run on the whole segment by `275`, finds those without ground truth:

1. the lattice walk (least squares on the window-to-window steps) gives the depth of the sheet in every chunk,
   once on the reference surface and once on the produced winding;
2. their difference, anchored on the median of the neighbouring blocks (the block itself left out), is where the
   produced winding departs from the reference;
3. a three-component mixture (the noise at 0, and a slip of one winding above and below, same width) is fitted to
   that departure by EM, and a point is corrected when a slip explains it better than the noise.

The judge (two hand-checked tracings of the next winding) only SCORES the result: it never takes part in a
decision. Ported from `la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py` on the `experimental` branch and
the files it imports (`la_spire_produite_se_lit_elle_dans_le_treillis.py`, `le_voisinage_dit_il_quel_niveau_est_le_bon.py`,
`la_marche_corrige_t_elle_la_spire_produite.py`, `la_marche_sait_elle_ou_ne_pas_corriger.py`), expression for
expression: the least squares receive their equations in the same order, so they return the same numbers.
"""
from __future__ import annotations

from math import comb

import numpy as np

HALF_SHEET = 36     # half the sheet-to-sheet step in voxels, round(173 / 2.4 / 2) (`R4-F14`)
BLOCK = 16          # chunks per side of a block
CHUNK = 128         # voxels per side of a chunk
MESH = 8            # a point of the transfer every 8 grid cells
GRID_STEP = 20      # voxels per grid cell of a tifxyz surface
ITERATIONS = 500    # EM iterations at most (`264`)
COUNTS = ("corrected_points", "misses_made_right", "rights_made_misses")


def neighbours(by: int, bx: int, candidates, side: int = BLOCK) -> list[tuple[int, int]]:
    """The blocks to the north, south, west and east, one block away, when they are candidates."""
    return [v for v in ((by - side, bx), (by + side, bx), (by, bx - side), (by, bx + side)) if v in candidates]


def neighbourhood_axes(by: int, bx: int, candidates, side: int = BLOCK) -> tuple[bool, bool]:
    """Whether the block has a candidate neighbour along the columns (north or south), and along the rows (west or east)."""
    return (((by - side, bx) in candidates or (by + side, bx) in candidates),
            ((by, bx - side) in candidates or (by, bx + side) in candidates))


def within_validated_geometry(by: int, bx: int, candidates, side: int = BLOCK) -> bool:
    """The geometry the correction was validated under: neighbours along BOTH axes.

    ⚠ This is where the research measured the correction to fail, not a preference. With east-west neighbours only,
    the same procedure on the same segment corrects 1047 points instead of 495 and its net gain falls from 122 to 5
    (`291`, `R4-F472`); the anchor carries the loss (`292`, `R4-F473`); on the band `w028-037`, one row of blocks, it
    gives 15 misses made right for 25 rights made misses (`281`, `R4-F462`), which chance explains (`R4-F471`).
    """
    return all(neighbourhood_axes(by, bx, candidates, side))


def block_depth(h: dict, v: dict, by: int, bx: int, side: int) -> dict:
    """The depth of the sheet in each chunk of a square, by least squares on the steps, with zero mean.

    `h[r][c]` is the depth of (r, c+1) minus that of (r, c); `v[r][c]`, that of (r+1, c) minus that of (r, c). Only the
    seams whose two chunks are in the square count, and only the largest connected set of chunks is solved: a chunk no
    seam links to it has no depth (NaN).
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse.linalg import lsqr

    def index(r, c):
        return (r - by) * side + (c - bx)

    def inside(r, c):
        return by <= r < by + side and bx <= c < bx + side

    rows, cols, vals, b, edges = [], [], [], [], []
    for direction, d in (("h", h), ("v", v)):
        for r, line in d.items():
            for c, x in line.items():
                r, c = int(r), int(c)
                r2, c2 = (r, c + 1) if direction == "h" else (r + 1, c)
                if not (inside(r, c) and inside(r2, c2)):
                    continue
                k = len(b)
                rows += [k, k]
                cols += [index(r2, c2), index(r, c)]
                vals += [1.0, -1.0]
                b.append(float(x))
                edges.append((index(r, c), index(r2, c2)))
    n = side * side
    depth = np.full((side, side), np.nan)
    if not b:
        return {"depth": depth, "seams": 0, "rms_residual": None, "linked_chunks": 0}
    g = coo_matrix((np.ones(len(edges)), ([a for a, _ in edges], [z for _, z in edges])), shape=(n, n))
    _, label = connected_components(g, directed=False)
    touched = np.zeros(n, dtype=bool)
    for a, z in edges:
        touched[a] = touched[z] = True
    counts = np.bincount(label[touched], minlength=label.max() + 1)
    kept = touched & (label == int(np.argmax(counts)))
    A = coo_matrix((vals, (rows, cols)), shape=(len(b), n)).tocsr()
    selected = np.array([kept[a] and kept[z] for a, z in edges])
    A2, b2 = A[selected][:, kept], np.array(b)[selected]
    x = lsqr(A2, b2, atol=1e-10, btol=1e-10)[0]
    x = x - x.mean()
    depth.ravel()[np.nonzero(kept)[0]] = x
    residual = A2 @ x - b2
    return {"depth": depth, "seams": int(selected.sum()),
            "rms_residual": round(float(np.sqrt(np.mean(residual ** 2))), 4), "linked_chunks": int(kept.sum())}


def assembled_walk(tables: dict, blocks: list[tuple[int, int]], y0: int, x0: int, side: int,
                   block: int = BLOCK) -> dict:
    """The walk over the square of side `side` at (y0, x0), made of the steps whose two chunks are in `blocks`.

    `tables[(by, bx)]` holds the mean step of every seam that LEAVES a chunk of that block, `{"h": {"r_c": step}, "v":
    …}`. The steps are put back row by row then column by column, the order the research gave them to the least
    squares.
    """
    allowed = set(blocks)

    def inside(r, c):
        return (r // block * block, c // block * block) in allowed

    h, v = {}, {}
    for r in range(y0, y0 + side):
        for c in range(x0, x0 + side):
            if not inside(r, c):
                continue
            t = tables[(r // block * block, c // block * block)]
            for direction, neighbour, d in (("h", (r, c + 1), h), ("v", (r + 1, c), v)):
                x = t[direction].get(f"{r}_{c}")
                if x is not None and inside(*neighbour):
                    d.setdefault(r, {})[c] = x
    return block_depth(h, v, y0, x0, side)


def neighbourhood_anchor(diff: np.ndarray, y0: int, x0: int, by: int, bx: int, side: int = BLOCK) -> float | None:
    """The median of the difference over the neighbourhood, the block itself left out."""
    d = diff.copy()
    d[by - y0:by - y0 + side, bx - x0:bx - x0 + side] = np.nan
    return float(np.nanmedian(d)) if np.isfinite(d).any() else None


def to_mesh_points(chunk_map: np.ndarray, by: int, bx: int, shape: tuple, mesh: int = MESH,
                   chunk: int = CHUNK) -> tuple[np.ndarray, np.ndarray]:
    """A map given at the chunk centres of a block, carried to the points of the transfer INSIDE the block.

    Bilinear between centres, held constant between the last centre and the edge of the block. Returns the map on the
    points (NaN outside the block and where one of the four centres is missing) and the mask of the block's points.
    """
    side = chunk_map.shape[0]
    px = GRID_STEP * mesh
    out = np.full(shape, np.nan)
    inside = np.zeros(shape, dtype=bool)
    for i in range(shape[0]):
        y = i * px / chunk - by - 0.5
        if not (-0.5 <= y < side - 0.5):
            continue
        for j in range(shape[1]):
            x = j * px / chunk - bx - 0.5
            if not (-0.5 <= x < side - 0.5):
                continue
            inside[i, j] = True
            yc, xc = min(max(y, 0.0), side - 1.0), min(max(x, 0.0), side - 1.0)
            y0, x0 = min(int(np.floor(yc)), side - 2), min(int(np.floor(xc)), side - 2)
            q = chunk_map[y0:y0 + 2, x0:x0 + 2]
            if not np.isfinite(q).all():
                continue
            fy, fx = yc - y0, xc - x0
            out[i, j] = (1 - fy) * ((1 - fx) * q[0, 0] + fx * q[0, 1]) + fy * ((1 - fx) * q[1, 0] + fx * q[1, 1])
    return out, inside


def slip_mixture(x: np.ndarray, slip: float, iterations: int = ITERATIONS) -> dict:
    """The noise and the two slips, centred on 0 and ±`slip`, one shared width; weights and width by EM.

    The width starts at the robust spread (1.4826 × the median absolute deviation) and never falls under one voxel.
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    centres = np.array([0.0, slip, -slip])
    w = np.array([0.9, 0.05, 0.05])
    s = max(1.4826 * float(np.median(np.abs(x - np.median(x)))), 1.0)
    for _ in range(iterations):
        z = (x[:, None] - centres[None, :]) / s
        dens = w[None, :] * np.exp(-0.5 * z * z)
        tot = dens.sum(axis=1, keepdims=True)
        r = dens / np.where(tot > 0, tot, 1.0)
        w_n = r.mean(axis=0)
        s_n = max(float(np.sqrt((r * (x[:, None] - centres[None, :]) ** 2).sum() / len(x))), 1.0)
        done = np.allclose(w_n, w, atol=1e-10) and abs(s_n - s) < 1e-8
        w, s = w_n, s_n
        if done:
            break
    return {"noise": round(float(w[0]), 4), "slipped_above": round(float(w[1]), 4),
            "slipped_below": round(float(w[2]), 4), "width_voxels": round(s, 4), "slip_voxels": slip,
            "chunks": int(len(x)), "_w": w.tolist(), "_s": s}


def decide(gap: np.ndarray, mixture: dict) -> np.ndarray:
    """The points whose gap is more likely that of a slipped winding than that of the noise."""
    w, s, g = np.array(mixture["_w"]), mixture["_s"], mixture["slip_voxels"]
    ok = np.isfinite(gap)
    x = np.where(ok, gap, 0.0)
    p = [w[k] * np.exp(-0.5 * ((x - c) / s) ** 2) for k, c in enumerate((0.0, g, -g))]
    return ok & (np.maximum(p[1], p[2]) > p[0])


def apply_correction(tau: np.ndarray, gap: np.ndarray, decided: np.ndarray) -> np.ndarray:
    """Each decided point is brought back by its gap."""
    t = tau.copy()
    t[decided] = tau[decided] - gap[decided]
    return t


# ── The judge: it scores, and never decides ──────────────────────────────────────────────────────────────────────

def judged_error(tau: np.ndarray, judges: list[np.ndarray], half: int = HALF_SHEET) -> np.ndarray:
    """The error of the transfer where every judge exists and they agree within half a sheet, NaN elsewhere."""
    ok = np.isfinite(tau)
    for j in judges:
        ok &= np.isfinite(j)
    for j in judges[1:]:
        with np.errstate(invalid="ignore"):
            ok &= np.abs(j - judges[0]) < half
    return np.where(ok, tau - judges[0], np.nan)


def share_right(tau: np.ndarray, truth: np.ndarray, mask: np.ndarray, half: int = HALF_SHEET) -> dict:
    """How many points are scored in `mask`, and the share of them on the right winding."""
    e = tau - truth
    scored = mask & np.isfinite(e)
    return {"scored_points": int(scored.sum()),
            "share_on_the_right_winding": round(float((np.abs(e[scored]) < half).mean()), 4) if scored.any() else None}


def tally(tau0, tau1, truth, err, inside, decided, half: int = HALF_SHEET) -> dict:
    """What the correction did to the scored points of a block: points corrected, misses made right, rights missed."""
    scored = inside & np.isfinite(err)
    with np.errstate(invalid="ignore"):
        miss = np.abs(err) >= half
        e1 = tau1 - truth
        return {"corrected_points": int((decided & inside).sum()),
                "after": share_right(tau1, truth, inside, half),
                "misses_made_right": int((scored & miss & (np.abs(e1) < half)).sum()),
                "rights_made_misses": int((scored & ~miss & (np.abs(e1) >= half)).sum())}


# ── A block, and the whole segment ───────────────────────────────────────────────────────────────────────────────

def block_decision(tau0: np.ndarray, err: np.ndarray, produced: np.ndarray, reference: np.ndarray, by: int, bx: int,
                   slip: float, margin: int = BLOCK):
    """The decision on one neighbourhood: its tally, the corrected points and their new values; None when no neighbour
    links to the block. The block sits `margin` chunks from the edge of the neighbourhood."""
    c = BLOCK
    diff = produced - reference
    anchor = neighbourhood_anchor(diff, by - margin, bx - margin, by, bx)
    if anchor is None:
        return None
    d_b = diff[margin:margin + c, margin:margin + c] - anchor
    gap, inside = to_mesh_points(d_b, by, bx, tau0.shape)
    gap = np.where(inside, gap, np.nan)
    decided = decide(gap, slip_mixture(d_b, slip))
    tau1 = apply_correction(tau0, gap, decided)
    truth = tau0 - err
    result = {"anchor_voxels": round(float(anchor), 4), "before": share_right(tau0, truth, inside),
              **tally(tau0, tau1, truth, err, inside, decided)}
    return result, decided & inside, tau1


def correct_block(by: int, bx: int, candidates, tables: dict, tau0, err, slip: float, surfaces: tuple) -> tuple:
    """The decision on a block and its candidate neighbours; `surfaces` is (the reference, the produced winding).

    `tables[(surface, by, bx)]` are the step tables. A block whose neighbourhood lacks a table, or that has no
    candidate neighbour, is left undecided, with the reason.
    """
    blocks = [(by, bx)] + neighbours(by, bx, candidates)
    for s in surfaces:
        for vy, vx in blocks:
            if (s, vy, vx) not in tables:
                return {"row": by, "column": bx, "decidable": False, "reason": f"no step table of {s} on ({vy}, {vx})"}, None
    if len(blocks) == 1:
        return {"row": by, "column": bx, "decidable": False, "reason": "no candidate neighbour"}, None
    margin = BLOCK
    depth = {s: assembled_walk({b: tables[(s, *b)] for b in blocks}, blocks, by - margin, bx - margin,
                               2 * margin + BLOCK)["depth"] for s in surfaces}
    got = block_decision(tau0, err, depth[surfaces[1]], depth[surfaces[0]], by, bx, slip, margin)
    if got is None:
        return {"row": by, "column": bx, "decidable": False, "reason": "no neighbour links to the block"}, None
    result, corrected, tau1 = got
    return {"row": by, "column": bx, "decidable": True, "neighbours": len(blocks) - 1, **result}, (corrected, tau1)


def pooled_share(blocks: list[dict], key: str) -> float | None:
    """The share on the right winding of all the scored points of the blocks, pooled."""
    n = sum(b[key]["scored_points"] for b in blocks if b.get(key))
    j = sum(b[key]["scored_points"] * b[key]["share_on_the_right_winding"] for b in blocks
            if b.get(key) and b[key]["share_on_the_right_winding"] is not None)
    return round(j / n, 4) if n else None


def pooled(blocks: list[dict]) -> dict:
    """The decided blocks, pooled: the share before and after over all their scored points, and the counts."""
    ok = [b for b in blocks if b.get("decidable")]
    out = {"blocks": len(ok), "before": pooled_share(ok, "before"), "after": pooled_share(ok, "after"),
           "scored_points": sum(b["before"]["scored_points"] for b in ok),
           **{k: sum(b[k] for b in ok) for k in COUNTS}}
    out["net_gain"] = out["misses_made_right"] - out["rights_made_misses"]

    def change(b):
        return (b["after"]["share_on_the_right_winding"] or 0) - (b["before"]["share_on_the_right_winding"] or 0)
    out["blocks_up"] = sum(1 for b in ok if change(b) > 0)
    out["blocks_down"] = sum(1 for b in ok if change(b) < 0)
    out["blocks_unchanged"] = sum(1 for b in ok if change(b) == 0)
    return out


def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact sign test at one chance in two: the smaller tail, doubled (`290`)."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def correct_segment(tau0: np.ndarray, judges: list[np.ndarray], tables: dict, candidates, slip: float,
                    surfaces: tuple) -> dict:
    """The procedure on every candidate block, in row then column order, and the corrected winding.

    Each block decides from the UNCORRECTED transfer; its corrected points are then written into the winding. The
    judges score the result and nothing else. `tau1` is the procedure as the research ran it, on every block;
    `claimed` keeps only the corrections of the blocks within the validated geometry, and is what the program
    delivers.
    """
    err = judged_error(tau0, judges)
    blocks, tau1, claimed = [], tau0.copy(), tau0.copy()
    for by, bx in sorted(candidates):
        b, corr = correct_block(by, bx, candidates, tables, tau0, err, slip, surfaces)
        b["validated_geometry"] = within_validated_geometry(by, bx, candidates)
        blocks.append(b)
        if corr is not None:
            mask, t = corr
            tau1[mask] = t[mask]
            if b["validated_geometry"]:
                claimed[mask] = t[mask]
    scored = np.isfinite(err)
    together = pooled(blocks)
    return {"blocks": blocks, "pooled": together, "tau1": tau1, "claimed": claimed,
            "pooled_within_validated_geometry": pooled([b for b in blocks if b["validated_geometry"]]),
            "share_of_the_segment_in_the_blocks": (round(together["scored_points"] / int(scored.sum()), 4)
                                                   if scored.any() else None),
            "whole_segment": {"before": share_right(tau0, tau0 - err, scored), "after": share_right(tau1, tau0 - err, scored)},
            "sign_test": {"on_points": sign_test(together["misses_made_right"], together["rights_made_misses"]),
                          "on_blocks": sign_test(together["blocks_up"], together["blocks_down"])}}
