#!/usr/bin/env python3
"""Qu'est-ce qui separe les deux populations de `107` ? — la question du graal, posee aux etapes.

⚠⚠⚠ POURQUOI CE FICHIER. `107` a mesure que les marches se separent en DEUX populations : les unes
franchissent ~1,1 feuille par pas — ce que le marcheur doit faire — les autres ~0,12, c'est-a-dire
rien. Les deux selecteurs se separent de la meme facon, donc c'est une propriete de la MATIERE. Et
**aucun critere existant ne les distingue** : le score du trajet est PLUS HAUT pour les marches qui
ne mesurent rien, donc un seuil de score ecarterait le BON mode. Trouver ce qui les separe EST le
graal — ce serait le signal qu'un automate lit pour savoir s'il est encore sur la feuille.

⭐⭐⭐ CE QUI REND CETTE TRANCHE GRATUITE. `107` a garde ses etapes, et chaque etape porte des
quantites mesurees SUR LE CUBE, avant qu'aucun profil ne soit ajuste : le desaccord des deux
demi-blocs, la planarite du tenseur, le pas retenu, l'accord de l'interstice, la butee. Le registre
du trajet — celui qui DEFINIT les deux modes — est calcule apres, sur la polyligne entiere. Les
candidats sont donc mesures INDEPENDAMMENT de la quantite qu'ils doivent predire, ce que la
consigne de reprise exigeait explicitement. Zero lecture distante, zero seconde de course.

⚠⚠⚠ ET LE PIEGE DE CETTE TRANCHE A UN NOM : un seuil regle sur les donnees qui le jugent. Avec
huit candidats et quarante-huit trajets, un test par candidat sans correction declare un gagnant
sur du BRUIT PUR une fois sur trois — et ce chiffre est MESURE ici plutot qu'invoque
(`combien_de_faux_gagnants_sans_correction`). Trois gardes en decoulent :
    - la famille de candidats est DECLAREE AVANT de regarder, dans `CANDIDATS`, et publiee
      entiere : le gagnant seul serait le survivant d'une selection invisible ;
    - la correction est une permutation sur le MAXIMUM de la famille, donc exacte et sans
      hypothese d'independance entre candidats ;
    - un seuil, s'il en sort un, est chiffre EN COUT (combien de bonnes marches il jette) et sa
      version hors echantillon est rendue a cote de la version en echantillon.

⚠⚠ DEUX TEMOINS ENCADRENT LA FAMILLE, ET ILS N'EN FONT PAS PARTIE. Le temoin POSITIF est une
quantite dont on sait qu'elle doit separer si l'instrument a la moindre puissance a cet effectif ;
le temoin NEGATIF est le score du trajet, dont `107` a mesure qu'il separe A L'ENVERS. Une batterie
qui ne rendrait aucun des deux ne mesurerait rien du tout.

Usage :
    uv run python src/nappe/ce_qui_separe_les_deux_populations.py --verifier
    uv run python src/nappe/ce_qui_separe_les_deux_populations.py \\
        --json docs/mesures/ce_qui_separe_les_deux_populations.json
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

CHEMIN_DE_107 = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"

# ⚠⚠ LE SEUIL DE MODE VIENT DE `107` ET N'EST PAS REGLE ICI. Il vaut la moitie du compte de pas
# attendu ; le redefinir ferait de cette tranche le juge de sa propre partition.
PART_DU_COMPTE_ATTENDU = 0.5

TIRAGES = 5000
GRAINE = 108

# ⚠⚠⚠ LA FAMILLE EST DECLAREE ICI, AVANT TOUTE MESURE, ET C'EST LA GARDE PRINCIPALE DE LA TRANCHE.
# Chaque entree porte : la cle rendue par `resume_dun_trajet`, le libelle publie, et le ROLE.
#   - « candidat » : mesure sur le cube ou sur les directions, donc AVANT et INDEPENDAMMENT du
#     registre du trajet qui definit les deux modes. Ce sont les seuls qui entrent dans le maximum
#     de la famille, donc les seuls que la correction protege.
#   - « temoin_positif » : doit separer si l'instrument a de la puissance a cet effectif.
#   - « temoin_negatif » : sait separer A L'ENVERS (`107`), donc il verifie que le SENS est lu.
# Ajouter un candidat apres avoir vu les resultats serait exactement la faute que la correction
# existe pour empecher ; la liste se modifie avant une course, jamais apres.
CANDIDATS = (
    ("desaccord_median_deg", "désaccord médian des demi-blocs (°)", "candidat"),
    ("desaccord_max_deg", "désaccord maximal des demi-blocs (°)", "candidat"),
    ("planarite_mediane", "planarité médiane du tenseur", "candidat"),
    ("planarite_min", "planarité minimale du tenseur", "candidat"),
    ("virage_median_deg", "virage médian entre deux pas (°)", "candidat"),
    ("dispersion_du_pas", "dispersion du pas retenu (écart interquartile / médiane)", "candidat"),
    ("pas_median_um", "pas médian retenu (µm)", "candidat"),
    ("score_du_balayage_median", "score médian du balayage", "candidat"),
    ("accord_de_linterstice_median", "accord médian de l'interstice", "candidat"),
    ("part_en_butee", "part des pas dont la fraction est en butée", "candidat"),
    ("rayon_mm", "rayon de la bande (mm)", "candidat"),
    # ⚠⚠⚠ LE TEMOIN POSITIF EST LA QUANTITE QUI DEFINIT LES MODES, donc sa force DOIT valoir un.
    # Ce n'est pas une hypothese sur la matiere mais un controle de plomberie : si elle ne separe
    # pas parfaitement, c'est que la reduction, l'appariement ou le seuil se sont perdus en route,
    # et tout le reste du tableau est a jeter avant d'etre lu.
    ("feuilles_par_pas", "feuilles franchies par pas (ce qui DÉFINIT les modes)", "temoin_positif"),
    # ⚠⚠⚠ ET CELUI-CI ETAIT DECLARE COMME TEMOIN POSITIF, A TORT. Je l'avais suppose tautologique
    # — « qui franchit plus de feuilles a marche plus loin » — et la mesure l'a refute : le mode
    # qui ne compte RIEN marche PLUS LOIN (1276 µm contre 1189). Il reste publie, hors famille,
    # sous son vrai statut : une hypothese sur la matiere, refutee. La corriger en la faisant
    # entrer dans la famille APRES avoir vu les resultats serait exactement la faute que la
    # correction existe pour empecher ; elle reste donc dehors, et ne peut rien gagner.
    ("longueur_um", "longueur parcourue (µm) — déclarée tautologique, RÉFUTÉE", "hypothese_refutee"),
    ("score_du_trajet", "score de l'ajustement du trajet", "temoin_negatif"),
)

NOMS_DES_CANDIDATS = tuple(c for c, _, r in CANDIDATS if r == "candidat")


def _mediane(v) -> float | None:
    """La mediane d'une liste qui peut etre vide ou pleine de None."""
    x = [float(t) for t in v if t is not None and np.isfinite(float(t))]
    return float(np.median(x)) if x else None


def _dispersion(v) -> float | None:
    """L'ecart interquartile rapporte a la mediane, donc sans dimension.

    ⚠ Elle est rapportee a la MEDIANE et non a la moyenne parce qu'un pas aberrant deplace la
    seconde ; et l'ecart interquartile plutot que l'ecart-type pour la meme raison. Sur six
    valeurs, un seul pas absurde suffirait a faire d'un marcheur regulier un marcheur erratique.
    """
    x = np.asarray([float(t) for t in v if t is not None and np.isfinite(float(t))])
    if x.size < 3:
        return None
    med = float(np.median(x))
    if abs(med) < 1e-12:
        return None
    return float(np.subtract(*np.percentile(x, [75, 25]))) / abs(med)


def _virage_median(etapes: list[dict]) -> float | None:
    """L'angle median entre les directions de deux pas CONSECUTIFS.

    ⚠ Le signe d'un vecteur propre est arbitraire — `106` a paye cet oubli — donc l'angle est pris
    sur le produit scalaire ABSOLU. Le meme choix que `virage_entre_pas` de `107`, et il est refait
    ici plutot qu'importe parce que cette tranche doit tourner sur un fichier, sans le lecteur.
    """
    d = [np.asarray(x["direction"], dtype=np.float64) for x in etapes if "direction" in x]
    ang = []
    for a, b in zip(d, d[1:]):
        na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
        if na < 1e-12 or nb < 1e-12:
            continue
        ang.append(float(np.rad2deg(np.arccos(min(abs(float(a @ b) / (na * nb)), 1.0)))))
    return float(np.median(ang)) if ang else None


def resume_dun_trajet(marche: dict, rayon_mm: float, selecteur: str,
                      bande: int) -> dict | None:
    """Reduit une marche de `107` a UNE valeur par candidat, plus son mode.

    ⚠⚠ LA REDUCTION EST DECLAREE AVEC LE CANDIDAT, PAS CHOISIE APRES. Mediane pour ce qui doit
    resumer, maximum pour ce qui doit attraper un seul mauvais pas, minimum pour ce qui doit
    attraper une seule cellule sans plan. Choisir la reduction apres avoir vu laquelle separe
    serait la meme faute qu'ajouter un candidat, deguisee en detail technique.

    ⚠ Un trajet dont le registre n'est pas decidable est ECARTE plutot que compte dans un mode :
    « le profil est plat » n'est pas « la marche n'a rien franchi », c'est « la mesure n'a pas eu
    lieu ». Les confondre mettrait dans le mode bas des marches dont on ne sait rien.
    """
    t = marche.get("trajet_entier") or {}
    if not t.get("decidable"):
        return None
    e = marche.get("etapes") or []
    if not e:
        return None
    return {
        "bande": int(bande), "selecteur": selecteur,
        "feuilles_franchies": float(t["feuilles_franchies"]),
        "pas_parcourus": int(t["pas_parcourus"]),
        "feuilles_par_pas": float(t["feuilles_franchies"]) / max(int(t["pas_parcourus"]), 1),
        # ⚠ La suite des scores de pas est gardee ENTIERE, pas seulement sa mediane : elle repond a
        # une question que la mediane ne peut pas poser — apres combien de pas le sait-on ?
        "scores_du_balayage": [None if x.get("score_du_balayage") is None
                               else float(x["score_du_balayage"]) for x in e],
        "desaccord_median_deg": _mediane([x.get("desaccord_des_moities_deg") for x in e]),
        "desaccord_max_deg": max((float(x["desaccord_des_moities_deg"]) for x in e
                                  if x.get("desaccord_des_moities_deg") is not None),
                                 default=None),
        "planarite_mediane": _mediane([x.get("planarite") for x in e]),
        "planarite_min": min((float(x["planarite"]) for x in e
                              if x.get("planarite") is not None), default=None),
        "virage_median_deg": _virage_median(e),
        "dispersion_du_pas": _dispersion([x.get("pas_um") for x in e]),
        "pas_median_um": _mediane([x.get("pas_um") for x in e]),
        "score_du_balayage_median": _mediane([x.get("score_du_balayage") for x in e]),
        "accord_de_linterstice_median": _mediane([x.get("accord_de_linterstice") for x in e]),
        "part_en_butee": float(np.mean([1.0 if x.get("fraction_en_butee") else 0.0
                                        for x in e])),
        "rayon_mm": float(rayon_mm),
        "longueur_um": float(t["longueur_um"]),
        "score_du_trajet": float(t["score"]),
    }


def trajets_de_107(brut: dict, selecteurs=("calibre", "deux_roles")) -> list[dict]:
    """Aplatit la mesure de `107` en une liste de trajets resumes."""
    out = []
    for ligne in brut.get("lignes", []):
        for cellule in ligne.get("detail", []):
            for sel in selecteurs:
                m = cellule.get(sel)
                if not m:
                    continue
                r = resume_dun_trajet(m, float(ligne["rayon_mm"]), sel, int(ligne["de"]))
                if r is not None:
                    out.append(r)
    return out


def modes(trajets: list[dict], part: float = PART_DU_COMPTE_ATTENDU) -> np.ndarray:
    """Le mode de chaque trajet : True au-dessus du seuil, False au-dessous.

    ⚠ Le seuil vaut `part` fois le compte de pas ATTENDU du trajet, exactement comme `107` le
    definit. Il est recalcule par trajet parce qu'une marche plus courte attend moins.
    """
    return np.asarray([x["feuilles_franchies"] >= part * x["pas_parcourus"]
                       for x in trajets], dtype=bool)


def le_vide_entre_les_modes(trajets: list[dict],
                            part: float = PART_DU_COMPTE_ATTENDU) -> dict:
    """Le seuil de mode tombe-t-il dans un VIDE, ou coupe-t-il un continuum ?

    ⭐⭐⭐ ELLE EXISTE PARCE QU'UN SEUIL QUI COUPE UN CONTINUUM FABRIQUE SES DEUX POPULATIONS. Si
    les feuilles par pas s'etalent continument, appeler « deux modes » les deux moities d'un nuage
    est une figure de style, et tout ce qui suit mesurerait un artefact de decoupe. Si en revanche
    il existe un intervalle VIDE autour du seuil, la partition ne depend pas de sa valeur exacte —
    et c'est la seule facon de le savoir sans regler quoi que ce soit.

    ⚠ Le vide est rendu en unites de feuilles par pas, donc comparable au seuil lui-meme, et
    l'effectif de chaque cote est rendu avec : un vide entre deux points n'est pas un vide.
    """
    if len(trajets) < 4:
        return {"decidable": False, "pourquoi": "moins de quatre trajets"}
    fpp = np.sort(np.asarray([x["feuilles_franchies"] / max(x["pas_parcourus"], 1)
                              for x in trajets], dtype=np.float64))
    m = modes(trajets, part)
    n_haut, n_bas = int(m.sum()), int((~m).sum())
    if n_haut == 0 or n_bas == 0:
        return {"decidable": False, "pourquoi": "un seul mode peuple"}
    ecarts = np.diff(fpp)
    i = int(np.argmax(ecarts))
    plus_grand_vide = float(ecarts[i])
    # ⭐ Le vide qui compte est celui qui CONTIENT le seuil, pas le plus grand n'importe ou.
    bas = float(fpp[fpp < part].max()) if (fpp < part).any() else None
    haut = float(fpp[fpp >= part].min()) if (fpp >= part).any() else None
    vide_au_seuil = None if (bas is None or haut is None) else float(haut - bas)
    return {"decidable": True, "trajets": len(trajets), "seuil_feuilles_par_pas": round(part, 3),
            "au_dessus": n_haut, "au_dessous": n_bas,
            "dernier_du_mode_bas": None if bas is None else round(bas, 3),
            "premier_du_mode_haut": None if haut is None else round(haut, 3),
            "vide_au_seuil": None if vide_au_seuil is None else round(vide_au_seuil, 3),
            "plus_grand_vide": round(plus_grand_vide, 3),
            "le_plus_grand_vide_contient_le_seuil": bool(
                fpp[i] < part <= fpp[i + 1]),
            # ⭐⭐ LE VERDICT : le seuil tombe-t-il dans un vide plus large qu'un cran raisonnable ?
            # Un vide de plus d'un quart de feuille par pas veut dire qu'aucune marche ne se tient
            # pres du seuil, donc que le deplacer ne changerait pas la partition.
            "la_partition_ne_depend_pas_du_seuil": bool(
                vide_au_seuil is not None and vide_au_seuil > 0.25)}


def part_des_paires_bien_ordonnees(a, b) -> float:
    """La part des paires (a_i, b_j) telles que a_i > b_j, les egalites comptant pour moitie.

    ⭐ C'est exactement `U / (n_a n_b)` de Mann-Whitney, et c'est la bonne forme ici parce qu'elle
    ne demande AUCUN seuil : elle vaut 0,5 quand les deux echantillons sont melanges et 0 ou 1
    quand ils sont parfaitement separes. Un seuil est un choix ; celui-ci est une quantite.

    ⚠ Elle est deliberement nommee ainsi et non par le sigle habituel : la campagne a un chiffre
    homonyme qui mesure autre chose (le modele d'encre), et confondre les deux serait facile.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size == 0 or b.size == 0:
        return float("nan")
    d = a[:, None] - b[None, :]
    return float((np.sum(d > 0) + 0.5 * np.sum(d == 0)) / (a.size * b.size))


def separation(a, b) -> dict:
    """La force de separation entre deux echantillons, et son SENS.

    ⚠⚠ LE SENS EST RENDU A COTE DE LA FORCE, et c'est la lecon de `107` : le score du trajet
    separe fort et A L'ENVERS. Une force sans sens laisserait croire qu'un seuil ecarterait le
    mauvais mode alors qu'il ecarterait le bon.
    """
    p = part_des_paires_bien_ordonnees(a, b)
    if not np.isfinite(p):
        return {"decidable": False, "pourquoi": "un echantillon vide"}
    return {"decidable": True, "n_haut": int(np.size(a)), "n_bas": int(np.size(b)),
            "part_des_paires_bien_ordonnees": round(p, 4),
            # La force est symetrique : 0 quand rien ne separe, 1 quand tout separe.
            "force": round(abs(p - 0.5) * 2.0, 4),
            "le_mode_haut_est_plus_grand": bool(p > 0.5)}


def _forces(table: np.ndarray, m: np.ndarray) -> np.ndarray:
    """La force de separation de chaque colonne, sous l'etiquetage `m`. NaN si la colonne est vide."""
    out = np.full(table.shape[1], np.nan)
    for j in range(table.shape[1]):
        col = table[:, j]
        bon = np.isfinite(col)
        a, b = col[bon & m], col[bon & ~m]
        if a.size and b.size:
            out[j] = abs(part_des_paires_bien_ordonnees(a, b) - 0.5) * 2.0
    return out


def _forces_rapide(table: np.ndarray, m: np.ndarray) -> np.ndarray:
    """La meme quantite que `_forces`, par les RANGS, pour les tables sans trou ni ex aequo.

    ⚠⚠ ELLE EST UNE SECONDE ORTHOGRAPHE D'UNE MEME QUANTITE, donc la seule chose qui la rend
    acceptable est qu'elle soit DEMONTREE egale a la premiere — la batterie le fait sur une table
    tiree au hasard. Elle existe pour une raison mesurable : la mesure du faux positif fait cent
    soixante mille comparaisons, et la forme par paires y coute des minutes la ou celle-ci coute
    des secondes.

    ⚠ Elle suppose qu'aucune valeur n'est repetee (pas de rang moyen a calculer) et qu'aucune n'est
    absente ; c'est vrai du bruit continu qu'elle sert, et faux en general. Ne pas l'appeler sur la
    vraie table.
    """
    n = table.shape[0]
    ordre = np.argsort(table, axis=0, kind="stable")
    rangs = np.empty_like(table, dtype=np.float64)
    croissant = np.arange(1, n + 1, dtype=np.float64)
    np.put_along_axis(rangs, ordre, np.broadcast_to(croissant[:, None], table.shape), axis=0)
    n1 = int(m.sum())
    n2 = n - n1
    u = rangs[m].sum(axis=0) - n1 * (n1 + 1) / 2.0
    return np.abs(u / (n1 * n2) - 0.5) * 2.0


def nul_de_la_plus_grande_separation(table: np.ndarray, m: np.ndarray,
                                     dans_la_famille: np.ndarray | None = None,
                                     tirages: int = TIRAGES,
                                     graine: int = GRAINE) -> dict:
    """La correction de multiplicite, par permutation sur le MAXIMUM de la famille.

    ⚠⚠⚠ POURQUOI LE MAXIMUM ET NON UNE DIVISION PAR LE NOMBRE DE CANDIDATS. Bonferroni suppose
    que les candidats sont independants ; ils ne le sont pas — la planarite et le desaccord des
    demi-blocs mesurent tous deux la coherence de la meme cellule. Permuter les ETIQUETTES de mode
    et regarder le maximum de la famille rend la loi exacte de « le meilleur des huit », quelles
    que soient leurs correlations, sans aucune hypothese.

    ⭐ La meme permutation rend aussi la valeur BRUTE de chaque candidat (celle qu'on aurait
    publiee sans correction), donc l'ecart entre les deux est lisible plutot qu'affirme.

    ⚠⚠ `dans_la_famille` dit quelles colonnes entrent dans le MAXIMUM. Les temoins recoivent leur
    valeur brute — sans quoi « le temoin separe-t-il ? » n'aurait pas de reponse chiffree — mais ils
    n'entrent pas dans le maximum : un temoin est la pour verifier l'instrument, pas pour concourir,
    et l'inclure gonflerait la correction que les vrais candidats doivent franchir.
    """
    obs = _forces(table, m)
    if dans_la_famille is None:
        dans_la_famille = np.ones(table.shape[1], dtype=bool)
    dans_la_famille = np.asarray(dans_la_famille, dtype=bool)
    rng = np.random.default_rng(graine)
    n = table.shape[0]
    maxi = np.empty(tirages)
    au_moins = np.zeros(table.shape[1], dtype=np.int64)
    k = int(m.sum())
    for t in range(tirages):
        idx = rng.permutation(n)
        mm = np.zeros(n, dtype=bool)
        mm[idx[:k]] = True
        f = _forces(table, mm)
        fam = f[dans_la_famille]
        maxi[t] = np.nanmax(fam) if np.isfinite(fam).any() else 0.0
        au_moins += np.where(np.isfinite(f) & np.isfinite(obs) & (f >= obs), 1, 0)
    out = []
    for j in range(table.shape[1]):
        if not np.isfinite(obs[j]):
            out.append({"decidable": False})
            continue
        out.append({
            "decidable": True,
            "force": round(float(obs[j]), 4),
            # ⚠ Le « +1 » aux deux termes est la correction de Davison-Hinkley : sans elle une
            # permutation qui n'atteint jamais l'observe rendrait p = 0, ce qui affirme plus que
            # ce que `tirages` peut porter.
            "p_brute": round(float((au_moins[j] + 1) / (tirages + 1)), 5),
            "p_corrigee": round(float((np.sum(maxi >= obs[j]) + 1) / (tirages + 1)), 5)})
    return {"tirages": int(tirages), "graine": int(graine),
            "force_max_du_nul_p95": round(float(np.percentile(maxi, 95)), 4),
            "force_max_du_nul_mediane": round(float(np.median(maxi)), 4),
            "par_candidat": out}


def combien_de_faux_gagnants_sans_correction(n_haut: int, n_bas: int, candidats: int,
                                             seuil_p: float = 0.05,
                                             tirages: int = 400,
                                             sous_tirages: int = 400,
                                             graine: int = GRAINE + 1) -> dict:
    """Sur du BRUIT PUR, combien de fois un test par candidat declare-t-il un gagnant ?

    ⭐⭐⭐ ELLE EXISTE PARCE QUE LE CHIFFRE QUI JUSTIFIE LA CORRECTION DOIT ETRE MESURE, PAS INVOQUE.
    « Avec huit candidats on trouve toujours quelque chose » est une intuition ; ce que rend cette
    fonction est la frequence reelle, a l'effectif reel, avec la meme machinerie de permutation que
    la mesure. C'est le chiffre qui empeche de lire un p brut de 0,03 comme un resultat.

    ⚠ Le bruit est tire independant par candidat, donc c'est le cas le PLUS FAVORABLE a la
    correction naive ; des candidats correles rendraient un taux plus faible. Le nombre rendu est
    donc une borne haute du faux positif, et il est publie comme telle.
    """
    rng = np.random.default_rng(graine)
    n = n_haut + n_bas
    m = np.zeros(n, dtype=bool)
    m[:n_haut] = True
    gagnants = 0
    for _ in range(tirages):
        table = rng.standard_normal((n, candidats))
        obs = _forces_rapide(table, m)
        # Le p brut de chaque candidat, par permutation, exactement comme dans la mesure.
        au_moins = np.zeros(candidats, dtype=np.int64)
        for _s in range(sous_tirages):
            mm = np.zeros(n, dtype=bool)
            mm[rng.permutation(n)[:n_haut]] = True
            au_moins += (_forces_rapide(table, mm) >= obs).astype(np.int64)
        p = (au_moins + 1) / (sous_tirages + 1)
        if np.nanmin(p) < seuil_p:
            gagnants += 1
    return {"tirages": int(tirages), "candidats": int(candidats),
            "n_haut": int(n_haut), "n_bas": int(n_bas), "seuil_p": seuil_p,
            "part_de_faux_gagnants": round(gagnants / tirages, 3),
            "un_test_par_candidat_ne_tient_pas": bool(gagnants / tirages > 2.0 * seuil_p)}


def ce_quun_seuil_couterait(valeurs, m: np.ndarray) -> dict:
    """Si l'on ecartait les marches sur ce candidat, combien de BONNES marches perdrait-on ?

    ⚠⚠⚠ UN SEUIL CHOISI SUR LES DONNEES QUI LE JUGENT EST OPTIMISTE PAR CONSTRUCTION, et cette
    fonction rend les deux chiffres cote a cote : celui EN echantillon (le meilleur seuil possible
    sur ces trajets) et celui HORS echantillon, par exclusion d'un trajet a la fois. L'ecart entre
    les deux est ce qu'un seuil publie sans validation ferait croire de trop.

    ⭐ Le critere de choix est Youden — sensibilite plus specificite moins un — parce qu'il ne
    depend pas de la proportion des deux modes, qui est ici un accident du corpus et non une
    propriete de la matiere.
    """
    v = np.asarray(valeurs, dtype=np.float64)
    bon = np.isfinite(v)
    v, mm = v[bon], m[bon]
    if v.size < 4 or mm.sum() == 0 or (~mm).sum() == 0:
        return {"decidable": False, "pourquoi": "pas assez de trajets lisibles"}

    def meilleur(vv, m2):
        # ⚠⚠ LES SEUILS CANDIDATS SONT LES MILIEUX ENTRE VALEURS OBSERVEES, JAMAIS LES VALEURS
        # ELLES-MEMES. Prendre les valeurs place la frontiere SUR un point, donc le point extreme
        # d'une classe devient inclassable des qu'on le retire — et la validation hors echantillon
        # rendrait 0,95 sur un separateur PARFAIT, ce qui se lirait comme une limite de la matiere
        # alors que c'est une limite de la grille de seuils. Mesure a l'appui : c'est exactement
        # l'ecart que ma premiere version rendait.
        u = np.unique(vv)
        cands = (np.concatenate([[-np.inf], (u[:-1] + u[1:]) / 2.0, [np.inf]])
                 if u.size > 1 else np.asarray([-np.inf, np.inf]))
        best = None
        for s in cands:
            for sens in (+1, -1):
                garde = (vv >= s) if sens > 0 else (vv <= s)
                sens_v = float((garde & m2).sum() / max(m2.sum(), 1))
                spec = float(((~garde) & ~m2).sum() / max((~m2).sum(), 1))
                j = sens_v + spec - 1.0
                if best is None or j > best[0]:
                    best = (j, float(s), sens)
        return best

    j, seuil, sens = meilleur(v, mm)
    seuil = float(seuil)
    garde = (v >= seuil) if sens > 0 else (v <= seuil)
    bonnes_jetees = int(((~garde) & mm).sum())
    mauvaises_gardees = int((garde & ~mm).sum())
    # ⚠ Hors echantillon : le seuil est refait sans le trajet qu'il doit classer.
    justes = 0
    for i in range(v.size):
        autres = np.ones(v.size, dtype=bool)
        autres[i] = False
        if mm[autres].sum() == 0 or (~mm[autres]).sum() == 0:
            continue
        _, s2, sens2 = meilleur(v[autres], mm[autres])
        pred = (v[i] >= s2) if sens2 > 0 else (v[i] <= s2)
        justes += int(bool(pred) == bool(mm[i]))
    return {"decidable": True, "seuil": round(seuil, 4),
            "sens": "au-dessus" if sens > 0 else "au-dessous",
            "youden_en_echantillon": round(float(j), 4),
            "bonnes_marches_jetees": bonnes_jetees, "bonnes_marches": int(mm.sum()),
            "mauvaises_marches_gardees": mauvaises_gardees, "mauvaises_marches": int((~mm).sum()),
            "justes_hors_echantillon": justes, "trajets": int(v.size),
            "part_juste_hors_echantillon": round(justes / v.size, 3),
            # Le hasard qui devine toujours le mode majoritaire fait deja ceci de juste.
            "part_juste_du_mode_majoritaire": round(
                max(float(mm.mean()), float((~mm).mean())), 3),
            "bat_le_mode_majoritaire": bool(
                justes / v.size > max(float(mm.mean()), float((~mm).mean())))}


def ce_que_le_hasard_obtient(n_haut: int, n_bas: int, tirages: int = 200,
                             graine: int = GRAINE + 2) -> dict:
    """Ce qu'un seuil regle sur du BRUIT obtient, en echantillon et hors echantillon.

    ⭐⭐⭐ ELLE CALIBRE `ce_quun_seuil_couterait`, ET SANS ELLE CE DERNIER NE VEUT RIEN DIRE. Un
    Youden de 0,30 n'est un resultat que si l'on sait ce que le hasard obtient au meme effectif ;
    sur vingt trajets il en obtient a peu pres autant. Le chiffre qui compte n'est donc pas la
    performance en echantillon mais l'ecart entre les deux colonnes.

    ⚠ Un seul tirage ne dit rien — ma premiere version assertait l'effondrement sur UNE table de
    bruit et l'a vu battre le hasard par chance. Une propriete d'un estimateur se mesure sur sa
    loi, pas sur un tirage.

    ⚠⚠⚠ ET LA LOI EST EN U, DONC C'EST LA MOYENNE QUI RESUME ET JAMAIS LA MEDIANE. Mesure a
    l'appui, sur six cents tirages a dix contre dix : moyenne **0,512**, c'est-a-dire le hasard
    exactement, et mediane **0,575**. Un seuil a un SENS, donc chaque tirage tombe du bon cote ou
    du mauvais — treize tirages sur quatre cents rendent zero juste — et la mediane d'une
    distribution a deux bosses choisit une bosse. C'est la faute que `107` a payee sur les feuilles
    par pas, repayee une tranche plus loin dans un autre fichier ; elle est ecrite ici pour qu'elle
    ne se represente pas une troisieme fois.
    """
    rng = np.random.default_rng(graine)
    n = n_haut + n_bas
    m = np.zeros(n, dtype=bool)
    m[:n_haut] = True
    dedans, dehors = [], []
    for _ in range(tirages):
        c = ce_quun_seuil_couterait(rng.standard_normal(n), m)
        if c.get("decidable"):
            dedans.append(c["youden_en_echantillon"])
            dehors.append(c["part_juste_hors_echantillon"])
    majoritaire = max(n_haut, n_bas) / n
    moyenne = float(np.mean(dehors))
    # ⚠⚠ LA TOLERANCE EST DERIVEE DU NOMBRE DE TIRAGES, PAS CHOISIE. « Le hasard obtient le
    # hasard » est un enonce sur une moyenne estimee : la comparer au niveau de chance par une
    # inegalite stricte ferait de la garde un tirage a pile ou face, ce qui est le meme defaut
    # qu'un seuil regle sur ce qui passe, dans l'autre sens.
    erreur = float(np.std(dehors, ddof=1)) / max(np.sqrt(len(dehors)), 1.0)
    return {"tirages": int(tirages), "n_haut": int(n_haut), "n_bas": int(n_bas),
            "youden_median_en_echantillon": round(float(np.median(dedans)), 4),
            "part_juste_moyenne_hors_echantillon": round(moyenne, 4),
            # ⚠ La mediane est rendue A COTE de la moyenne, et seulement pour montrer l'ecart : sur
            # une loi en U elle vaut 0,575 la ou la moyenne vaut 0,512. Publier la seule mediane
            # ferait croire que le hasard bat le hasard.
            "part_juste_mediane_hors_echantillon": round(float(np.median(dehors)), 4),
            "part_sous_le_hasard": round(float(np.mean(np.asarray(dehors) < 0.5)), 3),
            "part_juste_du_mode_majoritaire": round(majoritaire, 3),
            "erreur_type_de_la_moyenne": round(erreur, 4),
            # ⚠⚠⚠ ET LE FAIT MESURE EST QUE LE NIVEAU DE CHANCE N'EST PAS LE TAUX DU MODE
            # MAJORITAIRE : a dix contre dix il vaut **0,527 ± 0,009**, donc un seuil compare a
            # 0,500 recevrait deux points et demi gratuits. Choisir un seuil sur dix-neuf points
            # laisse une optimisme residuel que l'exclusion d'un point ne retire pas entierement.
            # Le niveau de chance publie ici est celui auquel un seuil doit etre compare.
            "le_niveau_de_chance_depasse_le_mode_majoritaire": bool(
                moyenne - 3.0 * erreur > majoritaire),
            "le_niveau_de_chance_reste_proche_du_mode_majoritaire": bool(
                abs(moyenne - majoritaire) < 0.05)}


def _table(trajets: list[dict], noms) -> np.ndarray:
    t = np.full((len(trajets), len(noms)), np.nan)
    for i, x in enumerate(trajets):
        for j, n in enumerate(noms):
            val = x.get(n)
            if val is not None and np.isfinite(float(val)):
                t[i, j] = float(val)
    return t


def separer(trajets: list[dict], tirages: int = TIRAGES, graine: int = GRAINE,
            part: float = PART_DU_COMPTE_ATTENDU) -> dict:
    """La mesure entiere sur un jeu de trajets : famille, correction, temoins, cout d'un seuil."""
    if len(trajets) < 8:
        return {"decidable": False, "pourquoi": "moins de huit trajets"}
    m = modes(trajets, part)
    if m.sum() < 3 or (~m).sum() < 3:
        return {"decidable": False, "pourquoi": "un mode a moins de trois trajets"}
    noms = [c for c, _lb, _ro in CANDIDATS]
    famille = np.asarray([ro == "candidat" for _c, _lb, ro in CANDIDATS], dtype=bool)
    nul = nul_de_la_plus_grande_separation(_table(trajets, noms), m, famille, tirages, graine)
    par = []
    for (cle, libelle, role) in CANDIDATS:
        col = np.asarray([x.get(cle) if x.get(cle) is not None else np.nan
                          for x in trajets], dtype=np.float64)
        bon = np.isfinite(col)
        s = separation(col[bon & m], col[bon & ~m])
        ligne = {"cle": cle, "libelle": libelle, "role": role, **s}
        j = noms.index(cle)
        garde = ("p_brute", "p_corrigee") if role == "candidat" else ("p_brute",)
        ligne.update({k: v for k, v in nul["par_candidat"][j].items() if k in garde})
        if role != "candidat":
            # ⚠⚠ LES TEMOINS NE SONT PAS DANS LA FAMILLE, DONC PAS CORRIGES, et c'est dit plutot
            # que sous-entendu : un temoin est la pour verifier l'instrument, pas pour concourir.
            ligne["hors_famille"] = True
        ligne["mediane_mode_haut"] = None if not (bon & m).any() else round(
            float(np.median(col[bon & m])), 4)
        ligne["mediane_mode_bas"] = None if not (bon & ~m).any() else round(
            float(np.median(col[bon & ~m])), 4)
        par.append(ligne)
    candidats = [x for x in par if x["role"] == "candidat" and x.get("decidable")]
    retenus = [x for x in candidats if x.get("p_corrigee", 1.0) < 0.05]
    retenus.sort(key=lambda x: -x["force"])
    meilleur = max(candidats, key=lambda x: x["force"]) if candidats else None
    out = {"decidable": True, "trajets": len(trajets),
           "mode_haut": int(m.sum()), "mode_bas": int((~m).sum()),
           "candidats_declares": len(NOMS_DES_CANDIDATS),
           "par_candidat": par, "nul": {k: v for k, v in nul.items() if k != "par_candidat"},
           "retenus": [x["cle"] for x in retenus],
           # ⭐⭐⭐ LE VERDICT DE LA TRANCHE, ET IL PEUT DIRE NON. Si aucun candidat ne survit a la
           # correction, la reponse publiee est « rien de ce qui est mesure ne les separe » — un
           # resultat, pas un echec, et celui que `107` annoncait sans l'avoir mesure.
           "quelque_chose_les_separe": bool(retenus)}
    if meilleur is not None:
        out["meilleur_candidat"] = meilleur["cle"]
        out["force_du_meilleur"] = meilleur["force"]
        col = np.asarray([x.get(meilleur["cle"]) if x.get(meilleur["cle"]) is not None
                          else np.nan for x in trajets], dtype=np.float64)
        out["cout_dun_seuil"] = ce_quun_seuil_couterait(col, m)
        hz = ce_que_le_hasard_obtient(int(m.sum()), int((~m).sum()))
        out["ce_que_le_hasard_obtient"] = hz
        c = out["cout_dun_seuil"]
        if c.get("decidable"):
            # ⚠⚠⚠ LE SEUIL EST COMPARE AU NIVEAU DE CHANCE MESURE, PAS A 0,5. Le second lui
            # offrirait l'optimisme residuel de l'exclusion d'un point — mesure a deux points et
            # demi au meme effectif — et c'est exactement la marge sur laquelle un critere
            # inexistant paraitrait exister.
            c["niveau_de_chance_mesure"] = hz["part_juste_moyenne_hors_echantillon"]
            c["bat_le_niveau_de_chance_mesure"] = bool(
                c["part_juste_hors_echantillon"]
                > hz["part_juste_moyenne_hors_echantillon"]
                + 3.0 * hz["erreur_type_de_la_moyenne"])
            out["le_seuil_bat_le_niveau_de_chance_mesure"] = c[
                "bat_le_niveau_de_chance_mesure"]
    temoins = {x["role"]: x for x in par if x["role"] != "candidat"}
    if "temoin_positif" in temoins:
        t = temoins["temoin_positif"]
        # ⚠⚠ LA PLOMBERIE EST VERIFIEE PAR UNE EGALITE, PAS PAR UN SEUIL : la quantite qui definit
        # les modes doit les separer PARFAITEMENT. Un « significatif » y serait deja une panne.
        out["force_du_temoin_positif"] = t.get("force")
        out["la_plomberie_tient"] = bool(t.get("force") == 1.0)
    if "hypothese_refutee" in temoins:
        h = temoins["hypothese_refutee"]
        out["force_de_lhypothese_refutee"] = h.get("force")
        out["lhypothese_de_la_longueur_est_refutee"] = bool(
            h.get("decidable") and h.get("p_brute", 1.0) >= 0.05)
        # ⭐ Et le SENS de son echec est un fait sur la matiere : le mode qui ne compte rien marche
        # PLUS LOIN, ce qui interdit de lire le retard comme « la marche s'est arretee tot ».
        out["le_mode_qui_ne_compte_rien_marche_plus_loin"] = bool(
            h.get("decidable") and not h["le_mode_haut_est_plus_grand"])
    if "temoin_negatif" in temoins:
        t = temoins["temoin_negatif"]
        out["le_temoin_negatif_separe_a_lenvers"] = bool(
            t.get("decidable") and not t["le_mode_haut_est_plus_grand"])
        out["force_du_temoin_negatif"] = t.get("force")
    return out


def apres_combien_de_pas_le_sait_on(trajets: list[dict], tirages: int = TIRAGES,
                                    graine: int = GRAINE + 3,
                                    part: float = PART_DU_COMPTE_ATTENDU) -> dict:
    """Avec les k premiers pas seulement, sait-on deja dans quel mode la marche est ?

    ⭐⭐⭐ C'EST LA QUESTION OPERATIONNELLE, ET ELLE EST DIFFERENTE DE LA PRECEDENTE. Savoir apres
    coup qu'une marche n'a rien compte ne remplace pas l'humain ; savoir AU PREMIER PAS qu'il ne
    faut pas partir d'ici, si. Un automate qui reconnait une cellule sterile avant de payer six
    cubes ne corrige pas un transfert : il ne le tente pas, et repart ailleurs. C'est la forme sous
    laquelle un signal devient une politique.

    ⚠⚠ UNE SEULE QUANTITE EST INTERROGEE ICI — le score du balayage — et elle est declaree avant :
    c'est celle que la famille a retenue. Ce qui varie est la LONGUEUR DE CE QU'ON A VU, pas le
    choix de la quantite, donc ce n'est pas une seconde peche. La correction sur les six longueurs
    est faite quand meme, par la meme permutation, parce qu'une courbe de six points offre six
    occasions de trouver un maximum.

    ⚠ La mediane COURANTE et non le pas isole : un pas seul est bruite, et l'automate dispose de
    tous ceux qu'il a deja payes. Pour k = 1 les deux coincident, donc la premiere colonne repond
    bien a « au premier pas ».
    """
    utiles = [x for x in trajets if x.get("scores_du_balayage")]
    if len(utiles) < 8:
        return {"decidable": False, "pourquoi": "moins de huit trajets avec des scores de pas"}
    kmax = max(len(x["scores_du_balayage"]) for x in utiles)
    m = modes(utiles, part)
    if m.sum() < 3 or (~m).sum() < 3:
        return {"decidable": False, "pourquoi": "un mode a moins de trois trajets"}
    table = np.full((len(utiles), kmax), np.nan)
    for i, x in enumerate(utiles):
        sc = [v for v in x["scores_du_balayage"] if v is not None]
        for k in range(1, kmax + 1):
            if len(sc) >= k:
                table[i, k - 1] = float(np.median(sc[:k]))
    nul = nul_de_la_plus_grande_separation(table, m, None, tirages, graine)
    lignes = []
    for k in range(1, kmax + 1):
        col = table[:, k - 1]
        bon = np.isfinite(col)
        sep = separation(col[bon & m], col[bon & ~m])
        lignes.append({"pas_vus": k, **sep,
                       **{c: v for c, v in nul["par_candidat"][k - 1].items()
                          if c in ("p_brute", "p_corrigee")},
                       "cout": ce_quun_seuil_couterait(col, m)})
    premier = lignes[0]
    return {"decidable": True, "trajets": len(utiles), "pas_max": kmax,
            "mode_haut": int(m.sum()), "mode_bas": int((~m).sum()),
            "par_longueur": lignes,
            "force_au_premier_pas": premier.get("force"),
            "p_corrigee_au_premier_pas": premier.get("p_corrigee"),
            # ⭐⭐⭐ LE VERDICT QUI DECIDE D'UNE POLITIQUE : le premier pas suffit-il ?
            "le_premier_pas_suffit": bool(premier.get("p_corrigee", 1.0) < 0.05),
            "force_au_dernier_pas": lignes[-1].get("force"),
            # ⚠ Voir plus longtemps doit aider, sinon la mediane courante n'apporte rien et un seul
            # pas est tout ce qu'il y a a lire. Le fait est publie dans les deux sens.
            "voir_plus_longtemps_aide": bool(
                lignes[-1].get("force", 0.0) > premier.get("force", 0.0))}


def combien_de_marches_pour_decider(trajets: list[dict],
                                    cibles=(24, 36, 48, 72, 96, 144),
                                    tirages: int = 300, tirages_du_nul: int = 600,
                                    graine: int = GRAINE + 4,
                                    part: float = PART_DU_COMPTE_ATTENDU) -> dict:
    """A quel effectif un SEUL selecteur deciderait-il, sans mise en commun ?

    ⭐⭐⭐ ELLE CHIFFRE LE PRIX DE LA COURSE SUIVANTE AVANT QU'ON LE PAIE, et c'est sa seule raison
    d'etre. Le resultat de cette tranche tient sur quarante-huit trajets qui ne sont PAS
    independants — deux marches partent de la meme cellule — et il ne se replique pas a
    l'effectif d'un selecteur. « Il faudrait plus de marches » est une phrase ; combien, et pour
    combien d'heures, est un chiffre. Une course de vingt-huit bandes coute cinq heures ; savoir
    s'il en faut deux ou dix se decide ici, sur des donnees deja payees.

    ⚠⚠ LA METHODE EST UN REECHANTILLONNAGE PAR LIGNE ENTIERE, jamais par colonne. Tirer chaque
    candidat separement casserait les correlations entre eux — or c'est exactement d'elles que
    depend la loi du MAXIMUM de la famille, donc la correction. Une ligne est un trajet ; on tire
    des trajets.

    ⚠⚠⚠ ET LA REPONSE EST OPTIMISTE, PAR CONSTRUCTION, POUR UNE RAISON QUI A UN NOM. L'ampleur
    qu'on reechantillonne est celle du candidat RETENU, c'est-a-dire du maximum d'une famille de
    onze — et un maximum surestime ce qu'il mesure (la « malediction du vainqueur »). Le nombre
    rendu est donc un PLANCHER du nombre de marches necessaires, jamais une estimation centrale,
    et il est publie comme tel.

    ⚠⚠⚠ ET CE QU'ELLE NE PEUT PAS FAIRE EST MESURE PAR SA PROPRE BATTERIE : elle ne distingue pas
    un effet REEL d'un effet CHANCEUX. Sur une table de bruit pur, le meilleur candidat porte
    quand meme une force non nulle par accident, et le reechantillonnage la traite comme la
    verite — a cent vingt trajets, il annonce alors quatre chances sur cinq de la « retrouver ».
    Ce qu'elle repond n'est donc PAS « combien de marches pour savoir » mais **combien de marches
    pour REPRODUIRE l'ampleur observee, quelle que soit son origine**. Le chiffre n'a de sens que
    si l'effet est etabli AILLEURS — ici il l'est, par l'ensemble des deux selecteurs, a p
    corrigee 0,0008 ; c'est cette p-la, et non celle du selecteur reechantillonne, qui autorise a
    poser la question.

    ⚠ La valeur critique du maximum est calculee UNE FOIS par effectif, sur une table
    reechantillonnee dont les etiquettes sont brassees : c'est exactement le seuil qu'une p
    corrigee inferieure a 0,05 franchit, et le recalculer a chaque tirage couterait mille fois
    plus pour le meme nombre.
    """
    if len(trajets) < 8:
        return {"decidable": False, "pourquoi": "moins de huit trajets"}
    m = modes(trajets, part)
    if m.sum() < 3 or (~m).sum() < 3:
        return {"decidable": False, "pourquoi": "un mode a moins de trois trajets"}
    noms = list(NOMS_DES_CANDIDATS)
    table = _table(trajets, noms)
    obs = _forces(table, m)
    if not np.isfinite(obs).any():
        return {"decidable": False, "pourquoi": "aucun candidat lisible"}
    meilleur = int(np.nanargmax(obs))
    part_haute = float(m.mean())
    hauts = np.flatnonzero(m)
    bas = np.flatnonzero(~m)
    rng = np.random.default_rng(graine)
    lignes = []
    for n in cibles:
        n_haut = max(int(round(n * part_haute)), 3)
        n_bas = max(n - n_haut, 3)
        mm = np.zeros(n_haut + n_bas, dtype=bool)
        mm[:n_haut] = True

        def tirer():
            return np.vstack([table[rng.choice(hauts, n_haut, replace=True)],
                              table[rng.choice(bas, n_bas, replace=True)]])

        # ⚠ La valeur critique vient d'une table reechantillonnee dont les etiquettes sont
        # BRASSEES : sous le nul, les deux modes sont echangeables, donc c'est bien la loi du
        # maximum a cet effectif, correlations comprises.
        t0 = tirer()
        maxi = np.empty(tirages_du_nul)
        for k in range(tirages_du_nul):
            b = np.zeros(t0.shape[0], dtype=bool)
            b[rng.permutation(t0.shape[0])[:n_haut]] = True
            f = _forces(t0, b)
            maxi[k] = np.nanmax(f) if np.isfinite(f).any() else 0.0
        critique = float(np.percentile(maxi, 95))
        retenu_meilleur = retenu_un = 0
        for _ in range(tirages):
            f = _forces(tirer(), mm)
            if np.isfinite(f[meilleur]) and f[meilleur] >= critique:
                retenu_meilleur += 1
            if np.isfinite(f).any() and np.nanmax(f) >= critique:
                retenu_un += 1
        lignes.append({"trajets": int(n_haut + n_bas), "mode_haut": n_haut, "mode_bas": n_bas,
                       "force_critique": round(critique, 4),
                       "part_ou_le_meilleur_est_retenu": round(retenu_meilleur / tirages, 3),
                       "part_ou_un_candidat_est_retenu": round(retenu_un / tirages, 3)})
    atteint = next((x for x in lignes if x["part_ou_le_meilleur_est_retenu"] >= 0.80), None)
    return {"decidable": True, "candidat": noms[meilleur],
            "force_observee": round(float(obs[meilleur]), 4),
            "trajets_de_depart": len(trajets), "tirages": int(tirages),
            "tirages_du_nul": int(tirages_du_nul), "par_effectif": lignes,
            "trajets_pour_quatre_chances_sur_cinq": None if atteint is None
            else atteint["trajets"],
            "la_reponse_est_un_plancher": True,
            "pourquoi_un_plancher": "l'ampleur reechantillonnee est celle du maximum d'une "
                                    "famille de onze, donc surestimee",
            "ce_nest_pas_combien_pour_savoir": "c'est combien pour REPRODUIRE l'ampleur "
                                               "observee ; sur du bruit pur la reponse monte "
                                               "aussi, donc le chiffre n'a de sens que si "
                                               "l'effet est etabli ailleurs"}


def mesurer(chemin: Path = CHEMIN_DE_107, tirages: int = TIRAGES,
            graine: int = GRAINE) -> dict:
    """La tranche entiere : le corpus des deux selecteurs, puis chacun separement."""
    brut = json.loads(Path(chemin).read_text())
    tous = trajets_de_107(brut)
    r = {"source": str(Path(chemin).relative_to(RACINE)),
         "fragment": brut.get("fragment"), "volume_fin": brut.get("volume_fin"),
         "pas_nominal_um": brut.get("pas_nominal_um"),
         "marches_de_107": sum(len(c) * 2 for l in brut.get("lignes", [])
                               for c in [l.get("detail", [])]),
         "trajets_lisibles": len(tous),
         "candidats": [{"cle": c, "libelle": lb, "role": ro} for c, lb, ro in CANDIDATS],
         "vide_entre_les_modes": le_vide_entre_les_modes(tous),
         # ⚠⚠ LE CORPUS ENTIER MELANGE LES DEUX SELECTEURS, DONC SES TRAJETS NE SONT PAS
         # INDEPENDANTS : deux marches partent de la meme cellule. La puissance y est meilleure et
         # la valeur de p optimiste ; c'est pour cela que l'analyse par selecteur est publiee a
         # cote et que l'accord des deux est ce qui compte.
         "ensemble": separer(tous, tirages, graine),
         "apres_combien_de_pas": apres_combien_de_pas_le_sait_on(tous, tirages, graine + 3),
         "par_selecteur": {}}
    # ⚠⚠ LE PRIX DE LA COURSE SUIVANTE EST CHIFFRE SUR LE SELECTEUR QUI A ECHOUE, pas sur
    # l'ensemble : c'est `deux_roles` qui ne retient rien a vingt-quatre trajets, donc c'est lui
    # qui dit combien il en aurait fallu. Le prendre sur l'ensemble repondrait a une question que
    # personne ne pose, puisque l'ensemble decide deja.
    faible = [x for x in tous if x["selecteur"] == "deux_roles"]
    prix = combien_de_marches_pour_decider(faible)
    # ⚠⚠⚠ LA P CORRIGEE DE L'ENSEMBLE VOYAGE AVEC LE PRIX, et sans elle le prix ne veut rien dire :
    # le reechantillonnage ne sait pas si l'ampleur qu'il reproduit est reelle ou chanceuse, donc
    # c'est la correction sur les quarante-huit trajets qui autorise a poser la question.
    # ⚠⚠ LE PRIX EN HEURES VIENT DU COUT QUE `107` A MESURE, jamais d'une estimation neuve : la
    # tranche precedente a mesure quatre valeurs et retenu la plus GRANDE des fiables, parce que
    # sous-estimer fait lancer une course qu'on ne peut pas finir. Le reprendre est ce qui rend
    # les deux projections comparables.
    n_cible = prix.get("trajets_pour_quatre_chances_sur_cinq") if prix.get("decidable") else None
    if n_cible:
        lu = len([x for x in tous if x["selecteur"] == "deux_roles"])
        marches = len(brut.get("lignes", [])) * max(brut.get("cellules_par_bande", 1), 1)
        # La part des marches dont le registre est lisible, mesuree plutot que supposee.
        part_lisible = lu / marches if marches else 1.0
        cellules = int(np.ceil(n_cible / max(part_lisible, 1e-9)
                               / max(len(brut.get("lignes", [])), 1)))
        pas = int(brut.get("pas_max", 6))
        etapes = len(brut.get("lignes", [])) * cellules * pas * 2
        sec = float((brut.get("cout_par_etape") or {}).get(
            "retenue_pour_les_projections_s", 55.0))
        reel = (float(brut.get("secondes", 0.0))
                / max((brut.get("prix_projete") or {}).get("etapes", 1), 1))
        prix["course_qui_deciderait"] = {
            "trajets_vises_par_selecteur": int(n_cible),
            "part_des_marches_lisibles": round(part_lisible, 3),
            "cellules_par_bande": cellules,
            "bandes": len(brut.get("lignes", [])),
            "etapes": etapes,
            "secondes_par_etape_retenue": sec,
            "heures_projetees": round(etapes * sec / 3600.0, 2),
            "secondes_par_etape_reelle_de_107": round(reel, 1),
            "heures_au_rythme_reel_de_107": round(etapes * reel / 3600.0, 2)}
    if prix.get("decidable") and r["ensemble"].get("decidable"):
        pc = next((x.get("p_corrigee") for x in r["ensemble"]["par_candidat"]
                   if x["cle"] == prix["candidat"]), None)
        prix["p_corrigee_de_lensemble_pour_ce_candidat"] = pc
        prix["leffet_est_etabli_par_lensemble"] = bool(pc is not None and pc < 0.05)
    r["combien_de_marches_pour_decider"] = prix
    for sel in ("calibre", "deux_roles"):
        jeu = [x for x in tous if x["selecteur"] == sel]
        r["par_selecteur"][sel] = separer(jeu, tirages, graine + 1)
    r["faux_gagnants_sans_correction"] = combien_de_faux_gagnants_sans_correction(
        n_haut=r["ensemble"].get("mode_haut", 10) if r["ensemble"].get("decidable") else 10,
        n_bas=r["ensemble"].get("mode_bas", 14) if r["ensemble"].get("decidable") else 14,
        candidats=len(NOMS_DES_CANDIDATS))
    a, b = r["par_selecteur"]["calibre"], r["par_selecteur"]["deux_roles"]
    r["le_meilleur_est_le_meme_dans_les_deux_selecteurs"] = bool(
        a.get("meilleur_candidat") and a.get("meilleur_candidat") == b.get("meilleur_candidat"))
    r["les_deux_selecteurs_retiennent_quelque_chose"] = bool(
        a.get("quelque_chose_les_separe") and b.get("quelque_chose_les_separe"))
    commun = sorted(set(a.get("retenus", [])) & set(b.get("retenus", [])))
    r["retenus_par_les_deux_selecteurs"] = commun
    return r


def afficher(r: dict) -> None:
    print(f"\n{r.get('fragment')} · {r['trajets_lisibles']} trajets lisibles de `107` · "
          f"{len(NOMS_DES_CANDIDATS)} candidats déclarés avant la mesure\n")
    v = r.get("vide_entre_les_modes", {})
    if v.get("decidable"):
        print(f"LE SEUIL DE MODE TOMBE-T-IL DANS UN VIDE ? "
              f"{'OUI' if v['la_partition_ne_depend_pas_du_seuil'] else 'NON'}")
        print(f"   dernier du mode bas {v['dernier_du_mode_bas']} · seuil "
              f"{v['seuil_feuilles_par_pas']} · premier du mode haut "
              f"{v['premier_du_mode_haut']} → vide de {v['vide_au_seuil']} feuille/pas\n")
    e = r.get("ensemble", {})
    if not e.get("decidable"):
        print(f"⚠ ensemble non décidable : {e.get('pourquoi')}")
        return
    print(f"{'candidat':<52} {'rôle':<15} {'force':>7} {'p brut':>8} {'p corr':>8} "
          f"{'haut':>9} {'bas':>9}")
    for x in sorted(e["par_candidat"], key=lambda y: (y["role"] != "candidat", -y["force"])):
        pb = f"{x['p_brute']:.4f}" if "p_brute" in x else "—"
        pc = f"{x['p_corrigee']:.4f}" if "p_corrigee" in x else "—"
        fl = "↑" if x.get("le_mode_haut_est_plus_grand") else "↓"
        print(f"{x['libelle']:<52} {x['role']:<15} {x['force']:>6.3f}{fl} {pb:>8} {pc:>8} "
              f"{str(x['mediane_mode_haut']):>9} {str(x['mediane_mode_bas']):>9}")
    fg = r.get("faux_gagnants_sans_correction", {})
    print(f"\n⚠ sur du BRUIT PUR au même effectif, un test par candidat sans correction déclare "
          f"un gagnant {fg.get('part_de_faux_gagnants', 0.0) * 100:.0f} % du temps "
          f"({fg.get('tirages')} tirages)")
    print(f"   le 95ᵉ centile de la plus grande force sous le nul vaut "
          f"{e['nul']['force_max_du_nul_p95']}")
    print(f"\n★★★ QUELQUE CHOSE LES SÉPARE-T-IL ? "
          f"{'OUI' if e['quelque_chose_les_separe'] else 'NON'}"
          + (f" — {', '.join(e['retenus'])}" if e["retenus"] else
             " — aucun candidat déclaré ne survit à la correction"))
    if e.get("le_temoin_negatif_separe_a_lenvers"):
        print(f"   ⚠ le témoin négatif (score du trajet) sépare bien À L'ENVERS, force "
              f"{e.get('force_du_temoin_negatif')} — un seuil de score écarterait le BON mode")
    if e.get("la_plomberie_tient") is False:
        print(f"   ⚠⚠⚠ LE TÉMOIN POSITIF NE SÉPARE PAS PARFAITEMENT (force "
              f"{e.get('force_du_temoin_positif')}) : la plomberie est en panne, le reste du "
              f"tableau est à jeter avant d'être lu")
    if e.get("le_mode_qui_ne_compte_rien_marche_plus_loin"):
        print(f"   ⚠ l'hypothèse de la longueur est RÉFUTÉE, et à l'envers : le mode qui ne "
              f"compte rien marche PLUS LOIN (force {e.get('force_de_lhypothese_refutee')})")
    c = e.get("cout_dun_seuil") or {}
    if c.get("decidable"):
        print(f"\nCE QU'UN SEUIL SUR « {e['meilleur_candidat']} » COÛTERAIT")
        print(f"   {c['sens']} de {c['seuil']} : {c['bonnes_marches_jetees']} bonnes marches "
              f"jetées sur {c['bonnes_marches']}, {c['mauvaises_marches_gardees']} mauvaises "
              f"gardées sur {c['mauvaises_marches']}")
        print(f"   hors échantillon {c['part_juste_hors_echantillon']:.3f} juste contre "
              f"{c.get('niveau_de_chance_mesure', 0.0):.3f} pour le niveau de chance MESURÉ "
              f"({c['part_juste_du_mode_majoritaire']:.3f} pour le mode majoritaire) "
              f"→ {'mieux' if c.get('bat_le_niveau_de_chance_mesure') else 'PAS mieux'}")
    ap = r.get("apres_combien_de_pas", {})
    if ap.get("decidable"):
        print(f"\nAPRÈS COMBIEN DE PAS LE SAIT-ON ? (médiane courante du score du balayage)")
        print(f"   {'pas vus':>8} {'force':>7} {'p corr':>8} {'justes hors éch.':>18}")
        for x in ap["par_longueur"]:
            c = x.get("cout") or {}
            print(f"   {x['pas_vus']:>8} {x['force']:>7.3f} {x['p_corrigee']:>8.4f} "
                  f"{c.get('part_juste_hors_echantillon', float('nan')):>18.3f}")
        print(f"   ★★★ LE PREMIER PAS SUFFIT-IL ? "
              f"{'OUI' if ap['le_premier_pas_suffit'] else 'NON'} "
              f"(force {ap['force_au_premier_pas']}, p corrigée {ap['p_corrigee_au_premier_pas']})")
        print(f"   ★ voir plus longtemps aide : {ap['voir_plus_longtemps_aide']}")
    cm = r.get("combien_de_marches_pour_decider", {})
    if cm.get("decidable"):
        print(f"\nCOMBIEN DE MARCHES POUR QU'UN SEUL SÉLECTEUR DÉCIDE ? "
              f"(rééchantillonnage de `deux_roles`, force observée {cm['force_observee']})")
        print(f"   {'trajets':>8} {'force critique':>15} {'le meilleur retenu':>20} "
              f"{'un candidat retenu':>20}")
        for x in cm["par_effectif"]:
            print(f"   {x['trajets']:>8} {x['force_critique']:>15.4f} "
                  f"{x['part_ou_le_meilleur_est_retenu']:>20.3f} "
                  f"{x['part_ou_un_candidat_est_retenu']:>20.3f}")
        n = cm["trajets_pour_quatre_chances_sur_cinq"]
        print(f"   ★★★ QUATRE CHANCES SUR CINQ À PARTIR DE "
              f"{n if n else 'PLUS QUE CE QUI A ÉTÉ SONDÉ'} TRAJETS")
        print(f"   ⚠ et c'est un PLANCHER : {cm['pourquoi_un_plancher']}")
        print(f"   ⚠⚠ et ce n'est PAS « combien pour savoir » : {cm['ce_nest_pas_combien_pour_savoir']}")
        c2 = cm.get("course_qui_deciderait")
        if c2:
            print(f"   ★★ LA COURSE QUI DÉCIDERAIT : {c2['bandes']} bandes × "
                  f"{c2['cellules_par_bande']} cellules × 2 sélecteurs × 6 pas = "
                  f"{c2['etapes']} étapes")
            print(f"      soit {c2['heures_projetees']} h au coût retenu "
                  f"({c2['secondes_par_etape_retenue']} s/étape) et "
                  f"{c2['heures_au_rythme_reel_de_107']} h au rythme réel de `107` "
                  f"({c2['secondes_par_etape_reelle_de_107']} s/étape)")
        if "p_corrigee_de_lensemble_pour_ce_candidat" in cm:
            print(f"   ★ ce qui autorise la question : l'ensemble établit ce candidat à p corrigée "
                  f"{cm['p_corrigee_de_lensemble_pour_ce_candidat']} "
                  f"({cm.get('leffet_est_etabli_par_lensemble')})")
    print("\nPAR SÉLECTEUR (mêmes cellules, donc PAS une réplication indépendante)")
    for sel, s in r.get("par_selecteur", {}).items():
        if s.get("decidable"):
            print(f"   {sel:<12} {s['mode_haut']} haut / {s['mode_bas']} bas · meilleur "
                  f"{s.get('meilleur_candidat')} (force {s.get('force_du_meilleur')}) · retenus "
                  f"{s.get('retenus') or '—'}")
        else:
            print(f"   {sel:<12} non décidable : {s.get('pourquoi')}")
    print(f"   ★ le meilleur est le même des deux côtés : "
          f"{r.get('le_meilleur_est_le_meme_dans_les_deux_selecteurs')}")
    print(f"   ★ retenus par les DEUX sélecteurs : "
          f"{r.get('retenus_par_les_deux_selecteurs') or '—'}")


def _trajets_fabriques(n_haut: int, n_bas: int, graine: int = 7,
                       separateur: str | None = None,
                       ecart: float = 4.0) -> list[dict]:
    """Un corpus fabrique dont on SAIT ce qui separe, ou dont on sait que RIEN ne separe.

    ⚠⚠ ELLE EXISTE PARCE QU'UNE BATTERIE QUI NE VOIT QUE DES DONNEES REELLES NE PEUT PAS DIRE SI
    ELLE SAIT DIRE NON. Avec `separateur=None` toutes les colonnes sont du bruit : la mesure doit
    ne retenir personne. Avec un `separateur`, cette colonne seule est decalee : elle doit sortir,
    et les autres pas.
    """
    rng = np.random.default_rng(graine)
    out = []
    for i in range(n_haut + n_bas):
        haut = i < n_haut
        t = {"bande": i, "selecteur": "fabrique",
             "pas_parcourus": 6,
             # Le registre place le trajet dans son mode, avec un vide franc entre les deux.
             "feuilles_franchies": (6.0 if haut else 0.7) + 0.1 * float(rng.standard_normal())}
        for cle, _lb, _ro in CANDIDATS:
            v = float(rng.standard_normal())
            if separateur is not None and cle == separateur and haut:
                v += ecart
            t[cle] = v
        # ⚠ Le temoin positif est la quantite qui DEFINIT les modes : elle ne peut pas etre du
        # bruit, sinon le controle de plomberie verifierait l'inverse de ce qu'il annonce.
        t["feuilles_par_pas"] = t["feuilles_franchies"] / t["pas_parcourus"]
        t["scores_du_balayage"] = [
            float(rng.standard_normal()) + (ecart if haut and separateur == "pas" else 0.0)
            for _ in range(t["pas_parcourus"])]
        out.append(t)
    return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LES REDUCTIONS =====================================================================
    v("la médiane ignore les valeurs absentes", _mediane([1.0, None, 3.0]) == 2.0)
    v("... et rend None quand tout est absent", _mediane([None, None]) is None)
    v("la dispersion d'une suite constante est nulle",
      _dispersion([173.0] * 6) == 0.0)
    # ⭐⭐ LA DISPERSION DOIT ETRE SANS DIMENSION : doubler toutes les valeurs ne doit rien changer,
    # sinon elle mesurerait le pas et non sa regularite, et separerait pour la mauvaise raison.
    a = _dispersion([150.0, 170.0, 190.0, 210.0, 230.0, 250.0])
    b = _dispersion([300.0, 340.0, 380.0, 420.0, 460.0, 500.0])
    v("... et elle est sans dimension : doubler les valeurs ne la change pas",
      a is not None and b is not None and abs(a - b) < 1e-12, f"{a} contre {b}")
    v("... et un pas aberrant sur six ne l'emporte pas",
      _dispersion([173.0, 173.0, 173.0, 173.0, 173.0, 900.0]) < 0.2,
      f"{_dispersion([173.0] * 5 + [900.0]):.3f}")
    v("la dispersion refuse moins de trois pas", _dispersion([173.0, 180.0]) is None)
    # ⚠ Un vecteur propre n'a pas de signe : deux directions opposees sont le MEME plan, donc un
    # virage nul. `106` a paye cet oubli sur soixante et un pour cent des cellules.
    e = [{"direction": [1.0, 0.0, 0.0]}, {"direction": [-1.0, 0.0, 0.0]}]
    v("deux directions opposées font un virage NUL, pas de cent quatre-vingts degrés",
      abs(_virage_median(e)) < 1e-6, f"{_virage_median(e)}")
    e = [{"direction": [1.0, 0.0, 0.0]}, {"direction": [0.0, 1.0, 0.0]}]
    v("... et deux directions perpendiculaires font quatre-vingt-dix degrés",
      abs(_virage_median(e) - 90.0) < 1e-6, f"{_virage_median(e)}")
    v("un seul pas ne rend aucun virage",
      _virage_median([{"direction": [1.0, 0.0, 0.0]}]) is None)

    # === LA PART DES PAIRES BIEN ORDONNEES ==================================================
    v("une séparation parfaite rend un",
      part_des_paires_bien_ordonnees([5, 6, 7], [1, 2, 3]) == 1.0)
    v("... et la séparation inverse rend zéro",
      part_des_paires_bien_ordonnees([1, 2, 3], [5, 6, 7]) == 0.0)
    v("... et deux échantillons identiques rendent un demi",
      part_des_paires_bien_ordonnees([1, 2, 3], [1, 2, 3]) == 0.5)
    # ⚠ Les ex aequo comptent pour moitie, sinon une quantite discrete (la part en butee, qui ne
    # prend que sept valeurs sur six pas) paraitrait separer par le seul effet de ses egalites.
    v("les ex aequo comptent pour moitié",
      part_des_paires_bien_ordonnees([1, 1], [1, 1]) == 0.5)
    # ⚠⚠ LE SENS EST RENDU A COTE DE LA FORCE, et c'est la lecon de `107` : le score du trajet
    # separe fort et A L'ENVERS. Une force sans sens se lit comme un critere utilisable.
    s = separation([1, 2, 3], [5, 6, 7])
    v("une séparation inverse a une force MAXIMALE et un sens négatif",
      s["force"] == 1.0 and s["le_mode_haut_est_plus_grand"] is False)

    # === LES DEUX ORTHOGRAPHES D'UNE MEME QUANTITE ==========================================
    # ⚠⚠ `_forces_rapide` existe pour la vitesse ; la seule chose qui la rend acceptable est
    # qu'elle soit DEMONTREE egale a la forme par paires, pas affirmee telle.
    rng = np.random.default_rng(3)
    tb = rng.standard_normal((40, 6))
    mm = np.zeros(40, dtype=bool)
    mm[rng.permutation(40)[:17]] = True
    ecart = float(np.max(np.abs(_forces(tb, mm) - _forces_rapide(tb, mm))))
    v("les deux orthographes de la force rendent le même nombre", ecart < 1e-12,
      f"écart max {ecart:.2e}")

    # === LE VIDE ENTRE LES MODES ============================================================
    # ⭐⭐⭐ UN SEUIL QUI COUPE UN CONTINUUM FABRIQUE SES DEUX POPULATIONS. La garde doit dire NON
    # sur un nuage etale, sinon toute la tranche mesurerait un artefact de decoupe.
    continu = [{"feuilles_franchies": 6.0 * x / 40.0, "pas_parcourus": 6}
               for x in range(1, 41)]
    v("un continuum n'est PAS annoncé comme deux populations",
      le_vide_entre_les_modes(continu)["la_partition_ne_depend_pas_du_seuil"] is False,
      f"vide {le_vide_entre_les_modes(continu)['vide_au_seuil']}")
    coupe = ([{"feuilles_franchies": 0.7, "pas_parcourus": 6}] * 10
             + [{"feuilles_franchies": 6.2, "pas_parcourus": 6}] * 10)
    r = le_vide_entre_les_modes(coupe)
    v("... et un vide franc l'est", r["la_partition_ne_depend_pas_du_seuil"] is True,
      f"vide {r['vide_au_seuil']}")
    v("... et le vide est rendu en feuilles par pas, donc comparable au seuil",
      abs(r["vide_au_seuil"] - (6.2 - 0.7) / 6.0) < 1e-3, f"{r['vide_au_seuil']}")

    # === LA CORRECTION DE MULTIPLICITE ======================================================
    # ⭐⭐⭐ LA GARDE CENTRALE, ET ELLE DOIT POUVOIR DIRE NON. Sur un corpus dont AUCUNE colonne ne
    # separe, la mesure ne doit retenir personne — sinon tout ce que cette tranche publiera sera
    # le survivant d'une selection invisible.
    bruit = separer(_trajets_fabriques(20, 24, graine=11), tirages=400, graine=5)
    v("sur du bruit pur, AUCUN candidat n'est retenu",
      bruit["quelque_chose_les_separe"] is False, f"retenus {bruit['retenus']}")
    # ⭐⭐ ET ELLE DOIT POUVOIR DIRE OUI : une colonne franchement decalee doit sortir, seule.
    plante = separer(_trajets_fabriques(20, 24, graine=11, separateur="planarite_mediane"),
                     tirages=400, graine=5)
    v("un séparateur planté est retenu",
      "planarite_mediane" in plante["retenus"], f"retenus {plante['retenus']}")
    v("... et il est le seul", plante["retenus"] == ["planarite_mediane"],
      f"retenus {plante['retenus']}")
    v("... et il est nommé comme le meilleur",
      plante["meilleur_candidat"] == "planarite_mediane")
    # ⚠⚠ LA CORRECTION DOIT COUTER QUELQUE CHOSE, sinon elle ne corrige rien. Sur du bruit, la
    # valeur corrigee du meilleur doit etre franchement plus grande que sa valeur brute.
    pires = max((x for x in bruit["par_candidat"] if x["role"] == "candidat"),
                key=lambda x: x["force"])
    v("la correction coûte quelque chose : p corrigée > p brute pour le meilleur du bruit",
      pires["p_corrigee"] > pires["p_brute"],
      f"{pires['p_brute']:.4f} → {pires['p_corrigee']:.4f}")
    # ⚠ Un candidat entierement absent ne doit pas planter la mesure ni compter comme retenu.
    troue = _trajets_fabriques(20, 24, graine=11)
    for t in troue:
        t["planarite_min"] = None
    tr = separer(troue, tirages=200, graine=5)
    v("un candidat entièrement absent est ignoré sans faire tomber la mesure",
      tr["decidable"] and "planarite_min" not in tr["retenus"])

    # === LES TEMOINS ========================================================================
    # ⚠⚠ UNE FAMILLE SANS TEMOIN NE SAIT PAS SI ELLE A DE LA PUISSANCE. Le temoin positif est
    # plante ici pour verifier que la mesure le lit hors famille et ne le corrige pas.
    tp = _trajets_fabriques(20, 24, graine=11, separateur="longueur_um")
    rp = separer(tp, tirages=400, graine=5)
    v("les témoins sont lus HORS famille, donc jamais corrigés",
      all(x.get("hors_famille") for x in rp["par_candidat"] if x["role"] != "candidat"))
    # ⭐⭐⭐ LE CONTROLE DE PLOMBERIE : la quantite qui definit les modes DOIT les separer
    # parfaitement. S'il tombe, la reduction, l'appariement ou le seuil se sont perdus en route et
    # tout le tableau est a jeter avant d'etre lu.
    v("le témoin positif sépare parfaitement, donc la plomberie tient",
      rp["la_plomberie_tient"] is True, f"force {rp['force_du_temoin_positif']}")
    v("... sans devenir un candidat retenu",
      "feuilles_par_pas" not in rp["retenus"] and "longueur_um" not in rp["retenus"])
    # ⚠⚠ ET LA PLOMBERIE DOIT POUVOIR TOMBER : un corpus dont le temoin positif est du bruit doit
    # etre annonce en panne, sinon ce controle ne verifie rien.
    casse = _trajets_fabriques(20, 24, graine=11)
    for t in casse:
        t["feuilles_par_pas"] = float(np.random.default_rng(t["bande"]).standard_normal())
    v("... et une plomberie cassée est annoncée comme telle",
      separer(casse, tirages=200, graine=5)["la_plomberie_tient"] is False)
    # ⚠ L'hypothese de la longueur est publiee hors famille avec son SENS : si elle separait a
    # l'envers, ce serait un fait sur la matiere et non un echec de mesure.
    th = _trajets_fabriques(20, 24, graine=11, separateur="longueur_um", ecart=-4.0)
    rh = separer(th, tirages=400, graine=5)
    v("une longueur qui sépare à l'envers est publiée comme telle",
      rh["le_mode_qui_ne_compte_rien_marche_plus_loin"] is True,
      f"force {rh['force_de_lhypothese_refutee']}")
    tn = _trajets_fabriques(20, 24, graine=11, separateur="score_du_trajet", ecart=-4.0)
    rn = separer(tn, tirages=400, graine=5)
    v("un témoin négatif qui sépare à l'envers est annoncé comme tel",
      rn["le_temoin_negatif_separe_a_lenvers"] is True,
      f"force {rn['force_du_temoin_negatif']}")

    # === APRES COMBIEN DE PAS LE SAIT-ON ====================================================
    # ⭐⭐ SUR DES SCORES DE PAS QUI SEPARENT, LE PREMIER PAS DOIT SUFFIRE ; sur du bruit, non.
    # ⚠⚠ L'ECART EST PETIT EXPRES : a quatre ecarts-types le premier pas separe DEJA
    # parfaitement, donc « voir plus longtemps aide » devient invérifiable — une garde satisfaite
    # par saturation ne garde rien. A un ecart-type, la mediane courante a de quoi montrer ce
    # qu'elle apporte.
    ap = apres_combien_de_pas_le_sait_on(
        _trajets_fabriques(20, 24, graine=11, separateur="pas", ecart=1.0), tirages=400)
    v("quand les scores de pas séparent, le premier pas suffit",
      ap["le_premier_pas_suffit"] is True,
      f"force {ap['force_au_premier_pas']}, p corrigée {ap['p_corrigee_au_premier_pas']}")
    v("... et voir plus longtemps aide encore", ap["voir_plus_longtemps_aide"] is True,
      f"{ap['force_au_premier_pas']} → {ap['force_au_dernier_pas']}")
    ap0 = apres_combien_de_pas_le_sait_on(_trajets_fabriques(20, 24, graine=11), tirages=400)
    v("... et sur du bruit le premier pas ne suffit PAS",
      ap0["le_premier_pas_suffit"] is False,
      f"p corrigée {ap0['p_corrigee_au_premier_pas']}")
    v("... et la courbe porte une colonne par pas vu",
      len(ap0["par_longueur"]) == 6, f"{len(ap0['par_longueur'])} colonnes")

    # === COMBIEN DE MARCHES POUR DECIDER ====================================================
    # ⭐⭐⭐ ELLE CHIFFRE LE PRIX DE LA COURSE SUIVANTE, donc elle doit se tromper dans les deux
    # sens : rendre un effectif atteignable quand l'effet existe, et n'en rendre AUCUN quand il
    # n'existe pas — sinon elle ferait payer une course pour mesurer du bruit.
    pw = combien_de_marches_pour_decider(
        _trajets_fabriques(20, 24, graine=11, separateur="planarite_mediane", ecart=1.2),
        cibles=(24, 48, 120), tirages=120, tirages_du_nul=200)
    v("un effet réel finit par être retenu quand l'effectif monte",
      pw["trajets_pour_quatre_chances_sur_cinq"] is not None,
      f"{[x['part_ou_le_meilleur_est_retenu'] for x in pw['par_effectif']]}")
    v("... et la part retenue MONTE avec l'effectif",
      [x["part_ou_le_meilleur_est_retenu"] for x in pw["par_effectif"]]
      == sorted(x["part_ou_le_meilleur_est_retenu"] for x in pw["par_effectif"]),
      f"{[x['part_ou_le_meilleur_est_retenu'] for x in pw['par_effectif']]}")
    # ⚠⚠ ET LA FORCE CRITIQUE DOIT BAISSER QUAND L'EFFECTIF MONTE : c'est ce qui fait qu'un effet
    # constant devient decidable. Si elle ne baissait pas, ce serait la correction qui est fausse.
    v("... et la force critique BAISSE avec l'effectif",
      [x["force_critique"] for x in pw["par_effectif"]]
      == sorted((x["force_critique"] for x in pw["par_effectif"]), reverse=True),
      f"{[x['force_critique'] for x in pw['par_effectif']]}")
    # ⭐⭐⭐ ET LA LIMITE DE LA METHODE EST MESUREE PLUTOT QUE TUE. Mon premier controle exigeait
    # que le bruit ne rende JAMAIS quatre chances sur cinq ; il a echoue, et il avait tort. Sur
    # une table de bruit le meilleur candidat porte une force non nulle par accident, et le
    # reechantillonnage la traite comme la verite : a cent vingt trajets il annonce donc quatre
    # chances sur cinq de la retrouver. La fonction ne repond pas « combien de marches pour
    # savoir » mais « combien pour REPRODUIRE l'ampleur observee ». La batterie asserte cette
    # limite dans les deux sens, parce que la taire ferait lire le chiffre comme une preuve.
    pw0 = combien_de_marches_pour_decider(_trajets_fabriques(20, 24, graine=11),
                                          cibles=(24, 48, 120), tirages=120,
                                          tirages_du_nul=200)
    v("⚠ sur du BRUIT aussi la part retenue monte : la méthode ne sait pas si l'effet est réel",
      pw0["par_effectif"][-1]["part_ou_le_meilleur_est_retenu"] > 0.5,
      f"{[x['part_ou_le_meilleur_est_retenu'] for x in pw0['par_effectif']]}")
    v("... donc la fonction DIT qu'elle ne répond pas à « combien pour savoir »",
      "etabli ailleurs" in pw0["ce_nest_pas_combien_pour_savoir"])
    # ⚠⚠ CE QUI SEPARE LE BRUIT DU REEL N'EST PAS ICI MAIS DANS LA CORRECTION : sur la meme table
    # de bruit, `separer` ne retient personne. Les deux outils repondent a deux questions, et
    # c'est leur COMBINAISON qui autorise a lire le prix.
    v("... et c'est la CORRECTION, pas le prix, qui écarte le bruit",
      separer(_trajets_fabriques(20, 24, graine=11), tirages=400,
              graine=5)["quelque_chose_les_separe"] is False)
    v("le prix se refuse sur trop peu de trajets",
      combien_de_marches_pour_decider(_trajets_fabriques(2, 2))["decidable"] is False)
    # ⚠⚠ ET LA REPONSE EST DECLAREE COMME UN PLANCHER, avec sa raison : l'ampleur
    # reechantillonnee est celle du MAXIMUM d'une famille, donc surestimee.
    v("... et la réponse se déclare comme un PLANCHER, avec sa raison",
      pw.get("la_reponse_est_un_plancher") is True and "famille" in pw["pourquoi_un_plancher"])

    # === LE FAUX POSITIF SANS CORRECTION ====================================================
    # ⭐⭐⭐ LE CHIFFRE QUI JUSTIFIE LA CORRECTION EST MESURE, PAS INVOQUE.
    fg = combien_de_faux_gagnants_sans_correction(20, 24, len(NOMS_DES_CANDIDATS),
                                                  tirages=120, sous_tirages=200)
    v("un test par candidat sans correction dépasse franchement son seuil nominal",
      fg["un_test_par_candidat_ne_tient_pas"] is True,
      f"{fg['part_de_faux_gagnants'] * 100:.0f} % de faux gagnants pour un seuil à 5 %")
    # ⚠ Le meme calcul avec UN seul candidat doit, lui, retomber pres du seuil nominal : sinon ce
    # n'est pas la multiplicite qu'on mesure mais un defaut du test lui-meme.
    un = combien_de_faux_gagnants_sans_correction(20, 24, 1, tirages=120, sous_tirages=200)
    v("... alors qu'avec un seul candidat il retombe près du seuil nominal",
      un["part_de_faux_gagnants"] < 0.12,
      f"{un['part_de_faux_gagnants'] * 100:.0f} %")

    # === CE QU'UN SEUIL COUTERAIT ===========================================================
    m = np.zeros(20, dtype=bool)
    m[:10] = True
    # ⚠⚠ LE SEPARATEUR PARFAIT PORTE UN VRAI VIDE ENTRE SES DEUX CLASSES, comme les deux modes de
    # `107` en portent un. Sur un treillis regulier sans vide, retirer un point de bord place le
    # milieu EXACTEMENT sur lui et le classement devient un tirage a pile ou face : le controle
    # rendrait 0,95 sur une reponse parfaite, ce qui mesurerait la grille et non la separation.
    parfait = np.concatenate([np.arange(10.0, 11.0, 0.1), np.arange(0.0, 1.0, 0.1)])
    c = ce_quun_seuil_couterait(parfait, m)
    v("un séparateur parfait ne jette aucune bonne marche",
      c["bonnes_marches_jetees"] == 0 and c["mauvaises_marches_gardees"] == 0)
    # ⚠⚠ ET IL RESTE PARFAIT HORS ECHANTILLON, ce qui n'etait vrai qu'apres avoir mis les seuils
    # AU MILIEU des valeurs observees : avec les valeurs elles-memes il rendait 0,95, et 0,95 sur
    # un separateur parfait se serait lu comme une limite de la matiere.
    v("... et il reste parfait hors échantillon",
      c["part_juste_hors_echantillon"] == 1.0, f"{c['part_juste_hors_echantillon']}")
    # ⚠⚠⚠ ET LA VERSION HORS ECHANTILLON DOIT S'EFFONDRER SUR DU BRUIT, sinon elle ne validerait
    # rien : un seuil regle sur les donnees qui le jugent est optimiste par construction. ⚠ Mesure
    # sur la LOI et non sur un tirage — ma premiere version assertait l'effondrement sur UNE table
    # et l'a vue battre le hasard par chance.
    hz = ce_que_le_hasard_obtient(10, 10, tirages=400)
    v("un seuil réglé sur du bruit paraît bon en échantillon",
      hz["youden_median_en_echantillon"] > 0.25,
      f"Youden médian {hz['youden_median_en_echantillon']}")
    # ⚠⚠⚠ ET LE NIVEAU DE CHANCE HORS ECHANTILLON N'EST PAS LE TAUX DU MODE MAJORITAIRE. Mesure :
    # il le depasse de facon reproductible, donc comparer un seuil a 0,500 lui offrirait ces
    # points-la. C'est pour cela que la mesure publie le niveau MESURE a cote du niveau naif.
    v("le niveau de chance hors échantillon DÉPASSE le taux du mode majoritaire",
      hz["le_niveau_de_chance_depasse_le_mode_majoritaire"] is True,
      f"{hz['part_juste_moyenne_hors_echantillon']} ± "
      f"{hz['erreur_type_de_la_moyenne']} contre {hz['part_juste_du_mode_majoritaire']}")
    v("... mais de peu, donc l'écart est un biais et non un signal",
      hz["le_niveau_de_chance_reste_proche_du_mode_majoritaire"] is True,
      f"écart {hz['part_juste_moyenne_hors_echantillon'] - hz['part_juste_du_mode_majoritaire']:.4f}")
    # ⚠⚠⚠ ET LA LOI EST EN U, DONC LA MEDIANE MENT ICI. La garde le VERIFIE plutot que de le
    # supposer : si un jour la distribution cessait d'avoir deux bosses, ce contrôle tomberait et
    # le commentaire ci-dessus deviendrait faux sans que rien ne le dise.
    v("la loi hors échantillon est en U, donc sa médiane dépasse sa moyenne",
      hz["part_juste_mediane_hors_echantillon"] > hz["part_juste_moyenne_hors_echantillon"],
      f"médiane {hz['part_juste_mediane_hors_echantillon']} contre moyenne "
      f"{hz['part_juste_moyenne_hors_echantillon']}")
    v("... et une part non nulle des tirages tombe SOUS le hasard",
      hz["part_sous_le_hasard"] > 0.2, f"{hz['part_sous_le_hasard'] * 100:.0f} %")

    # === LA LECTURE DE `107` ================================================================
    # ⚠ Un trajet dont le registre n'est pas decidable est ECARTE, jamais range dans le mode bas :
    # « le profil est plat » n'est pas « la marche n'a rien franchi ».
    v("un trajet non décidable est écarté et non compté dans le mode bas",
      resume_dun_trajet({"trajet_entier": {"decidable": False}, "etapes": [{}]},
                        4.0, "calibre", 1) is None)
    v("... et une marche sans étape aussi",
      resume_dun_trajet({"trajet_entier": {"decidable": True, "feuilles_franchies": 6.0,
                                           "pas_parcourus": 6, "longueur_um": 1.0,
                                           "score": 0.3}, "etapes": []},
                        4.0, "calibre", 1) is None)
    # ⚠ Le seuil de mode est recalcule PAR TRAJET, parce qu'une marche plus courte attend moins.
    mm2 = modes([{"feuilles_franchies": 1.6, "pas_parcourus": 3},
                 {"feuilles_franchies": 1.6, "pas_parcourus": 6}])
    v("le seuil de mode suit le compte de pas attendu de CHAQUE trajet",
      bool(mm2[0]) is True and bool(mm2[1]) is False, str(mm2.tolist()))
    if CHEMIN_DE_107.is_file():
        tous = trajets_de_107(json.loads(CHEMIN_DE_107.read_text()))
        v("la mesure de `107` est lisible et rend des trajets", len(tous) >= 24,
          f"{len(tous)} trajets")
        v("... et chaque candidat déclaré y est renseigné",
          all(all(t.get(c) is not None for c, _l, _r in CANDIDATS) for t in tous),
          f"{len(CANDIDATS)} candidats sur {len(tous)} trajets")
        mo = modes(tous)
        v("... et les deux modes sont peuplés",
          int(mo.sum()) >= 5 and int((~mo).sum()) >= 5,
          f"{int(mo.sum())} haut / {int((~mo).sum())} bas")
        # ⚠⚠ LE PRIX EN HEURES DOIT ETRE PLUS GRAND AU COUT RETENU QU'AU RYTHME REEL, sinon la
        # projection ne serait plus conservatrice — et `107` a retenu la plus grande des valeurs
        # fiables precisement pour que sous-estimer ne fasse pas lancer une course infinissable.
        m108 = json.loads(
            (RACINE / "docs" / "mesures"
             / "ce_qui_separe_les_deux_populations.json").read_text()) if (
                RACINE / "docs" / "mesures"
                / "ce_qui_separe_les_deux_populations.json").is_file() else {}
        c2 = ((m108.get("combien_de_marches_pour_decider") or {}).get(
            "course_qui_deciderait") or {})
        if c2:
            v("la course qui déciderait est projetée au coût RETENU, donc plus cher que le réel",
              c2["heures_projetees"] > c2["heures_au_rythme_reel_de_107"],
              f"{c2['heures_projetees']} h contre {c2['heures_au_rythme_reel_de_107']} h")
            v("... et ses étapes se recomposent depuis ses facteurs",
              c2["etapes"] == c2["bandes"] * c2["cellules_par_bande"] * 6 * 2,
              f"{c2['etapes']} étapes")
    else:
        v("la mesure de `107` est présente", False, str(CHEMIN_DE_107))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--source", type=Path, default=CHEMIN_DE_107)
    p.add_argument("--tirages", type=int, default=TIRAGES)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(chemin=a.source, tirages=a.tirages, graine=a.graine)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
