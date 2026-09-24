"""La surface produite se déchire-t-elle là où elle rate ?

⭐⭐⭐⭐ LA SUITE DE `251`. Là où `m7` et `ps256` s'accordent, elles ratent ensemble environ un point sur vingt, et aucun
contrôle qui relit ces deux prédictions ne le voit. Il reste une information qu'aucune des deux n'a lue : la surface
produite elle-même. La spire voisine est UNE feuille ; une tache partie sur la spire d'après est séparée de ses voisines
par une falaise d'un pas. La machine peut la voir sans juge.

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE. La surface est le premier saut de `247` avec `m7`, relu tel qu'il a été écrit,
sur la maille de huit. Deux mailles voisines, en haut, en bas, à gauche ou à droite, sont CONTINUES si leurs sauts
diffèrent de moins d'un demi-feuillet ; sinon une FALAISE les sépare. Deux détecteurs, sans aucun réglage :
  1. LA FALAISE : un point bordé d'au moins une falaise est signalé ;
  2. HORS DE LA PLUS GRANDE PIÈCE : les mailles reliées par des voisines continues forment des pièces ; tout point hors de
     la plus grande est signalé.
Ils sont notés comme ceux de `250` et `251`, contre la couche que l'objet porte lui-même, avec la réunion des trois
contrôles (le retour, le désaccord et la plus grande pièce), et surtout sur les RATÉS COMMUNS : les points où les deux
prédictions s'accordent et ratent toutes les deux.

⚠⚠ CE QUE LA PIÈCE NE PEUT PAS VOIR, écrit avant de mesurer : une falaise qui coupe la surface d'un bord à l'autre sépare
deux pièces, et la plus petite est signalée même si c'est elle qui est juste. Et une tache qui a sauté une spire sans
falaise, parce que tout son bord a sauté avec elle, est dans la plus grande pièce.

Usage :
    uv run python src/nappe/la_surface_produite_se_dechire_t_elle.py --verifier
    uv run python src/nappe/la_surface_produite_se_dechire_t_elle.py --json docs/mesures/la_surface_produite_se_dechire_t_elle.json
    uv run python src/nappe/la_surface_produite_se_dechire_t_elle.py --segment 20230702185753 \\
        --json docs/mesures/la_surface_produite_du_segment_5753.json
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

from deux_predictions_trahissent_elles_le_saut_rate import le_desaccord  # noqa: E402
from la_bande_a_t_elle_manque_un_tour import les_groupes  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, les_normales,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_retour_trahit_il_le_saut_rate import aller_retour, la_confusion  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS,  # noqa: E402
                                                       les_couches_ordonnees, lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LES_PREDICTIONS,  # noqa: E402
                                                         le_facteur, lecteur_du_depot)

LES_VOISINS = ((0, 1), (1, 0))   # à droite et en bas ; les deux autres sens sont les mêmes arêtes lues à l'envers


def les_aretes(carte: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Pour chaque sens, les couples de mailles voisines présentes, et s'ils sont continus (moins d'un demi-feuillet)."""
    h, w = carte.shape
    out = []
    for di, dj in LES_VOISINS:
        a = carte[:h - di, :w - dj]
        b = carte[di:, dj:]
        present = np.isfinite(a) & np.isfinite(b)
        with np.errstate(invalid="ignore"):
            continu = present & (np.abs(a - b) < DEMI_PAS_EN_VOXELS)
        out.append((present, continu, (di, dj)))
    return out


def la_falaise(carte: np.ndarray) -> np.ndarray:
    """Les mailles bordées d'au moins une falaise : une voisine présente à un demi-feuillet ou plus."""
    h, w = carte.shape
    borde = np.zeros((h, w), dtype=bool)
    for present, continu, (di, dj) in les_aretes(carte):
        f = present & ~continu
        borde[:h - di, :w - dj] |= f
        borde[di:, dj:] |= f
    return borde


def les_pieces(carte: np.ndarray) -> tuple[np.ndarray, int]:
    """Les pièces de la surface : les mailles reliées par des voisines continues. Rend l'étiquette de chaque maille (−1
    hors de la surface) et le nombre de pièces."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    h, w = carte.shape
    ids = np.arange(h * w).reshape(h, w)
    lignes, colonnes = [], []
    for _, continu, (di, dj) in les_aretes(carte):
        lignes.append(ids[:h - di, :w - dj][continu])
        colonnes.append(ids[di:, dj:][continu])
    li, co = np.concatenate(lignes), np.concatenate(colonnes)
    g = coo_matrix((np.ones(len(li)), (li, co)), shape=(h * w, h * w))
    n, etiquette = connected_components(g, directed=False)
    etiquette = etiquette.reshape(h, w)
    etiquette[~np.isfinite(carte)] = -1
    uniques = np.unique(etiquette[etiquette >= 0])
    renum = {int(u): k for k, u in enumerate(uniques)}
    out = np.full((h, w), -1)
    for u, k in renum.items():
        out[etiquette == u] = k
    return out, len(uniques)


def hors_de_la_plus_grande_piece(carte: np.ndarray) -> tuple[np.ndarray, dict]:
    """Les mailles présentes hors de la plus grande pièce, et le compte des pièces."""
    et, n = les_pieces(carte)
    if not n:
        return np.zeros(carte.shape, dtype=bool), {"les_pieces": 0}
    tailles = np.bincount(et[et >= 0], minlength=n)
    grande = int(np.argmax(tailles))
    return (et >= 0) & (et != grande), {"les_pieces": int(n), "la_plus_grande": int(tailles[grande]),
                                        "la_suivante": int(np.sort(tailles)[-2]) if n > 1 else 0,
                                        "les_mailles": int((et >= 0).sum())}


LA_FENETRE = 120   # colonnes de la maille


def la_fenetre(chaine: np.ndarray, bande: np.ndarray, sauts: np.ndarray, largeur: int = LA_FENETRE) -> dict:
    """Les `largeur` colonnes consécutives qui portent le plus de points du masque `sauts`, la première en cas d'égalité ;
    les deux cartes y sont rendues en voxels à un dixième près, NaN en `None`."""
    par_colonne = sauts.sum(axis=0)
    cumul = np.concatenate([[0], np.cumsum(par_colonne)])
    fen = cumul[largeur:] - cumul[:-largeur] if len(par_colonne) > largeur else np.array([cumul[-1]])
    a = int(np.argmax(fen))
    b = min(a + largeur, chaine.shape[1])

    def rendre(m):
        return [[None if not np.isfinite(x) else round(float(x), 1) for x in ligne] for ligne in m[:, a:b]]

    return {"les_colonnes": [a, b], "les_sauts_dans_la_fenetre": int(sauts[:, a:b].sum()),
            "la_chaine": rendre(chaine), "la_bande": rendre(bande),
            "les_sauts": [[bool(x) for x in ligne] for ligne in sauts[:, a:b]]}


def la_part_bordee(falaise: np.ndarray, groupe: np.ndarray) -> float | None:
    """La part des points d'un groupe qui sont bordés d'une falaise."""
    return round(float(falaise[groupe].mean()), 4) if groupe.any() else None


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
           "les_points": int(len(p)), "la_forme_de_la_maille": list(forme)}
    for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
        t_soi = couches[cote_][gi, gj, 0]
        note = np.isfinite(t_soi)
        sauts = {}
        for nom_p in ("m7", "ps256"):
            f = cache / f"transfert_suivante_{segment}_{nom_p}_{nom}.npy"
            if not f.exists():
                return {"decidable": False, "la_raison": f"le premier saut de 247 manque : {f.name}"}
            sauts[nom_p] = np.load(f)[gi, gj]
        carte = sur_la_grille(sauts["m7"])
        falaise = la_falaise(carte)[gi, gj]
        hors, pieces = hors_de_la_plus_grande_piece(carte)
        hors = hors[gi, gj]
        ar = aller_retour(p, n, cote, lire_rayon, sur_la_grille, gi, gj)
        desaccord = le_desaccord(sauts["m7"], sauts["ps256"])
        with np.errstate(invalid="ignore"):
            bon = np.abs(sauts["m7"] - t_soi) < DEMI_PAS_EN_VOXELS
            bon_ps = np.abs(sauts["ps256"] - t_soi) < DEMI_PAS_EN_VOXELS
        communs = note & ~desaccord & ~bon & ~bon_ps
        signale = {"la_falaise": falaise, "hors_de_la_plus_grande_piece": hors,
                   "le_retour_et_le_desaccord": ~ar["coherent"] | desaccord,
                   "les_trois": ~ar["coherent"] | desaccord | hors}
        r = {"laller_contre_247_ecart_max_voxels": round(float(np.nanmax(np.abs(ar["le_pas_de_laller"] - sauts["m7"]))), 4),
             "les_pieces": pieces,
             "la_part_bordee_dune_falaise": round(float(falaise.mean()), 4),
             "la_part_hors_de_la_plus_grande_piece": round(float(hors.mean()), 4),
             "les_detecteurs": {k: la_confusion(bon, ~s, note) for k, s in signale.items()},
             "les_rates_communs": {"combien": int(communs.sum()),
                                   "la_part_des_notes": round(float(communs[note].mean()), 4) if note.any() else None,
                                   **{f"la_part_signalee_par_{k}": (round(float(s[communs].mean()), 4) if communs.any() else None)
                                      for k, s in signale.items()}}}
        # ⚠⚠⚠ AJOUTÉ APRÈS LA MESURE, ET DIT COMME TEL : la surface de la chaîne tient presque entière en une pièce,
        # donc ses ratés ne s'en détachent pas. `249` laisse ouverte la question de savoir si, là où la bande saute, c'est
        # la bande qui a manqué un tour. Une feuille ne saute pas d'un tour entre deux mailles voisines : la même règle
        # de falaise est donc lue sur la couche de la bande, par groupe de `249`, à côté de celle de la chaîne.
        falaise_bande = la_falaise(sur_la_grille(t_soi))[gi, gj]
        gr = les_groupes(sauts["m7"], t_soi, cote)
        r["les_falaises_par_groupe"] = {k: {"combien": int(g.sum()),
                                            "bordes_dans_la_surface_de_la_chaine": la_part_bordee(falaise, g),
                                            "bordes_dans_la_couche_de_la_bande": la_part_bordee(falaise_bande, g)}
                                        for k, g in gr.items()}
        # ⚠ UNE BORNE, PAS UNE MESURE : la part juste du premier saut si toutes les chutes où la bande saute étaient des
        # défauts du juge. Elle dit ce qui est en jeu, jamais ce qui est vrai.
        saute = gr["trop_pres_la_ou_la_bande_saute"]
        r["la_part_juste_au_plus_si_les_chutes_ou_la_bande_saute_etaient_justes"] = (
            round(float((bon | saute)[note].mean()), 4) if note.any() else None)
        # ⚠ LA FENÊTRE QUE LA FIGURE DESSINE, choisie par une règle et non à l'œil : les colonnes de la maille qui portent
        # le plus de chutes où la bande saute, sur la largeur de `LA_FENETRE`.
        if segment == LA_BANDE:
            r["la_fenetre"] = la_fenetre(sur_la_grille(sauts["m7"]), sur_la_grille(t_soi),
                                         np.isfinite(sur_la_grille(np.where(saute, 1.0, np.nan))))
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
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points sur une maille {r['la_forme_de_la_maille']}, "
          f"{r['les_secondes']} s")
    for nom in ("du_cote_plus", "du_cote_moins"):
        x = r[nom]
        print(f"— {nom} : aller contre 247 {x['laller_contre_247_ecart_max_voxels']}, pièces {x['les_pieces']}, bordés "
              f"{x['la_part_bordee_dune_falaise']}, hors de la plus grande {x['la_part_hors_de_la_plus_grande_piece']}")
        for k, c in x["les_detecteurs"].items():
            print(f"    {k:30s} ratés signalés {c['la_part_des_rates_signales']}  justes à tort "
                  f"{c['la_part_des_justes_signales_a_tort']}  ratés parmi signalés {c['la_part_ratee_parmi_les_signales']}"
                  f"  juste {c['la_part_juste_a_laller']} → {c['la_part_juste_parmi_les_gardes']} (gardés {c['la_part_gardee']})")
        print(f"    ratés communs {x['les_rates_communs']}")
        print(f"    part juste au plus {x['la_part_juste_au_plus_si_les_chutes_ou_la_bande_saute_etaient_justes']}")
        for k, g in x["les_falaises_par_groupe"].items():
            print(f"    falaises, {k:34s} {g}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ UNE TACHE PARTIE SUR LA SPIRE D'APRÈS : trois sur trois au milieu d'une surface à un pas.
    c = np.full((10, 10), 72.0)
    c[4:7, 4:7] = 144.0
    f = la_falaise(c)
    v("★★★★ la falaise borde la tache des deux côtés : ses huit mailles de bord et les douze qui la touchent",
      f.sum() == 20 and not f[5, 5] and f[4, 4] and f[3, 5] and not f[0, 0], str(int(f.sum())))
    hors, pc = hors_de_la_plus_grande_piece(c)
    v("★★★★ la tache est hors de la plus grande pièce, et elle seule", hors.sum() == 9 and hors[4:7, 4:7].all(), str(pc))
    v("★★★ deux pièces : la surface et la tache", pc["les_pieces"] == 2 and pc["la_plus_grande"] == 91 and pc["la_suivante"] == 9)
    # ⚠⚠ UNE PENTE DOUCE N'EST PAS UNE FALAISE : l'écart varie de vingt voxels d'un bord à l'autre, par pas de deux.
    pente = 72.0 + 2.0 * np.arange(10)[None, :] * np.ones((10, 1))
    v("★★★★ une pente douce n'a aucune falaise et tient en une pièce",
      not la_falaise(pente).any() and hors_de_la_plus_grande_piece(pente)[1]["les_pieces"] == 1)
    # ⚠⚠ UN TROU N'EST PAS UNE FALAISE, MAIS IL PEUT SÉPARER : une colonne vide coupe la surface en deux pièces.
    trou = np.full((6, 9), 72.0)
    trou[:, 4] = np.nan
    ht, pt = hors_de_la_plus_grande_piece(trou)
    v("★★★ une colonne vide ne borde aucune maille d'une falaise", not la_falaise(trou).any())
    v("★★★ mais elle coupe la surface en deux pièces égales, et l'une est signalée", pt["les_pieces"] == 2
      and ht.sum() == 24 and not ht[:, 4].any(), str(pt))
    # ⚠⚠⚠ LA TACHE AVEUGLE, DÉCLARÉE : une falaise d'un bord à l'autre sépare deux pièces, et la plus petite est signalée
    # même si c'est elle qui est juste.
    coupe = np.full((6, 10), 72.0)
    coupe[:, 6:] = 144.0
    hc, _ = hors_de_la_plus_grande_piece(coupe)
    v("★★★★ une falaise d'un bord à l'autre fait signaler toute la plus petite pièce", hc.sum() == 24 and hc[:, 6:].all())
    # ⚠ LES DIAGONALES NE SONT PAS DES VOISINES : deux mailles qui ne se touchent que par un coin sont deux pièces.
    coin = np.full((3, 3), np.nan)
    coin[0, 0] = 72.0
    coin[1, 1] = 72.0
    v("★★★ deux mailles qui ne se touchent que par un coin sont deux pièces", hors_de_la_plus_grande_piece(coin)[1]["les_pieces"] == 2)
    v("★★★ la part bordée d'un groupe", la_part_bordee(f.ravel(), np.r_[np.ones(4, bool), np.zeros(96, bool)]) == 0.0
      and la_part_bordee(f.ravel(), f.ravel()) == 1.0 and la_part_bordee(f.ravel(), np.zeros(100, bool)) is None)
    msk = np.zeros((3, 10), bool)
    msk[:, 6] = True
    msk[0, 7] = True
    fe = la_fenetre(np.zeros((3, 10)), np.full((3, 10), np.nan), msk, 3)
    v("★★★ la fenêtre prend les colonnes qui portent le plus de sauts, et rend NaN en rien",
      fe["les_colonnes"] == [5, 8] and fe["les_sauts_dans_la_fenetre"] == 4 and fe["la_bande"][0][0] is None, str(fe["les_colonnes"]))
    v("★★ une surface vide n'a aucune pièce", hors_de_la_plus_grande_piece(np.full((3, 3), np.nan))[1]["les_pieces"] == 0)

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
