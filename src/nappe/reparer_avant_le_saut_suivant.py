"""Réparer les points signalés avant le saut suivant fait-il tenir la chaîne ?

⭐⭐⭐⭐ CE QUI REMPLACE L'HUMAIN, TENTÉ. `250` et `251` ont donné deux contrôles sans juge, le retour et le désaccord de
deux prédictions ; réunis, ils signalent deux ratés sur cinq. `251` les écartait. Une chaîne ne peut pas écarter un point
par spire : elle doit le réparer avant le saut suivant, sinon le raté se propage à tous les sauts qui suivent (`248`).

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE. À chaque saut, depuis la surface produite par le précédent :
  1. le saut de `248` avec `m7` (la feuille suivante, puis le vote), et le même avec `ps256` ;
  2. le retour de `250` avec `m7`, depuis la surface que ce saut produit ;
  3. un point est SIGNALÉ si son retour tombe à un demi-feuillet ou plus d'où il partait, ou si les deux prédictions sont
     en désaccord d'un demi-feuillet ou plus (`251`) ;
  4. un point signalé est RÉPARÉ : il vise la médiane des pas de ses voisins sains dans son carré de 3 × 3, s'il en a
     trois au moins, et prend la feuille de `m7` la plus proche de cette cible à moins d'un demi-feuillet, sinon la cible
     elle-même. Trois, c'est un côté entier du carré : le moins qui laisse une réparation avancer le long d'un bord droit,
     là où la majorité de cinq de `228` s'arrête aux coins. Un point réparé compte comme sain au tour suivant, et la
     réparation est répétée jusqu'à ce que plus rien ne change, au plus trente tours (ceux du vote de `247`) : une tache
     signalée se comble ainsi depuis son bord. Sans voisins sains, un point garde son pas.
La même chaîne sans réparation est refaite dans la même exécution : c'est celle de `248`, et c'est vérifié. Les deux sont
jugées par le juge de `248` et par le juge sans falaise de `253`.

⚠⚠ CE QUE LA RÉPARATION NE PEUT PAS FAIRE : un raté que ni le retour ni le désaccord ne signale n'est pas réparé, et il
peut même servir de voisin sain à un point signalé, qui est alors réparé vers le raté.

Usage :
    uv run python src/nappe/reparer_avant_le_saut_suivant.py --verifier
    uv run python src/nappe/reparer_avant_le_saut_suivant.py --json docs/mesures/reparer_avant_le_saut_suivant.json
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
from la_chaine_rejugee_hors_des_dechirures import la_courbe_et_la_tenue  # noqa: E402
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, PAS_EN_VOXELS,  # noqa: E402
                                                les_normales, lire_tifxyz, telecharger)
from la_surface_produite_se_dechire_t_elle import la_falaise  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS, enchainer,  # noqa: E402
                                                       les_couches_ordonnees, les_normales_de_la_grille,
                                                       lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LA_PORTEE, LES_PREDICTIONS,  # noqa: E402
                                                         la_feuille_suivante, le_consensus, le_facteur, le_vote_itere,
                                                         lecteur_du_depot, les_centres)


def un_saut(q, nq, cote, lire_rayon, sur_la_grille, gi, gj) -> tuple[np.ndarray, list[np.ndarray]]:
    """Le saut de `248` depuis `q` le long de `nq` : son pas, et les centres des feuilles vues le long de chaque rayon."""
    t, vu = lire_rayon(q, nq, cote, LA_PORTEE)
    suivante = la_feuille_suivante(t, vu)
    depart = np.where(np.isfinite(suivante), suivante, cote * PAS_EN_VOXELS)
    centres = les_centres(t, vu)
    pas, _ = le_vote_itere(centres, depart, sur_la_grille, gi, gj)
    return pas, centres


def la_normale_de(q, parent, sur_la_grille, gi, gj) -> np.ndarray:
    grille_q = np.stack([sur_la_grille(q[:, a]) for a in range(3)], axis=-1)
    grille_n = np.stack([sur_la_grille(parent[:, a]) for a in range(3)], axis=-1)
    ng, _ = les_normales_de_la_grille(grille_q, grille_n)
    return ng[gi, gj]


LES_TOURS_DE_REPARATION = 30
LES_VOISINS_SAINS = 3


def la_mediane_des_voisins_sains(carte: np.ndarray, minimum: int = LES_VOISINS_SAINS) -> np.ndarray:
    """La médiane des valeurs présentes du carré de 3 × 3 autour de chaque maille, le point lui-même exclu, s'il y en a
    au moins `minimum` ; sinon NaN."""
    h, w = carte.shape
    bord = np.pad(carte, 1, constant_values=np.nan)
    pile = np.stack([bord[i:i + h, j:j + w] for i in range(3) for j in range(3) if (i, j) != (1, 1)])
    combien = np.isfinite(pile).sum(axis=0)
    with np.errstate(all="ignore"):
        med = np.nanmedian(np.where(combien[None] > 0, pile, 0.0), axis=0)
    return np.where(combien >= minimum, med, np.nan)


def reparer(pas: np.ndarray, signale: np.ndarray, centres: list[np.ndarray], sur_la_grille, gi, gj,
            tours: int = LES_TOURS_DE_REPARATION) -> tuple[np.ndarray, np.ndarray]:
    """Les pas réparés : chaque point signalé vise la médiane de ses voisins sains (trois au moins) et prend la feuille la
    plus proche à moins d'un demi-feuillet, sinon la cible ; un point réparé devient sain au tour suivant. Rend aussi les
    points réparés."""
    neuf = pas.copy()
    malade = signale.copy()
    repare = np.zeros_like(signale)
    for _ in range(tours):
        cible = la_mediane_des_voisins_sains(sur_la_grille(np.where(malade, np.nan, neuf)))[gi, gj]
        ce_tour = malade & np.isfinite(cible)
        if not ce_tour.any():
            break
        for k in np.flatnonzero(ce_tour):
            c = centres[k]
            neuf[k] = cible[k]
            if len(c):
                d = np.abs(c - cible[k])
                m = int(np.argmin(d))
                if d[m] < DEMI_PAS_EN_VOXELS:
                    neuf[k] = c[m]
        malade &= ~ce_tour
        repare |= ce_tour
    return neuf, repare


def les_signales(coherent: np.ndarray, pas: np.ndarray, pas_ps: np.ndarray) -> np.ndarray:
    """Un point est signalé si son retour n'est pas cohérent, ou si les deux prédictions sont en désaccord."""
    return ~coherent | le_desaccord(pas, pas_ps)


def enchainer_en_reparant(p, n, cote, sauts, lire_m7, lire_ps, sur_la_grille, gi, gj, reparer_les_signales: bool = True):
    """La chaîne de `248` avec `m7`, et, si demandé, la réparation des points signalés avant chaque saut suivant."""
    q, nq = p.copy(), n.copy()
    out = []
    for _ in range(sauts):
        pas, centres = un_saut(q, nq, cote, lire_m7, sur_la_grille, gi, gj)
        avant = pas.copy()
        signale = np.zeros(len(q), dtype=bool)
        repare = np.zeros(len(q), dtype=bool)
        if reparer_les_signales:
            pas_ps, _ = un_saut(q, nq, cote, lire_ps, sur_la_grille, gi, gj)
            q1 = q + pas[:, None] * nq
            n1 = la_normale_de(q1, nq, sur_la_grille, gi, gj)
            retour, _ = un_saut(q1, n1, -cote, lire_m7, sur_la_grille, gi, gj)
            r = q1 + retour[:, None] * n1
            coherent = np.abs(np.einsum("ij,ij->i", r - q, nq)) < DEMI_PAS_EN_VOXELS
            signale = les_signales(coherent, pas, pas_ps)
            pas, repare = reparer(pas, signale, centres, sur_la_grille, gi, gj)
        q = q + pas[:, None] * nq
        nq = la_normale_de(q, nq, sur_la_grille, gi, gj)
        out.append({"q": q.copy(), "le_pas": pas, "le_pas_avant_reparation": avant, "signale": signale, "repare": repare})
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
    couches = les_couches_ordonnees(ref, valide, esp, maille, sauts)["les_cartes"]
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

    lecteurs, stats = {}, {}
    for nom_p, (chemin, niveau) in LES_PREDICTIONS.items():
        facteur, pred = le_facteur(chemin, niveau, delai)
        lire, st = lecteur_du_depot(pred, cache, nom_p, chemin, niveau, delai)
        lecteurs[nom_p] = (lambda f_, p_, l_: lambda q, nq, cote, portee: lire_le_rayon(q, nq, cote, portee, f_, p_, l_))(
            facteur, pred, lire)
        stats[nom_p] = st
    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None, "la_maille": maille,
           "les_points": int(len(p)), "les_sauts": sauts}
    for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
        verites = [couches[cote_][gi, gj, k] for k in range(sauts)]
        notes = [np.isfinite(v) for v in verites]
        sans_falaise = [np.isfinite(v) & ~la_falaise(sur_la_grille(v))[gi, gj] for v in verites]
        brute = enchainer_en_reparant(p, n, cote, sauts, lecteurs["m7"], lecteurs["ps256"], sur_la_grille, gi, gj, False)
        reparee = enchainer_en_reparant(p, n, cote, sauts, lecteurs["m7"], lecteurs["ps256"], sur_la_grille, gi, gj, True)
        ref248 = enchainer(p, n, cote, sauts, lecteurs["m7"], sur_la_grille, gi, gj, True)
        ecart = max(float(np.nanmax(np.abs(a["q"] - b["q"]))) for a, b in zip(brute, ref248))
        # ⚠⚠ CE QUE LA RÉPARATION A FAIT AU PREMIER SAUT, ajouté après la mesure pour comprendre son effet : parmi les points
        # réparés, ceux qu'elle a rendus justes, ceux qu'elle a rendus faux, et ceux qu'elle a laissés comme ils étaient.
        s1 = reparee[0]
        with np.errstate(invalid="ignore"):
            juste_avant = np.abs(s1["le_pas_avant_reparation"] - verites[0]) < DEMI_PAS_EN_VOXELS
            juste_apres = np.abs(s1["le_pas"] - verites[0]) < DEMI_PAS_EN_VOXELS
        m = s1["repare"] & notes[0]
        ce_qu_elle_a_fait = {"les_points_repares_notes": int(m.sum())}
        if m.any():
            ce_qu_elle_a_fait.update({
                "rate_devenu_juste": round(float((~juste_avant & juste_apres)[m].mean()), 4),
                "juste_devenu_rate": round(float((juste_avant & ~juste_apres)[m].mean()), 4),
                "reste_juste": round(float((juste_avant & juste_apres)[m].mean()), 4),
                "reste_rate": round(float((~juste_avant & ~juste_apres)[m].mean()), 4)})
        r = {"la_chaine_sans_reparation_contre_248_ecart_max_voxels": round(ecart, 4),
             "ce_que_la_reparation_a_fait_au_premier_saut": ce_qu_elle_a_fait,
             "la_part_signalee_par_saut": [round(float(s["signale"].mean()), 4) for s in reparee],
             "la_part_reparee_par_saut": [round(float(s["repare"].mean()), 4) for s in reparee]}
        for nom_c, ch in (("sans_reparation", brute), ("en_reparant", reparee)):
            taus = [np.einsum("ij,ij->i", s["q"] - p, n) for s in ch]
            r[nom_c] = {"le_juge_de_248": la_courbe_et_la_tenue(taus, verites, notes, cote),
                        "le_juge_sans_falaise": la_courbe_et_la_tenue(taus, verites, sans_falaise, cote)}
        out[nom] = r
    out["la_lecture"] = {k: {"chunks_lus": s["lus"], "combien_de_pannes": len(s["pannes"])} for k, s in stats.items()}
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = all(not s["pannes"] for s in stats.values())
    return out


def afficher(r: dict) -> None:
    if "les_points" not in r:
        print(f"indécidable : {r.get('la_raison')}")
        return
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points, {r['les_sauts']} sauts, {r['les_secondes']} s")
    for nom in ("du_cote_plus", "du_cote_moins"):
        x = r[nom]
        print(f"— {nom} : sans réparation contre 248 {x['la_chaine_sans_reparation_contre_248_ecart_max_voxels']}, signalés "
              f"{x['la_part_signalee_par_saut']}, réparés {x['la_part_reparee_par_saut']}")
        print(f"    au premier saut : {x['ce_que_la_reparation_a_fait_au_premier_saut']}")
        for nom_c in ("sans_reparation", "en_reparant"):
            for juge in ("le_juge_de_248", "le_juge_sans_falaise"):
                j = x[nom_c][juge]
                sf = j["sur_les_points_notes_a_chaque_saut"]
                q = j["qui_tient"]["la_chaine"]
                print(f"    {nom_c:16s} {juge:20s} sur {sf['les_points']} : {sf['la_chaine']}  tient tout "
                      f"{q['la_part_qui_tient_tous_les_sauts']}  pas à pas {q['parmi_ceux_qui_ont_tenu_le_saut_precedent']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ LA RÉPARATION, sur un carré de 9 × 9 : un point signalé vise la médiane de ses voisins non signalés et prend
    # la feuille la plus proche ; sans majorité de voisins sains, il garde son pas.
    H, W = 9, 9
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    pas = np.full(H * W, 72.0)
    k0 = 4 * W + 4
    pas[k0] = 150.0
    signale = np.zeros(H * W, bool)
    signale[k0] = True
    centres = [np.array([75.0, 150.0]) for _ in range(H * W)]
    neuf, rep = reparer(pas, signale, centres, grille_, gi_, gj_)
    v("★★★★ un point signalé prend la feuille la plus proche de ses voisins", neuf[k0] == 75.0 and rep[k0], str(neuf[k0]))
    v("★★★ les points non signalés ne bougent pas", np.array_equal(np.delete(neuf, k0), np.delete(pas, k0)))
    sans = [np.array([150.0]) for _ in range(H * W)]
    neuf2, _ = reparer(pas, signale, sans, grille_, gi_, gj_)
    v("★★★ sans feuille près de la cible, il prend la cible elle-même", neuf2[k0] == 72.0, str(neuf2[k0]))
    tache = np.zeros(H * W, bool)
    tache[(gi_ >= 2) & (gi_ <= 6) & (gj_ >= 2) & (gj_ <= 6)] = True
    neuf3, rep3 = reparer(np.where(tache, 150.0, 72.0), tache, centres, grille_, gi_, gj_)
    v("★★★★ une tache signalée de cinq sur cinq se comble depuis son bord, jusqu'à son cœur",
      rep3[tache].all() and np.all(neuf3[tache] == 75.0), str(int(rep3.sum())))
    un_tour, rep1 = reparer(np.where(tache, 150.0, 72.0), tache, centres, grille_, gi_, gj_, tours=1)
    v("★★★ en un seul tour, seul son bord est réparé", rep1.sum() == 16 and not rep1[k0], str(int(rep1.sum())))
    deux = la_mediane_des_voisins_sains(np.array([[np.nan, 1.0, np.nan], [np.nan, 9.0, np.nan], [np.nan, 2.0, np.nan]]))
    trois = la_mediane_des_voisins_sains(np.array([[np.nan, 1.0, np.nan], [4.0, 9.0, np.nan], [np.nan, 2.0, np.nan]]))
    v("★★★ la médiane des voisins sains exclut le point lui-même et en exige trois",
      np.isnan(deux[1, 1]) and trois[1, 1] == 2.0, f"{deux[1, 1]} {trois[1, 1]}")
    tout, rep_t = reparer(pas, np.ones(H * W, bool), centres, grille_, gi_, gj_)
    v("★★★ sans aucun voisin sain, rien n'est réparé", not rep_t.any() and np.array_equal(tout, pas))

    # ⭐⭐⭐ LE SIGNALEMENT : un retour incohérent, ou un désaccord, suffit ; un point cohérent et d'accord n'est pas signalé.
    sg = les_signales(np.array([True, False, True, False]), np.array([72.0, 72.0, 72.0, 72.0]),
                      np.array([72.0, 72.0, 150.0, 150.0]))
    v("★★★★ le retour ou le désaccord, chacun suffit", sg.tolist() == [False, True, True, True], str(sg))

    # ⭐⭐⭐⭐ LA CHAÎNE EN RÉPARANT, sur deux prédictions fabriquées : `m7` manque la deuxième feuille sur une plaque de cinq
    # sur cinq, `ps256` la voit partout. ⚠ Une plaque de trois sur trois, le vote de `247` la comble déjà seul : la cible de
    # ses voisins n'a pas de feuille à moins d'un demi-feuillet, et il la prend. Cinq sur cinq, il ne comble que les coins,
    # et le cœur saute une spire ; en réparant, le désaccord la signale et elle se comble depuis son bord.
    f = 4
    meta = {"shape": [128, 32, 32], "chunks": [16, 16, 16], "fill_value": 0}
    zs = [10, 30, 50, 70]
    vol_ps = np.zeros(meta["shape"], np.uint8)
    for z in zs:
        vol_ps[z, :, :] = 255
    vol_m7 = vol_ps.copy()
    pts = np.stack([gj_ * 8.0 + 10.0, gi_ * 8.0 + 10.0, np.full(H * W, zs[0] * f + 2.0)], axis=-1)
    plaque = (gi_ >= 2) & (gi_ <= 6) & (gj_ >= 2) & (gj_ <= 6)
    coeur = (gi_ == 4) & (gj_ == 4)
    for k in np.flatnonzero(plaque):
        x_, y_ = pts[k, 0], pts[k, 1]
        vol_m7[zs[2], int(y_ // f), int(x_ // f)] = 0

    def lecteur(vol):
        def lire(c_):
            a0 = np.asarray(c_) * 16
            return vol[a0[0]:a0[0] + 16, a0[1]:a0[1] + 16, a0[2]:a0[2] + 16]
        return lambda q, nq, cote, portee: lire_le_rayon(q, nq, cote, portee, f, meta, lire)

    nor = np.tile([0.0, 0.0, 1.0], (H * W, 1))
    brute = enchainer_en_reparant(pts, nor, 1.0, 2, lecteur(vol_m7), lecteur(vol_ps), grille_, gi_, gj_, False)
    rep_c = enchainer_en_reparant(pts, nor, 1.0, 2, lecteur(vol_m7), lecteur(vol_ps), grille_, gi_, gj_, True)
    vrai2 = (zs[2] - zs[0]) * f
    d_brute = brute[1]["q"][coeur, 2] - pts[coeur, 2]
    d_rep = rep_c[1]["q"][plaque, 2] - pts[plaque, 2]
    v("★★★★ sans réparation, le cœur de la plaque saute une spire au deuxième saut", np.all(d_brute > vrai2 + DEMI_PAS_EN_VOXELS),
      str(d_brute))
    v("★★★★ en réparant, toute la plaque retombe sur la bonne spire", np.all(np.abs(d_rep - vrai2) < DEMI_PAS_EN_VOXELS),
      str(np.round(d_rep, 1)))
    # ⚠ ICI LE RETOUR SIGNALE AUSSI LA PLAQUE : au bord de la falaise qu'elle fait, les normales penchent, les rayons du
    # retour manquent la feuille, et le vote répand le pas par défaut jusqu'au cœur. Le signalement ne dépend donc pas du
    # seul désaccord ; c'est le contrôle du signalement, plus haut, qui l'exige.
    v("★★★ et son cœur est signalé", rep_c[1]["signale"][coeur].all())
    v("★★★ au premier saut, où les deux prédictions voient tout, rien n'est signalé", not rep_c[0]["signale"].any())
    # ⚠ AUTOUR DE LA PLAQUE, LE RETOUR SIGNALE À TORT : la surface d'où il part a une falaise au bord de la plaque, donc
    # la normale y penche et le retour tombe ailleurs. Ces points sont réparés vers leurs voisins, et restent justes.
    d_tout = rep_c[1]["q"][:, 2] - pts[:, 2]
    v("★★★ les points signalés à tort autour de la plaque restent sur la bonne spire",
      rep_c[1]["signale"][~plaque].any() and np.all(np.abs(d_tout - vrai2) < DEMI_PAS_EN_VOXELS), str(np.round(d_tout, 1)))

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
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(LE_CACHE, LA_MAILLE, a.delai)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
