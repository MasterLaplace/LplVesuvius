"""Un ruban qui saute perd-il sa fibre ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon : sur une matière dont les
frontières sont POSÉES, un ruban qui les traverse perd sa crête et un ruban qui dérive autant sans
traverser la garde. En haut à droite, le rouleau. En bas à gauche, le nul — mélanger l'ordre des
couches doit effacer l'écart, sinon on mesurait la profondeur de départ et non le saut. En bas à
droite, ce que ça vaut pour le graal.

  uv run python src/figures/figure_un_ruban_qui_saute_perd_il_sa_fibre.py \\
      --json docs/mesures/un_ruban_qui_saute_perd_il_sa_fibre.json \\
      --sortie docs/images/187_un_ruban_qui_saute_perd_il_sa_fibre.png
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
    """Le JSON de `un_ruban_qui_saute_perd_il_sa_fibre.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE VOIT PAS UN SAUT CONSTRUIT. Si le témoin ne remarque pas
    une frontière POSÉE, ce qu'il rend sur le rouleau ne se lit pas — c'est le précédent de `185`,
    dont le premier critère d'arrêt était vacant et que seul l'étalon a montré nu.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "les_segments", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("le_temoin_voit_un_saut_construit"):
        raise ValueError(f"{chemin} : l'étalon ne voit pas un saut construit")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if v.get("le_saut_coute_plus_que_la_derive"):
        queue = "OUI, et plus que la seule dérive en profondeur"
    elif v.get("le_saut_coute_plus_que_le_hasard"):
        queue = "il perd, mais pas plus que la dérive"
    else:
        queue = "NON, sur le rouleau c'est la DÉRIVE qui coûte, pas le saut"
    return f"Un ruban qui saute perd-il sa fibre ? — {queue}"


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

    v, e = d["le_verdict"], d["letalon"]
    coul_v = BON if v.get("le_saut_coute_plus_que_la_derive") else ALERTE
    signe = "★" if v.get("le_saut_coute_plus_que_la_derive") else "✗"
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46, f"{d['departs_par_couche']} départs par couche · treillis "
                   f"{d['cote_du_treillis']}×{d['cote_du_treillis']} · {v['chunks_lus']} chunks · "
                   f"plafond {d['plafond_de_pas']} pas · montée {v.get('montee_mediane')} couches · "
                   f"voxel {_fr(d['voxel_um'], 1)} µm", petit, GRIS)

    # ---- panneau 1 : l'étalon, frontières posées
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — des frontières POSÉES, donc la réponse est connue avant",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "recouvrement", petit, GRIS)
    ecrire(x0 + 150, y0 + 10, "décalages", petit, GRIS)
    ecrire(x0 + 260, y0 + 10, "le saut coûte", petit, ALERTE)
    ecrire(x0 + 400, y0 + 10, "couches mélangées", petit, GRIS)
    hautb = max([abs(float(x["cout_median"] or 0.0)) for x in e["par_recouvrement"]] + [1.0]) * 1.25
    for k, x in enumerate(e["par_recouvrement"]):
        yy = y0 + 34 + k * 40
        ecrire(x0 + 14, yy, f"{_fr(x['recouvrement_um'], 1)} µm", 0, ENCRE)
        ecrire(x0 + 150, yy, f"{x['decalages_ou_le_saut_coute']} / {x['decalages_lisibles']}", 0,
               ENCRE)
        ecrire(x0 + 260, yy, f"{_fr(x['cout_median'], 2)} pas", 0, ALERTE)
        barre(x0 + 260, yy + 16, 120, abs(float(x["cout_median"] or 0.0)) / hautb, 6, ALERTE)
        ecrire(x0 + 400, yy, f"{_fr(x['nul_median'], 2)} pas", 0, GRIS)
        barre(x0 + 400, yy + 16, 120, abs(float(x["nul_median"] or 0.0)) / hautb, 6, GRIS)
    ecrire(x0 + 14, y0 + 122, "à plat", petit, CONTRE)
    ecrire(x0 + 150, y0 + 122, "en dérivant sans traverser", petit, BON)
    ecrire(x0 + 380, y0 + 122, "en traversant", petit, ALERTE)
    lignes = [x for x in e["lignes"] if x.get("decidable")]
    hautf = max([float(x["pas_en_restant"] or 0.0) for x in lignes]
                + [float(e["pas_a_plat_median"] or 0.0)] + [1.0]) * 1.2
    # ⚠⚠ LES TROIS BARRES PARTAGENT LA MEME LARGEUR MAXIMALE : sans cela deux valeurs EGALES se
    # dessineraient de longueurs differentes, et l'oeil lirait un ecart la ou il n'y en a pas.
    yy = y0 + 142
    ref = lignes[0] if lignes else {}
    for dx, val, coul in ((14, e["pas_a_plat_median"], CONTRE),
                          (150, ref.get("pas_en_restant"), BON),
                          (380, ref.get("pas_en_traversant"), ALERTE)):
        ecrire(x0 + dx, yy, _fr(val, 2), 0, coul)
        barre(x0 + dx, yy + 16, 110, float(val or 0.0) / hautf, 7, coul)
    ecrire(x0 + 14, y0 + 184,
           f"★ le saut coûte à {e['decalages_ou_le_saut_coute']} décalages sur "
           f"{e['decalages_lisibles']}, médiane {_fr(e['cout_median_du_saut'], 2)} pas,",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 206,
           f"     contre {_fr(e['cout_median_du_nul'], 2)} en mélangeant les couches — et DÉRIVER "
           f"y coûte {_fr(e['cout_median_de_la_derive'], 2)}.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 232,
           "⚠ Les deux recouvrements sont relus de `179` : le rasoir, et la plus petite", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 248,
           "transition où le creux tombe sur la frontière à tous les décalages.", petit, GRIS)

    # ---- panneau 2 : le rouleau
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau, par segment", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 200, y0 + 10, "à plat", petit, CONTRE)
    ecrire(x0 + 290, y0 + 10, "en restant", petit, BON)
    ecrire(x0 + 400, y0 + 10, "en traversant", petit, ALERTE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    hauts = max([float(s["pas_en_restant"] or 0.0) for s in lus]
                + [float(s["pas_a_plat"] or 0.0) for s in lus] + [1.0]) * 1.2
    for k, s in enumerate(lus):
        yy = y0 + 34 + k * 44
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 14, yy + 16, f"{s['chunks_lus']} chunks · coûte "
                                 f"{_fr(s['cout_median_du_saut'], 2)} · nul "
                                 f"{_fr(s['cout_median_du_nul'], 2)}", 0, GRIS)
        ecrire(x0 + 200, yy, _fr(s["pas_a_plat"], 2), 0, CONTRE)
        barre(x0 + 200, yy + 16, 70, float(s["pas_a_plat"] or 0.0) / hauts, 5, CONTRE)
        ecrire(x0 + 290, yy, _fr(s["pas_en_restant"], 2), 0, BON)
        barre(x0 + 290, yy + 16, 90, float(s["pas_en_restant"] or 0.0) / hauts, 5, BON)
        ecrire(x0 + 400, yy, _fr(s["pas_en_traversant"], 2), 0, ALERTE)
        barre(x0 + 400, yy + 16, 90, float(s["pas_en_traversant"] or 0.0) / hauts, 5, ALERTE)
    ecrire(x0 + 14, y0 + 178,
           f"{signe} sur {v['chunks_lus']} chunks, le saut coûte "
           f"{_fr(v['ce_que_le_saut_coute'], 2)} pas", moyen, coul_v)
    ecrire(x0 + 14, y0 + 200,
           f"     ({_fr(v['ce_que_le_saut_coute_um'], 2)} µm), et le mélange en rend "
           f"{_fr(v['ce_que_le_nul_rend'], 2)}.", moyen, coul_v)
    ecrire(x0 + 14, y0 + 226,
           f"⚠ Il ne reste que {_fr(v['il_en_reste_la_part'], 4)} de la longueur suivable "
           f"quand on traverse :", petit, GRIS)
    ecrire(x0 + 14, y0 + 242,
           f"{_fr(v['pas_en_traversant'], 2)} pas contre {_fr(v['pas_en_restant'], 2)}.", petit,
           GRIS)

    # ---- panneau 3 : le nul
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le nul — mélanger l'ordre des couches doit effacer l'écart", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14,
           "⚠⚠ Mélanger l'ordre des couches garde chaque couche INTACTE — même texture, même", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 30,
           "direction de fibres — et détruit seulement le fait que deux couches voisines", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 46,
           "appartiennent à la même feuille. Les étiquettes « traverse » et « reste » viennent", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 62,
           "des frontières d'ORIGINE, donc après le mélange elles ne désignent plus rien.", petit,
           GRIS)
    hautn = max(abs(float(v["ce_que_le_saut_coute"] or 0.0)),
                abs(float(v["ce_que_le_nul_rend"] or 0.0)),
                abs(float(v["ce_que_la_derive_coute"] or 0.0)),
                abs(float(e["cout_median_du_saut"] or 0.0)),
                abs(float(e["cout_median_de_la_derive"] or 0.0)),
                abs(float(e["cout_median_du_nul"] or 0.0)), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("l'étalon · le saut coûte", e["cout_median_du_saut"], ALERTE),
             ("l'étalon · la dérive coûte", e["cout_median_de_la_derive"], BON),
             ("l'étalon · couches mélangées", e["cout_median_du_nul"], GRIS),
             ("le rouleau · le saut coûte", v["ce_que_le_saut_coute"], ALERTE),
             ("le rouleau · la dérive coûte", v["ce_que_la_derive_coute"], BON),
             ("le rouleau · couches mélangées", v["ce_que_le_nul_rend"], GRIS))):
        yy = y0 + 88 + k * 25
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 250, yy, f"{_fr(val, 3)} pas", 0, coul)
        barre(x0 + 330, yy + 1, 240, abs(float(val or 0.0)) / hautn, 8, coul)
    ecrire(x0 + 14, y0 + 240,
           f"{signe} EXACTEMENT INVERSÉ : sur la matière construite dériver est gratuit",
           moyen, coul_v)
    ecrire(x0 + 14, y0 + 258,
           f"     et traverser coûte ; sur le rouleau c'est l'inverse.", moyen, coul_v)

    # ---- panneau 4 : ce que ça vaut pour le graal
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que ça vaut pour le graal", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14,
           "Le prix demande de suivre les fibres SANS SAUTER DE FEUILLE. Une fibre ne", petit, ENCRE)
    ecrire(x0 + 14, y0 + 30,
           "traverse pas une frontière : elle ne peut donc pas ANCRER le saut, elle peut", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 46,
           "en être le TÉMOIN. C'est cette lecture-là que la tranche met à l'épreuve.", petit, ENCRE)
    hautp = max(float(v["en_restant_um"] or 0.0), float(v["en_traversant_um"] or 0.0), 1.0) * 1.25
    for k, (nom, val, coul) in enumerate(
            (("un ruban qui reste", v["en_restant_um"], BON),
             ("un ruban qui traverse", v["en_traversant_um"], ALERTE))):
        yy = y0 + 82 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 190, yy, f"{_fr(val, 2)} µm", 0, coul)
        barre(x0 + 280, yy + 2, 270, float(val or 0.0) / hautp, 12, coul)
    for k, (nom, ok) in enumerate(
            (("le témoin voit un saut CONSTRUIT", v.get("le_temoin_voit_un_saut_construit")),
             ("un recouvrement adoucit le saut", v.get("le_recouvrement_adoucit_le_saut")),
             ("le saut coûte sur le rouleau", v.get("le_saut_coute_sur_le_rouleau")),
             ("et plus que le hasard", v.get("le_saut_coute_plus_que_le_hasard")),
             ("et plus que la seule dérive", v.get("le_saut_coute_plus_que_la_derive")))):
        yy = y0 + 144 + k * 21
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)
    # ⚠ CES DEUX LIGNES TIENNENT DANS LE CADRE, ET IL A FALLU REGARDER L'IMAGE POUR LE VOIR : une
    # ligne posee SOUS la bordure n'est signalee par aucune garde, parce que `textes_hors_cadre` ne
    # juge que les textes qui COMMENCENT dans un cadre.
    ecrire(x0 + 14, y0 + 242,
           f"⚠ Pente {_fr(v.get('pente_mediane'), 3)} couche par pas : une fibre ne témoigne", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 258,
           "que d'une traversée arrivée dans sa PROPRE longueur.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           "★  LE CRITÈRE DU PRIX EST PRIS DANS LE BON SENS. Une fibre ne traverse pas une "
           "frontière de feuille : elle ne peut pas ANCRER le transfert, elle en est le", moyen,
           ENCRE)
    ecrire(78, y + 46,
           "     TÉMOIN. C'est ce que l'humain surveille quand il corrige une spire, et `185` ne "
           "le mesurait que par procuration, en comparant une longueur à une distance.", moyen,
           ENCRE)
    ecrire(78, y + 78,
           f"★  L'ÉTALON VOIT LE SAUT : sur une matière dont les frontières sont posées, un ruban "
           f"qui les traverse perd {_fr(e['cout_median_du_saut'], 2)} pas là où DÉRIVER autant sans "
           f"traverser n'en coûte", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     que {_fr(e['cout_median_de_la_derive'], 2)}, et où mélanger les couches en rend "
           f"{_fr(e['cout_median_du_nul'], 2)}. Les deux groupes ont la MÊME montée : seule leur "
           "profondeur de départ change.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"{signe}  ET SUR LE ROULEAU C'EST EXACTEMENT L'INVERSE : traverser coûte "
           f"{_fr(v['ce_que_le_saut_coute'], 3)} pas sur {v['chunks_lus']} chunks, quand DÉRIVER en "
           f"coûte {_fr(v['ce_que_la_derive_coute'], 3)}", moyen, coul_v)
    ecrire(78, y + 166,
           f"     ({_fr(v['ce_que_la_derive_coute_um'], 2)} µm) : {_fr(v['pas_en_traversant'], 2)} "
           f"pas en traversant contre {_fr(v['pas_en_restant'], 2)} en restant, soit "
           f"{_fr(v['il_en_reste_la_part'], 4)}. La fibre témoigne d'un MOUVEMENT", moyen, coul_v)
    ecrire(78, y + 194,
           "     EN PROFONDEUR, pas d'un changement de feuille.", moyen, coul_v)
    ecrire(78, y + 212,
           "⚠⚠ Ce que la tranche ne dit pas : que le témoin suffise à PILOTER un transfert — il dit "
           "qu'un saut se voit, pas où il faut aller. ⚠ Et la frontière du rouleau est le creux de "
           "`180`, pas une vérité.", petit, GRIS)

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

    # ★★★★ LES DEUX LECTURES APPARIEES SONT LUES DE PLUSIEURS COTES : sans les deux, « traverser
    # coute » serait une phrase et non une comparaison.
    for cle, val in (("pas_en_restant", 41.25), ("pas_en_traversant", 19.75)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, 2) in t)
        v(f"★★★★ {cle} est lue de PLUSIEURS côtés", n >= 2, f"{n} mentions")

    # ★★★★ LE COUT ET LE NUL SONT LUS ENSEMBLE : un cout sans son nul se lirait comme un resultat.
    for cle, val in (("ce_que_le_saut_coute", 21.5), ("ce_que_le_nul_rend", 3.25)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if _fr(val, 2) in t)
        v(f"★★★★ {cle} est lu de PLUSIEURS côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET L'ETALON EST LU DES DEUX COTES : c'est lui qui rend le rouleau interpretable.
    faux = copy.deepcopy(d)
    faux["letalon"]["cout_median_du_saut"] = 17.75
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p4 if "17,75" in t)
    v("★★★★ le coût de l'étalon est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET UN ETALON AVEUGLE FAIT REFUSER LA MESURE : un temoin qui ne voit pas un saut
    # construit ne dit rien du rouleau.
    aveugle = copy.deepcopy(d)
    aveugle["le_verdict"]["le_temoin_voit_un_saut_construit"] = False
    refuse = False
    tmp = None
    try:
        import tempfile  # noqa: PLC0415
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(aveugle, fh, ensure_ascii=False)
            tmp = Path(fh.name)
        lire(tmp)
    except ValueError:
        refuse = True
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    v("★★★★ un étalon aveugle fait REFUSER la mesure", refuse)

    # ★★★ CHAQUE RECOUVREMENT DE L'ECHELLE EST DESSINE, AVEC SON COMPTE DE DECALAGES : douze
    # lignes ne tiennent pas dans un panneau, donc c'est le COMPTE qui porte les decalages — et il
    # bougerait si l'un d'eux cessait de couter.
    for k in range(len(d["letalon"]["par_recouvrement"])):
        faux = copy.deepcopy(d)
        faux["letalon"]["par_recouvrement"][k]["cout_median"] = 11.0 + k
        faux["letalon"]["par_recouvrement"][k]["decalages_ou_le_saut_coute"] = 4 + k
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p5 if _fr(11.0 + k, 2) in t)
        m = sum(1 for _x, _y, t, _f in p5 if f"{4 + k} / " in t)
        v(f"★★★ le recouvrement {k} est dessiné avec son compte", n >= 1 and m >= 1,
          f"{n} coûts, {m} comptes")
    v("★★★ et le compte des décalages de l'échelle égale celui du verdict",
      sum(x["decalages_lisibles"] for x in d["letalon"]["par_recouvrement"])
      == d["le_verdict"]["decalages_lisibles_de_letalon"],
      str([x["decalages_lisibles"] for x in d["letalon"]["par_recouvrement"]]))

    # ★★★★ CE QUE LA DERIVE COUTE EST LU DES DEUX COTES : sans lui, « le saut ne coute rien » ne
    # dirait pas que c'est le MOUVEMENT qui coute.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["ce_que_la_derive_coute"] = 8.125
    _c, p5b, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p5b if "8,125" in t)
    v("★★★★ ce que la dérive coûte est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ LES TROIS BRANCHES DU TITRE SONT EXERCEES : un titre qui suit la mesure doit pouvoir
    # dire les trois choses, sinon il est un verdict ecrit d'avance.
    branches = []
    for hasard, derive, attendu in ((True, True, "OUI"), (True, False, "pas plus que la dérive"),
                                    (False, False, "NON")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["le_saut_coute_plus_que_le_hasard"] = hasard
        faux["le_verdict"]["le_saut_coute_plus_que_la_derive"] = derive
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p6, 1360) and not textes_hors_cadre(p6, cadres)
          and not textes_qui_se_recouvrent(p6))
    v("★★★★ les trois branches sont distinctes", len(set(branches)) == 3, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_un_ruban_qui_saute_perd_il_sa_fibre.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "un_ruban_qui_saute_perd_il_sa_fibre.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "187_un_ruban_qui_saute_perd_il_sa_fibre.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
