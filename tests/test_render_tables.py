"""The step tables made here: the two surfaces, the mirror, the render and the steps, each against the research's.

The correction only holds if the program can make its own inputs: the two surfaces from the published segment and
its transfer, the chunks a render reads, the pile rendered by `vc_render_tifxyz`, and the window-to-window steps read
from it. Each piece is compared with the research function that made it, on inputs the research never saw; and the
row-by-row loop is exercised with a renderer that writes synthetic piles, so that its order (a table waits for the
pile to its south) is checked without downloading a gigabyte.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pytest

from conftest import research
from vesuve.transfer import mirror, rendering, steps, surfaces, tables
from vesuve.transport import InMemoryTransport


def _sheet_pile(ny: int, nx: int, seed: int = 7) -> np.ndarray:
    """A synthetic pile of `ny` × `nx` chunks: a sheet whose depth undulates, a fainter one below, fibres, and noise.

    ⚠ The fibres are what the texture filter keeps: without them every chunk is refused as too little texture, and a
    table of steps would compare two empty dictionaries.
    """
    rng = np.random.default_rng(seed)
    h, w = ny * 128, nx * 128
    yy, xx = np.mgrid[0:h, 0:w]
    z0 = 54 + 9 * np.sin(xx / 170.0) + 7 * np.cos(yy / 230.0)
    z = np.arange(109)[:, None, None]
    p = 200 * np.exp(-0.5 * ((z - z0[None]) / 3.0) ** 2) + 20 * np.exp(-0.5 * ((z - z0[None] - 30) / 3.0) ** 2)
    p = (p + 30) * (1 + 0.6 * np.sin(xx / 3.0))[None]
    return np.clip(p + rng.normal(0, 6, p.shape), 0, 255).astype(np.uint8)


def _curved_surface(h: int = 40, w: int = 50, seed: int = 3) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    v, u = np.mgrid[0:h, 0:w].astype(float)
    points = np.stack([4000 + 20 * u, 9000 + 20 * v, 30000 + 60 * np.sin(u / 9.0) + 40 * np.cos(v / 7.0)], axis=-1)
    valid = rng.random((h, w)) > 0.03
    points[~valid] = -1.0
    return points, valid


# ── The two surfaces ─────────────────────────────────────────────────────────────────────────────────────────────

@research
def test_the_normals_and_the_two_meshes_are_the_research_s():
    from la_spire_produite_se_lit_elle_dans_le_treillis import le_maillage_produit, le_maillage_reduit
    from la_spire_voisine_est_elle_a_un_pas import les_normales
    points, valid = _curved_surface(80, 96)
    n, ok = surfaces.normals(points, valid)
    rn, rok = les_normales(points, valid)
    assert np.array_equal(n, rn) and np.array_equal(ok, rok)
    ours, theirs = surfaces.reduced_mesh(points, valid), le_maillage_reduit(points, valid)
    assert all(np.array_equal(a, b) for a, b in zip(ours, theirs))
    tau = np.random.default_rng(1).normal(0, 40, points[::8, ::8].shape[:2])
    tau[3, 4] = np.nan
    ours, theirs = surfaces.produced_mesh(points, valid, tau), le_maillage_produit(points, valid, tau)
    assert all(np.array_equal(a, b) for a, b in zip(ours, theirs))


def test_a_transfer_of_the_wrong_shape_is_refused():
    points, valid = _curved_surface()
    with pytest.raises(ValueError, match="the transfer map is"):
        surfaces.produced_mesh(points, valid, np.zeros((2, 2)))


def test_the_written_mesh_reads_back(tmp_path):
    points, valid = _curved_surface()
    folder = surfaces.write_for_render(tmp_path / "m", points, valid, 1 / 160, "produced")
    back, v, spacing = surfaces.read_points(folder)
    assert np.array_equal(v, valid) and spacing == pytest.approx(160.0)
    assert np.array_equal(back[valid], points[valid].astype(np.float32).astype(np.float64))
    assert json.loads((folder / "meta.json").read_text())["uuid"] == "produced"


# ── The mirror ───────────────────────────────────────────────────────────────────────────────────────────────────

@research
def test_the_chunks_of_a_crop_are_the_research_s():
    from le_miroir_du_volume import les_chunks_dun_cadre
    points, valid = _curved_surface()
    for box in (rendering.crop(0, 0, 2), rendering.crop(3, 5, 4)):
        theirs = les_chunks_dun_cadre(points, 8.0, {"x": box["x"], "y": box["y"], "largeur": box["width"],
                                                    "hauteur": box["height"]})
        ours = mirror.chunks_of_crop(points, 8.0, box)
        assert ours == theirs and len(ours) > 10


def _volume(chunk=(2, 2, 2), compressor=None) -> dict:
    zarray = {"shape": [8, 8, 8], "chunks": list(chunk), "dtype": "|u1", "compressor": compressor, "filters": None,
              "fill_value": 0, "order": "C", "zarr_format": 2, "dimension_separator": "/"}
    return {"https://s3/v.zarr/.zgroup": b"{}", "https://s3/v.zarr/.zattrs": b"{}",
            "https://s3/v.zarr/0/.zattrs": b"{}", "https://s3/v.zarr/0/.zarray": json.dumps(zarray).encode()}


def test_the_mirror_fills_what_it_lacks_marks_what_is_absent_and_refuses_a_wrong_size(tmp_path):
    bodies = {**_volume(), "https://s3/v.zarr/0/0/0/0": bytes(8), "https://s3/v.zarr/0/0/0/1": bytes(5),
              "https://s3/v.zarr/0/1/1/1": None}
    t = InMemoryTransport(bodies)
    m = mirror.Mirror(tmp_path / "mirror", "https://s3/v.zarr", t)
    got = m.fill({(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 1, 1)}, threads=2)
    assert m.chunk_bytes == 8
    assert m.is_sound((0, 0, 0)) and m.is_sound((1, 0, 0))              # present, and declared absent
    assert not m.is_sound((0, 0, 1)) and not m.is_sound((1, 1, 1))        # a wrong size, and a dropped wire
    assert set(got["failed"]) == {"0/0/1", "1/1/1"} and got["downloaded"] == 2
    asked = len(t.requests)
    m.fill({(0, 0, 0), (1, 0, 0)})
    assert len(t.requests) == asked                                       # a sound chunk is not fetched again
    m.path((0, 0, 0)).write_bytes(bytes(3))                               # truncated by a crash
    again = m.fill({(0, 0, 0)})
    assert again["replaced_at_a_wrong_size"] == 1 and m.is_sound((0, 0, 0))


def test_the_mirror_keeps_only_what_is_asked(tmp_path):
    m = mirror.Mirror(tmp_path / "mirror", "https://s3/v.zarr", InMemoryTransport(
        {**_volume(), **{f"https://s3/v.zarr/0/0/0/{i}": bytes(8) for i in range(3)}}))
    m.fill({(0, 0, 0), (0, 0, 1), (0, 0, 2)})
    assert m.empty({(0, 0, 1)}) == 2 and m.is_sound((0, 0, 1)) and not m.path((0, 0, 0)).exists()


# ── The render ───────────────────────────────────────────────────────────────────────────────────────────────────

@research
def test_the_render_command_is_the_research_s(tmp_path):
    from la_spire_produite_se_lit_elle_dans_le_treillis import la_commande_de_rendu, le_cadre
    theirs = la_commande_de_rendu(tmp_path / "m", tmp_path / "o", le_cadre(16, 32, 16), miroir=tmp_path / "mir")
    ours = rendering.command(tmp_path / "m", tmp_path / "o", rendering.crop(16, 32, 16), tmp_path / "mir")
    # The research's watchdog script adds the cache cap in front of the real renderer (`rendre_surveille.sh`).
    assert ours == [rendering.RENDERER, *theirs, "--cache-gb", "1"]


def _fake_runner(layers=rendering.LAYERS, code=0):
    def run(cmd, output, log, patience):
        for k in range(layers):
            (output / f"{k:03d}.tif").write_bytes(b"x")
        return {"code": code, "abandoned": False, "seconds": 0.0}
    return run


def test_a_pile_is_complete_only_with_its_end_mark_and_an_unfinished_one_is_set_aside(tmp_path):
    out = tmp_path / "piles" / "block_0_0"
    got = rendering.render(tmp_path / "m", out, rendering.crop(0, 0, 1), tmp_path / "mir", runner=_fake_runner(50))
    assert not got["rendered"] and not rendering.is_complete(out)        # 50 layers of 109
    got = rendering.render(tmp_path / "m", out, rendering.crop(0, 0, 1), tmp_path / "mir", runner=_fake_runner())
    assert got["rendered"] and rendering.is_complete(out) and "set_aside" in got
    assert len(list((tmp_path / "piles" / "_set_aside").iterdir())) == 1  # the unfinished one, kept
    again = rendering.render(tmp_path / "m", out, rendering.crop(0, 0, 1), tmp_path / "mir", runner=_fake_runner())
    assert again["resumed"]
    failed = tmp_path / "piles" / "block_1_1"
    assert not rendering.render(tmp_path / "m", failed, rendering.crop(1, 1, 1), tmp_path / "mir",
                                runner=_fake_runner(code=3))["rendered"]


def test_the_watchdog_abandons_an_idle_process_and_spares_a_working_one(tmp_path):
    out = tmp_path / "o"
    out.mkdir()
    t0 = time.monotonic()
    idle = rendering.watch(["sleep", "30"], out, tmp_path / "idle.log", patience=1.0, poll=0.3)
    assert idle["abandoned"] and time.monotonic() - t0 < 10
    busy = rendering.watch(["bash", "-c", "for i in $(seq 1 12); do read -r _ < /etc/hostname; sleep 0.2; done"],
                           out, tmp_path / "busy.log", patience=1.0, poll=0.3)
    assert not busy["abandoned"] and busy["code"] == 0


# ── The steps ────────────────────────────────────────────────────────────────────────────────────────────────────

@research
def test_the_fine_step_the_windows_and_the_chained_step_are_the_research_s():
    from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_somme_des_pas, le_pas_fin, les_fenetres
    rng = np.random.default_rng(20260928)
    for _ in range(60):
        a = rng.normal(0, 1, 109).cumsum()
        b = np.roll(a, int(rng.integers(-20, 20))) + rng.normal(0, 0.3, 109)
        assert steps.fine_step(a, b) == le_pas_fin(a, b)
    assert steps.fine_step(np.ones(109), np.ones(109)) is None is le_pas_fin(np.ones(109), np.ones(109))
    section = rng.integers(0, 255, (109, 128)).astype(float)
    assert np.array_equal(steps.windows(section), les_fenetres(section))
    fa, fb = steps.windows(section), steps.windows(np.roll(section, 3, axis=0))
    assert steps.chained_step(fa, fb) == la_somme_des_pas(fa, fb)


@research
def test_a_block_table_is_the_research_s():
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import les_pas_dun_bloc
    from le_voisinage_dit_il_quel_niveau_est_le_bon import servir_plusieurs
    pile = _sheet_pile(3, 3)
    piles = {(y, x): pile[:, y * 128:(y + 2) * 128, x * 128:(x + 2) * 128] for y in (0, 2) for x in (0, 2)}
    piles = {k: v for k, v in piles.items() if v.shape[1] == 256 and v.shape[2] == 256} | {
        (0, 2): np.pad(pile[:, :256, 256:], ((0, 0), (0, 0), (0, 128))),
        (2, 0): np.pad(pile[:, 256:, :256], ((0, 0), (0, 128), (0, 0)))}
    theirs = les_pas_dun_bloc(servir_plusieurs(piles, cote=2), 0, 0, True, True, cote=2, combien=4)
    ours = steps.block_table(steps.chunk_reader(piles, side=2), 0, 0, True, True, side=2, count=4)
    assert ours["h"] == theirs["h"] and ours["v"] == theirs["v"] and len(ours["h"]) == 4 and len(ours["v"]) == 4
    assert ours["kept_chunks"] == theirs["les_chunks_retenus"] == 4


def test_the_filter_says_why_a_chunk_is_refused():
    pile = _sheet_pile(1, 1)
    assert steps.kept_chunk(None) == (None, steps.OUTSIDE)
    assert steps.kept_chunk(np.zeros_like(pile)) == (None, steps.EMPTY)
    noise = np.random.default_rng(2).integers(1, 255, pile.shape).astype(np.uint8)
    assert steps.kept_chunk(noise) == (None, steps.TOO_LITTLE_TEXTURE)   # no orientation: no fibres
    assert steps.kept_chunk(pile)[1] is None


def test_an_empty_chunk_breaks_its_seams_and_is_counted():
    pile = _sheet_pile(2, 2)
    pile[:, :128, 128:] = 0
    t = steps.block_table(steps.chunk_reader({(0, 0): pile}, side=2), 0, 0, False, False, side=2, count=4)
    assert t["refused"] == {steps.EMPTY: 1} and t["kept_chunks"] == 3
    assert set(t["h"]) == {"1_0"} and set(t["v"]) == {"0_0"}          # every seam of chunk (0, 1) is gone


# ── The row-by-row loop ──────────────────────────────────────────────────────────────────────────────────────────

def test_the_loop_reads_a_table_once_its_south_pile_exists_and_frees_the_piles(tmp_path, monkeypatch):
    points, valid = _curved_surface(60, 60)
    mesh = surfaces.write_for_render(tmp_path / "mesh", points, valid, 1 / 20.0, "s")
    pile = _sheet_pile(2, 2)
    rendered = []

    def fake_render(tifxyz, output, box, mirror_folder, **_):
        output.mkdir(parents=True, exist_ok=True)
        rendered.append(output.name)
        for k in range(rendering.LAYERS):
            (output / f"{k:03d}.tif").write_bytes(b"x")
        (output / rendering.END_MARK).write_text("ok\n")
        return {"rendered": True, "resumed": False}

    monkeypatch.setattr(tables.rendering, "render", fake_render)
    monkeypatch.setattr(tables.rendering, "read_pile", lambda folder: pile)
    monkeypatch.setattr(tables.TableMaker, "needs", lambda self, s, by, bx: set())
    monkeypatch.setattr(tables, "BLOCK", 2)
    monkeypatch.setattr(tables.steps, "block_table",
                        lambda read, by, bx, east, south, **_: {"row": by, "column": bx, "east": east, "south": south,
                                                                "h": {f"{by}_{bx}": [1.0, 0.0, 2]}, "v": {}})
    t = tables.TableMaker(tmp_path / "work", {"s": mesh}, {(0, 0), (0, 2), (2, 0)}, "https://s3/v.zarr",
                          InMemoryTransport(_volume()), disks=())
    got = t.make()
    assert got["rows_done"] == 2 and not got["failed"] and got["stopped"] is None
    assert t.table("s", 0, 0)["east"] and t.table("s", 0, 0)["south"]     # read after row 2 was rendered
    assert not t.table("s", 0, 2)["east"] and not t.table("s", 0, 2)["south"]
    assert set(t.tables_for_the_correction()) == {("s", 0, 0), ("s", 0, 2), ("s", 2, 0)}
    assert not any((tmp_path / "work" / "piles" / "s").glob("block_*"))  # every pile freed once read


def test_the_loop_stops_when_a_disk_runs_short(tmp_path, monkeypatch):
    points, valid = _curved_surface(60, 60)
    mesh = surfaces.write_for_render(tmp_path / "mesh", points, valid, 1 / 20.0, "s")
    monkeypatch.setattr(tables, "short_of_space", lambda disks, threshold_gb=40.0: "C: has only 3.0 GB free")
    got = tables.TableMaker(tmp_path / "work", {"s": mesh}, {(0, 0)}, "https://s3/v.zarr",
                            InMemoryTransport(_volume()), disks=()).make()
    assert got["stopped"].startswith("C: has only") and got["rows_done"] == 0


def test_a_chunk_two_rows_share_is_downloaded_once(tmp_path, monkeypatch):
    points, valid = _curved_surface(60, 60)
    mesh = surfaces.write_for_render(tmp_path / "mesh", points, valid, 1 / 20.0, "s")
    monkeypatch.setattr(tables, "BLOCK", 2)
    monkeypatch.setattr(tables.rendering, "render", lambda *a, **k: {"rendered": True, "resumed": False})
    monkeypatch.setattr(tables.TableMaker, "_tables_of_row", lambda self, r: None)
    shared = {0: {(0, 0, 0), (0, 0, 1)}, 2: {(0, 0, 1), (0, 0, 2)}, 4: {(0, 0, 3)}}
    monkeypatch.setattr(tables.TableMaker, "needs", lambda self, s, by, bx: shared[by])
    bodies = {**_volume(), **{f"https://s3/v.zarr/0/0/0/{i}": bytes(8) for i in range(4)}}
    transport = InMemoryTransport(bodies)
    maker = tables.TableMaker(tmp_path / "work", {"s": mesh}, {(0, 0), (2, 0), (4, 0)}, "https://s3/v.zarr",
                              transport, disks=())
    assert maker.make()["rows_done"] == 3
    chunks = [u for u in transport.requests if u.startswith("https://s3/v.zarr/0/0/0/")]
    assert sorted(chunks) == [f"https://s3/v.zarr/0/0/0/{i}" for i in range(4)]   # (0, 0, 1) once, not twice
    assert not maker.mirror.path((0, 0, 0)).exists() and maker.mirror.path((0, 0, 3)).exists()
