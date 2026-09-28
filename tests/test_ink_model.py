"""The ported sweep of the ink model, against the research's, on a small real window.

Skipped when torch, the model or the stack is missing: the `ink` group is optional, and the First Letters report
says "the model's ink is not computed" rather than returning an empty map.
"""
from __future__ import annotations

import importlib.util

import numpy as np
import pytest

from conftest import DATA, research

MODEL = DATA / "models" / "timesformer_GP_scroll1"
STACK = DATA / "couches" / "1447_20250702235910"

pytestmark = [research, pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="torch missing"),
              pytest.mark.skipif(not (MODEL / "config.json").exists() or not STACK.exists(),
                                 reason="the model or the PHerc1447 stack is missing")]


def test_the_ink_map_is_the_research_one():
    import infer_ink as ref
    from vesuve.render import model
    window = (1200, 1500, 160, 160)
    m = model.load(MODEL)
    stack = model.ink_stack(STACK, 2, window)
    assert np.array_equal(stack, ref.load_layer_stack(STACK, 2, window))
    mine, n = model.infer(stack, m, step=21, batch=4, threads=8)
    theirs, n_ref, _ = ref.infer(stack, m, 21, 4, 8, "cpu", progression=False)
    assert n == n_ref == 25
    assert np.array_equal(np.isnan(mine), np.isnan(theirs))
    assert np.allclose(mine, theirs, atol=1e-5, equal_nan=True)
