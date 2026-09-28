"""E4: reading a band, offline on a made volume, then against a published band."""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import MEASURES, network, research
from vesuve.core import Undecidable
from vesuve.journal import Journal
from vesuve.lattice.digest import DigestCache
from vesuve.lattice.reading import BandReader
from vesuve.remote_zarr import BUCKET, RemoteArray
from vesuve.research import to_english
from vesuve.transport import ABSENT, InMemoryTransport, Transport

URL = "https://example.invalid/volume.zarr"
NZ, SIDE = 109, 128


def _chunk(cy: int, cx: int) -> bytes:
    """A chunk whose sheet goes down 3 layers per column and up 2 per row."""
    z = np.arange(NZ)[:, None, None]
    y = np.arange(SIDE)[None, :, None]
    centre = 40 + 3 * cx - 2 * cy
    v = 110 + 100 * np.exp(-((z - centre) / 2.5) ** 2) + 30 * np.sin(y / 3.0) + 0 * np.arange(SIDE)[None, None, :]
    return np.clip(np.round(v), 0, 255).astype(np.uint8).tobytes()


def _volume(absent=(), failures=()):
    meta = {"shape": [NZ, 5 * SIDE, 6 * SIDE], "chunks": [NZ, SIDE, SIDE], "dtype": "|u1",
            "compressor": None, "dimension_separator": "/", "fill_value": 0, "order": "C", "zarr_format": 2}
    bodies = {f"{URL}/0/.zarray": json.dumps(meta).encode()}
    for cy in range(5):
        for cx in range(6):
            key = f"{URL}/0/0/{cy}/{cx}"
            if (cy, cx) in failures:
                bodies[key] = None
            elif (cy, cx) not in absent:
                bodies[key] = _chunk(cy, cx)
    return RemoteArray(URL, InMemoryTransport(bodies))


BAND = {"direction": "rows", "centre": 2, "lines": [1, 2, 3], "start": 0, "end": 5}


def test_a_band_returns_the_steps_of_the_made_volume():
    read = BandReader(_volume(), None, threads=4).read(BAND)
    assert set(read["along"]) == {"1", "2", "3"}
    for line in read["along"].values():
        assert set(line) == {"0", "1", "2", "3", "4"}  # five seams between six columns
        assert all(x == [3.0, 0.0, 16] for x in line.values())
    assert set(read["across"]) == {"1", "2"}  # between lines 1-2 and 2-3, key = upper row
    assert all(x == [-2.0, 0.0, 16] for s in read["across"].values() for x in s.values())


def test_a_column_reads_the_other_way():
    band = {"direction": "columns", "centre": 2, "lines": [1, 2, 3], "start": 0, "end": 4}
    read = BandReader(_volume(), None, threads=4).read(band)
    assert all(x == [-2.0, 0.0, 16] for s in read["along"].values() for x in s.values())
    assert set(read["along"]["2"]) == {"0", "1", "2", "3"}
    # across a band of columns: key = row, then left column
    assert set(read["across"]) == {"0", "1", "2", "3", "4"}
    assert all(x == [3.0, 0.0, 16] for s in read["across"].values() for x in s.values())


def test_an_absent_chunk_is_counted_and_cuts_its_two_seams():
    read = BandReader(_volume(absent={(2, 3)}), None, threads=4).read(BAND)
    assert read["readings"]["2"]["refused"] == {ABSENT: 1}
    assert set(read["along"]["2"]) == {"0", "1", "4"}
    assert "3" not in read["across"]["1"] and "3" not in read["across"]["2"]


def test_a_dropped_wire_refuses_the_whole_band():
    with pytest.raises(Undecidable, match="network"):
        BandReader(_volume(failures={(3, 1)}), None, threads=4).read(BAND)


def test_the_cache_serves_a_chunk_without_reading_it_again(tmp_path):
    t = _volume()
    cache = DigestCache(tmp_path, URL)
    first = BandReader(t, cache, threads=4).read(BAND)
    before = len(t.transport.requests)
    second = BandReader(t, cache, threads=4)
    assert second.read(BAND) == first
    assert len(t.transport.requests) == before and second.chunks_read == 0


def test_a_failure_is_never_cached(tmp_path):
    cache = DigestCache(tmp_path, URL)
    with pytest.raises(Undecidable):
        BandReader(_volume(failures={(3, 1)}), cache, threads=4).read(BAND)
    assert cache.read(3, 1) is None and cache.read(3, 0) is not None


# ── against a published band, on the real volume ─────────────────────────────────────────────

def _smallest_published_band():
    from la_couverture_sans_main import LES_LECTURES_PUBLIEES
    best = None
    for path in LES_LECTURES_PUBLIEES:
        for b in (json.loads(path.read_text()).get("les_bandes") or {}).values():
            n = len(b["les_lignes"]) * (int(b["a"]) - int(b["de"]) + 1)
            if len(b["les_lignes"]) >= 3 and int(b["a"]) - int(b["de"]) >= 8 and (best is None or n < best[0]):
                best = (n, b)
    return to_english(best[1])


@research
@network
def test_a_published_band_reads_again_identically(tmp_path):
    published = _smallest_published_band()
    key = next(l.split("\t")[1] for l in (MEASURES / "volumes_surface_PHercParis4.txt").read_text().splitlines()
               if l.startswith("20230702185753\t") and "/2.4um-" in l)
    t = RemoteArray(f"{BUCKET}/{key}", Transport())
    read = BandReader(t, DigestCache(tmp_path, t.url), threads=16, journal=Journal()).read(published)
    assert read["along"] == published["along"]
    assert read["across"] == published["across"]
    for line, reading in published["readings"].items():
        assert read["readings"][line]["refused"] == reading["refused"]
