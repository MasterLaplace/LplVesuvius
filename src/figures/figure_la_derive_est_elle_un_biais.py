#!/usr/bin/env python3
"""La dérive du pas : un cinquième de biais, quatre cinquièmes de dispersion.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « 20 % » est un nombre qui ne dit pas s'il faut construire un
recalage. **Les deux courbes le disent** : celle qui a servi à choisir la longueur, et celle de la
moitié réservée qui ne l'a jamais vue. Une longueur qui creuserait un puits profond sur la
première et rien sur la seconde serait un ajustement ; ici les deux creusent, mais aucune ne
descend à zéro — et ce plancher **est** la dispersion.

⭐⭐ Les deux longueurs sont marquées : la **nominale**, qui vient de l'écart mesuré entre spires,
et l'**ajustée**. L'écart entre elles est le biais ; la hauteur du plancher est ce qu'aucune
longueur ne peut retirer.

Usage :
    uv run python src/figures/figure_la_derive_est_elle_un_biais.py --verifier
    uv run python src/figures/figure_la_derive_est_elle_un_biais.py \\
        --sortie docs/images/75_la_derive_est_elle_un_biais.png
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
MESURE = RACINE / "docs" / "mesures" / "la_derive_est_elle_un_biais.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    e = m["erreur_sur_la_reserve"]
    return [
        f"longueur de pas ajustee sur {m['paires_ajustement']} paires et jugee sur les "
        f"{m['paires_reservees']} reservees, que la longueur n'a jamais vues.",
        f"l'ajustee vaut {m['longueur_ajustee_um']:.0f} um contre {m['ecart_nominal_um']:.0f} "
        f"nominaux, soit un biais de {m['ecart_des_deux_longueurs_um']:.0f} um.",
        f"sur la moitie reservee elle fait {e['ajustee_um']:.0f} um contre "
        f"{e['nominale_um']:.0f} : elle gagne, donc le biais est reel, mais il n'explique que "
        f"{m['part_de_la_derive_expliquee'] * 100:.0f} % de l'erreur.",
        "les quatre cinquiemes qui restent sont une DISPERSION : aucune longueur constante ne "
        "les retire, et seul un raccrochage a la matiere le peut.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    aj, re = m["balayage_ajustement"], m["balayage_reserve"]
    marge = 44
    gw, gh = 640, 280
    x0, y0 = marge + 48, 108
    lignes = couper(prose(m), 108)
    L = x0 + gw + marge + 40
    H = y0 + gh + 118 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "La derive du pas : un cinquieme de biais, le reste en dispersion",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"erreur mediane d'UN pas, en fonction de sa longueur — {m['echantillon']} points "
             f"par paire", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "ambre : les paires qui ont choisi la longueur — bleu : la moitie reservee",
             fill=DISCRET, font=moyen)

    xs = [e["longueur_um"] for e in aj]
    lo, hi = min(xs), max(xs)
    haut = max([e["erreur_um"] for e in aj] + [e["erreur_um"] for e in re]) * 1.1
    art.rectangle([x0, y0, x0 + gw, y0 + gh], outline=CADRE)
    for k in (0, 1, 2):
        val = haut * k / 2.0
        art.text((x0 - 44, y0 + gh - val / haut * gh - 6), f"{val:.0f}µ",
                 fill=DISCRET, font=petit)

    def pt(e):
        return (x0 + (e["longueur_um"] - lo) / (hi - lo) * gw,
                y0 + gh - e["erreur_um"] / haut * gh)

    for serie, coul in ((aj, AMBRE), (re, BLEU)):
        pts = [pt(e) for e in serie]
        for a_, b_ in zip(pts, pts[1:]):
            art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=3)

    for val, coul, nom in ((m["ecart_nominal_um"], ROUGE, "nominale"),
                           (m["longueur_ajustee_um"], TEXTE, "ajustee")):
        x = x0 + (val - lo) / (hi - lo) * gw
        art.line([x, y0, x, y0 + gh], fill=coul, width=2)
        art.text((x + 4, y0 + 6), f"{nom} {val:.0f}µ", fill=coul, font=petit)
    for k in (0, len(xs) // 2, len(xs) - 1):
        x = x0 + (xs[k] - lo) / (hi - lo) * gw
        art.text((x - 14, y0 + gh + 5), f"{xs[k]:.0f}", fill=DISCRET, font=petit)
    art.text((x0, y0 + gh + 22), "longueur du pas, en micrometres", fill=DISCRET, font=petit)

    e = m["erreur_sur_la_reserve"]
    ys = y0 + gh + 46
    art.text((x0, ys), f"sur la moitie RESERVEE : nominale {e['nominale_um']:.0f} um  →  "
             f"ajustee {e['ajustee_um']:.0f} um", fill=TEXTE, font=moyen)
    art.text((x0, ys + 20),
             f"soit {m['part_de_la_derive_expliquee'] * 100:.0f} % de l'erreur expliques par un "
             f"BIAIS de {m['ecart_des_deux_longueurs_um']:.0f} um, et "
             f"{100 - m['part_de_la_derive_expliquee'] * 100:.0f} % qui restent",
             fill=TEXTE, font=moyen)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    plancher = min(x["erreur_um"] for x in re)
    return {"points": len(aj), "plancher_reserve_um": plancher,
            "au_bord": m["minimum_au_bord"], "sortie": str(sortie)}


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
    # ⚠⚠⚠ LES DEUX MOITIÉS DU RÉSULTAT, et il faut les deux : l'ajustée gagne sur la moitié
    # réservée (donc le biais est réel), ET elle ne descend pas à zéro (donc il reste une
    # dispersion). Ne garder que l'une raconterait une explication ou un échec, pas la mesure.
    e = m["erreur_sur_la_reserve"]
    v("l'ajustée bat la nominale sur la moitié RÉSERVÉE",
      e["ajustee_um"] < e["nominale_um"], f"{e['ajustee_um']} contre {e['nominale_um']}")
    v("... et elle ne descend pas à zéro, donc il reste une dispersion",
      e["ajustee_um"] > 0.2 * m["ecart_nominal_um"],
      f"{e['ajustee_um']} µm sur un écart de {m['ecart_nominal_um']}")
    v("la part expliquée est celle que les deux erreurs donnent",
      abs(m["part_de_la_derive_expliquee"]
          - (1.0 - e["ajustee_um"] / e["nominale_um"])) < 1e-3,
      str(m["part_de_la_derive_expliquee"]))
    # ⚠⚠ Un minimum au bord ne désignerait aucune longueur : ce dépôt l'a déjà payé.
    v("le minimum du balayage est intérieur", not m["minimum_au_bord"])
    # ⚠ Et la moitié réservée doit être une vraie moitié, pas trois paires laissées de côté.
    v("les deux moitiés sont de tailles comparables",
      abs(m["paires_ajustement"] - m["paires_reservees"]) <= 1,
      f"{m['paires_ajustement']} contre {m['paires_reservees']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("le balayage entier est tracé", r["points"] == m["longueurs_essayees"],
          str(r["points"]))
        v("... et la courbe réservée a bien un plancher non nul",
          r["plancher_reserve_um"] > 0, f"{r['plancher_reserve_um']} µm")
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
                   default=RACINE / "docs" / "images" / "75_la_derive_est_elle_un_biais.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['points']} longueurs, plancher "
          f"{r['plancher_reserve_um']} µm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
