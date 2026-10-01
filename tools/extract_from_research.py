"""Extract from the research branch what the program embeds for a segment, and nothing else.

The Grand Prize pipeline must run without the research tree (in the Docker image, for instance). What it needs
from the research is PUBLISHED in `docs/mesures/` of the `experimental` branch: the presence of the chunks,
the 112 bands read, the sources that check a fresh reading, the procedure's context, the budget and the hand
coverage. This script reads them back through the research's own readers, translates them through
`vesuve.research`, and writes them under `vesuve/data/segments/<segment>/`, deterministically (sorted keys,
gzip without a date), so that a test can require the embedded data to equal a fresh extraction.

    VESUVE_RESEARCH=<working copy of the experimental branch> uv run --extra tests python tools/extract_from_research.py
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from vesuve.research import KEYS, to_english  # noqa: E402

SEGMENT = "20230702185753"
OUTPUT = HERE / "vesuve" / "data" / "segments" / SEGMENT


def _prepare(research: Path) -> None:
    for family in sorted((research / "src").iterdir()):
        if family.is_dir() and str(family) not in sys.path:
            sys.path.insert(0, str(family))


def _write(path: Path, x) -> None:
    raw = json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    if path.suffix == ".gz":
        raw = gzip.compress(raw, compresslevel=9, mtime=0)
    path.write_bytes(raw)


def _source_name(name: str) -> str:
    """A research source is named after its slice and its band, `224 colonnes_213`: the band's direction in English."""
    return name.replace("colonnes", "columns").replace("rangees", "rows")


def _digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract(research: Path, output: Path) -> dict:
    _prepare(research)
    from deux_chemins_arrivent_ils_sur_la_meme_spire import ce_que_223_a_rendu
    from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import ce_que_225_a_publie
    from la_couverture_sans_main import (LES_LECTURES_PUBLIEES, ce_que_243_a_publie, ce_que_245_a_publie,
                                         les_lectures_publiees)
    from le_segment_au_dela_du_rectangle_se_relie_t_il import ce_que_233_a_publie, les_sources_de_234
    from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu
    from ou_sarrete_le_segment import ce_que_232_a_publie
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS
    from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu
    measures = research / "docs" / "mesures"
    output.mkdir(parents=True, exist_ok=True)

    presence = json.loads((measures / "ou_sarrete_le_segment.json").read_text())["la_presence"]
    _write(output / "presence.json.gz", {"grid": presence["la_grille"], "rows": presence["les_rangees"]})

    bands = []
    for b in to_english(les_lectures_publiees()["les_bandes"]):
        bands.append({k: b[k] for k in ("direction", "centre", "lines", "start", "end", "along", "across")}
                     | {"readings": {l_: {"refused": x.get("refused") or {}} for l_, x in (b.get("readings") or {}).items()}})
    _write(output / "published_bands.json.gz", {"bands": bands})

    p219, p223, p224 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu()
    sources = les_sources_de_234(p219, p223, p224, ce_que_232_a_publie(), ce_que_233_a_publie())
    _write(output / "control_sources.json.gz", {
        _source_name(name): {"domain": {f: sorted([list(c) for c in s]) for f, s in S["domaine"].items()},
               "steps": {f: sorted([[r, c, p] for (r, c), p in s.items()]) for f, s in S["pas"].items()}}
        for name, S in sorted(sources.items())})

    p225, p245, p243 = ce_que_225_a_publie(), ce_que_245_a_publie(), ce_que_243_a_publie()
    budget = json.loads((measures / "le_budget_de_la_nappe.json").read_text())["les_budgets"]
    volume = next(l.split("\t")[1] for l in (measures / "volumes_surface_PHercParis4.txt").read_text().splitlines()
                  if l.startswith(f"{SEGMENT}\t") and "/2.4um-" in l)
    commit = subprocess.run(["git", "-C", str(research), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    read_sources = sorted({*LES_LECTURES_PUBLIEES, measures / "ou_sarrete_le_segment.json",
                           measures / "le_budget_de_la_nappe.json", measures / "une_aile_plus_etroite_tient_elle.json",
                           measures / "la_portee_voit_elle_sa_traversee.json"})
    context = {
        "segment": SEGMENT, "scroll": "PHercParis4", "volume": volume,
        "voxel_um": 2.4, "step_um": 173.0, "half_sheet_voxels": int(DEMI_PAS_EN_VOXELS),
        "procedure": {"longest": int(max(p225["les_longueurs_essayees"])), "seed": int(p224["graine"]),
                      "draws": int(p224["tirages"]), "half": float(DEMI_PAS_EN_VOXELS),
                      "reach": int(p245["la_portee_qui_voit"])},
        "budget": {"cross": {KEYS.get(k, k): v["la_dispersion_en_voxels"] for k, v in budget["traverser"].items()},
                   "agree": {k: v["la_dispersion_en_voxels"] for k, v in budget["saccorder"].items()},
                   "seams_of_a_row": 284},
        "hand_coverage": {"loops": [[co, k] for co, k in p243["les_boucles"]],
                          "coverage": to_english(p243["la_couverture"])},
        "provenance": {"research_commit": commit,
                       "files": {str(p.relative_to(research)): _digest(p) for p in read_sources}},
    }
    _write(output / "context.json", context)

    # The curved axis of PHercParis4 (`90`), for the title pipeline: where the core is.
    axis = json.loads((measures / "laxe_est_une_courbe.json").read_text())
    (output.parents[1] / "paris4").mkdir(parents=True, exist_ok=True)
    _write(output.parents[1] / "paris4" / "axis.json",
           {"volume": axis["volume"], "voxel_um": axis["voxel_um"], "trace": axis["trace"],
            "provenance": {"file": "docs/mesures/laxe_est_une_courbe.json",
                           "digest": _digest(measures / "laxe_est_une_courbe.json")}})
    return context


# The hand-free correction reads two surfaces, a reference then the produced winding, in the order `un_bloc` expects.
ROLES = ("reference", "produced")
BAND = "20260623142658-w028-037"


def _write_array(path: Path, a) -> None:
    """A NumPy array as `.npy.gz`, byte for byte the same on every run (np.savez would stamp the date)."""
    import io

    import numpy as np
    buf = io.BytesIO()
    np.save(buf, np.asarray(a), allow_pickle=False)
    path.write_bytes(gzip.compress(buf.getvalue(), compresslevel=9, mtime=0))


def _correction_inputs(research: Path, out: Path, *, tau0, judges: dict, candidates, slip: float, surfaces: tuple,
                       sources: dict, measure: str, corrected: Path, render: dict | None = None) -> dict:
    """Write what the correction reads on one surface: tables, transfer, judges and context."""
    from la_spire_produite_se_lit_elle_dans_le_treillis import LA_PREDICTION, LE_BLOC, LE_COTE, LE_DOSSIER
    out.mkdir(parents=True, exist_ok=True)
    tables, read = {}, []
    for role, french in zip(ROLES, surfaces):
        tables[role] = {}
        for by, bx in sorted(candidates):
            f = LE_DOSSIER / "les_pas" / french / f"bloc_{by}_{bx}.json"
            t = json.loads(f.read_text())
            # The walk reads the mean step of a seam and nothing else (`la_marche_du_bloc`, `x[0]`).
            tables[role][f"{by}_{bx}"] = {d: {seam: x[0] for seam, x in t[d].items()} for d in ("h", "v")}
            read.append(f)
    _write(out / "tables.json.gz", tables)
    _write_array(out / "transfer.npy.gz", tau0)
    for name, a in judges.items():
        _write_array(out / f"judge_{name}.npy.gz", a)
    import numpy as np
    # What the research wrote as the corrected transfer, for the port to be compared with. Not its bytes: the least
    # squares round differently on another processor, so the same decision can land slightly apart there.
    _write_array(out / "research_corrected_transfer.npy.gz", np.load(corrected))
    measures = research / "docs" / "mesures"
    context = {
        "prediction": LA_PREDICTION, "side": LE_COTE.replace("du_cote_", ""), "block": int(LE_BLOC),
        "slip_voxels": float(slip), "candidates": [list(b) for b in sorted(candidates)],
        "judges": list(judges), "research_surfaces": dict(zip(ROLES, surfaces)),
        "published": measure,
        # What making the step tables here reads: the published mesh the two surfaces come from, and the raw scan the
        # piles are rendered from (paths in the public bucket).
        **({"render": render} if render else {}),
        "provenance": {
            "measures": {str(p.relative_to(research)): _digest(p) for p in (
                measures / measure, measures / "la_marche_corrige_t_elle_la_spire_produite.json")},
            "inputs": {k: _digest(f) for k, f in sources.items()},
            "corrected_transfer": _digest(corrected),
            "tables": hashlib.sha256(b"".join(f.read_bytes() for f in read)).hexdigest(),
        },
    }
    _write(out / "context.json", context)
    return context


def extract_correction(research: Path, output: Path) -> dict:
    """What the hand-free correction reads, from the research's UNVERSIONED `data/`: on the segment (`275`, where it
    was validated) and on the band `w028-037` (`281`, where it was not).

    ⚠ These inputs are not in `docs/mesures/`: the step tables come from renders of the surface volume (about 50 GB
    of chunks read through `vc_render_tifxyz`), and the transfer and the judges from the chain of `248`. They are
    embedded so that the correction replays anywhere, and the replay is checked against what `275` and `281`
    PUBLISHED, block by block, which does run everywhere; this extraction itself only runs where the research data
    lives.
    """
    _prepare(research)
    import numpy as np
    from la_procedure_sans_juge_tient_elle_sur_la_bande import (LE_PREMIER_SAUT, LE_PREMIER_SAUT_CORRIGE,
                                                                LES_COUCHES_DE_LA_BANDE, LES_SURFACES_DE_LA_BANDE,
                                                                lire_le_plan)
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import LA_SPIRE_CORRIGEE, le_segment
    from la_spire_produite_se_lit_elle_dans_le_treillis import LA_PREDICTION, LE_COTE, LE_VOLUME_BRUT, LES_JUGES
    from la_spire_voisine_est_elle_a_un_pas import BUCKET, LE_CACHE, la_cle_du_maillage
    from le_voisinage_dit_il_quel_niveau_est_le_bon import LES_SURFACES
    tau0, _err, slip, candidates = le_segment(LE_CACHE)
    judges = {"segment_alone": "le_segment_seul", "segment_and_witnesses": "le_segment_et_ses_temoins"}
    assert tuple(judges.values()) == tuple(LES_JUGES), "the research changed its judges"
    files = {name: LE_CACHE / f"verite_{SEGMENT}_{french}_{LE_COTE}.npy" for name, french in judges.items()}
    transfer = LE_CACHE / f"transfert_suivante_{SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy"
    segment = _correction_inputs(
        research, output / "correction", tau0=tau0, judges={k: np.load(f) for k, f in files.items()},
        candidates=candidates, slip=slip, surfaces=tuple(LES_SURFACES), sources={"transfer": transfer, **files},
        measure="la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json", corrected=LA_SPIRE_CORRIGEE,
        render={"mesh": la_cle_du_maillage(SEGMENT), "raw_volume": LE_VOLUME_BRUT.removeprefix(f"{BUCKET}/"),
                "mesh_step": 8, "layers": 109})
    layers = np.load(LES_COUCHES_DE_LA_BANDE)
    _correction_inputs(
        research, output.parent / BAND / "correction", tau0=np.load(LE_PREMIER_SAUT),
        judges={"band_layers": layers[..., 0]}, candidates=lire_le_plan()["candidats"], slip=slip,
        surfaces=tuple(LES_SURFACES_DE_LA_BANDE),
        sources={"transfer": LE_PREMIER_SAUT, "band_layers": LES_COUCHES_DE_LA_BANDE},
        measure="la_procedure_sans_juge_tient_elle_sur_la_bande.json", corrected=LE_PREMIER_SAUT_CORRIGE)
    return segment


def _write_rays(out: Path, *, prediction: str, path: str, level: int, factor: int, side: float, t, seen, gi, gj,
                shape: tuple, research_transfer: Path) -> dict:
    """Write what the transfer to the next winding is computed from on one surface: the samples of the prediction
    along each ray, packed one bit per sample, and where each ray sits on the transfer's grid."""
    import numpy as np
    out.mkdir(parents=True, exist_ok=True)
    seen = np.asarray(seen, dtype=bool)
    _write_array(out / "rays_seen.npy.gz", np.packbits(seen, axis=1))
    _write_array(out / "rays_grid.npy.gz", np.stack([np.asarray(gi), np.asarray(gj)]).astype(np.int32))
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS as half_sheet_voxels
    from que_montrent_ces_deux_vues import PAS_EN_VOXELS as step_voxels
    context = {"prediction": prediction, "path": path, "level": int(level), "factor": int(factor),
               "side": "plus" if side > 0 else "minus", "samples": int(len(t)), "depth_step_voxels": float(t[1] - t[0]),
               "step_voxels": float(step_voxels), "half_sheet_voxels": float(half_sheet_voxels),
               "points": int(seen.shape[0]), "grid": [int(x) for x in shape],
               "provenance": {"research_transfer": _digest(research_transfer)}}
    _write(out / "rays.json", context)
    return context


def extract_rays(research: Path, output: Path) -> dict:
    """What the transfer to the next winding reads, on the segment (`247`) and on the band (`248`, its first jump):
    the points of the mesh, one in eight, their normals, and what the prediction `m7` sees along each normal, read
    by the research's own reader from the research's unversioned cache of `m7` chunks.

    ⚠ Only where that cache lives (`data/spire_voisine/m7`, about 1 GB): the samples are embedded so that the transfer
    is computed anywhere, and `vesuve grand-prize --read-prediction` reads them again from the public bucket.
    """
    _prepare(research)
    import numpy as np
    # The research's own names, renamed here on the import line, and the keys of what it returns, unpacked once: this
    # tool is one of the two places that cross the border with the research (`vesuve/research.py`).
    from la_procedure_sans_juge_tient_elle_sur_la_bande import LE_PREMIER_SAUT as band_first_jump
    from la_procedure_sans_juge_tient_elle_sur_la_bande import la_bande as read_the_band
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE as cache
    from la_spire_voisine_est_elle_a_un_pas import les_normales as surface_normals
    from la_spire_voisine_est_elle_a_un_pas import lire_tifxyz as read_tifxyz
    from la_spire_voisine_est_elle_a_un_pas import telecharger as download_mesh
    from le_transfert_enchaine_tient_il_les_spires import lire_le_rayon as read_the_ray
    from le_transfert_retrouve_t_il_la_spire_voisine import DELAI as timeout
    from le_transfert_retrouve_t_il_la_spire_voisine import LA_MAILLE as mesh
    from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE as reach
    from le_transfert_retrouve_t_il_la_spire_voisine import LES_PREDICTIONS as predictions
    from le_transfert_retrouve_t_il_la_spire_voisine import le_facteur as volume_to_prediction_ratio
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot as bucket_reader
    path, level = predictions["m7"]
    factor, prediction_meta = volume_to_prediction_ratio(path, level, timeout)
    read_chunk, _ = bucket_reader(prediction_meta, cache, "m7", path, level, timeout)
    points, valid, _ = read_tifxyz(download_mesh(SEGMENT, cache, timeout))
    normals, has_normal = surface_normals(points, valid)
    on_mesh = np.zeros_like(has_normal)
    on_mesh[::mesh, ::mesh] = True
    ii, jj = np.nonzero(has_normal & on_mesh)
    shape = np.full(has_normal.shape, np.nan)[::mesh, ::mesh].shape
    t, seen = read_the_ray(points[ii, jj], normals[ii, jj], 1.0, reach, factor, prediction_meta, read_chunk)
    segment = _write_rays(output / "correction", prediction="m7", path=path, level=level, factor=factor, side=1.0,
                          t=t, seen=seen, gi=ii // mesh, gj=jj // mesh, shape=shape,
                          research_transfer=cache / f"transfert_suivante_{SEGMENT}_m7_du_cote_plus.npy")
    band = read_the_band(cache)
    read_band_ray, on_band_grid = band["lire_rayon"], band["sur_la_grille"]
    band_points, band_normals, band_rows, band_columns = band["p"], band["n"], band["gi"], band["gj"]
    t, seen = read_band_ray(band_points, band_normals, 1.0, reach)
    _write_rays(output.parent / BAND / "correction", prediction="m7", path=path, level=level, factor=factor, side=1.0,
                t=t, seen=seen, gi=band_rows, gj=band_columns, shape=on_band_grid(np.zeros(len(band_rows))).shape,
                research_transfer=band_first_jump)
    return segment


def extract_ink_judge(research: Path, output: Path) -> dict:
    """What the judge of the text of the produced winding (`296`) reads from the meshes: the segment reduced and the
    produced winding, as the research rendered them for the step tables of `275` (one mesh point every 160 voxels).

    The ink readings and the published map are not embedded: the readings weigh 16 MB a block, and the map is public.
    """
    import numpy as np
    import tifffile
    out = output / "ink_judge"
    out.mkdir(parents=True, exist_ok=True)
    context = {"provenance": {}}
    for role, surface in (("reference", "le_segment_reduit"), ("produced", "la_spire_produite")):
        folder = research / "data" / "rendu_spire_voisine" / surface / "maillage"
        points = np.stack([tifffile.imread(folder / f"{c}.tif") for c in "xyz"], axis=-1).astype(np.float32)
        _write_array(out / f"{role}_mesh.npy.gz", points)
        scale = json.loads((folder / "meta.json").read_text())["scale"][0]
        context.setdefault("spacing_voxels", 1.0 / scale)
        assert context["spacing_voxels"] == 1.0 / scale, "the two meshes must share their spacing"
        context[f"{role}_shape"] = [int(x) for x in points.shape[:2]]
        context["provenance"][role] = {f"{c}.tif": _digest(folder / f"{c}.tif") for c in "xyz"}
    _write(out / "meshes.json", context)
    return context


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = os.environ.get("VESUVE_RESEARCH")
    p.add_argument("--research", type=Path, required=root is None, default=root,
                   help="a working copy of the experimental branch (default: VESUVE_RESEARCH)")
    p.add_argument("--output", type=Path, default=OUTPUT)
    a = p.parse_args()
    c = extract(a.research.resolve(), a.output)
    print(f"written: {a.output} ({len(c['provenance']['files'])} research files read)")
    k = extract_correction(a.research.resolve(), a.output)
    print(f"written: {a.output / 'correction'} ({len(k['candidates'])} candidate blocks)")
    if (a.research / "data" / "rendu_spire_voisine" / "la_spire_produite" / "maillage").is_dir():
        m = extract_ink_judge(a.research.resolve(), a.output)
        print(f"written: {a.output / 'ink_judge'} (meshes of {m['reference_shape']} and {m['produced_shape']} points)")
    else:
        print(f"ink judge meshes skipped: no rendu_spire_voisine meshes under {a.research / 'data'}")
    if (a.research / "data" / "spire_voisine" / "m7").is_dir():
        r = extract_rays(a.research.resolve(), a.output)
        print(f"written: {a.output / 'correction' / 'rays.json'} ({r['points']} rays of {r['samples']} samples)")
    else:
        print(f"rays skipped: the research's cache of m7 chunks is not under {a.research / 'data'} (about 1 GB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
