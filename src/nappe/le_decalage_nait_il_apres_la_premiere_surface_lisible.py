"""Sur PHercParis4, graines 4 à 8, côtés moins, si l'on prend pour référence la première surface de chaque côté qui retrouve un seul tour, le décalage dont la chaîne qui regrandit hérite y est-il déjà, ou naît-il dans une croissance après elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES LECTURES DE `363` NE SOIENT RELUES AVEC CETTE RÉFÉRENCE. Ce qui était vu avant d'écrire : tout ce
que `296` à `363` publient, dont `R4-F549` (seule la nappe de la graine 6 retrouve un seul tour ; les nappes des graines 4, 5, 7 et 8 sont
sur un tour non publié, et leur chaîne atteint `5753_0` au premier ou au deuxième saut ; sur la graine 6, côté moins, la nappe est propre et
la chaîne qui regrandit a 17, 40, 74, 113 puis 147 points hors de leur tour aux cinq premiers sauts). Les suites des autres côtés n'ont pas
été regardées.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P161`. `363` a pris pour référence la nappe, illisible sur quatre graines sur cinq. La première
surface qui retrouve un seul tour est lisible partout où la chaîne descend ; ce qui est avant elle reste inconnu, ce qui est après se lit.

## Ce qui est fait, sans mesure neuve

- **Les lectures** : celles de `363`, qui porte, pour chaque saut des deux chaînes, les tours où sont posés les points de la surface de
  départ et de la surface gardée.
- **La référence** d'un côté : si le premier saut qui a un tour de départ est le saut h, la surface de départ de ce saut, la nappe si h = 1,
  la surface gardée du saut h − 1 sinon ; son tour est ce tour de départ.
- **La suite** : la référence puis chaque surface gardée après elle, chacune contre son propre tour, décalé d'un tour par saut dans le sens
  du côté ; la naissance, la première qui a 50 points hors de son tour.
- **Les côtés jugés** : les côtés moins des graines 4 à 8 qui ont une référence.
- **La règle**, sur la chaîne qui regrandit : parmi les côtés où le décalage naît, si plus de la moitié l'ont déjà dans la référence, **il
  y est déjà** ; si plus de la moitié le font naître après elle, **il naît dans une croissance après elle** ; sinon, **l'un et l'autre**.
  Indécidable sous 3 côtés où il naît.

## Les issues

L'issue de la tranche : **sur a côtés jugés, le décalage naît sur b ; dans la référence sur c, après elle sur d**, puis ce que dit la
règle.

## Rapporté à côté, qui ne décide rien

La même lecture sous la chaîne mixte ; le saut où il naît.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : quand la référence est la surface gardée d'un saut, si le décalage qu'elle porte vient de la nappe
ou de ce saut ; ni pourquoi la croissance passe sur le tour voisin.

Usage :
    uv run python src/nappe/le_decalage_nait_il_apres_la_premiere_surface_lisible.py --verifier
    uv run python src/nappe/le_decalage_nait_il_apres_la_premiere_surface_lisible.py \\
        --json docs/mesures/le_decalage_nait_il_apres_la_premiere_surface_lisible.json
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

import le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux as m344  # noqa: E402
import ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite as m363  # noqa: E402

CE_QUE_363_A_PUBLIE = RACINE / "docs" / "mesures" / "ou_nait_le_decalage_que_la_chaine_qui_regrandit_herite.json"
LE_SEUIL = m363.LE_SEUIL
LE_MINIMUM = 3


def la_suite(cote: dict, sens: int) -> dict | None:
    """La référence du côté, le premier saut qui a un tour de départ, puis les points hors de leur tour de la référence et de chaque
    surface gardée après elle ; et l'indice de la naissance, 0 pour la référence. None sans référence."""
    sauts = cote["les_sauts"]
    h = next((i for i, s in enumerate(sauts, 1) if s.get("le_tour_de_depart") is not None and s.get("en_plus")), None)
    if h is None:
        return None
    w = sauts[h - 1]["le_tour_de_depart"]
    suite = [m363.hors_de_son_tour(sauts[h - 1]["en_plus"]["le_depart"], w)]
    for j, s in enumerate(sauts[h - 1:], 1):
        if not s.get("en_plus") or not s["en_plus"]["la_gardee"]:
            break
        suite.append(m363.hors_de_son_tour(s["en_plus"]["la_gardee"], w + j * sens))
    naissance = next((i for i, n in enumerate(suite) if n >= LE_SEUIL), None)
    return {"la_reference": h - 1, "son_tour": w, "hors_de_son_tour": suite, "la_naissance": naissance}


def le_bilan(cotes: list[dict]) -> dict:
    lus = []
    for c in cotes:
        if c["le_rang"] not in m344.LES_GRAINES_PROPRES or c["le_cote"] != "moins":
            continue
        s = la_suite(c, m344.LE_SENS[c["le_cote"]])
        if s is not None:
            lus.append({"le_rang": c["le_rang"], **s})
    nes = [x for x in lus if x["la_naissance"] is not None]
    return {"les_cotes_juges": len(lus), "ou_il_nait": len(nes), "dans_la_reference": sum(x["la_naissance"] == 0 for x in nes),
            "apres_elle": sum(x["la_naissance"] > 0 for x in nes), "le_detail": lus}


def le_verdict(d: dict) -> dict:
    if not d.get("le_controle"):
        return {"decidable": False, "lissue": "indécidable : les lectures de 363 ne sont pas celles qu'il publie"}
    b = d["les_bilans"]["la_chaine_qui_regrandit"]
    if b["ou_il_nait"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : le décalage naît sur {b['ou_il_nait']} côtés"}
    tete = (f"sur {b['les_cotes_juges']} côtés jugés, le décalage naît sur {b['ou_il_nait']} ; dans la référence sur "
            f"{b['dans_la_reference']}, après elle sur {b['apres_elle']}")
    suite = ("il y est déjà" if 2 * b["dans_la_reference"] > b["ou_il_nait"]
             else "il naît dans une croissance après elle" if 2 * b["apres_elle"] > b["ou_il_nait"] else "l'un et l'autre")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer(chemin: Path = CE_QUE_363_A_PUBLIE) -> dict:
    t0 = time.monotonic()
    d363 = json.loads(chemin.read_text())
    controle = all(m363.le_bilan(v) == d363["les_bilans"][k] for k, v in d363["les_cotes"].items())
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"le_seuil": LE_SEUIL, "le_minimum": LE_MINIMUM},
         "la_source": chemin.name, "le_controle": bool(controle),
         "les_bilans": {k: le_bilan(v) for k, v in d363["les_cotes"].items()}}
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

    def cote(tours, departs, gardees, rang=5, nom="moins"):
        return {"le_rang": rang, "le_cote": nom, "les_sauts": [{"le_tour_de_depart": t, "en_plus": {"le_depart": dp, "la_gardee": g}}
                                                               for t, dp, g in zip(tours, departs, gardees)]}
    c = cote([None, 0, -1, -2], [{"1": 900}, {"0": 900, "-1": 20}, {}, {}], [{"0": 900, "-1": 20}, {"-1": 900, "-2": 5}, {"-2": 900, "-1": 60},
                                                                          {"-3": 900}])
    s = la_suite(c, -1)
    v("★★★★ la référence : la surface de départ du premier saut qui a un tour de départ ; puis chaque surface gardée contre son tour",
      s == {"la_reference": 1, "son_tour": 0, "hors_de_son_tour": [20, 5, 60, 0], "la_naissance": 2}, str(s))
    c0 = cote([0, -1], [{"0": 900, "-1": 70}, {}], [{"-1": 900}, {"-2": 900}])
    v("★★★★ une nappe qui retrouve un seul tour est la référence, et le décalage peut y être déjà",
      la_suite(c0, -1) == {"la_reference": 0, "son_tour": 0, "hors_de_son_tour": [70, 0, 0], "la_naissance": 0}, str(la_suite(c0, -1)))
    v("★★★ sans tour de départ nulle part, pas de référence", la_suite(cote([None, None], [{}, {}], [{"0": 9}, {"0": 9}]), -1) is None)
    c_vide = cote([0, -1, -2], [{"0": 900}, {}, {}], [{"-1": 900}, {}, {"-3": 900, "-2": 90}])
    v("★★★ la suite s'arrête à la première surface vide", la_suite(c_vide, -1)["hors_de_son_tour"] == [0, 0], str(la_suite(c_vide, -1)))
    b = le_bilan([c, c0, cote([0], [{"0": 900}], [{"-1": 900}], rang=6), cote([0], [{"0": 900, "1": 80}], [{"-1": 900}], rang=2),
                  cote([0], [{"0": 900, "1": 80}], [{"1": 900}], rang=7, nom="plus")])
    v("★★★★ le bilan : les côtés moins des graines 4 à 8 ; dans la référence ou après elle",
      (b["les_cotes_juges"], b["ou_il_nait"], b["dans_la_reference"], b["apres_elle"]) == (3, 2, 1, 1), str(b))

    def d_(ref, apres, ok=True):
        return {"le_controle": ok, "les_bilans": {"la_chaine_qui_regrandit": {"les_cotes_juges": 5, "ou_il_nait": ref + apres,
                                                                              "dans_la_reference": ref, "apres_elle": apres}}}
    v("★★★★ la règle : déjà là, après, l'un et l'autre", le_verdict(d_(3, 1))["lissue"].endswith("il y est déjà")
      and le_verdict(d_(1, 3))["lissue"].endswith("après elle") and le_verdict(d_(2, 2))["lissue"].endswith("l'un et l'autre"))
    v("★★★ sous 3 côtés où il naît, des lectures qui ne redonnent pas 363 : indécidable", not le_verdict(d_(1, 1))["decidable"]
      and le_verdict(d_(2, 1))["decidable"] and not le_verdict(d_(3, 1, ok=False))["decidable"])

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
