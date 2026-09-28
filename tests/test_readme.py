"""Every `vesuve` command of the README is accepted by the program: a doc that quotes a renamed flag breaks here."""
from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from vesuve import cli

HERE = Path(__file__).resolve().parents[1]


def quoted_commands() -> list[list[str]]:
    out = []
    for page in (HERE / "README.md", HERE / "examples" / "README.md", HERE / "CONTRIBUTING.md"):
        for block in re.findall(r"```bash\n(.*?)```", page.read_text(), flags=re.S):
            for line in block.splitlines():
                line = line.split("#")[0].strip()
                m = re.match(r"(?:uv run )?vesuve (.+)", line)
                if m:
                    out.append(shlex.split(m.group(1)))
    return out


def test_the_readme_quotes_commands():
    assert len(quoted_commands()) >= 4  # a page without a command would check nothing


@pytest.mark.parametrize("argv", quoted_commands(), ids=lambda a: " ".join(a))
def test_each_command_of_the_readme_is_accepted(argv, monkeypatch):
    calls = []
    for name in ("_grand_prize", "_progress", "_first_letters", "_paris4_title", "_demo", "_read"):
        monkeypatch.setattr(cli, name, lambda a, *r, _n=name: calls.append(_n) or 0)
    assert cli.main(argv) == 0 and calls  # the parsing passes, and a verb is reached without running anything
