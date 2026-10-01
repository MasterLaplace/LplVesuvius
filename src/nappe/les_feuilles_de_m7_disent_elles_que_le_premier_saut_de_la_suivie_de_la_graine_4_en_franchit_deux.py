"""Sur PHerc0358, les feuilles de m7 franchies entre la nappe et la première surface des trois chaînes de la graine 4, côté plus, disent-elles que le premier saut de la suivie, à 1,40 pas, en franchit deux comme les autres ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE FEUILLE DE `m7` NE SOIT COMPTÉE SUR LA GRAINE 4, CÔTÉ PLUS. Ce qui était vu avant d'écrire :
tout ce que `296` à `382` publient, dont `R4-F567` (recompté double, le premier saut de la suivie, à 1,40 pas, fait tenir ses deux
couples, 27 paires sur 27 et 24 sur 24), `R4-F568` (la règle qui cherche seule le saut à recompter hésite entre le premier et le deuxième)
et `R4-F540` (sur PHerc0358, le compte des feuilles de `345`, au pas de 20 voxels et à une portée latérale de 0,555 pas, mesure les sauts).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P180`. L'accord et le recompte disent qu'un saut compté double fait tenir la suivie, mais ni
l'un ni l'autre ne voit ce qu'il y a entre la nappe et la surface. Deux explications rendent les mêmes paires : le premier saut de la suivie
franchit deux feuilles, à un écart court ; ou il n'en franchit qu'une, et les nappes de départ de la compagne et de la tierce sont une
feuille plus loin que celle de la suivie, de sorte que leurs comptes partent d'une autre feuille. `m7` les sépare.

## Ce qui est fait

- **Les chaînes** : les trois chaînes de `373` sur la graine 4, côté plus, rejouées comme `380` les a lancées ; leurs surfaces doivent
  redonner les points et les écarts des sauts que `380` publie, sans quoi la tranche est indécidable.
- **Le compte** : celui de `345`, comme `354` le porte sur PHerc0358 : pour au plus 1200 points posés de la surface d'arrivée, les plages
  de `m7` passées le long de sa normale jusqu'à la surface de départ, au pas de 20 voxels, à une portée latérale de 0,555 pas. Le **nombre
  de feuilles** d'un saut est le compte que porte le plus de points mesurés, s'il y en a au moins 50 et qu'aucun autre compte n'en porte
  autant ; sinon il n'est pas dit.
- **Les sauts** : chaque saut des trois chaînes, depuis la surface d'où il part (la nappe de départ pour le premier) ; **les nappes** : celle
  de la compagne et celle de la tierce, comptées contre celle de la suivie.
- **La règle** : si le premier saut de la suivie franchit deux feuilles et que les nappes de la compagne et de la tierce sont sur la feuille
  de la suivie, **oui, `m7` dit ce que dit le recompte de `381`** ; si le premier saut de la suivie ne franchit qu'une feuille, **non** ;
  sinon, **en partie**. Indécidable si l'un de ces trois nombres n'est pas dit, si une lecture échoue, ou si les chaînes ne redonnent pas `380`.

## Les issues

L'issue de la tranche : **le premier saut de la suivie franchit f feuilles ; les nappes de la compagne et de la tierce sont à c et t
feuilles de celle de la suivie**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

Le nombre de feuilles de chaque saut des trois chaînes, à côté du genre que `369` lui donne ; la part des points mesurés qui franchissent
deux feuilles.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si `m7` manque une feuille entre deux surfaces, un saut qui en franchit deux y est compté comme n'en
franchissant qu'une ; et ce que vaut le compte sur d'autres côtés.

Usage :
    uv run python src/nappe/les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.py --verifier
    uv run python src/nappe/les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.py \\
        --json docs/mesures/les_feuilles_de_m7_disent_elles_que_le_premier_saut_de_la_suivie_de_la_graine_4_en_franchit_deux.json
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

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import les_feuilles_de_m7_franchies_separent_elles_les_sauts_justes_des_faux as m345  # noqa: E402
import le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358 as m354  # noqa: E402
import la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358 as m366  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402
import deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358 as m368  # noqa: E402
import le_glissement_se_voit_il_dans_la_chaine_seule as m369  # noqa: E402
import trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse as m373  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_380_A_PUBLIE = LES_MESURES / "laccord_de_trois_chaines_valide_t_il_sur_les_cotes_que_324_na_pas_retenus.json"
LE_COTE = (4, "plus")
SUIVIE, COMPAGNE, TIERCE = "suivie", "compagne", "tierce"
LES_CHAINES = (SUIVIE, COMPAGNE, TIERCE)
LE_PAS = m300.LE_PAS_0358
LE_LATERAL = m354.LE_LATERAL_EN_PAS * LE_PAS
LE_MINIMUM_DE_MESURES = m345.LE_MINIMUM_DE_MESURES
_LES_CHAINES_ENTIERES: list = []


def le_chaineur(enchainer=None):
    """Les trois chaînes de `373`, depuis la nappe, la graine compagne et la graine tierce, gardées entières avec leurs nappes."""
    enchainer = enchainer or m366.la_chaine_dune_maille_de_0358

    def chainer(nappe, relancer, sauter, lire_valeurs):
        suivie = enchainer(nappe, relancer, sauter, lire_valeurs)
        g = m368.la_graine_compagne(nappe)
        nc = None if g is None else m305.la_nappe_croissante(tuple(g[0]), tuple(g[1]), lire_valeurs)
        t = m373.la_graine_tierce(nappe)
        nt = None if t is None else m305.la_nappe_croissante(tuple(t[0][0]), tuple(t[0][1]), lire_valeurs)
        _LES_CHAINES_ENTIERES.append({"les_nappes": {SUIVIE: nappe, COMPAGNE: nc, TIERCE: nt},
                                      "les_chaines": {SUIVIE: suivie,
                                                      COMPAGNE: [] if nc is None else enchainer(nc, relancer, sauter, lire_valeurs),
                                                      TIERCE: [] if nt is None else enchainer(nt, relancer, sauter, lire_valeurs)}})
        return suivie
    return chainer


def le_nombre_de_feuilles(comptes: dict, minimum: int = LE_MINIMUM_DE_MESURES) -> int | None:
    """Le compte que porte le plus de points mesurés, s'ils sont au moins `minimum` et qu'aucun autre compte n'en porte autant."""
    n = {int(k): v for k, v in comptes.items()}
    if sum(n.values()) < minimum:
        return None
    haut = max(n.values())
    tete = [k for k, v in n.items() if v == haut]
    return tete[0] if len(tete) == 1 else None


def le_compte(depart: dict | None, arrivee: dict | None, lire_valeurs) -> dict:
    """Le compte de `345` entre deux surfaces, comme `354` le porte sur PHerc0358, et le nombre de feuilles qu'il dit."""
    r = None if depart is None else m345.les_comptes_point_par_point(depart, arrivee, lire_valeurs, LE_PAS, lateral=LE_LATERAL)
    f = m345.le_resume(r)
    return {**f, "le_nombre_de_feuilles": le_nombre_de_feuilles(f["les_comptes"])}


def les_sauts(nappe: dict | None, chaine: list[dict], lire_valeurs) -> list[dict]:
    """Chaque saut d'une chaîne, compté depuis la surface d'où il part : la nappe pour le premier, la surface précédente ensuite."""
    out, avant = [], nappe
    for h, k in enumerate(chaine, 1):
        rl = k.get("la_relance")
        out.append({"le_saut": h, **le_compte(avant, rl, lire_valeurs)})
        avant = rl
    return out


def redonne_380(points: dict, ecarts: dict, c380: dict) -> bool:
    """Les surfaces rejouées ont les points, et leurs sauts les écarts, que `380` publie."""
    return bool(points == c380["les_points_par_surface"]
                and all(ecarts[x] == [s["lecart_median"] for s in c380["les_sauts"][x]] for x in LES_CHAINES))


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d.get("redonne_380"):
        return {"decidable": False, "lissue": "indécidable : les chaînes rejouées ne redonnent pas 380"}
    f = d["les_sauts"][SUIVIE][0]["le_nombre_de_feuilles"]
    c, t = (d["les_nappes"][x]["le_nombre_de_feuilles"] for x in (COMPAGNE, TIERCE))
    if f is None or c is None or t is None:
        return {"decidable": False, "lissue": "indécidable : le premier saut de la suivie ou une nappe n'a pas de nombre de feuilles dit"}
    tete = (f"le premier saut de la suivie franchit {f} feuille{'s' if f > 1 else ''} ; les nappes de la compagne et de la tierce sont à {c} "
            f"et {t} feuille{'s' if t > 1 else ''} de celle de la suivie")
    suite = ("oui, m7 dit ce que dit le recompte de 381" if f == 2 and c == 0 and t == 0 else "non" if f == 1 else "en partie")
    return {"decidable": True, "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    _LES_CHAINES_ENTIERES.clear()
    c380 = next(c for c in json.loads(CE_QUE_380_A_PUBLIE.read_text())["les_cotes"] if (c["le_rang"], c["le_cote"]) == LE_COTE)
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=le_chaineur(), cotes={LE_COTE})
    e = _LES_CHAINES_ENTIERES[0]
    surf = {x: [m367.les_points(k.get("la_relance")) for k in e["les_chaines"][x]] for x in LES_CHAINES}
    points = {x: [int(len(u[0])) for u in surf[x]] for x in LES_CHAINES}
    ecarts = {x: [s["lecart_median"] for s in m369.les_sauts(m367.les_points(e["les_nappes"][x]), surf[x])] for x in LES_CHAINES}
    sauts = {x: les_sauts(e["les_nappes"][x], e["les_chaines"][x], lv0) for x in LES_CHAINES}
    for x in LES_CHAINES:
        for s, k in zip(sauts[x], c380["les_sauts"][x]):
            s.update({"lecart_median": k["lecart_median"], "le_genre": k["le_genre"]})
    nappes = {x: le_compte(e["les_nappes"][SUIVIE], e["les_nappes"][x], lv0) for x in (COMPAGNE, TIERCE)}
    d = {"la_question": __doc__.splitlines()[0], "le_cote": list(LE_COTE),
         "les_constantes": {"le_pas": round(LE_PAS, 3), "le_lateral": round(LE_LATERAL, 3), "le_minimum_de_mesures": LE_MINIMUM_DE_MESURES},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "redonne_380": bool(len(chaines) == 1 and redonne_380(points, ecarts, c380)), "les_sauts": sauts, "les_nappes": nappes}
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

    v("★★★★ le nombre de feuilles : le compte du plus de points, au moins 50, sans égal",
      le_nombre_de_feuilles({"1": 10, "2": 60}) == 2 and le_nombre_de_feuilles({"1": 30, "2": 15}) is None
      and le_nombre_de_feuilles({"1": 40, "2": 40}) is None and le_nombre_de_feuilles({"0": 50}) == 0)
    v("★★★★ les constantes de 354 : 20 voxels de pas, une portée latérale de 0,555 pas",
      abs(LE_PAS - 20.0) < 1e-6 and abs(LE_LATERAL / LE_PAS - m345.LE_LATERAL_L2 / m345.m321.LE_PAS_L2) < 1e-9)

    def plan(y: float, n: int = 12) -> dict:
        g = np.zeros((n, n, 3))
        g[..., 0], g[..., 2] = np.meshgrid(np.arange(n) * 4.0 + 100.0, np.arange(n) * 4.0 + 100.0, indexing="ij")
        g[..., 1] = y
        return {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}

    def feuilles(*ys):
        def lire(idx):
            return np.isin(idx[..., 1], [int(y) for y in ys]).astype(np.uint8)
        return lire
    lire = feuilles(100, 120, 140, 160)
    v("★★★★ le compte : deux plans sur des feuilles voisines franchissent une feuille, à deux feuilles d'écart deux, sur la même zéro",
      lambda: le_compte(plan(100.0), plan(120.0), lire)["le_nombre_de_feuilles"] == 1
      and le_compte(plan(100.0), plan(140.0), lire)["le_nombre_de_feuilles"] == 2
      and le_compte(plan(100.0), plan(100.0), lire)["le_nombre_de_feuilles"] == 0)
    v("★★★★ un compte sans surface de départ ou d'arrivée n'est pas dit",
      lambda: le_compte(None, plan(120.0), lire)["le_nombre_de_feuilles"] is None
      and le_compte(plan(100.0), None, lire)["le_nombre_de_feuilles"] is None)
    ch = [{"la_relance": plan(140.0)}, {"la_relance": plan(160.0)}]
    v("★★★★ les sauts : le premier depuis la nappe, les suivants depuis la surface précédente",
      lambda: [s["le_nombre_de_feuilles"] for s in les_sauts(plan(100.0), ch, lire)] == [2, 1])
    c380 = {"les_points_par_surface": {x: [3, 4] for x in LES_CHAINES},
            "les_sauts": {x: [{"lecart_median": 1.5}, {"lecart_median": 2.5}] for x in LES_CHAINES}}
    v("★★★★ redonne 380 : les points et les écarts de chaque chaîne",
      redonne_380({x: [3, 4] for x in LES_CHAINES}, {x: [1.5, 2.5] for x in LES_CHAINES}, c380)
      and not redonne_380({**{x: [3, 4] for x in LES_CHAINES}, TIERCE: [3, 5]}, {x: [1.5, 2.5] for x in LES_CHAINES}, c380)
      and not redonne_380({x: [3, 4] for x in LES_CHAINES}, {**{x: [1.5, 2.5] for x in LES_CHAINES}, SUIVIE: [1.5, 2.4]}, c380))

    def d_(f, c, t, ok=True, pannes=()):
        return {"redonne_380": ok, "les_pannes": list(pannes), "les_sauts": {SUIVIE: [{"le_nombre_de_feuilles": f}]},
                "les_nappes": {COMPAGNE: {"le_nombre_de_feuilles": c}, TIERCE: {"le_nombre_de_feuilles": t}}}
    v("★★★★ la règle : deux feuilles et les nappes sur la même feuille, oui ; une feuille, non ; sinon, en partie",
      le_verdict(d_(2, 0, 0))["lissue"].endswith("recompte de 381") and le_verdict(d_(1, 0, 0))["lissue"].endswith("; non")
      and le_verdict(d_(1, 1, 1))["lissue"].endswith("; non") and le_verdict(d_(2, 1, 0))["lissue"].endswith("; en partie")
      and le_verdict(d_(3, 0, 0))["lissue"].endswith("; en partie")
      and "franchit 2 feuilles ; les nappes de la compagne et de la tierce sont à 0 et 0 feuille" in le_verdict(d_(2, 0, 0))["lissue"])
    v("★★★ indécidable sans nombre dit, sans redonne, ou sur une lecture en panne",
      not le_verdict(d_(None, 0, 0))["decidable"] and not le_verdict(d_(2, None, 0))["decidable"]
      and not le_verdict(d_(2, 0, 0, ok=False))["decidable"] and not le_verdict(d_(2, 0, 0, pannes=("x",)))["decidable"]
      and le_verdict(d_(2, 0, 0))["decidable"])

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
