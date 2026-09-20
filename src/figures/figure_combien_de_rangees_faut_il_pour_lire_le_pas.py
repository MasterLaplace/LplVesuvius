"""Combien de rangées faut-il pour lire le pas ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, les courbes par compte de rangées :
l'aléa qui tombe, la dispersion du pas qui tombe moins vite, et la dérive qui apparaît entre les
deux — elle n'existe pas à deux rangées. En bas à gauche, l'épreuve et son nul d'un demi, démontré
plutôt que posé. Au centre, le contrôle croisé avec `202`. À droite, la portée et l'étalon.

  uv run python src/figures/figure_combien_de_rangees_faut_il_pour_lire_le_pas.py \\
      --json docs/mesures/combien_de_rangees_faut_il_pour_lire_le_pas.json \\
      --sortie docs/images/204_combien_de_rangees_faut_il_pour_lire_le_pas.png
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
    """Le JSON de `combien_de_rangees_faut_il_pour_lire_le_pas.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, UNE QUI DÉCLARE PLUS D'UNE ÉPREUVE SANS EN
    DIVISER LA GARANTIE, ET UNE DONT UN BARREAU N'A PAS LA DISPERSION DU PAS : `203` a payé qu'un
    critère aveugle à la dynamique récompense un instrument mort.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_courbe", "lepreuve", "le_verdict", "letalon", "la_portee"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_courbe", "lepreuve", "le_verdict", "letalon"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    for b in d["la_courbe"]["les_barreaux"]:
        for cle in ("lalea_en_voxels", "lalea_predit_en_voxels",
                    "la_dispersion_du_pas_en_voxels"):
            if b.get(cle) is None:
                raise ValueError(f"{chemin} : le barreau {b.get('les_rangees')} n'a pas {cle}")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if not ve.get("la_couture_porte_un_pas"):
        return "Combien de rangées faut-il ? — aucune : la couture ne porte aucun pas lisible"
    sb = ve.get("le_signal_sur_bruit_au_maximum")
    if sb is not None and float(sb) > 1.0:
        return (f"Combien de rangées faut-il ? — {ve['les_rangees_de_lepreuve']}, et le signal "
                f"passe enfin devant le bruit")
    return "Combien de rangées faut-il ? — le pas existe, mais le bruit le domine encore"


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
    po, ve, e = d["la_portee"], d["le_verdict"], d["letalon"]
    bar = cb["les_barreaux"]

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · {len(lg['les_rangees_lues'])} rangées de coupe "
           f"· bord {lg['la_largeur_du_bord']} colonnes · {d['les_coutures_voisines']} coutures · "
           f"une seule épreuve, garantie {_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : les courbes par compte de rangées
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "ce que gagne chaque rangée de plus — l'aléa tombe, la dérive apparaît", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 14, pw - 396, 210
    haut = max(max(x["la_dispersion_du_pas_en_voxels"] for x in bar),
               max(x["lalea_en_voxels"] for x in bar), 1.0) * 1.1
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 42, yy - 6, _fr(haut * (1.0 - k / 4.0), 1), 0, GRIS)
    n = max(1, len(bar) - 1)
    for cle, coul, pointille in (("la_dispersion_du_pas_en_voxels", BON, False),
                                 ("lalea_en_voxels", ALERTE, False),
                                 ("lalea_predit_en_voxels", GRIS, True),
                                 ("la_derive_en_voxels", CONTRE, False)):
        prec = None
        for i, b in enumerate(bar):
            val = b.get(cle)
            if val is None:
                prec = None
                continue
            px = gx0 + gw * i / n
            py = gy0 + gh * (1.0 - float(val) / haut)
            if prec is not None and not pointille:
                art.line([prec[0], prec[1], px, py], fill=coul, width=2)
            elif prec is not None:
                for s in range(0, 10, 2):
                    a_ = (prec[0] + (px - prec[0]) * s / 10.0,
                          prec[1] + (py - prec[1]) * s / 10.0)
                    b_ = (prec[0] + (px - prec[0]) * (s + 1) / 10.0,
                          prec[1] + (py - prec[1]) * (s + 1) / 10.0)
                    art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=1)
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            points.append((px, py))
            prec = (px, py)
    for i, b in enumerate(bar):
        ecrire(gx0 + gw * i / n - 6, gy0 + gh + 8, str(b["les_rangees"]), 0, GRIS)
    ecrire(gx0 + gw / 2 - 52, gy0 + gh + 26, "rangées moyennées", 0, GRIS)
    lx = x0 + pw - 322
    for k, (nom, coul) in enumerate(
            (("la DISPERSION du pas lu", BON), ("l'ALÉA mesuré", ALERTE),
             ("l'aléa PRÉDIT en racine de k", GRIS), ("la DÉRIVE qui reste", CONTRE))):
        art.rectangle([lx, y0 + 18 + k * 22, lx + 22, y0 + 26 + k * 22], fill=coul)
        ecrire(lx + 30, y0 + 16 + k * 22, nom, 0, coul)
    ecrire(lx, y0 + 118, "★★★★ À DEUX RANGÉES IL N'Y A PAS DE DÉRIVE :", petit, ENCRE)
    ecrire(lx, y0 + 132, "la dispersion est SOUS l'aléa, exactement ce que", petit, ENCRE)
    ecrire(lx, y0 + 146, "`203` avait trouvé. À seize, elle est au-dessus,", petit, ENCRE)
    ecrire(lx, y0 + 160, "et la dérive existe.", petit, ENCRE)
    ecrire(lx, y0 + 184,
           f"⚠⚠ L'aléa tombe PLUS VITE que la racine de k ne", petit, GRIS)
    ecrire(lx, y0 + 198,
           f"le prédit — {_fr(ve['le_rapport_observe_sur_predit_au_maximum'], 4)} de l'attendu à "
           f"seize rangées.", petit, GRIS)
    ecrire(lx, y0 + 212, "La tranche l'enregistre sans l'expliquer.", petit, GRIS)
    ecrire(lx, y0 + 236,
           "⚠ La loi en racine de k n'est PAS l'épreuve : c'est", petit, GRIS)
    ecrire(lx, y0 + 250,
           "l'erreur type d'une moyenne, donc la vérifier serait", petit, GRIS)
    ecrire(lx, y0 + 264, "une vérification incapable d'échouer.", petit, GRIS)

    # ---- panneau 2 : l'épreuve
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve, et son nul d'un demi DÉMONTRÉ", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("rangées moyennées", f"{ep['les_rangees']}"),
            ("coutures vues", f"{ep['les_coutures_vues']}"),
            ("coutures informatives", f"{ep['les_coutures_informatives']}"),
            ("qui portent un pas", f"{ep['les_coutures_qui_portent_un_pas']}"),
            ("seuil de la garantie", f"{ep['le_seuil_apparie']}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 300, yy, val, 0, ENCRE)
    part = float(ep["les_coutures_qui_portent_un_pas"]) / max(
        1.0, float(ep["les_coutures_informatives"]))
    barre(x0 + 12, y0 + 118, 372, part, 12, BON)
    ecrire(x0 + 12, y0 + 138,
           f"soit {_fr(part, 4)} pour un nul d'un demi · P = {_fr(ep['la_valeur_p'], 7)}",
           0, ENCRE)
    porte = bool(ep["la_couture_porte_un_pas"])
    ecrire(x0 + 12, y0 + 160,
           f"{'★' if porte else '✗'} LA COUTURE PORTE UN PAS : {porte}", moyen,
           BON if porte else ALERTE)
    ecrire(x0 + 12, y0 + 188,
           "★ Le nul se DÉMONTRE : sans pas à lire, les deux", petit, GRIS)
    ecrire(x0 + 12, y0 + 202,
           "demi-moyennes sont deux tirages de même loi, donc", petit, GRIS)
    ecrire(x0 + 12, y0 + 216,
           "leur SOMME et leur DIFFÉRENCE sont identiquement", petit, GRIS)
    ecrire(x0 + 12, y0 + 230,
           "distribuées. Un demi exactement, sans réglage.", petit, GRIS)

    # ---- panneau 3 : le contrôle croisé
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle croisé avec `202`", moyen, ENCRE)
    hautD = max(float(ve["la_derive_par_le_creux_en_voxels"]),
                float(ve["la_derive_au_maximum_en_voxels"]), 1.0) * 1.15
    for k, (nom, val, coul) in enumerate(
            ((f"dérive à {ve['les_rangees_de_lepreuve']} rangées",
              ve["la_derive_au_maximum_en_voxels"], CONTRE),
             ("dérive par le creux (`202`)", ve["la_derive_par_le_creux_en_voxels"], BON))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 306, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 17, 372, float(val) / hautD, 9, coul)
    ecrire(x0 + 12, y0 + 100,
           f"rapport des deux : {_fr(ve['le_rapport_des_deux_derives'], 4)}", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("aléa à deux rangées", f"{_fr(ve['lalea_au_depart_en_voxels'], 4)} vx"),
            ("aléa au compte de l'épreuve", f"{_fr(ve['lalea_au_maximum_en_voxels'], 4)} vx"),
            ("dispersion du pas", f"{_fr(ve['la_dispersion_au_maximum_en_voxels'], 4)} vx"),
            ("signal sur bruit", _fr(ve["le_signal_sur_bruit_au_maximum"], 4)))):
        yy = y0 + 132 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 276, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 222,
           "★ Deux méthodes sans rien de commun s'accordent à un", petit, BON)
    ecrire(x0 + 12, y0 + 236,
           "facteur une fois et demie — `203` en donnait vingt-quatre.", petit, BON)

    # ---- panneau 4 : la portée et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la portée, et l'étalon", moyen, ENCRE)
    for k, (nom, val, coul) in enumerate((
            ("un demi-pli, par la dérive",
             f"{_fr(po['par_la_derive']['les_chunks'], 2)} chunks", BON),
            ("… soit", f"{_fr(po['par_la_derive']['la_largeur_en_mm'], 3)} mm", BON),
            ("par le pas de `199`",
             f"{_fr(po['par_le_pas_de_199']['les_chunks'], 2)} chunks", GRIS),
            ("rapport des portées", _fr(po["le_rapport_des_portees"], 4), ENCRE))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 250, yy, val, 0, coul)
    ecrire(x0 + 12, y0 + 102, "l'étalon — deux faces, sur réplicats", 0, GRIS)
    for k, (nom, val) in enumerate((
            ("pas posé", f"{_fr(e['le_pas_pose_en_voxels'], 2)} vx"),
            ("dérive retrouvée", f"{_fr(e['la_derive_retrouvee_en_voxels'], 4)} vx"),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"))):
        yy = y0 + 124 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 232, yy, val, 0, ENCRE)
    barre(x0 + 12, y0 + 208, 372, float(e["la_part_trouvee"]), 10, BON)
    ecrire(x0 + 12, y0 + 226,
           f"★ sépare : {e['letalon_separe']} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  MOYENNER {ve['les_rangees_de_lepreuve']} RANGÉES FAIT PASSER LE SIGNAL DEVANT LE "
           f"BRUIT : l'aléa tombe de {_fr(ve['lalea_au_depart_en_voxels'], 4)} à "
           f"{_fr(ve['lalea_au_maximum_en_voxels'], 4)} voxel, la dispersion du pas reste à "
           f"{_fr(ve['la_dispersion_au_maximum_en_voxels'], 4)},", moyen, BON)
    ecrire(78, y + 46,
           f"     et la dérive qui n'existait PAS à deux rangées vaut "
           f"{_fr(ve['la_derive_au_maximum_en_voxels'], 4)} voxels — un signal sur bruit de "
           f"{_fr(ve['le_signal_sur_bruit_au_maximum'], 4)}.", moyen, BON)
    ecrire(78, y + 78,
           f"★★★★ ET L'ÉPREUVE LE CONFIRME AVEC UN NUL DÉMONTRÉ : "
           f"{ep['les_coutures_qui_portent_un_pas']} coutures sur "
           f"{ep['les_coutures_informatives']} informatives portent un pas, pour un seuil de "
           f"{ep['le_seuil_apparie']} et un nul d'un demi.", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     Sans pas à lire, la somme des deux demi-moyennes et leur différence sont "
           f"identiquement distribuées — le nul se démontre, il ne se postule pas.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"★  LA PORTÉE PASSE DE {_fr(po['par_le_pas_de_199']['les_chunks'], 2)} À "
           f"{_fr(po['par_la_derive']['les_chunks'], 2)} CHUNKS, soit "
           f"{_fr(po['par_la_derive']['la_largeur_en_mm'], 3)} mm là où `199` en donnait "
           f"{_fr(po['par_le_pas_de_199']['la_largeur_en_mm'], 3)} : un facteur "
           f"{_fr(po['le_rapport_des_portees'], 4)}.", moyen, BON)
    ecrire(78, y + 166,
           f"     Et le contrôle croisé tient : {_fr(ve['la_derive_au_maximum_en_voxels'], 4)} "
           f"contre {_fr(ve['la_derive_par_le_creux_en_voxels'], 4)} par le creux de `202`, un "
           f"rapport de {_fr(ve['le_rapport_des_deux_derives'], 4)} là où `203` en donnait "
           f"0,0415.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ L'aléa tombe plus vite que la racine de k ne le prédit — "
           f"{_fr(ve['le_rapport_observe_sur_predit_au_maximum'], 4)} de l'attendu — et la "
           f"dispersion tombe aussi : une part de ce qui passait pour du pas à deux rangées était "
           f"du bruit.", petit, GRIS)

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

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(16.0, 0), _fr(0.05, 2), _fr(2.233, 4)) == ("16", "0,05", "2,233"),
      f"{(_fr(16.0, 0), _fr(0.05, 2), _fr(2.233, 4))}")
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

    # ★★★★ LES QUATRE COURBES VIENNENT DE LA MESURE, BARREAU PAR BARREAU.
    for cle in ("lalea_en_voxels", "lalea_predit_en_voxels", "la_dispersion_du_pas_en_voxels",
                "la_derive_en_voxels"):
        for k in (1, len(d["la_courbe"]["les_barreaux"]) - 1):
            faux = copy.deepcopy(d)
            faux["la_courbe"]["les_barreaux"][k][cle] = 3.3131
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            v(f"★★★★ le barreau {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ UNE DERIVE ABSENTE NE SE DESSINE PAS, ET NE RELIE RIEN.
    faux = copy.deepcopy(d)
    for b in faux["la_courbe"]["les_barreaux"]:
        b["la_derive_en_voxels"] = None
    _c, _p, _cd, pt0, _b, _t = dessiner(faux, sortie)
    v("★★★★ une dérive absente à tous les barreaux retire ses points du graphe",
      len(pt0) < len(points), f"{len(pt0)} contre {len(points)}")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "la_derive_au_maximum_en_voxels"), 7.4747, 4, 3),
            (("le_verdict", "la_derive_par_le_creux_en_voxels"), 9.6969, 4, 2),
            (("le_verdict", "le_rapport_des_deux_derives"), 0.8181, 4, 2),
            (("le_verdict", "lalea_au_depart_en_voxels"), 8.1818, 4, 2),
            (("le_verdict", "lalea_au_maximum_en_voxels"), 6.1616, 4, 2),
            (("le_verdict", "la_dispersion_au_maximum_en_voxels"), 5.5151, 4, 2),
            (("le_verdict", "le_signal_sur_bruit_au_maximum"), 4.2424, 4, 2),
            (("le_verdict", "le_rapport_observe_sur_predit_au_maximum"), 0.3131, 4, 2),
            (("lepreuve", "la_valeur_p"), 0.0303, 4, 1),
            (("lepreuve", "les_coutures_informatives"), 191, 0, 2),
            (("lepreuve", "les_coutures_qui_portent_un_pas"), 173, 0, 2),
            (("lepreuve", "le_seuil_apparie"), 111, 0, 2),
            (("letalon", "la_derive_retrouvee_en_voxels"), 7.1717, 4, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    for cle, val, combien in (("les_chunks", 313.13, 2), ("la_largeur_en_mm", 91.919, 2)):
        faux = copy.deepcopy(d)
        faux["la_portee"]["par_la_derive"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la_portee.par_la_derive.{cle} est lu autant de fois qu'il le faut",
          sum(1 for _x, _y, t, _f in p3
              if _fr(val, 2 if cle == "les_chunks" else 3) in t) >= combien)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["la_couture_porte_un_pas"] = False
    v("★★★★ une couture sans pas change le titre",
      "aucune : la couture ne porte" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_signal_sur_bruit_au_maximum"] = 0.4
    v("★★★★ un signal sous le bruit le dit autrement",
      "le bruit le domine encore" in le_titre(faux), le_titre(faux))
    v("★★★ et l'observé dit que le signal passe devant",
      "le signal passe enfin devant le bruit" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_courbe"].__setitem__("decidable", False),
             "à la courbe indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "la_dispersion_du_pas_en_voxels", None),
             "dont un barreau n'a pas la dispersion du pas"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "lalea_predit_en_voxels", None),
             "dont un barreau n'a pas l'aléa prédit"),
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

    print(f"figure_combien_de_rangees_faut_il_pour_lire_le_pas.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "combien_de_rangees_faut_il_pour_lire_le_pas.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "204_combien_de_rangees_faut_il_pour_lire_le_pas.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
