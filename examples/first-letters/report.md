# first-letters — report

`vesuve 0.2.0` · core `0.2.0` · Linux x86_64 python 3.13.14 · 14.42 s

## The requirements of the prize

| requirement | state | what is measured |
|---|---|---|
| one of the 23 eligible scrolls | **met** | PHerc1447, volume 20250521151220 |
| ten letters in 4 cm² | **not measured** | no letter is read by this pipeline: that is the work of an eye |
| a static programmatic image, named after its mesh | **met** | 20250702235910-auto_grown_20250702235910292_ink.png, 20250702235910-auto_grown_20250702235910292_fibres.png |
| a 1 cm scale bar | **met** | 10 mm = 1157 px at 8.64 µm |
| rows annotated | **not met** | no inner autocorrelation peak, at any angle within ±12°: no rows in the model's ink |
| ink on a render where the fibres show | **met** | 20250702235910-auto_grown_20250702235910292_ink.png |
| show the text is not hallucinated | **not met** | the shuffle of the same pixels loses the line spacing; the held-out region is measured separately; no ground truth on this scroll |

## The stages

### F0 — the object and its regime (B1): done

- **[F31] the Fresnel number** (`R6-F08`): $`F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}`$

  pixel_um = 8.64, distance_m = 1.2, energy_kev = 116 → **0.414506**

- **[F31] the Fresnel number** (`R6-F08`): $`F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}`$

  regime = production, pixel_um = 2.4, distance_m = 0.2, energy_kev = 78 → **0.742916**

- `volume`: 20250521151220
- `ratio_to_production_regime`: 0.558
- `consequence`: a survey scan: the published ink models were trained at the production regime, and at the prize regime their agreement with the published map is flat (`R1-F20`). Their output here is a view, not evidence.

### F1 — the surface (B1): done

- `layers`: 31
- `middle_layer`: 15
- `shape`: [2980, 3240]
- `dtype`: uint8
- `papyrus_share`: 0.5254
- `mesh`: 20250702235910-auto_grown_20250702235910292
- `mesh_exists`: true

### F2 — the 4 cm² window (B1): done

- `side_px`: 2315
- `side_mm`: 20.0
- `window`: {"r0": 208, "c0": 528, "side": 2315, "papyrus": 3825969, "papyrus_share": 0.7139}
- `held_out_window`: {"r0": 2064, "c0": 0, "side": 523, "papyrus": 240429, "papyrus_share": 0.879, "side_reduced": true}
- `rule`: chosen on papyrus coverage ALONE, never on the ink: a window elected where the ink looks strong would make letters out of any noise

### F3 — the render where the fibres show (B1): done

- `image`: 20250702235910-auto_grown_20250702235910292_fibres.png
- `rule`: the middle layer stretched between 1 and 99 % (`couche_de_rendu.py:35`)

### F4 — the ink without a model (B1): done

- `image`: 20250702235910-auto_grown_20250702235910292_without_model.png
- `layers`: [12, 13, 14, 15, 16, 17, 18]
- `rule`: "sometimes ink is visible directly in the flattened render, with no model at all — usually bright areas": the maximum projection of the seven central layers. A view, not a detector.

### F5 — the model's ink (B3): done

- `ink_map`: /home/masterlaplace/LplVesuvius/data/out/ink_PHerc1447_complet.npy
- `provenance`: a map inferred elsewhere, given with --ink-map
- `share_seen`: 1.0
- `share_above_0`: 0.042

### F6 — the witnesses (B3): done

- `rows`: {"real": {"period_px": null, "sharpness": 0.0, "angle_deg": null, "floor": null, "periodic": false}, "shuffled": {"period_px": 76, "sharpness": 0.14880421447260087, "floor": 0.17865619976519528, "angle_deg": 10.0, "periodic": false}, "held_out": {"period_px": null, "sharpness": 0.0, "angle_deg": nul …
- `rows_drawn`: 0
- `image`: 20250702235910-auto_grown_20250702235910292_ink.png
- `rule`: `typographie.py`: the ink binarised by Otsu, the density per row autocorrelated, periodic when the sharpness exceeds 2√(2 ln k)/√n; the shuffle must lose the period
- `training_overlap`: NONE: this segment is not among the 45 labelled segments of the 2023 model

### F7 — the packaging (B1): done

- `products`: ["20250702235910-auto_grown_20250702235910292_fibres.png", "20250702235910-auto_grown_20250702235910292_ink.png", "20250702235910-auto_grown_20250702235910292_without_model.png", "windows.json"]
- `left_to_a_human`: reading: count ten letters in the window, and check they hold on the held-out region. The pipeline says where to look and what its witnesses are worth; it does not read.

