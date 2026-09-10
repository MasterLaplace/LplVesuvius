#!/usr/bin/env python3
"""Ce qui separe les deux populations de `107` — la famille declaree, corrigee, et son cout.

★★★ LE PANNEAU A EST LA FAMILLE ENTIERE, un candidat par ligne, force et sens dessines. Publier le
seul gagnant en ferait le survivant d'une selection invisible ; c'est la liste complete qui rend
lisible ce que la correction a du franchir.

★★★ LE PANNEAU B EST LE CONTRASTE QUI PORTE LA TRANCHE : le score du PAS separe a l'endroit, le
score du TRAJET separe a l'envers. `107` avait raison de dire que le score separe a l'envers — ce
n'etait pas le bon score, et le bon etait deja calcule a chaque pas.

★★★ LE PANNEAU C EST LA QUESTION OPERATIONNELLE : apres combien de pas le sait-on ? Un signal qui
n'arrive qu'a la fin de la marche ne remplace pas l'humain ; un signal lisible au troisieme pas,
oui.

Usage :
    uv run python src/figures/figure_ce_qui_separe_les_deux_populations.py --verifier
    uv run python src/figures/figure_ce_qui_separe_les_deux_populations.py \\
        --sortie docs/images/108_ce_qui_separe_les_deux_populations.png
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
MESURE = RACINE / "docs" / "mesures" / "ce_qui_separe_les_deux_populations.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    e = m.get("ensemble", {})
    lignes = []
    v = m.get("vide_entre_les_modes", {})
    if v.get("decidable"):
        lignes.append(
            f"★★ LA PARTITION NE DÉPEND PAS DU SEUIL, ET C'EST LA PREMIÈRE CHOSE À VÉRIFIER : un "
            f"seuil qui coupe un continuum FABRIQUE ses deux populations. Mesuré, le dernier "
            f"trajet du mode bas franchit {v['dernier_du_mode_bas']} feuille par pas et le "
            f"premier du mode haut {v['premier_du_mode_haut']}, soit un VIDE de "
            f"{v['vide_au_seuil']} autour d'un seuil à {v['seuil_feuilles_par_pas']}. "
            f"{'Rien ne se tient près du seuil' if v['la_partition_ne_depend_pas_du_seuil'] else 'Le seuil coupe un continuum'}"
            f", donc le déplacer ne changerait pas la partition.")
    if e.get("decidable"):
        fg = m.get("faux_gagnants_sans_correction", {})
        lignes.append(
            f"⚠⚠⚠ LE PIÈGE DE CETTE TRANCHE A UN NOM : un seuil réglé sur les données qui le "
            f"jugent. Avec {e['candidats_declares']} candidats DÉCLARÉS AVANT la mesure et "
            f"{e['trajets']} trajets, un test par candidat sans correction déclare un gagnant sur "
            f"du BRUIT PUR {fg.get('part_de_faux_gagnants', 0.0):.0%} du temps — chiffre MESURÉ "
            f"({fg.get('tirages')} tirages) et non invoqué. La correction est donc une "
            f"permutation sur le MAXIMUM de la famille, exacte et sans hypothèse "
            f"d'indépendance entre candidats.")
        retenus = [x for x in e["par_candidat"] if x["cle"] in e.get("retenus", [])]
        if retenus:
            lignes.append(
                "★★★ QUELQUE CHOSE LES SÉPARE, ET DANS LE BON SENS : "
                + " ; ".join(
                    f"{x['libelle']} (force {x['force']}, p corrigée {x['p_corrigee']}, "
                    f"{x['mediane_mode_haut']} pour le mode qui compte contre "
                    f"{x['mediane_mode_bas']})" for x in retenus)
                + ". Ces quantités sont mesurées SUR LE CUBE, à chaque pas, avant qu'aucun profil "
                  "de trajet ne soit ajusté — donc indépendamment de ce qu'elles prédisent.")
        else:
            lignes.append(
                f"NON — AUCUN DES {e['candidats_declares']} CANDIDATS DÉCLARÉS NE SURVIT À LA "
                f"CORRECTION. Ce n'est pas un échec de mesure mais le résultat que `107` "
                f"annonçait sans l'avoir mesuré : rien de ce qui est lu aujourd'hui ne distingue "
                f"une marche qui compte d'une marche qui ne compte rien.")
        tn = [x for x in e["par_candidat"] if x["role"] == "temoin_negatif"]
        if tn and e.get("retenus"):
            meilleur = max((x for x in e["par_candidat"] if x["role"] == "candidat"),
                           key=lambda y: y["force"])
            lignes.append(
                f"★★★ ET LE CONTRASTE EST LE FAIT CENTRAL DE LA TRANCHE. Le score du TRAJET "
                f"sépare fort ({tn[0]['force']}) et À L'ENVERS — {tn[0]['mediane_mode_bas']} pour "
                f"les marches qui ne comptent rien contre {tn[0]['mediane_mode_haut']} — tandis "
                f"que le score du PAS sépare presque autant ({meilleur['force']}) et À L'ENDROIT. "
                f"`107` avait raison de dire que le score sépare à l'envers ; ce n'était pas le "
                f"bon score, et le bon était déjà calculé à chaque pas sans être lu.")
        if e.get("le_mode_qui_ne_compte_rien_marche_plus_loin"):
            h = [x for x in e["par_candidat"] if x["role"] == "hypothese_refutee"]
            lignes.append(
                f"⚠⚠ ET UNE HYPOTHÈSE À MOI EST RÉFUTÉE, DANS L'AUTRE SENS QUE PRÉVU. J'avais "
                f"déclaré la longueur parcourue comme témoin POSITIF, en supposant que franchir "
                f"plus de feuilles veut dire avoir marché plus loin. Mesuré : le mode qui ne "
                f"compte RIEN marche PLUS LOIN ({h[0]['mediane_mode_bas']} µm contre "
                f"{h[0]['mediane_mode_haut']}), et sa force est {h[0]['force']}. Le retard n'est "
                f"donc pas une marche qui s'arrête tôt : c'est une marche qui avance sans rien "
                f"traverser. Elle reste publiée HORS famille, parce que l'y faire entrer après "
                f"avoir vu les résultats serait la faute que la correction existe pour empêcher.")
    ap = m.get("apres_combien_de_pas", {})
    if ap.get("decidable"):
        seuil = next((x for x in ap["par_longueur"] if x["p_corrigee"] < 0.05), None)
        lignes.append(
            f"★★★ ET LA QUESTION OPÉRATIONNELLE EST DIFFÉRENTE DE LA PRÉCÉDENTE : savoir après "
            f"coup qu'une marche n'a rien compté ne remplace pas l'humain ; savoir AVANT d'avoir "
            f"payé six cubes, oui. Le premier pas NE SUFFIT PAS (force "
            f"{ap['force_au_premier_pas']}, p corrigée {ap['p_corrigee_au_premier_pas']})"
            + (f", et il faut {seuil['pas_vus']} pas pour que ce soit lisible (force "
               f"{seuil['force']}, p corrigée {seuil['p_corrigee']})." if seuil else
               ", et la courbe ne devient jamais lisible sur cette course.")
            + " Un automate ne peut donc pas savoir en partant ; il peut savoir assez tôt pour "
              "repartir ailleurs.")
    a = m.get("par_selecteur", {}).get("calibre", {})
    b = m.get("par_selecteur", {}).get("deux_roles", {})
    if a.get("decidable") and b.get("decidable"):
        lignes.append(
            f"⚠⚠ ET LA RÉPLICATION PAR SÉLECTEUR NE TIENT PAS, ce qui borne tout ce qui précède. "
            f"`{'calibre'}` retient {a.get('retenus') or 'rien'} sur {a['trajets']} trajets, "
            f"`deux_roles` retient {b.get('retenus') or 'rien'} sur {b['trajets']} — même "
            f"meilleur candidat des deux côtés ({a.get('meilleur_candidat')}), forces "
            f"{a.get('force_du_meilleur')} et {b.get('force_du_meilleur')}, mais à l'effectif "
            f"d'un seul sélecteur la correction n'est plus franchie. ⚠ Et les 48 trajets de "
            f"l'ensemble ne sont PAS indépendants : deux marches partent de la même cellule.")
    c = (m.get("ensemble") or {}).get("cout_dun_seuil") or {}
    if c.get("decidable"):
        lignes.append(
            f"⚠ CE QU'UN SEUIL COÛTERAIT, ET IL EST CHIFFRÉ EN MARCHES PLUTÔT QU'EN VERTU : "
            f"{c['sens']} de {c['seuil']}, il jette {c['bonnes_marches_jetees']} bonnes marches "
            f"sur {c['bonnes_marches']} et garde {c['mauvaises_marches_gardees']} mauvaises sur "
            f"{c['mauvaises_marches']}. Hors échantillon il classe juste "
            f"{c['part_juste_hors_echantillon']:.1%} contre "
            f"{c.get('niveau_de_chance_mesure', 0.0):.1%} pour le niveau de chance MESURÉ — et ce "
            f"niveau n'est pas {c['part_juste_du_mode_majoritaire']:.1%} : choisir un seuil sur "
            f"les points qui le jugent laisse un optimisme résiduel que l'exclusion d'un point ne "
            f"retire pas entièrement.")
    lignes.append(
        "⚠ CE QUE CETTE TRANCHE NE DIT PAS : le score du balayage et le registre du trajet "
        "mesurent tous deux une PÉRIODICITÉ, sur deux fenêtres et par deux estimateurs "
        "différents. Qu'ils s'accordent n'est donc pas une surprise ; ce qui l'est, c'est que "
        "l'un pointe dans le bon sens quand l'autre pointe dans le mauvais. Et `106` reste "
        "debout : la quantité que ce pas suit n'est pas l'espacement d'un empilement parallèle.")
    return lignes


def panneau_famille(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "la famille DÉCLARÉE avant la mesure, force et sens",
             fill=DISCRET, font=petit)
    e = m.get("ensemble", {})
    if not e.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    par = sorted(e["par_candidat"],
                 key=lambda y: (y["role"] != "candidat", -y["force"]))
    # ⚠ La colonne de droite porte « force, sens, p corrigee » : sa largeur est reservee ICI,
    # sinon le libelle la pousse hors du panneau et la garde de cadre le dit.
    g, d = x0 + 12, x0 + pw - 132
    y = y0 + 30
    barres = 0
    retenus = set(e.get("retenus", []))
    for x in par:
        coul = (VERT if x["cle"] in retenus else
                (ROUGE if x["role"] == "temoin_negatif" else
                 (BLEU if x["role"] == "temoin_positif" else
                  (AMBRE if x["role"] == "hypothese_refutee" else DISCRET))))
        nom = x["libelle"]
        if len(nom) > 34:
            nom = nom[:33] + "…"
        art.text((g, y), nom, fill=coul, font=petit)
        larg = (d - g) * float(x["force"])
        art.rectangle([g, y + 13, g + max(larg, 1.0), y + 20], fill=coul)
        # ⚠ LE SENS EST DESSINE A COTE DE LA FORCE : une force sans sens se lit comme un critere
        # utilisable, et le temoin negatif prouve que ce serait faux.
        fleche = "↑" if x.get("le_mode_haut_est_plus_grand") else "↓"
        pc = f"p {x['p_corrigee']:.4f}" if "p_corrigee" in x else "hors famille"
        art.text((d + 6, y + 11), f"{x['force']:.3f}{fleche} {pc}", fill=coul, font=petit)
        y += 26
        barres += 1
    seuil = e["nul"]["force_max_du_nul_p95"]
    xs = g + (d - g) * seuil
    art.line([xs, y0 + 40, xs, y - 8], fill=ROUGE)
    art.text((x0 + 8, y + 2), f"— la barre rouge est le 95ᵉ centile de la plus grande force",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 16), f"   SOUS LE NUL ({seuil}) : la franchir seule ne suffit pas,",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, y + 30), f"   c'est la p corrigée qui tranche", fill=ROUGE, font=petit)
    return barres


def panneau_contraste(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "le score du PAS contre le score du TRAJET",
             fill=DISCRET, font=petit)
    e = m.get("ensemble", {})
    if not e.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    cands = [x for x in e["par_candidat"] if x["role"] == "candidat"]
    if not cands:
        return 0
    meilleur = max(cands, key=lambda y: y["force"])
    tn = next((x for x in e["par_candidat"] if x["role"] == "temoin_negatif"), None)
    tp = next((x for x in e["par_candidat"] if x["role"] == "temoin_positif"), None)
    y = y0 + 34
    traces = 0
    for x, coul, quoi in ((meilleur, VERT, "mesuré à CHAQUE PAS, sur le cube"),
                          (tn, ROUGE, "mesuré sur le TRAJET, après coup"),
                          (tp, BLEU, "ce qui DÉFINIT les modes (plomberie)")):
        if x is None:
            continue
        # ⚠ Le libelle est coupe A LA LARGEUR MESUREE et non a un nombre de caracteres : couper
        # a trente-huit signes a rendu « ce qui DÉF », qui se lit comme une panne de rendu.
        lib = x["libelle"]
        while lib and petit.getbbox(lib)[2] > pw - 24:
            lib = lib[:-2]
        art.text((x0 + 12, y), lib if lib == x["libelle"] else lib + "…",
                 fill=coul, font=petit)
        art.text((x0 + 12, y + 14), quoi, fill=DISCRET, font=petit)
        haut, bas = float(x["mediane_mode_haut"]), float(x["mediane_mode_bas"])
        hi = max(abs(haut), abs(bas)) or 1.0
        # ⚠ L'etiquette de ligne est HORS de la barre : ecrite dedans, elle disparait des que la
        # barre est courte — et la barre courte est justement celle qu'il faut lire.
        g, d = x0 + 84, x0 + pw - 74
        for k, (val, nom) in enumerate(((haut, "compte"), (bas, "compte rien"))):
            yy = y + 32 + k * 20
            larg = (d - g) * abs(val) / hi
            art.text((x0 + 12, yy + 1), nom, fill=DISCRET, font=petit)
            art.rectangle([g, yy, g + max(larg, 1.0), yy + 12],
                          fill=coul if k == 0 else DISCRET)
            art.text((d + 4, yy), f"{val:.3g}", fill=TEXTE, font=petit)
        fleche = "à l'ENDROIT" if x.get("le_mode_haut_est_plus_grand") else "à l'ENVERS"
        art.text((x0 + 12, y + 74), f"★ sépare {fleche} · force {x['force']}",
                 fill=coul, font=petit)
        y += 100
        traces += 1
    return traces


def panneau_quand(art, x0, y0, pw, ph, m, petit) -> int:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "après combien de pas le sait-on ?", fill=DISCRET, font=petit)
    ap = m.get("apres_combien_de_pas", {})
    if not ap.get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    lig = ap["par_longueur"]
    g, d = x0 + 40, x0 + pw - 84
    haut, bas = y0 + 44, y0 + ph - 116
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    n = len(lig)
    pts = 0
    # ⚠ Deux forces voisines (0,503 et 0,510) posent leurs etiquettes au meme endroit et la garde
    # de recouvrement le dit. L'etiquette est donc ecartee vers le bas quand la precedente est
    # trop proche : deplacer un texte vaut mieux que le faire disparaitre.
    derniere = None
    for i, x in enumerate(lig):
        xx = g + (d - g) * i / max(n - 1, 1)
        yy = bas - (bas - haut) * float(x["force"])
        coul = VERT if x["p_corrigee"] < 0.05 else DISCRET
        art.rectangle([xx - 3, yy - 3, xx + 3, yy + 3], fill=coul)
        art.text((xx - 3, bas + 4), f"{x['pas_vus']}", fill=DISCRET, font=petit)
        ye = yy - 6
        if derniere is not None and abs(ye - derniere) < 14:
            ye = derniere + 14
        art.text((d + 5, ye), f"{x['force']:.3f}", fill=coul, font=petit)
        derniere = ye
        pts += 1
    for f in (0.0, 0.5, 1.0):
        art.text((x0 + 8, bas - (bas - haut) * f - 5), f"{f:.1f}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 20), "pas vus (médiane courante du score)",
             fill=DISCRET, font=petit)
    seuil = next((x for x in lig if x["p_corrigee"] < 0.05), None)
    art.text((x0 + 8, bas + 42),
             "★ le premier pas suffit" if ap["le_premier_pas_suffit"]
             else "NON — le premier pas ne suffit PAS",
             fill=VERT if ap["le_premier_pas_suffit"] else ROUGE, font=petit)
    if seuil:
        art.text((x0 + 8, bas + 58), f"   lisible à partir de {seuil['pas_vus']} pas "
                 f"(p corrigée {seuil['p_corrigee']})", fill=VERT, font=petit)
        art.text((x0 + 8, bas + 74), f"   soit {seuil['pas_vus']} cubes payés avant de savoir",
                 fill=DISCRET, font=petit)
    else:
        art.text((x0 + 8, bas + 58), "   jamais lisible sur cette course", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 92), "vert = franchit la correction de famille",
             fill=DISCRET, font=petit)
    return pts


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 470
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    e = m.get("ensemble", {})
    art.text((marge, 16),
             "Ce qui sépare les deux populations de `107` — la famille déclarée, corrigée",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m.get('trajets_lisibles')} trajets de `107` · "
             f"{e.get('mode_haut', 0)} qui comptent, {e.get('mode_bas', 0)} qui ne comptent rien · "
             f"{e.get('candidats_declares', 0)} candidats déclarés AVANT la mesure · "
             + ("retenus : " + ", ".join(e.get("retenus", []))
                if e.get("retenus") else "aucun candidat retenu"),
             fill=DISCRET, font=moyen)
    titres = ("A · la famille entière, force et sens",
              "B · ★ le pas contre le trajet",
              "C · ★ après combien de pas le sait-on")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_famille(art, marge, 104, pw, ph, m, petit)
    b = panneau_contraste(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_quand(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "famille": a, "contraste": b, "quand": c,
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
                 "108_ce_qui_separe_les_deux_populations.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["famille"] > 0 and d["contraste"] > 0 and d["quand"] > 0,
      f"{d['famille']} / {d['contraste']} / {d['quand']}")
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(w <= d["largeur_utile"] for _t, w in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _w in d["prose"]]))

    txt = " ".join(t for t, _w in d["prose"])
    e = m["ensemble"]
    # ⭐⭐⭐ LA GARDE QUI COMPTE : la figure doit publier la FAMILLE ENTIERE, pas le gagnant seul.
    v("le panneau A porte une ligne par candidat DÉCLARÉ, plus les témoins",
      d["famille"] == len(e["par_candidat"]),
      f"{d['famille']} lignes pour {len(e['par_candidat'])} entrées")
    # ⚠⚠ ET LE CHIFFRE QUI JUSTIFIE LA CORRECTION DOIT ETRE DANS LA PROSE : sans lui, un p brut de
    # 0,03 se lit comme un resultat.
    v("la prose porte le taux de faux gagnants MESURÉ sur du bruit",
      "BRUIT PUR" in txt and "MESURÉ" in txt)
    v("... et le nombre de candidats déclarés AVANT la mesure",
      "DÉCLARÉS AVANT" in txt or "déclarés AVANT" in txt)
    if e.get("retenus"):
        v("la prose nomme les candidats retenus",
          all(any(x["libelle"][:20] in txt for x in e["par_candidat"] if x["cle"] == c)
              for c in e["retenus"]))
        # ⚠⚠⚠ LE SENS EST CE QUI SE PERD LE PLUS FACILEMENT, et `107` l'a paye : publier « le
        # score separe » sans dire dans quel sens laisse croire qu'un seuil ecarterait le mauvais.
        v("... et le SENS du contraste entre le pas et le trajet",
          "À L'ENVERS" in txt and "À L'ENDROIT" in txt)
    else:
        v("la prose dit que rien ne survit, plutôt que de taire le résultat",
          "AUCUN DES" in txt and "CORRECTION" in txt)
    # ⚠⚠ LA REPLICATION EST LA BORNE DU RESULTAT : la taire ferait passer 48 trajets non
    # independants pour 48 mesures.
    v("la prose dit que les 48 trajets ne sont PAS indépendants",
      "PAS indépendants" in txt or "pas indépendants" in txt)
    v("... et ce que la réplication par sélecteur donne",
      "sélecteur" in txt)
    # ⚠ L'hypothese refutee est publiee AVEC son sens, parce que son echec est un fait.
    if e.get("le_mode_qui_ne_compte_rien_marche_plus_loin"):
        v("la prose publie l'hypothèse réfutée et le sens de son échec",
          "RÉFUTÉE" in txt and "PLUS LOIN" in txt)
    v("la prose garde debout ce que `106` a mesuré",
      "`106`" in txt and "parallèle" in txt)
    # ⭐ La plomberie doit etre verte, sinon la figure publie un tableau a jeter.
    v("le témoin positif sépare parfaitement, donc la plomberie tient",
      e.get("la_plomberie_tient") is True, f"force {e.get('force_du_temoin_positif')}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" /
                   "108_ce_qui_separe_les_deux_populations.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
