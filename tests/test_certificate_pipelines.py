"""The Grand Prize and Progress pipelines, offline, on the embedded segment."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tifffile

from vesuve import embedded, formulary
from vesuve.grand_prize.pipeline import run as grand_prize
from vesuve.progress.pipeline import run as progress
from vesuve.transport import InMemoryTransport


def _offline(monkeypatch):
    """Not one byte goes out: the transport knows no URL, so everything remote is absent."""
    monkeypatch.setattr("vesuve.grand_prize.pipeline.Transport", lambda **_: InMemoryTransport({}))
    monkeypatch.setattr("vesuve.progress.pipeline.Transport", lambda **_: InMemoryTransport({}))


def test_the_grand_prize_offline_returns_its_certificate_and_says_what_it_does_not_produce(tmp_path, monkeypatch):
    _offline(monkeypatch)
    r = grand_prize(output=tmp_path, cache=tmp_path / "cache")
    d = json.loads((tmp_path / "report.json").read_text())
    stages = {s["id"]: s for s in d["stages"]}
    assert [s["id"] for s in d["stages"]] == ["E0", "E1", "E2", "B", "E4", "E4L", "E6", "E7", "TR", "T", "E8", "E9"]
    assert stages["E2"]["equations"][0]["value"] == 36
    assert round(min(q["value"] for q in stages["B"]["equations"] if q["id"] == "N5"), 2) == 112.08
    assert round(next(q["value"] for q in stages["B"]["equations"] if q["id"] == "N7"), 4) == 2.3394  # R4-F343
    assert stages["E6"]["outputs"]["chunks_to_read"] == 24263
    assert stages["E8"]["state"] == "skipped" and "absent" in stages["E8"]["reason"]  # never an empty image
    m = tifffile.imread(tmp_path / "chunk_mask.tif")
    assert m.shape == (396, 285) and int((m == 2).sum()) == 6333
    requirements = {x["requirement"]: x["state"] for x in d["requirements"]}
    assert requirements["100 % of the recto unrolled"] == "not met"
    assert requirements["one mesh per column, `column_NN.tifxyz`"] == "not met"
    assert requirements["the transfer to the next winding corrected without a hand"] == "met"  # offline: embedded
    assert stages["T"]["outputs"]["net_gain"] == 122 and (tmp_path / "corrected_transfer.npy").exists()
    assert stages["TR"]["state"] == "skipped" and "--render" in stages["TR"]["reason"]
    assert not r.stopped


def test_the_audit_names_column_260(tmp_path, monkeypatch):
    _offline(monkeypatch)
    progress(output=tmp_path, cache=tmp_path / "cache")
    cases = json.loads((tmp_path / "failure_cases.json").read_text())
    assert len(cases) == 1 and cases[0]["drifting_line"] == 260
    assert cases[0]["cuts_beyond_half_sheet"] == [163, 173, 203]  # the two crossings of `245`
    m = tifffile.imread(tmp_path / "audit_mask.tif")
    assert int((m == 3).sum()) > 0 and not np.any((m == 3) & (m == 2))


def test_a_given_band_that_does_not_fall_back_stops_the_grand_prize(tmp_path, monkeypatch):
    _offline(monkeypatch)
    b = json.loads(json.dumps(next(x for x in embedded.segment("20230702185753")["bands"] if x["direction"] == "rows")))
    line = next(iter(b["along"]))
    b["along"][line][next(iter(b["along"][line]))][0] += 2.0
    (tmp_path / "wrong.json").write_text(json.dumps({"bands": {"wrong": b}}))
    r = grand_prize(output=tmp_path / "s", cache=tmp_path / "cache", readings=[tmp_path / "wrong.json"])
    assert r.stopped and r.data["stop"]["stage"] == "E4"


def test_each_equation_that_carries_a_computation_performs_it():
    for e in formulary.FORMULARY.values():
        assert e.fact and e.latex and e.source
    assert formulary.equation("N5").compute(36.0, 3.4004) > 112


def test_the_published_formulary_is_the_one_the_code_renders():
    from vesuve.cli import formulary_as_markdown
    published = Path(__file__).resolve().parents[1] / "FORMULARY.md"
    assert published.read_text() == formulary_as_markdown(), "FORMULARY.md is stale: `vesuve formulas --markdown`"


def test_every_equation_reaches_github_with_its_backslashes():
    """GitHub eats Markdown escapes between `$$` (`\\{` becomes `{`), so each equation must sit verbatim in a fence."""
    import re

    from vesuve.cli import formulary_as_markdown
    from vesuve.formulary import FORMULARY
    page = formulary_as_markdown()
    fenced = re.findall(r"```math\n(.*?)\n```", page, flags=re.S)
    assert "$$" not in page
    assert sorted(fenced) == sorted(e.latex for e in FORMULARY.values())
    assert any("\\{" in x for x in fenced)  # the case that broke on GitHub is among those checked


def test_without_the_renderer_the_tables_are_not_made_and_the_correction_says_whose_it_replays(tmp_path, monkeypatch):
    _offline(monkeypatch)
    monkeypatch.setattr("vesuve.grand_prize.pipeline.rendering.renderer", lambda: None)
    grand_prize(output=tmp_path, cache=tmp_path / "cache", ink=False, surface=False, render=True)
    stages = {s["id"]: s for s in json.loads((tmp_path / "report.json").read_text())["stages"]}
    assert stages["TR"]["state"] == "partial" and "vc_render_tifxyz" in stages["TR"]["reason"]
    assert stages["T"]["state"] == "done" and "research's renders" in stages["T"]["outputs"]["where_the_inputs_come_from"]
