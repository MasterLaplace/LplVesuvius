"""Les ratés du deuxième saut viennent-ils du premier ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LES RATÉS DU DEUXIÈME SAUT NE SOIENT RANGÉS. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `276` publient. `276` fait repartir la chaîne de `248` de la spire corrigée de `275` : au deuxième saut, 52
ratés rendus justes pour 27 justes rendus ratés, et la part sur la bonne spire passe de 0,8875 à 0,889. Des 65 points dont la
spire corrigée rend le premier saut juste, un peu moins de la moitié retombent juste au deuxième.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain doit dire à chaque saut ce qu'il faut corriger.
Si les ratés du deuxième saut viennent du premier, corriger le premier suffit à la chaîne. S'ils viennent du deuxième saut
lui-même, chaque saut demande sa propre correction, et la procédure de `265` doit tourner à chaque spire.

## Ce qui est rangé

Les deux chaînes de `276`, refaites telles quelles : le témoin, parti du segment, et la chaîne partie de la spire corrigée.
Sur les points notés aux deux premiers sauts, par le juge de `248`, un raté du deuxième saut est :
- HÉRITÉ si le premier saut de la même chaîne était raté ;
- PROPRE si le premier saut était juste.
Un raté propre est rangé à côté : trop près ou trop loin de la deuxième couche, retombé sur la première, ou d'un saut qui
n'avance pas d'un demi-feuillet.

⚠ Les deux chaînes doivent redonner `276` au deuxième saut, compte pour compte, et le premier saut du témoin la spire produite ;
sinon la mesure est indécidable.

## Les issues, exclusives, sur la chaîne partie de la spire corrigée

- les ratés propres sont plus nombreux que les ratés hérités : le deuxième saut rate surtout de lui-même, et chaque saut
  demande sa correction ;
- ils ne le sont pas : le deuxième saut rate surtout parce que le premier a raté.

⚠ Rapporté à côté : le même rangement pour le témoin ; les points notés au deuxième saut seulement, que rien ne range ; les
ratés rendus justes et les justes rendus ratés du deuxième saut, selon que le premier saut a changé ou non.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : pourquoi un saut parti d'un point juste rate ; une correction du deuxième saut.

Usage :
    uv run python src/nappe/les_rates_du_deuxieme_saut_viennent_ils_du_premier.py --verifier
    uv run python src/nappe/les_rates_du_deuxieme_saut_viennent_ils_du_premier.py \\
        --json docs/mesures/les_rates_du_deuxieme_saut_viennent_ils_du_premier.json
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

from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import (DEMI_PAS_EN_VOXELS,  # noqa: E402
                                                                                LE_SIGNE, le_bilan_du_saut,
                                                                                les_deux_chaines, les_justes)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_276_A_PUBLIE = LES_MESURES / "repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.json"


def les_origines(t1: np.ndarray, t2: np.ndarray, v1: np.ndarray, v2: np.ndarray, pas2: np.ndarray,
                 cote: float = LE_SIGNE) -> dict:
    """Les ratés du deuxième saut d'une chaîne, sur les points notés aux deux sauts : hérités ou propres."""
    note = np.isfinite(v1) & np.isfinite(v2)
    j1, j2 = les_justes(t1, v1), les_justes(t2, v2)
    rate = note & ~j2
    herite, propre = rate & ~j1, rate & j1
    with np.errstate(invalid="ignore"):
        err = cote * (t2 - v2)
        propres = {"trop_pres": int((propre & (err <= -DEMI_PAS_EN_VOXELS)).sum()),
                   "trop_loin": int((propre & (err >= DEMI_PAS_EN_VOXELS)).sum()),
                   "retombes_sur_la_premiere_couche": int((propre & (np.abs(t2 - v1) < DEMI_PAS_EN_VOXELS)).sum()),
                   "dun_saut_qui_navance_pas": int((propre & (np.abs(pas2) < DEMI_PAS_EN_VOXELS)).sum())}
    return {"les_points_notes_aux_deux_sauts": int(note.sum()),
            "les_points_notes_au_deuxieme_saut_seulement": int((np.isfinite(v2) & ~np.isfinite(v1)).sum()),
            "les_rates_du_deuxieme_saut": int(rate.sum()), "les_herites": int(herite.sum()),
            "les_propres": int(propre.sum()), "parmi_les_propres": propres}


def les_changements_selon_le_premier(t2: np.ndarray, c2: np.ndarray, v2: np.ndarray, change1: np.ndarray) -> dict:
    """Les ratés rendus justes et les justes rendus ratés du deuxième saut, selon que le premier saut a changé ou non."""
    note = np.isfinite(v2)
    bt, bc = les_justes(t2, v2), les_justes(c2, v2)
    rj, jr = note & ~bt & bc, note & bt & ~bc
    return {cle: {"le_premier_saut_a_change": int((m & change1).sum()), "le_premier_saut_est_le_meme": int((m & ~change1).sum())}
            for cle, m in (("les_rates_rendus_justes", rj), ("les_justes_rendus_rates", jr))}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : les deux chaînes ne redonnent pas 276"}
    o = r["partie_de_la_spire_corrigee"]
    if o["les_propres"] > o["les_herites"]:
        return {"lissue": "le deuxième saut rate surtout de lui-même : chaque saut demande sa correction"}
    return {"lissue": "le deuxième saut rate surtout parce que le premier a raté"}


def mesurer() -> dict:
    debut = time.monotonic()
    c = les_deux_chaines()
    if isinstance(c, str):
        return {"decidable": False, "la_raison": c, "le_verdict": le_verdict({})}
    v, pt, pc = c["verite"], c["pt"], c["pc"]
    publie = json.loads(CE_QUE_276_A_PUBLIE.read_text())
    refait = le_bilan_du_saut(pt[1], pc[1], v[1])
    with np.errstate(invalid="ignore"):
        ecart = float(np.nanmax(np.abs(c["temoin"][0]["le_pas"] - c["tau0"])))
        change1 = ~(np.abs(c["tau1"] - c["tau0"]) < 1e-9)
    out = {"le_deuxieme_saut_de_276": {"publie": publie["les_sauts"][1], "refait": refait,
                                       "reproduit": refait == publie["les_sauts"][1]},
           "le_premier_saut_du_temoin_contre_la_spire_produite_ecart_max_voxels": round(ecart, 4),
           "le_temoin": les_origines(pt[0], pt[1], v[0], v[1], c["temoin"][1]["le_pas"]),
           "partie_de_la_spire_corrigee": les_origines(pc[0], pc[1], v[0], v[1], c["corrigee"][1]["le_pas"]),
           "les_changements_du_deuxieme_saut": les_changements_selon_le_premier(pt[1], pc[1], v[1], change1),
           "la_lecture": {"combien_de_pannes": len(c["stats"]["pannes"])}}
    out["decidable"] = (out["le_deuxieme_saut_de_276"]["reproduit"] and ecart == 0.0
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

    # Six points : couches à 70 puis 140 ; un point sans première couche, un sans deuxième.
    v1 = np.array([70.0, 70.0, 70.0, 70.0, np.nan, 70.0])
    v2 = np.array([140.0, 140.0, 140.0, 140.0, 140.0, np.nan])
    t1 = np.array([70.0, 140.0, 70.0, 70.0, 70.0, 70.0])      # le deuxième point rate le premier saut
    t2 = np.array([140.0, 210.0, 72.0, 215.0, 0.0, 0.0])     # rate hérité, puis deux ratés propres
    pas2 = np.array([70.0, 70.0, 2.0, 145.0, 0.0, 0.0])
    o = les_origines(t1, t2, v1, v2, pas2, 1.0)
    v("★★★★ un raté du deuxième saut est hérité si le premier a raté, propre sinon, sur les seuls points notés aux deux",
      o["les_points_notes_aux_deux_sauts"] == 4 and o["les_rates_du_deuxieme_saut"] == 3 and o["les_herites"] == 1
      and o["les_propres"] == 2, str(o))
    v("★★★ un point noté au deuxième saut seulement n'est rangé nulle part, mais il est compté",
      o["les_points_notes_au_deuxieme_saut_seulement"] == 1)
    p_ = o["parmi_les_propres"]
    v("★★★★ un raté propre resté sur la première couche est trop près et d'un saut qui n'avance pas ; l'autre est trop loin",
      p_ == {"trop_pres": 1, "trop_loin": 1, "retombes_sur_la_premiere_couche": 1, "dun_saut_qui_navance_pas": 1}, str(p_))
    om = les_origines(-t1, -t2, -v1, -v2, -pas2, -1.0)
    v("★★ de l'autre côté, trop près reste trop près", om["parmi_les_propres"]["trop_pres"] == 1)

    t2_ = np.array([140.0, 210.0, 140.0, 140.0])
    c2_ = np.array([210.0, 140.0, 140.0, 210.0])
    v2_ = np.array([140.0, 140.0, np.nan, 140.0])
    ch = les_changements_selon_le_premier(t2_, c2_, v2_, np.array([True, True, True, False]))
    v("★★★★ les changements du deuxième saut sont rangés selon que le premier saut a changé",
      ch == {"les_rates_rendus_justes": {"le_premier_saut_a_change": 1, "le_premier_saut_est_le_meme": 0},
             "les_justes_rendus_rates": {"le_premier_saut_a_change": 1, "le_premier_saut_est_le_meme": 1}}, str(ch))

    r_ = lambda p, h: {"decidable": True, "partie_de_la_spire_corrigee": {"les_propres": p, "les_herites": h}}  # noqa: E731
    v("★★★★ les issues : de lui-même si les propres sont plus nombreux, sinon hérité ; indécidable si 276 n'est pas redonné",
      "de lui-même" in le_verdict(r_(3, 2))["lissue"] and "parce que le premier" in le_verdict(r_(2, 2))["lissue"]
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
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
