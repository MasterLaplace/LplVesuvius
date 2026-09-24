"""Le segment au-delà du plus grand rectangle se relie-t-il au rectangle sur la même spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE, ET AVANT QUE LES AILES NE SOIENT
DÉRIVÉES. Ce qui était vu avant d'écrire : ce que `233` publie, la présence listée et la figure qui la montre.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P79`. `233` a listé le dépôt : le segment porte des chunks des
rangées 5 à 394 et des colonnes 0 à 283, et le plus grand rectangle dont les quatre bandes de neuf lignes y
tiennent, des rangées 26 à 384 et des colonnes 22 à 243, ferme à −11,8449 voxels, sous le demi-feuillet.
Entre les bords de ce rectangle et ceux de l'empreinte, aucune boucle ne passe. Ce segment-là se relie-t-il
au rectangle sur la même spire ?

## Les ailes, dérivées

Une AILE est un rectangle qui partage avec le rectangle de `233` une portion de l'un de ses côtés et
s'étend vers l'extérieur. Ses trois autres bandes TIENNENT au sens de `233` : à chaque couture, leurs neuf
lignes ont leurs deux chunks dans le dépôt. ⚠⚠ Sa bande extérieure ne partage aucune ligne avec la bande
qu'elle prolonge, et ses deux bandes de travers aucune entre elles : elles sont à neuf lignes au moins l'une
de l'autre, sinon la boucle se fermerait sur les mêmes chunks. De chaque côté, l'aile est la plus grande :
la plus grande aire, qui est ce qu'elle relie, puis le plus long chemin, puis le plus petit début, puis la
bande extérieure la plus proche. Un côté où aucune aile ne tient est déclaré tel, jamais forcé. Le code
dérive les ailes de la présence que `233` publie, et rien d'autre ; elles ne sont pas choisies.

## Ce qui se lit, et ce qui le contrôle

Les trois bandes neuves de chaque aile, neuf lignes chacune, par le lecteur de `224`. ⚠⚠ La bande qu'une aile
partage avec le rectangle n'est pas relue : ses pas sont ceux que `233` publie. ⚠⚠⚠ Partout où une bande
neuve croise une bande publiée — `219`, `223`, `224`, `232`, `233` —, les pas relus retombent à l'arrondi,
sur les mêmes coutures, sinon refus. ⚠⚠ Chaque bande neuve est contrôlée sur au moins une couture : par une
bande publiée qu'elle croise, ou, faute de mieux, par une bande neuve déjà contrôlée qu'elle croise — sinon
refus. ⚠⚠ Les chunks que la lecture compte absents du dépôt sont ceux que la présence dit absents.

## Ce qui se mesure

L'instrument de `228` sur chaque aile, à chaque largeur de l'échelle de `218`, avec la garde de `232` : un
trou de majorité se franchit par le maillage, et seulement jusqu'aux 17 coutures que `225` a essayées.

LA COUVERTURE : un chunk est ENTOURÉ par une boucle quand il tombe entre ses bandes, bandes comprises. La
part de l'empreinte entourée se compte pour le rectangle seul, pour le rectangle et les ailes qui ferment, et
— déclarée avant toute lecture — pour le rectangle et toutes les ailes.

## Les issues, exclusives, jugées à neuf lignes

- aucune aile ne tient, d'aucun côté : il n'y a rien à relier, et rien n'est lu ;
- une aile garde un trou plus long que ceux que `225` a franchis : elle reste ouverte ;
- une aile atteint le demi-feuillet : elle arrive sur une autre spire que le rectangle ;
- toutes restent dessous : chaque aile arrive sur la même spire que le rectangle.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce qui reste au-delà des bandes extérieures des ailes et dans les
coins ; ce que porte l'intérieur d'une boucle ; ni lequel des deux chemins est sur la bonne spire.

Usage :
    uv run python src/nappe/le_segment_au_dela_du_rectangle_se_relie_t_il.py --verifier
    uv run python src/nappe/le_segment_au_dela_du_rectangle_se_relie_t_il.py --lire <lecture.json>
    uv run python src/nappe/le_segment_au_dela_du_rectangle_se_relie_t_il.py --depuis <lecture.json> \\
        --json docs/mesures/le_segment_au_dela_du_rectangle_se_relie_t_il.json
"""
from __future__ import annotations

import argparse
import bisect
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
                                                                            les_bandes_a_lire,
                                                                            les_pas_des_bandes)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (LA_TOLERANCE_DE_REPRODUCTION,  # noqa: E402
                                                          la_reproduction_croisee, le_domaine,
                                                          les_pas_dune_bande)
from ou_sarrete_le_segment import (ABSENT, ce_que_232_a_publie,  # noqa: E402
                                   la_grille_de_presence, la_presence_retombe, lempreinte,
                                   les_absents_dune_ligne, les_bandes_qui_tiennent, les_sources)
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import la_majorite, les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_233_A_PUBLIE = MESURES / "ou_sarrete_le_segment.json"
LES_COTES = ("haut", "droite", "bas", "gauche")

LA_QUESTION_DECLAREE = ("le segment au-delà du plus grand rectangle se relie-t-il au rectangle sur la même "
                        "spire ?")
LA_MESURE_DECLAREE = ("de chaque côté du rectangle de `233`, la plus grande aile dont les trois bandes neuves de "
                      "neuf lignes tiennent dans le dépôt, et l'instrument de `228` sur chaque aile")


# ─────────────────────────────── ce que `233` publie ───────────────────────────────

def ce_que_233_a_publie(chemin: Path = CE_QUE_233_A_PUBLIE) -> dict:
    """La présence listée, le rectangle, ses quatre bandes relues et sa fermeture, tels que `233` les publie."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    rect = d.get("le_rectangle") or {}
    if (not d.get("decidable") or not (d.get("la_presence") or {}).get("decidable") or not rect.get("les_coins")
            or not d.get("les_bandes") or not d.get("les_bandes_declarees") or not d.get("le_verdict")):
        return {"decidable": False, "raison": "`233` ne publie pas sa présence, son rectangle ou ses bandes"}
    v = d["le_verdict"]
    k1 = str(v.get("la_largeur_jugee"))
    return {"decidable": True, "presence": d["la_presence"], "coins": [int(x) for x in rect["les_coins"]],
            "bandes": d["les_bandes_declarees"], "publiees": d["les_bandes"],
            "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()},
            "ferme": bool(v.get("le_segment_entier_se_ferme")) and not bool(v.get("le_segment_entier_reste_ouvert")),
            "la_fermeture": ((d.get("par_largeur") or {}).get(k1) or {}).get("la_fermeture_en_voxels")}


# ─────────────────────────────── les ailes, dérivées ───────────────────────────────

def les_tenues(A: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Les coutures où une bande ne tient pas, cumulées : `PR[r, j]` pour la bande de rangées centrée en `r`
    sur les coutures `[0, j)`, `PC[i, c]` pour la bande de colonnes centrée en `c` sur `[0, i)`."""
    rangee, colonne = les_bandes_qui_tiennent(A, k)
    PR = np.hstack([np.zeros((rangee.shape[0], 1), dtype=int), np.cumsum(~rangee, axis=1)])
    PC = np.vstack([np.zeros((1, colonne.shape[1]), dtype=int), np.cumsum(~colonne, axis=0)])
    return PR, PC


def tient(PR: np.ndarray, PC: np.ndarray, sens: str, centre: int, de: int, a: int) -> bool:
    """La bande `(sens, centre)` tient-elle à chaque couture de `[de, a)` ?"""
    if int(a) <= int(de):
        return False
    if sens == "rangees":
        return int(PR[int(centre), int(a)] - PR[int(centre), int(de)]) == 0
    return int(PC[int(a), int(centre)] - PC[int(de), int(centre)]) == 0


def les_coins_de_laile(cote: str, coins, debut: int, fin: int, dehors: int) -> list[int]:
    """Les coins `(r0, r1, c0, c1)` d'une aile, depuis sa portion `[debut, fin]` du côté et sa bande extérieure."""
    r0, r1, c0, c1 = [int(x) for x in coins]
    return {"droite": [debut, fin, c1, dehors], "gauche": [debut, fin, dehors, c0],
            "haut": [dehors, r0, debut, fin], "bas": [r1, dehors, debut, fin]}[cote]


def la_bande_interieure(cote: str, coins) -> tuple[str, int]:
    """La bande du rectangle que l'aile partage : elle n'est pas relue."""
    r0, r1, c0, c1 = [int(x) for x in coins]
    return {"droite": ("colonnes", c1), "gauche": ("colonnes", c0), "haut": ("rangees", r0),
            "bas": ("rangees", r1)}[cote]


def laile(A: np.ndarray, coins, cote: str, k: int, tenues=None) -> dict:
    """La plus grande aile d'un côté : la plus grande aire, puis le plus long chemin, puis le plus petit début,
    puis la bande extérieure la plus proche ; ou aucune.

    ⚠⚠ La bande extérieure est à `k` lignes au moins de la bande intérieure, les deux bandes de travers à `k`
    lignes au moins l'une de l'autre : aucune ligne n'est partagée.
    """
    A = np.asarray(A, dtype=bool)
    gy, gx = A.shape
    h = int(k) // 2
    r0, r1, c0, c1 = [int(x) for x in coins]
    PR, PC = tenues if tenues is not None else les_tenues(A, k)
    if cote in ("droite", "gauche"):
        dedans, lo, hi = (c1 if cote == "droite" else c0), r0, r1
        dehors_ = range(c1 + k, gx - h) if cote == "droite" else range(h, c0 - k + 1)
        travers, exterieure = "rangees", "colonnes"
    else:
        dedans, lo, hi = (r0 if cote == "haut" else r1), c0, c1
        dehors_ = range(h, r0 - k + 1) if cote == "haut" else range(r1 + k, gy - h)
        travers, exterieure = "colonnes", "rangees"
    meilleur, cle_m = None, None
    for x in dehors_:
        a_, b_ = min(dedans, x), max(dedans, x)
        ys = [y for y in range(lo, hi + 1) if tient(PR, PC, travers, y, a_, b_)]
        for ya in ys:
            j0 = bisect.bisect_left(ys, ya + int(k))
            if j0 >= len(ys) or not tient(PR, PC, exterieure, x, ya, ys[j0]):
                continue
            g, d = j0, len(ys) - 1
            while g < d:
                m = (g + d + 1) // 2
                if tient(PR, PC, exterieure, x, ya, ys[m]):
                    g = m
                else:
                    d = m - 1
            yb = ys[g]
            larg = b_ - a_
            cle = ((yb - ya) * larg, (yb - ya) + larg, -ya, -larg)
            if cle_m is None or cle > cle_m:
                meilleur, cle_m = (ya, yb, x), cle
    if meilleur is None:
        return {"le_cote": cote, "les_coins": None, "laire": 0, "le_chemin": 0}
    ya, yb, x = meilleur
    return {"le_cote": cote, "les_coins": les_coins_de_laile(cote, coins, ya, yb, x), "laire": int(cle_m[0]),
            "le_chemin": int(cle_m[1])}


def les_ailes(A: np.ndarray, coins, k: int) -> dict:
    t = les_tenues(A, k)
    return {c: laile(A, coins, c, k, t) for c in LES_COTES}


def les_bandes_de_laile(aile: dict, coins, k: int) -> list[dict]:
    """Les trois bandes neuves d'une aile — la bande qu'elle partage avec le rectangle n'en est pas."""
    interieure = la_bande_interieure(aile["le_cote"], coins)
    return [{**b, "cle": f"{b['le_sens']}_{b['le_centre']}_{b['de']}_{b['a']}"}
            for b in les_bandes_a_lire(aile["les_coins"], k) if (b["le_sens"], int(b["le_centre"])) != interieure]


# ─────────────────────────────── la couverture ───────────────────────────────

def lentoure(forme, coins, k: int) -> np.ndarray:
    """Les chunks qu'une boucle entoure, bandes comprises."""
    gy, gx = [int(x) for x in forme]
    h = int(k) // 2
    r0, r1, c0, c1 = [int(x) for x in coins]
    M = np.zeros((gy, gx), dtype=bool)
    M[max(0, r0 - h):min(gy, r1 + h + 1), max(0, c0 - h):min(gx, c1 + h + 1)] = True
    return M


def la_couverture(A: np.ndarray, boucles, k: int) -> dict:
    """La part de l'empreinte que les boucles entourent : combien de chunks présents, sur combien."""
    A = np.asarray(A, dtype=bool)
    M = np.zeros(A.shape, dtype=bool)
    for c in boucles:
        M |= lentoure(A.shape, c, k)
    n, tot = int((A & M).sum()), int(A.sum())
    return {"combien": n, "sur": tot, "la_part": round(n / tot, 4) if tot else 0.0}


# ─────────────────────────────── le verdict ───────────────────────────────

def _ce_qui_reste(aucune: bool, ouverte: bool, loin: bool) -> str:
    """Les quatre issues, EXCLUSIVES, dans cet ordre de priorité."""
    if aucune:
        return "AUCUNE AILE NE TIENT AUTOUR DU PLUS GRAND RECTANGLE : IL N'Y A RIEN À RELIER"
    if ouverte:
        return "À NEUF LIGNES, UN TROU PLUS LONG QUE CEUX QUE `225` A FRANCHIS LAISSE UNE AILE OUVERTE"
    if loin:
        return "À NEUF LIGNES, UNE AILE ARRIVE À UN DEMI-FEUILLET DU PLUS GRAND RECTANGLE"
    return "À NEUF LIGNES, CHAQUE AILE ARRIVE SUR LA MÊME SPIRE QUE LE PLUS GRAND RECTANGLE"


def le_verdict_des_ailes(par_aile: dict, k1: int) -> dict:
    """Le verdict, à la plus large, depuis l'analyse de chaque aile qui tient."""
    tenues = sorted(c for c, x in par_aile.items() if x.get("les_coins"))
    ouv = sorted(c for c in tenues if par_aile[c]["le_verdict"]["le_segment_entier_reste_ouvert"])
    loin = sorted(c for c in tenues if c not in ouv and not par_aile[c]["le_verdict"]["le_segment_entier_se_ferme"])
    ferment = sorted(c for c in tenues if c not in ouv and c not in loin)
    return {"la_largeur_jugee": int(k1), "les_ailes_qui_tiennent": tenues, "les_ailes_ouvertes": ouv,
            "les_ailes_a_un_demi_feuillet": loin, "les_ailes_qui_ferment": ferment,
            "chaque_aile_se_ferme": bool(tenues) and not ouv and not loin,
            "ce_qui_reste_a_mesurer": _ce_qui_reste(not tenues, bool(ouv), bool(loin))}


# ─────────────────────────────── la mesure ───────────────────────────────

def les_sources_de_234(par219: dict, par223: dict, par224: dict, par232: dict, par233: dict) -> dict:
    """Ce qui contrôle une bande neuve : `219`, `223`, `224`, `232`, et les quatre bandes de `233`."""
    out = les_sources(par219, par223, par224, par232)
    for b in par233["bandes"]:
        out[f"233 {b['cle']}"] = {"domaine": le_domaine(b["le_sens"], b["les_lignes"], b["de"], b["a"]),
                                  "pas": les_pas_dune_bande(par233["relues"][b["cle"]])}
    return out


def la_reproduction_en_chaine(nouvelles: dict, sources: dict,
                               tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """La reproduction croisée de `227`, bande par bande : une bande neuve qui ne croise aucune source publiée
    est contrôlée par une bande neuve déjà contrôlée qu'elle croise. ⚠⚠ Jamais par une bande qui ne l'est pas :
    sinon deux bandes mal placées se contrôleraient l'une l'autre."""
    reste, controlees, ordre = sorted(nouvelles), [], []
    par, n, ecart = {}, 0, 0.0
    while reste:
        avance = False
        for b in list(reste):
            src = {**sources, **{f"234 {c}": nouvelles[c] for c in controlees}}
            r = la_reproduction_croisee({b: nouvelles[b]}, src, tolerance)
            if not r.get("decidable"):
                if "ne croise aucune couture" not in str(r.get("raison")):
                    return r
                continue
            reste.remove(b)
            controlees.append(b)
            ordre.append(b)
            avance = True
            par.update(r["par_croisement"])
            n += int(r["combien_de_coutures_relues"])
            ecart = max(ecart, float(r["lecart_le_plus_grand"]))
        if not avance:
            return {"decidable": False,
                    "raison": f"la bande {reste[0]} ne croise aucune couture publiée ni lue et contrôlée"}
    return {"decidable": True, "combien_de_coutures_relues": n, "par_croisement": par,
            "lecart_le_plus_grand": round(ecart, 6), "la_tolerance": float(tolerance), "lordre_du_controle": ordre}


def les_pas_de_laile(aile: dict, coins, bandes_neuves, relues: dict, par233: dict) -> dict:
    """Les pas des quatre côtés d'une aile : trois bandes lues ici, et celle de `233` qu'elle partage."""
    interieure = la_bande_interieure(aile["le_cote"], coins)
    b233 = next(b for b in par233["bandes"] if (b["le_sens"], int(b["le_centre"])) == interieure)
    pas = les_pas_des_bandes(par233["relues"], [b233])
    pas.update(les_pas_des_bandes(relues, bandes_neuves))
    return pas


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, lire=None, tirages: int | None = None) -> dict:
    """Les ailes dérivées de la présence de `233`, la lecture de leurs bandes puis l'analyse — ou rejouées."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    if not par233["ferme"]:
        return {**base, "decidable": False, "raison": "le rectangle de `233` ne ferme pas : il n'y a rien à quoi relier"}
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    for nom, par in (("232", par232), ("233", par233)):
        c_ = la_presence_retombe(A, par["bandes"], par["publiees"])
        base[f"la_presence_contre_{nom}"] = c_
        if not c_.get("decidable"):
            return {**base, "decidable": False, "raison": c_.get("raison")}
    k1 = les_largeurs()[-1]
    coins = par233["coins"]
    ailes = les_ailes(A, coins, k1)
    tenues = [c for c in LES_COTES if ailes[c]["les_coins"]]
    base.update({"lempreinte": lempreinte(A),
                 "le_rectangle_de_233": {"les_coins": coins, "la_fermeture_en_voxels": par233["la_fermeture"]},
                 "les_ailes": ailes,
                 "la_couverture_declaree": {
                     "par_le_rectangle": la_couverture(A, [coins], k1),
                     "par_le_rectangle_et_toutes_les_ailes": la_couverture(
                         A, [coins] + [ailes[c]["les_coins"] for c in tenues], k1)}})
    if not tenues:
        return {**base, "decidable": True, "le_verdict": le_verdict_des_ailes(ailes, k1)}
    bandes = [b for c in tenues for b in les_bandes_de_laile(ailes[c], coins, k1)]
    plus_long = max(pub225["les_longueurs_essayees"])
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    if depuis is not None:
        lecture = json.loads(Path(depuis).read_text())
        lu = {"decidable": True, "les_bandes": lecture.get("les_bandes") or {}}
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
    rep = la_reproduction_en_chaine(nouvelles, les_sources_de_234(par219, par223, par224, par232, par233))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    par_aile = {}
    for c in LES_COTES:
        if not ailes[c]["les_coins"]:
            par_aile[c] = {"les_coins": None}
            continue
        neuves = [b for b in bandes if b in les_bandes_de_laile(ailes[c], coins, k1)]
        a = analyser(les_pas_de_laile(ailes[c], coins, neuves, relues, par233), ailes[c]["les_coins"],
                     par225["la_regle"], plus_long, g, t_)
        if not a.get("decidable"):
            return {**base, "decidable": False, "raison": f"l'aile {c} : {a.get('raison')}", "la_reproduction": rep}
        par_aile[c] = {"les_coins": ailes[c]["les_coins"], **a}
    v = le_verdict_des_ailes(par_aile, k1)
    ferment = [ailes[c]["les_coins"] for c in v["les_ailes_qui_ferment"]]
    return {**base, "decidable": True, "la_reproduction": rep, "la_regle_appliquee": par225["la_regle"],
            "par_aile": par_aile, "le_verdict": v,
            "la_couverture": {"par_le_rectangle_et_les_ailes_qui_ferment": la_couverture(A, [coins] + ferment, k1)}}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"empreinte : {r['lempreinte']}")
    print(f"rectangle de 233 : {r['le_rectangle_de_233']}")
    for c, x in r["les_ailes"].items():
        print(f"  aile {c} : {x}")
    print(f"couverture déclarée : {r['la_couverture_declaree']}")
    if "par_aile" in r:
        rp = r["la_reproduction"]
        print(f"contre la lecture : {r['la_presence_contre_la_lecture']}")
        print(f"reproduction : {rp['combien_de_coutures_relues']} coutures {rp['par_croisement']}, écart "
              f"{rp['lecart_le_plus_grand']}")
        for c, a in r["par_aile"].items():
            if not a.get("les_coins"):
                print(f"  {c} · aucune aile")
                continue
            for k, x in a["par_largeur"].items():
                if not x["fermable"]:
                    print(f"  {c} · {k} lignes · OUVERT · trous trop longs {x['les_trous_trop_longs']}")
                    continue
                print(f"  {c} · {k} lignes · L {x['la_fermeture_en_voxels']} · σ {x['la_dispersion_du_pas_en_voxels']}"
                      f" · nul {x['le_nul']} · trous {x['les_trous']} · côtés {x['les_cotes']}")
        print(f"couverture : {r['la_couverture']}")
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

    # les ailes : contre une recherche exhaustive écrite autrement, sur des empreintes au hasard
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
        gy, gx = A_.shape
        r0, r1, c0, c1 = coins
        best, kb = None, None
        if cote in ("droite", "gauche"):
            dedans, span, dehors_ = (c1 if cote == "droite" else c0), range(r0, r1 + 1), range(gx)
        else:
            dedans, span, dehors_ = (r0 if cote == "haut" else r1), range(c0, c1 + 1), range(gy)
        for x in dehors_:
            if abs(x - dedans) < k or (x > dedans) != (cote in ("droite", "bas")):
                continue
            a_, b_ = min(x, dedans), max(x, dedans)
            for ya in span:
                for yb in span:
                    if yb - ya < k:
                        continue
                    if cote in ("droite", "gauche"):
                        ok = (_tient(A_, "rangees", ya, a_, b_, k) and _tient(A_, "rangees", yb, a_, b_, k)
                              and _tient(A_, "colonnes", x, ya, yb, k))
                    else:
                        ok = (_tient(A_, "colonnes", ya, a_, b_, k) and _tient(A_, "colonnes", yb, a_, b_, k)
                              and _tient(A_, "rangees", x, ya, yb, k))
                    if not ok:
                        continue
                    cle = ((yb - ya) * (b_ - a_), (yb - ya) + (b_ - a_), -ya, -(b_ - a_))
                    if kb is None or cle > kb:
                        best, kb = les_coins_de_laile(cote, coins, ya, yb, x), cle
        return best
    g = np.random.default_rng(23)
    accord = []
    for i in range(8):
        Ar = np.ones((26, 24), dtype=bool)
        for _ in range(int(g.integers(2, 7))):
            y, x = int(g.integers(0, 26)), int(g.integers(0, 24))
            Ar[max(0, y - int(g.integers(0, 5))):y + 1, max(0, x - int(g.integers(0, 5))):x + 1] = False
        Ar &= g.random((26, 24)) > 0.02
        co = [8, 17, 7, 16]
        for c in LES_COTES:
            accord.append(laile(Ar, co, c, 3)["les_coins"] == _brute(Ar, co, c, 3))
    v("★★★★ chaque aile est celle d'une recherche exhaustive, sur huit empreintes au hasard et quatre côtés",
      all(accord) and len(accord) == 32, str(accord))
    Ap = np.ones((40, 30), dtype=bool)
    ap = les_ailes(Ap, [10, 30, 10, 20], 3)
    v("★★★★ sur une grille pleine, chaque aile va aussi loin que ses lignes le permettent",
      [ap[c]["les_coins"] for c in LES_COTES] == [[1, 10, 10, 20], [10, 30, 20, 28], [30, 38, 10, 20], [10, 30, 1, 10]],
      str({c: ap[c]["les_coins"] for c in LES_COTES}))
    v("★★★ l'aire et le chemin d'une aile sont ceux de ses coins",
      ap["droite"]["laire"] == 20 * 8 and ap["droite"]["le_chemin"] == 28)
    Ae = np.zeros((40, 30), dtype=bool)
    Ae[0:40, 0:23] = True
    v("★★★★ une bande extérieure à moins de k lignes de la bande qu'elle prolonge n'est pas une aile",
      laile(Ae, [10, 30, 10, 20], "droite", 3)["les_coins"] is None
      and laile(np.ones((40, 25), dtype=bool), [10, 30, 10, 20], "droite", 3)["les_coins"] == [10, 30, 20, 23])
    Aa = np.ones((40, 30), dtype=bool)
    Aa[15:18, 23:26] = False
    v("★★★ un trou entre les bandes n'empêche pas l'aile : seules ses bandes doivent tenir",
      laile(Aa, [10, 30, 10, 20], "droite", 3)["les_coins"] == [10, 30, 20, 28])
    Aa[15:18, 27:29] = False
    ah = laile(Aa, [10, 30, 10, 20], "droite", 3)
    v("★★★★ une bande extérieure qu'un trou coupe ne tient pas : l'aile la contourne",
      ah["les_coins"] is not None and ah["les_coins"] != [10, 30, 20, 28] and ah["les_coins"] == _brute(Aa, [10, 30, 10, 20],
                                                                                                         "droite", 3),
      str(ah))
    v("★★★ à neuf lignes, un côté sans marge n'a pas d'aile, et c'est déclaré",
      les_ailes(np.ones((40, 30), dtype=bool), [4, 35, 4, 25], 9)["bas"]["les_coins"] is None)
    bd = les_bandes_de_laile(ap["droite"], [10, 30, 10, 20], 3)
    v("★★★★ une aile lit trois bandes neuves, jamais celle qu'elle partage avec le rectangle",
      len(bd) == 3 and ("colonnes", 20) not in {(b["le_sens"], b["le_centre"]) for b in bd}
      and len({b["cle"] for b in bd}) == 3
      and {(b["le_sens"], b["le_centre"], b["de"], b["a"]) for b in bd}
      == {("rangees", 10, 20, 28), ("rangees", 30, 20, 28), ("colonnes", 28, 10, 30)}, str(bd))
    v("★★★ la bande partagée est celle du côté de l'aile",
      [la_bande_interieure(c, [10, 30, 10, 20]) for c in LES_COTES]
      == [("rangees", 10), ("colonnes", 20), ("rangees", 30), ("colonnes", 10)])
    Ac = np.zeros((20, 20), dtype=bool)
    Ac[2:18, 2:18] = True
    cc = la_couverture(Ac, [[5, 10, 5, 10]], 3)
    v("★★★★ une boucle entoure ses chunks bandes comprises, et seuls les présents comptent",
      cc["combien"] == 8 * 8 and cc["sur"] == 256 and cc["la_part"] == 0.25
      and la_couverture(Ac, [[5, 10, 5, 10], [5, 10, 10, 15]], 3)["combien"] == 8 * 13
      and la_couverture(Ac, [[2, 8, 2, 8]], 3)["combien"] == 8 * 8, str(cc))
    iss = {_ce_qui_reste(a, b, c) for a in (True, False) for b in (True, False) for c in (True, False)}
    v("★★★★ quatre issues distinctes : aucune aile prime, puis le trou, puis le demi-feuillet",
      len(iss) == 4 and _ce_qui_reste(True, False, False) == _ce_qui_reste(True, True, True)
      and _ce_qui_reste(False, True, True) == _ce_qui_reste(False, True, False))

    def _a(ouv, fer):  # noqa: E306
        return {"les_coins": [0, 1, 0, 1], "le_verdict": {"le_segment_entier_reste_ouvert": ouv,
                                                          "le_segment_entier_se_ferme": fer}}
    vv = le_verdict_des_ailes({"haut": _a(False, True), "droite": _a(False, False), "bas": {"les_coins": None},
                               "gauche": _a(False, True)}, 9)
    v("★★★★ une seule aile à un demi-feuillet décide du verdict, et chaque aile garde son issue",
      vv["les_ailes_a_un_demi_feuillet"] == ["droite"] and vv["les_ailes_qui_ferment"] == ["gauche", "haut"]
      and not vv["chaque_aile_se_ferme"] and "DEMI-FEUILLET" in vv["ce_qui_reste_a_mesurer"], str(vv))
    vo = le_verdict_des_ailes({"haut": _a(True, False), "droite": _a(False, False)}, 9)
    v("★★★ une aile ouverte prime sur une aile à un demi-feuillet",
      vo["les_ailes_ouvertes"] == ["haut"] and "OUVERTE" in vo["ce_qui_reste_a_mesurer"])
    vf = le_verdict_des_ailes({"haut": _a(False, True), "bas": {"les_coins": None}}, 9)
    v("★★★ une aile qui ferme et un côté sans aile : chaque aile se ferme",
      vf["chaque_aile_se_ferme"] and vf["les_ailes_qui_tiennent"] == ["haut"])
    v0 = le_verdict_des_ailes({c: {"les_coins": None} for c in LES_COTES}, 9)
    v("★★★★ sans aile, rien ne se ferme : l'issue est qu'il n'y a rien à relier",
      not v0["chaque_aile_se_ferme"] and not v0["les_ailes_qui_tiennent"] and "RIEN À RELIER" in v0["ce_qui_reste_a_mesurer"])

    # la reproduction en chaîne
    def _b(cells, x0=0.0):  # noqa: E306
        return {"domaine": {"h": set(cells)}, "pas": {"h": {c: x0 + c[1] for c in cells}}}
    S0 = {"S": _b([(0, 0), (0, 1)])}
    ch = la_reproduction_en_chaine({"B": _b([(0, 2), (0, 3)]), "A": _b([(0, 1), (0, 2)])}, S0)
    v("★★★★ une bande qui ne croise que des bandes neuves est contrôlée par une bande neuve déjà contrôlée",
      ch.get("decidable") and ch["lordre_du_controle"] == ["A", "B"] and ch["combien_de_coutures_relues"] == 2
      and ch["par_croisement"] == {"A×S": 1, "B×234 A": 1}, str(ch))
    v("★★★★ deux bandes neuves qui ne croisent qu'elles-mêmes ne se contrôlent pas l'une l'autre",
      "ne croise aucune couture" in str(la_reproduction_en_chaine({"C": _b([(5, 5), (5, 6)]), "D": _b([(5, 6), (5, 7)])},
                                                                   S0).get("raison")))
    v("★★★★ une bande neuve qui ne retombe pas sur la bande neuve qui la contrôle est refusée",
      "ne retombe pas" in str(la_reproduction_en_chaine({"A": _b([(0, 1), (0, 2)]), "B": _b([(0, 2), (0, 3)], 1.0)},
                                                         S0).get("raison")))

    # la mesure, sur des publications réelles, une empreinte fabriquée et une lecture qui retombe
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    v("★★★★ ce que 233 publie se relit : sa présence, son rectangle, ses bandes, et il ferme",
      q233.get("decidable") and q233["ferme"] and q233["coins"] == [26, 384, 22, 243] and len(q233["bandes"]) == 4,
      str(q233.get("raison")))
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True

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
    src = _sur(les_sources_de_234, p219, p223, p224, q232f, q233f)
    v("★★★★ les quatre bandes de 233 contrôlent les bandes neuves, à côté de 219, 223, 224 et 232",
      _ok(lambda: sorted(k for k in src if k.startswith("233 ")) == sorted(f"233 {b['cle']}" for b in q233f["bandes"])
          and any(k.startswith("232 ") for k in src) and "219" in src and "223" in src))

    def _champ(f, r, c):  # noqa: E306
        # un même champ pour toutes les bandes neuves : deux bandes qui lisent la même couture y lisent le même pas
        return round(((r * 7919 + c * 104729 + (0 if f == "h" else 31)) % 1000) / 1000.0 * 0.6 - 0.3, 4)

    def _fabrique(bd, A_=Af):  # noqa: E306
        dom = le_domaine(bd["le_sens"], bd["les_lignes"], bd["de"], bd["a"])
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
                    pas_[f][cle] = _champ(f, *cle)
        le_long_f, trav_f = (("h", "v") if bd["le_sens"] == "rangees" else ("v", "h"))
        ll = {}
        for (r, c), x in pas_[le_long_f].items():
            a_, b_ = (r, c) if bd["le_sens"] == "rangees" else (c, r)
            ll.setdefault(a_, {})[b_] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_[trav_f].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        lectures = {l_: {"refuses": {ABSENT: les_absents_dune_ligne(A_, bd["le_sens"], l_, bd["de"], bd["a"])}}
                    for l_ in bd["les_lignes"]}
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": lectures}
    lus = []
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, lambda bd: lus.append(bd) or _fabrique(bd), 49)
    v("★★★★ une empreinte et une lecture fabriquées qui retombent passent la mesure entière",
      m.get("decidable") and "par_aile" in m, str(m.get("raison")))
    v("★★★★ les ailes sont dérivées de l'empreinte : aussi loin que neuf lignes le permettent, aucune en bas",
      _ok(lambda: [m["les_ailes"][c]["les_coins"] for c in LES_COTES]
          == [[9, 26, 22, 243], [26, 384, 243, 276], None, [26, 384, 7, 22]]),
      str({c: m.get("les_ailes", {}).get(c, {}).get("les_coins") for c in LES_COTES}))
    v("★★★★ neuf bandes neuves sont lues, trois par aile, et aucune bande de 233 n'est relue",
      len(lus) == 9 and not ({b["cle"] for b in lus} & {b["cle"] for b in q233f["bandes"]}), str(len(lus)))
    v("★★★★ la présence est contrôlée par les lignes de 232 et de 233, puis par celles qu'on lit",
      _ok(lambda: m["la_presence_contre_232"]["combien_de_lignes"] == 36
          and m["la_presence_contre_233"]["combien_de_lignes"] == 36
          and m["la_presence_contre_la_lecture"]["combien_de_lignes"] == 81))
    v("★★★★ chaque bande neuve est contrôlée par une bande publiée",
      _ok(lambda: {k.split("×")[0] for k in m["la_reproduction"]["par_croisement"]}
          == {b["cle"] for b in m["les_bandes_declarees"]}), str(m.get("la_reproduction")))
    v("★★★★ la bande extérieure de l'aile de gauche, qu'aucune bande publiée ne croise, est contrôlée en chaîne",
      _ok(lambda: not any(k.startswith("colonnes_7_26_384×2") and not k.startswith("colonnes_7_26_384×234 ")
                          for k in m["la_reproduction"]["par_croisement"])
          and any(k.startswith("colonnes_7_26_384×234 ") for k in m["la_reproduction"]["par_croisement"])),
      str(m.get("la_reproduction", {}).get("lordre_du_controle")))
    v("★★★★ chaque aile est analysée sur ses quatre côtés, la bande partagée prise à 233",
      _ok(lambda: all(sorted(m["par_aile"][c]["par_largeur"], key=int) == ["3", "5", "7", "9"]
                      and all(x["les_lignes_par_cote"] == {n_: int(k_) for n_ in ("haut", "droite", "bas", "gauche")}
                              for k_, x in m["par_aile"][c]["par_largeur"].items() if x["fermable"])
                      for c in ("haut", "droite", "gauche"))
          and any(x["fermable"] for c in ("haut", "droite", "gauche") for x in m["par_aile"][c]["par_largeur"].values())
          and m["par_aile"]["bas"] == {"les_coins": None}),
      str({c: {k_: x.get("les_lignes_par_cote") for k_, x in (m.get("par_aile") or {}).get(c, {}).get("par_largeur",
                                                                                                     {}).items()}
           for c in LES_COTES}))
    v("★★★★ la règle de 225 est appliquée, et le verdict est celui des ailes",
      _ok(lambda: m["la_regle_appliquee"] == p225["la_regle"] and m["le_plus_long_trou_franchi_par_225"] == 17
          and m["le_verdict"] == le_verdict_des_ailes(m["par_aile"], 9)))
    v("★★★★ la couverture déclarée est comptée avant la lecture, et celle des ailes qui ferment après",
      _ok(lambda: m["la_couverture_declaree"]["par_le_rectangle"]["combien"]
          < m["la_couverture_declaree"]["par_le_rectangle_et_toutes_les_ailes"]["combien"]
          and m["la_couverture_declaree"]["par_le_rectangle_et_toutes_les_ailes"]["sur"] == int(Af.sum())
          and m["la_couverture"]["par_le_rectangle_et_les_ailes_qui_ferment"]
          == la_couverture(Af, [q233f["coins"]] + [m["les_ailes"][c]["les_coins"]
                                                    for c in m["le_verdict"]["les_ailes_qui_ferment"]], 9)))
    v("★★★★ une présence qui ne retombe pas sur 232 est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232, q233f, _fabrique, 49)
                              .get("raison")))

    def _menteuse(bd):  # noqa: E306
        x = _fabrique(bd)
        l0 = bd["les_lignes"][0]
        x["les_lectures"][l0]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, _menteuse, 49)
                              .get("raison")))

    def _decale(bd):  # noqa: E306
        x = _fabrique(bd)
        for r, s_ in x["en_travers"].items():
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, _decale, 49)
                                  .get("raison")))
    q233o = copy.deepcopy(q233f)
    q233o["ferme"] = False
    v("★★★★ un rectangle de 233 qui ne ferme pas ne fait rien lire",
      "rien à quoi relier" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233o,
                                       lambda bd: lus.append(bd) or _fabrique(bd), 49).get("raison")))
    Ar_ = np.zeros((gy, gx), dtype=bool)
    Ar_[18:389, 18:248] = True
    q232r, q233r = _sur_lempreinte(Ar_)
    lus_r = []
    mr = _sur(mesurer, None, p219, p223, p224, p225, q225, q232r, q233r,
              lambda bd: lus_r.append(bd) or _fabrique(bd, Ar_), 49)
    v("★★★★ une empreinte sans marge autour du rectangle ne porte aucune aile, et rien n'est lu",
      mr.get("decidable") and not lus_r and not mr["le_verdict"]["les_ailes_qui_tiennent"]
      and "RIEN À RELIER" in mr["le_verdict"]["ce_qui_reste_a_mesurer"], str(mr.get("raison")))
    with tempfile.TemporaryDirectory() as tmp:
        dep = Path(tmp) / "lecture.json"
        af = les_ailes(Af, q233f["coins"], 9)
        bl_f = [b for c in LES_COTES if af[c]["les_coins"] for b in les_bandes_de_laile(af[c], q233f["coins"], 9)]
        faux = {b["cle"]: {**b, "le_long": {}, "en_travers": {}, "les_lectures": {}} for b in bl_f}
        une = next(k for k in sorted(faux) if k.startswith("colonnes"))
        faux[une]["les_lignes"] = [x - 2 for x in faux[une]["les_lignes"]]
        dep.write_text(json.dumps({"les_bandes": faux}))
        mf = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, None, 49)
        dep.write_text(json.dumps({"les_bandes": {k: x for k, x in (m.get("les_bandes") or {}).items()}}))
        mj = _sur(mesurer, dep, p219, p223, p224, p225, q225, q232f, q233f, None, 49)
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
        par233 = ce_que_233_a_publie()
        if not par233.get("decidable") or not par233["ferme"]:
            print(f"indécidable : {par233.get('raison') or 'le rectangle de 233 ne ferme pas'}")
            return 1
        A = la_grille_de_presence(par233["presence"])
        k1 = les_largeurs()[-1]
        ailes = les_ailes(A, par233["coins"], k1)
        tenues = [c for c in LES_COTES if ailes[c]["les_coins"]]
        for c in LES_COTES:
            print(f"aile {c} : {ailes[c]}", flush=True)
        print(f"couverture déclarée : rectangle {la_couverture(A, [par233['coins']], k1)} · avec toutes les ailes "
              f"{la_couverture(A, [par233['coins']] + [ailes[c]['les_coins'] for c in tenues], k1)}", flush=True)
        if not tenues:
            return 0
        bandes = [b for c in tenues for b in les_bandes_de_laile(ailes[c], par233["coins"], k1)]
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
