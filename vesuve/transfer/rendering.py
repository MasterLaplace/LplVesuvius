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
- The published renderer images (villa revision `1e3f4c0`, 2026-05-13) predate `--flip-normals`. Negating the
  normals only reverses the order of the layers, so a renderer without the option renders unflipped and the layers
  are reversed here: on the renderer that has both, the two piles are identical voxel for voxel
  (`tools/check_flip_fallback.py`).

Ported from `la_spire_produite_se_lit_elle_dans_le_treillis.py` (`la_commande_de_rendu`, `rendre`, `mettre_de_cote`,
`la_pile_est_complete`) and `src/outils/rendre_surveille.sh` on the `experimental` branch.
"""
from __future__ import annotations

import functools
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


@functools.lru_cache(maxsize=None)
def flips_normals(renderer_path: str = RENDERER) -> bool:
    """Whether the renderer knows `--flip-normals`, read from its own help; False when it cannot be run."""
    try:
        help_ = subprocess.run([renderer_path, "--help"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return "--flip-normals" in help_.stdout + help_.stderr


def command(tifxyz: Path, output: Path, box: dict, mirror: Path, layers: int = LAYERS,
            cache_gb: int = CACHE_GB, flip_normals: bool = True) -> list[str]:
    """The command that renders a pile as the published ones are: 109 layers one voxel apart, normals flipped.

    ⚠ The volume is read from the mirror and nowhere else: without the remote address, a chunk the mirror lacks reads
    as empty, never as a hidden download.
    """
    return [RENDERER, "-v", str(mirror), "--scale", "1", "-g", "0", "-s", str(tifxyz), "--tif-output", str(output),
            "-n", str(int(layers)), "--slice-step", "1", *(["--flip-normals"] if flip_normals else []),
            "--crop-x", str(box["x"]), "--crop-y", str(box["y"]),
            "--crop-width", str(box["width"]), "--crop-height", str(box["height"]),
            "--cache-gb", str(int(cache_gb))]


def reverse_layers(folder: Path) -> None:
    """The layers of a pile in the opposite order: what `--flip-normals` does, for a renderer that lacks it.

    Every file is renamed out of the way before any takes its new name, so no layer overwrites one not yet moved.
    """
    names = sorted(Path(folder).glob("*.tif"))
    moved = [f.rename(f.with_name(f.name + ".reversing")) for f in names]
    for k, f in enumerate(moved):
        f.rename(names[len(names) - 1 - k])


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
           runner=watch, flips: bool | None = None) -> dict:
    """The pile; a complete pile is not redone. `runner` and `flips` are given only by the tests; otherwise the
    renderer is asked whether it knows `--flip-normals`.

    ⚠ The end mark is written after the layers are reversed: a pile cut short while its files are being renamed has
    no mark, so it is set aside and rendered again instead of being read half reversed.
    """
    output = Path(output)
    if is_complete(output, layers):
        return {"rendered": True, "resumed": True}
    flips = flips_normals() if flips is None else bool(flips)
    (output / END_MARK).unlink(missing_ok=True)
    moved = set_aside(output)
    output.mkdir(parents=True, exist_ok=True)
    got = runner(command(tifxyz, output, box, mirror, layers, flip_normals=flips), output,
                 output.with_suffix(".log"), patience)
    n = len(list(output.glob("*.tif")))
    ok = got["code"] == 0 and n == layers
    if ok and not flips:
        reverse_layers(output)
    if ok:
        (output / END_MARK).write_text(f"code 0, {n} layers\n")
    return {"rendered": ok, "resumed": False, "layers": n, "layers_reversed": ok and not flips, **got,
            **({"set_aside": str(moved)} if moved else {})}


def read_pile(folder: Path, rows: slice = slice(None), columns: slice = slice(None)) -> np.ndarray:
    """The 109 layers of a pile, stacked (layer, y, x); `rows` and `columns` keep a strip, cut layer by layer so that the
    whole pile is never held for it."""
    return np.stack([np.ascontiguousarray(tifffile.imread(f)[rows, columns]) for f in sorted(Path(folder).glob("*.tif"))])
