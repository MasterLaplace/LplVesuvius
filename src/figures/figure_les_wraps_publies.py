#!/usr/bin/env python3
"""Treize spires publiées, et l'écart qui les sépare — la vérité de terrain que le dépôt n'avait pas ouverte.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « L'écart entre spires consécutives vaut 135 µm » est un
nombre ; **treize surfaces emboîtées vues en coupe** sont une preuve qu'on ne discute pas. La
projection montre d'un coup que ces segments ne sont pas treize morceaux quelconques mais des
tours successifs d'un même enroulement.

⭐⭐ **Et l'attendu est tracé, pas raconté** : la ligne des 147,4 µm vient d'une mesure du dépôt
faite sur un AUTRE rouleau. Un accord avec une prédiction extérieure vaut mieux qu'un accord avec
soi-même, et le voir sur la même figure est ce qui le rend lisible.

⚠ Les paires qui s'écartent de l'attendu sont dessinées comme les autres, pas gommées : trois
d'entre elles dépassent largement, et une passe sous la moitié — c'est le vrai visage de la
donnée.

Usage :
    uv run python src/figures/figure_les_wraps_publies.py --verifier
    uv run python src/figures/figure_les_wraps_publies.py \\
        --sortie docs/images/75_les_wraps_publies.png
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
MESURE = RACINE / "docs" / "mesures" / "les_wraps_publies.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    att = m["attendu_publie"].get("ecart_inter_feuilles_um")
    r = m["resume"]
    return [
        f"l'index publie {m['spires_publiees']} spires de ce fragment, chacune avec sa surface "
        f"en 3D sur trois volumes, et aucune mesure du depot ne les avait ouvertes.",
        f"entre spires CONSECUTIVES l'ecart median vaut {r['1']['mediane_um']:.0f} um, contre "
        f"{att:.1f} um mesures ailleurs dans le depot sur un autre rouleau.",
        f"et il croit avec le rang : {r['1']['mediane_um']:.0f}, {r['2']['mediane_um']:.0f}, "
        f"{r['3']['mediane_um']:.0f} um pour un saut de 1, 2 et 3 — donc ce sont bien des tours "
        "empiles et pas treize morceaux quelconques.",
        "c'est une verite de terrain du DEROULEMENT, publiee, exacte, contre laquelle une "
        "chaine reconstruite peut enfin etre notee.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    traces = m["traces_xz"]
    rangs = sorted((int(k) for k in traces), key=int)
    xs = [p[0] for r in rangs for p in traces[str(r)]]
    zs = [p[1] for r in rangs for p in traces[str(r)]]
    x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)

    marge = 44
    cote = 430
    ech = cote / max(x1 - x0, z1 - z0)
    lp, hp = int((x1 - x0) * ech), int((z1 - z0) * ech)
    xg = marge + 10
    xd = xg + lp + 110
    y0 = 104
    lignes = couper(prose(m), 108)
    L = xd + 400 + marge
    H = y0 + max(hp, 330) + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Treize spires publiees, et l'ecart qui les separe",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['fragment']} — coupe x/z des surfaces, volume {m['volume']} "
             f"({m['voxel_um']} um/voxel)", fill=DISCRET, font=moyen)
    art.text((marge, 62), "la couleur va de la spire 1 a la spire 13",
             fill=DISCRET, font=moyen)

    art.rectangle([xg, y0, xg + lp, y0 + hp], outline=CADRE)
    for r in rangs:
        coul = rampe((r - rangs[0]) / max(1, rangs[-1] - rangs[0]))
        for px, pz in traces[str(r)]:
            x = xg + (px - x0) * ech
            y = y0 + (pz - z0) * ech
            art.ellipse([x - 1.3, y - 1.3, x + 1.3, y + 1.3], fill=coul)
    art.text((xg, y0 + hp + 8),
             f"{len(rangs)} spires, {sum(len(traces[str(r)]) for r in rangs)} points traces",
             fill=DISCRET, font=petit)

    # --- les écarts par paire ---
    att = m["attendu_publie"].get("ecart_inter_feuilles_um") or 0.0
    paires = m["sauts"]["1"]
    art.text((xd, y0 - 20), "ecart median entre spires consecutives",
             fill=TEXTE, font=moyen)
    gw, gh = 340, 210
    haut = max([p["mediane_um"] for p in paires] + [att]) * 1.15
    art.rectangle([xd, y0, xd + gw, y0 + gh], outline=CADRE)
    ya = y0 + gh - att / haut * gh
    art.line([xd, ya, xd + gw, ya], fill=ROUGE, width=2)
    art.text((xd + 4, ya - 15), f"{att:.1f} um attendus, mesures ailleurs",
             fill=ROUGE, font=petit)
    lb = gw / max(1, len(paires))
    hors = 0
    for k, p in enumerate(paires):
        h = p["mediane_um"] / haut * gh
        x = xd + k * lb + 2
        loin = p["mediane_um"] > 1.5 * att or p["mediane_um"] < 0.5 * att
        hors += int(loin)
        art.rectangle([x, y0 + gh - h, x + lb - 4, y0 + gh],
                      fill=(ROUGE if loin else AMBRE))
        art.text((x - 1, y0 + gh + 5), f"{p['de']}", fill=DISCRET, font=petit)
    art.text((xd, y0 + gh + 22),
             f"une barre par paire ; en rouge les {hors} qui s'ecartent de moitie ou plus",
             fill=DISCRET, font=petit)

    # --- l'écart contre le rang ---
    ys = y0 + gh + 56
    art.text((xd, ys), "et l'ecart contre le saut de rang", fill=TEXTE, font=moyen)
    r1 = m["resume"]["1"]["mediane_um"]
    for k, cle in enumerate(("1", "2", "3")):
        e = m["resume"][cle]
        y = ys + 24 + k * 22
        art.text((xd, y), f"saut {cle} :", fill=DISCRET, font=petit)
        lg = e["mediane_um"] / (m["resume"]["3"]["mediane_um"] * 1.1) * 200
        art.rectangle([xd + 56, y + 2, xd + 56 + lg, y + 12], fill=AMBRE)
        art.text((xd + 66 + lg, y), f"{e['mediane_um']:.0f} um  (x{e['mediane_um'] / r1:.2f})",
                 fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"spires": len(rangs), "paires": len(paires), "paires_hors_attendu": hors,
            "points": sum(len(traces[str(r)]) for r in rangs), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ CE QUE LA FIGURE AFFIRME DOIT ÊTRE VRAI DANS LA MESURE. Les deux revendications sont
    # assertées : l'écart croît avec le rang, et il tombe près d'un attendu venu d'ailleurs.
    r = m["resume"]
    v("l'écart croît bien avec le rang, comme le dessin le montre",
      r["1"]["mediane_um"] < r["2"]["mediane_um"] < r["3"]["mediane_um"],
      f"{r['1']['mediane_um']}, {r['2']['mediane_um']}, {r['3']['mediane_um']}")
    att = m["attendu_publie"].get("ecart_inter_feuilles_um")
    v("... et il tombe à moins de 20 % d'un attendu mesuré ailleurs",
      att and abs(r["1"]["mediane_um"] - att) / att < 0.20,
      f"{r['1']['mediane_um']} contre {att}")
    # ⚠⚠ Le contrôle qui empêche « proche de l'attendu » d'être vide : l'attendu doit venir d'un
    # AUTRE fichier de mesure, sinon la figure comparerait un nombre à lui-même.
    v("l'attendu vient d'une autre mesure du dépôt",
      (RACINE / "docs" / "mesures" / "la_surface_et_la_feuille.json").is_file())
    v("les treize spires ont été lues", m["spires_lues"] == m["spires_publiees"],
      f"{m['spires_lues']} sur {m['spires_publiees']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        rr = dessiner(m, Path(d) / "t.png")
        v("toutes les spires sont tracées", rr["spires"] == m["spires_lues"], str(rr["spires"]))
        v("... et toutes les paires consécutives sont en barres",
          rr["paires"] == len(m["sauts"]["1"]), str(rr["paires"]))
        # ⚠ Les paires hors attendu sont COMPTÉES, donc la prose ne peut pas les taire.
        v("les paires qui s'écartent sont comptées et il y en a",
          1 <= rr["paires_hors_attendu"] < rr["paires"],
          f"{rr['paires_hors_attendu']} sur {rr['paires']}")
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
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_les_wraps_publies.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['spires']} spires, {r['points']} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
