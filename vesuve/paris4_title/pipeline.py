"""The title of PHerc. Paris 4: look where the text ends, that is, at the core of the scroll.

The prize: "The expected title region has shown no detectable ink so far — possibly a different ink, and the top
rows are physically missing". The research never aimed at the title; it has, on the other hand, the most
instrumented object of all (120 published windings, the curved axis measured). This pipeline does not read: it says
WHERE to look, with a rule written before looking.

The rule, REPORTED and not measured here (`docs/archive/06_mesures_a_faire.md:10-15` on the `experimental` branch,
quoting the Bodleian): the beginning of the text is on the outside, the end and the title (the colophon) at the core.

    T0 the rule            where a title sits on a Herculaneum scroll
    T1 the band            the innermost of the published bands, and its revisions
    T2 the direction       which end of the unrolled band is at the core: the radius to the curved axis
    T3 the registration    the orientation of the ink map against the mesh, by their silhouettes
    T4 the end of the text the ink profile along the winding: where the last column stops
    T5 the witness         do two revisions of the same band agree on that end?
    T6 the candidates      the views of the last column and of what follows it, for an eye to read
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw

from vesuve import images
from vesuve.render.rows import binarise_ink
from vesuve.report import MET, NOT_MEASURED, NOT_MET, PARTIAL, Report

PIXEL_UM = 2.4 * 8  # the map reduced 8× of a 2.4 µm surface volume
AXIS = Path(__file__).resolve().parents[1] / "data" / "paris4" / "axis.json"
A_BAND = re.compile(r"(\d{14})-w(\d{3})-(\d{3})\.jpg$")


def bands(ink_maps: Path) -> list[dict]:
    """The maps of the bands numbered `wNNN-MMM` (NNN, MMM: the winding ranks, increasing outwards)."""
    out = []
    for p in sorted(Path(ink_maps).glob("*.jpg")):
        m = A_BAND.search(p.name)
        if m:
            out.append({"segment": m.group(1), "start": int(m.group(2)), "end": int(m.group(3)), "ink_map": p})
    return out


def radius_per_column(mesh: Path, axis: dict) -> np.ndarray:
    """The median distance of each column of the mesh to the curved axis, in mm."""
    x, y, z = (tifffile.imread(Path(mesh) / f"{c}.tif").astype(np.float64) for c in "xyz")
    ok = (x > 0) & (y > 0) & (z > 0)
    v = float(axis["voxel_um"]) / 1000.0
    t = axis["trace"]
    cx = np.interp(z * v, t["z_mm"], t["cx_mm"])
    cy = np.interp(z * v, t["z_mm"], t["cy_mm"])
    r = np.hypot(x * v - cx, y * v - cy)
    r[~ok] = np.nan
    return np.nanmedian(r, axis=0)


def orientation(ink_map: np.ndarray, mesh: Path) -> tuple[str, float]:
    """Which of the four orientations (identity, mirrors) best overlays the map's silhouette on the mesh's: an
    orientation measured, never assumed."""
    x = tifffile.imread(Path(mesh) / "x.tif")
    s = (x > 0).astype(np.float32)
    c = np.asarray(Image.fromarray((ink_map > 0).astype(np.uint8) * 255).resize((s.shape[1], s.shape[0]),
                                                                                 Image.BILINEAR), dtype=np.float32) / 255
    shapes = {"identity": c, "horizontal_mirror": c[:, ::-1], "vertical_mirror": c[::-1, :], "half_turn": c[::-1, ::-1]}
    if float(s.std()) == 0.0 or float(c.std()) == 0.0:
        return "identity", float("nan")  # a full silhouette says nothing about the orientation
    scores = {k: float(np.corrcoef(s.ravel(), v.ravel())[0, 1]) for k, v in shapes.items()}
    k = max(scores, key=scores.get)
    return k, scores[k]


def described_cells(ink_map: np.ndarray, columns: int = 449, slices: int = 16) -> np.ndarray:
    """(slices, columns): the ink share of each cell, NaN where there is hardly any papyrus."""
    papyrus = ink_map > 0
    ink = binarise_ink(ink_map, papyrus)
    bc = np.linspace(0, ink_map.shape[1], columns + 1).astype(int)
    br = np.linspace(0, ink_map.shape[0], slices + 1).astype(int)
    out = np.full((slices, columns), np.nan)
    for i in range(slices):
        for j in range(columns):
            p = papyrus[br[i]:br[i + 1], bc[j]:bc[j + 1]].sum()
            if p > 0.5 * (br[i + 1] - br[i]) * (bc[j + 1] - bc[j]):
                out[i, j] = ink[br[i]:br[i + 1], bc[j]:bc[j + 1]].sum() / p
    return out


def cell_threshold(cells: np.ndarray) -> float:
    """Written or empty: Otsu's threshold on the ink shares of all the cells, with no parameter.

    ⚠ The first version took the middle between two percentiles of a profile averaged over the height: the last
    column of a book is SHORT (five lines at the top on `w010-027`), its mean stayed under the threshold, and the
    second-to-last column passed for the last. The image showed it.
    """
    v = cells[np.isfinite(cells)]
    as_bytes = np.clip(np.round(v / max(v.max(), 1e-9) * 254) + 1, 1, 255).astype(np.uint8)
    b = binarise_ink(as_bytes, np.ones_like(as_bytes, dtype=bool))
    return float(v[~b].max() if (~b).any() else v.max())


def end_of_the_text(cells: np.ndarray, core_end: str) -> dict:
    """From the core, the first run of at least 2 % of the band in which each slice carries a written cell: the last
    column. Its last line is the lowest of its written cells."""
    threshold = cell_threshold(cells)
    written = np.nan_to_num(cells, nan=0.0) > threshold
    n = cells.shape[1]
    order = np.arange(n) if core_end == "start" else np.arange(n)[::-1]
    min_run = max(3, int(0.02 * n))
    run_, first = 0, None
    for rank, j in enumerate(order):
        run_ = run_ + 1 if written[:, j].any() else 0
        if run_ >= min_run:
            first = rank - run_ + 1
            break
    if first is None:
        return {"threshold": round(threshold, 4), "last_column": None, "band_share_after_the_text": None}
    # The column extends outwards ON THE SLICES OF ITS OWN LINES ONLY, across gaps shorter than the minimal run: a
    # space between two words empties a slice, a gap between columns more than that.
    # ⚠ On all slices, the bottom lines overflowing from one column to the next welded the whole band together.
    its_own = np.flatnonzero(written[:, order[first:first + min_run]].any(axis=1))
    k, gap = first, 0
    while k + gap + 1 < n:
        if written[its_own, order[k + gap + 1]].any():
            k, gap = k + gap + 1, 0
        elif gap + 1 < min_run:
            gap += 1
        else:
            break
    j0, j1 = sorted((int(order[first]), int(order[k])))
    # Its lines are those of its core-side edge: the written height of the LAST column, not that of a neighbouring
    # overflow or of a grain at the papyrus's edge.
    return {"threshold": round(threshold, 4), "last_column": [j0, j1],
            "written_slices": [int(its_own.min()), int(its_own.max())] if its_own.size else None,
            "band_share_after_the_text": round(first / n, 4)}


def run(ink_maps: Path, output: Path = Path("outputs/paris4-title"), cache: Path = Path("cache"),
        meshes: Path | None = None, journal=None) -> Report:
    output = Path(output)
    r = Report("paris4-title", {"ink_maps": str(ink_maps), "meshes": str(meshes) if meshes else None}, journal)
    axis = json.loads(AXIS.read_text())

    with r.stage("T0", "the rule") as e:
        e.note(rule=("the beginning of the text is on the outside of the scroll, the end and the title (the colophon) at "
                     "the core: \"the end of the papyrus (the innermost part of the carbonised scroll) where the "
                     "colophon with the title of the work may be preserved\""),
               status="reported (`docs/archive/06_mesures_a_faire.md:10-15`, Bodleian), not measured here",
               what_the_prize_says=("no ink detected so far in the expected region; possibly a different ink; the top "
                                    "rows physically missing"))

    with r.stage("T1", "the innermost band") as e:
        found = bands(ink_maps)
        if not found:
            e.stop(f"no `wNNN-MMM` band map under {ink_maps}")
        else:
            d0 = min(b["start"] for b in found)
            revisions = [b for b in found if b["start"] == d0]
            e.note(bands_seen=len(found), innermost=f"w{d0:03d}-{revisions[0]['end']:03d}",
                   its_revisions=[b["segment"] for b in revisions],
                   missing=f"windings w000 to w{d0 - 1:03d} are in no published band: the core itself is not traced")
    if r.stopped:
        r.write(output)
        return r

    ends = []
    for rev in revisions:
        seg = rev["segment"]
        mesh = Path(meshes) / seg if meshes else None
        ink_map = images.read_image(Path(rev["ink_map"]).read_bytes())
        with r.stage(f"T2·{seg}", "the direction of the winding") as e:
            if mesh is None or not (mesh / "x.tif").exists():
                e.skip(f"the mesh of {seg} is not given (--meshes): the core end stays unknown")
                core_end = None
            else:
                radii = radius_per_column(mesh, axis)
                n = len(radii)
                at_start, at_end = float(np.nanmedian(radii[: n // 10])), float(np.nanmedian(radii[-n // 10:]))
                orient, score = orientation(ink_map, mesh)
                mesh_core_end = "start" if at_start < at_end else "end"
                mirrored = orient in ("horizontal_mirror", "half_turn")
                core_end = ({"start": "end", "end": "start"}[mesh_core_end] if mirrored else mesh_core_end)
                if not score == score:  # NaN: the silhouette measures nothing
                    e.partial("the mesh's silhouette is full: the orientation is not measurable, identity is assumed")
                elif score < 0.5:
                    e.partial(f"the map's silhouette only correlates at {score:.2f} with the mesh's: the orientation "
                              f"kept is not established")
                e.note(radius_at_start_mm=round(at_start, 2), radius_at_end_mm=round(at_end, 2),
                       ink_map_orientation=orient, its_correlation=round(score, 3),
                       core_is_on_the=("left" if core_end == "start" else "right") + " of the map")
        with r.stage(f"T4·{seg}", "the end of the text") as e:
            if core_end is None:
                e.skip("without the direction of the winding, \"the end\" has no side")
                continue
            cells = described_cells(ink_map)
            f = end_of_the_text(cells, core_end)
            ends.append({"segment": seg, **f, "core_end": core_end, "width": ink_map.shape[1],
                         "height": ink_map.shape[0], "ink_map": ink_map, "cells": cells.shape})
            e.note(**f, rule=("16 slices × 449 cells along the winding, written or empty by Otsu's threshold on all the "
                              "cells: no parameter chosen"))

    with r.stage("T5", "the witness: two revisions of the same band", "B3") as e:
        shares = [f["band_share_after_the_text"] for f in ends if f["band_share_after_the_text"] is not None]
        if len(shares) < 2:
            e.skip("two judged revisions are needed to compare them")
        else:
            e.note(shares_after_the_text=shares, their_gap=round(abs(shares[0] - shares[1]), 4),
                   reading=("two independent meshes of the same band: if they put the end of the text at the same place "
                            "on the winding, the end is not an artefact of one mesh"))

    with r.stage("T6", "the candidates") as e:
        output.mkdir(parents=True, exist_ok=True)
        products, places = [], []
        for f in ends:
            if f["last_column"] is None:
                continue
            c, w, h = f["ink_map"], f["width"], f["height"]
            nt, nc = f["cells"]
            c0, c1 = int(f["last_column"][0] * w / nc), int((f["last_column"][1] + 1) * w / nc)
            last = min(h - 1, int((f["written_slices"][1] + 1) * h / nt))
            margin = (c1 - c0) // 2
            towards_core = f["core_end"] != "start"
            z0, z1 = (max(0, c0 - margin // 2), min(w, c1 + 2 * margin)) if towards_core else \
                (max(0, c0 - 2 * margin), min(w, c1 + margin // 2))
            seg = f["segment"]
            images.scale_bar(images.grey_levels(c[:, z0:z1]), PIXEL_UM, 5.0).save(output / f"{seg}_last_column.png")
            images.scale_bar(images.grey_levels(c[max(0, last - h // 16):, z0:z1]), PIXEL_UM, 5.0).save(
                output / f"{seg}_below_the_last_line.png")
            preview = images.grey_levels(c)
            preview.thumbnail((2400, 2400))
            k = preview.width / w
            p2 = preview.convert("RGB")
            d = ImageDraw.Draw(p2)
            d.rectangle([c0 * k, 0, c1 * k, p2.height - 1], outline=(230, 120, 60), width=4)
            d.rectangle([z0 * k, min(last * k, p2.height - 2), z1 * k, p2.height - 1], outline=(80, 200, 255), width=4)
            p2.save(output / f"{seg}_whole_band.jpg", quality=85)
            products += [f"{seg}_last_column.png", f"{seg}_below_the_last_line.png", f"{seg}_whole_band.jpg"]
            places.append({"segment": seg, "last_column_px": [c0, c1], "its_last_line_px": last,
                           "its_written_height": round(last / h, 3),
                           "candidate_region_px": {"columns": [z0, z1], "rows": [last, h]}})
        (output / "candidates.json").write_text(json.dumps(places, indent=1))
        e.note(places=places, products=products + ["candidates.json"],
               reading=("when the last column is SHORT and nothing follows it towards the core, that is the shape of the "
                        "end of a book: the final title is to be looked for under its last line and in the space that "
                        "follows it. In orange the column, in blue the region"),
               left_to_do=("read, and look for ANOTHER ink: the prize says the expected region showed no detectable ink; "
                           "these views are those of the published model, and the ink-3d product or the 1.129 µm map "
                           "are the next ones to look at"))

    r.requirement("an image papyrologists can read", NOT_MEASURED,
                  "views of the end of the text on the innermost band, at 19.2 µm per pixel; nobody has read them")
    r.requirement("any volume of Scroll 1, 2.4 µm included", MET, "the published ink maps on the 2.4 µm volume")
    r.requirement("validation on a held-out region", PARTIAL,
                  "two independent revisions of the same band compared (T5); no ground truth")
    r.requirement("the core of the scroll", NOT_MET, "windings w000 to w009 are in no published band")
    r.write(output)
    return r
