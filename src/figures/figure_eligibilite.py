#!/usr/bin/env python3
"""Deux ensembles disjoints : ce qu'on sait tracer, et ce qu'on sait lire.

⚠⚠ **Ce que la figure établit.** Le point le plus profond du registre — *réparer une trace
sert-il à quelque chose ?* — demande une trace fautive, sa réparation, et le **même aval**
appliqué aux deux. La figure montre pourquoi il n'est pas montable sur ce qui est en main :
les rouleaux qu'on sait tracer et ceux dont la sortie publiée porte du texte **ne se
recouvrent pas**.

⭐ La colonne de droite porte la raison pour laquelle ce n'est pas une impasse : ce que
chaque rouleau lisible **publie**. Un rouleau sans prédiction de surface ne peut pas
recevoir la campagne de graines, quelle que soit la qualité de son encre — et c'est
justement le cas de celui dont la part écrite est la plus haute.

⚠ Tracé avec PIL, sans matplotlib (absent de cet environnement).

Usage :
    uv run python src/figures/figure_eligibilite.py \\
        --json docs/mesures/eligibilite_aval.json --sortie docs/images/48_eligibilite.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

LARGEUR = 1120
MARGE = 40
LIGNE = 24

ANGLAIS = {
    "Ce qu'on sait tracer, ce qu'on sait lire — et le vide entre les deux":
        "What we can trace, what we can read — and the gap between them",
    "rouleaux TRAÇABLES": "TRACEABLE scrolls",
    "rouleaux LISIBLES": "READABLE scrolls",
    "part des cartes publiées qui ont la statistique d'une page écrite":
        "share of published maps with the statistics of a written page",
    "campagne de tirages faite": "draw campaign done",
    "intersection": "intersection",
    "VIDE": "EMPTY",
    "ce que chaque rouleau lisible publie": "what each readable scroll publishes",
    "prédiction de surface": "surface prediction",
    "segments tracés": "traced segments",
    "écarté : pas de prédiction, la campagne de graines ne peut pas y tourner":
        "ruled out: no prediction, the seed campaign cannot run there",
    "aval mesuré directement : ": "downstream measured directly: ",
    " ne répond pas": " does not respond",
    "action : ": "action: ",
}

FOND, TEXTE, DOUX = (255, 255, 255), (25, 25, 25), (150, 150, 150)
TRACE, LIRE = (60, 110, 170), (40, 110, 60)
ALERTE = (200, 45, 45)


def replier(texte: str, largeur_px: int, mesurer) -> list[str]:
    """Couper un texte en lignes qui tiennent dans le cadre.

    ⚠⚠ Sans ça la dernière ligne sort de l'image, et une phrase coupée en plein milieu par
    le bord se lit comme une figure tronquée — c'est exactement ce qui est arrivé à la
    ligne d'action, dont il manquait les trois derniers mots.

    ⚠ `mesurer` est passé plutôt que déduit : la largeur d'un texte dépend de la police, et
    une estimation « n caractères × largeur moyenne » se trompe dès qu'un mot est long.
    """
    lignes, courante = [], ""
    for mot in texte.split():
        essai = (courante + " " + mot).strip()
        if courante and mesurer(essai) > largeur_px:
            lignes.append(courante)
            courante = mot
        else:
            courante = essai
    if courante:
        lignes.append(courante)
    return lignes


def barre(part: float, larg: int) -> int:
    """Largeur d'une barre de fraction, écrêtée au cadre."""
    return int(min(max(part, 0.0), 1.0) * larg)


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("une fraction nulle ne dessine rien", barre(0.0, 200) == 0)
    v("une fraction pleine remplit le cadre", barre(1.0, 200) == 200)
    v("la moitié fait la moitié", barre(0.5, 200) == 100)
    v("une fraction négative reste dans le cadre", barre(-1.0, 200) == 0)
    v("une fraction au-delà de 1 aussi", barre(3.0, 200) == 200)
    # ⚠ Deux fractions distinctes doivent donner deux largeurs distinctes, sinon la figure
    # ne discrimine rien -- c'est le controle que la premiere sonde ne fait pas.
    v("deux fractions distinctes donnent deux largeurs distinctes",
      barre(0.55, 200) != barre(0.92, 200))

    # ⚠⚠ Le repli, sonde comprise. Une mesure factice de 10 px par caractere rend le calcul
    # verifiable sans police : ce qui est teste est la REGLE de coupe, pas le rendu.
    m = lambda t: len(t) * 10
    v("un texte court tient sur une ligne", replier("un deux", 200, m) == ["un deux"])
    v("un texte long est coupé", len(replier("un deux trois quatre cinq", 100, m)) > 1)
    v("... sans perdre un mot",
      " ".join(replier("un deux trois quatre cinq", 100, m)) == "un deux trois quatre cinq")
    # ⚠ Un mot plus large que le cadre ne doit pas boucler ni disparaitre : il sort seul sur
    # sa ligne, ce qui est laid et honnete -- le couper inventerait un mot qui n'existe pas.
    v("un mot plus large que le cadre sort seul", replier("interminable", 30, m)
      == ["interminable"])
    v("un texte vide ne produit aucune ligne", replier("", 100, m) == [])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # ⚠⚠⚠ Le verdict imprimait « ALL PASS » et rendait 0 INCONDITIONNELLEMENT :
    # cette batterie était verte quoi que disent ses contrôles. Trente-neuf
    # fichiers du dépôt portaient le même défaut, corrigé le 2026-08-27.
    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", type=Path, default=Path(__file__).resolve().parents[2] / "docs/mesures/eligibilite_aval.json")
    ap.add_argument("--sortie", type=Path, default=Path(__file__).resolve().parents[2] / "docs/images/48_eligibilite.png")
    ap.add_argument("--anglais", action="store_true")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    import langue

    if not a.json.is_file():
        print(f"absent : {a.json} — lancer d'abord eligibilite_aval.py", file=sys.stderr)
        return 1
    d = json.loads(a.json.read_text(encoding="utf-8"))
    trac, lis = d["tracables"], d["lisibles"]
    pubs = d.get("publications") or {}

    def police(t, gras=False):
        c = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if gras
             else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        try:
            return ImageFont.truetype(c, t)
        except OSError:
            return ImageFont.load_default()

    f_t, f_n, f_p = police(21, True), police(15), police(12)
    n_col = max(len(trac), len(lis))
    hauteur = MARGE + 40 + LIGNE * n_col + 60 + LIGNE * len(lis) + 40 + 5 * 20 + MARGE
    img = Image.new("RGB", (LARGEUR, hauteur), FOND)
    g = langue.Traduisant(ImageDraw.Draw(img), ANGLAIS if a.anglais else None)

    g.text((MARGE, MARGE - 14),
           "Ce qu'on sait tracer, ce qu'on sait lire — et le vide entre les deux",
           font=f_t, fill=TEXTE)
    y0 = MARGE + 34
    xg, xd = MARGE, 620

    g.text((xg, y0), f"rouleaux TRAÇABLES ({len(trac)})", font=f_n, fill=TRACE)
    g.text((xg, y0 + 20), "campagne de tirages faite", font=f_p, fill=DOUX)
    for i, n in enumerate(trac):
        g.text((xg + 10, y0 + 44 + i * LIGNE), n, font=f_p, fill=TEXTE)

    n_lis = sum(1 for x in lis.values() if x["lisible"])
    g.text((xd, y0), f"rouleaux LISIBLES ({n_lis})", font=f_n, fill=LIRE)
    g.text((xd, y0 + 20),
           "part des cartes publiées qui ont la statistique d'une page écrite",
           font=f_p, fill=DOUX)
    larg = 220
    for i, (n, x) in enumerate(lis.items()):
        yy = y0 + 44 + i * LIGNE
        coul = LIRE if x["lisible"] else DOUX
        g.text((xd + 10, yy), n, font=f_p, fill=TEXTE)
        bx = xd + 120
        g.rectangle([bx, yy + 2, bx + larg, yy + 13], outline=DOUX)
        g.rectangle([bx, yy + 2, bx + barre(x["part_ecrite"], larg), yy + 13], fill=coul)
        g.text((bx + larg + 8, yy), f"{x['part_ecrite']:.0%}", font=f_p, fill=coul)
    # ⚠ Le seuil est TRACE, sinon « lisible » se lit comme un jugement au doigt mouille.
    sx = xd + 120 + barre(d["part_ecrite_min"], larg)
    g.line([sx, y0 + 44, sx, y0 + 44 + LIGNE * len(lis)], fill=ALERTE, width=1)

    y = y0 + 44 + LIGNE * n_col + 16
    g.line([MARGE, y, LARGEUR - MARGE, y], fill=DOUX)
    y += 14
    g.text((MARGE, y), "intersection", font=f_n, fill=TEXTE)
    g.text((MARGE + 130, y - 2), "VIDE" if not d["tracables_et_lisibles"]
           else ", ".join(d["tracables_et_lisibles"]), font=f_t,
           fill=ALERTE if not d["tracables_et_lisibles"] else LIRE)
    y += 34

    if pubs:
        g.text((MARGE, y), "ce que chaque rouleau lisible publie", font=f_n, fill=TEXTE)
        y += 24
        for n, p_ in sorted(pubs.items()):
            marques = []
            if p_.get("a_prediction"):
                marques.append("prédiction de surface")
            if p_.get("a_segments"):
                marques.append("segments tracés")
            ecarte = n in (d.get("candidats_ecartes") or {})
            g.text((MARGE + 10, y), f"{n:<14} " + " · ".join(marques) if marques
                   else f"{n:<14} —", font=f_p, fill=ALERTE if ecarte else TEXTE)
            if ecarte:
                g.text((MARGE + 400, y),
                       "écarté : pas de prédiction, la campagne de graines ne peut pas y "
                       "tourner", font=f_p, fill=ALERTE)
            y += LIGNE
        y += 12

    m = d.get("aval_mesure_directement")
    lignes = []
    if m:
        lignes.append(f"aval mesuré directement : {m['rouleau']}, "
                      f"{m['part_du_modele_qui_marche']:.1%} de ce que le modèle rend là "
                      f"où il marche" + ("" if m["repond"] else " → ne répond pas"))
    if d.get("action"):
        # ⚠ Pas de ⭐ : DejaVu n'a pas ce glyphe et PIL le rend en carré vide, ce qui donne
        # une figure qui a l'air cassée. Payé une fois déjà sur la figure de `47`.
        lignes.append("action : " + d["action"])
    dessin = ImageDraw.Draw(img)
    largeur_utile = LARGEUR - 2 * MARGE

    def mesurer(t):
        return dessin.textlength(t, font=f_n)

    i = 0
    for t in lignes:
        for morceau in replier(t, largeur_utile, mesurer):
            g.text((MARGE, y + i * 20), morceau, font=f_n,
                   fill=LIRE if t.startswith("action") else TEXTE)
            i += 1

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
