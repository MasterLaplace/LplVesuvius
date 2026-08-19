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
> - **The size confound is real and removed.** Segment footprint correlates with the
>   criterion (+0.384) *and* with ink (+0.463). The **partial** correlation goes from
>   −0.315 to **−0.382** — removing the confound *strengthens* it, the opposite of a size
>   effect.
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
> Three ideas were tested and did not survive. They are documented with the power that
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
> **Paired campaign, 12 prize scrolls** — ten with no published segment at all, plus the
> two that have official ones. Each scroll traced twice, one seed per criterion, everything
> else identical, so each scroll is its own control:
>
> | | area, sign test | self-intersections |
> |---|---|---|
> | planarity vs neighbourhood | **10 – 2, p = 0.0386** | **0 vs 0** |
>
> ⚠⚠ **The self-intersection result does not replicate, and we report that.** On
> `PHerc0358` the seed change took 240 transverse self-intersections to 0; across the other
> eleven scrolls both criteria return zero. What replicates is *how far the tracer gets
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
> - **`vc_grow_seg_from_seed`'s growth is deterministic; its final step is not.** Six runs
>   of the same seed — two at `thread_limit: 0`, two at `1`, one with a direction field —
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

---

## Ce qu'il reste à faire avant d'envoyer

| # | quoi |
|---|---|
| 1 | publier le dépôt (`tracecheck/` au minimum) et mettre l'adresse dans le texte |
| 2 | ~~revérifier chaque chiffre contre son fichier de sortie~~ ✅ **c'est une commande maintenant** — `analysis/src/verifier_chiffres.py` recalcule les 12 chiffres depuis leurs JSON et les cherche littéralement dans les documents. Sort **1** si l'un manque, **2** si un fichier de résultat est absent (sinon il passerait au vert en ne vérifiant rien) |
| 3 | joindre les deux figures de champ, `profondeur_deux_cas.png`, **et les deux figures de `25`** — `25_signatures.png` surtout, qui met le critère visuel du règlement sur un axe mesurable |
| 4 | ⚠ décider si le corps part en anglais — c'est la seule décision de forme ouverte |
