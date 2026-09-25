"""Recaler la spire corrigée sur la feuille rend-il le deuxième saut plus juste ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA SPIRE CORRIGÉE NE SOIT RECALÉE. Ce qui était vu avant d'écrire : tout ce que `247`,
`248` et `257` à `278` publient. `278` montre que, sous un juge intact, la spire corrigée ajoute au deuxième saut des ratés
propres d'un genre précis : 36 sauts retombent sur la première couche, contre 15 pour le témoin, et 16 n'avancent pas, contre 6.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. La correction de `265` pousse un point de l'écart que la marche lit
(`corriger_decide`), et cet écart n'est pas celui d'une feuille : le point corrigé tombe sur la bonne spire, pas sur la feuille.
Or le saut suivant (`247`) ne reconnaît la feuille d'où il part que si elle est à moins de 12 voxels (`LE_CONTROLE`) ; au-delà,
il la prend pour la suivante, et il retombe sur elle. Le transfert de `247` finit toujours par poser un point sur une feuille :
le vote prend la feuille la plus proche de sa cible, à moins d'un demi-feuillet. La correction ne le fait pas.

## Le recalage, déclaré avant la mesure

Pour chaque point que la correction a déplacé, parmi les centres des plages de feuille que la prédiction `m7` voit sur le rayon
du premier saut (la normale du segment, jusqu'à trois pas), prendre le plus proche de la spire corrigée s'il en est à moins d'un
demi-feuillet ; sinon, le point garde la spire corrigée. C'est la règle du vote de `247`, une fois, sans consensus : la cible est
la spire corrigée elle-même. Les points que la correction n'a pas déplacés ne changent pas.

La chaîne de `248` repart de la spire recalée, et elle est comparée à celle qui repart de la spire corrigée, sur les mêmes
points, par le juge de `248`.

⚠ Les chaînes du témoin et de la spire corrigée doivent redonner le deuxième saut de `276`, compte pour compte ; sinon la mesure
est indécidable. Elle l'est aussi si une lecture tombe en panne.

## Les issues, exclusives, au deuxième saut

- les ratés que la spire recalée rend justes, là où la spire corrigée les ratait, sont plus nombreux que les justes qu'elle rend
  ratés : recaler la spire corrigée sur la feuille rend le deuxième saut plus juste ;
- ils ne le sont pas : il ne le rend pas plus juste.

⚠ Rapporté à côté : à quelle distance de la feuille la plus proche la correction pose ses points, et la même distance pour les
points qu'elle n'a pas touchés ; le premier saut ; le rangement de `277` pour la spire recalée, sous le juge de `248` et sous le
juge intact de `253`.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : un recalage sur une feuille que la prédiction ne voit pas ; une correction du deuxième
saut ; un autre côté, une autre prédiction.

Usage :
    uv run python src/nappe/recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.py --verifier
    uv run python src/nappe/recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.py \\
        --json docs/mesures/recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.json
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

from la_chaine_rejugee_hors_des_dechirures import les_notes_intactes  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import enchainer  # noqa: E402
from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE, LE_CONTROLE, les_centres  # noqa: E402
from les_rates_du_deuxieme_saut_viennent_ils_du_premier import les_origines  # noqa: E402
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                                                                LE_SIGNE, le_bilan_du_saut,
                                                                                les_deux_chaines, les_profondeurs)
from sous_un_juge_intact_le_deuxieme_saut_rate_t_il_encore_de_lui_meme import sous_le_juge  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_276_A_PUBLIE = LES_MESURES / "repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.json"


def la_feuille_la_plus_proche(centres: list[np.ndarray], cible: np.ndarray) -> np.ndarray:
    """Pour chaque point, le centre de feuille le plus proche de sa cible, NaN si le rayon n'en voit aucun."""
    out = np.full(len(cible), np.nan)
    for k, c in enumerate(centres):
        if len(c) and np.isfinite(cible[k]):
            out[k] = c[int(np.argmin(np.abs(c - cible[k])))]
    return out


def recaler(tau1: np.ndarray, deplace: np.ndarray, proche: np.ndarray) -> np.ndarray:
    """Les points déplacés par la correction vont sur la feuille la plus proche, si elle est à moins d'un demi-feuillet."""
    with np.errstate(invalid="ignore"):
        prend = deplace & np.isfinite(proche) & (np.abs(proche - tau1) < DEMI_PAS_EN_VOXELS)
    return np.where(prend, proche, tau1)


def la_distance_a_la_feuille(tau: np.ndarray, proche: np.ndarray, quels: np.ndarray) -> dict:
    """À quelle distance de la feuille la plus proche une spire pose les points choisis."""
    d = np.abs(tau - proche)[quels]
    vus = np.isfinite(d)
    r = {"les_points": int(quels.sum()), "sans_feuille_sur_le_rayon": int((~vus).sum())}
    if vus.any():
        r |= {"la_mediane_voxels": round(float(np.median(d[vus])), 4),
              "au_dela_de_la_reconnaissance": int((d[vus] > LE_CONTROLE).sum()),
              "au_dela_dun_demi_feuillet": int((d[vus] >= DEMI_PAS_EN_VOXELS).sum())}
    return r


def le_bilan_recale(tau_c: np.ndarray, tau_r: np.ndarray, verite: np.ndarray) -> dict:
    """Le bilan d'un saut de `276`, la spire corrigée à la place du témoin et la spire recalée à la place de la corrigée."""
    b = le_bilan_du_saut(tau_c, tau_r, verite)
    b["partie_de_la_spire_recalee"] = b.pop("partie_de_la_spire_corrigee")
    b["partie_de_la_spire_corrigee"] = b.pop("le_temoin")
    return b


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : les chaînes ne redonnent pas le deuxième saut de 276, ou une lecture est tombée "
                          "en panne"}
    if r["les_sauts"][1]["le_gain_net"] > 0:
        return {"lissue": "recaler la spire corrigée sur la feuille rend le deuxième saut plus juste"}
    return {"lissue": "recaler la spire corrigée sur la feuille ne rend pas le deuxième saut plus juste"}


def mesurer() -> dict:
    debut = time.monotonic()
    c = les_deux_chaines()
    if isinstance(c, str):
        return {"decidable": False, "la_raison": c, "le_verdict": le_verdict({})}
    p, n, v, tau0, tau1 = c["p"], c["n"], c["verite"], c["tau0"], c["tau1"]
    gi, gj, grille, lire_rayon = c["gi"], c["gj"], c["sur_la_grille"], c["lire_rayon"]
    t, vu = lire_rayon(p, n, LE_SIGNE, LA_PORTEE)
    centres = les_centres(t, vu)
    with np.errstate(invalid="ignore"):
        deplace = ~(np.abs(tau1 - tau0) < 1e-9)
    proche = la_feuille_la_plus_proche(centres, tau1)
    tau1r = recaler(tau1, deplace, proche)
    recalee = enchainer(p, n, LE_SIGNE, len(v), lire_rayon, grille, gi, gj, True, premier=tau1r)
    pr, pc, pt = les_profondeurs(recalee, p, n), c["pc"], c["pt"]
    publie = json.loads(CE_QUE_276_A_PUBLIE.read_text())["les_sauts"][1]
    refait = le_bilan_du_saut(pt[1], pc[1], v[1])
    intact = [les_notes_intactes(x, grille, gi, gj) for x in v[:2]]
    vi = [sous_le_juge(v[k], intact[k]) for k in range(2)]
    with np.errstate(invalid="ignore"):
        bouge = deplace & ~(np.abs(tau1r - tau1) < 1e-9)
    out = {"le_deuxieme_saut_de_276": {"publie": publie, "refait": refait, "reproduit": refait == publie},
           "les_points_deplaces_par_la_correction": int(deplace.sum()),
           "les_points_recales": int(bouge.sum()),
           "la_distance_a_la_feuille": {
               "la_spire_corrigee_aux_points_deplaces": la_distance_a_la_feuille(tau1, proche, deplace),
               "la_spire_produite_ailleurs": la_distance_a_la_feuille(tau0, la_feuille_la_plus_proche(centres, tau0),
                                                                      ~deplace)},
           "les_sauts": [le_bilan_recale(pc[h], pr[h], v[h]) for h in range(len(v))],
           "le_rangement": {
               "le_juge_de_248": {"partie_de_la_spire_corrigee": les_origines(pc[0], pc[1], v[0], v[1], c["corrigee"][1]["le_pas"]),
                                  "partie_de_la_spire_recalee": les_origines(pr[0], pr[1], v[0], v[1], recalee[1]["le_pas"])},
               "le_juge_intact": {"partie_de_la_spire_corrigee": les_origines(pc[0], pc[1], vi[0], vi[1],
                                                                              c["corrigee"][1]["le_pas"]),
                                  "partie_de_la_spire_recalee": les_origines(pr[0], pr[1], vi[0], vi[1],
                                                                             recalee[1]["le_pas"])}},
           "le_deuxieme_saut_sous_le_juge_intact": le_bilan_recale(pc[1], pr[1], vi[1]),
           "la_lecture": {"combien_de_pannes": len(c["stats"]["pannes"])}}
    out["decidable"] = out["le_deuxieme_saut_de_276"]["reproduit"] and not out["la_lecture"]["combien_de_pannes"]
    out["le_verdict"] = le_verdict(out)
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


# ── LA BATTERIE ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    centres = [np.array([2.0, 71.0, 140.0]), np.array([2.0, 71.0]), np.empty(0), np.array([2.0, 140.0]),
               np.array([2.0, 71.0])]
    tau1 = np.array([90.0, 60.0, 70.0, 90.0, 71.0])
    deplace = np.array([True, True, True, True, False])
    proche = la_feuille_la_plus_proche(centres, tau1)
    v("★★★ la feuille la plus proche de la cible, NaN là où le rayon n'en voit aucune",
      np.allclose(proche[[0, 1, 3, 4]], [71.0, 71.0, 140.0, 71.0]) and np.isnan(proche[2]), str(proche))
    r = recaler(tau1, deplace, proche)
    v("★★★★ un point déplacé va sur la feuille la plus proche à moins d'un demi-feuillet, et garde sa place sinon",
      np.allclose(r, [71.0, 71.0, 70.0, 90.0, 71.0]), str(r))
    r2 = recaler(np.array([90.0]), np.array([False]), np.array([71.0]))
    v("★★★★ un point que la correction n'a pas déplacé ne bouge pas", r2[0] == 90.0)
    dist = la_distance_a_la_feuille(tau1, proche, deplace)
    v("★★★ la distance à la feuille compte les points sans feuille, et ceux au-delà de la reconnaissance",
      dist == {"les_points": 4, "sans_feuille_sur_le_rayon": 1, "la_mediane_voxels": 19.0,
               "au_dela_de_la_reconnaissance": 2, "au_dela_dun_demi_feuillet": 1}, str(dist))
    br = le_bilan_recale(np.array([140.0, 210.0, 210.0]), np.array([210.0, 140.0, 140.0]), np.full(3, 140.0))
    v("★★★ le bilan nomme la spire corrigée et la spire recalée, chacune à sa place",
      br["partie_de_la_spire_corrigee"] == 0.3333 and br["partie_de_la_spire_recalee"] == 0.6667
      and br["les_rates_rendus_justes"] == 2 and br["les_justes_rendus_rates"] == 1 and "le_temoin" not in br, str(br))
    s_ = lambda g: {"decidable": True, "les_sauts": [{"le_gain_net": 99}, {"le_gain_net": g}]}  # noqa: E731
    v("★★★★ les issues se lisent au deuxième saut : plus juste si le gain net y est positif, sinon non",
      "rend le deuxième saut plus juste" in le_verdict(s_(1))["lissue"]
      and "ne rend pas" in le_verdict(s_(0))["lissue"] and "indécidable" in le_verdict({})["lissue"])

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
    r = mesurer()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
