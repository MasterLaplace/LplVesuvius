"""Le creux bouge-t-il AVEC le maillage ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, le nuage apparié : le pas du creux contre
le pas du maillage, sur les MÊMES coutures, avec la pente mesurée et les deux droites de pente ±1
qu'une frontière attachée à la matière donnerait. En bas à gauche, l'unique épreuve déclarée. En bas
au centre, ce que chaque pas vaut séparément. En bas à droite, l'étalon, dont l'échelle est dérivée
du pas que `199` a publié.

  uv run python src/figures/figure_le_creux_bouge_t_il_avec_le_maillage.py \\
      --json docs/mesures/le_creux_bouge_t_il_avec_le_maillage.json \\
      --sortie docs/images/202_le_creux_bouge_t_il_avec_le_maillage.png
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
    """Le JSON de `le_creux_bouge_t_il_avec_le_maillage.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, ET UNE QUI DÉCLARE PLUS D'UNE ÉPREUVE SANS
    EN DIVISER LA GARANTIE : sans la première, un appariement lu par une chaîne aveugle passerait
    pour un résultat ; sans la seconde, une valeur `p` à la garantie aurait été achetée par le
    nombre d'épreuves.

    ⚠⚠ ET REFUSE UNE MESURE DONT LES PAS N'ONT PAS LEURS COLONNES : c'est le défaut que `201` a
    nommé chez `199`, et une figure qui dessinerait un nuage sans savoir de quelles coutures il
    sort le referait.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "les_deux_pas", "lappariement", "la_decomposition", "le_verdict",
                "letalon"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("les_deux_pas", "lappariement", "la_decomposition", "le_verdict", "letalon"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    dd = d["les_deux_pas"]
    if not dd.get("les_colonnes_des_pas"):
        raise ValueError(f"{chemin} : les pas n'ont pas leurs colonnes, donc rien n'est joignable")
    if not (len(dd["le_pas_du_maillage_en_voxels"]) == len(dd["le_pas_du_creux_en_voxels"])
            == len(dd["les_colonnes_des_pas"])):
        raise ValueError(f"{chemin} : les deux pas et leurs colonnes ne s'apparient pas")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if not d["le_verdict"].get("le_creux_bouge_avec_le_maillage"):
        return ("Le creux bouge-t-il avec le maillage ? — NON, il dérive pour son compte")
    p = d["le_verdict"].get("la_pente_du_creux_sur_le_maillage")
    if p is not None and abs(abs(float(p)) - 1.0) <= 0.35:
        return ("Le creux bouge-t-il avec le maillage ? — OUI, et de pente un : "
                "c'est une frontière du papyrus")
    return ("Le creux bouge-t-il avec le maillage ? — oui, mais d'une pente qui n'est pas un")


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

    lg, d2 = d["la_ligne"], d["les_deux_pas"]
    ap, ve, e = d["lappariement"], d["le_verdict"], d["letalon"]
    demi = float(d["la_demi_periode_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · {lg['les_reperes_lisibles']} repères lisibles · "
           f"{d2['les_coutures']} coutures appariées · "
           f"largeur de bord {d['la_largeur_du_bord']} colonnes · une seule épreuve déclarée, "
           f"garantie {_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : le nuage apparié
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "le pas du CREUX contre le pas du MAILLAGE, sur les mêmes coutures", moyen, ENCRE)
    mm = [float(x) for x in d2["le_pas_du_maillage_en_voxels"]]
    cc = [float(x) for x in d2["le_pas_du_creux_en_voxels"]]
    gx0, gy0, gw, gh = x0 + 470, y0 + 16, 308, 236
    art.rectangle([gx0, gy0, gx0 + gw, gy0 + gh], outline=TRAIT, width=1)

    def px_(v):
        return gx0 + gw * (float(v) + demi) / (2.0 * demi)

    def py_(v):
        return gy0 + gh * (1.0 - (float(v) + demi) / (2.0 * demi))

    art.line([gx0, py_(0.0), gx0 + gw, py_(0.0)], fill=TRAIT, width=1)
    traits.append((gx0, py_(0.0), gx0 + gw))
    art.line([px_(0.0), gy0, px_(0.0), gy0 + gh], fill=TRAIT, width=1)
    for s, coul in ((1.0, GRIS), (-1.0, GRIS)):
        art.line([px_(-demi), py_(-demi * s), px_(demi), py_(demi * s)], fill=coul, width=1)
    pente = ve.get("la_pente_du_creux_sur_le_maillage")
    if pente is not None:
        art.line([px_(-demi), py_(max(-demi, min(demi, -demi * float(pente)))),
                  px_(demi), py_(max(-demi, min(demi, demi * float(pente))))],
                 fill=ALERTE, width=2)
    for a_, b_ in zip(mm, cc):
        x, y = px_(a_), py_(b_)
        art.ellipse([x - 2, y - 2, x + 2, y + 2], fill=CONTRE)
        points.append((x, y))
    ecrire(gx0 - 4, gy0 + gh + 8, f"maillage −{_fr(demi, 0)} vx", 0, GRIS)
    ecrire(gx0 + gw - 104, gy0 + gh + 8, f"maillage +{_fr(demi, 0)} vx", 0, GRIS)
    ecrire(gx0 + gw + 10, gy0 - 2, f"creux +{_fr(demi, 0)} vx", 0, GRIS)
    ecrire(gx0 + gw + 10, gy0 + gh - 12, f"creux −{_fr(demi, 0)} vx", 0, GRIS)
    ecrire(x0 + 12, y0 + 16,
           "★★★★ Une frontière ATTACHÉE À LA MATIÈRE donnerait une", petit, ENCRE)
    ecrire(x0 + 12, y0 + 30,
           "pente de module UN : quand le maillage glisse d'un voxel,", petit, ENCRE)
    ecrire(x0 + 12, y0 + 44,
           "la frontière paraît glisser d'autant. Les deux droites", petit, ENCRE)
    ecrire(x0 + 12, y0 + 58, "grises sont ces deux pentes.", petit, ENCRE)
    ecrire(x0 + 12, y0 + 84,
           f"pente mesurée : {_fr(pente, 4)}", moyen, ALERTE)
    ecrire(x0 + 12, y0 + 110,
           f"corrélation signée : {_fr(ap['la_correlation_signee'], 4)}", moyen, ALERTE)
    ecrire(x0 + 12, y0 + 140,
           "⚠⚠⚠ LE SENS N'EST PAS POSÉ, IL EST MESURÉ : l'épreuve", petit, GRIS)
    ecrire(x0 + 12, y0 + 154,
           "porte sur le MODULE de la corrélation, parce que `199` a", petit, GRIS)
    ecrire(x0 + 12, y0 + 168,
           "déjà rendu un pas à l'envers une fois. Poser le sens", petit, GRIS)
    ecrire(x0 + 12, y0 + 182,
           "attendu ferait de l'accord une suite de la convention.", petit, GRIS)
    ecrire(x0 + 12, y0 + 204,
           "⚠ Le pas du maillage se lit à la COUTURE, le creux est", petit, GRIS)
    ecrire(x0 + 12, y0 + 218,
           "une propriété du CUBE entier : seule une dérive lisse à", petit, GRIS)
    ecrire(x0 + 12, y0 + 232,
           "l'échelle du chunk les rend comparables. C'est une raison", petit, GRIS)
    ecrire(x0 + 12, y0 + 246,
           "d'attendre une corrélation PARTIELLE, pas aucune.", petit, GRIS)
    ecrire(x0 + 12, y0 + 262,
           "⚠⚠ Le nuage est ÉTROIT : c'est la MESURE, pas le tracé.", petit, ALERTE)

    # ---- panneau 2 : l'épreuve
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve : les deux pas sont-ils appariés ?", moyen, ENCRE)
    hautE = max(float(ap["la_correlation_absolue"]),
                float(ap["la_correlation_absolue_maximale_du_nul"]), 0.05) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("|corrélation| OBSERVÉE", ap["la_correlation_absolue"], ALERTE),
             ("médiane des mélanges", ap["la_correlation_absolue_mediane_du_nul"], GRIS),
             ("le plus fort des mélanges",
              ap["la_correlation_absolue_maximale_du_nul"], CONTRE))):
        yy = y0 + 10 + k * 38
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 316, yy, _fr(val, 4), 0, coul)
        barre(x0 + 12, yy + 17, 372, float(val) / hautE, 9, coul)
    ecrire(x0 + 12, y0 + 128,
           f"{ap['les_melanges_au_moins_aussi_forts']} mélange sur {ap['tirages']} est aussi "
           f"fort · P = {_fr(ap['la_valeur_p'], 2)}", 0, ENCRE)
    appar = bool(ap["les_deux_pas_sont_apparies"])
    ecrire(x0 + 12, y0 + 152,
           f"{'★' if appar else '✗'} LES DEUX PAS SONT APPARIÉS : {appar}", moyen,
           BON if appar else ALERTE)
    ecrire(x0 + 12, y0 + 182,
           "★ Le mélange garde les DEUX lois marginales — bornes,", petit, GRIS)
    ecrire(x0 + 12, y0 + 196,
           "saturations, bruit des deux estimateurs — et ne détruit", petit, GRIS)
    ecrire(x0 + 12, y0 + 210,
           "que l'APPARIEMENT, qui est ce que la tranche mesure.", petit, GRIS)
    ecrire(x0 + 12, y0 + 230,
           f"⚠ {d2['les_pas_du_maillage_qui_saturent']} pas du maillage saturent.", petit, GRIS)

    # ---- panneau 3 : ce que chaque pas vaut
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la décomposition : la dérive, et les deux bruits", moyen, ENCRE)
    dc = d.get("la_decomposition") or {}
    hautP = max(float(d2["le_pas_quadratique_du_creux_en_voxels"]), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("dérive COMMUNE aux deux lecteurs",
              dc.get("la_derive_commune_en_voxels"), BON),
             ("bruit du MAILLAGE (`199`)", dc.get("le_bruit_du_maillage_en_voxels"), CONTRE),
             ("bruit du CREUX (`200`)", dc.get("le_bruit_du_creux_en_voxels"), ALERTE))):
        yy = y0 + 10 + k * 38
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 306, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 17, 372, (float(val or 0.0)) / hautP, 9, coul)
    for k, (nom, val) in enumerate((
            ("signal sur bruit du maillage", _fr(dc.get("le_signal_sur_bruit_du_maillage"), 4)),
            ("signal sur bruit du creux", _fr(dc.get("le_signal_sur_bruit_du_creux"), 4)),
            ("pas quadratique du maillage",
             f"{_fr(d2['le_pas_quadratique_du_maillage_en_voxels'], 4)} vx"),
            ("pas quadratique du creux",
             f"{_fr(d2['le_pas_quadratique_du_creux_en_voxels'], 4)} vx"),
            ("paires voisines / appariées",
             f"{d['les_paires_voisines']} / {d2['les_coutures']}"))):
        yy = y0 + 128 + k * 19
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 276, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 220,
           "★★ Le modèle : les deux lecteurs voient la MÊME dérive,", petit, GRIS)
    ecrire(x0 + 12, y0 + 234, "chacun avec son bruit propre et indépendant.", petit, GRIS)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — une chaîne entière, deux faces", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 10,
           f"dérive posée par couture → part des {e['replicats']} réplicats appariés", 0, GRIS)
    for k, pt in enumerate(e["la_courbe"]):
        yy = y0 + 32 + k * 22
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 12, yy, f"{_fr(pt['la_derive_par_couture_en_voxels'], 4)} vx", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 104, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 152, yy + 2, 226, part, 8, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 12, y0 + 128,
           f"tient jusqu'à {_fr(e['la_derive_qui_tient'], 4)} vx · casse à "
           f"{_fr(e['la_derive_qui_casse'], 4)} vx", 0, ENCRE)
    ecrire(x0 + 12, y0 + 150,
           f"★ sépare : {e['letalon_separe']} · faux {_fr(e['le_taux_de_faux'], 3)} pour "
           f"{_fr(e['la_garantie'], 2)} garantis", 0, BON)
    ecrire(x0 + 12, y0 + 176,
           "★★ L'échelle est DÉRIVÉE du pas que `199` a publié, et", petit, GRIS)
    ecrire(x0 + 12, y0 + 190,
           "son dernier barreau est la demi-période : c'est là que le", petit, GRIS)
    ecrire(x0 + 12, y0 + 204, "pas du creux aliase, donc là que l'appariement se perd.", petit,
           GRIS)
    ecrire(x0 + 12, y0 + 226,
           f"⚠⚠ La face négative fait dériver la cohérence DE SON CÔTÉ,", petit, GRIS)
    ecrire(x0 + 12, y0 + 240, "avec la même loi : c'est le refus difficile.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    bouge = bool(ve["le_creux_bouge_avec_le_maillage"])
    ecrire(78, y + 18,
           f"{'★' if bouge else '✗'}  LE CREUX "
           f"{'BOUGE AVEC LE MAILLAGE' if bouge else 'NE BOUGE PAS AVEC LE MAILLAGE'} : "
           f"corrélation {_fr(ap['la_correlation_signee'], 4)} sur {d2['les_coutures']} coutures, "
           f"contre {_fr(ap['la_correlation_absolue_mediane_du_nul'], 4)} à la médiane des "
           f"{ap['tirages']} mélanges,", moyen, BON if bouge else ALERTE)
    ecrire(78, y + 46,
           f"     {ap['les_melanges_au_moins_aussi_forts']} au moins aussi fort, P = "
           f"{_fr(ap['la_valeur_p'], 2)} pour {_fr(d['la_garantie_par_epreuve'], 2)} garantis. "
           f"La pente vaut {_fr(ve['la_pente_du_creux_sur_le_maillage'], 4)}.",
           moyen, BON if bouge else ALERTE)
    ecrire(78, y + 78,
           "★★★★ CE QUE `R4-P50` PRÉSUPPOSAIT EST MAINTENANT MESURÉ : elle demandait ce qui "
           "distingue les deux frontières d'un cube, encore faut-il que le creux", moyen, ENCRE)
    ecrire(78, y + 106,
           "     soit attaché à la matière. Les deux pas sortent des MÊMES coutures, donc "
           "l'appariement n'est pas une hypothèse : il est dans la donnée.", moyen, ENCRE)
    ecrire(78, y + 138,
           "⚠⚠⚠ ET LA CHAÎNE EST ÉTALONNÉE ENTIÈRE : sur une rangée fabriquée où l'intensité et "
           "la cohérence sortent du même décalage, l'appariement est", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     retrouvé jusqu'à {_fr(e['la_derive_qui_tient'], 4)} voxels de dérive par "
           f"couture et perdu à {_fr(e['la_derive_qui_casse'], 4)} ; une cohérence qui dérive DE "
           f"SON CÔTÉ est refusée {e['les_replicats_du_refus'] - e['les_faux']} fois sur "
           f"{e['les_replicats_du_refus']}.", moyen, ENCRE)
    dcb = d.get("la_decomposition") or {}
    ecrire(78, y + 198,
           f"⚠ Le modèle additif donne une dérive commune de "
           f"{_fr(dcb.get('la_derive_commune_en_voxels'), 4)} voxels, un bruit de "
           f"{_fr(dcb.get('le_bruit_du_maillage_en_voxels'), 4)} pour le maillage et de "
           f"{_fr(dcb.get('le_bruit_du_creux_en_voxels'), 4)} pour le creux. Le lien pente-"
           f"corrélation est une IDENTITÉ, pas une confirmation.", petit, GRIS)

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
      (_fr(36.0, 0), _fr(0.05, 2), _fr(4.941, 4)) == ("36", "0,05", "4,941"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(4.941, 4))}")
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

    # ★★★★ LE NUAGE VIENT DE LA MESURE, POINT PAR POINT, ET SUR SES DEUX AXES.
    n = len(d["les_deux_pas"]["le_pas_du_creux_en_voxels"])
    for cle in ("le_pas_du_creux_en_voxels", "le_pas_du_maillage_en_voxels"):
        for k in (0, n // 2, n - 1):
            faux = copy.deepcopy(d)
            faux["les_deux_pas"][cle][k] = -29 if "maillage" in cle else -29.0
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            # ⚠⚠ UNE SONDE DE NUAGE NE PEUT PAS S'APPUYER SUR LES OCTETS : deux cents points sur
            # une petite grille se recouvrent, donc deplacer un point peut ne RIEN changer a
            # l'image. Ce qui discrimine est la LISTE des points que la fonction rend.
            v(f"★★★★ le point {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ LE NUAGE EST TRACE SUR L'ECHELLE DE LA DEMI-PERIODE, PAS SUR CELLE DES DONNEES : un pas
    # au bord doit toucher le bord du graphe, ce qu'un cadrage automatique ferait toujours.
    faux = copy.deepcopy(d)
    demi = float(d["la_demi_periode_en_voxels"])
    faux["les_deux_pas"]["le_pas_du_creux_en_voxels"] = [0.0] * n
    faux["les_deux_pas"]["le_pas_du_maillage_en_voxels"] = [0] * n
    _c, _p, _cd, pt0, _b, _t = dessiner(faux, sortie)
    faux["les_deux_pas"]["le_pas_du_creux_en_voxels"] = [demi] * n
    _c, _p, _cd, pt1, _b, _t = dessiner(faux, sortie)
    v("★★★★ deux nuages différents ne se dessinent pas au même endroit",
      {(round(x, 1), round(y, 1)) for x, y in pt0}
      != {(round(x, 1), round(y, 1)) for x, y in pt1})
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("lappariement", "la_correlation_signee"), -0.7171, 4, 2),
            (("lappariement", "la_correlation_absolue"), 0.7171, 4, 1),
            (("lappariement", "la_correlation_absolue_mediane_du_nul"), 0.1313, 4, 2),
            (("lappariement", "la_correlation_absolue_maximale_du_nul"), 0.2424, 4, 1),
            (("lappariement", "la_valeur_p"), 0.03, 2, 2),
            (("le_verdict", "la_pente_du_creux_sur_le_maillage"), -0.8181, 4, 2),
            (("les_deux_pas", "le_pas_quadratique_du_creux_en_voxels"), 13.1313, 4, 1),
            (("les_deux_pas", "le_pas_quadratique_du_maillage_en_voxels"), 27.2727, 4, 1),
            (("letalon", "la_derive_qui_tient"), 3.1313, 4, 2),
            (("letalon", "la_derive_qui_casse"), 8.1818, 4, 2),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1),
            (("letalon", "la_garantie"), 0.07, 2, 1),
            (("la_decomposition", "la_derive_commune_en_voxels"), 7.4747, 4, 2),
            (("la_decomposition", "le_bruit_du_maillage_en_voxels"), 5.1515, 4, 2),
            (("la_decomposition", "le_bruit_du_creux_en_voxels"), 23.2323, 4, 2),
            (("la_decomposition", "le_signal_sur_bruit_du_maillage"), 0.6161, 4, 1),
            (("la_decomposition", "le_signal_sur_bruit_du_creux"), 0.3131, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2 if _fr(val, dec) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LES COMPTES SONT DESSINES, ET LES REFUS AUSSI.
    for chemin_cles, val, combien in (
            (("les_deux_pas", "les_coutures"), 191, 3),
            (("les_deux_pas", "les_pas_du_maillage_qui_saturent"), 73, 1),
            (("lappariement", "les_melanges_au_moins_aussi_forts"), 17, 2),
            (("la_ligne", "les_reperes_lisibles"), 133, 1),
            (("la_ligne", "colonnes_lues"), 167, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n3 = sum(1 for _x, _y, t, _f in p3 if str(val) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est dessiné", n3 >= combien,
          f"{n3} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★ CHAQUE BARREAU DE L'ETALON PORTE SA PART ET SA DERIVE.
    for k in (0, len(d["letalon"]["la_courbe"]) - 1):
        faux = copy.deepcopy(d)
        faux["letalon"]["la_courbe"][k]["part_des_replicats"] = 0.6464 + k / 1e4
        faux["letalon"]["la_courbe"][k]["la_derive_par_couture_en_voxels"] = 13.1313 + k
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part et sa dérive",
          any(_fr(0.6464 + k / 1e4, 3) in t for _x, _y, t, _f in p4)
          and any(_fr(13.1313 + k, 4) in t for _x, _y, t, _f in p4))
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_creux_bouge_avec_le_maillage"] = True
    faux["le_verdict"]["la_pente_du_creux_sur_le_maillage"] = -1.05
    v("★★★★ un appariement de pente un change le titre",
      "c'est une frontière du papyrus" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["la_pente_du_creux_sur_le_maillage"] = 0.05
    v("★★★★ un appariement de pente NON un le dit autrement",
      "d'une pente qui n'est pas un" in le_titre(faux), le_titre(faux))
    faux["le_verdict"]["le_creux_bouge_avec_le_maillage"] = False
    v("★★★ et un refus le dit franchement",
      "NON, il dérive pour son compte" in le_titre(faux), le_titre(faux))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["les_deux_pas"].__setitem__("decidable", False),
             "aux deux pas indécidables"),
            (lambda x: x["lappariement"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["les_deux_pas"].__setitem__("les_colonnes_des_pas", []),
             "dont les pas n'ont pas leurs colonnes"),
            (lambda x: x["les_deux_pas"]["les_colonnes_des_pas"].pop(),
             "dont les pas et leurs colonnes diffèrent"),
            (lambda x: x["la_decomposition"].__setitem__("decidable", False),
             "dont le modèle additif est réfuté par ses propres nombres"),
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

    print(f"figure_le_creux_bouge_t_il_avec_le_maillage.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_creux_bouge_t_il_avec_le_maillage.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "202_le_creux_bouge_t_il_avec_le_maillage.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
