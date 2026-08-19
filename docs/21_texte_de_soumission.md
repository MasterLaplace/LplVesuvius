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
> | `material` | fraction of probed windows containing papyrus | **rho +0.539** vs 80 published Scroll 1 ink maps (p < 1e-6; **+0.561** partialling out area) |
> | `edge_pinned` | peak sits at a stack edge — the sheet is *outside* the volume | rho −0.275 (p = 0.014) |
> | `offset` | median distance from traced layer to material peak | rho +0.388 vs published self-crossings (n = 54, p = 0.004) |
> | `residual` | what remains **after** the best rigid shift | **rho +0.428** vs the same crossings (p = 0.0012) |
> | `rigid_share` | share of error a mesh translation would remove | **21.7 %** median over 80 segments |
> | `coherence` | does a window's error predict its neighbour's | **99/99** segments over two scrolls beat their own shuffle control |
>
> #### 3. The failure case we detected on real scroll data
>
> On a published PHerc1667 segment, **61 % of windows have their material peak pinned to
> a stack edge** — the sheet is outside the 65-layer surface volume the ink model reads.
> Ink detection there returns nothing, and this explains why: **there is no papyrus under
> the trace to detect ink on.** No model change would have helped.
>
> #### 4. A rule that changes a decision
>
> Dropping the worst **20 %** of segments by `material` raises the corpus median ink
> contrast by **+0.381**, against **2000 random draws of the same size**: **p = 0.0005**.
>
> ⚠ **And the robustness check, which we ran on ourselves and which cuts this down.**
> `material` depends on a sampling grid. Two of our tools measure it with different grids
> (72 vs 200 probes), and they agree on the *ranking* only moderately: rho +0.280
> (p = 0.012, permutation control p95 = 0.219). Re-running the whole rule with the second
> grid's criterion: **every gain stays positive and every p stays under 0.09, but the
> significance drops an order of magnitude and the 15–25 % plateau disappears.**
>
> So what we claim is the **direction**, which replicates on two independent samplers:
> dropping the material-poorest segments improves what the corpus yields. We do **not**
> claim that 20 % is the right threshold. The fix is to measure `material` better — a
> denser probe, ~4 s more per segment — not to pick the grid with the better p-value.
>
> Three things still make this more than a correlation:
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
> median cannot: **is this trace fixable by moving the mesh?** On both scrolls, no. The
> plainest form of the number depends on no normalisation at all: on Scroll 1 the median
> shift is **14.4 µm** and the median residual is **56.4 µm** — what a translation could
> remove is **four times smaller** than what it would leave. (Expressed as a share:
> 21.7 % on Scroll 1, 35.3 % on Scroll 4.) The
> error is a smooth local deformation inside the sheet, not a mispose. **On these two
> scrolls the useful repair is a warp, not a shift** — worth knowing before anyone builds
> the shift.
>
> ⚠ We say *on these two scrolls* deliberately. One Scroll 5 segment returns a rigid share
> of **0.67** — there a translation would remove two thirds of the error. If that holds
> across its 53 segments, then *which repair works* is a property of the scroll rather than
> a constant of the problem. That measurement is running; until it lands, the claim is
> scoped.
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

---

## Ce qu'il reste à faire avant d'envoyer

| # | quoi |
|---|---|
| 1 | publier le dépôt (`tracecheck/` au minimum) et mettre l'adresse dans le texte |
| 2 | revérifier **chaque chiffre** contre son fichier de sortie, le jour de l'envoi |
| 3 | joindre les deux figures de champ **et** `profondeur_deux_cas.png` |
| 4 | ⚠ décider si le corps part en anglais — c'est la seule décision de forme ouverte |
