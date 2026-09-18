"""Que montrent ces deux vues — et à quelle échelle la chaîne cherchait-elle ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les trois axes du cube mis à la
même épreuve : lequel porte une période, et laquelle. En haut à droite, le serpentement du maillage
publié — de combien la surface dépliée quitte son feuillet, en fractions de pli. En bas à gauche, la
forme réelle d'un segment déplié et la part qu'une tuile de `195` et `196` en montre. En bas à
droite, l'étalon et ses faces.

  uv run python src/figures/figure_que_montrent_ces_deux_vues.py \\
      --json docs/mesures/que_montrent_ces_deux_vues.json \\
      --sortie docs/images/197_que_montrent_ces_deux_vues.png
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

LES_TROIS_AXES = ("la profondeur", "la hauteur", "la largeur")


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
    """Le JSON de `que_montrent_ces_deux_vues.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES FACES, OU DONT LES TROIS AXES NE SONT PAS
    TOUS MESURÉS. Ne mesurer que l'axe qu'on croit bon serait une vérification incapable d'échouer,
    et une figure qui l'afficherait donnerait à une supposition l'allure d'un résultat.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("par_axe", "le_serpentement", "la_forme_des_volumes", "la_part_montree",
                "letalon"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    manquants = [a for a in LES_TROIS_AXES if a not in d["par_axe"]]
    if manquants:
        raise ValueError(f"{chemin} : axes non mesurés {manquants}")
    e = d["letalon"]
    if not e.get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas la pile plate de la pile inclinée")
    if not e.get("seul_le_premier_axe_porte_la_periode"):
        raise ValueError(f"{chemin} : l'étalon ne distingue pas les trois axes")
    if not e.get("le_suivi_par_argmax_fabrique_du_serpentement"):
        raise ValueError(f"{chemin} : le contrôle nommé ne fabrique aucun serpentement, "
                         "donc il ne montre plus ce qu'il est là pour montrer")
    if not d["la_part_montree"].get("decidable"):
        raise ValueError(f"{chemin} : la part montrée n'a pas été mesurée")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    par = d["par_axe"]
    prof = par[LES_TROIS_AXES[0]]
    autres = max(par[a]["depassent_tous_les_melanges"] for a in LES_TROIS_AXES[1:])
    if prof["depassent_tous_les_melanges"] <= autres:
        return ("Que montrent ces deux vues ? — AUCUN AXE NE SE DISTINGUE, "
                "la profondeur pas plus qu'une autre")
    return ("Que montrent ces deux vues ? — la profondeur porte, "
            "et la fenêtre est minuscule")


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

    par, ser = d["par_axe"], d["le_serpentement"]
    part, e = d["la_part_montree"], d["letalon"]
    forme = next((v for v in d["la_forme_des_volumes"].values() if v.get("decidable")), {})

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"{d['les_cubes']['rendus']} cubes sur {d['les_cubes']['demandes']} · "
           f"pas d'un pli {_fr(d['le_pas_dun_pli_en_voxels'], 4)} voxels · "
           f"{d['tirages']} mélanges par axe, donc {_fr(par[LES_TROIS_AXES[0]].get('les_attendus_par_hasard'), 4)} "
           f"cube attendu par hasard · plage de recalage {d['la_plage_de_recalage']} voxels",
           petit, GRIS)

    # ---- panneau 1 : les trois axes
    x0, y0, pw, ph = 56, 122, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois axes, à la même épreuve — lequel traverse l'empilement ?",
           moyen, ENCRE)
    haut = max(float(par[a]["depassent_tous_les_melanges"]) for a in LES_TROIS_AXES) * 1.2 or 1.0
    for k, a in enumerate(LES_TROIS_AXES):
        x = par[a]
        yy = y0 + 14 + k * 54
        ecrire(x0 + 14, yy, a, 0, ENCRE if k == 0 else GRIS)
        ecrire(x0 + 130, yy,
               f"{x['depassent_tous_les_melanges']} / {x['cubes_lus']} dépassent tous les mélanges",
               0, ENCRE if k == 0 else GRIS)
        barre(x0 + 14, yy + 16, 420, float(x["depassent_tous_les_melanges"]) / haut, 10,
              CONTRE if k == 0 else TRAIT)
        ecrire(x0 + 448, yy + 14,
               f"période {_fr(x['la_periode_mediane_en_voxels'], 1)} vx "
               f"({_fr(x['la_periode_mediane_en_um'], 1)} µm)", 0, GRIS)
        ecrire(x0 + 14, yy + 32,
               f"autocorrélation médiane {_fr(x['lautocorrelation_mediane'], 6)}", 0, GRIS)
    ecrire(x0 + 14, y0 + 182,
           "⚠⚠ La période médiane de la profondeur n'est PAS celle d'un pli : le premier maximum",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 196,
           "local est le plus PETIT décalage où le profil se répète, donc une structure plus fine",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 210,
           "que le pli le remporte. Cent neuf couches ne portent qu'un pli et demi.", petit,
           ALERTE)

    # ---- panneau 2 : le serpentement
    x0, y0, pw, ph = 712, 122, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le serpentement — de combien la surface quitte son feuillet", moyen,
           ENCRE)
    for k, (nom, val, unite) in enumerate((
            ("médian", ser["le_median_en_voxels"], "voxels"),
            ("médian, en plis", ser["le_median_en_plis"], "pli"),
            ("maximal", ser["le_maximal_en_voxels"], "voxels"))):
        yy = y0 + 12 + k * 26
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 190, yy, f"{_fr(val, 6)} {unite}", 0, ENCRE)
        barre(x0 + 320, yy + 2, 250,
              float(val or 0.0) / max(1e-9, float(ser["le_maximal_en_voxels"] or 1.0))
              if unite == "voxels" else float(val or 0.0), 8, CONTRE)
    ecrire(x0 + 14, y0 + 96,
           f"coupes lues {ser['coupes_lues']}   ·   coupes dont des colonnes SATURENT "
           f"{ser['les_coupes_avec_colonnes_saturees']}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 116,
           f"colonnes saturées en tout {ser['les_colonnes_saturees_en_tout']}", 0, GRIS)
    ecrire(x0 + 14, y0 + 144,
           "⚠⚠⚠ La saturation est la LIMITE du recalage, nommée plutôt que tue : un décalage de",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 158,
           "plus d'une demi-période se confond avec celui d'un pli entier. Sans ce compte, une",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 172, "pile très inclinée rendrait un petit serpentement.", petit, ALERTE)
    ecrire(x0 + 14, y0 + 196,
           "★ C'est la quantité que le déroulage doit corriger, et la chaîne ne l'avait pas.",
           petit, ENCRE)

    # ---- panneau 3 : la forme et la part montrée
    x0, y0, pw, ph = 56, 408, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "à quelle échelle la chaîne cherchait-elle ?", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("un volume de surface", f"{forme.get('couches')} couches × "
                                     f"{forme.get('hauteur')} × {forme.get('largeur')}"),
            ("son épaisseur", f"{_fr(forme.get('epaisseur_en_plis'), 4)} pli "
                              f"({_fr(forme.get('epaisseur_um'), 2)} µm)"),
            ("sa surface dépliée", f"{_fr(forme.get('hauteur_mm'), 3)} × "
                                   f"{_fr(forme.get('largeur_mm'), 3)} mm"),
            ("l'aire médiane d'un segment",
             f"{_fr(part['laire_mediane_dun_segment_mm2'], 2)} mm²"),
            ("une tuile de `195` et `196`",
             f"{_fr(part['le_cote_de_la_tuile_um'], 2)} µm de côté = "
             f"{_fr(part['laire_dune_tuile_mm2'], 6)} mm²"),
            ("une tuile couvre", f"un segment sur "
                                 f"{part['une_tuile_pour_combien_de_segment']}"),
            ("la planche entière couvre",
             f"un segment sur {part['une_planche_pour_combien_de_segment']}"))):
        yy = y0 + 12 + k * 22
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 268, yy, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 180,
           "⚠⚠⚠ CE QUE CE PANNEAU DIT DES DEUX TRANCHES PRÉCÉDENTES : elles ont fait juger trente",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 194,
           "vignettes de trois dixièmes de millimètre sur une surface de plus de cent millimètres.",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 208,
           "Leurs résultats tiennent — l'étiquette de `194` est réelle, les négatifs sont bornés —",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 222,
           "mais la question « ce cube porte-t-il la marque ? » n'est peut-être pas à la bonne",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 236, "échelle.", petit, ALERTE)
    ecrire(x0 + 14, y0 + 262,
           "⚠ Le chiffre n'existait pas : les deux tranches n'ont jamais dit ce qu'une vignette",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 276, "couvre du déplié.", petit, GRIS)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 712, 408, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — une matière dont la réponse est construite", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, "un cube dont SEUL le premier axe est périodique", 0, ENCRE)
    for k, a in enumerate(LES_TROIS_AXES):
        x = e["par_axe"][a]
        yy = y0 + 34 + k * 18
        ok = bool(x.get("elle_depasse_tous_les_melanges")) == (k == 0)
        ecrire(x0 + 28, yy, a, 0, GRIS)
        ecrire(x0 + 150, yy,
               f"{'★' if ok else '✗'} dépasse {x.get('elle_depasse_tous_les_melanges')}", 0,
               BON if ok else ALERTE)
        ecrire(x0 + 300, yy, f"période {x.get('la_periode_en_voxels')} vx", 0, GRIS)
    ecrire(x0 + 14, y0 + 100,
           f"une pile PLATE serpente de "
           f"{_fr(e['une_pile_plate']['le_serpentement_en_voxels'], 4)} voxel", 0, BON)
    ecrire(x0 + 14, y0 + 120,
           f"une pile INCLINÉE d'un quart de pli "
           f"({_fr(e['la_pente_posee_en_plis'], 4)}) serpente de "
           f"{_fr(e['une_pile_inclinee']['le_serpentement_en_voxels'], 4)} voxels", 0, BON)
    ecrire(x0 + 14, y0 + 134,
           f"et elle ne sature aucune colonne : "
           f"{e['une_pile_inclinee']['les_colonnes_saturees']}", 0, GRIS)
    ecrire(x0 + 14, y0 + 148,
           f"une pile TROP inclinée en sature "
           f"{e['une_pile_trop_inclinee']['les_colonnes_saturees']}", 0, GRIS)
    ecrire(x0 + 14, y0 + 168,
           f"★ l'étalon sépare ses faces : {e['letalon_separe']}", 0, BON)
    argmax = e["la_meme_pile_suivie_par_la_bande_la_plus_claire"]
    ecrire(x0 + 14, y0 + 188,
           f"✗ LA MÊME PILE PLATE, suivie par la bande la plus CLAIRE : "
           f"{_fr(argmax['le_serpentement_en_voxels'], 4)} voxels", 0, ALERTE)
    ecrire(x0 + 14, y0 + 216,
           "⚠⚠⚠ C'EST LA RÈGLE RÉFUTÉE, PORTÉE COMME CONTRÔLE NOMMÉ : c'est la première qui",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 230,
           "vient à l'esprit, et l'argmax d'une colonne saute d'une bande à l'autre dès qu'il",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 244,
           "y en a deux. Le saut se lit alors comme un serpentement géant sur une pile",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 258,
           "parfaitement plate. Le recalage sur le profil moyen ne saute pas.", petit, ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    prof = par[LES_TROIS_AXES[0]]
    ecrire(78, y + 18,
           f"★  LA PROFONDEUR EST BIEN L'AXE QUI TRAVERSE L'EMPILEMENT : "
           f"{prof['depassent_tous_les_melanges']} cubes sur {prof['cubes_lus']} y dépassent tous "
           f"leurs mélanges contre "
           f"{_fr(prof.get('les_attendus_par_hasard'), 4)} attendu par hasard, et son", moyen,
           ENCRE)
    ecrire(78, y + 46,
           f"     autocorrélation médiane vaut {_fr(prof['lautocorrelation_mediane'], 6)} quand "
           f"celles des deux autres axes sont NÉGATIVES. Les deux vues de `195` et `196` montrent "
           f"donc ce qu'elles annonçaient.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"★  ET LE CHIFFRE QUI MANQUAIT AU DÉROULAGE EST LÀ : le maillage publié quitte son "
           f"feuillet de {_fr(ser['le_median_en_voxels'], 4)} voxels en médiane, soit "
           f"{_fr(ser['le_median_en_plis'], 6)} pli, sur trois dixièmes de", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     millimètre de largeur — mais jusqu'à {_fr(ser['le_maximal_en_voxels'], 4)} "
           f"voxels, et {ser['les_coupes_avec_colonnes_saturees']} coupes sur "
           f"{ser['coupes_lues']} saturent la plage. La tenue est bonne en général et perdue par "
           f"endroits.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"⚠⚠⚠ ET L'ÉCHELLE EST LE VRAI ENSEIGNEMENT : une tuile couvre un segment sur "
           f"{part['une_tuile_pour_combien_de_segment']}, la planche entière un sur "
           f"{part['une_planche_pour_combien_de_segment']}. La question « ce cube", moyen, ALERTE)
    ecrire(78, y + 166,
           "     porte-t-il la marque ? » a été posée dans une fenêtre d'un cent-millième d'un "
           "segment, alors que le prix demande CENT POUR CENT du recto.", moyen, ALERTE)
    ecrire(78, y + 198,
           "⚠ Cette tranche ne juge aucune étiquette et ne cherche aucun observable : elle DÉCRIT "
           "l'instrument, parce que deux tranches publiées reposaient dessus sans l'avoir vérifié.",
           petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.055491, 6), _fr(4.0, 4)) == ("90", "0,055491", "4"),
      f"{(_fr(90.0, 0), _fr(0.055491, 6), _fr(4.0, 4))}")
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

    # ★★★★ CHAQUE AXE EST DESSINE AVEC SON COMPTE ET SA PERIODE : n'en dessiner qu'un rendrait la
    # comparaison invisible, or c'est ELLE que le panneau existe pour montrer.
    for k, a in enumerate(LES_TROIS_AXES):
        faux = copy.deepcopy(d)
        faux["par_axe"][a]["depassent_tous_les_melanges"] = 23 + k
        faux["par_axe"][a]["la_periode_mediane_en_voxels"] = 37.1 + k
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ l'axe « {a} » porte son compte et sa période",
          any(f"{23 + k} / " in t for _x, _y, t, _f in p2)
          and any(_fr(37.1 + k, 1) in t for _x, _y, t, _f in p2))

    # ★★★★ LES DEUX ECRITURES DU SERPENTEMENT, ET LA SATURATION, SONT LUES.
    for cle, val, dec in (("le_median_en_voxels", 13.75, 4),
                          ("le_median_en_plis", 0.191919, 6),
                          ("le_maximal_en_voxels", 47.25, 4),
                          ("les_coupes_avec_colonnes_saturees", 12, 0)):
        faux = copy.deepcopy(d)
        faux["le_serpentement"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ LA PART MONTREE EST DESSINEE, ET C'EST TOUT L'ENSEIGNEMENT DE LA TRANCHE.
    faux = copy.deepcopy(d)
    faux["letalon"]["la_meme_pile_suivie_par_la_bande_la_plus_claire"][
        "le_serpentement_en_voxels"] = 81.75
    _c, pa, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le contrôle nommé est dessiné avec SON chiffre mesuré",
      any(_fr(81.75, 4) in t for _x, _y, t, _f in pa))

    for cle, val in (("une_tuile_pour_combien_de_segment", 424242),
                     ("une_planche_pour_combien_de_segment", 31313)):
        faux = copy.deepcopy(d)
        faux["la_part_montree"][cle] = val
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ {cle} est lu des DEUX côtés",
          sum(1 for _x, _y, t, _f in p4 if str(val) in t) >= 2)

    # ★★★ LE TITRE SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["par_axe"][LES_TROIS_AXES[0]]["depassent_tous_les_melanges"] = 0
    v("★★★★ un axe de profondeur qui ne se distingue pas change le titre",
      "AUCUN AXE" in le_titre(faux), le_titre(faux))
    v("★★★ et le titre observé dit l'inverse", "la profondeur porte" in le_titre(d),
      le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU DONT L'ETALON NE SEPARE PAS EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas ses piles"),
            (lambda x: x["letalon"].__setitem__("seul_le_premier_axe_porte_la_periode", False),
             "dont l'étalon ne distingue pas les axes"),
            (lambda x: x["par_axe"].pop(LES_TROIS_AXES[2]), "à qui il manque un axe"),
            (lambda x: x["la_part_montree"].__setitem__("decidable", False),
             "sans part montrée"),
            (lambda x: x["letalon"].__setitem__(
                "le_suivi_par_argmax_fabrique_du_serpentement", False),
             "dont le contrôle nommé ne fabrique rien"),
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

    print(f"figure_que_montrent_ces_deux_vues.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "que_montrent_ces_deux_vues.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "197_que_montrent_ces_deux_vues.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
