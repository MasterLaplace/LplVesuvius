"""Sur PHercParis4, graines 4 à 8, les points d'une croissance à cheval s'écartent-ils de la surface de départ autrement que les points de sa spire, et cet écart, sans référent, les sépare-t-il des croissances saines ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL ÉCART NE SOIT LU. Ce qui était vu avant d'écrire : tout ce que `296` à `359` publient, dont
`R4-F545` (le critère de `352`, lu sur la seule croissance, refuse 0 des 12 croissances à cheval de la chaîne de `358` et 3 des 13 saines :
compter les feuilles de `m7` jusqu'au départ ne voit pas le cheval) et `R4-F535` (une surface à cheval pose de 5 à 45 % de ses points
hors du tour attendu, 17 % en médiane).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P157`. Une croissance à cheval pose des points sur le tour de départ, ou au-delà du tour
attendu. Sa spire, elle, est à un tour du départ. Un point resté sur le tour de départ devrait être près de la surface de départ, un point
passé au-delà deux fois plus loin : l'écart au départ, rapporté à celui de la spire du même saut, ne demande pas à `m7` de voir une feuille,
et ne demande aucun tracé.

## Ce qui est fait

- **La chaîne qui regrandit** : celle de `358`, rejouée par la fonction de `357`, comme dans `359`.
- **L'écart** : sous chaque saut qui garde une surface regrandie, toute la surface est comptée contre la surface de départ par le compte
  de `345`, qui rend, pour chaque point pris qui a le départ en face, son écart signé au départ le long de sa normale. L'écart de la spire
  est la médiane des écarts de ses points semés ; un point de la croissance est **écarté** si son écart s'éloigne de celui de la spire de
  plus de la moitié de celui-ci.
- **Le critère** : une croissance est refusée si 50 de ses points au moins sont écartés, le seuil de `349` et de `352`. Une croissance
  dont la spire n'a aucun point en face n'est pas lue, et n'est pas refusée.
- **Les croissances jugées** : celles de `359`, à cheval au sens de `349` ou saines.
- **Le contrôle** : la chaîne rejouée redonne, côté par côté et saut par saut, ce que `358` publie.
- **La règle** : celle de `359`. r la part des croissances à cheval refusées, r' celle des saines ; si r > ½ et r' < ½, **oui, il les
  sépare** ; si r ≤ r', **non** ; sinon, **en partie**. Indécidable sous 5 croissances à cheval ou 5 saines.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, l'écart à la spire refuse a des n croissances à cheval et a' des n' saines**, puis ce que
dit la règle.

## Rapporté à côté, qui ne décide rien

L'écart de la spire, en voxels, en médiane ; la part des points écartés sous les croissances à cheval et sous les saines ; les
croissances non lues.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que ferait la chaîne si elle refusait ces croissances en chemin ; ni ce que vaut l'écart sur
PHerc0358.

Usage :
    uv run python src/nappe/lecart_de_la_croissance_a_son_depart_separe_t_il_les_croissances_a_cheval.py --verifier
    uv run python src/nappe/lecart_de_la_croissance_a_son_depart_separe_t_il_les_croissances_a_cheval.py \\
        --json docs/mesures/lecart_de_la_croissance_a_son_depart_separe_t_il_les_croissances_a_cheval.json
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

import sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart as m355  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402
import le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval as m359  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
LA_TOLERANCE = 0.5                 # part de l'écart de la spire
LE_SEUIL = m355.LE_SEUIL           # points écartés


def lecart_de_la_croissance(k: dict, lire_valeurs, comptes=m359.les_comptes4) -> dict | None:
    """Sous un saut qui garde une surface regrandie, l'écart de la spire au départ, la médiane des écarts de ses points semés, et combien
    de points de la croissance s'en éloignent de plus de `LA_TOLERANCE` fois cet écart ; refusée à `LE_SEUIL` points écartés. None sous un
    autre saut."""
    rl = k.get("la_relance")
    if k.get("depuis") != m356.DEPUIS_LA_CROISSANCE or rl is None or "les_semes" not in rl:
        return None
    r = comptes(k["le_depart"], rl, lire_valeurs)
    if r is None:
        return {"lecart_de_la_spire": None, "les_en_face": 0, "les_ecartes": 0, "lue": False, "mesuree": False, "tenue": True}
    semes = rl["les_semes"].ravel()[r["les_mailles"]]
    croissance = (rl["valide"] & ~rl["les_semes"]).ravel()[r["les_mailles"]]
    e = np.asarray(r["les_ecarts"], dtype=float)
    vus = r["en_face"] & np.isfinite(e)
    spire = e[vus & semes]
    if not len(spire):
        return {"lecart_de_la_spire": None, "les_en_face": int((vus & croissance).sum()), "les_ecartes": 0, "lue": False,
                "mesuree": False, "tenue": True}
    es = float(np.median(spire))
    ec = e[vus & croissance]
    ecartes = int((np.abs(ec - es) > LA_TOLERANCE * abs(es)).sum())
    return {"lecart_de_la_spire": round(es, 3), "les_en_face": int(len(ec)), "les_ecartes": ecartes, "lue": True,
            "mesuree": bool(len(ec) >= LE_SEUIL), "tenue": ecartes < LE_SEUIL}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_358"):
        return {"decidable": False, "lissue": "indécidable : la chaîne rejouée ne redonne pas ce que 358 publie"}
    c, s = d["la_separation"]["a_cheval"], d["la_separation"]["saines"]
    if c["les_croissances"] < m359.LE_MINIMUM or s["les_croissances"] < m359.LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {c['les_croissances']} croissances à cheval et {s['les_croissances']} saines"}
    tete = (f"sur les graines 4 à 8, l'écart à la spire refuse {c['les_refusees']} des {c['les_croissances']} croissances à cheval et "
            f"{s['les_refusees']} des {s['les_croissances']} saines")
    if c["r"] > 0.5 and s["r"] < 0.5:
        suite = "oui, il les sépare"
    elif c["r"] <= s["r"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    r = m357.la_chaine_jugee(chainer=m358.la_chaine_qui_regrandit, en_plus=lecart_de_la_croissance)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_tolerance": LA_TOLERANCE, "le_seuil": LE_SEUIL, "le_minimum": m359.LE_MINIMUM},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": r["le_controle"],
         "redonne_358": m359.redonne_358(r["les_cotes"], json.loads(m359.CE_QUE_358_A_PUBLIE.read_text())), "les_cotes": r["les_cotes"]}
    d["la_separation"] = m359.la_separation(m359.les_croissances_jugees(r["les_cotes"]))
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

    n = 20
    valide = np.ones((n, n), dtype=bool)
    semes = np.zeros((n, n), dtype=bool)
    semes[:5] = True
    k = {"depuis": m356.DEPUIS_LA_CROISSANCE, "le_depart": {}, "la_relance": {"la_nappe": np.zeros((n, n, 3)), "valide": valide,
                                                                              "les_semes": semes}}
    vus = []

    def comptes_de(ecart, en_face=lambda i: True):
        def comptes(dep, arr, lv):
            vus.append(lv)
            return {"les_mailles": np.arange(n * n), "les_ecarts": [ecart(i) for i in range(n * n)],
                    "en_face": np.array([en_face(i) for i in range(n * n)])}
        return comptes
    sain = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0))
    v("★★★★ une croissance à l'écart de sa spire : aucun point écarté, tenue, lue sur m7",
      vus == ["m7"] and sain["lecart_de_la_spire"] == 20.0 and sain["les_ecartes"] == 0 and sain["tenue"] and sain["lue"]
      and sain["les_en_face"] == 300, str(sain))
    reste = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 or i >= 160 else 1.0))
    loin = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 or i >= 160 else 39.0))
    v("★★★★ 60 points revenus vers le départ, ou partis deux fois plus loin : écartés, et la croissance refusée",
      reste["les_ecartes"] == 60 and not reste["tenue"] and loin["les_ecartes"] == 60 and not loin["tenue"], str((reste, loin)))
    aberrants = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 200.0 if i < 30 else 20.0))
    v("★★★★ l'écart de la spire est une médiane : 30 points semés aberrants ne l'emportent pas",
      aberrants["lecart_de_la_spire"] == 20.0 and aberrants["les_ecartes"] == 0 and aberrants["tenue"], str(aberrants))
    bord = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 else 30.0))
    v("★★★ un écart d'exactement la moitié de celui de la spire n'est pas écarté", bord["les_ecartes"] == 0, str(bord))
    peu = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 or i >= 149 else 1.0))
    v("★★★ 49 points écartés : tenue", peu["les_ecartes"] == 49 and peu["tenue"], str(peu))
    signe = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: -20.0 if i < 100 or i >= 160 else 20.0))
    v("★★★★ l'écart est signé : un point de l'autre côté du départ est écarté", signe["les_ecartes"] == 60 and not signe["tenue"], str(signe))
    semis_seuls = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 else 1.0, en_face=lambda i: i >= 100))
    v("★★★ une spire sans point en face : la croissance n'est pas lue, et n'est pas refusée",
      not semis_seuls["lue"] and semis_seuls["tenue"] and semis_seuls["lecart_de_la_spire"] is None, str(semis_seuls))
    hors = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 else 1.0, en_face=lambda i: i < 160))
    v("★★★ seuls les points en face comptent", hors["les_en_face"] == 60 and hors["les_ecartes"] == 60, str(hors))
    nan = lecart_de_la_croissance(k, "m7", comptes_de(lambda i: 20.0 if i < 100 else (float("nan") if i < 200 else 1.0)))
    v("★★★ un écart inconnu ne compte pas", nan["les_en_face"] == 200 and nan["les_ecartes"] == 200, str(nan))
    v("★★★ sous une spire gardée ou une relance, rien",
      lecart_de_la_croissance(dict(k, depuis=m356.DEPUIS_LA_SPIRE), "m7", comptes_de(lambda i: 1.0)) is None
      and lecart_de_la_croissance(dict(k, depuis=m356.DEPUIS_LA_RELANCE), "m7", comptes_de(lambda i: 1.0)) is None)

    def d_(rc, rs, nc=10, ns=10, rej=True):
        return {"les_pannes": [], "redonne_358": rej,
                "la_separation": {"a_cheval": {"les_croissances": nc, "les_refusees": round(rc * nc), "r": rc},
                                  "saines": {"les_croissances": ns, "les_refusees": round(rs * ns), "r": rs}}}
    v("★★★★ la règle de 359 : oui, non, en partie", le_verdict(d_(0.6, 0.4))["lissue"].endswith("oui, il les sépare")
      and le_verdict(d_(0.3, 0.3))["lissue"].endswith("; non") and le_verdict(d_(0.5, 0.2))["lissue"].endswith("en partie")
      and le_verdict(d_(0.9, 0.5))["lissue"].endswith("en partie"))
    v("★★★ moins de 5 croissances à cheval ou saines, une chaîne qui ne redonne pas 358 : indécidable",
      not le_verdict(d_(0.9, 0.1, nc=4))["decidable"] and not le_verdict(d_(0.9, 0.1, ns=4))["decidable"]
      and not le_verdict(d_(0.9, 0.1, rej=False))["decidable"] and le_verdict(d_(0.9, 0.1, nc=5, ns=5))["decidable"])

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
