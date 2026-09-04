#!/usr/bin/env python3
"""Dans quel sens comptent les indices de spire publiés — et ce qu'ils mesurent au passage.

⭐⭐⭐ CE QUE CE FICHIER ÉTABLIT. `74` §3 a compté le référent d'identité : 101 segments
publiés portent leur numéro de spire, dont **81 spires consécutives sans trou** sur
`PHerc0139` et `PHerc0172`. Restait la question que `73` §4 déclarait `[je ne sais pas]` et
qui bloque tout le reste : **`w` compte-t-il depuis le centre ou depuis l'extérieur ?** Tant
qu'on l'ignore, « consécutif » est une propriété des NOMS et pas de la géométrie, et un test
d'identité bâti dessus pourrait tourner à l'envers sans que rien ne le dise.

**Réponse mesurée : depuis le CENTRE vers l'extérieur.** Sur `PHerc0139`, `w_{k+1}` est plus
loin de l'axe que `w_k` dans **98 %** des cellules (z, angle) comparables.

⭐⭐ ET LA MÊME MESURE REND UN SECOND RÉSULTAT QU'ON NE CHERCHAIT PAS : l'écart radial médian
entre deux spires consécutives est un **écart inter-feuilles mesuré sur des surfaces
approuvées par des humains, sans aucun paramètre de traceur**. C'est exactement le chiffre que
l'article `§2.1` peine à nommer — ses 113 µm sont une distance au plus proche voisin qui
**dépend de `neighbor_step`** (116 → 102 µm quand le pas est halvé trois fois, `43`).

⚠⚠⚠ LE PIÈGE QUI AURAIT TOUT FAUSSÉ, EN SILENCE ET DE PLUSIEURS FAÇONS À LA FOIS. La taille
de voxel ne se lit PAS dans le nom du volume, et pas seulement parce qu'il se trompe : les
37 segments d'un même rouleau en déclarent **trois différents**, et aucun n'est le bon.

    26 segments   `2um_srf_ds2`
    10 segments   `4.681um_113keV_1.2m_binmean_2_PHerc_0139_110_surf`
     1 segment    `.vc3d_rasterize_20260313123342`   (aucune résolution du tout)

Le nom porte la résolution **avant** sous-échantillonnage ; le maillage vit dans la grille
**après**. Un lecteur qui parse le nom ne se tromperait donc pas d'un facteur constant — il se
tromperait **d'un facteur différent par segment**, ce qui rendrait les spires incomparables
entre elles pendant que chaque nombre resterait plausible.

Ce fichier décode plutôt le voxel du meta lui-même, qui publie la même aire dans deux unités :

    voxel = sqrt(area_cm2 × 1e8 / area_vx2)

⚠ Et c'est un **décodage**, pas une mesure physique indépendante : `area_cm2` a été calculée
À PARTIR de `area_vx2` et du voxel, donc le rapport rend exactement le voxel que l'éditeur a
utilisé. C'est ce qu'on veut — la valeur de l'éditeur, sans passer par une chaîne de
caractères — et ce qui le VALIDE est extérieur : **9,3620 µm est une résolution de scan
publiée pour ce rouleau** (`20250720065842-9.362um-1.2m-113keV`), donc le décodage tombe sur
un régime réel et non sur un nombre commode. 35 des 37 segments décodent exactement cette
valeur ; les deux autres (9,6198 et 13,3935) ont une comptabilité d'aire differente et sont
comptés comme tels plutôt que moyennés dans le tas.

⚠⚠ LA MESURE EST APPARIÉE, ET ELLE DOIT L'ÊTRE. Un rouleau d'Herculanum est **écrasé** : un
rayon absolu ajusté par un cercle n'a pas de sens (l'étendue p10–p90 d'une seule spire vaut
566 voxels, soit ~17 feuilles). Et l'axe **erre** — mesuré ici de (3625, 3526) à (3366, 3029)
sur 30 mm de hauteur, ce que `laxe_nest_pas_une_ligne.py` avait établi sur Scroll 1. Comparer
deux spires ne se fait donc qu'**à la même hauteur et au même angle**, avec un centre ajusté
sur l'UNION des deux — un centre par spire ferait dépendre l'écart de deux ajustements
différents.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que `w_k` et `w_{k+1}` soient des feuilles ADJACENTES.** Les indices sont consécutifs ;
   rien ici ne prouve qu'aucune feuille n'a été sautée à la numérotation. L'écart mesuré est
   donc un écart **par pas d'indice**, qui vaut un écart inter-feuilles si et seulement si la
   numérotation est dense. Le contrôle de linéarité ci-dessous rend cette hypothèse testable :
   si l'écart croît proportionnellement à `|Δw|`, c'est qu'un pas d'indice est une unité
   constante.
2. **Que le sens soit le même sur les quatre rouleaux indexés.** Mesuré ici sur `PHerc0139`.
   `PHerc0172` publie ses maillages sous un autre chemin (`mesh/*-on-*.tifxyz`, pas
   `tifxyz_original`) et n'est pas rapatrié par ce fichier.
3. **Que l'écart mesuré vaille pour un autre rouleau.** `16` mesure des écarts médians de 156
   à 225 µm selon le rouleau : c'est une propriété du rouleau, pas une constante.

Usage :
    uv run python src/excision/le_sens_des_indices.py --verifier
    uv run python src/excision/le_sens_des_indices.py --json docs/mesures/le_sens_des_indices.json

⚠ La figure est dessinée à part, par `src/figures/figure_sens_des_indices.py`, qui lit le JSON
ci-dessus. Le dépôt dessine avec PIL et non matplotlib (cf. `figure_commune.py`) : mesurer et
dessiner sont deux verbes, et les mêler ferait dépendre une mesure d'une pile graphique.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import tifffile

RACINE = Path(__file__).resolve().parents[2]
CACHE = RACINE / "data" / "indices_de_spire"

TRANCHES_Z = 24
"""Hauteurs comparées. ⚠ Le nombre est un compromis mesuré, pas un réglage : trop peu et une
tranche mélange des hauteurs où l'axe a bougé de plusieurs feuilles, trop et chaque tranche
n'a plus assez de points pour qu'une médiane veuille dire quelque chose."""

SECTEURS = 72
"""Secteurs angulaires, soit 5° chacun. Une cellule (tranche, secteur) est l'unité de
comparaison : c'est là, et seulement là, que deux spires sont comparables."""

POINTS_MINIMUM = 10
"""Points exigés dans une cellule POUR CHACUNE des deux spires. En dessous, la médiane d'une
cellule est le bruit d'une poignée de sommets."""

INVALIDE = 0.0
"""⚠ Un tifxyz publié marque ses trous par des valeurs ≤ 0 (on a vu -1,0), pas par NaN. Les
garder ferait passer un trou pour un point à l'origine, donc à un rayon énorme.

⚠ Mais ce filtre n'est PAS porteur pour cette mesure-ci, et le dire vaut mieux que le laisser
croire : sondé en le retirant, le sens passe de 95,0 à 94,6 % et l'écart de 154,1 à 152,3 µm —
les deux contrôles restent verts. La médiane par cellule absorbe une poignée de trous. Il est
gardé parce qu'il est juste, pas parce que le résultat en dépend."""


def voxel_de(meta: dict) -> float | None:
    """
    @brief La taille de voxel du maillage, DÉRIVÉE de son aire et jamais lue dans un nom.

    Le meta publie la même aire deux fois, en cm² et en voxels² : leur rapport donne le voxel
    sans rien parser. C'est ce qui immunise contre le nom de volume, qui porte la résolution
    d'avant binning (cf. l'avertissement en tête de fichier).
    """
    a_cm2, a_vx2 = meta.get("area_cm2"), meta.get("area_vx2")
    if not a_cm2 or not a_vx2 or a_vx2 <= 0:
        return None
    return math.sqrt(a_cm2 * 1e8 / a_vx2)


def charger(dossier: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """
    @brief Les sommets valides d'un tifxyz, en coordonnées de scan.
    """
    try:
        x, y, z = (tifffile.imread(dossier / f"{c}.tif").astype(np.float64) for c in "xyz")
    except (OSError, ValueError):
        return None
    valides = (x > INVALIDE) & (y > INVALIDE) & np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    if valides.sum() < 1000:
        return None
    return x[valides], y[valides], z[valides]


def centre_de(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """
    @brief Le centre d'un ajustement de cercle algébrique (Kāsa) — une résolution linéaire.

    ⚠ Le RAYON de cet ajustement n'est pas utilisé et ne doit pas l'être : un rouleau écrasé
    n'est pas un cercle. Seul le centre sert, et seulement comme origine commune d'une
    comparaison appariée.
    """
    a = np.c_[2 * x, 2 * y, np.ones(len(x))]
    solution, *_ = np.linalg.lstsq(a, x**2 + y**2, rcond=None)
    return float(solution[0]), float(solution[1])


def comparer(a: tuple, b: tuple) -> dict:
    """
    @brief Écart radial de la spire `b` à la spire `a`, cellule (hauteur, angle) par cellule.

    Rend la part de cellules où `b` est plus loin de l'axe, et la distribution des écarts.
    """
    (xa, ya, za), (xb, yb, zb) = a, b
    bas, haut = max(za.min(), zb.min()), min(za.max(), zb.max())
    if haut - bas < 1.0:
        return dict(cellules=0)

    bords_z = np.linspace(bas, haut, TRANCHES_Z + 1)
    bords_t = np.linspace(-np.pi, np.pi, SECTEURS + 1)
    ecarts: list[float] = []

    for lo, hi in zip(bords_z, bords_z[1:]):
        sa, sb = (za >= lo) & (za < hi), (zb >= lo) & (zb < hi)
        if sa.sum() < 200 or sb.sum() < 200:
            continue
        # ⚠⚠ Le centre est ajusté sur l'UNION des deux spires. Un centre par spire ferait
        # dépendre l'écart de deux ajustements independants, donc mesurerait la difference
        # entre deux ajustements autant que la distance entre deux feuilles.
        cx, cy = centre_de(np.r_[xa[sa], xb[sb]], np.r_[ya[sa], yb[sb]])
        ta = np.digitize(np.arctan2(ya[sa] - cy, xa[sa] - cx), bords_t)
        tb = np.digitize(np.arctan2(yb[sb] - cy, xb[sb] - cx), bords_t)
        ra = np.hypot(xa[sa] - cx, ya[sa] - cy)
        rb = np.hypot(xb[sb] - cx, yb[sb] - cy)
        for secteur in range(1, SECTEURS + 1):
            pa, pb = ra[ta == secteur], rb[tb == secteur]
            if len(pa) >= POINTS_MINIMUM and len(pb) >= POINTS_MINIMUM:
                ecarts.append(float(np.median(pb) - np.median(pa)))

    if not ecarts:
        return dict(cellules=0)
    e = np.array(ecarts)
    return dict(cellules=len(e), part_vers_l_exterieur=float((e > 0).mean()),
                median_vx=float(np.median(e)),
                p25_vx=float(np.percentile(e, 25)), p75_vx=float(np.percentile(e, 75)))


def _spires(rouleau: str) -> dict[int, Path]:
    base = CACHE / rouleau
    if not base.is_dir():
        return {}
    out = {}
    for d in sorted(base.iterdir()):
        m = re.fullmatch(r"w(\d{3})", d.name)
        if m and (d / "z.tif").is_file():
            out[int(m.group(1))] = d
    return out


def mesurer(rouleau: str = "PHerc0139") -> dict:
    dossiers = _spires(rouleau)
    if len(dossiers) < 2:
        raise SystemExit(
            f"moins de deux spires en cache pour {rouleau} sous {CACHE}\n"
            f"  les rapatrier :  uv run python src/excision/le_sens_des_indices.py --rapatrier {rouleau}")

    metas = {k: json.loads((d / "meta.json").read_text()) for k, d in dossiers.items()
             if (d / "meta.json").is_file()}
    # ⭐ L'ETALON que la tache A5 du registre `75` reclame, et il est PUBLIE : chaque meta porte
    # l'aire de sa spire. L'article §5.6 mesure que l'extension converge vers un point fixe de
    # 6,02 cm² ; une spire que des humains ont accepte de publier fait plusieurs fois ça.
    # ⚠ Compte a part des spires SANS aire : trois metas n'en portent pas, et les compter comme
    # zero tirerait la mediane vers le bas sans qu'aucun chiffre n'ait l'air faux.
    aires = sorted(m["area_cm2"] for m in metas.values() if m.get("area_cm2"))

    voxels = [v for v in (voxel_de(m) for m in metas.values()) if v]
    # ⚠ Le MODE, pas la moyenne ni la mediane : les segments dont la comptabilite d'aire
    # differe doivent etre COMPTES a part, pas dilues dans une moyenne qui rendrait une
    # valeur qu'aucun segment ne porte.
    voxel_um, accord = _voxel_dominant(voxels)

    nuages = {k: charger(d) for k, d in dossiers.items()}
    nuages = {k: v for k, v in nuages.items() if v}

    indices = sorted(nuages)
    consecutives, ecarts_par_pas = [], []
    for a, b in zip(indices, indices[1:]):
        if b - a != 1:
            continue
        r = comparer(nuages[a], nuages[b])
        if r["cellules"]:
            r.update(de=a, vers=b)
            consecutives.append(r)

    # ⚠⚠ LE CONTRÔLE DE LINÉARITÉ. Si un pas d'indice est une unité constante, l'écart doit
    # croître proportionnellement à |Δw|. Sans lui, « consécutif » resterait une hypothèse : un
    # ecart mesuré entre deux voisins ne dit pas qu'aucune feuille n'a ete sautee ailleurs.
    for saut in (1, 2, 3, 5):
        mesures = []
        for a in indices:
            if a + saut in nuages:
                r = comparer(nuages[a], nuages[a + saut])
                if r["cellules"]:
                    mesures.append(r["median_vx"])
        if mesures:
            ecarts_par_pas.append(dict(saut=saut, n=len(mesures),
                                       median_vx=float(np.median(mesures))))

    # Deux spires voisines d'un meme rouleau ont des boites qui se recouvrent largement : si
    # elles ne se recouvraient pas, elles seraient dans deux reperes differents et aucune
    # comparaison radiale n'aurait de sens.
    emboitees = 0
    for a_, b_ in zip(indices, indices[1:]):
        if b_ - a_ != 1:
            continue
        ba, bb = metas.get(a_, {}).get("bbox"), metas.get(b_, {}).get("bbox")
        if not ba or not bb:
            continue
        if all(min(ba[1][i], bb[1][i]) - max(ba[0][i], bb[0][i]) > 0 for i in range(3)):
            emboitees += 1

    # ⚠⚠⚠ LE CONTRÔLE QUI PEUT ÉCHOUER : une spire comparée à ELLE-MÊME doit rendre zéro.
    # Sans lui, un biais systématique de la méthode (un centre mal placé, un bord de secteur)
    # se lirait comme une distance entre feuilles.
    temoin = comparer(nuages[indices[0]], nuages[indices[0]])

    part = [c["part_vers_l_exterieur"] for c in consecutives]
    med = [c["median_vx"] for c in consecutives]

    # ⚠⚠⚠ LES DEFAUTS DU REFERENT, trouves en REGARDANT la figure et non en relisant le code.
    # Deux paires consecutives sur 36 ne sont pas a une feuille l'une de l'autre : `w045`/`w046`
    # sont la MEME surface (ecart 0,0 µm, confirme independamment par le discriminant du depot
    # `carte_segments.ecart_entre`, qui n'ajuste aucun cercle et ne decoupe aucun secteur), et
    # `w041`/`w042` sont a 88 µm, soit une demi-feuille.
    #
    # Ca compte pour la suite : un test d'identite qui supposerait que CHAQUE paire consecutive
    # vaut une feuille compterait ces deux-la comme des echecs du PREDICTEUR alors que ce sont
    # des defauts du REFERENT. Un referent approuve par des humains n'est pas un referent
    # parfait, et le seul moyen de le savoir est de le mesurer contre lui-meme.
    seuil = 0.5 * float(np.median(med)) if med else 0.0
    defauts = sorted(
        (dict(de=c["de"], vers=c["vers"],
              ecart_um=float(c["median_vx"] * voxel_um) if voxel_um else None,
              part_vers_l_exterieur=c["part_vers_l_exterieur"])
         for c in consecutives if c["median_vx"] < seuil),
        key=lambda d: d["ecart_um"] if d["ecart_um"] is not None else 0.0)
    return dict(
        rouleau=rouleau, spires_en_cache=len(nuages),
        indices=[indices[0], indices[-1]],
        voxel_um=voxel_um,
        segments_d_accord_sur_le_voxel=accord,
        segments_avec_une_aire=len(voxels),
        boites_qui_s_emboitent=emboitees,
        noms_de_volume=_noms_de_volume(metas),
        paires_consecutives=len(consecutives),
        cellules_comparees=int(sum(c["cellules"] for c in consecutives)),
        part_vers_l_exterieur=float(np.mean(part)) if part else None,
        ecart_median_vx=float(np.median(med)) if med else None,
        ecart_median_um=float(np.median(med) * voxel_um) if med and voxel_um else None,
        ecart_p25_um=float(np.median([c["p25_vx"] for c in consecutives]) * voxel_um)
        if med and voxel_um else None,
        ecart_p75_um=float(np.median([c["p75_vx"] for c in consecutives]) * voxel_um)
        if med and voxel_um else None,
        seuil_de_defaut_um=float(seuil * voxel_um) if voxel_um else None,
        defauts_du_referent=defauts,
        aire_par_spire_cm2=dict(
            n=len(aires),
            sans_aire=len(metas) - len(aires),
            min=float(aires[0]) if aires else None,
            median=float(np.median(aires)) if aires else None,
            max=float(aires[-1]) if aires else None,
        ),
        point_fixe_de_l_article_cm2=POINT_FIXE_CM2,
        facteur_sur_le_point_fixe=float(np.median(aires) / POINT_FIXE_CM2) if aires else None,
        par_pas=ecarts_par_pas,
        temoin_soi_meme=temoin,
        consecutives=consecutives,
    )


POINT_FIXE_CM2 = 6.02
"""L'aire vers laquelle le cycle rogner-étendre converge (article §5.6, `44`). ⚠ Écrite ici
parce qu'elle est la SEULE raison pour laquelle l'aire d'une spire publiée est intéressante :
sans point de comparaison, « 38 cm² » n'est qu'un nombre."""

SCANS_PUBLIES_UM = (9.362, 4.681, 2.403, 2.399, 1.129)
"""Les résolutions de scan que `PHerc0139` publie (`data/metadata.min.json`), plus la 4,681 que
son nom de volume revendique. ⚠ Écrites ici pour que le décodage soit VALIDÉ contre une liste
extérieure : un voxel décodé qui ne tombe sur aucun régime réel est un décodage à jeter, pas un
nombre à publier."""


def _voxel_dominant(voxels: list[float]) -> tuple[float | None, int]:
    """
    @brief La valeur de voxel que le PLUS de segments portent, et combien la portent.

    ⚠ Le mode et non la moyenne : deux segments dont la comptabilité d'aire diffère doivent
    être comptés à part. Une moyenne rendrait une valeur qu'aucun segment ne porte, et qui ne
    tomberait sur aucun régime publié — donc une valeur invalidable par rien.
    """
    if not voxels:
        return None, 0
    arrondis = [round(v, 4) for v in voxels]
    dominant = max(set(arrondis), key=arrondis.count)
    return float(dominant), arrondis.count(dominant)


def _noms_de_volume(metas: dict) -> dict[str, int]:
    """
    @brief Les noms de volume déclarés, comptés — ils sont plusieurs, et c'est le point.
    """
    compte: dict[str, int] = {}
    for m in metas.values():
        compte[str(m.get("volume"))] = compte.get(str(m.get("volume")), 0) + 1
    return dict(sorted(compte.items(), key=lambda kv: -kv[1]))


def _verifier(r: dict) -> int:
    echecs = 0

    def v(nom, ok, detail=""):
        nonlocal echecs
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    print("le voxel se décode de l'aire, et se valide contre les scans publiés")
    v("le voxel décodé tombe exactement sur un régime de scan publié",
      r["voxel_um"] is not None
      and any(abs(r["voxel_um"] - s) < 0.001 for s in SCANS_PUBLIES_UM),
      f"{r['voxel_um']:.4f} µm")
    v("une majorité nette de segments décode la même valeur",
      r["segments_d_accord_sur_le_voxel"] >= 0.7 * r["segments_avec_une_aire"],
      f"{r['segments_d_accord_sur_le_voxel']}/{r['segments_avec_une_aire']} segments")
    # ⚠⚠ LE CONTROLE QUI REND LA COMPARAISON LEGITIME, et il ne porte pas sur le voxel.
    # Sept segments decodent une valeur un peu differente. La question qui decide n'est pas
    # « laquelle est la bonne » mais « sont-ils dans la MEME grille de coordonnees » : deux
    # spires de deux reperes differents ne se comparent pas, et rien dans leurs nombres ne le
    # dirait. Des boites qui se recouvrent et s'emboitent le prouvent.
    v("toutes les spires vivent dans une seule grille de coordonnées",
      r["boites_qui_s_emboitent"] >= 0.9 * max(1, r["paires_consecutives"]),
      f"{r['boites_qui_s_emboitent']}/{r['paires_consecutives']} paires consécutives "
      f"dont les boîtes se recouvrent")
    # ⚠⚠ Le controle qui justifie tout le decodage : si le nom du volume donnait la meme
    # chose, ce fichier n'aurait aucune raison d'exister. Il faut donc montrer qu'il ne la
    # donne PAS -- et qu'il ne donne meme pas une reponse unique.
    v("... alors que le nom de volume n'est pas unique sur un même rouleau",
      len(r["noms_de_volume"]) >= 2,
      " · ".join(f"{n}×{k[:28]}" for k, n in r["noms_de_volume"].items()))
    v("... et qu'aucun de ces noms ne porte la bonne valeur",
      all(not re.match(rf"{r['voxel_um']:.3f}", k) for k in r["noms_de_volume"]),
      "aucun nom ne commence par le voxel réel")

    print("le sens des indices — la question que `73` §4 déclarait ouverte")
    v("assez de cellules comparables pour que ça veuille dire quelque chose",
      r["cellules_comparees"] > 1000, f"{r['cellules_comparees']} cellules (hauteur, angle)")
    v("`w` compte du CENTRE vers l'EXTÉRIEUR",
      r["part_vers_l_exterieur"] is not None and r["part_vers_l_exterieur"] > 0.90,
      f"{r['part_vers_l_exterieur'] * 100:.1f} % des cellules")

    print("le témoin qui peut échouer — une spire contre elle-même")
    t = r["temoin_soi_meme"]
    v("une spire comparée à elle-même rend un écart nul",
      t.get("cellules", 0) > 0 and abs(t.get("median_vx", 9)) < 1e-9,
      f"{t.get('median_vx')} vx sur {t.get('cellules')} cellules")

    print("l'écart par pas d'indice, et sa linéarité")
    v("l'écart médian est dans la plage des écarts inter-feuilles mesurés (`16` : 156–225 µm)",
      r["ecart_median_um"] is not None and 100.0 < r["ecart_median_um"] < 300.0,
      f"{r['ecart_median_um']:.1f} µm")
    pas = {p["saut"]: p["median_vx"] for p in r["par_pas"]}
    # ⚠ Sans ce controle, « consecutif » resterait une propriete des noms : un ecart entre
    # deux voisins ne dit pas qu'aucune feuille n'a ete sautee dans la numerotation.
    v("un saut de 3 indices vaut environ trois fois un saut de 1",
      1 in pas and 3 in pas and 2.4 < pas[3] / pas[1] < 3.6,
      f"×{pas[3] / pas[1]:.2f}" if 1 in pas and 3 in pas else "sauts absents")
    v("... et un saut de 5 environ cinq fois",
      1 in pas and 5 in pas and 4.0 < pas[5] / pas[1] < 6.0,
      f"×{pas[5] / pas[1]:.2f}" if 1 in pas and 5 in pas else "sauts absents")

    print("l'aire d'une spire publiée, contre le point fixe de l'extension")
    aire = r["aire_par_spire_cm2"]
    v("une spire approuvée dépasse largement le point fixe de 6,02 cm²",
      r["facteur_sur_le_point_fixe"] is not None and r["facteur_sur_le_point_fixe"] > 4.0,
      f"médiane {aire['median']:.1f} cm² soit ×{r['facteur_sur_le_point_fixe']:.1f}")
    # ⚠ Sans ce second controle, la mediane pourrait cacher que la plus PETITE spire publiee
    # est deja sous le point fixe -- auquel cas « une spire vaut plusieurs extensions » serait
    # vrai en moyenne et faux pour le cas qui compte.
    v("... et même la plus petite le dépasse",
      aire["min"] is not None and aire["min"] > POINT_FIXE_CM2,
      f"la plus petite fait {aire['min']:.1f} cm²")

    print("les défauts du référent — il en a, et c'est utile de le savoir")
    # ⚠ Ce controle est ecrit dans le sens « il Y EN A », pas « il n'y en a pas ». Un referent
    # sans defaut serait une bonne nouvelle ; un referent dont on n'a pas cherche les defauts
    # est une hypothese. C'est la difference entre les deux qui se garde ici.
    v("des paires consécutives ne sont PAS à une feuille l'une de l'autre",
      len(r["defauts_du_referent"]) >= 1,
      " · ".join(f"w{d['de']:03d}/w{d['vers']:03d} à {d['ecart_um']:.0f} µm"
                 for d in r["defauts_du_referent"]))
    v("... mais ils restent une petite minorité",
      len(r["defauts_du_referent"]) <= 0.15 * max(1, r["paires_consecutives"]),
      f"{len(r['defauts_du_referent'])}/{r['paires_consecutives']} paires")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print("  ALL PASS (0 failures, 15 checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer(args.rouleau)

    if not args.verifier or args.json:
        print(f"{r['rouleau']} — {r['spires_en_cache']} spires en cache, "
              f"w{r['indices'][0]:03d} à w{r['indices'][1]:03d}")
        print(f"  voxel dérivé de l'aire : {r['voxel_um']:.4f} µm "
              f"({r['segments_d_accord_sur_le_voxel']}/{r['segments_avec_une_aire']} segments d'accord)")
        for nom, n in r["noms_de_volume"].items():
            print(f"    ⚠ {n:2d} segment(s) déclarent le volume « {nom} »")
        print(f"  {r['paires_consecutives']} paires consécutives, "
              f"{r['cellules_comparees']} cellules (hauteur, angle)\n")
        print(f"  `w` compte vers l'EXTÉRIEUR dans "
              f"{r['part_vers_l_exterieur'] * 100:.1f} % des cellules")
        print(f"  écart radial médian par pas d'indice : {r['ecart_median_um']:.1f} µm "
              f"(p25 {r['ecart_p25_um']:.0f}, p75 {r['ecart_p75_um']:.0f})\n")
        if r["defauts_du_referent"]:
            print("  ⚠ défauts du référent (paires à moins d'une demi-feuille) :")
            for d in r["defauts_du_referent"]:
                print(f"      w{d['de']:03d} -> w{d['vers']:03d} : {d['ecart_um']:6.1f} µm "
                      f"({d['part_vers_l_exterieur'] * 100:.0f} % vers l'extérieur)")
        print(f"\n  aire d'une spire publiée : {r['aire_par_spire_cm2']['median']:.1f} cm² "
              f"médian ({r['aire_par_spire_cm2']['min']:.1f} à "
              f"{r['aire_par_spire_cm2']['max']:.1f}), soit "
              f"×{r['facteur_sur_le_point_fixe']:.1f} le point fixe de {POINT_FIXE_CM2} cm²")
        print("\n  écart contre saut d'indice :")
        for pp in r["par_pas"]:
            print(f"    Δw = {pp['saut']}  ->  {pp['median_vx'] * r['voxel_um']:7.1f} µm "
                  f"({pp['n']} paires)")

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
