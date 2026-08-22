#!/usr/bin/env python3
"""Ce que coûte un cache de chunks, et où la machine bascule.

⚠⚠ **Ce que cette figure doit montrer et qu'un tableau montre mal** : il y a deux
grandeurs et un mur. Le temps et le pic de mémoire varient avec `--cache-gb`, et
*quelque part* la somme dépasse la RAM de la machine — au-delà, le temps mesuré cesse
de décrire un calcul et décrit un swap. Le mur n'est pas une donnée de la série : c'est
une propriété de la machine, et il doit être **dessiné** au milieu des points, sinon on
lit une courbe de performance là où il y a une falaise.

⚠ Les deux axes sont sur la même figure mais **jamais sur la même échelle** : des
secondes et des gibioctets n'ont pas de rapport, et les superposer sur un axe commun
serait suggérer une comparaison qui n'existe pas. Deux panneaux empilés, un axe chacun.

⭐ Et la barre qui compte le plus n'est mesurée nulle part : c'est la **projection** de
la fenêtre profonde, calculée depuis la géométrie du rendu. Elle est dessinée en creux
pour qu'on ne la confonde pas avec une mesure.
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
TEMPS = (86, 104, 132)
MEM = (176, 128, 62)
MUR = (196, 72, 60)
PROJ = (196, 72, 60)


# ⚠ Les libellés qu'on NE traduit PAS, nommés un par un. `--cache-gb` est le nom d'un
# drapeau de ligne de commande : le traduire produirait une figure qui montre une option
# qui n'existe pas. Les tolérer en silence rouvrirait le trou que `inchanges` vient de
# fermer, donc la liste est explicite et courte.
NE_PAS_TRADUIRE = {"--cache-gb"}


def _pixels(im):
    """Les pixels d'une image, quelle que soit la version de Pillow."""
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


def dessiner(essais: list[dict], sortie: Path, ram_go: float | None = None,
             projection_go: float | None = None, anglais: bool = False) -> dict:
    p, pp, pg = _police()
    ok = [e for e in essais if e.get("secondes", 0) > 0]
    if not ok:
        raise ValueError("aucun essai chronométré")
    ok = sorted(ok, key=lambda e: e["cache_gb"])
    for e in ok:
        e["pic_go"] = e["pic_rss_kio"] / 1048576.0

    marge, larg_pan, haut_pan, ecart = 70, 640, 170, 56
    L = marge * 2 + larg_pan
    H = marge + 40 + haut_pan + ecart + haut_pan + 60
    img = Image.new("RGB", (L, H), FOND)
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)

    d.text((marge, marge - 42), "Ce que coûte le cache de chunks du rendu",
           fill=ENCRE, font=pg)
    d.text((marge, marge - 21),
           "même surface, même fenêtre ; seul --cache-gb change", fill=GRIS, font=pp)

    xs = [e["cache_gb"] for e in ok]
    lo, hi = min(xs), max(xs)

    def x_de(v: float) -> int:
        # ⚠ Échelle LOGARITHMIQUE : les valeurs testées doublent (1, 2, 4, 8, 16), donc une
        # échelle linéaire écraserait la moitié des points contre l'axe et ferait croire
        # que rien ne se passe en dessous de 8.
        import math
        f = (math.log2(v) - math.log2(lo)) / max(1e-9, math.log2(hi) - math.log2(lo))
        return marge + int(f * larg_pan)

    for i, (cle, couleur, unite, titre) in enumerate(
            (("secondes", TEMPS, "s", "temps de rendu"),
             ("pic_go", MEM, "Go", "pic de mémoire résidente"))):
        y0 = marge + 40 + i * (haut_pan + ecart)
        vals = [e[cle] for e in ok]
        vmax = max(vals)
        if cle == "pic_go":
            # ⚠⚠ Le cadre doit contenir le MUR et la PROJECTION, sinon la figure recadre
            # exactement ce qu'elle existe pour montrer.
            vmax = max([vmax] + [x for x in (ram_go, projection_go) if x])
        vmax *= 1.15

        def y_de(v: float) -> int:
            return y0 + haut_pan - int(min(1.0, v / vmax) * haut_pan)

        d.text((marge, y0 - 20), titre, fill=ENCRE, font=p)
        d.line([(marge, y0 + haut_pan), (marge + larg_pan, y0 + haut_pan)],
               fill=(215, 213, 208), width=1)

        if cle == "pic_go":
            if ram_go:
                yr = y_de(ram_go)
                for x in range(marge, marge + larg_pan, 9):
                    d.line([(x, yr), (x + 5, yr)], fill=MUR, width=2)
                d.text((marge + 4, yr - 16),
                       "RAM de la machine — au-delà, du swap", fill=MUR, font=pp)
            if projection_go:
                yp = y_de(projection_go)
                d.rectangle([marge, yp, marge + larg_pan, y_de(0)], outline=PROJ)
                d.text((marge + 4, yp + 4),
                       "projection de la fenêtre profonde (non mesurée)",
                       fill=PROJ, font=pp)

        pts = [(x_de(e["cache_gb"]), y_de(e[cle])) for e in ok]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=couleur, width=2)
        for e, (x, y) in zip(ok, pts):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)
            t = f"{e[cle]:.0f} {unite}" if cle == "secondes" else f"{e[cle]:.1f} {unite}"
            d.text((x - 14, y - 20), t, fill=couleur, font=pp)

        for e in ok:
            d.text((x_de(e["cache_gb"]) - 6, y0 + haut_pan + 6),
                   f"{e['cache_gb']}", fill=GRIS, font=pp)
        d.text((marge + larg_pan - 60, y0 + haut_pan + 22), "--cache-gb",
               fill=GRIS, font=pp)

    emp = {e.get("empreinte") for e in ok if e.get("empreinte")}
    d.text((marge, H - 40),
           f"{len(ok)} essais · " + ("sorties identiques — le réglage ne change pas l'image"
                                     if len(emp) <= 1 else
                                     "⚠ les sorties DIFFÈRENT — ce n'est pas un réglage de performance"),
           fill=ENCRE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"essais": len(ok), "largeur": L, "hauteur": H,
            "sorties_identiques": len(emp) <= 1, "intraduits": d.intraduits(),
            "inchanges": [x for x in d.inchanges() if x not in NE_PAS_TRADUIRE]}


ANGLAIS = {
    "Ce que coûte le cache de chunks du rendu": "What the render's chunk cache costs",
    "même surface, même fenêtre ; seul --cache-gb change":
        "same surface, same window; only --cache-gb changes",
    "temps de rendu": "render time",
    "pic de mémoire résidente": "peak resident memory",
    "RAM de la machine — au-delà, du swap": "machine RAM — beyond it, swap",
    "projection de la fenêtre profonde (non mesurée)":
        "deep-window projection (not measured)",
    " essais · ": " runs · ",
    "sorties identiques — le réglage ne change pas l'image":
        "identical outputs — the setting does not change the image",
    "⚠ les sorties DIFFÈRENT — ce n'est pas un réglage de performance":
        "⚠ outputs DIFFER — this is not a performance setting",
}


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    def e(gb, sec, go, emp="aaa"):
        return {"cache_gb": gb, "secondes": sec,
                "pic_rss_kio": int(go * 1048576), "empreinte": emp}

    base = [e(1, 65, 2.0), e(2, 62, 2.9), e(4, 100, 4.4), e(8, 95, 8.1), e(16, 99, 15.5)]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "e.png"
        r = dessiner(base, f, ram_go=31.8, projection_go=38.2)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les cinq essais sont dessinés", r["essais"] == 5)
        px = _pixels(Image.open(f).convert("RGB"))
        v("le mur de RAM est tracé", MUR in px)
        v("la courbe du temps est tracée", TEMPS in px)
        v("la courbe de mémoire est tracée", MEM in px)
        # ⚠⚠ Le controle qui porte la figure : la projection DEPASSE la RAM, donc si le
        # cadre etait borne par les seules mesures, elle serait recadree hors champ --
        # c est-a-dire que la figure supprimerait exactement ce qu elle existe pour montrer.
        f2 = Path(td) / "e2.png"
        dessiner(base, f2, ram_go=31.8, projection_go=None)
        v("sans projection, la figure se dessine quand même",
          f2.stat().st_size > 0)
        # une projection tres au-dessus doit rester visible : le cadre s etend
        f3 = Path(td) / "e3.png"
        r3 = dessiner(base, f3, ram_go=31.8, projection_go=120.0)
        v("une projection énorme ne sort pas du cadre", r3["hauteur"] == r["hauteur"])
        v("... et reste dessinée", PROJ in _pixels(Image.open(f3).convert("RGB")))
        # ⚠ Sorties differentes : la figure doit le DIRE, pas le taire.
        f4 = Path(td) / "e4.png"
        r4 = dessiner([e(1, 65, 2.0, "aaa"), e(2, 62, 2.9, "bbb")], f4)
        v("des sorties différentes sont signalées", not r4["sorties_identiques"])
        # ⚠ L anglais doit etre complet.
        f5 = Path(td) / "en.png"
        r5 = dessiner(base, f5, ram_go=31.8, projection_go=38.2, anglais=True)
        v("aucun libellé ne reste en français", not r5["intraduits"],
          ", ".join(r5["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r5["inchanges"], ", ".join(r5["inchanges"]))
        # ⚠ Et la liste d'exceptions doit rester COURTE et justifiée : si elle grossit, le
        # contrôle se vide. Une exception est un nom de drapeau ou un nom propre, rien d'autre.
        v("les exceptions de traduction sont peu nombreuses", len(NE_PAS_TRADUIRE) <= 3,
          str(NE_PAS_TRADUIRE))
        v("... et toutes commencent par un tiret ou une majuscule",
          all(x[0] in "-" or x[0].isupper() for x in NE_PAS_TRADUIRE))
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
    ap.add_argument("--json", type=Path, default=Path("docs/etalon_rendu.json"))
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/50_etalon_rendu.png"))
    ap.add_argument("--ram-go", type=float)
    ap.add_argument("--projection-go", type=float)
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    d = json.loads(a.json.read_text(encoding="utf-8"))
    ram = a.ram_go
    if ram is None:
        try:
            for l in open("/proc/meminfo"):
                if l.startswith("MemTotal:"):
                    ram = int(l.split()[1]) / 1048576.0
                    break
        except Exception:
            ram = None
    r = dessiner(d.get("essais") or [], a.sortie, ram_go=ram,
                 projection_go=a.projection_go, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ libellés non traduits : "
              + ", ".join(r["intraduits"] + r["inchanges"]), file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['essais']} essais)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
