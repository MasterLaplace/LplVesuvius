#!/usr/bin/env python3
"""Une feuille aplatie, ou des spires vues de côté ? La question se règle à l'œil.

⚠⚠ CE FICHIER VIENT D'UNE QUESTION DE L'AUTEUR : *« un jour on aura une vue des vraies
feuilles aplaties ou bien ? »*. Le dépôt mesurait le relief depuis des semaines sans jamais
mettre une couche publiée à côté d'une des nôtres. La réponse tenait dans deux images, et
elle n'était dans aucun nombre — ce qui est, mot pour mot, le piège que ce dépôt a déjà
consigné sous « regarder trouve de vrais bugs ».

⭐ Ce que le dessin rend évident : une surface publiée montre une **feuille de face**, avec
ses fibres et ses déchirures ; nos traces montrent des **spires coupées en travers**, des
rubans clairs séparés de vide. Ce ne sont pas deux qualités du même objet, ce sont deux
objets.

⚠⚠ **Les tuiles doivent avoir la MÊME étendue en voxels**, et le programme refuse si ce
n'est pas le cas. Comparer une tuile de 512 voxels à une de 2400 ferait passer une
différence d'échelle pour une différence de surface : c'est exactement la faute que
[`52`](docs/52_calibrer_sur_son_corpus.md) existe pour empêcher, transposée aux images.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sys
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from figure_commune import police  # noqa: E402

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
FEUILLE = (74, 132, 96)
TRANCHE = (196, 72, 60)

ANGLAIS = {
    "une feuille aplatie, ou des spires vues de côté":
        "a flattened sheet, or wraps seen edge on",
    "la même étendue de papyrus dans les quatre vignettes":
        "the same extent of papyrus in all four thumbnails",
    "référence publiée": "published reference",
    "maillage publié, notre rendu": "published mesh, our render",
    "notre trace": "our trace",
    "feuille": "sheet",
    "spires en travers": "wraps across",
    "relief ": "relief ",
    " voxels de côté": " voxels across",
    "⚠ même chaîne de rendu dans les trois dernières vignettes":
        "⚠ same render chain in the last three thumbnails",
}




def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def centre(image, cote: int):
    """Le carré central de `cote` voxels.

    ⚠ Le CENTRE et non le coin : le bord d'un rendu est là où le maillage s'arrête, donc là
    où l'image est la moins représentative de ce que le travail produit.
    """
    import numpy as np

    a = np.asarray(image)
    if a.ndim != 2:
        raise ValueError("la couche n'est pas une image")
    if a.shape[0] < cote or a.shape[1] < cote:
        raise ValueError(f"{a.shape} : plus petit que la tuile demandée ({cote})")
    r, c = a.shape[0] // 2, a.shape[1] // 2
    d = cote // 2
    return a[r - d:r + d, c - d:c + d]


def dessiner(vignettes: list[dict], cote_voxels: int, sortie: Path,
             anglais: bool = False) -> dict:
    """Les vignettes côte à côte, toutes à la même étendue de papyrus."""
    if not vignettes:
        raise ValueError("aucune vignette — une figure vide serait une figure qui ment")
    tailles = {tuple(v["tuile"].shape) for v in vignettes}
    if len(tailles) != 1:
        raise ValueError(f"étendues différentes : {tailles} — la comparaison ne voudrait "
                         f"rien dire")
    g1, g2, g3 = police(14, 12, 11)
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        for fr, en in ANGLAIS.items():
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    cote = 200
    marge, ecart, haut = 24, 16, 60
    largeur = marge * 2 + cote * len(vignettes) + ecart * (len(vignettes) - 1)
    # ⚠⚠ La hauteur SUIT le nombre de lignes de titre. La figer laissait la derniere ligne
    # -- « feuille » / « spires en travers », c'est-a-dire le VERDICT de chaque vignette --
    # passer sous le filet de bas de page et sous la note. Un verdict illisible est un
    # verdict qu'on n'a pas rendu.
    lignes_titre = max(len(T(v["titre"]).split("\n")) for v in vignettes)
    bas_legende = haut + cote + 9 + lignes_titre * 16 + 18 + 16 + 14
    hauteur = bas_legende + 26
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    d.text((marge, 16), T("une feuille aplatie, ou des spires vues de côté"),
           font=g1, fill=ENCRE)
    d.text((marge, 38), T(f"la même étendue de papyrus dans les quatre vignettes — "
                          f"{cote_voxels} voxels de côté"), font=g3, fill=GRIS)

    x = marge
    for v in vignettes:
        vue = Image.fromarray(v["tuile"].astype("uint8"), mode="L").convert("RGB")
        im.paste(vue.resize((cote, cote), Image.LANCZOS), (x, haut))
        feuille = bool(v.get("feuille"))
        d.rectangle([x - 1, haut - 1, x + cote, haut + cote],
                    outline=FEUILLE if feuille else TRANCHE, width=2)
        y = haut + cote + 9
        for i, ligne in enumerate(T(v["titre"]).split("\n")):
            d.text((x, y + i * 16), ligne, font=g2, fill=ENCRE)
        y += lignes_titre * 16 + 2
        if v.get("relief") is not None:
            d.text((x, y), T(f"relief {v['relief']:.3f}".replace(".", ",")),
                   font=g3, fill=GRIS)
        d.text((x, y + 16), T("feuille" if feuille else "spires en travers"),
               font=g3, fill=FEUILLE if feuille else TRANCHE)
        x += cote + ecart

    d.line([(marge, bas_legende + 4), (largeur - marge, bas_legende + 4)],
           fill=TRAIT, width=1)
    d.text((marge, bas_legende + 8),
           T("⚠ même chaîne de rendu dans les trois dernières vignettes"),
           font=g3, fill=GRIS)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"vignettes": len(vignettes), "largeur": largeur, "hauteur": hauteur,
            "feuilles": sum(1 for v in vignettes if v.get("feuille")),
            "cote_voxels": cote_voxels,
            "intraduits": intraduits, "inchanges": inchanges}


def _verifier() -> int:
    import tempfile

    import numpy as np

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    grand = np.arange(400 * 400, dtype=np.int64).reshape(400, 400) % 256
    t = centre(grand.astype(np.uint8), 100)
    v("le recadrage rend la taille demandée", t.shape == (100, 100), str(t.shape))
    # ⚠ Le centre, pas le coin : la valeur au coin de la tuile doit être celle du milieu de
    # l'image, sinon on recadre ailleurs qu'on ne le dit.
    v("... et il est pris au CENTRE",
      int(t[0, 0]) == int(grand[150, 150] % 256), f"{int(t[0, 0])}")
    try:
        centre(np.zeros((10, 10), dtype=np.uint8), 100)
        v("une image plus petite que la tuile est refusée", False)
    except ValueError:
        v("une image plus petite que la tuile est refusée", True)

    feuille = np.zeros((120, 120), dtype=np.uint8)
    feuille[:] = 130
    tranche = np.zeros((120, 120), dtype=np.uint8)
    tranche[:, ::7] = 240  # des rubans separes de vide

    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner([{"titre": "référence publiée", "tuile": feuille,
                       "feuille": True, "relief": 0.79},
                      {"titre": "notre trace", "tuile": tranche,
                       "feuille": False, "relief": 0.16}], 512, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux vignettes sont dessinées", r["vignettes"] == 2)
        v("une seule est une feuille", r["feuilles"] == 1)
        # ⚠⚠ LE VERDICT NE DOIT PAS PASSER SOUS LE FILET. Le premier tirage laissait
        # « feuille » et « spires en travers » recouverts par la note de bas de page, donc
        # chaque vignette perdait la ligne qui dit ce qu'elle montre. La hauteur doit
        # croitre avec le nombre de lignes de titre.
        r2l = dessiner([{"titre": "un titre\nsur deux lignes", "tuile": feuille,
                         "feuille": True}], 512, Path(td) / "deux.png")
        r1l = dessiner([{"titre": "une seule ligne", "tuile": feuille, "feuille": True}],
                       512, Path(td) / "une.png")
        v("un titre sur deux lignes rend une figure plus haute",
          r2l["hauteur"] > r1l["hauteur"], f"{r2l['hauteur']} contre {r1l['hauteur']}")
        px = _pixels(Image.open(f).convert("RGB"))
        v("le cadre de la feuille est tracé", FEUILLE in px)
        v("celui des spires aussi", TRANCHE in px)
        # ⚠⚠ LE REFUS QUI PORTE LA FIGURE : deux étendues différentes ne se comparent pas.
        try:
            dessiner([{"titre": "a", "tuile": feuille, "feuille": True},
                      {"titre": "b", "tuile": np.zeros((60, 60), dtype=np.uint8)}],
                     512, Path(td) / "b.png")
            v("deux étendues différentes sont refusées", False)
        except ValueError:
            v("deux étendues différentes sont refusées", True)
        try:
            dessiner([], 512, Path(td) / "c.png")
            v("une figure sans vignette est refusée", False)
        except ValueError:
            v("une figure sans vignette est refusée", True)
        # ⚠ Cas négatif du cadre : sans vignette « feuille », aucun vert.
        r2 = dessiner([{"titre": "notre trace", "tuile": tranche, "feuille": False}],
                      512, Path(td) / "d.png")
        v("sans feuille, aucun cadre vert",
          r2["feuilles"] == 0 and FEUILLE not in _pixels(
              Image.open(Path(td) / "d.png").convert("RGB")))

        f3 = Path(td) / "en.png"
        r3 = dessiner([{"titre": "référence publiée", "tuile": feuille, "feuille": True},
                       {"titre": "notre trace", "tuile": tranche, "feuille": False}],
                      512, f3, anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def _couche(chemin: Path):
    import tifffile

    if chemin.is_dir():
        fichiers = sorted((p for p in chemin.glob("*.tif") if p.stem.isdigit()),
                          key=lambda p: int(p.stem))
        if not fichiers:
            raise ValueError(f"{chemin} : aucune couche")
        return tifffile.imread(str(fichiers[len(fichiers) // 2]))
    return tifffile.imread(str(chemin))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--reference", type=Path, help="tuile de la surface-volume publiée")
    p.add_argument("--publie", type=Path, help="notre rendu du maillage publié")
    p.add_argument("--nos-traces", type=Path, nargs="*", default=[])
    p.add_argument("--noms", nargs="*", default=[])
    p.add_argument("--reliefs", nargs="*", type=float, default=[])
    p.add_argument("--cote", type=int, default=512)
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/images/54_feuille_ou_tranche.png"))
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return _verifier()
    if not (a.reference and a.publie):
        p.error("--reference et --publie requis")

    reliefs = list(a.reliefs) + [None] * 10
    vignettes = [{"titre": "référence publiée", "tuile": centre(_couche(a.reference), a.cote),
                  "feuille": True, "relief": reliefs[0]},
                 {"titre": "maillage publié,\nnotre rendu",
                  "tuile": centre(_couche(a.publie), a.cote),
                  "feuille": True, "relief": reliefs[1]}]
    for i, t in enumerate(a.nos_traces):
        nom = a.noms[i] if i < len(a.noms) else t.name
        vignettes.append({"titre": f"notre trace\n{nom}",
                          "tuile": centre(_couche(t), a.cote),
                          "feuille": False, "relief": reliefs[2 + i]})
    r = dessiner(vignettes, a.cote, a.sortie, a.anglais)
    print(f"écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, "
          f"{r['feuilles']} feuille(s) sur {r['vignettes']})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"sortie": str(a.sortie), "cote_voxels": a.cote,
             "vignettes": r["vignettes"], "feuilles": r["feuilles"]}, indent=2),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
