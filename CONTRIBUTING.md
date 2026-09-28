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
