"""A pile: 109 layers of the scan around a surface, rendered by `vc_render_tifxyz` from the local mirror.

The renderer is the community's (ScrollPrize/villa, `volume-cartographer`), the one that rendered the published
surface volumes: a render of 2 × 2 chunks of segment `20230702185753` by it equals the published pile in 0.99 of the
voxels (`257`). This module drives it; it does not reimplement it.

Three lessons of the research, each one paid for, and each one kept here:

- `vc_render_tifxyz` creates its 109 files at the start and fills them band by band, and it skips a pile whose 109
  files exist. A pile cut short and run again in place was declared rendered without a pixel changing. A pile is
  therefore complete only with an END MARK written after a render that returned zero with its 109 layers, and an
  unfinished pile is set aside, never overwritten or deleted.
- A render that stops making progress says nothing. The watchdog reads the ACTIVITY of the process (bytes read and
  written, `/proc/<pid>/io`, plus the size of its output), never the time elapsed: a long render is not a stuck one.
- Its chunk cache defaults to 16 GB. It is capped here, since this is the one place every render goes through.

Ported from `la_spire_produite_se_lit_elle_dans_le_treillis.py` (`la_commande_de_rendu`, `rendre`, `mettre_de_cote`,
`la_pile_est_complete`) and `src/outils/rendre_surveille.sh` on the `experimental` branch.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import tifffile

RENDERER = "vc_render_tifxyz"
LAYERS = 109
END_MARK = ".render_complete"
PATIENCE = 900        # seconds without any activity before a render is abandoned
POLL = 10.0
CACHE_GB = 1


def crop(cy: int, cx: int, side: int, chunk: int = 128) -> dict:
    """The pixel crop of the render that covers `side` × `side` chunks from chunk (cy, cx)."""
    return {"x": int(cx) * chunk, "y": int(cy) * chunk, "width": int(side) * chunk, "height": int(side) * chunk}


def renderer() -> str | None:
    """The path of `vc_render_tifxyz`, or None when it is not installed."""
    return shutil.which(RENDERER)


def command(tifxyz: Path, output: Path, box: dict, mirror: Path, layers: int = LAYERS,
            cache_gb: int = CACHE_GB) -> list[str]:
    """The command that renders a pile as the published ones are: 109 layers one voxel apart, normals flipped.

    ⚠ The volume is read from the mirror and nowhere else: without the remote address, a chunk the mirror lacks reads
    as empty, never as a hidden download.
    """
    return [RENDERER, "-v", str(mirror), "--scale", "1", "-g", "0", "-s", str(tifxyz), "--tif-output", str(output),
            "-n", str(int(layers)), "--slice-step", "1", "--flip-normals",
            "--crop-x", str(box["x"]), "--crop-y", str(box["y"]),
            "--crop-width", str(box["width"]), "--crop-height", str(box["height"]),
            "--cache-gb", str(int(cache_gb))]


def is_complete(output: Path, layers: int = LAYERS) -> bool:
    """Its 109 layers AND the end mark: counting the layers alone lets a pile cut at 18 % pass for complete."""
    return (Path(output) / END_MARK).is_file() and len(list(Path(output).glob("*.tif"))) == layers


def set_aside(output: Path) -> Path | None:
    """An unfinished pile, moved away before a render redoes it; nothing is deleted."""
    output = Path(output)
    if not (output.is_dir() and any(output.glob("*.tif"))):
        return None
    base = output.parent / "_set_aside" / f"{output.name}_{time.strftime('%Y%m%dT%H%M%S')}"
    target, k = base, 0
    while target.exists():
        k += 1
        target = base.with_name(f"{base.name}_{k}")
    target.parent.mkdir(parents=True, exist_ok=True)
    output.rename(target)
    return target


def _activity(pid: int, output: Path) -> int | None:
    """Bytes read and written by the process plus the size of its output; None once the process is gone.

    ⚠ None and never zero: the process can end between two polls, and reading zero then would look like total
    inactivity and abandon a render that just succeeded.
    """
    try:
        io = Path(f"/proc/{pid}/io").read_text()
    except OSError:
        return None
    moved = sum(int(line.split()[1]) for line in io.splitlines() if line.startswith(("rchar:", "wchar:")))
    return moved + sum(f.stat().st_size for f in Path(output).glob("*.tif"))


def watch(cmd: list[str], output: Path, log: Path, patience: float = PATIENCE, poll: float = POLL) -> dict:
    """Run `cmd` and kill it once it has done nothing for `patience` seconds; say which happened."""
    start = time.monotonic()
    with open(log, "w") as fh:
        p = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)
        last, still = None, time.monotonic()
        while p.poll() is None:
            time.sleep(poll)
            a = _activity(p.pid, output)
            if a is None:
                continue
            if a != last:
                last, still = a, time.monotonic()
            elif time.monotonic() - still > patience:
                p.kill()
                p.wait()
                return {"code": None, "abandoned": True, "seconds": round(time.monotonic() - start, 1)}
    return {"code": p.returncode, "abandoned": False, "seconds": round(time.monotonic() - start, 1)}


def render(tifxyz: Path, output: Path, box: dict, mirror: Path, layers: int = LAYERS, patience: float = PATIENCE,
           runner=watch) -> dict:
    """The pile; a complete pile is not redone. `runner` is replaced only by the tests."""
    output = Path(output)
    if is_complete(output, layers):
        return {"rendered": True, "resumed": True}
    (output / END_MARK).unlink(missing_ok=True)
    moved = set_aside(output)
    output.mkdir(parents=True, exist_ok=True)
    got = runner(command(tifxyz, output, box, mirror, layers), output, output.with_suffix(".log"), patience)
    n = len(list(output.glob("*.tif")))
    ok = got["code"] == 0 and n == layers
    if ok:
        (output / END_MARK).write_text(f"code 0, {n} layers\n")
    return {"rendered": ok, "resumed": False, "layers": n, **got, **({"set_aside": str(moved)} if moved else {})}


def read_pile(folder: Path) -> np.ndarray:
    """The 109 layers of a pile, stacked (layer, y, x)."""
    return np.stack([tifffile.imread(f) for f in sorted(Path(folder).glob("*.tif"))])
