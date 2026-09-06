#!/usr/bin/env python3
"""Tourner le pas ne rend rien — et l'oracle qui semblait le dire n'était pas une borne.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. La tranche précédente a mesuré que **48,5 %** de ce que coûte un
pas est un plancher que seul un changement de **direction** prendrait. Le seul chiffre que la
campagne avait dessus — « la rotation vaut 3 % » — venait de l'instrument non apparié que la
rétraction du registre a invalidé.

⭐ Le panneau A refait la mesure avec les instruments de la famille : une rotation **d'ensemble**,
ajustée **hors échantillon**, ne prend que **3,4 %** de ce que prend un oracle par cellule, et son
écart apparié tourne autour du dixième de micromètre. Le 3 % est confirmé, sur huit pas.

⚠⚠⚠ Et le panneau B porte le contrôle qui a payé immédiatement : **96,6 % des cellules choisissent
le BORD du cône**. Ce que l'oracle de direction rend n'est donc pas une borne mais un plancher du
balayage — et l'élargir ne le sauverait pas, puisque le point le plus proche du nuage se trouve à
**33,5°**, c'est-à-dire que l'optimum non borné est « viser ce qui est le plus près », qui n'est
pas la correspondance entre deux surfaces.

Usage :
    uv run python src/figures/figure_la_direction_du_pas.py --verifier
    uv run python src/figures/figure_la_direction_du_pas.py \\
        --sortie docs/images/75_la_direction_du_pas.png
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
MESURE = RACINE / "docs" / "mesures" / "la_direction_du_pas.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
PALE = (232, 226, 216)
CADRE = (200, 200, 200)


def court(e) -> str:
    if e is None or e["ecart_median_um"] is None:
        return "—"
    return (f"{e['ecart_median_um']:+.1f} um  {e['pas_ameliores']}/{e['pas']}  "
            f"{e['intervalle_um']}")


def prose(m: dict) -> list[str]:
    large = m["cone_le_plus_large"]
    return [
        f"{m['paires']} pas, {m['cellules']} cellules, {m['rotations_essayees']} rotations. le "
        f"pas angulaire est DERIVE : {m['pas_angulaire_deg']}° est la rotation qui deplace le "
        f"point d'arrivee d'un voxel, exactement comme la grille des decalages. et le cone n'est "
        f"pas choisi mais BALAYE — quatre demi-angles emboites, {m['demi_angles_deg']} degres.",
        f"⚠ une rotation d'ENSEMBLE, ajustee HORS ECHANTILLON — chaque pas juge a l'angle que les "
        f"AUTRES pas ont prefere — ne rend rien : {court(large['globale_contre_sans_rotation'])} "
        f"au plus large cone, contre {m['erreur_sans_rotation_mediane_um']} um sans rotation. "
        f"elle ne prend que {m['part_de_loracle_prise_par_une_rotation_densemble']} de ce que "
        f"prend l'oracle par cellule. le « 3 % » de la premiere campagne est CONFIRME, cette fois "
        "avec l'ecart apparie et sur huit pas.",
        f"⚠⚠⚠ ET LE CONTROLE QUI A PAYE IMMEDIATEMENT : {m['part_au_bord_du_cone']} des cellules "
        f"choisissent le BORD du cone. ce que l'oracle de direction rend "
        f"({court(large['oracle_contre_sans_rotation'])}) n'est donc PAS une borne mais un "
        f"plancher du balayage — et publier 2,9 um comme « ce que la direction vaut » aurait "
        "presente la limite d'une grille comme une limite de la matiere.",
        f"⚠⚠ et l'elargir ne le sauverait pas : le point le plus proche du nuage se trouve a "
        f"{m['angle_au_plus_proche_median_deg']}° de la normale, bien au-dela du cone. l'optimum "
        f"non borne est donc « viser ce qui est le plus pres » — or deux surfaces se "
        f"correspondent par leur PARAMETRAGE, jamais par leur proximite. l'oracle de direction "
        "par cellule est DEGENERE, et aucun cone ne le rend legitime.",
        f"⚠⚠ ce qui reste vrai et utilisable : le champ de rotations optimales est LISSE "
        f"localement (rugosite {m['rugosite_alpha_mediane_deg']}° pour un pas de "
        f"{m['pas_angulaire_deg']}°) et ETENDU a travers la feuille "
        f"({m['etendue_alpha_mediane_deg']}° / {m['etendue_beta_mediane_deg']}°). c'est "
        "precisement pourquoi un biais global n'en prend rien : ce qui aiderait varie lentement "
        "d'un bout de la feuille a l'autre, et un seul angle ne peut pas suivre.",
    ]


def courbe(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, legende: str) -> list:
    """Ce que chaque cône achète, l'oracle et la rotation d'ensemble sur la même échelle."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    xs = [x["demi_angle_deg"] for x in m["resume"]]
    oracle = [x["oracle_contre_sans_rotation"]["ecart_median_um"] for x in m["resume"]]
    globale = [(x["globale_contre_sans_rotation"]["ecart_median_um"]
                if x["globale_contre_sans_rotation"] else 0.0) for x in m["resume"]]
    bas = min(0.0, min(oracle + globale)) * 1.15
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    base = y0 + 40
    hmax = ph - 80
    gauche, droite = x0 + 60, x0 + pw - 30

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, len(xs) - 1)

    def py(val: float) -> float:
        return base + (val / bas) * hmax if bas else base

    art.line([gauche - 10, base, droite + 10, base], fill=TEXTE)
    art.text((x0 + 8, base - 7), "0", fill=DISCRET, font=petit)
    for serie, coul, nom in ((oracle, ROUGE, "ORACLE par cellule"),
                             (globale, BLEU, "rotation d'ENSEMBLE")):
        pts = [(px(i), py(v)) for i, v in enumerate(serie)]
        for (ax, ay), (bx_, by_) in zip(pts, pts[1:]):
            art.line([ax, ay, bx_, by_], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        art.text((pts[-1][0] - petit.getbbox(nom)[2], pts[-1][1] + 6), nom,
                 fill=coul, font=petit)
    for i, x in enumerate(xs):
        art.text((px(i) - 12, y0 + ph - 30), f"{x:.2f}°", fill=DISCRET, font=petit)
        val = oracle[i]
        art.text((px(i) - 14, py(val) - 15), f"{val:+.1f}", fill=DISCRET, font=petit)
    art.text((x0 + 10, y0 + ph - 16),
             "abscisse : demi-angle du cone · ordonnee : ecart apparie, um",
             fill=DISCRET, font=petit)
    return [f"{x:.2f}deg" for x in xs]


def diagnostic(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, legende: str) -> list:
    """Le cône, l'étendue des rotations choisies, et où se trouve le point le plus proche."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    large = m["cone_le_plus_large"]["demi_angle_deg"]
    proche = m["angle_au_plus_proche_median_deg"]
    haut_deg = proche * 1.18
    gauche, droite = x0 + 20, x0 + pw - 20

    def px(deg: float) -> float:
        return gauche + (droite - gauche) * deg / haut_deg

    lignes = [("le CONE balaye", large, VERT),
              ("etendue des rotations choisies", m["etendue_alpha_mediane_deg"], AMBRE),
              ("le point le plus PROCHE", proche, ROUGE)]
    haut_ligne = (ph - 74) / len(lignes)
    noms = []
    art.rectangle([px(0.0), y0 + 34, px(large), y0 + ph - 40], fill=PALE)
    for i, (nom, val, coul) in enumerate(lignes):
        yc = y0 + 44 + haut_ligne * i
        noms.append(nom)
        art.text((x0 + 12, yc - 16), nom, fill=TEXTE, font=petit)
        art.rectangle([px(0.0), yc, px(val), yc + 10], fill=coul)
        art.text((px(val) + 6, yc - 2), f"{val:.1f} deg", fill=DISCRET, font=petit)
    art.text((x0 + 12, y0 + ph - 34),
             f"{m['part_au_bord_du_cone']:.1%} des cellules choisissent le BORD du cone :",
             fill=TEXTE, font=petit)
    art.text((x0 + 12, y0 + ph - 18),
             "ce n'est donc pas une borne, et l'elargir vise ce qui est le plus pres",
             fill=DISCRET, font=petit)
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
    ph = 230
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Tourner le pas ne rend rien, et l'oracle n'etait pas une borne",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} pas · {m['cellules']} cellules · "
             f"{m['rotations_essayees']} rotations · pas angulaire {m['pas_angulaire_deg']}°",
             fill=DISCRET, font=moyen)
    art.text((marge, 76), "A · ce que chaque cone achete, par cellule et en bloc",
             fill=TEXTE, font=moyen)
    eta = courbe(art, marge, 96, pw, ph, m, petit,
                 "rouge : oracle par cellule (borne)  bleu : rotation d'ensemble (hors ech.)")
    bx = marge + pw + ecart
    art.text((bx, 76), "B · pourquoi l'oracle n'en est pas une", fill=TEXTE, font=moyen)
    eta += diagnostic(art, bx, 96, pw, ph, m, petit,
                      "en degres, sur une meme echelle")
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"cones": len(m["resume"]), "etiquettes": eta,
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
    large = m["cone_le_plus_large"]
    # ⚠⚠ LES CÔNES SONT EMBOÎTÉS ET L'ORACLE MONOTONE : ajouter une liberté ne peut pas faire
    # pire, et une courbe qui remonterait dirait qu'on ne compare pas des sous-ensembles.
    gains = [x["oracle_contre_sans_rotation"]["ecart_median_um"] for x in m["resume"]]
    v("l'oracle est monotone quand le cône s'élargit",
      all(b <= a + 1e-9 for a, b in zip(gains, gains[1:])), str(gains))
    # ⭐⭐⭐ LE RÉSULTAT PRINCIPAL : la rotation d'ensemble ne rend rien, et le « 3 % » est
    # confirmé avec l'instrument apparié.
    v("une rotation d'ENSEMBLE, hors échantillon, ne tranche pas au plus large cône",
      not m["une_rotation_densemble_ameliore"],
      str(large["globale_contre_sans_rotation"]))
    v("... et elle ne prend qu'une fraction minuscule de ce que prend l'oracle",
      m["part_de_loracle_prise_par_une_rotation_densemble"] < 0.1,
      str(m["part_de_loracle_prise_par_une_rotation_densemble"]))
    # ⚠⚠⚠ LE CONTRÔLE QUI A PAYÉ : l'oracle de direction n'est PAS une borne.
    v("l'oracle de direction n'est PAS une borne : les cellules saturent au bord",
      not m["loracle_de_direction_est_une_borne"] and m["part_au_bord_du_cone"] > 0.9,
      f"{m['part_au_bord_du_cone']:.1%} au bord")
    v("... et l'élargir ne le sauverait pas : l'optimum non borné est bien au-delà",
      m["loracle_de_direction_degenere"]
      and m["angle_au_plus_proche_median_deg"] > 3 * large["demi_angle_deg"],
      f"{m['angle_au_plus_proche_median_deg']}° contre un cône de "
      f"{large['demi_angle_deg']:.2f}°")
    # ⭐ ET CE QUI RESTE VRAI : le champ de rotations est lisse localement et étendu globalement.
    v("le champ de rotations est lisse localement et étendu à travers la feuille",
      m["le_champ_de_rotation_est_plus_lisse_quun_pas"]
      and m["le_champ_de_rotation_varie_a_travers_la_feuille"],
      f"rugosité {m['rugosite_alpha_mediane_deg']}° · étendue "
      f"{m['etendue_alpha_mediane_deg']}°")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les cônes sont dessinés", r["cones"] == len(m["resume"]), str(r["cones"]))
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
        for titre in ("A · ce que chaque cone achete, par cellule et en bloc",
                      "B · pourquoi l'oracle n'en est pas une"):
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
                   default=RACINE / "docs" / "images" / "75_la_direction_du_pas.png")
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
