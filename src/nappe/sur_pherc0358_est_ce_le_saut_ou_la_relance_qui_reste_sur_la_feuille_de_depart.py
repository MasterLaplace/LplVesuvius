"""Sur PHerc0358, quand une surface relancée garde au moins 50 points sur la feuille de départ, est-ce le saut qui ne la quitte pas, ou la relance qui y retombe ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE COMPTE DE `345` NE SOIT PORTÉ SUR UNE SEULE SPIRE DE PHERC0358. Ce qui était vu avant d'écrire :
tout ce que `296` à `354` publient, dont `R4-F540` (sur PHerc0358, le critère tient le premier saut de deux côtés et refuse le suivant de
l'un et de l'autre ; sous le deuxième saut de la graine 6, côté moins, 1125 des 1157 points comptés de la surface relancée restent sur la
feuille de départ). La spire que trouve chaque saut n'avait jamais été comptée.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P152`, OUVERTE PAR ELLE. `R4-P151`, l'encre des deux premières surfaces, attend une
décision de l'auteur : le détecteur de `296` est étalonné à 2,4 µm, PHerc0358 est scanné à 9,362 µm, et le rendre demande des lectures
neuves. En attendant, la chaîne de PHerc0358 ne va jamais au-delà d'un saut : un saut y cherche une spire à un pas, puis relance une nappe
entière depuis un seul point de cette spire. Si la spire est sur la feuille suivante et que la nappe relancée retombe sur la feuille de
départ, c'est la relance qu'il faut changer ; si la spire est déjà sur la feuille de départ, c'est le saut.

## Ce qui est fait

- **Les chaînes** : celles de PHerc0358 que `331` suit, par sa fonction ; les points à zéro de chaque surface relancée doivent redonner ce
  que `354` publie, sans quoi la tranche est indécidable.
- **Le compte** : celui de `345`, au pas et à la portée latérale de `354`, porté cette fois aussi sur la spire que trouve le saut, contre la
  surface d'où il part.
- **Les sauts jugés** : ceux dont la surface relancée garde au moins 50 points à zéro, le seuil de `351`. Sous chacun, la spire est
  **restée** si elle garde elle aussi au moins 50 points à zéro, **partie** sinon ; non lue si le compte mesure moins de 50 de ses points.
- **Le contrôle** : le compte doit mesurer les spires : au moins 50 points sous au moins la moitié des spires des sauts qui ont une surface,
  sans quoi la tranche est indécidable.
- **La règle** : au moins 5 sauts jugés lus, sinon indécidable. Si la spire est partie sous au moins les trois quarts, **c'est la relance
  qui retombe sur la feuille de départ** ; si elle est restée sous au moins les trois quarts, **c'est le saut qui ne la quitte pas** ;
  sinon, **l'un et l'autre**.

## Les issues

L'issue de la tranche : **sur PHerc0358, sous n sauts dont la surface relancée garde 50 points sur la feuille de départ, la spire est
partie sous p et restée sous r**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Saut par saut, les points à zéro et la part d'une feuille de la spire et de la surface relancée.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si une spire partie est sur la bonne feuille ; et ce qu'une autre relance ferait.

Usage :
    uv run python src/nappe/sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.py --verifier
    uv run python src/nappe/sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.py \\
        --json docs/mesures/sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.json
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

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358 as m354  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_354_A_PUBLIE = LES_MESURES / "le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.json"
LE_SEUIL = m354.LE_SEUIL
LE_MINIMUM = 5
LA_PART = 0.75
PARTIE, RESTEE, NON_LUE = "partie", "restée", "non lue"


def le_compte_de(depart: dict, arrivee: dict | None, lire_valeurs, pas: float = m354.LE_PAS) -> dict:
    """Le compte de `345` d'une surface contre la surface de départ, au pas et à la portée latérale de `354`."""
    if arrivee is None or not arrivee["valide"].any():
        return m345.le_resume(None)
    return m345.le_resume(m345.les_comptes_point_par_point(depart, arrivee, lire_valeurs, pas, lateral=m354.LE_LATERAL_EN_PAS * pas))


def tenue(f: dict) -> bool:
    """Rapporté à côté : le critère de `352` sur un compte, qu'il soit celui d'une spire ou d'une surface relancée."""
    return bool(m345.tient(f) and f["les_comptes"].get("0", 0) < LE_SEUIL)


def la_spire(k: dict) -> dict:
    return {"la_nappe": k["le_saut"]["la_spire"], "valide": k["le_saut"]["valide"]}


def la_lecture(spire: dict, relance: dict) -> str | None:
    """Sous un saut dont la surface relancée garde au moins 50 points à zéro : la spire est-elle partie ou restée ; None si le saut n'est
    pas jugé."""
    if relance["les_comptes"].get("0", 0) < LE_SEUIL:
        return None
    if spire["les_mesures"] < m354.LE_MINIMUM_DE_MESURES:
        return NON_LUE
    return RESTEE if spire["les_comptes"].get("0", 0) >= LE_SEUIL else PARTIE


def redonne_354(cotes: list[dict], publie: dict) -> bool:
    pub = {(c["le_rang"], c["le_cote"]): [s["les_zeros"] for s in c["les_sauts"]] for c in publie["les_cotes"]}
    rej = {(c["le_rang"], c["le_cote"]): [s["la_relance"]["les_comptes"].get("0", 0) for s in c["les_sauts"]] for c in cotes}
    return bool(pub) and pub == rej


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_354"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 354"}
    sauts = [s for c in d["les_cotes"] for s in c["les_sauts"] if s["a_une_surface"]]
    lues = sum(1 for s in sauts if s["la_spire"]["les_mesures"] >= m354.LE_MINIMUM_DE_MESURES)
    if not sauts or 2 * lues < len(sauts):
        return {"decidable": False, "lissue": f"indécidable : le compte mesure {lues} des {len(sauts)} spires"}
    juges = [s["la_lecture"] for s in sauts if s["la_lecture"] in (PARTIE, RESTEE)]
    if len(juges) < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {len(juges)} sauts jugés lus"}
    p, r = juges.count(PARTIE), juges.count(RESTEE)
    tete = (f"sur PHerc0358, sous {len(juges)} sauts dont la surface relancée garde 50 points sur la feuille de départ, la spire est partie "
            f"sous {p} et restée sous {r}")
    suite = ("c'est la relance qui retombe sur la feuille de départ" if p >= LA_PART * len(juges)
             else "c'est le saut qui ne la quitte pas" if r >= LA_PART * len(juges) else "l'un et l'autre")
    return {"decidable": True, "p": p, "r": r, "n": len(juges), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    chaines, lv0, stats0 = m331.les_chaines_de_0358()
    cotes = []
    for c in chaines:
        sauts = []
        for h, k in enumerate(c["la_chaine"], 1):
            rl = k.get("la_relance")
            sp = le_compte_de(k["le_depart"], la_spire(k), lv0)
            re = le_compte_de(k["le_depart"], rl, lv0)
            sauts.append({"le_saut": h, "a_une_surface": bool(rl is not None and rl["valide"].any()), "la_spire": sp, "la_relance": re,
                          "la_lecture": la_lecture(sp, re) if rl is not None and rl["valide"].any() else None,
                          "la_spire_tenue": tenue(sp), "la_relance_tenue": tenue(re)})
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"]}, ensure_ascii=False),
              [(s["la_spire"]["les_comptes"].get("0", 0), s["la_relance"]["les_comptes"].get("0", 0), s["la_lecture"]) for s in sauts],
              flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_seuil": LE_SEUIL, "le_minimum": LE_MINIMUM, "la_part": LA_PART, "le_pas": m354.LE_PAS,
                            "le_lateral_en_pas": round(m354.LE_LATERAL_EN_PAS, 4)},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_354": redonne_354(cotes, json.loads(CE_QUE_354_A_PUBLIE.read_text())), "les_cotes": cotes}
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

    f_ = lambda z, m=200: {"les_comptes": {"0": z, "1": m - z} if z else {"1": m}, "les_mesures": m}  # noqa: E731
    v("★★★★ une relance à moins de 50 points à zéro n'est pas jugée", la_lecture(f_(100), f_(49)) is None)
    v("★★★★ spire à 50 points à zéro sous une relance qui en garde autant : restée ; à 49 : partie",
      la_lecture(f_(50), f_(60)) == RESTEE and la_lecture(f_(49), f_(60)) == PARTIE)
    v("★★★ une spire mesurée sur moins de 50 points : non lue", la_lecture(f_(0, 49), f_(60)) == NON_LUE)
    t_ = lambda z, un, m: {"les_comptes": {"0": z, "1": un}, "les_mesures": m, "la_part_dune_feuille": un / m}  # noqa: E731
    v("★★★ à côté, le critère de 352 sur un compte : 345 et moins de 50 points à zéro",
      tenue(t_(0, 100, 100)) and not tenue(t_(50, 250, 300)) and tenue(t_(49, 251, 300)) and not tenue(t_(0, 70, 100)))

    def plan(z, n=21):
        g = np.zeros((n, n, 3))
        for a in range(n):
            for b in range(n):
                g[a, b] = (100.0 + 10.0 * b, 100.0 + 10.0 * a, z)
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    feuilles = lambda idx: (idx[..., 0] - 100) % 20 == 0  # noqa: E731
    k = {"le_depart": plan(100.0), "le_saut": {"la_spire": plan(120.0)["la_nappe"], "valide": plan(120.0)["valide"]},
         "la_relance": plan(100.0)}
    sp, re = le_compte_de(k["le_depart"], la_spire(k), feuilles, 20.0), le_compte_de(k["le_depart"], k["la_relance"], feuilles, 20.0)
    v("★★★★ une spire sur la feuille suivante et une relance retombée sur celle de départ : partie",
      sp["les_comptes"].get("0", 0) == 0 and re["les_comptes"].get("0", 0) >= LE_SEUIL and la_lecture(sp, re) == PARTIE,
      str((sp["les_comptes"], re["les_comptes"])))
    v("★★★ une surface absente : rien n'est compté", le_compte_de(plan(100.0), None, feuilles, 20.0)["les_mesures"] == 0)

    def clairseme(z):
        g = np.zeros((21, 11, 3))
        for a in range(21):
            for b in range(11):
                g[a, b] = (100.0 + 23.0 * b, 100.0 + 10.0 * a, z)
        return {"la_nappe": g, "valide": np.ones((21, 11), dtype=bool)}
    large = le_compte_de(clairseme(100.0), plan(120.0), feuilles, 20.0)["les_mesures"]
    etroit = m345.le_resume(m345.les_comptes_point_par_point(clairseme(100.0), plan(120.0), feuilles, 20.0))["les_mesures"]
    v("★★★★ la portée latérale est celle de 354, rapportée au pas", large > etroit, f"{large} contre {etroit}")

    pub = {"les_cotes": [{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"les_zeros": 0}, {"les_zeros": 1125}]}]}
    rj = lambda zs: [{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"la_relance": {"les_comptes": {"0": z} if z else {}}} for z in zs]}]  # noqa: E731
    v("★★★★ les points à zéro des relances doivent redonner 354", redonne_354(rj([0, 1125]), pub) and not redonne_354(rj([0, 1124]), pub))

    def s_(lecture, surface=True, mesures=200):
        return {"a_une_surface": surface, "la_lecture": lecture, "la_spire": {"les_mesures": mesures}}
    base = lambda ss: {"les_pannes": [], "redonne_354": True, "les_cotes": [{"les_sauts": ss}]}  # noqa: E731
    v("★★★★ les trois quarts parties : la relance retombe",
      le_verdict(base([s_(PARTIE)] * 6 + [s_(RESTEE)] * 2))["lissue"].endswith("la relance qui retombe sur la feuille de départ"))
    v("★★★★ les trois quarts restées : le saut ne la quitte pas",
      le_verdict(base([s_(RESTEE)] * 6 + [s_(PARTIE)] * 2))["lissue"].endswith("le saut qui ne la quitte pas"))
    v("★★★ sinon : l'un et l'autre", le_verdict(base([s_(RESTEE)] * 3 + [s_(PARTIE)] * 3))["lissue"].endswith("l'un et l'autre")
      and le_verdict(base([s_(PARTIE)] * 5 + [s_(RESTEE)] * 3))["lissue"].endswith("l'un et l'autre"))
    v("★★★ les sauts non jugés et non lus ne comptent pas", le_verdict(base([s_(PARTIE)] * 5 + [s_(None)] * 4 + [s_(NON_LUE)] * 2))["n"] == 5)
    v("★★★ moins de 5 sauts jugés lus : indécidable", not le_verdict(base([s_(PARTIE)] * 4 + [s_(None)] * 4))["decidable"])
    v("★★★★ le compte qui ne mesure pas les spires : indécidable",
      not le_verdict(base([s_(PARTIE)] * 5 + [s_(None, mesures=10)] * 6))["decidable"]
      and le_verdict(base([s_(PARTIE)] * 5 + [s_(None, mesures=10)] * 5))["decidable"])
    v("★★★ les sauts sans surface ne comptent pas au contrôle",
      le_verdict(base([s_(PARTIE)] * 5 + [s_(None, surface=False, mesures=0)] * 9))["decidable"])
    v("★★★ des chaînes qui ne redonnent pas 354 : indécidable", not le_verdict(dict(base([s_(PARTIE)] * 5), redonne_354=False))["decidable"])

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
