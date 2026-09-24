"""La couverture par boucles se déroule-t-elle sans main ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA PROCÉDURE NE SOIT LANCÉE, SUR LE SEGMENT COMME SUR L'EMPREINTE FABRIQUÉE. Ce qui
était vu avant d'écrire : ce que `233` à `245` publient, et leurs figures.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST CE QUE `244` MET EN TÊTE. De `233` à `243`, chaque boucle est une règle dérivée,
mais le choix de la boucle suivante a été fait en lisant le résultat de la précédente : c'est l'humain que le prix veut
retirer. Et `245` a montré que le pas des coupes de `239` ne voyait pas la traversée dont il était tiré. Une procédure qui
enchaîne les règles seule, au pas qui voit, retrouve-t-elle la couverture, et que lui manque-t-il ?

## La procédure, sans aucun choix

1. LE RECTANGLE : le plus grand de `233`, à neuf lignes, sur la présence que `233` publie.
2. LES CÔTÉS, dans l'ordre haut, droite, bas, gauche. Pour chacun, une file de portions du côté du rectangle, d'abord le
   côté entier. Pour une portion : la plus large largeur de l'échelle de `218` à laquelle la règle de `234` trouve une
   aile, parmi les bandes extérieures qui ne partagent aucune ligne avec les lignes que ce côté exclut.
3. CHAQUE BOUCLE — le rectangle, une aile — est coupée au pas qui voit de `245` : les coupes déjà lues d'abord, parce
   qu'une coupe lue ne coûte rien et qu'une coupe de plus ne fait qu'affiner le profil, à `k` lignes au moins de la
   précédente ; puis chaque écart qui dépasse le pas est partagé en le moins de parts égales qui ne le dépassent pas, là où
   la bande de coupe tient. Elle est jugée à sa largeur, comme `243` : ouverte, franchit, non vue, ou dessous.
4. UNE AILE DESSOUS entre dans la couverture, à sa largeur ; les portions du côté de part et d'autre d'elle rejoignent la
   file.
5. UNE AILE QUI FRANCHIT est départagée par la troisième ligne de `236`, à sa largeur. Si la ligne désignée est sa bande
   extérieure, ce côté l'exclut désormais, avec ses lignes, et la même portion est cherchée à nouveau. Sinon, la portion
   est laissée, et ses deux voisines rejoignent la file.
6. UNE BOUCLE DONT UNE BANDE N'EST PAS LUE est À LIRE : elle n'est pas jugée, et ses bandes sont demandées, avec ce
   qu'elles coûtent en chunks.

⚠⚠ Une bande est servie par ce qui est déjà publié quand des bandes lues de même sens, de même centre et aux lignes qui
contiennent les siennes couvrent toutes ses coutures ; sinon elle est à lire. Ce qui est publié : les lectures de `224`,
`225`, `227`, `228`, `229`, `230`, `231`, `232`, `233`, `234`, `235`, `236`, `237`, `238`, `239`, `240`, `241` et `243`.

## Ce qui se lit, et ce qui le contrôle

Les bandes à lire, par le lecteur de `224`, les moins chères d'abord, puis la procédure est relancée, jusqu'à ce qu'elle
ne demande plus rien. ⚠⚠⚠ Partout où une bande neuve croise une bande publiée ou une bande neuve déjà contrôlée, les pas
relus retombent à l'arrondi, sinon refus ; et les chunks qu'elle compte absents sont ceux que la présence dit absents.

## Ce qui se mesure

Le journal : chaque portion cherchée, la boucle trouvée, sa largeur, ses coupes, son état, et ce qu'il faudrait lire.
LA COUVERTURE : la part de l'empreinte qu'entourent les boucles dessous, chacune à sa largeur. ET LA COMPARAISON avec la
couverture que `243` a obtenue à la main : quelles de ses boucles la procédure retrouve, et lesquelles non.

## Les issues, exclusives

- aucun rectangle ne tient : rien n'est relié ;
- la procédure demande des bandes qui ne sont pas lues : la couverture est celle de ce qui est jugé ;
- elle ne demande plus rien : la couverture est celle de la procédure entière.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une traversée plus courte que le pas qui voit ; ce qui relie ce qu'aucune boucle
n'entoure ; ni ce que vaut la procédure sur un autre segment.

Usage :
    uv run python src/nappe/la_couverture_sans_main.py --verifier
    uv run python src/nappe/la_couverture_sans_main.py --lire <lecture.json>
    uv run python src/nappe/la_couverture_sans_main.py [--depuis <lecture.json>] \\
        --json docs/mesures/la_couverture_sans_main.json
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
from deux_chemins_arrivent_ils_sur_la_meme_spire import ce_que_223_a_rendu, lire_les_bandes, relire_une_bande  # noqa: E402
from deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire import ce_que_225_a_publie  # noqa: E402
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from laquelle_des_deux_colonnes_derive import (la_troisieme_ligne, le_verdict_des_trois,  # noqa: E402
                                               lemboitement_des_trois, les_lignes_de_laile, les_trois_boucles)
from le_rectangle_entre_ses_coupes import les_ecarts_au_dela, les_rangees_de_partage  # noqa: E402
from le_segment_au_dela_du_rectangle_se_relie_t_il import (ce_que_233_a_publie, laile,  # noqa: E402
                                                           les_sources_de_234, les_tenues, tient)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from les_ailes_tiennent_elles_sur_leur_profil import lentre  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (LA_TOLERANCE_DE_REPRODUCTION,  # noqa: E402
                                                          la_reproduction_croisee, le_domaine, les_pas_dune_bande)
from ou_laile_de_droite_se_separe import le_profil, le_travers, lemboitement, les_sous_boucles  # noqa: E402
from ou_sarrete_le_segment import (ce_que_232_a_publie, la_grille_de_presence,  # noqa: E402
                                   la_presence_retombe, le_plus_grand_rectangle)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from sous_laile_qui_evite_la_colonne import le_verdict_des_tranches  # noqa: E402
from une_aile_plus_etroite_tient_elle import analyser_jusqua, la_couverture_des_boucles  # noqa: E402
from une_bande_plus_large_ferme_t_elle_le_grand_rectangle import les_largeurs  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_243_A_PUBLIE = MESURES / "une_aile_plus_etroite_tient_elle.json"
CE_QUE_245_A_PUBLIE = MESURES / "la_portee_voit_elle_sa_traversee.json"
LES_LECTURES_PUBLIEES = [MESURES / f"{n}.json" for n in (
    "deux_chemins_arrivent_ils_sur_la_meme_spire", "une_bande_plus_large_ferme_t_elle_le_grand_rectangle",
    "ou_est_lerreur_de_la_boucle_en_haut_a_gauche", "un_detour_separe_t_il_lerreur_de_la_colonne_71",
    "un_detour_separe_t_il_lerreur_de_la_rangee_99", "la_suite_des_detours_se_deroule_t_elle_sans_main",
    "deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire", "ou_sarrete_le_segment",
    "le_segment_au_dela_du_rectangle_se_relie_t_il", "ou_laile_de_droite_se_separe",
    "laquelle_des_deux_colonnes_derive", "letroite_reste_t_elle_sans_ecart", "le_rectangle_tient_il_sur_son_profil",
    "le_rectangle_entre_ses_coupes", "les_ailes_tiennent_elles_sur_leur_profil", "au_dela_de_la_colonne_qui_derive",
    "une_aile_plus_etroite_tient_elle")]
LES_COTES = ("haut", "droite", "bas", "gauche")
LA_LIMITE_PAR_COTE = 64

LA_QUESTION_DECLAREE = "la couverture par boucles se déroule-t-elle sans main ?"
LA_MESURE_DECLAREE = ("la procédure déclarée — le rectangle de `233`, puis sur chaque côté la plus large aile de `234`, "
                      "coupée au pas qui voit de `245`, départagée par `236` quand elle franchit —, sa couverture, et "
                      "ce qu'elle demande à lire")


def _lire(chemin: Path) -> dict:
    try:
        return json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent ou illisible : {e}"}


def ce_que_245_a_publie(chemin: Path = CE_QUE_245_A_PUBLIE) -> dict:
    d = _lire(chemin)
    q = (d.get("le_verdict") or {}).get("la_portee_qui_voit")
    if not d.get("decidable") or q is None:
        return {"decidable": False, "raison": d.get("raison") or "`245` ne publie pas de pas qui voit"}
    return {"decidable": True, "la_portee_qui_voit": int(q)}


def ce_que_243_a_publie(chemin: Path = CE_QUE_243_A_PUBLIE) -> dict:
    d = _lire(chemin)
    if not d.get("decidable") or d.get("les_boucles_qui_tiennent") is None or not d.get("la_couverture"):
        return {"decidable": False, "raison": d.get("raison") or "`243` ne publie pas ses boucles ni sa couverture"}
    return {"decidable": True, "les_boucles": [([int(x) for x in b["les_coins"]], int(b["la_largeur"]))
                                               for b in d["les_boucles_qui_tiennent"]],
            "la_couverture": d["la_couverture"]}


def les_lectures_publiees(chemins=None) -> dict:
    """Toutes les bandes lues que la chaîne publie, une par définition, dans l'ordre des publications."""
    out, vues = [], set()
    for ch in (LES_LECTURES_PUBLIEES if chemins is None else chemins):
        d = _lire(ch)
        if not d.get("decidable"):
            return {"decidable": False, "raison": f"{Path(ch).name} : {d.get('raison') or 'indécidable'}"}
        for x in (d.get("les_bandes") or {}).values():
            if not isinstance(x, dict) or "le_sens" not in x:
                continue
            cle = (x["le_sens"], int(x["le_centre"]), tuple(int(l_) for l_ in x["les_lignes"]), int(x["de"]), int(x["a"]))
            if cle not in vues:
                vues.add(cle)
                out.append(x)
    return {"decidable": True, "les_bandes": out}


# ─────────────────────────────── les bandes, et ce qui les sert ───────────────────────────────

def une_demande(sens: str, centre: int, de: int, a: int, k: int) -> dict:
    return {"cle": f"{sens}_{int(centre)}_{int(de)}_{int(a)}_{int(k)}", "le_sens": sens, "le_centre": int(centre),
            "les_lignes": les_rangees_a_lire(int(centre), int(k)), "de": int(de), "a": int(a)}


def ce_quelle_coute(d: dict) -> int:
    return len(d["les_lignes"]) * (int(d["a"]) - int(d["de"]) + 1)


class Lectures:
    """Les bandes lues, indexées par sens et centre."""

    def __init__(self, bandes=()):
        self.index: dict = {}
        for x in bandes:
            self.ajouter(x)

    def ajouter(self, x: dict) -> None:
        self.index.setdefault((x["le_sens"], int(x["le_centre"])), []).append(x)

    def servir(self, d: dict) -> list[dict] | None:
        """Les bandes lues qui servent la demande : même sens, même centre, des lignes qui contiennent les siennes, et
        qui couvrent ensemble chacune de ses coutures ; ou aucune."""
        lignes = {int(x) for x in d["les_lignes"]}
        cand = sorted((x for x in self.index.get((d["le_sens"], int(d["le_centre"])), [])
                       if lignes <= {int(l_) for l_ in x["les_lignes"]}), key=lambda x: (int(x["de"]), -int(x["a"])))
        pris, jusqua = [], int(d["de"])
        for x in cand:
            if int(x["de"]) <= jusqua < int(x["a"]):
                pris.append(x)
                jusqua = int(x["a"])
            if jusqua >= int(d["a"]):
                return pris
        return pris if jusqua >= int(d["a"]) and pris else None


def les_pas(servies: dict) -> dict:
    """`{(sens, centre): {ligne: {couture: pas}}}`, depuis les bandes qui servent chaque demande. ⚠ Une bande servie
    dont aucune couture n'est lue a sa clé, vide : l'analyse y voit des trous, et non une bande qui manque."""
    pas: dict = {}
    for d, xs in servies.values():
        cle = (d["le_sens"], int(d["le_centre"]))
        pas.setdefault(cle, {})
        for x in xs:
            for l_, s in relire_une_bande(x)["le_long"].items():
                pas.setdefault(cle, {}).setdefault(int(l_), {}).update({int(c): float(t[0]) for c, t in s.items()})
    return pas


def les_cotes_dune_boucle(coins, k: int) -> list[dict]:
    r0, r1, c0, c1 = [int(x) for x in coins]
    return [une_demande("rangees", r0, c0, c1, k), une_demande("rangees", r1, c0, c1, k),
            une_demande("colonnes", c0, r0, r1, k), une_demande("colonnes", c1, r0, r1, k)]


# ─────────────────────────────── les coupes, au pas qui voit ───────────────────────────────

def les_coupes_sans_main(A: np.ndarray, coins, cote: str, portee: int, k: int, tenues, lue) -> dict:
    """Les coupes déjà lues d'abord, à `k` lignes au moins de la précédente et du bout ; puis chaque écart qui dépasse
    le pas, partagé en le moins de parts égales qui ne le dépassent pas, là où la bande tient."""
    PR, PC = tenues
    k = int(k)
    sens, lo, hi, de, a = le_travers(cote, coins)
    gardees = [int(lo)]
    for y in range(int(lo) + 1, int(hi)):
        if y - gardees[-1] >= k and int(hi) - y >= k and tient(PR, PC, sens, y, de, a) and lue(sens, y, de, a, k):
            gardees.append(y)
    deja = gardees[1:]
    gardees.append(int(hi))
    coupes = [int(lo)]
    for a_, b_ in zip(gardees[:-1], gardees[1:]):
        for y in les_rangees_de_partage([a_, b_], portee):
            if y - coupes[-1] >= k and b_ - y >= k and tient(PR, PC, sens, y, de, a):
                coupes.append(int(y))
        coupes.append(int(b_))
    return {"le_sens": sens, "les_bornes": [int(de), int(a)], "les_coupes": coupes, "les_coupes_deja_lues": deja,
            "combien_de_sous_boucles": len(coupes) - 1,
            "le_plus_grand_ecart": max(b - a_ for a_, b in zip(coupes[:-1], coupes[1:])),
            "les_ecarts_au_dela_de_la_portee": les_ecarts_au_dela(coupes, portee)}


# ─────────────────────────────── juger une boucle, départager une aile ───────────────────────────────

def _definition(x: dict) -> tuple:
    return (x["le_sens"], int(x["le_centre"]), tuple(int(l_) for l_ in x["les_lignes"]), int(x["de"]), int(x["a"]))


def _servir(demandes: list[dict], lectures: Lectures) -> tuple[dict, list[dict]]:
    servies, manquantes = {}, []
    for d in demandes:
        xs = lectures.servir(d)
        if xs is None:
            manquantes.append(d)
        else:
            servies[d["cle"]] = (d, xs)
    return servies, manquantes


def _non_controlee(servies: dict, ctx: dict) -> bool:
    nc = ctx.get("non_controlees") or set()
    return any(_definition(x) in nc for _d, xs in servies.values() for x in xs)


def juger(A: np.ndarray, coins, cote: str, k: int, portee: int, tenues, lectures: Lectures, ctx: dict) -> dict:
    """Une boucle coupée au pas qui voit, jugée à sa largeur ; ou à lire."""
    def lue(sens, y, de, a, k_):  # noqa: E306
        return lectures.servir(une_demande(sens, y, de, a, k_)) is not None
    dec = les_coupes_sans_main(A, coins, cote, portee, k, tenues, lue)
    sens, (de, a) = dec["le_sens"], dec["les_bornes"]
    demandes = les_cotes_dune_boucle(coins, k) + [une_demande(sens, c, de, a, k) for c in dec["les_coupes"][1:-1]]
    servies, manquantes = _servir(demandes, lectures)
    base = {"les_coins": [int(x) for x in coins], "la_largeur": int(k), "le_decoupage": dec}
    if manquantes:
        return {**base, "letat": "à lire", "les_demandes": manquantes,
                "ce_quelle_coute": sum(ce_quelle_coute(d) for d in manquantes)}
    if _non_controlee(servies, ctx):
        return {**base, "letat": "non contrôlée"}
    pas = les_pas(servies)
    entiere = analyser_jusqua(pas, coins, ctx["regle"], ctx["plus_long"], ctx["graine"], ctx["tirages"], k)
    if not entiere.get("decidable"):
        return {**base, "letat": "indécidable", "la_raison": entiere.get("raison")}
    par_sb = []
    for sb in les_sous_boucles(cote, coins, dec["les_coupes"]):
        x = analyser_jusqua(pas, sb, ctx["regle"], ctx["plus_long"], ctx["graine"], ctx["tirages"], k)
        if not x.get("decidable"):
            return {**base, "letat": "indécidable", "la_raison": f"la tranche {sb} : {x.get('raison')}"}
        par_sb.append({"entre": lentre(cote, sb), "les_coins": sb, **x})
    emb = lemboitement(par_sb, entiere, cote)
    if not emb.get("decidable"):
        return {**base, "letat": "indécidable", "la_raison": emb.get("raison")}
    vt = le_verdict_des_tranches(dec, par_sb, ctx["demi"], k)
    x = entiere["par_largeur"][str(k)]
    ouverte = (not x["fermable"]) or bool(vt["les_sous_boucles_ouvertes"])
    franchit = (not ouverte) and (bool(vt["franchit"]) or not x["sous_le_demi_pli"])
    non_vu = (not ouverte) and (not franchit) and bool(vt["les_ecarts_au_dela_de_la_portee"])
    etat = "ouverte" if ouverte else ("franchit" if franchit else ("non vue" if non_vu else "dessous"))
    return {**base, "letat": etat, "la_fermeture": x.get("la_fermeture_en_voxels"), "le_profil": le_profil(par_sb, k),
            "le_pic": vt.get("le_pic")}


def departager(A: np.ndarray, coins, cote: str, k: int, tenues, lectures: Lectures, ctx: dict) -> dict:
    """La troisième ligne de `236`, à la largeur de l'aile, et la ligne qui dérive ; ou à lire."""
    tl = la_troisieme_ligne(A, coins, cote, k, tenues)
    if tl is None:
        return {"letat": "rien ne départage", "la_troisieme_ligne": None}
    sens, _d, _e, lo, hi = les_lignes_de_laile(cote, coins)
    boucles = les_trois_boucles(tl, lo, hi)
    demandes, vues = [], set()
    for co in boucles.values():
        for d in les_cotes_dune_boucle(co, k):
            if d["cle"] not in vues:
                vues.add(d["cle"])
                demandes.append(d)
    servies, manquantes = _servir(demandes, lectures)
    if manquantes:
        return {"letat": "à lire", "la_troisieme_ligne": tl, "les_demandes": manquantes,
                "ce_quelle_coute": sum(ce_quelle_coute(d) for d in manquantes)}
    if _non_controlee(servies, ctx):
        return {"letat": "non contrôlée", "la_troisieme_ligne": tl}
    pas = les_pas(servies)
    par = {}
    for nom, co in boucles.items():
        x = analyser_jusqua(pas, co, ctx["regle"], ctx["plus_long"], ctx["graine"], ctx["tirages"], k)
        if not x.get("decidable"):
            return {"letat": "indécidable", "la_troisieme_ligne": tl, "la_raison": f"{nom} : {x.get('raison')}"}
        par[nom] = {"les_coins": co, **x}
    emb = lemboitement_des_trois(par, sens, tl["la_plus_proche"])
    if not emb.get("decidable"):
        return {"letat": "indécidable", "la_troisieme_ligne": tl, "la_raison": emb.get("raison")}
    v = le_verdict_des_trois(tl, par, k)
    return {"letat": "départagée" if v["la_ligne_qui_derive"] is not None else "non départagée",
            "la_troisieme_ligne": tl, "le_verdict": v}


# ─────────────────────────────── la procédure ───────────────────────────────

def la_portion(rect, cote: str, lo: int, hi: int) -> list[int]:
    r0, r1, c0, c1 = [int(x) for x in rect]
    return [int(lo), int(hi), c0, c1] if cote in ("droite", "gauche") else [r0, r1, int(lo), int(hi)]


def le_cote_entier(rect, cote: str) -> tuple[int, int]:
    r0, r1, c0, c1 = [int(x) for x in rect]
    return (r0, r1) if cote in ("droite", "gauche") else (c0, c1)


def lexterieure(cote: str, coins) -> int:
    r0, r1, c0, c1 = [int(x) for x in coins]
    return {"droite": c1, "gauche": c0, "haut": r0, "bas": r1}[cote]


def derouler(A: np.ndarray, lectures: Lectures, ctx: dict) -> dict:
    """La procédure entière, sur ce que `lectures` sert : le journal, les boucles qui tiennent, et ce qui est à lire."""
    A = np.asarray(A, dtype=bool)
    echelle = sorted(les_largeurs(), reverse=True)
    k1, portee = echelle[0], int(ctx["portee"])
    tenues = {k: les_tenues(A, k) for k in echelle}
    rect = le_plus_grand_rectangle(A, k1)
    if rect is None:
        return {"le_rectangle": None, "le_journal": [], "les_boucles_qui_tiennent": [], "les_demandes": []}
    journal, tiennent, demandes = [], [], {}

    def _noter(j):  # noqa: E306
        for d in j.get("les_demandes") or []:
            demandes.setdefault(d["cle"], d)
    jr = juger(A, rect, "droite", k1, portee, tenues[k1], lectures, ctx)
    _noter(jr)
    journal.append({"la_boucle": "le rectangle", **jr})
    if jr["letat"] == "dessous":
        tiennent.append((list(rect), k1))
    for cote in LES_COTES:
        a_voir, exclues, n = [le_cote_entier(rect, cote)], [], 0
        while a_voir and n < LA_LIMITE_PAR_COTE:
            lo, hi = a_voir.pop(0)
            n += 1
            trouve = None
            for k in echelle:
                d_ = laile(A, la_portion(rect, cote, lo, hi), cote, k, tenues[k], exclues=exclues)
                if d_["les_coins"]:
                    trouve = (k, [int(x) for x in d_["les_coins"]])
                    break
            e = {"la_boucle": "l'aile", "le_cote": cote, "la_portion": [int(lo), int(hi)],
                 "les_exclues": [list(x) for x in exclues]}
            if trouve is None:
                journal.append({**e, "letat": "aucune aile"})
                continue
            k, co = trouve
            j = juger(A, co, cote, k, portee, tenues[k], lectures, ctx)
            _noter(j)
            e.update(j)
            ya, yb = lentre(cote, co)
            voisines = [(p, q) for p, q in ((lo, ya), (yb, hi)) if q > p]
            if j["letat"] == "dessous":
                tiennent.append((co, k))
                a_voir = voisines + a_voir
            elif j["letat"] == "franchit":
                dp = departager(A, co, cote, k, tenues[k], lectures, ctx)
                _noter(dp)
                e["le_departage"] = dp
                x = lexterieure(cote, co)
                ligne = (dp.get("le_verdict") or {}).get("la_ligne_qui_derive")
                if dp["letat"] == "départagée" and ligne == x and [x, k] not in [list(y) for y in exclues]:
                    exclues.append((x, k))
                    a_voir = [(lo, hi)] + a_voir
                else:
                    a_voir = voisines + a_voir
            else:
                a_voir = voisines + a_voir
            journal.append(e)
    return {"le_rectangle": list(rect), "le_journal": journal,
            "les_boucles_qui_tiennent": [{"les_coins": co, "la_largeur": int(k)} for co, k in tiennent],
            "les_demandes": sorted(demandes.values(), key=lambda d: (ce_quelle_coute(d), d["cle"]))}


# ─────────────────────────────── le contrôle ───────────────────────────────

def la_reproduction_sans_main(nouvelles: dict, sources: dict,
                              tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> dict:
    """La reproduction en chaîne de `234`. ⚠⚠ Une bande qui ne croise rien de contrôlé n'est pas un refus : elle reste
    non contrôlée, et les boucles qui la prennent ne sont pas jugées. Un désaccord, lui, refuse la mesure."""
    reste, controlees = sorted(nouvelles), []
    par, n, ecart = {}, 0, 0.0
    avance = True
    while reste and avance:
        avance = False
        for b in list(reste):
            src = {**sources, **{f"neuve {c}": nouvelles[c] for c in controlees}}
            r = la_reproduction_croisee({b: nouvelles[b]}, src, tolerance)
            if not r.get("decidable"):
                if "ne croise aucune couture" not in str(r.get("raison")):
                    return r
                continue
            reste.remove(b)
            controlees.append(b)
            avance = True
            par.update(r["par_croisement"])
            n += int(r["combien_de_coutures_relues"])
            ecart = max(ecart, float(r["lecart_le_plus_grand"]))
    return {"decidable": True, "combien_de_coutures_relues": n, "par_croisement": par,
            "lecart_le_plus_grand": round(ecart, 6), "la_tolerance": float(tolerance), "lordre_du_controle": controlees,
            "les_non_controlees": sorted(reste)}


def le_controle(A: np.ndarray, neuves: dict, sources: dict) -> dict:
    """Les absents contre la présence, puis la reproduction : les bandes neuves non contrôlées, par définition."""
    defs = [{"cle": c, **{k_: x[k_] for k_ in ("le_sens", "le_centre", "les_lignes", "de", "a")}}
            for c, x in sorted(neuves.items())]
    cn = la_presence_retombe(A, defs, neuves)
    if not cn.get("decidable"):
        return {"decidable": False, "raison": cn.get("raison"), "la_presence": cn}
    nouvelles = {c: {"domaine": le_domaine(x["le_sens"], x["les_lignes"], x["de"], x["a"]),
                     "pas": les_pas_dune_bande(relire_une_bande(x))} for c, x in sorted(neuves.items())}
    rep = la_reproduction_sans_main(nouvelles, sources)
    if not rep.get("decidable"):
        return {"decidable": False, "raison": rep.get("raison"), "la_presence": cn, "la_reproduction": rep}
    return {"decidable": True, "la_presence": cn, "la_reproduction": rep,
            "non_controlees": {_definition(neuves[c]) for c in rep["les_non_controlees"]}}


# ─────────────────────────────── la mesure ───────────────────────────────

def la_comparaison(A: np.ndarray, sans_main: list, a_la_main: list) -> dict:
    """Les boucles que `243` tient à la main, celles que la procédure retrouve, et l'inverse."""
    s = {(tuple(b["les_coins"]), int(b["la_largeur"])) for b in sans_main}
    m = {(tuple(co), int(k)) for co, k in a_la_main}
    return {"retrouvees": [list(co) + [k] for co, k in sorted(m & s)],
            "tenues_a_la_main_seulement": [list(co) + [k] for co, k in sorted(m - s)],
            "tenues_sans_main_seulement": [list(co) + [k] for co, k in sorted(s - m)]}


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, pub225: dict | None = None,
            par232: dict | None = None, par233: dict | None = None, par243: dict | None = None,
            par245: dict | None = None, publiees: dict | None = None, lire=None, tirages: int | None = None,
            demi: float | None = None, tours: int = 20) -> dict:
    """La procédure sur ce qui est publié et lu — et, si `lire` est donné, en lisant ce qu'elle demande."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    pub225 = ce_que_225_a_publie() if pub225 is None else pub225
    par232 = ce_que_232_a_publie() if par232 is None else par232
    par233 = ce_que_233_a_publie() if par233 is None else par233
    par243 = ce_que_243_a_publie() if par243 is None else par243
    par245 = ce_que_245_a_publie() if par245 is None else par245
    publiees = les_lectures_publiees() if publiees is None else publiees
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("225 publiée", pub225),
                     ("232", par232), ("233", par233), ("243", par243), ("245", par245), ("les lectures", publiees)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    presence = par233["presence"]
    if [int(x) for x in presence["la_grille"]] != [int(x) for x in par224["la_grille"]]:
        return {**base, "decidable": False, "raison": "la grille de `233` n'est pas celle que les bandes parcourent"}
    A = la_grille_de_presence(presence)
    ctx = {"regle": par225["la_regle"], "plus_long": int(max(pub225["les_longueurs_essayees"])),
           "graine": int(par224["graine"]), "tirages": int(par224["tirages"] if tirages is None else tirages),
           "demi": float(DEMI_PAS_EN_VOXELS) if demi is None else float(demi), "portee": par245["la_portee_qui_voit"]}
    neuves: dict = {}
    if depuis is not None:
        neuves = dict(json.loads(Path(depuis).read_text()).get("les_bandes") or {})
    base.update({"la_portee": ctx["portee"], "combien_de_bandes_publiees": len(publiees["les_bandes"])})
    sources = les_sources_de_234(par219, par223, par224, par232, par233)
    for i, x in enumerate(publiees["les_bandes"]):
        sources[f"publiée {i} {x['le_sens']}_{x['le_centre']}_{x['de']}_{x['a']}"] = {
            "domaine": le_domaine(x["le_sens"], x["les_lignes"], x["de"], x["a"]),
            "pas": les_pas_dune_bande(relire_une_bande(x))}
    r, t, ctrl = None, 0, None
    while True:
        ctrl = le_controle(A, neuves, sources) if neuves else None
        if ctrl is not None and not ctrl.get("decidable"):
            return {**base, "decidable": False, "raison": ctrl.get("raison"), "les_bandes": neuves}
        ctx["non_controlees"] = ctrl["non_controlees"] if ctrl else set()
        lectures = Lectures(list(publiees["les_bandes"]) + list(neuves.values()))
        r = derouler(A, lectures, ctx)
        t += 1
        if not r["les_demandes"] or lire is None or t > int(tours):
            break
        lu = lire_les_bandes(r["les_demandes"], lire=lire)
        if not lu.get("decidable"):
            return {**base, "decidable": False, "raison": lu.get("raison"), "les_bandes": neuves}
        neuves.update(lu["les_bandes"])
    base.update({"les_bandes": neuves})
    if ctrl is not None:
        base.update({"la_presence_contre_la_lecture": ctrl["la_presence"], "la_reproduction": ctrl["la_reproduction"]})
    tiennent = [(b["les_coins"], b["la_largeur"]) for b in r["les_boucles_qui_tiennent"]]
    return {**base, "decidable": True, **r, "ce_qui_reste_a_lire": sum(ce_quelle_coute(d) for d in r["les_demandes"]),
            "la_couverture": la_couverture_des_boucles(A, tiennent),
            "la_couverture_a_la_main": par243["la_couverture"],
            "la_comparaison": la_comparaison(A, r["les_boucles_qui_tiennent"], par243["les_boucles"]),
            "le_verdict": le_verdict(r)}


def _ce_qui_reste(sans_rect: bool, a_lire: bool) -> str:
    if sans_rect:
        return "AUCUN RECTANGLE NE TIENT : RIEN N'EST RELIÉ"
    if a_lire:
        return "LA PROCÉDURE DEMANDE DES BANDES QUI NE SONT PAS LUES : LA COUVERTURE EST CELLE DE CE QUI EST JUGÉ"
    return "LA PROCÉDURE NE DEMANDE PLUS RIEN : LA COUVERTURE EST CELLE DE LA PROCÉDURE ENTIÈRE"


def le_verdict(r: dict) -> dict:
    sans = r["le_rectangle"] is None
    a_lire = (not sans) and bool(r["les_demandes"])
    return {"il_y_a_un_rectangle": not sans, "il_reste_a_lire": a_lire,
            "combien_de_bandes_a_lire": len(r["les_demandes"]),
            "ce_qui_reste_a_mesurer": _ce_qui_reste(sans, a_lire)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"rectangle : {r['le_rectangle']} · pas {r['la_portee']} · {r['combien_de_bandes_publiees']} bandes publiées · "
          f"{len(r['les_bandes'])} bandes neuves")
    for e in r["le_journal"]:
        dp = e.get("le_departage") or {}
        print(f"  {e['la_boucle']:<12} {e.get('le_cote', ''):<7} portion {e.get('la_portion')} · exclues "
              f"{e.get('les_exclues')} · {e.get('la_largeur')} lignes · {e.get('les_coins')} · {e['letat']}"
              f"{' · coût ' + str(e['ce_quelle_coute']) if e.get('ce_quelle_coute') else ''}"
              f"{' · profil ' + str([p['le_cumul_en_voxels'] for p in e['le_profil']]) if e.get('le_profil') else ''}"
              f"{' · départage ' + dp['letat'] + ' ' + str((dp.get('le_verdict') or {}).get('la_ligne_qui_derive')) if dp else ''}")
    print(f"à lire : {len(r['les_demandes'])} bandes, {r['ce_qui_reste_a_lire']} chunks")
    print(f"couverture : {r['la_couverture']} · à la main (243) : {r['la_couverture_a_la_main']}")
    print(f"comparaison : {r['la_comparaison']}")
    print(f"VERDICT · {r['le_verdict']}")


# ─────────────────────────────── la batterie ───────────────────────────────

def verifier() -> int:
    import copy
    import tempfile

    from ou_sarrete_le_segment import ABSENT, les_absents_dune_ligne, les_sources
    from au_dela_de_la_colonne_qui_derive import les_coupes_a_la_portee
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

    # servir une demande
    def _lu(sens, c, lignes, de, a):  # noqa: E306
        return {"le_sens": sens, "le_centre": c, "les_lignes": list(lignes), "de": de, "a": a,
                "le_long": {str(l_): {str(s): [0.1, 0.0, 16] for s in range(de, a)} for l_ in lignes},
                "en_travers": {}, "les_lectures": {}}
    L0 = Lectures([_lu("rangees", 50, range(46, 55), 10, 30), _lu("rangees", 50, range(46, 55), 30, 60),
                   _lu("colonnes", 20, range(17, 24), 0, 40)])
    v("★★★★ une demande est servie par une bande de lignes qui contiennent les siennes, ou par des morceaux qui en "
      "couvrent chaque couture",
      _ok(lambda: len(L0.servir(une_demande("rangees", 50, 12, 25, 9))) == 1
          and len(L0.servir(une_demande("rangees", 50, 12, 55, 9))) == 2
          and len(L0.servir(une_demande("colonnes", 20, 5, 35, 7))) == 1
          and len(L0.servir(une_demande("rangees", 50, 20, 40, 7))) == 2))
    v("★★★★ une demande n'est pas servie si une couture manque, si une ligne manque, ou d'un autre centre",
      _ok(lambda: L0.servir(une_demande("rangees", 50, 5, 25, 9)) is None
          and L0.servir(une_demande("rangees", 50, 12, 61, 9)) is None
          and L0.servir(une_demande("colonnes", 20, 5, 35, 9)) is None
          and L0.servir(une_demande("rangees", 51, 12, 25, 9)) is None
          and Lectures([_lu("rangees", 50, range(46, 55), 10, 20), _lu("rangees", 50, range(46, 55), 21, 40)])
          .servir(une_demande("rangees", 50, 12, 30, 9)) is None))
    d0 = une_demande("rangees", 50, 12, 25, 9)
    v("★★★ une bande servie dont aucune couture n'est lue a sa clé, vide : l'analyse y verra des trous",
      _ok(lambda: les_pas({"d": (d0, [{**_lu("rangees", 50, range(46, 55), 10, 30), "le_long": {}}])})
          == {("rangees", 50): {}}))
    v("★★★ ce qu'une bande coûte : ses lignes fois ses chunks", ce_quelle_coute(une_demande("colonnes", 20, 5, 35, 7)) == 7 * 31)

    # le contrôle
    def _b(cle, x):  # noqa: E306
        return {"domaine": {"h": {cle}}, "pas": {"h": {cle: x}}}
    rs = la_reproduction_sans_main({"a": _b((1, 1), 0.5), "b": _b((9, 9), 0.1), "c": _b((1, 1), 0.5)},
                                   {"s": _b((1, 1), 0.5)})
    rs2 = la_reproduction_sans_main({"a": _b((1, 1), 0.5), "d": {"domaine": {"h": {(1, 1), (2, 2)}},
                                                                 "pas": {"h": {(1, 1): 0.5, (2, 2): 0.2}}},
                                     "e": _b((2, 2), 0.2)}, {"s": _b((1, 1), 0.5)})
    v("★★★★ une bande qui ne croise rien de contrôlé reste non contrôlée ; une bande neuve contrôlée en contrôle une autre",
      _ok(lambda: rs["decidable"] and rs["les_non_controlees"] == ["b"] and sorted(rs["lordre_du_controle"]) == ["a", "c"]
          and rs2["les_non_controlees"] == [] and "e" in rs2["lordre_du_controle"]), str(rs))
    v("★★★★ une bande qui ne retombe pas sur une source est un refus, pas une bande non contrôlée",
      _ok(lambda: not la_reproduction_sans_main({"a": _b((1, 1), 0.9)}, {"s": _b((1, 1), 0.5)})["decidable"]))

    # les coupes sans main
    Ap = np.ones((396, 285), dtype=bool)
    tp = les_tenues(Ap, 9)
    rien = les_coupes_sans_main(Ap, [26, 223, 243, 276], "droite", 40, 9, tp, lambda *a: False)
    ref = les_coupes_a_la_portee(Ap, [26, 223, 243, 276], "droite", 40, 9, tp)
    v("★★★★ sans rien de lu, les coupes sont celles de 241 au même pas",
      _ok(lambda: all(rien[k_] == ref[k_] for k_ in ref) and rien["les_coupes_deja_lues"] == []), str(rien))
    lues = {100, 105, 150}
    cl = les_coupes_sans_main(Ap, [26, 223, 243, 276], "droite", 29, 9, tp, lambda s, y, *a: y in lues)
    v("★★★★ les coupes déjà lues d'abord, à k lignes l'une de l'autre, puis chaque écart partagé au pas",
      _ok(lambda: cl["les_coupes_deja_lues"] == [100, 150] and 100 in cl["les_coupes"] and 150 in cl["les_coupes"]
          and 105 not in cl["les_coupes"] and cl["le_plus_grand_ecart"] <= 29 and cl["les_coupes"][0] == 26
          and cl["les_coupes"][-1] == 223), str(cl))
    Ah = Ap.copy()
    Ah[80:85, 250] = False
    ch_ = les_coupes_sans_main(Ah, [26, 223, 243, 276], "droite", 29, 9, les_tenues(Ah, 9), lambda *a: False)
    v("★★★ une coupe dont la bande ne tient pas n'est pas gardée, et l'écart qui en naît est nommé",
      _ok(lambda: ch_["les_ecarts_au_dela_de_la_portee"] != []
          and all(not (76 <= c <= 88) for c in ch_["les_coupes"])), str(ch_))

    # la procédure, sur des publications réelles, une empreinte et un champ fabriqués
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    q225, q232, q233 = ce_que_225_a_publie(), ce_que_232_a_publie(), ce_que_233_a_publie()
    gy, gx = p224["la_grille"]
    Af = np.zeros((gy, gx), dtype=bool)
    Af[5:395, 3:281] = True
    Af[5:18, :] = False
    Af[200:395, 250:281] = False
    Af[100:111, 265:267] = False
    Af[140:146, 252] = False
    Af[140:146, 258] = False
    Af[140:200, 254:281] = False

    def _champ(f, r, c):  # noqa: E306
        return round((((r * 2654435761) ^ (c * 40503 + (0 if f == "h" else 97))) % 1001) / 1000.0 * 0.6 - 0.3, 4)

    def _plat(f, r, c):  # noqa: E306
        # la colonne extérieure de droite dérive, assez pour franchir le demi-feuillet
        return _champ(f, r, c) + (-0.5 if f == "v" and c >= 272 else 0.0)

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

    q232f, q233f = _sur_lempreinte(Af, _plat)
    src = les_sources_de_234(p219, p223, p224, q232f, q233f)
    Am = la_grille_de_presence(q233f["presence"])
    q243p = {"decidable": True, "les_boucles": [], "la_couverture": {"combien": 0, "sur": 0, "la_part": 0.0}}
    q245p = {"decidable": True, "la_portee_qui_voit": 29}
    rect9 = list(le_plus_grand_rectangle(Am, 9))
    vide = {"decidable": True, "les_bandes": []}
    lus = []

    def _lit(b):  # noqa: E306
        lus.append(b["cle"])
        return _fabrique(b, src, _plat)
    m0 = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, vide, None, 49, 36.0)
    v("★★★★ sans lecteur ni lecture, rien n'est lu : tout est à lire, chaque demande avec son coût, et rien n'est couvert",
      _ok(lambda: m0["decidable"] and m0["les_boucles_qui_tiennent"] == [] and m0["la_couverture"]["combien"] == 0
          and m0["les_demandes"] and m0["ce_qui_reste_a_lire"] == sum(ce_quelle_coute(d) for d in m0["les_demandes"])
          and all(e["letat"] in ("à lire", "aucune aile") for e in m0["le_journal"])
          and "NE SONT PAS LUES" in m0["le_verdict"]["ce_qui_reste_a_mesurer"]), str(m0.get("raison")))
    m = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, vide, _lit, 49, 36.0)
    v("★★★★ en lisant ce qu'elle demande, la procédure va au bout et ne demande plus rien",
      _ok(lambda: m["decidable"] and m["les_demandes"] == [] and len(lus) > 0
          and "NE DEMANDE PLUS RIEN" in m["le_verdict"]["ce_qui_reste_a_mesurer"]), str(m.get("raison")))
    v("★★★★ chaque bande est lue une fois, et seulement si elle est demandée",
      _ok(lambda: len(lus) == len(set(lus)) and set(lus) == set(m["les_bandes"])))
    v("★★★★ le rectangle est celui de 233, et il tient",
      _ok(lambda: m["le_rectangle"] == list(le_plus_grand_rectangle(Am, 9))
          and m["le_journal"][0]["la_boucle"] == "le rectangle" and m["le_journal"][0]["letat"] == "dessous"
          and m["le_journal"][0]["le_decoupage"]["le_plus_grand_ecart"] <= 29))
    dr = [e for e in m.get("le_journal") or [] if e.get("le_cote") == "droite" and e["letat"] != "aucune aile"]
    v("★★★★ l'aile de droite, par la colonne qui dérive, franchit ; la troisième ligne la départage, et le côté l'exclut",
      _ok(lambda: dr[0]["letat"] == "franchit" and dr[0]["les_coins"][3] == 276
          and dr[0]["le_departage"]["letat"] == "départagée"
          and dr[0]["le_departage"]["le_verdict"]["la_ligne_qui_derive"] == 276
          and dr[1]["les_exclues"] == [[276, 9]] and dr[1]["la_portion"] == dr[0]["la_portion"]),
      str([(e["les_coins"], e["letat"], e.get("les_exclues")) for e in dr]))
    v("★★★★ l'aile suivante évite la colonne, et sous elle la procédure descend en largeur tant que rien ne tient plus "
      "large",
      _ok(lambda: dr[1]["letat"] == "dessous" and abs(dr[1]["les_coins"][3] - 276) >= 9 and dr[1]["la_largeur"] == 9
          and any(e["la_largeur"] < 9 and e["letat"] == "dessous" for e in dr[2:])),
      str([(e["les_coins"], e["la_largeur"], e["letat"]) for e in dr]))
    v("★★★★ chaque boucle dessous est coupée au pas qui voit, et la couverture est leur union, chacune à sa largeur",
      _ok(lambda: all(e["le_decoupage"]["le_plus_grand_ecart"] <= 29 for e in m["le_journal"] if e["letat"] == "dessous")
          and m["la_couverture"] == la_couverture_des_boucles(
              Am, [(b["les_coins"], b["la_largeur"]) for b in m["les_boucles_qui_tiennent"]])
          and len(m["les_boucles_qui_tiennent"]) == sum(1 for e in m["le_journal"] if e["letat"] == "dessous")))
    v("★★★★ une boucle non contrôlée n'est ni jugée ni couverte",
      _ok(lambda: any(e["letat"] == "non contrôlée" for e in m["le_journal"]) and all(e["les_coins"] not in [b_["les_coins"] for b_ in m["les_boucles_qui_tiennent"]]
                      and "la_fermeture" not in e for e in m["le_journal"] if e["letat"] == "non contrôlée")))
    v("★★★ chaque côté est cherché, et les portions d'une aile dessous rejoignent la file",
      _ok(lambda: {e["le_cote"] for e in m["le_journal"][1:]} == set(LES_COTES)
          and any(e["la_portion"][0] == dr[1]["les_coins"][1] for e in dr[2:])))
    def _rejoue(m_):  # noqa: E306
        with tempfile.TemporaryDirectory() as tmp:
            dep = Path(tmp) / "l.json"
            dep.write_text(json.dumps({"les_bandes": m_["les_bandes"]}))
            return json.dumps(mesurer(dep, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, vide, None, 49,
                                      36.0), sort_keys=True)
    v("★★★★ la mesure se rejoue depuis sa lecture, à l'identique, sans rien lire",
      _ok(lambda: _rejoue(m) == json.dumps(m, sort_keys=True)))
    pub = {"decidable": True, "les_bandes": [{**_fabrique(d, src, _plat), **{k_: d[k_] for k_ in
                                                                              ("le_sens", "le_centre", "les_lignes",
                                                                               "de", "a")}}
                                             for d in les_cotes_dune_boucle(rect9, 9)]}
    for x in pub["les_bandes"]:
        for k_ in ("le_long", "en_travers"):
            x[k_] = {str(a_): {str(b_): list(t) for b_, t in s.items()} for a_, s in x[k_].items()}
        x["les_lectures"] = {str(l_): y for l_, y in x["les_lectures"].items()}
    lus_p = []
    mp = _sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, pub,
              lambda b: lus_p.append(b["cle"]) or _fabrique(b, src, _plat), 49, 36.0)
    v("★★★★ ce qui est déjà publié n'est pas relu, et la procédure retombe sur la même couverture",
      _ok(lambda: mp["decidable"] and not any(c in lus_p for c in (d["cle"] for d in les_cotes_dune_boucle(
          rect9, 9))) and mp["la_couverture"] == m["la_couverture"]), str(mp.get("raison")))
    v("★★★ la comparaison dit ce que la main tenait et ce que la procédure tient",
      _ok(lambda: la_comparaison(Am, [{"les_coins": [1, 2, 3, 4], "la_largeur": 9}], [([1, 2, 3, 4], 9), ([5, 6, 7, 8], 7)])
          == {"retrouvees": [[1, 2, 3, 4, 9]], "tenues_a_la_main_seulement": [[5, 6, 7, 8, 7]],
              "tenues_sans_main_seulement": []}))

    # les refus
    def _menteuse(b):  # noqa: E306
        x = _fabrique(b, src, _plat)
        x["les_lectures"][b["les_lignes"][0]]["refuses"][ABSENT] += 1
        return x
    v("★★★★ une lecture dont les absents ne sont pas ceux de la présence est refusée",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, vide,
                                   _menteuse, 49, 36.0).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b, src, _plat)
        for s_ in list(x["en_travers"].values()) + list(x["le_long"].values()):
            for c in s_:
                s_[c] = (s_[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une bande qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas sur" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p, q245p, vide,
                                       _decale, 49, 36.0).get("raison")))
    v("★★★ sans le pas de 245, ou sans une publication, la mesure est refusée",
      "`245`" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, q233f, q243p,
                          {"decidable": False, "raison": "x"}, vide, None, 49, 36.0).get("raison"))
      and "`233`" in str(_sur(mesurer, None, p219, p223, p224, p225, q225, q232f, {"decidable": False, "raison": "x"},
                              q243p, q245p, vide, None, 49, 36.0).get("raison")))
    Az = np.zeros_like(Af)
    q232z, q233z = _sur_lempreinte(Az, _plat)
    mz = _sur(mesurer, None, p219, p223, p224, p225, q225, q232z, q233z, q243p, q245p, vide, None, 49, 36.0)
    v("★★★ sans rectangle, rien n'est relié", _ok(lambda: mz["le_rectangle"] is None
                                                  and "RIEN N'EST RELIÉ" in mz["le_verdict"]["ce_qui_reste_a_mesurer"]),
      str(mz.get("raison")))

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
        deja = json.loads(a.lire.read_text()) if a.lire.exists() else {}
        neuves = dict(deja.get("les_bandes") or {})
        a.lire.parent.mkdir(parents=True, exist_ok=True)

        def ecrire(d):  # noqa: E306
            a.lire.write_text(json.dumps({"les_bandes": {**neuves, **d}}, ensure_ascii=False))
            print(f"écrit : {a.lire} ({len({**neuves, **d})} bandes)", flush=True)
        for tour in range(20):
            tmp = a.lire.with_suffix(".tour.json")
            tmp.write_text(json.dumps({"les_bandes": neuves}, ensure_ascii=False))
            r = mesurer(tmp)
            tmp.unlink(missing_ok=True)
            if not r.get("decidable"):
                print(f"indécidable : {r.get('raison')}")
                return 1
            print(f"tour {tour} : {len(r['les_demandes'])} bandes, {r['ce_qui_reste_a_lire']} chunks à lire", flush=True)
            if not r["les_demandes"]:
                return 0
            lu = lire_les_bandes(r["les_demandes"], neuves, ecrire)
            if not lu.get("decidable"):
                print(f"indécidable : {lu.get('raison')}")
                return 1
            neuves = dict(lu["les_bandes"])
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
