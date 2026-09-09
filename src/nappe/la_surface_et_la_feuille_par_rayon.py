#!/usr/bin/env python3
"""De combien la surface HUMAINE s'ecarte de la feuille, du coeur au bord.

⚠⚠⚠ POURQUOI CETTE QUESTION EST LA SUIVANTE. `94` vient de tuer le froissement comme signal de
confiance : a travers les rayons il est ANTI-predictif, et la raison mesuree est que les maillages
humains sont cinq fois plus LISSES au bord parce qu'ils ont ENJAMBE ce qu'ils ne pouvaient pas
suivre. Il faut donc une observable qui ne soit pas une propriete du maillage mais de la MATIERE,
et le depot en a deja une : `la_surface_et_la_feuille` mesure l'ecart entre la spire publiee et le
ruban de matiere qu'elle suit. ⭐ Ce qui est neuf ici est l'AXE : cette mesure ne couvre
`PHercParis4` que par UNE bande (`w010-027`), et la question de `94` est ce qu'elle devient a
travers les rayons.

⭐⭐⭐ ET C'EST AFFORDABLE PARCE QUE LES CHUNKS NE SONT PAS COMPRESSES. La mesure existante passe
par des couches RENDUES, ce qui coute assez cher pour n'en faire qu'une bande. Ici les points sont
lus directement dans le volume par requetes `Range` (`src/commun/voxel_distant.py`), donc les 28
bandes coutent une vingtaine de minutes au lieu d'un rendu par bande.

⚠⚠ DEUX VOLUMES, ET C'EST LE FIN QUI DECIDE. Le maillage est ecrit dans les voxels du volume a
45,532 µm, ou un demi-ecart inter-feuilles vaut DEUX voxels : on ne peut pas y mesurer un
decalage de vingt micrometres, et une mesure prise la serait une limite de grille publiee comme
une limite de matiere. Le meme objet publie un volume a **2,4 µm** couvrant 182 × 78 × 78 mm, et
la matrice qui relie les deux est publiee (`src/commun/transformations_de_volume.py`).

⭐⭐ LA PREDICTION EST ECRITE AVANT LA MESURE, AVEC SON SIGNE. Une feuille est un ruban brillant
et l'espace entre deux feuilles est sombre. Si le maillage a ponte au bord, ses cellules y
traversent du VIDE, donc le profil le long de la normale doit y perdre son RELIEF. Sonde sur trois
bandes, 90 cellules chacune :

    bande       rayon      contraste   dispersion du centre de masse
    w010-027    4,1 mm       119,0            23,1 µm
    w092-094   17,5 mm       107,5            16,3 µm
    w128-129   23,8 mm      **11,0**           7,2 µm

⚠⚠⚠ ET LA DISPERSION DU BORD EST UN ARTEFACT, PAS UN RESULTAT. Sans contraste, le centre de masse
d'un profil de bruit se pose au MILIEU de la fenetre, donc il disperse peu : lue seule, la
troisieme colonne dirait « la surface est la mieux placee au bord », c'est-a-dire exactement
l'inverse de ce que `92` et `93` mesurent. Le contraste est donc publie A COTE et c'est lui qui
dit si la dispersion veut dire quelque chose. Une dispersion sans son contraste est une mesure
satisfaite par l'absence de ce qu'elle mesure.

⛔ LE CONFONDANT QUI RESTE A TRANCHER, ET IL EST NOMME PLUTOT QUE SUPPOSE ABSENT. Le volume est
« masked » : tout ce qui est hors du rouleau vaut zero, et le bord du rouleau est precisement la
ou l'on approche du masque. Un contraste qui tombe au bord peut donc venir du PONTAGE ou du
MASQUE, et les deux se lisent pareil. `part_au_zero` mesure la seconde, bande par bande, et sans
elle ce fichier publierait « classer par rayon en croyant classer par difficulte » — la faute
exacte que `94` a nommee.

Usage :
    uv run python src/nappe/la_surface_et_la_feuille_par_rayon.py --verifier
    uv run python src/nappe/la_surface_et_la_feuille_par_rayon.py \\
        --json docs/mesures/la_surface_et_la_feuille_par_rayon.json
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

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

OBJET = "PHercParis4"
VOLUME_DU_MAILLAGE = "20260310170716"
VOLUME_FIN = "20260411134726"
ZARR_FIN = (f"{OBJET}/volumes/"
            f"{VOLUME_FIN}-2.400um-0.2m-78keV-masked.zarr")
VOXEL_FIN_UM = 2.4
VOXEL_MAILLAGE_UM = 45.532

# ⚠⚠ L'ECART INTER-FEUILLES VIENT DE `91`, MESURE SUR CET OBJET (164 a 182 µm), et non d'un
# atlas : `la_surface_et_la_feuille` publie 173 µm pour `PHercParis4`. La demi-fenetre en decoule
# et n'est PAS un reglage — c'est la plus grande fenetre qui ne peut pas contenir deux feuilles,
# et son absence avait deja gonfle un chiffre publie de 37,7 a 23,8 µm.
ECART_INTER_FEUILLES_UM = 173.0
FOND_PERCENTILE = 20
CELLULES_PAR_BANDE = 90


def demi_fenetre_voxels(ecart_um: float = ECART_INTER_FEUILLES_UM,
                        voxel_um: float = VOXEL_FIN_UM) -> int:
    """La demi-fenetre de recherche, en voxels fins : un DEMI ecart inter-feuilles."""
    return int(round(0.5 * ecart_um / voxel_um))


def profils(a: np.ndarray, n: np.ndarray, indices: np.ndarray, vol, m: np.ndarray,
            demi: int, fils: int = 32) -> tuple[np.ndarray, np.ndarray]:
    """Le profil d'intensite le long de la normale, dans le volume FIN. Et qui est mesurable.

    ⚠⚠ LE PAS EST UN VOXEL FIN, EXPRIME DANS LES UNITES DU MAILLAGE. La normale est unitaire en
    voxels du maillage (45,532 µm) ; avancer d'un voxel FIN veut donc dire avancer de
    2,4 / 45,532 unite de maillage. Confondre les deux echantillonnerait dix-neuf fois trop
    large et moyennerait plusieurs feuilles dans un seul profil.
    """
    from transformations_de_volume import appliquer  # noqa: PLC0415

    p = a[indices[:, 0], indices[:, 1]]
    d = n[indices[:, 0], indices[:, 1]]
    pas = np.arange(-demi, demi + 1)
    facteur = VOXEL_FIN_UM / VOXEL_MAILLAGE_UM
    points = p[:, None, :] + d[:, None, :] * (pas[None, :, None] * facteur)
    zyx = np.rint(appliquer(m, points)).astype(np.int64)
    dedans = vol.dans_le_volume(zyx.reshape(-1, 3)).reshape(zyx.shape[:2]).all(axis=1)
    lus = np.full((len(indices), len(pas)), np.nan)
    if dedans.any():
        lus[dedans] = vol.lire(zyx[dedans].reshape(-1, 3), fils=fils).reshape(
            int(dedans.sum()), len(pas))
    return lus, dedans


def centre_de_masse(prof: np.ndarray, fond_percentile: int = FOND_PERCENTILE) -> np.ndarray:
    """Le centre de masse du profil, en voxels fins depuis la cellule. L'ESTIMATEUR, pas l'argmax.

    ⚠⚠⚠ LE DEPOT A DEJA PAYE CE CHOIX. Le pic brut par colonne donne 0,486 feuille de dispersion,
    c'est-a-dire rien d'exploitable, quand le centre de masse en donne 0,188 : ce n'etait pas le
    signal qui manquait, c'etait l'estimateur qui choisissait un voxel la ou il faut integrer une
    bande. Reecrire un argmax ici serait refaire l'erreur avec le meme code sous les yeux.
    """
    demi = prof.shape[1] // 2
    pas = np.arange(-demi, demi + 1, dtype=np.float64)
    fond = np.nanpercentile(prof, fond_percentile)
    poids = np.clip(prof - fond, 0, None)
    total = np.nansum(poids, axis=1)
    return np.where(total > 1e-9, np.nansum(poids * pas[None, :], axis=1)
                    / np.clip(total, 1e-9, None), np.nan)


def echantillon(bon: np.ndarray, combien: int, graine: int) -> np.ndarray:
    """Des cellules valides tirees uniformement, INTERIEURES au sens de la normale.

    ⚠ Les cellules de bord n'ont pas de normale (differences centrees), donc les inclure ferait
    lire le volume le long d'une direction nulle : tout le profil au meme point, donc un
    contraste nul, donc une bande qui parait pontee parce qu'on l'a mal echantillonnee.
    """
    ou = np.argwhere(bon)
    if len(ou) == 0 or len(ou) <= combien:
        return ou
    r = np.random.default_rng(graine)
    return ou[r.choice(len(ou), size=combien, replace=False)]


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def correlation_partielle(x, y, z) -> float:
    """La correlation de x et y une fois RETIRE ce que z explique des deux.

    ⭐⭐⭐ C'EST L'INSTRUMENT QUI DECIDE SI CE FICHIER MESURE LA MATIERE OU LE MASQUE. La part au
    remplissage monte fortement avec le rayon, donc toute quantite qui tombe avec le rayon tombe
    aussi avec elle : sans retirer z, « la surface est mieux placee au bord » et « le volume
    s'arrete au bord » sont la MEME observation, et une seule est un resultat.

    ⚠ Elle ne prouve pas une cause, elle retire un confondant NOMME. Un confondant qu'on n'a pas
    pense a mesurer traverse cette formule sans laisser de trace.
    """
    x, y, z = (np.asarray(v, dtype=np.float64) for v in (x, y, z))
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0 or np.std(z) == 0:
        return 0.0
    rxy, rxz, ryz = (float(np.corrcoef(a, b)[0, 1]) for a, b in ((x, y), (x, z), (y, z)))
    denom = np.sqrt(max(1e-12, (1 - rxz ** 2) * (1 - ryz ** 2)))
    return round(float((rxy - rxz * ryz) / denom), 3)


SEUIL_MASQUE = 0.10
"""Part du profil au remplissage au-dela de laquelle une bande est dite RONGEE par le masque.

⚠⚠ CE SEUIL N'EST PAS CHOISI POUR QUE LE RESULTAT PASSE, et c'est verifiable : la batterie le
balaye et publie le verdict a chaque valeur. Un seuil dont la conclusion depend serait un reglage
deguise ; ici la conclusion doit tenir sur toute la plage ou il reste des bandes des deux cotes.
"""


def _sans_masque(mesurees: list[dict], seuil: float = SEUIL_MASQUE) -> dict:
    """Le meme verdict sur les seules bandes que le masque ne ronge pas."""
    gardees = [x for x in mesurees if x["part_au_zero"] < seuil]
    if len(gardees) < 6:
        return {"seuil": seuil, "bandes": len(gardees), "message": "trop peu de bandes gardées"}
    return {
        "seuil": seuil, "bandes": len(gardees),
        "rayon_max_mm": max(x["rayon_mm"] for x in gardees),
        "dispersion_contre_rayon": correlation(
            [x["dispersion_um"] for x in gardees], [x["rayon_mm"] for x in gardees]),
        "dispersion_contre_continuite": correlation(
            [x["dispersion_um"] for x in gardees], [x["continuite"] for x in gardees]),
        "contraste_contre_rayon": correlation(
            [x["contraste"] for x in gardees], [x["rayon_mm"] for x in gardees]),
    }


def mesurer(cellules: int = CELLULES_PAR_BANDE, graine: int = 5,
            bandes_max: int | None = None, fils: int = 32) -> dict:
    import deux_modes_dechec_du_transfert as D  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import echelle, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    if not ALIGNEMENT.is_file() or not CONTINUITE.is_file():
        return {"message": "il manque la carte d'échec : lancer `deux_modes_dechec_du_transfert` "
                           "et `la_continuite_des_transferts`"}
    al = {(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
    co = {(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
    m = matrice(OBJET, VOLUME_DU_MAILLAGE, VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    demi = demi_fenetre_voxels()
    lignes = []
    for x in R.bandes_du_fragment()[:bandes_max]:
        cle = (x["de"], x["a"])
        if cle not in al or cle not in co:
            continue
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        n, bon = D.normales(a, ok)
        ind = echantillon(bon, cellules, graine + x["de"])
        if len(ind) < 20:
            continue
        prof, dedans = profils(a, n, ind, vol, m, demi, fils=fils)
        fini = np.isfinite(prof).all(axis=1)
        if int(fini.sum()) < 15:
            # ⚠ Une bande hors du champ du volume fin est DECLAREE, jamais silencieusement
            # absente du tableau : « pas mesuree » et « mesuree sans relief » sont deux faits
            # opposes, et les confondre ferait passer un trou de couverture pour du pontage.
            lignes.append(dict(de=x["de"], a=x["a"], rayon_mm=al[cle]["rayon_mm"],
                               cellules=int(fini.sum()), hors_du_volume_fin=True,
                               cellules_dans_le_champ=int(dedans.sum()),
                               desalignement=al[cle]["rapport_au_plancher"],
                               continuite=co[cle]["rapport_interieur"]))
            continue
        p = prof[fini]
        cm = centre_de_masse(p)
        contraste = np.nanmax(p, axis=1) - np.nanmin(p, axis=1)
        lignes.append(dict(
            de=x["de"], a=x["a"], rayon_mm=al[cle]["rayon_mm"],
            cellules=int(fini.sum()), hors_du_volume_fin=False,
            cellules_dans_le_champ=int(dedans.sum()),
            # ⚠⚠⚠ CE COMPTE EXISTE PARCE QUE SON ABSENCE A DEJA FAIT BOUGER UN RESULTAT. Une
            # coupure passagere faisait tomber des cellules en SILENCE : une bande est passee de
            # 90 a 65 entre deux executions du meme calcul, et sa dispersion de 14,2 a 12,7 µm.
            # Le reessai le rend rare, le publier le rend VISIBLE — et les deux sont necessaires,
            # parce qu'un reessai qui echoue quand meme laisserait le meme trou muet.
            cellules_perdues=int(dedans.sum() - fini.sum()),
            # ⭐⭐ LE CONTRASTE EST PUBLIE AVANT LA DISPERSION, parce que c'est lui qui dit si la
            # dispersion veut dire quelque chose : sans relief, le centre de masse d'un bruit se
            # pose au milieu de la fenetre et disperse peu.
            contraste=round(float(np.median(contraste)), 1),
            dispersion_um=round(float(np.nanstd(cm) * VOXEL_FIN_UM), 1),
            decalage_median_um=round(float(np.nanmedian(cm) * VOXEL_FIN_UM), 1),
            # ⛔ LE CONFONDANT : la part du profil au remplissage. Un contraste qui tombe parce
            # qu'on est SORTI du rouleau n'a rien a voir avec un pontage.
            part_au_zero=round(float(np.mean(p == 0.0)), 3),
            intensite_mediane=round(float(np.median(p)), 1),
            desalignement=al[cle]["rapport_au_plancher"],
            continuite=co[cle]["rapport_interieur"],
        ))
    mesurees = [x for x in lignes if not x["hors_du_volume_fin"]]
    if not mesurees:
        return {"message": "aucune bande mesurable dans le volume fin"}

    ray = [x["rayon_mm"] for x in mesurees]
    ctr = [x["contraste"] for x in mesurees]
    dis = [x["dispersion_um"] for x in mesurees]
    zer = [x["part_au_zero"] for x in mesurees]
    des = [x["desalignement"] for x in mesurees]
    rup = [x["continuite"] for x in mesurees]

    tri = sorted(mesurees, key=lambda z: z["rayon_mm"])
    t = max(1, len(tri) // 3)
    tiers = {"coeur": tri[:t], "milieu": tri[t:2 * t], "bord": tri[2 * t:]}
    med = lambda v, k: round(float(np.median([y[k] for y in v])), 3)  # noqa: E731
    return {
        # ⭐ Le total des pertes est en tete du rapport, pas enfoui par bande : c'est la
        # premiere chose qui dit si ce run est comparable au precedent.
        "cellules_perdues": sum(x.get("cellules_perdues", 0) for x in mesurees),
        "run_complet": all(x.get("cellules_perdues", 0) == 0 for x in mesurees),
        "fragment": OBJET, "volume_fin": ZARR_FIN.rsplit("/", 1)[-1],
        "voxel_fin_um": VOXEL_FIN_UM, "echelle_de_la_transformation": round(echelle(m), 3),
        "bandes": len(lignes), "bandes_mesurees": len(mesurees),
        "cellules_par_bande": cellules,
        "demi_fenetre_voxels": demi,
        "demi_fenetre_um": round(demi * VOXEL_FIN_UM, 1),
        "lignes": lignes,
        "correlations": {
            "contraste_contre_rayon": correlation(ctr, ray),
            "contraste_contre_desalignement": correlation(ctr, des),
            "contraste_contre_continuite": correlation(ctr, rup),
            "dispersion_contre_rayon": correlation(dis, ray),
            "dispersion_contre_continuite": correlation(dis, rup),
            # ⛔ LE CONFONDANT, MESURE : si la part au remplissage explique le contraste, alors
            # ce fichier mesure le masque et non la matiere.
            "contraste_contre_part_au_zero": correlation(ctr, zer),
            "part_au_zero_contre_rayon": correlation(zer, ray),
            "dispersion_contre_part_au_zero": correlation(dis, zer),
        },
        # ⭐⭐⭐ LE MEME RESULTAT UNE FOIS LE MASQUE RETIRE. Ce bloc existe parce que sans lui,
        # « la surface est mieux placee au bord » et « le volume s'arrete au bord » seraient la
        # meme observation.
        "une_fois_le_masque_retire": {
            "dispersion_contre_rayon": correlation_partielle(dis, ray, zer),
            "dispersion_contre_continuite": correlation_partielle(dis, rup, zer),
            "dispersion_contre_desalignement": correlation_partielle(dis, des, zer),
            "contraste_contre_rayon": correlation_partielle(ctr, ray, zer),
            "contraste_contre_continuite": correlation_partielle(ctr, rup, zer),
        },
        # ⚠⚠ ET LE MEME RESULTAT SANS LES BANDES QUE LE MASQUE MANGE. Retirer un confondant par
        # une formule et le retirer en jetant les cas concernes sont deux gestes differents :
        # s'ils ne s'accordent pas, c'est la formule qui a tort, parce qu'elle suppose une
        # relation lineaire que deux bandes a 0,2 et 0,4 de remplissage ne respectent pas.
        "sans_les_bandes_rongees_par_le_masque": _sans_masque(mesurees),
        # ⭐⭐⭐ LE BALAYAGE EST PUBLIE, ET C'EST CE QUI REND « LE SEUIL N'EST PAS REGLE »
        # VERIFIABLE PLUTOT QU'AFFIRME. Un verdict qui ne tient qu'a une valeur est un verdict
        # choisi ; celui-ci doit tenir partout ou il reste des bandes des deux cotes.
        "balayage_du_seuil": [_sans_masque(mesurees, x)
                              for x in (0.05, 0.10, 0.15, 0.20, 0.30)],
        "par_tiers": {k: {"bandes": len(v),
                          "contraste": med(v, "contraste"),
                          "dispersion_um": med(v, "dispersion_um"),
                          "part_au_zero": med(v, "part_au_zero"),
                          "intensite_mediane": med(v, "intensite_mediane"),
                          "desalignement": med(v, "desalignement"),
                          "continuite": med(v, "continuite")}
                      for k, v in tiers.items() if v},
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · volume fin {r['voxel_fin_um']} µm · "
          f"{r['bandes_mesurees']}/{r['bandes']} bandes mesurées · fenêtre ±"
          f"{r['demi_fenetre_um']} µm\n")
    print(f"{'bande':>10} {'rayon':>7} {'contraste':>10} {'dispersion':>11} "
          f"{'part à 0':>9} {'désalign':>9} {'continuité':>11}")
    for x in r["lignes"]:
        if x["hors_du_volume_fin"]:
            print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} "
                  f"{'HORS DU CHAMP DU VOLUME FIN':>44}")
            continue
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mm']:>6.1f} "
              f"{x['contraste']:>10.1f} {x['dispersion_um']:>10.1f}µ "
              f"{x['part_au_zero']:>9.3f} {x['desalignement']:>9.2f} "
              f"{x['continuite']:>11.1f}")
    c, p = r["correlations"], r["par_tiers"]
    print(f"\n{'':>22} {'contraste':>11} {'dispersion':>11} {'part à 0':>10} "
          f"{'continuité':>11}")
    for k in ("coeur", "milieu", "bord"):
        if k in p:
            print(f"{k:>22} {p[k]['contraste']:>11.1f} {p[k]['dispersion_um']:>10.1f}µ "
                  f"{p[k]['part_au_zero']:>10.3f} {p[k]['continuite']:>11.1f}")
    print(f"\n{'':>30} {'rayon':>8} {'continuité':>12}")
    print(f"{'contraste':>30} {c['contraste_contre_rayon']:>+8.3f} "
          f"{c['contraste_contre_continuite']:>+12.3f}")
    print(f"{'dispersion':>30} {c['dispersion_contre_rayon']:>+8.3f} "
          f"{c['dispersion_contre_continuite']:>+12.3f}")
    # ⛔ LE CONFONDANT EST IMPRIME AVEC LE RESULTAT, jamais en annexe : un contraste qui tombe
    # au bord peut venir du pontage ou du MASQUE, et les deux se lisent pareil.
    print(f"\n⛔ CONFONDANT — part au remplissage contre le rayon : "
          f"{c['part_au_zero_contre_rayon']:+.3f}, et contre le contraste : "
          f"{c['contraste_contre_part_au_zero']:+.3f}")
    print("   si la part au zéro explique le contraste, ce fichier mesure le MASQUE et non la")
    print("   matière, et « le contraste tombe au bord » serait une limite de champ publiée")
    print("   comme une limite de matière.")
    # ⚠⚠ LA DISPERSION NE SE LIT PAS SEULE : sans relief, le centre de masse d'un profil de
    # bruit se pose au MILIEU de la fenetre, donc il disperse PEU.
    if r["cellules_perdues"]:
        print(f"\n⚠⚠⚠ {r['cellules_perdues']} CELLULE(S) PERDUE(S) AU RÉSEAU malgré les réessais :")
        print("   ce run n'est PAS comparable à un autre. Bandes concernées : "
              + ", ".join(f"w{x['de']:03d}-{x['a']:03d} ({x['cellules_perdues']})"
                          for x in r["lignes"] if x.get("cellules_perdues")))
    else:
        print("\n★ run complet : aucune cellule perdue au réseau, donc reproductible")
    print("\n⚠⚠ LA DISPERSION NE SE LIT PAS SANS SON CONTRASTE : sans relief, le centre de masse")
    print("   d'un profil de bruit se pose au milieu de la fenêtre et disperse peu. Lue seule,")
    print("   elle dirait « la surface est la mieux placée au bord », l'inverse de `92` et `93`.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'estimateur, sur des profils dont on connait la reponse -------------------------
    demi = 36
    n = 2 * demi + 1
    pic = np.zeros((3, n))
    pic[0, demi] = 200.0
    pic[1, demi + 10] = 200.0
    pic[2, demi - 7] = 200.0
    cm = centre_de_masse(pic)
    v("un pic au centre rend un décalage nul", abs(cm[0]) < 1e-6, str(cm[0]))
    v("... un pic à +10 rend +10", abs(cm[1] - 10) < 1e-6, str(cm[1]))
    v("... et un pic à -7 rend -7", abs(cm[2] + 7) < 1e-6, str(cm[2]))
    # ⚠⚠⚠ LE CONTROLE QUI NOMME LE PIEGE DU FICHIER, et il a fallu le corriger pour qu'il le
    # nomme vraiment. Le fond est pris sur TOUTE la bande, pas par cellule : une cellule PLATE
    # au milieu d'une bande contrastee recoit donc un poids uniforme, et son centre de masse se
    # pose au MILIEU de la fenetre. Sans le contraste a cote, ce zero se lirait comme « la
    # surface est parfaitement placee » — l'inverse exact du fait.
    lot = np.vstack([pic, np.full((1, n), 150.0)])
    cm_lot = centre_de_masse(lot)
    v("une cellule PLATE dans une bande contrastée se centre au MILIEU, d'où le contraste",
      abs(cm_lot[3]) < 1e-6, str(cm_lot[3]))
    v("... et son contraste, lui, vaut zéro", float(lot[3].max() - lot[3].min()) == 0.0)
    # ⚠⚠ ET UN PROFIL PLAT SEUL REND NaN PLUTOT QUE ZERO, ce que ma premiere fixture ignorait :
    # quand rien ne depasse le fond, il n'y a pas de centre de masse, et en inventer un serait
    # publier un decalage la ou aucune mesure n'a eu lieu.
    v("un profil plat SEUL rend NaN, pas un décalage inventé",
      bool(np.isnan(centre_de_masse(np.full((1, n), 90.0))[0])))
    # ⚠ Le bruit non plus ne se centre pas ailleurs qu'au milieu, en moyenne.
    r = np.random.default_rng(3)
    bruit = r.normal(90.0, 8.0, size=(400, n))
    v("... et du bruit pur se centre au milieu à moins d'un voxel",
      abs(float(np.nanmedian(centre_de_masse(bruit)))) < 1.0,
      f"{float(np.nanmedian(centre_de_masse(bruit))):.3f} voxel")

    # --- la demi-fenetre, DERIVEE et non reglee -------------------------------------------
    v("la demi-fenêtre est un demi-écart inter-feuilles",
      demi_fenetre_voxels() == int(round(0.5 * ECART_INTER_FEUILLES_UM / VOXEL_FIN_UM)),
      f"{demi_fenetre_voxels()} voxels = {demi_fenetre_voxels() * VOXEL_FIN_UM:.1f} µm")
    v("... donc la fenêtre entière ne peut pas contenir deux feuilles",
      (2 * demi_fenetre_voxels() + 1) * VOXEL_FIN_UM < ECART_INTER_FEUILLES_UM * 1.05,
      f"{(2 * demi_fenetre_voxels() + 1) * VOXEL_FIN_UM:.1f} µm pour "
      f"{ECART_INTER_FEUILLES_UM} µm d'écart")
    # ⚠⚠ ET LE VOLUME DU MAILLAGE NE POURRAIT PAS PORTER CETTE MESURE : c'est la raison d'etre
    # du volume fin, et la dire en controle evite qu'on la reprenne un jour sur le grossier.
    v("le volume du maillage ne résout PAS un demi-écart, d'où le volume fin",
      demi_fenetre_voxels(voxel_um=VOXEL_MAILLAGE_UM) <= 2,
      f"{demi_fenetre_voxels(voxel_um=VOXEL_MAILLAGE_UM)} voxels à "
      f"{VOXEL_MAILLAGE_UM} µm")

    v("l'échantillon écarte les cellules sans normale",
      len(echantillon(np.zeros((4, 4), dtype=bool), 10, 1)) == 0)
    v("... et rend tout ce qu'il y a quand il y en a moins que demandé",
      len(echantillon(np.ones((3, 3), dtype=bool), 100, 1)) == 9)
    v("... et exactement ce qu'on demande sinon",
      len(echantillon(np.ones((20, 20), dtype=bool), 50, 1)) == 50)
    v("une corrélation sur une constante rend zéro plutôt que NaN",
      correlation([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0)
    # --- la correlation partielle, sur un confondant FABRIQUE -----------------------------
    r = np.random.default_rng(1)
    z = r.normal(0, 1, 400)
    # ⭐⭐⭐ DEUX QUANTITES QUI NE DEPENDENT QUE DE z SE CORRELENT FORTEMENT ENTRE ELLES, et la
    # partielle doit les rendre a zero. C'est exactement la situation de ce fichier : la part
    # au remplissage monte avec le rayon, donc tout ce qui suit le rayon suit aussi le masque.
    x = z * 2 + r.normal(0, 0.2, 400)
    y = z * 3 + r.normal(0, 0.2, 400)
    v("deux quantités mues par un même confondant se corrèlent fort",
      correlation(x, y) > 0.9, str(correlation(x, y)))
    v("... et la partielle les ramène à zéro une fois le confondant retiré",
      abs(correlation_partielle(x, y, z)) < 0.2, str(correlation_partielle(x, y, z)))
    # ⚠⚠ ET ELLE NE DETRUIT PAS UN LIEN QUI NE PASSE PAS PAR LE CONFONDANT — mais la fixture
    # doit en CONTENIR un, et ma premiere version n'en contenait pas. J'y prenais
    # `w = 0,9·x + bruit` avec x ≈ 2z, donc le lien entre x et w passait bel et bien par z, et
    # la partielle avait RAISON de le reduire a 0,48. Ici les deux partagent une composante `a`
    # explicitement etrangere a z, donc ce qui survit est nommable.
    a = r.normal(0, 1, 400)
    x2, w2 = z * 2 + a, z * 3 + a
    v("... mais elle garde un lien qui ne passe PAS par le confondant",
      correlation_partielle(x2, w2, z) > 0.8, str(correlation_partielle(x2, w2, z)))
    v("la partielle rend zéro plutôt que NaN sur une constante",
      correlation_partielle([1.0] * 5, [1.0, 2, 3, 4, 5], [1.0, 2, 3, 4, 5]) == 0.0)

    resultat = mesurer(cellules=25, bandes_max=2)
    if "message" in resultat:
        print(f"  ⚠ {resultat['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("l'échelle de la transformation vaut le rapport des voxels",
      abs(resultat["echelle_de_la_transformation"]
          / (VOXEL_MAILLAGE_UM / VOXEL_FIN_UM) - 1) < 0.01,
      str(resultat["echelle_de_la_transformation"]))
    v("... et la mesure atteint le volume fin", resultat["bandes_mesurees"] >= 1,
      f"{resultat['bandes_mesurees']}/{resultat['bandes']}")
    # ⭐⭐ LE CONTROLE DE MAPPAGE SUR DONNEES REELLES : un maillage humain pose sur de la matiere
    # doit voir du RELIEF. Une transformation fausse rendrait des points sans rapport, donc un
    # contraste au niveau du bruit du volume.
    mes = [x for x in resultat["lignes"] if not x["hors_du_volume_fin"]]
    v("les cellules du cœur voient du relief, donc la transformation vise la matière",
      mes and mes[0]["contraste"] > 40, str(mes[0]["contraste"] if mes else None))
    # ⚠⚠ LA REPRODUCTIBILITE EST UN CHAMP PUBLIE, pas une esperance : sans lui, deux runs qui
    # different n'ont aucun moyen de dire lequel etait complet.
    v("le rapport dit si le run a perdu des cellules", "run_complet" in resultat)
    v("... et le compte est par bande aussi", all("cellules_perdues" in x for x in mes))
    v("le confondant du masque est publié",
      "part_au_zero_contre_rayon" in resultat["correlations"])
    v("... et le verdict une fois le masque retiré aussi",
      "une_fois_le_masque_retire" in resultat)
    # ⭐⭐ LE BALAYAGE EST CE QUI REND LE SEUIL VERIFIABLE : un verdict qui ne tient qu'a une
    # valeur serait un seuil choisi pour que le resultat passe.
    v("... et le balayage du seuil, publié plutôt qu'affirmé",
      len(resultat.get("balayage_du_seuil", [])) >= 4,
      str(len(resultat.get("balayage_du_seuil", []))))
    v("... et la part au remplissage aussi, bande par bande",
      all("part_au_zero" in x for x in mes))
    # ⚠ L'affichage est lance par la batterie : `93` a paye un `--verifier` vert pendant que
    # `main()` plantait sur une clef renommee.
    v("l'affichage tourne sur ce résultat", afficher(resultat) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cellules=a.cellules, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
