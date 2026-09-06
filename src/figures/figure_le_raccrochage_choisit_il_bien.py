#!/usr/bin/env python3
"""Le raccrochage lit mal, et c'est pourtant sa lecture qui le sauve.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le poste « point à point » vaut 19 % du coût d'un pas et sa
borne parfaite tient largement la feuille, mais le raccrochage n'en prenait presque rien. Deux
explications restaient, avec des remèdes opposés : la géométrie refuse, ou la lecture est mauvaise.

⭐⭐ Le panneau B tranche : l'accord de rang entre le décalage choisi et celui de l'oracle vaut
**0,076** — minuscule, mais positif, significatif, et le témoin du gabarit mélangé reste à
**−0,006**. La lecture voit donc quelque chose, très peu.

⚠⚠⚠ ET CE FICHIER A ÉTÉ CORRIGÉ PAR UNE MESURE POSTÉRIEURE. `le_gabarit_lu_ailleurs` a établi
que sur ces pas la dispersion d'un pas à l'autre — ne rien faire coûte de 32 à 74 µm — vaut
**quatre fois** l'écart entre deux méthodes, donc une différence de médianes s'y fait décider par
le tirage des pas. Repris en **écart apparié** (`src/commun/lecart_apparie.py`), trois des quatre
affirmations de cette figure ne tiennent plus : le gain de 5,6 µm sur l'immobilité, la nuisance
du déplacement d'ensemble, et l'avance sur le mélange. Les nombres n'étaient pas faux — ils
étaient les mauvais nombres pour la question.

⭐⭐ Ce qui TIENT est ce qui compare le raccrochage à une variante de LUI-MÊME, sur les mêmes
cellules : sa lecture par cellule bat sa propre médiane et retirer son biais d'ensemble
améliore. C'est cohérent — ces deux-là sont appariées par construction, les trois autres non.

Usage :
    uv run python src/figures/figure_le_raccrochage_choisit_il_bien.py --verifier
    uv run python src/figures/figure_le_raccrochage_choisit_il_bien.py \\
        --sortie docs/images/75_le_raccrochage_choisit_il_bien.png
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
MESURE = RACINE / "docs" / "mesures" / "le_raccrochage_choisit_il_bien.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    a_, mm = m["accord_du_raccrochage"], m["accord_du_melange"]
    ap = {k: (f"{v['ecart_median_um']:+.1f} um, {v['pas_ameliores']}/{v['pas']} pas, "
              f"intervalle {v['intervalle_um']}") for k, v in m["appariés"].items()}
    return [
        f"{m['paires']} paires, {m['cellules']} cellules. le raccrochage choisit un decalage par "
        "correlation avec un gabarit lu sur la spire de DEPART ; l'oracle choisit celui qui "
        "minimise vraiment la distance a la cible. ⚠ l'oracle est borne a la MEME fenetre, sinon "
        "la comparaison mesurerait une fenetre et non une lecture.",
        f"accord de rang avec l'oracle : raccrochage {a_['rho']} (p {a_['p']}, n {a_['n']}), "
        f"gabarit MELANGE {mm['rho']} (p {mm['p']}). la lecture voit donc quelque chose — mais "
        "0,076 de correlation, c'est un demi pour cent de variance : elle voit tres peu.",
        f"en erreur : sans bouger {m['erreur_sans_bouger_mediane_um']} um, RACCROCHE "
        f"{m['erreur_raccrochee_mediane_um']}, sa propre MEDIANE seule "
        f"{m['erreur_raccroche_constant_mediane_um']}, melange "
        f"{m['erreur_melangee_mediane_um']}, oracle {m['erreur_oracle_mediane_um']}.",
        "⚠⚠ CORRIGE PAR UNE MESURE POSTERIEURE. sur ces pas, ne rien faire coute de 32 a 74 um "
        "selon le pas : la dispersion entre pas vaut QUATRE fois l'ecart entre deux methodes, "
        "donc une difference de medianes s'y fait decider par le tirage des pas. les memes "
        "questions, reprises en ecart APPARIE pas par pas, chacune avec son intervalle a un pas "
        "de moins :",
        f"  raccroche contre ne pas bouger : {ap['raccrochage_contre_sans_bouger']} — NE "
        f"TRANCHE PAS, la ou la difference des medianes annoncait {m['gain_du_raccrochage_um']} "
        f"um de gain. son deplacement d'ensemble contre rien : "
        f"{ap['sa_mediane_contre_sans_bouger']} — NE TRANCHE PAS non plus, la ou elle annoncait "
        f"une nuisance de {m['gain_du_recentrage_seul_um']} um.",
        f"⚠⚠ ce qui TIENT est ce qui le compare a une variante de LUI-MEME, sur les memes "
        f"cellules : sa lecture par cellule bat sa propre mediane "
        f"({ap['raccrochage_contre_sa_mediane']}), et retirer son biais ameliore "
        f"({ap['centre_contre_raccrochage']}). les deux sont appariees par construction ; les "
        "trois qui tombent ne l'etaient pas.",
        f"⚠ mais son erreur ne bat PAS celle de son gabarit melange "
        f"({m['paires_ou_le_raccrochage_bat_son_melange']} paires sur {m['paires']}) : la "
        "lecture est mesurablement meilleure que le bruit dans ce qu'elle CHOISIT, pas encore "
        "dans ce qu'elle COUTE.",
        f"⚠⚠ ce que ca tranche, et c'est la SEULE affirmation que l'appariement renforce : la "
        f"geometrie ne refuse RIEN. l'avance de l'oracle vaut "
        f"{ap['oracle_contre_sans_bouger']} — sept pas sur sept, intervalle entierement "
        f"negatif. la ou tout gain du raccrochage s'evanouit des qu'on apparie, celui de sa "
        "borne ne bouge pas : c'est bien la LECTURE qui est le chantier, et il est entier.",
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
        "gris : sans bouger   ambre : RACCROCHE   bleu : sa mediane seule",
        "vert-gris : gabarit melange   rouge : oracle",
        "abscisse : les paires, par leur spire de depart",
        "ambre : accord du RACCROCHAGE avec l'oracle   gris : le melange",
        "abscisse : les paires · trait : zero, ou une lecture ne voit rien",
    ]
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Il lit mal, et seule sa lecture par cellule tient l'appariement",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['paires']} paires · {m['cellules']} cellules · rho "
             f"{m['accord_du_raccrochage']['rho']} contre "
             f"{m['accord_du_melange']['rho']} pour le melange", fill=DISCRET, font=moyen)

    lg = m["lignes"]
    # ---------- A : les cinq contendants ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · seule sa lecture PAR CELLULE tient l'appariement",
             fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    cles = (("erreur_sans_bouger_um", DISCRET), ("erreur_raccrochee_um", AMBRE),
            ("erreur_raccroche_constant_um", BLEU), ("erreur_melangee_um", (120, 140, 120)),
            ("erreur_oracle_um", ROUGE))
    top = max(e[c] for e in lg for c, _ in cles) * 1.18
    larg = pw / (len(lg) + 0.6)
    yd = ay + ph - m["demi_epaisseur_um"] / top * (ph - 46)
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    # ⚠ L'étiquette est posée à GAUCHE : à droite elle tombe sur les dernières paires, qui sont
    # les plus hautes, et un nombre par-dessus une barre ne se lit ni comme l'un ni comme l'autre.
    art.text((ax + 6, yd - 14), f"demi-feuille {m['demi_epaisseur_um']:.0f}µ",
             fill=TEXTE, font=petit)
    for i, e in enumerate(lg):
        x0 = ax + larg * (i + 0.55)
        for k, (cle, coul) in enumerate(cles):
            dec = (k - 2.0) * 0.17
            h = e[cle] / top * (ph - 46)
            art.rectangle([x0 + dec * larg - larg * 0.07, ay + ph - h,
                           x0 + dec * larg + larg * 0.07, ay + ph], fill=coul)
        art.text((x0 - 6, ay + ph + 3), str(e["de"]), fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 6), legendes[0], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + 22), legendes[1], fill=DISCRET, font=petit)
    art.text((ax + 6, ay + ph + 19), legendes[2], fill=DISCRET, font=petit)

    # ---------- B : l'accord avec l'oracle ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · ce que sa lecture voit, contre ce que le hasard voit",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    rhos = [(e["accord_du_raccrochage"]["rho"], e["accord_du_melange"]["rho"]) for e in lg]
    plats = [x for paire in rhos for x in paire if x is not None]
    haut = max(0.05, max(abs(x) for x in plats)) * 1.25
    y0 = by + ph / 2 + 10
    art.line([bx, y0, bx + pw, y0], fill=TEXTE)
    larg2 = pw / (len(lg) + 0.6)
    for i, (ra, rm) in enumerate(rhos):
        x0 = bx + larg2 * (i + 0.55)
        for dec, val, coul in ((-0.2, ra, AMBRE), (0.2, rm, DISCRET)):
            if val is None:
                continue
            # ⚠ Une barre NÉGATIVE descend sous l'axe : PIL exige que le coin haut vienne en
            # premier, donc les deux ordonnées sont triées. Sans ça, tout accord négatif — celui
            # du mélange, qui est précisément ce qu'on veut montrer — lève au lieu de se dessiner.
            h = val / haut * (ph / 2 - 24)
            art.rectangle([x0 + dec * larg2 - larg2 * 0.15, min(y0, y0 - h),
                           x0 + dec * larg2 + larg2 * 0.15, max(y0, y0 - h)], fill=coul)
        art.text((x0 - 6, by + ph + 3), str(lg[i]["de"]), fill=DISCRET, font=petit)
    art.text((bx + 6, by + 6), legendes[3], fill=DISCRET, font=petit)
    art.text((bx + 6, by + ph + 19), legendes[4], fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"paires": len(lg), "etiquettes": [str(e["de"]) for e in lg],
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
    # ⚠⚠⚠ LES DEUX MOITIÉS DU RÉSULTAT. Sans la première, on lirait « le raccrochage marche » ;
    # sans la seconde, « il ne lit rien ». Les deux sont vraies et elles ne disent pas la même
    # chose : il lit, très peu.
    v("le raccrochage lit quelque chose : son accord bat celui du mélange",
      m["le_raccrochage_lit_quelque_chose"],
      f"{m['accord_du_raccrochage']['rho']} contre {m['accord_du_melange']['rho']}")
    v("... mais très peu — la corrélation reste sous un dixième",
      abs(m["accord_du_raccrochage"]["rho"]) < 0.1,
      str(m["accord_du_raccrochage"]["rho"]))
    # ⚠⚠⚠ LA CORRECTION QUE CETTE FIGURE PORTE DÉSORMAIS, ET LES CONTRÔLES QUI L'EMPÊCHENT DE
    # SE PERDRE. Trois affirmations de la première version ne survivent pas à l'appariement ;
    # sans ces contrôles, la prose pourrait recommencer à les faire sans que rien ne le voie.
    v("le gain sur l'immobilité NE survit PAS à l'appariement",
      not m["le_gain_du_raccrochage_survit_a_lappariement"],
      str(m["appariés"]["raccrochage_contre_sans_bouger"]))
    v("... ni la nuisance de son déplacement d'ensemble",
      not m["son_deplacement_densemble_nuit_a_lappariement"],
      str(m["appariés"]["sa_mediane_contre_sans_bouger"]))
    # ⭐⭐ ET CE QUI TIENT : les deux comparaisons du raccrochage à une variante de LUI-MÊME,
    # appariées par construction. C'est ce qui garde la tranche debout plutôt qu'une retraite.
    v("sa lecture PAR CELLULE bat sa propre médiane, appariement compris",
      m["la_lecture_par_cellule_survit_a_lappariement"],
      str(m["appariés"]["raccrochage_contre_sa_mediane"]))
    v("... et retirer son biais d'ensemble améliore, appariement compris",
      m["le_retrait_du_biais_survit_a_lappariement"],
      str(m["appariés"]["centre_contre_raccrochage"]))
    # ⚠⚠ ET LE NÉGATIF QUI EMPÊCHE DE CONCLURE TROP VITE : son erreur ne bat celle de son
    # gabarit mélangé dans AUCUN des deux instruments.
    v("son erreur ne bat pas celle de son mélange, dans les deux instruments",
      not m["le_raccrochage_bat_son_melange"]
      and m["appariés"]["raccrochage_contre_melange"]["intervalle_um"][1] >= 0,
      f"{m['paires_ou_le_raccrochage_bat_son_melange']} paires sur {m['paires']} · "
      f"{m['appariés']['raccrochage_contre_melange']}")
    # ⚠⚠⚠ CE QUE LA MESURE TRANCHE : la géométrie ne refuse rien, l'oracle prend beaucoup dans
    # la même fenêtre. C'est donc la lecture qui est le chantier.
    # ⭐⭐⭐ LA SEULE AFFIRMATION DE CETTE FIGURE QUI SORT RENFORCÉE DE L'APPARIEMENT, et c'est
    # celle qui tient le chantier ouvert : l'avance de l'oracle vaut 23,8 µm sur SEPT pas sur
    # sept, intervalle entièrement négatif. Là où les gains du raccrochage disparaissent dès
    # qu'on apparie, celui de sa borne ne bouge pas.
    v("la géométrie ne refuse rien, et c'est vrai sur CHAQUE pas",
      m["la_geometrie_ne_refuse_rien_a_lappariement"]
      and m["appariés"]["oracle_contre_sans_bouger"]["pas_ameliores"] == m["paires"],
      str(m["appariés"]["oracle_contre_sans_bouger"]))
    v("... et le raccrochage n'en prend qu'une petite part",
      m["part_du_gain_de_loracle_prise"] < 0.4,
      str(m["part_du_gain_de_loracle_prise"]))
    # ⚠ L'oracle reste une borne : s'il était battu par un aveugle, quelque chose fuirait.
    v("l'oracle n'est battu par aucun contendant aveugle",
      all(e["erreur_oracle_um"] <= min(e["erreur_raccrochee_um"], e["erreur_melangee_um"],
                                       e["erreur_sans_bouger_um"],
                                       e["erreur_raccroche_constant_um"]) + 0.05
          for e in m["lignes"]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les paires sont dessinées", r["paires"] == m["paires"])
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
        for titre in ("A · seule sa lecture PAR CELLULE tient l'appariement",
                      "B · ce que sa lecture voit, contre ce que le hasard voit"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "75_le_raccrochage_choisit_il_bien.png")
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
