"""Sur PHercParis4, des chaînes qui rognent la plage retombée de leurs surfaces lisent-elles leurs surfaces validées sur le bon tour aussi souvent que celles de 385 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE ROGNÉE NE SOIT LANCÉE SUR PHERCPARIS4. Ce qui était vu avant d'écrire : tout ce que `296` à
`399` publient, dont `R4-F571` (sur PHercParis4, aux comptes de `m7`, l'accord valide 160 surfaces et les 58 lues sont sur le bon tour),
`R4-F580` (2 seulement des 88 sauts jugés de PHercParis4 sont des mélanges), `R4-F583` et `R4-F585` (sur PHerc0358, aucune des deux façons
de rogner ne bat les chaînes non rognées, et seuls des tours publiés les départageraient).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P197`. PHercParis4 a des tours publiés : c'est là qu'un rognage qui ferait tort se verrait.

## Ce qui est fait

- **Les chaînes** : les trois chaînes d'une maille de `379` sur les côtés de PHercParis4, dont chaque surface gardée est rognée comme `397`
  la rogne, au pas et au latéral de PHercParis4 ; chaque surface garde aussi sa forme entière.
- **Deux façons de compter**, comme sur PHerc0358 : **rognées**, comptées, appariées et jugées sur leurs surfaces rognées (comme `397`) ;
  **comptées entières**, sur leurs surfaces entières, chaque saut compté depuis la surface rognée d'où il part (comme `399`). Les comptes de
  `m7` et l'accord sont ceux de `385` ; la vérité est celle de `379`, lue sur la surface que chaque façon juge.
- **Le contrôle** : sur les côtés où aucune surface n'est rognée, les statuts rognés redonnent ceux de `385`.
- **La règle** : si dans les deux façons au moins 10 surfaces validées sont lues et toutes sont sur le bon tour, comme dans `385`, **oui** ;
  si dans l'une plus d'une sur dix est sur un mauvais tour, **non** ; sinon, **en partie**. Indécidable sous 10 surfaces validées lues dans
  une façon, si une lecture échoue, ou si le contrôle échoue.

## Les issues

L'issue de la tranche : **rognées, v des l surfaces validées lues sont sur le bon tour ; comptées entières, v' des l'**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

Les surfaces rognées et les mailles retirées ; les validées et les contredites des deux façons, contre les 160 et 81 de `385`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que le rognage vaut sur PHerc0358, dont les feuilles se touchent plus souvent.

Usage :
    uv run python src/nappe/des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.py --verifier
    uv run python src/nappe/des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.py \\
        --json docs/mesures/des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_dune_seule_maille_evite_il_le_decalage as m365  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4 as m385  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402
import compter_la_surface_entiere_et_rogner_le_depart_garde_t_il_les_deux_gains_sur_pherc0358 as m399  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_385_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"
LES_CHAINES = m374.LES_CHAINES
LE_MINIMUM, LA_PART_FAUSSE = 10, 0.1
LES_FACONS = ("rognees", "entieres")


def rogner4(depart: dict, garde: dict) -> dict:
    """Le rognage de `397` au pas et au latéral de PHercParis4, qui garde le masque entier comme `399`."""
    return {**m397.rogner(depart, garde, pas=m379.LE_PAS, lateral=m379.LE_LATERAL), "valide_entier": garde["valide"]}


def enchainer4(nappe, relancer, sauter, lire_valeurs):
    """La chaîne d'une maille de `365`, dont chaque surface gardée est rognée."""
    regrandir = lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lire_valeurs, marge=m365.LA_MARGE)  # noqa: E731
    return m356.la_chaine_mixte(nappe, relancer, sauter, lire_valeurs, compter=m357.compter4, regrandir=regrandir, rogner=rogner4)


def les_comptes_entiers(nap, rognees: list, entieres: list, lire_valeurs) -> tuple[list[int], list[int | None]]:
    """Pour chaque saut, depuis la surface rognée d'où il part jusqu'à sa surface entière : le compte de `369` corrigé et le nombre de
    feuilles de `m7`."""
    corriges, nombres, w, avant = [], [], 0, nap
    for rl, en in zip(rognees, entieres):
        w += m379.LES_POIDS[m379.le_genre(m379.lecart(m367.les_points(en), m367.les_points(avant)))]
        corriges.append(w)
        r = None if avant is None else m345.les_comptes_point_par_point(avant, en, lire_valeurs, m379.LE_PAS)
        nombres.append(m383.le_nombre_de_feuilles(m345.le_resume(r)["les_comptes"]))
        avant = rl
    return corriges, nombres


def le_bilan_lu(surfaces: list[dict]) -> dict:
    v = [s for s in surfaces if s["le_statut"] == m374.VALIDEE]
    lues = [s for s in v if s["lue"]]
    return {"validees": len(v), "contredites": sum(s["le_statut"] == m374.CONTREDITE for s in surfaces), "lues": len(lues),
            "sur_le_bon_tour": sum(bool(s["sur_le_bon_tour"]) for s in lues)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : sur les côtés sans rognage, les statuts ne redonnent pas 385"}
    b = d["le_bilan"]
    for f in LES_FACONS:
        if b[f]["lues"] < LE_MINIMUM:
            return {"decidable": False, "lissue": f"indécidable : {b[f]['lues']} surfaces validées lues ({f}), moins de {LE_MINIMUM}"}
    r, e = b["rognees"], b["entieres"]
    tete = (f"rognées, {r['sur_le_bon_tour']} des {r['lues']} surfaces validées lues sont sur le bon tour ; comptées entières, "
            f"{e['sur_le_bon_tour']} des {e['lues']}")
    faux = [(b[f]["lues"] - b[f]["sur_le_bon_tour"]) / b[f]["lues"] for f in LES_FACONS]
    suite = "oui" if max(faux) == 0 else "non" if max(faux) > LA_PART_FAUSSE else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m379._LES_TROIS.clear()
    m397._LES_ROGNAGES.clear()
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=m379.le_chaineur(enchainer=enchainer4))
    d385 = json.loads(CE_QUE_385_A_PUBLIE.read_text())
    cotes_d331 = [(g["le_rang"], cote) for g in d331["les_graines"]["PHercParis4"] for cote in g["les_cotes"]]
    controle = len(cotes_d331) == len(m379._LES_TROIS) == len(d385["les_cotes"])
    cotes, toutes = [], {f: [] for f in LES_FACONS}
    for (rang, cote), trois, c385 in zip(cotes_d331, m379._LES_TROIS, d385["les_cotes"]):
        sens = m344.LE_SENS[cote]
        rognees = {x: trois["les_relances"][x] for x in LES_CHAINES}
        entieres = {x: [m399.entiere(rl) for rl in rognees[x]] for x in LES_CHAINES}
        rognes = sum(1 for x in LES_CHAINES for rl in rognees[x] if rl is not None and "valide_entier" in rl
                     and (rl["valide_entier"] != rl["valide"]).any())
        cote_out = {"le_rang": rang, "le_cote": cote, "les_surfaces_rognees": rognes}
        for f, surfs in (("rognees", rognees), ("entieres", entieres)):
            pts = {x: [m367.les_points(s) for s in surfs[x]] for x in LES_CHAINES}
            nap = {x: m367.les_points(trois["les_nappes"][x]) for x in LES_CHAINES}
            retrouves = {x: [m379.les_retrouves(trois["les_nappes"][x], tours)] + [m379.les_retrouves(s, tours) for s in surfs[x]]
                         for x in LES_CHAINES}
            if f == "rognees":
                corriges = {x: m379.les_comptes(nap[x], pts[x]) for x in LES_CHAINES}
                nombres = {x: [n["le_nombre_de_feuilles"] for n in m385.les_nombres(trois["les_nappes"][x], rognees[x], lv["m7"])]
                           for x in LES_CHAINES}
            else:
                ce = {x: les_comptes_entiers(trois["les_nappes"][x], rognees[x], entieres[x], lv["m7"]) for x in LES_CHAINES}
                corriges, nombres = {x: ce[x][0] for x in LES_CHAINES}, {x: ce[x][1] for x in LES_CHAINES}
            m7 = {x: m385.les_comptes_de_m7(corriges[x], nombres[x]) for x in LES_CHAINES}
            paires = {f"{a}|{b}": m379.les_paires(pts[a], pts[b]) for a, b in m379.LES_COUPLES}
            surfaces = m379.le_cote(paires, m7, {x: m379.la_verite(retrouves[x], m7[x], sens) for x in LES_CHAINES})
            toutes[f] += surfaces
            cote_out[f] = {"les_nombres": nombres, "les_comptes": m7, "le_bilan": le_bilan_lu(surfaces),
                           "les_surfaces": [[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"], s["lue"], s["sur_le_bon_tour"]]
                                            for s in surfaces]}
        controle &= (rang, cote) == (c385["le_rang"], c385["le_cote"])
        if not rognes:
            controle &= ([tuple(s[:6]) for s in cote_out["rognees"]["les_surfaces"]]
                         == m385.les_statuts(c385["les_surfaces_avec_m7"]))
        cotes.append(cote_out)
        print(json.dumps({"le_rang": rang, "le_cote": cote, "rognes": rognes, "controle": bool(controle),
                          "rognees": cote_out["rognees"]["le_bilan"], "entieres": cote_out["entieres"]["le_bilan"]}, ensure_ascii=False),
              flush=True)
    ro = list(m397._LES_ROGNAGES)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_minimum": LE_MINIMUM, "la_part_fausse": LA_PART_FAUSSE},
         "les_pannes": list(d331["les_pannes"]), "la_lecture_de_m7": d331["la_lecture_de_m7"], "le_controle": bool(controle),
         "la_reference_385": {"validees": d385["avec_m7"][m374.VALIDEE]["les_surfaces"], "contredites": d385["avec_m7"][m374.CONTREDITE]["les_surfaces"],
                              "lues": d385["avec_m7"][m374.VALIDEE]["lues"], "sur_le_bon_tour": d385["avec_m7"][m374.VALIDEE]["sur_le_bon_tour"]},
         "les_rognages": {"vues": len(ro), "rognees": sum(r["rognee"] for r in ro), "mailles": sum(r["retombees"] for r in ro if r["rognee"])},
         "les_cotes": cotes}
    d["le_bilan"] = {f: le_bilan_lu(toutes[f]) for f in LES_FACONS}
    d["le_verdict"] = le_verdict(d)
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

    s_ = lambda st, lue, bon: {"le_statut": st, "lue": lue, "sur_le_bon_tour": bon}  # noqa: E731
    b = le_bilan_lu([s_(m374.VALIDEE, True, True), s_(m374.VALIDEE, True, False), s_(m374.VALIDEE, False, None), s_(m374.CONTREDITE, True, True),
                     s_(m374.SEULE, True, False)])
    v("★★★★ le bilan : validées, contredites, validées lues et validées lues sur le bon tour",
      b == {"validees": 3, "contredites": 1, "lues": 2, "sur_le_bon_tour": 1}, str(b))

    def d_(r, rl, e, el, ok=True):
        return {"le_controle": ok, "les_pannes": [], "le_bilan": {"rognees": {"lues": rl, "sur_le_bon_tour": r},
                                                                  "entieres": {"lues": el, "sur_le_bon_tour": e}}}
    v("★★★★ la règle : toutes sur le bon tour dans les deux façons, oui ; plus d'une sur dix fausse dans l'une, non ; sinon, en partie",
      le_verdict(d_(20, 20, 30, 30))["lissue"].endswith("; oui") and le_verdict(d_(17, 20, 30, 30))["lissue"].endswith("; non")
      and le_verdict(d_(19, 20, 30, 30))["lissue"].endswith("; en partie") and le_verdict(d_(18, 20, 30, 30))["lissue"].endswith("; en partie")
      and "rognées, 19 des 20 surfaces validées lues sont sur le bon tour ; comptées entières, 30 des 30" in le_verdict(d_(19, 20, 30, 30))["lissue"])
    v("★★★ indécidable sous 10 lues dans une façon, ou si le contrôle échoue",
      not le_verdict(d_(9, 9, 30, 30))["decidable"] and not le_verdict(d_(20, 20, 30, 30, ok=False))["decidable"])
    import numpy as np
    ii, jj = np.meshgrid(np.arange(12, dtype=float), np.arange(12, dtype=float), indexing="ij")
    plan = {"la_nappe": np.stack([jj, ii, np.zeros_like(ii)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    haut = (m379.LE_PAS + m383.LE_PAS) / 8.0
    marche = {"la_nappe": np.stack([jj, ii, np.where(jj < 6, 0.0, haut)], axis=-1), "valide": np.ones((12, 12), dtype=bool)}
    r = rogner4(plan, marche)
    v("★★★★ le rognage de PHercParis4 retire la plage retombée et garde le masque entier, au quart du pas de PHercParis4",
      m379.LE_PAS < m383.LE_PAS and r["valide_entier"].all() and not r["valide"][1:-1, 1:5].any() and r["valide"][1:-1, 7:-1].all())

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


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
