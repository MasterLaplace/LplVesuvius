"""La procédure sans juge de `265` corrige-t-elle le deuxième saut ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PILE DU DEUXIÈME SAUT NE SOIT RENDUE. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `279` publient. `277` et `278` montrent que le deuxième saut rate surtout de lui-même, même sous un juge
intact : corriger le premier saut ne suffit pas à la chaîne, chaque saut demande sa correction. `279` fait finir la correction
du premier saut sur une feuille, et la chaîne repartie de cette spire recalée rate encore 1823 des 16635 points notés au
deuxième saut.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain doit corriger chaque transfert, pas seulement le
premier. La procédure de `265` a corrigé le premier saut sur le segment entier (`275`). Il faut savoir si elle corrige aussi le
deuxième, partie de ce que la chaîne a produit et non plus d'un segment tracé par une main.

## La procédure, celle de `265`, sans rien y changer

Elle compare deux marches de fenêtre en fenêtre : celle de la surface produite, et celle d'une référence posée sur une feuille.
Au premier saut, la référence était le segment réduit. Au deuxième, c'est la spire recalée de `279`, d'où le deuxième saut
part ; la surface produite est ce deuxième saut. Une glissade que la référence a déjà se retrouve dans les deux marches et
s'annule : la procédure ne voit que ce que le deuxième saut ajoute, c'est-à-dire ses ratés propres. Le reste est `265` : l'ancre
prise sur les voisins, la décision de `264`, une passe, les pas calculés bloc par bloc comme dans `275`, les piles rendues
depuis le miroir local.

La correction pousse la profondeur du deuxième saut, le long de la normale du segment, de l'écart que la décision retient. Le
juge est la deuxième couche du segment, celle de `248`, et le juge intact de `253` est rapporté à côté. Le juge ne sert qu'à
noter.

⚠ Les blocs sont les blocs candidats de `257` où le juge note au moins un point au deuxième saut ; leurs voisins candidats
sont rendus aussi, sans être notés.

⚠ Deux contrôles rendent la mesure décidable :
- la chaîne repartie de la spire recalée redonne le deuxième saut de `279`, compte pour compte ;
- les deux blocs notés qui portent le plus de points au deuxième saut sont rendus à distance, sur les deux surfaces, puis
  depuis le miroir : les quatre piles doivent être identiques voxel pour voxel. Le miroir estime ses chunks depuis une surface,
  et ces deux surfaces sont neuves.

## Les issues, exclusives, sur les blocs décidés réunis

- les ratés rendus justes sont plus nombreux que les justes rendus ratés : la procédure sans juge corrige le deuxième saut ;
- ils ne le sont pas : elle ne le corrige pas.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : le troisième saut, reparti du deuxième corrigé ; le recalage du deuxième saut sur sa
feuille ; un autre côté, une autre prédiction.

Usage :
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py --verifier
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py --preparer
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py --controler 4
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py --rendre 3
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py --pas 5
    uv run python src/nappe/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.py \\
        --json docs/mesures/la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut.json
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

from la_chaine_rejugee_hors_des_dechirures import les_notes_intactes  # noqa: E402
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (calculer_les_pas, la_reunion,  # noqa: E402
                                                                     le_controle_du_miroir, le_segment,
                                                                     les_rendus_sur_le_disque, les_tables,
                                                                     tout_rendre, un_bloc)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LE_BLOC, LE_DOSSIER,  # noqa: E402
                                                            ecrire_tifxyz, la_fenetre_de_maille, le_cadre,
                                                            le_maillage_produit, rendre)
from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, LE_SEGMENT, lire_tifxyz, telecharger  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import enchainer  # noqa: E402
from le_transfert_retrouve_t_il_la_spire_voisine import LA_PORTEE, les_centres  # noqa: E402
from le_voisinage_dit_il_quel_niveau_est_le_bon import les_voisins  # noqa: E402
from recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste import (  # noqa: E402
    la_feuille_la_plus_proche, le_bilan_recale, recaler)
from repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste import (LA_PREDICTION, LE_COTE,  # noqa: E402
                                                                                LE_SIGNE, les_deux_chaines,
                                                                                les_profondeurs)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_279_A_PUBLIE = LES_MESURES / "recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.json"
LES_SURFACES_DU_DEUXIEME = ("la_spire_recalee", "le_deuxieme_saut")   # la référence, puis la surface produite
LE_SUFFIXE = f"{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}"
LE_DEUXIEME_SAUT = LE_CACHE / f"deuxieme_saut_depuis_la_recalee_265_{LE_SUFFIXE}.npy"
LA_COUCHE_DEUX = LE_CACHE / f"couche_deux_{LE_SUFFIXE}.npy"
LA_COUCHE_DEUX_INTACTE = LE_CACHE / f"couche_deux_intacte_{LE_SUFFIXE}.npy"
LE_DEUXIEME_SAUT_CORRIGE = LE_CACHE / f"deuxieme_saut_corrige_265_{LE_SUFFIXE}.npy"
LE_PLAN = LE_DOSSIER / "le_deuxieme_saut_plan.json"
LE_CONTROLE = LE_DOSSIER / "le_deuxieme_saut_controle.json"


def le_maillage_des_points(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Une surface donnée point par point sur la maille, `-1` là où l'un de ses trois axes manque, comme le format le veut."""
    bon = np.isfinite(q).all(axis=-1)
    return np.where(bon[..., None], q, -1.0), bon


def les_blocs_notes(couche: np.ndarray, candidats: set) -> dict:
    """Les blocs candidats où le juge note au moins un point, et combien."""
    out = {}
    for by, bx in sorted(candidats):
        fi, fj = la_fenetre_de_maille(by, bx, LE_BLOC)
        n = int(np.isfinite(couche[fi, fj]).sum())
        if n:
            out[(by, bx)] = n
    return out


def les_blocs_a_rendre(notes: dict, candidats: set) -> set:
    """Les blocs notés et leurs voisins candidats : la décision d'un bloc lit la marche de ses voisins."""
    return set(notes) | {v for b in notes for v in les_voisins(*b, candidats)}


def les_blocs_du_controle(notes: dict) -> list[tuple[int, int]]:
    """Les deux blocs notés qui portent le plus de points ; à égalité, l'ordre des blocs."""
    return [b for b, _ in sorted(notes.items(), key=lambda x: (-x[1], x[0]))[:2]]


def le_bilan_du_juge(bloc: dict) -> dict:
    return {k: bloc[k] for k in ("avant", "apres", "les_points_corriges", "les_rates_rendus_justes", "les_justes_rendus_rates")}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la chaîne ne redonne pas le deuxième saut de 279, ou le miroir ne redonne pas les "
                          "piles rendues à distance"}
    if r["les_reunis"]["le_gain_net"] > 0:
        return {"lissue": "la procédure sans juge corrige le deuxième saut"}
    return {"lissue": "la procédure sans juge ne corrige pas le deuxième saut"}


# ── LES ÉTAPES ─────────────────────────────────────────────────────────────────────────────────────────────────────

def preparer(cache: Path = LE_CACHE) -> dict:
    """La chaîne repartie de la spire recalée, les deux surfaces à rendre, le juge du deuxième saut et les blocs."""
    c = les_deux_chaines()
    if isinstance(c, str):
        return {"decidable": False, "la_raison": c}
    p, n, v, tau0, tau1 = c["p"], c["n"], c["verite"], c["tau0"], c["tau1"]
    grille, gi, gj, lire_rayon = c["sur_la_grille"], c["gi"], c["gj"], c["lire_rayon"]
    t, vu = lire_rayon(p, n, LE_SIGNE, LA_PORTEE)
    with np.errstate(invalid="ignore"):
        deplace = ~(np.abs(tau1 - tau0) < 1e-9)
    tau1r = recaler(tau1, deplace, la_feuille_la_plus_proche(les_centres(t, vu), tau1))
    recalee = enchainer(p, n, LE_SIGNE, 2, lire_rayon, grille, gi, gj, True, premier=tau1r)
    pr = les_profondeurs(recalee, p, n)
    refait = le_bilan_recale(c["pc"][1], pr[1], v[1])
    publie = json.loads(CE_QUE_279_A_PUBLIE.read_text())["les_sauts"][1]
    ref, valide, esp = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    scale = 1.0 / (esp * LA_MAILLE)
    pp, vp = le_maillage_produit(ref, valide, grille(tau1r))
    q2 = np.stack([grille(recalee[1]["q"][:, a]) for a in range(3)], axis=-1)
    p2, v2m = le_maillage_des_points(q2)
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_DU_DEUXIEME[0] / "maillage", pp, vp, scale, LES_SURFACES_DU_DEUXIEME[0])
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_DU_DEUXIEME[1] / "maillage", p2, v2m, scale, LES_SURFACES_DU_DEUXIEME[1])
    couche = grille(v[1])
    np.save(LE_DEUXIEME_SAUT, grille(pr[1]))
    np.save(LA_COUCHE_DEUX, couche)
    np.save(LA_COUCHE_DEUX_INTACTE, grille(les_notes_intactes(v[1], grille, gi, gj).astype(float)) > 0.5)
    _, _, _, candidats = le_segment(cache)
    notes = les_blocs_notes(couche, candidats)
    plan = {"le_deuxieme_saut_de_279": {"publie": publie, "refait": refait, "reproduit": refait == publie},
            "les_blocs_notes": {f"{b[0]}_{b[1]}": k for b, k in notes.items()},
            "les_blocs_a_rendre": sorted(f"{b[0]}_{b[1]}" for b in les_blocs_a_rendre(notes, candidats)),
            "les_blocs_du_controle": [f"{b[0]}_{b[1]}" for b in les_blocs_du_controle(notes)],
            "les_points_de_la_surface": {s: int(m.sum()) for s, m in zip(LES_SURFACES_DU_DEUXIEME, (vp, v2m))}}
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire_le_plan() -> dict:
    d = json.loads(LE_PLAN.read_text())
    bloc = lambda s: tuple(int(x) for x in s.split("_"))  # noqa: E731
    return {"notes": {bloc(k): v for k, v in d["les_blocs_notes"].items()},
            "a_rendre": {bloc(k) for k in d["les_blocs_a_rendre"]},
            "controle": [bloc(k) for k in d["les_blocs_du_controle"]], "brut": d}


def controler(ouvriers: int = 4) -> dict:
    """Les piles du contrôle, rendues à distance puis depuis le miroir, comparées voxel pour voxel."""
    plan = lire_le_plan()
    taches = [(s, by, bx) for s in LES_SURFACES_DU_DEUXIEME for by, bx in plan["controle"]]

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


def mesurer(cache: Path = LE_CACHE, pas_ouvriers: int = 5) -> dict:
    debut = time.monotonic()
    plan = lire_le_plan()
    controle = json.loads(LE_CONTROLE.read_text()) if LE_CONTROLE.is_file() else {"identiques": False}
    _, _, glissade, candidats = le_segment(cache)
    tau2, couche = np.load(LE_DEUXIEME_SAUT), np.load(LA_COUCHE_DEUX)
    intacte = np.load(LA_COUCHE_DEUX_INTACTE)
    err = tau2 - couche
    err_i = np.where(intacte, err, np.nan)
    surfaces = LES_SURFACES_DU_DEUXIEME
    out = {"la_glissade_voxels": glissade, "les_blocs_notes": len(plan["notes"]), "les_blocs_rendus_en_tout": len(plan["a_rendre"]),
           "le_deuxieme_saut_de_279": plan["brut"]["le_deuxieme_saut_de_279"],
           "le_controle_du_miroir": {"les_blocs": plan["brut"]["les_blocs_du_controle"], "identiques": controle["identiques"],
                                     "les_piles": {k: x.get("les_voxels_differents") for k, x in
                                                   controle.get("le_miroir", {}).get("les_piles", {}).items()}}}
    out["les_pas"] = calculer_les_pas(plan["a_rendre"], pas_ouvriers, True, surfaces)
    rendus = les_rendus_sur_le_disque(plan["a_rendre"], surfaces)
    out["les_piles_manquantes"] = sorted(f"{s}_{by}_{bx}" for (s, by, bx), ok in rendus.items() if not ok)
    tables = les_tables(plan["a_rendre"], rendus, surfaces)
    blocs, blocs_i, tau2c = [], [], tau2.copy()
    for by, bx in sorted(plan["notes"]):
        b, corr = un_bloc(by, bx, candidats, tables, rendus, tau2, err, glissade, surfaces)
        blocs.append(b)
        if corr is not None:
            masque, t_ = corr
            tau2c[masque] = t_[masque]
            bi, _ = un_bloc(by, bx, candidats, tables, rendus, tau2, err_i, glissade, surfaces)
            blocs_i.append(bi)
    out["les_blocs"] = blocs
    out["les_non_decides"] = {f"{b['la_rangee']}_{b['la_colonne']}": b["la_raison"] for b in blocs if not b["decidable"]}
    out["les_reunis"] = la_reunion(blocs)
    out["les_reunis_sous_le_juge_intact"] = la_reunion(blocs_i)
    np.save(LE_DEUXIEME_SAUT_CORRIGE, tau2c)
    out["le_deuxieme_saut_corrige"] = LE_DEUXIEME_SAUT_CORRIGE.name
    out["decidable"] = (bool(out["le_deuxieme_saut_de_279"]["reproduit"]) and bool(controle["identiques"])
                        and not out["les_piles_manquantes"])
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

    q = np.arange(2 * 3 * 3, dtype=float).reshape(2, 3, 3)
    q[1, 2, 0] = np.nan
    pts, bon = le_maillage_des_points(q)
    v("★★★★ une surface point par point : -1 partout où l'un des trois axes manque, et la valeur ailleurs",
      not bon[1, 2] and (pts[1, 2] == -1.0).all() and bon.sum() == 5 and np.allclose(pts[0, 0], [0.0, 1.0, 2.0]))

    # La maille : un point tous les 160 pixels, un chunk de 128 ; un bloc de 16 chunks couvre ~13 points de côté.
    forme = (60, 60)
    couche = np.full(forme, np.nan)
    fi, fj = la_fenetre_de_maille(16, 16, LE_BLOC)
    couche[fi.start + 5, fj.start + 5] = 140.0         # au milieu du bloc, hors des fenêtres de ses voisins
    candidats = {(0, 0), (0, 16), (16, 0), (16, 16), (16, 32), (32, 32)}
    notes = les_blocs_notes(couche, candidats)
    v("★★★★ un bloc est noté s'il porte au moins un point du juge, et seulement lui", notes == {(16, 16): 1}, str(notes))
    a_rendre = les_blocs_a_rendre({(16, 16): 1}, candidats)
    v("★★★★ les blocs à rendre sont le bloc noté et ses voisins candidats, en croix", a_rendre == {(16, 16), (0, 16), (16, 0),
                                                                                                    (16, 32)}, str(a_rendre))
    v("★★★ le contrôle prend les deux blocs notés qui portent le plus de points, l'ordre des blocs à égalité",
      les_blocs_du_controle({(0, 0): 3, (0, 16): 5, (16, 0): 5, (16, 16): 1}) == [(0, 16), (16, 0)])
    r_ = lambda g: {"decidable": True, "les_reunis": {"le_gain_net": g}}  # noqa: E731
    v("★★★★ les issues : corrige si le gain net est positif, sinon non, indécidable sans les deux contrôles",
      "corrige le deuxième saut" in le_verdict(r_(1))["lissue"] and "ne corrige pas" in le_verdict(r_(0))["lissue"]
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
        print(json.dumps({k: (len(x) if isinstance(x, (dict, list)) and k.startswith("les_blocs") else x)
                          for k, x in plan.items()}, ensure_ascii=False, indent=1))
        return 0 if plan.get("le_deuxieme_saut_de_279", {}).get("reproduit") else 2
    if a.controler is not None:
        r = controler(a.controler)
        print(json.dumps({"identiques": r["identiques"], "les_piles": r["le_miroir"]["les_piles"]}, ensure_ascii=False))
        return 0 if r["identiques"] else 2
    if a.rendre is not None:
        if not (LE_CONTROLE.is_file() and json.loads(LE_CONTROLE.read_text())["identiques"]):
            print("le miroir n'est pas contrôlé sur ces surfaces : --controler d'abord")
            return 2
        print(json.dumps(tout_rendre(lire_le_plan()["a_rendre"], a.rendre, LES_SURFACES_DU_DEUXIEME), ensure_ascii=False))
        return 0
    if a.pas is not None:
        print(json.dumps(calculer_les_pas(lire_le_plan()["a_rendre"], a.pas, False, LES_SURFACES_DU_DEUXIEME),
                         ensure_ascii=False))
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
