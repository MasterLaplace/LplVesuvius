"""Sur PHercParis4, graines 4 à 8, une chaîne qui regrandit sa spire tenue d'une seule maille au lieu de deux rend-elle de la surface sans faire naître le décalage ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SPIRE NE SOIT REGRANDIE D'UNE MAILLE. Ce qui était vu avant d'écrire : tout ce que `296` à
`364` publient, dont `R4-F544` (regrandie de deux mailles, la chaîne garde 1600 mailles en médiane sous ses sauts justes, contre 980,5 pour
la chaîne mixte, et passe à cheval sous 15 de ses 29 sauts justes, contre 1 sur 30) et `R4-F550` (c'est cette croissance qui fait naître le
décalage que la chaîne propage : après la première surface lisible, sur 3 des 5 côtés moins).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P162`. Si le décalage naît au bord de la croissance, une croissance plus courte en fait moins
naître, et rend moins de surface ; la question est de savoir si une maille suffit à regagner de la surface sur la chaîne mixte sans faire
naître de décalage.

## Ce qui est fait

- **La chaîne** : celle de `358`, sauf que la croissance bornée de `335` s'arrête à une maille des mailles semées au lieu de deux ; rejouée
  par la fonction de `357`, avec les lectures de `363`.
- **La surface, la justesse, à cheval** : celles de `358`. **La naissance du décalage** : celle de `364`, depuis la première surface lisible
  de chaque côté moins.
- **Les références** : la chaîne mixte, et la chaîne qui regrandit de deux mailles, telles que les lectures de `363` les donnent.
- **Le contrôle** : les nappes de départ sont celles de `340`, et les bilans de `364` se recalculent sur les lectures de `363`.
- **La règle** : si la chaîne qui regrandit d'une maille garde plus de mailles que la chaîne mixte sous ses sauts justes, et que le
  décalage n'y naît après la première surface lisible sur pas plus de côtés que sous la chaîne mixte, **oui, elle rend de la surface sans
  faire naître le décalage** ; si elle garde plus de mailles mais le fait naître sur plus de côtés, **en partie : elle rend de la surface,
  et fait naître le décalage** ; sinon, **non, elle ne rend pas de surface**.

## Les issues

L'issue de la tranche : **regrandie d'une maille, la chaîne garde s mailles en médiane sous ses sauts justes, contre s' pour la chaîne
mixte, et le décalage naît après la première surface lisible sur a côtés, contre a' sous la chaîne mixte**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La justesse et les sauts à cheval ; la même lecture sous la chaîne qui regrandit de deux mailles.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : ce que ferait une croissance qui ne pose que là où elle ne passe pas sur le tour voisin, ni ce que
vaut cette chaîne sur PHerc0358.

Usage :
    uv run python src/nappe/regrandir_dune_seule_maille_evite_il_le_decalage.py --verifier
    uv run python src/nappe/regrandir_dune_seule_maille_evite_il_le_decalage.py \\
        --json docs/mesures/regrandir_dune_seule_maille_evite_il_le_decalage.json
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

import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402
import une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358 as m356  # noqa: E402
import la_chaine_mixte_tient_elle_ses_sauts_justes_sur_paris4 as m357  # noqa: E402
import regrandir_la_spire_tenue_rend_il_de_la_surface_sans_passer_a_cheval as m358  # noqa: E402
import ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite as m363  # noqa: E402
import le_decalage_nait_il_apres_la_premiere_surface_lisible as m364  # noqa: E402

LA_MARGE = 1
CE_QUE_363_A_PUBLIE = m364.CE_QUE_363_A_PUBLIE


def la_chaine_dune_maille(nappe: dict, relancer, sauter, lire_valeurs, marge: int = LA_MARGE) -> list[dict]:
    """La chaîne de `358`, dont la croissance s'arrête à `marge` mailles des mailles semées."""
    regrandir = lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lire_valeurs, marge=marge)  # noqa: E731
    return m356.la_chaine_mixte(nappe, relancer, sauter, lire_valeurs, compter=m357.compter4, regrandir=regrandir)


def le_bilan(cotes: list[dict]) -> dict:
    """La surface, la justesse et le cheval de `358` sur les sauts jugés ; la naissance de `364`."""
    b = m358.le_bilan(m357.les_sauts_juges(cotes))
    n = m364.le_bilan(cotes)
    return {**b, "la_naissance": {k: v for k, v in n.items() if k != "le_detail"}, "les_suites": n["le_detail"]}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les nappes de départ ou les lectures de 363 ne sont pas celles publiées"}
    u, m = d["les_bilans"]["dune_maille"], d["les_bilans"]["la_chaine_mixte"]
    if u["la_surface"] is None or not u["la_naissance"]["les_cotes_juges"]:
        return {"decidable": False, "lissue": "indécidable : aucun saut juste ou aucun côté lu"}
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    tete = (f"regrandie d'une maille, la chaîne garde {f_(u['la_surface'])} mailles en médiane sous ses sauts justes, contre "
            f"{f_(m['la_surface'])} pour la chaîne mixte, et le décalage naît après la première surface lisible sur "
            f"{u['la_naissance']['apres_elle']} côtés, contre {m['la_naissance']['apres_elle']} sous la chaîne mixte")
    if u["la_surface"] <= m["la_surface"]:
        suite = "non, elle ne rend pas de surface"
    elif u["la_naissance"]["apres_elle"] <= m["la_naissance"]["apres_elle"]:
        suite = "oui, elle rend de la surface sans faire naître le décalage"
    else:
        suite = "en partie : elle rend de la surface, et fait naître le décalage"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    r = m357.la_chaine_jugee(chainer=la_chaine_dune_maille, en_plus=m363.les_surfaces_lues)
    d363 = json.loads(CE_QUE_363_A_PUBLIE.read_text())
    lectures = all(m363.le_bilan(v) == d363["les_bilans"][k] for k, v in d363["les_cotes"].items())
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_marge_en_mailles": LA_MARGE},
         "les_pannes": r["les_pannes"], "la_lecture_de_m7": r["la_lecture_de_m7"], "le_controle": bool(r["le_controle"] and lectures),
         "les_cotes": r["les_cotes"]}
    d["les_bilans"] = {"dune_maille": le_bilan(r["les_cotes"]), "la_chaine_mixte": le_bilan(d363["les_cotes"]["la_chaine_mixte"]),
                       "de_deux_mailles": le_bilan(d363["les_cotes"]["la_chaine_qui_regrandit"])}
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

    vu, avant = {}, (m356.la_chaine_mixte, m333.la_nappe_de_la_spire_de_paris4)
    m356.la_chaine_mixte = lambda *a, **k: vu.update(k, lv=a[3], rg=k["regrandir"]("p", "n", "s", "o")) or []
    m333.la_nappe_de_la_spire_de_paris4 = lambda s_, o_, p_, n_, lv, marge=None: ("croissance", s_, o_, p_, n_, lv, marge)
    try:
        la_chaine_dune_maille("nappe", "relancer", "sauter", "m7")
    finally:
        m356.la_chaine_mixte, m333.la_nappe_de_la_spire_de_paris4 = avant
    v("★★★★ la chaîne : celle de 358, sa croissance bornée à une maille, sur m7, comptée comme 357",
      vu.get("compter") is m357.compter4 and vu.get("lv") == "m7" and vu.get("rg") == ("croissance", "s", "o", "p", "n", "m7", 1), str(vu))
    v("★★★ la marge est d'une maille", LA_MARGE == 1)

    s_ = lambda j, n, c=False, rang=5: {"la_justesse": j, "a_cheval": c, "les_points": n, "le_rang": rang}  # noqa: E731
    cotes = [{"le_rang": 5, "le_cote": "moins", "les_sauts": [dict(s_("juste", 100), le_tour_de_depart=0,
                                                                   en_plus={"le_depart": {"0": 900}, "la_gardee": {"-1": 900, "0": 70}}),
                                                              dict(s_("juste", 300, True)),
                                                              dict(s_("faux : deux tours", 900))]}]
    b = le_bilan(cotes)
    v("★★★★ le bilan : la surface et le cheval de 358 sur les sauts jugés, la naissance de 364",
      b["la_surface"] == 200.0 and b["les_justes_a_cheval"] == 1 and b["la_naissance"]["apres_elle"] == 1
      and b["la_naissance"]["les_cotes_juges"] == 1, str(b))

    def d_(su, au, sm=980.5, am=1, ok=True, ou_u=None, ou_m=None):
        def bil(s, a, ou):
            return {"la_surface": s, "la_naissance": {"les_cotes_juges": 5, "apres_elle": a, "ou_il_nait": a if ou is None else ou}}
        return {"les_pannes": [], "le_controle": ok, "les_bilans": {"dune_maille": bil(su, au, ou_u), "la_chaine_mixte": bil(sm, am, ou_m)}}
    v("★★★★ seules comptent les naissances après la première surface lisible, pas celles qu'une référence porte déjà",
      lambda: le_verdict(d_(1200.0, 1, ou_u=3, ou_m=1))["lissue"].endswith("sans faire naître le décalage"))
    v("★★★★ la règle : plus de surface et pas plus de naissances, oui ; plus de naissances, en partie ; pas plus de surface, non",
      lambda: le_verdict(d_(1200.0, 1))["lissue"].endswith("sans faire naître le décalage")
      and le_verdict(d_(1200.0, 2))["lissue"].endswith("et fait naître le décalage")
      and le_verdict(d_(980.5, 0))["lissue"].endswith("ne rend pas de surface")
      and le_verdict(d_(900.0, 0))["lissue"].endswith("ne rend pas de surface"))
    v("★★★ un contrôle tombé : indécidable", not le_verdict(d_(1200.0, 1, ok=False))["decidable"])
    v("★★★ aucun saut juste : indécidable", not le_verdict(d_(None, 0))["decidable"])

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
