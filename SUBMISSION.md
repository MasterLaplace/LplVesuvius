# Submission: September 2026 Progress Prizes

**vesuve 0.2.0** is one Docker image with one pipeline per prize, built on a series of dated research slices,
295 so far. Its main result this month: on a published PHercParis4 segment, it corrects the transfer from one
winding to the next without a human. It takes the right decision four times as often as the wrong one (163 against
41, sign test p = 2e-18), and the judges are used only to score. On a band where the same procedure does not hold,
the program measures that and writes nothing.

Every number below links to the file that produces it. The research lives on the
[`experimental`](https://github.com/MasterLaplace/LplVesuvius/tree/experimental) branch, in French; this branch,
`main`, is the program, in English.

## The four questions of the form

### 1. Which scroll data

- **PHercParis4, segment `20230702185753`**: its surface volume
  (`2.4um-0.22m-78keV-volume-20260411134726.zarr`), read chunk by chunk from the public bucket; its published mesh;
  its published ink map; and the next winding that the segment's own tracer drew by hand, used as the judge.
- **PHercParis4, band `20260623142658-w028-037`**: where the correction was measured not to hold.
- **PHerc1447, segment `20250702235910`**, for First Letters, and the innermost published PHercParis4 bands
  (`w010-027`) for the title search.

### 2. How it raises the odds of reading a scroll

The [Open Problems](https://scrollprize.org/2026_open_problems) page names sheet switches as a bottleneck and asks for
"conservative failure detection". Today a human finds where a surface jumped to the next winding and fixes it. This
program does two parts of that job without a human, on real data:

- **It certifies where a surface stayed on one winding.** Loops closed on the lattice of steps between neighbouring
  chunks certify 6333 of the 97771 chunks of the segment, with no hand in any decision, and it names the 111 bands
  (24263 chunks) it would still have to read to judge the rest
  ([`246`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/246_la_couverture_sans_main.md),
  fact `R4-F410`; replayed by `tests/test_embedded_data.py`).
- **It corrects the transfer to the next winding where a point slipped.** It walks the sheet on the reference and on
  the produced winding, anchors their difference on the neighbouring blocks, and brings a point back by one winding
  when a slip explains its departure better than the noise. On 340 blocks it corrects 495 points: 163 misses become
  right and 41 right points become misses, a net gain of 122
  ([`275`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/275_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.md),
  fact `R4-F456`). The sign test gives p = 2.04e-18 on the points and 2.25e-05 on the blocks, 42 blocks up and 11
  down ([`290`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/290_les_gains_publies_se_distinguent_ils_du_hasard.md),
  fact `R4-F471`).

The gain has to be read at its real size. Most transferred points were already right, so over the whole segment the
share on the right winding moves from 0.9303 to 0.9334. What matters is that the decision to move a point is taken
without a judge and is right far more often than wrong, which is the property a human corrector provides.

### 3. What it enables that was not possible before

- **A verdict on a published surface without ground truth.** Which chunks stayed on one winding, and where a
  published segment changed winding: `vesuve progress` names column 260, rows 26 to 223, where the loop's cumulative
  closure crosses half a sheet at cuts 163, 173 and 203 ([`examples/progress/report.md`](examples/progress/report.md),
  facts `R4-F401`, `R4-F406`).
- **A correction of the next winding that says where it holds.** The same procedure on the band `w028-037` gives 15
  misses made right for 25 rights made misses (p = 0.154,
  [`281`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/281_la_procedure_sans_juge_tient_elle_sur_la_bande.md)).
  Four more slices measured why. With neighbours to the east and west only, even the segment's gain falls from 122 to
  5 ([`291`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/291_la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.md)),
  and the anchor carries the loss ([`292`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/292_lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment.md)).
  Yet giving the band's blocks neighbours to the north and south does not bring its gain back: 7 for 5, p = 0.774
  ([`295`](https://github.com/MasterLaplace/LplVesuvius/blob/experimental/docs/archive/295_une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.md)).
  The program therefore writes corrections only for blocks with neighbours along both axes, and its report says that
  this condition is necessary and not sufficient: the correction is validated on one segment.
- **Every equation in one place.** [`FORMULARY.md`](FORMULARY.md) is rendered from the code: each equation, the fact
  that carries it, and the research file that established it.

### 4. The evidence

- **The published numbers, replayed.** Each port is tested against the research function that produced the
  number. The correction gives back what `275` and `281` published, block by block, and the corrected transfer it
  writes corrects the same points as the one the research saved, to within a millionth of a voxel
  (`tests/test_correction.py`).
- **The judges never decide.** Replaced by noise, they change the counts and not one corrected point (same file).
- **Tests that can fail.** Rules were broken on purpose to check that their tests turn red. An anchor that keeps its
  own block, or a decision that favours the slip, makes four correction tests fail, the published counts and the
  saved bytes among them. On the research side, a figure's title check first passed against a frozen number, because
  the published gains happen to be 2 and 0; it was rewritten until the frozen title failed (`295` §5).
- **Negative results kept.** The band, the east-west anchor, the taller band: each is a dated slice with its
  measurement, its figure and its registry fact.
- **A run anyone can make.** `docker run` reproduces the Grand Prize and Progress reports from the embedded data,
  offline; the dated reports are in [`examples/`](examples/README.md).

## Checking it yourself

```bash
make test                                  # the C core under AddressSanitizer and UndefinedBehaviorSanitizer
uv run vesuve grand-prize --no-surface     # the certificate and the correction, about 20 s
uv run vesuve read outputs/grand-prize     # the stages, the requirements, where it stops
uv run vesuve formulas                     # every equation it applies
```

With the research next to it, the parity tests compare each port with its producer:

```bash
git worktree add ../research experimental
VESUVE_RESEARCH=../research uv run --extra tests pytest -q -rs
```

## What it does not do

- It does not unroll a scroll. It certifies and corrects surfaces others traced, on one segment of PHercParis4,
  which is not one of the thirteen scrolls of the 2027 Grand Prize.
- It does not render the step tables the correction reads. They come from the research's renders (two surfaces
  rendered through `vc_render_tifxyz` from about 50 GB of chunks) and are embedded; the program replays the decision.
- It does not read text. First Letters on PHerc1447 finds no periodic rows under the 2023 model (`R1-F20`), and the
  Paris 4 title search shows where an end-title would be, for a papyrologist to judge.

## A guide to the `experimental` branch

The research is a series of dated slices. Each asks one question and answers it with a measurement.

| where | what |
|---|---|
| `docs/archive/NNN_*.md` | one slice: the question, what was declared before measuring, the result, what it does not say |
| `docs/mesures/*.json` | the measurement of a slice, written by its script |
| `src/<family>/<slice>.py` | the script; `--verifier` runs its battery of checks, `--json` writes its measurement |
| `docs/images/NNN_*.png` | the figure, drawn from the measurement by `src/figures/` |
| `docs/rapports/REGISTRE_faits.tsv` | every fact (`R4-F456`...), its value, its status and the slice that carries it |
| `src/depot/verifier_chiffres.py` | checks that each number of a document is the one its measurement holds |

The slices of this submission: `244` and `246` for the certificate, `247` and `248` for the transfer and its judges,
`260` to `265` for the walk, the anchor and the decision, `275` for the whole segment, `281` and `291` to `295` for
where it does not hold, `290` for the sign test.
