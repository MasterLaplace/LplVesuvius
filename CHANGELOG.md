# Changelog

Written for whoever updates. The version follows SemVer: `0.y.z` promises no stability yet, and a report
field or an exit code that changes is a breaking change once 1.0 is out.

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
