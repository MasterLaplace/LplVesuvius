"""Check that a renderer without `--flip-normals` gives the same pile once its layers are reversed.

It renders one block twice from a mirror already on disk: once with `--flip-normals`, once without it and with the
layers reversed, as `vesuve` does for a renderer that lacks the option. Both piles must be identical, voxel for voxel.
The same comparison with the second pile left unreversed is the control: it must differ, or the check proves nothing.

    uv run python tools/check_flip_fallback.py [--work cache/render/20230702185753] [--block 368_128]

It needs a renderer that knows `--flip-normals` (the published villa images do not), and the chunks of the block in
the mirror of `--work`: nothing is downloaded. Two renders, about a minute.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from vesuve.transfer import rendering  # noqa: E402


def check(work: Path, by: int, bx: int, surface: str, out: Path) -> dict:
    mesh, mirror, box = work / "surfaces" / surface / "mesh", work / "mirror", rendering.crop(by, bx, 16)
    flipped = rendering.render(mesh, out / "flipped", box, mirror, flips=True)
    fallback = rendering.render(mesh, out / "fallback", box, mirror, flips=False)
    if not (flipped["rendered"] and fallback["rendered"]):
        return {"rendered": False, "flipped": flipped, "fallback": fallback}
    a, b = rendering.read_pile(out / "flipped"), rendering.read_pile(out / "fallback")
    return {"rendered": True, "block": f"{by}_{bx}", "surface": surface, "voxels": int(a.size),
            "voxels_different": int((a != b).sum()), "voxels_different_left_unreversed": int((a != b[::-1]).sum())}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--work", type=Path, default=HERE / "cache" / "render" / "20230702185753")
    p.add_argument("--block", default="368_128", help="the block `by_bx` whose chunks are in the mirror")
    p.add_argument("--surface", default="reference", choices=("reference", "produced"))
    a = p.parse_args()
    if not rendering.flips_normals():
        print(f"{rendering.RENDERER} has no --flip-normals here: there is nothing to compare it with", file=sys.stderr)
        return 2
    by, bx = (int(x) for x in a.block.split("_"))
    with tempfile.TemporaryDirectory() as tmp:
        got = check(a.work.resolve(), by, bx, a.surface, Path(tmp))
    print(json.dumps(got, indent=1))
    ok = got["rendered"] and got["voxels_different"] == 0 and got["voxels_different_left_unreversed"] > 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
