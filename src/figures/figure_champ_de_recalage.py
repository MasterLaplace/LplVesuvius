#!/usr/bin/env python3
"""Le champ de décalage résiduel, et la validation croisée qui le rend crédible.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat tient en deux affirmations qu'un tableau sépare mal :
l'affine globale laisse un résidu **structuré** (il a une direction, il n'est pas du bruit), et
ce résidu est **géométrique** (un champ qui n'a jamais vu d'encre restaure l'accord de l'encre).
Des flèches montrent la première d'un coup ; une paire de barres montre la seconde.

⭐⭐ LES FLÈCHES SONT À L'ÉCHELLE ET LEUR ÉCHELLE EST ÉCRITE. Un champ de déplacement dessiné à
une échelle muette se lit comme on veut : la longueur d'une flèche doit se convertir en
millimètres sans deviner.

⚠ Ne sont dessinés que les carreaux **portant un bord** — les seuls où le décalage est contraint.
Un carreau plein se ressemble à lui-même partout, donc son optimum est arbitraire, et le dessiner
suggérerait une mesure là où il n'y en a pas.

⚠ Les nombres sont LUS dans `docs/mesures/le_recalage_des_etiquettes.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_champ_de_recalage.py --verifier
    uv run python src/figures/figure_champ_de_recalage.py \\
        --sortie docs/images/75_champ_de_recalage.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
BLEU = (86, 148, 196)
ROUGE = (188, 68, 52)

CELLULE_UM = 17.7
"""Ce que vaut une cellule de la grille réduite, en micromètres — 8 × 2,215 µm.

⚠ Écrit une fois et utilisé partout : une figure qui convertirait en millimètres à deux endroits
avec deux facteurs finirait par se contredire elle-même dans sa propre légende."""


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    c, v = m["champ_local"], m["validation_du_champ"]
    return [
        f"l'affine globale laisse un residu de {c['norme_mediane']:.0f} cellules en mediane "
        f"({c['norme_mediane'] * CELLULE_UM / 1000:.1f} mm), jusqu'a "
        f"{c['norme_max']:.0f} ({c['norme_max'] * CELLULE_UM / 1000:.1f} mm).",
        f"le champ est estime sur {c['retenus']} carreaux portant un BORD, sans jamais voir "
        "d'encre.",
        f"et il remonte l'accord de l'encre de {v['auc_sans_champ']:.3f} a "
        f"{v['auc_avec_champ']:.3f} : le residu est bien geometrique.",
        "il n'atteint pas l'optimum trouve EN REGARDANT l'encre, et c'est la bonne nouvelle.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    champ = m["champ_local"]
    carreaux = champ["carreaux"]
    if len(carreaux) < 3:
        raise SystemExit("moins de trois carreaux : rien à dessiner")

    cote, marge = 460, 44
    L, H = marge * 2 + cote + 420, 96 + cote + 40 + len(prose(m)) * 19 + 30
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    d.text((marge, 22), "le residu que l'affine globale ne corrige pas", fill=TEXTE, font=gros)
    d.text((marge, 48), f"{m['segment']} — un carreau par bord du fragment ; "
                        "les carreaux pleins ne contraignent rien", fill=DISCRET, font=moyen)

    lignes = [c["i"] for c in carreaux] + [c["j"] for c in carreaux]
    hi = max(lignes) + champ["pas"]
    y0 = 96
    d.rectangle([marge, y0, marge + cote, y0 + cote], outline=(60, 60, 60))

    # ⚠⚠ L'ÉCHELLE DES FLÈCHES EST CHOISIE POUR QUE LA PLUS LONGUE TIENNE, et elle est écrite en
    # dessous. Sans ça une flèche est un ornement.
    plus_long = max(math.hypot(c["di"], c["dj"]) for c in carreaux) or 1.0
    facteur = (champ["pas"] * 0.9) * (cote / hi) / plus_long
    for c in carreaux:
        x = marge + c["j"] * cote / hi
        y = y0 + c["i"] * cote / hi
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=DISCRET)
        x2 = x + c["dj"] * facteur
        y2 = y + c["di"] * facteur
        norme = math.hypot(c["di"], c["dj"])
        couleur = ROUGE if norme > champ["norme_p90"] else AMBRE
        d.line([x, y, x2, y2], fill=couleur, width=2)
        d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], outline=couleur)
    d.text((marge, y0 + cote + 8),
           f"la plus longue fleche vaut {plus_long * CELLULE_UM / 1000:.1f} mm de decalage "
           f"({plus_long:.0f} cellules) ; en rouge, au-dela du 9e decile",
           fill=DISCRET, font=petit)

    # ---- la validation croisée, deux barres ------------------------------------------
    v = m["validation_du_champ"]
    bx, by, bh = marge + cote + 60, y0 + 40, 220
    d.text((bx, by - 30), "validation croisee sur l'encre", fill=TEXTE, font=moyen)
    lo, hi_ = 0.3, 0.8
    for k, (nom, val, couleur) in enumerate((("sans le champ", v["auc_sans_champ"], DISCRET),
                                             ("avec le champ", v["auc_avec_champ"], BLEU))):
        x = bx + k * 130
        haut = (val - lo) / (hi_ - lo) * bh
        d.rectangle([x, by + bh - haut, x + 78, by + bh], fill=couleur)
        d.text((x, by + bh + 8), nom, fill=DISCRET, font=petit)
        d.text((x, by + bh - haut - 18), f"{val:.3f}", fill=couleur, font=moyen)
    yh = by + bh - (0.5 - lo) / (hi_ - lo) * bh
    d.line([bx - 8, yh, bx + 220, yh], fill=(150, 120, 60))
    d.text((bx + 226, yh - 7), "hasard", fill=(150, 120, 60), font=petit)

    bas = y0 + cote + 34
    for j, ligne in enumerate(prose(m)):
        d.text((marge, bas + j * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"carreaux": len(carreaux), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if cond else 'ECHEC'}  {nom}" + (f"  — {detail}" if detail else ""))
        if not cond:
            echecs += 1

    faux = {"segment": "s",
            "champ_local": {"pas": 128, "retenus": 34, "norme_mediane": 60.0,
                            "norme_p90": 152.0, "norme_max": 160.0, "dice_median": 0.951,
                            "carreaux": [{"i": 0, "j": 0, "di": 10, "dj": 0, "dice": 0.9,
                                          "occupation": 0.5},
                                         {"i": 128, "j": 128, "di": -60, "dj": 30, "dice": 0.9,
                                          "occupation": 0.5},
                                         {"i": 256, "j": 0, "di": 160, "dj": -20, "dice": 0.9,
                                          "occupation": 0.5}]},
            "validation_du_champ": {"auc_sans_champ": 0.418, "auc_avec_champ": 0.612,
                                    "distance_au_carreau": 277.0,
                                    "carreau": {"di": -142, "dj": -30}}}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    # ⚠⚠ LA CONVERSION EN MILLIMÈTRES EST FAITE UNE FOIS : 60 cellules × 17,7 µm = 1,1 mm. Une
    # figure qui convertirait à deux endroits avec deux facteurs se contredirait dans sa légende.
    v("... et elle convertit les cellules en millimètres",
      any("1.1 mm" in l for l in lignes), str(lignes[0]))
    v("... et elle dit que le champ n'a jamais vu d'encre",
      any("sans jamais voir" in l for l in lignes), str(lignes[1]))
    v("... et que la validation croisée remonte l'accord",
      any("0.418 a 0.612" in l for l in lignes), str(lignes[2]))
    # ⚠ La bonne nouvelle est que le champ N'ATTEINT PAS l'optimum ajusté sur l'encre : un champ
    # indépendant qui l'égalerait serait suspect. La figure doit le dire.
    v("... et qu'il n'atteint pas l'optimum ajusté sur l'encre",
      any("bonne nouvelle" in l for l in lignes), str(lignes[-1]))
    v("moins de trois carreaux ne produit pas de figure",
      _leve(lambda: dessiner({**faux, "champ_local": {**faux["champ_local"],
                                                      "carreaux": [{"i": 0, "j": 0, "di": 1,
                                                                    "dj": 1, "dice": 1.0,
                                                                    "occupation": 0.5}]}},
                             Path("/tmp/x.png"))))
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_recalage_des_etiquettes.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_champ_de_recalage.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
