#!/usr/bin/env python3
"""Le champ publié compte-t-il des feuilles ? — les autocorrélations, et leur contrôle.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat est **négatif**, et un résultat négatif se lit mal
en tableau : « autocorrélation radiale +0,302 contre tangentielle +0,311 » demande au lecteur de
croire sur parole que le second est un contrôle et non un second résultat. Deux courbes
superposées le montrent — si la radiale ne se détache pas de la tangentielle, il n'y a rien à
compter, et ça se voit avant d'être lu.

⭐⭐ ET LE PIC RETENU EST MARQUÉ SUR LA COURBE, avec le passage sous zéro qui le rend légitime.
C'est la correction que ce lot a payée : le maximum **global** d'une autocorrélation lisse est
toujours son plus petit décalage, donc la première version rendait « 2 cellules » partout — la
largeur de lissage du champ, et rien du tout sur les feuilles. Voir la courbe descendre, passer
sous zéro, puis remonter est ce qui distingue un retour d'une pente.

⚠⚠ LE PAS DE FEUILLE EST TRACÉ EN REPÈRE, pas en légende. Les périodes mesurées valent deux à
trois fois ce pas ; l'écart est le résultat, donc il doit être visible à côté de la mesure et non
récité en dessous.

⚠ Les nombres sont LUS dans `docs/mesures/le_champ_de_fibres.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_champ_de_fibres.py --verifier
    uv run python src/figures/figure_le_champ_de_fibres.py \\
        --sortie docs/images/75_le_champ_de_fibres.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (110, 116, 124)
ROUGE = (188, 68, 52)
VERT = (108, 160, 108)


def lots_dessinables(m: dict) -> list[dict]:
    """
    @brief Les fenêtres qui portent une courbe — les seules qu'on puisse dessiner.

    ⚠ Une fenêtre sans courbe n'est pas dessinée en blanc : elle est **absente**. Un panneau vide
    dans une rangée de trois se lit comme « ici le champ ne répond rien », ce qui est un énoncé
    sur le rouleau et non sur ce qui a été mesuré.
    """
    return [l for l in (m.get("lots") or [])
            if (l.get("periodicite") or {}).get("courbes", {}).get("radial_1")]


def separe(p: dict, marge: float = 0.1) -> bool:
    """
    @brief Cette fenêtre sépare-t-elle le radial du tangentiel ?

    ⚠ La marge existe parce qu'une différence de quelques millièmes entre deux autocorrélations
    prises sur soixante-trois échantillons n'est pas une séparation. Sans elle, la moitié des
    fenêtres « sépareraient » par le bruit.
    """
    return p["autocorrelation_radiale"] > p["autocorrelation_tangentielle"] + marge


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    lots = lots_dessinables(m)
    perios = [l["periodicite"] for l in lots]
    combien = sum(1 for p in perios if separe(p))
    um = [p["periode_radiale_um"] for p in perios if p["periode_radiale_cellules"]]
    pas = 150.0
    return [
        f"une feuille est une SURFACE : elle se repete en travers, pas le long — donc le "
        "tangentiel est le controle.",
        f"le radial ne le bat que sur {combien} fenetre(s) sur {len(perios)}.",
        f"et la ou une periode apparait elle vaut {min(um):.0f} a {max(um):.0f} um, "
        f"soit {min(um) / pas:.1f} a {max(um) / pas:.1f} pas de feuille — jamais un.",
        "donc ce champ voit des GROUPES de feuilles, et un nombre d'enroulement en compte une.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lots = lots_dessinables(m)
    if not lots:
        raise SystemExit("aucune fenêtre ne porte de courbe : rien à dessiner")

    larg, haut, marge, ecart = 300, 230, 44, 26
    L = marge * 2 + len(lots) * larg + (len(lots) - 1) * ecart
    H = 104 + haut + 56 + len(prose(m)) * 19 + 30
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    d.text((marge, 22), "le champ publie compte-t-il des feuilles ?", fill=TEXTE, font=gros)
    d.text((marge, 48), f"autocorrelation le long d'un rayon depuis l'axe publie, "
                        f"et le meme profil pris perpendiculairement", fill=DISCRET, font=moyen)
    d.text((marge, 68), f"niveau {m['niveau']} — {m['resolution_um']:.1f} µm/cellule, "
                        f"{m['cellules_par_pas']:.1f} cellules par pas de feuille",
           fill=DISCRET, font=petit)

    y0, y1 = 104, 104 + haut
    lo, hi = -0.4, 1.0
    for k, lot in enumerate(lots):
        p = lot["periodicite"]
        x0 = marge + k * (larg + ecart)
        d.rectangle([x0, y0, x0 + larg, y1], outline=(60, 60, 60))
        rad = p["courbes"]["radial_1"]
        tan = p["courbes"].get("tangentiel_1") or []
        n = max(len(rad), len(tan), 2)

        def px(i):
            return x0 + larg * i / (n - 1)

        def py(v):
            return y1 - (max(lo, min(hi, v)) - lo) / (hi - lo) * haut

        # ⚠ Le zéro est tracé le premier : c'est lui qui rend le pic lisible, parce qu'un
        # maximum n'est un RETOUR que s'il vient après une descente sous zéro.
        d.line([x0, py(0.0), x0 + larg, py(0.0)], fill=(90, 90, 90))
        d.text((x0 + 3, py(0.0) - 13), "0", fill=(90, 90, 90), font=petit)
        # ⚠⚠ Le pas de feuille en REPÈRE, pas en légende : l'écart entre lui et le pic est le
        # résultat, donc il se mesure à l'œil au lieu de se réciter.
        pas_cellules = m["cellules_par_pas"]
        if pas_cellules < n:
            xp = px(pas_cellules)
            for yy in range(y0, y1, 8):
                d.line([xp, yy, xp, yy + 4], fill=VERT)
            d.text((xp + 4, y0 + 4), "un pas", fill=VERT, font=petit)
        for serie, couleur in ((tan, GRIS), (rad, AMBRE)):
            pts = [(px(i), py(v)) for i, v in enumerate(serie)]
            for a, b in zip(pts, pts[1:]):
                d.line([a, b], fill=couleur, width=2)
        kpic = p["periode_radiale_cellules"]
        if 0 < kpic < n:
            xx, yy = px(kpic - 1), py(p["autocorrelation_radiale"])
            d.ellipse([xx - 4, yy - 4, xx + 4, yy + 4], outline=AMBRE, width=2)
            d.text((xx - 14, yy - 20), f"{p['periode_radiale_um']:.0f} µm",
                   fill=AMBRE, font=petit)
        gagne = separe(p)
        d.text((x0, y0 - 20), f"chunk ({p['cz']}, {p['cy']}, {p['cx']})",
               fill=TEXTE, font=moyen)
        d.text((x0, y1 + 8), f"radial {p['autocorrelation_radiale']:+.3f}  contre  "
                             f"tangentiel {p['autocorrelation_tangentielle']:+.3f}",
               fill=DISCRET, font=petit)
        d.text((x0, y1 + 24), "separe" if gagne else "ne separe PAS",
               fill=VERT if gagne else ROUGE, font=moyen)
    d.text((marge, y1 + 44), "ambre : radial   ·   gris : tangentiel (le controle)",
           fill=DISCRET, font=petit)

    bas = y1 + 62
    for j, ligne in enumerate(prose(m)):
        d.text((marge, bas + j * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"fenetres": len(lots), "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        print(f"  {'ok  ' if cond else 'ECHEC'}  {nom}" + (f"  — {detail}" if detail else ""))
        if not cond:
            echecs += 1

    def fenetre(cz, rad, tan, k, um):
        return {"periodicite": {"cz": cz, "cy": 0, "cx": 0,
                                "autocorrelation_radiale": rad,
                                "autocorrelation_tangentielle": tan,
                                "periode_radiale_cellules": k, "periode_radiale_um": um,
                                "courbes": {"radial_1": [1.0, 0.3, -0.2, rad, 0.0],
                                            "tangentiel_1": [1.0, 0.2, -0.1, tan, 0.0]}}}

    faux = {"niveau": 3, "resolution_um": 19.192, "cellules_par_pas": 7.82,
            "lots": [fenetre(71, 0.245, -0.069, 23, 441.4),
                     fenetre(74, 0.302, 0.311, 22, 422.2),
                     fenetre(35, 0.237, 0.397, 16, 307.1)]}
    v("les trois fenêtres sont dessinables", len(lots_dessinables(faux)) == 3)
    # ⚠⚠ LA MARGE EST CE QUI EMPÊCHE LE BRUIT DE « SÉPARER ». Sans elle, +0,302 contre +0,311
    # serait à un cheveu de basculer, et une fenêtre qui sépare par trois millièmes n'est pas une
    # fenêtre qui sépare.
    v("une fenêtre qui bat franchement le contrôle sépare",
      separe(faux["lots"][0]["periodicite"]))
    v("... et une qui perd contre lui ne sépare pas",
      not separe(faux["lots"][1]["periodicite"]))
    v("... et un écart de quelques millièmes non plus",
      not separe({"autocorrelation_radiale": 0.305,
                  "autocorrelation_tangentielle": 0.300}))
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle nomme le tangentiel comme le CONTRÔLE",
      any("controle" in l for l in lignes), str(lignes[0]))
    v("... et elle dit combien de fenêtres séparent",
      any("1 fenetre(s) sur 3" in l for l in lignes), str(lignes[1]))
    # ⚠ La conversion en pas de feuille est faite dans la prose : « 441 µm » ne dit rien à qui ne
    # se souvient pas du pas, et c'est l'écart qui est le résultat.
    v("... et elle convertit la période en pas de feuille",
      any("pas de feuille" in l for l in lignes), str(lignes[2]))
    # ⚠ Une mesure sans courbe ne produit pas un panneau vide : elle refuse.
    v("une mesure sans courbe ne produit pas de figure",
      _leve(lambda: dessiner({"niveau": 3, "resolution_um": 19.2, "cellules_par_pas": 7.8,
                              "lots": []}, Path("/tmp/x.png"))))

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
                   default=RACINE / "docs" / "mesures" / "le_champ_de_fibres.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_champ_de_fibres.png")
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
