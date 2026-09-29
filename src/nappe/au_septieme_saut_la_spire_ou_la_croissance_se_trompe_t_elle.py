"""Au septième saut, là où la chaîne relancée depuis sa spire se trompe de tour publié, la spire elle-même est-elle sur le mauvais tour, ou est-ce la croissance au-delà de la spire qui y retombe ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE SPIRE NE SOIT LUE CONTRE LES TOURS PUBLIÉS. Ce qui était vu avant d'écrire : tout ce que
`296` à `333` publient, dont `R4-F519` (relancée depuis sa spire, la chaîne descend six tours publiés en médiane sur PHercParis4 et fait
trois sauts faux, tous au septième saut, après `5753_-6`, sur les graines 2, 3 et 4). `333` ne lit que la nappe relancée.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P130`. La nappe relancée est faite de deux parts : les mailles semées depuis la spire,
chacune sur la feuille de son point, et ce que la croissance a posé au-delà. Si la spire est déjà sur un mauvais tour, c'est le saut qui
se trompe ; si elle n'y est pas, c'est la croissance qui y retombe, et c'est elle qu'il faudrait borner.

## Ce qui est fait

- **La chaîne** : celle de `333` sur PHercParis4, sans rien y changer ; elle doit redonner, côté par côté, la descente et ce qui l'arrête
  que `333` publie, sans quoi la tranche est indécidable.
- **Les lectures** : à chaque saut, ce que la comparaison de `321` dit, contre chacun des tours `5753_0` à `5753_-7`, de la spire (ses
  points posés), et de la part de la nappe relancée que la croissance a posée hors de ses semis ; et, comme `333`, de la nappe relancée
  entière.
- **Ce qui est jugé** : pour chaque côté dont la descente s'arrête sur un saut faux, la spire du saut où elle s'arrête. Elle est **sur un
  mauvais tour** si elle en retrouve un sans retrouver celui qu'on attend ; **sur le bon tour** si elle retrouve celui qu'on attend ;
  **hors de tout tour** si elle n'en retrouve aucun.

## Les issues

L'issue de la tranche : **sur les f sauts faux, la spire est déjà sur un mauvais tour k fois, sur le bon tour j fois, hors de tout tour z
fois** ; et, déclaré avant : **c'est la spire qui se trompe** si k > f/2 ; **c'est la croissance qui y retombe** si k < f/2 ; **la
lecture ne tranche pas** si k = f/2.

## Rapporté à côté, qui ne décide rien

Ce que la croissance hors des semis retrouve au saut faux ; la descente de `330` jugée sur les spires seules au lieu des nappes relancées.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi la spire ou la croissance tombe là ; ni ce que ferait une croissance bornée.

Usage :
    uv run python src/nappe/au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.py --verifier
    uv run python src/nappe/au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.py \\
        --json docs/mesures/au_septieme_saut_la_spire_ou_la_croissance_se_trompe_t_elle.json
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

import la_chaine_qui_croit_tombe_t_elle_sur_les_tours_publies as m329  # noqa: E402
import jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle as m330  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse as m333  # noqa: E402

CE_QUE_333_A_PUBLIE = RACINE / "docs" / "mesures" / "la_relance_partie_de_la_spire_entiere_garde_t_elle_la_justesse.json"


def les_retrouves(lectures: dict) -> list[int]:
    return sorted(int(t) for t, x in lectures.items() if x == "retrouve")


def ce_que_dit_la_spire(lectures: dict, attendu: int) -> str:
    r = les_retrouves(lectures)
    if attendu in r:
        return "sur le bon tour"
    return "sur un mauvais tour" if r else "hors de tout tour"


def le_saut_ou_elle_sarrete(cote: dict) -> tuple[int, int] | None:
    """Pour une descente de `330` arrêtée, le rang (à partir de 1) du saut dont la surface l'arrête, et le tour qu'elle attendait ; None
    si la descente ne s'arrête pas sur une surface."""
    surfaces = [{int(t): x for t, x in cote["les_tours_de_la_nappe"].items()}]
    surfaces += [{int(t): x for t, x in s["les_tours"].items()} if "les_tours" in s else {} for s in cote["les_surfaces"]]
    k0 = next((k for k, s in enumerate(surfaces) if m329.le_tour_de_la_nappe(s) is not None), None)
    if k0 is None or cote["le_tour_de_depart"] is None:
        return None
    fin = k0 + cote["la_descente"] + 1
    if fin >= len(surfaces):
        return None
    return fin, cote["le_tour_de_depart"] - cote["la_descente"] - 1


def les_sauts_faux(graines: list[dict]) -> list[dict]:
    out = []
    for g in graines:
        for nom, c in g["les_cotes"].items():
            if c["larret"] != "un saut faux":
                continue
            ou = le_saut_ou_elle_sarrete(c)
            if ou is None:
                out.append({"le_rang": g["le_rang"], "le_cote": nom, "le_saut": None, "lissue": "introuvable"})
                continue
            h, attendu = ou
            s = c["les_surfaces"][h - 1]
            out.append({"le_rang": g["le_rang"], "le_cote": nom, "le_saut": h, "le_tour_attendu": attendu,
                        "la_nappe_retrouve": les_retrouves(s.get("les_tours", {})),
                        "la_spire_retrouve": les_retrouves(s["les_tours_de_la_spire"]),
                        "la_croissance_retrouve": les_retrouves(s.get("les_tours_de_la_croissance", {})),
                        "lissue": ce_que_dit_la_spire(s["les_tours_de_la_spire"], attendu)})
    return out


def la_descente_des_spires(cote: dict) -> dict:
    surfaces = [{int(t): x for t, x in cote["les_tours_de_la_nappe"].items()}]
    surfaces += [{int(t): x for t, x in s["les_tours_de_la_spire"].items()} for s in cote["les_surfaces"]]
    return m330.la_descente(surfaces)


def redonne_333(d: dict, publie: dict) -> bool:
    a = {(g["le_rang"], n): (c["le_tour_de_depart"], c["la_descente"], c["larret"])
         for g in d["les_graines"]["PHercParis4"] for n, c in g["les_cotes"].items()}
    b = {(g["le_rang"], n): (c["le_tour_de_depart"], c["la_descente"], c["larret"])
         for g in publie["les_graines"]["PHercParis4"] for n, c in g["les_cotes"].items()}
    return a == b


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_333"):
        return {"decidable": False, "lissue": "indécidable : la chaîne ne redonne pas celle de 333"}
    fx = d["les_sauts_faux"]
    if not fx or any(x["lissue"] == "introuvable" for x in fx):
        return {"decidable": False, "lissue": "indécidable : aucun saut faux à lire, ou un saut faux introuvable"}
    f = len(fx)
    k = sum(1 for x in fx if x["lissue"] == "sur un mauvais tour")
    j = sum(1 for x in fx if x["lissue"] == "sur le bon tour")
    z = f - k - j
    tete = (f"sur les {f} sauts faux, la spire est déjà sur un mauvais tour {k} fois, sur le bon tour {j} fois, hors de tout tour {z} "
            f"fois")
    suite = ("c'est la spire qui se trompe" if 2 * k > f else "c'est la croissance qui y retombe" if 2 * k < f
             else "la lecture ne tranche pas")
    return {"decidable": True, "f": f, "k": k, "j": j, "z": z, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    d = m331.mesurer(relancer4=lambda lv: (lambda p_, n_, s_, o_: m333.la_nappe_de_la_spire_de_paris4(s_, o_, p_, n_, lv)),
                     avec_la_spire=True, lire_la_spire=True, rouleaux=("PHercParis4",))
    d.pop("les_cotes", None)
    d["la_question"] = __doc__.splitlines()[0]
    d["redonne_333"] = redonne_333(d, json.loads(CE_QUE_333_A_PUBLIE.read_text()))
    d["les_sauts_faux"] = les_sauts_faux(d["les_graines"]["PHercParis4"])
    d["les_descentes_des_spires"] = [{"le_rang": g["le_rang"], "le_cote": n, **la_descente_des_spires(c)}
                                     for g in d["les_graines"]["PHercParis4"] for n, c in g["les_cotes"].items()]
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

    R, N = "retrouve", "ne retrouve pas"
    v("★★★★ la spire est sur le bon tour dès qu'elle retrouve celui qu'on attend, même avec un autre",
      ce_que_dit_la_spire({"-7": R, "-6": R}, -7) == "sur le bon tour")
    v("★★★★ sur un mauvais tour si elle en retrouve un autre sans celui qu'on attend",
      ce_que_dit_la_spire({"-7": N, "-6": R}, -7) == "sur un mauvais tour")
    v("★★★ hors de tout tour si elle n'en retrouve aucun", ce_que_dit_la_spire({"-7": "non lue", "-6": N}, -7) == "hors de tout tour")

    tours = lambda *r: {str(t): (R if t in r else N) for t in range(0, -8, -1)}  # noqa: E731
    cote = {"le_tour_de_depart": 0, "la_descente": 2, "larret": "un saut faux",
            "les_tours_de_la_nappe": tours(0, -1),
            "les_surfaces": [{"les_tours": tours(0), "les_tours_de_la_spire": tours(0)},
                             {"les_tours": tours(-1), "les_tours_de_la_spire": tours(-1)},
                             {"les_tours": tours(-2), "les_tours_de_la_spire": tours(-2)},
                             {"les_tours": tours(-5), "les_tours_de_la_spire": tours(-3), "les_tours_de_la_croissance": tours(-5)},
                             {"les_tours": tours(-6), "les_tours_de_la_spire": tours(-6)}]}
    v("★★★★★ le saut qui arrête la descente : compté depuis la première surface qui retrouve un seul tour, pas depuis la nappe",
      le_saut_ou_elle_sarrete(cote) == (4, -3), str(le_saut_ou_elle_sarrete(cote)))
    fx = les_sauts_faux([{"le_rang": 5, "les_cotes": {"moins": cote, "plus": dict(cote, larret="un tour manqué")}}])
    v("★★★★★ la spire lue est celle du saut qui arrête, pas celle du suivant ni du précédent",
      len(fx) == 1 and fx[0]["lissue"] == "sur le bon tour" and fx[0]["la_nappe_retrouve"] == [-5]
      and fx[0]["la_croissance_retrouve"] == [-5], str(fx))
    v("★★★ seuls les côtés arrêtés sur un saut faux sont lus", len(fx) == 1 and fx[0]["le_cote"] == "moins")
    ds = la_descente_des_spires(cote)
    v("★★★★ la descente jugée sur les spires seules", ds["la_descente"] == 3 and ds["larret"] == "un saut faux", str(ds))

    x_ = lambda i: {"lissue": i}  # noqa: E731
    base = {"les_pannes": [], "redonne_333": True}
    vd = le_verdict(dict(base, les_sauts_faux=[x_("sur un mauvais tour"), x_("sur un mauvais tour"), x_("sur le bon tour")]))
    v("★★★★ deux spires sur trois sur un mauvais tour : c'est la spire qui se trompe", vd["lissue"].endswith("c'est la spire qui se trompe"))
    vd = le_verdict(dict(base, les_sauts_faux=[x_("sur un mauvais tour"), x_("hors de tout tour"), x_("sur le bon tour")]))
    v("★★★★ une sur trois : c'est la croissance qui y retombe", vd["lissue"].endswith("c'est la croissance qui y retombe")
      and (vd["k"], vd["j"], vd["z"]) == (1, 1, 1))
    vd = le_verdict(dict(base, les_sauts_faux=[x_("sur un mauvais tour"), x_("hors de tout tour")]))
    v("★★★ une sur deux : la lecture ne tranche pas", vd["lissue"].endswith("la lecture ne tranche pas"))
    v("★★★★ une chaîne qui ne redonne pas 333 est indécidable", not le_verdict(dict(base, redonne_333=False,
                                                                                   les_sauts_faux=[x_("sur le bon tour")]))["decidable"])
    v("★★★ un saut faux introuvable rend la tranche indécidable",
      not le_verdict(dict(base, les_sauts_faux=[x_("introuvable"), x_("sur le bon tour")]))["decidable"])
    publie = {"les_graines": {"PHercParis4": [{"le_rang": 1, "les_cotes": {"moins": {"le_tour_de_depart": 0, "la_descente": 6,
                                                                                    "larret": "un saut faux"}}}]}}
    autre = json.loads(json.dumps(publie))
    autre["les_graines"]["PHercParis4"][0]["les_cotes"]["moins"]["larret"] = "un tour manqué"
    v("★★★★ la reproduction de 333 compare la descente ET ce qui l'arrête", redonne_333(publie, publie)
      and not redonne_333(autre, publie))

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
