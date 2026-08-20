#!/usr/bin/env python3
"""Minimal reproducer: `vc_tifxyz_selfcross` can report `clean` having tested nothing.

WHAT THIS SHOWS
---------------
`vc_tifxyz_selfcross --maxedge N` drops every quad with an edge longer than N voxels, for
a good reason stated in its own help text: *"a triangle built across a grid discontinuity
crosses everything it passes through"*. But when the threshold falls below the mesh's own
step size, it drops **all** of them -- and the report then reads:

    "clean_of_transverse_self_intersection": true
    "census": [{ "pairs_tested": 0, "quads_dropped_for_edge_length": <all of them>, ... }]

A verdict and an absence of measurement come out through the same field. A gate built on
`--fail-on-crossing` passes **any** surface in that state, with the exit code the script
expects.

WHY IT IS NOT ONLY A SILLY SETTING
----------------------------------
The default is `--maxedge 60`. A segmentation grown at `step_size 60` or coarser has quads
whose edges are about that long, so the default alone reaches this state. Measured on a
real mesh, decimated so that only its DESCRIPTION coarsens while its geometry does not:

    step ~20 vx : 240 crossings, 751 169 pairs tested
    step ~40 vx : 123 crossings,  32 255 pairs tested
    step ~60 vx :   0 crossings,       0 pairs tested   <- "clean", by default
    step ~80 vx :   0 crossings,       0 pairs tested   <- "clean", by default

With the filter disabled (`--maxedge 0`) the same two last rows report 72 and 49 crossings.

SUGGESTED FIX (one line, on their side)
---------------------------------------
Make `clean_of_transverse_self_intersection` false -- or add an explicit `measured: false`
-- when `pairs_tested == 0`. Until then, any consumer must check `pairs_tested` itself.

This script is self-contained: it builds a small tifxyz surface, runs the tool twice, and
reports what came back. It needs `numpy`, `tifffile`, and `vc_tifxyz_selfcross` on PATH.

    python3 repro_empty_verdict.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STEP = 20.0          # voxels between neighbouring grid points
SIDE = 24            # grid points per side


def build_surface(folder: Path) -> None:
    """A flat patch whose quads have edges of about STEP voxels."""
    import numpy as np
    import tifffile

    u = np.arange(SIDE, dtype=np.float32) * STEP
    x = np.tile(u, (SIDE, 1))
    y = np.tile(u.reshape(-1, 1), (1, SIDE))
    z = np.full((SIDE, SIDE), 1000.0, dtype=np.float32)

    folder.mkdir(parents=True, exist_ok=True)
    for name, grid in (("x", x), ("y", y), ("z", z)):
        tifffile.imwrite(folder / f"{name}.tif", grid.astype(np.float32))
    # The loader wants these as strings; leaving any of them out (or null) fails with
    # "type must be string, but is null", which names the type and not the field.
    (folder / "meta.json").write_text(json.dumps({
        "format": "tifxyz", "type": "seg",
        "uuid": "repro_empty_verdict",
        "name": "repro_empty_verdict",
        "source": "repro_empty_verdict.py",
        "target_volume": "none",
        "scale": [1.0 / STEP, 1.0 / STEP],
        "area_vx2": float((SIDE - 1) ** 2) * STEP * STEP,
        "area_cm2": 0.0,
        "bbox": [[0.0, 0.0, 1000.0],
                 [float((SIDE - 1) * STEP), float((SIDE - 1) * STEP), 1000.0]],
        "vc_gsfs_params": {"step_size": STEP},
    }, indent=4) + "\n")


def run(surface: Path, maxedge: int, out: Path) -> dict | None:
    cmd = ["vc_tifxyz_selfcross", "--surface", str(surface),
           "--maxedge", str(maxedge), "-o", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not out.is_file():
        print(f"  the tool wrote no report (exit {r.returncode})", file=sys.stderr)
        print((r.stderr or r.stdout or "").strip()[:400], file=sys.stderr)
        return None
    d = json.loads(out.read_text())
    census = d.get("census") or []
    return {
        "exit": r.returncode,
        "clean": bool(d.get("clean_of_transverse_self_intersection")),
        "pairs": sum(c.get("pairs_tested", 0) for c in census),
        "dropped": sum(c.get("quads_dropped_for_edge_length", 0) for c in census),
        "transverse": sum(c.get("transverse", 0) for c in census),
    }


def main() -> int:
    if shutil.which("vc_tifxyz_selfcross") is None:
        print("vc_tifxyz_selfcross is not on PATH", file=sys.stderr)
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="repro_empty_verdict_"))
    try:
        surface = tmp / "flat.tifxyz"
        build_surface(surface)
        print(f"a flat {SIDE}x{SIDE} patch, step {STEP:.0f} voxels "
              f"({(SIDE - 1) ** 2} quads)\n")

        # Below the step size the filter drops every quad; above it, none.
        sain = run(surface, int(STEP) * 3, tmp / "wide.json")
        vide = run(surface, int(STEP) - 1, tmp / "narrow.json")
        if sain is None or vide is None:
            return 2

        head = f"  {'--maxedge':>10} {'clean':>7} {'pairs tested':>13} {'quads dropped':>14}"
        print(head)
        print("  " + "-" * (len(head) - 2))
        for label, r in ((int(STEP) * 3, sain), (int(STEP) - 1, vide)):
            print(f"  {label:>10} {str(r['clean']).lower():>7} "
                  f"{r['pairs']:>13} {r['dropped']:>14}")

        ok = vide["clean"] and vide["pairs"] == 0
        print()
        if ok:
            print("  REPRODUCED: the second row reports a clean surface having compared")
            print("  zero pairs of quads. A --fail-on-crossing gate would pass here.")
            # A gate really does pass: check the exit code the tool gives.
            g = subprocess.run(["vc_tifxyz_selfcross", "--surface", str(surface),
                                "--maxedge", str(int(STEP) - 1),
                                "--fail-on-crossing", "-o", str(tmp / "gate.json")],
                               capture_output=True, text=True)
            print(f"  --fail-on-crossing exit code on the empty verdict: {g.returncode} "
                  f"(3 would mean 'crossing found')")
        else:
            print("  NOT REPRODUCED on this build -- the behaviour may have been fixed.")
            print("  That is the good outcome; please tell us which version you ran.")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
