#!/usr/bin/env python3
"""De combien une spire PUBLIÉE s'écarte de la feuille qu'elle suit — et ce que ça plafonne.

⭐⭐⭐ CE FICHIER VIENT D'UNE COUPE, PAS D'UNE HYPOTHÈSE. `77` §9 mesure que le champ
d'enroulement place la feuille suivante à **47 µm** près, et appelle ça son erreur. Restait à
savoir contre quoi cette erreur se mesure. On rend une spire publiée en coupe profondeur ×
largeur — le « B-scan » — et on regarde : **la bande de matière serpente** sur une bonne part
de l'épaisseur de la dalle.

**La surface publiée n'est pas sur la feuille.** Mesuré sur deux spires de `PHerc0172` :

    w062   écart-type 30,8 µm (0,209 feuille)   amplitude p5–p95 101,7 µm (0,690)
    w078   écart-type 29,4 µm (0,199)           amplitude p5–p95  96,8 µm (0,657)

⭐⭐ ET C'EST UN PLANCHER SUR TOUTE ERREUR MESURÉE CONTRE CES SPIRES. Les 47 µm de `77` §9 sont
un écart **à la spire publiée**, et la spire publiée est elle-même à ~30 µm de la matière. Une
part de ce que j'appelais mon erreur de prédiction est donc l'erreur du **référent**, et rien
dans ce dépôt ne peut les séparer tant que la règle est la spire publiée.

⚠ CE QUI REND LA MESURE POSSIBLE : la bande est **nette une fois suivie**. Au centre de masse
elle vaut 163 contre 133 de fond — c'est ce qui distingue « la surface est mal placée » de « il
n'y a pas de signal ». Le premier est corrigeable, le second ne l'est pas.

⚠⚠ L'ESTIMATEUR COMPTE, ET C'EST LE POINT. Le pic brut par colonne (`argmax` sur l'intensité)
donne **0,49 feuille** de dispersion, c'est-à-dire rien d'exploitable ; le **centre de masse**
en profondeur donne **0,19**. Ce n'est pas le signal qui manquait, c'est l'estimateur qui
choisissait un voxel là où il fallait intégrer une bande.

⚠ Voir `LISSAGE` : j'ai d'abord attribué ce gain à un lissage dans le plan, et la mesure dit
que le lissage ne fait rien à l'argmax et **dégrade** le centre de masse.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que la matière suivie soit la BONNE feuille.** Le centre de masse suit la bande la plus
   forte de la dalle ; sur une dalle de 33 couches à 7,91 µm, soit 1,8 écart inter-feuilles,
   une bande voisine peut dominer localement. C'est exactement ce qu'un prédicat d'identité
   doit trancher, et c'est pourquoi les deux ne se remplacent pas.
2. **Que ça vaille pour un autre rouleau.** Deux spires d'un seul rouleau, celles dont le
   volume de surface est rapatriable sans chercher où est la matière (piège nº 27).
3. **Qu'un traceur qui recale sur cette bande ferait mieux.** Il faudrait le mesurer contre
   autre chose que la spire publiée, et il n'y a rien d'autre.

Usage :
    uv run python src/excision/la_surface_et_la_feuille.py --verifier
    uv run python src/excision/la_surface_et_la_feuille.py --json docs/mesures/la_surface_et_la_feuille.json
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
COUCHES = RACINE / "data" / "couches"

SPIRES = ("PHerc0172_w060", "PHerc0172_w061", "PHerc0172_w062",
          "PHerc0172_w063", "PHerc0172_w064", "PHerc0172_w078")
"""Les spires dont les couches sont rapatriées : une course **consécutive** de cinq, plus une
lointaine. ⚠ La course consécutive dit si l'écart varie d'une spire à sa voisine ; la lointaine
dit s'il varie sur le rouleau. Deux questions différentes, et une seule liste ne répondrait
qu'à l'une."""

DALLE_UM = 33 * 7.91
"""L'épaisseur de la dalle rendue. ⚠⚠ Écrite parce qu'elle a réfuté une idée que j'ai eue :
« la dalle fait 1,8 écart inter-feuilles, donc la feuille voisine y est visible ». Faux — elle
fait ±0,9 écart **autour** de la surface, et les voisines sont à ±1,0, donc **juste dehors**.
Vérifié : l'autocorrélation en profondeur décroît et reste plate, sans aucun revival à 19
couches. On ne peut pas mesurer l'écart inter-feuilles dans une seule dalle."""

VOXEL_UM = 7.91
ECART_UM = 147.4
"""Le voxel et l'écart inter-feuilles de `PHerc0172`, mesurés par `76`."""

LISSAGE = 1
"""Fenêtre de lissage dans le plan, en pixels — **1, c'est-à-dire aucun**.

⚠⚠⚠ ET C'EST UNE CORRECTION DE CE QUE J'AVAIS ÉCRIT. J'ai d'abord lissé 9 × 9 et affirmé que
c'était le lissage qui faisait tomber la dispersion de 0,49 à 0,21 feuille — « une feuille est
cohérente dans le plan, et c'est cette cohérence qui la localise ». Une sonde a montré que le
lissage n'était pas porteur, alors je l'ai mesuré séparément :

    lissage    argmax    centre de masse
        1       0,486         0,188
        3       0,488         0,198
        9       0,490         0,209
       17       0,488         0,215

**Le lissage ne fait rien pour l'argmax et rend le centre de masse LÉGÈREMENT PIRE.** Tout le
gain vient de l'**estimateur** : un centre de masse intègre déjà la profondeur, là où un argmax
choisit un voxel. Lisser dans le plan ne fait qu'effacer de la variation réelle.

⭐ La leçon n'est pas « le lissage est inutile » mais « je ne savais pas laquelle des deux
choses faisait le travail, et j'avais publié la mauvaise ». La sonde qui ne mordait pas était
le signal."""

FOND_PERCENTILE = 20
"""Le niveau considéré comme fond. ⚠ Un percentile et non une valeur : les deux spires n'ont
pas le même niveau moyen, et une constante ferait dépendre la mesure de l'exposition."""


def _charger(nom: str) -> np.ndarray | None:
    fichiers = sorted(glob.glob(str(COUCHES / nom / "*.tif")))
    if len(fichiers) < 8:
        return None
    import tifffile
    return np.stack([tifffile.imread(f) for f in fichiers]).astype(np.float32)


def _suivre(pile: np.ndarray, lissage: int = LISSAGE) -> tuple[np.ndarray, np.ndarray, float]:
    """
    @brief Le centre de masse en profondeur de la bande de matière, colonne par colonne.

    Rend le centre de masse, le masque des colonnes qui portent de la matière, et l'intensité
    médiane lue au centre de masse.
    """
    from scipy.ndimage import uniform_filter

    n = pile.shape[0]
    # ⚠ « Il y a de la matiere ici » se lit sur la VARIATION en profondeur autant que sur le
    # niveau : une colonne de remplissage est plate, pas forcement nulle (piege nº 27).
    valide = (pile.max(0) > 0) & (pile.std(0) > 2)
    lisse = uniform_filter(pile, size=(1, lissage, lissage))
    seuil = float(np.percentile(lisse[:, valide], FOND_PERCENTILE)) if valide.any() else 0.0
    poids = np.clip(lisse - seuil, 0, None)
    z = np.arange(n)[:, None, None]
    centre = (poids * z).sum(0) / np.clip(poids.sum(0), 1e-9, None)
    lu = np.take_along_axis(lisse, np.clip(np.round(centre)[None].astype(int), 0, n - 1),
                            axis=0)[0]
    return centre, valide, float(np.median(lu[valide])) if valide.any() else 0.0


def mesurer() -> dict:
    spires = []
    for nom in SPIRES:
        pile = _charger(nom)
        if pile is None:
            continue
        centre, valide, intensite = _suivre(pile)
        c = centre[valide]
        if c.size < 1000:
            continue
        # ⚠ Le pic BRUT est garde a cote : c'est lui qui montre que le filtre est le point.
        brut = np.argmax(pile, axis=0)[valide].astype(float)
        spires.append(dict(
            nom=nom, couches=int(pile.shape[0]),
            par_echelle=ecart_par_echelle(pile),
            part_de_matiere=float(valide.mean()),
            centre_median=float(np.median(c)),
            ecart_type_um=float(c.std() * VOXEL_UM),
            ecart_type_feuilles=float(c.std() * VOXEL_UM / ECART_UM),
            amplitude_um=float((np.percentile(c, 95) - np.percentile(c, 5)) * VOXEL_UM),
            amplitude_feuilles=float((np.percentile(c, 95) - np.percentile(c, 5))
                                     * VOXEL_UM / ECART_UM),
            brut_ecart_type_feuilles=float(brut.std() * VOXEL_UM / ECART_UM),
            intensite_bande=intensite,
            fond=float(np.percentile(pile[:, valide], FOND_PERCENTILE)) if valide.any() else 0.0,
        ))
    if not spires:
        raise SystemExit(
            f"aucune couche sous {COUCHES}\n"
            "  les produire :  uv run python src/volume/zarr_vers_couches.py <clé .zarr> "
            "--sortie data/couches/<nom> --top 900 --left 900 --hauteur 1024 --largeur 1024")

    ecarts = [s["ecart_type_um"] for s in spires]
    erreur_champ, rouleau_champ = _erreur_du_champ(ROULEAU)
    # ⚠⚠ C'est CET ecart-la qui plafonne le champ, pas celui au pixel : le champ agrege sur
    # une cellule du maillage, soit 20 pixels de la dalle.
    echelle_cellule = "20"
    a_l_echelle = [s["par_echelle"][echelle_cellule] for s in spires
                   if echelle_cellule in s.get("par_echelle", {})]
    ecart_cellule = float(np.median(a_l_echelle)) if a_l_echelle else None
    return dict(
        voxel_um=VOXEL_UM, ecart_inter_feuilles_um=ECART_UM, lissage=LISSAGE,
        spires=spires,
        ecart_type_median_um=float(np.median(ecarts)),
        ecart_type_median_feuilles=float(np.median(ecarts) / ECART_UM),
        # ⚠ Le chiffre auquel ce plancher se compare, relu de SA mesure plutot que recopie.
        erreur_du_champ_um=erreur_champ,
        rouleau=ROULEAU,
        rouleau_du_champ=rouleau_champ,
        # ⚠⚠ La decomposition, avec son hypothese ECRITE. Si les deux erreurs sont
        # independantes, celle du champ seul vaut la racine de la difference des carres. Elles
        # ne le sont peut-etre pas -- d'ou les DEUX bornes, qui encadrent sans supposer.
        ecart_a_l_echelle_du_champ_um=ecart_cellule,
        voisines=correlation_entre_voisines(),
        echelle_du_champ_px=int(echelle_cellule),
        erreur_propre_si_independantes_um=(
            float(np.sqrt(max(0.0, erreur_champ ** 2 - (ecart_cellule or 0.0) ** 2)))
            if erreur_champ else None),
        borne_basse_um=(float(max(0.0, erreur_champ - (ecart_cellule or 0.0)))
                        if erreur_champ else None),
        borne_haute_um=erreur_champ,
    )


ROULEAU = "PHerc0172"
"""Le rouleau dont les couches sont ici. ⚠⚠ Nommé parce que j'ai comparé, dans une première
version, les 47 µm du champ de `PHerc0139` aux 28 µm du référent de `PHerc0172` — **deux
rouleaux différents**, à deux tailles de voxel différentes. Le contrôle qui l'aurait attrapé
n'existait pas ; il existe maintenant."""

VOXEL_PAR_ROULEAU = {"PHerc0139": 9.362, "PHerc0172": 7.91}


BLOCS = (1, 4, 20, 51)
"""Les échelles d'agrégation auxquelles l'écart est mesuré, en pixels. ⚠⚠ Une échelle, ce n'est
pas un détail : le champ d'enroulement travaille sur des **médianes de cellule**, pas sur des
pixels, donc c'est l'écart **à cette échelle-là** qui plafonne son erreur. 20 correspond au pas
du maillage `tifxyz` (`scale` 0,05), c'est-à-dire à une cellule du champ."""


def ecart_par_echelle(pile: np.ndarray) -> dict:
    """
    @brief L'écart de la surface à la feuille, mesuré à plusieurs échelles d'agrégation.

    ⚠⚠⚠ Existe parce que ma décomposition était trop optimiste. J'avais opposé les 49 µm du
    champ aux 27 µm du référent **mesurés au pixel**, alors que le champ agrège sur une cellule
    entière. À l'échelle de la cellule, l'écart du référent tombe — donc **une plus petite part**
    des 49 µm lui revient, et l'erreur propre du champ est plus grande que je ne l'avais écrit.
    """
    centre, valide, _ = _suivre(pile)
    out = {}
    for b in BLOCS:
        if b == 1:
            v = centre[valide]
        else:
            h = (centre.shape[0] // b) * b
            w = (centre.shape[1] // b) * b
            moy = centre[:h, :w].reshape(h // b, b, w // b, b).mean(axis=(1, 3))
            couv = valide[:h, :w].reshape(h // b, b, w // b, b).mean(axis=(1, 3))
            # ⚠ Un bloc n'est retenu que s'il est PLEIN de matiere : un bloc a moitie dans le
            # remplissage aurait une moyenne tiree vers le centre de la dalle, ce qui ferait
            # baisser l'ecart pour une raison qui n'a rien a voir avec l'echelle.
            v = moy[couv > 0.9]
        if v.size >= 20:
            out[str(b)] = float(v.std() * VOXEL_UM)
    return out


def correlation_entre_voisines(paires=((61, 62), (62, 63), (63, 64))) -> dict:
    """
    @brief L'écart de la surface à la feuille est-il corrélé d'une spire à sa voisine ?

    ⚠⚠⚠ C'EST CE QUI VALIDE — OU NON — LA DÉCOMPOSITION. L'erreur propre du champ se déduit de
    la sienne et de celle du référent **en supposant qu'elles sont indépendantes**. Si l'écart
    du référent était systématique d'une spire à l'autre, il s'annulerait dans les différences
    que le champ manipule, et la décomposition serait fausse.

    ⚠ Les spires sont appariées par **position dans le monde**, jamais par indice de grille :
    chaque maillage a sa propre origine de paramétrage, et les mêmes (ligne, colonne) tombent à
    des endroits complètement différents — vérifié, `w060` et `w061` diffèrent de 3400 voxels
    en y pour les mêmes indices.
    """
    import glob as _glob

    import tifffile
    from scipy.spatial import cKDTree

    sys.path[:0] = [str(RACINE / "src" / "excision")]
    from le_sens_des_indices import _spires  # noqa: PLC0415

    dossiers = _spires(ROULEAU)
    patches = {}
    for k in sorted({x for paire in paires for x in paire}):
        if k not in dossiers:
            continue
        pile = _charger(f"{ROULEAU}_w{k:03d}")
        if pile is None:
            continue
        centre, valide, _ = _suivre(pile)
        n = pile.shape[0]
        # ⚠ Blocs de 20 : c'est le pas du maillage, donc la grille des `tifxyz` s'y aligne
        # exactement. Un autre facteur demanderait une interpolation, donc une hypothese.
        h = (centre.shape[0] // 20) * 20
        bloc = centre[:h, :h].reshape(h // 20, 20, h // 20, 20).mean(axis=(1, 3))
        couv = valide[:h, :h].reshape(h // 20, 20, h // 20, 20).mean(axis=(1, 3))
        cote = h // 20
        d = dossiers[k]
        coords = []
        for canal in "xyz":
            coords.append(tifffile.imread(d / f"{canal}.tif").astype(np.float64)
                          [45:45 + cote, 45:45 + cote])
        masque = (coords[0] > 0) & (coords[1] > 0) & (couv > 0.9)
        if masque.sum() < 100:
            continue
        patches[k] = (np.c_[coords[0][masque], coords[1][masque], coords[2][masque]],
                      (bloc[masque] - (n - 1) / 2.0) * VOXEL_UM)

    sorties = []
    for a_, b_ in paires:
        if a_ not in patches or b_ not in patches:
            continue
        (pa, sa), (pb, sb) = patches[a_], patches[b_]
        distance, index = cKDTree(pb).query(pa)
        proches = distance < 40
        if proches.sum() < 50:
            continue
        sorties.append(dict(paire=f"w{a_:03d}-w{b_:03d}", appariements=int(proches.sum()),
                            correlation=float(np.corrcoef(sa[proches],
                                                          sb[index[proches]])[0, 1])))
    return dict(paires=sorties,
                correlation_max=max((abs(x["correlation"]) for x in sorties), default=None))


def _erreur_du_champ(rouleau: str) -> tuple[float, str] | tuple[None, None]:
    """
    @brief L'erreur de prédiction du champ à une feuille (`77` §9), pour CE rouleau.

    ⚠ Le nom du rouleau est un argument et non un défaut : c'est la seule façon d'empêcher la
    comparaison inter-rouleaux que j'ai faite une fois.
    """
    suffixe = "" if rouleau == "PHerc0139" else f"_{rouleau}"
    fichier = RACINE / "docs" / "mesures" / f"extraire_la_spire_suivante{suffixe}.json"
    if not fichier.is_file():
        return None, None
    d = json.loads(fichier.read_text())
    if d.get("rouleau") != rouleau:
        return None, None
    serie = d.get("series", {}).get("sans_reinjection") or []
    premier = next((x for x in serie if x["au_dela"] == 1), None)
    if not premier:
        return None, None
    return float(premier["erreur_vx"] * VOXEL_PAR_ROULEAU[rouleau]), rouleau


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    print("la bande de matière est là, et elle est nette une fois suivie")
    # ⚠⚠ SANS CE CONTROLE, tout ce qui suit serait compatible avec « il n'y a pas de signal ».
    # « La surface est mal placee » et « la dalle est du bruit » se distinguent ici.
    for s in r["spires"]:
        v(f"{s['nom']} : la bande ressort du fond",
          s["intensite_bande"] > s["fond"] * 1.1,
          f"{s['intensite_bande']:.0f} contre {s['fond']:.0f} de fond")

    print("l'ESTIMATEUR est le point — intégrer la bande, pas choisir un voxel")
    for s in r["spires"]:
        v(f"{s['nom']} : le centre de masse divise la dispersion par plus de deux",
          s["brut_ecart_type_feuilles"] > 2 * s["ecart_type_feuilles"],
          f"argmax {s['brut_ecart_type_feuilles']:.3f} contre centre de masse "
          f"{s['ecart_type_feuilles']:.3f} (feuilles)")

    print("⭐ et la spire publiée n'est PAS sur la feuille")
    for s in r["spires"]:
        v(f"{s['nom']} : elle s'en écarte d'une fraction notable d'un écart",
          0.05 < s["ecart_type_feuilles"] < 0.45,
          f"{s['ecart_type_um']:.1f} µm = {s['ecart_type_feuilles']:.3f} feuille · "
          f"amplitude {s['amplitude_um']:.0f} µm")
    # ⚠ Deux spires qui s'accordent : sans ca, ce serait la mesure d'UNE spire mal tracee.
    if len(r["spires"]) >= 2:
        a, b = r["spires"][0]["ecart_type_um"], r["spires"][1]["ecart_type_um"]
        v("... et les deux spires s'accordent, donc c'est systématique",
          abs(a - b) < 0.25 * max(a, b), f"{a:.1f} µm contre {b:.1f}")

    print("⭐⭐ ce qui plafonne toute erreur mesurée contre ces spires")
    # ⚠⚠⚠ LE CONTROLE QUI AURAIT ATTRAPE MON ERREUR : les deux chiffres qu'on compose doivent
    # venir du MEME rouleau. J'ai compare une fois 47 µm de `PHerc0139` a 28 µm de
    # `PHerc0172`, a deux tailles de voxel differentes, et rien ne l'a signale.
    v("les deux erreurs comparées viennent du même rouleau",
      r.get("rouleau_du_champ") == r.get("rouleau"),
      f"référent {r.get('rouleau')} · champ {r.get('rouleau_du_champ')}")
    if r["erreur_du_champ_um"]:
        v("l'erreur du champ est du même ordre que celle du référent lui-même",
          r["erreur_du_champ_um"] < 3 * r["ecart_type_median_um"],
          f"champ {r['erreur_du_champ_um']:.0f} µm contre référent "
          f"{r['ecart_type_median_um']:.0f} µm")
        # ⚠⚠ L'ECHELLE, et elle change la reponse : le champ agrege sur une cellule, donc
        # c'est l'ecart a CETTE echelle qui le plafonne. Au pixel il vaut 27 µm, a la cellule
        # 21 -- donc une plus petite part des 49 lui revient que je ne l'avais ecrit.
        v("l'écart décroît avec l'échelle d'agrégation",
          r["ecart_a_l_echelle_du_champ_um"] < r["ecart_type_median_um"],
          f"{r['ecart_a_l_echelle_du_champ_um']:.1f} µm à {r['echelle_du_champ_px']} px "
          f"contre {r['ecart_type_median_um']:.1f} au pixel")
        # ⚠⚠⚠ CE QUI VALIDE LA DECOMPOSITION : sans ca, « independantes » serait une hypothese
        # de confort. Un ecart systematique s'annulerait dans les differences du champ.
        vo = r.get("voisines") or {}
        if vo.get("correlation_max") is not None:
            v("... et l'écart du référent n'est PAS corrélé entre spires voisines",
              vo["correlation_max"] < 0.2,
              " · ".join(f"{x['paire']} {x['correlation']:+.3f}" for x in vo["paires"]))
        v("... donc l'erreur propre du champ est bornée, sans qu'on puisse la mesurer",
          r["borne_basse_um"] < r["erreur_propre_si_independantes_um"] < r["borne_haute_um"],
          f"entre {r['borne_basse_um']:.0f} et {r['borne_haute_um']:.0f} µm, "
          f"{r['erreur_propre_si_independantes_um']:.0f} si indépendantes")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    r = mesurer()
    if not args.verifier or args.json:
        print(f"écart de la spire publiée à la feuille "
              f"(lissage {r['lissage']}×{r['lissage']}, voxel {r['voxel_um']} µm)\n")
        for s in r["spires"]:
            print(f"  {s['nom']:18s} {s['part_de_matiere'] * 100:5.1f} % de matière · "
                  f"σ {s['ecart_type_um']:5.1f} µm ({s['ecart_type_feuilles']:.3f} feuille) · "
                  f"amplitude {s['amplitude_um']:5.1f} µm "
                  f"({s['amplitude_feuilles']:.3f})")
            print(f"  {'':18s} argmax σ {s['brut_ecart_type_feuilles']:.3f} feuille — "
                  f"l'estimateur divise par "
                  f"{s['brut_ecart_type_feuilles'] / s['ecart_type_feuilles']:.1f}")
        if r["erreur_du_champ_um"]:
            print(f"\n  ⭐ sur {r['rouleau']} : le champ prédit à "
                  f"{r['erreur_du_champ_um']:.0f} µm, contre un référent lui-même à "
                  f"{r['ecart_type_median_um']:.0f} µm de la matière")
            print(f"     erreur propre du champ : entre {r['borne_basse_um']:.0f} et "
                  f"{r['borne_haute_um']:.0f} µm · "
                  f"{r['erreur_propre_si_independantes_um']:.0f} si indépendantes")

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
