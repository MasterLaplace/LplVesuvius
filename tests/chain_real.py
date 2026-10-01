"""What a run of the chain on the real prediction needs, from the research's data: the cache of `m7` chunks served as a bucket,
the reduced mesh of the segment, the published windings."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from vesuve.transport import ABSENT, Response

HERE = Path(__file__).resolve().parent
ZARRAY = (HERE / "data" / "m7_L2.zarray").read_bytes()
URL = "https://cache.invalid/m7-L2.zarr"
TURNS = {0: "20260602225659-5753_0", -1: "20260603005223-5753_-1", -2: "20260603024952-5753_-2",
         -3: "20260603042357-5753_-3", -4: "20260603145540-5753_-4", -5: "20260603190005-5753_-5",
         -6: "20260603185441-5753_-6", -7: "20260602204401-5753_-7"}
FACTOR = 4.0


class CachedBucket:
    """The chunks of `m7` at level 2 the research cached, served under the keys the bucket uses; a chunk it did not cache is
    absent. The research's cache names them `z_y_x.blosc`."""

    def __init__(self, folder: Path):
        self.folder, self.requests = Path(folder), 0

    def close(self) -> None:
        pass

    def get(self, url: str) -> Response:
        key = url.removeprefix(URL + "/")
        if key == "0/.zarray":
            return Response(ZARRAY, None)
        self.requests += 1
        path = self.folder / (key.removeprefix("0/").replace("/", "_") + ".blosc")
        return Response(path.read_bytes(), None) if path.exists() else Response(None, ABSENT)


def reader(data: Path):
    from vesuve.chain.prediction import PredictionReader
    from vesuve.remote_zarr import RemoteArray
    return PredictionReader(RemoteArray(URL, CachedBucket(data / "nappe_paris4" / "m7" / "m7_L2"), 0))


def mesh_of_the_segment(data: Path):
    """The reduced mesh of the segment the seeds are taken on, with its normals: points in voxels of 2.4 µm."""
    import tifffile

    from vesuve.transfer.surfaces import normals
    folder = data / "rendu_spire_voisine" / "le_segment_reduit" / "maillage"
    x, y, z = (tifffile.imread(folder / f"{c}.tif").astype(np.float64) for c in "xyz")
    points = np.stack([x, y, z], axis=-1)
    valid = np.isfinite(points).all(axis=-1) & (x != -1.0) & (y != -1.0) & (z != -1.0)
    n, has_normal = normals(points, valid)
    return points, valid, n, has_normal


def published_turns(data: Path):
    from vesuve.chain.reading import read_turn
    return {rank: read_turn(data / "tours_publies_5753" / name) for rank, name in TURNS.items()}
