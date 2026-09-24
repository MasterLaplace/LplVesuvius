"""Revenir d'où l'on vient trahit-il le saut raté ?

⭐⭐⭐⭐ LA QUESTION DE `248`, PRISE PAR L'AUTRE BOUT. La chaîne perd de 0,09 à 0,14 des points à chaque saut, et un
saut raté est définitif. Pour qu'une machine remplace l'humain qui corrige, il faut qu'elle sache OÙ elle a raté, sans
juge. Le contrôle le moins cher qui soit : faire le saut, puis le saut inverse depuis la surface produite. Là où le
retour ne retombe pas sur le segment, un des deux sauts a raté, et la machine le sait seule.

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE. L'aller est le premier saut de `248` (la feuille suivante, puis le vote), le
retour est le même saut, parti de la surface produite, le long de sa normale retournée. Un point est INCOHÉRENT si le
retour tombe à un demi-feuillet ou plus du segment, le long de la normale du segment. Le juge de l'aller est la couche que
la bande porte elle-même, celle de `248`. La mesure est la table de confusion : la part des ratés que le retour signale,
la part des points justes qu'il signale à tort, et la part juste parmi ceux qu'il garde.

⚠⚠ CE QUE LE RETOUR NE PEUT PAS VOIR, écrit avant de mesurer : une feuille que la prédiction manque est manquée dans les
deux sens, donc un aller qui saute une spire revient sur le segment en la sautant encore. Le retour ne signale que les
ratés qui ne sont pas symétriques, comme un saut qui n'a pas quitté sa feuille. C'est asserté sur une prédiction fabriquée.

Usage :
    uv run python src/nappe/le_retour_trahit_il_le_saut_rate.py --verifier
    uv run python src/nappe/le_retour_trahit_il_le_saut_rate.py --json docs/mesures/le_retour_trahit_il_le_saut_rate.json
    uv run python src/nappe/le_retour_trahit_il_le_saut_rate.py --segment 20230702185753 \\
        --json docs/mesures/le_retour_sur_le_segment_5753.json
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

from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, PAS_EN_VOXELS,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS, enchainer,  # noqa: E402
                                                       les_couches_ordonnees, lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LES_PREDICTIONS,  # noqa: E402
                                                         le_facteur, lecteur_du_depot)


def aller_retour(p: np.ndarray, n: np.ndarray, cote: float, lire_rayon, sur_la_grille, gi, gj) -> dict:
    """L'aller de `248`, puis le retour depuis la surface produite, le long de sa normale retournée.

    Rend la profondeur de l'aller et celle du retour le long de la normale du segment, et la cohérence : le retour
    tombe à moins d'un demi-feuillet du segment."""
    aller = enchainer(p, n, cote, 1, lire_rayon, sur_la_grille, gi, gj, True)[0]
    retour = enchainer(aller["q"], aller["n"], -cote, 1, lire_rayon, sur_la_grille, gi, gj, True)[0]
    le_retour = np.einsum("ij,ij->i", retour["q"] - p, n)
    return {"aller": np.einsum("ij,ij->i", aller["q"] - p, n), "retour": le_retour,
            "coherent": np.abs(le_retour) < DEMI_PAS_EN_VOXELS, "le_pas_de_laller": aller["le_pas"]}


def la_confusion(bon: np.ndarray, coherent: np.ndarray, note: np.ndarray) -> dict:
    """La table de confusion du retour contre le juge, sur les points notés."""
    b, c = bon[note], coherent[note]
    rate = ~b
    out = {"les_points_notes": int(note.sum()), "les_justes": int(b.sum()), "les_rates": int(rate.sum()),
           "les_signales": int((~c).sum()),
           "la_part_juste_a_laller": round(float(b.mean()), 4) if note.any() else None}
    out["la_part_des_rates_signales"] = round(float((~c)[rate].mean()), 4) if rate.any() else None
    out["la_part_des_justes_signales_a_tort"] = round(float((~c)[b].mean()), 4) if b.any() else None
    out["la_part_ratee_parmi_les_signales"] = round(float(rate[~c].mean()), 4) if (~c).any() else None
    out["la_part_gardee"] = round(float(c.mean()), 4) if note.any() else None
    out["la_part_juste_parmi_les_gardes"] = round(float(b[c].mean()), 4) if c.any() else None
    return out


def les_rates_par_genre(aller: np.ndarray, t_b: np.ndarray, coherent: np.ndarray, cote: float) -> dict:
    """Parmi les ratés de l'aller, trop près et trop loin : combien le retour en signale."""
    note = np.isfinite(t_b)
    with np.errstate(invalid="ignore"):
        err = cote * (aller - t_b)
    out = {}
    for nom, m in (("trop_pres", note & (err <= -DEMI_PAS_EN_VOXELS)), ("trop_loin", note & (err >= DEMI_PAS_EN_VOXELS))):
        out[nom] = {"combien": int(m.sum()),
                    "la_part_signalee": round(float((~coherent)[m].mean()), 4) if m.any() else None}
    return out


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI, segment: str = LA_BANDE,
            rangees: tuple[float, float] | None = LA_TRANCHE) -> dict:
    debut = time.monotonic()
    d = telecharger(segment, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    if rangees is not None:
        h = ref.shape[0]
        a, b = int(h * rangees[0]), int(h * rangees[1])
        ref, valide = ref[a:b], valide[a:b]
    couches = les_couches_ordonnees(ref, valide, esp, maille, LES_SAUTS)["les_cartes"]
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    forme = np.full(ok.shape, np.nan)[::maille, ::maille].shape
    gi, gj = ii // maille, jj // maille

    def sur_la_grille(val):
        c = np.full(forme, np.nan)
        c[gi, gj] = val
        return c

    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None, "la_maille": maille,
           "les_points": int(len(p)), "les_predictions": {}}
    for nom_p, (chemin, niveau) in LES_PREDICTIONS.items():
        facteur, pred = le_facteur(chemin, niveau, delai)
        lire, stats = lecteur_du_depot(pred, cache, nom_p, chemin, niveau, delai)

        def lire_rayon(q, nq, cote, portee):
            return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

        r = {}
        for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
            t_b = couches[cote_][gi, gj, 0]
            ar = aller_retour(p, n, cote, lire_rayon, sur_la_grille, gi, gj)
            ancien = cache / f"transfert_suivante_{segment}_{nom_p}_{nom}.npy"
            note = np.isfinite(t_b)
            with np.errstate(invalid="ignore"):
                bon = np.abs(ar["aller"] - t_b) < DEMI_PAS_EN_VOXELS
            coherent = ar["coherent"]
            r[nom] = {
                "laller_contre_247_ecart_max_voxels": (round(float(np.nanmax(np.abs(np.load(ancien)[gi, gj]
                                                                                  - ar["le_pas_de_laller"]))), 4)
                                                       if ancien.exists() else None),
                "la_part_coherente_sur_tous_les_points": round(float(coherent.mean()), 4),
                "le_retour_median_voxels": round(float(np.median(np.abs(ar["retour"]))), 4),
                "la_confusion": la_confusion(bon, coherent, note),
                "les_rates_par_genre": les_rates_par_genre(ar["aller"], t_b, coherent, cote),
                "le_retour_des_incoherents_en_pas": {
                    k: round(float(np.percentile(ar["retour"][~coherent] / PAS_EN_VOXELS, q)), 4)
                    for k, q in (("q25", 25), ("mediane", 50), ("q75", 75))} if (~coherent).any() else None}
        r["la_lecture"] = {"chunks_lus": stats["lus"], "combien_de_pannes": len(stats["pannes"]),
                           "les_pannes": stats["pannes"][:20]}
        out["les_predictions"][nom_p] = r
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(not r["la_lecture"]["combien_de_pannes"] for r in out["les_predictions"].values())
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points, {r['les_secondes']} s")
    for nom_p, rp in r["les_predictions"].items():
        for nom in ("du_cote_plus", "du_cote_moins"):
            x = rp[nom]
            print(f"— {nom_p} {nom} : aller contre 247 {x['laller_contre_247_ecart_max_voxels']}, cohérents "
                  f"{x['la_part_coherente_sur_tous_les_points']}, retour médian {x['le_retour_median_voxels']} vx")
            print(f"    {x['la_confusion']}")
            print(f"    par genre {x['les_rates_par_genre']}   retour des incohérents {x['le_retour_des_incoherents_en_pas']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LA TABLE DE CONFUSION : deux justes dont un signalé, deux ratés dont un signalé, un point non noté.
    bon = np.array([True, True, True, False, False, True])
    coh = np.array([True, True, False, False, False, False])
    note = np.array([True, True, True, True, True, False])
    c = la_confusion(bon, coh, note)
    v("★★★★ un point non noté ne compte pas", c["les_points_notes"] == 5 and c["les_signales"] == 3, str(c))
    v("★★★★ les deux ratés sont signalés, un juste sur trois à tort",
      c["la_part_des_rates_signales"] == 1.0 and c["la_part_des_justes_signales_a_tort"] == round(1 / 3, 4), str(c))
    v("★★★ parmi les signalés, deux sur trois sont ratés ; tous les gardés sont justes",
      c["la_part_ratee_parmi_les_signales"] == round(2 / 3, 4) and c["la_part_juste_parmi_les_gardes"] == 1.0
      and c["la_part_gardee"] == 0.4, str(c))
    g = les_rates_par_genre(np.array([72.0, 20.0, 150.0, 72.0]), np.array([72.0, 72.0, 72.0, np.nan]),
                            np.array([True, False, True, True]), 1.0)
    v("★★★ un raté trop près signalé, un raté trop loin non signalé",
      g["trop_pres"] == {"combien": 1, "la_part_signalee": 1.0} and g["trop_loin"] == {"combien": 1, "la_part_signalee": 0.0},
      str(g))
    gm = les_rates_par_genre(-np.array([72.0, 20.0, 150.0, 72.0]), -np.array([72.0, 72.0, 72.0, np.nan]),
                             np.array([True, False, True, True]), -1.0)
    v("★★ de l'autre côté, les mêmes genres", gm == g, str(gm))

    # ⭐⭐⭐⭐ L'ALLER ET LE RETOUR, sur une prédiction fabriquée : quatre feuilles planes à 80 voxels.
    f = 4
    pred = {"shape": [128, 32, 32], "chunks": [16, 16, 16], "fill_value": 0}
    vol = np.zeros(pred["shape"], np.uint8)
    zs = [10, 30, 50, 70]
    for z in zs:
        vol[z, :, :] = 255

    def lire(c_):
        a0 = np.asarray(c_) * 16
        return vol[a0[0]:a0[0] + 16, a0[1]:a0[1] + 16, a0[2]:a0[2] + 16]

    def lire_rayon(q, nq, cote, portee):
        return lire_le_rayon(q, nq, cote, portee, f, pred, lire)

    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))

    def grille_(val):
        c_ = np.full((H, W), np.nan)
        c_[gi_, gj_] = val
        return c_

    nor = np.tile([0.0, 0.0, 1.0], (H * W, 1))

    def segment(z_maillage):
        return np.stack([gj_ * 8.0 + 20.0, gi_ * 8.0 + 20.0, np.full(H * W, z_maillage)], axis=-1)

    sur = segment(30 * f + 2.0)
    ar = aller_retour(sur, nor, 1.0, lire_rayon, grille_, gi_, gj_)
    v("★★★★ posé sur sa feuille, l'aller va à la suivante", np.allclose(ar["aller"], 80.0, atol=f), str(np.median(ar["aller"])))
    v("★★★★ et le retour retombe sur le segment : le point est cohérent", ar["coherent"].all(), str(np.median(ar["retour"])))
    ar_m = aller_retour(sur, nor, -1.0, lire_rayon, grille_, gi_, gj_)
    v("★★★ de l'autre côté aussi", np.allclose(ar_m["aller"], -80.0, atol=f) and np.all(np.abs(ar_m["retour"]) < DEMI_PAS_EN_VOXELS),
      f"{np.median(ar_m['aller'])} {np.median(ar_m['retour'])}")
    # ⚠⚠⚠ UN SAUT QUI NE QUITTE PAS SA FEUILLE : le segment posé vingt voxels devant elle la prend pour la suivante ;
    # le retour, lui, la reconnaît et va à la spire d'avant. Le retour le signale.
    devant = segment(30 * f - 20.0)
    ad = aller_retour(devant, nor, 1.0, lire_rayon, grille_, gi_, gj_)
    v("★★★★ un aller qui reste sur sa feuille n'avance pas d'un demi-feuillet", np.all(np.abs(ad["aller"]) < DEMI_PAS_EN_VOXELS),
      str(np.median(ad["aller"])))
    v("★★★★ et le retour, parti de là, tombe à la spire d'avant : le point est signalé",
      not ad["coherent"].any(), str(np.median(ad["retour"])))
    # ⚠⚠⚠ LA TACHE AVEUGLE, DÉCLARÉE : sans la deuxième feuille, l'aller saute une spire et le retour la saute aussi.
    vol[50, :, :] = 0
    am = aller_retour(sur, nor, 1.0, lire_rayon, grille_, gi_, gj_)
    v("★★★★ une feuille manquée dans la prédiction fait sauter une spire à l'aller",
      np.allclose(am["aller"], 160.0, atol=f), str(np.median(am["aller"])))
    v("★★★★ et le retour la saute aussi : le raté n'est PAS signalé", am["coherent"].all(), str(np.median(am["retour"])))
    vol[50, :, :] = 255

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} ({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--delai", type=float, default=DELAI)
    p.add_argument("--segment", default=LA_BANDE)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    rangees = LA_TRANCHE if a.segment == LA_BANDE else None
    r = mesurer(LE_CACHE, LA_MAILLE, a.delai, a.segment, rangees)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
