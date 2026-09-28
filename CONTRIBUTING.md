# Contributing

This page is for changing the program. To use it, start with the [README](README.md).

## The two branches

- **`main`** is the program. Everything here is tested against a published number.
- **`experimental`** is the research it comes from, in dated slices. It shares no history with `main` and
  is never merged into it. A result reaches `main` by being rewritten here, with a test that compares the
  port with the research code that produced the number.

## How a change flows

1. **An issue** says what is asked, what is true today, what is missing, and how we will know it is done.
2. **A branch** from `main`, named `<type>/<issue>-<slug>`, for example `feat/2-correct-the-transfer`.
3. **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/), in English, signed
   (`git commit -S`). A commit can be reverted on its own without breaking the build.
4. **A pull request** that closes its issue (`Closes #2`) and says what changed, why, how to verify it,
   and what is not in it.
5. **The changelog**: every observable change adds a line under `## [Unreleased]` in
   [`CHANGELOG.md`](CHANGELOG.md), written for whoever updates.

## How the work is planned

- **The direction** is the 2027 Grand Prize: 100 % of the recto of an eligible scroll unrolled without a hand. The
  other prizes are taken along the way, when the work serves them. The pinned *Roadmap* issue gives today's order.
- **Milestones are months**, each ending on a Progress Prize deadline, plus *Later* for what waits on a fact that is
  not yet established. An issue may move to the next month; the move and its reason are written in the issue.
- **Labels say what an issue serves**: `grand-prize`, `progress-prize`, `paris4-title`, `first-letters`. `research`
  marks a question answered on `experimental`. An issue is open or closed, and nothing else: its rank within its
  milestone is the first line of its body.
- **A `research` issue** names the doors of `docs/rapports/REGISTRE_portes.tsv` it addresses, without copying them:
  the registry stays the source of the research's open questions. A dated slice closes it by establishing or refuting
  a fact, and a negative result closes it as well as a positive one.
- **A `feat` issue** names the facts (`R*-F*`) that validate what it ports, and what the report will say where they do
  not hold. Nothing reaches `main` without an established fact behind it: until the fact exists, the issue waits in
  *Later* and names the fact it waits on.
- **Nothing postpones the hardest part without it showing.** Until unrolling from a scroll with no human trace has a
  first established fact, every monthly milestone holds at least one open issue on it.
- **When a milestone closes**, what remains moves with its reason, the rule above is checked, and the *Roadmap* issue
  is brought up to date.

## Before opening a pull request

```bash
make test                            # the C core under AddressSanitizer and UndefinedBehaviorSanitizer
make                                 # the shared library the Python layer loads
uv run --extra tests pytest -q -rs   # twice: an order dependency or a leftover state shows on the second run
uv run --extra tests pytest -q
```

No warning crosses a merge: the C flags live in the `Makefile` with `-Werror`, and pytest turns warnings
into errors. The parity tests need a working copy of `experimental` in `VESUVE_RESEARCH`; without it
they are skipped and say so. The CI does the same checkout, so a pull request is compared with the
published numbers whether or not you have the research locally.

## Versions

[SemVer](https://semver.org/). While the version is `0.y.z`, a breaking change (a CLI option, a report
field, an output file name, an exit code) bumps `y`; a fix bumps `z`. A signed tag `v*` builds the Docker
image and publishes it to `ghcr.io/masterlaplace/vesuve`.
