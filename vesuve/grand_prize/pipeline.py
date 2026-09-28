"""The Grand Prize pipeline: unroll automatically, and say exactly how far.

The prize's question fits in one line: what replaces the human who corrects the transfer from one winding to
the next? The answer this pipeline executes is that of `244` and `246`: the lattice gives the step of every
seam, the consensus of five neighbouring lines removes each line's own noise, and a loop that closes under the
half sheet cut after cut certifies that its two paths did not change winding.

The stages, in the order of `213` §2 and `244` §5:

    E0 the object       is it eligible, and if not what that costs
    E1 the volume       the presence of the chunks of the surface volume
    E2 the scale        the half sheet
    B  the budget       how far a sheet trace holds: why loops are closed instead of walking
    E4 the lattice      the steps of the bands, published or read here
    E6 the certificate  the hand-free procedure, and the per-chunk mask
    E7 the judge        (option) the material peak of the certified chunks, without ground truth
    T  the transfer     the hand-free correction of the transfer to the next winding, where it was validated
    E8 the ink          the published ink map, under the mask
    E9 the packaging    the mask, the certified surface and its `approval.tif`, and what is not produced
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tifffile

from vesuve import catalogue, embedded, images, tifxyz
from vesuve.core import Undecidable
from vesuve.lattice import certificate as cert
from vesuve.lattice.digest import DigestCache
from vesuve.lattice.reading import BandReader
from vesuve.lattice.segment import certify_segment, extra_readings, published_ink_map_path
from vesuve.remote import Remote, Unavailable
from vesuve.remote_zarr import BUCKET, RemoteArray
from vesuve.report import MET, NOT_MEASURED, NOT_MET, Report
from vesuve.transfer import correction
from vesuve.transport import Transport

TRACED_LAYER = 54      # a surface volume has 109 layers centred on the traced surface
MEASURED_RATE = 19.0   # chunks per second at 16 threads, measured on the smallest published band
CONTROL_BAND = "20260623142658-w028-037"  # where the correction was measured to fail (`281`)
THRESHOLD = 0.05       # the sign test's threshold (`290`)


def _correct(name: str) -> dict:
    k = embedded.correction(name)
    got = correction.correct_segment(k["transfer"], k["judges"], k["tables"], k["candidates"],
                                     k["context"]["slip_voxels"], k["surfaces"])
    return {**got, "context": k["context"]}


def _summary(got: dict) -> dict:
    """What a replay says, without the arrays."""
    return {"pooled": got["pooled"], "pooled_within_validated_geometry": got["pooled_within_validated_geometry"],
            "sign_test": {k: float(f"{v:.3g}") for k, v in got["sign_test"].items()},
            "whole_surface": got["whole_segment"],
            "blocks_within_validated_geometry": sum(1 for b in got["blocks"] if b["validated_geometry"]),
            "undecided": {f"{b['row']}_{b['column']}": b["reason"] for b in got["blocks"] if not b["decidable"]}}


def _certify(s, fresh):
    return certify_segment(s["context"]["segment"], fresh)[1]


def run(segment: str = "20230702185753", output: Path = Path("outputs/grand-prize"), cache: Path = Path("cache"),
        read: bool = False, rounds: int = 6, threads: int = 16, readings=(), judge: int = 0, ink: bool = True,
        surface: bool = True, journal=None) -> Report:
    s = embedded.segment(segment)
    ctx = s["context"]
    r = Report("grand-prize", {"segment": segment, "scroll": ctx["scroll"], "read": read, "rounds": rounds,
                               "threads": threads, "extra_readings": [str(x) for x in readings], "judge": judge},
               journal)
    output = Path(output)
    transport = Transport(journal=journal)
    remote = Remote(cache, transport)

    with r.stage("E0", "the object") as e:
        ok = catalogue.is_eligible("grand-prize", ctx["scroll"])
        e.note(scroll=ctx["scroll"], segment=segment, eligible=ok, eligible_scrolls=[v.scroll for v in catalogue.GRAND_PRIZE])
        if not ok:
            e.partial(f"{ctx['scroll']} is not one of the thirteen prize scrolls: the method is built where the reference "
                      f"exists, and it will have to be carried to a scroll without ground truth (`151` E0)")

    A = s["presence"]
    with r.stage("E1", "the volume") as e:
        e.note(volume=ctx["volume"], grid=list(A.shape), chunks_present=int(A.sum()),
               provenance="the list of the bucket's keys, read back by `ou_sarrete_le_segment.py` (98 pages)")

    with r.stage("E2", "the scale") as e:
        half = e.apply("E2", ctx["step_um"], ctx["voxel_um"], s_um=ctx["step_um"], v_um=ctx["voxel_um"])
        if half != ctx["procedure"]["half"]:
            e.stop(f"the recomputed half sheet ({half}) is not the procedure's ({ctx['procedure']['half']})")

    with r.stage("B", "the budget of a sheet trace") as e:
        b = ctx["budget"]
        holdable = {}
        for family in ("cross", "agree"):
            for name, sigma in b[family].items():
                holdable[f"{family} {name}"] = e.apply("N5", float(half), float(sigma), budget=f"{family} {name}",
                                                       delta=half, sigma=sigma)
        a_ = b["agree"]
        e.apply("N7", a_["198-197"] ** 2, a_["198-199"] ** 2, a_["197-199"] ** 2,
                row=198, var_198_197=a_["198-197"] ** 2, var_198_199=a_["198-199"] ** 2, var_197_199=a_["197-199"] ** 2)
        binding = min(v for k, v in holdable.items() if k.startswith("agree"))
        e.note(binding_holdable_length=round(binding, 2), seams_of_a_row=b["seams_of_a_row"],
               conclusion=(f"a row of {b['seams_of_a_row']} seams exceeds the {binding:.2f} the agreement allows: two "
                           f"rows each walked on its own end on two sheets (`R4-F341`). Hence the certificate: close "
                           f"loops rather than walk."))

    fresh = extra_readings(readings)
    with r.stage("E4", "the lattice: the published bands", "B4") as e:
        e.note(published_bands=len(s["bands"]), given_bands=len(fresh))
        try:
            res = _certify(s, fresh)
        except cert.ReadingRefused as x:
            e.stop(f"an extra band does not fall back on what is published: {x}")
    if r.stopped:
        r.write(output)
        return r
    with r.stage("E4L", "the lattice: reading what the procedure asks for", "B4") as e:
        chunks_read, done_rounds = 0, 0
        if read and res["requests"]:
            array = RemoteArray(f"{BUCKET}/{ctx['volume']}", transport)
            reader = BandReader(array, DigestCache(Path(cache) / "digests", array.url), threads, journal, segment)
            for done_rounds in range(1, rounds + 1):
                for d in res["requests"]:
                    try:
                        fresh[d["key"]] = reader.read(d)
                    except Undecidable as x:
                        e.partial(f"band {d['key']} could not be read: {x}")
                        break
                (output / "readings").mkdir(parents=True, exist_ok=True)
                (output / "readings" / "bands_read.json").write_text(json.dumps({"bands": fresh}, ensure_ascii=False))
                try:
                    res = _certify(s, fresh)
                except cert.ReadingRefused as x:
                    e.stop(f"a band read here does not fall back on what is published: {x}")
                    break
                if not res["requests"] or e.data["state"] != "done":
                    break
            chunks_read = reader.chunks_read
        e.note(published_bands=len(s["bands"]), fresh_bands=len(fresh), chunks_read_here=chunks_read,
               reading_rounds=done_rounds)
        if not read:
            e.skip("replay: the published bands and those given by --readings; --read reads what the procedure asks for")
    if r.stopped:
        r.write(output)
        return r

    with r.stage("E6", "the certificate", "B4") as e:
        states = {}
        for x in res["journal"]:
            states[x["state"]] = states.get(x["state"], 0) + 1
        e.record("S", ctx["procedure"]["reach"], gap_avoided=30)
        for x in res["journal"]:
            if x.get("closure") is not None:
                e.record("L", x["closure"], loop=x["corners"], width=x["width"], state=x["state"])
                if x.get("peak"):
                    e.record("P", x["peak"]["cumulative_voxels"], loop=x["corners"], at_cut=x["peak"]["cut"], half=half)
            v = (x.get("tie_break") or {}).get("verdict")
            if v and v.get("margins"):
                e.record("M", v["margins"], drifting_line=v["drifting_line"], tightest=v["tightest"])
        e.record("K", res["coverage"]["share"], chunks=res["coverage"]["count"], of=res["coverage"]["of"])
        e.note(rectangle=res["rectangle"], states=states, holding_loops=res["holding_loops"],
               bands_to_read=len(res["requests"]), chunks_to_read=res["left_to_read"],
               estimated_reading_minutes=round(res["left_to_read"] / MEASURED_RATE / 60, 1),
               wings_around_an_unjudged_rectangle=res["wings_around_an_unjudged_rectangle"])
        if res["requests"]:
            e.partial(f"{len(res['requests'])} bands ({res['left_to_read']} chunks) are still to read to judge what the "
                      f"procedure finds; the coverage is that of what is judged. `vesuve grand-prize --read` reads "
                      f"them, about {res['left_to_read'] / MEASURED_RATE / 60:.0f} min at 16 threads")
        if res["wings_around_an_unjudged_rectangle"]:
            e.note(warning=("wings are certified around a rectangle that is not itself judged: they hold on their "
                            "profile, but the rectangle that links them is not proved"))
    mask = res["mask"]

    with r.stage("E7", "the judge without ground truth", "B3") as e:
        if judge <= 0:
            e.skip("requested with --judge N: it reads N certified chunks from the bucket")
        else:
            array = RemoteArray(f"{BUCKET}/{ctx['volume']}", transport)
            reader = BandReader(array, DigestCache(Path(cache) / "digests", array.url), threads, journal, segment)
            ys, xs = np.nonzero(mask == cert.CERTIFIED)
            if not len(ys):
                e.skip("no chunk is certified")
            else:
                picked = np.random.default_rng(20260924).choice(len(ys), size=min(judge, len(ys)), replace=False)
                reader.preload([(int(ys[i]), int(xs[i])) for i in picked])
                gaps, reliefs = [], []
                for i in picked:
                    d = reader.digest(int(ys[i]), int(xs[i]))
                    if d.kept:
                        p = d.depth
                        gaps.append(abs(int(np.argmax(p)) - TRACED_LAYER) * ctx["voxel_um"])
                        reliefs.append(float((p.max() - p.min()) / p.mean()))
                e.note(chunks_judged=len(gaps), median_peak_gap_um=round(float(np.median(gaps)), 2),
                       share_within_half_sheet=round(float(np.mean(np.array(gaps) < half * ctx["voxel_um"])), 4),
                       median_relief=round(float(np.median(reliefs)), 4),
                       rule=("`src/tracecheck/tracecheck.py:204`: the material peak of each chunk must fall on the traced "
                             "layer; a gap beyond the half sheet (36 voxels, 86.4 µm) says the surface left its sheet"))

    transfer = None
    with r.stage("T", "the transfer to the next winding", "B4") as e:
        try:
            got = _correct(segment)
        except FileNotFoundError as x:
            e.skip(f"no correction inputs are embedded for this segment ({x})")
            got = None
        if got is not None:
            kc, p = got["context"], got["pooled"]
            decided = [b for b in got["blocks"] if b["decidable"]]
            e.record("W", 2 * len(decided), surfaces=kc["research_surfaces"], neighbourhoods=len(decided))
            e.record("A", round(float(np.median([abs(b["anchor_voxels"]) for b in decided])), 4) if decided else None,
                     what="median |anchor| over the decided blocks, voxels")
            e.record("X", kc["slip_voxels"], source="`261`, read on the segment without a judge")
            e.record("R", p["corrected_points"], blocks=p["blocks"])
            e.record("G", got["sign_test"]["on_points"], misses_made_right=p["misses_made_right"],
                     rights_made_misses=p["rights_made_misses"])
            e.record("G", got["sign_test"]["on_blocks"], blocks_up=p["blocks_up"], blocks_down=p["blocks_down"])
            output.mkdir(parents=True, exist_ok=True)
            np.save(output / "corrected_transfer.npy", got["claimed"])
            summary = _summary(got)
            try:
                control = _summary(_correct(CONTROL_BAND))
            except FileNotFoundError:
                control = None
            (output / "correction.json").write_text(json.dumps(
                {**summary, "prediction": kc["prediction"], "side": kc["side"], "blocks": got["blocks"],
                 "control_band": {"surface": CONTROL_BAND, **control} if control else None},
                ensure_ascii=False, indent=1))
            transfer = {"segment": summary, "band": control}
            e.note(corrected_transfer="corrected_transfer.npy", details="correction.json",
                   what_the_transfer_is=(f"the distance from each point of the segment's mesh (one point every 8 grid "
                                         f"cells) to the next winding, in voxels along the normal, side {kc['side']}, "
                                         f"transferred by `{kc['prediction']}` (`248`); NaN where there is no point"),
                   blocks=p["blocks"], corrected_points=p["corrected_points"],
                   misses_made_right=p["misses_made_right"], rights_made_misses=p["rights_made_misses"],
                   net_gain=p["net_gain"], share_before=p["before"], share_after=p["after"],
                   sign_test=summary["sign_test"], whole_segment=summary["whole_surface"],
                   blocks_within_validated_geometry=summary["blocks_within_validated_geometry"],
                   control_band=control and {"surface": CONTROL_BAND, "pooled": control["pooled"],
                                             "sign_test": control["sign_test"],
                                             "blocks_within_validated_geometry":
                                                 control["blocks_within_validated_geometry"]},
                   where_the_inputs_come_from=(
                       "the step tables are those of the research's renders (`275`, `281`: two surfaces rendered "
                       "through `vc_render_tifxyz` from about 50 GB of chunks); this program replays the decision on "
                       "them and does not render them"))
            if summary["undecided"]:
                e.partial(f"{len(summary['undecided'])} blocks are left undecided")

    with r.stage("E8", "the ink, the measuring rule", "B3") as e:
        if not ink:
            e.skip("disabled by --no-ink")
        else:
            path = published_ink_map_path(ctx)
            try:
                ink_map = images.read_image(remote.fetch(path))
                output.mkdir(parents=True, exist_ok=True)
                view = images.overlay(ink_map, mask)
                view = images.draw_loops(view, res["journal"], ink_map.shape[0] / mask.shape[0], 6)
                view.thumbnail((1600, 1600))  # the full map is the published product; the view is for reading
                view.save(output / "ink_under_mask.jpg", quality=88)
                e.note(ink_map=path, its_shape=list(ink_map.shape), image="ink_under_mask.jpg",
                       reading=("the PUBLISHED ink map (the team's model, 2.4 µm), under the mask: the ink is the "
                                "measuring rule that says whether the unrolling makes sense, not the work itself"))
            except Unavailable as x:
                e.skip(f"the ink map could not be obtained: {x}")

    with r.stage("E9", "the packaging") as e:
        output.mkdir(parents=True, exist_ok=True)
        tifffile.imwrite(output / "chunk_mask.tif", mask)
        images.draw_loops(images.mask_in_colours(mask), res["journal"], 2, 1).save(output / "chunk_mask.png")
        (output / "certificate.json").write_text(json.dumps(
            {k: res[k] for k in ("rectangle", "journal", "holding_loops", "coverage", "left_to_read")},
            ensure_ascii=False, indent=1))
        (output / "bands_to_read.json").write_text(json.dumps(res["requests"], ensure_ascii=False, indent=1))
        products = ["chunk_mask.tif", "chunk_mask.png", "certificate.json", "bands_to_read.json"]
        if transfer is not None:
            products += ["corrected_transfer.npy", "correction.json"]
        if surface:
            path = f"{ctx['scroll']}/segments/{segment}/mesh/{segment}-on-20260411134726-2.4um.tifxyz"
            try:
                sf = tifxyz.read(remote.tifxyz_folder(path))
                scale = float(sf.meta["scale"][0])
                grid = tifxyz.chunk_mask_to_grid(mask, sf.shape, 128, scale)
                certified = (grid == cert.CERTIFIED) & sf.valid()
                tifxyz.write(tifxyz.restrict(sf, certified), output / f"{segment}_certified.tifxyz",
                             approval=certified.astype(np.uint8))
                products.append(f"{segment}_certified.tifxyz/ (x, y, z, meta.json, approval.tif)")
                e.note(surface=path, its_grid=list(sf.shape), certified_vertices=int(certified.sum()),
                       valid_vertices=int(sf.valid().sum()))
            except Unavailable as x:
                e.partial(f"the surface could not be obtained: {x}")
        e.note(products=products,
               not_produced=("`column_NN.tifxyz`: cutting the surface into text columns requires the ink to be legible "
                             "column by column, and at the regime of the thirteen scrolls the published detector does "
                             "not separate the sheet from the void (`R1-F20`). The deliverable is the certified "
                             "surface, whole, and its mask."))

    share = res["coverage"]["share"]
    r.requirement("one of the thirteen eligible scrolls", NOT_MET if not catalogue.is_eligible("grand-prize", ctx["scroll"])
                  else MET, f"{ctx['scroll']}: the method's reference, outside the list")
    r.requirement("100 % of the recto unrolled", NOT_MET,
                  f"one published segment: {res['coverage']['count']} chunks certified out of {res['coverage']['of']} "
                  f"({share:.2%} of ITS footprint); a segment is not a scroll")
    r.requirement("automated pipeline, at most 8 h of human input", MET,
                  "0 h: the procedure takes every decision without a hand (`R4-F410`); its only input is the presence")
    if transfer is not None:
        seg, band = transfer["segment"], transfer["band"]
        p, st = seg["pooled"], seg["sign_test"]
        holds = p["net_gain"] > 0 and st["on_points"] < THRESHOLD and st["on_blocks"] < THRESHOLD
        r.requirement("the transfer to the next winding corrected without a hand", MET if holds else NOT_MET,
                      f"{p['misses_made_right']} misses made right for {p['rights_made_misses']} rights made misses "
                      f"on {p['blocks']} blocks, a net gain of {p['net_gain']}; sign test p = {st['on_points']} on the "
                      f"points and {st['on_blocks']} on the blocks ({p['blocks_up']} up, {p['blocks_down']} down). "
                      f"The judge only scores (`R4-F456`, `R4-F471`)")
        where = (f"{seg['blocks_within_validated_geometry']} of {p['blocks']} blocks have neighbours along both axes, "
                 f"and only their corrections are written")
        if band:
            bp, bs = band["pooled"], band["sign_test"]
            where += (f". On the band `{CONTROL_BAND}` ({band['blocks_within_validated_geometry']} of {bp['blocks']} "
                      f"blocks within that geometry), the same procedure gives {bp['misses_made_right']} for "
                      f"{bp['rights_made_misses']} (p = {bs['on_points']}), and nothing is claimed there. The "
                      f"geometry is necessary, not sufficient: on a slice of that band twice as tall, 28 blocks with "
                      f"neighbours on all four sides give 7 for 5 (p = 0.774, `295`, `R4-F476`). The correction is "
                      f"validated on this segment, against its judges, and nowhere else yet")
        r.requirement("the correction claimed only where it was validated", MET, where)
    r.requirement("70 % of the characters legible per column", NOT_MEASURED,
                  "no reading; at the prize regime the published ink is flat (`R1-F20`)")
    r.requirement("one mesh per column, `column_NN.tifxyz`", NOT_MET,
                  "the certified surface is returned whole, with `approval.tif`; no cutting into columns")
    r.requirement("Docker image", MET, "`Dockerfile`, which runs this pipeline from the embedded data")
    r.requirement("seeds fixed and reported", MET,
                  f"block null: seed {ctx['procedure']['seed']}, {ctx['procedure']['draws']} draws; judge: seed 20260924")
    r.requirement("integrated in VC3D", NOT_MEASURED, "the surface and `approval.tif` follow the tifxyz contract villa reads")
    transport.close()
    r.write(output)
    return r
