"""Au-delà du quart de segment, l'ajustement de toutes les boucles à la fois garde-t-il deux chemins sur la même spire ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE MOINDRE AJUSTEMENT NE SOIT CALCULÉ SUR LA MATIÈRE. Rien n'est
regardé de neuf : les sommes et les fermetures sont celles que `224` et `225` publient.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P71`. `225` a trouvé la limite du consensus : un chemin de
consensus accumule son erreur comme une marche, et à l'échelle de la moitié du segment les deux chemins du
grand rectangle arrivent à un demi-feuillet l'un de l'autre. Ce qui ne s'accumule pas se cherche ; la porte
nomme un candidat et son piège.

## Le candidat : ajuster toutes les boucles à la fois

Les six bandes forment un treillis de neuf nœuds — les croisements des rangées 99, 198, 297 et des
colonnes 71, 142, 213 — et de douze demi-côtés. Chaque demi-côté porte une somme de pas du consensus, le
trou de `225` franchi par la règle que `225` a retenue. L'ajustement donne à chaque nœud la profondeur
qui accorde au mieux TOUS les demi-côtés à la fois, par moindres carrés, chacun pesé par l'inverse de la
variance de sa somme — la variance que les blocs de ses propres pas centrés lui donnent, l'instrument du nul
de `224`. Un chemin seul accumule l'erreur de ses côtés ; l'ajustement la moyenne sur tous les chemins.

## Le piège, et comment il est évité

⚠⚠⚠ UN AJUSTEMENT FERME LES BOUCLES PAR CONSTRUCTION : jugé sur les côtés qu'il a vus, il est parfait. Il
n'est donc jugé que sur des côtés qu'il n'a PAS vus — une validation croisée à deux échelles :

1. ⭐⭐⭐ LE QUART : chaque demi-côté est retiré, le treillis ajusté sans lui, et la profondeur prédite
   entre ses deux bouts est comparée à sa somme mesurée ;
2. ⭐⭐⭐⭐ LA MOITIÉ : chaque ligne entière — ses deux demi-côtés, 142 ou 198 coutures — est retirée de même.
   C'est l'échelle où `225` a vu les chemins arriver à un demi-feuillet l'un de l'autre.

Chaque erreur est comparée au demi-feuillet, et à celle d'UN SEUL DÉTOUR — la fermeture de la boucle qui
contient le côté retiré, puisqu'un détour se trompe exactement de la fermeture de sa boucle.

## Ce que le bruit seul donnerait

⭐⭐ Des sommes tirées indépendamment, demi-côté par demi-côté, depuis les blocs de leurs pas centrés, passent
par le MÊME ajustement : l'erreur est linéaire dans les sommes, donc son nul est exact pour chaque tirage.
Il dit ce que l'ajustement ferait si les côtés n'étaient que du bruit indépendant, et combien de fois ce
bruit seul resterait sous le demi-feuillet.

## Les issues, exclusives

- même ajusté, un côté retiré est prédit au-delà du demi-feuillet ;
- ajusté, tout côté retiré est prédit sous le demi-feuillet, là où un seul détour en laisse au-delà ;
- ajusté, tout côté retiré est prédit sous le demi-feuillet, comme par un seul détour.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : l'ajustement moyenne les erreurs propres des côtés ; une erreur
commune à une bande entière, il la répartit sans la retirer. Et un treillis de quatre boucles moyenne peu :
ce que donnerait un treillis dense n'est pas mesuré ici.

Usage :
    uv run python src/nappe/lajustement_de_toutes_les_boucles_garde_t_il_la_spire.py --verifier
    uv run python src/nappe/lajustement_de_toutes_les_boucles_garde_t_il_la_spire.py \\
        --json docs/mesures/lajustement_de_toutes_les_boucles_garde_t_il_la_spire.json
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

from deux_chemins_arrivent_ils_sur_la_meme_spire import (ce_que_223_a_rendu,  # noqa: E402
                                                          la_fermeture, les_boucles_declarees,
                                                          les_demi_cotes, les_pas_des_six_bandes,
                                                          les_sommes_par_blocs)
from le_consensus_traverse_t_il_la_rangee import le_consensus  # noqa: E402
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from quest_ce_qui_franchit_le_trou_de_majorite import ce_que_224_a_rendu  # noqa: E402
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_225_A_RENDU = MESURES / "quest_ce_qui_franchit_le_trou_de_majorite.json"

LA_QUESTION_DECLAREE = ("au-delà du quart de segment, l'ajustement de toutes les boucles à la fois garde-t-il "
                        "deux chemins sur la même spire ?")
LA_MESURE_DECLAREE = ("l'erreur de prédiction de chaque demi-côté et de chaque ligne entière, retirés du "
                      "treillis puis prédits par l'ajustement pondéré des autres, contre le demi-feuillet, "
                      "contre un seul détour, et contre des côtés de bruit indépendant")

LES_RECTANGLES_DE_MOITIE = {"la_moitie_haute": ("haut_gauche", "haut_droite"),
                            "la_moitie_basse": ("bas_gauche", "bas_droite"),
                            "la_moitie_gauche": ("haut_gauche", "bas_gauche"),
                            "la_moitie_droite": ("haut_droite", "bas_droite")}


# ─────────────────────────────── ce qui est relu ───────────────────────────────

def ce_que_225_a_rendu(chemin: Path = CE_QUE_225_A_RENDU) -> dict:
    """La règle retenue par `225`, les pas qu'elle a écrits, et les fermetures qu'elle a publiées."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable"):
        return {"decidable": False, "raison": "`225` est indécidable"}
    r = (d.get("le_verdict") or {}).get("la_regle")
    f = (d.get("les_franchissements") or {}).get(r) or {}
    if r is None or not f.get("les_coutures_remplies"):
        return {"decidable": False, "raison": "`225` ne publie ni sa règle ni ses pas écrits"}
    remplir = {}
    for k, v in f["les_coutures_remplies"].items():
        sens, centre = k.split("_")
        remplir[(sens, int(centre))] = {int(s): float(x) for s, x in v.items()}
    return {"decidable": True, "la_regle": r, "remplir": remplir,
            "les_fermetures": {n: b.get("la_fermeture_en_voxels") for n, b in f["les_boucles"].items()
                               if b.get("fermable")}}


# ─────────────────────────────── le treillis ───────────────────────────────

def le_treillis(R, C) -> dict:
    """Les douze demi-côtés, chacun `(queue, tête)` entre nœuds `(i, j)` — rangée `R[i]`, colonne `C[j]`.

    ⚠⚠ LE SENS EST CELUI DES PAS : une somme de pas le long d'une rangée va de la colonne de gauche à celle de
    droite, le long d'une colonne de la rangée du dessus à celle du dessous. Pris à l'envers, un demi-côté
    s'ajusterait contre les autres avec le signe faux.
    """
    out = {}
    for d in les_demi_cotes(R, C):
        sens, centre, de, a = d
        if sens == "rangees":
            i = list(R).index(centre)
            out[d] = ((i, list(C).index(de)), (i, list(C).index(a)))
        else:
            j = list(C).index(centre)
            out[d] = ((list(R).index(de), j), (list(R).index(a), j))
    return out


def les_coefficients(treillis: dict, poids: dict, retires, depart, arrivee) -> dict | None:
    """L'erreur de prédiction, écrite comme une combinaison LINÉAIRE des sommes des douze demi-côtés.

    Le treillis est ajusté sans les demi-côtés `retires`, par moindres carrés pondérés, la profondeur du
    nœud `(0, 0)` fixée à zéro ; la prédiction est la profondeur d'`arrivee` moins celle de `depart`, et
    l'erreur est la prédiction moins la somme mesurée des demi-côtés retirés. ⚠ Linéaire dans les sommes :
    c'est ce qui rend le nul exact, tirage par tirage. `None` si le treillis restant ne relie plus tout.
    """
    noeuds = sorted({n for q, t in treillis.values() for n in (q, t)})
    libres = [n for n in noeuds if n != (0, 0)]
    idx = {n: i for i, n in enumerate(libres)}
    gardes = [d for d in sorted(treillis) if d not in set(retires)]
    A = np.zeros((len(gardes), len(libres)))
    for r_, d in enumerate(gardes):
        q, t = treillis[d]
        sw = float(np.sqrt(poids[d]))
        if t in idx:
            A[r_, idx[t]] += sw
        if q in idx:
            A[r_, idx[q]] -= sw
    if np.linalg.matrix_rank(A) < len(libres):
        return None
    W = np.diag([float(np.sqrt(poids[d])) for d in gardes])
    H = np.linalg.pinv(A) @ W
    v = np.zeros(len(libres))
    if arrivee in idx:
        v[idx[arrivee]] += 1.0
    if depart in idx:
        v[idx[depart]] -= 1.0
    c = {d: 0.0 for d in treillis}
    for r_, d in enumerate(gardes):
        c[d] = float(v @ H[:, r_])
    for d in retires:
        c[d] -= 1.0
    return c


def lerreur(coefs: dict, sommes: dict):
    """L'erreur que des coefficients donnent sur des sommes — nombres ou tableaux de tirages."""
    return sum(coefs[d] * sommes[d] for d in sorted(coefs))


def les_cas(R, C) -> dict:
    """Les côtés retirés à chaque échelle : chaque demi-côté, puis chaque ligne entière."""
    tr = le_treillis(R, C)
    demi = {f"{d[0]}_{d[1]}_{d[2]}_{d[3]}": {"retires": [d], "depart": tr[d][0], "arrivee": tr[d][1]}
            for d in sorted(tr)}
    lignes = {}
    for i, r in enumerate(R):
        lignes[f"rangees_{r}"] = {"retires": [d for d in tr if d[0] == "rangees" and d[1] == r],
                                  "depart": (i, 0), "arrivee": (i, 2)}
    for j, c in enumerate(C):
        lignes[f"colonnes_{c}"] = {"retires": [d for d in tr if d[0] == "colonnes" and d[1] == c],
                                   "depart": (0, j), "arrivee": (2, j)}
    return {"le_quart": demi, "la_moitie": lignes}


def les_detours(R, C, fermetures: dict) -> dict:
    """L'erreur d'un seul détour, cas par cas : la fermeture de chaque boucle qui contient le côté retiré.

    ⚠ Un détour prédit un côté par les trois autres de sa boucle, donc il se trompe exactement de la
    fermeture de cette boucle, au signe près — le signe n'importe pas contre le demi-feuillet.
    """
    decl = les_boucles_declarees(R, C)
    ferm = dict(fermetures)
    for n, (a, b) in LES_RECTANGLES_DE_MOITIE.items():
        if a in ferm and b in ferm:
            ferm[n] = float(ferm[a]) + float(ferm[b])
    moities = {"la_moitie_haute": (R[0], R[1], C[0], C[2]), "la_moitie_basse": (R[1], R[2], C[0], C[2]),
               "la_moitie_gauche": (R[0], R[2], C[0], C[1]), "la_moitie_droite": (R[0], R[2], C[1], C[2])}

    def _contient(coins, retires):  # noqa: E306
        r0, r1, c0, c1 = coins
        cotes = {("rangees", r0, c0, c1), ("colonnes", c1, r0, r1), ("rangees", r1, c0, c1),
                 ("colonnes", c0, r0, r1)}
        for sens, centre, de, a in retires:
            if not any(s == sens and ce == centre and d0 <= de and a <= a0 for s, ce, d0, a0 in cotes):
                return False
        return True
    out = {"le_quart": {}, "la_moitie": {}}
    cas = les_cas(R, C)
    for echelle in cas:
        for nom, x in cas[echelle].items():
            boites = ({n: c for n, c in decl.items() if n != "le_grand_rectangle"} if echelle == "le_quart"
                      else {**moities, "le_grand_rectangle": decl["le_grand_rectangle"]})
            out[echelle][nom] = {n: round(float(ferm[n]), 4) for n, c in sorted(boites.items())
                                 if n in ferm and _contient(c, x["retires"])}
    return out


# ─────────────────────────────── la mesure ───────────────────────────────

def _ce_qui_reste(ajuste_depasse: bool, un_detour_depasse: bool) -> str:
    """Les trois issues, EXCLUSIVES — et dépasser après l'ajustement prime."""
    if ajuste_depasse:
        return "MÊME AJUSTÉES TOUTES ENSEMBLE, LES BOUCLES PRÉDISENT UN CÔTÉ RETIRÉ AU-DELÀ DU DEMI-FEUILLET"
    if un_detour_depasse:
        return ("L'AJUSTEMENT DE TOUTES LES BOUCLES PRÉDIT CHAQUE CÔTÉ RETIRÉ SOUS LE DEMI-FEUILLET, LÀ OÙ UN "
                "SEUL DÉTOUR LE PERD")
    return ("L'AJUSTEMENT DE TOUTES LES BOUCLES PRÉDIT CHAQUE CÔTÉ RETIRÉ SOUS LE DEMI-FEUILLET, COMME UN "
            "SEUL DÉTOUR")


def analyser(sommes: dict, pas_des_demi_cotes: dict, R, C, fermetures: dict, graine: int, tirages: int,
             demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Tout ce qui se calcule sur les douze sommes — pur."""
    tr = le_treillis(R, C)
    if set(sommes) != set(tr) or any(sommes[d] is None for d in tr):
        return {"decidable": False, "raison": "un demi-côté du treillis n'a pas de somme"}
    # ⚠ LES TIRAGES DU NUL SONT CEUX DE 224, graine par graine, dans le même ordre des demi-côtés.
    nul = {d: les_sommes_par_blocs(p, tirages, int(graine) + 101 * i)
           for i, (d, p) in enumerate(sorted(pas_des_demi_cotes.items()))}
    variances = {d: float(np.var(nul[d])) for d in tr}
    if any(v <= 0.0 for v in variances.values()):
        return {"decidable": False, "raison": "un demi-côté n'a aucune variance à peser"}
    poids = {d: 1.0 / variances[d] for d in tr}
    detours = les_detours(R, C, fermetures)
    out, pire_ajuste, pire_detour = {}, 0.0, 0.0
    for echelle, cas in les_cas(R, C).items():
        out[echelle] = {}
        for nom, x in cas.items():
            c = les_coefficients(tr, poids, x["retires"], x["depart"], x["arrivee"])
            if c is None:
                return {"decidable": False, "raison": f"retirer {nom} coupe le treillis"}
            e = float(lerreur(c, sommes))
            en = np.abs(np.asarray(lerreur(c, nul), dtype=float))
            det = detours[echelle][nom]
            pire_ajuste = max(pire_ajuste, abs(e))
            if det:
                pire_detour = max(pire_detour, max(abs(v) for v in det.values()))
            out[echelle][nom] = {
                "les_coutures": int(sum(d[3] - d[2] for d in x["retires"])),
                "la_somme_mesuree_en_voxels": round(float(sum(sommes[d] for d in x["retires"])), 4),
                "lerreur_ajustee_en_voxels": round(e, 4),
                "sous_le_demi_pli": bool(abs(e) < float(demi)),
                "les_detours_en_voxels": det,
                "le_nul": {"lerreur_mediane_en_valeur_absolue": round(float(np.median(en)), 4),
                           "la_part_sous_le_demi_pli": round(float(np.mean(en < float(demi))), 4)}}
    depasse = any(not x["sous_le_demi_pli"] for e_ in out.values() for x in e_.values())
    un_detour = any(abs(v) >= float(demi) for e_ in detours.values() for dd in e_.values() for v in dd.values())
    return {"decidable": True, "le_demi_pli_en_voxels": int(demi),
            "les_demi_cotes": {f"{d[0]}_{d[1]}_{d[2]}_{d[3]}": {
                "de": list(tr[d][0]), "a": list(tr[d][1]), "la_somme_en_voxels": round(float(sommes[d]), 4),
                "la_variance_de_la_somme": round(variances[d], 4)} for d in sorted(tr)},
            "la_validation_croisee": out,
            "le_verdict": {"la_plus_grande_erreur_ajustee_en_valeur_absolue": round(pire_ajuste, 4),
                           "le_plus_grand_detour_en_valeur_absolue": round(pire_detour, 4),
                           "un_cote_ajuste_depasse": bool(depasse), "un_detour_depasse": bool(un_detour),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(depasse, un_detour)}}


def mesurer(par219: dict | None = None, par223: dict | None = None, par224: dict | None = None,
            par225: dict | None = None, tirages: int | None = None) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    R, C = par224["R"], par224["C"]
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    pas = les_pas_des_six_bandes(par219, par223, par224["relues"], par224["bandes"], R, C)
    cons = {k: le_consensus(p) for k, p in pas.items()}
    for k, v in par225["remplir"].items():
        if any(s in cons[k] for s in v):
            return {**base, "decidable": False, "raison": "`225` a écrit un pas là où un consensus existe"}
        cons[k] = {**cons[k], **v}
    tr = le_treillis(R, C)
    pas_dc = {d: [float(cons[(d[0], d[1])][s]) for s in range(d[2], d[3])] for d in tr
              if all(s in cons[(d[0], d[1])] for s in range(d[2], d[3]))}
    if set(pas_dc) != set(tr):
        return {**base, "decidable": False, "raison": "un demi-côté reste troué après le trou franchi"}
    sommes = {d: float(sum(pas_dc[d])) for d in tr}
    # ⚠⚠ D'ABORD, LES FERMETURES DE 225 REJOUÉES DEPUIS CES SOMMES : sinon ce n'est pas le même treillis.
    decl = les_boucles_declarees(R, C)
    for n, L in par225["les_fermetures"].items():
        x = la_fermeture(sommes, decl[n], les_demi_cotes(R, C))
        if x is None or round(float(x), 4) != float(L):
            return {**base, "decidable": False,
                    "raison": f"les sommes ne retombent pas sur la fermeture de {n} que `225` publie"}
    base.update({"graine": int(g), "tirages": int(t_), "la_regle_de_225": par225["la_regle"],
                 "la_reproduction_de_225": {"decidable": True, "les_boucles": len(par225["les_fermetures"])}})
    a = analyser(sommes, pas_dc, R, C, par225["les_fermetures"], g, t_)
    return {**base, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    print(f"225 rejoué : {r['la_reproduction_de_225']} · règle {r['la_regle_de_225']}")
    for echelle, cas in r["la_validation_croisee"].items():
        print(f"── {echelle}")
        for nom, x in cas.items():
            print(f"  {nom} · {x['les_coutures']} coutures · mesuré {x['la_somme_mesuree_en_voxels']} · ajusté "
                  f"{x['lerreur_ajustee_en_voxels']} · détours {x['les_detours_en_voxels']} · nul "
                  f"{x['le_nul']['lerreur_mediane_en_valeur_absolue']} ({x['le_nul']['la_part_sous_le_demi_pli']})")
    print(f"VERDICT · {r['le_verdict']}")


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

    R, C = [2, 5, 8], [1, 4, 7]
    tr = le_treillis(R, C)
    v("★★★★ douze demi-côtés, dans le sens des pas, entre les neuf nœuds",
      len(tr) == 12 and tr[("rangees", 5, 1, 4)] == ((1, 0), (1, 1))
      and tr[("colonnes", 7, 5, 8)] == ((1, 2), (2, 2)), str(list(tr.items())[:2]))
    g = np.random.default_rng(7)
    D = {(i, j): float(g.normal(0.0, 20.0)) for i in range(3) for j in range(3)}
    geo = {d: D[t] - D[q] for d, (q, t) in tr.items()}
    un = {d: 1.0 for d in tr}
    cas = les_cas(R, C)
    v("★★★ douze demi-côtés au quart, six lignes entières à la moitié",
      len(cas["le_quart"]) == 12 and len(cas["la_moitie"]) == 6
      and all(len(x["retires"]) == 2 for x in cas["la_moitie"].values()))

    def _err(sommes, poids, x):  # noqa: E306
        c = les_coefficients(tr, poids, x["retires"], x["depart"], x["arrivee"])
        return lerreur(c, sommes)
    v("★★★★ sur une géométrie, tout côté retiré est prédit EXACTEMENT, à toute échelle",
      _ok(lambda: all(abs(_err(geo, un, x)) < 1e-9 for e_ in cas.values() for x in e_.values())))
    faux = dict(geo)
    faux[("rangees", 2, 1, 4)] += 12.0
    x0 = cas["le_quart"]["rangees_2_1_4"]
    v("★★★★ un côté retiré qui porte seul une erreur est prédit à cette erreur près, au signe près",
      _ok(lambda: abs(_err(faux, un, x0) + 12.0) < 1e-9))
    x1 = cas["le_quart"]["rangees_5_1_4"]
    v("★★★★ et l'erreur d'un autre côté se répartit : l'ajustement la dilue sans l'effacer",
      _ok(lambda: 0.0 < abs(_err(faux, un, x1)) < 12.0))
    lourd = dict(un)
    lourd[("rangees", 2, 1, 4)] = 1e-6
    v("★★★★ le poids compte : un côté presque sans poids ne tire plus l'ajustement",
      _ok(lambda: abs(_err(faux, lourd, x1)) < 1e-3))
    v("★★★ un treillis coupé en deux ne prédit rien",
      les_coefficients(tr, un, [d for d in tr if d[0] == "colonnes" and d[1] == 4]
                       + [("rangees", 2, 4, 7), ("rangees", 5, 4, 7), ("rangees", 8, 4, 7)], (0, 0), (0, 2)) is None)
    c = les_coefficients(tr, un, x0["retires"], x0["depart"], x0["arrivee"])
    arr = {d: np.asarray([geo[d], 2 * geo[d]]) for d in tr}
    v("★★★ l'erreur est linéaire dans les sommes, donc le nul se calcule tirage par tirage",
      _ok(lambda: np.allclose(lerreur(c, arr), [0.0, 0.0])))

    ferm = {"haut_gauche": -3.0, "haut_droite": 5.0, "bas_gauche": 2.0, "bas_droite": -1.0,
            "le_grand_rectangle": 3.0}
    det = les_detours(R, C, ferm)
    v("★★★★ un demi-côté du bord n'a qu'une boucle pour détour, un demi-côté de la croix en a deux",
      det["le_quart"]["rangees_2_1_4"] == {"haut_gauche": -3.0}
      and det["le_quart"]["rangees_5_1_4"] == {"bas_gauche": 2.0, "haut_gauche": -3.0}, str(det["le_quart"]))
    v("★★★★ une ligne du bord a pour détours sa moitié et le grand rectangle, une ligne de la croix ses deux "
      "moitiés", det["la_moitie"]["rangees_2"] == {"la_moitie_haute": 2.0, "le_grand_rectangle": 3.0}
      and det["la_moitie"]["colonnes_4"] == {"la_moitie_droite": 4.0, "la_moitie_gauche": -1.0},
      str(det["la_moitie"]))
    from deux_chemins_arrivent_ils_sur_la_meme_spire import les_cotes

    def _par_le_detour(sommes, coins, nom_du_cote):  # noqa: E306
        cotes = les_cotes(coins)
        x = next(c_ for c_ in cotes if c_[5] == nom_du_cote)
        autres = sum(c_[4] * sommes[c_[:4]] for c_ in cotes if c_[5] != nom_du_cote)
        return -x[4] * autres - sommes[x[:4]]
    hg = les_boucles_declarees(R, C)["haut_gauche"]
    L_hg = float(la_fermeture(faux, hg, les_demi_cotes(R, C)))
    v("★★★★ l'erreur d'un détour est la fermeture de sa boucle : prédit par les trois autres côtés",
      _ok(lambda: abs(abs(_par_le_detour(faux, hg, "haut")) - abs(L_hg)) < 1e-9 and abs(abs(L_hg) - 12.0) < 1e-9
          and abs(abs(_par_le_detour(faux, hg, "gauche")) - abs(L_hg)) < 1e-9))

    # l'analyse sur des pas fabriqués
    pas_dc = {d: list(g.normal(0.0, 1.0, d[3] - d[2])) for d in les_demi_cotes(R, C)}
    s_ = {d: float(sum(p)) for d, p in pas_dc.items()}
    fm = {n: float(la_fermeture(s_, c_, les_demi_cotes(R, C))) for n, c_ in les_boucles_declarees(R, C).items()}
    a = _sur(analyser, s_, pas_dc, R, C, fm, 3, 199)
    v("★★★ l'analyse est décidable", a.get("decidable"), str(a.get("raison")))
    v("★★★★ chaque cas porte son erreur ajustée, ses détours et le nul", _ok(lambda: all(
        {"lerreur_ajustee_en_voxels", "les_detours_en_voxels", "le_nul"} <= set(x)
        for e_ in a["la_validation_croisee"].values() for x in e_.values())))
    v("★★★ les poids sont l'inverse de la variance des sommes tirées par blocs",
      _ok(lambda: all(abs(a["les_demi_cotes"][f"{d[0]}_{d[1]}_{d[2]}_{d[3]}"]["la_variance_de_la_somme"]
                          - round(float(np.var(les_sommes_par_blocs(pas_dc[d], 199, 3 + 101 * i))), 4)) < 1e-9
                      for i, d in enumerate(sorted(pas_dc)))))
    def _pese():  # noqa: E306
        var = {d: float(np.var(les_sommes_par_blocs(pas_dc[d], 199, 3 + 101 * i)))
               for i, d in enumerate(sorted(pas_dc))}
        x_ = les_cas(R, C)["le_quart"]["rangees_5_1_4"]
        c_ = les_coefficients(tr, {d: 1.0 / var[d] for d in tr}, x_["retires"], x_["depart"], x_["arrivee"])
        return abs(a["la_validation_croisee"]["le_quart"]["rangees_5_1_4"]["lerreur_ajustee_en_voxels"]
                   - round(float(lerreur(c_, s_)), 4)) < 1e-9
    v("★★★★ l'ajustement pèse chaque demi-côté par l'INVERSE de la variance de sa somme", _ok(_pese))
    geo50 = dict(geo)
    geo50[("rangees", 2, 1, 4)] += 50.0
    fm50 = {n: float(la_fermeture(geo50, c_, les_demi_cotes(R, C))) for n, c_ in les_boucles_declarees(R, C).items()}
    a50 = _sur(analyser, geo50, pas_dc, R, C, fm50, 3, 199)
    v("★★★★ une erreur entre le demi-feuillet et le feuillet entier est au-delà, et le verdict le dit",
      _ok(lambda: abs(a50["la_validation_croisee"]["le_quart"]["rangees_2_1_4"]["lerreur_ajustee_en_voxels"] + 50.0)
          < 1e-6 and not a50["la_validation_croisee"]["le_quart"]["rangees_2_1_4"]["sous_le_demi_pli"]
          and a50["le_verdict"]["un_cote_ajuste_depasse"]
          and "MÊME AJUSTÉES" in a50["le_verdict"]["ce_qui_reste_a_mesurer"]))
    v("★★ un demi-côté sans somme rend l'analyse indécidable",
      not _sur(analyser, {**s_, ("rangees", 2, 1, 4): None}, pas_dc, R, C, fm, 3, 19).get("decidable"))
    iss = {_ce_qui_reste(x, y) for x in (True, False) for y in (True, False)}
    v("★★★★ trois issues distinctes, et dépasser après l'ajustement prime",
      len(iss) == 3 and _ce_qui_reste(True, False) == _ce_qui_reste(True, True))

    # la mesure entière, sur la matière publiée
    m = _sur(mesurer, None, None, None, None, 49)
    v("★★★★ la mesure entière est décidable et rejoue d'abord les fermetures de 225",
      m.get("decidable") and m["la_reproduction_de_225"]["les_boucles"] == 5, str(m.get("raison")))
    p225 = ce_que_225_a_rendu()
    faux225 = copy.deepcopy(p225)
    faux225["les_fermetures"]["bas_droite"] = float(faux225["les_fermetures"]["bas_droite"]) + 1.0
    v("★★★★ des sommes qui ne retombent pas sur les fermetures de 225 sont refusées, par leur raison",
      "ne retombent pas" in str(_sur(mesurer, None, None, None, faux225, 49).get("raison")))
    faux225b = copy.deepcopy(p225)
    faux225b["remplir"] = {("colonnes", 213): {139: 0.0}}
    v("★★★ un pas de 225 écrit là où un consensus existe est refusé",
      "consensus existe" in str(_sur(mesurer, None, None, None, faux225b, 49).get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
