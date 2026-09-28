"""The step tables of the correction, made here: mirror, render, read, row of blocks by row of blocks.

For each candidate block and each of the two surfaces, a pile is rendered from the local mirror and its step table
is read. Nothing of a whole segment fits on a disk at once (the mirror alone would be hundreds of gigabytes), so the
work goes one ROW of blocks at a time:

1. the chunks of the row are downloaded, and those it does not read are dropped;
2. the piles of the row are rendered;
3. the tables of the PREVIOUS row are read: a table needs the pile to its south, which only exists now;
4. the piles of the row read, nothing asks for them any more: they are removed, unless `keep_piles`.

A table already on disk is not redone, and a table read without a neighbour that later became rendered is redone:
it would miss the seams to it. The work stops cleanly, and says why, as soon as a disk runs short.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from vesuve.transfer import mirror as mirror_
from vesuve.transfer import rendering, steps, surfaces

BLOCK = 16
FREE_GB = 40.0


def short_of_space(disks, threshold_gb: float = FREE_GB) -> str | None:
    """None while every disk keeps more than `threshold_gb` GB free; otherwise which one, and how much it has left.

    ⚠⚠ Under WSL, `/` is a virtual disk declared larger than the Windows disk that holds it: it announces room that
    `C:` does not have, and `C:` is what fills up. On 2026-09-28 a render filled it and brought the machine down while
    `/` still announced 278 GB free. Each disk is watched, and the first one short stops the work.
    """
    for d in disks:
        if Path(d).is_dir():
            free = shutil.disk_usage(d).free / 1e9
            if free < threshold_gb:
                return f"{d} has only {free:.1f} GB free, under the threshold of {threshold_gb:g} GB"
    return None


class TableMaker:
    """The piles and tables of one surface under test, in `work`."""

    def __init__(self, work: Path, meshes: dict[str, Path], candidates, volume: str, transport=None, journal=None,
                 disks=None, keep_piles: bool = False, threads: int = 16):
        self.work, self.meshes, self.candidates = Path(work), dict(meshes), set(candidates)
        self.mirror = mirror_.Mirror(self.work / "mirror", volume, transport, journal)
        self.journal, self.keep_piles, self.threads = journal, keep_piles, threads
        self.disks = tuple(disks) if disks is not None else tuple(p for p in (self.work, Path("/mnt/c")) if p.exists())
        self._points = {}
        for s, m in self.meshes.items():
            points, _, spacing = surfaces.read_points(m)
            self._points[s] = (points, spacing)

    def pile(self, s: str, by: int, bx: int) -> Path:
        return self.work / "piles" / s / f"block_{by}_{bx}"

    def table_path(self, s: str, by: int, bx: int) -> Path:
        return self.work / "tables" / s / f"block_{by}_{bx}.json"

    def needs(self, s: str, by: int, bx: int) -> set:
        points, spacing = self._points[s]
        return mirror_.chunks_of_crop(points, spacing, rendering.crop(by, bx, BLOCK))

    def _note(self, event: str, **fields) -> None:
        if self.journal is not None:
            self.journal.info(event, **fields)

    def _has_pile(self, s: str, b: tuple[int, int]) -> bool:
        return b in self.candidates and rendering.is_complete(self.pile(s, *b))

    def table(self, s: str, by: int, bx: int) -> dict | None:
        f = self.table_path(s, by, bx)
        return json.loads(f.read_text()) if f.is_file() else None

    def _table_from_piles(self, s: str, by: int, bx: int) -> dict:
        east, south = self._has_pile(s, (by, bx + BLOCK)), self._has_pile(s, (by + BLOCK, bx))
        old = self.table(s, by, bx)
        if old is not None and old["east"] == east and old["south"] == south:
            return old
        piles = {(by, bx): rendering.read_pile(self.pile(s, by, bx))}
        if east:
            piles[(by, bx + BLOCK)] = rendering.read_pile(self.pile(s, by, bx + BLOCK))[:, :, :steps.CHUNK]
        if south:
            piles[(by + BLOCK, bx)] = rendering.read_pile(self.pile(s, by + BLOCK, bx))[:, :steps.CHUNK, :]
        t = steps.block_table(steps.chunk_reader(piles), by, bx, east, south)
        f = self.table_path(s, by, bx)
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(t))
        tmp.replace(f)
        return t

    def make(self, stop_after_rows: int | None = None) -> dict:
        """Everything, row by row; `stop_after_rows` bounds a trial run."""
        start = time.monotonic()
        rows = sorted({by for by, _ in self.candidates})
        if stop_after_rows is not None:
            rows = rows[:int(stop_after_rows)]
        self._to_render = {r: self._piles_to_render(r) for r in rows}
        self._row_needs: dict[int, set] = {}
        done_rows, fills, failed, stopped = [], [], {}, short_of_space(self.disks)
        for r in rows:
            if stopped:
                break
            fill, stopped = self._download_row(r)
            fills += [fill] if fill else []
            if not stopped:
                stopped = self._render_row(r, failed)
            if stopped:
                break
            done_rows.append(r)
            if len(done_rows) >= 2:
                self._tables_of_row(done_rows[-2])
        if not stopped and done_rows:
            self._tables_of_row(done_rows[-1])
        return {"rows": len(rows), "rows_done": len(done_rows), "failed": failed, "stopped": stopped,
                "bytes_downloaded": int(sum(f["bytes"] for f in fills)), "seconds": round(time.monotonic() - start, 1)}

    def _piles_to_render(self, r: int) -> list[tuple[str, tuple[int, int]]]:
        return [(s, b) for b in sorted(b for b in self.candidates if b[0] == r) for s in self.meshes
                if not rendering.is_complete(self.pile(s, *b))]

    def _needs_of_row(self, r: int) -> set:
        if r not in self._row_needs:
            self._row_needs[r] = set().union(*(self.needs(s, *b) for s, b in self._to_render.get(r, [])))
        return self._row_needs[r]

    def _download_row(self, r: int) -> tuple[dict | None, str | None]:
        """The chunks of the row, downloaded; those it does not read, dropped.

        A row shares its upper chunks with the row before it, and only with it (measured on the segment: 153079 chunks
        in all, each read by one row or by two consecutive ones), so dropping everything else loses nothing.
        """
        if not self._to_render[r]:
            return None, None
        wanted = self._needs_of_row(r)
        self.mirror.empty(wanted)
        fill = self.mirror.fill(wanted, self.threads)
        self._note("MIRROR_FILLED", row=r, **{k: v for k, v in fill.items() if k != "failed"}, failed=len(fill["failed"]))
        for earlier in [x for x in self._row_needs if x < r]:
            del self._row_needs[earlier]
        if fill["failed"]:
            return fill, f"row {r}: {len(fill['failed'])} chunks could not be downloaded"
        return fill, None

    def _render_row(self, r: int, failed: dict) -> str | None:
        """The piles of the row, rendered; the reason to stop, if a disk runs short."""
        for s, b in self._to_render[r]:
            stopped = short_of_space(self.disks)
            if stopped:
                return stopped
            got = rendering.render(self.meshes[s], self.pile(s, *b), rendering.crop(*b, BLOCK), self.mirror.folder)
            self._note("PILE_RENDERED", surface=s, block=f"{b[0]}_{b[1]}", **got)
            if not got["rendered"]:
                failed[f"{s}_{b[0]}_{b[1]}"] = got
        return None

    def _tables_of_row(self, r: int) -> None:
        for b in sorted(b for b in self.candidates if b[0] == r):
            for s in self.meshes:
                if rendering.is_complete(self.pile(s, *b)):
                    t = self._table_from_piles(s, *b)
                    self._note("TABLE_READ", surface=s, block=f"{b[0]}_{b[1]}", seams=len(t["h"]) + len(t["v"]))
        if not self.keep_piles:
            # A pile serves its own table, its western neighbour's and the table of the row above, all read by now.
            for b in (b for b in self.candidates if b[0] == r):
                for s in self.meshes:
                    shutil.rmtree(self.pile(s, *b), ignore_errors=True)

    def tables_for_the_correction(self) -> dict:
        """Every table on disk, keyed `(surface, by, bx)`, in the shape the correction reads (the mean step only)."""
        out = {}
        for s in self.meshes:
            for by, bx in self.candidates:
                t = self.table(s, by, bx)
                if t is not None:
                    out[(s, by, bx)] = {d: {seam: x[0] for seam, x in t[d].items()} for d in ("h", "v")}
        return out
