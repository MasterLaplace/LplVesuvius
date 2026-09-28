"""The audit of a published segment, for the Progress Prizes: where did an existing trace change winding?

The judges say what they pay for: "detecting failure-cases of existing methods on real scroll data". The same
certificate as the Grand Prize, read the other way round: a consensus loop whose profile CROSSES the half sheet
says its two paths no longer arrive on the same winding, and the third line of `236` names the line that drifts.
On segment `20230702185753`, traced and published, it is column 260 (`R4-F401`).

⚠ What the audit does not say, and it says so: it does not tell a misread column from material that moves away
(`R4-F406`, `R4-F407`). It names a region to look at, it does not condemn it.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tifffile

from vesuve import images
from vesuve.lattice import certificate as cert
from vesuve.lattice.segment import certify_segment, extra_readings, published_ink_map_path
from vesuve.remote import Remote, Unavailable
from vesuve.report import MET, NOT_MET, Report
from vesuve.transport import Transport

SUSPECT = 3


def failure_cases(res: dict, half: float) -> list[dict]:
    """Each loop that crosses: where its cumulative closure passes the half sheet, and which line drifts."""
    cases = []
    for e in res["journal"]:
        if e["state"] != "crosses":
            continue
        prof = e.get("profile") or []
        beyond = [p["cut"] for p in prof if abs(p["cumulative_voxels"]) >= half]
        tb = e.get("tie_break") or {}
        v = tb.get("verdict") or {}
        cases.append({"loop": e["corners"], "side": e.get("side"), "width": e["width"],
                      "closure_voxels": e.get("closure"), "peak": e.get("peak"),
                      "cuts_beyond_half_sheet": beyond, "tie_break": tb.get("state"),
                      "third_line": (tb.get("third_line") or {}).get("line"),
                      "drifting_line": v.get("drifting_line"), "margins": v.get("margins")})
    return cases


def audit_mask(res: dict, cases: list[dict]) -> np.ndarray:
    """The certificate's mask, plus the chunks of the drifting band, along its loop."""
    m = res["mask"].copy()
    for c in cases:
        x, k = c["drifting_line"], c["width"]
        if x is None:
            continue
        r0, r1, c0, c1 = c["loop"]
        h = k // 2
        if c["side"] in ("right", "left"):
            zone = (slice(r0, r1 + 1), slice(max(0, x - h), x + h + 1))
        else:
            zone = (slice(max(0, x - h), x + h + 1), slice(c0, c1 + 1))
        sub = m[zone]
        sub[sub == cert.PRESENT] = SUSPECT
    return m


def run(segment: str = "20230702185753", output: Path = Path("outputs/progress"), cache: Path = Path("cache"),
        readings=(), judge: int = 0, journal=None) -> Report:
    output = Path(output)
    r = Report("progress", {"segment": segment, "extra_readings": [str(x) for x in readings]}, journal)
    fresh = extra_readings(readings)
    with r.stage("P0", "the audited segment") as e:
        s, res = certify_segment(segment, fresh)
        ctx = s["context"]
        e.note(scroll=ctx["scroll"], segment=segment, volume=ctx["volume"],
               nature="a published segment, traced by others: the audit judges an existing method")
    half = float(ctx["procedure"]["half"])

    with r.stage("P1", "the certificate, read the other way round", "B4") as e:
        cases = failure_cases(res, half)
        for c in cases:
            e.record("P", (c["peak"] or {}).get("cumulative_voxels"), loop=c["loop"],
                     at_cut=(c["peak"] or {}).get("cut"), half=half)
            if c["margins"]:
                e.record("M", c["margins"], drifting_line=c["drifting_line"])
        e.note(loops_judged=sum(1 for x in res["journal"] if x.get("closure") is not None), loops_that_cross=len(cases))

    with r.stage("P2", "the failure cases") as e:
        m = audit_mask(res, cases)
        output.mkdir(parents=True, exist_ok=True)
        (output / "failure_cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=1))
        tifffile.imwrite(output / "audit_mask.tif", m)
        images.draw_loops(images.mask_in_colours(m), [x for x in res["journal"] if x["state"] in ("crosses", "under")],
                          2, 1).save(output / "audit_mask.png")
        sentences = []
        for c in cases:
            if c["drifting_line"] is not None:
                direction = "column" if c["side"] in ("right", "left") else "row"
                bounds = c["loop"][:2] if direction == "column" else c["loop"][2:]
                sentences.append(f"{direction} {c['drifting_line']}, lines {bounds[0]} to {bounds[1]}: the cumulative "
                                 f"closure crosses the half sheet at cuts {c['cuts_beyond_half_sheet']} (peak "
                                 f"{c['peak']['cumulative_voxels']} voxels at cut {c['peak']['cut']})")
        e.note(suspect_chunks=int((m == SUSPECT).sum()), cases=sentences,
               limit=("the audit does not tell a misread column from material that moves away (`R4-F406`): it names "
                      "where to look"))
        if not cases:
            e.partial("no judged loop crosses: nothing is named on what is read")

    with r.stage("P3", "the suspect region, on the published ink", "B3") as e:
        try:
            ink_map = images.read_image(Remote(cache, Transport(journal=journal)).fetch(published_ink_map_path(ctx)))
            view = images.overlay(ink_map, m, alpha=0.5)
            view = images.draw_loops(view, [x for x in res["journal"] if x["state"] == "crosses"],
                                     ink_map.shape[0] / m.shape[0], 6)
            view.thumbnail((1600, 1600))
            view.save(output / "ink_and_suspect_region.jpg", quality=88)
            e.note(image="ink_and_suspect_region.jpg")
        except Unavailable as x:
            e.skip(f"the ink map could not be obtained: {x}")

    r.requirement("detect a failure case of an existing method on real data", MET if cases else NOT_MET,
                  "; ".join(e for e in r.data["stages"][2]["outputs"].get("cases", [])) or "no case named")
    r.requirement("reproducible and documented", MET, "replayed from the embedded data, with no network and no free seed")
    r.requirement("bound what is claimed", MET, "a region to look at, not a condemnation (`R4-F406`)")
    r.write(output)
    return r
