#!/usr/bin/env python3
"""La chaîne GLISSE hors de la feuille connue — elle n'y saute pas.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** Deux pannes
donnent le même « la chaîne s'écarte » : un **saut de spire**, qui est une marche brusque
d'un écart inter-feuilles, et un **glissement**, qui est une dérive lente et régulière. Elles
n'ont pas le même remède — l'une se répare par un décalage d'une spire le long de la normale,
l'autre par une correction de la dérive. Tracer l'écart CONTRE la distance parcourue montre
laquelle des deux se produit : une marche, ou une pente.

⭐ **Les deux bandes sont ce qui fait de l'écart un verdict.** `carte_segments.py` publie les
seuils du dépôt : sous **40 µm** deux morceaux sont la MÊME feuille et se raccordent ; au-delà
de **250 µm** ce sont des feuilles voisines qu'il ne faut surtout pas fusionner. Sans elles,
« 69 µm » est un nombre ; avec elles, c'est une position dans une échelle déjà argumentée.

⚠ L'axe des abscisses est la distance PARCOURUE, pas l'indice du maillon. Les maillons ont un
pas fixe, donc les deux sont proportionnels ici — mais un jour où le pas changera, l'indice
mentirait sur la distance, et c'est la distance qui a un sens physique.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import police  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
ECART = (176, 62, 62)
COUVERT = (86, 104, 132)
MEME = (120, 160, 110)
VOISINE = (196, 140, 60)

MEME_FEUILLE_UM = 40.0
VOISINES_UM = 250.0
"""⚠ Les seuils viennent de `src/commun/carte_segments.py` et **ne sont pas redéfinis ici**
au sens du jugement : ce module les recopie pour dessiner, et la batterie vérifie qu'ils
s'accordent. Deux valeurs de « même feuille » finiraient par ne pas dire la même chose."""


def lire(chemin: Path) -> dict:
    """Le JSON de `couverture_publiee.py`. ⚠ Refuse un fichier sans maillons plutôt que de
    dessiner un cadre vide, qui se lit comme « la mesure ne dit rien »."""
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("maillons"):
        raise ValueError(f"{chemin} ne porte aucun maillon")
    return d


def series(d: dict) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """(parcouru µm, |écart signé| µm) et (parcouru µm, part couverte %)."""
    um = d.get("um_par_voxel", 2.4)
    ecart, couvert = [], []
    for m in d["maillons"]:
        x = float(m["parcouru_um"])
        if "ecart_signe_median_vox" in m:
            ecart.append((x, abs(float(m["ecart_signe_median_vox"])) * um))
        couvert.append((x, float(m["part_sur_le_maillage"]) * 100.0))
    return ecart, couvert


def dessiner(d: dict, sortie: Path) -> dict:
    p, pp, pg = police(13, 11, 15)
    ecart, couvert = series(d)
    xmax = max(x for x, _ in ecart + couvert) or 1.0
    ymax = max(VOISINES_UM * 1.12, max(y for _, y in ecart) * 1.3)

    marge, larg, haut = 92, 520, 330
    L, H = marge + larg + 232, marge + haut + 150
    img = Image.new("RGB", (L, H), FOND)
    dr = ImageDraw.Draw(img)

    def X(v):
        return marge + int(v / (xmax * 1.06) * larg)

    def Y(v):
        return marge + haut - int(v / ymax * haut)

    dr.text((marge, marge - 54), "La chaîne GLISSE hors de la feuille connue — elle n'y saute pas",
            fill=ENCRE, font=pg)
    dr.text((marge, marge - 33),
            "écart médian à la surface publiée, le long de sa normale, contre la distance parcourue",
            fill=GRIS, font=pp)

    # Les deux bandes de verdict, dessinees AVANT la courbe pour rester dessous.
    for seuil, couleur, texte in ((MEME_FEUILLE_UM, MEME, "même feuille (< 40 µm)"),
                                  (VOISINES_UM, VOISINE, "feuilles voisines (> 250 µm)")):
        y = Y(seuil)
        dr.line([(marge, y), (marge + larg, y)], fill=couleur, width=1)
        dr.text((marge + larg + 8, y - 7), texte, fill=couleur, font=pp)

    dr.line([(marge, marge + haut), (marge + larg, marge + haut)], fill=TRAIT)
    dr.line([(marge, marge), (marge, marge + haut)], fill=TRAIT)
    dr.text((marge + larg // 2 - 70, marge + haut + 30), "distance parcourue (µm)",
            fill=GRIS, font=pp)
    for t in (0, 1000, 2000, 3000, 4000, 5000):
        if t > xmax:
            break
        dr.line([(X(t), marge + haut), (X(t), marge + haut + 5)], fill=TRAIT)
        dr.text((X(t) - 12, marge + haut + 10), str(t), fill=GRIS, font=pp)
    for t in (0, 50, 100, 150, 200, 250):
        if t > ymax:
            break
        dr.line([(marge - 5, Y(t)), (marge, Y(t))], fill=TRAIT)
        dr.text((marge - 34, Y(t) - 7), str(t), fill=GRIS, font=pp)
    dr.text((10, marge + haut // 2 - 24), "écart", fill=GRIS, font=pp)
    dr.text((10, marge + haut // 2 - 8), "(µm)", fill=GRIS, font=pp)

    if len(ecart) > 1:
        dr.line([(X(x), Y(y)) for x, y in ecart], fill=ECART, width=2)
    for x, y in ecart:
        dr.ellipse([X(x) - 3, Y(y) - 3, X(x) + 3, Y(y) + 3], fill=ECART)

    # ⚠⚠ La part encore COUVERTE a sa PROPRE bande sous le cadre, et pas des barres dans
    # le cadre : superposees a la courbe elles se lisaient comme une seconde serie sur
    # l axe des ecarts, c est-a-dire comme des microns. Deux grandeurs, deux echelles, deux
    # endroits.
    base, hb = marge + haut + 62, 34
    dr.line([(marge, base + hb), (marge + larg, base + hb)], fill=TRAIT)
    for x, y in couvert:
        h = max(1, int(y / 100.0 * hb))
        dr.rectangle([X(x) - 5, base + hb - h, X(x) + 5, base + hb], fill=COUVERT)
    dr.text((marge - 78, base + hb - 26), "part encore", fill=COUVERT, font=pp)
    dr.text((marge - 78, base + hb - 12), "SUR la surface", fill=COUVERT, font=pp)
    dr.text((marge + larg + 8, base + hb - 26),
            f"{couvert[0][1]:.0f} %  →  {couvert[-1][1]:.0f} %", fill=COUVERT, font=pp)

    fin = ecart[-1]
    dr.ellipse([X(fin[0]) - 4, Y(fin[1]) - 4, X(fin[0]) + 4, Y(fin[1]) + 4], fill=ECART)
    dr.text((X(fin[0]) - 128, Y(fin[1]) - 24),
            f"{fin[1]:.0f} µm après {fin[0] / 1000:.2f} mm", fill=ECART, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"points": len(ecart), "ecart_final_um": fin[1], "parcouru_final_um": fin[0]}


def verifier() -> int:
    """Le dessin se garde lui-même."""
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ Les seuils dessines doivent etre CEUX du depot. Une figure qui trace sa propre
    # frontiere de « meme feuille » rendrait un verdict que le code ne rend pas.
    sys.path.insert(0, str(RACINE / "src" / "commun"))
    import carte_segments as cs
    v("le seuil « même feuille » est celui du dépôt", MEME_FEUILLE_UM == cs.MEME_FEUILLE_UM,
      f"{MEME_FEUILLE_UM} contre {cs.MEME_FEUILLE_UM}")
    v("... et le seuil « voisines » aussi", VOISINES_UM == cs.VOISINES_UM,
      f"{VOISINES_UM} contre {cs.VOISINES_UM}")

    d = {"um_par_voxel": 2.4, "maillons": [
        {"parcouru_um": 96.0, "part_sur_le_maillage": 1.0, "ecart_signe_median_vox": -0.1},
        {"parcouru_um": 1920.0, "part_sur_le_maillage": 0.454,
         "ecart_signe_median_vox": -11.7},
        {"parcouru_um": 5760.0, "part_sur_le_maillage": 0.272,
         "ecart_signe_median_vox": -28.8}]}
    e, c = series(d)
    v("l'écart est rendu en µm, en valeur absolue", abs(e[-1][1] - 28.8 * 2.4) < 1e-9,
      str(e[-1]))
    v("... et la couverture en pourcents", abs(c[-1][1] - 27.2) < 1e-9, str(c[-1]))
    v("... et le premier maillon est presque nul", e[0][1] < 1.0, str(e[0]))

    try:
        lire_vide = Path(tempfile.mkstemp(suffix=".json")[1])
        lire_vide.write_text('{"maillons": []}', encoding="utf-8")
        lire(lire_vide)
        v("un JSON sans maillon est REFUSÉ", False)
    except ValueError:
        v("un JSON sans maillon est REFUSÉ", True)

    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "f.png"
        r = dessiner(d, out)
        v("la figure est écrite", out.is_file())
        v("... avec le bon nombre de points", r["points"] == 3, str(r))
        im = Image.open(out)
        # ⚠ `getdata` est deprecie ; `figure_commune._pixels` connait les deux formes.
        f = getattr(im, "get_flattened_data", None) or im.getdata
        couleurs = set(f())
        v("... et elle n'est pas vide", len(couleurs) > 4, str(len(couleurs)))
        # ⚠ La bande « voisines » doit etre DANS le cadre, sinon le verdict qu elle porte
        # n est pas lisible et la figure ne dit plus ou l ecart se situe.
        v("la bande « feuilles voisines » est tracée", VOISINE in couleurs)
        v("... et la bande « même feuille » aussi", MEME in couleurs)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--entree", type=Path,
                   default=RACINE / "docs/mesures/couverture_publiee.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/44_couverture_publiee.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = dessiner(lire(a.entree), a.sortie)
    print(f"{r['points']} maillons, écart final {r['ecart_final_um']:.0f} µm "
          f"à {r['parcouru_final_um'] / 1000:.2f} mm  →  {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
