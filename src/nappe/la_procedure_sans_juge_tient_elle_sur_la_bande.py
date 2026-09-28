"""La procédure sans juge de `265` tient-elle sur la bande `w028-037` ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE PILE DE LA BANDE NE SOIT RENDUE. Ce qui était vu avant d'écrire : tout ce que
`248` et `257` à `280` publient. La procédure de `265` corrige le premier saut sur le segment `20230702185753` (`275`), puis
le deuxième (`280`). Mais sur ce segment, le juge, les couches du segment lui-même, ne note plus que 295 points au troisième
saut et 32 au quatrième : au-delà du deuxième saut, rien n'y est mesurable.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. Ce qui remplace l'humain doit corriger chaque saut, et il faut un juge pour
le voir faire au-delà du deuxième. La bande `20260623142658-w028-037` trace dix spires d'un seul tenant, et c'est le juge de
`248` : sur sa tranche, côté plus, ses couches notent 0,8794, 0,7309, 0,5243 et 0,3071 des points aux sauts 1 à 4. Elle a été
tracée par d'autres, sans rien savoir de cette méthode. Avant d'y corriger le deuxième saut, il faut savoir si la procédure y
corrige le premier. Elle a été mise au point sur un autre segment : c'est aussi la première fois qu'elle en change.

## La procédure, celle de `265`, sans rien y changer

La tranche de la bande est celle de `248` (les rangées de 0,45 à 0,55, toutes les colonnes), et la chaîne est la sienne. Le
premier saut de cette chaîne est la spire produite ; la bande réduite à la maille de la chaîne est la référence. Le reste est
`275` : les blocs candidats de `257`, l'ancre prise sur les voisins, la décision de `264`, une passe, les pas calculés bloc par
bloc, les piles rendues depuis le miroir local. La glissade de la décision est celle que `261` a retrouvée sur le segment
`20230702185753`, reprise telle quelle. Le juge est la première couche de la bande, et il ne sert qu'à noter.

⚠ Le treillis des chunks est celui du volume de surface que le rendu produit : la grille de la tranche, au pas de sa grille
(20 voxels), coupée en chunks de 128. Sur le segment `20230702185753`, la même règle doit redonner le treillis que `257` lit dans
le volume publié.

⚠ Trois contrôles rendent la mesure décidable :
- la chaîne redonne `248` sur la bande, saut par saut, compte pour compte ;
- la règle du treillis redonne celui de `257` ;
- les deux blocs candidats qui portent le plus de points notés sont rendus à distance, sur les deux surfaces, puis depuis le
  miroir : les quatre piles doivent être identiques voxel pour voxel.
Il ne doit manquer aucune pile.

## Les issues, exclusives, sur les blocs décidés réunis

- les ratés rendus justes sont plus nombreux que les justes rendus ratés : la procédure améliore le premier saut sur la bande ;
- ils ne le sont pas : elle ne l'améliore pas.

⚠ Rapporté à côté : bloc par bloc, ce que la décision corrige ; les blocs non décidés et pourquoi ; la part des points notés
de la bande que les blocs candidats couvrent ; la part sur la bande entière, avant et après.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : le deuxième saut de la bande ; un autre côté, une autre prédiction ; une glissade
retrouvée sur la bande elle-même.

Usage :
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py --verifier
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py --preparer
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py --controler 4
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py --rendre 3
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py --pas 5
    uv run python src/nappe/la_procedure_sans_juge_tient_elle_sur_la_bande.py \\
        --json docs/mesures/la_procedure_sans_juge_tient_elle_sur_la_bande.json
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
from la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut import (le_maillage_des_points,  # noqa: E402
                                                                    les_blocs_du_controle, les_blocs_notes)
from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import (CE_QUE_257_A_PUBLIE,  # noqa: E402
                                                                     CE_QUE_261_A_PUBLIE, calculer_les_pas,
                                                                     la_reunion, le_controle_du_miroir,
                                                                     les_rendus_sur_le_disque, les_tables,
                                                                     tout_rendre, un_bloc)
from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_COTE_DU_CHUNK, LE_DOSSIER, ecrire_tifxyz,
                                                            le_cadre, le_maillage_produit, le_maillage_reduit,
                                                            les_blocs_candidats, rendre)
from la_spire_voisine_est_elle_a_un_pas import (LE_CACHE, LE_SEGMENT, les_normales, lire_tifxyz,  # noqa: E402
                                                telecharger)
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS, enchainer,  # noqa: E402
                                                       juger_le_saut, les_couches_ordonnees, lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LES_PREDICTIONS, le_facteur,  # noqa: E402
                                                         lecteur_du_depot)

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_248_A_PUBLIE = LES_MESURES / "le_transfert_enchaine_tient_il_les_spires.json"
LES_SURFACES_DE_LA_BANDE = ("la_bande_reduite", "la_spire_produite_de_la_bande")   # la référence, puis la surface produite
LE_SIGNE = {"du_cote_plus": 1.0, "du_cote_moins": -1.0}[LE_COTE]
LE_SUFFIXE = f"{LA_BANDE}_{LA_PREDICTION}_{LE_COTE}"
LE_PREMIER_SAUT = LE_CACHE / f"premier_saut_de_la_bande_{LE_SUFFIXE}.npy"
LES_COUCHES_DE_LA_BANDE = LE_CACHE / f"couches_de_la_bande_{LE_SUFFIXE}.npy"
LE_PREMIER_SAUT_CORRIGE = LE_CACHE / f"premier_saut_corrige_265_{LE_SUFFIXE}.npy"
LE_PLAN = LE_DOSSIER / "la_bande_plan.json"
LE_CONTROLE = LE_DOSSIER / "la_bande_controle.json"


def la_tranche(ref: np.ndarray, valide: np.ndarray, rangees: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
    """Les rangées de la grille pleine que `248` garde, comme `248` les coupe."""
    h = ref.shape[0]
    a, b = int(h * rangees[0]), int(h * rangees[1])
    return ref[a:b], valide[a:b]


def le_treillis_de(forme: tuple[int, int], pas_de_grille: int, chunk: int = LE_COTE_DU_CHUNK) -> tuple[int, int]:
    """Le treillis des chunks du volume de surface qu'une grille rend : un pixel par voxel, le dernier chunk entamé compté."""
    return -(-int(forme[0]) * int(pas_de_grille) // chunk), -(-int(forme[1]) * int(pas_de_grille) // chunk)


def la_reproduction_de_248(taus: list[np.ndarray], verite: list[np.ndarray], publie: list[dict]) -> dict:
    """Saut par saut, la chaîne refaite contre celle que `248` publie : ses points notés et le jugement de la chaîne."""
    lignes = []
    for h in range(1, len(publie) + 1):
        j = juger_le_saut(taus[h - 1], verite[h - 1], LE_SIGNE, h)
        refait = {"les_points_notes": j["les_points_notes"], "la_chaine": j.get("le_transfert")}
        pub = {"les_points_notes": publie[h - 1]["les_points_notes"], "la_chaine": publie[h - 1]["la_chaine"]}
        lignes.append({"publie": pub, "refait": refait, "reproduit": refait == pub})
    return {"les_sauts": lignes, "tous": bool(lignes) and all(x["reproduit"] for x in lignes)}


def le_verdict(r: dict) -> dict:
    if not r.get("decidable"):
        return {"lissue": "indécidable : la chaîne ne redonne pas 248 sur la bande, la règle du treillis ne redonne pas 257, "
                          "le miroir ne redonne pas les piles rendues à distance, ou il manque une pile"}
    if r["les_reunis"]["le_gain_net"] > 0:
        return {"lissue": "la procédure sans juge améliore le premier saut sur la bande"}
    return {"lissue": "la procédure sans juge n'améliore pas le premier saut sur la bande"}


# ── LES ÉTAPES ─────────────────────────────────────────────────────────────────────────────────────────────────────

def la_bande(cache: Path = LE_CACHE, sauts: int = LES_SAUTS, rangees: tuple[float, float] = LA_TRANCHE) -> dict | str:
    """La tranche de la bande comme `248` la lit : les points de la maille, leurs normales, leurs couches et le rayon.
    `rangees` choisit la tranche, celle de `248` par défaut."""
    d = telecharger(LA_BANDE, cache, DELAI)
    if isinstance(d, str):
        return d
    ref, valide, esp = lire_tifxyz(d)
    ref, valide = la_tranche(ref, valide, rangees)
    couches = les_couches_ordonnees(ref, valide, esp, LA_MAILLE, sauts)
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::LA_MAILLE, ::LA_MAILLE] = True
    ii, jj = np.nonzero(ok & grille)
    forme = np.full(ok.shape, np.nan)[::LA_MAILLE, ::LA_MAILLE].shape
    gi, gj = ii // LA_MAILLE, jj // LA_MAILLE

    def sur_la_grille(val):
        c = np.full(forme, np.nan)
        c[gi, gj] = val
        return c

    chemin, niveau = LES_PREDICTIONS[LA_PREDICTION]
    facteur, pred = le_facteur(chemin, niveau, DELAI)
    lire, stats = lecteur_du_depot(pred, cache, LA_PREDICTION, chemin, niveau, DELAI)

    def lire_rayon(q, nq, cote, portee):
        return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

    cote_ = "plus" if LE_SIGNE > 0 else "moins"
    return {"ref": ref, "valide": valide, "esp": esp, "p": ref[ii, jj], "n": normales[ii, jj], "gi": gi, "gj": gj,
            "sur_la_grille": sur_la_grille, "lire_rayon": lire_rayon, "stats": stats,
            "verite": [couches["les_cartes"][cote_][gi, gj, k] for k in range(sauts)]}


def preparer(cache: Path = LE_CACHE) -> dict:
    """La chaîne de `248` sur la bande, les deux surfaces à rendre, le juge et les blocs."""
    b = la_bande(cache)
    if isinstance(b, str):
        return {"decidable": False, "la_raison": b}
    p, n, gi, gj, grille = b["p"], b["n"], b["gi"], b["gj"], b["sur_la_grille"]
    chaine = enchainer(p, n, LE_SIGNE, LES_SAUTS, b["lire_rayon"], grille, gi, gj, True)
    taus = [np.einsum("ij,ij->i", s["q"] - p, n) for s in chaine]
    publie = json.loads(CE_QUE_248_A_PUBLIE.read_text())["les_predictions"][LA_PREDICTION][LE_COTE]["les_sauts"]
    tau0 = grille(taus[0])
    couches = np.stack([grille(v) for v in b["verite"]], axis=-1)
    err = tau0 - couches[..., 0]
    pas_de_grille = int(round(b["esp"]))
    gy, gx = le_treillis_de(b["valide"].shape, pas_de_grille)
    ref5753, _, esp5753 = lire_tifxyz(telecharger(LE_SEGMENT, cache))
    treillis_257 = json.loads(CE_QUE_257_A_PUBLIE.read_text())["le_treillis"]
    candidats = set(les_blocs_candidats(tau0, b["valide"], gy, gx, pas_de_grille=pas_de_grille))
    notes = les_blocs_notes(err, candidats)
    scale = 1.0 / (b["esp"] * LA_MAILLE)
    pr, vr = le_maillage_reduit(b["ref"], b["valide"])
    pp, vp = le_maillage_produit(b["ref"], b["valide"], tau0)
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_DE_LA_BANDE[0] / "maillage", pr, vr, scale, LES_SURFACES_DE_LA_BANDE[0])
    ecrire_tifxyz(LE_DOSSIER / LES_SURFACES_DE_LA_BANDE[1] / "maillage", pp, vp, scale, LES_SURFACES_DE_LA_BANDE[1])
    np.save(LE_PREMIER_SAUT, tau0)
    np.save(LES_COUCHES_DE_LA_BANDE, couches)
    plan = {"la_reproduction_de_248": la_reproduction_de_248(taus, b["verite"], publie),
            "le_treillis": {"la_bande": [gy, gx], "le_pas_de_grille_voxels": pas_de_grille,
                            "la_grille_de_la_tranche": list(b["valide"].shape),
                            "le_segment_20230702185753": list(le_treillis_de(ref5753.shape[:2], int(round(esp5753)))),
                            "celui_de_257": treillis_257},
            "les_points_de_la_maille": int(len(p)),
            "les_blocs_candidats": sorted(f"{by}_{bx}" for by, bx in candidats),
            "les_points_notes_par_bloc": {f"{k[0]}_{k[1]}": v for k, v in sorted(notes.items())},
            "les_blocs_du_controle": [f"{k[0]}_{k[1]}" for k in les_blocs_du_controle(notes)],
            "les_points_de_la_surface": {s: int(m.sum()) for s, m in zip(LES_SURFACES_DE_LA_BANDE, (vr, vp))},
            "la_lecture": {"combien_de_pannes": len(b["stats"]["pannes"])}}
    plan["le_treillis"]["reproduit"] = plan["le_treillis"]["le_segment_20230702185753"] == treillis_257
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire_le_plan() -> dict:
    d = json.loads(LE_PLAN.read_text())
    bloc = lambda s: tuple(int(x) for x in s.split("_"))  # noqa: E731
    return {"candidats": {bloc(k) for k in d["les_blocs_candidats"]},
            "controle": [bloc(k) for k in d["les_blocs_du_controle"]], "brut": d}


def controler(ouvriers: int = 4) -> dict:
    """Les piles du contrôle, rendues à distance puis depuis le miroir, comparées voxel pour voxel."""
    plan = lire_le_plan()
    taches = [(s, by, bx) for s in LES_SURFACES_DE_LA_BANDE for by, bx in plan["controle"]]

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
    tau0, couches = np.load(LE_PREMIER_SAUT), np.load(LES_COUCHES_DE_LA_BANDE)
    err = tau0 - couches[..., 0]
    candidats, surfaces = plan["candidats"], LES_SURFACES_DE_LA_BANDE
    out = {"la_glissade_voxels": glissade, "les_blocs_candidats": len(candidats),
           "la_reproduction_de_248": brut["la_reproduction_de_248"], "le_treillis": brut["le_treillis"],
           "les_points_de_la_maille": brut["les_points_de_la_maille"],
           "le_controle_du_miroir": {"les_blocs": brut["les_blocs_du_controle"], "identiques": controle["identiques"],
                                     "les_piles": {k: x.get("les_voxels_differents") for k, x in
                                                   controle.get("le_miroir", {}).get("les_piles", {}).items()}}}
    out["les_pas"] = calculer_les_pas(candidats, pas_ouvriers, True, surfaces)
    rendus = les_rendus_sur_le_disque(candidats, surfaces)
    out["les_piles_manquantes"] = sorted(f"{s}_{by}_{bx}" for (s, by, bx), ok in rendus.items() if not ok)
    tables = les_tables(candidats, rendus, surfaces)
    blocs, tau1 = [], tau0.copy()
    for by, bx in sorted(candidats):
        b_, corr = un_bloc(by, bx, candidats, tables, rendus, tau0, err, glissade, surfaces)
        blocs.append(b_)
        if corr is not None:
            masque, t_ = corr
            tau1[masque] = t_[masque]
    out["les_blocs"] = blocs
    out["les_non_decides"] = {f"{b_['la_rangee']}_{b_['la_colonne']}": b_["la_raison"] for b_ in blocs
                              if not b_["decidable"]}
    out["les_reunis"] = la_reunion(blocs)
    verite, partout = tau0 - err, np.ones(tau0.shape, dtype=bool)
    out["la_bande_entiere"] = {"avant": la_part_juste(tau0, verite, partout), "apres": la_part_juste(tau1, verite, partout)}
    notes_bande = out["la_bande_entiere"]["avant"]["les_points_notes"]
    out["la_part_des_points_notes_dans_les_blocs"] = (round(out["les_reunis"]["les_points_notes"] / notes_bande, 4)
                                                      if notes_bande else None)
    np.save(LE_PREMIER_SAUT_CORRIGE, tau1)
    out["le_premier_saut_corrige"] = LE_PREMIER_SAUT_CORRIGE.name
    out["decidable"] = (bool(brut["la_reproduction_de_248"]["tous"]) and bool(brut["le_treillis"]["reproduit"])
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

    ref = np.arange(20 * 3 * 3, dtype=float).reshape(20, 3, 3)
    r_, v_ = la_tranche(ref, np.ones((20, 3), dtype=bool), (0.45, 0.55))
    v("★★★★ la tranche garde les rangées de int(h × a) à int(h × b), comme 248", r_.shape[0] == 2 and r_[0, 0, 0] == ref[9, 0, 0]
      and v_.shape == (2, 3), str(r_.shape))
    v("★★★★ le treillis compte le dernier chunk entamé : 2534 × 1824 au pas de 20 font 396 × 285",
      le_treillis_de((2534, 1824), 20) == (396, 285) and le_treillis_de((7, 12), 20) == (2, 2)
      and le_treillis_de((64, 64), 2) == (1, 1), str(le_treillis_de((2534, 1824), 20)))

    tau = [np.array([72.0, 72.0, 200.0, np.nan]), np.array([144.0, 144.0, 144.0, 144.0])]
    verite = [np.array([70.0, 75.0, 72.0, 72.0]), np.array([144.0, 150.0, np.nan, 140.0])]
    pub = [{"les_points_notes": 4, "la_chaine": juger_le_saut(tau[0], verite[0], LE_SIGNE, 1)["le_transfert"]},
           {"les_points_notes": 3, "la_chaine": juger_le_saut(tau[1], verite[1], LE_SIGNE, 2)["le_transfert"]}]
    v("★★★★ la chaîne refaite qui égale 248 saut par saut est reproduite", la_reproduction_de_248(tau, verite, pub)["tous"])
    pub_points = [dict(pub[0]), dict(pub[1], les_points_notes=4)]
    v("★★★★ un compte de points notés qui diffère suffit à ne pas reproduire",
      not la_reproduction_de_248(tau, verite, pub_points)["tous"])
    pub_part = [dict(pub[0], la_chaine=dict(pub[0]["la_chaine"], la_part_sur_la_bonne_spire=0.25)), pub[1]]
    v("★★★ une part qui diffère aussi", not la_reproduction_de_248(tau, verite, pub_part)["tous"])
    v("★★★ sans saut publié, rien n'est reproduit", not la_reproduction_de_248(tau, verite, [])["tous"])

    q = np.full((2, 2, 3), 5.0)
    q[0, 1, 2] = np.nan
    pts, bon = le_maillage_des_points(q)
    v("★★ la surface point par point de 280 marque -1 là où un axe manque", not bon[0, 1] and (pts[0, 1] == -1).all())

    r_ = lambda g: {"decidable": True, "les_reunis": {"le_gain_net": g}}  # noqa: E731
    v("★★★★ les issues : améliore si le gain net est positif, sinon non, indécidable sans les contrôles",
      "n'améliore pas" not in le_verdict(r_(1))["lissue"] and "améliore le premier saut" in le_verdict(r_(1))["lissue"]
      and "n'améliore pas" in le_verdict(r_(0))["lissue"] and "indécidable" in le_verdict({"decidable": False})["lissue"])

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
        print(json.dumps({k: (len(x) if k in ("les_blocs_candidats", "les_points_notes_par_bloc") else x)
                          for k, x in plan.items()}, ensure_ascii=False, indent=1))
        return 0 if plan.get("la_reproduction_de_248", {}).get("tous") and plan["le_treillis"]["reproduit"] else 2
    if a.controler is not None:
        r = controler(a.controler)
        print(json.dumps({"identiques": r["identiques"], "les_piles": r["le_miroir"]["les_piles"]}, ensure_ascii=False))
        return 0 if r["identiques"] else 2
    if a.rendre is not None:
        if not (LE_CONTROLE.is_file() and json.loads(LE_CONTROLE.read_text())["identiques"]):
            print("le miroir n'est pas contrôlé sur ces surfaces : --controler d'abord")
            return 2
        print(json.dumps(tout_rendre(lire_le_plan()["candidats"], a.rendre, LES_SURFACES_DE_LA_BANDE), ensure_ascii=False))
        return 0
    if a.pas is not None:
        print(json.dumps(calculer_les_pas(lire_le_plan()["candidats"], a.pas, False, LES_SURFACES_DE_LA_BANDE),
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
