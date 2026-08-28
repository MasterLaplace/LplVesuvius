#!/usr/bin/env python3
"""Le jeu d'images en aveugle que le protocole de `09` réclame, et sa clé à part.

⚠⚠ Pourquoi ce fichier existe. [`29`](../../docs/29_ce_qui_reste.md) M1ter nomme son prochain
pas : *« répondre n'est pas lire : il faut une fenêtre large et le juge calibré de `09` »*. Ce
juge est un **modèle de langue**, et [`09`](../../docs/09_juger_un_rendu.md) pose un protocole
en trois familles mélangées — témoin positif dont le texte est publié, témoin négatif sans
encre, inconnu — sans dire au juge laquelle est laquelle.

⭐⭐ Les trois familles existent enfin **toutes les trois**, et la dernière est arrivée le
2026-08-28 : le témoin négatif de 5128 × 5128 rendu sur une trace à α = +1,01, dont
[`38`](../../docs/38_ce_qui_bouge_avec_la_fenetre.md) prouve géométriquement qu'aucune feuille
n'est à portée. Avant lui, le protocole de `09` n'était pas exécutable : il lui manquait sa
famille la plus importante, celle que son propre texte appelle « le plus important ».

⚠⚠⚠ CE FICHIER NE JUGE PAS, ET CELUI QUI L'A ÉCRIT NE PEUT PAS JUGER. `09` pose une règle
irréversible : *« une fois qu'un modèle a vu une image non calibrée dans un fil, on ne peut
plus mesurer son taux d'invention sans biais »*. La session qui a produit les cartes de
`PHerc1447` les a regardées. Elle est disqualifiée comme juge par la règle même du protocole,
et le dire est plus utile que de produire un avis qui ne vaudrait rien.

⚠⚠ L'ÉTIREMENT EST COMMUN À TOUTES LES TUILES, et ce n'est pas une élégance. Étirer chaque
tuile sur sa propre plage rendrait une tuile de témoin négatif aussi contrastée qu'une tuile
de texte — le juge trancherait alors sur une normalisation et non sur une image. C'est la
règle que `figure_echelle.py` porte déjà, appliquée ici où elle décide d'un protocole.

⚠ La clé part dans un fichier SÉPARÉ, jamais dans les noms de tuiles ni dans un coin d'image.
Un jeu dont la clé voyage avec lui n'est pas un jeu en aveugle.

Usage :
    uv run python src/encre/jeu_du_juge.py --verifier
    uv run python src/encre/jeu_du_juge.py \\
        --positif data/out/ink_segment_complet.npy \\
        --negatif data/temoin_negatif/en_travers_grand.npy \\
        --inconnu data/out/ink_2025*.npy \\
        --sortie data/jeu_du_juge --graine 20260828
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

SENTINELLE = -9e9
"""Valeur au-dessous de laquelle un pixel est « non couvert », comme dans les figures."""

COTE_TUILE = 512
"""Côté d'une tuile, en pixels de carte. ⚠ Assez large pour porter plusieurs lignes
d'écriture — `09` insiste sur la fenêtre large — et assez petit pour qu'une carte en donne
plusieurs, sans quoi le jeu n'aurait pas de quoi être mélangé."""

PART_COUVERTE_MINIMALE = 0.8
"""Part de pixels couverts qu'une tuile doit porter. ⚠ Une tuile à moitié vide se reconnaît
à sa forme et non à son contenu : elle donnerait au juge un indice qui n'est pas de l'encre."""


def tuiles_de(carte: np.ndarray, cote: int = COTE_TUILE,
              part_min: float = PART_COUVERTE_MINIMALE) -> list[tuple[int, int]]:
    """Les origines des tuiles assez couvertes, en balayage sans recouvrement."""
    valide = np.isfinite(carte) & (carte > SENTINELLE)
    h, w = carte.shape
    out = []
    for y in range(0, h - cote + 1, cote):
        for x in range(0, w - cote + 1, cote):
            if float(valide[y:y + cote, x:x + cote].mean()) >= part_min:
                out.append((y, x))
    return out


def etendue_commune(cartes: list[np.ndarray]) -> tuple[float, float]:
    """Les percentiles 2 et 98 de TOUTES les cartes ensemble.

    ⚠⚠ De toutes ensemble, jamais de chacune : c'est ce qui empêche le juge de trancher sur
    une normalisation. Une tuile sans encre étirée sur sa propre plage est aussi contrastée
    qu'une tuile de texte, et le protocole s'effondrerait sans que rien ne le signale.
    """
    morceaux = []
    for c in cartes:
        m = np.isfinite(c) & (c > SENTINELLE)
        if m.any():
            morceaux.append(c[m].ravel())
    if not morceaux:
        raise ValueError("aucune carte ne porte de pixel couvert")
    tout = np.concatenate(morceaux)
    lo, hi = np.percentile(tout, [2, 98])
    return float(lo), float(hi)


def rendre_tuile(carte: np.ndarray, y: int, x: int, cote: int,
                 lo: float, hi: float) -> np.ndarray:
    """Une tuile en niveaux de gris, étirée sur la plage COMMUNE."""
    bloc = carte[y:y + cote, x:x + cote]
    m = np.isfinite(bloc) & (bloc > SENTINELLE)
    img = np.clip((bloc - lo) / max(hi - lo, 1e-9), 0.0, 1.0)
    img[~m] = 0.0
    return (img * 255).astype(np.uint8)


def nom_aveugle(index: int, graine: int) -> str:
    """Un nom qui ne dit rien de la famille, et qui est reproductible depuis la graine.

    ⚠ Un compteur nu (`tuile_00`, `tuile_01`) trahirait l'ordre de génération, donc les
    familles, puisqu'elles sont produites l'une après l'autre. Le nom est un condensé de la
    graine et de l'index, ce qui le rend à la fois opaque et rejouable.
    """
    h = hashlib.sha256(f"{graine}:{index}".encode()).hexdigest()
    return f"tuile_{h[:10]}"


def melanger(n: int, graine: int) -> list[int]:
    """Une permutation reproductible de `n` éléments."""
    ordre = list(range(n))
    np.random.default_rng(graine).shuffle(ordre)
    return [int(i) for i in ordre]


def batir(familles: dict, sortie: Path, cote: int, graine: int,
          par_famille: int) -> dict:
    """Écrit les tuiles mélangées et la clé, et rend le relevé.

    `familles` associe un rôle (`positif`, `negatif`, `inconnu`) à une liste de cartes.
    """
    from PIL import Image

    toutes = [c for lot in familles.values() for c in lot]
    lo, hi = etendue_commune(toutes)
    choisies = []
    for role, cartes in familles.items():
        prises = 0
        for i, carte in enumerate(cartes):
            for (y, x) in tuiles_de(carte, cote):
                if prises >= par_famille:
                    break
                choisies.append({"role": role, "carte": i, "y": y, "x": x,
                                 "image": rendre_tuile(carte, y, x, cote, lo, hi)})
                prises += 1
            if prises >= par_famille:
                break
    ordre = melanger(len(choisies), graine)
    sortie.mkdir(parents=True, exist_ok=True)
    cle = []
    for rang, source in enumerate(ordre):
        t = choisies[source]
        nom = nom_aveugle(rang, graine)
        Image.fromarray(t["image"], "L").save(sortie / f"{nom}.png")
        cle.append({"nom": nom, "role": t["role"], "carte": t["carte"],
                    "y": t["y"], "x": t["x"]})
    return {"graine": graine, "cote": cote, "etendue_commune": [lo, hi],
            "par_famille": par_famille,
            "compte": {r: sum(1 for k in cle if k["role"] == r) for r in familles},
            "cle": cle}


def verifier() -> int:
    """Auto-test HORS LIGNE : le découpage, l'étirement commun, l'aveugle."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LE DECOUPAGE -------------------------------------------------------------------
    pleine = np.zeros((1024, 1024), dtype=np.float32)
    v("une carte pleine rend quatre tuiles de 512", len(tuiles_de(pleine, 512)) == 4)
    trouee = np.full((1024, 1024), np.nan, dtype=np.float32)
    trouee[:512, :512] = 0.0
    v("une tuile a moitie vide est ecartee", len(tuiles_de(trouee, 512)) == 1)
    v("une carte plus petite qu'une tuile n'en rend aucune",
      len(tuiles_de(np.zeros((100, 100), dtype=np.float32), 512)) == 0)

    # --- L'ETIREMENT COMMUN, la propriete qui porte le protocole -----------------------
    faible = np.full((64, 64), 0.0, dtype=np.float32)
    faible[0, 0] = 0.01
    forte = np.linspace(-2, 2, 64 * 64, dtype=np.float32).reshape(64, 64)
    lo, hi = etendue_commune([faible, forte])
    # ⚠⚠ Le controle qui compte : la tuile FAIBLE doit rester faible, donc son etendue
    # rendue doit etre bien plus petite que celle de la forte.
    tf = rendre_tuile(faible, 0, 0, 64, lo, hi)
    tF = rendre_tuile(forte, 0, 0, 64, lo, hi)
    v("l'etendue commune vient des DEUX cartes", lo < -1.0 and hi > 1.0)
    v("la carte faible reste faible sous l'etendue commune",
      int(tf.max()) - int(tf.min()) < int(tF.max()) - int(tF.min()))
    # ⚠ Et le controle NEGATIF : etiree sur SA propre plage, la faible deviendrait aussi
    # contrastee que la forte. C'est exactement le piege que l'etendue commune evite.
    lo2, hi2 = etendue_commune([faible])
    seule = rendre_tuile(faible, 0, 0, 64, lo2, hi2)
    v("... alors qu'etiree seule elle deviendrait aussi contrastee",
      int(seule.max()) - int(seule.min()) > int(tf.max()) - int(tf.min()))
    try:
        etendue_commune([np.full((4, 4), np.nan, dtype=np.float32)])
        v("une carte sans pixel couvert est refusee", False)
    except ValueError:
        v("une carte sans pixel couvert est refusee", True)

    # --- L'AVEUGLE -----------------------------------------------------------------------
    v("deux index donnent deux noms", nom_aveugle(0, 1) != nom_aveugle(1, 1))
    v("deux graines donnent deux noms", nom_aveugle(0, 1) != nom_aveugle(0, 2))
    v("le nom est reproductible", nom_aveugle(3, 7) == nom_aveugle(3, 7))
    # ⚠⚠⚠ LA propriete d'aveugle, et c'est la seule qui compte : trier les noms de fichiers
    # ne doit PAS rendre l'ordre de generation. Un compteur nu (`tuile_00`, `tuile_01`) le
    # rendrait exactement, donc les familles, puisqu'elles sont produites l'une apres
    # l'autre. Ma premiere version de ce controle etait un `... or True` : elle ne pouvait
    # pas echouer, ce qui est la panne du document 61 ecrite une troisieme fois.
    noms = [nom_aveugle(i, 11) for i in range(24)]
    v("trier les noms ne rend pas l'ordre de generation", sorted(noms) != noms)
    v("... ni son inverse", sorted(noms, reverse=True) != noms)
    v("les noms sont tous distincts", len(set(noms)) == len(noms))
    v("ils ont tous la meme longueur, donc aucun ne se distingue par sa forme",
      len({len(n) for n in noms}) == 1)
    # ⚠ Le controle NEGATIF : un compteur nu, lui, echoue au premier test.
    compteur = [f"tuile_{i:02d}" for i in range(24)]
    v("... alors qu'un compteur nu trahirait l'ordre", sorted(compteur) == compteur)
    v("le melange est reproductible", melanger(20, 4) == melanger(20, 4))
    v("... et il melange vraiment", melanger(20, 4) != list(range(20)))
    v("le melange est une permutation", sorted(melanger(20, 4)) == list(range(20)))

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--positif", type=Path, nargs="*", default=[])
    ap.add_argument("--negatif", type=Path, nargs="*", default=[])
    ap.add_argument("--inconnu", type=Path, nargs="*", default=[])
    ap.add_argument("--sortie", type=Path, default=RACINE / "data/jeu_du_juge")
    ap.add_argument("--cle", type=Path,
                    help="où écrire la clé (défaut : à CÔTÉ du jeu, jamais dedans)")
    ap.add_argument("--cote", type=int, default=COTE_TUILE)
    ap.add_argument("--par-famille", type=int, default=6)
    ap.add_argument("--graine", type=int, default=20260828)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not (a.positif and a.negatif and a.inconnu):
        ap.error("les TROIS familles sont requises : un jeu sans témoin négatif ne calibre "
                 "rien, et `09` dit que c'est la famille la plus importante")

    familles = {"positif": [np.load(p) for p in a.positif],
                "negatif": [np.load(p) for p in a.negatif],
                "inconnu": [np.load(p) for p in a.inconnu]}
    releve = batir(familles, a.sortie, a.cote, a.graine, a.par_famille)
    # ⚠ La clé va À CÔTÉ du jeu, pas dedans : un dossier qu'on transmet ne doit pas porter
    # sa propre réponse.
    cle = a.cle or a.sortie.parent / f"{a.sortie.name}_cle.json"
    cle.parent.mkdir(parents=True, exist_ok=True)
    cle.write_text(json.dumps(releve, indent=2, ensure_ascii=False) + "\n")
    print(f"  jeu   : {a.sortie}  ({sum(releve['compte'].values())} tuiles de {a.cote} px)")
    for r, n in releve["compte"].items():
        print(f"    {r:9s} {n}")
    print(f"  clé   : {cle}  ⚠ à ne PAS transmettre avec le jeu")
    print(f"  plage commune : {releve['etendue_commune'][0]:.3f} … "
          f"{releve['etendue_commune'][1]:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
