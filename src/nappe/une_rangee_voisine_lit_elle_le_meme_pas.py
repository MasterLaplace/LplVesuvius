"""Une rangée VOISINE du treillis lit-elle le même pas à la même couture ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST LE PLAFOND DE `207` QUI LE FORCE. `207` a établi que le cumul
des pas de `204` traverse son tronçon sans quitter le feuillet, et il a nommé sa borne : avec la
dérive seule, un lecteur PARFAIT donnerait encore **34,8806 voxels** sur une rangée, contre un
demi-feuillet de **36**. Une rangée se traverse de justesse, et rien de plus long ne se traverse,
quel que soit l'instrument. La seule chose qui batte une marche en racine de `n` est une référence
qui ne dérive pas — ou une FERMETURE DE BOUCLE.

⭐⭐⭐⭐ ET LE TREILLIS EN OFFRE UNE, GRATUITE ET JAMAIS MESURÉE : la rangée **au-dessus** et la
rangée **au-dessous** traversent les mêmes coutures. Si le pas d'une couture est une propriété de la
SURFACE, trois rangées voisines doivent le lire pareil, et leur accord devient une contrainte que le
cumul d'une seule rangée n'a pas. Si le pas est local à la rangée, chaque rangée est seule et le
plafond de `207` est définitif.

⭐⭐⭐⭐ LES DEUX LECTURES SE PRÉDISENT AVANT LA MESURE, ET ELLES DIFFÈRENT D'UN FACTEUR DEUX ET DEMI.
`204` sépare le pas en un aléa de lecture et une dérive vraie. Deux rangées qui lisent la MÊME
couture se désaccordent de la racine de deux fois l'aléa ; deux rangées qui lisent des choses
DIFFÉRENTES se désaccordent de la racine de deux fois la dispersion entière. Les deux nombres
sortent de `204` et se posent avant qu'un seul chunk ne soit lu.

⚠⚠ ET LES DEUX VOISINES SONT LUES, PAS UNE : choisir laquelle serait un choix, et les deux donnent
en prime un contrôle gratuit — elles doivent se comporter pareil vis-à-vis de la rangée médiane.

Usage :
    uv run python src/nappe/une_rangee_voisine_lit_elle_le_meme_pas.py --verifier
    uv run python src/nappe/une_rangee_voisine_lit_elle_le_meme_pas.py \\
        --json docs/mesures/une_rangee_voisine_lit_elle_le_meme_pas.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import (la_ligne,  # noqa: E402
                                                         le_pas_de_k_rangees)
from la_derive_saccumule_t_elle import la_ligne_declaree  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from le_creux_bouge_t_il_avec_le_maillage import (la_decomposition,  # noqa: E402
                                                  la_pente, lappariement)
from le_cumul_recale_traverse_t_il_la_rangee import (la_dispersion_de_204,  # noqa: E402
                                                     lexcursion_predite)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261016
LES_RANGEES = 16

LA_QUESTION_DECLAREE = ("deux rangées voisines du treillis lisent-elles le même pas à la même "
                        "couture, ou chacune le sien ?")
LES_EPREUVES_DECLAREES = ("les pas de deux rangées voisines sont-ils appariés",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def les_rangees_du_treillis(gy: int) -> dict:
    """La rangée déclarée et ses DEUX voisines — aucune n'est choisie.

    ⚠⚠ LES DEUX VOISINES SONT LUES PARCE QUE N'EN LIRE QU'UNE SERAIT UN CHOIX, et parce qu'elles
    donnent un controle gratuit : au-dessus et au-dessous doivent se comporter pareil vis-a-vis de
    la mediane. Une seule voisine qui s'accorderait pendant que l'autre non serait un fait, pas un
    bruit — et il faut deux voisines pour le voir.

    ⚠ La mediane vient de `la_ligne_declaree`, jamais retapee.
    """
    m = int(la_ligne_declaree(int(gy)))
    voisines = [x for x in (m - 1, m + 1) if 0 <= x < int(gy)]
    if not voisines:
        return {"decidable": False,
                "raison": f"un treillis de {int(gy)} rangées n'offre aucune voisine"}
    return {"decidable": True, "la_mediane": m, "les_voisines": voisines,
            "les_rangees": [m] + voisines}


def le_desaccord_predit(alea, dispersion) -> dict:
    """Les DEUX lectures possibles, posées avant la mesure.

    ⭐⭐⭐⭐ ELLES DIFFERENT D'UN FACTEUR QUE `204` FIXE, ET AUCUN REGLAGE N'ENTRE LA-DEDANS. La
    difference de deux mesures independantes d'une MEME quantite a pour ecart-type la racine de deux
    fois celui d'une mesure ; si les deux rangees lisent le meme pas, ce qui reste entre elles est
    leur seul alea de lecture. Si elles lisent des choses differentes, c'est leur dispersion
    ENTIERE qui les separe.

    ⚠ Les deux nombres viennent de `204` et de nulle part ailleurs : c'est lui qui a separe l'alea
    de la derive, et cette tranche ne refait pas cette separation.
    """
    if alea is None or dispersion is None:
        return {"decidable": False, "raison": "l'aléa ou la dispersion de `204` manque"}
    deux = 2.0 ** 0.5
    return {"decidable": True,
            "lalea_de_204_en_voxels": round(float(alea), 4),
            "la_dispersion_de_204_en_voxels": round(float(dispersion), 4),
            "si_elles_lisent_le_meme_pas_en_voxels": round(deux * float(alea), 4),
            "si_elles_lisent_autre_chose_en_voxels": round(deux * float(dispersion), 4),
            "le_rapport_des_deux_lectures": round(float(dispersion) / float(alea), 4)}


def les_pas_dune_rangee(droits: dict, gauches: dict, rangees) -> dict:
    """Le pas de chaque couture d'une rangée du treillis, indexé par sa COLONNE DE GAUCHE.

    ⚠⚠⚠ L'INDEX EST LA COLONNE, ET C'EST CE QUI REND L'APPARIEMENT POSSIBLE : deux rangees du
    treillis n'ont pas forcement les memes chunks lus, donc les apparier par RANG dans leur propre
    liste joindrait des coutures qui ne sont pas au meme endroit du rouleau. C'est le defaut que
    `201` a paye et que `202` a repare en publiant `les_colonnes_des_pas`.
    """
    out = {}
    for a in sorted(droits):
        b = a + 1
        if b not in droits or a not in gauches or b not in gauches:
            continue
        lu = le_pas_de_k_rangees(droits[a], gauches[b], rangees)
        if lu.get("decidable"):
            out[int(a)] = float(lu["le_pas_en_voxels"])
    return out


def les_coutures_communes(une: dict, autre: dict) -> list[int]:
    """Les colonnes où les DEUX rangées ont lu un pas — et rien d'autre."""
    return sorted(set(une) & set(autre))


def le_desaccord(une: dict, autre: dict, communes) -> dict:
    """Ce qui sépare deux rangées sur les coutures qu'elles partagent.

    ⚠⚠ L'ECART-TYPE EST PUBLIE A COTE DE LA DISPERSION DE CHAQUE RANGEE, toujours : deux rangees
    qui ne liraient qu'une valeur constante se desaccorderaient de zero sans rien mesurer. C'est la
    dette de `203`, et elle se paie ici aussi.
    """
    if len(communes) < 3:
        return {"decidable": False, "raison": "moins de trois coutures communes"}
    a = np.asarray([une[c] for c in communes], dtype=float)
    b = np.asarray([autre[c] for c in communes], dtype=float)
    d = a - b
    return {"decidable": True, "les_coutures_communes": len(communes),
            "lecart_type_du_desaccord_en_voxels": round(float(np.std(d)), 4),
            "le_desaccord_median_en_voxels": round(float(np.median(np.abs(d))), 4),
            "la_dispersion_de_la_premiere_en_voxels": round(float(np.std(a)), 4),
            "la_dispersion_de_la_seconde_en_voxels": round(float(np.std(b)), 4)}


def ce_que_le_desaccord_dit(desaccord: dict, prediction: dict) -> dict:
    """Laquelle des deux lectures posées d'avance la mesure choisit-elle ?

    ⭐⭐⭐⭐ LE VERDICT EST UNE COMPARAISON A DEUX NOMBRES POSES AVANT LA MESURE, donc il ne contient
    aucun seuil : l'observe tombe plus pres de l'un ou de l'autre, et le rapport a chacun est
    publie. Un critere qui aurait choisi une frontiere entre les deux aurait ete un seuil choisi.

    ⚠ Si l'observe tombe HORS des deux, la fonction le dit plutot que de le ranger de force.
    """
    if not desaccord.get("decidable") or not prediction.get("decidable"):
        return {"decidable": False, "raison": "le désaccord ou la prédiction manque"}
    obs = float(desaccord["lecart_type_du_desaccord_en_voxels"])
    meme = float(prediction["si_elles_lisent_le_meme_pas_en_voxels"])
    autre = float(prediction["si_elles_lisent_autre_chose_en_voxels"])
    if meme <= 0.0 or autre <= 0.0:
        return {"decidable": False, "raison": "une des deux prédictions est nulle"}
    plus_pres = ("le même pas" if abs(obs - meme) < abs(obs - autre) else "autre chose")
    return {"decidable": True,
            "lecart_type_observe_en_voxels": round(obs, 4),
            "le_rapport_a_la_lecture_meme_pas": round(obs / meme, 4),
            "le_rapport_a_la_lecture_autre_chose": round(obs / autre, 4),
            "de_laquelle_il_est_le_plus_proche": plus_pres,
            "il_tombe_entre_les_deux": bool(min(meme, autre) <= obs <= max(meme, autre))}


def ce_que_les_deux_rangees_partagent(une, autre) -> dict:
    """La part du pas qui est COMMUNE aux deux rangées, et le bruit propre de chacune.

    ⭐⭐⭐⭐ C'EST LA DECOMPOSITION DE `202`, IMPORTEE ET NON REECRITE, et c'est elle qui transforme
    « appariees mais pas identiques » en deux nombres. Le modele est le sien : les deux rangees
    voient une meme derive, et chacune y ajoute une erreur qui lui est propre. Alors la covariance
    des deux suites EST la variance de ce qu'elles partagent, et ce qui reste de chaque variance est
    le bruit de cette rangee-la.

    ⚠⚠ ET IL SE REFUTE PAR SES PROPRES NOMBRES si la variance commune sort negative ou plus grande
    que l'une des deux variances observees — ce qui est le seul comportement honnete a cet endroit.
    """
    a = [float(x) for x in une]
    b = [float(x) for x in autre]
    if len(a) < 3 or len(a) != len(b):
        return {"decidable": False, "raison": "moins de trois coutures appariées"}
    p = la_pente(a, b)
    d = la_decomposition(a, b, p)
    if not d.get("decidable"):
        return d
    return {"decidable": True,
            "la_derive_partagee_en_voxels": d.get("la_derive_commune_en_voxels"),
            "le_bruit_de_la_premiere_en_voxels": d.get("le_bruit_du_maillage_en_voxels"),
            "le_bruit_de_la_seconde_en_voxels": d.get("le_bruit_du_creux_en_voxels"),
            "le_signal_sur_bruit_de_la_premiere": d.get("le_signal_sur_bruit_du_maillage"),
            "le_signal_sur_bruit_de_la_seconde": d.get("le_signal_sur_bruit_du_creux"),
            "la_pente_signee": (None if p is None else round(float(p), 4))}


def juger(desaccords: dict, epreuves: dict, lecture: dict, prediction: dict,
          mediane: int, partages: dict | None = None) -> dict:
    """Les rangées voisines lisent-elles le même pas, et les deux se comportent-elles pareil ?

    ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE, qui porte sur la PREMIERE voisine — celle du
    dessus. La seconde est un CONTROLE : une seule epreuve est declaree, donc la garantie reste
    entiere, et ce que la seconde voisine rend est publie comme description.
    """
    if not lecture.get("decidable"):
        return {"decidable": False, "raison": "la lecture du désaccord manque"}
    noms = sorted(epreuves)
    premiere = noms[0] if noms else None
    if premiere is None or not epreuves[premiere].get("decidable"):
        return {"decidable": False, "raison": "l'épreuve manque"}
    return {"decidable": True,
            "la_rangee_mediane": int(mediane),
            "la_voisine_de_lepreuve": int(premiere),
            "les_voisines_en_controle": [int(x) for x in noms[1:]],
            "la_correlation_absolue": epreuves[premiere]["la_correlation_absolue"],
            "la_valeur_p": epreuves[premiere]["la_valeur_p"],
            "les_deux_pas_sont_apparies": bool(
                epreuves[premiere]["les_deux_pas_sont_apparies"]),
            "les_correlations_des_controles": [
                epreuves[x]["la_correlation_absolue"] for x in noms[1:]
                if epreuves[x].get("decidable")],
            "lecart_type_observe_en_voxels": lecture["lecart_type_observe_en_voxels"],
            "si_elles_lisent_le_meme_pas_en_voxels": prediction.get(
                "si_elles_lisent_le_meme_pas_en_voxels"),
            "si_elles_lisent_autre_chose_en_voxels": prediction.get(
                "si_elles_lisent_autre_chose_en_voxels"),
            "le_rapport_a_la_lecture_meme_pas": lecture["le_rapport_a_la_lecture_meme_pas"],
            "le_rapport_a_la_lecture_autre_chose": lecture["le_rapport_a_la_lecture_autre_chose"],
            "de_laquelle_il_est_le_plus_proche": lecture["de_laquelle_il_est_le_plus_proche"],
            "les_coutures_communes": (desaccords.get(premiere) or {}).get(
                "les_coutures_communes"),
            "la_derive_partagee_en_voxels": ((partages or {}).get(premiere) or {}).get(
                "la_derive_partagee_en_voxels"),
            "le_bruit_de_la_mediane_en_voxels": ((partages or {}).get(premiere) or {}).get(
                "le_bruit_de_la_premiere_en_voxels"),
            "le_bruit_de_la_voisine_en_voxels": ((partages or {}).get(premiere) or {}).get(
                "le_bruit_de_la_seconde_en_voxels"),
            "le_signal_sur_bruit_de_la_mediane": ((partages or {}).get(premiere) or {}).get(
                "le_signal_sur_bruit_de_la_premiere")}


def deux_rangees_fabriquees(coutures: int, partage: bool, derive: float, alea: float,
                            graine: int) -> tuple[dict, dict]:
    """Deux rangées dont les pas partagent — ou non — la même dérive de surface.

    ⭐⭐⭐⭐ LE PARTAGE EST LA SEULE CHOSE QUI CHANGE ENTRE LES DEUX FACES : la derive posee, l'alea
    pose et le nombre de coutures sont les memes des deux cotes. Une face negative batie sur une
    matiere plus bruitee serait plus facile a refuser, donc elle ne mesurerait pas le bon refus.
    """
    r = _rng(int(graine))
    commune = r.normal(0.0, float(derive), size=int(coutures))
    autre = commune if partage else r.normal(0.0, float(derive), size=int(coutures))
    une = {int(c): float(commune[c] + r.normal(0.0, float(alea))) for c in range(int(coutures))}
    deux = {int(c): float(autre[c] + r.normal(0.0, float(alea))) for c in range(int(coutures))}
    return une, deux


def sur_letalon(coutures: int = 240, derive: float = 2.233, alea: float = 1.029,
                graine: int = GRAINE, replicats: int = 12,
                tirages: int = PERMUTATIONS) -> dict:
    """L'épreuve voit-elle deux rangées qui partagent leur dérive, et se tait-elle sinon ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202`.
    ⚠⚠ LA DERIVE ET L'ALEA POSES SONT CEUX QUE `204` A MESURES : l'etalon exerce donc l'epreuve au
    regime ou elle va servir, et non a un regime plus facile.
    """
    vus, ecarts = 0, []
    for i in range(int(replicats)):
        une, deux = deux_rangees_fabriquees(coutures, True, derive, alea,
                                            int(graine) + 1000 * i)
        communes = les_coutures_communes(une, deux)
        ep = lappariement([une[c] for c in communes], [deux[c] for c in communes],
                          tirages, int(graine) + i, GARANTIE_PAR_EPREUVE)
        vus += int(bool(ep.get("les_deux_pas_sont_apparies")))
        d = le_desaccord(une, deux, communes)
        if d.get("decidable"):
            ecarts.append(float(d["lecart_type_du_desaccord_en_voxels"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux, sans = 0, []
    for i in range(replicats_du_refus):
        une, deux = deux_rangees_fabriquees(coutures, False, derive, alea,
                                            int(graine) + 500000 + 1000 * i)
        communes = les_coutures_communes(une, deux)
        ep = lappariement([une[c] for c in communes], [deux[c] for c in communes],
                          tirages, int(graine) + 77 + i, GARANTIE_PAR_EPREUVE)
        faux += int(bool(ep.get("les_deux_pas_sont_apparies")))
        d = le_desaccord(une, deux, communes)
        if d.get("decidable"):
            sans.append(float(d["lecart_type_du_desaccord_en_voxels"]))
    return {"decidable": True,
            "les_coutures_par_replicat": int(coutures),
            "la_derive_posee_en_voxels": float(derive),
            "lalea_pose_en_voxels": float(alea),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "lecart_median_sur_la_face_positive_en_voxels": (
                round(float(np.median(ecarts)), 4) if ecarts else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "lecart_median_sur_la_face_negative_en_voxels": (
                round(float(np.median(sans)), 4) if sans else None),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES) -> dict:
    """Les trois rangées du treillis, leurs pas appariés par colonne, l'épreuve et l'étalon."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    if meta is None:
        try:
            meta = array_meta(f"{BUCKET}/{v['cle']}", 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, _hx = meta["chunks"]
    rows = meta["shape"][1]
    gy = -(-rows // hy)
    echelle = les_rangees_du_treillis(gy)
    if not echelle.get("decidable"):
        return {"decidable": False, "raison": echelle.get("raison")}
    lignes, pas_par_rangee = {}, {}
    for r_ in echelle["les_rangees"]:
        lg = la_ligne(v, delai, colonnes, ouvrir, meta, combien, int(r_))
        if not lg.get("decidable"):
            return {"decidable": False,
                    "raison": f"la rangée {r_} est vide : {lg.get('raison')}"}
        pannes = les_pannes_de_reseau(lg.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": f"{pannes} chunks perdus par le réseau sur la rangée {r_} — une "
                              f"rangée dont le fil est tombé n'est pas comparable"}
        lignes[int(r_)] = {k: x for k, x in lg.items()
                           if k not in ("droits", "gauches", "les_colonnes")}
        pas_par_rangee[int(r_)] = les_pas_dune_rangee(lg["droits"], lg["gauches"],
                                                      lg["les_rangees_lues"])
    par_204 = la_dispersion_de_204()
    prediction = le_desaccord_predit(par_204.get("lalea_en_voxels"),
                                     par_204.get("la_dispersion_en_voxels"))
    mediane = int(echelle["la_mediane"])
    desaccords, epreuves = {}, {}
    for r_ in echelle["les_voisines"]:
        communes = les_coutures_communes(pas_par_rangee[mediane], pas_par_rangee[int(r_)])
        desaccords[int(r_)] = le_desaccord(pas_par_rangee[mediane], pas_par_rangee[int(r_)],
                                           communes)
        epreuves[int(r_)] = lappariement(
            [pas_par_rangee[mediane][c] for c in communes],
            [pas_par_rangee[int(r_)][c] for c in communes],
            PERMUTATIONS, graine, GARANTIE_PAR_EPREUVE)
    partages = {}
    for r_ in echelle["les_voisines"]:
        communes = les_coutures_communes(pas_par_rangee[mediane], pas_par_rangee[int(r_)])
        partages[int(r_)] = ce_que_les_deux_rangees_partagent(
            [pas_par_rangee[mediane][c] for c in communes],
            [pas_par_rangee[int(r_)][c] for c in communes])
    premiere = sorted(epreuves)[0] if epreuves else None
    lecture = ce_que_le_desaccord_dit(desaccords.get(premiere) or {}, prediction)
    # ⭐⭐⭐⭐ CE QUE LA BOUCLE RAPPORTERAIT, ET C'EST LE SEUL NOMBRE QUI DECIDE. Moyenner les
    # rangees du treillis retirerait le bruit PROPRE a chaque rangee et laisserait ce qu'elles
    # PARTAGENT ; l'excursion d'une marche de `n` pas de cette dispersion-la est donc le plancher
    # que la fermeture verticale peut atteindre. La fonction est celle de `207`, importee.
    partage = ((partages.get(premiere) or {}).get("la_derive_partagee_en_voxels")
               if premiere is not None else None)
    coutures = (desaccords.get(premiere) or {}).get("les_coutures_communes")
    ce_que_la_boucle_rapporte = (lexcursion_predite(partage, int(coutures))
                                 if partage and coutures else
                                 {"decidable": False,
                                  "raison": "la dérive partagée ou les coutures manquent"})
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "les_rangees_du_treillis": echelle,
        "ce_que_204_a_rendu": par_204,
        "la_prediction": prediction,
        "les_lignes": lignes,
        "les_pas_par_rangee": {str(k): len(x) for k, x in pas_par_rangee.items()},
        "les_desaccords": {str(k): x for k, x in desaccords.items()},
        "les_epreuves": {str(k): x for k, x in epreuves.items()},
        "les_partages": {str(k): x for k, x in partages.items()},
        "la_lecture": lecture,
        "ce_que_la_boucle_rapporte": ce_que_la_boucle_rapporte,
        "ce_que_la_rangee_seule_donne": lexcursion_predite(
            par_204.get("la_dispersion_en_voxels"),
            int((desaccords.get(premiere) or {}).get("les_coutures_communes") or 0)),
        "le_verdict": juger(desaccords, epreuves, lecture, prediction, mediane,
                            partages),
        "letalon": sur_letalon(graine=graine, replicats=replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    ec = r.get("les_rangees_du_treillis") or {}
    lignes = r.get("les_lignes") or {}
    une = lignes.get(ec.get("la_mediane")) or next(iter(lignes.values()), {})
    print(f"UNE RANGÉE VOISINE LIT-ELLE LE MÊME PAS   segment {une.get('segment')} · "
          f"rangées {ec.get('les_rangees')} · {une.get('colonnes_demandees')} colonnes "
          f"demandées · {len(une.get('les_rangees_lues') or [])} rangées de coupe")
    print(f"  LES RANGÉES LUES  " + " · ".join(
        f"{k}→{x.get('colonnes_lues')} chunks" for k, x in sorted(lignes.items())))
    print(f"  LES PAS           " + " · ".join(
        f"{k}→{n}" for k, n in sorted((r.get("les_pas_par_rangee") or {}).items())))
    p = r.get("la_prediction") or {}
    if p.get("decidable"):
        print(f"  LA PRÉDICTION     même pas → {p['si_elles_lisent_le_meme_pas_en_voxels']} · "
              f"autre chose → {p['si_elles_lisent_autre_chose_en_voxels']} · rapport "
              f"{p['le_rapport_des_deux_lectures']}")
    for k, d in sorted((r.get("les_desaccords") or {}).items()):
        if d.get("decidable"):
            print(f"  RANGÉE {k:<10} {d['les_coutures_communes']} coutures communes · désaccord "
                  f"{d['lecart_type_du_desaccord_en_voxels']} · dispersions "
                  f"{d['la_dispersion_de_la_premiere_en_voxels']} et "
                  f"{d['la_dispersion_de_la_seconde_en_voxels']}")
    for k, e in sorted((r.get("les_epreuves") or {}).items()):
        if e.get("decidable"):
            print(f"  ÉPREUVE {k:<9} |r| = {e['la_correlation_absolue']} contre "
                  f"{e['la_correlation_absolue_mediane_du_nul']} au mélange · "
                  f"{e['les_melanges_au_moins_aussi_forts']}/{e['tirages']} · P = "
                  f"{e['la_valeur_p']} · appariés {e['les_deux_pas_sont_apparies']}")
    for k, s in sorted((r.get("les_partages") or {}).items()):
        if s.get("decidable"):
            print(f"  PARTAGE {k:<9} dérive commune {s['la_derive_partagee_en_voxels']} · bruits "
                  f"{s['le_bruit_de_la_premiere_en_voxels']} et "
                  f"{s['le_bruit_de_la_seconde_en_voxels']} · S/B "
                  f"{s['le_signal_sur_bruit_de_la_premiere']}")
    for nom, cle in (("LA RANGÉE SEULE ", "ce_que_la_rangee_seule_donne"),
                     ("LA BOUCLE       ", "ce_que_la_boucle_rapporte")):
        x = r.get(cle) or {}
        if x.get("decidable"):
            print(f"  {nom}  {x['la_dispersion_de_204_en_voxels']} × racine de "
                  f"{x['les_coutures']} = {x['lecart_attendu_en_voxels']} voxels = "
                  f"{x['lecart_attendu_en_plis']} pli · sous le demi-pli "
                  f"{x['il_tient_sous_le_demi_pli']}")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        désaccord {ve['lecart_type_observe_en_voxels']} · rapport à "
              f"« même pas » {ve['le_rapport_a_la_lecture_meme_pas']} · à « autre chose » "
              f"{ve['le_rapport_a_la_lecture_autre_chose']} · plus proche de "
              f"« {ve['de_laquelle_il_est_le_plus_proche']} »")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (écart "
              f"{et['lecart_median_sur_la_face_positive_en_voxels']}) · {et['les_faux']} faux sur "
              f"{et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis (écart "
              f"{et['lecart_median_sur_la_face_negative_en_voxels']})")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★ une seule épreuve est déclarée, donc la garantie reste entière",
      len(LES_EPREUVES_DECLAREES) == 1
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)

    # ⚠⚠ LES DEUX VOISINES SONT LUES, ET LA MEDIANE VIENT DE `199`.
    e = les_rangees_du_treillis(396)
    v("★★★★ la médiane et ses DEUX voisines, aucune choisie",
      e["decidable"] and e["la_mediane"] == la_ligne_declaree(396)
      and e["les_voisines"] == [197, 199] and e["les_rangees"] == [198, 197, 199],
      str(e.get("les_rangees")))
    v("★★★ une rangée au bord du treillis n'a qu'une voisine, et la fonction le dit",
      les_rangees_du_treillis(2)["les_voisines"] == [0]
      if les_rangees_du_treillis(2)["decidable"] else False,
      str(les_rangees_du_treillis(2)))
    v("★★★ un treillis d'une seule rangée n'offre AUCUNE voisine",
      not les_rangees_du_treillis(1)["decidable"])

    # ⭐⭐⭐⭐ LES DEUX LECTURES SONT POSEES AVANT LA MESURE, ET ELLES VIENNENT DE `204`.
    p = le_desaccord_predit(1.029, 2.4587)
    v("★★★★ deux lectures d'une MÊME quantité se désaccordent de racine de deux fois l'aléa",
      p["decidable"]
      and abs(p["si_elles_lisent_le_meme_pas_en_voxels"] - round(2 ** 0.5 * 1.029, 4)) < 1e-9,
      str(p.get("si_elles_lisent_le_meme_pas_en_voxels")))
    v("★★★★ deux lectures de choses DIFFÉRENTES se désaccordent de la dispersion entière",
      abs(p["si_elles_lisent_autre_chose_en_voxels"]
          - round(2 ** 0.5 * 2.4587, 4)) < 1e-9)
    v("★★★ les deux lectures sont séparées par un facteur que `204` fixe",
      abs(p["le_rapport_des_deux_lectures"] - round(2.4587 / 1.029, 4)) < 1e-9)
    v("★★★ un aléa absent ne donne AUCUNE prédiction",
      not le_desaccord_predit(None, 2.0)["decidable"]
      and not le_desaccord_predit(1.0, None)["decidable"])
    v("★★★★ l'aléa et la dispersion viennent de `204` et de nulle part ailleurs",
      la_dispersion_de_204().get("lalea_en_voxels")
      == (json.loads((MESURES / "combien_de_rangees_faut_il_pour_lire_le_pas.json")
                     .read_text(encoding="utf-8"))["le_verdict"]["lalea_au_maximum_en_voxels"]))

    # ⚠⚠⚠ L'APPARIEMENT SE FAIT PAR COLONNE, JAMAIS PAR RANG.
    une = {3: 1.0, 4: 2.0, 7: 3.0}
    deux = {4: 20.0, 5: 30.0, 7: 40.0}
    v("★★★★ seules les colonnes lues des DEUX côtés entrent",
      les_coutures_communes(une, deux) == [4, 7],
      str(les_coutures_communes(une, deux)))
    v("★★★ deux rangées sans colonne commune ne rendent rien",
      les_coutures_communes({1: 1.0}, {2: 1.0}) == [])
    trois = {c: float(c) for c in range(10)}
    quatre = {c: float(c) + 5.0 for c in range(10)}
    d = le_desaccord(trois, quatre, les_coutures_communes(trois, quatre))
    v("★★★★ un décalage CONSTANT ne fait aucun désaccord d'écart-type, et le médian le voit",
      d["decidable"] and abs(d["lecart_type_du_desaccord_en_voxels"]) < 1e-9
      and abs(d["le_desaccord_median_en_voxels"] - 5.0) < 1e-9,
      f"{d.get('lecart_type_du_desaccord_en_voxels')} · {d.get('le_desaccord_median_en_voxels')}")
    # ⚠⚠⚠ DEUX SUITES DE MEME ECART-TYPE MAIS DE VALEURS MELANGEES : la difference des
    # ecarts-types y vaut ZERO pendant que l'ecart-type de la DIFFERENCE ne l'est pas. Sans ce cas,
    # un bris qui remplacait l'un par l'autre restait vert — la fixture etait complaisante.
    melange = {c: float(9 - c) for c in range(10)}
    dm = le_desaccord(trois, melange, les_coutures_communes(trois, melange))
    v("★★★★ le désaccord est l'écart-type de la DIFFÉRENCE, pas la différence des écarts-types",
      dm["decidable"]
      and dm.get("la_dispersion_de_la_premiere_en_voxels") is not None
      and dm.get("la_dispersion_de_la_seconde_en_voxels") is not None
      and abs(float(dm["la_dispersion_de_la_premiere_en_voxels"])
              - float(dm["la_dispersion_de_la_seconde_en_voxels"])) < 1e-9
      and dm["lecart_type_du_desaccord_en_voxels"] > 1.0,
      f"{dm.get('lecart_type_du_desaccord_en_voxels')} pour des dispersions égales")
    disp_lue = d.get("la_dispersion_de_la_premiere_en_voxels")
    v("★★★★ la dispersion de CHAQUE rangée est publiée à côté — la dette de `203`",
      disp_lue is not None
      and abs(float(disp_lue)
              - round(float(np.std([float(c) for c in range(10)])), 4)) < 1e-9
      and d["la_dispersion_de_la_seconde_en_voxels"] == disp_lue,
      str(disp_lue))
    v("★★★ moins de trois coutures communes ne rendent AUCUN désaccord",
      not le_desaccord(une, deux, [4, 7])["decidable"])

    # ⚠⚠ LA LECTURE COMPARE A DEUX NOMBRES POSES, SANS AUCUN SEUIL.
    proche = ce_que_le_desaccord_dit(
        {"decidable": True, "lecart_type_du_desaccord_en_voxels": 1.5}, p)
    v("★★★★ un désaccord petit est rangé du côté « même pas », sans seuil",
      proche["decidable"] and proche["de_laquelle_il_est_le_plus_proche"] == "le même pas",
      str(proche.get("le_rapport_a_la_lecture_meme_pas")))
    loin = ce_que_le_desaccord_dit(
        {"decidable": True, "lecart_type_du_desaccord_en_voxels": 3.4}, p)
    v("★★★★ un désaccord grand est rangé du côté « autre chose »",
      loin["de_laquelle_il_est_le_plus_proche"] == "autre chose")
    v("★★★ la fonction dit s'il tombe ENTRE les deux plutôt que de le ranger de force",
      proche["il_tombe_entre_les_deux"] is True
      and ce_que_le_desaccord_dit(
          {"decidable": True, "lecart_type_du_desaccord_en_voxels": 99.0},
          p)["il_tombe_entre_les_deux"] is False)
    v("★★★ une prédiction indécidable ne rend AUCUNE lecture",
      not ce_que_le_desaccord_dit({"decidable": True,
                                   "lecart_type_du_desaccord_en_voxels": 1.0},
                                  {"decidable": False})["decidable"])

    # ⚠⚠⚠ L'EPREUVE EST CELLE DE `202`, IMPORTEE ET NON REECRITE.
    memes, autres = deux_rangees_fabriquees(240, True, 2.233, 1.029, 21)
    com = les_coutures_communes(memes, autres)
    ep = lappariement([memes[c] for c in com], [autres[c] for c in com],
                      PERMUTATIONS, 5, GARANTIE_PAR_EPREUVE)
    v("★★★★ deux rangées qui partagent leur dérive sont VUES appariées",
      ep["decidable"] and ep["les_deux_pas_sont_apparies"]
      and ep["les_melanges_au_moins_aussi_forts"] == 0,
      str(ep.get("la_correlation_absolue")))
    sans_un, sans_deux = deux_rangees_fabriquees(240, False, 2.233, 1.029, 22)
    com2 = les_coutures_communes(sans_un, sans_deux)
    ep2 = lappariement([sans_un[c] for c in com2], [sans_deux[c] for c in com2],
                       PERMUTATIONS, 6, GARANTIE_PAR_EPREUVE)
    v("★★★★ deux rangées qui ne partagent rien ne sont PAS appariées",
      not ep2["les_deux_pas_sont_apparies"], str(ep2.get("la_valeur_p")))
    v("★★★★ la fixture ne change QUE le partage : même dérive, même aléa des deux côtés",
      abs(float(np.std([memes[c] for c in com]))
          - float(np.std([sans_un[c] for c in com2]))) < 0.5,
      f"{round(float(np.std([memes[c] for c in com])), 4)} contre "
      f"{round(float(np.std([sans_un[c] for c in com2])), 4)}")

    # ⭐⭐⭐⭐ LA DECOMPOSITION DE `202`, IMPORTEE, CHIFFRE CE QUE LES DEUX RANGEES PARTAGENT.
    part = ce_que_les_deux_rangees_partagent([memes[c] for c in com],
                                             [autres[c] for c in com])
    v("★★★★ deux rangées qui partagent leur dérive rendent une dérive commune POSITIVE",
      part["decidable"] and float(part["la_derive_partagee_en_voxels"]) > 1.0,
      str(part.get("la_derive_partagee_en_voxels")))
    v("★★★★ et le bruit propre de chaque rangée est publié à côté",
      part["le_bruit_de_la_premiere_en_voxels"] is not None
      and part["le_bruit_de_la_seconde_en_voxels"] is not None)
    sans_part = ce_que_les_deux_rangees_partagent([sans_un[c] for c in com2],
                                                  [sans_deux[c] for c in com2])
    v("★★★★ deux rangées sans rapport laissent le modèle se réfuter par ses propres nombres, ou "
      "rendre une dérive commune bien plus petite",
      (not sans_part.get("decidable"))
      or float(sans_part["la_derive_partagee_en_voxels"])
      < float(part["la_derive_partagee_en_voxels"]),
      str(sans_part.get("la_derive_partagee_en_voxels") or sans_part.get("raison")))
    v("★★★ moins de trois coutures ne rendent AUCUN partage",
      not ce_que_les_deux_rangees_partagent([1.0, 2.0], [3.0, 4.0])["decidable"])
    # ⭐⭐⭐⭐ CE QUE LA BOUCLE RAPPORTE SE LIT CONTRE CE QUE LA RANGEE SEULE DONNE, jamais seul.
    seule = lexcursion_predite(2.4587, 242)
    boucle = lexcursion_predite(1.5129, 242)
    v("★★★★ une dérive partagée plus petite donne une excursion plus petite, en racine du compte",
      boucle["lecart_attendu_en_voxels"] < seule["lecart_attendu_en_voxels"]
      and abs(boucle["lecart_attendu_en_voxels"] / seule["lecart_attendu_en_voxels"]
              - 1.5129 / 2.4587) < 1e-3,
      f"{boucle['lecart_attendu_en_voxels']} contre {seule['lecart_attendu_en_voxels']}")
    v("★★★ la projection est celle de `207`, importée et non réécrite",
      abs(seule["lecart_attendu_en_voxels"] - round(2.4587 * (242 ** 0.5), 4)) < 1e-9)

    # ⚠⚠ LE VERDICT NE TIENT QU'A L'EPREUVE DECLAREE, LA SECONDE VOISINE EST UN CONTROLE.
    jug = juger({197: d, 199: d}, {197: ep, 199: ep2}, proche, p, 198,
                {197: part, 199: part})
    v("★★★★ le verdict porte la PREMIÈRE voisine et range la seconde en contrôle",
      jug["decidable"] and jug["la_voisine_de_lepreuve"] == 197
      and jug["les_voisines_en_controle"] == [199]
      and len(jug["les_correlations_des_controles"]) == 1,
      f"{jug.get('la_voisine_de_lepreuve')} · {jug.get('les_voisines_en_controle')}")
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger({197: d}, {197: {"decidable": False}}, proche, p, 198, {})["decidable"])
    v("★★★ une lecture indécidable ne rend AUCUN verdict",
      not juger({197: d}, {197: ep}, {"decidable": False}, p, 198, {})["decidable"])

    # ⭐ L'ETALON, EN PETIT.
    et = sur_letalon(240, 2.233, 1.029, GRAINE, replicats=3, tirages=PERMUTATIONS)
    v("★★★★ l'étalon voit deux rangées qui partagent leur dérive",
      et["la_part_trouvee"] >= 0.99, str(et.get("la_part_trouvee")))
    v("★★★★ la face négative a DEUX fois le compte que la garantie exige — la leçon de `202`",
      et["les_replicats_du_refus"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ sur deux rangées sans rapport, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)
    v("★★★★ l'écart est publié sur les DEUX faces, et la partagée est la plus SERRÉE",
      et["lecart_median_sur_la_face_positive_en_voxels"]
      < et["lecart_median_sur_la_face_negative_en_voxels"],
      f"{et.get('lecart_median_sur_la_face_positive_en_voxels')} contre "
      f"{et.get('lecart_median_sur_la_face_negative_en_voxels')}")
    # ⚠⚠ L'ETALON EST APPELE SANS ARGUMENT ICI, SINON SES DEFAUTS NE SONT EXERCES PAR RIEN : un
    # bris qui changeait la derive par defaut restait vert tant que chaque sonde la passait.
    par_defaut = sur_letalon(24, replicats=1, tirages=3)
    v("★★★★ la dérive et l'aléa PAR DÉFAUT de l'étalon sont ceux que `204` a mesurés",
      par_defaut["la_derive_posee_en_voxels"]
      == la_dispersion_de_204()["la_derive_en_voxels"]
      and par_defaut["lalea_pose_en_voxels"] == la_dispersion_de_204()["lalea_en_voxels"],
      f"{par_defaut.get('la_derive_posee_en_voxels')} · "
      f"{par_defaut.get('lalea_pose_en_voxels')}")

    # ⚠⚠ LA LIGNE DE `204` LIT LA RANGEE QU'ON LUI DEMANDE, ET REFUSE HORS DU TREILLIS.
    meta = {"chunks": [109, 12, 12], "shape": [109, 36, 40]}
    # ⚠ LE BLOC PORTE UNE TEXTURE DANS LE PLAN, sinon le filtre du producteur l'écarte et la
    # sonde mesure ce filtre au lieu de la rangée demandée.
    bloc = _rng(31).normal(0.5, 0.2, size=(109, 12, 12)).astype(np.float32)

    def _depot(cy, cx):
        """Un dépôt qui REFUSE une rangée qui n'existe pas — comme le vrai le ferait.

        ⚠⚠ Un faux dépôt qui rend un chunk pour n'importe quelle rangée rend la sonde aveugle :
        un bris qui retirait le garde de bornes restait alors vert.
        """
        return ((bloc, None) if 0 <= int(cy) < 3 else (None, "absent du dépôt"))

    lg = la_ligne({"cle": "x", "segment": "s"}, 0.0, None, _depot, meta, 4, 0)
    v("★★★ une rangée du treillis demandée est bien celle qui est lue",
      lg.get("la_rangee") == 0 and lg.get("decidable"), str(lg.get("la_rangee")))
    # ⚠⚠ LA SONDE ASSERTE LA RAISON, PAS SEULEMENT LE REFUS : sans le garde de bornes, la ligne
    # refuse AUSSI — mais parce qu'elle n'a rien lu, ce qui est un tout autre fait. Un bris posé
    # sur le garde restait vert tant que la sonde se contentait de « ça refuse ».
    hors = la_ligne({"cle": "x", "segment": "s"}, 0.0, None, _depot, meta, 4, 99)
    v("★★★★ une rangée hors du treillis est REFUSÉE POUR CETTE RAISON, jamais faute de chunks",
      not hors["decidable"] and "hors du treillis" in str(hors.get("raison")),
      str(hors.get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--colonnes", type=int, default=None)
    ap.add_argument("--graine", type=int, default=GRAINE)
    ap.add_argument("--replicats", type=int, default=12)
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.graine, a.replicats, a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
