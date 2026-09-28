"""The embedded data equals a fresh extraction, and it is enough to replay the certificate without the research tree."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from conftest import MEASURES, RESEARCH, research
from vesuve import embedded
from vesuve.lattice import certificate as cert
from vesuve.research import to_english

HERE = Path(__file__).resolve().parents[1]


@research
def test_the_embedded_data_equals_a_fresh_extraction(tmp_path):
    spec = importlib.util.spec_from_file_location("extract", HERE / "tools" / "extract_from_research.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    tmp_path = tmp_path / "segments" / m.SEGMENT
    m.extract(RESEARCH, tmp_path)
    for f in ("presence.json.gz", "published_bands.json.gz", "control_sources.json.gz"):
        assert (tmp_path / f).read_bytes() == (embedded.ROOT / m.SEGMENT / f).read_bytes(), \
            f"{f} is stale: run tools/extract_from_research.py again"
    assert (tmp_path.parents[1] / "paris4" / "axis.json").read_bytes() == \
        (embedded.ROOT.parent / "paris4" / "axis.json").read_bytes(), "axis.json is stale"
    fresh = json.loads((tmp_path / "context.json").read_text())
    kept = embedded.segment(m.SEGMENT)["context"]
    fresh["provenance"].pop("research_commit")
    kept = {**kept, "provenance": {k: v for k, v in kept["provenance"].items() if k != "research_commit"}}
    assert fresh == kept, "context.json is stale: run tools/extract_from_research.py again"


def test_the_certificate_replays_from_the_embedded_data_alone():
    """Without the research tree: that is what the Docker image will do."""
    s = embedded.segment("20230702185753")
    r = cert.certify(s["presence"], s["bands"], s["context"]["procedure"])
    assert r["coverage"] == {"count": 6333, "of": 97771, "share": 0.0648}
    assert r["left_to_read"] == 24263 and len(r["requests"]) == 111


@research
def test_the_replay_from_the_embedded_data_equals_the_publication():
    s = embedded.segment("20230702185753")
    r = cert.certify(s["presence"], s["bands"], s["context"]["procedure"])
    published = to_english(json.loads((MEASURES / "la_couverture_sans_main.json").read_text()))
    assert r["requests"] == published["requests"]
    assert r["holding_loops"] == published["holding_loops"]


@research
def test_the_embedded_correction_inputs_equal_a_fresh_extraction(tmp_path):
    """Only where the research's unversioned `data/` lives: the step tables come from its renders."""
    import pytest
    if not (RESEARCH / "data" / "rendu_spire_voisine" / "les_pas").is_dir():
        pytest.skip(f"the research's renders are not under {RESEARCH / 'data'}")
    spec = importlib.util.spec_from_file_location("extract", HERE / "tools" / "extract_from_research.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = tmp_path / "segments" / m.SEGMENT
    m.extract_correction(RESEARCH, out)
    for name in (m.SEGMENT, m.BAND):
        fresh, kept = out.parent / name / "correction", embedded.ROOT / name / "correction"
        assert sorted(p.name for p in fresh.iterdir()) == sorted(p.name for p in kept.iterdir())
        for f in fresh.iterdir():
            assert f.read_bytes() == (kept / f.name).read_bytes(), f"{name}/correction/{f.name} is stale"
