"""La suite des détours peut-elle se dérouler sans main ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P76`. `229` et `230` ont chacun dérivé un détour — la colonne
78, puis la rangée 106 — et le second a fait sortir une boucle du bruit, la première depuis que `227` en a
posé la règle. Mais chaque fois, une main a choisi LE CÔTÉ à contourner : la colonne 71 parce que `228` la
désignait, la rangée 99 par une incidence lue à l'œil. Ce qui remplace l'humain qui corrige ne peut pas
choisir un côté à l'œil.

## La procédure, déclarée

Devant une boucle qui ne ferme pas, la procédure contourne SES QUATRE CÔTÉS À LA FOIS : pour chacun, le
détour de `229` — la bande de cinq lignes la plus proche du côté, vers l'intérieur, dont aucune ligne ne vote
pour lui ni pour le côté opposé. Aucun côté n'est choisi. Les quatre détours et les quatre côtés font un
treillis de quatre rangées et quatre colonnes, donc neuf cellules, et la fermeture de la boucle est
exactement la somme des leurs.

Chaque cellule est jugée par l'instrument de `224` — sa fermeture contre des demi-côtés tirés indépendamment
par blocs. Sans main pour déclarer une seule boucle, LA GARANTIE PORTE SUR LA FAMILLE DES NEUF.

⚠⚠⚠ DÉCLARÉ D'ABORD, ET REMPLACÉ AVANT LA LECTURE : une cellule devait sortir au-delà de `1 − 0,05 / 9`, la
garantie partagée de `227`. Sur des pas fabriqués indépendants, AVANT toute lecture, l'étalon de `227` ne tient
pas ce seuil : la plus forte des neuf cellules le passe trop souvent, et pas seulement sur des côtés courts. Le
seuil est donc DÉRIVÉ : c'est la plus petite part que la plus forte cellule de demi-côtés indépendants
fabriqués — au `θ`, aux longueurs et aux dispersions lues — n'atteint que dans au plus `0,05` de ses
calibrations ; et ⭐⭐⭐ un second étalon, sur d'autres tirages, celui de `227`, le vérifie. Si trop de
calibrations atteignent déjà le haut de l'échelle, le seuil n'existe pas et rien ne sort. Le seuil partagé et
son étalon restent publiés à côté. ⚠⚠ Et c'est une issue qu'on attend : tout détour tombe à sept coutures de
son côté, et sur des demi-côtés si courts, les pas fabriqués montrent déjà la part du nul toucher le haut de
l'échelle.

Un trou de majorité est franchi par la règle de `225`. Les détours déjà lus et publiés sont repris tels
quels ; seuls ceux qui manquent sont lus.

## Où elle commence, et où elle s'arrête

Elle commence là où la main a commencé en `229` : la boucle fine en haut à gauche de `227`, celle qui porte
la fermeture. ⚠ Commencer plus haut, au grand rectangle, est une autre question.

⚠⚠⚠ LA RÈGLE D'ARRÊT : la procédure ne descend dans une cellule que si elle sort du bruit, que l'étalon de
son niveau tient, et que chacun de ses quatre côtés a la place d'un détour. Elle s'arrête quand plus aucune
cellule n'y descend. Chaque niveau a sa garantie, et elles ne se partagent pas entre niveaux : c'est dit.

## Ce qui contrôle

⚠⚠⚠ Chaque bande lue croise les lectures publiées de `219`, `223`, `224`, `227`, `228`, `229` et `230` et
retombe partout où elles lisent la même couture, sinon refus. ⚠⚠⚠ LA PROCÉDURE DOIT RETROUVER `229` ET `230`
SANS QU'ON LES LUI INDIQUE : au premier niveau, ses détours de gauche et du haut sont la colonne 78 et la
rangée 106, et son treillis recompose EXACTEMENT la boucle fine de `227`, les deux boucles du haut de `229`
et la boucle étroite de la rangée de `230`, sinon refus.

## Les issues, exclusives — jugées au premier niveau

- le seuil de la famille n'existe pas à cette résolution : la procédure ne désigne rien ;
- il ne tient pas sa garantie sur l'étalon indépendant : la procédure ne désigne rien ;
- aucune cellule ne sort du bruit : sans main, la garantie se partage et la procédure s'arrête sans rien
  désigner ;
- les cellules qui sortent sont toutes sur la rangée 99, entre les colonnes 78 et 106 : sans main, la
  procédure retrouve la région que `230` a désignée ;
- une cellule sort ailleurs : la procédure désigne autre chose que `230`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une cellule désigne une RÉGION, pas un côté. Et elle ne dit pas qu'une
main qui choisit bien serait remplacée : seulement ce que coûte de ne plus choisir.

Usage :
    uv run python src/nappe/la_suite_des_detours_se_deroule_t_elle_sans_main.py --verifier
    uv run python src/nappe/la_suite_des_detours_se_deroule_t_elle_sans_main.py --lire <lecture.json>
    uv run python src/nappe/la_suite_des_detours_se_deroule_t_elle_sans_main.py --depuis <lecture.json> \\
        --json docs/mesures/la_suite_des_detours_se_deroule_t_elle_sans_main.json
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
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, la_fermeture, la_somme,
                                                          lautocorrelation_commune, lepreuve,
                                                          lire_les_bandes, relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import (le_consensus,  # noqa: E402
                                                  le_theta_dune_autocorrelation,
                                                  une_serie_dependante)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, le_seuil,
                                                          les_boucles_qui_sortent,
                                                          les_pas_dune_bande)
from quest_ce_qui_franchit_le_trou_de_majorite import (ce_que_224_a_rendu,  # noqa: E402
                                                       le_remplissage, les_trous)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from un_detour_separe_t_il_lerreur_de_la_colonne_71 import (CE_QUE_228_A_RENDU, _long,  # noqa: E402
                                                             ce_que_227_a_rendu, le_detour,
                                                             les_lectures_publiees,
                                                             les_lignes_de_la_colonne, les_sources)
from un_detour_separe_t_il_lerreur_de_la_rangee_99 import ce_que_229_a_rendu  # noqa: E402

CE_QUE_230_A_RENDU = RACINE / "docs" / "mesures" / "un_detour_separe_t_il_lerreur_de_la_rangee_99.json"

LA_QUESTION_DECLAREE = "la suite des détours peut-elle se dérouler sans main ?"
LA_MESURE_DECLAREE = ("les quatre détours d'une boucle qui ne ferme pas, dérivés sans choisir de côté, et ses "
                      "neuf cellules, chacune contre des demi-côtés tirés indépendamment ; une cellule sort du "
                      "bruit au-delà du seuil de la famille, dérivé d'un étalon et vérifié par un second, et la "
                      "procédure descend dans celle qui sort")
LES_LIGNES = ("haut", "milieu", "bas")
LES_COLONNES = ("gauche", "milieu", "droite")
LA_REGION_DE_230 = ("haut_milieu", "haut_droite")


# ─────────────────────────────── ce que 230 a publié ───────────────────────────────

def ce_que_230_a_rendu(chemin: Path = CE_QUE_230_A_RENDU) -> dict:
    """Le détour de la rangée de `230`, son treillis et les fermetures de ses boucles — relus."""
    lu = les_lectures_publiees(chemin)
    if not lu.get("decidable"):
        return lu
    d = lu["brut"]
    a = d.get("lanalyse_du_treillis_de_la_rangee") or {}
    if not d.get("le_treillis") or not a.get("les_boucles"):
        return {"decidable": False, "raison": "`230` ne publie pas son treillis ni ses boucles"}
    return {"decidable": True, "relues": lu["relues"], "le_detour": int(d["le_detour"]),
            "R": [int(x) for x in d["le_treillis"]["rangees"]], "C": [int(x) for x in d["le_treillis"]["colonnes"]],
            "les_fermetures": {n: float(b["la_fermeture_en_voxels"]) for n, b in a["les_boucles"].items()
                               if b.get("fermable")}}


# ─────────────────────────────── le registre des bandes ───────────────────────────────

def _entree(sens: str, centre: int, lignes, de: int, a: int, pas: dict, source: str) -> dict:
    return {"le_sens": sens, "le_centre": int(centre), "les_lignes": [int(x) for x in lignes], "de": int(de),
            "a": int(a), "pas": pas, "la_source": source}


def le_registre(par219: dict, par223: dict, par224: dict, par227: dict, par229: dict, par230: dict) -> list[dict]:
    """Toutes les bandes de cinq lignes publiées, avec leur étendue lue et leurs pas le long."""
    gy, gx = par224["la_grille"]
    r219 = sorted(int(r) for r in par219["les_rangees"])
    c223 = sorted(int(c) for c in par223["les_colonnes"])
    out = [_entree("rangees", r219[len(r219) // 2], r219, 0, gx - 1, par219["les_pas_par_rangee"], "219"),
           _entree("colonnes", c223[len(c223) // 2], c223, 0, gy - 1, par223["les_pas_par_colonne"], "223")]
    for nom, par in (("224", par224), ("227", par227), ("229", par229), ("230", par230)):
        for k, rel in sorted(par["relues"].items()):
            out.append(_entree(rel["le_sens"], rel["le_centre"], rel["les_lignes"], rel["de"], rel["a"], _long(rel),
                               f"{nom} {k}"))
    return out


def la_bande(registre: list[dict], sens: str, centre: int, de: int, a: int, combien: int) -> dict | None:
    """Une bande publiée de ce sens et de ce centre, à `combien` lignes, qui couvre `[de, à]` — ou rien."""
    voulues = les_rangees_a_lire(int(centre), int(combien))
    for e in registre:
        if (e["le_sens"] == sens and e["le_centre"] == int(centre) and e["les_lignes"] == voulues
                and e["de"] <= int(de) and e["a"] >= int(a)):
            return e
    return None


# ─────────────────────────────── un niveau de la procédure ───────────────────────────────

def les_detours(coins, combien: int) -> dict | None:
    """Les quatre détours d'une boucle `(r0, r1, c0, c1)`, dérivés par la fonction de `229` — ou rien, si un côté
    n'a pas la place d'un détour, ou si deux détours opposés se touchent."""
    r0, r1, c0, c1 = (int(x) for x in coins)
    d = {"haut": le_detour(r0, r1, combien), "bas": le_detour(r1, r0, combien),
         "gauche": le_detour(c0, c1, combien), "droite": le_detour(c1, c0, combien)}
    if any(x is None for x in d.values()):
        return None
    for a_, b_ in (("haut", "bas"), ("gauche", "droite")):
        if not d[a_] < d[b_] or set(les_rangees_a_lire(d[a_], combien)) & set(les_rangees_a_lire(d[b_], combien)):
            return None
    return d


def le_treillis_dun_niveau(coins, detours: dict) -> tuple[list[int], list[int]]:
    r0, r1, c0, c1 = (int(x) for x in coins)
    return [r0, detours["haut"], detours["bas"], r1], [c0, detours["gauche"], detours["droite"], c1]


def les_bandes_voulues(R, C, combien: int) -> list[dict]:
    """Les huit bandes d'un niveau, sur l'étendue de la boucle : quatre côtés et quatre détours."""
    out = []
    for r in R:
        out.append({"cle": f"rangees_{r}_{C[0]}_{C[-1]}", "le_sens": "rangees", "le_centre": int(r),
                    "les_lignes": les_rangees_a_lire(int(r), combien), "de": int(C[0]), "a": int(C[-1])})
    for c in C:
        out.append({"cle": f"colonnes_{c}_{R[0]}_{R[-1]}", "le_sens": "colonnes", "le_centre": int(c),
                    "les_lignes": les_rangees_a_lire(int(c), combien), "de": int(R[0]), "a": int(R[-1])})
    return out


def les_cellules(R, C) -> dict:
    """Les neuf cellules d'un treillis de quatre sur quatre, en coins."""
    out = {}
    for i, ni in enumerate(LES_LIGNES):
        for j, nj in enumerate(LES_COLONNES):
            out["centre" if (i, j) == (1, 1) else f"{ni}_{nj}"] = (int(R[i]), int(R[i + 1]), int(C[j]), int(C[j + 1]))
    return out


def les_segments(R, C) -> list[tuple]:
    """Chaque bande coupée aux nœuds du treillis : `(sens, centre, de, à)`."""
    return ([("rangees", int(r), int(C[j]), int(C[j + 1])) for r in R for j in range(len(C) - 1)]
            + [("colonnes", int(c), int(R[i]), int(R[i + 1])) for c in C for i in range(len(R) - 1)])


def la_place(coins, combien: int) -> bool:
    """Une cellule a la place d'un niveau de plus quand chacun de ses côtés a un détour."""
    return les_detours(coins, combien) is not None


def analyser_un_niveau(pas: dict, R, C, regle: str, graine: int, tirages: int, replicats: int,
                       garantie: float = GARANTIE, demi: float = DEMI_PAS_EN_VOXELS,
                       a_recomposer: dict | None = None) -> dict:
    """Un niveau : les trous franchis par la règle de `225`, les neuf cellules, leur épreuve et son étalon — pur.

    `pas` : `{(sens, centre): {ligne: {couture: pas}}}` pour les huit bandes du treillis.
    """
    attendues = {("rangees", int(r)) for r in R} | {("colonnes", int(c)) for c in C}
    if set(pas) != attendues:
        return {"decidable": False, "raison": "les bandes analysées ne sont pas les huit du treillis"}
    cons = {k: le_consensus(p) for k, p in pas.items()}
    trous, couverture = [], {}
    for (sens, centre), c_ in sorted(cons.items()):
        de, a = (C[0], C[-1]) if sens == "rangees" else (R[0], R[-1])
        tr = les_trous(c_, de, a)
        couverture[f"{sens}_{centre}"] = {"les_coutures_du_perimetre": int(a - de),
                                          "les_coutures_sans_consensus": [s for t in tr for s in range(t[0], t[0] + t[1])]}
        trous += [{"le_sens": sens, "le_centre": int(centre), "le_debut": int(t[0]), "la_longueur": int(t[1])}
                  for t in tr]
    remplies = {}
    if trous:
        rem = le_remplissage(regle, pas, trous)
        if rem is None:
            return {"decidable": False, "raison": f"la règle de `225`, {regle}, ne franchit pas les trous du niveau"}
        for k, v_ in rem.items():
            cons[k] = {**cons[k], **v_}
            remplies[f"{k[0]}_{k[1]}"] = {str(s): round(float(x), 4) for s, x in sorted(v_.items())}
    segs = les_segments(R, C)
    pas_seg = {d: [float(cons[(d[0], d[1])][s]) for s in range(d[2], d[3])] for d in segs}
    sommes = {d: la_somme(cons[(d[0], d[1])], d[2], d[3])[0] for d in segs}
    cellules = les_cellules(R, C)
    fermetures = {n: round(float(la_fermeture(sommes, co, segs)), 4) for n, co in cellules.items()}
    ep = lepreuve(pas_seg, cellules, segs, tirages, graine, garantie, demi)
    theta = le_theta_dune_autocorrelation(lautocorrelation_commune(pas_seg.values()) or 0.0)
    longueurs = {d: len(p) for d, p in pas_seg.items()}
    dispersions = {d: float(np.std(p)) for d, p in pas_seg.items()}
    # ⚠⚠⚠ LE SEUIL DE LA FAMILLE SE DÉRIVE D'UN ÉTALON, et un second étalon, indépendant, le vérifie.
    sf = le_seuil_de_la_famille(longueurs, dispersions, cellules, segs, theta, replicats, tirages, graine, garantie)
    tau = sf["le_seuil"]
    parts = {n: float(x["la_part_du_nul_sous_la_fermeture"]) for n, x in ep["par_rectangle"].items()}
    sortent = sorted(n for n, x in parts.items() if tau is not None and x >= tau)
    et = les_etalons_de_la_famille(longueurs, dispersions, cellules, segs, theta, replicats, tirages, graine, tau,
                                   garantie)
    partage = {"le_seuil": round(le_seuil(len(cellules), garantie), 4),
               "les_cellules_qui_sortent": les_boucles_qui_sortent(ep["par_rectangle"], garantie),
               "letalon": et["au_seuil_partage"]}
    return {"decidable": True, "le_treillis": {"rangees": [int(r) for r in R], "colonnes": [int(c) for c in C]},
            "la_couverture_du_consensus": couverture, "les_coutures_remplies": remplies,
            "les_cellules": {n: {"les_coins": [[co[0], co[2]], [co[1], co[3]]],
                                 "la_fermeture_en_voxels": fermetures[n], **ep["par_rectangle"][n]}
                             for n, co in cellules.items()},
            "la_boucle_entiere_en_voxels": round(float(la_fermeture(sommes, (R[0], R[-1], C[0], C[-1]), segs)), 4),
            "le_seuil_de_la_famille": sf, "les_cellules_qui_sortent": sortent, "letalon": et["au_seuil_de_la_famille"],
            "le_seuil_partage_declare_dabord": partage,
            "les_recompositions": {n: round(float(la_fermeture(sommes, co, segs)), 4)
                                   for n, co in (a_recomposer or {}).items()}}


# ─────────────────────────────── le seuil de la famille ───────────────────────────────

def _les_matieres(longueurs: dict, dispersions: dict, theta: float, graine: int, i: int) -> dict:
    """Des demi-côtés indépendants fabriqués, au `θ`, aux longueurs et aux dispersions lues — ceux de `227`."""
    echelle = float(np.sqrt(1.0 + float(theta) ** 2))
    return {d: une_serie_dependante(theta, int(n), int(graine) + 1000 * i + 7 * j) * float(dispersions[d]) / echelle
            for j, (d, n) in enumerate(sorted(longueurs.items()))}


def le_seuil_de_la_famille(longueurs: dict, dispersions: dict, cellules: dict, segs, theta: float,
                           calibrations: int, tirages: int, graine: int, garantie: float = GARANTIE) -> dict:
    """Le plus petit seuil de part que la plus forte cellule de demi-côtés indépendants n'atteint que dans au plus
    `garantie` des calibrations — ou rien, si trop d'entre elles atteignent déjà le haut de l'échelle.

    ⚠⚠ Dérivé sur ses PROPRES tirages, jamais sur ceux de l'étalon qui le vérifie.
    """
    maxima, base = [], int(graine) + 300000
    for i in range(int(calibrations)):
        mat = _les_matieres(longueurs, dispersions, theta, base, i)
        ep = lepreuve(mat, cellules, segs, tirages, int(graine) + 5 * i + 3, garantie)
        maxima.append(max(float(x["la_part_du_nul_sous_la_fermeture"]) for x in ep["par_rectangle"].values()))
    m = np.asarray(maxima, dtype=float)
    grille = sorted({round(k / float(tirages), 4) for k in range(int(tirages) + 1)})
    tau = next((v for v in grille if float(np.mean(m >= v)) <= float(garantie)), None)
    avant = [v for v in grille if tau is not None and v < tau]
    return {"le_seuil": tau, "les_calibrations": int(calibrations), "la_graine_des_calibrations": base,
            "la_part_des_maxima_au_seuil": (round(float(np.mean(m >= tau)), 4) if tau is not None else None),
            "la_part_des_maxima_un_cran_dessous": (round(float(np.mean(m >= avant[-1])), 4) if avant else None),
            "la_mediane_des_maxima": round(float(np.median(m)), 4),
            "la_part_des_maxima_au_haut_de_lechelle": round(float(np.mean(m >= 1.0)), 4)}


def les_etalons_de_la_famille(longueurs: dict, dispersions: dict, cellules: dict, segs, theta: float,
                              replicats: int, tirages: int, graine: int, tau, garantie: float = GARANTIE) -> dict:
    """Sur des demi-côtés indépendants — les tirages de l'étalon de `227`, pas ceux du seuil —, à quel taux une
    cellule sort-elle, au seuil de la famille et au seuil partagé ?"""
    oui_f = oui_p = 0
    sp, base = le_seuil(len(cellules), garantie), int(graine) + 200000
    for i in range(int(replicats)):
        mat = _les_matieres(longueurs, dispersions, theta, base, i)
        ep = lepreuve(mat, cellules, segs, tirages, int(graine) + 5 * i + 2, garantie)
        parts = [float(x["la_part_du_nul_sous_la_fermeture"]) for x in ep["par_rectangle"].values()]
        oui_f += int(tau is not None and max(parts) >= tau)
        oui_p += int(max(parts) >= sp)
    borne = float(garantie) + 2.0 * float(np.sqrt(garantie * (1.0 - garantie) / float(replicats)))

    def _e(oui):  # noqa: E306
        t = oui / float(replicats)
        return {"le_theta": round(float(theta), 4), "les_replicats": int(replicats), "tirages": int(tirages),
                "la_graine_des_replicats": base,
                "combien_designent": int(oui), "le_taux": round(t, 4), "la_borne": round(borne, 4),
                "elle_tient_sa_garantie": bool(t <= borne)}
    return {"au_seuil_de_la_famille": {**_e(oui_f), "elle_tient_sa_garantie": bool(tau is not None
                                                                                   and oui_f / float(replicats) <= borne)},
            "au_seuil_partage": _e(oui_p)}


# ─────────────────────────────── la procédure ───────────────────────────────

def derouler(depart, registre: list[dict], combien: int, regle: str, graine: int, tirages: int, replicats: int,
             a_recomposer=None) -> dict:
    """La procédure entière, niveau par niveau, jusqu'à ce qu'elle s'arrête — ou les bandes qui lui manquent.

    `a_recomposer(R, C)` rend les boucles publiées à recomposer sur le treillis du premier niveau.
    """
    niveaux, a_lire, file_ = [], [], [(tuple(int(x) for x in depart), 1, "départ")]
    while file_:
        coins, prof, nom = file_.pop(0)
        d = les_detours(coins, combien)
        base = {"la_profondeur": prof, "la_cellule_de_depart": nom, "les_coins": [int(x) for x in coins]}
        if d is None:
            niveaux.append({**base, "decidable": False, "raison": "un côté n'a pas la place d'un détour"})
            continue
        R, C = le_treillis_dun_niveau(coins, d)
        voulues = les_bandes_voulues(R, C, combien)
        pas, manquent = {}, []
        for b in voulues:
            e = la_bande(registre, b["le_sens"], b["le_centre"], b["de"], b["a"], combien)
            if e is None:
                manquent.append(b)
            else:
                pas[(b["le_sens"], b["le_centre"])] = e["pas"]
        if manquent:
            a_lire += manquent
            niveaux.append({**base, "les_detours": d, "decidable": False, "raison": "des bandes manquent",
                            "les_bandes_qui_manquent": [b["cle"] for b in manquent]})
            continue
        x = analyser_un_niveau(pas, R, C, regle, graine, tirages, replicats,
                               a_recomposer=(a_recomposer(R, C) if (a_recomposer and prof == 1) else None))
        niveaux.append({**base, "les_detours": d, "les_sources_des_bandes": {
            f"{b['le_sens']}_{b['le_centre']}": la_bande(registre, b["le_sens"], b["le_centre"], b["de"], b["a"],
                                                         combien)["la_source"] for b in voulues}, **x})
        if not x.get("decidable") or not x["letalon"]["elle_tient_sa_garantie"]:
            continue
        for n in x["les_cellules_qui_sortent"]:
            co = tuple(les_cellules(R, C)[n])
            if la_place(co, combien):
                file_.append((co, prof + 1, n))
    return {"les_niveaux": niveaux, "les_bandes_a_lire": a_lire}


def _ce_qui_reste(premier: dict) -> str:
    """Les cinq issues, EXCLUSIVES — jugées au premier niveau ; un seuil absent, puis un étalon qui ne tient pas,
    priment."""
    if premier["le_seuil_de_la_famille"]["le_seuil"] is None:
        return "LE SEUIL DE LA FAMILLE N'EXISTE PAS À CETTE RÉSOLUTION : LA PROCÉDURE NE DÉSIGNE RIEN"
    if not premier["letalon"]["elle_tient_sa_garantie"]:
        return ("LE SEUIL DE LA FAMILLE NE TIENT PAS SA GARANTIE SUR UN ÉTALON INDÉPENDANT : LA PROCÉDURE NE DÉSIGNE "
                "RIEN")
    s = premier["les_cellules_qui_sortent"]
    if not s:
        return ("AUCUNE CELLULE NE SORT DU BRUIT : SANS MAIN, LA GARANTIE SE PARTAGE ET LA PROCÉDURE S'ARRÊTE SANS RIEN "
                "DÉSIGNER")
    if set(s) <= set(LA_REGION_DE_230):
        return "SANS MAIN, LA PROCÉDURE RETROUVE LA RÉGION QUE `230` A DÉSIGNÉE"
    return "LA PROCÉDURE DÉSIGNE AUTRE CHOSE QUE `230`"


# ─────────────────────────────── la mesure ───────────────────────────────

def les_boucles_publiees(R, C) -> dict:
    """Les boucles de `227`, `229` et `230` que le treillis du premier niveau recompose, en coins."""
    r0, rh, rb, r1 = R
    c0, cg, cd, c1 = C
    return {"227 haut_gauche": (r0, r1, c0, c1), "229 haut_gauche": (r0, r1, c0, cg),
            "229 haut_droite": (r0, r1, cg, c1), "230 haut_gauche": (r0, rh, c0, cg), "230 haut_droite": (r0, rh, cg, c1)}


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, par227: dict | None = None,
            par228: dict | None = None, par229: dict | None = None, par230: dict | None = None, lire=None,
            replicats: int | None = None, tirages: int | None = None) -> dict:
    """La procédure, lisant ce qui lui manque jusqu'à s'arrêter — ou rejouée depuis sa lecture."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    par227 = ce_que_227_a_rendu() if par227 is None else par227
    par228 = les_lectures_publiees(CE_QUE_228_A_RENDU) if par228 is None else par228
    par229 = ce_que_229_a_rendu() if par229 is None else par229
    par230 = ce_que_230_a_rendu() if par230 is None else par230
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("227", par227),
                     ("228", par228), ("229", par229), ("230", par230)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    combien = len(par219["les_rangees"])
    depart = (par227["Rf"][0], par227["Rf"][1], par227["Cf"][0], par227["Cf"][1])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    rp_ = par224["replicats"] if replicats is None else int(replicats)
    registre = le_registre(par219, par223, par224, par227, par229, par230)
    if depuis is not None:
        lues = json.loads(Path(depuis).read_text()).get("les_bandes") or {}
    else:
        lues = {}
        while True:
            r = derouler(depart, registre + [_entree(x["le_sens"], x["le_centre"], x["les_lignes"], x["de"], x["a"],
                                                     _long(relire_une_bande(x)), f"lue {k}")
                                             for k, x in sorted(lues.items())],
                         combien, par225["la_regle"], g, t_, rp_)
            if not r["les_bandes_a_lire"]:
                break
            lu = lire_les_bandes(r["les_bandes_a_lire"], lues, lire=lire)
            if not lu.get("decidable"):
                return {**base, "decidable": False, "raison": lu.get("raison"), "les_bandes": lu.get("les_bandes")}
            lues = lu["les_bandes"]
    base.update({"graine": int(g), "tirages": t_, "replicats": rp_, "la_regle_de_225": par225["la_regle"],
                 "la_boucle_de_depart": [int(x) for x in depart], "les_bandes": lues})
    relues = {k: relire_une_bande(x) for k, x in lues.items()}
    reg = registre + [_entree(x["le_sens"], x["le_centre"], x["les_lignes"], x["de"], x["a"], _long(x), f"lue {k}")
                      for k, x in sorted(relues.items())]
    r = derouler(depart, reg, combien, par225["la_regle"], g, t_, rp_, les_boucles_publiees)
    if r["les_bandes_a_lire"]:
        return {**base, "decidable": False, "raison": "la lecture ne couvre pas ce que la procédure demande"}
    # ⚠⚠ La lecture est exactement ce que la procédure a demandé : ni moins, ni plus.
    voulues = {}
    reg0 = registre
    for n_ in r["les_niveaux"]:
        if "les_detours" not in n_:
            continue
        R, C = le_treillis_dun_niveau(n_["les_coins"], n_["les_detours"])
        for b in les_bandes_voulues(R, C, combien):
            if la_bande(reg0, b["le_sens"], b["le_centre"], b["de"], b["a"], combien) is None:
                voulues[b["cle"]] = b
    if sorted(lues) != sorted(voulues) or any(_la_definition(lues[k]) != _la_definition(voulues[k]) for k in lues):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des détours dérivés"}
    src = les_sources(par219, par223, par224, par227, par228)
    for nom, par in (("229", par229), ("230", par230)):
        for k, rel in sorted(par["relues"].items()):
            src[f"{nom} {k}"] = {"domaine": le_domaine(rel["le_sens"], rel["les_lignes"], rel["de"], rel["a"]),
                                 "pas": les_pas_dune_bande(rel)}
    nouvelles = {k: {"domaine": le_domaine(x["le_sens"], x["les_lignes"], x["de"], x["a"]),
                     "pas": les_pas_dune_bande(x)} for k, x in relues.items()}
    rep = la_reproduction_croisee(nouvelles, src) if nouvelles else {"decidable": True, "combien_de_coutures_relues": 0}
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    premier = r["les_niveaux"][0]
    if not premier.get("decidable"):
        return {**base, "decidable": False, "raison": f"le premier niveau : {premier.get('raison')}",
                "la_reproduction": rep}
    # ⚠⚠⚠ LA PROCÉDURE RETROUVE 229 ET 230 : leurs détours, et leurs boucles recomposées exactement.
    if (premier["les_detours"]["gauche"], premier["les_detours"]["haut"]) != (par229["le_detour"], par230["le_detour"]):
        return {**base, "decidable": False, "la_reproduction": rep,
                "raison": "les détours de gauche et du haut ne sont pas ceux de `229` et `230`"}
    publiees = {"227 haut_gauche": par227["les_fermetures"]["haut_gauche"],
                "229 haut_gauche": par229["les_fermetures"]["haut_gauche"],
                "229 haut_droite": par229["les_fermetures"]["haut_droite"],
                "230 haut_gauche": par230["les_fermetures"]["haut_gauche"],
                "230 haut_droite": par230["les_fermetures"]["haut_droite"]}
    for n, L in premier["les_recompositions"].items():
        if L != publiees[n]:
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"la boucle {n} recomposée ({L}) ne retombe pas sur sa tranche"}
    return {**base, "decidable": True, "la_reproduction": rep, "les_boucles_publiees": publiees,
            "les_niveaux": r["les_niveaux"],
            "le_verdict": {"les_cellules_qui_sortent_au_premier_niveau": premier["les_cellules_qui_sortent"],
                           "letalon_tient": bool(premier["letalon"]["elle_tient_sa_garantie"]),
                           "combien_de_niveaux": len(r["les_niveaux"]),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(premier)}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp.get('par_croisement')}, écart "
          f"{rp.get('lecart_le_plus_grand')}")
    for n_ in r["les_niveaux"]:
        print(f"niveau {n_['la_profondeur']} · {n_['la_cellule_de_depart']} · coins {n_['les_coins']} · détours "
              f"{n_.get('les_detours')} · {n_.get('raison', '')}")
        if not n_.get("decidable"):
            continue
        print(f"  sources {n_['les_sources_des_bandes']}")
        print(f"  remplies {n_['les_coutures_remplies']} · boucle entière {n_['la_boucle_entiere_en_voxels']}")
        for c, x in n_["les_cellules"].items():
            print(f"  {c:>14} · L {x['la_fermeture_en_voxels']:>9} · nul {x['la_fermeture_mediane_du_nul_en_valeur_absolue']}"
                  f" · part {x['la_part_du_nul_sous_la_fermeture']}")
        e = n_["letalon"]
        print(f"  seuil de la famille {n_['le_seuil_de_la_famille']} · sortent {n_['les_cellules_qui_sortent']} · "
              f"étalon {e['combien_designent']}/{e['les_replicats']} = {e['le_taux']} (borne {e['la_borne']}, "
              f"θ {e['le_theta']})")
        sp = n_["le_seuil_partage_declare_dabord"]
        print(f"  déclaré d'abord : seuil {sp['le_seuil']} · sortent {sp['les_cellules_qui_sortent']} · étalon "
              f"{sp['letalon']['combien_designent']}/{sp['letalon']['les_replicats']}")
        print(f"  recompositions {n_['les_recompositions']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import tempfile
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

    def _ok(f):
        try:
            return bool(f())
        except Exception:  # noqa: BLE001
            return False

    # ── ce qui est dérivé
    d = les_detours((99, 148, 71, 106), 5)
    v("★★★★ les quatre détours de la boucle fine de 227, sans choisir de côté : 106, 141, 78, 99",
      d == {"haut": 106, "bas": 141, "gauche": 78, "droite": 99}, str(d))
    v("★★★★ deux d'entre eux sont ceux de 229 et 230, retrouvés sans qu'on les indique",
      _ok(lambda: (d["gauche"], d["haut"]) == (78, 106)))
    v("★★★ une boucle trop étroite n'a pas la place de ses détours",
      les_detours((99, 106, 78, 106), 5) is None and not la_place((99, 106, 78, 106), 5)
      and la_place((106, 141, 78, 99), 5), str(les_detours((106, 141, 78, 99), 5)))
    v("★★★ deux détours opposés qui se toucheraient : pas de place",
      les_detours((0, 16, 0, 60), 5) is None, str(les_detours((0, 16, 0, 60), 5)))
    e0 = _entree("rangees", 50, les_rangees_a_lire(50, 5), 0, 10, {}, "x")
    v("★★★ une bande publiée qui ne couvre pas l'étendue voulue n'est pas reprise",
      la_bande([e0], "rangees", 50, 0, 20, 5) is None and la_bande([e0], "rangees", 50, 2, 9, 5) is e0
      and la_bande([e0], "rangees", 50, 2, 9, 3) is None)
    try:
        R, C = le_treillis_dun_niveau((99, 148, 71, 106), d)
    except Exception:  # noqa: BLE001
        R, C = [0, 1, 2, 3], [0, 1, 2, 3]
    v("★★★★ le treillis d'un niveau : quatre rangées, quatre colonnes", R == [99, 106, 141, 148]
      and C == [71, 78, 99, 106], str((R, C)))
    ce = les_cellules(R, C)
    v("★★★★ neuf cellules qui pavent la boucle, le centre fait de détours seuls",
      len(ce) == 9 and ce["centre"] == (106, 141, 78, 99) and ce["haut_gauche"] == (99, 106, 71, 78)
      and ce["bas_droite"] == (141, 148, 99, 106))
    bv = les_bandes_voulues(R, C, 5)
    v("★★★ huit bandes voulues, chacune sur l'étendue de la boucle",
      len(bv) == 8 and bv[1] == {"cle": "rangees_106_71_106", "le_sens": "rangees", "le_centre": 106,
                                 "les_lignes": [104, 105, 106, 107, 108], "de": 71, "a": 106}
      and bv[6]["de"] == 99 and bv[6]["a"] == 148, str(bv[:2]))
    v("★★★ les segments : chaque bande coupée aux nœuds", len(les_segments(R, C)) == 24)
    v("★★★★ la garantie se partage entre les neuf cellules", abs(le_seuil(9) - (1.0 - GARANTIE / 9)) < 1e-12)
    bp = les_boucles_publiees(R, C)
    v("★★★★ le treillis recompose la boucle de 227, les deux boucles du haut de 229 et les deux de 230",
      bp == {"227 haut_gauche": (99, 148, 71, 106), "229 haut_gauche": (99, 148, 71, 78),
             "229 haut_droite": (99, 148, 78, 106), "230 haut_gauche": (99, 106, 71, 78),
             "230 haut_droite": (99, 106, 78, 106)}, str(bp))

    def _pr(ss, tient=True, tau=0.999):  # noqa: E306
        return {"letalon": {"elle_tient_sa_garantie": tient}, "les_cellules_qui_sortent": ss,
                "le_seuil_de_la_famille": {"le_seuil": tau}}
    iss = {_ce_qui_reste(_pr(s_, t_, u_)) for s_ in ([], ["haut_milieu"], ["haut_milieu", "haut_droite"], ["centre"])
           for t_ in (True, False) for u_ in (0.999, None)}
    v("★★★★ cinq issues distinctes, un seuil absent prime, puis un étalon qui ne tient pas",
      len(iss) == 5 and _ce_qui_reste(_pr(["centre"], False)) == _ce_qui_reste(_pr([], False))
      and _ce_qui_reste(_pr(["centre"], False, None)) == _ce_qui_reste(_pr([], True, None))
      and _ce_qui_reste(_pr([], True, None)) != _ce_qui_reste(_pr([], False))
      and _ce_qui_reste(_pr(["haut_droite"])) == _ce_qui_reste(_pr(["haut_milieu"]))
      != _ce_qui_reste(_pr(["centre"]))
      and _ce_qui_reste(_pr(["haut_milieu", "haut_droite"])) == _ce_qui_reste(_pr(["haut_droite"]))
      and _ce_qui_reste(_pr(["haut_milieu", "centre"])) == _ce_qui_reste(_pr(["centre"])))

    # ── un niveau, sur des pas fabriqués
    g = np.random.default_rng(17)
    R2, C2 = [0, 8, 32, 40], [0, 8, 32, 40]

    def _bandes(erreur: dict | None = None, sd: float = 1.0):  # noqa: E306
        out = {}
        for sens, centres, x in (("rangees", R2, 0.2), ("colonnes", C2, 0.15)):
            for centre in centres:
                de, a_ = (C2[0], C2[-1]) if sens == "rangees" else (R2[0], R2[-1])
                out[(sens, centre)] = {l_: {s: x + float(g.normal(0.0, sd)) for s in range(de, a_)}
                                       for l_ in range(centre - 2, centre + 3)}
        for (sens, centre), (de, a_, e) in (erreur or {}).items():
            for l_ in out[(sens, centre)]:
                for s in range(de, a_):
                    out[(sens, centre)][l_][s] += e
        return out
    a = _sur(analyser_un_niveau, _bandes(), R2, C2, "le_maillage", 3, 999, 200, a_recomposer={"tout": (0, 40, 0, 40)})
    v("★★★ un niveau est décidable sur des pas fabriqués", a.get("decidable"), str(a.get("raison")))
    v("★★★★ la boucle entière est la somme de ses neuf cellules, et sa recomposition",
      _ok(lambda: abs(sum(x["la_fermeture_en_voxels"] for x in a["les_cellules"].values())
                      - a["la_boucle_entiere_en_voxels"]) < 1e-3
          and a["les_recompositions"]["tout"] == a["la_boucle_entiere_en_voxels"]))
    v("★★★★ sans erreur, aucune cellule ne sort au seuil de la famille, et son étalon indépendant tient",
      _ok(lambda: not a["les_cellules_qui_sortent"] and a["letalon"]["elle_tient_sa_garantie"]
          and a["le_seuil_de_la_famille"]["le_seuil"] is not None), str((a.get("le_seuil_de_la_famille"),
                                                                        a.get("letalon"))))
    v("★★★★ ⚠ ce qui a fait remplacer le seuil déclaré d'abord : sur ces pas indépendants, l'étalon de 227 ne tient pas "
      "le seuil partagé 1 − 0,05/9",
      _ok(lambda: a["le_seuil_partage_declare_dabord"]["le_seuil"] == round(1 - 0.05 / 9, 4)
          and not a["le_seuil_partage_declare_dabord"]["letalon"]["elle_tient_sa_garantie"]),
      str(a.get("le_seuil_partage_declare_dabord")))
    v("★★★★ le seuil de la famille est le plus petit que les maxima des calibrations n'atteignent qu'au plus 0,05",
      _ok(lambda: a["le_seuil_de_la_famille"]["la_part_des_maxima_au_seuil"] <= 0.05
          and a["le_seuil_de_la_famille"]["la_part_des_maxima_un_cran_dessous"] > 0.05),
      str(a.get("le_seuil_de_la_famille")))
    v("★★★★ le seuil se dérive sur d'autres tirages que ceux de l'étalon qui le vérifie",
      _ok(lambda: a["le_seuil_de_la_famille"]["la_graine_des_calibrations"] != a["letalon"]["la_graine_des_replicats"]))
    v("★★★ le seuil de la famille est plus haut que le seuil partagé, et une part de l'échelle",
      _ok(lambda: round(1 - 0.05 / 9, 4) <= a["le_seuil_de_la_famille"]["le_seuil"] <= 1.0
          and a["le_seuil_de_la_famille"]["le_seuil"] in {round(k / 999, 4) for k in range(1000)}),
      str(a.get("le_seuil_de_la_famille")))
    ah = _sur(analyser_un_niveau, _bandes({("rangees", 0): (8, 32, 0.8)}, 0.25), R2, C2, "le_maillage", 3, 999, 200)
    v("★★★★ une erreur partagée par les lignes d'un côté, sur un tronçon : la cellule qui la longe sort, seule",
      _ok(lambda: ah["les_cellules_qui_sortent"] == ["haut_milieu"]), str(ah.get("les_cellules_qui_sortent")))
    ac = _sur(analyser_un_niveau, _bandes({("rangees", 8): (8, 32, 0.8), ("rangees", 0): (8, 32, 0.8)}, 0.25),
              R2, C2, "le_maillage", 3, 999, 200)
    v("★★★★ la même erreur partagée par le détour : la cellule du bord ne la voit pas, celle du centre la porte",
      _ok(lambda: "haut_milieu" not in ac["les_cellules_qui_sortent"] and "centre" in ac["les_cellules_qui_sortent"]),
      str(ac.get("les_cellules_qui_sortent")))
    bt = _bandes()
    for l_ in (6, 7, 8):
        for s in (20, 21):
            del bt[("rangees", 8)][l_][s]
    at = _sur(analyser_un_niveau, bt, R2, C2, "le_maillage", 3, 999, 200)
    v("★★★★ un trou de majorité est franchi par la règle de 225, et nommé avant d'être rempli",
      _ok(lambda: at["la_couverture_du_consensus"]["rangees_8"]["les_coutures_sans_consensus"] == [20, 21]
          and at["les_coutures_remplies"] == {"rangees_8": {"20": 0.0, "21": 0.0}}), str(at.get("raison")))
    v("★★★ un trou que la règle ne franchit pas rend le niveau indécidable",
      "ne franchit pas" in str(_sur(analyser_un_niveau, {k: ({l_: {} for l_ in p} if k == ("rangees", 8) else p)
                                                          for k, p in _bandes().items()},
                                    R2, C2, "les_lignes_presentes", 3, 999, 200).get("raison")))
    v("★★★ des bandes qui ne sont pas les huit du treillis sont refusées",
      "pas les huit" in str(_sur(analyser_un_niveau, {k: p for k, p in _bandes().items() if k != ("rangees", 8)},
                                 R2, C2, "le_maillage", 3, 999, 200).get("raison")))

    # ── la procédure, sur un registre fabriqué : elle lit ce qui manque, descend, et s'arrête
    Rg, Cg = [0, 60], [0, 60]
    ent = []
    gg = np.random.default_rng(23)
    lig = {}

    def _fab_bande(sens, centre, de, a_, err=None):  # noqa: E306
        p = {l_: {s: 0.1 + float(gg.normal(0.0, 0.25)) for s in range(de, a_)} for l_ in les_rangees_a_lire(centre, 5)}
        for (x0, x1, e) in (err or []):
            for l_ in p:
                for s in range(x0, x1):
                    p[l_][s] += e
        return _entree(sens, centre, les_rangees_a_lire(centre, 5), de, a_, p, f"fab {sens} {centre}")
    ent += [_fab_bande("rangees", r, 0, 60, [(8, 52, 0.8)] if r == 0 else None) for r in Rg]
    ent += [_fab_bande("colonnes", c, 0, 60) for c in Cg]
    r1 = _sur(derouler, (0, 60, 0, 60), ent, 5, "le_maillage", 3, 999, 200)
    v("★★★★ la procédure demande ses quatre détours quand ils manquent, et rien d'autre",
      _ok(lambda: sorted(b["cle"] for b in r1["les_bandes_a_lire"])
          == sorted(["rangees_7_0_60", "rangees_53_0_60", "colonnes_7_0_60", "colonnes_53_0_60"])),
      str([b["cle"] for b in r1.get("les_bandes_a_lire", [])]))
    for b in r1.get("les_bandes_a_lire", []):
        ent.append(_fab_bande(b["le_sens"], b["le_centre"], b["de"], b["a"]))
    r2 = _sur(derouler, (0, 60, 0, 60), ent, 5, "le_maillage", 3, 999, 200)
    n1 = r2["les_niveaux"][0] if r2.get("les_niveaux") else {}
    v("★★★★ au premier niveau, la cellule qui longe l'erreur sort du bruit", _ok(lambda: n1["decidable"]
      and n1["les_cellules_qui_sortent"] == ["haut_milieu"]), str(n1.get("les_cellules_qui_sortent")))
    v("★★★★ ... et la procédure s'arrête : la cellule qui sort n'a pas la place d'un détour",
      _ok(lambda: len(r2["les_niveaux"]) == 1 and not r2["les_bandes_a_lire"]))
    ent3 = [e for e in ent if not (e["le_sens"] == "rangees" and e["le_centre"] in (0, 7))]
    ent3 += [_fab_bande("rangees", 0, 0, 60), _fab_bande("rangees", 7, 0, 60, [(7, 53, 0.8)])]
    r3n = _sur(derouler, (0, 60, 0, 60), ent3, 5, "le_maillage", 3, 999, 200)
    n3n = r3n["les_niveaux"][0] if r3n.get("les_niveaux") else {}
    v("★★★★ ⚠ à sept coutures du côté — là où tombe tout détour —, le seuil de la famille touche le haut de "
      "l'échelle, et la procédure ne descend pas",
      _ok(lambda: n3n["le_seuil_de_la_famille"]["le_seuil"] in (1.0, None) and len(r3n["les_niveaux"]) == 1
          and not r3n["les_bandes_a_lire"]), str(n3n.get("le_seuil_de_la_famille")))
    # la descente elle-même, son câblage seul : l'étalon forcé à tenir
    vrai_ = globals()["les_etalons_de_la_famille"]

    def _tient(*a_, **k_):  # noqa: E306
        x_ = vrai_(*a_, **k_)
        return {**x_, "au_seuil_de_la_famille": {**x_["au_seuil_de_la_famille"], "elle_tient_sa_garantie": True}}
    globals()["les_etalons_de_la_famille"] = _tient
    try:
        r3 = _sur(derouler, (0, 60, 0, 60), ent3, 5, "le_maillage", 3, 999, 200)
    finally:
        globals()["les_etalons_de_la_famille"] = vrai_
    n3 = r3["les_niveaux"][0] if r3.get("les_niveaux") else {}
    v("★★★★ une erreur du détour lui-même : c'est le centre qui sort, et la procédure y descend en demandant ses détours",
      _ok(lambda: "centre" in n3["les_cellules_qui_sortent"]
          and any(b["cle"].startswith("rangees_14_") for b in r3["les_bandes_a_lire"])
          and r3["les_niveaux"][-1]["la_cellule_de_depart"] == "centre"),
      str((n3.get("les_cellules_qui_sortent"), n3.get("le_seuil_de_la_famille"), n3.get("letalon"),
           [b["cle"] for b in r3.get("les_bandes_a_lire", [])])))
    vrai = globals()["les_etalons_de_la_famille"]

    def _faux(*a_, **k_):  # noqa: E306
        x_ = vrai(*a_, **k_)
        return {**x_, "au_seuil_de_la_famille": {**x_["au_seuil_de_la_famille"], "elle_tient_sa_garantie": False}}
    globals()["les_etalons_de_la_famille"] = _faux
    try:
        r4 = _sur(derouler, (0, 60, 0, 60), ent3, 5, "le_maillage", 3, 999, 200)
    finally:
        globals()["les_etalons_de_la_famille"] = vrai
    v("★★★★ la procédure ne descend pas quand l'étalon d'un niveau ne tient pas",
      _ok(lambda: "centre" in r4["les_niveaux"][0]["les_cellules_qui_sortent"] and len(r4["les_niveaux"]) == 1
          and not r4["les_bandes_a_lire"]), str(r4.get("les_niveaux", [{}])[-1].get("la_cellule_de_depart")))

    # ── la mesure, sur une lecture fabriquée qui retombe : copiée des sources là où elles lisent
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    p227, p228 = ce_que_227_a_rendu(), les_lectures_publiees(CE_QUE_228_A_RENDU)
    p229, p230 = ce_que_229_a_rendu(), ce_que_230_a_rendu()
    v("★★★ 230 se relit, et son détour est la rangée 106", p230.get("decidable") and p230.get("le_detour") == 106,
      str(p230.get("raison")))
    src = les_sources(p219, p223, p224, p227, p228)
    for nom, par in (("229", p229), ("230", p230)):
        for k, rel in sorted(par["relues"].items()):
            src[f"{nom} {k}"] = {"domaine": le_domaine(rel["le_sens"], rel["les_lignes"], rel["de"], rel["a"]),
                                 "pas": les_pas_dune_bande(rel)}

    def _fabrique(b):  # noqa: E306
        gf = np.random.default_rng(b["le_centre"])
        dom = le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"])
        pas_ = {}
        for f in ("h", "v"):
            pas_[f] = {}
            for cle in sorted(dom[f]):
                x = next((S_["pas"][f][cle] for S_ in src.values() if f in S_["pas"]
                          and cle in S_["domaine"].get(f, ()) and cle in S_["pas"][f]), None)
                vu = any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in src.values())
                if x is not None:
                    pas_[f][cle] = x
                elif not vu:
                    pas_[f][cle] = round(float(gf.normal(0.0, 1.0)), 4)
        le_long_f, trav_f = (("h", "v") if b["le_sens"] == "rangees" else ("v", "h"))
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if b["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": {}}
    pars = (p219, p223, p224, p225, p227, p228, p229, p230)
    m = _sur(mesurer, None, *pars, _fabrique, 20, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière, et la procédure retrouve 229 et 230",
      m.get("decidable") and m["les_niveaux"][0]["les_detours"] == {"haut": 106, "bas": 141, "gauche": 78, "droite": 99}
      and m["les_niveaux"][0]["les_recompositions"] == m["les_boucles_publiees"], str(m.get("raison")))
    v("★★★★ seules les deux bandes qui manquent sont lues : la colonne 99 et la rangée 141",
      _ok(lambda: sorted(m["les_bandes"]) == ["colonnes_99_99_148", "rangees_141_71_106"]), str(sorted(m.get("les_bandes") or {})))
    v("★★★★ les détours déjà publiés sont repris : 229 pour la colonne 78, 230 pour la rangée 106",
      _ok(lambda: m["les_niveaux"][0]["les_sources_des_bandes"]["colonnes_78"].startswith("229")
          and m["les_niveaux"][0]["les_sources_des_bandes"]["rangees_106"].startswith("230")))
    v("★★★ chaque bande lue est contrôlée par une source publiée",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]} == set(m["les_bandes"])))
    faux230 = copy.deepcopy(p230)
    faux230["les_fermetures"]["haut_droite"] += 1.0
    v("★★★★ une boucle de 230 qui ne retombe pas est refusée, par sa raison",
      "ne retombe pas sur sa tranche" in str(_sur(mesurer, None, p219, p223, p224, p225, p227, p228, p229, faux230,
                                                  _fabrique, 20, 49).get("raison")))
    faux229 = copy.deepcopy(p229)
    faux229["le_detour"] = 79
    v("★★★★ des détours qui ne sont pas ceux de 229 et 230 sont refusés",
      "ne sont pas ceux" in str(_sur(mesurer, None, p219, p223, p224, p225, p227, p228, faux229, p230,
                                     _fabrique, 20, 49).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, *pars, _decale, 20, 49).get("raison")))

    def _rejouer(lues):  # noqa: E306
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"les_bandes": lues}, f)
            chemin = Path(f.name)
        try:
            return mesurer(chemin, *pars, replicats=20, tirages=49)
        finally:
            chemin.unlink()
    v("★★★★ la mesure se rejoue à l'octet près depuis sa lecture publiée",
      _ok(lambda: json.dumps(_rejouer(m["les_bandes"]), ensure_ascii=False) == json.dumps(m, ensure_ascii=False)))
    v("★★★ une lecture à laquelle il manque une bande est refusée",
      "ne couvre pas" in str(_sur(_rejouer, {k: x for k, x in (m.get("les_bandes") or {}).items()
                                             if k.startswith("rangees")}).get("raison")))
    v("★★★ une lecture avec une bande de trop est refusée",
      "n'est pas celle des détours" in str(_sur(_rejouer, {**(m.get("les_bandes") or {}),
                                                          "rangees_120_71_106": {**next(iter((m.get("les_bandes") or {"x": {}}).values())),
                                                                                 "le_centre": 120}}).get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lire", type=Path, default=None)
    p.add_argument("--depuis", type=Path, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.lire:
        deja = (json.loads(a.lire.read_text()).get("les_bandes") or {}) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)
        pars = (ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu(),
                ce_que_227_a_rendu(), les_lectures_publiees(CE_QUE_228_A_RENDU), ce_que_229_a_rendu(),
                ce_que_230_a_rendu())
        for par in pars:
            if not par.get("decidable"):
                print(f"indécidable : {par.get('raison')}")
                return 1
        p219, p223, p224, p225, p227, p228, p229, p230 = pars
        combien = len(p219["les_rangees"])
        depart = (p227["Rf"][0], p227["Rf"][1], p227["Cf"][0], p227["Cf"][1])
        registre = le_registre(p219, p223, p224, p227, p229, p230)
        lues = dict(deja)
        while True:
            reg = registre + [_entree(x["le_sens"], x["le_centre"], x["les_lignes"], x["de"], x["a"],
                                      _long(relire_une_bande(x)), f"lue {k}") for k, x in sorted(lues.items())]
            r = derouler(depart, reg, combien, p225["la_regle"], p224["graine"], p224["tirages"], p224["replicats"])
            if not r["les_bandes_a_lire"]:
                break

            def ecrire(d_):  # noqa: E306
                a.lire.write_text(json.dumps({"les_bandes": d_}, ensure_ascii=False, indent=1))
                print(f"écrit : {a.lire} ({len(d_)} bandes)", flush=True)
            lu = lire_les_bandes(r["les_bandes_a_lire"], lues, ecrire)
            if not lu.get("decidable"):
                print(f"indécidable : {lu.get('raison')}")
                return 1
            lues = lu["les_bandes"]
        print(f"la procédure s'arrête : {len(r['les_niveaux'])} niveau(x), {len(lues)} bande(s) lue(s)")
        return 0
    r = mesurer(a.depuis)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
