#!/usr/bin/env python3
"""Le même maillage, deux repères : rien, et un papyrus.

⚠⚠ **Ce que le dessin doit rendre évident en une seconde** : les cinq piles `m7` n'étaient
pas des surfaces plates, elles étaient **noires**. Un tableau de chiffres le dit ; un tableau
de chiffres est aussi ce qui a permis de lire « relief 0,0000 » comme une propriété du
papyrus pendant deux jours. Une vignette de la couche elle-même ne laisse pas cette lecture
ouverte.

⭐ Les trois panneaux sont **lus dans les piles**, jamais redessinés : ce sont les pixels
qu'a produits le moteur de rendu. Le premier et le deuxième viennent du **même maillage**,
la seule différence étant le repère dans lequel on l'a lu.

⚠ Les chiffres sous chaque panneau sont recalculés depuis la pile affichée, pas recopiés
d'un document. Une légende qui cite un chiffre venu d'ailleurs peut se désaccorder de l'image
qu'elle légende, et c'est précisément la classe d'erreur que ce lot a corrigée.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
VIDE = (196, 72, 60)
PLEIN = (74, 132, 96)

ANGLAIS = {
    "le même maillage, deux repères": "the same mesh, two frames",
    "chaque vignette est une couche RÉELLE de la pile rendue":
        "each thumbnail is a REAL layer of the rendered stack",
    "rendu au niveau 0": "rendered at level 0",
    "le même maillage, remis dans son repère": "the same mesh, put back in its frame",
    "ps256, dont le repère était déjà bon": "ps256, whose frame was already right",
    "max ": "max ",
    " allumé": " lit",
    "VIDE — rien n'a été rendu": "EMPTY — nothing was rendered",
    "de la matière": "material",
    "⚠ « profil plat » était le nom donné à la première vignette":
        "\u26a0 'flat profile' was the name given to the first thumbnail",
}


def _police():
    from PIL import ImageFont
    for c in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return (ImageFont.truetype(c, 14), ImageFont.truetype(c, 12),
                    ImageFont.truetype(c, 11))
        except OSError:
            continue
    d = ImageFont.load_default()
    return d, d, d


def couper(texte: str, police, largeur: int, dessin) -> list[str]:
    """Le texte replié pour tenir dans `largeur`, mot par mot.

    ⚠⚠ Sans ça, un titre de panneau déborde sur le panneau d'à côté et les deux légendes se
    superposent — vu sur le premier tirage de cette figure, où « remis dans son repère »
    passait par-dessus « ps256 ». Un libellé illisible n'est pas un détail de mise en page :
    c'est la moitié du panneau qui cesse de dire ce qu'il montre.

    ⚠ La largeur est MESURÉE avec la police réelle, jamais estimée en nombre de caractères :
    les accents et les majuscules n'ont pas la même chasse, donc un compte de caractères
    déborde exactement sur les libellés français.
    """
    mots = texte.split()
    lignes, courante = [], ""
    for mot in mots:
        essai = f"{courante} {mot}".strip()
        if courante and dessin.textlength(essai, font=police) > largeur:
            lignes.append(courante)
            courante = mot
        else:
            courante = essai
    if courante:
        lignes.append(courante)
    return lignes or [""]


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def vignette(couche, cote: int):
    """Une couche ramenée à `cote` pixels, en niveaux de gris, sans rien inventer.

    ⚠ Réduction par `Image.NEAREST` et non par une moyenne : moyenner une pile noire donne
    du noir, mais moyenner une pile clairsemée **fabrique** des gris qui n'existent pas dans
    la donnée. Une vignette d'un rendu doit rester un échantillon du rendu.
    """
    import numpy as np

    a = np.asarray(couche)
    if a.ndim != 2 or a.size == 0:
        raise ValueError("la couche n'est pas une image")
    im = Image.fromarray(a.astype("uint8"), mode="L").convert("RGB")
    return im.resize((cote, cote), Image.NEAREST)


def mesurer(couche) -> dict:
    """Le maximum et la part allumée de CETTE couche, recalculés ici."""
    import numpy as np

    a = np.asarray(couche)
    return {"max": int(a.max()) if a.size else 0,
            "part": float((a > 0).mean()) if a.size else 0.0}


def dessiner(panneaux: list[dict], sortie: Path, anglais: bool = False) -> dict:
    """Trois panneaux côte à côte, chacun avec ce que sa propre couche mesure."""
    if not panneaux:
        raise ValueError("aucun panneau — une figure vide serait une figure qui ment")
    g1, g2, g3 = _police()
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        for fr, en in ANGLAIS.items():
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        # ⚠ Les accents sont le témoin le plus simple d'un libellé oublié par la table.
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    cote = 210
    marge = 26
    ecart = 22
    haut_titre = 62
    haut_legende = 86  # ajusté plus bas selon le repli réel des titres
    largeur = marge * 2 + cote * len(panneaux) + ecart * (len(panneaux) - 1)
    hauteur = haut_titre + cote + haut_legende
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)

    d.text((marge, 18), T("le même maillage, deux repères"), font=g1, fill=ENCRE)
    d.text((marge, 40), T("chaque vignette est une couche RÉELLE de la pile rendue"),
           font=g3, fill=GRIS)

    x = marge
    lignes_max = 1
    for p in panneaux:
        v = vignette(p["couche"], cote)
        im.paste(v, (x, haut_titre))
        m = mesurer(p["couche"])
        vide = m["max"] == 0
        d.rectangle([x - 1, haut_titre - 1, x + cote, haut_titre + cote],
                    outline=VIDE if vide else PLEIN, width=2)
        y = haut_titre + cote + 10
        lignes = couper(T(p["titre"]), g2, cote, d)
        for i, ligne in enumerate(lignes):
            d.text((x, y + i * 17), ligne, font=g2, fill=ENCRE)
        y += len(lignes) * 17 + 3
        d.text((x, y), T(f"max {m['max']}  ·  {100 * m['part']:.1f} % allumé"),
               font=g3, fill=GRIS)
        d.text((x, y + 17), T("VIDE — rien n'a été rendu" if vide else "de la matière"),
               font=g3, fill=VIDE if vide else PLEIN)
        lignes_max = max(lignes_max, len(lignes))
        x += cote + ecart

    # ⚠⚠ L'image est recadrée APRÈS coup à la hauteur réellement occupée. Poser la hauteur
    # avant de savoir sur combien de lignes les titres se replient laisse soit un blanc, soit
    # une note coupée — et une note coupée est une note qu'on n'a pas écrite.
    bas = haut_titre + cote + 10 + lignes_max * 17 + 3 + 34
    im = im.crop((0, 0, largeur, bas + 26))
    d = ImageDraw.Draw(im)
    d.line([(marge, bas + 6), (largeur - marge, bas + 6)], fill=TRAIT, width=1)
    d.text((marge, bas + 10),
           T("⚠ « profil plat » était le nom donné à la première vignette"),
           font=g3, fill=GRIS)
    hauteur = bas + 26

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"panneaux": len(panneaux), "largeur": largeur, "hauteur": hauteur,
            "vides": sum(1 for p in panneaux if mesurer(p["couche"])["max"] == 0),
            "intraduits": intraduits, "inchanges": inchanges}


def couche_de(pile: Path, indice: int | None = None):
    """La couche `indice` d'une pile, ou celle du milieu."""
    import tifffile

    fichiers = sorted((p for p in pile.glob("*.tif") if p.stem.isdigit()),
                      key=lambda p: int(p.stem))
    if not fichiers:
        raise ValueError(f"{pile} : aucune couche")
    k = len(fichiers) // 2 if indice is None else indice
    return tifffile.imread(str(fichiers[max(0, min(k, len(fichiers) - 1))]))


def _verifier() -> int:
    import tempfile

    import numpy as np

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    noir = np.zeros((60, 60), dtype=np.uint8)
    clair = (np.indices((60, 60)).sum(axis=0) % 200).astype(np.uint8)

    m = mesurer(noir)
    v("une couche noire mesure zéro", m["max"] == 0 and m["part"] == 0.0)
    m = mesurer(clair)
    v("une couche éclairée ne mesure pas zéro", m["max"] > 0 and m["part"] > 0.5, str(m))

    # ⚠ La vignette ne doit pas INVENTER de gris : réduire une image binaire par une moyenne
    # en fabriquerait. On vérifie que les valeurs de sortie sont un sous-ensemble de l'entrée.
    binaire = (np.indices((60, 60)).sum(axis=0) % 2 * 255).astype(np.uint8)
    vals = {p[0] for p in _pixels(vignette(binaire, 30))}
    v("la vignette n'invente pas de valeurs", vals <= {0, 255}, str(sorted(vals)[:6]))

    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner([{"titre": "rendu au niveau 0", "couche": noir},
                      {"titre": "le même maillage, remis dans son repère", "couche": clair},
                      {"titre": "ps256, dont le repère était déjà bon", "couche": clair}], f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les trois panneaux sont dessinés", r["panneaux"] == 3)
        # ⚠⚠ LE CONTRÔLE QUI PORTE LA FIGURE : un panneau vide est encadré de rouge et un
        # panneau plein de vert. Sans ça la figure serait trois vignettes sans verdict.
        v("un seul panneau est vide", r["vides"] == 1, str(r["vides"]))
        # ⚠⚠ LE REPLI DES TITRES, sondé plutôt qu'affirmé. Le premier tirage de cette figure
        # laissait « remis dans son repère » passer par-dessus « ps256 » : deux légendes
        # superposées, donc deux panneaux qui cessent de dire ce qu'ils montrent.
        from PIL import ImageDraw as _ID
        _d = _ID.Draw(Image.new("RGB", (10, 10)))
        _g = _police()[1]
        long_titre = "le même maillage, remis dans son repère de niveau zéro"
        v("un titre trop long est replié", len(couper(long_titre, _g, 210, _d)) > 1)
        v("... et chaque ligne tient dans la largeur",
          all(_d.textlength(l, font=_g) <= 210 for l in couper(long_titre, _g, 210, _d)))
        v("un titre court reste sur une ligne", len(couper("court", _g, 210, _d)) == 1)
        v("un mot plus large que la colonne n'est pas perdu",
          couper("anticonstitutionnellementaaaa", _g, 40, _d) != [""])
        px = _pixels(Image.open(f).convert("RGB"))
        v("le cadre du vide est tracé", VIDE in px)
        v("celui du plein aussi", PLEIN in px)
        # ⚠ Cas négatif : trois panneaux pleins ne doivent PAS produire de cadre rouge.
        f2 = Path(td) / "b.png"
        r2 = dessiner([{"titre": "a", "couche": clair}, {"titre": "b", "couche": clair}], f2)
        v("sans pile vide, aucun cadre rouge",
          r2["vides"] == 0 and VIDE not in _pixels(Image.open(f2).convert("RGB")))

        f3 = Path(td) / "en.png"
        r3 = dessiner([{"titre": "rendu au niveau 0", "couche": noir},
                       {"titre": "le même maillage, remis dans son repère",
                        "couche": clair}], f3, anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))

        try:
            dessiner([], Path(td) / "vide.png")
            v("une figure sans panneau est refusée", False)
        except ValueError:
            v("une figure sans panneau est refusée", True)
        try:
            vignette(np.zeros((0,), dtype=np.uint8), 10)
            v("une couche vide est refusée", False)
        except ValueError:
            v("une couche vide est refusée", True)
        try:
            couche_de(Path(td))
            v("une pile sans couche est refusée", False)
        except ValueError:
            v("une pile sans couche est refusée", True)

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vide", type=Path, help="pile rendue dans le mauvais repère")
    ap.add_argument("--rebase", type=Path, help="le MÊME maillage, remis dans son repère")
    ap.add_argument("--temoin", type=Path, help="une pile dont le repère était déjà bon")
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/54_piles_vides.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not (a.vide and a.rebase and a.temoin):
        ap.error("--vide, --rebase et --temoin requis")

    panneaux = [{"titre": "rendu au niveau 0", "couche": couche_de(a.vide)},
                {"titre": "le même maillage, remis dans son repère",
                 "couche": couche_de(a.rebase)},
                {"titre": "ps256, dont le repère était déjà bon",
                 "couche": couche_de(a.temoin)}]
    r = dessiner(panneaux, a.sortie, a.anglais)
    print(f"écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['vides']} pile(s) vide(s))")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"sortie": str(a.sortie), "vides": r["vides"],
             "mesures": [mesurer(p["couche"]) for p in panneaux]}, indent=2),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
