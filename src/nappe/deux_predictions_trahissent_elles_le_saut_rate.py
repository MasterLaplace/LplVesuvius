"""Deux prédictions qui ne s'accordent pas trahissent-elles le saut raté ?

⭐⭐⭐⭐ LA SUITE DE `250`. Le retour ne signale qu'un raté sur cinq ou six, parce que la plupart des ratés sont
symétriques : ce qu'une prédiction manque à l'aller, elle le manque au retour. Un contrôle doit donc venir d'ailleurs que
de la prédiction qui s'est trompée. Il y en a deux publiées pour PHercParis4, `m7` et `ps256`, entraînées séparément :
là où leurs premiers sauts tombent à plus d'un demi-feuillet l'un de l'autre, au moins l'un des deux a raté, et la
machine le sait seule.

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE. Les deux premiers sauts sont ceux de `247` (la feuille suivante, puis le vote),
relus tels qu'ils ont été écrits. Un point est EN DÉSACCORD si les deux tombent à un demi-feuillet ou plus l'un de
l'autre. Trois détecteurs sont notés côte à côte contre la couche que l'objet porte lui-même, celle de `248` : le retour
de `250` avec `m7`, le désaccord, et leur réunion. Là où les deux s'accordent, la part juste est lue pour chacune ; là où
elles divergent, la part où `m7` a raison, où `ps256` a raison, et où aucune.

⚠⚠ CE QUE LE DÉSACCORD NE PEUT PAS VOIR : un endroit où les deux prédictions ratent de la même façon. `249` a montré que
là où la bande saute, le scan brut à 9,6 µm ne résout pas les feuilles ; deux modèles lus sur le même scan peuvent y
échouer ensemble.

Usage :
    uv run python src/nappe/deux_predictions_trahissent_elles_le_saut_rate.py --verifier
    uv run python src/nappe/deux_predictions_trahissent_elles_le_saut_rate.py \\
        --json docs/mesures/deux_predictions_trahissent_elles_le_saut_rate.json
    uv run python src/nappe/deux_predictions_trahissent_elles_le_saut_rate.py --segment 20230702185753 \\
        --json docs/mesures/deux_predictions_sur_le_segment_5753.json
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

from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, les_normales,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_retour_trahit_il_le_saut_rate import aller_retour, la_confusion  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS,  # noqa: E402
                                                       les_couches_ordonnees, lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LES_PREDICTIONS,  # noqa: E402
                                                         le_facteur, lecteur_du_depot)


def le_desaccord(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Les points où deux sauts tombent à un demi-feuillet ou plus l'un de l'autre."""
    with np.errstate(invalid="ignore"):
        return ~(np.abs(a - b) < DEMI_PAS_EN_VOXELS)


def qui_a_raison(a: np.ndarray, b: np.ndarray, t_soi: np.ndarray, masque: np.ndarray) -> dict:
    """Parmi les points du masque qui ont une couche, la part où seul `a` est juste, seul `b`, les deux, aucun."""
    note = masque & np.isfinite(t_soi)
    with np.errstate(invalid="ignore"):
        ja = np.abs(a - t_soi) < DEMI_PAS_EN_VOXELS
        jb = np.abs(b - t_soi) < DEMI_PAS_EN_VOXELS
    n = int(note.sum())
    if not n:
        return {"combien": 0}
    return {"combien": n, "seul_le_premier": round(float((ja & ~jb)[note].mean()), 4),
            "seul_le_second": round(float((~ja & jb)[note].mean()), 4),
            "les_deux": round(float((ja & jb)[note].mean()), 4), "aucun": round(float((~ja & ~jb)[note].mean()), 4)}


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

    chemin, niveau = LES_PREDICTIONS["m7"]
    facteur, pred = le_facteur(chemin, niveau, delai)
    lire, stats = lecteur_du_depot(pred, cache, "m7", chemin, niveau, delai)

    def lire_rayon(q, nq, cote, portee):
        return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None, "la_maille": maille,
           "les_points": int(len(p))}
    for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
        t_soi = couches[cote_][gi, gj, 0]
        note = np.isfinite(t_soi)
        sauts = {}
        for nom_p in ("m7", "ps256"):
            f = cache / f"transfert_suivante_{segment}_{nom_p}_{nom}.npy"
            if not f.exists():
                return {"decidable": False, "la_raison": f"le premier saut de 247 manque : {f.name}"}
            sauts[nom_p] = np.load(f)[gi, gj]
        # ⚠⚠ LE RETOUR DE `250`, REFAIT ICI avec `m7` : son aller doit être le saut relu, au voxel près.
        ar = aller_retour(p, n, cote, lire_rayon, sur_la_grille, gi, gj)
        ecart_aller = float(np.nanmax(np.abs(ar["le_pas_de_laller"] - sauts["m7"])))
        desaccord = le_desaccord(sauts["m7"], sauts["ps256"])
        detecteurs = {"le_retour": ar["coherent"], "le_desaccord": ~desaccord,
                      "la_reunion": ar["coherent"] & ~desaccord}
        r = {"laller_contre_247_ecart_max_voxels": round(ecart_aller, 4),
             "la_part_en_desaccord_sur_tous_les_points": round(float(desaccord.mean()), 4), "les_detecteurs": {}}
        for nom_p in ("m7", "ps256"):
            with np.errstate(invalid="ignore"):
                bon = np.abs(sauts[nom_p] - t_soi) < DEMI_PAS_EN_VOXELS
            r["les_detecteurs"][nom_p] = {k: la_confusion(bon, c, note) for k, c in detecteurs.items()
                                          if not (k != "le_desaccord" and nom_p == "ps256")}
        r["la_ou_elles_divergent"] = qui_a_raison(sauts["m7"], sauts["ps256"], t_soi, desaccord)
        r["la_ou_elles_saccordent"] = qui_a_raison(sauts["m7"], sauts["ps256"], t_soi, ~desaccord)
        out[nom] = r
    out["la_lecture"] = {"chunks_lus": stats["lus"], "combien_de_pannes": len(stats["pannes"]),
                         "les_pannes": stats["pannes"][:20]}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = not stats["pannes"]
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points, {r['les_secondes']} s")
    for nom in ("du_cote_plus", "du_cote_moins"):
        x = r[nom]
        print(f"— {nom} : aller contre 247 {x['laller_contre_247_ecart_max_voxels']}, en désaccord "
              f"{x['la_part_en_desaccord_sur_tous_les_points']}")
        for nom_p, dets in x["les_detecteurs"].items():
            for k, c in dets.items():
                print(f"    {nom_p} {k:14s} ratés signalés {c['la_part_des_rates_signales']}  justes à tort "
                      f"{c['la_part_des_justes_signales_a_tort']}  ratés parmi signalés {c['la_part_ratee_parmi_les_signales']}"
                      f"  juste {c['la_part_juste_a_laller']} → {c['la_part_juste_parmi_les_gardes']} (gardés "
                      f"{c['la_part_gardee']})")
        print(f"    là où elles divergent {x['la_ou_elles_divergent']}")
        print(f"    là où elles s'accordent {x['la_ou_elles_saccordent']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LE DÉSACCORD : à 35 voxels on s'accorde, à 36 non ; un saut absent n'est pas un accord.
    a = np.array([72.0, 72.0, 72.0, 72.0, np.nan])
    b = np.array([107.0, 108.0, 72.0, 150.0, 72.0])
    v("★★★★ à moins d'un demi-feuillet on s'accorde, à un demi-feuillet non, et un saut absent est un désaccord",
      le_desaccord(a, b).tolist() == [False, True, False, True, True], str(le_desaccord(a, b)))
    v("★★ le désaccord est symétrique", np.array_equal(le_desaccord(a, b), le_desaccord(b, a)))
    # ⭐⭐⭐⭐ QUI A RAISON : deux points où seul le premier est juste, un pour chaque autre cas, plus un sans couche.
    t_soi = np.array([72.0, 72.0, 72.0, 144.0, 72.0, np.nan])
    pa = np.array([72.0, 72.0, 150.0, 144.0, 10.0, 72.0])
    pb = np.array([150.0, 160.0, 72.0, 144.0, 200.0, 150.0])
    q = qui_a_raison(pa, pb, t_soi, np.ones(6, bool))
    v("★★★★ seul le premier deux fois, puis seul le second, les deux, aucun ; le point sans couche ne compte pas",
      q == {"combien": 5, "seul_le_premier": 0.4, "seul_le_second": 0.2, "les_deux": 0.2, "aucun": 0.2}, str(q))
    v("★★★ un masque vide rend zéro point", qui_a_raison(pa, pb, t_soi, np.zeros(6, bool)) == {"combien": 0})
    # ⚠⚠⚠ LA TACHE AVEUGLE, DÉCLARÉE : deux prédictions qui ratent de la même façon s'accordent, et le raté passe.
    t2 = np.array([72.0, 72.0])
    m = np.array([144.0, 72.0])
    s = np.array([144.0, 144.0])
    dz = le_desaccord(m, s)
    cm = la_confusion(np.abs(m - t2) < DEMI_PAS_EN_VOXELS, ~dz, np.ones(2, bool))
    cs = la_confusion(np.abs(s - t2) < DEMI_PAS_EN_VOXELS, ~dz, np.ones(2, bool))
    v("★★★★ deux ratés identiques s'accordent : le désaccord ne signale rien là", not dz[0])
    v("★★★★ le raté de la seconde seule est signalé, le raté commun non", cs["la_part_des_rates_signales"] == 0.5, str(cs))
    v("★★★ et pour la première, qui avait raison là, c'est un juste signalé à tort",
      cm["la_part_des_justes_signales_a_tort"] == 1.0 and cm["la_part_des_rates_signales"] == 0.0, str(cm))

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
