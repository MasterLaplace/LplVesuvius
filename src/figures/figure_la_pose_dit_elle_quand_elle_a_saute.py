"""La pose dit-elle quand elle a sauté ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle, et il a DEUX moitiés :
sur la spirale nue aucun pas ne saute ET aucune des trois règles ne refuse une seule pose. En haut à
droite, le fait : bras par bras, ce que chaque énoncé VOIT. En bas à gauche, matière par matière,
avec l'inertie nommée là où un énoncé ne tente rien. En bas à droite, le PRIX, parce qu'un rappel
sans sa précision est satisfait par une règle qui refuse tout.

  uv run python src/figures/figure_la_pose_dit_elle_quand_elle_a_saute.py \\
      --json docs/mesures/la_pose_dit_elle_quand_elle_a_saute.json \\
      --sortie docs/images/162_la_pose_dit_elle_quand_elle_a_saute.png
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
TEMOIN = (150, 152, 156)
CONTRE = (92, 108, 150)
ENONCES = ("absolu", "relatif", "etalement")
COULEURS = {"absolu": CONTRE, "relatif": TEMOIN, "etalement": ALERTE}


def lire(chemin: Path) -> dict:
    """Le JSON de `la_pose_dit_elle_quand_elle_a_saute.py`.

    ⚠⚠ Refuse une mesure sans le contrôle de la spirale nue, et sans le verdict PAR BRAS. Une
    figure qui retomberait sur un verdict global dessinerait l'effacement que `161` a payé.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_vide") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if "le_dominant_par_bras" not in j:
        raise ValueError(f"{chemin} : le verdict par bras est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def _barres(art, ecrire, points, g, inertes, cle, x_barre, base, barre_max, pas_ligne):
    """Une ligne de trois barres, une par énoncé, sur le taux `cle`."""
    for k, regle in enumerate(ENONCES):
        t = g.get(regle)
        yy = base + k * pas_ligne
        if t is None or t["sauts"] == 0:
            ecrire(x_barre, yy - 1, "aucun saut à voir", 0, GRIS)
            continue
        if regle in inertes:
            # ⚠⚠ UN ENONCE INERTE N'A PAS RATE, IL N'A RIEN TENTE, et une barre a zero ferait
            # lire un echec la ou il n'y a pas eu de tentative.
            ecrire(x_barre, yy - 1, "inerte : aucune pose refusée", 0, BON)
            continue
        val = t.get(cle)
        if val is None:
            ecrire(x_barre, yy - 1, "pas de taux définissable", 0, GRIS)
            continue
        w = float(val) * barre_max
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 11], fill=COULEURS[regle])
        points.append((x_barre + w, yy + 5))
        ecrire(x_barre + barre_max + 8, yy - 1, f"{val:g}", 0, COULEURS[regle])


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j = d["juger"]
    bras, mat = j["par_bras"], j["par_matiere"]
    c = j["le_controle_de_la_spirale_nue"]
    in_bras = j.get("les_inertes_par_bras", {})
    in_mat = j.get("les_inertes_par_matiere", {})

    ecrire(28, 20, "La pose dit-elle quand elle a sauté ? La porte `R4-P29`, mise à l'épreuve",
           gros, ENCRE)
    ecrire(28, 46, "trois énoncés EXACTS, aucun seuil : deux regardent OÙ LE CENTRE EST ALLÉ, le "
                   "troisième SI LA MÂCHOIRE EST D'ACCORD AVEC ELLE-MÊME", petit, GRIS)

    # ---- panneau 1 : le controle, et il a DEUX moities
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle, et il a DEUX moitiés", moyen, ENCRE)
    marque = "★" if c["il_est_vide"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{marque}  {c['nom']}", moyen, BON if c["il_est_vide"] else ALERTE)
    ecrire(x0 + 14, y0 + 54, f"{c['sauts']} saut sur {c['pas_examines']} pas examinés", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 82, "et aucune règle n'y refuse une seule pose :", petit, ENCRE)
    for k, regle in enumerate(ENONCES):
        n = c["poses_refusees"].get(regle)
        ecrire(x0 + 30, y0 + 102 + k * 18,
               f"{regle} : {'—' if n is None else n} pose refusée",
               petit, BON if n == 0 else ALERTE)
    ecrire(x0 + 14, y0 + ph - 78,
           "la première moitié est `R4-F145`. La seconde est NEUVE : une règle", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 62,
           "qui refuserait là où rien ne saute mesurerait son propre bruit, et", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 46, "tout le reste du tableau ne voudrait plus rien dire.",
           petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 22,
           f"sur la grille entière : {j['tout']['pas_examines']} pas examinés", petit, ENCRE)

    # ---- panneau 2 : ce que chaque enonce VOIT, bras par bras
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que chaque énoncé VOIT — rappel, bras par bras", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 108
    barre_max = pw - 200
    for k, g in enumerate(bras):
        base = y0 + 26 + k * 86
        ecrire(x_nom, base - 18, f"{_court(g['nom'])} — {g['pas_examines']} pas", petit, ENCRE)
        for i, regle in enumerate(ENONCES):
            ecrire(x_nom, base + i * 20 - 1, regle, 0, GRIS)
        _barres(art, ecrire, points, g, set(in_bras.get(g["nom"], ())), "rappel",
                x_barre, base, barre_max, 20)
    ecrire(x0 + 12, y0 + ph - 38,
           "l'étalement voit partout davantage, et de très loin", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 20,
           "mais un rappel seul est satisfait par une règle qui refuse tout", petit, ALERTE)

    # ---- panneau 3 : matiere par matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "matière par matière — rappel, et l'inertie nommée", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 120
    barre_max = pw - 212
    # ⚠⚠ L'INTERLIGNE SE DERIVE DU NOMBRE DE MATIERES ET DE LA PLACE RESTANTE : pose a la main,
    # le cinquieme bloc marchait sur la legende, et c'est la garde qui l'a dit.
    pas_bloc = max((ph - 76) // max(len(mat), 1), 36)
    pas_ligne = pas_bloc // 3
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc
        ecrire(x_nom, base + pas_ligne, _court(g["nom"]), petit, ENCRE)
        _barres(art, ecrire, points, g, set(in_mat.get(g["nom"], ())), "rappel",
                x_barre, base, barre_max, pas_ligne)
    ecrire(x0 + 12, y0 + ph - 38,
           "bleu : l'absolu · gris : le relatif · ambre : l'étalement", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "sur la spirale ÉCRASÉE les deux énoncés de déplacement ne tentent RIEN", petit, ALERTE)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le PRIX — précision, matière par matière", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 120
    barre_max = pw - 212
    pas_bloc = max((ph - 76) // max(len(mat), 1), 36)
    pas_ligne = pas_bloc // 3
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc
        ecrire(x_nom, base + pas_ligne, _court(g["nom"]), petit, ENCRE)
        _barres(art, ecrire, points, g, set(in_mat.get(g["nom"], ())), "precision",
                x_barre, base, barre_max, pas_ligne)
    ecrire(x0 + 12, y0 + ph - 38,
           "une précision de 0,4 veut dire que trois refus sur cinq sont à tort", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 20,
           "c'est ce que l'étalement coûte, et pourquoi il ne DOMINE pas", petit, ALERTE)

    # ---- bande de conclusion
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = bras[0]
    et = pince.get("etalement", {})
    ab = pince.get("absolu", {})
    ecrire(74, y + 12,
           f"★★★★  La pose le dit. Sur la pince, l'étalement des appuis voit "
           f"{et.get('rappel')} des changements de feuille, contre {ab.get('rappel')} "
           f"pour le déplacement du centre.", moyen, ENCRE)
    ecrire(74, y + 38,
           "★★★  Ce n'est pas le déplacement qui porte l'information, c'est la CONTRADICTION "
           "INTERNE de la pose : ses appuis ne tiennent pas le même interstice.", moyen, BON)
    ecrire(74, y + 64,
           f"✗  Mais aucun énoncé ne DOMINE : l'étalement paie sa vue d'une précision de "
           f"{et.get('precision')}, donc trois refus sur cinq seraient à tort.", moyen, ALERTE)
    ecrire(74, y + 90,
           "⚠  Sur la spirale ÉCRASÉE, les deux énoncés de déplacement sont INERTES — pas une "
           "pose refusée sur 47888 — pendant que la pose, elle, se contredit.", moyen, ENCRE)
    ecrire(74, y + 110,
           "⚠⚠  Donc la porte `R4-P29` a un objet, et son prix est mesuré : reste à savoir si "
           "refuser à ce taux achète des marches ou les tue.", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["le_controle_de_la_spirale_nue"]["poses_refusees"]["etalement"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"]:
        if g.get("etalement"):
            g["etalement"]["rappel"] = 0.7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐ ... et le rappel de l'étalement est LU, pas supposé",
      any("0.7777" in t for _x, _y, t, _f in p3))
    # ⚠⚠⚠ LA FIGURE N'ARRONDIT PAS CE QUE LE PRODUCTEUR A DEJA ARRONDI : elle ecrivait `:.3f`
    # dans le tableau et la valeur brute dans la bande, donc DEUX nombres pour UNE mesure, dont un
    # seul est retrouvable par `verifier_chiffres`. Trouve a l'oeil.
    # ⚠ Le controle porte sur ce que la figure DESSINE : le rappel par bras (panneau 2), et le
    # rappel puis la precision par matiere (panneaux 3 et 4). Exiger davantage accuserait la
    # figure de ne pas montrer ce qu'elle n'a jamais promis.
    tous = [t for _x, _y, t, _f in poses]
    j_ = d["juger"]
    attendus = []
    for g in j_["par_bras"]:
        inertes = set(j_.get("les_inertes_par_bras", {}).get(g["nom"], ()))
        attendus += [str(g[r]["rappel"]) for r in ENONCES
                     if g.get(r) and r not in inertes and g[r].get("rappel") is not None]
    for g in j_["par_matiere"]:
        inertes = set(j_.get("les_inertes_par_matiere", {}).get(g["nom"], ()))
        for r in ENONCES:
            if not g.get(r) or r in inertes:
                continue
            attendus += [str(g[r][c]) for c in ("rappel", "precision")
                         if g[r].get(c) is not None]
    v("⭐⭐⭐⭐ la figure écrit les décimales DU PRODUCTEUR, elle ne les ré-arrondit pas",
      all(any(v_ in t for t in tous) for v_ in attendus),
      f"{[v_ for v_ in attendus if not any(v_ in t for t in tous)]}")
    # ⚠⚠⚠ UN ENONCE INERTE EST DIT, JAMAIS DESSINE A ZERO : une barre a zero ferait lire un echec
    # la ou il n'y a pas eu de tentative.
    faux3 = copy.deepcopy(d)
    faux3["juger"]["les_inertes_par_matiere"] = {
        k: list(ENONCES) for k in faux3["juger"]["les_inertes_par_matiere"]}
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ un énoncé INERTE est écrit, jamais dessiné comme une barre à zéro",
      sum("inerte" in t for _x, _y, t, _f in p4)
      > sum("inerte" in t for _x, _y, t, _f in poses),
      f"{sum('inerte' in t for _x, _y, t, _f in p4)} mentions contre "
      f"{sum('inerte' in t for _x, _y, t, _f in poses)}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_162.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans verdict PAR BRAS est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_dominant_par_bras")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "la_pose_dit_elle_quand_elle_a_saute.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "162_la_pose_dit_elle_quand_elle_a_saute.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
