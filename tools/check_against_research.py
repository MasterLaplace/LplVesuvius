"""Check what `vesuve grand-prize --render` makes against what the research made, on the research's own files.

Three checks, cheapest first; each prints what it compared and whether it is identical:

1. the two surfaces written from the published mesh and the embedded transfer, against the research's meshes;
2. the step table of one block, read from the research's piles, against the research's table;
3. with `--render`, one pile rendered here from a fresh mirror, against the research's pile, voxel for voxel.

    VESUVE_RESEARCH=<working copy of experimental> uv run python tools/check_against_research.py [--block 16_256] [--render]

The research's data (`data/rendu_spire_voisine/`, `data/spire_voisine/`) is not versioned: this runs where it lives.
The third check downloads about 2 GB of the raw scan and runs `vc_render_tifxyz`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from vesuve import embedded  # noqa: E402
from vesuve.remote_zarr import BUCKET  # noqa: E402
from vesuve.transfer import mirror, rendering, steps, surfaces  # noqa: E402

SEGMENT = "20230702185753"
ROLES = {"reference": "le_segment_reduit", "produced": "la_spire_produite"}


def check_meshes(research: Path, out: Path) -> dict:
    import tifffile

    k = embedded.correction(SEGMENT)
    made = surfaces.the_two_surfaces(research / "data" / "spire_voisine" / SEGMENT, k["transfer"], out)
    result = {}
    for role, french in ROLES.items():
        theirs = research / "data" / "rendu_spire_voisine" / french / "maillage"
        result[role] = all(np.array_equal(tifffile.imread(made[role] / f"{c}.tif"), tifffile.imread(theirs / f"{c}.tif"))
                           for c in "xyz")
    return {"identical": result, "points": made["points"]}


def check_table(research: Path, by: int, bx: int) -> dict:
    root = research / "data" / "rendu_spire_voisine"
    result = {}
    for role, french in ROLES.items():
        theirs = json.loads((root / "les_pas" / french / f"bloc_{by}_{bx}.json").read_text())
        piles = {(by, bx): rendering.read_pile(root / french / f"bloc_{by}_{bx}")}
        if theirs["est"]:
            piles[(by, bx + 16)] = rendering.read_pile(root / french / f"bloc_{by}_{bx + 16}")[:, :, :steps.CHUNK]
        if theirs["sud"]:
            piles[(by + 16, bx)] = rendering.read_pile(root / french / f"bloc_{by + 16}_{bx}")[:, :steps.CHUNK, :]
        ours = steps.block_table(steps.chunk_reader(piles), by, bx, theirs["est"], theirs["sud"])
        result[role] = {"seams": len(ours["h"]) + len(ours["v"]), "identical": ours["h"] == theirs["h"]
                        and ours["v"] == theirs["v"], "kept_chunks": ours["kept_chunks"]}
    return result


def check_render(research: Path, by: int, bx: int, work: Path, role: str = "reference") -> dict:
    k = embedded.correction(SEGMENT)
    rc = k["context"]["render"]
    root = research / "data" / "rendu_spire_voisine"
    theirs_mesh = root / ROLES[role] / "maillage"
    points, _, spacing = surfaces.read_points(theirs_mesh)
    box = rendering.crop(by, bx, 16)
    chunks = mirror.chunks_of_crop(points, spacing, box)
    m = mirror.Mirror(work / "mirror", f"{BUCKET}/{rc['raw_volume']}")
    filled = m.fill(chunks, threads=8)
    got = rendering.render(theirs_mesh, work / "pile", box, m.folder)
    if not got["rendered"]:
        return {"rendered": False, "render": got, "mirror": filled}
    ours, theirs = rendering.read_pile(work / "pile"), rendering.read_pile(root / ROLES[role] / f"bloc_{by}_{bx}")
    return {"rendered": True, "chunks": len(chunks), "mirror": {k: v for k, v in filled.items() if k != "failed"},
            "seconds": got.get("seconds"), "voxels_different": int((ours != theirs).sum()), "voxels": int(ours.size)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = os.environ.get("VESUVE_RESEARCH")
    p.add_argument("--research", type=Path, required=root is None, default=root)
    p.add_argument("--block", default="16_256", help="the block `by_bx` whose table and pile are compared")
    p.add_argument("--render", action="store_true", help="also render one pile here and compare it (about 2 GB read)")
    p.add_argument("--work", type=Path, default=None, help="where the render check writes (default: a temporary folder)")
    a = p.parse_args()
    by, bx = (int(x) for x in a.block.split("_"))
    research = a.research.resolve()
    with tempfile.TemporaryDirectory() as tmp:
        out = {"meshes": check_meshes(research, Path(tmp) / "surfaces"), "table": check_table(research, by, bx)}
        if a.render:
            out["render"] = check_render(research, by, bx, a.work or Path(tmp) / "render")
    print(json.dumps(out, indent=1))
    ok = all(out["meshes"]["identical"].values()) and all(x["identical"] for x in out["table"].values())
    ok = ok and (not a.render or out["render"].get("voxels_different") == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
