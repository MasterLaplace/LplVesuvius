"""Cinq rangées voisines désignent-elles la rangée fautive, là où trois ne le pouvaient pas ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES DEUX RANGÉES NOUVELLES NE SOIENT LUES. L'épreuve est celle de
`218`, importée et non réécrite ; ce fichier ne pose que ce qui change : quelles rangées, quelles
colonnes, et comment s'assurer que cinq rangées lues aujourd'hui sont comparables à trois lues hier.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P64`. `218` a trouvé qu'aux deux colonnes où tombent les
extrêmes de `217`, une rangée s'écarte seule pendant que les deux autres s'accordent — la forme exacte
d'un saut —, mais que trois rangées fabriquent cette forme par hasard : son épreuve ne voit pas, et
son étalon dit que des sauts de la taille observée sont vus trois fois sur douze à trois rangées et
douze fois sur douze à cinq. C'est la plus petite lecture neuve qui décide.

## Ce qui est dérivé, jamais choisi

⭐⭐⭐ LES RANGÉES. Leur nombre est celui que l'étalon de `218` rend — le plus petit qui voit partout en
résistant au piège —, relu dans son JSON. Elles sont centrées sur la rangée médiane du treillis de
`211`, relue elle aussi : la médiane et ses voisines de part et d'autre.

⭐⭐⭐ LES COLONNES. Celles où les cinq rangées ont toutes lu un pas — leur intersection. ⚠ Elles ne
sont plus limitées au plus long tronçon de chaque rangée comme chez `218`, parce que ce qu'il fallait
à `218` était ce que `211` avait publié ; ici tout est lu, et l'épreuve n'exige pas de contiguïté
puisque son nul rebrasse les colonnes. ⚠⚠ Les colonnes de `218` sont portées comme CONTRÔLE NOMMÉ :
la même épreuve restreinte à elles dit ce que cinq rangées rendent sur la matière exacte de `218`.

## Ce qui rend cinq rangées lues aujourd'hui comparables à trois lues hier

⚠⚠⚠ LES CINQ SONT LUES ENSEMBLE, PAR LE MÊME LECTEUR, et les trois que `211` avait déjà lues sont
RELUES. Mélanger des pas publiés hier à des pas lus aujourd'hui supposerait que rien n'a changé
entre-temps, ni le code, ni le dépôt. ⭐ La relecture en fait une vérification : sur les colonnes que
`211` publie, les pas relus doivent retomber sur les siens, à l'arrondi près du cumul — quatre
décimales, donc un pas relu à partir de deux positions arrondies s'écarte d'au plus deux dix-millièmes.
Une rangée qui ne retombe pas est REFUSÉE par son nom : comparer des rangées lues par deux lecteurs
différents serait `R4-L19` à l'échelle d'une lecture.

⚠⚠ UNE RANGÉE DONT LE FIL EST TOMBÉ EST REFUSÉE, comme chez `211` : des chunks perdus par le réseau
feraient des trous qui ne viennent pas de la matière.

## L'épreuve et l'étalon, importés

Anomalies centrées par colonne, blanchies par les bruits propres des CINQ rangées ; proximité à l'axe
d'une rangée ; colonnes fortes au-delà du quantile `1 - 1/n` d'un khi-deux à QUATRE degrés ; nul par
rebrassage des proximités. L'étalon est celui de `218`, repassé avec les bruits propres NOUVEAUX, le
même piège et des sauts de la même taille.

## Les issues, exclusives

- l'étalon ne tient pas : aucun verdict ;
- l'épreuve voit : les écarts extrêmes sont portés par une rangée à la fois, et cinq voisines la
  désignent — c'est ce qui remplace l'humain qui corrige le transfert ;
- elle ne voit pas et l'étalon la dit puissante à cinq rangées : ils sont portés par la colonne ;
- elle ne voit pas et l'étalon la dit aveugle : même cinq rangées ne décident pas.

Usage :
    uv run python src/nappe/cinq_rangees_designent_elles_la_fautive.py --verifier
    uv run python src/nappe/cinq_rangees_designent_elles_la_fautive.py \\
        --json docs/mesures/cinq_rangees_designent_elles_la_fautive.json
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

from combien_de_rangees_faut_il_pour_lire_le_pas import la_ligne  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI, PERMUTATIONS  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import (  # noqa: E402
    GARANTIE, LE_COMPTE_DECISIF, la_regle_de_la_porte, le_seuil_des_colonnes_fortes,
    les_bruits_propres, les_directions, lepreuve, sur_letalon, une_matiere)
from les_rangees_saccordent_elles_entre_elles import LES_RANGEES  # noqa: E402
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau)
from ouvrir_les_quinze import _rng  # noqa: E402
from une_rangee_voisine_lit_elle_le_meme_pas import les_pas_dune_rangee  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_211_A_RENDU = MESURES / "les_rangees_saccordent_elles_entre_elles.json"
CE_QUE_218_A_RENDU = MESURES / "lecart_extreme_est_il_porte_par_une_rangee.json"
GRAINE = 20261031
LA_TOLERANCE_DE_REPRODUCTION = 2e-4

LA_QUESTION_DECLAREE = ("cinq rangées voisines désignent-elles la rangée fautive aux écarts de "
                        "couture extrêmes, là où trois ne le pouvaient pas ?")
LEPREUVE_DECLAREE = ("l'épreuve de `218`, sans retouche, sur les colonnes communes aux cinq "
                     "rangées")


def ce_que_218_a_rendu(chemin: Path = CE_QUE_218_A_RENDU) -> dict:
    """Le nombre de rangées, les colonnes des extrêmes et l'étalon de `218` — relus, jamais retapés."""
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    ve, et = d.get("le_verdict") or {}, d.get("letalon") or {}
    k = ve.get("le_plus_petit_nombre_de_rangees_qui_voit")
    if k is None:
        return {"decidable": False,
                "raison": "`218` ne dit pas combien de rangées rendraient la question décidable"}
    amplitude, kappa = et.get("lamplitude_des_sauts_en_voxels"), et.get("laplatissement_du_piege")
    lu = d.get("ce_que_211_a_rendu") or {}
    if amplitude is None or kappa is None or lu.get("la_premiere_colonne") is None:
        return {"decidable": False,
                "raison": "`218` ne publie pas son étalon ou ses colonnes communes"}
    extremes = {}
    for nom, x in sorted((d.get("le_detail_des_extremes") or {}).items()):
        if x.get("dans_le_recouvrement"):
            extremes.setdefault(int(x["la_colonne"]), {"les_paires": [],
                                                       "la_rangee_designee_par_218":
                                                           int(x["la_rangee_que_la_direction_designe"])})
            extremes[int(x["la_colonne"])]["les_paires"].append(nom)
    return {"decidable": True,
            "le_nombre_de_rangees": int(k),
            "lamplitude_des_sauts_en_voxels": float(amplitude),
            "laplatissement_du_piege": float(kappa),
            "la_premiere_colonne": int(lu["la_premiere_colonne"]),
            "la_derniere_colonne": int(lu["la_derniere_colonne"]),
            "les_colonnes_des_extremes": extremes,
            "les_bruits_propres_de_218": d.get("les_bruits_propres_en_voxels") or {},
            "lepreuve_de_218_voyait": bool((d.get("lepreuve") or {}).get("elle_voit")),
            # ⚠⚠ RELUS POUR QUE LA COMPARAISON A TROIS RANGEES AIT SON PRODUCTEUR : `219` la cite.
            "les_tirages_de_218_au_moins_aussi_forts":
                (d.get("lepreuve") or {}).get("les_tirages_au_moins_aussi_forts"),
            "les_colonnes_de_lepreuve_de_218": (d.get("lepreuve") or {}).get("combien_de_colonnes")}


def ce_que_211_a_rendu(chemin: Path = CE_QUE_211_A_RENDU) -> dict:
    """La rangée médiane du treillis et les pas que `211` publie par rangée — pour la relecture."""
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    mediane = (d.get("les_rangees_du_treillis") or {}).get("la_mediane")
    marches = d.get("les_marches_separees")
    if mediane is None or not isinstance(marches, dict) or not marches:
        return {"decidable": False, "raison": "`211` ne publie ni sa médiane ni ses marches"}
    publies = {}
    for nom, m in sorted(marches.items()):
        cols, cum = m.get("les_colonnes"), m.get("le_cumul_en_voxels")
        if not isinstance(cols, list) or not isinstance(cum, list) or len(cum) != len(cols) + 1:
            return {"decidable": False,
                    "raison": f"la rangée {nom} ne publie pas un cumul d'une position de plus"}
        publies[int(nom)] = {int(c): float(s)
                             for c, s in zip(cols, np.diff(np.asarray(cum, dtype=float)))}
    return {"decidable": True, "la_mediane": int(mediane), "les_pas_publies": publies}


def les_rangees_a_lire(mediane: int, combien: int) -> list[int]:
    """La médiane et ses voisines de part et d'autre — `combien` rangées contiguës, jamais choisies."""
    k = int(combien)
    debut = int(mediane) - k // 2
    return list(range(debut, debut + k))


def _lire_une_rangee(rangee: int, delai: float, ouvrir, meta, volume):
    return la_ligne(volume, delai, None, ouvrir, meta, LES_RANGEES, int(rangee))


def _les_pas(lg: dict) -> dict:
    return les_pas_dune_rangee(lg["droits"], lg["gauches"], lg["les_rangees_lues"])


def lire_les_rangees(rangees, delai: float = DELAI, ouvrir=None, meta=None, volume=None,
                     lire_une=None, pas_de=None) -> dict:
    """Les pas de chaque rangée, lus par le lecteur de `211` avec ses paramètres.

    ⚠⚠ UNE RANGÉE VIDE OU DONT LE FIL EST TOMBÉ ARRÊTE TOUT, par son nom. Une lecture partielle
    comparerait des rangées dont les trous ne viennent pas de la matière.
    """
    if lire_une is None:
        if volume is None:
            volume = le_segment_declare()
            if volume is None:
                return {"decidable": False, "raison": "aucun volume recensé"}
        if meta is None:
            try:
                meta = array_meta(f"{BUCKET}/{volume['cle']}", 0, delai)
            except Exception as e:  # noqa: BLE001
                return {"decidable": False,
                        "raison": f"le volume ne répond pas : {type(e).__name__}"}

        def lire_une(r):  # noqa: E306
            return _lire_une_rangee(r, delai, ouvrir, meta, volume)
    pas_de = pas_de or _les_pas
    pas, lignes = {}, {}
    for r in rangees:
        lg = lire_une(int(r))
        if not lg.get("decidable"):
            return {"decidable": False, "raison": f"la rangée {r} est vide : {lg.get('raison')}"}
        pannes = les_pannes_de_reseau(lg.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": (f"{pannes} chunks perdus par le réseau sur la rangée {r} — une "
                               f"rangée dont le fil est tombé n'est pas comparable")}
        pas[int(r)] = {int(c): float(s) for c, s in pas_de(lg).items()}
        lignes[int(r)] = {k: x for k, x in lg.items()
                          if k not in ("droits", "gauches", "les_colonnes")}
    return {"decidable": True, "les_pas_par_rangee": pas, "les_lignes": lignes}


def la_reproduction(pas_par_rangee: dict, publies: dict,
                    tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """Les rangées que `211` avait lues retombent-elles sur ses pas ? SINON, REFUS PAR LEUR NOM.

    ⚠⚠⚠ LA TOLÉRANCE EST DÉRIVÉE DE L'ARRONDI : le cumul de `211` est publié à quatre décimales,
    donc un pas tiré de deux positions arrondies s'écarte du vrai d'au plus deux dix-millièmes.
    """
    communes = sorted(set(pas_par_rangee) & set(publies))
    if not communes:
        return {"decidable": False, "raison": "aucune rangée relue n'a été publiée par `211`"}
    ecarts = {}
    for r in communes:
        manque = [c for c in publies[r] if c not in pas_par_rangee[r]]
        if manque:
            return {"decidable": False,
                    "raison": (f"la rangée {r} relue n'a pas de pas à {len(manque)} colonnes que "
                               f"`211` publie")}
        e = max(abs(float(pas_par_rangee[r][c]) - float(publies[r][c])) for c in publies[r])
        if e > float(tolerance):
            return {"decidable": False,
                    "raison": (f"la rangée {r} relue ne retombe pas sur `211` (écart {e:.4g} "
                               f"voxel) — deux lecteurs différents")}
        ecarts[str(r)] = round(float(e), 6)
    return {"decidable": True, "les_rangees_relues": [int(r) for r in communes],
            "les_ecarts_les_plus_grands": ecarts, "la_tolerance": float(tolerance)}


def la_matiere_commune(pas_par_rangee: dict, rangees, colonnes=None) -> dict:
    """Les colonnes où TOUTES les rangées ont un pas, et la matrice des pas, une ligne par colonne."""
    rs = [int(r) for r in rangees]
    if any(r not in pas_par_rangee for r in rs):
        return {"decidable": False, "raison": "une rangée demandée n'a pas été lue"}
    communes = sorted(set.intersection(*[set(pas_par_rangee[r]) for r in rs]))
    if colonnes is not None:
        garde = set(int(c) for c in colonnes)
        communes = [c for c in communes if c in garde]
    if len(communes) < 30:
        return {"decidable": False, "raison": f"les rangées ne partagent que {len(communes)} colonnes"}
    return {"decidable": True, "les_colonnes": communes,
            "les_pas": [[float(pas_par_rangee[r][c]) for r in rs] for c in communes]}


def le_detail_aux_colonnes(matiere: dict, rangees, dirs: dict, seuil: float, voulues: dict) -> dict:
    """Aux colonnes où `218` a situé les extrêmes : ce que les CINQ rangées y font — une description.

    ⚠⚠ La rangée désignée à cinq est comparée à celle que `218` désignait à trois : si c'est la même,
    la forme que `218` décrivait tient avec deux témoins de plus ; sinon elle ne tenait qu'à trois.
    """
    index = {c: i for i, c in enumerate(matiere["les_colonnes"])}
    e = dirs["les_energies"]
    out = {}
    for col, x in sorted(voulues.items()):
        if int(col) not in index:
            out[str(col)] = {"lue_par_les_cinq": False}
            continue
        j = index[int(col)]
        designee = int(rangees[int(dirs["les_fautives"][j])])
        out[str(col)] = {"lue_par_les_cinq": True,
                         "les_paires_de_217": list(x["les_paires"]),
                         "les_anomalies_en_voxels":
                             {str(r): round(float(dirs["les_anomalies"][j, q]), 4)
                              for q, r in enumerate(rangees)},
                         "la_rangee_designee": designee,
                         "la_rangee_designee_par_218": int(x["la_rangee_designee_par_218"]),
                         "la_meme_rangee_que_218": designee == int(x["la_rangee_designee_par_218"]),
                         "la_proximite": round(float(dirs["les_proximites"][j]), 4),
                         "lenergie": round(float(e[j]), 4),
                         "le_rang_de_lenergie": int(1 + np.sum(e > e[j])),
                         "cest_une_colonne_forte": bool(e[j] > seuil)}
    return out


def _ce_qui_reste(valide: bool, voit: bool, puissante: bool, k: int, k_min) -> str:
    """Les quatre issues, et elles sont EXCLUSIVES."""
    if not valide:
        return "L'ÉTALON NE TIENT PAS : LE VERDICT EST RETENU"
    if voit:
        return (f"LOCALISÉ : LES ÉCARTS EXTRÊMES SONT PORTÉS PAR UNE RANGÉE À LA FOIS, ET {k} "
                f"VOISINES LA DÉSIGNENT")
    if puissante:
        return ("PARTAGÉ : LES ÉCARTS EXTRÊMES TOMBENT SUR DES COLONNES DIFFICILES POUR TOUTES LES "
                "RANGÉES, ET UN VOTE N'Y PEUT RIEN")
    combien = f"{k_min}" if k_min is not None else "PLUS QUE L'ÉCHELLE N'EN PORTE"
    return f"INDÉCIDABLE MÊME À {k} RANGÉES : IL EN FAUT {combien}"


def juger(epreuve: dict, etalon: dict, k: int) -> dict:
    valide = bool(etalon.get("elle_est_valide"))
    voit = bool(epreuve.get("elle_voit"))
    rang = next((e for e in etalon.get("lechelle_en_rangees") or []
                 if int(e["combien_de_rangees"]) == int(k)), None)
    puissante = bool(rang and rang["les_vus"] == int(etalon.get("les_replicats") or 0)
                     and rang.get("elle_resiste_au_piege"))
    k_min = etalon.get("le_plus_petit_nombre_de_rangees_qui_voit")
    return {"lepreuve_voit": voit,
            "combien_de_colonnes_fortes": epreuve.get("combien_de_colonnes_fortes"),
            "letalon_est_valide": valide,
            "le_nombre_de_rangees_lues": int(k),
            "elles_suffisent_au_nombre_observe": puissante,
            "le_plus_petit_nombre_de_rangees_qui_voit": k_min,
            "ce_qui_reste_a_mesurer": _ce_qui_reste(valide, voit, puissante, int(k), k_min)}


def analyser(pas_par_rangee: dict, rangees, par211: dict, par218: dict,
             tirages: int = PERMUTATIONS, graine: int = GRAINE, replicats: int = 12,
             decisif: int = LE_COMPTE_DECISIF, avec_etalon: bool = True) -> dict:
    """Tout ce qui suit la lecture — pur, donc rejouable sans réseau."""
    rep = la_reproduction(pas_par_rangee, par211["les_pas_publies"])
    if not rep.get("decidable"):
        return {"decidable": False, "raison": rep.get("raison")}
    rs = [int(r) for r in rangees]
    mat = la_matiere_commune(pas_par_rangee, rs)
    if not mat.get("decidable"):
        return {"decidable": False, "raison": mat.get("raison")}
    p = np.asarray(mat["les_pas"], dtype=float)
    bp = les_bruits_propres(p)
    if not bp.get("decidable"):
        return {"decidable": False, "raison": bp.get("raison")}
    dirs = les_directions(p, bp["les_variances"])
    if not dirs.get("decidable"):
        return {"decidable": False, "raison": dirs.get("raison")}
    n, k = p.shape
    seuil = le_seuil_des_colonnes_fortes(n, k)
    ep = lepreuve(p, tirages, graine)
    porte = la_regle_de_la_porte(p, tirages, graine)
    zone = range(par218["la_premiere_colonne"], par218["la_derniere_colonne"] + 1)
    mat218 = la_matiere_commune(pas_par_rangee, rs, zone)
    controle = (lepreuve(np.asarray(mat218["les_pas"], dtype=float), tirages, graine + 1)
                if mat218.get("decidable") else {"decidable": False, "raison": mat218.get("raison")})
    # ⚠⚠⚠ CONTROLE AJOUTE APRES LA MESURE, ET C'EST DIT : cinq rangees lues sur toutes leurs colonnes
    # different de `218` par DEUX choses a la fois — plus de rangees, et plus de colonnes. Sans ce
    # controle, le gain serait attribue aux rangees alors qu'il pourrait venir des colonnes. Les trois
    # rangees de `211`, sur TOUTES leurs colonnes communes relues, posent la question separement. Il
    # ne change pas le verdict, qui reste celui de l'epreuve declaree.
    trois = sorted(int(r) for r in par211["les_pas_publies"] if int(r) in pas_par_rangee)
    mat3 = la_matiere_commune(pas_par_rangee, trois)
    sur_trois = (lepreuve(np.asarray(mat3["les_pas"], dtype=float), tirages, graine + 2)
                 if mat3.get("decidable") else {"decidable": False, "raison": mat3.get("raison")})
    detail = le_detail_aux_colonnes(mat, rs, dirs, seuil, par218["les_colonnes_des_extremes"])
    sig = [float(np.sqrt(x)) for x in bp["les_variances"]]
    etalon = (sur_letalon(n, sig, par218["lamplitude_des_sauts_en_voxels"],
                          par218["laplatissement_du_piege"],
                          int(ep.get("combien_de_colonnes_fortes") or 0), replicats, decisif,
                          graine, tirages) if avec_etalon else None)
    return {"decidable": True,
            "la_reproduction": rep,
            "les_rangees": rs,
            "combien_de_colonnes": int(n),
            "la_premiere_colonne": int(mat["les_colonnes"][0]),
            "la_derniere_colonne": int(mat["les_colonnes"][-1]),
            "les_bruits_propres_en_voxels": {str(r): round(s, 4) for r, s in zip(rs, sig)},
            "les_bruits_propres_de_218": par218["les_bruits_propres_de_218"],
            "lepreuve": ep,
            "par_colonne": {"les_colonnes": [int(c) for c in mat["les_colonnes"]],
                            "les_energies": [round(float(x), 4) for x in dirs["les_energies"]],
                            "les_proximites": [round(float(x), 4) for x in dirs["les_proximites"]],
                            "les_rangees_designees": [int(rs[int(i)]) for i in dirs["les_fautives"]]},
            "la_regle_de_la_porte": porte,
            "sur_les_colonnes_de_218": {**controle,
                                        "combien_de_colonnes_communes":
                                            len(mat218.get("les_colonnes") or [])},
            "les_trois_rangees_de_211_sur_toutes_leurs_colonnes": {
                **sur_trois, "les_rangees": trois,
                "combien_de_colonnes_communes": len(mat3.get("les_colonnes") or [])},
            "le_detail_aux_colonnes_de_218": detail,
            "letalon": etalon,
            "le_verdict": juger(ep, etalon or {}, k)}


def mesurer(delai: float = DELAI, graine: int = GRAINE, tirages: int = PERMUTATIONS,
            replicats: int = 12, decisif: int = LE_COMPTE_DECISIF, ouvrir=None, meta=None,
            avec_etalon: bool = True, depuis: Path | None = None) -> dict:
    """La lecture des cinq rangées puis l'analyse — ou l'analyse seule, depuis une lecture publiée."""
    par211 = ce_que_211_a_rendu()
    if not par211.get("decidable"):
        return {"decidable": False, "raison": par211.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    par218 = ce_que_218_a_rendu()
    if not par218.get("decidable"):
        return {"decidable": False, "raison": par218.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    rangees = les_rangees_a_lire(par211["la_mediane"], par218["le_nombre_de_rangees"])
    if depuis is not None:
        ancien = json.loads(Path(depuis).read_text())
        pas = {int(r): {int(c): float(s) for c, s in d_.items()}
               for r, d_ in (ancien.get("les_pas_par_rangee") or {}).items()}
        lignes = ancien.get("les_lignes") or {}
    else:
        lu = lire_les_rangees(rangees, delai, ouvrir, meta)
        if not lu.get("decidable"):
            return {"decidable": False, "raison": lu.get("raison"),
                    "la_question_declaree": LA_QUESTION_DECLAREE}
        pas, lignes = lu["les_pas_par_rangee"], lu["les_lignes"]
    a = analyser(pas, rangees, par211, par218, tirages, graine, replicats, decisif, avec_etalon)
    base = {"graine": int(graine), "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE, "lepreuve_declaree": LEPREUVE_DECLAREE,
            "la_garantie_du_nul": GARANTIE, "les_rangees_lues": rangees,
            "ce_que_218_a_rendu": par218, "la_mediane_de_211": par211["la_mediane"],
            "les_lignes": {str(r): x for r, x in lignes.items()},
            # ⚠⚠ LES PAS DE CHAQUE RANGEE SONT PUBLIES, colonne par colonne, pour que l'analyse se
            # rejoue sans relire le volume (`--depuis`).
            "les_pas_par_rangee": {str(r): {str(c): round(float(s), 4) for c, s in sorted(d_.items())}
                                   for r, d_ in sorted(pas.items())}}
    return {**base, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"\nrangées {r['les_rangees']} · {r['combien_de_colonnes']} colonnes communes "
          f"({r['la_premiere_colonne']}–{r['la_derniere_colonne']}) · relecture de `211` : "
          f"{r['la_reproduction']['les_ecarts_les_plus_grands']}")
    print(f"  bruits propres : {r['les_bruits_propres_en_voxels']} (à trois : "
          f"{r['les_bruits_propres_de_218']})")
    e = r["lepreuve"]
    print(f"\nÉPREUVE · seuil {e['le_seuil_denergie']} · {e['combien_de_colonnes_fortes']} colonnes "
          f"fortes · énergie la plus forte {e['lenergie_la_plus_forte']}")
    if e.get("la_proximite_observee") is not None:
        print(f"  proximité {e['la_proximite_observee']} · nul médian "
              f"{e['la_proximite_du_nul_mediane']} le plus fort {e['la_proximite_du_nul_la_plus_forte']}"
              f" · {e['les_tirages_au_moins_aussi_forts']}/{e['tirages']} · voit {e['elle_voit']}")
    t3 = r["les_trois_rangees_de_211_sur_toutes_leurs_colonnes"]
    print(f"  trois rangées de 211 sur toutes leurs colonnes (contrôle) · "
          f"{t3.get('combien_de_colonnes_communes')} colonnes · voit {t3.get('elle_voit')} · "
          f"{t3.get('les_tirages_au_moins_aussi_forts')}/{t3.get('tirages')}")
    c = r["sur_les_colonnes_de_218"]
    print(f"  sur les colonnes de 218 (contrôle) · {c.get('combien_de_colonnes_communes')} colonnes · "
          f"voit {c.get('elle_voit')} · {c.get('les_tirages_au_moins_aussi_forts')}/{c.get('tirages')}")
    print(f"  règle de la porte · voit {r['la_regle_de_la_porte'].get('elle_voit')}")
    print("\nCOLONNES DES EXTRÊMES DE `218` :")
    for col, d in sorted(r["le_detail_aux_colonnes_de_218"].items()):
        if not d.get("lue_par_les_cinq"):
            print(f"  {col} · pas lue par les cinq")
            continue
        print(f"  {col} · {d['les_anomalies_en_voxels']} · désigne {d['la_rangee_designee']} "
              f"(218 : {d['la_rangee_designee_par_218']}) · proximité {d['la_proximite']} · rang "
              f"{d['le_rang_de_lenergie']} · forte {d['cest_une_colonne_forte']}")
    t = r.get("letalon")
    if t and t.get("decidable"):
        print(f"\nÉTALON · faux {t['le_faux']['les_vus']}/{t['le_faux']['sur']} · piège "
              f"{t['le_piege']['les_vus']}/{t['le_piege']['sur']} · valide {t['elle_est_valide']}")
        for x in t["lechelle_en_rangees"]:
            print(f"    {x['combien_de_rangees']} rangées · vu {x['les_vus']}/{x['sur']} · piège "
                  f"{x['le_taux_sur_le_piege']}")
        for x in t["lechelle_en_sauts"]:
            print(f"    {x['combien_de_sauts']} saut(s) · vu {x['les_vus']}/{x['sur']}")
    print(f"\nVERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        """Une sonde accepte un appelable, et une levée est un ÉCHEC — jamais une batterie morte."""
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    def _sur(fn, *args, **kw):
        try:
            return fn(*args, **kw)
        except Exception as exc:  # noqa: BLE001
            return {"decidable": False, "raison": f"LEVÉE {type(exc).__name__}: {exc}"}

    v("★★★ une seule question, et l'épreuve est celle de `218`",
      isinstance(LA_QUESTION_DECLAREE, str) and "218" in LEPREUVE_DECLAREE)

    # ⭐⭐⭐ CE QUI EST DERIVE.
    p218 = _sur(ce_que_218_a_rendu)
    p211 = _sur(ce_que_211_a_rendu)
    v("★★★★ le nombre de rangées est RELU dans l'étalon de `218`, jamais tapé",
      lambda: p218["le_nombre_de_rangees"] == json.loads(CE_QUE_218_A_RENDU.read_text())
      ["le_verdict"]["le_plus_petit_nombre_de_rangees_qui_voit"], str(p218.get("raison")))
    v("★★★★ la médiane est RELUE dans le treillis de `211`",
      lambda: p211["la_mediane"] == json.loads(CE_QUE_211_A_RENDU.read_text())
      ["les_rangees_du_treillis"]["la_mediane"], str(p211.get("raison")))
    v("★★★★ les rangées sont la médiane et ses voisines de part et d'autre, contiguës",
      les_rangees_a_lire(198, 5) == [196, 197, 198, 199, 200]
      and les_rangees_a_lire(198, 3) == [197, 198, 199] and les_rangees_a_lire(10, 7)[3] == 10)
    v("★★★★ elles contiennent les trois que `211` a lues, donc la relecture a de quoi vérifier",
      lambda: set(p211["les_pas_publies"]) <= set(
          les_rangees_a_lire(p211["la_mediane"], p218["le_nombre_de_rangees"])))
    v("★★★★ les colonnes des extrêmes de `218` sont relues avec la rangée qu'il désignait",
      lambda: all("la_rangee_designee_par_218" in x
                  for x in p218["les_colonnes_des_extremes"].values())
      and len(p218["les_colonnes_des_extremes"]) >= 1)
    v("★★★ un `218` absent est refusé", not ce_que_218_a_rendu(Path("/nen/existe.json")).get("decidable"))
    v("★★★ un `211` absent est refusé", not ce_que_211_a_rendu(Path("/nen/existe.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_219.json"
    try:
        d_ = json.loads(CE_QUE_218_A_RENDU.read_text())
        d_["le_verdict"]["le_plus_petit_nombre_de_rangees_qui_voit"] = None
        tmp.write_text(json.dumps(d_))
        v("★★★★ un `218` qui ne dit pas combien de rangées il faut est refusé, jamais défauté",
          lambda: "combien" in (ce_que_218_a_rendu(tmp).get("raison") or ""))
    finally:
        if tmp.exists():
            tmp.unlink()

    # ⚠⚠⚠ LA RELECTURE.
    publies = {197: {10: 1.0, 11: -2.0}, 198: {10: 0.5, 11: 0.25}}
    v("★★★★ des pas relus identiques passent la relecture",
      lambda: la_reproduction({197: {10: 1.0, 11: -2.0, 12: 3.0}, 198: {10: 0.5, 11: 0.25},
                               196: {}}, publies).get("decidable"))
    v("★★★★ un écart d'un dix-millième passe : c'est l'arrondi du cumul",
      lambda: la_reproduction({197: {10: 1.0001, 11: -2.0}, 198: {10: 0.5, 11: 0.25}}, publies)
      .get("decidable"))
    rr = _sur(la_reproduction, {197: {10: 1.01, 11: -2.0}, 198: {10: 0.5, 11: 0.25}}, publies)
    v("★★★★ une rangée relue qui ne retombe pas sur `211` est REFUSÉE par son nom — deux lecteurs",
      not rr.get("decidable") and "197" in (rr.get("raison") or ""), str(rr))
    rm = _sur(la_reproduction, {197: {10: 1.0}, 198: {10: 0.5, 11: 0.25}}, publies)
    v("★★★★ une rangée relue à qui manque une colonne publiée est refusée",
      not rm.get("decidable") and "197" in (rm.get("raison") or "")
      and "LEVÉE" not in (rm.get("raison") or ""), str(rm))
    v("★★★ aucune rangée commune avec `211` est refusé",
      lambda: not la_reproduction({196: {10: 1.0}}, publies).get("decidable"))
    v("★★★★ la tolérance est deux dix-millièmes : l'arrondi à quatre décimales de deux positions",
      abs(LA_TOLERANCE_DE_REPRODUCTION - 2e-4) < 1e-12)

    # ⚠⚠ LA LECTURE, SANS RESEAU.
    def _lg_ok(r):
        return {"decidable": True, "refuses": {}, "droits": {}, "gauches": {},
                "les_rangees_lues": [], "les_colonnes": [], "la_rangee": r}

    def _pas_fab(lg):
        g_ = _rng(1000 + int(lg["la_rangee"]))
        return {c: float(x) for c, x in zip(range(200), g_.normal(0.0, 2.0, 200))}

    lu_ok = _sur(lire_les_rangees, [196, 197], lire_une=_lg_ok, pas_de=_pas_fab)
    v("★★★★ la lecture rend un pas par colonne et par rangée, et garde le résumé de chaque ligne",
      lu_ok.get("decidable") and set(lu_ok["les_pas_par_rangee"]) == {196, 197}
      and len(lu_ok["les_pas_par_rangee"][196]) == 200
      and "droits" not in lu_ok["les_lignes"][196])
    panne = _sur(lire_les_rangees, [196], lire_une=lambda r: {**_lg_ok(r), "refuses":
                                                              {"le réseau a échoué : x": 3}},
                 pas_de=_pas_fab)
    v("★★★★ une rangée dont le fil est tombé ARRÊTE tout, par son nom",
      not panne.get("decidable") and "196" in (panne.get("raison") or ""), str(panne))
    vide = _sur(lire_les_rangees, [200], lire_une=lambda r: {"decidable": False, "raison": "rien"},
                pas_de=_pas_fab)
    v("★★★ une rangée vide arrête tout, par son nom",
      not vide.get("decidable") and "200" in (vide.get("raison") or "")
      and "LEVÉE" not in (vide.get("raison") or ""), str(vide))

    # ⭐⭐⭐ LA MATIERE COMMUNE.
    pas_x = {1: {c: 0.0 for c in range(40)}, 2: {c: 0.0 for c in range(5, 45)},
             3: {c: 0.0 for c in range(0, 50) if c != 20}}
    mc = _sur(la_matiere_commune, pas_x, [1, 2, 3])
    v("★★★★ les colonnes communes sont l'INTERSECTION, trous compris",
      mc.get("decidable") and mc["les_colonnes"] == [c for c in range(5, 40) if c != 20])
    v("★★★★ la restriction aux colonnes de `218` ne garde que les colonnes demandées",
      lambda: la_matiere_commune({1: {c: 0.0 for c in range(300)}, 2: {c: 0.0 for c in range(300)},
                                  3: {c: 0.0 for c in range(300)}}, [1, 2, 3], range(109, 214))
      ["les_colonnes"] == list(range(109, 214)))
    v("★★★ une rangée demandée non lue est refusée",
      lambda: not la_matiere_commune(pas_x, [1, 2, 4]).get("decidable"))
    v("★★★ trop peu de colonnes communes est refusé",
      lambda: not la_matiere_commune({1: {0: 1.0}, 2: {0: 1.0}, 3: {0: 1.0}}, [1, 2, 3])
      .get("decidable"))

    # ⭐⭐⭐⭐ L'ANALYSE ENTIERE, SUR UNE MATIERE FABRIQUEE A CINQ RANGEES.
    rs = [196, 197, 198, 199, 200]
    fab = une_matiere("saut", 180, [2.0, 2.1, 1.8, 2.7, 2.2], 7, amplitude=30.0, combien=8)
    pas_fab = {r: {c: float(fab[c, q]) for c in range(180)} for q, r in enumerate(rs)}
    p211_fab = {"la_mediane": 198, "les_pas_publies": {r: {c: pas_fab[r][c] for c in range(100, 150)}
                                                        for r in (197, 198, 199)}}
    p218_fab = {"le_nombre_de_rangees": 5, "lamplitude_des_sauts_en_voxels": 15.0,
                "laplatissement_du_piege": 7.0, "la_premiere_colonne": 40,
                "la_derniere_colonne": 150,
                "les_colonnes_des_extremes": {60: {"les_paires": ["a-b"],
                                                   "la_rangee_designee_par_218": 199}},
                "les_bruits_propres_de_218": {}}
    an = _sur(analyser, pas_fab, rs, p211_fab, p218_fab, PERMUTATIONS, 5, 2, 6, False)
    v("★★★★ l'analyse traverse et VOIT huit sauts francs à cinq rangées",
      lambda: an.get("decidable") and an["lepreuve"]["elle_voit"] is True, str(an.get("raison")))
    v("★★★★ son seuil est celui d'un khi-deux à QUATRE degrés, pas à deux",
      lambda: abs(an["lepreuve"]["le_seuil_denergie"]
                  - round(le_seuil_des_colonnes_fortes(180, 5), 4)) < 1e-9
      and an["lepreuve"]["le_seuil_denergie"] > round(2.0 * np.log(180), 4))
    v("★★★★ elle porte le contrôle nommé sur les colonnes de `218`, restreint à elles",
      lambda: an["sur_les_colonnes_de_218"]["combien_de_colonnes_communes"] == 111)
    v("★★★★ elle porte les trois rangées de `211` sur toutes leurs colonnes, pour séparer le gain "
      "des rangées de celui des colonnes",
      lambda: an["les_trois_rangees_de_211_sur_toutes_leurs_colonnes"]["les_rangees"]
      == [197, 198, 199]
      and an["les_trois_rangees_de_211_sur_toutes_leurs_colonnes"]["combien_de_colonnes_communes"]
      == 180 and an["les_trois_rangees_de_211_sur_toutes_leurs_colonnes"]["combien_de_rangees"] == 3)
    v("★★★★ elle situe les colonnes des extrêmes de `218` et compare la rangée désignée",
      lambda: "60" in an["le_detail_aux_colonnes_de_218"]
      and isinstance(an["le_detail_aux_colonnes_de_218"]["60"]["la_meme_rangee_que_218"], bool))
    faux211 = {**p211_fab, "les_pas_publies": {197: {c: pas_fab[197][c] + 0.01
                                                     for c in range(100, 150)}}}
    anf = _sur(analyser, pas_fab, rs, faux211, p218_fab, PERMUTATIONS, 5, 2, 6, False)
    v("★★★★ l'analyse REFUSE une matière dont la relecture ne retombe pas sur `211`",
      not anf.get("decidable") and "197" in (anf.get("raison") or ""), str(anf.get("raison")))
    manquante = {r: d_ for r, d_ in pas_fab.items() if r != 200}
    v("★★★ elle refuse une rangée demandée qui n'a pas été lue",
      lambda: not analyser(manquante, rs, p211_fab, p218_fab, PERMUTATIONS, 5, 2, 6, False)
      .get("decidable"))

    # ⭐⭐⭐ LES ISSUES.
    issues = {_ce_qui_reste(a, b, c, 5, k) for a in (True, False) for b in (True, False)
              for c in (True, False) for k in (7, None)}
    v("★★★★ les issues sont celles posées, et un étalon invalide prime sur tout",
      _ce_qui_reste(False, True, True, 5, 7) == _ce_qui_reste(False, False, False, 5, None)
      and len({x.split(":")[0] for x in issues}) == 4)
    faux_et = {"elle_est_valide": True, "les_replicats": 12,
               "lechelle_en_rangees": [{"combien_de_rangees": 3, "les_vus": 12,
                                        "elle_resiste_au_piege": True},
                                       {"combien_de_rangees": 5, "les_vus": 4,
                                        "elle_resiste_au_piege": True}],
               "le_plus_petit_nombre_de_rangees_qui_voit": 7}
    v("★★★★ la puissance est lue AU NOMBRE DE RANGÉES LUES, pas à trois",
      juger({"elle_voit": False}, faux_et, 5)["elles_suffisent_au_nombre_observe"] is False
      and "MÊME À 5" in juger({"elle_voit": False}, faux_et, 5)["ce_qui_reste_a_mesurer"])
    faux_et2 = {**faux_et, "lechelle_en_rangees": [{"combien_de_rangees": 5, "les_vus": 12,
                                                    "elle_resiste_au_piege": False}]}
    v("★★★★ une puissance qui tire sur le piège ne rend pas le silence « partagé »",
      juger({"elle_voit": False}, faux_et2, 5)["elles_suffisent_au_nombre_observe"] is False)

    # ⭐⭐⭐⭐ LE REJEU DEPUIS UNE LECTURE PUBLIEE.
    publie = RACINE / "docs" / "mesures" / "cinq_rangees_designent_elles_la_fautive.json"
    if publie.exists():
        rej = _sur(mesurer, depuis=publie, replicats=2, decisif=6)
        v("★★★★ l'analyse se rejoue depuis la lecture publiée, sans réseau, et retombe sur l'épreuve "
          "publiée",
          lambda: rej.get("decidable") and rej["lepreuve"] == json.loads(publie.read_text())
          ["lepreuve"], str(rej.get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--depuis", type=Path, default=None,
                   help="rejoue l'analyse depuis une lecture publiée, sans relire le volume")
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=PERMUTATIONS)
    p.add_argument("--replicats", type=int, default=12)
    p.add_argument("--decisif", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(DELAI, a.graine, a.tirages, a.replicats, a.decisif,
                avec_etalon=not a.sans_etalon, depuis=a.depuis)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
