#!/usr/bin/env python3
"""Aucun seuil ne sépare les feuilles — l'écart entre ce qu'on mesure et ce qu'on attendrait.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat est un **écart entre deux nombres**, et un
tableau le montre mal : 93 à 100 % contre 14 %, à six seuils et sur deux régions, se lit comme
une liste. Une bande par seuil, avec le repère de l'attente tracé en travers, le montre d'un
coup — et le repère n'est pas une valeur choisie, c'est @f$1/n@f$ où @f$n@f$ est le nombre de
feuilles que le chunk traverse.

⭐⭐ **Les coupes sont là pour la raison inverse de celle qu'on croit** : elles montrent que le
scan porte bel et bien une structure lamellaire visible à l'œil. C'est ce qui rend le résultat
non trivial — ce n'est pas « il n'y a rien à voir », c'est « ce qu'on voit ne se sépare pas ».

⚠ La part de matière est tracée à côté : sans elle, un lecteur pourrait croire que les seuils
hauts fabriquent des morceaux en vidant le volume. À 144 il reste encore 42 à 50 % de matière.

⚠ Les nombres sont LUS dans `docs/mesures/le_seuil_ne_separe_rien.json` et les coupes dans
`docs/mesures/coupes_du_seuil/`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_seuil_ne_separe_rien.py --verifier
    uv run python src/figures/figure_le_seuil_ne_separe_rien.py \\
        --sortie docs/images/79_le_seuil_ne_separe_rien.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (70, 118, 160)
VERT = (52, 122, 72)
GRIS = (206, 206, 204)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    parts = [l["part_de_la_plus_grosse"]
             for r in m["regions"] for l in r["balayage"]]
    return [
        f"a tous les seuils et sur les deux regions, le plus gros morceau tient "
        f"{min(parts) * 100:.0f} a {max(parts) * 100:.0f} % de la matiere.",
        f"des feuilles separees en mettraient {m['part_attendue_si_separees'] * 100:.0f} % : "
        f"un chunk de {m['cote']} voxels de {m['voxel_um']:g} um traverse "
        f"{m['feuilles_traversees']:g} feuilles a {m['pas_um']:g} um de pas.",
        "le repere n'est donc pas un seuil choisi, c'est la geometrie du rouleau.",
        "une isosurface affirmerait une frontiere que le scan n'a jamais resolue.",
    ]


def panneau_coupe(art, toile, chemin: Path, x: int, y: int, cote: int, titre: str, petit):
    """La coupe brute, à échelle de gris fixée sur SES propres percentiles."""
    import numpy as np
    from PIL import Image

    plan = np.load(chemin).astype(np.float32)
    vif = plan[plan > 0]
    bas, haut = (float(np.percentile(vif, 2)), float(np.percentile(vif, 98))) if vif.size \
        else (0.0, 1.0)
    img = np.clip((plan - bas) / max(haut - bas, 1e-9), 0.0, 1.0)
    vue = Image.fromarray((img * 255).astype("uint8"), mode="L").convert("RGB")
    toile.paste(vue.resize((cote, cote), Image.LANCZOS), (x, y))
    art.rectangle([x - 1, y - 1, x + cote, y + cote], outline=GRIS)
    art.text((x, y + cote + 6), titre, fill=DISCRET, font=petit)


def dessiner(m: dict, coupes: Path, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    regions = m["regions"]
    if not regions:
        raise SystemExit("aucune région dans la mesure")
    attendue = m["part_attendue_si_separees"]
    n_seuils = len(regions[0]["balayage"])

    cote_coupe, marge, ecart = 200, 26, 30
    barre, colonne, ligne_h = 250, 430, 48
    largeur = marge * 2 + cote_coupe + ecart + colonne * len(regions) \
        + ecart * (len(regions) - 1)
    lignes = prose(m)
    haut_bloc = max(cote_coupe * len(regions) + 26 * len(regions),
                    n_seuils * ligne_h + 30)
    hauteur = 88 + haut_bloc + 34 + len(lignes) * 19 + 26
    toile = Image.new("RGB", (largeur, hauteur), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Aucun seuil ne separe les feuilles", fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['volume'].split('/')[0]}, niveau {m['niveau']}, "
             f"chunks de {m['cote']}³ a {m['voxel_um']:g} um", fill=DISCRET, font=moyen)

    y0 = 84
    for i, reg in enumerate(regions):
        c = coupes / f"coupe_{reg['chunk'][0]}_{reg['chunk'][1]}_{reg['chunk'][2]}.npy"
        if not c.is_file():
            raise SystemExit(f"coupe absente : {c}")
        panneau_coupe(art, toile, c, marge, y0 + i * (cote_coupe + 26), cote_coupe,
                      f"rayon {reg['rayon_vox'] * m['voxel_um'] / 1000:.1f} mm — "
                      "la matiere brute", petit)

    for i, reg in enumerate(regions):
        x0 = marge + cote_coupe + ecart + i * (colonne + ecart)
        art.text((x0, y0 - 22),
                 f"rayon {reg['rayon_vox'] * m['voxel_um'] / 1000:.1f} mm  "
                 f"(chunk {reg['chunk']})", fill=TEXTE, font=moyen)
        bx = x0 + 62
        for k, l in enumerate(reg["balayage"]):
            y = y0 + 8 + k * ligne_h
            art.text((x0, y), f"seuil {l['seuil']}", fill=DISCRET, font=petit)
            art.rectangle([bx, y - 2, bx + barre, y + 14], outline=GRIS)
            art.rectangle([bx, y - 2, bx + int(barre * l["part_de_la_plus_grosse"]), y + 14],
                          fill=AMBRE)
            # ⚠⚠ Le repère de l'attente, tracé DANS la barre : sans lui l'ambre remplie se
            # lit comme « beaucoup », alors que ce qui compte est « beaucoup PAR RAPPORT A ».
            xa = bx + int(barre * attendue)
            art.line([xa, y - 8, xa, y + 20], fill=VERT, width=2)
            art.text((bx + barre + 10, y),
                     f"{l['part_de_la_plus_grosse'] * 100:.1f} %", fill=TEXTE, font=moyen)
            # ⚠ La part de matière est SOUS la barre et non après : sans elle un lecteur
            # croirait que les seuils hauts fabriquent des morceaux en vidant le volume.
            art.text((bx, y + 18),
                     f"matiere {l['part_matiere'] * 100:.1f} %  ·  "
                     f"{l['grandes']} morceau" + ("x" if l["grandes"] > 1 else ""),
                     fill=DISCRET, font=petit)

    yv = y0 + haut_bloc + 6
    xa = marge + cote_coupe + ecart + 62 + int(barre * attendue)
    art.line([xa, yv - 10, xa, yv + 2], fill=VERT, width=2)
    art.text((xa + 8, yv - 8),
             f"le trait vert vaut {attendue * 100:.0f} % — ce que pesera le plus gros morceau "
             "SI les feuilles sont separees", fill=VERT, font=petit)

    bas = hauteur - len(lignes) * 19 - 14
    for j, l in enumerate(lignes):
        art.text((marge, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"regions": len(regions), "seuils": n_seuils, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"volume": "PHerc0172/volumes/x.zarr", "niveau": 0, "cote": 128, "voxel_um": 7.91,
            "pas_um": 142.8, "feuilles_traversees": 7.09, "part_attendue_si_separees": 0.1411,
            "regions": [{"chunk": [82, 25, 33], "rayon_vox": 64, "moyenne": 149.7,
                         "ecart_type": 25.1, "un_seuil_separe": False,
                         "balayage": [{"seuil": 128, "part_matiere": 0.77, "faces": 803748,
                                       "grandes": 1, "plus_grosse": 1, "total": 1,
                                       "part_de_la_plus_grosse": 1.0},
                                      {"seuil": 144, "part_matiere": 0.496, "faces": 606528,
                                       "grandes": 48, "plus_grosse": 1, "total": 48,
                                       "part_de_la_plus_grosse": 0.973}]}],
            "un_seuil_separe_quelque_part": False}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle donne l'etendue mesuree, pas un seul point",
      any("97 a 100 %" in x for x in lignes), str(lignes[0]))
    # ⚠⚠ Le repère DOIT être présenté comme dérivé : s'il passait pour un seuil choisi, tout
    # le résultat se lirait comme un réglage. La figure doit le dire en toutes lettres.
    v("... et elle dit que le repere est DERIVE de la geometrie",
      any("geometrie du rouleau" in x for x in lignes)
      and any("traverse" in x for x in lignes), str(lignes[1:3]))
    v("... et elle conclut sur ce que ca interdit",
      any("isosurface" in x for x in lignes), str(lignes[-1]))

    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    # ⚠ Une coupe absente est un REFUS, pas un panneau vide : un panneau vide se lirait comme
    # « il n'y a rien dans ce chunk », soit exactement le contraire de ce que la figure établit.
    v("une coupe absente est refusée, pas dessinée en blanc",
      _leve(lambda: dessiner(faux, d, d / "x.png")))
    v("une mesure sans région est refusée",
      _leve(lambda: dessiner({**faux, "regions": []}, d, d / "x.png")))
    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
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
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_seuil_ne_separe_rien.json")
    p.add_argument("--coupes", type=Path,
                   default=RACINE / "docs" / "mesures" / "coupes_du_seuil")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "79_le_seuil_ne_separe_rien.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.coupes, a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
