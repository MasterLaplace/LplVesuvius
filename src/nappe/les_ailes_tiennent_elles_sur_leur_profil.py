"""Les ailes du haut et de gauche de `234`, jugées sur leur profil et non à leur bout, restent-elles sous le demi-feuillet ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE, ET AVANT QUE LES COUPES NE SOIENT
DÉRIVÉES. Ce qui était vu avant d'écrire : ce que `234`, `235` et `239` publient, et leurs figures.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P85`. `234` compte que les boucles qui ferment entourent 0,9153 de
l'empreinte, mais en jugeant chaque aile à son bout. Sur son profil, l'aile de droite franchit le demi-feuillet
(`237`), et le rectangle, 0,8633 de l'empreinte, reste dessous (`238`, `239`). Les ailes du haut et de gauche ferment
à −2,0133 et 6,9445 à leur bout ; rien ne dit encore ce que font leurs boucles partielles.

## Les ailes jugées, désignées

Les ailes qui ferment dans `234`, sauf la plus lâche : c'est celle que `235` a découpée, et elle doit l'être, sinon
refus. Aucune n'est choisie.

## Les coupes, dérivées

La règle de `235`, aile par aile : des bandes de travers de neuf lignes, parallèles aux deux bouts, qui tiennent
d'un long côté à l'autre ; deux coupes voisines à neuf lignes au moins ; le plus de sous-boucles, puis le plus petit
des plus grands écarts, puis les coupes les plus tôt. ⚠⚠ Le plus grand écart entre deux coupes est comparé à la
PORTÉE de `239`, la plus longue traversée que `235` publie : un écart au-delà est nommé, parce qu'une traversée de
cette durée pourrait s'y cacher.

## Ce qui se lit, et ce qui le contrôle

Les coupes intérieures seules, par le lecteur de `224`. ⚠⚠ Les bouts et les longs côtés ne sont pas relus : leurs pas
sont ceux que `233` et `234` publient. ⚠⚠⚠ Partout où une coupe croise une bande publiée — `219`, `223`, `224`, `232`,
`233`, `234` —, les pas relus retombent à l'arrondi, sinon refus ; une coupe qui ne croise aucune bande publiée est
refusée. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque sous-boucle, à chaque largeur de l'échelle de `218`. ⚠⚠⚠ Les sous-boucles d'une aile
somment à la fermeture que `234` publie pour elle, là où aucune n'a de trou le long des longs côtés, à l'arrondi près,
sinon refus. LE PROFIL : la fermeture cumulée, coupe après coupe, d'un bout de l'aile à l'autre. LA COUVERTURE : la
part de l'empreinte qu'entourent les boucles jugées sur leur profil et qui restent dessous — le rectangle si `239` le
dit, et les ailes jugées ici.

## Les issues, exclusives, jugées à neuf lignes

- aucune autre aile ne ferme dans `234` : il n'y a rien à juger, et rien n'est lu ;
- une sous-boucle garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- le profil d'une aile atteint le demi-feuillet à une coupe : elle ne ferme qu'au bout ;
- une aile ne se découpe pas : son profil n'est pas vu ;
- chaque profil reste dessous à chaque coupe.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une traversée plus courte que l'écart entre deux coupes ; ni lequel des deux
longs côtés d'une aile dérive, si l'une franchit.

Usage :
    uv run python src/nappe/les_ailes_tiennent_elles_sur_leur_profil.py --verifier
    uv run python src/nappe/les_ailes_tiennent_elles_sur_leur_profil.py --lire <lecture.json>
    uv run python src/nappe/les_ailes_tiennent_elles_sur_leur_profil.py --depuis <lecture.json> \\
        --json docs/mesures/les_ailes_tiennent_elles_sur_leur_profil.json
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

from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_rectangle_entre_ses_coupes import la_portee, les_ecarts_au_dela  # noqa: E402
from le_segment_au_dela_du_rectangle_se_relie_t_il import (LES_COTES,  # noqa: E402
                                                           ce_que_233_a_publie, la_couverture,
                                                           les_bandes_de_laile, les_pas_de_laile, les_tenues)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from letroite_reste_t_elle_sans_ecart import ce_que_235_a_publie, les_franchissements  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import (ce_que_234_a_publie, laile_la_plus_lache,  # noqa: E402
                                          le_profil, lemboitement, les_bandes_des_coupes, les_coupes,
                                          les_sources_de_235, les_sous_boucles)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_239_A_PUBLIE = MESURES / "le_rectangle_entre_ses_coupes.json"

LA_QUESTION_DECLAREE = ("les ailes du haut et de gauche de `234`, jugées sur leur profil et non à leur bout, "
                        "restent-elles sous le demi-feuillet ?")
LA_MESURE_DECLAREE = ("chaque aile qui ferme dans `234`, sauf celle que `235` a découpée, découpée par la règle de "
                      "`235`, l'instrument de `228` sur chaque sous-boucle, et la fermeture cumulée coupe après coupe")


def ce_que_239_a_publie(chemin: Path = CE_QUE_239_A_PUBLIE) -> dict:
    """Le rectangle, et si son profil reste sous le demi-feuillet, tels que `239` les publie."""
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent ou illisible : {e}"}
    if not d.get("decidable") or not d.get("le_rectangle") or not d.get("le_verdict"):
        return {"decidable": False, "raison": "`239` ne publie pas son rectangle ou son verdict"}
    return {"decidable": True, "le_rectangle": [int(x) for x in d["le_rectangle"]],
            "reste_dessous": bool(d["le_verdict"].get("reste_dessous"))}


# ─────────────────────────────── les ailes jugées ───────────────────────────────

def les_ailes_jugees(par234: dict, lache: str | None) -> list[str]:
    """Les ailes qui ferment dans `234`, sauf la plus lâche, dans l'ordre haut, droite, bas, gauche."""
    ferment = par234["verdict"].get("les_ailes_qui_ferment") or []
    return [c for c in LES_COTES if c in ferment and c != lache]


def lentre(cote: str, sb) -> list[int]:
    """Les deux coupes qui bornent une sous-boucle, le long de l'aile."""
    return [int(x) for x in (sb[:2] if cote in ("droite", "gauche") else sb[2:])]


# ─────────────────────────────── le verdict ───────────────────────────────

def le_verdict_de_laile(combien: int, par_sb: list[dict], demi: float, k1: int) -> dict:
    """Le verdict d'une aile, à la plus large, depuis ses sous-boucles."""
    kk = str(k1)
    base = {"la_largeur_jugee": int(k1), "combien_de_sous_boucles": int(combien)}
    if int(combien) < 2:
        return {**base, "sans_coupe": True, "les_sous_boucles_ouvertes": [], "franchit": False,
                "reste_dessous": False}
    ouv = [sb["entre"] for sb in par_sb if not sb["par_largeur"][kk]["fermable"]]
    if ouv:
        return {**base, "sans_coupe": False, "les_sous_boucles_ouvertes": ouv, "franchit": False,
                "reste_dessous": False}
    prof = le_profil(par_sb, k1)
    fr = les_franchissements(prof, demi)
    pic = max(prof, key=lambda p: abs(float(p["le_cumul_en_voxels"])))
    return {**base, "sans_coupe": False, "les_sous_boucles_ouvertes": [], "franchit": bool(fr),
            "reste_dessous": not fr, "le_pic": pic, "les_franchissements": fr}


def _ce_qui_reste(aucune: bool, ouverte: bool, franchit: bool, sans_coupe: bool) -> str:
    """Les cinq issues, EXCLUSIVES, dans cet ordre de priorité."""
    if aucune:
        return "AUCUNE AUTRE AILE NE FERME DANS `234` : IL N'Y A RIEN À JUGER"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE SOUS-BOUCLE OUVERTE"
    if franchit:
        return "À NEUF LIGNES, LE PROFIL D'UNE AILE ATTEINT LE DEMI-FEUILLET À UNE COUPE : ELLE NE FERME QU'AU BOUT"
    if sans_coupe:
        return "UNE AILE NE SE DÉCOUPE PAS : SON PROFIL N'EST PAS VU"
    return "À NEUF LIGNES, LE PROFIL DE CHAQUE AILE RESTE SOUS LE DEMI-FEUILLET À CHAQUE COUPE"


def le_verdict_des_ailes(jugees: list[str], par_aile: dict, k1: int) -> dict:
    """Le verdict d'ensemble, depuis le verdict de chaque aile jugée."""
    vs = {c: par_aile[c]["le_verdict"] for c in jugees}
    ouv = [c for c in jugees if vs[c]["les_sous_boucles_ouvertes"]]
    fr = [c for c in jugees if vs[c]["franchit"]]
    sc = [c for c in jugees if vs[c]["sans_coupe"]]
    dessous = [c for c in jugees if vs[c]["reste_dessous"]]
    return {"la_largeur_jugee": int(k1), "les_ailes_jugees": list(jugees), "les_ailes_ouvertes": ouv,
            "les_ailes_qui_franchissent": fr, "les_ailes_sans_coupe": sc, "les_ailes_qui_restent_dessous": dessous,
            "chaque_aile_reste_dessous": bool(jugees) and dessous == list(jugees),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(not jugees, bool(ouv), bool(fr), bool(sc))}


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par234: dict | None = None,
            par235: dict | None = None, par239: dict | None = None, lire=None, tirages: int | None = None,
            demi: float | None = None) -> dict:
    """Les ailes jugées, leurs coupes dérivées, leur lecture puis l'analyse — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    par235 = ce_que_235_a_publie() if par235 is None else par235
    par239 = ce_que_239_a_publie() if par239 is None else par239
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("234", par234), ("235", par235), ("239", par239)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    demi = float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi)
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    c_ = la_presence_retombe(A, par234["bandes"], par234["publiees"])
    base["la_presence_contre_234"] = c_
    if not c_.get("decidable"):
        return {**base, "decidable": False, "raison": c_.get("raison")}
    lache = laile_la_plus_lache(par234)
    lache_c = lache["le_cote"] if lache else None
    if lache_c is not None and (par235.get("aile") or {}).get("le_cote") != lache_c:
        return {**base, "decidable": False, "raison": "`235` n'a pas découpé l'aile la plus lâche de `234`"}
    k1 = les_largeurs()[-1]
    coins233 = [int(x) for x in par233["coins"]]
    jugees = les_ailes_jugees(par234, lache_c)
    portee = la_portee(par235.get("profil") or [], demi)
    tenues = les_tenues(A, k1)
    decs = {}
    for c in jugees:
        d_ = les_coupes(A, par234["ailes"][c]["les_coins"], c, k1, tenues)
        decs[c] = {**d_, "les_ecarts_au_dela_de_la_portee": (les_ecarts_au_dela(d_["les_coupes"], portee)
                                                             if portee is not None else None)}
    base.update({"laile_de_235": lache_c, "les_ailes_jugees": jugees, "la_portee": portee, "les_decoupages": decs,
                 "le_rectangle_de_239": {"les_coins": par239["le_rectangle"],
                                         "reste_dessous": par239["reste_dessous"]}})
    if not jugees:
        return {**base, "decidable": True, "le_verdict": le_verdict_des_ailes([], {}, k1)}
    bandes = [b for c in jugees if decs[c]["combien_de_sous_boucles"] >= 2 for b in les_bandes_des_coupes(decs[c], k1)]
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if bandes and depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    elif bandes:
        lu = lire_les_bandes(bandes, lire=lire)
    else:
        lu = {"decidable": True, "les_bandes": {}}
    base.update({"graine": int(g), "tirages": t_, "la_regle_de_225": par225["la_regle"],
                 "le_plus_long_trou_franchi_par_225": int(plus_long), "les_bandes_declarees": bandes,
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if (sorted(pub) != sorted(b["cle"] for b in bandes)
            or any(_la_definition(pub[b["cle"]]) != _la_definition(b) for b in bandes)):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des coupes dérivées"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    rep = {"decidable": True, "combien_de_coutures_relues": 0, "par_croisement": {}, "lecart_le_plus_grand": 0.0}
    if bandes:
        nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
        rep = la_reproduction_croisee(nouvelles, les_sources_de_235(par219, par223, par224, par232, par233, par234))
        if not rep.get("decidable"):
            return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    par_aile = {}
    for c in jugees:
        dec = decs[c]
        coins = [int(x) for x in par234["ailes"][c]["les_coins"]]
        if dec["combien_de_sous_boucles"] < 2:
            par_aile[c] = {"les_coins": coins, "le_verdict": le_verdict_de_laile(dec["combien_de_sous_boucles"], [],
                                                                                 demi, k1)}
            continue
        daile = {**par234["ailes"][c], "le_cote": c}
        b234 = [b for b in par234["bandes"] if b in les_bandes_de_laile(daile, coins233, k1)]
        pas = les_pas_de_laile(daile, coins233, b234, par234["relues"], par233)
        pas.update(les_pas_des_bandes(relues, les_bandes_des_coupes(dec, k1)))
        par_sb = []
        for sb in les_sous_boucles(c, coins, dec["les_coupes"]):
            a = analyser(pas, sb, par225["la_regle"], plus_long, g, t_)
            if not a.get("decidable"):
                return {**base, "decidable": False, "raison": f"l'aile {c}, la sous-boucle {sb} : {a.get('raison')}",
                        "la_reproduction": rep}
            par_sb.append({"entre": lentre(c, sb), "les_coins": sb, **a})
        emb = lemboitement(par_sb, par234["par_aile"][c], c)
        if not emb.get("decidable"):
            return {**base, "decidable": False, "raison": f"l'aile {c} : {emb.get('raison')}", "la_reproduction": rep,
                    "lemboitement": emb}
        par_aile[c] = {"les_coins": coins, "par_sous_boucle": par_sb, "lemboitement": emb,
                       "le_profil": le_profil(par_sb, k1),
                       "le_verdict": le_verdict_de_laile(dec["combien_de_sous_boucles"], par_sb, demi, k1)}
    v = le_verdict_des_ailes(jugees, par_aile, k1)
    tiennent = ([par239["le_rectangle"]] if par239["reste_dessous"] else []) + \
        [par_aile[c]["les_coins"] for c in v["les_ailes_qui_restent_dessous"]]
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_aile": par_aile, "le_verdict": v,
            "la_couverture": {"par_le_rectangle": la_couverture(A, [coins233], k1),
                              "par_les_boucles_qui_restent_dessous_sur_leur_profil": la_couverture(A, tiennent, k1)}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"aile de 235 : {r['laile_de_235']} · ailes jugées : {r['les_ailes_jugees']} · portée : {r['la_portee']}")
    for c, d in r["les_decoupages"].items():
        print(f"  {c} : {d['combien_de_sous_boucles']} sous-boucles, plus grand écart {d['le_plus_grand_ecart']}, "
              f"coupes {d['les_coupes']}, au-delà de la portée {d['les_ecarts_au_dela_de_la_portee']}")
    if "par_aile" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r.get('la_presence_contre_la_lecture')}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        for c, pa in r["par_aile"].items():
            print(f"AILE {c} · {pa['les_coins']}")
            if "lemboitement" in pa:
                print(f"  emboîtement : {pa['lemboitement']}")
            for sb in pa.get("par_sous_boucle") or []:
                x = sb["par_largeur"][str(pa["le_verdict"]["la_largeur_jugee"])]
                if not x["fermable"]:
                    print(f"  {sb['entre']} · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
                    continue
                print(f"  {sb['entre']} · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']} · "
                      f"nul {x['le_nul']}")
            print(f"  profil : {pa.get('le_profil')}")
            print(f"  verdict : {pa['le_verdict']}")
        print(f"couverture : {r['la_couverture']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_sources_de_234
    from le_segment_au_dela_du_rectangle_se_relie_t_il import mesurer as mesurer_234
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

    # les ailes jugées
    def _p234(ferment):  # noqa: E306
        return {"verdict": {"les_ailes_qui_ferment": ferment}}
    v("★★★★ les ailes jugées sont celles qui ferment, sauf la plus lâche, dans l'ordre des côtés",
      les_ailes_jugees(_p234(["droite", "gauche", "haut"]), "droite") == ["haut", "gauche"])
    v("★★★ une aile qui ne ferme pas n'est pas jugée ; sans aile la plus lâche, toutes celles qui ferment le sont",
      les_ailes_jugees(_p234(["droite", "haut"]), "droite") == ["haut"]
      and les_ailes_jugees(_p234(["haut"]), None) == ["haut"])
    v("★★★★ une sous-boucle est bornée par ses rangées sur une aile de côté, par ses colonnes sur une aile du haut",
      lentre("gauche", [216, 225, 13, 22]) == [216, 225] and lentre("haut", [14, 26, 32, 41]) == [32, 41])

    # le verdict d'une aile et d'ensemble, sur des sous-boucles fabriquées
    def _x(L, fermable=True):  # noqa: E306
        return {"fermable": fermable, "la_fermeture_en_voxels": L, "sous_le_demi_pli": abs(L) < 36, "les_trous": []}

    def _sb(e, L, **kw):  # noqa: E306
        return {"entre": list(e), "par_largeur": {"9": _x(L, **kw)}}
    sbf = [_sb((0, 9), 20.0), _sb((9, 18), 10.0), _sb((18, 27), -25.0)]
    va = le_verdict_de_laile(3, [_sb((0, 9), 20.0), _sb((9, 18), 16.0), _sb((18, 27), -30.0)], 36.0, 9)
    v("★★★★ un profil qui atteint exactement le demi-feuillet en chemin franchit, même si l'aile ferme au bout, et "
      "son pic est pris en chemin",
      va["franchit"] and not va["reste_dessous"]
      and va["les_franchissements"] == [{"la_coupe": 18, "le_cumul_en_voxels": 36.0}]
      and va["le_pic"] == {"la_coupe": 18, "le_cumul_en_voxels": 36.0})
    vd = le_verdict_de_laile(3, sbf, 36.0, 9)
    v("★★★★ un profil qui reste sous le demi-feuillet reste dessous, et son pic est nommé",
      vd["reste_dessous"] and not vd["franchit"] and vd["le_pic"] == {"la_coupe": 18, "le_cumul_en_voxels": 30.0})
    vn = le_verdict_de_laile(3, [_sb((0, 9), -20.0), _sb((9, 18), -16.5), _sb((18, 27), 30.0)], 36.0, 9)
    v("★★★ le demi-feuillet se compte en valeur absolue", vn["franchit"])
    vo = le_verdict_de_laile(3, [sbf[0], _sb((9, 18), 0.0, fermable=False), sbf[2]], 36.0, 9)
    v("★★★★ une sous-boucle ouverte empêche de juger le profil, et elle est nommée",
      vo["les_sous_boucles_ouvertes"] == [[9, 18]] and not vo["franchit"] and not vo["reste_dessous"])
    v0 = le_verdict_de_laile(1, [], 36.0, 9)
    v("★★★★ une aile sans coupe n'est pas jugée sur son profil", v0["sans_coupe"] and not v0["reste_dessous"])

    def _pa(vv):  # noqa: E306
        return {"le_verdict": vv}
    vg = le_verdict_des_ailes(["haut", "gauche"], {"haut": _pa(vd), "gauche": _pa(va)}, 9)
    v("★★★★ une aile qui franchit fait l'issue, l'autre reste dessous et seule elle compte",
      vg["les_ailes_qui_franchissent"] == ["gauche"] and vg["les_ailes_qui_restent_dessous"] == ["haut"]
      and not vg["chaque_aile_reste_dessous"] and "ELLE NE FERME QU'AU BOUT" in vg["ce_qui_reste_a_mesurer"])
    vt = le_verdict_des_ailes(["haut", "gauche"], {"haut": _pa(vd), "gauche": _pa(vd)}, 9)
    v("★★★★ deux ailes qui restent dessous : chaque aile reste dessous",
      vt["chaque_aile_reste_dessous"] and "CHAQUE AILE RESTE SOUS" in vt["ce_qui_reste_a_mesurer"])
    v("★★★★ une aile qui franchit prime sur une aile sans coupe, une aile ouverte sur les deux",
      "NE FERME QU'AU BOUT" in le_verdict_des_ailes(["haut", "gauche"], {"haut": _pa(v0), "gauche": _pa(va)},
                                                     9)["ce_qui_reste_a_mesurer"]
      and "OUVERTE" in le_verdict_des_ailes(["haut", "gauche"], {"haut": _pa(vo), "gauche": _pa(va)},
                                            9)["ce_qui_reste_a_mesurer"]
      and "NE SE DÉCOUPE PAS" in le_verdict_des_ailes(["haut", "gauche"], {"haut": _pa(v0), "gauche": _pa(vd)},
                                                      9)["ce_qui_reste_a_mesurer"])
    v("★★★ sans aile jugée, rien à juger ; les cinq issues sont distinctes",
      "RIEN À JUGER" in le_verdict_des_ailes([], {}, 9)["ce_qui_reste_a_mesurer"]
      and not le_verdict_des_ailes([], {}, 9)["chaque_aile_reste_dessous"]
      and len({_ce_qui_reste(*t) for t in itertools.product((True, False), repeat=4)}) == 5)

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    q235r, q239r = ce_que_235_a_publie(), ce_que_239_a_publie()
    v("★★★★ ce que 235 et 239 publient se relit : l'aile de droite, une portée de 40 rangées, un rectangle qui reste "
      "dessous",
      _ok(lambda: q235r["aile"]["le_cote"] == "droite" and la_portee(q235r["profil"], float(DEMI_PAS_EN_VOXELS)) == 40
          and q239r["le_rectangle"] == [26, 384, 22, 243] and q239r["reste_dessous"]))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[5:18, 30:90] = True  # une aile du haut, des colonnes 34 à 85
    Af[5:395, 3:18] = False
    Af[210:311, 3:18] = True  # une aile de gauche, des rangées 214 à 306
    Af[200:395, 250:281] = False  # l'aile de droite s'arrête à la rangée 195

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _plat(f, r, c):  # noqa: E306
        # la colonne extérieure de droite dérive : son aile est la plus lâche
        return _champ(f, r, c) + (-0.2 if f == "v" and c >= 272 else 0.0)

    def _ecart(f, r, c):  # noqa: E306
        # la colonne extérieure de gauche s'écarte puis revient : l'aile ferme au bout et franchit en chemin
        x = _plat(f, r, c)
        if f == "v" and c <= 11:
            x += 3.0 if 232 <= r < 255 else (-3.0 if 255 <= r < 278 else 0.0)
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

    def _p(cs, cum):  # noqa: E306
        return [{"la_coupe": c, "le_cumul_en_voxels": x} for c, x in zip(cs, cum)]
    q235p = {"decidable": True, "aile": {"le_cote": "droite"},
             "profil": _p([153, 163, 173, 183, 203, 213], [-27, -36.7, -40.2, -31.9, -37.7, -30.7])}
    q239p = {"decidable": True, "le_rectangle": [26, 384, 22, 243], "reste_dessous": True}

    def _scenario(champ):  # noqa: E306
        q2, q3 = _sur_lempreinte(Af, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda b: _fabrique(b, s0, champ), 49)
        q4 = _publie(m4, ce_que_234_a_publie)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        return m4, q2, q3, q4, s1
    m4f, q232f, q233f, q234f, src1 = _scenario(_plat)
    v("★★★★ 234 rejoué sur l'empreinte fabriquée : trois ailes qui ferment, celle de droite la plus lâche",
      _ok(lambda: m4f["le_verdict"]["les_ailes_qui_ferment"] == ["droite", "gauche", "haut"]
          and m4f["les_ailes"]["haut"]["les_coins"] == [9, 26, 34, 85]
          and m4f["les_ailes"]["gauche"]["les_coins"] == [214, 306, 7, 22]
          and laile_la_plus_lache(q234f)["le_cote"] == "droite"),
      str(m4f.get("raison") or ({c: x.get("les_coins") for c, x in (m4f.get("les_ailes") or {}).items()},
                                {c: (x.get("par_largeur") or {}).get("9", {}).get("la_fermeture_en_voxels")
                                 for c, x in (m4f.get("par_aile") or {}).items()})))
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b)
        return _fabrique(b, src1, _plat)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p, q239p, _lit, 49, 36.0)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_aile" in m, str(m.get("raison")))
    v("★★★★ les ailes du haut et de gauche sont jugées, et leurs coupes sont celles dérivées de l'empreinte",
      _ok(lambda: m["les_ailes_jugees"] == ["haut", "gauche"] and m["laile_de_235"] == "droite"
          and all({k_: x for k_, x in m["les_decoupages"][c].items() if k_ != "les_ecarts_au_dela_de_la_portee"}
                  == les_coupes(Af, m4f["les_ailes"][c]["les_coins"], c, 9) for c in ("haut", "gauche"))
          and m["les_decoupages"]["haut"]["le_sens"] == "colonnes"
          and m["les_decoupages"]["gauche"]["le_sens"] == "rangees"
          and m["les_decoupages"]["gauche"]["combien_de_sous_boucles"] >= 9), str(m.get("les_decoupages")))
    v("★★★★ seules les coupes intérieures des deux ailes se lisent, aucune de l'aile de droite",
      _ok(lambda: [b["cle"] for b in lus] == [b["cle"] for c in ("haut", "gauche")
                                               for b in les_bandes_des_coupes(m["les_decoupages"][c], 9)]
          and not ({b["cle"] for b in lus} & ({b["cle"] for b in q234f["bandes"]} | {b["cle"] for b in q233f["bandes"]}))
          and all(b["de"] in (9, 7) for b in lus)), str([b["cle"] for b in lus]))
    v("★★★★ chaque coupe est contrôlée par une bande publiée de 234 qu'elle croise",
      _ok(lambda: all(any(k.startswith(f"{b['cle']}×234 ") for k in m["la_reproduction"]["par_croisement"])
                      for b in m["les_bandes_declarees"])), str(m.get("la_reproduction", {}).get("par_croisement")))
    v("★★★★ les sous-boucles de l'aile de gauche somment à la fermeture que 234 publie pour elle, à toutes les "
      "largeurs ; celles du haut, qui ont des trous le long de leurs longs côtés, ne sont pas jugées",
      _ok(lambda: m["par_aile"]["gauche"]["lemboitement"]["combien_de_largeurs_jugees"] == 4
          and abs(m["par_aile"]["gauche"]["le_profil"][-1]["le_cumul_en_voxels"]
                  - q234f["par_aile"]["gauche"]["par_largeur"]["9"]["la_fermeture_en_voxels"]) <= 0.002
          and m["par_aile"]["haut"]["lemboitement"]["decidable"]
          and m["par_aile"]["haut"]["lemboitement"]["combien_de_largeurs_jugees"] == 0),
      str({c: m.get("par_aile", {}).get(c, {}).get("lemboitement") for c in ("haut", "gauche")}))
    v("★★★★ les sous-boucles vont d'un bout de chaque aile à l'autre, dans l'ordre des coupes",
      _ok(lambda: all([sb["entre"] for sb in m["par_aile"][c]["par_sous_boucle"]]
                      == [[a_, b_] for a_, b_ in zip(m["les_decoupages"][c]["les_coupes"][:-1],
                                                     m["les_decoupages"][c]["les_coupes"][1:])]
                      for c in ("haut", "gauche"))))
    v("★★★★ la règle de 225 est appliquée, les profils et le verdict sont ceux des sous-boucles",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and all(m["par_aile"][c]["le_profil"] == le_profil(m["par_aile"][c]["par_sous_boucle"], 9)
                  and m["par_aile"][c]["le_verdict"] == le_verdict_de_laile(
                      m["les_decoupages"][c]["combien_de_sous_boucles"], m["par_aile"][c]["par_sous_boucle"], 36.0, 9)
                  for c in ("haut", "gauche"))
          and m["le_verdict"] == le_verdict_des_ailes(["haut", "gauche"], m["par_aile"], 9)))
    v("★★★★ la portée de 235 borne les écarts : ceux au-delà sont nommés, aile par aile",
      _ok(lambda: m["la_portee"] == 40 and all(m["les_decoupages"][c]["les_ecarts_au_dela_de_la_portee"]
                                               == les_ecarts_au_dela(m["les_decoupages"][c]["les_coupes"], 40)
                                               for c in ("haut", "gauche"))))
    ms_ = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
               {**q235p, "profil": _p([100, 105], [-36.5, -36.2])}, q239p, lambda b: _fabrique(b, src1, _plat), 49,
               36.0)
    v("★★★★ une portée plus courte que tous les écarts les nomme tous, aile par aile",
      _ok(lambda: ms_["la_portee"] == 5 and all(
          ms_["les_decoupages"][c]["les_ecarts_au_dela_de_la_portee"]
          == [[a_, b_] for a_, b_ in zip(ms_["les_decoupages"][c]["les_coupes"][:-1],
                                         ms_["les_decoupages"][c]["les_coupes"][1:])] for c in ("haut", "gauche"))),
      str(ms_.get("raison")))
    mz = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
              {**q235p, "profil": _p([100], [1.0])}, q239p, lambda b: _fabrique(b, src1, _plat), 49, 36.0)
    v("★★★ sans traversée publiée par 235, aucun écart n'est nommé, et la mesure se fait quand même",
      _ok(lambda: mz["decidable"] and mz["la_portee"] is None
          and all(mz["les_decoupages"][c]["les_ecarts_au_dela_de_la_portee"] is None for c in ("haut", "gauche"))),
      str(mz.get("raison")))
    Am = la_grille_de_presence(q233f["presence"])
    v("★★★★ la couverture compte le rectangle de 239 et les seules ailes qui restent dessous",
      _ok(lambda: m["la_couverture"]["par_les_boucles_qui_restent_dessous_sur_leur_profil"]
          == la_couverture(Am, [[26, 384, 22, 243]] + [m4f["les_ailes"][c]["les_coins"]
                                                      for c in m["le_verdict"]["les_ailes_qui_restent_dessous"]], 9)
          and m["la_couverture"]["par_le_rectangle"] == la_couverture(Am, [[26, 384, 22, 243]], 9)))
    mr = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p,
              {**q239p, "reste_dessous": False}, lambda b: _fabrique(b, src1, _plat), 49, 36.0)
    v("★★★★ un rectangle que 239 ne dit pas dessous n'entre pas dans la couverture",
      _ok(lambda: mr["la_couverture"]["par_les_boucles_qui_restent_dessous_sur_leur_profil"]
          == la_couverture(Am, [m4f["les_ailes"][c]["les_coins"]
                                for c in mr["le_verdict"]["les_ailes_qui_restent_dessous"]], 9)))

    # la colonne extérieure de gauche s'écarte puis revient : le bout ne la voit pas, le profil oui
    m4e, q232e, q233e, q234e, src_e = _scenario(_ecart)
    me = _sur(mesurer, None, p219, p223, p224, p225, q225, q232e, q233e, q234e, q235p, q239p,
              lambda b: _fabrique(b, src_e, _ecart), 49, 36.0)
    ecarts = {q["la_coupe"]: round(float(q["le_cumul_en_voxels"]) - float(p_["le_cumul_en_voxels"]), 4)
              for q, p_ in zip(((me.get("par_aile") or {}).get("gauche") or {}).get("le_profil") or [],
                               ((m.get("par_aile") or {}).get("gauche") or {}).get("le_profil") or [])}
    v("★★★★ une colonne qui s'écarte puis revient : l'aile ferme au bout comme sans écart, et le profil en montre la "
      "trace",
      _ok(lambda: abs(ecarts[306]) <= 0.01 and max(abs(x) for x in ecarts.values()) >= 36.0
          and "gauche" in m4e["le_verdict"]["les_ailes_qui_ferment"]), str(ecarts))
    v("★★★★ et le verdict le dit : l'aile de gauche franchit, celle du haut reste dessous et seule compte",
      _ok(lambda: me["le_verdict"]["les_ailes_qui_franchissent"] == ["gauche"]
          and me["le_verdict"]["les_ailes_qui_restent_dessous"] == ["haut"]
          and me["la_couverture"]["par_les_boucles_qui_restent_dessous_sur_leur_profil"]
          == la_couverture(la_grille_de_presence(q233e["presence"]),
                           [[26, 384, 22, 243], m4e["les_ailes"]["haut"]["les_coins"]], 9)),
      str(me.get("raison") or me.get("le_verdict")))

    # les refus
    v("★★★★ une aile la plus lâche que 235 n'a pas découpée est refusée, et rien n'est lu",
      "n'a pas découpé" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
                                    {**q235p, "aile": {"le_cote": "gauche"}}, q239p, _lit, 49, 36.0).get("raison")))
    q234x = copy.deepcopy(q234f)
    if q234x.get("decidable"):
        q234x["par_aile"]["gauche"]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des sous-boucles qui ne somment pas à la fermeture publiée de l'aile sont refusées, par leur raison",
      "l'emboîtement ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234x,
                                                  q235p, q239p, lambda b: _fabrique(b, src1, _plat), 49, 36.0)
                                             .get("raison")))

    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p, q239p,
                                   _menteuse, 49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une coupe qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p, q239p,
                                       _decale, 49, 36.0).get("raison")))
    v("★★★★ une présence qui ne retombe pas sur les bandes de 234 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f,
                                   {**q234f, "publiees": ce_que_234_a_publie()["publiees"],
                                    "bandes": ce_que_234_a_publie()["bandes"]}, q235p, q239p, _lit, 49, 36.0)
                              .get("raison")))
    q234n = copy.deepcopy(q234f)
    if q234n.get("decidable"):
        q234n["verdict"]["les_ailes_qui_ferment"] = ["droite"]
    lus_n = []
    mn = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234n, q235p, q239p,
              lambda b: lus_n.append(b) or _fabrique(b, src1, _plat), 49, 36.0)
    v("★★★★ sans autre aile qui ferme dans 234, rien n'est jugé ni lu",
      _ok(lambda: mn["decidable"] and "RIEN À JUGER" in mn["le_verdict"]["ce_qui_reste_a_mesurer"] and not lus_n),
      str(mn.get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p, q239p, None, 49, 36.0)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q235p, q239p, None, 49, 36.0)
    v("★★★★ une coupe lue sur d'autres lignes que celles dérivées est refusée",
      "pas celle des coupes dérivées" in str(mf.get("raison")), str(mf.get("raison")))
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
        par233, par234, par235 = ce_que_233_a_publie(), ce_que_234_a_publie(), ce_que_235_a_publie()
        for nom, par in (("233", par233), ("234", par234), ("235", par235)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        lache = laile_la_plus_lache(par234)
        lache_c = lache["le_cote"] if lache else None
        if lache_c is not None and par235["aile"]["le_cote"] != lache_c:
            print("indécidable : `235` n'a pas découpé l'aile la plus lâche de `234`")
            return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        jugees = les_ailes_jugees(par234, lache_c)
        tenues = les_tenues(A, k1)
        bandes = []
        for c in jugees:
            dec = les_coupes(A, par234["ailes"][c]["les_coins"], c, k1, tenues)
            print(f"{c} : {dec}", flush=True)
            if dec["combien_de_sous_boucles"] >= 2:
                bandes += les_bandes_des_coupes(dec, k1)
        if not bandes:
            return 0
        print(f"coupes : {[(b['cle'], len(b['les_lignes']) * (b['a'] - b['de'] + 1)) for b in bandes]}", flush=True)
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
