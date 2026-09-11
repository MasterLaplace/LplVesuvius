#!/usr/bin/env python3
"""L'effet mesuré tient-il dans le bruit du tirage ? — la même flèche, sur deux colonnes.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de
[`07`](../../docs/archive/07_reparee_nest_pas_propre.md) §8bis est une comparaison entre une
**dispersion** et un **effet**, et une comparaison de cette forme se raconte mal en prose :
« étendue de graine 82 %, effet médian 35 % » se lit comme deux nombres alors que c'est
**l'effet qui tient à l'intérieur du bruit**. Un nuage et une flèche le montrent sans qu'aucun
chiffre soit nécessaire.

⭐⭐ LES DEUX PANNEAUX PARTAGENT LE MÊME AXE, ET C'EST LE POINT. Donner au panneau de droite
une échelle ajustée à ses propres données ferait paraître `shortfall` aussi dispersé que
`fraction_below_third` — c'est la façon la plus courante de faire mentir un graphique sans
écrire un seul chiffre faux. Sur un axe commun, le nuage de droite s'effondre en un trait, et
c'est exactement ce que la mesure dit.

⚠⚠⚠ CE QUE LA FLÈCHE COMPARE, dit ici plutôt que supposé. Le nuage gris est ce que rend le
maillage **avant réparation** quand on ne change QUE la graine du tirage — donc une dispersion
dont on sait qu'aucune géométrie n'est la cause. La pointe rouge est la valeur **après**
réparation, mesurée sur un autre maillage. Elle n'appartient pas au nuage et n'a pas à y
appartenir : la question est de savoir si elle en SORT. Une pointe dedans veut dire que le
même déplacement s'obtient en changeant une graine, donc que la réparation n'est pas ce qui
l'explique.

⚠ Les nombres sont LUS dans les deux mesures, jamais retapés.

Usage :
    uv run python src/figures/figure_bruit_de_lechantillon.py --verifier
    uv run python src/figures/figure_bruit_de_lechantillon.py \\
        --bruit docs/mesures/le_bruit_de_lechantillon.json \\
        --paire docs/mesures/reparation_et_proximite_scroll1.json \\
        --sortie docs/images/07_bruit_de_lechantillon.png
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (etiquette_de_trace as etiquette,  # noqa: E402
                            etiquettes_de_traces as etiquettes,
                            police, prose_tracable,
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)

BAS, HAUT = 0.12, 8.0
"""Les bornes de l'axe, en RAPPORT à la médiane des graines de chaque trace.

⚠⚠ Un axe en rapport et non en valeur : les traces diffèrent d'un facteur seize sur la
valeur brute, donc un axe absolu écraserait neuf nuages sur dix contre le bord. Normaliser
chaque trace par sa propre médiane de graines est la seule façon de mettre côte à côte des
dispersions prises à des niveaux différents — et c'est aussi ce qui rend les deux colonnes
comparables entre elles, puisqu'elles n'ont pas les mêmes unités.

⚠ Les bornes sont FIXES et non ajustées aux données : un axe qui s'ajuste des deux côtés fait
paraître énorme n'importe quelle dispersion, y compris une dispersion nulle. Toute valeur qui
sortirait est dessinée EN BUTÉE avec un marqueur distinct — laisser une donnée dehors est pire
que la montrer.
"""


def lire(bruit_path: Path, paire_path: Path) -> tuple[dict, dict]:
    """Charge les deux mesures et valide leur contenu minimal.

    Refuse si un fichier manque ou ne porte pas la structure minimale attendue.
    """
    for nom, p in (("bruit", bruit_path), ("paire", paire_path)):
        if not p.is_file():
            raise FileNotFoundError(f"mesure {nom} absente : {p}")
    bruit = json.loads(bruit_path.read_text(encoding="utf-8"))
    paire = json.loads(paire_path.read_text(encoding="utf-8"))
    if not bruit.get("lignes"):
        raise ValueError(f"{bruit_path} ne porte aucune ligne")
    if not paire.get("paires"):
        raise ValueError(f"{paire_path} ne porte aucune paire")
    return bruit, paire


def echelle(rapport: float, pixels: int) -> tuple[int, bool]:
    """
    @brief Un rapport à la médiane, en pixels depuis l'origine de l'axe logarithmique.

    Rend aussi si la valeur a été ramenée en butée. ⚠ Le rapport peut valoir **zéro** — une
    trace où aucune cellule ne passe sous le tiers pour une graine donnée, ce qui est arrivé —
    et le logarithme n'en veut pas. Zéro est une donnée, pas une panne : il se dessine au bord.
    """
    if rapport <= BAS:
        return 0, True
    if rapport >= HAUT:
        return pixels, True
    lo, hi = math.log(BAS), math.log(HAUT)
    return int(round((math.log(rapport) - lo) / (hi - lo) * pixels)), False


def rangs(bruit: dict, paire: dict) -> list[dict]:
    """
    @brief Une ligne par trace : le nuage des graines, et la paire publiée, pour deux colonnes.

    ⚠⚠ Les deux mesures sont appariées par le NOM de trace, jamais par leur ordre. Les deux
    fichiers sont produits par deux outils différents, et rien ne garantit qu'ils rangent leurs
    lignes pareil — un appariement positionnel produirait une figure parfaitement lisible dans
    laquelle chaque flèche serait posée sur le nuage d'une autre trace.
    """
    par_nom = {p["trace"]: p for p in paire.get("paires", [])}
    sortie = []
    for ligne in bruit.get("lignes", []):
        p = par_nom.get(ligne["trace"])
        if p is None:
            continue
        colonnes = {}
        for cle, champ, av, ap in (("fbt", "fbt", "fbt_avant", "fbt_apres"),
                                   ("shortfall", "shortfall", "shortfall_avant", "shortfall_apres")):
            serie = [x[champ] for x in ligne["serie"] if x.get(champ) is not None]
            if not serie or p.get(ap) is None:
                continue
            med = statistics.median(serie)
            if not med:
                continue
            colonnes[cle] = dict(
                graines=[x / med for x in serie],
                avant=(p[av] / med) if p.get(av) is not None else None,
                apres=p[ap] / med,
                etendue_pct=100.0 * (max(serie) - min(serie)) / med,
            )
        if colonnes:
            sortie.append(dict(trace=ligne["trace"], colonnes=colonnes,
                               cellules=(ligne["cellules_min"], ligne["cellules_max"])))
    return sortie


def dedans(colonne: dict) -> bool:
    """
    @brief La valeur « après » tombe-t-elle DANS l'étendue que la graine seule produit ?

    ⚠ C'est la lecture entière de la figure, écrite comme une fonction pour qu'elle soit
    testable et non laissée à l'œil du lecteur.
    """
    return min(colonne["graines"]) <= colonne["apres"] <= max(colonne["graines"])


def prose(rangees: list[dict]) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    n_fbt = sum(1 for r in rangees if "fbt" in r["colonnes"] and dedans(r["colonnes"]["fbt"]))
    n_sh = sum(1 for r in rangees
               if "shortfall" in r["colonnes"] and dedans(r["colonnes"]["shortfall"]))
    total = len(rangees)
    med_fbt = statistics.median(r["colonnes"]["fbt"]["etendue_pct"]
                                for r in rangees if "fbt" in r["colonnes"])
    med_sh = statistics.median(r["colonnes"]["shortfall"]["etendue_pct"]
                               for r in rangees if "shortfall" in r["colonnes"])
    return [
        f"a maillage identique, changer la seule graine du tirage deplace",
        f"fraction_below_third de {med_fbt:.0f} % en median, shortfall de {med_sh:.1f} %.",
        f"la valeur apres reparation tombe DANS ce bruit {n_fbt} fois sur {total} a gauche,",
        f"et {n_sh} fois sur {total} a droite.",
    ]


def dessiner(bruit: dict, paire: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import ImageDraw

    gros, moyen, petit = police(16, 13, 12)
    rangees = rangs(bruit, paire)
    if not rangees:
        raise ValueError("aucune trace appariable entre bruit et paire")

    L, H = 1240, 180 + 34 * max(len(rangees), 1) + 150
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(60, 30, "l'effet de la reparation tient-il dans le bruit du tirage ?",
           gros, TEXTE)
    ecrire(60, 54, f"{bruit['n_graines']} graines sur le maillage AVANT, "
                   "inchange -- puis la valeur APRES reparation", moyen, DISCRET)

    panneaux = (("fraction_below_third", "fbt", 300), ("shortfall", "shortfall", 770))
    largeur = 400
    haut_axe = 118

    for titre, cle, px in panneaux:
        ecrire(px, 92, titre, moyen, TEXTE)
        d.rectangle([px, haut_axe, px + largeur, haut_axe + 34 * len(rangees) + 10],
                    outline=(60, 60, 60))
        # ⚠ Les graduations sont des RAPPORTS ronds : x1 est la mediane des graines, donc la
        # seule graduation qui a un sens hors de ce jeu, et elle est marquee plus clair.
        for r in (0.25, 0.5, 1.0, 2.0, 4.0):
            xx, _ = echelle(r, largeur)
            couleur = (78, 78, 78) if r == 1.0 else (36, 36, 36)
            d.line([px + xx, haut_axe, px + xx, haut_axe + 34 * len(rangees) + 10], fill=couleur)
            lib = "x1" if r == 1.0 else (f"x{r:g}" if r >= 1 else f"/{1 / r:g}")
            ecrire(px + xx - 8, haut_axe + 34 * len(rangees) + 16, lib, petit, DISCRET)

    noms = etiquettes([r["trace"] for r in rangees])
    for i, rangee in enumerate(rangees):
        yy = haut_axe + 22 + 34 * i
        ecrire(60, yy - 7, noms[i], petit, TEXTE)
        ecrire(176, yy - 7, f"{rangee['cellules'][0]}-{rangee['cellules'][1]} cell.",
               petit, DISCRET)
        for titre, cle, px in panneaux:
            col = rangee["colonnes"].get(cle)
            if col is None:
                continue
            # ⚠ Le nuage est dessine AVANT la fleche : recouvert par elle, il donnerait
            # l'impression d'une barre d'erreur ajoutee apres coup sur des donnees choisies.
            lo, _ = echelle(min(col["graines"]), largeur)
            hi, _ = echelle(max(col["graines"]), largeur)
            d.rectangle([px + lo, yy - 8, px + hi, yy + 8], fill=(34, 36, 40))
            for g in col["graines"]:
                gx, butee = echelle(g, largeur)
                c = ROUGE if butee else GRIS
                d.ellipse([px + gx - 2, yy - 2, px + gx + 2, yy + 2], fill=c)
            ax, _ = echelle(col["apres"], largeur)
            couleur = GRIS if dedans(col) else AMBRE
            d.line([px + hi, yy, px + ax, yy], fill=couleur, width=1)
            d.polygon([(px + ax, yy), (px + ax - 5, yy - 4), (px + ax - 5, yy + 4)]
                      if ax > hi else
                      [(px + ax, yy), (px + ax + 5, yy - 4), (px + ax + 5, yy + 4)],
                      fill=couleur)

    bas = haut_axe + 34 * len(rangees) + 44
    # ⚠ La legende tient sur DEUX lignes : la premiere version posait trois entrees sur une
    # seule et les deux premieres se recouvraient -- une legende illisible est pire qu'absente.
    d.ellipse([60, bas + 4, 66, bas + 10], fill=GRIS)
    ecrire(76, bas, "une graine, un point -- meme fichier, meme geometrie",
           petit, DISCRET)
    d.polygon([(60, bas + 26), (55, bas + 22), (55, bas + 30)], fill=AMBRE)
    ecrire(76, bas + 19, "valeur apres reparation, HORS du nuage", petit, AMBRE)
    d.polygon([(420, bas + 26), (415, bas + 22), (415, bas + 30)], fill=GRIS)
    ecrire(436, bas + 19, "... ou dedans, donc indistinguable d'un changement de graine",
           petit, DISCRET)
    # ⚠⚠ Le panneau de droite s'effondre en un trait, ce point est le POINT -- mais un trait ne
    # se lit pas comme un nombre. L'etendue mediane est ecrite dessous pour qu'un lecteur ne
    # conclue pas a une dispersion nulle, qui serait faux.
    med_sh = statistics.median(r["colonnes"]["shortfall"]["etendue_pct"]
                               for r in rangees if "shortfall" in r["colonnes"])
    ecrire(770, haut_axe + 34 * len(rangees) + 34,
           f"le nuage n'est pas vide : etendue mediane {med_sh:.1f} %",
           petit, DISCRET)

    for k, ligne in enumerate(prose(rangees)):
        ecrire(60, bas + 50 + k * 19, ligne, moyen, TEXTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    cadres = [
        (300, haut_axe, 300 + largeur, haut_axe + 34 * len(rangees) + 10),
        (770, haut_axe, 770 + largeur, haut_axe + 34 * len(rangees) + 10),
    ]
    return sortie, poses, cadres


def verifier() -> int:
    """Auto-test HORS LIGNE : l'axe, l'appariement, la lecture, la figure et les sondes."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("la mediane est au milieu de l'axe logarithmique",
      abs(echelle(1.0, 400)[0] - 400 * math.log(1 / BAS) / math.log(HAUT / BAS)) <= 1)
    v("le bas de l'axe est a zero pixel", echelle(BAS, 400) == (0, True))
    v("le haut de l'axe est en butee", echelle(HAUT, 400) == (400, True))
    # ⚠⚠ LE CAS QUI A MOTIVE LA BUTEE : une graine peut rendre ZERO cellule sous le tiers,
    # donc un rapport nul, dont le logarithme n'existe pas. Le laisser lever ferait disparaitre
    # la trace la plus interessante de la figure.
    v("un rapport nul ne leve pas et se dessine en butee", echelle(0.0, 400) == (0, True))
    v("un rapport double est a droite du simple", echelle(2.0, 400)[0] > echelle(1.0, 400)[0])
    v("... et symetriquement a gauche pour la moitie",
      echelle(1.0, 400)[0] - echelle(0.5, 400)[0] == echelle(2.0, 400)[0] - echelle(1.0, 400)[0])

    # ⚠⚠ L'APPARIEMENT PAR NOM, teste avec des fichiers RANGES DIFFEREMMENT : c'est le seul
    # cas ou un appariement positionnel produit une figure lisible et fausse.
    faux_bruit = {"n_graines": 3, "lignes": [
        {"trace": "A", "cellules_min": 1, "cellules_max": 5,
         "serie": [{"fbt": 0.001, "shortfall": 0.07}, {"fbt": 0.003, "shortfall": 0.071},
                   {"fbt": 0.002, "shortfall": 0.072}]},
        {"trace": "B", "cellules_min": 30, "cellules_max": 40,
         "serie": [{"fbt": 0.010, "shortfall": 0.05}, {"fbt": 0.011, "shortfall": 0.051},
                   {"fbt": 0.012, "shortfall": 0.052}]}]}
    faux_paire = {"paires": [
        {"trace": "B", "fbt_avant": 0.011, "fbt_apres": 0.011,
         "shortfall_avant": 0.051, "shortfall_apres": 0.056},
        {"trace": "A", "fbt_avant": 0.002, "fbt_apres": 0.002,
         "shortfall_avant": 0.071, "shortfall_apres": 0.0715}]}
    r = rangs(faux_bruit, faux_paire)
    v("l'appariement suit le nom et non l'ordre", [x["trace"] for x in r] == ["A", "B"],
      str([x["trace"] for x in r]))
    v("... et chaque fleche part du bon nuage",
      abs(r[0]["colonnes"]["fbt"]["apres"] - 1.0) < 1e-9
      and abs(r[1]["colonnes"]["fbt"]["apres"] - 1.0) < 1e-9,
      str([x["colonnes"]["fbt"]["apres"] for x in r]))
    # ⚠ Une trace presente dans le balayage mais absente de la table appariee est SAUTEE, pas
    # dessinee a moitie : une ligne sans fleche se lirait comme un effet nul.
    v("une trace sans paire est sautee", len(rangs(faux_bruit, {"paires": []})) == 0)

    # ⚠⚠⚠ LA LECTURE, testee dans LES DEUX SENS. Une fonction qui repondrait toujours « dedans »
    # rendrait la figure incapable de montrer un effet.
    v("une valeur au milieu du nuage est lue dedans",
      dedans({"graines": [0.5, 1.0, 1.5], "apres": 1.2}))
    v("... et une valeur au-dela est lue dehors",
      not dedans({"graines": [0.5, 1.0, 1.5], "apres": 2.0}))
    v("... y compris juste en dessous du minimum",
      not dedans({"graines": [0.5, 1.0, 1.5], "apres": 0.49}))

    # ⚠⚠ L'ETIQUETTE, testee sur les deux formes reellement presentes dans le corpus. La
    # troncature aveugle rendait « 924-w010-027 » et « 46-052_jordi » ; ce controle interdit
    # qu'elle revienne.
    v("l'etiquette garde les indices de spire",
      etiquette("20260623141924-w010-027") == "w010-027",
      etiquette("20260623141924-w010-027"))
    v("... y compris avec un suffixe d'auteur",
      etiquette("20260623141135-w046-052_jordi") == "w046-052_jordi",
      etiquette("20260623141135-w046-052_jordi"))
    v("... et un nom sans indice ne leve pas", etiquette("sans_indice") == "sans_indice"[-12:])
    # ⚠⚠ LA COLLISION, testee dans LES DEUX SENS : deux traces aux memes indices doivent etre
    # separees, et les autres ne doivent PAS etre encombrees pour autant.
    lot = etiquettes(["20260701183126-w038-045", "20260623143441-w038-045",
                      "20260623150417-w064-068"])
    v("deux traces aux memes indices sont distinguees", lot[0] != lot[1], str(lot))
    v("... et une trace unique n'est pas encombree pour autant",
      lot[2] == "w064-068", str(lot))

    lignes = prose(r)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle dit le compte, pas seulement les dispersions",
      any("sur 2" in l for l in lignes), str(lignes))

    with tempfile.TemporaryDirectory() as d:
        rac = Path(d)
        f_bruit = rac / "bruit.json"
        f_paire = rac / "paire.json"
        f_bruit.write_text(json.dumps(faux_bruit), encoding="utf-8")
        f_paire.write_text(json.dumps(faux_paire), encoding="utf-8")

        lu_br, lu_pa = lire(f_bruit, f_paire)
        v("les deux JSON sont lus",
          len(lu_br["lignes"]) == 2 and len(lu_pa["paires"]) == 2)

        out_img, poses, cadres = dessiner(lu_br, lu_pa, rac / "f.png")
        v("l'image est écrite", out_img.is_file())
        v("... et elle n'est pas vide", out_img.stat().st_size > 1000)

        im = Image.open(out_img).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0] == 1240)
        v("... et sa hauteur correspond au nombre de rangées", im.size[1] == 180 + 34 * 2 + 150)

        pixels = list(im.getdata())
        v("... et elle porte les couleurs requises",
          AMBRE in pixels and GRIS in pixels)

        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]) == [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres) == [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses) == [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]] == [])

        # ⚠ Sonde : un fichier manquant est refusé
        try:
            lire(rac / "inexistant.json", f_paire)
            v("sonde : un fichier manquant est refusé", False)
        except FileNotFoundError:
            v("sonde : un fichier manquant est refusé", True)

        # ⚠ Sonde : un JSON sans paires est refusé
        f_invalide = rac / "sans_paire.json"
        f_invalide.write_text(json.dumps({"vide": True}), encoding="utf-8")
        try:
            lire(f_bruit, f_invalide)
            v("sonde : un JSON sans paires est refusé", False)
        except ValueError:
            v("sonde : un JSON sans paires est refusé", True)

        # ⚠ Sonde : aucun appariement possible est refusé par dessiner
        try:
            dessiner(faux_bruit,
                     {"paires": [{"trace": "Z", "fbt_apres": 1.0, "shortfall_apres": 1.0}]},
                     rac / "vide.png")
            v("sonde : aucun appariement possible est refusé", False)
        except ValueError:
            v("sonde : aucun appariement possible est refusé", True)

        # ⚠ Sonde : la garde attrape un débordement simulé
        trop_long = [(1200, 50, "Texte debordant de la toile", police(16))]
        v("sonde : textes_debordants détecte le dépassement",
          len(textes_debordants(trop_long, 1240)) > 0)

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--bruit", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_bruit_de_lechantillon.json")
    p.add_argument("--paire", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "reparation_et_proximite_scroll1.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "07_bruit_de_lechantillon.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    bruit, paire = lire(a.bruit, a.paire)
    out, _, _ = dessiner(bruit, paire, a.sortie)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"écrit : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
