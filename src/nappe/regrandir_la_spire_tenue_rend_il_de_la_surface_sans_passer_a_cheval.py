"""Sur PHercParis4, graines 4 à 8, une chaîne mixte qui regrandit la spire tenue, et garde la surface regrandie quand le critère de 352 la tient elle aussi, rend-elle de la surface sans perdre la justesse ni passer davantage à cheval ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SPIRE NE SOIT REGRANDIE DANS LA CHAÎNE MIXTE. Ce qui était vu avant d'écrire : tout ce que
`296` à `357` publient, dont `R4-F543` (sur les graines 4 à 8, la chaîne mixte est juste sous ses 30 sauts jugés et à cheval sous 1, mais
ses spires gardées rétrécissent, jusqu'à 71 points posés), `R4-F535` (la chaîne relancée après chaque saut depuis sa spire, sa croissance
bornée à deux mailles des semis, donne une surface à cheval sous 20 de ses 28 sauts justes, la chaîne sans relance sous aucun des 24) et
`R4-F538` (le critère de `352` tient 23 des 60 surfaces à cheval). ⚠ Ces deux faits laissent attendre que le critère ne filtre qu'une partie
des surfaces regrandies à cheval : c'est ce que la mesure doit dire, pas ce qu'elle doit confirmer.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P155`. Une chaîne qui rétrécit ne couvre pas un rouleau. Si la croissance bornée de `335`,
partie de toute la spire tenue et gardée seulement quand le critère la tient, rend de la surface sans la faire passer à cheval, la chaîne
mixte peut aller loin sans s'éteindre ; sinon, c'est par le nombre des graines et non par la longueur des chaînes qu'un rouleau se couvrira.

## Ce qui est fait

- **La chaîne mixte** : celle de `357`, rejouée telle quelle, par sa fonction, qui gagne pour cela de quoi recevoir la chaîne de l'appelant.
- **La chaîne qui regrandit** : la même, sauf qu'une spire que le critère de `352` tient est regrandie par la croissance bornée de `335`,
  partie de tous ses points, à deux mailles au plus des mailles semées ; la surface regrandie est comptée contre la surface de départ, et
  gardée à la place de la spire si le critère la tient elle aussi. Une spire refusée est relancée depuis un point comme dans `357`.
- **La justesse, à cheval, la tenue** : celles de `357`, saut par saut.
- **La surface** d'une chaîne : la médiane, sous ses sauts justes, des mailles posées de la surface gardée.
- **Le contrôle** : la chaîne mixte rejouée redonne, saut par saut, ce que `357` publie, et les nappes de départ sont celles de `340`.
- **La règle**, sur les graines 4 à 8 : si la chaîne qui regrandit a une surface plus grande que la chaîne mixte, un j au moins aussi haut
  et un c au plus aussi haut, **oui, elle rend de la surface sans perdre la justesse ni passer davantage à cheval** ; si sa surface est plus
  grande mais son j plus bas ou son c plus haut, **en partie : elle rend de la surface, au prix de la justesse ou du cheval** ; sinon,
  **non, elle ne rend pas de surface**. Indécidable sous 5 sauts justes.

## Les issues

L'issue de la tranche : **sur les graines 4 à 8, la chaîne qui regrandit garde s mailles en médiane sous ses sauts justes, contre s' pour
la chaîne mixte ; elle est juste sous a des n sauts jugés et à cheval sous b de ses a sauts justes, contre a' des n' et b' des a'**, puis ce
que dit la règle.

## Rapporté à côté, qui ne décide rien

Combien de spires tenues ont été regrandies et gardées regrandies ; les graines 1 à 3.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que ferait une autre marge, ni ce que vaut la chaîne qui regrandit sur PHerc0358.

Usage :
    uv run python src/nappe/regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.py --verifier
    uv run python src/nappe/regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.py \\
        --json docs/mesures/regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval.json
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

import la_croissance_bornee_autour_des_semis_garde_t_elle_la_justesse as m335  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_357_A_PUBLIE = LES_MESURES / "la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4.json"
LE_MINIMUM = m357.LE_MINIMUM
LES_CLES_REJOUEES = ("le_saut", "la_justesse", "depuis", "tenu", "a_cheval", "restes", "au_dela", "les_points_poses")


def la_chaine_qui_regrandit(nappe: dict, relancer, sauter, lire_valeurs) -> list[dict]:
    """La chaîne mixte de `357`, dont chaque spire tenue est regrandie par la croissance bornée de `335`."""
    return m356.la_chaine_mixte(nappe, relancer, sauter, lire_valeurs, compter=m357.compter4,
                                regrandir=m335.la_relance_de_paris4(lire_valeurs))


def le_bilan(sauts: list[dict]) -> dict:
    """Le bilan de `357`, et la surface : la médiane des mailles posées de la surface gardée sous les sauts justes."""
    b = m357.le_bilan(sauts)
    pts = [s["les_points"] for s in sauts if s["la_justesse"] == "juste" and s.get("les_points") is not None]
    b["la_surface"] = float(statistics.median(pts)) if pts else None
    return b


def redonne_357(cotes: list[dict], publie: dict) -> bool:
    """La chaîne mixte rejouée redonne-t-elle, côté par côté et saut par saut, ce que `357` publie ?"""
    cle = lambda c: (c["le_rang"], c["le_cote"])  # noqa: E731
    garde = lambda c: [{k: s.get(k) for k in LES_CLES_REJOUEES} for s in c["les_sauts"]]  # noqa: E731
    pub = {cle(c): garde(c) for c in publie["les_cotes"]}
    return bool(pub) and pub == {cle(c): garde(c) for c in cotes}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les nappes de départ ne sont pas celles que 340 publie"}
    if not d.get("redonne_357"):
        return {"decidable": False, "lissue": "indécidable : la chaîne mixte rejouée ne redonne pas ce que 357 publie"}
    r, m = d["les_bilans"]["la_chaine_qui_regrandit"], d["les_bilans"]["la_chaine_mixte"]
    if r["les_justes"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {r['les_justes']} sauts justes"}
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = (f"sur les graines 4 à 8, la chaîne qui regrandit garde {f_(r['la_surface'])} mailles en médiane sous ses sauts justes, contre "
            f"{f_(m['la_surface'])} pour la chaîne mixte ; elle est juste sous {r['les_justes']} des {r['les_juges']} sauts jugés et à "
            f"cheval sous {r['les_justes_a_cheval']} de ses {r['les_justes']} sauts justes, contre {m['les_justes']} des {m['les_juges']} "
            f"et {m['les_justes_a_cheval']} des {m['les_justes']}")
    if r["la_surface"] <= m["la_surface"]:
        suite = "non, elle ne rend pas de surface"
    elif r["j"] >= m["j"] and r["c"] <= m["c"]:
        suite = "oui, elle rend de la surface sans perdre la justesse ni passer davantage à cheval"
    else:
        suite = "en partie : elle rend de la surface, au prix de la justesse ou du cheval"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    mixte = m357.la_chaine_jugee()
    regrandie = m357.la_chaine_jugee(chainer=la_chaine_qui_regrandit)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_marge_en_mailles": m335.LA_MARGE, "le_minimum": LE_MINIMUM},
         "les_pannes": mixte["les_pannes"] + regrandie["les_pannes"],
         "la_lecture_de_m7": {"la_chaine_mixte": mixte["la_lecture_de_m7"], "la_chaine_qui_regrandit": regrandie["la_lecture_de_m7"]},
         "le_controle": bool(mixte["le_controle"] and regrandie["le_controle"]),
         "redonne_357": redonne_357(mixte["les_cotes"], json.loads(CE_QUE_357_A_PUBLIE.read_text())),
         "les_cotes": {"la_chaine_mixte": mixte["les_cotes"], "la_chaine_qui_regrandit": regrandie["les_cotes"]}}
    d["les_bilans"] = {"la_chaine_mixte": le_bilan(m357.les_sauts_juges(mixte["les_cotes"])),
                       "la_chaine_qui_regrandit": le_bilan(m357.les_sauts_juges(regrandie["les_cotes"])),
                       "graines_1_a_3": le_bilan(m357.les_sauts_juges(regrandie["les_cotes"], (1, 2, 3)))}
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
        petite = ok.copy()
        petite[0, :] = False
        return {"la_spire": surf + np.array([0.0, 0.0, 20.0]), "valide": petite}
    bon = {"les_comptes": {"1": 100}, "les_mesures": 100, "la_part_dune_feuille": 1.0}
    mauvais = {"les_comptes": {"0": 90, "1": 10}, "les_mesures": 100, "la_part_dune_feuille": 0.1}
    regrandies, relances = [], []

    def regrandir(p, n, s, o):
        regrandies.append(int(o.sum()))
        return plan(float(p[2]))

    def relancer(p, n):
        relances.append(p)
        return plan(float(p[2]))
    ch = m356.la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=3, compter=lambda dep, arr, lv: bon, regrandir=regrandir)
    v("★★★★ une spire tenue est regrandie depuis tous ses points, et la surface regrandie tenue devient la surface de départ",
      [k["depuis"] for k in ch] == [m356.DEPUIS_LA_CROISSANCE] * 3 and regrandies == [110] * 3 and not relances
      and all(k["les_points"] == 121 for k in ch), str(([k["depuis"] for k in ch], regrandies)))
    hauteurs = []

    def sauter_note(surf, ok):
        hauteurs.append(float(surf[1, 1, 2]))
        return sauter(surf, ok)
    m356.la_chaine_mixte(plan(0.0), relancer, sauter_note, None, sauts=3, compter=lambda dep, arr, lv: bon,
                         regrandir=lambda p, n, s, o: plan(float(p[2]) + 5.0))
    v("★★★★ le saut suivant part de la surface regrandie, pas de la spire", hauteurs == [0.0, 25.0, 50.0], str(hauteurs))
    appels = []

    def compter(dep, arr, lv):
        appels.append(int(arr["valide"].sum()))
        return bon if arr["valide"].sum() < 121 else mauvais
    ch = m356.la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=2, compter=compter, regrandir=regrandir)
    v("★★★★ une surface regrandie refusée : la spire est gardée, telle quelle",
      [k["depuis"] for k in ch] == [m356.DEPUIS_LA_SPIRE] * 2 and ch[0]["le_compte"] == bon and ch[0]["les_points"] == 110,
      str([k["depuis"] for k in ch]))
    regrandies[:], relances[:] = [], []
    ch = m356.la_chaine_mixte(plan(0.0), relancer, sauter, None, sauts=2, compter=lambda dep, arr, lv: mauvais, regrandir=regrandir)
    v("★★★ une spire refusée n'est pas regrandie : la nappe est relancée depuis un point",
      [k["depuis"] for k in ch] == [m356.DEPUIS_LA_RELANCE] * 2 and not regrandies and len(relances) == 2)
    vu, avant = {}, (m356.la_chaine_mixte, m335.la_relance_de_paris4)
    m356.la_chaine_mixte = lambda *a, **k: vu.update(k, lv=a[3]) or []
    m335.la_relance_de_paris4 = lambda lv: ("la croissance bornée de 335", lv)
    try:
        la_chaine_qui_regrandit(plan(0.0), relancer, sauter, "m7")
    finally:
        m356.la_chaine_mixte, m335.la_relance_de_paris4 = avant
    v("★★★ la chaîne qui regrandit passe la croissance bornée de 335, sur m7, et le compte de 357",
      vu.get("compter") is m357.compter4 and vu.get("regrandir") == ("la croissance bornée de 335", "m7") and vu.get("lv") == "m7",
      str(vu))

    s_ = lambda j, n, c=False: {"la_justesse": j, "a_cheval": c, "les_points": n}  # noqa: E731
    b = le_bilan([s_("juste", 100), s_("juste", 600), s_("faux : deux tours", 900), s_("juste", 200, True)])
    v("★★★★ la surface : la médiane des mailles des seuls sauts justes", b["la_surface"] == 200.0 and b["les_justes"] == 3, str(b))

    def d_(sr, jr, cr, sm=500.0, jm=1.0, cm=0.05, n=30, ok=True, rej=True):
        def bil(s, j, c):
            justes = round(j * n)
            return {"les_juges": n, "les_justes": justes, "les_justes_a_cheval": round(c * justes), "j": j, "c": c, "la_surface": s}
        return {"les_pannes": [], "le_controle": ok, "redonne_357": rej,
                "les_bilans": {"la_chaine_qui_regrandit": bil(sr, jr, cr), "la_chaine_mixte": bil(sm, jm, cm)}}
    v("★★★★ plus de surface, aussi juste, pas plus à cheval : oui",
      le_verdict(d_(800.0, 1.0, 0.05))["lissue"].endswith("ni passer davantage à cheval"))
    v("★★★★ plus de surface mais plus à cheval, ou moins juste : en partie",
      le_verdict(d_(800.0, 1.0, 0.2))["lissue"].endswith("au prix de la justesse ou du cheval")
      and le_verdict(d_(800.0, 0.9, 0.0))["lissue"].endswith("au prix de la justesse ou du cheval"))
    v("★★★★ une surface égale ou plus petite : non", le_verdict(d_(500.0, 1.0, 0.0))["lissue"].endswith("ne rend pas de surface")
      and le_verdict(d_(400.0, 1.0, 0.0))["lissue"].endswith("ne rend pas de surface"))
    v("★★★ moins de 5 sauts justes, un contrôle tombé, une chaîne mixte qui ne redonne pas 357 : indécidable",
      not le_verdict(d_(800.0, 0.1, 0.0))["decidable"] and not le_verdict(d_(800.0, 1.0, 0.0, ok=False))["decidable"]
      and not le_verdict(d_(800.0, 1.0, 0.0, rej=False))["decidable"])
    c = [{"le_rang": 4, "le_cote": "moins", "les_sauts": [{"le_saut": 1, "la_justesse": "juste", "depuis": "la spire", "tenu": True,
                                                          "a_cheval": False, "restes": 0, "au_dela": 0, "les_points_poses": 900,
                                                          "les_points": 700}]}]
    autre = json.loads(json.dumps(c))
    autre[0]["les_sauts"][0]["a_cheval"] = True
    v("★★★★ redonne 357 : saut par saut, pas seulement les bilans", redonne_357(c, {"les_cotes": c}) and not redonne_357(autre, {"les_cotes": c})
      and not redonne_357(c, {"les_cotes": []}))

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
