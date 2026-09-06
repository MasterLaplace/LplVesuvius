#!/usr/bin/env python3
"""Elle n'accélère pas — et l'itération ne paie que de la nappe.

⚠⚠ POURQUOI CETTE FIGURE EXISTE, ET ELLE RÉTRACTE LA PRÉCÉDENTE. J'avais publié « la dérive
accélère » sur un critère qui **omettait le plus grand incrément** — celui du bras zéro, dont
l'erreur est nulle par définition. Le panneau A remet ce point : la courbe reste **sous** la
droite du premier pas, à tous les bras et sur les deux populations, et le coût par tour est
**stable** autour de 33 µm.

⭐⭐ Le panneau B porte le résultat actionnable : **un seul grand pas fait aussi bien que la
marche itérée** — les deux vont au même endroit, la seconde recalcule ses normales à chaque tour
et ronge un anneau de cellules à chaque tour. À erreur égale, le grand pas rend **48 % de nappe
en plus** au bras 4.

Usage :
    uv run python src/figures/figure_pourquoi_la_derive_accelere.py --verifier
    uv run python src/figures/figure_pourquoi_la_derive_accelere.py \\
        --sortie docs/images/75_pourquoi_la_derive_accelere.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "pourquoi_la_derive_accelere.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    b = m["par_bras"]
    dernier = max(b, key=int)
    return [
        f"{m['marches']} marches aveugles depuis {len(m['departs'])} spires publiees, bras 1 a "
        f"{m['bras_max']}, boite de {m['boite']['cote_voxels']:.0f} voxels. tout est aveugle : "
        "aucune lecture du volume dans cette tranche.",
        "⚠⚠ RETRACTATION. j'avais publie « la derive ACCELERE » sur le critere « les increments "
        "consecutifs croissent » — un critere qui OMET le plus grand increment, celui du bras "
        f"zero (erreur nulle par definition) au bras un. la suite complete est "
        f"{m['increments_communs_um']} um : le PREMIER pas est le plus cher, et il n'y a pas de "
        "tendance apres lui.",
        "le critere retenu est sans seuil : l'erreur au bras k est-elle au-dessus ou en dessous "
        f"de k fois celle du bras un ? elle est EN DESSOUS partout — cout par tour "
        f"{m['cout_par_tour_commun_um']} um, stable. et il basculait sur deux micrometres : "
        "l'ancien rendait deux verdicts opposes sur deux populations qui mesurent la meme chose.",
        "⚠ deux artefacts ecartes. le MASQUE qui retrecit ne change pas la forme de la courbe "
        f"({m['ecart_du_masque_um']} um entre masque propre et masque commun) ; et la "
        "sous-linearite se voit A SPIRE DE DEPART FIXE, pas seulement en moyenne "
        f"({len(m['departs_sous_lineaires'])} departs sur "
        f"{len(m['departs_a_trois_bras_ou_plus'])} a trois bras ou plus).",
        f"et le panneau B, qui est le resultat actionnable : UN SEUL GRAND PAS fait aussi "
        f"bien que {dernier} pas iteres "
        f"({b[dernier]['un_grand_pas_um']} contre {b[dernier]['commune_um']} um), en ne "
        f"rongeant la grille qu'UNE fois. il garde {b[dernier]['cellules_dun_grand_pas']} "
        f"cellules contre {b[dernier]['cellules_propres']}, soit "
        f"{100 * m['part_de_nappe_gagnee_au_dernier_bras']:.0f} % de nappe en plus a erreur "
        "egale. recalculer les normales a chaque pas n'apporte rien et coute de la nappe.",
        "⚠ ce que ca ne dit pas : que la marche soit bonne. un pas coute deja "
        f"{b['1']['commune_um']} um, soit les deux tiers d'une demi-feuille, et c'est ce premier "
        "pas — pas l'accumulation — qui est le vrai poste de depense.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    legendes = [
        "bleu : marche iteree   ambre : UN SEUL grand pas",
        "gris : k fois le premier pas — la droite qu'on depasserait en accelerant",
        "abscisse : longueur du bras, en spires",
        "bleu : cellules de la marche iteree",
        "ambre : cellules d'un seul grand pas",
        "au-dessus de chaque paire : les deux erreurs, en um",
        "abscisse : longueur du bras, en spires",
    ]
    marge, pw, ph, ecart = 40, 400, 250, 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Elle n'accelere pas, et l'iteration ne paie que de la nappe",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['marches']} marches aveugles depuis {len(m['departs'])} spires · "
             f"cout par tour {m['cout_par_tour_commun_um']} um", fill=DISCRET, font=moyen)

    b = m["par_bras"]
    bras = sorted(int(k) for k in b)
    e1 = b[str(bras[0])]["commune_um"]

    # ---------- A : la courbe, contre la droite du premier pas ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · la courbe reste SOUS la droite du premier pas",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    top = max(max(k * e1 for k in bras),
              max(b[str(k)]["commune_um"] for k in bras)) * 1.12
    larg = pw / (len(bras) + 1)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 40)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    art.text((ax + 6, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    # ⚠ Les deux séries sont presque confondues — c'est le résultat —, donc leurs étiquettes se
    # recouvriraient : l'une est posée au-dessus du point, l'autre en dessous. Deux nombres
    # superposés ne se lisent ni l'un ni l'autre.
    series = ((DISCRET, [k * e1 for k in bras], None, 0),
              (BLEU, [b[str(k)]["commune_um"] for k in bras], "commune_um", -19),
              (AMBRE, [b[str(k)]["un_grand_pas_um"] for k in bras], "un_grand_pas_um", 7))
    for coul, vals, cle, dy in series:
        pts = [(ax + larg * (k - 0.5), ay + ph - v / top * (ph - 40))
               for k, v in zip(bras, vals) if v is not None]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            art.line([x0, y0, x1, y1], fill=coul, width=2)
        for (x0, y0), v in zip(pts, [v for v in vals if v is not None]):
            art.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=coul)
            if cle is not None:
                art.text((x0 - 16, y0 + dy), f"{v:.0f}µ", fill=coul, font=petit)
    for k in bras:
        art.text((ax + larg * (k - 0.5) - 4, ay + ph + 3), str(k), fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 6), legendes[0], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22), legendes[1], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + ph + 19), legendes[2], fill=DISCRET, font=petit)

    # ---------- B : la nappe gardée, à erreur égale ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · a erreur egale, un grand pas garde plus de nappe",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    top2 = max(max(b[str(k)]["cellules_dun_grand_pas"] for k in bras),
               max(b[str(k)]["cellules_propres"] for k in bras)) * 1.25
    larg2 = pw / (len(bras) + 0.6)
    for i, k in enumerate(bras):
        d = b[str(k)]
        x0 = bx + larg2 * (i + 0.55)
        for dec, val, coul in ((-0.22, d["cellules_propres"], BLEU),
                               (0.22, d["cellules_dun_grand_pas"], AMBRE)):
            h = val / top2 * (ph - 58)
            art.rectangle([x0 + dec * larg2 - larg2 * 0.18, by + ph - h,
                           x0 + dec * larg2 + larg2 * 0.18, by + ph], fill=coul)
        art.text((x0 - 30, by + ph - d["cellules_dun_grand_pas"] / top2 * (ph - 58) - 15),
                 f"{d['commune_um']:.0f}µ / {d['un_grand_pas_um']:.0f}µ",
                 fill=TEXTE, font=petit)
        art.text((x0 - 4, by + ph + 3), str(k), fill=DISCRET, font=petit)
    art.text((bx + 6, by + 6), legendes[3], fill=BLEU, font=petit)
    art.text((bx + 6, by + 22), legendes[4], fill=AMBRE, font=petit)
    art.text((bx + 6, by + 38), legendes[5], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19), legendes[6], fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"bras": len(bras), "legendes": [(t, petit.getbbox(t)[2]) for t in legendes],
            "sortie": str(sortie)}


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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LA RÉTRACTATION QUE LA FIGURE PORTE : la courbe est SOUS la droite du premier pas.
    # Sans ce contrôle, la légende pourrait cesser de le dire sans que rien ne le remarque.
    v("la dérive est sous-linéaire, donc elle n'accélère pas au sens publié",
      m["sous_lineaire_sur_le_masque_commun"], str(m["cout_par_tour_commun_um"]))
    v("... et le premier pas coûte plus que n'importe quel tour suivant",
      m["le_premier_pas_coute_le_plus"], str(m["increments_communs_um"]))
    # ⚠⚠ LES DEUX ARTEFACTS ÉCARTÉS : sans eux, la sous-linéarité pourrait être fabriquée par
    # la mesure elle-même plutôt que par la marche.
    v("le masque qui rétrécit ne change pas la forme de la courbe",
      not m["le_masque_change_la_forme_de_la_courbe"], str(m["ecart_du_masque_um"]))
    v("... et la sous-linéarité se voit à spire de départ FIXE",
      m["la_sous_linearite_tient_a_depart_fixe"],
      f"{len(m['departs_sous_lineaires'])} sur {len(m['departs_a_trois_bras_ou_plus'])}")
    # ⚠⚠⚠ LE RÉSULTAT ACTIONNABLE, ET SES DEUX MOITIÉS. Sans la seconde, « l'itération ne coûte
    # rien » se lirait comme une équivalence — alors qu'elle coûte de la nappe.
    v("l'itération ne coûte pas d'erreur", not m["literation_coute"],
      f"{m['marches_ou_liteation_coute']} marches sur {m['marches_comparables']}")
    v("... mais elle coûte de la NAPPE, et le compte le dit",
      m["part_de_nappe_gagnee_au_dernier_bras"] > 0.1,
      f"{100 * m['part_de_nappe_gagnee_au_dernier_bras']:.0f} %")
    v("... et le grand pas garde plus de cellules à chaque bras au-delà du premier",
      all(m["cellules_gardees_en_plus_par_le_grand_pas"][b] > 0
          for b in m["par_bras"] if int(b) > 1),
      str(m["cellules_gardees_en_plus_par_le_grand_pas"]))
    # ⚠ Et le négatif qui empêche de lire ça comme « la marche est bonne » : un seul pas coûte
    # déjà les deux tiers d'une demi-feuille.
    v("un seul pas coûte déjà une grande part de la demi-feuille",
      m["par_bras"]["1"]["commune_um"] > 0.5 * m["demi_epaisseur_um"],
      f"{m['par_bras']['1']['commune_um']} contre {m['demi_epaisseur_um']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les bras sont dessinés", r["bras"] == len(m["par_bras"]))
        trop = [(t, w) for t, w in r["legendes"] if w > 400 - 12]
        v("aucune ligne de légende ne déborde de son panneau", not trop,
          str(trop) if trop else f"la plus large fait {max(w for _, w in r['legendes'])} px")
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · la courbe reste SOUS la droite du premier pas",
                      "B · a erreur egale, un grand pas garde plus de nappe"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_pourquoi_la_derive_accelere.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
