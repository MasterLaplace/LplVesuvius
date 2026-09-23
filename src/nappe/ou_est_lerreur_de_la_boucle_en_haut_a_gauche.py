"""Où est l'erreur que porte la boucle en haut à gauche, et une boucle plus fine la désigne-t-elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE BANDE NOUVELLE NE SOIT LUE. Rien de neuf n'est regardé :
les bandes publiées par `219`, `223` et `224` couvrent déjà le bord du quadrant.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P72`. `226` a montré qu'ajuster toutes les boucles à la fois
répand l'erreur au lieu de la diluer, parce qu'elle est concentrée : la boucle en haut à gauche ferme à
−29,25 voxels quand les trois autres ferment à quelques voxels, et ses deux côtés extérieurs sont prédits à
la même erreur au signe près. Le treillis de `224` n'a qu'une boucle pour juger ces côtés.

## Les boucles fines, dérivées

Le quadrant — rangées 99 à 198, colonnes 71 à 142 — est coupé en quatre par une bande de rangées et une
bande de colonnes à mi-chemin de ses côtés : le milieu entier `(a + b) // 2`, soit la rangée 148 et la
colonne 106, cinq lignes chacune, par la fonction de `219`. Chaque bande nouvelle n'est lue que sur le
quadrant. Les quatre boucles fines ont pour côtés extérieurs des moitiés des côtés de la boucle en haut à
gauche, et pour côtés intérieurs les bandes nouvelles : la somme de leurs fermetures est la fermeture de la
boucle en haut à gauche, exactement.

⭐⭐ L'ANALYSE EST CELLE DE `224`, APPELÉE : sur le treillis fin, avec ses rangées 99, 148, 198 et ses
colonnes 71, 106, 142, elle rend les quatre boucles fines, leur « grand rectangle » — qui EST la boucle en
haut à gauche, et doit retomber sur la fermeture que `224` publie —, les contrôles nommés, et l'épreuve
contre des demi-côtés tirés indépendamment, avec son étalon.

## Ce qui contrôle la lecture

⚠⚠⚠ Chaque bande nouvelle croise des bandes publiées, et partout où deux lectures lisent la même couture —
les pas horizontaux ou verticaux, selon le sens — elles doivent retomber à l'arrondi, sur les mêmes coutures,
sinon la lecture est refusée par son nom. Une bande qui ne croise aucune couture publiée n'est pas
contrôlée, et elle est refusée aussi.

## Ce qui désigne, déclaré

Une boucle fine SORT DU BRUIT quand sa fermeture dépasse, en valeur absolue, ce que donnent des demi-côtés
tirés indépendamment par blocs dans au moins `1 − 0,05 / n` des tirages, `n` étant le nombre de boucles fines
fermées : la garantie, partagée entre elles. ⭐⭐⭐ L'ÉTALON DE CETTE RÈGLE : sur des demi-côtés indépendants
fabriqués — au `θ` dérivé, aux longueurs et aux dispersions lues —, la règle ne doit faire sortir une boucle
qu'au taux de sa garantie, à deux écarts-types binomiaux près ; sinon elle ne désigne rien.

## Les issues, exclusives

- aucune boucle fine ne sort du bruit : rien ne localise l'erreur au-delà de ce que le bruit ferait
  (⚠ l'issue déclarée disait « répartie », corrigée après la mesure : ne pas sortir du bruit ne dit pas
  qu'une erreur est répartie) ;
- une seule sort : elle désigne où l'erreur se trouve ;
- plusieurs sortent : l'erreur n'est pas une ;
- la règle de désignation ne tient pas sa garantie : elle ne désigne rien.

## ⚠⚠⚠ Ajouté après la lecture, et c'est dit

La déclaration n'avait pas prévu de trou de majorité dans les bandes fines. La lecture en montre un, et il
laisse deux boucles fines ouvertes. Il est FRANCHI PAR LA RÈGLE QUE `225` A RETENUE, lue dans sa mesure
publiée, jamais par une règle choisie ici ; et la mesure telle que déclarée, sans franchir, est publiée à
côté. Une boucle fine qui resterait ouverte après le franchissement rend la mesure indécidable : la question
porte sur les quatre.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle fine désigne une RÉGION, pas un côté — une boucle a
quatre côtés, et celle qui sort ne dit pas lequel porte l'erreur. Et le piège de `219` vaut : une boucle qui
désigne ne dit pas si c'est la matière ou la lecture qui se trompe.

Usage :
    uv run python src/nappe/ou_est_lerreur_de_la_boucle_en_haut_a_gauche.py --verifier
    uv run python src/nappe/ou_est_lerreur_de_la_boucle_en_haut_a_gauche.py --lire <lecture.json>
    uv run python src/nappe/ou_est_lerreur_de_la_boucle_en_haut_a_gauche.py --depuis <lecture.json> \\
        --json docs/mesures/ou_est_lerreur_de_la_boucle_en_haut_a_gauche.json
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
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition, analyser,  # noqa: E402
                                                          ce_que_223_a_rendu, lautocorrelation_commune,
                                                          lepreuve, les_boucles_declarees,
                                                          les_demi_cotes, lire_les_bandes,
                                                          relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import (ce_que_225_a_rendu,  # noqa: E402
                                                                   le_treillis)
from le_consensus_traverse_t_il_la_rangee import (le_consensus,  # noqa: E402
                                                  le_theta_dune_autocorrelation,
                                                  une_serie_dependante)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE  # noqa: E402
from les_boucles_se_ferment_elles import LA_TOLERANCE_DE_REPRODUCTION  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import (ce_que_224_a_rendu,  # noqa: E402
                                                       le_remplissage, les_trous_des_boucles)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

LA_BOUCLE = "haut_gauche"
LA_QUESTION_DECLAREE = ("où est l'erreur que porte la boucle en haut à gauche, et une boucle plus fine la "
                        "désigne-t-elle ?")
LA_MESURE_DECLAREE = ("les fermetures des quatre boucles fines du quadrant en haut à gauche, chacune contre "
                      "des demi-côtés tirés indépendamment ; une boucle sort du bruit au-delà de 1 − 0,05/n")


# ─────────────────────────────── ce qui est dérivé ───────────────────────────────

def le_treillis_fin(R, C, boucle: str = LA_BOUCLE) -> tuple[list[int], list[int]]:
    """Les rangées et les colonnes du treillis fin : les côtés de la boucle et leur milieu entier."""
    r0, r1, c0, c1 = les_boucles_declarees(R, C)[boucle]
    return [int(r0), (int(r0) + int(r1)) // 2, int(r1)], [int(c0), (int(c0) + int(c1)) // 2, int(c1)]


def les_bandes_fines(Rf, Cf, combien: int) -> list[dict]:
    """Les deux bandes nouvelles, lues sur le seul quadrant — au format des bandes de `224`."""
    return [{"cle": f"rangees_{Rf[1]}", "le_sens": "rangees", "le_centre": int(Rf[1]),
             "les_lignes": les_rangees_a_lire(Rf[1], combien), "de": int(Cf[0]), "a": int(Cf[2])},
            {"cle": f"colonnes_{Cf[1]}", "le_sens": "colonnes", "le_centre": int(Cf[1]),
             "les_lignes": les_rangees_a_lire(Cf[1], combien), "de": int(Rf[0]), "a": int(Rf[2])}]


# ─────────────────────────────── le contrôle de la lecture ───────────────────────────────

def le_domaine(sens: str, lignes, de: int, a: int) -> dict:
    """Les coutures qu'une bande lit, par famille : `h` (rangée, colonne de gauche), `v` (rangée du dessus,
    colonne). Une bande de rangées lit ses chunks de la colonne `de` à la colonne `a`, une bande de colonnes
    de la rangée `de` à la rangée `a`, bornes comprises."""
    L = [int(x) for x in lignes]
    if sens == "rangees":
        return {"h": {(r, c) for r in L for c in range(int(de), int(a))},
                "v": {(r, c) for r in L[:-1] for c in range(int(de), int(a) + 1)}}
    return {"v": {(r, c) for c in L for r in range(int(de), int(a))},
            "h": {(r, c) for r in range(int(de), int(a) + 1) for c in L[:-1]}}


def les_pas_dune_bande(relue: dict) -> dict:
    """Les pas d'une bande relue, par famille, `{(rangée, colonne): pas}`."""
    ll = {(int(a), int(b)): float(x[0]) for a, s in relue["le_long"].items() for b, x in s.items()}
    tt = {(int(r), int(c)): float(x[0]) for r, s in relue["en_travers"].items() for c, x in s.items()}
    if relue["le_sens"] == "rangees":
        return {"h": ll, "v": tt}
    return {"v": {(r, c): x for (c, r), x in ll.items()}, "h": tt}


def la_reproduction_croisee(nouvelles: dict, sources: dict,
                            tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """Partout où une bande nouvelle et une source publiée lisent la même couture, elles retombent. Sinon, refus.

    `nouvelles` et `sources` : `{nom: {"domaine": {famille: coutures}, "pas": {famille: {couture: pas}}}}`.
    ⚠⚠ LES MÊMES COUTURES DES DEUX CÔTÉS, sur l'intersection de ce qu'elles lisent ; et chaque bande nouvelle
    est contrôlée sur au moins une couture, sinon rien ne la contrôle.
    """
    par, ecarts = {}, []
    for n in sorted(nouvelles):
        N = nouvelles[n]
        vus = 0
        for s in sorted(sources):
            S = sources[s]
            for f in ("h", "v"):
                if f not in N["pas"] or f not in S["pas"]:
                    continue
                for cle in sorted(N["domaine"][f] & S["domaine"][f]):
                    chez_moi, chez_eux = cle in N["pas"][f], cle in S["pas"][f]
                    if chez_moi != chez_eux:
                        return {"decidable": False,
                                "raison": f"la couture {f} {cle} est lue par {n} et non par {s}, ou l'inverse"}
                    if not chez_moi:
                        continue
                    e = abs(N["pas"][f][cle] - S["pas"][f][cle])
                    if e > float(tolerance):
                        return {"decidable": False,
                                "raison": (f"la couture {f} {cle} de {n} ne retombe pas sur {s} (écart {e:.4g} "
                                           f"voxel) — deux lecteurs différents")}
                    ecarts.append(e)
                    vus += 1
                    par[f"{n}×{s}"] = par.get(f"{n}×{s}", 0) + 1
        if not vus:
            return {"decidable": False, "raison": f"la bande {n} ne croise aucune couture publiée"}
    return {"decidable": True, "combien_de_coutures_relues": len(ecarts), "par_croisement": par,
            "lecart_le_plus_grand": round(float(max(ecarts)), 6), "la_tolerance": float(tolerance)}


def les_sources_publiees(par219: dict, par223: dict, par224: dict) -> dict:
    """Ce que `219`, `223` et `224` ont publié, au format du contrôle : domaine lu et pas, par famille."""
    gy, gx = par224["la_grille"]
    out = {"219": {"domaine": {"h": le_domaine("rangees", par219["les_rangees"], 0, gx - 1)["h"]},
                   "pas": {"h": {(int(r), int(c)): float(x) for r, s in par219["les_pas_par_rangee"].items()
                                 for c, x in s.items()}}},
           "223": {"domaine": {"v": le_domaine("colonnes", par223["les_colonnes"], 0, gy - 1)["v"]},
                   "pas": {"v": {(int(r), int(c)): float(x) for c, s in par223["les_pas_par_colonne"].items()
                                 for r, x in s.items()}}}}
    for b in par224["bandes"]:
        rel = par224["relues"][b["cle"]]
        out[f"224 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                  "pas": les_pas_dune_bande(rel)}
    return out


# ─────────────────────────────── la désignation ───────────────────────────────

def le_seuil(n: int, garantie: float = GARANTIE) -> float:
    """`1 − garantie / n` : la garantie partagée entre les `n` boucles fines fermées."""
    return 1.0 - float(garantie) / max(1, int(n))


def les_boucles_qui_sortent(par_rectangle: dict, garantie: float = GARANTIE) -> list[str]:
    """Les boucles fines dont la fermeture dépasse le bruit seul dans au moins `1 − garantie / n` des tirages."""
    s = le_seuil(len(par_rectangle), garantie)
    return sorted(n for n, x in par_rectangle.items() if float(x["la_part_du_nul_sous_la_fermeture"]) >= s)


def sur_letalon(longueurs: dict, dispersions: dict, rectangles: dict, demi_cotes, theta: float,
                replicats: int, tirages: int, graine: int, garantie: float = GARANTIE) -> dict:
    """La règle de désignation fait-elle sortir une boucle, quand les demi-côtés SONT indépendants ?

    ⚠⚠⚠ LA RÉPONSE EST CONNUE : aucune boucle ne devrait sortir, sauf au taux de la garantie. Chaque
    demi-côté est une série à dépendance d'un pas, au `θ` dérivé, à la longueur et à la dispersion lues.
    """
    oui = 0
    echelle = float(np.sqrt(1.0 + float(theta) ** 2))
    for i in range(int(replicats)):
        matiere = {d: une_serie_dependante(theta, int(n), int(graine) + 200000 + 1000 * i + 7 * j)
                   * float(dispersions[d]) / echelle for j, (d, n) in enumerate(sorted(longueurs.items()))}
        e = lepreuve(matiere, rectangles, demi_cotes, tirages, int(graine) + 5 * i + 2, garantie)
        oui += int(bool(les_boucles_qui_sortent(e["par_rectangle"], garantie)))
    taux = oui / float(replicats)
    borne = float(garantie) + 2.0 * float(np.sqrt(garantie * (1.0 - garantie) / float(replicats)))
    return {"decidable": True, "le_theta": round(float(theta), 4), "les_replicats": int(replicats),
            "tirages": int(tirages), "combien_designent": int(oui), "le_taux": round(taux, 4),
            "la_borne": round(borne, 4), "elle_tient_sa_garantie": bool(taux <= borne)}


def _ce_qui_reste(sortent: list[str], tient: bool) -> str:
    """Les quatre issues, EXCLUSIVES — et une règle qui ne tient pas sa garantie ne désigne rien."""
    if not tient:
        return "LA RÈGLE DE DÉSIGNATION NE TIENT PAS SA GARANTIE : ELLE NE DÉSIGNE RIEN"
    if not sortent:
        # ⚠ Corrigé après la mesure, et c'est dit : l'issue déclarée disait l'erreur « répartie ». Aucune boucle
        # qui ne sort du bruit ne dit qu'elle est répartie — seulement que rien ne la localise au-delà du bruit.
        return ("AUCUNE BOUCLE FINE NE SORT DU BRUIT : RIEN NE LOCALISE L'ERREUR DE LA BOUCLE EN HAUT À GAUCHE "
                "AU-DELÀ DE CE QUE LE BRUIT FERAIT")
    if len(sortent) == 1:
        return f"UNE SEULE BOUCLE FINE SORT DU BRUIT, ET ELLE DÉSIGNE OÙ EST L'ERREUR : {sortent[0].upper()}"
    return "PLUSIEURS BOUCLES FINES SORTENT DU BRUIT : L'ERREUR N'EST PAS UNE"


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, lire=None, replicats: int | None = None,
            tirages: int | None = None, par225: dict | None = None) -> dict:
    """La lecture des deux bandes fines puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    R, C = par224["R"], par224["C"]
    Rf, Cf = le_treillis_fin(R, C)
    combien = len(par219["les_rangees"])
    bandes = les_bandes_fines(Rf, Cf, combien)
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    rp_ = par224["replicats"] if replicats is None else int(replicats)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "replicats": rp_, "le_treillis_fin":
                 {"rangees": Rf, "colonnes": Cf}, "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des bandes dérivées"}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources_publiees(par219, par223, par224))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}

    def _long(rel):  # noqa: E306
        return {int(a): {int(b): float(x[0]) for b, x in s.items()} for a, s in rel["le_long"].items()}
    pas = {("rangees", Rf[0]): _long(par224["relues"][f"rangees_{Rf[0]}"]),
           ("rangees", Rf[1]): _long(relues[f"rangees_{Rf[1]}"]),
           ("rangees", Rf[2]): par219["les_pas_par_rangee"],
           ("colonnes", Cf[0]): _long(par224["relues"][f"colonnes_{Cf[0]}"]),
           ("colonnes", Cf[1]): _long(relues[f"colonnes_{Cf[1]}"]),
           ("colonnes", Cf[2]): par223["les_pas_par_colonne"]}
    # ⚠⚠ LA MESURE TELLE QUE DÉCLARÉE, SANS FRANCHIR — publiée à côté, jamais remplacée.
    a0 = analyser(pas, Rf, Cf, g, t_, rp_, False)
    trous = les_trous_des_boucles(pas, Rf, Cf)
    rem = None
    if trous:
        rem = le_remplissage(par225["la_regle"], pas, trous)
        if rem is None:
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"la règle de `225`, {par225['la_regle']}, ne s'applique pas au trou des bandes fines"}
    a = analyser(pas, Rf, Cf, g, t_, rp_, True, DEMI_PAS_EN_VOXELS, rem)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": f"l'analyse de `224` : {a.get('raison')}", "la_reproduction": rep}
    ouvertes = [n for n, b in a["les_boucles"].items() if not b.get("fermable")]
    if ouvertes:
        return {**base, "decidable": False, "la_reproduction": rep,
                "raison": f"des boucles fines restent ouvertes après le franchissement : {ouvertes}"}
    # ⚠⚠ LE GRAND RECTANGLE DU TREILLIS FIN EST LA BOUCLE EN HAUT À GAUCHE : il retombe sur `224`, ou refus.
    gr, hg = a["les_boucles"]["le_grand_rectangle"], par224["les_boucles"][LA_BOUCLE]
    if not gr.get("fermable") or gr["la_fermeture_en_voxels"] != hg["la_fermeture_en_voxels"]:
        return {**base, "decidable": False, "la_reproduction": rep,
                "raison": "le grand rectangle du treillis fin ne retombe pas sur la boucle en haut à gauche de `224`"}
    ep = a["lepreuve"]
    if not ep.get("decidable"):
        return {**base, "decidable": False, "raison": "aucune boucle fine fermée", "la_reproduction": rep}
    cons = {k: le_consensus(p) for k, p in pas.items()}
    for k, v_ in (rem or {}).items():
        cons[k] = {**cons[k], **v_}
    dc = les_demi_cotes(Rf, Cf)
    pas_dc = {d: [float(cons[(d[0], d[1])][s]) for s in range(d[2], d[3])] for d in dc
              if all(s in cons[(d[0], d[1])] for s in range(d[2], d[3]))}
    theta = le_theta_dune_autocorrelation(lautocorrelation_commune(pas_dc.values()) or 0.0)
    rect = {n: c for n, c in les_boucles_declarees(Rf, Cf).items() if n in ep["les_rectangles"]}
    et = sur_letalon({d: len(p) for d, p in pas_dc.items()}, {d: float(np.std(p)) for d, p in pas_dc.items()},
                     rect, dc, theta, rp_, t_, g)
    sortent = les_boucles_qui_sortent(ep["par_rectangle"])
    sans = {"les_boucles": {n: ({"fermable": True, "la_fermeture_en_voxels": b["la_fermeture_en_voxels"],
                                 "la_part_du_nul_sous_la_fermeture":
                                     (a0["lepreuve"].get("par_rectangle") or {}).get(n, {}).get(
                                         "la_part_du_nul_sous_la_fermeture")}
                                if b.get("fermable") else {"fermable": False,
                                                           "les_coutures_manquantes": b["les_coutures_manquantes"]})
                            for n, b in a0["les_boucles"].items()},
            "les_boucles_qui_sortent": (les_boucles_qui_sortent(a0["lepreuve"]["par_rectangle"])
                                        if a0["lepreuve"].get("decidable") else [])}
    return {**base, "decidable": True, "la_reproduction": rep,
            "la_boucle_de_224": {"la_fermeture_en_voxels": hg["la_fermeture_en_voxels"]},
            "sans_franchir": sans, "les_trous_des_bandes_fines": trous,
            "le_trou_franchi": ({"la_regle_de_225": par225["la_regle"], "les_coutures_remplies":
                                 a.get("les_coutures_remplies")} if rem else None),
            "lanalyse_du_treillis_fin": a, "le_seuil_de_sortie": round(le_seuil(len(ep["par_rectangle"])), 4),
            "letalon_de_la_designation": et,
            "le_verdict": {"les_boucles_qui_sortent": sortent,
                           "la_regle_tient": et["elle_tient_sa_garantie"],
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(sortent, et["elle_tient_sa_garantie"])}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
          f"{rp['lecart_le_plus_grand']}")
    a = r["lanalyse_du_treillis_fin"]
    for k, c in a["la_couverture_du_consensus"].items():
        print(f"  {k} · {c['les_coutures_avec_consensus']}/{c['les_coutures_du_perimetre']} · sans "
              f"{c['les_coutures_sans_consensus'][:10]}")
    for n, b in a["les_boucles"].items():
        if not b.get("fermable"):
            print(f"  {n} · OUVERTE · {b['les_coutures_manquantes']}")
            continue
        print(f"  {n} · L {b['la_fermeture_en_voxels']} · côtés {b['les_cotes_en_voxels']} · nul {b.get('le_nul')}")
    e = a["lepreuve"]
    print(f"épreuve · T {e['la_statistique']} contre {e['la_statistique_mediane_du_nul']} · p {e['la_valeur_p']}")
    t = r["letalon_de_la_designation"]
    print(f"étalon de la désignation · {t['combien_designent']}/{t['les_replicats']} = {t['le_taux']} (borne "
          f"{t['la_borne']}) · seuil {r['le_seuil_de_sortie']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
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

    Rf, Cf = le_treillis_fin([99, 198, 297], [71, 142, 213])
    v("★★★★ le treillis fin est la boucle en haut à gauche et le milieu entier de ses côtés",
      Rf == [99, 148, 198] and Cf == [71, 106, 142], str((Rf, Cf)))
    bf = les_bandes_fines(Rf, Cf, 5)
    v("★★★★ deux bandes nouvelles, cinq lignes par la fonction de 219, lues sur le seul quadrant",
      bf[0]["les_lignes"] == [146, 147, 148, 149, 150] and (bf[0]["de"], bf[0]["a"]) == (71, 142)
      and bf[1]["les_lignes"] == [104, 105, 106, 107, 108] and (bf[1]["de"], bf[1]["a"]) == (99, 198))
    dr, dc_ = le_domaine("rangees", [3, 4], 10, 12), le_domaine("colonnes", [5, 6], 0, 2)
    v("★★★★ le domaine d'une bande est ce qu'elle lit, par famille",
      dr["h"] == {(3, 10), (3, 11), (4, 10), (4, 11)} and dr["v"] == {(3, 10), (3, 11), (3, 12)}
      and dc_["v"] == {(0, 5), (1, 5), (0, 6), (1, 6)} and dc_["h"] == {(0, 5), (1, 5), (2, 5)},
      str((dr, dc_)))
    rel_r = {"le_sens": "rangees", "le_long": {3: {10: (1.5, 0, 16)}}, "en_travers": {3: {11: (2.0, 0, 16)}}}
    rel_c = {"le_sens": "colonnes", "le_long": {5: {0: (0.5, 0, 16)}}, "en_travers": {1: {5: (4.0, 0, 16)}}}
    v("★★★★ une bande de colonnes rend ses pas le long comme des pas verticaux (rangée, colonne)",
      les_pas_dune_bande(rel_c) == {"v": {(0, 5): 0.5}, "h": {(1, 5): 4.0}}
      and les_pas_dune_bande(rel_r) == {"h": {(3, 10): 1.5}, "v": {(3, 11): 2.0}},
      str(les_pas_dune_bande(rel_c)))

    N = {"n": {"domaine": {"h": {(1, 1), (1, 2)}, "v": {(0, 1)}}, "pas": {"h": {(1, 1): 2.0}, "v": {(0, 1): 1.0}}}}
    S = {"s": {"domaine": {"h": {(1, 1), (1, 2), (1, 3)}}, "pas": {"h": {(1, 1): 2.0, (1, 3): 9.0}}}}
    rp = _sur(la_reproduction_croisee, N, S)
    v("★★★ des pas qui retombent, sur les seules coutures que les deux lisent",
      rp.get("decidable") and rp["combien_de_coutures_relues"] == 1, str(rp))
    S2 = copy.deepcopy(S)
    S2["s"]["pas"]["h"][(1, 1)] = 2.1
    v("★★★★ un écart au-delà de l'arrondi est refusé",
      "ne retombe pas" in str(_sur(la_reproduction_croisee, N, S2).get("raison")))
    S3 = copy.deepcopy(S)
    S3["s"]["pas"]["h"][(1, 2)] = 3.0
    v("★★★★ une couture lue d'un seul côté est refusée",
      "et non par" in str(_sur(la_reproduction_croisee, N, S3).get("raison")))
    S4 = {"s": {"domaine": {"h": {(9, 9)}}, "pas": {"h": {(9, 9): 1.0}}}}
    v("★★★ une bande qui ne croise aucune couture publiée n'est pas contrôlée",
      "aucune couture" in str(_sur(la_reproduction_croisee, N, S4).get("raison")))

    v("★★★ le seuil partage la garantie entre les boucles fermées",
      abs(le_seuil(4) - (1 - GARANTIE / 4)) < 1e-12 and abs(le_seuil(1) - (1 - GARANTIE)) < 1e-12)
    pr = {"a": {"la_part_du_nul_sous_la_fermeture": 0.99}, "b": {"la_part_du_nul_sous_la_fermeture": 0.98},
          "c": {"la_part_du_nul_sous_la_fermeture": 0.5}, "d": {"la_part_du_nul_sous_la_fermeture": 0.9875}}
    v("★★★★ une boucle sort à partir du seuil, pas en dessous",
      les_boucles_qui_sortent(pr) == ["a", "d"], str(les_boucles_qui_sortent(pr)))
    iss = {_ce_qui_reste(s_, t_) for s_ in ([], ["x"], ["x", "y"]) for t_ in (True, False)}
    v("★★★★ quatre issues distinctes, et une règle qui ne tient pas ne désigne rien",
      len(iss) == 4 and _ce_qui_reste(["x"], False) == _ce_qui_reste([], False)
      and "X" in _ce_qui_reste(["x"], True))

    # l'étalon de la désignation
    # ⚠ des demi-côtés de quarante coutures : sur trois, un tirage par blocs ne veut rien dire.
    R, C = [0, 40, 80], [0, 40, 80]
    dc = les_demi_cotes(R, C)
    rect = {n: c for n, c in les_boucles_declarees(R, C).items() if n != "le_grand_rectangle"}
    # ⚠ AUX TAILLES DE LA MESURE, deux cents réplicats de neuf cent quatre-vingt-dix-neuf tirages : à
    # quarante réplicats de cent quatre-vingt-dix-neuf, la résolution du nul fait à elle seule passer la borne.
    et = _sur(sur_letalon, {d: d[3] - d[2] for d in dc}, {d: 1.0 for d in dc}, rect, dc, 0.1, 200, 999, 7)
    v("★★★ sur des demi-côtés indépendants, la règle désigne au plus au taux de sa garantie",
      et.get("decidable") and et["le_taux"] <= et["la_borne"], str(et))
    # ⚠⚠ UN NUL TROP ÉTROIT FAIT DÉSIGNER TROP, et c'est la dépendance POSITIVE qui l'étrécit : des pas qui
    # persistent d'une couture à l'autre, que des blocs courts coupent. Un θ positif rend la règle prudente.
    et9 = _sur(sur_letalon, {d: d[3] - d[2] for d in dc}, {d: 1.0 for d in dc}, rect, dc, -0.9, 200, 999, 7)
    v("★★★★ et l'étalon voit une règle qui désigne trop : des pas qui persistent d'une couture à l'autre",
      et9.get("decidable") and not et9["elle_tient_sa_garantie"], str(et9))
    tr = le_treillis(R, C)
    g_ = np.random.default_rng(3)
    D = {(i, j): float(g_.normal(0.0, 5.0)) for i in range(3) for j in range(3)}
    pas_geo = {d: list(np.full(d[3] - d[2], (D[tr[d][1]] - D[tr[d][0]]) / (d[3] - d[2]))
                       + g_.normal(0.0, 1.0, d[3] - d[2])) for d in dc}
    pas_geo[("rangees", 0, 0, 40)] = list(np.asarray(pas_geo[("rangees", 0, 0, 40)]) + 1.5)
    e_ = _sur(lepreuve, pas_geo, rect, dc, 199, 3)
    v("★★★★ une erreur de soixante voxels sur un côté fait sortir sa seule boucle",
      _ok(lambda: les_boucles_qui_sortent(e_["par_rectangle"]) == ["haut_gauche"]),
      str({n: x["la_part_du_nul_sous_la_fermeture"] for n, x in (e_.get("par_rectangle") or {}).items()}))

    # la mesure : ce qui est publié est relu, et une lecture fabriquée qui retombe passe la mesure entière
    p219, p223, p224 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu()
    src = _sur(les_sources_publiees, p219, p223, p224)
    v("★★★ les sources publiées sont 219, 223 et les quatre bandes de 224",
      _ok(lambda: sorted(src) == sorted(["219", "223"] + [f"224 {b['cle']}" for b in p224["bandes"]])))

    def _fabrique(b):  # noqa: E306
        # ⚠ une bande fabriquée qui RETOMBE : ses coutures communes avec les sources sont copiées, les
        # autres tirées ; aucun pas n'est inventé là où une source a lu.
        g = np.random.default_rng(len(b["cle"]))
        dom = le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"])
        pas_ = {}
        for f in ("h", "v"):
            pas_[f] = {}
            for cle in sorted(dom[f]):
                x = next((S_["pas"][f][cle] for S_ in src.values() if f in S_["pas"] and cle in S_["domaine"].get(f, ())
                          and cle in S_["pas"][f]), None)
                vu = any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in src.values())
                if x is not None:
                    pas_[f][cle] = x
                elif not vu:
                    pas_[f][cle] = round(float(g.normal(0.0, 1.0)), 4)
        le_long_f, trav_f = (("h", "v") if b["le_sens"] == "rangees" else ("v", "h"))
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if b["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": {}}
    m = _sur(mesurer, None, p219, p223, p224, _fabrique, 4, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière, et le grand rectangle fin retombe sur 224",
      m.get("decidable") and m["la_reproduction"]["combien_de_coutures_relues"] > 0
      and m["lanalyse_du_treillis_fin"]["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"]
      == p224["les_boucles"][LA_BOUCLE]["la_fermeture_en_voxels"], str(m.get("raison")))
    v("★★★★ l'étalon de la désignation est tiré au θ que l'analyse de 224 dérive des mêmes demi-côtés",
      _ok(lambda: m["letalon_de_la_designation"]["le_theta"]
          == m["lanalyse_du_treillis_fin"]["letalon_de_lepreuve"]["le_theta"]))
    v("★★★★ chaque bande nouvelle est contrôlée par une source publiée",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]} == {b["cle"] for b in bf}))
    faux224 = copy.deepcopy(p224)
    faux224["les_boucles"][LA_BOUCLE]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ un grand rectangle fin qui ne retombe pas sur la boucle de 224 est refusé, par sa raison",
      "ne retombe pas sur la boucle" in str(_sur(mesurer, None, p219, p223, faux224, _fabrique, 4, 49).get("raison")))

    def _troue(b):  # noqa: E306
        # ⚠ trois lignes sur cinq sans pas aux coutures 133 et 134 de la bande de colonnes : un trou de majorité
        x = _fabrique(b)
        if b["le_sens"] == "colonnes":
            for l_ in b["les_lignes"][:3]:
                for s_ in (133, 134):
                    x["le_long"].get(l_, {}).pop(s_, None)
        return x
    mt = _sur(mesurer, None, p219, p223, p224, _troue, 4, 49)
    v("★★★★ un trou dans une bande fine est franchi par la règle de 225, et les quatre boucles se ferment",
      mt.get("decidable") and mt["le_trou_franchi"]["la_regle_de_225"] == ce_que_225_a_rendu()["la_regle"]
      and all(b.get("fermable") for b in mt["lanalyse_du_treillis_fin"]["les_boucles"].values()),
      str(mt.get("raison")))
    v("★★★★ et la mesure telle que déclarée, sans franchir, est publiée à côté avec ses boucles ouvertes",
      _ok(lambda: sorted(n for n, b in mt["sans_franchir"]["les_boucles"].items() if not b["fermable"])
          == ["haut_droite", "haut_gauche"]
          and mt["les_trous_des_bandes_fines"][0]["le_debut"] == 133))
    v("★★★★ et l'étalon de la désignation y est tiré au θ des demi-côtés FRANCHIS, celui de l'analyse",
      _ok(lambda: mt["letalon_de_la_designation"]["le_theta"]
          == mt["lanalyse_du_treillis_fin"]["letalon_de_lepreuve"]["le_theta"]))
    p225 = ce_que_225_a_rendu()
    v("★★★ une règle de 225 qui ne s'applique pas au trou rend la mesure indécidable, par sa raison",
      "ne s'applique pas" in str(_sur(mesurer, None, p219, p223, p224, lambda b: {
          **_troue(b), "le_long": ({l_: {k_: v_ for k_, v_ in d_.items() if k_ not in (133, 134)}
                                    for l_, d_ in _troue(b)["le_long"].items()} if b["le_sens"] == "colonnes"
                                   else _troue(b)["le_long"])}, 4, 49,
          {**p225, "la_regle": "les_lignes_presentes"}).get("raison")))
    v("★★ sans trou, rien n'est franchi", _ok(lambda: m["le_trou_franchi"] is None))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, _decale, 4, 49).get("raison")))

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
        p219, p224 = ce_que_219_a_rendu(), ce_que_224_a_rendu()
        if not (p219.get("decidable") and p224.get("decidable")):
            print(f"indécidable : {p219.get('raison') or p224.get('raison')}")
            return 1
        Rf, Cf = le_treillis_fin(p224["R"], p224["C"])
        bandes = les_bandes_fines(Rf, Cf, len(p219["les_rangees"]))
        deja = (json.loads(a.lire.read_text()).get("les_bandes") or {}) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": d}, ensure_ascii=False, indent=1))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja, ecrire)
        if not lu.get("decidable"):
            print(f"indécidable : {lu.get('raison')}")
            return 1
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
