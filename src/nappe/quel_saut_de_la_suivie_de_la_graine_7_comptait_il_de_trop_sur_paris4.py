"""Sur PHercParis4, quel saut de la suivie de la graine 7, côté moins, 385 comptait-il d'une feuille de trop, et sa surface était-elle à cheval ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES TOURS DES SURFACES ROGNÉES DE LA GRAINE 7 NE SOIENT LUS. Ce qui était vu avant d'écrire : tout ce que
`296` à `400` publient, dont `R4-F586` (rognées, les sixième et septième surfaces de cette suivie passent des comptes 7 et 8 aux comptes 6 et
7 et sont lues sur le bon tour) et **`R4-F580`, qui dit déjà ce que `385` fait à ce saut** : le sixième saut de cette suivie compte 2 feuilles,
105 de ses 166 points en comptant 2 et 60 en comptant 3, quand les tours en disent 3. ⚠ La porte `R4-P198` a été posée par `400` comme si
`385` comptait de trop ; `R4-F580` dit le contraire. Cette tranche le mesure au lieu de le supposer, et lit ce que fait la chaîne rognée.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P198`. Si le rognage corrigeait le compte d'une surface à cheval, il corrigerait la mesure ; s'il
fait faire à la chaîne un autre saut, il change la chaîne, et `R4-F586` dit moins qu'il n'en a l'air.

## Ce qui est fait

- **Les chaînes de `385`** : sur la graine 7, côté moins, les tours que `379` retrouve pour chaque surface et les comptes de `m7` que `385`
  publie pour chaque saut.
- **Les chaînes rognées** : celles de `400`, relancées ; leurs statuts sur ce côté doivent redonner ceux de `400`. Pour chaque surface, les
  tours publiés qu'elle retrouve ; pour chaque saut, le compte de `m7` de `385` sur les surfaces rognées.
- **Un saut jugé** : ses deux surfaces (la nappe pour le premier) retrouvent chacune un seul tour ; les tours qu'il franchit sont leur écart,
  dans le sens du côté. Il compte **de trop** si `m7` y dit plus de feuilles que de tours, **pas assez** s'il en dit moins ; sa surface est
  **à cheval** si c'est un mélange, comme `394` le prend.
- **La règle**, sur la suivie de `385` : si un saut jugé compte de trop et que sa surface est à cheval, **oui** ; si un saut compte de trop sans
  être à cheval, **en partie** ; si aucun saut jugé ne compte de trop, **non**. Indécidable si aucun saut de cette suivie n'est jugé, si une
  lecture échoue, ou si les chaînes rognées ne redonnent pas `400`.

## Les issues

L'issue de la tranche : **dans `385`, les sauts faux de la suivie : saut h, n feuilles pour t tours**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Pour chaque chaîne du côté, les tours de chaque surface et le compte de chaque saut, dans `385` et rognées.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que le rognage fait sur les autres côtés.

Usage :
    uv run python src/nappe/quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.py --verifier
    uv run python src/nappe/quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.py \\
        --json docs/mesures/quel_saut_de_la_suivie_de_la_graine_7_comptait_il_de_trop_sur_paris4.json
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
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4 as m379  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4 as m385  # noqa: E402
import les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4 as m394  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402
import des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4 as m400  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_379_A_PUBLIE = LES_MESURES / "une_surface_validee_par_trois_chaines_est_elle_sur_le_bon_tour_de_paris4.json"
CE_QUE_385_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"
CE_QUE_400_A_PUBLIE = LES_MESURES / "des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.json"
LE_COTE = (7, "moins")
LES_CHAINES = m374.LES_CHAINES


def les_sauts_juges(retrouves: list[list[int]], sauts: list[dict], sens: int) -> list[dict]:
    """Chaque saut d'une chaîne : les tours qu'il franchit s'il est jugé, le nombre de feuilles et la part majoritaire de `m7`, et ce qu'il
    en dit : juste, de trop, pas assez."""
    out = []
    for h, s in enumerate(sauts, 1):
        avant, apres = (retrouves[h - 1], retrouves[h]) if h < len(retrouves) else ([], [])
        tours = sens * (apres[0] - avant[0]) if len(avant) == 1 and len(apres) == 1 else None
        n = s["le_nombre_de_feuilles"]
        part = m394.la_part_majoritaire(s["les_comptes"])
        dit = None if tours is None or n is None else "juste" if n == tours else "de_trop" if n > tours else "pas_assez"
        out.append({"le_saut": h, "les_tours": tours, "le_nombre_de_feuilles": n, "les_comptes": s["les_comptes"], "la_part_majoritaire": part,
                    "a_cheval": part is not None and part < m394.LA_PART_DU_MELANGE, "dit": dit})
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_400"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rognées ne redonnent pas 400"}
    s = d["la_suivie_de_385"]
    juges = [x for x in s if x["dit"] is not None]
    if not juges:
        return {"decidable": False, "lissue": "indécidable : aucun saut de la suivie de 385 n'est jugé"}
    faux = [x for x in juges if x["dit"] != "juste"]
    tete = ("dans 385, les sauts faux de la suivie : " + ", ".join(f"saut {x['le_saut']}, {x['le_nombre_de_feuilles']} feuilles pour "
                                                                   f"{x['les_tours']} tours" for x in faux) if faux
            else "dans 385, aucun saut jugé de la suivie n'est faux")
    trop = [x for x in faux if x["dit"] == "de_trop"]
    suite = ("oui, une surface à cheval comptée de trop" if any(x["a_cheval"] for x in trop) else "en partie" if trop
             else "non, 385 ne comptait pas de trop")
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

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), chainer4=m379.le_chaineur(enchainer=m400.enchainer4))
    d379, d385, d400 = (json.loads(x.read_text()) for x in (CE_QUE_379_A_PUBLIE, CE_QUE_385_A_PUBLIE, CE_QUE_400_A_PUBLIE))
    cotes_d331 = [(g["le_rang"], cote) for g in d331["les_graines"]["PHercParis4"] for cote in g["les_cotes"]]
    trois = m379._LES_TROIS[cotes_d331.index(LE_COTE)]
    c379 = next(c for c in d379["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    c385 = next(c for c in d385["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    c400 = next(c for c in d400["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    sens = m344.LE_SENS[LE_COTE[1]]
    rognees = {x: trois["les_relances"][x] for x in LES_CHAINES}
    pts = {x: [m367.les_points(s) for s in rognees[x]] for x in LES_CHAINES}
    nap = {x: m367.les_points(trois["les_nappes"][x]) for x in LES_CHAINES}
    retrouves = {x: [m379.les_retrouves(trois["les_nappes"][x], tours)] + [m379.les_retrouves(s, tours) for s in rognees[x]] for x in LES_CHAINES}
    nombres = {x: m385.les_nombres(trois["les_nappes"][x], rognees[x], lv["m7"]) for x in LES_CHAINES}
    corriges = {x: m379.les_comptes(nap[x], pts[x]) for x in LES_CHAINES}
    m7 = {x: m385.les_comptes_de_m7(corriges[x], [n["le_nombre_de_feuilles"] for n in nombres[x]]) for x in LES_CHAINES}
    paires = {f"{a}|{b}": m379.les_paires(pts[a], pts[b]) for a, b in m379.LES_COUPLES}
    surfaces = m379.le_cote(paires, m7, {x: m379.la_verite(retrouves[x], m7[x], sens) for x in LES_CHAINES})
    redonne = ([[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"], s["lue"], s["sur_le_bon_tour"]] for s in surfaces]
               == c400["rognees"]["les_surfaces"])
    chaines = {x: {"385": {"les_tours": c379["les_retrouves"][x], "les_comptes": c385["les_comptes_de_m7"][x],
                           "les_sauts": les_sauts_juges(c379["les_retrouves"][x], c385["les_sauts"][x], sens)},
                   "rognees": {"les_tours": retrouves[x], "les_comptes": m7[x], "les_sauts": les_sauts_juges(retrouves[x], nombres[x], sens)}}
               for x in LES_CHAINES}
    d = {"la_question": __doc__.splitlines()[0], "le_cote": list(LE_COTE), "les_pannes": list(d331["les_pannes"]),
         "redonne_400": bool(redonne), "les_chaines": chaines, "la_suivie_de_385": chaines["suivie"]["385"]["les_sauts"]}
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

    s_ = lambda n, c: {"le_nombre_de_feuilles": n, "les_comptes": c}  # noqa: E731
    sa = les_sauts_juges([[0], [-1], [-1, -2], [-4], [-5]], [s_(1, {"1": 9}), s_(1, {"1": 5}), s_(2, {"2": 5}), s_(2, {"2": 6, "1": 4})], -1)
    v("★★★★ un saut est jugé si ses deux surfaces retrouvent un seul tour ; juste, de trop ou pas assez ; à cheval s'il est un mélange",
      [(x["les_tours"], x["dit"], x["a_cheval"]) for x in sa] == [(1, "juste", False), (None, None, False), (None, None, False),
                                                                  (1, "de_trop", True)], str([(x["les_tours"], x["dit"], x["a_cheval"]) for x in sa]))
    sb = les_sauts_juges([[0], [-3]], [s_(2, {"2": 105, "3": 60})], -1)
    v("★★★★ deux feuilles pour trois tours, c'est pas assez", sb[0]["dit"] == "pas_assez" and sb[0]["a_cheval"])
    v("★★★ un saut sans compte de m7 n'est pas jugé", les_sauts_juges([[0], [-1]], [s_(None, {"1": 30})], -1)[0]["dit"] is None)

    def d_(suivie, ok=True):
        return {"redonne_400": ok, "les_pannes": [], "la_suivie_de_385": suivie}
    j = lambda h, n, t, dit, ch: {"le_saut": h, "le_nombre_de_feuilles": n, "les_tours": t, "dit": dit, "a_cheval": ch}  # noqa: E731
    v("★★★★ la règle : de trop et à cheval, oui ; de trop sans être à cheval, en partie ; rien de trop, non",
      le_verdict(d_([j(1, 1, 1, "juste", False), j(6, 3, 2, "de_trop", True)]))["lissue"].endswith("comptée de trop")
      and le_verdict(d_([j(6, 3, 2, "de_trop", False)]))["lissue"].endswith("; en partie")
      and le_verdict(d_([j(6, 2, 3, "pas_assez", True)]))["lissue"]
      == "dans 385, les sauts faux de la suivie : saut 6, 2 feuilles pour 3 tours ; non, 385 ne comptait pas de trop")
    v("★★★ indécidable sans saut jugé, ou sans redonne", not le_verdict(d_([j(1, 1, None, None, False)]))["decidable"]
      and not le_verdict(d_([j(6, 2, 3, "pas_assez", True)], ok=False))["decidable"])

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
