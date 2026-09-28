"""An OME-Zarr array read remotely, chunk by chunk, never fetched whole.

What this module keeps from the research reader (`src/commun/zarr_depth.py` on the `experimental` branch):
the key follows the DECLARED separator (a hard-coded `/` sends requests to keys that do not exist, which would
be counted as absent chunks), and "I cannot decompress" is never confused with "this chunk does not exist".
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from vesuve.transport import ABSENT, Response

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
UNREADABLE = "unreadable"


class CodecUnavailable(RuntimeError):
    """The chunk is there and this machine cannot decompress it: never a fact about the scroll."""


@dataclass(frozen=True)
class Chunk:
    block: np.ndarray | None  # (z, y, x) when read
    reason: str | None        # "absent from the bucket", "unreadable", "the network failed: …"
    retries: int = 0


class RemoteArray:
    """Level `level` of a zarr v2 array under `url`, with the transport it is given."""

    def __init__(self, url: str, transport, level: int = 0):
        self.url, self.transport, self.level = url.rstrip("/"), transport, level
        r = transport.get(f"{self.url}/{level}/.zarray")
        if r.body is None:
            raise RuntimeError(f"no .zarray at level {level} under {self.url}: {r.reason}")
        self.meta = json.loads(r.body)
        self.shape = tuple(int(x) for x in self.meta["shape"])
        self.chunks = tuple(int(x) for x in self.meta["chunks"])
        self.dtype = np.dtype(self.meta["dtype"])
        self.separator = self.meta.get("dimension_separator", ".")
        self.codec = (self.meta.get("compressor") or {}).get("id")
        if self.codec not in (None, "blosc", "zstd"):
            raise CodecUnavailable(f"compressor \"{self.codec}\" not supported")

    @property
    def grid(self) -> tuple[int, ...]:
        """The number of chunks per axis, partial edges included."""
        return tuple(-(-n // c) for n, c in zip(self.shape, self.chunks))

    def key(self, *indices: int) -> str:
        return f"{self.level}/" + self.separator.join(str(int(i)) for i in indices)

    def _decode(self, body: bytes) -> bytes:
        if self.codec is None:
            return body
        import numcodecs
        codec = numcodecs.Blosc() if self.codec == "blosc" else numcodecs.Zstd()
        return codec.decode(body)

    def chunk(self, *indices: int) -> Chunk:
        r: Response = self.transport.get(f"{self.url}/{self.key(*indices)}")
        if r.body is None:
            return Chunk(None, r.reason or ABSENT, r.retries)
        expected = int(np.prod(self.chunks)) * self.dtype.itemsize
        try:
            raw = self._decode(r.body)
        except ImportError as e:  # the codec's library is missing here
            raise CodecUnavailable(str(e)) from e
        except Exception:  # noqa: BLE001 -- bytes the codec refuses
            return Chunk(None, UNREADABLE, r.retries)
        if len(raw) != expected:
            return Chunk(None, UNREADABLE, r.retries)
        return Chunk(np.frombuffer(raw, dtype=self.dtype).reshape(self.chunks), None, r.retries)
