"""Ouvrir les quinze — ce que l'œil a rendu, et ce que le dispositif sait voir.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la loi EXACTE : la distribution
hypergéométrique entière, le seuil que la garantie de la chaîne impose, et là où la lecture est
tombée. En haut à droite, la lecture elle-même — quinze numéros déposés une fois, et le critère que
l'œil a déclaré. En bas à gauche, la sensibilité du dispositif, mesurée sur réplicats, qui dit ce
qu'un négatif borne et ce qu'il ne borne pas. En bas à droite, la planche : d'où viennent les trente
cubes et ce qui rend l'aveugle aveugle.

  uv run python src/figures/figure_ouvrir_les_quinze.py \\
      --json docs/mesures/ouvrir_les_quinze.json \\
      --sortie docs/images/195_ouvrir_les_quinze.png
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


def _plier(texte: str, largeur: int) -> list[str]:
    """Plier une prose à une largeur de caractères, sans couper un mot."""
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
    """Le JSON d'`ouvrir_les_quinze.py`, levé.

    ⚠⚠⚠ REFUSE UNE MESURE NON LEVÉE, ET REFUSE UNE LECTURE ABSENTE. Une figure qui dessinerait
    « l'œil ne sépare pas » sur une planche que personne n'a regardée annoncerait un résultat là où
    il n'y a qu'un dispositif — la pire des vérifications incapables d'échouer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("la_loi_exacte", "la_sensibilite", "lappariement", "les_cubes", "la_planche"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d.get("la_cle"):
        raise ValueError(f"{chemin} : la mesure n'est pas levée")
    if not d.get("la_lecture_deposee"):
        raise ValueError(f"{chemin} : aucune lecture n'a été déposée")
    if not (d.get("la_note") or {}).get("decidable"):
        raise ValueError(f"{chemin} : la note est indécidable")
    if d["la_loi_exacte"].get("le_seuil") is None:
        raise ValueError(f"{chemin} : la loi n'a pas de seuil dérivé")
    if d["la_sensibilite"].get("la_force_quil_faut") is None:
        raise ValueError(f"{chemin} : le dispositif n'a pas de force dérivée, "
                         "donc son négatif ne borne rien")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    n = d["la_note"]
    if n.get("loeil_separe"):
        return "Ouvrir les quinze — L'ŒIL SÉPARE, et il faut maintenant le confirmer ailleurs"
    if int(n["les_justes"]) > float(n["les_attendus_par_hasard"]):
        return "Ouvrir les quinze — l'œil fait mieux que le hasard, pas assez pour être publié"
    return "Ouvrir les quinze — L'ŒIL NE SÉPARE PAS, et il tombe exactement sur le hasard"


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

    loi, note = d["la_loi_exacte"], d["la_note"]
    sens, app, cub = d["la_sensibilite"], d["lappariement"], d["les_cubes"]
    separe = bool(note.get("loeil_separe"))

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"{loi['tuiles']} cubes ouverts — {loi['retenants']} qui tiennent une feuille, "
           f"{loi['retenants']} contrôles appariés DANS LE MÊME SEGMENT · une ASSIGNATION déclarée, "
           f"pas un trait · nul hypergéométrique EXACT · garantie {_fr(loi['la_garantie'], 2)}",
           petit, GRIS)

    # ---- panneau 1 : la loi exacte
    x0, y0, pw, ph = 56, 122, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la loi exacte — où une lecture doit tomber pour valoir quelque chose",
           moyen, ENCRE)
    dist = loi["la_distribution"]
    hautP = max(x["probabilite"] for x in dist) * 1.12
    bx, by, bh, pas = x0 + 26, y0 + 14, 92, 34
    for x in dist:
        k = int(x["justes"])
        h = bh * float(x["probabilite"]) / hautP
        gx = bx + k * pas
        coul = (CONTRE if k == int(note["les_justes"])
                else ALERTE if k >= int(loi["le_seuil"]) else TRAIT)
        art.rectangle([gx, by + bh - h, gx + pas - 6, by + bh], fill=coul)
        points.append((gx + pas - 6, by + bh))
        ecrire(gx + 4, by + bh + 4, f"{k}", 0, GRIS if k % 2 else ENCRE)
    # ⚠⚠ LE SEUIL EST TRACE, PAS SEULEMENT ECRIT : les masses au-dela sont si petites qu'elles se
    # dessinent au ras de l'axe, donc sans ce trait le lecteur ne voit pas ou tombe la frontiere.
    xs = bx + int(loi["le_seuil"]) * pas - 3
    art.line([xs, by - 4, xs, by + bh + 2], fill=ALERTE, width=2)
    traits.append((bx, by, bx + 16 * pas))
    traits.append((xs, by - 4, by + bh + 2))
    ecrire(x0 + 26, y0 + 130,
           f"attendus par hasard {_fr(loi['attendus_par_hasard'], 1)}   ·   "
           f"seuil DÉRIVÉ de la garantie {loi['le_seuil']}   ·   "
           f"probabilité au seuil {_fr(loi['la_probabilite_au_seuil'], 7)}", 0, ENCRE)
    ecrire(x0 + 26, y0 + 150,
           f"un juste de moins ne la tiendrait pas : "
           f"{_fr(dist[int(loi['le_seuil']) - 1]['probabilite_den_avoir_autant_ou_plus'], 7)}",
           0, GRIS)
    ecrire(x0 + 26, y0 + 176,
           "⚠⚠ L'œil peut chercher ce qu'il veut, aussi longtemps qu'il veut : ce qui est noté",
           petit, GRIS)
    ecrire(x0 + 26, y0 + 190,
           "est son UNIQUE assignation. Une assignation est un objet, pas une famille — c'est",
           petit, GRIS)
    ecrire(x0 + 26, y0 + 204,
           "ce qui rend une maximisation sans liste déclarée payable en arithmétique exacte.",
           petit, GRIS)

    # ---- panneau 2 : la lecture
    x0, y0, pw, ph = 712, 122, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la lecture — quinze numéros, déposés une fois", moyen, ENCRE)
    lus = list(note["les_tuiles_designees"])
    ecrire(x0 + 14, y0 + 12, "les tuiles désignées", 0, GRIS)
    ecrire(x0 + 14, y0 + 30, " · ".join(str(i) for i in lus[:8]), moyen, ENCRE)
    ecrire(x0 + 14, y0 + 50, " · ".join(str(i) for i in lus[8:]), moyen, ENCRE)
    ecrire(x0 + 14, y0 + 78, "le critère que l'œil a DÉCLARÉ", 0, GRIS)
    for k, ligne in enumerate(_plier(d.get("ce_que_loeil_a_cru_voir") or "—", 78)):
        ecrire(x0 + 14, y0 + 96 + k * 16, ligne, 0, ENCRE)
    ecrire(x0 + 14, y0 + 140,
           f"justes {note['les_justes']} sur {loi['choisies']}   ·   "
           f"attendus {_fr(note['les_attendus_par_hasard'], 1)}   ·   "
           f"P = {_fr(note['la_probabilite'], 7)}", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 166,
           f"{'★' if separe else '✗'} L'ŒIL "
           f"{'SÉPARE' if separe else 'NE SÉPARE PAS'} LES DEUX CAMPS.", moyen,
           BON if separe else ALERTE)
    ecrire(x0 + 14, y0 + 186,
           "⚠⚠⚠ Le critère déclaré est, dans le vocabulaire de la chaîne, la COHÉRENCE du",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 200,
           "tenseur de structure — que `191` avait déjà déclarée et réfutée. L'œil libre a",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 214, "choisi un observable déjà payé, et il rend le même verdict.",
           petit, GRIS)

    # ---- panneau 3 : la sensibilité
    x0, y0, pw, ph = 56, 408, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la sensibilité du dispositif — ce qu'un négatif borne, mesuré sur réplicats", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 10,
           "Le fond de l'étalon est LA VRAIE MATIÈRE, et l'étiquette y est retirée à chaque",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 26,
           "réplicat : le trait réel du fond ne peut donc que nuire au lecteur, jamais l'aider.",
           petit, ENCRE)
    for k, pt in enumerate(sens["la_courbe"]):
        yy = y0 + 50 + k * 22
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 14, yy,
               f"+{int(pt['force']):>3} unité{'s' if int(pt['force']) > 1 else ''} du volume", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 168, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 216, yy + 2, 380, part, 8, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 14, y0 + 236,
           f"la force DÉRIVÉE — la plus petite vue à TOUS les {sens['replicats']} réplicats : "
           f"{_fr(sens['la_force_quil_faut'], 0)} unités du volume", 0, ENCRE)
    ecrire(x0 + 14, y0 + 258,
           "⚠⚠⚠ CE QUE CE NOMBRE BORNE, ET CE QU'IL NE BORNE PAS : le lecteur de l'étalon lit la",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 272,
           "LUMINOSITÉ MOYENNE et sait ce qu'on lui injecte. Un trait de luminosité plus faible,",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 286,
           "personne ne le voit. Pour un trait de TEXTURE, ce dispositif n'a pas de sensibilité "
           "mesurée.", petit, ALERTE)

    # ---- panneau 4 : la planche
    x0, y0, pw, ph = 712, 408, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la planche — d'où viennent les trente cubes", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("cubes demandés / rendus", f"{cub['demandes']} / {cub['rendus']}"),
            ("paires gardées", f"{cub['paires_gardees']}"),
            ("segments de l'étiquette / appariés",
             f"{app['segments']} / {app['segments_apparies']}"),
            ("retenants sans paire disponible", f"{app['sans_paire']}"),
            ("non-retenants disponibles", f"{app['non_retenants_en_tout']}"),
            ("couches du cube · côté de la tuile",
             f"{cub['couches_du_cube'][0]} · {d['la_planche']['cote']}"),
            ("la couche montrée", f"{d.get('la_couche_montree')}"),
            ("niveau de gris COMMUN aux trente",
             f"[{_fr(d['le_niveau_commun']['bas'], 0)} ; "
             f"{_fr(d['le_niveau_commun']['haut'], 0)}]"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 376, yy, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 184,
           "⚠⚠ L'APPARIEMENT EST DANS LE SEGMENT, et c'est `193` qui l'impose : deux chunks",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 198,
           "d'un même segment ne sont pas échangeables, donc un contrôle tiré ailleurs aurait",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 212,
           "fait voir à l'œil une différence de segment — un vrai trait, répondant à une autre",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 226, "question que celle posée.", petit, ENCRE)
    ecrire(x0 + 14, y0 + 250,
           "⚠⚠⚠ L'aveugle est de PROCÉDURE, pas de serrure : le chemin qui pose la planche",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 264,
           "n'appelle jamais la fonction qui calcule la clef, et la planche se redessine à",
           petit, GRIS)
    ecrire(x0 + 14, y0 + 278,
           "l'octet près que la mesure porte sa clef ou non. Le reste est de la discipline.",
           petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  L'ŒIL NE SÉPARE PAS : {note['les_justes']} justes sur {loi['choisies']} contre "
           f"{_fr(note['les_attendus_par_hasard'], 1)} attendus par hasard, soit une probabilité "
           f"de {_fr(note['la_probabilite'], 7)} — là où le seuil dérivé exigeait "
           f"{loi['le_seuil']}.", moyen, ALERTE)
    ecrire(78, y + 46,
           "     La chaîne a donc ouvert les quinze, et la matière ne les distingue pas à l'œil "
           "sur la couche du milieu de leur cube.", moyen, ALERTE)
    ecrire(78, y + 78,
           "★  ET C'EST LE TRENTE-DEUXIÈME OBSERVABLE, PAYÉ D'AVANCE : l'œil a eu droit à toutes "
           "les listes, y compris celles que personne ne sait écrire, et sa liberté", moyen, ENCRE)
    ecrire(78, y + 106,
           "     entière tient dans une seule assignation dont le nul est exact. C'est la forme "
           "qui manquait pour que REGARDER puisse produire autre chose qu'une anecdote.", moyen,
           ENCRE)
    ecrire(78, y + 138,
           f"⚠⚠⚠ CE QUE CE NÉGATIF NE DIT PAS : un trait de luminosité vaut moins de "
           f"{_fr(sens['la_force_quil_faut'], 0)} unités du volume — au-dessous, le dispositif ne "
           f"le voit à aucun réplicat.", moyen, GRIS)
    ecrire(78, y + 166,
           "     Et pour un trait de TEXTURE, aucune sensibilité n'a été mesurée : le silence de "
           "l'œil y est un silence, pas une absence.", moyen, GRIS)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche livre est l'instrument : une planche appariée, aveugle, dont "
           "toute lecture future se note contre la même loi exacte.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.05, 2), _fr(7.5, 1)) == ("90", "0,05", "7,5"),
      f"{(_fr(90.0, 0), _fr(0.05, 2), _fr(7.5, 1))}")
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
            (("la_note", "les_justes"), 13, 0, 2),
            (("la_note", "la_probabilite"), 0.4242424, 7, 2),
            (("la_note", "les_attendus_par_hasard"), 9.4, 1, 2),
            (("la_loi_exacte", "le_seuil"), 12, 0, 2),
            (("la_loi_exacte", "la_probabilite_au_seuil"), 0.0313131, 7, 1),
            (("la_sensibilite", "la_force_quil_faut"), 96, 0, 2)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[1]} est lu autant de fois qu'il le faut", n >= combien,
          f"{n} mentions pour {combien} attendues")

    # ★★★★ LA DISTRIBUTION DESSINEE EST CELLE DU PRODUCTEUR, PAS UNE LOI RECALCULEE.
    faux = copy.deepcopy(d)
    for x in faux["la_loi_exacte"]["la_distribution"]:
        x["probabilite"] = 1.0 if int(x["justes"]) == 0 else 0.0
    _c, _p3, _cd, _pt, b3, _t = dessiner(faux, sortie)
    v("★★★★ la distribution dessinée vient de la mesure", chemin.read_bytes() != octets,
      "une masse déplacée déplace l'image")
    dessiner(d, sortie)

    # ★★★ CHAQUE BARREAU DE L'ECHELLE DE SENSIBILITE EST DESSINE AVEC SA PART.
    for k in (1, 5):
        faux = copy.deepcopy(d)
        faux["la_sensibilite"]["la_courbe"][k]["part_des_replicats"] = 0.6161 + k / 1e4
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part",
          any(_fr(0.6161 + k / 1e4, 3) in t for _x, _y, t, _f in p4))

    # ★★★★ LA LECTURE DEPOSEE EST DESSINEE EN ENTIER, ET SON CRITERE AVEC.
    faux = copy.deepcopy(d)
    faux["la_note"]["les_tuiles_designees"] = list(range(41, 56))
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    dessinees = {int(x) for _a, _b, t, _f in p5 for x in t.replace(" · ", " ").split()
                 if x.isdigit()}
    v("★★★★ les quinze numéros déposés sont tous dessinés",
      set(range(41, 56)) <= dessinees, f"{sorted(set(range(41, 56)) - dessinees)}")
    faux = copy.deepcopy(d)
    faux["ce_que_loeil_a_cru_voir"] = "un motif que personne ne saurait nommer autrement"
    _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le critère DÉCLARÉ par l'œil est dessiné",
      any("que personne ne saurait nommer" in t for _x, _y, t, _f in p6))

    # ★★★★ LE TITRE ET LE VERDICT SUIVENT LA MESURE, ILS NE LA PRECEDENT PAS.
    faux = copy.deepcopy(d)
    faux["la_note"]["loeil_separe"] = True
    faux["la_note"]["les_justes"] = 13
    v("★★★★ un œil qui sépare change le titre", "SÉPARE," in le_titre(faux),
      le_titre(faux))
    v("★★★★ et un œil au niveau du hasard le change aussi",
      "NE SÉPARE PAS" in le_titre(d), le_titre(d))
    _c, p7, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★ le verdict du panneau suit la note",
      any("L'ŒIL SÉPARE LES DEUX CAMPS" in t for _x, _y, t, _f in p7))
    dessiner(d, sortie)

    # ⚠⚠ UNE MESURE NON LEVEE, SANS LECTURE, OU SANS SENSIBILITE EST REFUSEE.
    for casse, quoi in ((lambda x: x.__setitem__("la_cle", None), "non levée"),
                        (lambda x: x.__setitem__("la_lecture_deposee", []), "sans lecture"),
                        (lambda x: x["la_note"].__setitem__("decidable", False),
                         "à la note indécidable"),
                        (lambda x: x["la_sensibilite"].__setitem__("la_force_quil_faut", None),
                         "sans force dérivée")):
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

    print(f"figure_ouvrir_les_quinze.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "ouvrir_les_quinze.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "195_ouvrir_les_quinze.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt, _b, _t = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
