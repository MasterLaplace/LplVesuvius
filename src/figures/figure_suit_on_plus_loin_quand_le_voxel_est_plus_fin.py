"""Suit-on plus loin quand le voxel est plus fin ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle qui décide de tout le
reste : sur des crêtes dont la longueur physique est posée, le suiveur rend la même longueur en
micromètres aux deux résolutions — il mesure donc la matière et non sa propre résolution. En haut à
droite, le rouleau aux deux résolutions, EN MICROMÈTRES. En bas à gauche, ce que l'exactitude achète
une fois payé ce qu'elle achète sur du mélange. En bas à droite, la seule comparaison qui compte : la
longueur suivie contre le pas entre deux feuilles.

  uv run python src/figures/figure_suit_on_plus_loin_quand_le_voxel_est_plus_fin.py \\
      --json docs/mesures/suit_on_plus_loin_quand_le_voxel_est_plus_fin.json \\
      --sortie docs/images/186_suit_on_plus_loin_quand_le_voxel_est_plus_fin.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 ». Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `suit_on_plus_loin_quand_le_voxel_est_plus_fin.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'INVARIANCE EST ROUGE. Si le suiveur ne rend pas la même longueur en
    micromètres sur de la matière construite aux deux résolutions, il compte sa propre résolution et
    aucun gain du rouleau n'est interprétable — c'est le précédent de `181`, où rien n'a été publié
    pendant que le contrôle était rouge.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_segments", "les_etalons", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("linvariance", {}).get("le_suiveur_mesure_la_matiere"):
        raise ValueError(f"{chemin} : l'invariance est rouge, le suiveur mesure sa résolution")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if v.get("la_longueur_croit_avec_la_resolution"):
        queue = "la longueur suivable CROÎT avec la résolution"
    elif v.get("la_longueur_est_bornee_par_la_matiere"):
        queue = "la longueur suivable est BORNÉE PAR LA MATIÈRE"
    else:
        queue = "la réponse n'est pas rendue"
    return f"Suit-on plus loin quand le voxel est plus fin ? — {queue}"


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    v = d["le_verdict"]
    inv = v["linvariance"]
    vf, vg = float(v["voxel_fin_um"]), float(v["voxel_grossier_um"])
    pas_um = float(v["le_pas_entre_deux_feuilles_um"])
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46, f"champ commun {_fr(d['champ_commun_um'], 1)} µm aux deux résolutions · "
                   f"{d['departs_par_couche']} départs par couche · {d['couches_par_chunk']} couches "
                   f"par chunk · {v['chunks_fin']} champs fins · {v['chunks_grossier']} grossiers · "
                   f"voxels {_fr(vf, 3)} et {_fr(vg, 1)} µm", petit, GRIS)

    # ---- panneau 1 : l'invariance, le contrôle qui décide
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'invariance — le suiveur mesure-t-il la matière ou sa résolution ?",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "crête construite", petit, GRIS)
    ecrire(x0 + 190, y0 + 10, f"lue à {_fr(vg, 1)} µm", petit, CONTRE)
    ecrire(x0 + 350, y0 + 10, f"lue à {_fr(vf, 3)} µm", petit, ALERTE)
    ecrire(x0 + 510, y0 + 10, "écart", petit, ENCRE)
    etg = d["les_etalons"][str(vg)]["barreaux"]
    etf = d["les_etalons"][str(vf)]["barreaux"]
    hautc = max([float(b["longueur_construite_um"]) for b in etg]
                + [float(b["le_long_glouton_um"] or 0.0) for b in etg + etf]) * 1.2
    # ⚠⚠ L'ÉCART EST LU, PAS RECALCULÉ : une figure qui soustrairait elle-même deux valeurs
    # publierait un nombre sans producteur, et sa soustraction pourrait cesser d'être celle que la
    # mesure a faite.
    ecarts = inv.get("ecarts_par_barreau_glouton_um") or []
    for k, (bg, bf) in enumerate(zip(etg, etf)):
        yy = y0 + 34 + k * 44
        ecrire(x0 + 14, yy, f"{_fr(bg['longueur_construite_um'], 2)} µm", 0, ENCRE)
        barre(x0 + 14, yy + 16, 150, float(bg["longueur_construite_um"]) / hautc, 7, GRIS)
        ecrire(x0 + 190, yy, f"{_fr(bg['le_long_glouton_um'], 2)} µm", 0, CONTRE)
        barre(x0 + 190, yy + 16, 140, float(bg["le_long_glouton_um"] or 0.0) / hautc, 7, CONTRE)
        ecrire(x0 + 350, yy, f"{_fr(bf['le_long_glouton_um'], 2)} µm", 0, ALERTE)
        barre(x0 + 350, yy + 16, 140, float(bf["le_long_glouton_um"] or 0.0) / hautc, 7, ALERTE)
        ecrire(x0 + 510, yy, f"{_fr(ecarts[k] if k < len(ecarts) else None, 3)} µm", 0, ENCRE)
    ecrire(x0 + 14, y0 + 174,
           f"★ écart maximal {_fr(inv['ecart_maximal_entre_resolutions_um'], 3)} µm, pour une marche "
           f"d'échelle de {_fr(inv['marche_de_lechelle_um'], 2)} µm :", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 198,
           "     le suiveur distingue mieux deux longueurs que deux résolutions.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 226,
           "⚠⚠ La tolérance n'est pas choisie : c'est l'écart entre deux barreaux de l'échelle,",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 242,
           "et l'échelle est dérivée du pas entre deux feuilles, la distance qui décide.", petit,
           GRIS)

    # ---- panneau 2 : le rouleau aux deux résolutions
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau, aux deux résolutions — EN MICROMÈTRES", moyen, ENCRE)
    hautr = max([pas_um]
                + [float(v.get(f"{q}_glouton_um_{e}") or 0.0)
                   for q in ("le_long", "en_travers", "melangee")
                   for e in ("fin", "grossier")]) * 1.15
    for k, (nom, cle, coul) in enumerate(
            (("le long des fibres", "le_long", ALERTE),
             ("en travers", "en_travers", CONTRE),
             ("sur l'image mélangée", "melangee", GRIS))):
        yy = y0 + 14 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        a = v.get(f"{cle}_glouton_um_grossier")
        b = v.get(f"{cle}_glouton_um_fin")
        ecrire(x0 + 170, yy, f"{_fr(vg, 1)} µm : {_fr(a, 2)} µm", 0, coul)
        barre(x0 + 170, yy + 15, 170, float(a or 0.0) / hautr, 6, coul)
        ecrire(x0 + 360, yy, f"{_fr(vf, 3)} µm : {_fr(b, 2)} µm", 0, coul)
        barre(x0 + 360, yy + 15, 170, float(b or 0.0) / hautr, 6, coul)
    ecrire(x0 + 14, y0 + 122, "apparié par segment :", petit, GRIS)
    ecrire(x0 + 200, y0 + 122, f"à {_fr(vg, 1)} µm", petit, CONTRE)
    ecrire(x0 + 300, y0 + 122, f"à {_fr(vf, 3)} µm", petit, ALERTE)
    ecrire(x0 + 410, y0 + 122, "gain", petit, ENCRE)
    for k, x in enumerate(v.get("les_segments_apparies", [])):
        yy = y0 + 142 + k * 18
        ecrire(x0 + 14, yy, x["segment"], 0, ENCRE)
        ecrire(x0 + 200, yy, f"{_fr(x['um_grossier'], 2)}", 0, CONTRE)
        ecrire(x0 + 300, yy, f"{_fr(x['um_fin'], 2)}", 0, ALERTE)
        ecrire(x0 + 410, yy, f"{'+' if x['gain_um'] > 0 else ''}{_fr(x['gain_um'], 2)} µm "
                             f"({_fr(x['gain_fois'], 4)})", 0,
               BON if x["gain_um"] > 0 else ALERTE)
    coul_v = BON if v.get("la_longueur_suit_la_resolution") else ALERTE
    signe = "★" if v.get("la_longueur_suit_la_resolution") else "✗"
    ecrire(x0 + 14, y0 + 200,
           f"{signe} médiane des gains appariés {_fr(v['le_gain_apparie_um'], 2)} µm · "
           f"{v['segments_ou_la_longueur_croit']} segment sur "
           f"{v['segments_apparies']} croît", moyen, coul_v)
    ecrire(x0 + 14, y0 + 222,
           f"     et le meilleur gagne {_fr(v['le_meilleur_gain_apparie_fois'], 4)} fois pendant "
           f"que le voxel", moyen, coul_v)
    ecrire(x0 + 14, y0 + 240,
           f"     devient {_fr(v['le_voxel_est_plus_fin_fois'], 4)} fois plus fin.", moyen, coul_v)

    # ---- panneau 3 : ce que l'exactitude achète
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la marche gloutonne contre l'optimum exact", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10,
           "⚠⚠ Optimiser allonge la suite sur N'IMPORTE QUELLE image : ce que l'exactitude", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 26,
           "achète est son EXCÉDENT sur la même image mélangée, jamais sa longueur brute.", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 54, "règle", petit, GRIS)
    ecrire(x0 + 150, y0 + 54, "le long", petit, ALERTE)
    ecrire(x0 + 280, y0 + 54, "mélangée", petit, GRIS)
    ecrire(x0 + 410, y0 + 54, "excédent", petit, ENCRE)
    haute = max([abs(float(v.get(f"lexcedent_sur_le_melange_{r}_um_{e}") or 0.0))
                 for r in ("glouton", "au_mieux") for e in ("fin", "grossier")]
                + [float(v.get(f"le_long_{r}_um_{e}") or 0.0)
                   for r in ("glouton", "au_mieux") for e in ("fin", "grossier")]) * 1.15
    k = 0
    for etiquette, vx in (("grossier", vg), ("fin", vf)):
        for regle, nom in (("glouton", "gloutonne"), ("au_mieux", "exacte")):
            yy = y0 + 78 + k * 36
            k += 1
            ecrire(x0 + 14, yy, f"{_fr(vx, 3)} µm · {nom}", 0, ENCRE)
            ecrire(x0 + 150, yy, f"{_fr(v.get(f'le_long_{regle}_um_{etiquette}'), 1)}", 0, ALERTE)
            ecrire(x0 + 280, yy, f"{_fr(v.get(f'melangee_{regle}_um_{etiquette}'), 1)}", 0, GRIS)
            ex = v.get(f"lexcedent_sur_le_melange_{regle}_um_{etiquette}")
            ecrire(x0 + 410, yy, f"{_fr(ex, 2)} µm", 0, ENCRE)
            barre(x0 + 480, yy + 2, 120, float(ex or 0.0) / haute, 9,
                  BON if (ex or 0.0) > 0 else ALERTE)
    ecrire(x0 + 14, y0 + 230,
           f"{'★' if v.get('lexactitude_achete_quelque_chose') else '✗'} l'exactitude achète "
           f"{_fr(v['ce_que_lexactitude_achete_um'], 2)} µm d'excédent :", moyen,
           ENCRE if v.get("lexactitude_achete_quelque_chose") else ALERTE)
    ecrire(x0 + 14, y0 + 252,
           "     la restriction gloutonne EST ce qui rend la lecture spécifique.", moyen,
           ENCRE if v.get("lexactitude_achete_quelque_chose") else ALERTE)

    # ---- panneau 4 : la comparaison qui compte
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la seule comparaison qui compte pour le graal", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 16,
           "Le prix demande de suivre les fibres SANS SAUTER DE FEUILLE : la longueur", petit, ENCRE)
    ecrire(x0 + 14, y0 + 32, "suivable doit franchir la distance entre deux feuilles.", petit, ENCRE)
    hautp = max(pas_um, float(v.get("le_long_glouton_um_fin") or 0.0),
                float(v.get("le_long_glouton_um_maximal_fin") or 0.0)) * 1.15
    for k, (nom, val, coul) in enumerate(
            # ⚠⚠ LA LECTURE « AU MIEUX » EST GRISE ET DITE NON PAYÉE : elle est la plus longue et
            # serait lue comme la meilleure, alors que l'optimum exact atteint presque la même
            # longueur sur du MÉLANGE — la colorer comme un succès inviterait la conclusion inverse
            # de celle que le panneau d'à côté démontre.
            ((f"suivi à {_fr(vg, 1)} µm", v.get("le_long_glouton_um_grossier"), CONTRE),
             (f"suivi à {_fr(vf, 3)} µm", v.get("le_long_glouton_um_fin"), ALERTE),
             (f"au mieux à {_fr(vf, 3)} µm", v.get("le_long_au_mieux_um_fin"), GRIS),
             ("le pas entre deux feuilles", pas_um, ENCRE))):
        yy = y0 + 60 + k * 30
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 190, yy, f"{_fr(val, 2)} µm", 0, coul)
        barre(x0 + 280, yy + 2, 270, float(val or 0.0) / hautp, 11, coul)
    ecrire(x0 + 14, y0 + 190,
           f"{'★' if v.get('on_franchit_une_feuille_au_voxel_fin') else '✗'} on "
           f"{'franchit' if v.get('on_franchit_une_feuille_au_voxel_fin') else 'ne franchit pas'} "
           f"une feuille au voxel fin.", moyen,
           BON if v.get("on_franchit_une_feuille_au_voxel_fin") else ALERTE)
    ecrire(x0 + 14, y0 + 218,
           f"⚠ La plus longue crête suivie atteint pourtant "
           f"{_fr(v.get('le_long_glouton_um_maximal_fin'), 1)} µm, et", petit, GRIS)
    ecrire(x0 + 14, y0 + 234,
           f"une part de {_fr(v.get('part_qui_franchit_glouton_fin'), 4)} des départs franchit "
           f"déjà une feuille", petit, GRIS)
    ecrire(x0 + 14, y0 + 250,
           f"(contre {_fr(v.get('part_qui_franchit_glouton_grossier'), 4)} au voxel de la "
           f"campagne) : la médiane non. ⚠ « au mieux » n'est PAS payé.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  LE CONTRÔLE QUI DÉCIDE EST VERT : sur des crêtes dont la longueur physique est "
           f"posée, les deux résolutions s'accordent à {_fr(inv['ecart_maximal_entre_resolutions_um'], 3)} µm "
           f"près,", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     pour une marche d'échelle de {_fr(inv['marche_de_lechelle_um'], 2)} µm. Le "
           "suiveur mesure donc la MATIÈRE, et non sa propre résolution — sans quoi rien de ce qui "
           "suit ne serait lisible.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  ET LA RÉPONSE EST NON, DANS LE MÊME CHAMP DE {_fr(d['champ_commun_um'], 1)} "
           f"µm : médiane des gains appariés {_fr(v['le_gain_apparie_um'], 2)} µm, "
           f"{v['segments_ou_la_longueur_croit']} segment sur {v['segments_apparies']} croît, et le "
           f"meilleur", moyen, coul_v)
    ecrire(78, y + 106,
           f"     gagne {_fr(v['le_meilleur_gain_apparie_fois'], 4)} fois pendant que le voxel "
           f"devient {_fr(v['le_voxel_est_plus_fin_fois'], 4)} fois plus fin. Le rouleau porte "
           f"pourtant encore des crêtes suivables à {_fr(vf, 3)} µm "
           f"({_fr(v['le_long_glouton_um_fin'], 2)} contre "
           f"{_fr(v['en_travers_glouton_um_fin'], 2)} en travers).", moyen, coul_v)
    ecrire(78, y + 138,
           f"{'★' if v.get('lexactitude_achete_quelque_chose') else '✗'}  ET LEVER LA MARCHE "
           f"GLOUTONNE NE DONNE RIEN : l'optimum exact ajoute "
           f"{_fr(v['ce_que_lexactitude_achete_um'], 2)} µm d'excédent sur le mélange. Optimiser "
           f"allonge aussi le bruit —", moyen,
           BON if v.get("lexactitude_achete_quelque_chose") else ALERTE)
    ecrire(78, y + 166,
           f"     la restriction gloutonne EST ce qui rend la lecture spécifique. ⚠ Et "
           f"{_fr(v.get('part_qui_franchit_glouton_grossier'), 4)} des départs franchissent déjà "
           f"une feuille au voxel de la campagne : ce sont ces fibres-là", moyen, ENCRE)
    ecrire(78, y + 194,
           f"     qu'un transfert pourrait ancrer, pas la médiane. ⚠⚠ La fenêtre fine est une "
           f"MOSAÏQUE rognée au champ grossier, et son vide vaut "
           f"{_fr(v.get('part_vide_fin'), 4)} contre {_fr(v.get('part_vide_grossier'), 4)} : le "
           "recul n'est pas un trou.", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4)) == ("90", "173", "0,4855"),
      f"{(_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4))}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:200])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:200])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("★★★★ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:200])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    vv = d["le_verdict"]
    vf, vg = str(vv["voxel_fin_um"]), str(vv["voxel_grossier_um"])

    # ★★★★ LES DEUX LONGUEURS DU ROULEAU SONT LUES DE PLUSIEURS COTES : c'est la comparaison
    # que la tranche existe pour publier, et une seule mention la rendrait invisible.
    for cle, val in (("le_long_glouton_um_grossier", 61.75), ("le_long_glouton_um_fin", 97.125)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, 2) in t)
        v(f"★★★★ {cle} est lue de PLUSIEURS côtés", n >= 2, f"{n} mentions")

    # ★★★★ LE GAIN EST LU EN MICROMETRES, ET DES DEUX COTES.
    faux = copy.deepcopy(d)
    # ⚠⚠ LA VALEUR DE SONDE DOIT SURVIVRE A L'ARRONDI DU RENDU : la figure ecrit deux decimales,
    # donc une sonde a trois n'apparaitrait nulle part et la verification serait rouge pour une
    # raison de mise en forme et non de contenu.
    faux["le_verdict"]["le_gain_apparie_um"] = 41.62
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p3 if _fr(41.62, 2) in t)
    v("★★★★ le gain apparié en micromètres est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ L'INVARIANCE EST LUE : sans elle, aucun chiffre du rouleau n'est interpretable, et une
    # figure qui ne l'affiche pas laisserait croire qu'on a mesure la matiere.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["linvariance"]["ecart_maximal_entre_resolutions_um"] = 3.875
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p4 if "3,875" in t)
    v("★★★★ l'écart entre résolutions est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET L'ÉCART DE CHAQUE BARREAU EST LU DANS LA MESURE, pas recalculé par la figure : une
    # soustraction faite ici serait un second producteur du même nombre.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["linvariance"]["ecarts_par_barreau_glouton_um"] = [7.111, 7.222, 7.333]
    _c, p4b, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ l'écart de chaque barreau est LU et non recalculé",
      all(any(m in t for _x, _y, t, _f in p4b) for m in ("7,111", "7,222", "7,333")),
      str([m for m in ("7,111", "7,222", "7,333")
           if not any(m in t for _x, _y, t, _f in p4b)]))

    # ★★★★ ET UNE INVARIANCE ROUGE FAIT REFUSER LA MESURE, jamais dessiner un gain qui n'en est pas.
    rouge = copy.deepcopy(d)
    rouge["le_verdict"]["linvariance"]["le_suiveur_mesure_la_matiere"] = False
    refuse = False
    try:
        import tempfile  # noqa: PLC0415
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(rouge, fh, ensure_ascii=False)
            tmp = Path(fh.name)
        lire(tmp)
    except ValueError:
        refuse = True
    finally:
        tmp.unlink(missing_ok=True)
    v("★★★★ une invariance rouge fait REFUSER la mesure", refuse)

    # ★★★ CHAQUE BARREAU DE L'ECHELLE CONSTRUITE EST DESSINE, aux DEUX resolutions : une echelle
    # dont il manque un barreau ne montre plus que la longueur rendue SUIT la longueur posee.
    for k in range(len(d["les_etalons"][vg]["barreaux"])):
        faux = copy.deepcopy(d)
        faux["les_etalons"][vg]["barreaux"][k]["le_long_glouton_um"] = 11.0 + k
        faux["les_etalons"][vf]["barreaux"][k]["le_long_glouton_um"] = 21.0 + k
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        a = sum(1 for _x, _y, t, _f in p5 if _fr(11.0 + k, 2) in t)
        b = sum(1 for _x, _y, t, _f in p5 if _fr(21.0 + k, 2) in t)
        v(f"★★★ le barreau {k} est dessiné aux deux résolutions", a >= 1 and b >= 1, f"{a} / {b}")

    # ★★★★ LES DEUX BRANCHES DU TITRE SONT EXERCEES : un titre qui suit la mesure doit pouvoir
    # dire les deux choses, sinon il est un verdict ecrit d'avance.
    croit = copy.deepcopy(d)
    croit["le_verdict"]["la_longueur_croit_avec_la_resolution"] = True
    croit["le_verdict"]["la_longueur_est_bornee_par_la_matiere"] = False
    borne = copy.deepcopy(d)
    borne["le_verdict"]["la_longueur_croit_avec_la_resolution"] = False
    borne["le_verdict"]["la_longueur_est_bornee_par_la_matiere"] = True
    v("★★★★ le titre suit la mesure dans les deux sens",
      "CROÎT" in le_titre(croit["le_verdict"])
      and "BORNÉE" in le_titre(borne["le_verdict"])
      and le_titre(croit["le_verdict"]) != le_titre(borne["le_verdict"]),
      f"{le_titre(croit['le_verdict'])} | {le_titre(borne['le_verdict'])}")
    for nom, faux in (("croît", croit), ("bornée", borne)):
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {nom} »",
          not textes_debordants(p6, 1360) and not textes_hors_cadre(p6, cadres)
          and not textes_qui_se_recouvrent(p6))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ÉCHECS, PAS UN LITTÉRAL : un `return 0` après le verdict jette
    # ce que la batterie vient de compter.
    nom = "figure_suit_on_plus_loin_quand_le_voxel_est_plus_fin.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "suit_on_plus_loin_quand_le_voxel_est_plus_fin.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "186_suit_on_plus_loin_quand_le_voxel_est_plus_fin.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
