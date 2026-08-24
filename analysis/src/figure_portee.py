#!/usr/bin/env python3
"""Jusqu'où la tangente d'une nappe reste-t-elle sur la nappe ?

⚠⚠ CE QUE LA FIGURE DOIT RENDRE ÉVIDENT, et qu'un tableau de trois lignes ne rend pas : la
dégradation est **progressive et monotone**, pas un décrochement. Ce n'est pas la même
nouvelle — un décrochement dirait « au-delà de X, rien » et donnerait un pas de chaîne franc ;
une pente dit qu'il faut **choisir** le pas contre un budget de rendus.

⭐ Deux grandeurs sur un seul axe parce qu'elles disent la même chose de deux façons :
l'**amplitude** tombe (le profil s'aplatit) pendant que le **pic au bord** monte (la surface
sort de la fenêtre). Les tracer séparément laisserait croire à deux mesures indépendantes qui
se confirment, alors que c'est une seule dégradation vue de deux côtés.

⚠ L'axe des abscisses est en **micromètres**, jamais en pas de grille : un pas de grille ne
veut rien dire hors de la nappe qui l'a produit, et la question posée est physique.

⚠⚠ Et la figure porte sa propre limite : ces points mesurent une projection **pure**, sans
réoptimisation. Une vraie chaîne recollerait la nappe projetée sur la matière. C'est donc le
**plancher** de ce qu'une chaîne tangentielle peut faire, pas son plafond.
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
AMPLITUDE = (74, 132, 96)
AU_BORD = (196, 72, 60)

ANGLAIS = {
    "jusqu'où la tangente reste-t-elle sur la feuille": "how far does the tangent stay on the sheet",
    "⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, pas son plafond":
        "⚠ PURE projection, no re-optimisation: this is a chain's floor, not its ceiling",
    "amplitude du profil": "profile amplitude",
    "pic au bord de la pile": "peak at the stack edge",
    "déplacement le long de la tangente": "displacement along the tangent",
    "contrôle": "control",
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


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def monotone(valeurs: list[float], croissant: bool) -> bool:
    """La suite est-elle monotone ? — c'est l'énoncé que la figure prétend montrer.

    ⚠ Vérifié plutôt qu'affirmé : une figure qui annonce « progressif et monotone » sur des
    points qui ne le sont pas est une figure qui ment, et personne ne recompte trois nombres.
    """
    paires = zip(valeurs, valeurs[1:])
    return all((b >= a) if croissant else (b <= a) for a, b in paires)


def dessiner(points: list[dict], sortie: Path, anglais: bool = False) -> dict:
    """Amplitude et pic-au-bord contre le déplacement, sur un axe partagé."""
    if len(points) < 2:
        raise ValueError("moins de deux points — une tendance a besoin d'au moins deux points")
    g1, g2, g3 = _police()
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        for fr, en in sorted(ANGLAIS.items(), key=lambda kv: -len(kv[0])):
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    largeur, hauteur = 640, 356
    gx, gy = 76, 78
    gw, gh = largeur - gx - 40, hauteur - gy - 78
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    d.text((24, 16), T("jusqu'où la tangente reste-t-elle sur la feuille"), font=g1, fill=ENCRE)

    xs = [p["um"] for p in points]
    xmax = max(xs) or 1.0
    # ⚠ L'axe des y est FIXÉ de 0 à 1 pour les deux grandeurs : ce sont deux fractions, et les
    # mettre chacune à sa propre échelle ferait paraître identiques deux pentes qui ne le sont
    # pas — le piège le plus commun d'un graphe à deux courbes.
    def X(v):
        return gx + gw * (v / xmax)

    def Y(v):
        return gy + gh * (1.0 - max(0.0, min(1.0, v)))

    for k in range(5):
        y = gy + gh * k / 4
        d.line([(gx, y), (gx + gw, y)], fill=TRAIT, width=1)
        d.text((gx - 32, y - 7), f"{1.0 - k / 4:.2f}".replace(".", ","), font=g3, fill=GRIS)
    d.line([(gx, gy + gh), (gx + gw, gy + gh)], fill=GRIS, width=1)

    for p in points:
        d.line([(X(p["um"]), gy + gh), (X(p["um"]), gy + gh + 5)], fill=GRIS, width=1)
        t = f"{p['um']:.0f}"
        d.text((X(p["um"]) - d.textlength(t, font=g3) / 2, gy + gh + 8), t, font=g3, fill=GRIS)
    d.text((gx, gy + gh + 26), T("déplacement le long de la tangente") + " (µm)",
           font=g3, fill=GRIS)

    # ⚠⚠ La LÉGENDE est en haut, jamais au bout de la courbe. Premier tirage : les deux noms
    # de série débordaient du canevas et se superposaient à la dernière valeur — un libellé
    # coupé ne dit rien et fait douter du reste. Ici la place est connue d'avance.
    lx = gx
    for cle, couleur, nom in (("amplitude", AMPLITUDE, "amplitude du profil"),
                              ("au_bord", AU_BORD, "pic au bord de la pile")):
        d.rectangle([lx, 50, lx + 12, 58], fill=couleur)
        t = T(nom)
        d.text((lx + 17, 47), t, font=g3, fill=couleur)
        lx += 17 + int(d.textlength(t, font=g3)) + 22
    depassement = max(0, lx - (largeur - 24))

    for cle, couleur in (("amplitude", AMPLITUDE), ("au_bord", AU_BORD)):
        pts = [(X(p["um"]), Y(p[cle])) for p in points]
        d.line(pts, fill=couleur, width=2)
        for i, ((x, y), p) in enumerate(zip(pts, points)):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)
            t = f"{p[cle]:.3f}".replace(".", ",")
            w = d.textlength(t, font=g3)
            # ⚠ La dernière valeur s'écrit à GAUCHE de son point : à droite elle sortirait.
            tx = x - w - 8 if i == len(pts) - 1 else x + 7
            d.text((tx, y - 6), t, font=g3, fill=couleur)

    d.text((X(points[0]["um"]) - 12, gy - 16), T("contrôle"), font=g3, fill=GRIS)
    d.line([(24, hauteur - 30), (largeur - 24, hauteur - 30)], fill=TRAIT, width=1)
    d.text((24, hauteur - 24),
           T("⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, "
             "pas son plafond"), font=g3, fill=GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    return {"points": len(points), "largeur": largeur, "hauteur": hauteur,
            # ⚠⚠ Ce que la sonde peut vraiment vérifier : qu'aucun libellé ne dépasse du
            # canevas. Un texte coupé est invisible pour un test qui ne regarde que les
            # couleurs, et c'est exactement ce qui est passé au premier tirage.
            "depassement": int(depassement),
            "amplitude_decroissante": monotone([p["amplitude"] for p in points], False),
            "au_bord_croissant": monotone([p["au_bord"] for p in points], True),
            "intraduits": intraduits, "inchanges": inchanges}


def points_du_depot(racine: Path, voxel_um: float = 2.4) -> list[dict]:
    """Les trois mesures, lues dans les profils écrits par la campagne."""
    out = []
    for d in sorted(racine.glob("profil_*/g*_n*/profil.json"),
                    key=lambda p: int(p.parent.parent.name.split("_")[1])):
        pas = int(d.parent.parent.name.split("_")[1])
        meta = json.loads((racine / f"pas_{pas}" / "meta.json").read_text(encoding="utf-8"))
        prof = json.loads(d.read_text(encoding="utf-8"))[0]
        out.append({"pas": pas, "um": float(meta["pas_voxels"]) * voxel_um,
                    "amplitude": float(prof["amplitude_mediane"]),
                    "au_bord": float(prof["au_bord_intensite"])})
    return out


def _verifier() -> int:
    import tempfile

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    v("une suite décroissante est vue décroissante", monotone([3.0, 2.0, 1.0], False))
    v("... et pas croissante", not monotone([3.0, 2.0, 1.0], True))
    v("une suite croissante est vue croissante", monotone([1.0, 2.0, 3.0], True))
    # ⚠ Un plateau est monotone au sens large : deux mesures égales ne réfutent pas une pente.
    v("un plateau est monotone", monotone([2.0, 2.0], False) and monotone([2.0, 2.0], True))
    v("une bosse ne l'est pas", not monotone([1.0, 3.0, 2.0], True))

    faux = [{"pas": 0, "um": 0.0, "amplitude": 0.19, "au_bord": 0.06},
            {"pas": 10, "um": 476.0, "amplitude": 0.11, "au_bord": 0.18},
            {"pas": 50, "um": 2381.0, "amplitude": 0.04, "au_bord": 0.61}]
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner(faux, f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les trois points sont tracés", r["points"] == 3)
        # ⚠⚠ LE CONTRÔLE QUI PORTE LA FIGURE : elle annonce une dégradation monotone, donc
        # elle doit refuser de le dire si les points ne le sont pas.
        v("l'amplitude est vue décroissante", r["amplitude_decroissante"])
        v("le pic au bord est vu croissant", r["au_bord_croissant"])
        casse = [faux[0], {"pas": 10, "um": 476.0, "amplitude": 0.9, "au_bord": 0.01}, faux[2]]
        r2 = dessiner(casse, Path(td) / "b.png")
        v("... et une amplitude qui remonte est vue non monotone",
          not r2["amplitude_decroissante"])
        px = _pixels(Image.open(f).convert("RGB"))
        v("aucun libellé ne déborde du canevas", r["depassement"] == 0,
          f"{r['depassement']} px")
        v("la courbe d'amplitude est tracée", AMPLITUDE in px)
        v("celle du pic au bord aussi", AU_BORD in px)
        try:
            dessiner([faux[0]], Path(td) / "c.png")
            v("un seul point est refusé", False)
        except ValueError:
            v("un seul point est refusé", True)
        r3 = dessiner(faux, Path(td) / "en.png", anglais=True)
        v("aucun libellé ne reste en français", not r3["intraduits"],
          ", ".join(r3["intraduits"]))
        v("chaque libellé porteur d'un mot a été touché par la table",
          not r3["inchanges"], ", ".join(r3["inchanges"]))
        # ⚠⚠ Le débordement se vérifie AUSSI en anglais : « profile amplitude » et « peak at
        # the stack edge » sont plus longs que leurs équivalents français, donc une légende
        # qui tient en français peut sortir du canevas une fois traduite. Ma première version
        # de ce contrôle était écrite `if False else True` — une sonde incapable d'échouer,
        # dans une session qui n'a parlé que de ça.
        v("... et aucun ne déborde en anglais non plus", r3["depassement"] == 0,
          f"{r3['depassement']} px")

    ok = all(o for _, o, _ in ech)
    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--racine", type=Path, default=Path("data/portee_tangentielle"))
    p.add_argument("--voxel-um", type=float, default=2.4)
    p.add_argument("--sortie", type=Path,
                   default=Path("docs/images/44_portee_tangentielle.png"))
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return _verifier()
    pts = points_du_depot(a.racine, a.voxel_um)
    if len(pts) < 2:
        print(f"refus : {len(pts)} point(s) dans {a.racine} — il en faut au moins deux",
              file=sys.stderr)
        return 3
    r = dessiner(pts, a.sortie, a.anglais)
    print(f"écrit : {a.sortie}  ({r['points']} points, "
          f"amplitude {'décroissante' if r['amplitude_decroissante'] else '⚠ NON monotone'}, "
          f"pic au bord {'croissant' if r['au_bord_croissant'] else '⚠ NON monotone'})")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"points": pts, **{k: v for k, v in r.items()
                                                        if k.startswith(("amplitude", "au_bord"))}},
                                     indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
