#!/usr/bin/env python3
"""Ce que le détecteur voit sur une face écrite et sur un vide — à la même échelle.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de C2 est un **non-effondrement** : la dispersion
que le détecteur rend dans un vide vaut 94 % de celle qu'il rend sur une face, alors que le
contraste local y est **quatorze fois plus bas**. Un rapport de 0,94 se lit comme deux nombres ;
deux cartes côte à côte se lisent d'un coup.

⭐⭐⭐ ET L'ÉCHELLE EST COMMUNE, ce qui est tout le sujet. Rendre chaque carte à sa propre plage
ferait paraître le vide aussi structuré que la face — c'est-à-dire que la figure *illustrerait*
la panne au lieu de la montrer. Une seule plage, prise sur les deux, et la différence de
**niveau** devient visible en même temps que l'égalité de **dispersion**.

⭐ LE PROFIL DE PROFONDEUR EST AU-DESSUS parce qu'il rend la figure auto-suffisante : on y voit
que la fenêtre « face » est posée sur le pic de contraste et la fenêtre « nulle » dans le creux,
donc que le décalage est **mesuré** et non choisi.

⚠ Les nombres sont LUS dans `docs/mesures/le_nul_verso.json` et les cartes dans
`docs/mesures/nul_verso_cartes/`, jamais retapés.

Usage :
    uv run python src/figures/figure_le_nul_verso.py --verifier
    uv run python src/figures/figure_le_nul_verso.py --tous \\
        --sortie docs/images/75_le_nul_verso.png

⚠⚠ `--tous` n'est pas une option de confort : c'est la forme **publiée**. Sans lui le module
dessine UN segment, et `docs/75` en montre trois. Le bloc ci-dessus est lu par
`src/depot/fraicheur_des_figures.py`, qui rejoue chaque figure pour la comparer à son image —
une déclaration incomplète y faisait juger l'image publiée contre un dessin que personne ne
publie, donc la déclarait périmée alors qu'elle était juste.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]
CARTES = RACINE / "docs" / "mesures" / "nul_verso_cartes"

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


def lire(chemin: Path) -> dict:
    """Charge et valide une mesure de segment."""
    if not chemin.is_file():
        raise FileNotFoundError(f"mesure absente : {chemin}")
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not donnees.get("segment") or not donnees.get("profil"):
        raise ValueError(f"structure invalide dans {chemin}")
    return donnees


def bornes_communes(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """
    @brief La plage de couleur partagée par les deux cartes.

    ⚠⚠ Les percentiles 1 et 99 des DEUX cartes réunies, pas les extrêmes : un seul pixel
    aberrant fixerait la plage et écraserait tout le reste vers le gris. Et pas une plage par
    carte — c'est la comparaison qui est le sujet.
    """
    ensemble = np.concatenate([a[np.isfinite(a)].ravel(), b[np.isfinite(b)].ravel()])
    if ensemble.size == 0:
        return 0.0, 1.0
    lo, hi = float(np.percentile(ensemble, 1)), float(np.percentile(ensemble, 99))
    return (lo, hi) if hi > lo else (lo, lo + 1.0)


def en_gris(carte: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """
    @brief Une carte de prédiction en niveaux de gris, sur une plage IMPOSÉE.

    ⚠ Les pixels non couverts (NaN) sortent en **bleu sombre** et non en noir : un pixel non
    mesuré et un pixel à prédiction basse ne doivent pas se ressembler.
    """
    v = np.clip((carte - lo) / max(1e-9, hi - lo), 0.0, 1.0)
    # ⚠ Les NaN sont neutralisés AVANT la conversion, pas après : le cast d'un NaN en entier est
    # indéfini et émet un avertissement, et un avertissement dans une figure est du bruit qu'on
    # finit par ne plus lire. Ils sont de toute façon recouverts juste en dessous.
    g = (np.nan_to_num(v, nan=0.0) * 255).astype(np.uint8)
    rgb = np.dstack([g, g, g])
    absent = ~np.isfinite(carte)
    rgb[absent] = (18, 22, 40)
    return rgb


def series_du_panneau(m: dict) -> tuple[list[float], list[float]]:
    """
    @brief Les deux courbes du panneau de profondeur : (contraste, intensité).

    ⚠ Le repli existe pour les dossiers d'AVANT la correction du 2026-09-05, qui ne portent que
    le contraste : ils doivent rester dessinables. Un outil qui refuse les anciennes mesures
    pousse à les refaire, et refaire une mesure coûte deux inférences.
    """
    contraste = m["profil"]
    return contraste, (m.get("profil_intensite") or contraste)


def prose(m: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas.

    ⚠⚠ L'AUC EST EN TÊTE parce que c'est elle qui répond à la question posée : *peut-on, en
    regardant une valeur, dire si elle vient de la face ou du vide ?* Le niveau et la dispersion
    sont deux vues partielles de cette même question — une médiane qui se déplace n'est utile
    que si les distributions se séparent, et deux étendues égales n'interdisent pas une
    séparation parfaite.
    """
    f, n = m["face"], m["nul"]
    auc = m.get("auc_face_contre_nul")
    lignes = []
    if auc is not None:
        lignes.append(
            f"AUC face contre vide : {auc:.3f} -- la chance de distinguer un pixel de face "
            f"d'un pixel de vide sur sa seule valeur (0,5 = pile ou face).")
    cf, cn = m["contraste_face"], m["contraste_nul"]
    rapport = max(cf, cn) / max(1e-9, min(cf, cn))
    sens = "moins" if cn < cf else "PLUS"
    lignes += [
        f"contraste local : {cf:.3f} sur la face, {cn:.3f} dans le vide -- "
        f"{rapport:.1f}x {sens} dans le vide.",
        f"dispersion : {m['etendue_face']:.2f} sur la face, {m['etendue_nul']:.2f} dans le "
        f"vide (rapport {m['rapport_etendue']:.2f}).",
        f"niveau : mediane {f['mediane']:+.2f} sur la face, {n['mediane']:+.2f} dans le vide.",
    ]
    return lignes


def dessiner(m: dict, sortie: Path, cartes_dir: Path = CARTES) -> tuple[Path, list, list]:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    p_face = cartes_dir / f"{m['segment']}_face.npy"
    p_nul = cartes_dir / f"{m['segment']}_nul.npy"
    if not p_face.is_file() or not p_nul.is_file():
        raise FileNotFoundError(f"cartes introuvables pour {m['segment']} dans {cartes_dir}")
    a = np.load(p_face)
    b = np.load(p_nul)
    lo, hi = bornes_communes(a, b)

    cote = 420
    L, H = 2 * cote + 90, 150 + 190 + cote + 130
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(36, 24, "une face ecrite et un vide, vus par le meme detecteur",
           gros, TEXTE)
    ecrire(36, 50, f"{m['segment']} — meme pile, meme modele, meme pas ; "
                   "seule la profondeur change", moyen, DISCRET)

    # ---- le profil de profondeur, et les deux fenetres ---------------------------------
    px, py, pw, ph = 36, 92, L - 72, 130
    d.rectangle([px, py, px + pw, py + ph], outline=(60, 60, 60))
    contraste, intensite = series_du_panneau(m)
    n = len(intensite)
    for nom, debut, couleur in (("face", m["debut_face"], AMBRE),
                                ("vide", m["debut_nul"], GRIS)):
        x0 = px + int(pw * debut / n)
        x1 = px + int(pw * (debut + 26) / n)
        d.rectangle([x0, py + 1, x1, py + ph - 1], fill=(38, 32, 22) if nom == "face" else (26, 30, 34))
        ecrire(x0 + 4, py + 6, f"fenetre {nom}", petit, couleur)
    for serie, couleur, large in ((contraste, ROUGE, 1), (intensite, TEXTE, 2)):
        pts = [(px + int(pw * i / n), py + ph - int((ph - 8) * v)) for i, v in enumerate(serie)]
        for u, w in zip(pts, pts[1:]):
            d.line([u, w], fill=couleur, width=large)
    ecrire(px + 4, py + ph - 30, "intensite moyenne par couche -- c'est ELLE qui place les "
                                 "fenetres", petit, TEXTE)
    ecrire(px + 4, py + ph - 16, "contraste local -- un U a 2,4 µm : ses maxima sont les "
                                 "interfaces, pas la feuille", petit, ROUGE)

    # ---- les deux cartes, MEME echelle -------------------------------------------------
    for i, (nom, carte, sous) in enumerate((
            ("face ecrite", a, f"couches {m['debut_face']}..{m['debut_face'] + 26}"),
            ("vide entre feuilles", b, f"couches {m['debut_nul']}..{m['debut_nul'] + 26}"))):
        x0 = 36 + i * (cote + 18)
        y0 = py + ph + 44
        img = Image.fromarray(en_gris(carte, lo, hi)).resize((cote, cote), Image.NEAREST)
        toile.paste(img, (x0, y0))
        d.rectangle([x0, y0, x0 + cote, y0 + cote], outline=(70, 70, 70))
        ecrire(x0, y0 - 34, nom, moyen, TEXTE)
        ecrire(x0, y0 - 18, sous, petit, DISCRET)

    bas = py + ph + 44 + cote + 12
    ecrire(36, bas, f"meme echelle de gris : {lo:+.2f} a {hi:+.2f} (percentiles 1 et 99 des "
                    "DEUX cartes)", petit, AMBRE)
    for k, ligne in enumerate(prose(m)):
        ecrire(36, bas + 22 + k * 19, ligne, moyen, TEXTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def panorama(mesures: list[dict], sortie: Path, cartes_dir: Path = CARTES) -> tuple[Path, list, list]:
    """
    @brief Les trois segments l'un sous l'autre — la seule vue qui dise si c'est une propriété.
    """
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    cote, marge = 236, 36
    entete, ligne_h = 78, cote + 34

    def largeur(texte, fonte):
        boite = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), texte, font=fonte)
        return boite[2] - boite[0]

    colonne = max(
        [largeur(l, petit) for m in mesures for l in prose(m)[1:]]
        + [largeur(f"AUC face contre vide  {m.get('auc_face_contre_nul', 0):.3f}", moyen)
           for m in mesures]
        + [largeur(m["segment"].split("_")[0], moyen) for m in mesures])
    L = 2 * cote + 18 + 3 * marge + colonne
    H = entete + ligne_h * len(mesures) + 24
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(marge, 22, "une face et un vide, sur trois segments de PHerc0139",
           gros, TEXTE)
    ecrire(marge, 48, "meme pile, meme modele, meme pas ; seule la profondeur lue change",
           moyen, DISCRET)

    for k, m in enumerate(mesures):
        y = entete + k * ligne_h
        p_face = cartes_dir / f"{m['segment']}_face.npy"
        p_nul = cartes_dir / f"{m['segment']}_nul.npy"
        if not p_face.is_file() or not p_nul.is_file():
            raise FileNotFoundError(f"cartes introuvables pour {m['segment']} dans {cartes_dir}")
        a = np.load(p_face)
        b = np.load(p_nul)
        lo, hi = bornes_communes(a, b)
        for i, carte in enumerate((a, b)):
            x = marge + i * (cote + 18)
            toile.paste(Image.fromarray(en_gris(carte, lo, hi)).resize((cote, cote),
                                                                      Image.NEAREST), (x, y))
            d.rectangle([x, y, x + cote, y + cote], outline=(70, 70, 70))
            ecrire(x + 4, y + 4, "face" if i == 0 else "vide",
                   petit, AMBRE if i == 0 else GRIS)
        tx = marge + 2 * cote + 34
        auc = m.get("auc_face_contre_nul")
        ecrire(tx, y + 2, m["segment"].split("_")[0], moyen, TEXTE)
        if auc is not None:
            ecrire(tx, y + 24, f"AUC face contre vide  {auc:.3f}",
                   moyen, ROUGE if auc < 0.5 else TEXTE)
        ecrire(tx, y + 46, f"couches {m['debut_face']}..{m['debut_face'] + 26} "
                           f"contre {m['debut_nul']}..{m['debut_nul'] + 26}",
               petit, DISCRET)
        for j, texte in enumerate(prose(m)[1:]):
            ecrire(tx, y + 68 + j * 17, texte, petit, DISCRET)
        ecrire(tx, y + 68 + 3 * 17, f"echelle {lo:+.2f} a {hi:+.2f}", petit, AMBRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def verifier() -> int:
    """Auto-test HORS LIGNE : l'échelle commune, les absents, la prose, les sondes et le dessin."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    a = np.linspace(-1.6, 2.4, 100).reshape(10, 10)
    b = np.linspace(-1.7, 2.1, 100).reshape(10, 10)
    lo, hi = bornes_communes(a, b)
    # ⚠⚠ LA PLAGE VIENT DES DEUX CARTES : si elle ne venait que de la première, la seconde
    # saturerait ou s'écraserait, ce qui est exactement la façon de faire mentir la figure.
    v("la plage englobe les deux cartes", lo <= min(a.min(), b.min()) + 0.1
      and hi >= max(a.max(), b.max()) - 0.1, f"[{lo:.2f} ; {hi:.2f}]")
    # ⚠ Les percentiles, pas les extremes : un pixel aberrant ne doit pas fixer la plage.
    c = a.copy()
    c[0, 0] = 500.0
    lo2, hi2 = bornes_communes(c, b)
    v("... et un pixel aberrant ne l'emporte pas", hi2 < 10.0, f"{hi2:.2f}")
    v("une plage degeneree ne divise pas par zero",
      bornes_communes(np.zeros((4, 4)), np.zeros((4, 4)))[1] > 0.0)
    v("des cartes vides ne levent pas",
      bornes_communes(np.full((3, 3), np.nan), np.full((3, 3), np.nan)) == (0.0, 1.0))

    g = en_gris(np.array([[-1.6, 2.4], [np.nan, 0.0]]), -1.6, 2.4)
    v("le minimum de la plage est noir", tuple(g[0, 0]) == (0, 0, 0), str(g[0, 0]))
    v("... et le maximum blanc", tuple(g[0, 1]) == (255, 255, 255), str(g[0, 1]))
    # ⚠⚠ Un pixel NON MESURE ne doit pas ressembler a une prediction basse, sinon la figure
    # montre du vide la ou il n'y a pas de mesure.
    v("... et un pixel non mesuré n'est pas noir", tuple(g[1, 0]) != (0, 0, 0), str(g[1, 0]))

    faux = {"segment": "s", "profil": [0.5] * 109, "debut_face": 39, "debut_nul": 83,
            "contraste_face": 0.877, "contraste_nul": 0.063,
            "etendue_face": 3.994, "etendue_nul": 3.767, "rapport_etendue": 0.94,
            "auc_face_contre_nul": 0.819,
            "face": {"mediane": -0.272}, "nul": {"mediane": -1.502}}
    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    # ⚠⚠ L'AUC EN TETE : c'est la seule des trois grandeurs qui reponde a la question posee, et
    # une figure qui l'enterrerait en quatrieme ligne se lirait comme les deux precedentes.
    v("l'AUC ouvre la prose", lignes[0].startswith("AUC"), str(lignes[0]))
    v("... et elle dit le rapport de contraste, DANS LE BON SENS",
      any("13.9x moins dans le vide" in l for l in lignes), str(lignes))
    # ⚠⚠⚠ LA PHRASE DOIT SUIVRE LA MESURE. Elle disait « Nx moins » en dur ; depuis que les
    # fenetres se choisissent sur l'intensite, le vide tombe souvent sur une INTERFACE et porte
    # donc PLUS de contraste que la face -- la version en dur imprimait alors « 0x moins »,
    # c'est-a-dire une phrase fausse dans le sens qui rassure.
    inverse = dict(faux, contraste_face=0.187, contraste_nul=0.639)
    v("... et elle dit PLUS quand le vide en a plus",
      any("3.4x PLUS dans le vide" in l for l in prose(inverse)), str(prose(inverse)[1]))
    v("... et elle nomme le niveau", any("niveau :" in l for l in lignes), str(lignes))
    # ⚠ Une mesure d'avant l'AUC ne doit pas faire tomber la figure : elle en perd la premiere
    # ligne, pas sa capacite a etre dessinee. Un outil qui refuse les anciens dossiers pousse a
    # les refaire, et refaire une mesure coute huit minutes d'inference.
    sans = dict(faux); sans.pop("auc_face_contre_nul")
    v("... et une mesure sans AUC se dessine quand meme", len(prose(sans)) == 3, str(prose(sans)))
    # ⚠⚠ LE PANNEAU TRACE LES DEUX SERIES, et c'est ce qui rend la correction visible. Ecrit
    # d'abord comme un test sur la docstring de `dessiner` -- qui n'en a pas, donc le `if`
    # retombait sur True : une verification incapable d'echouer, dans le fichier d'a cote de
    # celui ou la meme faute vient d'etre corrigee. Extrait en fonction pure, il compare.
    c, i = series_du_panneau({"profil": [0.1] * 5, "profil_intensite": [0.9] * 5})
    v("le panneau prend l'intensite quand elle est la", i[0] == 0.9 and c[0] == 0.1, f"{i[0]}/{c[0]}")
    c2, i2 = series_du_panneau({"profil": [0.1] * 5})
    v("... et retombe sur le contraste quand elle manque", i2 == c2 == [0.1] * 5, str(i2))

    # --- VALIDATION HORS-LIGNE lire(), dessiner() ET panorama() AVEC SONDES ---
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        p_json = tmp / "mesure.json"
        p_json.write_text(json.dumps(faux), encoding="utf-8")

        m_lu = lire(p_json)
        v("lire charge le segment", m_lu["segment"] == "s")

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

        # Cartes .npy témoins
        c_dir = tmp / "cartes"
        c_dir.mkdir()
        mini_a = np.linspace(-1.0, 1.0, 100).reshape(10, 10)
        mini_b = np.linspace(-0.8, 0.8, 100).reshape(10, 10)
        np.save(c_dir / "s_face.npy", mini_a)
        np.save(c_dir / "s_nul.npy", mini_b)

        # Tracé d'un segment seul (dessiner)
        cible_single = tmp / "single.png"
        out_s, poses_s, cadres_s = dessiner(m_lu, cible_single, cartes_dir=c_dir)
        v("dessiner rend le chemin demandé", out_s == cible_single)
        v("le fichier png single est produit", cible_single.is_file() and cible_single.stat().st_size > 0)
        v("au moins 10 textes sont posés sur le dessin", len(poses_s) >= 10)
        v("aucun texte ne déborde (single)", textes_debordants(poses_s, cadres_s[0][2]) == [])
        v("aucun texte ne sort de son cadre (single)", textes_hors_cadre(poses_s, cadres_s) == [])
        v("aucun chevauchement critique (single)", textes_qui_se_recouvrent(poses_s) == [])

        # Tracé du panorama
        cible_pano = tmp / "panorama.png"
        out_p, poses_p, cadres_p = panorama([m_lu], cible_pano, cartes_dir=c_dir)
        v("panorama rend le chemin demandé", out_p == cible_pano)
        v("le fichier png panorama est produit", cible_pano.is_file() and cible_pano.stat().st_size > 0)
        v("au moins 5 textes sont posés sur le panorama", len(poses_p) >= 5)
        v("aucun texte ne déborde (panorama)", textes_debordants(poses_p, cadres_p[0][2]) == [])
        v("aucun texte ne sort de son cadre (panorama)", textes_hors_cadre(poses_p, cadres_p) == [])
        v("aucun chevauchement critique (panorama)", textes_qui_se_recouvrent(poses_p) == [])

        # Sonde 3 : texte débordant artificiel
        gros, _, _ = police(17, 13, 11)
        poses_trop_larges = poses_s + [(cadres_s[0][2] - 10, 50, "texte qui sort largement de l'image a droite", gros)]
        debord = textes_debordants(poses_trop_larges, cadres_s[0][2])
        v("sonde : un texte débordant est bien intercepté", len(debord) > 0)

        # Sonde 4 : cartes manquantes
        sonde_cartes = False
        try:
            dessiner(m_lu, tmp / "vide.png", cartes_dir=tmp / "vide_dir")
        except FileNotFoundError:
            sonde_cartes = True
        v("sonde : cartes manquantes refusées par dessiner", sonde_cartes)

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "le_nul_verso_20260325000000-w046.json")
    p.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "75_le_nul_verso.png")
    p.add_argument("--tous", action="store_true",
                    help="les trois segments l'un sous l'autre, depuis docs/mesures/")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.tous:
        fichiers = sorted((RACINE / "docs" / "mesures").glob("le_nul_verso*.json"))
        mesures = [lire(f) for f in fichiers]
        # ⚠ On ne dessine que ce qui a rendu DEUX cartes : un segment refusé par la garde porte
        # son profil et sa raison, pas d'image, et l'inventer serait un panneau vide qui
        # ressemble à une mesure.
        mesures = [m for m in mesures if m.get("face") and not m["face"].get("echec")]
        if not mesures:
            raise SystemExit("aucune mesure complète dans docs/mesures/")
        out, _, _ = panorama(mesures, a.sortie)
    else:
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
