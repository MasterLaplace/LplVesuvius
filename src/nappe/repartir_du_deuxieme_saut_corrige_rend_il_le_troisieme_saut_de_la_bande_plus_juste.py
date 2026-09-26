"""Repartie du deuxième saut corrigé de la bande `w028-037`, la chaîne rend-elle le troisième saut plus juste ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA CHAÎNE NE REPARTE DU DEUXIÈME SAUT CORRIGÉ. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `283` publient. `283` corrige le deuxième saut de la bande : 69 points déplacés, 23 ratés rendus justes pour 9
justes rendus ratés. `279` a montré sur le segment `20230702185753` qu'une correction doit finir sur une feuille avant que la
chaîne en reparte : le saut suivant ne reconnaît la feuille d'où il part que si elle est à moins de 12 voxels.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Corriger un saut ne sert la chaîne que si le saut suivant en profite. La bande
est le seul juge de ce dépôt qui note au troisième saut : sa troisième couche note 0,5243 des points de la tranche.

## Ce qui est fait, déclaré avant la mesure

- Le deuxième saut corrigé de `283` est recalé comme `279` recale : chaque point que la correction a déplacé va sur le centre de
  plage de `m7` le plus proche, sur le rayon de la bande (sa normale, jusqu'à trois pas), s'il en est à moins d'un
  demi-feuillet ; sinon il garde sa profondeur corrigée. Les autres points ne changent pas.
- La position d'un point déplacé bouge le long de la normale de la bande, de ce que sa profondeur a bougé.
- Les normales de la surface d'où la chaîne repart sont recalculées comme `248` les recalcule après un saut, orientées par
  celles du premier saut. La chaîne de `248` fait alors deux sauts de plus : le troisième et le quatrième.
- Le témoin est la même reprise, partie du deuxième saut non corrigé.

⚠ Les contrôles rendent la mesure décidable : partie du deuxième saut non corrigé, la reprise redonne les normales du deuxième
saut de `248` et ses troisième et quatrième sauts, compte pour compte ; le deuxième saut corrigé chargé déplace les 69 points de
`283` ; la lecture ne connaît aucune panne.

## Les issues, exclusives, au troisième saut

- les ratés que la chaîne repartie rend justes, là où le témoin les ratait, sont plus nombreux que les justes qu'elle rend
  ratés : repartir du deuxième saut corrigé rend le troisième saut de la bande plus juste ;
- ils ne le sont pas : il ne le rend pas plus juste.

⚠ Rapporté à côté : le quatrième saut ; le deuxième saut recalé contre le deuxième saut corrigé ; combien de points le
recalage déplace, et à quelle distance de la feuille la correction les posait.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une correction du troisième saut ; un autre côté, une autre prédiction.

Usage :
    uv run python src/nappe/repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste.py --verifier
    uv run python src/nappe/repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste.py \\
        --json docs/mesures/repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste.json
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
from le_transfert_enchaine_tient_il_les_spires import (LES_SAUTS, enchainer, juger_le_saut,  # noqa: E402
                                                       les_normales_de_la_grille)
from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE, les_centres  # noqa: E402
from recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste import (  # noqa: E402
    la_distance_a_la_feuille, la_feuille_la_plus_proche, recaler)
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import le_bilan_du_saut  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_283_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.json"
LE_DEUXIEME_SAUT_RECALE = LE_CACHE / LE_DEUXIEME_SAUT_CORRIGE.name.replace("_corrige_265_", "_corrige_recale_265_")


def deplacer_le_long_de_la_normale(q: np.ndarray, n: np.ndarray, tau: np.ndarray, tau_neuf: np.ndarray) -> np.ndarray:
    """La position d'un point bouge le long de la normale de la bande, de ce que sa profondeur a bougé ; NaN ne bouge pas."""
    d = np.where(np.isfinite(tau_neuf) & np.isfinite(tau), tau_neuf - tau, 0.0)
    return q + d[:, None] * n


def les_normales_de_la_reprise(q: np.ndarray, parent: np.ndarray, sur_la_grille, gi, gj) -> np.ndarray:
    """Les normales de la surface d'où la chaîne repart, comme `enchainer` les recalcule après un saut."""
    grille_q = np.stack([sur_la_grille(q[:, a]) for a in range(3)], axis=-1)
    grille_n = np.stack([sur_la_grille(parent[:, a]) for a in range(3)], axis=-1)
    return les_normales_de_la_grille(grille_q, grille_n)[0][gi, gj]


def la_reprise(q: np.ndarray, parent: np.ndarray, b: dict, sauts: int) -> list[dict]:
    """La chaîne de `248`, repartie d'une surface donnée point par point, pour `sauts` sauts de plus."""
    nq = les_normales_de_la_reprise(q, parent, b["sur_la_grille"], b["gi"], b["gj"])
    return enchainer(q, nq, LE_SIGNE, sauts, b["lire_rayon"], b["sur_la_grille"], b["gi"], b["gj"], True)


def la_reproduction_des_sauts(taus: list[np.ndarray], verite: list[np.ndarray], publie: list[dict], premier: int) -> dict:
    """Les sauts `premier`, `premier + 1`… refaits, contre ceux que `248` publie : points notés et jugement de la chaîne."""
    lignes = []
    for k, tau in enumerate(taus):
        h = premier + k
        j = juger_le_saut(tau, verite[h - 1], LE_SIGNE, h)
        refait = {"les_points_notes": j["les_points_notes"], "la_chaine": j.get("le_transfert")}
        pub = {"les_points_notes": publie[h - 1]["les_points_notes"], "la_chaine": publie[h - 1]["la_chaine"]}
        lignes.append({"le_saut": h, "publie": pub, "refait": refait, "reproduit": refait == pub})
    return {"les_sauts": lignes, "tous": bool(lignes) and all(x["reproduit"] for x in lignes)}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la reprise du deuxième saut non corrigé ne redonne pas 248, le deuxième saut corrigé "
                          "n'est pas celui de 283, ou la lecture est tombée en panne"}
    if r["les_sauts"][0]["le_gain_net"] > 0:
        return {"lissue": "repartir du deuxième saut corrigé rend le troisième saut de la bande plus juste"}
    return {"lissue": "repartir du deuxième saut corrigé ne rend pas le troisième saut de la bande plus juste"}


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
    q2, tau2 = chaine[1]["q"], taus[1]
    tau2c = np.load(LE_DEUXIEME_SAUT_CORRIGE)[gi, gj]
    with np.errstate(invalid="ignore"):
        deplace = ~(np.abs(tau2c - tau2) < 1e-9) & np.isfinite(tau2)
    t, vu = b["lire_rayon"](p, n, LE_SIGNE, LA_PORTEE)
    proche = la_feuille_la_plus_proche(les_centres(t, vu), tau2c)
    tau2r = recaler(tau2c, deplace, proche)
    with np.errstate(invalid="ignore"):
        recale = deplace & ~(np.abs(tau2r - tau2c) < 1e-9)
    grille = b["sur_la_grille"]
    np.save(LE_DEUXIEME_SAUT_RECALE, grille(tau2r))
    q2r = deplacer_le_long_de_la_normale(q2, n, tau2, tau2r)
    temoin = la_reprise(q2, chaine[0]["n"], b, LES_SAUTS - 2)
    reprise = la_reprise(q2r, chaine[0]["n"], b, LES_SAUTS - 2)
    tt, tr = les_profondeurs_de(temoin, p, n), les_profondeurs_de(reprise, p, n)
    nq2 = les_normales_de_la_reprise(q2, chaine[0]["n"], grille, gi, gj)
    out = {"la_reproduction_de_248": la_reproduction_des_sauts(taus, v, publie, 1),
           "la_reprise_du_temoin": la_reproduction_des_sauts(tt, v, publie, 3),
           "les_normales_du_deuxieme_saut_redonnees": bool(np.array_equal(nq2, chaine[1]["n"], equal_nan=True)),
           "les_points_deplaces_par_283": int(deplace.sum()),
           "les_points_corriges_publies_par_283": d283["les_reunis"]["les_points_corriges"],
           "les_points_recales": int(recale.sum()),
           "la_distance_a_la_feuille_des_points_deplaces": la_distance_a_la_feuille(tau2c, proche, deplace),
           "le_deuxieme_saut": {"corrige_contre_temoin": le_bilan_du_saut(tau2, tau2c, v[1]),
                                "recale_contre_temoin": le_bilan_du_saut(tau2, tau2r, v[1]),
                                "recale_contre_corrige": le_bilan_du_saut(tau2c, tau2r, v[1])},
           "les_sauts": [dict(le_bilan_du_saut(tt[k], tr[k], v[k + 2]), le_saut=k + 3) for k in range(len(tt))],
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])},
           "le_deuxieme_saut_recale": LE_DEUXIEME_SAUT_RECALE.name}
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

    q = np.array([[0.0, 0.0, 144.0], [5.0, 5.0, 150.0], [1.0, 1.0, 1.0]])
    n = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    tau = np.array([144.0, 150.0, np.nan])
    neuf = np.array([120.0, 150.0, 30.0])
    qq = deplacer_le_long_de_la_normale(q, n, tau, neuf)
    v("★★★★ un point déplacé bouge le long de la normale de la bande, de ce que sa profondeur a bougé",
      np.allclose(qq[0], [0.0, 0.0, 120.0]) and np.allclose(qq[1], q[1]), str(qq[:2]))
    v("★★★ une profondeur absente ne déplace rien", np.allclose(qq[2], q[2]))

    # Une surface plane sur une grille 3 × 3 : ses normales recalculées sont celles de la grille, orientées du × dv.
    gi, gj = np.divmod(np.arange(9), 3)
    grille = lambda val: np.asarray(val, dtype=float).reshape(3, 3)  # noqa: E731
    plan = np.stack([gj * 8.0, gi * 8.0, np.full(9, 5.0)], axis=-1)
    nn = les_normales_de_la_reprise(plan, np.tile([0.0, 0.0, -1.0], (9, 1)), grille, gi, gj)
    v("★★★ les normales de la reprise sont celles que la chaîne calcule après un saut",
      np.allclose(np.abs(nn[:, 2]), 1.0) and np.allclose(nn[:, :2], 0.0), str(nn[0]))

    pub = [{"les_points_notes": 2, "la_chaine": None}, {"les_points_notes": 2, "la_chaine": None},
           {"les_points_notes": 3, "la_chaine": juger_le_saut(np.array([216.0, 216.0, 150.0]),
                                                               np.array([210.0, 250.0, 216.0]), LE_SIGNE, 3)["le_transfert"]}]
    v("★★★★ la reprise redonne 248 si ses sauts, pris à leur rang, égalent les publiés",
      lambda: la_reproduction_des_sauts([np.array([216.0, 216.0, 150.0])], [None, None, np.array([210.0, 250.0, 216.0])],
                                        pub, 3)["tous"])
    v("★★★★ un saut jugé au mauvais rang ne se reproduit pas",
      lambda: not la_reproduction_des_sauts([np.array([216.0, 216.0, 150.0])],
                                            [None, np.array([210.0, 250.0, 216.0]), None], pub, 2)["tous"])

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
