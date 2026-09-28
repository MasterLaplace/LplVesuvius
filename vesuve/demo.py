"""`vesuve demo`: the four pipelines in a row, and a table of what each concluded.

The Grand Prize and Progress run on the embedded segment, with nothing else (the network only adds the ink map and
the surface). First Letters and the Paris 4 title need data the program does not embed (layer stacks, ink maps):
they are given with `--data`, a folder organised as the `data/` of the `experimental` branch, and without it they
are skipped, naming what it should carry.
"""
from __future__ import annotations

from pathlib import Path

INPUTS = {
    # ⚠ The folder itself and not `couches/1447_20250702235910`, which is a link to an ABSOLUTE path of the host:
    # mounted in a container, it points to nothing.
    "first-letters": {"layers": "couches/PHerc1447_complet",
                      "surface": "segments_officiels/20250702235910-auto_grown_20250702235910292",
                      "ink_map": "out/ink_PHerc1447_complet.npy",
                      "labels": "repos/Vesuvius-Grandprize-Winner/all_labels"},
    "paris4-title": {"ink_maps": "encre/PHercParis4", "meshes": "paris4_bandes"},
}


def _missing(d: Path | None, inputs: dict) -> str | None:
    """None if everything is there; otherwise each missing input, by name, and whether it is a dead link."""
    if d is None:
        return "give --data DIR, which carries " + ", ".join(inputs.values())
    missing = [f"{v}{' (dead link)' if (d / v).is_symlink() else ''}" for v in inputs.values() if not (d / v).exists()]
    return ("missing from " + str(d) + ": " + ", ".join(missing)) if missing else None


def run(output: Path, cache: Path, journal, data: Path | None = None) -> int:
    from vesuve.first_letters.pipeline import run as first_letters
    from vesuve.grand_prize.pipeline import run as grand_prize
    from vesuve.paris4_title.pipeline import run as paris4_title
    from vesuve.progress.pipeline import run as progress
    rows = []

    def note(prize, r=None, reason=""):
        if r is None:
            rows.append((prize, "skipped", reason))
            return
        req = r.data["requirements"]
        met = sum(1 for x in req if x["state"] == "met")
        stop = r.data["stop"]
        rows.append((prize, "stopped at " + stop["stage"] if stop else "to the end", f"{met} requirements met of {len(req)}"))

    note("grand-prize", grand_prize(output=output / "grand-prize", cache=cache, journal=journal))
    note("progress", progress(output=output / "progress", cache=cache, journal=journal))
    d = Path(data) if data else None
    e = INPUTS["first-letters"]
    missing = _missing(d, e)
    if missing is None:
        note("first-letters", first_letters(d / e["layers"], d / e["surface"], "PHerc1447", output / "first-letters",
                                            ink_map=d / e["ink_map"], labels=d / e["labels"], journal=journal))
    else:
        note("first-letters", reason=missing)
    e = INPUTS["paris4-title"]
    missing = _missing(d, e)
    if missing is None:
        note("paris4-title", paris4_title(d / e["ink_maps"], output / "paris4-title", cache, meshes=d / e["meshes"],
                                          journal=journal))
    else:
        note("paris4-title", reason=missing)
    print(f"{'prize':<14} {'outcome':<16} what is concluded")
    for prize, outcome, what in rows:
        print(f"{prize:<14} {outcome:<16} {what}")
    print(f"\nthe reports: {output}/<prize>/report.md")
    return 0
