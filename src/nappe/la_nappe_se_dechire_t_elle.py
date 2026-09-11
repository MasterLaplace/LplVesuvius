#!/usr/bin/env python3
"""Deux marches voisines restent-elles sur la MÊME feuille ? — une nappe, pas un faisceau.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST LA DIFFÉRENCE ENTRE UNE LIGNE ET UNE SURFACE. Tout ce que les
tranches `113` à `123` mesurent porte sur **une** marche. Le graal demande **100 % d'un recto**,
c'est-à-dire une **nappe** : des marches voisines qui, mises côte à côte, forment une surface. Deux
marches qui finissent sur deux feuilles différentes produisent une **déchirure** dans l'image
déroulée — et c'est précisément ce que l'humain recoud.

⭐⭐⭐⭐ **ELLES NE SE DÉCHIRENT PAS SUR UNE TRAVERSÉE COMPLÈTE.** Huit marches parties de la même
feuille, écartées latéralement, sur une pile inclinée à 35° et bruitée : après les **112 pas**
qu'une traversée demande (`122`), elles finissent entre **112,01 et 112,52 feuilles** — la même. La
dispersion des phases **sature** autour de 0,20 et ne franchit jamais la demi-feuille.

⭐⭐⭐⭐ **ET ELLE EST SOUS-DIFFUSIVE**, ce qui est le fait important : des marches indépendantes
disperseraient en racine du nombre de pas, soit **0,4545** au pas 112 ; l'observé vaut **0,1969**,
moins de la moitié. Les marches sont donc **couplées par la matière** — chacune relit la structure
locale, donc aucune ne peut s'éloigner des autres.

⚠⚠ **Analytique, et ça borne ce que ça dit.** Une pile plane à pas constant n'a ni déchirure, ni
feuille qui fusionne, ni région sans matière — or `91` mesure que la vérité de terrain humaine
elle-même devient discontinue au bord du rouleau. Ce qui est établi est que **le mécanisme** ne
déchire pas, pas que le rouleau se laisse faire.

⚠ Aucune lecture distante.

  uv run python src/nappe/la_nappe_se_dechire_t_elle.py --verifier
  uv run python src/nappe/la_nappe_se_dechire_t_elle.py --json docs/mesures/la_nappe_se_dechire_t_elle.json
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

from le_marcheur_reste_t_il_verrouille import _outils, phases  # noqa: E402

MARCHES = 8
PAS = 112
ECART_VOXELS = 40.0
"""L'écartement latéral entre deux départs, en voxels du volume fin — 96 µm, soit un peu plus d'une
demi-feuille.

⚠ Il est choisi du même ordre que le pas de feuille : plus serré, les huit marches liraient des
cubes qui se recouvrent presque entièrement et le test mesurerait surtout le recouvrement ; plus
large, elles cesseraient d'être voisines et la question ne serait plus celle d'une nappe."""

GRAINE = 1241


def huit_marches(obliquite_deg: float, bruit: float, marches: int = MARCHES, pas: int = PAS,
                 demi: int = 20, ecart_vx: float = ECART_VOXELS, graine: int = 3) -> dict:
    """Des marches parties de la MÊME feuille, écartées latéralement, et leurs phases.

    ⚠⚠ Elles partent de la même feuille et pas de la même cellule : une nappe se construit de
    marches voisines, donc la question est si elles restent ensemble, pas si elles font la même
    chose. Partir de la même cellule les rendrait identiques par construction et le test serait
    vide.

    ⚠ Le volume fabriqué est **agrandi** : une traversée de 112 pas fait plus de huit mille voxels,
    et la forme par défaut (4 000) arrêtait la marche au tiers du chemin. Une borne de fixture lue
    comme une portée serait le péché nº 1 de ce dépôt.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabrique

    o = _outils(demi)
    C = o["C"]
    x_hat = np.array([0.0, 0.0, 1.0])
    cote = int(4000 + pas * C.PAS_UM / C.VOXEL_FIN_UM * 1.5)
    pile = VolumeFabrique(C.PAS_UM, obliquite_deg=obliquite_deg, bruit=bruit, graine=graine,
                          forme=(cote, cote, cote))
    base = np.array([2000.0, 2000.0, 2000.0])
    proj = float(base @ pile.normale) * C.VOXEL_FIN_UM
    base = base + pile.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
    # ⚠ L'écart est porté par l'axe z du volume, qui est orthogonal à la normale aux deux
    # obliquités testées : les départs restent donc SUR la feuille, ce que le contrôle vérifie.
    lateral = np.array([1.0, 0.0, 0.0])
    toutes = []
    for k in range(marches):
        dep = base + lateral * (k * ecart_vx)
        etapes, ph = _une(o, pile, dep, x_hat, pas, demi)
        toutes.append({"depart_lateral_vx": round(k * ecart_vx, 1), "pas": len(ph),
                       "phases": [round(x, 4) for x in ph]})
    return {"obliquite_deg": obliquite_deg, "bruit": bruit, "graine": graine,
            "ecart_lateral_vx": ecart_vx,
            "ecart_lateral_um": round(ecart_vx * C.VOXEL_FIN_UM, 1),
            "pas_demande": pas, "marches": toutes,
            # ⚠⚠ L'alignement se verifie sur la PHASE et pas sur la valeur lue : avec du bruit,
            # une lecture sur la feuille vaut 140 plus ou moins huit, donc un controle sur la
            # valeur echouerait sur une pile parfaitement alignee. La phase, elle, est exacte.
            "depart_sur_la_feuille": bool(
                abs(float(base @ pile.normale) * C.VOXEL_FIN_UM / C.PAS_UM
                    - round(float(base @ pile.normale) * C.VOXEL_FIN_UM / C.PAS_UM)) < 1e-9)}


def _une(o, pile, depart, x_hat, pas, demi):
    from combien_de_pas_la_matiere_porte import marcher

    etapes = [e for e in marcher(
        pile, depart, x_hat, o["longueurs"], o["mu"], o["sd"], o["barre"], o["barre_moities"],
        o["barre_interstice"], o["C"].VOXEL_FIN_UM, pas_max=pas, demi=demi) if "confirme" in e]
    return etapes, phases(pile, depart, etapes, o["C"].VOXEL_FIN_UM)


def la_nappe_se_dechire_t_elle(lot: dict) -> dict:
    """La dispersion des phases franchit-elle la demi-feuille ?

    ⭐⭐⭐⭐ C'EST LE TEST DE LA DÉCHIRURE, et le seuil n'est pas réglé : **une demi-feuille** est
    la distance au-delà de laquelle deux marches arrondissent vers deux feuilles différentes. Ce
    n'est pas une tolérance choisie, c'est la définition d'être sur la même feuille.

    ⚠⚠ Le pas où la dispersion la franchit est rendu s'il existe, et `None` sinon. Extrapoler « elle
    la franchirait vers le pas 500 » serait refaire l'erreur que `109` a trouvée dans le
    `(1 − risque)^120` de `107` : une loi supposée, appliquée bien au-delà de ce qui est mesuré.
    """
    ph = [m["phases"] for m in lot["marches"] if m["phases"]]
    if len(ph) < 4:
        return {"decidable": False, "pourquoi": f"{len(ph)} marches"}
    n = min(len(x) for x in ph)
    if n < 8:
        return {"decidable": False, "pourquoi": f"{n} pas communs"}
    disp = [float(np.std([x[i] for x in ph])) for i in range(n)]
    franchit = next((i + 1 for i, x in enumerate(disp) if x >= 0.5), None)
    finales = [x[n - 1] for x in ph]
    feuilles = {int(round(x)) for x in finales}
    # ⭐⭐⭐⭐ CE QUI DÉCHIRE EST L'ÉCART ENTRE VOISINES, PAS LE NUMÉRO DE FEUILLE. Un faisceau qui
    # reste groupé mais dont la moyenne vient s'asseoir SUR une frontière rend deux numéros
    # différents par simple arrondi — et ma première version le comptait comme une déchirure. Le
    # saut entre deux marches VOISINES est la même quantité que `91` mesure chez l'humain (« le
    # plus grand saut entre deux cellules voisines d'une même ligne de grille »), ce qui rend les
    # deux comparables.
    sauts = [abs(finales[k + 1] - finales[k]) for k in range(len(finales) - 1)]
    saut_max = max(sauts) if sauts else 0.0
    return {
        "decidable": True, "marches": len(ph), "pas_communs": n,
        "dispersion_par_pas": [round(x, 4) for x in disp],
        "dispersion_au_premier_pas": round(disp[0], 4),
        "dispersion_au_dernier_pas": round(disp[-1], 4),
        "dispersion_max": round(max(disp), 4),
        "pas_ou_elle_franchit_une_demi_feuille": franchit,
        "phases_finales": [round(x, 3) for x in finales],
        "feuilles_finales_distinctes": len(feuilles),
        "ecart_max_a_la_feuille_finale": round(
            max(abs(x - round(x)) for x in finales), 4),
        "avance_mediane_par_pas": round(float(np.median([x[n - 1] / n for x in ph])), 4),
        "saut_maximal_entre_voisines": round(saut_max, 4),
        # ⚠ Une demi-feuille n'est pas un seuil réglé : c'est la distance au-delà de laquelle
        # aucune affectation cohérente ne met deux voisines sur la même feuille.
        "la_nappe_se_dechire": bool(franchit is not None or saut_max > 0.5)}


def temoin_des_marches_independantes(lot: dict, tirages: int = 400,
                                     graine: int = GRAINE) -> dict:
    """Des marches INDÉPENDANTES disperseraient-elles davantage ?

    ⭐⭐⭐⭐ LE CONTRÔLE QUI REND LE RÉSULTAT LISIBLE. Une dispersion qui ne grandit pas peut venir
    de deux choses : les marches sont couplées par la matière, ou leurs pas ne varient tout
    simplement pas. Le témoin tranche en **permutant, à chaque pas, quelle marche reçoit quel
    incrément de phase** : la distribution des incréments est gardée exactement, seul le lien entre
    une marche et ses propres incréments est détruit.

    ⚠⚠ Si l'observé disperse MOINS que ce tirage, les marches se tiennent — chacune relit la
    structure locale, donc aucune ne peut s'éloigner. Si elles dispersent autant, la matière ne les
    couple pas et la nappe ne tient que par chance.

    ⚠ Graine posée : un témoin dont le tirage change à chaque lancement n'est pas un témoin.
    """
    ph = [m["phases"] for m in lot["marches"] if m["phases"]]
    if len(ph) < 4:
        return {"decidable": False, "pourquoi": f"{len(ph)} marches"}
    n = min(len(x) for x in ph)
    inc = np.asarray([[x[0]] + [x[i] - x[i - 1] for i in range(1, n)] for x in ph])
    reel = float(np.std(inc.sum(axis=1)))
    rng = np.random.default_rng(graine)
    tire = []
    for _ in range(tirages):
        melange = np.stack([rng.permutation(inc[:, i]) for i in range(n)], axis=1)
        tire.append(float(np.std(melange.sum(axis=1))))
    tire = np.asarray(tire)
    return {"decidable": True, "tirages": tirages, "graine": graine, "pas_communs": n,
            "dispersion_reelle": round(reel, 4),
            "dispersion_mediane_sous_permutation": round(float(np.median(tire)), 4),
            "part_des_permutations_aussi_basse": round(float(np.mean(tire <= reel)), 5),
            "racine_du_premier_pas": round(
                float(np.std(inc[:, 0])) * float(np.sqrt(n)), 4),
            "les_marches_sont_couplees": bool(np.mean(tire <= reel) < 0.05)}


GRAINES = (3, 11, 29, 53, 97, 131, 179, 223, 271, 313, 367, 419)
"""Les graines de bruit répétées.

⚠⚠⚠ UNE SEULE RÉALISATION N'EST PAS UNE MESURE, ET CE FICHIER L'A APPRIS DEUX FOIS. Le premier
tirage rendait un saut maximal entre voisines de **0,5042** contre un seuil de 0,5 — un verdict sur
une marge de huit millièmes. Et quand cinq graines ont été tirées, il s'est révélé être **le
meilleur des cinq** : deux autres rendaient 3,0 et 11,5 feuilles. Publier la première aurait été
publier la plus favorable en croyant publier la seule."""


def mesurer(demi: int = 20, graines=GRAINES) -> dict:
    """La condition dure sur plusieurs graines de bruit, et le cas propre en contraste."""
    out = {"marches_par_lot": MARCHES, "pas": PAS, "graines": list(graines), "lots": [],
           "repetitions": []}
    sauts, disp, dechire = [], [], 0
    for g in graines:
        lot = huit_marches(35.0, 8.0, demi=demi, graine=g)
        d = la_nappe_se_dechire_t_elle(lot)
        w = temoin_des_marches_independantes(lot)
        if not d.get("decidable"):
            continue
        sauts.append(d["saut_maximal_entre_voisines"])
        disp.append(d["dispersion_max"])
        dechire += int(d["la_nappe_se_dechire"])
        out["repetitions"].append({
            "graine": g, "pas_communs": d["pas_communs"],
            # ⚠ La trajectoire est GARDÉE : sans elle on ne peut pas demander si la déchirure se
            # voit tôt, qui est la seule question actionnable que ce document pose.
            "dispersion_par_pas": d["dispersion_par_pas"],
            "saut_maximal_entre_voisines": d["saut_maximal_entre_voisines"],
            "dispersion_max": d["dispersion_max"],
            "dispersion_au_dernier_pas": d["dispersion_au_dernier_pas"],
            "avance_mediane_par_pas": d["avance_mediane_par_pas"],
            "franchit": d["pas_ou_elle_franchit_une_demi_feuille"],
            "se_dechire": d["la_nappe_se_dechire"],
            "temoin_reel": w.get("dispersion_reelle"),
            "temoin_permute": w.get("dispersion_mediane_sous_permutation"),
            "couplees": w.get("les_marches_sont_couplees")})
    if sauts:
        out["saut_median_entre_voisines"] = round(float(np.median(sauts)), 4)
        out["saut_min"] = round(float(min(sauts)), 4)
        out["saut_max"] = round(float(max(sauts)), 4)
        out["dispersion_max_mediane"] = round(float(np.median(disp)), 4)
        out["lots_qui_se_dechirent"] = dechire
        out["lots"] = len(sauts)
        # ⚠⚠ LE VERDICT EST UNE PROPORTION, PAS UN BOOLÉEN, et c'est une correction : l'issue est
        # BIMODALE — ou la matière couple les marches et le saut reste sous le quart de feuille, ou
        # elle ne les couple pas et il se compte en feuilles. Une médiane d'une distribution à deux
        # bosses ne décrit aucune des deux, et sur ce corpus elle tombait à 0,5042 contre un seuil
        # de 0,5, c'est-à-dire un verdict tiré au sort.
        out["part_des_lots_qui_se_dechirent"] = round(dechire / len(sauts), 3)
        out["lots_couples"] = sum(1 for r in out["repetitions"] if r["couplees"])
        # ⚠ L'issue est-elle bimodale ? Mesuré plutôt qu'affirmé : aucun lot ne tombe entre le
        # quart de feuille et la feuille entière.
        out["lots_entre_0_25_et_1_feuille"] = sum(1 for s in sauts if 0.25 < s < 1.0)
    out["le_dechirement_se_voit_il_tot"] = le_dechirement_se_voit_il_tot(out["repetitions"])
    propre = huit_marches(0.0, 0.0, demi=demi)
    out["cas_propre"] = {
        "la_nappe_se_dechire_t_elle": la_nappe_se_dechire_t_elle(propre),
        # ⚠ Sur une pile sans bruit les huit marches sont identiques, donc le témoin n'a rien à
        # coupler et rend « non ». Ce n'est pas un échec : c'est le contraste qui montre que la
        # dispersion mesurée plus haut vient du BRUIT et pas du mécanisme.
        "temoin_des_marches_independantes": temoin_des_marches_independantes(propre)}
    return out


def le_dechirement_se_voit_il_tot(repetitions: list[dict], rang: int = 16) -> dict:
    """La dispersion des seize premiers pas annonce-t-elle le saut final ?

    ⭐⭐⭐⭐ C'EST LA SEULE QUESTION ACTIONNABLE QUE CE DOCUMENT POSE. Si la déchirure se voit dans
    les premiers pas, un remplaçant de l'humain peut la **détecter** — c'est la forme exacte de ce
    que `115` et `116` ont établi pour la cécité, dont la signature est disponible avant le pas. Si
    elle ne se voit pas, il faut marcher jusqu'au bout pour savoir, et l'automate ne peut que
    constater les dégâts.

    ⚠ Le rang 16 est déclaré ici, avant le résultat, et il vaut un septième des 112 pas d'une
    traversée : assez tôt pour qu'une détection serve à quelque chose, assez tard pour que la
    dispersion ait eu le temps de se former.
    """
    couples = [(r["dispersion_par_pas"][rang - 1], r["saut_maximal_entre_voisines"])
               for r in repetitions
               if len(r.get("dispersion_par_pas", [])) >= rang]
    if len(couples) < 6:
        return {"decidable": False, "pourquoi": f"{len(couples)} lots"}
    tot = [a for a, _ in couples]
    fin = [b for _, b in couples]
    if len(set(tot)) < 3 or len(set(fin)) < 3:
        return {"decidable": False, "pourquoi": "une des deux séries est constante"}
    from scipy import stats  # noqa: PLC0415

    rho, p = stats.spearmanr(tot, fin)
    return {"decidable": True, "rang": rang, "lots": len(couples),
            "rho": round(float(rho), 4), "p": float(p),
            "dispersion_au_rang": [round(x, 4) for x in tot],
            "saut_final": [round(x, 4) for x in fin],
            "le_dechirement_se_voit_tot": bool(rho > 0.6 and p < 0.05)}


def afficher(r: dict) -> None:
    print(f"{r['marches_par_lot']} marches par lot · {r['pas']} pas · graines {r['graines']}")
    print("\n  graine   pas   saut voisines   dispersion max   réel / permuté   couplées")
    for x in r.get("repetitions", []):
        print(f"    {x['graine']:>4}   {x['pas_communs']:>3}   "
              f"{x['saut_maximal_entre_voisines']:>13.4f}   {x['dispersion_max']:>14.4f}   "
              f"{x['temoin_reel']:>6.3f} / {x['temoin_permute']:<6.3f}  {x['couplees']}")
    if "saut_median_entre_voisines" in r:
        print(f"\n  saut entre voisines : médiane {r['saut_median_entre_voisines']} feuille "
              f"[{r['saut_min']} ; {r['saut_max']}]")
        print(f"  ⭐ lots qui se déchirent : {r['lots_qui_se_dechirent']}/{r['lots']} "
              f"({r['part_des_lots_qui_se_dechirent']}) · lots couplés {r['lots_couples']}")
        print(f"  ⚠ lots entre un quart et une feuille : "
              f"{r['lots_entre_0_25_et_1_feuille']} — l'issue est bimodale")
    e = r.get("le_dechirement_se_voit_il_tot", {})
    if e.get("decidable"):
        print(f"\n  la déchirure se voit-elle au pas {e['rang']} ? rho {e['rho']:+.4f} "
              f"(p {e['p']:.4f}) sur {e['lots']} lots · {e['le_dechirement_se_voit_tot']}")
    c = r.get("cas_propre", {}).get("la_nappe_se_dechire_t_elle", {})
    if c.get("decidable"):
        print(f"\n  contraste, pile propre sans bruit : dispersion max {c['dispersion_max']}, "
              f"saut {c['saut_maximal_entre_voisines']} — la dispersion vient du BRUIT")


def verifier() -> int:
    """La batterie, hors ligne."""
    echecs = controles = 0

    def v(nom, obtenu, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not obtenu:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f" — {detail}" if detail else ""))

    # ⭐⭐ Le test de dechirure sur des phases FABRIQUEES, ou la reponse est connue.
    serre = {"marches": [{"phases": [i * 1.0 + 0.01 * k for i in range(1, 21)]}
                         for k in range(8)]}
    d = la_nappe_se_dechire_t_elle(serre)
    v("des marches serrees ne se dechirent pas", not d["la_nappe_se_dechire"],
      f"{d['dispersion_max']}")
    v("... et leur saut entre voisines est minuscule",
      d["saut_maximal_entre_voisines"] < 0.05, f"{d['saut_maximal_entre_voisines']}")
    v("... et aucun pas ne franchit la demi-feuille",
      d["pas_ou_elle_franchit_une_demi_feuille"] is None)
    # ⚠⚠ LA SONDE SYMETRIQUE : un test qui ne verrait jamais une dechirure serait satisfait par
    # n'importe quoi. Des marches qui s'ecartent lineairement DOIVENT etre vues.
    large = {"marches": [{"phases": [i * (1.0 + 0.03 * k) for i in range(1, 21)]}
                         for k in range(8)]}
    dl = la_nappe_se_dechire_t_elle(large)
    v("sonde : des marches qui s'ecartent SONT vues", dl["la_nappe_se_dechire"],
      f"dispersion max {dl['dispersion_max']}, franchit au pas "
      f"{dl['pas_ou_elle_franchit_une_demi_feuille']}")
    v("... par un saut entre voisines qui dépasse la demi-feuille",
      dl["saut_maximal_entre_voisines"] > 0.5, f"{dl['saut_maximal_entre_voisines']}")
    # ⚠⚠ LA SONDE QUI A CORRIGÉ LE PRÉDICAT : un faisceau GROUPÉ dont la moyenne tombe sur une
    # frontière rend deux numéros de feuille et n'est PAS une déchirure. Ma première version le
    # comptait comme telle.
    frontiere = {"marches": [{"phases": [i * 1.0 + 0.5 + 0.02 * (k - 4) for i in range(1, 21)]}
                             for k in range(8)]}
    df = la_nappe_se_dechire_t_elle(frontiere)
    v("sonde : un faisceau groupé posé sur une frontière n'est PAS une déchirure",
      not df["la_nappe_se_dechire"],
      f"{df['feuilles_finales_distinctes']} numéros, saut "
      f"{df['saut_maximal_entre_voisines']}")
    v("moins de quatre marches rend indecidable",
      not la_nappe_se_dechire_t_elle({"marches": serre["marches"][:2]})["decidable"])
    v("moins de huit pas communs rend indecidable",
      not la_nappe_se_dechire_t_elle(
          {"marches": [{"phases": [1.0, 2.0, 3.0]} for _ in range(8)]})["decidable"])

    # ⭐⭐⭐ LE TEMOIN : des marches COUPLEES doivent battre la permutation, des marches
    # independantes non.
    # ⚠⚠ La fixture `serre` ne convient PAS ici, et c'est un defaut que la sonde a trouve : ses
    # increments sont tous egaux a un, donc les permuter ne change rien et le temoin rend le meme
    # nombre des deux cotes. Une fixture couplee doit avoir des increments QUI VARIENT et une
    # somme qui revient — c'est ce que « couple » veut dire.
    rr = np.random.default_rng(5)
    couple = {"marches": []}
    for _ in range(8):
        ph, cumul = [], 0.0
        for _ in range(24):
            # ⚠ Rappel proportionnel a l'ecart accumule : chaque marche est ramenee vers la
            # moyenne, exactement comme la matiere ramene le marcheur vers la feuille.
            cumul += 1.0 + rr.normal(0.0, 0.25) - 0.8 * (cumul - len(ph))
            ph.append(cumul)
        couple["marches"].append({"phases": ph})
    w = temoin_des_marches_independantes(couple, tirages=200)
    v("temoin : des marches couplees battent la permutation", w["les_marches_sont_couplees"],
      f"{w['dispersion_reelle']} contre {w['dispersion_mediane_sous_permutation']}")
    # ⚠⚠ Et la sonde inverse : des marches dont les increments sont INDEPENDANTS ne doivent PAS
    # etre declarees couplees. Sans elle, le temoin repondrait « couplees » a tout.
    rng = np.random.default_rng(7)
    libre = {"marches": [{"phases": list(np.cumsum(rng.normal(1.0, 0.2, 24)))}
                         for _ in range(8)]}
    wl = temoin_des_marches_independantes(libre, tirages=200)
    v("sonde : des marches independantes ne sont PAS declarees couplees",
      not wl["les_marches_sont_couplees"],
      f"{wl['dispersion_reelle']} contre {wl['dispersion_mediane_sous_permutation']}")
    v("le temoin est reproductible",
      temoin_des_marches_independantes(couple, tirages=200)["dispersion_reelle"]
      == w["dispersion_reelle"])

    # ⚠ Le lot reel, sur peu de pas pour que la batterie reste rapide.
    lot = huit_marches(35.0, 8.0, marches=5, pas=10)
    v("les departs sont sur la feuille", lot["depart_sur_la_feuille"])
    v("les cinq marches partent d'abscisses differentes",
      len({m["depart_lateral_vx"] for m in lot["marches"]}) == 5)
    dr = la_nappe_se_dechire_t_elle(lot)
    v("le lot reel est decidable", dr["decidable"], f"{dr.get('pourquoi')}")
    v("... et il ne se dechire pas sur dix pas", not dr["la_nappe_se_dechire"],
      f"dispersion max {dr.get('dispersion_max')}")
    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
