# paris4-title — report

`vesuve 0.2.0` · core `0.2.0` · Linux x86_64 python 3.13.14 · 25.43 s

## The requirements of the prize

| requirement | state | what is measured |
|---|---|---|
| an image papyrologists can read | **not measured** | views of the end of the text on the innermost band, at 19.2 µm per pixel; nobody has read them |
| any volume of Scroll 1, 2.4 µm included | **met** | the published ink maps on the 2.4 µm volume |
| validation on a held-out region | **partial** | two independent revisions of the same band compared (T5); no ground truth |
| the core of the scroll | **not met** | windings w000 to w009 are in no published band |

## The stages

### T0 — the rule (B1): done

- `rule`: the beginning of the text is on the outside of the scroll, the end and the title (the colophon) at the core: "the end of the papyrus (the innermost part of the carbonised scroll) where the colophon with the title of the work may be preserved"
- `status`: reported (`docs/archive/06_mesures_a_faire.md:10-15`, Bodleian), not measured here
- `what_the_prize_says`: no ink detected so far in the expected region; possibly a different ink; the top rows physically missing

### T1 — the innermost band (B1): done

- `bands_seen`: 55
- `innermost`: w010-027
- `its_revisions`: ["20260623141924", "20260701183124"]
- `missing`: windings w000 to w009 are in no published band: the core itself is not traced

### T2·20260623141924 — the direction of the winding (B1): partial

*the map's silhouette only correlates at 0.30 with the mesh's: the orientation kept is not established*

- `radius_at_start_mm`: 5.54
- `radius_at_end_mm`: 2.88
- `ink_map_orientation`: identity
- `its_correlation`: 0.303
- `core_is_on_the`: right of the map

### T4·20260623141924 — the end of the text (B1): done

- `threshold`: 0.128
- `last_column`: [146, 222]
- `written_slices`: [5, 15]
- `band_share_after_the_text`: 0.5033
- `rule`: 16 slices × 449 cells along the winding, written or empty by Otsu's threshold on all the cells: no parameter chosen

### T2·20260701183124 — the direction of the winding (B1): done

- `radius_at_start_mm`: 5.41
- `radius_at_end_mm`: 2.88
- `ink_map_orientation`: identity
- `its_correlation`: 0.981
- `core_is_on_the`: right of the map

### T4·20260701183124 — the end of the text (B1): done

- `threshold`: 0.1393
- `last_column`: [239, 306]
- `written_slices`: [0, 2]
- `band_share_after_the_text`: 0.3163
- `rule`: 16 slices × 449 cells along the winding, written or empty by Otsu's threshold on all the cells: no parameter chosen

### T5 — the witness: two revisions of the same band (B3): done

- `shares_after_the_text`: [0.5033, 0.3163]
- `their_gap`: 0.187
- `reading`: two independent meshes of the same band: if they put the end of the text at the same place on the winding, the end is not an artefact of one mesh

### T6 — the candidates (B1): done

- `places`: [{"segment": "20260623141924", "last_column_px": [7344, 11218], "its_last_line_px": 5968, "its_written_height": 1.0, "candidate_region_px": {"columns": [6376, 15092], "rows": [5968, 5969]}}, {"segment": "20260701183124", "last_column_px": [11311, 14529], "its_last_line_px": 1635, "its_written_height …
- `products`: ["20260623141924_last_column.png", "20260623141924_below_the_last_line.png", "20260623141924_whole_band.jpg", "20260701183124_last_column.png", "20260701183124_below_the_last_line.png", "20260701183124_whole_band.jpg", "candidates.json"]
- `reading`: when the last column is SHORT and nothing follows it towards the core, that is the shape of the end of a book: the final title is to be looked for under its last line and in the space that follows it. In orange the column, in blue the region
- `left_to_do`: read, and look for ANOTHER ink: the prize says the expected region showed no detectable ink; these views are those of the published model, and the ink-3d product or the 1.129 µm map are the next ones to look at

