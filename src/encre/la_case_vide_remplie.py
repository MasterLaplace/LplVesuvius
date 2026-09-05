#!/usr/bin/env python3
"""Remplir une case vide du régime du prix, et la confronter à la carte publiée du même segment.

⚠⚠⚠ CE QUE `68` §4 ÉTABLIT ET QUE CE FICHIER EXÉCUTE. Le corpus publie **103 cases vides du
régime du prix** : des segments dont la pile de couches est rendue à 8,6–9,4 µm / 1,2 m et dont
**aucune carte d'encre** n'existe, alors que le même segment en porte une dans le régime de
production. Le Grand Prix se joue sur des rouleaux qui n'existent *que* dans le régime vide.

⭐⭐⭐ LA MESURE QUI REND CE FICHIER SIMPLE, prise le 2026-09-05 : les deux volumes de surface
d'un même segment couvrent **la même épaisseur physique**.

| régime | taille de voxel | couches | pile | ce que les 26 du modèle couvrent |
|---|---:|---:|---:|---:|
| production | 2,399 µm | **109** | 261 µm | **62 µm** |
| **prix** | 9,362 µm | **28** | 262 µm | **243 µm** |

Un volume de surface est donc une dalle d'épaisseur **fixée en micromètres** ; le nombre de
couches n'est que la taille de voxel. Conséquences directes, et elles vont dans deux sens :

  - au régime du prix la fenêtre du modèle **est** le volume — il n'y a **aucun choix de
    profondeur à faire**, et donc aucune façon de se tromper de fenêtre ;
  - et c'est le régime **grossier** qui lit les 243 µm proches des 206 µm de l'entraînement,
    pendant que le régime **fin** n'en lit que 62. Le scan de repérage est, sur ce point précis,
    celui qui ressemble à l'entraînement.

⚠⚠ ET LA CONFRONTATION EST LA MOITIÉ QUI COMPTE. « Ce que le détecteur rend à 9,362 µm » est un
nombre sans référence. Le même segment publie une carte d'encre **à 2,399 µm**, produite par la
communauté avec son propre modèle (`new_canon_autoresearch_recipe`) : c'est la meilleure réponse
disponible à *« y a-t-il de l'encre ici ? »*, et elle est indépendante de nous.

⚠ Ce n'est PAS une vérité terrain. Deux modèles peuvent se tromper ensemble, et celui-ci n'est
pas le nôtre. Ce qui se mesure est un **accord**, pas une justesse — et un désaccord ne dit pas
lequel a tort. La vérité terrain infrarouge existe sur `PHerc0500P2`, pas ici.

⚠⚠⚠ ET LA GARANTIE ANTI-HALLUCINATION NE SE TRANSPORTE PAS, ce que `68` §5 mesure : une tuile de
256 px couvre 614 µm à 2,4 µm — moins d'une lettre, ce qui est toute la défense du papier — et
**2 397 µm** à 9,362, soit près de quatre lettres. Ce fichier note donc la largeur physique de
sa fenêtre plutôt que son compte de pixels, et l'unité de **notation** (la tuile) est choisie
séparément de la fenêtre du **modèle**.

Usage :
    uv run python src/encre/la_case_vide_remplie.py --verifier
    uv run python src/encre/la_case_vide_remplie.py --segment 20260325000000-w046_20260325 \\
        --json docs/mesures/la_case_vide_remplie.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from le_nul_verso import (  # noqa: E402
    COUCHES_LUES, EXTRACTEUR, REGIMES, _inference, _lancer, aire_sous_la_courbe,
    chercher_fenetre, niveau_le_plus_grossier, prendre_le_verrou,
)

RACINE = Path(__file__).resolve().parents[2]
CARTES = RACINE / "docs" / "mesures" / "case_vide_cartes"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "la_case_vide_remplie.json"

VOXEL_UM = {"production": 2.399, "prix": 9.362}
"""Taille de voxel de chaque régime, lue dans la clef du volume publié."""

TUILE_DU_PAPIER_PX = 256
"""La tuile des cartes publiées (`tile256-stride128`), et le piège de `68` §5."""


def largeur_physique_um(pixels: int, regime: str) -> float:
    """
    @brief Ce qu'une fenêtre de N pixels couvre RÉELLEMENT, en micromètres.

    ⚠⚠ C'est la seule unité dans laquelle deux régimes se comparent. « 256 px » ne veut pas dire
    la même chose des deux côtés, et c'est exactement ce que `68` §5 mesure : 614 µm à 2,4 µm
    contre 2 397 à 9,362 — moins d'une lettre d'un côté, presque quatre de l'autre.
    """
    return pixels * VOXEL_UM[regime]


def formes_du_segment(segment: str) -> dict:
    """
    @brief Les formes des deux piles publiées, et l'alignement de leurs grilles.

    ⚠⚠⚠ L'ALIGNEMENT EST VÉRIFIÉ, PAS SUPPOSÉ. Les deux cartes vivent sur deux `tifxyz`
    différents (`on-…-2.399um` et `on-…-9.362um`) : leurs coordonnées ne coïncident que si les
    grilles sont dans le rapport des tailles de voxel. Mesuré : 23 280 / 5 980 = **3,893** et
    32 160 / 8 260 = **3,893**, contre un rapport de voxels de **3,903** — 0,3 % d'écart, ce
    qu'un arrondi de dimensions explique. Sans ce contrôle, comparer les deux cartes
    comparerait deux régions différentes du même segment, et le désaccord se lirait comme un
    désaccord de modèles.
    """
    import json as _json

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    out = {}
    for regime, cle in REGIMES.items():
        z = f"PHerc0139/segments/{segment}/surface-volumes/{cle}"
        b = _json.loads(get(f"{BUCKET}/{z.rstrip('/')}/0/.zarray", 30))
        forme = list(b["shape"])
        out[regime] = dict(zarr=z, forme=forme,
                           pile_um=forme[0] * VOXEL_UM[regime],
                           fenetre_um=COUCHES_LUES * VOXEL_UM[regime])
    a, b_ = out["production"]["forme"], out["prix"]["forme"]
    rapports = [a[1] / b_[1], a[2] / b_[2]]
    attendu = VOXEL_UM["prix"] / VOXEL_UM["production"]
    out["rapport_grilles"] = rapports
    out["rapport_voxels"] = attendu
    out["grilles_alignees"] = all(abs(r / attendu - 1.0) < 0.01 for r in rapports)
    return out


def carte_publiee(segment: str) -> np.ndarray | None:
    """
    @brief La carte d'encre publiée du segment, en version réduite ×8.

    ⚠⚠ LA VERSION RÉDUITE, ET C'EST UN CHOIX ASSUMÉ. La carte pleine fait 23 280 × 32 160 à
    2,399 µm ; la réduite `-ds8.jpg` pèse **870 Ko**. Comme notre propre carte est rendue au pas
    21, elle est de toute façon grossière : réclamer la pleine résolution paierait un gigaoctet
    pour une comparaison qui n'en tirerait rien.

    ⚠⚠⚠ MAIS C'EST UN JPEG, DONC SES VALEURS SONT PERDUES. Une compression avec perte et une
    renormalisation d'affichage détruisent l'échelle du modèle : ce qui reste comparable est le
    **motif spatial** — où le modèle dit « encre » — jamais le niveau. Toute mesure ici est donc
    de RANG (corrélation de rangs, aire sous la courbe), jamais une différence de valeurs.
    """
    from PIL import Image

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    prefixe = (f"PHerc0139/segments/{segment}/ink-detection/downsampled/")
    # ⚠ Le nom exact du fichier porte un horodatage et une recette : il se LIT dans l'index
    # publié plutôt que de se deviner, sinon un changement de recette casse silencieusement.
    sys.path.insert(0, str(RACINE / "src" / "encre"))
    import la_case_vide as cv  # noqa: PLC0415

    for _, fiche in cv._charger().items():
        for sid, seg in fiche.get("segments", {}).items():
            if seg.get("long_id", sid) != segment:
                continue
            for e in seg.get("data", []):
                chemin = e.get("origins", [{}])[0].get("path", "")
                if (e.get("type") == "ink-detection-downsampled"
                        and chemin.startswith(prefixe) and "2.399um" in chemin):
                    brut = get(f"{BUCKET}/{chemin}", 120)
                    if brut is None:
                        return None
                    return np.asarray(Image.open(io.BytesIO(brut)).convert("L"), dtype=float)
    return None


def region_publiee(carte: np.ndarray, top: int, left: int, taille: int,
                   forme_prix: list[int], forme_prod: list[int]) -> np.ndarray | None:
    """
    @brief La même région physique, découpée dans la carte publiée réduite.

    ⚠⚠ Les coordonnées sont celles de la grille du RÉGIME DU PRIX ; la carte publiée vit sur la
    grille de production réduite ×8. Le facteur se dérive donc des deux formes réelles, jamais
    d'un 8 ou d'un 3,9 écrit à la main — les dimensions publiées sont arrondies, et un facteur
    supposé décalerait la fenêtre d'une dizaine de pixels sans que rien ne le dise.
    """
    fr = carte.shape[0] / forme_prix[1]
    fc = carte.shape[1] / forme_prix[2]
    r0, c0 = int(round(top * fr)), int(round(left * fc))
    r1, c1 = int(round((top + taille) * fr)), int(round((left + taille) * fc))
    if r1 <= r0 or c1 <= c0 or r1 > carte.shape[0] or c1 > carte.shape[1]:
        return None
    return carte[r0:r1, c0:c1]


def remplir(segment: str, taille: int = 512) -> dict:
    formes = formes_du_segment(segment)
    if not formes["grilles_alignees"]:
        raise SystemExit(
            f"grilles non alignées : rapports {formes['rapport_grilles']} contre un rapport de "
            f"voxels de {formes['rapport_voxels']:.3f} — comparer les deux cartes comparerait "
            "deux régions différentes")
    zarr = formes["prix"]["zarr"]
    f = chercher_fenetre(zarr, taille)
    top, left = f["top"], f["left"]
    couches_dispo = formes["prix"]["forme"][0]
    # ⚠⚠ À 28 couches pour une fenêtre de 26, le début n'a que trois valeurs possibles. On prend
    # le centre : la surface tracée est au milieu du volume par construction, et un début à 0
    # ou à 2 décalerait la fenêtre d'un demi-pas sans rien gagner.
    debut = max(0, (couches_dispo - COUCHES_LUES) // 2)
    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp) / "couches"
        code, texte = _lancer(
            ["uv", "run", "python", str(EXTRACTEUR), zarr, "--sortie", str(dossier),
             "--top", str(top), "--left", str(left),
             "--hauteur", str(taille), "--largeur", str(taille)], 3600)
        if code != 0:
            raise SystemExit(f"extraction échouée : {texte.strip()[-200:]}")
        CARTES.mkdir(parents=True, exist_ok=True)
        sortie = CARTES / f"{segment}_prix.npy"
        rendu = _inference(dossier, debut, taille, sortie)
    out = dict(segment=segment, regime="prix", zarr=zarr, top=top, left=left, taille=taille,
               debut=debut, couches_disponibles=couches_dispo,
               fenetre_um=formes["prix"]["fenetre_um"],
               tuile_du_papier_um=largeur_physique_um(TUILE_DU_PAPIER_PX, "prix"),
               formes=formes, rendu=rendu)
    if rendu and not rendu.get("echec"):
        nous = np.load(sortie)
        publiee = carte_publiee(segment)
        if publiee is not None:
            region = region_publiee(publiee, top, left, taille,
                                    formes["prix"]["forme"], formes["production"]["forme"])
            if region is not None:
                out.update(_confronter(nous, region))
    return out


def _confronter(nous: np.ndarray, publiee: np.ndarray) -> dict:
    """
    @brief L'accord entre notre carte au régime du prix et la carte publiée en production.

    ⚠⚠ TOUT EST DE RANG. La carte publiée nous parvient en JPEG réduit, donc ses valeurs ont
    traversé une compression avec perte et une renormalisation. Une corrélation de Pearson ou un
    écart de médianes y mesurerait l'encodage ; une AUC et une corrélation de rangs ne mesurent
    que l'ORDRE, qui survit à une renormalisation monotone.

    ⚠ Les deux cartes n'ont pas la même taille : on ramène la nôtre sur la grille de l'autre par
    échantillonnage au plus proche, ce qui ne crée aucune valeur — un ré-échantillonnage lissant
    en inventerait, et un lissage d'un seul côté est exactement ce qui fabrique une corrélation.
    """
    bons = np.isfinite(nous)
    if bons.sum() < 1000 or publiee.size < 100:
        return {}
    lignes = np.linspace(0, nous.shape[0] - 1, publiee.shape[0]).round().astype(int)
    colonnes = np.linspace(0, nous.shape[1] - 1, publiee.shape[1]).round().astype(int)
    reduite = nous[np.ix_(lignes, colonnes)]
    valides = np.isfinite(reduite)
    a, b = reduite[valides].ravel(), publiee[valides].ravel()
    if a.size < 100:
        return {}
    # ⚠⚠⚠ LE SEUIL VIENT DE LA CARTE PUBLIÉE, pas de la nôtre : « ce que la communauté appelle
    # encre » est la question posée. Sa médiane partage sa propre population en deux, donc l'AUC
    # demande *notre carte classe-t-elle ces deux moitiés-là ?*
    seuil = float(np.median(b))
    encre, fond = a[b > seuil], a[b <= seuil]
    if encre.size < 20 or fond.size < 20:
        return {}
    return dict(auc_contre_publiee=aire_sous_la_courbe(encre, fond),
                pixels_confrontes=int(a.size),
                seuil_publie=seuil,
                part_encre_publiee=float((b > seuil).mean()))


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE PIÈGE DE `68` §5, REPRODUIT ICI : « 256 px » ne veut pas dire la même chose.
    v("une tuile de 256 px couvre 614 µm en production",
      abs(largeur_physique_um(256, "production") - 614) < 5,
      f"{largeur_physique_um(256, 'production'):.0f} µm")
    v("... et 2 397 µm au régime du prix",
      abs(largeur_physique_um(256, "prix") - 2397) < 5,
      f"{largeur_physique_um(256, 'prix'):.0f} µm")
    v("... soit près de quatre lettres au lieu d'une",
      largeur_physique_um(256, "prix") / largeur_physique_um(256, "production") > 3.5)
    # ⚠ La fenêtre du modèle, elle, se compare en µm et non en couches.
    v("la fenêtre du modèle couvre 62 µm en production et 243 au régime du prix",
      abs(COUCHES_LUES * VOXEL_UM["production"] - 62) < 2
      and abs(COUCHES_LUES * VOXEL_UM["prix"] - 243) < 2)

    # ⚠⚠⚠ LE DÉCOUPAGE DE LA RÉGION, testé sur une carte FABRIQUÉE dont on connaît la réponse.
    # Un facteur supposé au lieu de dérivé décalerait la fenêtre sans rien lever.
    carte = np.arange(100 * 400, dtype=float).reshape(100, 400)
    reg = region_publiee(carte, top=200, left=400, taille=100,
                         forme_prix=[28, 1000, 2000], forme_prod=[109, 3900, 7800])
    v("la région découpée a la taille attendue", reg.shape == (10, 20), str(reg.shape))
    v("... et elle commence au bon endroit", reg[0, 0] == carte[20, 80],
      f"{reg[0, 0]} contre {carte[20, 80]}")
    # ⚠ Une région hors carte rend None plutôt qu'un tableau tronqué : un tableau plus petit
    # que demandé se comparerait quand même, à la mauvaise région.
    v("une région hors de la carte est refusée",
      region_publiee(carte, top=990, left=0, taille=100,
                     forme_prix=[28, 1000, 2000], forme_prod=[109, 3900, 7800]) is None)

    # ⚠⚠ L'AUC contre une carte publiée, sur deux cas dont on connaît la réponse.
    n = np.arange(60 * 60, dtype=float).reshape(60, 60)
    v("un accord parfait rend une AUC de 1", _confronter(n, n.copy())["auc_contre_publiee"] > 0.99)
    v("... et un désaccord parfait une AUC de 0",
      _confronter(n, -n)["auc_contre_publiee"] < 0.01)

    if r:
        print("\net la mesure")
        v("les grilles des deux régimes sont alignées",
          r["formes"]["grilles_alignees"],
          f"rapports {[round(x, 3) for x in r['formes']['rapport_grilles']]} contre "
          f"{r['formes']['rapport_voxels']:.3f}")
        v("la case vide est remplie", bool(r["rendu"]) and not r["rendu"].get("echec"),
          str(r["rendu"].get("echec") or "carte rendue"))
        if r.get("auc_contre_publiee") is not None:
            # ⚠⚠⚠ ÉCRIT POUR TOMBER DANS LES DEUX SENS. Un accord franc dirait que le régime du
            # prix garde ce que la communauté appelle encre ; un accord au hasard dirait qu'il
            # ne le garde pas. Les deux sont publiables, et c'est ce que `68` §4 demande.
            v("notre carte au régime du prix s'accorde avec la carte publiée",
              r["auc_contre_publiee"] > 0.60,
              f"AUC {r['auc_contre_publiee']:.3f} sur {r['pixels_confrontes']} pixels "
              f"(0,5 = pile ou face)")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--segment", default="20260325000000-w046_20260325")
    p.add_argument("--taille", type=int, default=512)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.verifier and not a.json:
        cible = DEFAUT_JSON
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0

    _verrou = prendre_le_verrou()  # noqa: F841
    r = remplir(a.segment, a.taille)
    print(f"{r['segment']} — régime du prix, {r['couches_disponibles']} couches disponibles")
    print(f"  fenêtre du modèle : {r['debut']}..{r['debut'] + COUCHES_LUES} "
          f"= {r['fenetre_um']:.0f} µm")
    print(f"  ⚠ une tuile de 256 px vaudrait ici {r['tuile_du_papier_um']:.0f} µm")
    d = r["rendu"]
    if d.get("echec"):
        print(f"  ÉCHEC — {d['echec']}", file=sys.stderr)
        return 2
    print(f"  encre min/méd/max {d['minimum']:+.3f} / {d['mediane']:+.3f} / {d['maximum']:+.3f}"
          f"   ({d['couverts']}/{d['total']} px)")
    if r.get("auc_contre_publiee") is not None:
        print(f"\n  AUC contre la carte publiée en production : "
              f"{r['auc_contre_publiee']:.3f}   "
              f"({r['pixels_confrontes']} pixels, "
              f"{100 * r['part_encre_publiee']:.0f} % au-dessus du seuil publié)")
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
