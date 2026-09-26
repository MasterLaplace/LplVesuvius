"""Recalé sur le rayon d'où il part, le deuxième saut corrigé de la bande rend-il le troisième saut plus juste ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CE RECALAGE. Ce qui était vu avant d'écrire : tout ce que `248` et `257` à `284` publient. `284`
recale le deuxième saut corrigé de `283` comme `279` recale le premier : sur les feuilles que `m7` voit le long du rayon de la
bande, sa normale partie d'elle. Il n'en recale que 18 sur 69, et trouve les points corrigés à une médiane de 59,5061 voxels de
la feuille la plus proche, 13 sans aucune feuille sur ce rayon. La chaîne qui en repart rend le troisième saut moins juste.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Le rayon de la bande est celui du premier saut. Le deuxième saut, lui, part du
premier : la chaîne le lit le long de la normale du premier saut, depuis le premier saut, et c'est sur ce rayon qu'elle pose ses
points sur une feuille. Recaler le deuxième saut sur le rayon de la bande, c'est chercher ses feuilles là où la chaîne ne les
a pas cherchées. Une correction doit finir sur une feuille (`279`), et c'est sur le rayon du saut qu'elle se trouve.

## Ce qui est fait, déclaré avant la mesure

- Le rayon du deuxième saut part de chaque point du premier saut, le long de sa normale, jusqu'à trois pas : c'est celui que
  la chaîne de `248` lit pour le deuxième saut.
- Chaque point que la correction de `283` a déplacé est projeté sur ce rayon. Il va sur le centre de plage de `m7` le plus proche
  de cette projection, s'il en est à moins d'un demi-feuillet, et se pose alors sur le rayon, comme la chaîne pose ses points ;
  sinon il garde sa position corrigée. C'est la règle du vote de `247`, une fois. Les autres points ne changent pas.
- La chaîne repart de là pour le troisième et le quatrième saut, comme dans `284`, et le témoin repart du deuxième saut non
  corrigé.

⚠ Les contrôles rendent la mesure décidable : la chaîne redonne `248` aux quatre sauts ; partie du deuxième saut non corrigé,
la reprise redonne ses normales et ses troisième et quatrième sauts ; le deuxième saut corrigé chargé déplace les 69 points de
`283` ; la lecture ne connaît aucune panne.

## Les issues, exclusives, au troisième saut

- les ratés que la chaîne repartie rend justes, là où le témoin les ratait, sont plus nombreux que les justes qu'elle rend
  ratés : recalé sur son rayon, le deuxième saut corrigé rend le troisième saut plus juste ;
- ils ne le sont pas : il ne le rend pas plus juste.

⚠ Rapporté à côté : à quelle distance de la feuille la plus proche, sur ce rayon, le deuxième saut non corrigé pose ses points,
et la correction les siens ; combien de points le recalage déplace ; le deuxième saut recalé contre le témoin et contre le
corrigé ; le quatrième saut.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une correction du troisième saut ; un autre côté, une autre prédiction.

Usage :
    uv run python src/nappe/recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.py --verifier
    uv run python src/nappe/recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.py \\
        --json docs/mesures/recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json
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

from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande import (  # noqa: E402
    LE_DEUXIEME_SAUT_CORRIGE, les_profondeurs_de)
from la_procedure_sans_juge_tient_elle_sur_la_bande import (CE_QUE_248_A_PUBLIE, LE_CACHE, LE_SIGNE,  # noqa: E402
                                                            la_bande)
from la_spire_produite_se_lit_elle_dans_le_treillis import LA_PREDICTION, LE_COTE  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import LES_SAUTS, enchainer  # noqa: E402
from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE, les_centres  # noqa: E402
from recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste import (  # noqa: E402
    la_distance_a_la_feuille, la_feuille_la_plus_proche, recaler)
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import le_bilan_du_saut  # noqa: E402
from repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste import (  # noqa: E402
    CE_QUE_283_A_PUBLIE, deplacer_le_long_de_la_normale, la_reprise, la_reproduction_des_sauts,
    les_normales_de_la_reprise)

LE_DEUXIEME_SAUT_RECALE_SUR_SON_RAYON = LE_CACHE / LE_DEUXIEME_SAUT_CORRIGE.name.replace(
    "_corrige_265_", "_corrige_recale_sur_son_rayon_265_")


def la_projection_sur_le_rayon(q: np.ndarray, origine: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Où tombe chaque point le long du rayon parti de `origine` selon `direction`, une normale unitaire."""
    return np.einsum("ij,ij->i", q - origine, direction)


def poser_sur_le_rayon(q: np.ndarray, origine: np.ndarray, direction: np.ndarray, s: np.ndarray,
                       quels: np.ndarray) -> np.ndarray:
    """Les points choisis se posent sur le rayon, à la profondeur `s` ; les autres gardent leur position."""
    return np.where(quels[:, None], origine + s[:, None] * direction, q)


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la reprise du deuxième saut non corrigé ne redonne pas 248, le deuxième saut corrigé "
                          "n'est pas celui de 283, ou la lecture est tombée en panne"}
    if r["les_sauts"][0]["le_gain_net"] > 0:
        return {"lissue": "recalé sur son rayon, le deuxième saut corrigé rend le troisième saut de la bande plus juste"}
    return {"lissue": "recalé sur son rayon, le deuxième saut corrigé ne rend pas le troisième saut de la bande plus juste"}


def mesurer() -> dict:
    debut = time.monotonic()
    b = la_bande()
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b, "le_verdict": le_verdict({})}
    p, n, gi, gj, v = b["p"], b["n"], b["gi"], b["gj"], b["verite"]
    chaine = enchainer(p, n, LE_SIGNE, LES_SAUTS, b["lire_rayon"], b["sur_la_grille"], gi, gj, True)
    taus = les_profondeurs_de(chaine, p, n)
    publie = json.loads(CE_QUE_248_A_PUBLIE.read_text())["les_predictions"][LA_PREDICTION][LE_COTE]["les_sauts"]
    d283 = json.loads(CE_QUE_283_A_PUBLIE.read_text())
    q1, n1, q2, tau2 = chaine[0]["q"], chaine[0]["n"], chaine[1]["q"], taus[1]
    tau2c = np.load(LE_DEUXIEME_SAUT_CORRIGE)[gi, gj]
    with np.errstate(invalid="ignore"):
        deplace = ~(np.abs(tau2c - tau2) < 1e-9) & np.isfinite(tau2)
    q2c = deplacer_le_long_de_la_normale(q2, n, tau2, tau2c)
    t, vu = b["lire_rayon"](q1, n1, LE_SIGNE, LA_PORTEE)
    centres = les_centres(t, vu)
    s2, s2c = la_projection_sur_le_rayon(q2, q1, n1), la_projection_sur_le_rayon(q2c, q1, n1)
    proche = la_feuille_la_plus_proche(centres, s2c)
    s2r = recaler(s2c, deplace, proche)
    with np.errstate(invalid="ignore"):
        recale = deplace & ~(np.abs(s2r - s2c) < 1e-9)
    q2r = poser_sur_le_rayon(q2c, q1, n1, s2r, recale)
    tau2r = les_profondeurs_de([{"q": q2r}], p, n)[0]
    grille = b["sur_la_grille"]
    np.save(LE_DEUXIEME_SAUT_RECALE_SUR_SON_RAYON, grille(tau2r))
    temoin = la_reprise(q2, chaine[0]["n"], b, LES_SAUTS - 2)
    reprise = la_reprise(q2r, chaine[0]["n"], b, LES_SAUTS - 2)
    tt, tr = les_profondeurs_de(temoin, p, n), les_profondeurs_de(reprise, p, n)
    nq2 = les_normales_de_la_reprise(q2, chaine[0]["n"], grille, gi, gj)
    tous = np.isfinite(s2)
    out = {"la_reproduction_de_248": la_reproduction_des_sauts(taus, v, publie, 1),
           "la_reprise_du_temoin": la_reproduction_des_sauts(tt, v, publie, 3),
           "les_normales_du_deuxieme_saut_redonnees": bool(np.array_equal(nq2, chaine[1]["n"], equal_nan=True)),
           "les_points_deplaces_par_283": int(deplace.sum()),
           "les_points_corriges_publies_par_283": d283["les_reunis"]["les_points_corriges"],
           "les_points_recales": int(recale.sum()),
           "la_distance_a_la_feuille_sur_le_rayon_du_saut": {
               "le_deuxieme_saut_non_corrige_partout": la_distance_a_la_feuille(
                   s2, la_feuille_la_plus_proche(centres, s2), tous),
               "le_deuxieme_saut_non_corrige_aux_points_deplaces": la_distance_a_la_feuille(
                   s2, la_feuille_la_plus_proche(centres, s2), deplace),
               "le_deuxieme_saut_corrige_aux_points_deplaces": la_distance_a_la_feuille(s2c, proche, deplace)},
           "le_deuxieme_saut": {"corrige_contre_temoin": le_bilan_du_saut(tau2, tau2c, v[1]),
                                "recale_contre_temoin": le_bilan_du_saut(tau2, tau2r, v[1]),
                                "recale_contre_corrige": le_bilan_du_saut(tau2c, tau2r, v[1])},
           "les_sauts": [dict(le_bilan_du_saut(tt[k], tr[k], v[k + 2]), le_saut=k + 3) for k in range(len(tt))],
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])},
           "le_deuxieme_saut_recale_sur_son_rayon": LE_DEUXIEME_SAUT_RECALE_SUR_SON_RAYON.name}
    out["decidable"] = (out["la_reproduction_de_248"]["tous"] and out["la_reprise_du_temoin"]["tous"]
                        and out["les_normales_du_deuxieme_saut_redonnees"]
                        and out["les_points_deplaces_par_283"] == out["les_points_corriges_publies_par_283"]
                        and not out["la_lecture"]["combien_de_pannes"])
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

    o = np.array([[0.0, 0.0, 72.0], [10.0, 0.0, 72.0]])
    d = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    q = np.array([[3.0, 4.0, 150.0], [10.0, 80.0, 70.0]])
    s = la_projection_sur_le_rayon(q, o, d)
    v("★★★★ un point se projette sur le rayon de son saut, depuis le point d'où il part, le long de sa normale",
      np.allclose(s, [78.0, 80.0]), str(s))
    pose = poser_sur_le_rayon(q, o, d, np.array([72.0, 60.0]), np.array([True, False]))
    v("★★★★ un point recalé se pose sur le rayon, à la profondeur de sa feuille, et les autres ne bougent pas",
      np.allclose(pose[0], [0.0, 0.0, 144.0]) and np.allclose(pose[1], q[1]), str(pose))

    # Le recalage de 279 appliqué sur le rayon : la feuille la plus proche de la projection, à moins d'un demi-feuillet.
    centres = [np.array([72.0, 144.0]), np.array([72.0, 144.0]), np.empty(0)]
    cible = np.array([130.0, 100.0, 80.0])
    r = recaler(cible, np.array([True, True, True]), la_feuille_la_plus_proche(centres, cible))
    v("★★★ la projection va sur la feuille la plus proche à moins d'un demi-feuillet, et reste sans feuille à portée",
      np.allclose(r, [144.0, 72.0, 80.0]), str(r))

    r_ = lambda g: {"decidable": True, "les_sauts": [{"le_gain_net": g}]}  # noqa: E731
    v("★★★★ les issues : plus juste si le gain net du troisième saut est positif, sinon non, indécidable sans contrôle",
      "ne rend pas" not in le_verdict(r_(1))["lissue"] and "ne rend pas" in le_verdict(r_(0))["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

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
    texte = json.dumps(r, ensure_ascii=False, indent=1)
    print(texte)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
