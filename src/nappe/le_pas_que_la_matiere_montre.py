#!/usr/bin/env python3
"""Quel pas de feuille la MATIERE montre-t-elle ici ? — `98` cesse d'auditer et se met a decider.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST L'ITEM A DU BLOC DE REPRISE. `98` a livre le premier critere
dont le seuil ne vient ni d'un maillage ni d'un reglage : entre une cellule et le point situe UN
PAS NOMINAL plus loin, le profil doit valoir brillant-sombre-brillant. Mais il AUDITE — il verifie
un pas qu'on lui donne. Un automate a besoin de l'inverse : qu'on lui DISE le pas. Le meme filtre
le fait en balayant la distance et en gardant celle que la matiere accorde le mieux.

⭐⭐⭐ ET C'EST CE QUI TRANSFORME L'INSTRUMENT EN REGLE DE DECISION. La sortie n'est plus « ce
transfert est-il confirme ? » mais « de combien faut-il avancer ici ? », et la reponse ne demande
aucun maillage — ce qui est exactement ce que `97` a rendu necessaire en mesurant que deux traces
humains de la meme matiere divergent de plus d'une demi-feuille.

⚠⚠ LA DEGENERESCENCE EST LEVEE EN FIXANT k = 1. Un segment de 2p traverse par deux interstices
est indiscernable d'un segment de p traverse par un — c'est la meme matiere lue deux fois. Chercher
p ET k rendrait donc une famille de reponses equivalentes ; chercher p a k FIXE rend la distance a
la feuille VOISINE, qui est la question de l'automate.

⭐⭐ ET LE NOMBRE D'ECHANTILLONS EST CONSTANT, PAS LA LONGUEUR. Chaque segment candidat est
reechantillonne sur le meme nombre de points, donc le modele nul — qui ne depend que de ce nombre —
est le MEME pour toutes les longueurs. Sans ca, la barre changerait avec le candidat et un
candidat long paraitrait meilleur parce qu'il porte plus de points.

⚠⚠⚠ ET LE BALAYAGE NE PEUT PAS INVENTER UN PAS HORS DE SA FENETRE. Elle est DERIVEE et non
choisie : de la moitie au double du pas nominal. En deca on retrouverait la feuille de depart, au
dela on peut sauter la voisine et attraper la suivante — c'est la seule bande ou « la feuille
voisine » veut dire quelque chose, et c'est le meme raisonnement que `la_longueur_locale_du_pas`
tient deja sur l'autre objet.

Usage :
    uv run python src/nappe/le_pas_que_la_matiere_montre.py --verifier
    uv run python src/nappe/le_pas_que_la_matiere_montre.py \\
        --json docs/mesures/le_pas_que_la_matiere_montre.json
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
FERMETURE = RACINE / "docs" / "mesures" / "la_fermeture_dun_tour.json"

# ⚠ La fenetre de recherche, DERIVEE : de la moitie au double du pas nominal de cet objet.
FACTEUR_BAS = 0.5
FACTEUR_HAUT = 2.0
CANDIDATS = 31
CELLULES_PAR_BANDE = 120


def candidats_de_pas(pas_nominal_um: float, bas: float = FACTEUR_BAS,
                     haut: float = FACTEUR_HAUT, combien: int = CANDIDATS) -> np.ndarray:
    """Les longueurs candidates, de la moitie au double du pas nominal.

    ⚠ Le pas du balayage est ce qui borne la RESOLUTION du resultat : 31 candidats sur une
    fenetre de 0,5 a 2,0 pas font un cran de 5 % du pas nominal, soit ~8 µm ici — trois fois
    sous la demi-feuille, donc assez fin pour que le choix veuille dire quelque chose.
    """
    return np.linspace(bas, haut, combien) * pas_nominal_um


def pas_montre(profils: np.ndarray, longueurs: np.ndarray,
               sur_la_feuille: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pour chaque cellule, la longueur candidate que la matiere accorde le mieux.

    `profils` a la forme (cellules, candidats, echantillons). Rend la longueur retenue, le score
    de cet accord, et l'indice du candidat — l'indice servant a dire si l'optimum touche un BORD
    de la fenetre, auquel cas la reponse est « au moins ceci », pas « ceci ».

    ⭐⭐⭐ LE FILTRE EST CELUI DE `98`, IMPORTE ET NON RECOPIE. Deux implementations d'un meme
    gabarit finiraient par ne pas s'accorder sur ce qu'est un interstice, et c'est precisement le
    genre de desaccord qu'aucune des deux ne pourrait signaler.
    """
    from combien_dinterstices_traverses import gabarit  # noqa: PLC0415

    g = gabarit(1, sur_la_feuille=sur_la_feuille, echantillons=profils.shape[-1])
    z = profils - profils.mean(axis=-1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=-1, keepdims=True), 1e-12)
    scores = z @ g
    k = np.argmax(scores, axis=1)
    lignes = np.arange(len(profils))
    return longueurs[k], scores[lignes, k], k


def touche_un_bord(k: np.ndarray, combien: int = CANDIDATS) -> np.ndarray:
    """Les cellules dont l'optimum tombe sur une extremite de la fenetre.

    ⚠⚠ UN OPTIMUM AU BORD N'EST PAS UNE MESURE, C'EST UNE BUTEE. La matiere y dit « au moins
    ceci » ou « au plus ceci », et le publier comme une longueur ferait passer une limite de
    FENETRE pour une limite de matiere — le peche nº 1 de ce depot, deja paye par `98` sous la
    forme d'un seuil absolu de brillance.
    """
    return (k == 0) | (k == combien - 1)


ECHANTILLONS = 73
SUR_ECHANTILLONNAGE = 2  # le segment lu couvre le plus LONG candidat, a la meme finesse


def profils_emboites(v_long: np.ndarray, longueurs: np.ndarray,
                     echantillons: int = ECHANTILLONS) -> np.ndarray:
    """Les profils de tous les candidats, RESSAMPLES dans le plus long segment lu.

    ⭐⭐⭐ C'EST CE QUI REND LE BALAYAGE ABORDABLE, ET IL EST EXACT PLUTOT QU'APPROCHE. Les
    candidats sont EMBOITES : le segment du plus long les contient tous, donc un seul aller au
    volume suffit et chaque candidat se relit dedans. Lire 31 segments separement couterait
    dix-neuf fois `98` pour la meme information.

    ⚠⚠ ET CHAQUE CANDIDAT EST RENDU SUR LE MEME NOMBRE D'ECHANTILLONS, ce qui n'est pas un
    detail : le modele nul ne depend que de ce nombre, donc c'est ce qui garantit que la barre
    est la MEME pour toutes les longueurs. Sans ca, un candidat long porterait plus de points et
    paraitrait meilleur pour cette seule raison.
    """
    n = v_long.shape[-1]
    u = np.linspace(0.0, 1.0, n)
    fractions = longueurs / longueurs[-1]
    sortie = np.empty((len(v_long), len(longueurs), echantillons))
    for j, f in enumerate(fractions):
        cible = np.linspace(0.0, float(f), echantillons)
        for i in range(len(v_long)):
            sortie[i, j] = np.interp(cible, u, v_long[i])
    return sortie


def nul_du_balayage(longueurs: np.ndarray, tirages: int = 400, graine: int = 77,
                    echantillons: int = ECHANTILLONS) -> dict:
    """Ce que le BALAYAGE rend sur du bruit pur — le nul du meilleur de N candidats.

    ⚠⚠⚠ ET C'EST UNE CORRECTION, PAS UN RAFFINEMENT. `98` teste UN gabarit et compare son score
    au nul d'UN test. Ici on garde le MEILLEUR de trente-et-un candidats et de deux polarites,
    donc soixante-deux essais : comparer ce maximum au nul d'un seul essai est l'erreur des
    comparaisons multiples, et elle rend la mesure INCAPABLE D'ECHOUER. Mesure du defaut : la
    part de cellules « lues » sautait a **0,98** avec la mauvaise barre, alors que `98` en lit
    0,54 a 0,74 avec la bonne.

    ⭐ Le nul est donc construit exactement comme la mesure : du bruit blanc, resample dans la
    meme structure de candidats emboites, et l'on prend le meme maximum. Sa barre est plus haute,
    et c'est ce qui la rend franchissable seulement par de la matiere.
    """
    r = np.random.default_rng(graine)
    n_long = echantillons * SUR_ECHANTILLONNAGE
    out = {}
    for sigma in (2.0, 10.0, 40.0):
        v = r.normal(100.0, sigma, size=(tirages, n_long))
        profs = profils_emboites(v, longueurs, echantillons)
        _, sc_s, _ = pas_montre(profs, longueurs, sur_la_feuille=True)
        _, sc_d, _ = pas_montre(profs, longueurs, sur_la_feuille=False)
        sc = np.maximum(sc_s, sc_d)
        out[f"sigma_{sigma:.0f}"] = {
            "median": round(float(np.median(sc)), 4),
            "p95": round(float(np.percentile(sc, 95)), 4),
            "p99": round(float(np.percentile(sc, 99)), 4),
        }
    return out


def nul_par_candidat(longueurs: np.ndarray, tirages: int = 800, graine: int = 11,
                     echantillons: int = ECHANTILLONS) -> tuple[np.ndarray, np.ndarray]:
    """Ce qu'un bruit pur atteint POUR CHAQUE longueur candidate : moyenne et ecart-type.

    ⚠⚠⚠ SANS CE NUL-LA, LA RECHERCHE EST BIAISEE VERS LES COURTS, ET LE BIAIS EXPLIQUE TOUT LE
    RESULTAT. Un segment court reechantillonne sur le meme nombre de points est SUR-echantillonne,
    donc plus lisse, donc il correle mieux avec un gabarit lisse. Mesure du nul : le score moyen
    passe de **0,16** au candidat le plus court a **0,09** au plus long.

    ⛔ Consequence mesuree, et c'est ce qui a failli etre publie : sur du BRUIT PUR, la recherche
    non calibree choisit une longueur mediane de **130 a 138 µm** pour une fenetre centree a 216,
    et **147 a 156 µm** hors butee — c'est-a-dire EXACTEMENT ce qu'elle rendait sur le vrai
    volume. Le « pas que la matiere montre » etait donc indiscernable du biais de la recherche.

    ⭐⭐⭐ ET LA LECON SE GENERALISE : un modele nul doit s'appliquer a CHAQUE quantite qu'une
    recherche rapporte, pas seulement a sa confiance. Le nul du score existait et etait juste ;
    celui de la longueur CHOISIE manquait, et c'est la que vivait l'artefact.

    Apres calibration, la meme recherche sur du bruit pur choisit **207,6 µm** pour un centre de
    fenetre a 216, avec un histogramme quasi plat.
    """
    from combien_dinterstices_traverses import gabarit  # noqa: PLC0415

    r = np.random.default_rng(graine)
    n_long = echantillons * SUR_ECHANTILLONNAGE
    v = r.normal(100.0, 10.0, size=(tirages, n_long))
    profs = profils_emboites(v, longueurs, echantillons)
    z = profs - profs.mean(axis=-1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=-1, keepdims=True), 1e-12)
    scores = np.maximum(z @ gabarit(1, True, echantillons),
                        z @ gabarit(1, False, echantillons))
    return scores.mean(axis=0), np.maximum(scores.std(axis=0), 1e-9)


def pas_montre_calibre(profils: np.ndarray, longueurs: np.ndarray, mu: np.ndarray,
                       sd: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                                np.ndarray]:
    """La longueur retenue apres CALIBRATION par le nul de chaque candidat.

    Rend la longueur, l'ecart au nul en ecarts-types, l'indice du candidat, et si l'optimum
    partait du gabarit « sur la feuille ».

    ⭐⭐ LE SCORE COMPARE EST UN ECART AU NUL DE SA PROPRE LONGUEUR, donc les candidats sont
    comparables entre eux — ce qu'ils n'etaient pas, un court partant avec 0,07 d'avance.
    """
    from combien_dinterstices_traverses import gabarit  # noqa: PLC0415

    n = profils.shape[-1]
    z = profils - profils.mean(axis=-1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=-1, keepdims=True), 1e-12)
    s_sur = z @ gabarit(1, True, n)
    s_dans = z @ gabarit(1, False, n)
    brut = np.maximum(s_sur, s_dans)
    calibre = (brut - mu[None, :]) / sd[None, :]
    k = np.argmax(calibre, axis=1)
    lignes = np.arange(len(profils))
    return (longueurs[k], calibre[lignes, k], k, s_sur[lignes, k] >= s_dans[lignes, k])


def nul_du_balayage_calibre(longueurs: np.ndarray, mu: np.ndarray, sd: np.ndarray,
                            tirages: int = 400, graine: int = 77) -> dict:
    """La barre : ce que le maximum CALIBRE atteint sur du bruit pur.

    ⚠ Elle est en ecarts-types du nul, pas en correlation, parce que c'est cette quantite-la
    qu'on maximise desormais. Reutiliser la barre du score brut comparerait deux choses
    differentes.
    """
    r = np.random.default_rng(graine)
    n_long = ECHANTILLONS * SUR_ECHANTILLONNAGE
    out = {}
    for sigma in (2.0, 10.0, 40.0):
        v = r.normal(100.0, sigma, size=(tirages, n_long))
        _, z, _, _ = pas_montre_calibre(profils_emboites(v, longueurs), longueurs, mu, sd)
        out[f"sigma_{sigma:.0f}"] = {"median": round(float(np.median(z)), 3),
                                     "p95": round(float(np.percentile(z, 95)), 3),
                                     "p99": round(float(np.percentile(z, 99)), 3)}
    return out


def _distribution_contre_le_nul(lignes: list[dict], longueurs: np.ndarray, mu: np.ndarray,
                                sd: np.ndarray, barre: float, tirages: int = 3000,
                                graine: int = 3) -> dict:
    """La distribution des longueurs retenues differe-t-elle de celle du bruit pur ?

    ⭐⭐⭐ C'EST LE CONTROLE QUI DECIDE SI LA LONGUEUR EST UNE MESURE. Un test de
    Kolmogorov-Smirnov entre les longueurs retenues sur le vrai volume et celles que le MEME
    balayage retient sur du bruit pur, au-dessus de la MEME barre. S'ils ne different pas, la
    longueur ne porte rien et seul « la matiere a repondu » survit.

    ⚠ Le nul passe par la meme barre et le meme rejet des butees : comparer une population
    filtree a une population brute comparerait deux choses.
    """
    from scipy import stats  # noqa: PLC0415

    reelles = [x["pas_median_um"] for x in lignes
               if x.get("pas_median_um") is not None]
    if len(reelles) < 5:
        return {"message": "trop peu de bandes lisibles"}
    r = np.random.default_rng(graine)
    v = r.normal(100.0, 10.0, size=(tirages, ECHANTILLONS * SUR_ECHANTILLONNAGE))
    lu, z, k, _ = pas_montre_calibre(profils_emboites(v, longueurs), longueurs, mu, sd)
    garde = (z > barre) & (~touche_un_bord(k, len(longueurs)))
    if int(garde.sum()) < 10:
        # ⚠ Un nul qui ne franchit presque jamais la barre est un BON signe pour la barre, mais
        # il prive le test de comparaison. Le dire vaut mieux que rendre un p sur dix points.
        return {"nul_au_dessus_de_la_barre": int(garde.sum()), "tirages": tirages,
                "message": "le nul franchit trop rarement la barre pour un test de distribution"}
    st = stats.ks_2samp(np.asarray(reelles), lu[garde])
    return {
        "nul_au_dessus_de_la_barre": int(garde.sum()), "tirages": tirages,
        "part_du_nul_au_dessus_de_la_barre": round(float(garde.mean()), 4),
        "mediane_reelle_um": round(float(np.median(reelles)), 1),
        "mediane_du_nul_um": round(float(np.median(lu[garde])), 1),
        "kolmogorov_smirnov_D": round(float(st.statistic), 3),
        "kolmogorov_smirnov_p": float(f"{st.pvalue:.3g}"),
        "differe": bool(st.pvalue < 0.05),
    }


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def mesurer(cellules: int = CELLULES_PAR_BANDE, graine: int = 41,
            bandes_max: int | None = None, fils: int = 32) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import appliquer, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    co = ({(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
          if CONTINUITE.is_file() else {})
    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    longueurs = candidats_de_pas(C.PAS_UM)
    # ⭐⭐⭐ DEUX NULS, ET IL FAUT LES DEUX. Celui PAR CANDIDAT retire le biais vers les courts —
    # sans lui la longueur rendue est indiscernable de celle que le bruit produit. Celui du
    # BALAYAGE donne la barre du maximum, parce qu'on garde le meilleur de soixante-deux essais
    # et que la barre d'un seul essai serait l'erreur des comparaisons multiples.
    mu, sd = nul_par_candidat(longueurs)
    nul = nul_du_balayage_calibre(longueurs, mu, sd)
    nul_brut = nul_du_balayage(longueurs)
    nul_dun_seul_essai = C.accord_du_bruit_pur()
    barre = max(x["p99"] for x in nul.values())
    n_long = ECHANTILLONS * SUR_ECHANTILLONNAGE

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    lignes = []
    for x in bandes:
        cle = (x["de"], x["a"])
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 20:
            continue
        # ⚠⚠ LE SEGMENT LU COUVRE LE PLUS LONG CANDIDAT, et la geometrie vient de `98` — meme
        # centre interpole en z, meme direction radiale a z constant. Deux geometries feraient
        # deux droites differentes sous un seul nom.
        seg = C.segments(a, ok, bords, cx, cy, ind, pas_um=float(longueurs[-1]))
        # `segments` echantillonne sur C.ECHANTILLONS ; on veut le double pour resampler.
        t = np.linspace(0.0, 1.0, n_long)
        p0, p1 = seg[:, 0, :], seg[:, -1, :]
        seg = p0[:, None, :] + (p1 - p0)[:, None, :] * t[None, :, None]
        zyx = np.rint(appliquer(m, seg)).astype(np.int64)
        dedans = vol.dans_le_volume(zyx.reshape(-1, 3)).reshape(zyx.shape[:2]).all(axis=1)
        if int(dedans.sum()) < 15:
            lignes.append(dict(de=x["de"], a=x["a"], rayon_mm=al.get(cle, {}).get("rayon_mm"),
                               mesurable=False, cellules=0))
            continue
        v = vol.lire(zyx[dedans].reshape(-1, 3), fils=fils).reshape(int(dedans.sum()), n_long)
        fini = np.isfinite(v).all(axis=1)
        if int(fini.sum()) < 15:
            lignes.append(dict(de=x["de"], a=x["a"], rayon_mm=al.get(cle, {}).get("rayon_mm"),
                               mesurable=False, cellules=int(fini.sum())))
            continue
        v = v[fini]
        profs = profils_emboites(v, longueurs)
        # ⚠ LES DEUX POLARITES SONT ESSAYEES, et la meilleure gagne : `98` a mesure que la
        # moitie des cellules partent d'un INTERSTICE, donc imposer « sur la feuille » ferait
        # lire la moitie des cellules avec le mauvais gabarit.
        lu, sc, k, sur = pas_montre_calibre(profs, longueurs, mu, sd)
        bord = touche_un_bord(k, len(longueurs))
        # ⭐ « La matiere a repondu » et « l'optimum n'est pas une butee » sont DEUX conditions,
        # et les confondre ferait lire une butee comme une mesure.
        lisible = (sc > barre) & ~bord
        d = dict(
            de=x["de"], a=x["a"], mesurable=True,
            rayon_mm=al.get(cle, {}).get("rayon_mm"),
            desalignement=al.get(cle, {}).get("rapport_au_plancher"),
            continuite=co.get(cle, {}).get("rapport_interieur"),
            cellules=int(len(v)),
            part_lue=round(float((sc > barre).mean()), 3),
            part_en_butee=round(float(bord.mean()), 3),
            part_utilisable=round(float(lisible.mean()), 3),
            accord_median=round(float(np.median(sc)), 4),
        )
        if int(lisible.sum()) >= 10:
            pas = lu[lisible]
            d.update({
                "pas_median_um": round(float(np.median(pas)), 1),
                "pas_p10_um": round(float(np.percentile(pas, 10)), 1),
                "pas_p90_um": round(float(np.percentile(pas, 90)), 1),
                # ⭐⭐ L'ECART AU NOMINAL EST LA QUANTITE QUI SERT A UN AUTOMATE : c'est de
                # combien il se tromperait en avancant du pas publie plutot que du pas montre.
                "ecart_au_nominal": round(float(np.median(pas) / C.PAS_UM), 3),
                "part_a_plus_dun_dixieme_du_nominal": round(
                    float(np.mean(np.abs(pas - C.PAS_UM) > 0.1 * C.PAS_UM)), 3),
                "part_partant_sur_la_feuille": round(float(sur[lisible].mean()), 3),
            })
        else:
            d["pas_median_um"] = None
        lignes.append(d)

    # ⭐⭐⭐ LE CONTROLE QUI DONNE UN SENS A LA LONGUEUR RENDUE : sa distribution doit differer
    # de celle que le NUL produit. Sans lui, « le pas montre vaut 216 µm » ne dit rien — la
    # premiere version de ce fichier rendait 147 µm sur le reel ET 147 sur du bruit pur, et
    # seule cette comparaison-la pouvait le montrer.
    contre_le_nul = _distribution_contre_le_nul(lignes, longueurs, mu, sd, barre)

    mesurees = [x for x in lignes if x["mesurable"] and x.get("pas_median_um") is not None]
    if not mesurees:
        return {"message": "aucune bande lisible dans le volume fin"}

    ray = [x["rayon_mm"] for x in mesurees if x["rayon_mm"] is not None]
    pas = [x["pas_median_um"] for x in mesurees if x["rayon_mm"] is not None]
    rup = [x["continuite"] for x in mesurees if x["continuite"] is not None]
    pasc = [x["pas_median_um"] for x in mesurees if x["continuite"] is not None]
    utl = [x["part_utilisable"] for x in mesurees if x["continuite"] is not None]

    tri = sorted([x for x in mesurees if x["rayon_mm"] is not None],
                 key=lambda z: z["rayon_mm"])
    t = max(1, len(tri) // 3)
    tiers = {"coeur": tri[:t], "milieu": tri[t:2 * t], "bord": tri[2 * t:]}
    med = lambda v, k: round(float(np.median([y[k] for y in v])), 3)  # noqa: E731
    return {
        "fragment": C.OBJET, "volume_fin": C.ZARR_FIN.rsplit("/", 1)[-1],
        "pas_nominal_um": C.PAS_UM, "voxel_fin_um": C.VOXEL_FIN_UM,
        "fenetre_de_recherche_um": [round(float(longueurs[0]), 1),
                                    round(float(longueurs[-1]), 1)],
        "cran_du_balayage_um": round(float(longueurs[1] - longueurs[0]), 1),
        "candidats": len(longueurs), "echantillons_par_candidat": ECHANTILLONS,
        "barre_du_nul": round(float(barre), 4),
        "la_longueur_differe_du_nul": contre_le_nul,
        "nul_du_balayage_calibre": nul,
        # ⛔ LE NUL PAR CANDIDAT, PUBLIE : c'est lui qui montre le biais vers les courts, de
        # 0,16 au plus court a 0,09 au plus long.
        "nul_par_candidat": {"le_plus_court": round(float(mu[0]), 4),
                             "le_plus_long": round(float(mu[-1]), 4),
                             "rapport": round(float(mu[0] / max(mu[-1], 1e-9)), 2)},
        "nul_du_balayage_non_calibre": nul_brut,
        # ⚠⚠ LE NUL D'UN SEUL ESSAI EST PUBLIE A COTE : l'ecart entre les deux barres EST la
        # mesure de l'erreur qu'aurait faite une comparaison naive.
        "nul_dun_seul_essai": nul_dun_seul_essai,
        "barre_dun_seul_essai": round(
            float(max(x["p99"] for x in nul_dun_seul_essai.values())), 4),
        "bandes": len(lignes), "bandes_lisibles": len(mesurees),
        "cellules_par_bande": cellules,
        "lignes": lignes,
        "correlations": {
            "pas_montre_contre_rayon": correlation(pas, ray),
            "pas_montre_contre_continuite": correlation(pasc, rup),
            "part_utilisable_contre_continuite": correlation(utl, rup),
        },
        "par_tiers": {k: {"bandes": len(v),
                          "pas_median_um": med(v, "pas_median_um"),
                          "ecart_au_nominal": med(v, "ecart_au_nominal"),
                          "part_utilisable": med(v, "part_utilisable"),
                          "part_en_butee": med(v, "part_en_butee"),
                          "part_a_plus_dun_dixieme_du_nominal": med(
                              v, "part_a_plus_dun_dixieme_du_nominal"),
                          "part_partant_sur_la_feuille": med(
                              v, "part_partant_sur_la_feuille"),
                          "continuite": med(v, "continuite")}
                      for k, v in tiers.items() if v},
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · pas nominal {r['pas_nominal_um']} µm · fenêtre "
          f"{r['fenetre_de_recherche_um'][0]} à {r['fenetre_de_recherche_um'][1]} µm par crans "
          f"de {r['cran_du_balayage_um']} · {r['bandes_lisibles']}/{r['bandes']} bandes")
    print(f"  barre du nul DU BALAYAGE : {r['barre_du_nul']} — contre "
          f"{r['barre_dun_seul_essai']} pour un seul essai\n")
    print(f"{'bande':>10} {'rayon':>6} {'lue':>6} {'butée':>7} {'utilis.':>8} "
          f"{'pas µm':>8} {'p10–p90':>14} {'/nominal':>9} {'>10 %':>7} {'continuité':>11}")
    for x in r["lignes"]:
        if not x["mesurable"] or x.get("pas_median_um") is None:
            print(f"  w{x['de']:03d}-{x['a']:03d} "
                  f"{(x['rayon_mm'] or float('nan')):>6.1f} {'ILLISIBLE':>60}")
            continue
        print(f"  w{x['de']:03d}-{x['a']:03d} {(x['rayon_mm'] or float('nan')):>6.1f} "
              f"{x['part_lue']:>6.2f} {x['part_en_butee']:>7.2f} {x['part_utilisable']:>8.2f} "
              f"{x['pas_median_um']:>8.1f} "
              f"{x['pas_p10_um']:>6.1f}–{x['pas_p90_um']:<7.1f} "
              f"{x['ecart_au_nominal']:>9.2f} "
              f"{x['part_a_plus_dun_dixieme_du_nominal']:>7.2f} "
              f"{(x['continuite'] or float('nan')):>11.1f}")
    p, c = r["par_tiers"], r["correlations"]
    print(f"\n{'':>16} {'utilis.':>8} {'butée':>7} {'pas µm':>8} {'/nominal':>9} "
          f"{'>10 %':>7} {'continuité':>11}")
    for k in ("coeur", "milieu", "bord"):
        if k in p:
            print(f"{k:>16} {p[k]['part_utilisable']:>8.2f} {p[k]['part_en_butee']:>7.2f} "
                  f"{p[k]['pas_median_um']:>8.1f} {p[k]['ecart_au_nominal']:>9.2f} "
                  f"{p[k]['part_a_plus_dun_dixieme_du_nominal']:>7.2f} "
                  f"{p[k]['continuite']:>11.1f}")
    print(f"\n{'':>36} {'rayon':>8} {'continuité':>12}")
    print(f"{'pas montré':>36} {c['pas_montre_contre_rayon']:>+8.3f} "
          f"{c['pas_montre_contre_continuite']:>+12.3f}")
    print(f"{'part utilisable':>36} {'':>8} "
          f"{c['part_utilisable_contre_continuite']:>+12.3f}")
    # ⭐⭐⭐ LA CORRECTION QUI PORTE LE FICHIER, IMPRIMEE AVEC SON AMPLEUR.
    print(f"\n★★★ LA BARRE EST CELLE DU NUL DU BALAYAGE ({r['barre_du_nul']}), PAS CELLE D'UN")
    print(f"   SEUL ESSAI ({r['barre_dun_seul_essai']}). On garde le meilleur de "
          f"{r['candidats']} candidats × 2 polarités,")
    print("   donc comparer ce maximum à la barre d'un seul test est l'erreur des comparaisons")
    print("   multiples — et elle rend la mesure INCAPABLE D'ÉCHOUER : avec la mauvaise barre,")
    print("   la part lue sautait à 0,98.")
    cn = r.get("la_longueur_differe_du_nul", {})
    if "kolmogorov_smirnov_p" in cn:
        print(f"\n★★★ ET LA LONGUEUR EST UNE MESURE, PAS UN BIAIS : sa distribution DIFFÈRE de")
        print(f"   celle du nul (Kolmogorov-Smirnov D={cn['kolmogorov_smirnov_D']}, "
              f"p={cn['kolmogorov_smirnov_p']}), médiane {cn['mediane_reelle_um']} µm contre")
        print(f"   {cn['mediane_du_nul_um']} au nul, et la barre ne laisse passer que "
              f"{100 * cn['part_du_nul_au_dessus_de_la_barre']:.1f} % du bruit pur.")
    print(f"\n⛔⛔ LE BIAIS QUE LA CALIBRATION CORRIGE, ET IL AVAIT FAILLI ÊTRE PUBLIÉ : un")
    print(f"   segment court rééchantillonné est SUR-échantillonné, donc plus lisse, donc il")
    print(f"   corrèle mieux — le nul passe de {r['nul_par_candidat']['le_plus_court']} au plus "
          f"court à {r['nul_par_candidat']['le_plus_long']} au plus long,")
    print(f"   soit ×{r['nul_par_candidat']['rapport']}. Sans calibration, la recherche rendait "
          f"147 µm sur le VRAI")
    print("   volume et 147 µm sur du BRUIT PUR — indiscernables. ⭐ La leçon se généralise : un")
    print("   modèle nul doit s'appliquer à CHAQUE quantité qu'une recherche rapporte, pas")
    print("   seulement à sa confiance.")
    print("\n⚠⚠ ET UNE BUTÉE N'EST PAS UNE MESURE : quand l'optimum tombe sur une extrémité de la")
    print("   fenêtre, la matière dit « au moins ceci », pas « ceci ». Ces cellules sont comptées")
    print("   à part et retirées de l'utilisable, sinon une limite de FENÊTRE se publierait")
    print("   comme une limite de matière.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415

    longueurs = candidats_de_pas(C.PAS_UM)
    v("la fenêtre est dérivée du pas nominal, de la moitié au double",
      abs(longueurs[0] / C.PAS_UM - FACTEUR_BAS) < 1e-9
      and abs(longueurs[-1] / C.PAS_UM - FACTEUR_HAUT) < 1e-9,
      f"{longueurs[0]:.1f} à {longueurs[-1]:.1f} µm")
    # ⚠ Le cran borne la resolution du resultat : il doit rester bien sous la demi-feuille.
    cran = float(longueurs[1] - longueurs[0])
    v("... et son cran reste sous la demi-feuille", cran < 0.5 * C.PAS_UM / 3,
      f"{cran:.1f} µm pour une demi-feuille de {0.5 * C.PAS_UM:.1f}")

    # --- la recherche, sur des profils dont on connait le pas -----------------------------
    n = 73
    for vrai in (110.0, 173.0, 250.0, 320.0):
        profs = np.stack([[100.0 + 40.0 * np.cos(2 * np.pi * np.linspace(0, L, n) / vrai)
                           for L in longueurs]])
        lu, sc, k = pas_montre(profs, longueurs)
        v(f"un pas injecté de {vrai:.0f} µm est retrouvé au cran près",
          abs(float(lu[0]) - vrai) <= cran, f"lu {float(lu[0]):.1f}")
        v(f"... avec un accord franc à {vrai:.0f} µm", float(sc[0]) > 0.9,
          f"{float(sc[0]):.3f}")
    # ⚠⚠ UN PAS HORS FENETRE DOIT SORTIR EN BUTEE, pas en valeur : la matiere dit « au moins ».
    hors = np.stack([[100.0 + 40.0 * np.cos(2 * np.pi * np.linspace(0, L, n) / 500.0)
                      for L in longueurs]])
    _, _, k_hors = pas_montre(hors, longueurs)
    v("un pas HORS de la fenêtre ressort en butée, pas en valeur",
      bool(touche_un_bord(k_hors, len(longueurs))[0]), f"indice {int(k_hors[0])}")

    # --- l'emboîtement, qui rend le balayage abordable ------------------------------------
    # ⭐⭐ LE RESSAMPLE DOIT RENDRE CE QU'UNE LECTURE DIRECTE AURAIT RENDU, sinon l'economie
    # serait payee en exactitude.
    n_long = ECHANTILLONS * SUR_ECHANTILLONNAGE
    vrai = 173.0
    v_long = np.stack([100.0 + 40.0 * np.cos(
        2 * np.pi * np.linspace(0, float(longueurs[-1]), n_long) / vrai)])
    profs = profils_emboites(v_long, longueurs)
    direct = np.stack([[100.0 + 40.0 * np.cos(2 * np.pi * np.linspace(0, L, ECHANTILLONS)
                                              / vrai) for L in longueurs]])
    ecart = float(np.max(np.abs(profs - direct)))
    v("le profil ressamplé égale une lecture directe", ecart < 1.0, f"écart max {ecart:.3f}")
    v("... et tous les candidats portent le MÊME nombre d'échantillons",
      profs.shape[1] == len(longueurs) and profs.shape[2] == ECHANTILLONS,
      str(profs.shape))

    # --- LE NUL DU BALAYAGE, ET C'EST LA CORRECTION QUI PORTE LE FICHIER ------------------
    nul = nul_du_balayage(longueurs, tirages=200)
    barre = max(x["p99"] for x in nul.values())
    barre1 = max(x["p99"] for x in C.accord_du_bruit_pur(tirages=200).values())
    # ⚠⚠⚠ SANS CE CONTROLE, LA MESURE SERAIT INCAPABLE D'ECHOUER : garder le meilleur de
    # soixante-deux essais et le comparer a la barre d'UN essai laisse passer presque tout.
    v("la barre du BALAYAGE est plus haute que celle d'un seul essai",
      barre > 1.3 * barre1, f"{barre:.4f} contre {barre1:.4f}")
    medianes = [x["median"] for x in nul.values()]
    v("... et le nul du balayage ne dépend pas de l'écart-type",
      max(medianes) - min(medianes) < 0.03, str(medianes))
    # ⭐ Et un vrai pas doit franchir la barre HAUTE, sinon l'instrument ne servirait a rien.
    bruite = np.stack([[100.0 + 40.0 * np.cos(2 * np.pi * np.linspace(0, L, n) / 173.0)
                        + np.random.default_rng(9 + j).normal(0, 10.0, n)
                        for L in longueurs] for j in range(60)])
    _, sc_b, _ = pas_montre(bruite, longueurs)
    v("un vrai pas bruité franchit quand même la barre haute",
      float(np.median(sc_b)) > barre, f"{float(np.median(sc_b)):.3f} contre {barre:.4f}")

    r = mesurer(cellules=40, bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le volume fin", r["bandes_lisibles"] >= 1,
      f"{r['bandes_lisibles']}/{r['bandes']}")
    v("les DEUX barres sont publiées, pas seulement celle qui sert",
      r["barre_du_nul"] > r["barre_dun_seul_essai"],
      f"{r['barre_du_nul']} contre {r['barre_dun_seul_essai']}")
    v("les butées sont comptées à part de l'utilisable",
      all(x["part_utilisable"] <= x["part_lue"] for x in r["lignes"] if x["mesurable"]))
    # ⭐⭐⭐ LE CONTROLE QUI DECIDE SI LA LONGUEUR EST UNE MESURE, ET IL EST PUBLIE.
    v("la distribution des longueurs est confrontée au nul",
      "la_longueur_differe_du_nul" in r)
    cn = r["la_longueur_differe_du_nul"]
    if "kolmogorov_smirnov_p" in cn:
        v("... et elle en diffère, sinon la longueur ne porterait rien",
          cn["differe"], f"D={cn['kolmogorov_smirnov_D']} p={cn['kolmogorov_smirnov_p']}")
        v("... la barre laissant passer moins d'un vingtième du nul",
          cn["part_du_nul_au_dessus_de_la_barre"] < 0.05,
          str(cn["part_du_nul_au_dessus_de_la_barre"]))
    # ⛔ LE BIAIS REFUTE EST PUBLIE : le rapport du nul entre le candidat le plus court et le
    # plus long EST l'ampleur de ce que la calibration corrige.
    v("le biais vers les courts est publié avec son ampleur",
      r["nul_par_candidat"]["rapport"] > 1.3, str(r["nul_par_candidat"]))
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

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
