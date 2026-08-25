#!/usr/bin/env python3
"""Ce qu'α mesure, rendu visible : un croisillon contre un tourbillon.

⚠⚠ **Ce dépôt mesure α depuis des semaines sans avoir jamais REGARDÉ ce qu'il décrit.** α
est une grandeur géométrique — l'écart au pic suit-il la fenêtre — et rien ne garantissait
qu'elle corresponde à quelque chose de visible. Cette figure le vérifie.

⭐ Et la signature visuelle est nette, une fois qu'on sait quoi chercher. Du papyrus, c'est
**deux couches de fibres perpendiculaires** : la face d'un feuillet montre donc un
croisillon régulier. Une surface qui coupe l'empilement montre au contraire les **tranches**
de nombreux feuillets — des fibres qui tourbillonnent, changent de direction, s'interrompent.

⚠⚠ **La limite, dite avant la figure.** Les deux images viennent de rouleaux et de scans
DIFFÉRENTS. Ce n'est donc pas une comparaison contrôlée : c'est une illustration de deux
signatures, pas une preuve qu'α les sépare. La preuve, c'est α ; l'image dit seulement que
ce qu'α condamne ne ressemble pas à ce qu'il accepte.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sys
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from figure_commune import police  # noqa: E402

import numpy as np
from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
BON = (94, 156, 106)
MAUVAIS = (196, 72, 60)




def vignette(chemin: Path, cote: int) -> Image.Image:
    """Un carré pris au CENTRE de la surface, à la même taille pour les deux.

    ⚠⚠ **Prendre le centre, jamais l'image entière.** Les deux rendus n'ont ni la même
    taille ni la même forme ; les redimensionner à un cadre commun changerait l'échelle des
    fibres, donc exactement la chose qu'on compare. Un carré de même taille en pixels, pris
    au même endroit relatif, garde la texture comparable.
    """
    a = np.array(Image.open(chemin))
    if a.ndim == 3:
        a = a[..., 0]
    # ⚠ Le centre de la MATIÈRE, pas du fichier : une surface décentrée dans son cadre
    # donnerait une vignette de fond noir.
    ys, xs = np.nonzero(a)
    cy, cx = (int(ys.mean()), int(xs.mean())) if ys.size else (a.shape[0] // 2,
                                                               a.shape[1] // 2)
    d = cote // 2
    y0 = max(0, min(a.shape[0] - cote, cy - d))
    x0 = max(0, min(a.shape[1] - cote, cx - d))
    bout = a[y0:y0 + cote, x0:x0 + cote]
    if bout.shape != (cote, cote):
        pad = np.zeros((cote, cote), a.dtype)
        pad[:bout.shape[0], :bout.shape[1]] = bout
        bout = pad
    nz = bout[bout > 0]
    if nz.size:
        lo, hi = np.percentile(nz, [1, 99])
        if hi > lo:
            bout = np.clip((bout.astype(np.float32) - lo) / (hi - lo), 0, 1) * 255
            bout = bout.astype(np.uint8)
    return Image.fromarray(bout).convert("RGB")


def dessiner(gauche: dict, droite: dict, sortie: Path, cote: int = 460) -> dict:
    p, pp, pg = police(15, 12, 19)
    marge, ecart = 30, 34
    L = marge * 2 + cote * 2 + ecart
    H = marge + 62 + cote + 78
    img = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(img)

    d.text((marge, marge - 12), "Ce qu'α mesure, vu de près", fill=ENCRE, font=pg)
    d.text((marge, marge + 12),
           "un carré de même taille, pris au centre de chaque surface",
           fill=GRIS, font=pp)

    ecarts = []
    for i, spec in enumerate((gauche, droite)):
        x = marge + i * (cote + ecart)
        y = marge + 56
        v = vignette(Path(spec["image"]), cote)
        img.paste(v, (x, y))
        d.rectangle([x, y, x + cote, y + cote], outline=(200, 197, 192))
        c = BON if spec["alpha"] is None or abs(spec["alpha"]) < 0.7 else MAUVAIS
        d.text((x, y + cote + 8), spec["titre"], fill=c, font=p)
        d.text((x, y + cote + 28), spec["signature"], fill=ENCRE, font=pp)
        a = "α non mesuré" if spec["alpha"] is None else f"α = {spec['alpha']:+.2f}"
        d.text((x, y + cote + 46), a, fill=c, font=p)
        ecarts.append(float(np.array(v.convert("L")).std()))

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return {"largeur": L, "hauteur": H, "cote": cote,
            "ecart_type_gauche": round(ecarts[0], 1),
            "ecart_type_droite": round(ecarts[1], 1)}


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    import tempfile
    g = np.random.default_rng(3)
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        # ── Un « croisillon » synthetique et un « tourbillon » synthetique ────────
        n = 300
        croisillon = np.zeros((n, n), np.uint8)
        croisillon[::7, :] = 200
        croisillon[:, ::7] = 180
        Image.fromarray(croisillon).save(t / "croix.tif")
        yy, xx = np.mgrid[0:n, 0:n]
        tourbillon = ((np.sin(np.hypot(yy - n / 2, xx - n / 2) / 3.0) + 1) * 120)
        Image.fromarray(tourbillon.astype(np.uint8)).save(t / "tour.tif")

        # ⚠⚠ La sonde qui porte la figure : la vignette doit etre prise au centre de la
        # MATIERE. Une surface decentree dans son cadre donnerait un carre de fond noir,
        # et la figure comparerait deux rectangles vides sans rien dire.
        decentre = np.zeros((600, 600), np.uint8)
        decentre[20:120, 20:120] = g.integers(80, 200, (100, 100))
        Image.fromarray(decentre).save(t / "coin.tif")
        vg = np.array(vignette(t / "coin.tif", 120).convert("L"))
        v("la vignette suit la matière, pas le cadre", vg.std() > 5, f"{vg.std():.1f}")
        # ⚠ Controle : sur une image vide, la vignette ne doit pas lever.
        Image.fromarray(np.zeros((200, 200), np.uint8)).save(t / "vide.tif")
        v("une image vide ne fait pas planter", vignette(t / "vide.tif", 80) is not None)

        gg = {"image": str(t / "croix.tif"), "titre": "officiel",
              "signature": "croisillon", "alpha": None}
        dd = {"image": str(t / "tour.tif"), "titre": "la nôtre",
              "signature": "tourbillon", "alpha": 0.95}
        f = t / "duo.png"
        r = dessiner(gg, dd, f, cote=200)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux vignettes portent de la texture",
          r["ecart_type_gauche"] > 5 and r["ecart_type_droite"] > 5, str(r))
        # ⚠ Les deux vignettes font la MEME taille : sinon on compare des echelles.
        v("les deux carrés ont le même côté", r["cote"] == 200)
        px = set(Image.open(f).convert("RGB").getdata())
        v("l'α condamné est peint en rouge", MAUVAIS in px)
        v("... et le non condamné ne l'est pas en rouge", BON in px)
        # ⚠ Un alpha sous le seuil doit passer au vert : sinon la couleur ne dit rien.
        f2 = t / "duo2.png"
        dessiner(gg, dict(dd, alpha=0.2), f2, cote=200)
        v("un α convergent est peint en vert",
          MAUVAIS not in set(Image.open(f2).convert("RGB").getdata()))

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--officiel", type=Path,
                    default=Path("data/officiel_appariee/rendu/40.tif"))
    ap.add_argument("--notre", type=Path,
                    default=Path("data/paris4_plafond/ps256_c2_g200/apercu_g2/01.tif"))
    ap.add_argument("--alpha-notre", type=float, default=0.95)
    ap.add_argument("--sortie", type=Path, default=Path("docs/images/50_deux_surfaces.png"))
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    for f in (a.officiel, a.notre):
        if not f.is_file():
            print(f"absent : {f}", file=sys.stderr)
            return 2
    r = dessiner(
        {"image": str(a.officiel), "titre": "un segment officiel de Scroll 1",
         "signature": "croisillon régulier — deux couches de fibres perpendiculaires",
         "alpha": None},
        {"image": str(a.notre), "titre": "notre trace sur PHercParis4",
         "signature": "tourbillons — les tranches de plusieurs feuillets",
         "alpha": a.alpha_notre},
        a.sortie)
    print(f"  écrit : {a.sortie}  ({r['largeur']}×{r['hauteur']})")
    print(f"  contraste des deux vignettes : {r['ecart_type_gauche']} / "
          f"{r['ecart_type_droite']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
