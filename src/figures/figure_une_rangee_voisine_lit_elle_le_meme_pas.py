"""Une rangée voisine du treillis lit-elle le même pas ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, les deux pas mis face à face couture par
couture, et ce qu'ils partagent. En bas à gauche, les deux lectures posées avant la mesure et celle
que le désaccord choisit. Au centre, l'épreuve et son contrôle — la seconde voisine. À droite, ce
que la boucle rapporterait, contre ce qu'une rangée seule donne.

  uv run python src/figures/figure_une_rangee_voisine_lit_elle_le_meme_pas.py \\
      --json docs/mesures/une_rangee_voisine_lit_elle_le_meme_pas.json \\
      --sortie docs/images/208_une_rangee_voisine_lit_elle_le_meme_pas.png
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
    """Le JSON de `une_rangee_voisine_lit_elle_le_meme_pas.py`.

    ⚠⚠⚠ REFUSE UNE MESURE SANS LES DEUX PROJECTIONS — celle d'une rangée seule et celle de la
    boucle : publier la seconde seule ferait lire un gain sans son point de comparaison.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("les_rangees_du_treillis", "la_prediction", "la_lecture", "le_verdict",
                "letalon", "ce_que_la_boucle_rapporte", "ce_que_la_rangee_seule_donne"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("les_rangees_du_treillis", "la_prediction", "la_lecture", "le_verdict",
                "letalon", "ce_que_la_boucle_rapporte", "ce_que_la_rangee_seule_donne"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    if len(d.get("les_epreuves") or {}) < 2:
        raise ValueError(f"{chemin} : la seconde voisine, qui est le contrôle, manque")
    if d["le_verdict"].get("la_derive_partagee_en_voxels") is None:
        raise ValueError(f"{chemin} : la dérive partagée est absente")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if not ve.get("les_deux_pas_sont_apparies"):
        return "Une rangée voisine lit-elle le même pas ? — non, chacune lit le sien"
    if d["ce_que_la_boucle_rapporte"].get("il_tient_sous_le_demi_pli"):
        return ("Une rangée voisine lit-elle le même pas ? — en partie, et cette part suffit à "
                "passer sous le demi-feuillet")
    return ("Une rangée voisine lit-elle le même pas ? — en partie, mais pas assez pour changer "
            "la portée")


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

    ec, pr, le = d["les_rangees_du_treillis"], d["la_prediction"], d["la_lecture"]
    ve, et = d["le_verdict"], d["letalon"]
    boucle, seule = d["ce_que_la_boucle_rapporte"], d["ce_que_la_rangee_seule_donne"]
    lignes = d.get("les_lignes") or {}
    une = lignes.get(str(ec["la_mediane"])) or next(iter(lignes.values()), {})
    demi = float(d["le_demi_pli_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {une.get('segment')} · rangées du treillis {ec['les_rangees']} · "
           f"{une.get('colonnes_demandees')} colonnes demandées · "
           f"{len(une.get('les_rangees_lues') or [])} rangées de coupe · une seule épreuve, "
           f"garantie {_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : ce que les deux rangées partagent
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "ce que deux rangées voisines partagent, et ce que chacune garde pour elle",
           moyen, ENCRE)
    partages = d.get("les_partages") or {}
    lx = x0 + 24
    hautP = max([float(x.get("la_derive_partagee_en_voxels") or 0.0)
                 for x in partages.values()]
                + [float(x.get("le_bruit_de_la_premiere_en_voxels") or 0.0)
                   for x in partages.values()]
                + [float(x.get("le_bruit_de_la_seconde_en_voxels") or 0.0)
                   for x in partages.values()] + [1.0]) * 1.2
    k = 0
    for r_, s in sorted(partages.items()):
        if not s.get("decidable"):
            continue
        ecrire(lx, y0 + 16 + k * 88,
               f"rangée {ec['la_mediane']} contre rangée {r_}", moyen, ENCRE)
        for j, (nom, val, coul) in enumerate((
                ("la dérive PARTAGÉE", s["la_derive_partagee_en_voxels"], BON),
                (f"le bruit propre de {ec['la_mediane']}",
                 s["le_bruit_de_la_premiere_en_voxels"], CONTRE),
                (f"le bruit propre de {r_}",
                 s["le_bruit_de_la_seconde_en_voxels"], PROFOND))):
            yy = y0 + 38 + k * 88 + j * 18
            ecrire(lx, yy, nom, 0, coul)
            ecrire(lx + 214, yy, f"{_fr(val, 4)} vx", 0, coul)
            barre(lx + 292, yy + 2, 300, float(val) / hautP, 8, coul)
        k += 1
    rx = x0 + 700
    for j, (nom, val) in enumerate((
            ("coutures communes", f"{ve['les_coutures_communes']}"),
            ("désaccord mesuré", f"{_fr(ve['lecart_type_observe_en_voxels'], 4)} vx"),
            ("si elles lisaient le MÊME pas",
             f"{_fr(ve['si_elles_lisent_le_meme_pas_en_voxels'], 4)} vx"),
            ("si elles lisaient autre chose",
             f"{_fr(ve['si_elles_lisent_autre_chose_en_voxels'], 4)} vx"),
            ("rapport à « même pas »", _fr(ve["le_rapport_a_la_lecture_meme_pas"], 4)),
            ("rapport à « autre chose »", _fr(ve["le_rapport_a_la_lecture_autre_chose"], 4)))):
        yy = y0 + 20 + j * 20
        ecrire(rx, yy, nom, 0, GRIS)
        ecrire(rx + 296, yy, val, 0, ENCRE)
    ecrire(rx, y0 + 152,
           f"plus proche de « {ve['de_laquelle_il_est_le_plus_proche']} »", moyen, ALERTE)
    ecrire(rx, y0 + 180, "★ LA DÉCOMPOSITION EST CELLE DE `202`, importée :", petit, GRIS)
    ecrire(rx, y0 + 194, "les deux rangées voient une même dérive, et chacune", petit, GRIS)
    ecrire(rx, y0 + 208, "y ajoute une erreur qui lui est propre. La", petit, GRIS)
    ecrire(rx, y0 + 222, "covariance EST la variance de ce qu'elles", petit, GRIS)
    ecrire(rx, y0 + 236, "partagent, et le modèle se réfute par ses propres", petit, GRIS)
    ecrire(rx, y0 + 250, "nombres si elle sort négative.", petit, GRIS)

    # ---- panneau 2 : les deux lectures posées
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux lectures, posées AVANT la mesure", moyen, ENCRE)
    for j, (nom, val) in enumerate((
            ("aléa de `204`", f"{_fr(pr['lalea_de_204_en_voxels'], 4)} vx"),
            ("dispersion de `204`", f"{_fr(pr['la_dispersion_de_204_en_voxels'], 4)} vx"),
            ("si le MÊME pas", f"{_fr(pr['si_elles_lisent_le_meme_pas_en_voxels'], 4)} vx"),
            ("si autre chose", f"{_fr(pr['si_elles_lisent_autre_chose_en_voxels'], 4)} vx"),
            ("elles diffèrent de", _fr(pr["le_rapport_des_deux_lectures"], 4)))):
        yy = y0 + 12 + j * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 252, yy, val, 0, ENCRE)
    hautL = max(float(pr["si_elles_lisent_autre_chose_en_voxels"]),
                float(ve["lecart_type_observe_en_voxels"]), 1.0) * 1.15
    for j, (nom, val, coul) in enumerate((
            ("même pas", pr["si_elles_lisent_le_meme_pas_en_voxels"], BON),
            ("mesuré", ve["lecart_type_observe_en_voxels"], ALERTE),
            ("autre chose", pr["si_elles_lisent_autre_chose_en_voxels"], GRIS))):
        yy = y0 + 122 + j * 26
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 252, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 14, 372, float(val) / hautL, 6, coul)
    ecrire(x0 + 12, y0 + 206,
           "⚠⚠ Aucun seuil ne sépare les deux : l'observé tombe", petit, GRIS)
    ecrire(x0 + 12, y0 + 220,
           "plus près de l'un ou de l'autre, et le rapport à", petit, GRIS)
    ecrire(x0 + 12, y0 + 234, "chacun est publié.", petit, GRIS)

    # ---- panneau 3 : l'épreuve et son contrôle
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve de `202`, et la seconde voisine en contrôle", moyen, ENCRE)
    epreuves = d.get("les_epreuves") or {}
    hautC = max([float(x.get("la_correlation_absolue") or 0.0) for x in epreuves.values()]
                + [0.1]) * 1.3
    j = 0
    for r_, e_ in sorted(epreuves.items()):
        if not e_.get("decidable"):
            continue
        role = ("l'épreuve" if int(r_) == int(ve["la_voisine_de_lepreuve"]) else "le contrôle")
        ecrire(x0 + 12, y0 + 12 + j * 58,
               f"rangée {r_} — {role}", 0, ENCRE if role == "l'épreuve" else GRIS)
        ecrire(x0 + 12, y0 + 28 + j * 58,
               f"|r| = {_fr(e_['la_correlation_absolue'], 4)} contre "
               f"{_fr(e_['la_correlation_absolue_mediane_du_nul'], 4)} au mélange · "
               f"{e_['les_melanges_au_moins_aussi_forts']} sur {e_['tirages']}", 0, GRIS)
        barre(x0 + 12, y0 + 44 + j * 58, 372,
              float(e_["la_correlation_absolue"]) / hautC, 8,
              BON if e_["les_deux_pas_sont_apparies"] else ALERTE)
        j += 1
    apparies = bool(ve["les_deux_pas_sont_apparies"])
    ecrire(x0 + 12, y0 + 132,
           f"{'★' if apparies else '✗'} LES DEUX PAS SONT APPARIÉS : {apparies}", moyen,
           BON if apparies else ALERTE)
    ecrire(x0 + 12, y0 + 154,
           f"P = {_fr(ve['la_valeur_p'], 4)} sur {ve['les_coutures_communes']} coutures", 0,
           ENCRE)
    ecrire(x0 + 12, y0 + 180,
           "⚠⚠ UNE SEULE ÉPREUVE EST DÉCLARÉE, donc la garantie", petit, GRIS)
    ecrire(x0 + 12, y0 + 194,
           "reste entière. La seconde voisine est un CONTRÔLE :", petit, GRIS)
    ecrire(x0 + 12, y0 + 208,
           "au-dessus et au-dessous doivent se comporter pareil,", petit, GRIS)
    ecrire(x0 + 12, y0 + 222, "et une seule qui s'accorderait serait un fait.", petit, GRIS)

    # ---- panneau 4 : ce que la boucle rapporte
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que la boucle rapporterait, contre une rangée seule", moyen, ENCRE)
    hautB = max(float(seule["lecart_attendu_en_voxels"]),
                float(boucle["lecart_attendu_en_voxels"]), demi) * 1.15
    for j, (nom, val, coul) in enumerate((
            ("une rangée seule", seule["lecart_attendu_en_voxels"], ALERTE),
            ("le demi-feuillet", demi, ENCRE),
            ("la boucle", boucle["lecart_attendu_en_voxels"], BON))):
        yy = y0 + 12 + j * 30
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 264, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 15, 372, float(val) / hautB, 8, coul)
    tient = bool(boucle["il_tient_sous_le_demi_pli"])
    ecrire(x0 + 12, y0 + 106,
           f"{'★' if tient else '✗'} LA BOUCLE PASSE SOUS LE DEMI-FEUILLET : {tient}", moyen,
           BON if tient else ALERTE)
    for j, (nom, val) in enumerate((
            ("coutures projetées", f"{boucle['les_coutures']}"),
            ("la boucle, en plis", _fr(boucle["lecart_attendu_en_plis"], 6)),
            ("une rangée, en plis", _fr(seule["lecart_attendu_en_plis"], 6)),
            ("l'étalon sépare", f"{et['letalon_separe']}"),
            ("faux", f"{et['les_faux']} sur {et['les_replicats_du_refus']}"))):
        yy = y0 + 136 + j * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 264, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 238,
           f"★ étalon : {et['les_vus']} des {et['replicats']} réplicats · taux de faux "
           f"{_fr(et['le_taux_de_faux'], 3)}", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"{'★' if apparies else '✗'}  LES RANGÉES VOISINES SONT APPARIÉES : |r| = "
           f"{_fr(ve['la_correlation_absolue'], 4)} sur {ve['les_coutures_communes']} coutures, "
           f"P = {_fr(ve['la_valeur_p'], 4)} — et le contrôle, la seconde voisine, donne "
           f"{_fr(ve['les_correlations_des_controles'][0] if ve.get('les_correlations_des_controles') else None, 4)}.",
           moyen, BON if apparies else ALERTE)
    ecrire(78, y + 46,
           f"⚠⚠ MAIS ELLES NE LISENT PAS LE MÊME PAS : le désaccord vaut "
           f"{_fr(ve['lecart_type_observe_en_voxels'], 4)} voxels, soit "
           f"{_fr(ve['le_rapport_a_la_lecture_meme_pas'], 4)} fois ce que deux lectures d'une même "
           f"couture donneraient.", moyen, GRIS)
    ecrire(78, y + 78,
           f"★  CE QU'ELLES PARTAGENT EST CHIFFRÉ : une dérive commune de "
           f"{_fr(ve['la_derive_partagee_en_voxels'], 4)} voxels, contre un bruit propre de "
           f"{_fr(ve['le_bruit_de_la_mediane_en_voxels'], 4)} pour la rangée médiane et "
           f"{_fr(ve['le_bruit_de_la_voisine_en_voxels'], 4)} pour sa voisine.", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     Le signal sur bruit vaut {_fr(ve['le_signal_sur_bruit_de_la_mediane'], 4)} : "
           f"chaque rangée porte donc plus de bruit propre que de dérive partagée.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"{'★' if tient else '✗'}  ET C'EST CE QUI BRISE LE PLAFOND DE `207` : moyenner les "
           f"rangées du treillis retirerait le bruit propre et laisserait "
           f"{_fr(ve['la_derive_partagee_en_voxels'], 4)} voxels, donc une excursion de",
           moyen, BON if tient else ALERTE)
    ecrire(78, y + 166,
           f"     {_fr(boucle['lecart_attendu_en_voxels'], 4)} voxels sur "
           f"{boucle['les_coutures']} coutures — {_fr(boucle['lecart_attendu_en_plis'], 6)} pli — "
           f"là où une rangée seule en donne {_fr(seule['lecart_attendu_en_voxels'], 4)}, "
           f"au-dessus du demi-feuillet de {_fr(demi, 0)}.", moyen, BON if tient else ALERTE)
    ecrire(78, y + 198,
           f"⚠ C'est une PROJECTION, pas une marche mesurée : elle dit ce que la moyenne des "
           f"rangées donnerait, et la mesurer demande de la construire.", petit, GRIS)

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
      (_fr(36.0, 0), _fr(0.05, 2), _fr(1.5129, 4)) == ("36", "0,05", "1,5129"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(1.5129, 4))}")
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

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "la_derive_partagee_en_voxels"), 7.4747, 4, 2),
            (("le_verdict", "le_bruit_de_la_mediane_en_voxels"), 8.1818, 4, 1),
            (("le_verdict", "le_bruit_de_la_voisine_en_voxels"), 9.6969, 4, 1),
            (("le_verdict", "le_signal_sur_bruit_de_la_mediane"), 0.3131, 4, 1),
            (("le_verdict", "lecart_type_observe_en_voxels"), 5.5151, 4, 3),
            (("le_verdict", "si_elles_lisent_le_meme_pas_en_voxels"), 6.1616, 4, 1),
            (("le_verdict", "si_elles_lisent_autre_chose_en_voxels"), 7.1717, 4, 1),
            (("le_verdict", "le_rapport_a_la_lecture_meme_pas"), 1.9191, 4, 2),
            (("le_verdict", "le_rapport_a_la_lecture_autre_chose"), 0.4141, 4, 1),
            (("le_verdict", "la_correlation_absolue"), 0.7171, 4, 1),
            (("le_verdict", "la_valeur_p"), 0.0303, 4, 2),
            (("la_prediction", "lalea_de_204_en_voxels"), 3.1313, 4, 1),
            (("la_prediction", "la_dispersion_de_204_en_voxels"), 4.2424, 4, 1),
            (("la_prediction", "le_rapport_des_deux_lectures"), 8.8181, 4, 1),
            (("ce_que_la_boucle_rapporte", "lecart_attendu_en_voxels"), 51.5151, 4, 2),
            (("ce_que_la_boucle_rapporte", "lecart_attendu_en_plis"), 0.717171, 6, 2),
            (("ce_que_la_rangee_seule_donne", "lecart_attendu_en_voxels"), 61.6161, 4, 2),
            (("ce_que_la_rangee_seule_donne", "lecart_attendu_en_plis"), 0.818181, 6, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LA DECOMPOSITION DE CHAQUE VOISINE EST DESSINEE, PAS SEULEMENT CELLE DE L'EPREUVE.
    voisines = sorted(d["les_partages"])
    faux = copy.deepcopy(d)
    faux["les_partages"][voisines[-1]]["la_derive_partagee_en_voxels"] = 41.4141
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la décomposition de la SECONDE voisine est dessinée aussi",
      sum(1 for _x, _y, t, _f in p3 if _fr(41.4141, 4) in t) >= 1)
    faux = copy.deepcopy(d)
    faux["les_epreuves"][voisines[-1]]["la_correlation_absolue"] = 0.9393
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la corrélation du CONTRÔLE est dessinée aussi",
      sum(1 for _x, _y, t, _f in p4 if _fr(0.9393, 4) in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["les_deux_pas_sont_apparies"] = False
    v("★★★★ des rangées non appariées changent le titre",
      "chacune lit le sien" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["les_deux_pas_sont_apparies"] = True
    faux["ce_que_la_boucle_rapporte"]["il_tient_sous_le_demi_pli"] = False
    v("★★★★ une boucle qui ne suffit pas le dit autrement",
      "pas assez pour changer la portée" in le_titre(faux), le_titre(faux))
    v("★★★ et l'observé dit que cette part suffit",
      "suffit à passer sous le demi-feuillet" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_lecture"].__setitem__("decidable", False),
             "à la lecture indécidable"),
            (lambda x: x["la_prediction"].__setitem__("decidable", False),
             "à la prédiction indécidable"),
            (lambda x: x["ce_que_la_boucle_rapporte"].__setitem__("decidable", False),
             "sans ce que la boucle rapporte"),
            (lambda x: x["ce_que_la_rangee_seule_donne"].__setitem__("decidable", False),
             "sans ce qu'une rangée seule donne"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x.__setitem__("les_epreuves", {"197": {}}),
             "sans la seconde voisine, qui est le contrôle"),
            (lambda x: x["le_verdict"].__setitem__("la_derive_partagee_en_voxels", None),
             "sans la dérive partagée"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_une_rangee_voisine_lit_elle_le_meme_pas.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "une_rangee_voisine_lit_elle_le_meme_pas.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "208_une_rangee_voisine_lit_elle_le_meme_pas.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
