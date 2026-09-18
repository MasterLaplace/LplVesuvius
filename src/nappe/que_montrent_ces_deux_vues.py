"""Que montrent ces deux vues — et l'axe que j'appelle profondeur en est-il une ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST UNE OBJECTION DE L'AUTEUR QUI L'OUVRE. Devant la planche de
`196` il a dit : « ça ressemble encore à une vue axiale, pas au résultat déplié ». `195` et `196` ont
publié deux vues de trente cubes en AFFIRMANT ce que leurs axes signifient — « la couche du milieu »,
« la coupe en profondeur » — et **rien dans la chaîne ne l'a jamais mesuré**. Le dépôt lit des
`surface-volumes` de segment : leur premier axe est censé traverser l'empilement des feuillets et les
deux autres porter la surface DÉPLIÉE. Censé.

⭐⭐⭐⭐ DEUX QUESTIONS, DÉCLARÉES AVANT DE REGARDER, ET LA SECONDE SERT LE GRAAL DIRECTEMENT :
1. **QUEL AXE TRAVERSE L'EMPILEMENT ?** Le pas d'un pli est connu — `PAS_UM` — donc un axe qui
   traverse la pile porte une PÉRIODE près de ce pas, et les deux autres non. Mesuré par
   autocorrélation, jugé contre le MÉLANGE du profil, sur les trois axes.
2. **LA SURFACE DÉPLIÉE SUIT-ELLE SON FEUILLET ?** Si le maillage du segment tenait le feuillet, une
   coupe en profondeur montrerait des bandes HORIZONTALES. Leur serpentement est exactement l'écart
   que le déroulage doit corriger, et il se mesure en fractions de pli.

⚠⚠⚠ LA SECONDE QUESTION N'EST PAS UNE RECHERCHE : elle ne cherche aucun observable et ne juge
aucune étiquette. C'est une DESCRIPTION de l'instrument, et elle est là parce que deux tranches
publiées reposent dessus sans l'avoir vérifiée.

Usage :
    uv run python src/nappe/que_montrent_ces_deux_vues.py --verifier
    uv run python src/nappe/que_montrent_ces_deux_vues.py \\
        --json docs/mesures/que_montrent_ces_deux_vues.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from combien_dinterstices_traverses import PAS_UM, VOXEL_FIN_UM  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS, les_volumes  # noqa: E402
from ou_le_chunk_se_trouve_t_il import les_etiquettes  # noqa: E402
from ouvrir_les_quinze import _rng, les_cubes  # noqa: E402
from regarder_dans_la_profondeur import (GRAINE, la_rangee_montree,  # noqa: E402
                                         les_tuiles_declarees, une_section)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"

# ⚠⚠ LE PAS D'UN PLI EN VOXELS EST DERIVE, PAS CHOISI : c'est la seule echelle que la matiere impose,
# et c'est elle qui dit si une periode mesuree est celle de l'empilement ou autre chose.
PAS_EN_VOXELS = PAS_UM / VOXEL_FIN_UM

# ⚠⚠⚠ LES TROIS AXES SONT DECLARES DANS L'ORDRE DU TABLEAU, et les trois sont mesures : ne mesurer
# que celui qu'on croit etre le bon serait une verification incapable d'echouer.
LES_TROIS_AXES = ("la profondeur", "la hauteur", "la largeur")

# ⚠⚠ LA PLAGE DE RECALAGE EST LA DEMI-PERIODE, ET C'EST UNE BORNE, PAS UN REGLAGE : au-dela, un
# decalage se confond avec le decalage d'un pli entier. La limite est nommee plutot que tue.
DEMI_PAS_EN_VOXELS = int(round(PAS_EN_VOXELS / 2.0))
LES_DECILES = (10.0, 90.0)


def le_profil(bloc: np.ndarray, axe: int) -> np.ndarray:
    """La moyenne du cube le long des DEUX autres axes — un profil par axe."""
    b = np.asarray(bloc, dtype=float)
    autres = tuple(i for i in range(b.ndim) if i != int(axe))
    return b.mean(axis=autres)


def lautocorrelation(profil: np.ndarray) -> np.ndarray:
    """L'autocorrélation d'un profil centré, normalisée PAR LE RECOUVREMENT de chaque décalage.

    ⚠⚠⚠ LA NORMALISATION PAR LE RECOUVREMENT EST LA CORRECTION D'UN VRAI DEFAUT, ET UNE SONDE L'A
    DIT : divisee par la norme entiere, l'autocorrelation d'une onde de periode quarante culminait
    au decalage DEUX, parce qu'un decalage court somme plus de termes qu'un decalage long. La
    fonction rendait donc « periode 2 » sur une matiere dont la periode etait posee.
    """
    x = np.asarray(profil, dtype=float)
    x = x - x.mean()
    n = len(x)
    d = float(np.dot(x, x)) / float(n)
    if d <= 0.0:
        return np.zeros(n)
    return np.array([(float(np.dot(x[:n - k], x[k:])) / float(n - k)) / d
                     for k in range(n)] + [], dtype=float)


def le_premier_passage_a_zero(a: np.ndarray, defaut: int = 2) -> int:
    """Le premier décalage où l'autocorrélation cesse d'être positive.

    ⭐ C'EST CE QUI SEPARE UNE PERIODE D'UNE SIMPLE DECROISSANCE : avant ce passage, la courbe ne
    fait que descendre depuis un, et son maximum n'y designe rien. La borne est DERIVEE de la
    courbe, jamais choisie.
    """
    for k in range(1, len(a)):
        if a[k] <= 0.0:
            return k
    return int(defaut)


def la_periode_dominante(profil: np.ndarray) -> dict:
    """Le décalage, après le premier passage à zéro, où l'autocorrélation culmine.

    ⚠⚠ LA PLAGE HAUTE EST DERIVEE AUSSI : un decalage n'est estimable que si un QUART du profil se
    recouvre encore, donc elle s'arrete aux trois quarts de la longueur. Sans cela, la periode d'un
    pli — soixante-douze voxels sur cent neuf couches — serait hors d'atteinte par construction.
    """
    x = np.asarray(profil, dtype=float)
    if len(x) < 8:
        return {"decidable": False, "raison": "profil trop court"}
    a = lautocorrelation(x)
    if float(np.max(np.abs(a))) <= 0.0:
        return {"decidable": False, "raison": "profil plat"}
    bas = le_premier_passage_a_zero(a)
    haut = int(round(0.75 * len(a)))
    if haut <= bas:
        return {"decidable": False, "raison": "aucune plage estimable après le passage à zéro"}
    # ⚠⚠⚠ LE PREMIER MAXIMUM LOCAL, ET NON LE PLUS GRAND, ET UNE SONDE L'A IMPOSE : une onde de
    # periode quarante sur quatre cents points culmine AUTANT a quarante qu'a quatre-vingts ou a
    # deux cents, donc un argmax global rendait « periode 200 ». La periode fondamentale est le PLUS
    # PETIT decalage ou le profil se repete ; les multiples sont ses harmoniques.
    k = None
    for j in range(bas + 1, haut - 1):
        if a[j] >= a[j - 1] and a[j] > a[j + 1]:
            k = j
            break
    if k is None:
        k = int(np.argmax(a[bas:haut])) + bas
    return {"decidable": True, "la_periode_en_voxels": int(k),
            "le_premier_passage_a_zero": int(bas),
            "lautocorrelation": round(float(a[k]), 6),
            "la_periode_en_um": round(float(k) * VOXEL_FIN_UM, 4)}


def contre_le_melange_du_profil(profil: np.ndarray, tirages: int = PERMUTATIONS,
                                graine: int = GRAINE) -> dict:
    """La période observée dépasse-t-elle celle de tous les mélanges du même profil ?

    ⭐⭐⭐⭐ C'EST LA STATISTIQUE DE FAMILLE DE `176` ET DE `179` : le maximum de l'autocorrélation
    est cherché sur toute la plage, donc il se paie — et le MÉLANGE le cherche sur la même plage,
    avec exactement les mêmes occasions. Un profil sans période le dépasse une fois sur vingt.
    """
    obs = la_periode_dominante(profil)
    if not obs.get("decidable"):
        return {**obs}
    r = _rng(graine)
    x = np.asarray(profil, dtype=float)
    pics = []
    for _ in range(int(tirages)):
        m = la_periode_dominante(x[r.permutation(len(x))])
        pics.append(float(m["lautocorrelation"]) if m.get("decidable") else -1.0)
    plus_grands = int(sum(1 for p in pics if p >= float(obs["lautocorrelation"])))
    return {**obs, "tirages": int(tirages),
            "lautocorrelation_mediane_du_nul": round(float(np.median(pics)), 6),
            "les_melanges_au_moins_aussi_forts": plus_grands,
            "elle_depasse_tous_les_melanges": plus_grands == 0}


def le_serpentement(section: np.ndarray, plage: int = DEMI_PAS_EN_VOXELS,
                    deciles=LES_DECILES) -> dict:
    """De combien la pile se DÉPLACE en profondeur d'une colonne à l'autre de la coupe.

    ⭐⭐⭐⭐ C'EST LA QUANTITÉ QUE LE DÉROULAGE DOIT CORRIGER, et la chaîne ne l'avait pas. Si le
    maillage du segment tenait son feuillet, chaque colonne aurait le même profil en profondeur et
    tous les décalages vaudraient zéro ; leur étalement EST l'écart à corriger.

    ⚠⚠ LE DECALAGE EST ESTIME PAR RECALAGE SUR LE PROFIL MOYEN DE LA COUPE, et non en suivant la
    bande la plus claire : un argmax par colonne saute d'une bande a l'autre des qu'il y en a deux,
    et le saut ressemble alors a un serpentement geant.

    ⚠⚠⚠ ET LA LIMITE EST NOMMEE : un decalage superieur a la DEMI-PERIODE se confond avec celui
    d'un pli entier. Ce qui est mesure est donc borne par construction, et le compte de colonnes qui
    SATURENT est publie a cote — sans lui, une pile tres inclinee rendrait un petit serpentement.
    """
    s = np.asarray(section, dtype=float)
    if s.ndim != 2 or s.shape[0] < 4 or s.shape[1] < 2:
        return {"decidable": False, "raison": "coupe trop petite"}
    p = int(min(int(plage), (s.shape[0] - 1) // 2))
    if p < 1:
        return {"decidable": False, "raison": "plage de recalage nulle"}
    moyen = s.mean(axis=1)
    moyen = moyen - moyen.mean()
    if float(np.dot(moyen, moyen)) <= 0.0:
        return {"decidable": False, "raison": "profil moyen plat"}
    decalages = []
    for c in range(s.shape[1]):
        col = s[:, c] - s[:, c].mean()
        if float(np.dot(col, col)) <= 0.0:
            decalages.append(0)
            continue
        scores = []
        for k in range(-p, p + 1):
            a = moyen[max(0, k):len(moyen) + min(0, k)]
            b = col[max(0, -k):len(col) + min(0, -k)]
            scores.append(float(np.dot(a, b)) / max(1, len(a)))
        decalages.append(int(np.argmax(scores)) - p)
    d = np.asarray(decalages, dtype=float)
    bas, haut = (float(np.percentile(d, deciles[0])), float(np.percentile(d, deciles[1])))
    satures = int(np.sum(np.abs(d) >= p))
    return {"decidable": True, "colonnes": int(s.shape[1]), "la_plage": int(p),
            "le_serpentement_en_voxels": round(haut - bas, 4),
            "le_serpentement_en_plis": round((haut - bas) / PAS_EN_VOXELS, 6),
            "lecart_maximal_en_voxels": int(np.max(d) - np.min(d)),
            "les_colonnes_saturees": satures,
            "la_part_saturee": round(satures / float(s.shape[1]), 6)}


def un_suivi_par_la_bande_la_plus_claire(section: np.ndarray) -> dict:
    """La règle RÉFUTÉE, portée comme contrôle nommé : suivre la bande la plus claire.

    ⚠⚠⚠ ELLE EST ICI PARCE QU'ELLE EST LA PREMIERE QUI VIENT A L'ESPRIT, ET QU'ELLE EST FAUSSE : sur
    une coupe qui porte deux bandes, l'argmax d'une colonne saute de l'une a l'autre, et le saut se
    lit comme un serpentement geant sur une pile parfaitement plate. Le dire avec un chiffre MESURE
    vaut mieux que de le dire avec un chiffre de sonde.
    """
    s_ = np.asarray(section, dtype=float)
    if s_.ndim != 2 or s_.shape[1] < 2:
        return {"decidable": False, "raison": "coupe trop petite"}
    d = np.asarray([int(np.argmax(s_[:, c])) for c in range(s_.shape[1])], dtype=float)
    bas, haut = (float(np.percentile(d, LES_DECILES[0])), float(np.percentile(d, LES_DECILES[1])))
    return {"decidable": True, "le_serpentement_en_voxels": round(haut - bas, 4),
            "le_serpentement_en_plis": round((haut - bas) / PAS_EN_VOXELS, 6)}


def une_pile(couches: int, largeur: int, periode: float = PAS_EN_VOXELS,
             pente: float = 0.0, bruit: float = 0.0, graine: int = GRAINE) -> np.ndarray:
    """Une pile de feuillets, éventuellement inclinée — la fixture des deux questions."""
    r = _rng(graine)
    z = np.arange(int(couches), dtype=float)[:, None]
    x = np.arange(int(largeur), dtype=float)[None, :]
    s = 120.0 + 40.0 * np.cos(2.0 * np.pi * (z - float(pente) * x) / float(periode))
    if bruit > 0.0:
        s = s + r.normal(0.0, float(bruit), size=s.shape)
    return s


def un_cube(couches: int, hauteur: int, largeur: int, periode: float = PAS_EN_VOXELS,
            graine: int = GRAINE) -> np.ndarray:
    """Un cube dont SEUL le premier axe porte la période — la fixture de la première question."""
    r = _rng(graine + 1)
    z = np.arange(int(couches), dtype=float)[:, None, None]
    s = 120.0 + 40.0 * np.cos(2.0 * np.pi * z / float(periode))
    return np.broadcast_to(s, (int(couches), int(hauteur), int(largeur))) \
        + r.normal(0.0, 2.0, size=(int(couches), int(hauteur), int(largeur)))


def la_forme_des_volumes(segments, delai: float = DELAI) -> dict:
    """La forme publiée de chaque volume de surface, et son étendue en millimètres."""
    voulus = {str(s) for s in segments}
    out = {}
    for v in les_volumes(combien=10 ** 6):
        if str(v["segment"]) not in voulus or str(v["segment"]) in out:
            continue
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            out[str(v["segment"])] = {"decidable": False, "raison": type(e).__name__}
            continue
        prof, rows, cols = meta["shape"]
        out[str(v["segment"])] = {
            "decidable": True, "couches": int(prof), "hauteur": int(rows),
            "largeur": int(cols),
            "epaisseur_um": round(float(prof) * VOXEL_FIN_UM, 2),
            "epaisseur_en_plis": round(float(prof) * VOXEL_FIN_UM / PAS_UM, 4),
            "hauteur_mm": round(float(rows) * VOXEL_FIN_UM / 1000.0, 3),
            "largeur_mm": round(float(cols) * VOXEL_FIN_UM / 1000.0, 3)}
    return out


def la_part_montree(formes: dict, cote: int = 128) -> dict:
    """Quelle part d'un segment déplié une tuile de `195` et de `196` montre-t-elle ?

    ⭐⭐⭐⭐ LA QUESTION EST NEE D'UNE OBJECTION DE L'AUTEUR, ET LE CHIFFRE N'EXISTAIT PAS. Les deux
    tranches ont fait juger trente vignettes sans jamais dire ce qu'une vignette couvre du DÉPLIÉ.
    Une surface de segment se compte en dizaines de millimètres ; une tuile en centaines de
    micromètres.

    ⚠ La mediane des segments lisibles, jamais un segment choisi : le plus grand ou le plus petit
    ferait mesurer le choix.
    """
    lus = [v for v in formes.values() if v.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucune forme lisible"}
    aires = sorted(float(v["hauteur_mm"]) * float(v["largeur_mm"]) for v in lus)
    mediane = float(np.median(aires))
    tuile_mm2 = (float(cote) * VOXEL_FIN_UM / 1000.0) ** 2
    return {"decidable": True, "segments_lus": len(lus),
            "le_cote_de_la_tuile_um": round(float(cote) * VOXEL_FIN_UM, 2),
            "laire_dune_tuile_mm2": round(tuile_mm2, 6),
            "laire_mediane_dun_segment_mm2": round(mediane, 2),
            "la_part_dun_segment_par_tuile": float(f"{tuile_mm2 / mediane:.3e}"),
            "la_part_dun_segment_par_planche": float(f"{30.0 * tuile_mm2 / mediane:.3e}"),
            # ⚠ « un sur cent vingt-quatre mille » se lit ; « 8,035e-06 » ne se lit pas. C'est la
            # meme quantite, ecrite pour etre comprise plutot que dechiffree.
            "une_tuile_pour_combien_de_segment": int(round(mediane / tuile_mm2)),
            "une_planche_pour_combien_de_segment": int(round(mediane / (30.0 * tuile_mm2)))}


def sur_letalon(tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Les deux questions posées à une matière dont la réponse est construite."""
    cube = un_cube(109, 48, 48, graine=graine)
    par_axe = {}
    for i, nom in enumerate(LES_TROIS_AXES):
        par_axe[nom] = contre_le_melange_du_profil(le_profil(cube, i), tirages, graine)
    la_plate = une_pile(109, 128, pente=0.0, bruit=2.0, graine=graine)
    plate = le_serpentement(la_plate)
    # ⚠⚠⚠ LE CONTROLE NOMME : la regle refutee, mesuree sur la MEME pile plate.
    par_argmax = un_suivi_par_la_bande_la_plus_claire(la_plate)
    # ⚠⚠ LA PENTE POSEE EST DERIVEE : un quart de pli sur toute la largeur de la coupe.
    pente = (PAS_EN_VOXELS / 4.0) / 128.0
    inclinee = le_serpentement(une_pile(109, 128, pente=pente, bruit=2.0, graine=graine))
    trop = le_serpentement(une_pile(109, 128, pente=(2.0 * PAS_EN_VOXELS) / 128.0, bruit=2.0,
                                    graine=graine))
    return {
        "par_axe": par_axe,
        "seul_le_premier_axe_porte_la_periode": bool(
            par_axe[LES_TROIS_AXES[0]].get("elle_depasse_tous_les_melanges")
            and not par_axe[LES_TROIS_AXES[1]].get("elle_depasse_tous_les_melanges")
            and not par_axe[LES_TROIS_AXES[2]].get("elle_depasse_tous_les_melanges")),
        "une_pile_plate": plate,
        "la_meme_pile_suivie_par_la_bande_la_plus_claire": par_argmax,
        "une_pile_inclinee": inclinee,
        "la_pente_posee_en_plis": round(pente * 128.0 / PAS_EN_VOXELS, 6),
        "une_pile_trop_inclinee": trop,
        "le_suivi_par_argmax_fabrique_du_serpentement": bool(
            par_argmax.get("decidable")
            and float(par_argmax["le_serpentement_en_voxels"])
            > float(plate["le_serpentement_en_voxels"])),
        "letalon_separe": bool(
            plate.get("decidable") and inclinee.get("decidable")
            and float(plate["le_serpentement_en_voxels"])
            < float(inclinee["le_serpentement_en_voxels"])
            and int(trop["les_colonnes_saturees"]) > 0
            and int(inclinee["les_colonnes_saturees"]) == 0),
    }


def mesurer(graine: int = GRAINE, delai: float = DELAI, tirages: int = PERMUTATIONS) -> dict:
    """Les deux questions posées aux trente cubes que `195` et `196` ont montrés."""
    etq = les_etiquettes()
    dec = les_tuiles_declarees(etq["chunks"], graine)
    cubes = les_cubes(dec["paires"], delai, True)
    brut = cubes["tuiles"]
    # ⚠⚠⚠ ICI UN CUBE MANQUANT N'INVALIDE RIEN, ET LA REGLE DE `196` A ETE TRANSPLANTEE A TORT :
    # la-bas un cube perdu change le NOMBRE de tuiles, donc le tirage de l'ordre de la planche, donc
    # la lecture deposee. Cette tranche ne pose aucune planche et ne note aucune lecture : elle
    # DECRIT. Ce qui doit etre publie n'est donc pas un refus mais le COMPTE de ce qui a repondu et
    # la raison de ce qui manque — un cube absent peut l'etre parce qu'il est hors du maillage, donc
    # le taire biaiserait la description sans le dire.
    if not brut:
        return {"decidable": False, "raison": "aucun cube n'a répondu"}
    par_axe = {nom: [] for nom in LES_TROIS_AXES}
    serpents, pics = [], []
    for t in brut:
        cube = t["cube"]
        for i, nom in enumerate(LES_TROIS_AXES):
            r = contre_le_melange_du_profil(le_profil(cube, i), tirages, graine)
            if r.get("decidable"):
                par_axe[nom].append(r)
        s = le_serpentement(une_section(cube, la_rangee_montree(cube.shape[1])))
        if s.get("decidable"):
            serpents.append(s)
    resume = {}
    for nom in LES_TROIS_AXES:
        xs = par_axe[nom]
        resume[nom] = {
            "cubes_lus": len(xs),
            "depassent_tous_les_melanges": int(
                sum(1 for x in xs if x["elle_depasse_tous_les_melanges"])),
            "la_periode_mediane_en_voxels": (None if not xs else
                                             float(np.median([x["la_periode_en_voxels"]
                                                              for x in xs]))),
            "la_periode_mediane_en_um": (None if not xs else
                                         round(float(np.median([x["la_periode_en_um"]
                                                                for x in xs])), 4)),
            "lautocorrelation_mediane": (None if not xs else
                                         round(float(np.median([x["lautocorrelation"]
                                                                for x in xs])), 6))}
    sv = [float(x["le_serpentement_en_voxels"]) for x in serpents]
    sp = [float(x["le_serpentement_en_plis"]) for x in serpents]
    pics = [int(x["les_colonnes_saturees"]) for x in serpents]
    formes = la_forme_des_volumes(sorted({t["segment"] for t in dec["tuiles"]}), delai)
    for nom in LES_TROIS_AXES:
        # ⚠⚠ LE COMPTE ATTENDU PAR HASARD VOYAGE AVEC LE COMPTE OBSERVE : avec dix-neuf melanges, un
        # cube les depasse tous une fois sur vingt, donc « quatorze sur trente » ne se lit pas seul.
        resume[nom]["les_attendus_par_hasard"] = round(
            float(resume[nom]["cubes_lus"]) / float(int(tirages) + 1), 4)
    return {
        "graine": int(graine), "tirages": int(tirages),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_plage_de_recalage": int(DEMI_PAS_EN_VOXELS),
        "les_cubes": {"demandes": 2 * len(dec["paires"]), "rendus": len(brut),
                      "refuses": cubes["refuses"]},
        "la_forme_des_volumes": formes,
        "la_part_montree": la_part_montree(formes),
        "par_axe": resume,
        "le_serpentement": {
            "coupes_lues": len(serpents),
            "le_median_en_voxels": (None if not sv else round(float(np.median(sv)), 4)),
            "le_median_en_plis": (None if not sp else round(float(np.median(sp)), 6)),
            "le_maximal_en_voxels": (None if not sv else round(float(np.max(sv)), 4)),
            "les_coupes_avec_colonnes_saturees": int(sum(1 for x in pics if x > 0)),
            "les_colonnes_saturees_en_tout": int(sum(pics))},
        "letalon": sur_letalon(tirages, graine),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"QUE MONTRENT CES DEUX VUES   indécidable : {r.get('raison')}")
        return
    print(f"QUE MONTRENT CES DEUX VUES   {r['les_cubes']['rendus']} cubes sur "
          f"{r['les_cubes']['demandes']} · refus {r['les_cubes']['refuses'] or '—'} · pas d'un pli "
          f"{r['le_pas_dun_pli_en_voxels']} voxels · plage {r['la_plage_de_recalage']}")
    for nom in LES_TROIS_AXES:
        a = r["par_axe"][nom]
        print(f"  {nom:<16} {a['depassent_tous_les_melanges']}/{a['cubes_lus']} dépassent tous "
              f"les mélanges · période médiane {a['la_periode_mediane_en_voxels']} voxels "
              f"({a['la_periode_mediane_en_um']} µm) · autocorr {a['lautocorrelation_mediane']}")
    s = r["le_serpentement"]
    print(f"  LE SERPENTEMENT  médian {s['le_median_en_voxels']} voxels "
          f"({s['le_median_en_plis']} pli) · maximal {s['le_maximal_en_voxels']} · "
          f"{s['les_coupes_avec_colonnes_saturees']} coupes saturées")
    f = r["la_forme_des_volumes"]
    un = next((v for v in f.values() if v.get("decidable")), None)
    if un:
        print(f"  UN VOLUME        {un['couches']} couches ({un['epaisseur_en_plis']} pli) × "
              f"{un['hauteur']} × {un['largeur']} = {un['hauteur_mm']} × {un['largeur_mm']} mm")
    m = r.get("la_part_montree") or {}
    if m.get("decidable"):
        print(f"  LA PART MONTRÉE  une tuile de {m['le_cote_de_la_tuile_um']} µm de côté = "
              f"{m['laire_dune_tuile_mm2']} mm² sur {m['laire_mediane_dun_segment_mm2']} mm² · "
              f"une tuile pour {m['une_tuile_pour_combien_de_segment']} segments · "
              f"la planche entière pour {m['une_planche_pour_combien_de_segment']}")
    e = r["letalon"]
    print(f"  L'ÉTALON         seul le premier axe porte la période "
          f"{e['seul_le_premier_axe_porte_la_periode']} · sépare {e['letalon_separe']} · "
          f"plate {e['une_pile_plate']['le_serpentement_en_voxels']} · inclinée "
          f"{e['une_pile_inclinee']['le_serpentement_en_voxels']} · par argmax "
          f"{e['la_meme_pile_suivie_par_la_bande_la_plus_claire']['le_serpentement_en_voxels']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ le pas d'un pli en voxels est DÉRIVÉ",
      abs(PAS_EN_VOXELS - PAS_UM / VOXEL_FIN_UM) < 1e-12, str(round(PAS_EN_VOXELS, 4)))
    v("★★ la plage de recalage est la DEMI-période, pas un réglage",
      DEMI_PAS_EN_VOXELS == int(round(PAS_EN_VOXELS / 2.0)), str(DEMI_PAS_EN_VOXELS))
    v("★★★ les TROIS axes sont déclarés, pas seulement celui qu'on croit bon",
      len(LES_TROIS_AXES) == 3, str(LES_TROIS_AXES))

    # ⭐⭐⭐⭐ L'AUTOCORRELATION ET LA PERIODE SE VERIFIENT SUR UNE MATIERE CONSTRUITE.
    z = np.arange(400, dtype=float)
    onde = np.cos(2.0 * np.pi * z / 40.0)
    a = lautocorrelation(onde)
    v("l'autocorrélation vaut un au décalage nul", abs(a[0] - 1.0) < 1e-9, str(a[0]))
    p = la_periode_dominante(onde)
    v("★★★★ la période trouvée est celle qu'on a posée", p["la_periode_en_voxels"] == 40,
      str(p["la_periode_en_voxels"]))
    v("★★★★ et c'est la FONDAMENTALE, pas une de ses harmoniques",
      p["la_periode_en_voxels"] < 80, f"{p['la_periode_en_voxels']} contre 80, 120, 200…")
    v("★★ et elle est rendue aussi en micromètres",
      abs(p["la_periode_en_um"] - 40.0 * VOXEL_FIN_UM) < 1e-6, str(p["la_periode_en_um"]))
    # ⚠⚠ SUR UN PROFIL LONG, LA PERIODE D'UN PLI SE RETROUVE AU VOXEL PRES.
    zl = np.arange(400, dtype=float)
    pl = la_periode_dominante(np.cos(2.0 * np.pi * zl / PAS_EN_VOXELS))
    v("★★★★ sur quatre cents couches, la période d'un pli est retrouvée au voxel près",
      abs(pl["la_periode_en_voxels"] - PAS_EN_VOXELS) <= 1.0,
      f"{pl['la_periode_en_voxels']} contre {round(PAS_EN_VOXELS, 2)}")
    v("un profil plat ne rend aucune autocorrélation",
      float(np.max(np.abs(lautocorrelation(np.ones(50))))) == 0.0)
    v("★★ un profil trop court est indécidable",
      la_periode_dominante(np.ones(3)).get("decidable") is False)
    v("★★★ un profil PLAT est indécidable, jamais périodique",
      la_periode_dominante(np.ones(200)).get("decidable") is False,
      str(la_periode_dominante(np.ones(200)).get("raison")))
    v("★★★★ la plage basse est DÉRIVÉE du premier passage à zéro",
      p["le_premier_passage_a_zero"] == 10,
      f"{p['le_premier_passage_a_zero']} pour une onde de période 40")
    v("★★★ et la plage haute laisse la période d'un pli atteignable sur cent neuf couches",
      int(round(0.75 * 109)) > PAS_EN_VOXELS,
      f"{int(round(0.75 * 109))} contre {round(PAS_EN_VOXELS, 2)}")

    r19 = contre_le_melange_du_profil(onde, 19, 5)
    v("★★★★ une vraie période dépasse TOUS les mélanges", r19["elle_depasse_tous_les_melanges"],
      f"{r19['les_melanges_au_moins_aussi_forts']} mélanges au moins aussi forts")
    bruit = _rng(7).normal(0.0, 1.0, size=400)
    v("★★★★ et du bruit ne les dépasse PAS",
      not contre_le_melange_du_profil(bruit, 19, 5)["elle_depasse_tous_les_melanges"],
      str(contre_le_melange_du_profil(bruit, 19, 5)["les_melanges_au_moins_aussi_forts"]))
    v("★★★ la médiane du nul est publiée à côté de l'observé",
      r19["lautocorrelation_mediane_du_nul"] < r19["lautocorrelation"],
      f"{r19['lautocorrelation_mediane_du_nul']} contre {r19['lautocorrelation']}")

    # ⭐⭐⭐⭐ LE SERPENTEMENT : LES DEUX FACES, ET LA SATURATION NOMMEE.
    plate = le_serpentement(une_pile(109, 128, pente=0.0, bruit=1.0, graine=3))
    v("★★★★ une pile PLATE ne serpente pas", plate["le_serpentement_en_voxels"] == 0.0,
      str(plate["le_serpentement_en_voxels"]))
    pente = (PAS_EN_VOXELS / 4.0) / 128.0
    incl = le_serpentement(une_pile(109, 128, pente=pente, bruit=1.0, graine=3))
    v("★★★★ une pile INCLINÉE serpente de ce qu'on a posé",
      abs(incl["le_serpentement_en_voxels"] - 0.8 * PAS_EN_VOXELS / 4.0)
      < 0.25 * PAS_EN_VOXELS / 4.0,
      f"{incl['le_serpentement_en_voxels']} pour un quart de pli posé sur toute la largeur, "
      f"soit {round(0.8 * PAS_EN_VOXELS / 4.0, 2)} attendus entre les déciles")
    v("★★★ et son étalement est rendu en PLIS aussi",
      abs(incl["le_serpentement_en_plis"]
          - incl["le_serpentement_en_voxels"] / PAS_EN_VOXELS) < 1e-6)
    v("★★★ une pile inclinée dans la plage ne sature AUCUNE colonne",
      incl["les_colonnes_saturees"] == 0, str(incl["les_colonnes_saturees"]))
    trop = le_serpentement(une_pile(109, 128, pente=(2.0 * PAS_EN_VOXELS) / 128.0, bruit=1.0,
                                    graine=3))
    v("★★★★ une pile TROP inclinée sature, et le compte est publié",
      trop["les_colonnes_saturees"] > 0, str(trop["les_colonnes_saturees"]))
    v("★★★ la part saturée est rendue à côté du compte",
      abs(trop["la_part_saturee"] - trop["les_colonnes_saturees"] / trop["colonnes"]) < 1e-9)
    v("une coupe trop petite est indécidable",
      le_serpentement(np.ones((2, 1))).get("decidable") is False)
    v("★★ un profil moyen plat est indécidable, jamais nul",
      le_serpentement(np.ones((40, 20))).get("decidable") is False)

    # ⚠⚠ LE RECALAGE NE SUIT PAS LA BANDE LA PLUS CLAIRE, ET LA SONDE LE MONTRE : sur une pile a
    # deux bandes, un argmax par colonne sauterait de l'une a l'autre et rendrait un serpentement
    # geant la ou il n'y en a aucun.
    deux = une_pile(109, 128, periode=40.0, pente=0.0, bruit=1.0, graine=3)
    v("★★★★ deux bandes dans la coupe ne fabriquent pas de serpentement",
      le_serpentement(deux)["le_serpentement_en_voxels"] == 0.0,
      str(le_serpentement(deux)["le_serpentement_en_voxels"]))
    v("★★★★ tandis que le suivi par la bande la plus claire EN FABRIQUE, et c'est mesuré",
      un_suivi_par_la_bande_la_plus_claire(deux)["le_serpentement_en_voxels"] > 0.0,
      str(un_suivi_par_la_bande_la_plus_claire(deux)["le_serpentement_en_voxels"]))
    v("★★ un contrôle nommé sur une coupe trop petite est indécidable",
      un_suivi_par_la_bande_la_plus_claire(np.ones((4, 1))).get("decidable") is False)

    # ⭐⭐⭐⭐ L'ETALON DES TROIS AXES : LE PREMIER PORTE, LES DEUX AUTRES NON.
    e = sur_letalon(19, 5)
    v("★★★★ sur un cube dont seul le premier axe est périodique, seul lui dépasse",
      e["seul_le_premier_axe_porte_la_periode"],
      str({k: x.get("elle_depasse_tous_les_melanges") for k, x in e["par_axe"].items()}))
    # ⚠⚠⚠ SUR CENT NEUF COUCHES LA PERIODE N'EST PAS RETROUVEE AU VOXEL PRES, ET C'EST UNE LIMITE
    # MESUREE PLUTOT QU'UN SEUIL : un pli et demi tient dans la profondeur d'un cube. Ce qui se
    # verifie est donc que le decalage trouve est PLUS PRES du pli que de sa moitie ou de son
    # double — une affirmation qui discrimine et qui peut echouer.
    kk = float(e["par_axe"][LES_TROIS_AXES[0]]["la_periode_en_voxels"])
    v("★★★★ sur cent neuf couches, le décalage trouvé est plus près du pli que de ses harmoniques",
      abs(kk - PAS_EN_VOXELS) < min(abs(kk - PAS_EN_VOXELS / 2.0),
                                    abs(kk - 2.0 * PAS_EN_VOXELS)),
      f"{kk} contre {round(PAS_EN_VOXELS, 2)}, {round(PAS_EN_VOXELS / 2, 2)} et "
      f"{round(2 * PAS_EN_VOXELS, 2)}")
    v("★★★★ le contrôle nommé fabrique bien du serpentement là où le recalage n'en voit aucun",
      e["le_suivi_par_argmax_fabrique_du_serpentement"],
      f"{e['la_meme_pile_suivie_par_la_bande_la_plus_claire']['le_serpentement_en_voxels']} "
      f"contre {e['une_pile_plate']['le_serpentement_en_voxels']}")
    v("★★★★ l'étalon sépare ses faces", e["letalon_separe"],
      f"plate {e['une_pile_plate']['le_serpentement_en_voxels']}, inclinée "
      f"{e['une_pile_inclinee']['le_serpentement_en_voxels']}, saturées "
      f"{e['une_pile_trop_inclinee']['les_colonnes_saturees']}")
    # ⭐⭐⭐⭐ LA PART MONTREE SE VERIFIE SUR DES FORMES CONSTRUITES.
    faux_formes = {"A": {"decidable": True, "hauteur_mm": 100.0, "largeur_mm": 100.0},
                   "B": {"decidable": True, "hauteur_mm": 100.0, "largeur_mm": 100.0},
                   "C": {"decidable": False}}
    pm = la_part_montree(faux_formes, 128)
    v("★★★ la part montrée compte l'aire d'une tuile sur celle d'un segment",
      pm["segments_lus"] == 2 and abs(pm["laire_mediane_dun_segment_mm2"] - 10000.0) < 1e-6,
      str(pm["laire_mediane_dun_segment_mm2"]))
    # ⚠⚠ LES TOLERANCES SONT CELLES DE LA PRECISION PUBLIEE, PAS PLUS FINES : ces deux parts sont
    # arrondies a trois chiffres significatifs, donc exiger l'egalite exacte reviendrait a exiger
    # que l'arrondi n'existe pas. Les deux premieres versions de ces sondes l'ont fait.
    v("★★★★ et la planche entière en couvre trente fois plus qu'une tuile, à la précision publiée",
      abs(pm["la_part_dun_segment_par_planche"] - 30.0 * pm["la_part_dun_segment_par_tuile"])
      <= 30.0 * pm["la_part_dun_segment_par_tuile"] * 1e-2,
      f"{pm['la_part_dun_segment_par_planche']} contre "
      f"{30.0 * pm['la_part_dun_segment_par_tuile']}")
    v("★★★★ la part montrée se lit aussi en « une tuile pour N », et les deux écritures s'accordent",
      abs(1.0 / pm["une_tuile_pour_combien_de_segment"] - pm["la_part_dun_segment_par_tuile"])
      <= pm["la_part_dun_segment_par_tuile"] * 1e-2,
      f"{pm['une_tuile_pour_combien_de_segment']} contre "
      f"{1.0 / pm['la_part_dun_segment_par_tuile']}")
    v("★★★ et la planche en couvre trente fois plus, donc trente fois moins de segments",
      abs(pm["une_tuile_pour_combien_de_segment"]
          - 30 * pm["une_planche_pour_combien_de_segment"])
      <= 0.02 * pm["une_tuile_pour_combien_de_segment"],
      f"{pm['une_tuile_pour_combien_de_segment']} contre "
      f"{30 * pm['une_planche_pour_combien_de_segment']}")
    v("★★ une forme illisible est écartée, jamais comptée",
      la_part_montree({"A": {"decidable": False}}).get("decidable") is False)
    v("★★★ et la part d'une tuile de 128 voxels vaut ce que l'arithmétique dit",
      abs(pm["laire_dune_tuile_mm2"] - (128 * VOXEL_FIN_UM / 1000.0) ** 2) <= 5e-7,
      str(pm["laire_dune_tuile_mm2"]))

    v("★★★ et la pente posée est publiée en plis",
      abs(e["la_pente_posee_en_plis"] - 0.25) < 1e-6, str(e["la_pente_posee_en_plis"]))

    nom = "que_montrent_ces_deux_vues.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e_ in echecs:
            print(f"   ✗ {e_}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return len(echecs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
