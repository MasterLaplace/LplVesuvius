# Changelog

Written for whoever updates. The version follows SemVer: `0.y.z` promises no stability yet, and a report
field or an exit code that changes is a breaking change once 1.0 is out.

## [Unreleased]

### Added
- `vesuve.chain`, the chain of windings grown from the surface prediction `m7` (slices 345, 352, 356, 365): the criterion
  that needs no referent (a jump is held if at least three quarters of its counted points cross one sheet and fewer
  than 50 cross none, `R4-F531`, `R4-F538`), the jump and the growth from a seed, the regrowth of a held winding by one
  mesh (`R4-F551`), the chain that keeps, regrows or relaunches at each jump, the strict reading against the published
  windings, the seeds, a reader of `m7`, and a report of where the criterion was not validated. On PHercParis4, seeds 1
  to 8, it gives back the chain the research published jump by jump, 27 of the 28 judged jumps right on seeds 4 to 8, and
  the research's surfaces point for point on seeds 4 and 7. It is a library: no stage or command exposes it yet, and it
  does not read the bucket for a segment's mesh.

## [0.3.0] - 2026-10-01

The transfer to the next winding, computed here from the published surface prediction instead of replayed from
the research, and the correction run on it, which still gives back 163 for 41.

### Added
- `vesuve grand-prize` computes the transfer to the next winding itself (stage TN) instead of replaying the one the
  research saved: along the normal of each point of the mesh, one point in eight, the first sheet the prediction `m7`
  marks after the surface's own, then a vote of the neighbours, the rule of `247` (`R4-F412`). On segment
  `20230702185753` and on the band `w028-037` it gives back the research's transfers point for point within a millionth
  of a voxel, and on the segment the shares on the right winding `247` published: 0.9214, against 0.7613 for a fixed
  step. The correction then runs on the transfer computed here, and gives back 163 for 41.
- The correction runs on that transfer only where its step tables describe it: the embedded tables were rendered from
  the research's transfer. Where the transfer computed here differs, stage T corrects the research's transfer and says
  so, until `--render` makes tables for the other one; the control band follows the same rule.
- The samples of the prediction along each normal are embedded for the segment and the band (0.5 MB, one bit per
  sample), so the transfer is computed offline; `--read-prediction` reads them again from the public prediction
  (1780 chunks, about 630 MB) along the normals of the published mesh (55 MB), after checking that the scan is the
  ratio of the prediction the samples assume. The report of stage TN says where the samples come from, how many rays
  see the surface's own sheet within 12 voxels on the side read (41791 of 62815 on the segment), how many see no next
  sheet and start from the fixed step, and whether the result is the research's, on the segment and on the band.
- The formulary gains the three rules of the transfer: the sheets along a normal, the next sheet, the vote.

## [0.2.0] - 2026-09-28

The transfer to the next winding, corrected where the research validated it, and a plain statement of
where it did not hold. Everything is in English now, which breaks every script written against 0.1.0.

### Added
- `vesuve grand-prize` corrects the transfer to the next winding without a hand (stage T), the procedure of
  `265` as `275` ran it on segment `20230702185753`: 163 misses made right for 41 rights made misses on 340
  blocks, a net gain of 122, sign test p = 2.04e-18 on the points and 2.25e-05 on the blocks. It writes
  `corrected_transfer.npy` and `correction.json`, and the report says what the transfer is.
- The correction is claimed only within the geometry it was validated under, neighbours along both axes. On the
  band `20260623142658-w028-037`, one row of blocks, the same procedure gives 15 for 25 (p = 0.154): the report
  says so and nothing is written there. The geometry is necessary and not sufficient: on a taller slice of the
  band, blocks with neighbours on all four sides give 7 for 5 (p = 0.774), so the correction stays validated on
  one segment only.
- The formulary gains the six rules of the correction (window-to-window step, walk, anchor, slip mixture,
  correction rule, sign test).
- `SUBMISSION.md` answers the four questions of the September 2026 Progress Prizes form, each number linked to the
  file that produces it, with a guide to the `experimental` branch.
- The step tables, the transfer and the judges of the segment and of the band are embedded (5.9 MB), so the
  correction replays without the research tree.
- `vesuve grand-prize --render` makes those step tables here (stage TR): the two surfaces from the published mesh
  and the transfer, a local mirror of the raw scan one row of blocks at a time, two piles per block rendered by
  `vc_render_tifxyz`, and the window-to-window steps read from them. `--render-rows` bounds a trial run and
  `--keep-piles` keeps the piles. The next row downloads while the current one renders, and `--table-workers`
  processes (2 by default) read the tables meanwhile. It stops cleanly when a disk runs short, a run started again
  picks up where it stopped (it reads its tables, since piles are freed once read), and a chunk at the wrong size,
  which a crash leaves behind, is downloaded again instead of being rendered.
- Measured over the whole segment on three cores, `--render` took 5 h 09. Its 680 tables equal the research's
  seam for seam: 334 171 seams, none different, none missing. The correction run on them writes a
  `corrected_transfer.npy` byte-identical to the research's and the same `correction.json` as the replay. The run
  read 288 GB of the raw scan, since its first two rows were already on disk from a trial.
- A renderer without `--flip-normals`, like the one in villa's published images, renders the pile unflipped and
  its layers are reversed. On the renderer that has both, the two piles are identical voxel for voxel
  (`tools/check_flip_fallback.py`), and the pile's journal line says `layers_reversed`.
- `docker build --target render` puts the program on villa's published image, so `--render` runs in a container.
  Its renderer is older than the research's (villa revision `1e3f4c0`, 2026-05-13). The last row rendered with it
  changed 790 seams by at most 0.00065 voxel, and the correction decided all 340 blocks alike: the same 495 points
  moved, 14 of them by values that differ by at most 1e-4 voxel (`tools/compare_corrections.py`).
- `tools/next_winding_ink_image.py` draws the picture of research slice 296 for the submission: where the segment
  passes over the winding the transfer produces, the ink read on that winding matches the segment's own published ink
  (0.83 against 0.12 and 0.10 for two controls, on six blocks chosen without the ink).
- `tools/check_against_research.py` compares what `--render` makes with what the research made, and
  `tools/estimate_render.py` says what a render will download before it does: 153 079 chunks, 321 GB, for the
  segment.

### Changed
- **Breaking: the program is now in English**, from the command line down to the C core, so that anyone
  can read it. Scripts written against 0.1.0 need these renames:
  - verbs: `formules` is `formulas`, `lire` is `read`;
  - options: `--sortie` is `--output`, `--donnees` is `--data`, `--lire` is `--read`, `--tours` is
    `--rounds`, `--fils` is `--threads`, `--lectures` is `--readings`, `--juger` is `--judge`,
    `--sans-encre` is `--no-ink`, `--sans-surface` is `--no-surface`, `--couches` is `--layers`,
    `--rouleau` is `--scroll`, `--cote-mm` is `--side-mm`, `--modele` is `--model`, `--carte` is
    `--ink-map`, `--etiquettes` is `--labels`, `--cartes` is `--ink-maps`, `--maillages` is `--meshes`;
  - outputs: `rapport.json` and `rapport.md` are `report.json` and `report.md`, and every file a pipeline
    writes has an English name (`certificat.json` is `certificate.json`, `masque_par_chunk.tif` is
    `chunk_mask.tif`, and so on). Report fields and state words are English too: a stage is `done`,
    `stopped`, `skipped` or `partial`, a requirement is `met`, `not met`, `not measured` or
    `not applicable`;
  - environment: `VESUVE_JOURNAL` is `VESUVE_LOG`, `VESUVE_RECHERCHE` is `VESUVE_RESEARCH`,
    `VESUVE_DONNEES` is `VESUVE_DATA`, `VESUVE_RESEAU` is `VESUVE_NETWORK`;
  - the Docker image writes to `/outputs` and reads `/data`; its optional extra is `INK=1`;
  - the C library is `vesuve/_core/libvesuve.so`, and its status codes are `VESUVE_OK`,
    `VESUVE_BAD_ARGUMENT`, `VESUVE_UNDECIDABLE` and `VESUVE_NOT_IMPLEMENTED`.
- The research stays in French. Its keys become this program's names in one place,
  `vesuve/research.py`, and the parity tests go through it, so they still compare each port with the
  research's own numbers.
- Work is tracked in GitHub issues and pull requests, described in `CONTRIBUTING.md`; `backlog/` is
  retired, and its one item, V-001, is issue #1.

### Fixed
- A journal field named `code` (the exit code of a render) collided with the event code and stopped the first real
  render on its first pile; the event code is now positional-only.
- Four equations of the formulary rendered wrong on GitHub: between `$$`, GitHub strips Markdown's
  backslash escapes before the math renderer runs, so the median lost its braces, `\#\{\ell\}` in the
  consensus [C1] failed with "macro parameter character", and `\!` turned into a `!`. Each equation now
  sits in a `math` fence, and a test fails if one does not.

### Known limits
- The default Docker image does not carry `vc_render_tifxyz`, so `--render` inside it reports the renderer missing
  and the correction replays the embedded tables; the `render` target carries it. The renderer is
  ScrollPrize/villa's `volume-cartographer`.
- The correction is validated on one segment. `--render` makes its inputs from the public data, but the
  transfer itself is still the one the research's chain produced (`248`), embedded.

## [0.1.0] - 2026-09-24

The first version: one pipeline per prize, on what the research validated.

### Added
- `vesuve grand-prize`: the hand-free loop certificate on segment `20230702185753` (PHercParis4). It
  writes a per-chunk mask, the certified part of the published surface as tifxyz with `approval.tif`, and
  the published ink map under the mask. Replayed from the 112 bands the research published, it certifies
  6333 of 97771 chunks and names the 111 bands (24263 chunks) it still has to read; `--lire` reads them.
- `vesuve progress`: where a published segment changes winding (column 260, rows 26 to 223, crossing
  half a sheet at cuts 163, 173 and 203).
- `vesuve first-letters`: a 4 cm² window chosen on papyrus coverage alone, the fibre render, the view
  without a model, the model's ink, row witnesses and a 1 cm scale bar.
- `vesuve paris4-title`: the last written column of the innermost published band of PHercParis4, and the
  region after it, where an end-title would be.
- `vesuve demo`, `vesuve lire`, `vesuve formules`; a C11 core with one function per equation; a Docker
  image that builds and tests the core before installing anything.

### Known limits
- Only the Grand Prize and Progress run on embedded data. First Letters and the Paris 4 title need local
  inputs (layers, ink maps, meshes), which the demo names one by one; nothing downloads them yet.
- The certificate is measured on one segment only, and that segment was traced by someone else.
