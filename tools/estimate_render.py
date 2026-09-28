"""What `vesuve grand-prize --render` will download before it downloads it: the chunks of the raw scan, row by row.

It builds the two surfaces from the published mesh and the embedded transfer (the mesh is read once, 55 MB), then
lists the chunks each pile's render reads, exactly as the render loop does, and prints how many chunks each row of
blocks needs, how many are shared with the row before, and what the whole segment costs.

    uv run python tools/estimate_render.py [--cache cache] [--rows N]

About six minutes of one core for the whole segment; nothing of the raw scan is downloaded.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from vesuve import embedded  # noqa: E402
from vesuve.remote import Remote  # noqa: E402
from vesuve.transfer import mirror, rendering, surfaces  # noqa: E402

SEGMENT = "20230702185753"
BLOCK = 16


def estimate(cache: Path, rows: int | None = None) -> dict:
    k = embedded.correction(SEGMENT)
    rc = k["context"]["render"]
    remote = Remote(cache)
    with tempfile.TemporaryDirectory() as tmp:
        made = surfaces.the_two_surfaces(remote.tifxyz_folder(rc["mesh"]), k["transfer"], Path(tmp), rc["mesh_step"])
        meshes = {role: surfaces.read_points(made[role]) for role in ("reference", "produced")}
    chunk_bytes = 128 ** 3
    ordered = sorted({by for by, _ in k["candidates"]})[:rows]
    per_row, seen, total = {}, set(), set()
    for r in ordered:
        need = set()
        for b in sorted(b for b in k["candidates"] if b[0] == r):
            for points, _, spacing in meshes.values():
                need |= mirror.chunks_of_crop(points, spacing, rendering.crop(*b, BLOCK))
        per_row[r] = {"chunks": len(need), "shared_with_the_row_before": len(need & seen)}
        seen, total = need, total | need
    downloads = sum(x["chunks"] - x["shared_with_the_row_before"] for x in per_row.values())
    return {"rows": len(ordered), "piles": 2 * sum(1 for b in k["candidates"] if b[0] in per_row),
            "per_row": per_row, "unique_chunks": len(total), "downloads": downloads,
            "download_gb": round(downloads * chunk_bytes / 1e9, 1),
            "largest_mirror_gb": round(max(x["chunks"] for x in per_row.values()) * chunk_bytes / 1e9, 1)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cache", type=Path, default=Path("cache"))
    p.add_argument("--rows", type=int, default=None, help="only the first N rows of blocks")
    a = p.parse_args()
    print(json.dumps(estimate(a.cache, a.rows), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
