"""Le consensus de cinq voisines, pris à chaque couture, traverse-t-il la rangée sans quitter le feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE CONSENSUS NE SOIT CALCULÉ SUR LA MATIÈRE. La seule chose
regardée avant d'écrire est la COUVERTURE — combien de colonnes ont assez de rangées pour voter —,
jamais un pas.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P66`. `220` établit que le vote aux seules colonnes fortes
retire les extrêmes sans garder les rangées ensemble : ce qui les sépare est la marche des coutures
ordinaires. Si chaque rangée prend, à CHAQUE couture, ce que disent ses voisines, les rangées ne se
séparent plus — par construction. La question devient celle de `210` : la marche du consensus reste-
t-elle à moins d'un demi-feuillet de son départ ?

⭐⭐ AUCUNE LECTURE NEUVE : `219` publie les pas des cinq rangées colonne par colonne.

## Le consensus, déclaré

À chaque couture, la MÉDIANE des pas des rangées présentes, pourvu qu'elles soient au moins TROIS —
la majorité de cinq, sans quoi il n'y a pas de vote. ⭐ C'est ce qui rend la traversée possible : une
rangée seule a des trous (chunks absents du dépôt, trop peu texturés) là où ses voisines lisent, et le
consensus les franchit tant que la majorité est là. ⚠ La moyenne des rangées présentes, qui est ce
que `210` moyennait, est portée comme contrôle nommé.

## Ce qui se mesure, dans l'ordre

1. ⭐⭐⭐⭐ LA TRAVERSÉE OBSERVÉE — la seule qui ne suppose rien. Sur le plus long tronçon où le
   consensus existe sans interruption, la distance au départ `max_k |S_k|`, `S` étant le cumul des pas
   du consensus parti de zéro, contre le demi-feuillet.
2. ⭐⭐ LE CONTRÔLE APPARIÉ — une rangée seule sur le MÊME tronçon, quand l'une le couvre sans trou :
   même départ, mêmes coutures, donc leur comparaison ne contient aucune correction de longueur. C'est
   le contrôle de `210`.
3. ⭐⭐ L'EXTRAPOLATION À UNE RANGÉE ENTIÈRE, par blocs : des pas CENTRÉS (`R4-L22`) tirés par blocs
   mobiles de longueur `⌈n^(1/3)⌉` (la règle de `217`), pour garder la dépendance courte que `220` a vue
   — une marche qui revient sur elle-même s'étale moins que des pas indépendants. Le consensus TIENT à
   cette échelle quand la marche médiane reste sous le demi-feuillet. Le tirage pas à pas est publié à
   côté, comme contrôle nommé.

## L'étalon de l'extrapolation, et ce qu'il doit montrer

⚠⚠⚠ UNE EXTRAPOLATION N'EST PAS UNE MESURE, ET ELLE SE VÉRIFIE SUR UNE MATIÈRE DONT ON CONNAÎT LA
RÉPONSE. Des séries à dépendance d'un pas — `s_i = e_i - θ·e_(i-1)`, la forme exacte d'un chunk mal
recalé qui déplace une couture et rend le déplacement à la suivante — dont le `θ` est DÉRIVÉ de
l'autocorrélation au premier décalage que la matière montre. On connaît la marche médiane d'une
rangée entière sous ce modèle ; on demande à chaque instrument de la retrouver depuis un seul tronçon
de la longueur observée. L'instrument retenu est celui qui s'en approche.

## Les issues, exclusives

- la traversée observée quitte le feuillet : le consensus ne suffit pas, même sur ce qu'il lit ;
- elle reste, mais l'extrapolation dit qu'une rangée entière le quitterait : il traverse ce qu'il lit,
  pas une rangée ;
- les deux restent : le consensus traverse la rangée sans quitter le feuillet.

⚠⚠⚠ ET LA LIMITE EST ÉCRITE D'AVANCE : la part du pas que les rangées PARTAGENT (`208`) ne se retire par
aucun consensus. Elle est la géométrie de la matière ou une erreur commune, et rien de local ne le
dit. Ce que le consensus mesure est ce qui reste quand les erreurs PROPRES se compensent.

Usage :
    uv run python src/nappe/le_consensus_traverse_t_il_la_rangee.py --verifier
    uv run python src/nappe/le_consensus_traverse_t_il_la_rangee.py \\
        --json docs/mesures/le_consensus_traverse_t_il_la_rangee.json
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

from lecart_extreme_est_il_porte_par_une_rangee import LE_COMPTE_DECISIF  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import (  # noqa: E402
    ce_que_219_a_rendu, la_separation, les_marches_independantes)
from ouvrir_les_quinze import _rng  # noqa: E402
from pourquoi_lerreur_declaree_est_trop_petite import (la_longueur_de_bloc,  # noqa: E402
                                                       lautocorrelation)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
GRAINE = 20261102
LE_MINIMUM_DE_RANGEES = 3

LA_QUESTION_DECLAREE = ("le consensus de cinq voisines, pris à chaque couture, traverse-t-il la "
                        "rangée sans quitter le feuillet ?")
LA_MESURE_DECLAREE = ("la distance au départ du consensus sur sa plus longue traversée observée, puis "
                      "sa marche médiane extrapolée par blocs à une rangée entière, contre le "
                      "demi-feuillet")


def le_consensus(pas: dict, minimum: int = LE_MINIMUM_DE_RANGEES, forme: str = "mediane") -> dict:
    """Le pas du consensus à chaque couture où au moins `minimum` rangées ont lu — et rien d'autre.

    ⚠⚠ UNE COUTURE SANS MAJORITÉ N'A PAS DE CONSENSUS, ELLE N'EN A PAS UN MOINS BON : la compter
    ferait voter une rangée seule sous le nom d'un consensus.
    """
    colonnes = sorted(set().union(*[set(x) for x in pas.values()]))
    out = {}
    for c in colonnes:
        v = [pas[r][c] for r in pas if c in pas[r]]
        if len(v) >= int(minimum):
            out[int(c)] = float(np.median(v) if forme == "mediane" else np.mean(v))
    return out


def les_troncons(colonnes) -> list[list[int]]:
    """Les suites de colonnes CONTIGUËS, dans l'ordre."""
    cols = sorted(int(c) for c in colonnes)
    if not cols:
        return []
    out, courant = [], [cols[0]]
    for c in cols[1:]:
        if c == courant[-1] + 1:
            courant.append(c)
        else:
            out.append(courant)
            courant = [c]
    out.append(courant)
    return out


def le_plus_long(colonnes) -> list[int]:
    """Le plus long tronçon contigu — le premier à égalité."""
    tr = les_troncons(colonnes)
    return max(tr, key=len) if tr else []


def les_marches_par_blocs(pas, longueur: int, tirages: int, graine: int, bloc: int) -> np.ndarray:
    """Les distances au départ de marches de `longueur` pas CENTRÉS tirés par blocs mobiles.

    ⚠⚠ CENTRÉS, parce qu'une marche extrapolée qui garde la moyenne de son échantillon mesure
    l'erreur de cette moyenne (`R4-L22`). ⚠ PAR BLOCS, parce qu'un bloc garde la dépendance courte
    qu'un tirage pas à pas détruirait.
    """
    a = np.asarray(pas, dtype=float)
    a = a - float(np.mean(a))
    n, b = len(a), max(1, min(int(bloc), len(a)))
    g = _rng(int(graine))
    out = []
    for _ in range(int(tirages)):
        idx = []
        while len(idx) < int(longueur):
            d = int(g.integers(0, n - b + 1))
            idx.extend(range(d, d + b))
        out.append(la_separation(a[np.asarray(idx[:int(longueur)])]))
    return np.asarray(out)


def le_theta_dune_autocorrelation(rho1: float) -> float:
    """Le `θ` d'une dépendance d'un pas `s_i = e_i - θ·e_(i-1)` qui rend l'autocorrélation `ρ1`.

    ⚠ `ρ1 = -θ/(1+θ²)` ne vaut qu'entre `-1/2` et `1/2` : au-delà, aucune dépendance d'un pas ne le
    rend, et l'autocorrélation est écrêtée plutôt que de rendre un `θ` imaginaire. La racine gardée
    est celle de module inférieur à un.
    """
    r = max(-0.49, min(0.49, float(rho1)))
    if abs(r) < 1e-12:
        return 0.0
    return float((-1.0 + np.sqrt(1.0 - 4.0 * r * r)) / (2.0 * r))


def une_serie_dependante(theta: float, n: int, graine: int) -> np.ndarray:
    """`s_i = e_i - θ·e_(i-1)`, `e` gaussien réduit — la matière de l'étalon."""
    g = _rng(int(graine))
    e = g.normal(0.0, 1.0, int(n) + 1)
    return e[1:] - float(theta) * e[:-1]


def sur_letalon(n: int, longueur: int, theta: float, replicats: int = 60,
                tirages: int = LE_COMPTE_DECISIF, graine: int = GRAINE,
                verites: int = 999) -> dict:
    """L'étalon de l'extrapolation : chaque instrument retrouve-t-il la marche d'une rangée entière ?

    ⚠⚠⚠ LA VÉRITÉ EST CONNUE : `verites` séries de la longueur d'une rangée, sous le même modèle, en
    donnent la marche médiane. Chaque réplicat ne voit qu'UN tronçon de longueur `n`, comme la matière,
    et chaque instrument en tire son estimation. Le rapport à la vérité dit qui se trompe, et de combien.
    """
    vraies = [la_separation(une_serie_dependante(theta, longueur, int(graine) + 7 * i))
              for i in range(int(verites))]
    verite = float(np.median(vraies))
    bloc = la_longueur_de_bloc(n)
    par_blocs, pas_a_pas = [], []
    for i in range(int(replicats)):
        s = une_serie_dependante(theta, n, int(graine) + 100000 + 11 * i)
        par_blocs.append(float(np.median(les_marches_par_blocs(s, longueur, tirages,
                                                               int(graine) + 3 * i, bloc))) / verite)
        c = s - float(np.mean(s))
        pas_a_pas.append(float(np.median(les_marches_independantes(c, longueur, tirages,
                                                                    int(graine) + 5 * i, True)))
                         / verite)
    mb, mi = float(np.median(par_blocs)), float(np.median(pas_a_pas))
    return {"decidable": True, "le_theta": round(float(theta), 4), "les_coutures_du_troncon": int(n),
            "les_coutures_dune_rangee": int(longueur), "la_longueur_de_bloc": int(bloc),
            "les_replicats": int(replicats), "les_verites": int(verites),
            "la_marche_mediane_vraie_en_ecarts_types": round(verite, 4),
            "le_rapport_median_par_blocs": round(mb, 4),
            "le_rapport_median_pas_a_pas": round(mi, 4),
            "les_blocs_sapprochent_le_plus": bool(abs(mb - 1.0) <= abs(mi - 1.0))}


def une_traversee(steps: list[float], demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Une marche observée : sa distance au départ, son étendue, et sa moyenne avec son erreur."""
    a = np.asarray(steps, dtype=float)
    s = np.concatenate(([0.0], np.cumsum(a)))
    se = float(np.std(a)) / np.sqrt(len(a)) if len(a) > 0 else None
    return {"les_coutures": int(len(a)),
            "la_distance_au_depart_en_voxels": round(float(np.max(np.abs(s))), 4),
            "letendue_en_voxels": round(float(s.max() - s.min()), 4),
            "le_deplacement_net_en_voxels": round(float(s[-1]), 4),
            "lecart_type_des_pas_en_voxels": round(float(np.std(a)), 4),
            "la_moyenne_des_pas_en_voxels": round(float(np.mean(a)), 4),
            "son_erreur_en_voxels": (round(se, 4) if se else None),
            "elle_reste_sous_le_demi_pli": bool(float(np.max(np.abs(s))) < float(demi))}


def lextrapolation(steps, longueur: int, tirages: int, graine: int,
                   demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """La marche médiane d'une rangée entière, par blocs (retenue) et pas à pas (contrôle nommé)."""
    bloc = la_longueur_de_bloc(len(steps))
    pb = les_marches_par_blocs(steps, longueur, tirages, graine, bloc)
    c = np.asarray(steps, dtype=float) - float(np.mean(steps))
    pi = les_marches_independantes(c, longueur, tirages, graine + 1, True)
    return {"la_longueur_de_bloc": int(bloc), "tirages": int(tirages),
            "la_marche_mediane_par_blocs_en_voxels": round(float(np.median(pb)), 4),
            "les_marches_sous_le_demi_pli_par_blocs": int(np.sum(pb < float(demi))),
            "la_marche_mediane_pas_a_pas_en_voxels": round(float(np.median(pi)), 4),
            "les_marches_sous_le_demi_pli_pas_a_pas": int(np.sum(pi < float(demi))),
            "elle_tient_a_lechelle_de_la_rangee": bool(float(np.median(pb)) < float(demi))}


def _ce_qui_reste(observee: bool, extrapolee: bool) -> str:
    """Les trois issues, et elles sont EXCLUSIVES."""
    if not observee:
        return "LE CONSENSUS QUITTE LE FEUILLET, MÊME SUR CE QU'IL LIT"
    if not extrapolee:
        return ("LE CONSENSUS TRAVERSE CE QU'IL LIT, MAIS UNE RANGÉE ENTIÈRE LE FERAIT SORTIR DU "
                "FEUILLET")
    return "LE CONSENSUS TRAVERSE LA RANGÉE SANS QUITTER LE FEUILLET"


def mesurer(graine: int = GRAINE, tirages: int = LE_COMPTE_DECISIF, replicats: int = 60,
            avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    lu = ce_que_219_a_rendu()
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    pas, N = lu["les_pas_par_rangee"], int(lu["les_coutures_dune_rangee"])
    cons = le_consensus(pas)
    tr = le_plus_long(cons)
    if len(tr) < 30:
        return {"decidable": False, "raison": "le consensus n'a pas de tronçon utilisable",
                "la_question_declaree": LA_QUESTION_DECLAREE}
    steps = [cons[c] for c in tr]
    obs = une_traversee(steps)
    ext = lextrapolation(steps, N, tirages, graine)
    moy = le_consensus(pas, forme="moyenne")
    obs_moy = une_traversee([moy[c] for c in tr])
    apparies = {}
    for r in sorted(pas):
        if all(c in pas[r] for c in tr):
            apparies[str(r)] = une_traversee([pas[r][c] for c in tr])
    seules = {}
    for r in sorted(pas):
        t_ = le_plus_long(pas[r])
        st = [pas[r][c] for c in t_]
        seules[str(r)] = {"le_troncon": [int(t_[0]), int(t_[-1]), len(t_)],
                          **une_traversee(st), **lextrapolation(st, N, tirages, graine + 50 + r)}
    c = np.asarray(steps) - float(np.mean(steps))
    rho1 = lautocorrelation(c, 1)
    theta = le_theta_dune_autocorrelation(rho1 if rho1 is not None else 0.0)
    etalon = (sur_letalon(len(steps), N, theta, replicats, tirages, graine) if avec_etalon else None)
    couverture = les_troncons(cons)

    def _cumul(st):
        return [round(float(x), 4) for x in np.concatenate(([0.0], np.cumsum(st)))]

    # ⚠⚠ LES MARCHES ELLES-MEMES SONT PUBLIEES, pour que la figure trace ce qui a ete mesure et non
    # un resume, et que la distance au depart se relise a la main.
    marches = {"le_consensus": _cumul(steps), "la_moyenne": _cumul([moy[c] for c in tr])}
    for r in apparies:
        marches[f"la_rangee_{r}"] = _cumul([pas[int(r)][c] for c in tr])
    return {"decidable": True, "graine": int(graine), "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE,
            "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
            "le_minimum_de_rangees": LE_MINIMUM_DE_RANGEES, "les_rangees": sorted(pas),
            "les_coutures_dune_rangee": N,
            "les_coutures_avec_consensus": len(cons),
            "les_troncons_du_consensus": [[int(t[0]), int(t[-1]), len(t)] for t in couverture],
            "le_troncon_retenu": [int(tr[0]), int(tr[-1]), len(tr)],
            "les_troncons_par_rangee": {str(r): [[int(x[0]), int(x[-1]), len(x)]
                                                 for x in les_troncons(pas[r])] for r in sorted(pas)},
            "les_marches_du_troncon_retenu_en_voxels": marches,
            "la_traversee_du_consensus": obs,
            "lextrapolation_du_consensus": ext,
            "la_traversee_de_la_moyenne": obs_moy,
            "les_rangees_seules_sur_le_meme_troncon": apparies,
            "les_rangees_seules_sur_leur_plus_long_troncon": seules,
            "lautocorrelation_au_premier_decalage": (round(float(rho1), 4) if rho1 is not None
                                                     else None),
            "letalon_de_lextrapolation": etalon,
            "le_verdict": {
                "la_traversee_observee_reste_sous_le_demi_pli": obs["elle_reste_sous_le_demi_pli"],
                "lextrapolation_tient": ext["elle_tient_a_lechelle_de_la_rangee"],
                # ⚠⚠ UN ECART A LA VERITE, PAS UN BOOLEEN : quand la matiere ne montre aucune
                # dependance, les deux instruments rendent la verite et « lequel s'en approche le plus »
                # ne dit plus rien. C'est l'ecart de l'instrument retenu qui dit s'il est juste.
                "lecart_des_blocs_a_la_verite":
                    (round(abs(etalon["le_rapport_median_par_blocs"] - 1.0), 4) if etalon else None),
                "ce_qui_reste_a_mesurer": _ce_qui_reste(obs["elle_reste_sous_le_demi_pli"],
                                                        ext["elle_tient_a_lechelle_de_la_rangee"])}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"\n{r['les_coutures_avec_consensus']} coutures avec consensus sur {r['les_coutures_dune_rangee']}"
          f" · tronçons {r['les_troncons_du_consensus']} · retenu {r['le_troncon_retenu']}")
    o = r["la_traversee_du_consensus"]
    print(f"  consensus · distance au départ {o['la_distance_au_depart_en_voxels']} · étendue "
          f"{o['letendue_en_voxels']} · net {o['le_deplacement_net_en_voxels']} · σ "
          f"{o['lecart_type_des_pas_en_voxels']} · moyenne {o['la_moyenne_des_pas_en_voxels']} ± "
          f"{o['son_erreur_en_voxels']} · reste {o['elle_reste_sous_le_demi_pli']}")
    m = r["la_traversee_de_la_moyenne"]
    print(f"  moyenne (contrôle) · distance {m['la_distance_au_depart_en_voxels']} · σ "
          f"{m['lecart_type_des_pas_en_voxels']}")
    for k, x in r["les_rangees_seules_sur_le_meme_troncon"].items():
        print(f"  rangée {k} seule, même tronçon · distance {x['la_distance_au_depart_en_voxels']} · σ "
              f"{x['lecart_type_des_pas_en_voxels']}")
    e = r["lextrapolation_du_consensus"]
    print(f"  extrapolation · blocs de {e['la_longueur_de_bloc']} · médiane {e['la_marche_mediane_par_blocs_en_voxels']}"
          f" ({e['les_marches_sous_le_demi_pli_par_blocs']}/{e['tirages']} sous) · pas à pas "
          f"{e['la_marche_mediane_pas_a_pas_en_voxels']} · tient {e['elle_tient_a_lechelle_de_la_rangee']}")
    for k, x in r["les_rangees_seules_sur_leur_plus_long_troncon"].items():
        print(f"    rangée {k} · tronçon {x['le_troncon']} · distance {x['la_distance_au_depart_en_voxels']}"
              f" · médiane par blocs {x['la_marche_mediane_par_blocs_en_voxels']} · tient "
              f"{x['elle_tient_a_lechelle_de_la_rangee']}")
    t = r.get("letalon_de_lextrapolation")
    if t:
        print(f"\nÉTALON · ρ1 {r['lautocorrelation_au_premier_decalage']} → θ {t['le_theta']} · vérité "
              f"{t['la_marche_mediane_vraie_en_ecarts_types']} σ · par blocs {t['le_rapport_median_par_blocs']}"
              f" · pas à pas {t['le_rapport_median_pas_a_pas']} · blocs plus justes "
              f"{t['les_blocs_sapprochent_le_plus']}")
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

    v("★★★ une seule question et une seule mesure sont déclarées",
      isinstance(LA_QUESTION_DECLAREE, str) and isinstance(LA_MESURE_DECLAREE, str))
    v("★★★★ le minimum de rangées est la majorité de cinq", LE_MINIMUM_DE_RANGEES == 3)

    # ⭐⭐⭐ LE CONSENSUS.
    pas_x = {1: {0: 1.0, 1: 5.0, 2: 0.0}, 2: {0: 2.0, 1: 5.0}, 3: {0: 30.0, 2: 0.0},
             4: {0: 3.0}, 5: {1: 5.0}}
    cx = _sur(le_consensus, pas_x)
    v("★★★★ le consensus est la MÉDIANE des rangées présentes : une rangée folle ne l'emporte pas",
      lambda: cx[0] == 2.5 and cx[1] == 5.0)
    v("★★★★ une couture sans majorité n'a PAS de consensus", lambda: 2 not in cx)
    v("★★★★ la moyenne, contrôle nommé, se laisse emporter là où la médiane résiste",
      lambda: le_consensus(pas_x, forme="moyenne")[0] == 9.0)
    v("★★★ les tronçons sont contigus et dans l'ordre",
      les_troncons([5, 1, 2, 3, 9, 10]) == [[1, 2, 3], [5], [9, 10]]
      and le_plus_long([1, 2, 5, 6]) == [1, 2] and le_plus_long([1, 4, 5, 6]) == [4, 5, 6])

    # ⭐⭐⭐ LA TRAVERSEE.
    tv = une_traversee([10.0, -30.0, 5.0])
    v("★★★★ la distance au départ n'est pas l'étendue, et la moyenne porte son erreur",
      tv["la_distance_au_depart_en_voxels"] == 20.0 and tv["letendue_en_voxels"] == 30.0
      and tv["son_erreur_en_voxels"] > 0)
    v("★★★ une marche plate reste sous le demi-pli", une_traversee([0.0] * 50)["elle_reste_sous_le_demi_pli"])

    # ⭐⭐⭐ LES BLOCS.
    mb = les_marches_par_blocs([1.0, -1.0] * 50, 300, 20, 3, 2)
    v("★★★★ des blocs de deux gardent l'alternance : la marche ne dépasse jamais un pas",
      len(mb) == 20 and float(mb.max()) <= 1.0 + 1e-12, str(mb.max()))
    v("★★★★ des pas tirés un à un la détruisent : la marche s'étale bien plus loin",
      lambda: float(np.median(les_marches_independantes(np.asarray([1.0, -1.0] * 50), 300, 20, 3,
                                                        True))) > 5.0)
    alt = [10.0, -10.0] * 108
    ex_ = _sur(lextrapolation, alt, 284, 40, 1)
    v("★★★★ une rangée TIENT sur les blocs, pas sur le tirage pas à pas qui détruirait l'alternance",
      lambda: ex_["la_longueur_de_bloc"] == 6 and ex_["elle_tient_a_lechelle_de_la_rangee"] is True
      and ex_["la_marche_mediane_pas_a_pas_en_voxels"] > DEMI_PAS_EN_VOXELS, str(ex_))
    v("★★★★ les pas sont CENTRÉS : une dérive constante ne fabrique aucune marche",
      float(les_marches_par_blocs([2.0] * 60, 300, 5, 1, 3).max()) == 0.0)

    # ⭐⭐⭐ LE THETA.
    for th in (0.0, 0.3, -0.4, 0.8):
        r_ = -th / (1.0 + th * th)
        v(f"★★★★ θ = {th} se retrouve depuis son autocorrélation (racine de module inférieur à un)",
          lambda th=th, r_=r_: abs(le_theta_dune_autocorrelation(r_)
                                   - (th if abs(th) < 1 else 1.0 / th)) < 1e-9)
    v("★★★ une autocorrélation hors de portée est écrêtée, jamais imaginaire",
      abs(le_theta_dune_autocorrelation(-0.9)) < 1.0)
    s_ = une_serie_dependante(0.6, 20000, 4)
    v("★★★★ la matière de l'étalon a l'autocorrélation que son θ annonce",
      lambda: abs(lautocorrelation(s_, 1) - (-0.6 / 1.36)) < 0.03)

    # ⚠⚠⚠ L'ETALON DOIT POUVOIR DISTINGUER LES DEUX INSTRUMENTS.
    et = _sur(sur_letalon, 150, 284, 0.6, replicats=8, tirages=40, graine=5, verites=200)
    v("★★★★ sur une matière qui revient sur elle-même, les blocs s'approchent de la vérité plus que "
      "le tirage pas à pas, qui la surestime",
      lambda: et["les_blocs_sapprochent_le_plus"] is True and et["le_rapport_median_pas_a_pas"] > 1.2,
      str(et))
    et0 = _sur(sur_letalon, 150, 284, 0.0, replicats=8, tirages=40, graine=6, verites=200)
    v("★★★★ sans dépendance, les deux instruments rendent à peu près la vérité — le contrôle gratuit",
      lambda: abs(et0["le_rapport_median_par_blocs"] - 1.0) < 0.25
      and abs(et0["le_rapport_median_pas_a_pas"] - 1.0) < 0.25, str(et0))

    # ⭐⭐⭐ LES ISSUES.
    v("★★★★ les trois issues sont distinctes, et quitter sur ce qu'on lit prime",
      len({_ce_qui_reste(a, b) for a in (True, False) for b in (True, False)}) == 3
      and _ce_qui_reste(False, True) == _ce_qui_reste(False, False))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE.
    out = _sur(mesurer, GRAINE, 12, 4, avec_etalon=False)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      lambda: out.get("decidable") and out["le_verdict"]["ce_qui_reste_a_mesurer"],
      str(out.get("raison")))
    v("★★★★ le tronçon retenu est le plus long où le consensus existe",
      lambda: out["le_troncon_retenu"][2] == max(t[2] for t in out["les_troncons_du_consensus"]))
    v("★★★★ le contrôle apparié ne prend que des rangées qui couvrent le tronçon SANS trou",
      lambda: all(x["les_coutures"] == out["le_troncon_retenu"][2]
                  for x in out["les_rangees_seules_sur_le_meme_troncon"].values()))
    v("★★★★ la marche publiée du consensus redonne sa distance au départ",
      lambda: round(max(abs(x) for x in out["les_marches_du_troncon_retenu_en_voxels"]["le_consensus"]), 4)
      == out["la_traversee_du_consensus"]["la_distance_au_depart_en_voxels"])
    v("★★★★ chaque rangée seule est aussi jugée sur son propre plus long tronçon",
      lambda: sorted(out["les_rangees_seules_sur_leur_plus_long_troncon"])
      == [str(r) for r in out["les_rangees"]])

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
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--replicats", type=int, default=60)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graine, a.tirages, a.replicats, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
