"""The step tables of the correction, made here: mirror, render, read, row of blocks by row of blocks.

For each candidate block and each of the two surfaces, a pile is rendered from the local mirror and its step table
is read. Nothing of a whole segment fits on a disk at once (the mirror alone would be hundreds of gigabytes), so the
work goes one ROW of blocks at a time:

1. the chunks of the row are downloaded while the row before it renders, and those neither reads are dropped;
2. the piles of the row are rendered;
3. the tables of the PREVIOUS row are read: a table needs the pile to its south, which only exists now;
4. once a row's tables are read, nothing asks for its piles any more: they are removed, unless `keep_piles`.

A table already on disk is not redone, and a table read without a neighbour that later became rendered is redone:
it would miss the seams to it. The work stops cleanly, and says why, as soon as a disk runs short.
"""
from __future__ import annotations

import json
import multiprocessing
import shutil
import time
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
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


def table_from_piles(own: Path, east: Path | None, south: Path | None, by: int, bx: int, out: Path,
                     side: int = BLOCK) -> dict:
    """The step table of block (by, bx) read from its pile and, when rendered, its eastern and southern neighbours';
    written to `out` and returned. Only the first column (east) or row (south) of chunks of a neighbour is read."""
    piles = {(by, bx): rendering.read_pile(own)}
    if east is not None:
        piles[(by, bx + side)] = rendering.read_pile(east, columns=slice(0, steps.CHUNK))
    if south is not None:
        piles[(by + side, bx)] = rendering.read_pile(south, rows=slice(0, steps.CHUNK))
    t = steps.block_table(steps.chunk_reader(piles, side=side), by, bx, east is not None, south is not None,
                          side=side)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(t))
    tmp.replace(out)
    return t


def _done(value) -> Future:
    f = Future()
    f.set_result(value)
    return f


class TableMaker:
    """The piles and tables of one surface under test, in `work`.

    The next row downloads while the current one renders, and the tables of a row are read by `table_workers`
    processes while the next rows render (0: read in this process, one after the other).
    """

    def __init__(self, work: Path, meshes: dict[str, Path], candidates, volume: str, transport=None, journal=None,
                 disks=None, keep_piles: bool = False, threads: int = 16, table_workers: int = 0):
        self.work, self.meshes, self.candidates = Path(work), dict(meshes), set(candidates)
        self.mirror = mirror_.Mirror(self.work / "mirror", volume, transport, journal)
        self.journal, self.keep_piles, self.threads = journal, keep_piles, threads
        self.table_workers = int(table_workers)
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

    def make(self, stop_after_rows: int | None = None) -> dict:
        """Everything, row by row; `stop_after_rows` bounds a trial run."""
        start = time.monotonic()
        rows = sorted({by for by, _ in self.candidates})
        if stop_after_rows is not None:
            rows = rows[:int(stop_after_rows)]
        self._to_render = {r: self._piles_to_render(r) for r in rows}
        self._row_needs: dict[int, set] = {}
        done_rows, fills, failed, pending, stopped = [], [], {}, [], short_of_space(self.disks)
        if stopped or not rows:
            return {"rows": len(rows), "rows_done": 0, "failed": {}, "stopped": stopped, "bytes_downloaded": 0,
                    "seconds": round(time.monotonic() - start, 1)}
        # Spawned, not forked: the download thread is alive when the pool starts, and forking a threaded process can
        # deadlock the child.
        pool = (ProcessPoolExecutor(self.table_workers, mp_context=multiprocessing.get_context("spawn"))
                if self.table_workers > 0 else None)
        try:
            with ThreadPoolExecutor(max_workers=1) as downloads:
                ahead = downloads.submit(self._download_row, rows[0], set())
                for i, r in enumerate(rows):
                    fill, stopped = ahead.result()
                    fills += [fill] if fill else []
                    if stopped:
                        break
                    later = rows[i + 1] if i + 1 < len(rows) else None
                    ahead = (downloads.submit(self._download_row, later, self._needs_of_row(r)) if later is not None
                             else _done((None, None)))
                    stopped = self._render_row(r, failed)
                    if stopped:
                        break
                    done_rows.append(r)
                    if len(done_rows) >= 2:
                        pending.append((done_rows[-2], self._submit_tables(done_rows[-2], pool)))
                    while len(pending) > 1:
                        self._finish(*pending.pop(0))
                ahead.result()
            if not stopped and done_rows:
                pending.append((done_rows[-1], self._submit_tables(done_rows[-1], pool)))
            for row, futures in pending:
                self._finish(row, futures)
        finally:
            if pool is not None:
                pool.shutdown(wait=True)
        return {"rows": len(rows), "rows_done": len(done_rows), "failed": failed, "stopped": stopped,
                "bytes_downloaded": int(sum(f["bytes"] for f in fills)), "seconds": round(time.monotonic() - start, 1)}

    def _piles_to_render(self, r: int) -> list[tuple[str, tuple[int, int]]]:
        return [(s, b) for b in sorted(b for b in self.candidates if b[0] == r) for s in self.meshes
                if not rendering.is_complete(self.pile(s, *b))]

    def _needs_of_row(self, r: int) -> set:
        if r not in self._row_needs:
            self._row_needs[r] = set().union(*(self.needs(s, *b) for s, b in self._to_render.get(r, [])))
        return self._row_needs[r]

    def _download_row(self, r: int, rendering_now: set) -> tuple[dict | None, str | None]:
        """The chunks of the row, downloaded while the row before renders; everything neither reads, dropped.

        A row shares its upper chunks with the row before it, and only with it (measured on the segment: 153079 chunks
        in all, each read by one row or by two consecutive ones), so dropping everything else loses nothing.
        """
        if not self._to_render[r]:
            return None, None
        stopped = short_of_space(self.disks)
        if stopped:
            return None, stopped
        wanted = self._needs_of_row(r)
        self.mirror.empty(wanted | rendering_now)
        fill = self.mirror.fill(wanted, self.threads)
        self._note("MIRROR_FILLED", row=r, **{k: v for k, v in fill.items() if k != "failed"}, failed=len(fill["failed"]))
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

    def _submit_tables(self, r: int, pool) -> list[tuple[str, tuple[int, int], Future]]:
        """The tables of the row that are missing, or were read without a neighbour that is rendered now."""
        out = []
        for b in sorted(b for b in self.candidates if b[0] == r):
            for s in self.meshes:
                if not self._has_pile(s, b):
                    continue
                east = self.pile(s, b[0], b[1] + BLOCK) if self._has_pile(s, (b[0], b[1] + BLOCK)) else None
                south = self.pile(s, b[0] + BLOCK, b[1]) if self._has_pile(s, (b[0] + BLOCK, b[1])) else None
                old = self.table(s, *b)
                if old is not None and old["east"] == (east is not None) and old["south"] == (south is not None):
                    out.append((s, b, _done(old)))
                    continue
                args = (self.pile(s, *b), east, south, b[0], b[1], self.table_path(s, *b))
                out.append((s, b, pool.submit(table_from_piles, *args) if pool else _done(table_from_piles(*args))))
        return out

    def _finish(self, r: int, futures: list) -> None:
        """Wait for the tables of the row, then free its piles: nothing reads them any more."""
        for s, b, f in futures:
            t = f.result()
            self._note("TABLE_READ", surface=s, block=f"{b[0]}_{b[1]}", seams=len(t["h"]) + len(t["v"]))
        if not self.keep_piles:
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
