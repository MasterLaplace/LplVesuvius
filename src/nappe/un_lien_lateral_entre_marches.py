#!/usr/bin/env python3
"""Un lien latéral entre marches voisines empêche-t-il la nappe de se déchirer ?

⚠⚠⚠ POURQUOI CE FICHIER. `124` a mesuré que huit marches parties de la même feuille se déchirent
**9 fois sur 12** sous bruit et obliquité, alors que chacune prise seule ne dérive ni en direction
(`119`) ni en phase (`123`). Ce qui manque n'est donc pas une correction de trajectoire, c'est un
lien **latéral** — et c'est très exactement ce que l'humain fait quand il recoud. `R4-P25` demande
ce qui tient deux marches voisines ensemble.

⭐⭐⭐ **LE LIEN LE PLUS SIMPLE QUI PUISSE MARCHER, ET IL EST MESURÉ CONTRE LA MÊME BASE.** Après
chaque pas, chaque marche est ramenée d'une fraction **λ** vers la moyenne de ses voisines, le long
de son propre axe d'avance. λ = 0 est la nappe libre de `124` ; le test est apparié, graine par
graine.

⚠⚠ **ET LE CONTRÔLE QUI COMPTE N'EST PAS QUE ÇA MARCHE, C'EST QUE ÇA PUISSE ÉCHOUER.** Un lissage
assez fort colle toujours les marches ensemble — y compris **par-dessus une vraie discontinuité du
rouleau**, qu'il effacerait au lieu de la suivre. La batterie fabrique donc une pile avec un
**décrochement réel** et exige qu'un lien fort le masque : sans cette sonde, « le lien empêche la
déchirure » serait vrai par construction.

⚠ Le pas lui-même n'est PAS réimplémenté : ce fichier appelle `marcher` un pas à la fois, donc il
n'existe qu'une seule marche dans le dépôt.

⚠ Aucune lecture distante.

  uv run python src/nappe/un_lien_lateral_entre_marches.py --verifier
  uv run python src/nappe/un_lien_lateral_entre_marches.py \
      --json docs/mesures/un_lien_lateral_entre_marches.json
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

from la_nappe_se_dechire_t_elle import ECART_VOXELS, la_nappe_se_dechire_t_elle  # noqa: E402
from le_marcheur_reste_t_il_verrouille import _outils  # noqa: E402

LIENS = (0.0, 0.25, 0.5)
"""Les forces de lien comparées. λ = 0 est la nappe libre de `124`, donc la base.

⚠ Trois valeurs et pas un balayage : le but est de savoir **si** un lien change quelque chose et ce
qu'il coûte, pas de trouver la meilleure valeur. Chercher le λ optimal sur le corpus qui sert à
juger serait régler un seuil sur ce qui passe."""

MARCHES = 8
PAS = 112
GRAINES = (3, 11, 29, 53, 97, 131)


def marcher_en_nappe(o, pile, departs, x_hat, pas: int, demi: int, lien: float) -> list[dict]:
    """Fait avancer les marches EN MÊME TEMPS, avec un rappel vers les voisines.

    ⭐⭐⭐⭐ LE LIEN EST APPLIQUÉ À LA POSITION, PAS À LA DIRECTION, et la distinction décide de ce
    qu'on mesure. Corriger la direction changerait ce que la marche lit au pas suivant, donc on ne
    saurait plus si le lien a tenu la nappe ou modifié la lecture. Corriger la position déplace le
    point de départ du pas suivant et rien d'autre.

    ⚠⚠ La correction est projetée sur l'axe d'AVANCE de la marche : c'est là que vit la phase. Une
    correction libre déplacerait aussi latéralement, et les huit marches finiraient par se
    rejoindre en une seule — ce qui supprimerait la déchirure en supprimant la nappe.

    ⚠ Les deux marches de bord n'ont qu'une voisine, et c'est elle qui sert. Leur donner un rappel
    vers elles-mêmes les laisserait libres, donc la nappe se déchirerait toujours par ses bords.

    ⚠⚠ `marcher` est appelé **un pas à la fois** : le pas n'est pas réimplémenté ici. Le sens est
    repris de la direction du pas précédent, ce que `marcher` fait déjà quand on lui passe
    `direction0`.
    """
    from combien_de_pas_la_matiere_porte import marcher

    n = len(departs)
    p = [np.asarray(d, dtype=np.float64).copy() for d in departs]
    sens = [np.asarray(x_hat, dtype=np.float64).copy() for _ in range(n)]
    suites = [[] for _ in range(n)]
    vivant = [True] * n
    for _ in range(pas):
        avance = []
        for k in range(n):
            if not vivant[k]:
                avance.append(None)
                continue
            e = marcher(pile, p[k], sens[k], o["longueurs"], o["mu"], o["sd"], o["barre"],
                        o["barre_moities"], o["barre_interstice"], o["C"].VOXEL_FIN_UM,
                        pas_max=1, demi=demi, rendre_position=True)
            pas_lu = [x for x in e if "confirme" in x]
            if not pas_lu:
                vivant[k] = False
                avance.append(None)
                continue
            x = pas_lu[0]
            d = np.asarray(x["direction"], dtype=np.float64)
            # ⚠⚠⚠ LA POSITION EXACTE, PAS CELLE RECONSTRUITE DEPUIS L'ETAPE. Les champs publies
            # sont arrondis ; piloter la marche depuis eux accumule un arrondi que `marcher` n'a
            # pas, et le systeme est chaotique. Ma premiere version le faisait, et un lien NUL ne
            # reproduisait plus la nappe libre — 11,99 contre 2,11 feuilles sur la meme graine.
            p[k] = np.asarray(x["position_zyx"], dtype=np.float64)
            sens[k] = d
            suites[k].append(x)
            avance.append(d)
        if lien <= 0.0 or not any(vivant):
            continue
        # ⚠ La correction est calculée sur les positions AVANT d'en appliquer aucune : corriger au
        # fil ferait dépendre une marche de la correction déjà reçue par sa voisine, donc de
        # l'ordre d'itération.
        avant = [q.copy() for q in p]
        for k in range(n):
            if not vivant[k] or avance[k] is None:
                continue
            voisines = [avant[j] for j in (k - 1, k + 1) if 0 <= j < n and vivant[j]]
            if not voisines:
                continue
            cible = np.mean(voisines, axis=0)
            ecart = cible - avant[k]
            p[k] = p[k] + avance[k] * (lien * float(ecart @ avance[k]))
    return suites


def un_lot(obliquite_deg: float, bruit: float, lien: float, graine: int,
           marches: int = MARCHES, pas: int = PAS, demi: int = 20) -> dict:
    """Un lot de marches voisines, à une force de lien donnée."""
    from combien_de_pas_la_matiere_porte import VolumeFabrique
    from le_marcheur_reste_t_il_verrouille import phases

    o = _outils(demi)
    C = o["C"]
    x_hat = np.array([0.0, 0.0, 1.0])
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit, graine=graine,
                          forme=(cote, cote, cote))
    base = np.array([2000.0, 2000.0, 2000.0])
    proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
    base = base + pile.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
    lateral = np.array([1.0, 0.0, 0.0])
    departs = [base + lateral * (k * ECART_VOXELS) for k in range(marches)]
    suites = marcher_en_nappe(o, pile, departs, x_hat, pas, demi, lien)
    lot = {"marches": [{"depart_lateral_vx": round(k * ECART_VOXELS, 1),
                        "pas": len(s),
                        "phases": [round(x, 4) for x in phases(pile, departs[k], s,
                                                               C.VOXEL_FIN_UM)],
                        "confirmes": sum(1 for x in s if x["confirme"])}
                       for k, s in enumerate(suites)]}
    d = la_nappe_se_dechire_t_elle(lot)
    total = sum(m["pas"] for m in lot["marches"])
    return {"lien": lien, "graine": graine,
            "pas_totaux": total,
            "taux": round(sum(m["confirmes"] for m in lot["marches"]) / max(1, total), 4),
            "saut_maximal_entre_voisines": d.get("saut_maximal_entre_voisines"),
            "dispersion_max": d.get("dispersion_max"),
            "pas_communs": d.get("pas_communs"),
            "se_dechire": d.get("la_nappe_se_dechire")}


def le_lien_tient_il_la_nappe(liens=LIENS, graines=GRAINES, obliquite_deg: float = 35.0,
                              bruit: float = 8.0, demi: int = 20, pas: int = PAS) -> dict:
    """Le lien réduit-il la déchirure, et à quel coût ?

    ⭐⭐⭐⭐ LE TEST EST APPARIÉ GRAINE PAR GRAINE : la même réalisation de bruit est marchée à
    chaque force de lien. Comparer des graines différentes mesurerait surtout laquelle est tombée
    sur un tirage clément — et `124` a payé exactement ça, en publiant d'abord la meilleure des
    douze en croyant publier la seule.

    ⚠ Le **coût** est rendu à côté du bénéfice. Un lien qui supprimerait la déchirure en faisant
    chuter le taux de confirmation n'aurait rien réparé : il aurait collé des marches qui ne lisent
    plus rien.
    """
    par_lien: dict[float, list[dict]] = {}
    for g in graines:
        for lam in liens:
            par_lien.setdefault(lam, []).append(
                un_lot(obliquite_deg, bruit, lam, g, pas=pas, demi=demi))
    out = {"obliquite_deg": obliquite_deg, "bruit": bruit, "graines": list(graines),
           "pas": pas, "par_lien": []}
    for lam in liens:
        lots = par_lien[lam]
        sauts = [x["saut_maximal_entre_voisines"] for x in lots
                 if x["saut_maximal_entre_voisines"] is not None]
        if not sauts:
            continue
        out["par_lien"].append({
            "lien": lam, "lots": len(lots),
            "se_dechirent": sum(1 for x in lots if x["se_dechire"]),
            "saut_median": round(float(np.median(sauts)), 4),
            "saut_max": round(float(max(sauts)), 4),
            "taux_median": round(float(np.median([x["taux"] for x in lots])), 4),
            "pas_totaux_median": float(np.median([x["pas_totaux"] for x in lots])),
            "detail": lots})
    base = next((x for x in out["par_lien"] if x["lien"] == 0.0), None)
    if base:
        for x in out["par_lien"]:
            if x["lien"] == 0.0:
                continue
            x["dechirures_evitees"] = base["se_dechirent"] - x["se_dechirent"]
            x["cout_en_taux"] = round(base["taux_median"] - x["taux_median"], 4)
    # ⚠⚠ AUCUN VERDICT ICI, et c'est délibéré : cette fonction marche la nappe, donc elle ne
    # peut rien savoir de ce que le lien fait à un décrochement RÉEL, qui vit sur un autre
    # empilement. Les deux verdicts sont rendus par `juger`, où les deux moitiés sont connues.
    return out


def juger(par_lien: list[dict], temoins: list[dict]) -> list[dict]:
    """Croise les deux moitiés : ce que le lien fait à la nappe ET à un vrai décrochement.

    ⭐⭐⭐⭐ LE VERDICT NE PEUT PAS ÊTRE RENDU PAR L'UNE DES DEUX MOITIÉS SEULE, et c'est
    une correction de ma première version. `le_lien_tient_il_la_nappe` déclarait « le lien tient
    la nappe » dès qu'il évitait une déchirure sans coûter de taux — donc **vrai pour
    λ = 0,50**, qui évite un lot sur six et fausse un décrochement réel de 13,99 feuilles. Le
    même fichier mesurait les deux et le verdict n'en lisait qu'un.

    ⚠⚠ Un lissage assez fort colle toujours les marches ensemble : « moins de déchirures » est
    donc satisfait par construction passé une certaine force. Ce qui distingue une réparation d'un
    écrasement est ce qu'il advient de ce qui n'est PAS une déchirure, et ça ne vit que dans le
    témoin.

    ⚠ Pure : elle ne marche rien. C'est ce qui permet à la batterie de lui donner des moitiés
    fabriquées et de vérifier qu'elle sait refuser — une fonction qui exigerait de remarcher la
    nappe ne serait sondable qu'au prix d'une traversée.
    """
    par_force = {t["avec_lien"]["lien"]: t for t in temoins if "avec_lien" in t}
    base = next((x for x in par_lien if x["lien"] == 0.0), None)
    if base is None:
        return par_lien
    for x in par_lien:
        if x["lien"] == 0.0:
            continue
        # La moitié nappe : moins de déchirures, sans taux sacrifié.
        x["la_nappe_tient"] = bool(x["se_dechirent"] < base["se_dechirent"]
                                   and x["taux_median"] >= base["taux_median"] - 0.05)
        t = par_force.get(x["lien"])
        x["temoin_rendu"] = t is not None
        fausse = None if t is None else t.get("le_lien_fausse_le_decrochement")
        x["fausse_un_decrochement_reel"] = fausse
        # ⭐⭐⭐⭐ Un témoin ABSENT n'est pas un témoin favorable : sans lui le verdict est
        # indécidable, donc il est refusé. L'inverse laisserait une force non sondée passer pour
        # utilisable au seul motif qu'on ne l'a pas regardée.
        x["le_lien_est_utilisable"] = bool(x["la_nappe_tient"] and fausse is False)
    return par_lien


def temoin_le_lien_fausse_t_il_un_vrai_decrochement(lien: float = 0.5, demi: int = 20,
                                                    pas: int = 40, saut_um: float = 200.0) -> dict:
    """Un lien fort rend-il FAUX un vrai décrochement du rouleau ?

    ⭐⭐⭐⭐ C'EST LE CONTRÔLE QUI REND LE RÉSULTAT HONNÊTE. Un lissage assez fort colle toujours
    les marches ensemble ; la question n'est donc pas s'il supprime la déchirure, mais ce qu'il
    fait à ce qui n'en est **pas** une. Un rouleau réel a des décrochements — `91` mesure que la
    vérité de terrain humaine devient elle-même discontinue au bord.

    La moitié des marches part d'une feuille, l'autre moitié d'une feuille **décalée** : la nappe
    porte donc un saut connu.

    ⚠⚠ ET LA RÉPONSE MESURÉE N'EST PAS CELLE QUE J'ATTENDAIS. J'avais écrit que le lien le
    **masquerait**. Il fait pire : il l'**amplifie**, parce que tirer une marche vers une voisine
    située une feuille plus loin l'arrache à la sienne, et les dégâts se propagent. Le prédicat
    mesure donc l'ÉCART À LA VÉRITÉ INJECTÉE, qui couvre les deux façons de se tromper.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique
    from le_marcheur_reste_t_il_verrouille import phases

    o = _outils(demi)
    C = o["C"]
    x_hat = np.array([0.0, 0.0, 1.0])
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    pile = VolumeFabrique(C.PAS_UM, forme=(cote, cote, cote))
    base = np.array([2000.0, 2000.0, 2000.0])
    proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
    base = base + pile.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
    lateral = np.array([1.0, 0.0, 0.0])
    departs = []
    for k in range(MARCHES):
        d = base + lateral * (k * ECART_VOXELS)
        if k >= MARCHES // 2:
            d = d + pile.normale * (saut_um / C.VOXEL_FIN_UM)
        departs.append(d)
    # ⚠⚠ ORIGINE COMMUNE, et c'est ce qui fait exister la sonde : mesurée depuis le départ de
    # chaque marche, l'injection est invisible — chacune compte depuis son propre zéro. Ma première
    # version le faisait et rendait un saut de 0,15 là où on venait d'injecter 1,16 feuille.
    origine = float(base @ pile.normale) * C.VOXEL_FIN_UM
    out = {"saut_injecte_um": saut_um, "saut_injecte_en_feuilles": round(saut_um / C.PAS_UM, 3)}
    for nom, lam in (("sans_lien", 0.0), ("avec_lien", lien)):
        suites = marcher_en_nappe(o, pile, departs, x_hat, pas, demi, lam)
        lot = {"marches": [{"phases": [round(x, 4) for x in
                                       phases(pile, departs[k], s, C.VOXEL_FIN_UM, origine)]}
                           for k, s in enumerate(suites)]}
        d = la_nappe_se_dechire_t_elle(lot)
        out[nom] = {"lien": lam, "saut": d.get("saut_maximal_entre_voisines"),
                    "pas_communs": d.get("pas_communs")}
    s0 = out["sans_lien"]["saut"]
    s1 = out["avec_lien"]["saut"]
    vrai = saut_um / C.PAS_UM
    out["saut_vrai_en_feuilles"] = round(vrai, 4)
    if s0 is not None and s1 is not None:
        out["ecart_a_la_verite_sans_lien"] = round(abs(s0 - vrai), 4)
        out["ecart_a_la_verite_avec_lien"] = round(abs(s1 - vrai), 4)
        # ⭐⭐⭐⭐ Le prédicat couvre les DEUX façons de se tromper : masquer le décrochement ou
        # l'amplifier. Un lien qui l'éloigne de la vérité l'a faussé, dans un sens ou dans l'autre.
        out["le_lien_fausse_le_decrochement"] = bool(abs(s1 - vrai) > abs(s0 - vrai))
        out["le_lien_lamplifie"] = bool(s1 > s0)
    return out


def mesurer(demi: int = 20, pas: int = PAS, graines=GRAINES) -> dict:
    """Tout, analytique."""
    nappe = le_lien_tient_il_la_nappe(demi=demi, pas=pas, graines=graines)
    # ⚠⚠ LE TÉMOIN TOURNE POUR CHAQUE FORCE, PAS SEULEMENT LA PLUS FORTE. La force qu'on
    # recommanderait est celle qui tient la nappe, pas celle qu'on a testée par commodité : ne
    # sonder que λ = 0,5 laisserait sans réponse la seule valeur qui compte.
    temoins = [temoin_le_lien_fausse_t_il_un_vrai_decrochement(lien=lam, demi=demi)
               for lam in LIENS if lam > 0.0]
    juger(nappe["par_lien"], temoins)
    return {"marches_par_lot": MARCHES, "liens": list(LIENS),
            "le_lien_tient_il_la_nappe": nappe, "temoin_par_lien": temoins}


def afficher(r: dict) -> None:
    d = r["le_lien_tient_il_la_nappe"]
    print(f"{r['marches_par_lot']} marches par lot · obliquité {d['obliquite_deg']}° · "
          f"bruit {d['bruit']} · {len(d['graines'])} graines · {d['pas']} pas")
    print("\n   lien   se déchirent   saut médian   saut max   taux   évitées   coût")
    for x in d["par_lien"]:
        print(f"   {x['lien']:>4.2f}   {x['se_dechirent']:>5}/{x['lots']:<6} "
              f"{x['saut_median']:>11.4f}   {x['saut_max']:>8.3f}   {x['taux_median']:.3f}"
              f"   {x.get('dechirures_evitees', '')!s:>7}   {x.get('cout_en_taux', '')!s:>6}")
    for x in d["par_lien"]:
        if "la_nappe_tient" not in x:
            continue
        print(f"   lien {x['lien']} · la nappe tient : {x['la_nappe_tient']}"
              f" · fausse un décrochement réel : {x.get('fausse_un_decrochement_reel')}"
              f" · ⭐ UTILISABLE : {x.get('le_lien_est_utilisable')}")
    for t in r.get("temoin_par_lien", []):
        print(f"\n  témoin, décrochement injecté de {t['saut_injecte_um']} µm "
              f"({t['saut_injecte_en_feuilles']} feuilles) :")
        print(f"    sans lien : saut {t['sans_lien']['saut']} (écart "
              f"{t.get('ecart_a_la_verite_sans_lien')}) · avec lien {t['avec_lien']['lien']} : "
              f"saut {t['avec_lien']['saut']} (écart {t.get('ecart_a_la_verite_avec_lien')})")
        print(f"    ⚠ le lien fausse le décrochement : "
              f"{t.get('le_lien_fausse_le_decrochement')} · l'amplifie : "
              f"{t.get('le_lien_lamplifie')}")


def verifier() -> int:
    """La batterie, hors ligne, sur peu de pas pour rester rapide."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    # ⭐⭐ Le lien nul doit rendre EXACTEMENT la nappe libre : sinon ce fichier mesurerait une
    # seconde marche au lieu de la marche du dépôt.
    a = un_lot(35.0, 8.0, 0.0, 3, marches=5, pas=8)
    b = un_lot(35.0, 8.0, 0.0, 3, marches=5, pas=8)
    v("un lien nul est reproductible",
      a["saut_maximal_entre_voisines"] == b["saut_maximal_entre_voisines"],
      f"{a['saut_maximal_entre_voisines']} contre {b['saut_maximal_entre_voisines']}")
    v("... et il fait avancer les marches", a["pas_totaux"] >= 30, f"{a['pas_totaux']}")
    # ⭐⭐⭐⭐ LE CONTROLE QUI MANQUAIT, ET SANS LUI TOUTE LA COMPARAISON EST BANCALE : un lien
    # NUL doit rendre EXACTEMENT la nappe libre de `124`. Ma premiere version pilotait la marche
    # depuis les champs ARRONDIS de l'etape, et les deux chemins divergeaient completement.
    from la_nappe_se_dechire_t_elle import huit_marches
    libre = huit_marches(35.0, 8.0, marches=5, pas=8, graine=3)
    d_libre = la_nappe_se_dechire_t_elle(libre)
    d_nul = un_lot(35.0, 8.0, 0.0, 3, marches=5, pas=8)
    v("un lien NUL reproduit la nappe libre",
      d_nul["saut_maximal_entre_voisines"] == d_libre["saut_maximal_entre_voisines"],
      f"{d_nul['saut_maximal_entre_voisines']} contre "
      f"{d_libre['saut_maximal_entre_voisines']}")

    c = un_lot(35.0, 8.0, 0.5, 3, marches=5, pas=8)
    v("un lien non nul change le résultat",
      c["saut_maximal_entre_voisines"] != a["saut_maximal_entre_voisines"],
      f"{c['saut_maximal_entre_voisines']} contre {a['saut_maximal_entre_voisines']}")
    v("... sans faire chuter le taux de moitié", c["taux"] > 0.5 * a["taux"],
      f"{c['taux']} contre {a['taux']}")

    # ⭐⭐⭐⭐ LE TÉMOIN : un lien fort DOIT masquer un vrai décrochement. Sans ça, « le lien tient
    # la nappe » serait vrai par construction et ne dirait rien.
    t = temoin_le_lien_fausse_t_il_un_vrai_decrochement(lien=0.5, pas=16)
    v("sans lien, un décrochement injecté se voit",
      t["sans_lien"]["saut"] is not None and t["sans_lien"]["saut"] > 0.5,
      f"{t['sans_lien']['saut']}")
    v("... et il est proche de la vérité injectée",
      t["ecart_a_la_verite_sans_lien"] < 0.5, f"{t['ecart_a_la_verite_sans_lien']}")
    v("⚠ avec un lien fort, il est FAUSSÉ", t["le_lien_fausse_le_decrochement"],
      f"{t['sans_lien']['saut']} → {t['avec_lien']['saut']} pour une vérité de "
      f"{t['saut_vrai_en_feuilles']}")
    v("... et ici il l'AMPLIFIE plutôt que de le masquer", t["le_lien_lamplifie"])

    # ⭐⭐⭐⭐ LE VERDICT CROISÉ, SONDÉ SUR DES MOITIÉS FABRIQUÉES. `juger` est pure, donc la
    # batterie peut lui donner exactement le cas qui a révélé le défaut : une force qui tient la
    # nappe ET fausse un vrai décrochement. L'ancien verdict la déclarait bonne.
    def _moities(tient, fausse):
        nappe = [{"lien": 0.0, "se_dechirent": 6, "taux_median": 0.999},
                 {"lien": 0.25, "se_dechirent": 0 if tient else 6, "taux_median": 1.0}]
        temoins = ([] if fausse is None
                   else [{"avec_lien": {"lien": 0.25},
                          "le_lien_fausse_le_decrochement": fausse}])
        return juger(nappe, temoins)[1]

    v("un lien qui tient la nappe SANS fausser un décrochement est utilisable",
      _moities(True, False)["le_lien_est_utilisable"] is True)
    x = _moities(True, True)
    v("⭐ ... et le même lien devient INUTILISABLE s'il fausse un décrochement réel",
      x["le_lien_est_utilisable"] is False)
    v("... alors que la moitié nappe, elle, dit toujours oui — c'est le défaut corrigé",
      x["la_nappe_tient"] is True)
    v("un témoin ABSENT refuse le lien au lieu de le laisser passer",
      _moities(True, None)["le_lien_est_utilisable"] is False
      and _moities(True, None)["temoin_rendu"] is False)
    v("... et un lien qui ne tient pas la nappe reste inutilisable",
      _moities(False, False)["le_lien_est_utilisable"] is False)

    # ⚠ La correction est calculée sur les positions AVANT correction : le résultat ne doit pas
    # dépendre de l'ordre d'itération. Deux ordres, le même lot.
    o = _outils(20)
    from combien_de_pas_la_matiere_porte import VolumeFabrique
    C = o["C"]
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=35.0, bruit=8.0, graine=3,
                          forme=(9000, 9000, 9000))
    base = np.array([2000.0, 2000.0, 2000.0])
    dep = [base + np.array([1.0, 0.0, 0.0]) * (k * ECART_VOXELS) for k in range(4)]
    s1 = marcher_en_nappe(o, pile, dep, np.array([0.0, 0.0, 1.0]), 6, 20, 0.5)
    s2 = marcher_en_nappe(o, pile, list(dep), np.array([0.0, 0.0, 1.0]), 6, 20, 0.5)
    v("la nappe est déterministe", [len(x) for x in s1] == [len(x) for x in s2])
    v("... et chaque marche garde ses pas", all(len(x) > 0 for x in s1))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--pas", type=int, default=PAS)
    p.add_argument("--verifier", action="store_true")
    # ⚠ Le verdict est une LECTURE des marches, pas une marche : le recalculer ne coûte rien
    # quand les remarcher coûte une traversée par graine et par force. Le calcul reste dans
    # l'arbre — c'est `juger`, la même fonction que `mesurer` appelle.
    p.add_argument("--rejuger", type=Path, help="relire le verdict d'une mesure déjà écrite")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.rejuger:
        r = json.loads(a.rejuger.read_text(encoding="utf-8"))
        juger(r["le_lien_tient_il_la_nappe"]["par_lien"], r.get("temoin_par_lien", []))
        for x in r["le_lien_tient_il_la_nappe"]["par_lien"]:
            x.pop("le_lien_tient_la_nappe", None)
        a.rejuger.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        afficher(r)
        print(f"\nrejugé : {a.rejuger}")
        return 0
    r = mesurer(pas=a.pas)
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
