#!/usr/bin/env python3
"""Le détecteur reçoit deux volumes différents et rend la même carte.

⚠⚠ **Ce que la figure établit, et ce qu'elle n'établit pas.** Elle ne montre PAS que le
détecteur signale de l'encre là où il n'y en a pas — sur ce rouleau il n'en signale nulle
part, ce que [`36`](../docs/36_lorigine_de_la_pile.md) §5bis avait déjà mesuré. Elle montre
quelque chose de plus étroit et de vérifiable : **sa sortie ne dépend pas de ce qu'il
reçoit**.

⭐ Les trois bandes répondent aux trois questions dans l'ordre où un sceptique les pose.
*Les deux entrées sont-elles réellement différentes ?* — bande du haut, et c'est le contrôle
du contrôle : deux fenêtres vides expliqueraient deux sorties identiques sans rien apprendre.
*Les deux sorties se ressemblent-elles ?* — bande du milieu, à **échelle de couleur
commune**, sans quoi deux cartes plates de niveaux différents auraient l'air identiques par
construction. *À quel point ?* — bande du bas, où l'écart mesuré est confronté à celui
qu'auraient **deux cartes étrangères l'une à l'autre**, valeur dérivée et non choisie.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_temoin_negatif.py \\
        --json docs/mesures/temoin_negatif.json \\
        --positif data/temoin_negatif/sur_sa_feuille.npy \\
        --negatif data/temoin_negatif/en_travers.npy \\
        --sortie docs/images/46_temoin_negatif.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

LARGEUR = 1120
VIGN = 300                    # côté d'une vignette
MARGE = 40

# ⚠ La table de traduction de CETTE figure — elle vit à côté du dessin, comme les autres :
# une table partagée obligerait à formuler les libellés pareil partout.
ANGLAIS = {
    "Deux volumes différents, une seule réponse": "Two different volumes, one single answer",
    "ce que le modèle a REÇU": "what the model RECEIVED",
    "ce que le modèle a RENDU": "what the model RETURNED",
    "sur sa feuille": "on its sheet",
    "en travers": "across the stack",
    "moyenne des 26 couches": "mean of the 26 layers",
    " non nul": " non-zero",
    " px non mesurés": " px not measured",
    "même échelle de couleur": "same colour scale",
    "écart entre les deux cartes": "gap between the two maps",
    "si elles étaient étrangères": "if they were unrelated",
    "de ce que chaque carte varie": "of what each map varies by",
    "les entrées diffèrent de ": "the inputs differ by ",
    " — les sorties, de ": " — the outputs, by ",
    "le modèle est inerte sur ce rouleau : sa sortie ne dépend pas de la présence d'une feuille":
        "the model is inert on this scroll: its output does not depend on a sheet being there",
    "⚠ ce qui reste NON établi : qu'il signale de l'encre là où il n'y a pas de feuille":
        "⚠ what remains NOT established: that it reports ink where there is no sheet",
}

# ⚠⚠ La COULEUR des pixels que le modèle n'a pas produits. Un niveau de gris ne peut pas
# faire ce travail : quelle que soit la valeur choisie, elle tombe quelque part dans la
# rampe et se lit comme une prédiction de ce niveau-là. Une première version prenait 0,5 —
# soit exactement le milieu de la plage utile, donc la valeur la plus confusante possible,
# alors que le commentaire prétendait le contraire. Une teinte hors du gris est le seul
# marqueur qu'une rampe en niveaux de gris ne peut pas produire.
NON_MESURE_RVB = (232, 168, 40)

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (120, 120, 120)
ALERTE, BON = (200, 45, 45), (40, 110, 60)


def normaliser(a, lo=None, hi=None):
    """Une image 8 bits, avec des bornes IMPOSÉES quand on compare deux cartes.

    ⚠⚠ Normaliser chaque carte sur ses propres extrêmes est exactement l'erreur à ne pas
    faire ici : deux cartes plates de niveaux très différents ressortiraient identiques,
    et la figure prouverait sa conclusion par son étirement de contraste. Les bornes
    communes sont passées par l'appelant.
    """
    import numpy as np
    a = np.asarray(a, dtype=np.float64)
    fini = np.isfinite(a)
    lo = (a[fini].min() if fini.any() else 0.0) if lo is None else lo
    hi = (a[fini].max() if fini.any() else 1.0) if hi is None else hi
    if hi <= lo:
        hi = lo + 1e-12
    # ⚠⚠ Ce que le modèle N'A PAS produit ne doit pas ressembler à ce qu'il a produit.
    # Une valeur non finie convertie en entier donne du HASARD, et un lecteur lit du hasard
    # comme de la structure — sur une carte dont toute la thèse est « il n'y a pas de
    # structure », c'est l'artefact qui la contredirait. On rend donc DEUX choses : la
    # rampe, et le masque de ce qui n'a pas été mesuré.
    return np.clip(np.where(fini, (a - lo) / (hi - lo), 0.0), 0, 1), ~fini


def vignette(a, cote: int, lo=None, hi=None):
    """Une carte réduite à une vignette carrée, en niveaux de gris."""
    import numpy as np
    from PIL import Image
    a = np.asarray(a)
    if a.ndim == 1:
        c = int(round(a.size ** 0.5))
        # ⚠ Une carte qui n'est pas carrée ne peut pas être devinée : mieux vaut le dire
        # que de la replier de travers, ce qui produirait une image plausible et fausse.
        if c * c != a.size:
            return None
        a = a.reshape(c, c)
    r, absent = normaliser(a, lo, hi)
    rvb = np.repeat((r * 255).astype("uint8")[:, :, None], 3, axis=2)
    rvb[absent] = NON_MESURE_RVB
    # ⚠ NEAREST et non BILINEAR : une interpolation mélangerait la teinte du marqueur avec
    # la rampe et fabriquerait, tout autour des trous, des couleurs qui ne veulent rien dire.
    return Image.fromarray(rvb, mode="RGB").resize((cote, cote), Image.NEAREST)


def vignette_entree(e: dict, cote: int):
    """La matière que le modèle a réellement vue, moyennée sur ses couches.

    ⭐ Le dossier et la fenêtre viennent du JSON de la campagne, pas d'arguments répétés :
    la figure montre ainsi exactement les pixels que la mesure a décrits, et pas une
    seconde définition de « la fenêtre » libre de s'en écarter.

    ⚠ Chaque carte est normalisée sur SES propres extrêmes ici, contrairement aux sorties :
    on ne compare pas deux niveaux d'entrée, on montre deux textures. Le nombre qui compare
    est le σ imprimé à côté.
    """
    import numpy as np
    from PIL import Image
    if not e or "impossible" in e:
        return None
    dossier = Path(e["dossier"])
    top, left, h, w = e["fenetre"]
    tifs = sorted(dossier.glob("*.tif"))
    if not tifs:
        return None
    # ⚠ Un sous-échantillon des couches suffit pour une vignette et évite de relire 26
    # images de plusieurs mégapixels — la mesure, elle, les a toutes lues.
    pris = tifs[::max(1, len(tifs) // 6)][:6]
    acc = None
    for t in pris:
        b = np.asarray(Image.open(t), dtype=np.float64)[top:top + h, left:left + w]
        acc = b if acc is None else acc + b
    if acc is None or acc.size == 0:
        return None
    return vignette(acc / len(pris), cote)


def verifier() -> int:
    import numpy as np
    echecs = controles = 0

    # ⚠⚠ La batterie de temoins du depot tourne HORS LIGNE, sans la pile d'imagerie. Les
    # controles qui demandent PIL sont donc sautes quand elle est absente -- mais le saut
    # est ANNONCE et compte, jamais silencieux : un temoin qui se tait sur une machine
    # incomplete passe pour un temoin qui reussit, ce qui est la panne que ce depot
    # recense sous « une verification incapable d'echouer ».
    try:
        from PIL import Image  # noqa: F401
        avec_pil = True
    except ImportError:
        avec_pil = False

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    plate_basse = np.full((40, 40), 0.10)
    plate_haute = np.full((40, 40), 0.90)
    # ⚠⚠ LA sonde qui protège la figure de prouver sa propre conclusion. Sur des bornes
    # COMMUNES, deux cartes plates de niveaux différents doivent rester DIFFÉRENTES à
    # l'écran ; normalisées chacune sur elle-même, elles deviendraient identiques.
    lo = min(plate_basse.min(), plate_haute.min())
    hi = max(plate_basse.max(), plate_haute.max())
    nb, _ = normaliser(plate_basse, lo, hi)
    nh, _ = normaliser(plate_haute, lo, hi)
    v("à bornes communes, deux niveaux différents restent différents",
      abs(float(nb.mean()) - float(nh.mean())) > 0.5,
      f"{nb.mean():.3f} contre {nh.mean():.3f}")
    v("... alors que normalisées chacune sur elle-même elles seraient identiques",
      abs(float(normaliser(plate_basse)[0].mean())
          - float(normaliser(plate_haute)[0].mean())) < 1e-9)
    v("une carte constante ne divise pas par zéro",
      0.0 <= float(normaliser(np.full((8, 8), 3.0))[0].mean()) <= 1.0)
    # ⚠⚠ LA sonde du NaN. Les vraies cartes en portent 8784 sur 1 210 000 — un bord que
    # le pas de balayage n'atteint pas. Casté tel quel, un NaN donne un entier arbitraire,
    # donc du bruit visible sur une figure qui affirme qu'il n'y en a pas.
    troue = np.full((8, 8), 0.2)
    troue[0, 0] = np.nan
    n_, absent = normaliser(troue, 0.0, 1.0)
    v("un pixel non mesuré est SIGNALÉ par un masque", bool(absent[0, 0]))
    v("... et ne contamine pas les bornes des autres",
      abs(float(n_[1, 1]) - 0.2) < 1e-12)
    v("... et survit à la conversion en entier", np.isfinite(n_).all())
    v("des bornes déduites ignorent les non finis",
      abs(float(normaliser(troue)[0][1, 1]) - 0.0) < 1e-12)
    v("une carte entièrement non finie ne lève pas",
      np.isfinite(normaliser(np.full((4, 4), np.nan))[0]).all())
    # ⚠⚠ LA sonde qui a corrigé le marqueur : sa teinte ne doit PAS être un gris, sinon
    # elle tombe quelque part dans la rampe et se lit comme une prédiction de ce niveau.
    v("le marqueur du non mesuré n'est pas un gris",
      len(set(NON_MESURE_RVB)) > 1, str(NON_MESURE_RVB))
    if avec_pil:
        vg = vignette(troue, 8, 0.0, 1.0)
        v("... et il apparaît dans la vignette",
          NON_MESURE_RVB in [c for _, c in vg.getcolors(maxcolors=1 << 16)],
          "absent de la vignette")

    if avec_pil:
        v("une vignette est carrée et de la taille demandée",
          vignette(np.arange(64.0), 32).size == (32, 32))
        # ⚠ Une carte non carrée aplatie ne peut pas être repliée : la refuser vaut mieux
        # que d'en produire une image plausible et fausse.
        v("une carte plate non carrée est REFUSÉE", vignette(np.arange(63.0), 32) is None)
        v("une carte déjà 2D passe", vignette(np.zeros((10, 20)), 16).size == (16, 16))
        v("une entrée illisible ne produit pas de vignette",
          vignette_entree({"impossible": "x"}, 16) is None)
        v("... et une entrée absente non plus", vignette_entree(None, 16) is None)
        v("un dossier sans couche ne produit pas de vignette",
          vignette_entree({"dossier": "/nexistepas", "fenetre": [0, 0, 8, 8]}, 16) is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    saut = "" if avec_pil else "  ⚠ 7 contrôles SAUTÉS : la pile d'imagerie est absente"
    print(f"ALL PASS ({echecs} failures, {controles} checks){saut}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=Path(__file__).resolve().parents[2] / "docs/mesures/temoin_negatif.json")
    ap.add_argument("--positif", type=Path, default=Path("../data/temoin_negatif/sur_sa_feuille.npy"))
    ap.add_argument("--negatif", type=Path, default=Path("../data/temoin_negatif/en_travers.npy"))
    ap.add_argument("--sortie", type=Path, default=Path(__file__).resolve().parents[2] / "docs/images/46_temoin_negatif.png")
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue

    if not a.json.is_file():
        print(f"absent : {a.json} — lancer d'abord src/campagnes/campagne_temoin_negatif.sh",
              file=sys.stderr)
        return 1
    d = json.loads(a.json.read_text(encoding="utf-8"))
    cp, cn = np.load(a.positif), np.load(a.negatif)

    def police(t):
        for c in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(c, t)
            except OSError:
                pass
        return ImageFont.load_default()

    f_t, f_n, f_p = police(22), police(15), police(13)
    # ⚠ Deux bandes d'images plus une bande de barres plus trois lignes de légende. Une
    # version antérieure comptait TROIS bandes d'images et laissait 200 px de blanc en bas,
    # ce qui fait passer une figure finie pour une figure tronquée.
    hauteur = MARGE + 34 + 2 * (VIGN + 66) + 122 + 3 * 20 + MARGE
    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    g.text((MARGE, MARGE - 12), "Deux volumes différents, une seule réponse",
           font=f_t, fill=TEXTE)
    y = MARGE + 34

    # ── bande 1 : ce que le modèle a reçu ────────────────────────────────────────────
    g.text((MARGE, y), "ce que le modèle a REÇU", font=f_n, fill=TEXTE)
    ep, en = d.get("entree_positif"), d.get("entree_negatif")
    xs = (MARGE, MARGE + VIGN + 60)
    for x, nom, e in ((xs[0], "sur sa feuille", ep), (xs[1], "en travers", en)):
        ve = vignette_entree(e, VIGN)
        if ve is not None:
            img.paste(ve, (x, y + 22))
        g.rectangle([x, y + 22, x + VIGN, y + 22 + VIGN], outline=DOUX)
        if e and "impossible" not in e:
            # ⚠ Sur une vignette sombre, du texte sombre disparaît : un fond plein
            # derrière l'étiquette est ce qui garde la figure lisible quelle que soit
            # l'image en dessous.
            g.rectangle([x + 4, y + 24, x + 116, y + 58], fill=FOND)
            g.text((x + 8, y + 26), f"σ {e['sigma']:.1f}".replace(".", ","),
                   font=f_p, fill=TEXTE)
            g.text((x + 8, y + 42), f"{e['part_non_nulle']:.0%} non nul",
                   font=f_p, fill=TEXTE)
        g.text((x, y + 26 + VIGN), nom, font=f_n, fill=TEXTE)
    g.text((xs[1] + VIGN + 24, y + 22), "moyenne des 26 couches", font=f_p, fill=DOUX)
    if d.get("ecart_relatif_sigma_entree") is not None:
        g.text((xs[1] + VIGN + 24, y + 44),
               f"{d['ecart_relatif_sigma_entree']:.0%}".replace(".", ","),
               font=f_t, fill=BON)
    y += VIGN + 66

    # ── bande 2 : ce que le modèle a rendu, à échelle COMMUNE ────────────────────────
    g.text((MARGE, y), "ce que le modèle a RENDU", font=f_n, fill=TEXTE)
    lo = float(min(np.nanmin(cp), np.nanmin(cn)))
    hi = float(max(np.nanmax(cp), np.nanmax(cn)))
    for x, nom, c in ((xs[0], "sur sa feuille", cp), (xs[1], "en travers", cn)):
        vg = vignette(c, VIGN, lo, hi)
        if vg is not None:
            img.paste(vg, (x, y + 22))
        g.rectangle([x, y + 22, x + VIGN, y + 22 + VIGN], outline=DOUX)
        g.text((x, y + 26 + VIGN), nom, font=f_n, fill=TEXTE)
    g.text((xs[1] + VIGN + 24, y + 22), "même échelle de couleur", font=f_p, fill=DOUX)
    absents = int((~np.isfinite(cp)).sum())
    if absents:
        g.rectangle([xs[1] + VIGN + 24, y + 72, xs[1] + VIGN + 38, y + 86],
                    fill=NON_MESURE_RVB, outline=DOUX)
        g.text((xs[1] + VIGN + 44, y + 71),
               f"{absents} px non mesurés", font=f_p, fill=DOUX)
    if d.get("accord_pixel") is not None:
        g.text((xs[1] + VIGN + 24, y + 44), f"ρ = {d['accord_pixel']:+.4f}".replace(".", ","),
               font=f_t, fill=ALERTE)
    y += VIGN + 66

    # ── bande 3 : l'écart, confronté à celui de deux cartes étrangères ───────────────
    e = d.get("ecart_median_en_variation_interne")
    ref = d.get("ecart_attendu_si_independantes")
    if e is not None and ref:
        g.text((MARGE, y), "écart entre les deux cartes", font=f_n, fill=TEXTE)
        x0, larg = MARGE + 20, 700
        for i, (val, coul, lib) in enumerate(
                ((e, ALERTE, "de ce que chaque carte varie"),
                 (ref, DOUX, "si elles étaient étrangères"))):
            yy = y + 30 + i * 40
            g.rectangle([x0, yy, x0 + larg, yy + 24], outline=DOUX)
            g.rectangle([x0, yy, x0 + int(larg * min(val / max(ref, 1e-9), 1.0)), yy + 24],
                        fill=coul)
            g.text((x0 + larg + 14, yy + 4), f"{val:.0%}  ".replace(".", ",") + lib,
                   font=f_n, fill=TEXTE)
        y += 122

    for i, t in enumerate((
            f"les entrées diffèrent de {d.get('ecart_relatif_sigma_entree', 0):.0%}"
            f" — les sorties, de {e:.0%}".replace(".", ","),
            "⚠⚠ le modèle est inerte sur ce rouleau : sa sortie ne dépend pas de la "
            "présence d'une feuille",
            "⚠ ce qui reste NON établi : qu'il signale de l'encre là où il n'y a pas de "
            "feuille")):
        g.text((MARGE, y + i * 20), t, font=f_n, fill=ALERTE if i == 1 else TEXTE)

    # ⚠⚠ Une figure à moitié traduite a l'air traduite. On REFUSE de l'écrire.
    if a.anglais and g.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for t in g.intraduits():
            print(f"    « {t} »", file=sys.stderr)
        return 1

    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(a.sortie)
    print(f"écrit : {a.sortie}  ({LARGEUR}×{hauteur})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
