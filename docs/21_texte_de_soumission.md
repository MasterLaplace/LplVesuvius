# Le texte de la soumission — brouillon

2026-08-19. `15` §5 disait qu'il ne restait que ça. Le voici.

⚠ **Deux décisions de forme, et la seconde est à l'auteur de trancher.**

1. Le corps de la soumission est **en anglais**. L'auteur a dit que le français n'est pas
   un problème — et ça vaut pour nos documents, qui expliquent. Ce texte-ci **part** vers
   une équipe qui lit l'anglais, comme `tracecheck` est destiné à être *utilisé* par
   d'autres. Le même partage que pour l'outil.
2. Elle vise le Progress Prize d'**août 2026**, pas le Grand Prize. Nos instruments
   jugent et trient ; ils ne déroulent pas de rouleau.

⚠ **Ce brouillon ne s'envoie pas tel quel** : chaque chiffre doit être revérifié contre
son fichier de sortie le jour de l'envoi, et l'adresse du dépôt public n'existe pas
encore.

---

## Le texte

> ### Trace quality, measured before you pay for it
>
> **What this is.** Three measurements on a segment's *published surface volume*, read
> remotely, that answer questions currently answered only after a 32 GB download or a
> 40-minute inference run. Plus one rule built on top of them that improves what a corpus
> yields, tested against a permutation control.
>
> Everything is open source: `tracecheck/` is a single file, needs `numpy` and nothing
> else, and ships with 16 offline self-tests.
>
> ---
>
> #### 1. It is cheap because of how the data is shaped
>
> A published surface volume is OME-Zarr with chunks `[depth, 128, 128]`. **One chunk is
> the entire depth column of a 128×128 window** — exactly the unit a depth profile needs.
> Chunks are independent HTTPS objects, so reads parallelise with no coordination:
> measured speed-up at 16 threads is **×8.35**, with byte-identical output.
>
> A whole segment is judged from ~300 range reads, a few megabytes, ~15 seconds. On this
> basis, judging **all ~800 scrolls** of the Villa would read **0.004 % of their volume**
> in **0.9 hours**.
>
> #### 2. What is measured, and what each number is worth
>
> | field | meaning | evidence |
> |---|---|---|
> | `material` | fraction of probed windows containing papyrus | **rho +0.539** vs 80 published Scroll 1 ink maps (p < 1e-6; **+0.561** partialling out area). ⚠ Driven by a near-blank class: **+0.190, ns** once those segments are removed. **Does not replicate** on three other scrolls — see §4 |
> | `edge_pinned` | peak sits at a stack edge — the sheet is *outside* the volume | rho −0.275 (p = 0.014) |
> | `offset` | median distance from traced layer to material peak | rho +0.388 vs published self-crossings (n = 54, p = 0.004) |
> | `residual` | what remains **after** the best rigid shift | **rho +0.428** vs the same crossings (p = 0.0012) |
> | `rigid_share` | share of error a mesh translation would remove | **21.7 %** median over 80 segments |
> | `coherence` | does a window's error predict its neighbour's | **150/152** segments over three scrolls beat their own shuffle control (80/80, 19/19, 51/53) |
>
> #### 3. The failure case we detected on real scroll data
>
> On a published PHerc1667 segment, **61 % of windows have their material peak pinned to
> a stack edge** — the sheet is outside the 65-layer surface volume the ink model reads.
> Ink detection there returns nothing, and this explains why: **there is no papyrus under
> the trace to detect ink on.** No model change would have helped.
>
> #### 4. A rule that flags a failure class before you pay for it
>
> On Scroll 1, `material` identifies a **class** of segments whose published ink map is
> nearly flat — **14 of 80**. Dropping the material-poorest **20 %** raises the corpus
> median ink contrast by **+0.381** against **2000 random draws of the same size**
> (**p = 0.0005**) because it removes members of that class.
>
> ⚠⚠ **It is a class, not a gradient, and we measured which.** Remove the 16 segments
> below a contrast of 3.0 and the correlation falls from **+0.539 to +0.190 (p = 0.13,
> not significant)**. Among segments that actually carry ink, `material` says little. We
> state this because the weaker claim is the one the evidence supports — and because
> "flags a failure class" is closer to what your bottleneck table asks for than "improves
> a median" ever was.
>
> ⚠⚠ **And it does not replicate.** We tested it on 110 further segments across three more
> scrolls, all with published surface volumes and published ink maps, using the identical
> measurement:
>
> | corpus | n | voxel | target's relative spread | rho | detectable at 80 % |
> |---|---:|---:|---:|---:|---:|
> | **Scroll 1** | 80 | 2.4 µm | 1.008 | **+0.539** | 0.31 |
> | **PHerc0139** | 38 | **2.399 µm** | **1.628** | **−0.229** | 0.44 |
> | PHerc1667 | 19 | 2.399 µm | 0.720 | +0.425 | 0.60 |
> | PHerc0172 | 53 | 7.91 µm | 0.220 | −0.217 | 0.37 |
>
> Our first explanation was a floor effect — PHerc0172's ink maps barely differ from one
> another (relative spread 4.6× smaller than Scroll 1's), so there is nothing there to
> predict. **That explains one corpus out of three.** PHerc0139 sits at the *same*
> resolution as Scroll 1, has a *larger* relative spread, and still returns the opposite
> sign.
>
> None of the three negatives is individually significant. But the pattern — one strong
> positive, three non-positive — is the shape we have twice watched dissolve in this
> project. **We therefore report the rule as a property of Scroll 1's published corpus,
> not of the problem.** It remains strong there: it survives Bonferroni over 20 pairings,
> a 5.4× increase in probe density, and 2000 permutations. What falls is its reach.
>
> ⭐ We publish all four corpora rather than the one that works, because that is what makes
> the measurement usable: anyone reusing it learns at once that it needs re-validating on
> their corpus, instead of discovering it afterwards.
>
> Three more things make this more than a correlation:
>
> - **The target is another pipeline's output.** The 80 ink maps are the ones published
>   here, taken as-is. Nothing of ours enters them, so the relationship cannot be a shared
>   artefact.
> - **The size confound is real and removed.** Segment footprint correlates with
>   ⚠ **`ecart_a_la_trace`** (+0.384) *and* with ink (+0.463). Its **partial**
>   correlation goes from −0.315 to **−0.382** — removing the confound *strengthens* it,
>   the opposite of a size effect. ⚠ **This criterion clears the nominal threshold only:
>   `19` marks it « ❌ *nominal seulement* » — it does not survive Bonferroni.**

⚠⚠ **Corrigé le 2026-08-19.** Cette puce vivait sous une section qui parle de
`material` (+0,539) et **importait les chiffres d'un autre critère** — +0,384, +0,463,
−0,315 → −0,382 appartiennent tous à `ecart_a_la_trace` (`19` §64, §78-79, §88). Deux
fautes en une : le mauvais critère, et une réserve omise que la source porte.
> - **The threshold sits on a plateau, not a peak.** 15–25 % all hold at p ≤ 0.001; 5 %
>   does nothing (p = 0.054) and 30 % degrades. An overfitted knob produces a peak.
>
> **What we do not claim.** A blank ink map can mean a failed trace *or* blank papyrus.
> Nothing here separates them, so this is corpus triage, never a verdict on one segment.
>
> #### 5. Sheet jumps: measured, and shown
>
> The brief asks to show that a surface *doesn't jump across sheets*. We measure it: the
> **residual after the best rigid shift**, compared to that scroll's own inter-sheet
> pitch. On 80 published Scroll 1 segments, **1** exceeds one sheet gap, and it is named.
>
> The figures put each field next to its control — same values, same windows, random
> assignment. Structure on the left, salt-and-pepper on the right.
>
> ⚠ We publish the **median** case alongside the strongest one. On the median case the
> difference is hard to see, which is exactly what a coherence of 0.31 means. Showing
> only the best figure would imply an effect we did not measure.
>
> #### 6. And what it says about repair
>
> Because the residual is measured *after* the best translation, it answers a question a
> median cannot: **is this trace fixable by moving the mesh?** On all three scrolls
> measured, no. The plainest form of the number depends on no normalisation at all: on
> Scroll 1 the median shift is **14.4 µm** and the median residual is **56.4 µm** — what a
> translation could remove is **four times smaller** than what it would leave. As a share:
> **21.7 %** (Scroll 1, 80 segments), **35.3 %** (Scroll 4, 19), **28.6 %** (Scroll 5, 53).
> The
> error is a smooth local deformation inside the sheet, not a mispose. **On these two
> scrolls the useful repair is a warp, not a shift** — worth knowing before anyone builds
> the shift.
>
> ⚠ We nearly scoped this claim to two scrolls: a single Scroll 5 segment returned a rigid
> share of **0.67**, which would have made *which repair works* a property of the scroll
> rather than a constant. Measuring all 53 put its median at **28.6 %** — that segment was
> an outlier. We report the near-miss because one sample is not a result in either
> direction.
>
> #### 7. Negative results we are also reporting
>
> ⚠ **Four** ideas were tested and did not survive *(corrigé le 2026-08-19 : le texte
> annonçait « three » et la liste en compte quatre)*. They are documented with the power that
> would have detected them, because a corpus of dead ends saves other people's months:
>
> - **Fibre orientation as a sheet-jump discriminant** — sign *inverted* from n = 12
>   (+0.330) to n = 54 (**−0.192**).
> - **Winding-phase steps between adjacent mesh cells** — +0.517 at n = 8, +0.306 at
>   n = 30, **+0.150 at n = 38**. A real effect does not melt when you sample it better.
>   And it is not a resolution artefact: the `cos` volume publishes no level finer than 3,
>   and the median step there is 12.2 out of 255 with **zero** of 38 traces at zero.
> - **Depth-field measures as legibility predictors** — rho −0.028 at n = 80, where 0.31
>   would have been detectable. They measure a defect of the **trace**, not of the
>   **result**.
> - **A µm threshold separating "legible" from "not"** — we proposed one on three
>   segments (>50 µm offset ⇒ no readable ink) and tested it on eighty. The *direction*
>   holds (4.93 vs 5.91, p = 0.017) but 60 µm scores worse than both 50 and 70: a curve
>   that rises, dips and rises again has no cut point. And the strong form fails outright
>   — the corpus median offset is 67 µm, so the threshold would condemn 64 of 80 segments
>   that visibly carry ink, and only 8 % of those above it land in the bottom ink decile
>   against 10 % expected by chance. **The quantity is ordinal; an absolute threshold on
>   it does not transport.**
>
> #### 8. Choosing a seed, measured — and one number that stands in for your own visual test
>
> `vc_grow_seg_from_seed` starts from one coordinate. In VC3D you click it; there is no
> published criterion for choosing it, and we could not find one. `tracecheck --seed`
> proposes one, reading the published surface *prediction* remotely.
>
> **The obvious criterion saturates, silently.** "Where is there the most predicted
> surface" returned **eight candidates all scoring 255** on `PHerc0358` — a thresholded
> prediction is binary, so any block fully inside predicted matter hits the format ceiling.
> Eight tied candidates are a coin toss, not a ranking. The tool now says so out loud.
>
> **What we rank instead** is the 3D structure tensor, `(lam1 - lam2) / lam1`. One sheet
> crossing a block puts every gradient along its normal (planarity ~1); **two parallel
> sheets score just as high**, which is the point — a regular stack is exactly where a seed
> belongs; a **junction** populates two directions and collapses to ~0, and a junction is
> where the tracer can slip between wraps with nothing in the prediction to stop it.
>
> ⚠ An argmax over a chunk's ~13 800 blocks **saturates too**, so what is ranked is the
> planarity averaged over the 3×3×3 block neighbourhood, ties broken on how many valid
> neighbours exist. The orientation bias a thresholded prediction introduces is measured,
> not assumed: swept 0–90°, raw planarity spans 0.828–1.000, blurred 0.947–1.000.
>
> **Paired campaign, 13 prize scrolls** — ten with no published segment at all, plus the
> three that have official ones. Each scroll traced twice, one seed per criterion,
> everything else identical, so each scroll is its own control:
>
> | | area, sign test | self-intersections |
> |---|---|---|
> | planarity vs neighbourhood | **11 – 2, p = 0.0225** | **0 vs 0** |
>
> ⚠⚠ **The self-intersection result does not replicate, and we report that.** On
> `PHerc0358` the seed change took 240 transverse self-intersections to 0; across the other
> twelve scrolls both criteria return zero. What replicates is *how far the tracer gets
> before stalling* — and the extremes say it better than a median: on `PHerc0125` and
> `PHerc0826` the neighbourhood seed stalls at **0.85 cm²**, barely above `min_area_cm`,
> where planarity reaches 19.82 and 13.14.
>
> ⚠ **And the fix that mattered on `PHerc0358` was not the criterion.** Replayed without an
> occupancy ceiling, the neighbourhood criterion returns exactly the bad seed — whose block
> has **occupancy 1.000**. A block entirely full of predicted matter has a **null structure
> tensor**: no sheet, no normal, no orientation. The prediction had merged several wraps
> into a solid blob, and the tracer started where there was no geometry to follow.
>
> #### 9. The number we would most like others to use
>
> Your First Letters brief asks whether one can *"visually follow horizontal papyrus fibers
> across the page"*. That is an eye's test. **The amplitude of the depth profile of a
> render is its measurable form**, and the reasoning is geometric: depth is travelled along
> the surface **normal**, so a surface *parallel* to the sheets has a normal that **crosses**
> the stack and a profile that swings; a surface *cutting* the stack has a normal that stays
> in the same material, and a flat profile.
>
> Measured at a matched 1.2 mm window, and anchored at both ends by images:
>
> | trace | amplitude | what the face shows |
> |---|---:|---|
> | Scroll 1 `20230909121925` (AUC 0.925) | **50.1 %** | straight parallel fibres — a sheet's face |
> | official `PHerc1447` segment | 28.8 % | fibres, on a narrow band |
> | Scroll 4 `20231111135340` (known failure) | 19.3 % | fragments in the void |
> | our best `PHerc0358` trace | **8.7 %** | concentric laminations — the roll seen **edge-on** |
>
> ⚠⚠ **This told us our own trace is worse than we thought, in a way zero self-intersections
> cannot catch**: it is not drifting between sheets, it is laid *across* the stack. A surface
> can slice the roll like a knife without ever crossing itself.
>
> ⚠ It is **necessary, not sufficient**: Scroll 4 fails a third way — the trace is in the
> void — at a *higher* amplitude than ours. One number does not rank three failure modes.
>
> ⚠ And the criterion we first reached for — *"does the material peak sit in the central
> third"* — **does not transport to prize scrolls**: the official `PHerc1447` segment fails
> it (2 %) worse than either of ours (16 % and 20 %). We retired it rather than keep a
> verdict a reference fails.
>
> #### 10. Two reproducibility facts about the official tracer
>
> - **`vc_grow_seg_from_seed`'s growth is deterministic; its final step is not.**
>   ⚠ **Five** runs of the same seed — two at `thread_limit: 0`, two at `1`, one with a
>   direction field — *(corrigé : le texte disait « six » et l'énumération en décrit cinq)*
>   produce **byte-identical growth logs across all 118 generations**, all ending at
>   1985.73 mm². The **saved** surfaces then span 19.8219–19.8387 cm² (and 20.7471 with the
>   field). So what varies is a post-growth optimisation, not the path taken. ⚠ We first
>   wrote "the tracer is not reproducible", which is true but too coarse; comparing the
>   growth logs rather than the final areas is what sharpened it. All four field-free runs
>   returned **0 self-intersections**: the surface is not reproducible, the verdict is.
> - **Area saturates against the generation budget.** Two traces on *different scrolls* both
>   stopped at generation 119 of 120 and returned the same area to eight thousandths of a
>   percent — a surface grows as a front, so its area is set by the step count when nothing
>   stops it. Pushed to 600 generations the same seed reaches 127.9 cm² (and 174
>   self-intersections, at a rate 21× lower per pair tested than the bad seed). Area is a
>   proxy for *how far it got*, never a quality score.

⚠⚠ **Le §10 ci-dessus est PÉRIMÉ, et sa dernière phrase est fausse.** Il conclut *« the
surface is not reproducible, the verdict is »*, sur cinq exécutions d'une seule graine.
[`30`](30_le_traceur_est_un_tirage.md) a d'abord montré qu'une **autre** graine fait varier
la croissance elle-même (64 à 86 générations, 5,69 à 10,34 cm²), puis
[`35`](35_le_tirage_sur_douze_rouleaux.md) a mesuré **13 rouleaux, 78 tirages** — et le
verdict, lui aussi, bascule. Le §10 est donc à **remplacer** par le texte ci-dessous, pas à
nuancer.

### 10 bis. ⭐⭐ Le remplacement, écrit sur 78 tirages *(2026-08-20, étendu le 08-22)*

> #### 10. The official tracer is a draw, not a function
>
> `vc_grow_seg_from_seed` returns a different result on every run. **78 tirages**,
> thirteen prize scrolls, six per scroll, strictly identical parameters and seeds:
>
> | | |
> |---|---:|
> | scrolls whose six runs return the same area | **0 of 13** |
> | ⭐ scrolls where the **verdict flips** between runs | **5 sur 13** |
> | bad runs | **5 / 78 = 6,4 %** (exact 95 % CI: **2,1 % – 14,3 %**) |
>
> The five flips, with the worst count each scroll produced: 1615, 428, 607, 140, 1371
> self-intersections — against zero on the other five runs of the same scroll.
>
> ⚠ **This corrects our own earlier claim.** An earlier draft of this section said *« the
> surface is not reproducible, the verdict is »*, on five runs of one seed. The verdict is
> not reproducible either; we had simply not repeated on enough scrolls to see it.
>
> ⭐⭐ **And the extent does not tell you which run went wrong.** The three scrolls whose six
> areas agree to within a third of a percent are the ones carrying the worst counts. Ranking
> a bad run by how far it grew gives a rank excentricity of 0,60 where 0,50 is what "area
> says nothing" predicts — on four events, that is nothing. The usable conclusion is
> negative and sufficient: **you cannot discard a bad run by looking at its size. You have to
> judge it**, which is what a 0.05 s judge is for.
>
> ⚠ We do not know **why**. `thread_limit` was ruled out; nothing replaced it. And a clean
> run is not thereby a *good* run — zero self-intersections is necessary, never sufficient.
>
> **Why this matters to anyone comparing methods**: published ablation tables give one line
> per configuration, with no repetition and no error bar, and the full-unwrapping paper
> publishes no trace-error rate at all. On this evidence, a single run is not a measurement.


### 11. ⭐⭐⭐ Juger une trace sans vérité terrain, sans seuil et sans échelle *(2026-08-21)*

> #### 11. Trace quality without ground truth, without a threshold, and without a scale
>
> **The problem.** Every published way of judging a traced surface needs something you do
> not have at scale: a reference segment, a human eye, or a threshold calibrated on one
> scroll. Self-intersection counts are not it — the same mesh, decimated without changing
> its geometry, goes from 240 crossings to 49 (section 9), so a count is a property of the
> sampling as much as of the surface.
>
> **The test.** Render the *same* surface in progressively deeper windows and measure, in
> each, the distance from the surface to the nearest material. A surface that lies **on**
> its sheet has that material right there: widening the window changes nothing. A surface
> lying **across** the stack has no peak to find, so the "peak" it reports is the strongest
> thing the window happened to contain — and it moves **with** the window.
>
> One dimensionless number says which: `α = log(growth) / log(widening)`.
>
> | | layers | distance | **α** |
> |---|---:|---:|---:|
> | an official segment (`PHerc1447`) | 31 → 81 | 17.28 µm → 17.30 µm | **+0.00** |
> | one of our traces, same scroll, same chain | 21 → 161 | 86.40 µm → 682.56 µm | **+1.01** |
>
> **Three properties, and we know of no other trace test that has all three:**
>
> - **no threshold** — the surface is compared to *itself* in another window;
> - **no ground truth** — no reference segment, no ink map, no annotation;
> - **no scale** — α is a ratio, so it crosses scrolls, voxel sizes and resolutions without
>   being re-calibrated.
>
> ⚠ **What it does not tell you: by how much to correct.** A trace that does not converge has
> no distance to its sheet, because there is no sheet within reach. The test separates *lying
> beside* from *lying across*, and that is all — which is already what nothing else did.
>
> ⭐⭐ **The consequence for anyone publishing a distance.** Every distance-to-sheet figure we
> had published for our own non-converging traces — 94 µm, 146–187 µm, 311 µm — is **without
> object**. Not an underestimate: a measurement of a quantity that does not exist at that
> location. We found this by measuring our own numbers, and we expect it applies to any
> pipeline that reports a surface-to-sheet distance without first showing that the figure is
> stable under the rendering depth.
>
> **Cost**: two renders of the same surface. No model, no annotation, no download of a full
> volume.

### 12. What made our surfaces converge: project them, do not grow them

> The test above condemns our own traces, so the obvious question is what to do instead. We
> have an answer, and it is measured rather than argued.
>
> **Seventeen attempts at growing a surface from a seed all gave α ≈ 1** — every one lying
> across the stack, with no exception. Four rewound-and-corrected runs got to +0.89 at best:
> feeding a tracer a list of points it should have passed through does not reorient a surface
> that has already grown.
>
> What works is not growing at all. `vc_grow_seg_from_seed`'s `gen_neighbor` mode takes an
> existing surface and **projects** it along its own vertex normals to the next sheet. It has
> no freedom, so it has no drift. Chaining it — each surface the source of the next — gives:
>
> | | α |
> |---|---:|
> | the official segment we start from | **+0.00** |
> | **six consecutive surfaces we generate**, each grown from the previous | **all ≤ +0.246** |
>
> For scale: a surface lying across the stack gives α ≈ 1. **These are the first surfaces we
> produce that the convergence test does not condemn.**
>
> **And the mode has one tunable that decides everything — with a measured optimum.** The
> ray-marching step `neighbor_step`, swept over a factor of eight, at *equal chain depth*:
>
> | step | mean α | α of the worst wrap |
> |---:|---:|---:|
> | 1.0 | +0.357 | +1.475 |
> | 0.5 | +0.129 | +0.583 |
> | **0.25** | **+0.102** | **+0.246** |
> | 0.125 | +0.327 | +0.758 |
>
> A U-curve, not a monotone improvement: too coarse and too fine are both three times worse.
> Halving again is not the way.
>
> ⭐ **What the step does NOT change is as informative.** Erosion holds at 4.0 % of grid area
> per turn across all four settings, and the measured distance between consecutive sheets
> stays at 102–116 µm throughout — so the ray lands on the *correct* sheet even where α is
> bad. The step decides **where the surface settles, not how much of it survives.** Why too
> fine a step degrades is still unknown; we say so rather than guess.
>
> **Three limits we state because they bound what this is worth.**
>
> - ⚠ **Erosion bounds the chain before quality does.** On the surface actually carrying
>   material — not the grid — it is 15.6 % per turn, so half the area is gone in four turns.
>   The published 4.0 % figure counts invalid grid vertices as surface; the fraction of valid
>   vertices falls from 58 % to 23 % along a nine-wrap chain.
> - ⚠⚠ **A radial chain is a column, not a strip.** Each window covers ~10 % of one turn, and
>   consecutive wraps sit 113 µm apart in the *same* angular window — separated, along the
>   papyrus, by a full circumference we do not have. Gluing them end to end would produce a
>   band that does not exist. Reaching a length of unrolled papyrus needs a *tangential*
>   chain — section 13 is what happened when we tried.
> - ⚠⚠ **We do not know why a wrap fails.** The best predictor of a wrap's α, across four
>   campaigns and forty wraps, is its **ordinal position in the chain** (ρ = +0.53, p = 0.001)
>   — better than erosion, arc length, area, or any single-render statistic we tried. Depth is
>   a clock, and we cannot yet separate it from a cause.
>
> ⚠ **One methodological note, because it changed our own numbers.** α on two windows does not
> discriminate to better than ±0.2, so a *count* of verdicts is a count of threshold
> crossings: nearly a quarter of our distinct wrap verdicts sit inside that width, one of them two
> thousandths from its threshold. We had published a conclusion resting on that wrap and
> retracted it the same day. Every figure in this section is an α or an area — a continuous
> quantity measured directly — and never a count.
>
> **Cost**: one `gen_neighbor` call and two renders per wrap. No model, no annotation.

### 13. Growing sideways: one extension triples a published segment — and the cycle has a fixed point

> Section 12 ends on a limit: a radial chain stacks sheets, it does not lengthen one. So we
> asked the cheapest question we had never asked — **what happens if we let a published
> segment simply keep growing along itself?**
>
> | | useful area | arc | valid vertices | α |
> |---|---:|---:|---:|---:|
> | published segment, as downloaded | 4.28 cm² | 21.9 mm | 59 % | **+0.000** |
> | after one extension | **12.97 cm²** | **37.2 mm** | **96 %** | **+0.000** |
>
> ⭐ **Three times the useful area, 70 % more arc, and the convergence test still does not
> condemn it.** This is the largest converging surface this work has produced, and it costs one
> call.
>
> ⚠⚠ **But the first time we measured it, the result was a coin flip, and saying so is the
> point.** The growth mode draws from an unseeded generator and runs multi-threaded: three runs
> of *identical* parameters gave 0, 596 and 0 self-intersections, and α of +0.000, +0.422,
> +0.000. Pinning the seed and forcing a single thread makes it reproducible — two runs then
> give the same mesh, bit for bit. Every number above is from the pinned configuration. A
> result that only replicates two times in three is not a result, and it took a repeat to see
> it.
>
> ⚠⚠ **More growth does not give more surface.** The budget is the one knob, and past a point
> it fails hard rather than gradually:
>
> | growth budget | area | self-intersections | α |
> |---:|---:|---:|---:|
> | **100** | 12.97 cm² | ⭐ **0** | ⭐ **+0.000** |
> | 200 | 28.62 cm² | 25 036 | **+1.313** — across the stack |
> | 200, in two sessions of 100 | 50.30 cm² | 4 996 | +1.040 |
>
> Splitting the budget helps a great deal and still does not save it. What decides the outcome
> is not the size of the step but **how clean the surface it starts from is** — measured on its
> periphery, which is where a growth mode's newest and worst vertices live.
>
> ⭐⭐ **That gives a repair, and it works.** Every vertex carries the generation at which it was
> created, so trimming the late periphery is a filter, not a guess. Trimming the extension to
> its first ten generations returns **6.02 cm² with a periphery as clean as the source's** —
> **41 % more validated material than the published segment**, at α = +0.000.
>
> ⚠⚠ **And then the cycle closes on itself.** Extending *that* clean surface again converges
> too (α = +0.000) — but trimming the result back to a clean periphery returns 6.02 cm² again,
> exactly. **The trim-and-extend cycle does not diverge; it converges to a fixed point near
> 6 cm².** Each turn regains what it just gave up. We report this because a cycle that appears
> to work for one iteration is exactly what a reader would extrapolate from, and it does not.
>
> ⚠⚠ **The remaining route — stitching published segments together — has no candidate.** The
> tool for it exists (`vc_merge_tifxyz`: patch-index overlap, RANSAC, joint affine bundle
> adjustment, TPS RBF, N-way EDT blending) and it needs surfaces that *overlap*. This scroll
> has **15 published segments**, and 51 of their 105 pairs do overlap by bounding box — but a
> box overlap cannot tell "two patches of one sheet" from "two adjacent sheets", which in a
> scroll occupy nearly the same volume. Measuring the median point-to-point gap instead:
> **0 pairs under 40 µm**, 2 between 40 and 250 µm, the rest further. **The closest pair in the
> whole scroll is still 79 µm apart** — twice the same-sheet threshold, and about the sheet
> spacing we measured. The published segmentation of this scroll is a set of samples, **one
> patch per sheet**, not a tiling of one sheet. Cost of establishing this: 4.5 MB and a few
> seconds, against building a volpkg for a merge that would have found no edges.
>
> **What we claim, exactly**: any published segment that converges can be **tripled once**, and
> **grown by 41 % of clean, validated surface permanently**, both at α = +0.000 and
> reproducibly. That is a real gain on already-validated material. It is not a continuous
> strip, and both named routes to one are now measured and closed — each for its own reason.

---

## Ce qu'il reste à faire avant d'envoyer

| # | quoi |
|---|---|
| 1 | publier le dépôt (`tracecheck/` au minimum) et mettre l'adresse dans le texte |
| 2 | ~~revérifier chaque chiffre contre son fichier de sortie~~ ✅ **c'est une commande maintenant** — `analysis/src/verifier_chiffres.py` recalcule **125 chiffres** depuis leurs JSON et les cherche littéralement dans les documents. Sort **1** si l'un manque, **2** si un fichier de résultat est absent (sinon il passerait au vert en ne vérifiant rien) |
| 2 bis | ~~relire la transcription anglaise du corps~~ ✅ **`--soumission docs/21…md`** — les chiffres que le corps cite doivent être trouvés **dans ce document-là**, pas seulement quelque part dans le dépôt. ⚠ Sans ça, la recherche globale était satisfaite par la prose française source et une faute de frappe à la recopie passait : la sonde `12,97 → 12,79` le montre |
| 3 | ~~joindre les figures~~ ✅ **c'est une commande maintenant** — `tools/dossier_soumission.sh` rassemble le texte, ses figures et le journal des chiffres. ⭐⭐ La liste des figures est **dérivée du document** : toute image nommée entre backticks ci-dessous est copiée, donc en ajouter une au texte l'ajoute au dossier. ⚠ Et le script **refuse** de produire un dossier incomplet — un dossier auquel il manque une pièce ressemble à un dossier complet. Sonde faite : retirer `38_convergence.png` fait sortir en 1 |
| 3 ter | ⭐⭐ joindre `43_optimum_du_pas.png` (la courbe en U du pas du rayon) et `44_geometrie_chaine.png` (où la chaîne se trouve dans le rouleau) — la section 12 ne se lit pas sans la première, et la seconde est ce qui rend honnête la limite « une colonne, pas une bande » |
| 3 quater | ⭐⭐ joindre `44_ecarts_segments.png` (la distribution des écarts entre segments publiés) et `44_extension.jpg` — la **section 13** en dépend : le tableau y donne « 0 candidat », et un compte de zéro se lit comme un résultat faible tant qu'on n'a pas vu le **trou d'un facteur deux** sous le seuil |
| 3 bis | ⭐ joindre `38_convergence.png` et `38_en_travers.png` — la section 11 ne se lit pas sans elles : l'une montre les deux pentes, l'autre montre à quoi ressemble une surface posée en travers (des laminations concentriques, pas du papyrus) |
| 3 | joindre les deux figures de champ, `profondeur_deux_cas.png`, **et les deux figures de `25`** — `25_signatures.png` surtout, qui met le critère visuel du règlement sur un axe mesurable |
| 4 | ⚠ décider si le corps part en anglais — c'est la seule décision de forme ouverte |
