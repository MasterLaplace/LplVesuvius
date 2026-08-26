#!/usr/bin/env python3
"""La correction appliquée, et son témoin de signe opposé — trois fois la même couche.

⚠⚠ **Ce que cette figure établit, et que trois nombres ne montrent pas.** `20` §9 mesure
qu'un déplacement du maillage le long de sa normale ramène le pic de matière sur la
couche tracée. Un lecteur a le droit de demander à quoi ça ressemble : si la feuille
est *dans* la fenêtre, la couche tracée montre du papyrus net ; si elle est à côté, elle
montre du vide ou une autre feuille.

⚠ **Les trois panneaux sont la MÊME couche du MÊME endroit**, à la résolution native.
Réduire une image moyenne ses pixels et efface les fibres — c'est l'avertissement que
`regarder_rendu.py` porte déjà —, donc on **recadre** au lieu de redimensionner.

⚠⚠ **Le troisième panneau est un TÉMOIN, pas une variante.** C'est le même déplacement
au signe opposé. Sans lui, un lecteur ne peut pas distinguer « le déplacement a centré la
feuille » de « n'importe quel changement aurait amélioré l'image ». Le signe ne se déduit
d'aucune convention écrite : il se mesure, et ce panneau est la mesure.

⚠ L'échelle de gris est **PARTAGÉE** par les trois panneaux et bornée par le maximum
commun : normaliser chacun sur son propre maximum ferait paraître une couche vide aussi
contrastée qu'une couche pleine.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARGE, ENTRE, TITRE, PIED = 46, 26, 34, 74


def couche(dossier: Path, index: int):
    """La couche `index` d'un rendu, en tableau."""
    import numpy as np
    import tifffile

    fichiers = sorted(dossier.glob("*.tif"))
    if not fichiers:
        raise SystemExit(f"aucune couche dans {dossier}")
    if not 0 <= index < len(fichiers):
        raise SystemExit(f"couche {index} hors des {len(fichiers)} rendues")
    return np.asarray(tifffile.imread(str(fichiers[index])))


def meilleur_pave(image, cote: int) -> tuple[int, int]:
    """Le pavé le plus PLEIN, pour ne pas illustrer un résultat avec du vide.

    ⚠ Choisi sur la couche de RÉFÉRENCE seule, puis imposé aux trois : un pavé choisi
    par panneau montrerait trois endroits différents, et la comparaison ne porterait
    plus sur la correction mais sur le cadrage.
    """
    import numpy as np

    h, w = image.shape
    cote = min(cote, h, w)
    pas = max(1, cote // 2)
    best, ou = -1.0, (0, 0)
    for y in range(0, h - cote + 1, pas):
        for x in range(0, w - cote + 1, pas):
            part = float((image[y:y + cote, x:x + cote] > 0).mean())
            if part > best:
                best, ou = part, (y, x)
    return ou


def dessiner(paves, titres, sous_titres, sortie: Path, borne: float) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    try:
        police = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
        grasse = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
    except OSError:
        police = grasse = ImageFont.load_default()

    cote = paves[0].shape[0]
    largeur = MARGE * 2 + cote * len(paves) + ENTRE * (len(paves) - 1)
    hauteur = MARGE + TITRE + cote + PIED
    toile = Image.new("RGB", (largeur, hauteur), (250, 250, 248))
    art = ImageDraw.Draw(toile)

    for i, (pave, titre, sous) in enumerate(zip(paves, titres, sous_titres)):
        # ⚠ Borne PARTAGEE : sans elle une couche vide se re-normaliserait sur son propre
        # maximum et paraitrait aussi contrastee qu'une couche pleine.
        gris = np.clip(pave.astype(np.float64) / max(borne, 1e-9), 0, 1)
        vignette = Image.fromarray((gris * 255).astype(np.uint8), "L").convert("RGB")
        x = MARGE + i * (cote + ENTRE)
        toile.paste(vignette, (x, MARGE + TITRE))
        art.rectangle([x - 1, MARGE + TITRE - 1, x + cote, MARGE + TITRE + cote],
                      outline=(150, 150, 148))
        art.text((x, MARGE + 4), titre, fill=(20, 20, 20), font=grasse)
        art.text((x, MARGE + TITRE + cote + 8), sous, fill=(60, 60, 60), font=police)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)


def verifier() -> int:
    """Les contrôles hors ligne, chacun avec son cas négatif."""
    import tempfile

    import numpy as np
    import tifffile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        for nom, valeur in (("clair", 200), ("sombre", 40)):
            (r / nom).mkdir()
            for i in range(3):
                img = np.zeros((40, 40), np.uint8)
                img[10:30, 10:30] = valeur
                tifffile.imwrite(str(r / nom / f"{i:02d}.tif"), img)

        clair = couche(r / "clair", 1)
        v("la couche demandee est bien lue", int(clair.max()) == 200, str(clair.max()))
        # ⚠⚠ Un index hors des couches rendues doit etre un REFUS : sans lui, une figure
        # legendee « couche 30 » pourrait montrer la 2, et rien ne le dirait.
        try:
            couche(r / "clair", 9)
            v("une couche hors bornes est refusee", False, "acceptee")
        except SystemExit:
            v("une couche hors bornes est refusee", True)
        try:
            couche(r / "vide-inexistant", 0)
            v("un dossier sans couche est refuse", False, "accepte")
        except SystemExit:
            v("un dossier sans couche est refuse", True)

        # Le pave le plus PLEIN, et non le premier venu.
        creux = np.zeros((60, 60), np.uint8)
        creux[36:60, 36:60] = 255
        v("le pave choisi est le plus plein", meilleur_pave(creux, 24) == (36, 36),
          str(meilleur_pave(creux, 24)))

        # ⚠⚠ LE controle qui compte : la borne de gris est PARTAGEE. Un panneau sombre
        # normalise sur son propre maximum paraitrait aussi contraste qu'un panneau clair,
        # et la figure montrerait alors l'inverse de ce qu'elle mesure.
        sombre = couche(r / "sombre", 1)
        sortie = r / "f.png"
        borne = float(max(clair.max(), sombre.max()))
        dessiner([clair, sombre, clair], ["a", "b", "c"], ["", "", ""], sortie, borne)
        from PIL import Image
        img = np.asarray(Image.open(sortie).convert("L"))
        v("la figure est ecrite", sortie.exists() and img.size > 0)
        cote = clair.shape[0]
        p1 = img[MARGE + TITRE + 20, MARGE + 20]
        p2 = img[MARGE + TITRE + 20, MARGE + cote + ENTRE + 20]
        v("le panneau sombre reste SOMBRE a cote du clair", int(p2) < int(p1) - 60,
          f"{int(p1)} vs {int(p2)}")

        # ⚠ La figure accepte N panneaux, pas trois : la comparaison a gagne un quatrieme
        # etat (le maillage RE-APLATI) et un nombre fige aurait force soit a jeter un
        # etat, soit a ecrire une seconde figure qui aurait derive de la premiere.
        for combien in (2, 4, 5):
            s2 = r / f"f{combien}.png"
            dessiner([clair] * combien, [str(i) for i in range(combien)],
                     [""] * combien, s2, borne)
            larg = np.asarray(Image.open(s2)).shape[1]
            attendu = MARGE * 2 + cote * combien + ENTRE * (combien - 1)
            v(f"une figure a {combien} panneaux a la bonne largeur", larg == attendu,
              f"{larg} au lieu de {attendu}")

        # ⚠⚠ Le pave COMMUN est le bon choix par defaut -- il compare le meme endroit --
        # et il devient FAUX quand deux rendus n'ont pas la meme rasterisation. Le controle
        # porte sur la difference : deux images dont la matiere est a des endroits opposes
        # doivent donner deux paves DIFFERENTS quand on les choisit par panneau.
        g1 = np.zeros((60, 60), np.uint8); g1[0:24, 0:24] = 255
        g2 = np.zeros((60, 60), np.uint8); g2[36:60, 36:60] = 255
        v("un pave par panneau suit la matiere de CHAQUE image",
          meilleur_pave(g1, 24) == (0, 0) and meilleur_pave(g2, 24) == (36, 36),
          f"{meilleur_pave(g1, 24)} / {meilleur_pave(g2, 24)}")
        # ... et le cas negatif : normalise chacun sur soi, les deux seraient egaux.
        v("... alors qu'une normalisation par panneau les egaliserait",
          abs(int(clair.max()) - int(sombre.max())) > 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trois fois la meme couche tracee : base, corrigee, temoin de signe oppose.")
    parser.add_argument("--verifier", action="store_true")
    parser.add_argument("rendus", type=Path, nargs="*",
                        help="les dossiers de rendu, dans l'ordre des panneaux")
    parser.add_argument("--sortie", type=Path, default=None)
    parser.add_argument("--titres", nargs="*", default=None)
    parser.add_argument("--couche", type=int, default=None, help="index de la couche tracee")
    parser.add_argument("--pave-par-panneau", action="store_true",
                        help="choisir le pave dans CHAQUE panneau. ⚠ A n'utiliser que si "
                             "les rendus n'ont PAS le meme rasterisation -- un ré-aplatissement "
                             "recadre, donc les memes coordonnees ne designent plus le meme "
                             "endroit. Sinon le pave commun est le bon choix, parce qu'il "
                             "compare le MEME endroit")
    parser.add_argument("--cote", type=int, default=560)
    parser.add_argument("--legendes", nargs="*", default=None,
                        help="les trois sous-titres, mesures a l'appui")
    a = parser.parse_args()

    if a.verifier:
        return verifier()
    if len(a.rendus) < 2 or a.sortie is None or a.couche is None:
        parser.error("au moins deux rendus, --sortie et --couche sont requis")

    import numpy as np

    images = [couche(d, a.couche) for d in a.rendus]
    cote = min(a.cote, *[min(im.shape) for im in images])
    if a.pave_par_panneau:
        # ⚠⚠ Un pave par panneau ne compare plus le MEME endroit : il ne vaut que pour
        # juger une TEXTURE (est-elle localement etiree ?), jamais une position. Le dire
        # ici, parce qu'un lecteur suppose par defaut que quatre vignettes cote a cote
        # montrent le meme morceau de papyrus.
        paves = [im[y0:y0 + cote, x0:x0 + cote]
                 for im in images
                 for (y0, x0) in (meilleur_pave(im, cote),)]
        ou = "un pave par panneau (rasterisations differentes)"
    else:
        y, x = meilleur_pave(images[0], cote)
        paves = [im[y:y + cote, x:x + cote] for im in images]
        ou = f"pave commun ({y}, {x})"
    borne = float(max(p.max() for p in paves))

    titres = a.titres or [d.name for d in a.rendus]
    legendes = (a.legendes or [""] * len(paves))[:len(paves)]
    legendes += [""] * (len(paves) - len(legendes))
    dessiner(paves, titres, legendes, a.sortie, borne)
    print(f"{ou} de {cote} px, borne de gris commune {borne:.0f}")
    for t, p in zip(titres, paves):
        print(f"  {t:<8} matiere {100 * float((p > 0).mean()):5.1f} %   "
              f"moyenne {float(p.mean()):6.1f}")
    print(f"ecrit : {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
