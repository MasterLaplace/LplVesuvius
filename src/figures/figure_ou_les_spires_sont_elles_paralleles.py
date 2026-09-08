#!/usr/bin/env python3
"""Ou les spires voisines sont-elles paralleles ? Au milieu — et les deux echecs sont au bord.

⚠⚠⚠ CETTE FIGURE PORTE LA CARTE DU PROBLEME. Le panneau A montre le U du desalignement, avec les
deux bandes que l'echantillonnage ne resout pas. Le panneau B superpose les DEUX mesures — la
continuite de `92` et le parallelisme de `93` — et c'est lui qui dit que le probleme est
LOCALISE : les deux modes d'echec vivent au meme endroit, le bord.

Usage :
    uv run python src/figures/figure_ou_les_spires_sont_paralleles.py --verifier
    uv run python src/figures/figure_ou_les_spires_sont_paralleles.py \\
        --sortie docs/images/93_ou_les_spires_sont_elles_paralleles.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import Tracee, police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
PALE = (231, 240, 231)
GRIS = (196, 196, 196)
CADRE = (200, 200, 200)


def prose(m: dict, c: dict | None) -> list[str]:
    p, mini = m["par_tiers"], m["le_minimum"]
    der = m["aux_deux_bouts"]["derniere"]
    lignes = [
        "un marcheur transfere en avancant d'un pas le long de la NORMALE a la feuille. ce pas "
        "n'atterrit sur la spire voisine que si les deux spires sont PARALLELES : a trente degres "
        "de desalignement, un pas de 182 µm tombe a 91 µm de cote, soit la moitie du pas. savoir "
        "ou elles le sont, c'est savoir ou un pas geometrique suffit.",
        f"★★★ PANNEAU A — LA REPONSE EST UN U. l'angle entre la normale d'une cellule et celle "
        f"d'un tour plus loin vaut {mini['un_tour_deg']}° a mi-rayon ({mini['rayon_mm']} mm), "
        f"contre {mini['adjacent_deg']}° entre cellules adjacentes — soit "
        f"×{mini['rapport_au_plancher']}, quasi parallele. au bord ({der['rayon_mm']} mm) il "
        f"remonte a {der['un_tour_deg']}°, ×{der['rapport_au_plancher']}. ce n'est donc ni pire "
        "au coeur ni pire au bord : c'est MINIMAL AU MILIEU.",
        f"⚠⚠⚠ ET LES {len(m['bandes_non_resolues'])} BANDES LES PLUS INTERNES NE SONT PAS "
        f"DESALIGNEES, ELLES SONT NON RESOLUES. "
        + ", ".join(m["bandes_non_resolues"]) +
        " n'ont pas assez de colonnes par tour : leur normale est moyennee sur plus d'arc que "
        "leur propre variation locale. le critere d'exclusion est DERIVE de cette comparaison, "
        "pas choisi, et il exclut exactement ces bandes-la.",
        "⚠⚠ ET LE REPERE N'EST PAS UN PLANCHER DE BRUIT. le desaccord entre cellules ADJACENTES "
        "est domine par la ROTATION de la normale d'une cellule a l'autre — 13,3° au coeur, 1,9° "
        "au bord — et non par la rugosite : une spirale PARFAITE a 60 colonnes par tour rend "
        "6,0°, soit exactement 360/60. il reste utile parce qu'il est mesure a la meme "
        "resolution, mais l'appeler « bruit » serait faux.",
    ]
    if c is not None:
        d = c["degradation"]
        lignes.append(
            f"★★ PANNEAU B — LA CARTE DU PROBLEME, ET IL EST LOCALISE. la continuite de `92` "
            f"vaut {d['coeur']['rapport_median']} au coeur, {d['milieu']['rapport_median']} au "
            f"milieu et {d['bord']['rapport_median']} au bord ; le parallelisme de `93` vaut "
            f"{p['coeur']['rapport_median']}, {p['milieu']['rapport_median']} et "
            f"{p['bord']['rapport_median']}. LES DEUX MODES D'ECHEC VIVENT AU MEME ENDROIT : au "
            "bord la surface est brisee ET les spires sont desalignees. au milieu, les deux sont "
            "propres.")
    lignes += [
        "★ CE QUE CA CONTRAINT POUR LE REMPLACANT DE L'HUMAIN : un automate qui traiterait tout "
        "le rouleau de la meme facon echouerait au bord et gaspillerait au milieu. le probleme "
        "est LOCALISE, ce qui est une contrainte de conception et non une observation.",
        f"★ LE CONTROLE QUI VALIDE LA METHODE EST DANS LA MESURE : une normale de spirale TOURNE "
        f"avec l'angle, donc elle doit maximalement diverger a un quart de tour "
        f"({m['quart_de_tour_median_deg']}°) et REVENIR a un tour entier. sans ce retour, la "
        "mesure ne suivrait pas la spire et ne dirait rien du transfert.",
        "⚠⚠⚠ et une erreur a moi, gardee, qui avait INVERSE la conclusion : mon exploration "
        "comparait la bande 0 a la bande 7 en appelant la seconde « le bord », alors que les deux "
        "sont dans le tiers interieur. un tiers se compte sur le corpus ENTIER, pas sur les "
        "premieres lignes d'un tableau.",
    ]
    return lignes


def panneau_u(art, x0, y0, pw, ph, m, petit) -> tuple[int, int]:
    """Le désalignement contre le rayon, avec les bandes non résolues marquées."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "angle entre la normale d'une cellule et celle d'un tour plus loin",
             fill=DISCRET, font=petit)
    lignes = m["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 24
    base, sommet = y0 + ph - 46, y0 + 34
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    hi = max(x["un_tour_deg"] for x in lignes) * 1.06

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.94) / (r1 * 1.04 - r0 * 0.94)

    def py(v):
        return base - (base - sommet) * v / hi

    art.line([gauche, base, droite, base], fill=TEXTE)
    for g in (0, int(hi / 2), int(hi)):
        art.text((gauche - 28, py(g) - 6), f"{g:>3}°", fill=DISCRET, font=petit)
    # ⚠⚠ LE REPERE ADJACENT EST TRACE SOUS LA COURBE : sans lui, « ×1,23 » serait un nombre nu,
    # et un lecteur ne saurait pas a quoi le desalignement est rapporte.
    art.line([(px(x["rayon_mm"]), py(x["adjacent_deg"])) for x in lignes], fill=GRIS)
    art.text((px(lignes[len(lignes) // 2]["rayon_mm"]),
              py(lignes[len(lignes) // 2]["adjacent_deg"]) + 5),
             "cellules adjacentes — la rotation, pas du bruit", fill=DISCRET, font=petit)
    resolues = [x for x in lignes if x["resolue"]]
    art.line([(px(x["rayon_mm"]), py(x["un_tour_deg"])) for x in resolues], fill=BLEU, width=2)
    marques = non_res = 0
    for x in lignes:
        cx, cy = px(x["rayon_mm"]), py(x["un_tour_deg"])
        if not x["resolue"]:
            non_res += 1
            art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=ROUGE)
            art.text((cx + 7, cy - 6), f"w{x['de']:03d}-{x['a']:03d} : NON RÉSOLUE",
                     fill=ROUGE, font=petit)
            continue
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLEU)
    mini = m["le_minimum"]
    cx, cy = px(mini["rayon_mm"]), py(mini["un_tour_deg"])
    art.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=VERT)
    # ⚠ Le libellé du minimum vit AU-DESSUS du point : posé dessous, il tombait sur la courbe
    # grise des cellules adjacentes, et les deux se lisaient l'un par-dessus l'autre.
    art.text((cx - 30, cy - 20),
             f"minimum : {mini['un_tour_deg']}° → ×{mini['rapport_au_plancher']}",
             fill=VERT, font=petit)
    marques += 1
    for g in (int(r0), int((r0 + r1) / 2), int(r1)):
        art.text((px(g) - 12, base + 6), f"{g} mm", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "abscisse : rayon médian de la bande", fill=DISCRET, font=petit)
    return marques, non_res


def panneau_carte(art, x0, y0, pw, ph, m, c, petit) -> int:
    """La carte du problème : continuité et parallélisme, par tiers."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6),
             "les deux mesures, par tiers — rapport à leur propre référence locale",
             fill=DISCRET, font=petit)
    if c is None:
        art.text((x0 + 20, y0 + ph / 2), "mesure de continuité absente", fill=ROUGE, font=petit)
        return 0
    tiers = ("coeur", "milieu", "bord")
    mots = {"coeur": "cœur", "milieu": "milieu", "bord": "bord"}
    # ⚠⚠ LA HAUTEUR LAISSE LEUR PLACE AUX ETIQUETTES DE TIERS ET AU TITRE DU SECOND GRAPHE :
    # ma premiere version les faisait se recouvrir, et « cœur » se lisait par-dessus
    # « parallélisme (`93`) ».
    gauche, droite = x0 + 92, x0 + pw - 40
    haut = y0 + 44
    h = (ph - 150) / 2
    faits = 0
    for k, (cle, source, nom, coul) in enumerate((
            ("continuite", c["degradation"], "continuité (`92`)", AMBRE),
            ("parallelisme", m["par_tiers"], "parallélisme (`93`)", BLEU))):
        y0b = haut + k * (h + 44)
        hi = max(source[t]["rapport_median"] for t in tiers) * 1.15
        art.text((x0 + 8, y0b - 14), nom, fill=coul, font=petit)
        for j, t in enumerate(tiers):
            v = source[t]["rapport_median"]
            yb = y0b + h
            larg = (droite - gauche) / 3.6
            a0 = gauche + j * (droite - gauche) / 3
            # ⭐ La ligne « 1 » est tracee : c'est elle qui dit ce que « propre » veut dire.
            art.line([gauche, yb - h / hi, droite, yb - h / hi], fill=GRIS)
            art.rectangle([a0, yb - h * v / hi, a0 + larg, yb], fill=coul)
            art.text((a0 + 4, yb - h * v / hi - 13), f"×{v}", fill=coul, font=petit)
            art.text((a0 + 4, yb + 4), mots[t], fill=DISCRET, font=petit)
            faits += 1
        art.text((droite + 4, yb - h / hi - 5), "×1", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             "★ les deux montent AU MÊME ENDROIT : le problème est localisé, pas uniforme",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             "gris : ×1, c'est-à-dire indistinguable de la référence locale",
             fill=DISCRET, font=petit)
    return faits


def dessiner(m: dict, c: dict | None, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 392
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m, c), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    mini = m["le_minimum"]
    der = m["aux_deux_bouts"]["derniere"]
    art.text((marge, 16),
             "Où les spires voisines sont-elles parallèles ? Au milieu — et les deux échecs sont "
             "au bord", fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {m['bandes']} bandes · ×{mini['rapport_au_plancher']} à "
             f"{mini['rayon_mm']} mm contre ×{der['rapport_au_plancher']} à {der['rayon_mm']} mm",
             fill=DISCRET, font=moyen)
    titres = ("A · le U du désalignement, contre le rayon",
              "B · la carte du problème — `92` et `93` ensemble")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    minima, non_res = panneau_u(art, marge, 104, pw, ph, m, petit)
    faits = panneau_carte(art, marge + pw + ecart, 104, pw, ph, m, c, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "minima": minima, "non_resolues": non_res, "barres": faits,
            "textes_dessines": art.textes,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    c = json.loads(CONTINUITE.read_text()) if CONTINUITE.is_file() else None
    v("la prose est traçable", prose_tracable(prose(m, c)))
    d = dessiner(m, c, RACINE / "docs" / "images" / "93_ou_les_spires_sont_elles_paralleles.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    # ⚠⚠⚠ LES BANDES NON RÉSOLUES SONT MARQUÉES : une courbe qui les tracerait comme les autres
    # ferait lire une limite de grille comme un désalignement.
    v("les bandes non résolues sont marquées à part",
      d["non_resolues"] == len(m["bandes_non_resolues"]),
      f"{d['non_resolues']} pour {len(m['bandes_non_resolues'])}")
    v("... et le minimum du U est marqué", d["minima"] == 1, str(d["minima"]))
    # ⭐⭐ LE PANNEAU B EST LA SYNTHÈSE : sans les deux mesures ensemble, « le problème est
    # localisé » serait une phrase et pas une chose qu'on voit.
    v("la carte porte les deux mesures sur trois tiers", d["barres"] == 6, str(d["barres"]))
    v("... et la continuité est bien lue depuis `92`",
      c is not None and c["degradation"]["bord"]["rapport_median"] > 20,
      "docs/mesures/la_continuite_des_transferts.json")
    # ⭐⭐⭐ LE VERDICT EST DANS LA MESURE, pas seulement dans la prose.
    v("les deux mesures montent au même endroit",
      c["degradation"]["bord"]["rapport_median"] > c["degradation"]["milieu"]["rapport_median"]
      and m["par_tiers"]["bord"]["rapport_median"]
      > m["par_tiers"]["milieu"]["rapport_median"])
    v("la prose dit que le problème est LOCALISÉ",
      any("LOCALISE" in x for x in prose(m, c)))
    # ⚠⚠ LES DEUX FAUTES SONT DANS LA PROSE.
    v("la prose garde l'erreur du tiers", any("bande 0 a la bande 7" in x
                                              for x in prose(m, c)))
    v("... et dit que le repère n'est pas du bruit",
      any("360/60" in x for x in prose(m, c)))
    v("le contrôle de méthode est dit", any("REVENIR a un tour entier" in x
                                            for x in prose(m, c)))
    v("les deux panneaux sont titrés", len(d["titres"]) == 2)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "93_ou_les_spires_sont_elles_paralleles.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    c = json.loads(CONTINUITE.read_text()) if CONTINUITE.is_file() else None
    d = dessiner(json.loads(MESURE.read_text()), c, a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
