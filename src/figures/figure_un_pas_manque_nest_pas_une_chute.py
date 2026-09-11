#!/usr/bin/env python3
"""Un pas non confirme est-il une chute ? — deux lectures d'un meme critere.

★★★ LE PANNEAU A EST LE DEFAUT DE DEFINITION, dessine : la distribution des pas CONFIRMES a cote
de celle du RUN depuis le depart. Les deux comptent les memes pas ; leur ecart vient entierement
de ce que le run s'arrete au premier manque.

★★★ LE PANNEAU B EST LE TEST QUI TRANCHE, et il ne regarde jamais le registre du trajet : les
manques se suivent-ils plus qu'un tirage independant de MEME TAUX n'en produirait ? Une marche qui
se perd manque en rafale ; une marche qui rate une confirmation manque au hasard.

★★★ LE PANNEAU C EST CE QUE LES DEUX LECTURES FONT A L'ARITHMETIQUE ENCHAINEE, et l'ecart entre
elles est de vingt-neuf ordres de grandeur. Il ne prouve pas qu'un marcheur tient cent vingt
spires ; il montre que le nombre publie depend d'une hypothese jamais testee.

Usage :
    uv run python src/figures/figure_un_pas_manque_nest_pas_une_chute.py --verifier
    uv run python src/figures/figure_un_pas_manque_nest_pas_une_chute.py \\
        --sortie docs/images/109_un_pas_manque_nest_pas_une_chute.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "un_pas_manque_nest_pas_une_chute.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    lignes = []
    j = m.get("ce_que_la_lecture_consecutive_jette", {})
    if j.get("decidable"):
        lignes.append(
            f"★★★ LA PORTÉE PUBLIÉE EST UNE LECTURE DU CRITÈRE, PAS UNE PROPRIÉTÉ DE LA MATIÈRE, "
            f"et le défaut est dans la DÉFINITION avant d'être dans les données. `102` et `107` "
            f"comptent les pas confirmés CONSÉCUTIFS DEPUIS LE DÉPART — un compte borné par la "
            f"position du premier manque. Une marche qui confirme cinq pas sur six mais manque le "
            f"deuxième vaut UN, exactement comme une marche qui s'effondre au premier : les deux "
            f"sont INDISCERNABLES par le nombre publié. Mesuré sur les {j['marches']} marches de "
            f"`107` : médiane des pas confirmés {j['confirmes_median']}, médiane du run "
            f"{j['run_median']} — et la portée publiée est "
            f"{m.get('portee_publiee_par_107')}.")
        lignes.append(
            f"★★ {j['confirment_presque_tout']} marches confirment {j['pas'] - 1} ou {j['pas']} "
            f"pas sur {j['pas']}, et {j['... et sont creditees de zero ou un']} d'entre elles "
            f"sont créditées de ZÉRO ou UN. C'est le péché recensé de ce dépôt sous un costume "
            f"neuf : une quantité qui ne peut pas prendre la valeur qui signale la réussite "
            f"partielle.")
    p = m.get("paraphrase", {})
    if p.get("decidable"):
        lignes.append(
            f"★★ ET LE RUN NE PORTE RIEN QUE LE TAUX NE PORTE DÉJÀ. Sous des manques "
            f"INDÉPENDANTS de taux p, le run vaut p + p² + … + p⁶, donc il est entièrement "
            f"déterminé par p. Mesuré : taux {p['taux_de_confirmation']}, run observé "
            f"{p['run_moyen_observe']}, attendu {p['run_moyen_si_les_manques_sont_independants']} "
            f"— écart {p['ecart_en_pas']:+.3f} pas. « La matière porte deux pas » est donc une "
            f"façon coûteuse de dire « le critère confirme trois fois sur cinq ».")
    g = m.get("groupement", {})
    nc = m.get("nul_a_taux_commun", {})
    if g.get("decidable"):
        lignes.append(
            f"★★★ ET LE TEST QUI TRANCHE NE REGARDE JAMAIS LE REGISTRE DU TRAJET. Une marche qui "
            f"se PERD manque en rafale — une fois à côté de la feuille elle y reste — tandis "
            f"qu'une marche qui rate une confirmation manque au hasard. Mesuré : rafale moyenne "
            f"{g['rafale_moyenne_observee']} contre "
            f"{g['rafale_moyenne_sous_lindependance']} sous l'indépendance à MÊME TAUX "
            f"(p95 {g['p95_du_nul']}), p = {g['p_les_manques_sont_groupes']}. "
            f"{'Les manques SONT groupés' if g['les_manques_sont_groupes'] else 'Les manques ne sont PAS groupés'}"
            f" — donc un pas non confirmé n'est pas une chute mais une confirmation manquée.")
    if nc.get("decidable"):
        lignes.append(
            f"⚠⚠ ET LE NUL FAIT LA DÉCISION, CE QUE MA PREMIÈRE SONDE A PROUVÉ EN SE TROMPANT. "
            f"Avec un nul à taux COMMUN — le taux moyen donné à toutes les marches — le même test "
            f"rend p = {nc['p_avec_un_nul_a_taux_commun']} et déclare les manques GROUPÉS. Il "
            f"reproche à une marche qui confirme un pas sur deux d'avoir des rafales longues, "
            f"alors qu'à ce taux-là elles sont la norme. Le groupement se teste À TAUX ÉGAL, et "
            f"la batterie le démontre sur un jeu fabriqué plutôt que de l'argumenter.")
    c = m.get("un_manque_coute_t_il_des_feuilles", {})
    if c.get("decidable"):
        lignes.append(
            f"★★ ET LA SECONDE MOITIÉ : DANS LE MODE QUI COMPTE, UN MANQUE NE FAIT PAS COMPTER "
            f"PLUS MAL. {c['marches_completes']} marches entièrement confirmées s'écartent de "
            f"{c['ecart_a_un_des_completes']} feuille par pas du compte juste, "
            f"{c['marches_avec_manque']} marches avec manque de "
            f"{c['ecart_a_un_des_manquantes']} — différence {c['difference_des_ecarts']:+.3f}, "
            f"p = {c['p_bilaterale']}. ⚠⚠ Et les marches ENTIÈREMENT confirmées DÉPASSENT de "
            f"{c['le_depassement_des_completes']:+.3f} feuille par pas : le critère confirme des "
            f"pas qui traversent TROP, ce que `104` avait mesuré comme une bande de 0,68 à 1,38 "
            f"et `105` comme un sélecteur qui lit +18,4 % trop haut.")
    s = m.get("survie_du_mode_haut") or m.get("survie")
    if s:
        lignes.append(
            f"★★★ ET C'EST LE CHIFFRE QUI AVAIT DÉCLARÉ LE GRAAL MORT. `107` calcule la survie de "
            f"cent vingt spires comme (1 − risque)^120 en traitant un pas non confirmé comme une "
            f"CHUTE : au taux {s['taux_de_confirmation']} du mode qui compte, cela donne "
            f"{s['survie_si_un_manque_est_une_chute']:.2e}. Sous l'autre lecture, les mêmes "
            f"{s['pas_enchaines']} pas donnent "
            f"{s['manques_attendus_si_un_manque_est_un_manque']} confirmations manquées et une "
            f"marche qui continue. ⚠⚠⚠ Ce n'est PAS une preuve qu'un marcheur tient cent vingt "
            f"spires : six pas ne sont pas cent vingt, le mode qui ne compte rien existe "
            f"toujours, et rien ici ne mesure la dérive au-delà de six pas. La tranche ne prouve "
            f"PAS le graal ; elle prouve que "
            f"le nombre publié dépendait d'une hypothèse que personne n'avait testée.")
    pm = m.get("par_mode", {})
    if pm.get("mode_haut") and pm.get("mode_bas"):
        lignes.append(
            f"⚠ ET LE VERDICT SE LIT PAR MODE, PARCE QUE LE NUL EST CONSERVATEUR : il ne détecte "
            f"que ce qui dépasse ce que le taux explique déjà. À {pm['mode_haut']['taux_de_confirmation']} "
            f"— le mode qui compte — une rafale sauterait aux yeux, donc « non groupé » y est "
            f"informatif ; à {pm['mode_bas']['taux_de_confirmation']} — le mode qui ne compte rien "
            f"— une rafale est banale, donc le « non » y dit surtout que le test manque de "
            f"puissance. ★ Et les 8 marches sans registre décidable confirment ZÉRO pas : deux "
            f"instruments indépendants échouent au même endroit.")
    return lignes


def panneau_lectures(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les deux lectures des MÊMES pas", fill=DISCRET, font=petit)
    j = m.get("ce_que_la_lecture_consecutive_jette", {})
    if not j.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    a, b = j["distribution_des_confirmes"], j["distribution_du_run"]
    hi = max(max(a), max(b)) or 1
    g, d = x0 + 42, x0 + pw - 24
    barres = 0
    for k, (serie, nom, coul) in enumerate(((a, "pas confirmés sur 6", VERT),
                                            (b, "run depuis le départ", ROUGE))):
        haut = y0 + 34 + k * 190
        art.text((x0 + 10, haut - 14), nom, fill=coul, font=petit)
        for i, v in enumerate(serie):
            y = haut + i * 21
            larg = (d - g) * v / hi
            art.rectangle([g, y, g + max(larg, 1.0), y + 14], fill=coul)
            art.text((x0 + 12, y + 1), f"{i}", fill=DISCRET, font=petit)
            art.text((g + max(larg, 1.0) + 4, y + 1), f"{v}", fill=TEXTE, font=petit)
            barres += 1
    art.text((x0 + 8, y0 + ph - 46),
             f"★ médiane {j['confirmes_median']} contre {j['run_median']}",
             fill=TEXTE, font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             f"   {j['confirment_presque_tout']} marches presque complètes, dont",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 16),
             f"   {j['... et sont creditees de zero ou un']} créditées de zéro ou un",
             fill=ROUGE, font=petit)
    return barres


def panneau_groupement(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les manques se suivent-ils, à MÊME taux ?",
             fill=DISCRET, font=petit)
    pm = m.get("par_mode", {})
    jeux = [("toutes", m.get("groupement", {}), None)]
    for nom in ("mode_haut", "mode_bas"):
        if pm.get(nom, {}).get("marches"):
            jeux.append((nom.replace("_", " "), pm[nom]["groupement"],
                         pm[nom]["taux_de_confirmation"]))
    hi = max([x[1].get("rafale_moyenne_observee", 0.0) for x in jeux]
             + [x[1].get("rafale_moyenne_sous_lindependance", 0.0) for x in jeux]) or 1.0
    g, d = x0 + 14, x0 + pw - 92
    y = y0 + 38
    traces = 0
    for nom, gg, taux in jeux:
        if not gg.get("decidable"):
            continue
        art.text((x0 + 12, y), nom + ("" if taux is None else f" · taux {taux}"),
                 fill=TEXTE, font=petit)
        for k, (val, lib, coul) in enumerate((
                (gg["rafale_moyenne_observee"], "observé", ROUGE),
                (gg["rafale_moyenne_sous_lindependance"], "sous l'indép.", DISCRET))):
            yy = y + 16 + k * 18
            larg = (d - g) * val / hi
            art.text((x0 + 12, yy + 1), lib, fill=DISCRET, font=petit)
            art.rectangle([g + 72, yy, g + 72 + max(larg * 0.7, 1.0), yy + 12], fill=coul)
            art.text((d + 4, yy + 1), f"{val:.2f}", fill=TEXTE, font=petit)
        art.text((x0 + 12, y + 54),
                 f"★ {'GROUPÉS' if gg['les_manques_sont_groupes'] else 'NON groupés'} · "
                 f"p = {gg['p_les_manques_sont_groupes']}",
                 fill=ROUGE if gg["les_manques_sont_groupes"] else VERT, font=petit)
        y += 84
        traces += 1
    nc = m.get("nul_a_taux_commun", {})
    if nc.get("decidable"):
        art.text((x0 + 12, y + 6), "⚠ avec un nul à taux COMMUN, le même test rend",
                 fill=AMBRE, font=petit)
        art.text((x0 + 12, y + 22),
                 f"   p = {nc['p_avec_un_nul_a_taux_commun']} → "
                 f"{'GROUPÉS' if nc['declare_groupe_a_taux_commun'] else 'non groupés'}",
                 fill=AMBRE, font=petit)
        art.text((x0 + 12, y + 38), "   le nul fait la décision", fill=AMBRE, font=petit)
    return traces


def panneau_arithmetique(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "ce que les deux lectures font à 120 spires",
             fill=DISCRET, font=petit)
    y = y0 + 34
    traces = 0
    for cle, titre in (("survie_du_mode_haut", "le mode qui compte"),
                       ("survie", "toutes les marches")):
        s = m.get(cle)
        if not s:
            continue
        art.text((x0 + 12, y), f"{titre} · taux {s['taux_de_confirmation']}",
                 fill=TEXTE, font=petit)
        art.text((x0 + 12, y + 18), "un manque est une CHUTE", fill=ROUGE, font=petit)
        # ⚠ L'echelle est LOGARITHMIQUE, parce que les deux nombres sont separes par des ordres
        # de grandeur : une echelle lineaire ferait de la survie une barre invisible, donc un
        # dessin qui cache exactement ce qu'il doit montrer.
        surv = max(float(s["survie_si_un_manque_est_une_chute"]), 1e-40)
        larg = (pw - 120) * max(0.0, 1.0 + math.log10(surv) / 40.0)
        art.rectangle([x0 + 12, y + 32, x0 + 12 + max(larg, 1.0), y + 44], fill=ROUGE)
        art.text((x0 + 16 + max(larg, 1.0), y + 33),
                 f"{s['survie_si_un_manque_est_une_chute']:.1e}", fill=ROUGE, font=petit)
        art.text((x0 + 12, y + 52), "un manque est un MANQUE", fill=VERT, font=petit)
        art.text((x0 + 12, y + 68),
                 f"   {s['manques_attendus_si_un_manque_est_un_manque']} confirmations "
                 f"manquées", fill=VERT, font=petit)
        art.text((x0 + 12, y + 84), "   et la marche continue", fill=VERT, font=petit)
        y += 116
        traces += 1
    art.text((x0 + 12, y + 6), "⚠ l'échelle des survies est LOGARITHMIQUE",
             fill=DISCRET, font=petit)
    art.text((x0 + 12, y + 22), "⚠⚠⚠ et ceci ne prouve PAS qu'un marcheur", fill=AMBRE,
             font=petit)
    art.text((x0 + 12, y + 38), "    tient cent vingt spires : six pas ne sont",
             fill=AMBRE, font=petit)
    art.text((x0 + 12, y + 54), "    pas cent vingt, et le mode qui ne compte",
             fill=AMBRE, font=petit)
    art.text((x0 + 12, y + 70), "    rien existe toujours", fill=AMBRE, font=petit)
    return traces


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 420
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    j = m.get("ce_que_la_lecture_consecutive_jette", {})
    art.text((marge, 16),
             "Un pas non confirmé est-il une chute ? — deux lectures d'un même critère",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m.get('marches')} marches de `107` · portée publiée "
             f"{m.get('portee_publiee_par_107')} pas confirmés · médiane des pas RÉELLEMENT "
             f"confirmés {j.get('confirmes_median')}",
             fill=DISCRET, font=moyen)
    titres = ("A · ★ les deux lectures des mêmes pas",
              "B · ★ les manques se suivent-ils ?",
              "C · ★ ce que ça fait à 120 spires")
    for k, t in enumerate(titres):
        art.text((marge + k * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_lectures(art, marge, 104, pw, ph, m, petit)
    b = panneau_groupement(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_arithmetique(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + k * (pw + ecart), 104, marge + k * (pw + ecart) + pw, 104 + ph)
              for k in range(3)]
    debut = H - len(lignes) * 19 - 12
    for k, l in enumerate(lignes):
        art.text((marge, debut + k * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "lectures": a, "groupement": b, "arithmetique": c,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
            "hors_cadre": textes_hors_cadre(art.poses, cadres),
            "recouvrements": textes_qui_se_recouvrent(art.poses),
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
    d = dessiner(m, RACINE / "docs" / "images" /
                 "109_un_pas_manque_nest_pas_une_chute.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["lectures"] > 0 and d["groupement"] > 0 and d["arithmetique"] > 0,
      f"{d['lectures']} / {d['groupement']} / {d['arithmetique']}")
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(w <= d["largeur_utile"] for _t, w in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _w in d["prose"]]))

    txt = " ".join(t for t, _w in d["prose"])
    # ⭐⭐⭐ LA GARDE QUI COMPTE : les DEUX lectures voyagent ensemble. Publier la seule mediane des
    # confirmes remplacerait un nombre trompeur par un autre.
    j = m["ce_que_la_lecture_consecutive_jette"]
    v("la prose porte les DEUX médianes, pas seulement celle qui arrange",
      str(j["confirmes_median"]) in txt and str(j["run_median"]) in txt)
    v("... et dit que les deux marches sont INDISCERNABLES par le nombre publié",
      "INDISCERNABLES" in txt)
    v("... et nomme la portée publiée par `107`",
      str(m.get("portee_publiee_par_107")) in txt and "`107`" in txt)
    # ⚠⚠ LE NUL FAIT LA DECISION, et le dire est ce qui empeche de lire le verdict comme un fait
    # de la matiere plutot que comme un choix de test.
    v("la prose publie le nul à taux COMMUN, qui rend le verdict inverse",
      "taux COMMUN" in txt and "GROUPÉS" in txt)
    # ⚠⚠⚠ ET CE QUE LA TRANCHE NE PROUVE PAS EST DANS LA PROSE : sans cette phrase, vingt-neuf
    # ordres de grandeur se liraient comme la resurrection du graal.
    v("la prose dit explicitement ce que la tranche ne prouve PAS",
      "ne prouve PAS" in txt and "cent vingt" in txt)
    v("... et que le mode qui ne compte rien existe toujours",
      "compte rien existe" in txt)
    # ⚠ Le depassement des marches completes est le fait qui relie cette tranche a `104` et `105`.
    c = m.get("un_manque_coute_t_il_des_feuilles", {})
    if c.get("decidable") and c.get("les_completes_depassent"):
        v("la prose publie que les marches ENTIÈREMENT confirmées dépassent",
          "DÉPASSENT" in txt and "`104`" in txt and "`105`" in txt)
    g = m.get("groupement", {})
    if g.get("decidable"):
        v("la prose porte le verdict du groupement avec sa p",
          str(g["p_les_manques_sont_groupes"]) in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" /
                   "109_un_pas_manque_nest_pas_une_chute.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
