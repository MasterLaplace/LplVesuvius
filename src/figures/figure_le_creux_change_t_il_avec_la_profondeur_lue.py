"""Le creux change-t-il avec la profondeur lue ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, l'erreur commune à un chunk en fonction de
la profondeur lue, avec la valeur que `205` avait isolée tracée en travers : si elle bouge, la cause
est bien « quelle frontière » ; si elle ne bouge pas, ce n'est pas ça. En bas à gauche, la fenêtre
effective — la prémisse de `R4-P54` réfutée par un chiffre que `179` publiait déjà. Au centre,
l'épreuve d'accord et son nul par permutation. À droite, l'étalon.

  uv run python src/figures/figure_le_creux_change_t_il_avec_la_profondeur_lue.py \\
      --json docs/mesures/le_creux_change_t_il_avec_la_profondeur_lue.json \\
      --sortie docs/images/206_le_creux_change_t_il_avec_la_profondeur_lue.png
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
PROFOND = (128, 86, 124)


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
    """Le JSON de `le_creux_change_t_il_avec_la_profondeur_lue.py`.

    ⚠⚠⚠ REFUSE UNE MESURE SANS FENÊTRE EFFECTIVE, UNE DONT L'ÉTALON NE SÉPARE PAS, UNE QUI DÉCLARE
    PLUS D'UNE ÉPREUVE SANS EN DIVISER LA GARANTIE, ET UNE DONT UN BARREAU N'A PAS SON COMPTE DE
    CHUNKS LISIBLES : `200` a payé qu'une erreur qui baisse peut n'être que l'effet d'avoir jeté les
    chunks difficiles.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_courbe", "lepreuve", "le_verdict", "letalon",
                "lechelle_des_profondeurs", "la_fenetre_effective"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_courbe", "lepreuve", "le_verdict", "letalon",
                "lechelle_des_profondeurs", "la_fenetre_effective"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    for b in d["la_courbe"]["les_barreaux"]:
        if b.get("les_chunks_lisibles") is None:
            raise ValueError(f"{chemin} : le barreau {b.get('la_profondeur')} n'a pas son compte "
                             f"de chunks lisibles")
    if d["le_verdict"].get("lerreur_que_205_a_isolee_en_voxels") is None:
        raise ValueError(f"{chemin} : l'erreur que `205` a isolée est absente")
    # ⚠⚠⚠ SANS CETTE LISTE, LA FIGURE ATTACHE LES DEUX ERREURS A LA PREMIERE ET A LA DERNIERE
    # PROFONDEUR DE L'ECHELLE, alors que la plus courte n'en rend pas forcement une. Defaut vu en
    # REGARDANT l'image : « 11,651 voxels à 36 couches » là où ce nombre est celui de 72.
    if len(d["la_courbe"].get("les_profondeurs_qui_rendent_une_erreur") or []) < 2:
        raise ValueError(f"{chemin} : moins de deux profondeurs rendent une erreur commune")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if not ve.get("elles_lisent_la_meme_frontiere"):
        return ("Le creux change-t-il avec la profondeur ? — les deux fenêtres ne lisent pas la "
                "même frontière")
    r = ve.get("le_rapport_des_deux_erreurs")
    if r is None:
        return "Le creux change-t-il avec la profondeur ? — une seule profondeur rend une erreur"
    if float(r) < 1.0:
        return ("Le creux change-t-il avec la profondeur ? — oui, l'erreur commune tombe quand la "
                "fenêtre raccourcit")
    if float(r) > 1.0:
        return ("Le creux change-t-il avec la profondeur ? — oui, mais dans l'autre sens : "
                "raccourcir empire")
    return "Le creux change-t-il avec la profondeur ? — l'erreur commune ne bouge pas"


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

    lg, cb, ep = d["la_ligne"], d["la_courbe"], d["lepreuve"]
    ve, e, ec = d["le_verdict"], d["letalon"], d["lechelle_des_profondeurs"]
    fe = d["la_fenetre_effective"]
    bar = cb["les_barreaux"]
    ref205 = float(ve["lerreur_que_205_a_isolee_en_voxels"])
    # ⚠⚠ LES DEUX PROFONDEURS VIENNENT DE LA LISTE QUE LE PRODUCTEUR PUBLIE, jamais des deux bouts
    # de l'echelle : la plus courte profondeur lue n'est pas forcement celle qui rend une erreur.
    rend = cb["les_profondeurs_qui_rendent_une_erreur"]
    d_courte, d_longue = int(rend[0]), int(rend[-1])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · cube de {lg['les_couches_du_cube']} couches · "
           f"{lg['les_sous_colonnes']} sous-colonnes · {d['les_coutures_voisines']} coutures · "
           f"une seule épreuve, garantie {_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : la courbe par profondeur
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "ce que chaque profondeur rend — et ce que `205` avait isolé", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 14, pw - 430, 206
    valeurs = [float(x[c]) for x in bar
               for c in ("lalea_en_voxels", "la_dispersion_du_pas_en_voxels",
                         "lerreur_commune_en_voxels") if x.get(c) is not None]
    haut = max(valeurs + [ref205, 1.0]) * 1.1
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 42, yy - 6, _fr(haut * (1.0 - k / 4.0), 1), 0, GRIS)
    yr = gy0 + gh * (1.0 - ref205 / haut)
    for s in range(0, int(gw), 12):
        art.line([gx0 + s, yr, gx0 + min(s + 6, int(gw)), yr], fill=PROFOND, width=2)
    traits.append((gx0, yr, gx0 + gw))
    ecrire(gx0 + 6, yr - 16,
           f"l'erreur commune que `205` a isolée : {_fr(ref205, 4)} vx", 0, PROFOND)
    n = max(1, len(bar) - 1)
    for cle, coul in (("la_dispersion_du_pas_en_voxels", CONTRE),
                      ("lerreur_commune_en_voxels", ALERTE),
                      ("lalea_en_voxels", BON)):
        prec = None
        for i, b in enumerate(bar):
            val = b.get(cle)
            if val is None:
                prec = None
                continue
            px = gx0 + gw * i / n
            py = gy0 + gh * (1.0 - float(val) / haut)
            if prec is not None:
                art.line([prec[0], prec[1], px, py], fill=coul, width=2)
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            points.append((px, py))
            prec = (px, py)
    for i, b in enumerate(bar):
        ecrire(gx0 + gw * i / n - 12, gy0 + gh + 8,
               f"{b['la_profondeur']}", 0, GRIS)
        ecrire(gx0 + gw * i / n - 24, gy0 + gh + 22,
               f"{b['les_chunks_lisibles']} lus", 0, GRIS)
    ecrire(gx0 + gw / 2 - 74, gy0 + gh + 40, "couches lues, et chunks lisibles", 0, GRIS)
    lx = x0 + pw - 322
    for k, (nom, coul) in enumerate(
            (("la DISPERSION du pas", CONTRE), ("l'ERREUR COMMUNE", ALERTE),
             ("l'ALÉA entre sous-colonnes", BON),
             ("ce que `205` avait isolé", PROFOND))):
        art.rectangle([lx, y0 + 18 + k * 22, lx + 22, y0 + 26 + k * 22], fill=coul)
        ecrire(lx + 30, y0 + 16 + k * 22, nom, 0, coul)
    ecrire(lx, y0 + 118,
           f"erreur commune : {_fr(ve['lerreur_a_la_plus_courte_en_voxels'], 4)} voxels à",
           petit, ENCRE)
    ecrire(lx, y0 + 132,
           f"{d_courte} couches contre "
           f"{_fr(ve['lerreur_a_la_plus_longue_en_voxels'], 4)} à {d_longue},", petit, ENCRE)
    ecrire(lx, y0 + 146,
           f"soit un rapport de {_fr(ve['le_rapport_des_deux_erreurs'], 4)}.", petit, ENCRE)
    ecrire(lx, y0 + 170, "⚠⚠ LE COMPTE DE CHUNKS LISIBLES EST SOUS", petit, GRIS)
    ecrire(lx, y0 + 184, "chaque profondeur — le piège de `200` : une", petit, GRIS)
    ecrire(lx, y0 + 198, "erreur qui baisse peut n'être que l'effet", petit, GRIS)
    ecrire(lx, y0 + 212, "d'avoir jeté les chunks difficiles.", petit, GRIS)
    ecrire(lx, y0 + 236, "⚠ Comparer deux erreurs d'une profondeur à", petit, GRIS)
    ecrire(lx, y0 + 250, "l'autre est une DESCRIPTION : une seule", petit, GRIS)
    ecrire(lx, y0 + 264, "épreuve est déclarée, et c'est l'accord.", petit, GRIS)

    # ---- panneau 2 : la fenêtre effective
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la fenêtre VRAIE, transition comprise", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 12,
           f"transition de `179` : {_fr(fe['la_transition_de_179_en_voxels'], 4)} voxels",
           0, ENCRE)
    for k, f_ in enumerate(fe["les_fenetres"]):
        yy = y0 + 36 + k * 20
        ecrire(x0 + 12, yy, f"{f_['la_profondeur']} couches lues", 0, GRIS)
        ecrire(x0 + 180, yy,
               f"{_fr(f_['la_fenetre_effective_en_voxels'], 4)} vx", 0, ENCRE)
        ecrire(x0 + 300, yy, f"{_fr(f_['elle_vaut_le_pas_fois'], 4)} pas", 0, ENCRE)
    discrimine = bool(fe["la_geometrie_peut_elle_discriminer"])
    ecrire(x0 + 12, y0 + 128,
           f"{'★' if discrimine else '✗'} LA GÉOMÉTRIE PEUT DISCRIMINER : {discrimine}",
           moyen, BON if discrimine else ALERTE)
    ecrire(x0 + 12, y0 + 156,
           "⚠⚠⚠ C'est la prémisse de `R4-P54` réfutée par un", petit, GRIS)
    ecrire(x0 + 12, y0 + 170,
           "chiffre que `179` publiait déjà. La porte annonçait", petit, GRIS)
    ecrire(x0 + 12, y0 + 184,
           "qu'une fenêtre de moins d'un pli DEVAIT ne rien", petit, GRIS)
    ecrire(x0 + 12, y0 + 198,
           "rendre. Mais une frontière située jusqu'à une", petit, GRIS)
    ecrire(x0 + 12, y0 + 212,
           "transition HORS de la fenêtre incline encore la", petit, GRIS)
    ecrire(x0 + 12, y0 + 226,
           "cohérence DEDANS, donc aucune de ces fenêtres ne", petit, GRIS)
    ecrire(x0 + 12, y0 + 236, "peut être vide de frontière.", petit, GRIS)

    # ---- panneau 3 : l'épreuve
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve : la MÊME frontière, nul par permutation", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("profondeurs comparées",
             f"{ep['la_profondeur_courte']} et {ep['la_profondeur_longue']}"),
            ("chunks lus aux deux", f"{ep['les_chunks_lus_aux_deux']}"),
            ("écart médian replié", f"{_fr(ep['lecart_median_replie_en_voxels'], 4)} vx"),
            ("au mélange", f"{_fr(ep['lecart_median_des_melanges_en_voxels'], 4)} vx"),
            ("mélanges aussi bas",
             f"{ep['les_melanges_au_moins_aussi_bas']} sur {ep['les_tirages']}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 270, yy, val, 0, ENCRE)
    hautE = max(float(ep["lecart_median_des_melanges_en_voxels"]),
                float(ep["lecart_median_replie_en_voxels"]), 1.0) * 1.15
    barre(x0 + 12, y0 + 118, 372,
          float(ep["lecart_median_replie_en_voxels"]) / hautE, 10, BON)
    barre(x0 + 12, y0 + 134, 372,
          float(ep["lecart_median_des_melanges_en_voxels"]) / hautE, 10, GRIS)
    meme = bool(ep["elles_lisent_la_meme_frontiere"])
    ecrire(x0 + 12, y0 + 152,
           f"P = {_fr(ep['la_valeur_p'], 7)}", 0, ENCRE)
    ecrire(x0 + 12, y0 + 172,
           f"{'★' if meme else '✗'} ELLES LISENT LA MÊME FRONTIÈRE : {meme}", moyen,
           BON if meme else ALERTE)
    ecrire(x0 + 12, y0 + 196,
           "★ Le nul est une PERMUTATION, donc il ne suppose", petit, GRIS)
    ecrire(x0 + 12, y0 + 209,
           "aucune période : il apparie la lecture courte d'un", petit, GRIS)
    ecrire(x0 + 12, y0 + 222,
           "chunk à la lecture longue d'un AUTRE, et le repli", petit, GRIS)
    ecrire(x0 + 12, y0 + 235, "s'applique des deux côtés.", petit, GRIS)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — deux faces, sur réplicats", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("chunks par réplicat", f"{e['les_chunks_par_replicat']}"),
            ("tirages de l'épreuve", f"{e['les_tirages_de_lepreuve']}"),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("écart, face positive",
             f"{_fr(e['lecart_median_sur_la_face_positive_en_voxels'], 4)} vx"),
            ("écart, face négative",
             f"{_fr(e['lecart_median_sur_la_face_negative_en_voxels'], 4)} vx"),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 244, yy, val, 0, ENCRE)
    barre(x0 + 12, y0 + 140, 372, float(e["la_part_trouvee"]), 10, BON)
    ecrire(x0 + 12, y0 + 158,
           f"★ sépare : {e['letalon_separe']} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, BON)
    ecrire(x0 + 12, y0 + 182,
           "⚠⚠ Les deux comptes de tirages sont SÉPARÉS : celui", petit, GRIS)
    ecrire(x0 + 12, y0 + 196,
           "du lecteur de creux et celui du nul. Les confondre", petit, GRIS)
    ecrire(x0 + 12, y0 + 210,
           "plafonne la valeur p au premier des deux, donc rend", petit, GRIS)
    ecrire(x0 + 12, y0 + 224,
           "l'épreuve incapable de RÉUSSIR — et l'étalon accuse", petit, GRIS)
    ecrire(x0 + 12, y0 + 236, "alors le code au lieu du réglage.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{'★' if meme else '✗'}  LES DEUX FENÊTRES LISENT LA MÊME FRONTIÈRE : écart médian "
           f"replié {_fr(ep['lecart_median_replie_en_voxels'], 4)} voxels contre "
           f"{_fr(ep['lecart_median_des_melanges_en_voxels'], 4)} au mélange, "
           f"{ep['les_melanges_au_moins_aussi_bas']} sur {ep['les_tirages']} · P = "
           f"{_fr(ep['la_valeur_p'], 7)}.", moyen, BON if meme else ALERTE)
    ecrire(78, y + 46,
           f"     Sans cette garde, comparer les erreurs d'une profondeur à l'autre n'aurait "
           f"aucun sens : c'est une épreuve sur l'INSTRUMENT, pas un résultat de plus.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"⚠⚠⚠ ET LA PRÉMISSE DE `R4-P54` EST RÉFUTÉE PAR UN CHIFFRE DÉJÀ PUBLIÉ : la transition "
           f"de `179` vaut {_fr(fe['la_transition_de_179_en_voxels'], 4)} voxels, donc la fenêtre "
           f"effective la plus courte", moyen, GRIS)
    ecrire(78, y + 106,
           f"     vaut {_fr(fe['les_fenetres'][0]['la_fenetre_effective_en_voxels'], 4)} voxels = "
           f"{_fr(fe['les_fenetres'][0]['elle_vaut_le_pas_fois'], 4)} pas. Aucune de ces fenêtres "
           f"ne peut être vide de frontière, donc un compte de fenêtres lisibles ne pouvait rien "
           f"trancher.", moyen, GRIS)
    ecrire(78, y + 138,
           f"★  L'ERREUR COMMUNE PASSE DE "
           f"{_fr(ve['lerreur_a_la_plus_courte_en_voxels'], 4)} VOXELS À "
           f"{d_courte} COUCHES À "
           f"{_fr(ve['lerreur_a_la_plus_longue_en_voxels'], 4)} À {d_longue}, un "
           f"rapport de {_fr(ve['le_rapport_des_deux_erreurs'], 4)}, là où `205` en isolait "
           f"{_fr(ref205, 4)}.", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     Et le compte de chunks lisibles suit la fenêtre : "
           f"{' · '.join(str(x['les_chunks_lisibles']) + ' à ' + str(x['la_profondeur']) for x in bar)}"
           f" — publié à côté de l'erreur, jamais après.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ La comparaison des erreurs d'une profondeur à l'autre reste une DESCRIPTION : une "
           f"seule épreuve est déclarée, donc la garantie reste entière, et départager deux erreurs "
           f"dérivées demanderait un second nul.", petit, GRIS)

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

    import copy  # noqa: PLC0415

    def _refuse(base, out, casse):
        """Une mesure cassée de cette façon est-elle refusée par `lire` ?"""
        faux_ = copy.deepcopy(base)
        casse(faux_)
        tmp_ = out.with_name(out.stem + "_sonde.json")
        tmp_.write_text(json.dumps(faux_), encoding="utf-8")
        try:
            lire(tmp_)
            return False
        except ValueError:
            return True
        finally:
            tmp_.unlink(missing_ok=True)

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(36.0, 0), _fr(0.05, 2), _fr(14.9372, 4)) == ("36", "0,05", "14,9372"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(14.9372, 4))}")
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
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ★★★★ LES TROIS COURBES VIENNENT DE LA MESURE, BARREAU PAR BARREAU.
    for cle in ("lalea_en_voxels", "la_dispersion_du_pas_en_voxels",
                "lerreur_commune_en_voxels"):
        for k in (0, len(d["la_courbe"]["les_barreaux"]) - 1):
            faux = copy.deepcopy(d)
            if faux["la_courbe"]["les_barreaux"][k].get(cle) is None:
                continue
            faux["la_courbe"]["les_barreaux"][k][cle] = 3.3131
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            v(f"★★★★ le barreau {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ LA LIGNE DE `205` EST TRACEE DEPUIS LA MESURE, PAS POSEE DANS LA FIGURE.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["lerreur_que_205_a_isolee_en_voxels"] = 2.3456
    _c, _p, _cd, _pt, _b, tr_c = dessiner(faux, sortie)
    v("★★★★ la ligne de référence suit l'erreur que `205` a publiée",
      [round(y, 2) for _a, y, _b in tr_c] != [round(y, 2) for _a, y, _b in traits],
      f"{len(tr_c)} traits")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "lerreur_a_la_plus_courte_en_voxels"), 6.1616, 4, 2),
            (("le_verdict", "lerreur_a_la_plus_longue_en_voxels"), 8.1818, 4, 2),
            (("le_verdict", "le_rapport_des_deux_erreurs"), 0.8181, 4, 2),
            (("le_verdict", "lerreur_que_205_a_isolee_en_voxels"), 5.5151, 4, 2),
            (("lepreuve", "lecart_median_replie_en_voxels"), 7.4747, 4, 2),
            (("lepreuve", "lecart_median_des_melanges_en_voxels"), 9.6969, 4, 2),
            (("lepreuve", "la_valeur_p"), 0.0303, 4, 2),
            (("lepreuve", "les_chunks_lus_aux_deux"), 171, 0, 1),
            (("letalon", "les_faux"), 7, 0, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1),
            (("letalon", "lecart_median_sur_la_face_positive_en_voxels"), 1.3131, 4, 1),
            (("letalon", "lecart_median_sur_la_face_negative_en_voxels"), 2.1212, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    faux = copy.deepcopy(d)
    faux["la_fenetre_effective"]["la_transition_de_179_en_voxels"] = 41.4141
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la transition de `179` est lue autant de fois qu'il le faut",
      sum(1 for _x, _y, t, _f in p3 if _fr(41.4141, 4) in t) >= 2)
    dessiner(d, sortie)

    # ★★★★ LES DEUX ERREURS SONT ATTACHEES A LA PROFONDEUR QUI LES REND, PAS AUX BOUTS DE
    # L'ECHELLE — le defaut vu en REGARDANT l'image.
    faux = copy.deepcopy(d)
    faux["la_courbe"]["les_profondeurs_qui_rendent_une_erreur"] = [41, 42]
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la profondeur écrite à côté d'une erreur vient de la liste du producteur",
      sum(1 for _x, _y, t_, _f in p5 if "41" in t_) >= 2
      and sum(1 for _x, _y, t_, _f in p5 if "42" in t_) >= 2)
    v("★★★★ une mesure où moins de deux profondeurs rendent une erreur est refusée",
      _refuse(d, sortie,
              lambda x: x["la_courbe"].__setitem__(
                  "les_profondeurs_qui_rendent_une_erreur", [72])))
    dessiner(d, sortie)

    # ★★★★ LE COMPTE DE CHUNKS LISIBLES EST DESSINE, PAS SEULEMENT STOCKE.
    faux = copy.deepcopy(d)
    faux["la_courbe"]["les_barreaux"][0]["les_chunks_lisibles"] = 313
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de chunks lisibles d'un barreau est écrit sous sa profondeur",
      sum(1 for _x, _y, t, _f in p4 if "313" in t) >= 2)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES QUATRE ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elles_lisent_la_meme_frontiere"] = False
    v("★★★★ deux fenêtres qui ne s'accordent pas changent le titre",
      "ne lisent pas la même frontière" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["elles_lisent_la_meme_frontiere"] = True
    faux["le_verdict"]["le_rapport_des_deux_erreurs"] = 0.5
    v("★★★★ une erreur qui tombe avec la fenêtre le dit",
      "l'erreur commune tombe quand la fenêtre raccourcit" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["le_rapport_des_deux_erreurs"] = 1.5
    v("★★★★ une erreur qui monte le dit autrement",
      "raccourcir empire" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["le_rapport_des_deux_erreurs"] = 1.0
    v("★★★ une erreur qui ne bouge pas le dit aussi",
      "ne bouge pas" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_courbe"].__setitem__("decidable", False),
             "à la courbe indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["la_fenetre_effective"].__setitem__("decidable", False),
             "à la fenêtre effective indécidable"),
            (lambda x: x["lechelle_des_profondeurs"].__setitem__("decidable", False),
             "à l'échelle des profondeurs indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "les_chunks_lisibles", None),
             "dont un barreau n'a pas son compte de chunks lisibles"),
            (lambda x: x["le_verdict"].__setitem__(
                "lerreur_que_205_a_isolee_en_voxels", None),
             "sans l'erreur que `205` a isolée"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        faux = copy.deepcopy(d)
        casse(faux)
        tmp = sortie.with_name(sortie.stem + "_sonde.json")
        tmp.write_text(json.dumps(faux), encoding="utf-8")
        refuse = False
        try:
            lire(tmp)
        except ValueError:
            refuse = True
        v(f"une mesure {quoi} est refusée", refuse)
        tmp.unlink(missing_ok=True)
    dessiner(d, sortie)

    print(f"figure_le_creux_change_t_il_avec_la_profondeur_lue.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_creux_change_t_il_avec_la_profondeur_lue.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "206_le_creux_change_t_il_avec_la_profondeur_lue.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
