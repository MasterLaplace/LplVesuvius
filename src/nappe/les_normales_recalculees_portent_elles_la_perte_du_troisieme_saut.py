"""Les normales recalculées portent-elles la perte du troisième saut de la bande, autour des points corrigés ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CETTE REPRISE. Ce qui était vu avant d'écrire : tout ce que `248` et `257` à `286` publient.
Repartie du deuxième saut corrigé de la bande, recalé sur son rayon, la chaîne rend au troisième saut 7 ratés justes pour 15
justes ratés (`285`). 10 de ces 15 justes sont des points que la correction n'a pas touchés, à une, deux ou trois mailles d'un
point déplacé (`286`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Deux mécanismes de la chaîne lisent les voisins d'un point. Les normales de
la surface d'où elle repart sont recalculées par différences entre mailles voisines : un point déplacé change la normale de ses
voisins, donc le rayon qu'ils lisent. Et le vote vise, tour après tour, la médiane d'un carré de trois mailles. `286` ne les
sépare pas. Cette tranche fait repartir la chaîne du même deuxième saut recalé, mais avec les normales du témoin : aucune
normale n'est recalculée à partir des points déplacés, et seul le vote peut encore porter un point déplacé vers ses voisins.

## Ce qui est fait, déclaré avant la mesure

- Le deuxième saut recalé est celui de `285`, refait à l'identique.
- La chaîne en repart pour le troisième et le quatrième saut avec les normales du deuxième saut de `248`, celles du témoin, au
  lieu de les recalculer. Après le troisième saut, les normales sont recalculées comme d'habitude.
- Le témoin est celui de `285` : parti du deuxième saut non corrigé, avec ces mêmes normales.
- Les changements du troisième saut sont rangés comme dans `286`, par leur distance au plus proche point déplacé.

⚠ Les contrôles rendent la mesure décidable : les reprises de `285` redonnent ses comptes au troisième et au quatrième saut ; la
lecture ne connaît aucune panne.

## Les issues, exclusives, autour des points corrigés au troisième saut

- les justes que la reprise rend ratés à une maille ou plus d'un point déplacé sont moins nombreux que dans `285` : les normales
  recalculées portent une part de la perte ;
- ils ne le sont pas : les normales ne la portent pas, et la perte passe par le vote ou par la lecture.

⚠ Rapporté à côté : le troisième saut entier, contre le témoin ; aux points déplacés eux-mêmes ; le quatrième saut.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : si garder les normales du témoin est une bonne façon de repartir ; le vote, isolé à son
tour.

Usage :
    uv run python src/nappe/les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.py --verifier
    uv run python src/nappe/les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.py \\
        --json docs/mesures/les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.json
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
from les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges import (la_distance_en_mailles,  # noqa: E402
                                                                             le_rangement)
from recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste import les_deux_reprises  # noqa: E402
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import le_bilan_du_saut  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_285_A_PUBLIE = LES_MESURES / "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json"
CE_QUE_286_A_PUBLIE = LES_MESURES / "les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges.json"


def les_justes_perdus_autour(rangement: dict) -> int:
    """Les justes que la reprise rend ratés à une maille ou plus d'un point déplacé."""
    return sum(c["les_justes_rendus_rates"] for nom, c in rangement["les_classes"].items() if nom != "le_point_lui_meme")


def la_reprise_avec_ces_normales(q: np.ndarray, normales: np.ndarray, b: dict, sauts: int) -> list[dict]:
    """La chaîne de `248`, repartie d'une surface donnée point par point avec des normales données, sans les recalculer."""
    return enchainer(q, normales, LE_SIGNE, sauts, b["lire_rayon"], b["sur_la_grille"], b["gi"], b["gj"], True)


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : les reprises ne redonnent pas les comptes de 285, ou la lecture est tombée en panne"}
    if r["les_justes_perdus_autour"]["avec_les_normales_du_temoin"] < r["les_justes_perdus_autour"]["dans_285"]:
        return {"lissue": "les normales recalculées portent une part de la perte du troisième saut"}
    return {"lissue": "les normales recalculées ne portent pas la perte du troisième saut"}


def mesurer() -> dict:
    debut = time.monotonic()
    b = la_bande()
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b, "le_verdict": le_verdict({})}
    r = les_deux_reprises(b)
    v, deplace = b["verite"], r["deplace"]
    p, n = b["p"], b["n"]
    reprise = la_reprise_avec_ces_normales(r["q2r"], r["chaine"][1]["n"], b, LES_SAUTS - 2)
    tn = les_profondeurs_de(reprise, p, n)
    distance = la_distance_en_mailles(b["gi"], b["gj"], deplace)
    d285 = json.loads(CE_QUE_285_A_PUBLIE.read_text())["les_sauts"]
    d286 = json.loads(CE_QUE_286_A_PUBLIE.read_text())
    comptes = lambda x: [x["les_rates_rendus_justes"], x["les_justes_rendus_rates"]]  # noqa: E731
    rangement = le_rangement(r["tt"][0], tn[0], v[2], distance)
    out = {"les_points_deplaces": int(deplace.sum()),
           "les_comptes_de_285_refaits": {"au_troisieme": comptes(le_bilan_du_saut(r["tt"][0], r["tr"][0], v[2])),
                                          "au_quatrieme": comptes(le_bilan_du_saut(r["tt"][1], r["tr"][1], v[3]))},
           "les_comptes_de_285_publies": {"au_troisieme": comptes(d285[0]), "au_quatrieme": comptes(d285[1])},
           "les_sauts": [dict(le_bilan_du_saut(r["tt"][k], tn[k], v[k + 2]), le_saut=k + 3) for k in range(len(tn))],
           "le_troisieme_saut_range": rangement,
           "les_justes_perdus_autour": {"avec_les_normales_du_temoin": les_justes_perdus_autour(rangement),
                                        "dans_285": les_justes_perdus_autour(d286["le_troisieme_saut"])},
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    out["decidable"] = (out["les_comptes_de_285_refaits"] == out["les_comptes_de_285_publies"]
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

    rg = {"les_classes": {"le_point_lui_meme": {"les_justes_rendus_rates": 5}, "a_une_maille": {"les_justes_rendus_rates": 6},
                          "a_deux_ou_trois_mailles": {"les_justes_rendus_rates": 4},
                          "a_quatre_mailles_ou_plus": {"les_justes_rendus_rates": 0}}}
    v("★★★★ autour des points corrigés veut dire à une maille ou plus, le point lui-même exclu",
      les_justes_perdus_autour(rg) == 10, str(les_justes_perdus_autour(rg)))

    # Sans lecture qui trouve une feuille, la chaîne avance d'un pas le long des normales qu'on lui donne.
    gi, gj = np.divmod(np.arange(9), 3)
    b = {"gi": gi, "gj": gj, "sur_la_grille": lambda val: np.asarray(val, dtype=float).reshape(3, 3),
         "lire_rayon": lambda q, nq, cote, portee: (np.arange(0.0, 10.0), np.zeros((len(q), 10), dtype=bool))}
    q = np.stack([gj * 8.0, gi * 8.0, np.zeros(9)], axis=-1)
    penchees = np.tile([0.6, 0.0, 0.8], (9, 1))
    c = la_reprise_avec_ces_normales(q, penchees, b, 1)
    v("★★★★ la reprise suit les normales données, sans les recalculer d'abord",
      np.allclose(c[0]["q"] - q, 72.0833 * penchees, atol=1e-3), str((c[0]["q"] - q)[0]))

    r_ = lambda a, b_: {"decidable": True, "les_justes_perdus_autour": {"avec_les_normales_du_temoin": a,  # noqa: E731
                                                                        "dans_285": b_}}
    v("★★★★ les issues : les normales portent une part si l'on perd moins autour, sinon non, indécidable sans contrôle",
      "portent une part" in le_verdict(r_(9, 10))["lissue"] and "ne portent pas" in le_verdict(r_(10, 10))["lissue"]
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
