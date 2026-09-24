"""Enchaîner le transfert de spire en spire tient-il plusieurs tours ?

⭐⭐⭐⭐ LA SUITE DIRECTE DE `247`. Un transfert fait passer d'une spire à la suivante ; dérouler un rouleau
en demande des dizaines d'affilée, et c'est là qu'un humain corrige aujourd'hui. Cette mesure enchaîne
quatre transferts et compte, à chaque saut, la part des points qui retombent sur la bonne spire. Un saut
raté est définitif : la chaîne reste décalée d'une spire pour tous les sauts suivants.

⭐⭐⭐⭐ LE JUGE EST LA BANDE `20260623142658-w028-037`, QUI TRACE DIX SPIRES D'UN SEUL TENANT. En face d'un
de ses points, la bande porte elle-même ses tours voisins : la h-ième couche rencontrée le long de la
normale, du même côté, est le tour situé h spires plus loin. Elle a été tracée par d'autres, sans rien
savoir de cette méthode. La tranche est celle de `247` (les rangées de 0,45 à 0,55, toutes les colonnes).
Le segment `20230702185753` est le second objet, noté pour les couches qu'il porte.

⚠⚠⚠ LES PROCÉDURES SONT DÉCLARÉES AVANT LA MESURE, et elles sont quatre :
  1. LE TÉMOIN : h pas le long de la normale du segment, sans rien lire.
  2. LE COMPTE SUR UN RAYON : le long de la normale du segment, on passe la feuille du segment et on
     prend la h-ième feuille suivante ; puis le vote itéré de `247`. Un seul rayon droit, lu une fois, de
     la feuille du segment jusqu'à deux pas au-delà du dernier saut.
  3. LA CHAÎNE : h transferts de `247` (la feuille suivante, puis le vote), chacun parti de la surface
     que le précédent a produite, le long de SA normale. C'est la procédure qui déroule.
  4. LA CHAÎNE LE LONG DE LA NORMALE DU SEGMENT : la même chaîne, sans recalculer la normale. Elle n'est
     pas une concurrente : son écart à la chaîne dit ce que coûte la normale estimée, et son écart au
     compte sur un rayon ce que coûte de repartir de la surface produite.

⚠⚠ LA NORMALE D'UNE SURFACE PRODUITE est prise sur la maille elle-même : différences centrées, sinon d'un
seul côté au bord ou contre un trou, et l'orientation du × dv du maillage. Là où aucune différence n'est
possible, la normale du saut précédent est reprise, et c'est compté.

⚠⚠ UN POINT EST JUGÉ SUR SA PROFONDEUR LE LONG DE LA NORMALE DU SEGMENT : au saut h, il est sur la bonne
spire s'il en est à moins d'un demi-feuillet de la h-ième couche. La dérive latérale de la chaîne est
rendue à côté, pour qu'on voie ce que cette projection néglige.

⚠ LA COUCHE h EST LA h-IÈME PLAGE DE PROFONDEURS séparée de la précédente par plus d'un demi-feuillet. Là
où la bande n'a pas tracé un tour, la couche suivante est comptée à sa place, et un transfert juste y
est noté faux : c'est la même réserve que `247`, et elle est dite au lieu d'être corrigée par un pas.

Usage :
    uv run python src/nappe/le_transfert_enchaine_tient_il_les_spires.py --verifier
    uv run python src/nappe/le_transfert_enchaine_tient_il_les_spires.py \\
        --json docs/mesures/le_transfert_enchaine_tient_il_les_spires.json
    uv run python src/nappe/le_transfert_enchaine_tient_il_les_spires.py --segment 20230702185753 \\
        --json docs/mesures/le_transfert_enchaine_sur_le_segment_5753.json
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
                                                _spirale, les_couches_du_segment, les_normales,
                                                lire_tifxyz, telecharger)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LA_PORTEE,  # noqa: E402
                                                         LE_CONTROLE, LES_PREDICTIONS,
                                                         la_carte_des_issues, la_feuille_suivante,
                                                         le_facteur, le_vote_itere, lecteur_du_depot,
                                                         les_centres, lire_les_valeurs)

LA_BANDE = "20260623142658-w028-037"
LA_TRANCHE = (0.45, 0.55)
LES_SAUTS = 4
LE_PAQUET = 2000   # les points interrogés à la fois dans l'arbre, pour borner la mémoire


def les_couches_ordonnees(ref: np.ndarray, valide: np.ndarray, espacement: float, maille: int = LA_MAILLE,
                          sauts: int = LES_SAUTS, pas_du_nuage: int = 2) -> dict:
    """La h-ième couche du segment en face de chacun de ses points, de chaque côté, h = 1 à `sauts`.

    Les bornes sont celles de `les_couches_du_segment` : l'écart latéral, la distance sur la surface, et
    un rayon d'un demi-pas au-delà du dernier saut, comme les trois pas et demi de `246` pour trois tours.
    Les profondeurs retenues sont triées et coupées là où deux se suivent à plus d'un demi-feuillet ; la
    couche h est la plus proche de la h-ième plage.
    """
    from scipy.spatial import cKDTree

    rayon = (sauts + 0.5) * PAS_EN_VOXELS
    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    ni, nj = np.nonzero(valide[::pas_du_nuage, ::pas_du_nuage])
    ni, nj = ni * pas_du_nuage, nj * pas_du_nuage
    nuage = ref[ni, nj]
    lateral_max = espacement * pas_du_nuage
    loin_min = int(np.ceil(rayon * np.sqrt(2.0) / espacement)) + 1
    plus = np.full((len(p), sauts), np.nan)
    moins = np.full((len(p), sauts), np.nan)
    arbre = cKDTree(nuage)
    for a in range(0, len(p), LE_PAQUET):
        for k, lst in enumerate(arbre.query_ball_point(p[a:a + LE_PAQUET], r=rayon), start=a):
            if not lst:
                continue
            lst = np.asarray(lst)
            d = nuage[lst] - p[k]
            t = d @ n[k]
            lat = np.linalg.norm(d - t[:, None] * n[k], axis=1)
            loin = (np.abs(ni[lst] - ii[k]) + np.abs(nj[lst] - jj[k])) > loin_min
            garde = (lat <= lateral_max) & loin
            for signe, dest in ((1.0, plus), (-1.0, moins)):
                prof = np.sort(signe * t[garde & (signe * t > 0)])
                if not len(prof):
                    continue
                debuts = np.concatenate([[0], np.flatnonzero(np.diff(prof) > DEMI_PAS_EN_VOXELS) + 1])[:sauts]
                dest[k, :len(debuts)] = signe * prof[debuts]
    forme = np.full(ok.shape, np.nan)[::maille, ::maille].shape
    cartes = {}
    for nom, v in (("plus", plus), ("moins", moins)):
        c = np.full(forme + (sauts,), np.nan)
        c[ii // maille, jj // maille] = v
        cartes[nom] = c
    return {"le_rayon_voxels": round(rayon, 4), "la_distance_sur_la_surface_min_mailles": loin_min,
            "les_cartes": cartes}


def la_hieme_feuille(t: np.ndarray, vu: np.ndarray, h: int) -> np.ndarray:
    """Le centre de la h-ième plage de feuille après celle du segment ; NaN si le rayon n'en voit pas
    autant. Au premier rang, c'est `la_feuille_suivante` de `247`."""
    out = np.full(vu.shape[0], np.nan)
    a_t = np.abs(t)
    for k in range(vu.shape[0]):
        m = vu[k]
        if not m.any():
            continue
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        plages = list(zip(bords[::2], bords[1::2]))
        suivantes = [(a, b) for a, b in plages if a_t[a] > LE_CONTROLE]
        propre = [(a, b) for a, b in plages if a_t[a] <= LE_CONTROLE]
        if propre:
            fin = propre[0][1]
            suivantes = [(a, b) for a, b in plages if a >= fin]
        if len(suivantes) >= h:
            a, b = suivantes[h - 1]
            out[k] = (t[a] + t[b - 1]) / 2.0
    return out


def les_normales_de_la_grille(q: np.ndarray, parent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Les normales d'une surface donnée sur la maille (NaN hors d'elle), orientées du × dv comme le
    maillage : différences centrées, sinon d'un seul côté. Là où aucune n'existe, la normale `parent`.
    Rend aussi le masque des normales calculées."""
    pad = np.pad(q, ((1, 1), (1, 1), (0, 0)), constant_values=np.nan)
    c = pad[1:-1, 1:-1]
    c_ok = np.isfinite(c).all(-1)

    def derivee(avant, arriere):
        a_ok, r_ok = np.isfinite(avant).all(-1), np.isfinite(arriere).all(-1)
        both = a_ok & r_ok
        out = np.where(both[..., None], (avant - arriere) / 2.0, np.nan)
        seul_a = ~both & a_ok & c_ok
        out = np.where(seul_a[..., None], avant - c, out)
        seul_r = ~both & ~seul_a & r_ok & c_ok
        return np.where(seul_r[..., None], c - arriere, out)

    du = derivee(pad[1:-1, 2:], pad[1:-1, :-2])
    dv = derivee(pad[2:, 1:-1], pad[:-2, 1:-1])
    cr = np.cross(du, dv)
    norme = np.linalg.norm(cr, axis=-1)
    ok = c_ok & np.isfinite(norme) & (norme > 0)
    with np.errstate(all="ignore"):
        n = np.where(ok[..., None], cr / norme[..., None], parent)
    return n, ok


def lire_le_rayon(q: np.ndarray, nq: np.ndarray, cote: float, portee: float, facteur: int, pred: dict,
                  lire) -> tuple[np.ndarray, np.ndarray]:
    """Le rayon de chaque point, de sa feuille jusqu'à `portee`, et ce que la prédiction y voit."""
    t = cote * np.arange(0.0, np.floor(portee) + 1.0)
    idx = np.floor((q[:, None, :] + t[None, :, None] * nq[:, None, :])[..., ::-1] / facteur).astype(np.int64)
    return t, lire_les_valeurs(idx, pred, lire) > 0


def compter_sur_un_rayon(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj) -> list[np.ndarray]:
    """La h-ième feuille après celle du segment, le long de sa normale, puis le vote ; h = 1 à `sauts`."""
    t, vu = lire_rayon(p, n, cote, (sauts + 2) * PAS_EN_VOXELS)
    centres = les_centres(t, vu)
    out = []
    for h in range(1, sauts + 1):
        f = la_hieme_feuille(t, vu, h)
        vote, _ = le_vote_itere(centres, np.where(np.isfinite(f), f, cote * h * PAS_EN_VOXELS),
                                sur_la_grille, gi, gj)
        out.append(vote)
    return out


def enchainer(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj, recalculer: bool = True) -> list[dict]:
    """Les sauts successifs de `247`, chacun parti de la surface produite par le précédent.

    Avec `recalculer`, chaque saut suit la normale de la surface d'où il part ; sans, celle du segment."""
    q, nq = p.copy(), n.copy()
    out = []
    for _ in range(sauts):
        t, vu = lire_rayon(q, nq, cote, LA_PORTEE)
        suivante = la_feuille_suivante(t, vu)
        depart = np.where(np.isfinite(suivante), suivante, cote * PAS_EN_VOXELS)
        pas, changes = le_vote_itere(les_centres(t, vu), depart, sur_la_grille, gi, gj)
        q = q + pas[:, None] * nq
        calcule = np.ones(len(q), dtype=bool)
        if recalculer:
            grille_q = np.stack([sur_la_grille(q[:, a]) for a in range(3)], axis=-1)
            grille_n = np.stack([sur_la_grille(nq[:, a]) for a in range(3)], axis=-1)
            ng, okg = les_normales_de_la_grille(grille_q, grille_n)
            nq, calcule = ng[gi, gj], okg[gi, gj]
        out.append({"q": q.copy(), "n": nq.copy(), "le_pas": pas, "calcule": calcule,
                    "les_tours_de_vote": len(changes)})
    return out


def juger_le_saut(tau: np.ndarray, t_soi: np.ndarray, cote: float, h: int) -> dict:
    """La profondeur atteinte au saut h contre la h-ième couche, et le témoin qui avance de h pas."""
    note = np.isfinite(t_soi)
    r = {"les_points_notes": int(note.sum())}
    if not note.any():
        return r
    naif = cote * h * PAS_EN_VOXELS - t_soi[note]
    err = tau[note] - t_soi[note]
    trouve = np.isfinite(err)
    e = np.where(trouve, err, np.nan)
    r["le_temoin_sans_lecture"] = {
        "la_part_sur_la_bonne_spire": round(float((np.abs(naif) < DEMI_PAS_EN_VOXELS).mean()), 4),
        "lerreur_mediane_voxels": round(float(np.median(np.abs(naif))), 4)}
    with np.errstate(invalid="ignore"):
        r["le_transfert"] = {
            "la_part_sur_la_bonne_spire": round(float((np.abs(e) < DEMI_PAS_EN_VOXELS).mean()), 4),
            "la_part_trop_loin": round(float((cote * e >= DEMI_PAS_EN_VOXELS).mean()), 4),
            "la_part_trop_pres": round(float((cote * e <= -DEMI_PAS_EN_VOXELS).mean()), 4),
            "lerreur_mediane_voxels": round(float(np.nanmedian(np.abs(e))), 4) if trouve.any() else None}
    return r


def la_part_qui_tient(bons: list[np.ndarray], notes: list[np.ndarray]) -> dict:
    """La part des points qui tiennent chaque saut, parmi ceux qui ont tenu le précédent, et la part qui
    tient tous les sauts d'affilée, parmi ceux qui ont une couche à chaque saut."""
    out = {"parmi_ceux_qui_ont_tenu_le_saut_precedent": []}
    tenu = np.ones_like(bons[0])
    for b, nt in zip(bons, notes):
        base = tenu & nt
        out["parmi_ceux_qui_ont_tenu_le_saut_precedent"].append(
            round(float(b[base].mean()), 4) if base.any() else None)
        tenu = tenu & nt & b
    tous = np.logical_and.reduce(notes)
    out["les_points_notes_a_chaque_saut"] = int(tous.sum())
    out["la_part_qui_tient_tous_les_sauts"] = (round(float(np.logical_and.reduce(bons)[tous].mean()), 4)
                                              if tous.any() else None)
    return out


def les_rates(tau: np.ndarray, verite: list[np.ndarray], h: int, cote: float) -> dict:
    """Où tombent les points ratés au saut h : trop près, et parmi eux ceux qui sont restés sur la couche
    d'avant, ou là où la bande elle-même saute plus d'un pas et demi d'une couche à la suivante (le juge a
    peut-être compté un tour qu'elle n'a pas tracé) ; trop loin, et parmi eux ceux qui sont sur la couche
    d'après."""
    t = verite[h - 1]
    avant = verite[h - 2] if h > 1 else np.zeros_like(t)
    note = np.isfinite(t) & np.isfinite(avant)
    with np.errstate(invalid="ignore"):
        err = cote * (tau - t)
        pres = note & (err <= -DEMI_PAS_EN_VOXELS)
        loin = note & (err >= DEMI_PAS_EN_VOXELS)
        sur_avant = np.abs(tau - avant) < DEMI_PAS_EN_VOXELS
        saut = np.abs(t - avant) > PAS_EN_VOXELS + DEMI_PAS_EN_VOXELS
    out = {"les_points_notes": int(note.sum()), "trop_pres": int(pres.sum()), "trop_loin": int(loin.sum())}
    if pres.any():
        out["trop_pres_dont_sur_la_couche_davant"] = round(float(sur_avant[pres].mean()), 4)
        out["trop_pres_dont_la_ou_la_bande_saute_plus_dun_pas_et_demi"] = round(float(saut[pres].mean()), 4)
    if h < len(verite) and loin.any():
        apres = verite[h]
        with np.errstate(invalid="ignore"):
            out["trop_loin_dont_sur_la_couche_dapres"] = round(float((np.abs(tau - apres) < DEMI_PAS_EN_VOXELS)[loin].mean()), 4)
    with np.errstate(invalid="ignore"):
        out["la_part_des_notes_ou_la_bande_saute_plus_dun_pas_et_demi"] = round(float(saut[note].mean()), 4) if note.any() else None
    return out


def mesurer(cache: Path = LE_CACHE, maille: int = LA_MAILLE, delai: float = DELAI, segment: str = LA_BANDE,
            rangees: tuple[float, float] | None = LA_TRANCHE, sauts: int = LES_SAUTS) -> dict:
    debut = time.monotonic()
    d = telecharger(segment, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, valide, esp = lire_tifxyz(d)
    if rangees is not None:
        h = ref.shape[0]
        a, b = int(h * rangees[0]), int(h * rangees[1])
        ref, valide = ref[a:b], valide[a:b]
    couches = les_couches_ordonnees(ref, valide, esp, maille, sauts)
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

    present = np.isfinite(sur_la_grille(np.zeros(len(gi))))
    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None, "la_maille": maille,
           "les_points": int(len(p)), "les_sauts": sauts, "le_rayon_des_couches_voxels": couches["le_rayon_voxels"],
           "les_couches": {}, "les_controles": {}, "les_predictions": {}}
    # ⚠⚠ LA PREMIÈRE COUCHE EST CELLE DE `247` : là où `247` a une couche, elle est la même.
    v1 = les_couches_du_segment(ref, valide, esp, maille)["les_cartes"]
    for cote_, nom in (("plus", "du_cote_plus"), ("moins", "du_cote_moins")):
        c = couches["les_cartes"][cote_]
        out["les_couches"][nom] = [round(float(np.isfinite(c[gi, gj, k]).mean()), 4) for k in range(sauts)]
        a1, b1 = c[gi, gj, 0], v1[cote_][gi, gj]
        les_deux = np.isfinite(a1) & np.isfinite(b1)
        out["les_controles"][f"la_premiere_couche_est_celle_de_247_{nom}"] = {
            "les_points_ou_247_a_une_couche": int(np.isfinite(b1).sum()),
            "lecart_max_voxels": round(float(np.abs(a1[les_deux] - b1[les_deux]).max()), 4) if les_deux.any() else None,
            "les_points_ou_247_en_a_une_et_pas_ici": int((np.isfinite(b1) & ~np.isfinite(a1)).sum()),
            "les_points_ou_les_deux_different": int((np.abs(a1[les_deux] - b1[les_deux]) > 1e-6).sum()),
            "les_points_ou_les_deux_different_de_plus_dun_demi_feuillet": int(
                (np.abs(a1[les_deux] - b1[les_deux]) >= DEMI_PAS_EN_VOXELS).sum())}
    # ⚠⚠ LA NORMALE DE LA MAILLE contre celle du maillage, sur le segment lui-même : c'est l'estimateur que
    # la chaîne emploie à chaque saut, mesuré là où la vraie normale est connue.
    ng, okg = les_normales_de_la_grille(np.stack([sur_la_grille(p[:, a]) for a in range(3)], axis=-1),
                                        np.stack([sur_la_grille(n[:, a]) for a in range(3)], axis=-1))
    ang = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", ng[gi, gj], n), -1, 1)))
    out["les_controles"]["la_normale_de_la_maille_contre_celle_du_maillage_degres"] = {
        "mediane": round(float(np.median(ang)), 4), "q95": round(float(np.percentile(ang, 95)), 4)}
    for nom_p, (chemin, niveau) in LES_PREDICTIONS.items():
        facteur, pred = le_facteur(chemin, niveau, delai)
        lire, stats = lecteur_du_depot(pred, cache, nom_p, chemin, niveau, delai)

        def lire_rayon(q, nq, cote, portee):
            return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

        r = {"le_facteur": facteur}
        for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
            verite = [couches["les_cartes"][cote_][gi, gj, k] for k in range(sauts)]
            notes = [np.isfinite(v) for v in verite]
            compte = compter_sur_un_rayon(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj)
            chaine = enchainer(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj, True)
            droite = enchainer(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj, False)
            ancien = cache / f"transfert_suivante_{segment}_{nom_p}_{nom}.npy"
            le_premier = None
            if ancien.exists():
                a0 = np.load(ancien)[gi, gj]
                le_premier = round(float(np.nanmax(np.abs(a0 - chaine[0]["le_pas"]))), 4)
            procs = {"le_compte_sur_un_rayon": compte,
                     "la_chaine": [np.einsum("ij,ij->i", s["q"] - p, n) for s in chaine],
                     "la_chaine_le_long_de_la_normale_du_segment": [np.einsum("ij,ij->i", s["q"] - p, n)
                                                                    for s in droite]}
            rs = {"le_premier_saut_contre_celui_de_247_ecart_max_voxels": le_premier, "les_sauts": []}
            bons = {k: [] for k in procs}
            temoin = []
            for h in range(1, sauts + 1):
                jh = {}
                for k, taus in procs.items():
                    j = juger_le_saut(taus[h - 1], verite[h - 1], cote, h)
                    jh[k] = j.get("le_transfert")
                    jh["le_temoin_sans_lecture"] = j.get("le_temoin_sans_lecture")
                    jh["les_points_notes"] = j["les_points_notes"]
                    with np.errstate(invalid="ignore"):
                        bons[k].append(np.abs(taus[h - 1] - verite[h - 1]) < DEMI_PAS_EN_VOXELS)
                temoin.append(np.abs(cote * h * PAS_EN_VOXELS - verite[h - 1]) < DEMI_PAS_EN_VOXELS)
                s = chaine[h - 1]
                dq = s["q"] - p
                lat = np.linalg.norm(dq - np.einsum("ij,ij->i", dq, n)[:, None] * n, axis=1)
                jh["la_chaine_en_detail"] = {
                    "la_derive_laterale_mediane_voxels": round(float(np.median(lat)), 4),
                    "langle_median_a_la_normale_du_segment_degres": round(float(np.median(np.degrees(np.arccos(
                        np.clip(np.einsum("ij,ij->i", s["n"], n), -1, 1))))), 4),
                    "la_part_des_normales_reprises": round(float((~s["calcule"]).mean()), 4),
                    # ⚠⚠ UN SAUT QUI N'AVANCE PAS D'UN DEMI-FEUILLET est resté sur la feuille d'où il partait : la
                    # plage de départ n'a pas été reconnue comme la sienne, et la chaîne prend une spire de retard.
                    "la_part_des_sauts_qui_navancent_pas": round(float((np.abs(s["le_pas"]) < DEMI_PAS_EN_VOXELS).mean()), 4),
                    "les_tours_de_vote": s["les_tours_de_vote"]}
                rs["les_sauts"].append(jh)
            rs["qui_tient"] = {k: la_part_qui_tient(b, notes) for k, b in bons.items()}
            # ⚠⚠ LA COURBE PAR SAUT, SUR LES MÊMES POINTS À CHAQUE SAUT : sinon la part notée change d'un saut à
            # l'autre (les tours du bord n'ont pas de quatrième couche) et la courbe mêle deux effets.
            fixe = np.logical_and.reduce(notes)
            rs["sur_les_points_notes_a_chaque_saut"] = {"les_points": int(fixe.sum())}
            for k, b in list(bons.items()) + [("le_temoin_sans_lecture", temoin)]:
                rs["sur_les_points_notes_a_chaque_saut"][k] = ([round(float(x[fixe].mean()), 4) for x in b]
                                                               if fixe.any() else None)
            rs["les_rates_de_la_chaine"] = [les_rates(procs["la_chaine"][h - 1], verite, h, cote)
                                            for h in range(1, sauts + 1)]
            rs["qui_tient"]["le_temoin_sans_lecture"] = la_part_qui_tient(temoin, notes)
            # ⚠ LES CARTES NE SONT ÉCRITES QUE POUR LA BANDE, que la figure dessine : sur le segment, elles pèseraient
            # le double de la mesure pour des sauts que sa troisième couche ne juge presque nulle part.
            if nom_p == next(iter(LES_PREDICTIONS)) and segment == LA_BANDE:
                rs["les_cartes_de_la_chaine"] = [la_carte_des_issues(procs["la_chaine"][k], verite[k],
                                                                     sur_la_grille, present) for k in range(sauts)]
                rs["les_cartes_du_temoin"] = [la_carte_des_issues(np.full(len(gi), cote * (k + 1) * PAS_EN_VOXELS),
                                                                  verite[k], sur_la_grille, present)
                                              for k in range(sauts)]
            r[nom] = rs
        r["la_lecture"] = {"chunks_lus": stats["lus"], "chunks_absents": stats["absents"],
                           "mo_lus": round(stats["octets"] / 1e6, 1), "les_pannes": stats["pannes"][:20],
                           "combien_de_pannes": len(stats["pannes"])}
        out["les_predictions"][nom_p] = r
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(not r["la_lecture"]["combien_de_pannes"] for r in out["les_predictions"].values())
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points, {r['les_sauts']} sauts, "
          f"{r['les_secondes']} s")
    print(f"  couches présentes : {r['les_couches']}")
    for k, c in r["les_controles"].items():
        print(f"  contrôle {k} : {c}")
    for nom_p, rp in r["les_predictions"].items():
        print(f"— {nom_p} : {rp['la_lecture']['chunks_lus']} chunks, {rp['la_lecture']['combien_de_pannes']} pannes")
        for nom in ("du_cote_plus", "du_cote_moins"):
            rs = rp[nom]
            for h, jh in enumerate(rs["les_sauts"], start=1):
                cells = "   ".join(f"{k.replace('la_chaine_le_long_de_la_normale_du_segment', 'chaîne-droite')} "
                                   f"{(jh[k] or {}).get('la_part_sur_la_bonne_spire')}"
                                   for k in ("le_compte_sur_un_rayon", "la_chaine",
                                             "la_chaine_le_long_de_la_normale_du_segment"))
                print(f"  {nom:14s} saut {h} ({jh['les_points_notes']:6d} notés)  témoin "
                      f"{jh['le_temoin_sans_lecture']['la_part_sur_la_bonne_spire']}   {cells}   "
                      f"{jh['la_chaine_en_detail']}")
            sf = rs["sur_les_points_notes_a_chaque_saut"]
            print(f"  {nom:14s} sur les {sf['les_points']} points notés à chaque saut : " + "   ".join(
                f"{k} {sf[k]}" for k in sf if k != "les_points"))
            for h, rt in enumerate(rs["les_rates_de_la_chaine"], start=1):
                print(f"  {nom:14s} ratés de la chaîne au saut {h} : {rt}")
            for k, q in rs["qui_tient"].items():
                print(f"  {nom:14s} {k:44s} tient tous les sauts {q['la_part_qui_tient_tous_les_sauts']} "
                      f"(sur {q['les_points_notes_a_chaque_saut']})  pas à pas "
                      f"{q['parmi_ceux_qui_ont_tenu_le_saut_precedent']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LA h-IÈME FEUILLE : on passe la sienne et on compte les suivantes, quel que soit leur écart.
    tl = np.arange(0.0, 433.0)
    ray = np.zeros((2, len(tl)), bool)
    ray[:, :4] = True
    for a, b in ((60, 65), (140, 146), (230, 236)):
        ray[0, a:b] = True
    ray[1, 70:76] = True
    v("★★★★ la première feuille est à 62", la_hieme_feuille(tl, ray, 1)[0] == 62.0)
    v("★★★★ la deuxième est à 142,5, pas à deux pas", la_hieme_feuille(tl, ray, 2)[0] == 142.5)
    v("★★★★ la troisième est à 232,5", la_hieme_feuille(tl, ray, 3)[0] == 232.5)
    v("★★★ un rayon qui n'en voit pas autant n'invente pas la quatrième", np.isnan(la_hieme_feuille(tl, ray, 4)[0]))
    v("★★★ ni la deuxième là où il n'en voit qu'une", np.isnan(la_hieme_feuille(tl, ray, 2)[1]))
    v("★★ et elle se lit de l'autre côté", la_hieme_feuille(-tl, ray, 2)[0] == -142.5)
    # ⚠⚠ AU PREMIER RANG, C'EST LA FEUILLE SUIVANTE DE `247`, sur ses propres rayons.
    t7 = np.arange(0.0, 217.0)
    r7 = np.zeros((4, len(t7)), bool)
    r7[:3, :4] = True
    r7[0, 120:126] = True
    r7[1, 40:44] = True
    r7[1, 90:95] = True
    r7[2, 4:6] = False
    r7[3, 70:76] = True
    un, ref7 = la_hieme_feuille(t7, r7, 1), la_feuille_suivante(t7, r7)
    v("★★★★ au premier rang la h-ième feuille est la feuille suivante de 247",
      np.array_equal(np.isnan(un), np.isnan(ref7)) and np.allclose(un[np.isfinite(un)], ref7[np.isfinite(ref7)]))

    # ⭐⭐⭐⭐ LES COUCHES ORDONNÉES, sur une spirale de neuf tours : au milieu, la h-ième couche est à h
    # pas, des deux côtés. Et la première est celle de `247`.
    esp = 20.0
    spi, sv = _spirale(9.3, 40, esp, 3000.0)
    co = les_couches_ordonnees(spi, sv, esp, 4, 4)
    milieu = spi.shape[1] // 2
    for cote_, signe in (("plus", 1.0), ("moins", -1.0)):
        c = co["les_cartes"][cote_][:, milieu // 4 - 20: milieu // 4 + 20]
        for h in range(1, 5):
            m = np.nanmedian(signe * c[..., h - 1])
            v(f"★★★★ au milieu de la spirale la couche {h} est à {h} pas, {cote_}",
              abs(m - h * PAS_EN_VOXELS) < 1.0, str(m))
    ref1 = les_couches_du_segment(spi, sv, esp, 4)["les_cartes"]
    les_deux = np.isfinite(ref1["plus"]) & np.isfinite(co["les_cartes"]["plus"][..., 0])
    v("★★★★ la première couche est celle de 247 partout où 247 en a une",
      les_deux.sum() > 100 and np.allclose(ref1["plus"][les_deux], co["les_cartes"]["plus"][..., 0][les_deux]),
      str(int(les_deux.sum())))
    v("★★★ et partout où 247 en a une, elle en a une",
      not (np.isfinite(ref1["plus"]) & ~np.isfinite(co["les_cartes"]["plus"][..., 0])).any())
    # ⚠⚠⚠ UN TOUR NON TRACÉ : la couche suivante prend sa place, et c'est la réserve déclarée.
    sans = sv.copy()
    b = PAS_EN_VOXELS / (2 * np.pi)
    th = np.arctan2(spi[..., 2], spi[..., 0]) % (2 * np.pi)
    rr = np.hypot(spi[..., 0], spi[..., 2])
    tour = np.floor((rr - 3000.0 - b * th) / PAS_EN_VOXELS + 0.5)
    t_milieu = np.median(tour[:, milieu])
    sans[tour == t_milieu + 1] = False
    cs = les_couches_ordonnees(spi, sans, esp, 4, 2)
    cm = cs["les_cartes"]["plus"][:, milieu // 4 - 5: milieu // 4 + 5]
    cm2 = cs["les_cartes"]["moins"][:, milieu // 4 - 5: milieu // 4 + 5]
    ecarts_ = [abs(np.nanmedian(np.abs(c_[..., 0])) - 2 * PAS_EN_VOXELS) for c_ in (cm, cm2)]
    v("★★★ derrière un tour non tracé, la première couche est le tour d'après, à deux pas",
      min(ecarts_) < 1.0, str(ecarts_))

    # ⭐⭐⭐⭐ LA NORMALE DE LA MAILLE, sur un cylindre : radiale, orientée comme celle du maillage.
    R = 3000.0
    arc = np.arange(30) * 160.0 / R
    jj_, ii_ = np.meshgrid(arc, np.arange(12) * 160.0)
    cyl = np.stack([R * np.cos(jj_), ii_, R * np.sin(jj_)], axis=-1)
    fine, fok = les_normales(cyl, np.ones(cyl.shape[:2], bool))
    ng, okg = les_normales_de_la_grille(cyl, np.zeros_like(cyl))
    radial = -cyl / np.linalg.norm(cyl, axis=-1, keepdims=True)
    radial[..., 1] = 0.0
    radial /= np.linalg.norm(radial, axis=-1, keepdims=True)
    signe_ = np.sign(np.einsum("ij,ij->i", fine[fok], radial[fok]).mean())
    ang = np.degrees(np.arccos(np.clip(np.einsum("ijk,ijk->ij", ng, signe_ * radial), -1, 1)))
    v("★★★★ sur un cylindre la normale de la maille est radiale, bords compris", ang.max() < 2.0, str(ang.max()))
    v("★★★★ et orientée comme celle du maillage",
      np.einsum("ij,ij->i", ng[fok], fine[fok]).min() > 0.99)
    v("★★★ toutes sont calculées sur une grille pleine", okg.all())
    trou = cyl.copy()
    trou[5, 10] = np.nan
    par = np.broadcast_to(np.array([0.0, 1.0, 0.0]), cyl.shape).copy()
    ngt, okt = les_normales_de_la_grille(trou, par)
    autour = [(5, 9), (5, 11), (4, 10), (6, 10)]
    v("★★★ contre un trou, la normale est prise d'un seul côté et reste radiale",
      all(okt[a] for a in autour) and max(np.degrees(np.arccos(np.clip(ngt[a] @ (signe_ * radial[a]), -1, 1)))
                                          for a in autour) < 2.0)
    iso = cyl.copy()
    iso[:, :] = np.nan
    iso[6, 15] = cyl[6, 15]
    ngi, oki = les_normales_de_la_grille(iso, par)
    v("★★★★ un point sans aucun voisin reprend la normale du saut précédent, et c'est compté",
      not oki[6, 15] and np.allclose(ngi[6, 15], [0.0, 1.0, 0.0]))

    # ⭐⭐⭐⭐ LA CHAÎNE, sur une prédiction fabriquée : quatre feuilles à des écarts qui ne sont pas un pas.
    f = 4
    pred = {"shape": [128, 32, 32], "chunks": [16, 16, 16], "fill_value": 0}
    vol = np.zeros(pred["shape"], np.uint8)
    z0 = 10
    ecarts = [20, 26, 20, 26]                      # 80, 104, 80, 104 voxels du maillage
    zs = [z0] + list(z0 + np.cumsum(ecarts))
    for z in zs:
        vol[z, :, :] = 255

    def lire(c):
        a = np.asarray(c) * 16
        return vol[a[0]:a[0] + 16, a[1]:a[1] + 16, a[2]:a[2] + 16]

    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))
    pts = np.stack([gj_ * 8.0 + 20.0, gi_ * 8.0 + 20.0, np.full(H * W, z0 * f + 2.0)], axis=-1)
    nor = np.tile([0.0, 0.0, 1.0], (H * W, 1))

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    def lire_rayon(q, nq, cote, portee):
        return lire_le_rayon(q, nq, cote, portee, f, pred, lire)

    vrai = [(z - z0) * f for z in zs[1:]]
    ch = enchainer(pts, nor, 1.0, 4, lire_rayon, grille_, gi_, gj_, True)
    atteint = [np.median(s["q"][:, 2] - pts[:, 2]) for s in ch]
    v("★★★★ la chaîne retrouve les quatre feuilles à leurs vrais écarts, à un voxel de prédiction près",
      all(abs(a - (w_ - 2.0 + f / 2.0)) <= f for a, w_ in zip(atteint, vrai)), f"{atteint} contre {vrai}")
    tem = [abs(h * PAS_EN_VOXELS - (w_ - 2.0)) < DEMI_PAS_EN_VOXELS for h, w_ in enumerate(vrai, start=1)]
    v("★★★ alors que le pas fixe tombe hors de la bonne spire dès le deuxième saut", tem == [True, False, False, False],
      str(tem))
    v("★★★ sur des feuilles planes la normale produite reste celle du segment",
      all(np.allclose(s["n"], nor) for s in ch))
    cr = compter_sur_un_rayon(pts, nor, 1.0, 4, lire_rayon, grille_, gi_, gj_)
    v("★★★★ le compte sur un rayon retrouve les mêmes feuilles",
      all(abs(np.median(c) - np.median(s["q"][:, 2] - pts[:, 2])) <= f for c, s in zip(cr, ch)),
      str([np.median(c) for c in cr]))
    # ⚠⚠⚠ UN SAUT RATÉ EST DÉFINITIF : sans la deuxième feuille, la chaîne tombe sur la troisième au
    # deuxième saut et reste décalée d'une spire au troisième.
    vol[zs[2], :, :] = 0
    ch2 = enchainer(pts, nor, 1.0, 3, lire_rayon, grille_, gi_, gj_, True)
    a2 = [np.median(s["q"][:, 2] - pts[:, 2]) for s in ch2]
    v("★★★★ une feuille que la prédiction manque fait sauter une spire, et la chaîne ne la rattrape pas",
      abs(a2[1] - (vrai[2] - 2.0 + f / 2.0)) <= f and abs(a2[2] - (vrai[3] - 2.0 + f / 2.0)) <= f, str(a2))
    vol[zs[2], :, :] = 255

    # ⭐⭐⭐⭐ LE JUGE D'UN SAUT : la h-ième couche, et un témoin qui avance de h pas.
    t_soi = np.array([150.0, 150.0, 150.0, np.nan])
    tau = np.array([152.0, 230.0, 80.0, 150.0])
    j = juger_le_saut(tau, t_soi, 1.0, 2)
    v("★★★★ au deuxième saut, un point sans couche n'est pas noté", j["les_points_notes"] == 3)
    v("★★★★ le point à la deuxième couche est bon, les deux autres ratés",
      j["le_transfert"]["la_part_sur_la_bonne_spire"] == round(1 / 3, 4))
    v("★★★ l'un est trop loin, l'autre trop près",
      j["le_transfert"]["la_part_trop_loin"] == round(1 / 3, 4) and j["le_transfert"]["la_part_trop_pres"] == round(1 / 3, 4))
    v("★★★★ le témoin avance de deux pas, et 144 est à moins d'un demi-feuillet de 150",
      j["le_temoin_sans_lecture"]["la_part_sur_la_bonne_spire"] == 1.0)
    jm = juger_le_saut(-tau, -t_soi, -1.0, 2)
    v("★★ de l'autre côté, trop loin reste trop loin", jm["le_transfert"]["la_part_trop_loin"] == round(1 / 3, 4))

    # ⭐⭐⭐ QUI TIENT : un point qui rate le deuxième saut ne tient pas les quatre, même s'il retombe juste.
    bons = [np.array([1, 1, 1, 0], bool), np.array([1, 0, 1, 1], bool), np.array([1, 1, 1, 1], bool),
            np.array([1, 1, 0, 1], bool)]
    notes = [np.array([1, 1, 1, 1], bool)] * 3 + [np.array([1, 1, 1, 0], bool)]
    q = la_part_qui_tient(bons, notes)
    v("★★★★ tenir tous les sauts, c'est tenir chacun d'affilée", q["la_part_qui_tient_tous_les_sauts"] == round(1 / 3, 4)
      and q["les_points_notes_a_chaque_saut"] == 3, str(q))
    v("★★★ pas à pas, seuls ceux qui ont tenu le saut précédent comptent",
      q["parmi_ceux_qui_ont_tenu_le_saut_precedent"] == [0.75, round(2 / 3, 4), 1.0, 0.5], str(q))

    # ⚠⚠ LES RATÉS : un point resté sur la couche d'avant, un point là où la bande saute deux pas, un point
    # parti sur la couche d'après ; chacun est compté dans sa case.
    ver = [np.array([72.0, 72.0, 72.0, 72.0]), np.array([144.0, 216.0, 144.0, 144.0]), np.array([216.0, 288.0, 216.0, 216.0])]
    tau2 = np.array([73.0, 150.0, 216.0, 145.0])
    rt = les_rates(tau2, ver, 2, 1.0)
    v("★★★★ trop près au deuxième saut : deux points, l'un sur la couche d'avant, l'autre là où la bande saute",
      rt["trop_pres"] == 2 and rt["trop_pres_dont_sur_la_couche_davant"] == 0.5
      and rt["trop_pres_dont_la_ou_la_bande_saute_plus_dun_pas_et_demi"] == 0.5, str(rt))
    v("★★★ trop loin : sur la couche d'après", rt["trop_loin"] == 1 and rt["trop_loin_dont_sur_la_couche_dapres"] == 1.0,
      str(rt))
    v("★★★ au premier saut, la couche d'avant est le segment lui-même",
      les_rates(np.array([2.0]), [np.array([72.0])], 1, 1.0).get("trop_pres_dont_sur_la_couche_davant") == 1.0)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} ({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--maille", type=int, default=LA_MAILLE)
    p.add_argument("--delai", type=float, default=DELAI)
    p.add_argument("--segment", default=LA_BANDE)
    p.add_argument("--rangees", type=float, nargs=2, default=None, metavar=("DEBUT", "FIN"),
                   help="une tranche des rangées, en fractions ; par défaut celle de 247 pour la bande")
    p.add_argument("--sauts", type=int, default=LES_SAUTS)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    rangees = tuple(a.rangees) if a.rangees else (LA_TRANCHE if a.segment == LA_BANDE else None)
    r = mesurer(LE_CACHE, a.maille, a.delai, a.segment, rangees, a.sauts)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
