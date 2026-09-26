"""Ramener chaque point sur la feuille que l'écart lu désigne corrige-t-il le deuxième saut de la bande `w028-037` ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT CETTE CORRECTION. Ce qui était vu avant d'écrire : tout ce que `248` et `257` à `288` publient.
Au deuxième saut de la bande, la décision de `264` retient 23 des 444 ratés que l'écart lu répare, et 9 des 421 justes qu'il
casse (`283`). Elle corrige 69 points, et les pose à une médiane de 36,2988 voxels de la feuille la plus proche sur le rayon du
saut : 34 à plus d'un demi-feuillet (`285`). La chaîne, elle, pose toujours ses points sur une feuille (`247`).

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `282` a montré que la marche lit les ratés et que c'est le choix qui manque.
Un glissement vrai déplace un point d'une feuille à une autre : l'écart qui le désigne doit donc mener près d'une autre feuille.
Un écart de bruit, lui, ne mène près d'aucune, ou ramène à la feuille où le point est déjà. Cette correction ne garde que les
écarts qui mènent à une autre feuille, et pose le point sur elle, comme la chaîne pose les siens.

## La correction, déclarée avant la mesure

Sur les blocs notés de `283`, pour chaque point où l'écart que la décision lit est défini :
- le rayon est celui du deuxième saut : depuis le point du premier saut, le long de sa normale, jusqu'à trois pas (`285`) ;
- la cible est la projection du point sur ce rayon, moins l'écart lu ;
- si le centre de plage de `m7` le plus proche de la cible en est à moins de 12 voxels, la distance à laquelle la chaîne
  reconnaît sa feuille (`LE_CONTROLE`), et n'est pas celui dont le point est le plus proche, le point se pose sur lui ;
- sinon, le point ne bouge pas. Aucun réglage : l'écart, les feuilles et le seuil sont ceux qui existent déjà.

⚠ Le contrôle rend la mesure décidable : sur chaque bloc noté, la décision de `264` prise sur l'écart relu redonne les points
corrigés de `283`, et, réunis, ses 23 ratés rendus justes et ses 9 justes rendus ratés. La lecture ne doit connaître aucune panne.

## Les issues, exclusives, sur les blocs notés réunis

- les ratés que cette correction rend justes sont plus nombreux que les justes qu'elle rend ratés : ramener sur la feuille que
  l'écart désigne corrige le deuxième saut de la bande ;
- ils ne le sont pas : elle ne le corrige pas.

⚠ Rapporté à côté : combien de points bougent, et parmi eux combien de ratés réparables et de justes cassables ; la décision de
`283` sur les mêmes points ; le deuxième saut entier.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : le troisième saut, reparti de cette correction ; le premier saut ; le segment
`20230702185753`.

Usage :
    uv run python src/nappe/ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.py --verifier
    uv run python src/nappe/ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.py \\
        --json docs/mesures/ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.json
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

from la_marche_corrige_t_elle_la_spire_produite import la_part_juste  # noqa: E402
from la_marche_lit_elle_les_rates_de_la_bande import ce_que_la_marche_lit, lecart_du_bloc  # noqa: E402
from la_marche_sait_elle_ou_ne_pas_corriger import la_decision, le_melange  # noqa: E402
from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande import (LES_SURFACES,  # noqa: E402
                                                                                 les_profondeurs_de, lire_le_plan)
from la_procedure_sans_juge_tient_elle_sur_la_bande import LE_SIGNE, la_bande  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_la_bande import lire_le_plan as le_plan_de_281  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import les_rendus_sur_le_disque, les_tables  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import LES_SAUTS, enchainer  # noqa: E402
from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE, LE_CONTROLE, les_centres  # noqa: E402
from recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste import (  # noqa: E402
    la_feuille_la_plus_proche)
from recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste import (  # noqa: E402
    la_projection_sur_le_rayon, poser_sur_le_rayon)
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import le_bilan_du_saut  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_283_A_PUBLIE = LES_MESURES / "la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.json"
CE_QUE_261_A_PUBLIE = LES_MESURES / "la_marche_corrige_t_elle_la_spire_produite.json"


def la_feuille_que_lecart_designe(centres: list[np.ndarray], s: np.ndarray, ecart: np.ndarray,
                                  seuil: float = LE_CONTROLE) -> np.ndarray:
    """La profondeur, sur le rayon, de la feuille où l'écart mène le point ; NaN s'il ne mène près d'aucune autre feuille
    que celle dont le point est déjà le plus proche."""
    cible = s - ecart
    ici = la_feuille_la_plus_proche(centres, s)
    la = la_feuille_la_plus_proche(centres, cible)
    with np.errstate(invalid="ignore"):
        prend = np.isfinite(la) & (np.abs(la - cible) < seuil) & ~(np.abs(la - ici) < 1e-9)
    return np.where(prend, la, np.nan)


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : l'écart relu ne redonne pas la décision de 283, ou la lecture est tombée en panne"}
    if r["les_blocs_notes_reunis"]["le_gain_net"] > 0:
        return {"lissue": "ramener sur la feuille que l'écart désigne corrige le deuxième saut de la bande"}
    return {"lissue": "ramener sur la feuille que l'écart désigne ne corrige pas le deuxième saut de la bande"}


def mesurer() -> dict:
    debut = time.monotonic()
    b = la_bande()
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b, "le_verdict": le_verdict({})}
    p, n, gi, gj, v, grille = b["p"], b["n"], b["gi"], b["gj"], b["verite"], b["sur_la_grille"]
    chaine = enchainer(p, n, LE_SIGNE, LES_SAUTS, b["lire_rayon"], grille, gi, gj, True)
    tau2 = les_profondeurs_de(chaine, p, n)[1]
    q1, n1, q2 = chaine[0]["q"], chaine[0]["n"], chaine[1]["q"]
    d283 = json.loads(CE_QUE_283_A_PUBLIE.read_text())
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    plan, candidats = lire_le_plan(), le_plan_de_281()["candidats"]
    rendus = les_rendus_sur_le_disque(plan["a_rendre"], LES_SURFACES)
    tables = les_tables(plan["a_rendre"], rendus, LES_SURFACES)
    t2g = grille(tau2)
    err_g = t2g - grille(v[1])
    ecart_g, dans_g, decide_g = np.full(t2g.shape, np.nan), np.zeros(t2g.shape, bool), np.zeros(t2g.shape, bool)
    par = {(x["la_rangee"], x["la_colonne"]): x for x in d283["les_blocs"] if x.get("decidable")}
    differents = []
    for by, bx in sorted(plan["notes"]):
        lu = lecart_du_bloc(by, bx, candidats, tables, rendus, t2g.shape, LES_SURFACES)
        if lu is None:
            differents.append(f"{by}_{bx}")
            continue
        ecart, dedans, d_b = lu
        dec = la_decision(ecart, le_melange(d_b, glissade)) & dedans
        if (by, bx) not in par or int(dec.sum()) != par[(by, bx)]["les_points_corriges"]:
            differents.append(f"{by}_{bx}")
        ecart_g = np.where(dedans, ecart, ecart_g)
        dans_g |= dedans
        decide_g |= dec
    ecart_p, dans, decide = ecart_g[gi, gj], dans_g[gi, gj], decide_g[gi, gj]
    lecture = ce_que_la_marche_lit(err_g[dans_g], ecart_g[dans_g], decide_g[dans_g], glissade)
    t, vu = b["lire_rayon"](q1, n1, LE_SIGNE, LA_PORTEE)
    centres = les_centres(t, vu)
    s2 = la_projection_sur_le_rayon(q2, q1, n1)
    feuille = la_feuille_que_lecart_designe(centres, s2, np.where(dans, ecart_p, np.nan))
    bouge = np.isfinite(feuille)
    tau2n = les_profondeurs_de([{"q": poser_sur_le_rayon(q2, q1, n1, feuille, bouge)}], p, n)[0]
    lue = ce_que_la_marche_lit(err_g[dans_g], ecart_g[dans_g], grille(bouge.astype(float))[dans_g] > 0.5, glissade)
    bilan_blocs = le_bilan_du_saut(tau2, tau2n, np.where(dans, v[1], np.nan))
    out = {"les_blocs_notes": len(plan["notes"]), "les_blocs_qui_different_de_283": differents,
           "la_decision_de_283_refaite": {"des_reparables": lecture["la_decision_retient"]["des_reparables"],
                                          "des_cassables": lecture["la_decision_retient"]["des_cassables"],
                                          "en_tout": int(decide.sum())},
           "la_decision_de_283_publiee": {"des_reparables": d283["les_reunis"]["les_rates_rendus_justes"],
                                          "des_cassables": d283["les_reunis"]["les_justes_rendus_rates"],
                                          "en_tout": d283["les_reunis"]["les_points_corriges"]},
           "les_points_ou_lecart_est_lu": int(dans.sum()),
           "les_points_qui_bougent": int(bouge.sum()),
           "parmi_eux": {"des_reparables": lue["la_decision_retient"]["des_reparables"],
                         "des_cassables": lue["la_decision_retient"]["des_cassables"],
                         "les_reparables_en_tout": lue["les_rates_reparables"],
                         "les_cassables_en_tout": lue["les_justes_cassables"]},
           "les_blocs_notes_reunis": {**bilan_blocs, "avant": la_part_juste(tau2, v[1], dans),
                                      "apres": la_part_juste(tau2n, v[1], dans)},
           "le_deuxieme_saut_entier": le_bilan_du_saut(tau2, tau2n, v[1]),
           "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    out["decidable"] = (not differents and out["la_decision_de_283_refaite"] == out["la_decision_de_283_publiee"]
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

    c = [np.array([72.0, 144.0])] * 5 + [np.empty(0)]
    s = np.array([144.0, 144.0, 144.0, 144.0, 144.0, 144.0])
    e = np.array([70.0, 50.0, 5.0, np.nan, -70.0, 70.0])
    f = la_feuille_que_lecart_designe(c, s, e)
    v("★★★★ un écart qui mène à moins de 12 voxels d'une autre feuille y pose le point",
      f[0] == 72.0, str(f))
    v("★★★★ un écart qui ne mène près d'aucune feuille ne déplace rien", np.isnan(f[1]) and np.isnan(f[4]), str(f))
    v("★★★ un petit écart qui ramène à la feuille où le point est déjà ne déplace rien", np.isnan(f[2]))
    v("★★★ sans écart lu, ou sans feuille sur le rayon, rien ne bouge", np.isnan(f[3]) and np.isnan(f[5]))
    v("★★ le seuil est la distance où la chaîne reconnaît sa feuille", LE_CONTROLE == 12.0)

    r_ = lambda g: {"decidable": True, "les_blocs_notes_reunis": {"le_gain_net": g}}  # noqa: E731
    v("★★★★ les issues : corrige si le gain net est positif, sinon non, indécidable sans contrôle",
      "ne corrige pas" not in le_verdict(r_(1))["lissue"] and "ne corrige pas" in le_verdict(r_(0))["lissue"]
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
