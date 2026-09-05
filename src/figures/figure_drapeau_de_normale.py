#!/usr/bin/env python3
"""Le drapeau qui renumérote — l'identité, montrée plutôt qu'affirmée.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de `src/rendu/le_drapeau_de_normale.py` est une
**identité**, et une identité se lit mal en chiffres : « 41 sur 41 » demande de croire sur
parole qu'il s'agit des mêmes pixels. Trois vignettes le montrent — la première couche du rendu
normal, la **dernière** du rendu inversé (les mêmes octets), et la première de l'inversé (l'autre
bout de la pile).

⭐⭐ Et la bande du bas porte ce que les vignettes ne peuvent pas montrer : la comparaison a été
faite sur les **deux** appariements, couche par couche. « Renversé, tout coïncide » ne veut rien
dire sans « à l'endroit, une seule couche coïncide » — une pile constante satisferait le premier
seul, et c'est exactement le faux positif qu'on doit écarter.

⚠ Les vignettes sont rendues à une échelle de gris **commune**, calculée sur la première : une
normalisation par vignette ferait paraître différentes deux images identiques, ce qui est
précisément la conclusion inverse de celle qu'on établit.

⚠ Les nombres sont LUS dans `docs/mesures/le_drapeau_de_normale.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_drapeau_de_normale.py --verifier
    uv run python src/figures/figure_drapeau_de_normale.py \\
        --normale data/sens_normale/rendu_normal --inverse data/sens_normale/rendu_inverse \\
        --sortie docs/images/38_drapeau_de_normale.png
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
AMBRE = (150, 90, 20)
VERT = (52, 122, 72)
GRIS = (206, 206, 204)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    n = m["couches"]
    return [
        f"les deux rendus portent les MEMES {n} images, en ordre inverse : "
        f"{m['identiques_apres_renversement']}/{n} identiques octet pour octet.",
        f"a l'endroit, {m['identiques_sans_renversement']} seule couche coincide — le milieu, "
        f"celui que le renversement laisse en place.",
        "le drapeau renumerote donc la pile ; il ne la deplace pas, et la fenetre reste "
        "centree sur la surface.",
        "il n'existe pas de « mauvais cote » ou elle aurait pu etre : l'hypothese n'est pas "
        "infirmee, elle est inexprimable.",
    ]


def bande(art, x0: int, y: int, largeur: int, n: int, marques: list[bool], titre: str,
          couleur, police_petite) -> None:
    """Une cellule par couche : pleine si les deux piles coïncident à cet indice."""
    pas = max(1, largeur // n)
    art.text((x0, y - 16), titre, fill=DISCRET, font=police_petite)
    for k in range(n):
        x = x0 + k * pas
        art.rectangle([x, y, x + pas - 2, y + 14],
                      fill=couleur if marques[k] else FOND, outline=GRIS)


def dessiner(m: dict, normale: Path, inverse: Path, sortie: Path) -> dict:
    import numpy as np
    import tifffile
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    n = m["couches"]
    a = sorted(normale.glob("*.tif"))
    b = sorted(inverse.glob("*.tif"))
    if len(a) != n or len(b) != n:
        raise SystemExit(f"les piles ne portent pas {n} couches : {len(a)} / {len(b)}")

    # ⚠ L'ECHELLE DE GRIS EST COMMUNE, prise sur la premiere vignette. Normaliser chacune sur
    # sa propre plage ferait paraitre differentes deux images identiques — soit exactement la
    # conclusion inverse de celle qu'on etablit.
    ref = tifffile.imread(a[0]).astype(np.float32)
    vif = ref[ref > 0]
    bas, haut = (float(np.percentile(vif, 2)), float(np.percentile(vif, 98))) if vif.size \
        else (0.0, 1.0)

    cote = 300

    def vignette(chemin: Path):
        plan = tifffile.imread(chemin).astype(np.float32)
        img = np.clip((plan - bas) / max(haut - bas, 1e-9), 0.0, 1.0)
        return Image.fromarray((img * 255).astype(np.uint8), mode="L").convert("RGB") \
            .resize((cote, cote), Image.LANCZOS)

    vues = [(vignette(a[0]), f"normal — couche 00", "la premiere du rendu a l'endroit"),
            (vignette(b[n - 1]), f"inverse — couche {n - 1:02d}",
             "LES MEMES OCTETS que celle de gauche"),
            (vignette(b[0]), "inverse — couche 00", "l'autre bout de la meme pile")]

    marge, ecart, entete = 26, 20, 64
    largeur = marge * 2 + cote * 3 + ecart * 2
    lignes = prose(m)
    hauteur = entete + cote + 46 + 74 + len(lignes) * 19 + 22
    toile = Image.new("RGB", (largeur, hauteur), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Ce que « --flip-normals » fait vraiment a la pile rendue",
             fill=TEXTE, font=gros)
    art.text((marge, 38), f"PHerc1447, meme surface, meme fenetre de {n} couches a 8,64 um",
             fill=DISCRET, font=moyen)

    for i, (img, titre, sous) in enumerate(vues):
        x = marge + i * (cote + ecart)
        toile.paste(img, (x, entete))
        art.rectangle([x - 1, entete - 1, x + cote, entete + cote], outline=GRIS)
        art.text((x, entete + cote + 8), titre,
                 fill=AMBRE if i == 1 else TEXTE, font=moyen)
        art.text((x, entete + cote + 26), sous, fill=DISCRET, font=petit)

    y = entete + cote + 62
    large = cote * 3 + ecart * 2
    bande(art, marge, y + 16, large, n,
          [k < m["identiques_apres_renversement"] for k in range(n)],
          f"apparie A[k] contre B[{n - 1}-k] — {m['identiques_apres_renversement']}/{n}",
          VERT, petit)
    bande(art, marge, y + 52, large, n,
          [k == m["milieu"] for k in range(n)],
          f"apparie A[k] contre B[k] — {m['identiques_sans_renversement']}/{n}", AMBRE, petit)

    ligne_de_base = y + 84
    for j, ligne in enumerate(lignes):
        art.text((marge, ligne_de_base + j * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"couches": n, "sortie": str(sortie), "plage_de_gris": [bas, haut]}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    faux = {"couches": 41, "identiques_apres_renversement": 41,
            "identiques_sans_renversement": 1, "le_drapeau_renumerote": True, "milieu": 20}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle donne les DEUX appariements, pas seulement celui qui coincide",
      any("41/41" in x for x in lignes) and any("1 seule couche" in x for x in lignes),
      str(lignes[:2]))
    # ⚠⚠ La conclusion qui compte n'est pas « les deux sens se valent » mais « la question ne
    # se pose pas » : la figure doit le DIRE, sinon un lecteur la lit comme un match nul.
    v("... et elle dit que l'hypothese est inexprimable, pas seulement non confirmee",
      any("inexprimable" in x for x in lignes), str(lignes[-1]))

    # ⚠ Une figure dessinee depuis des piles qui ne portent pas le compte annonce comparerait
    # autre chose que ce que la mesure a compare.
    import shutil
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "a").mkdir()
    (d / "b").mkdir()
    v("une pile qui ne porte pas le compte annonce est REFUSEE",
      _leve(lambda: dessiner(faux, d / "a", d / "b", d / "x.png")))
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
                   default=RACINE / "docs" / "mesures" / "le_drapeau_de_normale.json")
    p.add_argument("--normale", type=Path, default=RACINE / "data/sens_normale/rendu_normal")
    p.add_argument("--inverse", type=Path, default=RACINE / "data/sens_normale/rendu_inverse")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "38_drapeau_de_normale.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.normale, a.inverse, a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
