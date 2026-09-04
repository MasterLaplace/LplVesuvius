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
import pathlib
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
COUCHES = RACINE / "data" / "couches"

SPIRES = ("PHerc0172_w060", "PHerc0172_w061", "PHerc0172_w062",
          "PHerc0172_w063", "PHerc0172_w064", "PHerc0172_w078",
          "1447_20250702235910", "1447_20250703025628", "1447_20250703034159",
          "PHerc1447_20250702235910", "PHerc1447_complet",
          "PHercParis4_w010-027")
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

REGIMES = {"PHerc0172": (7.91, 147.4), "PHerc1447": (8.64, 113.0),
           "PHercParis4": (7.91, 173.0)}
"""Par rouleau : la taille de voxel et l'écart inter-feuilles. ⚠ `PHerc1447` est là parce que
c'est le rouleau sur lequel `44` a mesuré la dérive de la chaîne de spires — sans lui, la
correction de budget du §10 serait transportée d'un rouleau à l'autre sans preuve.

⚠ Les 173 µm de `PHercParis4` viennent de `16` (médiane mesurée), **pas** d'une estimation :
ma première version y avait écrit 148, un nombre que je n'avais mesuré nulle part. Et son voxel
est **7,91 µm**, lu dans le `meta.json` du volume que son `meta.json` de segment déclare —
ses deux volumes publiés sont à 7,91.

⚠⚠ Les 113 µm de `PHerc1447` sont ceux de `44` §4, et `77` §10 montre justement qu'ils sont
une distance au plus proche voisin **entre surfaces**, pas un écart centre à centre. Ils sont
gardés ici parce que la dérive à corriger est exprimée dans cette même unité : corriger un
budget suppose de rester dans l'unité où il a été compté."""

VOXEL_UM = 7.91
ECART_UM = 147.4
"""Le régime par défaut, celui de `PHerc0172` (`76`)."""


def _rouleau_de(nom: str) -> str:
    """
    @brief Le rouleau auquel appartient une pile, quel que soit le nom du dossier.

    ⚠ Les dossiers de `data/couches/` sont nommés à la main, donc le même rouleau y apparaît
    sous `1447_…` et `PHerc1447_…`. Découper sur le premier `_` en ferait **deux** rouleaux, et
    une médiane par rouleau compterait alors deux fois le même régime.
    """
    for rouleau in REGIMES:
        if nom.startswith(rouleau) or nom.startswith(rouleau.replace("PHerc", "")):
            return rouleau
    return "?"


def _regime(nom: str) -> tuple[float, float]:
    """
    @brief Le voxel et l'écart inter-feuilles du rouleau auquel appartient une pile.
    """
    rouleau = _rouleau_de(nom)
    return REGIMES.get(rouleau, (VOXEL_UM, ECART_UM))


def _empreinte(nom: str) -> str | None:
    """
    @brief Une empreinte du contenu d'une pile, pour ne pas compter deux fois la même.

    ⚠⚠ Existe parce que `data/couches/` porte le MÊME segment sous deux noms
    (`1447_20250702235910` et `PHerc1447_complet`, empreinte identique). Les compter tous deux
    donnerait deux fois son poids à un segment dans la médiane — un doublon silencieux, du
    genre qu'aucune assertion sur la valeur ne peut attraper.
    """
    import hashlib
    fichiers = sorted(glob.glob(str(COUCHES / nom / "*.tif")))
    if not fichiers:
        return None
    return hashlib.md5(pathlib.Path(fichiers[0]).read_bytes()).hexdigest()

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


COPIES_EN_POINTE = 3
"""Combien d'exemplaires de la pile vivent au pire moment : la pile, le tableau de poids, et
une marge pour les intermédiaires de `_suivre`. ⚠ Compté et non deviné — c'est ce qui transforme
« combien pèse la pile » en « combien la machine doit avoir »."""

PART_DE_LA_RAM = 0.35
"""La part de la mémoire disponible qu'on s'autorise à la pointe. ⚠ Une part et non un nombre
de gibioctets : un budget en dur serait juste sur la machine où il a été écrit et faux partout
ailleurs — trop grand sur un portable, absurdement petit sur un serveur."""


def budget_memoire_mo() -> float:
    """
    @brief Ce qu'une pile a le droit de peser une fois chargée, dérivé de la RAM disponible.

    ⚠ Dérivé à l'exécution : la même valeur en dur serait fausse sur une autre machine, et
    c'est exactement le genre de constante qu'on ne repense jamais.
    """
    dispo_mo = 4096.0
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for ligne in f:
                if ligne.startswith("MemAvailable:"):
                    dispo_mo = float(ligne.split()[1]) / 1024
                    break
    except OSError:
        pass
    return dispo_mo * PART_DE_LA_RAM / COPIES_EN_POINTE


BUDGET_MEMOIRE_MO = None
"""Laissé à `None` : le budget se calcule. ⚠ Le nom est gardé parce que des appels le passent.

⚠⚠⚠ CE GARDE EXISTE PARCE QUE SON ABSENCE A FAIT TOMBER LA MACHINE DE L'AUTEUR. `_charger`
faisait `np.stack([...]).astype(np.float32)` sans regarder la taille : une liste de couches,
puis une copie empilée, puis une copie en flottant — **trois exemplaires, dont un ×4**. Sur les
spires de `PHerc0172` (33 × 1024², soit 138 Mio en flottant) c'est sans conséquence ; sur un
segment publié de `PHerc1447`, qui pèse **3,3 Gio en 31 couches**, ça demande une trentaine de
gibioctets et le système meurt.

⭐ Le remède n'est pas de lancer l'outil sous une limite mémoire — ça déplace le problème chez
l'appelant, qui ne connaît pas la taille — mais que l'outil **regarde avant de charger** et
**refuse en disant quoi faire**. Une couche suffit pour connaître la forme des trente et une.

⚠ Et le refus est explicite plutôt que silencieux : rendre `None` ferait disparaître la spire
du tableau, ce qui se lit comme « pas de données » et non comme « trop grosse »."""


def _cout_en_mo(fichiers: list[str]) -> float:
    """
    @brief Ce que pèserait la pile en mémoire, lu sur UNE couche.
    """
    import tifffile
    une = tifffile.imread(fichiers[0])
    return len(fichiers) * une.size * 4 / (1024 * 1024)


def _charger(nom: str, budget_mo: float | None = None,
             bruyant: bool = True) -> np.ndarray | None:
    """
    @brief La pile de couches d'une spire, en flottant — ou rien si elle ne tient pas.
    """
    fichiers = sorted(glob.glob(str(COUCHES / nom / "*.tif")))
    if len(fichiers) < 8:
        return None
    budget = budget_mo if budget_mo is not None else budget_memoire_mo()
    cout = _cout_en_mo(fichiers)
    if cout > budget:
        if bruyant:
            print(f"  ⚠ {nom} : {cout / 1024:.1f} Gio une fois chargée, au-dessus du budget "
                  f"de {budget / 1024:.1f} Gio — SAUTÉE.\n"
                  f"    la mesurer quand même : découper une fenêtre avec "
                  f"`src/volume/zarr_vers_couches.py --hauteur 1024 --largeur 1024`",
                  file=sys.stderr)
        return None
    import tifffile
    # ⚠ Alloue la pile UNE fois et la remplit couche par couche : `np.stack` d'une liste
    # garde la liste ET la pile en vie le temps de la copie, donc double la pointe.
    une = tifffile.imread(fichiers[0])
    pile = np.empty((len(fichiers), *une.shape), dtype=np.float32)
    pile[0] = une
    del une
    for i, f in enumerate(fichiers[1:], start=1):
        pile[i] = tifffile.imread(f)
    return pile


def _suivre(pile: np.ndarray, lissage: int = LISSAGE,
            demi_fenetre: int | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    """
    @brief Le centre de masse en profondeur de la bande de matière, colonne par colonne.

    ⚠⚠⚠ `demi_fenetre` BORNE LA RECHERCHE À UNE SEULE FEUILLE, ET SON ABSENCE A GONFLÉ UN
    CHIFFRE PUBLIÉ. Les dalles rendues ici couvrent **1,8 à 3,0 écarts inter-feuilles**, donc
    9 des 12 contiennent **deux à quatre** feuilles — vérifié en comptant les lobes du profil.
    Un centre de masse pris sur toute la dalle enjambe alors plusieurs lobes et atterrit **dans
    le creux entre eux**, c'est-à-dire dans l'interstice, ce qui gonfle l'écart mesuré.

    Mesuré : la borne à ±0,5 écart fait tomber l'écart de **25 à 37 %** sur les douze piles, et
    ramène `PHercParis4` de 37,7 à 23,8 µm — il n'était pas un rouleau à part, c'était mon
    estimateur qui enjambait deux feuilles de plus que les autres.

    ⚠ La borne est un **demi-écart**, pas un réglage : c'est la plus grande fenêtre qui ne peut
    pas contenir deux feuilles. La choisir plus petite améliorerait le chiffre sans raison.

    Rend le centre de masse, le masque des colonnes qui portent de la matière, et l'intensité
    médiane lue au centre de masse.
    """
    from scipy.ndimage import uniform_filter

    n_total = pile.shape[0]
    # ⚠ « Il y a de la matiere ici » se lit sur la VARIATION en profondeur autant que sur le
    # niveau : une colonne de remplissage est plate, pas forcement nulle (piege nº 27).
    valide = (pile.max(0) > 0) & (pile.std(0) > 2)
    decalage = 0
    if demi_fenetre is not None:
        centre = n_total // 2
        a_, b_ = max(0, centre - demi_fenetre), min(n_total, centre + demi_fenetre + 1)
        pile, decalage = pile[a_:b_], a_
    n = pile.shape[0]
    # ⚠ `uniform_filter` de taille 1 est l'identite, mais il COPIE quand meme -- un doublement
    # de la pointe memoire pour rien. Avec `LISSAGE = 1` (le defaut mesure), on ne l'appelle pas.
    lisse = (pile if lissage <= 1
             else uniform_filter(pile, size=(1, lissage, lissage)))
    seuil = float(np.percentile(lisse[:, valide], FOND_PERCENTILE)) if valide.any() else 0.0
    poids = np.clip(lisse - seuil, 0, None)
    z = np.arange(n)[:, None, None] + decalage
    centre = (poids * z).sum(0) / np.clip(poids.sum(0), 1e-9, None)
    lu = np.take_along_axis(
        lisse, np.clip(np.round(centre)[None].astype(int) - decalage, 0, n - 1), axis=0)[0]
    return centre, valide, float(np.median(lu[valide])) if valide.any() else 0.0


def mesurer() -> dict:
    spires = []
    vues: dict[str, str] = {}
    for nom in SPIRES:
        empreinte = _empreinte(nom)
        if empreinte and empreinte in vues:
            print(f"  ⚠ {nom} : même contenu que {vues[empreinte]} — non recompté.",
                  file=sys.stderr)
            continue
        if empreinte:
            vues[empreinte] = nom
        voxel, ecart = _regime(nom)
        pile = _charger(nom)
        # ⚠ La borne vaut UN DEMI-ECART, exprimee en couches du regime de CE rouleau.
        demi_fenetre = int(round(ecart / voxel / 2))
        if pile is None:
            continue
        centre, valide, intensite = _suivre(pile, demi_fenetre=demi_fenetre)
        c = centre[valide]
        if c.size < 1000:
            continue
        # ⚠ Le pic BRUT est garde a cote : c'est lui qui montre que le filtre est le point.
        brut = np.argmax(pile, axis=0)[valide].astype(float)
        spires.append(dict(
            nom=nom, rouleau=_rouleau_de(nom), voxel_um=voxel, ecart_um=ecart,
            couches=int(pile.shape[0]),
            par_echelle=ecart_par_echelle(pile, voxel),
            part_de_matiere=float(valide.mean()),
            centre_median=float(np.median(c)),
            ecart_type_um=float(c.std() * voxel),
            ecart_type_feuilles=float(c.std() * voxel / ecart),
            amplitude_um=float((np.percentile(c, 95) - np.percentile(c, 5)) * voxel),
            amplitude_feuilles=float((np.percentile(c, 95) - np.percentile(c, 5))
                                     * voxel / ecart),
            brut_ecart_type_feuilles=float(brut.std() * voxel / ecart),
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
        correction_du_budget=correction_du_budget(spires),
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


def ecart_par_echelle(pile: np.ndarray, voxel: float = VOXEL_UM) -> dict:
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
            out[str(b)] = float(v.std() * voxel)
    return out


def correlation_entre_voisines(paires=((61, 62), (62, 63), (63, 64)),
                               voxel: float = VOXEL_UM) -> dict:
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
                      (bloc[masque] - (n - 1) / 2.0) * voxel)

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


VOXEL_DES_ROULEAUX = {2.4: "PHercParis4", 7.91: "PHerc0172", 8.64: "PHerc1447",
                      9.362: "PHerc0139"}
"""Quel rouleau derrière quelle taille de voxel. ⚠ Sert à **identifier** le rouleau d'une
mesure au lieu de le supposer — voir `correction_du_budget`."""


def correction_du_budget(spires: list[dict] | None = None) -> dict:
    """
    @brief De combien l'écart de la chaîne de spires (`44`) est gonflé par l'erreur du référent.

    ⭐⭐ C'EST LA SEULE CHOSE NEUVE QUE CETTE MESURE APPORTE À `44`. Cette dérive est mesurée
    **contre la surface publiée**, et `77` §10 établit que cette surface est elle-même à ~25 µm
    de la matière. Le budget de la chaîne est donc gonflé, et le seuil « même feuille » de 40 µm
    est franchi **plus tard** qu'annoncé.

    ⚠⚠⚠ ET LA FONCTION REFUSE D'APPLIQUER LA CORRECTION SI ELLE N'A PAS MESURÉ CE ROULEAU-LÀ.
    J'avais écrit dans le registre que `44` mesure sur `PHerc1447` ; c'est **`PHercParis4`**, ce
    que dit son `um_par_voxel` de 2,4. Aucun volume de surface de son segment de référence n'est
    publié sur le bucket ouvert, donc l'erreur du référent n'y est **pas** mesurée. La
    correction reste une **conjecture**, appuyée sur deux autres rouleaux — et c'est dit ici
    plutôt que dans une prose qu'on peut oublier de lire.
    """
    fichier = RACINE / "docs" / "mesures" / "couverture_publiee.json"
    if not fichier.is_file():
        return {}
    d = json.loads(fichier.read_text())
    voxel = float(d.get("um_par_voxel", 0.0))
    rouleau = VOXEL_DES_ROULEAUX.get(voxel)

    # ⚠⚠⚠ LA PROVENANCE DE CE VOXEL N'EST PAS RECONSTRUCTIBLE, et c'est un fait sur `44`, pas
    # sur ce fichier. `couverture_publiee.py` pose `UM_PAR_VOXEL = 2.4` en le justifiant par
    # « la convention de `chainer_tangentiel.sh` » et par une cohérence INTERNE (le maillon 20
    # rapporte 800 voxels et le document lit 1920 µm) — jamais contre le voxel déclaré d'un
    # volume. Or son répertoire de référence, `publie_20230702185753`, porte le nom d'un
    # segment de `PHercParis4`, dont les DEUX volumes publiés sont à **7,91 µm** (lu dans leurs
    # `meta.json`), et son propre `meta.json` est dépouillé (`uuid: out`).
    #
    # Conséquence : tous les micromètres du tableau de couverture de `44` reposent sur une
    # constante que rien ne relie à un volume. On le DIT au lieu de composer avec.
    maillons = d.get("maillons") or []
    if not maillons:
        return {}
    dernier = maillons[-1]
    ecart_um = abs(float(dernier["ecart_signe_median_vox"])) * voxel

    # ⚠ Les spires sont PASSEES et non recalculees : `mesurer` appelle cette fonction, donc
    # l'appel inverse ferait une recursion infinie. Le defaut a `None` garde l'appel direct
    # possible depuis un terminal, au prix d'une mesure de plus.
    mesures = spires if spires is not None else mesurer()["spires"]
    par_rouleau: dict[str, list[float]] = {}
    for sp in mesures:
        par_rouleau.setdefault(sp["rouleau"], []).append(sp["ecart_type_um"])
    # ⚠ On cherche le rouleau de LA CHAINE, pas « un rouleau quelconque ».
    dispo = next((v for k, v in par_rouleau.items()
                  if rouleau and (k.startswith(rouleau) or rouleau.endswith(k))), None)

    referents = {k: float(np.median(v)) for k, v in par_rouleau.items()}
    referent = float(np.median(dispo)) if dispo else None
    # ⭐ Et en unités de FEUILLE, le référent est transportable d'un rouleau à l'autre : les
    # trois mesurés donnent 0,16 à 0,25 écart inter-feuilles, à trois tailles de voxel. C'est
    # la forme sous laquelle la correction VOYAGE, quand les micromètres ne le peuvent pas.
    en_feuilles = [sp["ecart_type_feuilles"] for sp in mesures]
    return dict(
        rouleau_de_la_chaine=rouleau, voxel_um=voxel,
        provenance_du_voxel_reconstructible=False,
        referent_en_feuilles=float(np.median(en_feuilles)) if en_feuilles else None,
        referent_en_feuilles_min=float(min(en_feuilles)) if en_feuilles else None,
        referent_en_feuilles_max=float(max(en_feuilles)) if en_feuilles else None,
        rouleaux_mesures=sorted({sp["rouleau"] for sp in mesures}),
        parcouru_um=float(dernier.get("parcouru_um", 0.0)),
        ecart_mesure_um=ecart_um,
        referent_mesure_sur_ce_rouleau=referent is not None,
        referents_par_rouleau=referents,
        # ⚠ Rendu QUAND MEME, mais nomme comme une conjecture : c'est la moitie utile, et la
        # cacher parce qu'elle n'est pas mesuree sur le bon rouleau reviendrait a ne rien dire.
        referent_conjecture_um=float(np.median(list(referents.values()))) if referents else None,
        ecart_corrige_conjecture_um=(
            float(np.sqrt(max(0.0, ecart_um ** 2
                              - float(np.median(list(referents.values()))) ** 2)))
            if referents else None),
    )


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
        # ⚠⚠⚠ ET CE CONTROLE A CHANGE DE SENS QUAND L'ESTIMATEUR A ETE BORNE A UNE FEUILLE.
        # Il disait « l'ecart DECROIT avec l'agregation », donc qu'une part etait du bruit de
        # pixel : au pixel 27 µm, a la cellule 21. Une fois le centre de masse empeche
        # d'enjamber deux feuilles, il ne decroit plus (19,2 au pixel contre 19,9 a 20 px).
        #
        # ⭐ Ce n'est pas une regression, c'est un renforcement : ce qui decroissait etait le
        # BIAIS d'enjambement, qui se moyennait sur une cellule. Ce qui reste est un
        # deplacement REEL et spatialement COHERENT de la surface -- exactement ce qu'un
        # traceur pourrait corriger, et exactement ce que du bruit ne serait pas.
        ecart_relatif = abs(r["ecart_a_l_echelle_du_champ_um"]
                            - r["ecart_type_median_um"]) / r["ecart_type_median_um"]
        v("l'écart ne décroît PAS avec l'agrégation — il est spatialement cohérent",
          ecart_relatif < 0.15,
          f"{r['ecart_a_l_echelle_du_champ_um']:.1f} µm à {r['echelle_du_champ_px']} px "
          f"contre {r['ecart_type_median_um']:.1f} au pixel, soit {ecart_relatif * 100:.0f} % d'écart")
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

    cb = r.get("correction_du_budget") or {}
    if cb:
        print("⭐ ce que ça corrige à la dérive de la chaîne de `44` — et ce que ça ne corrige pas")
        # ⚠⚠⚠ LE CONTROLE QUI AURAIT ATTRAPE MA CONFUSION. J'avais ecrit dans le registre que
        # `44` mesure sur `PHerc1447` ; c'est `PHercParis4`, et son `um_par_voxel` de 2,4 le
        # dit. Identifier le rouleau plutot que le supposer est ce qui rend le reste lisible.
        v("le rouleau de la chaîne est identifié, pas supposé",
          cb.get("rouleau_de_la_chaine") is not None,
          f"{cb.get('rouleau_de_la_chaine')} · voxel {cb.get('voxel_um')} µm")
        # ⭐⭐⭐ CE CONTROLE A FAIT EXACTEMENT CE POUR QUOI IL A ETE ECRIT. Il disait « le
        # referent n'est PAS mesure sur ce rouleau, donc c'est une conjecture », avec la note
        # qu'il tomberait le jour ou un volume de `PHercParis4` deviendrait disponible. Il est
        # tombe le meme jour : l'auteur a demande « t'es vraiment sur que c'est pas stocke
        # quelque part ? », et ça l'etait -- sur `dl.ash2txt.org`, l'autre serveur.
        v("le référent EST mesuré sur le rouleau de la chaîne",
          cb.get("referent_mesure_sur_ce_rouleau") is True,
          f"référents mesurés sur : {', '.join(sorted(cb.get('referents_par_rouleau', {})))}")
        v("la correction va dans le bon sens et reste modeste",
          cb.get("ecart_corrige_conjecture_um") is not None
          and 0.8 * cb["ecart_mesure_um"] < cb["ecart_corrige_conjecture_um"]
          < cb["ecart_mesure_um"],
          f"{cb['ecart_mesure_um']:.1f} µm → {cb['ecart_corrige_conjecture_um']:.1f} µm")
        # ⚠ Deux rouleaux qui s'accordent : c'est ce qui rend la conjecture defendable plutot
        # que gratuite. Un seul rouleau ne dirait rien de PHercParis4.
        # ⚠⚠ L'accord se juge en FEUILLES et non en micrometres : trois rouleaux a trois
        # tailles de voxel donnent 22 a 38 µm, ce qui a l'air d'un desaccord, et 0,16 a 0,25
        # feuille, ce qui est le meme fait. Ma premiere version comparait les micrometres et
        # echouait -- pour la bonne raison.
        v("... et l'accord entre rouleaux se lit en FEUILLES, pas en micromètres",
          cb.get("referent_en_feuilles_max") is not None
          and cb["referent_en_feuilles_max"] < 2 * cb["referent_en_feuilles_min"],
          " · ".join(f"{x:.1f} µm" for x in cb.get("referents_par_rouleau", {}).values())
          + f" → {cb['referent_en_feuilles_min']:.3f}–{cb['referent_en_feuilles_max']:.3f} feuille")
        # ⚠⚠⚠ Le controle qui empeche de composer des micrometres a travers un voxel dont on
        # ne sait pas d'ou il vient. Il est ecrit dans le sens « ce n'est PAS reconstructible » :
        # le jour ou `44` nommera son volume, il tombera, et il faudra passer la conjecture en
        # mesure.
        v("la provenance du voxel de `44` n'est PAS reconstructible — donc on ne compose pas",
          cb.get("provenance_du_voxel_reconstructible") is False,
          f"{cb.get('voxel_um')} µm justifié par cohérence interne, "
          f"pas contre un volume déclaré")
        # ⭐ Ce qui VOYAGE quand les micrometres ne le peuvent pas.
        v("... mais le référent est transportable en unités de FEUILLE",
          cb.get("referent_en_feuilles") is not None
          and cb["referent_en_feuilles_max"] < 2 * cb["referent_en_feuilles_min"],
          f"{cb['referent_en_feuilles_min']:.3f} à {cb['referent_en_feuilles_max']:.3f} "
          f"feuille sur {len(cb['rouleaux_mesures'])} rouleaux")

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
