"""What the tests share: where the research code that serves as oracle lives, and the network."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# The research code is the ORACLE of the parity tests: it produced every published number, so a rewrite that does not
# return its outputs on the same inputs is not a rewrite. It lives on the `experimental` branch; `VESUVE_RESEARCH`
# points to a working copy of that branch, for instance `git worktree add ../LplVesuvius-experimental experimental`.
_ROOT = os.environ.get("VESUVE_RESEARCH")
RESEARCH = Path(_ROOT) if _ROOT else Path("VESUVE_RESEARCH-not-set")
MEASURES = RESEARCH / "docs" / "mesures"
# The heavy data (stacks, models) is not versioned: `VESUVE_DATA` points to the `data/` that carries it.
DATA = Path(os.environ.get("VESUVE_DATA", RESEARCH / "data"))


def research_is_here() -> bool:
    return _ROOT is not None and (RESEARCH / "src" / "nappe" / "la_couverture_sans_main.py").exists()


if research_is_here():
    for family in sorted((RESEARCH / "src").iterdir()):
        if family.is_dir() and str(family) not in sys.path:
            sys.path.insert(0, str(family))

research = pytest.mark.skipif(
    not research_is_here(),
    reason=(f"the research code (the oracle) is not under {RESEARCH}" if _ROOT else
            "VESUVE_RESEARCH is not set: point it to a working copy of the experimental branch"))
network = pytest.mark.skipif(os.environ.get("VESUVE_NETWORK") != "1",
                             reason="reads the public bucket: run with VESUVE_NETWORK=1")
