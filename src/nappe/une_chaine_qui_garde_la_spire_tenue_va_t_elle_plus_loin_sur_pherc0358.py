"""Sur PHerc0358, une chaîne qui saute depuis la spire quand le critère de 352 la tient, et ne relance que sinon, tient-elle plus de sauts à la suite que la chaîne relancée ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CHAÎNE DE CE GENRE NE SOIT CONSTRUITE. Ce qui était vu avant d'écrire : tout ce que `296` à
`355` publient, dont `R4-F540` (la chaîne relancée de PHerc0358 tient 1, 0, 0, 1 et 0 sauts à la suite par le critère de `352` sur ses cinq
côtés) et `R4-F541` (sous 14 des 23 sauts dont la surface relancée garde 50 points sur la feuille de départ, la spire était partie ; lu
après coup, le critère tiendrait 18 des 31 spires et 4 des 31 surfaces relancées). ⚠ `328` a vu une chaîne sans relance rétrécir sur
PHerc0358 : sa spire tombe sous 10 % du plan (`R4-F513`).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P153`. La spire est plus souvent une bonne surface que la nappe relancée depuis un seul de
ses points, mais une chaîne qui ne relance jamais rétrécit. Ne relancer que là où la spire est refusée garde le meilleur des deux, si la
spire tenue reste assez grande pour que le saut suivant la trouve.

## Ce qui est fait

- **Les graines, les nappes de départ, le saut et la relance** : ceux des chaînes de PHerc0358 que `331` suit, par sa fonction, qui gagne
  pour cela de quoi recevoir la chaîne de l'appelant.
- **La chaîne mixte** : à chaque saut, la spire est comptée contre la surface de départ par le compte de `345` au pas et à la portée de
  `354`. Si le critère de `352` la tient, elle devient la surface de départ du saut suivant, sans relance ; sinon la nappe est relancée
  depuis la spire comme dans `331`, et c'est elle qui continue. Chaque saut porte la surface qu'il garde et son compte.
- **La suite** d'un côté : les sauts à la suite depuis la nappe de départ dont la surface gardée est tenue par le critère de `352`.
- **Le contrôle** : le premier saut de chaque côté part de la même nappe que dans `355` : le compte de sa spire doit redonner ce que `355`
  publie, sans quoi la tranche est indécidable.
- **La règle** : sur les cinq côtés, la médiane des suites de la chaîne mixte contre celle de la chaîne relancée que `354` publie : plus
  haute, **elle tient plus de sauts à la suite** ; égale, **pas plus** ; plus basse, **moins**.

## Les issues

L'issue de la tranche : **sur PHerc0358, la chaîne mixte tient m sauts à la suite en médiane, contre r pour la chaîne relancée**, puis ce
que dit la règle.

## Rapporté à côté, qui ne décide rien

Côté par côté, les suites des deux chaînes, les sauts partis de la spire et de la relance, et la taille des surfaces gardées.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les surfaces que la chaîne mixte tient sont sur leur feuille.

Usage :
    uv run python src/nappe/une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.py --verifier
    uv run python src/nappe/une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.py \\
        --json docs/mesures/une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.json
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

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358 as m354  # noqa: E402
import sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart as m355  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_354_A_PUBLIE = m355.CE_QUE_354_A_PUBLIE
CE_QUE_355_A_PUBLIE = LES_MESURES / "sur_pherc0358_est_ce_le_saut_ou_la_relance_qui_reste_sur_la_feuille_de_depart.json"
DEPUIS_LA_SPIRE, DEPUIS_LA_RELANCE, DEPUIS_LA_CROISSANCE = "la spire", "la relance", "la croissance"


def la_chaine_mixte(nappe: dict, relancer, sauter, lire_valeurs, sauts: int = m331.LES_SAUTS, compter=m355.le_compte_de,
                    regrandir=None, rogner=None) -> list[dict]:
    """Jusqu'à `sauts` sauts ; chacun garde sa spire si le critère de `352` la tient contre la surface de départ, relance une nappe depuis
    elle sinon, et part de ce qu'il a gardé. Chaque saut porte le compte de la surface gardée, et, pour `357`, la surface d'où il part et la
    surface gardée sous les noms `le_depart` et `la_relance` que la mesure de `331` lit. Avec `regrandir(point, normale, spire, valide)`,
    écrit pour `358`, une spire tenue est regrandie, et la surface regrandie est gardée à sa place si le critère la tient elle aussi. Avec
    `rogner(depart, gardee)`, écrit pour `397`, la surface gardée est rognée avant d'être enregistrée et d'être le départ du saut suivant ;
    les comptes enregistrés restent ceux qui l'ont fait garder."""
    surf, ok = nappe["la_nappe"], nappe["valide"]
    out = []
    for _ in range(sauts):
        s = sauter(surf, ok)
        depart = {"la_nappe": surf, "valide": ok}
        spire = {"la_nappe": s["la_spire"], "valide": s["valide"]}
        f_sp = compter(depart, spire, lire_valeurs)
        if s["valide"].any() and m355.tenue(f_sp):
            garde, f_g, depuis = spire, f_sp, DEPUIS_LA_SPIRE
            g = m331.la_graine_de_la_relance(s["la_spire"], s["valide"]) if regrandir is not None else None
            if g is not None:
                r = regrandir(*g, s["la_spire"], s["valide"])
                f_r = compter(depart, r, lire_valeurs)
                if r["valide"].any() and m355.tenue(f_r):
                    garde, f_g, depuis = r, f_r, DEPUIS_LA_CROISSANCE
            if rogner is not None:
                garde = rogner(depart, garde)
            out.append({"le_saut": s, "depuis": depuis, "le_compte_de_la_spire": f_sp, "le_compte": f_g,
                        "les_points": int(garde["valide"].sum()), "le_depart": depart, "la_relance": garde})
            surf, ok = garde["la_nappe"], garde["valide"]
            continue
        g = m331.la_graine_de_la_relance(s["la_spire"], s["valide"]) if s["valide"].any() else None
        if g is None:
            out.append({"le_saut": s, "depuis": None, "le_compte_de_la_spire": f_sp, "le_compte": m345.le_resume(None), "les_points": 0,
                        "le_depart": depart, "la_relance": None})
            break
        r = relancer(*g)
        f_r = compter(depart, r, lire_valeurs)
        if rogner is not None and r["valide"].any():
            r = rogner(depart, r)
        out.append({"le_saut": s, "depuis": DEPUIS_LA_RELANCE, "le_compte_de_la_spire": f_sp, "le_compte": f_r,
                    "les_points": int(r["valide"].sum()), "le_depart": depart, "la_relance": r})
        if not r["valide"].any():
            break
        surf, ok = r["la_nappe"], r["valide"]
    return out


def la_suite(chaine: list[dict]) -> int:
    return m354.la_suite([bool(k["depuis"] is not None and m355.tenue(k["le_compte"])) for k in chaine])


def redonne_355(cotes: list[dict], publie: dict) -> bool:
    """Le compte de la spire du premier saut, parti de la même nappe, redonne-t-il ce que `355` publie ?"""
    pub = {(c["le_rang"], c["le_cote"]): c["les_sauts"][0]["la_spire"] for c in publie["les_cotes"] if c["les_sauts"]}
    rej = {(c["le_rang"], c["le_cote"]): c["les_sauts"][0]["le_compte_de_la_spire"] for c in cotes if c["les_sauts"]}
    return bool(pub) and pub == rej


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_355"):
        return {"decidable": False, "lissue": "indécidable : les premiers sauts ne redonnent pas 355"}
    m = statistics.median(c["la_suite"] for c in d["les_cotes"])
    r = statistics.median(d["les_suites_relancees"])
    f_ = lambda x: f"{x:g}".replace(".", ",") + (" saut" if x <= 1 else " sauts")  # noqa: E731
    tete = f"sur PHerc0358, la chaîne mixte tient {f_(m)} à la suite en médiane, contre {f_(r)} pour la chaîne relancée"
    suite = "elle tient plus de sauts à la suite" if m > r else "pas plus" if m == r else "moins"
    return {"decidable": True, "m": m, "r": r, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=lambda r, rel0, sauter, lv: la_chaine_mixte(r, rel0, sauter, lv))
    cotes = []
    for c in chaines:
        sauts = [{"le_saut": h, "depuis": k["depuis"], "le_compte_de_la_spire": k["le_compte_de_la_spire"], "le_compte": k["le_compte"],
                  "les_points": k["les_points"], "tenu": bool(k["depuis"] is not None and m355.tenue(k["le_compte"]))}
                 for h, k in enumerate(c["la_chaine"], 1)]
        cote = {"le_rang": c["le_rang"], "le_cote": c["le_cote"], "les_sauts": sauts, "la_suite": la_suite(c["la_chaine"])}
        cotes.append(cote)
        print(json.dumps({x: cote[x] for x in ("le_rang", "le_cote", "la_suite")}, ensure_ascii=False),
              [(s["depuis"], s["les_points"], s["le_compte"]["les_comptes"].get("0", 0), s["tenu"]) for s in sauts], flush=True)
    publie354 = json.loads(CE_QUE_354_A_PUBLIE.read_text())
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_seuil": m354.LE_SEUIL, "le_pas": m354.LE_PAS, "les_sauts": m331.LES_SAUTS},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_355": redonne_355(cotes, json.loads(CE_QUE_355_A_PUBLIE.read_text())), "les_cotes": cotes,
         "les_suites_relancees": [c["la_suite"] for c in publie354["les_cotes"]]}
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

    def plan(z, n=11):
        g = np.zeros((n, n, 3))
        for a in range(n):
            for b in range(n):
                g[a, b] = (10.0 * b, 10.0 * a, z)
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}

    def sauter(surf, ok):
        return {"la_spire": surf + np.array([0.0, 0.0, 20.0]), "valide": ok.copy()}
    bon = {"les_comptes": {"1": 100}, "les_mesures": 100, "la_part_dune_feuille": 1.0}
    mauvais = {"les_comptes": {"0": 90, "1": 10}, "les_mesures": 100, "la_part_dune_feuille": 0.1}
    relances = []

    def relancer(p, n):
        relances.append(p)
        return plan(float(p[2]))
    ch = la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=3, compter=lambda dep, arr, lv: bon)
    v("★★★★ une spire tenue devient la surface de départ, sans relance",
      [k["depuis"] for k in ch] == [DEPUIS_LA_SPIRE] * 3 and not relances and la_suite(ch) == 3, str([k["depuis"] for k in ch]))
    ch = la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=3, compter=lambda dep, arr, lv: mauvais)
    v("★★★★ une spire refusée : la nappe est relancée depuis elle, et c'est elle qui est comptée et continue",
      [k["depuis"] for k in ch] == [DEPUIS_LA_RELANCE] * 3 and len(relances) == 3 and la_suite(ch) == 0
      and ch[0]["le_compte"] == mauvais, str([k["depuis"] for k in ch]))
    appels = []

    def compter(dep, arr, lv):
        appels.append(arr)
        return bon if len(appels) % 2 == 0 else mauvais
    ch = la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=2, compter=compter)
    v("★★★ spire refusée puis relance tenue : la suite compte la surface gardée, pas la spire",
      ch[0]["depuis"] == DEPUIS_LA_RELANCE and ch[0]["le_compte"] == bon and ch[0]["le_compte_de_la_spire"] == mauvais
      and la_suite(ch[:1]) == 1, str(ch[0]["depuis"]))
    hauteurs = []

    def sauter_note(surf, ok):
        hauteurs.append(float(surf[0, 0, 2]))
        return sauter(surf, ok)
    la_chaine_mixte(plan(0.0), relancer, sauter_note, None, sauts=3, compter=lambda dep, arr, lv: bon)
    tenues, hauteurs[:] = list(hauteurs), []
    la_chaine_mixte(plan(0.0), relancer, sauter_note, None, sauts=3, compter=lambda dep, arr, lv: mauvais)
    v("★★★★ chaque saut part de la surface gardée au saut précédent, spire ou nappe relancée",
      tenues == [0.0, 20.0, 40.0] and hauteurs == [0.0, 20.0, 40.0], str((tenues, hauteurs)))
    vide = lambda surf, ok: {"la_spire": surf, "valide": np.zeros_like(ok)}  # noqa: E731
    ch = la_chaine_mixte(plan(0.0), relancer, vide, None, sauts=3, compter=lambda dep, arr, lv: bon)
    v("★★★ une spire vide arrête la chaîne", len(ch) == 1 and ch[0]["depuis"] is None and la_suite(ch) == 0)

    pub = {"les_cotes": [{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"la_spire": bon}]}]}
    v("★★★★ le premier saut doit redonner la spire de 355",
      redonne_355([{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"le_compte_de_la_spire": bon}]}], pub)
      and not redonne_355([{"le_rang": 6, "le_cote": "moins", "les_sauts": [{"le_compte_de_la_spire": mauvais}]}], pub))

    def d_(suites, relancees, ok=True):
        return {"les_pannes": [], "redonne_355": ok, "les_cotes": [{"la_suite": x} for x in suites], "les_suites_relancees": relancees}
    v("★★★★ médiane plus haute : elle tient plus", le_verdict(d_([2, 1, 3, 0, 1], [1, 0, 0, 1, 0]))["lissue"].endswith("plus de sauts à la suite"))
    v("★★★ égale : pas plus ; plus basse : moins", le_verdict(d_([0, 1, 0, 0, 1], [1, 0, 0, 1, 0]))["lissue"].endswith("pas plus")
      and le_verdict(d_([0, 0, 0, 0, 1], [1, 1, 0, 1, 2]))["lissue"].endswith("; moins"))
    v("★★★ la médiane, pas la moyenne", le_verdict(d_([0, 0, 0, 8, 8], [1, 0, 0, 1, 0]))["lissue"].endswith("pas plus"))
    v("★★★ des premiers sauts qui ne redonnent pas 355 : indécidable", not le_verdict(d_([1], [0], ok=False))["decidable"])

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
