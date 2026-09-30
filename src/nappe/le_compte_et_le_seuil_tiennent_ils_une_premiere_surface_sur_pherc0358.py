"""Sur PHerc0358, le compte des feuilles de 345 et le seuil de 50 points à zéro tiennent-ils des sauts de la chaîne relancée, et combien à la suite depuis la surface de départ ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE COMPTE DE `345` NE SOIT PORTÉ SUR UNE SEULE SURFACE DE PHERC0358. Ce qui était vu avant d'écrire :
tout ce que `296` à `353` publient, dont `R4-F538` (sur PHercParis4, le compte de `345` et le seuil de 50 points à zéro tiennent 39 des 44
sauts justes sains et 24 des 66 autres) et `R4-F539` (ce qu'ils tiennent y est sur son tour à 92 %). Sur PHerc0358, `331` a suivi cinq
côtés de graines, ceux dont le premier saut pose au pas, et le critère de `328` y tient 1, 5, 2, 1 et 6 sauts à la suite.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P150`. PHerc0358 n'a pas de tracé humain : c'est le rouleau de `#5`. Le critère de `352`
n'y demande aucun référent. S'il tient le premier saut d'un côté, cette surface est la première que le projet peut proposer sur un rouleau
sans tracé avec une précision connue ailleurs : sur Paris4, ce qu'il tient est sur son tour à 92 %.

## Ce qui est fait

- **Les chaînes** : celles de PHerc0358 que `331` suit, relancées de la même façon, par sa fonction sortie pour cette tranche ; la tenue
  de `328` rejouée doit redonner, saut par saut, ce que `331` publie, sans quoi la tranche est indécidable.
- **Le compte** : celui de `345`, sur la surface relancée de chaque saut et la surface d'où il part, au pas de PHerc0358 (20 voxels) ; la
  portée latérale d'un point en face, 10 voxels du niveau 2 sur Paris4, est rapportée au pas, soit 0,555 pas.
- **Le critère** : celui de `352`, sans rien changer : un saut tient si le compte en mesure au moins 50 points et que les trois quarts
  d'entre eux franchissent une feuille, et s'il a moins de 50 points à zéro feuille. Un saut sans surface relancée ne tient pas.
- **La suite** d'un côté : le nombre de sauts tenus à la suite depuis la surface de départ.
- **Le contrôle** : le compte doit mesurer PHerc0358 ; sous au moins la moitié des sauts qui ont une surface relancée, il doit mesurer au
  moins 50 points, sans quoi la tranche est indécidable.
- **La règle** : sur les côtés suivis, si le critère ne tient le premier saut d'aucun, **il ne tient aucune première surface** ; s'il tient
  le premier saut d'au moins la moitié, **il tient une première surface sur au moins la moitié des côtés** ; sinon, **sur certains côtés
  seulement**.

## Les issues

L'issue de la tranche : **sur PHerc0358, le critère tient le premier saut de k des N côtés suivis, et h sauts à la suite en médiane**,
puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Saut par saut, les comptes, les points à zéro, la tenue de `345` et celle de `328` ; et la suite que tient `328`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une surface que le critère tient sur PHerc0358 est sur sa feuille : les 92 % de Paris4 sont un
étalon, pas une mesure de PHerc0358.

Usage :
    uv run python src/nappe/le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.py --verifier
    uv run python src/nappe/le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.py \\
        --json docs/mesures/le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains as m352  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_331_A_PUBLIE = LES_MESURES / "une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.json"
LE_PAS = m300.LE_PAS_0358
LE_LATERAL_EN_PAS = m345.LE_LATERAL_L2 / m321.LE_PAS_L2
LE_SEUIL = m352.LE_SEUIL
LE_MINIMUM_DE_MESURES = m345.LE_MINIMUM_DE_MESURES


def le_saut(k: dict, lire_valeurs, pas: float = LE_PAS) -> dict:
    """Pour un saut de la chaîne relancée : le compte de `345` entre la surface relancée et la surface d'où il part, ses points à zéro, et si
    le critère de `352` le tient ; un saut sans surface relancée ne tient pas."""
    rl = k.get("la_relance")
    if rl is None or not rl["valide"].any():
        return {"les_feuilles": m345.le_resume(None), "les_zeros": 0, "tient_345": False, "tient": False}
    r = m345.les_comptes_point_par_point(k["le_depart"], rl, lire_valeurs, pas, lateral=LE_LATERAL_EN_PAS * pas)
    f = m345.le_resume(r)
    z = f["les_comptes"].get("0", 0)
    t345 = m345.tient(f)
    return {"les_feuilles": f, "les_zeros": z, "tient_345": t345, "tient": bool(t345 and z < LE_SEUIL)}


def la_suite(tenus: list[bool]) -> int:
    """Le nombre de sauts tenus à la suite depuis la surface de départ."""
    n = 0
    for t in tenus:
        if not t:
            break
        n += 1
    return n


def redonne_331(cotes: list[dict], publie: dict) -> bool:
    """La tenue de `328` rejouée redonne-t-elle, côté par côté et saut par saut, ce que `331` publie ?"""
    pub = {(c["le_rang"], c["le_cote"]): [s["tient"] for s in c["les_sauts"]] for c in publie["les_cotes"]["PHerc0358"]}
    rej = {(c["le_rang"], c["le_cote"]): [s["tient_328"] for s in c["les_sauts"]] for c in cotes}
    return bool(pub) and pub == rej


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_331"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 331"}
    avec = [s for c in d["les_cotes"] for s in c["les_sauts"] if s["a_une_surface"]]
    mesures = sum(1 for s in avec if s["les_feuilles"]["les_mesures"] >= LE_MINIMUM_DE_MESURES)
    if not avec or 2 * mesures < len(avec):
        return {"decidable": False, "lissue": f"indécidable : le compte mesure {mesures} des {len(avec)} sauts qui ont une surface"}
    n = len(d["les_cotes"])
    k = sum(1 for c in d["les_cotes"] if c["la_suite"] >= 1)
    h = statistics.median(c["la_suite"] for c in d["les_cotes"])
    hs = f"{h:g}".replace(".", ",")
    tete = f"sur PHerc0358, le critère tient le premier saut de {k} des {n} côtés suivis, et {hs} saut{'s' if h > 1 else ''} à la suite en médiane"
    suite = ("il ne tient aucune première surface" if k == 0
             else "il tient une première surface sur au moins la moitié des côtés" if 2 * k >= n
             else "il en tient une sur certains côtés seulement")
    return {"decidable": True, "k": k, "n": n, "h": h, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    chaines, lv0, stats0 = m331.les_chaines_de_0358()
    cotes = []
    for c in chaines:
        sauts = []
        for h, k in enumerate(c["la_chaine"], 1):
            e = le_saut(k, lv0)
            t328 = m331.la_tenue(k, lv0, LE_PAS)
            sauts.append({"le_saut": h, "a_une_surface": bool(k.get("la_relance") is not None and k["la_relance"]["valide"].any()),
                          **e, "tient_328": t328["tient"]})
        cote = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts,
                "la_suite": la_suite([s["tient"] for s in sauts]), "la_suite_de_328": la_suite([s["tient_328"] for s in sauts])}
        cotes.append(cote)
        print(json.dumps({x: cote[x] for x in ("le_rang", "le_cote", "la_suite", "la_suite_de_328")}, ensure_ascii=False),
              [(s["les_feuilles"]["les_mesures"], s["les_feuilles"]["la_part_dune_feuille"], s["les_zeros"], s["tient"]) for s in sauts],
              flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_pas": LE_PAS, "le_lateral_en_pas": round(LE_LATERAL_EN_PAS, 4), "le_seuil": LE_SEUIL,
                            "le_minimum_de_mesures": LE_MINIMUM_DE_MESURES},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_331": redonne_331(cotes, json.loads(CE_QUE_331_A_PUBLIE.read_text())), "les_cotes": cotes}
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

    v("★★★★ la suite s'arrête au premier saut refusé", la_suite([True, True, False, True]) == 2 and la_suite([]) == 0
      and la_suite([False, True]) == 0)
    v("★★★ la portée latérale est celle de Paris4, rapportée au pas", abs(LE_LATERAL_EN_PAS * m321.LE_PAS_L2 - m345.LE_LATERAL_L2) < 1e-9)

    def plan(z, n=21, marche=None):
        g = np.zeros((n, n, 3))
        for a in range(n):
            for b in range(n):
                g[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, marche if (marche is not None and a < 4) else z)
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    e = le_saut({"le_depart": plan(100.0), "la_relance": plan(120.0)}, feuilles, 20.0)
    v("★★★★ d'une feuille à la suivante, sans point resté : tenu", e["tient"] and e["tient_345"] and e["les_zeros"] == 0, str(e))
    e = le_saut({"le_depart": plan(100.0), "la_relance": plan(120.0, marche=100.0)}, feuilles, 20.0)
    v("★★★★ un morceau resté sur la feuille de départ, assez grand pour 50 points à zéro : 345 le tient, le seuil le refuse",
      e["tient_345"] and e["les_zeros"] >= LE_SEUIL and not e["tient"], str({k: e[k] for k in ("les_zeros", "tient_345", "tient")}))
    e = le_saut({"le_depart": plan(100.0), "la_relance": plan(140.0)}, feuilles, 20.0)
    v("★★★ par-dessus une feuille : 345 le refuse", not e["tient_345"] and not e["tient"])
    v("★★★ un saut sans surface relancée ne tient pas", not le_saut({"le_depart": plan(100.0), "la_relance": None}, feuilles, 20.0)["tient"])
    def clairseme(z):
        g = np.zeros((21, 11, 3))
        for a in range(21):
            for b in range(11):
                g[a, b] = (100.0 + 23.0 * b, 100.0 + 10.0 * a, z)
        return {"la_nappe": g, "valide": np.ones((21, 11), dtype=bool)}
    k_ = {"le_depart": clairseme(100.0), "la_relance": plan(120.0)}
    large = le_saut(k_, feuilles, 20.0)["les_feuilles"]["les_mesures"]
    etroit = m345.le_resume(m345.les_comptes_point_par_point(k_["le_depart"], k_["la_relance"], feuilles, 20.0))["les_mesures"]
    v("★★★★ la portée latérale suit le pas : au pas de 20, plus de points ont le départ en face qu'à la portée de Paris4",
      large > etroit, f"{large} contre {etroit}")

    pub = {"les_cotes": {"PHerc0358": [{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"tient": True}, {"tient": False}]}]}}
    v("★★★★ la tenue de 328 rejouée doit redonner celle que 331 publie, saut par saut",
      redonne_331([{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"tient_328": True}, {"tient_328": False}]}], pub)
      and not redonne_331([{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"tient_328": True}, {"tient_328": True}]}], pub)
      and not redonne_331([], {"les_cotes": {"PHerc0358": []}}))

    def s_(tient, mesures=80, surface=True):
        return {"tient": tient, "a_une_surface": surface, "les_feuilles": {"les_mesures": mesures}}

    def c_(suite, sauts=None):
        return {"la_suite": suite, "les_sauts": sauts or [s_(suite >= 1)]}
    base = lambda cs: {"les_pannes": [], "redonne_331": True, "les_cotes": cs}  # noqa: E731
    v("★★★★ aucun premier saut tenu : aucune première surface",
      le_verdict(base([c_(0)] * 5))["lissue"].endswith("il ne tient aucune première surface"))
    v("★★★★ la moitié des côtés, borne comprise : au moins la moitié",
      le_verdict(base([c_(1), c_(2), c_(0), c_(0)]))["lissue"].endswith("au moins la moitié des côtés"))
    v("★★★ moins de la moitié : sur certains côtés seulement",
      le_verdict(base([c_(3), c_(0), c_(0)]))["lissue"].endswith("certains côtés seulement"))
    v("★★★ la suite médiane", le_verdict(base([c_(3), c_(1), c_(0)]))["h"] == 1)
    v("★★★★ le compte qui ne mesure pas PHerc0358 : indécidable",
      not le_verdict(base([c_(0, [s_(False, 10)] * 3 + [s_(False, 80)])]))["decidable"]
      and le_verdict(base([c_(0, [s_(False, 10)] * 2 + [s_(False, 80)] * 2)]))["decidable"])
    v("★★★ les sauts sans surface ne comptent pas au contrôle",
      le_verdict(base([c_(0, [s_(False, 0, False)] * 5 + [s_(False, 80)])]))["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 331 : indécidable", not le_verdict(dict(base([c_(1)]), redonne_331=False))["decidable"])

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
