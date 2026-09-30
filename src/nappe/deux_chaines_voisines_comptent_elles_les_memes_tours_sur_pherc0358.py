"""Sur PHerc0358, là où deux chaînes d'une maille de graines différentes se recouvrent, les surfaces que l'accord met sur la même feuille ont-elles toutes le même décalage de sauts entre les deux graines ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CHAÎNE COMPAGNE NE TOURNE. Ce qui était vu avant d'écrire : tout ce que `296` à `367` publient,
dont `R4-F553` (sur PHercParis4, deux chaînes d'une maille qui se croisent sont sur la même feuille exactement quand elles sont sur le
même tour publié, 56 paires sur 56) et `R4-F552`. ⚠ Et un fait lu avant d'écrire, dans ce que `301` publie : les graines de PHerc0358 sont à
1985 voxels du niveau 0 au moins les unes des autres, et un plan en fait 650 ; aucune paire de chaînes existante ne peut se recouvrir.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P165`. Deux chaînes qui comptent leurs sauts sans se tromper se retrouvent sur la même
feuille toujours au même décalage. Sur PHerc0358, rouleau sans tracé, c'est une vérification qui ne demande que les chaînes.

## Ce qui est fait

- **Les chaînes suivies** : la chaîne d'une maille de `366` sur les cinq côtés de PHerc0358 que `331` suit.
- **La chaîne compagne** : pour chacun, une graine posée sur la nappe de départ à 15 mailles de son centre, soit 150 voxels, avec la
  normale de la nappe en ce point, et la même chaîne d'une maille partie d'elle, du même côté. Les deux nappes de départ sont donc sur la
  même feuille par construction, et le décalage attendu est nul.
- **Les paires** : une surface gardée de la chaîne suivie et une de la chaîne compagne qui se recouvrent, au moins 50 points en face à un
  pas et demi au plus, à la portée latérale de `354` ; **même feuille** si la médiane des écarts absolus est d'au plus un quart de pas,
  comme dans `367`.
- **Une paire tient les comptes** si « même feuille » et « même nombre de sauts depuis la nappe » disent la même chose.
- **La règle** : la part des paires qui tiennent les comptes. Au moins 90 %, **oui, les deux chaînes comptent les mêmes tours** ; moins de
  75 %, **non** ; sinon, **en partie**. Indécidable sous 10 paires, ou sans paire « même feuille ».

## Les issues

L'issue de la tranche : **sur n paires de surfaces qui se recouvrent, a tiennent les comptes**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La table des quatre cas ; les décalages des paires « même feuille » ; la distance réelle des deux graines.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si les deux chaînes sont sur la bonne feuille ; deux chaînes voisines qui glissent ensemble tiennent
leurs comptes et se trompent ensemble.

Usage :
    uv run python src/nappe/deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.py --verifier
    uv run python src/nappe/deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.py \\
        --json docs/mesures/deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

import la_nappe_de_m7_retrouve_t_elle_le_trace_humain_de_paris4 as m321  # noqa: E402
import une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin as m331  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358 as m354  # noqa: E402
import la_chaine_dune_maille_va_t_elle_plus_loin_sur_pherc0358 as m366  # noqa: E402
import deux_chaines_qui_se_croisent_disent_elles_le_tour as m367  # noqa: E402

LE_DECALAGE_EN_MAILLES = 15
LE_PAS = m354.LE_PAS
LE_QUART = LE_PAS / 4.0
LA_PORTEE = 1.5 * LE_PAS
LE_LATERAL = m354.LE_LATERAL_EN_PAS * LE_PAS
LE_MINIMUM_EN_FACE = m367.LE_MINIMUM_EN_FACE
LE_MINIMUM = 10
_LES_PAIRES_DE_CHAINES: list = []


LES_DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def la_graine_compagne(nappe: dict, decalage: int = LE_DECALAGE_EN_MAILLES,
                       directions: tuple = LES_DIRECTIONS) -> tuple[np.ndarray, np.ndarray] | None:
    """Le point de la nappe à `decalage` mailles de son centre, dans la première des directions où il est posé à normale connue, et sa
    normale ; None s'il n'y en a pas."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    nn, ok = les_normales(nappe["la_nappe"], nappe["valide"])
    c0, c1 = nappe["valide"].shape[0] // 2, nappe["valide"].shape[1] // 2
    for u0, u1 in directions:
        i, j = c0 + u0 * decalage, c1 + u1 * decalage
        if 0 <= i < ok.shape[0] and 0 <= j < ok.shape[1] and ok[i, j]:
            return nappe["la_nappe"][i, j], nn[i, j]
    return None


def les_surfaces(chaine: list[dict]) -> list[tuple[np.ndarray, np.ndarray]]:
    return [m367.les_points(k.get("la_relance")) for k in chaine]


def le_chaineur(croitre=None, enchainer=None):
    """Le chaîneur à passer à `331` : la chaîne d'une maille de `366` depuis la nappe, et la même depuis la graine compagne ; les surfaces
    des deux sont gardées en mémoire, dans l'ordre des côtés, et la chaîne suivie est rendue à `331`."""
    enchainer = enchainer or m366.la_chaine_dune_maille_de_0358

    def chainer(nappe, relancer, sauter, lire_valeurs):
        suivie = enchainer(nappe, relancer, sauter, lire_valeurs)
        g = la_graine_compagne(nappe)
        compagne = []
        if g is not None:
            grandir = croitre or (lambda p_, n_: m305.la_nappe_croissante(tuple(p_), tuple(n_), lire_valeurs))
            compagne = enchainer(grandir(*g), relancer, sauter, lire_valeurs)
        _LES_PAIRES_DE_CHAINES.append({"la_graine_compagne": None if g is None else [round(float(x), 2) for x in g[0]],
                                       "suivie": les_surfaces(suivie), "compagne": les_surfaces(compagne)})
        return suivie
    return chainer


def les_paires(suivie: list, compagne: list, comparer=None) -> list[dict]:
    comparer = comparer or (lambda a, b: m367.la_comparaison(a, b, lateral=LE_LATERAL))
    out = []
    for h, a in enumerate(suivie, 1):
        for k, b in enumerate(compagne, 1):
            if not len(a[0]) or not len(b[0]):
                continue
            c = comparer(a, b)
            if c["en_face"] < LE_MINIMUM_EN_FACE:
                continue
            meme = c["lecart_median"] <= LE_QUART
            out.append({"le_saut_suivi": h, "le_saut_compagnon": k, **c, "meme_feuille": bool(meme), "meme_saut": h == k,
                        "tient_les_comptes": bool(meme == (h == k))})
    return out


def le_bilan(paires: list[dict]) -> dict:
    t = {f"{'meme' if ms else 'autre'}_saut_{'meme' if mf else 'autre'}_feuille": sum(p["meme_saut"] == ms and p["meme_feuille"] == mf
                                                                                    for p in paires) for ms in (True, False) for mf in (True, False)}
    return {"les_paires": len(paires), "tiennent": sum(p["tient_les_comptes"] for p in paires), "la_table": t,
            "meme_feuille": sum(p["meme_feuille"] for p in paires),
            "les_decalages": dict(sorted(Counter(str(p["le_saut_compagnon"] - p["le_saut_suivi"]) for p in paires if p["meme_feuille"]).items()))}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    b = d["le_bilan"]
    if b["les_paires"] < LE_MINIMUM or not b["meme_feuille"]:
        return {"decidable": False, "lissue": f"indécidable : {b['les_paires']} paires, dont {b['meme_feuille']} sur la même feuille"}
    tete = f"sur {b['les_paires']} paires de surfaces qui se recouvrent, {b['tiennent']} tiennent les comptes"
    p = b["tiennent"] / b["les_paires"]
    suite = "oui, les deux chaînes comptent les mêmes tours" if p >= 0.9 else "non" if p < 0.75 else "en partie"
    return {"decidable": True, "p": round(p, 4), "lissue": f"{tete} ; {suite}"}


def mesurer() -> dict:
    t0 = time.monotonic()
    _LES_PAIRES_DE_CHAINES.clear()
    chaines, lv0, stats0 = m331.les_chaines_de_0358(chainer=le_chaineur())
    cotes, toutes = [], []
    for c, pc in zip(chaines, _LES_PAIRES_DE_CHAINES):
        p = les_paires(pc["suivie"], pc["compagne"])
        toutes += p
        cotes.append({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "la_graine_compagne": pc["la_graine_compagne"],
                      "les_sauts_suivis": len(pc["suivie"]), "les_sauts_compagnons": len(pc["compagne"]), "les_paires": p})
        print(json.dumps({"le_rang": c["le_rang"], "le_cote": c["le_cote"], "paires": len(p)}, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"le_decalage_en_mailles": LE_DECALAGE_EN_MAILLES, "le_quart": LE_QUART, "la_portee": LA_PORTEE,
                            "le_lateral": round(LE_LATERAL, 3), "le_minimum": LE_MINIMUM},
         "les_pannes": list(stats0["pannes"]), "la_lecture_de_m7": {k: v for k, v in stats0.items() if k != "pannes"},
         "les_cotes": cotes, "le_bilan": le_bilan(toutes)}
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

    n = 65
    g = np.zeros((n, n, 3))
    g[..., 0], g[..., 1] = np.meshgrid(np.arange(n) * 10.0, np.arange(n) * 10.0)
    nappe = {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    p, nn = la_graine_compagne(nappe)
    v("★★★★ la graine compagne : sur la nappe, à 15 mailles du centre, avec sa normale", np.allclose(p, g[32, 47])
      and np.allclose(np.abs(nn), [0, 0, 1]), str((p, nn)))
    trou = {"la_nappe": g, "valide": np.ones((n, n), dtype=bool)}
    trou["valide"][32, 47] = False
    p2, _ = la_graine_compagne(trou)
    v("★★★ si la maille est vide, la direction suivante", np.allclose(p2, g[47, 32]), str(p2))
    v("★★★ sans maille posée, pas de compagne", la_graine_compagne({"la_nappe": g, "valide": np.zeros((n, n), dtype=bool)}) is None)
    appels = []

    def enchainer(nap, rel, sau, lv):
        appels.append(("nappe" if nap is nappe else nap, lv))
        return [{"la_relance": nappe}]
    _LES_PAIRES_DE_CHAINES.clear()
    r = le_chaineur(croitre=lambda p_, n_: ("compagne", tuple(np.round(p_, 1))), enchainer=enchainer)(nappe, "rel", "sau", "m7")
    v("★★★★ le chaîneur : la chaîne suivie depuis la nappe, rendue à 331 ; la compagne depuis la graine compagne, même lecteur",
      r == [{"la_relance": nappe}] and appels[0] == ("nappe", "m7") and appels[1] == (("compagne", (470.0, 320.0, 0.0)), "m7")
      and len(_LES_PAIRES_DE_CHAINES) == 1 and len(_LES_PAIRES_DE_CHAINES[0]["suivie"]) == 1, str(appels))
    faux = {(1, 1): {"en_face": 60, "lecart_median": 0.3}, (1, 2): {"en_face": 60, "lecart_median": 19.0},
            (2, 2): {"en_face": 60, "lecart_median": 0.4}, (2, 1): {"en_face": 60, "lecart_median": 20.0},
            (3, 2): {"en_face": 60, "lecart_median": 0.5}, (3, 3): {"en_face": 30, "lecart_median": 0.2}}
    a = [(np.zeros((1, 3)), None, h) for h in (1, 2, 3)]
    b = [(np.zeros((1, 3)), None, k) for k in (1, 2, 3)]
    ps = les_paires(a, b, comparer=lambda x, y: faux.get((x[2], y[2]), {"en_face": 0, "lecart_median": None}))
    v("★★★★ les paires : 50 points en face ; même feuille au quart de pas ; tenir les comptes, c'est même feuille au même saut",
      [(q["le_saut_suivi"], q["le_saut_compagnon"], q["meme_feuille"], q["tient_les_comptes"]) for q in ps]
      == [(1, 1, True, True), (1, 2, False, True), (2, 1, False, True), (2, 2, True, True), (3, 2, True, False)], str(ps))
    b_ = le_bilan(ps)
    v("★★★★ le bilan : les paires qui tiennent, la table, les décalages des paires sur la même feuille",
      b_["tiennent"] == 4 and b_["meme_feuille"] == 3 and b_["les_decalages"] == {"-1": 1, "0": 2}
      and b_["la_table"] == {"meme_saut_meme_feuille": 2, "meme_saut_autre_feuille": 0, "autre_saut_meme_feuille": 1,
                             "autre_saut_autre_feuille": 2}, str(b_))
    v("★★★ le quart de pas de PHerc0358, cinq voxels", LE_QUART == 5.0 and LA_PORTEE == 30.0)
    vus, avant = [], m367.la_comparaison
    m367.la_comparaison = lambda x, y, lateral=None: vus.append(lateral) or {"en_face": 0, "lecart_median": None}
    try:
        les_paires([(np.zeros((1, 3)), None)], [(np.zeros((1, 3)), None)])
    finally:
        m367.la_comparaison = avant
    v("★★★★ sans comparaison donnée, celle de 367 à la portée latérale de 354 sur PHerc0358", vus == [LE_LATERAL], str(vus))

    def d_(tiennent, n_=40, meme=10):
        return {"les_pannes": [], "le_bilan": {"les_paires": n_, "tiennent": tiennent, "meme_feuille": meme}}
    v("★★★★ la règle : 90 %, oui ; sous 75 %, non ; entre les deux, en partie",
      le_verdict(d_(36))["lissue"].endswith("les mêmes tours") and le_verdict(d_(29))["lissue"].endswith("; non")
      and le_verdict(d_(30))["lissue"].endswith("en partie"))
    v("★★★ sous 10 paires, ou sans paire sur la même feuille : indécidable",
      not le_verdict(d_(9, n_=9))["decidable"] and not le_verdict(d_(40, meme=0))["decidable"] and le_verdict(d_(10, n_=10))["decidable"])

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
