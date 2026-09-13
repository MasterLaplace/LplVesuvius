#!/usr/bin/env python3
"""Le compte de feuilles suit-il le compte de pas ? — la derive, lue sur les PREFIXES du trajet.

⚠⚠⚠ POURQUOI CE FICHIER, ET `109` L'A NOMME. Tant qu'un pas non confirme passait pour une chute,
la question etait « combien de pas la matiere porte ». `109` a mesure que les manques ne sont pas
groupes, donc qu'un manque n'arrete pas la marche : la question devient **de combien le compte
DERIVE quand la marche est longue**. C'est celle que `104` posait deja sous sa forme decisive —
*un retard est-il un BIAIS, qui coute `n`, ou un JITTER de moyenne nulle, qui coute `√n` ?*

⭐⭐⭐ ET ELLE SE MESURE SANS REMARCHER. `107` a garde les etapes de chaque marche : avance et
direction, pas par pas. La polyligne est donc entierement reconstructible, et le registre peut etre
recalcule sur chacun de ses PREFIXES — deux pas, trois pas, jusqu'a six. Une lecture par marche
suffit, la ou refaire les marches en couterait des heures.

⚠⚠ LE DEPART, LUI, N'A PAS ETE GARDE, ET C'EST LA LECON DE `102` QUI SE REJOUE. `107` conserve les
etapes mais pas leur ancre, donc la polyligne n'existe qu'a une translation pres. Il est
RE-DERIVABLE parce que l'echantillonnage des cellules est deterministe (graine 613 plus l'indice de
bande), et cette tranche l'ecrit dans SA mesure pour qu'il ne se reperde pas.

⭐⭐⭐ ET LA RE-DERIVATION SE VERIFIE GRATUITEMENT, SUR CHAQUE MARCHE. Le prefixe COMPLET est le
trajet entier que `107` a publie : s'il ne reproduit pas le meme nombre de feuilles, c'est que le
depart re-derive n'est pas celui de la course, et la tranche le dit au lieu de publier. Chaque
marche porte donc sa propre verification.

⚠⚠ CE QUE CETTE TRANCHE NE PEUT PAS DIRE. Six pas ne sont pas cent vingt, et un prefixe court est
lu par un estimateur dont `98` a mesure qu'il ne garde rien sous sa fenetre. Le controle fabrique
est donc obligatoire : si le registre des prefixes ne retrouve pas un compte CONNU a chaque
longueur, aucune courbe mesuree sur la matiere ne veut dire quoi que ce soit.

Usage :
    uv run python src/nappe/le_compte_suit_il_le_pas.py --verifier
    uv run python src/nappe/le_compte_suit_il_le_pas.py \\
        --json docs/mesures/le_compte_suit_il_le_pas.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

CHEMIN_DE_107 = RACINE / "docs" / "mesures" / "le_marcheur_avec_le_bon_pas.json"

# ⚠⚠ LA GRAINE ET LE NOMBRE DE CELLULES SONT CEUX DE `107`, PAS DES REGLAGES. Les changer
# re-derive d'autres departs que ceux de la course, donc un trajet qui n'a jamais ete marche.
GRAINE_DE_107 = 613
CELLULES_DE_107 = 1
SELECTEURS = ("calibre", "deux_roles")
PREFIXE_MIN = 2
# ⚠ La tolerance de la verification est en FEUILLES, au cran auquel `107` publie (trois
# decimales) : plus serre elle attraperait l'arrondi du fichier, plus lache elle laisserait passer
# un depart voisin.
TOLERANCE_DE_LA_VERIFICATION = 0.01


def registre_des_prefixes(v: np.ndarray, pas: int, echantillons: int) -> list[dict]:
    """Le registre du trajet, recalcule sur chacun de ses prefixes de `PREFIXE_MIN` a `pas`.

    ⭐⭐⭐ C'EST LA COURBE DE DERIVE, ET ELLE NE COUTE QU'UNE LECTURE. Les echantillons d'un prefixe
    sont un SOUS-ENSEMBLE de ceux du trajet complet, donc lire la polyligne une fois les donne
    tous. Ce qui se lit ensuite est si le compte de feuilles suit le compte de pas.

    ⚠⚠ LA FENETRE DE FREQUENCE SUIT LE PREFIXE (`k + 4`), exactement comme `107` le fait pour le
    trajet entier. Garder la fenetre du trajet complet ferait chercher huit periodes dans deux pas,
    donc rendrait une butee lue comme une mesure.

    ⚠ Un prefixe de moins de deux pas n'est pas calcule : une seule periode ne distingue pas une
    periodicite d'une derive, et `98` a mesure que sous sa fenetre l'estimateur ne garde rien.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    out = []
    for k in range(PREFIXE_MIN, pas + 1):
        n = k * echantillons + 1
        if n > v.size:
            break
        frac, sc, butee = C.feuilles_franchies(v[:n].reshape(1, -1),
                                               f_min=0.35, f_max=float(k) + 4.0)
        if not np.isfinite(frac[0]):
            out.append({"pas": k, "decidable": False, "pourquoi": "profil plat"})
            continue
        out.append({"pas": k, "decidable": True, "echantillons": int(n),
                    "feuilles": round(float(frac[0]), 3),
                    "score": round(float(sc[0]), 3),
                    "en_butee": bool(butee[0]),
                    "feuilles_par_pas": round(float(frac[0]) / k, 3),
                    "ecart_au_compte_de_pas": round(float(frac[0]) - k, 3)})
    return out


def le_prefixe_complet_reproduit_107(prefixes: list[dict], publie: float,
                                     tolerance: float = TOLERANCE_DE_LA_VERIFICATION) -> dict:
    """Le prefixe le plus long doit rendre le nombre que `107` a publie pour ce trajet.

    ⭐⭐⭐ C'EST LA VERIFICATION DE LA RE-DERIVATION, ET CHAQUE MARCHE PORTE LA SIENNE. Le depart
    n'ayant pas ete garde, tout ce qui suit repose sur le fait qu'il a ete retrouve ; si le prefixe
    complet rend un autre nombre, c'est qu'on lit une polyligne qui n'a jamais ete marchee. Une
    tranche qui publierait sans ce controle mesurerait un trajet imaginaire avec assurance.
    """
    derniers = [x for x in prefixes if x.get("decidable")]
    if not derniers or publie is None:
        return {"decidable": False, "pourquoi": "aucun prefixe lisible ou rien de publie"}
    d = derniers[-1]
    return {"decidable": True, "pas": d["pas"],
            "lu": d["feuilles"], "publie": round(float(publie), 3),
            "ecart": round(d["feuilles"] - float(publie), 3),
            "reproduit": bool(abs(d["feuilles"] - float(publie)) <= tolerance)}


def biais_ou_jitter(courbes: list[list[dict]]) -> dict:
    """L'ecart au compte de pas grandit-il comme `n` (BIAIS) ou comme `√n` (JITTER) ?

    ⭐⭐⭐ C'EST LA QUESTION QUI DECIDE DU GRAAL, ET `104` L'AVAIT POSEE SANS POUVOIR Y REPONDRE. Un
    biais coute `n` : cent vingt pas a un pour cent de trop font douze spires d'erreur, et rien ne
    les signale. Un jitter de moyenne nulle coute `√n` : la meme erreur par pas ne fait plus qu'une
    spire sur cent vingt. Ce ne sont pas deux degres du meme probleme, ce sont deux mondes.

    ⚠⚠ ELLE SE LIT SUR L'ENSEMBLE DES MARCHES, PAS SUR UNE SEULE. Sur une marche, cinq points ne
    separent pas `n` de `√n`. Sur quarante-huit, la MOYENNE de l'ecart a chaque longueur dit le
    biais et son ECART-TYPE dit le jitter, et les deux se lisent separement.

    ⚠ Les prefixes d'une meme marche sont EMBOITES, donc correles : ce qui est rendu ici est une
    description de la croissance, pas un test. Le test demanderait des marches independantes a
    chaque longueur, c'est-a-dire une course, et son prix est chiffre ailleurs.
    """
    par_pas: dict[int, list[float]] = {}
    for c in courbes:
        for x in c:
            if x.get("decidable"):
                par_pas.setdefault(x["pas"], []).append(float(x["ecart_au_compte_de_pas"]))
    if len(par_pas) < 3:
        return {"decidable": False, "pourquoi": "moins de trois longueurs lisibles"}
    lignes = []
    for k in sorted(par_pas):
        v = np.asarray(par_pas[k])
        lignes.append({"pas": k, "marches": int(v.size),
                       "ecart_moyen": round(float(v.mean()), 3),
                       "ecart_median": round(float(np.median(v)), 3),
                       "ecart_type": round(float(v.std(ddof=1)) if v.size > 1 else 0.0, 3)})
    k = np.asarray([x["pas"] for x in lignes], dtype=np.float64)
    moy = np.asarray([x["ecart_moyen"] for x in lignes])
    sd = np.asarray([x["ecart_type"] for x in lignes])
    # ⚠ Les deux ajustements passent par l'ORIGINE : a zero pas, l'ecart est nul par definition.
    # Laisser une constante libre ferait absorber le biais par une ordonnee a l'origine qui ne
    # correspond a rien de physique.
    pente_biais = float(np.sum(k * moy) / np.sum(k * k))
    pente_jitter = float(np.sum(np.sqrt(k) * sd) / np.sum(k))
    res_lin = float(np.sum((moy - pente_biais * k) ** 2))
    res_rac = float(np.sum((sd - pente_jitter * np.sqrt(k)) ** 2))
    return {"decidable": True, "par_longueur": lignes,
            "biais_par_pas": round(pente_biais, 4),
            "jitter_par_racine_de_pas": round(pente_jitter, 4),
            "residu_de_lajustement_lineaire": round(res_lin, 5),
            "residu_de_lajustement_en_racine": round(res_rac, 5),
            # ⭐⭐⭐ LES DEUX CONSEQUENCES ENCHAINEES, cote a cote, parce que c'est leur ECART qui
            # decide : un biais se multiplie par le nombre de pas, un jitter par sa racine.
            "spires_derivees_a_120_pas_si_biais": round(pente_biais * 120.0, 2),
            "spires_derivees_a_120_pas_si_jitter": round(
                pente_jitter * float(np.sqrt(120.0)), 2),
            # ⚠ Le verdict est rendu avec la reserve qui va avec : cinq longueurs emboitees ne
            # tranchent pas, elles decrivent.
            "le_biais_domine": bool(abs(pente_biais * 120.0)
                                    > abs(pente_jitter * float(np.sqrt(120.0)))),
            "ce_nest_pas_un_test": "les prefixes d'une meme marche sont emboites, donc correles ; "
                                   "ce qui est rendu decrit la croissance et ne la teste pas"}


def le_compte_suit_il_le_pas(courbes: list[list[dict]]) -> dict:
    """A chaque longueur, le compte de feuilles egale-t-il le compte de pas ?

    ⭐ C'est la forme la plus simple de la question, et elle se lit sans modele : si les k pas
    etaient justes, le prefixe de k pas franchit k feuilles.
    """
    par_pas: dict[int, list[float]] = {}
    for c in courbes:
        for x in c:
            if x.get("decidable"):
                par_pas.setdefault(x["pas"], []).append(float(x["feuilles_par_pas"]))
    if not par_pas:
        return {"decidable": False, "pourquoi": "aucun prefixe lisible"}
    scores: dict[int, list[float]] = {}
    for c in courbes:
        for x in c:
            if x.get("decidable"):
                scores.setdefault(x["pas"], []).append(float(x["score"]))
    lignes = [{"pas": k, "marches": len(v),
               "feuilles_par_pas_median": round(float(np.median(v)), 3),
               "feuilles_par_pas_moyen": round(float(np.mean(v)), 3),
               # ⚠⚠⚠ LE SCORE EST PUBLIE ET JAMAIS UTILISE COMME FILTRE. `98` a montre que hors de
               # sa fenetre l'estimateur rend un maximum parasite au score effondre, donc un score
               # bas signale un prefixe a ne pas croire — mais `108` a mesure que le score du
               # TRAJET est PLUS HAUT pour les marches qui ne comptent rien. Filtrer dessus
               # ecarterait donc preferentiellement les bonnes. Il se lit, il ne trie pas.
               "score_median": round(float(np.median(scores.get(k, [float("nan")]))), 3)}
              for k, v in sorted(par_pas.items())]
    return {"decidable": True, "par_longueur": lignes,
            "le_score_est_publie_jamais_filtre":
                "`98` : hors fenetre le score s'effondre, donc il signale un prefixe a ne pas "
                "croire ; `108` : le score du trajet est plus haut pour les marches qui ne "
                "comptent rien, donc filtrer dessus ecarterait les bonnes",
            "feuilles_par_pas_au_plus_court": lignes[0]["feuilles_par_pas_median"],
            "feuilles_par_pas_au_plus_long": lignes[-1]["feuilles_par_pas_median"],
            "derive_du_taux": round(lignes[-1]["feuilles_par_pas_median"]
                                    - lignes[0]["feuilles_par_pas_median"], 3)}


def controle_fabrique(pas_max: int = 6, graine: int = 110) -> dict:
    """Sur un empilement FABRIQUE dont le compte est connu, le registre des prefixes le rend-il ?

    ⚠⚠⚠ SANS CE CONTROLE, AUCUNE COURBE MESUREE SUR LA MATIERE NE VEUT RIEN DIRE. Un prefixe court
    est lu par un estimateur dont `98` a mesure qu'il ne garde rien sous sa fenetre : si le
    registre ne retrouve pas un compte CONNU a deux pas, sa valeur a deux pas sur la matiere est
    une invention, et la courbe de derive commence par un artefact.

    ⭐ L'empilement est droit, sans bruit puis avec : la reponse exacte est le nombre de pas, a
    chaque longueur. Ce qui est rendu est l'ecart a cette reponse, longueur par longueur.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    rng = np.random.default_rng(graine)
    out = []
    for bruit in (0.0, 15.0):
        lignes = []
        for k in range(PREFIXE_MIN, pas_max + 1):
            n = k * C.ECHANTILLONS + 1
            t = np.linspace(0.0, float(k), n)
            v = 100.0 + 40.0 * np.cos(2.0 * np.pi * t)
            if bruit:
                v = v + rng.normal(0.0, bruit, n)
            frac, sc, _ = C.feuilles_franchies(v.reshape(1, -1), f_min=0.35,
                                               f_max=float(k) + 4.0)
            lignes.append({"pas": k, "feuilles": round(float(frac[0]), 3),
                           "score": round(float(sc[0]), 3),
                           "ecart": round(float(frac[0]) - k, 3)})
        out.append({"bruit": bruit, "par_longueur": lignes,
                    "ecart_max": round(max(abs(x["ecart"]) for x in lignes), 3)})
    return {"empilements": out,
            # ⭐ Le verdict : le registre des prefixes est-il utilisable a TOUTE longueur ? La
            # barre est un dixieme de feuille, soit bien moins que ce qu'une derive interessante
            # deplacerait.
            "le_registre_des_prefixes_est_fidele": bool(
                all(x["ecart_max"] <= 0.1 for x in out)),
            "ecart_max_sur_fabrique": round(max(x["ecart_max"] for x in out), 3)}


def courbes_par_mode(lignes: list[dict], brut_de_107: dict,
                     part: float = 0.5) -> dict:
    """Les courbes separees par le mode que `107` a trouve, parce que leur MELANGE ment.

    ⚠⚠⚠ ELLE EXISTE PARCE QUE LA MEDIANE DE L'ENSEMBLE DIT L'INVERSE DE CHAQUE MODE. Sur les
    quarante-huit marches melangees, le taux tombe de 1,008 a 0,199 quand la fenetre s'allonge, ce
    qui se lit comme une derive. Separes : le mode qui compte ne derive PAS (1,012 a deux pas,
    1,085 a six) et le mode qui ne compte rien est CORRECT a deux pas puis s'effondre a trois.
    C'est une falaise dans une population, pas une derive dans les deux — et la mediane d'un
    melange dont les proportions changent avec la longueur est le piege que `107` a deja paye.

    ⚠ Le mode vient de `107`, donc d'une mesure faite sur le trajet COMPLET. Les prefixes courts
    sont donc etiquetes par ce que la marche fera plus tard : c'est legitime pour DECRIRE les deux
    populations, et ce serait circulaire pour les DEFINIR.
    """
    mode = {}
    for ln in brut_de_107.get("lignes", []):
        for cel in ln.get("detail", []):
            for sel in SELECTEURS:
                t = ((cel.get(sel) or {}).get("trajet_entier") or {})
                if t.get("decidable"):
                    mode[(int(ln["de"]), sel)] = bool(
                        float(t["feuilles_franchies"]) >= part * int(t["pas_parcourus"]))
    jeux: dict[str, list[dict]] = {"mode_haut": [], "mode_bas": []}
    for ln in lignes:
        for cel in ln.get("detail", []):
            for sel in SELECTEURS:
                m = cel.get(sel)
                if not isinstance(m, dict) or not m.get("decidable"):
                    continue
                if not (m.get("verification") or {}).get("reproduit"):
                    continue
                cle = (int(ln["de"]), sel)
                if cle not in mode:
                    continue
                jeux["mode_haut" if mode[cle] else "mode_bas"].append(
                    {x["pas"]: x for x in (m.get("prefixes") or []) if x.get("decidable")})
    out = {}
    for nom, jeu in jeux.items():
        if not jeu:
            out[nom] = {"marches": 0}
            continue
        longueurs = sorted({k for c in jeu for k in c})
        lig = []
        for k in longueurs:
            v = [c[k]["feuilles_par_pas"] for c in jeu if k in c]
            lig.append({"pas": k, "marches": len(v),
                        "feuilles_par_pas_median": round(float(np.median(v)), 3)})
        baisse = sum(1 for c in jeu if 2 in c and max(c) in c
                     and c[max(c)]["feuilles_par_pas"] < c[2]["feuilles_par_pas"])
        out[nom] = {"marches": len(jeu), "par_longueur": lig,
                    "marches_dont_le_taux_baisse": baisse,
                    "part_dont_le_taux_baisse": round(baisse / len(jeu), 3),
                    "au_plus_court": lig[0]["feuilles_par_pas_median"],
                    "au_plus_long": lig[-1]["feuilles_par_pas_median"],
                    "derive": round(lig[-1]["feuilles_par_pas_median"]
                                    - lig[0]["feuilles_par_pas_median"], 3)}
    a, b = out.get("mode_haut", {}), out.get("mode_bas", {})
    if a.get("marches") and b.get("marches"):
        out["les_deux_modes_coincident_au_plus_court"] = bool(
            abs(a["au_plus_court"] - b["au_plus_court"]) < 0.1)
        out["ecart_au_plus_court"] = round(a["au_plus_court"] - b["au_plus_court"], 3)
        out["ecart_au_plus_long"] = round(a["au_plus_long"] - b["au_plus_long"], 3)
        # ⭐⭐⭐ LE FAIT QUI COMPTE : les deux populations de `107` n'existent PAS a deux pas. Elles
        # apparaissent entre le deuxieme et le troisieme.
        out["les_deux_populations_naissent_apres_le_plus_court"] = bool(
            out["les_deux_modes_coincident_au_plus_court"]
            and abs(out["ecart_au_plus_long"]) > 0.5)
    return out


def la_falaise_est_elle_celle_de_linstrument(
        longueurs_donde=(6.0, 8.0, 10.0, 14.0), amplitudes=(1.0, 1.5, 2.0),
        pas_max: int = 6, graine: int = 110) -> dict:
    """Une DERIVE seule reproduit-elle « correct a deux pas, effondre a trois » ?

    ⭐⭐⭐ C'EST LE CONTROLE QUI DECIDE DU SENS DE TOUTE LA TRANCHE. Le mode qui ne compte rien lit
    exactement un a deux pas puis tombe : cela ressemble a une marche qui quitte la feuille. Mais
    l'estimateur a un plancher de frequence (`F_MIN = 0,35`), donc une composante de basse
    frequence n'est EXPRIMABLE qu'une fois la fenetre assez longue pour en contenir un tiers de
    periode — et des qu'elle l'est, si elle est plus forte que la periodicite, elle gagne
    l'argmax. Une falaise a une longueur precise est donc la signature attendue de l'INSTRUMENT.

    ⚠⚠ CE QUE CE CONTROLE ETABLIT ET CE QU'IL N'ETABLIT PAS. S'il reproduit la falaise, il montre
    que l'observation ne DISTINGUE PAS « la marche a quitte la feuille » de « une composante plus
    forte a masque la periodicite » : les deux restent possibles. Il ne montre pas laquelle est
    vraie. Ce qui serait fautif est de lire la falaise comme un fait de la matiere sans avoir
    regarde si l'instrument la fabrique tout seul.

    ⭐ L'empilement fabrique garde une periodicite PARFAITE en dessous : c'est ce qui rend le
    resultat lisible. Si le compte s'effondre alors que les feuilles sont toujours la, c'est bien
    l'instrument qui les perd.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    rng = np.random.default_rng(graine)
    cas = []
    for lam in longueurs_donde:
        for a in amplitudes:
            lig = []
            for k in range(PREFIXE_MIN, pas_max + 1):
                n = k * C.ECHANTILLONS + 1
                t = np.linspace(0.0, float(k), n)
                v = (100.0 + 40.0 * np.cos(2.0 * np.pi * t)
                     + 40.0 * a * np.cos(2.0 * np.pi * t / lam)
                     + rng.normal(0.0, 5.0, n))
                frac, _sc, _b = C.feuilles_franchies(v.reshape(1, -1), f_min=0.35,
                                                     f_max=float(k) + 4.0)
                lig.append({"pas": k, "feuilles_par_pas": round(float(frac[0]) / k, 3)})
            court = lig[0]["feuilles_par_pas"]
            suite = [x["feuilles_par_pas"] for x in lig[1:]]
            cas.append({"longueur_donde_en_pas": lam, "amplitude_de_la_derive": a,
                        "par_longueur": lig,
                        # ⚠ « Correct a deux pas » vaut a un dixieme pres : c'est le cran auquel
                        # l'empilement sans derive rend le compte juste.
                        "correct_au_plus_court": bool(abs(court - 1.0) <= 0.1),
                        "effondre_ensuite": bool(suite and max(suite) < 0.5),
                        "valeur_effondree": round(float(np.median(suite)), 3) if suite else None})
    falaises = [x for x in cas if x["correct_au_plus_court"] and x["effondre_ensuite"]]
    return {"cas": cas, "falaises": len(falaises), "cas_essayes": len(cas),
            # ⭐⭐⭐ LE VERDICT : une derive SEULE, sur une periodicite parfaite, suffit-elle ?
            "une_derive_seule_reproduit_la_falaise": bool(falaises),
            "valeur_effondree_mediane": (
                round(float(np.median([x["valeur_effondree"] for x in falaises])), 3)
                if falaises else None),
            "ce_que_ce_controle_netablit_pas":
                "laquelle des deux explications est vraie : il montre que l'observation ne les "
                "distingue pas"}


def departs_de_107(bandes_max: int | None = None, cellules: int = CELLULES_DE_107,
                   graine: int = GRAINE_DE_107) -> dict:
    """Les departs de la course de `107`, RE-DERIVES — il ne les avait pas gardes.

    ⚠⚠ CE N'EST PAS UN CHOIX DE DEPARTS MAIS UNE RECONSTITUTION. La graine et le nombre de
    cellules sont ceux de la course ; les changer donnerait d'autres cellules, donc des trajets qui
    n'ont jamais ete marches et dont les etapes de `107` ne diraient rien.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import la_normale_nest_pas_le_rayon as N  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import appliquer, appliquer_direction, matrice  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))
    out = {}
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
        out[(int(x["de"]), int(x["a"]))] = {
            "departs": appliquer(m, p0),
            "radial": appliquer_direction(m, N.direction_radiale(p0, c0))}
    return {"par_bande": out, "bandes": len(out)}


def mesurer(chemin: Path = CHEMIN_DE_107, bandes_max: int | None = None,
            fils: int = 32, brouillon: Path | None = None) -> dict:
    """Une lecture de polyligne par marche, puis le registre sur chacun de ses prefixes.

    ⚠⚠⚠ `brouillon` EST LA GARDE CONTRE LA PERTE D'UNE COURSE : les lectures y sont ecrites AVANT
    que le verdict ne soit calcule, donc un defaut dans l'agregation coute une seconde de calcul
    et non vingt minutes de reseau. C'est la lecon de `102` — *un agregat ne se desagrege pas* —
    prise par l'autre bout : ce qui a ete paye s'ecrit d'abord.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from la_normale_nest_pas_le_rayon import avancement, maintenant  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    brut = json.loads(Path(chemin).read_text())
    dep = departs_de_107(bandes_max)
    if "message" in dep:
        return dep
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    t0 = maintenant()
    lignes, courbes, lectures = [], [], 0
    bandes = [x for x in brut.get("lignes", []) if (int(x["de"]), int(x["a"])) in dep["par_bande"]]
    for i, ligne in enumerate(bandes):
        cle = (int(ligne["de"]), int(ligne["a"]))
        d = dep["par_bande"][cle]
        detail = []
        for j, cellule in enumerate(ligne.get("detail", [])):
            if j >= len(d["departs"]):
                break
            cel = {"depart_zyx": [round(float(t), 3) for t in d["departs"][j]],
                   "radial_zyx": [round(float(t), 6) for t in d["radial"][j]]}
            for sel in SELECTEURS:
                m = cellule.get(sel)
                if not m or not m.get("etapes"):
                    continue
                etapes = [x for x in m["etapes"] if "avance_um" in x]
                if len(etapes) < PREFIXE_MIN:
                    continue
                # ⚠ La polyligne est reconstruite des AVANCES et DIRECTIONS reellement prises,
                # jamais d'une droite entre les bouts : une droite couperait au travers et
                # compterait autre chose. Meme reconstruction que `107`.
                n = C.ECHANTILLONS * len(etapes)
                pts, p = [], np.asarray(d["departs"][j], dtype=np.float64).copy()
                for x in etapes:
                    dd = np.asarray(x["direction"], dtype=np.float64)
                    av = float(x["avance_um"]) / C.VOXEL_FIN_UM
                    tt = np.linspace(0.0, 1.0, C.ECHANTILLONS, endpoint=False)
                    pts.append(p[None, :] + dd[None, :] * (av * tt)[:, None])
                    p = p + dd * av
                pts.append(p[None, :])
                zyx = np.rint(np.concatenate(pts)).astype(np.int64)
                if not vol.dans_le_volume(zyx).all():
                    cel[sel] = {"decidable": False, "pourquoi": "le trajet sort du volume"}
                    continue
                v = vol.lire(zyx, fils=fils)
                lectures += 1
                if not np.isfinite(v).all():
                    cel[sel] = {"decidable": False, "pourquoi": "le trajet traverse un trou"}
                    continue
                pref = registre_des_prefixes(v, len(etapes), C.ECHANTILLONS)
                publie = (m.get("trajet_entier") or {}).get("feuilles_franchies")
                verif = le_prefixe_complet_reproduit_107(pref, publie)
                cel[sel] = {"decidable": True, "pas": len(etapes),
                            "prefixes": pref, "verification": verif}
                # ⚠⚠ SEULES LES MARCHES DONT LE DEPART EST VERIFIE ENTRENT DANS LES COURBES : une
                # polyligne qu'on n'a pas su reconstituer ne mesure pas une derive, elle mesure une
                # erreur de reconstitution.
                if verif.get("reproduit"):
                    courbes.append(pref)
            detail.append(cel)
        lignes.append({"de": ligne["de"], "a": ligne["a"],
                       "rayon_mm": ligne.get("rayon_mm"), "detail": detail})
        avancement(i + 1, len(bandes), "bandes", t0)

    lu = {"fragment": C.OBJET, "volume_fin": C.VOLUME_FIN,
          "source": str(Path(chemin).relative_to(RACINE)),
          "graine_de_107": GRAINE_DE_107, "cellules_de_107": CELLULES_DE_107,
          "lectures": lectures, "secondes": round(maintenant() - t0, 1),
          "bandes": len(lignes), "lignes": lignes}
    if brouillon is not None:
        brouillon.parent.mkdir(parents=True, exist_ok=True)
        brouillon.write_text(json.dumps(lu, indent=2, ensure_ascii=False))
        print(f"lectures écrites avant le verdict : {brouillon}")
    return agreger(lu)


def agreger(r: dict) -> dict:
    """Le verdict, DERIVE des prefixes gardes — meme partage que `100` a `107`.

    ⚠⚠⚠ ELLE EXISTE PARCE QUE J'AI PERDU VINGT MINUTES DE LECTURE. Ma premiere version agregeait
    a la fin de `mesurer`, donc un `KeyError` dans le verdict a jete toute la course : les
    verifications non decidables n'ont pas de champ `ecart`, et le maximum le lisait sans garde.
    `107` avait deja ce partage et son `--reagreger` ; ne pas l'avoir copie a coute la course.
    Desormais la lecture ECRIT avant que le verdict ne soit calcule, et `--reagreger` le refait
    sans rien relire.
    """
    lignes = r.get("lignes", [])
    verifs, courbes = [], []
    for l in lignes:
        for c in l.get("detail", []):
            for sel in SELECTEURS:
                m = c.get(sel)
                if not isinstance(m, dict) or not m.get("decidable"):
                    continue
                ver = m.get("verification") or {}
                verifs.append(ver)
                if ver.get("reproduit"):
                    courbes.append(m.get("prefixes") or [])
    # ⚠ Seules les verifications DECIDABLES portent un ecart : une marche dont aucun prefixe n'est
    # lisible n'a pas d'ecart a la mesure de `107`, elle n'a pas de mesure du tout.
    ecarts = [abs(x["ecart"]) for x in verifs if x.get("decidable")]
    reproduites = [x for x in verifs if x.get("reproduit")]
    r = dict(r)
    r.update({
        "marches_verifiees": len(reproduites), "marches_lues": len(verifs),
        "marches_sans_verification_possible": len(verifs) - len(ecarts),
        "part_verifiee": round(len(reproduites) / len(verifs), 3) if verifs else None,
        "ecart_max_de_verification": round(max(ecarts), 3) if ecarts else None,
        # ⭐⭐⭐ LE CONTROLE QUI AUTORISE TOUT LE RESTE : le depart re-derive est-il celui de la
        # course ? Si non, la tranche mesure un trajet imaginaire.
        "la_rederivation_du_depart_est_verifiee": bool(
            ecarts and len(reproduites) == len(ecarts)),
        "controle_fabrique": controle_fabrique(),
        "le_compte_suit_il_le_pas": le_compte_suit_il_le_pas(courbes),
        "biais_ou_jitter": biais_ou_jitter(courbes),
        "la_falaise_est_elle_celle_de_linstrument": la_falaise_est_elle_celle_de_linstrument()})
    # ⚠⚠ LES COURBES PAR MODE DEMANDENT LA MESURE DE `107`, donc elles ne sont calculees que si
    # elle est lisible : `agreger` doit rester utilisable sur un brouillon seul.
    src = RACINE / (r.get("source") or "")
    if src.is_file():
        r["par_mode"] = courbes_par_mode(lignes, json.loads(src.read_text()))
    return r


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    print(f"\n{r.get('fragment')} · {r['marches_lues']} marches relues en "
          f"{r['lectures']} lectures ({r['secondes']} s)\n")
    print(f"★★★ LE DÉPART RE-DÉRIVÉ EST-IL CELUI DE LA COURSE ? "
          f"{'OUI' if r['la_rederivation_du_depart_est_verifiee'] else 'NON'}")
    print(f"   {r['marches_verifiees']}/{r['marches_lues']} marches reproduisent le nombre "
          f"publié par `107`, écart max {r['ecart_max_de_verification']} feuille")
    cf = r.get("controle_fabrique", {})
    print(f"\n{'★' if cf.get('le_registre_des_prefixes_est_fidele') else 'NON —'} LE REGISTRE DES "
          f"PRÉFIXES EST-IL FIDÈLE SUR UN EMPILEMENT FABRIQUÉ ? "
          f"{'OUI' if cf.get('le_registre_des_prefixes_est_fidele') else 'NON'}"
          f" — écart max {cf.get('ecart_max_sur_fabrique')} feuille")
    for e in cf.get("empilements", []):
        print(f"   bruit {e['bruit']:>4} : "
              + "  ".join(f"{x['pas']}→{x['feuilles']}" for x in e["par_longueur"]))
    s = r.get("le_compte_suit_il_le_pas", {})
    if s.get("decidable"):
        print(f"\nLE COMPTE SUIT-IL LE PAS ? (feuilles par pas, médiane)")
        for x in s["par_longueur"]:
            print(f"   {x['pas']} pas · {x['marches']:>3} marches · "
                  f"{x['feuilles_par_pas_median']:.3f} · score médian {x['score_median']:.3f}")
        print(f"   ★ dérive du taux entre le plus court et le plus long : "
              f"{s['derive_du_taux']:+.3f} feuille par pas")
    pm = r.get("par_mode", {})
    if pm.get("mode_haut", {}).get("marches") and pm.get("mode_bas", {}).get("marches"):
        print(f"\n★★★ ET LA MÉDIANE DE L'ENSEMBLE DIT L'INVERSE DE CHAQUE MODE")
        for nom in ("mode_haut", "mode_bas"):
            m = pm[nom]
            print(f"   {nom:<11} {m['marches']:>3} marches · "
                  + "  ".join(f"{x['pas']}→{x['feuilles_par_pas_median']:.3f}"
                              for x in m["par_longueur"])
                  + f"  · dérive {m['derive']:+.3f}")
            print(f"   {'':<11}     dont le taux baisse : "
                  f"{m['marches_dont_le_taux_baisse']}/{m['marches']}")
        print(f"   ★ écart entre les modes : {pm['ecart_au_plus_court']:+.3f} au plus court, "
              f"{pm['ecart_au_plus_long']:+.3f} au plus long")
        print(f"   ★★★ LES DEUX POPULATIONS DE `107` N'EXISTENT PAS AU PLUS COURT : "
              f"{pm.get('les_deux_populations_naissent_apres_le_plus_court')}")
    fa = r.get("la_falaise_est_elle_celle_de_linstrument", {})
    if fa:
        print(f"\n★★★ UNE DÉRIVE SEULE REPRODUIT-ELLE LA FALAISE ? "
              f"{'OUI' if fa.get('une_derive_seule_reproduit_la_falaise') else 'NON'}")
        print(f"   {fa.get('falaises')} cas sur {fa.get('cas_essayes')} rendent « correct à deux "
              f"pas, effondré ensuite », valeur effondrée médiane "
              f"{fa.get('valeur_effondree_mediane')}")
        print(f"   ⚠ ce contrôle n'établit pas {fa.get('ce_que_ce_controle_netablit_pas')}")
    b = r.get("biais_ou_jitter", {})
    if b.get("decidable"):
        print(f"\n⚠⚠⚠ BIAIS OU JITTER — SUR L'ENSEMBLE, DONC SUR UN MÉLANGE")
        print(f"   {'pas':>5} {'marches':>8} {'écart moyen':>13} {'écart-type':>12}")
        for x in b["par_longueur"]:
            print(f"   {x['pas']:>5} {x['marches']:>8} {x['ecart_moyen']:>13.3f} "
                  f"{x['ecart_type']:>12.3f}")
        print(f"   biais {b['biais_par_pas']:+.4f} feuille par pas → "
              f"{b['spires_derivees_a_120_pas_si_biais']:+.2f} spires sur cent vingt")
        print(f"   jitter {b['jitter_par_racine_de_pas']:.4f} par racine de pas → "
              f"{b['spires_derivees_a_120_pas_si_jitter']:.2f} spires sur cent vingt")
        print(f"   sur le MÉLANGE : "
              f"{'le biais domine' if b['le_biais_domine'] else 'le jitter domine'}")
        print(f"   ⚠ {b['ce_nest_pas_un_test']}")
        if pm.get("les_deux_populations_naissent_apres_le_plus_court"):
            print(f"   ⚠⚠⚠ ET CE BIAIS EST CELUI D'UN MÉLANGE DONT LES PROPORTIONS CHANGENT AVEC "
                  f"LA LONGUEUR : le mode qui compte ne dérive pas "
                  f"({pm['mode_haut']['derive']:+.3f}), le mode qui ne compte rien tombe d'une "
                  f"falaise ({pm['mode_bas']['derive']:+.3f}). Le lire comme une dérive de la "
                  f"matière serait la faute de `107` repayée.")


def _prefixes(feuilles, pas_debut: int = PREFIXE_MIN) -> list[dict]:
    """Une courbe de prefixes fabriquee, pour eprouver ce qui la lit."""
    return [{"pas": pas_debut + i, "decidable": True, "feuilles": f,
             "feuilles_par_pas": round(f / (pas_debut + i), 3),
             "ecart_au_compte_de_pas": round(f - (pas_debut + i), 3),
             "score": 0.5, "en_butee": False, "echantillons": 0}
            for i, f in enumerate(feuilles)]


def verifier() -> int:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # === LE REGISTRE DES PREFIXES SUR UN SIGNAL CONNU =======================================
    # ⭐⭐⭐ SANS CE CONTROLE, LA COURBE DE DERIVE COMMENCE PAR UN ARTEFACT. `98` a mesure que sous
    # sa fenetre l'estimateur ne garde rien ; si le registre ne retrouve pas un compte CONNU a deux
    # pas, sa valeur a deux pas sur la matiere est une invention.
    n = 6 * C.ECHANTILLONS + 1
    t = np.linspace(0.0, 6.0, n)
    pref = registre_des_prefixes(100.0 + 40.0 * np.cos(2.0 * np.pi * t), 6, C.ECHANTILLONS)
    v("le registre des préfixes rend une ligne par longueur, de deux à six",
      [x["pas"] for x in pref] == [2, 3, 4, 5, 6], str([x["pas"] for x in pref]))
    v("... et il retrouve le compte de pas à chaque longueur",
      all(abs(x["feuilles"] - x["pas"]) <= 0.1 for x in pref if x["decidable"]),
      str([(x["pas"], x["feuilles"]) for x in pref]))
    # ⚠⚠⚠ LA FENETRE SUIT LE PREFIXE, ET LA GARDE VERIFIE CE QUI ARRIVE QUAND ELLE EST TROP
    # ETROITE. Mon premier controle attendait une BUTEE ; c'est faux, et `98` l'avait deja ecrit :
    # loin au-dela de la fenetre l'estimateur trouve un maximum INTERIEUR parasite et la butee ne
    # voit rien — c'est le SCORE qui ecarte. Mesure : huit periodes dans une fenetre qui plafonne
    # a six rendent 5,785 au score 0,067, contre 1,000 pour deux periodes bien dedans.
    def _lire(periodes, fmax):
        tt = np.linspace(0.0, periodes, 2 * C.ECHANTILLONS + 1)
        return C.feuilles_franchies((100.0 + 40.0 * np.cos(2.0 * np.pi * tt)).reshape(1, -1),
                                    f_min=0.35, f_max=fmax)

    f8, s8, b8 = _lire(8.0, 6.0)
    f2, s2, _ = _lire(2.0, 6.0)
    v("hors de la fenêtre, c'est le SCORE qui écarte et la butée ne voit rien",
      float(s8[0]) < 0.2 and float(s2[0]) > 0.9 and not bool(b8[0]),
      f"score {s8[0]:.4f} hors fenêtre contre {s2[0]:.4f} dedans, butée {bool(b8[0])}")
    v("... et le maximum parasite est INTÉRIEUR, donc indiscernable sans le score",
      0.35 < float(f8[0]) < 6.0, f"fraction {f8[0]:.3f}")
    # ⚠ Un profil plat n'est pas un compte nul : il est declare non decidable.
    plat = registre_des_prefixes(np.full(6 * C.ECHANTILLONS + 1, 100.0), 6, C.ECHANTILLONS)
    v("un profil plat est déclaré non décidable, pas compté zéro",
      all(not x["decidable"] for x in plat))
    court = registre_des_prefixes(np.zeros(3), 6, C.ECHANTILLONS)
    v("un profil plus court qu'un préfixe ne fabrique pas de ligne", court == [])

    # === LA VERIFICATION DE LA RE-DERIVATION ================================================
    # ⭐⭐⭐ ELLE DOIT POUVOIR DIRE NON, sinon tout ce qui suit repose sur un depart invérifié.
    ok = le_prefixe_complet_reproduit_107(_prefixes([2.0, 3.0, 4.0, 5.0, 6.0]), 6.0)
    v("un préfixe complet qui reproduit le nombre publié est accepté",
      ok["reproduit"] is True, f"écart {ok['ecart']}")
    non = le_prefixe_complet_reproduit_107(_prefixes([2.0, 3.0, 4.0, 5.0, 6.0]), 4.5)
    v("... et un qui ne le reproduit PAS est refusé",
      non["reproduit"] is False, f"écart {non['ecart']}")
    v("... à la tolérance déclarée, pas à l'œil",
      le_prefixe_complet_reproduit_107(_prefixes([6.005]), 6.0)["reproduit"] is True
      and le_prefixe_complet_reproduit_107(_prefixes([6.05]), 6.0)["reproduit"] is False)
    v("la vérification se refuse sans rien de publié",
      le_prefixe_complet_reproduit_107(_prefixes([6.0]), None)["decidable"] is False)

    # === BIAIS CONTRE JITTER ================================================================
    # ⭐⭐⭐ LA GARDE CENTRALE : les deux formes doivent etre distinguees, et dans les deux sens.
    # Un BIAIS est un ecart qui grandit avec la longueur ; un JITTER est un ecart de moyenne nulle
    # dont seule la DISPERSION grandit. Les confondre change le verdict du graal.
    rng = np.random.default_rng(3)
    biaisees = [_prefixes([(k * 1.1) + 0.02 * float(rng.standard_normal())
                           for k in range(2, 7)]) for _ in range(40)]
    b = biais_ou_jitter(biaisees)
    v("un écart qui grandit avec la longueur est lu comme un BIAIS",
      b["le_biais_domine"] is True,
      f"biais {b['biais_par_pas']:+.4f}, jitter {b['jitter_par_racine_de_pas']:.4f}")
    v("... et le biais mesuré vaut celui qu'on a injecté",
      abs(b["biais_par_pas"] - 0.1) < 0.02, f"{b['biais_par_pas']:+.4f} pour 0,1 injecté")
    gigues = [_prefixes([k + 0.3 * float(rng.standard_normal()) * np.sqrt(k)
                         for k in range(2, 7)]) for _ in range(60)]
    j = biais_ou_jitter(gigues)
    v("un écart de moyenne nulle dont la dispersion grandit est lu comme un JITTER",
      j["le_biais_domine"] is False,
      f"biais {j['biais_par_pas']:+.4f}, jitter {j['jitter_par_racine_de_pas']:.4f}")
    v("... et le jitter mesuré vaut celui qu'on a injecté",
      abs(j["jitter_par_racine_de_pas"] - 0.3) < 0.08,
      f"{j['jitter_par_racine_de_pas']:.4f} pour 0,3 injecté")
    # ⚠⚠ ET L'ECART ENTRE LES DEUX CONSEQUENCES EST UNE PROPRIETE ARITHMETIQUE, PAS UN SEUIL. A
    # AMPLEUR EGALE par pas, un biais coute `n` et un jitter `√n`, donc leur rapport vaut
    # exactement `√120` — 10,95. Mon premier controle comparait deux fixtures d'amplitudes
    # differentes et exigeait un facteur cinq choisi a la main : un seuil regle sur ce qui passe.
    egal = biais_ou_jitter([_prefixes([k * 1.1 for k in range(2, 7)])])
    rapport = (abs(egal["spires_derivees_a_120_pas_si_biais"])
               / max(abs(0.1 * float(np.sqrt(120.0))), 1e-12))
    v("à ampleur égale par pas, le biais coûte √120 fois le jitter",
      abs(rapport - float(np.sqrt(120.0))) < 0.3, f"rapport {rapport:.2f} pour 10,95 attendu")
    v("... et la fonction dit que ce n'est pas un test",
      "correles" in biais_ou_jitter(gigues)["ce_nest_pas_un_test"])
    v("le partage se refuse sous trois longueurs",
      biais_ou_jitter([_prefixes([2.0, 3.0])])["decidable"] is False)

    # === LE COMPTE SUIT-IL LE PAS ===========================================================
    s = le_compte_suit_il_le_pas([_prefixes([2.0, 3.0, 4.0, 5.0, 6.0])] * 5)
    v("un compte parfait rend une feuille par pas à toute longueur",
      all(abs(x["feuilles_par_pas_median"] - 1.0) < 1e-9 for x in s["par_longueur"]))
    v("... et une dérive du taux nulle", abs(s["derive_du_taux"]) < 1e-9)
    s2 = le_compte_suit_il_le_pas([_prefixes([2.4, 3.3, 4.2, 5.1, 6.0])] * 5)
    v("... là où un taux qui baisse est rendu avec son signe",
      s2["derive_du_taux"] < 0, f"{s2['derive_du_taux']:+.3f}")

    # === LE CONTROLE FABRIQUE ===============================================================
    cf = controle_fabrique()
    v("le contrôle fabriqué est fidèle à toute longueur, avec et sans bruit",
      cf["le_registre_des_prefixes_est_fidele"] is True,
      f"écart max {cf['ecart_max_sur_fabrique']}")
    v("... et il porte les deux niveaux de bruit",
      [x["bruit"] for x in cf["empilements"]] == [0.0, 15.0])

    # === LES COURBES PAR MODE, PARCE QUE LEUR MELANGE MENT ==================================
    # ⭐⭐⭐ LA GARDE QUI A SAUVE LA TRANCHE D'UNE FAUSSE CONCLUSION. Sur l'ensemble, le taux tombe
    # avec la longueur et se lit comme une derive ; separes, un mode ne derive pas et l'autre tombe
    # d'une falaise. Une mediane sur un melange dont les PROPORTIONS changent avec la longueur est
    # la faute de `107` sous un costume neuf.
    def _faux107(modes):
        return {"lignes": [{"de": i, "detail": [{
            "calibre": {"trajet_entier": {"decidable": True, "pas_parcourus": 6,
                                          "feuilles_franchies": 6.0 if m else 0.7}}}]}
            for i, m in enumerate(modes)]}

    def _faux110(courbes):
        return [{"de": i, "detail": [{"calibre": {
            "decidable": True, "pas": 6, "prefixes": _prefixes(c),
            "verification": {"decidable": True, "reproduit": True, "ecart": 0.0}}}]}
            for i, c in enumerate(courbes)]

    hauts = [[2.0, 3.0, 4.0, 5.0, 6.0]] * 6
    bas = [[2.0, 0.7, 0.8, 0.9, 0.9]] * 6
    pm = courbes_par_mode(_faux110(hauts + bas), _faux107([True] * 6 + [False] * 6))
    v("les deux modes sont séparés et comptés",
      pm["mode_haut"]["marches"] == 6 and pm["mode_bas"]["marches"] == 6,
      f"{pm['mode_haut']['marches']} / {pm['mode_bas']['marches']}")
    v("... et deux populations qui COÏNCIDENT au plus court sont annoncées comme naissant après",
      pm["les_deux_populations_naissent_apres_le_plus_court"] is True,
      f"écart {pm['ecart_au_plus_court']:+.3f} au plus court, "
      f"{pm['ecart_au_plus_long']:+.3f} au plus long")
    # ⚠⚠ ET LA GARDE DOIT DIRE NON quand les deux populations different DES LE PLUS COURT : sinon
    # « elles naissent apres » serait un verdict qui ne depend pas des donnees.
    bas2 = [[0.6, 0.7, 0.8, 0.9, 0.9]] * 6
    pm2 = courbes_par_mode(_faux110(hauts + bas2), _faux107([True] * 6 + [False] * 6))
    v("... et NON quand elles diffèrent dès le plus court",
      pm2["les_deux_populations_naissent_apres_le_plus_court"] is False,
      f"écart {pm2['ecart_au_plus_court']:+.3f} au plus court")
    v("... et le compte des marches dont le taux baisse est rendu par mode",
      pm["mode_bas"]["marches_dont_le_taux_baisse"] == 6
      and pm["mode_haut"]["marches_dont_le_taux_baisse"] == 0,
      f"{pm['mode_bas']['marches_dont_le_taux_baisse']} contre "
      f"{pm['mode_haut']['marches_dont_le_taux_baisse']}")
    # ⚠ Une marche dont `107` n'a pas de mode ne peut pas etre rangee : elle est ecartee.
    pm3 = courbes_par_mode(_faux110(hauts), {"lignes": []})
    v("une marche sans mode connu de `107` est écartée, pas rangée au hasard",
      pm3["mode_haut"]["marches"] == 0 and pm3["mode_bas"]["marches"] == 0)

    # === LA FALAISE EST-ELLE CELLE DE L'INSTRUMENT ? =========================================
    # ⭐⭐⭐ LE CONTROLE QUI DECIDE DU SENS DE LA TRANCHE, et il doit trancher dans les DEUX sens.
    # Sans derive, une periodicite parfaite ne doit produire AUCUNE falaise ; avec une derive assez
    # forte, elle doit en produire — sinon lire une falaise comme un fait de la matiere serait
    # gratuit.
    sans = la_falaise_est_elle_celle_de_linstrument(amplitudes=(0.0,))
    v("sans dérive, une périodicité parfaite ne produit AUCUNE falaise",
      sans["une_derive_seule_reproduit_la_falaise"] is False,
      f"{sans['falaises']} falaises sur {sans['cas_essayes']}")
    avec = la_falaise_est_elle_celle_de_linstrument(longueurs_donde=(8.0,), amplitudes=(1.5,))
    v("... et une dérive assez forte en produit une, sur une périodicité INTACTE",
      avec["une_derive_seule_reproduit_la_falaise"] is True,
      f"effondré à {avec['valeur_effondree_mediane']}")
    v("... et la fonction dit ce qu'elle n'établit PAS",
      "ne les distingue pas" in avec["ce_que_ce_controle_netablit_pas"])

    # === L'AGREGATION SURVIT A CE QUI N'EST PAS DECIDABLE ====================================
    # ⚠⚠⚠ CE CONTROLE EXISTE PARCE QUE SON ABSENCE A COUTE VINGT MINUTES DE LECTURE. Une marche
    # dont aucun prefixe n'est lisible rend une verification SANS champ `ecart`, et mon maximum le
    # lisait sans garde : le verdict plantait apres la course, donc la course etait perdue.
    brut = {"lignes": [{"de": 1, "a": 2, "rayon_mm": 4.0, "detail": [{
        "calibre": {"decidable": True, "pas": 6,
                    "prefixes": _prefixes([2.0, 3.0, 4.0, 5.0, 6.0]),
                    "verification": {"decidable": True, "pas": 6, "lu": 6.0,
                                     "publie": 6.0, "ecart": 0.0, "reproduit": True}},
        "deux_roles": {"decidable": True, "pas": 6,
                       "prefixes": _prefixes([2.0, 3.0, 4.0, 5.0, 6.0]),
                       # ⚠ Celle-ci n'a PAS de champ `ecart` : c'est exactement le cas qui a
                       # plante la course.
                       "verification": {"decidable": False, "pourquoi": "rien de publié"}}}]}]}
    try:
        ag = agreger(brut)
        ok = True
    except KeyError as e:
        ag, ok = {}, False
        print(f"     (KeyError : {e})")
    v("l'agrégation survit à une vérification non décidable",
      ok and ag.get("marches_lues") == 2 and ag.get("ecart_max_de_verification") == 0.0,
      f"{ag.get('marches_lues')} lues, écart max {ag.get('ecart_max_de_verification')}")
    v("... et elle compte à part celles dont la vérification est impossible",
      ag.get("marches_sans_verification_possible") == 1,
      f"{ag.get('marches_sans_verification_possible')}")
    # ⚠⚠ ET SEULES LES MARCHES VERIFIEES ENTRENT DANS LES COURBES : une polyligne qu'on n'a pas su
    # reconstituer ne mesure pas une derive, elle mesure une erreur de reconstitution.
    v("... et seule la marche vérifiée entre dans les courbes",
      ag.get("le_compte_suit_il_le_pas", {}).get("par_longueur", [{}])[0].get("marches") == 1,
      str(ag.get("le_compte_suit_il_le_pas", {}).get("par_longueur", [{}])[0]))
    v("... et le verdict de re-dérivation est vrai quand tout ce qui est vérifiable l'est",
      ag.get("la_rederivation_du_depart_est_verifiee") is True)
    faux = json.loads(json.dumps(brut))
    faux["lignes"][0]["detail"][0]["calibre"]["verification"] = {
        "decidable": True, "pas": 6, "lu": 4.0, "publie": 6.0, "ecart": -2.0,
        "reproduit": False}
    v("... et FAUX dès qu'une marche vérifiable ne reproduit pas le nombre publié",
      agreger(faux)["la_rederivation_du_depart_est_verifiee"] is False)

    # === LA RE-DERIVATION DES DEPARTS ========================================================
    # ⚠ Elle est locale (maillages en cache), donc la batterie peut l'exercer sans reseau.
    d = departs_de_107(bandes_max=2)
    if "message" in d:
        v("les départs de `107` se re-dérivent hors réseau", False, d["message"])
    else:
        v("les départs de `107` se re-dérivent hors réseau", d["bandes"] >= 1,
          f"{d['bandes']} bandes")
        cle = next(iter(d["par_bande"]))
        v("... et chaque bande rend autant de départs que de cellules",
          len(d["par_bande"][cle]["departs"]) == CELLULES_DE_107)
        # ⭐⭐ ET ELLE EST DETERMINISTE : deux appels rendent le meme depart, sinon la
        # reconstitution ne serait pas reproductible et la verification ne voudrait rien dire.
        d2 = departs_de_107(bandes_max=2)
        v("... et la re-dérivation est déterministe",
          bool(np.allclose(d["par_bande"][cle]["departs"],
                           d2["par_bande"][cle]["departs"])))
        # ⚠⚠ UNE AUTRE GRAINE DOIT DONNER UN AUTRE DEPART, sinon la graine ne serait pas ce qui
        # choisit la cellule et la reconstitution tiendrait par hasard.
        d3 = departs_de_107(bandes_max=2, graine=GRAINE_DE_107 + 1)
        if "message" not in d3 and cle in d3["par_bande"]:
            v("... et une autre graine donne un autre départ",
              not np.allclose(d["par_bande"][cle]["departs"],
                              d3["par_bande"][cle]["departs"]))

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 0 if echecs == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--source", type=Path, default=CHEMIN_DE_107)
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
    r = mesurer(chemin=a.source, bandes_max=a.bandes, fils=a.fils, brouillon=a.json)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
