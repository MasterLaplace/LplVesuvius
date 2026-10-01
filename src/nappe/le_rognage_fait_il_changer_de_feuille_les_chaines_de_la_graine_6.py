"""Sur la graine 6, côté moins, de PHerc0358, les surfaces des chaînes rognées sont-elles sur les mêmes feuilles que celles des chaînes de 389, ou le rognage les fait-il changer de feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE CHAÎNE ROGNÉE NE SOIT COMPARÉE À SA CHAÎNE NON ROGNÉE. Ce qui était vu avant d'écrire : tout ce que
`296` à `397` publient, dont `R4-F583` (rognées, les chaînes de la graine 6, côté moins, perdent 14 validées à surfaces égales : 18 → 4) et
les nombres de feuilles que `389` et `397` publient pour ce côté (rognées, le deuxième saut de la compagne et le cinquième de la suivie,
nuls dans `389`, comptent une feuille).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P195`. Si les surfaces rognées sont sur les feuilles des chaînes de `389`, le rognage ne déplace
pas la chaîne, il change ses comptes, et c'est par les comptes que l'accord a perdu ses validées. Si elles ont changé de feuille, c'est la
chaîne elle-même qui part ailleurs.

## Ce qui est fait

- **Les chaînes** : les trois chaînes à seize sauts de la graine 6, côté moins, lancées deux fois, comme `389` puis comme `397` ; leurs
  nombres de feuilles doivent redonner ceux que `389` et `397` publient pour ce côté.
- **La comparaison** : pour chaque chaîne, les paires de `368` entre ses surfaces rognées et ses surfaces de `389` ; une surface rognée est
  **sur une feuille de `389`** si une surface de `389` de la même chaîne est même feuille qu'elle. Son compte de `m7` est alors comparé à
  celui de ces surfaces de `389`.
- **Les classes** d'une surface rognée comparée (qui a au moins une paire) : même feuille et même compte ; même feuille et autre compte ; hors
  des feuilles de `389`.
- **La règle**, sur les surfaces rognées comparées : si au moins 75 % sont sur une feuille de `389`, **oui, mêmes feuilles** ; au plus 25 %,
  **non, le rognage les fait changer de feuille** ; sinon, **en partie**. Indécidable sous 10 surfaces comparées, si une lecture échoue, ou
  si les nombres de feuilles ne redonnent pas `389` et `397`.

## Les issues

L'issue de la tranche : **sur n surfaces rognées comparées, f sont sur une feuille de `389`, dont c avec un autre compte, et h hors de ses
feuilles**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Pour chaque surface que `389` validait, la surface rognée sur sa feuille et son compte.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : lequel des deux comptes est juste ; PHerc0358 n'a pas de tours publiés.

Usage :
    uv run python src/nappe/le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.py --verifier
    uv run python src/nappe/le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.py \\
        --json docs/mesures/le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.json
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

import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux as m383  # noqa: E402
import les_sauts_doubles_de_369_franchissent_ils_deux_feuilles_de_m7_sur_pherc0358 as m384  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358 as m389  # noqa: E402
import une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358 as m397  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_389_A_PUBLIE = LES_MESURES / "laccord_aux_comptes_de_m7_valide_t_il_encore_a_seize_sauts_sur_pherc0358.json"
CE_QUE_397_A_PUBLIE = LES_MESURES / "une_chaine_qui_rogne_la_plage_retombee_se_contredit_elle_moins_sur_pherc0358.json"
LE_COTE = (6, "moins")
LES_CHAINES = ("suivie", "compagne", "tierce")
LA_PART, LA_PART_BASSE, LE_MINIMUM = 0.75, 0.25, 10
MEME, AUTRE, HORS = "meme_feuille_meme_compte", "meme_feuille_autre_compte", "hors_des_feuilles"


def la_classe(compte: int, paires: list[dict], comptes389: list[int]) -> str | None:
    """La classe d'une surface rognée, depuis ses paires avec les surfaces de `389` de la même chaîne ; None sans paire."""
    if not paires:
        return None
    vus = {comptes389[p["k"] - 1] for p in paires if p["meme"]}
    return HORS if not vus else MEME if compte in vus else AUTRE


def les_classes(rognees: list[int], comptes389: list[int], paires: list[dict]) -> list[dict]:
    """Pour chaque surface rognée d'une chaîne, ses paires avec les surfaces de `389`, sa classe et les comptes de `389` de sa feuille."""
    out = []
    for h, c in enumerate(rognees, 1):
        siennes = [p for p in paires if p["h"] == h]
        out.append({"le_saut": h, "le_compte": c, "la_classe": la_classe(c, siennes, comptes389),
                    "les_comptes_de_389": sorted({comptes389[p["k"] - 1] for p in siennes if p["meme"]}),
                    "les_sauts_de_389": sorted(p["k"] for p in siennes if p["meme"])})
    return out


def le_bilan(classes: dict) -> dict:
    toutes = [s for x in LES_CHAINES for s in classes[x] if s["la_classe"] is not None]
    return {"comparees": len(toutes), "sur_389": sum(s["la_classe"] != HORS for s in toutes),
            "autre_compte": sum(s["la_classe"] == AUTRE for s in toutes), "hors": sum(s["la_classe"] == HORS for s in toutes)}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne"):
        return {"decidable": False, "lissue": "indécidable : les nombres de feuilles ne redonnent pas 389 et 397"}
    b = d["le_bilan"]
    if b["comparees"] < LE_MINIMUM:
        return {"decidable": False, "lissue": f"indécidable : {b['comparees']} surfaces rognées comparées, moins de {LE_MINIMUM}"}
    tete = (f"sur {b['comparees']} surfaces rognées comparées, {b['sur_389']} sont sur une feuille de 389, dont {b['autre_compte']} avec un "
            f"autre compte, et {b['hors']} hors de ses feuilles")
    p = b["sur_389"] / b["comparees"]
    suite = "oui, mêmes feuilles" if p >= LA_PART else "non, le rognage les fait changer de feuille" if p <= LA_PART_BASSE else "en partie"
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def les_chaines(enchainer) -> tuple[dict, object, dict]:
    m383._LES_CHAINES_ENTIERES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=m383.le_chaineur(enchainer), cotes={LE_COTE})
    assert len(chaines) == 1 and (chaines[0]["le_rang"], chaines[0]["le_cote"]) == LE_COTE
    return m383._LES_CHAINES_ENTIERES[0], lv0, stats0


def les_comptes(e: dict, lv0) -> tuple[dict, dict, dict]:
    surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
    s369 = {x: m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x]) for x in LES_CHAINES}
    nb = {x: m383.les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
    sauts = {x: [{**a, "le_nombre_de_feuilles": b["le_nombre_de_feuilles"]} for a, b in zip(s369[x], nb[x])] for x in LES_CHAINES}
    return surf, {x: [s["le_nombre_de_feuilles"] for s in sauts[x]] for x in LES_CHAINES}, \
        {x: [s["le_compte_corrige"] for s in m384.les_comptes_de_m7(sauts[x])] for x in LES_CHAINES}


def mesurer() -> dict:
    t0 = time.monotonic()
    d389, d397 = (json.loads(x.read_text()) for x in (CE_QUE_389_A_PUBLIE, CE_QUE_397_A_PUBLIE))
    c389 = next(c for c in d389["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    c397 = next(c for c in d397["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    e0, lv0, st0 = les_chaines(m389.enchainer)
    surf0, nb0, cpt0 = les_comptes(e0, lv0)
    e1, lv1, st1 = les_chaines(m397.enchainer)
    surf1, nb1, cpt1 = les_comptes(e1, lv1)
    redonne = (nb0 == c389["les_nombres"] and cpt0 == c389["les_comptes"]
               and nb1 == {x: [s["le_nombre_de_feuilles"] for s in c397["les_sauts"][x]] for x in LES_CHAINES})
    paires, classes = {}, {}
    for x in LES_CHAINES:
        p = m368.les_paires(surf1[x], surf0[x])
        paires[x] = [{"h": q["le_saut_suivi"], "k": q["le_saut_compagnon"], "meme": q["meme_feuille"]} for q in p]
        classes[x] = les_classes(cpt1[x], cpt0[x], paires[x])
    validees = [(s["la_chaine"], s["le_saut"], s["le_compte"]) for s in c389["les_surfaces"] if s["le_statut"] == "validée"]
    sur_les_validees = [{"la_chaine": x, "le_saut_de_389": h, "le_compte_de_389": c,
                         "les_rognees": [[s["le_saut"], s["le_compte"]] for s in classes[x] if h in s["les_sauts_de_389"]]}
                        for x, h, c in validees]
    d = {"la_question": __doc__.splitlines()[0], "le_cote": list(LE_COTE),
         "les_constantes": {"la_part": LA_PART, "la_part_basse": LA_PART_BASSE, "le_minimum": LE_MINIMUM},
         "les_pannes": list(st0["pannes"]) + list(st1["pannes"]), "redonne": bool(redonne),
         "les_comptes_de_389": cpt0, "les_comptes_rognes": cpt1, "les_paires": paires, "les_classes": classes,
         "sur_les_validees_de_389": sur_les_validees}
    d["le_bilan"] = le_bilan(classes)
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

    cpt389 = [1, 1, 2, 3]
    v("★★★★ la classe : même feuille et même compte, même feuille et autre compte, hors des feuilles, sans paire",
      la_classe(2, [{"k": 3, "meme": True}], cpt389) == MEME and la_classe(3, [{"k": 3, "meme": True}], cpt389) == AUTRE
      and la_classe(2, [{"k": 3, "meme": False}, {"k": 4, "meme": False}], cpt389) == HORS and la_classe(2, [], cpt389) is None)
    v("★★★★ une surface même feuille que deux surfaces de 389 de comptes différents est au même compte si l'un des deux est le sien",
      la_classe(2, [{"k": 2, "meme": True}, {"k": 3, "meme": True}], cpt389) == MEME
      and la_classe(1, [{"k": 2, "meme": True}, {"k": 3, "meme": True}], cpt389) == MEME)
    cl = les_classes([1, 2, 4], cpt389, [{"h": 1, "k": 1, "meme": True}, {"h": 2, "k": 3, "meme": True}, {"h": 2, "k": 4, "meme": False},
                                          {"h": 3, "k": 3, "meme": False}])
    v("★★★★ les classes d'une chaîne, avec les sauts et les comptes de 389 de leur feuille",
      [(s["le_saut"], s["la_classe"], s["les_sauts_de_389"], s["les_comptes_de_389"]) for s in cl]
      == [(1, MEME, [1], [1]), (2, MEME, [3], [2]), (3, HORS, [], [])], str(cl))
    b = le_bilan({"suivie": cl, "compagne": [{"la_classe": AUTRE}], "tierce": [{"la_classe": None}]})
    v("★★★★ le bilan : les surfaces sans paire ne sont pas comparées", b == {"comparees": 4, "sur_389": 3, "autre_compte": 1, "hors": 1}, str(b))

    def d_(n, s, a, h, ok=True):
        return {"redonne": ok, "les_pannes": [], "le_bilan": {"comparees": n, "sur_389": s, "autre_compte": a, "hors": h}}
    v("★★★★ la règle : trois quarts sur une feuille de 389, oui ; un quart au plus, non ; sinon, en partie",
      le_verdict(d_(12, 9, 4, 3))["lissue"].endswith("mêmes feuilles") and le_verdict(d_(12, 3, 1, 9))["lissue"].endswith("changer de feuille")
      and le_verdict(d_(12, 6, 1, 6))["lissue"].endswith("; en partie")
      and "sur 12 surfaces rognées comparées, 9 sont sur une feuille de 389, dont 4 avec un autre compte, et 3 hors" in le_verdict(d_(12, 9, 4, 3))["lissue"])
    v("★★★ indécidable sous 10 comparées ou sans redonne", not le_verdict(d_(9, 9, 0, 0))["decidable"]
      and not le_verdict(d_(12, 9, 0, 3, ok=False))["decidable"])

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
