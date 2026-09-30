"""Sur PHercParis4, graines 4 à 8, le critère de 352 appliqué à la seule partie regrandie d'une spire, hors des mailles semées depuis elle, refuse-t-il les croissances à cheval en gardant les saines ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CROISSANCE NE SOIT COMPTÉE SEULE. Ce qui était vu avant d'écrire : tout ce que `296` à `358`
publient, dont `R4-F544` (la chaîne qui regrandit sa spire tenue garde 25 surfaces regrandies sous ses sauts jugés des graines 4 à 8, dont
12 à cheval, toutes tenues par le critère de `352` compté sur toute la surface) et `R4-F538` (le critère de `352` tient 23 des 60 surfaces
à cheval). ⚠ Sur une partie plus petite, le seuil de 50 points à zéro est plus lâche et la part d'une feuille se calcule sur moins de
points : le critère peut aussi bien refuser davantage que moins.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P156`. Sur toute la surface regrandie, les points de la spire, sains, diluent ceux de la
croissance ; si la croissance comptée seule trahit le cheval sans référent, la chaîne mixte peut regagner la surface que `358` lui rend
sans quitter sa feuille.

## Ce qui est fait

- **La chaîne qui regrandit** : celle de `358`, rejouée telle quelle, par la fonction de `357`, qui gagne pour cela de quoi garder une
  observation de plus sur chaque saut.
- **La croissance seule** : sous chaque saut qui garde une surface regrandie, toute la surface est comptée contre la surface de départ par
  le compte de `345`, au pas et à la portée de PHercParis4, et ce compte n'est lu que sur ses mailles posées hors des mailles semées depuis
  la spire ; le critère de `352` sur ce compte lu.

⚠⚠ UNE PREMIÈRE PASSE COMPTAIT LA CROISSANCE COMME UNE SURFACE À PART, ET NE MESURAIT PAS CE QU'ELLE NOMMAIT. Une normale ne se calcule
qu'en une maille dont les quatre voisines sont posées ; une croissance de deux mailles de large n'en a presque pas, et le critère refusait
faute de mesures (53 points de normale pour 310 mailles, en médiane). Elle est gardée dans
`docs/mesures/le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval_premiere_passe.json`. La règle n'a pas changé.
- **Les croissances jugées** : celles des graines 4 à 8 dont le saut est jugé par les tours publiés ; à cheval au sens de `349`, ou saines.
- **Le contrôle** : la chaîne rejouée redonne, côté par côté et saut par saut, ce que `358` publie.
- **La règle** : soit r la part des croissances à cheval que le critère refuse, et r' la part des saines qu'il refuse. Si r > ½ et
  r' < ½, **oui, il les sépare** ; si r ≤ r', **non** ; sinon, **en partie**. Indécidable sous 5 croissances à cheval ou 5 saines.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, compté sur la seule croissance, le critère de 352 refuse a des n croissances à cheval et
a' des n' saines**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Les croissances refusées faute de 50 points mesurés, à part ; la taille des croissances ; leurs points à zéro et leur part d'une feuille.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que ferait la chaîne si elle refusait ces croissances en chemin ; les sauts suivants
changeraient, et c'est une autre mesure.

Usage :
    uv run python src/nappe/le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.py --verifier
    uv run python src/nappe/le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.py \\
        --json docs/mesures/le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.json
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

import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart as m355  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_358_A_PUBLIE = LES_MESURES / "regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.json"
LE_MINIMUM = 5
LES_CLES_REJOUEES = m358.LES_CLES_REJOUEES + ("les_points",)


def les_comptes4(depart: dict, arrivee: dict, lire_valeurs) -> dict | None:
    """Le compte point par point de `345` au pas et à la portée de PHercParis4."""
    return m345.les_comptes_point_par_point(depart, arrivee, lire_valeurs, m357.m321.LE_PAS_L2)


def la_croissance_seule(k: dict, lire_valeurs, comptes=les_comptes4) -> dict | None:
    """Sous un saut qui garde une surface regrandie, le compte de `345` de toute cette surface, pour que chaque maille ait sa normale, lu
    sur ses seules mailles posées hors des mailles semées depuis la spire ; et ce qu'en dit le critère de `352`. None sous un autre saut."""
    rl = k.get("la_relance")
    if k.get("depuis") != m356.DEPUIS_LA_CROISSANCE or rl is None or "les_semes" not in rl:
        return None
    croissance = (rl["valide"] & ~rl["les_semes"]).ravel()
    r = comptes(k["le_depart"], rl, lire_valeurs)
    if r is None:
        f = m345.le_resume(None)
    else:
        sel = croissance[r["les_mailles"]]
        f = m345.le_resume({"les_points": r["les_points"][sel], "en_face": r["en_face"][sel],
                            "les_comptes": [c for c, s in zip(r["les_comptes"], sel) if s]})
    return {"les_mailles": int(croissance.sum()), "le_compte": f, "mesuree": bool(f["les_mesures"] >= m345.LE_MINIMUM_DE_MESURES),
            "tenue": m355.tenue(f)}


def les_croissances_jugees(cotes: list[dict], graines=m357.m344.LES_GRAINES_PROPRES) -> list[dict]:
    return [s for c in cotes if c["le_rang"] in graines for s in c["les_sauts"]
            if s["la_justesse"] == "juste" and s["depuis"] == m356.DEPUIS_LA_CROISSANCE and s.get("en_plus")]


def la_separation(croissances: list[dict]) -> dict:
    """Pour les croissances à cheval et les saines : combien, combien le critère refuse, dont faute de mesures, et la part refusée."""
    out = {}
    for nom, a_cheval in (("a_cheval", True), ("saines", False)):
        g = [s for s in croissances if bool(s["a_cheval"]) == a_cheval]
        refusees = [s for s in g if not s["en_plus"]["tenue"]]
        out[nom] = {"les_croissances": len(g), "les_refusees": len(refusees),
                    "faute_de_mesures": sum(1 for s in refusees if not s["en_plus"]["mesuree"]),
                    "r": round(len(refusees) / len(g), 4) if g else None}
    return out


def redonne_358(cotes: list[dict], publie: dict) -> bool:
    """La chaîne rejouée redonne-t-elle, côté par côté et saut par saut, ce que `358` publie ?"""
    cle = lambda c: (c["le_rang"], c["le_cote"])  # noqa: E731
    garde = lambda c: [{k: s.get(k) for k in LES_CLES_REJOUEES} for s in c["les_sauts"]]  # noqa: E731
    pub = {cle(c): garde(c) for c in publie["les_cotes"]["la_chaine_qui_regrandit"]}
    return bool(pub) and pub == {cle(c): garde(c) for c in cotes}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_358"):
        return {"decidable": False, "lissue": "indécidable : la chaîne rejouée ne redonne pas ce que 358 publie"}
    c, s = d["la_separation"]["a_cheval"], d["la_separation"]["saines"]
    if c["les_croissances"] < LE_MINIMUM or s["les_croissances"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {c['les_croissances']} croissances à cheval et {s['les_croissances']} saines"}
    tete = (f"sur les graines 4 à 8, compté sur la seule croissance, le critère de 352 refuse {c['les_refusees']} des "
            f"{c['les_croissances']} croissances à cheval et {s['les_refusees']} des {s['les_croissances']} saines")
    if c["r"] > 0.5 and s["r"] < 0.5:
        suite = "oui, il les sépare"
    elif c["r"] <= s["r"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    r = m357.la_chaine_jugee(chainer=m358.la_chaine_qui_regrandit, en_plus=la_croissance_seule)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_minimum": LE_MINIMUM},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": r["le_controle"],
         "redonne_358": redonne_358(r["les_cotes"], json.loads(CE_QUE_358_A_PUBLIE.read_text())), "les_cotes": r["les_cotes"]}
    d["la_separation"] = la_separation(les_croissances_jugees(r["les_cotes"]))
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

    valide = np.ones((6, 6), dtype=bool)
    semes = np.zeros((6, 6), dtype=bool)
    semes[:2] = True
    vus = []

    def fabrique(les_comptes):
        def comptes(dep, arr, lv):
            vus.append((int(arr["valide"].sum()), lv))
            mailles = np.arange(36)
            return {"les_points": np.zeros((36, 3)), "en_face": np.ones(36, dtype=bool), "les_mailles": mailles,
                    "les_comptes": [les_comptes(i) for i in mailles]}
        return comptes
    k = {"depuis": m356.DEPUIS_LA_CROISSANCE, "le_depart": {}, "la_relance": {"la_nappe": np.zeros((6, 6, 3)), "valide": valide,
                                                                              "les_semes": semes}}
    sur_la_spire = fabrique(lambda i: 0 if i < 12 else 1)
    e = la_croissance_seule(k, "m7", comptes=sur_la_spire)
    v("★★★★ la croissance seule : toute la surface regrandie est comptée sur m7, et le compte n'est lu que sur les mailles hors semis",
      vus == [(36, "m7")] and e["les_mailles"] == 24 and e["le_compte"]["les_mesures"] == 24
      and e["le_compte"]["les_comptes"] == {"1": 24}, str((vus, e)))
    v("★★★ sous une spire gardée ou une relance, rien",
      la_croissance_seule(dict(k, depuis=m356.DEPUIS_LA_SPIRE), "m7", sur_la_spire) is None
      and la_croissance_seule(dict(k, depuis=m356.DEPUIS_LA_RELANCE), "m7", sur_la_spire) is None)
    def plan(z, n=40):
        g = np.zeros((n, n, 3))
        g[..., 0], g[..., 1] = np.meshgrid(np.arange(n) * 5.0, np.arange(n) * 5.0)
        g[..., 2] = z
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    arr = plan(20.0)
    r = m345.les_comptes_point_par_point(plan(0.0), arr, lambda idx: np.zeros(idx.shape[:-1]), 20.0)
    v("★★★★ le compte de 345 rend la maille de chaque point, même quand il n'en prend qu'une partie",
      len(r["les_mailles"]) == len(r["les_points"]) < 38 * 38
      and np.array_equal(arr["la_nappe"].reshape(-1, 3)[r["les_mailles"]], r["les_points"]), str(len(r["les_mailles"])))
    grand = np.ones((20, 20), dtype=bool)
    petits = np.zeros((20, 20), dtype=bool)
    petits[:2] = True
    k2 = dict(k, la_relance={"la_nappe": np.zeros((20, 20, 3)), "valide": grand, "les_semes": petits})

    def comptes400(les_comptes):
        return lambda dep, arr, lv: {"les_points": np.zeros((400, 3)), "en_face": np.ones(400, dtype=bool), "les_mailles": np.arange(400),
                                     "les_comptes": [les_comptes(i) for i in range(400)]}
    tenue = la_croissance_seule(k2, "m7", comptes400(lambda i: 1))
    zeros = la_croissance_seule(k2, "m7", comptes400(lambda i: 0 if i >= 350 else 1))
    peu = la_croissance_seule(k, "m7", sur_la_spire)
    v("★★★★ le critère de 352 sur la croissance seule : tenue ; 50 points à zéro, refusée ; moins de 50 mesures, refusée",
      tenue["tenue"] and tenue["mesuree"] and not zeros["tenue"] and zeros["mesuree"] and not peu["tenue"] and not peu["mesuree"],
      str((tenue["le_compte"], zeros["le_compte"], peu["le_compte"])))

    s_ = lambda c, t, m=True, j="juste", dep=m356.DEPUIS_LA_CROISSANCE: {  # noqa: E731
        "la_justesse": j, "depuis": dep, "a_cheval": c, "en_plus": {"tenue": t, "mesuree": m}}
    cotes = [{"le_rang": 5, "les_sauts": [s_(True, False), s_(False, True), s_(True, True, dep=m356.DEPUIS_LA_SPIRE),
                                          s_(True, False, j="faux : deux tours")]},
             {"le_rang": 2, "les_sauts": [s_(True, False)]}]
    v("★★★ seules les croissances justes des graines 4 à 8 sont jugées", len(les_croissances_jugees(cotes)) == 2)
    sep = la_separation([s_(True, False), s_(True, False, m=False), s_(True, True), s_(False, True), s_(False, False)])
    v("★★★★ la séparation : les refusées à cheval et saines, dont faute de mesures, et leurs parts",
      sep == {"a_cheval": {"les_croissances": 3, "les_refusees": 2, "faute_de_mesures": 1, "r": 0.6667},
              "saines": {"les_croissances": 2, "les_refusees": 1, "faute_de_mesures": 0, "r": 0.5}}, str(sep))

    def d_(rc, rs, nc=10, ns=10, rej=True):
        return {"les_pannes": [], "redonne_358": rej,
                "la_separation": {"a_cheval": {"les_croissances": nc, "les_refusees": round(rc * nc), "r": rc},
                                  "saines": {"les_croissances": ns, "les_refusees": round(rs * ns), "r": rs}}}
    v("★★★★ plus de la moitié des à cheval refusées et moins de la moitié des saines : oui",
      le_verdict(d_(0.6, 0.4))["lissue"].endswith("oui, il les sépare"))
    v("★★★★ pas plus de refus chez les à cheval que chez les saines : non", le_verdict(d_(0.3, 0.3))["lissue"].endswith("; non")
      and le_verdict(d_(0.2, 0.4))["lissue"].endswith("; non"))
    v("★★★ sinon : en partie", le_verdict(d_(0.5, 0.2))["lissue"].endswith("en partie")
      and le_verdict(d_(0.9, 0.5))["lissue"].endswith("en partie"))
    v("★★★ moins de 5 croissances à cheval ou saines, une chaîne qui ne redonne pas 358 : indécidable",
      not le_verdict(d_(0.9, 0.1, nc=4))["decidable"] and not le_verdict(d_(0.9, 0.1, ns=4))["decidable"]
      and le_verdict(d_(0.9, 0.1, nc=5, ns=5))["decidable"] and not le_verdict(d_(0.9, 0.1, rej=False))["decidable"])
    c = [{"le_rang": 4, "le_cote": "moins", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "depuis": "la croissance", "tenu": True,
                                                          "a_cheval": True, "restes": 60, "au_dela": 0, "les_points_poses": 900,
                                                          "les_points": 1500}]}]
    autre = json.loads(json.dumps(c))
    autre[0]["les_sauts"][0]["les_points"] = 1400
    pub = {"les_cotes": {"la_chaine_qui_regrandit": c}}
    v("★★★★ redonne 358 : saut par saut, taille comprise", redonne_358(c, pub) and not redonne_358(autre, pub)
      and not redonne_358(c, {"les_cotes": {"la_chaine_qui_regrandit": []}}))

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
