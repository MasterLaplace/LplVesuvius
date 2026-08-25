#!/usr/bin/env python3
"""« Consistent with », mesuré : ce qui suit le contraste d'encre, et ce qui va contre.

⚠⚠ **Ce que cette figure établit.** Le papier fondateur défend ce qu'il lit sur les couches
cachées par une seule phrase — *« the scale, line separation, and script are consistent
with those observed on the fragment surfaces »* — qui met l'échelle, la séparation des
lignes et le tracé dans un même souffle, comme si elles allaient ensemble. Mesurées, elles
ne vont pas ensemble : trois grandeurs retrouvent le classement du contraste d'encre publié,
et la **séparation des lignes va franchement à contre-sens**.

⭐ Le panneau de droite montre pourquoi, et c'est ce qui rend la chose lisible plutôt
qu'étrange : plus une carte porte d'encre, plus ses lignes sont proches de se toucher, donc
**moins** de fenêtres montrent une séparation nette. Les deux grandeurs mesurent des choses
différentes, et une phrase qui les rassemble le cache.

⚠ La couverture, elle, est presque tautologique — le contraste d'encre est bâti sur des
percentiles d'encre, donc une carte plus encrée a les deux. Sa barre est marquée comme telle :
sans ça, un AUC de 0,97 se lirait comme une validation alors qu'il mesure deux fois la même
chose.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_typographie.py \\
        --entree docs/typographie.json --sortie docs/images/45_typographie.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LARGEUR, HAUTEUR = 1180, 500
# Panneau gauche : les AUC, centrés sur 0,50.
GX, GLARG, GY, LIGNE = 230, 300, 110, 40
# Panneau droit : le nuage qui explique l'inversion.
DX, DLARG, DY, DHAUT = 730, 380, 128, 232

FOND, TEXTE, TRAIT = (255, 255, 255), (25, 25, 25), (150, 150, 150)
SUIT, CONTRE, NEUTRE = (40, 110, 60), (200, 45, 45), (150, 150, 150)
TAUTO = (185, 140, 40)

# ⚠ Les deux bornes de lecture. Elles ne decident rien -- l'AUC est publie tel quel -- mais
# elles disent au lecteur ou commence « ca suit » et ou commence « ca va contre ».
AUC_SUIT = 0.75
AUC_CONTRE = 0.35

# ⚠⚠ Nommee ici parce que la figure DOIT la signaler : le contraste d'encre est construit
# sur des percentiles d'encre, donc la couverture le retrouve par construction.
TAUTOLOGIQUES = ("couverture",)

NOMS = {
    "couverture": "coverage",
    "epaisseur_trait_px": "stroke thickness",
    "nettete_mediane": "peak sharpness",
    "hauteur_mediane_px": "component height",
    "composantes": "component count",
    "part_periodique": "line separability",
}


def x_auc(a: float) -> int:
    """L'AUC sur l'axe, borné à [0, 1]."""
    return GX + int(min(max(a, 0.0), 1.0) * GLARG)


def classer(nom: str, auc: float) -> tuple:
    """La couleur et le mot qui vont avec cet AUC."""
    if nom in TAUTOLOGIQUES:
        return TAUTO, "quasi-tautological"
    if auc >= AUC_SUIT:
        return SUIT, "tracks the contrast"
    if auc <= AUC_CONTRE:
        return CONTRE, "runs AGAINST it"
    return NEUTRE, ""


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("l'axe des AUC est croissant", x_auc(0.0) < x_auc(0.5) < x_auc(1.0))
    v("... et 0,50 tombe au milieu",
      abs(x_auc(0.5) - (GX + GLARG // 2)) <= 1, f"{x_auc(0.5)}")
    v("un AUC hors bornes reste dans le cadre",
      GX <= x_auc(-1.0) and x_auc(2.0) <= GX + GLARG)

    v("une grandeur qui suit est verte", classer("nettete_mediane", 0.80)[0] == SUIT)
    v("une grandeur qui va contre est rouge",
      classer("part_periodique", 0.32)[0] == CONTRE)
    v("une grandeur sans signal est grise", classer("composantes", 0.59)[0] == NEUTRE)
    # ⚠⚠ LA sonde qui compte : la couverture doit etre signalee comme tautologique MEME
    # avec un AUC excellent. Sans ce cas particulier, sa barre verte a 0,97 se lirait comme
    # la meilleure validation de la figure, alors qu'elle mesure deux fois la meme chose.
    coul, mot = classer("couverture", 0.97)
    v("la couverture est marquée quasi-tautologique malgré son AUC",
      coul == TAUTO and "tauto" in mot, f"{coul} / {mot}")

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    racine = Path(__file__).resolve().parents[2]
    ap.add_argument("--entree", type=Path, default=racine / "docs/typographie.json")
    ap.add_argument("--sortie", type=Path,
                    default=racine / "docs/images/45_typographie.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont

    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer d'abord typographie.py --json",
              file=sys.stderr)
        return 1
    d = json.loads(a.entree.read_text())
    cr = d.get("croisement_encre") or {}
    if not cr.get("grandeurs"):
        print("le fichier ne porte pas de croisement — relancer avec --encre",
              file=sys.stderr)
        return 1

    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    img = Image.new("RGB", (LARGEUR, HAUTEUR), FOND)
    g = ImageDraw.Draw(img)
    g.text((30, 22), "« Consistent with », measured — three quantities agree, one does not",
           font=f_t, fill=TEXTE)
    g.text((30, 46), f"{cr['n']} published ink maps of one scroll, split at their median "
                     f"published ink contrast", font=f_p, fill=(100, 100, 100))

    # ---- Panneau gauche : les AUC ------------------------------------------------------
    g.text((GX - 220, GY - 30), "does the quantity recover the contrast ranking?",
           font=f_n, fill=TEXTE)
    ordre = sorted(cr["grandeurs"].items(), key=lambda kv: -(kv[1]["auc"] or 0))
    bas = GY + len(ordre) * LIGNE
    x50 = x_auc(0.5)
    for t in (0.0, 0.5, 1.0):
        x = x_auc(t)
        g.line([x, GY - 8, x, bas], fill=(228, 228, 228) if t != 0.5 else (120, 120, 120))
        g.text((x - 10, bas + 6), f"{t:.1f}".replace(".", "."), font=f_p,
               fill=(110, 110, 110))
    g.text((x50 - 62, bas + 24), "0.50 = says nothing", font=f_p, fill=(120, 120, 120))

    for i, (nom, gr) in enumerate(ordre):
        y = GY + i * LIGNE
        auc = gr["auc"]
        coul, mot = classer(nom, auc)
        g.text((30, y - 6), NOMS.get(nom, nom), font=f_n, fill=TEXTE)
        x = x_auc(auc)
        g.rectangle([min(x, x50), y - 8, max(x, x50), y + 8], fill=coul)
        # ⚠ Le nombre se pose du cote OPPOSE a la barre : colle a son extremite, il
        # chevauchait le mot de verdict, et « 0.965 » se lisait « 0.96quasi-tauto ».
        g.text((x50 + 6 if x < x50 else x50 - 44, y - 7), f"{auc:.3f}", font=f_p,
               fill=coul)
        if mot:
            g.text((GX + GLARG + 16, y - 7), mot, font=f_p, fill=coul)

    # ---- Panneau droit : LES DONNEES SUR LESQUELLES L'AUC EST CALCULE ------------------
    # ⚠⚠ La premiere version tracait la couverture des 190 cartes des quatre rouleaux,
    # alors que l'AUC porte sur le contraste de 80 cartes d'un seul. Deux variables, deux
    # corpus : le nuage montait la ou le tableau dit que ca descend. Une figure qui
    # contredit son propre tableau est pire qu'aucune figure -- celle-ci trace desormais
    # exactement les couples apparies.
    g.text((DX, GY - 48), "the same 80 maps, contrast against separability",
           font=f_n, fill=TEXTE)
    pts = [(c["contraste"], c["part_periodique"]) for c in cr.get("couples", [])]
    if pts:
        cmax = max(p[0] for p in pts) or 1.0
        for i in range(5):
            yy = DY + int(i * DHAUT / 4)
            g.line([DX, yy, DX + DLARG, yy], fill=(238, 238, 238))
        for cx, cy in pts:
            px = DX + int(min(cx / cmax, 1.0) * DLARG)
            py = DY + DHAUT - int(min(max(cy, 0.0), 1.0) * DHAUT)
            g.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(70, 110, 170),
                      outline=(255, 255, 255))
        # ⚠⚠ Le nuage seul ne montre RIEN : une bonne partie des cartes sature a 1,0 et
        # forme une ligne au plafond, ce qui cache la pente. La mediane par quartile de
        # couverture la rend visible -- et le plafond est DIT, parce qu'un lecteur doit
        # savoir que la grandeur est bornee avant de lire une tendance.
        pts_tries = sorted(pts)
        q = max(1, len(pts_tries) // 4)
        milieux = []
        for i in range(4):
            lot = pts_tries[i * q:(i + 1) * q] if i < 3 else pts_tries[3 * q:]
            if not lot:
                continue
            mx = sorted(x for x, _ in lot)[len(lot) // 2]
            my = sorted(y for _, y in lot)[len(lot) // 2]
            milieux.append((DX + int(min(mx / cmax, 1.0) * DLARG),
                            DY + DHAUT - int(min(max(my, 0.0), 1.0) * DHAUT)))
        for j in range(len(milieux) - 1):
            g.line([*milieux[j], *milieux[j + 1]], fill=CONTRE, width=3)
        for mx, my in milieux:
            g.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=CONTRE,
                      outline=(255, 255, 255))
        satures = sum(1 for _, y in pts if y >= 0.999)
        g.text((DX, DY - 16), f"↑ share of windows with separable lines "
                              f"({satures} maps saturate at 1.0)", font=f_p,
               fill=(110, 110, 110))
        g.text((DX + DLARG // 2 - 62, DY + DHAUT + 12), "published ink contrast →",
               font=f_p, fill=(110, 110, 110))
        rho = (cr["grandeurs"].get("part_periodique") or {}).get("rho")
        g.text((DX + 6, DY + DHAUT - 22),
               f"red: median per contrast quartile" +
               (f"  ·  rho = {rho:+.3f}" if rho is not None else ""),
               font=f_p, fill=CONTRE)

    bas_txt = HAUTEUR - 74
    for i, t in enumerate((
            "⚠ coverage is quasi-tautological: the published contrast is built on ink "
            "percentiles, so a more inked map has both.",
            "* stroke thickness and peak sharpness are genuinely different quantities, "
            "and they agree with the contrast.",
            "⚠⚠ line separability runs against it — WEAKLY (rho = -0.27) and not "
            "monotonically: it falls over the first three quartiles, then flattens.")):
        g.text((30, bas_txt + i * 20), t, font=f_p,
               fill=CONTRE if i == 2 else TAUTO if i == 0 else SUIT)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{HAUTEUR})  {len(ordre)} grandeurs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
