"""Sur PHerc0358, les points d'un saut mélangé de m7 qui franchissent une feuille et ceux qui n'en franchissent aucune occupent-ils deux plages séparées de la surface, ou sont-ils entremêlés ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES POINTS D'UN SAUT MÉLANGÉ NE SOIENT LUS À LEUR PLACE. Ce qui était vu avant d'écrire : tout ce que
`296` à `395` publient, dont `R4-F581` (le compte majoritaire de `m7` reste le meilleur compte connu ; 96 des 343 sauts comptés sont des
mélanges), `R4-F579` (un saut nul de `m7` est presque toujours un mélange) et `R4-F564` (`378` : un saut dont un quart des points s'écarte
de plus d'un demi-pas de son écart médian est rare sur les côtés qui tiennent leurs comptes).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P193`. Un mélange a deux lectures. Si ses deux comptes occupent deux plages de la surface, la
surface est à cheval sur deux feuilles, et c'est elle qu'il faut scinder ; si ses points sont entremêlés, c'est le compte de `m7` qui est
bruité, et aucune scission n'y fera rien.

## Ce qui est fait

- **Les chaînes et les comptes** : les chaînes à seize sauts de `389`, rejouées ; pour chaque saut, les comptes de `m7` point par point de
  `345`, avec la position de chaque point. Leurs répartitions doivent redonner celles que `395` publie.
- **Les mélanges jugés** : les sauts que `395` dit mélangés, dont les deux comptes les plus portés ont chacun au moins 20 points.
- **La séparation** d'un saut : sur les points de ses deux comptes les plus portés, chaque point est relié à ses 6 plus proches voisins dans
  l'espace ; la part des liens qui joignent deux points de même compte, rapportée à celle qu'un tirage au hasard des comptes donnerait :
  `(observée − attendue) / (1 − attendue)`. Elle vaut 0 pour des points entremêlés au hasard et approche 1 pour deux plages nettes.
- **La règle** : un mélange est **en deux plages** si sa séparation vaut au moins 0,5, **entremêlé** si elle est sous 0,2. Si au moins
  75 % des mélanges jugés sont en deux plages, **oui, les mélanges sont des surfaces à cheval** ; si au moins 75 % sont entremêlés, **non,
  leurs points sont entremêlés** ; sinon, **en partie**. Indécidable sous 10 mélanges jugés, si une lecture échoue, ou si les comptes ne
  redonnent pas `395`.

## Les issues

L'issue de la tranche : **sur m mélanges jugés, p sont en deux plages et e entremêlés**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La séparation des sauts nets dont le compte minoritaire a au moins 20 points ; pour chaque mélange, l'écart médian à la surface de départ des
points de chacun de ses deux comptes, en pas.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : laquelle des deux plages est sur la bonne feuille ; PHerc0358 n'a pas de tours publiés.

Usage :
    uv run python src/nappe/les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.py --verifier
    uv run python src/nappe/les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.py \\
        --json docs/mesures/les_points_dun_saut_melange_de_m7_forment_ils_deux_plages_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402
import les_sauts_melanges_de_m7_se_trompent_ils_plus_souvent_sur_paris4 as m394  # noqa: E402
import rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358 as m395  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_395_A_PUBLIE = LES_MESURES / "rendre_aux_melanges_de_m7_le_poids_de_leur_genre_contredit_il_moins_sur_pherc0358.json"
LES_CHAINES = m395.LES_CHAINES
LES_VOISINS = 6
LE_MINIMUM_PAR_COMPTE = 20
EN_PLAGES, ENTREMELE = 0.5, 0.2
LA_PART, LE_MINIMUM = 0.75, 10


def la_separation(points: np.ndarray, comptes: list[int], voisins: int = LES_VOISINS) -> float | None:
    """La part des liens aux plus proches voisins qui joignent deux points de même compte, rapportée à celle d'un tirage au hasard."""
    n = len(comptes)
    if n <= voisins:
        return None
    c = np.asarray(comptes)
    _, idx = cKDTree(points).query(points, k=voisins + 1)
    observee = float((c[idx[:, 1:]] == c[:, None]).mean())
    tailles = np.array(list(Counter(comptes).values()), dtype=float)
    attendue = float((tailles * (tailles - 1)).sum() / (n * (n - 1)))
    return None if attendue >= 1 else round((observee - attendue) / (1 - attendue), 4)


def les_deux_comptes(r: dict) -> tuple[list[int], np.ndarray, list[int], np.ndarray]:
    """Les deux comptes les plus portés d'un saut (le plus petit d'abord à égalité), les positions de leurs points, leurs comptes et leurs
    écarts à la surface de départ."""
    vus = [(i, c) for i, c in enumerate(r["les_comptes"]) if c is not None]
    n = Counter(c for _, c in vus)
    deux = sorted(sorted(n, key=lambda k: (-n[k], k))[:2])
    garde = [i for i, c in vus if c in deux]
    return deux, r["les_points"][garde], [r["les_comptes"][i] for i in garde], r["les_ecarts"][garde]


def le_jugement(r: dict, pas: float) -> dict:
    deux, q, c, d = les_deux_comptes(r)
    n = Counter(c)
    out = {"les_deux_comptes": deux, "les_points": {str(k): n[k] for k in deux}}
    if len(deux) < 2 or min(n[k] for k in deux) < LE_MINIMUM_PAR_COMPTE:
        return {**out, "juge": False, "la_separation": None}
    s = la_separation(q, c)
    ecarts = {str(k): round(float(np.median(np.abs(d[np.asarray(c) == k]))) / pas, 3) for k in deux}
    return {**out, "juge": s is not None, "la_separation": s, "les_ecarts_en_pas": ecarts}


def le_genre(s: float | None) -> str | None:
    if s is None:
        return None
    return "en_plages" if s >= EN_PLAGES else "entremele" if s < ENTREMELE else "entre_les_deux"


def le_bilan(melanges: list[dict]) -> dict:
    juges = [m for m in melanges if m["juge"]]
    g = Counter(le_genre(m["la_separation"]) for m in juges)
    return {"melanges": len(melanges), "juges": len(juges), "en_plages": g["en_plages"], "entremeles": g["entremele"],
            "entre_les_deux": g["entre_les_deux"]}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_395"):
        return {"decidable": False, "lissue": "indécidable : les comptes ne redonnent pas 395"}
    b = d["le_bilan"]
    if b["juges"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {b['juges']} mélanges jugés, moins de {LE_MINIMUM}"}
    tete = f"sur {b['juges']} mélanges jugés, {b['en_plages']} sont en deux plages et {b['entremeles']} entremêlés"
    suite = ("oui, les mélanges sont des surfaces à cheval" if b["en_plages"] >= LA_PART * b["juges"]
             else "non, leurs points sont entremêlés" if b["entremeles"] >= LA_PART * b["juges"] else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def lexemple(r: dict, rl: dict) -> dict:
    """Pour la figure : la place de chaque point compté dans la grille d'arrivée, et son compte."""
    w = rl["la_nappe"].shape[1]
    return {"les_cases": [[int(m // w), int(m % w), int(c)] for m, c in zip(r["les_mailles"], r["les_comptes"]) if c is not None]}


def mesurer() -> dict:
    t0 = time.monotonic()
    m383._LES_CHAINES_ENTIERES.clear()
    d395 = json.loads(CE_QUE_395_A_PUBLIE.read_text())
    tous = [(c["le_rang"], c["le_cote"]) for c in d395["les_cotes"]]
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(m389.enchainer), cotes=set(tous))
    redonne, melanges, nets, exemples = len(chaines) == len(tous), [], [], {}
    for c, e, c395 in zip(chaines, m383._LES_CHAINES_ENTIERES, d395["les_cotes"]):
        redonne &= (c["le_rang"], c["le_cote"]) == (c395["le_rang"], c395["le_cote"])
        for x in LES_CHAINES:
            avant = e["les_nappes"][x]
            redonne &= len(e["les_chaines"][x]) == len(c395["les_sauts"][x])
            for h, (k, s395) in enumerate(zip(e["les_chaines"][x], c395["les_sauts"][x]), 1):
                rl = k.get("la_relance")
                r = None if avant is None else m345.les_comptes_point_par_point(avant, rl, lv0, m383.LE_PAS, lateral=m383.LE_LATERAL)
                avant = rl
                redonne &= m345.le_resume(r)["les_comptes"] == s395["les_comptes"]
                if r is None or s395["le_nombre_de_feuilles"] is None:
                    continue
                cle = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_chaine": x, "le_saut": h,
                       "le_nombre_de_feuilles": s395["le_nombre_de_feuilles"], "les_comptes": s395["les_comptes"]}
                j = le_jugement(r, m383.LE_PAS)
                if m395.est_un_melange(s395):
                    melanges.append({**cle, **j})
                    exemples[(c["le_rang"], c["le_cote"], x, h)] = (r, rl)
                elif j["juge"]:
                    nets.append({**cle, **j})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne), "melanges": len(melanges)},
                         ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_voisins": LES_VOISINS, "le_minimum_par_compte": LE_MINIMUM_PAR_COMPTE, "en_plages": EN_PLAGES,
                            "entremele": ENTREMELE, "la_part": LA_PART, "le_minimum": LE_MINIMUM},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_395": bool(redonne), "les_melanges": melanges, "les_nets": nets}
    d["le_bilan"] = le_bilan(melanges)
    juges = sorted((m for m in melanges if m["juge"]), key=lambda m: (m["la_separation"], m["le_rang"], m["le_cote"], m["la_chaine"],
                                                                         m["le_saut"]))
    if juges:
        for nom, m in (("le_plus_entremele", juges[0]), ("le_plus_separe", juges[-1])):
            r, rl = exemples[(m["le_rang"], m["le_cote"], m["la_chaine"], m["le_saut"])]
            d[nom] = {k: m[k] for k in ("le_rang", "le_cote", "la_chaine", "le_saut", "la_separation", "les_deux_comptes")} | lexemple(r, rl)
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

    g = np.array([[i, j, 0.0] for i in range(20) for j in range(20)])
    moities = [0 if j < 10 else 1 for i in range(20) for j in range(20)]
    damier = [(i + j) % 2 for i in range(20) for j in range(20)]
    hasard = list(np.random.default_rng(7).integers(0, 2, 400))
    sm, sd, sh = la_separation(g, moities), la_separation(g, damier), la_separation(g, hasard)
    v("★★★★ deux moitiés nettes : séparation au moins 0,5", sm is not None and sm >= EN_PLAGES, str(sm))
    v("★★★★ des comptes tirés au hasard : séparation sous 0,2", sh is not None and abs(sh) < ENTREMELE, str(sh))
    v("★★★★ un damier : séparation négative", sd is not None and sd < 0, str(sd))
    r = {"les_points": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0]], dtype=float),
         "les_comptes": [1, 0, None, 2, 0, 1], "les_ecarts": np.array([20.0, 1.0, 5.0, 40.0, -3.0, -22.0])}
    deux, q, c, d_ = les_deux_comptes(r)
    v("★★★★ les deux comptes les plus portés, le plus petit d'abord à égalité ; les points non comptés et du troisième compte écartés",
      deux == [0, 1] and c == [1, 0, 0, 1] and q[:, 0].tolist() == [0.0, 1.0, 4.0, 5.0] and d_.tolist() == [20.0, 1.0, -3.0, -22.0])
    peu = {"les_points": g[:35], "les_comptes": [0] * 25 + [1] * 10, "les_ecarts": np.zeros(35)}
    v("★★★★ un mélange n'est jugé qu'avec au moins 20 points dans chacun de ses deux comptes",
      not le_jugement(peu, 20.0)["juge"] and le_jugement({**peu, "les_comptes": [0] * 15 + [1] * 20}, 20.0)["juge"] is False
      and le_jugement({**peu, "les_comptes": [0] * 15 + [1] * 20}, 20.0)["les_points"] == {"0": 15, "1": 20})
    rr = {"les_points": g, "les_comptes": moities, "les_ecarts": np.array([2.0 if m == 0 else 20.0 for m in moities])}
    jj = le_jugement(rr, 20.0)
    v("★★★★ jugé, avec l'écart médian de chaque compte en pas", jj["juge"] and jj["les_ecarts_en_pas"] == {"0": 0.1, "1": 1.0}, str(jj))
    v("★★★ le genre d'une séparation", [le_genre(x) for x in (0.6, 0.5, 0.3, 0.19, None)]
      == ["en_plages", "en_plages", "entre_les_deux", "entremele", None])

    def d__(p, e, n, ok=True):
        return {"redonne_395": ok, "les_pannes": [], "le_bilan": {"juges": n, "en_plages": p, "entremeles": e}}
    v("★★★★ la règle : trois quarts en plages, oui ; trois quarts entremêlés, non ; sinon, en partie",
      le_verdict(d__(9, 1, 12))["lissue"].endswith("surfaces à cheval") and le_verdict(d__(1, 9, 12))["lissue"].endswith("entremêlés")
      and le_verdict(d__(5, 5, 12))["lissue"].endswith("; en partie")
      and "sur 12 mélanges jugés, 9 sont en deux plages et 1 entremêlés" in le_verdict(d__(9, 1, 12))["lissue"])
    v("★★★ indécidable sous 10 jugés ou sans redonne", not le_verdict(d__(9, 0, 9))["decidable"]
      and not le_verdict(d__(9, 1, 12, ok=False))["decidable"])

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
