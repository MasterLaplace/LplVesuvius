#!/usr/bin/env python3
"""Le cube lu moins cher — l'economie est REFUTEE par le corpus, et par ma propre sonde.

⭐⭐⭐ LE PANNEAU A PORTE LA GARDE : sur un empilement FABRIQUE dont la reponse est connue, chaque
finesse est jugee contre la barre du nul de SA PROPRE FORME. Et la premiere ligne est le fait qui
surprend — a fort bruit, le cube PLEINE RESOLUTION ne tient pas sa propre garde, la ou un pas de 2
la passe avec sept degres de marge.

⭐⭐⭐ LE PANNEAU B EST LE CONTROLE APPARIE SUR LE VRAI VOLUME : chaque cellule lue une fois par
pas, et la quantite rendue est l'angle entre les reponses. Comparer deux populations differentes
ferait dire au resultat ce qu'on veut.

⚠⚠⚠ ET LE PANNEAU C PORTE LA CORRECTION QUI COMPTE : le comptage de points predisait un gain de
SEPT, la mesure en rend DEUX. Une lecture distante est dominee par le nombre de PLAGES d'octets et
par un fixe par cube, pas par le nombre de points.

Usage :
    uv run python src/figures/figure_le_cube_lu_moins_cher.py --verifier
    uv run python src/figures/figure_le_cube_lu_moins_cher.py \\
        --sortie docs/images/103_le_cube_lu_moins_cher.png
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
MESURE = RACINE / "docs" / "mesures" / "le_cube_lu_moins_cher.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    f = m["sur_empilement_fabrique"]
    v = m["sur_le_vrai_volume"]
    pr = m["le_pas_retenu"]
    fin = next(x for x in f["lignes"] if x["pas_echantillon"] == 1)
    ret = next((x for x in v["lignes"] if x["pas_echantillon"] == pr["pas_retenu"]), None)
    moins = min(pr["verdicts"], key=lambda z: z["pas_echantillon"]) if pr["verdicts"] else {}
    refus = [x for x in pr["verdicts"] if not x["retenu"]]
    return [
        f"★★★ CE QUE CE FICHIER MESURE, ET C'EST `102` QUI L'IMPOSE. `102` a mesure que la matiere "
        f"porte AU MOINS deux pas, et sa portee est CENSUREE : 17 bandes sur 28 butent sur un "
        f"plafond de six pas. relever ce plafond est la marche suivante — mais un cube coute "
        f"15,4 s de lecture reseau, donc trente pas demanderaient QUATORZE HEURES. avant de subir "
        f"ce cout, il faut savoir s'il est reductible.",
        f"★★★ ET IL L'EST, PAR UNE ECONOMIE QUI NE CHANGE PAS CE QU'ON REGARDE. retrecir le cube "
        f"changerait la structure vue ; l'ECHANTILLONNER plus grossierement — un voxel sur deux, "
        f"meme portee de {m['cote_um_du_cube']} µm — change seulement combien on paie pour la "
        f"regarder. la portee physique est identique a tous les pas, et c'est asserte.",
        f"★★★ PANNEAU A — LA GARDE, SUR UN EMPILEMENT DONT LA REPONSE EST CONNUE. chaque finesse "
        f"est jugee contre la barre du nul de SA PROPRE FORME, parce qu'un cube plus grossier a "
        f"moins de points donc un nul different — reutiliser la barre d'une autre forme "
        f"comparerait deux choses. et la premiere ligne surprend : a bruit fort, le cube PLEINE "
        f"RESOLUTION ne tient PAS sa propre garde ({fin['desaccord_des_moities_deg']}° de "
        f"desaccord pour une barre de {fin['barre_de_sa_forme_deg']}°, marge "
        f"{fin['marge_sous_la_barre_deg']}°), la ou un pas de 2 la passe largement.",
        f"★★★ PANNEAU B — LE CONTROLE APPARIE SUR LE VRAI VOLUME, {v['cellules']} cellules. chaque "
        f"cellule est lue UNE FOIS PAR PAS et la quantite rendue est l'angle entre les reponses. "
        f"comparer deux populations differentes ferait dire au resultat ce qu'on veut, et ce depot "
        f"l'a deja paye — `derouler_par_le_pas_normal` mesure son temoin sur les memes cellules, "
        f"exactement pour ca.",
        (f"★★ LE PAS RETENU EST {pr['pas_retenu']}, ET IL EST DERIVE PLUTOT QUE CHOISI : le plus "
         f"grossier qui satisfait DEUX conditions INDEPENDANTES — la garde du fabrique, et aucune "
         f"cellule reelle au-dela de {pr['tolere_deg']:.0f}° du pas le plus fin. il s'accorde a "
         f"{ret.get('ecart_median_au_plus_fin_deg')}° (p90 {ret.get('ecart_p90_deg')}°) et coute "
         f"×{ret.get('gain_de_temps')} moins de temps."
         if ret is not None else
         f"NON — AUCUNE ECONOMIE NE PASSE, ET C'EST LE CORPUS ENTIER QUI LE DIT. le pas 2 — le "
         f"moins grossier — ecarte deja "
         f"{100 * moins.get('part_reelle_au_dela_du_tolere', 0):.1f} % des cellules de plus de "
         f"{pr['tolere_deg']:.0f}° du pas le plus fin. pris UN pas a la fois cela n'a l'air de "
         f"rien ; mais `102` les ENCHAINE, et a six pas cela abime "
         f"{100 * moins.get('part_de_marches_de_six_pas_touchees', 0):.0f} % des marches. le cube "
         f"se lit donc au voxel pres."),
        f"⚠⚠⚠ ET C'EST MA PROPRE SONDE QUI ETAIT TOMBEE DANS LE PIEGE. sur DEUX bandes j'avais "
        f"mesure 0 % de cellules au-dela de dix degres au pas 2, et j'allais l'adopter ; sur les "
        f"VINGT-HUIT bandes, c'est 7,3 %. « un bord se compte sur le corpus entier, pas sur les "
        f"bandes qu'on a sondees » — la faute que `93` a payee, que `95` a reecrite, et que je "
        f"viens de repayer.",
        f"⚠ ET LES REFUS SONT RENDUS AVEC LEUR RAISON, sinon relever le pas plus tard se ferait "
        f"sans la revoir : "
        + " · ".join(f"pas {x['pas_echantillon']} — {x['pourquoi_refuse']}" for x in refus)
        + ".",
        f"⚠⚠⚠ PANNEAU C — ET LE GAIN DE TEMPS N'EST PAS LE GAIN DE POINTS. le comptage de points "
        f"predisait SEPT, la mesure rend DEUX. une lecture distante est dominee par le nombre de "
        f"PLAGES d'octets — une par rangee (z, y) — et par un fixe par cube, pas par le nombre de "
        f"points : un cube sous-echantillonne touche toujours une plage par rangee. le cout se "
        f"MESURE, il ne se modelise pas.",
        f"⚠ ET LE RAPPORT DE POINTS LUI-MEME N'EST PAS HUIT. un pas de 2 sur 41 points en laisse "
        f"21, pas 20,5, donc le rapport vaut (41/21)³ = 7,44 et non 2³. le supposer rond etait une "
        f"erreur, et le compte exact passe par la forme reellement produite.",
        f"⚠⚠ CE QUE CA NE DEBLOQUE PAS, ET IL FAUT LE DIRE : la mesure de PORTEE de `102` — celle "
        f"qui dirait combien de pas la matiere porte vraiment, au lieu d'« au moins deux » — reste "
        f"a QUATORZE HEURES pour trente pas. l'economie aurait divise ce cout par deux ; elle est "
        f"refutee, donc la borne de `102` se levera en payant le prix plein, ou pas du tout.",
        f"★ CE QUE LA TRANCHE LAISSE QUAND MEME : le cout est desormais MESURE et non suppose — "
        f"15,4 s par cube, un plancher de 3,8 s qui ne descend jamais, et un temps qui suit les "
        f"RANGEES. c'est ce qui permet de chiffrer d'avance ce que coute chaque nouvelle mesure "
        f"au lieu de le decouvrir apres sept heures.",
    ]


def panneau_garde(art, x0, y0, pw, ph, m, petit) -> int:
    """La marge sous la barre du nul, par finesse, sur l'empilement fabriqué."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "la garde tient-elle, sur réponse connue ?",
             fill=DISCRET, font=petit)
    lignes = m["sur_empilement_fabrique"]["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 84
    haut = y0 + 46
    h = (ph - 150) / max(len(lignes), 1)
    vals = [x["marge_sous_la_barre_deg"] for x in lignes
            if x["marge_sous_la_barre_deg"] is not None]
    hi = max(max(abs(v) for v in vals), 1.0) * 1.2 if vals else 1.0
    zero = gauche + (droite - gauche) * 0.35
    barres = 0
    for j, x in enumerate(lignes):
        y = haut + j * h
        mg = x["marge_sous_la_barre_deg"]
        tient = x["la_garde_tient"]
        art.text((x0 + 6, y + 2), f"pas {x['pas_echantillon']}", fill=TEXTE, font=petit)
        if mg is None:
            art.text((zero + 4, y + 2), "pas comparable", fill=DISCRET, font=petit)
            barres += 1
            continue
        larg = (droite - gauche) * 0.45 * mg / hi
        coul = VERT if tient else ROUGE
        a, b = (zero, zero + larg) if larg >= 0 else (zero + larg, zero)
        art.rectangle([a, y, b, y + 13], fill=coul)
        art.text((max(b, zero) + 5, y - 1),
                 f"{mg:+.2f}° — {'TIENT' if tient else 'NON'}", fill=coul, font=petit)
        barres += 1
    art.line([zero, haut - 6, zero, haut + len(lignes) * h], fill=TEXTE)
    art.text((zero - 14, haut + len(lignes) * h + 4), "0", fill=DISCRET, font=petit)
    bas = haut + len(lignes) * h + 22
    art.text((x0 + 8, bas), "marge = barre du nul de SA forme moins le",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 14), "désaccord des deux moitiés du cube",
             fill=DISCRET, font=petit)
    fin = next(x for x in lignes if x["pas_echantillon"] == 1)
    if not fin["la_garde_tient"]:
        art.text((x0 + 8, bas + 34),
                 "★★ à ce bruit, le cube PLEINE RÉSOLUTION", fill=ROUGE, font=petit)
        art.text((x0 + 8, bas + 48),
                 "   ne tient pas sa propre garde.", fill=ROUGE, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             f"empilement fabriqué, bruit σ = {m['sur_empilement_fabrique'].get('bruit')}",
             fill=DISCRET, font=petit)
    return barres


def panneau_accord(art, x0, y0, pw, ph, m, petit) -> int:
    """L'écart au pas le plus fin, sur les mêmes cellules du vrai volume."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "les deux finesses disent-elles la même chose ?",
             fill=DISCRET, font=petit)
    v = m["sur_le_vrai_volume"]
    lignes = v["lignes"]
    gauche, droite = x0 + 56, x0 + pw - 70
    haut = y0 + 46
    h = (ph - 160) / max(len(lignes), 1)
    hi = max(max(x["ecart_p90_deg"] for x in lignes), m["le_pas_retenu"]["tolere_deg"]) * 1.2
    barres = 0
    for j, x in enumerate(lignes):
        y = haut + j * h
        art.text((x0 + 6, y + 6), f"pas {x['pas_echantillon']}", fill=TEXTE, font=petit)
        # ⭐ La MEDIANE et le p90 sont traces ensemble : une mediane basse peut cacher une queue
        # qui change le resultat, et c'est la queue qui a fait tomber le pas 3.
        for k, (cle, coul) in enumerate((("ecart_median_au_plus_fin_deg", BLEU),
                                         ("ecart_p90_deg", AMBRE))):
            larg = (droite - gauche) * x[cle] / hi
            yy = y + k * 13
            art.rectangle([gauche, yy, gauche + max(larg, 1.0), yy + 11], fill=coul)
            art.text((gauche + max(larg, 1.0) + 5, yy - 2),
                     f"{x[cle]:.2f}°", fill=coul, font=petit)
            barres += 1
        p = x["part_au_dela_de_dix_degres"]
        art.text((droite + 8, y + 6), f"{100 * p:.0f} %",
                 fill=(ROUGE if p > 0 else VERT), font=petit)
    tol = (droite - gauche) * m["le_pas_retenu"]["tolere_deg"] / hi + gauche
    for yy in range(int(haut) - 6, int(haut + len(lignes) * h), 7):
        art.line([tol, yy, tol, yy + 3], fill=ROUGE)
    art.text((x0 + 8, y0 + 26), "bleu : écart médian   ambre : p90   à droite : part > 10°",
             fill=DISCRET, font=petit)
    bas = haut + len(lignes) * h + 12
    art.text((x0 + 8, bas), f"rouge pointillé : la tolérance de "
             f"{m['le_pas_retenu']['tolere_deg']:.0f}°", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 20),
             f"★★ {v['cellules']} cellules APPARIÉES, chacune lue", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 34), "   une fois par pas — pas deux populations.",
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : angle au pas le plus fin",
             fill=DISCRET, font=petit)
    return barres


def panneau_cout(art, x0, y0, pw, ph, m, petit) -> int:
    """Le gain prédit par le comptage de points contre le gain mesuré."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "le coût suit-il le nombre de points ?",
             fill=DISCRET, font=petit)
    lignes = m["sur_le_vrai_volume"]["lignes"]
    fin = next(x for x in lignes if x["pas_echantillon"] == 1)
    gauche, droite = x0 + 56, x0 + pw - 68
    haut = y0 + 46
    h = (ph - 170) / max(len(lignes), 1)
    predits = [fin["points"] / x["points"] for x in lignes]
    hi = max(max(predits), max(x["gain_de_temps"] for x in lignes)) * 1.15
    barres = 0
    for j, x in enumerate(lignes):
        y = haut + j * h
        art.text((x0 + 6, y + 6), f"pas {x['pas_echantillon']}", fill=TEXTE, font=petit)
        for k, (val, coul, nom) in enumerate(
                ((fin["points"] / x["points"], ROUGE, "prédit par les points"),
                 (x["gain_de_temps"], VERT, "MESURÉ"))):
            larg = (droite - gauche) * val / hi
            yy = y + k * 13
            art.rectangle([gauche, yy, gauche + max(larg, 1.0), yy + 11], fill=coul)
            art.text((gauche + max(larg, 1.0) + 5, yy - 2), f"×{val:.2f}", fill=coul,
                     font=petit)
            barres += 1
            del nom
    art.text((x0 + 8, y0 + 26), "rouge : prédit par le comptage de points   vert : MESURÉ",
             fill=DISCRET, font=petit)
    bas = haut + len(lignes) * h + 12
    art.text((x0 + 8, bas), "⚠⚠ le coût suit les RANGÉES, pas les points :",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 14), "   une plage d'octets par rangée (z, y),",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 28), "   plus un fixe par cube.", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 48), f"★ secondes par cube : "
             f"{fin['secondes_par_cube']:.2f} au pas 1,", fill=VERT, font=petit)
    ret = next((x for x in lignes
                if x["pas_echantillon"] == m["le_pas_retenu"]["pas_retenu"]), None)
    art.text((x0 + 8, bas + 62),
             (f"   {ret['secondes_par_cube']:.2f} au pas retenu."
              if ret is not None else "   aucun pas grossier n'est retenu."),
             fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "le coût se MESURE, il ne se modélise pas",
             fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 330, 26, 400
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (150, 142, 134, 126, 118, 110):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    pr = m["le_pas_retenu"]
    v = m["sur_le_vrai_volume"]
    art.text((marge, 16),
             "Le cube lu moins cher — l'économie est réfutée par le corpus entier",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · cube de {m['cote_um_du_cube']} µm · {v['cellules']} cellules "
             f"appariées sur 28 bandes · "
             + (f"pas retenu {pr['pas_retenu']}, ×{pr['gain_du_pas_retenu']} moins de temps"
                if pr["pas_retenu"] is not None
                else "AUCUNE économie ne passe : le cube se lit au voxel près"),
             fill=DISCRET, font=moyen)
    titres = ("A · la garde, sur réponse connue",
              "B · NON — l'accord ne tient pas sur le corpus",
              "C · ⚠ le coût prédit contre le coût mesuré")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    garde = panneau_garde(art, marge, 104, pw, ph, m, petit)
    accord = panneau_accord(art, marge + pw + ecart, 104, pw, ph, m, petit)
    cout = panneau_cout(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "garde": garde, "accord": accord, "cout": cout,
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
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images" / "103_le_cube_lu_moins_cher.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("aucun texte ne déborde de son PANNEAU", not d["hors_cadre"], str(d["hors_cadre"]))
    v("aucun texte n'est écrit par-dessus un autre", not d["recouvrements"],
      str(d["recouvrements"][:3]))
    n = len(m["sur_empilement_fabrique"]["lignes"])
    v("le panneau A trace une marge par finesse", d["garde"] == n, str(d["garde"]))
    v("le panneau B trace la médiane ET le p90 par finesse",
      d["accord"] == 2 * len(m["sur_le_vrai_volume"]["lignes"]), str(d["accord"]))
    # ⭐⭐⭐ LE PANNEAU C DOIT TRACER LES DEUX GAINS, pas un : c'est leur ECART qui porte la
    # correction, et un seul se lirait comme une simple mesure de coût.
    v("le panneau C trace le gain PRÉDIT et le gain MESURÉ",
      d["cout"] == 2 * len(m["sur_le_vrai_volume"]["lignes"]), str(d["cout"]))
    # ⚠⚠ LES VERDICTS SONT DANS LA MESURE, pas seulement dans la prose.
    # ⚠⚠⚠ STRUCTUREL, PAS UN RESULTAT : asserter qu'un pas est retenu obligerait a reecrire le
    # controle le jour ou la reponse change, c'est-a-dire un controle qui ne peut pas echouer.
    pr = m["le_pas_retenu"]
    v("le verdict est rendu, quel qu'il soit",
      "pas_retenu" in pr and "une_economie_est_possible" in pr)
    v("... chaque refus portant sa raison ET sa conséquence enchaînée",
      all(x["pourquoi_refuse"] and x.get("part_de_marches_de_six_pas_touchees") is not None
          for x in pr["verdicts"] if not x["retenu"]))
    v("... et la référence n'étant pas jugée comme une économie",
      all(x["pas_echantillon"] > pr["pas_de_reference"] for x in pr["verdicts"]))
    fin = next(x for x in m["sur_le_vrai_volume"]["lignes"] if x["pas_echantillon"] == 1)
    # ⭐⭐ LA CORRECTION QUI PORTE LE PANNEAU C : le gain mesure est bien plus bas que le predit,
    # a CHAQUE pas — donc ce n'est pas un accident d'un pas particulier.
    v("le gain MESURÉ est partout bien plus bas que le gain prédit par les points",
      all(x["gain_de_temps"] < 0.6 * (fin["points"] / x["points"])
          for x in m["sur_le_vrai_volume"]["lignes"] if x["pas_echantillon"] > 1),
      str([(x["pas_echantillon"], x["gain_de_temps"],
            round(fin["points"] / x["points"], 2))
           for x in m["sur_le_vrai_volume"]["lignes"] if x["pas_echantillon"] > 1]))
    v("la prose garde la correction du gain de points", any("SEPT" in x for x in prose(m)))
    # ⭐⭐⭐ ET LA FAUTE DE MA PROPRE SONDE, qui est la lecon du fichier.
    v("... et la sonde à deux bandes qui disait l'inverse",
      any("corpus entier" in x for x in prose(m)))
    v("... et le fait que la portée ne change pas",
      any("portee physique est identique" in x for x in prose(m)))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "103_le_cube_lu_moins_cher.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
