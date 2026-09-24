"""Le format tifxyz : trois images float32 (x, y, z) d'une grille de surface, et son `meta.json`.

Le contrat est celui que `villa` lit (`lasagna/approval_inpaint.py:_load_tifxyz_arrays`) : trois tifs 2D de
même forme, `meta.json` avec `format`, `scale`, `bbox`, `uuid`, `type`, et des canaux optionnels comme
`approval.tif`. ⚠ Un sommet invalide vaut -1 ou n'est pas fini : c'est la sentinelle de VC3D. Le dépôt de
recherche avait deux réponses (-1 dans certains lecteurs, 0 dans d'autres) ; il n'y en a qu'une ici.
"""
from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tifffile

INVALIDE = -1.0


@dataclass
class Surface:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    meta: dict

    @property
    def forme(self) -> tuple[int, int]:
        return self.x.shape

    def valide(self) -> np.ndarray:
        return np.isfinite(self.x) & np.isfinite(self.y) & np.isfinite(self.z) & ~(
            (self.x == INVALIDE) & (self.y == INVALIDE) & (self.z == INVALIDE))


def lire(source, transport=None) -> Surface:
    """Un dossier local, ou une URL lue par `transport` (un dossier du bucket, par exemple)."""
    def octets(nom):
        if transport is None:
            return (Path(source) / nom).read_bytes()
        r = transport.get(f"{str(source).rstrip('/')}/{nom}")
        if r.corps is None:
            raise FileNotFoundError(f"{source}/{nom} : {r.raison}")
        return r.corps
    meta = json.loads(octets("meta.json"))
    x, y, z = (tifffile.imread(io.BytesIO(octets(f"{c}.tif"))).astype(np.float32) for c in "xyz")
    if not (x.shape == y.shape == z.shape and x.ndim == 2):
        raise ValueError(f"x, y, z de formes {x.shape}, {y.shape}, {z.shape} : ce n'est pas un tifxyz")
    return Surface(x, y, z, meta)


def ecrire(surface: Surface, dossier: Path, approbation: np.ndarray | None = None) -> Path:
    """Écrit le tifxyz ; `approbation` (uint8, même forme) devient `approval.tif`, 255 approuvé, 0 sinon."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, a in (("x", surface.x), ("y", surface.y), ("z", surface.z)):
        tifffile.imwrite(dossier / f"{nom}.tif", np.ascontiguousarray(a, dtype=np.float32))
    ok = surface.valide()
    meta = dict(surface.meta)
    if ok.any():
        pts = np.stack([surface.x[ok], surface.y[ok], surface.z[ok]], axis=1)
        meta["bbox"] = [pts.min(axis=0).tolist(), pts.max(axis=0).tolist()]
    meta.setdefault("format", "tifxyz")
    meta.setdefault("type", "seg")
    (dossier / "meta.json").write_text(json.dumps(meta, indent=4))
    if approbation is not None:
        if approbation.shape != surface.forme:
            raise ValueError(f"approbation {approbation.shape} contre surface {surface.forme}")
        tifffile.imwrite(dossier / "approval.tif", np.where(approbation > 0, 255, 0).astype(np.uint8))
    return dossier


def restreindre(surface: Surface, garder: np.ndarray) -> Surface:
    """La même surface, les sommets hors de `garder` mis à la sentinelle."""
    x, y, z = (np.where(garder, a, INVALIDE).astype(np.float32) for a in (surface.x, surface.y, surface.z))
    return Surface(x, y, z, dict(surface.meta))


def masque_de_chunks_vers_grille(masque: np.ndarray, forme: tuple[int, int], cote_du_chunk: int,
                                 echelle: float) -> np.ndarray:
    """Un masque par chunk du volume de surface (cy, cx) porté sur la grille du tifxyz : la cellule (i, j)
    du tifxyz est le pixel (i / échelle, j / échelle) du volume, donc le chunk (i / (échelle × côté), …)."""
    gy, gx = masque.shape
    i = np.minimum((np.arange(forme[0]) / (echelle * cote_du_chunk)).astype(int), gy - 1)
    j = np.minimum((np.arange(forme[1]) / (echelle * cote_du_chunk)).astype(int), gx - 1)
    return masque[np.ix_(i, j)]
