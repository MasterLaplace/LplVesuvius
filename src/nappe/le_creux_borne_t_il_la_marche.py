"""Le creux de cohérence borne-t-il la marche — une référence ABSOLUE, enfin ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `R4-P48` QUI LE NOMME. `199` a établi que les pas d'une couture
à l'autre **se compensent** — il n'y a aucun biais à retirer — et que la marche au hasard qui en
résulte perd pourtant un **demi-feuillet en seize millimètres**. Une correction DIFFÉRENTIELLE ne
peut donc rien : de proche en proche, elle n'a rien à corriger localement. Il faut quelque chose qui
dise, en CHAQUE chunk et **sans regarder ses voisins**, où est le feuillet.

⭐⭐⭐⭐ OR `180` L'A DÉJÀ MESURÉ : la cohérence du tenseur de structure **creuse** à une frontière de
pli, et vingt-sept chunks sur vingt-sept y dépassent toutes leurs permutations. C'est un repère
**absolu** — il ne se déduit d'aucun voisin — et rien dans la chaîne ne l'a encore utilisé pour
**borner** une marche.

⚠⚠⚠ ET LE PIÈGE EST NOMMÉ D'AVANCE : un repère qui MANQUE dans un chunk sur deux ne borne rien. Le
compte de chunks où le creux est lisible se publie donc **avant** tout verdict — `180` le donne sur
vingt-sept chunks d'un treillis, jamais sur une rangée entière.

⚠⚠ ET UNE SECONDE LIMITE, TOUT AUSSI PRÉVISIBLE : un creux désigne UNE frontière, pas LAQUELLE. Deux
chunks voisins peuvent se caler sur deux frontières différentes séparées d'un pli, et la trace
absolue saute alors d'un pli entier. Ces sauts sont **comptés**, jamais lissés.

Usage :
    uv run python src/nappe/le_creux_borne_t_il_la_marche.py --verifier
    uv run python src/nappe/le_creux_borne_t_il_la_marche.py \\
        --json docs/mesures/le_creux_borne_t_il_la_marche.json
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

from fiber_orientation import orientation_profile  # noqa: E402
from la_coherence_creuse_t_elle_a_la_frontiere import le_verdict_du_creux  # noqa: E402
from la_derive_saccumule_t_elle import LA_PAUSE_ENTRE_ESSAIS, la_ligne_declaree  # noqa: E402
from la_recette_posee_sur_le_rouleau import (DELAI, PERMUTATIONS,  # noqa: E402
                                             PLANCHER_DE_COHERENCE)
from ou_le_maillage_quitte_t_il_son_feuillet import (ABSENT_DU_DEPOT,  # noqa: E402
                                                     LE_RESEAU_A_ECHOUE,
                                                     le_segment_declare,
                                                     les_pannes_de_reseau, un_chunk)
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LA_MARCHE_A_RENDU = MESURES / "la_derive_saccumule_t_elle.json"
GRAINE = 20261008

LA_QUESTION_DECLAREE = ("le creux borne-t-il la marche, là où le recalage de proche en proche "
                        "ne le peut pas ?")


def la_courbe_dun_bloc(bloc: np.ndarray) -> tuple:
    """La courbe (angle, cohérence) d'un cube, avec le FILTRE DU PRODUCTEUR.

    ⚠⚠ LE FILTRE EST CELUI DE `14` ET DE `176`, RELU ET NON CHOISI : un chunk est retenu quand au
    moins un quart de ses couches dépasse le plancher de cohérence. Un filtre plus large ferait
    entrer des chunks que le producteur n'a jamais lus, et la comparaison a ses conclusions cesserait
    d'en etre une.
    """
    b = np.asarray(bloc)
    ang, coh = orientation_profile(b)
    if int((np.asarray(coh) > PLANCHER_DE_COHERENCE).sum()) < b.shape[0] // 4:
        return None, "trop peu texturé"
    return [[float(a), float(c)] for a, c in zip(ang, coh)], None


def le_repere_dun_chunk(courbe, permutations: int = PERMUTATIONS,
                        graine: int = GRAINE) -> dict:
    """Le creux de ce chunk, s'il en a un que ses mélanges ne rendent pas.

    ⭐⭐⭐⭐ C'EST LE REPERE ABSOLU : il se lit dans le chunk SEUL, sans jamais regarder un voisin.
    C'est toute la difference avec `199`, ou chaque pas etait une relation entre DEUX chunks.

    ⚠ `le_verdict_du_creux` est celui de `179`, avec sa statistique de famille — la largeur du creux
    est une liberte de choix, et elle y est payee.
    """
    lu = le_verdict_du_creux(courbe, None, permutations, graine)
    return {"lisible": bool(lu.get("frontiere_lue") is not None),
            "la_couche": (None if lu.get("frontiere_lue") is None
                          else int(lu["frontiere_lue"])),
            # ⚠⚠⚠ LA PROFONDEUR VIENT DE LA COURBE ELLE-MEME, PAS D'UNE CLEF DU LECTEUR : la
            # premiere version la lisait dans la sortie de `le_verdict_du_creux`, qui ne la porte
            # pas toujours, et la mesure a rendu ZERO couche. Mes sondes ne l'avaient pas vu parce
            # que leurs fixtures fournissaient le champ elles-memes — elles testaient la fixture.
            "les_couches": int(len(courbe)),
            "la_profondeur": lu.get("profondeur"),
            "la_largeur": lu.get("largeur")}


def lecart_type_dune_loi_uniforme(couches: int) -> float:
    """L'écart-type qu'une couche TIRÉE AU HASARD dans le cube aurait — la borne du non-informatif.

    ⭐⭐⭐⭐ SANS CE NOMBRE, « ECART-TYPE 29,1 VOXELS » NE SE LIT PAS. Un repere qui designerait une
    couche au hasard dans un cube de `n` couches rend un ecart-type de `n/√12` ; comparer l'observe a
    cette valeur dit d'un seul coup s'il porte une position ou seulement la presence d'une
    frontiere. Le nombre est exact et sans reglage.
    """
    return float(couches) / (12.0 ** 0.5)


def la_trace_absolue(reperes: dict, colonnes: list[int]) -> dict:
    """La couche du creux, colonne après colonne — et ce qu'elle fait.

    ⭐⭐⭐⭐ SI LE MAILLAGE TENAIT SON FEUILLET, CETTE TRACE SERAIT PLATE. Sa variation EST l'écart
    absolu, et elle ne s'accumule pas par construction : chaque point est lu dans son chunk seul.

    ⚠⚠ LES SAUTS DE PLUS D'UNE DEMI-PERIODE SONT COMPTES A PART : un creux designe UNE frontiere,
    pas LAQUELLE, donc deux chunks voisins peuvent se caler sur deux frontieres separees d'un pli.
    Lisser ces sauts inventerait une continuite que la mesure ne voit pas.
    """
    lus = [(int(c), int(reperes[c]["la_couche"])) for c in colonnes
           if c in reperes and reperes[c].get("lisible")]
    if len(lus) < 2:
        return {"decidable": False, "raison": "moins de deux repères lisibles"}
    cs = np.asarray([x[1] for x in lus], dtype=float)
    pas = np.diff(cs)
    sauts = int(np.sum(np.abs(pas) > DEMI_PAS_EN_VOXELS))
    profs = [int(reperes[c]["les_couches"]) for c, _k in lus
             if reperes[c].get("les_couches")]
    couches = int(np.median(profs)) if profs else 0
    uni = lecart_type_dune_loi_uniforme(couches) if couches else None
    return {"decidable": True, "les_reperes": len(lus),
            "les_couches_du_cube": int(couches),
            "lecart_type_si_uniforme_en_voxels": (None if uni is None else round(uni, 4)),
            "le_rapport_a_luniforme": (None if not uni else
                                       round(float(np.std(cs)) / uni, 4)),
            "les_colonnes": [int(x[0]) for x in lus],
            "la_trace_en_couches": [int(x[1]) for x in lus],
            "la_couche_mediane": round(float(np.median(cs)), 4),
            "lecart_type_en_voxels": round(float(np.std(cs)), 4),
            "lecart_type_en_plis": round(float(np.std(cs)) / PAS_EN_VOXELS, 6),
            "lexcursion_en_voxels": int(np.max(cs) - np.min(cs)),
            "lexcursion_en_plis": round(float(np.max(cs) - np.min(cs)) / PAS_EN_VOXELS, 6),
            "les_sauts_de_plus_dun_demi_pli": sauts,
            "la_part_qui_saute": round(float(sauts) / max(1, len(pas)), 6),
            "le_pas_quadratique_en_voxels": round(float(np.sqrt(float(np.mean(pas * pas)))), 4)}


def ce_que_la_marche_a_rendu(chemin: Path = CE_QUE_LA_MARCHE_A_RENDU) -> dict:
    """Ce que `199` a publié sur la MÊME rangée — relu, jamais recalculé.

    ⚠⚠⚠ LA COMPARAISON EST LA RAISON D'ETRE DE CETTE TRANCHE, donc les deux nombres compares doivent
    venir de leurs producteurs respectifs. Recalculer la trace differentielle ici en ferait une
    seconde definition, libre de ne plus s'accorder avec celle qui est publiee.
    """
    if not Path(chemin).is_file():
        return {"decidable": False, "raison": "la mesure de `199` est absente"}
    d = json.loads(Path(chemin).read_text(encoding="utf-8"))
    m = d.get("la_marche") or {}
    if not m.get("decidable"):
        return {"decidable": False, "raison": "la marche de `199` est indécidable"}
    return {"decidable": True,
            "lexcursion_en_plis": m.get("lexcursion_maximale_en_plis"),
            "le_pas_quadratique_en_voxels": m.get("le_pas_quadratique_en_voxels"),
            "les_pas": m.get("les_pas"),
            "la_rangee": (d.get("la_ligne") or {}).get("la_rangee")}


def juger(trace: dict, differentiel: dict) -> dict:
    """Le creux borne-t-il la marche ? La comparaison est DÉCLARÉE et unique.

    ⚠⚠⚠ CE QUI EST COMPARE EST L'EXCURSION, PAS LE PAS : un repere absolu n'a pas de « pas » au sens
    de `199` — chaque point est independant des autres — donc la seule quantite qui se compare entre
    les deux lectures est jusqu'ou la surface s'eloigne de son depart.

    ⚠⚠ ET LA COMPARAISON NE VAUT QUE SI LE REPERE EST LISIBLE ASSEZ SOUVENT : un repere absent dans
    un chunk sur deux ne borne rien, et le compte est publie avant le verdict.
    """
    if not trace.get("decidable") or not differentiel.get("decidable"):
        return {"decidable": False, "raison": "une des deux lectures manque"}
    a = float(trace["lexcursion_en_plis"])
    b = float(differentiel["lexcursion_en_plis"])
    return {"decidable": True,
            "lexcursion_absolue_en_plis": round(a, 6),
            "lexcursion_differentielle_en_plis": round(b, 6),
            "le_rapport": round(a / b, 4) if b > 0 else None,
            "le_creux_borne_la_marche": bool(a < b)}


def une_pile_a_frontiere(couches: int, colonnes: int, couche_de_la_frontiere: float,
                         bruit: float, graine: int, largeur: int = 9) -> np.ndarray:
    """Un cube dont la cohérence CREUSE à une couche posée — la fixture du repère.

    ⚠ Ce que la fixture fabrique est la COURBE, pas la matiere : `orientation_profile` est teste
    ailleurs, et le reperage ne depend que de la courbe qu'il recoit.
    """
    r = _rng(graine)
    z = np.arange(int(couches), dtype=float)
    creux = np.exp(-0.5 * ((z - float(couche_de_la_frontiere)) / (largeur / 2.0)) ** 2)
    coh = 0.6 - 0.45 * creux + r.normal(0.0, float(bruit), size=int(couches))
    return [[0.0, float(max(0.0, c))] for c in coh]


def la_part_vue(couche_posee: float, bruit: float, replicats: int, permutations: int,
                graine: int, tolerance: int = 4) -> dict:
    """La part des réplicats où le repère tombe à la couche posée, à `tolerance` près."""
    vus = 0
    for k in range(int(replicats)):
        c = une_pile_a_frontiere(109, 1, couche_posee, bruit, int(graine) + k)
        rp = le_repere_dun_chunk(c, permutations, int(graine) + k)
        vus += int(bool(rp["lisible"])
                   and abs(int(rp["la_couche"]) - float(couche_posee)) <= int(tolerance))
    return {"vus": int(vus), "replicats": int(replicats),
            "la_part": float(vus) / float(replicats)}


def sur_letalon(permutations: int = PERMUTATIONS, graine: int = GRAINE,
                replicats: int = 20, bruits=(0.02, 0.05, 0.1, 0.2)) -> dict:
    """Le repère retrouve-t-il une frontière posée, et se tait-il sur une courbe sans frontière ?

    ⚠⚠⚠ LES DEUX FACES SUR REPLICATS — la lecon de `198` et `199`. Une face negative jugee sur un
    tirage unique tombe du mauvais cote une fois sur vingt par construction.
    """
    courbe, trouve = [], None
    for b in bruits:
        x = la_part_vue(54.0, float(b), replicats, permutations, graine)
        courbe.append({"le_bruit": float(b), "part_des_replicats": float(x["la_part"])})
        if trouve is None and x["la_part"] >= 1.0:
            trouve = float(b)
    r = _rng(graine + 3)
    faux = 0
    for k in range(int(replicats)):
        plate = [[0.0, float(max(0.0, 0.6 + v))]
                 for v in r.normal(0.0, 0.05, size=109)]
        faux += int(bool(le_repere_dun_chunk(plate, permutations, graine + k)["lisible"]))
    garantie = 1.0 / (int(permutations) + 1)
    return {"la_courbe": courbe, "le_bruit_qui_tient": trouve,
            "replicats": int(replicats),
            "le_taux_de_faux": round(float(faux) / float(replicats), 4),
            "les_faux": int(faux), "la_garantie": round(float(garantie), 4),
            "letalon_separe": bool(trouve is not None
                                   and float(faux) / float(replicats)
                                   <= float(garantie) + 1e-12)}


def la_ligne(volume: dict, delai: float = DELAI, colonnes: int | None = None,
             permutations: int = PERMUTATIONS, graine: int = GRAINE,
             ouvrir=None, meta=None) -> dict:
    """Le repère absolu de chaque chunk d'une rangée — la MÊME que `199`."""
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    ligne = la_ligne_declaree(gy)
    voulues = list(range(gx if colonnes is None else min(int(colonnes), gx)))
    prendre = ouvrir or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, None,
                                                 pause=LA_PAUSE_ENTRE_ESSAIS))
    reperes, refus, reprises = {}, {}, 0
    for cx in voulues:
        bloc, pourquoi = prendre(int(ligne), int(cx))
        if bloc is not None and pourquoi and str(pourquoi).startswith("repris"):
            reprises += int(str(pourquoi).split()[-1])
            pourquoi = None
        if bloc is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        b = np.asarray(bloc)
        if float(b.max()) <= 0.0:
            refus["vide"] = refus.get("vide", 0) + 1
            continue
        courbe, quoi = la_courbe_dun_bloc(b)
        if courbe is None:
            refus[quoi] = refus.get(quoi, 0) + 1
            continue
        reperes[int(cx)] = le_repere_dun_chunk(courbe, permutations, graine)
    return {"decidable": bool(reperes), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_rangee": int(ligne),
            "colonnes_demandees": len(voulues), "colonnes_lues": len(reperes),
            "les_reperes_lisibles": int(sum(1 for x in reperes.values() if x["lisible"])),
            "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "reperes": reperes, "les_colonnes": voulues}


def mesurer(delai: float = DELAI, permutations: int = PERMUTATIONS, graine: int = GRAINE,
            replicats: int = 20, colonnes: int | None = None, ouvrir=None,
            meta=None) -> dict:
    """La trace absolue le long de la rangée, et la comparaison déclarée avec `199`."""
    v = le_segment_declare()
    if v is None:
        return {"decidable": False, "raison": "aucun volume recensé"}
    lg = la_ligne(v, delai, colonnes, permutations, graine, ouvrir, meta)
    if not lg.get("decidable"):
        return {"decidable": False, "raison": lg.get("raison", "la ligne est vide")}
    pannes = les_pannes_de_reseau(lg.get("refuses"))
    if pannes:
        return {"decidable": False,
                "raison": f"{pannes} chunks perdus par le réseau — une rangée dont le fil est "
                          f"tombé n'est pas comparable à celle de `199`",
                "la_ligne": {k: x for k, x in lg.items() if k not in ("reperes",
                                                                     "les_colonnes")}}
    trace = la_trace_absolue(lg["reperes"], lg["les_colonnes"])
    diff = ce_que_la_marche_a_rendu()
    return {
        "graine": int(graine), "permutations": int(permutations),
        "la_question_declaree": LA_QUESTION_DECLAREE,
        "le_pas_dun_pli_en_voxels": round(float(PAS_EN_VOXELS), 4),
        "la_demi_periode_en_voxels": int(DEMI_PAS_EN_VOXELS),
        "le_plancher_de_coherence": float(PLANCHER_DE_COHERENCE),
        "la_ligne": {k: x for k, x in lg.items() if k not in ("reperes", "les_colonnes")},
        "la_trace_absolue": trace,
        "ce_que_199_a_rendu": diff,
        "le_verdict": juger(trace, diff),
        "letalon": sur_letalon(permutations, graine, replicats),
    }


def afficher(r: dict) -> None:
    if not r.get("decidable", True):
        print(f"LE CREUX BORNE-T-IL LA MARCHE   indécidable : {r.get('raison')}")
        return
    lg, t = r["la_ligne"], r["la_trace_absolue"]
    ve, d9, e = r["le_verdict"], r["ce_que_199_a_rendu"], r["letalon"]
    print(f"LE CREUX BORNE-T-IL LA MARCHE   segment {lg['segment']} · rangée {lg['la_rangee']} · "
          f"{lg['colonnes_lues']} chunks lus sur {lg['colonnes_demandees']} · refus "
          f"{lg['refuses'] or '—'}")
    print(f"  LES REPÈRES       {lg['les_reperes_lisibles']} lisibles sur {lg['colonnes_lues']} "
          f"chunks lus")
    if t.get("decidable"):
        print(f"  LA TRACE          médiane {t['la_couche_mediane']} · écart-type "
              f"{t['lecart_type_en_voxels']} vx ({t['lecart_type_en_plis']} pli) · excursion "
              f"{t['lexcursion_en_voxels']} vx ({t['lexcursion_en_plis']} pli)")
        print(f"  CONTRE L'UNIFORME {t['lecart_type_si_uniforme_en_voxels']} vx si la couche "
              f"était tirée au hasard dans {t['les_couches_du_cube']} · rapport "
              f"{t['le_rapport_a_luniforme']}")
        print(f"  LES SAUTS         {t['les_sauts_de_plus_dun_demi_pli']} de plus d'un demi-pli "
              f"({t['la_part_qui_saute']}) · pas quadratique "
              f"{t['le_pas_quadratique_en_voxels']} vx")
    else:
        print(f"  LA TRACE          indécidable : {t.get('raison')}")
    if ve.get("decidable"):
        print(f"  LE VERDICT        absolue {ve['lexcursion_absolue_en_plis']} pli contre "
              f"différentielle {ve['lexcursion_differentielle_en_plis']} pli · rapport "
              f"{ve['le_rapport']} · borne {ve['le_creux_borne_la_marche']}")
    print(f"  L'ÉTALON          sépare {e['letalon_separe']} · bruit tenu "
          f"{e['le_bruit_qui_tient']} · taux de faux {e['le_taux_de_faux']} pour "
          f"{e['la_garantie']} garantis · courbe " + " · ".join(
              f"{x['le_bruit']:g}→{x['part_des_replicats']:g}" for x in e["la_courbe"]))


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    v("★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★ le plancher de cohérence est RELU du producteur",
      abs(PLANCHER_DE_COHERENCE - 0.15) < 1e-12, str(PLANCHER_DE_COHERENCE))
    v("★★ la rangée est la MÊME que celle de `199`", la_ligne_declaree(396) == 198)

    # ⭐⭐⭐⭐ LE REPERE SE LIT DANS LE CHUNK SEUL, ET IL RETROUVE UNE FRONTIERE POSEE.
    for pose in (30, 54, 78):
        c = une_pile_a_frontiere(109, 1, float(pose), 0.02, 11)
        rp = le_repere_dun_chunk(c, 19, 11)
        v(f"★★★★ le repère à {pose} porte la profondeur de SA courbe, pas une clef du lecteur",
          rp["les_couches"] == len(c), f"{rp['les_couches']} pour {len(c)} couches")
        v(f"★★★★ une frontière posée à {pose} est retrouvée",
          rp["lisible"] and abs(int(rp["la_couche"]) - pose) <= 4,
          f"lu {rp['la_couche']}")
    r0 = _rng(4)
    plate = [[0.0, float(0.6 + x)] for x in r0.normal(0.0, 0.05, size=109)]
    v("★★★★ et une courbe SANS frontière ne rend aucun repère",
      not le_repere_dun_chunk(plate, 19, 11)["lisible"])
    v("★★★ un repère illisible ne rend AUCUNE couche, jamais zéro",
      le_repere_dun_chunk(plate, 19, 11)["la_couche"] is None)
    v("★★★★ mais il porte QUAND MÊME la profondeur de sa courbe",
      le_repere_dun_chunk(plate, 19, 11)["les_couches"] == 109,
      str(le_repere_dun_chunk(plate, 19, 11)["les_couches"]))
    v("★★★ et une courbe plus courte le dit",
      le_repere_dun_chunk(plate[:60], 19, 11)["les_couches"] == 60)

    # ⚠⚠⚠ LE FILTRE DU PRODUCTEUR ECARTE UN CUBE TROP PEU TEXTURE.
    v("★★★ un cube sans texture est refusé par le filtre du producteur",
      la_courbe_dun_bloc(np.zeros((109, 16, 16), dtype=np.uint8))[1] == "trop peu texturé")

    # ⭐⭐⭐⭐ LA TRACE ABSOLUE NE S'ACCUMULE PAS, ET SES SAUTS SE COMPTENT.
    # ⭐⭐⭐⭐ L'ECART-TYPE D'UNE LOI UNIFORME EST LA BORNE DU NON-INFORMATIF, ET IL SE VERIFIE.
    v("★★★★ une couche tirée au hasard dans 109 couches a un écart-type de n sur racine de douze",
      abs(lecart_type_dune_loi_uniforme(109) - 109.0 / (12.0 ** 0.5)) < 1e-9,
      str(round(lecart_type_dune_loi_uniforme(109), 4)))
    v("★★★ et il croît avec la profondeur du cube",
      lecart_type_dune_loi_uniforme(218) > lecart_type_dune_loi_uniforme(109))

    plats = {c: {"lisible": True, "la_couche": 54, "les_couches": 109} for c in range(10)}
    t = la_trace_absolue(plats, list(range(10)))
    v("★★★★ une trace plate a une excursion nulle", t["lexcursion_en_voxels"] == 0,
      str(t["lexcursion_en_voxels"]))
    v("★★★ et aucun saut", t["les_sauts_de_plus_dun_demi_pli"] == 0)
    v("★★★★ une trace constante est loin sous l'uniforme, donc elle PORTE une position",
      t["le_rapport_a_luniforme"] is not None and t["le_rapport_a_luniforme"] < 0.05,
      str(t["le_rapport_a_luniforme"]))
    rr2 = _rng(21)
    disperse = {c: {"lisible": True, "la_couche": int(rr2.integers(0, 109)),
                    "les_couches": 109} for c in range(200)}
    td = la_trace_absolue(disperse, list(range(200)))
    v("★★★★ tandis qu'une trace TIRÉE AU HASARD tombe sur l'uniforme, donc elle n'en porte aucune",
      abs(td["le_rapport_a_luniforme"] - 1.0) < 0.12, str(td["le_rapport_a_luniforme"]))

    saute = {c: {"lisible": True, "la_couche": 54 if c < 5 else 54 + int(PAS_EN_VOXELS),
                 "les_couches": 109} for c in range(10)}
    ts = la_trace_absolue(saute, list(range(10)))
    v("★★★★ un saut d'un pli entier est COMPTÉ, jamais lissé",
      ts["les_sauts_de_plus_dun_demi_pli"] == 1, str(ts["les_sauts_de_plus_dun_demi_pli"]))
    v("★★★ et il gonfle l'excursion d'un pli",
      abs(ts["lexcursion_en_plis"] - 1.0) < 0.02, str(ts["lexcursion_en_plis"]))
    v("★★★ les repères illisibles sont écartés, jamais défautés",
      la_trace_absolue({0: {"lisible": True, "la_couche": 10, "les_couches": 109},
                        1: {"lisible": False, "la_couche": None, "les_couches": 109},
                        2: {"lisible": True, "la_couche": 12, "les_couches": 109}},
                       [0, 1, 2])["les_reperes"] == 2)
    v("★★ moins de deux repères est indécidable",
      la_trace_absolue({0: {"lisible": True, "la_couche": 5, "les_couches": 109}},
                       [0]).get("decidable") is False)

    # ⚠⚠⚠ CE QUE `199` A RENDU EST RELU, JAMAIS RECALCULE.
    d9 = ce_que_la_marche_a_rendu()
    v("★★★★ l'excursion de `199` est relue de sa mesure",
      d9.get("decidable") and d9["lexcursion_en_plis"] is not None,
      str(d9.get("lexcursion_en_plis")))
    v("★★★ et elle porte sur la MÊME rangée", d9.get("la_rangee") == la_ligne_declaree(396),
      str(d9.get("la_rangee")))
    v("★★★ une mesure absente ne se fabrique pas",
      ce_que_la_marche_a_rendu(Path("/n/existe/pas.json")).get("decidable") is False)

    # ⭐⭐⭐⭐ LE VERDICT COMPARE LES DEUX EXCURSIONS, ET SES DEUX FACES.
    v("★★★★ une trace absolue plus serrée BORNE la marche",
      juger({"decidable": True, "lexcursion_en_plis": 0.2},
            {"decidable": True, "lexcursion_en_plis": 1.3})["le_creux_borne_la_marche"])
    v("★★★★ et une trace plus large ne la borne PAS",
      not juger({"decidable": True, "lexcursion_en_plis": 2.0},
                {"decidable": True, "lexcursion_en_plis": 1.3})["le_creux_borne_la_marche"])
    v("★★★ le rapport des deux est publié",
      abs(juger({"decidable": True, "lexcursion_en_plis": 0.65},
                {"decidable": True, "lexcursion_en_plis": 1.3})["le_rapport"] - 0.5) < 1e-9)
    v("★★ une lecture manquante rend le verdict indécidable",
      juger({"decidable": False}, {"decidable": True,
                                   "lexcursion_en_plis": 1.0}).get("decidable") is False)

    # ⭐⭐⭐⭐ L'ETALON, SES DEUX FACES SUR REPLICATS.
    e = sur_letalon(19, 11, 8, bruits=(0.02, 0.2))
    v("★★★★ l'étalon sépare ses deux faces", e["letalon_separe"],
      f"bruit tenu {e['le_bruit_qui_tient']}, taux de faux {e['le_taux_de_faux']}")
    v("★★★ le bruit retenu est vu à TOUS les réplicats",
      e["le_bruit_qui_tient"] is not None
      and la_part_vue(54.0, e["le_bruit_qui_tient"], 8, 19, 11)["la_part"] >= 1.0,
      str(e["le_bruit_qui_tient"]))
    v("★★★★ et la face SANS frontière tient la garantie",
      e["le_taux_de_faux"] <= e["la_garantie"] + 1e-12,
      f"{e['le_taux_de_faux']} contre {e['la_garantie']}")
    v("★★★ la courbe entière est publiée", len(e["la_courbe"]) == 2,
      str([x["part_des_replicats"] for x in e["la_courbe"]]))

    # ⚠⚠⚠ LA LIGNE S'EXERCE SANS RESEAU, ET SES REFUS SE COMPTENT PAR LEUR RAISON.
    faux_meta = {"chunks": [109, 8, 16], "shape": [109, 8 * 5, 16 * 6], "dtype": "|u1"}
    rr = _rng(6)

    def _faux_ouvrir(absents=(), coupes=()):
        def _prendre(cy, cx):
            if (cy, cx) in coupes:
                return None, f"{LE_RESEAU_A_ECHOUE} : transport : coupure"
            if (cy, cx) in absents:
                return None, ABSENT_DU_DEPOT
            z = np.arange(109, dtype=float)[:, None, None]
            creux = np.exp(-0.5 * ((z - 54.0 - 2.0 * (int(cx) % 3)) / 5.0) ** 2)
            b = 180.0 * (1.0 - 0.7 * creux) * (
                1.0 + 0.4 * np.cos(np.arange(16, dtype=float)[None, None, :] / 2.0))
            return np.clip(b + rr.normal(0.0, 4.0, size=(109, 8, 16)), 0, 255).astype(
                np.uint8), None
        return _prendre

    lg = la_ligne({"segment": "S", "cle": "x"}, 0.01, None, 19, 11,
                  _faux_ouvrir(absents={(2, 3)}), faux_meta)
    v("★★★★ la ligne est la rangée médiane, la MÊME que `199`", lg["la_rangee"] == 2,
      f"{lg['la_rangee']} sur {lg['grille_de_chunks'][0]}")
    v("★★★ un chunk absent du dépôt est compté par sa raison",
      lg["refuses"].get(ABSENT_DU_DEPOT) == 1, str(lg["refuses"]))
    v("★★★★ et le compte de repères LISIBLES est publié à côté des chunks lus",
      "les_reperes_lisibles" in lg and lg["les_reperes_lisibles"] <= lg["colonnes_lues"],
      f"{lg['les_reperes_lisibles']} sur {lg['colonnes_lues']}")
    mc = mesurer(0.01, 19, 11, 4, None, _faux_ouvrir(coupes={(2, 1)}), faux_meta)
    v("★★★★ une rangée dont le RÉSEAU a lâché est REFUSÉE",
      mc.get("decidable") is False and "réseau" in str(mc.get("raison")),
      str(mc.get("raison"))[:90])

    nom = "le_creux_borne_t_il_la_marche.py"
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
    p.add_argument("--colonnes", type=int)
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(colonnes=a.colonnes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
