# tracecheck

Judge a Herculaneum scroll segment's trace **before** you spend anything on it.

```
$ python3 tracecheck.py Scroll1 20230702185753 --voxel-um 2.4 --prefer 2.4um --sheet-um 172.8
2.4um-0.22m-78keV-volume-20260411134726.zarr
  296 requests, 96 windows with papyrus
  material           68.5 %   <- correlates with published ink on Scroll 1 (rho +0.54, n=80) -- see the caveat below
  relief             0.184     <- x9.20 the detection floor of 0.02; below it the column is noise, not a sheet
  edge pinned         7.3 %   <- sheet outside the surface volume
  offset            -13.2 um
  residual           43.2 um  (p90 128.4)
  rigid share        23.4 %   <- what a mesh translation would remove
  coherence        +0.310   (shuffled control -0.081)
  vs 173 um sheet pitch: 0.74 sheets  -> stays on its sheet
```
⚠⚠ **`material` comes with two measured caveats, and neither is optional.** They are
stated here because this is the only document that leaves the repository, and a tool that
overstates its own result is worse than one that measures nothing.

1. **The correlation is driven by a near-blank class.** Remove the segments that carry
   almost no ink and it falls to **rho +0.190, not significant**.
2. **It does not replicate outside Scroll 1.** On Scroll 5 it is **rho −0.217**
   (p = 0.12) — the wrong sign. Tested on three other scrolls; it holds on none.

> **Read it as a property of Scroll 1's published corpus, not of the problem.** Within
> that corpus it is solid and useful. Outside it, we have measured that it is not.



## `relief` is the field to read first, and we measured why

`relief` is the peak-to-trough spread of a depth column divided by its mean — dimensionless,
so a change of scanner gain does not move it. Below the instrument's floor of **0.02** the
column carries no structure: what you are reading is noise, not a sheet.

⚠ **Where this comparison was measured, stated because it matters.** We profiled **138
series** from *rendered layer stacks*, in 1024-pixel analysis windows — not from published
surface volumes in 128-pixel chunks, which is what this tool reads. The mechanism is
instrument-independent: relief present in a narrow window is what following a sheet *means*.
The two error counts below are not, and we have not measured them on this instrument.

| signal | follows a sheet | lies across the stack |
|---|---:|---:|
| **relief** below the floor | **0 / 75** | **34 / 63** |
| `edge_pinned` at 90 % or more | **6 / 75** | **39 / 63** |

> **On those rendered stacks, `relief` never erred in the direction that costs you;
> `edge_pinned` did so six times.** Six surfaces that genuinely follow a sheet still had more
> than 90 % of their peaks at an edge. That is why `relief` is printed first — but read both,
> and calibrate both where you are reading them.

⚠⚠ **No threshold transports between instruments, and we got this wrong for an hour.** An
earlier version of this file offered **2.25** as the lowest ratio measured on a surface that
does follow a sheet. That number was measured in **1024-pixel** analysis windows; this tool
reads **128-pixel** chunks, and the window size moves the reading as much as the depth does.
Measured on one unchanged rendered stack:

| analysis window | relief |
|---:|---:|
| 1024 px | 0.046 |
| 512 px | 0.081 |
| 256 px | 0.146 |

It triples across two halvings. `relief` also grows with the **depth** of the window it is
read in — measured exponent **+1.01** on surfaces lying across the stack. So a cutoff
calibrated on one instrument is meaningless on another, and the reference point has been
withdrawn rather than carried over.

⭐ **Calibrate on your own corpus, which is one command.** `--all --csv` judges every
published segment of a scroll and gives you the distribution `relief` takes where you are
reading it. Compare a candidate to that, never to a number from somewhere else.

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
| `rigid_share` | share of the error a mesh translation would remove. ⚠ The normalisation is a choice; the raw pair is not — median shift **14.4 µm** against a **56.4 µm** residual | **21.7 / 35.3 / 28.6 %** on Scrolls 1, 4 and 5 — the useful repair is a warp, not a shift. ⚠ One single segment returned 0.67; its scroll's median is 28.6 %. One sample is not a result |
| `coherence` | does a window's error predict its neighbour's | **150 of 152** segments across three scrolls beat their own shuffle control — 80/80, 19/19, 51/53 |

### The one that changes a decision

Dropping the worst **20 %** of segments by `material` raises the corpus median ink
contrast by **+0.381**, against 2000 random draws of the same size: **p = 0.0005**.
The threshold is defended by a plateau (15–25 %), not by a peak — 5 % does nothing
(p = 0.054) and 30 % degrades.

## The other verb: where to *start*

`tracecheck` judges a trace you already have. `--seed` answers the question at the other
end — **where to put the seed** that `vc_grow_seg_from_seed` needs — and it reads the
published surface *prediction* instead of a surface volume.

```
$ python3 tracecheck.py --voxel-um 9.362 --level 0 \
    --seed PHerc0358/representations/predictions/surfaces/2025...-th0.2.zarr
  25 chunks probed, 18 empty  block 8^3 = 75 um  smooth r=1
   planar   nb  region  occup   -s x y z
   0.9982   14   0.967  0.045   5842 5839 7386
   0.9979   15   0.589  0.332   1964 2042 7324
  order is x y z, what vc_grow_seg_from_seed wants -- the zarr is (z, y, x)
```

### Why not "where is there the most predicted surface"

Because it **saturates, silently**. A surface prediction is *thresholded*, so it is binary:
any block fully inside predicted matter hits the format ceiling and comes back at 255. Our
first attempt returned **eight candidates all scoring 255** — and eight tied candidates are
not a ranking, they are a coin toss wearing a measurement's clothes. The tool now says so
out loud when it happens.

### What it ranks instead

The 3D structure tensor, `planarity = (lam1 - lam2) / lam1`:

| situation | planarity |
|---|---:|
| one sheet crosses the block | **1.00** |
| **two parallel sheets** | **1.00** |
| a junction at 90 deg | **0.00** |
| isotropic noise | 0.04 |
| a uniform block (all void or all matter) | gated out — a null tensor's eigenvalues are ordered noise |

The second row is the one that matters: a regular stack is exactly where a seed belongs, so
a criterion that penalised it would be looking for *little matter* rather than *well-ordered
matter*. What collapses the score is a **junction** — precisely where the tracer can slip
from one wrap to the next with nothing in the prediction to stop it.

⚠ **An argmax over a chunk's ~13 800 blocks saturates too** — the maximum of a bounded
score over that many draws is ~1 whatever the terrain, and our first version duly returned
four candidates at 1.0000. What is ranked is the planarity **averaged over the 3×3×3 block
neighbourhood**, ties broken by how many valid neighbours there are; each chunk also reports
its `region` share, a property of the region that no maximum can manufacture.

⚠ **The orientation bias is measured, not assumed.** A thresholded prediction turns a tilted
sheet into a staircase. Swept 0–90°, raw planarity ranges **0.828–1.000**; with the default
blur, **0.947–1.000** — and the residual stays far below the signal, since a junction scores
0.000.

### What it bought, measured — and what did not replicate

On `PHerc0358`, one variable changed — the seed, everything else identical:

| | neighbourhood seed | **planarity seed** |
|---|---:|---:|
| area | 8.48 cm² | 19.82 cm² |
| pairs tested by `vc_tifxyz_selfcross` | 387 151 | **852 135** |
| **transverse self-intersections** | **240** | **0** |

⚠⚠ **We then ran it paired over 12 prize scrolls, and the self-intersection result did not
replicate**: both criteria return **zero** on the other eleven. That 240 is one scroll's
accident, and we report it as such. What *does* replicate is how far the tracer gets before
stalling — **10 – 2, sign test p = 0.0386** — and the extremes say it best: on `PHerc0125`
and `PHerc0826` the neighbourhood seed stalls at **0.85 cm²**, barely above `min_area_cm`,
where planarity reaches 19.82 and 13.14.

⚠ **And on `PHerc0358` the fix that mattered was not the criterion but the occupancy
ceiling.** Replayed without it, the neighbourhood criterion returns exactly the bad seed —
whose block has **occupancy 1.000**, entirely full of predicted matter. A uniform block has
a **null structure tensor**: no sheet, no normal, nothing to follow. The prediction had
merged several wraps into a solid blob.

⚠ And the honest limits, both measured: **area saturates against the generation budget**
(two different scrolls both stop at generation 119 of 120 and return the same area to eight
thousandths of a percent), and pushed to 600 generations — 127.9 cm² — the same planar seed
*does* self-intersect, 174 times. Its rate stays **21× lower per pair tested**, and First
Letters needs 4 cm², not 128. **A seed fixes where you start, not how you travel.**

⚠⚠ `vc_grow_seg_from_seed` is **not bit-reproducible**, and the obvious remedy does not
work. Six runs of the same seed, measured:

| | area | self-intersections |
|---|---:|---:|
| `thread_limit: 0`, run 1 | 19.834872 cm² | 0 |
| `thread_limit: 0`, run 2 | 19.821850 cm² | 0 |
| `thread_limit: 1`, run 1 | 19.838660 cm² | 0 |
| `thread_limit: 1`, run 2 | 19.823302 cm² | 0 |

**Setting `thread_limit: 1` — the value VC3D itself uses, and the one the tool's own
startup message recommends — does not fix it.** A ~0.08 % spread survives.

⭐ But "the tracer is not reproducible" is too coarse, and comparing *growth logs* rather
than final areas says something sharper: **all 118 generations are identical to the
hundredth across all six runs**, including one given a direction field. **The growth is
deterministic; the final step is not.** That is a much narrower defect than it first
looks — and it means a growth trajectory can be compared run to run, which is what makes
a controlled experiment on this tool possible at all.

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
python3 tracecheck.py ... --json                  # machine-readable, one segment
python3 tracecheck.py <scroll> --all --csv ...    # every segment of a scroll, ranked
python3 selftest.py                               # offline controls, no network
```

`--all` judges every segment of a scroll that publishes a surface volume and prints each
row **as it lands** — an interrupted run keeps what it has. Segments without a published
volume are skipped and counted; "no volume" and "volume with no papyrus" are different
facts and are reported separately.

⚠ **`coherence` needs neighbour pairs to mean anything.** Measured on a real segment with
`--blocks 2 --side 3`: coherence 0.435 against a shuffled control of **0.423** — the
control had stopped discriminating, and nothing in the output said so. The tool now
reports `pairs` and `coherence_reliable`, and marks a thin row `⚠thin`. Raise `--side` or
`--blocks` rather than reading a number that cannot be wrong.

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

## A bug in `vc_tifxyz_selfcross`, with a two-second reproducer

`repro_empty_verdict.py` in this folder builds a small flat surface, runs the official
tool twice, and shows this:

```
   --maxedge   clean  pairs tested  quads dropped
  -----------------------------------------------
          60    true         12320              0
          19    true             0           1058

  --fail-on-crossing exit code on the empty verdict: 0
```

**A verdict and an absence of measurement come out through the same field.** When
`--maxedge` falls below the mesh's own step size the filter drops every quad, `clean`
stays `true`, and a gate built on `--fail-on-crossing` passes any surface at all — with
the exit code the calling script expects.

This is not only a silly setting. The default is `--maxedge 60`, so a segmentation grown
at `step_size 60` or coarser reaches the same state on the defaults. Measured on a real
self-intersecting mesh, decimated so that only its *description* coarsens while its
geometry does not:

| step | crossings (default) | pairs tested | crossings (`--maxedge 0`) |
|---:|---:|---:|---:|
| ~20 vx | 240 | 751 169 | 240 |
| ~40 vx | 123 | 32 255 | 123 |
| ~60 vx | **0** | **0** | 72 |
| ~80 vx | **0** | **0** | 49 |

Two separate losses, and the right-hand column separates them: coarsening the mesh alone
takes 240 down to 49 on geometry that never changes, and the filter then turns the last
two into silent zeros.

**Suggested fix, one line on your side**: make `clean_of_transverse_self_intersection`
false — or add an explicit `measured: false` — when `pairs_tested == 0`. Until then, any
consumer has to check `pairs_tested` itself, which is what this repository now does in a
single shared reader.

> A second consequence, for anyone comparing `step_size` settings by their crossing
> counts: **those counts are not comparable across steps.** The detector finds 51 % of a
> known set of crossings at step 40, and less beyond. A sweep that reports "zero at a
> coarse step" is partly reporting its own loss of sensitivity.

## Licence and provenance

Written for the Vesuvius Challenge. The measurements quoted above are reproducible from
the sources in this repository; each number has a script that computes it.
