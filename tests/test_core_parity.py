"""The C core against the very function that produced each published number.

Each test draws thousands of inputs, gives them to both, and requires the SAME output. An approximate equality is
admitted only where the research itself rounds or accumulates in float32, and that is said where it happens. The
research functions keep their own (French) names and output keys.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from conftest import MEASURES, research
from vesuve import core

pytestmark = research

SEED = 20260924


def _papyrus_profiles(rng, n=109, sheets=3):
    """Two realistic edge profiles: bright sheets in a medium at 115-130, shifted.

    The profile is a MEAN of sixteen integer voxels, hence a multiple of 1/16: the same shape the research hands to
    `un_pas`.
    """
    z = np.arange(n)
    shift = int(rng.integers(-40, 41))
    centres = rng.uniform(10, n - 10, size=sheets)

    def column(dz):
        v = 120.0 + rng.normal(0, 6, size=(16, n))
        for c in centres:
            v += 90.0 * np.exp(-((z - c - dz) / rng.uniform(1.5, 3.0)) ** 2)
        return np.clip(np.round(v), 0, 255).astype(np.uint8).sum(axis=0) / 16.0

    return column(0), column(shift)


def test_the_step_of_a_cut_is_the_research_one():
    from la_derive_saccumule_t_elle import un_pas
    rng = np.random.default_rng(SEED)
    compared = 0
    for _ in range(3000):
        a, b = _papyrus_profiles(rng)
        theirs = un_pas(a.reshape(-1, 1), b.reshape(-1, 1), 1, 36)
        if not theirs["decidable"]:
            with pytest.raises(core.Undecidable):
                core.cut_step(a, b, 36)
            continue
        step, saturated = core.cut_step(a, b, 36)
        assert (step, saturated) == (theirs["le_pas_en_voxels"], theirs["il_sature"])
        compared += 1
    assert compared > 2900  # an empty corpus would prove nothing


def test_a_flat_edge_is_undecidable_on_both_sides():
    from la_derive_saccumule_t_elle import un_pas
    a, b = np.full(109, 120.0), np.linspace(100, 140, 109)
    assert un_pas(a.reshape(-1, 1), b.reshape(-1, 1), 1, 36)["decidable"] is False
    with pytest.raises(core.Undecidable):
        core.cut_step(a, b, 36)


def test_the_step_of_a_seam_is_the_research_one():
    from combien_de_rangees_faut_il_pour_lire_le_pas import le_pas_de_k_rangees
    rng = np.random.default_rng(SEED + 1)
    compared = 0
    for _ in range(400):
        cuts = list(range(4, 128, 8))
        rights, lefts, readable = {}, {}, []
        a2, b2 = np.zeros((16, 109)), np.zeros((16, 109))
        for i, r in enumerate(cuts):
            a, b = _papyrus_profiles(rng)
            a2[i], b2[i] = a, b
            ok = bool(rng.random() > 0.15)  # a cut missing from one of the two chunks
            readable.append(ok)
            if ok:
                rights[r], lefts[r] = a, b
        theirs = le_pas_de_k_rangees(rights, lefts, cuts, 36)
        if not theirs["decidable"]:
            with pytest.raises(core.Undecidable):
                core.seam_step(a2, b2, readable, 36)
            continue
        step, disagreement, n = core.seam_step(a2, b2, readable, 36)
        # The research rounds to four decimals with `round`; the same is applied.
        assert (round(step, 4), round(disagreement, 4), n) == (
            theirs["le_pas_en_voxels"], theirs["le_desaccord_en_voxels"], theirs["les_rangees"])
        compared += 1
    assert compared > 350


def test_the_edge_profiles_are_the_research_means():
    from combien_de_rangees_faut_il_pour_lire_le_pas import (les_bords_droit_et_gauche, les_bords_haut_et_bas,
                                                            les_rangees_a_lire)
    rng = np.random.default_rng(SEED + 2)
    block = rng.integers(0, 256, size=(109, 128, 128), dtype=np.uint8)
    cuts = les_rangees_a_lire(128, 16)
    right, left = les_bords_droit_et_gauche(block, cuts, 16)
    bottom, top = les_bords_haut_et_bas(block, cuts, 16)
    s = core.edge_profiles(block, cuts, 16)
    for i, c in enumerate(cuts):
        # A sum of sixteen integers divided by sixteen is exact in double: the equality is STRICT.
        assert np.array_equal(s["right"][i] / 16.0, right[c])
        assert np.array_equal(s["left"][i] / 16.0, left[c])
        assert np.array_equal(s["bottom"][i] / 16.0, bottom[c])
        assert np.array_equal(s["top"][i] / 16.0, top[c])


def test_the_texture_filter_keeps_what_the_research_keeps():
    """⚠ The research accumulates its gradients in float32, the core in exact integers: a layer at the floor may
    flip. The corpus is therefore TIGHTENED around the floor, the test counts the layers that fall there (without
    them it would check nothing), and it counts the flips instead of hiding them."""
    from fiber_orientation import orientation_profile
    from le_creux_borne_t_il_la_marche import la_courbe_dun_bloc
    rng = np.random.default_rng(SEED + 3)
    y = np.arange(128)[None, :, None]
    near_the_floor, layer_flips, chunk_flips = 0, 0, 0
    for _ in range(60):
        # Stripes whose strength varies with the layer, around the one that puts the coherence at the floor: in a
        # noise of sigma 20, <gy^2> gains 0.2146 A^2 over 800, so 0.15 falls near A = 36. Every cube crosses the floor.
        strength = np.linspace(rng.uniform(25, 34), rng.uniform(38, 48), 109)[:, None, None]
        block = rng.normal(120, 20, size=(109, 128, 128)) + strength * np.sin(y / 3.0)
        block = np.clip(np.round(block), 0, 255).astype(np.uint8)
        _, coh = orientation_profile(block)
        coh = np.asarray(coh)
        near_the_floor += int((np.abs(coh - 0.15) < 0.005).sum())
        layers, kept = core.texture_filter(block, 0.15)
        layer_flips += abs(layers - int((coh > 0.15).sum()))
        curve, _ = la_courbe_dun_bloc(block)
        chunk_flips += int((curve is not None) != kept)
    assert near_the_floor >= 50, f"only {near_the_floor} layers at the floor: the test tests nothing"
    assert layer_flips == 0
    assert chunk_flips == 0


def test_the_block_length_is_the_research_one():
    from pourquoi_lerreur_declaree_est_trop_petite import la_longueur_de_bloc
    for n in range(1, 10001):
        assert core.block_length(n) == min(la_longueur_de_bloc(n), n)


def test_the_fresnel_number_is_the_research_one():
    from nombre_de_fresnel import nombre_de_fresnel
    rng = np.random.default_rng(SEED + 4)
    for _ in range(2000):
        p, d, e = rng.uniform(0.5, 50), rng.uniform(0, 12), rng.uniform(20, 150)
        assert core.fresnel_number(p, d, e) == nombre_de_fresnel(p, d, e)


def test_the_fresnel_number_returns_what_the_measurement_publishes():
    m = json.loads((MEASURES / "nombre_de_fresnel.json").read_text())
    seen = 0
    for scan in m["scans"]:
        if all(scan.get(k) is not None for k in ("pas_um", "distance_m", "energie_kev", "fresnel")):
            # The JSON carries the value at full precision: the equality is strict.
            assert core.fresnel_number(scan["pas_um"], scan["distance_m"], scan["energie_kev"]) == scan["fresnel"]
            seen += 1
    assert seen >= 50


def test_the_area_under_the_curve_is_the_research_one():
    from evaluate_segment import auc
    rng = np.random.default_rng(SEED + 5)
    for _ in range(200):
        n = int(rng.integers(2, 3000))
        scores = np.round(rng.normal(size=n), int(rng.integers(0, 3)))  # ties, on purpose
        truth = rng.random(n) < rng.uniform(0.05, 0.95)
        theirs = auc(scores, truth)
        if np.isnan(theirs):
            with pytest.raises(core.Undecidable):
                core.area_under_curve(scores, truth)
            continue
        assert core.area_under_curve(scores, truth) == pytest.approx(theirs, abs=1e-12)


def test_the_holdable_length_returns_the_published_budget():
    m = json.loads((MEASURES / "le_budget_de_la_nappe.json").read_text())
    seen = 0

    def walk(x):
        nonlocal seen
        if isinstance(x, dict):
            if "la_dispersion_en_voxels" in x and "la_longueur_tenable_en_coutures" in x:
                # The published spread is rounded to four decimals: the length recomputed from it falls back to 0.01,
                # not to the bit.
                assert round(core.holdable_length(float(x["le_demi_pli_en_voxels"]), x["la_dispersion_en_voxels"]), 2) \
                    == pytest.approx(x["la_longueur_tenable_en_coutures"], abs=0.011)
                seen += 1
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(m["les_budgets"])
    assert seen >= 4
