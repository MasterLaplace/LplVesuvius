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
    uv run python src/figures/figure_le_nul_verso.py \\
        --sortie docs/images/75_le_nul_verso.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
CARTES = RACINE / "docs" / "mesures" / "nul_verso_cartes"

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


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
    lignes += [
        f"contraste local : {m['contraste_face']:.3f} sur la face, "
        f"{m['contraste_nul']:.3f} dans le vide -- "
        f"{m['contraste_face'] / max(1e-9, m['contraste_nul']):.0f}x moins.",
        f"et pourtant la dispersion du detecteur ne tombe que de "
        f"{100 * (1 - m['rapport_etendue']):.0f} % ({m['etendue_face']:.2f} -> {m['etendue_nul']:.2f}).",
        f"le NIVEAU, lui, se deplace : mediane {f['mediane']:+.2f} contre {n['mediane']:+.2f}.",
    ]
    return lignes


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    a = np.load(CARTES / f"{m['segment']}_face.npy")
    b = np.load(CARTES / f"{m['segment']}_nul.npy")
    lo, hi = bornes_communes(a, b)

    cote = 420
    L, H = 2 * cote + 90, 150 + 190 + cote + 130
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    d.text((36, 24), "une face ecrite et un vide, vus par le meme detecteur",
           fill=TEXTE, font=gros)
    d.text((36, 50), f"{m['segment']} — meme pile, meme modele, meme pas ; "
                     "seule la profondeur change", fill=DISCRET, font=moyen)

    # ---- le profil de profondeur, et les deux fenetres ---------------------------------
    px, py, pw, ph = 36, 92, L - 72, 130
    d.rectangle([px, py, px + pw, py + ph], outline=(60, 60, 60))
    # ⚠⚠⚠ LES DEUX SERIES, ET C'EST LE SUJET DE CE PANNEAU. A 2,4 µm le contraste local
    # dessine un U -- maximal aux deux interfaces de la feuille, minimal dans son interieur --
    # donc s'en servir pour placer les fenetres met la face au BORD et le vide DANS le papyrus.
    # C'est l'inversion qui a ete payee le 2026-09-05. L'intensite, elle, pique sur la matiere.
    # Les tracer ensemble rend la correction verifiable a l'oeil au lieu d'etre racontee.
    contraste, intensite = series_du_panneau(m)
    n = len(intensite)
    for nom, debut, couleur in (("face", m["debut_face"], AMBRE),
                                ("vide", m["debut_nul"], GRIS)):
        x0 = px + int(pw * debut / n)
        x1 = px + int(pw * (debut + 26) / n)
        d.rectangle([x0, py + 1, x1, py + ph - 1], fill=(38, 32, 22) if nom == "face" else (26, 30, 34))
        d.text((x0 + 4, py + 6), f"fenetre {nom}", fill=couleur, font=petit)
    for serie, couleur, large in ((contraste, ROUGE, 1), (intensite, TEXTE, 2)):
        pts = [(px + int(pw * i / n), py + ph - int((ph - 8) * v)) for i, v in enumerate(serie)]
        for u, w in zip(pts, pts[1:]):
            d.line([u, w], fill=couleur, width=large)
    d.text((px + 4, py + ph - 30), "intensite moyenne par couche -- c'est ELLE qui place les "
                                   "fenetres", fill=TEXTE, font=petit)
    d.text((px + 4, py + ph - 16), "contraste local -- un U a 2,4 µm : ses maxima sont les "
                                   "interfaces, pas la feuille", fill=ROUGE, font=petit)

    # ---- les deux cartes, MEME echelle -------------------------------------------------
    for i, (nom, carte, sous) in enumerate((
            ("face ecrite", a, f"couches {m['debut_face']}..{m['debut_face'] + 26}"),
            ("vide entre feuilles", b, f"couches {m['debut_nul']}..{m['debut_nul'] + 26}"))):
        x0 = 36 + i * (cote + 18)
        y0 = py + ph + 44
        img = Image.fromarray(en_gris(carte, lo, hi)).resize((cote, cote), Image.NEAREST)
        toile.paste(img, (x0, y0))
        d.rectangle([x0, y0, x0 + cote, y0 + cote], outline=(70, 70, 70))
        d.text((x0, y0 - 34), nom, fill=TEXTE, font=moyen)
        d.text((x0, y0 - 18), sous, fill=DISCRET, font=petit)

    bas = py + ph + 44 + cote + 12
    d.text((36, bas), f"meme echelle de gris : {lo:+.2f} a {hi:+.2f} (percentiles 1 et 99 des "
                      "DEUX cartes)", fill=AMBRE, font=petit)
    for k, ligne in enumerate(prose(m)):
        d.text((36, bas + 22 + k * 19), ligne, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"plage": [lo, hi], "rapport_etendue": m["rapport_etendue"], "sortie": str(sortie)}


def verifier() -> int:
    """Auto-test HORS LIGNE : l'échelle commune, les absents, la prose."""
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
    v("... et elle dit le rapport de contraste", any("14x moins" in l for l in lignes),
      str(lignes))
    v("... et elle nomme le NIVEAU", any("NIVEAU" in l for l in lignes), str(lignes))
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

    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "le_nul_verso_20260325000000-w046.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_nul_verso.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
