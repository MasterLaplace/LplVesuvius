"""The program's borders, checked and not only drawn.

A prize never imports another prize; what they share lives in a shared module (`lattice/` for the Grand Prize and the
audit, `render/` for First Letters and the title) or in the common services. And the C core depends on nothing: it is
what everything else calls.
"""
from __future__ import annotations

import ast
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "vesuve"
PRIZES = ("grand_prize", "first_letters", "paris4_title", "progress")


def _imports(path: Path) -> set[str]:
    out = set()
    for n in ast.walk(ast.parse(path.read_text())):
        if isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
        elif isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
    return out


def test_a_prize_never_imports_another_prize():
    seen = 0
    for prize in PRIZES:
        for f in (PACKAGE / prize).glob("*.py"):
            for m in _imports(f):
                others = [p for p in PRIZES if p != prize and m.startswith(f"vesuve.{p}")]
                assert not others, f"{f.relative_to(PACKAGE)} imports {m}"
            seen += 1
    assert seen >= 8


def test_the_shared_modules_import_no_prize():
    for folder in ("lattice", "render"):
        for f in (PACKAGE / folder).glob("*.py"):
            for m in _imports(f):
                assert not any(m.startswith(f"vesuve.{p}") for p in PRIZES), f"{f.name} imports {m}"


def test_the_c_core_depends_on_the_standard_library_only():
    for f in (PACKAGE.parent / "core" / "src").glob("*.c"):
        for line in f.read_text().splitlines():
            if line.startswith("#include"):
                assert line.split()[1].strip('<>"') in {"vesuve.h", "math.h", "stdlib.h", "stdint.h", "stddef.h",
                                                        "string.h"}, f"{f.name}: {line}"
