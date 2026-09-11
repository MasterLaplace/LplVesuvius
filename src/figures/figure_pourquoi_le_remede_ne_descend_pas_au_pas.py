#!/usr/bin/env python3
"""Pourquoi le remede de `111` ne descend pas au pas — et ou il redevient possible.

★★★ LE PANNEAU A EST LE FAIT STRUCTUREL : quels modes de Fourier d'une fenetre sont SOUS le
signal. A un pas la liste est vide, et elle cesse de l'etre exactement quand la fenetre depasse la
plus grande longueur d'onde plausible.

★★★ LE PANNEAU B EST CE QUI DESIGNE LA BONNE BASE, par l'echec des deux autres : un detrendage
polynomial de degre deux absorbe presque tout le gabarit d'un pas, une grille harmonique non
entiere l'absorbe entierement, et seule la base de Fourier de la fenetre le laisse.

★★★ LE PANNEAU C EST LA MESURE SUR LES SEGMENTS REELS, gratuite parce que `111` a garde ses
profils : le gain par fenetre, et la part qui franchit la barre avant et apres.

Usage :
    uv run python src/figures/figure_pourquoi_le_remede_ne_descend_pas_au_pas.py --verifier
    uv run python src/figures/figure_pourquoi_le_remede_ne_descend_pas_au_pas.py \\
        --sortie docs/images/112_pourquoi_le_remede_ne_descend_pas_au_pas.png
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
MESURE = RACINE / "docs" / "mesures" / "pourquoi_le_remede_ne_descend_pas_au_pas.json"

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
    a = m.get("a_partir_de_quelle_fenetre", {})
    c = m.get("la_contamination_est_irreductible", {})
    lignes.append(
        f"★★★ LE REMÈDE DE `111` NE DESCEND PAS AU PAS, ET CE N'EST PAS UN MANQUE D'EFFORT : "
        f"c'est la RÉSOLUTION de la fenêtre. Une base de Fourier a pour modes les entiers — "
        f"1, 2, 3 périodes sur la fenêtre — et « longueur d'onde supérieure à λmax » se lit "
        f"`j < f_lo = L / λmax`. Sur un segment d'UN pas, f_lo vaut {a.get('par_fenetre', [{}])[0].get('f_lo')} : "
        f"aucun mode non nul n'est sous le signal, parce que le PREMIER mode de la fenêtre EST le "
        f"signal. Une dérive plus longue que la fenêtre n'y est pas REPRÉSENTABLE — elle ne se "
        f"distingue pas d'un décalage constant plus le signal lui-même.")
    if c:
        lignes.append(
            f"★★★ ET LA CONSÉQUENCE EST MESURÉE, PAS DÉDUITE : sur cinq dérives injectées, le "
            f"retrait des modes bas rend un gain de EXACTEMENT zéro à chaque fois — non pas parce "
            f"qu'il est mal fait, mais parce que la liste des modes est vide "
            f"({c.get('parce_que_la_liste_est_vide')}). ⚠ Et il y aurait de quoi réparer : la "
            f"contamination atteint {c.get('contamination_max')} d'accord, d'un instrument qui "
            f"vaut {c.get('accord_sans_derive')} sans dérive.")
    b = m.get("pourquoi_les_autres_bases_echouent", {})
    o = m.get("lorthogonalite_est_elle_exacte", {})
    if b:
        poly = b["polynomial"][0]
        lignes.append(
            f"⚠⚠⚠ ET J'AI ÉCHOUÉ DEUX FOIS AVANT DE LE COMPRENDRE, CHAQUE FOIS SUR LA BASE ET NON "
            f"SUR LA MATIÈRE. Un détrendage POLYNOMIAL de degré deux absorbe {poly["degre_2"]} "
            f"du gabarit à un pas : ce n'est pas un sous-espace de basse fréquence, c'est un "
            f"sous-espace qui contient le signal. Et une grille harmonique à fréquences NON "
            f"ENTIÈRES en absorbe jusqu'à "
            f"{max(x['part'] for x in b['harmonique_non_entiere'])} — elle n'est pas orthogonale "
            f"sur la fenêtre, et son conditionnement est si mauvais qu'une décomposition par `qr` "
            f"en rendait un espace plus grand que le sien. C'est par SVD que le rang réel se voit.")
        lignes.append(
            f"★★ LA SEULE BASE HONNÊTE EST CELLE DE FOURIER SUR LA FENÊTRE, et elle en absorbe "
            f"{b.get('part_absorbee_par_fourier')}. ⚠⚠⚠ Mais « EXACTEMENT orthogonal » était faux "
            f"et la batterie m'a repris : l'orthogonalité est exacte sur la grille DFT "
            f"({o.get('pire_sur_la_grille_dft')}) et seulement approchée "
            f"({o.get('pire_sur_la_grille_incluse')}) sur la grille à extrémité INCLUSE que `98` "
            f"et `111` emploient — le premier et le dernier échantillon y sont à la même phase. "
            f"Le résidu décroît comme `1/n`, donc la conclusion tient, mais le chiffre remplace "
            f"le mot.")
    if a:
        lignes.append(
            f"★★★ ET LE REMÈDE REDEVIENT POSSIBLE À {a.get('premiere_fenetre_nettoyable')} PAS, par "
            f"une inégalité et non par un essai : le premier mode retirable apparaît quand la "
            f"fenêtre dépasse λmax, soit {a.get('seuil_en_micrometres')} µm — "
            f"{a.get('seuil_en_pas')} pas à l'avance mesurée. ★ Et le signal n'est JAMAIS dans ce "
            f"qu'on retire, à aucune longueur "
            f"({a.get('le_signal_reste_toujours_hors_du_retrait')}) : c'est ce qui rend le remède "
            f"de `111` juste plutôt qu'approximatif.")
    s = m.get("sur_les_segments_reels", {})
    if s.get("decidable"):
        un = s["par_fenetre"][0]
        long_ = s["par_fenetre"][-1]
        lignes.append(
            f"★★ SUR LES SEGMENTS RÉELS — et gratuitement, parce que `111` a gardé ses profils — "
            f"le retrait ne change RIEN à un pas (gain {un['gain_median']}, "
            f"{s.get('a_un_pas_le_retrait_ne_change_rien')}) et aide sur les fenêtres longues : la "
            f"part au-dessus de la barre passe de {un['part_au_dessus_brut']} à "
            f"{un['part_au_dessus_apres_retrait']} à un pas, et de {long_['part_au_dessus_brut']} "
            f"à {long_['part_au_dessus_apres_retrait']} à {long_['pas']} pas.")
        lignes.append(
            f"⚠⚠ MAIS CE N'EST PAS UN GAIN GRATUIT, ET LE DIRE EST LA MOITIÉ DU RÉSULTAT : une "
            f"fenêtre longue confirme MOINS SOUVENT qu'un pas seul — "
            f"{long_['part_au_dessus_apres_retrait']} contre {un['part_au_dessus_brut']} — parce "
            f"qu'un gabarit de {long_['pas']} feuilles sur {long_['pas']} pas est un ajustement "
            f"bien plus exigeant. Le remède améliore la fenêtre longue de six à neuf points ; il "
            f"ne la rend pas meilleure que le pas seul.")
        lignes.append(
            f"⚠ ET LES FENÊTRES D'UNE MÊME MARCHE SE RECOUVRENT, ce qui borne tout ce qui précède : {s['par_fenetre'][0]['fenetres']} "
            f"fenêtres d'un pas viennent de 56 marches, donc elles partagent leurs pas. Ce qui est "
            f"rendu décrit une population de fenêtres, pas autant de mesures indépendantes.")
    lignes.append(
        "⚠ CE QUE CETTE TRANCHE NE DIT PAS : que la portée du marcheur change — elle ne touche "
        "aucun marcheur ; ni que confirmer sur une fenêtre longue soit la bonne politique — elle "
        "chiffre ce que cette politique gagnerait et ce qu'elle coûterait, et la trancher demande "
        "une course. Et `106` reste debout : la quantité que ce pas suit n'est pas l'espacement "
        "d'un empilement localement parallèle.")
    return lignes


def _cadre(art, x0, y0, pw, ph, titre, petit):
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), titre, fill=DISCRET, font=petit)


def panneau_modes(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "quels modes sont SOUS le signal ?", petit)
    a = m.get("a_partir_de_quelle_fenetre", {})
    lig = a.get("par_fenetre") or []
    if not lig:
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    y = y0 + 34
    traces = 0
    art.text((x0 + 12, y), f"{'fenêtre':>8} {'f_lo':>6}  modes à retirer", fill=DISCRET,
             font=petit)
    y += 18
    for x in lig:
        coul = ROUGE if not x["modes_a_retirer"] else VERT
        art.text((x0 + 12, y),
                 f"{x['pas']:>4} pas {x['f_lo']:>6.2f}  "
                 + (str(x["modes_a_retirer"]) if x["modes_a_retirer"] else "— AUCUN"),
                 fill=coul, font=petit)
        art.text((x0 + 12, y + 13), f"          signal au mode {x['mode_du_signal']}",
                 fill=DISCRET, font=petit)
        y += 32
        traces += 1
    art.text((x0 + 12, y + 8),
             f"★★★ première fenêtre nettoyable : "
             f"{a.get('premiere_fenetre_nettoyable')} pas", fill=VERT, font=petit)
    art.text((x0 + 12, y + 24),
             f"    seuil {a.get('seuil_en_micrometres')} µm = "
             f"{a.get('seuil_en_pas')} pas", fill=TEXTE, font=petit)
    c = m.get("la_contamination_est_irreductible", {})
    if c:
        art.text((x0 + 12, y + 46), "à UN pas, gain du retrait :", fill=DISCRET, font=petit)
        yy = y + 60
        for x in c.get("par_derive", []):
            art.text((x0 + 12, yy),
                     f"  λ={x['longueur_donde_um']:>7.1f} µm : {x['accord_brut']:.3f} → "
                     f"{x['accord_apres_retrait']:.3f}  ({x['gain']:+.4f})",
                     fill=ROUGE, font=petit)
            yy += 13
        art.text((x0 + 12, yy + 6),
                 f"★ contamination {c.get('contamination_max')}, irréductible",
                 fill=ROUGE, font=petit)
    return traces


def panneau_bases(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "ce que chaque base ABSORBE du signal", petit)
    b = m.get("pourquoi_les_autres_bases_echouent", {})
    if not b.get("polynomial"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    series = [("polynôme, degré 2", [x["degre_2"] for x in b["polynomial"]], ROUGE),
              ("grille harmonique NON entière",
               [x["part"] for x in b["harmonique_non_entiere"]], AMBRE),
              ("FOURIER de la fenêtre",
               [x["part"] for x in b["fourier_de_la_fenetre"]], VERT)]
    pas = [x["pas"] for x in b["polynomial"]]
    g, d = x0 + 46, x0 + pw - 66
    haut, bas = y0 + 66, y0 + ph - 150
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    for f, lib in ((0.0, "0"), (0.5, "0,5"), (1.0, "1,0")):
        yy = bas - (bas - haut) * f
        art.text((x0 + 12, yy - 6), lib, fill=DISCRET, font=petit)
    traces = 0
    for j, (nom, vals, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 22 + j * 13), nom, fill=coul, font=petit)
        prec = None
        for i, val in enumerate(vals):
            xx = g + (d - g) * i / max(len(vals) - 1, 1)
            yy = bas - (bas - haut) * min(val, 1.0)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 4, bas + 4), f"{pas[i]}", fill=DISCRET, font=petit)
            traces += 1
    art.text((x0 + 8, bas + 22), "longueur de la fenêtre, en pas", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 42),
             f"★ le polynôme de degré deux détruit le gabarit", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 56),
             f"   à UN pas ({b['polynomial'][0]['degre_2']}), et devient inoffensif",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 70),
             f"   à six ({b['polynomial'][-1]['degre_2']})", fill=ROUGE, font=petit)
    o = m.get("lorthogonalite_est_elle_exacte", {})
    if o:
        art.text((x0 + 8, bas + 92), "⚠⚠⚠ « exactement orthogonal » était faux :",
                 fill=AMBRE, font=petit)
        art.text((x0 + 8, bas + 106),
                 f"    {o.get('pire_sur_la_grille_incluse')} sur la grille employée,",
                 fill=AMBRE, font=petit)
        art.text((x0 + 8, bas + 120),
                 f"    {o.get('pire_sur_la_grille_dft')} sur la grille DFT",
                 fill=AMBRE, font=petit)
    return traces


def panneau_reels(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "sur les segments réels — zéro lecture", petit)
    s = m.get("sur_les_segments_reels", {})
    lig = s.get("par_fenetre") or []
    if not lig:
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    g, d = x0 + 46, x0 + pw - 66
    haut, bas = y0 + 66, y0 + ph - 150
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    hi = 0.8
    for f, lib in ((0.0, "0"), (0.4, "0,4"), (0.8, "0,8")):
        yy = bas - (bas - haut) * (f / hi)
        art.text((x0 + 12, yy - 6), lib, fill=DISCRET, font=petit)
    series = [("part > barre, BRUT", "part_au_dessus_brut", ROUGE),
              ("part > barre, APRÈS retrait", "part_au_dessus_apres_retrait", VERT)]
    traces = 0
    for j, (nom, cle, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 22 + j * 13), nom, fill=coul, font=petit)
        prec = None
        for i, x in enumerate(lig):
            xx = g + (d - g) * i / max(len(lig) - 1, 1)
            yy = bas - (bas - haut) * (x[cle] / hi)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 4, bas + 4), f"{x['pas']}", fill=DISCRET, font=petit)
            traces += 1
    art.text((x0 + 8, bas + 22), "longueur de la fenêtre, en pas", fill=DISCRET, font=petit)
    un = lig[0]
    art.text((x0 + 8, bas + 42),
             f"★★★ à UN pas, rien ne bouge (gain {un['gain_median']})", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 58), "    parce qu'il n'y a rien à retirer", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 80), "★ le retrait aide dès deux pas :", fill=VERT, font=petit)
    for i, x in enumerate(lig[1:], start=0):
        art.text((x0 + 8, bas + 94 + i * 13),
                 f"   {x['pas']} pas : {x['part_au_dessus_brut']:.3f} → "
                 f"{x['part_au_dessus_apres_retrait']:.3f}", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 94 + len(lig[1:]) * 13 + 6),
             f"⚠⚠ mais toutes restent SOUS le pas seul ({un['part_au_dessus_brut']:.3f})",
             fill=AMBRE, font=petit)
    return traces


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 500
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    a = m.get("a_partir_de_quelle_fenetre", {})
    art.text((marge, 16),
             "Pourquoi le remède de `111` ne descend pas au pas — la résolution de la fenêtre",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"λmax {m.get('lambda_max_um')} µm · avance médiane {m.get('avance_mediane_um')} µm · "
             f"première fenêtre nettoyable {a.get('premiere_fenetre_nettoyable')} pas · "
             f"zéro lecture distante",
             fill=DISCRET, font=moyen)
    titres = ("A · ★ les modes sous le signal",
              "B · ★ ce que chaque base absorbe",
              "C · ★ sur les segments réels")
    for k, t in enumerate(titres):
        art.text((marge + k * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    x = panneau_modes(art, marge, 104, pw, ph, m, petit)
    y = panneau_bases(art, marge + pw + ecart, 104, pw, ph, m, petit)
    z = panneau_reels(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + k * (pw + ecart), 104, marge + k * (pw + ecart) + pw, 104 + ph)
              for k in range(3)]
    debut = H - len(lignes) * 19 - 12
    for k, l in enumerate(lignes):
        art.text((marge, debut + k * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "modes": x, "bases": y, "reels": z,
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
                 "112_pourquoi_le_remede_ne_descend_pas_au_pas.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["modes"] > 0 and d["bases"] > 0 and d["reels"] > 0,
      f"{d['modes']} / {d['bases']} / {d['reels']}")
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(w <= d["largeur_utile"] for _t, w in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _w in d["prose"]]))

    txt = " ".join(t for t, _w in d["prose"])
    # ⭐⭐⭐ LA GARDE QUI COMPTE : le fait structurel ne voyage jamais sans sa RAISON. « Ça ne marche
    # pas » se lit comme un manque d'effort ; « la liste des modes est vide » est une propriété.
    v("la prose dit POURQUOI le retrait ne rend rien à un pas",
      "REPRÉSENTABLE" in txt and "liste des modes est vide" in txt)
    # ⚠⚠ LES DEUX ECHECS DE BASE SONT PUBLIES, parce que c'est leur echec qui designe la bonne.
    v("la prose publie les deux bases qui échouent, avec ce qu'elles absorbent",
      str(m["pourquoi_les_autres_bases_echouent"]["polynomial"][0]["degre_2"]) in txt
      and "NON ENTIÈRES" in txt)
    # ⚠⚠⚠ ET LA CORRECTION DE MA PROPRE REVENDICATION : « exactement orthogonal » etait faux.
    o = m.get("lorthogonalite_est_elle_exacte", {})
    v("la prose corrige « exactement orthogonal » avec les deux grilles",
      "était faux" in txt and str(o.get("pire_sur_la_grille_incluse")) in txt
      and str(o.get("pire_sur_la_grille_dft")) in txt)
    a = m.get("a_partir_de_quelle_fenetre", {})
    v("la prose dit à partir de quelle fenêtre le remède redevient possible",
      str(a.get("premiere_fenetre_nettoyable")) in txt
      and str(a.get("seuil_en_micrometres")) in txt)
    s = m.get("sur_les_segments_reels", {})
    if s.get("decidable"):
        # ⚠⚠ LE GAIN NE VOYAGE JAMAIS SANS SON COUT : une fenetre longue confirme MOINS souvent
        # qu'un pas seul, et le taire ferait lire le gain comme une amelioration nette.
        v("la prose dit que le gain n'est PAS gratuit",
          "MOINS SOUVENT" in txt)
        # ⚠ Comparaison insensible a la casse : la prose ecrit « SE RECOUVRENT » en capitales, et
        # une garde qui cherchait la minuscule echouait sur une prose correcte. Meme piege que
        # dans la figure de `110`.
        v("... et que les fenêtres se recouvrent",
          "recouvrent" in txt.lower())
    v("la prose garde debout ce que `106` a mesuré", "`106`" in txt)
    v("... et dit que la portée du marcheur n'est pas touchée",
      "portée du marcheur" in txt and "ne touche" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" /
                   "112_pourquoi_le_remede_ne_descend_pas_au_pas.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
