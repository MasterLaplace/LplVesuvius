#!/usr/bin/env python3
"""La moitié de l'erreur est un plancher, et le vrai champ de décalages est parfaitement lisse.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Quatre portes se sont fermées sur la lecture et l'écart au
chemin déployé valait toujours une quinzaine de micromètres. Avant d'en ouvrir une cinquième, il
fallait demander si cet écart est **prenable** — c'est-à-dire décomposer les 20 µm de la borne
elle-même.

⭐⭐⭐ Le panneau A répond : **18,2 µm sont irréductibles le long de la normale**, soit la moitié de
l'erreur du chemin déployé. C'est la distance à laquelle le rayon passe de la feuille visée ;
aucun décalage sur cette normale ne descend en dessous. La grille d'un voxel, elle, ne coûte
**rien** — affiner ne rendrait pas un micromètre.

⭐⭐⭐ Et le panneau B dit où est le chantier, ce qu'aucune erreur ne montrerait : le champ de
décalages que produirait une méthode parfaite est **parfaitement lisse** (rugosité 0,0), pendant
que celui du raccrochage est à plus de la moitié de la rugosité du **bruit pur**. Ce qui manque
n'est donc pas une meilleure forme à chercher, c'est un champ **lisse par construction**.

Usage :
    uv run python src/figures/figure_loracle_est_il_atteignable.py --verifier
    uv run python src/figures/figure_loracle_est_il_atteignable.py \\
        --sortie docs/images/75_loracle_est_il_atteignable.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402
from lecart_apparie import tranche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "loracle_est_il_atteignable.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
PLANCHER = (232, 226, 216)
CADRE = (200, 200, 200)


def court(e: dict) -> str:
    return (f"{e['ecart_median_um']:+.1f} um  {e['pas_ameliores']}/{e['pas']}  "
            f"{e['intervalle_um']}")


def prose(m: dict) -> list[str]:
    return [
        f"{m['paires']} pas, {m['cellules']} cellules. les 20 um de la borne sont decomposes : "
        f"ce que coute la GRILLE d'un voxel (l'oracle refait au quart de voxel), ce que coute la "
        f"FENETRE (refait sur +/-{m['rayon_en_feuilles']} feuille), et ce que laisse le RAYON — "
        f"la distance a laquelle la normale passe de la feuille visee.",
        f"⚠ la grille d'un voxel ne coute RIEN : {court(m['ce_que_coute_la_grille'])}. affiner "
        f"le decalage ne rendrait pas un micrometre, ce qui ferme d'avance une piste evidente. "
        f"la fenetre, elle, coute {court(m['ce_que_coute_la_fenetre'])} — mais l'elargir n'est "
        "pas une methode : une fenetre plus large peut se poser sur la feuille VOISINE.",
        f"⚠⚠ ET LE PLANCHER : {m['erreur_rayon_mediane_um']} um, soit "
        f"{m['part_du_rayon_dans_lerreur_deployee']} de l'erreur du chemin deploye "
        f"({m['erreur_deploye_mediane_um']} um). la moitie de ce que coute un pas n'est donc "
        f"PAS une affaire de lecture : c'est la distance a laquelle la normale rate sa cible, et "
        "seule une autre DIRECTION la prendrait. ce qui reste a la lecture est l'ecart apparie "
        f"{court(m['ce_qui_reste_au_deploye'])}.",
        f"⚠⚠⚠ ET LE PANNEAU B DIT OU EST LE CHANTIER. le champ de decalages qu'une methode "
        f"parfaite devrait produire est PARFAITEMENT LISSE : sa rugosite vaut "
        f"{m['rugosite_oracle_mediane_vx']} voxel, et le lisser ne coute que "
        f"{m['lisser_loracle_coute']['ecart_median_um']} um. celui du raccrochage vaut "
        f"{m['rugosite_raccrochage_mediane_vx']}, contre {m['rugosite_melange_mediane_vx']} pour "
        f"du BRUIT pur : il en est a {m['part_de_bruit_dans_le_raccrochage']}.",
        "⚠⚠ ce que ca change pour la suite : le raccrochage ne produit pas un champ un peu "
        "bruite autour du bon, il produit un champ a mi-chemin du hasard, la ou la verite est "
        "plate. ce qui manque n'est donc pas une meilleure FORME a chercher — quatre tranches "
        "l'ont deja ferme — mais un champ lisse PAR CONSTRUCTION, la ou le lissage actuel ne "
        "fait que moyenner du bruit apres coup.",
    ]


def barres_um(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, legende: str) -> list:
    """Les niveaux d'erreur, du repos au plancher, avec la bande irréductible en fond.

    ⚠⚠⚠ LA BANDE DU PLANCHER EST DESSINÉE DERRIÈRE LES BARRES, et c'est tout le propos : elle
    montre d'un coup d'œil quelle part de chaque barre n'est PAS prenable. Des barres seules
    feraient lire cinq nombres ; avec la bande, on lit que la moitié de la première est du sol.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    niveaux = [("ne rien faire", m["erreur_ne_rien_faire_mediane_um"], DISCRET),
               ("chemin DEPLOYE", m["erreur_deploye_mediane_um"], BLEU),
               ("oracle, grille 1 vx", m["erreur_oracle_mediane_um"], VERT),
               ("oracle, grille fine", m["erreur_oracle_fine_mediane_um"], VERT),
               ("le RAYON (plancher)", m["erreur_rayon_mediane_um"], ROUGE)]
    haut = max(v for _, v, _ in niveaux) * 1.12
    gauche, droite = x0 + 150, x0 + pw - 60
    plancher = m["erreur_rayon_mediane_um"]

    def xx(val: float) -> float:
        return gauche + val / haut * (droite - gauche)

    art.rectangle([gauche, y0 + 26, xx(plancher), y0 + ph - 10], fill=PLANCHER)
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    haut_ligne = (ph - 40) / len(niveaux)
    noms = []
    for i, (nom, val, coul) in enumerate(niveaux):
        yc = y0 + 32 + haut_ligne * (i + 0.5)
        noms.append(nom)
        art.text((x0 + 10, yc - 6), nom, fill=TEXTE, font=petit)
        art.rectangle([gauche, yc - 7, xx(val), yc + 7], fill=coul)
        art.text((xx(val) + 6, yc - 6), f"{val:.1f} um", fill=DISCRET, font=petit)
    art.line([xx(plancher), y0 + 26, xx(plancher), y0 + ph - 10], fill=ROUGE)
    return noms


def barres_rugosite(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit,
                    legende: str) -> list:
    """Les trois rugosités, sur la même échelle, le bruit servant d'unité de lecture.

    ⚠⚠ LE BRUIT EST DESSINÉ, PAS RÉSUMÉ : une rugosité seule ne veut rien dire — c'est un
    nombre de voxels. C'est sa position entre zéro et le bruit pur qui porte le sens.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    lignes = [("champ de l'ORACLE", m["rugosite_oracle_mediane_vx"], VERT),
              ("champ du RACCROCHAGE", m["rugosite_raccrochage_mediane_vx"], BLEU),
              ("temoin : gabarit MELANGE", m["rugosite_melange_mediane_vx"], AMBRE)]
    haut = max(v for _, v, _ in lignes if v is not None) * 1.15
    gauche, droite = x0 + 170, x0 + pw - 60
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    haut_ligne = (ph - 40) / len(lignes)
    noms = []
    for i, (nom, val, coul) in enumerate(lignes):
        yc = y0 + 32 + haut_ligne * (i + 0.5)
        noms.append(nom)
        art.text((x0 + 10, yc - 6), nom, fill=TEXTE, font=petit)
        if val is None:
            continue
        largeur = val / haut * (droite - gauche)
        art.rectangle([gauche, yc - 7, gauche + max(2.0, largeur), yc + 7], fill=coul)
        art.text((gauche + largeur + 8, yc - 6), f"{val:.2f} vx", fill=DISCRET, font=petit)
    art.text((x0 + 10, y0 + ph - 18),
             "zero = un champ plat · a droite = du bruit pur", fill=DISCRET, font=petit)
    return noms


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart = 40, 440, 46
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    ph = 210
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "La moitie de l'erreur est un plancher, et la verite est plate",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} pas · {m['cellules']} cellules · la borne elle-meme, decomposee",
             fill=DISCRET, font=moyen)
    art.text((marge, 76), "A · ce que chaque terme coute, et ce que le rayon ne rend pas",
             fill=TEXTE, font=moyen)
    eta = barres_um(art, marge, 96, pw, ph, m, petit,
                    "bande claire : la part qu'AUCUN decalage sur la normale ne prend")
    bx = marge + pw + ecart
    art.text((bx, 76), "B · la rugosite du champ de decalages, contre celle du bruit",
             fill=TEXTE, font=moyen)
    eta += barres_rugosite(art, bx, 96, pw, ph, m, petit,
                           "de combien un decalage s'ecarte de la mediane de ses voisins")
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"niveaux": len(eta), "etiquettes": eta,
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "panneau": pw, "sortie": str(sortie)}


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
    # ⚠⚠ LES BORNES SONT EMBOÎTÉES PAR CONSTRUCTION : le rayon contient la grille fine, qui
    # contient celle d'un voxel. Une figure tirée d'une mesure où l'ordre serait rompu
    # dessinerait un plancher au-dessus de ce qu'il borne.
    v("les bornes sont emboîtées : rayon ≤ oracle fin ≤ oracle",
      m["erreur_rayon_mediane_um"] <= m["erreur_oracle_fine_mediane_um"] + 0.05
      <= m["erreur_oracle_mediane_um"] + 0.1,
      f"{m['erreur_rayon_mediane_um']} ≤ {m['erreur_oracle_fine_mediane_um']} ≤ "
      f"{m['erreur_oracle_mediane_um']}")
    # ⭐⭐⭐ LE RÉSULTAT DU PANNEAU A : affiner ne rend rien, et la moitié de l'erreur est du sol.
    v("affiner la grille d'un voxel ne rend RIEN", not m["la_grille_coute_quelque_chose"],
      str(m["ce_que_coute_la_grille"]))
    v("... et le plancher vaut près de la moitié de l'erreur du chemin déployé",
      0.4 < m["part_du_rayon_dans_lerreur_deployee"] < 0.6,
      str(m["part_du_rayon_dans_lerreur_deployee"]))
    v("... ce qui reste à la lecture est un écart apparié qui TRANCHE",
      tranche(m["ce_qui_reste_au_deploye"]), str(m["ce_qui_reste_au_deploye"]))
    # ⭐⭐⭐ LE RÉSULTAT DU PANNEAU B, et il est l'inverse de ce qu'on aurait supposé : la vérité
    # est plate, et c'est notre champ qui est bruité.
    v("le champ de l'oracle est plus lisse que celui du raccrochage",
      m["loracle_est_plus_lisse_que_le_raccrochage"],
      f"{m['rugosite_oracle_mediane_vx']} contre {m['rugosite_raccrochage_mediane_vx']} vx")
    v("... et le raccrochage est à mi-chemin du bruit pur",
      0.3 < m["part_de_bruit_dans_le_raccrochage"] < 0.8,
      str(m["part_de_bruit_dans_le_raccrochage"]))
    # ⚠⚠ ET LE CONTRÔLE QUI EMPÊCHE LA FIGURE DE PUBLIER DEUX NOMBRES QUI SE CONTREDISENT : un
    # champ dont la rugosité est nulle ne peut pas être présenté comme rugueux.
    v("... et lisser l'oracle ne coûte presque rien, cohérent avec sa rugosité",
      abs(m["lisser_loracle_coute"]["ecart_median_um"])
      < m["erreur_oracle_mediane_um"] / 10.0,
      f"{m['lisser_loracle_coute']['ecart_median_um']} µm sur "
      f"{m['erreur_oracle_mediane_um']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les cinq niveaux et les trois rugosités sont dessinés", r["niveaux"] == 8,
          str(r["niveaux"]))
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"][:3]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · ce que chaque terme coute, et ce que le rayon ne rend pas",
                      "B · la rugosite du champ de decalages, contre celle du bruit"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < r["panneau"],
              f"{pt_.getbbox(titre)[2]} px pour {r['panneau']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_loracle_est_il_atteignable.png")
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
