"""Les images qu'un pipeline rend : un masque en couleurs, une superposition, une barre d'échelle.

Des PNG et des TIFF écrits par Pillow et tifffile, rien de plus. ⚠ Une image est une VUE : ce qu'un
pipeline conclut est dans son rapport, et une image qu'il faudrait lire pour savoir est un défaut.
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw

# absent, présent non certifié, certifié, suspect (entouré par une boucle qui franchit)
LES_COULEURS = np.array([[18, 18, 24], [92, 96, 110], [70, 190, 140], [230, 120, 60]], dtype=np.uint8)


def masque_en_couleurs(masque: np.ndarray, agrandir: int = 2) -> Image.Image:
    rgb = LES_COULEURS[np.clip(masque, 0, len(LES_COULEURS) - 1)]
    im = Image.fromarray(rgb, "RGB")
    return im.resize((im.width * agrandir, im.height * agrandir), Image.NEAREST)


def superposer(fond: np.ndarray, masque: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Le masque par chunk, étiré à la taille du fond (une carte d'encre, un rendu), en transparence."""
    f = np.asarray(fond, dtype=np.float32)
    if f.ndim == 3:
        f = f.mean(axis=2)
    bas, haut = np.percentile(f, [1, 99])
    g = np.clip((f - bas) / max(haut - bas, 1e-9), 0, 1)
    base = np.stack([g * 255] * 3, axis=-1)
    m = np.asarray(Image.fromarray(masque.astype(np.uint8)).resize((f.shape[1], f.shape[0]), Image.NEAREST))
    teinte = LES_COULEURS[np.clip(m, 0, len(LES_COULEURS) - 1)].astype(np.float32)
    colore = m >= 2
    base[colore] = (1 - alpha) * base[colore] + alpha * teinte[colore]
    return Image.fromarray(base.astype(np.uint8), "RGB")


def niveaux(image: np.ndarray, bas_pct: float = 1.0, haut_pct: float = 99.0) -> Image.Image:
    """Une image en niveaux de gris, étirée entre deux percentiles (`couche_de_rendu.py:35` : 1 et 99)."""
    a = np.asarray(image, dtype=np.float32)
    ok = np.isfinite(a)
    bas, haut = np.percentile(a[ok], [bas_pct, haut_pct]) if ok.any() else (0.0, 1.0)
    g = np.clip((np.where(ok, a, bas) - bas) / max(haut - bas, 1e-9), 0, 1)
    return Image.fromarray((g * 255).astype(np.uint8), "L")


def barre_dechelle(im: Image.Image, pixel_um: float, longueur_mm: float = 10.0) -> Image.Image:
    """Une barre de `longueur_mm` en bas à gauche, comme First Letters l'exige (1 cm)."""
    im = im.convert("RGB")
    n = int(round(longueur_mm * 1000.0 / pixel_um))
    d = ImageDraw.Draw(im)
    h = max(4, im.height // 150)
    x0, y0 = im.width // 40, im.height - im.height // 30 - h
    d.rectangle([x0, y0, x0 + n, y0 + h], fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((x0, y0 - 14), f"{longueur_mm:g} mm", fill=(255, 255, 255))
    return im


def lire_une_image(octets: bytes) -> np.ndarray:
    Image.MAX_IMAGE_PIXELS = None  # une carte d'encre d'un segment dépasse la garde anti-bombe de Pillow
    return np.asarray(Image.open(io.BytesIO(octets)).convert("L"))


LES_ETATS = {"dessous": (70, 190, 140), "franchit": (230, 120, 60), "à lire": (120, 170, 230),
             "non vue": (200, 200, 90), "ouverte": (180, 90, 180)}


def dessiner_les_boucles(im: Image.Image, journal, pixels_par_chunk: float, epaisseur: int = 2) -> Image.Image:
    """Le contour de chaque boucle du journal, de la couleur de son état : ce qui tient, ce qui franchit,
    et ce qui reste à lire. Une boucle est dessinée à ses coins ; la légende est dans le rapport."""
    im = im.convert("RGB")
    d = ImageDraw.Draw(im)
    ordre = {"à lire": 0, "ouverte": 1, "non vue": 1, "franchit": 2, "dessous": 3}
    for e in sorted(journal, key=lambda e: ordre.get(e.get("letat"), 0)):
        co, etat = e.get("les_coins"), e.get("letat")
        if not co or etat not in LES_ETATS:
            continue
        r0, r1, c0, c1 = co
        k = pixels_par_chunk
        d.rectangle([c0 * k, r0 * k, (c1 + 1) * k - 1, (r1 + 1) * k - 1], outline=LES_ETATS[etat],
                    width=epaisseur + (1 if etat in ("dessous", "franchit") else 0))
    return im
