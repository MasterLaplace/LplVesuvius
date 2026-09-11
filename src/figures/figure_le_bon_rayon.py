#!/usr/bin/env python3
"""Trois paramètres qui semblaient importants, et qui cessent de l'être ensemble.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de
[`07`](../../docs/archive/07_reparee_nest_pas_propre.md) §11 est le même énoncé répété sur trois familles
— le seuil, la grandeur, la référence locale — et trois tableaux ne se lisent pas comme un fait
unique. Trois courbes qui s'effondrent à gauche et trois qui restent plates à droite se lisent
d'un coup, et c'est **exactement** ce que la mesure dit : le rayon injectait une erreur
structurée, donc toute variation changeait la part qui en fuyait ; corrigé, plus rien ne bouge.

⭐⭐ LES SIX PANNEAUX PARTAGENT LE MÊME AXE VERTICAL. Donner à la colonne de droite une échelle
ajustée à ses propres données ferait ré-apparaître une dispersion qui n'existe plus — c'est la
façon la plus courante de faire mentir un graphique sans écrire un seul chiffre faux.

⭐ ET LA BANDE DE BRUIT EST DESSINÉE. Chaque rho est lui-même un tirage d'étendue **0,125**
(`le_bruit_de_lechantillon --population`, cinq graines). Sans elle, un lecteur compare des
hauteurs à la troisième décimale ; avec elle, il voit que les points de droite sont **tous dans
la même bande**, donc indiscernables. C'est la garde contre la sur-lecture, en image.

⚠ Les nombres sont LUS dans `docs/mesures/le_seuil_au_bon_rayon.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_bon_rayon.py --verifier
    uv run python src/figures/figure_le_bon_rayon.py \\
        --mesure docs/mesures/le_seuil_au_bon_rayon.json \\
        --sortie docs/images/07_le_bon_rayon.png
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)


def lire(chemin: Path) -> dict:
    """Charge et valide la mesure nécessaire au tracé."""
    if not chemin.is_file():
        raise FileNotFoundError(f"mesure absente : {chemin}")
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not donnees.get("grandeurs") and not donnees.get("seuils"):
        raise ValueError(f"structure invalide dans {chemin}")
    return donnees
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)
BANDE = (40, 34, 22)

BAS, HAUT = 0.0, 1.0
"""Les bornes de l'axe des rho.

⚠⚠ FIXES, et de zéro à un : un axe ajusté aux données ferait paraître énorme n'importe quelle
dispersion, y compris une dispersion nulle. Zéro a un sens hors de ce jeu (aucune corrélation),
un aussi (parfaite), donc les deux bornes sont lisibles par quelqu'un qui n'a pas lu le document.
⚠ `ratio_p5` est négatif par nature — la corrélation est **inverse** — donc c'est sa **valeur
absolue** qui est tracée, et le libellé le dit."""

ETENDUE_DE_GRAINE = 0.125
"""L'étendue du rho d'une graine à l'autre, mesurée sur cinq graines. ⚠ Recopiée depuis
`le_bruit_de_lechantillon.py`, où elle est **mesurée** ; ici elle n'est que dessinée."""


def echelle(valeur: float, pixels: int) -> int:
    """Un rho, en pixels depuis le bas de l'axe."""
    v = min(max(valeur, BAS), HAUT)
    return int(round((v - BAS) / (HAUT - BAS) * pixels))


def familles(mesure: dict) -> list[dict]:
    """
    @brief Les trois familles, chacune avec ses points à l'ancien rayon et au corrigé.

    ⚠⚠ Une famille n'est retenue que si ses DEUX colonnes existent. Dessiner une famille dont
    seule la moitié est mesurée produirait un panneau où l'absence ressemble à un effondrement.
    """
    out = []

    def points(bloc: str, cles, libelle):
        av, ap, noms = [], [], []
        for c in cles:
            d = mesure.get(bloc, {}).get(c)
            if not d or not d.get("ancien") or not d.get("corrige"):
                continue
            av.append(abs(d["ancien"]["rho"]))
            ap.append(abs(d["corrige"]["rho"]))
            noms.append(libelle(c))
        return av, ap, noms

    seuils = [f"below_{x}" for x in ("015", "020", "025", "030", "033", "040", "050", "060", "070")]
    av, ap, noms = points("seuils", seuils,
                          lambda c: ("1/3" if c == "below_033" else f"0,{c[-2:]}"))
    if av:
        out.append(dict(titre="le SEUIL", sous="rho par seuil de rapport",
                        av=av, ap=ap, noms=noms, ordonnee=True))

    grandeurs = ("fraction_below_third", "fraction_below_half", "ratio_p5", "shortfall",
                 "shortfall_worst_decile")
    court = {"fraction_below_third": "1/3", "fraction_below_half": "1/2",
             "ratio_p5": "p5 (abs)", "shortfall": "deficit", "shortfall_worst_decile": "decile"}
    av, ap, noms = points("grandeurs", grandeurs, lambda c: court.get(c, c))
    if av:
        out.append(dict(titre="la GRANDEUR", sous="avec seuil, et sans",
                        av=av, ap=ap, noms=noms, ordonnee=False))

    fam = mesure.get("reference_locale") or {}
    if fam.get("ancien") and fam.get("corrige"):
        # ⚠ TRI NUMERIQUE au sein de chaque genre, pas alphabetique : l'ordre alphabetique
        # rendait « col 10, col 100, col 150, col 20, col 50 », qui se lit comme une largeur
        # qui monte puis redescend alors qu'elle ne fait que monter.
        def rang(k: str) -> tuple:
            genre, _, n = k.rpartition("_")
            return (0 if genre == "colonnes" else 1, int(n) if n.isdigit() else 0)
        cles = [k for k in sorted(fam["corrige"], key=rang) if k in fam["ancien"]]
        av = [fam["ancien"][k]["rho"] for k in cles]
        ap = [fam["corrige"][k]["rho"] for k in cles]
        noms = [k.replace("colonnes_", "col ").replace("boule_", "boule ") for k in cles]
        out.append(dict(titre="la REFERENCE locale", sous="bande de colonnes, boule 3D",
                        av=av, ap=ap, noms=noms, ordonnee=False))
    return out


def prose(fams: list[dict]) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    etendues_av = [max(f["av"]) - min(f["av"]) for f in fams]
    etendues_ap = [max(f["ap"]) - min(f["ap"]) for f in fams]
    return [
        "a gauche, le rayon de recherche est 4x trop grand : il trouve la spire VOISINE,",
        "qui est de la geometrie normale, et noie l'anomalie dedans.",
        f"chaque famille s'y etale de {min(etendues_av):.2f} a {max(etendues_av):.2f}.",
        f"a droite, au rayon tire de la physique, de {min(etendues_ap):.2f} a "
        f"{max(etendues_ap):.2f} -- sous le bruit du rho.",
        "aucun de ces trois choix ne compte : c'est le rayon qui les faisait paraitre importants.",
    ]


def dessiner(mesure: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    fams = familles(mesure)
    if not fams:
        raise ValueError("aucune famille complète dans la mesure")

    larg_p, haut_p = 250, 300
    marge_g, marge_h, ecart = 76, 150, 56
    L = marge_g + 2 * larg_p + ecart + 60
    H = marge_h + len(fams) * (haut_p + 96) + 130
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(60, 30, "trois parametres qui cessent de compter ENSEMBLE",
           gros, TEXTE)
    ecrire(60, 56, "correlation aux croisements publies, Scroll 1 -- "
                   "meme axe des deux cotes", moyen, DISCRET)
    ecrire(marge_g + larg_p // 2 - 60, 88, "rayon 4x TROP GRAND", moyen, ROUGE)
    ecrire(marge_g + larg_p + ecart + larg_p // 2 - 60, 88,
           "rayon tire de la PHYSIQUE", moyen, AMBRE)

    for i, f in enumerate(fams):
        y0 = marge_h + i * (haut_p + 96)
        # ⚠ Le libelle etait POSE SUR l'axe des rho, qu'il recouvrait. Au-dessus de sa rangee,
        # il ne peut rien recouvrir.
        ecrire(marge_g, y0 - 22, f["titre"], moyen, TEXTE)
        # ⚠ La sous-legende est posee APRES la largeur reelle du titre, mesuree : un decalage
        # fixe la faisait chevaucher « la REFERENCE locale », le plus long des trois.
        ecrire(marge_g + int(d.textlength(f["titre"], font=moyen)) + 18, y0 - 20,
               f["sous"], petit, DISCRET)
        for j, (cle, couleur) in enumerate((("av", ROUGE), ("ap", AMBRE))):
            x0 = marge_g + j * (larg_p + ecart)
            d.rectangle([x0, y0, x0 + larg_p, y0 + haut_p], outline=(60, 60, 60))
            # ⚠ La bande de bruit est dessinee AVANT les points : par-dessus, elle aurait l'air
            # d'une zone ajoutee apres coup sur des donnees choisies.
            centre = statistics.median(f[cle])
            b1 = y0 + haut_p - echelle(centre + ETENDUE_DE_GRAINE / 2, haut_p)
            b2 = y0 + haut_p - echelle(centre - ETENDUE_DE_GRAINE / 2, haut_p)
            d.rectangle([x0 + 1, b1, x0 + larg_p - 1, b2], fill=BANDE)
            for r in (0.25, 0.50, 0.75):
                yy = y0 + haut_p - echelle(r, haut_p)
                d.line([x0, yy, x0 + larg_p, yy], fill=(36, 36, 36))
                if j == 0:
                    ecrire(x0 - 34, yy - 6, f"{r:.2f}", petit, DISCRET)
            pas = larg_p / max(len(f[cle]), 1)
            pts = []
            for k, val in enumerate(f[cle]):
                px = int(x0 + pas * (k + 0.5))
                py = y0 + haut_p - echelle(abs(val), haut_p)
                pts.append((px, py))
                d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=couleur)
            # ⚠⚠ UNE LIGNE ENTRE DEUX CATEGORIES INVENTE UNE TENDANCE. Le balayage de seuil est
            # ordonne (0,15 → 0,70), donc une ligne y a un sens ; « 1/3, 1/2, p5, deficit,
            # decile » et « boule, colonnes » ne le sont pas, et les relier dessinait un V que
            # personne n'a mesure. Points seuls dans ce cas.
            if f.get("ordonnee"):
                for a, b in zip(pts, pts[1:]):
                    d.line([a, b], fill=couleur, width=1)
            etendue = max(f[cle]) - min(f[cle])
            ecrire(x0 + 6, y0 + haut_p + 8, f"etendue {etendue:.3f}", petit, couleur)
            if j == 1:
                # ⚠ EN QUINCONCE : a huit variantes les libelles se recouvraient au point
                # d'etre illisibles (« boule 100boule 200boule 400col 10col 100 »). Une ligne
                # sur deux les separe sans rien retirer.
                for k, nom in enumerate(f["noms"]):
                    ecrire(int(x0 + pas * (k + 0.5)) - 4 * len(nom),
                           y0 + haut_p + 26 + (k % 2) * 15, nom,
                           petit, DISCRET)

    bas = marge_h + len(fams) * (haut_p + 96) - 20
    d.rectangle([60, bas + 3, 84, bas + 13], fill=BANDE)
    ecrire(92, bas, "bruit du rho d'une graine a l'autre (etendue 0,125, cinq graines)",
           petit, DISCRET)
    for k, ligne in enumerate(prose(fams)):
        ecrire(60, bas + 26 + k * 19, ligne, moyen, TEXTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def verifier() -> int:
    """Auto-test HORS LIGNE : l'axe, la sélection des familles, la prose, les sondes et le dessin."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("le bas de l'axe est a zero pixel", echelle(0.0, 300) == 0)
    v("le haut est en butee", echelle(1.0, 300) == 300)
    v("le milieu est au milieu", echelle(0.5, 300) == 150)
    # ⚠ `ratio_p5` est NEGATIF : sans borne basse il sortirait du cadre par le bas, et une
    # correlation inverse parfaitement forte paraitrait nulle.
    v("une valeur negative est ramenee en butee basse", echelle(-0.85, 300) == 0)
    v("... et une valeur au-dela de 1 en butee haute", echelle(1.4, 300) == 300)

    faux = {
        "grandeurs": {
            "fraction_below_third": {"ancien": {"rho": 0.769}, "corrige": {"rho": 0.840}},
            "ratio_p5": {"ancien": {"rho": -0.512}, "corrige": {"rho": -0.851}},
            "shortfall": {"ancien": {"rho": 0.340}, "corrige": {"rho": 0.785}},
            # ⚠⚠ Une grandeur dont une seule colonne existe doit etre SAUTEE : la dessiner
            # ferait passer une absence pour un effondrement.
            "incomplete": {"ancien": {"rho": 0.5}, "corrige": None},
        },
        "seuils": {"below_015": {"ancien": {"rho": 0.759}, "corrige": {"rho": 0.854}},
                   "below_070": {"ancien": {"rho": 0.282}, "corrige": {"rho": 0.829}}},
        "reference_locale": {
            "ancien": {"colonnes_150": {"rho": 0.769, "couverture": 1.0},
                       "boule_400": {"rho": 0.560, "couverture": 1.0}},
            "corrige": {"colonnes_150": {"rho": 0.840, "couverture": 1.0},
                        "boule_400": {"rho": 0.803, "couverture": 0.985}}},
    }
    fams = familles(faux)
    v("les trois familles sont trouvees", len(fams) == 3, str([f["titre"] for f in fams]))
    grandeur = next(f for f in fams if f["titre"] == "la GRANDEUR")
    v("une famille a moitie mesuree est sautee", len(grandeur["av"]) == 3,
      str(grandeur["noms"]))
    # ⚠⚠ La VALEUR ABSOLUE, testee : `ratio_p5` vaut -0,851 et doit se tracer a 0,851. Sans ca
    # la correlation la plus forte du tableau serait dessinee comme la plus faible.
    v("une correlation inverse est tracee par sa valeur absolue",
      abs(max(grandeur["ap"]) - 0.851) < 1e-9, str(grandeur["ap"]))
    v("une famille sans aucune donnee ne produit rien", familles({}) == [])
    # ⚠⚠ SEUL le balayage de seuil est ordonne, donc seul lui a le droit d'etre relie.
    v("le balayage de seuil est declare ordonne",
      next(f for f in fams if f["titre"] == "le SEUIL")["ordonnee"])
    v("... et les familles de categories ne le sont pas",
      not any(f["ordonnee"] for f in fams if f["titre"] != "le SEUIL"))
    # ⚠ Le tri de la famille de reference est NUMERIQUE dans chaque genre : l'alphabetique
    # rendait « col 10, col 100, col 150, col 20, col 50 ».
    ref = next(f for f in fams if f["titre"] == "la REFERENCE locale")
    v("la reference locale range les colonnes avant les boules",
      ref["noms"][0].startswith("col"), str(ref["noms"]))

    lignes = prose(fams)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle nomme la cause, pas seulement les nombres",
      any("rayon" in l for l in lignes), str(lignes))

    # --- VALIDATION HORS-LIGNE lire() ET dessiner() AVEC SONDES ---
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        p_json = tmp / "mesure.json"
        p_json.write_text(json.dumps(faux), encoding="utf-8")

        m_lu = lire(p_json)
        v("lire charge les grandeurs", len(m_lu.get("grandeurs", {})) == 4)

        # Sonde 1 : fichier absent
        sonde_absent = False
        try:
            lire(tmp / "inexistant.json")
        except FileNotFoundError:
            sonde_absent = True
        v("sonde : fichier json absent lève FileNotFoundError", sonde_absent)

        # Sonde 2 : schéma invalide
        p_invalide = tmp / "invalide.json"
        p_invalide.write_text(json.dumps({"aucun": 1}), encoding="utf-8")
        sonde_invalide = False
        try:
            lire(p_invalide)
        except ValueError:
            sonde_invalide = True
        v("sonde : schéma json invalide lève ValueError", sonde_invalide)

        # Tracé réel de la figure témoin
        cible = tmp / "figure.png"
        out, poses, cadres = dessiner(m_lu, cible)
        v("dessiner rend le chemin demandé", out == cible)
        v("le fichier png est produit", cible.is_file() and cible.stat().st_size > 0)
        v("au moins 20 textes sont posés", len(poses) >= 20)
        larg_toile = 76 + 2 * 250 + 56 + 60
        v("aucun texte ne déborde de la toile", textes_debordants(poses, larg_toile) == [])
        v("aucun texte ne sort de son cadre", textes_hors_cadre(poses, cadres) == [])
        v("aucun chevauchement critique", textes_qui_se_recouvrent(poses) == [])

        # Sonde 3 : texte débordant artificiel
        gros, _, _ = police(17, 13, 11)
        poses_trop_larges = poses + [(larg_toile - 10, 50, "texte qui sort largement de l'image a droite", gros)]
        debord = textes_debordants(poses_trop_larges, larg_toile)
        v("sonde : un texte débordant est bien intercepté", len(debord) > 0)

        # Sonde 4 : texte hors cadre
        poses_hors = poses + [(larg_toile - 10, 100, "texte hors cadre", gros)]
        hors = textes_hors_cadre(poses_hors, cadres)
        v("sonde : un texte hors cadre est bien intercepté", len(hors) > 0)

        # Sonde 5 : mesure vide refusée par dessiner
        sonde_vide = False
        try:
            dessiner({}, tmp / "vide.png")
        except ValueError:
            sonde_vide = True
        v("sonde : mesure vide refusée par dessiner", sonde_vide)

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_seuil_au_bon_rayon.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "07_le_bon_rayon.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    mesure = lire(a.mesure)
    out, _, _ = dessiner(mesure, a.sortie)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"écrit : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
