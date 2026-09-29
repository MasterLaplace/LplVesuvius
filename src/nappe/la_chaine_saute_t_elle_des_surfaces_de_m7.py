"""Entre chaque surface de la chaîne de 303 et sa spire suivante, combien de plages de m7 le rayon traverse-t-il ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PLAGE INTERMÉDIAIRE NE SOIT COMPTÉE. Ce qui était vu avant d'écrire : tout ce que
`303` à `312` publient, dont `R4-F493` : le long des rayons, les plages de `m7` se suivent tous les 10 à 17,5 voxels au plus, et la
chaîne de `303` avance de 18,5 à 22,5 voxels par saut.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P113`. Chaque saut de `303` part de la première plage de `m7` après la sienne, puis
le vote de `247` la déplace vers la médiane de ses voisins, à moins d'un demi-pas : un point peut ainsi finir sur la plage d'après.
Si la chaîne saute une surface de `m7` à chaque saut, ses « spires » sont une surface de `m7` sur deux.

## Ce qui est fait

- **La chaîne** : celle de `303`, retirée de `m7` à l'identique, cinq graines, dix côtés, quatre sauts.
- **Les rayons** : pour chaque point de la surface de départ d'un saut où le saut est appuyé sur `m7`, le long de la normale que le
  saut a suivie, de la surface jusqu'au pas qu'il a pris.
- **Les plages intermédiaires** : celles de `m7` dont le centre est à plus de 3 voxels de la surface de départ (la plage de sa propre
  feuille, comme `300`) et à plus de 3 voxels de la spire d'arrivée.
- **Par saut** : la part des rayons qui n'en traversent aucune, une, ou plus.

## Les issues

Un saut **passe à la surface suivante** si au moins la moitié de ses rayons ne traversent aucune plage intermédiaire, **en saute
une** si au moins la moitié en traversent exactement une, **mêlé** sinon. Par côté, le dernier saut h tel que les sauts 1 à h
passent tous à la surface suivante. **L'issue de la tranche** : sur k des dix côtés, la chaîne passe d'une surface de `m7` à la
suivante pendant ses quatre sauts.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que deux surfaces consécutives de `m7` soient deux spires consécutives du rouleau.

Usage :
    uv run python src/nappe/la_chaine_saute_t_elle_des_surfaces_de_m7.py --verifier
    uv run python src/nappe/la_chaine_saute_t_elle_des_surfaces_de_m7.py --json docs/mesures/la_chaine_saute_t_elle_des_surfaces_de_m7.json
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

import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402
import la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut as m303  # noqa: E402

LA_MARGE = m300.LE_CONTROLE


def les_intermediaires(centres: list[np.ndarray], pas_: np.ndarray, marge: float = LA_MARGE) -> np.ndarray:
    """Pour chaque rayon, le nombre de plages dont le centre est à plus de `marge` du départ et de l'arrivée (au pas |pas_|)."""
    out = np.zeros(len(centres), dtype=int)
    for k, c in enumerate(centres):
        a = np.abs(c)
        out[k] = int(((a > marge) & (a < abs(pas_[k]) - marge)).sum())
    return out


def le_saut(n: np.ndarray) -> dict:
    if not len(n):
        return {"les_rayons": 0, "aucune": None, "une": None, "plus": None, "le_saut": "non lu"}
    p0, p1, p2 = (round(float(x), 4) for x in ((n == 0).mean(), (n == 1).mean(), (n >= 2).mean()))
    lec = "passe à la surface suivante" if p0 >= 0.5 else ("en saute une" if p1 >= 0.5 else "mêlé")
    return {"les_rayons": int(len(n)), "aucune": p0, "une": p1, "plus": p2, "le_saut": lec}


def le_dernier_qui_passe(sauts: list[dict]) -> int:
    h = 0
    for s in sauts:
        if s["le_saut"] != "passe à la surface suivante":
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    cotes = d["les_cotes"]
    if not cotes:
        return {"decidable": False, "lissue": "indécidable : aucun côté"}
    k = sum(1 for c in cotes if c["le_dernier_saut_qui_passe"] == m303.LES_SAUTS)
    return {"decidable": True, "k": k, "n": len(cotes),
            "lissue": f"sur {k} des {len(cotes)} côtés, la chaîne passe d'une surface de m7 à la suivante pendant ses "
                      f"{m303.LES_SAUTS} sauts"}


def mesurer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta
    import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298
    import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299

    t0 = time.monotonic()
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    r302, identiques = m302.retirer()
    cotes = []
    for rang, r in r302["les_nappes"].items():
        for nom, cote in m303.LES_COTES:
            surf, ok = r["la_nappe"], r["valide"]
            e = {"le_rang": rang, "le_cote": nom, "les_sauts": []}
            for h, s in enumerate(m303.enchainer(r["la_nappe"], r["valide"], cote, lv), 1):
                nn, nok = les_normales(surf, ok)
                m = (s["appui"] & s["valide"] & nok & np.isfinite(s["le_pas"])).ravel()
                q, nq, pas_ = surf.reshape(-1, 3)[m], nn.reshape(-1, 3)[m], s["le_pas"].ravel()[m]
                n = np.zeros(0, dtype=int)
                if len(q):
                    L = int(np.ceil(np.abs(pas_).max())) + 1
                    ts = cote * np.arange(0.0, float(L))
                    idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
                    vu = lv(idx) > 0
                    vu &= (np.abs(ts)[None, :] <= np.abs(pas_)[:, None] + LA_MARGE)
                    n = les_intermediaires(m300.les_plages(vu, ts), pas_)
                e["les_sauts"].append(dict(le_saut(n), le_numero=h))
                surf, ok = s["la_spire"], s["valide"]
            e["le_dernier_saut_qui_passe"] = le_dernier_qui_passe(e["les_sauts"])
            cotes.append(e)
            print(json.dumps(e, ensure_ascii=False), flush=True)
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {"la_marge_voxels": LA_MARGE},
         "les_nappes_se_redonnent": identiques, "les_pannes": list(stats["pannes"]) + list(r302["les_pannes"]),
         "les_cotes": cotes}
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

    c = [np.array([0.0, 20.0]), np.array([0.0, 11.0, 20.0]), np.array([1.0, 8.0, 14.0, 20.0]), np.array([0.0, 18.5])]
    n = les_intermediaires(c, np.array([20.0, 20.0, 20.0, 20.0]))
    v("★★★★ les plages intermédiaires : ni la sienne, ni celle d'arrivée", list(n) == [0, 1, 2, 0], str(n))
    v("★★★ du côté moins, les distances comptent en valeur absolue",
      list(les_intermediaires([np.array([0.0, -11.0, -20.0])], np.array([-20.0]))) == [1])
    s = le_saut(np.array([0, 0, 1, 0, 2]))
    v("★★★★ un saut qui passe à la surface suivante", s["le_saut"] == "passe à la surface suivante" and s["aucune"] == 0.6)
    v("★★★★ un saut qui en saute une", le_saut(np.array([1, 1, 1, 0]))["le_saut"] == "en saute une")
    v("★★★ un saut mêlé", le_saut(np.array([0, 1, 2, 2]))["le_saut"] == "mêlé"
      and le_saut(np.array([0, 0, 1, 2, 2, 2]))["le_saut"] == "mêlé")
    v("★★★ sans rayon, non lu", le_saut(np.zeros(0, dtype=int))["le_saut"] == "non lu")
    sauts = [{"le_saut": "passe à la surface suivante"}, {"le_saut": "en saute une"}, {"le_saut": "passe à la surface suivante"}]
    v("★★★ le dernier qui passe s'arrête au premier qui saute", le_dernier_qui_passe(sauts) == 1)
    vd = le_verdict({"les_cotes": [{"le_dernier_saut_qui_passe": 4}, {"le_dernier_saut_qui_passe": 3}]})
    v("★★★ l'issue : les côtés qui passent pendant les quatre sauts", vd["k"] == 1 and vd["lissue"].startswith("sur 1 des 2"))
    v("★★★ indécidable sans côté ou si une lecture échoue", not le_verdict({"les_cotes": []})["decidable"]
      and not le_verdict({"les_pannes": ["x"], "les_cotes": []})["decidable"])

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
