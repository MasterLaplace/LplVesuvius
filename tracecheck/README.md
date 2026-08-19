# tracecheck

Judge a Herculaneum scroll segment's trace **before** you spend anything on it.

```
$ python3 tracecheck.py Scroll1 20230702185753 --voxel-um 2.4 --prefer 2.4um --sheet-um 172.8
2.4um-0.22m-78keV-volume-20260411134726.zarr
  296 requests, 96 windows with papyrus
  material           68.5 %   <- strongest predictor of published ink (rho +0.54, n=80)
  edge pinned         7.3 %   <- sheet outside the surface volume
  offset            -13.2 um
  residual           43.2 um  (p90 128.4)
  rigid share        23.4 %   <- what a mesh translation would remove
  coherence        +0.310   (shuffled control -0.081)
  vs 173 um sheet pitch: 0.74 sheets  -> stays on its sheet
```

**No download. No credentials. numpy and Python 3.9+, nothing else.** Roughly 300 HTTPS
range reads, a few megabytes, ~15 seconds. The equivalent measurement from rendered
layer stacks costs about 32 GB per segment.

## Why it is cheap

A published surface volume is OME-Zarr shaped `[depth, rows, cols]` with chunks
`[depth, 128, 128]`. **One chunk therefore holds the entire depth column of a
128×128 window** — exactly the unit a depth profile needs. Chunks are independent HTTPS
objects, so the reads parallelise with no coordination (measured speed-up at 16 threads:
**×8.35**, byte-identical output).

## What the numbers mean

| field | meaning | what it is worth |
|---|---|---|
| `material` | fraction of probed windows containing any papyrus | **rho +0.539** against 80 published Scroll 1 ink maps (n = 80, p < 1e-6; **+0.561** after partialling out segment area) |
| `edge_pinned` | fraction whose intensity peak sits at a stack edge — the sheet is *outside* the surface volume | rho −0.275 (p = 0.014) against the same ink maps |
| `offset_um` | median distance from traced layer to peak of material | rho +0.388 (n = 54, p = 0.004) against independently published self-crossing counts |
| `residual_um` | what remains **after** the best rigid shift | **rho +0.428** (n = 54, p = 0.0012) against the same crossings |
| `rigid_share` | share of the error a mesh translation would remove | **21.7 %** median on 80 Scroll 1 segments — so the useful repair is a warp, not a shift |
| `coherence` | does a window's error predict its neighbour's | **80/80** Scroll 1 and **19/19** Scroll 4 segments beat their own shuffle control (p = 1.3e-25 / 7.4e-08) |

### The one that changes a decision

Dropping the worst **20 %** of segments by `material` raises the corpus median ink
contrast by **+0.381**, against 2000 random draws of the same size: **p = 0.0005**.
The threshold is defended by a plateau (15–25 %), not by a peak — 5 % does nothing
(p = 0.054) and 30 % degrades.

## What it does **not** do

- **It does not predict legibility.** `offset`, `residual` and `coherence` show no
  relationship with published ink content (rho = −0.028, n = 80, where 0.31 would be
  detectable at 80 % power). They measure a defect of the **trace**, not of the
  **result**. Only `material` and `edge_pinned` carry over.
- **A blank ink map can also mean blank papyrus.** Nothing here separates the two, so
  the output is a corpus triage signal, never a verdict on one segment.
- **`--sheet-um` has no default, deliberately.** It is the inter-sheet spacing *of that
  scroll*. We once applied PHerc0172's 142.8 µm to PHercParis4 segments, whose measured
  spacing is 172.8 µm, and it inflated our sheet-jump count fourfold. Without the
  parameter the tool gives no sheet-jump verdict at all.

## Usage

```
python3 tracecheck.py <scroll> <segment> --voxel-um <um> [--prefer 2.4um] [--sheet-um <um>]
python3 tracecheck.py --key <full/s3/key.zarr> --voxel-um <um>
python3 tracecheck.py ... --json          # machine-readable
python3 selftest.py                       # offline controls, no network
```

Scroll aliases: `Scroll1` → `PHercParis4`, `Scroll4` → `PHerc1667`, `Scroll5` →
`PHerc0172`. Any published scroll name also works directly.

`--prefer` picks among several surface volumes by substring (a segment often publishes
its scan at 1.1, 2.4 and 45 µm). Without it, the finest is used — and `--voxel-um` must
match whichever one is read.

## Three traps this reader already pays for you

1. **The chunk key separator is not always `/`.** It is declared in `.zarray`
   (`dimension_separator`), and one corpus mixes both. Hardcoding it does not raise an
   error — it requests a key that does not exist, which a naive reader counts as an
   "empty chunk", and the segment then reports as having no papyrus. That looks like a
   result.
2. **A surface volume is mostly padding.** The segment is a twisted band inside a
   rectangular canvas. Blocks placed on a regular lattice landed in the void: **6 useful
   windows out of 96**. A scouting pass finds the papyrus before sampling it.
3. **Intensity locates the material; local contrast does not.** On a 2.4 µm volume the
   contrast curve is a U — maximal at both stack edges and minimal inside the sheet,
   because it follows interfaces and noise. The two agree only on coarse volumes, so
   nothing distinguishes them until you plot the curve.

## Licence and provenance

Written for the Vesuvius Challenge. The measurements quoted above are reproducible from
the sources in this repository; each number has a script that computes it.
