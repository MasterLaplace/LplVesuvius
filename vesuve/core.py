"""The C core, seen from Python: one function per equation, and the loops where the time goes.

Each function of this module calls its namesake in `core/include/vesuve.h`. A `VESUVE_BAD_ARGUMENT`
status becomes `ValueError` (the caller made a mistake); `VESUVE_UNDECIDABLE` becomes `Undecidable`,
never a zero nor a `None`: a stage that cannot answer says so, and that is what lets a pipeline name
where it stops.
"""
from __future__ import annotations

import ctypes
from pathlib import Path

import numpy as np

from vesuve import __version__

LIBRARY = Path(__file__).resolve().parent / "_core" / "libvesuve.so"

_OK, _BAD_ARGUMENT, _UNDECIDABLE, _NOT_IMPLEMENTED = 0, 1, 2, 99


class CoreMissing(RuntimeError):
    """The library is not built, or not at this package's version."""


class Undecidable(Exception):
    """The data cannot answer; the message says why."""


def _load() -> ctypes.CDLL:
    if not LIBRARY.exists():
        raise CoreMissing(f"the C core is not built: run `make -C {LIBRARY.parents[2]}`")
    lib = ctypes.CDLL(str(LIBRARY))
    lib.vesuve_version.restype = ctypes.c_char_p
    version = lib.vesuve_version().decode()
    if version != __version__:
        raise CoreMissing(f"core {version} against package {__version__}: rebuild with `make`")
    lib.vesuve_status_name.restype = ctypes.c_char_p
    lib.vesuve_status_name.argtypes = [ctypes.c_int]
    return lib


_lib = _load()

_d, _i, _pd, _pi = ctypes.c_double, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)
_pu8, _pu16 = ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint16)
_pf = ctypes.POINTER(ctypes.c_float)


def _declare(name: str, *argtypes) -> None:
    f = getattr(_lib, name)
    f.argtypes = list(argtypes)
    f.restype = ctypes.c_int


def _check(status: int, what: str) -> None:
    if status == _OK:
        return
    name = _lib.vesuve_status_name(status).decode()
    if status == _UNDECIDABLE:
        raise Undecidable(f"{what}: {name}")
    if status == _BAD_ARGUMENT:
        raise ValueError(f"{what}: {name}")
    raise NotImplementedError(f"{what}: {name}")


def _array(x, dtype) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(x, dtype=dtype))


def _ptr(a: np.ndarray, t):
    return a.ctypes.data_as(t)


for _name, _args in {
    "vesuve_half_sheet_voxels": (_d, _d, _pi),
    "vesuve_holdable_length": (_d, _d, _pd),
    "vesuve_spread_of_k_rows": (_d, _d, _i, _pd),
    "vesuve_triangle_own_noise": (_d, _d, _d, _pd),
    "vesuve_spread_standard_error": (_d, _i, _pd),
    "vesuve_decisive_count": (_d, _pi),
    "vesuve_block_length": (_i, _pi),
    "vesuve_convergence_alpha": (_d, _d, _d, _d, _pd),
    "vesuve_coherence": (_pd, _i, _pd),
    "vesuve_corrected_coherence": (_d, _i, _pd),
    "vesuve_fresnel_number": (_d, _d, _d, _pd),
    "vesuve_texture_filter": (_pu8, _i, _i, _i, _d, _pi, _pi),
    "vesuve_edge_profiles": (_pu8, _i, _i, _i, _pi, _i, _i, _pu16, _pu16, _pu16, _pu16),
    "vesuve_depth_profile": (_pu8, _i, _i, _i, _pd),
    "vesuve_cut_step": (_pd, _pd, _i, _i, _pi, _pi),
    "vesuve_seam_step": (_pd, _pd, _pu8, _i, _i, _i, _pd, _pd, _pi),
    "vesuve_area_under_curve": (_pd, _pu8, ctypes.c_size_t, ctypes.c_void_p, _pd),
    "vesuve_sample_along_normals": (_pu8, _i, _i, _i, _pf, _pf, ctypes.c_size_t, _pf, _i, _pf, _pu8),
}.items():
    _declare(_name, *_args)


class _Pair(ctypes.Structure):
    _fields_ = [("score", ctypes.c_double), ("label", ctypes.c_uint8)]


def version() -> str:
    return _lib.vesuve_version().decode()


# ── E2, B: the scale and the budget ─────────────────────────────────────────────────────────────

def half_sheet_voxels(step_um: float, voxel_um: float) -> int:
    r = ctypes.c_int()
    _check(_lib.vesuve_half_sheet_voxels(step_um, voxel_um, ctypes.byref(r)), "half sheet")
    return r.value


def _scalar(name: str, what: str, *args) -> float:
    r = ctypes.c_double()
    _check(getattr(_lib, name)(*args, ctypes.byref(r)), what)
    return r.value


def holdable_length(half_sheet: float, sigma: float) -> float:
    return _scalar("vesuve_holdable_length", "holdable length", half_sheet, sigma)


def spread_of_k_rows(sigma_shared: float, sigma_own: float, k: int) -> float:
    return _scalar("vesuve_spread_of_k_rows", "spread of k rows", sigma_shared, sigma_own, k)


def triangle_own_noise(v_ij: float, v_ik: float, v_jk: float) -> float:
    return _scalar("vesuve_triangle_own_noise", "triangle of own noises", v_ij, v_ik, v_jk)


def spread_standard_error(sigma: float, n: int) -> float:
    return _scalar("vesuve_spread_standard_error", "standard error of a spread", sigma, n)


def decisive_count(guarantee: float) -> int:
    r = ctypes.c_int()
    _check(_lib.vesuve_decisive_count(guarantee, ctypes.byref(r)), "decisive count")
    return r.value


def block_length(n: int) -> int:
    r = ctypes.c_int()
    _check(_lib.vesuve_block_length(int(n), ctypes.byref(r)), "block length")
    return r.value


# ── E7: judging without ground truth ────────────────────────────────────────────────────────────

def convergence_alpha(e0: float, e1: float, n0: float, n1: float) -> float:
    return _scalar("vesuve_convergence_alpha", "convergence test", e0, e1, n0, n1)


def coherence(increments) -> float:
    a = _array(increments, np.float64)
    return _scalar("vesuve_coherence", "coherence", _ptr(a, _pd), int(a.size))


def corrected_coherence(c: float, n: int) -> float:
    return _scalar("vesuve_corrected_coherence", "corrected coherence", c, n)


def fresnel_number(step_um: float, distance_m: float, energy_kev: float) -> float:
    return _scalar("vesuve_fresnel_number", "Fresnel number", step_um, distance_m, energy_kev)


# ── E4: the lattice ─────────────────────────────────────────────────────────────────────────────

EDGES = ("right", "left", "bottom", "top")


def _block(block) -> np.ndarray:
    b = _array(block, np.uint8)
    if b.ndim != 3:
        raise ValueError(f"a chunk is a cube (z, y, x), not an array of shape {b.shape}")
    return b


def texture_filter(block, floor_value: float = 0.15) -> tuple[int, bool]:
    b = _block(block)
    layers, kept = ctypes.c_int(), ctypes.c_int()
    _check(_lib.vesuve_texture_filter(_ptr(b, _pu8), *b.shape, floor_value, ctypes.byref(layers),
                                      ctypes.byref(kept)), "texture filter")
    return layers.value, bool(kept.value)


def edge_profiles(block, cuts, width: int) -> dict[str, np.ndarray]:
    """The four edge profiles, as integer sums: (cuts, depth) each, uint16."""
    b = _block(block)
    c = _array(cuts, np.int32)
    outputs = {k: np.zeros((c.size, b.shape[0]), dtype=np.uint16) for k in EDGES}
    _check(_lib.vesuve_edge_profiles(_ptr(b, _pu8), *b.shape, _ptr(c, _pi), int(c.size), int(width),
                                     *(_ptr(outputs[k], _pu16) for k in EDGES)), "edge profiles")
    return outputs


def depth_profile(block) -> np.ndarray:
    b = _block(block)
    p = np.zeros(b.shape[0], dtype=np.float64)
    _check(_lib.vesuve_depth_profile(_ptr(b, _pu8), *b.shape, _ptr(p, _pd)), "depth profile")
    return p


def cut_step(a, b, search_range: int) -> tuple[int, bool]:
    x, y = _array(a, np.float64), _array(b, np.float64)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError(f"two profiles of the same length, not {x.shape} and {y.shape}")
    step, saturated = ctypes.c_int(), ctypes.c_int()
    _check(_lib.vesuve_cut_step(_ptr(x, _pd), _ptr(y, _pd), int(x.size), int(search_range),
                                ctypes.byref(step), ctypes.byref(saturated)), "step of a cut")
    return step.value, bool(saturated.value)


def seam_step(a, b, readable, search_range: int) -> tuple[float, float, int]:
    """(step, disagreement, cuts) of a seam, NOT rounded; `a` and `b` are (cuts, depth)."""
    x, y = _array(a, np.float64), _array(b, np.float64)
    m = _array(readable, np.uint8)
    if x.shape != y.shape or x.ndim != 2 or m.shape != (x.shape[0],):
        raise ValueError(f"profiles {x.shape} and {y.shape}, mask {m.shape}: incompatible shapes")
    step, disagreement, cuts = ctypes.c_double(), ctypes.c_double(), ctypes.c_int()
    _check(_lib.vesuve_seam_step(_ptr(x, _pd), _ptr(y, _pd), _ptr(m, _pu8), x.shape[0], x.shape[1],
                                 int(search_range), ctypes.byref(step), ctypes.byref(disagreement),
                                 ctypes.byref(cuts)), "step of a seam")
    return step.value, disagreement.value, cuts.value


# ── E8: rendering, and validating by the ink ────────────────────────────────────────────────────

def area_under_curve(scores, labels) -> float:
    s = _array(scores, np.float64).ravel()
    e = _array(np.asarray(labels).astype(bool), np.uint8).ravel()
    if s.size != e.size:
        raise ValueError(f"{s.size} scores for {e.size} labels")
    work = (_Pair * max(1, s.size))()
    r = ctypes.c_double()
    _check(_lib.vesuve_area_under_curve(_ptr(s, _pd), _ptr(e, _pu8), s.size, ctypes.cast(work, ctypes.c_void_p),
                                        ctypes.byref(r)), "area under the curve")
    return r.value


def sample_along_normals(volume, points, normals, offsets) -> tuple[np.ndarray, np.ndarray]:
    """(output, valid) of shape (offsets, points); points and normals (n, 3) in (x, y, z)."""
    v = _block(volume)
    p, n = _array(points, np.float32).reshape(-1, 3), _array(normals, np.float32).reshape(-1, 3)
    d = _array(offsets, np.float32).ravel()
    if p.shape != n.shape:
        raise ValueError(f"{p.shape[0]} points for {n.shape[0]} normals")
    output = np.zeros((d.size, p.shape[0]), dtype=np.float32)
    valid = np.zeros((d.size, p.shape[0]), dtype=np.uint8)
    _check(_lib.vesuve_sample_along_normals(_ptr(v, _pu8), *v.shape, _ptr(p, _pf), _ptr(n, _pf), p.shape[0],
                                            _ptr(d, _pf), int(d.size), _ptr(output, _pf), _ptr(valid, _pu8)),
           "sampling")
    return output, valid.astype(bool)
