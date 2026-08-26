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


# --- relief: the signal that separates, measured offline on 138 series -----------------
# ⚠⚠ Its formula is (max - min) / mean, the same as the offline profiler's, and these
# checks pin it. A second definition of one quantity would drift from the numbers it is
# meant to be compared against.
ck(abs(T.relief_of([0.0, 0.0, 1.0, 0.0, 0.0]) - 5.0) < 1e-9,
   "one spike in five layers: (1-0)/0.2 = 5")
ck(T.relief_of([1.0, 1.0, 1.0, 1.0]) == 0.0, "a flat column has no relief")
# ⚠ Dimensionless: the same shape in different intensity units must read the same. Without
# this the number would be a property of the scanner's gain, not of the surface.
ck(abs(T.relief_of([0.0, 0.0, 1.0, 0.0, 0.0])
       - T.relief_of([0.0, 0.0, 1000.0, 0.0, 0.0])) < 1e-9,
   "relief is dimensionless: a gain of 1000 does not move it")
# ⚠ An empty or non-positive column must not divide by zero, and must not claim relief.
ck(T.relief_of([]) == 0.0, "an empty column claims no relief")
ck(T.relief_of([0.0, 0.0, 0.0]) == 0.0, "an all-zero column claims no relief")
# ⚠⚠ And the floor must be the SAME number the offline profiler uses. Two floors for one
# quantity would let a surface pass here and fail there.
ck(T.RELIEF_FLOOR == 0.02, "the floor is the profiler's own 0.02")


# ⚠⚠ THE CSV HEADER AND ITS ROW MUST HAVE THE SAME WIDTH. A column added to one and not
# the other shifts every field after it, silently, and the result is a table of confident
# wrong numbers -- the worst failure this tool can have, because nothing downstream can see
# it. The two views now come from one declaration, so the width is checked rather than
# trusted, and a missing field must not kill a two-hundred-segment run.
_fake = {"segment": "s", "material": 0.5, "relief": 0.18, "edge_pinned": 0.07,
         "offset_um": -13.2, "residual_um": 43.2, "residual_p90_um": 128.4,
         "rigid_share": 0.234, "coherence": 0.31, "coherence_shuffled": -0.081,
         "neighbour_pairs": 150, "coherence_reliable": True,
         "windows_with_papyrus": 96, "layers": 65, "window_px": 128}
ck(len(T.csv_header().split(",")) == len(T.csv_row(_fake).split(",")),
   "the CSV header and its row have the same width")
ck(T.csv_header().split(",")[2] == "relief", "relief is the third column, after material")
ck(T.csv_row(_fake).split(",")[2] == "0.1800", "and the row puts it there too")
# ⚠ Un champ absent ne doit pas tuer un balayage de deux cents segments.
ck(T.csv_row({k: v for k, v in _fake.items() if k != "relief"}).split(",")[2] == "0.0000",
   "a missing relief defaults to a visible zero instead of raising")
# ⚠⚠ La geometrie de lecture doit etre DANS le fichier : un tableau de calibration qui ne
# dit pas dans quelle fenetre il a ete lu ne calibre rien. Paye deux fois le meme jour.
ck("layers" in T.csv_header().split(",") and "window_px" in T.csv_header().split(","),
   "the CSV carries the reading geometry with the numbers")
ck(T.csv_row(_fake).split(",")[-1] == "128", "and the row puts the window size there")


def noisy_peak(url, level, meta, cy, cx, timeout):
    """Peaks scattered with no spatial structure: coherence must stay near zero."""
    rng = np.random.default_rng(cy * 1000 + cx)
    mean = np.zeros(DEPTH, dtype=np.float32)
    mean[int(rng.integers(0, DEPTH))] = 1.0
    return mean


# ⚠ Et le champ doit remonter jusqu au verdict, pas seulement exister dans la fonction :
# une colonne a un seul pic sur DEPTH couches a un relief de DEPTH.
ck(abs(out["relief"] - float(DEPTH)) < 1e-6,
   f"a single spike over {DEPTH} layers reads a relief of {DEPTH}")
ck(out["relief_floor"] == T.RELIEF_FLOOR, "and the verdict carries the floor with it")


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

# ---------------------------------------------------------------------------
# The seed verb. The claim it rests on is physical, so the controls are physical too:
# one sheet is planar, TWO PARALLEL SHEETS are just as planar (a regular stack is exactly
# where a seed belongs), and a junction collapses. Without the second line this would be a
# "little matter here" detector wearing a geometry's clothes.
# ---------------------------------------------------------------------------
K = 8


def cube():
    return np.zeros((K, K, K), np.uint8)


def planarity_of(block, k=K, smooth=1):
    return float(T.planarity_map(block, k, smooth)["planarity"][0])


one = cube(); one[4] = 255
two = cube(); two[2] = 255; two[6] = 255
cross = cube(); cross[4] = 255; cross[:, 4, :] = 255
ck(planarity_of(one) > 0.99, "one sheet must be planar")
ck(planarity_of(two) > 0.99, "TWO PARALLEL sheets must be just as planar")
ck(planarity_of(cross) < 0.10, "a junction must collapse")
noise = (np.random.default_rng(0).random((K, K, K)) < 0.15).astype(np.uint8) * 255
ck(planarity_of(noise) < 0.20, "isotropic noise is not a sheet")

# --- a uniform block -- all void or all matter -- has a NULL tensor. Its eigenvalues are
# --- ordered noise: a perfectly defined score that means nothing. It must be gated out,
# --- and the gate must survive an caller who widens the occupancy band to everything.
for b in (cube(), np.full((K, K, K), 255, np.uint8)):
    m = T.planarity_map(b, K)
    ck(float(m["energy"][0]) == 0.0, "a uniform block has no gradient energy")

# --- the orientation bias is MEASURED, not assumed: a thresholded prediction turns a
# --- tilted sheet into a staircase, and the steps populate a second gradient direction.
def tilted(k, deg, thick=1.2):
    g = np.indices((k, k, k)).astype(np.float32) - (k - 1) / 2.0
    nrm = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0.0])
    d = nrm[0] * g[0] + nrm[1] * g[1] + nrm[2] * g[2]
    return (np.abs(d) < thick).astype(np.uint8) * 255


K2 = 16
raw = [planarity_of(tilted(K2, t), K2, 0) for t in range(0, 91, 10)]
blur = [planarity_of(tilted(K2, t), K2, 1) for t in range(0, 91, 10)]
ck((max(raw) - min(raw)) > 2.5 * (max(blur) - min(blur)),
   "the blur must cut the orientation bias, not merely shift it")
ck(min(blur) > 0.85, "and the worst-oriented plane must stay clearly planar")
ck(min(blur) > planarity_of(cross) + 0.8,
   "the residual bias must stay far below the signal")

# --- the seed must be a LIT voxel. Returning the block centre puts it in the void as soon
# --- as the sheet crosses the block off-centre, and the tracer does not complain.
edge = cube(); edge[1] = 255
ck(edge[K // 2, K // 2, K // 2] == 0, "this fixture's centre must be void, or the check is empty")
spot = T.lit_voxel(edge, K, 0, 0, 0)
ck(spot is not None and edge[spot] > 0, "the seed must land on matter")
ck(spot[0] == 1)
ck(T.lit_voxel(cube(), K, 0, 0, 0) is None, "and an empty block yields no seed")

# --- the 3x3x3 aggregation must PAD, never wrap: a block on the rim sees fewer
# --- neighbours, not the neighbours of the opposite face.
val = np.zeros((3, 3, 3), np.float32); val[0, 0, 0] = 1.0
total, count = T._neighbourhood(val, np.ones((3, 3, 3), bool))
ck(total[2, 2, 2] == 0.0, "the far corner must not see the near one")
ck(count[0, 0, 0] == 8 and count[1, 1, 1] == 27)

# --- and the end-to-end claim: an isolated fleck, planar by accident, must LOSE against a
# --- clean extended stack. Without this, the neighbourhood mean is just an argmax.
C = 48
chunk = np.zeros((C, C, C), np.uint8)
gi = np.indices((C, C, C // 2))
chunk[:, :, :C // 2] = np.where(((gi[0] * 4 + gi[1]) % 20) < 3, 255, 0)
chunk[16:24, 16:24, 32:40][3] = 255
m = T.planarity_map(chunk, K)
valid = ((m["occupancy"] >= 0.02) & (m["occupancy"] <= 0.80) & (m["energy"] > 0))
shape = m["shape"]
total, count = T._neighbourhood(m["planarity"].reshape(shape), valid.reshape(shape))
mean = np.where(count.ravel() > 0, total.ravel() / np.maximum(count.ravel(), 1), 0.0)
kept = valid & (count.ravel() >= 6)
brut = m["planarity"].reshape(shape)
ck(brut[2, 2, 4] >= float(brut[:, :, :(C // 2) // K].max()) - 1e-6,
   "the fleck must be the single most planar block, or an argmax would not be tempted")
idx = int(np.argmax(np.where(kept, mean + 1e-6 * count.ravel(), -np.inf)))
ck(np.unravel_index(idx, shape)[2] < (C // 2) // K, "the seed must not land on the fleck")
ck(not bool(kept.reshape(shape)[2, 2, 4]), "and the fleck must not even be eligible")

# --- a missing object and a failing network are DIFFERENT FACTS. Collapsing them makes a
# --- diagnosis point at the wrong thing: a probe that cannot reach the bucket then reports
# --- "there is nothing at this coordinate", which is a claim about the DATA drawn from a
# --- claim about the WIRE. Paid on 2026-08-26, when a saturated link made a seed guard
# --- announce that a perfectly good seed designated no scanned matter.
import io
import urllib.error


def _raising(failure):
    def fake(url, timeout=None):
        raise failure
    return fake


_real_urlopen = T.urllib.request.urlopen
try:
    T.urllib.request.urlopen = _raising(
        urllib.error.HTTPError("u", 404, "Not Found", {}, None))
    ck(T.get_with_reason("u", 1) == (None, "absent"), "404 means the object is not served")
    T.urllib.request.urlopen = _raising(
        urllib.error.HTTPError("u", 403, "Forbidden", {}, None))
    ck(T.get_with_reason("u", 1) == (None, "absent"), "403 means the same to a prober")
    # ⚠ THE CHECK THAT MATTERS: a 5xx, a timeout and a broken socket must NOT be
    # reported as absence. Without these three the distinction would be a comment.
    T.urllib.request.urlopen = _raising(
        urllib.error.HTTPError("u", 503, "Slow Down", {}, None))
    ck(T.get_with_reason("u", 1)[1] == "http 503", "a 5xx is the service failing")
    T.urllib.request.urlopen = _raising(TimeoutError())
    ck(T.get_with_reason("u", 1)[1] == "delai depasse", "a timeout is not an absence")
    T.urllib.request.urlopen = _raising(urllib.error.URLError("no route"))
    ck(str(T.get_with_reason("u", 1)[1]).startswith("transport"),
       "a dead link is not an absence")
    # ... and none of those may look like absence to a caller that only tests presence.
    for failure in (urllib.error.HTTPError("u", 503, "x", {}, None), TimeoutError(),
                    urllib.error.URLError("no route")):
        T.urllib.request.urlopen = _raising(failure)
        ck(T.get_with_reason("u", 1)[1] != "absent",
           "a transport failure never reports as absence")
    # the success path still returns bytes and no reason
    T.urllib.request.urlopen = lambda url, timeout=None: io.BytesIO(b"ok")
    ck(T.get_with_reason("u", 1) == (b"ok", None), "a hit carries no reason")
    ck(T.get("u", 1) == b"ok", "and the presence-only form is unchanged")
finally:
    T.urllib.request.urlopen = _real_urlopen

print(f"ALL PASS (0 failures, {n} checks)")
