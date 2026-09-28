"""The First Letters pipeline: a 4 cm² area of a scroll where nothing has been read, rendered, inked, and
accompanied by what makes it credible.

The prize: ten letters in 4 cm², a static programmatic image, a 1 cm scale bar, named after its mesh, the rows
annotated, the ink on a render where the fibres show, and evidence that the text is not hallucinated. A human in
the loop is allowed: this pipeline reads NO letter, it renders what an eye will have to read, and it says what its
witnesses are worth.

    F0 the object       eligible? and at which scan regime (Fresnel number)
    F1 the surface      the layer stack and the mesh
    F2 the window       4 cm² chosen on papyrus coverage alone, and a held-out region
    F3 the fibres       the middle layer stretched: the render where the fibres show
    F4 without a model  the maximum projection of the central layers: "ink visible without a model"
    F5 the model        an ink map (given, or inferred with --model)
    F6 the witnesses    the rows against the shuffle, the held-out region, the training overlap
    F7 the packaging    the images named after the mesh, and what is left for a human to do
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from vesuve import catalogue, images
from vesuve.render import layers, rows, windows
from vesuve.render.model import LAYERS, InkUnavailable, infer, ink_stack, load
from vesuve.report import MET, NOT_MEASURED, NOT_MET, PARTIAL, Report

SHUFFLE_SEED = 20260924


def _mesh_name(surface: Path) -> str:
    return Path(surface).name.removesuffix(".tifxyz")


def _ink_as_bytes(ink_map: np.ndarray) -> np.ndarray:
    """Logits into 0..255 by the sigmoid, 0 outside what is seen (NaN)."""
    p = 1.0 / (1.0 + np.exp(-np.nan_to_num(ink_map, nan=-50.0)))
    return np.where(np.isfinite(ink_map), np.clip(p * 254 + 1, 1, 255), 0).astype(np.uint8)


def _overlay_ink(fibres: np.ndarray, ink: np.ndarray, trace: np.ndarray | None) -> Image.Image:
    base = np.stack([fibres] * 3, axis=-1).astype(np.float32)
    a = (ink.astype(np.float32) / 255.0)[..., None]
    red = np.array([255.0, 70.0, 40.0])
    out = base * (1 - 0.65 * a) + red * 0.65 * a
    if trace is not None:
        out[trace] = [80, 200, 255]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def _row_witness(ink: np.ndarray, papyrus: np.ndarray) -> dict:
    b = rows.binarise_ink(ink, papyrus & (ink > 0))
    m = papyrus & (ink > 0)
    real = rows.line_spacing(b, m)
    shuffled = rows.line_spacing(rows.shuffle(b, m, SHUFFLE_SEED), m)
    return {"real": real, "shuffled": shuffled, "binary": b, "mask": m}


def run(layers_folder: Path, surface: Path, scroll: str, output: Path = Path("outputs/first-letters"),
        side_mm: float = 20.0, model: Path | None = None, ink_map: Path | None = None,
        labels: Path | None = None, journal=None) -> Report:
    output, name = Path(output), _mesh_name(surface)
    r = Report("first-letters", {"layers": str(layers_folder), "surface": str(surface), "scroll": scroll,
                                 "side_mm": side_mm, "model": str(model) if model else None,
                                 "ink_map": str(ink_map) if ink_map else None}, journal)
    v = catalogue.volume_of("first-letters", scroll)

    with r.stage("F0", "the object and its regime") as e:
        if v is None:
            e.stop(f"{scroll} is not one of the 23 First Letters scrolls")
        else:
            f = e.apply("F31", v.pixel_um, v.distance_m, v.energy_kev, pixel_um=v.pixel_um,
                        distance_m=v.distance_m, energy_kev=v.energy_kev)
            p = catalogue.PRODUCTION
            fp = e.apply("F31", p.pixel_um, p.distance_m, p.energy_kev, regime="production",
                         pixel_um=p.pixel_um, distance_m=p.distance_m, energy_kev=p.energy_kev)
            e.note(volume=v.volume, ratio_to_production_regime=round(f / fp, 3),
                   consequence=("a survey scan: the published ink models were trained at the production regime, and at "
                                "the prize regime their agreement with the published map is flat (`R1-F20`). Their "
                                "output here is a view, not evidence."))
    if r.stopped:
        r.write(output)
        return r

    with r.stage("F1", "the surface") as e:
        fs = layers.layer_files(layers_folder)
        middle = len(fs) // 2
        a = layers.layer(fs[middle])
        papyrus = layers.papyrus(a)
        e.note(layers=len(fs), middle_layer=middle, shape=list(a.shape), dtype=str(a.dtype),
               papyrus_share=round(float(papyrus.mean()), 4), mesh=name, mesh_exists=(Path(surface) / "x.tif").exists())

    side = int(round(side_mm * 1000.0 / v.pixel_um))
    with r.stage("F2", "the 4 cm² window") as e:
        w = windows.best_window(papyrus, side)
        if w is None:
            side = (min(papyrus.shape) // 16) * 16
            w = windows.best_window(papyrus, side)
            e.partial(f"the surface does not carry {side_mm} mm in one piece: the largest square window is "
                      f"{side * v.pixel_um / 1000:.1f} mm wide ({(side * v.pixel_um / 1e4) ** 2:.2f} cm²)")
        held_out = windows.held_out_window(papyrus, side, w)
        e.note(side_px=side, side_mm=round(side * v.pixel_um / 1000, 2), window=w, held_out_window=held_out,
               rule=("chosen on papyrus coverage ALONE, never on the ink: a window elected where the ink looks strong "
                     "would make letters out of any noise"))

    def _within(we):
        return (we["r0"], we["c0"], we["side"], we["side"])

    with r.stage("F3", "the render where the fibres show") as e:
        layer_w = layers.layer(fs[middle], _within(w))
        fibres = np.asarray(images.grey_levels(layer_w))
        output.mkdir(parents=True, exist_ok=True)
        images.scale_bar(Image.fromarray(fibres), v.pixel_um).save(output / f"{name}_fibres.png")
        e.note(image=f"{name}_fibres.png", rule="the middle layer stretched between 1 and 99 % (`couche_de_rendu.py:35`)")

    with r.stage("F4", "the ink without a model") as e:
        central = list(range(max(0, middle - 3), min(len(fs), middle + 4)))
        proj = layers.maximum_projection(layers.stack(layers_folder, _within(w), central))
        images.scale_bar(images.grey_levels(proj), v.pixel_um).save(output / f"{name}_without_model.png")
        e.note(image=f"{name}_without_model.png", layers=central,
               rule=("\"sometimes ink is visible directly in the flattened render, with no model at all — usually "
                     "bright areas\": the maximum projection of the seven central layers. A view, not a detector."))

    ink_w = ink_h = None
    with r.stage("F5", "the model's ink", "B3") as e:
        try:
            if ink_map is not None:
                c = np.load(ink_map, mmap_mode="r")
                if c.shape != papyrus.shape:
                    raise InkUnavailable(f"the map {c.shape} does not have the shape of the stack {papyrus.shape}")
                cw = np.asarray(c[w["r0"]:w["r0"] + side, w["c0"]:w["c0"] + side])
                ch = (np.asarray(c[held_out["r0"]:held_out["r0"] + held_out["side"],
                                   held_out["c0"]:held_out["c0"] + held_out["side"]]) if held_out else None)
                e.note(ink_map=str(ink_map), provenance="a map inferred elsewhere, given with --ink-map")
            elif model is not None:
                m = load(model)
                start = max(0, (len(fs) - LAYERS) // 2)
                cw, n = infer(ink_stack(layers_folder, start, _within(w)), m)
                ch = infer(ink_stack(layers_folder, start, _within(held_out)), m)[0] if held_out else None
                e.note(model=str(model), windows_swept=n, layers=[start, start + LAYERS - 1])
            else:
                raise InkUnavailable("neither --ink-map nor --model: the model's ink is not computed")
            ink_w, ink_h = _ink_as_bytes(cw), (_ink_as_bytes(ch) if ch is not None else None)
            e.note(share_seen=round(float(np.isfinite(cw).mean()), 4),
                   share_above_0=round(float((np.nan_to_num(cw, nan=-1) > 0).mean()), 4))
        except InkUnavailable as x:
            e.skip(str(x))

    with r.stage("F6", "the witnesses", "B3") as e:
        if ink_w is None:
            e.skip("without an ink map the rows have nothing to measure; the F3 and F4 renders remain to be looked at")
        else:
            papyrus_w = papyrus[w["r0"]:w["r0"] + side, w["c0"]:w["c0"] + side]
            ink_w = np.where(papyrus_w, ink_w, 0).astype(np.uint8)  # outside the papyrus, the model saw black
            t = _row_witness(ink_w, papyrus_w)
            trace = rows.row_lines(t["binary"], t["mask"], t["real"])
            _overlay_ink(fibres, ink_w, trace if trace.any() else None).save(output / f"{name}_ink.png")
            images.scale_bar(Image.open(output / f"{name}_ink.png"), v.pixel_um).save(output / f"{name}_ink.png")
            witness = {k: t[k] for k in ("real", "shuffled")}
            if ink_h is not None:
                ph = papyrus[held_out["r0"]:held_out["r0"] + held_out["side"],
                             held_out["c0"]:held_out["c0"] + held_out["side"]]
                th = _row_witness(ink_h, ph)
                witness["held_out"] = th["real"]
                witness["held_out_shuffled"] = th["shuffled"]
            e.note(rows=witness, rows_drawn=int(trace.any()), image=f"{name}_ink.png",
                   rule=("`typographie.py`: the ink binarised by Otsu, the density per row autocorrelated, periodic "
                         "when the sharpness exceeds 2√(2 ln k)/√n; the shuffle must lose the period"))
            seen = (sorted(p.name.split("_")[0] for p in Path(labels).glob("*_inklabels.png"))
                    if labels is not None and Path(labels).exists() else None)
            ident = re.findall(r"\d{14}", name)
            e.note(training_overlap=(
                "not checkable here: the list of training labels is not present" if seen is None else
                ("NONE: this segment is not among the %d labelled segments of the 2023 model" % len(seen)
                 if not set(ident) & set(seen) else "⚠ THIS SEGMENT IS IN THE TRAINING SET")))

    with r.stage("F7", "the packaging") as e:
        (output / "windows.json").write_text(json.dumps({"window": w, "held_out_window": held_out,
                                                         "pixel_um": v.pixel_um}, indent=1))
        e.note(products=sorted(p.name for p in output.glob(f"{name}_*.png")) + ["windows.json"],
               left_to_a_human=("reading: count ten letters in the window, and check they hold on the held-out region. "
                                "The pipeline says where to look and what its witnesses are worth; it does not read."))

    witness = r.data["stages"][-2]["outputs"].get("rows") or {}
    real, shuffled = witness.get("real") or {}, witness.get("shuffled") or {}
    r.requirement("one of the 23 eligible scrolls", MET, f"{scroll}, volume {v.volume}")
    r.requirement("ten letters in 4 cm²", NOT_MEASURED, "no letter is read by this pipeline: that is the work of an eye")
    r.requirement("a static programmatic image, named after its mesh", MET, f"{name}_ink.png, {name}_fibres.png")
    r.requirement("a 1 cm scale bar", MET, f"10 mm = {int(round(10000 / v.pixel_um))} px at {v.pixel_um} µm")
    r.requirement("rows annotated", MET if real.get("periodic") else NOT_MET,
                  ("without an ink map" if not real else
                   "no inner autocorrelation peak, at any angle within ±12°: no rows in the model's ink"
                   if real.get("period_px") is None else
                   f"line spacing {real['period_px']} px, sharpness {real['sharpness']:.3f} against a floor "
                   f"{real['floor']:.3f}"))
    r.requirement("ink on a render where the fibres show", MET if ink_w is not None else NOT_MET, f"{name}_ink.png")
    r.requirement("show the text is not hallucinated",
                  PARTIAL if real.get("periodic") and not shuffled.get("periodic") else NOT_MET,
                  "the shuffle of the same pixels loses the line spacing; the held-out region is measured separately; "
                  "no ground truth on this scroll")
    r.write(output)
    return r
