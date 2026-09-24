"""Une pile de couches rendues autour d'une surface (`NN.tif`), et les vues qu'on en tire."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import tifffile


def les_couches(dossier: Path) -> list[Path]:
    """Les `.tif` d'une pile, triés par leur NUMÉRO : `10.tif` vient après `9.tif`."""
    fs = [p for p in Path(dossier).glob("*.tif") if re.search(r"\d+", p.stem)]
    if not fs:
        raise FileNotFoundError(f"aucune couche NN.tif dans {dossier}")
    return sorted(fs, key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))


def la_couche(chemin: Path, fenetre=None) -> np.ndarray:
    """Une couche, entière ou restreinte à `(r0, c0, cote_r, cote_c)`, en mémoire projetée quand c'est possible."""
    try:
        a = tifffile.memmap(chemin)
    except (ValueError, OSError):  # compressée : il faut la décoder entière
        a = tifffile.imread(chemin)
    if fenetre is None:
        return np.asarray(a)
    r0, c0, h, w = fenetre
    return np.asarray(a[r0:r0 + h, c0:c0 + w])


def la_pile(dossier: Path, fenetre=None, indices=None) -> np.ndarray:
    fs = les_couches(dossier)
    choisies = fs if indices is None else [fs[i] for i in indices]
    return np.stack([la_couche(f, fenetre) for f in choisies])


def le_papyrus(couche: np.ndarray) -> np.ndarray:
    """Ce qui est rendu : un rendu met 0 hors de la surface (`typographie.py:87`)."""
    return np.asarray(couche) > 0


def projection_maximale(pile: np.ndarray) -> np.ndarray:
    """Le maximum le long de la profondeur : « l'encre visible dans le rendu aplati, sans modèle, souvent
    des zones brillantes » (règle de First Letters). Ce n'est pas un détecteur ; c'est une vue."""
    return np.asarray(pile).max(axis=0)
