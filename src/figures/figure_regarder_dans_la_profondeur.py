"""Regarder dans la profondeur — deux épreuves déclarées, deux lois exactes, deux silences.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'épreuve de l'assignation, sa
distribution entière et le seuil que la MOITIÉ de la garantie impose. En haut à droite, l'épreuve
appariée, déclarée avant la lecture, avec ses paires muettes. En bas à gauche, la sensibilité à un
trait de TEXTURE et les quatre contrôles croisés qui séparent les deux lecteurs. En bas à droite, la
vue déclarée et ce que `195` rendait sur les mêmes cubes.

  uv run python src/figures/figure_regarder_dans_la_profondeur.py \\
      --json docs/mesures/regarder_dans_la_profondeur.json \\
      --sortie docs/images/196_regarder_dans_la_profondeur.png
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

LES_QUATRE_CROISES = (
    ("une texture, lue par le lecteur de TEXTURE", "la_texture_vue_par_le_lecteur_de_texture",
     True),
    ("une texture, lue par celui de luminosité", "la_texture_vue_par_le_lecteur_de_luminosite",
     False),
    ("une luminosité, lue par celui de LUMINOSITÉ",
     "la_luminosite_vue_par_le_lecteur_de_luminosite", True),
    ("une luminosité, lue par celui de texture", "la_luminosite_vue_par_le_lecteur_de_texture",
     False),
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


def _plier(texte: str, largeur: int) -> list[str]:
    lignes, courante = [], ""
    for mot in str(texte).split():
        if courante and len(courante) + 1 + len(mot) > largeur:
            lignes.append(courante)
            courante = mot
        else:
            courante = f"{courante} {mot}".strip()
    if courante:
        lignes.append(courante)
    return lignes


def lire(chemin: Path) -> dict:
    """Le JSON de `regarder_dans_la_profondeur.py`, levé.

    ⚠⚠⚠ REFUSE UNE MESURE NON LEVEE, UNE LECTURE ABSENTE, ET UN ETALON DONT LES QUATRE CONTROLES
    CROISES NE SEPARENT PAS LES DEUX LECTEURS. Sans cette derniere condition, « la sensibilite a un
    trait de texture » ne serait qu'un nom : un lecteur qui monterait aussi avec la luminosite
    mesurerait ce que `195` mesurait deja, et le second silence ne bornerait rien de neuf.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("la_loi_exacte", "la_sensibilite_de_texture", "les_controles_croises",
                "lappariement", "les_cubes", "la_planche"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d.get("la_cle"):
        raise ValueError(f"{chemin} : la mesure n'est pas levée")
    if not d.get("la_lecture_deposee"):
        raise ValueError(f"{chemin} : aucune lecture n'a été déposée")
    for cle in ("la_note", "la_note_appariee"):
        if not (d.get(cle) or {}).get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if d.get("ce_que_195_rendait") is None:
        raise ValueError(f"{chemin} : ce que `195` a rendu n'est pas relu, "
                         "donc la comparaison n'aurait pas de producteur")
    if d["la_sensibilite_de_texture"].get("la_force_quil_faut") is None:
        raise ValueError(f"{chemin} : aucune force de texture dérivée, donc rien n'est borné")
    k = d["les_controles_croises"]
    if not croises_separent(k):
        raise ValueError(f"{chemin} : les contrôles croisés ne séparent pas les deux lecteurs")
    return d


def croises_separent(k: dict) -> bool:
    """Chaque lecteur voit-il SON trait à tous les réplicats, et pas celui de l'autre ?"""
    return all((float(k.get(cle, 0.0)) >= 1.0) if attendu else (float(k.get(cle, 1.0)) < 1.0)
               for _nom, cle, attendu in LES_QUATRE_CROISES)


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    v = d["le_verdict"]
    if v.get("loeil_separe_sur_lassignation") and v.get("loeil_separe_sur_les_paires"):
        return "Regarder dans la profondeur — L'ŒIL SÉPARE SUR LES DEUX ÉPREUVES"
    if v.get("loeil_separe"):
        return "Regarder dans la profondeur — L'ŒIL SÉPARE SUR UNE DES DEUX ÉPREUVES DÉCLARÉES"
    n = d["la_note"]
    if int(n["les_justes"]) > float(n["les_attendus_par_hasard"]):
        return ("Regarder dans la profondeur — MIEUX QUE LE HASARD, PAS ASSEZ POUR ÊTRE PUBLIÉ")
    return "Regarder dans la profondeur — l'œil ne sépare pas davantage qu'en surface"


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

    def histogramme(x0, y0, dist, cle, seuil, observe, largeur, hauteur):
        haut = max(x["probabilite"] for x in dist) * 1.12 if dist else 1.0
        pas = max(6, int(largeur / max(1, len(dist))))
        for x in dist:
            k = int(x[cle])
            h = hauteur * float(x["probabilite"]) / haut
            gx = x0 + k * pas
            coul = (CONTRE if k == int(observe)
                    else ALERTE if seuil is not None and k >= int(seuil) else TRAIT)
            art.rectangle([gx, y0 + hauteur - h, gx + pas - 6, y0 + hauteur], fill=coul)
            points.append((gx + pas - 6, y0 + hauteur))
            ecrire(gx + 3, y0 + hauteur + 4, f"{k}", 0, GRIS if k % 2 else ENCRE)
        if seuil is not None:
            xs = x0 + int(seuil) * pas - 3
            art.line([xs, y0 - 4, xs, y0 + hauteur + 2], fill=ALERTE, width=2)
            traits.append((xs, y0 - 4, y0 + hauteur + 2))

    loi, note = d["la_loi_exacte"], d["la_note"]
    ap, sens = d["la_note_appariee"], d["la_sensibilite_de_texture"]
    crois, cub = d["les_controles_croises"], d["les_cubes"]
    pl = d["la_planche"]

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"{loi['tuiles']} coupes de {pl['hauteur']}×{pl['largeur']} voxels à la rangée médiane "
           f"· {len(d['les_deux_epreuves'])} épreuves DÉCLARÉES avant la lecture, donc une garantie "
           f"de {_fr(d['la_garantie_par_epreuve'], 3)} chacune · nuls EXACTS", petit, GRIS)

    # ---- panneau 1 : l'assignation
    x0, y0, pw, ph = 56, 122, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'assignation — quinze tuiles désignées parmi trente", moyen, ENCRE)
    histogramme(x0 + 26, y0 + 14, loi["la_distribution"], "justes", loi["le_seuil"],
                note["les_justes"], 544, 92)
    ecrire(x0 + 26, y0 + 130,
           f"justes {note['les_justes']}   ·   attendus "
           f"{_fr(note['les_attendus_par_hasard'], 1)}   ·   "
           f"P = {_fr(note['la_probabilite'], 7)}   ·   seuil {loi['le_seuil']}", 0, ENCRE)
    sep1 = bool(note.get("loeil_separe"))
    ecrire(x0 + 26, y0 + 152,
           f"{'★' if sep1 else '✗'} l'œil {'SÉPARE' if sep1 else 'NE SÉPARE PAS'} "
           f"sur cette épreuve.", moyen, BON if sep1 else ALERTE)
    ecrire(x0 + 26, y0 + 180,
           f"⚠⚠ `195` rendait {d['ce_que_195_rendait']} justes sur la couche du milieu des "
           f"MÊMES cubes. La coupe", petit, GRIS)
    ecrire(x0 + 26, y0 + 194,
           "en profondeur en rend davantage, mais la comparaison des deux tranches n'a PAS été",
           petit, GRIS)
    ecrire(x0 + 26, y0 + 208,
           "déclarée : c'est une observation, pas une épreuve, et elle ne se publie pas comme telle.",
           petit, GRIS)

    # ---- panneau 2 : les paires
    x0, y0, pw, ph = 712, 122, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les paires — déclarée AVANT la lecture, ce que `195` s'était interdit",
           moyen, ENCRE)
    histogramme(x0 + 22, y0 + 14, ap["la_distribution"], "bonnes", ap["le_seuil"],
                ap["les_bonnes_designations"], 520, 92)
    ecrire(x0 + 22, y0 + 130,
           f"bonnes {ap['les_bonnes_designations']} sur {ap['les_paires_informatives']} "
           f"informatives   ·   attendues {_fr(ap['les_attendues_par_hasard'], 1)}   ·   "
           f"P = {_fr(ap['la_probabilite'], 7)}", 0, ENCRE)
    ecrire(x0 + 22, y0 + 150,
           f"{ap['les_paires_muettes']} paires MUETTES — l'œil y a désigné les deux tuiles ou "
           f"aucune   ·   seuil {ap['le_seuil']}", 0, GRIS)
    sep2 = bool(ap.get("loeil_separe"))
    ecrire(x0 + 22, y0 + 172,
           f"{'★' if sep2 else '✗'} l'œil {'SÉPARE' if sep2 else 'NE SÉPARE PAS'} "
           f"sur cette épreuve.", moyen, BON if sep2 else ALERTE)
    ecrire(x0 + 22, y0 + 200,
           "⚠ Une paire où l'œil a désigné les deux, ou aucune, ne tranche rien : elle est écartée",
           petit, GRIS)
    ecrire(x0 + 22, y0 + 214,
           "comme une égalité l'est d'un test des signes, et le nul ne porte que sur les autres.",
           petit, GRIS)

    # ---- panneau 3 : la texture et les croisés
    x0, y0, pw, ph = 56, 408, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la sensibilité à un trait de TEXTURE — la dette que `195` laissait", moyen, ENCRE)
    for k, pt in enumerate(sens["la_courbe"]):
        yy = y0 + 10 + k * 20
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 14, yy,
               f"+{int(pt['force']):>3} unité{'s' if int(pt['force']) > 1 else ''} du volume", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 166, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 212, yy + 2, 384, part, 8, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 14, y0 + 176,
           f"force DÉRIVÉE {_fr(sens['la_force_quil_faut'], 0)} unités du volume, à la période d'un "
           f"pli : {_fr(sens['la_periode_en_voxels'], 4)} voxels", 0, ENCRE)
    ecrire(x0 + 14, y0 + 198, "les quatre contrôles croisés, qui séparent les deux lecteurs", 0,
           GRIS)
    for k, (nom, cle, attendu) in enumerate(LES_QUATRE_CROISES):
        yy = y0 + 218 + k * 18
        val = float(crois.get(cle, 0.0))
        ok = (val >= 1.0) if attendu else (val < 1.0)
        ecrire(x0 + 14, yy, nom, 0, ENCRE)
        ecrire(x0 + 330, yy, f"{'★' if ok else '✗'} {_fr(val, 3)}", 0, BON if ok else ALERTE)
        ecrire(x0 + 420, yy, "attendu vue" if attendu else "attendu aveugle", 0, GRIS)

    # ---- panneau 4 : la vue et le prix
    x0, y0, pw, ph = 712, 408, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la vue déclarée, et le prix des deux épreuves", moyen, ENCRE)
    for k, ligne in enumerate(_plier(d.get("la_vue_declaree") or "—", 70)):
        ecrire(x0 + 14, y0 + 10 + k * 16, ligne, 0, ENCRE)
    for k, (nom, val) in enumerate((
            ("cubes demandés / rendus", f"{cub['demandes']} / {cub['rendus']}"),
            ("paires gardées", f"{cub['paires_gardees']}"),
            ("épreuves déclarées avant la lecture", f"{len(d['les_deux_epreuves'])}"),
            ("garantie de la chaîne / par épreuve",
             f"{_fr(2 * d['la_garantie_par_epreuve'], 2)} / "
             f"{_fr(d['la_garantie_par_epreuve'], 3)}"),
            ("niveau de gris COMMUN aux trente",
             f"[{_fr(d['le_niveau_commun']['bas'], 0)} ; "
             f"{_fr(d['le_niveau_commun']['haut'], 0)}]"))):
        yy = y0 + 62 + k * 20
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 376, yy, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 172, "le critère que l'œil a DÉCLARÉ", 0, GRIS)
    for k, ligne in enumerate(_plier(d.get("ce_que_loeil_a_cru_voir") or "—", 78)):
        ecrire(x0 + 14, y0 + 190 + k * 16, ligne, 0, ENCRE)
    ecrire(x0 + 14, y0 + 250,
           "⚠⚠ Le prix est DÉCLARÉ et payé, et il se trouve gratuit ici : les deux lois exactes",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 264,
           "sautent la garantie d'un compte au suivant, donc en prendre la moitié ne déplace",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 278,
           "aucun des deux seuils. Le dire vaut mieux que laisser croire qu'il a mordu.", petit,
           GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  AUCUNE DES DEUX ÉPREUVES DÉCLARÉES NE PASSE : l'assignation rend "
           f"{note['les_justes']} justes sur {loi['choisies']} pour un seuil de {loi['le_seuil']} "
           f"(P = {_fr(note['la_probabilite'], 7)}), et les paires", moyen, ALERTE)
    ecrire(78, y + 46,
           f"     {ap['les_bonnes_designations']} bonnes sur {ap['les_paires_informatives']} "
           f"informatives pour un seuil de {ap['le_seuil']} (P = {_fr(ap['la_probabilite'], 7)}). "
           f"Mieux que le hasard des deux côtés, assez pour rien.", moyen, ALERTE)
    ecrire(78, y + 78,
           "★  ET LE NÉGATIF EST DEUX FOIS MIEUX BORNÉ QUE CELUI DE `195` : un trait de TEXTURE à "
           "la période d'un pli est maintenant calibré, et les quatre contrôles croisés", moyen,
           ENCRE)
    ecrire(78, y + 106,
           f"     montrent que chacun des deux lecteurs est AVEUGLE au trait de l'autre. Il faut "
           f"{_fr(sens['la_force_quil_faut'], 0)} unités du volume dans les deux cas.", moyen,
           ENCRE)
    ecrire(78, y + 138,
           "⚠⚠⚠ CE QU'IL NE FAUT PAS LIRE ICI : que la profondeur ne porte rien. Le seuil exige "
           "onze justes sur quinze, c'est-à-dire une séparation presque parfaite, et la", moyen,
           GRIS)
    ecrire(78, y + 166,
           "     PART exigée baisse avec la taille de la planche. Ce qui manque n'est pas une "
           "idée, c'est un compte de chunks étiquetés.", moyen, GRIS)
    ecrire(78, y + 198,
           "⚠ La lecture a été SCELLÉE dans un commit signé avant qu'aucune clef n'existe dans "
           "l'arbre — ce que `195` ne pouvait pas offrir.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.025, 3), _fr(7.5, 1)) == ("90", "0,025", "7,5"),
      f"{(_fr(90.0, 0), _fr(0.025, 3), _fr(7.5, 1))}")
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

    # ★★★★ CHAQUE NOMBRE QUI PORTE UN VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("la_note", "les_justes"), 13, 0, 2),
            (("la_note", "la_probabilite"), 0.4242424, 7, 2),
            (("la_loi_exacte", "le_seuil"), 12, 0, 2),
            (("la_note_appariee", "les_bonnes_designations"), 6, 0, 2),
            (("la_note_appariee", "la_probabilite"), 0.3131313, 7, 2),
            (("la_note_appariee", "le_seuil"), 5, 0, 2),
            (("la_note_appariee", "les_paires_muettes"), 4, 0, 1),
            (("la_sensibilite_de_texture", "la_force_quil_faut"), 96, 0, 2)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n >= combien, f"{n} mentions pour {combien}")

    # ★★★★ LES DEUX DISTRIBUTIONS DESSINEES VIENNENT DE LA MESURE.
    for cle, champ in (("la_loi_exacte", "justes"), ("la_note_appariee", "bonnes")):
        faux = copy.deepcopy(d)
        for x in faux[cle]["la_distribution"]:
            x["probabilite"] = 1.0 if int(x[champ]) == 0 else 0.0
        _c, _p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la distribution de {cle} vient de la mesure", chemin.read_bytes() != octets)
        dessiner(d, sortie)

    # ★★★★ LES QUATRE CROISES SONT DESSINES AVEC LEUR ATTENDU ET LEUR LU.
    for nom, cle, attendu in LES_QUATRE_CROISES:
        faux = copy.deepcopy(d)
        faux["les_controles_croises"][cle] = 0.6464 if attendu else 1.0
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le croisé « {nom} » suit ce que la mesure dit",
          any("✗" in t for _x, _y, t, _f in p4))

    # ★★★ CHAQUE BARREAU DE L'ECHELLE DE TEXTURE PORTE SA PART.
    for k in (1, 6):
        faux = copy.deepcopy(d)
        faux["la_sensibilite_de_texture"]["la_courbe"][k]["part_des_replicats"] = 0.7272 + k / 1e4
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part",
          any(_fr(0.7272 + k / 1e4, 3) in t for _x, _y, t, _f in p5))

    # ★★★★ LE TITRE SUIT LA MESURE.
    v("★★★★ deux épreuves passées changent le titre",
      "LES DEUX ÉPREUVES" in le_titre({**d, "le_verdict": {
          "loeil_separe": True, "loeil_separe_sur_lassignation": True,
          "loeil_separe_sur_les_paires": True}}))
    v("★★★★ une seule aussi", "UNE DES DEUX" in le_titre({**d, "le_verdict": {
        "loeil_separe": True, "loeil_separe_sur_lassignation": False,
        "loeil_separe_sur_les_paires": True}}))
    v("★★★ et aucune le dit autrement", "PAS ASSEZ" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE NON LEVEE, OU DONT LES CROISES NE SEPARENT PAS, EST REFUSEE.
    for casse, quoi in (
            (lambda x: x.__setitem__("la_cle", None), "non levée"),
            (lambda x: x.__setitem__("la_lecture_deposee", []), "sans lecture"),
            (lambda x: x["la_note_appariee"].__setitem__("decidable", False),
             "à l'épreuve appariée indécidable"),
            (lambda x: x["la_sensibilite_de_texture"].__setitem__("la_force_quil_faut", None),
             "sans force de texture dérivée"),
            (lambda x: x["les_controles_croises"].__setitem__(
                "la_texture_vue_par_le_lecteur_de_luminosite", 1.0),
             "dont les deux lecteurs lisent la même chose"),
            (lambda x: x.__setitem__("ce_que_195_rendait", None),
             "où ce que `195` a rendu n'est pas relu")):
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

    print(f"figure_regarder_dans_la_profondeur.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "regarder_dans_la_profondeur.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "196_regarder_dans_la_profondeur.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
