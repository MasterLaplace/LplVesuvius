"""E4: the steps of a band, in the very layout of the published bands.

A band is a definition (`direction`, `centre`, `lines`, `start`, `end`); its reading returns `along` (the
steps along each line), `across` (the steps between two neighbouring lines, which check the reading against
the published bands) and `readings` (what each line refused, and why). The indexing and the rounding to four
decimals are those of `deux_chemins_arrivent_ils_sur_la_meme_spire.py:200-263` on the `experimental` branch,
because the hand-free procedure serves a request with published or fresh bands alike: a layout with two
spellings would be two procedures.

⚠⚠ A band is read WHOLE or refused: one chunk lost by the network makes the whole band undecidable, and it
is never published half read.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from vesuve import core
from vesuve.core import Undecidable
from vesuve.lattice.digest import CHUNK_SIDE, CUTS, EDGE_WIDTH, Digest, DigestCache, digest_chunk
from vesuve.lattice.geometry import ROWS
from vesuve.transport import NETWORK

HALF_SHEET = 36  # round(173 / 2.4 / 2): the step's search range AND the certificate's threshold


def _triple(step: float, disagreement: float, cuts: int) -> list:
    return [round(step, 4), round(disagreement, 4), int(cuts)]


def seam(a: Digest, side_a: str, b: Digest, side_b: str, search_range: int = HALF_SHEET) -> list | None:
    """The step between edge `side_a` of a and edge `side_b` of b, or None when it is not readable."""
    if not (a.kept and b.kept):
        return None
    try:
        return _triple(*core.seam_step(a.profile(side_a), b.profile(side_b), [1] * len(CUTS), search_range))
    except Undecidable:
        return None


class BandReader:
    """Reads the chunks of a band in parallel, reduces them to digests, and returns its steps."""

    def __init__(self, array, cache: DigestCache | None, threads: int = 16, journal=None, segment: str = ""):
        self.array, self.cache, self.threads, self.journal, self.segment = array, cache, threads, journal, segment
        self._memory: dict[tuple[int, int], Digest] = {}
        self.chunks_read = 0

    def digest(self, cy: int, cx: int) -> Digest:
        key = (int(cy), int(cx))
        d = self._memory.get(key)
        if d is None and self.cache is not None:
            d = self.cache.read(*key)
        if d is None:
            c = self.array.chunk(0, *key)
            d = digest_chunk(*key, c.block, c.reason, c.retries)
            self.chunks_read += 1
            if self.cache is not None:
                self.cache.write(d)
        self._memory[key] = d
        return d

    def preload(self, positions) -> None:
        missing = [p for p in dict.fromkeys(positions) if p not in self._memory]
        if not missing:
            return
        start, before = time.monotonic(), getattr(self.array.transport, "bytes_read", 0)
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as pool:
                list(pool.map(lambda p: self.digest(*p), missing))
        finally:
            getattr(self.array.transport, "close", lambda: None)()  # the pool's threads are dead
        if self.journal is not None:
            seconds = time.monotonic() - start
            read = getattr(self.array.transport, "bytes_read", 0) - before
            self.journal.info("CHUNKS_READ", count=len(missing), seconds=round(seconds, 2),
                              mb_per_s=round(read / 1e6 / max(seconds, 1e-9), 1), threads=self.threads)

    def _line(self, direction: str, line: int, wanted: list[int]) -> tuple[dict[int, Digest], dict]:
        digests = {v: self.digest(*((line, v) if direction == ROWS else (v, line))) for v in wanted}
        refused: dict[str, int] = {}
        for d in digests.values():
            if not d.kept:
                refused[d.reason] = refused.get(d.reason, 0) + 1
        failures = sum(n for r, n in refused.items() if r.startswith(NETWORK))
        name = "row" if direction == ROWS else "column"
        if failures:
            raise Undecidable(f"{failures} chunks lost by the network on {name} {line}: a line whose wire dropped "
                              f"is not comparable")
        read = sum(1 for d in digests.values() if d.kept)
        if read == 0:
            raise Undecidable(f"{name} {line} is empty: {refused}")
        count = "columns" if direction == ROWS else "rows"
        reading = {"segment": self.segment, "chunk_grid": list(self.array.grid[1:]), name: int(line),
                   "chunk_side": CHUNK_SIDE, "edge_width": EDGE_WIDTH,
                   "cut_rows": list(CUTS), "cut_columns": list(CUTS),
                   f"{count}_requested": len(wanted), f"{count}_read": read,
                   "network_retries": sum(d.retries for d in digests.values()), "refused": refused}
        return digests, reading

    def read(self, band: dict) -> dict:
        """The band as published: {definition, along, across, readings}, keys as strings."""
        direction, lines = band["direction"], [int(x) for x in band["lines"]]
        wanted = list(range(int(band["start"]), int(band["end"]) + 1))
        self.preload([(l, v) if direction == ROWS else (v, l) for l in lines for v in wanted])
        along, across, readings, previous = {}, {}, {}, None
        for l in lines:
            digests, readings[str(l)] = self._line(direction, l, wanted)
            if direction == ROWS:  # along: horizontal, key = left column; across: vertical
                along_ = {v: seam(digests[v], "right", digests[v + 1], "left") for v in wanted if v + 1 in digests}
                if previous is not None:
                    for v in wanted:
                        x = seam(previous[1][v], "bottom", digests[v], "top")
                        if x is not None:
                            across.setdefault(str(previous[0]), {})[str(v)] = x
            else:  # along: vertical, key = upper row; across: horizontal, key = left column
                along_ = {v: seam(digests[v], "bottom", digests[v + 1], "top") for v in wanted if v + 1 in digests}
                if previous is not None:
                    for v in wanted:
                        x = seam(previous[1][v], "right", digests[v], "left")
                        if x is not None:
                            across.setdefault(str(v), {})[str(previous[0])] = x
            along[str(l)] = {str(v): x for v, x in sorted(along_.items()) if x is not None}
            previous = (l, digests)
        across = {r: dict(sorted(s.items(), key=lambda kv: int(kv[0])))
                  for r, s in sorted(across.items(), key=lambda kv: int(kv[0]))}
        return {"direction": direction, "centre": int(band["centre"]), "lines": lines,
                "start": int(band["start"]), "end": int(band["end"]), "along": along, "across": across,
                "readings": readings}
