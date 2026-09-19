"""Où le maillage quitte-t-il son feuillet — la carte d'un segment entier.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la carte elle-même : une case par
position du treillis, sa couleur donne le serpentement, et les trous sont ceux du maillage. En haut
à droite, comment ce serpentement se distribue et ce qui sature. En bas à gauche, la seule question
déclarée — se groupe-t-il ? En bas à droite, l'étalon, posé sur les positions RÉELLEMENT lues.

  uv run python src/figures/figure_ou_le_maillage_quitte_t_il_son_feuillet.py \\
      --json docs/mesures/ou_le_maillage_quitte_t_il_son_feuillet.json \\
      --sortie docs/images/198_ou_le_maillage_quitte_t_il_son_feuillet.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from ou_le_maillage_quitte_t_il_son_feuillet import ABSENT_DU_DEPOT  # noqa: E402

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
TROU = (232, 230, 225)


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
    """Le JSON de `ou_le_maillage_quitte_t_il_son_feuillet.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, ET UNE DONT L'ÉTALON N'EST PAS POSÉ SUR LES
    POSITIONS RÉELLEMENT LUES. Sans la première, un silence rendu par un instrument aveugle passerait
    pour un résultat ; sans la seconde, l'étalon répondrait à la question d'une carte que personne
    n'a mesurée — c'est ce que `193` a mesuré sur `191`.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_carte", "les_positions", "les_quantiles", "le_groupement", "letalon"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if d["la_carte"].get("les_reprises_du_reseau") is None:
        raise ValueError(f"{chemin} : la carte ne dit pas combien de fois le fil a flanché, "
                         "donc son compte de couverture n'est pas qualifiable")
    for cle in ("les_lignes_du_treillis", "les_colonnes_du_treillis"):
        if not d["la_carte"].get(cle):
            raise ValueError(f"{chemin} : la carte ne publie pas {cle}, donc un trou ne "
                             "pourrait pas être dessiné à sa place")
    if not d["le_groupement"].get("decidable"):
        raise ValueError(f"{chemin} : le groupement est indécidable")
    e = d["letalon"]
    if not e.get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    if e["la_sensibilite"].get("les_positions") != d["la_carte"].get("positions_lues"):
        raise ValueError(f"{chemin} : l'étalon n'est pas posé sur les positions lues")
    if (e.get("le_taux_de_faux_tient") or {}).get("replicats") != e["la_sensibilite"].get(
            "replicats"):
        raise ValueError(f"{chemin} : les deux faces de l'étalon n'ont pas le même nombre "
                         "de réplicats")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if d["le_groupement"].get("ca_se_groupe"):
        return ("Où le maillage quitte son feuillet — LE DÉFAUT SE GROUPE, "
                "donc un correcteur peut être local")
    return ("Où le maillage quitte son feuillet — LE DÉFAUT NE SE GROUPE PAS, "
            "il est partout à la fois")


def _couleur(part: float) -> tuple[int, int, int]:
    """Du gris pâle au brun d'alerte, en passant par le bleu — une échelle continue."""
    p = max(0.0, min(1.0, float(part)))
    if p < 0.5:
        q = p / 0.5
        return (int(226 + (CONTRE[0] - 226) * q), int(224 + (CONTRE[1] - 224) * q),
                int(219 + (CONTRE[2] - 219) * q))
    q = (p - 0.5) / 0.5
    return (int(CONTRE[0] + (ALERTE[0] - CONTRE[0]) * q),
            int(CONTRE[1] + (ALERTE[1] - CONTRE[1]) * q),
            int(CONTRE[2] + (ALERTE[2] - CONTRE[2]) * q))


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

    c, q = d["la_carte"], d["les_quantiles"]
    g, e = d["le_groupement"], d["letalon"]
    cote = int(d["le_cote_de_la_carte"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {c['segment']} · grille {c['grille_de_chunks'][0]}×"
           f"{c['grille_de_chunks'][1]} chunks · treillis RÉGULIER {cote}×{cote} · "
           f"{c['positions_lues']} positions lues sur {c['positions_du_treillis']} · "
           f"pas d'un pli {_fr(d['le_pas_dun_pli_en_voxels'], 4)} voxels · "
           f"{d['tirages']} mélanges, une seule question déclarée", petit, GRIS)

    # ---- panneau 1 : la carte
    x0, y0, pw, ph = 56, 122, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la carte — une case par position, sa couleur donne le serpentement",
           moyen, ENCRE)
    lues = {(int(p["position"][0]), int(p["position"][1])):
            float(p["le_serpentement_en_voxels"]) for p in d["les_positions"]}
    # ⚠⚠⚠ LA GEOMETRIE EST CELLE DU TREILLIS, PAS CELLE DES POSITIONS LUES : ranger par leur rang
    # entre elles COMPRIME les lignes entierement vides, donc un trou cesserait de se voir a sa
    # place. Defaut vu en REGARDANT la carte, et qu'aucune garde n'aurait signale.
    rang_y = {v: i for i, v in enumerate(c["les_lignes_du_treillis"])}
    rang_x = {v: i for i, v in enumerate(c["les_colonnes_du_treillis"])}
    haut = max(lues.values()) if lues else 1.0
    cell = 13
    gx0, gy0 = x0 + 18, y0 + 14
    ny, nx = len(rang_y), len(rang_x)
    for y in range(ny):
        for x in range(nx):
            px, py = gx0 + x * cell, gy0 + y * cell
            art.rectangle([px, py, px + cell - 2, py + cell - 2], fill=TROU)
    for (cy, cx), val in lues.items():
        y, x = rang_y[cy], rang_x[cx]
        px, py = gx0 + x * cell, gy0 + y * cell
        art.rectangle([px, py, px + cell - 2, py + cell - 2], fill=_couleur(val / haut))
        points.append((px + cell - 2, py + cell - 2))
    ech = gy0 + ny * cell + 12
    for k in range(6):
        px = gx0 + k * 40
        art.rectangle([px, ech, px + 36, ech + 10], fill=_couleur(k / 5.0))
        points.append((px + 36, ech + 10))
    ecrire(gx0, ech + 14, "0 voxel", 0, GRIS)
    ecrire(gx0 + 172, ech + 14, f"{_fr(haut, 1)} voxels", 0, GRIS)
    ecrire(gx0 + 276, ech - 2, "les cases pâles sont les positions où le", 0, GRIS)
    ecrire(gx0 + 276, ech + 12, f"maillage n'a AUCUNE surface : "
                                f"{c['refuses'].get(ABSENT_DU_DEPOT, 0)} sur "
                                f"{c['positions_du_treillis']}", 0, ALERTE)
    ecrire(x0 + 18, y0 + 268,
           "⚠⚠ Ce qui est cartographié est le serpentement LOCAL, dans les trois dixièmes de",
           petit, GRIS)
    ecrire(x0 + 18, y0 + 282,
           "millimètre d'un chunk. La dérive ACCUMULÉE d'un bout à l'autre demanderait des "
           "chunks contigus.", petit, GRIS)

    # ---- panneau 2 : les quantiles
    x0, y0, pw, ph = 712, 122, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "comment il se distribue, et ce qui sature", moyen, ENCRE)
    hautQ = float(q["le_maximal_en_voxels"]) or 1.0
    for k, (nom, val) in enumerate((("médian", q["le_median_en_voxels"]),
                                    ("décile haut", q["le_decile_haut_en_voxels"]),
                                    ("maximal", q["le_maximal_en_voxels"]))):
        yy = y0 + 14 + k * 34
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 140, yy, f"{_fr(val, 4)} voxels", 0, ENCRE)
        barre(x0 + 260, yy + 2, 310, float(val) / hautQ, 10, CONTRE)
    ecrire(x0 + 14, y0 + 118,
           f"en plis : médian {_fr(q['le_median_en_plis'], 6)}   ·   décile haut "
           f"{_fr(q['le_decile_haut_en_plis'], 6)}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 142,
           f"positions qui SATURENT la plage de {d['la_plage_de_recalage']} voxels : "
           f"{q['les_positions_qui_saturent']} sur {q['positions']}", 0, ALERTE)
    ecrire(x0 + 14, y0 + 162,
           f"soit une part de {_fr(q['la_part_qui_sature'], 6)}", 0, ALERTE)
    ecrire(x0 + 14, y0 + 192,
           "⚠⚠⚠ LA SATURATION EST LA LIMITE DU RECALAGE, publiée à côté du résultat : un",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 206,
           "décalage de plus d'une demi-période se confond avec celui d'un pli entier, donc",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 220,
           "sans ce compte une pile très inclinée rendrait un PETIT serpentement.", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 236,
           f"⚠ Et {c['refuses'].get(ABSENT_DU_DEPOT, 0)} positions n'ont AUCUNE surface : une carte",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 250,
           "qui les compterait à zéro s'améliorerait là où le segment s'arrête.", petit, GRIS)
    ecrire(x0 + 14, y0 + 270,
           f"⚠⚠ Le fil a flanché {c.get('les_reprises_du_reseau', 0)} fois, redemandées jusqu'à "
           f"{c.get('les_reprises_permises', 0)} : un 404 est une", petit, GRIS)
    ecrire(x0 + 14, y0 + 284,
           "réponse et ne se redemande pas, une panne de transport n'en est pas une.", petit,
           GRIS)

    # ---- panneau 3 : le groupement
    x0, y0, pw, ph = 56, 478, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, f"la seule question déclarée — {d['la_question_declaree']}", moyen,
           ENCRE)
    hautD = max(float(g["la_distance_moyenne"]), float(g["la_distance_moyenne_du_nul"]),
                1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("la distance moyenne observée", g["la_distance_moyenne"], CONTRE),
             ("celle des mélanges", g["la_distance_moyenne_du_nul"], GRIS))):
        yy = y0 + 14 + k * 40
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 290, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 16, 570, float(val) / hautD, 12, coul)
    ecrire(x0 + 14, y0 + 102,
           f"{g['les_positions_du_pire_decile']} positions au-delà de "
           f"{_fr(g['le_seuil_du_pire_decile'], 4)} voxels   ·   "
           f"{g['les_melanges_au_moins_aussi_serres']} mélanges au moins aussi serrés sur "
           f"{g['tirages']}", 0, ENCRE)
    groupe = bool(g["ca_se_groupe"])
    ecrire(x0 + 14, y0 + 130,
           f"{'★' if groupe else '✗'} LE DÉFAUT "
           f"{'SE GROUPE' if groupe else 'NE SE GROUPE PAS'}.", moyen,
           BON if groupe else ALERTE)
    ecrire(x0 + 14, y0 + 164,
           "★ Et cette réponse décide de la FORME du correcteur : un défaut groupé se corrige",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 178,
           "localement, un défaut dispersé se corrige partout. C'est la seule chose que cette",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 192, "tranche demande, et elle l'a demandée avant de regarder.",
           petit, ENCRE)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 712, 478, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — posé sur les positions RÉELLEMENT lues", moyen, ENCRE)
    for k, pt in enumerate(e["la_sensibilite"]["la_courbe"]):
        yy = y0 + 10 + k * 20
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 14, yy, f"+{_fr(pt['force'], 0):>3} voxels posés", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 150, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 200, yy + 2, 240, part, 8, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 14, y0 + 116,
           f"force DÉRIVÉE {_fr(e['la_force_posee'], 0)} voxels, sur "
           f"{e['la_sensibilite']['replicats']} réplicats et "
           f"{e['la_sensibilite']['les_positions']} positions", 0, ENCRE)
    ecrire(x0 + 14, y0 + 136,
           f"taux de faux de la face DISPERSÉE : {_fr(e['le_taux_de_faux'], 3)} "
           f"({e['les_faux']} sur {e['le_taux_de_faux_tient']['replicats']}), pour "
           f"{_fr(e['la_garantie'], 2)} garantis", 0, ENCRE)
    ecrire(x0 + 14, y0 + 156, f"★ l'étalon sépare ses deux faces : {e['letalon_separe']}", 0,
           BON)
    ecrire(x0 + 14, y0 + 184,
           "⚠⚠⚠ LA PREMIÈRE VERSION NE SÉPARAIT PAS, et la mesure l'a dit : elle jugeait la",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 198,
           "face DISPERSÉE sur un TIRAGE UNIQUE, qui tombe du mauvais côté une fois sur vingt",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 212,
           "par construction. C'est le défaut que `193` avait trouvé dans `191`.", petit,
           ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  LE DÉFAUT NE SE GROUPE PAS : les {g['les_positions_du_pire_decile']} pires "
           f"positions sont à {_fr(g['la_distance_moyenne'], 4)} les unes des autres contre "
           f"{_fr(g['la_distance_moyenne_du_nul'], 4)} au hasard, et "
           f"{g['les_melanges_au_moins_aussi_serres']} mélanges", moyen, ALERTE)
    ecrire(78, y + 46,
           "     sur 19 sont au moins aussi serrés. Un correcteur ne pourra donc PAS être local "
           "et ciblé : le maillage quitte son feuillet partout à la fois.", moyen, ALERTE)
    ecrire(78, y + 78,
           f"★  ET LA CARTE EXISTE : {c['positions_lues']} positions lues sur "
           f"{c['positions_du_treillis']}, serpentement médian "
           f"{_fr(q['le_median_en_voxels'], 4)} voxels ({_fr(q['le_median_en_plis'], 6)} pli), "
           f"décile haut {_fr(q['le_decile_haut_en_voxels'], 4)}, maximal", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     {_fr(q['le_maximal_en_voxels'], 4)}. C'est la première moitié de ce qui "
           f"remplace l'humain du transfert — savoir OÙ corriger — et elle tient sur un segment "
           f"entier.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"⚠⚠⚠ MAIS DEUX CHIFFRES BORNENT CE QU'ELLE VAUT : "
           f"{q['les_positions_qui_saturent']} positions sur {q['positions']} SATURENT la plage, "
           f"donc leur serpentement est un plancher et non une valeur ; et", moyen, GRIS)
    ecrire(78, y + 166,
           f"     {c['refuses'].get(ABSENT_DU_DEPOT, 0)} positions du treillis n'ont AUCUNE surface, "
           f"c'est-à-dire que le maillage publié ne couvre pas un quart de ce qu'il enjambe.",
           moyen, GRIS)
    ecrire(78, y + 198,
           "⚠ Et ce qui est mesuré reste le serpentement LOCAL : la dérive accumulée d'un bout "
           "à l'autre du segment demanderait des chunks contigus.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.069364, 6), _fr(5.0, 4)) == ("90", "0,069364", "5"),
      f"{(_fr(90.0, 0), _fr(0.069364, 6), _fr(5.0, 4))}")
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

    # ★★★★ LA CARTE DESSINEE VIENT DE LA MESURE, CASE PAR CASE.
    for k in (0, 40, len(d["les_positions"]) - 1):
        faux = copy.deepcopy(d)
        faux["les_positions"][k]["le_serpentement_en_voxels"] = 999.0
        _c, _p, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la case {k} vient bien de la mesure", chemin.read_bytes() != octets)
        dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("les_quantiles", "le_median_en_voxels"), 13.75, 4, 2),
            (("les_quantiles", "le_median_en_plis"), 0.191919, 6, 2),
            (("les_quantiles", "le_maximal_en_voxels"), 47.25, 4, 2),
            (("les_quantiles", "les_positions_qui_saturent"), 77, 0, 2),
            (("le_groupement", "la_distance_moyenne"), 313.1313, 4, 2),
            (("le_groupement", "la_distance_moyenne_du_nul"), 424.2424, 4, 2),
            (("le_groupement", "les_positions_du_pire_decile"), 41, 0, 2),
            (("letalon", "le_taux_de_faux"), 0.125, 3, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n >= combien, f"{n} mentions pour {combien}")

    # ★★★★ UN TROU SE DESSINE A SA PLACE : deplacer une ligne du treillis deplace la carte.
    faux = copy.deepcopy(d)
    faux["la_carte"]["les_lignes_du_treillis"] = list(
        reversed(faux["la_carte"]["les_lignes_du_treillis"]))
    _c, _p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ la géométrie dessinée est celle du TREILLIS, pas celle des positions lues",
      chemin.read_bytes() != octets)
    dessiner(d, sortie)

    # ★★★★ LES TROUS DU MAILLAGE SONT DESSINES ET COMPTES : les taire ferait une carte pleine.
    faux = copy.deepcopy(d)
    faux["la_carte"]["refuses"][ABSENT_DU_DEPOT] = 133
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de positions SANS surface est dessiné des deux côtés",
      sum(1 for _x, _y, t, _f in p3 if "133" in t) >= 2)
    faux = copy.deepcopy(d)
    faux["la_carte"]["les_reprises_du_reseau"] = 41
    _c, p3b, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ et le nombre de fois où le fil a flanché est dessiné",
      any("41" in t for _x, _y, t, _f in p3b))

    # ★★★ CHAQUE BARREAU DE LA SENSIBILITE PORTE SA PART.
    for k in (0, 2):
        faux = copy.deepcopy(d)
        faux["letalon"]["la_sensibilite"]["la_courbe"][k]["part_des_replicats"] = 0.8181 + k / 1e4
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part",
          any(_fr(0.8181 + k / 1e4, 3) in t for _x, _y, t, _f in p4))

    # ★★★★ LE TITRE SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_groupement"]["ca_se_groupe"] = True
    v("★★★★ un défaut groupé change le titre", "SE GROUPE, donc" in le_titre(faux),
      le_titre(faux))
    v("★★★ et l'observé dit l'inverse", "NE SE GROUPE PAS" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE DONT L'ETALON NE TIENT PAS EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["letalon"]["la_sensibilite"].__setitem__("les_positions", 7),
             "dont l'étalon n'est pas posé sur les positions lues"),
            (lambda x: x["letalon"]["le_taux_de_faux_tient"].__setitem__("replicats", 1),
             "dont les deux faces n'ont pas le même nombre de réplicats"),
            (lambda x: x["le_groupement"].__setitem__("decidable", False),
             "au groupement indécidable"),
            (lambda x: x["la_carte"].pop("les_lignes_du_treillis"),
             "qui ne publie pas les lignes du treillis"),
            (lambda x: x["la_carte"].pop("les_reprises_du_reseau"),
             "qui ne dit pas combien de fois le fil a flanché"),
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

    print(f"figure_ou_le_maillage_quitte_t_il_son_feuillet.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "ou_le_maillage_quitte_t_il_son_feuillet.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "198_ou_le_maillage_quitte_t_il_son_feuillet.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
