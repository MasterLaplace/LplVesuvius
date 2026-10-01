// vesuve 0.3.0: the September 2026 Progress Prize submission, as a preprint.
// Build from the repository root, so that the figures under examples/ resolve:
//   typst compile --root . paper/vesuve.typ paper/vesuve.pdf
// Every number below is carried by a registry fact of the research (R4-F...), cited where it is used, and the
// equations are those of FORMULARY.md, which is rendered from the code.
#set document(
  title: "Correcting the transfer to the next winding without a human, and judging it by the text it carries",
  author: "Guillaume Papineau",
)
#set page(paper: "a4", margin: (x: 2.4cm, y: 2.6cm), numbering: "1", number-align: center)
#set text(font: ("New Computer Modern", "DejaVu Serif"), size: 10pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 0.78em, first-line-indent: 1.2em)
#set heading(numbering: "1.1")
#show heading: it => block(above: 1.4em, below: 0.7em)[
  #set text(weight: "bold", size: if it.level == 1 { 12pt } else { 10.5pt })
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

#let um = [μm]
#let ORCID = "0009-0006-1371-4119"
#let fact(id) = text(size: 8.6pt, font: ("DejaVu Sans Mono", "DejaVu Sans"))[#id]
#let caveat(body) = block(
  inset: (left: 0.8em, y: 0.5em), stroke: (left: 1.6pt + rgb("#b03030")),
  text(size: 9.4pt)[#body],
)
#let repo = "https://github.com/MasterLaplace/LplVesuvius"
#let slice(n, file) = link(repo + "/blob/experimental/docs/archive/" + file)[#raw(n)]

#align(center)[
  #block(width: 92%)[
    #text(size: 16pt, weight: "bold")[
      Correcting the transfer to the next winding without a human,
      and judging it by the text it carries
    ]
    #v(0.4em)
    #text(size: 11.5pt)[vesuve 0.3.0, a submission to the September 2026 Progress Prizes]
  ]
  #v(1.1em)
  #text(size: 10.5pt)[Guillaume Papineau]
  #v(0.3em)
  #text(size: 9pt, style: "italic")[Independent researcher]
  #v(0.25em)
  #text(size: 9pt, font: ("DejaVu Sans Mono", "DejaVu Sans"))[guillaume.papineau\@epitech.eu]
  #v(0.2em)
  #text(size: 9pt)[ORCID iD #link("https://orcid.org/" + ORCID)[#ORCID]]
  #v(0.5em)
  #text(size: 9pt)[Preprint, 1 October 2026 · code and data: #link(repo)[#repo]]
]

#v(1.2em)

#block(width: 100%, inset: (x: 1.6em))[
  #set text(size: 9.3pt)
  #set par(first-line-indent: 0em)
  *Abstract.* Virtual unwrapping fits a surface to one sheet of a carbonised scroll inside an X-ray tomogram. When
  the surface slips onto the neighbouring winding, a human finds the switch and repairs it; the Vesuvius Challenge
  names these sheet switches a bottleneck and asks for conservative failure detection. We present `vesuve`, one
  program with one pipeline per prize, and three hand-free steps it performs on a published PHercParis4 segment.
  It *certifies* where the surface stayed on one winding, by closing loops on a lattice of steps between chunks:
  6333 of 97771 chunks. It *produces* the next winding from the published surface prediction, by taking the first
  sheet along each normal and letting neighbours vote: 92.14 % of the points land on the right winding, against
  76.13 % for a fixed step. It *corrects* the points that slipped, by modelling each chunk's departure from its
  neighbourhood as noise or a one-winding slip: 163 misses become right for 41 rights made misses (sign test
  $p = 2.04 times 10^(-18)$), and no judge takes part in any decision. Where the segment passes over the winding
  it produced, the published ink map says what text that winding must carry; our ink reading of the produced
  winding correlates with it at 0.83, against 0.12 and 0.10 for two controls, and at 0.87 one jump further. On a
  second band the correction does not hold, and the program measures that and writes nothing there. Every number
  is replayed by a test against the research function that produced it, and the inputs of the correction are
  rebuilt from public data byte for byte.
]

= Introduction

A Herculaneum scroll is read in three stages: a tomogram of the closed scroll, a surface fitted to one sheet of
papyrus inside it, and an ink model applied to that surface once flattened @seales2023 @angelotti2026complete. The
middle stage, segmentation, is where most human time goes. A surface that follows its sheet for a few centimetres
and then slips onto the neighbouring winding produces a flattened image that mixes two texts, and today a human
finds the switch and repairs it. The Challenge's 2026 Open Problems page names sheet switches as a bottleneck and
asks for "conservative failure detection" #footnote[#link("https://scrollprize.org/2026_open_problems")].

This report describes the parts of that job that `vesuve` does without a human, on real data, and where it stops.
Its contributions are four, each carried by a dated research slice and a registry fact:

+ a *certificate*: loops closed on a lattice of steps between neighbouring chunks say which chunks of a published
  surface stayed on one winding (#slice("246", "246_la_couverture_sans_main.md"), #fact("R4-F410"));
+ the *next winding*, computed from the published surface prediction `m7` rather than drawn by hand
  (#slice("247", "247_le_transfert_retrouve_t_il_la_spire_voisine.md"), #fact("R4-F412"));
+ a *correction* of that transfer where a point slipped, decided without a judge
  (#slice("275", "275_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.md"), #fact("R4-F456"));
+ a *judge by the text*: where the segment passes over the produced winding, its published ink map says what text
  that winding must carry (#slice("296", "296_le_tour_produit_porte_t_il_le_texte_du_segment.md"),
  #fact("R4-F477")).

The research behind them is a series of 402 dated slices on the `experimental` branch, each asking one question,
declaring its rule before measuring, and keeping its negative results. The program on `main` ports only what a
slice established, and its tests replay each ported number against the research function that produced it.

= Related work

Recent Progress Prize work attacks the same failure while a surface is built. Stevens assembles unwrappings from
patches and detects incompatible 3D locations, so that sheet switches are avoided during the assembly
@stevens2026; ScrollFiesta extracts surfaces from the prediction cube by cube and welds them into sheets
@scrollfiesta2026. Both produce surfaces. `vesuve` starts from a surface that is already published and asks two
other questions: which parts of it stayed on one winding, and how to repair the next winding with a decision no
judge takes part in, whose rate of error is then measured. Neither its certificate nor its correction depends on
how the mesh was made; we have not yet run them on meshes from these tools.

= Data

All data are public and read from the Challenge's bucket.

- *PHercParis4, segment `20230702185753`*: its surface volume, read chunk by chunk; its published mesh; its
  published ink map; and, as the only judge, the next winding the segment's own tracer drew by hand. For rendering,
  the raw scan the segment was cut from, at 2.4 #um (`20260411134726`).
- *The surface prediction `m7`*, sampled along the normals of the mesh. The samples are embedded (0.5 MB, one bit
  per sample) and can be read again from the bucket (1780 chunks, about 630 MB).
- *PHercParis4, band `20260623142658-w028-037`*: a second surface, where the correction was measured not to hold.
- *PHerc1447, segment `20250702235910`*, for First Letters, and the innermost published PHercParis4 bands
  (`w010-027`), for the title search.

= One program, one pipeline per prize

`vesuve` is a Python package over a small C core, shipped as one Docker image. Each prize has its pipeline, and each
pipeline writes a dated report that says where it stops (@tab-pipelines).

#figure(
  table(
    columns: (auto, 1fr),
    align: (left, left),
    [pipeline], [what it produces on real data, and where it stops],
    [`grand-prize`], [the per-chunk certificate (6333 of 97771 chunks), the certified surface, the next winding
      computed from `m7`, and that transfer corrected without a hand; it still has to read 111 bands (24263 chunks)
      to judge the rest],
    [`progress`], [where a published segment changes winding: column 260, rows 26 to 223, where the loop's
      cumulative closure crosses half a sheet at cuts 163, 173 and 203 (#fact("R4-F401"), #fact("R4-F406"))],
    [`first-letters`], [a 4 cm² window chosen on papyrus alone, its fibre render and ink; on PHerc1447 the 2023 model
      shows no periodic rows (#fact("R1-F20")), so it claims no letters],
    [`paris4-title`], [the last written column of the innermost band and the region after it, where an end-title
      would sit, for a papyrologist to judge],
  ),
  caption: [The four pipelines of `vesuve` 0.3.0. Their dated reports are in `examples/`.],
) <tab-pipelines>

The rest of this report follows the `grand-prize` pipeline, which carries this month's result.

= Method

Distances are in voxels of 2.4 #um. The published sheet-to-sheet step is $s = 173$ #um, and half a sheet is
$delta = "round"(s \/ (2 v)) = 36$ voxels; it is both the search range of a step and the threshold of every
decision below (#fact("R4-F14")).

== Certifying where a surface stayed on one winding

The surface volume is cut into chunks. Between neighbouring chunks, a step says how far the sheet moves across their
seam; at each seam the consensus is the median of the lines of a band that are present, if a majority of them is
(#fact("R4-F378")). Around a loop of four chunks, two paths lead from one corner to the other:
$
  L = H(r_0; c_0 -> c_1) + V(c_1; r_0 -> r_1) - H(r_1; c_0 -> c_1) - V(c_0; r_0 -> r_1).
$
A geometry closes it exactly; a surface that switched winding inside the loop leaves a whole sheet in it. Along a
row of loops, the profile $P_j = sum_(i <= j) L_i$ must stay within half a sheet, $|P_j| < delta$ for every $j$
(#fact("R4-F393")). Chunks enclosed by loops that close are certified; the others are named, with the bands that
would have to be read to judge them.

#figure(
  image("../examples/grand-prize/chunk_mask.jpg", width: 46%),
  caption: [The certificate of segment `20230702185753`, as `vesuve grand-prize` writes it. Green: certified chunks;
    grey: present and not certified. Outlines: blue, the loops it would still have to read; orange, a loop whose
    closure crosses half a sheet.],
) <fig-mask>

== Producing the next winding

Along the normal $n_k$ of each mesh point $x_k$, from the surface out to three steps, the prediction $P$ ($f$ times
coarser than the scan) marks runs of samples. The centre of each run is a sheet the next winding may land on:
$
  C_k = { (t_a + t_(b-1)) / 2 : [a, b) "a maximal run of" P(floor((x_k + t_i n_k) / f)) > 0 },
  quad t_i = sigma i, quad 0 <= i <= floor(3 s).
$
The starting choice $tau_k^((0))$ is the first run after the surface's own, the run within 12 voxels of the
surface. Then every point moves at once to the sheet its own ray sees nearest to its neighbours' median, within
half a sheet:
$
  mu_k^((r)) = "med"{tau_j^((r)) : j in W_k} quad "if" |W_k| >= 5, wide
  tau_k^((r+1)) = cases(
    op("argmin", limits: #true)_(c in C_k) |c - mu_k^((r))| & "if" min_(c in C_k) |c - mu_k^((r))| < delta,
    mu_k^((r)) & "otherwise",
  )
$
where $W_k$ is the three by three square of mesh cells centred on $k$. The vote stops when fewer than one point in
a thousand moves by more than half a voxel, thirty rounds at most, and the transfer is $y_k = x_k + tau_k n_k$
(#fact("R4-F412")).

== Correcting the points that slipped, without a judge

The depth of the sheet in every chunk is walked by least squares on the window-to-window steps $s_(i j)$ of the
seams, once on the reference and once on the produced winding (#fact("R4-F440")):
$
  hat(D) = op("argmin", limits: #true)_(D, sum_c D_c = 0) sum_((i, j)) (D_j - D_i - s_(i j))^2.
$
A block is anchored on its neighbours only, so that its own slip cannot pull its anchor (#fact("R4-F446")):
$a = "median" lr(\{ hat(D)^p_c - hat(D)^r_c : c in cal(N) without B \})$. The departure $x$ of each chunk from
its anchor is noise or a slip of one winding above or below,
$
  x tilde w_0 cal(N)(0, sigma^2) + w_+ cal(N)(g, sigma^2) + w_- cal(N)(-g, sigma^2),
$
with the weights and the shared width fitted by expectation-maximisation, and the slip $g = 69.458$ voxels read
without a judge (#fact("R4-F445")). A point is brought back by its departure, $tau_1 = tau_0 - x$, only when a slip
explains that departure better than the noise:
$
  max(w_+ e^(-(x - g)^2 \/ (2 sigma^2)), w_- e^(-(x + g)^2 \/ (2 sigma^2))) > w_0 e^(-x^2 \/ (2 sigma^2)).
$
No judge takes part in this rule (#fact("R4-F456")). The hand-drawn next winding is used only afterwards, to score.

== Judging the produced winding by its text

The segment makes more than one turn, so in places it passes over the very winding the transfer produced, one turn
further along its own surface. There, its published ink map says what text the produced winding must carry: a judge
that knows nothing of the transfer. We read the ink of the produced winding $I$ with the model that made the
published map (`scrollprize/ink_canonical_2um`), and compare it with the published map $J$ at the counterpart
$phi(u)$, on the mask where the segment passes within half a sheet, $M = {u : |d(u)| < delta}$:
$
  r = (sum_M (I - overline(I)) (J compose phi - overline(J compose phi)))
      / sqrt(sum_M (I - overline(I))^2 sum_M (J compose phi - overline(J compose phi))^2).
$
The six blocks were chosen from the meshes alone, before any ink was read on them.

= Results

== The next winding

Computed from the prediction, the transfer lands on the right winding for 92.14 % of the points of the segment
(@tab-transfer). The program gives back the research's transfer point for point, within a millionth of a voxel, on
the segment and on the band.

#figure(
  table(
    columns: (1fr, auto),
    align: (left, right),
    [rule], [points on the right winding],
    [a fixed step], [0.7613],
    [first sheet along the normal, no vote], [0.9119],
    [first sheet along the normal, then the vote], [*0.9214*],
  ),
  caption: [Share of the transferred points of segment `20230702185753` that land on the right winding, judged by the
    winding its tracer drew (#slice("247", "247_le_transfert_retrouve_t_il_la_spire_voisine.md"),
    #fact("R4-F412")).],
) <tab-transfer>

== The correction

On the 340 blocks of the segment that have neighbours along both axes, the correction moves 495 points: 163 misses
become right and 41 right points become misses, a net gain of 122 (@tab-correction). The exact two-sided sign test
gives $p = 2.04 times 10^(-18)$ on the points, and $p = 2.25 times 10^(-5)$ on the blocks, 42 up and 11 down
(#slice("290", "290_les_gains_publies_se_distinguent_ils_du_hasard.md"), #fact("R4-F471")). Replaced by noise, the
judges change the counts and not one corrected point: they score, they do not decide.

#figure(
  table(
    columns: (1fr, auto, auto, auto),
    align: (left, right, right, right),
    [setting], [made right], [made wrong], [sign test $p$],
    [segment, neighbours along both axes (340 blocks)], [163], [41], [$2.04 times 10^(-18)$],
    [segment, neighbours east and west only], [net +5], [], [],
    [band `w028-037` (84 blocks)], [15], [25], [0.154],
    [band, neighbours along both axes], [7], [5], [0.774],
  ),
  caption: [The correction where it holds and where it does not (#slice("275",
    "275_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.md"), #slice("281",
    "281_la_procedure_sans_juge_tient_elle_sur_la_bande.md"), #slice("291",
    "291_la_procedure_tient_elle_sur_le_segment_avec_ses_seuls_voisins_est_et_ouest.md"), #slice("295",
    "295_une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.md")).],
) <tab-correction>

The gain has to be read at its real size. Most transferred points were already right, so over the whole segment the
share on the right winding moves from 0.9303 to 0.9334. What matters is that the decision to move a point is taken
without a judge and is right four times as often as it is wrong, which is the property a human corrector provides.

The negative rows are kept on purpose. With neighbours to the east and west only, even the segment's gain falls from
122 to 5, and the anchor carries the loss (#slice("292", "292_lancre_est_ouest_suffit_elle_a_perdre_le_gain_du_segment.md")).
Yet giving the band's blocks neighbours to the north and south does not bring its gain back. The program therefore
writes corrections only for blocks with neighbours along both axes, and its report says that this condition is
necessary and not sufficient.

== The text of the produced winding

The ink reading is first calibrated on the traced winding, where it correlates at 0.96 with the published map. On
the produced winding, where the segment passes within half a sheet, it correlates at *0.83*, against 0.12 for the
text of the starting winding and 0.10 for the counterpart shifted by a letter; each of the six blocks alone lies
between 0.68 and 0.92 (@tab-ink, @fig-ink).

#figure(
  table(
    columns: (auto, auto, 1fr),
    align: (left, right, left),
    [jump along the chain], [$r$], [controls],
    [first], [*0.8331*], [0.1166 (starting text), 0.1037 (shifted counterpart)],
    [second], [*0.8749*], [0.1761, 0.0016, 0.2914 (one turn back)],
    [third], [0.4459], [0.3992 at best: undecided],
  ),
  caption: [The text judge along the chain (#slice("296", "296_le_tour_produit_porte_t_il_le_texte_du_segment.md"),
    #fact("R4-F477"); #slice("297", "297_le_texte_suit_il_la_chaine_au_dela_du_premier_saut.md"),
    #fact("R4-F478")). The second and third jumps are research, not yet in the program.],
) <tab-ink>

#figure(
  image("../examples/grand-prize-render/next_winding_ink.jpg", width: 100%),
  caption: [Top: the ink read on the produced winding, over a 29.5 × 4.9 mm strip of row 176. Bottom: the published
    ink map where the segment passes over that winding. In amber, where the segment passes within half a sheet, the
    only place where the comparison judges anything. This strip was looked at before the slice was written; the six
    blocks behind the 0.83 were not.],
) <fig-ink>

#caveat[The text judge sees little: a median of 2.2 % of a block lies within half a sheet of the segment. At the
third jump it separates nothing, and we report it as undecided rather than as a pass.]

= Reproducibility

- *Published numbers, replayed.* Each port is tested against the research function that produced the number. The
  correction gives back what slices 275 and 281 published, block by block, and the corrected transfer it writes
  corrects the same points as the one the research saved, to within a millionth of a voxel.
- *Inputs, made again from public data.* `vesuve grand-prize --render` renders two piles per block through
  `vc_render_tifxyz` @villa, from the published mesh and the raw scan. Over the whole segment (5 h 09 on three cores,
  288 GB read), its 680 step tables equal the research's seam for seam, 334 171 seams with none different, and the
  corrected transfer it writes has the research's SHA-256.
- *Tests that can fail.* Rules were broken on purpose to check that their tests turn red: an anchor that keeps its
  own block, or a decision that favours the slip, makes four correction tests fail; a broken vote loses the right
  winding.
- *One command.* `docker run` reproduces the Grand Prize and Progress reports from the embedded data, offline:
  `uv run vesuve grand-prize --no-surface` takes about 20 s.
- *Every equation in one place.* `FORMULARY.md` is rendered from the code: each equation, the fact that carries it,
  and the research file that established it.

= Limitations

`vesuve` does not unroll a scroll. It certifies, produces and corrects windings of surfaces others traced, on one
segment of PHercParis4, which is not one of the thirteen scrolls of the 2027 Grand Prize. The correction is validated
on that segment only: on a second band it does not hold, and the condition the program enforces (neighbours along
both axes) is necessary, not sufficient. The text judge needs the segment to pass over the produced winding, which
covers a small part of each block. The program does not read text: First Letters claims no letters on PHerc1447.

= Conclusion

Three steps that a human performs when repairing a sheet switch (finding where a surface stayed on its winding,
producing the next one, and bringing back the points that slipped) run here without a human, on public data, with
decisions that are right four times as often as wrong and a judge that only scores. Where they do not hold, the
program measures that and writes nothing. The next steps are the chain of windings, each jump judged by its text,
and a scroll with no published trace.

#bibliography("references.bib", title: "References", style: "institute-of-electrical-and-electronics-engineers")
