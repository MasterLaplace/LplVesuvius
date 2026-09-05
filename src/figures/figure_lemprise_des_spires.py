#!/usr/bin/env python3
"""Où le segment de C1 tombe parmi les treize spires publiées.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Un tableau de recouvrements dit **combien** ; la coupe dit
**où**. Superposer le segment sur lequel toute la colonne C a été bâtie et les treize spires, dans
la même projection, répond d'un coup d'œil à la question que les nombres formulent : est-ce la
même feuille, un morceau recousu, ou une autre région du fragment ?

⭐ Les deux nuages sont tracés au **même compte de points** : deux semis dessinés à deux densités
se comparent à l'œil sur leur densité et non sur leur place, ce qui est exactement l'erreur que
cette figure existe pour éviter.

⚠ Les nombres et les traces sont LUS dans `docs/mesures/lemprise_des_spires.json` et
`docs/mesures/les_wraps_publies.json`.

Usage :
    uv run python src/figures/figure_lemprise_des_spires.py --verifier
    uv run python src/figures/figure_lemprise_des_spires.py \\
        --sortie docs/images/75_lemprise_des_spires.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper, rampe  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "lemprise_des_spires.json"
SPIRES = RACINE / "docs" / "mesures" / "les_wraps_publies.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    b = m["meilleure_spire"]
    return [
        f"le seuil vaut {m['seuil_um']:.1f} um, soit {m['seuil_derive_de']} : sous une "
        "demi-epaisseur, deux surfaces sont la MEME feuille.",
        f"et la barre du verdict est MESUREE, pas choisie : {m['plafond_entre_spires'] * 100:.1f} % "
        f"est {m['plafond_derive_de']}.",
        f"le segment de C1 est a moins de ce seuil d'une spire pour "
        f"{m['part_du_segment_sur_l_union'] * 100:.1f} % de ses points, et la meilleure spire "
        f"seule en couvre {b['part_du_segment_sur_la_spire'] * 100:.1f} % (rang {b['rang']}).",
        f"→ {m['verdict']}.",
    ]


def dessiner(m: dict, spires: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    traces = spires["traces_xz"]
    rangs = sorted((int(k) for k in traces), key=int)
    seg = m["trace_xz_du_segment"]
    xs = [p[0] for r in rangs for p in traces[str(r)]] + [p[0] for p in seg]
    zs = [p[1] for r in rangs for p in traces[str(r)]] + [p[1] for p in seg]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)

    marge, cote = 44, 430
    ech = cote / max(x1 - x0, z1 - z0)
    lp, hp = int((x1 - x0) * ech), int((z1 - z0) * ech)
    xg = marge + 10
    xd = xg + lp + 100
    y0 = 104
    lignes = couper(prose(m), 108)
    L = xd + 380 + marge
    H = y0 + max(hp, 300) + 46 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Ou le segment de C1 tombe parmi les treize spires",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"coupe x/z, volume {m['volume']} ({m['voxel_um']} um/voxel) ; "
             f"seuil {m['seuil_um']:.1f} um", fill=DISCRET, font=moyen)
    art.text((marge, 62), "en gris-ambre les spires 1 a 13, en rouge le segment de C1",
             fill=DISCRET, font=moyen)

    art.rectangle([xg, y0, xg + lp, y0 + hp], outline=CADRE)
    for r in rangs:
        coul = rampe((r - rangs[0]) / max(1, rangs[-1] - rangs[0]))
        for px, pz in traces[str(r)]:
            x, y = xg + (px - x0) * ech, y0 + (pz - z0) * ech
            art.ellipse([x - 1.2, y - 1.2, x + 1.2, y + 1.2], fill=coul)
    for px, pz in seg:
        x, y = xg + (px - x0) * ech, y0 + (pz - z0) * ech
        art.ellipse([x - 1.8, y - 1.8, x + 1.8, y + 1.8], fill=ROUGE)
    art.text((xg, y0 + hp + 8),
             f"{len(rangs)} spires et le segment, {len(seg)} points chacun",
             fill=DISCRET, font=petit)

    art.text((xd, y0 - 20), "part du segment a moins du seuil d'une spire",
             fill=TEXTE, font=moyen)
    gw, gh = 320, 210
    art.rectangle([xd, y0, xd + gw, y0 + gh], outline=CADRE)
    parts = [e["part_du_segment_sur_la_spire"] for e in m["spires"]]
    haut = max(parts + [m["part_du_segment_sur_l_union"],
                       m["plafond_entre_spires"]]) or 1.0
    lb = gw / max(1, len(parts))
    for k, e in enumerate(m["spires"]):
        h = e["part_du_segment_sur_la_spire"] / haut * gh
        x = xd + k * lb + 2
        art.rectangle([x, y0 + gh - h, x + lb - 4, y0 + gh], fill=AMBRE)
        art.text((x - 1, y0 + gh + 5), f"{e['rang']}", fill=DISCRET, font=petit)
    yu = y0 + gh - m["part_du_segment_sur_l_union"] / haut * gh
    art.line([xd, yu, xd + gw, yu], fill=ROUGE, width=2)
    art.text((xd + 4, yu - 15),
             f"union des spires : {m['part_du_segment_sur_l_union'] * 100:.1f} %",
             fill=ROUGE, font=petit)
    # ⚠ La barre mesurée est tracée : un verdict dont le seuil n'est pas sur la figure est un
    # verdict qu'il faut croire sur parole.
    yb = y0 + gh - m["plafond_entre_spires"] / haut * gh
    for x in range(xd, xd + gw, 8):
        art.line([x, yb, x + 4, yb], fill=TEXTE)
    art.text((xd + 4, yb + 3),
             f"plafond entre spires distinctes : {m['plafond_entre_spires'] * 100:.1f} %",
             fill=TEXTE, font=petit)
    art.text((xd, y0 + gh + 22), "une barre par spire, le rang en dessous",
             fill=DISCRET, font=petit)
    for k, l in enumerate(couper([m["verdict"]], 46)):
        art.text((xd, y0 + gh + 44 + k * 18), l, fill=TEXTE, font=moyen)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"spires": len(rangs), "points_du_segment": len(seg),
            "barres": len(m["spires"]), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file() or not SPIRES.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    sp = json.loads(SPIRES.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LE VERDICT DESSINÉ DOIT ÊTRE CELUI QUE LES NOMBRES DONNENT. La figure l'imprime en
    # toutes lettres ; s'il ne découlait pas des parts publiées, elle citerait une conclusion que
    # son propre graphique contredit.
    b = m["meilleure_spire"]
    u = m["part_du_segment_sur_l_union"]
    pl = m["plafond_entre_spires"]
    branche = ("EST une" if b["part_du_segment_sur_la_spire"] > pl
               else "RECOUSU" if u > pl else "AILLEURS")
    v("le verdict découle de la barre MESURÉE, pas d'un seuil écrit",
      branche.split()[0] in m["verdict"],
      f"{branche} attendu, verdict {m['verdict'][:44]!r}")
    # ⚠⚠⚠ ET LA BARRE DOIT ÊTRE CELLE DE LA DONNÉE : le plafond publié est le maximum de la
    # calibration entre spires. S'ils divergeaient, la figure citerait une barre que la mesure
    # n'a pas posée.
    v("la barre est le maximum de la calibration entre spires",
      abs(pl - m["calibration_entre_spires"]["maximum"]) < 1e-9,
      f"{pl} contre {m['calibration_entre_spires']['maximum']}")
    # ⚠⚠ Et le seuil doit être celui des spires, pas un nombre de ce fichier : sinon la figure
    # comparerait deux campagnes à deux règles.
    v("le seuil est la moitié de l'écart mesuré entre spires",
      abs(m["seuil_um"] * 2 - sp["resume"]["1"]["mediane_um"]) < 1e-6,
      f"{m['seuil_um']} pour {sp['resume']['1']['mediane_um']}")
    v("la meilleure spire est bien la meilleure",
      b["part_du_segment_sur_la_spire"]
      == max(e["part_du_segment_sur_la_spire"] for e in m["spires"]))
    v("... et l'union ne peut pas être sous la meilleure",
      u >= b["part_du_segment_sur_la_spire"] - 1e-9, f"{u} contre {b['part_du_segment_sur_la_spire']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, sp, Path(d) / "t.png")
        v("les spires et le segment sont tracés",
          r["spires"] == sp["spires_lues"] and r["points_du_segment"] > 100,
          f"{r['spires']} spires, {r['points_du_segment']} points")
        v("... et il y a une barre par spire", r["barres"] == len(m["spires"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png").convert("L")
        gris = img.getextrema()
        v("l'image a du relief", gris[0] < 90 and gris[1] > 240, str(gris))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--spires", type=Path, default=SPIRES)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_lemprise_des_spires.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file() or not a.spires.is_file():
        raise SystemExit("mesure absente")
    r = dessiner(json.loads(a.mesure.read_text()),
                 json.loads(a.spires.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['spires']} spires)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
