"""Une bande de bord plus large lit-elle mieux le pas ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, les trois courbes par largeur — l'aléa, le
serpentement, l'erreur qu'ils composent — et, sous elles, la dispersion du pas lui-même : la
quantité que l'estimateur est censé lire. En bas à gauche, la prémisse de `198` mise en regard de ce
que la bande serpente vraiment. Au centre, l'épreuve sur les coutures réservées. À droite, la dérive
refusée et l'étalon.

  uv run python src/figures/figure_une_bande_plus_large_lit_elle_mieux.py \\
      --json docs/mesures/une_bande_plus_large_lit_elle_mieux.json \\
      --sortie docs/images/203_une_bande_plus_large_lit_elle_mieux.png
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
    """Le JSON de `une_bande_plus_large_lit_elle_mieux.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, UNE QUI DÉCLARE PLUS D'UNE ÉPREUVE SANS EN
    DIVISER LA GARANTIE, ET UNE DONT LES BARREAUX NE PORTENT PAS LA DISPERSION DU PAS : sans le
    dernier, une bande qui ne lit RIEN passerait pour la meilleure, et c'est le défaut que la mesure
    a rendu.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_ligne", "la_recherche", "la_courbe_entiere", "lepreuve", "le_verdict",
                "letalon"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_recherche", "la_courbe_entiere", "le_verdict", "letalon"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    for b in d["la_courbe_entiere"]["les_barreaux"]:
        for cle in ("lalea_en_voxels", "le_serpentement_en_voxels", "lerreur_en_voxels",
                    "la_dispersion_du_pas_en_voxels"):
            if b.get(cle) is None:
                raise ValueError(f"{chemin} : le barreau {b.get('la_largeur')} n'a pas {cle}")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if ve.get("la_premisse_de_198_tient"):
        return "Une bande plus large lit-elle mieux ? — la prémisse de `198` tient sur la matière"
    return ("Une bande plus large lit-elle mieux ? — NON, et aucune largeur ne lit "
            "plus de signal que de bruit")


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

    lg, en = d["la_ligne"], d["la_courbe_entiere"]
    re_, ep, ve, e = d["la_recherche"], d["lepreuve"], d["le_verdict"], d["letalon"]
    po = d.get("la_portee") or {}
    bar = en["les_barreaux"]

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"segment {lg['segment']} · rangée {lg['la_rangee']} · {lg['colonnes_lues']} chunks "
           f"lus sur {lg['colonnes_demandees']} · coupes aux rangées {lg['les_rangees_de_coupe']} "
           f"· {d['les_coutures_voisines']} coutures voisines · largeur de `198` "
           f"{d['la_largeur_de_198']} · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : les courbes par largeur
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "ce que chaque largeur lit — et ce qu'elle lit faux", moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 14, pw - 380, 206
    haut = max(max(b["lerreur_en_voxels"] for b in bar), 1.0) * 1.1
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 48, yy - 6, _fr(haut * (1.0 - k / 4.0), 1), 0, GRIS)
    n = max(1, len(bar) - 1)
    for cle, coul in (("lerreur_en_voxels", ALERTE), ("le_serpentement_en_voxels", CONTRE),
                      ("lalea_en_voxels", GRIS), ("la_dispersion_du_pas_en_voxels", BON)):
        prec = None
        for i, b in enumerate(bar):
            px = gx0 + gw * i / n
            py = gy0 + gh * (1.0 - float(b[cle]) / haut)
            if prec is not None:
                art.line([prec[0], prec[1], px, py], fill=coul, width=2)
            art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=coul)
            points.append((px, py))
            prec = (px, py)
    for i, b in enumerate(bar):
        ecrire(gx0 + gw * i / n - 6, gy0 + gh + 8, str(b["la_largeur"]), 0, GRIS)
    ecrire(gx0 + gw / 2 - 60, gy0 + gh + 26, "largeur de bande, en colonnes", 0, GRIS)
    lx = x0 + pw - 306
    for k, (nom, coul) in enumerate(
            (("l'ERREUR composée", ALERTE), ("le SERPENTEMENT de la bande", CONTRE),
             ("l'ALÉA de l'estimateur", GRIS),
             ("la DISPERSION du pas lu", BON))):
        art.rectangle([lx, y0 + 18 + k * 22, lx + 22, y0 + 26 + k * 22], fill=coul)
        ecrire(lx + 30, y0 + 16 + k * 22, nom, 0, coul)
    ecrire(lx, y0 + 116,
           "★★★★ LA COURBE VERTE EST SOUS LA GRISE", petit, ALERTE)
    ecrire(lx, y0 + 130, "PARTOUT : à toute largeur, l'estimateur", petit, ALERTE)
    ecrire(lx, y0 + 144, "se contredit d'une rangée à l'autre plus", petit, ALERTE)
    ecrire(lx, y0 + 158, "que le pas qu'il lit ne varie.", petit, ALERTE)
    ecrire(lx, y0 + 182, "⚠ L'aléa est une BORNE SUPÉRIEURE : deux", petit, GRIS)
    ecrire(lx, y0 + 196, "rangées d'un même chunk ne dérivent pas", petit, GRIS)
    ecrire(lx, y0 + 210, "exactement pareil, donc leur désaccord", petit, GRIS)
    ecrire(lx, y0 + 224, "porte le bruit PLUS cette différence.", petit, GRIS)
    ecrire(lx, y0 + 248, "Dans les deux lectures, un correcteur", petit, GRIS)
    ecrire(lx, y0 + 262, "différentiel n'a pas de quoi corriger.", petit, GRIS)

    # ---- panneau 2 : la prémisse de `198`
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la prémisse de `198`, mise à l'épreuve", moyen, ENCRE)
    s198 = float(ve["le_serpentement_a_la_largeur_de_198_en_voxels"])
    hautP = max(s198, 1.0) * 1.15
    for k, (nom, val, coul) in enumerate(
            ((f"serpentement MESURÉ à {d['la_largeur_de_198']} colonnes", s198, ALERTE),
             ("ce que la règle de `198` autorisait", 1.0, BON))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 320, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 17, 372, float(val) / hautP, 9, coul)
    tient = ve.get("la_premisse_de_198_tient")
    ecrire(x0 + 12, y0 + 100,
           f"{'★' if tient else '✗'} LA PRÉMISSE TIENT : {tient}", moyen,
           BON if tient else ALERTE)
    ecrire(x0 + 12, y0 + 130,
           "La règle prend la plus grande puissance de deux", petit, GRIS)
    ecrire(x0 + 12, y0 + 144,
           "dont le serpentement reste sous UN voxel. À sa", petit, GRIS)
    ecrire(x0 + 12, y0 + 158,
           f"propre largeur, il en vaut {_fr(s198, 4)}.", petit, GRIS)
    ecrire(x0 + 12, y0 + 182,
           "⚠⚠⚠ CE VERDICT NE DÉPEND D'AUCUN CRITÈRE DE", petit, ALERTE)
    ecrire(x0 + 12, y0 + 196,
           "SÉLECTION : il suffit de lire le serpentement à la", petit, ALERTE)
    ecrire(x0 + 12, y0 + 210,
           "largeur que la règle nomme elle-même. C'est le seul", petit, ALERTE)
    ecrire(x0 + 12, y0 + 224,
           "résultat de la tranche qui ne doive rien au choix", petit, ALERTE)
    ecrire(x0 + 12, y0 + 238, "d'une largeur.", petit, ALERTE)

    # ---- panneau 3 : l'épreuve
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve, sur des coutures réservées", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("coutures pour CHERCHER", f"{d['les_coutures_pour_chercher']}"),
            ("coutures pour CONFIRMER", f"{d['les_coutures_pour_confirmer']}"),
            ("largeur nommée par la recherche", f"{re_['la_largeur_nommee']}"),
            ("coutures informatives", f"{ep.get('les_coutures_informatives')}"),
            ("où la nommée gagne", f"{ep.get('les_coutures_ou_la_nommee_gagne')}"),
            ("seuil de la garantie", f"{ep.get('le_seuil_apparie')}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 300, yy, val, 0, ENCRE)
    part = (float(ep.get("les_coutures_ou_la_nommee_gagne") or 0)
            / max(1.0, float(ep.get("les_coutures_informatives") or 1)))
    barre(x0 + 12, y0 + 140, 372, part, 12, ALERTE)
    ecrire(x0 + 12, y0 + 160,
           f"P = {_fr(ep.get('la_valeur_p'), 7)} pour "
           f"{_fr(d['la_garantie_par_epreuve'], 2)} garantis", 0, ENCRE)
    ecrire(x0 + 12, y0 + 184,
           "⚠⚠⚠ LA BANDE LA PLUS ÉTROITE GAGNE, MAIS ELLE", petit, ALERTE)
    ecrire(x0 + 12, y0 + 198,
           "GAGNE EN NE LISANT RIEN : sa dispersion de pas", petit, ALERTE)
    ecrire(x0 + 12, y0 + 212,
           f"vaut {_fr(bar[0]['la_dispersion_du_pas_en_voxels'], 4)} voxel. Le critère de "
           f"l'erreur", petit, ALERTE)
    ecrire(x0 + 12, y0 + 224,
           "composée récompense un instrument mort, et c'est", petit, ALERTE)
    ecrire(x0 + 12, y0 + 238, "le contrôle croisé qui l'a dit.", petit, ALERTE)

    # ---- panneau 4 : la dérive refusée et l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle croisé, et l'étalon", moyen, ENCRE)
    for k, (nom, val, coul) in enumerate((
            ("dérive à la largeur nommée",
             f"{_fr(en.get('la_derive_a_la_largeur_nommee'), 4)} vx", ALERTE),
            ("dérive par le creux (`202`)",
             f"{_fr(en.get('la_derive_de_202_en_voxels'), 4)} vx", CONTRE),
            ("rapport des deux", _fr(en.get("le_rapport_des_deux_derives"), 4), ALERTE))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 288, yy, val, 0, coul)
    ecrire(x0 + 12, y0 + 78,
           "✗ LA PORTÉE EST REFUSÉE :", moyen, ALERTE)
    ecrire(x0 + 12, y0 + 102,
           "la dérive ne dépasse pas l'aléa qui la mesure.", petit, ALERTE)
    ecrire(x0 + 12, y0 + 126, "l'étalon — deux faces, sur réplicats", 0, GRIS)
    for k, (nom, x_) in enumerate((
            ("quand la règle dit LARGE", e["quand_la_regle_dit_large"]),
            ("quand la règle dit ÉTROIT", e["quand_la_regle_dit_etroit"]))):
        yy = y0 + 146 + k * 22
        bonp = (x_["la_part"] >= 1.0) if k == 0 else (x_["la_part"] <= 0.0)
        ecrire(x0 + 12, yy, nom, 0, BON if bonp else ALERTE)
        ecrire(x0 + 236, yy, _fr(x_["la_part"], 3), 0, BON if bonp else ALERTE)
        barre(x0 + 286, yy + 2, 98, x_["la_part"], 8, BON if bonp else CONTRE)
    ecrire(x0 + 12, y0 + 196,
           f"★ sépare : {e['letalon_separe']} · {e['quand_la_regle_dit_large']['les_replicats']} "
           f"réplicats par face", 0, BON)
    ecrire(x0 + 12, y0 + 220,
           "★ Le contrôle croisé était bâti pour être", petit, GRIS)
    ecrire(x0 + 12, y0 + 234,
           "falsifiable. Il l'a été, et il a pris le critère.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  LA PRÉMISSE DE `198` EST RÉFUTÉE PAR LA MATIÈRE : à la largeur de "
           f"{d['la_largeur_de_198']} colonnes qu'elle nomme, la bande serpente de "
           f"{_fr(s198, 4)} voxels là où la règle", moyen, ALERTE)
    ecrire(78, y + 46,
           "     en autorisait moins d'un. Ce verdict ne doit rien au choix d'une largeur : il "
           "suffit de lire le serpentement là où la règle le borne.", moyen, ALERTE)
    ecrire(78, y + 78,
           f"★★★★ ET AUCUNE LARGEUR NE LIT PLUS DE SIGNAL QUE DE BRUIT : aux {len(bar)} largeurs "
           f"essayées, le désaccord des deux rangées dépasse la dispersion", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     du pas lui-même — de {_fr(bar[0]['lalea_en_voxels'], 4)} contre "
           f"{_fr(bar[0]['la_dispersion_du_pas_en_voxels'], 4)} à deux colonnes, jusqu'à "
           f"{_fr(bar[-1]['lalea_en_voxels'], 4)} contre "
           f"{_fr(bar[-1]['la_dispersion_du_pas_en_voxels'], 4)} à {bar[-1]['la_largeur']}.",
           moyen, ENCRE)
    ecrire(78, y + 138,
           f"⚠⚠⚠ ET LE CONTRÔLE CROISÉ A PRIS MON PROPRE CRITÈRE : la largeur que l'erreur "
           f"composée nomme rend une dérive de "
           f"{_fr(en.get('la_derive_a_la_largeur_nommee'), 4)} voxel contre "
           f"{_fr(en.get('la_derive_de_202_en_voxels'), 4)}", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     par le creux — un rapport de "
           f"{_fr(en.get('le_rapport_des_deux_derives'), 4)}. Deux méthodes qui doivent s'accorder "
           f"ne s'accordent pas, donc l'une est cassée : c'est le critère.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ La portée de `199` n'est donc PAS recalculée ici : une dérive qui ne dépasse pas "
           f"l'aléa qui la mesure ne se projette pas, et la projeter rendait dix-neuf mètres sur "
           f"un rouleau large de cent vingt et un millimètres.", petit, GRIS)

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
      (_fr(16.0, 0), _fr(0.05, 2), _fr(10.9752, 4)) == ("16", "0,05", "10,9752"),
      f"{(_fr(16.0, 0), _fr(0.05, 2), _fr(10.9752, 4))}")
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
    for cle in ("lalea_en_voxels", "le_serpentement_en_voxels", "lerreur_en_voxels",
                "la_dispersion_du_pas_en_voxels"):
        for k in (0, len(d["la_courbe_entiere"]["les_barreaux"]) - 1):
            faux = copy.deepcopy(d)
            faux["la_courbe_entiere"]["les_barreaux"][k][cle] = 7.7171
            _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
            v(f"★★★★ le barreau {k} de {cle} vient de la mesure",
              [(round(x, 2), round(y, 2)) for x, y in ptk]
              != [(round(x, 2), round(y, 2)) for x, y in points])
            dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "le_serpentement_a_la_largeur_de_198_en_voxels"), 23.2323, 4, 3),
            (("lepreuve", "la_valeur_p"), 0.0303, 4, 1),
            (("lepreuve", "les_coutures_informatives"), 191, 0, 1),
            (("lepreuve", "les_coutures_ou_la_nommee_gagne"), 173, 0, 1),
            (("lepreuve", "le_seuil_apparie"), 111, 0, 1),
            (("la_recherche", "la_largeur_nommee"), 41, 0, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    for cle, val, combien in (("la_derive_a_la_largeur_nommee", 7.4747, 2),
                              ("la_derive_de_202_en_voxels", 2.7272, 2),
                              ("le_rapport_des_deux_derives", 0.8181, 2)):
        faux = copy.deepcopy(d)
        faux["la_courbe_entiere"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ la_courbe_entiere.{cle} est lu autant de fois qu'il le faut",
          sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t) >= combien)
    dessiner(d, sortie)

    # ★★★ LES DEUX FACES DE L'ETALON PORTENT LEUR PART.
    for face in ("quand_la_regle_dit_large", "quand_la_regle_dit_etroit"):
        faux = copy.deepcopy(d)
        faux["letalon"][face]["la_part"] = 0.6464
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la face {face} porte sa part",
          any(_fr(0.6464, 3) in t for _x, _y, t, _f in p4))
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["la_premisse_de_198_tient"] = True
    v("★★★★ une prémisse qui tient change le titre",
      "la prémisse de `198` tient" in le_titre(faux), le_titre(faux))
    v("★★★ et l'observé dit l'inverse",
      "aucune largeur ne lit" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_courbe_entiere"].__setitem__("decidable", False),
             "à la courbe indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_courbe_entiere"]["les_barreaux"][0].__setitem__(
                "la_dispersion_du_pas_en_voxels", None),
             "dont un barreau n'a pas la dispersion du pas"),
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

    print(f"figure_une_bande_plus_large_lit_elle_mieux.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "une_bande_plus_large_lit_elle_mieux.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "203_une_bande_plus_large_lit_elle_mieux.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
