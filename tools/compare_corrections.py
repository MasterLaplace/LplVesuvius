"""Compare two runs of the correction: which points each one moved, and by how much their values differ.

Two runs that decide alike move the same points; their values can still differ in the last digits when their step
tables did, since a moved point is brought back by a gap measured on those tables. This says which of the two it is.
A block decides alike when every field of it but its anchor is the same: the anchor is a median of those tables, and
its last digits are allowed to move with them.

    uv run python tools/compare_corrections.py outputs/render-full outputs/render-docker
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from vesuve import embedded  # noqa: E402

SEGMENT = "20230702185753"


def compare(a: Path, b: Path) -> dict:
    transfer = embedded.correction(SEGMENT)["transfer"]
    ta, tb = np.load(a / "corrected_transfer.npy"), np.load(b / "corrected_transfer.npy")
    with np.errstate(invalid="ignore"):
        moved_a, moved_b = np.isfinite(ta) & (ta != transfer), np.isfinite(tb) & (tb != transfer)
        both = np.isfinite(ta) & np.isfinite(tb)
        gap = np.abs(ta - tb)
    ca, cb = (json.loads((x / "correction.json").read_text()) for x in (a, b))
    blocks_a, blocks_b = ({f"{k['row']}_{k['column']}": k for k in c["blocks"]} for c in (ca, cb))
    decided_alike = all({f: v for f, v in blocks_a[k].items() if f != "anchor_voxels"}
                        == {f: v for f, v in blocks_b.get(k, {}).items() if f != "anchor_voxels"} for k in blocks_a)
    anchors = sum(1 for k in blocks_a if blocks_a[k]["anchor_voxels"] != blocks_b.get(k, {}).get("anchor_voxels"))
    return {"same_points_defined": bool(np.array_equal(np.isfinite(ta), np.isfinite(tb))),
            "moved_in_a": int(moved_a.sum()), "moved_in_b": int(moved_b.sum()),
            "moved_in_one_only": int((moved_a != moved_b).sum()),
            "points_whose_values_differ": int((both & (gap > 0)).sum()),
            "largest_value_difference_voxels": float(np.nanmax(np.where(both, gap, np.nan))),
            "blocks": len(blocks_a), "same_blocks": sorted(blocks_a) == sorted(blocks_b),
            "every_block_decided_alike": decided_alike, "blocks_whose_anchor_differs": anchors}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    a = p.parse_args()
    got = compare(a.a, a.b)
    print(json.dumps(got, indent=1))
    return 0 if got["moved_in_one_only"] == 0 and got["every_block_decided_alike"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
