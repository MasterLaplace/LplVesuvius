#!/usr/bin/env python3
"""L'axe d'un rouleau n'est pas une droite — et l'invariant y survit quand même.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UNE PRÉMISSE FAUSSE CORRIGÉE.
`sensibilite_centre.py` s'ouvre sur deux faits censés remplacer la question de `06` §2.3, et
le premier est faux :

    « ⚠ **`umbilicus.txt` n'existe pas.** Vérifié sur le bucket ouvert, préfixe par préfixe :
      zéro occurrence du mot pour PHercParis4, PHerc0139, PHerc1667 et Scroll1. Le fichier
      noté dans `06` n'est pas à une autre adresse — il n'est pas publié. »

Il **est** publié. La vérification portait sur le bucket S3 `vesuvius-challenge-open-data` ;
l'ombilic vit sur **`dl.ash2txt.org`**, l'autre serveur du concours, et
`spiral-fitting/scroll1_umbilicus.py` en donne l'adresse en commentaire depuis toujours.
Vérifié le 2026-09-03 : **HTTP 200, 241 points** `z, y, x`.

⚠ C'est le même angle mort que `59` — chercher sur un seul des deux serveurs — commis une
seconde fois, sur un autre objet.

⭐⭐⭐ CE QUE LE FICHIER RÉCUPÉRÉ APPREND, ET QU'AUCUNE ANALYSE DE SENSIBILITÉ NE POUVAIT
DIRE. `radial.py` dérive **un** centre `(cx, cy)` par rouleau. L'ombilic publié dit que ce
modèle est faux : sur les 108 mm de hauteur de Scroll 1, l'axe **erre de 21,6 mm en y et de
10,0 mm en x**. Remplacer cette courbe par un point unique coûte une distance médiane de
**5,80 mm** et maximale de **16,75 mm**, soit **148 écarts inter-feuilles** à 113 µm.

**Un axe de rouleau n'est pas une droite. C'est une courbe, et elle est longue.**

⭐⭐ ET POURTANT LA CONCLUSION DE `sensibilite_centre.py` TIENT — c'est le second résultat, et
il est plus fort que le premier ne le laissait craindre. Ce fichier-là avait balayé des
décalages **constants** jusqu'à 6328 µm et mesuré que l'invariant rayon/feuilles bouge d'au
plus **1,85 %**. Or 6328 µm **encadre** la dérive médiane réelle de 5800 µm. Donc le centre
unique est défendable pour cet invariant — mais désormais **sur une mesure**, plus sur un
fichier qu'on croyait absent.

⚠⚠ CE QUE CE FICHIER N'ÉTABLIT PAS, et il faut le dire à chaque usage :

1. La dérive mesurée est celle de **Scroll 1**. Rien ici ne dit que les autres errent autant,
   ni aussi peu.

   ⚠⚠⚠ **CORRIGÉ le 2026-09-04 : ce n'est PAS le seul rouleau à publier un ombilic.** Cette
   ligne affirmait « le **seul** rouleau qui publie un ombilic — vérifié le même jour sur les
   cinq répertoires `umbilici/` de `dl.ash2txt.org` ». La vérification était juste et sa
   conclusion fausse : elle portait sur **un** serveur et **une** convention de chemin. Sur le
   bucket ouvert, l'axe vit sous `<rouleau>/representations/umbilicus/`, et **cinq** rouleaux
   en publient un (`PHerc0125`, `PHerc0139`, `PHerc0211`, `PHerc0332`, `PHerc0826`) — balayés
   sur les 46 préfixes de premier niveau par `lombilic_publie.py`, pas sur une liste écrite à
   la main.

   C'est l'angle mort de `59` — interroger une vue du corpus et conclure sur le corpus —
   commis ici pour la troisième fois, et sur le **même objet** que la deuxième.
2. Le balayage de `sensibilite_centre.py` déplace le centre d'un **offset constant**, alors
   que l'axe réel **dérive avec z**. Un offset constant translate la géométrie ; une dérive la
   cisaille. Les deux perturbations ne sont pas la même, et la robustesse mesurée sur la
   première ne se transporte à la seconde que parce que chaque tranche est mesurée séparément.
3. Notre seul centre dérivé est celui de `PHerc0172` (Scroll 5), qui **ne publie pas**
   d'ombilic. La comparaison directe « notre centre contre le leur » n'est donc pas montable ;
   ce fichier mesure la courbe publiée, pas notre erreur.

Usage :
    uv run python src/excision/laxe_nest_pas_une_ligne.py --verifier
    uv run python src/excision/laxe_nest_pas_une_ligne.py --json docs/mesures/laxe_nest_pas_une_ligne.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
OMBILIC = RACINE / "data" / "axes" / "umbilicus-scroll1a_zyx.txt"

URL = ("https://dl.ash2txt.org/full-scrolls/Scroll1/PHercParis4.volpkg/"
       "umbilici/umbilicus-scroll1a_zyx.txt")
"""L'adresse, écrite ici parce qu'un fichier de données sans son adresse est un fichier
qu'on ne peut pas rafraîchir. Elle vient de `spiral-fitting/scroll1_umbilicus.py:2`."""

VOXEL_UM = 7.91
"""Scroll 1 au niveau 0. ⚠ L'ombilic est publié en coordonnées de **voxel**, pas en microns :
sans cette conversion tout ce qui suit serait un nombre sans unité."""

ENTRE_FEUILLES_UM = 113.0
"""Écart médian centre à centre mesuré sur `PHerc1447` (`44`, repris dans l'article §2.1).
⚠ C'est une mesure faite sur un AUTRE rouleau : elle sert ici d'échelle de lecture, pas de
propriété de Scroll 1."""


def charger() -> np.ndarray:
    """
    @brief Les points publiés de l'ombilic, en (z, y, x) de voxel.
    """
    if not OMBILIC.is_file():
        raise SystemExit(
            f"ombilic absent : {OMBILIC}\n"
            f"  le récupérer :  curl -s '{URL}' -o {OMBILIC}")
    d = np.loadtxt(OMBILIC, delimiter=",")
    if d.ndim != 2 or d.shape[1] != 3:
        raise SystemExit(f"format inattendu : {d.shape}, attendu (n, 3) en z,y,x")
    return d


def mesurer() -> dict:
    """
    @brief Ce que coûte le modèle « un centre unique » contre la courbe publiée.
    """
    d = charger()
    z, y, x = d[:, 0], d[:, 1], d[:, 2]
    etendue = lambda a: float(a.max() - a.min())  # noqa: E731

    cx, cy = float(x.mean()), float(y.mean())
    r = np.hypot(x - cx, y - cy)

    return dict(
        source=URL,
        points=int(len(d)),
        hauteur_vx=etendue(z),
        hauteur_mm=etendue(z) * VOXEL_UM / 1000.0,
        errance_x_vx=etendue(x), errance_x_mm=etendue(x) * VOXEL_UM / 1000.0,
        errance_y_vx=etendue(y), errance_y_mm=etendue(y) * VOXEL_UM / 1000.0,
        centre_unique=dict(cx=cx, cy=cy),
        ecart_median_mm=float(np.median(r)) * VOXEL_UM / 1000.0,
        ecart_p90_mm=float(np.percentile(r, 90)) * VOXEL_UM / 1000.0,
        ecart_max_mm=float(r.max()) * VOXEL_UM / 1000.0,
        ecart_max_en_feuilles=float(r.max()) * VOXEL_UM / ENTRE_FEUILLES_UM,
        # ⚠ Le balayage auquel on se compare, relu depuis SON fichier de résultat plutôt que
        # recopié : un chiffre recopié est un chiffre qui peut se désaccorder de sa source.
        balayage=_balayage(),
    )


def _balayage() -> dict:
    """Le décalage maximal sondé par `sensibilite_centre.py`, et l'écart qu'il a produit."""
    f = RACINE / "docs" / "mesures" / "sensibilite_centre.json"
    if not f.is_file():
        return {}
    d = json.loads(f.read_text())
    m = d.get("mesures", [])
    if not m:
        return {}
    return dict(
        rouleau=d.get("centre"),
        decalage_max_um=max(x["decalage_um"] for x in m),
        ecart_max_pct=max(abs(x["ecart_pct"]) for x in m),
    )


def _verifier(r: dict) -> int:
    echecs = 0

    def v(intitule: str, cond: bool, detail: str = "") -> None:
        nonlocal echecs
        if not cond:
            echecs += 1
        print(f"  [{'ok  ' if cond else 'FAIL'}] {intitule}{(' — ' + detail) if detail else ''}")

    print("le fichier que l'on croyait absent")
    v("l'ombilic publié est là", r["points"] > 100, f"{r['points']} points")
    v("il couvre la hauteur d'un rouleau", r["hauteur_mm"] > 50,
      f"{r['hauteur_mm']:.1f} mm")

    print("l'axe n'est pas une droite")
    # ⚠⚠ LE CONTRÔLE QUI PORTE LE RÉSULTAT. Si l'errance était de l'ordre du bruit, un centre
    # unique serait le bon modèle et il n'y aurait rien à dire. Elle doit donc dépasser
    # largement l'écart entre deux feuilles, qui est la plus petite longueur qui compte ici.
    v("l'errance dépasse de loin l'écart entre deux feuilles",
      r["ecart_max_en_feuilles"] > 20,
      f"{r['ecart_max_mm']:.2f} mm = {r['ecart_max_en_feuilles']:.0f} entre-feuilles")
    v("... et elle est plus grande en y qu'en x sur ce rouleau",
      r["errance_y_mm"] > r["errance_x_mm"],
      f"{r['errance_y_mm']:.2f} mm contre {r['errance_x_mm']:.2f} mm")
    v("la médiane est du même ordre, donc ce n'est pas un point aberrant",
      r["ecart_median_mm"] > r["ecart_max_mm"] / 5,
      f"médiane {r['ecart_median_mm']:.2f} mm contre max {r['ecart_max_mm']:.2f} mm")

    print("et l'invariant y survit — le contre-contrôle")
    b = r.get("balayage", {})
    # ⚠ Sans ce contrôle, le fichier annoncerait une catastrophe qui n'a pas eu lieu. Le
    # balayage de `sensibilite_centre.py` a exploré des décalages qui ENCADRENT la dérive
    # médiane réelle, et l'invariant n'a pas bougé de 2 %.
    v("le balayage encadre la dérive médiane réelle",
      bool(b) and b["decalage_max_um"] >= r["ecart_median_mm"] * 1000.0,
      f"sondé jusqu'à {b.get('decalage_max_um', 0):.0f} µm contre une dérive médiane de "
      f"{r['ecart_median_mm'] * 1000.0:.0f} µm")
    v("... et l'invariant y bouge de moins de 2 %",
      bool(b) and b["ecart_max_pct"] < 2.0, f"{b.get('ecart_max_pct', 0):.2f} %")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print("  ALL PASS (0 failures, 7 checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer()

    if not args.verifier or args.json:
        print(f"ombilic publié de Scroll 1 : {r['points']} points sur "
              f"{r['hauteur_mm']:.1f} mm de hauteur")
        print(f"  errance en x : {r['errance_x_mm']:6.2f} mm")
        print(f"  errance en y : {r['errance_y_mm']:6.2f} mm")
        print(f"\nce que coûte de le remplacer par UN centre :")
        print(f"  médiane {r['ecart_median_mm']:6.2f} mm · p90 {r['ecart_p90_mm']:6.2f} mm · "
              f"max {r['ecart_max_mm']:6.2f} mm")
        print(f"  soit un maximum de {r['ecart_max_en_feuilles']:.0f} écarts inter-feuilles")
        b = r.get("balayage", {})
        if b:
            print(f"\nl'analyse de sensibilité de {b['rouleau']} a sondé jusqu'à "
                  f"{b['decalage_max_um']:.0f} µm")
            print(f"  et l'invariant y bouge d'au plus {b['ecart_max_pct']:.2f} % : il tient.")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")

    if args.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
