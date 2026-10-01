"""Sur PHerc0358, à seize sauts, l'accord qui rend aux sauts mélangés de m7 le poids de leur genre de 369 valide-t-il autant de surfaces en se contredisant moins ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES SAUTS MÉLANGÉS DE PHERC0358 NE SOIENT RECOMPTÉS PAR LEUR GENRE. Ce qui était vu avant d'écrire :
tout ce que `296` à `394` publient, dont `R4-F575` (à seize sauts, aux comptes de `m7`, l'accord valide 89 surfaces et en contredit 161),
`R4-F578` (un saut nul de `m7` sur cinq franchit une feuille), `R4-F579` (un saut nul de `m7` est presque toujours un mélange) et `R4-F580`
(sur PHercParis4, le seul compte faux de `m7` est un mélange, et les 86 sauts nets sont justes).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P192`. Si les comptes faux de `m7` sont des mélanges, un mélange peut être compté autrement : par
le genre que `369` donne à son saut, comme `384` le fait déjà quand `m7` ne dit rien. Si l'accord se contredit moins sans perdre de surfaces
validées, le compte d'un mélange est à prendre au genre.

## Ce qui est fait

- **Les chaînes et les sauts** : les chaînes à seize sauts de `389`, rejouées ; leurs nombres de feuilles, leurs comptes, leurs paires et les
  statuts de leurs surfaces doivent redonner ceux de `389`. Pour chaque saut, son genre de `369` et le compte de `m7` point par point.
- **Mélange** : comme `394`, un saut dont le compte majoritaire est porté par moins des deux tiers de ses points mesurés.
- **Les deux accords** : celui de `389`, aux comptes de `m7` ; et le même où chaque mélange ajoute le poids de son genre (nul 0, simple 1,
  double 2) au lieu de son nombre de feuilles. Paires, couples et accord de `374` inchangés.
- **La règle** : si le second accord contredit moins de surfaces et en valide au moins autant, **oui** ; s'il en contredit moins mais en
  valide moins, **en partie** ; s'il n'en contredit pas moins, **non**. Indécidable si une lecture échoue, si les chaînes rejouées ne
  redonnent pas `389`, ou si aucun mélange ne change de poids.

## Les issues

L'issue de la tranche : **rendre leur genre aux m mélanges dont le poids change fait passer les surfaces contredites de c à c' et les
validées de v à v'**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Le genre des sauts nuls que `392` dit restés et de ceux qu'il dit franchis ; côté par côté, les validées et les contredites des deux accords.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface validée est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés.

Usage :
    uv run python src/nappe/rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358.py --verifier
    uv run python src/nappe/rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358.py \\
        --json docs/mesures/rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358.json
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
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402
import quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358 as m374  # noqa: E402
import laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus as m380  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402
import les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4 as m394  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
CE_QUE_392_A_PUBLIE = LES_MESURES / "les_sauts_que_m7_compte_nuls_laissent_ils_les_chaines_sur_leur_feuille.json"
LES_CHAINES = m374.LES_CHAINES
LA_PART_DU_MELANGE = m394.LA_PART_DU_MELANGE


def est_un_melange(s: dict) -> bool:
    p = m394.la_part_majoritaire(s["les_comptes"])
    return s["le_nombre_de_feuilles"] is not None and p is not None and p < LA_PART_DU_MELANGE


def au_genre(sauts: list[dict]) -> list[dict]:
    """Les sauts d'une chaîne où chaque mélange perd son nombre de feuilles, pour que `384` lui donne le poids de son genre."""
    return [{**s, "le_nombre_de_feuilles": None} if est_un_melange(s) else s for s in sauts]


def les_changes(sauts: list[dict]) -> list[dict]:
    """Les mélanges dont le poids du genre n'est pas leur nombre de feuilles."""
    return [s for s in sauts if est_un_melange(s) and m369.LES_PAS[s["le_genre"]] != s["le_nombre_de_feuilles"]]


def les_statuts(cote: dict) -> dict:
    return {k: sum(s["le_statut"] == k for s in cote["les_surfaces"]) for k in (m374.VALIDEE, m374.CONTREDITE)}


def le_bilan(cotes: list[dict]) -> dict:
    out = {}
    for cle in ("aux_comptes_de_m7", "au_genre"):
        out[cle] = {k: sum(c[cle][k] for c in cotes) for k in (m374.VALIDEE, m374.CONTREDITE)}
    out["les_melanges"] = sum(c["les_melanges"] for c in cotes)
    out["les_changes"] = sum(len(c["les_changes"]) for c in cotes)
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_389"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 389"}
    b = d["le_bilan"]
    if not b["les_changes"]:
        return {"decidable": False, "lissue": "indécidable : aucun mélange ne change de poids"}
    a, g = b["aux_comptes_de_m7"], b["au_genre"]
    c, c_, v, v_ = a[m374.CONTREDITE], g[m374.CONTREDITE], a[m374.VALIDEE], g[m374.VALIDEE]
    tete = (f"rendre leur genre aux {b['les_changes']} mélanges dont le poids change fait passer les surfaces contredites de {c} à {c_} et "
            f"les validées de {v} à {v_}")
    suite = "oui" if c_ < c and v_ >= v else "en partie" if c_ < c else "non"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def le_genre_des_nuls(cotes: list[dict], d392: dict) -> dict:
    """Le genre de `369` des sauts nuls que `392` dit restés et de ceux qu'il dit franchis."""
    g = {(c["le_rang"], c["le_cote"], x, h): s["le_genre"] for c in cotes for x in LES_CHAINES for h, s in enumerate(c["les_sauts"][x], 1)}
    out = {"restes": {}, "franchis": {}}
    for s in d392["les_sauts"]:
        if s["le_nombre_de_feuilles"] != 0 or s["lavance"] not in (0, 1):
            continue
        k = "restes" if s["lavance"] == 0 else "franchis"
        genre = g.get((s["le_rang"], s["le_cote"], s["la_chaine"], s["le_saut"]))
        out[k][genre] = out[k].get(genre, 0) + 1
    return out


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    d389, d392 = (json.loads(x.read_text()) for x in (CE_QUE_389_A_PUBLIE, CE_QUE_392_A_PUBLIE))
    tous = [(c["le_rang"], c["le_cote"]) for c in d389["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(m389.enchainer), cotes=set(tous))
    redonne, cotes = len(chaines) == len(tous), []
    for c, e, c389 in zip(chaines, m383._LES_CHAINES_ENTIERES, d389["les_cotes"]):
        surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
        s369 = {x: m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x]) for x in LES_CHAINES}
        nombres = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
        sauts = {x: [{"le_saut": a["le_saut"], "le_genre": a["le_genre"], "le_nombre_de_feuilles": b["le_nombre_de_feuilles"],
                      "les_mesures": b["les_mesures"], "les_comptes": b["les_comptes"]} for a, b in zip(s369[x], nombres[x])] for x in LES_CHAINES}
        paires = {"|".join(k): m368.les_paires(surf[k[0]], surf[k[1]]) for k in m373.LES_COUPLES}
        a = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: m384.les_comptes_de_m7(sauts[x]) for x in LES_CHAINES})
        g = m380.le_cote(c["le_rang"], c["le_cote"], paires, {x: m384.les_comptes_de_m7(au_genre(sauts[x])) for x in LES_CHAINES})
        redonne &= ((c["le_rang"], c["le_cote"]) == (c389["le_rang"], c389["le_cote"])
                    and all([s["le_nombre_de_feuilles"] for s in sauts[x]] == c389["les_nombres"][x] for x in LES_CHAINES)
                    and {k: [[p["le_saut_suivi"], p["le_saut_compagnon"], p["meme_feuille"]] for p in v] for k, v in paires.items()}
                    == c389["les_paires"]
                    and [(s["la_chaine"], s["le_saut"], s["le_statut"]) for s in a["les_surfaces"]]
                    == [(s["la_chaine"], s["le_saut"], s["le_statut"]) for s in c389["les_surfaces"]])
        changes = [{"la_chaine": x, **s} for x in LES_CHAINES for s in les_changes(sauts[x])]
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts,
                      "les_melanges": sum(est_un_melange(s) for x in LES_CHAINES for s in sauts[x]), "les_changes": changes,
                      "aux_comptes_de_m7": les_statuts(a), "au_genre": les_statuts(g),
                      "les_comptes_au_genre": {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(au_genre(sauts[x]))]
                                               for x in LES_CHAINES},
                      "les_surfaces_au_genre": [[s["la_chaine"], s["le_saut"], s["le_compte"], s["le_statut"]] for s in g["les_surfaces"]]})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne), "melanges": cotes[-1]["les_melanges"],
                          "changes": len(changes), "m7": cotes[-1]["aux_comptes_de_m7"], "genre": cotes[-1]["au_genre"]},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_part_du_melange": round(LA_PART_DU_MELANGE, 4)},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_389": bool(redonne), "les_cotes": cotes}
    d["le_bilan"] = le_bilan(cotes)
    d["le_genre_des_nuls"] = le_genre_des_nuls(cotes, d392)
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

    s_ = lambda n, g, c: {"le_nombre_de_feuilles": n, "le_genre": g, "les_comptes": c}  # noqa: E731
    sauts = [s_(1, "simple", {"1": 9, "0": 1}), s_(0, "simple", {"0": 5, "1": 4}), s_(None, "double", {}), s_(2, "double", {"2": 3, "1": 3}),
             s_(0, "nul", {"0": 6, "1": 4})]
    v("★★★★ un mélange : un nombre de feuilles dit, porté par moins des deux tiers des points",
      [est_un_melange(s) for s in sauts] == [False, True, False, True, True])
    ag = au_genre(sauts)
    v("★★★★ au genre : un mélange perd son nombre de feuilles, les autres le gardent",
      [s["le_nombre_de_feuilles"] for s in ag] == [1, None, None, None, None])
    v("★★★★ au genre, les comptes de 384 donnent aux mélanges le poids de leur genre",
      [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(ag)] == [1, 2, 4, 6, 6]
      and [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(sauts)] == [1, 1, 3, 5, 5])
    v("★★★★ les changés : les mélanges dont le poids du genre diffère du nombre de feuilles", les_changes(sauts) == [sauts[1]])

    def d_(c, c_, v_a, v_g, ch=3):
        return {"redonne_389": True, "les_pannes": [], "le_bilan": {"les_changes": ch, "aux_comptes_de_m7": {m374.VALIDEE: v_a, m374.CONTREDITE: c},
                                                                    "au_genre": {m374.VALIDEE: v_g, m374.CONTREDITE: c_}}}
    v("★★★★ la règle : moins contredites et autant validées, oui ; moins contredites mais moins validées, en partie ; sinon, non",
      le_verdict(d_(10, 8, 5, 5))["lissue"].endswith("; oui") and le_verdict(d_(10, 8, 5, 4))["lissue"].endswith("; en partie")
      and le_verdict(d_(10, 10, 5, 9))["lissue"].endswith("; non")
      and "aux 3 mélanges dont le poids change fait passer les surfaces contredites de 10 à 8 et les validées de 5 à 4"
      in le_verdict(d_(10, 8, 5, 4))["lissue"])
    v("★★★ indécidable sans redonne, ou si aucun mélange ne change de poids",
      not le_verdict({**d_(10, 8, 5, 5), "redonne_389": False})["decidable"] and not le_verdict(d_(10, 8, 5, 5, ch=0))["decidable"])
    cotes = [{"le_rang": 4, "le_cote": "moins", "les_sauts": {"suivie": [{"le_genre": "simple"}, {"le_genre": "nul"}], "compagne": [],
                                                               "tierce": [{"le_genre": "double"}]}}]
    d392 = {"les_sauts": [{"le_rang": 4, "le_cote": "moins", "la_chaine": "suivie", "le_saut": 1, "le_nombre_de_feuilles": 0, "lavance": 1},
                          {"le_rang": 4, "le_cote": "moins", "la_chaine": "suivie", "le_saut": 2, "le_nombre_de_feuilles": 0, "lavance": 0},
                          {"le_rang": 4, "le_cote": "moins", "la_chaine": "tierce", "le_saut": 1, "le_nombre_de_feuilles": 1, "lavance": 1},
                          {"le_rang": 4, "le_cote": "moins", "la_chaine": "tierce", "le_saut": 1, "le_nombre_de_feuilles": 0, "lavance": -1}]}
    v("★★★ le genre des nuls restés et franchis, sans les sauts d'une feuille ni les reculs",
      le_genre_des_nuls(cotes, d392) == {"restes": {"nul": 1}, "franchis": {"simple": 1}}, str(le_genre_des_nuls(cotes, d392)))

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
