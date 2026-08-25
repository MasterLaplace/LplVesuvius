#!/usr/bin/env python3
"""Le relief d'une fenêtre étroite, sur une surface qui suit une feuille et sur une qui n'en suit pas.

⚠⚠ **Pourquoi cette figure et pas un histogramme de α.** Trente-neuf séries de l'arbre
rendent un α que leurs appuis ne portent pas ([`51`](../../docs/51_une_pente_a_deux_appuis.md)),
donc un graphique de α empilerait des nombres dont une bonne part ne mesure rien. Le relief
de la fenêtre **étroite** échappe à ce défaut : c'est une lecture faite *à l'intérieur* d'une
seule fenêtre, sans pente, sans second appui et sans profondeurs à apparier.

⭐ Ce que le dessin doit rendre évident : les points verts sont **tous** à droite du plancher,
les rouges le chevauchent et descendent jusqu'à zéro. Une échelle logarithmique en rapport au
plancher — et non en amplitude nue — parce que le plancher peut différer d'un profil à
l'autre, et comparer des amplitudes brutes comparerait aussi des seuils.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
CONVERGE = (74, 132, 96)
CONDAMNE = (196, 72, 60)
PLANCHER = (28, 30, 34)

# ⚠ Un point d amplitude NULLE n a pas de logarithme. On le pose sur une position reservee,
# a gauche de tout le reste, et on la MARQUE -- l ecraser sur la plus petite valeur non nulle
# ferait passer « rien du tout » pour « presque rien ».
RAPPORT_ZERO = 0.04

ANGLAIS = {
    "le relief de la fenêtre étroite sépare les deux populations":
        "relief in the narrow window separates the two populations",
    "amplitude de la fenêtre la plus étroite, en multiples du plancher de détection":
        "amplitude of the narrowest window, in multiples of the detection floor",
    "suit une feuille": "follows a sheet",
    "posée en travers": "lying across",
    "plancher de détection": "detection floor",
    "amplitude nulle": "zero amplitude",
    "la plus basse qui converge : ": "lowest that converges: ",
    "× le plancher": "× the floor",
    " séries, ": " series, ",
    " sous le plancher": " below the floor",
    "aucune": "none",
}


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def _police():
    from PIL import ImageFont
    for c in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(c, 13), ImageFont.truetype(c, 11), \
                   ImageFont.truetype(c, 15)
        except Exception:
            continue
    f = ImageFont.load_default()
    return f, f, f


def repartir(valeurs: list[float], largeur: int, x_de) -> list[tuple[int, int]]:
    """Empile les points qui tombent sur la même colonne, pour qu'aucun n'en cache un autre.

    ⚠ Un nuage de points sans empilement ment sur la densité : deux cents séries au même
    endroit se dessinent comme une. On décale verticalement par colonne occupée.
    """
    par_colonne: dict[int, int] = {}
    out = []
    for v in sorted(valeurs):
        x = x_de(v)
        k = par_colonne.get(x, 0)
        par_colonne[x] = k + 1
        out.append((x, k))
    return out


def dessiner(points: list[dict], sortie: Path, anglais: bool = False) -> dict:
    if not points:
        raise ValueError("aucun point")
    p, pp, pg = _police()
    conv = [x["amplitude_sur_plancher"] for x in points if x["converge"]]
    cond = [x["amplitude_sur_plancher"] for x in points if not x["converge"]]
    if not conv or not cond:
        raise ValueError("il faut les deux populations")

    def borne(v):
        return max(v, RAPPORT_ZERO)

    tous = [borne(v) for v in conv + cond]
    xmin, xmax = min(tous), max(tous)
    marge, larg, haut, ecart = 92, 600, 120, 52
    L, H = marge + larg + 64, marge + haut * 2 + ecart + 96
    img = Image.new("RGB", (L, H), FOND)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    brut = ImageDraw.Draw(img)

    def X(v):
        v = borne(v)
        f = (math.log10(v) - math.log10(xmin * 0.8)) / \
            (math.log10(xmax * 1.25) - math.log10(xmin * 0.8))
        return marge + int(f * larg)

    d.text((marge, 26), "le relief de la fenêtre étroite sépare les deux populations",
           fill=ENCRE, font=pg)
    d.text((marge, 47),
           "amplitude de la fenêtre la plus étroite, en multiples du plancher de détection",
           fill=GRIS, font=pp)

    bas = marge + haut * 2 + ecart
    graduations = 0
    for val in (0.1, 0.5, 1, 2, 5, 10):
        if xmin * 0.8 <= val <= xmax * 1.25:
            brut.line([(X(val), marge), (X(val), bas)], fill=TRAIT)
            brut.text((X(val) - 7, bas + 8), f"{val:g}", fill=GRIS, font=pp)
            graduations += 1

    # ⚠⚠ Le plancher est la seule ligne PLEINE : c est lui qui sépare « mesure » de « ne
    # mesure rien », et tout le dessin est une réponse à « de quel côté ».
    brut.line([(X(1.0), marge - 6), (X(1.0), bas + 4)], fill=PLANCHER, width=2)
    d.text((X(1.0) - 34, marge - 24), "plancher de détection", fill=PLANCHER, font=pp)

    zeros = 0
    rangs = ((conv, CONVERGE, "suit une feuille", marge),
             (cond, CONDAMNE, "posée en travers", marge + haut + ecart))
    for vals, couleur, libelle, y0 in rangs:
        # ⚠ Le libelle va AU-DESSUS de sa rangee et non a gauche : pose a gauche, il
        # tombait sur la colonne des amplitudes nulles, qui est justement la plus peuplee
        # de la rangee rouge.
        d.text((marge, y0 + 2), libelle, fill=couleur, font=p)
        for x, k in repartir(vals, larg, X):
            y = y0 + haut - 8 - (k % 12) * 8
            brut.ellipse([x - 3, y - 3, x + 3, y + 3], fill=couleur)
        zeros += sum(1 for v in vals if v <= 0)
        sous = sum(1 for v in vals if v < 1.0)
        d.text((marge + larg - 200, y0 + 2),
               f"{len(vals)}" + " séries, " + (f"{sous}" if sous else "aucune")
               + " sous le plancher", fill=couleur, font=pp)

    if zeros:
        d.text((X(RAPPORT_ZERO) - 24, bas + 26), "amplitude nulle", fill=CONDAMNE, font=pp)

    d.text((marge, H - 30),
           "la plus basse qui converge : " + f"{min(conv):.2f}" + "× le plancher",
           fill=CONVERGE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"largeur": L, "hauteur": H, "convergentes": len(conv), "condamnees": len(cond),
            "graduations": graduations, "zeros": zeros,
            "plus_basse_convergente": min(conv),
            "convergentes_sous_le_plancher": sum(1 for v in conv if v < 1.0),
            "intraduits": d.intraduits() if anglais else [],
            "inchanges": d.inchanges() if anglais else []}


def _verifier() -> int:
    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    # ⚠ L empilement : trois valeurs sur la meme colonne doivent recevoir trois rangs.
    r = repartir([1.0, 1.0, 1.0], 100, lambda v: 50)
    v("les points d une meme colonne s empilent", [k for _, k in r] == [0, 1, 2], str(r))
    v("... et deux colonnes distinctes repartent a zero",
      [k for _, k in repartir([1.0, 9.0], 100, lambda v: int(v))] == [0, 0])

    pts = ([{"serie": f"c{i}", "converge": True, "amplitude_sur_plancher": 2.5 + i}
            for i in range(4)]
           + [{"serie": f"k{i}", "converge": False, "amplitude_sur_plancher": v}
              for i, v in enumerate([0.0, 0.4, 0.9, 3.0])])
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(pts, f)
        v("l image est ecrite", f.is_file() and f.stat().st_size > 0)
        v("les deux populations sont comptees",
          r["convergentes"] == 4 and r["condamnees"] == 4)
        # ⚠⚠ Le constat que la figure porte : aucune convergente sous le plancher.
        v("aucune convergente sous le plancher", r["convergentes_sous_le_plancher"] == 0)
        v("la plus basse convergente est chiffree",
          abs(r["plus_basse_convergente"] - 2.5) < 1e-9)
        # ⚠ Une amplitude NULLE n a pas de logarithme : elle doit etre posee et SIGNALEE,
        # pas ecrasee sur la plus petite valeur non nulle.
        v("l amplitude nulle est comptee a part", r["zeros"] == 1)
        px = _pixels(Image.open(f).convert("RGB"))
        v("les convergentes portent leur couleur", CONVERGE in px)
        v("les condamnees aussi", CONDAMNE in px)
        v("l axe porte des graduations", r["graduations"] >= 3, str(r["graduations"]))
        f2 = Path(td) / "en.png"
        r2 = dessiner(pts, f2, anglais=True)
        v("aucun libelle ne reste en francais", not r2["intraduits"],
          ", ".join(r2["intraduits"]))
        v("chaque libelle porteur d un mot a ete touche par la table",
          not r2["inchanges"], ", ".join(r2["inchanges"]))
        try:
            dessiner([x for x in pts if x["converge"]], Path(td) / "une.png")
            v("une seule population est refusee", False)
        except ValueError:
            v("une seule population est refusee", True)
        try:
            dessiner([], Path(td) / "vide.png")
            v("aucun point est refuse", False)
        except ValueError:
            v("aucun point est refuse", True)

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/appui_de_pente.json"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/51_contraste.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.json.is_file():
        print(f"absent : {a.json}", file=sys.stderr)
        return 2
    d = json.loads(a.json.read_text(encoding="utf-8"))
    pts = (d.get("contraste_des_appuis") or {}).get("points") or []
    if not pts:
        print("aucun point de contraste dans le JSON", file=sys.stderr)
        return 2
    r = dessiner(pts, a.sortie, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ non traduits : " + ", ".join(r["intraduits"] + r["inchanges"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, "
          f"{r['convergentes']} convergentes / {r['condamnees']} condamnées, "
          f"plus basse convergente {r['plus_basse_convergente']:.2f}×)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
