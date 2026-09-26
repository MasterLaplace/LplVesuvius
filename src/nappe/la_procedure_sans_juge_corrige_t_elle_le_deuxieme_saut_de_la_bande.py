"""La procédure sans juge de `265` corrige-t-elle le deuxième saut de la bande `w028-037` ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PILE DU DEUXIÈME SAUT DE LA BANDE NE SOIT RENDUE. Ce qui était vu avant d'écrire :
tout ce que `248` et `257` à `282` publient. Sur le segment `20230702185753`, la procédure corrige le deuxième saut (`280`, un
gain net de 51). Sur la bande, elle n'améliore pas le premier (`281`, −10) ; la marche y lit pourtant les ratés, et c'est le
choix qui ne les retient pas (`282`). Les ratés du premier saut de la bande sont à moins d'un pas, quand la décision cherche des
glissements d'un pas (`282`, vu après coup). Au deuxième saut, la chaîne de `248` sur la bande rate 0,1913 des points notés,
dont 0,1452 trop près.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain doit corriger chaque saut, et la bande est le seul
juge de ce dépôt qui note au-delà du deuxième. La procédure y est éprouvée là où elle a marché sur le segment : au deuxième
saut.

## La procédure, celle de `280`, sans rien y changer

Elle compare la marche du deuxième saut à celle de la surface d'où il part. Cette surface est le premier saut de la bande, celui
que `281` a rendu, non corrigé : `281` a montré que sa correction ne l'améliore pas. Une glissade que le premier saut a déjà se
retrouve dans les deux marches et s'annule. Le reste est `265` : l'ancre prise sur les voisins, la décision de `264` avec la
glissade de `261`, une passe, les pas calculés bloc par bloc, les piles rendues depuis le miroir local. La correction pousse la
profondeur du deuxième saut, le long de la normale de la bande, de l'écart que la décision retient. Le juge est la deuxième
couche de la bande, et il ne sert qu'à noter.

⚠ Les blocs sont les blocs candidats de `281` où le juge note au moins un point au deuxième saut ; leurs voisins candidats sont
rendus aussi. Les piles du premier saut sont celles de `281`, et ne sont pas refaites.

⚠ Trois contrôles rendent la mesure décidable :
- la chaîne redonne `248` sur la bande, saut par saut, compte pour compte ;
- son premier saut est celui dont `281` a rendu les piles ;
- les deux blocs notés qui portent le plus de points au deuxième saut sont rendus à distance sur la surface neuve, puis depuis
  le miroir : les deux piles doivent être identiques voxel pour voxel.
Il ne doit manquer aucune pile, et la lecture ne doit connaître aucune panne.

## Les issues, exclusives, sur les blocs décidés réunis

- les ratés rendus justes sont plus nombreux que les justes rendus ratés : la procédure sans juge corrige le deuxième saut de
  la bande ;
- ils ne le sont pas : elle ne le corrige pas.

⚠ Rapporté à côté : bloc par bloc, ce que la décision corrige ; le deuxième saut entier, avant et après ; la part de ses points
notés que les blocs couvrent ; et, comme `282`, les ratés que la marche répare et les justes qu'elle casse, et ce que la décision
en retient.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : le troisième saut, reparti du deuxième corrigé ; un recalage sur la feuille ; un autre
côté, une autre prédiction.

Usage :
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py --verifier
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py --preparer
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py --controler 2
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py --rendre 3
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py --pas 5
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py \\
        --json docs/mesures/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

from la_marche_corrige_t_elle_la_spire_produite import la_part_juste  # noqa: E402
from la_marche_lit_elle_les_rates_de_la_bande import ce_que_la_marche_lit, lecart_du_bloc  # noqa: E402
from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut import (le_maillage_des_points,  # noqa: E402
                                                                    les_blocs_a_rendre, les_blocs_du_controle,
                                                                    les_blocs_notes)
from la_procedure_sans_juge_tient_elle_sur_la_bande import (CE_QUE_248_A_PUBLIE, LE_CACHE,  # noqa: E402
                                                            LE_PREMIER_SAUT, LE_SIGNE, LE_SUFFIXE,
                                                            LES_SURFACES_DE_LA_BANDE, la_bande,
                                                            la_reproduction_de_248)
from la_procedure_sans_juge_tient_elle_sur_la_bande import lire_le_plan as le_plan_de_281  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (CE_QUE_261_A_PUBLIE,  # noqa: E402
                                                                     calculer_les_pas, la_reunion,
                                                                     le_controle_du_miroir, les_rendus_sur_le_disque,
                                                                     les_tables, tout_rendre, un_bloc)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_DOSSIER, ecrire_tifxyz, le_cadre, rendre)
from le_transfert_enchaine_tient_il_les_spires import LES_SAUTS, enchainer  # noqa: E402

# La référence, le premier saut que `281` a rendu, puis la surface produite, le deuxième saut.
LES_SURFACES = (LES_SURFACES_DE_LA_BANDE[1], "le_deuxieme_saut_de_la_bande")
LE_DEUXIEME_SAUT = LE_CACHE / f"deuxieme_saut_de_la_bande_{LE_SUFFIXE}.npy"
LA_COUCHE_DEUX = LE_CACHE / f"couche_deux_de_la_bande_{LE_SUFFIXE}.npy"
LE_DEUXIEME_SAUT_CORRIGE = LE_CACHE / f"deuxieme_saut_de_la_bande_corrige_265_{LE_SUFFIXE}.npy"
LE_PLAN = LE_DOSSIER / "le_deuxieme_saut_de_la_bande_plan.json"
LE_CONTROLE = LE_DOSSIER / "le_deuxieme_saut_de_la_bande_controle.json"


def les_profondeurs_de(chaine: list[dict], p: np.ndarray, n: np.ndarray) -> list[np.ndarray]:
    """La profondeur de chaque saut, le long de la normale de la bande, depuis la bande."""
    return [np.einsum("ij,ij->i", s["q"] - p, n) for s in chaine]


def la_reference_est_celle_de_281(tau0: np.ndarray, sauve: np.ndarray) -> bool:
    """Le premier saut refait est-il, point pour point, celui dont `281` a rendu les piles ?"""
    return tau0.shape == sauve.shape and bool(np.array_equal(tau0, sauve, equal_nan=True))


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la chaîne ne redonne pas 248 ou le premier saut de 281, le miroir ne redonne pas les "
                          "piles rendues à distance, il manque une pile, ou la lecture est tombée en panne"}
    if r["les_reunis"]["le_gain_net"] > 0:
        return {"lissue": "la procédure sans juge corrige le deuxième saut de la bande"}
    return {"lissue": "la procédure sans juge ne corrige pas le deuxième saut de la bande"}


# ── LES ÉTAPES ─────────────────────────────────────────────────────────────────────────────────────────────────────

def preparer(cache: Path = LE_CACHE) -> dict:
    """La chaîne de `248` sur la bande, la surface du deuxième saut à rendre, son juge et les blocs."""
    b = la_bande(cache)
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b}
    p, n, gi, gj, grille = b["p"], b["n"], b["gi"], b["gj"], b["sur_la_grille"]
    chaine = enchainer(p, n, LE_SIGNE, LES_SAUTS, b["lire_rayon"], grille, gi, gj, True)
    taus = les_profondeurs_de(chaine, p, n)
    publie = json.loads(CE_QUE_248_A_PUBLIE.read_text())["les_predictions"][LA_PREDICTION][LE_COTE]["les_sauts"]
    q2 = np.stack([grille(chaine[1]["q"][:, a]) for a in range(3)], axis=-1)
    p2, v2 = le_maillage_des_points(q2)
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES[1] / "maillage", p2, v2, 1.0 / (b["esp"] * LA_MAILLE), LES_SURFACES[1])
    couche = grille(b["verite"][1])
    np.save(LE_DEUXIEME_SAUT, grille(taus[1]))
    np.save(LA_COUCHE_DEUX, couche)
    candidats = le_plan_de_281()["candidats"]
    notes = les_blocs_notes(couche, candidats)
    plan = {"la_reproduction_de_248": la_reproduction_de_248(taus, b["verite"], publie),
            "la_reference_est_celle_de_281": la_reference_est_celle_de_281(grille(taus[0]), np.load(LE_PREMIER_SAUT)),
            "les_blocs_notes": {f"{k[0]}_{k[1]}": x for k, x in notes.items()},
            "les_blocs_a_rendre": sorted(f"{k[0]}_{k[1]}" for k in les_blocs_a_rendre(notes, candidats)),
            "les_blocs_du_controle": [f"{k[0]}_{k[1]}" for k in les_blocs_du_controle(notes)],
            "les_points_de_la_surface": int(v2.sum()),
            "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire_le_plan() -> dict:
    d = json.loads(LE_PLAN.read_text())
    bloc = lambda s: tuple(int(x) for x in s.split("_"))  # noqa: E731
    return {"notes": {bloc(k): v for k, v in d["les_blocs_notes"].items()},
            "a_rendre": {bloc(k) for k in d["les_blocs_a_rendre"]},
            "controle": [bloc(k) for k in d["les_blocs_du_controle"]], "brut": d}


def controler(ouvriers: int = 2) -> dict:
    """Les piles du contrôle sur la surface neuve, rendues à distance puis depuis le miroir, comparées voxel pour voxel."""
    plan = lire_le_plan()
    taches = [(LES_SURFACES[1], by, bx) for by, bx in plan["controle"]]

    def a_distance(t_):
        s, by, bx = t_
        return t_, rendre(LE_DOSSIER / s / "maillage", LE_DOSSIER / s / f"bloc_{by}_{bx}", le_cadre(by, bx, LE_BLOC))

    with ThreadPoolExecutor(max_workers=int(ouvriers)) as pool:
        distance = dict(pool.map(a_distance, taches))
    r = {"a_distance": {f"{s}_{by}_{bx}": x for (s, by, bx), x in distance.items()}}
    r["le_miroir"] = le_controle_du_miroir(min(int(ouvriers), 3), tuple(taches))
    r["identiques"] = bool(r["le_miroir"]["identiques"])
    LE_CONTROLE.write_text(json.dumps(r, ensure_ascii=False, indent=1))
    return r


def mesurer(pas_ouvriers: int = 5) -> dict:
    debut = time.monotonic()
    plan = lire_le_plan()
    brut = plan["brut"]
    controle = json.loads(LE_CONTROLE.read_text()) if LE_CONTROLE.is_file() else {"identiques": False}
    glissade = float(json.loads(CE_QUE_261_A_PUBLIE.read_text())["le_signe"]["lecart_retrouve_voxels"])
    candidats = le_plan_de_281()["candidats"]
    tau2, couche = np.load(LE_DEUXIEME_SAUT), np.load(LA_COUCHE_DEUX)
    err = tau2 - couche
    out = {"la_glissade_voxels": glissade, "les_blocs_notes": len(plan["notes"]),
           "les_blocs_rendus_en_tout": len(plan["a_rendre"]), "la_reproduction_de_248": brut["la_reproduction_de_248"],
           "la_reference_est_celle_de_281": brut["la_reference_est_celle_de_281"],
           "le_controle_du_miroir": {"les_blocs": brut["les_blocs_du_controle"], "identiques": controle["identiques"],
                                     "les_piles": {k: x.get("les_voxels_differents") for k, x in
                                                   controle.get("le_miroir", {}).get("les_piles", {}).items()}}}
    out["les_pas"] = calculer_les_pas(plan["a_rendre"], pas_ouvriers, True, LES_SURFACES)
    rendus = les_rendus_sur_le_disque(plan["a_rendre"], LES_SURFACES)
    out["les_piles_manquantes"] = sorted(f"{s}_{by}_{bx}" for (s, by, bx), ok in rendus.items() if not ok)
    tables = les_tables(plan["a_rendre"], rendus, LES_SURFACES)
    blocs, tau2c, E, X, D = [], tau2.copy(), [], [], []
    for by, bx in sorted(plan["notes"]):
        b_, corr = un_bloc(by, bx, candidats, tables, rendus, tau2, err, glissade, LES_SURFACES)
        blocs.append(b_)
        if corr is None:
            continue
        masque, t_ = corr
        tau2c[masque] = t_[masque]
        ecart, dedans, _ = lecart_du_bloc(by, bx, candidats, tables, rendus, tau2.shape, LES_SURFACES)
        E.append(err[dedans])
        X.append(ecart[dedans])
        D.append(masque[dedans])
    out["les_blocs"] = blocs
    out["les_non_decides"] = {f"{b_['la_rangee']}_{b_['la_colonne']}": b_["la_raison"] for b_ in blocs
                              if not b_["decidable"]}
    out["les_reunis"] = la_reunion(blocs)
    out["ce_que_la_marche_lit"] = (ce_que_la_marche_lit(np.concatenate(E), np.concatenate(X), np.concatenate(D), glissade)
                                   if E else None)
    verite, partout = tau2 - err, np.ones(tau2.shape, dtype=bool)
    out["le_deuxieme_saut_entier"] = {"avant": la_part_juste(tau2, verite, partout),
                                      "apres": la_part_juste(tau2c, verite, partout)}
    notes_saut = out["le_deuxieme_saut_entier"]["avant"]["les_points_notes"]
    out["la_part_des_points_notes_dans_les_blocs"] = (round(out["les_reunis"]["les_points_notes"] / notes_saut, 4)
                                                      if notes_saut else None)
    np.save(LE_DEUXIEME_SAUT_CORRIGE, tau2c)
    out["le_deuxieme_saut_corrige"] = LE_DEUXIEME_SAUT_CORRIGE.name
    out["decidable"] = (bool(brut["la_reproduction_de_248"]["tous"]) and bool(brut["la_reference_est_celle_de_281"])
                        and bool(controle["identiques"]) and not out["les_piles_manquantes"]
                        and not brut["la_lecture"]["combien_de_pannes"])
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

    v("★★★★ la référence est la surface produite de 281, dont les piles existent, et elle vient d'abord",
      LES_SURFACES[0] == "la_spire_produite_de_la_bande" and LES_SURFACES[1] not in LES_SURFACES_DE_LA_BANDE)
    a = np.array([[1.0, np.nan], [3.0, 4.0]])
    v("★★★★ le premier saut refait est celui de 281 s'il l'égale point pour point, trous compris",
      la_reference_est_celle_de_281(a, a.copy()) and not la_reference_est_celle_de_281(a, np.where(a == 3.0, 3.5, a))
      and not la_reference_est_celle_de_281(a, a[:1]) and not la_reference_est_celle_de_281(a, np.nan_to_num(a)))
    p = np.array([[0.0, 0.0, 0.0], [1.0, 2.0, 3.0]])
    n = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
    t = les_profondeurs_de([{"q": p + np.array([[72.0], [-10.0]]) * n}], p, n)[0]
    v("★★★ la profondeur d'un saut se lit le long de la normale de la bande, avec son signe", np.allclose(t, [72.0, -10.0]))
    r_ = lambda g: {"decidable": True, "les_reunis": {"le_gain_net": g}}  # noqa: E731
    v("★★★★ les issues : corrige si le gain net est positif, sinon non, indécidable sans les contrôles",
      "ne corrige pas" not in le_verdict(r_(1))["lissue"] and "ne corrige pas" in le_verdict(r_(0))["lissue"]
      and "indécidable" in le_verdict({"decidable": False})["lissue"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--controler", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--rendre", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--pas", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        plan = preparer()
        print(json.dumps({k: (len(x) if k in ("les_blocs_notes", "les_blocs_a_rendre") else x) for k, x in plan.items()},
                         ensure_ascii=False, indent=1))
        return 0 if plan.get("la_reproduction_de_248", {}).get("tous") and plan.get("la_reference_est_celle_de_281") else 2
    if a.controler is not None:
        r = controler(a.controler)
        print(json.dumps({"identiques": r["identiques"], "les_piles": r["le_miroir"]["les_piles"]}, ensure_ascii=False))
        return 0 if r["identiques"] else 2
    if a.rendre is not None:
        if not (LE_CONTROLE.is_file() and json.loads(LE_CONTROLE.read_text())["identiques"]):
            print("le miroir n'est pas contrôlé sur la surface neuve : --controler d'abord")
            return 2
        print(json.dumps(tout_rendre(lire_le_plan()["a_rendre"], a.rendre, LES_SURFACES), ensure_ascii=False))
        return 0
    if a.pas is not None:
        print(json.dumps(calculer_les_pas(lire_le_plan()["a_rendre"], a.pas, False, LES_SURFACES), ensure_ascii=False))
        return 0
    r = mesurer()
    print(json.dumps({k: r[k] for k in r if k != "les_blocs"}, ensure_ascii=False, indent=1))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
