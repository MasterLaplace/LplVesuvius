# Changelog

Written for whoever updates. The version follows SemVer: `0.y.z` promises no stability yet, and a report
field or an exit code that changes is a breaking change once 1.0 is out.

## [Unreleased]

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
- Four equations of the formulary rendered wrong on GitHub: between `$$`, GitHub strips Markdown's
  backslash escapes before the math renderer runs, so the median lost its braces, `\#\{\ell\}` in the
  consensus [C1] failed with "macro parameter character", and `\!` turned into a `!`. Each equation now
  sits in a `math` fence, and a test fails if one does not.

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
