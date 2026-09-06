#!/usr/bin/env python3
"""L'écart déjà franchi ne dit presque rien du suivant.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Un tiers du coût d'un pas vient d'une longueur prise sur la
mauvaise population, et un dérouleur ne peut pas mesurer l'écart qu'il n'a pas encore franchi.
Il peut mesurer celui qu'il vient de franchir — c'était la seule piste positive qui restait.

⚠⚠ Le panneau B la ferme, et il la ferme en la MONTRANT plutôt qu'en la résumant : quand l'écart
franchi parcourt **137 µm**, le suivant n'en parcourt que **46**, et dans le mauvais sens. Si le
premier prédisait le second, les points suivraient la diagonale ; ils sont plats.

⚠ Ce qui reste est petit mais réel : la **médiane** de l'écart franchi, prise comme longueur
unique, bat le pas nominal sur 4 triplets sur 5 — 1,8 µm des 20 que connaître le vrai écart
rapporterait, soit un dixième.

Usage :
    uv run python src/figures/figure_lecart_deja_franchi.py --verifier
    uv run python src/figures/figure_lecart_deja_franchi.py \\
        --sortie docs/images/75_lecart_deja_franchi.png
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
MESURE = RACINE / "docs" / "mesures" / "lecart_deja_franchi.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    d = m["ecart_avant_contre_apres"]
    return [
        f"{m['triplets']} triplets de spires consecutives, {m['cellules']} cellules. le "
        "predicteur est DISPONIBLE : la distance de chaque point a la spire precedente se "
        "calcule avec les deux ancres que le derouleur a deja, et rien de la cible n'y entre.",
        f"mais il ne predit rien : rho {d['rho']} sur {d['n']} cellules, donc NEGATIF et "
        f"minuscule. le panneau B le montre — quand l'ecart franchi parcourt "
        f"{m['etendue_de_lecart_franchi_um']} um, le suivant n'en parcourt que "
        f"{m['etendue_de_lecart_suivant_um']}, et en descendant.",
        f"en erreur de marche : nominal {m['erreur_nominale_mediane_um']} um, PREDIT "
        f"{m['erreur_predite_mediane_um']}, recentre {m['erreur_recentree_mediane_um']}, "
        f"melange {m['erreur_melangee_mediane_um']}, oracle {m['erreur_oracle_mediane_um']}. la "
        f"prediction ne bat le nominal que sur "
        f"{m['triplets_ou_la_prediction_bat_le_nominal']} triplets sur {m['triplets']} : ce "
        "n'est pas un verdict, c'est une mediane que le compte par cas contredit.",
        "⚠ ce qui reste est petit mais reel : la MEDIANE de l'ecart franchi, prise comme "
        "longueur unique et sans aucune information par point, bat le nominal sur "
        f"{m['triplets_ou_le_recentrage_bat_le_nominal']} triplets sur {m['triplets']} — "
        f"{m['gain_du_recentrage_um']} um sur les "
        f"{m['erreur_nominale_mediane_um'] - m['erreur_oracle_mediane_um']:.0f} que connaitre "
        "le vrai ecart rapporterait, soit un dixieme.",
        "⚠⚠ le temoin MELANGE — les memes longueurs attribuees aux mauvais points — fait PIRE "
        f"que le nominal ({m['gain_du_melange_seul_um']} um). une longueur par point tiree dans "
        "la bonne distribution mais mal placee coute donc plus qu'elle ne rapporte : c'est le "
        "bruit d'un predicteur qui ne predit pas.",
        f"⚠ et l'oracle reste a {m['erreur_oracle_mediane_um']} um, tres loin sous tout le "
        "reste : le gain existe, il n'est simplement pas atteignable depuis l'ecart precedent.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ph, ecart = 40, 400, 250, 56
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    legendes = [
        "gris : NOMINAL   ambre : predit par point   bleu : recentre",
        "rouge : oracle · abscisse : les triplets, par leur spire de depart",
        "trait fin : la diagonale — ou seraient les points si le franchi predisait",
        "abscisse : ecart FRANCHI (um)   ordonnee : ecart SUIVANT (um)",
    ]
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "L'ecart deja franchi ne dit presque rien du suivant",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['triplets']} triplets · {m['cellules']} cellules · rho "
             f"{m['ecart_avant_contre_apres']['rho']}", fill=DISCRET, font=moyen)

    # ---------- A : les quatre contendants ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · marcher le pas nominal, le predit, le recentre, l'oracle",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    lg = m["lignes"]
    cles = (("erreur_nominale_um", DISCRET), ("erreur_predite_um", AMBRE),
            ("erreur_recentree_um", BLEU), ("erreur_oracle_um", ROUGE))
    top = max(e[c] for e in lg for c, _ in cles) * 1.2
    larg = pw / (len(lg) + 0.6)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 46)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    art.text((ax + pw - 128, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for i, e in enumerate(lg):
        x0 = ax + larg * (i + 0.55)
        for k, (cle, coul) in enumerate(cles):
            dec = (k - 1.5) * 0.21
            h = e[cle] / top * (ph - 46)
            art.rectangle([x0 + dec * larg - larg * 0.09, ay + ph - h,
                           x0 + dec * larg + larg * 0.09, ay + ph], fill=coul)
        art.text((x0 - 8, ay + ph + 3), str(e["depuis"]), fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 6), legendes[0], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22), legendes[1], fill=DISCRET, font=petit)

    # ---------- B : le suivant par décile du franchi ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · s'il predisait, les points suivraient la diagonale",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    tr = m["apres_par_decile_de_avant"]
    top2 = max(max(t["avant_median_um"] for t in tr),
               max(t["apres_median_um"] for t in tr)) * 1.12
    def px(val):  # noqa: E306
        return bx + 34 + (val / top2) * (pw - 50)

    def py(val):
        return by + ph - 30 - (val / top2) * (ph - 62)

    art.line([px(0), py(0), px(top2), py(top2)], fill=DISCRET)
    pts = [(px(t["avant_median_um"]), py(t["apres_median_um"])) for t in tr]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        art.line([x0, y0, x1, y1], fill=AMBRE, width=2)
    for x0, y0 in pts:
        art.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=AMBRE)
    yn = py(m["pas_nominal_um"])
    art.line([bx, yn, bx + pw, yn], fill=TEXTE)
    art.text((bx + pw - 96, yn - 14), f"nominal {m['pas_nominal_um']:.0f}µ",
             fill=TEXTE, font=petit)
    art.text((bx + 6, by + 6), legendes[2], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 3), legendes[3], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19),
             f"le franchi parcourt {m['etendue_de_lecart_franchi_um']:.0f}µ, le suivant "
             f"{m['etendue_de_lecart_suivant_um']:.0f}µ", fill=AMBRE, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    etiquettes = [str(e["depuis"]) for e in lg]
    return {"triplets": len(lg), "deciles": len(tr), "etiquettes": etiquettes,
            "legendes": [(t, petit.getbbox(t)[2]) for t in legendes],
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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LE NÉGATIF QUE LA FIGURE PORTE : le prédicteur ne prédit pas. Sans ce contrôle, la
    # prose pourrait cesser de le dire sans que rien ne le remarque.
    v("l'écart franchi ne prédit PAS le suivant",
      not m["lecart_franchi_predit_le_suivant"],
      f"rho {m['ecart_avant_contre_apres']['rho']} sur "
      f"{m['ecart_avant_contre_apres']['n']} cellules")
    # ⚠⚠ ET CE QUI REND LE PANNEAU B LISIBLE : la courbe des déciles est PLATE devant l'étendue
    # du prédicteur. Un rho seul ne dirait pas si la relation est petite ou juste bruitée.
    v("... et la courbe des déciles est plate devant l'étendue du prédicteur",
      m["etendue_de_lecart_suivant_um"] < 0.5 * m["etendue_de_lecart_franchi_um"],
      f"{m['etendue_de_lecart_suivant_um']} contre {m['etendue_de_lecart_franchi_um']} µm")
    v("... la prédiction par point ne bat pas le nominal", not m["la_prediction_bat_le_nominal"],
      f"{m['triplets_ou_la_prediction_bat_le_nominal']} triplets sur {m['triplets']}")
    # ⚠⚠ ET LE POSITIF QUI RESTE, sans lequel la figure dirait « rien n'est possible » là où un
    # dixième du gain l'est : le RECENTRAGE bat le nominal.
    v("le recentrage seul bat le nominal", m["le_recentrage_bat_le_nominal"],
      f"{m['triplets_ou_le_recentrage_bat_le_nominal']} triplets sur {m['triplets']}")
    v("... mais il ne prend qu'une petite part de ce que l'oracle prendrait",
      m["gain_du_recentrage_um"]
      < 0.2 * (m["erreur_nominale_mediane_um"] - m["erreur_oracle_mediane_um"]),
      f"{m['gain_du_recentrage_um']} sur "
      f"{m['erreur_nominale_mediane_um'] - m['erreur_oracle_mediane_um']:.1f} µm")
    # ⚠⚠ L'ORACLE EST UNE BORNE : s'il était battu par un aveugle, quelque chose fuirait.
    v("l'oracle reste sous tous les contendants aveugles",
      all(e["erreur_oracle_um"] <= min(e["erreur_nominale_um"], e["erreur_predite_um"],
                                       e["erreur_recentree_um"], e["erreur_melangee_um"]) + 0.05
          for e in m["lignes"]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les triplets sont dessinés", r["triplets"] == m["triplets"])
        v("tous les déciles sont dessinés", r["deciles"] == len(m["apres_par_decile_de_avant"]))
        trop = [(t, w) for t, w in r["legendes"] if w > 400 - 12]
        v("aucune ligne de légende ne déborde de son panneau", not trop,
          str(trop) if trop else f"la plus large fait {max(w for _, w in r['legendes'])} px")
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · marcher le pas nominal, le predit, le recentre, l'oracle",
                      "B · s'il predisait, les points suivraient la diagonale"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_lecart_deja_franchi.png")
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
