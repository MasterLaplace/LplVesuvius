"""The rendering shared by First Letters and Paris 4: windows chosen without the ink, and rows without reading."""
from __future__ import annotations

import numpy as np

from conftest import research
from vesuve.render import rows, windows


def _page(period=30, thickness=4, side=400, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    img = np.full((side, side), 60, dtype=np.uint8)
    for r in range(40, side - 40, period):
        img[r:r + thickness, 40:side - 40] = 220
    if noise:
        img = np.clip(img + rng.normal(0, noise, img.shape), 1, 255).astype(np.uint8)
    return img


@research
def test_the_line_spacing_is_the_research_one():
    import typographie as ref
    rng = np.random.default_rng(1)
    seen = 0
    for seed in range(30):
        img = _page(int(rng.integers(12, 40)), int(rng.integers(2, 7)), noise=float(rng.uniform(0, 60)), seed=seed)
        if seed % 3 == 0:
            img = rng.integers(1, 255, size=img.shape).astype(np.uint8)  # pure noise
        m = img > 0
        b = rows.binarise_ink(img, m)
        assert np.array_equal(b, ref.binariser_encre(img, m))
        theirs = ref.interligne(b, m)
        assert rows.line_spacing(b, m) == {"period_px": theirs["periode_px"], "sharpness": theirs["nettete"],
                                           "floor": theirs["plancher"], "angle_deg": theirs["angle_deg"],
                                           "periodic": theirs["periodique"]}
        seen += 1
    assert seen == 30


def test_a_lined_page_is_periodic_and_its_shuffle_no_longer_is():
    img = _page(30, 4, noise=20)
    m = img > 0
    b = rows.binarise_ink(img, m)
    x = rows.line_spacing(b, m)
    assert x["periodic"] and abs(x["period_px"] - 30) <= 1
    assert not rows.line_spacing(rows.shuffle(b, m, 7), m)["periodic"]


def test_the_window_is_chosen_on_the_papyrus_and_the_held_out_one_does_not_overlap_it():
    m = np.zeros((600, 900), dtype=bool)
    m[50:550, 100:850] = True
    w = windows.best_window(m, 256)
    assert w["papyrus_share"] == 1.0 and (w["r0"], w["c0"]) == (64, 112)  # the first full one in reading order
    t = windows.held_out_window(m, 256, w)
    assert not (t["r0"] < w["r0"] + 256 and w["r0"] < t["r0"] + 256 and t["c0"] < w["c0"] + 256 and w["c0"] < t["c0"] + 256)
    assert t["side_reduced"] is False
    assert windows.best_window(m, 1000) is None


def test_the_rows_drawn_fall_on_the_lines_even_skewed():
    from scipy import ndimage
    img = _page(28, 5, side=500, noise=15)
    img = ndimage.rotate(img, 6, order=0, reshape=False, mode="constant", cval=60)
    m = np.ones(img.shape, dtype=bool)
    m[:60, :] = m[-60:, :] = m[:, :60] = m[:, -60:] = False  # an edge: the rotation leaves background there
    b = rows.binarise_ink(img, m)
    x = rows.line_spacing(b, m)
    assert x["periodic"]
    assert abs(abs(rows.row_skew(b, m)) - 6) <= 1  # the angle at which the lines contrast
    trace = rows.row_lines(b, m, x)
    on_the_ink = b[trace].mean()
    assert trace.sum() > 0 and on_the_ink > 2 * b[m].mean()  # the lines drawn are on the ink
