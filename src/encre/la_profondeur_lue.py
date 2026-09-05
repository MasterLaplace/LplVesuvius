#!/usr/bin/env python3
"""À quelle PROFONDEUR PHYSIQUE le détecteur lit-il, et est-ce celle qu'il a apprise ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UN NOMBRE, PAS UNE INTUITION. Le modèle GP-2023 lit
**26 couches**. Ce qui compte n'est pas ce compte mais l'**épaisseur** qu'il couvre, et elle est
le produit du compte par la taille de voxel :

| pile | taille de voxel | 26 couches couvrent |
|---|---:|---:|
| Scroll 1 `20230909121925` — où le modèle marche, AUC 0,925 | 7,91 µm | **206 µm** |
| segments officiels de `PHerc1447` | 8,64 µm | 225 µm |
| **volumes de surface de `PHerc0139`** | **2,399 µm** | **62 µm** |

⚠⚠⚠ **62 µm, c'est moins qu'une épaisseur de feuille** (~100 µm). Sur ces volumes le détecteur
ne voit donc pas « une feuille et ses voisines » comme à l'entraînement : il voit une tranche
*intérieure* à une feuille. Toute inférence de ce dépôt sur un volume de surface à 2,4 µm a lu
cette tranche-là, et rien ne le disait — `infer_ink.py` portait même le contraire, en
répétant les « 62 µm à l'entraînement » que `36` §5bis a déclarés faux le 2026-08-27.

⭐⭐ CE QUI REND LA QUESTION MESURABLE : `load_layer_stack` prend depuis longtemps un pas de
profondeur qui **épaissit la fenêtre sans changer le nombre d'images** — une couche sur `pas`.
Il n'avait aucun drapeau, donc personne ne pouvait s'en servir. À `pas = 3` les 26 couches
couvrent **187 µm**, soit le régime d'entraînement à 9 % près.

⚠⚠ CE QUE CE FICHIER MESURE ET CE QU'IL NE MESURE PAS. Il mesure ce que le détecteur **rend**
quand on change une seule chose — la profondeur lue. Il ne mesure PAS la présence d'encre : il
n'y a pas de vérité terrain ici. Un écart-type qui monte dit « le modèle cesse de rendre une
constante », pas « il lit du texte ». `36` §5bis donne l'étalon absolu : σ **0,7712** sur la
pile où le modèle marche, σ **0,0171** là où il est muet — un facteur **45**.

⚠ Et la fenêtre est la même à tous les pas, au même début : c'est ce qui en fait une
comparaison appariée. Un pas plus grand lit plus loin **vers le bas** de la pile, donc la
fenêtre n'est plus centrée pareil — ce biais est nommé et borné ci-dessous (`debut_pour`),
jamais laissé implicite.

Usage :
    uv run python src/encre/la_profondeur_lue.py --verifier
    uv run python src/encre/la_profondeur_lue.py --segment 20260325000000-w046_20260325 \\
        --json docs/mesures/la_profondeur_lue.json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from le_nul_verso import (  # noqa: E402
    COUCHES_LUES, EXTRACTEUR, SURFACE_DANS_LA_FENETRE, _inference, _lancer,
    chercher_fenetre, fenetres, prendre_le_verrou, profil_de_profondeur,
)

RACINE = Path(__file__).resolve().parents[2]
CARTES = RACINE / "docs" / "mesures" / "profondeur_lue_cartes"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "la_profondeur_lue.json"

VOXEL_UM = 2.399
"""Taille de voxel des surface-volumes de `PHerc0139` (`73` §0, clef du volume)."""

VOXEL_ENTRAINEMENT_UM = 7.91
"""Celle de la pile où le modèle atteint 0,925 — `36` §5bis, **corrigé le 2026-08-27**.

⚠ La valeur 2,4 µm qu'on lit encore ici ou là est la ligne que ce document déclare fausse :
elle vient de la campagne ESRF, qui rend des *volumes de surface*, pas la pile de Scroll 1."""

SIGMA_MODELE_VIVANT = 0.7712
"""σ mesuré là où le modèle marche (`36` §5bis)."""

SIGMA_MODELE_MUET = 0.0171
"""σ mesuré là où il rend une constante (`36` §5bis) — 45 fois plus petit."""

PAS = (1, 2, 3)
"""Les pas mesurés.

⚠ 1 est le régime **actuel** de tout ce dépôt, 3 le régime d'**entraînement** à 9 % près, et 2
existe pour que la réponse soit une **tendance** et pas un couple : deux points ne distinguent
pas un effet d'un accident, trois disent au moins si c'est monotone."""


def profondeur_um(pas: int, voxel_um: float = VOXEL_UM) -> float:
    """
    @brief L'épaisseur réellement lue par les 26 couches, en micromètres.

    ⚠ `(26 - 1) * pas + 1` couches de SOURCE sont traversées, pas `26 * pas` : la première et
    la dernière sont lues, les intervalles sont 25. Compter 26 surestime d'un pas entier, ce
    qui à pas 3 fait 7 µm annoncés en trop.
    """
    return ((COUCHES_LUES - 1) * pas + 1) * voxel_um


def debut_pour(pic: int, pas: int, couches: int) -> int:
    """
    @brief Le début de fenêtre qui garde la surface à la MÊME place, en micromètres.

    ⚠⚠ `SURFACE_DANS_LA_FENETRE` compte des **images du modèle**, pas des couches de source :
    à pas 3, la 17ᵉ image est la couche `debut + 51`. Reprendre l'offset tel quel décalerait la
    surface de 34 couches, soit 82 µm, et on mesurerait un décentrage en croyant mesurer une
    profondeur.

    ⚠ Bornée à la pile : au-delà, `load_layer_stack` refuse sur une couche absente. Le
    rognage est **rendu** à l'appelant par la valeur elle-même, qui n'est alors plus centrée —
    d'où `centre_perdu` dans la mesure.
    """
    etendue = (COUCHES_LUES - 1) * pas
    return max(0, min(couches - 1 - etendue, pic - SURFACE_DANS_LA_FENETRE * pas))


def resume_carte(chemin: Path) -> dict:
    """
    @brief Ce qu'une carte de prédiction dit d'elle-même : σ, étendue, médiane.

    ⚠⚠ σ EST LA GRANDEUR PRINCIPALE ici et pas la médiane, parce que la panne connue de ce
    modèle hors domaine est de rendre une **constante** (`36` §5bis, `60`). Une médiane basse
    est compatible avec une carte riche ; un σ effondré ne l'est pas.
    """
    a = np.load(chemin)
    bons = a[np.isfinite(a)]
    if bons.size == 0:
        return {}
    return dict(sigma=float(bons.std()), mediane=float(np.median(bons)),
                minimum=float(bons.min()), maximum=float(bons.max()),
                etendue=float(bons.max() - bons.min()), pixels=int(bons.size))


def mesurer(segment: str, zarr: str, top: int, left: int, taille: int = 512,
            pas_mesures: tuple[int, ...] = PAS) -> dict:
    """
    @brief La même fenêtre, lue à plusieurs profondeurs — une seule chose change.

    ⚠ L'extraction est faite UNE fois et les inférences tournent sur la même pile de couches :
    ré-extraire par pas ferait varier le téléchargement en même temps que la profondeur.
    """
    with tempfile.TemporaryDirectory() as tmp:
        couches = Path(tmp) / "couches"
        code, texte = _lancer(
            ["uv", "run", "python", str(EXTRACTEUR), zarr, "--sortie", str(couches),
             "--top", str(top), "--left", str(left),
             "--hauteur", str(taille), "--largeur", str(taille)], 3600)
        if code != 0:
            raise SystemExit(f"extraction échouée : {texte.strip()[-200:]}")
        profil = profil_de_profondeur(couches, taille)
        if not profil:
            raise SystemExit("profil de profondeur illisible")
        f = fenetres(profil)
        if not f or not f["pic_central"]:
            raise SystemExit(
                "pic d'intensité hors de la moitié centrale : cette fenêtre ne tombe pas sur "
                "la feuille tracée, et comparer des profondeurs y comparerait des voisines")
        n = f["couches"]
        CARTES.mkdir(parents=True, exist_ok=True)
        lots = []
        for pas in pas_mesures:
            debut = debut_pour(f["pic"], pas, n)
            atteint = debut + (COUCHES_LUES - 1) * pas
            sortie = CARTES / f"{segment}_pas{pas}.npy"
            r = _inference(couches, debut, taille, sortie, pas=pas)
            lot = dict(pas=pas, debut=debut, derniere_couche=atteint,
                       profondeur_um=profondeur_um(pas),
                       # ⚠ « La surface est-elle restée au centre ? » — à grand pas la fenêtre
                       # bute sur la pile et se décale. Dit, jamais deviné.
                       centre_perdu=int(abs((f["pic"] - debut) // max(1, pas)
                                            - SURFACE_DANS_LA_FENETRE)),
                       echec=(r or {}).get("echec"))
            if not lot["echec"]:
                lot.update(resume_carte(sortie))
            lots.append(lot)
    return dict(segment=segment, zarr=zarr, top=top, left=left, taille=taille,
                voxel_um=VOXEL_UM, pic=f["pic"], couches=n,
                profil=profil["contraste"], profil_intensite=profil["moyenne"], lots=lots)


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE NOMBRE QUI JUSTIFIE TOUT LE FICHIER, vérifié plutôt que répété : à 2,399 µm la
    # fenêtre du modèle est TROIS FOIS plus mince que ce qu'il a appris à lire.
    v("à 2,399 µm, 26 couches ne couvrent que 62 µm",
      abs(profondeur_um(1) - 60.0) < 3.0, f"{profondeur_um(1):.1f} µm")
    v("... alors que l'entraînement en voit 206",
      abs(profondeur_um(1, VOXEL_ENTRAINEMENT_UM) - 198.0) < 10.0,
      f"{profondeur_um(1, VOXEL_ENTRAINEMENT_UM):.1f} µm")
    v("... soit un facteur trois et demi",
      3.0 < profondeur_um(1, VOXEL_ENTRAINEMENT_UM) / profondeur_um(1) < 3.6,
      f"{profondeur_um(1, VOXEL_ENTRAINEMENT_UM) / profondeur_um(1):.2f}")
    v("le pas 3 ramène la fenêtre dans le régime d'entraînement",
      abs(profondeur_um(3) - profondeur_um(1, VOXEL_ENTRAINEMENT_UM)) < 25.0,
      f"{profondeur_um(3):.1f} contre {profondeur_um(1, VOXEL_ENTRAINEMENT_UM):.1f} µm")
    # ⚠ 25 intervalles et non 26 : compter 26 surestime d'un pas entier.
    v("l'épaisseur compte 25 intervalles, pas 26",
      profondeur_um(2) < 26 * 2 * VOXEL_UM, f"{profondeur_um(2):.1f} µm")

    # ⚠⚠⚠ L'OFFSET DE SURFACE EST EN IMAGES DU MODÈLE, PAS EN COUCHES. Sans cette conversion
    # la fenêtre à pas 3 serait décalée de 34 couches — on mesurerait un décentrage en croyant
    # mesurer une profondeur, et l'effet ressemblerait à celui qu'on cherche.
    v("à pas 1 la surface est à la 17ᵉ image", debut_pour(52, 1, 109) == 52 - 17)
    v("... et à pas 3 aussi, donc le début recule de 51 couches",
      debut_pour(60, 3, 109) == 60 - 51, str(debut_pour(60, 3, 109)))
    v("... jamais avant le début de la pile", debut_pour(10, 3, 109) == 0)
    v("... ni au-delà de sa fin",
      debut_pour(105, 3, 109) + (COUCHES_LUES - 1) * 3 <= 108,
      f"début {debut_pour(105, 3, 109)}")
    # ⚠ Un pas trop grand pour la pile est BORNÉ, pas refusé en silence : la mesure le dit par
    # `centre_perdu`, sinon un run rognant sa fenêtre passerait pour un run centré.
    v("une pile trop courte pour le pas donne un début nul, donc un centre perdu",
      debut_pour(52, 5, 109) == 0 and abs(52 // 5 - SURFACE_DANS_LA_FENETRE) > 5,
      f"début {debut_pour(52, 5, 109)}")

    if r:
        print("\net la mesure")
        lots = [x for x in r["lots"] if not x.get("echec")]
        v("chaque pas a rendu une carte", len(lots) == len(r["lots"]),
          f"{len(lots)} sur {len(r['lots'])}")
        if len(lots) >= 2:
            for x in lots:
                print(f"      pas {x['pas']} — {x['profondeur_um']:6.1f} µm, "
                      f"couches {x['debut']}..{x['derniere_couche']}, "
                      f"σ {x['sigma']:.4f}, médiane {x['mediane']:+.3f}, "
                      f"étendue {x['etendue']:.3f}, centre perdu {x['centre_perdu']}")
            # ⚠⚠⚠ ÉCRIT POUR TOMBER DANS LES DEUX SENS, et les deux sont publiables. Si σ
            # monte franchement avec la profondeur, la fenêtre trop mince explique une part de
            # ce que ce dépôt attribuait au rouleau ou à la trace. S'il ne bouge pas, la
            # profondeur est innocentée et l'axe est clos — ce qui vaut d'être écrit aussi.
            sigmas = [x["sigma"] for x in lots]
            v("le détecteur ne rend une CONSTANTE à aucun pas",
              min(sigmas) > SIGMA_MODELE_MUET * 3,
              " · ".join(f"{s:.4f}" for s in sigmas))
            v("... et la fenêtre reste centrée sur la surface à tous les pas",
              all(x["centre_perdu"] <= 1 for x in lots),
              " · ".join(str(x["centre_perdu"]) for x in lots))
            ecart = (max(sigmas) - min(sigmas)) / max(1e-9, min(sigmas))
            print(f"\n      σ : {min(sigmas):.4f} → {max(sigmas):.4f}  "
                  f"({100 * ecart:.0f} % d'écart ; étalon vivant {SIGMA_MODELE_VIVANT}, "
                  f"muet {SIGMA_MODELE_MUET})")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--segment", default="20260325000000-w046_20260325")
    p.add_argument("--zarr", default=None)
    p.add_argument("--top", type=int, default=21504)
    p.add_argument("--left", type=int, default=5120)
    p.add_argument("--taille", type=int, default=512)
    p.add_argument("--chercher", action="store_true")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.verifier and not a.json:
        cible = DEFAUT_JSON
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0

    zarr = a.zarr or (f"PHerc0139/segments/{a.segment}/surface-volumes/"
                      "2.399um-0.22m-78keV-volume-20260102150214.zarr")
    top, left = a.top, a.left
    if a.chercher:
        f = chercher_fenetre(zarr, a.taille)
        top, left = f["top"], f["left"]
        print(f"  fenêtre trouvée : top {top}, left {left} "
              f"({100 * f['part_matiere']:.0f} % de matière)")
    _verrou = prendre_le_verrou()  # noqa: F841 — relâché à la mort du processus
    r = mesurer(a.segment, zarr, top, left, a.taille)
    print(f"{r['segment']} — pile de {r['couches']} couches, pic d'intensité à {r['pic']}")
    for x in r["lots"]:
        if x.get("echec"):
            print(f"  pas {x['pas']} ÉCHEC — {x['echec']}", file=sys.stderr)
        else:
            print(f"  pas {x['pas']}  {x['profondeur_um']:6.1f} µm  "
                  f"couches {x['debut']}..{x['derniere_couche']}  "
                  f"σ {x['sigma']:.4f}  méd {x['mediane']:+.3f}  ét {x['etendue']:.3f}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
