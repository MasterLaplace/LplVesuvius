"""Sous la rangée où s'arrête l'aile qui évite la colonne qui dérive, une aile qui l'évite encore tient-elle sur son profil ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE, ET AVANT QUE L'AILE NE SOIT DÉRIVÉE. Ce
qui était vu avant d'écrire : ce que `233`, `234`, `235` et `241` publient, et leurs figures.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P87`. Des rangées 26 à 112, l'aile de droite qui évite la colonne 260
tient sur son profil (`241`) ; elle s'arrête là. Plus bas, de la coupe 163 à la coupe 203 de `235`, la colonne 260
franchit le demi-feuillet, et aucune aile qui l'évite n'a été jugée. Qu'est-ce qui relie au rectangle la matière
au-delà de la colonne 243 sous la rangée où l'aile de `241` s'arrête ?

## L'aile, dérivée

La règle de `234` du côté de l'aile de `241` — la plus grande aire, puis le plus long chemin, puis le plus petit début,
puis la bande extérieure la plus proche —, parmi les bandes extérieures qui ne partagent aucune ligne avec la ligne
que `241` évite, sur les rangées du rectangle de `233` qui vont de la dernière rangée de l'aile de `241` à la dernière
du rectangle. Aucune n'est choisie.

## Les coupes, dérivées

Celles de `241` : l'aile est partagée en le moins de parts égales qui ne dépassent pas la portée que `241` publie, et
les rangées de partage sont gardées là où leur bande de neuf lignes tient d'un long côté à l'autre. ⚠⚠ Les deux bouts
de l'aile sont des coupes : une aile qui ne dépasse pas la portée n'en demande pas d'autre, et son profil est sa
fermeture. ⚠⚠⚠ Un écart entre deux coupes gardées qui dépasse la portée laisse le profil non vu là.

## Ce qui se lit, et ce qui le contrôle

Les trois bandes neuves de l'aile — la bande extérieure et les deux bouts — et les coupes, par le lecteur de `224`. ⚠⚠
La bande intérieure n'est pas relue : ses pas sont ceux que `233` publie. ⚠⚠⚠ Partout où une bande neuve croise une bande
publiée — `219`, `223`, `224`, `232`, `233`, `234` — ou une bande neuve déjà contrôlée, les pas relus retombent à
l'arrondi, sinon refus ; une bande qui ne croise rien de contrôlé est refusée. ⚠⚠ Les chunks que la lecture compte
absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur l'aile entière et sur chaque tranche, à chaque largeur de l'échelle de `218`. ⚠⚠⚠ Les tranches
somment à la fermeture de l'aile, là où aucune n'a de trou le long des longs côtés, à l'arrondi près, sinon refus. LE
PROFIL : la fermeture cumulée, coupe après coupe. LA COUVERTURE : la part de l'empreinte qu'entourent les boucles qui
tiennent sur leur profil selon `241`, et l'aile si elle reste dessous.

## Les issues, exclusives, jugées à neuf lignes

- sous cette rangée, aucune aile ne tient sans partager de ligne avec la ligne évitée : rien n'est lu ;
- un trou plus long que ceux que `225` a franchis laisse l'aile ou une tranche ouverte ;
- le profil de l'aile atteint le demi-feuillet à une coupe, ou à son bout ;
- un écart entre deux coupes gardées dépasse la portée : le profil n'y est pas vu ;
- il reste dessous à chaque coupe.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une traversée plus courte que la portée, entre deux coupes ; ni ce qui relie les
chunks que l'aile n'entoure pas, entre la dernière rangée de `241` et la première de l'aile.

Usage :
    uv run python src/nappe/sous_laile_qui_evite_la_colonne.py --verifier
    uv run python src/nappe/sous_laile_qui_evite_la_colonne.py --lire <lecture.json>
    uv run python src/nappe/sous_laile_qui_evite_la_colonne.py --depuis <lecture.json> \\
        --json docs/mesures/sous_laile_qui_evite_la_colonne.json
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

from au_dela_de_la_colonne_qui_derive import les_coupes_a_la_portee  # noqa: E402
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition,  # noqa: E402
                                                          ce_que_223_a_rendu, lire_les_bandes,
                                                          relire_une_bande)
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import (analyser,  # noqa: E402
                                                                            ce_que_225_a_publie,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_segment_au_dela_du_rectangle_se_relie_t_il import (ce_que_233_a_publie,  # noqa: E402
                                                           la_couverture, la_reproduction_en_chaine, laile,
                                                           les_bandes_de_laile, les_pas_de_laile, les_tenues)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from les_ailes_tiennent_elles_sur_leur_profil import lentre  # noqa: E402
from letroite_reste_t_elle_sans_ecart import les_franchissements  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import le_domaine, les_pas_dune_bande  # noqa: E402
from ou_laile_de_droite_se_separe import (ce_que_234_a_publie, le_profil,  # noqa: E402
                                          lemboitement, les_bandes_des_coupes, les_sources_de_235,
                                          les_sous_boucles)
from ou_sarrete_le_segment import (ce_que_232_a_publie, la_grille_de_presence,  # noqa: E402
                                   la_presence_retombe)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_241_A_PUBLIE = MESURES / "au_dela_de_la_colonne_qui_derive.json"

LA_QUESTION_DECLAREE = ("sous la rangée où s'arrête l'aile qui évite la colonne qui dérive, une aile qui l'évite encore "
                        "tient-elle sur son profil ?")
LA_MESURE_DECLAREE = ("la plus grande aile du côté de `241` dont la bande extérieure ne partage aucune ligne avec la "
                      "ligne que `241` évite, sur les rangées du rectangle de `233` sous l'aile de `241`, coupée à la "
                      "portée de `241`, l'instrument de `228` sur l'aile et sur chaque tranche, et la fermeture "
                      "cumulée coupe après coupe")


def ce_que_241_a_publie(chemin: Path = CE_QUE_241_A_PUBLIE) -> dict:
    """Le côté, la ligne évitée, la portée, l'aile et les boucles qui tiennent sur leur profil, tels que `241` les
    publie."""
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent ou illisible : {e}"}
    co = (d.get("laile") or {}).get("les_coins")
    if (not d.get("decidable") or not co or d.get("la_portee") is None or not d.get("le_verdict")
            or not d.get("la_couverture")):
        return {"decidable": False,
                "raison": d.get("raison") or "`241` ne publie pas d'aile, de portée, de verdict ou de couverture"}
    co = [int(x) for x in co]
    tiennent = [[int(x) for x in b] for b in d["les_boucles_de_240"]] + ([co] if d["le_verdict"]["reste_dessous"] else [])
    return {"decidable": True, "le_cote": d["le_cote"], "la_ligne_evitee": int(d["la_ligne_evitee"]),
            "la_portee": int(d["la_portee"]), "laile": co, "tiennent": tiennent, "la_couverture": d["la_couverture"]}


# ─────────────────────────────── le verdict ───────────────────────────────

def le_verdict_des_tranches(dec: dict, par_sb: list[dict], demi: float, k1: int) -> dict:
    """Le verdict des tranches, à la largeur jugée.

    ⚠⚠ Les deux bouts de l'aile sont des coupes : une aile qui ne dépasse pas la portée n'en demande pas d'autre, et
    son profil est sa fermeture. Les écarts au-delà de la portée sont rapportés, et c'est le verdict qui les juge.
    """
    kk = str(k1)
    base = {"la_largeur_jugee": int(k1), "combien_de_sous_boucles": len(par_sb),
            "les_ecarts_au_dela_de_la_portee": [[int(a), int(b)] for a, b in dec["les_ecarts_au_dela_de_la_portee"]]}
    ouv = [sb["entre"] for sb in par_sb if not sb["par_largeur"][kk]["fermable"]]
    if ouv:
        return {**base, "les_sous_boucles_ouvertes": ouv, "franchit": False}
    prof = le_profil(par_sb, k1)
    fr = les_franchissements(prof, demi)
    return {**base, "les_sous_boucles_ouvertes": [], "franchit": bool(fr),
            "le_pic": max(prof, key=lambda p: abs(float(p["le_cumul_en_voxels"]))), "les_franchissements": fr}


def _ce_qui_reste(sans_aile: bool, ouverte: bool, franchit: bool, non_vu: bool, ligne, rangee) -> str:
    """Les cinq issues, EXCLUSIVES, dans cet ordre de priorité."""
    if sans_aile:
        return (f"SOUS LA RANGÉE {rangee}, AUCUNE AILE NE TIENT SANS PARTAGER DE LIGNE AVEC LA LIGNE {ligne} : RIEN "
                f"N'EST LU")
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE L'AILE OU UNE TRANCHE OUVERTE"
    if franchit:
        return f"À NEUF LIGNES, SOUS LA RANGÉE {rangee}, L'AILE QUI ÉVITE LA LIGNE {ligne} ATTEINT LE DEMI-FEUILLET"
    if non_vu:
        return "UN ÉCART ENTRE DEUX COUPES GARDÉES DÉPASSE LA PORTÉE : LE PROFIL N'Y EST PAS VU"
    return (f"À NEUF LIGNES, SOUS LA RANGÉE {rangee}, L'AILE QUI ÉVITE LA LIGNE {ligne} RESTE SOUS LE DEMI-FEUILLET À "
            f"CHAQUE COUPE")


def le_verdict(ligne, rangee, aile: dict | None, vt: dict | None, k1: int) -> dict:
    """Le verdict d'ensemble, depuis l'aile entière et le verdict de ses tranches."""
    base = {"la_largeur_jugee": int(k1), "la_ligne_evitee": ligne, "sous_la_rangee": rangee}
    if aile is None:
        return {**base, "reste_dessous": False, "franchit": False,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(True, False, False, False, ligne, rangee)}
    x = aile["par_largeur"][str(k1)]
    ouverte = (not x["fermable"]) or bool(vt["les_sous_boucles_ouvertes"])
    franchit = (not ouverte) and (bool(vt["franchit"]) or not x["sous_le_demi_pli"])
    non_vu = (not ouverte) and (not franchit) and bool(vt["les_ecarts_au_dela_de_la_portee"])
    dessous = not (ouverte or franchit or non_vu)
    return {**base, "la_fermeture_de_laile": x.get("la_fermeture_en_voxels"), "ouverte": ouverte,
            "franchit": franchit, "non_vu": non_vu, "reste_dessous": dessous,
            "ce_qui_reste_a_mesurer": _ce_qui_reste(False, ouverte, franchit, non_vu, ligne, rangee)}


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par234: dict | None = None,
            par241: dict | None = None, lire=None, tirages: int | None = None, demi: float | None = None) -> dict:
    """L'aile qui évite encore la ligne sous l'aile de `241`, ses coupes, leur lecture puis l'analyse — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    par241 = ce_que_241_a_publie() if par241 is None else par241
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("234", par234), ("241", par241)):
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
    k1 = les_largeurs()[-1]
    coins233 = [int(x) for x in par233["coins"]]
    cote, ligne, portee = par241["le_cote"], int(par241["la_ligne_evitee"]), int(par241["la_portee"])
    rangee = int(par241["laile"][1])
    dessous_233 = [rangee, coins233[1], coins233[2], coins233[3]]
    tenues = les_tenues(A, k1)
    daile = laile(A, dessous_233, cote, k1, tenues, exclues=[ligne])
    base.update({"le_cote": cote, "la_ligne_evitee": ligne, "la_portee": portee, "sous_la_rangee": rangee,
                 "laile_de_241": par241["laile"], "les_rangees_cherchees": dessous_233, "laile": daile,
                 "les_boucles_de_241": par241["tiennent"], "la_couverture_de_241": par241["la_couverture"]})
    if not daile["les_coins"]:
        return {**base, "decidable": True, "le_verdict": le_verdict(ligne, rangee, None, None, k1)}
    coins = [int(x) for x in daile["les_coins"]]
    dec = les_coupes_a_la_portee(A, coins, cote, portee, k1, tenues)
    b_aile = les_bandes_de_laile(daile, coins233, k1)
    b_coupes = les_bandes_des_coupes(dec, k1)
    bandes = b_aile + b_coupes
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    base["le_decoupage"] = dec
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
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des bandes dérivées"}
    cn = la_presence_retombe(A, bandes, pub)
    base["la_presence_contre_la_lecture"] = cn
    if not cn.get("decidable"):
        return {**base, "decidable": False, "raison": cn.get("raison")}
    relues = {k: relire_une_bande(x) for k, x in pub.items()}
    nouvelles = {b["cle"]: {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                            "pas": les_pas_dune_bande(relues[b["cle"]])} for b in bandes}
    rep = la_reproduction_en_chaine(nouvelles, les_sources_de_235(par219, par223, par224, par232, par233, par234))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = les_pas_de_laile({**daile, "le_cote": cote}, coins233, b_aile, relues, par233)
    pas.update(les_pas_des_bandes(relues, b_coupes))
    entiere = analyser(pas, coins, par225["la_regle"], plus_long, g, t_)
    if not entiere.get("decidable"):
        return {**base, "decidable": False, "raison": f"l'aile : {entiere.get('raison')}", "la_reproduction": rep}
    par_sb = []
    for sb in les_sous_boucles(cote, coins, dec["les_coupes"]):
        a = analyser(pas, sb, par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"la tranche {sb} : {a.get('raison')}", "la_reproduction": rep}
        par_sb.append({"entre": lentre(cote, sb), "les_coins": sb, **a})
    emb = lemboitement(par_sb, entiere, cote)
    if not emb.get("decidable"):
        return {**base, "decidable": False, "raison": emb.get("raison"), "la_reproduction": rep, "lemboitement": emb}
    vt = le_verdict_des_tranches(dec, par_sb, demi, k1)
    v = le_verdict(ligne, rangee, entiere, vt, k1)
    tiennent = par241["tiennent"] + ([coins] if v["reste_dessous"] else [])
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "laile_entiere": entiere, "par_tranche": par_sb, "lemboitement": emb,
            "le_profil": le_profil(par_sb, k1), "le_verdict_des_tranches": vt, "le_verdict": v,
            "la_couverture": la_couverture(A, tiennent, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"côté : {r['le_cote']} · ligne évitée : {r['la_ligne_evitee']} · portée : {r['la_portee']} · sous la "
          f"rangée {r['sous_la_rangee']}")
    print(f"aile : {r['laile']}")
    if "le_decoupage" in r:
        print(f"découpage : {r['le_decoupage']}")
    if "par_tranche" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        for k, x in r["laile_entiere"]["par_largeur"].items():
            print(f"  aile · {k} lignes · fermable {x['fermable']} · L {x.get('la_fermeture_en_voxels')} · nul "
                  f"{x.get('le_nul')} · trous {x['les_trous']}")
        print(f"emboîtement : {r['lemboitement']}")
        k1 = str(r["le_verdict"]["la_largeur_jugee"])
        for sb in r["par_tranche"]:
            x = sb["par_largeur"][k1]
            if not x["fermable"]:
                print(f"  {sb['entre']} · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
                continue
            print(f"  {sb['entre']} · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']} · "
                  f"nul {x['le_nul']}")
        print(f"profil : {r['le_profil']}")
        print(f"tranches : {r['le_verdict_des_tranches']}")
        print(f"couverture : {r['la_couverture']} · 241 : {r['la_couverture_de_241']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

    from au_dela_de_la_colonne_qui_derive import mesurer as mesurer_241
    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_sources_de_234
    from le_segment_au_dela_du_rectangle_se_relie_t_il import mesurer as mesurer_234
    from ou_sarrete_le_segment import ABSENT, les_absents_dune_ligne, les_sources
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

    # le verdict des tranches, et le verdict, sur des tranches fabriquées
    def _sb(a_, b_, L, fermable=True):  # noqa: E306
        return {"entre": [a_, b_], "par_largeur": {"9": {"fermable": fermable, "la_fermeture_en_voxels": L}}}

    def _dec(ecarts=()):  # noqa: E306
        return {"les_ecarts_au_dela_de_la_portee": [list(e) for e in ecarts]}
    t1 = le_verdict_des_tranches(_dec(), [_sb(150, 180, 7.0)], 36.0, 9)
    v("★★★★ une aile d'une seule tranche, qui ne dépasse pas la portée, a pour profil sa fermeture",
      _ok(lambda: t1["combien_de_sous_boucles"] == 1 and not t1["franchit"] and t1["les_sous_boucles_ouvertes"] == []
          and t1["le_pic"] == {"la_coupe": 180, "le_cumul_en_voxels": 7.0}), str(t1))
    t2 = le_verdict_des_tranches(_dec(), [_sb(150, 172, 30.0), _sb(172, 195, -28.0)], 36.0, 9)
    t3 = le_verdict_des_tranches(_dec(), [_sb(150, 172, 37.0), _sb(172, 195, -35.0)], 36.0, 9)
    v("★★★★ le profil se cumule coupe après coupe, et l'atteinte du demi-feuillet à une coupe franchit",
      _ok(lambda: not t2["franchit"] and t2["le_pic"]["la_coupe"] == 172 and t3["franchit"]
          and t3["les_franchissements"] == [{"la_coupe": 172, "le_cumul_en_voxels": 37.0}]), str(t3))
    t4 = le_verdict_des_tranches(_dec(), [_sb(150, 172, 1.0), _sb(172, 195, 0.0, fermable=False)], 36.0, 9)
    t5 = le_verdict_des_tranches(_dec([[150, 195]]), [_sb(150, 195, 3.0)], 36.0, 9)
    v("★★★ une tranche ouverte est nommée ; un écart au-delà de la portée est rapporté",
      _ok(lambda: t4["les_sous_boucles_ouvertes"] == [[172, 195]] and not t4["franchit"]
          and t5["les_ecarts_au_dela_de_la_portee"] == [[150, 195]]), str(t4))

    def _ae(L, fermable=True):  # noqa: E306
        return {"par_largeur": {"9": {"fermable": fermable, "la_fermeture_en_voxels": L,
                                      "sous_le_demi_pli": abs(L) < 36}}}
    vd = le_verdict(260, 112, _ae(7.0), t1, 9)
    v("★★★★ une aile d'une seule tranche qui ferme sous le demi-feuillet reste dessous : ses bouts sont ses coupes",
      vd["reste_dessous"] and "RESTE SOUS" in vd["ce_qui_reste_a_mesurer"] and "RANGÉE 112" in vd["ce_qui_reste_a_mesurer"]
      and "LIGNE 260" in vd["ce_qui_reste_a_mesurer"], str(vd))
    vn = le_verdict(260, 112, _ae(3.0), t5, 9)
    v("★★★★ un écart au-delà de la portée laisse le profil non vu : l'aile n'est pas dite dessous",
      vn["non_vu"] and not vn["reste_dessous"] and "N'Y EST PAS VU" in vn["ce_qui_reste_a_mesurer"], str(vn))
    vf = le_verdict(260, 112, _ae(2.0), t3, 9)
    v("★★★★ un profil qui atteint le demi-feuillet en chemin franchit, même si l'aile ferme au bout",
      vf["franchit"] and not vf["reste_dessous"] and "ATTEINT" in vf["ce_qui_reste_a_mesurer"])
    vb = le_verdict(260, 112, _ae(-40.0), {**t5, "franchit": False}, 9)
    v("★★★★ une aile qui dépasse le demi-feuillet au bout franchit, même quand un écart dépasse la portée",
      vb["franchit"] and not vb["non_vu"] and not vb["reste_dessous"])
    vo = le_verdict(260, 112, _ae(0.0, fermable=False), t3, 9)
    v("★★★★ une aile ouverte, ou une tranche ouverte, prime sur tout le reste",
      vo["ouverte"] and not vo["franchit"] and le_verdict(260, 112, _ae(5.0), {**t4, "franchit": True}, 9)["ouverte"])
    v("★★★ atteindre le demi-feuillet prime sur un écart non vu, un trou sur les deux",
      "ATTEINT" in _ce_qui_reste(False, False, True, True, 260, 112)
      and "OUVERTE" in _ce_qui_reste(False, True, True, True, 260, 112))
    v0 = le_verdict(260, 112, None, None, 9)
    v("★★★ sans aile, rien n'est dit dessous ; les cinq issues sont distinctes",
      not v0["reste_dessous"] and "RIEN N'EST LU" in v0["ce_qui_reste_a_mesurer"]
      and "RANGÉE 112" in v0["ce_qui_reste_a_mesurer"]
      and len({_ce_qui_reste(*t, 260, 112) for t in itertools.product((True, False), repeat=4)}) == 5)

    # ce que 241 publie
    q241r = ce_que_241_a_publie()
    v("★★★★ ce que 241 publie se relit : l'aile de droite qui évite la colonne 260 s'arrête à la rangée 112, portée "
      "40, quatre boucles qui tiennent",
      _ok(lambda: q241r["le_cote"] == "droite" and q241r["la_ligne_evitee"] == 260 and q241r["laile"][1] == 112
          and q241r["la_portee"] == 40 and len(q241r["tiennent"]) == 4 and q241r["tiennent"][-1] == q241r["laile"]
          and q241r["la_couverture"]["la_part"] == 0.9047), str(q241r.get("raison")))
    brut = json.loads(CE_QUE_241_A_PUBLIE.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        pj = Path(tmp) / "241.json"
        pj.write_text(json.dumps({**brut, "le_verdict": {**brut["le_verdict"], "reste_dessous": False}}))
        sans_dessous = ce_que_241_a_publie(pj)
        pj.write_text(json.dumps({**brut, "laile": {**brut["laile"], "les_coins": None}}))
        sans_aile = ce_que_241_a_publie(pj)
    v("★★★★ l'aile de 241 n'est comptée parmi les boucles qui tiennent que si elle reste dessous ; sans aile, 241 est "
      "refusé",
      _ok(lambda: sans_dessous["tiennent"] == q241r["tiennent"][:-1] and not sans_aile["decidable"]))

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[200:395, 250:281] = False  # l'aile de droite s'arrête à la rangée 195
    Af[100:111, 265:267] = False  # entre les colonnes 260 et 276, rien ne tient des rangées 26 à 195
    Af[140:146, 252] = False      # des rangées 140 à 145, aucune colonne au-delà de la 243 ne tient : l'aile de 241
    Af[140:146, 258] = False      # s'arrête avant
    Af[140:200, 265:281] = False  # et sous la rangée 140, l'empreinte s'arrête à la colonne 264

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _plat(f, r, c):  # noqa: E306
        # la colonne extérieure de droite dérive, et c'est elle que 236 désigne
        return _champ(f, r, c) + (-0.2 if f == "v" and c >= 272 else 0.0)

    def _ecart(f, r, c):  # noqa: E306
        # sous l'aile de 241, la matière entre la colonne 243 et la colonne évitée s'écarte puis revient
        x = _plat(f, r, c)
        if f == "v" and 256 <= c <= 264:
            x += 3.0 if 155 <= r < 172 else (-3.0 if 172 <= r < 189 else 0.0)
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

    def _fabrique(bd_, src, champ, A_=None):  # noqa: E306
        A_ = Af if A_ is None else A_
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
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(A_, bd_["le_sens"], l_, bd_["de"], bd_["a"])}}
                    for l_ in bd_["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}

    def _publie(m_, lecteur):  # noqa: E306
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m.json"
            pj.write_text(json.dumps(m_, ensure_ascii=False))
            return lecteur(pj)

    def _p(cs, cum):  # noqa: E306
        return [{"la_coupe": c, "le_cumul_en_voxels": x} for c, x in zip(cs, cum)]
    q235p = {"decidable": True, "aile": {"le_cote": "droite"}, "bandes": [], "publiees": {}, "relues": {},
             "profil": _p([153, 163, 173, 183, 203, 213], [-27, -36.7, -40.2, -31.9, -37.7, -30.7])}
    q236p = {"decidable": True, "la_ligne_qui_derive": 276, "cest_une_colonne_de_laile": True}
    q240p = {"decidable": True, "tiennent": [[26, 384, 22, 243]],
             "la_couverture": {"combien": 0, "sur": 0, "la_part": 0.0}}

    def _scenario(champ, A_=None):  # noqa: E306
        A_ = Af if A_ is None else A_
        q2, q3 = _sur_lempreinte(A_, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda b: _fabrique(b, s0, champ, A_),
                  49)
        q4 = _publie(m4, ce_que_234_a_publie)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        m41 = _sur(mesurer_241, None, p219, p223, p224, p225, q225, q2, q3, q4, q235p, q236p, q240p,
                   lambda b: _fabrique(b, s1, champ, A_), 49, 36.0)
        q41 = _publie(m41, ce_que_241_a_publie)
        return m4, m41, q2, q3, q4, q41, s1
    m4f, m41f, q232f, q233f, q234f, q241f, src1 = _scenario(_plat)
    Am = la_grille_de_presence(q233f["presence"])
    v("★★★★ 234 puis 241 rejoués sur l'empreinte fabriquée : l'aile qui évite la colonne 276 s'arrête avant le bout "
      "de l'empreinte",
      _ok(lambda: m4f["les_ailes"]["droite"]["les_coins"][3] == 276
          and q241f["laile"] == laile(Am, [26, 384, 22, 243], "droite", 9, exclues=[276])["les_coins"]
          and q241f["laile"][1] < 186 and q241f["la_ligne_evitee"] == 276 and q241f["la_portee"] == 40),
      str(m41f.get("raison") or q241f.get("laile")))
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b)
        return _fabrique(b, src1, _plat)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f, _lit, 49, 36.0)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_tranche" in m, str(m.get("raison")))
    bas = q241f["laile"][1] if q241f.get("decidable") else None
    v("★★★★ l'aile est la plus grande de droite sous l'aile de 241 dont la colonne extérieure ne partage aucune ligne "
      "avec la 276",
      _ok(lambda: m["laile"] == laile(Am, [bas, 384, 22, 243], "droite", 9, exclues=[276])
          and m["laile"]["les_coins"][0] >= bas and abs(m["laile"]["les_coins"][3] - 276) >= 9
          and m["le_decoupage"] == les_coupes_a_la_portee(Am, m["laile"]["les_coins"], "droite", 40, 9)
          and m["le_decoupage"]["combien_de_sous_boucles"] >= 2), str(m.get("laile")))
    v("★★★★ se lisent les trois bandes neuves de l'aile et ses coupes, et rien d'autre",
      _ok(lambda: [b["cle"] for b in lus] == [b["cle"] for b in les_bandes_de_laile(m["laile"], [26, 384, 22, 243], 9)
                                               + les_bandes_des_coupes(m["le_decoupage"], 9)]
          and not any(b["le_sens"] == "colonnes" and b["le_centre"] == 243 for b in lus)), str([b["cle"] for b in lus]))
    v("★★★★ chaque bande neuve est contrôlée, par une bande publiée ou par une bande neuve déjà contrôlée",
      _ok(lambda: sorted(m["la_reproduction"]["lordre_du_controle"]) == sorted(b["cle"] for b in lus)
          and any("×233 colonnes_243" in k_ for k_ in m["la_reproduction"]["par_croisement"])))
    v("★★★★ les tranches somment à la fermeture de l'aile entière, à neuf lignes",
      _ok(lambda: m["lemboitement"]["par_largeur"]["9"]["jugeable"]
          and abs(m["le_profil"][-1]["le_cumul_en_voxels"]
                  - m["laile_entiere"]["par_largeur"]["9"]["la_fermeture_en_voxels"]) <= 0.002),
      str(m.get("lemboitement")))
    v("★★★★ la règle de 225 est appliquée, le profil et les verdicts sont ceux des tranches",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and [sb["entre"] for sb in m["par_tranche"]] == [[a_, b_] for a_, b_ in zip(
              m["le_decoupage"]["les_coupes"][:-1], m["le_decoupage"]["les_coupes"][1:])]
          and m["le_profil"] == le_profil(m["par_tranche"], 9)
          and m["le_verdict_des_tranches"] == le_verdict_des_tranches(m["le_decoupage"], m["par_tranche"], 36.0, 9)
          and m["le_verdict"] == le_verdict(276, bas, m["laile_entiere"], m["le_verdict_des_tranches"], 9)))
    v("★★★★ sur un champ où seule la colonne 276 dérive, l'aile reste dessous, et la couverture la compte avec les "
      "boucles de 241",
      _ok(lambda: m["le_verdict"]["reste_dessous"]
          and m["la_couverture"] == la_couverture(Am, q241f["tiennent"] + [m["laile"]["les_coins"]], 9)),
      str(m.get("le_verdict")))

    # sous l'aile de 241, la matière s'écarte puis revient : le bout ne la voit pas, le profil oui
    _, _, q232e, q233e, q234e, q241e, src_e = _scenario(_ecart)
    me = _sur(mesurer, None, p219, p223, p224, p225, q225, q232e, q233e, q234e, q241e,
              lambda b: _fabrique(b, src_e, _ecart), 49, 36.0)
    ecarts = {q["la_coupe"]: round(float(q["le_cumul_en_voxels"]) - float(p_["le_cumul_en_voxels"]), 4)
              for q, p_ in zip(me.get("le_profil") or [], m.get("le_profil") or [])}
    v("★★★★ une matière qui s'écarte puis revient : l'aile ferme au bout à moins d'un voxel de ce qu'elle ferme sans "
      "écart, et le profil en montre la trace",
      _ok(lambda: q241e["laile"] == q241f["laile"] and abs(ecarts[max(ecarts)]) <= 1.0
          and max(abs(x) for x in ecarts.values()) >= 36.0), str(ecarts))
    v("★★★★ et le verdict le dit : l'aile franchit, et la couverture ne la compte pas",
      _ok(lambda: me["le_verdict"]["franchit"] and not me["le_verdict"]["reste_dessous"]
          and me["la_couverture"] == la_couverture(la_grille_de_presence(q233e["presence"]), q241e["tiennent"], 9)),
      str(me.get("raison") or me.get("le_verdict")))

    # les refus
    g_ = globals()
    vrai = g_["analyser"]

    def _faux(pas_, co, *a, **k):  # noqa: E306
        r_ = vrai(pas_, co, *a, **k)
        if [int(x) for x in co] == [int(x) for x in m["laile"]["les_coins"]] and r_.get("decidable"):
            r_["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
        return r_
    g_["analyser"] = _faux
    try:
        mfx = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f,
                   lambda b: _fabrique(b, src1, _plat), 49, 36.0)
    finally:
        g_["analyser"] = vrai
    v("★★★★ des tranches qui ne somment pas à la fermeture de l'aile entière sont refusées, par leur raison",
      "l'emboîtement ne retombe pas" in str(mfx.get("raison")), str(mfx.get("raison")))
    lus_r = []
    v("★★★★ sans aile publiée par 241, la mesure est refusée, et rien n'est lu",
      "`241`" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
                          {"decidable": False, "raison": "pas d'aile"},
                          lambda b: lus_r.append(b) or _fabrique(b, src1, _plat), 49, 36.0).get("raison"))
      and not lus_r)
    lus_x = []
    mx = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
              {**q241f, "laile": [26, 190, 243, 260]},
              lambda b: lus_x.append(b) or _fabrique(b, src1, _plat), 49, 36.0)
    v("★★★★ sous une rangée d'où aucune aile ne tient, rien n'est lu",
      _ok(lambda: mx["decidable"] and mx["laile"]["les_coins"] is None and "RIEN N'EST LU" in
          mx["le_verdict"]["ce_qui_reste_a_mesurer"] and "190" in mx["le_verdict"]["ce_qui_reste_a_mesurer"]
          and not lus_x), str(mx.get("raison")))
    # la ligne évitée décide : la 256 écarte toutes les colonnes que l'empreinte porte sous l'aile de 241, la 251
    # laisse la colonne 260, à neuf lignes pile
    lus_256 = []
    m256 = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, {**q241f, "la_ligne_evitee": 256},
                lambda b: lus_256.append(b) or _fabrique(b, src1, _plat), 49, 36.0)
    m251 = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, {**q241f, "la_ligne_evitee": 251},
                lambda b: _fabrique(b, src1, _plat), 49, 36.0)
    v("★★★★ une ligne évitée qui écarte toutes les colonnes laisse l'aile sans colonne extérieure, et rien n'est lu ; "
      "une ligne à neuf colonnes de la 260 la laisse",
      _ok(lambda: m256["laile"]["les_coins"] is None and "LIGNE 256" in m256["le_verdict"]["ce_qui_reste_a_mesurer"]
          and not lus_256 and m251["laile"]["les_coins"] == m["laile"]["les_coins"]
          and m251["laile"]["les_coins"][3] == 260 and "par_tranche" in m251),
      str(m256.get("raison") or m256.get("laile")) + " " + str(m251.get("raison") or m251.get("laile")))

    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f,
                                   _menteuse, 49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src1, _plat)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        for a_, s_ in x["le_long"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une bande qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f,
                                       _decale, 49, 36.0).get("raison")))
    v("★★★★ une présence qui ne retombe pas sur les bandes de 234 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f,
                                   {**q234f, "publiees": ce_que_234_a_publie()["publiees"],
                                    "bandes": ce_que_234_a_publie()["bandes"]}, q241f, _lit, 49, 36.0)
                              .get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f, None, 49, 36.0)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, q241f, None, 49, 36.0)
    v("★★★★ une bande lue sur d'autres lignes que celles dérivées est refusée",
      "pas celle des bandes dérivées" in str(mf.get("raison")), str(mf.get("raison")))
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
        par233, par241 = ce_que_233_a_publie(), ce_que_241_a_publie()
        for nom, par in (("233", par233), ("241", par241)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        tenues = les_tenues(A, k1)
        c233 = [int(x) for x in par233["coins"]]
        daile = laile(A, [par241["laile"][1], c233[1], c233[2], c233[3]], par241["le_cote"], k1, tenues,
                      exclues=[par241["la_ligne_evitee"]])
        print(f"aile : {daile}", flush=True)
        if not daile["les_coins"]:
            return 0
        dec = les_coupes_a_la_portee(A, daile["les_coins"], par241["le_cote"], par241["la_portee"], k1, tenues)
        print(f"découpage : {dec}", flush=True)
        bandes = les_bandes_de_laile(daile, c233, k1) + les_bandes_des_coupes(dec, k1)
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
