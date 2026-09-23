"""La colonne 71 porte-t-elle, dans sa moitié haute, une erreur que ses lignes partagent ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE LIGNE NOUVELLE NE SOIT LUE.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P74`. À toutes les largeurs de l'échelle de `218`, la colonne
de gauche du grand rectangle porte l'essentiel de sa fermeture (`228`) ; et `227` a montré que la moitié basse
de cette colonne, dans le quadrant en haut à gauche, est compensée par la colonne 106, pas la moitié haute :
la boucle fine en haut à gauche ferme à −23,8438 voxels. Une erreur que les lignes d'une bande partagent ne se
réduit par aucune largeur, c'est le piège de `208`, et elle ne se voit pas par le vote des lignes qui la
partagent. Il faut un chemin qui ne passe pas par elles.

## Le détour, dérivé

Les lignes de la colonne 71 sont toutes celles qui votent pour elle à une largeur de l'échelle de `218` :
de 67 à 75. Le détour est la bande de cinq lignes — la largeur de `219`, celle de chaque côté des boucles
fines de `227` — la plus proche de la colonne 71 dont AUCUNE ligne n'est une des siennes, ni une de celles
de la colonne 106. Il est cherché vers l'intérieur de la boucle fine, et c'est dérivé aussi : c'est le seul
côté où les trois autres côtés de la boucle étroite sont déjà lus, par la rangée 99 de `224`, la rangée 148
de `227` et la rangée 198 de `219`. Le détour est lu sur l'étendue du treillis fin de `227`, des rangées 99
à 198.

Le treillis du détour garde les rangées de `227` et coupe sa boucle fine de gauche par le détour : ses
colonnes sont 71, le détour, et 106. ⭐⭐ L'ANALYSE EST CELLE DE `224`, APPELÉE sur ce treillis. Sa boucle
en haut à gauche est LA BOUCLE ÉTROITE : la moitié haute de la colonne 71 d'un côté, la même moitié du
détour de l'autre, et entre elles quelques coutures des rangées 99 et 148.

## Ce qui contrôle

⚠⚠⚠ La lecture neuve croise les bandes publiées de `219`, `223`, `224`, `227` et `228` ; partout où deux
lectures lisent la même couture, elles retombent à l'arrondi, sur les mêmes coutures, sinon refus.
⚠⚠⚠ Recomposées sur ce treillis, les boucles fines de gauche de `227` — en haut et en bas — doivent retomber
EXACTEMENT sur les fermetures que `227` publie : c'est le même consensus, et sinon la tranche ne compare pas
ce qu'elle croit comparer. ⚠⚠ Un trou de majorité est franchi par la règle que `225` a retenue, lue dans sa
mesure — déclaré ici, avant la lecture, et non après comme en `227`.

## Ce qui se mesure, et le seul test déclaré

⭐⭐⭐⭐ UN SEUL TEST : la boucle étroite sort du bruit quand sa fermeture dépasse, en valeur absolue, celle de
demi-côtés tirés indépendamment par blocs (l'instrument de `224`) dans au moins `1 − 0,05` des tirages. La
garantie n'est pas partagée : la boucle étroite est la seule que `227` et `228` désignent AVANT cette lecture,
et les trois autres boucles du détour sont publiées, jamais testées. ⭐⭐⭐ L'ÉTALON DE CE TEST, celui de
`227` : sur des demi-côtés indépendants fabriqués — au `θ` dérivé, aux longueurs et aux dispersions lues —,
il ne doit faire sortir la boucle étroite qu'au taux de sa garantie, à deux écarts-types binomiaux près.

Publiés sans test : la fermeture de chaque boucle du détour et sa part du nul ; et la part de la fermeture de
la boucle fine en haut à gauche de `227` que porte la boucle étroite. ⚠ La boucle étroite en bas à gauche est
le témoin : c'est la moitié où `227` a trouvé la colonne 71 compensée.

## Les issues, exclusives

- l'étalon ne tient pas : le test ne désigne rien ;
- la boucle étroite sort du bruit : la moitié haute de la colonne 71 porte une erreur que le détour ne
  partage pas ;
- elle n'en sort pas : le détour ne sépare pas l'erreur de la colonne 71 de ce que le bruit ferait.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle désigne une RÉGION, pas un côté — la boucle étroite, c'est
aussi les quelques coutures des rangées 99 et 148 qui la ferment. Un détour qui s'accorde avec la colonne 71
ne dit pas qu'elle est juste : une erreur partagée au-delà de sept lignes le serait aussi par lui. Et le
piège de `219` vaut : une boucle qui désigne ne dit pas si c'est la matière ou la lecture qui se trompe.

Usage :
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_colonne_71.py --verifier
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_colonne_71.py --lire <lecture.json>
    uv run python src/nappe/un_detour_separe_t_il_lerreur_de_la_colonne_71.py --depuis <lecture.json> \\
        --json docs/mesures/un_detour_separe_t_il_lerreur_de_la_colonne_71.json
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
from deux_chemins_arrivent_ils_sur_la_meme_spire import (_la_definition, analyser,  # noqa: E402
                                                          ce_que_223_a_rendu, la_fermeture,
                                                          lautocorrelation_commune, lepreuve,
                                                          les_boucles_declarees, les_demi_cotes,
                                                          les_sommes, lire_les_bandes,
                                                          relire_une_bande)
from lajustement_de_toutes_les_boucles_garde_t_il_la_spire import ce_que_225_a_rendu  # noqa: E402
from le_consensus_traverse_t_il_la_rangee import (le_consensus,  # noqa: E402
                                                  le_theta_dune_autocorrelation)
from le_vote_ramene_t_il_les_rangees_sur_le_feuillet import ce_que_219_a_rendu  # noqa: E402
from lecart_extreme_est_il_porte_par_une_rangee import GARANTIE, LES_NOMBRES_DE_RANGEES  # noqa: E402
from ou_est_lerreur_de_la_boucle_en_haut_a_gauche import (la_reproduction_croisee,  # noqa: E402
                                                          le_domaine, le_seuil, le_treillis_fin,
                                                          les_boucles_qui_sortent,
                                                          les_pas_dune_bande, les_sources_publiees,
                                                          sur_letalon)
from quest_ce_qui_franchit_le_trou_de_majorite import (ce_que_224_a_rendu,  # noqa: E402
                                                       le_remplissage, les_trous_des_boucles)
from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_227_A_RENDU = MESURES / "ou_est_lerreur_de_la_boucle_en_haut_a_gauche.json"
CE_QUE_228_A_RENDU = MESURES / "une_bande_plus_large_ferme_t_elle_le_grand_rectangle.json"

LA_BOUCLE_ETROITE = "haut_gauche"
LE_TEMOIN = "bas_gauche"
LA_QUESTION_DECLAREE = ("la colonne 71 porte-t-elle, dans sa moitié haute, une erreur que ses lignes "
                        "partagent ?")
LA_MESURE_DECLAREE = ("la fermeture de la boucle étroite entre la moitié haute de la colonne 71 et un détour "
                      "dont aucune ligne n'est une des siennes, contre des demi-côtés tirés indépendamment ; "
                      "un seul test, au-delà de 1 − 0,05")


# ─────────────────────────────── ce que 227 et 228 ont publié ───────────────────────────────

def les_lectures_publiees(chemin: Path) -> dict:
    """Les bandes qu'une tranche a lues et publiées, relues — jamais relues au volume."""
    if not Path(chemin).exists():
        return {"decidable": False, "raison": f"{Path(chemin).name} est absent"}
    try:
        d = json.loads(Path(chemin).read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{Path(chemin).name} est illisible : {e}"}
    if not d.get("decidable") or not d.get("les_bandes"):
        return {"decidable": False, "raison": f"{Path(chemin).name} ne publie pas de bandes décidables"}
    return {"decidable": True, "brut": d, "relues": {k: relire_une_bande(x) for k, x in d["les_bandes"].items()}}


def ce_que_227_a_rendu(chemin: Path = CE_QUE_227_A_RENDU) -> dict:
    """Le treillis fin de `227`, ses deux bandes et les fermetures de ses boucles fines — relus."""
    lu = les_lectures_publiees(chemin)
    if not lu.get("decidable"):
        return lu
    d = lu["brut"]
    a = d.get("lanalyse_du_treillis_fin") or {}
    if not d.get("le_treillis_fin") or not a.get("les_boucles"):
        return {"decidable": False, "raison": "`227` ne publie pas son treillis fin ni ses boucles"}
    return {"decidable": True, "relues": lu["relues"],
            "Rf": [int(x) for x in d["le_treillis_fin"]["rangees"]],
            "Cf": [int(x) for x in d["le_treillis_fin"]["colonnes"]],
            "les_fermetures": {n: float(b["la_fermeture_en_voxels"]) for n, b in a["les_boucles"].items()
                               if b.get("fermable")}}


def les_sources(par219: dict, par223: dict, par224: dict, par227: dict, par228: dict) -> dict:
    """Toutes les lectures publiées, au format du contrôle : `219`, `223`, `224`, puis `227` et `228`."""
    out = les_sources_publiees(par219, par223, par224)
    for nom, par in (("227", par227), ("228", par228)):
        for k, rel in sorted(par["relues"].items()):
            out[f"{nom} {k}"] = {"domaine": le_domaine(rel["le_sens"], rel["les_lignes"], rel["de"], rel["a"]),
                                 "pas": les_pas_dune_bande(rel)}
    return out


# ─────────────────────────────── ce qui est dérivé ───────────────────────────────

def les_lignes_de_la_colonne(centre: int) -> set[int]:
    """Toutes les lignes qui votent pour une colonne à une largeur de l'échelle de `218`."""
    return set().union(*[set(les_rangees_a_lire(int(centre), int(k))) for k in LES_NOMBRES_DE_RANGEES])


def le_detour(depuis: int, vers: int, combien: int) -> int | None:
    """Le centre de la bande de `combien` lignes la plus proche de `depuis`, en allant vers `vers`, dont aucune
    ligne ne vote pour l'une ou l'autre colonne — ou rien, s'il n'y a pas la place entre elles."""
    interdites = les_lignes_de_la_colonne(depuis) | les_lignes_de_la_colonne(vers)
    pas_ = 1 if int(vers) > int(depuis) else -1
    for c in range(int(depuis) + pas_, int(vers), pas_):
        if not set(les_rangees_a_lire(c, combien)) & interdites:
            return int(c)
    return None


def le_treillis_du_detour(Rf, Cf, detour: int) -> tuple[list[int], list[int]]:
    """Les rangées du treillis fin, et ses colonnes de gauche coupées par le détour."""
    return [int(r) for r in Rf], [int(Cf[0]), int(detour), int(Cf[1])]


def la_bande_du_detour(Rf, detour: int, combien: int) -> dict:
    """La seule bande à lire : le détour, sur l'étendue du treillis fin — au format des bandes de `224`."""
    return {"cle": f"colonnes_{int(detour)}", "le_sens": "colonnes", "le_centre": int(detour),
            "les_lignes": les_rangees_a_lire(int(detour), int(combien)), "de": int(Rf[0]), "a": int(Rf[-1])}


def les_boucles_de_227(R, C) -> dict:
    """Les deux boucles fines de gauche de `227`, en coins, sur le treillis du détour."""
    return {"haut_gauche": (int(R[0]), int(R[1]), int(C[0]), int(C[2])),
            "bas_gauche": (int(R[1]), int(R[2]), int(C[0]), int(C[2]))}


# ─────────────────────────────── l'analyse ───────────────────────────────

def _ce_qui_reste(sort: bool, tient: bool) -> str:
    """Les trois issues, EXCLUSIVES — et un étalon qui ne tient pas prime."""
    if not tient:
        return "LE TEST NE TIENT PAS SA GARANTIE SUR SON ÉTALON : IL NE DÉSIGNE RIEN"
    if sort:
        return ("LA BOUCLE ÉTROITE SORT DU BRUIT : LA MOITIÉ HAUTE DE LA COLONNE 71 PORTE UNE ERREUR QUE LE "
                "DÉTOUR NE PARTAGE PAS")
    return ("LA BOUCLE ÉTROITE NE SORT PAS DU BRUIT : LE DÉTOUR NE SÉPARE PAS L'ERREUR DE LA COLONNE 71 DE CE QUE "
            "LE BRUIT FERAIT")


def analyser_le_detour(pas: dict, R, C, regle: str, graine: int, tirages: int, replicats: int,
                       garantie: float = GARANTIE, demi: float = DEMI_PAS_EN_VOXELS) -> dict:
    """Le treillis du détour, ses trous franchis par la règle de `225`, le test unique et son étalon — pur."""
    trous = les_trous_des_boucles(pas, R, C)
    rem = None
    if trous:
        rem = le_remplissage(regle, pas, trous)
        if rem is None:
            return {"decidable": False, "les_trous": trous,
                    "raison": f"la règle de `225`, {regle}, ne franchit pas les trous du treillis du détour"}
    a = analyser(pas, R, C, graine, tirages, replicats, False, demi, rem)
    if not a.get("decidable"):
        return {"decidable": False, "raison": f"l'analyse de `224` : {a.get('raison')}"}
    ouvertes = [n for n, b in a["les_boucles"].items() if not b.get("fermable")]
    if ouvertes:
        return {"decidable": False, "raison": f"des boucles du détour restent ouvertes : {ouvertes}"}
    cons = {k: le_consensus(p) for k, p in pas.items()}
    for k, v_ in (rem or {}).items():
        cons[k] = {**cons[k], **v_}
    dc = les_demi_cotes(R, C)
    sommes = les_sommes(cons, dc)
    recomposees = {n: round(float(la_fermeture(sommes, co, dc)), 4) for n, co in les_boucles_de_227(R, C).items()}
    pas_dc = {d: [float(cons[(d[0], d[1])][s]) for s in range(d[2], d[3])] for d in dc}
    # ⚠⚠ UN SEUL TEST : la boucle étroite, seule dans l'épreuve, donc à la garantie entière.
    ep = lepreuve(pas_dc, {LA_BOUCLE_ETROITE: les_boucles_declarees(R, C)[LA_BOUCLE_ETROITE]}, dc, tirages,
                  graine, garantie, demi)
    testees = {n: les_boucles_declarees(R, C)[n] for n in ep["les_rectangles"]}
    sort = les_boucles_qui_sortent(ep["par_rectangle"], garantie) == [LA_BOUCLE_ETROITE]
    theta = le_theta_dune_autocorrelation(lautocorrelation_commune(pas_dc.values()) or 0.0)
    et = sur_letalon({d: len(p) for d, p in pas_dc.items()}, {d: float(np.std(p)) for d, p in pas_dc.items()},
                     testees, dc, theta, replicats, tirages, graine, garantie)
    L = a["les_boucles"][LA_BOUCLE_ETROITE]["la_fermeture_en_voxels"]
    l227 = recomposees["haut_gauche"]
    return {"decidable": True, "le_treillis": {"rangees": [int(r) for r in R], "colonnes": [int(c) for c in C]},
            "lanalyse_du_treillis_du_detour": a, "les_boucles_de_227_recomposees": recomposees,
            "le_test": {"les_boucles_testees": sorted(testees),
                        "le_seuil": round(le_seuil(len(testees), garantie), 4),
                        "la_fermeture_en_voxels": L, **ep["par_rectangle"][LA_BOUCLE_ETROITE],
                        "elle_sort_du_bruit": bool(sort)},
            "letalon_du_test": {**et, "les_boucles_testees": sorted(testees)},
            "la_part_de_227_portee_par_la_boucle_etroite": (round(float(L) / l227, 4) if l227 else None),
            "le_verdict": {"la_boucle_etroite_sort_du_bruit": bool(sort),
                           "letalon_tient": bool(et["elle_tient_sa_garantie"]),
                           "ce_qui_reste_a_mesurer": _ce_qui_reste(sort, et["elle_tient_sa_garantie"])}}


# ─────────────────────────────── la mesure ───────────────────────────────

def _long(rel: dict) -> dict:
    return {int(a): {int(b): float(x[0]) for b, x in s.items()} for a, s in rel["le_long"].items()}


def mesurer(depuis: Path | None = None, par219: dict | None = None, par223: dict | None = None,
            par224: dict | None = None, par225: dict | None = None, par227: dict | None = None,
            par228: dict | None = None, lire=None, replicats: int | None = None,
            tirages: int | None = None) -> dict:
    """La lecture du détour puis l'analyse — ou l'analyse seule, rejouée."""
    par219 = ce_que_219_a_rendu() if par219 is None else par219
    par223 = ce_que_223_a_rendu() if par223 is None else par223
    par224 = ce_que_224_a_rendu() if par224 is None else par224
    par225 = ce_que_225_a_rendu() if par225 is None else par225
    par227 = ce_que_227_a_rendu() if par227 is None else par227
    par228 = les_lectures_publiees(CE_QUE_228_A_RENDU) if par228 is None else par228
    base = {"la_question_declaree": LA_QUESTION_DECLAREE, "la_mesure_declaree": LA_MESURE_DECLAREE}
    for nom, par in (("219", par219), ("223", par223), ("224", par224), ("225", par225), ("227", par227),
                     ("228", par228)):
        if not par.get("decidable"):
            return {**base, "decidable": False, "raison": f"`{nom}` : {par.get('raison')}"}
    Rf, Cf = par227["Rf"], par227["Cf"]
    if (Rf, Cf) != tuple(le_treillis_fin(par224["R"], par224["C"])):
        return {**base, "decidable": False, "raison": "le treillis publié par `227` n'est pas celui qu'il dérive de `224`"}
    combien = len(par219["les_rangees"])
    detour = le_detour(Cf[0], Cf[1], combien)
    if detour is None:
        return {**base, "decidable": False, "raison": "aucune bande de lignes libres entre les colonnes"}
    R, C = le_treillis_du_detour(Rf, Cf, detour)
    bande = la_bande_du_detour(Rf, detour, combien)
    g = par224["graine"]
    t_ = par224["tirages"] if tirages is None else int(tirages)
    rp_ = par224["replicats"] if replicats is None else int(replicats)
    if depuis is not None:
        lu = {"decidable": True, "les_bandes": json.loads(Path(depuis).read_text()).get("les_bandes") or {}}
    else:
        lu = lire_les_bandes([bande], lire=lire)
    base.update({"graine": int(g), "tirages": t_, "replicats": rp_, "la_regle_de_225": par225["la_regle"],
                 "les_lignes_de_la_colonne": sorted(les_lignes_de_la_colonne(Cf[0])),
                 "les_lignes_de_la_colonne_interieure": sorted(les_lignes_de_la_colonne(Cf[1])),
                 "le_detour": int(detour), "les_bandes_declarees": [bande],
                 "les_bandes": lu.get("les_bandes") or {}})
    if not lu.get("decidable"):
        return {**base, "decidable": False, "raison": lu.get("raison")}
    pub = lu["les_bandes"]
    if sorted(pub) != [bande["cle"]] or _la_definition(pub[bande["cle"]]) != _la_definition(bande):
        return {**base, "decidable": False, "raison": "la lecture n'est pas celle du détour dérivé"}
    relue = relire_une_bande(pub[bande["cle"]])
    nouvelles = {bande["cle"]: {"domaine": le_domaine("colonnes", bande["les_lignes"], bande["de"], bande["a"]),
                                "pas": les_pas_dune_bande(relue)}}
    rep = la_reproduction_croisee(nouvelles, les_sources(par219, par223, par224, par227, par228))
    if not rep.get("decidable"):
        return {**base, "decidable": False, "raison": rep.get("raison"), "la_reproduction": rep}
    pas = {("rangees", R[0]): _long(par224["relues"][f"rangees_{R[0]}"]),
           ("rangees", R[1]): _long(par227["relues"][f"rangees_{R[1]}"]),
           ("rangees", R[2]): par219["les_pas_par_rangee"],
           ("colonnes", C[0]): _long(par224["relues"][f"colonnes_{C[0]}"]),
           ("colonnes", C[1]): _long(relue),
           ("colonnes", C[2]): _long(par227["relues"][f"colonnes_{C[2]}"])}
    a = analyser_le_detour(pas, R, C, par225["la_regle"], g, t_, rp_)
    if not a.get("decidable"):
        return {**base, "decidable": False, "raison": a.get("raison"), "la_reproduction": rep}
    # ⚠⚠⚠ RECOMPOSÉES SUR CE TREILLIS, LES BOUCLES FINES DE GAUCHE RETOMBENT EXACTEMENT SUR `227`, ou refus.
    for n, L in a["les_boucles_de_227_recomposees"].items():
        if L != par227["les_fermetures"].get(n):
            return {**base, "decidable": False, "la_reproduction": rep,
                    "raison": f"la boucle fine {n} recomposée ({L}) ne retombe pas sur `227`"}
    return {**base, "decidable": True, "la_reproduction": rep,
            "les_fermetures_de_227": {n: par227["les_fermetures"][n] for n in les_boucles_de_227(R, C)}, **a}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    rp = r["la_reproduction"]
    print(f"détour : colonne {r['le_detour']} · reproduction {rp['combien_de_coutures_relues']} coutures "
          f"{rp['par_croisement']}, écart {rp['lecart_le_plus_grand']}")
    a = r["lanalyse_du_treillis_du_detour"]
    for k, c in a["la_couverture_du_consensus"].items():
        print(f"  {k} · {c['les_coutures_avec_consensus']}/{c['les_coutures_du_perimetre']} · sans "
              f"{c['les_coutures_sans_consensus'][:10]}")
    for n, b in a["les_boucles"].items():
        print(f"  {n} · L {b['la_fermeture_en_voxels']} · côtés {b['les_cotes_en_voxels']} · nul {b.get('le_nul')}")
    print(f"recomposées : {r['les_boucles_de_227_recomposees']} contre {r['les_fermetures_de_227']}")
    print(f"test : {r['le_test']}")
    t = r["letalon_du_test"]
    print(f"étalon : {t['combien_designent']}/{t['les_replicats']} = {t['le_taux']} (borne {t['la_borne']}, "
          f"θ {t['le_theta']})")
    print(f"part de 227 portée par la boucle étroite : {r['la_part_de_227_portee_par_la_boucle_etroite']}")
    print(f"VERDICT · {r['le_verdict']['ce_qui_reste_a_mesurer']}")


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

    # ── ce qui est dérivé
    v("★★★★ les lignes de la colonne 71 sont celles de toute l'échelle de 218, de 67 à 75",
      les_lignes_de_la_colonne(71) == set(range(67, 76)), str(sorted(les_lignes_de_la_colonne(71))))
    v("★★★★ le détour de 71 vers 106, à cinq lignes, est la colonne 78, de 76 à 80",
      le_detour(71, 106, 5) == 78 and les_rangees_a_lire(78, 5) == [76, 77, 78, 79, 80])
    v("★★★ le détour ne partage aucune ligne avec l'une ou l'autre colonne",
      not set(les_rangees_a_lire(le_detour(71, 106, 5), 5)) & (les_lignes_de_la_colonne(71)
                                                                | les_lignes_de_la_colonne(106)))
    v("★★★ le détour se cherche dans les deux sens : de 106 vers 71, la colonne 99",
      le_detour(106, 71, 5) == 99, str(le_detour(106, 71, 5)))
    v("★★★ sans la place entre deux colonnes, pas de détour", le_detour(71, 84, 5) is None
      and le_detour(71, 85, 5) == 78, str((le_detour(71, 84, 5), le_detour(71, 85, 5))))
    Rd, Cd = le_treillis_du_detour([99, 148, 198], [71, 106, 142], 78)
    v("★★★★ le treillis du détour garde les rangées de 227 et coupe sa boucle de gauche",
      Rd == [99, 148, 198] and Cd == [71, 78, 106], str((Rd, Cd)))
    bd = la_bande_du_detour([99, 148, 198], 78, 5)
    v("★★★★ une seule bande à lire, le détour, sur l'étendue du treillis fin",
      bd == {"cle": "colonnes_78", "le_sens": "colonnes", "le_centre": 78, "les_lignes": [76, 77, 78, 79, 80],
             "de": 99, "a": 198}, str(bd))
    v("★★★ les deux boucles fines de gauche de 227, sur ce treillis",
      les_boucles_de_227(Rd, Cd) == {"haut_gauche": (99, 148, 71, 106), "bas_gauche": (148, 198, 71, 106)})
    v("★★★★ un seul test, à la garantie entière", abs(le_seuil(1) - (1.0 - GARANTIE)) < 1e-12)
    iss = {_ce_qui_reste(x, y) for x in (True, False) for y in (True, False)}
    v("★★★★ trois issues distinctes, et un étalon qui ne tient pas prime",
      len(iss) == 3 and _ce_qui_reste(True, False) == _ce_qui_reste(False, False))

    # ── l'analyse, sur des pas fabriqués : une géométrie exacte et du bruit par ligne
    g = np.random.default_rng(11)
    R2, C2 = [0, 40, 80], [0, 12, 40]
    geo = {("rangees", 0): 0.2, ("rangees", 40): 0.2, ("rangees", 80): 0.2,
           ("colonnes", 0): 0.15, ("colonnes", 12): 0.15, ("colonnes", 40): 0.15}

    def _bandes(erreur: dict | None = None, sd: float = 1.0):  # noqa: E306
        out = {}
        for (sens, centre), x in geo.items():
            de, a_ = (C2[0], C2[2]) if sens == "rangees" else (R2[0], R2[2])
            out[(sens, centre)] = {l_: {s: x + float(g.normal(0.0, sd)) for s in range(de, a_)}
                                   for l_ in range(centre - 2, centre + 3)}
        for (sens, centre), (de, a_, e) in (erreur or {}).items():
            for l_ in out[(sens, centre)]:
                for s in range(de, a_):
                    out[(sens, centre)][l_][s] += e
        return out
    _bandes_a = _bandes()
    a = _sur(analyser_le_detour, _bandes_a, R2, C2, "le_maillage", 3, 199, 40)
    v("★★★ l'analyse est décidable sur des pas fabriqués", a.get("decidable"), str(a.get("raison")))
    v("★★★★ sans erreur, la boucle étroite ne sort pas du bruit",
      _ok(lambda: not a["le_test"]["elle_sort_du_bruit"]), str(a.get("le_test")))
    v("★★★★ recomposées, les boucles fines de gauche sont la somme de leurs deux boucles du détour",
      _ok(lambda: all(abs(a["les_boucles_de_227_recomposees"][n]
                          - a["lanalyse_du_treillis_du_detour"]["les_boucles"][g_]["la_fermeture_en_voxels"]
                          - a["lanalyse_du_treillis_du_detour"]["les_boucles"][d_]["la_fermeture_en_voxels"]) < 3e-4
                      for n, g_, d_ in (("haut_gauche", "haut_gauche", "haut_droite"),
                                        ("bas_gauche", "bas_gauche", "bas_droite")))))
    v("★★★ le test est celui de la boucle étroite dans l'épreuve de 224 : même nul, même part",
      _ok(lambda: a["le_test"]["la_part_du_nul_sous_la_fermeture"]
          == a["lanalyse_du_treillis_du_detour"]["lepreuve"]["par_rectangle"][LA_BOUCLE_ETROITE][
              "la_part_du_nul_sous_la_fermeture"]))
    v("★★★★ une seule boucle testée, la boucle étroite, au seuil de la garantie entière, étalon compris",
      _ok(lambda: a["le_test"]["les_boucles_testees"] == [LA_BOUCLE_ETROITE] and a["le_test"]["le_seuil"] == 0.95
          and a["letalon_du_test"]["les_boucles_testees"] == [LA_BOUCLE_ETROITE]), str(a.get("le_test")))
    v("★★★ l'étalon est tiré au θ dérivé des demi-côtés, franchis",
      _ok(lambda: a["letalon_du_test"]["le_theta"] == round(le_theta_dune_autocorrelation(lautocorrelation_commune(
          [[float(np.median([p[l_][s] for l_ in p])) for s in range(d[2], d[3])]
           for d in les_demi_cotes(R2, C2) for p in [_bandes_a[(d[0], d[1])]]])), 4)))
    v("★★★ l'étalon tient sur des pas indépendants",
      _ok(lambda: a["letalon_du_test"]["elle_tient_sa_garantie"]), str(a.get("letalon_du_test")))
    # ⚠ une erreur que les lignes de la colonne partagent, sur sa moitié haute : la boucle étroite la porte
    ah = _sur(analyser_le_detour, _bandes({("colonnes", 0): (0, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ une erreur partagée par les lignes de la colonne, en haut : la boucle étroite sort du bruit",
      _ok(lambda: ah["le_test"]["elle_sort_du_bruit"]
          and 0.8 < ah["la_part_de_227_portee_par_la_boucle_etroite"] < 1.2
          and abs(ah["la_part_de_227_portee_par_la_boucle_etroite"] - ah["le_test"]["la_fermeture_en_voxels"]
                  / ah["les_boucles_de_227_recomposees"]["haut_gauche"]) < 1e-3),
      str((ah.get("le_test"), ah.get("raison"))))
    v("★★★ ... et le témoin, en bas, ne la porte pas",
      _ok(lambda: abs(ah["lanalyse_du_treillis_du_detour"]["les_boucles"][LE_TEMOIN]["la_fermeture_en_voxels"])
          < 0.5 * abs(ah["le_test"]["la_fermeture_en_voxels"])))
    ap = _sur(analyser_le_detour, _bandes({("colonnes", 0): (0, 40, 0.6), ("colonnes", 12): (0, 40, 0.6)}, 0.25),
              R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ la même erreur, partagée par le détour : la boucle étroite ne la voit pas, l'autre la porte",
      _ok(lambda: not ap["le_test"]["elle_sort_du_bruit"]
          and ap["lanalyse_du_treillis_du_detour"]["les_boucles"]["haut_droite"]["la_fermeture_en_voxels"] < -12.0),
      str({n: x.get("la_fermeture_en_voxels") for n, x in (ap.get("lanalyse_du_treillis_du_detour") or {}).get("les_boucles", {}).items()}))
    ad = _sur(analyser_le_detour, _bandes({("colonnes", 40): (0, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3, 199, 40)
    v("★★★ la boucle étroite sort exactement quand sa part du nul atteint le seuil, et le verdict le suit",
      _ok(lambda: all(x["le_test"]["elle_sort_du_bruit"] == (x["le_test"]["la_part_du_nul_sous_la_fermeture"]
                                                               >= x["le_test"]["le_seuil"])
                      and x["le_verdict"]["ce_qui_reste_a_mesurer"]
                      == _ce_qui_reste(x["le_test"]["elle_sort_du_bruit"], x["letalon_du_test"]["elle_tient_sa_garantie"])
                      for x in (a, ah, ap, ad))))
    v("★★★ une erreur de la colonne intérieure : la boucle étroite n'en porte presque rien",
      _ok(lambda: not ad["le_test"]["elle_sort_du_bruit"]
          and abs(ad["la_part_de_227_portee_par_la_boucle_etroite"]) < 0.5), str(ad.get("le_test")))
    # ⚠ un étalon qui ne tient pas : le verdict ne désigne rien, même quand la boucle étroite sort
    vrai = globals()["sur_letalon"]
    globals()["sur_letalon"] = lambda *a_, **k_: {**vrai(*a_, **k_), "elle_tient_sa_garantie": False}
    try:
        af = _sur(analyser_le_detour, _bandes({("colonnes", 0): (0, 40, 0.6)}, 0.25), R2, C2, "le_maillage", 3,
                  199, 40)
    finally:
        globals()["sur_letalon"] = vrai
    v("★★★★ un étalon qui ne tient pas : le verdict ne désigne rien, même quand la boucle étroite sort",
      _ok(lambda: af["le_test"]["elle_sort_du_bruit"]
          and af["le_verdict"]["ce_qui_reste_a_mesurer"] == _ce_qui_reste(True, False)), str(af.get("le_verdict")))
    # un trou de majorité sur le détour est franchi par la règle de 225, et nommé avant le remplissage
    bt = _bandes()
    for l_ in (10, 11, 12):
        for s in (20, 21):
            del bt[("colonnes", 12)][l_][s]
    at = _sur(analyser_le_detour, bt, R2, C2, "le_maillage", 3, 199, 40)
    v("★★★★ un trou de majorité du détour est franchi par la règle de 225, et nommé",
      _ok(lambda: at["lanalyse_du_treillis_du_detour"]["la_couverture_du_consensus"]["colonnes_12"][
          "les_coutures_sans_consensus"] == [20, 21]
          and at["lanalyse_du_treillis_du_detour"]["les_coutures_remplies"] == {"colonnes_12": {"20": 0.0, "21": 0.0}}),
      str(at.get("raison")))
    bv = _bandes()
    for l_ in bv[("colonnes", 12)]:
        for s in (20, 21):
            del bv[("colonnes", 12)][l_][s]
    v("★★★ un trou que la règle ne franchit pas rend l'analyse indécidable, par sa raison",
      "ne franchit pas" in str(_sur(analyser_le_detour, bv, R2, C2, "les_lignes_presentes", 3, 199, 40).get("raison")))

    # ── la mesure, sur une lecture fabriquée qui retombe : copiée des sources là où elles lisent
    p219, p223, p224, p225 = ce_que_219_a_rendu(), ce_que_223_a_rendu(), ce_que_224_a_rendu(), ce_que_225_a_rendu()
    p227, p228 = ce_que_227_a_rendu(), les_lectures_publiees(CE_QUE_228_A_RENDU)
    v("★★★ 227 et 228 se relisent, et le treillis de 227 est celui qu'il dérive de 224",
      p227.get("decidable") and p228.get("decidable")
      and (p227["Rf"], p227["Cf"]) == tuple(le_treillis_fin(p224["R"], p224["C"])), str(p227.get("raison")))
    src = _sur(les_sources, p219, p223, p224, p227, p228)

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
        for (r, c), x in pas_["v"].items():
            ll.setdefault(c, {})[r] = (x, 0.0, 16)
        tt = {}
        for (r, c), x in pas_["h"].items():
            tt.setdefault(r, {})[c] = (x, 0.0, 16)
        return {"decidable": True, "le_long": ll, "en_travers": tt, "les_lectures": {}}
    m = _sur(mesurer, None, p219, p223, p224, p225, p227, p228, _fabrique, 20, 49)
    v("★★★★ une lecture fabriquée qui retombe passe la mesure entière, et les boucles de 227 retombent",
      m.get("decidable") and m.get("le_detour") == 78
      and m["les_boucles_de_227_recomposees"] == m["les_fermetures_de_227"]
      and m["la_reproduction"]["combien_de_coutures_relues"] > 0, str(m.get("raison")))
    v("★★★★ le détour est contrôlé par 224, 227 et 219, là où ils le croisent",
      _ok(lambda: {k.split("×")[1].split(" ")[0] for k in m["la_reproduction"]["par_croisement"]}
          >= {"224", "227", "219"}), str(m.get("la_reproduction")))
    faux227 = copy.deepcopy(p227)
    faux227["les_fermetures"]["haut_gauche"] += 1.0
    v("★★★★ une boucle fine de 227 qui ne retombe pas est refusée, par sa raison",
      "ne retombe pas sur `227`" in str(_sur(mesurer, None, p219, p223, p224, p225, faux227, p228,
                                             _fabrique, 20, 49).get("raison")))
    faux227b = copy.deepcopy(p227)
    faux227b["Cf"] = [71, 107, 142]
    v("★★★ un treillis de 227 qui n'est pas celui dérivé de 224 est refusé",
      "n'est pas celui" in str(_sur(mesurer, None, p219, p223, p224, p225, faux227b, p228,
                                    _fabrique, 20, 49).get("raison")))

    def _decale(b):  # noqa: E306
        x = _fabrique(b)
        for r, s in x["en_travers"].items():
            for c in s:
                s[c] = (s[c][0] + 1.0, 0.0, 16)
        return x
    v("★★★★ une lecture qui ne retombe pas sur ce qui est publié est refusée, par sa raison",
      "ne retombe pas" in str(_sur(mesurer, None, p219, p223, p224, p225, p227, p228, _decale, 20, 49).get("raison")))

    lu_juste = lire_les_bandes([la_bande_du_detour(p227["Rf"], 78, 5)], lire=_fabrique)
    v("★★★★ la mesure se rejoue à l'octet près depuis sa lecture publiée",
      _ok(lambda: json.dumps(_rejouer(lu_juste, p219, p223, p224, p225, p227, p228), ensure_ascii=False)
          == json.dumps(m, ensure_ascii=False)))

    def _ailleurs(b):  # noqa: E306
        return _fabrique({**b, "les_lignes": [x + 1 for x in b["les_lignes"]]})
    lu_ailleurs = lire_les_bandes([{**la_bande_du_detour(p227["Rf"], 78, 5), "les_lignes": [77, 78, 79, 80, 81]}],
                                  lire=_ailleurs)
    v("★★★ une lecture qui n'est pas celle du détour dérivé est refusée",
      "n'est pas celle du détour" in str(_sur(_rejouer, lu_ailleurs, p219, p223, p224, p225, p227, p228).get("raison")))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def _rejouer(lu: dict, *pars) -> dict:
    """La mesure rejouée depuis une lecture en mémoire, comme depuis un fichier."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"les_bandes": lu.get("les_bandes") or {}}, f)
        chemin = Path(f.name)
    try:
        return mesurer(chemin, *pars, replicats=20, tirages=49)
    finally:
        chemin.unlink()


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
        p219, p227 = ce_que_219_a_rendu(), ce_que_227_a_rendu()
        if not (p219.get("decidable") and p227.get("decidable")):
            print(f"indécidable : {p219.get('raison') or p227.get('raison')}")
            return 1
        combien = len(p219["les_rangees"])
        detour = le_detour(p227["Cf"][0], p227["Cf"][1], combien)
        if detour is None:
            print("indécidable : aucun détour")
            return 1
        bandes = [la_bande_du_detour(p227["Rf"], detour, combien)]
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
