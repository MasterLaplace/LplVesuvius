#!/usr/bin/env python3
"""Offline controls for tracecheck — no network, no bucket, no credentials.

Every claim the tool makes about its own arithmetic is checked here against a synthetic
volume whose answer is known in advance. Run it before trusting a run.

A check that cannot fail proves nothing, so each battery includes a negative case: a
field of noise must NOT look coherent, and a pure shift must leave a residual of exactly
zero.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tracecheck as T

n = 0


def ck(condition, what=""):
    global n
    assert condition, what
    n += 1


# --- the chunk key uses the separator the array DECLARES, and the level is always a
# directory. Getting this wrong returns 404s that a naive reader counts as empty chunks.
ck(T.chunk_key({"dimension_separator": "/"}, 0, 3, 5) == "0/0/3/5")
ck(T.chunk_key({"dimension_separator": "."}, 2, 3, 5) == "2/0.3.5")
ck(T.chunk_key({}, 1, 0, 0) == "1/0.0.0", "absent separator defaults to '.' per the spec")

# --- an uncompressed chunk of the wrong length is a corrupt read, not data.
ck(T.decode(b"\x01" * 12, {}, 12) == b"\x01" * 12)
ck(T.decode(b"\x01" * 11, {}, 12) is None)

# --- surface-volume discovery must prefer the FINEST scan when nothing is asked for,
# and honour --prefer when something is.
paths = ["S/segments/x/surface-volumes/45.532um-a.zarr",
         "S/segments/x/surface-volumes/2.4um-b.zarr",
         "S/segments/x/surface-volumes/1.129um-c.zarr"]
T.list_prefix = lambda prefix, timeout, delimiter="/": [p + "/" for p in paths]
ck(T.find_surface_volume("S", "x", 1.0, None).endswith("1.129um-c.zarr"))
ck(T.find_surface_volume("S", "x", 1.0, "2.4um").endswith("2.4um-b.zarr"))
ck(T.find_surface_volume("S", "x", 1.0, "9.9um").endswith("1.129um-c.zarr"),
   "an unmatched --prefer falls back rather than failing")

# --- the whole judgement, on a synthetic volume whose answer is known.
DEPTH, HY, HX = 16, 8, 8
META = {"chunks": [DEPTH, HY, HX], "shape": [DEPTH, 8 * HY, 40 * HX],
        "dtype": "|u1", "dimension_separator": "/"}
T.array_meta = lambda *a, **k: META


def constant_peak(url, level, meta, cy, cx, timeout):
    """Every window peaks 3 layers below the traced surface: a pure rigid shift."""
    mean = np.zeros(DEPTH, dtype=np.float32)
    mean[DEPTH // 2 + 3] = 1.0
    return mean


T.column = constant_peak
out = T.judge("x", 0, 2.0, 4, 4, 1.0, 4)
ck(abs(out["offset_um"] - 6.0) < 1e-9, "3 layers x 2 um")
ck(out["residual_um"] == 0.0, "a PURE shift leaves nothing behind")
ck(out["rigid_share"] > 0.99, "and a translation would remove all of it")
ck(out["material"] == 1.0)


def noisy_peak(url, level, meta, cy, cx, timeout):
    """Peaks scattered with no spatial structure: coherence must stay near zero."""
    rng = np.random.default_rng(cy * 1000 + cx)
    mean = np.zeros(DEPTH, dtype=np.float32)
    mean[int(rng.integers(0, DEPTH))] = 1.0
    return mean


T.column = noisy_peak
noisy = T.judge("x", 0, 2.0, 5, 4, 1.0, 4)
ck(abs(noisy["coherence"]) < 0.4, "noise must NOT look coherent")
ck(noisy["residual_um"] > 0, "and it must leave a residual")


def smooth_peak(url, level, meta, cy, cx, timeout):
    """A peak that drifts smoothly with position: coherence must be high, shuffle low."""
    mean = np.zeros(DEPTH, dtype=np.float32)
    mean[min(DEPTH - 1, (cy + cx) % DEPTH)] = 1.0
    return mean


T.column = smooth_peak
smooth = T.judge("x", 0, 2.0, 6, 3, 1.0, 4)
ck(smooth["coherence"] > smooth["coherence_shuffled"] + 0.3,
   "a smooth field must beat its own shuffle")

# --- coherence must declare when it has too few pairs to mean anything.
# ⚠ Measured on a real segment at --blocks 2 --side 3: coherence 0.435 against a shuffle
# control of 0.423. The control had stopped discriminating and nothing said so.
T.column = smooth_peak
thin = T.judge("x", 0, 2.0, 2, 2, 1.0, 4)
ck(not thin["coherence_reliable"], "a tiny sample must NOT claim a reliable coherence")
ck(thin["neighbour_pairs"] < 40)
ck(smooth["coherence_reliable"], "and a proper one must")
ck(smooth["neighbour_pairs"] >= 40)

# --- an empty canvas is refused, not reported as a perfect trace.
T.column = lambda *a, **k: "empty"
try:
    T.judge("x", 0, 2.0, 4, 4, 1.0, 4)
    ck(False, "an empty volume must be refused")
except RuntimeError:
    ck(True)

print(f"ALL PASS (0 failures, {n} checks)")
