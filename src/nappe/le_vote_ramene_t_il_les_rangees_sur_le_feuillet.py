"""Corrigées par un vote de cinq voisines, deux rangées restent-elles sur le même feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA CORRECTION NE SOIT APPLIQUÉE À LA MATIÈRE. Les sondes de
conception n'ont tourné que sur des matières fabriquées.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P65`. `219` établit que les écarts de couture extrêmes
sont portés par une rangée à la fois et qu'un vote de cinq voisines la désigne. C'est la moitié de ce
qui remplace l'humain qui corrige le transfert ; l'autre est de corriger. `211` avait établi que deux
rangées voisines, traversées chacune pour elle-même, s'éloignent d'un demi-feuillet à l'échelle d'une
rangée. La question est de savoir si le vote les garde ensemble.

⭐⭐ AUCUNE LECTURE NEUVE : `219` publie les pas des cinq rangées colonne par colonne, ses colonnes
fortes et la rangée que le vote y désigne.

## ⚠⚠⚠ Le nul que la porte prescrivait partage la décision qu'il juge, et son sort se MESURE

`R4-P65` proposait de juger le vote contre la même correction appliquée aux mêmes colonnes à une
AUTRE rangée. Mais le vote désigne la rangée dont l'anomalie pointe le plus vers son axe — en
pratique la plus déviante —, donc la remplacer par ses voisines retire plus de désaccord à cette
colonne que d'en remplacer une autre, qu'il y ait un saut ou non. ⚠⚠ Cela ne suffit pourtant pas à
dire d'avance qu'il gagnerait sur du bruit pur : la séparation est un MAXIMUM le long de la marche, et
retirer un pas peut la rapprocher ou l'éloigner selon le côté où la marche se trouve. Ce n'est pas
démontrable sans mesure. Il est donc porté comme CONTRÔLE NOMMÉ et son taux est MESURÉ sur des
matières gaussiennes : l'étalon dit s'il est réfuté ou s'il tient, et le verdict ne s'appuie pas sur
lui.

⭐ La question de savoir si le vote désigne la bonne rangée a déjà sa réponse, qui est `219`. Ce qui
reste est une MESURE contre un seuil physique, le demi-feuillet.

## La correction, déclarée

À chaque colonne forte de `219`, le pas de la rangée que le vote désigne est remplacé par la MÉDIANE
des pas des quatre autres à cette colonne. ⚠ La médiane et non la moyenne : si une seconde rangée
s'écarte aussi, la moyenne l'emporterait avec elle. ⚠ Toutes les colonnes fortes sont corrigées, y
compris celles que `219` dit mal portées par une seule rangée : c'est le vote tel qu'il est, pas tel
qu'on le voudrait.

## Ce qui se mesure

Pour chaque paire de rangées VOISINES, sur son plus long tronçon commun contigu :

- la SÉPARATION, `max_k |S_k|`, où `S` est le cumul des désaccords de pas parti de zéro — la quantité
  de `211` : deux rangées partent alignées, et c'est leur distance qui décide si elles finissent sur
  le même feuillet ;
- avant le vote, et après ;
- et la même séparation pour des marches INDÉPENDANTES de mêmes pas — les désaccords corrigés
  rebrassés le long du tronçon — qui disent si rester sous le demi-feuillet est la règle ou la chance.

⭐⭐⭐⭐ ET À L'ÉCHELLE DE LA RANGÉE ENTIÈRE, qui est la question du graal : des marches de la longueur
d'une rangée, tirées dans les désaccords corrigés. Une paire TIENT à cette échelle quand la marche
MÉDIANE reste sous le demi-feuillet. ⚠ La médiane et non un quantile réglé : c'est « une rangée
typique », la seule lecture qui ne choisit rien.

⚠⚠⚠⚠ LA MARCHE DE LA RANGÉE DÉCLARÉE D'ABORD EST REFUSÉE, POUR UNE RAISON STRUCTURELLE — ET L'ORDRE
EST DIT : LE DÉFAUT A ÉTÉ VU SUR LA MESURE AVANT D'ÊTRE DÉMONTRÉ. Tirer avec remise les désaccords du
tronçon garde leur MOYENNE, et une marche de `N` pas tirés ainsi dérive de `N` fois cette moyenne. Or
la moyenne de `n` désaccords n'est connue qu'à `σ/√n` près : la dérive qu'elle fabrique vaut donc
`σ·N/√n`, quand la marche elle-même ne s'étale que de `σ·√N`. Dès que la rangée est plus longue que le
tronçon — c'est toujours le cas ici —, l'erreur sur la moyenne l'emporte sur la marche, et la
référence mesure l'échantillonnage d'une moyenne au lieu du feuillet. ⭐ Cela se démontre sans
regarder la moindre donnée, ce qui rend le remplacement légitime : la statistique refusée est
publiée avec ses valeurs, et elle est remplacée par la marche de pas CENTRÉS — ce que la déclaration
voulait dire, une rangée typique de pas indépendants de même dispersion. ⚠ Ce que le centrage
suppose est écrit à côté : que la moyenne du tronçon ne soit que du hasard. Elle est publiée avec son
erreur, pour que ce ne soit pas une supposition muette.

⚠⚠ LA PRÉDICTION EST DÉFAVORABLE ET ELLE EST DANS LA PORTE : le désaccord des pas ordinaires est, à
lui seul, une marche qui s'éloigne comme la racine du nombre de coutures, et le vote ne touche que
quatorze colonnes.

## Les issues, exclusives

- aucune paire ne tient à l'échelle de la rangée : le vote aux extrêmes ne suffit pas, la marche
  ordinaire sépare les rangées ;
- certaines tiennent et d'autres non : le vote suffit là où le bruit propre est faible ;
- toutes tiennent : le vote garde les rangées sur le même feuillet.

Usage :
    uv run python src/nappe/le_vote_ramene_t_il_les_rangees_sur_le_feuillet.py --verifier
    uv run python src/nappe/le_vote_ramene_t_il_les_rangees_sur_le_feuillet.py \\
        --json docs/mesures/le_vote_ramene_t_il_les_rangees_sur_le_feuillet.json
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

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import (  # noqa: E402
    GARANTIE, LE_COMPTE_DECISIF, les_bruits_propres, les_directions,
    le_seuil_des_colonnes_fortes, une_matiere)
from le_bruit_propre_croit_il_avec_lecartement import le_taux_tient  # noqa: E402
from le_cumul_recale_traverse_t_il_la_rangee import le_cumul  # noqa: E402
from ouvrir_les_quinze import _rng  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_219_A_RENDU = MESURES / "cinq_rangees_designent_elles_la_fautive.json"
GRAINE = 20261101

LA_QUESTION_DECLAREE = ("corrigées par un vote de cinq voisines, deux rangées voisines restent-elles "
                        "sur le même feuillet ?")
LA_MESURE_DECLAREE = ("la séparation de chaque paire voisine après le vote, et celle de sa marche "
                      "médiane à l'échelle d'une rangée, contre le demi-feuillet")


def ce_que_219_a_rendu(chemin: Path = CE_QUE_219_A_RENDU) -> dict:
    """Les pas, les colonnes fortes et les rangées désignées de `219` — relus, jamais recalculés.

    ⚠⚠ LES COLONNES FORTES SONT CELLES QUE `219` A PUBLIÉES : les recalculer ici ferait une seconde
    réponse à « où le vote corrige », libre de diverger de la première.
    """
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    if not d.get("decidable"):
        return {"decidable": False, "raison": "`219` est indécidable"}
    pas_ = d.get("les_pas_par_rangee")
    pc = d.get("par_colonne") or {}
    seuil = (d.get("lepreuve") or {}).get("le_seuil_denergie")
    if not isinstance(pas_, dict) or not pc.get("les_colonnes") or seuil is None:
        return {"decidable": False,
                "raison": "`219` ne publie ni ses pas, ni ses colonnes, ni son seuil"}
    pas = {int(r): {int(c): float(s) for c, s in x.items()} for r, x in pas_.items()}
    fortes = {int(c): int(r) for c, e, r in zip(pc["les_colonnes"], pc["les_energies"],
                                                pc["les_rangees_designees"]) if float(e) > float(seuil)}
    if len(fortes) != int((d.get("lepreuve") or {}).get("combien_de_colonnes_fortes") or -1):
        return {"decidable": False,
                "raison": "les colonnes fortes relues ne sont pas celles que `219` compte"}
    lignes = d.get("les_lignes") or {}
    grilles = {tuple(x.get("grille_de_chunks") or []) for x in lignes.values()}
    if len(grilles) != 1:
        return {"decidable": False, "raison": "les rangées de `219` ne partagent pas une grille"}
    colonnes = int(next(iter(grilles))[1])
    return {"decidable": True, "les_pas_par_rangee": pas, "les_colonnes_fortes": fortes,
            "les_rangees": sorted(pas), "le_seuil_denergie": float(seuil),
            "les_coutures_dune_rangee": colonnes - 1}


def le_vote(pas: dict, fortes: dict) -> tuple[dict, int]:
    """Les pas après le vote : à chaque colonne forte, la rangée désignée prend la médiane des autres."""
    out = {r: dict(x) for r, x in pas.items()}
    faites = 0
    for c, r in sorted(fortes.items()):
        autres = [pas[q][c] for q in pas if q != r and c in pas[q]]
        if r in pas and c in pas[r] and len(autres) == len(pas) - 1:
            out[r][c] = float(np.median(autres))
            faites += 1
    return out, faites


def le_plus_long_troncon(une: dict, autre: dict) -> list[int]:
    """Le plus long tronçon de colonnes CONTIGUËS où les deux rangées ont un pas — le premier à égalité."""
    communes = sorted(set(une) & set(autre))
    if not communes:
        return []
    meilleur, courant = [communes[0]], [communes[0]]
    for c in communes[1:]:
        courant = courant + [c] if c == courant[-1] + 1 else [c]
        if len(courant) > len(meilleur):
            meilleur = courant
    return meilleur


def la_separation(desaccords) -> float:
    """La plus grande distance entre deux rangées parties alignées : `max_k |S_k|`, `S_0 = 0`."""
    return float(np.max(np.abs(le_cumul(desaccords))))


def les_marches_independantes(desaccords, longueur: int, tirages: int, graine: int,
                              remise: bool) -> np.ndarray:
    """Les séparations de marches de pas INDÉPENDANTS tirés dans les désaccords observés.

    ⚠⚠ SANS REMISE, c'est un rebrassage le long du tronçon : mêmes pas, ordre détruit. AVEC REMISE,
    c'est une marche de n'importe quelle longueur, la seule façon de parler d'une rangée entière avec
    un tronçon plus court qu'elle.
    """
    d = np.asarray(desaccords, dtype=float)
    g = _rng(int(graine))
    out = []
    for _ in range(int(tirages)):
        m = g.choice(d, size=int(longueur), replace=True) if remise else g.permutation(d)
        out.append(la_separation(m))
    return np.asarray(out)


def une_paire(pas_avant: dict, pas_apres: dict, a: int, b: int, coutures_rangee: int,
              tirages: int, graine: int, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Une paire voisine : sa séparation avant et après le vote, et ses marches de référence."""
    tr = le_plus_long_troncon(pas_avant[a], pas_avant[b])
    if len(tr) < 10:
        return {"decidable": False, "raison": f"la paire {a}-{b} n'a pas de tronçon commun"}
    avant = [pas_avant[a][c] - pas_avant[b][c] for c in tr]
    apres = [pas_apres[a][c] - pas_apres[b][c] for c in tr]
    corrigees = sum(1 for x, y in zip(avant, apres) if x != y)
    s0, s1 = la_separation(avant), la_separation(apres)
    rebr = les_marches_independantes(apres, len(apres), tirages, graine, remise=False)
    # ⚠⚠⚠ LA MARCHE DECLAREE D'ABORD, REFUSEE ET PUBLIEE : elle garde la moyenne du troncon.
    ref_ = les_marches_independantes(apres, coutures_rangee, tirages, graine + 1, remise=True)
    ref0 = les_marches_independantes(avant, coutures_rangee, tirages, graine + 2, remise=True)
    # ⭐ LA MARCHE RETENUE : les memes desaccords, CENTRES.
    ca, cb = np.asarray(apres) - float(np.mean(apres)), np.asarray(avant) - float(np.mean(avant))
    rang_ = les_marches_independantes(ca, coutures_rangee, tirages, graine + 1, remise=True)
    rang0 = les_marches_independantes(cb, coutures_rangee, tirages, graine + 2, remise=True)
    se = float(np.std(apres)) / np.sqrt(len(apres))
    return {"decidable": True,
            "la_paire": [int(a), int(b)],
            "le_troncon": [int(tr[0]), int(tr[-1]), len(tr)],
            "les_coutures_corrigees_par_le_vote": int(corrigees),
            "la_separation_avant_en_voxels": round(s0, 4),
            "la_separation_apres_en_voxels": round(s1, 4),
            "sous_le_demi_pli_avant": bool(s0 < float(demi)),
            "sous_le_demi_pli_apres": bool(s1 < float(demi)),
            "lecart_type_des_desaccords_avant_en_voxels": round(float(np.std(avant)), 4),
            "lecart_type_des_desaccords_apres_en_voxels": round(float(np.std(apres)), 4),
            "la_moyenne_des_desaccords_apres_en_voxels": round(float(np.mean(apres)), 4),
            "son_erreur_en_voxels": round(se, 4),
            "la_moyenne_en_erreurs": round(float(np.mean(apres)) / se, 4) if se > 0 else None,
            "le_troncon_rebrasse_median_en_voxels": round(float(np.median(rebr)), 4),
            "les_rebrassages_sous_le_demi_pli": int(np.sum(rebr < float(demi))),
            "les_rebrassages_au_moins_aussi_loin": int(np.sum(rebr >= s1)),
            "les_coutures_dune_rangee": int(coutures_rangee),
            "la_rangee_mediane_apres_en_voxels": round(float(np.median(rang_)), 4),
            "la_rangee_mediane_avant_en_voxels": round(float(np.median(rang0)), 4),
            "les_rangees_sous_le_demi_pli_apres": int(np.sum(rang_ < float(demi))),
            "les_rangees_sous_le_demi_pli_avant": int(np.sum(rang0 < float(demi))),
            "tirages": int(tirages),
            "la_marche_refusee": {
                "pourquoi": "elle garde la moyenne du tronçon, dont l'erreur l'emporte sur la marche",
                "la_rangee_mediane_avant_en_voxels": round(float(np.median(ref0)), 4),
                "la_rangee_mediane_apres_en_voxels": round(float(np.median(ref_)), 4),
                "la_derive_quelle_fabrique_apres_en_voxels":
                    round(abs(float(np.mean(apres))) * int(coutures_rangee), 4),
                "lerreur_sur_cette_derive_en_voxels": round(se * int(coutures_rangee), 4),
                "ce_que_la_marche_setale_en_voxels":
                    round(float(np.std(apres)) * np.sqrt(int(coutures_rangee)), 4)},
            "elle_tient_a_lechelle_de_la_rangee": bool(float(np.median(rang_)) < float(demi))}


def le_nul_de_la_porte(pas: dict, fortes: dict, tirages: int, graine: int) -> dict:
    """CONTRÔLE NOMMÉ : le vote contre la même correction appliquée à une AUTRE rangée.

    ⚠⚠⚠ CALCULÉ ET PUBLIÉ, JAMAIS SUIVI. La statistique est la somme des séparations des paires
    voisines sur leurs tronçons ; le vote « gagne » quand aucun des tirages d'une autre rangée ne fait
    aussi bien. Son taux sur de la matière gaussienne est MESURÉ par l'étalon, et c'est lui qui dit
    s'il tient sa garantie.
    """
    rs = sorted(pas)
    corr, faites = le_vote(pas, fortes)

    def _somme(p):
        tot = 0.0
        for a, b in zip(rs, rs[1:]):
            tr = le_plus_long_troncon(pas[a], pas[b])
            if len(tr) >= 2:
                tot += la_separation([p[a][c] - p[b][c] for c in tr])
        return tot

    obs = _somme(corr)
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        autre = {c: int(g.choice([q for q in rs if q != r])) for c, r in fortes.items()}
        nuls.append(_somme(le_vote(pas, autre)[0]))
    au_moins = int(sum(1 for x in nuls if x <= obs))
    return {"decidable": True, "les_colonnes_corrigees": int(faites),
            "la_somme_des_separations_apres_le_vote": round(obs, 4),
            "la_somme_mediane_par_une_autre_rangee": round(float(np.median(nuls)), 4),
            "les_tirages_au_moins_aussi_bons": au_moins, "tirages": int(tirages),
            "le_vote_gagne": bool(au_moins == 0 and faites > 0)}


def les_colonnes_fortes_dune_matiere(p: np.ndarray, rangees) -> dict:
    """Les colonnes fortes et leurs rangées désignées, par les fonctions de `218` — pour l'étalon."""
    bp = les_bruits_propres(p)
    if not bp.get("decidable"):
        return {}
    d = les_directions(p, bp["les_variances"])
    if not d.get("decidable"):
        return {}
    seuil = le_seuil_des_colonnes_fortes(p.shape[0], p.shape[1])
    return {int(c): int(rangees[int(d["les_fautives"][c])])
            for c in range(p.shape[0]) if float(d["les_energies"][c]) > seuil}


def sur_letalon(n: int, ecarts_types, decisif: int = LE_COMPTE_DECISIF,
                tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """L'étalon du nul de la porte : combien de fois « gagne-t-il » sur du bruit gaussien PUR ?

    ⚠⚠⚠ UN NUL QUI GAGNE SUR DU BRUIT NE DIT RIEN DE LA MATIÈRE. S'il dépasse deux fois la garantie
    ici, il est réfuté, et la tranche dit pourquoi au lieu de le suivre.
    """
    sig = [float(x) for x in ecarts_types]
    rs = list(range(len(sig)))
    gagnes, sans = 0, 0
    for i in range(int(decisif)):
        m = une_matiere("gaussienne", n, sig, int(graine) + 13 * i)
        pas = {r: {c: float(m[c, r]) for c in range(n)} for r in rs}
        fortes = les_colonnes_fortes_dune_matiere(m, rs)
        if not fortes:
            sans += 1
            continue
        if le_nul_de_la_porte(pas, fortes, tirages, int(graine) + 13 * i + 1)["le_vote_gagne"]:
            gagnes += 1
    taux = gagnes / float(decisif)
    return {"decidable": True, "les_colonnes_par_matiere": int(n),
            "les_bruits_propres_en_voxels": [round(x, 4) for x in sig],
            "le_compte_decisif": int(decisif), "les_victoires_sur_du_bruit": int(gagnes),
            "les_matieres_sans_colonne_forte": int(sans), "le_taux": round(taux, 4),
            "le_nul_de_la_porte_tient_sa_garantie": le_taux_tient(taux, GARANTIE)}


def _ce_qui_reste(tiennent: int, paires: int) -> str:
    """Les trois issues, et elles sont EXCLUSIVES."""
    if tiennent == 0:
        return ("LE VOTE AUX EXTRÊMES NE SUFFIT PAS : LA MARCHE ORDINAIRE SÉPARE LES RANGÉES À "
                "L'ÉCHELLE D'UNE RANGÉE")
    if tiennent < paires:
        return (f"LE VOTE SUFFIT POUR {tiennent} PAIRE(S) SUR {paires} : LÀ OÙ LE BRUIT PROPRE EST "
                f"FAIBLE")
    return "LE VOTE GARDE LES RANGÉES SUR LE MÊME FEUILLET"


def mesurer(graine: int = GRAINE, decisif: int = LE_COMPTE_DECISIF, tirages: int = PERMUTATIONS,
            chemin: Path = CE_QUE_219_A_RENDU, avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    lu = ce_que_219_a_rendu(chemin)
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    pas, fortes, rs = lu["les_pas_par_rangee"], lu["les_colonnes_fortes"], lu["les_rangees"]
    apres, faites = le_vote(pas, fortes)
    paires = {}
    for i, (a, b) in enumerate(zip(rs, rs[1:])):
        paires[f"{a}-{b}"] = une_paire(pas, apres, a, b, lu["les_coutures_dune_rangee"],
                                       int(decisif), int(graine) + 100 * i)
    porte = le_nul_de_la_porte(pas, fortes, tirages, graine)
    sig = []
    p5 = np.asarray([[pas[r][c] for r in rs] for c in sorted(set.intersection(
        *[set(pas[r]) for r in rs]))], dtype=float)
    bp = les_bruits_propres(p5)
    if bp.get("decidable"):
        sig = [float(np.sqrt(x)) for x in bp["les_variances"]]
    etalon = (sur_letalon(p5.shape[0], sig, decisif, tirages, graine)
              if (avec_etalon and sig) else None)
    ok = [x for x in paires.values() if x.get("decidable")]
    tiennent = sum(1 for x in ok if x["elle_tient_a_lechelle_de_la_rangee"])
    return {"decidable": bool(ok),
            "graine": int(graine), "tirages": int(tirages), "le_compte_decisif": int(decisif),
            "la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE,
            "la_garantie_du_nul": GARANTIE,
            "le_demi_pli_en_voxels": int(DEMI_PAS_EN_VOXELS),
            "les_rangees": rs, "les_coutures_dune_rangee": int(lu["les_coutures_dune_rangee"]),
            "les_colonnes_fortes_de_219": {str(c): int(r) for c, r in sorted(fortes.items())},
            "les_colonnes_corrigees": int(faites),
            "les_paires_voisines": paires,
            "le_nul_de_la_porte": porte,
            "letalon": etalon,
            "le_verdict": {
                "combien_de_paires": len(ok),
                "combien_tiennent_a_lechelle_de_la_rangee": int(tiennent),
                "combien_sous_le_demi_pli_avant_sur_le_troncon":
                    sum(1 for x in ok if x["sous_le_demi_pli_avant"]),
                "combien_sous_le_demi_pli_apres_sur_le_troncon":
                    sum(1 for x in ok if x["sous_le_demi_pli_apres"]),
                "le_nul_de_la_porte_est_refute":
                    (not etalon["le_nul_de_la_porte_tient_sa_garantie"]) if etalon else None,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(int(tiennent), len(ok))}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"\n{len(r['les_colonnes_fortes_de_219'])} colonnes fortes, {r['les_colonnes_corrigees']} "
          f"corrigées · demi-pli {r['le_demi_pli_en_voxels']} vx · une rangée = "
          f"{r['les_coutures_dune_rangee']} coutures")
    for nom, x in r["les_paires_voisines"].items():
        if not x.get("decidable"):
            print(f"  {nom} · {x.get('raison')}")
            continue
        print(f"  {nom} · tronçon {x['le_troncon']} · {x['les_coutures_corrigees_par_le_vote']} "
              f"corrigées · séparation {x['la_separation_avant_en_voxels']} → "
              f"{x['la_separation_apres_en_voxels']} · rebrassé médian "
              f"{x['le_troncon_rebrasse_median_en_voxels']} ({x['les_rebrassages_sous_le_demi_pli']}/"
              f"{x['tirages']} sous le demi-pli) · rangée médiane {x['la_rangee_mediane_avant_en_voxels']}"
              f" → {x['la_rangee_mediane_apres_en_voxels']} ({x['les_rangees_sous_le_demi_pli_apres']}"
              f"/{x['tirages']} sous) · tient {x['elle_tient_a_lechelle_de_la_rangee']}")
    p = r["le_nul_de_la_porte"]
    print(f"\nNUL DE LA PORTE · {p['la_somme_des_separations_apres_le_vote']} contre "
          f"{p['la_somme_mediane_par_une_autre_rangee']} · {p['les_tirages_au_moins_aussi_bons']}/"
          f"{p['tirages']} · le vote gagne {p['le_vote_gagne']}")
    t = r.get("letalon")
    if t:
        print(f"  sur du bruit pur, il gagne {t['les_victoires_sur_du_bruit']}/{t['le_compte_decisif']}"
              f" = {t['le_taux']} · tient sa garantie {t['le_nul_de_la_porte_tient_sa_garantie']}")
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

    lu = _sur(ce_que_219_a_rendu)
    v("★★★★ les colonnes fortes relues sont exactement celles que `219` compte",
      lambda: lu.get("decidable") and len(lu["les_colonnes_fortes"]) == json.loads(
          CE_QUE_219_A_RENDU.read_text())["lepreuve"]["combien_de_colonnes_fortes"],
      str(lu.get("raison")))
    v("★★★★ la longueur d'une rangée est DÉRIVÉE de la grille publiée, jamais tapée",
      lambda: lu["les_coutures_dune_rangee"] == json.loads(CE_QUE_219_A_RENDU.read_text())
      ["les_lignes"]["198"]["grille_de_chunks"][1] - 1)
    v("★★★ un `219` absent est refusé", not ce_que_219_a_rendu(Path("/nen/existe.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_220.json"
    try:
        d_ = json.loads(CE_QUE_219_A_RENDU.read_text())
        d_["lepreuve"]["combien_de_colonnes_fortes"] += 1
        tmp.write_text(json.dumps(d_))
        v("★★★★ des colonnes fortes qui ne sont pas celles que `219` compte sont REFUSÉES",
          lambda: "fortes" in (ce_que_219_a_rendu(tmp).get("raison") or ""))
    finally:
        if tmp.exists():
            tmp.unlink()

    # ⭐⭐⭐ LE VOTE.
    pas_x = {1: {0: 0.0, 1: 0.0}, 2: {0: 1.0, 1: 0.0}, 3: {0: 2.0, 1: 0.0}, 4: {0: 3.0, 1: 0.0},
             5: {0: 40.0, 1: 0.0}}
    corr, n_ = le_vote(pas_x, {0: 5})
    v("★★★★ le vote remplace la rangée désignée par la MÉDIANE des quatre autres, et rien d'autre",
      corr[5][0] == 1.5 and n_ == 1 and all(corr[r] == pas_x[r] for r in (1, 2, 3, 4))
      and pas_x[5][0] == 40.0)
    v("★★★★ la médiane résiste à une seconde rangée déviante, là où la moyenne la suivrait",
      lambda: le_vote({1: {0: 0.0}, 2: {0: 0.0}, 3: {0: 0.0}, 4: {0: 30.0}, 5: {0: 40.0}},
                      {0: 5})[0][5][0] == 0.0)
    v("★★★ une colonne où une rangée manque n'est pas corrigée",
      le_vote({1: {0: 0.0}, 2: {}, 3: {0: 0.0}}, {0: 1})[1] == 0)

    # ⭐⭐⭐ LE TRONCON ET LA SEPARATION.
    v("★★★★ le plus long tronçon est contigu, et le premier à égalité",
      le_plus_long_troncon({c: 0 for c in [1, 2, 3, 7, 8, 9, 10]}, {c: 0 for c in range(20)})
      == [7, 8, 9, 10]
      and le_plus_long_troncon({c: 0 for c in [1, 2, 5, 6]}, {c: 0 for c in range(9)}) == [1, 2])
    v("★★★★ la séparation est la plus grande distance au DÉPART, pas l'étendue",
      la_separation([5.0, -10.0, 2.0]) == 5.0 and la_separation([-3.0, -4.0, 10.0]) == 7.0)
    v("★★★ deux rangées identiques ne se séparent jamais", la_separation([0.0] * 50) == 0.0)
    m_ = les_marches_independantes([1.0, -1.0] * 20, 40, 5, 3, remise=False)
    v("★★★★ un rebrassage garde les mêmes pas : une marche de pas ±1 ne dépasse jamais sa longueur",
      len(m_) == 5 and float(m_.max()) <= 40.0 and float(m_.min()) >= 1.0)
    v("★★★★ avec remise, la marche a la longueur demandée — celle d'une rangée, pas du tronçon",
      lambda: float(les_marches_independantes([1.0] * 10, 300, 3, 4, remise=True).max()) == 300.0)

    # ⭐⭐⭐⭐ UNE PAIRE, SUR UNE MATIERE CONSTRUITE.
    g = _rng(21)
    base = {r: {c: float(x) for c, x in enumerate(g.normal(0.0, 1.0, 120))} for r in (1, 2)}
    avec_saut = {r: dict(x) for r, x in base.items()}
    avec_saut[1][60] += 60.0
    rep = une_paire(avec_saut, base, 1, 2, 284, 40, 5)
    v("★★★★ un saut retiré par le vote fait tomber la séparation sous le demi-pli",
      rep.get("decidable") and rep["la_separation_avant_en_voxels"] > DEMI_PAS_EN_VOXELS
      and rep["sous_le_demi_pli_apres"] is True and rep["les_coutures_corrigees_par_le_vote"] == 1,
      str(rep))
    grosse = {r: {c: float(x) for c, x in enumerate(g.normal(0.0, 6.0, 120))} for r in (1, 2)}
    rg = une_paire(grosse, grosse, 1, 2, 284, 40, 6)
    v("★★★★ un bruit propre fort ne tient pas à l'échelle de la rangée, même sans aucun saut",
      rg.get("decidable") and rg["elle_tient_a_lechelle_de_la_rangee"] is False
      and rg["les_coutures_corrigees_par_le_vote"] == 0, str(rg))
    faible = {r: {c: float(x) for c, x in enumerate(g.normal(0.0, 0.3, 120))} for r in (1, 2)}
    rf = une_paire(faible, faible, 1, 2, 284, 40, 7)
    v("★★★★ un bruit propre faible tient à l'échelle de la rangée — la mesure peut dire oui",
      rf.get("decidable") and rf["elle_tient_a_lechelle_de_la_rangee"] is True, str(rf))
    v("★★★★ la rangée se juge APRÈS le vote : le saut retiré ne revient pas dans ses marches",
      lambda: rep["la_rangee_mediane_apres_en_voxels"] < rep["la_rangee_mediane_avant_en_voxels"])
    d_apres = np.asarray([base[1][c] - base[2][c] for c in range(120)])
    v("★★★★ et sa marche est tirée dans les désaccords APRÈS le vote, centrés — pas dans ceux d'avant",
      lambda: rep["la_rangee_mediane_apres_en_voxels"] == round(float(np.median(
          les_marches_independantes(d_apres - float(np.mean(d_apres)), 284, 40, 6, remise=True))), 4))
    # ⚠⚠⚠ LE REFUS SE DEMONTRE SUR UNE MATIERE SANS AUCUNE DERIVE : des pas de moyenne vraie nulle,
    # dont la moyenne echantillonnale n'est que du hasard. La marche refusee la transforme en derive.
    derive = {1: {c: float(x) for c, x in enumerate(g.normal(0.0, 2.0, 60))}, 2: {c: 0.0 for c in range(60)}}
    rd = une_paire(derive, derive, 1, 2, 2000, 60, 12)
    v("★★★★ sur des pas sans dérive vraie, la marche REFUSÉE dérive de N fois une moyenne de hasard, "
      "et la marche retenue ne dérive pas",
      lambda: rd["la_marche_refusee"]["la_rangee_mediane_apres_en_voxels"]
      > 1.5 * rd["la_rangee_mediane_apres_en_voxels"]
      and abs(rd["la_marche_refusee"]["la_derive_quelle_fabrique_apres_en_voxels"]
              - abs(rd["la_moyenne_des_desaccords_apres_en_voxels"]) * 2000) < 1.0, str(rd))
    v("★★★★ la moyenne du tronçon est publiée avec son erreur, pour que le centrage ne soit pas muet",
      lambda: rep["son_erreur_en_voxels"] > 0 and rep["la_moyenne_en_erreurs"] is not None)
    # ⚠⚠ UN BRUIT INTERMEDIAIRE, OU LA MEDIANE ET LE MEILLEUR TIRAGE NE DISENT PAS LA MEME CHOSE :
    # sans lui, une regle « tient si UNE marche tient » passerait toutes les sondes.
    moyen = {r: {c: float(x) for c, x in enumerate(g.normal(0.0, 1.7, 120))} for r in (1, 2)}
    rm_ = une_paire(moyen, moyen, 1, 2, 284, 60, 8)
    v("★★★★ une paire tient quand sa marche MÉDIANE tient, pas quand une marche chanceuse tient",
      lambda: 0 < rm_["les_rangees_sous_le_demi_pli_apres"] < rm_["tirages"]
      and rm_["elle_tient_a_lechelle_de_la_rangee"]
      == (rm_["la_rangee_mediane_apres_en_voxels"] < DEMI_PAS_EN_VOXELS), str(rm_))
    m5 = une_matiere("saut", 150, [2.0, 2.1, 1.9, 2.5, 2.3], 31, amplitude=60.0, combien=8)
    pas5 = {r: {c: float(m5[c, r]) for c in range(150)} for r in range(5)}
    np5 = _sur(le_nul_de_la_porte, pas5, les_colonnes_fortes_dune_matiere(m5, list(range(5))),
               PERMUTATIONS, 9)
    v("★★★★ sur de vrais sauts, le vote bat la correction d'une autre rangée — le nul de la porte "
      "corrige bien une AUTRE rangée",
      lambda: np5["le_vote_gagne"] is True
      and np5["la_somme_mediane_par_une_autre_rangee"] > np5["la_somme_des_separations_apres_le_vote"],
      str(np5))
    v("★★★ une paire sans tronçon est refusée",
      not une_paire({1: {0: 1.0}, 2: {5: 1.0}}, {1: {0: 1.0}, 2: {5: 1.0}}, 1, 2, 284, 5, 1)
      .get("decidable"))

    # ⚠⚠⚠ LE NUL DE LA PORTE.
    et = _sur(sur_letalon, 120, [2.0, 2.1, 1.9, 2.5, 2.3], decisif=12, tirages=PERMUTATIONS, graine=3)
    v("★★★★ l'étalon du nul de la porte rend un taux et dit s'il tient sa garantie",
      lambda: et.get("decidable") and isinstance(et["le_nul_de_la_porte_tient_sa_garantie"], bool)
      and 0.0 <= et["le_taux"] <= 1.0, str(et.get("raison")))
    v("★★★★ son taux compte les matières sans colonne forte comme des défaites, pas comme absentes",
      lambda: et["le_taux"] == round(et["les_victoires_sur_du_bruit"] / float(et["le_compte_decisif"]),
                                     4))
    v("★★★ un étalon sans colonne forte le compte à part",
      lambda: "les_matieres_sans_colonne_forte" in et)

    # ⭐⭐⭐ LES ISSUES.
    v("★★★★ les trois issues sont distinctes et dépendent du compte des paires qui tiennent",
      "NE SUFFIT PAS" in _ce_qui_reste(0, 4) and "GARDE" in _ce_qui_reste(4, 4)
      and all(_ce_qui_reste(k, 4).startswith("LE VOTE SUFFIT POUR") for k in (1, 2, 3))
      and _ce_qui_reste(1, 4) != _ce_qui_reste(3, 4))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE.
    out = _sur(mesurer, GRAINE, 12, PERMUTATIONS, avec_etalon=False)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      lambda: out.get("decidable") and out["le_verdict"]["ce_qui_reste_a_mesurer"],
      str(out.get("raison")))
    v("★★★★ elle mesure les quatre paires VOISINES, et seulement elles",
      lambda: sorted(out["les_paires_voisines"]) == ["196-197", "197-198", "198-199", "199-200"])
    v("★★★★ elle corrige exactement les colonnes fortes de `219`",
      lambda: out["les_colonnes_corrigees"] == len(out["les_colonnes_fortes_de_219"]))
    v("★★★★ elle publie le nul de la porte à côté, jamais à la place",
      lambda: out["le_nul_de_la_porte"].get("decidable"))

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
    p.add_argument("--decisif", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--tirages", type=int, default=PERMUTATIONS)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graine, a.decisif, a.tirages, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
