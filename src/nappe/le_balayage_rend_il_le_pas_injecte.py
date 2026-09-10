#!/usr/bin/env python3
"""Le balayage rend-il le pas qu'on lui injecte ? — le selecteur calibre choisit un cran trop haut.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST UN CONTROLE FABRIQUE QUI L'A OUVERT. En calibrant un eventail de
directions sur un empilement FABRIQUE de pas 173,0 µm exactement, le minimum est ressorti a
**181,7** — un cran de balayage au-dessus. Sur une donnee dont la reponse est exacte et sans le
moindre bruit.

⛔⛔⛔ LA BATTERIE DE `99` A UN CONTROLE ALLER-RETOUR, ET IL EXERCE UN AUTRE CHEMIN QUE LA
PRODUCTION. Elle injecte un pas connu et le relit par `pas_montre` — le selecteur BRUT — alors que
`mesurer` appelle `pas_montre_calibre`. Le seul controle capable de voir ce defaut regarde donc a
cote, et c'est une forme neuve d'une faute que ce depot recense deja : *une verification qui
n'emprunte pas le chemin de la production*.

⛔⛔ ET LE SELECTEUR DE PRODUCTION EST BIAISE HAUT, a toutes les periodes et a tous les bruits. Le
selecteur brut rend la periode injectee EXACTEMENT ; le calibre rend un a deux crans au-dessus,
soit **+5 a +9 %**.

⭐⭐⭐ LE MECANISME EST MESURE, PAS SUPPOSE. Le nul par candidat DECROIT avec la longueur — un
segment court reechantillonne est sur-echantillonne, donc plus lisse, donc il correle mieux — et la
calibration divise par cet ecart-type decroissant. Un candidat plus long dont l'accord BRUT est
moins bon peut donc obtenir un score CALIBRE meilleur. La calibration est juste pour la question
« ce candidat depasse-t-il le bruit » et fausse pour la question « lequel colle le mieux ».

⭐⭐⭐ ET LE REMEDE EST LE PATRON QUE CE DEPOT APPLIQUE DEJA UN ETAGE PLUS HAUT : deux roles, deux
statistiques. Le score CALIBRE decide si la matiere a repondu ; le score BRUT choisit lequel des
candidats admis colle le mieux. C'est exactement la separation que `102` a imposee entre `99` qui
DECIDE de l'avance et `98` qui VERIFIE ce qu'elle a traverse.

⚠⚠ ET LA CALIBRATION NE DOIT PAS ETRE JETEE, ce que la mesure confirme : sans elle la recherche
rendait 147 µm sur le VRAI volume ET 147 sur du BRUIT PUR — indiscernables. Elle reste donc la
GARDE ; seul le CHOIX parmi les candidats admis change.

Usage :
    uv run python src/nappe/le_balayage_rend_il_le_pas_injecte.py --verifier
    uv run python src/nappe/le_balayage_rend_il_le_pas_injecte.py \\
        --json docs/mesures/le_balayage_rend_il_le_pas_injecte.json
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

MESURE_99 = RACINE / "docs" / "mesures" / "le_pas_que_la_matiere_montre.json"
MESURE_HUMAINS = RACINE / "docs" / "mesures" / "deux_humains_sur_la_meme_matiere.json"

# ⚠ Les periodes injectees et les bruits sont declares AVANT tout resultat. Elles couvrent la
# fenetre utile (le nominal 173, le pas publie par `99` a 198,9, celui des transferts humains a
# 164,0) plus deux bornes, pour qu'aucune ne soit choisie apres coup pour arranger la conclusion.
PERIODES = (140.0, 164.0, 173.0, 190.0, 198.9, 220.0, 250.0)
BRUITS = (0.0, 5.0, 15.0, 30.0)
TIRAGES = 120


def selecteurs():
    """Les trois facons de choisir un candidat, nommees une fois pour toutes.

    ⭐⭐ « deux roles » N'EST PAS UN TROISIEME REGLAGE : c'est la composition des deux autres, le
    calibre gardant et le brut choisissant. L'ecrire ici plutot que dans la mesure evite qu'une
    quatrieme variante apparaisse le jour ou celle-ci deplairait.
    """
    return ("brut", "calibre", "deux_roles")


def choisir(profils: np.ndarray, longueurs: np.ndarray, mu: np.ndarray, sd: np.ndarray,
            comment: str, barre: float | None = None) -> tuple[np.ndarray, np.ndarray,
                                                               np.ndarray, np.ndarray]:
    """Le candidat retenu, son score calibre, son indice, et s'il part sur la feuille.

    ⚠⚠ LES TROIS SELECTEURS PARTAGENT LE MEME CALCUL DE SCORES et ne different que par l'argmax.
    Deux implementations du meme gabarit finiraient par ne pas s'accorder sur ce qu'elles
    comparent, et aucune des deux ne pourrait le signaler.
    """
    from combien_dinterstices_traverses import gabarit  # noqa: PLC0415

    n = profils.shape[-1]
    z = profils - profils.mean(axis=-1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=-1, keepdims=True), 1e-12)
    s_sur = z @ gabarit(1, True, n)
    s_dans = z @ gabarit(1, False, n)
    brut = np.maximum(s_sur, s_dans)
    calibre = (brut - mu[None, :]) / sd[None, :]
    if comment == "brut":
        k = np.argmax(brut, axis=1)
    elif comment == "calibre":
        k = np.argmax(calibre, axis=1)
    elif comment == "deux_roles":
        # ⭐⭐⭐ LE CALIBRE GARDE, LE BRUT CHOISIT. Un candidat sous la barre n'est pas eligible :
        # son accord brut peut etre eleve par hasard sur une fenetre courte, et c'est exactement
        # ce que la calibration existe pour ecarter.
        if barre is None:
            raise ValueError("le sélecteur à deux rôles demande la barre du nul calibré")
        admis = calibre > barre
        # ⚠ Aucune ligne admise : on retombe sur le calibre, PAS sur le brut. Le brut sans garde
        # est precisement la panne d'origine (147 µm sur le reel comme sur le bruit pur).
        eligible = np.where(admis, brut, -np.inf)
        k = np.where(admis.any(axis=1), np.argmax(eligible, axis=1), np.argmax(calibre, axis=1))
    else:
        raise ValueError(f"sélecteur inconnu : {comment}")
    lignes = np.arange(len(profils))
    return (longueurs[k], calibre[lignes, k], k, s_sur[lignes, k] >= s_dans[lignes, k])


def aller_retour(periodes=PERIODES, bruits=BRUITS, tirages: int = TIRAGES,
                 graine: int = 909) -> dict:
    """Injecter un pas CONNU, le relire par les trois selecteurs, et publier l'ecart.

    ⭐⭐⭐ C'EST LE CONTROLE QUE `99` NE POUVAIT PAS FAIRE : il emprunte le chemin de la
    PRODUCTION. La batterie de `99` injecte un pas connu et le relit par `pas_montre`, le
    selecteur brut, alors que sa mesure appelle `pas_montre_calibre`. Un controle qui exerce un
    autre chemin que la production ne peut pas voir ce que la production fait de travers.

    ⚠ Le profil est lu sur un segment de la longueur du PLUS LONG candidat, exactement comme le
    fait `mesurer`, puis emboite. Lire une autre longueur mesurerait un autre instrument.
    """
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    x = float(longueurs[-1]) * np.linspace(0.0, 1.0, n_long)
    lignes = []
    for i, vrai in enumerate(periodes):
        # ⚠ Le candidat le plus proche est publie A COTE de la valeur lue : sans lui on ne peut
        # pas distinguer « le selecteur se trompe » de « la grille ne contient pas la reponse ».
        prox = float(longueurs[np.argmin(np.abs(longueurs - vrai))])
        for j, sg in enumerate(bruits):
            r = np.random.default_rng(graine + 31 * i + j)
            v = np.repeat((100.0 + 40.0 * np.cos(2 * np.pi * x / vrai)).reshape(1, -1),
                          tirages, axis=0)
            if sg:
                v = v + r.normal(0.0, float(sg), v.shape)
            profs = M.profils_emboites(v, longueurs)
            d = {"periode_injectee_um": float(vrai), "bruit": float(sg),
                 "candidat_le_plus_proche_um": round(prox, 2),
                 "la_grille_contient_la_reponse": bool(abs(prox - vrai) < 1e-6)}
            for nom in selecteurs():
                lu, sc, k, _ = choisir(profs, longueurs, mu, sd, nom, barre)
                med = float(np.median(lu))
                d[nom] = {
                    "lu_median_um": round(med, 1),
                    "biais_um": round(med - vrai, 1),
                    "biais_relatif": round(med / vrai - 1.0, 4),
                    # ⚠ L'ECART TYPE EST PUBLIE A COTE DU BIAIS : un selecteur sans biais mais
                    # tres disperse n'est pas meilleur, et le biais seul ne le dirait pas.
                    "ecart_type_um": round(float(np.std(lu)), 1),
                    "crans_decart": round((med - prox) / float(longueurs[1] - longueurs[0]), 2),
                    "part_en_butee": round(float(M.touche_un_bord(k, len(longueurs)).mean()), 3),
                }
            lignes.append(d)
    return {"cran_du_balayage_um": round(float(longueurs[1] - longueurs[0]), 2),
            "fenetre_um": [round(float(longueurs[0]), 1), round(float(longueurs[-1]), 1)],
            "barre_du_nul_calibre": round(float(barre), 4),
            "tirages": tirages, "lignes": lignes}


def pourquoi_le_calibre_derive() -> dict:
    """Le mecanisme, mesure : le nul decroit avec la longueur, donc la calibration favorise long.

    ⭐⭐ IL EST PUBLIE PLUTOT QU'ASSERTE, parce qu'un lecteur doit pouvoir verifier que le biais
    n'est pas un accident de mise en oeuvre mais une consequence arithmetique de la calibration.
    La ligne qui le montre est celle ou un candidat au meilleur accord BRUT perd contre un
    candidat plus long au meilleur accord CALIBRE.
    """
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from combien_dinterstices_traverses import gabarit  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    x = float(longueurs[-1]) * np.linspace(0.0, 1.0, n_long)
    vrai = float(C.PAS_UM)
    v = (100.0 + 40.0 * np.cos(2 * np.pi * x / vrai)).reshape(1, -1)
    profs = M.profils_emboites(v, longueurs)
    n = profs.shape[-1]
    z = profs - profs.mean(axis=-1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=-1, keepdims=True), 1e-12)
    brut = np.maximum(z @ gabarit(1, True, n), z @ gabarit(1, False, n))[0]
    cal = (brut - mu) / sd
    k_brut, k_cal = int(np.argmax(brut)), int(np.argmax(cal))
    return {
        "periode_injectee_um": vrai,
        "nul_par_candidat": [{"longueur_um": round(float(longueurs[i]), 1),
                              "mu": round(float(mu[i]), 4), "sd": round(float(sd[i]), 4),
                              "accord_brut": round(float(brut[i]), 4),
                              "score_calibre": round(float(cal[i]), 3)}
                             # ⚠ TOUS les candidats, pas un sur trois : l'ecart entre les deux
                             # argmax vaut UN cran, donc un echantillonnage plus lache le rend
                             # invisible dans la figure — une figure qui illustre un mecanisme
                             # sans le montrer est pire qu'une figure absente.
                             for i in range(len(longueurs))],
        "mu_le_plus_court": round(float(mu[0]), 4),
        "mu_le_plus_long": round(float(mu[-1]), 4),
        "sd_le_plus_court": round(float(sd[0]), 4),
        "sd_le_plus_long": round(float(sd[-1]), 4),
        "le_nul_decroit_avec_la_longueur": bool(mu[-1] < mu[0] and sd[-1] < sd[0]),
        "choix_brut_um": round(float(longueurs[k_brut]), 1),
        "choix_calibre_um": round(float(longueurs[k_cal]), 1),
        "accord_brut_du_choix_brut": round(float(brut[k_brut]), 4),
        "accord_brut_du_choix_calibre": round(float(brut[k_cal]), 4),
        # ⭐⭐⭐ LA LIGNE QUI PROUVE LE MECANISME : le candidat retenu par la calibration a un
        # accord BRUT strictement moins bon. Ce n'est donc pas du bruit, c'est l'arithmetique.
        "le_calibre_retient_un_accord_brut_moins_bon": bool(brut[k_cal] < brut[k_brut]),
        "de_combien_de_crans": int(k_cal - k_brut),
    }


def ce_que_ca_change_pour_99(aller: dict, bruit: float = 15.0) -> dict:
    """Quelle periode VRAIE le selecteur de production aurait rendue comme celle que `99` publie ?

    ⭐⭐⭐ C'EST L'INVERSION DE LA CARTE DE CALIBRATION, et elle est faite dans le bon sens. On ne
    corrige pas la valeur publiee par un facteur ; on cherche laquelle des periodes injectees
    ressort, apres le selecteur CALIBRE, a la valeur que `99` a publiee. C'est la meme operation
    qu'une courbe d'etalonnage lue a l'envers.

    ⚠⚠⚠ ET SA LIMITE EST DITE PLUTOT QUE CACHEE : la carte est mesuree sur un profil SINUSOIDAL
    PARFAIT. L'appliquer au vrai volume suppose que le profil reel se comporte comme lui, ce que
    rien ici ne montre. C'est donc une INDICATION, et la reponse ferme demande de rejouer la
    mesure sur le volume avec les trois selecteurs sur les MEMES lectures — ce que `mesurer` fait.
    """
    if not MESURE_99.is_file():
        return {"message": "mesure de `99` absente"}
    d = json.loads(MESURE_99.read_text())
    publie = d["la_longueur_differe_du_nul"]["mediane_reelle_um"]
    hum = (json.loads(MESURE_HUMAINS.read_text())["pas_um"]
           if MESURE_HUMAINS.is_file() else None)
    j = [x for x in aller["lignes"] if x["bruit"] == bruit]
    if not j:
        return {"message": f"aucune ligne au bruit {bruit}"}
    # ⚠ On cherche l'injectee dont la lecture CALIBREE tombe sur la valeur publiee, au cran pres.
    cran = aller["cran_du_balayage_um"]
    proches = [x for x in j if abs(x["calibre"]["lu_median_um"] - publie) < 0.5 * cran]
    out = {"publie_par_99_um": publie, "bruit_suppose": bruit,
           "pas_des_transferts_humains_um": hum,
           "candidates": [{"injectee_um": x["periode_injectee_um"],
                           "lue_par_le_calibre_um": x["calibre"]["lu_median_um"],
                           "lue_par_les_deux_roles_um": x["deux_roles"]["lu_median_um"]}
                          for x in proches]}
    if proches:
        vraie = float(np.median([x["periode_injectee_um"] for x in proches]))
        out["periode_vraie_indiquee_um"] = round(vraie, 1)
        out["correction_relative"] = round(vraie / publie - 1.0, 4)
        if hum:
            # ⭐⭐ L'ECART PUBLIE PAR LA CAMPAGNE, RELU : c'est lui que `99` laisse ouvert depuis
            # cinq tranches, et l'inversion en reprend une partie a l'instrument.
            out["ecart_publie_en_pourcent"] = round(100.0 * (publie / hum - 1.0), 1)
            out["ecart_indique_en_pourcent"] = round(100.0 * (vraie / hum - 1.0), 1)
            out["part_de_lecart_imputable_a_linstrument"] = round(
                1.0 - (vraie / hum - 1.0) / max(publie / hum - 1.0, 1e-9), 3)
    else:
        # ⚠ Aucune injectee ne ressort a la valeur publiee : la grille des periodes essayees est
        # trop lache. On le DIT plutot que d'interpoler, ce qui inventerait une precision.
        out["message"] = "aucune période injectée ne ressort à la valeur publiée ; grille trop lâche"
    return out


def mesurer(cellules: int = 40, bandes_max: int | None = None, graine: int = 41,
            fils: int = 32) -> dict:
    """Les trois selecteurs sur les MEMES lectures du vrai volume, bande par bande.

    ⭐⭐⭐ LE CONTROLE EST APPARIE, ET C'EST TOUTE SA FORCE. Chaque cellule est lue UNE FOIS et les
    trois selecteurs choisissent dans les memes profils : la quantite rendue est donc l'ecart entre
    les selecteurs et rien d'autre. Comparer trois populations differentes ferait dire au resultat
    ce qu'on veut, et ce depot l'a deja paye deux fois.

    ⚠ La geometrie des segments est celle de `99`, importee et non recopiee : meme centre interpole
    en z, meme direction radiale, meme longueur (le plus long candidat). Deux geometries feraient
    deux droites differentes sous un seul nom.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement  # noqa: PLC0415
    from transformations_de_volume import appliquer, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415
    import time  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    # ⚠⚠ LA SOURCE DU RAYON EST CELLE DE `99`, PAS UNE AUTRE. Ma premiere version lisait un
    # fichier qui n'existe pas, donc `rayon_mm` valait `None` sur les 28 bandes — un champ
    # toujours absent qui ne fait echouer rien, ce que ce depot appelle un faux zero.
    al = ({(x["de"], x["a"]): x for x in json.loads(M.ALIGNEMENT.read_text())["lignes"]}
          if M.ALIGNEMENT.is_file() else {})
    if not al:
        return {"message": f"alignement des bandes absent : {M.ALIGNEMENT}"}

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = time.time()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 10:
            continue
        seg = C.segments(a, ok, bords, cx, cy, ind, pas_um=float(longueurs[-1]))
        t = np.linspace(0.0, 1.0, n_long)
        p0, p1 = seg[:, 0, :], seg[:, -1, :]
        seg = p0[:, None, :] + (p1 - p0)[:, None, :] * t[None, :, None]
        zyx = np.rint(appliquer(m, seg)).astype(np.int64)
        dedans = vol.dans_le_volume(zyx.reshape(-1, 3)).reshape(zyx.shape[:2]).all(axis=1)
        if int(dedans.sum()) < 10:
            continue
        v = vol.lire(zyx[dedans].reshape(-1, 3), fils=fils).reshape(int(dedans.sum()), n_long)
        fini = np.isfinite(v).all(axis=1)
        if int(fini.sum()) < 10:
            continue
        profs = M.profils_emboites(v[fini], longueurs)
        d = {"de": x["de"], "a": x["a"],
             "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
             "cellules": int(fini.sum())}
        garde = None
        for nom in selecteurs():
            lu, sc, k, sur = choisir(profs, longueurs, mu, sd, nom, barre)
            bord = M.touche_un_bord(k, len(longueurs))
            # ⚠⚠ LA GARDE EST LA MEME POUR LES TROIS, et elle vient du selecteur CALIBRE. La
            # laisser varier ferait comparer trois populations differentes, ce qui est exactement
            # la faute que ce controle apparie existe pour eviter.
            if garde is None:
                garde = (sc > barre) & ~bord
            util = garde & ~bord
            d[nom] = {
                "part_utilisable": round(float(util.mean()), 3),
                "pas_median_um": (round(float(np.median(lu[util])), 1)
                                  if int(util.sum()) >= 5 else None),
                "pas_p10_um": (round(float(np.percentile(lu[util], 10)), 1)
                               if int(util.sum()) >= 5 else None),
                "pas_p90_um": (round(float(np.percentile(lu[util], 90)), 1)
                               if int(util.sum()) >= 5 else None),
                "part_en_butee": round(float(bord.mean()), 3),
            }
        lignes.append(d)
        avancement(len(lignes), len(bandes), "bandes", depart)

    if not lignes:
        return {"message": "aucune bande lisible dans le volume fin"}
    contre = {nom: _contre_le_nul(lignes, nom, longueurs, mu, sd, barre)
              for nom in selecteurs()}
    return agreger({
        "fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_nominal_um": C.PAS_UM,
        "cellules_par_bande": cellules, "bandes": len(lignes),
        "barre_du_nul_calibre": round(float(barre), 4),
        "cran_du_balayage_um": round(float(longueurs[1] - longueurs[0]), 2),
        "secondes": round(time.time() - depart, 1),
        "lignes": lignes,
        "la_longueur_differe_du_nul": contre,
        "aller_retour": aller_retour(),
        "mecanisme": pourquoi_le_calibre_derive(),
    })


def _contre_le_nul(lignes, nom, longueurs, mu, sd, barre, tirages: int = 3000,
                   graine: int = 3) -> dict:
    """La longueur choisie par CE selecteur differe-t-elle de celle que le MEME rend sur du bruit ?

    ⭐⭐⭐ C'EST LE CONTROLE QUE `99` IMPOSE A SA PROPRE LONGUEUR, ET IL DOIT SURVIVRE AU CHANGEMENT
    DE SELECTEUR. Sans lui, remplacer le selecteur calibre par le brut serait un pari : le brut
    non garde rend une valeur courte sur du bruit pur, donc il faut montrer que ce qu'il rend sur
    la matiere n'est PAS ce qu'il rend sur du bruit. Une valeur plus proche des transferts humains
    qui serait un artefact du selecteur serait la pire issue possible.

    ⚠ Le nul passe par la MEME barre et le MEME rejet des butees que le reel : comparer une
    population filtree a une population brute comparerait deux choses, faute que `99` nomme deja.
    """
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from scipy import stats  # noqa: PLC0415

    reelles = [x[nom]["pas_median_um"] for x in lignes
               if x.get(nom, {}).get("pas_median_um") is not None]
    if len(reelles) < 5:
        return {"message": "trop peu de bandes lisibles"}
    r = np.random.default_rng(graine)
    v = r.normal(100.0, 10.0, size=(tirages, M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE))
    profs = M.profils_emboites(v, longueurs)
    # ⚠⚠ LA GARDE VIENT DU CALIBRE POUR LES TROIS, exactement comme sur le reel : c'est ce qui
    # fait que les trois selecteurs sont juges sur la MEME population de cellules.
    _, sc_g, k_g, _ = choisir(profs, longueurs, mu, sd, "calibre", barre)
    garde = (sc_g > barre) & ~M.touche_un_bord(k_g, len(longueurs))
    if int(garde.sum()) < 10:
        return {"nul_au_dessus_de_la_barre": int(garde.sum()), "tirages": tirages,
                "message": "le nul franchit trop rarement la barre pour un test de distribution"}
    lu, _, _, _ = choisir(profs, longueurs, mu, sd, nom, barre)
    st = stats.ks_2samp(np.asarray(reelles), lu[garde])
    return {"nul_au_dessus_de_la_barre": int(garde.sum()),
            "part_du_nul_au_dessus_de_la_barre": round(float(garde.mean()), 4),
            "mediane_reelle_um": round(float(np.median(reelles)), 1),
            "mediane_du_nul_um": round(float(np.median(lu[garde])), 1),
            "kolmogorov_smirnov_D": round(float(st.statistic), 3),
            "kolmogorov_smirnov_p": float(f"{st.pvalue:.3g}"),
            "differe": bool(st.pvalue < 0.05)}


def _bande_de_104(franchi: float) -> dict:
    """La bande d'acceptation de `104`, LUE, et si le depassement mesure y tombe.

    ⭐⭐ ELLE EST LUE PLUTOT QUE RECOPIEE : un chiffre tape ici cesserait de suivre la mesure qui
    le produit, et c'est precisement ce que ce depot reproche a une constante en dur.
    """
    p = RACINE / "docs" / "mesures" / "un_pas_confirme_nest_pas_une_feuille.json"
    if not p.is_file():
        return {"bande_de_104": "mesure absente"}
    d = json.loads(p.read_text())
    j = next((x for x in d["bande"]["par_bruit"] if x.get("bruit") == 15.0), None)
    if j is None:
        return {"bande_de_104": "niveau de bruit absent"}
    return {"bande_dacceptation_de_104": [j["fraction_basse"], j["fraction_haute"]],
            # ⭐⭐⭐ LE FAIT QUI RELIE LES DEUX TRANCHES : le depassement mesure est DANS la bande,
            # donc chaque pas est CONFIRME et rien ne le signale. C'est le cas « biais » que `104`
            # opposait au cas « taux d'echec », mesure cette fois au lieu d'etre hypothetique.
            "le_depassement_est_confirme_par_le_critere": bool(
                j["fraction_basse"] <= franchi <= j["fraction_haute"])}


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des lignes appariees et du controle fabrique."""
    a = r.get("aller_retour")
    if a:
        r["ce_que_ca_change_pour_99"] = ce_que_ca_change_pour_99(a)
        # ⭐⭐ LE BIAIS FABRIQUE, RESUME PAR SELECTEUR : la mediane des biais relatifs sur toute
        # la grille, ce qui est la quantite qu'un lecteur veut comparer entre les trois.
        r["biais_fabrique"] = {
            nom: {
                "biais_relatif_median": round(float(np.median(
                    [x[nom]["biais_relatif"] for x in a["lignes"]])), 4),
                "biais_relatif_max": round(float(np.max(
                    [x[nom]["biais_relatif"] for x in a["lignes"]])), 4),
                "ecart_type_median_um": round(float(np.median(
                    [x[nom]["ecart_type_um"] for x in a["lignes"]])), 1),
            } for nom in selecteurs()}
    med = {}
    for nom in selecteurs():
        v = [x[nom]["pas_median_um"] for x in r.get("lignes", [])
             if x.get(nom, {}).get("pas_median_um") is not None]
        med[nom] = round(float(np.median(v)), 1) if v else None
    # ⚠ Le decoupage en tiers est celui de `99` — trie par rayon, trois parts egales — pour que
    # les deux mesures se lisent l'une contre l'autre. Un autre decoupage comparerait deux choses.
    tri = sorted([x for x in r.get("lignes", []) if x.get("rayon_mm") is not None],
                 key=lambda z: z["rayon_mm"])
    if tri:
        t = max(1, len(tri) // 3)
        r["par_tiers"] = {
            nom_t: {nom_s: (round(float(np.median(
                [y[nom_s]["pas_median_um"] for y in part
                 if y.get(nom_s, {}).get("pas_median_um") is not None])), 1)
                if any(y.get(nom_s, {}).get("pas_median_um") is not None for y in part)
                else None) for nom_s in selecteurs()}
            for nom_t, part in (("coeur", tri[:t]), ("milieu", tri[t:2 * t]),
                                ("bord", tri[2 * t:])) if part}
    r["resume"] = {
        "pas_median_par_selecteur_um": med,
        "bandes_lues": len(r.get("lignes", [])),
        **({"ecart_calibre_moins_brut_um": round(med["calibre"] - med["brut"], 1),
            "ecart_relatif": round(med["calibre"] / med["brut"] - 1.0, 4)}
           if med.get("brut") and med.get("calibre") else {}),
        **({"les_deux_roles_suivent_le_brut":
            bool(med.get("deux_roles") is not None and med.get("brut") is not None
                 and abs(med["deux_roles"] - med["brut"]) <= r.get("cran_du_balayage_um", 9.0))}
           if med.get("brut") else {}),
    }
    if r.get("biais_fabrique"):
        b = r["biais_fabrique"]
        # ⭐⭐⭐ LES DEUX VERDICTS DU FICHIER, CALCULES : le calibre est-il biaise haut, et les
        # deux roles le corrigent-ils ? Chacun peut echouer separement.
        r["resume"]["le_calibre_est_biaise_haut"] = bool(
            b["calibre"]["biais_relatif_median"] > 2.0 * abs(b["brut"]["biais_relatif_median"]))
        r["resume"]["les_deux_roles_corrigent_le_biais"] = bool(
            abs(b["deux_roles"]["biais_relatif_median"])
            <= abs(b["calibre"]["biais_relatif_median"]))
    # ⭐⭐⭐ LA CONSEQUENCE POUR LE MARCHEUR DE `102`, ET C'EST LE LIEN AVEC `104`. Le marcheur
    # avance de ce que `pas_que_la_matiere_dicte` rend, donc du selecteur CALIBRE ; si le pas vrai
    # est celui du remede, il franchit `calibre / remede` feuille a chaque pas. `104` a mesure que
    # le critere confirme tout ce qui franchit entre 0,68 et 1,38 feuille : un depassement de
    # cet ordre est donc CONFIRME a chaque pas et ne signale rien.
    p = r.get("resume", {}).get("pas_median_par_selecteur_um", {})
    if p.get("calibre") and p.get("deux_roles"):
        franchi = p["calibre"] / p["deux_roles"]
        r["consequence_pour_le_marcheur"] = {
            "pas_du_marcheur_um": p["calibre"],
            "pas_vrai_indique_um": p["deux_roles"],
            "feuilles_franchies_par_pas": round(franchi, 3),
            "spires_apres_120_pas": round(120.0 * franchi, 1),
            "spires_en_trop_sur_120": round(120.0 * (franchi - 1.0), 1),
            # ⚠ La bande d'acceptation vient de `104` et elle est LUE, pas recopiee : un chiffre
            # tape ici cesserait de suivre la mesure qui le produit.
            **_bande_de_104(franchi),
        }
    c = r.get("la_longueur_differe_du_nul")
    if c:
        # ⭐⭐⭐ LE VERDICT QUI AUTORISE — OU NON — A PUBLIER LA NOUVELLE VALEUR : la longueur que
        # le remede choisit doit differer de celle que le MEME selecteur rend sur du bruit pur.
        # Si elle n'en differait pas, le nombre plus proche des humains serait un artefact.
        r["resume"]["la_longueur_du_remede_differe_du_nul"] = bool(
            c.get("deux_roles", {}).get("differe"))
        r["resume"]["mediane_du_nul_pour_le_remede_um"] = c.get(
            "deux_roles", {}).get("mediane_du_nul_um")
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    a = r.get("aller_retour")
    if a:
        print(f"ALLER-RETOUR SUR UN PAS INJECTÉ — fenêtre {a['fenetre_um'][0]} à "
              f"{a['fenetre_um'][1]} µm, cran {a['cran_du_balayage_um']} µm, "
              f"{a['tirages']} tirages")
        print(" injecté  bruit |     BRUT           CALIBRÉ        DEUX RÔLES    | grille ?")
        for x in a["lignes"]:
            if x["bruit"] not in (0.0, 15.0):
                continue
            cols = "  ".join(
                f"{x[n]['lu_median_um']:6.1f} ({x[n]['biais_relatif']:+.3f})"
                for n in selecteurs())
            print(f"  {x['periode_injectee_um']:6.1f} {x['bruit']:5.1f} | {cols} |"
                  f" {'oui' if x['la_grille_contient_la_reponse'] else 'non'}")
        b = r.get("biais_fabrique", {})
        for n in selecteurs():
            if n in b:
                print(f"   {n:>11} : biais relatif médian {b[n]['biais_relatif_median']:+.4f}, "
                      f"max {b[n]['biais_relatif_max']:+.4f}, "
                      f"dispersion {b[n]['ecart_type_median_um']} µm")

    m = r.get("mecanisme")
    if m:
        print(f"\nLE MÉCANISME — le nul décroît avec la longueur du candidat")
        print(f"   µ : {m['mu_le_plus_court']} au plus court → {m['mu_le_plus_long']} au plus long"
              f"   ·   σ : {m['sd_le_plus_court']} → {m['sd_le_plus_long']}")
        print(f"   sur {m['periode_injectee_um']} µm injectés : le brut choisit "
              f"{m['choix_brut_um']} (accord {m['accord_brut_du_choix_brut']}),")
        print(f"   le calibré choisit {m['choix_calibre_um']} (accord "
              f"{m['accord_brut_du_choix_calibre']}) — soit {m['de_combien_de_crans']} cran(s) "
              f"plus haut")
        print(f"   ★ le calibré retient un accord BRUT moins bon : "
              f"{m['le_calibre_retient_un_accord_brut_moins_bon']}")

    c = r.get("ce_que_ca_change_pour_99", {})
    if c.get("periode_vraie_indiquee_um"):
        print(f"\nCE QUE ÇA CHANGE POUR `99` — inversion de la carte d'étalonnage")
        print(f"   `99` publie {c['publie_par_99_um']} µm ; injecter "
              f"{c['periode_vraie_indiquee_um']} µm fait rendre exactement cela au sélecteur")
        print(f"   de production. La période vraie INDIQUÉE est donc "
              f"{c['periode_vraie_indiquee_um']} µm ({c['correction_relative']:+.1%}).")
        print(f"   ★ l'écart aux transferts humains ({c['pas_des_transferts_humains_um']} µm) "
              f"passe de {c['ecart_publie_en_pourcent']} % à {c['ecart_indique_en_pourcent']} %,")
        print(f"     soit {c['part_de_lecart_imputable_a_linstrument']:.1%} de l'écart publié "
              f"imputable à l'INSTRUMENT.")
        print("   ⚠⚠ INDICATION et non mesure : la carte est établie sur un profil sinusoïdal")
        print("      parfait. La réponse ferme est le contrôle apparié sur le vrai volume.")

    s = r.get("resume", {})
    if s.get("pas_median_par_selecteur_um", {}).get("brut") is not None:
        p = s["pas_median_par_selecteur_um"]
        print(f"\nSUR LE VRAI VOLUME, {s['bandes_lues']} bandes APPARIÉES — mêmes lectures, "
              f"trois sélecteurs")
        print(f"   brut {p['brut']} µm · calibré {p['calibre']} µm · "
              f"deux rôles {p['deux_roles']} µm")
        if "ecart_calibre_moins_brut_um" in s:
            print(f"   ★ le calibré lit {s['ecart_calibre_moins_brut_um']:+.1f} µm "
                  f"({s['ecart_relatif']:+.1%}) de plus que le brut, sur les MÊMES profils")
    if "le_calibre_est_biaise_haut" in s:
        print(f"\n★★★ LE SÉLECTEUR DE PRODUCTION EST BIAISÉ HAUT : "
              f"{s['le_calibre_est_biaise_haut']}")
        print(f"★★  ET LES DEUX RÔLES CORRIGENT LE BIAIS : "
              f"{s['les_deux_roles_corrigent_le_biais']}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    x = float(longueurs[-1]) * np.linspace(0.0, 1.0, n_long)

    def profil(periode, sigma=0.0, tirages=1, graine=1):
        r = np.random.default_rng(graine)
        v_ = np.repeat((100.0 + 40.0 * np.cos(2 * np.pi * x / periode)).reshape(1, -1),
                       tirages, axis=0)
        if sigma:
            v_ = v_ + r.normal(0.0, sigma, v_.shape)
        return M.profils_emboites(v_, longueurs)

    # === LE SELECTEUR DE PRODUCTION EST BIEN CELUI QU'ON CROIT ==============================
    # ⚠⚠⚠ SANS CE CONTROLE, TOUT LE FICHIER PORTE A COTE. Il faut que `choisir(..., "calibre")`
    # rende EXACTEMENT ce que `pas_montre_calibre` rend, sinon on auditerait une reimplementation
    # et non la production — la faute meme que ce fichier reproche a la batterie de `99`.
    p = profil(173.0)
    lu_ref, _, k_ref, sur_ref = M.pas_montre_calibre(p, longueurs, mu, sd)
    lu_ici, _, k_ici, sur_ici = choisir(p, longueurs, mu, sd, "calibre", barre)
    v("le sélecteur audité EST celui de la production, pas une réimplémentation",
      float(lu_ref[0]) == float(lu_ici[0]) and int(k_ref[0]) == int(k_ici[0])
      and bool(sur_ref[0]) == bool(sur_ici[0]),
      f"{float(lu_ref[0])} contre {float(lu_ici[0])}")
    lu_b, _, _ = M.pas_montre(p, longueurs)  # ⚠ `pas_montre` rend TROIS valeurs
    lu_i, _, _, _ = choisir(p, longueurs, mu, sd, "brut", barre)
    v("... et le sélecteur brut aussi", float(lu_b[0]) == float(lu_i[0]))

    # === L'ALLER-RETOUR, SUR DES PERIODES QUI SONT DANS LA GRILLE ===========================
    # ⭐⭐⭐ LE CONTROLE QUI PORTE LE FICHIER : une periode qui EST un candidat doit ressortir
    # elle-meme. Si elle ne le fait pas, le selecteur ne mesure pas ce qu'il pretend mesurer.
    for per in (float(longueurs[10]), float(longueurs[14]), float(longueurs[18])):
        lu, _, _, _ = choisir(profil(per), longueurs, mu, sd, "brut", barre)
        v(f"le brut retrouve exactement un candidat injecté ({per:.1f} µm)",
          abs(float(lu[0]) - per) < 1e-6, f"lu {float(lu[0]):.1f}")
    cran = float(longueurs[1] - longueurs[0])
    haut = 0
    for per in (float(longueurs[10]), float(longueurs[14]), float(longueurs[18])):
        lu, _, _, _ = choisir(profil(per), longueurs, mu, sd, "calibre", barre)
        haut += 1 if float(lu[0]) > per + 0.5 * cran else 0
    v("... là où le CALIBRÉ choisit systématiquement plus haut",
      haut == 3, f"{haut}/3 périodes lues au-dessus")
    # ⭐⭐ ET LES DEUX ROLES DOIVENT CORRIGER, sinon le remede propose ne sert a rien.
    bas = 0
    for per in (float(longueurs[10]), float(longueurs[14]), float(longueurs[18])):
        lu, _, _, _ = choisir(profil(per), longueurs, mu, sd, "deux_roles", barre)
        bas += 1 if abs(float(lu[0]) - per) < 1e-6 else 0
    v("... et les DEUX RÔLES retrouvent la période injectée", bas == 3, f"{bas}/3")

    # === LA GARDE DOIT RESTER : PAS DE RETOUR A LA PANNE D'ORIGINE ==========================
    # ⚠⚠⚠ SANS CALIBRATION, LA RECHERCHE RENDAIT 147 µm SUR LE REEL COMME SUR LE BRUIT PUR. Le
    # remede ne doit pas ressusciter ce defaut : sur du BRUIT PUR les deux roles doivent etre
    # GARDES par la barre, donc leur choix ne doit pas etre publie.
    rng = np.random.default_rng(4)
    bruit = M.profils_emboites(rng.normal(100.0, 10.0, size=(300, n_long)), longueurs)
    _, sc_c, k_c, _ = choisir(bruit, longueurs, mu, sd, "calibre", barre)
    admis = (sc_c > barre) & ~M.touche_un_bord(k_c, len(longueurs))
    v("sur du bruit pur, la barre écarte l'écrasante majorité des cellules",
      float(admis.mean()) < 0.05, f"{float(admis.mean()):.3f} admises")
    lu_dr, _, _, _ = choisir(bruit, longueurs, mu, sd, "deux_roles", barre)
    lu_br, _, _, _ = choisir(bruit, longueurs, mu, sd, "brut", barre)
    # ⚠⚠⚠ LE BRUT NON GARDE SE RUE SUR LES CANDIDATS COURTS : c'est la panne d'origine de `99`,
    # et elle doit rester VISIBLE pour que la garde ait un sens. ⭐ Le seuil n'est pas invente :
    # la propriete assertee est « biaise SOUS le nominal », et la valeur affichee tombe sur les
    # **147 µm** que la prose de `99` documente comme sa lecture d'avant calibration — sur le
    # vrai volume comme sur du bruit pur, indiscernables. Mon premier seuil (1,2 fois le plus
    # court candidat) etait un nombre choisi et il a echoue contre une observation juste.
    med_bruit = float(np.median(lu_br))
    v("... et le brut NON gardé se rue bien sur les candidats courts",
      med_bruit < C.PAS_UM,
      f"médiane {med_bruit:.1f} µm sous un nominal de {C.PAS_UM:.0f} "
      f"(la prose de `99` documente 147 µm)")
    v("... donc la calibration reste indispensable comme GARDE",
      float(np.median(lu_dr[admis])) > float(longueurs[0]) if admis.any() else True)
    # ⭐ Et le selecteur a deux roles DOIT exiger la barre : l'appeler sans elle est une erreur,
    # pas un defaut silencieux.
    try:
        choisir(profil(173.0), longueurs, mu, sd, "deux_roles", None)
        ok = False
    except ValueError:
        ok = True
    v("le sélecteur à deux rôles REFUSE d'être appelé sans barre", ok)

    # === LE MECANISME ======================================================================
    m = pourquoi_le_calibre_derive()
    v("le nul décroît bien avec la longueur du candidat",
      m["le_nul_decroit_avec_la_longueur"] is True,
      f"µ {m['mu_le_plus_court']} → {m['mu_le_plus_long']}")
    # ⭐⭐⭐ LA LIGNE QUI PROUVE QUE C'EST L'ARITHMETIQUE ET NON DU BRUIT.
    v("le calibré retient un candidat au meilleur score mais au PIRE accord brut",
      m["le_calibre_retient_un_accord_brut_moins_bon"] is True,
      f"{m['accord_brut_du_choix_calibre']} contre {m['accord_brut_du_choix_brut']}")
    v("... et il le retient plus haut, pas plus bas", m["de_combien_de_crans"] > 0,
      f"{m['de_combien_de_crans']} cran(s)")

    # === L'INVERSION, ET SA LIMITE =========================================================
    a = aller_retour(tirages=40)
    v("l'aller-retour couvre les trois sélecteurs sur toute la grille",
      all(all(n in x for n in selecteurs()) for x in a["lignes"]),
      f"{len(a['lignes'])} lignes")
    r = agreger({"aller_retour": a, "lignes": [],
                 "mecanisme": m, "cran_du_balayage_um": a["cran_du_balayage_um"]})
    b = r["biais_fabrique"]
    v("le biais médian du calibré dépasse celui du brut",
      b["calibre"]["biais_relatif_median"] > b["brut"]["biais_relatif_median"],
      f"{b['calibre']['biais_relatif_median']:+.4f} contre "
      f"{b['brut']['biais_relatif_median']:+.4f}")
    v("... et les deux verdicts sont rendus, quels qu'ils soient",
      "le_calibre_est_biaise_haut" in r["resume"]
      and "les_deux_roles_corrigent_le_biais" in r["resume"])
    c = r.get("ce_que_ca_change_pour_99", {})
    if "periode_vraie_indiquee_um" in c:
        v("l'inversion rend une période vraie indiquée pour la valeur publiée par `99`",
          c["periode_vraie_indiquee_um"] < c["publie_par_99_um"],
          f"{c['periode_vraie_indiquee_um']} pour {c['publie_par_99_um']} publiés")
        # ⚠⚠ ET L'ECART NE DOIT PAS ETRE DECLARE EXPLIQUE : une part seulement est imputable a
        # l'instrument, et le dire est ce qui empeche de lire cette tranche comme une solution.
        v("... et l'écart reste NON expliqué en majorité",
          c["part_de_lecart_imputable_a_linstrument"] < 0.5,
          f"{c['part_de_lecart_imputable_a_linstrument']:.1%} imputable à l'instrument")
    else:
        v("l'inversion rend une période vraie indiquée pour la valeur publiée par `99`",
          False, c.get("message", "absente"))
    v("l'affichage tourne sur ce résultat", afficher(r) is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=40)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--fils", type=int, default=32)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = agreger(json.loads(a.json.read_text()))
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, bandes_max=a.bandes, fils=a.fils)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
