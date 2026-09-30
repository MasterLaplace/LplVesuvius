"""Sur PHerc0358, les paires « même feuille » à plusieurs tours d'écart sont-elles deux feuilles qui se touchent, une part de leurs points à moins d'un quart de pas et le reste à plus d'un demi-pas ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL ÉCART NE SOIT RELU POINT PAR POINT. Ce qui était vu avant d'écrire : tout ce que `296` à `374`
publient, dont `R4-F560` (l'accord de trois chaînes valide 25 surfaces sur 120 ; sur la graine 8, 47 des 48 sont contredites). Et, compté
sur les paires que `368` et `373` publient : sous les comptes corrigés, 38 paires « même feuille » sont au même compte, 31 à un tour d'écart
et 27 à deux tours ou plus, toutes les 27 sur la graine 8.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P172`. Le juge de feuille de `367` dit « même feuille » quand la médiane des écarts est sous
un quart de pas ; il a été étalonné sur PHercParis4. Là où deux feuilles se touchent sur une partie de la surface, plus de la moitié des
points peut être à moins d'un quart de pas d'une autre feuille, et le juge se tromper.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373`, rejouées par sa fonction ; leurs paires et leurs comptes corrigés doivent redonner ceux que
  `368`, `369` et `373` publient.
- **Chaque paire « même feuille »** : ses points en face relus un à un, à la portée et au latéral de `368` ; **sa part lointaine** est la
  part de ceux qui sont à plus d'un demi-pas, 10 voxels. Elle **touche** si sa part lointaine atteint un quart.
- **Les groupes** : les paires au même compte corrigé, et celles à deux tours d'écart ou plus.
- **La règle** : si au moins 90 % des paires à deux tours ou plus touchent et au plus 10 % de celles au même compte, **oui, ce sont deux
  feuilles qui se touchent** ; si moins de la moitié des paires à deux tours ou plus touchent, **non** ; sinon, **en partie**. Indécidable
  sous 5 paires dans l'un des groupes.

## Les issues

L'issue de la tranche : **a des n paires à deux tours ou plus touchent, contre a' des n' au même compte**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La médiane des parts lointaines de chaque groupe, et celle des paires à un tour d'écart.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : où, sur la surface, les feuilles se touchent, ni si un juge qui en tient compte ferait s'accorder
les chaînes de la graine 8.

Usage :
    uv run python src/nappe/les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.py --verifier
    uv run python src/nappe/les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.py \\
        --json docs/mesures/les_paires_meme_feuille_a_plusieurs_tours_sont_elles_deux_feuilles_qui_se_touchent.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_373_A_PUBLIE = LES_MESURES / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
CE_QUE_368_A_PUBLIE = LES_MESURES / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"
LE_DEMI_PAS = m368.LE_PAS / 2.0
LE_QUART_DE_POINTS = 0.25
LE_MINIMUM = 5
MEME, UN, PLUSIEURS = "même compte", "un tour", "deux tours ou plus"


def la_repartition(a, b, lateral: float = m368.LE_LATERAL) -> dict:
    """Les points de `a` qui ont `b` en face, comme `368` les compte, la médiane de leurs écarts absolus et la part de ceux à plus d'un
    demi-pas."""
    import numpy as np

    e = m321.les_ecarts(a[0], a[1], b[0], lateral=lateral)
    vus = np.isfinite(e) & (np.abs(e) <= m367.LA_PORTEE)
    x = np.abs(e[vus])
    return {"en_face": int(vus.sum()), "lecart_median": round(float(np.median(x)), 3) if len(x) else None,
            "la_part_lointaine": round(float((x > LE_DEMI_PAS).mean()), 4) if len(x) else None}


def le_groupe(ecart: int) -> str:
    return MEME if ecart == 0 else UN if ecart == 1 else PLUSIEURS


def touche(p: dict) -> bool:
    return p["la_part_lointaine"] is not None and p["la_part_lointaine"] >= LE_QUART_DE_POINTS


def le_bilan(paires: list[dict]) -> dict:
    out = {}
    for g in (MEME, UN, PLUSIEURS):
        ps = [p for p in paires if p["le_groupe"] == g]
        parts = [p["la_part_lointaine"] for p in ps if p["la_part_lointaine"] is not None]
        out[g] = {"les_paires": len(ps), "touchent": sum(touche(p) for p in ps),
                  "la_part_lointaine_mediane": round(statistics.median(parts), 4) if parts else None}
    return out


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les paires et les comptes rejoués ne redonnent pas ceux que 368 à 373 publient"}
    b = d["le_bilan"]
    m, p = b[MEME], b[PLUSIEURS]
    if m["les_paires"] < LE_MINIMUM or p["les_paires"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {m['les_paires']} paires au même compte et {p['les_paires']} à deux tours ou plus"}
    tete = (f"{p['touchent']} des {p['les_paires']} paires « même feuille » à deux tours ou plus touchent, contre {m['touchent']} des "
            f"{m['les_paires']} au même compte")
    if p["touchent"] >= 0.9 * p["les_paires"] and m["touchent"] <= 0.1 * m["les_paires"]:
        suite = "oui, ce sont deux feuilles qui se touchent"
    elif p["touchent"] < 0.5 * p["les_paires"]:
        suite = "non"
    else:
        suite = "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    m368._LES_PAIRES_DE_CHAINES.clear()
    m369._LES_CHAINES.clear()
    m373._LES_TIERCES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m373.le_chaineur())
    p373, p368 = json.loads(CE_QUE_373_A_PUBLIE.read_text()), json.loads(CE_QUE_368_A_PUBLIE.read_text())
    paires, redonne = [], True
    for c, pc, nap, pt, q3, q8 in zip(chaines, m368._LES_PAIRES_DE_CHAINES, m369._LES_CHAINES, m373._LES_TIERCES, p373["les_cotes"],
                                      p368["les_cotes"]):
        surfaces = {"suivie": pc["suivie"], "compagne": pc["compagne"], "tierce": pt["tierce"]}
        comptes = {"suivie": [s["le_compte_corrige"] for s in m369.les_sauts(nap["la_nappe"], pc["suivie"])],
                   "compagne": [s["le_compte_corrige"] for s in m369.les_sauts(nap["la_nappe_compagne"], pc["compagne"])],
                   "tierce": [s["le_compte_corrige"] for s in m369.les_sauts(pt["la_nappe"], pt["tierce"])]}
        redonne &= comptes["tierce"] == [s["le_compte_corrige"] for s in q3["les_sauts_de_la_tierce"]]
        publiees = {"suivie|compagne": q8["les_paires"], **q3["les_paires"]}
        for cle, pub in publiees.items():
            a, b = cle.split("|")
            for q in pub:
                h, k = q["le_saut_suivi"], q["le_saut_compagnon"]
                r = la_repartition(surfaces[a][h - 1], surfaces[b][k - 1])
                redonne &= (r["en_face"], r["lecart_median"]) == (q["en_face"], q["lecart_median"])
                if not q["meme_feuille"]:
                    continue
                ecart = abs(comptes[a][h - 1] - comptes[b][k - 1])
                paires.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "le_couple": cle, "les_sauts": [h, k], "lecart_de_comptes": ecart,
                               "le_groupe": le_groupe(ecart), **r})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "redonne": bool(redonne)}), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_demi_pas": LE_DEMI_PAS, "le_quart_de_points": LE_QUART_DE_POINTS, "le_minimum": LE_MINIMUM},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne": bool(redonne), "les_paires": paires}
    d["le_bilan"] = le_bilan(paires)
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


def verifier() -> int:
    import numpy as np

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

    g = np.stack(np.meshgrid(np.arange(0.0, 20.0, 2.0), np.arange(0.0, 20.0, 2.0)), -1).reshape(-1, 2)
    haut = np.full(len(g), 12.0)
    haut[g[:, 0] < 6.0] = 2.0
    a = (np.c_[g, np.zeros(len(g))], np.tile([0.0, 0.0, 1.0], (len(g), 1)))
    b = np.c_[g, haut]
    r = la_repartition(a, (b, None), lateral=0.5)
    v("★★★★ la répartition : une feuille qui en touche une autre sur trois colonnes, médiane sous un quart de pas, 40 % lointains",
      lambda: r == {"en_face": 50, "lecart_median": 2.0, "la_part_lointaine": 0.4}, str(r))
    b2 = np.c_[g, np.full(len(g), 10.0)]
    v("★★★ un point à un demi-pas juste n'est pas lointain", lambda: la_repartition(a, (b2, None))["la_part_lointaine"] == 0.0)
    b3 = np.c_[g, np.full(len(g), 28.0)]
    v("★★★ au-delà de la portée de 368, aucun point en face", lambda: la_repartition(a, (b3, None))["en_face"] == 0)
    v("★★★★ les groupes : même compte, un tour, deux tours ou plus",
      [le_groupe(x) for x in (0, 1, 2, 5)] == [MEME, UN, PLUSIEURS, PLUSIEURS])
    v("★★★★ une paire touche si sa part lointaine atteint un quart",
      touche({"la_part_lointaine": 0.25}) and not touche({"la_part_lointaine": 0.2499}) and not touche({"la_part_lointaine": None}))
    q = lambda gr, part: {"le_groupe": gr, "la_part_lointaine": part}  # noqa: E731
    b_ = le_bilan([q(MEME, 0.0), q(MEME, 0.3), q(MEME, 0.1), q(PLUSIEURS, 0.5), q(PLUSIEURS, 0.2), q(UN, None)])
    v("★★★★ le bilan : paires, celles qui touchent, médiane des parts lointaines, par groupe",
      b_[MEME] == {"les_paires": 3, "touchent": 1, "la_part_lointaine_mediane": 0.1}
      and b_[PLUSIEURS] == {"les_paires": 2, "touchent": 1, "la_part_lointaine_mediane": 0.35}
      and b_[UN] == {"les_paires": 1, "touchent": 0, "la_part_lointaine_mediane": None}, str(b_))

    def d_(pt, pn, mt, mn, ok=True):
        return {"les_pannes": [], "redonne": ok, "le_bilan": {MEME: {"les_paires": mn, "touchent": mt}, PLUSIEURS: {"les_paires": pn,
                                                                                                                  "touchent": pt}}}
    v("★★★★ la règle : 90 % contre 10 %, oui ; moins de la moitié, non ; sinon en partie",
      le_verdict(d_(9, 10, 1, 10))["lissue"].endswith("se touchent") and le_verdict(d_(9, 10, 2, 10))["lissue"].endswith("en partie")
      and le_verdict(d_(8, 10, 0, 10))["lissue"].endswith("en partie") and le_verdict(d_(4, 10, 0, 10))["lissue"].endswith("; non")
      and le_verdict(d_(5, 10, 0, 10))["lissue"].endswith("en partie"))
    v("★★★ indécidable sous 5 paires dans un groupe, ou sans la redite",
      not le_verdict(d_(4, 4, 0, 10))["decidable"] and not le_verdict(d_(9, 10, 0, 4))["decidable"]
      and not le_verdict(d_(9, 10, 0, 10, ok=False))["decidable"])
    v("★★★ le demi-pas : 10 voxels", LE_DEMI_PAS == 10.0)

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
