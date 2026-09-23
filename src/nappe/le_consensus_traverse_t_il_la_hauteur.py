"""Le consensus de cinq colonnes voisines, pris à chaque couture verticale, traverse-t-il la hauteur ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE COLONNE NE SOIT LUE. La seule chose regardée avant
d'écrire est la PRÉSENCE, dans la lecture de `222`, des pas verticaux aux colonnes choisies — pour
savoir si la relecture peut se contrôler —, jamais une valeur.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P68`. `222` établit que le pas commun du consensus reste
cohérent, sous le demi-feuillet, avec le transfert d'une rangée de chunks à la suivante sur les cinq
rangées lues. Une surface entière demande de traverser aussi la HAUTEUR du segment, colonne par
colonne. C'est `221` transposé : là où `221` prenait la médiane de cinq rangées voisines à chaque couture
le long d'une rangée, cette tranche prend la médiane de cinq colonnes voisines à chaque couture verticale
le long d'une colonne.

## Ce qui est dérivé, jamais choisi

⭐⭐⭐ LES COLONNES. Leur nombre est celui des rangées de `219` — cinq, relu —, et elles sont centrées
sur la colonne médiane de la grille de chunks, comme `219` centrait ses rangées sur la rangée médiane :
la médiane et ses voisines de part et d'autre, par la fonction même de `219`.

⭐⭐ LE LECTEUR. Le même chunk, le même filtre du producteur, la même bande et la même estimation que
`222` : le filtre et la coupe des bords haut et bas sont ÉCRITS UNE FOIS dans le lecteur de `204` et
appelés par les deux. Seul change le sens de la marche : une colonne de chunks, du haut en bas.

## Ce qui rend une colonne lue aujourd'hui comparable à une rangée lue hier

⚠⚠⚠ LA RELECTURE. Les cinq colonnes croisent les rangées `196`–`200` de `222`, qui a publié les pas
verticaux à ces colonnes. Sur ce recouvrement, les pas relus par la marche en colonne doivent retomber
sur ceux de `222` à l'arrondi de sa quatrième décimale, sur exactement les mêmes coutures : sinon la
lecture est REFUSÉE par son nom — deux lecteurs qui ne s'accordent pas ne se comparent pas. Une colonne
dont le fil est tombé est refusée aussi.

## Ce qui se mesure : l'instrument de `221`, bloc par bloc

Importé, jamais réécrit : le consensus (la MÉDIANE des colonnes présentes, au moins TROIS sur cinq), le
plus long tronçon, la traversée, l'extrapolation par blocs de pas centrés, son étalon. Dans l'ordre :

1. ⭐⭐⭐⭐ LA TRAVERSÉE OBSERVÉE : sur le plus long tronçon où le consensus existe sans interruption, la
   distance au départ `max_k |S_k|` contre le demi-feuillet. La moyenne des colonnes présentes est
   portée comme contrôle nommé.
2. ⭐⭐ LE CONTRÔLE APPARIÉ : une colonne seule sur le MÊME tronçon, quand l'une le couvre sans trou.
3. ⭐⭐ L'EXTRAPOLATION À LA HAUTEUR ENTIÈRE, par blocs de `⌈n^(1/3)⌉`, pas centrés (`R4-L22`), avec
   l'étalon de `221` à la dépendance que le consensus montre.

## Les issues, exclusives — celles de `221`

- la traversée observée quitte le feuillet : le consensus ne suffit pas, même sur ce qu'il lit ;
- elle reste, mais l'extrapolation dit que la hauteur entière le ferait sortir ;
- les deux restent : le consensus des colonnes traverse la hauteur sans quitter le feuillet.

⚠⚠⚠ ET `222` A DÉJÀ DIT CE QUI ATTEND : le pas vertical varie davantage que l'horizontal, donc le
consensus des colonnes a plus à compenser que celui des rangées. ⚠⚠ La limite de `221` vaut ici aussi :
la part du pas que les colonnes PARTAGENT ne se retire par aucun consensus.

Usage :
    uv run python src/nappe/le_consensus_traverse_t_il_la_hauteur.py --verifier
    uv run python src/nappe/le_consensus_traverse_t_il_la_hauteur.py --lire <lecture.json>
    uv run python src/nappe/le_consensus_traverse_t_il_la_hauteur.py --depuis <lecture.json> \\
        --json docs/mesures/le_consensus_traverse_t_il_la_hauteur.json
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

from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from combien_de_rangees_faut_il_pour_lire_le_pas import (LES_RANGEES,  # noqa: E402
                                                         les_bords_haut_et_bas,
                                                         un_chunk_retenu)
from combien_de_rangees_faut_il_pour_lire_le_pas import \
    les_rangees_a_lire as les_coupes_a_lire  # noqa: E402
from la_derive_saccumule_t_elle import LA_PAUSE_ENTRE_ESSAIS, la_largeur_du_bord  # noqa: E402
from la_recette_posee_sur_le_rouleau import DELAI  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import (LE_MINIMUM_DE_RANGEES,  # noqa: E402
                                                  le_consensus, le_plus_long,
                                                  le_theta_dune_autocorrelation,
                                                  les_troncons, lextrapolation, sur_letalon,
                                                  une_traversee)
from lecart_extreme_est_il_porte_par_une_rangee import LE_COMPTE_DECISIF  # noqa: E402
from les_boucles_se_ferment_elles import (LA_TOLERANCE_DE_REPRODUCTION,  # noqa: E402
                                          _un_pas)
from ou_le_maillage_quitte_t_il_son_feuillet import (le_segment_declare,  # noqa: E402
                                                     les_pannes_de_reseau, un_chunk)
from pourquoi_lerreur_declaree_est_trop_petite import lautocorrelation  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from zarr_depth import BUCKET, array_meta  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_222_A_RENDU = MESURES / "les_boucles_se_ferment_elles.json"
GRAINE = 20261104
LE_TRONCON_MINIMAL = 30

LA_QUESTION_DECLAREE = ("le consensus de cinq colonnes voisines, pris à chaque couture verticale, "
                        "traverse-t-il la hauteur du segment sans quitter le feuillet ?")
LA_MESURE_DECLAREE = ("la distance au départ du consensus des colonnes sur sa plus longue traversée "
                      "observée, puis sa marche médiane extrapolée par blocs à la hauteur entière, "
                      "contre le demi-feuillet — l'instrument de `221`, transposé")


# ─────────────────────────────── ce qui est relu ───────────────────────────────

def ce_que_222_a_rendu(chemin: Path = CE_QUE_222_A_RENDU) -> dict:
    """Les pas verticaux de `222`, sa grille et son nombre de rangées — relus, jamais recalculés."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable"):
        return {"decidable": False, "raison": "`222` est indécidable"}
    v_ = d.get("les_pas_verticaux")
    lignes = d.get("les_lignes") or {}
    grilles = {tuple(x.get("grille_de_chunks") or []) for x in lignes.values()}
    if not isinstance(v_, dict) or not v_ or len(grilles) != 1:
        return {"decidable": False, "raison": "`222` ne publie ni ses pas verticaux ni sa grille"}
    gy, gx = next(iter(grilles))
    pas = {int(r): {int(c): float(x[0]) for c, x in s.items()} for r, s in v_.items()}
    return {"decidable": True, "les_pas_verticaux": pas, "la_grille": [int(gy), int(gx)],
            "combien_de_rangees": len(d.get("les_rangees") or []),
            "les_rangees_de_222": [int(r) for r in (d.get("les_rangees") or [])]}


def les_colonnes_a_lire(colonnes_de_la_grille: int, combien: int) -> list[int]:
    """La colonne médiane de la grille et ses voisines — par la fonction même de `219`."""
    return les_rangees_a_lire(int(colonnes_de_la_grille) // 2, int(combien))


# ─────────────────────────────── la lecture ───────────────────────────────

def la_colonne(volume: dict, delai: float, colonne: int, ouvrir=None, meta=None,
               combien: int = LES_RANGEES) -> dict:
    """Les bords haut et bas de chaque chunk d'une COLONNE de chunks, du haut en bas.

    ⚠⚠ LE FILTRE ET LA COUPE SONT CEUX DE `la_ligne`, appelés et non recopiés : `un_chunk_retenu` et
    `les_bords_haut_et_bas`. Seul le sens de la marche change.
    """
    url = f"{BUCKET}/{volume['cle']}"
    if meta is None:
        try:
            meta = array_meta(url, 0, delai)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"le volume ne répond pas : {type(e).__name__}"}
    _, hy, hx = meta["chunks"]
    _, rows, cols = meta["shape"]
    gy, gx = -(-rows // hy), -(-cols // hx)
    if not 0 <= int(colonne) < gx:
        return {"decidable": False,
                "raison": f"la colonne {colonne} est hors du treillis de {gx} colonnes"}
    prendre = ouvrir or (lambda cy, cx: un_chunk(url, meta, cy, cx, delai, None,
                                                 pause=LA_PAUSE_ENTRE_ESSAIS))
    w = int(la_largeur_du_bord())
    bas, hauts, refus, reprises, coupes = {}, {}, {}, 0, None
    for cy in range(gy):
        b, pourquoi, repris = un_chunk_retenu(prendre, int(cy), int(colonne))
        reprises += repris
        if b is None:
            refus[pourquoi] = refus.get(pourquoi, 0) + 1
            continue
        if coupes is None:
            coupes = les_coupes_a_lire(b.shape[2], combien)
        bas[int(cy)], hauts[int(cy)] = les_bords_haut_et_bas(b, coupes, w)
    return {"decidable": bool(bas), "segment": volume["segment"],
            "grille_de_chunks": [int(gy), int(gx)], "la_colonne": int(colonne),
            "le_cote_du_chunk": int(hy), "la_largeur_du_bord": w,
            "les_colonnes_de_coupe": (coupes or []), "rangees_demandees": int(gy),
            "rangees_lues": len(bas), "les_reprises_du_reseau": int(reprises), "refuses": refus,
            "bas": bas, "hauts": hauts}


def les_pas_dune_colonne(lc: dict) -> dict:
    """Le pas de chaque couture verticale d'une colonne, indexé par la rangée du DESSUS — comme `222`."""
    out = {}
    coupes = lc.get("les_colonnes_de_coupe") or []
    for r in sorted(lc.get("bas") or {}):
        if (r + 1) not in (lc.get("hauts") or {}):
            continue
        x = _un_pas(lc["bas"][r], lc["hauts"][r + 1], coupes)
        if x is not None:
            out[int(r)] = x
    return out


def lire_les_colonnes(colonnes, delai: float = DELAI, ouvrir=None, meta=None, volume=None,
                      lire_une=None) -> dict:
    """Les pas verticaux de chaque colonne. ⚠⚠ Une colonne vide ou dont le fil est tombé arrête tout."""
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

        def lire_une(c):  # noqa: E306
            return la_colonne(volume, delai, int(c), ouvrir, meta)
    pas, lignes = {}, {}
    for c in [int(x) for x in colonnes]:
        lc = lire_une(c)
        if not lc.get("decidable"):
            return {"decidable": False, "raison": f"la colonne {c} est vide : {lc.get('raison')}"}
        pannes = les_pannes_de_reseau(lc.get("refuses"))
        if pannes:
            return {"decidable": False,
                    "raison": (f"{pannes} chunks perdus par le réseau sur la colonne {c} — une "
                               f"colonne dont le fil est tombé n'est pas comparable")}
        pas[c] = les_pas_dune_colonne(lc)
        lignes[c] = {k: x for k, x in lc.items() if k not in ("bas", "hauts")}
    return {"decidable": True, "v": pas, "les_colonnes_lues": lignes}


def publier_la_lecture(lu: dict) -> dict:
    """La lecture sous la forme qui se rejoue : `[pas, désaccord, coupes]` par couture."""
    return {"les_pas_verticaux_par_colonne": {
                str(c): {str(r): [round(float(x[0]), 4), round(float(x[1]), 4), int(x[2])]
                         for r, x in sorted(s.items())} for c, s in sorted(lu["v"].items())},
            "les_colonnes_lues": {str(c): x for c, x in sorted(lu["les_colonnes_lues"].items())}}


def relire_la_lecture(d: dict) -> dict:
    return {"decidable": True,
            "v": {int(c): {int(r): (float(t[0]), float(t[1]), int(t[2])) for r, t in s.items()}
                  for c, s in (d.get("les_pas_verticaux_par_colonne") or {}).items()},
            "les_colonnes_lues": d.get("les_colonnes_lues") or {}}


def la_reproduction(v: dict, par222: dict,
                    tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """Sur le recouvrement avec `222`, la marche en colonne retombe-t-elle sur ses pas ? Sinon, refus.

    ⚠⚠ LES MÊMES COUTURES DES DEUX CÔTÉS : un pas que l'un lit et l'autre non serait un chunk que les
    deux lecteurs ne retiennent pas pareil.
    """
    publies = par222["les_pas_verticaux"]
    ecarts, vus = {}, 0
    for c in sorted(v):
        for r in sorted(publies):
            chez_222 = c in publies[r]
            chez_moi = r in v[c]
            if chez_222 != chez_moi:
                return {"decidable": False,
                        "raison": (f"la couture ({r}, {c}) est lue par un seul des deux lecteurs")}
            if not chez_222:
                continue
            e = abs(float(v[c][r][0]) - float(publies[r][c]))
            if e > float(tolerance):
                return {"decidable": False,
                        "raison": (f"la couture ({r}, {c}) relue ne retombe pas sur `222` (écart "
                                   f"{e:.4g} voxel) — deux lecteurs différents")}
            ecarts[f"{r},{c}"] = e
            vus += 1
    if not vus:
        return {"decidable": False, "raison": "aucune couture commune avec `222`"}
    return {"decidable": True, "combien_de_coutures_relues": vus,
            "lecart_le_plus_grand": round(max(ecarts.values()), 6), "la_tolerance": float(tolerance)}


# ─────────────────────────────── l'analyse ───────────────────────────────

def _ce_qui_reste(observee: bool, extrapolee: bool) -> str:
    """Les trois issues de `221`, dites pour la hauteur — et elles sont EXCLUSIVES."""
    if not observee:
        return "LE CONSENSUS DES COLONNES QUITTE LE FEUILLET, MÊME SUR CE QU'IL LIT"
    if not extrapolee:
        return ("LE CONSENSUS DES COLONNES TRAVERSE CE QU'IL LIT, MAIS LA HAUTEUR ENTIÈRE LE FERAIT "
                "SORTIR DU FEUILLET")
    return "LE CONSENSUS DES COLONNES TRAVERSE LA HAUTEUR SANS QUITTER LE FEUILLET"


def analyser(pas: dict, N: int, graine: int = GRAINE, tirages: int = LE_COMPTE_DECISIF,
             replicats: int = 60, avec_etalon: bool = True) -> dict:
    """Tout ce qui se calcule sur les pas des colonnes — pur, et bloc par bloc celui de `221`.

    `pas` : `{colonne: {couture: pas}}` ; `N` : le nombre de coutures verticales d'une colonne.
    """
    cons = le_consensus(pas)
    tr = le_plus_long(cons)
    if len(tr) < LE_TRONCON_MINIMAL:
        return {"decidable": False, "raison": "le consensus n'a pas de tronçon utilisable"}
    steps = [cons[r] for r in tr]
    obs = une_traversee(steps)
    ext = lextrapolation(steps, N, tirages, graine)
    moy = le_consensus(pas, forme="moyenne")
    obs_moy = une_traversee([moy[r] for r in tr])
    apparies = {str(c): une_traversee([pas[c][r] for r in tr])
                for c in sorted(pas) if all(r in pas[c] for r in tr)}
    seules = {}
    for c in sorted(pas):
        t_ = le_plus_long(pas[c])
        if len(t_) < 2:
            continue
        st = [pas[c][r] for r in t_]
        seules[str(c)] = {"le_troncon": [int(t_[0]), int(t_[-1]), len(t_)],
                          **une_traversee(st), **lextrapolation(st, N, tirages, graine + 50 + c)}
    centre = np.asarray(steps) - float(np.mean(steps))
    rho1 = lautocorrelation(centre, 1)
    theta = le_theta_dune_autocorrelation(rho1 if rho1 is not None else 0.0)
    etalon = (sur_letalon(len(steps), N, theta, replicats, tirages, graine) if avec_etalon
              else None)

    def _cumul(st):
        return [round(float(x), 4) for x in np.concatenate(([0.0], np.cumsum(st)))]

    marches = {"le_consensus": _cumul(steps), "la_moyenne": _cumul([moy[r] for r in tr])}
    for c in apparies:
        marches[f"la_colonne_{c}"] = _cumul([pas[int(c)][r] for r in tr])
    return {"decidable": True, "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
            "le_minimum_de_colonnes": LE_MINIMUM_DE_RANGEES, "les_colonnes": sorted(pas),
            "les_coutures_dune_colonne": int(N), "les_coutures_avec_consensus": len(cons),
            "les_troncons_du_consensus": [[int(t[0]), int(t[-1]), len(t)]
                                          for t in les_troncons(cons)],
            "le_troncon_retenu": [int(tr[0]), int(tr[-1]), len(tr)],
            "les_troncons_par_colonne": {str(c): [[int(x[0]), int(x[-1]), len(x)]
                                                  for x in les_troncons(pas[c])]
                                         for c in sorted(pas)},
            "les_marches_du_troncon_retenu_en_voxels": marches,
            "la_traversee_du_consensus": obs, "lextrapolation_du_consensus": ext,
            "la_traversee_de_la_moyenne": obs_moy,
            "les_colonnes_seules_sur_le_meme_troncon": apparies,
            "les_colonnes_seules_sur_leur_plus_long_troncon": seules,
            "lautocorrelation_au_premier_decalage": (round(float(rho1), 4) if rho1 is not None
                                                     else None),
            "letalon_de_lextrapolation": etalon,
            "le_verdict": {
                "la_traversee_observee_reste_sous_le_demi_pli": obs["elle_reste_sous_le_demi_pli"],
                "lextrapolation_tient": ext["elle_tient_a_lechelle_de_la_rangee"],
                "lecart_des_blocs_a_la_verite":
                    (round(abs(etalon["le_rapport_median_par_blocs"] - 1.0), 4) if etalon else None),
                "ce_qui_reste_a_mesurer": _ce_qui_reste(obs["elle_reste_sous_le_demi_pli"],
                                                        ext["elle_tient_a_lechelle_de_la_rangee"])}}


def mesurer(depuis: Path | None = None, delai: float = DELAI, graine: int = GRAINE,
            tirages: int = LE_COMPTE_DECISIF, replicats: int = 60, ouvrir=None, meta=None,
            avec_etalon: bool = True) -> dict:
    """La lecture des cinq colonnes puis l'analyse — ou l'analyse seule, rejouée."""
    par222 = ce_que_222_a_rendu()
    if not par222.get("decidable"):
        return {"decidable": False, "raison": par222.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    gy, gx = par222["la_grille"]
    colonnes = les_colonnes_a_lire(gx, par222["combien_de_rangees"])
    if depuis is not None:
        lu = relire_la_lecture(json.loads(Path(depuis).read_text()))
    else:
        lu = lire_les_colonnes(colonnes, delai, ouvrir, meta)
        if not lu.get("decidable"):
            return {"decidable": False, "raison": lu.get("raison"),
                    "la_question_declaree": LA_QUESTION_DECLAREE}
    base = {"graine": int(graine), "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE,
            "les_colonnes_declarees": colonnes, **publier_la_lecture(lu)}
    if sorted(lu["v"]) != colonnes:
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des colonnes dérivées"}
    rep = la_reproduction(lu["v"], par222)
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = {c: {r: float(x[0]) for r, x in s.items()} for c, s in lu["v"].items()}
    a = analyser(pas, int(gy) - 1, graine, tirages, replicats, avec_etalon)
    return {**base, "la_reproduction": rep, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"reproduction de 222 : {rp['combien_de_coutures_relues']} coutures, écart "
          f"{rp['lecart_le_plus_grand']}")
    print(f"{r['les_coutures_avec_consensus']} coutures avec consensus sur "
          f"{r['les_coutures_dune_colonne']} · tronçons {r['les_troncons_du_consensus']} · retenu "
          f"{r['le_troncon_retenu']}")
    o = r["la_traversee_du_consensus"]
    print(f"  consensus · distance {o['la_distance_au_depart_en_voxels']} · σ "
          f"{o['lecart_type_des_pas_en_voxels']} · moyenne {o['la_moyenne_des_pas_en_voxels']} ± "
          f"{o['son_erreur_en_voxels']} · reste {o['elle_reste_sous_le_demi_pli']}")
    m = r["la_traversee_de_la_moyenne"]
    print(f"  moyenne · distance {m['la_distance_au_depart_en_voxels']} · σ "
          f"{m['lecart_type_des_pas_en_voxels']}")
    for k, x in r["les_colonnes_seules_sur_le_meme_troncon"].items():
        print(f"  colonne {k} seule, même tronçon · distance {x['la_distance_au_depart_en_voxels']}")
    e = r["lextrapolation_du_consensus"]
    print(f"  extrapolation · blocs {e['la_longueur_de_bloc']} · médiane "
          f"{e['la_marche_mediane_par_blocs_en_voxels']} ({e['les_marches_sous_le_demi_pli_par_blocs']}"
          f"/{e['tirages']}) · pas à pas {e['la_marche_mediane_pas_a_pas_en_voxels']}")
    for k, x in r["les_colonnes_seules_sur_leur_plus_long_troncon"].items():
        print(f"    colonne {k} · {x['le_troncon']} · distance {x['la_distance_au_depart_en_voxels']} · "
              f"blocs {x['la_marche_mediane_par_blocs_en_voxels']}")
    t = r.get("letalon_de_lextrapolation")
    if t:
        print(f"étalon · ρ1 {r['lautocorrelation_au_premier_decalage']} → θ {t['le_theta']} · blocs "
              f"{t['le_rapport_median_par_blocs']} · pas à pas {t['le_rapport_median_pas_a_pas']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import tempfile

    import combien_de_rangees_faut_il_pour_lire_le_pas as cdr
    from combien_de_rangees_faut_il_pour_lire_le_pas import la_ligne
    from les_boucles_se_ferment_elles import _une_grille, les_pas_verticaux
    from ou_le_maillage_quitte_t_il_son_feuillet import LE_RESEAU_A_ECHOUE
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom} {detail}")

    def _sur(f, *a, **k):
        try:
            return f(*a, **k)
        except Exception as e:  # noqa: BLE001
            return {"decidable": False, "raison": f"exception {type(e).__name__}: {e}"}

    v("★★★★ les colonnes sont la médiane de la grille et ses voisines, par la fonction de `219`",
      les_colonnes_a_lire(285, 5) == [140, 141, 142, 143, 144] and les_colonnes_a_lire(10, 3) == [4, 5, 6],
      str(les_colonnes_a_lire(285, 5)))

    # ⚠ LE FILTRE DE TEXTURE EST REMPLACÉ DANS LA SONDE, JAMAIS DANS LA MESURE — comme chez `222`.
    filtre = cdr.la_courbe_dun_bloc
    cdr.la_courbe_dun_bloc = lambda b: ([], None)
    try:
        al, be, ga, ba_ = 3, -2, 1, 5
        ouvrir, meta = _une_grille(4, 3, 60, 32, lambda r, c: al * r + be * c + ga * r * c, 7,
                                   droite=2, bas=ba_)
        vol = {"cle": "x", "segment": "s"}
        lc = _sur(la_colonne, vol, 0.0, 1, ouvrir, meta, 16)
        pc = les_pas_dune_colonne(lc) if lc.get("decidable") else {}
        v("★★★★ le pas d'une couture verticale est la profondeur du dessous moins celle du dessus",
          sorted(pc) == [0, 1, 2] and all(abs(pc[r][0] - (al + ga * 1 - ba_)) < 1e-9 for r in pc),
          str({r: x[0] for r, x in pc.items()}))
        lignes = {r: la_ligne(vol, 0.0, None, ouvrir, meta, 16, r, les_bords_verticaux=True)
                  for r in range(4)}
        par_ligne = {r: les_pas_verticaux(lignes[r], lignes[r + 1]) for r in range(3)}
        tous = [_sur(la_colonne, vol, 0.0, c, ouvrir, meta, 16) for c in range(3)]
        v("★★★★ la marche en colonne et la marche en rangée lisent EXACTEMENT les mêmes pas",
          all(les_pas_dune_colonne(tous[c]) == {r: par_ligne[r][c] for r in range(3)}
              for c in range(3)))
        v("★★★ une colonne hors de la grille est refusée",
          not _sur(la_colonne, vol, 0.0, 3, ouvrir, meta, 16).get("decidable"))
        trou = lambda cy, cx: (None, "absent du dépôt") if cy == 2 else ouvrir(cy, cx)  # noqa: E731
        lt = _sur(la_colonne, vol, 0.0, 1, trou, meta, 16)
        v("★★★ un chunk absent coupe les deux coutures qui le touchent, et est compté",
          sorted(les_pas_dune_colonne(lt)) == [0] and lt["refuses"].get("absent du dépôt") == 1,
          str(sorted(les_pas_dune_colonne(lt))))
        panne = _sur(lire_les_colonnes, [0, 1], lire_une=lambda c: {
            **la_colonne(vol, 0.0, c, ouvrir, meta, 16), "refuses": {f"{LE_RESEAU_A_ECHOUE} x": 1}})
        v("★★★ une colonne dont le fil est tombé est refusée, par sa raison",
          not panne.get("decidable") and "réseau" in str(panne.get("raison")), str(panne.get("raison")))
        vide = _sur(lire_les_colonnes, [0], lire_une=lambda c: {"decidable": False})
        v("★★ une colonne vide est refusée", not vide.get("decidable"))
        lu = _sur(lire_les_colonnes, [0, 1, 2], lire_une=lambda c: la_colonne(vol, 0.0, c, ouvrir,
                                                                              meta, 16))
        v("★★★ la lecture se publie et se relit à la quatrième décimale",
          lu.get("decidable") and relire_la_lecture(json.loads(json.dumps(publier_la_lecture(lu))))["v"]
          == {c: {r: (round(x[0], 4), round(x[1], 4), x[2]) for r, x in s.items()}
              for c, s in lu["v"].items()})
        # ⚠⚠ ET LE FILTRE EST BIEN APPELÉ : un filtre qui refuse tout vide la colonne, par sa raison.
        cdr.la_courbe_dun_bloc = lambda b: (None, "trop peu texturé")
        tout_refuse = _sur(la_colonne, vol, 0.0, 1, ouvrir, meta, 16)
        v("★★★★ le filtre du producteur est appelé sur chaque chunk de la colonne",
          not tout_refuse.get("decidable")
          and (tout_refuse.get("refuses") or {}).get("trop peu texturé") == 4, str(tout_refuse.get("refuses")))
    finally:
        cdr.la_courbe_dun_bloc = filtre

    # la reproduction de 222
    p222 = {"les_pas_verticaux": {196: {140: 1.5, 141: -2.0}, 197: {140: 0.25}}}
    vv = {140: {196: (1.5, 0.0, 16), 197: (0.25, 0.0, 16), 50: (9.0, 0.0, 16)},
          141: {196: (-2.0, 0.0, 16)}}
    rp = _sur(la_reproduction, vv, p222)
    v("★★★ des pas qui retombent sont reproduits, sur les seules coutures communes",
      rp.get("decidable") and rp["combien_de_coutures_relues"] == 3, str(rp))
    v("★★★★ un écart au-delà de l'arrondi est refusé", not _sur(la_reproduction, {
        140: {196: (1.6, 0.0, 16), 197: (0.25, 0.0, 16)}, 141: {196: (-2.0, 0.0, 16)}},
        p222).get("decidable"))
    v("★★★★ une couture lue par un seul des deux lecteurs est refusée", not _sur(la_reproduction, {
        140: {196: (1.5, 0.0, 16)}, 141: {196: (-2.0, 0.0, 16)}}, p222).get("decidable"))
    v("★★★ et dans l'autre sens aussi", not _sur(la_reproduction, {
        140: {196: (1.5, 0.0, 16), 197: (0.25, 0.0, 16)},
        141: {196: (-2.0, 0.0, 16), 197: (3.0, 0.0, 16)}}, p222).get("decidable"))
    v("★★ sans recouvrement, pas de reproduction",
      not _sur(la_reproduction, {7: {1: (0.0, 0.0, 16)}}, {"les_pas_verticaux": {196: {}}}).get("decidable"))

    # l'analyse : l'instrument de 221, transposé
    g = np.random.default_rng(3)
    N = 120
    pas = {c: {r: float(g.normal(0.0, 1.0)) for r in range(N)} for c in range(5)}
    for r in range(40, 45):
        pas[0].pop(r)
    for r in range(30, 33):
        for c in (1, 2, 3):
            pas[c].pop(r)
    pas[4][50] = 500.0
    a = _sur(analyser, pas, N, 5, 20, 6, True)
    ok_a = bool(a.get("decidable"))

    def _a(f):  # noqa: E306
        # ⚠⚠ chaque sonde de l'analyse TOURNE, même quand l'analyse a échoué : sinon un bris qui fait
        # lever l'analyse retirerait ses sondes au lieu de les rougir.
        try:
            return ok_a and bool(f())
        except Exception:  # noqa: BLE001
            return False
    v("★★★ l'analyse est décidable sur une matière fabriquée", ok_a, str(a.get("raison")))
    v("★★★★ le consensus franchit le trou d'une colonne et s'arrête où la majorité manque",
      _a(lambda: a["le_troncon_retenu"] == [33, N - 1, N - 33]
         and a["les_coutures_avec_consensus"] == N - 3), str(a.get("le_troncon_retenu")))
    v("★★★★ la médiane ignore la couture où une seule colonne s'écarte",
      _a(lambda: max(abs(x) for x in a["les_marches_du_troncon_retenu_en_voxels"]["le_consensus"])
         < 60.0))
    v("★★★ le contrôle apparié ne prend que les colonnes sans trou sur le tronçon",
      _a(lambda: sorted(a["les_colonnes_seules_sur_le_meme_troncon"]) == ["1", "2", "3", "4"]))
    v("★★★ chaque marche publiée a la longueur du tronçon",
      _a(lambda: all(len(x) == a["le_troncon_retenu"][2] + 1
                     for x in a["les_marches_du_troncon_retenu_en_voxels"].values())))
    v("★★★ l'extrapolation porte sur la hauteur entière, par blocs de ⌈n^(1/3)⌉",
      _a(lambda: a["lextrapolation_du_consensus"]["la_longueur_de_bloc"] == 5
         and a["les_coutures_dune_colonne"] == N))
    cons_ = le_consensus(pas)
    v("★★★★ et elle est celle de `221` sur les pas du consensus, à la longueur de la HAUTEUR",
      _a(lambda: a["lextrapolation_du_consensus"]
         == lextrapolation([cons_[r] for r in range(33, N)], N, 20, 5)))

    def _theta():  # noqa: E306
        et_ = a["letalon_de_lextrapolation"] or {}
        th_ = le_theta_dune_autocorrelation(a["lautocorrelation_au_premier_decalage"])
        return ("le_rapport_median_par_blocs" in et_ and abs(th_) > 1e-3
                and abs(float(et_.get("le_theta", 99.0)) - th_) < 1e-3)
    v("★★★★ l'étalon est celui de `221`, au θ DÉRIVÉ de l'autocorrélation du consensus", _a(_theta))
    court = {c: {r: 0.0 for r in range(10)} for c in range(5)}
    v("★★ un consensus sans tronçon utilisable est indécidable",
      not _sur(analyser, court, 10, 5, 5, 2, False).get("decidable"))

    # les issues
    iss = {_ce_qui_reste(o, e) for o in (True, False) for e in (True, False)}
    v("★★★★ trois issues distinctes, et sortir sur ce qu'on lit prime",
      len(iss) == 3 and _ce_qui_reste(False, True) == _ce_qui_reste(False, False))
    v("★★★ les deux qui restent disent la hauteur",
      "HAUTEUR" in _ce_qui_reste(True, True) and "HAUTEUR" in _ce_qui_reste(True, False))

    # la mesure refuse une lecture qui n'est pas celle des colonnes dérivées, ou qui ne retombe pas
    par = ce_que_222_a_rendu()
    v("★★★ `222` est relu, avec sa grille et ses cinq rangées",
      par.get("decidable") and par["la_grille"] == [396, 285] and par["combien_de_rangees"] == 5)
    if par.get("decidable"):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "l.json"
            f.write_text(json.dumps({"les_pas_verticaux_par_colonne": {
                "1": {"196": [0.0, 0.0, 16]}}, "les_colonnes_lues": {}}))
            autre = _sur(mesurer, f, replicats=2, avec_etalon=False)
            v("★★★★ une lecture d'autres colonnes que les colonnes dérivées est refusée, par sa raison",
              not autre.get("decidable") and "colonnes dérivées" in str(autre.get("raison")),
              str(autre.get("raison")))
            cols = les_colonnes_a_lire(285, 5)
            faux = {str(c): {str(r): [par["les_pas_verticaux"][r][c] + 1.0, 0.0, 16]
                             for r in par["les_pas_verticaux"] if c in par["les_pas_verticaux"][r]}
                    for c in cols}
            f.write_text(json.dumps({"les_pas_verticaux_par_colonne": faux, "les_colonnes_lues": {}}))
            m = _sur(mesurer, f, replicats=2, avec_etalon=False)
            v("★★★★ une lecture qui ne retombe pas sur `222` est refusée par sa raison",
              not m.get("decidable") and "ne retombe pas" in str(m.get("raison")), str(m.get("raison")))
            # ⭐ une lecture fabriquée qui retombe sur `222` passe TOUTE la mesure
            gg = np.random.default_rng(9)
            juste = {str(c): {str(r): ([par["les_pas_verticaux"][r][c], 0.0, 16]
                                       if r in par["les_pas_verticaux"] else
                                       [round(float(gg.normal(0.0, 1.0)), 4), 0.0, 16])
                              for r in range(395)} for c in cols}
            f.write_text(json.dumps({"les_pas_verticaux_par_colonne": juste, "les_colonnes_lues": {}}))
            ok = _sur(mesurer, f, tirages=20, replicats=2, avec_etalon=False)
            v("★★★★ une lecture qui retombe passe la mesure entière, sur 395 coutures par colonne",
              ok.get("decidable") and ok["les_coutures_dune_colonne"] == 395
              and ok["la_reproduction"]["combien_de_coutures_relues"] == 20
              and ok["les_colonnes_declarees"] == cols, str(ok.get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lire", type=Path, default=None,
                   help="lit les cinq colonnes sur toute la hauteur et écrit la lecture seule")
    p.add_argument("--depuis", type=Path, default=None,
                   help="rejoue l'analyse depuis une lecture, sans relire le volume")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--replicats", type=int, default=60)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        par = ce_que_222_a_rendu()
        if not par.get("decidable"):
            print(f"indécidable : {par.get('raison')}")
            return 1
        lu = lire_les_colonnes(les_colonnes_a_lire(par["la_grille"][1], par["combien_de_rangees"]))
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
        a.lire.parent.mkdir(parents=True, exist_ok=True)
        a.lire.write_text(json.dumps(publier_la_lecture(lu), ensure_ascii=False, indent=1))
        print(f"écrit : {a.lire}")
        return 0
    r = mesurer(a.depuis, DELAI, a.graine, a.tirages, a.replicats, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
