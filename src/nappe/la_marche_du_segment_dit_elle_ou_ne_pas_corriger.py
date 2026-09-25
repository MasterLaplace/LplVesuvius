"""La marche du segment réduit, plate par construction, dit-elle où ne pas corriger ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA GARDE NE SOIT APPLIQUÉE À UN SEUL POINT. Ce qui était vu avant d'écrire : tout ce que
`257` à `273` publient. Les marches des deux surfaces ont été regardées séparément sur trois voisinages seulement (`272`) ; sur
les sept voisinages réguliers de `270`, seule leur différence est publiée.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `273` montre que ce que la procédure abîme sur `(160, 160)` vient de la
marche : elle lit 46 voxels sous une surface qui ne s'écarte que de deux voxels de sa feuille. Le segment réduit est sur une
seule feuille partout : sa marche devrait rester plate partout. Là où elle ne l'est pas, la marche lit mal, et une correction
qui s'appuie sur elle n'a pas de raison d'être crue. Cette garde ne demande ni juge ni humain : le segment réduit est toujours
là, puisque c'est de lui qu'on part.

## La procédure

Celle de `265`, sans rien y changer, sur les neuf voisinages de `265` et `270`, marches refaites ; plus une garde : un point que
la décision corrige ne l'est que si la marche du segment réduit, moins son ancre prise sur les voisins seuls, y est à moins d'un
quart de pas, 18 voxels. Sans la garde, la procédure doit redonner les comptes publiés.

## Les issues, exclusives, sur les neuf voisinages réunis

- les ratés rendus justes moins les justes rendus ratés sont plus nombreux avec la garde que sans elle : la garde améliore la
  procédure ;
- ils ne le sont pas : la garde n'améliore pas la procédure.

⚠ Rapporté à côté : bloc par bloc, les points que la garde retient, et parmi eux ceux qui auraient été rendus justes et ceux qui
auraient été rendus ratés ; la part réunie des blocs réguliers, avant, sans la garde et avec elle.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : d'autres blocs, un autre seuil, une seconde passe.

Usage :
    uv run python src/nappe/la_marche_du_segment_dit_elle_ou_ne_pas_corriger.py --verifier
    uv run python src/nappe/la_marche_du_segment_dit_elle_ou_ne_pas_corriger.py \\
        --json docs/mesures/la_marche_du_segment_dit_elle_ou_ne_pas_corriger.json
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

from la_correction_tient_elle_sur_des_blocs_reguliers import la_part_reunie  # noqa: E402
from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points, la_part_juste  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import (corriger_decide, la_decision, le_bilan,  # noqa: E402
                                                    le_melange)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_DOSSIER, LES_JUGES, le_cadre, les_blocs_candidats,
                                                            lerreur_jugee, lire_la_pile, rendre)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_voisinage_dit_il_quel_niveau_est_le_bon import (LES_SURFACES, la_marche_du_voisinage,  # noqa: E402
                                                        lancre_du_voisinage, les_voisins)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
CE_QUE_270_A_PUBLIE = LES_MESURES / "lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json"
LE_QUART_DE_PAS = DEMI_PAS_EN_VOXELS / 2.0
LES_COMPTES = ("les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")


def les_bilans(tau0: np.ndarray, err: np.ndarray, prod: np.ndarray, red: np.ndarray, by: int, bx: int,
               glissade: float, seuil: float = LE_QUART_DE_PAS) -> dict:
    """La décision de `265` sur un voisinage, sans la garde et avec elle."""
    c = LE_BLOC
    y0, x0 = by - c, bx - c
    diff = prod - red
    a_d, a_r = lancre_du_voisinage(diff, y0, x0, by, bx), lancre_du_voisinage(red, y0, x0, by, bx)
    d_b, r_b = diff[c:2 * c, c:2 * c] - a_d, red[c:2 * c, c:2 * c] - a_r
    ecart, dedans = la_carte_aux_points(d_b, by, bx, tau0.shape)
    ecart = np.where(dedans, ecart, np.nan)
    dec = la_decision(ecart, le_melange(d_b, glissade))
    plat, _ = la_carte_aux_points(r_b, by, bx, tau0.shape)
    with np.errstate(invalid="ignore"):
        garde = np.isfinite(plat) & (np.abs(plat) < seuil)
    verite = tau0 - err
    sans = le_bilan(tau0, corriger_decide(tau0, ecart, dec), verite, err, dedans, dec)
    avec = le_bilan(tau0, corriger_decide(tau0, ecart, dec & garde), verite, err, dedans, dec & garde)
    return {"les_ancres_voxels": {"la_difference": round(float(a_d), 4), "le_segment_reduit": round(float(a_r), 4)},
            "avant": la_part_juste(tau0, verite, dedans), "sans_la_garde": sans, "avec_la_garde": avec,
            "retenus_par_la_garde": {k: sans[k] - avec[k] for k in LES_COMPTES}}


def les_reunions(voisinages: dict, noms: list[str]) -> dict:
    v = {n: voisinages[n] for n in noms}
    out = {"les_blocs": len(v), "avant": la_part_reunie({n: {"avant": x["avant"]} for n, x in v.items()}, "avant")}
    for cle in ("sans_la_garde", "avec_la_garde"):
        out[cle] = {"apres": la_part_reunie({n: x[cle] for n, x in v.items()}, "apres"),
                    **{k: sum(x[cle][k] for x in v.values()) for k in LES_COMPTES}}
        out[cle]["le_gain_net"] = out[cle]["les_rates_rendus_justes"] - out[cle]["les_justes_rendus_rates"]
    return out


def un_voisinage(nom, by, bx, candidats, tau0, err, glissade, publie) -> dict:
    debut = time.monotonic()
    blocs = [(by, bx)] + les_voisins(by, bx, candidats)
    for s in LES_SURFACES:
        for vy, vx in blocs:
            if not rendre(LE_DOSSIER / s / "maillage", LE_DOSSIER / s / f"bloc_{vy}_{vx}", le_cadre(vy, vx, LE_BLOC))["rendue"]:
                return {"decidable": False, "la_raison": f"{s} ne se rend pas sur ({vy}, {vx})"}
    prof = {}
    for s in LES_SURFACES:
        piles = {v: lire_la_pile(LE_DOSSIER / s / f"bloc_{v[0]}_{v[1]}") for v in blocs}
        prof[s] = la_marche_du_voisinage(piles, by - LE_BLOC, bx - LE_BLOC, 3 * LE_BLOC)["la_profondeur"]
        del piles
    r = les_bilans(tau0, err, prof["la_spire_produite"], prof["le_segment_reduit"], by, bx, glissade)
    r.update({"la_rangee": by, "la_colonne": bx, "publie": publie,
              "reproduit": {k: r["sans_la_garde"][k] for k in LES_COMPTES} == publie,
              "les_secondes": round(time.monotonic() - debut, 1)})
    print(f"{nom} : reproduit {r['reproduit']}, sans {r['sans_la_garde']['apres']}, avec {r['avec_la_garde']['apres']}, "
          f"retenus {r['retenus_par_la_garde']}", flush=True)
    return r


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    gy, gx = d257["le_treillis"]
    _, valide, _ = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    tau0 = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    err = lerreur_jugee(tau0, [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES])
    candidats = set(les_blocs_candidats(tau0, valide, gy, gx))
    out = {"la_glissade_voxels": glissade, "le_seuil_voxels": LE_QUART_DE_PAS, "les_voisinages": {}}
    choisis, reguliers = [], []
    for source, liste in ((CE_QUE_265_A_PUBLIE, choisis), (CE_QUE_270_A_PUBLIE, reguliers)):
        for nom, b in json.loads(source.read_text())["les_blocs"].items():
            publie = {k: b["lancre_du_voisinage"]["la_decision"][k] for k in LES_COMPTES}
            out["les_voisinages"][nom] = un_voisinage(nom, b["la_rangee"], b["la_colonne"], candidats, tau0, err,
                                                      glissade, publie)
            liste.append(nom)
    v = out["les_voisinages"]
    out["decidable"] = all(x.get("reproduit") for x in v.values())
    if out["decidable"]:
        out["les_reunis"] = {"les_neuf": les_reunions(v, choisis + reguliers), "les_choisis": les_reunions(v, choisis),
                             "les_reguliers": les_reunions(v, reguliers)}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : sans la garde, la procédure ne redonne pas les comptes publiés"}
    g = r["les_reunis"]["les_neuf"]
    if g["avec_la_garde"]["le_gain_net"] > g["sans_la_garde"]["le_gain_net"]:
        return {"lissue": "la garde améliore la procédure"}
    return {"lissue": "la garde n'améliore pas la procédure"}


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

    # Un voisinage fabriqué : deux bosses d'une glissade dans la différence. Sous la première, la spire produite a glissé
    # (le segment réduit est plat), et le juge y voit des ratés ; sous la seconde, c'est la marche du segment réduit qui
    # plonge, et le juge y voit des justes.
    c, n = LE_BLOC, 3 * LE_BLOC
    rng = np.random.default_rng(7)
    prod, red = rng.normal(0.0, 2.0, (n, n)), rng.normal(0.0, 2.0, (n, n))
    prod[c:c + 5, c:c + 5] += 69.458
    red[c + 9:c + 14, c + 9:c + 14] -= 69.458
    tau0 = np.zeros((40, 40))
    _, dedans = la_carte_aux_points(np.zeros((c, c)), c, c, tau0.shape)
    b1, _ = la_carte_aux_points(np.pad(np.ones((5, 5)), ((0, 11), (0, 11))), c, c, tau0.shape)
    b2, _ = la_carte_aux_points(np.pad(np.ones((5, 5)), ((9, 2), (9, 2))), c, c, tau0.shape)
    err = np.zeros((40, 40))
    err[dedans & (b1 > 0) & (b1 < 0.99)] = np.nan
    err[dedans & (b2 > 0) & (b2 < 0.99)] = np.nan
    err[dedans & (b1 > 0.99)] = 70.0
    r = les_bilans(tau0, err, prod, red, c, c, 69.458)
    n1, n2 = int((dedans & (b1 > 0.99)).sum()), int((dedans & (b2 > 0.99)).sum())
    v("★★★★ sans la garde, la décision corrige les deux bosses : les ratés de l'une rendus justes, les justes de l'autre ratés",
      lambda: r["sans_la_garde"]["les_rates_rendus_justes"] == n1 and r["sans_la_garde"]["les_justes_rendus_rates"] == n2
      and n1 > 0 and n2 > 0, f"{r['sans_la_garde']} ; {n1} et {n2}")
    v("★★★★ avec la garde, la bosse que porte la marche du segment réduit n'est plus corrigée, l'autre l'est toujours",
      lambda: r["avec_la_garde"]["les_rates_rendus_justes"] == n1 and r["avec_la_garde"]["les_justes_rendus_rates"] == 0
      and r["retenus_par_la_garde"]["les_justes_rendus_rates"] == n2, str(r["avec_la_garde"]))
    v("★★★ l'ancre du segment réduit est prise sur ses voisins, pas sur le bloc",
      lambda: abs(r["les_ancres_voxels"]["le_segment_reduit"]) < 1.0)
    g = les_reunions({"a": r, "b": r}, ["a", "b"])
    v("★★★★ la réunion additionne les comptes et le gain net",
      lambda: g["sans_la_garde"]["le_gain_net"] == 2 * (n1 - n2) and g["avec_la_garde"]["le_gain_net"] == 2 * n1, str(g))
    v("★★★★ les issues : améliore si le gain net grandit, sinon non, indécidable si non reproduit",
      lambda: "améliore la" in le_verdict({"decidable": True, "les_reunis": {"les_neuf": g}})["lissue"]
      and "n'améliore pas" in le_verdict({"decidable": True, "les_reunis": {"les_neuf": {
          "sans_la_garde": {"le_gain_net": 5}, "avec_la_garde": {"le_gain_net": 5}}}})["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({"les_reunis": r.get("les_reunis"), "le_verdict": r["le_verdict"]}, indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
