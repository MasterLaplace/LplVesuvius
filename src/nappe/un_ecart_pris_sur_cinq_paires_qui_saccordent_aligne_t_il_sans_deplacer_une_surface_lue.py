"""Un écart de comptes pris sur au moins cinq paires même feuille qui s'accordent aligne-t-il les comptes de deux chaînes sans mettre une surface lue de PHercParis4 hors de son tour, et que valide-t-il sur la graine 8 de PHerc0358 ?

⚠⚠⚠ CE FICHIER EST ÉCRIT APRÈS `387`, DONT LA SORTIE A DONNÉ L'IDÉE, ET AVANT QU'UN SEUL ÉCART MAJORITAIRE NE SOIT CALCULÉ. Ce qui était
vu avant d'écrire : tout ce que `296` à `387` publient, dont `R4-F573` (aligner sur une seule paire même feuille déplace 6 surfaces lues de
la tierce de la graine 8, côté moins, de PHercParis4, parce que cette paire est fausse) et `R4-F572` (sur la graine 8, côté moins, de
PHerc0358, la suivie compte 2 de plus que la compagne sur 8 paires même feuille de 9, 1 de moins que la tierce sur 6 de 8). ⚠ Cette tranche
ne lit pas `m7` : elle relit ce que `379`, `380`, `384` et `385` publient.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P185`. Une paire même feuille fausse ne doit pas suffire à décaler une chaîne ; plusieurs paires
qui disent le même écart sont un témoignage que le juge de `367` aurait du mal à fabriquer par erreur.

## Ce qui est fait

- **L'écart majoritaire** : pour la compagne et pour la tierce, l'écart des comptes avec la suivie sur chaque paire même feuille ; l'écart le
  plus fréquent est retenu s'il est porté par au moins 5 paires et par au moins les deux tiers des paires même feuille ; sinon, rien n'est
  décalé. Les comptes sont ceux de `m7`, de `385` et de `384`.
- **L'accord et la vérité** : ceux de `387`, l'accord de `374` sur les comptes alignés, jugé sur PHercParis4 dans le repère commun.
- **Les surfaces déplacées** : les surfaces lues, de tout statut, sur le bon tour sans alignement et hors de leur tour une fois alignées.
- **La règle**, sur PHercParis4 : aucune surface déplacée, et au moins 90 % des surfaces validées lues sur le bon tour, au moins autant que
  sans alignement, **oui** ; aucune surface déplacée mais moins de surfaces validées sur le bon tour, **en partie** ; une surface déplacée au
  moins, ou moins de 75 %, **non**. Indécidable sous 10 surfaces validées lues.

## Les issues

L'issue de la tranche : **alignés par l'écart majoritaire, d surfaces lues de PHercParis4 quittent leur tour, et a des n surfaces validées
lues sont sur le bon tour, contre a' des n'**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les côtés où l'écart majoritaire décale une chaîne ; sur PHerc0358, les surfaces validées avec et sans alignement, et le plus grand compte.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si l'origine de la suivie est la bonne ; ni si cinq paires qui s'accordent ne peuvent pas être toutes
fausses.

Usage :
    uv run python src/nappe/un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.py --verifier
    uv run python src/nappe/un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.py \\
        --json docs/mesures/un_ecart_pris_sur_cinq_paires_qui_saccordent_aligne_t_il_sans_deplacer_une_surface_lue.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402
import aligner_les_comptes_sur_la_premiere_paire_meme_feuille_valide_t_il_sur_le_bon_tour as m387  # noqa: E402

SUIVIE, COMPAGNE, TIERCE = m374.SUIVIE, m374.COMPAGNE, m374.TIERCE
LES_CHAINES = m374.LES_CHAINES
LE_MINIMUM_DE_PAIRES = 5
LA_PART_DES_PAIRES = 2 / 3
LA_PART, LA_PART_BASSE, LE_MINIMUM = m387.LA_PART, m387.LA_PART_BASSE, m387.LE_MINIMUM


def lecart_majoritaire(paires: list[dict], cs: list[int], cx: list[int]) -> dict:
    """L'écart le plus fréquent des comptes de la suivie et d'une autre chaîne sur leurs paires même feuille, retenu s'il est porté par
    au moins 5 paires et par les deux tiers d'entre elles, ce qui le rend seul de son rang ; sinon None."""
    es = [cs[p["le_saut_suivi"] - 1] - cx[p["le_saut_compagnon"] - 1] for p in paires if p["meme_feuille"]]
    if not es:
        return {"lecart": None, "porte_par": 0, "les_paires_meme_feuille": 0}
    (e, n), = Counter(es).most_common(1)
    retenu = e if n >= LE_MINIMUM_DE_PAIRES and n >= LA_PART_DES_PAIRES * len(es) else None
    return {"lecart": retenu, "porte_par": n, "les_paires_meme_feuille": len(es)}


def aligner(paires: dict, comptes: dict) -> tuple[dict, dict]:
    ecarts = {x: lecart_majoritaire(paires[f"{SUIVIE}|{x}"], comptes[SUIVIE], comptes[x]) for x in (COMPAGNE, TIERCE)}
    out = {SUIVIE: list(comptes[SUIVIE])}
    for x in (COMPAGNE, TIERCE):
        out[x] = [c + (ecarts[x]["lecart"] or 0) for c in comptes[x]]
    return out, ecarts


def les_deplacees(sans: list[dict], alignes: list[dict]) -> list[dict]:
    """Les surfaces lues sur le bon tour sans alignement et hors de leur tour une fois alignées."""
    avant = {(s["la_chaine"], s["le_saut"]): s for s in sans}
    return [s for s in alignes if s["lue"] and s["sur_le_bon_tour"] is False and avant[(s["la_chaine"], s["le_saut"])]["sur_le_bon_tour"]]


def le_verdict(d: dict) -> dict:
    a, b = d["paris4_alignes"][m374.VALIDEE], d["paris4_sans_alignement"][m374.VALIDEE]
    if a["lues"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {a['lues']} surfaces validées lues, moins de {LE_MINIMUM}"}
    n = d["les_deplacees"]
    tete = (f"alignés par l'écart majoritaire, {n} surface{'s' if n > 1 else ''} lue{'s' if n > 1 else ''} de PHercParis4 "
            f"quitte{'nt leur' if n > 1 else ' son'} tour, et {a['sur_le_bon_tour']} des {a['lues']} surfaces validées lues sont sur le bon "
            f"tour, contre {b['sur_le_bon_tour']} des {b['lues']}")
    p = a["sur_le_bon_tour"] / a["lues"]
    if n or p < LA_PART_BASSE:
        suite = "non"
    elif p >= LA_PART and a["sur_le_bon_tour"] >= b["sur_le_bon_tour"]:
        suite = "oui, l'écart majoritaire aligne sans déplacer une surface lue"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    d379, d380, d384, d385 = (json.loads(x.read_text()) for x in (m387.CE_QUE_379_A_PUBLIE, m387.CE_QUE_380_A_PUBLIE,
                                                                    m387.CE_QUE_384_A_PUBLIE, m387.CE_QUE_385_A_PUBLIE))
    p4, p4_sans, deplacees, cotes4 = [], [], [], []
    for c3, c5 in zip(d379["les_cotes"], d385["les_cotes"]):
        assert (c3["le_rang"], c3["le_cote"]) == (c5["le_rang"], c5["le_cote"])
        sens = m344.LE_SENS[c3["le_cote"]]
        alignes, ecarts = aligner(c3["les_paires"], c5["les_comptes_de_m7"])
        sa = m387.les_statuts(c3["les_paires"], alignes, c3["les_retrouves"], sens)
        ss = m387.les_statuts(c3["les_paires"], c5["les_comptes_de_m7"], c3["les_retrouves"], sens)
        dep = les_deplacees(ss, sa)
        p4 += sa
        p4_sans += ss
        deplacees += dep
        cotes4.append({"le_rang": c3["le_rang"], "le_cote": c3["le_cote"], "les_ecarts": ecarts,
                       "validees": [sum(s["le_statut"] == m374.VALIDEE for s in ss), sum(s["le_statut"] == m374.VALIDEE for s in sa)],
                       "les_deplacees": [[s["la_chaine"], s["le_saut"]] for s in dep]})
    p380 = {(c["le_rang"], c["le_cote"]): c["les_paires"] for c in d380["les_cotes"]}
    cotes0 = []
    for c in d384["les_cotes"]:
        comptes = {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(c["les_sauts"][x])] for x in LES_CHAINES}
        paires = p380[(c["le_rang"], c["le_cote"])]
        alignes, ecarts = aligner(paires, comptes)
        sa, ss = m387.les_statuts(paires, alignes, None, None), m387.les_statuts(paires, comptes, None, None)
        va = [s for s in sa if s["le_statut"] == m374.VALIDEE]
        cotes0.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_ecarts": ecarts,
                       "validees": [sum(s["le_statut"] == m374.VALIDEE for s in ss), len(va)],
                       "le_plus_loin": max((s["le_compte"] for s in va), default=None),
                       "les_validees_alignees": [[s["la_chaine"], s["le_saut"], s["le_compte"]] for s in va]})
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_minimum_de_paires": LE_MINIMUM_DE_PAIRES, "la_part_des_paires": round(LA_PART_DES_PAIRES, 4),
                            "la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
         "les_cotes_de_paris4": cotes4, "les_cotes_de_0358": cotes0, "les_deplacees": len(deplacees)}
    d["paris4_alignes"] = m387.le_bilan(p4)
    d["paris4_sans_alignement"] = m387.le_bilan(p4_sans)
    d["le_verdict"] = le_verdict(d)
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

    p = lambda h, k, m=True: {"le_saut_suivi": h, "le_saut_compagnon": k, "meme_feuille": m}  # noqa: E731
    cs = list(range(1, 11))
    cx = list(range(1, 11))
    six = [p(h + 2, h) for h in range(1, 7)]
    v("★★★★ l'écart majoritaire : six paires à +2 le portent", lecart_majoritaire(six, cs, cx) == {"lecart": 2, "porte_par": 6,
                                                                                                "les_paires_meme_feuille": 6})
    v("★★★★ une seule paire ne suffit pas", lecart_majoritaire([p(3, 1)], cs, cx)["lecart"] is None)
    v("★★★★ quatre paires ne suffisent pas", lecart_majoritaire(six[:4], cs, cx)["lecart"] is None)
    v("★★★★ cinq paires sur neuf ne font pas les deux tiers", lecart_majoritaire(six[:5] + [p(h, h) for h in range(1, 5)], cs, cx)["lecart"] is None)
    v("★★★★ les paires d'autres feuilles ne comptent pas", lecart_majoritaire(six + [p(h, h, False) for h in range(1, 9)], cs, cx)["lecart"] == 2)
    al, ec = aligner({f"{SUIVIE}|{COMPAGNE}": six, f"{SUIVIE}|{TIERCE}": [p(1, 2)], f"{COMPAGNE}|{TIERCE}": []},
                     {SUIVIE: cs, COMPAGNE: cx, TIERCE: cx})
    v("★★★★ l'alignement décale par l'écart majoritaire, et pas par une paire seule", al[COMPAGNE][:2] == [3, 4] and al[TIERCE][:2] == [1, 2])
    s_ = lambda x, h, lue, bon: {"la_chaine": x, "le_saut": h, "lue": lue, "sur_le_bon_tour": bon}  # noqa: E731
    v("★★★★ les surfaces déplacées : justes sans alignement, fausses alignées",
      [(s["la_chaine"], s["le_saut"]) for s in les_deplacees([s_(TIERCE, 1, True, True), s_(TIERCE, 2, True, False), s_(SUIVIE, 1, False, None)],
                                                              [s_(TIERCE, 1, True, False), s_(TIERCE, 2, True, False), s_(SUIVIE, 1, False, None)])]
      == [(TIERCE, 1)])

    def d_(a, n, b, nb, dep=0):
        return {"les_deplacees": dep, "paris4_alignes": {m374.VALIDEE: {"sur_le_bon_tour": a, "lues": n}},
                "paris4_sans_alignement": {m374.VALIDEE: {"sur_le_bon_tour": b, "lues": nb}}}
    v("★★★★ la règle : aucune déplacée et autant, oui ; une déplacée, non ; moins, en partie",
      le_verdict(d_(66, 66, 66, 66))["lissue"].endswith("sans déplacer une surface lue") and le_verdict(d_(66, 66, 66, 66, dep=1))["lissue"].endswith("; non")
      and le_verdict(d_(60, 60, 66, 66))["lissue"].endswith("; en partie") and le_verdict(d_(7, 10, 66, 66))["lissue"].endswith("; non")
      and "6 surfaces lues de PHercParis4 quittent leur tour" in le_verdict(d_(66, 66, 66, 66, dep=6))["lissue"])
    v("★★★ indécidable sous 10 surfaces validées lues", not le_verdict(d_(9, 9, 66, 66))["decidable"])

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
