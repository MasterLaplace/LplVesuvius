"""La rangée 99, entre les colonnes 78 et 106, porte-t-elle la fermeture que `228` voyait du côté de la colonne 71 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P75`. `229` a montré que la moitié haute de la colonne 71
s'accorde avec un détour qui ne partage aucune de ses lignes, la colonne 78, et que la fermeture de la boucle
fine en haut à gauche de `227` tombe de l'autre côté du détour : la boucle entre les colonnes 78 et 106, en
haut, ferme à −27,25 voxels. Le long de la rangée 99, à cinq lignes, les boucles qui ferment à quelques voxels
évitent le segment entre les colonnes 78 et 106, et celles qui manquent de plus de vingt voxels le traversent
toutes. C'est une incidence, pas un test.

## Le détour de la rangée, dérivé comme celui de `229`

Les lignes de la rangée 99 sont toutes celles qui votent pour elle à une largeur de l'échelle de `218` : de
95 à 103. Le détour est la bande de cinq lignes — la largeur de `219` — la plus proche de la rangée 99 dont
aucune ligne n'est une des siennes ni une de celles de la rangée 148, cherchée vers l'intérieur de la boucle
de `229`, le seul côté où les trois autres côtés de la boucle étroite sont déjà lus : par la colonne 78 de
`229`, la colonne 106 de `227` et la colonne 71 de `224`. Il est lu sur les colonnes du treillis de `229`,
de 71 à 106. C'EST LA FONCTION DE `229`, APPELÉE sur les rangées.

Le treillis de la rangée garde les colonnes de `229` et coupe ses boucles du haut par le détour : ses rangées
sont 99, le détour, et 148. ⭐⭐ L'ANALYSE EST CELLE DE `224`, APPELÉE, et le test est celui de `229`. Sa
boucle en haut à droite est LA BOUCLE ÉTROITE DE LA RANGÉE : la rangée 99 entre les colonnes 78 et 106 d'un
côté, le détour sur les mêmes colonnes de l'autre, et entre eux quelques coutures des colonnes 78 et 106.

## Ce qui contrôle

⚠⚠⚠ La lecture neuve croise les bandes publiées de `219`, `223`, `224`, `227`, `228` et `229` ; partout où
deux lectures lisent la même couture, elles retombent à l'arrondi, sur les mêmes coutures, sinon refus.
⚠⚠⚠ Recomposées sur ce treillis, les deux boucles du haut de `229` doivent retomber EXACTEMENT sur les
fermetures qu'il publie, sinon refus. ⚠⚠ Un trou de majorité est franchi par la règle que `225` a retenue,
déclaré ici, avant la lecture.

## Ce qui se mesure, et le seul test déclaré

⭐⭐⭐⭐ UN SEUL TEST, celui de `229` : la boucle étroite de la rangée sort du bruit quand sa fermeture dépasse,
en valeur absolue, celle de demi-côtés tirés indépendamment par blocs dans au moins `1 − 0,05` des tirages. La
garantie n'est pas partagée : c'est la seule boucle que `229` désigne AVANT cette lecture. ⭐⭐⭐ Son étalon,
celui de `227`. Publiés sans test : la fermeture de chaque boucle du treillis de la rangée et sa part du nul,
et la part de la fermeture de la boucle de `229` entre les colonnes 78 et 106 que porte la boucle étroite de
la rangée. ⚠ La boucle en haut à gauche est le témoin : elle longe la rangée 99 entre les colonnes 71 et 78,
où la boucle étroite de `229` ferme.

## Les issues, exclusives

- l'étalon ne tient pas : le test ne désigne rien ;
- la boucle étroite de la rangée sort du bruit : la rangée 99, entre les colonnes 78 et 106, porte une erreur
  que le détour ne partage pas ;
- elle n'en sort pas : le détour ne sépare pas la rangée 99 de ce que le bruit ferait.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle désigne une RÉGION, pas un côté — la boucle étroite de la
rangée, c'est aussi les quelques coutures des colonnes 78 et 106 qui la ferment. Un détour qui s'accorde avec
la rangée ne dit pas qu'elle est juste. Et le piège de `219` vaut.

Usage :
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_rangee_99.py --verifier
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_rangee_99.py --lire <lecture.json>
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_rangee_99.py --depuis <lecture.json> \\
        --json docs/mesures/un_detour_separe_t_il_lerreur_de_la_rangee_99.json
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

import un_detour_separe_t_il_lerreur_de_la_colonne_71 as t229  # noqa: E402
from cinq_rangees_designent_elles_la_fautive import les_rangees_a_lire  # noqa: E402
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import le_consensus  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, le_seuil, les_pas_dune_bande)
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from un_detour_separe_t_il_lerreur_de_la_colonne_71 import (CE_QUE_228_A_RENDU, _long,  # noqa: E402
                                                             ce_que_227_a_rendu, le_detour,
                                                             le_test_dune_boucle,
                                                             les_lectures_publiees,
                                                             les_lignes_de_la_colonne, les_sources,
                                                             recomposer)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

CE_QUE_229_A_RENDU = RACINE / "docs" / "mesures" / "un_detour_separe_t_il_lerreur_de_la_colonne_71.json"

LA_BOUCLE_ETROITE = "haut_droite"
LE_TEMOIN = "haut_gauche"
LA_QUESTION_DECLAREE = ("la rangée 99, entre les colonnes 78 et 106, porte-t-elle la fermeture que `228` voyait du "
                        "côté de la colonne 71 ?")
LA_MESURE_DECLAREE = ("la fermeture de la boucle étroite entre la rangée 99, des colonnes 78 à 106, et un détour "
                      "dont aucune ligne n'est une des siennes, contre des demi-côtés tirés indépendamment ; un seul "
                      "test, au-delà de 1 − 0,05")


# ─────────────────────────────── ce que 229 a publié ───────────────────────────────

def ce_que_229_a_rendu(chemin: Path = CE_QUE_229_A_RENDU) -> dict:
    """Le détour de `229`, son treillis et les fermetures de ses boucles — relus, jamais recalculés."""
    lu = les_lectures_publiees(chemin)
    if not lu.get("decidable"):
        return lu
    d = lu["brut"]
    a = d.get("lanalyse_du_treillis_du_detour") or {}
    if not d.get("le_treillis") or not a.get("les_boucles"):
        return {"decidable": False, "raison": "`229` ne publie pas son treillis ni ses boucles"}
    return {"decidable": True, "relues": lu["relues"], "le_detour": int(d["le_detour"]),
            "R": [int(x) for x in d["le_treillis"]["rangees"]], "C": [int(x) for x in d["le_treillis"]["colonnes"]],
            "les_fermetures": {n: float(b["la_fermeture_en_voxels"]) for n, b in a["les_boucles"].items()
                               if b.get("fermable")}}


# ─────────────────────────────── ce qui est dérivé ───────────────────────────────

def le_treillis_de_la_rangee(R229, C229, detour: int) -> tuple[list[int], list[int]]:
    """Les colonnes de `229`, et ses rangées du haut coupées par le détour de la rangée."""
    return [int(R229[0]), int(detour), int(R229[1])], [int(c) for c in C229]


def la_bande_de_la_rangee(C229, detour: int, combien: int) -> dict:
    """La seule bande à lire : le détour de la rangée, sur les colonnes du treillis de `229`."""
    return {"cle": f"rangees_{int(detour)}", "le_sens": "rangees", "le_centre": int(detour),
            "les_lignes": les_rangees_a_lire(int(detour), int(combien)), "de": int(C229[0]), "a": int(C229[-1])}


def les_boucles_de_229(R, C) -> dict:
    """Les deux boucles du haut de `229`, en coins, sur le treillis de la rangée."""
    return {"haut_gauche": (int(R[0]), int(R[2]), int(C[0]), int(C[1])),
            "haut_droite": (int(R[0]), int(R[2]), int(C[1]), int(C[2]))}


# ─────────────────────────────── l'analyse ───────────────────────────────

def _ce_qui_reste(sort: bool, tient: bool) -> str:
    """Les trois issues, EXCLUSIVES — et un étalon qui ne tient pas prime."""
    if not tient:
        return "LE TEST NE TIENT PAS SA GARANTIE SUR SON ÉTALON : IL NE DÉSIGNE RIEN"
    if sort:
        return ("LA BOUCLE ÉTROITE DE LA RANGÉE SORT DU BRUIT : LA RANGÉE 99, ENTRE LES COLONNES 78 ET 106, PORTE UNE "
                "ERREUR QUE LE DÉTOUR NE PARTAGE PAS")
    return ("LA BOUCLE ÉTROITE DE LA RANGÉE NE SORT PAS DU BRUIT : LE DÉTOUR NE SÉPARE PAS LA RANGÉE 99 DE CE QUE LE "
            "BRUIT FERAIT")


def analyser_la_rangee(pas: dict, R, C, regle: str, graine: int, tirages: int, replicats: int,
                       garantie: float = GARANTIE, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Le treillis de la rangée, ses trous franchis, le test unique de `229` et son étalon — pur."""
    x = le_test_dune_boucle(pas, R, C, regle, graine, tirages, replicats, LA_BOUCLE_ETROITE, garantie, demi)
    if not x.get("decidable"):
        return x
    recomposees = recomposer(x, les_boucles_de_229(R, C))
    t, et = x["le_test"], x["letalon_du_test"]
    L, l229 = t["la_fermeture_en_voxels"], recomposees["haut_droite"]
    sort, tient = t["elle_sort_du_bruit"], et["elle_tient_sa_garantie"]
    return {"decidable": True, "le_treillis": {"rangees": [int(r) for r in R], "colonnes": [int(c) for c in C]},
            "lanalyse_du_treillis_de_la_rangee": x["lanalyse"], "les_boucles_de_229_recomposees": recomposees,
            "le_test": t, "letalon_du_test": et,
            "la_part_de_229_portee_par_la_boucle_etroite": (round(float(L) / l229, 4) if l229 else None),
            "le_verdict": {"la_boucle_etroite_sort_du_bruit": bool(sort), "letalon_tient": bool(tient),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(sort, tient)}}


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, par227: dict | None = None,
            par228: dict | None = None, par229: dict | None = None, lire=None, replicats: int | None = None,
            tirages: int | None = None) -> dict:
    """La lecture du détour de la rangée puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    par227 = ce_que_227_a_rendu() if par227 is None else par227
    par228 = les_lectures_publiees(CE_QUE_228_A_RENDU) if par228 is None else par228
    par229 = ce_que_229_a_rendu() if par229 is None else par229
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("227", par227),
                     ("228", par228), ("229", par229)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    combien = len(par219["les_rangees"])
    d229 = le_detour(par227["Cf"][0], par227["Cf"][1], combien)
    if (par229["R"], par229["C"]) != tuple(t229.le_treillis_du_detour(par227["Rf"], par227["Cf"], d229)):
        return {**base, "decidable": False, "raison": "le treillis publié par `229` n'est pas celui qu'il dérive"}
    R229, C229 = par229["R"], par229["C"]
    detour = le_detour(R229[0], R229[1], combien)
    if detour is None:
        return {**base, "decidable": False, "raison": "aucune bande de lignes libres entre les rangées"}
    R, C = le_treillis_de_la_rangee(R229, C229, detour)
    bande = la_bande_de_la_rangee(C229, detour, combien)
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    rp_ = par224["replicats"] if replicats is None else int(replicats)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes([bande], lire=lire)
    base.update({"graine": int(g), "tirages": t_, "replicats": rp_, "la_regle_de_225": par225["la_regle"],
                 "les_lignes_de_la_rangee": sorted(les_lignes_de_la_colonne(R229[0])),
                 "les_lignes_de_la_rangee_interieure": sorted(les_lignes_de_la_colonne(R229[1])),
                 "le_detour": int(detour), "les_bandes_declarees": [bande],
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if sorted(pub) != [bande["cle"]] or _la_definition(pub[bande["cle"]]) != _la_definition(bande):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle du détour dérivé"}
    relue = relire_une_bande(pub[bande["cle"]])
    nouvelles = {bande["cle"]: {"domaine": le_domaine("rangees", bande["les_lignes"], bande["de"], bande["a"]),
                                "pas": les_pas_dune_bande(relue)}}
    src = les_sources(par219, par223, par224, par227, par228)
    for k, rel in sorted(par229["relues"].items()):
        src[f"229 {k}"] = {"domaine": le_domaine(rel["le_sens"], rel["les_lignes"], rel["de"], rel["a"]),
                           "pas": les_pas_dune_bande(rel)}
    rep = la_reproduction_croisee(nouvelles, src)
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = {("rangees", R[0]): _long(par224["relues"][f"rangees_{R[0]}"]),
           ("rangees", R[1]): _long(relue),
           ("rangees", R[2]): _long(par227["relues"][f"rangees_{R[2]}"]),
           ("colonnes", C[0]): _long(par224["relues"][f"colonnes_{C[0]}"]),
           ("colonnes", C[1]): _long(par229["relues"][f"colonnes_{C[1]}"]),
           ("colonnes", C[2]): _long(par227["relues"][f"colonnes_{C[2]}"])}
    a = analyser_la_rangee(pas, R, C, par225["la_regle"], g, t_, rp_)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": a.get("raison"), "la_reproduction": rep}
    # ⚠⚠⚠ RECOMPOSÉES SUR CE TREILLIS, LES BOUCLES DU HAUT DE `229` RETOMBENT EXACTEMENT, ou refus.
    for n, L in a["les_boucles_de_229_recomposees"].items():
        if L != par229["les_fermetures"].get(n):
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"la boucle {n} de `229` recomposée ({L}) ne retombe pas sur `229`"}
    return {**base, "decidable": True, "la_reproduction": rep,
            "les_fermetures_de_229": {n: par229["les_fermetures"][n] for n in les_boucles_de_229(R, C)}, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"détour : rangée {r['le_detour']} · reproduction {rp['combien_de_coutures_relues']} coutures "
          f"{rp['par_croisement']}, écart {rp['lecart_le_plus_grand']}")
    a = r["lanalyse_du_treillis_de_la_rangee"]
    for k, c in a["la_couverture_du_consensus"].items():
        print(f"  {k} · {c['les_coutures_avec_consensus']}/{c['les_coutures_du_perimetre']} · sans "
              f"{c['les_coutures_sans_consensus'][:10]}")
    for n, b in a["les_boucles"].items():
        print(f"  {n} · L {b['la_fermeture_en_voxels']} · côtés {b['les_cotes_en_voxels']} · nul {b.get('le_nul')}")
    print(f"recomposées : {r['les_boucles_de_229_recomposees']} contre {r['les_fermetures_de_229']}")
    print(f"test : {r['le_test']}")
    t = r["letalon_du_test"]
    print(f"étalon : {t['combien_designent']}/{t['les_replicats']} = {t['le_taux']} (borne {t['la_borne']}, "
          f"θ {t['le_theta']})")
    print(f"part de 229 portée par la boucle étroite de la rangée : {r['la_part_de_229_portee_par_la_boucle_etroite']}")
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
    v("★★★★ les lignes de la rangée 99 sont celles de toute l'échelle de 218, de 95 à 103",
      les_lignes_de_la_colonne(99) == set(range(95, 104)))
    v("★★★★ le détour de la rangée 99 vers 148, à cinq lignes, est la rangée 106, de 104 à 108",
      le_detour(99, 148, 5) == 106 and les_rangees_a_lire(106, 5) == [104, 105, 106, 107, 108],
      str(le_detour(99, 148, 5)))
    R, C = le_treillis_de_la_rangee([99, 148, 198], [71, 78, 106], 106)
    v("★★★★ le treillis de la rangée garde les colonnes de 229 et coupe ses boucles du haut",
      R == [99, 106, 148] and C == [71, 78, 106], str((R, C)))
    bd = la_bande_de_la_rangee([71, 78, 106], 106, 5)
    v("★★★★ une seule bande à lire, le détour de la rangée, sur les colonnes de 229",
      bd == {"cle": "rangees_106", "le_sens": "rangees", "le_centre": 106, "les_lignes": [104, 105, 106, 107, 108],
             "de": 71, "a": 106}, str(bd))
    v("★★★ les deux boucles du haut de 229, sur ce treillis",
      les_boucles_de_229(R, C) == {"haut_gauche": (99, 148, 71, 78), "haut_droite": (99, 148, 78, 106)})
    v("★★★★ un seul test, à la garantie entière", abs(le_seuil(1) - (1.0 - GARANTIE)) < 1e-12)
    iss = {_ce_qui_reste(x, y) for x in (True, False) for y in (True, False)}
    v("★★★★ trois issues distinctes, et un étalon qui ne tient pas prime",
      len(iss) == 3 and _ce_qui_reste(True, False) == _ce_qui_reste(False, False))

    # ── l'analyse, sur des pas fabriqués : une géométrie exacte et du bruit par ligne
    g = np.random.default_rng(13)
    R2, C2 = [0, 8, 40], [0, 12, 40]

    def _bandes(erreur: dict | None = None, sd: float = 1.0):  # noqa: E306
        out = {}
        for sens, centres, x in (("rangees", R2, 0.2), ("colonnes", C2, 0.15)):
            for centre in centres:
                de, a_ = (C2[0], C2[2]) if sens == "rangees" else (R2[0], R2[2])
                out[(sens, centre)] = {l_: {s: x + float(g.normal(0.0, sd)) for s in range(de, a_)}
                                       for l_ in range(centre - 2, centre + 3)}
        for (sens, centre), (de, a_, e) in (erreur or {}).items():
            for l_ in out[(sens, centre)]:
                for s in range(de, a_):
                    out[(sens, centre)][l_][s] += e
        return out
    a = _sur(analyser_la_rangee, _bandes(), R2, C2, "le_maillage", 3, 199, 40)
    v("★★★ l'analyse est décidable sur des pas fabriqués", a.get("decidable"), str(a.get("raison")))
    v("★★★★ sans erreur, la boucle étroite de la rangée ne sort pas du bruit",
      _ok(lambda: not a["le_test"]["elle_sort_du_bruit"]), str(a.get("le_test")))
    v("★★★★ une seule boucle testée, la boucle étroite de la rangée, au seuil de la garantie entière",
      _ok(lambda: a["le_test"]["les_boucles_testees"] == [LA_BOUCLE_ETROITE] and a["le_test"]["le_seuil"] == 0.95
          and a["letalon_du_test"]["les_boucles_testees"] == [LA_BOUCLE_ETROITE]), str(a.get("le_test")))
    v("★★★★ recomposées, les boucles de 229 sont la somme de leurs deux boucles de la rangée",
      _ok(lambda: all(abs(a["les_boucles_de_229_recomposees"][n]
                          - a["lanalyse_du_treillis_de_la_rangee"]["les_boucles"][h_]["la_fermeture_en_voxels"]
                          - a["lanalyse_du_treillis_de_la_rangee"]["les_boucles"][b_]["la_fermeture_en_voxels"]) < 3e-4
                      for n, h_, b_ in (("haut_gauche", "haut_gauche", "bas_gauche"),
                                        ("haut_droite", "haut_droite", "bas_droite")))))
    # ⚠ une erreur que les lignes de la rangée partagent, entre les deux colonnes de droite
    ah = _sur(analyser_la_rangee, _bandes({("rangees", 0): (12, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ une erreur partagée par les lignes de la rangée, à droite : la boucle étroite de la rangée sort du bruit",
      _ok(lambda: ah["le_test"]["elle_sort_du_bruit"]
          and 0.8 < ah["la_part_de_229_portee_par_la_boucle_etroite"] < 1.2
          and abs(ah["la_part_de_229_portee_par_la_boucle_etroite"] - ah["le_test"]["la_fermeture_en_voxels"]
                  / ah["les_boucles_de_229_recomposees"]["haut_droite"]) < 1e-3), str(ah.get("le_test")))
    v("★★★ ... et le témoin, à gauche, ne la porte pas",
      _ok(lambda: abs(ah["lanalyse_du_treillis_de_la_rangee"]["les_boucles"][LE_TEMOIN]["la_fermeture_en_voxels"])
          < 0.5 * abs(ah["le_test"]["la_fermeture_en_voxels"])))
    ap = _sur(analyser_la_rangee, _bandes({("rangees", 0): (12, 40, 0.6), ("rangees", 8): (12, 40, 0.6)}, 0.25),
              R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ la même erreur, partagée par le détour : la boucle étroite ne la voit pas, celle du dessous la porte",
      _ok(lambda: not ap["le_test"]["elle_sort_du_bruit"]
          and ap["lanalyse_du_treillis_de_la_rangee"]["les_boucles"]["bas_droite"]["la_fermeture_en_voxels"] > 12.0),
      str({n: x.get("la_fermeture_en_voxels") for n, x in
           (ap.get("lanalyse_du_treillis_de_la_rangee") or {}).get("les_boucles", {}).items()}))
    ad = _sur(analyser_la_rangee, _bandes({("colonnes", 40): (8, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3, 199, 40)
    v("★★★ une erreur de la colonne de droite, sous le détour : la boucle étroite n'en porte presque rien",
      _ok(lambda: not ad["le_test"]["elle_sort_du_bruit"]
          and abs(ad["la_part_de_229_portee_par_la_boucle_etroite"]) < 0.5), str(ad.get("le_test")))
    v("★★★ la boucle étroite sort exactement quand sa part du nul atteint le seuil, et le verdict le suit",
      _ok(lambda: all(x["le_test"]["elle_sort_du_bruit"] == (x["le_test"]["la_part_du_nul_sous_la_fermeture"]
                                                               >= x["le_test"]["le_seuil"])
                      and x["le_verdict"]["ce_qui_reste_a_mesurer"]
                      == _ce_qui_reste(x["le_test"]["elle_sort_du_bruit"], x["letalon_du_test"]["elle_tient_sa_garantie"])
                      for x in (a, ah, ap, ad))))
    # ⚠ un étalon qui ne tient pas : le verdict ne désigne rien, même quand la boucle étroite sort
    vrai = t229.sur_letalon
    t229.sur_letalon = lambda *a_, **k_: {**vrai(*a_, **k_), "elle_tient_sa_garantie": False}
    try:
        af = _sur(analyser_la_rangee, _bandes({("rangees", 0): (12, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3,
                  199, 40)
    finally:
        t229.sur_letalon = vrai
    v("★★★★ un étalon qui ne tient pas : le verdict ne désigne rien, même quand la boucle étroite sort",
      _ok(lambda: af["le_test"]["elle_sort_du_bruit"]
          and af["le_verdict"]["ce_qui_reste_a_mesurer"] == _ce_qui_reste(True, False)), str(af.get("le_verdict")))
    bt = _bandes()
    for l_ in (6, 7, 8):
        for s in (20, 21):
            del bt[("rangees", 8)][l_][s]
    at = _sur(analyser_la_rangee, bt, R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ un trou de majorité du détour est franchi par la règle de 225, et nommé",
      _ok(lambda: at["lanalyse_du_treillis_de_la_rangee"]["la_couverture_du_consensus"]["rangees_8"][
          "les_coutures_sans_consensus"] == [20, 21]
          and at["lanalyse_du_treillis_de_la_rangee"]["les_coutures_remplies"] == {"rangees_8": {"20": 0.0, "21": 0.0}}),
      str(at.get("raison")))

    # ── la mesure, sur une lecture fabriquée qui retombe : copiée des sources là où elles lisent
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    p227, p228, p229 = ce_que_227_a_rendu(), les_lectures_publiees(CE_QUE_228_A_RENDU), ce_que_229_a_rendu()
    v("★★★ 229 se relit, et son détour est la colonne 78", p229.get("decidable") and p229.get("le_detour") == 78,
      str(p229.get("raison")))
    src = _sur(les_sources, p219, p223, p224, p227, p228)
    for k, rel in sorted((p229.get("relues") or {}).items()):
        src[f"229 {k}"] = {"domaine": le_domaine(rel["le_sens"], rel["les_lignes"], rel["de"], rel["a"]),
                           "pas": les_pas_dune_bande(rel)}

    def _fabrique(b):  # noqa: E306
        gg = np.random.default_rng(b["le_centre"])
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
                    pas_[f][cle] = round(float(gg.normal(0.0, 1.0)), 4)
        ll = {}
        for (r, c), x in pas_["h"].items():
            ll.setdefault(r, {})[c] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_["v"].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": {}}
    pars = (p219, p223, p224, p225, p227, p228, p229)
    m = _sur(mesurer, None, *pars, _fabrique, 20, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière, et les boucles de 229 retombent",
      m.get("decidable") and m.get("le_detour") == 106
      and m["les_boucles_de_229_recomposees"] == m["les_fermetures_de_229"]
      and m["la_reproduction"]["combien_de_coutures_relues"] > 0, str(m.get("raison")))
    v("★★★★ le détour de la rangée est contrôlé par 224, 227 et 229, là où ils le croisent",
      _ok(lambda: {k.split("×")[1].split(" ")[0] for k in m["la_reproduction"]["par_croisement"]}
          >= {"224", "227", "229"}), str(m.get("la_reproduction")))
    faux229 = copy.deepcopy(p229)
    faux229["les_fermetures"]["haut_droite"] += 1.0
    v("★★★★ une boucle de 229 qui ne retombe pas est refusée, par sa raison",
      "ne retombe pas sur `229`" in str(_sur(mesurer, None, p219, p223, p224, p225, p227, p228, faux229,
                                             _fabrique, 20, 49).get("raison")))
    faux229b = copy.deepcopy(p229)
    faux229b["C"] = [71, 79, 106]
    v("★★★ un treillis de 229 qui n'est pas celui qu'il dérive est refusé",
      "n'est pas celui" in str(_sur(mesurer, None, p219, p223, p224, p225, p227, p228, faux229b,
                                    _fabrique, 20, 49).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, *pars, _decale, 20, 49).get("raison")))

    def _rejouer(lu):  # noqa: E306
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"les_bandes": lu.get("les_bandes") or {}}, f)
            chemin = Path(f.name)
        try:
            return mesurer(chemin, *pars, replicats=20, tirages=49)
        finally:
            chemin.unlink()
    lu_juste = lire_les_bandes([la_bande_de_la_rangee(p229["C"], 106, 5)], lire=_fabrique)
    cj = le_consensus(_long(relire_une_bande(lu_juste["les_bandes"]["rangees_106"])))
    v("★★★★ la rangée du détour, dans l'analyse, est la lecture neuve et non une autre",
      _ok(lambda: m["lanalyse_du_treillis_de_la_rangee"]["les_demi_cotes"]["rangees_106_78_106"]["la_somme_en_voxels"]
          == round(float(sum(cj[s_] for s_ in range(78, 106))), 4)))
    v("★★★★ la mesure se rejoue à l'octet près depuis sa lecture publiée",
      _ok(lambda: json.dumps(_rejouer(lu_juste), ensure_ascii=False) == json.dumps(m, ensure_ascii=False)))
    lu_ailleurs = lire_les_bandes([{**la_bande_de_la_rangee(p229["C"], 106, 5), "les_lignes": [105, 106, 107, 108, 109]}],
                                  lire=_fabrique)
    v("★★★ une lecture qui n'est pas celle du détour dérivé est refusée",
      "n'est pas celle du détour" in str(_sur(_rejouer, lu_ailleurs).get("raison")))

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
        p219, p229 = ce_que_219_a_rendu(), ce_que_229_a_rendu()
        if not (p219.get("decidable") and p229.get("decidable")):
            print(f"indécidable : {p219.get('raison') or p229.get('raison')}")
            return 1
        combien = len(p219["les_rangees"])
        detour = le_detour(p229["R"][0], p229["R"][1], combien)
        if detour is None:
            print("indécidable : aucun détour")
            return 1
        bandes = [la_bande_de_la_rangee(p229["C"], detour, combien)]
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
