#!/usr/bin/env python3
"""α est une pente, et deux résolutions doivent la lire pareil.

⚠⚠ **Le choix d'axe est tout le dessin.** α est défini comme
$\\log(d_1/d_0) / \\log(n_1/n_0)$ : c'est la **pente** de l'écart mesuré contre la
profondeur de fenêtre, en échelle log-log. Le montrer autrement — deux barres, deux
nombres — donne à lire un résultat sans donner à lire ce qu'il mesure.

⚠⚠ **Et l'axe des abscisses est la profondeur PHYSIQUE, pas le nombre de tranches.** Au
niveau 1 une tranche vaut deux fois l'épaisseur, donc 21 tranches y couvrent ce que 41
couvrent au niveau 0. Tracer contre le compte de tranches décalerait les deux séries d'un
facteur deux et ferait *paraître* un désaccord là où il y a coïncidence — l'erreur serait
purement dans le dessin, et parfaitement crédible.

⭐ Ce que la figure doit rendre évident : les deux séries se superposent, donc réduire la
résolution ne déplace pas la pente. C'est ce qui rend la fenêtre profonde mesurable.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
NIVEAU0 = (86, 104, 132)
NIVEAU1 = (176, 128, 62)
PENTE1 = (196, 72, 60)

NE_PAS_TRADUIRE: set[str] = set()

ANGLAIS = {
    "α est une pente : deux résolutions la lisent pareil":
        "α is a slope: two resolutions read it the same",
    "écart au pic mesuré, contre la profondeur de fenêtre — échelles logarithmiques":
        "measured gap to the peak against window depth — logarithmic axes",
    "profondeur de fenêtre (µm)": "window depth (µm)",
    "écart au pic (µm)": "gap to the peak (µm)",
    "écart": "gap",
    "au pic": "to peak",
    "(µm)": "(µm)",
    "pente 1 : l'écart suit la fenêtre": "slope 1: the gap tracks the window",
    "niveau ": "level ",
    " (voxel ": " (voxel ",
    " µm)": " µm)",
    "écart entre les deux pentes : ": "gap between the two slopes: ",
    "   résolution de α : ": "   α resolution: ",
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


def series_physiques(serie: list, voxel_um: float) -> list[tuple[float, float]]:
    """Passe une série (tranches, écart µm) en (profondeur µm, écart µm).

    ⚠ C'est ici que les deux niveaux deviennent comparables, et nulle part ailleurs. Un
    appelant qui oublierait la conversion obtiendrait deux courbes décalées d'un facteur
    deux — un désaccord qui n'existe pas.
    """
    return [(n * voxel_um, d) for n, d in serie]


def dessiner(niveaux: list[dict], sortie: Path, resolution_alpha: float = 0.2,
             anglais: bool = False) -> dict:
    p, pp, pg = _police()
    pts = {}
    for niv in niveaux:
        pts[niv["niveau"]] = series_physiques(niv["serie"], niv["voxel_um"])
    if not pts:
        raise ValueError("aucune série")

    tous = [q for v in pts.values() for q in v]
    xmin, xmax = min(x for x, _ in tous), max(x for x, _ in tous)
    ymin, ymax = min(y for _, y in tous), max(y for _, y in tous)
    marge, larg, haut = 84, 520, 360
    L, H = marge + larg + 200, marge + haut + 96
    img = Image.new("RGB", (L, H), FOND)
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)

    def X(v):
        f = (math.log10(v) - math.log10(xmin * 0.85)) / \
            (math.log10(xmax * 1.18) - math.log10(xmin * 0.85))
        return marge + int(f * larg)

    def Y(v):
        f = (math.log10(v) - math.log10(ymin * 0.85)) / \
            (math.log10(ymax * 1.18) - math.log10(ymin * 0.85))
        return marge + haut - int(f * haut)

    d.text((marge, marge - 52), "α est une pente : deux résolutions la lisent pareil",
           fill=ENCRE, font=pg)
    d.text((marge, marge - 31),
           "écart au pic mesuré, contre la profondeur de fenêtre — échelles logarithmiques",
           fill=GRIS, font=pp)

    d.line([(marge, marge + haut), (marge + larg, marge + haut)], fill=(215, 213, 208))
    d.line([(marge, marge), (marge, marge + haut)], fill=(215, 213, 208))
    d.text((marge + larg // 2 - 70, marge + haut + 44), "profondeur de fenêtre (µm)",
           fill=GRIS, font=pp)
    d.text((6, marge + haut // 2 - 40), "écart", fill=GRIS, font=pp)
    d.text((6, marge + haut // 2 - 24), "au pic", fill=GRIS, font=pp)
    d.text((6, marge + haut // 2 - 8), "(µm)", fill=GRIS, font=pp)

    # ⚠⚠ Sans graduations, une figure log-log ne laisse lire AUCUNE grandeur : on y voit
    # deux droites parallèles sans savoir si elles parlent de dix microns ou de mille. Les
    # décades sont marquées, plus les points de mesure eux-mêmes — ce sont eux que le
    # lecteur voudra retrouver dans le tableau.
    graduations = 0
    for dec in (10, 100, 1000):
        for mult in (1, 2, 5):
            val = dec * mult
            if xmin * 0.85 <= val <= xmax * 1.18:
                d.line([(X(val), marge + haut), (X(val), marge + haut + 5)], fill=GRIS)
                d.text((X(val) - 10, marge + haut + 9), f"{val}", fill=GRIS, font=pp)
                graduations += 1
            if ymin * 0.85 <= val <= ymax * 1.18:
                d.line([(marge - 5, Y(val)), (marge, Y(val))], fill=GRIS)
                d.text((marge - 34, Y(val) - 7), f"{val}", fill=GRIS, font=pp)
                graduations += 1

    # ⚠⚠ La droite de pente 1 est le REFERENTIEL de lecture : « α ≈ 1 » veut dire « l'écart
    # double quand la fenêtre double », et sans cette droite le lecteur doit croire le
    # chiffre au lieu de le voir. Elle passe par le premier point de la première série.
    x0, y0 = pts[sorted(pts)[0]][0]
    for t in range(0, 101, 4):
        xv = xmin * 0.9 * (xmax * 1.3 / (xmin * 0.9)) ** (t / 100)
        yv = y0 * (xv / x0)
        if ymin * 0.8 <= yv <= ymax * 1.25:
            d.line([(X(xv), Y(yv)), (X(xv) + 5, Y(yv * 1.001))], fill=PENTE1, width=1)
    d.text((X(xmax * 0.62), Y(y0 * (xmax * 0.62 / x0)) - 18),
           "pente 1 : l'écart suit la fenêtre", fill=PENTE1, font=pp)

    couleurs = {}
    for i, niv in enumerate(sorted(pts)):
        c = NIVEAU0 if niv == 0 else NIVEAU1
        couleurs[niv] = c
        q = sorted(pts[niv])
        for a, b in zip(q, q[1:]):
            d.line([(X(a[0]), Y(a[1])), (X(b[0]), Y(b[1]))], fill=c, width=2)
        for x, y in q:
            d.ellipse([X(x) - 5, Y(y) - 5, X(x) + 5, Y(y) + 5], fill=c)
        n = next(v for v in niveaux if v["niveau"] == niv)
        d.text((marge + larg + 16, marge + 10 + i * 44),
               "niveau " + f"{niv}" + " (voxel " + f"{n['voxel_um']:g}" + " µm)",
               fill=c, font=p)
        d.text((marge + larg + 16, marge + 28 + i * 44),
               f"α = {n['alpha']:+.2f}", fill=c, font=p)

    a = [n["alpha"] for n in niveaux]
    ecart = max(a) - min(a)
    d.text((marge, H - 34),
           "écart entre les deux pentes : " + f"{ecart:.2f}"
           + "   résolution de α : " + f"{resolution_alpha}",
           fill=ENCRE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"niveaux": len(niveaux), "ecart": round(ecart, 3), "largeur": L, "hauteur": H,
            "graduations": graduations,
            "dans_la_resolution": ecart <= resolution_alpha,
            "intraduits": d.intraduits(),
            "inchanges": [x for x in d.inchanges() if x not in NE_PAS_TRADUIRE]}


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    # ⚠⚠ La sonde qui porte l axe : au niveau 1, 21 tranches de 4,8 µm couvrent 100,8 µm,
    # soit ce que 41 tranches de 2,4 couvrent (98,4). En profondeur PHYSIQUE les deux
    # series se superposent ; en compte de tranches elles seraient decalees d un facteur
    # deux, et la figure montrerait un desaccord qui n existe pas.
    s0 = series_physiques([[41, 45.6], [161, 158.4]], 2.4)
    s1 = series_physiques([[21, 48.0], [81, 144.0]], 4.8)
    v("le niveau 0 est converti en µm", abs(s0[0][0] - 98.4) < 1e-9, str(s0[0]))
    v("le niveau 1 aussi", abs(s1[0][0] - 100.8) < 1e-9, str(s1[0]))
    v("... et les deux premières fenêtres coïncident à 3 %",
      abs(s0[0][0] - s1[0][0]) / s0[0][0] < 0.03)
    v("... les secondes aussi",
      abs(s0[1][0] - s1[1][0]) / s0[1][0] < 0.03, f"{s0[1][0]} vs {s1[1][0]}")
    # ⚠ Le controle : SANS conversion, les abscisses seraient decalees d un facteur ~2.
    v("sans conversion, l'écart serait grossier", abs(41 - 21) / 41 > 0.4)

    reel = [{"niveau": 0, "voxel_um": 2.4, "alpha": 0.9104, "serie": [[41, 45.6], [161, 158.4]]},
            {"niveau": 1, "voxel_um": 4.8, "alpha": 0.8900, "serie": [[21, 48.0], [81, 144.0]]}]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "p.png"
        r = dessiner(reel, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux niveaux sont dessinés", r["niveaux"] == 2)
        v("l'écart est chiffré", abs(r["ecart"] - 0.0204) < 1e-3, str(r["ecart"]))
        v("... et déclaré dans la résolution", r["dans_la_resolution"])
        px = _pixels(Image.open(f).convert("RGB"))
        v("la série du niveau 0 est tracée", NIVEAU0 in px)
        v("celle du niveau 1 aussi", NIVEAU1 in px)
        # ⚠⚠ Sans la droite de pente 1, « α ≈ 1 » est un chiffre a croire et pas a voir.
        v("la droite de pente 1 est tracée", PENTE1 in px)
        # ⚠ Sans graduations, une figure log-log ne laisse lire aucune grandeur : deux
        # droites paralleles sans echelle pourraient parler de dix microns ou de mille.
        v("les deux axes portent des graduations", r["graduations"] >= 4,
          str(r["graduations"]))
        # ⚠ Le controle du verdict : un ecart au-dela de la resolution doit etre dit hors.
        loin = [dict(reel[0]), dict(reel[1], alpha=0.30)]
        v("un écart au-delà de la résolution est signalé",
          not dessiner(loin, Path(td) / "p2.png")["dans_la_resolution"])
        f3 = Path(td) / "en.png"
        r3 = dessiner(reel, f3, anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))
        try:
            dessiner([], Path(td) / "vide.png")
            v("une série vide est refusée", False)
        except ValueError:
            v("une série vide est refusée", True)

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs", type=Path, default=Path("docs"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/50_pyramide.png"))
    ap.add_argument("--voxel-base", type=float, default=2.4)
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    niveaux = []
    for f in sorted(a.docs.glob("resolution_g*.json")):
        niv = int(f.stem.split("g")[-1])
        d = json.loads(f.read_text(encoding="utf-8"))
        for x in (d.get("series") or ([d] if "alpha" in d else [])):
            if isinstance(x.get("alpha"), (int, float)) and x.get("serie"):
                niveaux.append({"niveau": niv, "voxel_um": a.voxel_base * 2 ** niv,
                                "alpha": x["alpha"], "serie": x["serie"]})
    if len(niveaux) < 2:
        print("il faut au moins deux niveaux mesurés", file=sys.stderr)
        return 2
    r = dessiner(niveaux, a.sortie, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ non traduits : " + ", ".join(r["intraduits"] + r["inchanges"]),
              file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, "
          f"{r['niveaux']} niveaux, écart {r['ecart']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
