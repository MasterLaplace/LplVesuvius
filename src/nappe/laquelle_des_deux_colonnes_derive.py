"""Laquelle des deux colonnes de l'aile de droite dérive ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE, ET AVANT QUE LA TROISIÈME COLONNE NE
SOIT DÉRIVÉE. Ce qui était vu avant d'écrire : ce que `235` publie, et sa figure. La présence autour de l'aile n'a
pas été regardée.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P81`. `235` a découpé l'aile de droite de `234`, des rangées 26 à 223 et
des colonnes 243 à 260, en 21 sous-boucles : aucune n'arrive au demi-feuillet, l'écart de −35,6938 voxels se cumule
par petits pas, et la fermeture cumulée franchit le demi-feuillet en chemin, à −40,2188 à la coupe 173. Deux colonnes
qui s'écartent : laquelle dérive ? Entre les colonnes 243 et 260, aucune troisième colonne de neuf lignes ne tient
sans partager de ligne ; la référence est hors de l'aile.

## La troisième ligne, dérivée

L'aile est la plus lâche de celles qui ferment dans `234`, celle que `235` a découpée. Une TROISIÈME LIGNE est une
bande de neuf lignes parallèle à ses deux longs côtés, à neuf lignes au moins de chacun, qui tient au sens de `233`
sur toute la longueur de l'aile ; et les deux bandes de bout qui la relient au long côté le plus proche tiennent
aussi. Des deux côtés de l'aile, la plus proche d'un long côté ; à égalité, celle du côté du rectangle. Le code la
dérive de la présence que `233` publie, et de rien d'autre.

## Ce qui se lit, et ce qui le contrôle

La troisième ligne, et les deux bandes de bout qui la relient au long côté le plus proche, neuf lignes chacune, par
le lecteur de `224`. ⚠⚠ Les deux longs côtés et les bouts de l'aile ne sont pas relus : leurs pas sont ceux que `233`
et `234` publient. ⚠⚠⚠ Partout où une bande neuve croise une bande publiée — `219`, `223`, `224`, `232`, `233`,
`234` —, les pas relus retombent à l'arrondi, sinon refus ; une bande neuve qui ne croise aucune bande publiée est
refusée. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

Trois lignes parallèles, trois boucles entre elles deux à deux, sur les mêmes bouts : la boucle de l'aile, la boucle
étroite entre la troisième ligne et le long côté le plus proche, et la boucle large entre la troisième ligne et le
long côté le plus loin. L'instrument de `228` sur chacune, à chaque largeur, avec la garde de `232`.

⚠⚠⚠ DEUX CONTRÔLES SANS LECTURE DE PLUS. La boucle de l'aile retombe sur ce que `234` publie, à chaque largeur, sinon
refus. Et la boucle large est la somme des deux autres : leur ligne commune est parcourue une fois dans chaque sens.
À chaque largeur où aucun trou de majorité ne touche, sur un bout, la jonction avec la ligne commune, la somme retombe
à l'arrondi, sinon refus. ⚠ Un trou ailleurs se franchit de la même façon dans les boucles qui le partagent.

LA LIGNE QUI DÉRIVE est celle qu'exclut la boucle qui ferme le plus serré : si deux lignes s'accordent, leur boucle
ferme, et les deux boucles qui passent par la troisième portent son écart. ⚠⚠ Elle n'est DÉSIGNÉE que si la boucle
la plus serrée l'est plus que chacune des deux autres d'au moins la fermeture médiane du bruit seul de cette autre :
en deçà, le bruit seul suffit à inverser l'ordre.

## Les issues, exclusives, jugées à neuf lignes

- aucune troisième ligne ne tient : rien ne départage les deux colonnes, et rien n'est lu ;
- une boucle garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- la boucle la plus serrée ne l'est pas assez : les trois boucles ne départagent pas ;
- elle l'est : la ligne qu'elle exclut dérive, que ce soit l'une des deux colonnes de l'aile ou la troisième ligne.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, le long de l'aile, la ligne désignée dérive — les boucles ne sont pas
découpées ; ni si la troisième ligne est elle-même juste : elle départage, elle n'est pas une vérité de terrain.

Usage :
    uv run python src/nappe/laquelle_des_deux_colonnes_derive.py --verifier
    uv run python src/nappe/laquelle_des_deux_colonnes_derive.py --lire <lecture.json>
    uv run python src/nappe/laquelle_des_deux_colonnes_derive.py --depuis <lecture.json> \\
        --json docs/mesures/laquelle_des_deux_colonnes_derive.json
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
from le_segment_au_dela_du_rectangle_se_relie_t_il import (ce_que_233_a_publie,  # noqa: E402
                                                           les_bandes_de_laile, les_pas_de_laile, les_tenues,
                                                           tient)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import (L_ARRONDI, ce_que_234_a_publie,  # noqa: E402
                                          laile_la_plus_lache, les_sources_de_235)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

LA_QUESTION_DECLAREE = "laquelle des deux colonnes de l'aile la plus lâche dérive ?"
LA_MESURE_DECLAREE = ("une troisième ligne parallèle, dérivée de la présence hors de l'aile, les trois boucles que "
                      "les trois lignes ferment deux à deux, et l'instrument de `228` sur chacune")


# ─────────────────────────────── la troisième ligne, dérivée ───────────────────────────────

def les_lignes_de_laile(cote: str, coins) -> tuple[str, int, int, int, int]:
    """`(sens, interieure, exterieure, lo, hi)` : le sens des deux longs côtés de l'aile, celui qu'elle partage avec
    le rectangle, l'autre, et l'étendue qu'ils couvrent."""
    a0, a1, b0, b1 = [int(x) for x in coins]
    return {"droite": ("colonnes", b0, b1, a0, a1), "gauche": ("colonnes", b1, b0, a0, a1),
            "haut": ("rangees", a1, a0, b0, b1), "bas": ("rangees", a0, a1, b0, b1)}[cote]


def les_coins_entre(sens: str, p: int, q: int, lo: int, hi: int) -> list[int]:
    """Les coins de la boucle entre deux lignes parallèles `p < q`, de `lo` à `hi`."""
    return [int(lo), int(hi), int(p), int(q)] if sens == "colonnes" else [int(p), int(q), int(lo), int(hi)]


def la_troisieme_ligne(A: np.ndarray, coins, cote: str, k: int, tenues=None) -> dict | None:
    """La plus proche d'un long côté, des deux côtés de l'aile ; à égalité, celle du côté du rectangle. Elle tient sur
    toute la longueur de l'aile, et les deux bandes de bout qui la relient au long côté le plus proche aussi."""
    A = np.asarray(A, dtype=bool)
    k, h = int(k), int(k) // 2
    PR, PC = tenues if tenues is not None else les_tenues(A, k)
    sens, dedans, dehors, lo, hi = les_lignes_de_laile(cote, coins)
    travers = "rangees" if sens == "colonnes" else "colonnes"
    borne = A.shape[1] if sens == "colonnes" else A.shape[0]
    bas_, haut_ = min(dedans, dehors), max(dedans, dehors)
    meilleure, cle_m = None, None
    for c in list(range(h, bas_ - k + 1)) + list(range(haut_ + k, borne - h)):
        proche = bas_ if c < bas_ else haut_
        a_, b_ = min(c, proche), max(c, proche)
        if not (tient(PR, PC, sens, c, lo, hi) and tient(PR, PC, travers, lo, a_, b_)
                and tient(PR, PC, travers, hi, a_, b_)):
            continue
        cle = (abs(c - proche), 0 if proche == dedans else 1)
        if cle_m is None or cle < cle_m:
            meilleure, cle_m = {"la_ligne": int(c), "le_sens": sens, "la_plus_proche": int(proche),
                                "la_plus_loin": int(dehors if proche == dedans else dedans),
                                "du_cote_du_rectangle": proche == dedans, "lecart": int(abs(c - proche))}, cle
    return meilleure


def les_bandes_de_la_troisieme(tl: dict, lo: int, hi: int, k: int) -> list[dict]:
    """La troisième ligne sur toute la longueur de l'aile, et les deux bandes de bout vers le long côté le plus
    proche."""
    sens, c, p = tl["le_sens"], int(tl["la_ligne"]), int(tl["la_plus_proche"])
    travers = "rangees" if sens == "colonnes" else "colonnes"
    a_, b_ = min(c, p), max(c, p)
    out = [{"cle": f"{sens}_{c}_{lo}_{hi}", "le_sens": sens, "le_centre": c, "les_lignes": les_rangees_a_lire(c, k),
            "de": int(lo), "a": int(hi)}]
    for r in (lo, hi):
        out.append({"cle": f"{travers}_{r}_{a_}_{b_}", "le_sens": travers, "le_centre": int(r),
                    "les_lignes": les_rangees_a_lire(int(r), k), "de": a_, "a": b_})
    return out


def les_trois_boucles(tl: dict, lo: int, hi: int) -> dict:
    """La boucle de l'aile, l'étroite entre la troisième ligne et le côté le plus proche, la large jusqu'au plus
    loin."""
    sens, c, p, f = tl["le_sens"], int(tl["la_ligne"]), int(tl["la_plus_proche"]), int(tl["la_plus_loin"])
    return {"laile": les_coins_entre(sens, min(p, f), max(p, f), lo, hi),
            "letroite": les_coins_entre(sens, min(c, p), max(c, p), lo, hi),
            "la_large": les_coins_entre(sens, min(c, f), max(c, f), lo, hi)}


def _fusionner(*dicts) -> dict:
    """Les pas d'une même bande de bout, publiés en deux morceaux qui ne partagent aucune couture."""
    out: dict = {}
    for d in dicts:
        for l_, s in d.items():
            out.setdefault(int(l_), {}).update(s)
    return out


# ─────────────────────────────── l'emboîtement et le verdict ───────────────────────────────

def les_bouts(sens: str) -> tuple[str, str]:
    """Les deux côtés d'une boucle qui relient ses deux lignes parallèles."""
    return ("haut", "bas") if sens == "colonnes" else ("gauche", "droite")


def lemboitement_des_trois(par: dict, sens: str, jonction: int) -> dict:
    """À chaque largeur où aucun trou de majorité ne touche, sur un bout, la jonction avec la ligne commune, la large
    est la somme des deux autres, à l'arrondi près. Sinon, refus. ⚠ Un trou qui touche la jonction serait coupé
    autrement dans la large que dans les deux autres ; ailleurs, il se franchit de la même façon."""
    bouts = les_bouts(sens)

    def _touche(t):  # noqa: E306
        return t["le_cote"] in bouts and int(t["le_debut"]) <= int(jonction) <= int(t["le_debut"]) + int(t["la_longueur"])
    out = {}
    for k in sorted(par["laile"]["par_largeur"], key=int):
        xs = {n: par[n]["par_largeur"][k] for n in ("laile", "letroite", "la_large")}
        if any(not x["fermable"] or any(_touche(t) for t in x["les_trous"]) for x in xs.values()):
            out[k] = {"jugeable": False}
            continue
        s = float(xs["laile"]["la_fermeture_en_voxels"]) + float(xs["letroite"]["la_fermeture_en_voxels"])
        e = abs(s - float(xs["la_large"]["la_fermeture_en_voxels"]))
        tol = 3 * L_ARRONDI + 1e-9
        out[k] = {"jugeable": True, "la_somme": round(s, 4), "la_large": float(xs["la_large"]["la_fermeture_en_voxels"]),
                  "lecart": round(e, 6), "la_tolerance": round(tol, 6)}
        if e > tol:
            return {"decidable": False, "par_largeur": out,
                    "raison": (f"à {k} lignes, l'aile et l'étroite somment à {round(s, 4)} voxels et la large ferme à "
                               f"{xs['la_large']['la_fermeture_en_voxels']} : l'emboîtement ne retombe pas")}
    return {"decidable": True, "par_largeur": out,
            "combien_de_largeurs_jugees": sum(1 for x in out.values() if x["jugeable"])}


def lexclue(nom: str, tl: dict) -> int:
    """La ligne qu'une boucle exclut."""
    return {"laile": int(tl["la_ligne"]), "letroite": int(tl["la_plus_loin"]),
            "la_large": int(tl["la_plus_proche"])}[nom]


def _ce_qui_reste(aucune: bool, ouverte: bool, tranche: bool, derive: str | None) -> str:
    """Les issues, EXCLUSIVES, dans cet ordre de priorité."""
    if aucune:
        return "AUCUNE TROISIÈME LIGNE NE TIENT PRÈS DE L'AILE : RIEN NE DÉPARTAGE SES DEUX COLONNES"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE BOUCLE OUVERTE"
    if not tranche:
        return "À NEUF LIGNES, LES TROIS BOUCLES NE DÉPARTAGENT PAS LES DEUX COLONNES : LE BRUIT SEUL INVERSERAIT L'ORDRE"
    return f"À NEUF LIGNES, C'EST {derive} QUI DÉRIVE"


def le_verdict_des_trois(tl: dict | None, par: dict | None, k1: int) -> dict:
    """Le verdict à la plus large, depuis les trois boucles."""
    base = {"la_largeur_jugee": int(k1), "les_boucles_ouvertes": [], "la_plus_serree": None, "tranche": False,
            "la_ligne_qui_derive": None}
    if tl is None:
        return {**base, "ce_qui_reste_a_mesurer": _ce_qui_reste(True, False, False, None)}
    kk = str(k1)
    xs = {n: par[n]["par_largeur"][kk] for n in ("laile", "letroite", "la_large")}
    ouv = [n for n, x in xs.items() if not x["fermable"]]
    if ouv:
        return {**base, "les_boucles_ouvertes": ouv, "ce_qui_reste_a_mesurer": _ce_qui_reste(False, True, False, None)}
    L = {n: abs(float(x["la_fermeture_en_voxels"])) for n, x in xs.items()}
    serree = min(("laile", "letroite", "la_large"), key=lambda n: L[n])
    marges = {n: round(L[n] - L[serree] - float(xs[n]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]), 4)
              for n in L if n != serree}
    tranche = all(m >= 0 for m in marges.values())
    ligne = lexclue(serree, tl)
    nom_ = "LA COLONNE" if tl["le_sens"] == "colonnes" else "LA RANGÉE"
    lib = "LA TROISIÈME LIGNE" if ligne == int(tl["la_ligne"]) else f"{nom_} {ligne}"
    return {**base, "la_plus_serree": serree, "les_marges": marges, "tranche": bool(tranche),
            "la_ligne_qui_derive": ligne if tranche else None,
            "cest_une_colonne_de_laile": bool(tranche) and ligne != int(tl["la_ligne"]),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(False, False, tranche, lib)}


# ─────────────────────────────── la mesure ───────────────────────────────

def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par234: dict | None = None, lire=None,
            tirages: int | None = None) -> dict:
    """La troisième ligne dérivée, sa lecture, puis les trois boucles — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    par234 = ce_que_234_a_publie() if par234 is None else par234
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("234", par234)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    c_ = la_presence_retombe(A, par234["bandes"], par234["publiees"])
    base["la_presence_contre_234"] = c_
    if not c_.get("decidable"):
        return {**base, "decidable": False, "raison": c_.get("raison")}
    aile = laile_la_plus_lache(par234)
    if aile is None:
        return {**base, "decidable": False, "raison": "aucune aile de `234` ne ferme : il n'y a rien à départager"}
    k1 = les_largeurs()[-1]
    cote, coins = aile["le_cote"], aile["les_coins"]
    sens, _d, _e, lo, hi = les_lignes_de_laile(cote, coins)
    tl = la_troisieme_ligne(A, coins, cote, k1)
    base.update({"laile": aile, "la_troisieme_ligne": tl})
    if tl is None:
        return {**base, "decidable": True, "le_verdict": le_verdict_des_trois(None, None, k1)}
    boucles = les_trois_boucles(tl, lo, hi)
    bandes = les_bandes_de_la_troisieme(tl, lo, hi, k1)
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes(bandes, lire=lire)
    base.update({"les_boucles": boucles, "graine": int(g), "tirages": t_, "la_regle_de_225": par225["la_regle"],
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
    rep = la_reproduction_croisee(nouvelles, les_sources_de_235(par219, par223, par224, par232, par233, par234))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    daile = {**par234["ailes"][cote], "le_cote": cote}
    b234 = [b for b in par234["bandes"] if b in les_bandes_de_laile(daile, par233["coins"], k1)]
    pas = les_pas_de_laile(daile, par233["coins"], b234, par234["relues"], par233)
    neuves = les_pas_des_bandes(relues, bandes)
    for cle, x in neuves.items():
        pas[cle] = _fusionner(pas.get(cle) or {}, x)
    par = {}
    for nom, co in boucles.items():
        a = analyser(pas, co, par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"la boucle {nom} : {a.get('raison')}", "la_reproduction": rep}
        par[nom] = {"les_coins": co, **a}
    pa = par234["par_aile"][cote]["par_largeur"]
    for k, x in par["laile"]["par_largeur"].items():
        y = pa.get(k) or {}
        if bool(x["fermable"]) != bool(y.get("fermable")) or (
                x["fermable"] and abs(float(x["la_fermeture_en_voxels"]) - float(y["la_fermeture_en_voxels"]))
                > 2 * L_ARRONDI + 1e-9):
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"à {k} lignes, la boucle de l'aile ne retombe pas sur ce que `234` publie"}
    emb = lemboitement_des_trois(par, sens, tl["la_plus_proche"])
    if not emb.get("decidable"):
        return {**base, "decidable": False, "raison": emb.get("raison"), "la_reproduction": rep, "lemboitement": emb}
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_boucle": par, "lemboitement": emb, "le_verdict": le_verdict_des_trois(tl, par, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"aile : {r['laile']}")
    print(f"troisième ligne : {r['la_troisieme_ligne']}")
    if "par_boucle" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        print(f"emboîtement : {r['lemboitement']}")
        for n, b in r["par_boucle"].items():
            for k, x in b["par_largeur"].items():
                if not x["fermable"]:
                    print(f"  {n} {b['les_coins']} · {k} lignes · OUVERT · {x['les_trous_trop_longs']}")
                    continue
                print(f"  {n} {b['les_coins']} · {k} lignes · L {x['la_fermeture_en_voxels']} · σ "
                      f"{x['la_dispersion_du_pas_en_voxels']} · nul {x['le_nul']} · trous {x['les_trous']} · côtés "
                      f"{x['les_cotes']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

    from le_segment_au_dela_du_rectangle_se_relie_t_il import les_sources_de_234
    from ou_sarrete_le_segment import les_sources
    from le_segment_au_dela_du_rectangle_se_relie_t_il import mesurer as mesurer_234
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

    # la troisième ligne : contre une recherche exhaustive écrite autrement, sur des empreintes au hasard
    def _tient(A_, sens, centre, de, a, k):  # noqa: E306
        L = les_rangees_a_lire(centre, k)
        gy, gx = A_.shape
        if a <= de or min(L) < 0 or max(L) >= (gy if sens == "rangees" else gx):
            return False
        for s in range(de, a):
            for l_ in L:
                if not (A_[l_, s] and A_[l_, s + 1] if sens == "rangees" else A_[s, l_] and A_[s + 1, l_]):
                    return False
        return True

    def _brute(A_, coins, cote, k):  # noqa: E306
        sens, dedans, dehors, lo, hi = les_lignes_de_laile(cote, coins)
        trav = "rangees" if sens == "colonnes" else "colonnes"
        n_ = A_.shape[1] if sens == "colonnes" else A_.shape[0]
        best = None
        for c in range(n_):
            for proche in (dedans, dehors):
                autre = dehors if proche == dedans else dedans
                if abs(c - proche) < k or abs(c - autre) < k or (min(dedans, dehors) < c < max(dedans, dehors)):
                    continue
                if abs(c - autre) < abs(c - proche):
                    continue
                a_, b_ = min(c, proche), max(c, proche)
                if not (_tient(A_, sens, c, lo, hi, k) and _tient(A_, trav, lo, a_, b_, k)
                        and _tient(A_, trav, hi, a_, b_, k)):
                    continue
                cle = (abs(c - proche), 0 if proche == dedans else 1)
                if best is None or cle < best[0]:
                    best = (cle, c)
        return None if best is None else best[1]
    g = np.random.default_rng(236)
    accord, vus = [], 0
    for i in range(12):
        Ar = np.ones((24, 40), dtype=bool)
        for _ in range(int(g.integers(2, 9))):
            y, x = int(g.integers(0, 24)), int(g.integers(0, 40))
            Ar[max(0, y - int(g.integers(0, 3))):y + 1, max(0, x - int(g.integers(0, 3))):x + 1] = False
        cote = ("droite", "gauche")[i % 2]
        co = [4, 19, 17, 23] if cote == "droite" else [4, 19, 17, 23]
        t_ = _sur(la_troisieme_ligne, Ar, co, cote, 3)
        b_ = _brute(Ar, co, cote, 3)
        accord.append((None if t_ is None else t_.get("la_ligne")) == b_)
        vus += b_ is not None
    v("★★★★ la troisième ligne est celle d'une recherche exhaustive, sur douze empreintes au hasard",
      all(accord) and vus >= 8, f"{accord} {vus}")
    Ap = np.ones((396, 285), dtype=bool)
    tp = _sur(la_troisieme_ligne, Ap, [26, 223, 243, 260], "droite", 9)
    v("★★★★ sur une grille pleine, la troisième ligne de l'aile de droite est la colonne 234, du côté du rectangle",
      _ok(lambda: tp["la_ligne"] == 234 and tp["la_plus_proche"] == 243 and tp["la_plus_loin"] == 260
          and tp["du_cote_du_rectangle"] and tp["lecart"] == 9), str(tp))
    Ah = Ap.copy()
    Ah[100:103, 230:238] = False
    th = _sur(la_troisieme_ligne, Ah, [26, 223, 243, 260], "droite", 9)
    v("★★★★ une colonne coupée par un trou ne tient pas : la troisième ligne passe de l'autre côté de l'aile",
      _ok(lambda: th["la_ligne"] == 269 and th["la_plus_proche"] == 260 and not th["du_cote_du_rectangle"]), str(th))
    Ab = Ah.copy()
    Ab[100:103, 265:274] = False
    tb = _sur(la_troisieme_ligne, Ab, [26, 223, 243, 260], "droite", 9)
    v("★★★ à égale distance des deux côtés, la troisième ligne est du côté du rectangle",
      _ok(lambda: tb["la_ligne"] == 225 and tb["lecart"] == 18 and tb["du_cote_du_rectangle"]), str(tb))
    Ae = Ap.copy()
    Ae[222, 234:243] = False
    te = _sur(la_troisieme_ligne, Ae, [26, 223, 243, 260], "droite", 9)
    v("★★★★ une bande de bout qui ne tient pas écarte la troisième ligne", _ok(lambda: te["la_ligne"] != 234), str(te))
    tg = _sur(la_troisieme_ligne, Ap, [216, 308, 13, 22], "gauche", 9)
    v("★★★ la troisième ligne d'une aile de gauche est du côté du rectangle, à droite de sa colonne intérieure",
      _ok(lambda: tg["la_ligne"] == 31 and tg["la_plus_proche"] == 22 and tg["la_plus_loin"] == 13), str(tg))
    tt = _sur(la_troisieme_ligne, Ap, [14, 26, 32, 81], "haut", 9)
    v("★★★ la troisième ligne d'une aile du haut est une rangée",
      _ok(lambda: tt["le_sens"] == "rangees" and tt["la_ligne"] == 35 and tt["la_plus_proche"] == 26), str(tt))
    v("★★★★ sans place autour, aucune troisième ligne", _sur(la_troisieme_ligne, np.ones((40, 30), dtype=bool),
                                                             [4, 35, 6, 23], "droite", 9) is None)
    bd = _sur(les_bandes_de_la_troisieme, tp, 26, 223, 9)
    v("★★★★ se lisent la troisième ligne sur toute l'aile et ses deux bouts vers le côté le plus proche",
      _ok(lambda: [b["cle"] for b in bd] == ["colonnes_234_26_223", "rangees_26_234_243", "rangees_223_234_243"]
          and bd[0]["les_lignes"] == list(range(230, 239)) and (bd[0]["de"], bd[0]["a"]) == (26, 223)
          and all((b["de"], b["a"]) == (234, 243) for b in bd[1:])))
    tb3 = _sur(les_trois_boucles, tp, 26, 223)
    v("★★★★ les trois boucles : l'aile, l'étroite vers le côté le plus proche, la large vers le plus loin",
      _ok(lambda: tb3 == {"laile": [26, 223, 243, 260], "letroite": [26, 223, 234, 243],
                          "la_large": [26, 223, 234, 260]}))
    v("★★★ les trois boucles d'une aile du haut sont des boucles de rangées",
      _ok(lambda: les_trois_boucles(tt, 32, 81) == {"laile": [14, 26, 32, 81], "letroite": [26, 35, 32, 81],
                                                    "la_large": [14, 35, 32, 81]}
          and les_bouts("rangees") == ("gauche", "droite") and les_bouts("colonnes") == ("haut", "bas")))
    v("★★★ chaque boucle exclut une ligne : la troisième, la plus loin, la plus proche",
      _ok(lambda: [lexclue(n, tp) for n in ("laile", "letroite", "la_large")] == [234, 260, 243]))
    v("★★★ deux morceaux d'une bande de bout se fusionnent sans se recouvrir",
      _fusionner({1: {5: 0.1}}, {1: {6: 0.2}, 2: {6: 0.3}}) == {1: {5: 0.1, 6: 0.2}, 2: {6: 0.3}})

    # l'emboîtement et le verdict, sur des boucles fabriquées
    def _x(L, med=5.0, fermable=True, trous=()):  # noqa: E306
        return {"fermable": fermable, "la_fermeture_en_voxels": L, "le_nul": {"la_fermeture_mediane_en_valeur_absolue":
                                                                              med}, "les_trous": list(trous)}

    def _par(La, Le, Ll, **kw):  # noqa: E306
        return {n: {"par_largeur": {"9": _x(L, **kw.get(n, {}))}} for n, L in (("laile", La), ("letroite", Le),
                                                                                ("la_large", Ll))}
    v("★★★★ la large est la somme de l'aile et de l'étroite : l'emboîtement passe",
      lemboitement_des_trois(_par(-35.6938, 30.0, -5.6938), "colonnes", 243).get("decidable"))
    v("★★★★ une large qui n'est pas la somme est refusée, par sa raison",
      "l'emboîtement ne retombe pas" in str(lemboitement_des_trois(_par(-35.6938, 30.0, -5.6), "colonnes", 243)
                                           .get("raison")))
    tj = [{"le_cote": "haut", "le_debut": 241, "la_longueur": 2}]
    ta = [{"le_cote": "bas", "le_debut": 250, "la_longueur": 2}]
    tp_ = [{"le_cote": "droite", "le_debut": 243, "la_longueur": 1}]
    v("★★★★ un trou de bout qui touche la jonction empêche de juger ; ailleurs, sur un bout ou une ligne, non",
      not lemboitement_des_trois(_par(-35.6938, 30.0, -5.6, letroite={"trous": tj}), "colonnes", 243)["par_largeur"]
      ["9"]["jugeable"]
      and not lemboitement_des_trois(_par(-35.6938, 30.0, -5.6, la_large={"trous": ta}), "colonnes", 243).get("decidable")
      and not lemboitement_des_trois(_par(-35.6938, 30.0, -5.6, letroite={"trous": tp_}), "colonnes", 243)
      .get("decidable"))
    vb = le_verdict_des_trois(tp, _par(-35.6938, 30.0, -5.6938), 9)
    v("★★★★ la boucle qui exclut la colonne 243 ferme le plus serré, de loin : la colonne 243 dérive",
      vb["tranche"] and vb["la_plus_serree"] == "la_large" and vb["la_ligne_qui_derive"] == 243
      and vb["cest_une_colonne_de_laile"] and "LA COLONNE 243 QUI DÉRIVE" in vb["ce_qui_reste_a_mesurer"], str(vb))
    vc = le_verdict_des_trois(tp, _par(-35.6938, -1.0, -36.6938), 9)
    v("★★★★ la boucle qui exclut la colonne 260 ferme le plus serré : la colonne 260 dérive",
      vc["tranche"] and vc["la_ligne_qui_derive"] == 260 and "260 QUI DÉRIVE" in vc["ce_qui_reste_a_mesurer"])
    vn = le_verdict_des_trois(tp, _par(-35.6938, 17.0, -18.6938), 9)
    v("★★★★ deux boucles trop proches l'une de l'autre au regard du bruit seul ne départagent pas",
      not vn["tranche"] and vn["la_ligne_qui_derive"] is None and "NE DÉPARTAGENT PAS" in vn["ce_qui_reste_a_mesurer"])
    v("★★★ la marge est prise contre le bruit seul de chaque autre boucle",
      le_verdict_des_trois(tp, _par(-35.6938, 30.0, -5.6938, letroite={"med": 25.0}), 9)["tranche"] is False)
    vt = le_verdict_des_trois(tp, _par(-2.0, 40.0, 38.0), 9)
    v("★★★ si l'aile ferme le plus serré, c'est la troisième ligne qui dérive",
      vt["tranche"] and vt["la_ligne_qui_derive"] == 234 and not vt["cest_une_colonne_de_laile"]
      and "LA TROISIÈME LIGNE QUI DÉRIVE" in vt["ce_qui_reste_a_mesurer"])
    vo = le_verdict_des_trois(tp, _par(-35.6938, 30.0, -5.6938, letroite={"fermable": False}), 9)
    v("★★★★ une boucle ouverte prime", not vo["tranche"] and vo["les_boucles_ouvertes"] == ["letroite"]
      and "OUVERTE" in vo["ce_qui_reste_a_mesurer"])
    v0 = le_verdict_des_trois(None, None, 9)
    v("★★★★ sans troisième ligne, rien ne départage", not v0["tranche"] and "RIEN NE DÉPARTAGE" in
      v0["ce_qui_reste_a_mesurer"])
    v("★★★ les issues sont distinctes",
      len({_ce_qui_reste(a, b, c, "LA COLONNE 243") for a, b, c in itertools.product((True, False), repeat=3)}
          | {_ce_qui_reste(False, False, True, "LA TROISIÈME LIGNE")}) == 5)

    # la mesure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
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

    def _sur_lempreinte(A_, champ):  # noqa: E306
        # l'empreinte fabriquée, et les bandes de 233 relues dans le champ fabriqué, sauf là où une autre source
        # publiée lit la même couture : aucune dérive réelle de 233 n'y reste, et les sources s'accordent encore
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

    def _fabrique(bd, src, champ):  # noqa: E306
        dom = le_domaine(bd["le_sens"], bd["les_lignes"], bd["de"], bd["a"])
        le_long_f, trav_f = (("h", "v") if bd["le_sens"] == "rangees" else ("v", "h"))
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
            a_, b_ = (r, c) if bd["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(Af, bd["le_sens"], l_, bd["de"], bd["a"])}}
                    for l_ in bd["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}

    def _scenario(champ):  # noqa: E306
        q2, q3 = _sur_lempreinte(Af, champ)
        s0 = les_sources_de_234(p219, p223, p224, q2, q3)
        m4 = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q2, q3, lambda bd: _fabrique(bd, s0, champ), 49)
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m234.json"
            pj.write_text(json.dumps(m4, ensure_ascii=False))
            q4 = ce_que_234_a_publie(pj)
        s1 = les_sources_de_235(p219, p223, p224, q2, q3, q4) if q4.get("decidable") else {}
        return q2, q3, q4, m4, s1
    q232f, q233f, q234f, m234, src1 = _scenario(_derive)
    v("★★★★ 234 rejoué sur l'empreinte fabriquée : seule l'aile de droite ferme",
      _ok(lambda: m234["le_verdict"]["les_ailes_qui_ferment"] == ["droite"]
          and m234["les_ailes"]["droite"]["les_coins"] == [26, 195, 243, 276]), str(m234.get("raison")
                                                                                 or m234.get("le_verdict")))
    lus = []

    def _lit(bd):  # noqa: E306
        lus.append(bd)
        return _fabrique(bd, src1, _derive)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _lit, 49)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_boucle" in m, str(m.get("raison")))
    v("★★★★ la troisième ligne est la colonne 234, et trois bandes seulement sont lues",
      _ok(lambda: m["la_troisieme_ligne"]["la_ligne"] == 234 and [b["cle"] for b in lus]
          == ["colonnes_234_26_195", "rangees_26_234_243", "rangees_195_234_243"]), str(m.get("la_troisieme_ligne")))
    v("★★★★ chaque bande neuve est contrôlée par une bande publiée, le bout du haut par la bande de 233",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]} == {b["cle"] for b in lus}
          and any(k.startswith("rangees_26_234_243×233 ") for k in m["la_reproduction"]["par_croisement"])),
      str(m.get("la_reproduction", {}).get("par_croisement")))
    v("★★★★ la boucle de l'aile retombe sur 234, et la large sur la somme des deux autres à neuf lignes",
      _ok(lambda: m["par_boucle"]["laile"]["par_largeur"]["9"]["la_fermeture_en_voxels"]
          == m234["par_aile"]["droite"]["par_largeur"]["9"]["la_fermeture_en_voxels"]
          and m["lemboitement"]["par_largeur"]["9"]["jugeable"]),
      str({n: {k_: x.get("les_trous") for k_, x in b_["par_largeur"].items()} for n, b_ in (m.get("par_boucle") or {}).items()}))
    v("★★★★ la colonne extérieure qui dérive est désignée : la boucle qui l'exclut ferme le plus serré",
      _ok(lambda: m["le_verdict"]["tranche"] and m["le_verdict"]["la_plus_serree"] == "letroite"
          and m["le_verdict"]["la_ligne_qui_derive"] == 276), str(m.get("le_verdict")))
    v("★★★★ la règle de 225 est appliquée, et le verdict est celui des trois boucles",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["le_verdict"] == le_verdict_des_trois(m["la_troisieme_ligne"], m["par_boucle"], 9)))

    def _derive_dedans(f, r, c):  # noqa: E306
        # la colonne intérieure dérive, dans la bande de 233 comme partout où elle se lit
        return _champ(f, r, c) + (0.15 if f == "v" and 239 <= c <= 247 else 0.0) + (
            0.3 if f == "v" and c <= 11 else 0.0)
    q232d, q233d, q234d, m234d, src_d = _scenario(_derive_dedans)
    md = _sur(mesurer, None, p219, p223, p224, p225, q225, q232d, q233d, q234d,
              lambda bd: _fabrique(bd, src_d, _derive_dedans), 49)
    v("★★★★ la colonne intérieure qui dérive est désignée : la boucle large, qui l'exclut, ferme le plus serré",
      _ok(lambda: md["le_verdict"]["tranche"] and md["le_verdict"]["la_plus_serree"] == "la_large"
          and md["le_verdict"]["la_ligne_qui_derive"] == 243), str(md.get("raison") or md.get("le_verdict")))

    def _menteuse(bd):  # noqa: E306
        x = _fabrique(bd, src1, _derive)
        x["les_lectures"][bd["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _menteuse, 49)
                              .get("raison")))
    q234r = ce_que_234_a_publie()
    v("★★★★ une présence qui ne retombe pas sur les bandes de 234 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f,
                                   {**q234f, "publiees": q234r.get("publiees"), "bandes": q234r.get("bandes")},
                                   lambda bd: _fabrique(bd, src1, _derive), 49).get("raison")))
    analyser_vrai = globals()["analyser"]

    def _analyser_faux(pas_, co, *a, **kw):  # noqa: E306
        r = analyser_vrai(pas_, co, *a, **kw)
        if m.get("les_boucles") and co == m["les_boucles"]["la_large"] and r.get("decidable"):
            r["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
        return r
    globals()["analyser"] = _analyser_faux
    try:
        me = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f,
                  lambda bd: _fabrique(bd, src1, _derive), 49)
    finally:
        globals()["analyser"] = analyser_vrai
    v("★★★★ une large qui ne retombe pas sur la somme des deux autres est refusée, par sa raison",
      "l'emboîtement ne retombe pas" in str(me.get("raison")), str(me.get("raison")))

    def _decale(bd):  # noqa: E306
        x = _fabrique(bd, src1, _derive)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une bande qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _decale, 49)
                                  .get("raison")))
    q234e = copy.deepcopy(q234f)
    if q234e.get("decidable"):
        q234e["par_aile"]["droite"]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ une boucle de l'aile qui ne retombe pas sur ce que 234 publie est refusée",
      "ne retombe pas sur ce que `234` publie" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f,
                                                            q234e, lambda bd: _fabrique(bd, src1, _derive), 49)
                                                       .get("raison")))
    q234n = copy.deepcopy(q234f)
    if q234n.get("decidable"):
        q234n["verdict"]["les_ailes_qui_ferment"] = []
    lus_n = []
    v("★★★★ sans aile qui ferme dans 234, rien n'est lu",
      "rien à départager" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234n,
                                      lambda bd: lus_n.append(bd) or _fabrique(bd, src1, _derive), 49).get("raison"))
      and not lus_n)
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        faux = {k: dict(x) for k, x in (m.get("les_bandes") or {}).items()}
        if faux:
            une = sorted(faux)[0]
            faux[une] = {**faux[une], "les_lignes": [x - 2 for x in faux[une]["les_lignes"]]}
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, None, 49)
        dep.write_text(json.dumps({"les_bandes": m.get("les_bandes") or {}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, q234f, None, 49)
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
        par233, par234 = ce_que_233_a_publie(), ce_que_234_a_publie()
        for nom, par in (("233", par233), ("234", par234)):
            if not par.get("decidable"):
                print(f"indécidable : `{nom}` : {par.get('raison')}")
                return 1
        aile = laile_la_plus_lache(par234)
        if aile is None:
            print("indécidable : aucune aile de `234` ne ferme")
            return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        _s, _d, _e, lo, hi = les_lignes_de_laile(aile["le_cote"], aile["les_coins"])
        tl = la_troisieme_ligne(A, aile["les_coins"], aile["le_cote"], k1)
        print(f"aile : {aile}", flush=True)
        print(f"troisième ligne : {tl}", flush=True)
        if tl is None:
            return 0
        bandes = les_bandes_de_la_troisieme(tl, lo, hi, k1)
        print(f"boucles : {les_trois_boucles(tl, lo, hi)}", flush=True)
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
