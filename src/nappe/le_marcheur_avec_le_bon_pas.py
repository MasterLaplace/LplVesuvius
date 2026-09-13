#!/usr/bin/env python3
"""Le marcheur porte-t-il plus loin avec le BON pas ? — `102` rejoue, et ses etapes gardees.

⚠⚠⚠ POURQUOI CE FICHIER, ET TROIS TRANCHES L'IMPOSENT. `102` a mesure que la matiere porte deux
pas confirmes, avec un marcheur dont `105` a montre que le pas est **+18,4 % trop grand** : il
avance de ce que `pas_montre_calibre` rend, et ce selecteur lit un cran trop haut. Refaire la
marche avec le selecteur corrige est donc la relance qui compte, parce que c'est celle qui EST le
graal — les autres rendraient des nombres justes pour une quantite dont `106` a montre que le sens
reste ouvert.

⭐⭐⭐ ET ELLE REPOND EN MEME TEMPS AUX DEUX QUESTIONS QUE `104` A LAISSEES, parce que cette fois
LES ETAPES SONT GARDEES. `102` a marche 224 fois en ne conservant qu'une mediane par bande ; d'une
mediane de quatre on ne tire que `a2 <= m <= a3`, donc la survie n'y etait bornee qu'a 0,5 pres, et
un risque par pas constant de 0,056 a 0,546 y restait compatible. **Un agregat ne se desagrege
pas**, et aucune relecture ne rend ce qui n'a pas ete ecrit.

⭐⭐⭐ LA COMPARAISON EST APPARIEE PAR LE DEPART, ET C'EST LA SEULE FORME HONNETE POUR UNE MARCHE.
Les deux marcheurs partent de la MEME cellule avec le MEME sens initial ; ils divergent ensuite
parce que leurs pas differents les menent ailleurs, donc ils ne lisent pas les memes cubes. Apparier
les LECTURES est impossible pour une marche ; apparier les DEPARTS l'est, et c'est ce que `102`
faisait deja entre le marcheur et le temoin naif.

⭐⭐ TROIS QUANTITES SORTENT DE LA MEME COURSE, et chacune repond a une question differente :
    - les pas CONSECUTIFS confirmes, le chiffre de `102`, refait avec le bon pas ;
    - le RISQUE par pas, conditionnel a avoir tenu les precedents — c'est lui qui decide du graal,
      un risque constant `p` rendant `(1-p)^120` sur cent vingt spires ;
    - le REGISTRE des feuilles franchies, en fraction CONTINUE, qui dit de combien le marcheur
      derive sans que rien ne le signale (`104`).

⚠⚠ LA CENSURE SE DIT AVANT LE RESULTAT QU'ELLE BORNE. Une cellule au plafond de pas dit « AU
MOINS ceci », pas « ceci » ; publier la mediane sans dire qu'elle est tronquee ferait passer un
budget de lecture pour une limite de matiere — la butee de `99`.

Usage :
    uv run python src/nappe/le_marcheur_avec_le_bon_pas.py --verifier
    uv run python src/nappe/le_marcheur_avec_le_bon_pas.py --bandes 28 --cellules 2 --pas 8 \\
        --json docs/mesures/le_marcheur_avec_le_bon_pas.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

# ⚠⚠⚠ DECLARES AVANT TOUT RESULTAT, ET LE CHIFFRE A ETE MESURE TROIS FOIS AVANT D'ETRE JUSTE.
# `104` projetait **22,92 s** par etape en additionnant un cube et deux planchers de segment. Un
# premier pilote en a mesure **58,5** — mais il tournait EN CONCURRENCE avec une autre batterie, et
# *un cout mesure sous contention n'est pas un cout*. Mesure seule : **38,0 s** par pas sur une
# marche de six pas, avec 2,2 s de mise en place.
#
# ⭐⭐ ET LA REPARTITION EST MESUREE, CE QUI DESIGNE LE SEUL LEVIER REEL : sur un pas isole le cube
# coute **14,88 s** contre 0,76 pour le balayage et 0,70 pour la verification — **91 %**. Monter
# les fils de 32 a 96 ne gagne rien (14,88 -> 15,62 s, legerement pire) : la lecture suit les
# PLAGES d'octets et non la latence, exactement ce que `103` a mesure. Et l'ecart entre 14,88 s
# pour un pas isole et 38,0 s en marche vient de ce qu'une marche se DEPLACE : chaque pas lit un
# cube dans des morceaux jamais atteints.
#
# ⭐ Consequence : 28 x 1 x 6 x 2 selecteurs = **336 etapes**, soit **3,5 h**. Vingt-huit marches
# par selecteur, ce qui est mince pour une courbe de risque et suffisant pour compter des
# premieres chutes — `104` avait etabli que couvrir bat approfondir pour cela.
SECONDES_PAR_ETAPE_MESUREES = 38.0

# ⚠⚠⚠ LE COUT D'UNE ETAPE A ETE MESURE QUATRE FOIS ET IL A RENDU QUATRE VALEURS. Les publier
# toutes avec leur CONDITION vaut mieux qu'un chiffre unique, parce que la dispersion EST le
# resultat : une lecture distante ne coute pas une constante, elle coute ce que le reseau a deja
# servi. `103` avait mesure « 15,4 s par cube » ; ce chiffre est juste et il ne se transpose pas
# tel quel a une marche, qui se DEPLACE et touche donc des morceaux jamais atteints.
COUTS_PAR_ETAPE_MESURES = (
    {"secondes": 22.92, "condition": "projeté par `104` : un cube plus deux planchers de segment",
     "mesure": False},
    {"secondes": 58.5, "condition": "pilote lancé EN CONCURRENCE avec une autre batterie",
     "mesure": True},
    {"secondes": 38.0, "condition": "marche de six pas mesurée SEULE, sur des cellules déjà lues",
     "mesure": True},
    {"secondes": 55.0, "condition": "première bande de la course complète, cellules neuves",
     "mesure": True},
)


def cout_par_etape_mesure() -> dict:
    """Les quatre mesures du cout d'une etape, avec leur condition — la dispersion EST le resultat.

    ⭐⭐⭐ ELLE EXISTE PARCE QUE CE CHIFFRE M'A ECHAPPE QUATRE FOIS, et qu'un chiffre publie dont on
    tait les conditions se lit comme une constante. *Un cout mesure sous contention n'est pas un
    cout* ; et un cout mesure sur des cellules deja servies n'est pas celui d'une cellule neuve.

    ⚠ La valeur retenue pour les projections est la plus grande des mesures FIABLES, parce qu'une
    projection trop basse fait lancer une course qu'on ne peut pas finir — l'erreur qui coute, ici,
    est de sous-estimer.
    """
    fiables = [x for x in COUTS_PAR_ETAPE_MESURES
               if x["mesure"] and "CONCURRENCE" not in x["condition"]]
    return {"mesures": list(COUTS_PAR_ETAPE_MESURES),
            "retenue_pour_les_projections_s": max(x["secondes"] for x in fiables),
            "la_plus_basse_fiable_s": min(x["secondes"] for x in fiables),
            "rapport_entre_les_extremes": round(
                max(x["secondes"] for x in fiables) / min(x["secondes"] for x in fiables), 2),
            "pourquoi_elles_diffèrent": (
                "une lecture distante coûte ce que le réseau a déjà servi ; une marche se déplace "
                "et touche des morceaux jamais atteints")}
PAS_MAX = 6
CELLULES_PAR_BANDE = 1
DEMI = 20
SELECTEURS = ("calibre", "deux_roles")
SPIRES = 120


def modes_du_trajet(trajets: list[dict], pas_attendus: int) -> dict:
    """Les trajets se separent-ils en DEUX populations, et si oui lesquelles ?

    ⚠⚠⚠ ELLE EXISTE PARCE QUE J'AI PUBLIE UNE MEDIANE SUR UNE DISTRIBUTION BIMODALE. Les trajets
    rendent soit ~6 feuilles pour 6 pas (4,4 a 8,6), soit ~1 (0,5 a 1,4) ; leur mediane tombe dans
    le mode BAS par accident de comptage et se lit comme « le marcheur ne franchit presque rien »,
    alors que la moitie des marches franchit exactement ce qu'elle doit. **Une mediane sur une
    distribution bimodale n'est pas un resume, c'est un choix de mode qui s'ignore.**

    ⚠⚠ LE SEUIL EST LA MOITIE DU COMPTE ATTENDU, et il est DERIVE et non regle : un trajet qui a
    franchi moins de la moitie des feuilles qu'il aurait du ne mesure pas des feuilles. Le placer
    ailleurs demanderait de le justifier ; celui-ci se lit tout seul.

    ⭐ Et les deux modes sont rendus avec leur EFFECTIF : un mode a deux marches n'est pas un mode.
    """
    if not trajets:
        return {"decidable": False, "pourquoi": "aucun trajet lisible"}
    seuil = 0.5 * float(pas_attendus)
    haut = [x for x in trajets if x["feuilles_franchies"] >= seuil]
    bas = [x for x in trajets if x["feuilles_franchies"] < seuil]
    out = {"decidable": True, "trajets": len(trajets), "seuil_feuilles": round(seuil, 2),
           "pas_attendus": int(pas_attendus),
           "au_dessus": len(haut), "au_dessous": len(bas),
           "part_au_dessus": round(len(haut) / len(trajets), 3)}
    for nom, jeu in (("mode_haut", haut), ("mode_bas", bas)):
        if jeu:
            out[nom] = {
                "trajets": len(jeu),
                "feuilles_median": round(float(np.median(
                    [x["feuilles_franchies"] for x in jeu])), 3),
                "feuilles_par_pas_median": round(float(np.median(
                    [x["feuilles_par_pas"] for x in jeu])), 3),
                "score_median": round(float(np.median([x["score"] for x in jeu])), 3)}
    # ⭐⭐⭐ LE VERDICT : les deux modes existent-ils vraiment, ou un seul est-il peuple ? Publier
    # « bimodal » sur trois marches d'un cote serait une figure de style.
    out["les_deux_modes_sont_peuples"] = bool(len(haut) >= 5 and len(bas) >= 5)
    if "mode_haut" in out and "mode_bas" in out:
        # ⚠⚠⚠ LE SCORE SEPARE LES DEUX MODES, MAIS A L'ENVERS, ET C'EST LE FAIT QUI COMPTE : il
        # est PLUS HAUT pour les trajets qui ne mesurent RIEN (0,483) que pour ceux qui comptent
        # juste (0,371), parce qu'une derive de basse frequence s'ajuste mieux sur une longue
        # fenetre qu'un vrai signal periodique. On ne peut donc PAS s'en servir pour ecarter le
        # mauvais mode : il ecarterait le bon. Publier le SENS de l'ecart est ce qui empeche de
        # croire qu'un seuil de score reglerait la question.
        out["ecart_des_scores_entre_modes"] = round(
            out["mode_bas"]["score_median"] - out["mode_haut"]["score_median"], 3)
        out["le_score_est_plus_haut_pour_le_mode_sans_periodicite"] = bool(
            out["mode_bas"]["score_median"] > out["mode_haut"]["score_median"])
        out["un_seuil_de_score_ecarterait_le_BON_mode"] = out[
            "le_score_est_plus_haut_pour_le_mode_sans_periodicite"]
    return out


def virage_entre_pas(etapes: list[dict]) -> dict:
    """L'angle entre les directions de deux pas CONSECUTIFS, lu dans les etapes gardees.

    ⭐⭐⭐ ELLE REPOND GRATUITEMENT A LA QUESTION DU COUT, et c'est pour cela qu'elle existe. Le
    cube de direction fait **91 %** du prix d'un pas ; le seul levier restant est de le lire MOINS
    SOUVENT, puisque `103` a refute de le lire moins cher. Or la reponse est dans les etapes que
    cette tranche garde : si la direction tourne peu d'un pas au suivant, un marcheur pourrait la
    reutiliser et le prix serait divise par deux.

    ⚠⚠ ELLE NE TRANCHE PAS LA QUESTION, ELLE LA CHIFFRE. Savoir que la direction tourne de trois
    degres ne dit pas qu'un marcheur qui la reutilise porte aussi loin : cela se mesure en faisant
    marcher les deux depuis le meme depart, comme `102` l'a fait entre le marcheur et le naif. Ce
    qui est rendu ici est le chiffre qui dit si cette mesure vaut la peine d'etre payee.

    ⚠ Le signe d'une direction est arbitraire — un vecteur propre n'a pas de sens, et `106` a paye
    cet oubli — donc l'angle est pris sur le produit scalaire ABSOLU.
    """
    d = [np.asarray(x["direction"], dtype=np.float64) for x in etapes if "direction" in x]
    if len(d) < 2:
        return {"decidable": False, "pourquoi": "moins de deux pas parcourus"}
    ang = []
    for a, b in zip(d, d[1:]):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-12 or nb < 1e-12:
            continue
        c = abs(float(a @ b) / (na * nb))
        ang.append(float(np.rad2deg(np.arccos(min(c, 1.0)))))
    if not ang:
        return {"decidable": False, "pourquoi": "aucune paire de directions lisible"}
    return {"decidable": True, "paires": len(ang),
            "virage_median_deg": round(float(np.median(ang)), 2),
            "virage_p90_deg": round(float(np.percentile(ang, 90)), 2),
            "virage_max_deg": round(float(np.max(ang)), 2)}


def prix_de_la_course(bandes: int, cellules: int, pas: int, selecteurs: int = 2,
                      secondes_par_etape: float = SECONDES_PAR_ETAPE_MESUREES) -> dict:
    """Le prix de la course, chiffre AVANT de la lancer, depuis le cout MESURE par le pilote.

    ⭐⭐ ELLE EXISTE PARCE QUE MA PREMIERE PROJECTION ETAIT FAUSSE D'UN FACTEUR 2,5. `104` avait
    chiffre 22,92 s par etape en additionnant un cube et deux planchers de segment ; le pilote en
    mesure 58,5. Le cout se MESURE, il ne se modelise pas — c'est la lecon de `103`, et je viens de
    la repayer en l'appliquant trop grossierement.
    """
    etapes = bandes * cellules * pas * selecteurs
    return {"bandes": bandes, "cellules_par_bande": cellules, "pas": pas,
            "selecteurs": selecteurs, "marches": bandes * cellules * selecteurs,
            "etapes": etapes, "secondes_par_etape": secondes_par_etape,
            "heures": round(etapes * secondes_par_etape / 3600.0, 2)}


def risque_par_pas(marches: list[list[dict]]) -> list[dict]:
    """Le risque CONDITIONNEL du pas k : tomber au pas k sachant qu'on a tenu les k-1 premiers.

    ⭐⭐⭐ C'EST LA QUANTITE QUI DECIDE DU GRAAL, ET PAS LA PORTEE. Un risque constant `p` rend
    `(1-p)^120` sur cent vingt spires : a 0,3 par pas cela vaut 10^-19, donc l'enchainement est
    mort quelle que soit la portee mesuree. Un risque qui S'EFFONDRE apres les premiers pas dit
    l'inverse — la difficulte est de S'ACCROCHER, pas de PORTER — et le remede est alors un
    meilleur depart, pas un meilleur marcheur.

    ⚠ Les marches sorties du volume sont CENSUREES au pas de leur sortie, pas comptees comme des
    chutes : elles quittent le denominateur au lieu d'alimenter le numerateur.
    """
    out, k = [], 1
    while True:
        risque = tombees = 0
        for e in marches:
            pas = [x for x in e if "confirme" in x]
            if len(pas) < k:
                continue
            if any(not x["confirme"] for x in pas[: k - 1]):
                continue
            risque += 1
            if not pas[k - 1]["confirme"]:
                tombees += 1
        if risque == 0:
            break
        out.append({"pas": k, "en_risque": risque, "tombees": tombees,
                    "risque": round(tombees / risque, 3)})
        k += 1
    return out


def confirmation_marginale(marches: list[list[dict]]) -> list[dict]:
    """La part de pas k confirmes, SANS regarder l'histoire — l'autre moitie de la question.

    ⭐⭐ ELLE SE LIT CONTRE LE RISQUE CONDITIONNEL, ET C'EST LEUR ECART QUI INFORME. Si la matiere
    repond encore aussi bien au pas huit qu'au pas un alors que la course consecutive est rompue,
    les chutes sont des manques isoles sur une marche encore posee sur la matiere. Si les deux
    baissent ensemble, le marcheur s'egare vraiment.
    """
    out, k = [], 1
    while True:
        n = c = 0
        for e in marches:
            pas = [x for x in e if "confirme" in x]
            if len(pas) < k:
                continue
            n += 1
            c += 1 if pas[k - 1]["confirme"] else 0
        if n == 0:
            break
        out.append({"pas": k, "marches": n, "confirmes": c, "part": round(c / n, 3)})
        k += 1
    return out


def registre_continu(etapes: list[dict]) -> list[dict]:
    """Le REGISTRE : combien de feuilles — en fraction — ont ete franchies apres k pas.

    ⭐⭐⭐ C'EST L'INSTRUMENT QUE `104` A CONSTRUIT APRES AVOIR REFUTE LE PREMIER. Le compteur
    entier de `98` a une famille {1, 2, 3}, donc il ne descend jamais sous un : il voit un SAUT et
    il est AVEUGLE A UN RETARD. La fraction continue peut valoir moins de un, donc elle s'accumule
    en un registre qui dit sur quelle spire le marcheur se trouve — la phrase meme que l'humain
    prononce quand il corrige un transfert, et elle est gratuite.

    ⚠⚠ CE QUE LE REGISTRE NE DIT PAS : il contraint l'INDICE RADIAL de la feuille, jamais la
    position SUR la feuille. Un marcheur qui derive tangentiellement garde un registre juste. C'est
    exactement la portee du transfert de spire a spire, et rien de plus.

    ⚠ Une etape dont la fraction est en BUTEE ou absente interrompt le cumul : prolonger un
    registre a travers une valeur inconnue en ferait une invention.
    """
    out, cumul = [], 0.0
    for e in etapes:
        if e.get("fin") == "sortie du volume":
            break
        f = e.get("feuilles_franchies")
        if f is None or e.get("fraction_en_butee"):
            break
        cumul += float(f)
        out.append({"pas": int(e["pas"]), "cumul": round(cumul, 3),
                    "ecart": round(cumul - int(e["pas"]), 3),
                    "confirme": bool(e.get("confirme"))})
    return out


def registre_du_trajet_entier(lecteur, depart_fin: np.ndarray, etapes: list[dict],
                              voxel_fin_um: float, fils: int = 32) -> dict:
    """Combien de feuilles le trajet ENTIER a franchies, lu en UNE fois sur toute sa longueur.

    ⚠⚠⚠ POURQUOI CETTE FONCTION EXISTE, ET C'EST LA SECONDE FOIS QUE LE REGISTRE PAR PAS MEURT.
    `104` avait deja refute le compteur ENTIER (famille {1, 2, 3}, jamais moins de un). Le pilote de
    cette tranche a refute la fraction CONTINUE mesuree sur le segment d'UN pas : les deux
    marcheurs rendent **0,965 feuille par pas** malgre des pas de 255 et 225 µm, parce que chacun
    CHOISIT son pas pour qu'une periode y tienne. La fraction par pas est donc TAUTOLOGIQUE, et
    aucune amelioration de l'estimateur n'y changera rien.

    ⭐⭐⭐ CE QUI N'EST PAS TAUTOLOGIQUE EST LE TRAJET ENTIER. Le marcheur a optimise chaque pas
    SEPAREMENT ; il n'a jamais rien optimise sur la CONCATENATION. Si les k pas etaient justes, le
    trajet complet franchit k feuilles ; s'ils derivent, le compte global le dit — et il le dit
    d'autant mieux que k est grand, parce que l'erreur s'accumule quand la tautologie, elle, ne
    s'accumule pas.

    ⚠⚠ LE COMPTE DE FRANCHISSEMENTS EST TOPOLOGIQUE, donc il ne depend pas de la FORME du trajet :
    une ligne brisee qui traverse une famille de feuilles en croise autant qu'une droite entre les
    memes bouts, tant qu'elle ne repart pas en arriere. C'est ce qui autorise a lire une polyligne
    comme un seul segment.

    ⚠ La fenetre de frequence est etendue a `k + 4` : mesurer huit periodes avec une fenetre qui
    plafonne a 3,2 rendrait une BUTEE lue comme une mesure.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    pas = [x for x in etapes if "avance_um" in x]
    if len(pas) < 2:
        return {"decidable": False, "pourquoi": "moins de deux pas parcourus"}
    # ⚠ On reconstruit le trajet a partir des avances et des directions REELLEMENT prises, pas
    # d'une droite entre les bouts : une droite couperait au travers et compterait autre chose.
    n = C.ECHANTILLONS * len(pas)
    pts, p = [], np.asarray(depart_fin, dtype=np.float64).copy()
    for x in pas:
        d = np.asarray(x["direction"], dtype=np.float64)
        av = float(x["avance_um"]) / voxel_fin_um
        t = np.linspace(0.0, 1.0, C.ECHANTILLONS, endpoint=False)
        pts.append(p[None, :] + d[None, :] * (av * t)[:, None])
        p = p + d * av
    pts.append(p[None, :])
    zyx = np.rint(np.concatenate(pts)).astype(np.int64)
    if not lecteur.dans_le_volume(zyx).all():
        return {"decidable": False, "pourquoi": "le trajet sort du volume"}
    v = lecteur.lire(zyx, fils=fils)
    if not np.isfinite(v).all():
        return {"decidable": False, "pourquoi": "le trajet traverse un trou"}
    k = len(pas)
    frac, sc, butee = C.feuilles_franchies(v.reshape(1, -1), f_min=0.35,
                                          f_max=float(k) + 4.0)
    if not np.isfinite(frac[0]):
        return {"decidable": False, "pourquoi": "profil plat sur le trajet"}
    return {"decidable": True, "pas_parcourus": k, "echantillons": int(n),
            "feuilles_franchies": round(float(frac[0]), 3),
            "score": round(float(sc[0]), 3), "en_butee": bool(butee[0]),
            "ecart_au_compte_de_pas": round(float(frac[0]) - k, 3),
            "feuilles_par_pas": round(float(frac[0]) / k, 3),
            "longueur_um": round(sum(float(x["avance_um"]) for x in pas), 1)}


def _fisher(a: int, b: int, c: int, d: int) -> float:
    """La probabilite exacte, sous marges fixees, d'un tableau au moins aussi extreme.

    ⚠⚠ ELLE EST BILATERALE ET EXACTE, et elle existe parce que « le risque baisse » n'est un
    resultat que si l'on sait ce qu'un risque CONSTANT aurait rendu sur les memes effectifs. Ce
    depot a deja publie un modele nul applique a la confiance et pas a la valeur.
    """
    n = a + b + c + d
    if min(a + b, c + d, a + c, b + d) < 0 or n == 0:
        return 1.0

    def p(x: int) -> float:
        return (math.comb(a + b, x) * math.comb(c + d, a + c - x) / math.comb(n, a + c)
                if 0 <= a + c - x <= c + d else 0.0)

    seuil = p(a) * (1.0 + 1e-12)
    return min(1.0, sum(p(x) for x in range(0, a + b + 1) if p(x) <= seuil))


def le_risque_baisse(risques: list[dict], precoce: int = 3, fin: int = 3) -> dict:
    """Le risque des premiers pas contre celui des derniers, avec le nul d'un risque constant.

    ⭐⭐⭐ LES DEUX TIERS SONT DECLARES DANS LA SIGNATURE, donc avant de voir les chiffres : il n'y
    a pas de decoupage a regler jusqu'a ce que le resultat plaise.

    ⚠ Elle rend « indecidable » plutot qu'un verdict quand un des deux tiers n'a pas d'effectif :
    un risque tardif calcule sur deux marches survivantes n'est pas un risque, c'est un bruit.
    """
    if not risques:
        return {"decidable": False, "pourquoi": "aucun pas mesuré"}
    tot = risques[-1]["pas"]
    tp = [x for x in risques if x["pas"] <= precoce]
    tf = [x for x in risques if x["pas"] > max(tot - fin, precoce)]
    a = sum(x["tombees"] for x in tp)
    b = sum(x["en_risque"] for x in tp) - a
    c = sum(x["tombees"] for x in tf)
    d = sum(x["en_risque"] for x in tf) - c
    if (a + b) < 5 or (c + d) < 5:
        return {"decidable": False, "pourquoi": "un des deux tiers a moins de cinq pas en risque",
                "en_risque_precoce": a + b, "en_risque_tardif": c + d}
    rp, rf = a / (a + b), c / (c + d)
    p = _fisher(a, b, c, d)
    return {"decidable": True,
            "pas_precoces": [x["pas"] for x in tp], "pas_tardifs": [x["pas"] for x in tf],
            "risque_precoce": round(rp, 3), "en_risque_precoce": a + b, "tombees_precoces": a,
            "risque_tardif": round(rf, 3), "en_risque_tardif": c + d, "tombees_tardives": c,
            "rapport": (round(rp / rf, 2) if rf > 0 else None),
            "p_sous_risque_constant": round(p, 4),
            "le_risque_baisse": bool(rf < rp and p < 0.05),
            # ⚠⚠ ET LA CONSEQUENCE SUR LE GRAAL EST CALCULEE A COTE, sinon « 0,2 par pas » se lit
            # comme un petit nombre. Cent vingt spires enchainees, c'est (1-p)^120.
            "part_des_cent_vingt_spires_qui_survit_au_risque_precoce": round((1.0 - rp) ** SPIRES, 6),
            "part_des_cent_vingt_spires_qui_survit_au_risque_tardif": round((1.0 - rf) ** SPIRES, 6)}


def combien_de_pas_confirmes(etapes: list[dict]) -> int:
    """Combien de pas CONSECUTIFS la matiere a confirmes — importe de `102`, pas recopie."""
    from combien_de_pas_la_matiere_porte import combien_de_pas_confirmes as f  # noqa: PLC0415
    return f(etapes)


def controle_fabrique(longueurs, mu, sd, barre_balayage: float, barre_moities: float,
                      barre_interstice: float, pas_max: int = PAS_MAX,
                      demi: int = DEMI, obliquites=(0.0, 35.0)) -> dict:
    """Ce que les DEUX selecteurs rendent sur des empilements dont on connait la reponse.

    ⭐⭐⭐ IL EST PUBLIE PLUTOT QU'ASSERTE, et la difference compte : le lecteur doit voir sur la
    meme page que sur une pile DROITE de pas 173,0 le selecteur corrige avance de 173 la ou le
    calibre avance de 182 — sinon « le pas corrige est meilleur » se lit comme une opinion.

    ⚠ Le depart est recale sur la famille de plans, faute de quoi le controle mesurerait sa propre
    mise en place — le defaut que la fixture de `100` a paye et que `106` a repaye.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import VolumeFabrique, marcher  # noqa: PLC0415

    x_hat = np.array([0.0, 0.0, 1.0])
    out = {"pas_max": pas_max, "empilements": []}
    for th in obliquites:
        vf = VolumeFabrique(C.PAS_UM, obliquite_deg=float(th))
        dep = np.array([2000.0, 2000.0, 2000.0])
        proj = float(dep @ vf.normale) * C.VOXEL_FIN_UM
        dep = dep + vf.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
        d = {"obliquite_deg": float(th)}
        for sel in SELECTEURS:
            e = marcher(vf, dep, x_hat, longueurs, mu, sd, barre_balayage, barre_moities,
                        barre_interstice, C.VOXEL_FIN_UM, pas_max=pas_max, demi=demi,
                        selecteur=sel, barre_du_selecteur=barre_balayage)
            reg = registre_continu(e)
            d[sel] = {
                "pas_confirmes": combien_de_pas_confirmes(e),
                "pas_lu_median_um": _mediane([x.get("pas_um") for x in e]),
                "registre_final": (reg[-1]["cumul"] if reg else None),
                "ecart_final": (reg[-1]["ecart"] if reg else None),
                "pas_du_registre": len(reg)}
        out["empilements"].append(d)
    droit = next((x for x in out["empilements"] if x["obliquite_deg"] == 0.0), None)
    if droit:
        # ⭐⭐⭐ LA CONDITION QUI REND LE RESTE LISIBLE : sur une pile DROITE de pas 173,0 µm, le
        # selecteur corrige doit avancer de 173 et le calibre d'un cran de plus. Si le corrige ne
        # rendait pas la bonne longueur ICI, sa superiorite sur le vrai volume ne voudrait rien.
        out["le_corrige_lit_le_pas_vrai_sur_une_pile_droite"] = bool(
            droit["deux_roles"]["pas_lu_median_um"] is not None
            and abs(droit["deux_roles"]["pas_lu_median_um"] - C.PAS_UM) < 1.0)
        # ⚠⚠⚠ ET « LE CALIBRE LIT PLUS HAUT » N'EST PAS ASSERTE ICI, il est RAPPORTE. Sur une
        # pile fabriquee LUE PAR LE MARCHEUR, les positions sont arrondies au voxel, donc le profil
        # est un escalier et non un cosinus : les deux selecteurs y rendent 173,0. Le biais de
        # `105` est mesure sur des profils analytiques ET sur le vrai volume ; l'asserter ici
        # ferait dependre le controle d'un effet de quantification sans rapport avec ce qu'il nomme.
        out["ecart_des_selecteurs_sur_la_pile_droite_um"] = (
            round(droit["calibre"]["pas_lu_median_um"]
                  - droit["deux_roles"]["pas_lu_median_um"], 2)
            if droit["calibre"]["pas_lu_median_um"] is not None
            and droit["deux_roles"]["pas_lu_median_um"] is not None else None)
        out["pourquoi_le_biais_de_105_ne_sy_voit_pas"] = (
            "le marcheur lit des positions arrondies au voxel, donc un escalier et non un "
            "cosinus ; le biais de `105` est mesuré sur des profils analytiques et sur le vrai "
            "volume")
        # ⚠ Et le registre du corrige doit etre EXACT sur une pile droite : s'il derivait la,
        # un registre juste sur le vrai volume ne prouverait rien.
        out["le_registre_du_corrige_est_exact_sur_une_pile_droite"] = bool(
            droit["deux_roles"]["ecart_final"] is not None
            and abs(droit["deux_roles"]["ecart_final"]) < 0.25)
    return out


def _mediane(v) -> float | None:
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], dtype=np.float64)
    return round(float(np.median(v)), 2) if len(v) else None


def mesurer(cellules: int = CELLULES_PAR_BANDE, pas_max: int = PAS_MAX, demi: int = DEMI,
            graine: int = 613, bandes_max: int | None = None, fils: int = 32) -> dict:
    """Les deux marcheurs, depuis les MEMES departs, sur le vrai volume, etapes gardees."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from combien_de_pas_la_matiere_porte import marcher  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415
    from transformations_de_volume import (appliquer, appliquer_direction,  # noqa: PLC0415
                                           matrice)
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}
    if not M.ALIGNEMENT.is_file():
        return {"message": f"alignement des bandes absent : {M.ALIGNEMENT}"}
    al = {(x["de"], x["a"]): x for x in json.loads(M.ALIGNEMENT.read_text())["lignes"]}

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    barre_moities = nul_du_tenseur(demi=demi)["accord_des_moities_p1_deg"]
    barre_interstice = max(x["p99"] for x in C.accord_du_bruit_pur().values())

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = maintenant()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 1:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = N.centre_interpole(p0[:, 2], bords, cx, cy)
        rad_fin = appliquer_direction(m, N.direction_radiale(p0, c0))
        departs = appliquer(m, p0)
        detail = []
        for j in range(len(departs)):
            # ⭐⭐⭐ LE MEME DEPART ET LE MEME SENS INITIAL POUR LES DEUX. Ils divergent ensuite
            # parce que leurs pas les menent ailleurs : apparier les LECTURES est impossible pour
            # une marche, apparier les DEPARTS l'est, et c'est ce que `102` faisait deja.
            cel = {}
            for sel in SELECTEURS:
                e = marcher(vol, departs[j], rad_fin[j], longueurs, mu, sd, barre,
                            barre_moities, barre_interstice, C.VOXEL_FIN_UM, pas_max, demi,
                            interroge_la_matiere=True, fils=fils,
                            selecteur=sel, barre_du_selecteur=barre)
                # ⭐⭐⭐ LE REGISTRE DU TRAJET ENTIER, une lecture de plus par MARCHE (pas par
                # pas), donc quelques secondes : c'est la seule forme non tautologique.
                trajet = registre_du_trajet_entier(vol, departs[j], e, C.VOXEL_FIN_UM, fils)
                cel[sel] = {
                    "trajet_entier": trajet,
                    # ⭐⭐⭐ LES ETAPES SONT GARDEES, et c'est la seule raison d'etre de cette
                    # ligne : `102` les a jetees au profit d'une mediane, et sept heures de course
                    # sont irrecuperables.
                    "etapes": e,
                    "pas_confirmes": combien_de_pas_confirmes(e),
                    "registre": registre_continu(e),
                    "virage": virage_entre_pas(e),
                    "sortie": bool(e and e[-1].get("fin") == "sortie du volume"),
                    "au_plafond": bool(combien_de_pas_confirmes(e) >= pas_max)}
            detail.append(cel)
        if not detail:
            continue
        lignes.append({"de": x["de"], "a": x["a"],
                       "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
                       "cellules": len(detail), "detail": detail})
        avancement(len(lignes), len(bandes), "bandes", depart)

    if not lignes:
        return {"message": "aucune cellule lisible dans le volume fin"}
    return agreger({
        "fragment": C.OBJET, "volume_fin": C.VOLUME_FIN, "pas_nominal_um": C.PAS_UM,
        "pas_max": pas_max, "cellules_par_bande": cellules, "demi_cube_voxels": demi,
        "barre_du_balayage": round(float(barre), 3),
        "barre_de_linterstice": round(float(barre_interstice), 4),
        "barre_daccord_des_moities_deg": barre_moities,
        "secondes": round(maintenant() - depart, 1),
        "bandes": len(lignes), "lignes": lignes,
        "controle_fabrique": controle_fabrique(longueurs, mu, sd, barre, barre_moities,
                                               barre_interstice, pas_max, demi),
    })


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des etapes gardees — meme partage que `100` a `106`."""
    cel = [c for x in r["lignes"] for c in x["detail"]]
    # ⚠ Le prix est calcule DANS l'agregat et non dans la mesure, pour que `--reagreger` le
    # rafraichisse quand le cout mesure change — et il a change quatre fois.
    r["cout_par_etape"] = cout_par_etape_mesure()
    r["prix_projete"] = prix_de_la_course(
        len(r["lignes"]), r["cellules_par_bande"], r["pas_max"],
        secondes_par_etape=r["cout_par_etape"]["retenue_pour_les_projections_s"])
    r["resume"] = {"cellules": len(cel), "bandes": len(r["lignes"]),
                   "plafond_de_pas": r["pas_max"]}
    for sel in SELECTEURS:
        e_tous = [c[sel]["etapes"] for c in cel]
        conf = [c[sel]["pas_confirmes"] for c in cel]
        regs = [c[sel]["registre"] for c in cel]
        risques = risque_par_pas(e_tous)
        # ⚠⚠⚠ LA CENSURE EST NOMMEE AVANT LE RESULTAT QU'ELLE BORNE : une cellule au plafond dit
        # « AU MOINS ceci ». Publier la mediane sans elle ferait passer un budget de lecture pour
        # une limite de matiere — la butee de `99`.
        au_plafond = sum(1 for c in cel if c[sel]["au_plafond"])
        d = {
            "cellules_au_plafond": au_plafond,
            "part_censuree": round(au_plafond / max(len(cel), 1), 3),
            "la_portee_est_censuree": bool(au_plafond > 0),
            "pas_confirmes_median": round(float(np.median(conf)), 2) if conf else None,
            "pas_confirmes_max": int(max(conf)) if conf else 0,
            "cellules_qui_ont_porte": int(sum(1 for c in conf if c >= 1)),
            "sorties_du_volume": sum(1 for c in cel if c[sel]["sortie"]),
            "pas_lu_median_um": _mediane([s.get("pas_um") for e in e_tous for s in e]),
            "risque_par_pas": risques,
            "confirmation_marginale": confirmation_marginale(e_tous),
            "le_risque_baisse": le_risque_baisse(risques),
        }
        # ⭐⭐⭐ LE REGISTRE DU TRAJET ENTIER, ET C'EST LA SEULE FORME NON TAUTOLOGIQUE. Le pilote
        # a mesure que la fraction PAR PAS vaut 0,965 pour les DEUX selecteurs malgre des pas de
        # 255 et 225 µm : chacun choisit son pas pour qu'une periode y tienne. Le trajet complet,
        # lui, n'a jamais ete optimise.
        tr = [c[sel]["trajet_entier"] for c in cel
              if c[sel].get("trajet_entier", {}).get("decidable")
              and not c[sel]["trajet_entier"].get("en_butee")]
        # ⭐⭐⭐ LE VIRAGE ENTRE PAS CONSECUTIFS, ET IL CHIFFRE LE SEUL LEVIER DE COUT RESTANT.
        vir = [c[sel]["virage"] for c in cel if c[sel].get("virage", {}).get("decidable")]
        if vir:
            d["virage_median_deg"] = round(float(np.median(
                [x["virage_median_deg"] for x in vir])), 2)
            d["virage_p90_deg"] = round(float(np.median([x["virage_p90_deg"] for x in vir])), 2)
            # ⚠⚠ La comparaison est a la barre de l'accord des demi-blocs, la seule echelle
            # d'angle que ce depot ait calibree : sous elle, deux directions ne sont pas
            # distinguables par l'instrument qui les mesure.
            d["virage_sous_la_barre_des_moities"] = bool(
                d["virage_median_deg"] < r.get("barre_daccord_des_moities_deg", 8.88))
        d["cellules_a_trajet_lisible"] = len(tr)
        d["trajets_en_butee"] = sum(1 for c in cel
                                    if c[sel].get("trajet_entier", {}).get("en_butee"))
        # ⚠⚠⚠ LES MODES AVANT LA MEDIANE : une mediane sur une distribution bimodale choisit un
        # mode sans le dire. Elle reste publiee, mais APRES ce qui la rend lisible.
        d["modes_du_trajet"] = modes_du_trajet(tr, r["pas_max"])
        if tr:
            d.update({
                "feuilles_du_trajet_median": round(float(np.median(
                    [x["feuilles_franchies"] for x in tr])), 3),
                "pas_du_trajet_median": round(float(np.median(
                    [x["pas_parcourus"] for x in tr])), 1),
                "ecart_au_compte_de_pas_median": round(float(np.median(
                    [x["ecart_au_compte_de_pas"] for x in tr])), 3),
                "feuilles_par_pas_du_trajet": round(float(np.median(
                    [x["feuilles_par_pas"] for x in tr])), 3),
                "score_du_trajet_median": round(float(np.median([x["score"] for x in tr])), 3),
                # ⚠⚠ LA CONSEQUENCE ENCHAINEE, sinon « 0,96 feuille par pas » se lit comme un
                # petit ecart alors que cent vingt pas en font des spires entieres.
                "spires_du_trajet_apres_120_pas": round(SPIRES * float(np.median(
                    [x["feuilles_par_pas"] for x in tr])), 1),
            })
        # ⚠⚠⚠ LE REGISTRE PAR PAS EST GARDE ET DECLARE TAUTOLOGIQUE, pas jete : il faut qu'un
        # lecteur voie que les deux selecteurs y rendent le meme nombre, sinon « tautologique »
        # est une affirmation.
        finaux = [g[-1] for g in regs if g]
        if finaux:
            d.update({
                "cellules_a_registre": len(finaux),
                "derive_mediane_par_pas": round(float(np.median(
                    [g["ecart"] / max(g["pas"], 1) for g in finaux])), 4),
                "derive_mediane_finale": round(float(np.median([g["ecart"] for g in finaux])), 3),
                "feuilles_franchies_par_pas_median": round(float(np.median(
                    [g["cumul"] / max(g["pas"], 1) for g in finaux])), 3),
                # ⚠⚠ ET LA CONSEQUENCE ENCHAINEE, sinon « 1,07 feuille par pas » se lit comme un
                # petit ecart alors que cent vingt pas en font une erreur de spires entiere.
                "spires_apres_120_pas": round(SPIRES * float(np.median(
                    [g["cumul"] / max(g["pas"], 1) for g in finaux])), 1),
            })
        r[sel] = d
    ca, dr = r["calibre"], r["deux_roles"]
    # ⭐⭐⭐ LES DEUX VERDICTS DU FICHIER, CALCULES, ET CHACUN PEUT ECHOUER SEPAREMENT.
    if ca.get("pas_confirmes_median") is not None and dr.get("pas_confirmes_median") is not None:
        r["resume"]["pas_confirmes_calibre"] = ca["pas_confirmes_median"]
        r["resume"]["pas_confirmes_corrige"] = dr["pas_confirmes_median"]
        r["resume"]["gain_en_pas"] = round(
            dr["pas_confirmes_median"] - ca["pas_confirmes_median"], 2)
        r["resume"]["le_pas_corrige_porte_plus_loin"] = bool(
            dr["pas_confirmes_median"] > ca["pas_confirmes_median"])
    # ⚠⚠⚠ LE VERDICT SUR LE TRAJET PORTE SUR LES MODES, PAS SUR LEUR MEDIANE.
    md = dr.get("modes_du_trajet", {})
    if md.get("decidable"):
        r["resume"]["trajets_lisibles"] = md["trajets"]
        r["resume"]["part_des_trajets_au_compte_attendu"] = md["part_au_dessus"]
        r["resume"]["les_deux_modes_sont_peuples"] = md["les_deux_modes_sont_peuples"]
        if "mode_haut" in md:
            r["resume"]["feuilles_par_pas_du_mode_haut"] = md["mode_haut"][
                "feuilles_par_pas_median"]
        if "mode_bas" in md:
            r["resume"]["feuilles_par_pas_du_mode_bas"] = md["mode_bas"][
                "feuilles_par_pas_median"]
        for cle in ("le_score_est_plus_haut_pour_le_mode_sans_periodicite",
                    "un_seuil_de_score_ecarterait_le_BON_mode",
                    "ecart_des_scores_entre_modes"):
            if cle in md:
                r["resume"][cle] = md[cle]
    # ⭐⭐⭐ LE VERDICT SUR LE REGISTRE PORTE SUR LE TRAJET ENTIER, jamais sur la fraction par pas.
    if (dr.get("feuilles_par_pas_du_trajet") is not None
            and ca.get("feuilles_par_pas_du_trajet") is not None):
        r["resume"]["feuilles_par_pas_du_trajet_corrige"] = dr["feuilles_par_pas_du_trajet"]
        r["resume"]["feuilles_par_pas_du_trajet_calibre"] = ca["feuilles_par_pas_du_trajet"]
        r["resume"]["spires_du_trajet_corrige"] = dr["spires_du_trajet_apres_120_pas"]
        r["resume"]["spires_du_trajet_calibre"] = ca["spires_du_trajet_apres_120_pas"]
        r["resume"]["le_trajet_du_corrige_est_plus_juste"] = bool(
            abs(dr["feuilles_par_pas_du_trajet"] - 1.0)
            < abs(ca["feuilles_par_pas_du_trajet"] - 1.0))
    # ⚠⚠ ET LA TAUTOLOGIE DE LA FRACTION PAR PAS EST PUBLIEE COMME UN FAIT : si les deux
    # selecteurs y rendent le meme nombre, c'est que la quantite ne depend pas du selecteur.
    if (dr.get("feuilles_franchies_par_pas_median") is not None
            and ca.get("feuilles_franchies_par_pas_median") is not None):
        r["resume"]["la_fraction_par_pas_est_tautologique"] = bool(
            abs(dr["feuilles_franchies_par_pas_median"]
                - ca["feuilles_franchies_par_pas_median"]) < 0.02)
    if dr.get("feuilles_franchies_par_pas_median") is not None:
        r["resume"]["feuilles_par_pas_corrige"] = dr["feuilles_franchies_par_pas_median"]
        r["resume"]["spires_apres_120_pas_corrige"] = dr["spires_apres_120_pas"]
        if ca.get("feuilles_franchies_par_pas_median") is not None:
            r["resume"]["feuilles_par_pas_calibre"] = ca["feuilles_franchies_par_pas_median"]
            r["resume"]["spires_apres_120_pas_calibre"] = ca["spires_apres_120_pas"]
            # ⭐⭐ LE REGISTRE EST-IL PLUS PROCHE DE UN AVEC LE PAS CORRIGE ? C'est la question
            # que `104` posait et que seul un registre continu peut trancher.
            r["resume"]["le_registre_du_corrige_est_plus_juste"] = bool(
                abs(dr["feuilles_franchies_par_pas_median"] - 1.0)
                < abs(ca["feuilles_franchies_par_pas_median"] - 1.0))
    if dr.get("virage_median_deg") is not None:
        r["resume"]["virage_median_deg"] = dr["virage_median_deg"]
        r["resume"]["virage_p90_deg"] = dr["virage_p90_deg"]
        r["resume"]["virage_sous_la_barre_des_moities"] = dr["virage_sous_la_barre_des_moities"]
        # ⚠ Et la conséquence de coût est chiffrée à côté, sans être présentée comme un acquis :
        # relire un cube sur deux ne vaut que si la marche le supporte, ce qui reste à mesurer.
        r["resume"]["heures_si_un_cube_sur_deux"] = round(
            0.5 * prix_de_la_course(r["resume"]["bandes"], r["cellules_par_bande"],
                                    r["pas_max"])["heures"], 2)
    v = dr.get("le_risque_baisse", {})
    if v.get("decidable"):
        r["resume"]["le_risque_baisse"] = v["le_risque_baisse"]
        r["resume"]["risque_precoce"] = v["risque_precoce"]
        r["resume"]["risque_tardif"] = v["risque_tardif"]
        r["resume"]["survie_a_120_spires_au_risque_tardif"] = v[
            "part_des_cent_vingt_spires_qui_survit_au_risque_tardif"]
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    s = r["resume"]
    print(f"{r['fragment']} · {s['bandes']} bandes × {r['cellules_par_bande']} cellules × "
          f"{r['pas_max']} pas · DEUX sélecteurs depuis les MÊMES départs · "
          f"{s['cellules']} cellules")
    # ⚠⚠ LA CENSURE D'ABORD, avant le résultat qu'elle borne.
    for sel in SELECTEURS:
        d = r[sel]
        print(f"\n  ⚠ {sel} : {d['cellules_au_plafond']}/{s['cellules']} cellules AU PLAFOND "
              f"({d['part_censuree']:.1%}) — la portée est donc une BORNE INFÉRIEURE"
              if d["la_portee_est_censuree"] else
              f"\n  {sel} : aucune cellule au plafond")
    print("\n              pas confirmés  max  ont porté  sorties  pas lu µm  "
          "feuilles/pas  spires/120")
    for sel in SELECTEURS:
        d = r[sel]
        print(f"  {sel:>11}  {d['pas_confirmes_median']:13}  {d['pas_confirmes_max']:3d}  "
              f"{d['cellules_qui_ont_porte']:10d}  {d['sorties_du_volume']:7d}  "
              f"{d['pas_lu_median_um']:9}  "
              f"{d.get('feuilles_franchies_par_pas_median', float('nan')):12}  "
              f"{d.get('spires_apres_120_pas', float('nan')):10}")
    if "gain_en_pas" in s:
        print(f"\n★★★ LE PAS CORRIGÉ PORTE-T-IL PLUS LOIN ? "
              f"{'OUI' if s['le_pas_corrige_porte_plus_loin'] else 'NON'} — "
              f"{s['pas_confirmes_corrige']} contre {s['pas_confirmes_calibre']} pas "
              f"({s['gain_en_pas']:+.2f})")
    md = r["deux_roles"].get("modes_du_trajet", {})
    if md.get("decidable"):
        print(f"\n⚠⚠⚠ LES TRAJETS SE SÉPARENT EN DEUX POPULATIONS, et une médiane sur une "
              f"distribution")
        print(f"    bimodale choisit un mode sans le dire. Seuil : {md['seuil_feuilles']} feuilles "
              f"pour {md['pas_attendus']} pas attendus.")
        for nom, eti in (("mode_haut", "AU COMPTE ATTENDU"), ("mode_bas", "SANS PÉRIODICITÉ")):
            if nom in md:
                b = md[nom]
                print(f"    {eti:20s} : {b['trajets']:2d} trajets · "
                      f"{b['feuilles_median']} feuilles · {b['feuilles_par_pas_median']} par pas "
                      f"· score {b['score_median']}")
        print(f"    ★ {md['part_au_dessus']:.1%} des trajets franchissent au moins la moitié des "
              f"feuilles attendues")
        if "le_score_est_plus_haut_pour_le_mode_sans_periodicite" in md:
            print(f"    ⚠⚠⚠ le score est PLUS HAUT pour le mode SANS périodicité "
                  f"({md['ecart_des_scores_entre_modes']:+.3f}) :")
            print(f"        un seuil de score écarterait donc le BON mode. "
                  f"{md['un_seuil_de_score_ecarterait_le_BON_mode']}")
    if "le_trajet_du_corrige_est_plus_juste" in s:
        print(f"\n★★★ LE REGISTRE DU TRAJET ENTIER — la seule forme NON tautologique")
        print(f"    corrigé {s['feuilles_par_pas_du_trajet_corrige']} feuille par pas contre "
              f"{s['feuilles_par_pas_du_trajet_calibre']} pour le calibré,")
        print(f"    donc {s['spires_du_trajet_corrige']} spires pour cent vingt pas contre "
              f"{s['spires_du_trajet_calibre']}")
        print(f"    ★ le trajet du corrigé est plus juste : "
              f"{s['le_trajet_du_corrige_est_plus_juste']}")
    if s.get("la_fraction_par_pas_est_tautologique"):
        print(f"\n⚠⚠⚠ LA FRACTION PAR PAS EST TAUTOLOGIQUE, et c'est mesuré : les deux sélecteurs "
              f"y rendent")
        print(f"    le même nombre ({s.get('feuilles_par_pas_corrige')} contre "
              f"{s.get('feuilles_par_pas_calibre')}) malgré des pas différents, parce que chacun")
        print(f"    CHOISIT son pas pour qu'une période y tienne. C'est le trajet entier qui "
              f"mesure.")
    if "le_registre_du_corrige_est_plus_juste" in s:
        print(f"★★★ ET SON REGISTRE EST-IL PLUS JUSTE ? "
              f"{'OUI' if s['le_registre_du_corrige_est_plus_juste'] else 'NON'} — "
              f"{s['feuilles_par_pas_corrige']} feuille par pas contre "
              f"{s['feuilles_par_pas_calibre']},")
        print(f"    donc {s['spires_apres_120_pas_corrige']} spires pour cent vingt pas contre "
              f"{s['spires_apres_120_pas_calibre']}")
    v = r["deux_roles"].get("le_risque_baisse", {})
    if v.get("decidable"):
        print(f"\nLE RISQUE PAR PAS, SÉLECTEUR CORRIGÉ")
        print(f"  précoce (pas {v['pas_precoces']}) {v['risque_precoce']:.3f} sur "
              f"{v['en_risque_precoce']} en risque · tardif (pas {v['pas_tardifs']}) "
              f"{v['risque_tardif']:.3f} sur {v['en_risque_tardif']}")
        print(f"  rapport ×{v['rapport']}, p = {v['p_sous_risque_constant']} sous un risque "
              f"CONSTANT · ★ le risque baisse : {v['le_risque_baisse']}")
        print(f"  ⚠ enchaîné sur cent vingt spires : "
              f"{v['part_des_cent_vingt_spires_qui_survit_au_risque_precoce']:.6f} au risque "
              f"précoce, {v['part_des_cent_vingt_spires_qui_survit_au_risque_tardif']:.6f} au "
              f"tardif")
    elif v:
        print(f"\n⚠ le risque n'est pas décidable : {v.get('pourquoi')}")
    print("\n pas  en risque  tombées  risque   part confirmée (marginale)")
    marg = {x["pas"]: x for x in r["deux_roles"].get("confirmation_marginale", [])}
    for x in r["deux_roles"].get("risque_par_pas", []):
        mm = marg.get(x["pas"], {})
        print(f" {x['pas']:3d}  {x['en_risque']:9d}  {x['tombees']:7d}   {x['risque']:.3f}"
              f"    {mm.get('part', float('nan')):.3f}  ({mm.get('confirmes', 0)}"
              f"/{mm.get('marches', 0)})")
    c = r.get("controle_fabrique", {})
    for e in c.get("empilements", []):
        print(f"\nEMPILEMENT FABRIQUÉ à {e['obliquite_deg']:.0f}° :")
        for sel in SELECTEURS:
            d = e[sel]
            print(f"   {sel:>11} — {d['pas_confirmes']} pas confirmés, pas lu "
                  f"{d['pas_lu_median_um']} µm, registre {d['registre_final']} "
                  f"(écart {d['ecart_final']}) sur {d['pas_du_registre']} pas")
    for cle, nom in (("le_corrige_lit_le_pas_vrai_sur_une_pile_droite",
                      "le corrigé lit le pas VRAI sur une pile droite"),
                     ("le_calibre_lit_plus_haut_sur_la_meme_pile",
                      "le calibré lit plus haut sur la même pile"),
                     ("le_registre_du_corrige_est_exact_sur_une_pile_droite",
                      "le registre du corrigé est exact sur une pile droite")):
        if cle in c:
            print(f"   ★ {nom} : {c[cle]}")


def _etapes(interstices, confirmes=None, fractions=None, sortie_apres=None) -> list[dict]:
    """Une marche FABRIQUEE : compte d'interstices, confirmation, fraction continue.

    ⚠ Elle vit dans le module et non dans la batterie parce que plusieurs controles la partagent,
    et deux definitions d'une meme fixture derivent.
    """
    if confirmes is None:
        confirmes = [n == 1 for n in interstices]
    if fractions is None:
        fractions = [float(n) for n in interstices]
    out = []
    for k, (n, c, fr) in enumerate(zip(interstices, confirmes, fractions), start=1):
        if sortie_apres is not None and k > sortie_apres:
            out.append({"pas": k, "fin": "sortie du volume"})
            break
        out.append({"pas": k, "interstices_traverses": int(n), "confirme": bool(c),
                    "feuilles_franchies": (None if fr is None else float(fr)),
                    "fraction_en_butee": False, "pas_um": 173.0,
                    "avance_um": 173.0, "direction": [0.0, 0.0, 1.0]})
    return out


def verifier() -> int:
    # ⚠ Les imports sont en tete de la batterie et non au milieu : mon premier jet utilisait `C`
    # dans un bloc place AVANT son import, ce qui rendait une UnboundLocalError plutot qu'un echec
    # de controle — une batterie qui plante n'est pas une batterie qui echoue.
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    from la_direction_que_la_matiere_montre import nul_du_tenseur  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LE REGISTRE CONTINU ================================================================
    reg = registre_continu(_etapes([1] * 5))
    v("une marche en règle a un écart nul à chaque pas",
      [x["ecart"] for x in reg] == [0.0] * 5, str([x["ecart"] for x in reg]))
    # ⭐⭐⭐ CE QUE LE COMPTEUR ENTIER NE POUVAIT PAS VOIR : un retard FRACTIONNAIRE. `104` a mesuré
    # que la famille {1, 2, 3} ne descend jamais sous un, donc un pas à 0,82 feuille passait pour
    # un pas entier. Le registre continu l'accumule.
    reg = registre_continu(_etapes([1] * 5, fractions=[0.82] * 5))
    v("un retard fractionnaire s'accumule, là où le compteur entier ne le voyait pas",
      abs(reg[-1]["ecart"] + 0.9) < 0.01, f"écart final {reg[-1]['ecart']}")
    v("... et le cumul dit sur quelle spire le marcheur se trouve",
      abs(reg[-1]["cumul"] - 4.1) < 0.01, f"cumul {reg[-1]['cumul']}")
    # ⚠⚠ UNE FRACTION EN BUTEE OU ABSENTE INTERROMPT LE CUMUL : prolonger un registre à travers une
    # valeur inconnue en ferait une invention.
    e = _etapes([1] * 5)
    e[2]["fraction_en_butee"] = True
    v("une fraction en butée interrompt le registre au lieu de l'inventer",
      len(registre_continu(e)) == 2, f"{len(registre_continu(e))} pas comptés")
    e = _etapes([1] * 5, fractions=[1.0, 1.0, None, 1.0, 1.0])
    v("... et une fraction absente aussi",
      len(registre_continu(e)) == 2, f"{len(registre_continu(e))} pas comptés")
    v("le registre s'arrête à la sortie du volume",
      len(registre_continu(_etapes([1] * 4, sortie_apres=2))) == 2)

    # === LE RISQUE CONDITIONNEL CONTRE LA CONFIRMATION MARGINALE =============================
    # ⭐⭐ LES DEUX DOIVENT DIFFERER SUR LA MEME ENTREE, sinon l'une des deux ne sert à rien.
    jeu = [_etapes([1, 1, 1], [False, False, True]), _etapes([1, 1, 1], [True, True, True])]
    rc, cm = risque_par_pas(jeu), confirmation_marginale(jeu)
    v("une marche tombée au pas 1 quitte le dénominateur du risque au pas 2",
      rc[1]["en_risque"] == 1, f"{rc[1]['en_risque']} en risque")
    v("... mais elle reste dans la confirmation MARGINALE du pas 2",
      cm[1]["marches"] == 2, f"{cm[1]['marches']} marches")
    v("... donc les deux courbes diffèrent sur la même entrée",
      abs(rc[1]["risque"] - (1.0 - cm[1]["part"])) > 1e-9,
      f"risque {rc[1]['risque']} contre 1 − marginale {1.0 - cm[1]['part']:.3f}")
    jeu = [_etapes([1, 1, 1], sortie_apres=1), _etapes([1, 1, 1])]
    v("une marche sortie au pas 2 est censurée, pas comptée comme une chute",
      risque_par_pas(jeu)[1]["en_risque"] == 1 and risque_par_pas(jeu)[1]["tombees"] == 0)

    # === LE NUL D'UN RISQUE CONSTANT ========================================================
    v("le test exact rend la valeur connue du tableau de Fisher",
      abs(_fisher(3, 1, 1, 3) - 0.4857) < 5e-4, f"{_fisher(3, 1, 1, 3):.4f}")
    plat = [{"pas": k, "en_risque": 200, "tombees": 60, "risque": 0.3} for k in range(1, 9)]
    # ⭐⭐⭐ LA GARDE DOIT POUVOIR DIRE NON : un risque CONSTANT sur de gros effectifs ne doit pas
    # être annoncé comme une baisse, sinon le verdict est un oui déguisé.
    v("un risque constant sur de gros effectifs n'est PAS annoncé comme une baisse",
      le_risque_baisse(plat)["le_risque_baisse"] is False,
      f"p = {le_risque_baisse(plat)['p_sous_risque_constant']}")
    baisse = ([{"pas": k, "en_risque": 200, "tombees": 80, "risque": 0.4} for k in (1, 2, 3)]
              + [{"pas": k, "en_risque": 200, "tombees": 20, "risque": 0.1}
                 for k in range(4, 9)])
    d = le_risque_baisse(baisse)
    v("un risque qui baisse vraiment est détecté",
      d["le_risque_baisse"] is True and d["rapport"] == 4.0, f"×{d['rapport']}")
    maigre = [{"pas": 1, "en_risque": 40, "tombees": 20, "risque": 0.5},
              {"pas": 2, "en_risque": 2, "tombees": 0, "risque": 0.0}]
    v("... et il rend « indécidable » plutôt qu'un verdict sur un tiers vide",
      le_risque_baisse(maigre)["decidable"] is False)
    v("la conséquence sur cent vingt spires est publiée à côté du risque",
      d["part_des_cent_vingt_spires_qui_survit_au_risque_tardif"] == round(0.9 ** 120, 6))

    # === L'AGREGATION, ET SES DEUX VERDICTS =================================================
    def cell(conf_cal, conf_dr, fr_cal=1.18, fr_dr=1.02, pas_max=4):
        d = {}
        for sel, cf, fr in (("calibre", conf_cal, fr_cal), ("deux_roles", conf_dr, fr_dr)):
            e = _etapes([1] * pas_max, [True] * cf + [False] * (pas_max - cf),
                        fractions=[fr] * pas_max)
            d[sel] = {"etapes": e, "pas_confirmes": cf, "registre": registre_continu(e),
                      "sortie": False, "au_plafond": cf >= pas_max}
        return d
    faux = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 5.0, "cellules": 3,
                        "detail": [cell(1, 3), cell(2, 3), cell(1, 4)]}],
            "pas_max": 4, "cellules_par_bande": 3, "fragment": "X", "pas_nominal_um": 173.0}
    g = agreger(faux)["resume"]
    v("le verdict sur la portée est rendu, quel qu'il soit",
      "le_pas_corrige_porte_plus_loin" in g and "gain_en_pas" in g)
    v("... et il dit OUI quand le corrigé porte plus loin",
      g["le_pas_corrige_porte_plus_loin"] is True, f"{g['gain_en_pas']:+.2f} pas")
    # ⭐⭐⭐ ET IL DOIT POUVOIR DIRE NON, sinon ce n'est pas une mesure mais une annonce.
    faux["lignes"][0]["detail"] = [cell(3, 1), cell(3, 2), cell(4, 1)]
    v("... et NON quand il porte moins loin",
      agreger(faux)["resume"]["le_pas_corrige_porte_plus_loin"] is False)
    # ⭐⭐ LE SECOND VERDICT : le registre du corrigé est-il PLUS PROCHE de un ?
    faux["lignes"][0]["detail"] = [cell(2, 3), cell(2, 3)]
    g = agreger(faux)["resume"]
    v("le registre du corrigé est plus juste quand il l'est",
      g["le_registre_du_corrige_est_plus_juste"] is True,
      f"{g['feuilles_par_pas_corrige']} contre {g['feuilles_par_pas_calibre']}")
    faux["lignes"][0]["detail"] = [cell(2, 3, fr_cal=1.02, fr_dr=1.18)]
    v("... et il ne l'est pas quand il ne l'est pas",
      agreger(faux)["resume"]["le_registre_du_corrige_est_plus_juste"] is False)
    # ⚠⚠⚠ LA CENSURE EST NOMMEE AVANT LE RESULTAT QU'ELLE BORNE.
    faux["lignes"][0]["detail"] = [cell(4, 4), cell(2, 3)]
    g = agreger(faux)
    v("la censure est comptée et déclarée",
      g["deux_roles"]["cellules_au_plafond"] == 1
      and g["deux_roles"]["la_portee_est_censuree"] is True,
      f"part {g['deux_roles']['part_censuree']}")
    # ⚠ Et la conséquence enchaînée voyage avec le registre, sinon « 1,02 feuille par pas » se lit
    # comme un petit écart alors que cent vingt pas en font des spires entières.
    v("la conséquence sur cent vingt pas voyage avec le registre",
      abs(g["resume"]["spires_apres_120_pas_corrige"] - 120 * 1.02) < 0.2,
      f"{g['resume']['spires_apres_120_pas_corrige']} spires")
    v("l'affichage tourne sur ce résultat", afficher(g) is None)

    # === LE COUT A ETE MESURE QUATRE FOIS, ET LA DISPERSION EST LE RESULTAT ==================
    ce = cout_par_etape_mesure()
    v("les quatre mesures du coût par étape sont publiées avec leur condition",
      len(ce["mesures"]) == 4
      and all("condition" in x and "mesure" in x for x in ce["mesures"]),
      f"{[x['secondes'] for x in ce['mesures']]}")
    # ⚠⚠⚠ LA MESURE SOUS CONTENTION EST EXCLUE DES PROJECTIONS, et c'est la règle qui compte : un
    # coût mesuré pendant qu'une autre batterie lit le même volume n'est pas un coût.
    v("... et celle prise sous contention est exclue des projections",
      ce["retenue_pour_les_projections_s"] < 58.5
      and ce["retenue_pour_les_projections_s"] == 55.0,
      f"{ce['retenue_pour_les_projections_s']} s retenues")
    # ⚠⚠ ET C'EST LA PLUS GRANDE DES FIABLES QUI SERT, pas la moyenne : sous-estimer fait lancer
    # une course qu'on ne peut pas finir, ce qui est l'erreur qui coûte ici.
    v("... la plus GRANDE des fiables servant, parce que sous-estimer coûte plus que surestimer",
      ce["retenue_pour_les_projections_s"] > ce["la_plus_basse_fiable_s"],
      f"{ce['retenue_pour_les_projections_s']} contre {ce['la_plus_basse_fiable_s']}")
    v("... et le rapport entre les extrêmes fiables est publié",
      ce["rapport_entre_les_extremes"] > 1.0, f"×{ce['rapport_entre_les_extremes']}")

    # === UNE MEDIANE SUR UNE DISTRIBUTION BIMODALE N'EST PAS UN RESUME ======================
    # ⚠⚠⚠ C'EST L'ERREUR QUE J'AI COMMISE EN LISANT LA PREMIERE SORTIE : les trajets rendent soit
    # ~6 feuilles pour 6 pas soit ~1, et leur mediane tombe dans le mode BAS par accident de
    # comptage. Elle se lit alors « le marcheur ne franchit presque rien » alors que quatre marches
    # sur dix franchissent exactement ce qu'elles doivent.
    def tj(f, sc=0.4):
        return {"feuilles_franchies": f, "feuilles_par_pas": f / 6.0, "score": sc,
                "pas_parcourus": 6}
    deux_modes = [tj(x) for x in (0.5, 0.7, 0.8, 1.0, 1.2, 1.4)] + \
                 [tj(x) for x in (5.8, 6.0, 6.2, 6.5, 7.0)]
    md = modes_du_trajet(deux_modes, 6)
    v("deux populations sont rendues séparément, avec leur effectif",
      md["au_dessus"] == 5 and md["au_dessous"] == 6,
      f"{md['au_dessus']} au-dessus, {md['au_dessous']} au-dessous")
    v("... et leur médiane commune tomberait dans le MAUVAIS mode",
      abs(float(np.median([x["feuilles_franchies"] for x in deux_modes]))
          - md["mode_bas"]["feuilles_median"]) < 1.0,
      f"médiane commune {float(np.median([x['feuilles_franchies'] for x in deux_modes])):.2f} "
      f"contre {md['mode_haut']['feuilles_median']} pour le bon mode")
    # ⚠ Le seuil est DERIVE — la moitie du compte attendu — et non regle : un trajet qui a franchi
    # moins de la moitie des feuilles qu'il devait ne mesure pas des feuilles.
    v("le seuil est la moitié du compte attendu, pas un réglage",
      md["seuil_feuilles"] == 3.0 and modes_du_trajet(deux_modes, 10)["seuil_feuilles"] == 5.0)
    # ⭐ Et « bimodal » n'est pas revendique sur trois marches d'un cote.
    v("un mode à trois trajets n'est pas déclaré peuplé",
      modes_du_trajet([tj(0.5)] * 3 + [tj(6.0)] * 9, 6)["les_deux_modes_sont_peuples"] is False)
    v("... alors que deux modes à cinq le sont",
      md["les_deux_modes_sont_peuples"] is True)
    # ⭐⭐⭐ ET LE SENS DE L'ECART DE SCORE EST PUBLIE : s'il est plus haut pour le mode SANS
    # periodicite, un seuil de score ecarterait le BON mode. C'est mesure sur le vrai volume.
    envers = [tj(x, 0.48) for x in (0.5, 0.7, 0.8, 1.0, 1.2)] + \
             [tj(x, 0.37) for x in (5.8, 6.0, 6.2, 6.5, 7.0)]
    me = modes_du_trajet(envers, 6)
    v("quand le score est plus haut pour le mode sans périodicité, on le DIT",
      me["le_score_est_plus_haut_pour_le_mode_sans_periodicite"] is True
      and me["un_seuil_de_score_ecarterait_le_BON_mode"] is True,
      f"écart {me['ecart_des_scores_entre_modes']:+.3f}")
    endroit = [tj(x, 0.30) for x in (0.5, 0.7, 0.8, 1.0, 1.2)] + \
              [tj(x, 0.60) for x in (5.8, 6.0, 6.2, 6.5, 7.0)]
    v("... et l'inverse quand il l'est dans le bon sens",
      modes_du_trajet(endroit, 6)[
          "le_score_est_plus_haut_pour_le_mode_sans_periodicite"] is False)

    # === LE VIRAGE ENTRE PAS CONSECUTIFS, QUI CHIFFRE LE SEUL LEVIER DE COUT =================
    # ⭐⭐⭐ Le cube de direction fait 91 % du prix d'un pas, et `103` a refute de le lire moins
    # cher. Le seul levier restant est de le lire MOINS SOUVENT, et le chiffre qui dit si cela vaut
    # la peine d'etre mesure est le virage entre deux pas consecutifs — lisible GRATUITEMENT dans
    # les etapes que cette tranche garde.
    droite = _etapes([1] * 4)
    vv = virage_entre_pas(droite)
    v("une marche en ligne droite ne vire pas",
      vv["decidable"] and vv["virage_median_deg"] < 1e-6, f"{vv.get('virage_median_deg')}°")
    # ⭐ Un virage de dix degres par pas doit ressortir a dix degres, pas a autre chose.
    tourne = _etapes([1] * 4)
    for i, x in enumerate(tourne):
        a = np.deg2rad(10.0 * i)
        x["direction"] = [0.0, float(np.sin(a)), float(np.cos(a))]
    vv = virage_entre_pas(tourne)
    v("... et un virage de dix degrés par pas ressort à dix degrés",
      abs(vv["virage_median_deg"] - 10.0) < 0.01, f"{vv['virage_median_deg']}°")
    # ⚠⚠⚠ LE SIGNE D'UNE DIRECTION EST ARBITRAIRE — un vecteur propre n'a pas de sens, et `106` a
    # paye cet oubli. Retourner un pas sur deux ne doit RIEN changer au virage.
    retourne = _etapes([1] * 4)
    for i, x in enumerate(retourne):
        a = np.deg2rad(10.0 * i)
        d = np.array([0.0, float(np.sin(a)), float(np.cos(a))]) * (-1.0 if i % 2 else 1.0)
        x["direction"] = [float(q) for q in d]
    v("... et retourner une direction sur deux n'y change rien",
      abs(virage_entre_pas(retourne)["virage_median_deg"] - 10.0) < 0.01,
      f"{virage_entre_pas(retourne)['virage_median_deg']}°")
    v("moins de deux pas rend « indécidable » plutôt qu'un virage",
      virage_entre_pas(_etapes([1]))["decidable"] is False)

    # === LE PRIX EST CHIFFRE DEPUIS UNE MESURE, PAS DEPUIS UN MODELE =========================
    # ⚠⚠⚠ MA PREMIERE PROJECTION ETAIT FAUSSE D'UN FACTEUR 2,5 : `104` chiffrait 22,92 s par etape
    # en additionnant un cube et deux planchers, le pilote en mesure 58,5. Le controle asserte que
    # le prix est DERIVE du chiffre mesure, et que l'allocation retenue tient sous six heures.
    p = prix_de_la_course(28, CELLULES_PAR_BANDE, PAS_MAX)
    v("le prix de la course est dérivé du coût MESURÉ par le pilote",
      p["etapes"] == 28 * CELLULES_PAR_BANDE * PAS_MAX * 2
      and p["heures"] == round(p["etapes"] * SECONDES_PAR_ETAPE_MESUREES / 3600.0, 2),
      f"{p['etapes']} étapes, {p['heures']} h à {SECONDES_PAR_ETAPE_MESUREES} s")
    v("... et l'allocation retenue tient sous six heures",
      p["heures"] < 6.0, f"{p['heures']} h")
    # ⭐ Et l'allocation que j'avais d'abord ecrite aurait coute plus du double : le dire evite de
    # croire que le plafond de six pas est un choix de confort.
    v("... là où l'allocation que j'avais d'abord écrite en coûtait plus du double",
      prix_de_la_course(28, 2, 8)["heures"] > 2.0 * p["heures"],
      f"{prix_de_la_course(28, 2, 8)['heures']} h contre {p['heures']}")
    # ⚠⚠⚠ ET LE CHIFFRE RETENU EST CELUI MESURE SEUL, PAS SOUS CONTENTION : un premier pilote
    # rendait 58,5 s en tournant a cote d'une autre batterie. Un cout mesure sous contention n'est
    # pas un cout, et le controle fige la valeur pour qu'un retour a l'ancienne se voie.
    v("le coût par étape retenu est celui mesuré SEUL",
      abs(SECONDES_PAR_ETAPE_MESUREES - 38.0) < 1e-9,
      f"{SECONDES_PAR_ETAPE_MESUREES} s, contre 58,5 mesurées sous contention")

    # === LE REGISTRE DU TRAJET ENTIER, LA SEULE FORME NON TAUTOLOGIQUE ======================
    # ⚠⚠⚠ LE PILOTE A MESURE QUE LA FRACTION PAR PAS EST TAUTOLOGIQUE : les deux selecteurs y
    # rendent 0,965 malgre des pas de 255 et 225 µm, parce que chacun choisit son pas pour qu'une
    # periode y tienne. Le trajet ENTIER n'a jamais ete optimise, donc lui seul mesure.
    from combien_de_pas_la_matiere_porte import VolumeFabrique  # noqa: PLC0415

    vf = VolumeFabrique(C.PAS_UM, obliquite_deg=0.0)
    dep = np.array([2000.0, 2000.0, 2000.0])
    proj = float(dep @ vf.normale) * C.VOXEL_FIN_UM
    dep = dep + vf.normale * ((round(proj / C.PAS_UM) * C.PAS_UM - proj) / C.VOXEL_FIN_UM)
    # ⭐ Six pas d'exactement un pas de feuille : le trajet doit compter SIX feuilles.
    juste = _etapes([1] * 6)
    t = registre_du_trajet_entier(vf, dep, juste, C.VOXEL_FIN_UM)
    v("un trajet de six pas justes compte six feuilles",
      t["decidable"] and abs(t["feuilles_franchies"] - 6.0) < 0.3,
      f"{t.get('feuilles_franchies')} pour 6 · score {t.get('score')}")
    v("... et son écart au compte de pas est nul",
      abs(t["ecart_au_compte_de_pas"]) < 0.3, f"{t['ecart_au_compte_de_pas']}")
    # ⭐⭐⭐ ET C'EST LE CONTROLE QUI COMPTE : des pas TROP LONGS doivent compter PLUS de feuilles
    # que de pas. Si le trajet ne le voyait pas, il serait tautologique lui aussi.
    trop = _etapes([1] * 6)
    for x in trop:
        x["avance_um"] = 173.0 * 1.2
    t2 = registre_du_trajet_entier(vf, dep, trop, C.VOXEL_FIN_UM)
    v("des pas 20 % trop longs comptent PLUS de feuilles que de pas",
      t2["decidable"] and t2["feuilles_par_pas"] > 1.1,
      f"{t2.get('feuilles_par_pas')} feuille par pas pour 1,2 injecté")
    # ⚠ Et des pas trop COURTS doivent en compter MOINS : le registre voit les deux sens, ce que
    # le compteur entier de `98` ne pouvait pas faire.
    court = _etapes([1] * 6)
    for x in court:
        x["avance_um"] = 173.0 * 0.8
    t3 = registre_du_trajet_entier(vf, dep, court, C.VOXEL_FIN_UM)
    v("... et des pas 20 % trop courts en comptent MOINS",
      t3["decidable"] and t3["feuilles_par_pas"] < 0.9,
      f"{t3.get('feuilles_par_pas')} feuille par pas pour 0,8 injecté")
    # ⚠⚠ MOINS DE DEUX PAS : on avoue plutot que de rendre un compte sur un seul pas, qui serait
    # exactement la tautologie qu'on vient d'ecarter.
    v("moins de deux pas rend « indécidable » plutôt qu'un compte tautologique",
      registre_du_trajet_entier(vf, dep, _etapes([1]), C.VOXEL_FIN_UM)["decidable"] is False)

    # === LE CONTROLE FABRIQUE, SUR LE VRAI MARCHEUR ==========================================
    L = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(L)
    barre = max(x["p99"] for x in M.nul_du_balayage_calibre(L, mu, sd).values())
    barre_moities = nul_du_tenseur(demi=DEMI)["accord_des_moities_p1_deg"]
    barre_int = max(x["p99"] for x in C.accord_du_bruit_pur().values())
    cf = controle_fabrique(L, mu, sd, barre, barre_moities, barre_int, pas_max=4, demi=DEMI)
    droit = next(x for x in cf["empilements"] if x["obliquite_deg"] == 0.0)
    # ⭐⭐⭐ SANS CE CONTROLE, LA SUPERIORITE DU PAS CORRIGE SUR LE VRAI VOLUME NE VOUDRAIT RIEN :
    # sur une pile DROITE de pas 173,0 µm il doit lire 173, et le calibré un cran de plus.
    v("le sélecteur corrigé lit le pas VRAI sur une pile fabriquée droite",
      cf["le_corrige_lit_le_pas_vrai_sur_une_pile_droite"] is True,
      f"{droit['deux_roles']['pas_lu_median_um']} µm pour {C.PAS_UM}")
    # ⚠⚠⚠ « LE CALIBRE LIT PLUS HAUT » N'EST PAS ASSERTE ICI, IL EST RAPPORTE, et c'est une
    # correction : sur une pile fabriquee LUE PAR LE MARCHEUR les positions sont arrondies au
    # voxel, donc le profil est un escalier et les deux selecteurs y rendent 173,0. Asserter le
    # biais de `105` ici ferait dependre le controle d'un effet de quantification sans rapport
    # avec ce qu'il nomme. Ce qui est asserte est que l'ECART est PUBLIE avec sa raison.
    v("... et l'écart entre les deux sélecteurs est RAPPORTÉ, avec la raison de son absence ici",
      "ecart_des_selecteurs_sur_la_pile_droite_um" in cf
      and "pourquoi_le_biais_de_105_ne_sy_voit_pas" in cf,
      f"écart {cf.get('ecart_des_selecteurs_sur_la_pile_droite_um')} µm")
    # ⭐⭐ ET LE REGISTRE DU CORRIGE DOIT ETRE EXACT LA : s'il dérivait sur du connu, un registre
    # juste sur le vrai volume ne prouverait rien.
    v("le registre du corrigé est exact sur une pile fabriquée droite",
      cf["le_registre_du_corrige_est_exact_sur_une_pile_droite"] is True,
      f"écart final {droit['deux_roles']['ecart_final']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--pas", type=int, default=PAS_MAX)
    p.add_argument("--demi", type=int, default=DEMI)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--fils", type=int, default=32)
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = agreger(json.loads(a.json.read_text()))
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, pas_max=a.pas, demi=a.demi,
                bandes_max=a.bandes, fils=a.fils)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
