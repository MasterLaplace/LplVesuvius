"""Jusqu'à quel tour publié la chaîne qui croît de PHercParis4 descend-elle, avec les huit tours 5753_0 à 5753_-7 chargés et huit sauts, en partant du premier tour publié qu'elle touche ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES TOURS `5753_-4` À `5753_-7` NE SOIENT TÉLÉCHARGÉS, ET AVANT QU'UNE CHAÎNE DE PLUS DE TROIS SAUTS NE
SOIT COMPARÉE À UN TOUR PUBLIÉ. Ce qui était vu avant d'écrire : tout ce que `296` à `329` publient, dont `R4-F514` (côté intérieur, la
chaîne passe d'un tour publié au suivant 14 fois sur 14 sur `5753_0` à `5753_-3`), `R4-F515` (six nappes sur huit sont un ou deux tours
à l'extérieur de `5753_0`) et `R4-F513` (sur PHercParis4, la chaîne tient au pas jusqu'à huit sauts sur la graine 6 côté moins).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P127`. Combien de tours consécutifs une chaîne tirée de `m7` sans main traverse avant de
se tromper est la portée qu'un rouleau sans tracé peut espérer. `329` n'en chargeait que quatre, et sa règle ne lisait que les nappes
posées sur l'un d'eux ; celle-ci part du premier tour publié que la chaîne touche, ce que `329` a montré nécessaire.

## Ce qui est fait

- **Les tours** : `5753_0` à `5753_-7`, leur maillage au pas de 2,4 µm, les quatre premiers déjà rangés par `329`.
- **Les graines, la nappe et la chaîne** : celles de `329`, avec huit sauts de chaque côté au lieu de trois.
- **La comparaison** : celle de `329`, sans rien y changer.

## Les issues

Par côté : **le tour de départ** est le tour publié que la première surface de la chaîne qui en retrouve un seul retrouve, nappe comprise.
Puis la chaîne **descend un tour** à chaque surface suivante qui retrouve, parmi ses tours, celui qui suit le précédent (le tour attendu
moins un) ; elle s'arrête à la première surface qui ne le retrouve pas, lue ou non. **La descente** est le nombre de tours descendus. Par
graine, la plus longue des deux côtés. L'issue de la tranche : **sur k des huit graines, la chaîne touche un tour publié, et elle en
descend h en médiane, au plus H** ; et, déclaré avant : **elle traverse plus de trois tours** si la médiane de h sur ces k graines est
d'au moins quatre.

## Rapporté à côté, qui ne décide rien

Pour chaque côté, ce qui arrête la descente : la surface suivante retrouve un autre tour (**un saut faux**), ne retrouve aucun tour chargé
(**un tour manqué**), n'est pas lue, ou la chaîne atteint `5753_-7` (**le bout des tours chargés**).

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que valent les tours `5753_k` comme vérité ; ni la chaîne au-delà de `5753_-7`.

Usage :
    uv run python src/nappe/jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.py --verifier
    uv run python src/nappe/jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.py --telecharger
    uv run python src/nappe/jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.py \\
        --json docs/mesures/jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.json
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
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402

LES_TOURS = {**m329.LES_TOURS, -4: "20260603145540-5753_-4", -5: "20260603190005-5753_-5", -6: "20260603185441-5753_-6",
             -7: "20260602204401-5753_-7"}
LES_SAUTS = 8
LE_DERNIER = min(LES_TOURS)


def la_descente(surfaces: list[dict]) -> dict:
    """Le tour de départ, le nombre de tours descendus, et ce qui arrête la descente ; les surfaces dans l'ordre de la chaîne, chacune
    comme {tour : lecture}."""
    depart, k0 = None, None
    for k, s in enumerate(surfaces):
        w = m329.le_tour_de_la_nappe(s)
        if w is not None:
            depart, k0 = w, k
            break
    if depart is None:
        return {"le_tour_de_depart": None, "la_descente": 0, "larret": "aucun tour touché"}
    attendu, h = depart - 1, 0
    for s in surfaces[k0 + 1:]:
        if attendu < LE_DERNIER:
            return {"le_tour_de_depart": depart, "la_descente": h, "larret": "le bout des tours chargés"}
        if s.get(attendu) == "retrouve":
            h += 1
            attendu -= 1
            continue
        autres = [t for t, x in s.items() if x == "retrouve"]
        lue = any(x != "non lue" for x in s.values())
        larret = "un saut faux" if autres else ("un tour manqué" if lue else "non lue")
        return {"le_tour_de_depart": depart, "la_descente": h, "larret": larret}
    larret = "le bout des tours chargés" if attendu < LE_DERNIER else "le bout de la chaîne"
    return {"le_tour_de_depart": depart, "la_descente": h, "larret": larret}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    touchees = [g for g in d["les_graines"] if g["la_descente"] is not None and g["le_tour_touche"]]
    if not touchees:
        return {"decidable": False, "lissue": "indécidable : aucune chaîne ne touche un tour publié"}
    hs = [g["la_descente"] for g in touchees]
    h = float(np.median(hs))
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    traverse = h >= 4
    return {"decidable": True, "k": len(touchees), "h": h, "H": max(hs), "traverse": traverse,
            "lissue": f"sur {len(touchees)} des {len(d['les_graines'])} graines, la chaîne qui croît touche un tour publié, et elle en "
                      f"descend {f_(h)} en médiane, au plus {max(hs)} ; "
                      + ("elle traverse plus de trois tours" if traverse else "elle ne traverse pas plus de trois tours")}


def mesurer() -> dict:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    from zarr_depth import BUCKET, array_meta

    t0 = time.monotonic()
    tours = {r: m329.lire_un_tour(r, LES_TOURS) for r in LES_TOURS}
    seg, sok, _ = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    sn, snok = les_normales(seg, sok)
    pred = array_meta(f"{BUCKET}/{m321.LA_PREDICTION}", 0, 120.0)
    lire4, stats4 = lecteur_du_depot(pred, m321.LE_CACHE, "m7_L2", m321.LA_PREDICTION, 0)
    lv4 = lambda idx: m300.lire_m7(idx, (pred, lire4))  # noqa: E731
    graines = []
    for rang, (i, j) in enumerate(m321.les_graines(seg, sok, snok), 1):
        r = m322.la_nappe_de_paris4(seg[i, j] / m321.LE_FACTEUR, sn[i, j], lv4)
        lect_nappe = m329.les_lectures(r["la_nappe"][r["valide"]] * m321.LE_FACTEUR, tours)
        e = {"le_rang": rang, "la_nappe": {str(t): x for t, x in lect_nappe.items()}, "les_cotes": {}}
        for nom, cote in m306.LES_COTES:
            surf, ok = r["la_nappe"], r["valide"]
            spires = []
            with m321.le_rouleau_de_paris4():
                for _ in range(LES_SAUTS):
                    s = m306.le_saut_croissant(surf, ok, cote, lv4, tolerance=m322.LA_TOLERANCE_L2)
                    pts = s["la_spire"][s["valide"]] * m321.LE_FACTEUR
                    spires.append({"la_part_du_plan": round(float(s["valide"].mean()), 4),
                                   "les_tours": {str(t): x for t, x in m329.les_lectures(pts, tours).items()}})
                    if not s["valide"].any():
                        break
                    surf, ok = s["la_spire"], s["valide"]
            surfaces = [{t: x["la_lecture"] for t, x in lect_nappe.items()}] + [
                {int(t): x["la_lecture"] for t, x in sp["les_tours"].items()} for sp in spires]
            e["les_cotes"][nom] = dict({"les_spires": spires}, **la_descente(surfaces))
        meilleur = max(e["les_cotes"].values(), key=lambda c: c["la_descente"])
        e["la_descente"] = meilleur["la_descente"]
        e["le_tour_touche"] = any(c["le_tour_de_depart"] is not None for c in e["les_cotes"].values())
        graines.append(e)
        print(json.dumps({"le_rang": rang, "la_descente": e["la_descente"],
                          "par_cote": {c: (v["le_tour_de_depart"], v["la_descente"], v["larret"]) for c, v in e["les_cotes"].items()}},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_tours": {str(k): v for k, v in LES_TOURS.items()}, "les_sauts": LES_SAUTS},
         "les_tours_lus": {str(k): {"les_sommets": v["les_sommets"]} for k, v in tours.items()},
         "les_pannes": list(stats4["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats4.items() if k != "pannes"},
         "les_graines": graines}
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

    R, N, M_ = "retrouve", "ne retrouve pas", "non lue"
    d = la_descente([{0: N}, {0: R, -1: N}, {-1: R}, {-2: R, -3: R}, {-3: R}, {-4: N, -5: R}])
    v("★★★★ départ au premier tour touché, deux tours retrouvés à la fois acceptés, arrêt sur un saut faux",
      d == {"le_tour_de_depart": 0, "la_descente": 3, "larret": "un saut faux"}, str(d))
    d = la_descente([{0: R}, {-1: R}, {-2: N, -1: N}])
    v("★★★ un tour attendu non retrouvé, sans autre tour : un tour manqué", d["larret"] == "un tour manqué" and d["la_descente"] == 1)
    d = la_descente([{0: R}, {-1: M_, -2: M_}])
    v("★★★ une surface suivante non lue arrête aussi", d["larret"] == "non lue" and d["la_descente"] == 0)
    d = la_descente([{0: R, -1: R}, {0: N}])
    v("★★★ une nappe qui retrouve deux tours n'est pas un départ", d["le_tour_de_depart"] is None)
    surf = [{-6: R}, {-7: R}, {-7: N}]
    d = la_descente(surf)
    v("★★★★ après le dernier tour chargé : le bout des tours chargés", d["la_descente"] == 1 and d["larret"] == "le bout des tours chargés",
      str(d))
    d = la_descente([{0: R}, {-1: R}])
    v("★★★ la chaîne finit avant les tours : le bout de la chaîne", d["larret"] == "le bout de la chaîne" and d["la_descente"] == 1)
    g = lambda h, t: {"la_descente": h, "le_tour_touche": t}  # noqa: E731
    vd = le_verdict({"les_pannes": [], "les_graines": [g(5, True), g(4, True), g(3, True), g(0, False)]})
    v("★★★★ médiane 4 sur les graines qui touchent : elle traverse plus de trois tours", vd["traverse"] and vd["k"] == 3 and vd["H"] == 5,
      str(vd))
    vd = le_verdict({"les_pannes": [], "les_graines": [g(5, True), g(3, True), g(3, True)]})
    v("★★★ médiane 3 : non", not vd["traverse"])
    v("★★★ les huit tours, de 0 à -7", sorted(LES_TOURS) == list(range(-7, 1)) and LE_DERNIER == -7)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--telecharger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.telecharger:
        print(json.dumps(m329.telecharger(LES_TOURS), ensure_ascii=False))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
