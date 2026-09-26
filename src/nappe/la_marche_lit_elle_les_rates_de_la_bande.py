"""La marche lit-elle les ratés du premier saut de la bande `w028-037` comme ceux du segment `20230702185753` ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT LA MESURE. Ce qui était vu avant d'écrire : tout ce que `275` et `281` publient. Sur le
segment, la procédure de `265` rend au premier saut 163 ratés justes pour 41 justes ratés (`275`) ; sur la bande, 15 pour 25
(`281`). Ni l'un ni l'autre ne dit si c'est la LECTURE qui manque sur la bande, ou le CHOIX.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. La correction de `265` ramène un point de l'écart que la marche lit, et la
décision de `264` ne fait que choisir quels points ramener. Un point que le juge dit raté est donc réparable par la marche si
l'écart lu le ramène à moins d'un demi-feuillet de sa couche ; un point juste est cassable si l'écart lu l'en éloigne d'un
demi-feuillet ou plus. Ces deux parts ne dépendent pas de la décision : elles disent ce que la marche sait. Si elles tiennent
sur la bande, ce qui manque est le choix ; sinon, c'est la lecture.

## Ce qui est lu, et d'où

Aucune pile n'est rendue, aucune table de pas n'est refaite : ce sont celles de `275` sur le segment (340 blocs) et de `281`
sur la bande (84 blocs). L'écart est celui que la décision lit, calculé comme `265` le calcule : la marche d'un seul tenant sur
le bloc et ses voisins candidats, pour les deux surfaces, leur différence, moins l'ancre (la médiane sur les voisins seuls),
portée aux points de la maille du bloc. Chaque surface est jugée par le juge qui a noté sa procédure : les deux juges de `275`
sur le segment, la première couche de la bande sur la bande.

⚠ Deux contrôles rendent la mesure décidable : sur chaque bloc, la décision de `264` prise sur cet écart doit redonner les
points corrigés publiés ; et, réunis, les réparables qu'elle retient et les cassables qu'elle retient doivent redonner les
ratés rendus justes et les justes rendus ratés publiés (163 et 41, 15 et 25).

## Les issues, exclusives

- la part des ratés que la marche répare est, sur la bande, au moins celle du segment : la marche lit les ratés de la bande
  aussi bien, et ce qui manque sur la bande est le choix ;
- elle est plus faible : la marche lit moins bien les ratés de la bande.

⚠ Rapporté à côté : la part des justes que la marche casse ; la corrélation de l'écart à l'erreur ; la médiane de l'écart sur
les justes (le biais de l'ancre) ; la part réparable des ratés trop loin et des ratés trop près ; la médiane de l'écart des
ratés réparables, contre la glissade de `261` ; ce que la décision retient des uns et des autres.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi la lecture ou le choix diffère ; une autre décision ; le deuxième saut.

Usage :
    uv run python src/nappe/la_marche_lit_elle_les_rates_de_la_bande.py --verifier
    uv run python src/nappe/la_marche_lit_elle_les_rates_de_la_bande.py \\
        --json docs/mesures/la_marche_lit_elle_les_rates_de_la_bande.json
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

from la_marche_corrige_t_elle_la_spire_produite import la_carte_aux_points  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import la_decision, le_melange  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_la_bande import (LES_COUCHES_DE_LA_BANDE,  # noqa: E402
                                                            LES_SURFACES_DE_LA_BANDE, LE_PREMIER_SAUT,
                                                            lire_le_plan)
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (LES_SURFACES,  # noqa: E402
                                                                     la_decision_du_bloc, la_marche_assemblee,
                                                                     le_segment, les_rendus_sur_le_disque,
                                                                     les_tables)
from la_spire_produite_se_lit_elle_dans_le_treillis import LE_BLOC  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import DEMI_PAS_EN_VOXELS  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import lancre_du_voisinage, les_voisins  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_275_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
CE_QUE_281_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_tient_elle_sur_la_bande.json"
# L'erreur (en ligne) contre l'écart lu (en colonne), par pas de 12 voxels ; ce qui dépasse est compté au bord.
LES_BORDS = np.arange(-144.0, 145.0, 12.0)


# ── L'ÉCART QUE LA DÉCISION LIT ────────────────────────────────────────────────────────────────────────────────────

def lecart_des_profondeurs(prod: np.ndarray, red: np.ndarray, by: int, bx: int,
                           forme: tuple) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """L'écart aux points du bloc, le masque du bloc et l'écart aux chunks, comme `la_decision_du_bloc` les calcule."""
    c = LE_BLOC
    diff = prod - red
    ancre = lancre_du_voisinage(diff, by - c, bx - c, by, bx)
    if ancre is None:
        return None
    d_b = diff[c:2 * c, c:2 * c] - ancre
    ecart, dedans = la_carte_aux_points(d_b, by, bx, forme)
    return np.where(dedans, ecart, np.nan), dedans, d_b


def lecart_du_bloc(by: int, bx: int, candidats: set, tables: dict, rendus: dict, forme: tuple,
                   surfaces: tuple) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """L'écart d'un bloc, avec les mêmes refus que `un_bloc` de `275` ; `surfaces` est (la référence, la produite)."""
    blocs = [(by, bx)] + les_voisins(by, bx, candidats)
    for s in surfaces:
        for vy, vx in blocs:
            if not rendus.get((s, vy, vx)) or (s, vy, vx) not in tables:
                return None
    if len(blocs) == 1:
        return None
    prof = {s: la_marche_assemblee({b: tables[(s, *b)] for b in blocs}, blocs, by - LE_BLOC, bx - LE_BLOC,
                                   3 * LE_BLOC)["la_profondeur"] for s in surfaces}
    return lecart_des_profondeurs(prof[surfaces[1]], prof[surfaces[0]], by, bx, forme)


# ── CE QUE LA MARCHE SAIT ──────────────────────────────────────────────────────────────────────────────────────────

def _part(n: int, sur: int) -> float | None:
    return round(n / sur, 4) if sur else None


def ce_que_la_marche_lit(err: np.ndarray, ecart: np.ndarray, decide: np.ndarray, glissade: float) -> dict:
    """Sur les points notés où l'écart est lu : les ratés que l'écart répare, les justes qu'il casse, et ce que la décision
    retient des uns et des autres."""
    note = np.isfinite(err) & np.isfinite(ecart)
    e, x, d = err[note], ecart[note], decide[note]
    rate = np.abs(e) >= DEMI_PAS_EN_VOXELS
    apres = np.abs(e - x) < DEMI_PAS_EN_VOXELS
    reparable, cassable = rate & apres, ~rate & ~apres
    loin, pres = rate & (e > 0), rate & (e < 0)
    return {"les_points_notes": int(note.sum()), "les_rates": int(rate.sum()), "les_justes": int((~rate).sum()),
            "les_rates_reparables": int(reparable.sum()), "les_justes_cassables": int(cassable.sum()),
            "la_part_des_rates_que_la_marche_repare": _part(int(reparable.sum()), int(rate.sum())),
            "la_part_des_justes_que_la_marche_casse": _part(int(cassable.sum()), int((~rate).sum())),
            "la_part_reparable_des_rates_trop_loin": _part(int((reparable & loin).sum()), int(loin.sum())),
            "la_part_reparable_des_rates_trop_pres": _part(int((reparable & pres).sum()), int(pres.sum())),
            "la_correlation_de_lecart_a_lerreur": (round(float(np.corrcoef(x, e)[0, 1]), 4)
                                                  if len(e) > 2 and np.std(x) > 0 and np.std(e) > 0 else None),
            "la_mediane_de_lecart_des_justes_voxels": (round(float(np.median(x[~rate])), 4) if (~rate).any() else None),
            "la_mediane_de_lecart_absolu_des_reparables_voxels": (round(float(np.median(np.abs(x[reparable]))), 4)
                                                                   if reparable.any() else None),
            "la_glissade_voxels": glissade,
            "lhistogramme": {"les_bords_voxels": LES_BORDS.tolist(),
                             "les_comptes": np.histogram2d(np.clip(e, LES_BORDS[0], LES_BORDS[-1] - 1e-9),
                                                           np.clip(x, LES_BORDS[0], LES_BORDS[-1] - 1e-9),
                                                           bins=[LES_BORDS, LES_BORDS])[0].astype(int).tolist()},
            "la_decision_retient": {"des_reparables": int((d & reparable).sum()), "des_cassables": int((d & cassable).sum()),
                                    "en_tout": int(d.sum())}}


def lire_une_surface(tau0, err, glissade, candidats, surfaces, publie: dict) -> dict:
    """Tous les blocs d'une surface : l'écart, la décision de `264` sur cet écart, et le contrôle contre ce qui est publié."""
    rendus = les_rendus_sur_le_disque(candidats, surfaces)
    tables = les_tables(candidats, rendus, surfaces)
    par = {(b["la_rangee"], b["la_colonne"]): b for b in publie["les_blocs"] if b.get("decidable")}
    E, X, D = [], [], []
    ecarts = {}
    for by, bx in sorted(candidats):
        lu = lecart_du_bloc(by, bx, candidats, tables, rendus, tau0.shape, surfaces)
        if lu is None:
            ecarts[(by, bx)] = None
            continue
        ecart, dedans, d_b = lu
        dec = la_decision(ecart, le_melange(d_b, glissade)) & dedans
        ecarts[(by, bx)] = int(dec.sum())
        E.append(err[dedans])
        X.append(ecart[dedans])
        D.append(dec[dedans])
    lus = {k for k, v in ecarts.items() if v is not None}
    differents = sorted(f"{k[0]}_{k[1]}" for k in set(par) | lus
                        if k not in par or k not in lus or ecarts[k] != par[k]["les_points_corriges"])
    r = ce_que_la_marche_lit(np.concatenate(E), np.concatenate(X), np.concatenate(D), glissade) if E else {}
    g = publie["les_reunis"]
    r["le_controle"] = {"les_blocs_lus": len(lus), "les_blocs_publies": len(par), "les_blocs_qui_different": differents,
                        "les_rates_rendus_justes_publies": g["les_rates_rendus_justes"],
                        "les_justes_rendus_rates_publies": g["les_justes_rendus_rates"]}
    r["le_controle"]["reproduit"] = bool(
        E and not differents and r["la_decision_retient"]["des_reparables"] == g["les_rates_rendus_justes"]
        and r["la_decision_retient"]["des_cassables"] == g["les_justes_rendus_rates"])
    return r


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : l'écart relu ne redonne pas la décision publiée"}
    s, b = (r[k]["la_part_des_rates_que_la_marche_repare"] for k in ("le_segment", "la_bande"))
    if b >= s:
        return {"lissue": "la marche lit les ratés de la bande aussi bien que ceux du segment : ce qui manque est le choix"}
    return {"lissue": "la marche lit moins bien les ratés de la bande que ceux du segment"}


def mesurer() -> dict:
    debut = time.monotonic()
    d275, d281 = json.loads(CE_QUE_275_A_PUBLIE.read_text()), json.loads(CE_QUE_281_A_PUBLIE.read_text())
    tau0, err, glissade, candidats = le_segment()
    out = {"le_segment": lire_une_surface(tau0, err, glissade, candidats, LES_SURFACES, d275)}
    plan = lire_le_plan()
    tb = np.load(LE_PREMIER_SAUT)
    eb = tb - np.load(LES_COUCHES_DE_LA_BANDE)[..., 0]
    out["la_bande"] = lire_une_surface(tb, eb, float(d281["la_glissade_voxels"]), plan["candidats"],
                                       LES_SURFACES_DE_LA_BANDE, d281)
    out["decidable"] = bool(out["le_segment"]["le_controle"]["reproduit"] and out["la_bande"]["le_controle"]["reproduit"])
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

    h = DEMI_PAS_EN_VOXELS
    err = np.array([72.0, 72.0, -72.0, 5.0, 5.0, np.nan, 72.0])
    ecart = np.array([70.0, 0.0, -70.0, 0.0, 72.0, 72.0, np.nan])
    dec = np.array([True, False, True, False, True, True, True])
    r = ce_que_la_marche_lit(err, ecart, dec, 69.458)
    v("★★★★ un raté est réparable si l'écart lu le ramène à moins d'un demi-feuillet, et seulement alors",
      r["les_rates"] == 3 and r["les_rates_reparables"] == 2 and r["la_part_des_rates_que_la_marche_repare"] == 0.6667,
      str(r))
    v("★★★★ un juste est cassable si l'écart lu l'éloigne d'un demi-feuillet ou plus",
      r["les_justes"] == 2 and r["les_justes_cassables"] == 1 and r["la_part_des_justes_que_la_marche_casse"] == 0.5)
    v("★★★ un point sans erreur notée ou sans écart lu ne compte pas", r["les_points_notes"] == 5)
    hc = np.array(r["lhistogramme"]["les_comptes"])
    i = lambda val: int(np.searchsorted(LES_BORDS, val, side="right")) - 1  # noqa: E731
    v("★★★ l'histogramme compte chaque point noté une fois, l'erreur en ligne et l'écart en colonne",
      hc.sum() == 5 and hc[i(72.0), i(70.0)] == 1 and hc[i(72.0), i(0.0)] == 1 and hc[i(5.0), i(72.0)] == 1,
      str(hc.sum()))
    v("★★ ce qui dépasse l'histogramme est compté à son bord",
      np.array(ce_que_la_marche_lit(np.array([500.0]), np.array([-500.0]), np.array([False]), 1.0)
               ["lhistogramme"]["les_comptes"])[-1, 0] == 1)
    v("★★★ trop loin et trop près se lisent au signe de l'erreur",
      r["la_part_reparable_des_rates_trop_loin"] == 0.5 and r["la_part_reparable_des_rates_trop_pres"] == 1.0)
    v("★★★★ la décision retient ses réparables et ses cassables, qui sont ses ratés rendus justes et justes rendus ratés",
      r["la_decision_retient"] == {"des_reparables": 2, "des_cassables": 1, "en_tout": 3}, str(r["la_decision_retient"]))
    v("★★ au demi-feuillet exact, un raté ramené à zéro est réparable",
      ce_que_la_marche_lit(np.array([h]), np.array([h]), np.array([False]), 1.0)["les_rates_reparables"] == 1)

    # L'écart relu est celui que la décision de 275 lit : sur des profondeurs tirées au hasard, la même décision.
    rng = np.random.default_rng(3)
    c = LE_BLOC
    prod = rng.normal(0, 30, (3 * c, 3 * c))
    red = rng.normal(0, 30, (3 * c, 3 * c))
    prod[c + 4:c + 9, c + 2:c + 12] += 72.0
    forme = (360, 360)
    tau0 = rng.normal(72, 10, forme)
    errf = rng.normal(0, 20, forme)
    lu = lecart_des_profondeurs(prod, red, 16, 16, forme)
    ref = la_decision_du_bloc(tau0, errf, prod, red, 16, 16, 69.458)
    v("★★★★ l'écart relu redonne la décision de 275 point pour point",
      lu is not None and ref is not None
      and np.array_equal(la_decision(lu[0], le_melange(lu[2], 69.458)) & lu[1], ref[1]) and ref[1].any(),
      str(None if ref is None else int(ref[1].sum())))
    v("★★★ sans voisin qui se relie, pas d'écart",
      lecart_des_profondeurs(np.pad(np.full((c, c), 1.0), c, constant_values=np.nan),
                             np.pad(np.zeros((c, c)), c, constant_values=np.nan), 16, 16, forme) is None)

    s = {"la_part_des_rates_que_la_marche_repare": 0.3}
    v("★★★★ les issues : aussi bien si la bande répare au moins autant, sinon moins bien, indécidable sans contrôle",
      "aussi bien" in le_verdict({"decidable": True, "le_segment": s, "la_bande": dict(s)})["lissue"]
      and "moins bien" in le_verdict({"decidable": True, "le_segment": s,
                                      "la_bande": {"la_part_des_rates_que_la_marche_repare": 0.2999}})["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
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
    texte = json.dumps(r, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
        print(f"écrit : {a.json}")
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
