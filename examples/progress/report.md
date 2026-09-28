# progress — report

`vesuve 0.2.0` · core `0.2.0` · Linux x86_64 python 3.13.14 · 3.75 s

## The requirements of the prize

| requirement | state | what is measured |
|---|---|---|
| detect a failure case of an existing method on real data | **met** | column 260, lines 26 to 223: the cumulative closure crosses the half sheet at cuts [163, 173, 203] (peak -40.2188 voxels at cut 173) |
| reproducible and documented | **met** | replayed from the embedded data, with no network and no free seed |
| bound what is claimed | **met** | a region to look at, not a condemnation (`R4-F406`) |

## The stages

### P0 — the audited segment (B1): done

- `scroll`: PHercParis4
- `segment`: 20230702185753
- `volume`: PHercParis4/segments/20230702185753/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
- `nature`: a published segment, traced by others: the audit judges an existing method

### P1 — the certificate, read the other way round (B4): done

- **[P] the profile of a loop** (`R4-F403`): $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  loop = 26, 223, 243, 260, at_cut = 173, half = 36 → **-40.2188**

- **[M] the deciding margin** (`R4-F401`): $`\mu_n = |L_n| - \min_m |L_m| - \mathrm{median}\,|L_n^{\mathrm{null}}|`$

  drifting_line = 260 → **{'wing': 11.2626, 'wide': 2.8875}**

- `loops_judged`: 4
- `loops_that_cross`: 1

### P2 — the failure cases (B1): done

- `suspect_chunks`: 963
- `cases`: ["column 260, lines 26 to 223: the cumulative closure crosses the half sheet at cuts [163, 173, 203] (peak -40.2188 voxels at cut 173)"]
- `limit`: the audit does not tell a misread column from material that moves away (`R4-F406`): it names where to look

### P3 — the suspect region, on the published ink (B3): done

- `image`: ink_and_suspect_region.jpg

