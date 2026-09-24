"""Un tableau OME-Zarr lu à distance, chunk par chunk, sans jamais le rapatrier en entier.

Ce que ce module garde du lecteur du producteur (`src/commun/zarr_depth.py`) : la clé qui suit le
séparateur DÉCLARÉ (un `/` codé en dur envoie vers des clés inexistantes, qu'on compterait comme des
chunks absents), et le refus de confondre « je ne sais pas décompresser » avec « ce chunk n'existe
pas ».
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from vesuve.transport import ABSENT, Reponse

LE_BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


class CodecIndisponible(RuntimeError):
    """Le chunk est là et cette machine ne sait pas le décompresser : jamais un fait sur le rouleau."""


@dataclass(frozen=True)
class Chunk:
    bloc: np.ndarray | None  # (z, y, x) quand il est lu
    raison: str | None       # « absent du dépôt », « illisible », « le réseau a échoué : … »
    reprises: int = 0


class TableauDistant:
    """Le niveau `niveau` d'un tableau zarr v2 sous `url`, avec le transport qu'on lui donne."""

    def __init__(self, url: str, transport, niveau: int = 0):
        self.url, self.transport, self.niveau = url.rstrip("/"), transport, niveau
        r = transport.get(f"{self.url}/{niveau}/.zarray")
        if r.corps is None:
            raise RuntimeError(f"pas de .zarray au niveau {niveau} sous {self.url} : {r.raison}")
        self.meta = json.loads(r.corps)
        self.forme = tuple(int(x) for x in self.meta["shape"])
        self.chunks = tuple(int(x) for x in self.meta["chunks"])
        self.dtype = np.dtype(self.meta["dtype"])
        self.separateur = self.meta.get("dimension_separator", ".")
        self.codec = (self.meta.get("compressor") or {}).get("id")
        if self.codec not in (None, "blosc", "zstd"):
            raise CodecIndisponible(f"compresseur « {self.codec} » non géré")

    @property
    def grille(self) -> tuple[int, ...]:
        """Le nombre de chunks par axe, bords partiels compris."""
        return tuple(-(-n // c) for n, c in zip(self.forme, self.chunks))

    def cle(self, *indices: int) -> str:
        return f"{self.niveau}/" + self.separateur.join(str(int(i)) for i in indices)

    def _decoder(self, corps: bytes) -> bytes:
        if self.codec is None:
            return corps
        import numcodecs
        codec = numcodecs.Blosc() if self.codec == "blosc" else numcodecs.Zstd()
        return codec.decode(corps)

    def chunk(self, *indices: int) -> Chunk:
        r: Reponse = self.transport.get(f"{self.url}/{self.cle(*indices)}")
        if r.corps is None:
            return Chunk(None, r.raison or ABSENT, r.reprises)
        attendu = int(np.prod(self.chunks)) * self.dtype.itemsize
        try:
            brut = self._decoder(r.corps)
        except ImportError as e:  # la bibliothèque du codec manque ici
            raise CodecIndisponible(str(e)) from e
        except Exception:  # noqa: BLE001 -- des octets que le codec refuse
            return Chunk(None, "illisible", r.reprises)
        if len(brut) != attendu:
            return Chunk(None, "illisible", r.reprises)
        return Chunk(np.frombuffer(brut, dtype=self.dtype).reshape(self.chunks), None, r.reprises)
