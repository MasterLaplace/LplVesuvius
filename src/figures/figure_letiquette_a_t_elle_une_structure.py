"""L'étiquette a-t-elle une structure ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le compte global : ce que la
marche retient contre ce que la règle se déclenche toute seule. En haut à droite, les douze
segments, et le khi-deux observé posé au milieu de ses mélanges. En bas à gauche, le groupement dans
l'espace, avec le contrôle nommé qui ne discrimine pas. En bas à droite, l'étalon à six faces et la
force DÉRIVÉE de sa face positive.

  uv run python src/figures/figure_letiquette_a_t_elle_une_structure.py \\
      --json docs/mesures/letiquette_a_t_elle_une_structure.json \\
      --sortie docs/images/194_letiquette_a_t_elle_une_structure.png
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

LES_SIX_FACES = (
    ("des segments qui DIFFÈRENT", "les_segments_different_quand_ils_different",
     "les_segments_different", True),
    ("des segments qui ne diffèrent pas",
     "les_segments_ne_different_pas_quand_ils_ne_different_pas", "les_segments_different", False),
    ("une étiquette GROUPÉE", "ca_se_groupe_quand_c_est_groupe",
     "les_chunks_qui_retiennent_se_groupent", True),
    ("une étiquette dispersée", "ca_ne_se_groupe_pas_quand_c_est_disperse",
     "les_chunks_qui_retiennent_se_groupent", False),
    ("un compte au-dessus du hasard", "le_compte_dit_oui_quand_il_le_faut",
     "letiquette_porte_plus_que_le_hasard", True),
    ("un compte dans le hasard", "le_compte_dit_non_quand_il_le_faut",
     "letiquette_porte_plus_que_le_hasard", False),
)


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
    """Le JSON de `letiquette_a_t_elle_une_structure.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES SIX FACES. Trois questions, six faces :
    un instrument qui dirait « oui » partout, ou « non » partout, passerait la moitié du contrôle en
    ne discriminant rien, et les trois silences qu'il autorise ne voudraient rien dire.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "le_verdict", "le_compte_global", "entre_les_segments",
                "dans_lespace"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not d.get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses six faces")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if not v.get("letiquette_porte_plus_que_le_hasard"):
        return "L'étiquette a-t-elle une structure ? — elle ne porte même pas plus que le hasard"
    if v.get("reelle_et_sans_structure"):
        return ("L'étiquette a-t-elle une structure ? — RÉELLE en gros, SANS STRUCTURE en détail")
    return "L'étiquette a-t-elle une structure ? — réelle, et elle en porte une"


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
    reelle = bool(v.get("letiquette_porte_plus_que_le_hasard"))
    sans = bool(v.get("reelle_et_sans_structure"))
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46,
           f"{v['qui_retiennent']} chunks qui retiennent sur {v['chunks']}, {v['segments']} "
           f"segments · {len(d['les_trois_questions'])} questions DÉCLARÉES · {d['tirages']} "
           f"mélanges, donc un seuil de {_fr(v.get('le_seuil_des_trois_questions'), 6)} · "
           f"{v.get('les_observables_deja_cherches')} observables déjà cherchés par `191` et `193`",
           petit, GRIS)

    # ---- panneau 1 : le compte global
    x0, y0, pw, ph = 56, 122, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le compte global — la marche retient-elle plus que la règle ne se "
                        "déclenche ?", moyen, ENCRE)
    hautC = max(float(v["qui_retiennent"]), float(v.get("les_attendus_par_hasard") or 0.0),
                1.0) * 1.25
    for k, (nom, val, coul) in enumerate(
            (("ce que la marche retient", v["qui_retiennent"], CONTRE),
             ("ce que la règle rend toute seule", v.get("les_attendus_par_hasard"), GRIS))):
        yy = y0 + 16 + k * 40
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 16, 570, float(val or 0.0) / hautC, 12, coul)
    ecrire(x0 + 14, y0 + 106,
           f"le taux de faux de `190`, MESURÉ sur quarante réplicats : "
           f"{_fr(d.get('le_taux_de_faux_relu_de_190'), 4)}", 0, GRIS)
    ecrire(x0 + 14, y0 + 126,
           f"la probabilité d'en avoir autant ou plus : "
           f"{_fr(v.get('la_probabilite_du_compte'), 9)}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 146,
           f"le seuil que trois questions déclarées imposent : "
           f"{_fr(v.get('le_seuil_des_trois_questions'), 6)}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 174,
           f"{'★' if reelle else '✗'} L'ÉTIQUETTE PORTE "
           f"{'PLUS' if reelle else 'PAS PLUS'} QUE LE HASARD.", moyen, BON if reelle else ALERTE)
    ecrire(x0 + 14, y0 + 202,
           "⚠ La probabilité est EXACTE, par la loi binomiale : le taux est mesuré et chaque chunk",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 216,
           "est jugé par sa propre famille de dix-neuf tirages. Une permutation n'ajouterait "
           "que du bruit.", petit, GRIS)

    # ---- panneau 2 : entre les segments
    x0, y0, pw, ph = 712, 122, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "entre les segments — diffèrent-ils ?", moyen, ENCRE)
    taux = d["entre_les_segments"].get("les_taux_par_segment") or {}
    hautT = max(list(taux.values()) + [0.01]) * 1.15
    for k, (s, t) in enumerate(taux.items()):
        yy = y0 + 8 + k * 14
        ecrire(x0 + 10, yy, s[:14], 0, GRIS)
        ecrire(x0 + 112, yy, _fr(t, 4), 0, GRIS)
        barre(x0 + 168, yy + 2, 180, float(t) / hautT, 6, CONTRE)
    ecrire(x0 + 366, y0 + 24, f"khi-deux observé  {_fr(v.get('le_khi_deux'), 4)}", 0, ENCRE)
    ecrire(x0 + 366, y0 + 42, f"médiane du nul    {_fr(v.get('le_khi_deux_median_du_nul'), 4)}",
           0, GRIS)
    ecrire(x0 + 366, y0 + 60,
           f"part des nuls plus grands {_fr(v.get('la_part_des_nuls_au_moins_aussi_grands'), 4)}",
           0, GRIS)
    ecrire(x0 + 366, y0 + 92,
           f"{'★' if v.get('les_segments_different') else '✗'} les segments",
           moyen, BON if v.get("les_segments_different") else ALERTE)
    ecrire(x0 + 366, y0 + 112,
           "     diffèrent" if v.get("les_segments_different") else "     NE diffèrent PAS",
           moyen, BON if v.get("les_segments_different") else ALERTE)
    ecrire(x0 + 10, y0 + 194,
           "⚠⚠ Le khi-deux observé est SOUS la médiane du nul : l'étiquette est plus UNIFORME",
           petit, GRIS)
    ecrire(x0 + 10, y0 + 208,
           "que le hasard ne la ferait, ce qui est une information et non un échec.", petit, GRIS)

    # ---- panneau 3 : dans l'espace
    x0, y0, pw, ph = 56, 408, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "dans l'espace — les chunks qui retiennent se groupent-ils ?", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 12,
           "Le nul mélange l'étiquette À L'INTÉRIEUR de chaque segment : chacun garde son", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 28,
           "compte, seule la place change. C'est le seul nul qui isole le groupement de", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 44, "l'effet de segment que la deuxième question mesure déjà.", petit,
           ENCRE)
    hautD = max(float(v.get("la_distance_moyenne") or 0.0),
                float(v.get("la_distance_moyenne_du_nul") or 0.0), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("la distance moyenne observée", v.get("la_distance_moyenne"), CONTRE),
             ("celle des mélanges", v.get("la_distance_moyenne_du_nul"), GRIS))):
        yy = y0 + 76 + k * 40
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 300, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 16, 570, float(val or 0.0) / hautD, 12, coul)
    ecrire(x0 + 14, y0 + 162,
           f"part des mélanges au moins aussi serrés : "
           f"{_fr(v.get('la_part_des_nuls_au_moins_aussi_serres'), 4)}", 0, ENCRE)
    ecrire(x0 + 14, y0 + 190,
           f"{'★' if v.get('les_chunks_qui_retiennent_se_groupent') else '✗'} LES CHUNKS QUI "
           f"RETIENNENT NE SE GROUPENT "
           f"{'' if v.get('les_chunks_qui_retiennent_se_groupent') else 'PAS'}.", moyen,
           BON if v.get("les_chunks_qui_retiennent_se_groupent") else ALERTE)
    ecrire(x0 + 14, y0 + 226,
           f"⚠⚠⚠ Un CONTRÔLE NOMMÉ, incapable de discriminer : le compte de paires voisines vaut",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 240,
           f"{d['dans_lespace'].get('les_paires_voisines')} pour l'observé comme pour les "
           f"mélanges — le treillis est trop lâche pour que deux positions", petit, ALERTE)
    ecrire(x0 + 14, y0 + 254,
           "y soient adjacentes. Le dire est plus utile que de le taire, et c'est la distance",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 268, "moyenne qui répond.", petit, ALERTE)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 712, 408, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — trois questions, six faces", moyen, ENCRE)
    for k, (nom, cle, lu, attendu) in enumerate(LES_SIX_FACES):
        yy = y0 + 10 + k * 20
        x = e.get(cle) or {}
        obtenu = bool(x.get(lu))
        ok = obtenu == attendu
        ecrire(x0 + 14, yy, nom, 0, ENCRE)
        ecrire(x0 + 300, yy, f"attendu {attendu}", 0, GRIS)
        ecrire(x0 + 420, yy, f"{'★' if ok else '✗'} lu {obtenu}", 0, BON if ok else ALERTE)
    ecrire(x0 + 14, y0 + 140,
           f"la force DÉRIVÉE de la face positive : "
           f"{v.get('la_force_derivee_de_letalon')} chunks chauds sur 7", 0, ENCRE)
    ecrire(x0 + 14, y0 + 160, "la courbe de sensibilité, par force posée", 0, GRIS)
    courbe = d.get("la_courbe_de_sensibilite") or {}
    for k, (f, part) in enumerate(sorted(courbe.items(), key=lambda kv: int(kv[0]))):
        yy = y0 + 180 + (k // 4) * 18
        ecrire(x0 + 14 + (k % 4) * 140, yy, f"{f}/7 → {_fr(part, 4)}", 0,
               BON if float(part) >= 1.0 else GRIS)
    ecrire(x0 + 14, y0 + 228,
           "⚠⚠⚠ Une face positive MARGINALE n'est pas une face positive : un effet posé qui n'est",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 242,
           "vu qu'une fois sur cinq ne dit pas que l'instrument voit. La force est donc DÉRIVÉE",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 256, "de cette courbe — la plus petite vue à TOUS les réplicats.", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 278,
           f"★ l'étalon sépare ses six faces : {d.get('letalon_separe')}", 0, BON)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  L'ÉTIQUETTE EST RÉELLE : {v['qui_retiennent']} chunks sur {v['chunks']} "
           f"retiennent contre {_fr(v.get('les_attendus_par_hasard'), 4)} attendus au taux de faux "
           f"MESURÉ de `190` — une probabilité de "
           f"{_fr(v.get('la_probabilite_du_compte'), 9)},", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     bien sous le seuil de {_fr(v.get('le_seuil_des_trois_questions'), 6)} que trois "
           f"questions déclarées imposent. Ce que `190` avait trouvé n'est donc pas du bruit.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  MAIS ELLE N'A AUCUNE STRUCTURE : les {v['segments']} segments ne diffèrent pas "
           f"(khi-deux {_fr(v.get('le_khi_deux'), 4)} contre une médiane de nul de "
           f"{_fr(v.get('le_khi_deux_median_du_nul'), 4)}, donc plus UNIFORME que le hasard),",
           moyen, ALERTE)
    ecrire(78, y + 106,
           f"     et les chunks qui retiennent ne se groupent pas — distance moyenne "
           f"{_fr(v.get('la_distance_moyenne'), 4)} contre {_fr(v.get('la_distance_moyenne_du_nul'), 4)} "
           f"au nul, {_fr(v.get('la_part_des_nuls_au_moins_aussi_serres'), 4)} des mélanges étant "
           f"plus serrés.", moyen, ALERTE)
    ecrire(78, y + 138,
           f"★  CE QUI RESSERRE LES DEUX NÉGATIFS DE `191` ET DE `193` : ce que la marche retient "
           f"est réel, réparti uniformément, sans voisinage, et aucun des "
           f"{v.get('les_observables_deja_cherches')} observables", moyen, ENCRE)
    ecrire(78, y + 166,
           "     déclarés ne le touche. Ce n'est pas une propriété du segment ni du lieu : c'est "
           "une propriété du chunk que rien de ce qui est mesuré ne nomme.", moyen, ENCRE)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche ne dit pas : ce qu'est cette propriété. Elle dit qu'elle existe, "
           "et où elle n'est pas.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.075, 4), _fr(6.075, 4)) == ("90", "0,075", "6,075"),
      f"{(_fr(90.0, 0), _fr(0.075, 4), _fr(6.075, 4))}")
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
    # ⚠⚠⚠ UNE GARDE QUE `textes_hors_cadre` NE DONNE PAS : elle ne signale pas un texte qui COMMENCE
    # sous un cadre. Defaut vu en REGARDANT l'image de `190`.
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    # ★★★★ CHAQUE QUESTION A SES DEUX NOMBRES, ET ILS SONT LUS DES DEUX COTES : l'observe sans son
    # nul ne dirait rien, et le nul sans l'observe non plus.
    for cle, val, dec in (("qui_retiennent", 37, 0),
                          ("les_attendus_par_hasard", 9.8765, 4),
                          ("la_probabilite_du_compte", 0.00042424, 9),
                          ("le_khi_deux", 31.3131, 4),
                          ("le_khi_deux_median_du_nul", 27.2727, 4),
                          ("la_distance_moyenne", 151.5151, 4),
                          ("la_distance_moyenne_du_nul", 191.9191, 4),
                          ("la_part_des_nuls_au_moins_aussi_serres", 0.6363, 4),
                          ("le_seuil_des_trois_questions", 0.030303, 6)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2
                if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★ CHAQUE SEGMENT EST DESSINE AVEC SON TAUX.
    taux = d["entre_les_segments"]["les_taux_par_segment"]
    for k, s in enumerate(list(taux)[:3]):
        faux = copy.deepcopy(d)
        faux["entre_les_segments"]["les_taux_par_segment"][s] = 0.7171 + k / 1e4
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le segment {k} est dessiné avec son taux",
          any(_fr(0.7171 + k / 1e4, 4) in t for _x, _y, t, _f in p3))

    # ★★★ CHAQUE FACE DE L'ETALON EST DESSINEE AVEC SON ATTENDU ET SON LU.
    for nom, cle, lu, attendu in LES_SIX_FACES:
        faux = copy.deepcopy(d)
        faux["letalon"][cle][lu] = not attendu
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la face « {nom} » suit ce que la mesure dit",
          any(f"✗ lu {not attendu}" in t for _x, _y, t, _f in p4))

    # ★★★★ LE CONTROLE NOMME QUI NE DISCRIMINE PAS EST DESSINE : le taire serait le cacher.
    faux = copy.deepcopy(d)
    faux["dans_lespace"]["les_paires_voisines"] = 77
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le contrôle nommé incapable de discriminer est dessiné",
      any("77" in t for _x, _y, t, _f in p5))

    # ★★★ LA FORCE DERIVEE ET LA COURBE DE SENSIBILITE SONT DESSINEES.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["la_force_derivee_de_letalon"] = 6
    _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★ la force dérivée est dessinée",
      any("6 chunks chauds" in t for _x, _y, t, _f in p6))
    faux = copy.deepcopy(d)
    faux["la_courbe_de_sensibilite"]["3"] = 0.3131
    _c, p7, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★ la courbe de sensibilité est dessinée",
      any(_fr(0.3131, 4) in t for _x, _y, t, _f in p7))

    # ★★★★ UN ETALON QUI NE SEPARE PAS FAIT REFUSER LA MESURE.
    import tempfile  # noqa: PLC0415

    rouge = copy.deepcopy(d)
    rouge["letalon_separe"] = False
    refuse, tmp = False, None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(rouge, fh, ensure_ascii=False)
            tmp = Path(fh.name)
        lire(tmp)
    except ValueError:
        refuse = True
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    v("★★★★ un étalon qui ne sépare pas fait REFUSER la mesure", refuse)

    # ★★★★ LES TROIS BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for reelle, sans, attendu in ((True, True, "SANS STRUCTURE"), (True, False, "en porte une"),
                                  (False, False, "même pas plus")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["letiquette_porte_plus_que_le_hasard"] = reelle
        faux["le_verdict"]["reelle_et_sans_structure"] = sans
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p8, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p8, 1360) and not textes_hors_cadre(p8, cadres)
          and not textes_qui_se_recouvrent(p8))
    v("★★★★ les trois branches sont distinctes", len(set(branches)) == 3, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_letiquette_a_t_elle_une_structure.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "letiquette_a_t_elle_une_structure.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "194_letiquette_a_t_elle_une_structure.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
