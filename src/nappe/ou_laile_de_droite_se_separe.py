"""Où, le long de l'aile la plus lâche, ses deux longs côtés se séparent-ils ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE, ET AVANT QUE LES COUPES NE SOIENT
DÉRIVÉES. Ce qui était vu avant d'écrire : ce que `234` publie, et la figure qui le montre.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P80`. `234` a relié trois ailes au plus grand rectangle de `233`.
À neuf lignes, l'aile de droite, des rangées 26 à 223 et des colonnes 243 à 260, ferme à −35,6938 voxels, à
0,3062 du demi-feuillet, et le bruit seul ferme plus serré dans 0,8959 des tirages. Son écart tient à ses deux
colonnes : 28,9375 voxels le long de la colonne 243, −4,9437 le long de la colonne 260. Entre-t-il d'un coup,
entre deux rangées, ou se cumule-t-il le long de l'aile ?

## L'aile, désignée

L'aile découpée est celle que `234` publie comme la plus lâche : parmi les ailes qui ferment, celle dont la
fermeture à neuf lignes est la plus grande. Elle n'est pas choisie.

## Les coupes, dérivées

Une COUPE est une bande de travers, parallèle aux deux bouts de l'aile, tendue entre ses deux longs côtés. Elle
tient au sens de `233` : à chaque couture, ses neuf lignes ont leurs deux chunks dans le dépôt. Deux coupes
voisines sont à neuf lignes au moins l'une de l'autre, et des deux bouts : aucune ligne n'est partagée. Les
coupes découpent l'aile en SOUS-BOUCLES. Parmi tous les découpages : le plus de sous-boucles, puis le plus petit
des plus grands écarts entre deux coupes, puis les coupes les plus tôt. Le code les dérive de la présence que
`233` publie, et de rien d'autre.

## Ce qui se lit, et ce qui le contrôle

Les coupes seules, neuf lignes chacune, par le lecteur de `224`. ⚠⚠ Les deux longs côtés et les deux bouts ne
sont pas relus : leurs pas sont ceux que `233` et `234` publient. ⚠⚠⚠ Partout où une coupe croise une bande
publiée — `219`, `223`, `224`, `232`, `233`, `234` —, les pas relus retombent à l'arrondi, sinon refus ; une
coupe qui ne croise aucune bande publiée est refusée. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont
ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque sous-boucle, à chaque largeur de l'échelle de `218`, avec la garde de `232` : un
trou de majorité se franchit par le maillage, et seulement jusqu'aux coutures que `225` a essayées.

⚠⚠⚠ LES SOUS-BOUCLES S'EMBOÎTENT : chaque coupe est parcourue une fois dans chaque sens, donc la somme de leurs
fermetures est la fermeture de l'aile. À chaque largeur où ni l'aile ni aucune sous-boucle n'a de trou de
majorité le long de ses deux longs côtés, la somme retombe sur ce que `234` publie, à l'arrondi près, sinon refus.
⚠ Un trou sur une coupe ne l'empêche pas : il se franchit de la même façon dans les deux sous-boucles qui la
partagent, et s'y annule.

LE PROFIL : la fermeture cumulée, coupe après coupe, d'un bout de l'aile à l'autre.

## Les issues, exclusives, jugées à neuf lignes

- aucune coupe ne tient : l'aile ne se découpe pas, et rien n'est lu ;
- une sous-boucle garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- une sous-boucle atteint le demi-feuillet : l'aile change de spire entre deux coupes, qui sont nommées ;
- aucune ne l'atteint : l'écart de l'aile se cumule d'une coupe à l'autre.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux longs côtés dérive — entre les colonnes 243 et 260, dix-sept
coutures, aucune troisième colonne de neuf lignes ne tient sans partager de ligne avec l'une des deux ; ni ce qui
reste de l'empreinte au-delà des ailes.

Usage :
    uv run python src/nappe/ou_laile_de_droite_se_separe.py --verifier
    uv run python src/nappe/ou_laile_de_droite_se_separe.py --lire <lecture.json>
    uv run python src/nappe/ou_laile_de_droite_se_separe.py --depuis <lecture.json> \\
        --json docs/mesures/ou_laile_de_droite_se_separe.json
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
from le_segment_au_dela_du_rectangle_se_relie_t_il import (LES_COTES,  # noqa: E402
                                                           ce_que_233_a_publie, les_bandes_de_laile,
                                                           les_pas_de_laile, les_sources_de_234, les_tenues,
                                                           tient)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, les_pas_dune_bande)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, les_absents_dune_ligne)
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_234_A_PUBLIE = MESURES / "le_segment_au_dela_du_rectangle_se_relie_t_il.json"
L_ARRONDI = 5e-5  # une fermeture est publiée à quatre décimales

LA_QUESTION_DECLAREE = "où, le long de l'aile la plus lâche, ses deux longs côtés se séparent-ils ?"
LA_MESURE_DECLAREE = ("l'aile la plus lâche de `234`, découpée par les bandes de travers de neuf lignes qui y "
                      "tiennent, et l'instrument de `228` sur chaque sous-boucle")


# ─────────────────────────────── ce que `234` publie ───────────────────────────────

def ce_que_234_a_publie(chemin: Path = CE_QUE_234_A_PUBLIE) -> dict:
    """Les ailes, leurs bandes relues et leur analyse, telles que `234` les publie."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if (not d.get("decidable") or not d.get("les_ailes") or not d.get("par_aile") or not d.get("les_bandes")
            or not d.get("les_bandes_declarees") or not d.get("le_verdict")):
        return {"decidable": False, "raison": "`234` ne publie pas ses ailes, leurs bandes ou leur analyse"}
    return {"decidable": True, "ailes": d["les_ailes"], "par_aile": d["par_aile"],
            "bandes": d["les_bandes_declarees"], "publiees": d["les_bandes"],
            "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()}, "verdict": d["le_verdict"]}


def laile_la_plus_lache(par234: dict) -> dict | None:
    """Parmi les ailes qui ferment, celle dont la fermeture à la largeur jugée est la plus grande ; à égalité, la
    première dans l'ordre haut, droite, bas, gauche. Aucune si aucune ne ferme."""
    v = par234["verdict"]
    k1 = str(v["la_largeur_jugee"])
    meilleure = None
    for c in LES_COTES:
        if c not in (v.get("les_ailes_qui_ferment") or []):
            continue
        L = float(par234["par_aile"][c]["par_largeur"][k1]["la_fermeture_en_voxels"])
        if meilleure is None or abs(L) > abs(meilleure["la_fermeture_en_voxels"]):
            meilleure = {"le_cote": c, "les_coins": [int(x) for x in par234["ailes"][c]["les_coins"]],
                         "la_fermeture_en_voxels": L}
    return meilleure


# ─────────────────────────────── les coupes, dérivées ───────────────────────────────

def le_travers(cote: str, coins) -> tuple[str, int, int, int, int]:
    """`(sens, lo, hi, de, a)` : les coupes sont des bandes `sens`, centrées de `lo` à `hi`, tendues de `de` à `a`."""
    a0, a1, b0, b1 = [int(x) for x in coins]
    if cote in ("droite", "gauche"):
        return "rangees", a0, a1, b0, b1
    return "colonnes", b0, b1, a0, a1


def les_coupes(A: np.ndarray, coins, cote: str, k: int, tenues=None) -> dict:
    """Le découpage de l'aile : le plus de sous-boucles, puis le plus petit des plus grands écarts, puis les coupes
    les plus tôt. Les deux bouts sont des coupes ; deux coupes voisines sont à `k` lignes au moins."""
    A = np.asarray(A, dtype=bool)
    k = int(k)
    PR, PC = tenues if tenues is not None else les_tenues(A, k)
    sens, lo, hi, de, a = le_travers(cote, coins)
    F = [y for y in range(lo, hi + 1) if y in (lo, hi) or tient(PR, PC, sens, y, de, a)]
    cnt = {hi: 0}
    for y in reversed(F[:-1]):
        cs = [cnt[n] + 1 for n in F if n >= y + k and n in cnt]
        if cs:
            cnt[y] = max(cs)
    m = int(cnt.get(lo, 0))
    mg = {(hi, 0): 0}
    for y in reversed(F[:-1]):
        for t in range(1, m + 1):
            gs = [max(n - y, mg[(n, t - 1)]) for n in F if n >= y + k and (n, t - 1) in mg]
            if gs:
                mg[(y, t)] = min(gs)
    g = int(mg[(lo, m)]) if m else 0
    ok = {(hi, 0)}
    for y in reversed(F[:-1]):
        for t in range(1, m + 1):
            if any(k <= n - y <= g and (n, t - 1) in ok for n in F):
                ok.add((y, t))
    coupes, y = [lo], lo
    for t in range(m, 0, -1):
        y = next(n for n in F if k <= n - y <= g and (n, t - 1) in ok)
        coupes.append(int(y))
    return {"le_sens": sens, "les_bornes": [int(de), int(a)], "les_coupes": coupes,
            "combien_de_sous_boucles": m, "le_plus_grand_ecart": g}


def les_sous_boucles(cote: str, coins, coupes) -> list[list[int]]:
    """Les coins de chaque sous-boucle, d'une coupe à la suivante."""
    a0, a1, b0, b1 = [int(x) for x in coins]
    if cote in ("droite", "gauche"):
        return [[int(coupes[j]), int(coupes[j + 1]), b0, b1] for j in range(len(coupes) - 1)]
    return [[a0, a1, int(coupes[j]), int(coupes[j + 1])] for j in range(len(coupes) - 1)]


def les_bandes_des_coupes(dec: dict, k: int) -> list[dict]:
    """Les coupes à lire : toutes sauf les deux bouts, que `234` publie."""
    sens, (de, a) = dec["le_sens"], dec["les_bornes"]
    return [{"cle": f"{sens}_{c}_{de}_{a}", "le_sens": sens, "le_centre": int(c),
             "les_lignes": les_rangees_a_lire(int(c), int(k)), "de": int(de), "a": int(a)}
            for c in dec["les_coupes"][1:-1]]


# ─────────────────────────────── l'emboîtement, le profil, le verdict ───────────────────────────────

def les_longs_cotes(cote: str) -> tuple[str, str]:
    """Les deux côtés d'une boucle qui suivent l'aile de bout en bout."""
    return ("gauche", "droite") if cote in ("droite", "gauche") else ("haut", "bas")


def lemboitement(par_sb: list[dict], aile234: dict, cote: str) -> dict:
    """À chaque largeur où ni l'aile ni aucune sous-boucle n'a de trou de majorité le long de ses deux longs côtés,
    la somme des fermetures des sous-boucles retombe sur celle que `234` publie pour l'aile, à l'arrondi près.
    Sinon, refus. ⚠ Un trou sur une coupe se franchit de la même façon dans les deux sous-boucles qui la partagent."""
    longs = les_longs_cotes(cote)

    def _troue(x):  # noqa: E306
        return any(t["le_cote"] in longs for t in x["les_trous"])
    out = {}
    for k in sorted(aile234["par_largeur"], key=int):
        xa = aile234["par_largeur"][k]
        xs = [sb["par_largeur"][k] for sb in par_sb]
        if not xa["fermable"] or _troue(xa) or any(not x["fermable"] or _troue(x) for x in xs):
            out[k] = {"jugeable": False}
            continue
        s = float(sum(float(x["la_fermeture_en_voxels"]) for x in xs))
        e = abs(s - float(xa["la_fermeture_en_voxels"]))
        tol = L_ARRONDI * (len(xs) + 1) + 1e-9
        out[k] = {"jugeable": True, "la_somme_des_sous_boucles": round(s, 4),
                  "la_fermeture_de_laile": float(xa["la_fermeture_en_voxels"]), "lecart": round(e, 6),
                  "la_tolerance": round(tol, 6)}
        if e > tol:
            return {"decidable": False, "par_largeur": out,
                    "raison": (f"à {k} lignes, les sous-boucles somment à {round(s, 4)} voxels et l'aile ferme à "
                               f"{xa['la_fermeture_en_voxels']} : l'emboîtement ne retombe pas")}
    return {"decidable": True, "par_largeur": out,
            "combien_de_largeurs_jugees": sum(1 for x in out.values() if x["jugeable"])}


def le_profil(par_sb: list[dict], k1: int) -> list[dict]:
    """La fermeture cumulée, coupe après coupe, à la largeur jugée — tant qu'aucune sous-boucle n'est ouverte."""
    cum, out = 0.0, []
    for sb in par_sb:
        x = sb["par_largeur"][str(k1)]
        if not x["fermable"]:
            return out
        cum += float(x["la_fermeture_en_voxels"])
        out.append({"la_coupe": int(sb["entre"][1]), "le_cumul_en_voxels": round(cum, 4)})
    return out


def _ce_qui_reste(sans_coupe: bool, ouverte: bool, loin: bool) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if sans_coupe:
        return "AUCUNE COUPE NE TIENT DANS L'AILE : ELLE NE SE DÉCOUPE PAS"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE SOUS-BOUCLE OUVERTE"
    if loin:
        return "À NEUF LIGNES, UNE SOUS-BOUCLE ARRIVE À UN DEMI-FEUILLET : L'AILE CHANGE DE SPIRE ENTRE DEUX COUPES"
    return ("À NEUF LIGNES, AUCUNE SOUS-BOUCLE N'ARRIVE À UN DEMI-FEUILLET : L'ÉCART DE L'AILE SE CUMULE D'UNE COUPE "
            "À L'AUTRE")


def le_verdict_des_coupes(combien: int, par_sb: list[dict], k1: int) -> dict:
    """Le verdict à la plus large, depuis l'analyse de chaque sous-boucle."""
    kk = str(k1)
    if int(combien) < 2:
        return {"la_largeur_jugee": int(k1), "combien_de_sous_boucles": int(combien),
                "les_sous_boucles_ouvertes": [], "les_sous_boucles_a_un_demi_feuillet": [], "la_plus_grande": None,
                "laile_change_de_spire": False, "lecart_se_cumule": False,
                "ce_qui_reste_a_mesurer": _ce_qui_reste(True, False, False)}
    ouv = [sb["entre"] for sb in par_sb if not sb["par_largeur"][kk]["fermable"]]
    loin = [sb["entre"] for sb in par_sb if sb["par_largeur"][kk]["fermable"]
            and not sb["par_largeur"][kk]["sous_le_demi_pli"]]
    fermables = [sb for sb in par_sb if sb["par_largeur"][kk]["fermable"]]
    plus = None
    if fermables:
        sb = max(fermables, key=lambda s: abs(float(s["par_largeur"][kk]["la_fermeture_en_voxels"])))
        plus = {"entre": sb["entre"], "la_fermeture_en_voxels": sb["par_largeur"][kk]["la_fermeture_en_voxels"]}
    return {"la_largeur_jugee": int(k1), "combien_de_sous_boucles": int(combien), "les_sous_boucles_ouvertes": ouv,
            "les_sous_boucles_a_un_demi_feuillet": loin, "la_plus_grande": plus,
            "laile_change_de_spire": bool(loin) and not ouv, "lecart_se_cumule": not ouv and not loin,
            "ce_qui_reste_a_mesurer": _ce_qui_reste(False, bool(ouv), bool(loin))}


# ─────────────────────────────── la mesure ───────────────────────────────

def les_sources_de_235(par219: dict, par223: dict, par224: dict, par232: dict, par233: dict, par234: dict) -> dict:
    """Ce qui contrôle une coupe : les sources de `234`, et les neuf bandes que `234` publie."""
    out = les_sources_de_234(par219, par223, par224, par232, par233)
    for b in par234["bandes"]:
        out[f"234 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                  "pas": les_pas_dune_bande(par234["relues"][b["cle"]])}
    return out


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par234: dict | None = None, lire=None,
            tirages: int | None = None) -> dict:
    """L'aile la plus lâche de `234`, ses coupes dérivées, leur lecture puis l'analyse — ou rejouées."""
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
        return {**base, "decidable": False, "raison": "aucune aile de `234` ne ferme : il n'y a rien à découper"}
    k1 = les_largeurs()[-1]
    cote, coins = aile["le_cote"], aile["les_coins"]
    dec = les_coupes(A, coins, cote, k1)
    sbs = les_sous_boucles(cote, coins, dec["les_coupes"])
    base.update({"laile": aile, "le_decoupage": dec, "les_sous_boucles_declarees": sbs})
    if dec["combien_de_sous_boucles"] < 2:
        return {**base, "decidable": True, "le_verdict": le_verdict_des_coupes(dec["combien_de_sous_boucles"], [], k1)}
    bandes = les_bandes_des_coupes(dec, k1)
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
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle des coupes dérivées"}
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
    pas.update(les_pas_des_bandes(relues, bandes))
    par_sb = []
    for sb in sbs:
        a = analyser(pas, sb, par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"la sous-boucle {sb} : {a.get('raison')}",
                    "la_reproduction": rep}
        entre = sb[:2] if cote in ("droite", "gauche") else sb[2:]
        par_sb.append({"entre": [int(x) for x in entre], "les_coins": sb, **a})
    emb = lemboitement(par_sb, par234["par_aile"][cote], cote)
    if not emb.get("decidable"):
        return {**base, "decidable": False, "raison": emb.get("raison"), "la_reproduction": rep,
                "lemboitement": emb}
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_sous_boucle": par_sb, "lemboitement": emb, "le_profil": le_profil(par_sb, k1),
            "le_verdict": le_verdict_des_coupes(dec["combien_de_sous_boucles"], par_sb, k1)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"aile : {r['laile']}")
    d = r["le_decoupage"]
    print(f"découpage : {d['combien_de_sous_boucles']} sous-boucles, plus grand écart {d['le_plus_grand_ecart']}, "
          f"coupes {d['les_coupes']}")
    if "par_sous_boucle" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        print(f"emboîtement : {r['lemboitement']}")
        for sb in r["par_sous_boucle"]:
            for k, x in sb["par_largeur"].items():
                if not x["fermable"]:
                    print(f"  {sb['entre']} · {k} lignes · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
                    continue
                print(f"  {sb['entre']} · {k} lignes · L {x['la_fermeture_en_voxels']} · σ "
                      f"{x['la_dispersion_du_pas_en_voxels']} · nul {x['le_nul']} · trous {x['les_trous']} · côtés "
                      f"{x['les_cotes']}")
        print(f"profil : {r['le_profil']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import itertools
    import tempfile

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

    # les coupes : contre une énumération de tous les découpages, sur des empreintes au hasard
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
        sens, lo, hi, de, a = le_travers(cote, coins)
        dedans = [y for y in range(lo + 1, hi) if _tient(A_, sens, y, de, a, k)]
        best, kb = None, None
        for n in range(len(dedans) + 1):
            for sous in itertools.combinations(dedans, n):
                cs = [lo, *sous, hi]
                ecarts = [cs[i + 1] - cs[i] for i in range(len(cs) - 1)]
                if min(ecarts) < k:
                    continue
                cle = (len(ecarts), -max(ecarts), [-x for x in cs])
                if kb is None or cle > kb:
                    best, kb = cs, cle
        return best
    g = np.random.default_rng(235)
    accord, vus = [], 0
    for i in range(10):
        Ar = np.ones((30, 18), dtype=bool)
        for _ in range(int(g.integers(1, 5))):
            y, x = int(g.integers(0, 30)), int(g.integers(0, 18))
            Ar[max(0, y - int(g.integers(0, 3))):y + 1, max(0, x - int(g.integers(0, 3))):x + 1] = False
        cote = ("droite", "haut")[i % 2]
        co = [3, 26, 4, 13] if cote == "droite" else [4, 13, 3, 26]
        A_ = Ar if cote == "droite" else Ar.T.copy()
        d_ = _sur(les_coupes, A_, co, cote, 3)
        b_ = _brute(A_, co, cote, 3)
        accord.append(d_.get("les_coupes") == b_)
        vus += len(b_) - 2
    v("★★★★ les coupes sont celles d'une énumération de tous les découpages, sur dix empreintes au hasard",
      all(accord) and vus > 10, f"{accord} {vus}")
    Ap = np.ones((396, 285), dtype=bool)
    dp = _sur(les_coupes, Ap, [26, 223, 243, 260], "droite", 9)
    v("★★★★ sur une grille pleine, 197 coutures se coupent en 21 sous-boucles de 9 et de 10, les 9 d'abord",
      _ok(lambda: dp["combien_de_sous_boucles"] == 21 and dp["le_plus_grand_ecart"] == 10
          and dp["les_coupes"] == [26 + 9 * j for j in range(14)] + [143 + 10 * j for j in range(1, 9)]), str(dp))
    v("★★★★ les coupes d'une aile de droite sont des rangées tendues entre ses deux colonnes",
      _ok(lambda: dp["le_sens"] == "rangees" and dp["les_bornes"] == [243, 260]
          and les_sous_boucles("droite", [26, 223, 243, 260], dp["les_coupes"])[3] == [53, 62, 243, 260]))
    dh = _sur(les_coupes, Ap.T.copy(), [243, 260, 26, 223], "haut", 9)
    v("★★★ les coupes d'une aile du haut sont des colonnes tendues entre ses deux rangées",
      _ok(lambda: dh["le_sens"] == "colonnes" and dh["les_bornes"] == [243, 260] and dh["les_coupes"] == dp["les_coupes"]
          and les_sous_boucles("haut", [243, 260, 26, 223], dh["les_coupes"])[3] == [243, 260, 53, 62]))
    Ah = Ap.copy()
    Ah[100:103, 250] = False
    dtr = _sur(les_coupes, Ah, [26, 223, 243, 260], "droite", 9)
    v("★★★★ une coupe dont une ligne perd un chunk ne tient pas : aucune coupe ne passe par le trou",
      _ok(lambda: all(abs(c - 101) > 5 for c in dtr["les_coupes"]) and dtr["combien_de_sous_boucles"] < 21), str(dtr))
    dc = _sur(les_coupes, Ap, [14, 26, 32, 81], "droite", 9)
    v("★★★★ une aile trop courte pour deux sous-boucles ne se coupe pas : ses deux bouts seuls",
      _ok(lambda: dc["les_coupes"] == [14, 26] and dc["combien_de_sous_boucles"] == 1), str(dc))
    bd = _sur(les_bandes_des_coupes, dp, 9)
    v("★★★★ seules les coupes intérieures se lisent, neuf lignes chacune, au format des bandes de 234",
      _ok(lambda: len(bd) == 20 and bd[0]["cle"] == "rangees_35_243_260" and bd[0]["les_lignes"] == list(range(31, 40))
          and all(b["de"] == 243 and b["a"] == 260 for b in bd)))

    # l'aile la plus lâche
    def _p234(Ls, ferment):  # noqa: E306
        return {"verdict": {"la_largeur_jugee": 9, "les_ailes_qui_ferment": ferment},
                "par_aile": {c: {"par_largeur": {"9": {"la_fermeture_en_voxels": L}}} for c, L in Ls.items()},
                "ailes": {c: {"les_coins": [0, 20, 0, 20]} for c in Ls}}
    lp = laile_la_plus_lache(_p234({"haut": -2.0, "droite": -35.7, "gauche": 6.9}, ["droite", "gauche", "haut"]))
    v("★★★★ l'aile coupée est la plus lâche de celles qui ferment, par sa fermeture en valeur absolue",
      lp is not None and lp["le_cote"] == "droite" and lp["la_fermeture_en_voxels"] == -35.7)
    v("★★★ une aile qui ne ferme pas n'est jamais la plus lâche",
      laile_la_plus_lache(_p234({"haut": -2.0, "droite": -50.0}, ["haut"]))["le_cote"] == "haut")
    v("★★★ sans aile qui ferme, aucune aile n'est désignée",
      laile_la_plus_lache(_p234({"haut": -50.0}, [])) is None)

    # l'emboîtement, le profil et le verdict, sur des sous-boucles fabriquées
    def _x(L, ferme=True, fermable=True, trous=()):  # noqa: E306
        return {"fermable": fermable, "la_fermeture_en_voxels": L, "sous_le_demi_pli": ferme, "les_trous": list(trous)}

    def _sb(e, L, **kw):  # noqa: E306
        return {"entre": list(e), "par_largeur": {"9": _x(L, **kw)}}
    sbf = [_sb((0, 9), -1.25), _sb((9, 18), -30.5), _sb((18, 27), 2.0)]
    em = lemboitement(sbf, {"par_largeur": {"9": _x(-29.75)}}, "droite")
    v("★★★★ la somme des sous-boucles retombe sur la fermeture de l'aile : l'emboîtement passe",
      em.get("decidable") and em["par_largeur"]["9"]["jugeable"] and em["combien_de_largeurs_jugees"] == 1)
    v("★★★★ une somme qui ne retombe pas sur l'aile est refusée, par sa raison",
      "l'emboîtement ne retombe pas" in str(lemboitement(sbf, {"par_largeur": {"9": _x(-29.6)}}, "droite").get("raison")))
    v("★★★ l'arrondi de chaque sous-boucle est toléré, pas davantage",
      lemboitement(sbf, {"par_largeur": {"9": _x(-29.7501)}}, "droite").get("decidable")
      and not lemboitement(sbf, {"par_largeur": {"9": _x(-29.751)}}, "droite").get("decidable"))
    tl, tc = [{"le_cote": "droite", "le_debut": 3, "la_longueur": 1}], [{"le_cote": "haut", "le_debut": 3,
                                                                           "la_longueur": 1}]
    v("★★★★ une largeur où l'aile ou une sous-boucle a un trou le long d'un long côté n'est pas jugée",
      lemboitement(sbf, {"par_largeur": {"9": _x(0.0, trous=tl)}}, "droite").get("decidable")
      and not lemboitement(sbf, {"par_largeur": {"9": _x(0.0, trous=tl)}}, "droite")["par_largeur"]["9"]["jugeable"]
      and lemboitement([_sb((0, 9), 0.0, trous=tl)], {"par_largeur": {"9": _x(5.0)}}, "droite").get("decidable"))
    v("★★★★ un trou sur une coupe n'empêche pas de juger : il s'annule entre les deux sous-boucles",
      not lemboitement([_sb((0, 9), 0.0, trous=tc)], {"par_largeur": {"9": _x(5.0)}}, "droite").get("decidable")
      and lemboitement([_sb((0, 9), 0.0, trous=tc)], {"par_largeur": {"9": _x(5.0)}}, "haut").get("decidable"))
    v("★★★ le profil cumule les fermetures coupe après coupe",
      le_profil(sbf, 9) == [{"la_coupe": 9, "le_cumul_en_voxels": -1.25}, {"la_coupe": 18, "le_cumul_en_voxels": -31.75},
                            {"la_coupe": 27, "le_cumul_en_voxels": -29.75}])
    v("★★★ le profil s'arrête à la première sous-boucle ouverte",
      le_profil([sbf[0], _sb((9, 18), 0.0, fermable=False), sbf[2]], 9) == [{"la_coupe": 9, "le_cumul_en_voxels": -1.25}])
    vc = le_verdict_des_coupes(3, sbf, 9)
    v("★★★★ aucune sous-boucle au demi-feuillet : l'écart se cumule, et la plus grande est nommée",
      vc["lecart_se_cumule"] and not vc["laile_change_de_spire"] and "SE CUMULE" in vc["ce_qui_reste_a_mesurer"]
      and vc["la_plus_grande"] == {"entre": [9, 18], "la_fermeture_en_voxels": -30.5})
    vl = le_verdict_des_coupes(3, [sbf[0], _sb((9, 18), -40.0, ferme=False), sbf[2]], 9)
    v("★★★★ une sous-boucle au demi-feuillet : l'aile change de spire entre ces deux coupes",
      vl["laile_change_de_spire"] and vl["les_sous_boucles_a_un_demi_feuillet"] == [[9, 18]]
      and "CHANGE DE SPIRE" in vl["ce_qui_reste_a_mesurer"])
    vo = le_verdict_des_coupes(3, [_sb((0, 9), 0.0, fermable=False), _sb((9, 18), -40.0, ferme=False), sbf[2]], 9)
    v("★★★★ une sous-boucle ouverte prime sur une sous-boucle au demi-feuillet",
      vo["les_sous_boucles_ouvertes"] == [[0, 9]] and not vo["laile_change_de_spire"] and not vo["lecart_se_cumule"]
      and "OUVERTE" in vo["ce_qui_reste_a_mesurer"])
    v0 = le_verdict_des_coupes(1, [], 9)
    v("★★★★ sans coupe, rien ne se juge : l'aile ne se découpe pas",
      not v0["lecart_se_cumule"] and not v0["laile_change_de_spire"] and "NE SE DÉCOUPE PAS" in v0["ce_qui_reste_a_mesurer"])
    v("★★★ les quatre issues sont distinctes",
      len({_ce_qui_reste(a, b, c) for a, b, c in itertools.product((True, False), repeat=3)}) == 4)

    # la mesure, sur des publications réelles, une empreinte fabriquée et une lecture qui retombe
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    q234 = ce_que_234_a_publie()
    v("★★★★ ce que 234 publie se relit : ses ailes, leurs neuf bandes et leur analyse",
      q234.get("decidable") and len(q234["bandes"]) == 9 and sorted(q234["publiees"]) == sorted(b["cle"] for b in
                                                                                             q234["bandes"]),
      str(q234.get("raison")))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False  # aucune aile en haut
    Af[200:395, 250:281] = False  # l'aile de droite s'arrête à la rangée 195

    def _sur_lempreinte(A_):  # noqa: E306
        q2, q3 = copy.deepcopy(q232), copy.deepcopy(q233)
        for q in (q2, q3):
            for bb in q["bandes"]:
                for l_ in bb["les_lignes"]:
                    q["publiees"][bb["cle"]]["les_lectures"][str(l_)]["refuses"][ABSENT] = \
                        les_absents_dune_ligne(A_, bb["le_sens"], l_, bb["de"], bb["a"])
        q3["presence"] = {"decidable": True, "la_grille": [gy, gx], "les_pages": 1,
                          "les_rangees": ["".join("1" if x else "0" for x in r) for r in A_]}
        return q2, q3
    q232f, q233f = _sur_lempreinte(Af)
    src0 = les_sources_de_234(p219, p223, p224, q232f, q233f)

    def _champ(f, r, c):  # noqa: E306
        return round(((r * 7919 + c * 104729 + (0 if f == "h" else 31)) % 1000) / 1000.0 * 0.6 - 0.3, 4)

    def _derive(f, r, c):  # noqa: E306
        # la colonne extérieure de droite dérive, sur chaque couture verticale de ses lignes quelle que soit la bande
        # qui la lit ; celle de gauche dérive assez pour que son aile ne ferme pas
        return _champ(f, r, c) + (-0.05 if f == "v" and c >= 272 else 0.0) + (0.3 if f == "v" and c <= 11 else 0.0)

    def _saute(f, r, c):  # noqa: E306
        # un saut sur la seule couture 110 de la colonne extérieure de droite, compensé par une dérive ; celle de
        # gauche dérive assez pour que son aile ne ferme pas
        x = _champ(f, r, c)
        if f == "v" and c >= 272:
            x += -0.15 + (50.0 if r == 110 else 0.0)
        if f == "v" and c <= 11:
            x += 0.3
        return x

    def _fabrique(bd, src, champ=_champ):  # noqa: E306
        # ⚠ un pas qu'une source publiée lit est celui de la source ; le champ ne donne que le reste, le même pour
        # toutes les bandes qui lisent une même couture
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

    def _publie_234(lire_):  # noqa: E306
        m_ = _sur(mesurer_234, None, p219, p223, p224, p225, q225, q232f, q233f, lire_, 49)
        with tempfile.TemporaryDirectory() as tmp:
            pj = Path(tmp) / "m234.json"
            pj.write_text(json.dumps(m_, ensure_ascii=False))
            return m_, ce_que_234_a_publie(pj)

    # `234` sur l'empreinte fabriquée : la colonne extérieure de droite dérive, l'aile de droite est la plus lâche
    m234, q234f = _publie_234(lambda bd: _fabrique(bd, src0, _derive))
    v("★★★★ 234 rejoué sur l'empreinte fabriquée : seule l'aile de droite ferme, c'est la plus lâche",
      _ok(lambda: m234["le_verdict"]["les_ailes_qui_ferment"] == ["droite"]
          and m234["les_ailes"]["droite"]["les_coins"] == [26, 195, 243, 276]
          and laile_la_plus_lache(q234f)["le_cote"] == "droite"),
      str(m234.get("raison") or {c: (x.get("les_coins"), {k_: y.get("la_fermeture_en_voxels") for k_, y in
                                                         (x.get("par_largeur") or {}).items()})
                                 for c, x in (m234.get("par_aile") or {}).items()}))
    src1 = les_sources_de_235(p219, p223, p224, q232f, q233f, q234f) if q234f.get("decidable") else {}
    lus = []

    def _lit(bd):  # noqa: E306
        lus.append(bd)
        return _fabrique(bd, src1, _derive)
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _lit, 49)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_sous_boucle" in m, str(m.get("raison")))
    v("★★★★ l'aile de droite de 234 est découpée, et ses coupes sont celles dérivées de l'empreinte",
      _ok(lambda: m["laile"]["le_cote"] == "droite" and m["le_decoupage"] == les_coupes(Af, [26, 195, 243, 276],
                                                                                         "droite", 9)
          and m["le_decoupage"]["combien_de_sous_boucles"] == 18), str(m.get("le_decoupage")))
    v("★★★★ seules les coupes intérieures sont lues, aucun bout ni long côté",
      _ok(lambda: [b["cle"] for b in lus] == [b["cle"] for b in les_bandes_des_coupes(m["le_decoupage"], 9)]
          and not ({b["cle"] for b in lus} & ({b["cle"] for b in q234f["bandes"]} | {b["cle"] for b in q233f["bandes"]}))
          and len(lus) == 17), str(len(lus)))
    v("★★★★ chaque coupe est contrôlée par les bandes publiées de 233 et de 234 qu'elle croise",
      _ok(lambda: all(any(k.startswith(f"{b['cle']}×233 ") for k in m["la_reproduction"]["par_croisement"])
                      and any(k.startswith(f"{b['cle']}×234 ") for k in m["la_reproduction"]["par_croisement"])
                      for b in m["les_bandes_declarees"])), str(m.get("la_reproduction", {}).get("par_croisement")))
    v("★★★★ chaque sous-boucle est analysée sur ses quatre côtés à chaque largeur",
      _ok(lambda: len(m["par_sous_boucle"]) == 18
          and all(sorted(sb["par_largeur"], key=int) == ["3", "5", "7", "9"] for sb in m["par_sous_boucle"])
          and all(x["les_lignes_par_cote"] == {n_: int(k_) for n_ in ("haut", "droite", "bas", "gauche")}
                  for sb in m["par_sous_boucle"] for k_, x in sb["par_largeur"].items())))
    v("★★★★ l'emboîtement retombe sur la fermeture que 234 publie, à neuf lignes et aux largeurs sans trou",
      _ok(lambda: m["lemboitement"]["par_largeur"]["9"]["jugeable"] and m["lemboitement"]["combien_de_largeurs_jugees"] == 3
          and all(abs(x["la_somme_des_sous_boucles"] - x["la_fermeture_de_laile"]) <= x["la_tolerance"]
                  for x in m["lemboitement"]["par_largeur"].values() if x["jugeable"])), str(m.get("lemboitement")))

    v("★★★★ le profil finit sur la fermeture de l'aile que 234 publie",
      _ok(lambda: abs(m["le_profil"][-1]["le_cumul_en_voxels"] - m["laile"]["la_fermeture_en_voxels"])
          <= L_ARRONDI * 19 and len(m["le_profil"]) == 18 and m["le_profil"][-1]["la_coupe"] == 195),
      str(m.get("le_profil")))
    v("★★★★ la règle de 225 est appliquée, le profil et le verdict sont ceux des sous-boucles",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["le_profil"] == le_profil(m["par_sous_boucle"], 9)
          and m["le_verdict"] == le_verdict_des_coupes(18, m["par_sous_boucle"], 9)))

    # un saut sur une seule couture de la colonne extérieure, compensé par une dérive : l'aile ferme encore
    m234s, q234s = _publie_234(lambda bd: _fabrique(bd, src0, _saute))
    src_s = les_sources_de_235(p219, p223, p224, q232f, q233f, q234s) if q234s.get("decidable") else {}
    ms = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234s, lambda bd: _fabrique(bd, src_s, _saute),
              49)
    v("★★★★ un saut d'un demi-feuillet sur une seule couture se localise entre les deux coupes qui l'entourent",
      _ok(lambda: m234s["le_verdict"]["les_ailes_qui_ferment"] == ["droite"]
          and ms["le_verdict"]["laile_change_de_spire"]
          and len(ms["le_verdict"]["les_sous_boucles_a_un_demi_feuillet"]) == 1
          and ms["le_verdict"]["les_sous_boucles_a_un_demi_feuillet"][0][0] <= 110
          < ms["le_verdict"]["les_sous_boucles_a_un_demi_feuillet"][0][1]),
      str(ms.get("raison") or ms.get("le_verdict") or m234s.get("le_verdict")))

    q234e = copy.deepcopy(q234f)
    if q234e.get("decidable"):
        q234e["par_aile"]["droite"]["par_largeur"]["9"]["la_fermeture_en_voxels"] += 1.0
    v("★★★★ des sous-boucles qui ne somment pas à la fermeture publiée de l'aile sont refusées, par leur raison",
      "l'emboîtement ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234e,
                                                  lambda bd: _fabrique(bd, src1, _derive), 49).get("raison")))

    def _menteuse(bd):  # noqa: E306
        x = _fabrique(bd, src1, _derive)
        x["les_lectures"][bd["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _menteuse, 49)
                              .get("raison")))

    def _decale(bd):  # noqa: E306
        x = _fabrique(bd, src1, _derive)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une coupe qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234f, _decale, 49)
                                  .get("raison")))
    v("★★★★ une présence qui ne retombe pas sur les bandes de 234 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f,
                                   {**q234f, "publiees": q234["publiees"], "bandes": q234["bandes"]}, _lit, 49)
                              .get("raison")))
    q234n = copy.deepcopy(q234f)
    if q234n.get("decidable"):
        q234n["verdict"]["les_ailes_qui_ferment"] = []
    lus_n = []
    v("★★★★ sans aile qui ferme dans 234, rien n'est découpé ni lu",
      "rien à découper" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q234n,
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
        dec = les_coupes(A, aile["les_coins"], aile["le_cote"], k1)
        print(f"aile : {aile}", flush=True)
        print(f"découpage : {dec}", flush=True)
        if dec["combien_de_sous_boucles"] < 2:
            return 0
        bandes = les_bandes_des_coupes(dec, k1)
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
