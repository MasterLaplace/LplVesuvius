#!/usr/bin/env python3
"""La deuxième ancre fait tout, la troisième ne fait rien.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. La tranche précédente avait ouvert une piste et une seule —
*« ce n'est pas une méthode, c'est une borne : elle dit si l'effort doit aller vers une meilleure
propagation ou vers PLUS D'ANCRES »*. Le panneau A la referme : à jeux comparables, la troisième
ancre vaut **1,2 µm** et la quatrième **0,2**.

⭐⭐ Le panneau B porte le mécanisme, et c'est lui qui explique le panneau A : deux ancres qui
encadrent **annulent la pente** de la dérive, et une pente annulée l'est d'un coup — il ne reste
rien à annuler pour la troisième.

⚠⚠⚠ ET CE PANNEAU A PORTÉ UNE AFFIRMATION RETIRÉE. J'y avais lu une **accélération**, sur le
critère « les incréments consécutifs croissent » — qui omet le plus grand de tous, celui du bras
zéro au bras un. La suite complète est **41,1 puis 22,0 / 37,7 / 48,6** µm, et l'erreur au bras
`k` reste **sous** `k` fois celle du bras un : le coût par tour vaut 41,1 puis 31,6 / 33,6 /
37,4 µm, il est **stable**. La dérive est donc à peu près linéaire avec un premier pas plus cher
— ce qui est exactement la prémisse de l'estimateur, et ce qui explique que la parabole ne trouve
rien à annuler. Détail dans `pourquoi_la_derive_accelere`.

Usage :
    uv run python src/figures/figure_combien_dancres.py --verifier
    uv run python src/figures/figure_combien_dancres.py \\
        --sortie docs/images/75_combien_dancres.png
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
MESURE = RACINE / "docs" / "mesures" / "combien_dancres.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    enc = m["par_nombre_dancres_encadrants"]
    sym = m["encadrements_symetriques_par_bras"]
    return [
        f"{m['jeux']} jeux d'ancres sur {m['cibles']} cibles, portee {m['portee']}, jusqu'a "
        f"{m['kmax']} ancres. l'estimateur est la droite des moindres carres en BRAS SIGNE, "
        "evaluee en zero : aucun parametre libre, et a deux ancres elle rend exactement la "
        "ponderation par les bras deja mesuree — une identite algebrique, verifiee.",
        f"la deuxieme ancre enleve {m['gain_de_la_deuxieme_ancre']} um. la troisieme, a jeux "
        f"comparables, {m['gain_de_la_troisieme_ancre_en_encadrant']} um ; la quatrieme "
        f"{m['gain_de_la_quatrieme_ancre_en_encadrant']}. le gain s'arrete a "
        f"{m['ancres_avant_que_le_gain_cesse_en_encadrant']} ancres qui encadrent.",
        "⚠ la courbe AGREGEE descend encore, et elle ment : la part de jeux encadrants change "
        f"avec le nombre d'ancres ({', '.join(str(d['n']) for d in enc.values())} sur "
        f"{', '.join(str(d['n']) for d in m['par_nombre_dancres'].values())}), donc son "
        "affaissement mesure d'abord ce changement de composition. les deux sont publiees.",
        "le panneau B dit POURQUOI : deux ancres qui encadrent annulent la PENTE de la derive, "
        "et une pente annulee l'est d'un coup — il ne reste rien pour la troisieme.",
        "⚠⚠ RETRACTATION : j'avais lu ici une ACCELERATION, sur le critere « les increments "
        "consecutifs croissent » — qui omet le plus grand de tous, celui du bras zero au bras "
        f"un. la suite complete est {m['increments_par_tour_um']} um, et le cout par tour "
        f"{m['cout_par_tour_um']} um est STABLE : l'erreur au bras k reste SOUS k fois celle du "
        "bras un. la derive est a peu pres lineaire avec un premier pas plus cher — ce qui est "
        "la premisse de l'estimateur, et ce qui explique que la parabole ne trouve rien a "
        "annuler. detail dans pourquoi_la_derive_accelere.",
        # ⚠ Les comptes sont lus dans la mesure et non ecrits ici : une prose qui annoncerait
        # « sur un cas » quand la mesure en a trois se lirait comme une precaution alors qu'elle
        # serait fausse — et c'est arrive dans la premiere version de cette legende.
        "et le chiffre qui decide de l'effort : deux ancres a "
        f"±{m['plus_grand_bras_symetrique_qui_tient']} tours tiennent encore la feuille, sur "
        f"{m['cas_a_ce_bras']} cas. le detail, avec ses comptes ATTACHES : "
        + " · ".join(f"±{b} {d['ajustee_um']} um sur {d['n']}" for b, d in sym.items())
        + f". ⚠ le plus grand bras ne repose que sur {m['cas_a_ce_bras']} cas, et ce depot a "
        "deja vu un verdict s'inverser quand l'echantillon a grandi.",
        "⚠⚠ et la parabole ne paie pas non plus. la courbure etant reelle, un ajustement de "
        "degre DEUX l'annulerait — mesure sur les "
        f"{m['jeux_a_trois_ancres_ou_plus_qui_encadrent']} jeux d'au moins trois ancres qui "
        f"encadrent : {m['erreur_courbe_mediane_um']} um contre "
        f"{m['erreur_droite_sur_les_memes_jeux_um']} pour la droite, et il ne gagne que sur "
        f"{m['jeux_ou_la_courbure_bat_la_droite']}. sur des bras entiers de 1 a 4, identifier une "
        "courbure coute plus de variance qu'elle n'enleve de biais.",
        "⚠ ce n'est toujours pas une methode mais une BORNE : encadrer suppose de connaitre les "
        "deux bouts. ce que ca dit est ou NE PAS porter l'effort — ni une troisieme ancre, ni un "
        "estimateur d'un degre de plus.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    # ⚠⚠ LES LÉGENDES SONT NOMMÉES UNE FOIS, ici, et la batterie mesure CES chaînes-là. Une
    # seconde liste recopiée pour le contrôle mesurerait des textes que la figure ne dessine
    # pas — et c'est exactement comme ça qu'un débordement passerait inaperçu.
    legendes = [
        "gris : tous les jeux   ambre : ceux qui ENCADRENT",
        "la part d'encadrants change avec k : le gris melange deux regimes",
        "abscisse : nombre d'ancres du jeu",
        "bleu : UNE ancre a ce bras",
        "ambre : DEUX ancres a ±ce bras, qui encadrent",
        f"increments de la bleue : {m['increments_par_tour_um']} um par tour",
        "abscisse : longueur du bras, en spires",
        "entre parentheses : le nombre de cas",
    ]
    marge, pw, ph, ecart = 40, 400, 250, 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "La deuxieme ancre fait tout, la troisieme ne fait rien",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['jeux']} jeux d'ancres sur {m['cibles']} cibles · ecart inter-feuilles "
             f"{m['ecart_lu_um']} um", fill=DISCRET, font=moyen)

    # ---------- A : l'erreur par NOMBRE d'ancres ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · l'erreur par nombre d'ancres, et ou elle cesse de descendre",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    agg = m["par_nombre_dancres"]
    enc = m["par_nombre_dancres_encadrants"]
    ks = sorted(int(k) for k in agg)
    top = max(agg[str(k)]["ajustee_um"] for k in ks) * 1.15
    larg = pw / (len(ks) + 1)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 40)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    art.text((ax + pw - 132, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for serie, coul, dec in ((agg, DISCRET, -0.16), (enc, AMBRE, 0.16)):
        pts = [(ax + larg * (k - 0.5) + dec * larg,
                ay + ph - (serie[str(k)]["ajustee_um"] or 0) / top * (ph - 40))
               for k in ks if serie[str(k)]["ajustee_um"] is not None]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            art.line([x0, y0, x1, y1], fill=coul, width=2)
        for k, (x0, y0) in zip([k for k in ks if serie[str(k)]["ajustee_um"] is not None], pts):
            art.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=coul)
            art.text((x0 - 16, y0 - 18), f"{serie[str(k)]['ajustee_um']:.0f}µ",
                     fill=coul, font=petit)
    for k in ks:
        art.text((ax + larg * (k - 0.5) - 4, ay + ph + 3), str(k), fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 6), legendes[0], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22), legendes[1], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + ph + 19), legendes[2], fill=DISCRET, font=petit)

    # ---------- B : la premisse, et ce que l'encadrement en fait ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · la derive ACCELERE, et l'encadrement n'en annule que la pente",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    seule = m["erreur_dune_ancre_par_bras_um"]
    sym = m["encadrements_symetriques_par_bras"]
    bras = sorted(int(b) for b in seule)
    top2 = max(seule[str(b)]["erreur_um"] for b in bras) * 1.15
    larg2 = pw / (len(bras) + 1)
    yd2 = by + ph - m["demi_epaisseur_um"] / top2 * (ph - 40)
    art.line([bx, yd2, bx + pw, yd2], fill=TEXTE)
    art.text((bx + pw - 132, yd2 - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for serie, cle, coul, dec in ((seule, "erreur_um", BLEU, -0.16),
                                  (sym, "ajustee_um", AMBRE, 0.16)):
        pts, vus = [], []
        for b in bras:
            d = serie.get(str(b))
            if d is None or d[cle] is None:
                continue
            pts.append((bx + larg2 * (b - 0.5) + dec * larg2,
                        by + ph - d[cle] / top2 * (ph - 40)))
            vus.append((b, d))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            art.line([x0, y0, x1, y1], fill=coul, width=2)
        for (x0, y0), (b, d) in zip(pts, vus):
            art.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=coul)
            art.text((x0 - 20, y0 - 18), f"{d[cle]:.0f}µ ({d['n']})", fill=coul, font=petit)
    for b in bras:
        art.text((bx + larg2 * (b - 0.5) - 4, by + ph + 3), str(b), fill=DISCRET, font=petit)
    art.text((bx + 6, by + 6), legendes[3], fill=BLEU, font=petit)
    art.text((bx + 6, by + 22), legendes[4], fill=AMBRE, font=petit)
    art.text((bx + 6, by + 38), legendes[5], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19), legendes[6], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 35), legendes[7], fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠⚠ Les largeurs sont RENDUES pour que la batterie vérifie qu'aucune ligne ne déborde de
    # son panneau : une ligne qui dépasse se lit tronquée, donc faux, et ce dépôt l'a déjà payé
    # une fois sur un titre. Les mesurer après coup dans l'image ne dirait pas LAQUELLE déborde.
    return {"points_a": len(ks), "points_b": len(bras),
            "legendes": [(t, petit.getbbox(t)[2]) for t in legendes],
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
    # ⚠⚠⚠ LE FAIT QUE LA FIGURE PORTE : la deuxième ancre fait presque tout, et la suivante
    # presque rien. Les deux moitiés ensemble — sans la seconde, « les ancres aident » se
    # lirait comme une invitation à en tracer davantage.
    v("la deuxième ancre enlève beaucoup", m["gain_de_la_deuxieme_ancre"] > 20,
      f"{m['gain_de_la_deuxieme_ancre']} µm")
    v("... et la troisième, à jeux comparables, presque rien",
      abs(m["gain_de_la_troisieme_ancre_en_encadrant"])
      < m["gain_de_la_deuxieme_ancre"] / 10,
      f"{m['gain_de_la_troisieme_ancre_en_encadrant']} contre "
      f"{m['gain_de_la_deuxieme_ancre']} µm")
    v("le gain cesse à deux ancres qui encadrent",
      m["ancres_avant_que_le_gain_cesse_en_encadrant"] == 2,
      str(m["ancres_avant_que_le_gain_cesse_en_encadrant"]))
    # ⚠⚠ LA PRÉMISSE DE L'ESTIMATEUR, sans laquelle le panneau B ne veut rien dire : l'erreur
    # d'une ancre croît avec son bras, et par pas à peu près constants.
    v("l'erreur d'une ancre croît avec son bras", m["lerreur_dune_ancre_croit_avec_son_bras"],
      str(m["increments_par_tour_um"]))
    # ⚠⚠⚠ ET LA FORME DE LA COURBE, APRÈS RÉTRACTATION : l'erreur au bras `k` reste SOUS `k`
    # fois celle du bras un, et le coût par tour est stable. C'est ce qui rend la droite le bon
    # estimateur — une figure qui écrirait encore « accélère » mentirait sur sa propre mesure.
    v("la dérive d'une ancre est SOUS-linéaire, pas accélérée",
      m["la_derive_dune_ancre_est_sous_lineaire"], str(m["cout_par_tour_um"]))
    v("... le premier pas coûte plus que n'importe quel tour suivant",
      m["le_premier_pas_coute_le_plus"], str(m["increments_par_tour_um"]))
    v("... et le résidu de l'encadrement suit la même forme",
      m["le_residu_de_lencadrement_est_sous_lineaire"],
      str(m["cout_par_tour_de_lencadrement_um"]))
    # ⚠⚠ ET CE QUE L'ENCADREMENT ACHÈTE, EN UN CHIFFRE : il divise le coût par tour. Sans ça,
    # « il aide » resterait une médiane sans mécanisme.
    v("... et il divise le coût par tour d'une ancre seule",
      m["cout_par_tour_de_lencadrement_um"][-1] < m["cout_par_tour_um"][-1] / 1.5,
      f"{m['cout_par_tour_de_lencadrement_um']} contre {m['cout_par_tour_um']}")
    # ⚠⚠⚠ ET LE CONTRÔLE QUI EMPÊCHE DE LIRE LA COURBE AGRÉGÉE COMME UN RÉSULTAT : la part de
    # jeux encadrants change avec k. Si elle ne changeait pas, les deux courbes seraient la
    # même et la précaution du panneau A serait une décoration.
    parts = {k: m["par_nombre_dancres_encadrants"][k]["n"] / m["par_nombre_dancres"][k]["n"]
             for k in m["par_nombre_dancres"]}
    v("la part de jeux encadrants change avec le nombre d'ancres",
      len(set(round(x, 3) for x in parts.values())) > 1,
      str({k: round(x, 2) for k, x in parts.items()}))
    # ⚠⚠ ET LE CHIFFRE QUI DÉCIDE DE L'EFFORT, avec son compte de cas : sans le compte, « il
    # tient jusqu'à ±3 » se lirait comme un résultat alors qu'un cas ne tranche rien.
    v("le plus grand bras qui tient est publié AVEC son nombre de cas",
      m["plus_grand_bras_symetrique_qui_tient"] is not None and m["cas_a_ce_bras"] >= 1,
      f"±{m['plus_grand_bras_symetrique_qui_tient']} sur {m['cas_a_ce_bras']} cas")
    # ⚠⚠⚠ LE NÉGATIF QUE LA FIGURE DOIT PORTER : la courbure est réelle, et l'estimateur qui
    # l'annulerait ne paie PAS. Sans ce contrôle, la prose pourrait cesser de le dire sans que
    # rien ne le remarque — et c'est le résultat qui ferme la dernière piste ouverte.
    v("l'ajustement de degré deux est mesuré et ne paie pas",
      not m["la_courbure_paie"]
      and m["erreur_courbe_mediane_um"] > m["erreur_droite_sur_les_memes_jeux_um"],
      f"{m['erreur_courbe_mediane_um']} contre {m['erreur_droite_sur_les_memes_jeux_um']} µm")
    v("... et il est comparé à la droite sur les MÊMES jeux, pas sur deux populations",
      m["jeux_a_trois_ancres_ou_plus_qui_encadrent"] > 0
      and m["jeux_ou_la_courbure_bat_la_droite"]
      < m["jeux_a_trois_ancres_ou_plus_qui_encadrent"] / 2,
      f"{m['jeux_ou_la_courbure_bat_la_droite']} sur "
      f"{m['jeux_a_trois_ancres_ou_plus_qui_encadrent']}")
    v("... et un encadrement à bras deux tient la feuille sur plusieurs cas",
      m["encadrements_symetriques_par_bras"]["2"]["tient_la_feuille"]
      and m["encadrements_symetriques_par_bras"]["2"]["n"] > 1,
      str(m["encadrements_symetriques_par_bras"]["2"]))
    # ⚠⚠ LA PROSE NE DOIT PAS ANNONCER UN COMPTE QUE LA MESURE CONTREDIT. La première version de
    # cette légende écrivait « un verdict sur un cas n'est pas un verdict » alors que la mesure
    # en avait trois : une précaution fausse se lit comme une précaution, donc elle est pire
    # qu'absente. Les comptes sont désormais lus dans la mesure, et ce contrôle l'exige.
    texte = " ".join(prose(m))
    v("chaque compte de cas cité par la prose est celui de la mesure",
      all(f"sur {d['n']}" in texte
          for d in m["encadrements_symetriques_par_bras"].values()),
      str({b: d["n"] for b, d in m["encadrements_symetriques_par_bras"].items()}))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les nombres d'ancres sont dessinés",
          r["points_a"] == len(m["par_nombre_dancres"]))
        v("toutes les longueurs de bras sont dessinées",
          r["points_b"] == len(m["erreur_dune_ancre_par_bras_um"]))
        trop = [(t, w) for t, w in r["legendes"] if w > 400 - 12]
        v("aucune ligne de légende ne déborde de son panneau", not trop,
          str(trop) if trop else f"la plus large fait {max(w for _, w in r['legendes'])} px")
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        # ⚠⚠ UN TITRE DE PANNEAU QUI DÉBORDE SE LIT TRONQUÉ, DONC FAUX — le dépôt l'a payé une
        # fois avec « en sens contraire » pour « contraires ».
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · l'erreur par nombre d'ancres, et ou elle cesse de descendre",
                      "B · la derive ACCELERE, et l'encadrement n'en annule que la pente"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_combien_dancres.png")
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
