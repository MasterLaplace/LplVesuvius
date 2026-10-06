"""The citation names the version that is installed.

`CITATION.cff` is what GitHub shows under "Cite this repository". A release that leaves its version behind
has people cite a version that is not the one they ran.
"""
from __future__ import annotations

import re
from pathlib import Path

from vesuve import __version__

CITATION = Path(__file__).resolve().parents[1] / "CITATION.cff"


def test_the_citation_names_the_installed_version():
    found = re.search(r'^version: "([^"]*)"$', CITATION.read_text(), re.MULTILINE)
    assert found, "CITATION.cff has no quoted version"
    assert found.group(1) == __version__
