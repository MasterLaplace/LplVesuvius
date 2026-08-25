#!/usr/bin/env python3
"""Les 35,6 Gio de contenu identique de `data/`, et POURQUOI ils le sont.

⚠⚠ **Ce que cette figure établit**, et c'est plus que du disque : **70 % du doublonnage n'est
pas un doublon de campagne, c'est une FENÊTRE IMBRIQUÉE.** Une fenêtre de 31 couches est le
centre d'une fenêtre de 81 rendue au même endroit, donc la tranche `i` de l'une **est** la
tranche `i + 25` de l'autre — le même fichier, au bit près. Les paires trouvées sont
exactement la série de convergence du dépôt : (31, 81) et (41, 161).

⭐ La conséquence n'est donc pas 25 Gio de disque, c'est **le temps de rendu de toute campagne
de convergence** : rendre n=161 produit déjà n=81 et n=41. Un cache indexé sur
(surface, niveau, N) ne peut pas le voir, puisque N diffère — seul un cache par TRANCHE le
verrait.

⚠ Mesuré par HACHAGE, jamais par nom : le proxy « même nom + même taille » que le plan
utilisait annonçait 17,4 Go, et il se trompait dans les deux sens — il comptait des chunks
zarr homonymes de contenu différent, et il ratait ces tranches-là, qui ne portent pas le même
nom.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/depot/contenu_en_double.py data --json docs/contenu_en_double.json
    uv run python src/figures/figure_doublons.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GIO = 1073741824
LARGEUR = 1020
FOND, ENCRE, GRIS = (255, 255, 255), (25, 25, 28), (150, 150, 155)
AMBRE, BLEU, PALE = (214, 141, 40), (44, 90, 160), (205, 210, 218)

LIBELLES = {
    "fenetres_imbriquees": "fenêtres imbriquées — la tranche i de n=31 EST la tranche i+25 de n=81",
    "meme_fenetre": "même fenêtre, deux campagnes — le doublon que le cache par contenu supprime",
    "autre": "autre contenu identique",
}
COULEURS = {"fenetres_imbriquees": AMBRE, "meme_fenetre": BLEU, "autre": PALE}


def parts(rapport: dict) -> list[tuple[str, int]]:
    """Les motifs, du plus coûteux au moins coûteux. ⚠ Un motif absent vaut zéro, pas rien."""
    m = dict(rapport.get("par_motif", {}))
    for connu in LIBELLES:
        m.setdefault(connu, 0)
    return sorted(m.items(), key=lambda kv: -kv[1])


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    r = {"par_motif": {"autre": 10, "fenetres_imbriquees": 25}, "recuperable": 35}
    p = parts(r)
    v("les motifs sortent du plus coûteux au moins coûteux",
      [x[0] for x in p][:2] == ["fenetres_imbriquees", "autre"])
    # ⚠ Un motif que la mesure n'a pas trouvé vaut ZÉRO, et il doit apparaître : son absence
    # de la figure se lirait comme « on n'a pas regardé », ce qui n'est pas la même chose.
    v("un motif absent de la mesure vaut zéro et reste affiché",
      dict(p).get("meme_fenetre") == 0 and len(p) == 3)
    v("chaque motif connu a un libellé", all(k in LIBELLES for k, _ in p))
    v("... et une couleur", all(k in COULEURS for k, _ in p))
    v("la somme des parts est le total", sum(x[1] for x in p) == r["recuperable"])
    v("un rapport sans motifs ne fait pas planter", len(parts({})) == 3)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    racine = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entree", type=Path, default=racine / "docs/contenu_en_double.json")
    ap.add_argument("--sortie", type=Path, default=racine / "docs/images/56_doublons.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.entree.is_file():
        print(f"absent : {a.entree} — lancer contenu_en_double.py --json", file=sys.stderr)
        return 1
    r = json.loads(a.entree.read_text(encoding="utf-8"))
    p = parts(r)
    total = sum(x[1] for x in p)

    from PIL import Image, ImageDraw, ImageFont

    def police(t):
        for n in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
            try:
                return ImageFont.truetype(n, t)
            except OSError:
                continue
        return ImageFont.load_default()

    hauteur = 128 + 58 * len(p) + 96
    im = Image.new("RGB", (LARGEUR, hauteur), FOND)
    d = ImageDraw.Draw(im)
    f_t, f_x, f_p = police(21), police(14), police(12)

    d.text((40, 26), f"{total / GIO:.1f} Gio de contenu identique dans data/ — mesurés par hachage",
           font=f_t, fill=ENCRE)
    d.text((40, 56), f"{r.get('groupes', 0)} groupes  ·  {r.get('fichiers_vus', 0)} fichiers vus  ·  "
                     f"{r.get('hachages_complets', 0)} hachages complets seulement",
           font=f_x, fill=GRIS)

    # Une barre unique, empilée : ce qui compte est la PART, pas la valeur absolue.
    x, y = 40, 100
    larg = LARGEUR - 80
    for motif, octets in p:
        if total and octets:
            w = larg * octets / total
            d.rectangle([x, y, x + w, y + 30], fill=COULEURS[motif])
            x += w
    y += 52

    for motif, octets in p:
        d.rectangle([40, y + 2, 56, y + 16], fill=COULEURS[motif])
        part = 100.0 * octets / total if total else 0.0
        d.text((66, y), f"{octets / GIO:5.2f} Gio  ({part:4.1f} %)", font=f_x, fill=ENCRE)
        d.text((230, y + 1), LIBELLES[motif], font=f_p, fill=GRIS)
        y += 58

    d.text((40, y + 6),
           "⚠ Le gain des fenêtres imbriquées n'est pas du disque, c'est du TEMPS DE RENDU :",
           font=f_x, fill=ENCRE)
    d.text((40, y + 28),
           "rendre n=161 produit déjà n=81 et n=41. Un cache indexé sur (surface, niveau, N) "
           "ne peut pas le voir.", font=f_p, fill=GRIS)
    d.text((40, y + 50),
           "Le proxy « même nom + même taille » annonçait 17,4 Go : il comptait des homonymes "
           "et ratait ces tranches-ci.", font=f_p, fill=GRIS)

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(a.sortie)
    print(f"{total / GIO:.2f} Gio répartis en {len(p)} motifs  →  {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
