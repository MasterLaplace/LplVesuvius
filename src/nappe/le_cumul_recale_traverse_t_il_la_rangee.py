"""Le cumul recalé sur seize rangées traverse-t-il la rangée sans perdre un demi-feuillet ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET IL NE VIENT PAS D'UNE PORTE NOUVELLE. La chaîne `201`–`206` a passé
quatre tranches à diagnostiquer le CREUX, et les quatre disent la même chose autrement : son erreur
porte une composante de chunk d'environ quinze voxels que rien n'atteint. C'est utile pour ne pas y
revenir à l'aveugle, et ça n'avance pas d'un pas vers le déroulage.

⭐⭐⭐⭐ LE SEUL RÉSULTAT POSITIF DE LA CHAÎNE EST `204`, ET IL N'A JAMAIS ÉTÉ MIS À L'ÉPREUVE DE CE
QU'ON LUI DEMANDE. Moyenner seize rangées met le signal devant le bruit et rend le pas MESURABLE ;
`204` le dit lui-même, sa portée est celle d'une marche au hasard, pas d'un correcteur. La question
qui sert l'objectif est donc celle-ci, et elle se tranche sur la rangée déjà lue : le cumul de ces
pas-là traverse-t-il la rangée sans jamais s'éloigner d'un demi-feuillet de son départ ?

⭐⭐⭐⭐ LA PRÉDICTION SE POSE AVANT LA MESURE, ET ELLE N'A QU'UNE PIÈCE. `204` publie la dispersion
du pas à seize rangées ; une marche de `n` pas indépendants de cette dispersion s'éloigne de son
départ d'environ cette dispersion fois la racine de `n`. Ce nombre-là se calcule avant qu'un seul
chunk ne soit lu, et il se compare au demi-pli — la distance à laquelle la surface saute au feuillet
voisin, qui est une constante de la chaîne et non un seuil choisi.

⚠⚠ ET LE TROU DANS LA RANGÉE EST UNE CONTRAINTE, PAS UN DÉTAIL : un cumul ne se construit que sur
des chunks CONTIGUS, parce que deux chunks séparés par un trou n'ont pas de couture commune. Les
tronçons sont donc publiés, et le verdict porte sur le plus long — c'est la règle que `199` avait
déjà écrite.

Usage :
    uv run python src/nappe/le_cumul_recale_traverse_t_il_la_rangee.py --verifier
    uv run python src/nappe/le_cumul_recale_traverse_t_il_la_rangee.py \\
        --json docs/mesures/le_cumul_recale_traverse_t_il_la_rangee.json
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
from la_derive_saccumule_t_elle import (contre_les_signes,  # noqa: E402
                                        les_troncons)
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from moyenner_le_creux_reduit_il_son_bruit import ce_que_les_rangees_ont_rendu  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from peut_on_deplier_la_phase import ce_que_la_marche_a_rendu  # noqa: E402
from que_montrent_ces_deux_vues import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                        PAS_EN_VOXELS)

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LES_RANGEES_ONT_RENDU = MESURES / "combien_de_rangees_faut_il_pour_lire_le_pas.json"
GRAINE = 20261015
LES_RANGEES = 16

LA_QUESTION_DECLAREE = ("le cumul des pas lus sur seize rangées traverse-t-il la rangée sans "
                        "jamais s'éloigner d'un demi-feuillet de son départ ?")
LES_EPREUVES_DECLAREES = ("les pas lus sur seize rangées s'additionnent-ils, ou se "
                          "compensent-ils",)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)


def la_dispersion_de_204(chemin: Path = CE_QUE_LES_RANGEES_ONT_RENDU) -> dict:
    """La dispersion du pas à seize rangées, telle que `204` l'a publiée — relue, jamais refaite.

    ⚠⚠⚠ C'EST LA SEULE PIECE DE LA PREDICTION, donc elle vient de son producteur. `204` publie
    l'alea ET la dispersion ; c'est la DISPERSION qu'une marche accumule, parce qu'elle porte a la
    fois ce que la surface fait et ce que le lecteur se trompe — et un cumul ne sait pas les
    separer.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `204` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    v = d.get("le_verdict") or {}
    if not v.get("decidable") or v.get("la_dispersion_au_maximum_en_voxels") is None:
        return {"decidable": False, "raison": "`204` ne publie pas de dispersion du pas"}
    return {"decidable": True,
            "la_dispersion_en_voxels": v.get("la_dispersion_au_maximum_en_voxels"),
            "lalea_en_voxels": v.get("lalea_au_maximum_en_voxels"),
            "la_derive_en_voxels": v.get("la_derive_au_maximum_en_voxels"),
            "les_rangees": v.get("les_rangees_de_lepreuve")}


def le_cumul(pas) -> np.ndarray:
    """La position cumulée, départ à zéro : `n` pas donnent `n+1` positions."""
    p = np.asarray(pas, dtype=float)
    return np.concatenate(([0.0], np.cumsum(p)))


def lexcursion(cumul, periode: float = PAS_EN_VOXELS) -> dict:
    """Jusqu'où la marche s'éloigne de son départ — l'AMPLITUDE, pas le point d'arrivée.

    ⭐⭐⭐⭐ C'EST L'EXCURSION QUI COUTE UN FEUILLET, PAS LE DEPLACEMENT NET. Une marche qui part a
    quarante voxels et revient a zero a deja saute de feuillet en chemin, et son deplacement net
    vaut zero : le juger sur l'arrivee dirait qu'elle n'a rien fait. `199` mesurait le deplacement
    NET — c'est une autre question, et c'est pourquoi celle-ci ne la refait pas.
    """
    c = np.asarray(cumul, dtype=float)
    if c.size < 2:
        return {"decidable": False, "raison": "moins de deux positions"}
    ec = float(c.max() - c.min())
    return {"decidable": True, "les_positions": int(c.size),
            "lexcursion_en_voxels": round(ec, 4),
            "lexcursion_en_plis": round(ec / float(periode), 6),
            "le_deplacement_net_en_voxels": round(float(c[-1] - c[0]), 4),
            "le_plus_loin_en_voxels": round(float(np.abs(c).max()), 4)}


def lexcursion_predite(dispersion, coutures: int, periode: float = PAS_EN_VOXELS,
                       demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Ce qu'une marche de pas INDÉPENDANTS de cette dispersion donnerait — posé avant la mesure.

    ⭐⭐⭐⭐ UNE SEULE PIECE, ET ELLE VIENT DE `204` : l'ecart-type d'une somme de `n` tirages
    independants de meme dispersion vaut cette dispersion fois la racine de `n`. Aucun reglage
    n'entre la-dedans, et le nombre se calcule avant qu'un seul chunk ne soit lu.

    ⚠⚠ ELLE SE COMPARE AU DEMI-PLI, QUI N'EST PAS UN SEUIL CHOISI : c'est la distance a laquelle la
    surface saute au feuillet voisin, et c'est une constante publiee de la chaine.
    """
    if dispersion is None or int(coutures) < 1:
        return {"decidable": False, "raison": "la dispersion de `204` ou les coutures manquent"}
    att = float(dispersion) * (float(coutures) ** 0.5)
    return {"decidable": True,
            "la_dispersion_de_204_en_voxels": round(float(dispersion), 4),
            "les_coutures": int(coutures),
            "lecart_attendu_en_voxels": round(att, 4),
            "lecart_attendu_en_plis": round(att / float(periode), 6),
            "le_demi_pli_en_voxels": int(demi),
            "il_tient_sous_le_demi_pli": bool(att < float(demi))}


def juger(excursion: dict, prediction: dict, epreuve: dict, par_199: dict,
          demi: float = DEMI_PAS_EN_VOXELS, periode: float = PAS_EN_VOXELS) -> dict:
    """Le cumul traverse-t-il la rangée sans perdre un demi-feuillet ?

    ⚠⚠ L'EPREUVE EST PORTEE EN PREMIER PARCE QU'ELLE GARDE LA PREDICTION : si les pas sont
    correles, « dispersion fois racine de n » ne vaut plus, et l'ecart entre l'observe et l'attendu
    ne se lit plus comme un ecart a l'independance.
    """
    if not excursion.get("decidable") or not epreuve.get("decidable"):
        return {"decidable": False, "raison": "l'excursion ou l'épreuve manque"}
    ec = float(excursion["lexcursion_en_voxels"])
    att = prediction.get("lecart_attendu_en_voxels")
    return {"decidable": True,
            "les_positions": excursion["les_positions"],
            "lexcursion_en_voxels": excursion["lexcursion_en_voxels"],
            "lexcursion_en_plis": excursion["lexcursion_en_plis"],
            "le_deplacement_net_en_voxels": excursion["le_deplacement_net_en_voxels"],
            "le_demi_pli_en_voxels": int(demi),
            "elle_traverse_sous_le_demi_pli": bool(ec < float(demi)),
            "lexcursion_en_demi_plis": round(ec / float(demi), 4),
            "lecart_attendu_en_voxels": att,
            "le_rapport_observe_sur_attendu": (round(ec / float(att), 4)
                                               if att else None),
            "ca_saccumule": bool(epreuve["ca_saccumule"]),
            "les_tirages_au_moins_aussi_loin": epreuve["les_tirages_au_moins_aussi_loin"],
            "combien_de_marches_au_hasard": epreuve["combien_de_marches_au_hasard"],
            "lexcursion_de_199_en_plis": par_199.get("lexcursion_en_plis"),
            "le_rapport_a_199": (
                round(float(excursion["lexcursion_en_plis"])
                      / float(par_199["lexcursion_en_plis"]), 4)
                if par_199.get("lexcursion_en_plis") else None)}


def des_pas_fabriques(coutures: int, biais: float, dispersion: float,
                      graine: int) -> np.ndarray:
    """Des pas de dispersion posée, avec ou sans BIAIS systématique.

    ⭐⭐⭐⭐ LE BIAIS EST CE QUE LE NUL PAR SIGNES PEUT VOIR, et rien d'autre : tirer les signes
    garde les tailles et remplace la marche par une marche au hasard, donc seule une composante qui
    va toujours dans le MEME sens fait dépasser l'observé. Une fixture qui grossirait la dispersion
    sans biais ne testerait rien.

    ⚠ La dispersion est tenue constante quel que soit le biais, sinon la face positive serait plus
    facile pour la mauvaise raison.
    """
    r = _rng(int(graine))
    bruit = r.normal(0.0, 1.0, size=int(coutures))
    ecart = float(np.std(bruit))
    if ecart > 0.0:
        bruit = bruit * (float(dispersion) / ecart)
    return bruit + float(biais)


def sur_letalon(coutures: int = 244, dispersion: float = 2.4587, biais: float | None = None,
                graine: int = GRAINE, replicats: int = 12,
                tirages: int = PERMUTATIONS, lecteur=None) -> dict:
    """L'épreuve voit-elle un biais posé, et se tait-elle quand il n'y en a aucun ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS, ET LA FACE NEGATIVE EN A DAVANTAGE — la lecon de `202`.
    ⚠⚠ ET LA FACE NEGATIVE PORTE LA MEME DISPERSION QUE LA POSITIVE : c'est le refus difficile, et
    le seul qui mesure quelque chose.

    ⚠⚠⚠ UNE PREMIERE VERSION DE CETTE TRANCHE DECLARAIT UNE AUTRE EPREUVE — l'excursion contre ses
    propres pas remis dans un autre ordre — et l'etalon l'a REFUSEE : cette statistique-la ne voit
    une correlation forte que dans dix replicats sur douze, parce que l'excursion d'une seule
    realisation est tres variable. L'epreuve declaree est donc celle que `199` avait deja ecrite,
    posee sur le pas que `204` rend enfin mesurable — et c'est aussi ce qui rend les deux reponses
    directement comparables.
    """
    # ⚠⚠⚠ LE BIAIS N'EST PAS CHOISI ICI : c'est celui que l'etalon de `199` avait pose, relu chez
    # son producteur. Cette tranche reprend l'EPREUVE de `199`, donc elle en reprend aussi la
    # matiere de calibration — sinon « l'etalon separe » voudrait dire autre chose des deux cotes.
    # ⚠ Une premiere version en posait un plus petit, et sa face positive n'atteignait que deux
    # replicats sur trois : le rapport du net au nul y valait environ trois, et une seule
    # realisation de bruit malheureuse suffit alors a l'annuler.
    if biais is None:
        lu = (lecteur or ce_que_la_marche_a_rendu)()
        biais = (lu or {}).get("le_biais_de_letalon_en_voxels")
    if biais is None:
        return {"decidable": False,
                "raison": "`199` ne publie pas le biais de son étalon"}
    vus, nets = 0, []
    for i in range(int(replicats)):
        pas = des_pas_fabriques(coutures, biais, dispersion, int(graine) + 1000 * i)
        ep = contre_les_signes(pas, tirages, int(graine) + i)
        vus += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            nets.append(float(ep["le_deplacement_net_en_voxels"]))
    replicats_du_refus = int(2.0 / float(GARANTIE_PAR_EPREUVE))
    faux, sans = 0, []
    for i in range(replicats_du_refus):
        pas = des_pas_fabriques(coutures, 0.0, dispersion, int(graine) + 500000 + 1000 * i)
        ep = contre_les_signes(pas, tirages, int(graine) + 77 + i)
        faux += int(bool(ep.get("ca_saccumule")))
        if ep.get("decidable"):
            sans.append(float(ep["le_deplacement_net_en_voxels"]))
    return {"decidable": True,
            "les_coutures_par_replicat": int(coutures),
            "la_dispersion_posee_en_voxels": float(dispersion),
            "le_biais_pose_en_voxels": float(biais),
            "replicats": int(replicats), "les_vus": int(vus),
            "la_part_trouvee": round(float(vus) / float(replicats), 4),
            "le_net_median_sur_la_face_positive_en_voxels": (
                round(float(np.median(nets)), 4) if nets else None),
            "les_replicats_du_refus": int(replicats_du_refus), "les_faux": int(faux),
            "le_taux_de_faux": round(float(faux) / float(replicats_du_refus), 4),
            "le_net_median_sur_la_face_negative_en_voxels": (
                round(float(np.median(sans)), 4) if sans else None),
            "la_garantie": round(float(GARANTIE_PAR_EPREUVE), 4),
            "letalon_separe": bool(vus >= replicats
                                   and faux / float(replicats_du_refus)
                                   <= float(GARANTIE_PAR_EPREUVE) * 2.0 + 1e-12)}


def mesurer(delai: float = DELAI, graine: int = GRAINE, replicats: int = 12,
            colonnes: int | None = None, ouvrir=None, meta=None,
            combien: int = LES_RANGEES) -> dict:
    """La prédiction posée, le cumul sur le plus long tronçon, l'épreuve et l'étalon."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, ouvrir, meta, combien)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celles de `199` à `206`",
                "la_ligne": {k: x for k, x in lg.items()
                             if k not in ("droits", "gauches", "les_colonnes")}}
    droits, gauches = lg["droits"], lg["gauches"]
    rangees = lg["les_rangees_lues"]
    troncons = les_troncons(droits, lg["les_colonnes"])
    le_plus_long = max(troncons, key=len) if troncons else []
    pas, colonnes_des_pas = [], []
    for a, b in zip(le_plus_long, le_plus_long[1:]):
        lu = le_pas_de_k_rangees(droits[a], gauches[b], rangees)
        if not lu.get("decidable"):
            continue
        pas.append(float(lu["le_pas_en_voxels"]))
        colonnes_des_pas.append([int(a), int(b)])
    cumul = le_cumul(pas)
    par_204 = la_dispersion_de_204()
    prediction = lexcursion_predite(par_204.get("la_dispersion_en_voxels"), len(pas))
    # ⚠⚠⚠ LA MEME PREDICTION A LA LONGUEUR DE LA RANGEE ENTIERE, PARCE QUE LE PLUS LONG TRONCON
    # N'EST PAS LA RANGEE. Le filtre du producteur ecarte quelques chunks, et chacun COUPE la
    # rangee : le cumul ne traverse donc qu'un troncon. Publier la seule prediction du troncon
    # laisserait croire que le verdict porte sur la rangee — un nombre juste sous un mauvais nom.
    coutures_de_la_rangee = sum(max(0, len(x) - 1) for x in troncons)
    prediction_a_la_rangee = lexcursion_predite(par_204.get("la_dispersion_en_voxels"),
                                                coutures_de_la_rangee)
    # ⭐⭐⭐⭐ ET LE PLANCHER QUE LA MATIERE IMPOSE, AVEC LA DERIVE SEULE : `204` separe la
    # dispersion du pas en un alea de lecture et une derive VRAIE. Un lecteur parfait ferait tomber
    # l'alea a zero et laisserait la derive, donc cette prediction-la est la meilleure qu'un
    # instrument PUISSE atteindre sur cette matiere. Sans elle, « il faudrait mieux lire » resterait
    # une phrase au lieu d'un nombre.
    prediction_au_meilleur_lecteur = lexcursion_predite(par_204.get("la_derive_en_voxels"),
                                                        coutures_de_la_rangee)
    excursion = lexcursion(cumul)
    epreuve = contre_les_signes(pas, PERMUTATIONS, graine)
    par_199 = ce_que_la_marche_a_rendu()
    return {
        "graine": int(graine), "tirages": int(PERMUTATIONS),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
        "la_garantie_par_epreuve": round(float(GARANTIE_PAR_EPREUVE), 7),
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "la_ligne": {k: x for k, x in lg.items()
                     if k not in ("droits", "gauches", "les_colonnes")},
        "les_troncons": [[int(t[0]), int(t[-1]), len(t)] for t in troncons],
        "le_plus_long_troncon": [int(le_plus_long[0]), int(le_plus_long[-1]),
                                 len(le_plus_long)] if le_plus_long else None,
        "les_pas_du_cumul": len(pas),
        "les_colonnes_des_pas": colonnes_des_pas,
        # ⭐⭐⭐⭐ LA TRACE ELLE-MEME EST PUBLIEE, PAS SEULEMENT SON AMPLITUDE : c'est la seule
        # chose qu'un oeil peut juger, et une figure qui la redessinerait depuis un resume
        # dessinerait autre chose que ce qui a ete mesure.
        "les_pas_en_voxels": [round(float(x), 4) for x in pas],
        "le_cumul_en_voxels": [round(float(x), 4) for x in cumul],
        "ce_que_204_a_rendu": par_204,
        "ce_que_199_a_rendu": par_199,
        "les_coutures_de_tous_les_troncons": int(coutures_de_la_rangee),
        "la_prediction": prediction,
        "la_prediction_a_la_rangee": prediction_a_la_rangee,
        "la_prediction_au_meilleur_lecteur": prediction_au_meilleur_lecteur,
        "lexcursion": excursion,
        "lepreuve": epreuve,
        "le_verdict": juger(excursion, prediction, epreuve, par_199),
        "letalon": sur_letalon(max(3, len(pas)),
                               par_204.get("la_dispersion_en_voxels") or 2.4587,
                               None, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True) and "raison" in r:
        print(f"INDÉCIDABLE : {r['raison']}")
        return
    lg = r.get("la_ligne") or {}
    print(f"LE CUMUL RECALÉ TRAVERSE-T-IL LA RANGÉE   segment {lg.get('segment')} · "
          f"rangée {lg.get('la_rangee')} · {lg.get('colonnes_lues')} chunks lus sur "
          f"{lg.get('colonnes_demandees')} · {len(lg.get('les_rangees_lues') or [])} rangées")
    t = r.get("le_plus_long_troncon")
    print(f"  LES TRONÇONS      {len(r.get('les_troncons') or [])} · le plus long "
          f"{t} · {r.get('les_pas_du_cumul')} pas")
    p = r.get("la_prediction") or {}
    if p.get("decidable"):
        print(f"  LA PRÉDICTION     dispersion {p['la_dispersion_de_204_en_voxels']} × racine de "
              f"{p['les_coutures']} = {p['lecart_attendu_en_voxels']} voxels = "
              f"{p['lecart_attendu_en_plis']} pli · sous le demi-pli "
              f"{p['il_tient_sous_le_demi_pli']}")
    pr = r.get("la_prediction_a_la_rangee") or {}
    if pr.get("decidable"):
        print(f"  À LA RANGÉE       {pr['les_coutures']} coutures en tout → "
              f"{pr['lecart_attendu_en_voxels']} voxels = {pr['lecart_attendu_en_plis']} pli · "
              f"sous le demi-pli {pr['il_tient_sous_le_demi_pli']}")
    pm = r.get("la_prediction_au_meilleur_lecteur") or {}
    if pm.get("decidable"):
        print(f"  LE PLANCHER       dérive seule {pm['la_dispersion_de_204_en_voxels']} × racine "
              f"de {pm['les_coutures']} = {pm['lecart_attendu_en_voxels']} voxels = "
              f"{pm['lecart_attendu_en_plis']} pli · sous le demi-pli "
              f"{pm['il_tient_sous_le_demi_pli']}")
    e = r.get("lexcursion") or {}
    if e.get("decidable"):
        print(f"  L'EXCURSION       {e['lexcursion_en_voxels']} voxels = "
              f"{e['lexcursion_en_plis']} pli · déplacement net "
              f"{e['le_deplacement_net_en_voxels']} · le plus loin "
              f"{e['le_plus_loin_en_voxels']}")
    ep = r.get("lepreuve") or {}
    if ep.get("decidable"):
        print(f"  L'ÉPREUVE         déplacement net {ep['le_deplacement_net_en_voxels']} contre "
              f"{ep['le_deplacement_du_nul_median_en_voxels']} au nul · "
              f"{ep['les_tirages_au_moins_aussi_loin']}/{ep['tirages']} · "
              f"{ep['combien_de_marches_au_hasard']} marche au hasard · ça s'accumule "
              f"{ep['ca_saccumule']}")
    ve = r.get("le_verdict") or {}
    if ve.get("decidable"):
        print(f"  LE VERDICT        traverse sous le demi-pli "
              f"{ve['elle_traverse_sous_le_demi_pli']} · "
              f"{ve['lexcursion_en_demi_plis']} demi-pli · observé sur attendu "
              f"{ve['le_rapport_observe_sur_attendu']}")
        print(f"                    `199` en donnait {ve['lexcursion_de_199_en_plis']} pli · "
              f"rapport {ve['le_rapport_a_199']}")
    et = r.get("letalon") or {}
    if et.get("decidable"):
        print(f"  L'ÉTALON          sépare {et['letalon_separe']} · trouve "
              f"{et['la_part_trouvee']} des {et['replicats']} réplicats (net "
              f"{et['le_net_median_sur_la_face_positive_en_voxels']}) · {et['les_faux']} "
              f"faux sur {et['les_replicats_du_refus']} = {et['le_taux_de_faux']} pour "
              f"{et['la_garantie']} garantis (net "
              f"{et['le_net_median_sur_la_face_negative_en_voxels']})")


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

    # ⚠⚠⚠ UN CUMUL NE SE CONSTRUIT QUE SUR DES CHUNKS CONTIGUS, ET LE DECOUPAGE EST CELUI DE `199`,
    # IMPORTE ET NON REECRIT : une seconde ecriture finirait par ne plus s'accorder sur ce qu'est un
    # voisin, et c'est exactement la duplication que cette tranche existe pour ne pas faire.
    toutes = list(range(10))
    v("★★★★ un trou coupe le tronçon, il ne se recolle pas",
      les_troncons({0: 1, 1: 1, 2: 1, 5: 1, 6: 1, 9: 1}, toutes) == [[0, 1, 2], [5, 6]],
      str(les_troncons({0: 1, 1: 1, 2: 1, 5: 1, 6: 1, 9: 1}, toutes)))
    v("★★★★ un chunk ISOLÉ ne fait pas de tronçon : il ne porte aucune couture",
      les_troncons({9: 1}, toutes) == [])
    v("★★★ une rangée sans trou ne fait qu'un tronçon",
      les_troncons({3: 1, 4: 1, 5: 1, 6: 1}, toutes) == [[3, 4, 5, 6]])
    v("★★★ une rangée vide ne fait aucun tronçon", les_troncons({}, toutes) == [])

    # ⚠⚠ LE CUMUL PART DE ZERO ET REND UNE POSITION DE PLUS QUE DE PAS.
    c = le_cumul([1.0, -2.0, 3.0])
    v("★★★★ n pas rendent n+1 positions, la première à zéro",
      c.size == 4 and abs(c[0]) < 1e-12 and abs(c[-1] - 2.0) < 1e-12, str(list(c)))

    # ⭐⭐⭐⭐ L'EXCURSION EST L'AMPLITUDE, PAS L'ARRIVEE.
    ec = lexcursion(le_cumul([10.0, -10.0]))
    v("★★★★ une marche qui part loin et revient a une excursion NON NULLE",
      ec["decidable"] and abs(ec["lexcursion_en_voxels"] - 10.0) < 1e-9
      and abs(ec["le_deplacement_net_en_voxels"]) < 1e-9,
      f"{ec.get('lexcursion_en_voxels')} pour un net de "
      f"{ec.get('le_deplacement_net_en_voxels')}")
    v("★★★ l'excursion est aussi rendue en plis, par la période de la chaîne",
      abs(ec["lexcursion_en_plis"] - round(10.0 / PAS_EN_VOXELS, 6)) < 1e-9)
    v("★★★ moins de deux positions ne rendent AUCUNE excursion",
      not lexcursion([0.0])["decidable"])

    # ⭐⭐⭐⭐ LA PREDICTION N'A QU'UNE PIECE, ET ELLE VIENT DE `204`.
    pr = lexcursion_predite(2.4587, 244)
    v("★★★★ l'écart attendu est la dispersion fois la racine du nombre de coutures",
      pr["decidable"]
      and abs(pr["lecart_attendu_en_voxels"] - round(2.4587 * (244 ** 0.5), 4)) < 1e-9,
      str(pr.get("lecart_attendu_en_voxels")))
    v("★★★★ il se compare au DEMI-PLI, constante de la chaîne et non seuil choisi",
      pr["le_demi_pli_en_voxels"] == int(DEMI_PAS_EN_VOXELS)
      and pr["il_tient_sous_le_demi_pli"] is bool(
          pr["lecart_attendu_en_voxels"] < DEMI_PAS_EN_VOXELS))
    v("★★★ une dispersion assez grande fait échouer la prédiction, et elle le dit",
      lexcursion_predite(10.0, 244)["il_tient_sous_le_demi_pli"] is False)
    v("★★★★ une rangée plus longue rend la prédiction plus grande, en racine du compte",
      abs(lexcursion_predite(2.4587, 420)["lecart_attendu_en_voxels"]
          / lexcursion_predite(2.4587, 105)["lecart_attendu_en_voxels"] - 2.0) < 1e-4,
      str(lexcursion_predite(2.4587, 420)["lecart_attendu_en_voxels"]))
    # ⚠⚠ « CA REFUSE » ET « CA LEVE » SONT DEUX FACONS DE NE RIEN RENDRE, et seule la premiere
    # laisse la batterie aller jusqu'a son verdict : l'exception est attrapee et comptee en echec.
    try:
        refuse_pred = (not lexcursion_predite(None, 244)["decidable"]
                       and not lexcursion_predite(2.0, 0)["decidable"])
    except Exception as exc:  # noqa: BLE001
        refuse_pred, detail_pred = False, type(exc).__name__
    else:
        detail_pred = ""
    v("★★★★ une dispersion absente ne donne AUCUNE prédiction, et ne lève pas",
      refuse_pred, detail_pred)
    v("★★★★ la dispersion vient de `204` et de nulle part ailleurs",
      la_dispersion_de_204().get("la_dispersion_en_voxels")
      == (json.loads(CE_QUE_LES_RANGEES_ONT_RENDU.read_text(encoding="utf-8"))
          ["le_verdict"]["la_dispersion_au_maximum_en_voxels"]))
    v("★★★ `204` absent est dit, jamais remplacé",
      not la_dispersion_de_204(Path("/pas/de/fichier.json"))["decidable"])
    v("★★★★ c'est la DISPERSION qui est relue, pas l'aléa : un cumul ne sait pas les séparer",
      la_dispersion_de_204().get("la_dispersion_en_voxels")
      != la_dispersion_de_204().get("lalea_en_voxels"))
    v("★★★★ la DÉRIVE de `204` est relue aussi : elle donne le plancher qu'un lecteur parfait "
      "laisserait",
      la_dispersion_de_204().get("la_derive_en_voxels")
      == (json.loads(CE_QUE_LES_RANGEES_ONT_RENDU.read_text(encoding="utf-8"))
          ["le_verdict"]["la_derive_au_maximum_en_voxels"]))
    v("★★★★ le plancher est SOUS la prédiction complète, puisque la dérive est sous la dispersion",
      lexcursion_predite(la_dispersion_de_204()["la_derive_en_voxels"], 244)[
          "lecart_attendu_en_voxels"]
      < lexcursion_predite(la_dispersion_de_204()["la_dispersion_en_voxels"], 244)[
          "lecart_attendu_en_voxels"])

    # ⚠⚠⚠ L'EPREUVE EST CELLE DE `199`, REPRISE ET NON REECRITE, POSEE SUR LE PAS DE `204`.
    r = _rng(4)
    libres = des_pas_fabriques(244, 0.0, 2.4587, 11)
    ep_libre = contre_les_signes(libres, PERMUTATIONS, 5)
    v("★★★★ des pas sans biais ne s'accumulent PAS",
      ep_libre["decidable"] and not ep_libre["ca_saccumule"],
      f"{ep_libre.get('les_tirages_au_moins_aussi_loin')} tirages aussi loin")
    biaises = des_pas_fabriques(244, 0.5, 2.4587, 12)
    ep_biaise = contre_les_signes(biaises, PERMUTATIONS, 7)
    v("★★★★ un biais systématique est VU, et le nul par signes est le seul qui le puisse",
      ep_biaise["ca_saccumule"] and ep_biaise["les_tirages_au_moins_aussi_loin"] == 0,
      f"{ep_biaise.get('le_deplacement_net_en_voxels')} contre "
      f"{ep_biaise.get('le_deplacement_du_nul_median_en_voxels')}")
    v("★★★★ la fixture tient sa dispersion quel que soit le biais, sinon la face positive serait "
      "facile pour la mauvaise raison",
      abs(float(np.std(libres)) - float(np.std(biaises))) < 1e-9,
      f"{round(float(np.std(libres)), 4)} contre {round(float(np.std(biaises)), 4)}")
    v("★★★ une permutation serait VIDE sur cette statistique, et c'est pourquoi `199` tire les "
      "signes",
      abs(float(np.sum(libres)) - float(np.sum(_rng(3).permutation(libres)))) < 1e-9)
    v("★★★ moins de deux pas ne rendent AUCUN verdict",
      not contre_les_signes([1.0])["decidable"])

    # ⚠⚠ LE VERDICT PORTE L'EPREUVE EN PREMIER, PARCE QU'ELLE GARDE LA PREDICTION.
    # ⚠⚠ LES SONDES LISENT PAR `.get()` : un bris qui fait refuser une etape en amont doit rendre
    # la sonde ROUGE, jamais tuer la batterie avant son verdict.
    jug = juger(ec, pr, ep_libre, {"lexcursion_en_plis": 1.304046})
    v("★★★★ le verdict dit si la marche traverse SOUS le demi-pli",
      jug.get("decidable") and jug.get("elle_traverse_sous_le_demi_pli") is True
      and jug.get("lexcursion_en_demi_plis") is not None
      and abs(jug["lexcursion_en_demi_plis"] - round(10.0 / DEMI_PAS_EN_VOXELS, 4)) < 1e-9,
      str(jug.get("lexcursion_en_demi_plis")))
    v("★★★★ une excursion au-delà du demi-pli est refusée, et elle le dit",
      juger(lexcursion(le_cumul([40.0])), pr, ep_libre,
            {}).get("elle_traverse_sous_le_demi_pli") is False)
    v("★★★★ le verdict porte l'excursion de `199` telle qu'elle, et le rapport qui va avec",
      jug.get("lexcursion_de_199_en_plis") == 1.304046
      and jug.get("le_rapport_a_199") is not None
      and abs(float(jug["le_rapport_a_199"])
              - round(float(ec["lexcursion_en_plis"]) / 1.304046, 4)) < 1e-9,
      f"{jug.get('lexcursion_de_199_en_plis')} · {jug.get('le_rapport_a_199')}")
    v("★★★ une épreuve indécidable ne rend AUCUN verdict",
      not juger(ec, pr, {"decidable": False}, {})["decidable"])

    # ⭐ L'ETALON, EN PETIT.
    et = sur_letalon(244, 2.4587, None, GRAINE, replicats=3, tirages=PERMUTATIONS)
    v("★★★★ l'étalon voit un biais posé", et["la_part_trouvee"] >= 0.99,
      str(et.get("la_part_trouvee")))
    v("★★★★ le biais de l'étalon est celui de `199`, relu et jamais choisi",
      et["le_biais_pose_en_voxels"]
      == json.loads((MESURES / "la_derive_saccumule_t_elle.json").read_text(encoding="utf-8")
                    )["letalon"]["le_biais_quil_faut"],
      str(et.get("le_biais_pose_en_voxels")))
    v("★★★★ sans le biais de `199`, l'étalon se REFUSE plutôt que d'en choisir un",
      not sur_letalon(244, 2.4587, None, GRAINE, replicats=1, tirages=3,
                      lecteur=lambda: {"decidable": False})["decidable"])
    v("★★★★ la face négative a DEUX fois le compte que la garantie exige — la leçon de `202`",
      et["les_replicats_du_refus"] == int(2.0 / GARANTIE_PAR_EPREUVE))
    v("★★★★ sur des pas indépendants, le taux de faux tient la garantie",
      et["le_taux_de_faux"] <= GARANTIE_PAR_EPREUVE * 2.0 + 1e-12,
      f"{et.get('les_faux')} faux sur {et.get('les_replicats_du_refus')}")
    v("★★★ l'étalon sépare ses deux faces, et il le DIT", et["letalon_separe"] is True)
    v("★★★★ le déplacement net est publié sur les DEUX faces, et la biaisée va PLUS LOIN",
      et["le_net_median_sur_la_face_positive_en_voxels"]
      > et["le_net_median_sur_la_face_negative_en_voxels"],
      f"{et.get('le_net_median_sur_la_face_positive_en_voxels')} contre "
      f"{et.get('le_net_median_sur_la_face_negative_en_voxels')}")

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
