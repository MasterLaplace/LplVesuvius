// ─────────────────────────────────────────────────────────────────────────────
//  Mise en page : préprint arXiv, une colonne. C'est la forme qu'ont les trois
//  articles primaires du domaine, et elle supporte de grandes figures.
// ─────────────────────────────────────────────────────────────────────────────
#set document(
  title: "Measuring segmentation quality without ground truth in virtual unwrapping",
  author: "Guillaume Papineau",
)
#set page(
  paper: "a4",
  margin: (x: 2.4cm, y: 2.6cm),
  numbering: "1",
  number-align: center,
)
#set text(font: ("New Computer Modern", "DejaVu Serif"), size: 10pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 0.78em, first-line-indent: 1.2em)
#set heading(numbering: "1.1")
#show heading: it => block(above: 1.4em, below: 0.7em)[
  #set text(weight: "bold", size: if it.level == 1 { 12pt } else { 10.5pt })
  // ⚠ La bibliographie est un titre SANS numérotation : sans ce garde, `display`
  // reçoit `none` et la compilation échoue au tout dernier élément du document.
  #if it.numbering != none [
    #counter(heading).display(it.numbering) #h(0.6em)
  ]
  #it.body
]
#set math.equation(numbering: "(1)")
#show figure.caption: set text(size: 8.6pt)
#show figure: set block(above: 1.5em, below: 1.5em)
#set table(stroke: (x, y) => (
  top: if y == 0 { 0.8pt } else if y == 1 { 0.4pt } else { 0pt },
  bottom: 0pt, left: 0pt, right: 0pt,
))
#show table.cell.where(y: 0): set text(weight: "bold")
#set cite(style: "institute-of-electrical-and-electronics-engineers")

// `#um` écrit « µ m » avec une espace : en markup, deux éléments voisins sont
// séparés. On définit donc l'unité comme un seul mot.
#let um = [μm]

// ⚠ L'ORCID est l'identifiant qui SURVIT aux changements d'adresse — c'est exactement ce
// pour quoi il existe, et un préprint reste en ligne bien plus longtemps qu'une adresse
// d'école. Renseigner ici (« 0000-0000-0000-0000 ») et la ligne s'affiche ; laisser vide
// et elle disparaît, plutôt qu'un gabarit qui partirait tel quel.
#let ORCID = "0009-0006-1371-4119"

// Un raccourci pour les réserves, très utilisé dans ce texte.
#let caveat(body) = block(
  inset: (left: 0.8em, y: 0.5em), stroke: (left: 1.6pt + rgb("#b03030")),
  text(size: 9.4pt)[#body],
)

// ─────────────────────────────────────────────────────────────────────────────
//  Bloc de titre
// ─────────────────────────────────────────────────────────────────────────────
#align(center)[
  #block(width: 92%)[
    #text(size: 16pt, weight: "bold")[
      Measuring segmentation quality without ground truth
      in the virtual unwrapping of Herculaneum papyri
    ]
    #v(0.4em)
    #text(size: 11.5pt)[and four artefacts the measurement reveals]
  ]
  #v(1.1em)
  #text(size: 10.5pt)[Guillaume Papineau]
  #v(0.3em)
  #text(size: 9pt, style: "italic")[Independent researcher]
  #v(0.25em)
  #text(size: 9pt, font: ("DejaVu Sans Mono", "DejaVu Sans"))[guillaume.papineau\@epitech.eu]
  #if ORCID != "" [
    #v(0.2em)
    #text(size: 9pt)[ORCID iD #link("https://orcid.org/" + ORCID)[#ORCID]]
  ]
  #v(0.5em)
  #text(size: 9pt)[Preprint --- 22 August 2026]
]

#v(1.2em)

#block(width: 100%, inset: (x: 1.6em))[
  #set text(size: 9.3pt)
  #set par(first-line-indent: 0em)
  *Abstract.* Virtual unwrapping recovers text from carbonised scrolls by fitting a
  surface to the papyrus inside an X-ray tomogram and flattening it. The fitting step
  --- *segmentation* --- is the acknowledged bottleneck, and it has no ground truth: on a
  sealed scroll nothing says where the sheet actually is. Existing quality signals are
  therefore either geometric self-consistency checks or human inspection. We introduce a
  measurement that needs neither a threshold, nor a reference surface, nor a physical
  scale. It renders the same surface through progressively deeper windows and reads the
  exponent $alpha$ of the power law relating the apparent distance-to-material to the
  window depth. A surface lying on its sheet gives $alpha approx 0$; one lying across the
  stack gives $alpha approx 1$, because its "peak" is merely the strongest thing the
  window happened to contain. Applying this and a complementary remote triage to 13 of
  the scrolls in the Vesuvius Challenge prize set, we report four findings that bear on
  how the community's results are read. First, the reference tracer is *a draw, not a
  function*: over 78 runs with strictly identical parameters, 5 of 13 scrolls flip
  between a clean and a self-intersecting verdict. Second, both the *stability* and the
  *cleanliness* usually attributed to a good trace are artefacts of the generation
  budget: raising it from 120 to 400 moves the median area dispersion from 0.55 % to
  86.00 %, and the share of self-intersecting runs from 1/12 to 9/12. Third, the render
  window imposes a second ceiling of the same kind: 13 of 16 traces sit exactly on it, so
  an absolute threshold on a distance compares settings rather than surfaces. Fourth, the
  published segmentation of a prize scroll is a set of samples --- *one patch per sheet*
  --- not a tiling of one sheet: of 105 pairs among 15 published segments, none is closer
  than 79 #um, twice the same-sheet threshold. We also show that a surface with
  $alpha approx 1$ is a *negative control by construction* for an ink detector, since its
  geometry rules out a papyrus face being within reach --- the control the foundational
  work lacks. We then show what a point estimate costs on the one
  quantity in this field that has a ground truth: the usual standard error of an AUC is
  $109 times$ too narrow on an ink map, and the fragment effect it certifies does not
  survive a variance decomposition. We argue that repetition and error bars, absent from
  the primary literature, are the cheapest available improvement to the field's
  evidentiary standard.
]

#v(0.8em)
#line(length: 100%, stroke: 0.4pt)

= Introduction

Eighteen hundred carbonised scrolls were recovered from a villa at Herculaneum in the
eighteenth century. They cannot be opened: the papyrus is a brittle carbon foam, and every
mechanical attempt has destroyed what it read. *Virtual unwrapping* replaces the physical
gesture with a computational one @seales2023 --- X-ray tomography produces a volume, a
surface is fitted to each sheet inside it, and the surface is flattened into a plane where
ink can be detected.

The fitting step is where the difficulty lives. The community calls it *segmentation*, and
its own documentation states plainly that "the problem is still unsolved. No method so far
manages to perfectly fit the wanted surface to the data."#footnote[Vesuvius Challenge,
`scrollprize.org/unwrapping`, retrieved August 2026.] The recent complete unwrapping of a
sealed scroll @angelotti2026complete required roughly 25 hours of human work per wrap ---
about 775 hours in total --- precisely because the automatic fit had to be inspected and
corrected turn by turn.

What makes segmentation hard to improve is not only that it is hard to do, but that it is
hard to *judge*. On an opened fragment one can compare a fit to a photograph. On a sealed
scroll there is nothing to compare to. The consequence is visible in the literature: the
complete-unwrapping paper publishes no tracing error rate; the spiral-fitting method
@henderson2025 publishes a topological guarantee --- the fitted surface is a single sheet
by construction --- but reports 3.20 % of *sheet traversals* anyway, because a guarantee
about topology is not a guarantee about which sheet one is on.

This paper is about the judging step. We contribute:

+ *A convergence test* (#link(<sec:conv>)[Section 3]) that decides whether a traced
  surface is on a sheet or across the stack, using no ground truth, no threshold on a
  physical quantity, and no scale. It compares a measurement to itself under a change of
  a rendering parameter.

+ *A remote triage* (#link(<sec:triage>)[Section 4]) that measures three properties of a
  published segment from a few megabytes of its published surface volume, before any
  download or inference is paid for.

+ *Four empirical findings* (#link(<sec:results>)[Section 5]) obtained by applying these
  to 13 prize scrolls: the tracer is non-deterministic in a way that changes verdicts; the
  stability and cleanliness of a trace are artefacts of its generation budget; the render
  window imposes a second ceiling, so that an absolute threshold on a distance compares
  settings rather than surfaces on 14 of 16 traces; and published segments do not tile a
  sheet.

+ *A negative control that costs nothing extra* (#link(<sec:negctrl>)[Section 6.5]). A
  surface whose convergence exponent is near 1 carries a geometric proof that no papyrus
  face is within reach, so any ink reported on it is a false positive by construction. This
  is the control the foundational paper lacks, and any pipeline that traces surfaces can
  produce one deliberately.

+ *An argument about method* (#link(<sec:disc>)[Section 6]): every number here is a
  measurement repeated, and the repetition is what produced the findings. None of them
  would have been visible from a single run. The same move applied one step downstream ---
  to the field's only ground-truth-free argument about *reading* --- shows that two of the
  three properties that argument groups together do not go together.

#caveat[
  *What this paper does not claim.* It does not propose a better segmentation algorithm,
  and it does not read any text. It measures. Where a measurement is negative or fails to
  replicate, we report it as such --- #link(<sec:triage>)[Section 4] contains a result
  that works on one corpus and fails on three others, and we publish all four.
]

= Background <sec:bg>

== The data

A scroll is imaged by synchrotron X-ray tomography. The public corpus of the Vesuvius
Challenge publishes, per scroll, one or more *volumes* (the tomogram, at 7.91, 8.64 or
9.362 #um per voxel depending on the scan), *predictions* (a learned per-voxel
score that the voxel lies on a papyrus surface), and, for some scrolls, *segments* --- the
fitted surfaces themselves, together with a *surface volume*: the tomogram resampled onto
a small stack of layers parallel to the fitted surface.

Ink is detected on the flattened surface. It is worth noting why the *geometry* of that
surface matters so much to the reading step: the carbon ink has almost no X-ray absorption
contrast, and what recent work detects is in part a *morphological* imprint --- surface
roughness together with pressure-induced deformation @angelotti2026ink. A surface fitted a
few tens of microns off the sheet does not merely blur the signal; it samples a different
material.

Two geometric facts matter throughout. The sheets are thin and close: on `PHerc1447` we
measure a median centre-to-centre spacing of 113 #um between neighbouring sheets
(#link(<sec:geom>)[Section 5.5]), which is about 13 voxels at 8.64 #um. And a
segment is small relative to a turn: each of ours spans 8 to 22 mm of arc, between 7.7 %
and 11.8 % of one revolution.

== Segmentation and its tools

The reference tool of the public pipeline @villa grows a surface from a *seed* point. Given a
seed and a parameter file, it expands a quad mesh outward, generation by generation,
stopping when it can no longer grow or when a *generation budget* is exhausted. The
budget matters a great deal, and #link(<sec:ceiling>)[Section 5.2] is about that.

Other tools attack the same step differently: `ThaumatoAnakalyptor` @thaumato segments
automatically from instance predictions rather than from a seed, `khartes` @khartes lets a
human annotate a surface interactively, and `tifxyz-surgeon` @tifxyzsurgeon repairs an
existing surface for self-consistency --- while stating plainly what that cannot settle:
"nothing here reads the volume [...] whether the surface is on papyrus at all is a different
question". That different question is the one #link(<sec:conv>)[Section 3] answers.

The published corpus itself is scriptable: `vesuvius-catalog` @vesuviuscatalog exposes the
bucket's own `metadata.min.json` --- 45 samples, their scans, their energies and voxel sizes,
and which of them carry segments or ink outputs --- which is the index we use in
#link(<sec:triage>)[Section 4] to choose what to measure.

The tool also offers a *neighbour* mode that projects an existing surface along its own
vertex normals to the next sheet, and a *resume* mode that lets an existing surface keep
growing. We use both in #link(<sec:chain>)[Section 5.6].

== Existing quality signals

Three kinds of signal are in use, and each has a documented limit.

/ Self-intersection: the fitted mesh is tested for pairs of faces that cross. The official
  checker reports a count. It is a necessary condition, not a sufficient one: a surface can
  be perfectly free of self-intersections and still sit on the wrong sheet.

/ Topological guarantee: spiral fitting @henderson2025 constructs the surface as a
  diffeomorphic image of a spiral, so it *cannot* be non-manifold. The same paper measures
  3.20 % of sheet traversals, which shows exactly what the guarantee does not cover.

/ Human inspection: the complete unwrapping @angelotti2026complete relies on it, at the
  cost quoted above. It is the only signal that currently catches a wrong-sheet error, and
  it does not scale.

== The community toolchain <sec:community>

Alongside the published papers, an independent toolchain has grown around the challenge, and
it carries quality signals that the three categories above do not cover. We read the following
at pinned commits from local clones; where we attribute a claim, it is in their code or their
own documentation, not inferred.

/ Render-quality gates: `vesuvius-automesh` @automesh scores a rendered patch before ink is
  attempted --- band contrast, sub-voxel re-centering statistics, merge fraction --- and its
  thresholds are *calibrated against a control*, with the calibration log kept in the source.
  It reports a found-fraction of 0.97--1.00 on true pages against 0.36--0.54 on traces lying
  across the stack, which is the same separation our #link(<sec:conv>)[convergence test]
  targets, obtained differently.

/ Winding structure across a corpus: `winding-ruler` @windingruler publishes a winding-pitch
  atlas over 36 scrolls, and states the principle we also rely on --- "it is the variance, not
  the mean, that decides usability". `winding-sync` @windingsync validates relative winding
  structure while declaring absolute counts unvalidated.

/ Patch-level auditing with clustered uncertainty: `tifxyz-doctor` @tifxyzdoctor bootstraps
  *by cluster* rather than by patch, on the stated ground that "patches are not independent
  draws". `windcheck` @windcheck sweeps its own detector's parameters and reports a curve
  rather than a single number, "because a single number from the easiest setting would
  overstate it".

/ Testing the tests: `spiralcheck` @spiralcheck mutates a checker to verify it can fail ---
  "this is the test of the tests" --- and names the failure mode we also guard against,
  "comparing a tool to itself is a check that cannot fail".

/ Support in the volume: `herculaneum-scroll-tools` @scrolltools streams the masked CT
  alongside a surface prediction and finds that roughly 70 % of positive voxels in the
  published predictions are phantoms, sitting where the CT reads exactly zero.

#caveat[
  *Two of these tools measure what we measure.* We record it here rather than in a footnote.
  `winding-ruler` @windingruler had already published a winding-pitch atlas covering the
  scrolls we surveyed, and had already found that reading it at pyramid level 2 merges
  adjacent sheets --- an overestimate of 10.3 % on 36 of 36 scrolls. And the official monorepo
  @villa measures line spacing on ink maps by sliding windows at the same width we chose. A
  prior-art audit of our own instruments (2026-08-29) found 22 of 98 already present in this
  toolchain. The failure was one of vocabulary: none of these carries our names for these
  quantities.
]

What is nonetheless missing across this toolchain, and what this paper adds, is narrower than
"an automatic semantic signal" and can be stated exactly:

+ *A verdict that needs no threshold on a physical quantity.* Every signal above compares a
  measurement to a calibrated cut-off. #link(<sec:conv>)[Section 3] compares a measurement to
  *itself* under a change of a rendering parameter, so it transports between instruments and
  scales.

+ *Uncertainty on the verdicts themselves.* Across the toolchain we read --- and across
  `ink-id`, `villa` and the Grand Prize model @gpwinner --- there is no permutation test, no
  power analysis, and no confidence interval on an ink-detection score. Numbers are published
  as point estimates. #link(<sec:interval>)[Section 6.2] shows what that costs on a quantity whose
  tile-to-tile standard deviation is 0.22: the usual standard error is a hundred times
  too narrow, and the effect it certifies does not survive a variance decomposition.

+ *A judge with a control condition.* The published judging protocol is human and shows no
  blank image, so a judge's fabrication rate is never measured.

= A convergence test for a traced surface <sec:conv>

== The idea

Take a fitted surface and render it: resample the tomogram onto a stack of $n$ layers
centred on the surface. In that stack, look for the layer at which material is densest
--- the *peak* --- and record its distance $d$ from the surface.

If the surface sits on a sheet, the peak is that sheet, it is close, and $d$ does not
depend on $n$: widening the window adds layers that contain nothing nearer. If the surface
sits *across* the stack, there is no sheet within reach, and the peak is simply the
strongest thing the window happened to contain --- so it moves outward as the window
widens.

The test is therefore not a measurement of $d$ at all. It is a measurement of how $d$
responds to $n$.

== Definition

Render the same surface at two depths $n_0 < n_1$ and record the two distances $d_0, d_1$.
Assume a power law $d prop n^alpha$ and read the exponent:

$ alpha = (log(d_1 \/ d_0)) / (log(n_1 \/ n_0)) . $ <eq:alpha>

The normalisation by $log(n_1\/n_0)$ is what makes two series comparable when they were
not observed over the same range: a surface looked at from 21 to 161 layers is not "worse"
than one looked at from 21 to 41 merely because it was looked at further.

Two regimes:

$ alpha approx 0 quad & <==> quad d "is a distance" & quad "(the sheet is there)" \
  alpha approx 1 quad & <==> quad d "is the window radius" & quad "(no sheet within reach)" $

#caveat[
  *Why this needs no ground truth, no threshold and no scale.* No ground truth, because the
  surface is compared only to *itself* under a change of parameter. No physical threshold,
  because the discriminating quantity is a dimensionless exponent, not a distance in
  #um --- one does not have to decide how many microns is "too far". No scale,
  because $alpha$ is invariant under $d arrow.r lambda d$: it does not matter whether the
  voxel is 8.64 or 9.362 #um, nor whether the sheets are 113 #um apart or 300.
]

== Behaviour on a known-good and a known-bad surface

#figure(
  image("figures/38_convergence.png", width: 100%),
  caption: [
    The test on two surfaces of the same scroll, measured with the same instrument. Both
    axes are logarithmic; the thin grey line is slope 1. *Green:* a published segment of
    `PHerc1447`. Its measured distance is 17.3 #um at 31 layers and 17.3 #um
    at 81 --- a factor 1.00 for a factor 2.6 of window, $alpha = +0.00$. *Orange:* one of
    our own traces of the same scroll, at 21, 41, 81 and 161 layers: 86.4, 159.8, 311.0 and
    682.6 #um --- a factor 7.90 for a factor 7.7 of window, $alpha = +1.01$. The
    French labels are those of the original instrument; the numbers are unchanged.
  ],
) <fig:conv>

The interpretation of the orange series is worth stating carefully, because it is
stronger than it first appears. It is *not* "our trace is 311 #um away from its
sheet". At 161 layers the search reached 691 #um --- about four inter-sheet spacings
--- and still found nothing. The correct reading is that *there is no sheet within reach at
all*.

That the surface is lying *across the stack*, rather than merely far from everything, is
settled by the rendering below and not by $alpha$ alone --- a distinction we make precise in
#link(<sec:twofailures>)[Section 3.5].

#figure(
  image("figures/38_en_travers.png", width: 78%),
  caption: [
    A rendering of the across-the-stack surface. One sees concentric laminations --- the
    scroll seen edge-on --- and not the fibrous texture of a papyrus face. This is what
    $alpha = +1.01$ looks like. The convergence test puts a number on an appearance that
    was previously only describable.
  ],
) <fig:travers>

== Resolution, and a verdict that is a coin flip <sec:resolution>

An instrument must state what it cannot distinguish. On two windows, $alpha$ does not
discriminate better than about $plus.minus 0.2$. That has a direct consequence for how
$alpha$ may be used: *a count of verdicts is a count of threshold crossings*, and any
verdict whose $alpha$ lies within $0.2$ of the decision boundary is a coin flip, not a
measurement.

We enforce this in the instrument rather than in the prose. Each verdict carries its
margin to the threshold and a `fragile` flag when the margin is below the resolution.
Nearly a quarter of our distinct verdicts are fragile, one of them by two thousandths ---
and we retracted a published conclusion that rested on it the same day.

#caveat[
  *A median hides a minority.* $alpha$ is computed from a median over rendered windows, so
  a surface can converge on the median while a minority of its windows have their peak
  pinned to the edge of the stack --- a periphery with no sheet within reach. We therefore
  report, alongside $alpha$, the fraction of windows whose peak is edge-pinned. A surface
  measured at $alpha = +0.000$ can carry 9 % of such windows, and a chain with the *better*
  $alpha$ ($+1.040$ against $+1.313$) can have nearly double the edge-pinned fraction
  (56 % against 30 %). The two measurements disagree, and both are reported.
]

== What $alpha approx 1$ does not distinguish <sec:twofailures>

A depth profile reports the distance to the nearest peak. When the profile is *flat* there
is no peak, and the reported distance defaults to the edge of the window. The ratio of two
window edges is the ratio of the two windows, so such a series yields $alpha approx 1$ *by
arithmetic identity*, whatever the volume contains.

The two situations are different. A receding peak is a measurement: there is a sheet, it is
far, and its distance tracks the window. A flat profile is not a measurement at all. Both
print the same verdict.

We audited every depth profile in our tree --- 225 profiles across 114 series --- computing
each series' measured $alpha$ alongside the $alpha$ it would have if every reading were its
own window edge.

#figure(
  image("figures/49_deux_pannes.png", width: 100%),
  caption: [
    Each series placed on its *measured* $alpha$ against the $alpha$ it would have if every
    reading were its own window edge. The ceiling $alpha$ is always near 1, so the band ---
    whose width is $alpha$'s own declared resolution, not a display choice --- collects
    exactly the series that cannot say whether a peak was there. The gap between the green
    cloud and the band *is* the reassurance: no converging verdict is anywhere near it.
  ],
) <fig:twofailures>

#figure(
  table(
    columns: (1fr, auto),
    align: (left, right),
    table.header[quantity][value],
    [profiles whose reading *is* the window edge], [21 / 225],
    [flat profiles (nothing to measure)], [15 / 225],
    [series where no window measures anything], [4 / 114],
    [series where $alpha$ cannot separate the two failures], [*24 / 111*],
    [*converging* series so affected], [*0 / 111*],
  ),
  caption: [
    The audit. What loses discriminating power is exactly the *across-the-stack* verdict.
    The smallest non-discriminating $alpha$ is $+0.8729$; the largest converging $alpha$ is
    $+0.4222$. The two populations do not overlap.
  ],
) <tab:twofailures>

#caveat[
  *This weakens a phrase, not a conclusion.* The ceiling $alpha$ is always near 1, so a
  converging surface is far from it by construction and no positive verdict is affected. And
  the two causes of $alpha approx 1$ --- the peak recedes, or there is no peak --- both mean
  *no sheet within the window*, which is what the verdict is used for. What over-claims is
  the wording "the peak moves with the window", which presumes a peak. Our tool now reads
  the profile's own amplitude against its own detection floor and returns *undecidable*
  rather than a confident sentence about an object that is not there.
]

== A slope has two footings <sec:footings>

The refusal above aggregates window amplitudes with a *maximum*: if one window has relief,
the series is not empty. That rule answers "is there anything here". It does not answer
"what is the slope", and $alpha$ is a slope through two points. A footing that measures
nothing is not a footing.

The remedy is not another refusal. A reading pinned to the window edge is not missing data:
it is a *bound*. The peak is at least that far, possibly further. Since
$alpha = log(e_1 slash e_0) slash log(n_1 slash n_0)$ with $n_1 > n_0$, the direction
follows rather than being guessed.

#figure(
  image("figures/51_appuis.png", width: 100%),
  caption: [
    A gap at the window edge is an *arrow*, not a point. *Left:* both footings at the edge,
    so no slope is excluded and $alpha = +1.01$ carries nothing. *Right:* only the narrow
    footing is at the edge, so the admissible slopes open into a single corner --- all of
    them below the drawn line --- and the converging verdict survives.
  ],
) <fig:footings>

#figure(
  table(
    columns: (1fr, auto),
    align: (left, right),
    table.header[footing at the edge][$alpha$ is],
    [neither], [exact],
    [the *narrow* one], [an *upper* bound: convergence holds, condemnation does not],
    [the *wide* one], [a *lower* bound: condemnation holds, convergence does not],
    [both], [nothing],
  ),
  caption: [
    The sign of the bound decides which verdict survives. A footing that is *flat but not at
    the edge* gives no sign at all: its reading is the argmax of noise, neither an upper nor
    a lower bound.
  ],
) <tab:footings>

Over the 138 judgeable series of our tree: 92 rest on two measured footings, 16 on an upper
bound, *none* on a lower bound, and 30 on no footing that holds. *39 verdicts no longer
stand*; 7 are saved by the sign; and *0 of the 75 converging series* is lost --- because the
only sign observed preserves exactly what sits below the threshold. The reassurance of
#link(<sec:twofailures>)[Section 3.5] is thereby given a mechanism instead of an observation.

Thirty-nine verdicts that no longer stand means stacking alphas says little. But *does the
narrow window show relief* is a binary question asked *inside* one window: no threshold to
tune, no depths to match, no slope resting on two footings.

#figure(
  image("figures/51_contraste.png", width: 100%),
  caption: [
    Amplitude of the narrowest window of each series, in multiples of the instrument's own
    detection floor, on a logarithmic axis. Every series that *converges* sits to the right
    of the floor; the lowest is at 2.25 times it. Series lying *across the stack* straddle
    it, and the tall column on the left is amplitude exactly zero, which has no logarithm
    and is therefore placed apart rather than crushed onto the smallest non-zero value.
  ],
) <fig:contrast>

*Not one.* Zero of 75 converging series has a flat narrow window, against *34 of 63*
condemned ones. On a surface that follows a sheet the relief is already there in a narrow
window, which is what following a sheet means; on a surface lying across the stack it appears
only by widening, that is, what one reads is the window and not the surface.

#caveat[
  *This is not circular, and the contrast is one-sided.* The partition is by the sign of
  $alpha$, which comes from the gaps; the flatness comes from the amplitudes. Two different
  quantities from the same profiles, linked by a mechanism --- a peak inside the window gives
  both a stable gap and a frank amplitude --- and that link is the content of the finding
  rather than a flaw in it. In the other direction 29 condemned series do have a measuring
  narrow window: a flat one condemns, a measuring one does not absolve.
]

#caveat[
  *And we then transported those two counts, which is the same error one level up.* The
  0 of 75 and 34 of 63 above were measured on *rendered layer stacks in 1024-pixel analysis
  windows*. We first published them, and a threshold drawn from them, as a property of our
  remote screening tool, which reads *128-pixel chunks of published surface volumes*. Relief
  depends on the depth of the window it is read in --- exponent $+1.01$ --- and on its extent
  in the plane: measured on one unchanged stack where only the window changes, 0.046 at
  1024 px, 0.081 at 512, 0.146 at 256, an exponent of $-0.830$. A corpus sweep confirmed it
  in the field, where `edge_pinned` never reaches the threshold at which we had called it
  wrong.
  #linebreak()
  What is instrument-independent is the *mechanism*: relief present in a narrow window is
  what following a sheet means. The two counts are not. The threshold was withdrawn, and the
  rule now lives in three places rather than in our vigilance --- the tool writes its reading
  geometry into its own output, the calibration refuses to mix two geometries in one file,
  and the figure prints the geometry on itself.
]

#caveat[
  *The first count was 132, and it was missing six.* Two directory conventions coexist in our
  tree: older campaigns write the profiles of a surface side by side, while our profiling
  tool writes *one window per subdirectory*. Grouping by parent directory cut the latter into
  series of a single profile, which are unjudgeable --- and they include the pyramid control
  and the raised-budget campaign, among the most consequential runs we have. None of the six
  carries a verdict. The series key is now shared and *the pyramid level is part of it*:
  merging two resolutions would compare two voxel sizes while appearing to compare two
  depths.
]

#caveat[
  *Twenty series returned the same number, to four decimals.* When both footings are at the
  edge, $alpha = log(192 slash 48) slash log(161 slash 41) = 1.0135$ --- a property of the
  *window pair* and of nothing else. Twenty independent runs, on seeds thousands of voxels
  apart, in two different predictions, with different draws of a stochastic tracer, return
  it identically. This is the lesson of
  #link(<sec:ceiling>)[Section 5.2] one level deeper: there, eight areas agreed to four
  significant figures because a budget truncated them all; here, twenty exponents agree to
  four decimals because a window pair determines them all. In both cases the *coherence* is
  what makes the artefact invisible, and each individual value --- 0.3175 cm#super[2],
  $+1.01$ --- looks entirely plausible on its own.
]

= Remote triage from published surface volumes <sec:triage>

== Why it is cheap

A published surface volume is stored as OME-Zarr with chunks of shape
$[d, 128, 128]$ --- one chunk is *the entire depth column of a #box[128 #sym.times 128]
window*, which is exactly the unit a depth profile needs. Chunks are independent HTTP
objects, so reads parallelise with no coordination. A whole segment is judged from about
300 range requests, a few megabytes and some fifteen seconds; we measure a speed-up of
#sym.times 8.35 at 16 threads with byte-identical output.

== What is measured

#figure(
  table(
    columns: (auto, 1fr, auto),
    align: (left, left, right),
    table.header[field][meaning][evidence],
    [`material`], [fraction of probed windows containing papyrus],
      [$rho = +0.539$],
    [`relief`], [peak-to-trough spread of a depth column over its mean --- flat means
      noise, not a sheet],
      [0 of 75 #super[†]],
    [`edge_pinned`], [peak sits at a stack edge --- the sheet is outside the volume],
      [$rho = -0.275$],
    [`offset`], [median distance from the traced layer to the material peak],
      [$rho = +0.388$],
    [`residual`], [what remains after the best rigid shift], [$rho = +0.428$],
    [`rigid_share`], [share of the error a mesh translation would remove], [22.1 %],
    [`coherence`], [does a window's error predict its neighbour's], [148/151],
  ),
  caption: [
    Fields measured remotely, and their correlation with an independent target: the
    published ink maps of 80 `Scroll 1` segments, taken as-is. Nothing of ours enters the
    target, so the relationship cannot be a shared artefact. `coherence` is compared to
    each segment's own shuffle control. #super[†] `relief` has no correlation against that
    target: its evidence is the contrast of #link(<sec:footings>)[Section 3.6], where it
    misses none of the 75 surfaces that follow a sheet --- but that count was measured on
    *rendered stacks*, not on this instrument, and does not transport between the two.
  ],
) <tab:triage>

== What a corpus reads, on the instrument that reads it <sec:calibration>

The footnote above admits a gap: `relief` earns its place from a contrast measured
elsewhere. Closing it costs one command --- `--all --csv` judges every published segment of
a scroll --- and the answer is a distribution, not a threshold.

#figure(
  image("figures/52_calibration.png", width: 100%),
  caption: [
    Where a published corpus sits, and in which window it was read. Each dot is one of the
    80 `Scroll 1` segments read over 109 layers; the geometry is printed on the figure
    because a reading averaged over a patch belongs to the patch. `relief` clusters far from
    the detection floor --- x2 at the lowest, x37 at the median --- and `edge_pinned` never
    reaches the threshold at which it was called wrong on the other instrument.
  ],
) <fig:calibration>

*The corpus is not homogeneous, and the tool refused before we noticed.* Of 81 segments, 80
are read over 109 layers and *one over 6*. A single distribution would have blended a
six-layer reading into eighty hundred-and-nine-layer ones. The calibration now groups by
geometry, and a group of one segment shows as one.

#caveat[
  *On this instrument the two signals do not separate, and that is the honest report.*
  `edge_pinned` runs from 0.000 to 0.254 across the corpus and never approaches 90 %, so it
  has no occasion to misfire here. Reciting the rendered-stack comparison as if it were a
  property of this tool would have been the fourth number of the day carried out of the
  geometry that produced it.
  #linebreak()
  One published segment reads *0.040*, twice the floor, where the next lowest is already at
  x19. It is alone, invisible in a table and obvious in the figure. That does not make it
  wrong --- thin, poorly exposed, or a lean region all read the same way. The criterion is
  necessary and never sufficient.
]

== A rule, and its failure to replicate

On `Scroll 1`, dropping the 20 % of segments poorest in `material` raises the corpus
median ink contrast by $+0.381$ against 2000 random draws of the same size
($p = 0.0005$). The threshold sits on a plateau --- 15 % to 25 % all hold at
$p <= 0.001$ --- which is what an honest knob looks like; an overfitted one produces a
peak.

We then tested the same measurement on 110 further segments across three more scrolls,
all with published surface volumes and published ink maps:

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    table.header[corpus][$n$][voxel][target spread][$rho$][detectable $rho$],
    [`Scroll 1`], [80], [2.4 #um], [1.008], [$bold(+0.539)$], [0.309],
    [`PHerc0139`], [38], [2.399 #um], [1.628], [$-0.229$], [0.441],
    [`PHerc1667`], [19], [2.399 #um], [0.720], [$+0.425$], [0.605],
    [`PHerc0172`], [53], [7.91 #um], [0.220], [$-0.217$], [0.377],
  ),
  caption: [
    The rule does not replicate --- and the last column says why that sentence must be read
    carefully. *Detectable $rho$* is the correlation each corpus could find at 80 % power
    and $alpha = 0.05$, given its $n$ alone. Only `Scroll 1` exceeds its own floor. Our
    first explanation was a target floor effect --- `PHerc0172`'s ink maps barely differ from
    one another --- but that explains one corpus out of three: `PHerc0139` sits at the same
    resolution as `Scroll 1`, has a *larger* relative spread, and returns the opposite sign.
  ],
) <tab:replication>

The honest reading is narrower than "it does not replicate". *None of the three had the
power to detect an effect the size of the one measured on `Scroll 1`*: each $abs(rho)$ falls
below its own 80 %-power floor. `PHerc1667` in particular returns $+0.425$ --- the same sign
and a comparable magnitude --- on 19 segments, where 0.605 would be needed. Two corpora do
return the opposite sign, which no amount of power explains away, and that is the part of
the shape that suggests a result which will dissolve.

We therefore report the rule as a property of `Scroll 1`'s published corpus, *not* of the
problem, and we publish all four corpora rather than the one that works: a reader learns at
once that it needs re-validating on their corpus, instead of discovering it afterwards.

#caveat[
  *A zero is reported with its power, or it is not reported.* Writing "three non-positive"
  --- as an earlier draft of this section did --- puts a corpus returning $+0.425$ in the
  same bin as one returning $-0.229$, and hides that neither could have seen the effect. The
  three negatives constrain the rule far less than their count suggests.
]

= Results <sec:results>

== The tracer is a draw, not a function <sec:draw>

The public tracer is multi-threaded and draws from an unseeded generator. Running it twice
with *strictly identical* parameters, seed and input does not return the same surface. This
is not documented, and no repetition or error bar appears in the primary literature.

We measured it as a paired campaign: 13 prize scrolls, six runs each, 78 runs, every
parameter fixed.

#figure(
  image("figures/35_tirages.png", width: 100%),
  caption: [
    Thirteen scrolls, six runs each, identical parameters. If the tracer were
    deterministic, every row would be a single point. None is. On five rows one point is
    red: the same call that returns a clean trace five times returns a self-intersecting
    one the sixth.
  ],
) <fig:draws>

#figure(
  table(
    columns: (1fr, auto),
    align: (left, right),
    table.header[quantity][value],
    [runs, scrolls], [78 over 13],
    [scrolls whose six runs return the same area], [0 of 13],
    [scrolls where the *verdict* flips between runs], [*5 of 13*],
    [bad runs], [*5 / 78 = 6.4 %* (exact 95 % CI 2.1 %--14.3 %)],
  ),
  caption: [Non-determinism of the reference tracer, measured.],
) <tab:draws>

A verdict flip is the strongest evidence available here, because it needs no threshold and
no ground truth: two executions with identical inputs, two opposite answers from the
official checker. The five flips carry 1615, 428, 607, 140 and 1371 self-intersections
respectively, against zero on the other five runs of the same scroll.

#caveat[
  *And the area does not signal the bad run.* If a bad run could be recognised by its area
  being unusual, one could discard it without judging it. It cannot: over the five bad
  runs the mean centre-normalised rank of the area is $0.68$, where $0.5$ is expected if
  the area says nothing. One has to judge the trace, not measure it.
]

== Stability and cleanliness are artefacts of the generation budget <sec:ceiling>

In the campaign above, the scrolls with the lowest area dispersion are exactly those whose
six runs stop at the same generation count. Two readings compete: either those scrolls are
genuinely more stable, or their dispersion is *crushed by a common truncation* --- six
traces cut at the same place necessarily have the same area.

The measurement that separates them is cheap: raise the budget and replay. We did, on two
of them, changing nothing else.

#figure(
  image("figures/35_plafond.png", width: 100%),
  caption: [
    The same scroll, the same call, six runs each; only the generation budget changes (120
    against 400). One dot per run, red if the trace self-intersects. The upper row of each
    pair is the original budget --- six runs collapsed onto one point --- and the lower row
    is the raised budget.
  ],
) <fig:ceiling>

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    table.header[scroll / budget][generations][median area][dispersion][dirty runs],
    [`PHerc0125` / 120], [118--118], [19.83 cm#super[2]], [0.3 %], [1/6],
    [`PHerc0125` / *400*], [207--333], [*71.31* cm#super[2]], [*115 %*], [*5/6*],
    [`PHerc0191` / 120], [118--118], [19.83 cm#super[2]], [0.8 %], [0/6],
    [`PHerc0191` / *400*], [216--283], [*80.39* cm#super[2]], [*57 %*], [*4/6*],
  ),
  caption: [
    Raising the generation budget. Median dispersion over the two scrolls moves from
    *0.55 % to 86.00 %*, a factor 156.
  ],
) <tab:ceiling>

Two conclusions follow, and the second was not what the experiment was designed to find.

*The stability was a truncation.* Six traces cut at the same generation have the same area
by construction. It was not a property of the scroll; it was the budget cutting them.

*The cleanliness was a truncation too.* Self-intersecting runs go from 1/12 to 9/12.
`PHerc0191` did not flip at all at the original budget --- zero dirty runs out of six ---
and flips 4 times out of 6 once released. *The traces were clean because they were short.*

#caveat[
  *Scope, and cost.* Two scrolls entered the verdict, not thirteen. A third, `PHerc0358`,
  goes the same way --- 19.83 to 211.43 cm#super[2], a factor 10.7, with 9907
  self-intersections --- but contributes only one run, and a single number does not
  disperse; including it would lower the median for a reason unrelated to the phenomenon,
  so our tooling excludes it *by name*. The campaign was stopped after 13 runs of 24
  because at the raised budget a single run takes 40 minutes against 2 to 4, the fringe
  growing with the generation count. Anyone tempted to "just raise the budget" should
  price that first.
]

The same artefact contaminates a comparison we had published. Two seed criteria were
compared on the same 13 scrolls, paired, one seed per criterion, everything else identical.
The sign test on the reached area gives 11--2 in favour of the planarity criterion,
$p = 0.0225$. But 7 of the 13 planarity traces stop at the budget --- and the two
"defeats" are exactly the two scrolls on which *both* criteria stop at the budget. Their
area differences, 0.09 and 0.001 cm#super[2], do not compare two criteria; they compare two
truncations at the same place.

#figure(
  image("figures/25_campagne_graines.png", width: 100%),
  caption: [
    The paired seed campaign. Each row is one scroll traced twice with everything held
    fixed but the seed. A chevron marks a trace stopped by the budget: on `PHerc0268` and
    `PHerc0800` both traces carry one. On the 11 informative pairs the sign test is 11--0,
    $p = 0.0010$.
  ],
) <fig:seeds>

#caveat[
  *We keep the conservative number.* The headline stays $11-2$, $p = 0.0225$, over all 13
  pairs. Publishing only the more favourable figure once one has seen which is more
  favourable is choosing one's sample after the fact. The two excluded pairs are excluded
  by a rule stated before looking at what excluding them does.
]

#caveat[
  *And we then failed to apply it to ourselves.* Every trace we made on `PHercParis4` ---
  the sixteen cells of the prediction cross, the eight seed candidates of
  #link(<sec:seedchoice>)[Section 5.3] --- was run at 60 generations, and all of them stop
  at generation 59. Their areas agree to *0.06 %* (0.3174 to 0.3176 cm#super[2]) across
  seeds separated by thousands of voxels in two different predictions. That agreement is
  exactly the signature this section teaches one to recognise, and we read it as nothing at
  all for a week. The budget itself was not a choice: it was set when we estimated render
  throughput at 57 KiB/s from a *single* observation, later measured at 1108--5861 KiB/s.
  #linebreak()
  The general lesson is worse than the local one. A setting adopted for a reason that has
  since stopped being true never announces itself; the *coherence* of the results it
  produces is precisely what makes it invisible. Eight traces agreeing to four significant
  figures look like a robust measurement.
]

== Seed choice does not predict convergence <sec:seedchoice>

#link(<sec:triage>)[Section 4] left one lever untried. Our seed finder ranks candidates by
*planarity alone*, and on one prediction the seed every earlier trace had used scored 1.0000
on *nine* supporting neighbours --- less supported than 0.987 on *twenty-seven*. Three
ten-thousandths separate the planarities while occupancy varies by a factor of thirty-five.

We did not invent a composite ranking to break the tie: choosing the weights is choosing the
answer before measuring it. We traced all eight candidates.

#figure(
  image("figures/48_candidats.png", width: 100%),
  caption: [
    Eight seed candidates on `PHercParis4`. Each property is drawn on *its own observed
    range*, printed above the column --- a full planarity bar spans 0.987 to 1.000, not 0 to
    1. Five candidates return a profile too flat to measure at all; three return
    $alpha approx 1$ --- and #link(<sec:footings>)[Section 3.6] shows that those three do
    not measure either. The properties vary widely; the outcome does not vary at all.
  ],
) <fig:candidates>

*Zero of eight converge.* The lowest $alpha$ obtained is $+1.01$ against a condemnation
threshold of 0.7. The five candidates of the second prediction all fall under the flat-profile
refusal of #link(<sec:twofailures>)[Section 3.5]: they report window *edges*, whose ratio is
the ratio of the windows, so $alpha approx 1$ by arithmetic identity whatever the volume
contains.

*And zero of eight measure.* The remaining three, which we first reported as yielding an
$alpha$, have their narrow window *below the instrument's detection floor*; two of them have
*both* readings pinned to the half-window. By #link(<sec:footings>)[Section 3.6] none of the
eight rests on two footings that carry a verdict. Of the 27 `PHercParis4` series in our tree,
*26 fall and one holds*: `ps256_sur_graine_ps256`, at $alpha = +1.12$ on two measured
footings, still condemning the trace. The wall stands on one measurement rather than
twenty-seven --- harder to state, and easier to defend, since twenty-seven numbers of which
twenty are the same arithmetic identity are not twenty-seven witnesses.

#caveat[
  *We decline to report a correlation, and that is the point.* Only three candidates yielded
  an $alpha$ at all --- and by #link(<sec:footings>)[Section 3.6], none of the three carries
  information. With eight points, the correlation detectable at 80 % power and
  $alpha = 0.05$ exceeds *0.84*: nothing short of a near-perfect relationship would be
  visible. A middling $rho$ here would not be an absence of effect, it would be an absence of
  power, and reporting it as the former is the most common way a null result is manufactured.
]

== A second ceiling: the render depth <sec:depth>

The budget of #link(<sec:ceiling>)[Section 5.2] is not the only one. Rendering a surface
flattens a window of $n$ layers around it, so a measurement of *how far the nearest matter
lies* cannot report a distance larger than that window. It reports the window.

We rendered the same 16 traces, across 4 scrolls, at two depths --- 21 and 41 layers --- and
paired them by identity rather than by list position.

#figure(
  image("figures/47_derive_profondeur.png", width: 100%),
  caption: [
    Left: each trace's distance to matter at both render depths, with the ceiling of *that
    trace* drawn as a vertical tick. Hollow red marks sit exactly on their ceiling: the
    value is the setting, not the surface. Right, on the *same rows*: a criterion with no
    ceiling --- a bounded fraction --- moving between the same two depths. A trace pinned
    to its ceiling on the left can still travel a long way on the right.
  ],
) <fig:depth>

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    table.header[criterion][compared][censored][median drift][max drift],
    [distance to matter (#um)], [*2*], [*14*], [88.939], [93.620],
    [share at profile edge], [16], [0], [*0.075*], [*0.450*],
    [share of flat columns], [16], [0], [0.153], [0.250],
  ),
  caption: [
    The same 16 traces at render depth 21 and 41. The ceiling doubles with the depth
    ($93.62 -> 187.24$ #um, a factor 2.00 for a factor 1.95 of depth), and 13 of 16 traces
    sit on it at the shallower depth, 10 of 16 at the deeper one.
  ],
) <tab:depth>

Two things follow. First, a threshold on the distance compares *settings* rather than
surfaces on 14 of 16 traces --- the same failure as the generation budget, in a different
part of the pipeline. Second, a criterion that *cannot* be truncated drifts anyway: a
median 0.075 on a quantity whose typical value is 0.5, and a maximum of 0.450, which is
almost the full range of the criterion, produced by changing nothing but the render depth.

#caveat[
  *The cohort has two ceilings, not one.* It mixes two voxel sizes, 8.64 and
  9.362 #um, so the ceiling is proportional to the scroll's voxel: 86.40 and 93.62 #um at
  the shallow depth. Drawing a single cohort-level ceiling makes the traces of the other
  voxel look as though they sit *below* the ceiling when they sit exactly *on* theirs, and
  half the censoring disappears from the figure without a single number changing. Each
  trace carries its own tick above.
]

The consequence for practice is not that a better reference must be found. It is that an
absolute threshold on such a criterion is not a statement about a surface. The convergence
test of #link(<sec:conv>)[Section 3] escapes this by construction: it is an *exponent*
relating two window sizes, so it has no reference, no threshold and no scale. A
profile-based criterion read the same way --- at two depths, as a ratio --- would inherit
the same property. We have not built it: it needs traces uncensored at both depths, and
this corpus contains two.

== Where a radial chain actually sits <sec:geom>

The neighbour mode projects a surface onto the next sheet, and chaining it produces a
sequence of surfaces that the convergence test does not condemn --- the first such
sequence we obtained. It is tempting to read that sequence as a piece of unrolled papyrus.
It is not.

To locate a surface inside a scroll one would normally need the scroll's axis, which is
unknown. The following observation removes the need. On a cylinder, a grid line running
along the circumference *curves*; a line running along the axis is *straight*. One does not
need to know where the axis is to know which grid direction is which --- only which one
bends.

Curvature is read from the *sagitta* of the arc, the maximum distance between the arc and
its chord. For an arc of half-angle $phi$, the chord is $2R sin phi$ and the sagitta
$R(1 - cos phi)$, so

$ phi = 2 arctan ( (2 s) / c ) , $ <eq:sagitta>

with $s$ the sagitta and $c$ the chord, exactly and with no small-angle approximation.
The radius cancels, which is what makes the quantity usable where the radius itself is not
determined.

#figure(
  image("figures/44_geometrie_chaine.png", width: 100%),
  caption: [
    Nine consecutive surfaces of a radial chain, located inside the scroll without knowing
    its axis. Each covers between 7.7 % and 11.8 % of one revolution, and consecutive
    surfaces sit a median 113 #um apart --- one sheet.
  ],
) <fig:geom>

The measurement gives the median gap between consecutive surfaces as 113 #um
(range 100--138), which is one sheet: the chain advances one sheet at a time, as designed.
But each surface covers only about a tenth of a turn, and consecutive surfaces occupy *the
same angular window*. Along the papyrus they are separated by a full circumference that we
do not possess.

#block(stroke: (left: 1.6pt + rgb("#1f6f43")), inset: (left: 0.8em, y: 0.5em))[
  A radial chain is a *column*, not a *strip*. Gluing its members end to end would produce a
  band of papyrus that does not exist. Reaching a *length* of unrolled text requires a
  tangential chain.
]

Erosion bounds such a chain before quality does. On the surface actually carrying material
--- not the grid --- it is 15.6 % per turn, so half is gone in four turns; the fraction of
valid vertices falls from 58 % to 23 % along nine wraps.

== Growing sideways, and a fixed point <sec:chain>

The natural response is a *tangential* extension: let a published segment keep growing
along itself. It works, once.

#figure(
  table(
    columns: (1fr, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    table.header[surface][useful area][arc][valid vertices][$alpha$],
    [published segment, as downloaded], [4.28 cm#super[2]], [21.9 mm], [59 %], [$+0.000$],
    [after one extension], [*12.97* cm#super[2]], [*37.2* mm], [*96 %*], [$bold(+0.000)$],
  ),
  caption: [
    One tangential extension of a converging published segment. Three times the useful
    area and 70 % more arc, and the convergence test still does not condemn it.
  ],
) <tab:ext>

#figure(
  image("figures/44_extension.jpg", width: 88%),
  caption: [
    The extended surface, rendered. The material is continuous across the extension; the
    periphery is where the newest --- and worst --- vertices live.
  ],
) <fig:ext>

#caveat[
  *The first time we measured this, it was a coin flip, and saying so is the point.* Three
  runs of identical parameters gave 0, 596 and 0 self-intersections, and $alpha$ of
  $+0.000$, $+0.422$, $+0.000$. Pinning the generator's seed and forcing a single thread
  makes it reproducible --- two runs then give the same mesh, bit for bit --- and every
  figure above is from the pinned configuration. A result that replicates two times out of
  three is not a result, and it took a repetition to see it.
]

More growth does not give more surface. At budget 200 the area reaches 28.62 cm#super[2]
with 25 036 self-intersections and $alpha = +1.313$; split into two sessions of 100 it
reaches 50.30 cm#super[2] with 4996 crossings and $alpha = +1.040$ --- better, and still
across the stack. What decides the outcome is not the size of the step but *how clean the
surface it starts from is*, measured on its periphery.

That gives a repair. Every vertex carries the generation at which it was created, so
trimming the late periphery is a filter, not a guess. Trimming to the first ten generations
returns 6.02 cm#super[2] with a periphery as clean as the source's --- 41 % more validated
material than the published segment, at $alpha = +0.000$.

#block(inset: (left: 0.8em, y: 0.5em), stroke: (left: 1.6pt + rgb("#b03030")))[
  *And then the cycle closes on itself.* Extending that clean surface again also converges,
  but trimming the result back to a clean periphery returns 6.02 cm#super[2] again,
  exactly. The trim-and-extend cycle does not diverge; it *converges to a fixed point near
  6 cm#super[2]*. Each turn regains what it just gave up.
]

We report this because a cycle that appears to work for one iteration is exactly what a
reader would extrapolate from, and it does not.

== Published segments do not tile a sheet <sec:merge>

The remaining route to a continuous strip is to stitch published segments together. The
tool exists and needs surfaces that *overlap*.

`PHerc1447` publishes 15 segments. Of their 105 pairs, 51 overlap by bounding box, many by
90--100 %. But a box overlap cannot tell "two patches of one sheet" from "two adjacent
sheets", which in a scroll occupy nearly the same volume. The discriminant is the median
point-to-point gap.

#figure(
  image("figures/44_ecarts_segments.png", width: 100%),
  caption: [
    Every overlapping pair of published segments, placed on its median point-to-point gap
    (logarithmic axis). The band below the same-sheet threshold is *empty*, and the closest
    pair in the whole scroll is still 79 #um away --- twice the threshold, and of the
    order of the measured inter-sheet spacing.
  ],
) <fig:segments>

#figure(
  table(
    columns: (auto, 1fr, auto),
    align: (left, left, right),
    table.header[median gap][meaning][pairs],
    [$< 40$ #um], [two patches of the *same sheet* --- mergeable], [*0*],
    [40--250 #um], [*neighbouring* sheets --- must not be merged], [2],
    [$>= 318$ #um], [several sheets apart], [45 measured, 4 out of reach],
  ),
  caption: [
    Pairwise gaps among 15 published segments of `PHerc1447`. Establishing this cost 4.5 MB
    of download and a few seconds.
  ],
) <tab:segments>

The published segmentation of this scroll is a set of samples --- *one patch per sheet* ---
not a tiling of one sheet. There is nothing to stitch. Combined with the fixed point of
#link(<sec:chain>)[Section 5.6], both named routes to a continuous strip are measured and
closed, each for its own reason.

= Discussion <sec:disc>

== Repetition is the cheapest available improvement

Every finding in #link(<sec:results>)[Section 5] came from doing the same thing twice.
The tracer's non-determinism is invisible in one run. The truncation artefact is invisible
without a second budget. The coin-flip nature of the tangential extension is invisible
without a third repetition. None required a new algorithm, a new dataset, or a new model.

The primary literature publishes neither repetitions nor error bars for the segmentation
step. Given a tool that returns a different surface on every call, a single reported
surface is a sample from a distribution whose width is not reported --- and we measure that
width to be, in the extreme, 115 % of the mean.

== What a point estimate costs <sec:interval>

#link(<sec:community>)[Section 2.4] says that no interval is published anywhere in the
toolchain we read. This section is what one costs to compute, and what it changes, on the
only quantity in this field for which a ground truth exists.

Detached fragments publish `inklabels.png` aligned to their surface layers, so an ink map can
be scored against labels rather than against another rendering. On three of them our chain
returns AUC $0.746$, $0.600$ and $0.575$ --- a spread of $0.171$ that reads as a fragment
effect, and that we initially treated as one.

*The usual standard error says the spread is certain, and it is the wrong formula.*
Hanley--McNeil gives $0.00055$, $0.00072$ and $0.0024$ on these maps, which would make the
observed gap a hundred standard errors wide. That formula assumes independent draws. An ink
map is not: neighbouring pixels carry almost the same value and almost always the same label,
so a million pixels are not a million observations. Resampling instead *by tile* --- the scale
at which the spatial structure exists --- gives $0.060$, $0.071$ and $0.082$ ---
wider by $109 times$, $99 times$ and $34 times$.

*And a variance decomposition removes the effect entirely.* Tile-to-tile dispersion *within* a
fragment is $sigma = 0.2243$; dispersion *between* fragments is $0.0391$. The within term is
$5.7 times$ the between term, the intraclass correlation is $0.030$, and separating the
observed gap would take *27 tiles per fragment* where we had 10, 11 and 2. The three numbers
do not compare. What looked like a property of three objects is the noise of a single window.

#caveat[
  *The same point estimate hid a second thing: how many questions we had asked.* We tested six
  measurable quantities against the same AUC over 23 tiles, looking for one that predicts it.
  The strongest is median component area at $rho = -0.448$; after a permutation test with 5000
  draws and a Holm correction, *none survives* --- the best reaches $p = 0.187$. Among them is
  $sigma$, the output dispersion this repository had been reading for weeks as evidence that a
  model is reading rather than idling. It ranks *fourth of six*, at $p = 0.739$. We retracted
  the inference rather than the correction.
]

== The truncation artefact generalises beyond this pipeline

The mechanism is not specific to one tool. Any iterative fitting procedure with a budget
will, on the instances where the budget binds, produce outputs that agree with each other
for a reason that has nothing to do with the instance. Reporting a dispersion over such
outputs measures the budget. The diagnostic is cheap: record the stopping condition
alongside the result, and check whether the low-variance instances are the ones that hit
it.

We met the same mechanism three times in this work, in three unrelated parts of the
pipeline: the generation budget of the tracer (#link(<sec:ceiling>)[Section 5.2]), the
render window of the flattening step (#link(<sec:depth>)[Section 5.4]), and --- in the
opposite direction --- the fact that the *absence* of a stopping condition is what made the
convergence test of #link(<sec:conv>)[Section 3] transportable. A quantity that a setting
can cap is a quantity whose reported spread is, in part, a property of the setting.

== The same move works one step downstream <sec:downstream>

The instruments above judge *geometry*. The field's only ground-truth-free argument about
the *reading* step has the same shape, and the same gap. Defending what it reads on hidden
layers, the foundational paper writes that "the scale, line separation, and script of the
revealed characters are consistent with those observed on the fragment surfaces"
@seales2023. The form is right — a verifiable region, an unverifiable one, and confidence
transported by second-order statistics. It is left to the eye.

All four quantities are measurable without reading a letter: line spacing by
autocorrelation of the row-density profile, character scale by connected components, ink
coverage, and stroke width by the distance transform. We measured them on 190 published ink
maps across four scrolls, and crossed them against the published ink contrast of one
scroll's 80 maps, split at its median.

#figure(
  image("figures/45_typographie.png", width: 100%),
  caption: [
    Each typographic quantity against the published ink contrast, as an AUC (0.50 = no
    association). Three recover the ranking. *Coverage is quasi-tautological* — the
    published contrast is built on ink percentiles — so the informative agreements are
    stroke width (0.857) and peak sharpness (0.753), which are genuinely different
    quantities obtained by a distance transform and an autocorrelation. Right: the same 80
    maps behind the one quantity that runs the other way.
  ],
) <fig:typo>

⚠⚠ *And the three properties the sentence groups together do not go together.* Line
separability runs *against* the contrast (AUC 0.319, $rho = -0.281$). The association is
weak and not monotone — it falls over the first three quartiles and then flattens — and we
do not present the obvious mechanism (heavier ink, lines closer to merging) as established.
What matters here is the form of the finding: *an eye that judges a page "consistent" cannot
see that two of its properties point in opposite directions. A number can.*

#caveat[
  *And this instrument has the same shape of limit as the first.* A prediction that fails
  the typographic test is certainly not text; one that passes may be a periodic artefact —
  necessary, never sufficient, exactly as the absence of self-intersections is for a traced
  surface. Its periodicity floor is derived rather than chosen: white-noise autocorrelation
  over $k$ lags of an $n$-point profile peaks near $sqrt(2 ln k) \/ sqrt(n)$, so the floor
  rises by itself on a smaller map.
]

== The control the field does not have <sec:negctrl>

The same paper reports a false-positive rate for its ink detector @seales2023, measured on
images that contain ink all around. It never measures what the detector returns on a
substrate *known* to carry none. The ideal control was in the scan --- the paper sheet the
fragments are mounted on, imaged in the same session at the same voxel --- and the
preprocessing removes it: "These are removed manually."

A traced surface with a high convergence exponent is a better control than a paper backing,
and it costs nothing extra. A surface with $alpha approx 1$ has a *geometric proof* that no
papyrus face is within reach: its distance to matter follows the render window. Any ink
reported there is a false positive by construction. We ran the published ink model on such a
surface and, as a positive control, on the official segment of the *same scroll* --- same
volume, same voxel, same model, same region size, same stride. The only thing that differs
is whether there is a sheet under the surface.

#figure(
  image("figures/46_temoin_negatif.png", width: 100%),
  caption: [
    Top: what the model received --- a woven papyrus face against a slice cut across the
    stack, two textures no eye would confuse, differing by 11.0 % in dispersion. Middle:
    what it returned, on a *shared* colour scale. Bottom: the gap between the two outputs
    against the gap two unrelated maps would show.
  ],
) <fig:negctrl>

#caveat[
  *This section was rewritten on 2026-08-28, and its conclusion changed sign.* The
  measurement first published here was taken with a normalisation constant that divided
  `uint8` stacks by 65535 instead of 255, so the model was shown near-black and returned
  near-constants --- and two near-constants correlate perfectly. The $rho = +0.9979$ we
  reported was not a fact about the detector, it was the signature of that bug. With the
  constant fixed, the intended claim is *in* reach, and it is established.
]

The detector now responds. On the positive control --- an official segment of the same
scroll, on a real sheet --- it returns $sigma = 0.5894$, which is 76.4 % of the 0.7712 it
returns where it reaches an AUC of 0.925. There is a working detector to control.

#emph[And it reports as much structure where no sheet can be.] On the negative control, a
surface whose geometry rules out any papyrus face within reach, it returns
$sigma = 0.7111$ --- *more* dispersion than on the real sheet, a ratio of 0.83, and a
larger contrast as well (1.869 against 1.471).

The two maps are not the same map. Pixel to pixel they correlate at $rho = -0.0100$, and
their median difference is 66.8 % of what each map itself varies by --- against 95.4 % for
two fully unrelated maps of the same dispersion, a value derived rather than
chosen.#footnote[For two independent maps of dispersion $sigma$, the difference has
dispersion $sigma sqrt(2)$, so the median of its absolute value is
$0.6745 sigma sqrt(2) = 0.9539 sigma$.] So the model does respond to its inputs, and the
residual 66.8 % against 95.4 % says the two outputs still share something --- the texture
of the block, most plausibly --- that this control does not separate.

#emph[The conclusion is harder than the one we first published, not softer.] A stuck model
is easy to catch: it returns the same thing twice. A model that hallucinates a *different*
and convincing structure on every input, including inputs that cannot carry ink, is caught
by no inspection of its output. That is precisely what the founding paper never measures.

The boring explanation is excluded by measurement rather than by argument: both input
windows are full and different --- 93.4 % and 100 % non-zero, dispersions 39.26 against
34.95.

#caveat[
  *What this control cannot yet answer.* The periodicity result of Section 5 rests on a
  pixel-shuffle control, which destroys all spatial structure. A real negative control ---
  a surface that is not a sheet but keeps the texture of the block --- asks a harder
  question: are our maps periodic where a sheetless surface is not? At the calibrated
  setting these two 1100 #sym.times 1100 controls yield *one* window each, so the test
  correctly refuses. Answering it requires a negative control of at least about
  2100 #sym.times 2100 map pixels, and until that render exists the periodicity claim says
  what it says and no more.
]

The generalisable part is the design. A negative control for an ink detector does not
require a special acquisition or a substrate known to be blank. It requires a surface whose
*geometry* rules out the thing being detected, and any pipeline that can trace surfaces can
produce one deliberately.

It also yields a cheap entry condition for a question this field has not answered: *does
repairing a trace improve what is read from it?* Answering it requires a faulty trace, its
repaired version, and the same downstream applied to both. On this scroll the downstream
cannot separate them --- a difference far larger than any repair leaves the output
unchanged. Before spending compute on such an experiment, one can measure whether the
detector responds on the target scroll at all: one inference on one window, and compare its
dispersion to what the model returns where it is known to work.

Applied across the prize set, that condition is restrictive. Crossing the scrolls we can
trace with those whose published ink maps carry the typographic statistics of a written page
(#link(<sec:downstream>)[Section 6.4]) gives an *empty* intersection: 13 against 3, disjoint.
The experiment is therefore not mountable on the prize set as it stands --- not because
repair cannot be measured, but because the scrolls where it could be read are not the ones
that have been traced. Naming that before running the experiment is cheaper than discovering
it after.

== Where a measurement like this plugs in <sec:plug>

A quality signal is only useful if something consumes it. The pipeline that produced the
complete unwrapping @angelotti2026complete consumes exactly one, and it is painted by hand.

Its published code#footnote[`github.com/ScrollPrize/villa`, commit
`e583fb67468f483fadd73d52e06f0ab0fe5ba813`, cited as the reproduction commit of
@angelotti2026complete.] carries a tool named `ApprovalMaskBrushTool`: a brush, with
`Approve` and `Unapprove` modes, strokes and an undo stack. It is how an annotator marks
the regions the paper describes as "judged geometrically consistent with a single sheet",
and it is where the reported cost is spent --- roughly 25 hours per wrap, about 775 hours
for one scroll.

Two things follow. The first is that the predicate is *the same one $alpha$ estimates*: a
region is approved when a human believes the surface there follows one sheet, which is the
question a convergence test answers by changing the render depth and reading the response.
The manual gesture and the measurement are not adjacent, they are the same judgement made
two ways.

The second is that the interface is a file. A surface is stored as a `tifxyz` directory
holding `x.tif`, `y.tif` and `z.tif`; the loader adopts *any* other `.tif` in that
directory as a named channel, and the channel called `approval` is what gates the
subsequent mesh re-optimisation.#footnote[`core/src/QuadSurface.cpp` (channel discovery)
and `core/src/GrowPatch.cpp` (`make_approved_mask`), at the commit above.] Writing
`approval.tif` beside the coordinates is the whole of the integration --- no fork, no
patched call site.

#caveat[
  *We have not done this, and the gap is worth stating precisely.* We have not rendered an
  approval mask from $alpha$, and we have not compared one to a human-painted mask, because
  we have found none published. What the paragraph above establishes is that the output has
  a named destination and that the destination costs nothing to reach; whether a computed
  mask is *good enough to replace a brush* is an open question, and the honest first step is
  to obtain one human mask to score against.
]

== What a good measurement looked like here

Three properties recur in the instruments above and are worth naming.

/ Compare a thing to itself: the convergence test changes a rendering parameter and reads
  the response. No reference surface is needed, which is precisely what a sealed scroll
  denies.

/ Prefer a dimensionless quantity: $alpha$ needs no threshold in microns, so it transfers
  between scrolls, resolutions and inter-sheet spacings without recalibration.

/ Make the refusal explicit: several of our tools decline to answer rather than guess ---
  on fewer than two windows, on windows too close together, on a scroll with a single run,
  on a pair where both members hit the budget. Each refusal was added after an instance
  where guessing produced a plausible and wrong number.

= Limitations <sec:lim>

+ *$alpha$ has a resolution of about $plus.minus 0.2$ on two windows* (#link(<sec:resolution>)[Section 3.4]). Counts of
  verdicts near the boundary are counts of coin flips, and we treat them as such.

+ *$alpha$ is a median and hides a minority.* A surface can converge while a fraction of
  its windows has no sheet within reach. We report that fraction alongside, and the two
  measurements do sometimes disagree.

+ *The budget experiment covers two scrolls*, not the seven that plateau. It establishes
  that truncation explains the low dispersion where it was measured, not that every
  plateaued scroll behaves so.

+ *The remote triage does not replicate* outside `Scroll 1` (#link(<sec:triage>)[Section 4]), and we do not know why.
  One of three negative corpora is explained by a floor effect; two are not.

+ *We do not know why a wrap fails.* Across four campaigns and forty wraps, the best
  predictor of a wrap's $alpha$ is its ordinal position in the chain
  ($rho = +0.53$, $p = 0.001$) --- better than erosion, arc length, area or any
  single-render statistic we tried. Depth is a clock, and we cannot yet separate it from a
  cause.

+ *The relative criterion is proposed, not built* (#link(<sec:depth>)[Section 5.4]). We
  show that an absolute threshold on a profile criterion compares settings; we do not show
  that reading the same criterion as an exponent works. It needs traces uncensored at both
  depths --- 92 of our series qualify --- so what is missing is the definition of the
  criterion, not the material to build it on.

+ *$alpha approx 1$ has two causes and does not separate them* (#link(<sec:twofailures>)[Section 3.5]).
  A flat profile yields $alpha approx 1$ by identity. Both causes condemn the trace, and no
  converging verdict is affected, but 24 of 111 series in our tree cannot be said to be
  *across the stack* rather than *unmeasured*.

+ *The negative control establishes the strong claim* (#link(<sec:negctrl>)[Section 6.5]).
  On the one scroll where we have both a sheet-following and a stack-crossing surface, the
  ink model reports *more* dispersion on the surface that cannot carry ink (0.7111 against
  0.5894), while returning two unrelated maps ($rho = -0.0100$). It reports ink where there
  is no sheet, and nothing in its output distinguishes that from a real detection. This
  rests on one scroll and one model.

+ *A render's cost is dominated by a setting nobody had set, and by a wall nobody had
  measured.* Our renderer's Zarr chunk cache defaults to 16 GB; none of the 28 call sites
  in our tree set it. On small surfaces this is invisible --- the cache is allocated lazily
  and never fills. On a 3.66 cm#super[2] surface it fills, and together with the output
  buffers the process held *28.2 GB* on a 32 GB machine: 274 MB free, 3.4 GB swapped, and
  *23.7 % of one core* while 22 sat idle and the process carried 59 threads. It was not
  computing; it was waiting on memory. Capping the cache at 1 GB is measured to be both the
  smallest peak and the fastest median over 15 runs (peak *1.81 GB* against
  *4.53 GB* at the default), with all 15 outputs byte-identical --- which is what
  licenses changing the setting at all.
  #linebreak()
  The wall behind it is harder. Buffers scale as area times depth: 41 layers of that
  surface need 9.7 GB, 161 need *38.2 GB*, and no cache setting moves that. The deep window
  of our own convergence test is therefore not slow on this machine, it is *impossible* ---
  a fact no amount of patience discovers, and one that our published cost caveat
  (#link(<sec:ceiling>)[Section 5.2]) priced in minutes when it should also have priced in
  gibibytes.

+ *Nothing here reads text.* The measurements judge geometry. A surface that passes every
  test in this paper may still carry no ink.

= Conclusion

Segmentation quality can be measured on a sealed scroll, without ground truth, without a
physical threshold and without a scale, by comparing a surface to itself under a change of
rendering depth. Doing so on 13 prize scrolls shows that the reference tracer is a draw
rather than a function, that the stability and cleanliness usually read as signs of a good
trace are artefacts of the generation budget, that the render window imposes a second
ceiling of the same kind, and that the published segmentation of a prize scroll samples
sheets rather than tiling one. Each of the four was found by repeating a measurement that
the field currently performs once. The same construction that judges a surface also
supplies what the field's reading step lacks: a surface whose geometry rules out a papyrus
face is a negative control that costs one extra render. And the judgement it automates is
the one the field currently pays for by hand: the predicate behind an approval mask, whose
integration point is a single `.tif` written beside a surface's coordinates
(#link(<sec:plug>)[Section 6.6]).

#v(0.6em)
#block(inset: (left: 0.8em, y: 0.5em), stroke: (left: 1.6pt + rgb("#404040")))[
  *Reproducibility.* Every figure in this paper is produced by a script from a versioned
  result file, and every number quoted in the text is recomputed from that file and
  searched literally in the source of the paper by an automated guard. We audited that
  discipline against itself: of 105 verification batteries in our tree, *39 printed a
  pass unconditionally* and could not fail, a defect found by accident while probing
  something else. The rule the guard
  enforces is the one we would offer as the paper's methodological summary: *a published
  number whose computation is not in the tree is not a result, it is an anecdote.*
]

#v(1em)
#line(length: 100%, stroke: 0.4pt)
#v(0.5em)

#bibliography("references.bib", title: "References", style: "institute-of-electrical-and-electronics-engineers")
