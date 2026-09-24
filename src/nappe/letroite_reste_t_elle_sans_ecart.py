"""Découpée aux coupes de `235`, l'étroite reste-t-elle sans écart cumulé pendant que l'aile dérive ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE. Ce qui était vu avant d'écrire : ce que `236`
publie, et sa figure.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P82`. `236` a désigné, de l'aile de droite de `234`, la colonne 260 : une
troisième colonne, la 234, s'accorde avec la 243, l'étroite (colonnes 234 à 243) fermant à 9,2812 voxels à neuf
lignes quand l'aile ferme à −35,6938 et la large (234 à 260) à −26,4125. Mais la marge sur le bruit seul de la large
n'est que de 2,8875 voxels, et `235` a montré qu'une fermeture au bout peut cacher un demi-feuillet franchi en chemin.
Découpée comme l'aile, l'étroite reste-t-elle sans écart cumulé tout du long ? Et où la colonne 260 s'écarte-t-elle ?

## Les coupes, reprises

Les coupes de l'étroite sont celles que `235` a dérivées pour l'aile, aux mêmes rangées, tendues cette fois de la
colonne 234 à la 243, pour que chaque intervalle de rangées ait ses trois sous-boucles : celle de l'aile, celle de
l'étroite et celle de la large. ⚠⚠ Une coupe de `235` dont la bande de 234 à 243 ne tient pas dans le dépôt est
retirée, et ses deux intervalles se fondent en un : rien n'est choisi.

## Ce qui se lit, et ce qui le contrôle

Les coupes de l'étroite seules, neuf lignes chacune, par le lecteur de `224`. ⚠⚠ Tout le reste est publié : les
colonnes 234 et 243 et les bouts de l'étroite par `233` et `236`, la colonne 260 et les bouts de l'aile par `234`, les
coupes de l'aile par `235`. ⚠⚠⚠ Partout où une coupe neuve croise une bande publiée — `219`, `223`, `224`, `232`,
`233`, `234`, `235`, `236` —, les pas relus retombent à l'arrondi, sinon refus ; une coupe qui ne croise aucune bande
publiée est refusée. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque sous-boucle des trois familles, à chaque largeur, avec la garde de `232`.

⚠⚠⚠ TROIS CONTRÔLES SANS LECTURE DE PLUS. Les sous-boucles de l'aile retombent sur ce que `235` publie. Dans chaque
intervalle, la sous-boucle large est la somme des deux autres, là où aucun trou de bout ne touche la colonne 243. Et les
sous-boucles de l'étroite somment à la fermeture que `236` publie pour l'étroite, là où aucune colonne n'a de trou.
Sinon, refus.

LES PROFILS : pour chaque famille, la fermeture cumulée depuis la rangée 26, coupe après coupe.

## Les issues, exclusives, jugées à neuf lignes

- aucune coupe ne tient dans l'étroite : elle ne se découpe pas, et rien n'est lu ;
- une sous-boucle garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- le profil de l'étroite atteint le demi-feuillet en chemin : les colonnes 234 et 243 ne s'accordent qu'au bout ;
- il reste dessous tout du long : les colonnes 234 et 243 s'accordent sur toute la longueur de l'aile.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi la colonne 260 dérive ; ni si les colonnes 234 et 243, qui s'accordent,
sont justes.

Usage :
    uv run python src/nappe/letroite_reste_t_elle_sans_ecart.py --verifier
    uv run python src/nappe/letroite_reste_t_elle_sans_ecart.py --lire <lecture.json>
    uv run python src/nappe/letroite_reste_t_elle_sans_ecart.py --depuis <lecture.json> \\
        --json docs/mesures/letroite_reste_t_elle_sans_ecart.json
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
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from laquelle_des_deux_colonnes_derive import _fusionner, lemboitement_des_trois  # noqa: E402
from le_segment_au_dela_du_rectangle_se_relie_t_il import (ce_que_233_a_publie,  # noqa: E402
                                                           les_bandes_de_laile, les_pas_de_laile, les_tenues,
                                                           tient)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import (L_ARRONDI, ce_que_234_a_publie,  # noqa: E402
                                          le_profil, lemboitement, les_sources_de_235)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_235_A_PUBLIE = MESURES / "ou_laile_de_droite_se_separe.json"
CE_QUE_236_A_PUBLIE = MESURES / "laquelle_des_deux_colonnes_derive.json"
LES_FAMILLES = ("laile", "letroite", "la_large")

LA_QUESTION_DECLAREE = ("découpée aux coupes de `235`, l'étroite reste-t-elle sans écart cumulé pendant que l'aile "
                        "dérive ?")
LA_MESURE_DECLAREE = ("les coupes de `235` tendues de la troisième ligne de `236` à la colonne qu'elle rejoint, les "
                      "sous-boucles de l'aile, de l'étroite et de la large dans chaque intervalle, et leurs profils")


# ─────────────────────────────── ce que `235` et `236` publient ───────────────────────────────

def _lire(chemin: Path, nom: str, cles) -> dict:
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable") or any(not d.get(c) for c in cles):
        return {"decidable": False, "raison": f"`{nom}` ne publie pas {', '.join(cles)}"}
    return d


def ce_que_235_a_publie(chemin: Path = CE_QUE_235_A_PUBLIE) -> dict:
    """Le découpage de l'aile, ses coupes relues et l'analyse de ses sous-boucles, tels que `235` les publie."""
    d = _lire(chemin, "235", ("laile", "le_decoupage", "les_bandes", "les_bandes_declarees", "par_sous_boucle"))
    if not d.get("decidable"):
        return d
    return {"decidable": True, "aile": d["laile"], "decoupage": d["le_decoupage"], "bandes": d["les_bandes_declarees"],
            "publiees": d["les_bandes"], "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()},
            "par_sous_boucle": d["par_sous_boucle"]}


def ce_que_236_a_publie(chemin: Path = CE_QUE_236_A_PUBLIE) -> dict:
    """La troisième ligne, ses bandes relues et l'analyse des trois boucles, tels que `236` les publie."""
    d = _lire(chemin, "236", ("laile", "la_troisieme_ligne", "les_bandes", "les_bandes_declarees", "par_boucle"))
    if not d.get("decidable"):
        return d
    return {"decidable": True, "aile": d["laile"], "ligne": d["la_troisieme_ligne"], "bandes": d["les_bandes_declarees"],
            "publiees": d["les_bandes"], "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()},
            "par_boucle": d["par_boucle"]}


# ─────────────────────────────── les coupes, reprises ───────────────────────────────

def les_coupes_de_letroite(A: np.ndarray, coupes235, de: int, a: int, k: int, tenues=None) -> list[int]:
    """Les coupes de `235`, gardées là où la bande de rangées de `de` à `a` tient ; les deux bouts toujours."""
    PR, PC = tenues if tenues is not None else les_tenues(np.asarray(A, dtype=bool), int(k))
    cs = [int(c) for c in coupes235]
    return [cs[0]] + [c for c in cs[1:-1] if tient(PR, PC, "rangees", c, de, a)] + [cs[-1]]


def les_bandes_des_coupes_de_letroite(coupes, de: int, a: int, k: int) -> list[dict]:
    """Les coupes intérieures de l'étroite, à lire."""
    return [{"cle": f"rangees_{c}_{de}_{a}", "le_sens": "rangees", "le_centre": int(c),
             "les_lignes": les_rangees_a_lire(int(c), int(k)), "de": int(de), "a": int(a)} for c in coupes[1:-1]]


def les_intervalles(coupes) -> list[list[int]]:
    return [[int(coupes[j]), int(coupes[j + 1])] for j in range(len(coupes) - 1)]


# ─────────────────────────────── le verdict ───────────────────────────────

def les_franchissements(profil: list[dict], demi: float) -> list[dict]:
    """Les coupes où le cumul atteint le demi-feuillet."""
    return [p for p in profil if abs(float(p["le_cumul_en_voxels"])) >= float(demi)]


def _ce_qui_reste(sans_coupe: bool, ouverte: bool, franchit: bool) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if sans_coupe:
        return "AUCUNE COUPE DE `235` NE TIENT DANS L'ÉTROITE : ELLE NE SE DÉCOUPE PAS"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE SOUS-BOUCLE OUVERTE"
    if franchit:
        return ("À NEUF LIGNES, L'ÉTROITE ATTEINT LE DEMI-FEUILLET EN CHEMIN : SES DEUX COLONNES NE S'ACCORDENT QU'AU "
                "BOUT")
    return "À NEUF LIGNES, L'ÉTROITE RESTE SOUS LE DEMI-FEUILLET TOUT DU LONG : SES DEUX COLONNES S'ACCORDENT"


def le_verdict_de_letroite(combien: int, par_famille: dict, demi: float, k1: int) -> dict:
    """Le verdict à la plus large, depuis les sous-boucles des trois familles."""
    kk = str(k1)
    base = {"la_largeur_jugee": int(k1), "combien_de_sous_boucles": int(combien)}
    if int(combien) < 2:
        return {**base, "les_sous_boucles_ouvertes": [], "letroite_franchit": False, "letroite_reste_dessous": False,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(True, False, False)}
    ouv = sorted({tuple(sb["entre"]) for n in LES_FAMILLES for sb in par_famille[n]
                  if not sb["par_largeur"][kk]["fermable"]})
    if ouv:
        return {**base, "les_sous_boucles_ouvertes": [list(x) for x in ouv], "letroite_franchit": False,
                "letroite_reste_dessous": False, "ce_qui_reste_a_mesurer": _ce_qui_reste(False, True, False)}
    prof = {n: le_profil(par_famille[n], k1) for n in LES_FAMILLES}
    fr = {n: les_franchissements(prof[n], demi) for n in LES_FAMILLES}
    pic = max(prof["letroite"], key=lambda p: abs(float(p["le_cumul_en_voxels"])))
    grande = max(par_famille["la_large"], key=lambda sb: abs(float(sb["par_largeur"][kk]["la_fermeture_en_voxels"])))
    return {**base, "les_sous_boucles_ouvertes": [], "letroite_franchit": bool(fr["letroite"]),
            "letroite_reste_dessous": not fr["letroite"],
            "le_pic_de_letroite": pic, "les_franchissements": fr,
            "la_plus_grande_de_la_large": {"entre": grande["entre"],
                                           "la_fermeture_en_voxels": grande["par_largeur"][kk]["la_fermeture_en_voxels"]},
            "ce_qui_reste_a_mesurer": _ce_qui_reste(False, False, bool(fr["letroite"]))}


# ─────────────────────────────── la mesure ───────────────────────────────

def les_sources_de_237(par219, par223, par224, par232, par233, par234, par235, par236) -> dict:
    """Ce qui contrôle une coupe neuve : les sources de `235`, ses coupes, et les bandes de `236`."""
    out = les_sources_de_235(par219, par223, par224, par232, par233, par234)
    for nom, par in (("235", par235), ("236", par236)):
        for b in par["bandes"]:
            out[f"{nom} {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                        "pas": les_pas_dune_bande(par["relues"][b["cle"]])}
    return out


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par234: dict | None = None,
            par235: dict | None = None, par236: dict | None = None, lire=None, tirages: int | None = None,
            demi: float | None = None) -> dict:
    """Les coupes de l'étroite, leur lecture, puis les trois familles de sous-boucles — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    par235 = ce_que_235_a_publie() if par235 is None else par235
    par236 = ce_que_236_a_publie() if par236 is None else par236
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("234", par234), ("235", par235), ("236", par236)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    demi = float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi)
    aile = par235["aile"]
    tl = par236["ligne"]
    if aile["les_coins"] != par236["aile"]["les_coins"] or aile["le_cote"] not in ("droite", "gauche") \
            or tl["le_sens"] != "colonnes":
        return {**base, "decidable": False, "raison": "`235` et `236` ne parlent pas de la même aile de colonnes"}
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    for nom, par in (("234", par234), ("235", par235), ("236", par236)):
        c_ = la_presence_retombe(A, par["bandes"], par["publiees"])
        base[f"la_presence_contre_{nom}"] = c_
        if not c_.get("decidable"):
            return {**base, "decidable": False, "raison": c_.get("raison")}
    k1 = les_largeurs()[-1]
    cote = aile["le_cote"]
    lo, hi = int(aile["les_coins"][0]), int(aile["les_coins"][1])
    c_ligne, c_proche, c_loin = int(tl["la_ligne"]), int(tl["la_plus_proche"]), int(tl["la_plus_loin"])
    de, a = min(c_ligne, c_proche), max(c_ligne, c_proche)
    coupes = les_coupes_de_letroite(A, par235["decoupage"]["les_coupes"], de, a, k1)
    base.update({"laile": aile, "la_troisieme_ligne": tl, "les_coupes_de_235": par235["decoupage"]["les_coupes"],
                 "les_coupes_de_letroite": coupes, "les_intervalles": les_intervalles(coupes)})
    if len(coupes) < 3:
        return {**base, "decidable": True, "le_verdict": le_verdict_de_letroite(len(coupes) - 1, {}, demi, k1)}
    bandes = les_bandes_des_coupes_de_letroite(coupes, de, a, k1)
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"graine": int(g), "tirages": t_, "la_regle_de_225": par225["la_regle"],
                 "le_plus_long_trou_franchi_par_225": int(plus_long), "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des coupes reprises"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_croisee(nouvelles, les_sources_de_237(par219, par223, par224, par232, par233, par234,
                                                                par235, par236))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    daile = {**par234["ailes"][cote], "le_cote": cote}
    b234 = [b for b in par234["bandes"] if b in les_bandes_de_laile(daile, par233["coins"], k1)]
    pas = les_pas_de_laile(daile, par233["coins"], b234, par234["relues"], par233)
    for relu_, bs_ in ((par235["relues"], par235["bandes"]), (par236["relues"], par236["bandes"]), (relues, bandes)):
        for cle, x in les_pas_des_bandes(relu_, bs_).items():
            pas[cle] = _fusionner(pas.get(cle) or {}, x)
    lignes = {"laile": (min(c_proche, c_loin), max(c_proche, c_loin)), "letroite": (de, a),
              "la_large": (min(c_ligne, c_loin), max(c_ligne, c_loin))}
    par_famille = {}
    for n in LES_FAMILLES:
        p_, q_ = lignes[n]
        sbs = []
        for r_, s_ in les_intervalles(coupes):
            co = [r_, s_, p_, q_]
            x = analyser(pas, co, par225["la_regle"], plus_long, g, t_)
            if not x.get("decidable"):
                return {**base, "decidable": False, "raison": f"la sous-boucle {n} {co} : {x.get('raison')}",
                        "la_reproduction": rep}
            sbs.append({"entre": [r_, s_], "les_coins": co, **x})
        par_famille[n] = sbs
    pub235 = {tuple(sb["entre"]): sb["par_largeur"] for sb in par235["par_sous_boucle"]}
    for sb in par_famille["laile"]:
        y_ = pub235.get(tuple(sb["entre"]))
        if y_ is None:
            continue
        for k, x in sb["par_largeur"].items():
            y = y_.get(k) or {}
            if bool(x["fermable"]) != bool(y.get("fermable")) or (
                    x["fermable"] and abs(float(x["la_fermeture_en_voxels"]) - float(y["la_fermeture_en_voxels"]))
                    > 2 * L_ARRONDI + 1e-9):
                return {**base, "decidable": False, "la_reproduction": rep,
                        "raison": f"à {k} lignes, la sous-boucle de l'aile {sb['entre']} ne retombe pas sur `235`"}
    par_intervalle = []
    for j in range(len(coupes) - 1):
        emb = lemboitement_des_trois({n: par_famille[n][j] for n in LES_FAMILLES}, "colonnes", c_proche)
        if not emb.get("decidable"):
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"l'intervalle {par_famille['laile'][j]['entre']} : {emb.get('raison')}"}
        par_intervalle.append({"entre": par_famille["laile"][j]["entre"],
                               "combien_de_largeurs_jugees": emb["combien_de_largeurs_jugees"]})
    emb_e = lemboitement(par_famille["letroite"], par236["par_boucle"]["letroite"], cote)
    if not emb_e.get("decidable"):
        return {**base, "decidable": False, "raison": emb_e.get("raison"), "la_reproduction": rep}
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_famille": par_famille, "lemboitement_par_intervalle": par_intervalle, "lemboitement_de_letroite": emb_e,
            "les_profils": {n: le_profil(par_famille[n], k1) for n in LES_FAMILLES},
            "le_verdict": le_verdict_de_letroite(len(coupes) - 1, par_famille, demi, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"aile : {r['laile']}")
    print(f"troisième ligne : {r['la_troisieme_ligne']}")
    print(f"coupes de l'étroite : {r['les_coupes_de_letroite']}")
    if "par_famille" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures, écart {rp['lecart_le_plus_grand']}, "
              f"{sorted({k.split('×')[1] for k in rp['par_croisement']})}")
        print(f"emboîtement de l'étroite : {r['lemboitement_de_letroite']}")
        print(f"emboîtement par intervalle : {[x['combien_de_largeurs_jugees'] for x in r['lemboitement_par_intervalle']]}")
        for j in range(len(r["par_famille"]["laile"])):
            ls = {n: r["par_famille"][n][j]["par_largeur"]["9"] for n in LES_FAMILLES}
            print(f"  {r['par_famille']['laile'][j]['entre']} · " + " · ".join(
                f"{n} {x['la_fermeture_en_voxels'] if x['fermable'] else 'OUVERT'}" for n, x in ls.items())
                + f" · nul étroite {ls['letroite']['le_nul']}")
        for n, p in r["les_profils"].items():
            print(f"profil {n} : {[q['le_cumul_en_voxels'] for q in p]}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

    from laquelle_des_deux_colonnes_derive import mesurer as mesurer_236
    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_sources_de_234
    from le_segment_au_dela_du_rectangle_se_relie_t_il import mesurer as mesurer_234
    from ou_laile_de_droite_se_separe import mesurer as mesurer_235
    from ou_sarrete_le_segment import les_sources
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

    # les coupes reprises
    Ap = np.ones((396, 285), dtype=bool)
    c235 = [26, 35, 44, 53, 62, 71, 80, 89, 98, 107, 116, 125, 134, 143, 153, 163, 173, 183, 193, 203, 213, 223]
    v("★★★★ sur une grille pleine, l'étroite garde toutes les coupes de 235",
      _ok(lambda: les_coupes_de_letroite(Ap, c235, 234, 243, 9) == c235))
    Ah = Ap.copy()
    Ah[100, 236] = False
    ch = _sur(les_coupes_de_letroite, Ah, c235, 234, 243, 9)
    v("★★★★ une coupe dont une ligne perd un chunk entre les deux colonnes est retirée, et elle seule",
      _ok(lambda: ch == [c for c in c235 if c != 98]), str(ch))
    Ab = Ap.copy()
    Ab[25, 240] = False
    Ab[33, 240] = False
    v("★★★ les deux bouts restent, même si leur bande ne tient pas : ce sont ceux que 236 a lus",
      _ok(lambda: les_coupes_de_letroite(Ab, c235, 234, 243, 9)[0] == 26
          and 35 not in les_coupes_de_letroite(Ab, c235, 234, 243, 9)))
    bd = _sur(les_bandes_des_coupes_de_letroite, c235, 234, 243, 9)
    v("★★★★ seules les coupes intérieures se lisent, tendues de la colonne 234 à la 243",
      _ok(lambda: len(bd) == 20 and bd[0]["cle"] == "rangees_35_234_243" and bd[0]["les_lignes"] == list(range(31, 40))
          and all((b["de"], b["a"]) == (234, 243) for b in bd)))
    v("★★★ les intervalles vont de coupe en coupe",
      les_intervalles([26, 35, 44]) == [[26, 35], [35, 44]])

    # le verdict, sur des sous-boucles fabriquées
    def _sb(e, L, fermable=True):  # noqa: E306
        return {"entre": list(e), "par_largeur": {"9": {"fermable": fermable, "la_fermeture_en_voxels": L}}}

    def _fam(ea, ee, el):  # noqa: E306
        es = [(0, 9), (9, 18), (18, 27)]
        return {"laile": [_sb(e, L) for e, L in zip(es, ea)], "letroite": [_sb(e, L) for e, L in zip(es, ee)],
                "la_large": [_sb(e, L) for e, L in zip(es, el)]}
    vd = le_verdict_de_letroite(3, _fam([-20, -20, 5], [2, -3, 1], [-18, -23, 6]), 36.0, 9)
    v("★★★★ une étroite dont le cumul reste sous le demi-feuillet : ses deux colonnes s'accordent",
      vd["letroite_reste_dessous"] and not vd["letroite_franchit"] and "RESTE SOUS" in vd["ce_qui_reste_a_mesurer"]
      and vd["le_pic_de_letroite"] == {"la_coupe": 9, "le_cumul_en_voxels": 2.0}
      and [p["la_coupe"] for p in vd["les_franchissements"]["laile"]] == [18]
      and vd["la_plus_grande_de_la_large"] == {"entre": [9, 18], "la_fermeture_en_voxels": -23}, str(vd))
    vf = le_verdict_de_letroite(3, _fam([-20, -20, 5], [20, 20, -39], [0, 0, -34]), 36.0, 9)
    v("★★★★ une étroite dont le cumul atteint le demi-feuillet en chemin : ses colonnes ne s'accordent qu'au bout",
      vf["letroite_franchit"] and not vf["letroite_reste_dessous"] and "EN CHEMIN" in vf["ce_qui_reste_a_mesurer"]
      and [p["la_coupe"] for p in vf["les_franchissements"]["letroite"]] == [18])
    fo = _fam([-20, -20, 5], [20, 20, -39], [0, 0, -34])
    fo["laile"][1] = _sb((9, 18), 0.0, fermable=False)
    vo = le_verdict_de_letroite(3, fo, 36.0, 9)
    v("★★★★ une sous-boucle ouverte, de n'importe quelle famille, prime",
      vo["les_sous_boucles_ouvertes"] == [[9, 18]] and not vo["letroite_franchit"] and not vo["letroite_reste_dessous"]
      and "OUVERTE" in vo["ce_qui_reste_a_mesurer"])
    v0 = _sur(le_verdict_de_letroite, 1, {}, 36.0, 9)
    v("★★★★ sans coupe, rien ne se juge", _ok(lambda: "NE SE DÉCOUPE PAS" in v0["ce_qui_reste_a_mesurer"]
                                              and not v0["letroite_reste_dessous"] and not v0["letroite_franchit"]))
    v("★★★ les quatre issues sont distinctes",
      len({_ce_qui_reste(a, b, c) for a, b, c in itertools.product((True, False), repeat=3)}) == 4)
    v("★★★ le demi-feuillet se compte en valeur absolue, et l'atteindre suffit",
      [p["la_coupe"] for p in les_franchissements([{"la_coupe": 1, "le_cumul_en_voxels": -36.0},
                                                    {"la_coupe": 2, "le_cumul_en_voxels": 35.9}], 36.0)] == [1])

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    v("★★★★ ce que 235 et 236 publient se relit, et parle de la même aile",
      _ok(lambda: ce_que_235_a_publie()["aile"]["les_coins"] == ce_que_236_a_publie()["aile"]["les_coins"]
          == [26, 223, 243, 260] and ce_que_236_a_publie()["ligne"]["la_ligne"] == 234))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[200:395, 250:281] = False

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _derive(f, r, c):  # noqa: E306
        # la colonne extérieure de droite dérive ; celle de gauche assez pour que son aile ne ferme pas
        return _champ(f, r, c) + (-0.15 if f == "v" and c >= 272 else 0.0) + (0.3 if f == "v" and c <= 11 else 0.0)

    def _aller_retour(f, r, c):  # noqa: E306
        # la troisième colonne s'écarte puis revient : l'étroite ferme au bout, pas en chemin
        x = _derive(f, r, c)
        if f == "v" and 230 <= c <= 238:
            x += 0.5 if 26 <= r < 110 else (-0.5 if 110 <= r < 195 else 0.0)
        return x

    def _sur_lempreinte(A_, champ):  # noqa: E306
        q2, q3 = copy.deepcopy(q232), copy.deepcopy(q233)
        for q in (q2, q3):
            for bb in q["bandes"]:
                for l_ in bb["les_lignes"]:
                    q["publiees"][bb["cle"]]["les_lectures"][str(l_)]["refuses"][ABSENT] = \
                        les_absents_dune_ligne(A_, bb["le_sens"], l_, bb["de"], bb["a"])
        autres = les_sources(p219, p223, p224, q2)

        def _lue_ailleurs(f, cle):  # noqa: E306
            return any(f in S_["pas"] and cle in S_["domaine"].get(f, ()) for S_ in autres.values())
        for bb in q3["bandes"]:
            rl = q3["relues"][bb["cle"]]
            f_long, f_trav = ("h", "v") if bb["le_sens"] == "rangees" else ("v", "h")
            for a_, s_ in rl["le_long"].items():
                for b_, t in s_.items():
                    r, c = (a_, b_) if bb["le_sens"] == "rangees" else (b_, a_)
                    if not _lue_ailleurs(f_long, (r, c)):
                        s_[b_] = (champ(f_long, r, c),) + tuple(t[1:])
            for r, s_ in rl["en_travers"].items():
                for c, t in s_.items():
                    if not _lue_ailleurs(f_trav, (r, c)):
                        s_[c] = (champ(f_trav, r, c),) + tuple(t[1:])
        q3["presence"] = {"decidable": True, "la_grille": [gy, gx], "les_pages": 1,
                          "les_rangees": ["".join("1" if x else "0" for x in r) for r in A_]}
        return q2, q3

    def _fabrique(bd_, src, champ):  # noqa: E306
        dom = le_domaine(bd_["le_sens"], bd_["les_lignes"], bd_["de"], bd_["a"])
        le_long_f, trav_f = (("h", "v") if bd_["le_sens"] == "rangees" else ("v", "h"))
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
                    pas_[f][cle] = champ(f, *cle)
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if bd_["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(Af, bd_["le_sens"], l_, bd_["de"], bd_["a"])}}
                    for l_ in bd_["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}

    def _publie(m_, lecteur):  # noqa: E306
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m.json"
            pj.write_text(json.dumps(m_, ensure_ascii=False))
            return lecteur(pj)

    def _scenario(champ):  # noqa: E306
        q2, q3 = _sur_lempreinte(Af, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda b: _fabrique(b, s0, champ), 49)
        q4 = _publie(m4, ce_que_234_a_publie)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        m5 = _sur(mesurer_235, None, p219, p223, p224, p225, q225, q2, q3, q4, lambda b: _fabrique(b, s1, champ), 49)
        m6 = _sur(mesurer_236, None, p219, p223, p224, p225, q225, q2, q3, q4, lambda b: _fabrique(b, s1, champ), 49)
        q5, q6 = _publie(m5, ce_que_235_a_publie), _publie(m6, ce_que_236_a_publie)
        s2 = les_sources_de_237(p219, p223, p224, q2, q3, q4, q5, q6) if q5.get("decidable") and q6.get(
            "decidable") else {}
        return q2, q3, q4, q5, q6, s2
    q232f, q233f, q234f, q235f, q236f, src2 = _scenario(_derive)
    v("★★★★ 234, 235 et 236 rejoués sur l'empreinte fabriquée : l'aile de droite, ses 18 sous-boucles, la colonne 234",
      _ok(lambda: q235f["aile"]["les_coins"] == [26, 195, 243, 276] and q235f["decoupage"]["combien_de_sous_boucles"]
          == 18 and q236f["ligne"]["la_ligne"] == 234), str(q235f.get("raison") or q236f.get("raison")))
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b)
        return _fabrique(b, src2, _derive)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f, _lit, 49, 36.0)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_famille" in m, str(m.get("raison")))
    v("★★★★ seules les coupes intérieures de l'étroite sont lues, aux rangées de 235",
      _ok(lambda: [b["le_centre"] for b in lus] == q235f["decoupage"]["les_coupes"][1:-1]
          and all((b["de"], b["a"]) == (234, 243) for b in lus)), str([b["cle"] for b in lus][:3]))
    v("★★★★ chaque coupe neuve est contrôlée par la colonne 243 de 233, la colonne 234 de 236 et la coupe de 235",
      _ok(lambda: all(any(k.startswith(f"{b['cle']}×233 ") for k in m["la_reproduction"]["par_croisement"])
                      and any(k.startswith(f"{b['cle']}×236 ") for k in m["la_reproduction"]["par_croisement"])
                      and any(k.startswith(f"{b['cle']}×235 ") for k in m["la_reproduction"]["par_croisement"])
                      for b in m["les_bandes_declarees"])), str(m.get("la_reproduction", {}).get("par_croisement")))
    v("★★★★ trois familles de 18 sous-boucles, sur les colonnes que 236 désigne",
      _ok(lambda: all(len(m["par_famille"][n]) == 18 for n in LES_FAMILLES)
          and m["par_famille"]["laile"][0]["les_coins"] == [26, 35, 243, 276]
          and m["par_famille"]["letroite"][0]["les_coins"] == [26, 35, 234, 243]
          and m["par_famille"]["la_large"][0]["les_coins"] == [26, 35, 234, 276]))
    v("★★★★ les sous-boucles de l'aile retombent sur 235, la large sur la somme des deux autres dans chaque intervalle",
      _ok(lambda: all(sb["par_largeur"]["9"]["la_fermeture_en_voxels"] == q235f["par_sous_boucle"][j]["par_largeur"]["9"]
                      ["la_fermeture_en_voxels"] for j, sb in enumerate(m["par_famille"]["laile"]))
          and all(x["combien_de_largeurs_jugees"] >= 1 for x in m["lemboitement_par_intervalle"])))
    v("★★★★ les sous-boucles de l'étroite somment à ce que 236 publie pour l'étroite",
      _ok(lambda: m["lemboitement_de_letroite"]["par_largeur"]["9"]["jugeable"]), str(m.get("lemboitement_de_letroite")))
    v("★★★★ la colonne extérieure dérive : l'étroite reste sous le demi-feuillet tout du long",
      _ok(lambda: m["le_verdict"]["letroite_reste_dessous"] and m["le_verdict"]["ce_qui_reste_a_mesurer"]
          == _ce_qui_reste(False, False, False)), str(m.get("le_verdict")))
    v("★★★★ les profils et le verdict sont ceux des trois familles",
      _ok(lambda: m["les_profils"] == {n: le_profil(m["par_famille"][n], 9) for n in LES_FAMILLES}
          and m["le_verdict"] == le_verdict_de_letroite(18, m["par_famille"], 36.0, 9)))
    q232a, q233a, q234a, q235a, q236a, src_a = _scenario(_aller_retour)
    ma = _sur(mesurer, None, p219, p223, p224, p225, q225, q232a, q233a, q234a, q235a, q236a,
              lambda b: _fabrique(b, src_a, _aller_retour), 49, 36.0)
    v("★★★★ une troisième colonne qui s'écarte puis revient : l'étroite atteint le demi-feuillet en chemin",
      _ok(lambda: ma["le_verdict"]["letroite_franchit"] and abs(ma["les_profils"]["letroite"][-1]["le_cumul_en_voxels"])
          < 36.0), str(ma.get("raison") or ma.get("le_verdict")))

    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src2, _derive)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f,
                                   _menteuse, 49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src2, _derive)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une coupe qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f,
                                       _decale, 49, 36.0).get("raison")))
    emb_vrai, jonctions = globals()["lemboitement_des_trois"], []

    def _emb_espion(par_, sens_, jonction_):  # noqa: E306
        jonctions.append(int(jonction_))
        return emb_vrai(par_, sens_, jonction_)
    globals()["lemboitement_des_trois"] = _emb_espion
    try:
        _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f,
             lambda b: _fabrique(b, src2, _derive), 49, 36.0)
    finally:
        globals()["lemboitement_des_trois"] = emb_vrai
    v("★★★★ dans chaque intervalle, la jonction de l'emboîtement est la colonne commune à l'aile et à l'étroite",
      len(jonctions) == 18 and set(jonctions) == {243}, str(sorted(set(jonctions))))
    q235e = copy.deepcopy(q235f)
    if q235e.get("decidable"):
        q235e["par_sous_boucle"][3]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ une sous-boucle de l'aile qui ne retombe pas sur ce que 235 publie est refusée",
      "ne retombe pas sur `235`" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235e,
                                             q236f, lambda b: _fabrique(b, src2, _derive), 49, 36.0).get("raison")))
    q236e = copy.deepcopy(q236f)
    if q236e.get("decidable"):
        q236e["par_boucle"]["letroite"]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des sous-boucles de l'étroite qui ne somment pas à ce que 236 publie sont refusées",
      "l'emboîtement ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
                                                  q235f, q236e, lambda b: _fabrique(b, src2, _derive), 49, 36.0)
                                             .get("raison")))
    analyser_vrai = globals()["analyser"]

    def _analyser_faux(pas_, co, *a_, **kw):  # noqa: E306
        r = analyser_vrai(pas_, co, *a_, **kw)
        if co[2:] == [234, 276] and co[0] == 44 and r.get("decidable"):
            r["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
        return r
    globals()["analyser"] = _analyser_faux
    try:
        me = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f,
                  lambda b: _fabrique(b, src2, _derive), 49, 36.0)
    finally:
        globals()["analyser"] = analyser_vrai
    v("★★★★ une sous-boucle large qui n'est pas la somme des deux autres est refusée, par son intervalle",
      "l'intervalle [44, 53]" in str(me.get("raison")) and "l'emboîtement ne retombe pas" in str(me.get("raison")),
      str(me.get("raison")))
    q236x = copy.deepcopy(q236f)
    if q236x.get("decidable"):
        q236x["aile"] = {**q236x["aile"], "les_coins": [26, 195, 243, 277]}
    v("★★★★ 235 et 236 qui ne parlent pas de la même aile sont refusés",
      "pas de la même aile" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f,
                                        q236x, _lit, 49, 36.0).get("raison")))
    q236p = copy.deepcopy(q236f)
    if q236p.get("decidable"):
        b0_ = q236p["bandes"][0]
        q236p["publiees"][b0_["cle"]]["les_lectures"][str(b0_["les_lignes"][0])]["refuses"][ABSENT] += 1
    v("★★★★ une présence qui ne retombe pas sur les bandes de 236 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236p,
                                   _lit, 49, 36.0).get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f, None, 49, 36.0)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235f, q236f, None, 49, 36.0)
    v("★★★★ une coupe lue sur d'autres lignes que celles reprises est refusée",
      "pas celle des coupes reprises" in str(mf.get("raison")), str(mf.get("raison")))
    v("★★★★ la mesure se rejoue depuis sa lecture publiée, à l'identique",
      _ok(lambda: json.dumps(mj, sort_keys=True) == json.dumps(m, sort_keys=True)))

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
        par233, par235, par236 = ce_que_233_a_publie(), ce_que_235_a_publie(), ce_que_236_a_publie()
        for nom, par in (("233", par233), ("235", par235), ("236", par236)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        tl = par236["ligne"]
        de, a_ = min(int(tl["la_ligne"]), int(tl["la_plus_proche"])), max(int(tl["la_ligne"]), int(tl["la_plus_proche"]))
        coupes = les_coupes_de_letroite(A, par235["decoupage"]["les_coupes"], de, a_, k1)
        print(f"coupes de l'étroite : {coupes}", flush=True)
        if len(coupes) < 3:
            return 0
        bandes = les_bandes_des_coupes_de_letroite(coupes, de, a_, k1)
        print(f"bandes : {[(b['cle'], len(b['les_lignes']) * (b['a'] - b['de'] + 1)) for b in bandes]}", flush=True)
        deja = json.loads(a.lire.read_text()) if a.lire.exists() else {}
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": d}, ensure_ascii=False))
            print(f"écrit : {a.lire} ({len(d)} bandes)", flush=True)
        lu = lire_les_bandes(bandes, deja.get("les_bandes") or {}, ecrire)
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
