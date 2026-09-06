#!/usr/bin/env python3
"""Le tiers du coût d'un pas est une longueur prise sur la mauvaise population.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le premier pas coûte 42,7 µm et c'est le seul poste qui reste.
Le panneau A le décompose en une **hiérarchie de libertés** : chaque marche de l'escalier est ce
qu'une classe de remèdes rapporterait **au mieux**, et le plancher est ce que rien ne prend.

⭐⭐ Le panneau B porte la découverte : la meilleure longueur ne suit **pas** le pas nominal de
135,5 µm, elle suit l'**écart local** mesuré dans la boîte — 104,1 µm. Le pas nominal est la
médiane sur **toutes** les spires du fragment ; la boîte où toute cette campagne mesure est une
région plus serrée. Ce tiers du coût n'est donc pas un réglage à trouver, c'est un nombre à
**mesurer**.

Usage :
    uv run python src/figures/figure_le_cout_dun_seul_pas.py --verifier
    uv run python src/figures/figure_le_cout_dun_seul_pas.py \\
        --sortie docs/images/75_le_cout_dun_seul_pas.png
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
MESURE = RACINE / "docs" / "mesures" / "le_cout_dun_seul_pas.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def etages(m: dict) -> list[tuple[str, float, float]]:
    """Les quatre marches de l'escalier : leur nom, ce qu'elles enlèvent, ce qui reste après.

    ⚠ Construites depuis les niveaux publiés plutôt que recopiées : une figure qui réécrirait
    les gains les recalculerait, et deux calculs d'une même différence finissent par ne pas
    s'accorder.
    """
    n = [m["e0_nominal_median_um"], m["e1_meilleure_longueur_median_um"],
         m["e2_plus_rotation_median_um"], m["e3_par_point_median_um"]]
    noms = ["longueur", "+ rotation", "+ point a point"]
    return [(noms[i], n[i] - n[i + 1], n[i + 1]) for i in range(3)]


def prose(m: dict) -> list[str]:
    return [
        f"{m['paires']} paires consecutives de spires, boite de "
        f"{m['boite']['cote_voxels']:.0f} voxels, {m['rotations_essayees']} rotations essayees. "
        "tout est aveugle : aucune lecture du volume.",
        "⚠⚠ CE NE SONT PAS DES METHODES, CE SONT DES BORNES. E1, E2 et E3 sont choisis EN "
        "REGARDANT LA CIBLE : aucun derouleur ne peut les atteindre. ils disent ce qu'un remede "
        "parfait de cette classe rapporterait, et la liberte donnee est bornee expres — laisser "
        "chaque point aller ou il veut rendrait zero et ne dirait rien.",
        f"E0 {m['e0_nominal_median_um']} um → E1 {m['e1_meilleure_longueur_median_um']} → E2 "
        f"{m['e2_plus_rotation_median_um']} → E3 {m['e3_par_point_median_um']} um. une meilleure "
        f"longueur constante prend {100 * m['part_du_cout_prise_par_la_longueur']:.0f} % du "
        f"cout, une rotation globale {100 * m['part_du_cout_prise_par_la_direction']:.0f} %, une "
        f"correction PAR POINT {100 * m['part_du_cout_prise_par_le_point_a_point']:.0f} %, et le "
        f"plancher en garde {100 * m['part_irreductible']:.0f} %.",
        "et le panneau B dit pourquoi le premier tiers existe : la meilleure longueur suit "
        f"l'ecart LOCAL mesure dans la boite ({m['distance_sans_bouger_mediane_um']} um) et non "
        f"le pas NOMINAL ({m['pas_nominal_um']}), sur "
        f"{m['paires_ou_la_longueur_suit_lecart_local']} paires sur "
        f"{m['paires_comparees_a_lecart_local']} hors butee. le nominal est la mediane sur "
        "TOUTES les spires du fragment ; cette boite est une region plus serree.",
        f"⚠ deux paires butent sur le bord de la fenetre de recherche : leur minimum est "
        "ailleurs, ce n'est pas un optimum mais un refus, et la mediane des longueurs est donc "
        "publiee AUSSI sans elles "
        f"({m['longueur_retenue_mediane_hors_butee_um']} um sur "
        f"{m['paires_comparees_a_lecart_local']} paires).",
        f"⚠⚠ le plancher, {m['plancher_um']} um, est ce qu'un raccrochage PARFAIT le long de la "
        f"normale laisserait. il tient la feuille "
        f"({m['plancher_um']} contre {m['demi_epaisseur_um']} um), donc rien n'interdit au "
        "raccrochage de marcher — mais il n'a que "
        f"{100 * m['part_du_cout_prise_par_le_point_a_point']:.0f} % du cout a prendre, la ou "
        "la longueur en a un tiers pour rien.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ph, ecart = 40, 400, 250, 56
    # ⚠⚠ LA LARGEUR DE COUPE EST MESURÉE, PAS COMPTÉE EN CARACTÈRES. Une ligne en capitales est
    # bien plus large qu'une ligne en bas de casse à nombre de caractères égal, donc une coupe à
    # 128 signes laisse déborder les lignes qui crient — et une ligne qui déborde de l'image se
    # lit tronquée, donc faux. La coupe est resserrée jusqu'à ce que la plus large tienne.
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    legendes = [
        "chaque marche : ce qu'une classe de remedes prend, AU MIEUX",
        "en bas, le plancher que rien ne prend",
        "bleu : ecart LOCAL (ne pas bouger)   ambre : meilleure longueur",
        "trait : le pas NOMINAL, le meme partout",
        "abscisse : les paires de spires consecutives · (b) butee sur la fenetre",
    ]
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le tiers du cout d'un pas est une longueur prise ailleurs",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} paires · un pas coute {m['e0_nominal_median_um']} um · plancher "
             f"{m['plancher_um']} um", fill=DISCRET, font=moyen)

    # ---------- A : l'escalier des libertés ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · ce que chaque classe de remedes prend, au mieux",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    e0 = m["e0_nominal_median_um"]
    top = e0 * 1.05
    marches = etages(m)
    larg = pw / (len(marches) + 1.4)
    haut_de = lambda val: (val / top) * (ph - 56)  # noqa: E731
    y0 = ay + ph
    # la colonne de gauche : le coût entier
    art.rectangle([ax + 12, y0 - haut_de(e0), ax + 12 + larg * 0.5, y0], fill=DISCRET)
    art.text((ax + 12, y0 - haut_de(e0) - 15), f"E0 {e0:.0f}µ", fill=TEXTE, font=petit)
    reste = e0
    for i, (nom, gain, apres) in enumerate(marches):
        x0 = ax + 12 + larg * (i + 0.85)
        art.rectangle([x0, y0 - haut_de(reste), x0 + larg * 0.5, y0 - haut_de(apres)],
                      fill=AMBRE)
        art.rectangle([x0, y0 - haut_de(apres), x0 + larg * 0.5, y0], fill=BLEU)
        art.text((x0, y0 - haut_de(reste) - 15), f"-{gain:.1f}µ", fill=AMBRE, font=petit)
        # ⚠ Les noms sont ALTERNÉS sur deux lignes : trois étiquettes sur quatre cents pixels se
        # chevauchent, et deux noms superposés ne se lisent ni l'un ni l'autre.
        art.text((x0 - 4, y0 + 3 + 15 * (i % 2)), nom, fill=DISCRET, font=petit)
        reste = apres
    art.text((ax + 12 + larg * 2.6, y0 - haut_de(reste) - 15), f"plancher {reste:.0f}µ",
             fill=BLEU, font=petit)
    art.text((ax + 6, ay + 6), legendes[0], fill=AMBRE, font=petit)
    art.text((ax + 6, ay + 22), legendes[1], fill=BLEU, font=petit)

    # ---------- B : la longueur suit l'écart local ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · la meilleure longueur suit l'ecart LOCAL, pas le nominal",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    lg = m["lignes"]
    top2 = max(max(e["distance_sans_bouger_um"] for e in lg),
               max(e["longueur_retenue_um"] for e in lg), m["pas_nominal_um"]) * 1.2
    larg2 = pw / (len(lg) + 0.6)
    yn = by + ph - m["pas_nominal_um"] / top2 * (ph - 58)
    art.line([bx, yn, bx + pw, yn], fill=TEXTE)
    # ⚠ L'étiquette du trait est posée à DROITE : à gauche elle tombe sur la première paire, et
    # un nombre par-dessus une barre ne se lit ni comme l'un ni comme l'autre.
    art.text((bx + pw - 92, yn - 14), f"nominal {m['pas_nominal_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for i, e in enumerate(lg):
        x0 = bx + larg2 * (i + 0.55)
        for dec, val, coul in ((-0.22, e["distance_sans_bouger_um"], BLEU),
                               (0.22, e["longueur_retenue_um"], AMBRE)):
            h = val / top2 * (ph - 58)
            art.rectangle([x0 + dec * larg2 - larg2 * 0.18, by + ph - h,
                           x0 + dec * larg2 + larg2 * 0.18, by + ph], fill=coul)
        # ⚠ Le marqueur de butée est un signe que la police REND : ce dépôt a déjà publié une
        # figure portant une étoile qui sortait en carré vide.
        etiquette = f"{e['de']}→{e['vers']}" + (" (b)" if e["longueur_au_bord_de_la_fenetre"]
                                                else "")
        art.text((x0 - 14, by + ph + 3), etiquette, fill=DISCRET, font=petit)
    art.text((bx + 6, by + 6), legendes[2], fill=DISCRET, font=petit)
    art.text((bx + 6, by + 22), legendes[3], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19), legendes[4], fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠⚠ TOUT CE QUI EST DESSINÉ EST RENDU POUR CONTRÔLE, pas seulement les légendes : les
    # étiquettes d'axe et les lignes de prose portaient des caractères et des largeurs que le
    # contrôle de traçabilité ne regardait pas, et une figure a été publiée avec un marqueur qui
    # sortait en carré vide.
    etiquettes = [nom for nom, _, _ in marches] + [
        f"{e['de']}→{e['vers']}" + (" (b)" if e["longueur_au_bord_de_la_fenetre"] else "")
        for e in lg]
    return {"marches": len(marches), "paires": len(lg),
            "legendes": [(t, petit.getbbox(t)[2]) for t in legendes],
            "etiquettes": etiquettes,
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
    # ⚠⚠ L'ESCALIER EST CONSTRUIT DEPUIS LES NIVEAUX PUBLIÉS, jamais recalculé : les gains
    # dessinés doivent être exactement ceux de la mesure, sinon la figure porterait des nombres
    # que le JSON ne contient pas.
    gains = [g for _, g, _ in etages(m)]
    v("les marches dessinées sont exactement les gains publiés",
      all(abs(a - b) < 0.05 for a, b in zip(gains, [
          m["gain_dune_meilleure_longueur_um"], m["gain_dune_rotation_globale_um"],
          m["gain_dune_correction_par_point_um"]])), str([round(g, 1) for g in gains]))
    v("... et la dernière marche laisse le plancher publié",
      abs(etages(m)[-1][2] - m["plancher_um"]) < 0.05)
    # ⚠⚠⚠ LES DEUX FAITS QUE LA FIGURE PORTE. Sans le premier, l'escalier serait un dessin sans
    # conclusion ; sans le second, on lirait « il faut mieux régler la longueur » là où la
    # mesure dit « on l'a prise sur la mauvaise population ».
    v("une meilleure longueur est la marche la plus haute",
      m["gain_dune_meilleure_longueur_um"] > m["gain_dune_rotation_globale_um"]
      and m["gain_dune_meilleure_longueur_um"] > m["gain_dune_correction_par_point_um"],
      f"{m['gain_dune_meilleure_longueur_um']} contre "
      f"{m['gain_dune_rotation_globale_um']} et {m['gain_dune_correction_par_point_um']}")
    v("... et elle suit l'écart LOCAL plutôt que le pas nominal",
      m["la_longueur_suit_lecart_local_plutot_que_le_nominal"],
      f"{m['paires_ou_la_longueur_suit_lecart_local']} paires sur "
      f"{m['paires_comparees_a_lecart_local']}")
    v("... parce que le pas nominal n'est PAS celui de cette boîte",
      not m["le_pas_nominal_est_celui_de_la_boite"],
      f"{m['distance_sans_bouger_mediane_um']} contre {m['pas_nominal_um']} µm")
    # ⚠⚠ LE NÉGATIF QUI EMPÊCHE DE LIRE « LA ROTATION EST UNE PISTE » : elle ne prend rien.
    v("la rotation globale ne prend presque rien",
      m["gain_dune_rotation_globale_um"] < 0.15 * m["e0_nominal_median_um"],
      f"{m['gain_dune_rotation_globale_um']} µm sur {m['e0_nominal_median_um']}")
    # ⚠⚠ ET LE PLANCHER, QUI DÉCIDE DU RACCROCHAGE : s'il ne tenait pas la feuille, aucune
    # lecture du volume ne sauverait le pas normal.
    v("le plancher d'un raccrochage parfait tient la feuille",
      m["le_plancher_tient_la_feuille"],
      f"{m['plancher_um']} contre {m['demi_epaisseur_um']} µm")
    v("les butées sur la fenêtre sont comptées et sorties de la médiane",
      m["paires_dont_la_longueur_bute_sur_la_fenetre"] > 0
      and m["longueur_retenue_mediane_hors_butee_um"] is not None,
      f"{m['paires_dont_la_longueur_bute_sur_la_fenetre']} sur {m['paires']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les trois marches sont dessinées", r["marches"] == 3)
        v("toutes les paires sont dessinées", r["paires"] == m["paires"])
        trop = [(t, w) for t, w in r["legendes"] if w > 400 - 12]
        v("aucune ligne de légende ne déborde de son panneau", not trop,
          str(trop) if trop else f"la plus large fait {max(w for _, w in r['legendes'])} px")
        # ⚠⚠⚠ ET LA PROSE AUSSI, ce que le contrôle de largeur ne regardait pas : elle est coupée
        # au nombre de CARACTÈRES, or une ligne en capitales est bien plus large à nombre égal.
        # Une ligne qui déborde de l'image se lit tronquée, donc faux.
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        # ⚠⚠ ET LES ÉTIQUETTES DESSINÉES SONT TRAÇABLES ELLES AUSSI : le contrôle de traçabilité
        # ne regardait que `prose`, donc un marqueur que la police ne rend pas passait — ce
        # dépôt a déjà publié une étoile sortie en carré vide.
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"][:4]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · ce que chaque classe de remedes prend, au mieux",
                      "B · la meilleure longueur suit l'ecart LOCAL, pas le nominal"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_cout_dun_seul_pas.png")
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
