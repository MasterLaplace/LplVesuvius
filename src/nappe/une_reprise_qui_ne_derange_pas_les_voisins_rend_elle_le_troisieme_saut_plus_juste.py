"""Une reprise qui ne dérange pas les voisins des points corrigés rend-elle le troisième saut de la bande plus juste ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CETTE REPRISE. Ce qui était vu avant d'écrire : tout ce que `248` et `257` à `287` publient.
Repartie du deuxième saut corrigé de la bande, recalé sur son rayon, la chaîne perd le troisième saut, et surtout autour des
points corrigés (`286`). Avec les normales du témoin, elle en perd moins : 7 justes autour d'eux au lieu de 10, un gain net de
−5 au lieu de −8 (`287`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Avec les normales du témoin, un voisin d'un point corrigé lit le même rayon
que le témoin, depuis la même position : il ne peut plus changer que par le vote, qui vise la médiane d'un carré de trois
mailles, tour après tour. Un point corrigé n'a pas à entraîner ses voisins : sa correction vaut pour lui. Cette reprise garde
les normales du témoin, et les points corrigés ne votent plus pour leurs voisins.

## Ce qui est fait, déclaré avant la mesure

- Le deuxième saut recalé est celui de `285`, refait à l'identique, et la chaîne en repart avec les normales du témoin, comme
  dans `287`.
- Au troisième et au quatrième saut, les points que la correction a déplacés n'entrent plus dans la médiane du vote de leurs
  voisins. Eux-mêmes votent comme avant, sur la médiane de leurs voisins.
- Le témoin est celui de `285`.

⚠ Les contrôles rendent la mesure décidable : les reprises de `285` redonnent ses comptes ; avec tous les points votants, la
reprise redonne ceux de `287` ; la lecture ne connaît aucune panne.

## Les issues, exclusives, au troisième saut

- les ratés que la reprise rend justes sont plus nombreux que les justes qu'elle rend ratés : une reprise qui ne dérange pas les
  voisins rend le troisième saut de la bande plus juste ;
- ils ne le sont pas : elle ne le rend pas plus juste.

⚠ Rapporté à côté : les changements rangés par leur distance aux points corrigés, comme dans `286` ; le quatrième saut.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une autre prédiction, un autre côté ; la même reprise sur le segment `20230702185753`.

Usage :
    uv run python src/nappe/une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.py --verifier
    uv run python src/nappe/une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.py \\
        --json docs/mesures/une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.json
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

from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande import les_profondeurs_de  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_la_bande import LE_SIGNE, la_bande  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import LES_SAUTS, enchainer  # noqa: E402
from le_transfert_retrouve_t_il_la_spire_voisine import le_vote_itere  # noqa: E402
from les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges import (la_distance_en_mailles,  # noqa: E402
                                                                             le_rangement)
from recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste import les_deux_reprises  # noqa: E402
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import le_bilan_du_saut  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_285_A_PUBLIE = LES_MESURES / "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json"
CE_QUE_287_A_PUBLIE = LES_MESURES / "les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.json"


def la_reprise_sans_deranger(q: np.ndarray, normales: np.ndarray, b: dict, sauts: int,
                             votant: np.ndarray | None) -> list[dict]:
    """La chaîne de `248`, repartie d'une surface donnée avec des normales données ; seuls les points `votant` entrent
    dans le vote de leurs voisins."""
    return enchainer(q, normales, LE_SIGNE, sauts, b["lire_rayon"], b["sur_la_grille"], b["gi"], b["gj"], True,
                     votant=votant)


def comptes(x: dict) -> list[int]:
    return [x["les_rates_rendus_justes"], x["les_justes_rendus_rates"]]


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : les reprises ne redonnent pas 285 ou 287, ou la lecture est tombée en panne"}
    if r["les_sauts"][0]["le_gain_net"] > 0:
        return {"lissue": "une reprise qui ne dérange pas les voisins rend le troisième saut de la bande plus juste"}
    return {"lissue": "une reprise qui ne dérange pas les voisins ne rend pas le troisième saut de la bande plus juste"}


def mesurer() -> dict:
    debut = time.monotonic()
    b = la_bande()
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b, "le_verdict": le_verdict({})}
    r = les_deux_reprises(b)
    v, deplace, p, n = b["verite"], r["deplace"], b["p"], b["n"]
    normales = r["chaine"][1]["n"]
    t287 = les_profondeurs_de(la_reprise_sans_deranger(r["q2r"], normales, b, LES_SAUTS - 2, None), p, n)
    tv = les_profondeurs_de(la_reprise_sans_deranger(r["q2r"], normales, b, LES_SAUTS - 2, ~deplace), p, n)
    tt = r["tt"]
    distance = la_distance_en_mailles(b["gi"], b["gj"], deplace)
    d285 = json.loads(CE_QUE_285_A_PUBLIE.read_text())["les_sauts"]
    d287 = json.loads(CE_QUE_287_A_PUBLIE.read_text())["les_sauts"]
    out = {"les_points_deplaces": int(deplace.sum()),
           "les_comptes_de_285": {"refaits": [comptes(le_bilan_du_saut(tt[k], r["tr"][k], v[k + 2])) for k in range(2)],
                                  "publies": [comptes(d285[k]) for k in range(2)]},
           "les_comptes_de_287": {"refaits": [comptes(le_bilan_du_saut(tt[k], t287[k], v[k + 2])) for k in range(2)],
                                  "publies": [comptes(d287[k]) for k in range(2)]},
           "les_sauts": [dict(le_bilan_du_saut(tt[k], tv[k], v[k + 2]), le_saut=k + 3) for k in range(len(tv))],
           "le_troisieme_saut_range": le_rangement(tt[0], tv[0], v[2], distance),
           "le_quatrieme_saut_range": le_rangement(tt[1], tv[1], v[3], distance),
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    out["decidable"] = (out["les_comptes_de_285"]["refaits"] == out["les_comptes_de_285"]["publies"]
                        and out["les_comptes_de_287"]["refaits"] == out["les_comptes_de_287"]["publies"]
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

    gi, gj = np.divmod(np.arange(9), 3)
    grille = lambda val: np.asarray(val, dtype=float).reshape(3, 3)  # noqa: E731
    sans = [np.empty(0)] * 9
    depart = np.array([90.0, 90.0, 90.0, 0.0, 90.0, 0.0, 0.0, 0.0, 0.0])
    tous, _ = le_vote_itere(sans, depart, grille, gi, gj, tours=1)
    muet = np.ones(9, dtype=bool)
    muet[4] = False
    sauf, _ = le_vote_itere(sans, depart, grille, gi, gj, tours=1, votant=muet)
    v("★★★★ un point qui ne vote pas n'entre plus dans la médiane de ses voisins",
      tous[3] == 45.0 and sauf[3] == 0.0, f"{tous[3]} {sauf[3]}")
    v("★★★ sans masque, le vote est celui d'avant", np.array_equal(
        le_vote_itere(sans, depart, grille, gi, gj, tours=1, votant=np.ones(9, dtype=bool))[0], tous))

    b = {"gi": gi, "gj": gj, "sur_la_grille": grille,
         "lire_rayon": lambda q, nq, cote, portee: (np.arange(0.0, 10.0), np.zeros((len(q), 10), dtype=bool))}
    q = np.stack([gj * 8.0, gi * 8.0, np.zeros(9)], axis=-1)
    z = np.tile([0.0, 0.0, 1.0], (9, 1))
    import le_transfert_enchaine_tient_il_les_spires as chaine_de_248
    vus, vrai_vote = [], chaine_de_248.le_vote_itere

    def espion(*args, **kwargs):
        vus.append(kwargs.get("votant"))
        return vrai_vote(*args, **kwargs)

    chaine_de_248.le_vote_itere = espion
    try:
        la_reprise_sans_deranger(q, z, b, 2, muet)
    finally:
        chaine_de_248.le_vote_itere = vrai_vote
    v("★★★★ la reprise passe le masque au vote de chaque saut",
      len(vus) == 2 and all(x is muet for x in vus), str([None if x is None else int(x.sum()) for x in vus]))

    r_ = lambda g: {"decidable": True, "les_sauts": [{"le_gain_net": g}]}  # noqa: E731
    v("★★★★ les issues : plus juste si le gain net du troisième saut est positif, sinon non, indécidable sans contrôle",
      "ne rend pas" not in le_verdict(r_(1))["lissue"] and "ne rend pas" in le_verdict(r_(0))["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
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
