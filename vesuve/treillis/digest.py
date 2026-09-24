"""Le digest d'un chunk : tout ce que la lecture du pas regarde, et rien d'autre.

Un chunk de surface fait 109 × 128 × 128 octets (1,78 Mo). Le pas n'en regarde que les bords : seize
coupes, seize voxels de large, sur les quatre côtés. Le digest garde ces bords en SOMMES entières
(4 × 16 × 109 × 2 octets = 14 Ko), le verdict du filtre de texture et le profil de profondeur. Une
somme divisée par seize rend exactement la moyenne du producteur, donc aucun nombre ne bouge ; et un
chunk lu une fois ne se relit plus, quelle que soit la bande qui le redemande.
"""
from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from vesuve import noyau

LE_COTE = 128
LES_COUPES = tuple(LE_COTE * (2 * i + 1) // (2 * 16) for i in range(16))  # 4, 12, …, 124 (`204`:69)
LA_LARGEUR_DU_BORD = 16    # `199`:67, dérivée d'un méandre médian de 5 voxels
LE_PLANCHER_DE_COHERENCE = 0.15  # `la_recette_posee_sur_le_rouleau.py:62`
VIDE, TROP_PEU_TEXTURE = "vide", "trop peu texturé"


@dataclass(frozen=True)
class Digest:
    cy: int
    cx: int
    raison: str | None  # None : retenu
    reprises: int = 0
    droit: np.ndarray | None = None   # (16, profondeur) uint16
    gauche: np.ndarray | None = None
    bas: np.ndarray | None = None
    haut: np.ndarray | None = None
    profondeur: np.ndarray | None = None  # (profondeur,) moyenne par couche

    @property
    def retenu(self) -> bool:
        return self.raison is None

    def profil(self, cote: str) -> np.ndarray:
        """Les seize profils d'un bord, en MOYENNES : la forme que `un_pas` reçoit."""
        return getattr(self, cote).astype(np.float64) / LA_LARGEUR_DU_BORD


def digerer(cy: int, cx: int, bloc: np.ndarray | None, raison: str | None, reprises: int = 0) -> Digest:
    """Le filtre du producteur, dans son ordre : absent, vide, trop peu texturé, puis les bords."""
    if bloc is None:
        return Digest(cy, cx, raison, reprises)
    if int(bloc.max()) <= 0:
        return Digest(cy, cx, VIDE, reprises)
    _, retenu = noyau.filtre_de_texture(bloc, LE_PLANCHER_DE_COHERENCE)
    if not retenu:
        return Digest(cy, cx, TROP_PEU_TEXTURE, reprises)
    bords = noyau.profils_de_bord(bloc, LES_COUPES, LA_LARGEUR_DU_BORD)
    return Digest(cy, cx, None, reprises, profondeur=noyau.profil_de_profondeur(bloc), **bords)


class CacheDeDigests:
    """Un digest par fichier, sous un dossier par volume. ⚠ Une panne de réseau ne se met jamais en
    cache : elle dit quelque chose du fil, pas du chunk."""

    def __init__(self, racine: Path, url_du_volume: str):
        cle = hashlib.sha1(url_du_volume.encode()).hexdigest()[:16]
        self.dossier = Path(racine) / cle
        self.dossier.mkdir(parents=True, exist_ok=True)
        (self.dossier / "VOLUME").write_text(url_du_volume + "\n")

    def _chemin(self, cy: int, cx: int) -> Path:
        return self.dossier / f"{cy}_{cx}.npz"

    def lire(self, cy: int, cx: int) -> Digest | None:
        p = self._chemin(cy, cx)
        if not p.exists():
            return None
        with np.load(p, allow_pickle=False) as z:
            raison = str(z["raison"]) or None
            if raison is not None:
                return Digest(cy, cx, raison)
            return Digest(cy, cx, None, 0, *(z[k] for k in ("droit", "gauche", "bas", "haut", "profondeur")))

    def ecrire(self, d: Digest) -> None:
        if d.raison is not None and d.raison not in (VIDE, TROP_PEU_TEXTURE, "absent du dépôt", "illisible"):
            return
        tampon = io.BytesIO()
        champs = {"raison": np.array(d.raison or "")}
        if d.retenu:
            champs.update({k: getattr(d, k) for k in ("droit", "gauche", "bas", "haut", "profondeur")})
        np.savez_compressed(tampon, **champs)
        tmp = self._chemin(d.cy, d.cx).with_suffix(".tmp")
        tmp.write_bytes(tampon.getvalue())
        tmp.replace(self._chemin(d.cy, d.cx))
