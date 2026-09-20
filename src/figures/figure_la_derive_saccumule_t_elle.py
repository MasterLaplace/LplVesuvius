"""La dérive s'accumule-t-elle le long d'une spire ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la trace elle-même : la dérive cumulée
d'une couture à l'autre, en plis, avec les lignes du demi-pli et du pli. En bas à gauche, les pas et
leurs limites. En bas au centre, le verdict contre le tirage des signes. En bas à droite, la portée
d'une marche au hasard de ce pas, et l'étalon.

  uv run python src/figures/figure_la_derive_saccumule_t_elle.py \\
      --json docs/mesures/la_derive_saccumule_t_elle.json \\
      --sortie docs/images/199_la_derive_saccumule_t_elle.png
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
    """Le JSON de `la_derive_saccumule_t_elle.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, ET UNE DONT LES TRONÇONS NE PORTENT PAS LEUR
    TRACE : sans l'étalon, un silence rendu par un instrument aveugle passerait pour un résultat ;
    sans la trace, la figure devrait recalculer l'accumulation, c'est-à-dire en donner une seconde
    définition — or c'est exactement ce que cette tranche mesure.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_marche", "le_verdict", "letalon", "avant_un_demi_pli",
                "avant_un_pli"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : le verdict est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    trs = d["la_marche"].get("les_troncons") or []
    if not trs or any(not t.get("le_cumul_en_voxels") for t in trs):
        raise ValueError(f"{chemin} : un tronçon ne porte pas sa trace cumulée")
    for t in trs:
        if t["le_cumul_en_voxels"][-1] != t["le_deplacement_net_en_voxels"]:
            raise ValueError(f"{chemin} : la trace d'un tronçon ne finit pas sur son net")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if d["le_verdict"].get("ca_saccumule"):
        return ("La dérive s'accumule-t-elle ? — OUI, les pas s'additionnent "
                "et il y a un biais à retirer")
    return ("La dérive s'accumule-t-elle ? — les pas se COMPENSENT, "
            "et la marche au hasard perd quand même le feuillet")


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

    lg, m = d["la_ligne"], d["la_marche"]
    ve, e = d["le_verdict"], d["letalon"]
    a1, a2 = d["avant_un_demi_pli"], d["avant_un_pli"]
    pli = float(d["le_pas_dun_pli_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} de "
           f"{lg['grille_de_chunks'][0]} · {lg['colonnes_lues']} chunks lus sur "
           f"{lg['colonnes_demandees']} · {m['les_pas']} pas en {d['les_troncons']} tronçon(s) · "
           f"bord de {d['la_largeur_du_bord']} colonnes, DÉRIVÉ du serpentement de `198`",
           petit, GRIS)

    # ---- panneau 1 : la trace
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la dérive cumulée, couture après couture — en plis de papyrus", moyen, ENCRE)
    trs = m["les_troncons"]
    total = sum(len(t["le_cumul_en_voxels"]) for t in trs)
    haut = max(1.0, max(abs(float(v)) / pli for t in trs for v in t["le_cumul_en_voxels"]))
    haut = max(haut, 0.6) * 1.15
    gx0, gy0, gw, gh = x0 + 46, y0 + 16, pw - 92, 210
    milieu = gy0 + gh / 2.0
    # ⚠ Les deux reperes sont traces DES DEUX COTES et etiquetes des deux cotes : une derive vers
    # le bas franchit les memes seuils qu'une derive vers le haut, et n'etiqueter qu'un cote laisse
    # croire que l'autre n'a pas de repere.
    for part, nom in ((0.5 / haut, "0,5 pli"), (1.0 / haut, "1 pli")):
        if part <= 1.0:
            for signe in (-1, 1):
                yy = milieu - signe * part * gh / 2.0
                art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
                traits.append((gx0, yy, gx0 + gw))
                ecrire(gx0 - 44, yy - 6, ("+" if signe > 0 else "-") + nom, 0, GRIS)
    art.line([gx0, milieu, gx0 + gw, milieu], fill=GRIS, width=1)
    traits.append((gx0, milieu, gx0 + gw))
    place = 0
    for t in trs:
        trace = [float(v) / pli for v in t["le_cumul_en_voxels"]]
        pts = []
        for i, val in enumerate(trace):
            px = gx0 + gw * float(place + i) / max(1, total - 1)
            py = milieu - (val / haut) * gh / 2.0
            pts.append((px, py))
            points.append((px, py))
        if len(pts) > 1:
            art.line(pts, fill=CONTRE, width=2)
        place += len(trace)
    ecrire(gx0, gy0 + gh + 6, "0", 0, GRIS)
    ecrire(gx0 + gw - 30, gy0 + gh + 6, f"{m['les_pas']}", 0, GRIS)
    ecrire(gx0 + gw / 2 - 60, gy0 + gh + 6, "coutures parcourues", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 32,
           f"⚠⚠⚠ L'excursion maximale atteint {_fr(m['lexcursion_maximale_en_plis'], 6)} pli : la "
           f"surface s'est éloignée de plus d'un feuillet entier de là où elle était partie.",
           petit, ALERTE)

    # ---- panneau 2 : les pas
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les pas, et leurs limites", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("pas médian", f"{_fr(m['le_pas_median_en_voxels'], 4)} voxels"),
            ("pas quadratique", f"{_fr(m['le_pas_quadratique_en_voxels'], 4)} voxels"),
            ("pas qui SATURENT", f"{m['les_pas_qui_saturent']}"),
            ("déplacement net", f"{m['le_deplacement_net_en_voxels']} voxels"),
            ("… soit", f"{_fr(m['le_deplacement_net_en_plis'], 6)} pli"),
            ("excursion maximale", f"{_fr(m['lexcursion_maximale_en_plis'], 6)} pli"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 210, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 142,
           "⚠⚠⚠ UN PAS PLUS GRAND QU'UNE DEMI-PÉRIODE N'EST PAS", petit, ALERTE)
    ecrire(x0 + 12, y0 + 156,
           "SATURÉ, IL EST ALIASÉ : une couture qui a sauté un", petit, ALERTE)
    ecrire(x0 + 12, y0 + 170,
           "feuillet entier se lit comme un PETIT pas en arrière,", petit, ALERTE)
    ecrire(x0 + 12, y0 + 184,
           "et rien dans le pas seul ne les distingue.", petit, ALERTE)
    ecrire(x0 + 12, y0 + 208,
           f"⚠ Un chunk manquant coupe la ligne : {d['les_troncons']} tronçon(s),", petit, GRIS)
    ecrire(x0 + 12, y0 + 222,
           "et la dérive ne s'accumule jamais par-dessus un trou.", petit, GRIS)

    # ---- panneau 3 : le verdict
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le verdict — additionnent ou compensent ?", moyen, ENCRE)
    hautV = max(float(ve["le_deplacement_net_en_voxels"]),
                float(ve["le_deplacement_du_nul_median_en_voxels"]), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("déplacement observé", ve["le_deplacement_net_en_voxels"], CONTRE),
             ("médiane des tirages de signes", ve["le_deplacement_du_nul_median_en_voxels"],
              GRIS))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, _fr(val, 4), 0, coul)
        barre(x0 + 12, yy + 16, 372, float(val) / hautV, 10, coul)
    ecrire(x0 + 12, y0 + 98,
           f"{ve['les_tirages_au_moins_aussi_loin']} tirages sur {ve['tirages']} vont au moins "
           f"aussi loin", 0, ENCRE)
    ecrire(x0 + 12, y0 + 118,
           f"soit {_fr(ve['combien_de_marches_au_hasard'], 4)} écart-type de marche au hasard",
           0, ENCRE)
    acc = bool(ve["ca_saccumule"])
    ecrire(x0 + 12, y0 + 146,
           f"{'★' if acc else '✗'} LES PAS {'S ADDITIONNENT' if acc else 'SE COMPENSENT'}.",
           moyen, BON if acc else ALERTE)
    ecrire(x0 + 12, y0 + 176,
           "⚠⚠⚠ PERMUTER LES PAS LAISSERAIT LEUR SOMME INCHANGÉE :", petit, GRIS)
    ecrire(x0 + 12, y0 + 190,
           "un nul par permutation serait vide par construction. Le", petit, GRIS)
    ecrire(x0 + 12, y0 + 204,
           "nul tire donc les SIGNES, ce qui garde les tailles des", petit, GRIS)
    ecrire(x0 + 12, y0 + 218,
           "pas et remplace la marche observée par une marche au hasard.", petit, GRIS)

    # ---- panneau 4 : la portée et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la portée d'une marche au hasard de ce pas", moyen, ENCRE)
    for k, (nom, a) in enumerate((("un demi-pli après", a1), ("un pli après", a2))):
        yy = y0 + 12 + k * 22
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 172, yy,
               f"{_fr(a['les_chunks'], 2)} chunks = {_fr(a['la_largeur_en_mm'], 3)} mm", 0,
               ENCRE)
    ecrire(x0 + 12, y0 + 62, "l'étalon — deux faces, mesurées sur réplicats", 0, GRIS)
    for k, pt in enumerate(e["la_courbe"]):
        yy = y0 + 82 + k * 18
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 12, yy, f"biais {_fr(pt['le_biais_pose'], 1)} vx/couture", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 168, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 214, yy + 2, 170, part, 7, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 12, y0 + 178,
           f"biais DÉRIVÉ {_fr(e['le_biais_quil_faut'], 1)} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, ENCRE)
    ecrire(x0 + 12, y0 + 198, f"★ l'étalon sépare ses deux faces : {e['letalon_separe']}", 0,
           BON)
    ecrire(x0 + 12, y0 + 222,
           f"⚠ sur {e['replicats']} réplicats de {e['les_chunks']} chunks, bruit "
           f"{_fr(e['le_bruit'], 1)}", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  LES PAS SE COMPENSENT : le déplacement net vaut "
           f"{_fr(ve['le_deplacement_net_en_voxels'], 4)} voxels contre "
           f"{_fr(ve['le_deplacement_du_nul_median_en_voxels'], 4)} pour la médiane des tirages "
           f"de signes, "
           f"et {ve['les_tirages_au_moins_aussi_loin']} tirages sur {ve['tirages']} vont aussi "
           f"loin.", moyen, ALERTE)
    ecrire(78, y + 46,
           f"     C'est {_fr(ve['combien_de_marches_au_hasard'], 4)} écart-type de marche au "
           f"hasard : il n'y a AUCUN biais systématique à retirer.", moyen, ALERTE)
    ecrire(78, y + 78,
           f"★  ET C'EST LA MAUVAISE NOUVELLE, PAS LA BONNE : une marche au hasard DÉRIVE quand "
           f"même, comme la racine du nombre de pas. L'excursion atteint déjà", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     {_fr(m['lexcursion_maximale_en_plis'], 6)} pli sur cette rangée, et un pas "
           f"quadratique de {_fr(m['le_pas_quadratique_en_voxels'], 4)} voxels fait perdre un "
           f"DEMI-FEUILLET en {_fr(a1['les_chunks'], 2)} chunks, soit "
           f"{_fr(a1['la_largeur_en_mm'], 3)} mm de largeur dépliée.", moyen, ENCRE)
    ecrire(78, y + 138,
           "★★★★ CE QUI CONTRAINT LE CORRECTEUR : il n'a pas à retirer un biais, il doit BORNER "
           "UNE MARCHE. Une correction différentielle — de proche en proche —", moyen, ENCRE)
    ecrire(78, y + 166,
           "     ne peut par construction rien faire contre une accumulation sans biais : il faut "
           "une RÉFÉRENCE ABSOLUE, quelque chose qui dise où est le feuillet.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ Et une limite reste : un pas de plus d'une demi-période ALIASE. Ici "
           f"{m['les_pas_qui_saturent']} pas saturent, mais un saut de feuillet entier se lirait "
           f"comme un petit pas en arrière.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(1.304046, 6), _fr(4.941, 4)) == ("90", "1,304046", "4,941"),
      f"{(_fr(90.0, 0), _fr(1.304046, 6), _fr(4.941, 4))}")
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

    # ★★★★ LA TRACE DESSINEE EST CELLE DE LA MESURE, POINT PAR POINT.
    for k in (0, 60, len(d["la_marche"]["les_troncons"][0]["le_cumul_en_voxels"]) - 1):
        faux = copy.deepcopy(d)
        faux["la_marche"]["les_troncons"][0]["le_cumul_en_voxels"][k] += 400
        faux["la_marche"]["les_troncons"][0]["le_deplacement_net_en_voxels"] = \
            faux["la_marche"]["les_troncons"][0]["le_cumul_en_voxels"][-1]
        _c, _p, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le point {k} de la trace vient de la mesure", chemin.read_bytes() != octets)
        dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("la_marche", "lexcursion_maximale_en_plis"), 3.131313, 6, 2),
            (("la_marche", "le_pas_quadratique_en_voxels"), 13.75, 4, 2),
            (("la_marche", "les_pas_qui_saturent"), 77, 0, 2),
            (("le_verdict", "le_deplacement_net_en_voxels"), 424.2424, 4, 2),
            (("le_verdict", "le_deplacement_du_nul_median_en_voxels"), 313.1313, 4, 2),
            (("le_verdict", "les_tirages_au_moins_aussi_loin"), 13, 0, 2),
            (("le_verdict", "combien_de_marches_au_hasard"), 7.4747, 4, 2)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n >= combien, f"{n} mentions pour {combien}")

    # ★★★★ LA PORTEE EST DESSINEE DANS LES DEUX UNITES, ET DES DEUX COTES.
    for cle, val, dec in (("les_chunks", 313.13, 2), ("la_largeur_en_mm", 96.255, 3)):
        faux = copy.deepcopy(d)
        faux["avant_un_demi_pli"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la portée ({cle}) est lue des deux côtés",
          sum(1 for _x, _y, t, _f in p3 if _fr(val, dec) in t) >= 2)

    # ★★★ CHAQUE BARREAU DE L'ETALON PORTE SA PART.
    for k in (1, 3):
        faux = copy.deepcopy(d)
        faux["letalon"]["la_courbe"][k]["part_des_replicats"] = 0.7373 + k / 1e4
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part",
          any(_fr(0.7373 + k / 1e4, 3) in t for _x, _y, t, _f in p4))

    # ★★★★ LE TITRE SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["ca_saccumule"] = True
    v("★★★★ des pas qui s'additionnent changent le titre", "OUI, les pas" in le_titre(faux),
      le_titre(faux))
    v("★★★ et l'observé dit l'inverse", "se COMPENSENT" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["le_verdict"].__setitem__("decidable", False),
             "au verdict indécidable"),
            (lambda x: x["la_marche"]["les_troncons"][0].pop("le_cumul_en_voxels"),
             "dont un tronçon ne porte pas sa trace"),
            (lambda x: x["la_marche"]["les_troncons"][0].__setitem__(
                "le_deplacement_net_en_voxels", 4242),
             "dont la trace ne finit pas sur son net"),
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

    print(f"figure_la_derive_saccumule_t_elle.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_derive_saccumule_t_elle.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "199_la_derive_saccumule_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
