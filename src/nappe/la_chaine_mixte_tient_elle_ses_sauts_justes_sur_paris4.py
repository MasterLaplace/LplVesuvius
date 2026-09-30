"""Sur PHercParis4, graines 4 à 8, la chaîne mixte, qui garde la spire quand le critère de 352 la tient et ne relance que sinon, tient-elle ses sauts justes, et donne-t-elle moins de surfaces à cheval que la chaîne relancée depuis un point ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA CHAÎNE MIXTE NE SOIT CONSTRUITE SUR PHERCPARIS4. Ce qui était vu avant d'écrire : tout ce que
`296` à `356` publient, dont `R4-F535` (sur les graines 4 à 8, 13 des 23 sauts justes de la chaîne relancée depuis un point donnent une
surface à cheval) et `R4-F542` (sur PHerc0358, la chaîne mixte tient 3 sauts à la suite en médiane, contre 0 pour la chaîne relancée, et
22 des 40 sauts, dont 20 spires gardées). Sur PHerc0358, rien ne dit si ses surfaces sont sur leur feuille.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P154`. Une chaîne qui va plus loin sur un rouleau sans tracé ne vaut que si elle ne va pas
plus loin sur la mauvaise feuille. Sur PHercParis4 les tours publiés disent, saut par saut, si la surface gardée est juste et si elle est à
cheval : c'est là que la chaîne mixte doit être jugée avant d'être crue sur PHerc0358.

## Ce qui est fait

- **La chaîne mixte** : celle de `356`, sur les nappes de départ, le saut et la relance depuis un point de `331` sur PHercParis4, par sa
  mesure qui gagne de quoi recevoir la chaîne de l'appelant ; le critère de `352` est lu au pas et à la portée de PHercParis4.
- **La justesse** : la lecture stricte de `344` sur la suite des surfaces gardées, la nappe de départ en tête, lue par les tours publiés
  comme dans `340`.
- **À cheval** : la définition de `349`, sur les points du compte de `345` de chaque surface gardée.
- **Le témoin** : la chaîne relancée depuis un point, sur les mêmes graines, telle que `344` et `349` la publient.
- **Le contrôle** : la nappe de départ de chaque côté est celle que `340` publie ; la lecture stricte du premier saut n'en dépend que par
  elle, et chaque côté doit avoir au moins un saut, sans quoi la tranche est indécidable.
- **La règle** : sur les graines 4 à 8, soit j la part des sauts jugés qui sont justes et c la part des sauts justes qui donnent une surface
  à cheval. Si la chaîne mixte a un j au moins aussi haut que le témoin et un c plus bas, **oui, elle est au moins aussi juste et moins à
  cheval** ; si elle a un j plus bas et un c au moins aussi haut, **non** ; sinon, **en partie**. Indécidable sous 5 sauts justes.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, la chaîne mixte est juste sous a des n sauts jugés et à cheval sous b de ses a sauts
justes, contre a' des n' et b' des a' pour la chaîne relancée depuis un point**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les sauts gardant leur spire et les sauts relancés, séparément ; la tenue du critère de `352` sur les sauts justes et faux ; les graines 1
à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que vaut la chaîne mixte sur PHerc0358, où rien ne la juge.

Usage :
    uv run python src/nappe/la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.py --verifier
    uv run python src/nappe/la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.py \\
        --json docs/mesures/la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.json
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

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import la_nappe_qui_croit_tient_elle_le_trace_humain_de_paris4 as m322  # noqa: E402
import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import jugee_strictement_jusquou_la_chaine_bornee_descend_elle as m340  # noqa: E402
import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille as m347  # noqa: E402
import les_sauts_justes_donnent_ils_des_surfaces_a_cheval as m349  # noqa: E402
import sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart as m355  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_344_A_PUBLIE = m345.CE_QUE_344_A_PUBLIE
CE_QUE_349_A_PUBLIE = LES_MESURES / "les_sauts_justes_donnent_ils_des_surfaces_a_cheval.json"
LE_TEMOIN = "relancée depuis un point"
LE_MINIMUM = 5


def compter4(depart: dict, arrivee: dict | None, lire_valeurs) -> dict:
    """Le compte de `345` au pas et à la portée de PHercParis4."""
    if arrivee is None or not arrivee["valide"].any():
        return m345.le_resume(None)
    return m345.le_resume(m345.les_comptes_point_par_point(depart, arrivee, lire_valeurs, m321.LE_PAS_L2))


def les_sauts_juges(cotes: list[dict], graines=m344.LES_GRAINES_PROPRES) -> list[dict]:
    return [s for c in cotes if c["le_rang"] in graines for s in c["les_sauts"] if s["la_justesse"] != "non jugé"]


def le_bilan(sauts: list[dict]) -> dict:
    """Les sauts jugés, les justes, et les justes à cheval ; les parts j et c."""
    justes = [s for s in sauts if s["la_justesse"] == "juste"]
    cheval = [s for s in justes if s.get("a_cheval")]
    return {"les_juges": len(sauts), "les_justes": len(justes), "les_justes_a_cheval": len(cheval),
            "j": round(len(justes) / len(sauts), 4) if sauts else None, "c": round(len(cheval) / len(justes), 4) if justes else None}


def le_temoin(d344: dict, d349: dict) -> dict:
    """La chaîne relancée depuis un point, sur les graines 4 à 8, telle que `344` et `349` la publient."""
    sauts = [dict(s) for g in d344["les_chaines"][LE_TEMOIN]["les_graines"] if g["le_rang"] in m344.LES_GRAINES_PROPRES
             for x in g["les_cotes"].values() for s in x["les_sauts"] if s["la_justesse"] != "non jugé"]
    cheval = {(s["le_rang"], s["le_cote"], s["le_saut"]) for s in d349["les_surfaces"] if s["la_chaine"] == LE_TEMOIN
              and s["la_surface"] is not None and s["la_surface"]["a_cheval"]}
    cles = [(g["le_rang"], c, s["le_saut"]) for g in d344["les_chaines"][LE_TEMOIN]["les_graines"] if g["le_rang"] in m344.LES_GRAINES_PROPRES
            for c, x in g["les_cotes"].items() for s in x["les_sauts"] if s["la_justesse"] != "non jugé"]
    for s, k in zip(sauts, cles):
        s["a_cheval"] = k in cheval
    return le_bilan(sauts)


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les nappes de départ ne sont pas celles que 340 publie"}
    m, t = d["les_bilans"]["la_chaine_mixte"], d["les_bilans"]["le_temoin"]
    if m["les_justes"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {m['les_justes']} sauts justes"}
    tete = (f"sur les graines 4 à 8, la chaîne mixte est juste sous {m['les_justes']} des {m['les_juges']} sauts jugés et à cheval sous "
            f"{m['les_justes_a_cheval']} de ses {m['les_justes']} sauts justes, contre {t['les_justes']} des {t['les_juges']} et "
            f"{t['les_justes_a_cheval']} des {t['les_justes']} pour la chaîne relancée depuis un point")
    if m["j"] >= t["j"] and m["c"] < t["c"]:
        suite = "oui, elle est au moins aussi juste et moins à cheval"
    elif m["j"] < t["j"] and m["c"] >= t["c"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def la_chaine_jugee(chainer=None, en_plus=None) -> dict:
    """La chaîne de PHercParis4 jugée saut par saut : justesse, tenue, à cheval, points posés et taille de la surface gardée. Sans
    `chainer(nappe, relancer, sauter, lire_valeurs)`, la chaîne mixte de `356` ; avec, écrit pour `358`, celle de l'appelant, dont chaque
    saut doit porter ce que la chaîne mixte porte. Avec `en_plus(saut, lire_valeurs)`, écrit pour `359`, ce qu'il rend de chaque saut est
    gardé sous `en_plus`. Rend les côtés, le contrôle, les pannes et la lecture de `m7`."""
    tours = {r: m329.lire_un_tour(r, m330.LES_TOURS) for r in m330.LES_TOURS}
    lv = {}

    def relancer4(lv4):
        lv["m7"] = lv4
        return lambda p_, n_: m322.la_nappe_de_paris4(p_, n_, lv4)

    def chainer4(r, rel4, sauter, lv4):
        if chainer is None:
            return m356.la_chaine_mixte(r, rel4, sauter, lv4, compter=compter4)
        return chainer(r, rel4, sauter, lv4)

    def observer(rang, nom, h, k):
        out = {"depuis": k["depuis"], "le_compte": k["le_compte"], "les_points": k["les_points"]}
        if en_plus is not None:
            out["en_plus"] = en_plus(k, lv["m7"])
        rl = k["la_relance"]
        if rl is None or not rl["valide"].any():
            return out
        r = m345.les_comptes_point_par_point(k["le_depart"], rl, lv["m7"], m321.LE_PAS_L2)
        if r is not None:
            out["_comptes"] = r["les_comptes"]
            out["_poses"] = m347.les_poses(r["les_points"] * m321.LE_FACTEUR, r["les_normales"], tours)
        return out

    d331 = m331.mesurer(relancer4=relancer4, rouleaux=("PHercParis4",), observer=observer, chainer4=chainer4)
    publiees = {n: json.loads((LES_MESURES / f).read_text()) for n, f in m340.LES_CHAINES.items()}
    nappes = {g["le_rang"]: {t: x["la_lecture"] for t, x in g["la_nappe"].items()} for g in publiees["sans relance"]["les_graines"]}
    cotes, controle = [], True
    for g in d331["les_graines"]["PHercParis4"]:
        for cote, c in g["les_cotes"].items():
            lect = m340.les_surfaces("mixte", d331, nappes, g["le_rang"], cote)
            controle &= g["le_rang"] in nappes and len(c["les_surfaces"]) >= 1
            sauts = []
            for h, s in enumerate(c["les_surfaces"], 1):
                j = m344.la_justesse(lect[h - 1], lect[h], m344.LE_SENS[cote])
                en_plus = {"les_retrouves": m340.les_retrouves(lect[h])} if "les_tours" in s else {}
                if "_comptes" in s:
                    en_plus.update({"les_comptes": s["_comptes"], "les_poses": s["_poses"]})
                a = m349.la_lecture(lect[h - 1], en_plus, m344.LE_SENS[cote]) if "_poses" in s else None
                sauts.append({"le_saut": h, "la_justesse": j, "depuis": s.get("depuis"), "les_points": s.get("les_points"),
                              "tenu": m355.tenue(s["le_compte"]),
                              "a_cheval": bool(a is not None and a["a_cheval"]),
                              "restes": a["restes"]["les_points"] if a else None, "au_dela": a["au_dela"]["les_points"] if a else None,
                              "les_points_poses": a["les_points_poses"] if a else None,
                              "le_tour_de_depart": a["le_tour_de_depart"] if a else None,
                              **({"en_plus": s["en_plus"]} if "en_plus" in s else {})})
            cotes.append({"le_rang": g["le_rang"], "le_cote": cote, "les_sauts": sauts})
            print(json.dumps({"le_rang": g["le_rang"], "le_cote": cote}, ensure_ascii=False),
                  [(s["depuis"], s["la_justesse"], s["tenu"], s["a_cheval"]) for s in sauts], flush=True)
    return {"les_pannes": d331["les_pannes"], "la_lecture_de_m7": d331["la_lecture_de_m7"], "le_controle": bool(controle),
            "les_cotes": cotes}


def mesurer() -> dict:
    t0 = time.monotonic()
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_temoin": LE_TEMOIN, "le_minimum": LE_MINIMUM},
         **la_chaine_jugee()}
    cotes = d["les_cotes"]
    temoin = le_temoin(json.loads(CE_QUE_344_A_PUBLIE.read_text()), json.loads(CE_QUE_349_A_PUBLIE.read_text()))
    d["les_bilans"] = {"la_chaine_mixte": le_bilan(les_sauts_juges(cotes)), "le_temoin": temoin,
                       "graines_1_a_3": le_bilan(les_sauts_juges(cotes, (1, 2, 3)))}
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

    s_ = lambda j, c=False: {"la_justesse": j, "a_cheval": c}  # noqa: E731
    b = le_bilan([s_("juste"), s_("juste", True), s_("faux : deux tours", True), s_("faux : un autre tour")])
    v("★★★★ j sur les sauts jugés, c sur les seuls sauts justes : un faux à cheval ne compte pas",
      b == {"les_juges": 4, "les_justes": 2, "les_justes_a_cheval": 1, "j": 0.5, "c": 0.5}, str(b))
    cotes = [{"le_rang": 5, "les_sauts": [s_("juste"), s_("non jugé")]}, {"le_rang": 2, "les_sauts": [s_("juste")]}]
    v("★★★ les sauts non jugés et les graines 1 à 3 ne comptent pas", len(les_sauts_juges(cotes)) == 1)

    d344 = {"les_chaines": {LE_TEMOIN: {"les_graines": [
        {"le_rang": 5, "les_cotes": {"moins": {"les_sauts": [{"le_saut": 1, "la_justesse": "non jugé"}, {"le_saut": 2, "la_justesse": "juste"},
                                                             {"le_saut": 3, "la_justesse": "juste"}, {"le_saut": 4, "la_justesse": "faux : deux tours"}]}}},
        {"le_rang": 2, "les_cotes": {"moins": {"les_sauts": [{"le_saut": 2, "la_justesse": "juste"}]}}}]}}}
    d349 = {"les_surfaces": [{"la_chaine": LE_TEMOIN, "le_rang": 5, "le_cote": "moins", "le_saut": 3, "la_surface": {"a_cheval": True}},
                             {"la_chaine": LE_TEMOIN, "le_rang": 5, "le_cote": "moins", "le_saut": 4, "la_surface": {"a_cheval": True}},
                             {"la_chaine": "bornée", "le_rang": 5, "le_cote": "moins", "le_saut": 2, "la_surface": {"a_cheval": True}}]}
    t = le_temoin(d344, d349)
    v("★★★★ le témoin : la chaîne relancée depuis un point des graines 4 à 8, à cheval par 349 saut par saut",
      t == {"les_juges": 3, "les_justes": 2, "les_justes_a_cheval": 1, "j": 0.6667, "c": 0.5}, str(t))

    def d_(jm, cm, jt, ct, n=20, ok=True):
        def bil(j, c):
            justes = round(j * n)
            return {"les_juges": n, "les_justes": justes, "les_justes_a_cheval": round(c * justes), "j": j, "c": c}
        return {"les_pannes": [], "le_controle": ok, "les_bilans": {"la_chaine_mixte": bil(jm, cm), "le_temoin": bil(jt, ct)}}
    v("★★★★ au moins aussi juste et moins à cheval : oui", le_verdict(d_(0.8, 0.3, 0.8, 0.5))["lissue"].endswith("moins à cheval"))
    v("★★★★ moins juste et au moins aussi à cheval : non", le_verdict(d_(0.7, 0.5, 0.8, 0.5))["lissue"].endswith("; non"))
    v("★★★ sinon : en partie", le_verdict(d_(0.7, 0.3, 0.8, 0.5))["lissue"].endswith("en partie")
      and le_verdict(d_(0.9, 0.6, 0.8, 0.5))["lissue"].endswith("en partie")
      and le_verdict(d_(0.8, 0.5, 0.8, 0.5))["lissue"].endswith("en partie"))
    v("★★★ moins de 5 sauts justes : indécidable", not le_verdict(d_(0.2, 0.3, 0.8, 0.5, n=20))["decidable"]
      and le_verdict(d_(0.25, 0.2, 0.8, 0.5, n=20))["decidable"])
    v("★★★ le contrôle tombé : indécidable", not le_verdict(d_(0.8, 0.3, 0.8, 0.5, ok=False))["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
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
