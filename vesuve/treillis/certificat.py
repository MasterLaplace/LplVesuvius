"""E6 : le certificat par boucles, enchaîné sans main — ce qui remplace l'humain du transfert.

Une boucle de bandes de consensus qui reste sous le demi-feuillet à CHAQUE coupe de son profil, coupée
au pas qui voit (29 rangées, `245`), certifie que ses deux chemins n'ont pas changé de spire : les
chunks qu'elle entoure sont sur la spire du rectangle, au sens où aucun écart d'une spire n'y est vu
(`R4-F404`). La procédure (`246` §1) : le plus grand rectangle, puis sur chaque côté la plus large aile,
coupée au pas qui voit, départagée par une troisième ligne quand elle franchit, et les portions
voisines remises en file.

Ce module rend en plus ce que `246` ne publiait pas : le MASQUE par chunk (0 absent, 1 présent non
certifié, 2 certifié), et il dit, quand c'est le cas, que des ailes sont comptées autour d'un rectangle
qui n'est pas lui-même jugé.
"""
from __future__ import annotations

import numpy as np

from vesuve.treillis import boucle, geometrie as geo

LA_LIMITE_PAR_COTE = 64
LA_TOLERANCE_DE_REPRODUCTION = 0.5e-4 + 1e-6
ABSENT = "absent du dépôt"


# ── les demandes, et ce qui les sert ─────────────────────────────────────────────────────────────

def une_demande(sens: str, centre: int, de: int, a: int, k: int) -> dict:
    return {"cle": f"{sens}_{int(centre)}_{int(de)}_{int(a)}_{int(k)}", "le_sens": sens, "le_centre": int(centre),
            "les_lignes": geo.les_lignes(int(centre), int(k)), "de": int(de), "a": int(a)}


def ce_quelle_coute(d: dict) -> int:
    """En chunks : ce qu'une bande demande de lire."""
    return len(d["les_lignes"]) * (int(d["a"]) - int(d["de"]) + 1)


def la_definition(x: dict) -> tuple:
    return (x["le_sens"], int(x["le_centre"]), tuple(int(l_) for l_ in x["les_lignes"]), int(x["de"]), int(x["a"]))


class Lectures:
    """Les bandes lues, indexées par sens et centre. Une demande est servie par des bandes de même sens
    et même centre, dont les lignes contiennent les siennes, et qui couvrent ensemble chacune de ses
    coutures ; une bande de neuf lignes sert donc une demande de sept."""

    def __init__(self, bandes=()):
        self.index: dict = {}
        for x in bandes:
            self.index.setdefault((x["le_sens"], int(x["le_centre"])), []).append(x)

    def servir(self, d: dict) -> list[dict] | None:
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
    """`{(sens, centre): {ligne: {couture: pas}}}`. Une bande servie sans couture lue garde sa clé, vide :
    l'analyse y voit des trous, et non une bande qui manque."""
    pas: dict = {}
    for d, xs in servies.values():
        cle = (d["le_sens"], int(d["le_centre"]))
        pas.setdefault(cle, {})
        for x in xs:
            for l_, s in (x.get("le_long") or {}).items():
                pas[cle].setdefault(int(l_), {}).update({int(c): float(t[0]) for c, t in s.items()})
    return pas


def les_cotes_dune_boucle(coins, k: int) -> list[dict]:
    r0, r1, c0, c1 = (int(x) for x in coins)
    return [une_demande("rangees", r0, c0, c1, k), une_demande("rangees", r1, c0, c1, k),
            une_demande("colonnes", c0, r0, r1, k), une_demande("colonnes", c1, r0, r1, k)]


def _servir(demandes: list[dict], lectures: Lectures) -> tuple[dict, list[dict]]:
    servies, manquantes = {}, []
    for d in demandes:
        xs = lectures.servir(d)
        if xs is None:
            manquantes.append(d)
        else:
            servies[d["cle"]] = (d, xs)
    return servies, manquantes


# ── le contrôle d'une lecture neuve ──────────────────────────────────────────────────────────────

def le_domaine(sens: str, lignes, de: int, a: int) -> dict:
    """Les coutures qu'une bande lit, par famille : `h` (rangée, colonne de gauche), `v` (rangée du dessus, colonne)."""
    L = [int(x) for x in lignes]
    if sens == "rangees":
        return {"h": {(r, c) for r in L for c in range(int(de), int(a))},
                "v": {(r, c) for r in L[:-1] for c in range(int(de), int(a) + 1)}}
    return {"v": {(r, c) for c in L for r in range(int(de), int(a))},
            "h": {(r, c) for r in range(int(de), int(a) + 1) for c in L[:-1]}}


def les_pas_dune_bande(x: dict) -> dict:
    ll = {(int(a), int(b)): float(t[0]) for a, s in x["le_long"].items() for b, t in s.items()}
    tt = {(int(r), int(c)): float(t[0]) for r, s in x["en_travers"].items() for c, t in s.items()}
    if x["le_sens"] == "rangees":
        return {"h": ll, "v": tt}
    return {"v": {(r, c): p for (c, r), p in ll.items()}, "h": tt}


def une_source(x: dict) -> dict:
    return {"domaine": le_domaine(x["le_sens"], x["les_lignes"], x["de"], x["a"]), "pas": les_pas_dune_bande(x)}


class LectureRefusee(Exception):
    """Une bande neuve ne retombe pas sur ce qui est publié : deux lecteurs différents, la mesure s'arrête."""


def _controler_une(n: str, N: dict, sources: dict, tolerance: float) -> int:
    vus = 0
    for s in sorted(sources):
        S = sources[s]
        for f in ("h", "v"):
            if f not in N["pas"] or f not in S["pas"]:
                continue
            for cle in sorted(N["domaine"][f] & S["domaine"][f]):
                chez_moi, chez_eux = cle in N["pas"][f], cle in S["pas"][f]
                if chez_moi != chez_eux:
                    raise LectureRefusee(f"la couture {f} {cle} est lue par {n} et non par {s}, ou l'inverse")
                if not chez_moi:
                    continue
                e = abs(N["pas"][f][cle] - S["pas"][f][cle])
                if e > float(tolerance):
                    raise LectureRefusee(f"la couture {f} {cle} de {n} ne retombe pas sur {s} (écart {e:.4g} voxel)")
                vus += 1
    return vus


def les_non_controlees(neuves: dict, sources: dict, tolerance: float = LA_TOLERANCE_DE_REPRODUCTION) -> set:
    """La reproduction en chaîne : une bande neuve est contrôlée par une source publiée qu'elle croise, ou
    par une bande neuve DÉJÀ contrôlée. Une bande qui ne croise rien reste non contrôlée (ses boucles ne
    sont pas jugées) ; un désaccord lève `LectureRefusee`."""
    nouvelles = {c: une_source(x) for c, x in neuves.items()}
    reste, controlees, avance = sorted(nouvelles), [], True
    while reste and avance:
        avance = False
        for b in list(reste):
            src = {**sources, **{f"neuve {c}": nouvelles[c] for c in controlees}}
            if _controler_une(b, nouvelles[b], src, tolerance) == 0:
                continue
            reste.remove(b)
            controlees.append(b)
            avance = True
    return {la_definition(neuves[c]) for c in reste}


def la_presence_retombe(A: np.ndarray, neuves: dict) -> None:
    """Chaque ligne lue compte autant de chunks absents que la liste du dépôt ; sinon, refus."""
    for c, b in neuves.items():
        for l_ in b["les_lignes"]:
            x = (b.get("les_lectures") or {}).get(str(l_))
            if x is None:
                raise LectureRefusee(f"la ligne {l_} de {c} n'a pas de lecture")
            lu = int((x.get("refuses") or {}).get(ABSENT, 0))
            if b["le_sens"] == "rangees":
                liste = int((~A[int(l_), int(b["de"]):int(b["a"]) + 1]).sum())
            else:
                liste = int((~A[int(b["de"]):int(b["a"]) + 1, int(l_)]).sum())
            if lu != liste:
                raise LectureRefusee(f"la ligne {l_} de {c} : {lu} chunks absents à la lecture, {liste} selon la liste")


# ── juger une boucle, départager une aile ───────────────────────────────────────────────────────

def juger(coins, cote: str, k: int, portee: int, tenues, lectures: Lectures, ctx: dict) -> dict:
    """Une boucle coupée au pas qui voit, jugée à sa largeur : dessous, franchit, ouverte, non vue, ou à lire."""
    def lue(sens, y, de, a, k_):
        return lectures.servir(une_demande(sens, y, de, a, k_)) is not None
    dec = geo.les_coupes_sans_main(coins, cote, portee, k, tenues, lue)
    sens, (de, a) = dec["le_sens"], dec["les_bornes"]
    demandes = les_cotes_dune_boucle(coins, k) + [une_demande(sens, c, de, a, k) for c in dec["les_coupes"][1:-1]]
    servies, manquantes = _servir(demandes, lectures)
    base = {"les_coins": [int(x) for x in coins], "la_largeur": int(k), "le_decoupage": dec}
    if manquantes:
        return {**base, "letat": "à lire", "les_demandes": manquantes,
                "ce_quelle_coute": sum(ce_quelle_coute(d) for d in manquantes)}
    nc = ctx.get("non_controlees") or set()
    if any(la_definition(x) in nc for _d, xs in servies.values() for x in xs):
        return {**base, "letat": "non contrôlée"}
    pas = les_pas(servies)
    arg = (ctx["plus_long"], ctx["graine"], ctx["tirages"], k)
    entiere = boucle.analyser_jusqua(pas, coins, *arg)
    par_sb = [{"entre": geo.lentre(cote, sb), "les_coins": sb, **boucle.analyser_jusqua(pas, sb, *arg)}
              for sb in geo.les_sous_boucles(cote, coins, dec["les_coupes"])]
    refus = boucle.lemboitement(par_sb, entiere, cote)
    if refus is not None:
        return {**base, "letat": "indécidable", "la_raison": refus}
    vt = boucle.le_verdict_des_tranches(dec, par_sb, ctx["demi"], k)
    x = entiere["par_largeur"][str(k)]
    ouverte = (not x["fermable"]) or bool(vt["les_sous_boucles_ouvertes"])
    franchit = (not ouverte) and (bool(vt["franchit"]) or not x["sous_le_demi_pli"])
    non_vue = (not ouverte) and (not franchit) and bool(vt["les_ecarts_au_dela_de_la_portee"])
    etat = "ouverte" if ouverte else ("franchit" if franchit else ("non vue" if non_vue else "dessous"))
    return {**base, "letat": etat, "la_fermeture": x.get("la_fermeture_en_voxels"),
            "le_profil": boucle.le_profil(par_sb, k), "le_pic": vt.get("le_pic")}


def departager(A: np.ndarray, coins, cote: str, k: int, tenues, lectures: Lectures, ctx: dict) -> dict:
    """Quelle ligne de l'aile dérive ? La troisième ligne de `236` : parmi l'aile, l'étroite et la large, la
    plus serrée n'emprunte pas la ligne fautive, si chacune des deux autres la dépasse de plus que son bruit."""
    tl = geo.la_troisieme_ligne(A, coins, cote, k, tenues)
    if tl is None:
        return {"letat": "rien ne départage", "la_troisieme_ligne": None}
    sens, _d, _e, lo, hi = geo.les_lignes_de_laile(cote, coins)
    boucles = geo.les_trois_boucles(tl, lo, hi)
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
    nc = ctx.get("non_controlees") or set()
    if any(la_definition(x) in nc for _d, xs in servies.values() for x in xs):
        return {"letat": "non contrôlée", "la_troisieme_ligne": tl}
    pas = les_pas(servies)
    par = {nom: {"les_coins": co, **boucle.analyser_jusqua(pas, co, ctx["plus_long"], ctx["graine"], ctx["tirages"], k)}
           for nom, co in boucles.items()}
    refus = boucle.lemboitement_des_trois(par, sens, tl["la_plus_proche"])
    if refus is not None:
        return {"letat": "indécidable", "la_troisieme_ligne": tl, "la_raison": refus}
    verdict = le_verdict_des_trois(tl, par, k)
    return {"letat": "départagée" if verdict["la_ligne_qui_derive"] is not None else "non départagée",
            "la_troisieme_ligne": tl, "le_verdict": verdict}


def le_verdict_des_trois(tl: dict, par: dict, k: int) -> dict:
    """À la largeur de l'aile : la plus serrée des trois boucles, et la ligne qu'elle n'emprunte pas, si
    chacune des deux autres la dépasse de plus que la médiane de son propre nul."""
    xs = {n: par[n]["par_largeur"][str(k)] for n in ("laile", "letroite", "la_large")}
    ouvertes = [n for n, x in xs.items() if not x["fermable"]]
    verdict = {"la_largeur_jugee": int(k), "les_boucles_ouvertes": ouvertes, "la_plus_serree": None,
               "tranche": False, "la_ligne_qui_derive": None}
    if ouvertes:
        return verdict
    L = {n: abs(float(x["la_fermeture_en_voxels"])) for n, x in xs.items()}
    serree = min(("laile", "letroite", "la_large"), key=lambda n: L[n])
    marges = {n: round(L[n] - L[serree] - float(xs[n]["le_nul"]["la_fermeture_mediane_en_valeur_absolue"]), 4)
              for n in L if n != serree}
    tranche = all(m >= 0 for m in marges.values())
    ligne = geo.lexclue(serree, tl)
    verdict.update({"la_plus_serree": serree, "les_marges": marges, "tranche": bool(tranche),
                    "la_ligne_qui_derive": ligne if tranche else None,
                    "cest_une_colonne_de_laile": bool(tranche) and ligne != int(tl["la_ligne"])})
    return verdict


# ── la procédure ─────────────────────────────────────────────────────────────────────────────────

def derouler(A: np.ndarray, lectures: Lectures, ctx: dict) -> dict:
    """La procédure entière sur ce que `lectures` sert : le journal, les boucles qui tiennent, ce qui est à lire."""
    A = np.asarray(A, dtype=bool)
    echelle = sorted(geo.LES_LARGEURS, reverse=True)
    k1, portee = echelle[0], int(ctx["portee"])
    tenues = {k: geo.les_tenues(A, k) for k in echelle}
    rect = geo.le_plus_grand_rectangle(A, k1)
    if rect is None:
        return {"le_rectangle": None, "le_journal": [], "les_boucles_qui_tiennent": [], "les_demandes": []}
    journal, tiennent, demandes = [], [], {}

    def _noter(j):
        for d in j.get("les_demandes") or []:
            demandes.setdefault(d["cle"], d)
    jr = juger(rect, "droite", k1, portee, tenues[k1], lectures, ctx)
    _noter(jr)
    journal.append({"la_boucle": "le rectangle", **jr})
    if jr["letat"] == "dessous":
        tiennent.append((list(rect), k1))
    for cote in geo.LES_COTES:
        a_voir, exclues, n = [geo.le_cote_entier(rect, cote)], [], 0
        while a_voir and n < LA_LIMITE_PAR_COTE:
            lo, hi = a_voir.pop(0)
            n += 1
            trouve = None
            for k in echelle:  # la plus large largeur à laquelle une aile tient
                co = geo.laile(A, geo.la_portion(rect, cote, lo, hi), cote, k, tenues[k], exclues=exclues)
                if co:
                    trouve = (k, [int(x) for x in co])
                    break
            e = {"la_boucle": "l'aile", "le_cote": cote, "la_portion": [int(lo), int(hi)],
                 "les_exclues": [list(x) for x in exclues]}
            if trouve is None:
                journal.append({**e, "letat": "aucune aile"})
                continue
            k, co = trouve
            j = juger(co, cote, k, portee, tenues[k], lectures, ctx)
            _noter(j)
            e.update(j)
            ya, yb = geo.lentre(cote, co)
            voisines = [(p, q) for p, q in ((lo, ya), (yb, hi)) if q > p]
            if j["letat"] == "dessous":
                tiennent.append((co, k))
                a_voir = voisines + a_voir
            elif j["letat"] == "franchit":
                dp = departager(A, co, cote, k, tenues[k], lectures, ctx)
                _noter(dp)
                e["le_departage"] = dp
                x = geo.lexterieure(cote, co)
                ligne = (dp.get("le_verdict") or {}).get("la_ligne_qui_derive")
                if dp["letat"] == "départagée" and ligne == x and [x, k] not in [list(y) for y in exclues]:
                    exclues.append((x, k))  # la bande extérieure dérive : on cherche la même portion sans elle
                    a_voir = [(lo, hi)] + a_voir
                else:
                    a_voir = voisines + a_voir
            else:
                a_voir = voisines + a_voir
            journal.append(e)
    return {"le_rectangle": list(rect), "le_journal": journal,
            "les_boucles_qui_tiennent": [{"les_coins": co, "la_largeur": int(k)} for co, k in tiennent],
            "les_demandes": sorted(demandes.values(), key=lambda d: (ce_quelle_coute(d), d["cle"]))}


# ── le masque, et le verdict ─────────────────────────────────────────────────────────────────────

ABSENT_DU_MASQUE, PRESENT, CERTIFIE = 0, 1, 2


def le_masque(A: np.ndarray, boucles) -> np.ndarray:
    """Par chunk : 0 absent du dépôt, 1 présent mais non certifié, 2 entouré par une boucle qui tient."""
    A = np.asarray(A, dtype=bool)
    M = np.zeros(A.shape, dtype=bool)
    for b in boucles:
        M |= geo.lentoure(A.shape, b["les_coins"], b["la_largeur"])
    out = np.where(A, PRESENT, ABSENT_DU_MASQUE).astype(np.uint8)
    out[A & M] = CERTIFIE
    return out


def certifier(A: np.ndarray, publiees: list[dict], ctx: dict, neuves: dict | None = None,
              sources: dict | None = None) -> dict:
    """La procédure sur ce qui est publié et lu. `ctx` : plus_long, graine, tirages, demi, portee.

    Les bandes neuves sont d'abord contrôlées contre la présence et contre ce qui est publié ; une bande
    qui ne retombe pas lève `LectureRefusee`, une bande qui ne croise rien reste non contrôlée.
    """
    A = np.asarray(A, dtype=bool)
    neuves = dict(neuves or {})
    ctx = dict(ctx)
    if neuves:
        la_presence_retombe(A, neuves)
        src = dict(sources or {})
        for i, x in enumerate(publiees):
            src[f"publiée {i}"] = une_source(x)
        ctx["non_controlees"] = les_non_controlees(neuves, src)
    r = derouler(A, Lectures(list(publiees) + list(neuves.values())), ctx)
    rect_juge = bool(r["le_journal"]) and r["le_journal"][0]["letat"] == "dessous"
    ailes = [b for b in r["les_boucles_qui_tiennent"] if b["les_coins"] != r["le_rectangle"]]
    return {**r, "ce_qui_reste_a_lire": sum(ce_quelle_coute(d) for d in r["les_demandes"]),
            "la_couverture": geo.la_couverture_des_boucles(A, [(b["les_coins"], b["la_largeur"])
                                                                for b in r["les_boucles_qui_tiennent"]]),
            "le_masque": le_masque(A, r["les_boucles_qui_tiennent"]),
            "les_ailes_autour_dun_rectangle_non_juge": (not rect_juge) and bool(ailes)}
