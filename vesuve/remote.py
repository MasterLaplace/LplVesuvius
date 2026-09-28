"""A file of the public bucket, read once and kept on disk: an ink map, a tifxyz."""
from __future__ import annotations

import hashlib
from pathlib import Path

from vesuve.remote_zarr import BUCKET
from vesuve.transport import Transport


class Unavailable(RuntimeError):
    """The file could not be obtained; the message says whether it is absent or the wire dropped."""


class Remote:
    def __init__(self, cache: Path, transport=None, bucket: str = BUCKET):
        self.cache, self.transport, self.bucket = Path(cache) / "files", transport or Transport(), bucket
        self.cache.mkdir(parents=True, exist_ok=True)

    def url(self, path: str) -> str:
        return f"{self.bucket}/{path.lstrip('/')}"

    def fetch(self, path: str) -> bytes:
        f = self.cache / hashlib.sha1(path.encode()).hexdigest()
        if f.exists():
            return f.read_bytes()
        r = self.transport.get(self.url(path))
        if r.body is None:
            raise Unavailable(f"{path}: {r.reason}")
        tmp = f.with_suffix(".tmp")
        tmp.write_bytes(r.body)
        tmp.replace(f)
        getattr(self.transport, "close", lambda: None)()
        return r.body

    def tifxyz_folder(self, path: str) -> Path:
        """The four files of a tifxyz, copied under the cache: a folder `tifxyz.read` opens."""
        d = self.cache / ("tifxyz-" + hashlib.sha1(path.encode()).hexdigest()[:16])
        d.mkdir(exist_ok=True)
        for name in ("meta.json", "x.tif", "y.tif", "z.tif"):
            if not (d / name).exists():
                (d / name).write_bytes(self.fetch(f"{path.rstrip('/')}/{name}"))
        return d
