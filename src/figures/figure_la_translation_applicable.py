#!/usr/bin/env python3
"""Ce que la géométrie a le droit de corriger, et ce qu'elle laisse à l'encre.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « La translation applicable n'est pas la meilleure » est une
phrase qui se discute. Placer les quatre candidates **sur le plan de l'encre**, avec le segment
qui va de celle qu'on retient à l'optimum, montre d'un coup ce que la règle de provenance coûte :
la distance dessinée EST la part du désaccord que les silhouettes ne voient pas.

⭐⭐ **Et le thermomètre à côté dit combien il en reste.** De l'affine publiée au plafond de
l'encre, chaque candidate géométrique se place, et la part atteinte est écrite. Sans lui, « la
géométrie corrige une partie » ne dit pas laquelle.

⚠ Les nombres sont LUS dans `docs/mesures/la_translation_applicable.json` et
`docs/mesures/le_residu_est_une_translation.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_la_translation_applicable.py --verifier
    uv run python src/figures/figure_la_translation_applicable.py \\
        --sortie docs/images/75_la_translation_applicable.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import (  # noqa: E402
    CASE, _plan, _point, bornes, couper, rampe,
)

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_translation_applicable.json"
PLAN = RACINE / "docs" / "mesures" / "le_residu_est_une_translation.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
VERT = (52, 122, 72)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)

COULEURS = (ROUGE, AMBRE, BLEU, VERT, (140, 90, 160))


def prose(m: dict, plan: dict) -> list[str]:
    r, pl, s = m["retenue"], m["plafond"], m["sans_correction"]
    lignes = [
        "la regle est de PROVENANCE : une translation tiree de l'encre ne peut pas etre "
        "appliquee, sinon l'encre devient juge et partie.",
        f"la retenue est donc « {r['nom']} » {tuple(r['decalage'])}, celle qui maximise le Dice "
        f"parmi les candidates geometriques ; elle porte l'accord publie de {s['auc']:.4f} a "
        f"{r['auc']:.4f}, soit {m['part_du_plafond_atteinte'] * 100:.0f} % du plafond "
        f"({pl['auc']:.4f}).",
        f"mais les quatre criteres geometriques s'etalent sur "
        f"{m['etalement_des_candidates_geometriques']:.0f} cases et atteignent de "
        f"{m['part_du_plafond_min'] * 100:.0f} a {m['part_du_plafond_max'] * 100:.0f} % du "
        f"plafond : la geometrie n'IDENTIFIE pas la translation, elle la borne.",
    ]
    if m.get("candidates_qui_degradent_le_dice"):
        lignes.append(
            f"et « {m['candidates_qui_degradent_le_dice'][0]} » fait BAISSER le Dice tout en "
            "faisant monter l'AUC : le critere des silhouettes n'est pas seulement faible, il "
            "est en partie contraire a celui qui compte.")
    return lignes


def dessiner(m: dict, plan: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    bal = plan["balayage"]
    lo, hi = bornes(bal, plan["temoin_carte_melangee"])
    portee, pas = bal["portee"], bal["pas"]
    n = 2 * portee // pas + 1
    largeur = n * CASE

    marge = 44
    xg = marge + 34
    xd = xg + largeur + 96
    y0 = 106
    lignes = couper(prose(m, plan))
    L = xd + 300 + marge
    H = y0 + largeur + 108 + len(m["candidates"]) * 16 + 36 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Ce que la geometrie a le droit de corriger", fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"fond : l'AUC de la carte publiee en fonction d'un decalage constant "
             f"(1 case = {plan['cellule_um']:.1f} um)", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             "une candidate tiree de l'ENCRE est dessinee mais barree : elle est un plafond, "
             "pas une correction", fill=DISCRET, font=moyen)

    for c in bal["grille"]:
        cx, cy = (c["dj"] + portee) // pas, (c["di"] + portee) // pas
        t = (c["auc"] - lo) / max(1e-9, hi - lo)
        art.rectangle([xg + cx * CASE, y0 + cy * CASE,
                       xg + (cx + 1) * CASE - 1, y0 + (cy + 1) * CASE - 1], fill=rampe(t))
    _plan(art, xg, y0, portee, pas, petit)

    dedans = 0
    for k, c in enumerate(m["candidates"]):
        di, dj = c["decalage"]
        if abs(di) > portee or abs(dj) > portee:
            continue
        dedans += 1
        px, py = _point(portee, pas, di, dj)
        x, y = xg + px, y0 + py
        coul = COULEURS[k % len(COULEURS)]
        art.ellipse([x - 5, y - 5, x + 5, y + 5], outline=coul, width=2)
        if c["applicable"]:
            art.line([x - 8, y, x + 8, y], fill=coul)
            art.line([x, y - 8, x, y + 8], fill=coul)
        else:
            # ⚠ Barrée plutôt qu'absente : une candidate qu'on n'a pas le droit d'appliquer doit
            # rester visible, sinon la figure cache le plafond qu'elle sert à situer.
            art.line([x - 8, y - 8, x + 8, y + 8], fill=coul, width=2)
            art.line([x - 8, y + 8, x + 8, y - 8], fill=coul, width=2)

    # ⭐ Le segment entre la retenue et le plafond : c'est la mesure que la figure existe pour
    # montrer, donc elle est DESSINÉE et pas seulement écrite.
    rp = _point(portee, pas, *m["retenue"]["decalage"])
    pp = _point(portee, pas, *m["plafond"]["decalage"])
    art.line([xg + rp[0], y0 + rp[1], xg + pp[0], y0 + pp[1]], fill=TEXTE, width=1)
    art.text((xg + (rp[0] + pp[0]) / 2 + 8, y0 + (rp[1] + pp[1]) / 2 - 14),
             f"{m['ecart_geometrie_encre_cases']:.0f} cases", fill=TEXTE, font=petit)

    # ⚠ La légende passe SOUS les deux colonnes et non à côté : ses lignes sont longues et
    # venaient recouvrir le thermomètre, ce qui rendait les deux illisibles à la fois.
    ly = y0 + largeur + 92
    for k, c in enumerate(m["candidates"]):
        coul = COULEURS[k % len(COULEURS)]
        art.ellipse([xg, ly + k * 16 + 3, xg + 8, ly + k * 16 + 11], outline=coul, width=2)
        etat = "applicable" if c["applicable"] else "PLAFOND, non applicable"
        art.text((xg + 14, ly + k * 16),
                 f"{c['nom']} {tuple(c['decalage'])} — Dice {c['dice']:.4f}, "
                 f"AUC {c['auc']:.4f} — {etat}", fill=DISCRET, font=petit)

    # --- le thermomètre ---
    art.text((xd, y0 - 20), "de l'affine publiee au plafond", fill=TEXTE, font=moyen)
    bas, haut = m["sans_correction"]["auc"], m["plafond"]["auc"]
    hx, ht = xd + 26, largeur
    art.rectangle([hx, y0, hx + 28, y0 + ht], outline=CADRE)

    def place(auc):
        return y0 + ht - (auc - bas) / max(1e-9, haut - bas) * ht

    for k, c in enumerate(m["candidates"]):
        if c["auc"] is None:
            continue
        yy = place(c["auc"])
        coul = COULEURS[k % len(COULEURS)]
        art.line([hx, yy, hx + 28, yy], fill=coul, width=3)
        art.text((hx + 34, yy - 7), f"{c['auc']:.4f}", fill=coul, font=petit)
    art.text((hx - 22, y0 - 2), "plafond", fill=DISCRET, font=petit)
    art.text((hx - 22, y0 + ht - 12), "aucune", fill=DISCRET, font=petit)
    art.text((xd, y0 + ht + 24),
             f"part atteinte par la geometrie : "
             f"{m['part_du_plafond_atteinte'] * 100:.0f} %", fill=TEXTE, font=moyen)
    e = m.get("equivalence") or {}
    if e.get("ecart") is not None:
        art.text((xd, y0 + ht + 46),
                 f"corriger l'affine ou decaler la lecture :", fill=DISCRET, font=petit)
        art.text((xd, y0 + ht + 60),
                 f"{e['auc_par_laffine']:.4f} contre {e['auc_par_lecture']:.4f}, "
                 f"ecart {e['ecart']:.4f}", fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"candidates": len(m["candidates"]), "dans_le_plan": dedans,
            "barrees": sum(1 for c in m["candidates"] if not c["applicable"]),
            "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    v("assez de couleurs pour les candidates", len(COULEURS) >= 5, str(len(COULEURS)))

    if not MESURE.is_file() or not PLAN.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    plan = json.loads(PLAN.read_text())
    v("la prose est traçable", prose_tracable(prose(m, plan)))
    # ⚠⚠⚠ LA RETENUE EST RECALCULÉE ICI, pas relue : la figure affirme « celle qui maximise le
    # Dice parmi les applicables », et si le dossier désignait autre chose la figure mentirait
    # avec l'air de citer.
    geo = [c for c in m["candidates"] if c["applicable"] and c["decalage"] != [0.0, 0.0]]
    v("la retenue est bien la meilleure applicable au sens du Dice",
      m["retenue"]["nom"] == max(geo, key=lambda c: c["dice"])["nom"],
      f"{m['retenue']['nom']} contre {max(geo, key=lambda c: c['dice'])['nom']}")
    # ⚠⚠ Et le contrôle qui empêche la règle d'être décorative : la candidate de l'encre doit
    # avoir une MEILLEURE AUC que la retenue, sinon « on s'interdit le plafond » ne coûte rien
    # et la règle de provenance n'aurait jamais été mise à l'épreuve.
    v("la candidate d'encre bat bien la retenue sur l'encre, donc la règle COÛTE",
      m["plafond"]["auc"] > m["retenue"]["auc"],
      f"{m['plafond']['auc']} contre {m['retenue']['auc']}")
    v("... et elle est marquée non applicable", not m["plafond"]["applicable"])

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, plan, Path(d) / "t.png")
        v("toutes les candidates sont dessinées", r["candidates"] == len(m["candidates"]),
          str(r["candidates"]))
        v("... et toutes tiennent dans le plan", r["dans_le_plan"] == r["candidates"],
          f"{r['dans_le_plan']}/{r['candidates']}")
        v("... et celle de l'encre est barrée, pas absente", r["barrees"] == 1, str(r["barrees"]))
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
    p.add_argument("--plan", type=Path, default=PLAN)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_la_translation_applicable.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file() or not a.plan.is_file():
        raise SystemExit("mesure absente")
    r = dessiner(json.loads(a.mesure.read_text()), json.loads(a.plan.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['candidates']} candidates, {r['barrees']} barrée)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
