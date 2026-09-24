"""Le noyau C, vu de Python : une fonction par équation, et les boucles où le temps part.

Chaque fonction de ce module appelle son homonyme de `noyau/include/vesuve.h`. Un statut
`VESUVE_ARGUMENT` devient `ValueError` (l'appelant s'est trompé) ; `VESUVE_INDECIDABLE` devient
`Indecidable`, jamais un zéro ni un `None` : un étage qui ne sait pas répondre le dit, et c'est ce
qui laisse le pipeline nommer où il s'arrête.
"""
from __future__ import annotations

import ctypes
from pathlib import Path

import numpy as np

from vesuve import __version__

LA_BIBLIOTHEQUE = Path(__file__).resolve().parent / "_noyau" / "libvesuve.so"

_OK, _ARGUMENT, _INDECIDABLE, _NON_IMPLEMENTE = 0, 1, 2, 99


class NoyauAbsent(RuntimeError):
    """La bibliothèque n'est pas construite, ou pas à la version de ce paquet."""


class Indecidable(Exception):
    """Les données ne permettent pas de répondre ; le message dit pourquoi."""


def _charger() -> ctypes.CDLL:
    if not LA_BIBLIOTHEQUE.exists():
        raise NoyauAbsent(f"le noyau C n'est pas construit : lancer `make -C {LA_BIBLIOTHEQUE.parents[2]}`")
    lib = ctypes.CDLL(str(LA_BIBLIOTHEQUE))
    lib.vesuve_version.restype = ctypes.c_char_p
    version = lib.vesuve_version().decode()
    if version != __version__:
        raise NoyauAbsent(f"noyau {version} contre paquet {__version__} : reconstruire avec `make`")
    lib.vesuve_nom_du_statut.restype = ctypes.c_char_p
    lib.vesuve_nom_du_statut.argtypes = [ctypes.c_int]
    return lib


_lib = _charger()

_d, _i, _pd, _pi = ctypes.c_double, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)
_pu8, _pu16 = ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint16)
_pf = ctypes.POINTER(ctypes.c_float)


def _declarer(nom: str, *argtypes) -> None:
    f = getattr(_lib, nom)
    f.argtypes = list(argtypes)
    f.restype = ctypes.c_int


def _verifier(statut: int, quoi: str) -> None:
    if statut == _OK:
        return
    nom = _lib.vesuve_nom_du_statut(statut).decode()
    if statut == _INDECIDABLE:
        raise Indecidable(f"{quoi} : {nom}")
    if statut == _ARGUMENT:
        raise ValueError(f"{quoi} : {nom}")
    raise NotImplementedError(f"{quoi} : {nom}")


def _tableau(x, dtype) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(x, dtype=dtype))


def _ptr(a: np.ndarray, t):
    return a.ctypes.data_as(t)


for _nom, _args in {
    "vesuve_demi_feuillet_voxels": (_d, _d, _pi),
    "vesuve_longueur_tenable": (_d, _d, _pd),
    "vesuve_dispersion_de_k_rangees": (_d, _d, _i, _pd),
    "vesuve_bruit_propre_du_triangle": (_d, _d, _d, _pd),
    "vesuve_erreur_dune_dispersion": (_d, _i, _pd),
    "vesuve_compte_decisif": (_d, _pi),
    "vesuve_longueur_de_bloc": (_i, _pi),
    "vesuve_alpha_de_convergence": (_d, _d, _d, _d, _pd),
    "vesuve_coherence": (_pd, _i, _pd),
    "vesuve_coherence_corrigee": (_d, _i, _pd),
    "vesuve_nombre_de_fresnel": (_d, _d, _d, _pd),
    "vesuve_filtre_de_texture": (_pu8, _i, _i, _i, _d, _pi, _pi),
    "vesuve_profils_de_bord": (_pu8, _i, _i, _i, _pi, _i, _i, _pu16, _pu16, _pu16, _pu16),
    "vesuve_profil_de_profondeur": (_pu8, _i, _i, _i, _pd),
    "vesuve_pas_dune_coupe": (_pd, _pd, _i, _i, _pi, _pi),
    "vesuve_pas_dune_couture": (_pd, _pd, _pu8, _i, _i, _i, _pd, _pd, _pi),
    "vesuve_aire_sous_la_courbe": (_pd, _pu8, ctypes.c_size_t, ctypes.c_void_p, _pd),
    "vesuve_echantillonner_le_long_des_normales": (_pu8, _i, _i, _i, _pf, _pf, ctypes.c_size_t, _pf, _i,
                                                    _pf, _pu8),
}.items():
    _declarer(_nom, *_args)


class _Paire(ctypes.Structure):
    _fields_ = [("score", ctypes.c_double), ("etiquette", ctypes.c_uint8)]


def version() -> str:
    return _lib.vesuve_version().decode()


# ── E2, B : l'échelle et le budget ──────────────────────────────────────────────────────────────

def demi_feuillet_voxels(pas_um: float, voxel_um: float) -> int:
    r = ctypes.c_int()
    _verifier(_lib.vesuve_demi_feuillet_voxels(pas_um, voxel_um, ctypes.byref(r)), "demi-feuillet")
    return r.value


def _scalaire(nom: str, quoi: str, *args) -> float:
    r = ctypes.c_double()
    _verifier(getattr(_lib, nom)(*args, ctypes.byref(r)), quoi)
    return r.value


def longueur_tenable(demi_feuillet: float, sigma: float) -> float:
    return _scalaire("vesuve_longueur_tenable", "longueur tenable", demi_feuillet, sigma)


def dispersion_de_k_rangees(sigma_partage: float, sigma_propre: float, k: int) -> float:
    return _scalaire("vesuve_dispersion_de_k_rangees", "dispersion de k rangées", sigma_partage, sigma_propre, k)


def bruit_propre_du_triangle(v_ij: float, v_ik: float, v_jk: float) -> float:
    return _scalaire("vesuve_bruit_propre_du_triangle", "triangle des bruits propres", v_ij, v_ik, v_jk)


def erreur_dune_dispersion(sigma: float, n: int) -> float:
    return _scalaire("vesuve_erreur_dune_dispersion", "erreur d'une dispersion", sigma, n)


def compte_decisif(garantie: float) -> int:
    r = ctypes.c_int()
    _verifier(_lib.vesuve_compte_decisif(garantie, ctypes.byref(r)), "compte décisif")
    return r.value


def longueur_de_bloc(n: int) -> int:
    r = ctypes.c_int()
    _verifier(_lib.vesuve_longueur_de_bloc(int(n), ctypes.byref(r)), "longueur de bloc")
    return r.value


# ── E7 : juger sans vérité terrain ──────────────────────────────────────────────────────────────

def alpha_de_convergence(e0: float, e1: float, n0: float, n1: float) -> float:
    return _scalaire("vesuve_alpha_de_convergence", "test de convergence", e0, e1, n0, n1)


def coherence(increments) -> float:
    a = _tableau(increments, np.float64)
    return _scalaire("vesuve_coherence", "cohérence", _ptr(a, _pd), int(a.size))


def coherence_corrigee(c: float, n: int) -> float:
    return _scalaire("vesuve_coherence_corrigee", "cohérence corrigée", c, n)


def nombre_de_fresnel(pas_um: float, distance_m: float, energie_kev: float) -> float:
    return _scalaire("vesuve_nombre_de_fresnel", "nombre de Fresnel", pas_um, distance_m, energie_kev)


# ── E4 : le treillis ────────────────────────────────────────────────────────────────────────────

def _bloc(bloc) -> np.ndarray:
    b = _tableau(bloc, np.uint8)
    if b.ndim != 3:
        raise ValueError(f"un chunk est un cube (z, y, x), pas un tableau de forme {b.shape}")
    return b


def filtre_de_texture(bloc, plancher: float = 0.15) -> tuple[int, bool]:
    b = _bloc(bloc)
    couches, retenu = ctypes.c_int(), ctypes.c_int()
    _verifier(_lib.vesuve_filtre_de_texture(_ptr(b, _pu8), *b.shape, plancher, ctypes.byref(couches),
                                            ctypes.byref(retenu)), "filtre de texture")
    return couches.value, bool(retenu.value)


def profils_de_bord(bloc, coupes, largeur: int) -> dict[str, np.ndarray]:
    """Les quatre profils de bord, en sommes entières : (coupes, profondeur) chacun, uint16."""
    b = _bloc(bloc)
    c = _tableau(coupes, np.int32)
    sorties = {k: np.zeros((c.size, b.shape[0]), dtype=np.uint16) for k in ("droit", "gauche", "bas", "haut")}
    _verifier(_lib.vesuve_profils_de_bord(_ptr(b, _pu8), *b.shape, _ptr(c, _pi), int(c.size), int(largeur),
                                          *(_ptr(sorties[k], _pu16) for k in ("droit", "gauche", "bas", "haut"))),
              "profils de bord")
    return sorties


def profil_de_profondeur(bloc) -> np.ndarray:
    b = _bloc(bloc)
    p = np.zeros(b.shape[0], dtype=np.float64)
    _verifier(_lib.vesuve_profil_de_profondeur(_ptr(b, _pu8), *b.shape, _ptr(p, _pd)), "profil de profondeur")
    return p


def pas_dune_coupe(a, b, plage: int) -> tuple[int, bool]:
    x, y = _tableau(a, np.float64), _tableau(b, np.float64)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError(f"deux profils de même longueur, pas {x.shape} et {y.shape}")
    pas, sature = ctypes.c_int(), ctypes.c_int()
    _verifier(_lib.vesuve_pas_dune_coupe(_ptr(x, _pd), _ptr(y, _pd), int(x.size), int(plage),
                                         ctypes.byref(pas), ctypes.byref(sature)), "pas d'une coupe")
    return pas.value, bool(sature.value)


def pas_dune_couture(a, b, lisible, plage: int) -> tuple[float, float, int]:
    """(pas, désaccord, coupes) d'une couture, NON arrondis ; `a` et `b` sont (coupes, profondeur)."""
    x, y = _tableau(a, np.float64), _tableau(b, np.float64)
    m = _tableau(lisible, np.uint8)
    if x.shape != y.shape or x.ndim != 2 or m.shape != (x.shape[0],):
        raise ValueError(f"profils {x.shape} et {y.shape}, masque {m.shape} : formes incompatibles")
    pas, desaccord, coupes = ctypes.c_double(), ctypes.c_double(), ctypes.c_int()
    _verifier(_lib.vesuve_pas_dune_couture(_ptr(x, _pd), _ptr(y, _pd), _ptr(m, _pu8), x.shape[0], x.shape[1],
                                           int(plage), ctypes.byref(pas), ctypes.byref(desaccord),
                                           ctypes.byref(coupes)), "pas d'une couture")
    return pas.value, desaccord.value, coupes.value


# ── E8 : rendre, et valider par l'encre ─────────────────────────────────────────────────────────

def aire_sous_la_courbe(scores, etiquettes) -> float:
    s = _tableau(scores, np.float64).ravel()
    e = _tableau(np.asarray(etiquettes).astype(bool), np.uint8).ravel()
    if s.size != e.size:
        raise ValueError(f"{s.size} scores pour {e.size} étiquettes")
    travail = (_Paire * max(1, s.size))()
    r = ctypes.c_double()
    _verifier(_lib.vesuve_aire_sous_la_courbe(_ptr(s, _pd), _ptr(e, _pu8), s.size, ctypes.cast(travail, ctypes.c_void_p),
                                              ctypes.byref(r)), "aire sous la courbe")
    return r.value


def echantillonner_le_long_des_normales(volume, points, normales, decalages) -> tuple[np.ndarray, np.ndarray]:
    """(sortie, valide) de forme (décalages, points) ; points et normales (n, 3) en (x, y, z)."""
    v = _bloc(volume)
    p, n = _tableau(points, np.float32).reshape(-1, 3), _tableau(normales, np.float32).reshape(-1, 3)
    d = _tableau(decalages, np.float32).ravel()
    if p.shape != n.shape:
        raise ValueError(f"{p.shape[0]} points pour {n.shape[0]} normales")
    sortie = np.zeros((d.size, p.shape[0]), dtype=np.float32)
    valide = np.zeros((d.size, p.shape[0]), dtype=np.uint8)
    _verifier(_lib.vesuve_echantillonner_le_long_des_normales(_ptr(v, _pu8), *v.shape, _ptr(p, _pf), _ptr(n, _pf),
                                                              p.shape[0], _ptr(d, _pf), int(d.size), _ptr(sortie, _pf),
                                                              _ptr(valide, _pu8)), "échantillonnage")
    return sortie, valide.astype(bool)
