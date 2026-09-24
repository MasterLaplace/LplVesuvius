"""Les rangées d'écriture, sans lire : une carte d'encre porte-t-elle des lignes, et à quel interligne ?

Port de `src/encre/typographie.py` (`interligne` et ce qu'elle appelle). L'encre est séparée du support par
Otsu sur les seuls pixels de papyrus, la densité d'encre par rangée est rapportée à la surface traversée,
détendancée, puis autocorrélée ; le pic intérieur le plus NET, sur un éventail d'angles, donne l'interligne.
Un pic compte quand sa proéminence dépasse le plancher DÉRIVÉ du bruit blanc :

    plancher = 2 × √(2 ln k) / √n

⚠ C'est un contrôle nécessaire, jamais suffisant : une prédiction qui échoue n'est certainement pas du
texte, une qui le passe PEUT être un artefact périodique. D'où le mélange, qui doit perdre la période.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage

ANGLES_DEG = tuple(range(-12, 13, 2))
PERIODE_MIN = 8
PERIODE_MAX_PART = 0.25
FACTEUR_BRUIT = 2.0


def binariser_encre(img: np.ndarray, masque: np.ndarray) -> np.ndarray:
    """L'encre contre le support, par Otsu sur les seuls pixels de papyrus (`img` en 0..255)."""
    vals = img[masque]
    if vals.size < 64:
        return np.zeros_like(masque)
    hist = np.bincount(vals.astype(np.int64), minlength=256)[:256].astype(float)
    total = hist.sum()
    if total == 0:
        return np.zeros_like(masque)
    niveaux = np.arange(256, dtype=float)
    poids0 = np.cumsum(hist)
    poids1 = total - poids0
    somme = np.cumsum(hist * niveaux)
    ok = (poids0 > 0) & (poids1 > 0)
    moy0 = np.where(ok, somme / np.maximum(poids0, 1.0), 0.0)
    moy1 = np.where(ok, (somme[-1] - somme) / np.maximum(poids1, 1.0), 0.0)
    variance = np.where(ok, poids0 * poids1 * (moy0 - moy1) ** 2, -1.0)
    return masque & (img > int(np.argmax(variance)))


def _profil(binaire: np.ndarray, masque: np.ndarray, angle_deg: float):
    if abs(angle_deg) > 1e-9:
        b = ndimage.rotate(binaire.astype(np.float32), angle_deg, order=0, reshape=False, mode="constant", cval=0.0)
        m = ndimage.rotate(masque.astype(np.float32), angle_deg, order=0, reshape=False, mode="constant", cval=0.0)
    else:
        b, m = binaire.astype(np.float32), masque.astype(np.float32)
    surf, encre = m.sum(axis=1), b.sum(axis=1)
    garde = surf > (0.60 * max(surf.max(), 1.0))  # une rangée de bord ne fabrique pas de pic
    if garde.sum() < 4 * PERIODE_MIN:
        return None
    return encre[garde] / surf[garde]


def plancher_de_bruit(n: int, k: int) -> float:
    if n < 4 or k < 2:
        return float("inf")
    return FACTEUR_BRUIT * math.sqrt(2.0 * math.log(k)) / math.sqrt(n)


def _detendancer(profil: np.ndarray, largeur: int) -> np.ndarray:
    largeur = max(3, int(largeur) | 1)
    if profil.size <= largeur:
        return profil - profil.mean()
    tendance = np.convolve(profil, np.ones(largeur) / largeur, mode="same")
    demi = largeur // 2
    if demi:
        tendance[:demi] = profil[:largeur].mean()
        tendance[-demi:] = profil[-largeur:].mean()
    return profil - tendance


def _autocorrelation(profil: np.ndarray):
    x = profil - profil.mean()
    n = x.size
    if n < 4 * PERIODE_MIN or float(np.dot(x, x)) <= 0:
        return None
    ac = np.correlate(x, x, mode="full")[n - 1:]
    return ac / ac[0]


def interligne(binaire: np.ndarray, masque: np.ndarray) -> dict:
    """{période en pixels, netteté, plancher, angle, périodique} : le couple période-netteté est la mesure."""
    meilleur = {"periode_px": None, "nettete": 0.0, "angle_deg": None}
    for angle in ANGLES_DEG:
        prof = _profil(binaire, masque, angle)
        if prof is None:
            continue
        haut = max(PERIODE_MIN + 1, int(len(prof) * PERIODE_MAX_PART))
        ac = _autocorrelation(_detendancer(prof, haut))
        if ac is None:
            continue
        fenetre = ac[PERIODE_MIN:haut]
        if fenetre.size < 3:
            continue
        i = int(np.argmax(fenetre))
        if i == 0 or i >= fenetre.size - 1:  # un pic au bord est une marche, pas une période
            continue
        nettete = float(fenetre[i]) - max(float(fenetre[:i].min()), float(fenetre[i:].min()))
        if nettete > meilleur["nettete"]:
            meilleur = {"periode_px": int(i + PERIODE_MIN), "nettete": nettete,
                        "plancher": plancher_de_bruit(len(prof), fenetre.size), "angle_deg": float(angle)}
    meilleur.setdefault("plancher", None)
    meilleur["periodique"] = bool(meilleur["plancher"] is not None and meilleur["nettete"] >= meilleur["plancher"])
    return meilleur


def melanger(binaire: np.ndarray, masque: np.ndarray, graine: int) -> np.ndarray:
    """Les mêmes pixels d'encre, redistribués au hasard DANS le papyrus : la distribution reste, la structure
    part. Un interligne qui survit au mélange n'était pas une écriture."""
    rng = np.random.default_rng(int(graine))
    out = np.zeros_like(binaire)
    ou = np.flatnonzero(masque.ravel())
    vals = binaire.ravel()[ou].copy()
    rng.shuffle(vals)
    out.ravel()[ou] = vals
    return out


def linclinaison_des_rangees(binaire: np.ndarray, masque: np.ndarray, pas: float = 0.5) -> float:
    """L'angle où les rangées sont horizontales : celui qui maximise la variance du profil de projection
    (la méthode standard d'estimation de l'inclinaison d'une page, Postl 1986, Baird 1987).

    ⚠ Ce n'est PAS l'angle de `interligne`, et la différence est mesurée : sa netteté est une
    autocorrélation NORMALISÉE, donc invariante d'échelle ; une page inclinée de 6° reste périodique à tous
    les angles et `interligne` peut répondre 0°. Pour décider « périodique ou non », c'est sans conséquence ;
    pour TRACER des lignes, il faut l'angle où leur contraste est le plus fort, et c'est celui-ci.
    """
    meilleur, var_m = 0.0, -1.0
    for angle in np.arange(ANGLES_DEG[0], ANGLES_DEG[-1] + 1e-9, pas):
        prof = _profil(binaire, masque, float(angle))
        if prof is None:
            continue
        v = float(np.var(_detendancer(prof, max(PERIODE_MIN + 1, int(len(prof) * PERIODE_MAX_PART)))))
        if v > var_m:
            meilleur, var_m = float(angle), v
    return meilleur


def les_rangees(binaire: np.ndarray, masque: np.ndarray, mesure: dict) -> np.ndarray:
    """Le tracé des rangées trouvées : un masque de lignes, dans le repère de l'image.

    Les lignes sont posées là où la densité détendancée culmine, espacées d'au moins les trois cinquièmes de
    l'interligne, dans le repère TOURNÉ où la mesure les a trouvées, puis ramenées par la rotation inverse de
    la même fonction : aucune convention de signe à deviner.
    """
    h, w = binaire.shape
    trace = np.zeros((h, w), dtype=bool)
    if not mesure.get("periodique"):
        return trace
    angle, periode = linclinaison_des_rangees(binaire, masque), int(mesure["periode_px"])
    b = ndimage.rotate(binaire.astype(np.float32), angle, order=0, reshape=False, mode="constant", cval=0.0)
    m = ndimage.rotate(masque.astype(np.float32), angle, order=0, reshape=False, mode="constant", cval=0.0)
    surf, encre = m.sum(axis=1), b.sum(axis=1)
    garde = surf > (0.60 * max(surf.max(), 1.0))
    rangs = np.flatnonzero(garde)
    if rangs.size < 4 * PERIODE_MIN:
        return trace
    prof = _detendancer(encre[garde] / surf[garde], max(PERIODE_MIN + 1, int(rangs.size * PERIODE_MAX_PART)))
    pics, dernier = [], -10 ** 9
    for i in np.argsort(-prof):
        if all(abs(int(i) - p) >= 0.6 * periode for p in pics) and prof[i] > 0:
            pics.append(int(i))
    lignes = np.zeros((h, w), dtype=np.float32)
    for p in pics:
        r = int(rangs[p])
        lignes[max(0, r - 1):r + 2, :] = 1.0
    retour = ndimage.rotate(lignes, -angle, order=0, reshape=False, mode="constant", cval=0.0) > 0.5
    return retour & masque
