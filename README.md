# LplVesuvius

**Measuring whether a traced surface follows a papyrus sheet, before spending anything on it.**

A Herculaneum scroll is a carbonised roll that cannot be unrolled. It is CT-scanned into a
stack of slices, and *segmentation* means following one sheet through that stack. The hard
part is not producing a surface. It is knowing whether the surface you produced follows a
sheet at all, because a wrong one still renders a plausible image.

There is no ground truth to compare against: nobody has ever unrolled these scrolls. So this
repository builds measurements that a trace can answer **about itself**.

---

## Start in five minutes

```bash
# 1. the deliverable answers for itself: 38 offline checks, no network
uv run --project . python tracecheck/selftest.py

# 2. every instrument in the tree, offline, one line per battery
./tools/temoins.sh

# 3. judge a published segment remotely, before downloading 32 GB
uv run --project . python tracecheck/tracecheck.py Scroll1 20230702185753 --voxel-um 2.4
```

Dependencies are declared at the root, so the tool runs from a fresh clone with no
sub-project to set up. Rebuilding the paper is `./article/build.sh`.

## Every instrument, from one entry point

```bash
./lplv --help              # the verbs, each with the first line of its own docstring
./lplv <verb> --help       # ITS help, produced by the module itself
./lplv --version           # which tier this build is, and which families it carries
```

⭐ This page deliberately does **not** list the verbs. `lplv --help` derives them from the
tree, so it cannot go stale, while any list written here would announce twenty-six verbs the
day there are thirty and nobody would notice. Same rule for options: `lplv <verb> --help`
*executes* the module with `--help` rather than re-describing its parser, so there is exactly
one description of every flag in this repository.

⚠ A verb that exists in the tree but not in the tier you are running does **not** answer
"unknown command" — it says so, and names the families this build carries.

`tools/temoins.sh` runs every self-test in the repository and prints one line per battery.
It ends with a count, and that count is itself a guarded number: a battery that stops being
run stops being counted, and the discrepancy shows.

For any tool's options, defaults and exit codes: `--help`. This file does not list them,
because a list of options copied into a README is stale before it is read.

---

## What is claimed, and where the evidence is

| claim | evidence |
|---|---|
| a trace can be judged **without ground truth**, by reading it at two window depths | `analysis/src/test_convergence.py`, paper section 3 |
| stability across runs can be an artefact of a **shared generation budget**, not of the scroll | paper section 5.2, dispersion 0.55 % to 86 % once the budget is raised |
| an ink model can return the **same map** on a surface geometrically proven to follow no sheet | paper section 6.4, correlation +0.9979 |
| a trace's quality can be read **remotely**, from published surface volumes | `tracecheck/`, paper section 4 |

Every number in the paper is recomputed from a result file and searched literally inside the
text. `analysis/src/verifier_chiffres.py` fails if a published number no longer matches what
its source produces. This is what makes "reproducible" a check rather than a word.

---

## Where things live

| path | what it holds |
|---|---|
| `tracecheck/` | the deliverable: one file, numpy only, 16 offline self-tests |
| `article/` | the paper, its typst sources, its english figures, `build.sh` |
| `analysis/src/` | the instruments: one file per measurement, each with `--verifier` |
| `tools/` | the campaigns that produce results, and `temoins.sh` that checks everything |
| `docs/*.json` | the result files every published number is recomputed from |
| `docs/*.md` | the working notebook, in french: one document per measurement, dated |

⚠ The working documents are in french and stay that way. They are the audit trail, not the
publication; the paper is the publication and it stands alone.

---

## ⚠ What this repository refuses to do

This section is the one worth reading twice.

- **It does not read text.** The measurements judge geometry. A surface that passes every
  check here may still carry nothing legible. Ink is the ruler, not the work.
- **It does not claim a trace is good.** Every measurement here can condemn a surface; none
  can certify one. `alpha` near zero means "no evidence it crosses the stack", not "it
  follows a sheet".
- **It does not report a correlation without its power floor.** With eight points, the
  correlation detectable at 80 % power exceeds 0.84. A middling result there is an absence
  of power, not an absence of effect, and reporting it as the latter is how a null result
  gets manufactured.
- **It does not compare a single run to a single run.** The tracer is not a function: the
  same seed, same parameters, gives a different surface every time, and alpha ranges over
  0.23 on one seed. Any difference smaller than that means nothing.
- **It does not publish a number it cannot recompute.** A figure whose computation is not in
  the tree is an anecdote, not a result.
- **It does not hide a measurement it cannot make.** A profile too flat to carry a peak is
  refused, not given a misleading alpha.

---

## Reproducing a specific number

Each working document ends with a `Reproduire` block holding the exact commands. The result
files in `docs/*.json` are the inputs to `verifier_chiffres.py`, which is what the battery
runs. If a document and its result file disagree, the battery fails and names both.

---

## Licence and citation

MIT, see `LICENSE`. The scroll data belongs to the Vesuvius Challenge and its partners; this
repository ships none of it, only measurements over it.
