"""Le rouleau creuse-t-il ? — la cohérence du vrai volume, et ce que le creux y sépare.

⭐⭐⭐⭐ POURQUOI CE FICHIER. `179` a construit le lecteur que `R4-P31` resserrée nommait : un creux
de COHÉRENCE, qui ne passe pas par le tour accumulé, donc qui n'est pas soumis à l'échange que `178`
a mesuré. Il tient — creux sur la frontière construite aux douze décalages, domaine jusqu'au bruit
seize de `156`, contrôle vide muet, liberté de la largeur payée par une statistique de famille — MAIS
il est conditionné à une propriété de la MATIÈRE que rien n'avait mesurée : les deux plis doivent se
recouvrir sur un demi-pli. `R4-P32` demande cette mesure, et c'est celle-ci.

⚠⚠⚠ LE PIÈGE PROPRE À CETTE TRANCHE, ET IL EST NOUVEAU. Sur une matière construite, une permutation
des couches est un contrôle suffisant : elle conserve le multiensemble et détruit l'ordre. Sur une
matière RÉELLE, la cohérence est AUTOCORRÉLÉE — deux couches voisines se ressemblent parce que le
volume est lisse — donc n'importe quelle ondulation bat ses mélanges, et « le creux dépasse toutes
ses permutations » pourrait ne vouloir dire que « la cohérence est lisse ». La permutation est ici
NÉCESSAIRE ET NON SUFFISANTE, et ce qui la complète est un ÉTALON SANS FRONTIÈRE lu par le même
chemin : une feuille d'UN SEUL pli, au même recouvrement, aux mêmes bruits. Ce que ce matériau rend
est ce qu'une matière lisse et sans frontière peut produire, et le rouleau se compare à LUI autant
qu'à l'étalon qui porte une frontière.

⭐⭐⭐⭐ LES DEUX ÉTALONS ENCADRENT LA QUESTION, ET LE ROULEAU SE PLACE ENTRE EUX. Sans frontière et
avec frontière, lus par le MÊME instrument, aux MÊMES bruits : la profondeur du rouleau n'a pas
besoin d'un seuil pour être lue, elle a besoin de deux bornes mesurées.

⚠⚠ ET LE BRUIT DE COMPARAISON EST DÉRIVÉ, PAS CHOISI : on retient le barreau de l'échelle de `156`
dont la cohérence médiane est la plus proche de celle du rouleau. Comparer une matière dont la
cohérence vaut un à un rouleau dont elle vaut un sixième serait comparer deux régimes.

⭐⭐⭐⭐ ET LA SECONDE MOITIÉ EST CE QUE LE CREUX SÉPARE. Un creux de cohérence dit qu'il se passe
quelque chose ; il ne dit pas QUOI. Deux causes le produisent et elles ne sont pas la même chose :
une frontière de pli DANS une feuille, où deux directions se recouvrent et où les deux côtés restent
DIRIGÉS ; et l'interstice ENTRE deux feuilles, où il n'y a pas de matière, donc pas de texture, donc
aucune direction d'aucun côté. `14` §3 note déjà que l'orientation devient erratique là où la
cohérence s'effondre. On lit donc, de part et d'autre de chaque creux, si la matière est DIRIGÉE au
sens de `174` — résultante au-dessus de `1/√n` — et quel est l'écart entre les deux directions.

⚠ Le chemin du rouleau est EXACTEMENT celui de `176`, appelé et non recopié : mêmes volumes dans
l'ordre du dépôt, même treillis régulier, même filtre du producteur. Une seconde définition du
« chunk lu » serait libre d'en diverger, et la comparaison à `176` cesserait d'en être une.

Usage :
    uv run python src/nappe/le_rouleau_creuse_t_il.py --verifier
    uv run python src/nappe/le_rouleau_creuse_t_il.py \\
        --json docs/mesures/le_rouleau_creuse_t_il.json
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

from fiber_orientation import angular_gap  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import (  # noqa: E402
    CONTRASTE_DE_LA_FIXTURE, PLIS_DE_LA_FIXTURE, le_verdict_du_creux)
from la_coupe_cherchee_trouve_t_elle_la_frontiere import (  # noqa: E402
    COUCHES_MINIMALES, PLANCHER_DE_COHERENCE, la_direction_dune_tranche)
from la_croix_marche_t_elle_le_tour import BRUITS  # noqa: E402
from la_profondeur_tourne_t_elle_ou_bascule_t_elle import (  # noqa: E402
    PERMUTATIONS, ce_que_le_rouleau_a_rendu)
from la_recette_posee_sur_le_rouleau import (COTE_DU_TREILLIS, DELAI,  # noqa: E402
                                             SEGMENTS, la_courbe_dun_chunk, les_chunks,
                                             les_volumes)
from quelle_fenetre_lit_une_bascule import courbe_de_la_fixture  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_FIXTURE_A_RENDU = MESURES / "la_coherence_creuse_t_elle_a_la_frontiere.json"
GRAINE = 20260920
DECALAGES = 12


def ce_que_la_fixture_a_rendu(chemin: Path = CE_QUE_LA_FIXTURE_A_RENDU) -> dict | None:
    """Le recouvrement juste suffisant et la profondeur à la borne, RELUS de la mesure de `179`.

    ⚠ Ils sont LUS et non recopiés : deux écritures d'un même nombre sont deux nombres qui peuvent
    se contredire, et celui-ci a un producteur. Précédent de `177` relisant `176`.
    """
    if not chemin.exists():
        return None
    v = json.loads(chemin.read_text(encoding="utf-8")).get("le_verdict", {})
    if v.get("le_recouvrement_juste_suffisant_um") is None:
        return None
    return {"recouvrement_um": float(v["le_recouvrement_juste_suffisant_um"]),
            "profondeur_a_la_borne": float(v["profondeur_du_creux_a_la_borne"]),
            "largeur_a_la_borne": int(v["largeur_du_creux_a_la_borne"]),
            "il_vaut_le_pli_fois": float(v["il_vaut_le_pli_fois"])}


def ce_que_le_creux_separe(courbe, couche: int, largeur: int,
                           plancher: float = PLANCHER_DE_COHERENCE,
                           minimum: int = COUCHES_MINIMALES) -> dict:
    """De part et d'autre du creux, la matière est-elle DIRIGÉE, et de combien diffèrent les deux ?

    ⭐⭐⭐⭐ C'EST CE QUI SÉPARE UNE FRONTIÈRE DE PLI D'UN INTERSTICE, et les deux creusent. Dans une
    feuille, deux plis se recouvrent : la cohérence tombe au milieu et les deux côtés gardent chacun
    leur direction. Entre deux feuilles il n'y a pas de matière : la cohérence tombe aussi, mais il
    n'y a de direction NULLE PART. La question « les deux côtés sont-ils dirigés » sépare donc les
    deux causes sans qu'aucun seuil n'entre.

    ⚠ « Dirigée » est ce que `174` a défini et rien d'autre : une résultante au-dessus de `1/√n`,
    borne dérivée et non choisie. Réécrire ce test ici en ferait une seconde définition.

    ⚠⚠ L'écart est lu en angle DOUBLE par `angular_gap`, donc il vit dans [0, 90] : une fibre n'a
    pas de sens, et une frontière de pli en prédit un quart de tour.
    """
    h = int(largeur) // 2
    a, b = max(0, int(couche) - h), min(len(courbe), int(couche) + h + 1)
    gauche = la_direction_dune_tranche(courbe, 0, a, plancher, minimum)
    droite = la_direction_dune_tranche(courbe, b, len(courbe), plancher, minimum)
    return {"couches_a_gauche": int(a), "couches_a_droite": int(len(courbe) - b),
            "gauche_est_dirigee": bool(gauche is not None),
            "droite_est_dirigee": bool(droite is not None),
            "les_deux_cotes_sont_diriges": bool(gauche is not None and droite is not None),
            "angle_a_gauche_deg": (round(float(gauche["angle_deg"]), 3) if gauche else None),
            "angle_a_droite_deg": (round(float(droite["angle_deg"]), 3) if droite else None),
            "ecart_deg": (round(float(angular_gap(gauche["angle_deg"], droite["angle_deg"])), 3)
                          if (gauche and droite) else None)}


def lire_un_chunk(courbe, permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """Le creux d'un chunk, et ce qu'il sépare.

    ⚠ Le lecteur est celui de `179`, appelé sans un octet de plus : la statistique de famille, la
    permutation des couches, les largeurs dérivées. La tranche mesure une MATIÈRE, pas un lecteur.
    """
    v = le_verdict_du_creux(courbe, None, permutations, graine)
    coh = [float(x[1]) for x in courbe]
    ligne = {"coherence_mediane": round(float(statistics.median(coh)), 4),
             "coherence_minimale": round(float(min(coh)), 4), **v}
    if v["gagnant"] == "empilement":
        ligne["ce_que_le_creux_separe"] = ce_que_le_creux_separe(
            courbe, int(v["couche"]), int(v["largeur"]))
    return ligne


def _med(v):
    return round(float(statistics.median(v)), 4) if v else None


def un_segment(volume: dict, cote: int = COTE_DU_TREILLIS, permutations: int = PERMUTATIONS,
               delai: float = DELAI, graine: int = GRAINE) -> dict:
    """Un segment : ses chunks du treillis, lus par le creux contre leurs permutations."""
    url = f"{BUCKET}/{volume['cle']}"
    try:
        meta = array_meta(url, 0, delai)
    except Exception as e:  # noqa: BLE001
        return {"decidable": False, "segment": volume["segment"],
                "raison": f"le volume ne répond pas : {type(e).__name__}"}
    profond, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    positions = les_chunks(gy, gx, cote)
    lignes, refus = [], {}
    for cy, cx in positions:
        courbe, pourquoi = la_courbe_dun_chunk(url, meta, cy, cx, delai)
        if courbe is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        lignes.append({"chunk": [int(cy), int(cx)],
                       **lire_un_chunk(courbe, permutations, graine)})
    lus = [x for x in lignes if x.get("decidable")]
    creusent = [x for x in lus if x["gagnant"] == "empilement"]
    separe = [x["ce_que_le_creux_separe"] for x in creusent]
    return {"decidable": bool(lus), "segment": volume["segment"],
            "zarr": volume["cle"].rsplit("/", 1)[-1], "couches": int(profond),
            "grille_de_chunks": [int(gy), int(gx)],
            "chunks_du_treillis": len(positions), "chunks_lus": len(lus), "refuses": refus,
            "chunks_qui_creusent": len(creusent),
            "coherence_mediane": _med([x["coherence_mediane"] for x in lus]),
            "profondeur_mediane": _med([x["profondeur"] for x in creusent]),
            "largeur_mediane": (int(statistics.median_low([x["largeur"] for x in creusent]))
                                if creusent else None),
            "les_deux_cotes_sont_diriges": int(
                sum(1 for x in separe if x["les_deux_cotes_sont_diriges"])),
            "aucun_cote_nest_dirige": int(
                sum(1 for x in separe if not x["gauche_est_dirigee"]
                    and not x["droite_est_dirigee"])),
            "ecart_median_deg": _med([x["ecart_deg"] for x in separe
                                      if x["ecart_deg"] is not None]),
            "lignes": lignes}


def un_etalon(plis: int, recouvrement_um: float, bruit: float, decalages: int = DECALAGES,
              permutations: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """La MÊME lecture sur la fixture, au même recouvrement et au même bruit.

    ⚠⚠ `plis=1` EST L'ÉTALON SANS FRONTIÈRE, et c'est lui qui rend la permutation suffisante ou non
    sur cette matière : une feuille d'un seul pli n'a aucune frontière d'orientation, donc tout ce
    que le lecteur y trouve est ce qu'une matière lisse peut produire toute seule.

    ⚠ `plis=2` est l'étalon AVEC frontière, lu au recouvrement que `179` a encadré.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    lignes = []
    for k in range(int(decalages)):
        dec = pas * k / float(decalages)
        courbe = courbe_de_la_fixture(109, dec, CONTRASTE_DE_LA_FIXTURE, int(plis), vx, pas,
                                      transition_um=float(recouvrement_um), bruit=float(bruit))
        lignes.append({"decalage_um": round(dec, 3),
                       **lire_un_chunk(courbe, permutations, graine)})
    creusent = [x for x in lignes if x["gagnant"] == "empilement"]
    separe = [x["ce_que_le_creux_separe"] for x in creusent]
    return {"plis": int(plis), "bruit": float(bruit), "cellules": len(lignes),
            "chunks_qui_creusent": len(creusent),
            "coherence_mediane": _med([x["coherence_mediane"] for x in lignes]),
            "profondeur_mediane": _med([x["profondeur"] for x in creusent]),
            "largeur_mediane": (int(statistics.median_low([x["largeur"] for x in creusent]))
                                if creusent else None),
            "les_deux_cotes_sont_diriges": int(
                sum(1 for x in separe if x["les_deux_cotes_sont_diriges"])),
            "ecart_median_deg": _med([x["ecart_deg"] for x in separe
                                      if x["ecart_deg"] is not None])}


def le_bruit_qui_correspond(etalons: list[dict], coherence_du_rouleau: float) -> float | None:
    """Le barreau de l'échelle de `156` dont la cohérence médiane est la plus proche du rouleau.

    ⚠⚠ DÉRIVÉ, PAS CHOISI. La cohérence de la fixture vaut un sans bruit et un sixième au bruit
    seize : comparer le rouleau à un étalon d'un autre régime comparerait deux instruments en
    croyant comparer deux matières. Ce qui est apparié est le NIVEAU de cohérence, la seule chose
    qui soit commune aux deux et qu'aucune des deux ne choisit.

    ⚠ L'appariement se fait sur l'étalon SANS frontière : c'est le fond, et c'est le fond qui doit
    ressembler à celui du rouleau. Égalités tranchées par le bruit le plus faible.
    """
    sans = [x for x in etalons if int(x["plis"]) == 1 and x["coherence_mediane"] is not None]
    if not sans or coherence_du_rouleau is None:
        return None
    return float(min(sans, key=lambda x: (abs(x["coherence_mediane"]
                                              - float(coherence_du_rouleau)), x["bruit"]))["bruit"])


def juger(segments: list[dict], etalons: list[dict], fixture: dict,
          permutations: int = PERMUTATIONS, de_176: dict | None = None) -> dict:
    """Le rouleau creuse-t-il, aussi profond qu'une frontière, et que sépare son creux ?

    ⚠⚠⚠ LE COMPTE ATTENDU SOUS L'HYPOTHÈSE NULLE EST PUBLIÉ À CÔTÉ DU COMPTE OBSERVÉ, comme `176`
    le fait : avec `K` permutations un chunk les dépasse toutes par hasard une fois sur `K+1`.

    ⚠⚠ ET LA PERMUTATION NE SUFFIT PAS ICI. Le compte de l'étalon SANS frontière, au bruit apparié,
    est publié à côté du compte du rouleau : c'est lui qui dit ce qu'une matière lisse et sans
    frontière produit, et c'est à lui que le rouleau doit être comparé autant qu'au hasard.
    """
    lus = [s for s in segments if s.get("decidable")]
    if not lus:
        return {"decidable": False, "raison": "aucun segment lisible",
                "segments_essayes": len(segments)}
    chunks = sum(s["chunks_lus"] for s in lus)
    creusent = sum(s["chunks_qui_creusent"] for s in lus)
    coherence = _med([s["coherence_mediane"] for s in lus if s["coherence_mediane"] is not None])
    bruit = le_bruit_qui_correspond(etalons, coherence)
    sans = next((x for x in etalons if int(x["plis"]) == 1 and x["bruit"] == bruit), None)
    avec = next((x for x in etalons if int(x["plis"]) == PLIS_DE_LA_FIXTURE
                 and x["bruit"] == bruit), None)
    profondeur = _med([s["profondeur_mediane"] for s in lus
                       if s["profondeur_mediane"] is not None])
    separe = [x["ce_que_le_creux_separe"] for s in lus for x in s["lignes"]
              if x.get("gagnant") == "empilement"]
    deux_cotes = int(sum(1 for x in separe if x["les_deux_cotes_sont_diriges"]))
    aucun_cote = int(sum(1 for x in separe if not x["gauche_est_dirigee"]
                         and not x["droite_est_dirigee"]))
    return {"decidable": True, "segments": len(lus), "segments_essayes": len(segments),
            "chunks_lus": chunks, "permutations": int(permutations),
            "chunks_attendus_par_hasard": round(chunks / (int(permutations) + 1.0), 2),
            "chunks_qui_creusent": int(creusent),
            "coherence_mediane_du_rouleau": coherence,
            "le_bruit_apparie": bruit,
            "coherence_mediane_de_letalon_sans_frontiere": (sans["coherence_mediane"]
                                                            if sans else None),
            "profondeur_mediane_du_rouleau": profondeur,
            "profondeur_de_letalon_sans_frontiere": (sans["profondeur_mediane"] if sans else None),
            "profondeur_de_letalon_avec_frontiere": (avec["profondeur_mediane"] if avec else None),
            "creusent_sur_letalon_sans_frontiere": (sans["chunks_qui_creusent"] if sans else None),
            "cellules_de_letalon": (sans["cellules"] if sans else None),
            "creusent_sur_letalon_avec_frontiere": (avec["chunks_qui_creusent"] if avec else None),
            "profondeur_a_la_borne_de_179": fixture["profondeur_a_la_borne"],
            "recouvrement_juste_suffisant_um_de_179": fixture["recouvrement_um"],
            "largeur_mediane_du_rouleau": (int(statistics.median_low(
                [s["largeur_mediane"] for s in lus if s["largeur_mediane"] is not None]))
                if any(s["largeur_mediane"] is not None for s in lus) else None),
            "largeur_de_letalon_avec_frontiere": (avec["largeur_mediane"] if avec else None),
            "creux_dont_les_deux_cotes_sont_diriges": deux_cotes,
            "creux_dont_aucun_cote_nest_dirige": aucun_cote,
            "ecart_median_aux_creux_deg": _med([x["ecart_deg"] for x in separe
                                                if x["ecart_deg"] is not None]),
            "ecart_de_letalon_avec_frontiere_deg": (avec["ecart_median_deg"] if avec else None),
            # ⚠⚠ DEUX RAPPORTS, ET ILS DISENT DEUX CHOSES DIFFERENTES. Le premier place l'ecart aux
            # creux par rapport au quart de tour qu'une frontiere de pli construite rend ; le second
            # le place par rapport a la bascule MOYENNE que `176` a publiee sur le meme rouleau.
            # L'un dit ce que ce n'est pas, l'autre ce que le creux ajoute a ce qu'on savait.
            "lecart_aux_creux_vaut_letalon_fois": (
                round(float(_med([x["ecart_deg"] for x in separe if x["ecart_deg"] is not None]))
                      / float(avec["ecart_median_deg"]), 4)
                if (separe and avec and avec.get("ecart_median_deg")) else None),
            "la_bascule_mediane_de_176_deg": (de_176["bascule_deg"] if de_176 else None),
            "lecart_aux_creux_vaut_la_bascule_de_176_fois": (
                round(float(_med([x["ecart_deg"] for x in separe if x["ecart_deg"] is not None]))
                      / float(de_176["bascule_deg"]), 4)
                if (separe and de_176) else None),
            # ⚠⚠ TROIS ENONCES DISTINCTS, ET IL FAUT LES TROIS. Le premier dit que le rouleau
            # creuse plus souvent que le hasard ; le second qu'il creuse plus souvent qu'une
            # matiere SANS frontiere, ce que la permutation seule ne peut pas dire sur une
            # cohérence autocorrelee ; le troisieme que la profondeur atteinte est celle d'une
            # frontiere et non celle d'un fond.
            "il_creuse_plus_que_le_hasard": bool(
                chunks and creusent > chunks / (int(permutations) + 1.0)),
            "il_creuse_plus_quun_fond_sans_frontiere": bool(
                sans is not None and sans["cellules"]
                and creusent / float(chunks) > sans["chunks_qui_creusent"] / float(
                    sans["cellules"])),
            "sa_profondeur_est_celle_dune_frontiere": bool(
                profondeur is not None and avec is not None
                and avec["profondeur_mediane"] is not None
                and profondeur >= avec["profondeur_mediane"]),
            "ses_creux_separent_deux_cotes_diriges": bool(
                separe and deux_cotes > len(separe) / 2.0)}


def les_profils(volumes: list[dict], bruit: float, recouvrement_um: float,
                cote: int = COTE_DU_TREILLIS, permutations: int = PERMUTATIONS,
                delai: float = DELAI, graine: int = GRAINE) -> list:
    """Les cohérences elles-mêmes : un chunk par segment, et les deux étalons au bruit apparié.

    ⚠⚠ ON PREND LE PREMIER CHUNK LISIBLE DU TREILLIS, jamais un chunk choisi : prendre le plus
    creusé ferait dessiner le choix. Et les deux étalons sont dessinés à côté, au même bruit, parce
    qu'une cohérence réelle ne veut rien dire seule — c'est son écart aux deux bornes qui parle.

    ⚠ Elles sont produites par la mesure et non par la figure : une figure qui recalculerait la
    matière dessinerait autre chose que ce que le document publie, et rien ne le dirait.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    sorties = []
    for volume in volumes:
        url = f"{BUCKET}/{volume['cle']}"
        try:
            meta = array_meta(url, 0, delai)
        except Exception:  # noqa: BLE001
            continue
        profond, hy, hx = meta["chunks"]
        _, rows, cols = meta["shape"]
        for cy, cx in les_chunks(-(-rows // hy), -(-cols // hx), cote):
            courbe, _ = la_courbe_dun_chunk(url, meta, cy, cx, delai)
            if courbe is None:
                continue
            x = lire_un_chunk(courbe, permutations, graine)
            sorties.append({"quoi": "le rouleau", "segment": volume["segment"],
                            "chunk": [int(cy), int(cx)],
                            "coherences": [round(float(a[1]), 4) for a in courbe],
                            "gagnant": x["gagnant"], "couche": x.get("couche"),
                            "largeur": x.get("largeur"), "profondeur": x.get("profondeur")})
            break
    for plis, nom in ((1, "un seul pli"), (PLIS_DE_LA_FIXTURE, "deux plis")):
        courbe = courbe_de_la_fixture(109, 0.0, CONTRASTE_DE_LA_FIXTURE, int(plis), vx, pas,
                                      transition_um=float(recouvrement_um), bruit=float(bruit))
        x = lire_un_chunk(courbe, permutations, graine)
        sorties.append({"quoi": nom, "bruit": float(bruit),
                        "coherences": [round(float(a[1]), 4) for a in courbe],
                        "gagnant": x["gagnant"], "couche": x.get("couche"),
                        "largeur": x.get("largeur"), "profondeur": x.get("profondeur")})
    return sorties


def mesurer(combien: int = SEGMENTS, cote: int = COTE_DU_TREILLIS,
            permutations: int = PERMUTATIONS, decalages: int = DECALAGES) -> dict:
    fixture = ce_que_la_fixture_a_rendu()
    if fixture is None:
        return {"message": "la mesure de `179` est absente : elle donne le recouvrement et l'échelle"}
    volumes = les_volumes(combien=combien)
    if not volumes:
        return {"message": "aucun volume de surface à la résolution de la campagne n'est recensé"}
    segments = [un_segment(v, cote, permutations) for v in volumes]
    etalons = [un_etalon(p, fixture["recouvrement_um"], b, decalages, permutations)
               for p in (1, PLIS_DE_LA_FIXTURE) for b in BRUITS]
    de_176 = ce_que_le_rouleau_a_rendu()
    verdict = juger(segments, etalons, fixture, permutations, de_176)
    profils = (les_profils(volumes, float(verdict["le_bruit_apparie"]),
                           fixture["recouvrement_um"], cote, permutations)
               if verdict.get("le_bruit_apparie") is not None else [])
    return {"cote_du_treillis": int(cote), "permutations": int(permutations),
            "graine": int(GRAINE), "decalages": int(decalages),
            "plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
            "bruits": [float(x) for x in BRUITS],
            "la_fixture_de_179": fixture, "le_rouleau_de_176": de_176,
            "les_segments": segments, "les_etalons": etalons, "les_profils": profils,
            "le_verdict": verdict}


def afficher(r: dict) -> None:
    if "message" in r:
        print(r["message"])
        return
    v = r["le_verdict"]
    print("LE ROULEAU CREUSE-T-IL ?")
    print(f"  treillis {r['cote_du_treillis']}×{r['cote_du_treillis']} · "
          f"{r['permutations']} permutations · recouvrement de l'étalon "
          f"{r['la_fixture_de_179']['recouvrement_um']} µm (`179`)")
    print()
    for s in r["les_segments"]:
        if not s.get("decidable"):
            print(f"  {s['segment']} — {s.get('raison')}")
            continue
        print(f"  {s['segment']} · {s['chunks_lus']}/{s['chunks_du_treillis']} chunks · "
              f"refusés {s['refuses']}")
        print(f"     cohérence {s['coherence_mediane']} · creusent "
              f"{s['chunks_qui_creusent']}/{s['chunks_lus']} · profondeur "
              f"{s['profondeur_mediane']} · largeur {s['largeur_mediane']} · deux côtés dirigés "
              f"{s['les_deux_cotes_sont_diriges']} · écart {s['ecart_median_deg']}°")
    print()
    print("  LES ÉTALONS · la MÊME lecture sur la fixture, au même recouvrement")
    print(f"   {'plis':>5} {'bruit':>6} {'cohérence':>10} {'creusent':>9} {'profondeur':>11} "
          f"{'largeur':>8} {'écart':>8}")
    for e in r["les_etalons"]:
        marque = "★" if e["bruit"] == v.get("le_bruit_apparie") else " "
        print(f"   {e['plis']:>5} {e['bruit']:>6.1f} {str(e['coherence_mediane']):>10} "
              f"{e['chunks_qui_creusent']:>6}/{e['cellules']:<2} "
              f"{str(e['profondeur_mediane']):>11} {str(e['largeur_mediane']):>8} "
              f"{str(e['ecart_median_deg']):>8} {marque}")
    print()
    if not v.get("decidable"):
        print(f"  ✗ {v.get('raison')}")
        return
    print(f"  ★ LE VERDICT · {v['chunks_lus']} chunks sur {v['segments']} segments · attendu par "
          f"hasard {v['chunks_attendus_par_hasard']}")
    for cle in ("chunks_qui_creusent", "coherence_mediane_du_rouleau", "le_bruit_apparie",
                "coherence_mediane_de_letalon_sans_frontiere",
                "creusent_sur_letalon_sans_frontiere", "cellules_de_letalon",
                "creusent_sur_letalon_avec_frontiere", "profondeur_mediane_du_rouleau",
                "profondeur_de_letalon_sans_frontiere", "profondeur_de_letalon_avec_frontiere",
                "profondeur_a_la_borne_de_179", "largeur_mediane_du_rouleau",
                "largeur_de_letalon_avec_frontiere", "creux_dont_les_deux_cotes_sont_diriges",
                "creux_dont_aucun_cote_nest_dirige", "ecart_median_aux_creux_deg",
                "ecart_de_letalon_avec_frontiere_deg", "lecart_aux_creux_vaut_letalon_fois",
                "la_bascule_mediane_de_176_deg",
                "lecart_aux_creux_vaut_la_bascule_de_176_fois", "il_creuse_plus_que_le_hasard",
                "il_creuse_plus_quun_fond_sans_frontiere",
                "sa_profondeur_est_celle_dune_frontiere",
                "ses_creux_separent_deux_cotes_diriges"):
        print(f"     {cle:<48} {v.get(cle)}")


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    vx, pas = float(C.VOXEL_FIN_UM), float(C.PAS_UM)
    n = 109

    # ⭐⭐⭐⭐ CE QUE LE CREUX SEPARE, SUR UNE MATIERE DONT LA REPONSE EST CONSTRUITE : deux cotes
    # diriges et un quart de tour entre eux. La reponse est connue AVANT la mesure.
    pose, large = 54, 5
    cote = [[20.0, 0.9]] * pose + [[110.0, 0.9]] * (n - pose)
    lu = ce_que_le_creux_separe(cote, pose, large)
    v("les deux côtés d'une frontière construite sont dirigés", lu["les_deux_cotes_sont_diriges"],
      f"{lu['gauche_est_dirigee']} / {lu['droite_est_dirigee']}")
    v("et l'écart entre eux est le quart de tour",
      lu["ecart_deg"] is not None and abs(lu["ecart_deg"] - 90.0) < 1e-6, str(lu["ecart_deg"]))

    # ⚠⚠ UN COTE SANS TEXTURE N'EST PAS DIRIGE, ET C'EST CE QUI SEPARE UN INTERSTICE D'UNE
    # FRONTIERE. Le cote gauche porte des orientations tirees au hasard sous le plancher de
    # coherence : `174` le refuse, donc le lecteur doit le dire.
    r = np.random.default_rng(GRAINE)
    muet = ([[float(a), 0.02] for a in r.uniform(0.0, 180.0, pose)]
            + [[110.0, 0.9]] * (n - pose))
    lu2 = ce_que_le_creux_separe(muet, pose, large)
    v("un côté sans texture n'est pas dirigé", not lu2["gauche_est_dirigee"],
      str(lu2["angle_a_gauche_deg"]))
    v("et le creux ne sépare alors pas deux côtés dirigés",
      not lu2["les_deux_cotes_sont_diriges"])
    v("l'écart n'est pas rendu quand un côté manque", lu2["ecart_deg"] is None,
      str(lu2["ecart_deg"]))

    # ⭐⭐⭐⭐ LE CHEMIN PHYSIQUE, ET C'EST LUI QUI DONNE LEUR ECHELLE AUX DEUX ETALONS : une feuille
    # d'UN SEUL pli ne creuse pas au bruit qui correspond au rouleau, une feuille de DEUX creuse et
    # son creux separe un quart de tour.
    fixture = ce_que_la_fixture_a_rendu()
    v("la mesure de `179` donne le recouvrement et l'échelle", fixture is not None)
    if fixture is not None:
        v("le recouvrement relu est celui que `179` a encadré",
          fixture["recouvrement_um"] > 0.0 and fixture["profondeur_a_la_borne"] > 0.0,
          str(fixture))
        for plis, attendu in ((1, False), (PLIS_DE_LA_FIXTURE, True)):
            creuse, ecarts = 0, []
            for k in range(3):
                dec = pas * k / 3.0
                courbe = courbe_de_la_fixture(n, dec, CONTRASTE_DE_LA_FIXTURE, plis, vx, pas,
                                              transition_um=fixture["recouvrement_um"],
                                              bruit=float(max(BRUITS)))
                x = lire_un_chunk(courbe, PERMUTATIONS, GRAINE)
                if x["gagnant"] == "empilement":
                    creuse += 1
                    e = x["ce_que_le_creux_separe"]["ecart_deg"]
                    if e is not None:
                        ecarts.append(float(e))
            v(f"à {plis} pli(s) et au bruit le plus fort, la fixture "
              f"{'creuse' if attendu else 'ne creuse pas'}",
              (creuse == 3) if attendu else (creuse == 0), f"{creuse}/3")
            if attendu:
                v("et son creux sépare un quart de tour",
                  bool(ecarts) and abs(float(statistics.median(ecarts)) - 90.0) < 5.0,
                  str(ecarts))

    # ⚠⚠ LE BRUIT DE COMPARAISON EST DERIVE : le barreau dont la coherence est la plus proche, et
    # les egalites tranchees par le bruit le plus faible. Exerce sur une liste FABRIQUEE, donc la
    # reponse est connue avant.
    faux = [{"plis": 1, "bruit": 0.0, "coherence_mediane": 1.0},
            {"plis": 1, "bruit": 8.0, "coherence_mediane": 0.40},
            {"plis": 1, "bruit": 16.0, "coherence_mediane": 0.16},
            {"plis": 2, "bruit": 8.0, "coherence_mediane": 0.16}]
    v("le bruit apparié est le plus proche en cohérence",
      le_bruit_qui_correspond(faux, 0.155) == 16.0, str(le_bruit_qui_correspond(faux, 0.155)))
    v("et il est apparié sur l'étalon SANS frontière",
      le_bruit_qui_correspond(faux, 0.42) == 8.0, str(le_bruit_qui_correspond(faux, 0.42)))
    v("une égalité se tranche par le bruit le plus faible",
      le_bruit_qui_correspond([{"plis": 1, "bruit": 8.0, "coherence_mediane": 0.2},
                               {"plis": 1, "bruit": 16.0, "coherence_mediane": 0.2}], 0.2) == 8.0)

    # ⭐⭐⭐⭐ LES TROIS ENONCES DU VERDICT SONT EXERCES SUR DES ENTREES FABRIQUEES, chacune
    # construite pour qu'UN SEUL bascule. Sans cela, « il creuse plus qu'un fond » serait une
    # phrase qu'aucune mesure ne peut contredire.
    def _segment(chunks, creusent, profondeur, diriges):
        return {"decidable": True, "chunks_lus": int(chunks),
                "chunks_qui_creusent": int(creusent), "coherence_mediane": 0.16,
                "profondeur_mediane": float(profondeur), "largeur_mediane": 7,
                "lignes": [{"gagnant": "empilement",
                            "ce_que_le_creux_separe": {
                                "les_deux_cotes_sont_diriges": bool(i < diriges),
                                "gauche_est_dirigee": bool(i < diriges),
                                "droite_est_dirigee": True, "ecart_deg": 30.0}}
                           for i in range(int(creusent))]}

    def _etalons(creusent_sans, profondeur_avec):
        return [{"plis": 1, "bruit": 16.0, "coherence_mediane": 0.16, "cellules": 12,
                 "chunks_qui_creusent": int(creusent_sans),
                 "profondeur_mediane": (0.5 if creusent_sans else None),
                 "largeur_mediane": 7, "ecart_median_deg": 40.0},
                {"plis": PLIS_DE_LA_FIXTURE, "bruit": 16.0, "coherence_mediane": 0.13,
                 "cellules": 12, "chunks_qui_creusent": 12,
                 "profondeur_mediane": float(profondeur_avec), "largeur_mediane": 7,
                 "ecart_median_deg": 88.0}]

    ref = {"recouvrement_um": 45.6, "profondeur_a_la_borne": 0.7166, "largeur_a_la_borne": 5,
           "il_vaut_le_pli_fois": 0.5278}
    plein = juger([_segment(20, 20, 0.80, 15)], _etalons(0, 0.74), ref, PERMUTATIONS)
    v("un rouleau qui creuse partout dépasse le hasard", plein["il_creuse_plus_que_le_hasard"])
    v("il dépasse un fond sans frontière qui ne creuse pas",
      plein["il_creuse_plus_quun_fond_sans_frontiere"])
    v("sa profondeur est celle d'une frontière quand elle l'atteint",
      plein["sa_profondeur_est_celle_dune_frontiere"])
    v("et ses creux séparent deux côtés dirigés à la majorité",
      plein["ses_creux_separent_deux_cotes_diriges"])
    v("le compte attendu par hasard est le nombre de chunks sur K+1",
      abs(plein["chunks_attendus_par_hasard"] - 20.0 / (PERMUTATIONS + 1.0)) < 1e-9,
      str(plein["chunks_attendus_par_hasard"]))

    # ⚠⚠⚠ ET CHAQUE ENONCE TOMBE SEUL SUR L'ENTREE QUI LE VISE : un fond qui creuse AUTANT que le
    # rouleau retire le second, une profondeur sous l'etalon retire le troisieme, une majorite de
    # creux sans deux cotes diriges retire le quatrieme. Sans ces trois, un verdict qui repondrait
    # « oui » a tout passerait la batterie.
    sourd = juger([_segment(20, 20, 0.80, 15)], _etalons(12, 0.74), ref, PERMUTATIONS)
    v("un fond qui creuse autant retire le second énoncé",
      not sourd["il_creuse_plus_quun_fond_sans_frontiere"])
    plat = juger([_segment(20, 20, 0.30, 15)], _etalons(0, 0.74), ref, PERMUTATIONS)
    v("une profondeur sous l'étalon retire le troisième",
      not plat["sa_profondeur_est_celle_dune_frontiere"])
    muette = juger([_segment(20, 20, 0.80, 2)], _etalons(0, 0.74), ref, PERMUTATIONS)
    v("des creux qui ne séparent rien retirent le quatrième",
      not muette["ses_creux_separent_deux_cotes_diriges"])
    rare = juger([_segment(200, 1, 0.80, 1)], _etalons(0, 0.74), ref, PERMUTATIONS)
    v("un rouleau qui creuse moins que le hasard retire le premier",
      not rare["il_creuse_plus_que_le_hasard"],
      f"{rare['chunks_qui_creusent']} contre {rare['chunks_attendus_par_hasard']}")

    # ⚠ UN SEGMENT MUET SE DIT AU LIEU D'ETRE COMPTE : un verdict rendu sans chunk lisible serait
    # un nombre sans matiere derriere lui.
    vide = juger([{"decidable": False, "segment": "x", "raison": "le volume ne répond pas"}],
                 _etalons(0, 0.74), ref, PERMUTATIONS)
    v("aucun segment lisible rend un verdict indécidable", not vide["decidable"],
      str(vide.get("raison")))

    nom = "le_rouleau_creuse_t_il.py"
    if echecs:
        print(f"{nom}   {len(echecs)} ÉCHECS sur {faits}")
        for e in echecs:
            print(f"   ✗ {e}")
        return 1
    print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--segments", type=int, default=SEGMENTS)
    p.add_argument("--cote", type=int, default=COTE_DU_TREILLIS)
    p.add_argument("--permutations", type=int, default=PERMUTATIONS)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.segments, a.cote, a.permutations)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
