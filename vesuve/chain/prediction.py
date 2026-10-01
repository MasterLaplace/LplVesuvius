"""Reading the prediction `m7` at integer indices, chunk by chunk, for the chain.

The chain reads the prediction along thousands of short rays, a few hundred points at a time, over a region that a few
hundred chunks cover; the same chunk is asked for again and again. The reader keeps the last decoded chunks, and, as the
rest of the program does, never takes an unreadable chunk for an empty one.
"""
from __future__ import annotations

from collections import OrderedDict

import numpy as np

from vesuve.remote_zarr import RemoteArray
from vesuve.transport import ABSENT

KEPT_CHUNKS = 16


class PredictionReader:
    """`read_values(index)` for a `RemoteArray`: the value at each (z, y, x) index, zero outside the array and in a chunk the
    bucket does not hold; a chunk that cannot be read stops the reading with its reason."""

    def __init__(self, array: RemoteArray, kept: int = KEPT_CHUNKS):
        self.array, self.kept = array, kept
        self._chunks: OrderedDict[tuple, np.ndarray | None] = OrderedDict()
        self.reads = 0

    def _chunk(self, key: tuple) -> np.ndarray | None:
        if key in self._chunks:
            self._chunks.move_to_end(key)
            return self._chunks[key]
        got = self.array.chunk(*key)
        if got.block is None and got.reason != ABSENT:
            raise RuntimeError(f"chunk {key} of {self.array.url} could not be read: {got.reason}")
        self.reads += 1
        self._chunks[key] = got.block
        if len(self._chunks) > self.kept:
            self._chunks.popitem(last=False)
        return got.block

    def __call__(self, index: np.ndarray) -> np.ndarray:
        shape, chunks = np.asarray(self.array.shape), np.asarray(self.array.chunks)
        flat = index.reshape(-1, 3)
        values = np.zeros(len(flat), dtype=self.array.dtype)
        inside = np.flatnonzero(np.all((flat >= 0) & (flat < shape), axis=1))
        if len(inside):
            keys = flat[inside] // chunks
            unique, which = np.unique(keys, axis=0, return_inverse=True)
            order = np.argsort(which.ravel(), kind="stable")
            members = np.split(inside[order], np.flatnonzero(np.diff(which.ravel()[order])) + 1)
            for key, group in zip(unique, members):
                block = self._chunk(tuple(int(k) for k in key))
                if block is not None:
                    local = flat[group] - key * chunks
                    values[group] = block[local[:, 0], local[:, 1], local[:, 2]]
        return values.reshape(index.shape[:-1])
