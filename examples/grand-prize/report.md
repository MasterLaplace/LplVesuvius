# grand-prize — report

`vesuve 0.2.0` · core `0.2.0` · Linux x86_64 python 3.13.14 · 22.21 s

## The requirements of the prize

| requirement | state | what is measured |
|---|---|---|
| one of the thirteen eligible scrolls | **not met** | PHercParis4: the method's reference, outside the list |
| 100 % of the recto unrolled | **not met** | one published segment: 6333 chunks certified out of 97771 (6.48% of ITS footprint); a segment is not a scroll |
| automated pipeline, at most 8 h of human input | **met** | 0 h: the procedure takes every decision without a hand (`R4-F410`); its only input is the presence |
| the transfer to the next winding corrected without a hand | **met** | 163 misses made right for 41 rights made misses on 340 blocks, a net gain of 122; sign test p = 2.04e-18 on the points and 2.25e-05 on the blocks (42 up, 11 down). The judge only scores (`R4-F456`, `R4-F471`) |
| the correction claimed only where it was validated | **met** | 339 of 340 blocks have neighbours along both axes, and only their corrections are written. On the band `20260623142658-w028-037` (0 of 84 blocks within that geometry), the same procedure gives 15 for 25 (p = 0.154), and nothing is claimed there. The geometry is necessary, not sufficient: on a slice of that band twice as tall, 28 blocks with neighbours on all four sides give 7 for 5 (p = 0.774, `295`, `R4-F476`). The correction is validated on this segment, against its judges, and nowhere else yet |
| 70 % of the characters legible per column | **not measured** | no reading; at the prize regime the published ink is flat (`R1-F20`) |
| one mesh per column, `column_NN.tifxyz` | **not met** | the certified surface is returned whole, with `approval.tif`; no cutting into columns |
| Docker image | **met** | `Dockerfile`, which runs this pipeline from the embedded data |
| seeds fixed and reported | **met** | block null: seed 20261105, 999 draws; judge: seed 20260924 |
| integrated in VC3D | **not measured** | the surface and `approval.tif` follow the tifxyz contract villa reads |

## The stages

### E0 — the object (B1): partial

*PHercParis4 is not one of the thirteen prize scrolls: the method is built where the reference exists, and it will have to be carried to a scroll without ground truth (`151` E0)*

- `scroll`: PHercParis4
- `segment`: 20230702185753
- `eligible`: false
- `eligible_scrolls`: ["PHerc0125", "PHerc0191", "PHerc0211", "PHerc0257", "PHerc0268", "PHerc0358", "PHerc0800", "PHerc0813", "PHerc0826", "PHerc1203", "PHerc1218", "PHerc1447", "PHerc1545"]

### E1 — the volume (B1): done

- `volume`: PHercParis4/segments/20230702185753/surface-volumes/2.4um-0.22m-78keV-volume-20260411134726.zarr
- `grid`: [396, 285]
- `chunks_present`: 97771
- `provenance`: the list of the bucket's keys, read back by `ou_sarrete_le_segment.py` (98 pages)

### E2 — the scale (B1): done

- **[E2] the half sheet** (`R4-F14`): $`\delta = \mathrm{round}\!\left(\frac{s}{2\,v}\right)`$

  s_um = 173, v_um = 2.4 → **36**


### B — the budget of a sheet trace (B1): done

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = cross material_floor, delta = 36, sigma = 2.233 → **259.913**

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = cross mean_of_rows, delta = 36, sigma = 1.9245 → **349.92**

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = cross single_row, delta = 36, sigma = 2.4587 → **214.385**

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = agree 197-199, delta = 36, sigma = 3.4004 → **112.084**

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = agree 198-197, delta = 36, sigma = 2.7138 → **175.974**

- **[N5] the holdable length** (`R4-F340`): $`n_{\max} = \left(\frac{\delta}{\sigma}\right)^2`$

  budget = agree 198-199, delta = 36, sigma = 2.9794 → **145.998**

- **[N7] the triangle of own noises** (`R4-F343`): $`\sigma_{b,i}^2 = \frac{\sigma_\Delta^2(i,j) + \sigma_\Delta^2(i,k) - \sigma_\Delta^2(j,k)}{2}`$

  row = 198, var_198_197 = 7.36471, var_198_199 = 8.87682, var_197_199 = 11.5627 → **2.33941**

- `binding_holdable_length`: 112.08
- `seams_of_a_row`: 284
- `conclusion`: a row of 284 seams exceeds the 112.08 the agreement allows: two rows each walked on its own end on two sheets (`R4-F341`). Hence the certificate: close loops rather than walk.

### E4 — the lattice: the published bands (B4): done

- `published_bands`: 112
- `given_bands`: 0

### E4L — the lattice: reading what the procedure asks for (B4): skipped

*replay: the published bands and those given by --readings; --read reads what the procedure asks for*

- `published_bands`: 112
- `fresh_bands`: 0
- `chunks_read_here`: 0
- `reading_rounds`: 0

### E6 — the certificate (B4): partial

*111 bands (24263 chunks) are still to read to judge what the procedure finds; the coverage is that of what is judged. `vesuve grand-prize --read` reads them, about 21 min at 16 threads*

- **[S] the reach that sees** (`R4-F409`): $`p = \max_{\text{cuts off the crossing}} (y_{j+1} - y_j) - 1 = 29`$

  gap_avoided = 30 → **29**

- **[L] the closure of a loop** (`R4-F393`): $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  loop = 14, 26, 32, 81, width = 9, state = under → **-2.0133**

- **[P] the profile of a loop** (`R4-F403`): $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  loop = 14, 26, 32, 81, at_cut = 71, half = 36 → **-8.1875**

- **[L] the closure of a loop** (`R4-F393`): $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  loop = 26, 223, 243, 260, width = 9, state = crosses → **-35.6938**

- **[P] the profile of a loop** (`R4-F403`): $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  loop = 26, 223, 243, 260, at_cut = 173, half = 36 → **-40.2188**

- **[M] the deciding margin** (`R4-F401`): $`\mu_n = |L_n| - \min_m |L_m| - \mathrm{median}\,|L_n^{\mathrm{null}}|`$

  drifting_line = 260, tightest = narrow → **{'wing': 11.2626, 'wide': 2.8875}**

- **[L] the closure of a loop** (`R4-F393`): $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  loop = 26, 112, 243, 269, width = 9, state = under → **1.2159**

- **[P] the profile of a loop** (`R4-F403`): $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  loop = 26, 112, 243, 269, at_cut = 54, half = 36 → **7.3125**

- **[L] the closure of a loop** (`R4-F393`): $`L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)`$

  loop = 216, 308, 13, 22, width = 9, state = under → **6.9445**

- **[P] the profile of a loop** (`R4-F403`): $`P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j`$

  loop = 216, 308, 13, 22, at_cut = 308, half = 36 → **6.9446**

- **[K] the coverage** (`R4-F410`): $`\kappa = \frac{|A \wedge \bigcup_b M_b|}{|A|}`$

  chunks = 6333, of = 97771 → **0.0648**

- `rectangle`: [26, 384, 22, 243]
- `states`: {"to read": 33, "under": 3, "crosses": 1, "no wing": 1}
- `holding_loops`: [{"corners": [14, 26, 32, 81], "width": 9}, {"corners": [26, 112, 243, 269], "width": 9}, {"corners": [216, 308, 13, 22], "width": 9}]
- `bands_to_read`: 111
- `chunks_to_read`: 24263
- `estimated_reading_minutes`: 21.3
- `wings_around_an_unjudged_rectangle`: true
- `warning`: wings are certified around a rectangle that is not itself judged: they hold on their profile, but the rectangle that links them is not proved

### E7 — the judge without ground truth (B3): skipped

*requested with --judge N: it reads N certified chunks from the bucket*


### T — the transfer to the next winding (B4): done

- **[W] the walk of a neighbourhood** (`R4-F440`): $`\hat D = \arg\min_{D,\ \sum_c D_c = 0} \sum_{(i,j)} \left(D_j - D_i - s_{ij}\right)^2`$

  surfaces = {'produced': 'la_spire_produite', 'reference': 'le_segment_reduit'}, neighbourhoods = 340 → **680**

- **[A] the anchor of a block** (`R4-F446`): $`a = \mathrm{median}\left\{\hat D^{\,p}_c - \hat D^{\,r}_c \ :\ c \in \mathcal{N} \setminus B\right\}`$

  what = median |anchor| over the decided blocks, voxels → **1.5455**

- **[X] the slip mixture** (`R4-F445`): $`x \sim w_0\,\mathcal{N}(0, \sigma^2) + w_+\,\mathcal{N}(g, \sigma^2) + w_-\,\mathcal{N}(-g, \sigma^2)`$

  source = `261`, read on the segment without a judge → **69.458**

- **[R] the correction rule** (`R4-F456`): $`\tau_1 = \tau_0 - x \quad \text{if} \quad \max\left(w_+ e^{-\frac{(x-g)^2}{2\sigma^2}},\ w_- e^{-\frac{(x+g)^2}{2\sigma^2}}\right) > w_0\, e^{-\frac{x^2}{2\sigma^2}}`$

  blocks = 340 → **495**

- **[G] the sign test** (`R4-F471`): $`p = \min\left(1,\ 2 \sum_{i \le \min(a, b)} \binom{a+b}{i} 2^{-(a+b)}\right)`$

  misses_made_right = 163, rights_made_misses = 41 → **2.04447e-18**

- **[G] the sign test** (`R4-F471`): $`p = \min\left(1,\ 2 \sum_{i \le \min(a, b)} \binom{a+b}{i} 2^{-(a+b)}\right)`$

  blocks_up = 42, blocks_down = 11 → **2.24756e-05**

- `corrected_transfer`: corrected_transfer.npy
- `details`: correction.json
- `what_the_transfer_is`: the distance from each point of the segment's mesh (one point every 8 grid cells) to the next winding, in voxels along the normal, side plus, transferred by `m7` (`248`); NaN where there is no point
- `blocks`: 340
- `corrected_points`: 495
- `misses_made_right`: 163
- `rights_made_misses`: 41
- `net_gain`: 122
- `share_before`: 0.9339
- `share_after`: 0.9374
- `sign_test`: {"on_points": 2.04e-18, "on_blocks": 2.25e-05}
- `whole_segment`: {"before": {"scored_points": 38581, "share_on_the_right_winding": 0.9303}, "after": {"scored_points": 38581, "share_on_the_right_winding": 0.9334}}
- `blocks_within_validated_geometry`: 339
- `control_band`: {"surface": "20260623142658-w028-037", "pooled": {"blocks": 84, "before": 0.9527, "after": 0.9519, "scored_points": 12398, "corrected_points": 61, "misses_made_right": 15, "rights_made_misses": 25, "net_gain": -10, "blocks_up": 6, "blocks_down": 8, "blocks_unchanged": 70}, "sign_test": {"on_points": …
- `where_the_inputs_come_from`: the step tables are those of the research's renders (`275`, `281`: two surfaces rendered through `vc_render_tifxyz` from about 50 GB of chunks); this program replays the decision on them and does not render them

### E8 — the ink, the measuring rule (B3): done

- `ink_map`: PHercParis4/segments/20230702185753/ink-detection/downsampled/PHercParis4-20230702185753-2.4um-0.22m-78keV-volume-20260411134726-20260417190342-new_canon_autoresearch_recipe-tile256-stride128-ds8.jpg
- `its_shape`: [6325, 4550]
- `image`: ink_under_mask.jpg
- `reading`: the PUBLISHED ink map (the team's model, 2.4 µm), under the mask: the ink is the measuring rule that says whether the unrolling makes sense, not the work itself

### E9 — the packaging (B1): done

- `surface`: PHercParis4/segments/20230702185753/mesh/20230702185753-on-20260411134726-2.4um.tifxyz
- `its_grid`: [2530, 1820]
- `certified_vertices`: 258292
- `valid_vertices`: 4029118
- `products`: ["chunk_mask.tif", "chunk_mask.png", "certificate.json", "bands_to_read.json", "corrected_transfer.npy", "correction.json", "20230702185753_certified.tifxyz/ (x, y, z, meta.json, approval.tif)"]
- `not_produced`: `column_NN.tifxyz`: cutting the surface into text columns requires the ink to be legible column by column, and at the regime of the thirteen scrolls the published detector does not separate the sheet from the void (`R1-F20`). The deliverable is the certified surface, whole, and its mask.

