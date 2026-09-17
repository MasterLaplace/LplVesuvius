"""L'empilement se répète-t-il, ou est-ce la même feuille ? — la FORME de la courbe, pas son bout.

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P37` QUI LE NOMME. `188` mesure que mélanger l'ordre des
couches détruit de l'information sur au moins **175,2** µm de profondeur — mais DEUX explications
rendent ce fait entier et `188` ne les sépare pas : la **continuité d'une même feuille**, et la
**périodicité de l'empilement**, une spire ressemblant à la suivante.

⭐⭐⭐⭐ ET LA FORME DE LA MESURE EST DANS LA COURBE ELLE-MÊME. Une périodicité fait REMONTER l'excédent
au voisinage d'un multiple du pas — à une feuille d'écart, la matière se ressemble à nouveau — tandis
qu'une continuité le fait décroître PARTOUT. `188` ne pouvait pas le voir : son échelle doublait, donc
elle n'avait que deux points près du pas et s'arrêtait juste après.

⚠⚠⚠ ET LE CONTRÔLE EST ÉCRIT D'AVANCE PAR LA PORTE : une remontée doit être comparée à celle que le
MÉLANGE rend au même barreau, sinon on lirait la remontée du ruban. Le mélange n'a plus d'ordre en
profondeur, donc il ne peut pas remonter à un multiple du pas ; s'il remonte quand même, la remontée
est une propriété de la marche et non de la matière.

⚠⚠⚠ ET CE N'EST PAS UN RUBAN QU'IL FAUT ICI, C'EST UN TRANSFERT — une sonde l'a montré et c'était une
erreur de CONCEPTION, pas de code. Un ruban de montée `m` ne saute pas `m` couches : il TRAVERSE tout
ce qu'il y a entre, donc sa crête meurt dans la matière intermédiaire et le fait que les deux bouts se
ressemblent n'y change rien. Une périodicité ne peut PAS produire de bosse dans cette statistique-là.
Ce qui la produit est un TRANSFERT : on lit les départs et la direction des fibres d'une couche, et on
marche avec eux dans une couche située `m` plus loin. C'est exactement la question du pipeline — si ma
surface se trompe de `m` couches, la lecture de la fibre tient-elle encore ?

⚠⚠⚠ ET LE MÊME JEU DE DÉPARTS SERT À TOUS LES BARREAUX. Sans cela, un écart qui approche la hauteur
du bloc n'a plus que quelques profondeurs admissibles, et la FORME de la courbe mêlerait ce que la
matière porte et ce que l'échantillon a rétréci — or c'est la forme, et elle seule, que cette tranche
lit.

⚠⚠ Les trois pièges de `187` et `188` tiennent : le plafond du ruban se lit dans la MATIÈRE, le
plancher dans CHAQUE COUCHE, et le sommet se cherche avant la décroissance.

Usage :
    uv run python src/nappe/lempilement_se_repete_t_il.py --verifier
    uv run python src/nappe/lempilement_se_repete_t_il.py \\
        --json docs/mesures/lempilement_se_repete_t_il.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from fiber_orientation import orientation_profile  # noqa: E402
from jusquou_suit_on_une_fibre import DEPARTS_PAR_COUCHE  # noqa: E402
from jusquou_une_surface_peut_elle_deriver import (la_portee_en_profondeur,  # noqa: E402
                                                   les_departs_par_couche, une_pile_qui_tourne)
from langle_publie_est_il_celui_des_fibres import direction_des_fibres_deg  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import (CONTRASTE_DE_LA_FIXTURE,  # noqa: E402
                                                       PLIS_DE_LA_FIXTURE)
from la_coupe_cherchee_trouve_t_elle_la_frontiere import COUCHES_DE_LA_CAMPAGNE  # noqa: E402
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             PLANCHER_DE_COHERENCE, SEGMENTS, les_chunks,
                                             les_volumes)
from quelle_fenetre_lit_une_bascule import bloc_de_la_fixture  # noqa: E402
from suit_on_plus_loin_quand_le_voxel_est_plus_fin import le_plafond  # noqa: E402
from un_ruban_qui_saute_perd_il_sa_fibre import le_plafond_du_ruban, un_ruban  # noqa: E402
from zarr_depth import BUCKET, array_meta, chunk_key, decode, get  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_DERIVE_A_RENDU = MESURES / "jusquou_une_surface_peut_elle_deriver.json"
GRAINE = 20260929


def le_sommet_publie(chemin: Path = CE_QUE_LA_DERIVE_A_RENDU) -> int | None:
    """La montée où `188` a mesuré que l'excédent culmine — le PAS de l'échelle, relu et non tapé.

    ⭐ C'EST L'ÉCHELLE DE CORRÉLATION DE LA MATIÈRE, ET ELLE SE LIT DANS LA MESURE PRÉCÉDENTE. Un pas
    d'échelle plus grossier que cette échelle-là ne pourrait pas résoudre une bosse ; un pas plus fin
    coûterait des barreaux sans rien ajouter.
    """
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text(encoding="utf-8"))
    return (d.get("le_verdict") or {}).get("sommet_en_couches")


def le_pas_en_couches(voxel_um: float, pas_um: float) -> int:
    """Le pas entre deux feuilles, en couches, ARRONDI AU PLUS PROCHE.

    ⚠ `188` l'arrondissait vers le HAUT parce que son dernier barreau devait FRANCHIR le pas ; ici
    l'échelle le dépasse de deux sommets, et ce qu'il faut est un barreau AU pas, aussi près que la
    grille des couches le permette.
    """
    return int(round(float(pas_um) / float(voxel_um)))


def la_portee_du_chemin_publiee(chemin: Path = CE_QUE_LA_DERIVE_A_RENDU) -> float | None:
    """Ce que `188` a publié de la portée d'un CHEMIN, en micromètres — relu, jamais retapé."""
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text(encoding="utf-8"))
    return (d.get("le_verdict") or {}).get("portee_minimale_um")


def lechelle_autour_du_pas(voxel_um: float, pas_um: float, sommet: int) -> list[int]:
    """L'échelle : linéaire, au pas du SOMMET de `188`, et poussée au-delà du pas d'une feuille.

    ⭐⭐⭐⭐ LINÉAIRE ET NON DOUBLANTE, PARCE QU'ON CHERCHE UNE BOSSE ET NON UN ORDRE DE GRANDEUR.
    `188` doublait, donc elle n'avait que deux points près du pas et ne pouvait pas voir une remontée.

    ⚠⚠ ET ELLE VA AU-DELÀ DU PAS D'EXACTEMENT DEUX SOMMETS : pour lire une bosse il faut son autre
    versant, et la demi-largeur d'une bosse est l'échelle de corrélation — le sommet que `188` a
    mesuré. S'arrêter AU pas ferait d'une montée finale une bosse indiscernable d'un plateau.

    ⚠ Le pas est ARRONDI AU PLUS PROCHE et non vers le haut, contrairement à `188` : là-bas le
    dernier barreau devait FRANCHIR le pas, ici l'échelle le dépasse de deux sommets de toute façon
    et ce qu'il faut est un barreau AU pas, aussi près que la grille le permette. Le pas lui-même est
    ajouté s'il ne tombe pas sur un barreau.
    """
    pas_en_couches = le_pas_en_couches(voxel_um, pas_um)
    plafond = pas_en_couches + 2 * int(sommet)
    out = list(range(0, plafond + 1, int(sommet)))
    if out[-1] != plafond:
        out.append(int(plafond))
    if pas_en_couches not in out:
        out.append(int(pas_en_couches))
    return sorted(set(out))


def les_profondeurs_communes(coherences, montee_max: int,
                             plancher: float = PLANCHER_DE_COHERENCE) -> dict:
    """Les profondeurs de départ qui restent admissibles à TOUS les barreaux, par sens de montée.

    ⭐⭐⭐⭐ C'EST CE QUI REND UNE COURBE COMPARABLE D'UN BARREAU À L'AUTRE. Une montée qui approche la
    hauteur du bloc n'a plus que quelques profondeurs admissibles ; laisser chaque barreau prendre ce
    qu'il peut ferait varier l'échantillon le long de la courbe, et la FORME — la seule chose que
    cette tranche lit — mêlerait la matière et le rétrécissement.

    ⚠ Elles sont TEXTURÉES, la règle du producteur que toute la chaîne suit depuis `176`.
    """
    n = len(coherences)
    m = int(montee_max)
    texture = [k for k in range(n) if float(coherences[k]) > float(plancher)]
    return {1: [k for k in texture if 0 <= k + m < n],
            -1: [k for k in texture if 0 <= k - m < n]}


def _med(v):
    return round(float(statistics.median(v)), 3) if v else None


def un_barreau_de_transfert(bloc: np.ndarray, angles, ecart: int, departs_par_couche: dict,
                            plafond: int, profondeurs_par_signe: dict) -> dict:
    """Ce que la lecture d'une couche rend quand on la porte `ecart` couches plus loin.

    ⭐⭐⭐⭐ C'EST UN TRANSFERT ET NON UN CHEMIN, ET C'EST TOUTE LA DIFFÉRENCE. On prend les départs et
    la direction des fibres de la couche `k`, et on MARCHE AVEC EUX dans la couche `k ± ecart`, à
    plat. Rien n'est lu entre les deux. Un ruban, lui, traverse toute la matière intermédiaire : sa
    crête y meurt, et deux bouts qui se ressemblent n'y changent rien — c'est pourquoi un ruban ne
    peut pas voir une périodicité, et c'est une sonde qui l'a montré.

    ⚠ À écart nul, c'est la lecture de `185` sur la couche elle-même : le barreau de référence.
    ⚠⚠ L'angle reste celui de la couche SOURCE : c'est ce qu'un pipeline connaît, et si la couche
    cible porte d'autres fibres, la marche les quitte — ce qui est l'effet mesuré.
    """
    lus: list[int] = []
    for signe in (1, -1):
        e = int(signe) * int(ecart)
        departs, kk, aa = [], [], []
        for k in profondeurs_par_signe.get(int(signe), []):
            d = departs_par_couche.get(int(k))
            if not d or not (0 <= int(k) + e < bloc.shape[0]):
                continue
            ang = float(direction_des_fibres_deg(float(angles[k])))
            for x in d:
                departs.append(x)
                kk.append(float(int(k) + e))
                aa.append(ang)
        if departs:
            lus += un_ruban(bloc, departs, np.asarray(kk), np.asarray(aa), 0, plafond)
        if int(ecart) == 0:
            break
    return {"ecart": int(ecart), "lectures": len(lus), "pas_median": _med(lus)}


def la_courbe(bloc: np.ndarray, angles, coherences, montees, combien: int, plafond_max: int,
              plancher_de_coherence: float = PLANCHER_DE_COHERENCE,
              graine: int = GRAINE) -> dict:
    """La courbe de la vraie matière et celle de son mélange, sur le MÊME jeu de départs."""
    pl = le_plafond_du_ruban(bloc, angles, coherences, combien, plafond_max,
                             plancher_de_coherence)
    if not pl:
        return {"decidable": False, "raison": "aucune couche texturée"}
    profondeurs = les_profondeurs_communes(coherences, max(montees), plancher_de_coherence)
    if not profondeurs[1] and not profondeurs[-1]:
        return {"decidable": False, "raison": "aucune profondeur commune à tous les barreaux"}
    r = np.random.default_rng(int(graine))
    ordre = r.permutation(bloc.shape[0])
    melange = bloc[ordre]
    ang_m, coh_m = np.asarray(angles)[ordre], np.asarray(coherences)[ordre]
    dep = les_departs_par_couche(bloc, coherences, combien, plancher_de_coherence)
    dep_m = les_departs_par_couche(melange, coh_m, combien, plancher_de_coherence)
    prof_m = les_profondeurs_communes(coh_m, max(montees), plancher_de_coherence)
    barreaux = []
    for m in montees:
        vrai = un_barreau_de_transfert(bloc, angles, m, dep, pl, profondeurs)
        faux = un_barreau_de_transfert(melange, ang_m, m, dep_m, pl, prof_m)
        barreaux.append({
            "montee": int(m), "rubans": vrai["lectures"], "rubans_melanges": faux["lectures"],
            "pas_median": vrai["pas_median"], "pas_median_melange": faux["pas_median"],
            "excedent": (round(float(vrai["pas_median"]) - float(faux["pas_median"]), 3)
                         if vrai["pas_median"] is not None and faux["pas_median"] is not None
                         else None)})
    return {"decidable": True, "plafond_du_ruban": int(pl),
            "profondeurs_montantes": len(profondeurs[1]),
            "profondeurs_descendantes": len(profondeurs[-1]),
            "lectures_par_barreau": (barreaux[1]["rubans"] if len(barreaux) > 1 else 0),
            # ⚠ LE BARREAU ZERO COMPTE LA MOITIE DES RUBANS, ET C'EST VOULU : a montee nulle les
            # deux sens sont le MEME ruban (`188`). L'egalite porte donc sur les barreaux non nuls.
            "le_meme_jeu_a_tous_les_barreaux": bool(
                len({b["rubans"] for b in barreaux if int(b["montee"]) != 0}) == 1),
            "barreaux": barreaux}


def la_bosse_au_pas(courbe, cle: str, pas_en_couches: int, tolerance: int) -> dict:
    """La courbe REDESCEND-elle puis REMONTE-t-elle au pas ? — la forme, pas le dernier point.

    ⭐⭐⭐⭐ C'EST UNE REMONTÉE DEPUIS LE CREUX, ET NON UN MAXIMUM LOCAL. Une première version exigeait
    que la valeur au pas dépasse STRICTEMENT ses deux voisins ; or une périodicité de plis rend un
    PLATEAU de retour — la matière redevient semblable sur toute l'épaisseur d'un pli, pas sur une
    seule couche — donc le maximum local n'existe pas et le contrôle déclarait « pas de bosse » sur une
    matière construite pour en avoir une. C'est l'étalon qui l'a montré, rouge sur ses DEUX faces.

    ⭐ La forme juste est celle que la physique annonce : une matière qui se répète voit sa lecture
    CHUTER puis REVENIR au voisinage du pas ; une matière continue la voit décroître sans revenir. On
    mesure donc la remontée depuis le CREUX de la courbe avant le pas.

    ⚠ Le barreau zéro est la référence — la lecture de la couche par elle-même — et il est exclu du
    creux : sinon la remontée se mesurerait depuis un point que rien n'a dégradé.
    """
    lus = [b for b in courbe if b.get(cle) is not None]
    if len(lus) < 3:
        return {"decidable": False, "raison": "trop peu de barreaux"}
    i = min(range(len(lus)), key=lambda j: abs(int(lus[j]["montee"]) - int(pas_en_couches)))
    if abs(int(lus[i]["montee"]) - int(pas_en_couches)) > int(tolerance):
        return {"decidable": False, "raison": "aucun barreau au voisinage du pas"}
    if i < 2:
        return {"decidable": False, "raison": "le pas est trop près du départ de l'échelle"}
    vals = [float(b[cle]) for b in lus]
    creux = min(vals[1:i])
    j = 1 + vals[1:i].index(creux)
    # ⚠⚠⚠ LA REMONTÉE DOIT ÊTRE LA PLUS GRANDE DE LA COURBE, ET ELLE DOIT COMMENCER AU PAS. Une
    # première version se contentait de « la valeur au pas dépasse le creux » — ce qu'un frisson de
    # médiane suffit à satisfaire — donc elle ne testait PAS « au pas », seulement « au-dessus du
    # creux quelque part ». Elle n'implémentait pas son propre énoncé. Ici on prend le MAXIMUM de la
    # courbe après le creux et l'on regarde à quel barreau il est atteint POUR LA PREMIÈRE FOIS : une
    # périodicité de plis rend un plateau qui commence au pas, donc ce premier barreau EST le pas.
    apres = vals[j + 1:]
    sommet_apres = max(apres) if apres else None
    ou = (int(lus[j + 1 + apres.index(sommet_apres)]["montee"])
          if sommet_apres is not None else None)
    return {"decidable": True, "montee_lue": int(lus[i]["montee"]),
            "au_pas": round(vals[i], 3), "le_creux": round(creux, 3),
            "le_creux_en_couches": int(lus[j]["montee"]),
            "la_remontee_maximale": (round(sommet_apres - creux, 3)
                                     if sommet_apres is not None else None),
            "elle_commence_a": ou,
            "la_bosse": round(vals[i] - creux, 3),
            "il_y_a_une_bosse": bool(
                sommet_apres is not None and sommet_apres > creux and ou is not None
                and abs(int(ou) - int(pas_en_couches)) <= int(tolerance)),
            "sommet_de_la_courbe_en_couches": int(
                lus[max(range(len(vals)), key=lambda t: vals[t])]["montee"]),
            "elle_decroit_partout": bool(all(b <= a for a, b in zip(vals[1:i + 1],
                                                                   vals[2:i + 1])))}


def juger_une_courbe(courbe, pas_en_couches: int, tolerance: int) -> dict:
    """Ce qu'une courbe dit : l'empilement se répète, ou la texture décroît partout.

    ⚠⚠⚠ ET LA BOSSE DU MÉLANGE EST LUE AU MÊME BARREAU, parce que la porte l'exige : le mélange n'a
    plus d'ordre en profondeur, donc il ne peut pas faire de bosse à un multiple du pas. S'il en fait
    une quand même, la bosse est une propriété de la MARCHE et non de la matière.
    """
    vrai = la_bosse_au_pas(courbe, "pas_median", pas_en_couches, tolerance)
    melange = la_bosse_au_pas(courbe, "pas_median_melange", pas_en_couches, tolerance)
    return {"lexcedent": vrai, "le_melange": melange,
            # ⚠⚠⚠ ET LA REMONTEE DU MELANGE PRICE CELLE DE LA MATIERE : le melange n'a plus d'ordre
            # en profondeur, donc ce qu'il remonte est ce que la quantification et la marche
            # rapportent toutes seules. Exiger seulement « la matiere remonte » ferait passer un
            # frisson de mediane pour une periodicite.
            "lempilement_se_repete": bool(
                vrai.get("decidable") and melange.get("decidable")
                and vrai.get("il_y_a_une_bosse")
                and float(vrai.get("la_bosse") or 0.0) > float(melange.get("la_bosse") or 0.0)),
            "la_texture_decroit_partout": bool(
                vrai.get("decidable") and vrai.get("elle_decroit_partout"))}


def sur_la_fixture(montees, pas_en_couches: int, tolerance: int,
                   combien: int = DEPARTS_PAR_COUCHE, graine: int = GRAINE) -> dict:
    """Deux matières dont la réponse est CONNUE : l'une se répète, l'autre décroît.

    ⭐⭐⭐⭐ LE CONTRÔLE EST À DEUX FACES ET IL PEUT ÉCHOUER DES DEUX CÔTÉS. La première est un
    empilement dont chaque feuille est la COPIE de la précédente — il se répète exactement au pas, et
    l'instrument DOIT le dire. La seconde tourne lentement et ne repasse jamais par le même état — sa
    courbe DOIT décroître partout. Un instrument qui rendrait la même réponse aux deux lirait sa
    propre échelle.

    ⚠ La seconde étale un quart de tour sur TOUTE la hauteur du bloc : c'est la rotation la plus lente
    que cette hauteur permette, donc celle qui ressemble le plus à une continuité.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    plafond = le_plafond(vx, pas)
    lignes = []
    periodique = bloc_de_la_fixture(COUCHES_DE_LA_CAMPAGNE, 0.0, CONTRASTE_DE_LA_FIXTURE,
                                    int(PLIS_DE_LA_FIXTURE), vx, pas, transition_um=0.0,
                                    feuilles_independantes=False)
    continue_ = une_pile_qui_tourne(COUCHES_DE_LA_CAMPAGNE, COUCHES_DE_LA_CAMPAGNE)
    for nom, bloc, attendu in (("chaque feuille copie la précédente", periodique, "se répète"),
                               ("un quart de tour sur tout le bloc", continue_, "décroît partout")):
        ang, coh = orientation_profile(bloc)
        lu = la_courbe(bloc, ang, coh, montees, combien, plafond, PLANCHER_DE_COHERENCE, graine)
        if not lu.get("decidable"):
            lignes.append({"matiere": nom, "attendu": attendu, "decidable": False,
                           "raison": lu.get("raison")})
            continue
        lignes.append({"matiere": nom, "attendu": attendu, **lu,
                       **juger_une_courbe(lu["barreaux"], pas_en_couches, tolerance)})
    return {"lignes": lignes,
            "la_periodique_se_repete": bool(
                lignes and lignes[0].get("lempilement_se_repete")),
            "la_continue_decroit_partout": bool(
                len(lignes) > 1 and lignes[1].get("la_texture_decroit_partout")),
            # ⚠⚠ LES DEUX ENSEMBLE, ET PAS L'UN OU L'AUTRE : un instrument qui dirait « se repete »
            # aux deux, ou « decroit » aux deux, passerait la moitie du controle en ne discriminant
            # rien.
            "letalon_separe_les_deux": bool(
                lignes and len(lignes) > 1 and lignes[0].get("lempilement_se_repete")
                and lignes[1].get("la_texture_decroit_partout")
                and not lignes[0].get("la_texture_decroit_partout")
                and not lignes[1].get("lempilement_se_repete"))}


def un_segment(volume: dict, montees, pas_en_couches: int, tolerance: int, combien: int,
               plafond_max: int, cote: int = COTE_DU_TREILLIS, delai: float = DELAI,
               graine: int = GRAINE) -> dict:
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    lignes, refus = [], {}
    for cy, cx in les_chunks(-(-rows // hy), -(-cols // hx), cote):
        raw = get(f"{url}/{chunk_key(meta, 0, cy, cx)}", delai)
        if raw is None:
            refus["absent"] = refus.get("absent", 0) + 1
            continue
        data = decode(raw, meta, profond * hy * hx)
        if data is None:
            refus["illisible"] = refus.get("illisible", 0) + 1
            continue
        bloc = np.frombuffer(data, dtype=np.dtype(meta["dtype"])).reshape(profond, hy, hx)
        if int(bloc.max()) == 0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        ang, coh = orientation_profile(bloc)
        if int((coh > PLANCHER_DE_COHERENCE).sum()) < profond // 4:
            refus["trop peu texturé"] = refus.get("trop peu texturé", 0) + 1
            continue
        lu = la_courbe(bloc.astype(np.float32), ang, coh, montees, combien, plafond_max,
                       PLANCHER_DE_COHERENCE, graine)
        if not lu.get("decidable"):
            refus[lu.get("raison", "indécidable")] = refus.get(lu.get("raison", "indécidable"),
                                                               0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)], **lu,
                       **juger_une_courbe(lu["barreaux"], pas_en_couches, tolerance)})
    # ⚠⚠ LA COURBE DU SEGMENT EST LA MEDIANE BARREAU PAR BARREAU : un chunk atypique deviendrait
    # sinon la mesure, et c'est la FORME qu'on lit.
    courbe = []
    for i, m in enumerate(montees):
        v = [x["barreaux"][i]["pas_median"] for x in lignes
             if x["barreaux"][i]["pas_median"] is not None]
        f = [x["barreaux"][i]["pas_median_melange"] for x in lignes
             if x["barreaux"][i]["pas_median_melange"] is not None]
        courbe.append({"montee": int(m), "pas_median": _med(v), "pas_median_melange": _med(f),
                       "excedent": (round(_med(v) - _med(f), 3) if v and f else None)})
    return {"decidable": bool(lignes), "segment": volume["segment"], "chunks_lus": len(lignes),
            "refuses": refus, "courbe": courbe,
            "chunks_qui_se_repetent": int(sum(1 for x in lignes
                                              if x.get("lempilement_se_repete"))),
            "chunks_qui_decroissent_partout": int(sum(1 for x in lignes
                                                      if x.get("la_texture_decroit_partout"))),
            **juger_une_courbe(courbe, pas_en_couches, tolerance), "chunks": lignes}


def juger(segments: list[dict], etalon: dict, montees, pas_en_couches: int, tolerance: int,
          voxel_um: float, pas_um: float) -> dict:
    """L'empilement se répète-t-il, ou la texture décroît-elle partout ?"""
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible"}
    courbe = []
    for i, m in enumerate(montees):
        v = [s["courbe"][i]["pas_median"] for s in lus
             if s["courbe"][i]["pas_median"] is not None]
        f = [s["courbe"][i]["pas_median_melange"] for s in lus
             if s["courbe"][i]["pas_median_melange"] is not None]
        courbe.append({"montee": int(m), "montee_um": round(float(m) * float(voxel_um), 3),
                       "pas_median": _med(v), "pas_median_melange": _med(f),
                       "excedent": (round(_med(v) - _med(f), 3) if v and f else None)})
    verdict = juger_une_courbe(courbe, pas_en_couches, tolerance)
    # ⭐⭐⭐⭐ LA PORTEE DU TRANSFERT SE LIT AVEC LA REGLE DE `188`, LA MEME, et c'est ce qui rend les
    # deux nombres comparables : le croisement de la vraie matiere avec son melange. Ce que `188`
    # mesurait etait la portee d'un CHEMIN ; ici c'est celle d'un SAUT direct, et leur ecart est le
    # resultat.
    portee = la_portee_en_profondeur(courbe)
    pt = portee.get("portee_en_couches")
    chemin_um = la_portee_du_chemin_publiee()
    transfert_um = (round(float(pt) * float(voxel_um), 3) if pt is not None else None)
    return {"decidable": True, "segments": len(lus),
            "la_portee_du_transfert": portee,
            "la_portee_du_transfert_en_couches": pt,
            "la_portee_du_transfert_um": transfert_um,
            "la_portee_du_chemin_um": chemin_um,
            "le_chemin_porte_plus_loin_fois": (
                round(float(chemin_um) / float(transfert_um), 4)
                if chemin_um and transfert_um else None),
            # ⚠⚠ L'ENONCE QUI SEPARE LES DEUX LECTURES : si un chemin porte plus loin qu'un saut
            # direct, alors ce que l'ordre en profondeur porte est la CONTIGUITE et non la
            # ressemblance a distance.
            "la_contiguite_porte_plus_loin_que_la_ressemblance": bool(
                chemin_um is not None and transfert_um is not None
                and float(chemin_um) > float(transfert_um)),
            "chunks_lus": int(sum(s["chunks_lus"] for s in lus)),
            "chunks_qui_se_repetent": int(sum(s["chunks_qui_se_repetent"] for s in lus)),
            "chunks_qui_decroissent_partout": int(sum(s["chunks_qui_decroissent_partout"]
                                                      for s in lus)),
            "courbe": courbe, **verdict,
            "le_pas_en_couches": int(pas_en_couches),
            "le_pas_entre_deux_feuilles_um": float(pas_um),
            "la_tolerance_en_couches": int(tolerance),
            "la_bosse_tombe_a_um": (
                round(float(verdict["lexcedent"]["montee_lue"]) * float(voxel_um), 3)
                if verdict["lexcedent"].get("montee_lue") is not None else None),
            "la_hauteur_de_la_bosse": verdict["lexcedent"].get("la_bosse"),
            "letalon_separe_les_deux": bool(etalon.get("letalon_separe_les_deux")),
            "la_periodique_se_repete_sur_letalon": bool(etalon.get("la_periodique_se_repete")),
            "la_continue_decroit_partout_sur_letalon": bool(
                etalon.get("la_continue_decroit_partout"))}


def mesurer(segments_n: int = SEGMENTS, combien: int = DEPARTS_PAR_COUCHE,
            cote: int = COTE_DU_TREILLIS) -> dict:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    sommet = le_sommet_publie()
    if not sommet:
        return {"message": "le sommet de `188` n'est pas lisible ; relancer `188` d'abord"}
    montees = lechelle_autour_du_pas(vx, pas, int(sommet))
    pas_en_couches = le_pas_en_couches(vx, pas)
    plafond = le_plafond(vx, pas)
    volumes = les_volumes(combien=segments_n)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    etalon = sur_la_fixture(montees, pas_en_couches, int(sommet), combien)
    segs = [un_segment(v, montees, pas_en_couches, int(sommet), combien, plafond, cote)
            for v in volumes]
    return {"departs_par_couche": int(combien), "cote_du_treillis": int(cote),
            "plafond_de_pas": int(plafond), "voxel_um": vx, "pas_um": pas, "graine": int(GRAINE),
            "sommet_relu_de_188": int(sommet), "montees": [int(m) for m in montees],
            "le_pas_en_couches": int(pas_en_couches),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "letalon": etalon, "les_segments": segs,
            "le_verdict": juger(segs, etalon, montees, pas_en_couches, int(sommet), vx, pas)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v, e = r["le_verdict"], r["letalon"]
    print("L'EMPILEMENT SE RÉPÈTE-T-IL, OU EST-CE LA MÊME FEUILLE ?")
    print(f"  échelle au pas de {r['sommet_relu_de_188']} couches (le sommet de `188`) · "
          f"{r['montees']} · le pas vaut {r['le_pas_en_couches']} couches · "
          f"{v['chunks_lus']} chunks")
    print()
    print("  L'ÉTALON")
    for x in e["lignes"]:
        if not x.get("decidable"):
            print(f"     {x['matiere']:<38} — {x.get('raison')}")
            continue
        print(f"     {x['matiere']:<38} attendu « {x['attendu']} » · se répète "
              f"{x['lempilement_se_repete']} · décroît partout {x['la_texture_decroit_partout']} · "
              f"bosse {x['lexcedent'].get('la_bosse')} au barreau "
              f"{x['lexcedent'].get('montee_lue')}")
    print()
    print("  LA COURBE — la vraie matière contre ses couches mélangées")
    for b in v["courbe"]:
        marque = " ←— le pas" if int(b["montee"]) == int(v["le_pas_en_couches"]) else ""
        print(f"     montée {b['montee']:>3} couches ({b['montee_um']:>7} µm) · "
              f"{b['pas_median']} contre {b['pas_median_melange']} · excédent "
              f"{b['excedent']}{marque}")
    print()
    print("  ★ LE VERDICT")
    for cle in ("segments", "chunks_lus", "chunks_qui_se_repetent",
                "chunks_qui_decroissent_partout", "le_pas_en_couches",
                "la_tolerance_en_couches", "la_bosse_tombe_a_um",
                "la_hauteur_de_la_bosse", "la_portee_du_transfert_en_couches",
                "la_portee_du_transfert_um", "la_portee_du_chemin_um",
                "le_chemin_porte_plus_loin_fois",
                "la_contiguite_porte_plus_loin_que_la_ressemblance",
                "letalon_separe_les_deux", "la_periodique_se_repete_sur_letalon",
                "la_continue_decroit_partout_sur_letalon", "lempilement_se_repete",
                "la_texture_decroit_partout"):
        print(f"     {cle:<46} {v.get(cle)}")
    print(f"     {'lexcedent':<46} {v['lexcedent']}")
    print(f"     {'le_melange':<46} {v['le_melange']}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    pas_en_couches = le_pas_en_couches(vx, pas)

    # ⚠⚠ LE PAS DE L'ECHELLE EST RELU DE `188` ET NON TAPE : c'est l'echelle de correlation que
    # `188` a mesuree, et un pas plus grossier ne pourrait pas resoudre une bosse.
    sommet = le_sommet_publie()
    v("le sommet de `188` est relu", sommet is not None and sommet > 0, str(sommet))
    v("et il est absent quand la mesure l'est",
      le_sommet_publie(Path("/n/existe/pas.json")) is None)

    ech = lechelle_autour_du_pas(vx, pas, 8)
    v("l'échelle part de zéro", ech[0] == 0, str(ech))
    v("elle est LINÉAIRE au pas du sommet",
      all(b - a == 8 for a, b in zip(ech, ech[1:])), str(ech))
    # ⚠⚠⚠ ELLE VA AU-DELA DU PAS D'EXACTEMENT DEUX SOMMETS : sans l'autre versant, une montee finale
    # serait une bosse indiscernable d'un plateau.
    v("★ elle dépasse le pas d'exactement deux sommets",
      ech[-1] == pas_en_couches + 16, f"{ech[-1]} pour un pas de {pas_en_couches}")
    v("et le pas tombe sur un barreau", pas_en_couches in ech, str(ech))
    v("le pas est arrondi au PLUS PROCHE et non vers le haut",
      le_pas_en_couches(2.4, 173.0) == 72, str(le_pas_en_couches(2.4, 173.0)))
    v("un pas qui ne tomberait pas sur un barreau y est ajouté",
      175 in lechelle_autour_du_pas(1.0, 175.0, 8),
      str(lechelle_autour_du_pas(1.0, 175.0, 8))[-40:])

    # ⭐⭐⭐⭐ LE MEME JEU DE DEPARTS A TOUS LES BARREAUX : sans lui, la FORME de la courbe melerait ce
    # que la matiere porte et ce que l'echantillon a retreci.
    coh = np.full(109, 0.9)
    prof = les_profondeurs_communes(coh, 88)
    v("les profondeurs montantes tiennent la plus grande montée",
      all(0 <= k + 88 < 109 for k in prof[1]) and len(prof[1]) == 21, str(len(prof[1])))
    v("les descendantes aussi", all(0 <= k - 88 < 109 for k in prof[-1])
      and len(prof[-1]) == 21, str(len(prof[-1])))
    v("une couche sans texture n'y entre pas",
      les_profondeurs_communes([0.01] * 109, 88) == {1: [], -1: []})
    v("et une montée plus grande que le bloc ne laisse personne",
      les_profondeurs_communes(coh, 200) == {1: [], -1: []})

    # ⭐⭐⭐⭐ L'ANGLE EST CELUI DE LA COUCHE SOURCE, ET RIEN NE L'EXERCAIT — une sonde est passee au
    # VERT et c'est elle qui a fait ecrire ce controle. Ici les six premieres couches portent des
    # cretes HORIZONTALES et les six suivantes des VERTICALES : porter la lecture de la premiere dans
    # la seconde doit rendre une marche COURTE, parce qu'on y avance en travers. Prendre l'angle de la
    # couche CIBLE rendrait une marche aussi longue qu'a ecart nul, et le transfert ne mesurerait plus
    # que « la couche cible a-t-elle des cretes ».
    yy3, xx3 = np.mgrid[0:64, 0:64].astype(np.float32)
    horiz = 100.0 + 40.0 * np.cos(2.0 * np.pi * yy3 / 12.0)
    verti = 100.0 + 40.0 * np.cos(2.0 * np.pi * xx3 / 12.0)
    croise = np.stack([horiz] * 6 + [verti] * 6).astype(np.float32)
    ang_c, coh_c = orientation_profile(croise)
    dep_c = les_departs_par_couche(croise, coh_c, DEPARTS_PAR_COUCHE)
    prof_c = les_profondeurs_communes(coh_c, 6)
    t0 = un_barreau_de_transfert(croise, ang_c, 0, dep_c, 40, prof_c)
    t6 = un_barreau_de_transfert(croise, ang_c, 6, dep_c, 40, prof_c)
    v("le transfert à écart nul est la lecture de la couche elle-même",
      t0["pas_median"] is not None and t0["pas_median"] >= 30, str(t0))
    # ⚠⚠⚠ ET LA COMPARAISON EST STRUCTURELLE ET NON UN ECART CHOISI : une premiere version assertait
    # seulement « plus court », ce qu'un demi-pas suffit a satisfaire — donc la sonde passait au VERT
    # meme en prenant l'angle de la cible. Le transfert doit etre plus proche de la lecture EN
    # TRAVERS que de la lecture LE LONG, et ces deux-la se mesurent.
    travers = []
    for k in prof_c[1]:
        a = float(direction_des_fibres_deg(float(ang_c[k]))) + 90.0
        travers += un_ruban(croise, dep_c[k], float(k), a, 0, 40)
    t_travers = _med(travers)
    v("★★★★ porté dans une couche aux fibres perpendiculaires, il lit EN TRAVERS et non le long",
      t6["pas_median"] is not None and t_travers is not None
      and abs(t6["pas_median"] - t_travers) < abs(t6["pas_median"] - t0["pas_median"]),
      f"{t6['pas_median']} contre {t_travers} en travers et {t0['pas_median']} le long")

    # ⭐⭐⭐⭐ LA BOSSE EST UN MAXIMUM LOCAL AU PAS, ET LA MEME REGLE VAUT POUR LES DEUX COURBES.
    def _c(m, x, mel=5.0):
        return {"montee": int(m), "excedent": float(x), "pas_median_melange": float(mel),
                "pas_median": round(float(mel) + float(x), 3)}

    bosse = [_c(0, 0.0), _c(8, 10.0), _c(16, 8.0), _c(32, 5.0), _c(64, 3.0), _c(72, 6.0),
             _c(80, 4.0), _c(88, 3.0)]
    plate = [_c(0, 0.0), _c(8, 10.0), _c(16, 8.0), _c(32, 5.0), _c(64, 3.0), _c(72, 2.0),
             _c(80, 1.5), _c(88, 1.0)]
    rb = la_bosse_au_pas(bosse, "excedent", 72, 8)
    rp = la_bosse_au_pas(plate, "excedent", 72, 8)
    v("★★★★ une bosse au pas est trouvée, et au bon barreau",
      rb["il_y_a_une_bosse"] and rb["montee_lue"] == 72, str(rb))
    # ⚠ La hauteur se mesure depuis le CREUX de la courbe avant le pas, pas depuis le voisin : ici
    # le creux vaut 3,0 au barreau 64 et la valeur au pas 6,0.
    v("et sa hauteur est publiée, mesurée depuis le creux",
      rb["la_bosse"] == 3.0 and rb["le_creux_en_couches"] == 64, str(rb))
    v("★★★★ une courbe qui décroît partout ne fait aucune bosse",
      rp["elle_decroit_partout"] and not rp["il_y_a_une_bosse"], str(rp))
    # ⚠⚠⚠ UNE BOSSE AILLEURS QU'AU PAS N'EST PAS LUE : le barreau interroge est celui du PAS.
    ailleurs = [_c(0, 0.0), _c(8, 10.0), _c(16, 8.0), _c(32, 9.0), _c(64, 3.0), _c(72, 2.0),
                _c(80, 1.5), _c(88, 1.0)]
    ra = la_bosse_au_pas(ailleurs, "excedent", 72, 8)
    v("★★★★ une bosse AILLEURS qu'au pas n'est pas lue comme une bosse au pas",
      not ra["il_y_a_une_bosse"] and ra["montee_lue"] == 72, str(ra))
    v("et elle empêche de dire que la courbe décroît partout",
      not ra["elle_decroit_partout"], str(ra["elle_decroit_partout"]))
    # ⚠⚠⚠ ET C'EST LE DÉFAUT QUE LA TRANCHE A PAYÉ, DEVENU UN CONTRÔLE NOMMÉ. Une courbe qui remonte
    # AVANT le pas puis redescend un peu satisfaisait l'ancienne règle — « la valeur au pas dépasse le
    # creux » — alors que la remontée n'était pas au pas du tout. La règle réparée demande que le
    # MAXIMUM d'après le creux soit atteint POUR LA PREMIÈRE FOIS au pas.
    remonte_avant = [_c(0, 0.0), _c(8, 10.0), _c(16, 8.0), _c(32, 5.0), _c(48, 7.0),
                     _c(64, 7.0), _c(72, 6.0), _c(80, 5.0), _c(88, 5.5)]
    rr = la_bosse_au_pas(remonte_avant, "excedent", 72, 8)
    v("★★★★ une remontée qui commence AVANT le pas n'est pas une bosse au pas",
      not rr["il_y_a_une_bosse"] and rr["elle_commence_a"] == 48, str(rr))
    v("et la remontée maximale est publiée avec l'endroit où elle commence",
      rr["la_remontee_maximale"] == 2.0 and rr["le_creux_en_couches"] == 32, str(rr))

    v("la tolérance admet un barreau voisin",
      la_bosse_au_pas([_c(0, 0.0), _c(8, 10.0), _c(64, 3.0), _c(76, 9.0), _c(88, 2.0)],
                      "excedent", 72, 8)["il_y_a_une_bosse"])
    v("et un barreau trop loin du pas n'est pas décidable",
      not la_bosse_au_pas([_c(0, 0.0), _c(8, 10.0), _c(32, 9.0), _c(40, 2.0)],
                          "excedent", 72, 8).get("decidable"))
    # ⚠ Le pas doit avoir de la place AVANT lui : sans deux barreaux en amont il n'y a pas de creux
    # d'où remonter, et une « remontée » se mesurerait depuis la référence elle-même.
    v("un pas trop près du départ de l'échelle n'est pas décidable",
      not la_bosse_au_pas([_c(0, 0.0), _c(8, 10.0), _c(72, 9.0)],
                          "excedent", 8, 8).get("decidable"))
    v("une courbe trop courte n'est pas décidable",
      not la_bosse_au_pas([_c(0, 0.0), _c(8, 1.0)], "excedent", 72, 8).get("decidable"))

    # ⚠⚠⚠ ET LA BOSSE DU MELANGE EST LUE AU MEME BARREAU : s'il en fait une, elle est celle de la
    # MARCHE et non de la matiere. Une regle qui ne regarderait qu'apres le sommet ne pourrait
    # JAMAIS la voir sur une courbe plate, ou la bosse EST le sommet — ce controle serait alors
    # incapable d'echouer.
    j1 = juger_une_courbe(bosse, 72, 8)
    v("★★★★ une bosse au pas dit que l'empilement se répète", j1["lempilement_se_repete"])
    bosse_melange = [dict(x, pas_median_melange=(9.0 if x["montee"] == 72 else 5.0))
                     for x in bosse]
    j2 = juger_une_courbe(bosse_melange, 72, 8)
    v("★★★★ mais pas si le MÉLANGE fait une bosse au même barreau",
      not j2["lempilement_se_repete"], str(j2["le_melange"]))
    j3 = juger_une_courbe(plate, 72, 8)
    v("une courbe qui décroît partout dit que la texture décroît",
      j3["la_texture_decroit_partout"] and not j3["lempilement_se_repete"])
    v("et les deux énoncés ne sont jamais vrais ensemble",
      not (j1["lempilement_se_repete"] and j1["la_texture_decroit_partout"]))

    # ⚠⚠ LES ENONCES DU VERDICT TOMBENT CHACUN SUR L'ENTREE QUI LE VISE.
    mont = [0, 8, 16, 32, 64, 72, 80, 88]

    def _seg(courbe, rep=3, dec=0):
        return {"decidable": True, "segment": "x", "chunks_lus": 9, "refuses": {},
                "courbe": [dict(x, montee_um=x["montee"] * vx) for x in courbe],
                "chunks_qui_se_repetent": int(rep),
                "chunks_qui_decroissent_partout": int(dec), "chunks": []}

    bon = {"letalon_separe_les_deux": True, "la_periodique_se_repete": True,
           "la_continue_decroit_partout": True}
    r1 = juger([_seg(bosse)], bon, mont, 72, 8, vx, pas)
    v("un étalon qui sépare les deux rend le premier énoncé", r1["letalon_separe_les_deux"])
    v("une bosse au pas dit que l'empilement se répète", r1["lempilement_se_repete"])
    v("et la bosse est publiée en micromètres",
      abs(r1["la_bosse_tombe_a_um"] - 72 * vx) < 1e-9, str(r1["la_bosse_tombe_a_um"]))
    v("et sa hauteur aussi", r1["la_hauteur_de_la_bosse"] == 3.0,
      str(r1["la_hauteur_de_la_bosse"]))
    r2 = juger([_seg(plate)], bon, mont, 72, 8, vx, pas)
    v("une courbe qui décroît partout le dit", r2["la_texture_decroit_partout"]
      and not r2["lempilement_se_repete"])
    for cle in ("la_periodique_se_repete", "la_continue_decroit_partout"):
        r3 = juger([_seg(bosse)], {**bon, cle: False, "letalon_separe_les_deux": False},
                   mont, 72, 8, vx, pas)
        v(f"★ un étalon qui perd « {cle} » retire le premier énoncé",
          not r3["letalon_separe_les_deux"])
    # ⭐⭐⭐⭐ ET L'ENONCE QUI SEPARE LES DEUX LECTURES : un CHEMIN qui porte plus loin qu'un SAUT
    # direct dit que ce que l'ordre en profondeur porte est la CONTIGUITE et non la ressemblance a
    # distance. La portee du transfert se lit avec la regle de `188`, la MEME, pour qu'elles soient
    # comparables.
    v("la portée du transfert est lue avec la règle de `188`",
      r2["la_portee_du_transfert_en_couches"] is not None
      or r2["la_portee_du_transfert"].get("au_dela_de_lechelle"),
      str(r2["la_portee_du_transfert"]))
    if r2["la_portee_du_transfert_um"] and r2["la_portee_du_chemin_um"]:
        v("★★★★ et un chemin qui porte plus loin qu'un saut dit que c'est la CONTIGUÏTÉ",
          r2["la_contiguite_porte_plus_loin_que_la_ressemblance"]
          == (float(r2["la_portee_du_chemin_um"]) > float(r2["la_portee_du_transfert_um"])),
          f"{r2['la_portee_du_chemin_um']} contre {r2['la_portee_du_transfert_um']}")

    vide = juger([{"decidable": False, "segment": "x"}], bon, mont, 72, 8, vx, pas)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"])

    # ⭐⭐⭐⭐ ET LA MATIERE CONSTRUITE : une pile dont chaque feuille COPIE la precedente doit se
    # repeter, une pile qui tourne lentement doit decroitre partout. C'est le controle a deux faces,
    # et il peut echouer des deux cotes.
    # ⚠⚠ UNE PERIODICITE EXTREME ET POSEE : douze couches d'une texture, douze de l'autre, et ainsi
    # de suite. A une montee de VINGT-QUATRE la matiere est identique a elle-meme, a DOUZE elle est
    # l'autre texture. La bosse doit donc tomber a vingt-quatre, et nulle part ailleurs.
    petit = [0, 6, 12, 18, 24, 30, 36]
    yy2, xx2 = np.mgrid[0:64, 0:64].astype(np.float32)
    a_ = 100.0 + 40.0 * np.cos(2.0 * np.pi * yy2 / 12.0)
    b_ = 100.0 + 40.0 * np.cos(2.0 * np.pi * xx2 / 12.0)
    periodique = np.stack([(a_ if (k // 12) % 2 == 0 else b_)
                           for k in range(60)]).astype(np.float32)
    ang_p, coh_p = orientation_profile(periodique)
    lu_p = la_courbe(periodique, ang_p, coh_p, petit, DEPARTS_PAR_COUCHE, 40)
    v("une pile qui se répète rend une courbe", lu_p.get("decidable"), str(lu_p.get("raison")))
    if lu_p.get("decidable"):
        v("★ et le même jeu de départs sert à tous ses barreaux",
          lu_p["le_meme_jeu_a_tous_les_barreaux"],
          str({b["montee"]: b["rubans"] for b in lu_p["barreaux"]}))
        jp = juger_une_courbe(lu_p["barreaux"], 24, 6)
        v("★★★★ et l'instrument dit qu'elle se répète", jp["lempilement_se_repete"],
          str(jp["lexcedent"]))
    lente = une_pile_qui_tourne(60, 60)
    ang_l, coh_l = orientation_profile(lente)
    lu_l = la_courbe(lente, ang_l, coh_l, petit, DEPARTS_PAR_COUCHE, 40)
    if lu_l.get("decidable"):
        jl = juger_une_courbe(lu_l["barreaux"], 24, 6)
        v("★★★★ et qu'une pile qui tourne lentement ne se répète PAS",
          not jl["lempilement_se_repete"], str(jl["lexcedent"]))

    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "lempilement_se_repete_t_il.py"
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
