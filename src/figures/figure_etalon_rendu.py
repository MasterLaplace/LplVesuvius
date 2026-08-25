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
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import police  # noqa: E402

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




def dessiner(essais: list[dict], sortie: Path, ram_go: float | None = None,
             projections: list[tuple[str, float]] | None = None,
             anglais: bool = False) -> dict:
    """Trois panneaux, parce qu'il y a trois échelles et qu'aucune n'accepte les autres.

    ⚠⚠ **Le défaut de ma première version, corrigé ici.** Elle traçait les *quinze* essais
    reliés dans l'ordre, donc une ligne qui zigzague entre répétitions d'une même valeur : on
    lisait une variation du réglage là où il y a de la variance de run. Ce sont les
    **médianes** qui sont reliées, et l'étendue de chaque valeur est dessinée en moustache —
    c'est elle qui dit si la ligne veut dire quelque chose.

    ⚠⚠ **Et la projection ne partage pas l'axe des mesures.** Superposer 38 Go à des mesures
    de 1,8 à 4,5 Go aplatit ces dernières en une ligne au ras de l'axe : la figure supprime
    ce qu'elle mesure pour montrer ce qu'elle extrapole. Le troisième panneau a son propre
    axe et son propre titre, et dit en clair qu'il n'est pas mesuré.
    """
    p, pp, pg = police(13, 11, 15)
    ok = _grouper(essais)
    if not ok:
        raise ValueError("aucun essai chronométré")

    marge, larg_pan, haut_pan, ecart = 74, 600, 132, 62
    haut_proj = 30 * (len(projections or []) + (1 if ram_go else 0)) + 40
    L = marge * 2 + larg_pan + 60
    H = marge + 40 + 2 * (haut_pan + ecart) + haut_proj + 40
    img = Image.new("RGB", (L, H), FOND)
    import langue
    d = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)

    d.text((marge, marge - 46), "Ce que coûte le cache de chunks du rendu",
           fill=ENCRE, font=pg)
    d.text((marge, marge - 25),
           "même surface, même fenêtre ; seul --cache-gb change", fill=GRIS, font=pp)

    import math
    xs = [e["cache_gb"] for e in ok]
    lo, hi = min(xs), max(xs)

    def x_de(v: float) -> int:
        # ⚠ Échelle logarithmique : les valeurs doublent, une échelle linéaire écraserait
        # la moitié des points contre l'axe.
        f = (math.log2(v) - math.log2(lo)) / max(1e-9, math.log2(hi) - math.log2(lo))
        return marge + int(f * larg_pan)

    moustaches = 0
    for i, (cle, bas, haut, couleur, unite, titre) in enumerate(
            (("secondes", "t_min", "t_max", TEMPS, "s", "temps de rendu"),
             ("pic_go", "m_min", "m_max", MEM, "Go", "pic de mémoire résidente"))):
        y0 = marge + 40 + i * (haut_pan + ecart)
        vmax = max(e[haut] for e in ok) * 1.18
        def y_de(v: float, y0=y0, vmax=vmax) -> int:
            return y0 + haut_pan - int(min(1.0, v / vmax) * haut_pan)

        d.text((marge, y0 - 20), titre, fill=ENCRE, font=p)
        d.line([(marge, y0 + haut_pan), (marge + larg_pan, y0 + haut_pan)],
               fill=(215, 213, 208), width=1)

        pts = [(x_de(e["cache_gb"]), y_de(e[cle])) for e in ok]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=couleur, width=2)
        for e, (x, y) in zip(ok, pts):
            # ⚠⚠ La moustache EST l'argument : sans elle, une médiane plus basse ressemble
            # à un réglage meilleur même quand les nuages se recouvrent entièrement.
            if e[haut] > e[bas]:
                yb, yh = y_de(e[bas]), y_de(e[haut])
                d.line([(x, yb), (x, yh)], fill=couleur, width=1)
                d.line([(x - 4, yb), (x + 4, yb)], fill=couleur, width=1)
                d.line([(x - 4, yh), (x + 4, yh)], fill=couleur, width=1)
                moustaches += 1
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)
            t = f"{e[cle]:.0f} {unite}" if cle == "secondes" else f"{e[cle]:.1f} {unite}"
            d.text((x + 8, y - 6), t, fill=couleur, font=pp)

        for e in ok:
            d.text((x_de(e["cache_gb"]) - 6, y0 + haut_pan + 6),
                   f"{e['cache_gb']}", fill=GRIS, font=pp)
        d.text((marge + larg_pan - 56, y0 + haut_pan + 22), "--cache-gb", fill=GRIS, font=pp)

    # ⚠⚠ Troisieme panneau, son propre axe : ce que demanderait la grande surface. Ce ne
    # sont PAS des mesures et le titre le dit -- une extrapolation dessinee comme une mesure
    # est la facon la plus economique de se tromper soi-meme plus tard.
    y0 = marge + 40 + 2 * (haut_pan + ecart)
    d.text((marge, y0 - 20), "ce que demanderait la grande surface (projeté, non mesuré)",
           fill=ENCRE, font=p)
    barres = list(projections or [])
    mmax = max([v for _, v in barres] + [ram_go or 0, max(e["m_max"] for e in ok)]) * 1.12
    franchit = 0
    for k, (nom, val) in enumerate(barres):
        yb = y0 + k * 30
        w = int(larg_pan * val / mmax)
        d.rectangle([marge, yb, marge + w, yb + 18],
                    fill=PROJ if (ram_go and val > ram_go) else MEM)
        if ram_go and val > ram_go:
            franchit += 1
        d.text((marge + w + 8, yb + 2), f"{val:.1f} Go", fill=ENCRE, font=pp)
        d.text((marge + 6, yb + 2), nom, fill=FOND, font=pp)
    if ram_go:
        xr = marge + int(larg_pan * ram_go / mmax)
        d.line([(xr, y0 - 6), (xr, y0 + 30 * max(1, len(barres)))], fill=MUR, width=2)
        d.text((xr + 6, y0 + 30 * max(1, len(barres)) + 2),
               "RAM de la machine — au-delà, du swap", fill=MUR, font=pp)

    emp = {e.get("empreinte") for e in ok if e.get("empreinte")}
    n_essais = sum(e["n"] for e in ok)
    d.text((marge, H - 26),
           f"{n_essais}" + (" essais · sorties identiques — le réglage ne change pas l'image"
                            if len(emp) <= 1 else
                            " essais · ⚠ les sorties DIFFÈRENT — ce n'est pas un réglage de performance"),
           fill=ENCRE, font=p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"essais": n_essais, "valeurs": len(ok), "largeur": L, "hauteur": H,
            "moustaches": moustaches, "barres_au_dela_de_la_ram": franchit,
            "sorties_identiques": len(emp) <= 1, "intraduits": d.intraduits(),
            "inchanges": [x for x in d.inchanges() if x not in NE_PAS_TRADUIRE]}


def _grouper(essais: list[dict]) -> list[dict]:
    """Une ligne par valeur : médiane et étendue de ses répétitions.

    ⚠ La médiane et pas la moyenne : un essai qui tombe sur une lenteur réseau tire une
    moyenne sans limite, et le cache disque n'est pas matérialisé ici — chaque essai
    retélécharge.
    """
    par: dict[int, list[dict]] = {}
    for e in essais:
        if e.get("secondes", 0) > 0:
            par.setdefault(e["cache_gb"], []).append(e)

    def med(v):
        x = sorted(v); n = len(x)
        return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2

    out = []
    for gb, lot in sorted(par.items()):
        t = [x["secondes"] for x in lot]
        m = [x["pic_rss_kio"] / 1048576.0 for x in lot]
        out.append({"cache_gb": gb, "n": len(lot), "secondes": med(t), "pic_go": med(m),
                    "t_min": min(t), "t_max": max(t), "m_min": min(m), "m_max": max(m),
                    "empreinte": lot[0].get("empreinte")})
    return out


ANGLAIS = {
    "Ce que coûte le cache de chunks du rendu": "What the render's chunk cache costs",
    "même surface, même fenêtre ; seul --cache-gb change":
        "same surface, same window; only --cache-gb changes",
    "temps de rendu": "render time",
    "pic de mémoire résidente": "peak resident memory",
    "RAM de la machine — au-delà, du swap": "machine RAM — beyond it, swap",
    "ce que demanderait la grande surface (projeté, non mesuré)":
        "what the large surface would need (projected, not measured)",
    "fenêtre 41 au défaut": "41-layer window at the default",
    "fenêtre 41 à --cache-gb 1": "41-layer window at --cache-gb 1",
    "fenêtre 161 à --cache-gb 1": "161-layer window at --cache-gb 1",
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

    def e(gb, sec, go, rep=1, emp="aaa"):
        return {"cache_gb": gb, "repetition": rep, "secondes": sec,
                "pic_rss_kio": int(go * 1048576), "empreinte": emp}

    # Trois repetitions par valeur, comme la vraie serie.
    base = []
    for gb, ts, go in ((1, (67, 71, 81), 1.8), (2, (144, 110, 82), 3.0),
                       (4, (125, 103, 118), 4.4), (8, (141, 153, 129), 4.5),
                       (16, (125, 148, 135), 4.5)):
        base += [e(gb, t, go, r + 1) for r, t in enumerate(ts)]
    PROJ_REELLES = [("fenêtre 41 au défaut", 25.7),
                    ("fenêtre 41 à --cache-gb 1", 10.7),
                    ("fenêtre 161 à --cache-gb 1", 39.2)]

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "e.png"
        r = dessiner(base, f, ram_go=31.8, projections=PROJ_REELLES)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les quinze essais sont comptés", r["essais"] == 15, str(r["essais"]))
        v("... mais cinq points seulement sont tracés", r["valeurs"] == 5)
        # ⚠⚠ La sonde du defaut corrige : sans regroupement, la figure reliait les QUINZE
        # essais dans l ordre -- une ligne qui zigzague entre repetitions d une meme valeur,
        # donc de la variance de run lue comme un effet du reglage.
        v("chaque valeur porte une moustache d'étendue", r["moustaches"] == 5,
          str(r["moustaches"]))
        px = _pixels(Image.open(f).convert("RGB"))
        v("le mur de RAM est tracé", MUR in px)
        v("la courbe du temps est tracée", TEMPS in px)
        v("la courbe de mémoire est tracée", MEM in px)
        # ⚠⚠ Le controle qui porte le troisieme panneau : exactement UNE projection franchit
        # la RAM. Si aucune ne la franchissait, le panneau ne montrerait rien ; si toutes la
        # franchissaient, il ne distinguerait rien.
        v("une seule projection franchit la RAM", r["barres_au_dela_de_la_ram"] == 1,
          str(r["barres_au_dela_de_la_ram"]))
        v("... et elle est peinte de la couleur d'alerte", PROJ in px)

        # ⚠ Sans projection, la figure doit se dessiner quand meme -- un etalonnage seul
        # est un resultat.
        f2 = Path(td) / "e2.png"
        r2 = dessiner(base, f2, ram_go=31.8)
        v("sans projection, la figure se dessine", f2.stat().st_size > 0)
        v("... et n'invente aucune barre", r2["barres_au_dela_de_la_ram"] == 0)

        # ⚠ Une valeur sans repetition n a pas de moustache, et ce n est pas un defaut :
        # une etendue nulle ne doit pas etre dessinee comme une etendue.
        f3 = Path(td) / "e3.png"
        r3 = dessiner([e(1, 70, 1.8), e(8, 140, 4.5)], f3, ram_go=31.8)
        v("un essai unique par valeur ne dessine pas de moustache", r3["moustaches"] == 0)

        f4 = Path(td) / "e4.png"
        r4 = dessiner([e(1, 65, 2.0, 1, "aaa"), e(2, 62, 2.9, 1, "bbb")], f4)
        v("des sorties différentes sont signalées", not r4["sorties_identiques"])

        f5 = Path(td) / "en.png"
        r5 = dessiner(base, f5, ram_go=31.8, projections=PROJ_REELLES, anglais=True)
        v("aucun libellé ne reste en français", not r5["intraduits"],
          ", ".join(r5["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r5["inchanges"], ", ".join(r5["inchanges"]))
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
    ap.add_argument("--projection", action="append", default=[],
                    metavar="NOM=GO",
                    help="barre du panneau projeté, ex. « fenêtre 161 à --cache-gb 1=39.2 »")
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
    proj = []
    for x in a.projection:
        nom, _, val = x.rpartition("=")
        proj.append((nom, float(val)))
    r = dessiner(d.get("essais") or [], a.sortie, ram_go=ram,
                 projections=proj, anglais=a.anglais)
    if a.anglais and (r["intraduits"] or r["inchanges"]):
        print("  ⚠ libellés non traduits : "
              + ", ".join(r["intraduits"] + r["inchanges"]), file=sys.stderr)
        return 3
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']}, {r['essais']} essais)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
