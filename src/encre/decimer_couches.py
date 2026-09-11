#!/usr/bin/env python3
"""Décimer une pile de couches et ses étiquettes du MÊME facteur, pour un test contrôlé.

⚠⚠ Pourquoi ce fichier existe. `Frag1` est scanné à **3,24 µm** et le modèle a été entraîné
à **7,91 µm** (Scroll 1, cf. [`58`](../../docs/archive/58_resolution_ou_rouleau.md) §8 bis). L'AUC de
**0,746** mesurée contre la vérité terrain est donc prise **hors du domaine d'entraînement**,
sur un scan 2,4 fois plus fin. Le test juste est de ramener le fragment au pas du modèle et
de refaire la mesure : si l'AUC monte, l'écart s'explique par la résolution ; sinon, non.

⚠⚠⚠ LES ÉTIQUETTES SONT DÉCIMÉES PAR MAJORITÉ, jamais par échantillonnage. Prendre un pixel
sur deux perdrait la moitié des traits fins et rendrait la vérité terrain plus pauvre que la
réalité — ce qui **abaisserait** l'AUC pour une raison étrangère au modèle. La majorité
(moyenne puis seuil à un demi) garde la part d'encre du bloc.

⚠ Et les couches sont décimées par MOYENNE, comme un voxel plus large intègre réellement.
`58` note la limite : une décimation conserve le détail en PROFONDEUR qu'un vrai scan
grossier n'aurait pas, donc le résultat est un **majorant** de ce qu'un vrai scan rendrait.

Usage :
    uv run python src/encre/decimer_couches.py --verifier
    uv run python src/encre/decimer_couches.py --couches data/couches/frag1_54keV \\
        --labels data/frag1/labels_fenetre.png --facteur 2 \\
        --top 3440 --left 2336 --cote 1024 --sortie data/couches/frag1_54keV_d2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]


def decimer_moyenne(a: np.ndarray, facteur: int) -> np.ndarray:
    """Une couche décimée par moyenne de blocs, dans son type d'origine.

    ⚠ Le type est conservé : le modèle est normalisé par le plafond du TYPE, et rendre du
    `float` ici ferait diviser par un plafond qui n'existe pas. C'est la panne de `60` sous
    un autre costume.
    """
    if facteur < 1:
        raise ValueError("le facteur doit valoir au moins 1")
    if facteur == 1:
        return a
    h, w = a.shape[0] // facteur * facteur, a.shape[1] // facteur * facteur
    bloc = a[:h, :w].reshape(h // facteur, facteur, w // facteur, facteur)
    return bloc.mean(axis=(1, 3)).astype(a.dtype)


def decimer_majorite(labels: np.ndarray, facteur: int) -> np.ndarray:
    """Des étiquettes binaires décimées par MAJORITÉ, jamais par échantillonnage.

    ⚠⚠ Prendre un pixel sur `facteur` perdrait les traits fins, donc appauvrirait la vérité
    terrain et abaisserait l'AUC pour une raison qui n'a rien à voir avec le modèle. La
    majorité garde la part d'encre de chaque bloc.
    """
    if facteur < 1:
        raise ValueError("le facteur doit valoir au moins 1")
    binaire = labels > 0
    if facteur == 1:
        return (binaire * 255).astype(np.uint8)
    h, w = binaire.shape[0] // facteur * facteur, binaire.shape[1] // facteur * facteur
    bloc = binaire[:h, :w].reshape(h // facteur, facteur, w // facteur, facteur)
    return ((bloc.mean(axis=(1, 3)) >= 0.5) * 255).astype(np.uint8)


def verifier() -> int:
    """Auto-test HORS LIGNE : les deux décimations et leurs différences."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LA COUCHE ------------------------------------------------------------------------
    a = np.array([[0, 100], [100, 200]], dtype=np.uint8)
    v("un bloc 2x2 devient sa moyenne", int(decimer_moyenne(a, 2)[0, 0]) == 100)
    v("le TYPE est conserve", decimer_moyenne(a, 2).dtype == np.uint8)
    v("un facteur 1 ne touche a rien", decimer_moyenne(a, 1) is a)
    v("la forme est divisee", decimer_moyenne(np.zeros((10, 10), np.uint8), 2).shape == (5, 5))
    # ⚠ Une dimension non multiple est ROGNEE, pas completee : completer inventerait du
    # papyrus au bord.
    v("une dimension impaire est rognee",
      decimer_moyenne(np.zeros((7, 7), np.uint8), 2).shape == (3, 3))
    try:
        decimer_moyenne(a, 0)
        v("un facteur nul est refuse", False)
    except ValueError:
        v("un facteur nul est refuse", True)

    # --- LES ETIQUETTES : majorite, pas echantillonnage --------------------------------
    # ⚠⚠ LE CONTROLE QUI COMPTE : un trait fin d'un pixel de large survit a la majorite
    # quand il remplit la moitie du bloc, et un echantillonnage le perdrait une fois sur deux.
    lab = np.zeros((4, 4), dtype=np.uint8)
    lab[:, 0:2] = 255                      # un trait de deux pixels de large
    d = decimer_majorite(lab, 2)
    v("un trait qui remplit la moitie du bloc survit", int(d[0, 0]) == 255)
    v("... et le vide reste vide", int(d[0, 1]) == 0)
    # ⚠⚠ Le seuil est INCLUSIF (`>= 0.5`), et c'est un choix qui protege la classe
    # minoritaire : un trait d'un pixel dans un bloc 2x2 remplit EXACTEMENT la moitie, et il
    # survit. Mon premier attendu disait qu'il disparaissait, et c'est moi qui avais tort.
    maigre = np.zeros((4, 4), dtype=np.uint8)
    maigre[:, 0] = 255                     # un trait d'UN pixel : la MOITIE d'un bloc 2x2
    v("un trait a exactement la moitie survit — le seuil est inclusif",
      int(decimer_majorite(maigre, 2)[0, 0]) == 255)
    # ⚠ En dessous de la moitie il disparait, et c'est une PERTE assumee : la majorite est
    # le moins mauvais choix, pas un choix neutre.
    tres_maigre = np.zeros((6, 6), dtype=np.uint8)
    tres_maigre[:, 0] = 255                # un pixel sur trois de large : un tiers du bloc
    v("... et en dessous de la moitie il disparait",
      int(decimer_majorite(tres_maigre, 3)[0, 0]) == 0)
    # ⚠ Et c'est une PERTE assumee : la majorite est le moins mauvais choix, pas un choix
    # neutre. L'echantillonnage, lui, perdrait ce meme trait UNE FOIS SUR DEUX selon la
    # phase, ce qui rendrait la mesure dependante d'un decalage d'un pixel.
    v("l'echantillonnage, lui, dependrait de la phase",
      int(maigre[::2, ::2][0, 0]) != int(maigre[::2, 1::2][0, 0]))
    v("les etiquettes restent binaires",
      set(np.unique(decimer_majorite(lab, 2)).tolist()) <= {0, 255})
    v("un facteur 1 rend les memes etiquettes, en binaire propre",
      set(np.unique(decimer_majorite(lab, 1)).tolist()) == {0, 255})

    # --- LES DEUX ENSEMBLE ----------------------------------------------------------------
    # ⚠⚠ Couches et etiquettes doivent sortir a la MEME forme, sinon `evaluate_segment`
    # refuse -- correctement -- et on croirait a un defaut de modele.
    couche = np.zeros((100, 100), dtype=np.uint8)
    etiq = np.zeros((100, 100), dtype=np.uint8)
    v("couches et etiquettes gardent la meme forme",
      decimer_moyenne(couche, 3).shape == decimer_majorite(etiq, 3).shape)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--couches", type=Path)
    ap.add_argument("--labels", type=Path)
    ap.add_argument("--facteur", type=int, default=2)
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--left", type=int, default=0)
    ap.add_argument("--cote", type=int, default=1024)
    ap.add_argument("--sortie", type=Path)
    ap.add_argument("--labels-sortie", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not (a.couches and a.sortie):
        ap.error("donner --couches et --sortie, ou --verifier")

    import tifffile
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None

    a.sortie.mkdir(parents=True, exist_ok=True)
    fichiers = sorted(a.couches.glob("*.tif"))
    for f in fichiers:
        brut = tifffile.imread(str(f))[a.top:a.top + a.cote, a.left:a.left + a.cote]
        tifffile.imwrite(str(a.sortie / f.name), decimer_moyenne(brut, a.facteur))
    print(f"  {len(fichiers)} couches décimées ×{a.facteur} → {a.sortie}")

    if a.labels:
        cible = a.labels_sortie or a.sortie.parent / f"{a.sortie.name}_labels.png"
        lab = np.array(Image.open(a.labels).convert("L"))
        Image.fromarray(decimer_majorite(lab, a.facteur)).save(cible)
        print(f"  étiquettes décimées par MAJORITÉ → {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
