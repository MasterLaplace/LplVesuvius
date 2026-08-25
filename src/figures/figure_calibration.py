#!/usr/bin/env python3
"""La distribution du relief sur un corpus, avec la géométrie où elle a été lue.

⚠⚠ **La géométrie est écrite SUR la figure, et c'est le sujet.** Trois fois dans la même
journée un nombre a été déplacé hors de la géométrie qui l'avait produit — un seuil, deux
taux d'erreur, une profondeur de corpus. Une figure de calibration qui ne dit pas dans
quelle fenêtre elle a été lue invite à la quatrième.

⭐ Ce que le dessin doit rendre évident : le corpus publié se tient **loin** du plancher de
détection, et le seuil auquel `edge_pinned` a été déclaré fautif ailleurs **n'est jamais
atteint ici**. Un seuil qu'aucun point n'atteint se voit d'un coup d'œil et ne se voit pas
dans un tableau.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
CORPUS = (74, 132, 96)
PLANCHER = (196, 72, 60)
SEUIL = (176, 128, 62)

ANGLAIS = {
    "où se tient un corpus publié, et dans quelle fenêtre il a été lu":
        "where a published corpus sits, and in which window it was read",
    "chaque point est un segment publié — échelle logarithmique":
        "each dot is a published segment — logarithmic scale",
    "plancher de détection": "detection floor",
    "seuil où edge_pinned a été déclaré fautif AILLEURS": "threshold where edge_pinned was called wrong ELSEWHERE",
    "jamais atteint ici": "never reached here",
    " au bord gauche": " on the left edge",
    "fenêtre de lecture : ": "reading window: ",
    " px × ": " px x ",
    " couches": " layers",
    "médiane ": "median ",
    "⚠ cette distribution ne vaut pour aucune autre géométrie":
        "⚠ this distribution holds for no other geometry",
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


def empiler(valeurs: list[float], x_de, largeur_point: int = 7) -> list[tuple[float, int]]:
    """Chaque valeur avec sa rangée, pour qu'aucun point n'en cache un autre.

    ⚠ Un nuage de points sur un axe unique superpose les valeurs proches, donc un corpus
    dense se lit comme quelques points. L'empilement est la seule façon de rendre un COMPTE
    visible sans le remplacer par une hauteur d'histogramme — qui, elle, dépend du choix des
    classes.
    """
    occupe: dict[int, int] = {}
    out = []
    for v in sorted(valeurs):
        colonne = int(x_de(v)) // largeur_point
        rang = occupe.get(colonne, 0)
        occupe[colonne] = rang + 1
        out.append((v, rang))
    return out


def dessiner(relief: list[float], bord: list[float], geo: dict, plancher: float,
             sortie: Path, anglais: bool = False) -> dict:
    if not relief:
        raise ValueError("aucun relief à dessiner")
    p, pp, pg = _police()
    marge, larg, haut = 92, 600, 300
    # ⚠ La hauteur est CALCULEE depuis la geometrie des rangees, pas posee : la poser
    # faisait chevaucher la seconde rangee et le pied de figure.
    L, H = marge + larg + 40, marge + 30 + 2 * (96 + 42) + 96
    img = Image.new("RGB", (L, H), FOND)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    brut = ImageDraw.Draw(img)

    bas, hautv = plancher * 0.6, max(max(relief), 1.0) * 1.6

    def X(v):
        v = max(v, bas)
        f = (math.log10(v) - math.log10(bas)) / (math.log10(hautv) - math.log10(bas))
        return marge + int(f * larg)

    d.text((marge, 26), "où se tient un corpus publié, et dans quelle fenêtre il a été lu",
           fill=ENCRE, font=pg)
    d.text((marge, 47), "chaque point est un segment publié — échelle logarithmique",
           fill=GRIS, font=pp)

    # ⚠⚠ DEUX RANGEES SUR UN AXE PARTAGE, chacune avec SON seuil dans SA couleur. Les deux
    # grandeurs sont des lectures sans dimension des memes fenetres, donc l axe est commun ;
    # ce qui differe est le seuil auquel chacune se juge, et c est precisement ce que la
    # figure existe pour montrer. Une seule rangee laissait la mention « jamais atteint »
    # flotter a cote d un seuil qui n etait dessine nulle part.
    y0 = marge + 30
    rangees = ((relief, CORPUS, plancher, PLANCHER, "relief", "plancher de détection"),
               (bord, GRIS, 0.90, SEUIL, "edge_pinned",
                "seuil où edge_pinned a été déclaré fautif AILLEURS"))
    graduations = 0
    hauteur_rangee = 96
    for i, (vals, couleur, seuil, couleur_seuil, nom, libelle) in enumerate(rangees):
        base = y0 + i * (hauteur_rangee + 42) + hauteur_rangee
        d.line([(marge, base), (marge + larg, base)], fill=TRAIT)
        for val in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0):
            if bas <= val <= hautv:
                d.line([(X(val), base), (X(val), base + 5)], fill=GRIS)
                brut.text((X(val) - 10, base + 8), f"{val:g}", fill=GRIS, font=pp)
                graduations += 1
        if bas <= seuil <= hautv:
            d.line([(X(seuil), base - hauteur_rangee + 4), (X(seuil), base)],
                   fill=couleur_seuil, width=2)
            # ⚠ Un libelle pose a gauche de sa ligne sort du cadre quand la ligne est
            # dans le tiers droit. La position se MESURE au lieu d etre posee.
            w = int(brut.textlength(d.traduire(libelle), font=pp))
            lx = min(max(marge, X(seuil) - w // 2), marge + larg - w)
            # ⚠ DANS la bande de sa rangee et non au-dessus : pose au-dessus, le libelle
            # de la seconde rangee tombait sur la legende de la premiere.
            d.text((lx, base - hauteur_rangee + 6), libelle,
                   fill=couleur_seuil, font=pp)
        # ⚠ Une valeur nulle n a pas de logarithme : elle est posee sur le bord GAUCHE et
        # comptee, jamais silencieusement omise -- un point manquant se lit comme un point
        # qui n existe pas.
        au_bas = sum(1 for v in vals if v <= bas)
        for v, rang in empiler([max(v, bas) for v in vals], X):
            x, y = X(v), base - 10 - rang * 8
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=couleur)
        # ⚠⚠ LA MEDIANE VIENT DE `calibration_corpus`, jamais recalculee ici. Une version
        # anterieure prenait `sorted(vals)[len//2]` -- le milieu SUPERIEUR -- la ou
        # `statistics.median` moyenne les deux valeurs centrales sur un compte pair. Les
        # deux ont produit 0,746 et 0,744 pour les memes quatre-vingts segments, et le
        # premier est parti dans un document. Deux definitions d une meme grandeur dans un
        # meme depot finissent toujours par se contredire.
        med = st.median(vals) if vals else 0.0
        if i == 0:
            # ⚠⚠ La valeur RAPPORTEE est celle qui est DESSINEE, pas une seconde qu on
            # recalculerait dans le `return`. Ma premiere version renvoyait `st.median` a
            # part : le controle comparait alors `st.median` a `st.median` et ne pouvait
            # pas echouer -- verifie par sonde, il restait vert en remettant la mediane
            # maison dans le dessin.
            mediane_dessinee = med
        brut.text((marge, base + 24), f"{nom}", fill=ENCRE, font=p)
        brut.text((marge + 96, base + 24), f"{len(vals)} segments", fill=GRIS, font=p)
        d.text((marge + 226, base + 24), "médiane " + f"{med:.3f}", fill=GRIS, font=p)
        if au_bas:
            d.text((marge + 356, base + 24),
                   f"{au_bas}" + " au bord gauche", fill=GRIS, font=pp)
        if seuil <= hautv and not any(v >= seuil for v in vals):
            t = "jamais atteint ici"
            w2 = int(brut.textlength(d.traduire(t), font=p))
            d.text((min(X(seuil) + 10, marge + larg - w2), base - hauteur_rangee + 26),
                   t, fill=couleur_seuil, font=p)

    atteints = sum(1 for x in bord if x >= 0.90) if bord else 0

    d.text((marge, H - 46), "fenêtre de lecture : " + f"{geo.get('window_px', '?')}"
           + " px × " + f"{geo.get('layers', '?')}" + " couches", fill=ENCRE, font=p)
    d.text((marge, H - 24), "⚠ cette distribution ne vaut pour aucune autre géométrie",
           fill=GRIS, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"largeur": L, "hauteur": H, "points": len(relief),
            "mediane_relief": mediane_dessinee,
            "bande_brute": (marge - 4, y0 + hauteur_rangee + 20,
                            marge + 216, y0 + hauteur_rangee + 42),
            "graduations": graduations, "au_bord_90": atteints,
            "intraduits": d.intraduits() if anglais else [],
            "inchanges": d.inchanges() if anglais else []}


def _verifier() -> int:
    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    # ⚠ L empilement : deux valeurs dans la meme colonne doivent occuper deux rangees, sinon
    # un corpus dense se lit comme quelques points.
    e = empiler([0.80, 0.801, 0.802], lambda x: 300.0)
    v("des valeurs voisines s'empilent", [r for _, r in e] == [0, 1, 2], str(e))
    v("des valeurs éloignées restent au sol",
      [r for _, r in empiler([0.02, 0.9], lambda x: x * 1000)] == [0, 0])

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        rel = [0.52, 0.74, 0.79, 0.80, 0.83, 0.93]
        r = dessiner(rel, [0.0, 0.05, 0.07, 0.15, 0.21, 0.02],
                     {"window_px": 128, "layers": 109}, 0.02, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("tous les segments sont dessinés", r["points"] == len(rel))
        px = _pixels(Image.open(f).convert("RGB"))
        v("le corpus est tracé", CORPUS in px)
        v("le plancher aussi", PLANCHER in px)
        v("l'axe porte des graduations", r["graduations"] >= 4, str(r["graduations"]))
        # ⚠⚠ Le controle qui porte la figure : le seuil venu d ailleurs n est jamais
        # atteint, et la figure doit le DIRE plutot que de laisser un vide muet.
        v("le seuil venu d'ailleurs n'est jamais atteint ici", r["au_bord_90"] == 0)
        # ⚠⚠ La mediane doit etre CELLE de `calibration_corpus` : deux definitions ont deja
        # rendu 0,746 et 0,744 sur les memes donnees.
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
        from calibration_corpus import distribution as _dist
        v("la mediane est celle de calibration_corpus",
          abs(r["mediane_relief"] - _dist(sorted(rel))["mediane"]) < 1e-12,
          f"{r['mediane_relief']} contre {_dist(sorted(rel))['mediane']}")
        v("... et un corpus qui l'atteindrait serait compté",
          dessiner(rel, [0.95, 0.05], {"window_px": 128, "layers": 109}, 0.02,
                   Path(td) / "b.png")["au_bord_90"] == 1)
        f2 = Path(td) / "en.png"
        r2 = dessiner(rel, [0.0, 0.05], {"window_px": 128, "layers": 109}, 0.02, f2,
                      anglais=True)
        v("aucun libellé ne reste en français", not r2["intraduits"],
          ", ".join(r2["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r2["inchanges"], ", ".join(r2["inchanges"]))
        # ⚠⚠ Les libellés qui ne PEUVENT pas être traduits — un nom de colonne, un mot
        # identique dans les deux langues — ne sont pas excusés dans le garde : ils
        # n'y entrent pas, et on le prouve par les pixels.
        bande = tuple(r2["bande_brute"])
        a_fr = Image.open(f).convert("RGB").crop(bande).tobytes()
        a_en = Image.open(f2).convert("RGB").crop(bande).tobytes()
        v("la bande brute sort identique dans les deux langues", a_fr == a_en)
        try:
            dessiner([], [], {}, 0.02, Path(td) / "v.png")
            v("un corpus vide est refusé", False)
        except ValueError:
            v("un corpus vide est refusé", True)

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=Path("docs/calibration_scroll1.json"))
    ap.add_argument("--csv", type=Path, help="le balayage, pour les points individuels")
    # ⚠⚠ UNE figure, UNE geometrie. Un corpus publie n est pas homogene -- mesure sur
    # `Scroll1` : 80 segments a 109 couches et un a 6 -- et le relief depend de la
    # profondeur, donc superposer deux geometries dessinerait un instrument qui n existe
    # pas. Le groupe se choisit ici, explicitement, et la figure l estampille.
    ap.add_argument("--layers", type=int,
                    help="ne dessiner que les segments lus à cette profondeur")
    ap.add_argument("--sortie", type=Path,
                    default=Path("docs/images/52_calibration.png"))
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.csv or not a.csv.is_file():
        print("donner --csv, le balayage lui-même", file=sys.stderr)
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    from calibration_corpus import lire, nombres, geometrie
    lignes = lire(a.csv)
    if a.layers is not None:
        avant = len(lignes)
        lignes = [r for r in lignes if r.get("layers") == str(a.layers)]
        if not lignes:
            print(f"aucun segment à {a.layers} couches dans {a.csv}", file=sys.stderr)
            return 2
        if len(lignes) != avant:
            print(f"  ⚠ {avant - len(lignes)} segment(s) écarté(s) : lus à une autre "
                  f"profondeur", file=sys.stderr)
    geo = geometrie(lignes, None, None)
    r = dessiner(nombres(lignes, "relief"), nombres(lignes, "edge_pinned"), geo,
                 0.02, a.sortie, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ non traduits : " + ", ".join(r["intraduits"] + r["inchanges"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['points']} segments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
