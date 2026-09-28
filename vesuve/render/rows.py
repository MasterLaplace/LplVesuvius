"""Rows of writing, without reading: does an ink map carry lines, and at what line spacing?

Port of `src/encre/typographie.py` on the `experimental` branch (`interligne` and what it calls). The ink is
separated from the support by Otsu on the papyrus pixels alone, the ink density per row is related to the surface
crossed, detrended, then autocorrelated; the SHARPEST inner peak, over a fan of angles, gives the line spacing. A
peak counts when its prominence exceeds the floor DERIVED from white noise:

    floor = 2 × √(2 ln k) / √n

⚠ It is a necessary check, never a sufficient one: a prediction that fails it is certainly not text, one that
passes it MAY be a periodic artefact. Hence the shuffle, which must lose the period.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage

ANGLES_DEG = tuple(range(-12, 13, 2))
MIN_PERIOD = 8
MAX_PERIOD_SHARE = 0.25
NOISE_FACTOR = 2.0


def binarise_ink(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """The ink against the support, by Otsu on the papyrus pixels alone (`img` in 0..255)."""
    vals = img[mask]
    if vals.size < 64:
        return np.zeros_like(mask)
    hist = np.bincount(vals.astype(np.int64), minlength=256)[:256].astype(float)
    total = hist.sum()
    if total == 0:
        return np.zeros_like(mask)
    levels = np.arange(256, dtype=float)
    weight0 = np.cumsum(hist)
    weight1 = total - weight0
    running = np.cumsum(hist * levels)
    ok = (weight0 > 0) & (weight1 > 0)
    mean0 = np.where(ok, running / np.maximum(weight0, 1.0), 0.0)
    mean1 = np.where(ok, (running[-1] - running) / np.maximum(weight1, 1.0), 0.0)
    variance = np.where(ok, weight0 * weight1 * (mean0 - mean1) ** 2, -1.0)
    return mask & (img > int(np.argmax(variance)))


def _profile(binary: np.ndarray, mask: np.ndarray, angle_deg: float):
    if abs(angle_deg) > 1e-9:
        b = ndimage.rotate(binary.astype(np.float32), angle_deg, order=0, reshape=False, mode="constant", cval=0.0)
        m = ndimage.rotate(mask.astype(np.float32), angle_deg, order=0, reshape=False, mode="constant", cval=0.0)
    else:
        b, m = binary.astype(np.float32), mask.astype(np.float32)
    area, ink = m.sum(axis=1), b.sum(axis=1)
    keep = area > (0.60 * max(area.max(), 1.0))  # an edge row does not make a peak
    if keep.sum() < 4 * MIN_PERIOD:
        return None
    return ink[keep] / area[keep]


def noise_floor(n: int, k: int) -> float:
    if n < 4 or k < 2:
        return float("inf")
    return NOISE_FACTOR * math.sqrt(2.0 * math.log(k)) / math.sqrt(n)


def _detrend(profile: np.ndarray, width: int) -> np.ndarray:
    width = max(3, int(width) | 1)
    if profile.size <= width:
        return profile - profile.mean()
    trend = np.convolve(profile, np.ones(width) / width, mode="same")
    half = width // 2
    if half:
        trend[:half] = profile[:width].mean()
        trend[-half:] = profile[-width:].mean()
    return profile - trend


def _autocorrelation(profile: np.ndarray):
    x = profile - profile.mean()
    n = x.size
    if n < 4 * MIN_PERIOD or float(np.dot(x, x)) <= 0:
        return None
    ac = np.correlate(x, x, mode="full")[n - 1:]
    return ac / ac[0]


def line_spacing(binary: np.ndarray, mask: np.ndarray) -> dict:
    """{period in pixels, sharpness, floor, angle, periodic}: the period-sharpness pair is the measurement."""
    best = {"period_px": None, "sharpness": 0.0, "angle_deg": None}
    for angle in ANGLES_DEG:
        prof = _profile(binary, mask, angle)
        if prof is None:
            continue
        high = max(MIN_PERIOD + 1, int(len(prof) * MAX_PERIOD_SHARE))
        ac = _autocorrelation(_detrend(prof, high))
        if ac is None:
            continue
        window = ac[MIN_PERIOD:high]
        if window.size < 3:
            continue
        i = int(np.argmax(window))
        if i == 0 or i >= window.size - 1:  # a peak on the edge is a step, not a period
            continue
        sharpness = float(window[i]) - max(float(window[:i].min()), float(window[i:].min()))
        if sharpness > best["sharpness"]:
            best = {"period_px": int(i + MIN_PERIOD), "sharpness": sharpness,
                    "floor": noise_floor(len(prof), window.size), "angle_deg": float(angle)}
    best.setdefault("floor", None)
    best["periodic"] = bool(best["floor"] is not None and best["sharpness"] >= best["floor"])
    return best


def shuffle(binary: np.ndarray, mask: np.ndarray, seed: int) -> np.ndarray:
    """The same ink pixels, redistributed at random WITHIN the papyrus: the distribution stays, the structure
    goes. A line spacing that survives the shuffle was not writing."""
    rng = np.random.default_rng(int(seed))
    out = np.zeros_like(binary)
    where = np.flatnonzero(mask.ravel())
    vals = binary.ravel()[where].copy()
    rng.shuffle(vals)
    out.ravel()[where] = vals
    return out


def row_skew(binary: np.ndarray, mask: np.ndarray, step: float = 0.5) -> float:
    """The angle at which the rows are horizontal: the one that maximises the variance of the projection profile
    (the standard page-skew estimation, Postl 1986, Baird 1987).

    ⚠ It is NOT the angle of `line_spacing`, and the difference is measured: its sharpness is a NORMALISED
    autocorrelation, hence scale invariant; a page skewed by 6° stays periodic at every angle and `line_spacing`
    may answer 0°. To decide "periodic or not" that is harmless; to DRAW lines, one needs the angle at which their
    contrast is strongest, and it is this one.
    """
    best, best_var = 0.0, -1.0
    for angle in np.arange(ANGLES_DEG[0], ANGLES_DEG[-1] + 1e-9, step):
        prof = _profile(binary, mask, float(angle))
        if prof is None:
            continue
        v = float(np.var(_detrend(prof, max(MIN_PERIOD + 1, int(len(prof) * MAX_PERIOD_SHARE)))))
        if v > best_var:
            best, best_var = float(angle), v
    return best


def row_lines(binary: np.ndarray, mask: np.ndarray, measurement: dict) -> np.ndarray:
    """The trace of the rows found: a mask of lines, in the frame of the image.

    The lines are placed where the detrended density peaks, at least three fifths of the line spacing apart, in the
    ROTATED frame where the measurement found them, then brought back by the inverse rotation of the same function:
    no sign convention to guess.
    """
    h, w = binary.shape
    trace = np.zeros((h, w), dtype=bool)
    if not measurement.get("periodic"):
        return trace
    angle, period = row_skew(binary, mask), int(measurement["period_px"])
    b = ndimage.rotate(binary.astype(np.float32), angle, order=0, reshape=False, mode="constant", cval=0.0)
    m = ndimage.rotate(mask.astype(np.float32), angle, order=0, reshape=False, mode="constant", cval=0.0)
    area, ink = m.sum(axis=1), b.sum(axis=1)
    keep = area > (0.60 * max(area.max(), 1.0))
    rows = np.flatnonzero(keep)
    if rows.size < 4 * MIN_PERIOD:
        return trace
    prof = _detrend(ink[keep] / area[keep], max(MIN_PERIOD + 1, int(rows.size * MAX_PERIOD_SHARE)))
    peaks = []
    for i in np.argsort(-prof):
        if all(abs(int(i) - p) >= 0.6 * period for p in peaks) and prof[i] > 0:
            peaks.append(int(i))
    lines = np.zeros((h, w), dtype=np.float32)
    for p in peaks:
        r = int(rows[p])
        lines[max(0, r - 1):r + 2, :] = 1.0
    back = ndimage.rotate(lines, -angle, order=0, reshape=False, mode="constant", cval=0.0) > 0.5
    return back & mask
