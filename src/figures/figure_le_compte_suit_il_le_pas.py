#!/usr/bin/env python3
"""Le compte suit-il le pas ? — la derive lue sur les prefixes du trajet.

★★★ LE PANNEAU A EST LA COURBE DE DERIVE, avec l'empilement FABRIQUE trace par-dessus : sans lui,
un ecart a un pourrait etre celui de l'estimateur plutot que celui de la matiere. Le score median
est annote a chaque longueur, parce qu'il signale un prefixe a ne pas croire — et il n'est jamais
utilise comme filtre, `108` ayant mesure qu'il separe a l'envers.

★★★ LE PANNEAU B EST LA QUESTION QUI DECIDE DU GRAAL : l'ecart grandit-il comme `n` (BIAIS) ou sa
dispersion comme `√n` (JITTER) ? Les deux se lisent separement — la MOYENNE dit le biais, l'ECART-
TYPE dit le jitter — et les deux ajustements passent par l'origine.

★★★ LE PANNEAU C EST LA CONSEQUENCE ENCHAINEE. A ampleur egale par pas, un biais coute `n` et un
jitter `√n` : sur cent vingt pas le rapport vaut exactement 10,95. Ce ne sont pas deux degres du
meme probleme, ce sont deux mondes.

Usage :
    uv run python src/figures/figure_le_compte_suit_il_le_pas.py --verifier
    uv run python src/figures/figure_le_compte_suit_il_le_pas.py \\
        --sortie docs/images/110_le_compte_suit_il_le_pas.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_compte_suit_il_le_pas.json"

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
    lignes.append(
        f"★★★ LA RE-DÉRIVATION DU DÉPART EST VÉRIFIÉE SUR CHAQUE MARCHE, et c'est ce qui autorise "
        f"tout le reste. `107` a gardé les étapes mais PAS leur ancre — la leçon de `102` qui se "
        f"rejoue — donc la polyligne n'existait qu'à une translation près. Elle est re-dérivable "
        f"parce que l'échantillonnage des cellules est déterministe (graine "
        f"{m.get('graine_de_107')}), et la vérification ne coûte rien : le préfixe COMPLET est le "
        f"trajet que `107` a publié. Mesuré : {m.get('marches_verifiees')}/"
        f"{m.get('marches_lues')} marches reproduisent le nombre publié, écart max "
        f"{m.get('ecart_max_de_verification')} feuille. ⚠ Une marche qui ne le reproduirait pas "
        f"serait une polyligne jamais marchée, et elle est écartée des courbes plutôt que "
        f"publiée.")
    cf = m.get("controle_fabrique", {})
    if cf:
        lignes.append(
            f"⚠⚠⚠ ET LE CONTRÔLE FABRIQUÉ EST OBLIGATOIRE, PAS DÉCORATIF. Un préfixe court est lu "
            f"par un estimateur dont `98` a mesuré qu'il ne garde rien sous sa fenêtre : si le "
            f"registre ne retrouvait pas un compte CONNU à deux pas, la courbe de dérive "
            f"commencerait par un artefact. Mesuré sur un empilement droit, avec et sans bruit : "
            f"écart max {cf.get('ecart_max_sur_fabrique')} feuille à toute longueur. "
            f"{'Le registre des préfixes est fidèle' if cf.get('le_registre_des_prefixes_est_fidele') else 'Le registre des préfixes N EST PAS fidèle'}.")
    s = m.get("le_compte_suit_il_le_pas", {})
    pm = m.get("par_mode", {})
    if s.get("decidable"):
        a, b = s["par_longueur"][0], s["par_longueur"][-1]
        lignes.append(
            f"⚠⚠⚠ SUR L'ENSEMBLE DES MARCHES, LE COMPTE S'EFFONDRE AVEC LA LONGUEUR — et ce serait "
            f"la fausse conclusion de cette tranche. À {a['pas']} pas la médiane vaut "
            f"{a['feuilles_par_pas_median']} feuille par pas, à {b['pas']} pas "
            f"{b['feuilles_par_pas_median']}, soit {s['derive_du_taux']:+.3f}. Lu ainsi, le biais "
            f"vaut {m['biais_ou_jitter']['spires_derivees_a_120_pas_si_biais']:+.2f} spires sur "
            f"cent vingt.")
    if pm.get("mode_haut", {}).get("marches") and pm.get("mode_bas", {}).get("marches"):
        h, bs = pm["mode_haut"], pm["mode_bas"]
        lignes.append(
            f"★★★ ET LA MÉDIANE DE L'ENSEMBLE DIT L'INVERSE DE CHAQUE MODE. Séparés : le mode qui "
            f"COMPTE ne dérive pas ({h['au_plus_court']} à deux pas, {h['au_plus_long']} à six, "
            f"soit {h['derive']:+.3f}, et seulement {h['marches_dont_le_taux_baisse']} de ses "
            f"{h['marches']} marches baissent) tandis que le mode qui ne compte RIEN tombe d'une "
            f"falaise ({bs['au_plus_court']} puis {bs['au_plus_long']}, soit {bs['derive']:+.3f}, "
            f"et {bs['marches_dont_le_taux_baisse']} de ses {bs['marches']} baissent). "
            f"⚠⚠⚠ Le biais de l'ensemble est donc celui d'un MÉLANGE dont les proportions changent "
            f"avec la longueur — la faute de `107` sous un costume neuf.")
        lignes.append(
            f"★★★ ET LES DEUX POPULATIONS DE `107` N'EXISTENT PAS À DEUX PAS. L'écart entre les "
            f"modes vaut {pm['ecart_au_plus_court']:+.3f} feuille par pas au plus court et "
            f"{pm['ecart_au_plus_long']:+.3f} au plus long : les deux lisent EXACTEMENT UNE "
            f"feuille par pas sur deux pas. La bimodalité que `107` a mesurée sur six pas naît "
            f"donc entre le deuxième et le troisième, elle n'est pas là au départ.")
    fa = m.get("la_falaise_est_elle_celle_de_linstrument", {})
    if fa:
        lignes.append(
            f"★★★ ET UNE DÉRIVE SEULE REPRODUIT LA FALAISE, SUR UNE PÉRIODICITÉ INTACTE — "
            f"{'OUI' if fa.get('une_derive_seule_reproduit_la_falaise') else 'NON'}, "
            f"{fa.get('falaises')} cas sur {fa.get('cas_essayes')}, valeur effondrée médiane "
            f"{fa.get('valeur_effondree_mediane')} contre {pm.get('mode_bas', {}).get('au_plus_long')} "
            f"observé. Le mécanisme est le plancher de fréquence de l'estimateur : une composante "
            f"de basse fréquence n'est EXPRIMABLE qu'une fois la fenêtre assez longue pour en "
            f"contenir un tiers de période, et dès qu'elle l'est, si elle est plus forte que la "
            f"périodicité, elle gagne l'argmax. ⚠⚠⚠ Ce contrôle n'établit PAS "
            f"{fa.get('ce_que_ce_controle_netablit_pas')} — mais lire la falaise comme un fait de "
            f"la matière sans l'avoir regardé aurait été gratuit.")
        lignes.append(
            f"⚠⚠⚠ LE SCORE EST PUBLIÉ À CÔTÉ DE CHAQUE LONGUEUR ET N'EST JAMAIS UTILISÉ COMME "
            f"FILTRE, ce qui est une décision plutôt qu'un oubli. `98` a montré qu'au-delà de sa "
            f"fenêtre l'estimateur rend un maximum parasite au score effondré — donc un score bas "
            f"signale un préfixe à ne pas croire. Mais `108` a mesuré que le score du TRAJET est "
            f"PLUS HAUT pour les marches qui ne comptent rien : filtrer dessus écarterait "
            f"préférentiellement les bonnes. Il se lit, il ne trie pas.")
    b = m.get("biais_ou_jitter", {})
    if b.get("decidable"):
        lignes.append(
            f"⚠ BIAIS OU JITTER, LA QUESTION QUI DÉCIDE DU GRAAL — ET ELLE RESTE OUVERTE. Un biais coûte `n` : "
            f"cent vingt pas à un pour cent de trop font plus d'une spire d'erreur, et rien ne la "
            f"signale. Un jitter de moyenne nulle coûte `√n`. Mesuré sur l'ensemble des marches — "
            f"la MOYENNE de l'écart dit le biais, son ÉCART-TYPE dit le jitter : biais "
            f"{b['biais_par_pas']:+.4f} feuille par pas, jitter {b['jitter_par_racine_de_pas']:.4f} "
            f"par racine de pas. Enchaînés sur cent vingt pas : "
            f"{b['spires_derivees_a_120_pas_si_biais']:+.2f} spires contre "
            f"{b['spires_derivees_a_120_pas_si_jitter']:.2f}. "
            f"{'LE BIAIS DOMINE' if b['le_biais_domine'] else 'LE JITTER DOMINE'}.")
        lignes.append(
            f"⚠⚠ ET CE N'EST PAS UN TEST, C'EST UNE DESCRIPTION. Les préfixes d'une même marche "
            f"sont EMBOÎTÉS, donc corrélés : les cinq points d'une marche ne sont pas cinq "
            f"mesures. Trancher demanderait des marches indépendantes à chaque longueur, "
            f"c'est-à-dire une course en profondeur — et le plafond de six pas de `107` est "
            f"exactement ce qui empêche de la poser ici.")
    lignes.append(
        "⚠ CE QUE CETTE TRANCHE NE DIT PAS : six pas ne sont pas cent vingt, et la courbe "
        "s'arrête où le plafond de `107` s'arrête. Elle ne dit pas non plus ce que la quantité "
        "mesurée SIGNIFIE — `106` reste debout, la périodicité que ce pas suit n'est pas "
        "l'espacement d'un empilement localement parallèle.")
    return lignes


def _cadre(art, x0, y0, pw, ph, titre, petit):
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), titre, fill=DISCRET, font=petit)


def panneau_derive(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "feuilles par pas — l'ensemble, puis chaque mode", petit)
    s = m.get("le_compte_suit_il_le_pas", {})
    if not s.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    pm = m.get("par_mode", {})
    series = [("l'ensemble (MÉLANGE)", s["par_longueur"], AMBRE)]
    for nom, coul, lib in (("mode_haut", VERT, "le mode qui compte"),
                           ("mode_bas", ROUGE, "le mode qui ne compte rien")):
        if pm.get(nom, {}).get("marches"):
            series.append((lib, pm[nom]["par_longueur"], coul))
    g, d = x0 + 46, x0 + pw - 66
    haut, bas = y0 + 58, y0 + ph - 128
    hi = max([y["feuilles_par_pas_median"] for _n, lg, _c in series for y in lg] + [1.0]) * 1.15
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # ⚠ La ligne de reference est UN, le compte juste — sans elle un nuage de points ne dit pas
    # de quel cote il se trompe.
    yun = bas - (bas - haut) * (1.0 / hi)
    art.line([g, yun, d, yun], fill=DISCRET)
    art.text((d + 3, yun - 6), "1,0", fill=DISCRET, font=petit)
    pts = 0
    for j, (nom, lig, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 20 + j * 12), nom, fill=coul, font=petit)
        n = len(lig)
        prec = None
        for i, x in enumerate(lig):
            xx = g + (d - g) * i / max(n - 1, 1)
            yy = bas - (bas - haut) * (x["feuilles_par_pas_median"] / hi)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 4, bas + 4), f"{x['pas']}", fill=DISCRET, font=petit)
            pts += 1
    art.text((x0 + 8, bas + 22), "longueur du préfixe, en pas", fill=DISCRET, font=petit)
    if pm.get("ecart_au_plus_court") is not None:
        art.text((x0 + 8, bas + 42),
                 f"★★★ les deux modes COÏNCIDENT au plus court", fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 58),
                 f"    écart {pm['ecart_au_plus_court']:+.3f} à deux pas, "
                 f"{pm['ecart_au_plus_long']:+.3f} à six", fill=TEXTE, font=petit)
        art.text((x0 + 8, bas + 78),
                 f"    donc la bimodalité NAÎT entre 2 et 3", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 100), "score médian par longueur (lu, jamais filtrant) :",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 114),
             "  " + "  ".join(f"{x['pas']}→{x['score_median']:.2f}"
                              for x in s["par_longueur"]),
             fill=DISCRET, font=petit)
    return pts


def panneau_instrument(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "une DÉRIVE seule, sur une périodicité INTACTE", petit)
    fa = m.get("la_falaise_est_elle_celle_de_linstrument", {})
    cas = [x for x in fa.get("cas", []) if x.get("correct_au_plus_court")
           and x.get("effondre_ensuite")]
    if not cas:
        cas = fa.get("cas", [])[:3]
    if not cas:
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    pm = m.get("par_mode", {})
    obs = (pm.get("mode_bas") or {}).get("par_longueur")
    g, d = x0 + 46, x0 + pw - 66
    haut, bas = y0 + 58, y0 + ph - 140
    hi = 1.25
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    yun = bas - (bas - haut) * (1.0 / hi)
    art.line([g, yun, d, yun], fill=DISCRET)
    art.text((d + 3, yun - 6), "1,0", fill=DISCRET, font=petit)
    traces = 0
    series = [(f"fabriqué · λ={x['longueur_donde_en_pas']:.0f} pas, "
               f"×{x['amplitude_de_la_derive']:.1f}",
               [{"pas": y["pas"], "v": y["feuilles_par_pas"]} for y in x["par_longueur"]],
               BLEU) for x in cas[:3]]
    if obs:
        series.append(("OBSERVÉ · le mode qui ne compte rien",
                       [{"pas": y["pas"], "v": y["feuilles_par_pas_median"]} for y in obs],
                       ROUGE))
    for j, (nom, lig, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 20 + j * 12), nom, fill=coul, font=petit)
        n = len(lig)
        prec = None
        for i, x in enumerate(lig):
            xx = g + (d - g) * i / max(n - 1, 1)
            yy = bas - (bas - haut) * (min(x["v"], hi) / hi)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 4, bas + 4), f"{x['pas']}", fill=DISCRET, font=petit)
            traces += 1
    art.text((x0 + 8, bas + 22), "longueur du préfixe, en pas", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 44),
             f"★★★ {'une dérive SEULE reproduit la falaise' if fa.get('une_derive_seule_reproduit_la_falaise') else 'aucune dérive ne la reproduit'}",
             fill=ROUGE if fa.get("une_derive_seule_reproduit_la_falaise") else VERT, font=petit)
    art.text((x0 + 8, bas + 60),
             f"    {fa.get('falaises')} cas sur {fa.get('cas_essayes')} · effondré à "
             f"{fa.get('valeur_effondree_mediane')} contre "
             f"{(pm.get('mode_bas') or {}).get('au_plus_long')} observé",
             fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 82), "⚠ le mécanisme : plancher de fréquence 0,35 —", fill=AMBRE,
             font=petit)
    art.text((x0 + 8, bas + 96), "   une basse fréquence n'est exprimable qu'une", fill=AMBRE,
             font=petit)
    art.text((x0 + 8, bas + 110), "   fois la fenêtre assez longue, et alors elle", fill=AMBRE,
             font=petit)
    art.text((x0 + 8, bas + 124), "   gagne l'argmax si elle est plus forte", fill=AMBRE,
             font=petit)
    return traces


def panneau_biais(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "l'écart au compte de pas : moyenne et dispersion", petit)
    b = m.get("biais_ou_jitter", {})
    if not b.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    lig = b["par_longueur"]
    g, d = x0 + 46, x0 + pw - 96
    haut, bas = y0 + 40, y0 + ph - 130
    vals = ([x["ecart_moyen"] for x in lig] + [x["ecart_type"] for x in lig] + [0.0])
    lo, hi = min(vals), max(vals)
    etendue = max(hi - lo, 1e-6)
    yzero = bas - (bas - haut) * ((0.0 - lo) / etendue)
    art.line([g, yzero, d, yzero], fill=CADRE)
    art.text((d + 4, yzero - 6), "0", fill=DISCRET, font=petit)
    n = len(lig)
    pts = 0
    for k, (cle, coul, nom) in enumerate((("ecart_moyen", ROUGE, "moyenne → BIAIS"),
                                          ("ecart_type", BLEU, "écart-type → JITTER"))):
        art.text((x0 + 10, y0 + 22 + k * 14), nom, fill=coul, font=petit)
        for i, x in enumerate(lig):
            xx = g + (d - g) * i / max(n - 1, 1)
            yy = bas - (bas - haut) * ((x[cle] - lo) / etendue)
            art.rectangle([xx - 3, yy - 3, xx + 3, yy + 3], fill=coul)
            if k == 0:
                art.text((xx - 4, bas + 4), f"{x['pas']}", fill=DISCRET, font=petit)
            pts += 1
    art.text((x0 + 8, bas + 22), "longueur du préfixe, en pas", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 44), f"biais {b['biais_par_pas']:+.4f} feuille par pas",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 60), f"jitter {b['jitter_par_racine_de_pas']:.4f} / √pas",
             fill=BLEU, font=petit)
    art.text((x0 + 8, bas + 82),
             f"⚠ sur le MÉLANGE : "
             f"{'le biais domine' if b['le_biais_domine'] else 'le jitter domine'}",
             fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 102), "⚠ préfixes EMBOÎTÉS, donc corrélés :", fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 118), "   ceci décrit, ne teste pas", fill=AMBRE, font=petit)
    return pts


def panneau_enchaine(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "enchaîné sur cent vingt pas", petit)
    b = m.get("biais_ou_jitter", {})
    if not b.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    paires = ((abs(b["spires_derivees_a_120_pas_si_biais"]), ROUGE,
               "si c'est un BIAIS · coûte n",
               f"{b['spires_derivees_a_120_pas_si_biais']:+.2f} spires"),
              (abs(b["spires_derivees_a_120_pas_si_jitter"]), BLEU,
               "si c'est un JITTER · coûte √n",
               f"{b['spires_derivees_a_120_pas_si_jitter']:.2f} spires"))
    hi = max(x[0] for x in paires) or 1.0
    g, d = x0 + 14, x0 + pw - 110
    y = y0 + 44
    traces = 0
    for val, coul, nom, lib in paires:
        art.text((x0 + 12, y), nom, fill=coul, font=petit)
        larg = (d - g) * val / hi
        art.rectangle([g, y + 16, g + max(larg, 1.0), y + 30], fill=coul)
        art.text((g + max(larg, 1.0) + 5, y + 17), lib, fill=TEXTE, font=petit)
        y += 60
        traces += 1
    art.text((x0 + 12, y + 6), "⚠ à ampleur ÉGALE par pas, le rapport", fill=DISCRET,
             font=petit)
    art.text((x0 + 12, y + 22), "   des deux vaut exactement √120 = 10,95", fill=DISCRET,
             font=petit)
    art.text((x0 + 12, y + 44), "⚠⚠ ce ne sont pas deux degrés du même", fill=AMBRE, font=petit)
    art.text((x0 + 12, y + 60), "    problème, ce sont deux mondes", fill=AMBRE, font=petit)
    art.text((x0 + 12, y + 84), f"vérification du départ :", fill=DISCRET, font=petit)
    art.text((x0 + 12, y + 100),
             f"   {m.get('marches_verifiees')}/{m.get('marches_lues')} marches, écart max "
             f"{m.get('ecart_max_de_verification')}",
             fill=VERT if m.get("la_rederivation_du_depart_est_verifiee") else ROUGE,
             font=petit)
    art.text((x0 + 12, y + 120),
             f"{m.get('lectures')} lectures · {m.get('secondes')} s",
             fill=DISCRET, font=petit)
    return traces


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 430
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    b = m.get("biais_ou_jitter", {})
    art.text((marge, 16),
             "Le compte suit-il le pas ? — la dérive lue sur les préfixes du trajet",
             fill=TEXTE, font=gros)
    pmm = m.get("par_mode", {})
    art.text((marge, 40),
             f"{m.get('marches_lues')} marches de `107` relues en {m.get('lectures')} lectures · "
             f"départ RE-DÉRIVÉ et vérifié sur {m.get('marches_verifiees')} · "
             + ("les deux populations naissent après le plus court"
                if pmm.get("les_deux_populations_naissent_apres_le_plus_court")
                else "les deux populations existent dès le plus court"),
             fill=DISCRET, font=moyen)
    titres = ("A · ★ le taux, par mode",
              "B · ★ la falaise, fabriquée",
              "C · ⚠ biais contre jitter")
    for k, t in enumerate(titres):
        art.text((marge + k * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_derive(art, marge, 104, pw, ph, m, petit)
    bb = panneau_instrument(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_biais(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + k * (pw + ecart), 104, marge + k * (pw + ecart) + pw, 104 + ph)
              for k in range(3)]
    debut = H - len(lignes) * 19 - 12
    for k, l in enumerate(lignes):
        art.text((marge, debut + k * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "derive": a, "instrument": bb, "biais": c,
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
    d = dessiner(m, RACINE / "docs" / "images" / "110_le_compte_suit_il_le_pas.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["derive"] > 0 and d["instrument"] > 0 and d["biais"] > 0,
      f"{d['derive']} / {d['instrument']} / {d['biais']}")
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(w <= d["largeur_utile"] for _t, w in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _w in d["prose"]]))

    txt = " ".join(t for t, _w in d["prose"])
    # ⭐⭐⭐ LA GARDE QUI COMPTE : la verification du depart voyage avec le resultat, parce que sans
    # elle la tranche mesure peut-etre un trajet qui n'a jamais ete marche.
    v("la prose porte la vérification du départ re-dérivé",
      f"{m.get('marches_verifiees')}/{m.get('marches_lues')}" in txt
      and "RE-DÉRIVATION" in txt.upper())
    # ⚠ La comparaison est insensible a la casse : la prose ecrit « CONTRÔLE FABRIQUÉ » en
    # capitales, et une garde qui cherchait la minuscule echouait sur une prose correcte.
    v("... et le contrôle fabriqué, qui autorise à lire les préfixes courts",
      "fabriqué" in txt.lower()
      and str(m["controle_fabrique"]["ecart_max_sur_fabrique"]) in txt)
    # ⚠⚠ LE SCORE EST PUBLIE ET NON FILTRANT, et le DIRE est ce qui empeche de croire qu'un tri
    # aurait ete plus propre.
    v("la prose dit que le score se lit et ne trie pas",
      "ne trie pas" in txt and "`108`" in txt)
    b = m.get("biais_ou_jitter", {})
    if b.get("decidable"):
        v("la prose porte les DEUX conséquences enchaînées, pas seulement celle qui domine",
          f"{b['spires_derivees_a_120_pas_si_biais']:+.2f}" in txt
          and f"{b['spires_derivees_a_120_pas_si_jitter']:.2f}" in txt)
        v("... et dit que les préfixes emboîtés décrivent sans tester",
          "EMBOÎTÉS" in txt and "PAS UN TEST" in txt)
    pm = m.get("par_mode", {})
    if pm.get("les_deux_populations_naissent_apres_le_plus_court"):
        # ⭐⭐⭐ LA GARDE QUI EMPECHE LA FAUSSE CONCLUSION : le biais de l'ensemble ne voyage JAMAIS
        # sans le partage par mode, sinon la figure publierait une derive de la matiere qui est un
        # artefact de melange.
        v("la prose dit que le biais de l'ensemble est celui d'un MÉLANGE",
          "MÉLANGE" in txt and "proportions changent" in txt)
        v("... et que les deux populations n'existent pas au plus court",
          "N'EXISTENT PAS À DEUX PAS" in txt)
        v("... et porte l'écart entre les modes aux deux bouts",
          f"{pm['ecart_au_plus_court']:+.3f}" in txt
          and f"{pm['ecart_au_plus_long']:+.3f}" in txt)
    fa = m.get("la_falaise_est_elle_celle_de_linstrument", {})
    if fa.get("une_derive_seule_reproduit_la_falaise"):
        v("la prose publie que l'instrument reproduit la falaise tout seul",
          "DÉRIVE SEULE REPRODUIT" in txt and str(fa["valeur_effondree_mediane"]) in txt)
        v("... et ce que ce contrôle n'établit PAS",
          "n'établit PAS" in txt and "ne les distingue pas" in txt)
    v("la prose garde debout ce que `106` a mesuré",
      "`106`" in txt and "parallèle" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "110_le_compte_suit_il_le_pas.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
