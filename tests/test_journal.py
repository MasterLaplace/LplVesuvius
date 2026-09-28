"""The journal: structured, correlated, filtered by level, and never on standard output."""
import io

import pytest

from vesuve.journal import Journal


def test_a_line_carries_its_code_its_run_and_its_fields():
    f = io.StringIO()
    Journal(f, "INFO", run="ab12").warn("CHUNK_REFUSED", cy=99, cx=71, reason="absent from the bucket")
    assert f.getvalue() == "WARN  CHUNK_REFUSED run=ab12 cy=99 cx=71 reason='absent from the bucket'\n"


def test_the_level_filters_without_rebuilding_anything(monkeypatch):
    f = io.StringIO()
    monkeypatch.setenv("VESUVE_LOG", "WARN")
    j = Journal(f)
    j.info("CHATTY")
    j.error("SERIOUS", what="x")
    assert "CHATTY" not in f.getvalue() and "SERIOUS" in f.getvalue()


def test_an_unknown_level_is_refused_by_its_name():
    with pytest.raises(ValueError, match="CHATTY"):
        Journal(io.StringIO(), "CHATTY")


def test_nothing_goes_to_standard_output(capsys):
    Journal(level="DEBUG").info("VISIBLE_TRACE", n=1)
    out = capsys.readouterr()
    assert out.out == "" and "VISIBLE_TRACE" in out.err
