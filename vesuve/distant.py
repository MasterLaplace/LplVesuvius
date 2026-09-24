"""Un fichier du bucket public, lu une fois et gardé sur disque : une carte d'encre, un tifxyz."""
from __future__ import annotations

import hashlib
from pathlib import Path

from vesuve.transport import Transport
from vesuve.zarr_distant import LE_BUCKET


class Indisponible(RuntimeError):
    """Le fichier n'a pas pu être obtenu ; le message dit s'il est absent ou si le fil est tombé."""


class Distant:
    def __init__(self, cache: Path, transport=None, bucket: str = LE_BUCKET):
        self.cache, self.transport, self.bucket = Path(cache) / "fichiers", transport or Transport(), bucket
        self.cache.mkdir(parents=True, exist_ok=True)

    def url(self, chemin: str) -> str:
        return f"{self.bucket}/{chemin.lstrip('/')}"

    def octets(self, chemin: str) -> bytes:
        f = self.cache / hashlib.sha1(chemin.encode()).hexdigest()
        if f.exists():
            return f.read_bytes()
        r = self.transport.get(self.url(chemin))
        if r.corps is None:
            raise Indisponible(f"{chemin} : {r.raison}")
        tmp = f.with_suffix(".tmp")
        tmp.write_bytes(r.corps)
        tmp.replace(f)
        return r.corps

    def dossier_tifxyz(self, chemin: str) -> Path:
        """Les quatre fichiers d'un tifxyz, copiés sous le cache : un dossier que `tifxyz.lire` ouvre."""
        d = self.cache / ("tifxyz-" + hashlib.sha1(chemin.encode()).hexdigest()[:16])
        d.mkdir(exist_ok=True)
        for nom in ("meta.json", "x.tif", "y.tif", "z.tif"):
            if not (d / nom).exists():
                (d / nom).write_bytes(self.octets(f"{chemin.rstrip('/')}/{nom}"))
        return d
