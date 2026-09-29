"""Sur les graines 4 à 8 de PHercParis4, où les tours publiés ne se recouvrent presque pas, le critère sans référent de 328 sépare-t-il les sauts que la lecture stricte dit justes de ceux qu'elle dit faux ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE CRITÈRE DE `328` NE SOIT LU SUR UN SEUL SAUT D'UNE CHAÎNE RELANCÉE DE PHERCPARIS4. Ce qui était vu avant
d'écrire : tout ce que `296` à `343` publient, dont `R4-F513` (la tenue par côté de la chaîne sans relance, et aucune spire des deux
rouleaux dans un bloc de `m7`), `R4-F522` (`5753_-7` est décalé là où les chaînes l'attendent), `R4-F526` (les descentes strictes),
`R4-F527` et `R4-F529` (autour des graines 1 à 3, le référent se trompe de feuille), et les lectures que `330`, `331`, `333` et `336`
publient pour chaque surface : sur les graines 4 à 8, côté moins, une centaine de sauts vont d'un seul tour au suivant, et moins d'une
dizaine vont ailleurs.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P140`, LA QUESTION DE `#5`. Sur PHerc0358, qui n'a pas de tracé, une chaîne ne se juge que
par un critère qui se passe de référent : celui de `328`, un saut qui pose au pas et dont la surface n'est pas posée dans un bloc de `m7`.
Là où le référent de PHercParis4 est propre, il peut étalonner ce critère ; s'il dit tenir les sauts que le référent dit justes et pas les
autres, il vaut pour PHerc0358.

## Ce qui est fait

- **Les chaînes** : les quatre que `340` a jugées strictement, rejouées sur PHercParis4 sans en changer une règle : sans relance (`330`),
  relancée depuis un point (`331`), relancée depuis la spire (`333`), bornée (`335`, que `336` redonne). Leurs lectures rejouées doivent
  redonner, surface par surface, celles que chaque tranche publie, et la tenue de la chaîne sans relance celle que `328` publie sur ses 14
  côtés, sans quoi la tranche est indécidable.
- **Le critère sans référent**, saut par saut, celui de `328` : le saut pose au pas (la règle de `324` : au moins 10 % du plan, pas médian
  entre un demi-pas et un pas et demi) et la surface qu'il donne n'est pas posée dans un bloc de `m7` (la règle de `326`) ; cette surface
  est la spire pour la chaîne sans relance, la nappe relancée pour les trois autres, comme `331` le fait sur PHerc0358. Un saut sans nappe
  relancée ne tient pas.
- **La lecture stricte d'un saut**, de la surface qui le précède à celle qu'il donne, la nappe en tête : si la première retrouve un seul
  tour w, le tour attendu est son voisin du côté du saut, w − 1 côté moins et w + 1 côté plus, dans le sens où `330` voit les chaînes
  descendre. Le saut est **juste** si la seconde retrouve ce seul tour ; **faux** si elle le retrouve avec un autre (deux tours), si elle
  en retrouve un autre sans lui (un autre tour), ou si elle ne retrouve rien alors que le tour attendu est lu en face d'elle (le tour
  manqué). Il n'est **pas jugé** si la surface qui précède ne retrouve pas un seul tour, si le tour attendu n'est pas lu, ou s'il n'est pas
  entre `5753_0` et `5753_-6` : `5753_-7` est décalé là où les chaînes l'attendent (`R4-F522`).
- **Les graines** : les sauts des graines 4 à 8 décident, où les tours publiés voisins se recouvrent sur 0 à 15 % de leurs sommets
  (`R4-F527`) ; ceux des graines 1 à 3, où le référent se trompe de feuille (`R4-F529`), sont rapportés à côté.

## Les issues

Sur les sauts jugés des quatre chaînes, graines 4 à 8, la part tj des sauts justes que le critère dit tenir et la part tf des sauts faux.
L'issue : **sur les graines 4 à 8, le critère sans référent dit tenir a des nj sauts justes et b des nf sauts faux** ; et, déclaré avant :
**il les sépare** si tj ≥ 0,75 et tf ≤ 0,25 ; **il ne les sépare pas** si tj − tf < 0,25 ; **il ne les sépare qu'en partie** sinon.
Indécidable s'il y a moins de 5 sauts justes ou moins de 5 sauts faux jugés.

## Rapporté à côté, qui ne décide rien

Le même compte chaîne par chaîne et sur les graines 1 à 3 ; la part des sauts que le critère dit tenir qui sont justes ; pour chaque saut
faux, sa raison, la part posée, le pas médian et la plage de `m7` ; et les sauts que le référent ne juge pas, avec ce qu'en dit le critère.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut le critère sur PHerc0358, où ni la matière ni `m7` ne sont celles de PHercParis4 ; et,
les quatre chaînes partant des mêmes nappes, ses sauts ne sont pas indépendants d'une chaîne à l'autre.

Usage :
    uv run python src/nappe/le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.py --verifier
    uv run python src/nappe/le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.py \\
        --json docs/mesures/le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import la_chaine_dune_seule_feuille_suit_elle_sa_feuille_sur_quatre_spires as m306  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas as m328  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402
import la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse as m335  # noqa: E402
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_328_A_PUBLIE = LES_MESURES / "combien_de_sauts_la_chaine_qui_croit_tient_elle_au_pas.json"
LES_GRAINES_PROPRES = (4, 5, 6, 7, 8)
LES_TOURS_JUGES = tuple(range(0, -7, -1))          # 5753_0 à 5753_-6 ; 5753_-7 est décalé (R4-F522)
LE_SENS = {"plus": 1, "moins": -1}
LA_TENUE_DES_JUSTES, LA_TENUE_DES_FAUX, LECART_MINIMAL = 0.75, 0.25, 0.25
LE_MINIMUM = 5
LES_CLES_DE_LA_TENUE = ("la_part_du_plan", "le_pas_median_en_pas", "pose_au_pas", "la_plage_en_pas", "tient")
LES_RELANCES = {
    "relancée depuis un point": (lambda lv: (lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv)), False),
    "relancée depuis la spire": (lambda lv: (lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lv)), True),
    "bornée": (m335.la_relance_de_paris4, True),
}


def la_justesse(avant: dict, apres: dict, sens: int) -> str:
    """Ce que la lecture stricte dit d'un saut de la surface `avant` à la surface `apres`, chacune comme {tour : lecture}, du côté `sens`."""
    r0 = m340.les_retrouves(avant)
    if len(r0) != 1:
        return "non jugé"
    attendu = r0[0] + sens
    if attendu not in LES_TOURS_JUGES:
        return "non jugé"
    r1 = m340.les_retrouves(apres)
    if r1 == [attendu]:
        return "juste"
    if attendu in r1:
        return "faux : deux tours"
    if r1:
        return "faux : un autre tour"
    lu = {int(t): x for t, x in apres.items()}.get(attendu)
    return "faux : le tour manqué" if lu == "ne retrouve pas" else "non jugé"


def les_sauts(surfaces: list[dict], tenues: list[dict], cote: str, en_plus: list | None = None) -> list[dict]:
    """Chaque saut h d'un côté, de la surface h − 1 à la surface h (la nappe en tête), avec ce que dit la lecture stricte et ce que dit le
    critère sans référent ; avec `en_plus`, écrit pour `345`, ce qu'une autre mesure dit de chaque saut."""
    if len(surfaces) != len(tenues) + 1 or (en_plus is not None and len(en_plus) != len(tenues)):
        raise ValueError(f"{len(surfaces)} surfaces pour {len(tenues)} sauts")
    return [{"le_saut": h, "la_justesse": la_justesse(surfaces[h - 1], surfaces[h], LE_SENS[cote]),
             **{k: t.get(k) for k in LES_CLES_DE_LA_TENUE}, **({"en_plus": en_plus[h - 1]} if en_plus is not None else {})}
            for h, t in enumerate(tenues, 1)]


def un_cote_sans_relance(nappe: dict, cote: float, lire_valeurs, lire_les_tours, pas: float, tolerance: float,
                         sauts: int = m330.LES_SAUTS, en_plus=None) -> tuple[list[dict], list[dict]]:
    """La chaîne de `330` sur un côté, avec la tenue de `328` à chaque saut : la tenue et la lecture de chaque spire par `lire_les_tours` ;
    avec `en_plus(depart, arrivee, lire_valeurs)`, écrit pour `345`, ce qu'il rend de la surface de départ et de la spire."""
    surf, ok = nappe["la_nappe"], nappe["valide"]
    tenues, lectures = [], []
    for _ in range(sauts):
        s = m306.le_saut_croissant(surf, ok, cote, lire_valeurs, tolerance=tolerance)
        tenues.append(m328.un_saut(s, lire_valeurs, pas))
        lectures.append({"la_part_du_plan": round(float(s["valide"].mean()), 4), "les_tours": lire_les_tours(s["la_spire"][s["valide"]])})
        if en_plus is not None:
            lectures[-1]["en_plus"] = en_plus({"la_nappe": surf, "valide": ok}, {"la_nappe": s["la_spire"], "valide": s["valide"]},
                                              lire_valeurs)
        if not s["valide"].any():
            break
        surf, ok = s["la_spire"], s["valide"]
    return tenues, lectures


def la_chaine_sans_relance(en_plus=None) -> dict:
    """La chaîne de `330` rejouée graine par graine, avec ses lectures et la tenue de `328`."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    lire_les_tours = lambda pts: {str(t): x for t, x in m329.les_lectures(pts * m321.LE_FACTEUR, tours).items()}  # noqa: E731
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        e = {"le_rang": rang, "la_nappe": lire_les_tours(r["la_nappe"][r["valide"]]), "les_cotes": {}}
        for nom, cote in m306.LES_COTES:
            with m321.le_rouleau_de_paris4():
                tenues, spires = un_cote_sans_relance(r, cote, lv4, lire_les_tours, m321.LE_PAS_L2, m322.LA_TOLERANCE_L2,
                                                      en_plus=en_plus)
            e["les_cotes"][nom] = {"les_tenues": tenues, "les_spires": spires}
        graines.append(e)
        print("sans relance", rang, {c: [t["tient"] for t in v["les_tenues"]] for c, v in e["les_cotes"].items()}, flush=True)
    return {"les_graines": graines, "les_pannes": list(stats4["pannes"]),
            "la_lecture_de_m7": {k: v for k, v in stats4.items() if k != "pannes"}}


def une_chaine_relancee(fabrique, avec_la_spire: bool, en_plus=None) -> dict:
    """Une chaîne relancée de `331`, rejouée sur PHercParis4, avec la tenue de chaque saut par `m331.la_tenue` ; avec `en_plus`, écrit pour
    `345`, ce qu'il rend de la surface d'où part chaque saut et de sa nappe relancée."""
    lv, tenues, plus = {}, {}, {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return fabrique(lv4)

    def observer(rang, nom, h, k):
        tenues[(rang, nom, h)] = m331.la_tenue(k, lv["m7"], m321.LE_PAS_L2)
        if en_plus is not None:
            plus[(rang, nom, h)] = en_plus(k["le_depart"], k["la_relance"], lv["m7"])
        return {}

    d = m331.mesurer(relancer4=relancer4, avec_la_spire=avec_la_spire, rouleaux=("PHercParis4",), observer=observer)
    for g in d["les_graines"]["PHercParis4"]:
        for nom, c in g["les_cotes"].items():
            c["les_tenues"] = [tenues[(g["le_rang"], nom, h)] for h in range(1, len(c["les_surfaces"]) + 1)]
            if en_plus is not None:
                c["les_en_plus"] = [plus[(g["le_rang"], nom, h)] for h in range(1, len(c["les_surfaces"]) + 1)]
        print(g["le_rang"], {c: [t["tient"] for t in v["les_tenues"]] for c, v in g["les_cotes"].items()}, flush=True)
    return d


def les_lectures_rejouees(nom: str, d: dict, nappes: dict, rang: int, cote: str) -> list[dict]:
    """La suite des lectures rejouées d'un côté, la nappe en tête, sous la forme que `340` lit dans les tranches publiées."""
    if nom != "sans relance":
        return m340.les_surfaces(nom, d, nappes, rang, cote)
    g = next(x for x in d["les_graines"] if x["le_rang"] == rang)
    return [nappes[rang]] + [{t: x["la_lecture"] for t, x in s["les_tours"].items()} for s in g["les_cotes"][cote]["les_spires"]]


def les_tenues(nom: str, d: dict, rang: int, cote: str) -> list[dict]:
    g = next(x for x in m340.les_graines_de(nom, d) if x["le_rang"] == rang)
    return g["les_cotes"][cote]["les_tenues"]


def les_en_plus(nom: str, d: dict, rang: int, cote: str) -> list | None:
    g = next(x for x in m340.les_graines_de(nom, d) if x["le_rang"] == rang)
    if nom == "sans relance":
        spires = g["les_cotes"][cote]["les_spires"]
        return [s["en_plus"] for s in spires] if all("en_plus" in s for s in spires) else None
    return g["les_cotes"][cote].get("les_en_plus")


def redonne_328(d: dict, publie: dict) -> bool:
    """La tenue de la chaîne sans relance rejouée redonne-t-elle, saut par saut, celle que `328` publie sur ses côtés de PHercParis4 ?"""
    ok = bool(publie["les_cotes"]["PHercParis4"])
    for c in publie["les_cotes"]["PHercParis4"]:
        ok &= les_tenues("sans relance", d, c["le_rang"], c["le_cote"]) == c["les_sauts"]
    return bool(ok)


def le_bilan(sauts: list[dict]) -> dict:
    """Les sauts justes, faux et non jugés, et combien de chacun le critère dit tenir."""
    juste = [s for s in sauts if s["la_justesse"] == "juste"]
    faux = [s for s in sauts if s["la_justesse"].startswith("faux")]
    non = [s for s in sauts if s["la_justesse"] == "non jugé"]
    part = lambda xs: round(sum(s["tient"] for s in xs) / len(xs), 4) if xs else None  # noqa: E731
    return {"les_justes": len(juste), "les_justes_qui_tiennent": sum(s["tient"] for s in juste), "tj": part(juste),
            "les_faux": len(faux), "les_faux_qui_tiennent": sum(s["tient"] for s in faux), "tf": part(faux),
            "les_non_juges": len(non), "les_non_juges_qui_tiennent": sum(s["tient"] for s in non),
            "la_part_des_tenus_qui_sont_justes": (round(sum(s["tient"] for s in juste) / t_, 4)
                                                   if (t_ := sum(s["tient"] for s in juste + faux)) else None)}


def les_sauts_de(d: dict, graines: tuple, chaines=None) -> list[dict]:
    return [s for nom, c in d["les_chaines"].items() if chaines is None or nom in chaines
            for g in c["les_graines"] if g["le_rang"] in graines for cote in g["les_cotes"].values() for s in cote["les_sauts"]]


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    faux_ = [n for n, c in d["les_chaines"].items() if not c["redonne"]]
    if faux_:
        return {"decidable": False, "lissue": f"indécidable : la chaîne rejouée ne redonne pas ses lectures publiées ({faux_[0]})"}
    if not d.get("redonne_328"):
        return {"decidable": False, "lissue": "indécidable : la tenue rejouée ne redonne pas celle de 328"}
    b = le_bilan(les_sauts_de(d, LES_GRAINES_PROPRES))
    if b["les_justes"] < LE_MINIMUM or b["les_faux"] < LE_MINIMUM:
        return {"decidable": False, **b, "lissue": f"indécidable : {b['les_justes']} sauts justes et {b['les_faux']} sauts faux jugés"}
    tj, tf = b["tj"], b["tf"]
    tete = (f"sur les graines 4 à 8, le critère sans référent dit tenir {b['les_justes_qui_tiennent']} des {b['les_justes']} sauts justes "
            f"et {b['les_faux_qui_tiennent']} des {b['les_faux']} sauts faux")
    if tj >= LA_TENUE_DES_JUSTES and tf <= LA_TENUE_DES_FAUX:
        suite, issue = "il les sépare", "sépare"
    elif tj - tf < LECART_MINIMAL:
        suite, issue = "il ne les sépare pas", "ne sépare pas"
    else:
        suite, issue = "il ne les sépare qu'en partie", "en partie"
    return {"decidable": True, **b, "lissue_courte": issue, "lissue": f"{tete} ; {suite}"}


def les_parts_publiees(nom: str, publiee: dict, rang: int, cote: str) -> list[tuple]:
    """La part du plan de chaque saut, et la part de sa nappe relancée, telles que la tranche publiée les donne."""
    g = next(x for x in m340.les_graines_de(nom, publiee) if x["le_rang"] == rang)
    if nom == "sans relance":
        return [(s["la_part_du_plan"], None) for s in g["les_cotes"][cote]["les_spires"]]
    return [(s["la_part_de_la_spire"], s["la_part_relancee"]) for s in g["les_cotes"][cote]["les_surfaces"]]


def mesurer(en_plus=None) -> dict:
    """La mesure de `344` ; avec `en_plus(depart, arrivee, lire_valeurs)`, écrit pour `345`, chaque saut porte aussi ce qu'il rend."""
    t0 = time.monotonic()
    rejouees = {"sans relance": la_chaine_sans_relance(en_plus)}
    for nom, (fabrique, avec) in LES_RELANCES.items():
        print("==", nom, flush=True)
        rejouees[nom] = une_chaine_relancee(fabrique, avec, en_plus)
    publiees = {n: json.loads((LES_MESURES / f).read_text()) for n, f in m340.LES_CHAINES.items()}
    lecture = lambda g: {t: x["la_lecture"] for t, x in g["la_nappe"].items()}  # noqa: E731
    nappes = {g["le_rang"]: lecture(g) for g in publiees["sans relance"]["les_graines"]}
    nappes_rejouees = {g["le_rang"]: lecture(g) for g in rejouees["sans relance"]["les_graines"]}
    chaines, pannes = {}, []
    for nom, dr in rejouees.items():
        pannes += list(dr.get("les_pannes", []))
        redonne = nappes_rejouees == nappes
        graines = []
        for g in m340.les_graines_de(nom, publiees[nom]):
            cotes = {}
            for cote in g["les_cotes"]:
                pub = m340.les_surfaces(nom, publiees[nom], nappes, g["le_rang"], cote)
                rej = les_lectures_rejouees(nom, dr, nappes_rejouees, g["le_rang"], cote)
                ten = les_tenues(nom, dr, g["le_rang"], cote)
                redonne &= [{str(t): x for t, x in s.items()} for s in rej] == [{str(t): x for t, x in s.items()} for s in pub]
                redonne &= [(t["la_part_du_plan"], t.get("la_part_relancee")) for t in ten] == les_parts_publiees(
                    nom, publiees[nom], g["le_rang"], cote)
                cotes[cote] = {"les_sauts": les_sauts(rej, ten, cote, les_en_plus(nom, dr, g["le_rang"], cote))}
            graines.append({"le_rang": g["le_rang"], "les_cotes": cotes})
        chaines[nom] = {"redonne": bool(redonne), "les_graines": graines}
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_graines_propres": list(LES_GRAINES_PROPRES), "les_tours_juges": list(LES_TOURS_JUGES),
                            "la_tenue_des_justes": LA_TENUE_DES_JUSTES, "la_tenue_des_faux": LA_TENUE_DES_FAUX,
                            "lecart_minimal": LECART_MINIMAL, "le_minimum": LE_MINIMUM},
         "les_pannes": pannes, "la_lecture_de_m7": {n: dr["la_lecture_de_m7"] for n, dr in rejouees.items()},
         "redonne_328": redonne_328(rejouees["sans relance"], json.loads(CE_QUE_328_A_PUBLIE.read_text())),
         "les_chaines": chaines}
    d["le_verdict"] = le_verdict(d)
    d["les_bilans"] = {"par_chaine": {n: le_bilan(les_sauts_de(d, LES_GRAINES_PROPRES, (n,))) for n in chaines},
                       "graines_1_a_3": le_bilan(les_sauts_de(d, (1, 2, 3)))}
    d["les_sauts_faux"] = [{"la_chaine": n, "le_rang": g["le_rang"], "le_cote": c, **s} for n, ch in chaines.items()
                           for g in ch["les_graines"] for c, x in g["les_cotes"].items() for s in x["les_sauts"]
                           if s["la_justesse"].startswith("faux")]
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    R, N, L = "retrouve", "ne retrouve pas", "non lue"
    lect = lambda **kw: {str(t): kw.get(f"t{-t}", L) for t in range(0, -8, -1)}  # noqa: E731
    un = lect(t0=R, t1=N)
    v("★★★★ de 5753_0 seul à 5753_-1 seul, côté moins : juste", la_justesse(un, lect(t1=R, t0=N), -1) == "juste")
    v("★★★★ la surface retrouve 5753_-1 et 5753_-2 : faux, deux tours",
      la_justesse(un, lect(t1=R, t2=R), -1) == "faux : deux tours")
    v("★★★★ la surface retrouve 5753_-2 seul : faux, un autre tour", la_justesse(un, lect(t2=R, t1=N), -1) == "faux : un autre tour")
    v("★★★★ rien de retrouvé, 5753_-1 lu en face : faux, le tour manqué ; 5753_-1 non lu : non jugé",
      la_justesse(un, lect(t1=N, t0=N), -1) == "faux : le tour manqué" and la_justesse(un, lect(t0=N), -1) == "non jugé")
    v("★★★★ une surface de départ qui retrouve deux tours, ou aucun : non jugé",
      la_justesse(lect(t0=R, t1=R), lect(t2=R), -1) == "non jugé" and la_justesse(lect(t0=N), lect(t1=R), -1) == "non jugé")
    v("★★★★ 5753_-7 n'est pas un tour jugé, même retrouvé seul", la_justesse(lect(t6=R), lect(t7=R), -1) == "non jugé"
      and la_justesse(lect(t5=R), lect(t6=R), -1) == "juste")
    v("★★★★ côté plus, le tour attendu est w + 1 : de 5753_-3 à 5753_-2 juste, à 5753_-4 faux, et au-delà de 5753_0 non jugé",
      la_justesse(lect(t3=R), lect(t2=R), 1) == "juste" and la_justesse(lect(t3=R), lect(t4=R), 1) == "faux : un autre tour"
      and la_justesse(lect(t0=R), lect(t1=R), 1) == "non jugé")
    t_ = lambda b: {"la_part_du_plan": 0.5, "le_pas_median_en_pas": 1.0, "pose_au_pas": b, "la_plage_en_pas": 0.1, "tient": b}  # noqa: E731
    ss = les_sauts([lect(t0=R), lect(t1=R), lect(t2=R), lect(t4=R)], [t_(True), t_(False), t_(True)], "moins")
    v("★★★★ le saut h va de la surface h − 1 à la surface h, pas de la nappe, et porte la tenue du saut h",
      [(s["le_saut"], s["la_justesse"], s["tient"]) for s in ss]
      == [(1, "juste", True), (2, "juste", False), (3, "faux : un autre tour", True)], str(ss))
    v("★★★ une surface de trop ou de moins est refusée", _leve(lambda: les_sauts([lect(t0=R)], [t_(True)] * 2, "moins")))

    grille = np.zeros((9, 9, 3))
    for a in range(9):
        for b in range(9):
            grille[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, 100.0)
    nappe = {"la_nappe": grille, "valide": np.ones((9, 9), dtype=bool)}
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    hauteur = lambda pts: {"z": float(np.median(pts[:, 2])) if len(pts) else None}  # noqa: E731
    tenues, spires = un_cote_sans_relance(nappe, 1.0, feuilles, hauteur, 20.0, 5.0, sauts=3)
    v("★★★★ sans relance : la tenue de 328 à chaque saut, et chaque spire lue à sa place",
      tenues == m328.la_chaine(nappe, 1.0, feuilles, 20.0, 5.0, sauts=3) and [s["les_tours"]["z"] for s in spires] == [120.0, 140.0, 160.0],
      str(spires))
    z_ = lambda s: float(np.median(s["la_nappe"][s["valide"]][:, 2]))  # noqa: E731
    _, spires = un_cote_sans_relance(nappe, 1.0, feuilles, hauteur, 20.0, 5.0, sauts=3, en_plus=lambda a, b, lv: (z_(a), z_(b)))
    v("★★★★ en plus, chaque saut reçoit la surface d'où il part et la spire où il arrive",
      [s["en_plus"] for s in spires] == [(100.0, 120.0), (120.0, 140.0), (140.0, 160.0)], str([s["en_plus"] for s in spires]))
    ss = les_sauts([lect(t0=R), lect(t1=R), lect(t2=R)], [t_(True), t_(False)], "moins", en_plus=["a", "b"])
    v("★★★ en plus, chaque saut porte ce qu'on a mesuré de lui", [s["en_plus"] for s in ss] == ["a", "b"])
    sp = lambda *xs: {"les_graines": [{"le_rang": 1, "les_cotes": {"moins": {"les_spires": list(xs)}}}]}  # noqa: E731
    v("★★★ en plus, une mesure qui ne rend rien est portée telle quelle, et une mesure absente ne l'est pas",
      les_en_plus("sans relance", sp({"en_plus": None}, {"en_plus": "x"}), 1, "moins") == [None, "x"]
      and les_en_plus("sans relance", sp({}, {}), 1, "moins") is None)

    s_ = lambda j, t: {"la_justesse": j, "tient": t}  # noqa: E731
    def d_(sauts_propres, sauts_sales=(), **kw):
        g = lambda r, xs: {"le_rang": r, "les_cotes": {"moins": {"les_sauts": list(xs)}}}  # noqa: E731
        return dict({"les_pannes": [], "redonne_328": True,
                     "les_chaines": {"bornée": {"redonne": True, "les_graines": [g(4, sauts_propres), g(2, sauts_sales)]}}}, **kw)
    j9, f5 = [s_("juste", True)] * 9 + [s_("juste", False)], [s_("faux : deux tours", False)] * 4 + [s_("faux : un autre tour", True)]
    vd = le_verdict(d_(j9 + f5))
    v("★★★★ 9 justes sur 10 tenus et 1 faux sur 5 : il les sépare", vd.get("lissue_courte") == "sépare", str(vd))
    vd = le_verdict(d_(j9 + [s_("faux : deux tours", True)] * 4 + [s_("faux : le tour manqué", False)]))
    v("★★★★ 9 justes sur 10 et 4 faux sur 5 : il ne les sépare pas", vd.get("lissue_courte") == "ne sépare pas", str(vd))
    vd = le_verdict(d_(j9 + [s_("faux : deux tours", True)] * 3 + [s_("faux : deux tours", False)] * 2))
    v("★★★★ 9 justes sur 10 et 3 faux sur 5 : en partie", vd.get("lissue_courte") == "en partie", str(vd))
    vd = le_verdict(d_(j9 + f5[:4], sauts_sales=[s_("faux : deux tours", True)] * 6))
    v("★★★★ les sauts des graines 1 à 3 ne comptent pas : 4 faux sur les graines propres, indécidable",
      not vd["decidable"] and vd["les_faux"] == 4, str(vd))
    vd = le_verdict(d_(j9 + f5 + [s_("non jugé", True)] * 20))
    v("★★★ les sauts non jugés ne comptent pas", vd.get("lissue_courte") == "sépare" and vd["les_non_juges"] == 20, str(vd))
    bad = d_(j9 + f5)
    bad["les_chaines"]["bornée"]["redonne"] = False
    v("★★★★ une chaîne rejouée qui ne redonne pas ses lectures publiées : indécidable", not le_verdict(bad)["decidable"])
    v("★★★ une tenue qui ne redonne pas 328 : indécidable", not le_verdict(d_(j9 + f5, redonne_328=False))["decidable"])
    v("★★★ les deux bornes sont larges : 0,75 et 0,25 disent qu'il les sépare",
      le_verdict(d_([s_("juste", True)] * 6 + [s_("juste", False)] * 2 + [s_("faux : deux tours", True)] * 2
                    + [s_("faux : deux tours", False)] * 6)).get("lissue_courte") == "sépare")

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except ValueError:
        return True
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
