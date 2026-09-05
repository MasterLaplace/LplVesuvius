#!/usr/bin/env python3
"""La pile publiée s'arrête à six micromètres de la feuille voisine.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « Il manque 5,9 µm » est un nombre qu'on lit sans le croire ;
le profil dessiné avec sa portée et la feuille voisine juste derrière le rend évident. La pile
va **presque** assez loin — 0,956 feuille — et ce presque est toute la différence entre
« construire le raccrochage sur ce qui est publié » et « aller chercher le volume brut ».

⭐⭐ Le profil sert aussi de preuve à la convention : le pic d'intensité tombe sur le **centre**
de la pile, donc la surface y est bien, et l'indice de couche est bien une distance signée.

⚠ Le pic n'est PAS ce qui définit la surface — le centre l'est. Le pic la confirme, et l'écart
entre les deux est dessiné pour qu'on voie de combien.

Usage :
    uv run python src/figures/figure_la_portee_des_piles.py --verifier
    uv run python src/figures/figure_la_portee_des_piles.py \\
        --sortie docs/images/75_la_portee_des_piles.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_portee_des_piles_publiees.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    return [
        f"chaque spire publie une pile en (couche, u, v) : l'indice de couche EST une distance "
        f"signee le long de la normale, a {m['voxel_um']} um la couche.",
        f"les metadonnees ne disent pas ou est la surface ; mesure sur "
        f"{sum(s['colonnes'] for s in m['spires'])} colonnes, le pic tombe a "
        f"{m['ecart_median_du_pic_au_centre']:+.1f} couche du centre, donc la convention du "
        "milieu tient.",
        f"la pile porte a {m['portee_um']:.1f} um, soit {m['portee_en_feuilles']:.3f} feuille, "
        f"quand la voisine est a {m['ecart_inter_feuilles_um']:.1f}.",
        f"il manque {m['manque_um']:.1f} um : le raccrochage a la matiere ne peut PAS se batir "
        "sur ce qui est publie, il faut le volume brut.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    prem = m["spires"][0]
    prof = prem["profil"]
    n = len(prof)
    marge = 44
    gw, gh = 660, 250
    x0, y0 = marge + 46, 108
    lignes = couper(prose(m), 108)
    L = x0 + gw + marge + 40
    H = y0 + gh + 128 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "La pile publiee s'arrete a six micrometres de la feuille voisine",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"intensite moyenne par couche, spire {prem['spire']}, "
             f"{prem['colonnes']} colonnes cumulees", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "l'axe est la distance signee a la surface, en micrometres",
             fill=DISCRET, font=moyen)

    lo, hi = min(prof), max(prof)
    surf = m["couche_de_surface"]
    art.rectangle([x0, y0, x0 + gw, y0 + gh], outline=CADRE)

    def xk(k):
        return x0 + k / (n - 1) * gw

    pts = [(xk(k), y0 + gh - (v - lo) / max(1e-9, hi - lo) * gh) for k, v in enumerate(prof)]
    for a_, b_ in zip(pts, pts[1:]):
        art.line([a_[0], a_[1], b_[0], b_[1]], fill=AMBRE, width=3)

    xs = xk(surf)
    art.line([xs, y0, xs, y0 + gh], fill=BLEU, width=2)
    art.text((xs + 4, y0 + 6), "la surface (le centre)", fill=BLEU, font=petit)
    xp = xk(prem["pic"])
    art.line([xp, y0, xp, y0 + gh], fill=TEXTE)
    art.text((xp + 4, y0 + 24), f"le pic ({prem['ecart_au_centre']:+.1f} couche)",
             fill=TEXTE, font=petit)

    # ⚠ La feuille voisine est HORS de la pile : elle est dessinée quand même, au delà du cadre,
    # parce que c'est justement sa position qui fait le résultat.
    par_couche = gw / (n - 1)
    xf = xs + m["ecart_inter_feuilles_um"] / m["voxel_um"] * par_couche
    art.line([min(xf, x0 + gw + 34), y0 + 40, min(xf, x0 + gw + 34), y0 + gh],
             fill=ROUGE, width=3)
    art.text((x0 + gw - 150, y0 + 22),
             f"la feuille voisine, a {m['ecart_inter_feuilles_um']:.0f} um",
             fill=ROUGE, font=petit)
    art.line([x0 + gw, y0 + gh + 14, min(xf, x0 + gw + 34), y0 + gh + 14], fill=ROUGE, width=3)
    art.text((x0 + gw - 60, y0 + gh + 20), f"{m['manque_um']:.1f} um", fill=ROUGE, font=moyen)

    for k in (0, int(surf), n - 1):
        art.text((xk(k) - 18, y0 + gh + 2),
                 f"{(k - surf) * m['voxel_um']:+.0f}µ", fill=DISCRET, font=petit)

    ys = y0 + gh + 46
    art.text((x0, ys), f"portee {m['portee_um']:.1f} um = "
             f"{m['portee_en_feuilles']:.3f} feuille  →  la voisine n'est PAS atteinte",
             fill=TEXTE, font=moyen)
    for k, s in enumerate(m["spires"]):
        art.text((x0, ys + 22 + k * 16),
                 f"spire {s['spire']} : pic a {s['ecart_au_centre']:+.1f} couche du centre, "
                 f"{s['colonnes']} colonnes, contraste {s['contraste']:.2f}",
                 fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"couches": n, "spires": len(m["spires"]),
            "voisine_hors_cadre": bool(xf > x0 + gw), "sortie": str(sortie)}


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
    # ⚠⚠⚠ LES DEUX FAITS QUE LA FIGURE PORTE, et il faut les deux : la convention du centre TIENT
    # (sinon l'axe des distances est faux et rien d'autre ne vaut), et la voisine n'est PAS
    # atteinte (sinon la conclusion serait l'inverse).
    v("la convention du centre tient", m["convention_du_centre_tient"],
      f"pic médian à {m['ecart_median_du_pic_au_centre']:+.1f} couche")
    v("... et la feuille voisine n'est pas atteinte",
      not m["atteint_la_voisine"] and m["manque_um"] > 0,
      f"il manque {m['manque_um']} µm")
    v("... de peu, ce qui est tout l'intérêt",
      m["portee_en_feuilles"] > 0.9, f"{m['portee_en_feuilles']} feuille")
    # ⚠ Le profil doit venir d'assez de colonnes : sur un bloc isolé le pic tombe n'importe où.
    v("le profil est cumulé sur beaucoup de colonnes",
      all(s["colonnes"] > 10000 for s in m["spires"]),
      str([s["colonnes"] for s in m["spires"]]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("le profil entier est tracé", r["couches"] == m["spires"][0]["couches"],
          str(r["couches"]))
        v("... et la feuille voisine tombe hors du cadre, comme la mesure le dit",
          r["voisine_hors_cadre"])
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
                   default=RACINE / "docs" / "images" / "75_la_portee_des_piles.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['couches']} couches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
