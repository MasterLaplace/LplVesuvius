"""First Letters and the Paris 4 title, on made data whose answer is known."""
from __future__ import annotations

import json

import numpy as np
import tifffile
from PIL import Image

from vesuve.first_letters.pipeline import run as first_letters
from vesuve.paris4_title import pipeline as p4


def _stack(folder, side=700, layers=31):
    """A round papyrus surface: horizontal fibres, and 0 outside the papyrus as in a real render."""
    folder.mkdir(parents=True)
    rng = np.random.default_rng(0)
    y, x = np.mgrid[:side, :side]
    papyrus = (y - side / 2) ** 2 + (x - side / 2) ** 2 < (0.48 * side) ** 2
    for i in range(layers):
        a = 120 + 30 * np.sin(y / 3.0) + rng.normal(0, 10, (side, side))
        tifffile.imwrite(folder / f"{i:02d}.tif", np.where(papyrus, np.clip(a, 1, 255), 0).astype(np.uint8))
    return papyrus


def _lined_map(papyrus, period=24):
    """Logits: rows of ink every `period` pixels, noise elsewhere."""
    rng = np.random.default_rng(1)
    y = np.arange(papyrus.shape[0])[:, None] * np.ones(papyrus.shape)
    c = np.where((y % period) < 5, 3.0, -3.0) + rng.normal(0, 0.5, papyrus.shape)
    return np.where(papyrus, c, np.nan).astype(np.float32)


def test_first_letters_draws_the_rows_of_a_lined_map_and_the_shuffle_loses_them(tmp_path):
    papyrus = _stack(tmp_path / "layers")
    np.save(tmp_path / "ink.npy", _lined_map(papyrus))
    (tmp_path / "20250101000000-trial.tifxyz").mkdir()
    r = first_letters(tmp_path / "layers", tmp_path / "20250101000000-trial.tifxyz", "PHerc1447", tmp_path / "s",
                      side_mm=4.0, ink_map=tmp_path / "ink.npy")
    d = json.loads((tmp_path / "s" / "report.json").read_text())
    f6 = next(s for s in d["stages"] if s["id"] == "F6")
    assert f6["outputs"]["rows"]["real"]["periodic"]
    assert abs(f6["outputs"]["rows"]["real"]["period_px"] - 24) <= 1
    assert not f6["outputs"]["rows"]["shuffled"]["periodic"]
    req = {x["requirement"]: x["state"] for x in d["requirements"]}
    assert req["rows annotated"] == "met" and req["ten letters in 4 cm²"] == "not measured"
    assert (tmp_path / "s" / "20250101000000-trial_ink.png").exists() and not r.stopped


def test_first_letters_refuses_a_scroll_that_is_not_eligible(tmp_path):
    _stack(tmp_path / "layers", side=200)
    r = first_letters(tmp_path / "layers", tmp_path / "x.tifxyz", "PHercParis4", tmp_path / "s")
    assert r.stopped and r.data["stop"]["stage"] == "F0"


def _band(folder, width=4490, height=1600):
    """An unrolled band: three full columns, then a SHORT column, then nothing up to the core (on the right)."""
    rng = np.random.default_rng(2)
    ink_map = np.full((height, width), 40, dtype=np.uint8) + rng.integers(0, 30, (height, width)).astype(np.uint8)
    for c0, lines in ((200, 40), (1100, 40), (2000, 40), (2900, 8)):
        for k in range(lines):
            r = 60 + k * 36
            ink_map[r:r + 12, c0:c0 + 700] = 230
    Image.fromarray(ink_map).save(folder / "20260101000000-w010-027.jpg")
    # The mesh: 20 × 449 cells on a spiral whose radius DECREASES towards the right.
    m = folder / "meshes" / "20260101000000"
    m.mkdir(parents=True)
    j = np.arange(449)[None, :] * np.ones((20, 1))
    theta, radius = j / 449 * 12 * np.pi, 6.0 - 3.0 * j / 449  # mm
    v = 0.045532
    z = (40.0 + np.arange(20)[:, None] * 2.0 + 0 * j) / v
    x = (46.3 + radius * np.cos(theta)) / v
    y = (56.3 + radius * np.sin(theta)) / v
    for name, a in (("x", x), ("y", y), ("z", z)):
        tifffile.imwrite(m / f"{name}.tif", a.astype(np.float32))
    return folder / "meshes"


def test_the_title_is_looked_for_under_the_short_last_column(tmp_path):
    meshes = _band(tmp_path)
    p4.run(tmp_path, tmp_path / "s", meshes=meshes)
    places = json.loads((tmp_path / "s" / "candidates.json").read_text())
    assert len(places) == 1
    c0, c1 = places[0]["last_column_px"]
    assert 2800 <= c0 <= 2950 and 3550 <= c1 <= 3700  # the short column, not the second-to-last
    assert places[0]["its_written_height"] < 0.3  # eight lines at the top
    d = json.loads((tmp_path / "s" / "report.json").read_text())
    t2 = next(s for s in d["stages"] if s["id"].startswith("T2"))
    assert t2["outputs"]["core_is_on_the"] == "right of the map"
