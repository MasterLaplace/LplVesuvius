"""Sous les chunks que la décision corrige, laquelle des deux marches porte l'écart ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES DEUX MARCHES NE SOIENT REGARDÉES SÉPARÉMENT. Ce qui était vu avant d'écrire : tout ce
que `257` à `271` publient, dont leur différence, jamais ses deux termes. Sur `(160, 160)`, le juge voit les points que la
décision abîme à 8,43 voxels en médiane et la marche lit 67,65 sous eux (`271`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. L'écart que la décision corrige est une différence : la marche de la spire
produite moins celle du segment réduit. Le segment réduit est le segment tracé à la main, un point sur huit : il est sur une
seule feuille. Sa marche ne peut donc pas s'écarter d'un pas de ses voisins sans que ce soit la marche qui glisse. Si, sous les
chunks que la décision corrige sur `(160, 160)`, c'est la marche du segment réduit qui porte l'écart, la marche se trompe d'une
spire, pas le juge. Si c'est celle de la spire produite, la question reste entière.

## La mesure

Sur trois voisinages, celui de `(160, 160)` et, en témoin, ceux des deux blocs choisis où la décision corrige juste : les deux
marches d'un seul tenant, refaites ; leur différence doit redonner celle que `265` et `270` publient. Chaque marche est ancrée
comme la différence, à la médiane sur les voisins seuls. Les chunks du bloc que la décision de `264` dit glissés, sur la
différence ancrée : pour chacun, la part de la spire produite, `(p − ancre)`, et celle du segment réduit, `−(r − ancre)`,
comptées du côté de l'écart. L'erreur jugée au centre du chunk dit s'il est juste ou raté.

## Les issues, exclusives, sur les chunks corrigés de `(160, 160)` que le juge tient pour justes

- la médiane de la part du segment réduit dépasse celle de la spire produite : la marche du segment réduit porte l'écart ;
- elle ne la dépasse pas : la marche de la spire produite porte l'écart.

⚠ Rapporté à côté, le témoin : les chunks corrigés des deux blocs choisis que le juge tient pour ratés.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi une marche glisse, ni si la spire produite est juste là où sa marche porte
l'écart.

Usage :
    uv run python src/nappe/laquelle_des_deux_marches_porte_lecart.py --verifier
    uv run python src/nappe/laquelle_des_deux_marches_porte_lecart.py \\
        --json docs/mesures/laquelle_des_deux_marches_porte_lecart.json
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

from la_marche_sait_elle_ou_ne_pas_corriger import la_decision, le_melange  # noqa: E402
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_PREDICTION, LE_BLOC, LE_COTE,  # noqa: E402
                                                            LE_DOSSIER, LES_JUGES, le_cadre, les_blocs_candidats,
                                                            lerreur_aux_chunks, lerreur_jugee, lire_la_pile,
                                                            rendre)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_voisinage_dit_il_quel_niveau_est_le_bon import (LES_SURFACES, la_marche_du_voisinage,  # noqa: E402
                                                        lancre_du_voisinage, les_voisins)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"
CE_QUE_265_A_PUBLIE = LES_MESURES / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"
CE_QUE_270_A_PUBLIE = LES_MESURES / "lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json"
LA_TOLERANCE_DE_REPRODUCTION = 0.006   # la différence publiée est arrondie au centième


def la_carte(publiee: list) -> np.ndarray:
    return np.array([[np.nan if v is None else float(v) for v in rr] for rr in publiee])


def les_parts(prod: np.ndarray, red: np.ndarray, by: int, bx: int, glissade: float) -> dict:
    """Les chunks du bloc que la décision dit glissés, et la part de chaque marche dans l'écart, comptée de son côté."""
    y0, x0, c = by - LE_BLOC, bx - LE_BLOC, LE_BLOC
    diff = prod - red
    a_d, a_p, a_r = (lancre_du_voisinage(m, y0, x0, by, bx) for m in (diff, prod, red))
    d_b = diff[c:2 * c, c:2 * c] - a_d
    dec = la_decision(d_b, le_melange(d_b, glissade))
    sigma = np.sign(d_b)
    return {"les_ancres_voxels": {"la_difference": a_d, "la_spire_produite": a_p, "le_segment_reduit": a_r},
            "decide": dec, "lecart": d_b,
            "la_part_de_la_spire_produite": (prod[c:2 * c, c:2 * c] - a_p) * sigma,
            "la_part_du_segment_reduit": -(red[c:2 * c, c:2 * c] - a_r) * sigma}


def la_famille(parts: dict, masque: np.ndarray, erreur: np.ndarray) -> dict:
    if not masque.any():
        return {"les_chunks": 0}
    med = lambda a: round(float(np.median(a[masque])), 4)  # noqa: E731
    return {"les_chunks": int(masque.sum()), "lecart_median_voxels": med(np.abs(parts["lecart"])),
            "la_part_de_la_spire_produite_mediane_voxels": med(parts["la_part_de_la_spire_produite"]),
            "la_part_du_segment_reduit_mediane_voxels": med(parts["la_part_du_segment_reduit"]),
            "lerreur_jugee_abs_mediane_voxels": med(np.abs(erreur))}


def les_familles(parts: dict, erreur: np.ndarray) -> dict:
    ok = parts["decide"] & np.isfinite(erreur)
    with np.errstate(invalid="ignore"):
        juste = np.abs(erreur) < DEMI_PAS_EN_VOXELS
    return {"juges_justes": la_famille(parts, ok & juste, erreur), "juges_rates": la_famille(parts, ok & ~juste, erreur),
            "les_chunks_corriges": int(parts["decide"].sum())}


def ce_qui_porte(f: dict) -> str | None:
    if not f.get("les_chunks"):
        return None
    return ("le_segment_reduit" if f["la_part_du_segment_reduit_mediane_voxels"]
            > f["la_part_de_la_spire_produite_mediane_voxels"] else "la_spire_produite")


def un_voisinage(nom: str, by: int, bx: int, publiee: list, candidats: set, err: np.ndarray, glissade: float) -> dict:
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
    prod, red = prof["la_spire_produite"], prof["le_segment_reduit"]
    ecart = np.abs((prod - red) - la_carte(publiee))
    reproduit = bool(np.nanmax(ecart) <= LA_TOLERANCE_DE_REPRODUCTION)
    parts = les_parts(prod, red, by, bx, glissade)
    erreur = lerreur_aux_chunks(err, by, bx, LE_BLOC)
    arr = lambda a: [[None if not np.isfinite(v) else round(float(v), 2) for v in rr] for rr in a]  # noqa: E731
    r = {"la_rangee": by, "la_colonne": bx, "reproduit": reproduit,
         "lecart_max_a_la_publiee_voxels": round(float(np.nanmax(ecart)), 4),
         "les_ancres_voxels": {k: round(float(v), 4) for k, v in parts["les_ancres_voxels"].items()},
         **les_familles(parts, erreur),
         "la_marche_de_la_spire_produite": arr(prod), "la_marche_du_segment_reduit": arr(red),
         "les_chunks_decides": [[int(i), int(j)] for i, j in zip(*np.nonzero(parts["decide"]))],
         "lerreur_aux_chunks": arr(erreur), "les_secondes": round(time.monotonic() - debut, 1)}
    print(f"{nom} : reproduit {reproduit}, {r['juges_justes']} / {r['juges_rates']}", flush=True)
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
    d265 = json.loads(CE_QUE_265_A_PUBLIE.read_text())["les_blocs"]
    d270 = json.loads(CE_QUE_270_A_PUBLIE.read_text())["les_blocs"]
    sources = {"160_160": d270["160_160"], "le_bloc_de_257": d265["le_bloc_de_257"],
               "le_bloc_de_259": d265["le_bloc_de_259"]}
    out = {"la_glissade_voxels": glissade, "les_voisinages": {}}
    for nom, b in sources.items():
        out["les_voisinages"][nom] = un_voisinage(nom, b["la_rangee"], b["la_colonne"], b["la_difference"], candidats,
                                                  err, glissade)
    v = out["les_voisinages"]
    out["decidable"] = all(x.get("reproduit") for x in v.values())
    out["le_temoin"] = la_reunion([v["le_bloc_de_257"]["juges_rates"], v["le_bloc_de_259"]["juges_rates"]])
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    return out


def la_reunion(familles: list[dict]) -> dict:
    """Deux familles réunies par leurs chunks : la médiane pondérée n'existe pas, donc la réunion ne rend que les
    comptes et, pour chaque part, la plus petite et la plus grande des médianes."""
    f = [x for x in familles if x.get("les_chunks")]
    out = {"les_chunks": sum(x["les_chunks"] for x in f)}
    for k in ("la_part_de_la_spire_produite_mediane_voxels", "la_part_du_segment_reduit_mediane_voxels"):
        out[k] = [min(x[k] for x in f), max(x[k] for x in f)] if f else None
    out["porte"] = sorted({ce_qui_porte(x) for x in f})
    return out


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : les deux marches refaites ne redonnent pas la différence publiée"}
    qui = ce_qui_porte(r["les_voisinages"]["160_160"]["juges_justes"])
    if qui is None:
        return {"lissue": "indécidable : aucun chunk corrigé que le juge tient pour juste"}
    return {"lissue": {"le_segment_reduit": "la marche du segment réduit porte l'écart",
                       "la_spire_produite": "la marche de la spire produite porte l'écart"}[qui]}


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

    c, n = LE_BLOC, 3 * LE_BLOC
    rng = np.random.default_rng(5)
    base_p, base_r = rng.normal(0.0, 2.0, (n, n)) + 30.0, rng.normal(0.0, 2.0, (n, n)) - 10.0
    coin = (slice(c, c + 5), slice(c, c + 5))

    # La spire produite glisse sur un coin du bloc : sa marche porte l'écart, celle du segment réduit est plate.
    p1, r1 = base_p.copy(), base_r.copy()
    p1[coin] += 69.458
    a = les_parts(p1, r1, c, c, 69.458)
    f_a = la_famille(a, a["decide"], np.full((c, c), 70.0))
    v("★★★★ quand la spire produite glisse, sa marche porte l'écart et chaque ancre est lue sur sa propre marche",
      lambda: int(a["decide"].sum()) == 25 and ce_qui_porte(f_a) == "la_spire_produite"
      and abs(f_a["la_part_de_la_spire_produite_mediane_voxels"] - 69.458) < 8
      and abs(f_a["la_part_du_segment_reduit_mediane_voxels"]) < 8
      and abs(a["les_ancres_voxels"]["le_segment_reduit"] + 10.0) < 1.0, str(f_a))
    # Le segment réduit glisse, vers le bas, sur le même coin : la différence monte pareil, c'est l'autre marche qui la porte.
    p2, r2 = base_p.copy(), base_r.copy()
    r2[coin] -= 69.458
    b = les_parts(p2, r2, c, c, 69.458)
    f_b = la_famille(b, b["decide"], np.zeros((c, c)))
    v("★★★★ quand c'est la marche du segment réduit qui glisse, c'est elle qui porte l'écart, du côté de l'écart",
      lambda: int(b["decide"].sum()) == 25 and ce_qui_porte(f_b) == "le_segment_reduit"
      and f_b["la_part_du_segment_reduit_mediane_voxels"] > 60, str(f_b))
    # Le même glissement vers le haut sur la spire produite, vers le bas sur l'autre : le côté de l'écart suit le signe.
    p3, r3 = base_p.copy(), base_r.copy()
    p3[coin] -= 69.458
    g = les_parts(p3, r3, c, c, 69.458)
    f_g = la_famille(g, g["decide"], np.full((c, c), -70.0))
    v("★★★★ une glissade vers le bas se compte aussi du côté de l'écart",
      lambda: ce_qui_porte(f_g) == "la_spire_produite" and f_g["la_part_de_la_spire_produite_mediane_voxels"] > 60)
    err = np.zeros((c, c))
    err[0:2, :] = 70.0
    err[4, 4] = np.nan
    fam = les_familles(a, err)
    v("★★★★ le juge partage les chunks corrigés en justes et en ratés, et laisse un chunk non noté",
      lambda: fam["juges_rates"]["les_chunks"] == 10 and fam["juges_justes"]["les_chunks"] == 14
      and fam["les_chunks_corriges"] == 25, str(fam))
    v("★★★★ les issues : l'une ou l'autre marche, indécidable si non reproduit",
      lambda: "segment réduit porte" in le_verdict({"decidable": True, "les_voisinages": {"160_160": {"juges_justes": f_b}}})["lissue"]
      and "spire produite porte" in le_verdict({"decidable": True, "les_voisinages": {"160_160": {"juges_justes": f_a}}})["lissue"]
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
    print(json.dumps({k: r.get(k) for k in ("le_temoin", "le_verdict", "decidable")}, indent=1, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
