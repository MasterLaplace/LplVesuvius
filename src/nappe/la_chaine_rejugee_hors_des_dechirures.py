"""Que perd la chaîne à chaque saut, jugée là où le juge ne se déchire pas ?

⭐⭐⭐⭐ LA SUITE DE `252`. `248` a mesuré que la chaîne perd de 0,09 à 0,14 des points qui avaient tenu le saut précédent,
et `252` que là où la bande saute, c'est la couche de la bande qui se déchire : elle saute d'un tour entre deux mailles
voisines, ce qu'une feuille ne fait pas. Une part de ce que `248` compte comme perdu est donc un défaut du juge. Cette
mesure refait la chaîne de `248` et la juge là seulement où la couche du juge est continue.

⚠⚠⚠ CE QUI EST DÉCLARÉ AVANT LA MESURE. La chaîne est celle de `248` (la feuille suivante, puis le vote, chaque saut parti
de la surface produite le long de sa normale), avec `m7` et `ps256`, sur quatre sauts. Au saut h, un point n'est noté que
si la h-ième couche de la bande existe en face de lui, qu'elle n'est bordée d'aucune falaise et qu'elle tient à la plus
grande pièce de la couche, avec les règles de `252` : une falaise est une voisine, en haut, en bas, à gauche ou à droite,
à un demi-feuillet ou plus. Tout le reste est le jugement de `248`,
refait dans la même exécution pour que les deux se comparent sur les mêmes sauts.

⚠⚠ CE QUE LE JUGE INTACT NE PEUT PAS VOIR : une couche qui glisse d'une spire à l'autre par des pentes douces reste
continue, et elle n'est pas écartée ; et un point juste dont le juge se déchire est écarté comme un raté.

Usage :
    uv run python src/nappe/la_chaine_rejugee_hors_des_dechirures.py --verifier
    uv run python src/nappe/la_chaine_rejugee_hors_des_dechirures.py \\
        --json docs/mesures/la_chaine_rejugee_hors_des_dechirures.json
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
from la_surface_produite_se_dechire_t_elle import hors_de_la_plus_grande_piece, la_falaise  # noqa: E402
from le_transfert_enchaine_tient_il_les_spires import (LA_BANDE, LA_TRANCHE, LES_SAUTS, enchainer,  # noqa: E402
                                                       juger_le_saut, la_part_qui_tient, les_couches_ordonnees,
                                                       lire_le_rayon)
from le_transfert_retrouve_t_il_la_spire_voisine import (DELAI, LA_MAILLE, LES_PREDICTIONS,  # noqa: E402
                                                         le_facteur, lecteur_du_depot)


def les_notes_intactes(verite: np.ndarray, sur_la_grille, gi, gj) -> np.ndarray:
    """Les points dont la couche existe, n'est bordée d'aucune falaise, et tient à la plus grande pièce de la couche.

    ⚠⚠ La plus grande pièce, et pas seulement la falaise : une plaque de couche qui a changé d'identité est bordée de
    falaises, mais son intérieur ne l'est pas ; elle forme une pièce à part, et c'est cette pièce qui est écartée."""
    carte = sur_la_grille(verite)
    hors, _ = hors_de_la_plus_grande_piece(carte)
    return np.isfinite(verite) & ~la_falaise(carte)[gi, gj] & ~hors[gi, gj]


def la_courbe_et_la_tenue(taus: list[np.ndarray], verites: list[np.ndarray], notes: list[np.ndarray], cote: float) -> dict:
    """Saut par saut, la part juste de la chaîne et celle du pas fixe, sur les points notés à ce saut et sur les points
    notés à chaque saut, et la tenue d'affilée."""
    bons, temoin = [], []
    for h, (tau, v) in enumerate(zip(taus, verites), start=1):
        with np.errstate(invalid="ignore"):
            bons.append(np.abs(tau - v) < DEMI_PAS_EN_VOXELS)
            temoin.append(np.abs(cote * h * PAS_EN_VOXELS - v) < DEMI_PAS_EN_VOXELS)
    fixe = np.logical_and.reduce(notes)
    par_saut = []
    for h, (tau, v, nt) in enumerate(zip(taus, verites, notes), start=1):
        j = juger_le_saut(tau, np.where(nt, v, np.nan), cote, h)
        par_saut.append({"les_points_notes": j["les_points_notes"], "la_chaine": j.get("le_transfert"),
                         "le_temoin_sans_lecture": j.get("le_temoin_sans_lecture")})
    return {"par_saut": par_saut,
            "sur_les_points_notes_a_chaque_saut": {
                "les_points": int(fixe.sum()),
                "la_chaine": [round(float(b[fixe].mean()), 4) for b in bons] if fixe.any() else None,
                "le_temoin_sans_lecture": [round(float(b[fixe].mean()), 4) for b in temoin] if fixe.any() else None},
            "qui_tient": {"la_chaine": la_part_qui_tient(bons, notes), "le_temoin_sans_lecture": la_part_qui_tient(temoin, notes)}}


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

    out = {"le_segment": segment, "les_rangees": list(rangees) if rangees else None, "la_maille": maille,
           "les_points": int(len(p)), "les_sauts": sauts, "les_predictions": {}}
    for nom_p, (chemin, niveau) in LES_PREDICTIONS.items():
        facteur, pred = le_facteur(chemin, niveau, delai)
        lire, stats = lecteur_du_depot(pred, cache, nom_p, chemin, niveau, delai)

        def lire_rayon(q, nq, cote, portee):
            return lire_le_rayon(q, nq, cote, portee, facteur, pred, lire)

        r = {}
        for cote_, nom, cote in (("plus", "du_cote_plus", 1.0), ("moins", "du_cote_moins", -1.0)):
            verites = [couches[cote_][gi, gj, k] for k in range(sauts)]
            notes = [np.isfinite(v) for v in verites]
            intactes = [les_notes_intactes(v, sur_la_grille, gi, gj) for v in verites]
            chaine = enchainer(p, n, cote, sauts, lire_rayon, sur_la_grille, gi, gj, True)
            taus = [np.einsum("ij,ij->i", s["q"] - p, n) for s in chaine]
            # ⚠⚠⚠ AJOUTÉ APRÈS LA MESURE, ET DIT COMME TEL : aux sauts 3 et 4, les couches de la bande sont morcelées par
            # des trous, et la règle de la plus grande pièce en écarte presque tout. Le juge sans falaise, la règle de
            # `252` seule, garde l'intérieur des plaques mais écarte leurs bords ; il est noté à côté, jamais à la place.
            sans_falaise = [np.isfinite(v) & ~la_falaise(sur_la_grille(v))[gi, gj] for v in verites]
            r[nom] = {
                "la_part_des_couches_dechirees": [round(float((nt & ~it).sum() / max(nt.sum(), 1)), 4)
                                                  for nt, it in zip(notes, intactes)],
                "la_part_des_couches_bordees_dune_falaise": [round(float((nt & ~sf).sum() / max(nt.sum(), 1)), 4)
                                                             for nt, sf in zip(notes, sans_falaise)],
                "le_juge_de_248": la_courbe_et_la_tenue(taus, verites, notes, cote),
                "le_juge_intact": la_courbe_et_la_tenue(taus, verites, intactes, cote),
                "le_juge_sans_falaise": la_courbe_et_la_tenue(taus, verites, sans_falaise, cote)}
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
    print(f"{r['le_segment']} {r['les_rangees']} : {r['les_points']} points, {r['les_sauts']} sauts, {r['les_secondes']} s")
    for nom_p, rp in r["les_predictions"].items():
        for nom in ("du_cote_plus", "du_cote_moins"):
            x = rp[nom]
            print(f"— {nom_p} {nom} : couches déchirées {x['la_part_des_couches_dechirees']}, bordées "
                  f"{x['la_part_des_couches_bordees_dune_falaise']}")
            for juge in ("le_juge_de_248", "le_juge_intact", "le_juge_sans_falaise"):
                j = x[juge]
                sf = j["sur_les_points_notes_a_chaque_saut"]
                print(f"    {juge:16s} par saut " + "  ".join(
                    f"{s['les_points_notes']}:{(s['la_chaine'] or {}).get('la_part_sur_la_bonne_spire')}" for s in j["par_saut"]))
                print(f"    {'':16s} sur {sf['les_points']} points chaîne {sf['la_chaine']} pas fixe {sf['le_temoin_sans_lecture']}")
                q = j["qui_tient"]["la_chaine"]
                print(f"    {'':16s} tient tout {q['la_part_qui_tient_tous_les_sauts']} pas à pas "
                      f"{q['parmi_ceux_qui_ont_tenu_le_saut_precedent']} ; pas fixe "
                      f"{j['qui_tient']['le_temoin_sans_lecture']['la_part_qui_tient_tous_les_sauts']}")


# ---------------------------------------------------------------------------------------------------
def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # ⭐⭐⭐⭐ UNE COUCHE QUI SE DÉCHIRE : une plaque de trois sur trois saute d'un tour dans la couche du juge, et la
    # chaîne continue à un pas. Le juge de `248` y compte neuf ratés ; le juge intact écarte la plaque, son intérieur
    # compris, et le bord qui la touche.
    H, W = 10, 10
    gi_, gj_ = np.nonzero(np.ones((H, W), bool))

    def grille_(val):
        c = np.full((H, W), np.nan)
        c[gi_, gj_] = val
        return c

    verite = np.full(H * W, 72.0)
    plaque = (gi_ >= 4) & (gi_ <= 6) & (gj_ >= 4) & (gj_ <= 6)
    verite[plaque] = 144.0
    verite[(gi_ == 0) & (gj_ == 0)] = np.nan
    intact = les_notes_intactes(verite, grille_, gi_, gj_)
    v("★★★★ la plaque, son intérieur compris, et le bord qui la touche sont écartés, pas le reste",
      intact.sum() == 100 - 1 - 21 and not intact[plaque].any(), str(int(intact.sum())))
    v("★★★ un point sans couche n'est pas noté", not intact[0])
    tau = np.full(H * W, 72.0)
    j248 = la_courbe_et_la_tenue([tau], [verite], [np.isfinite(verite)], 1.0)
    jint = la_courbe_et_la_tenue([tau], [verite], [intact], 1.0)
    v("★★★★ le juge de 248 compte la plaque comme ratée", j248["par_saut"][0]["la_chaine"]["la_part_sur_la_bonne_spire"]
      == round(90 / 99, 4), str(j248["par_saut"][0]))
    v("★★★★ le juge intact ne la compte pas", jint["par_saut"][0]["la_chaine"]["la_part_sur_la_bonne_spire"] == 1.0
      and jint["par_saut"][0]["les_points_notes"] == 78, str(jint["par_saut"][0]))
    # ⚠⚠⚠ LA TACHE AVEUGLE, DÉCLARÉE : une couche qui glisse d'un tour par des pentes de moins d'un demi-feuillet n'est
    # pas écartée, et la chaîne restée à un pas y est comptée ratée.
    rampe = 72.0 + 8.0 * gj_.astype(float)
    ir = les_notes_intactes(rampe, grille_, gi_, gj_)
    jr = la_courbe_et_la_tenue([tau], [rampe], [ir], 1.0)
    v("★★★★ une rampe douce n'est pas écartée", ir.all())
    v("★★★ et la chaîne restée à un pas y est ratée là où la rampe dépasse un demi-feuillet",
      jr["par_saut"][0]["la_chaine"]["la_part_sur_la_bonne_spire"] == 0.5, str(jr["par_saut"][0]))
    # ⭐⭐⭐ LA COURBE SUR LES POINTS NOTÉS À CHAQUE SAUT, et la tenue d'affilée, par le code de `248`.
    v2 = [np.array([72.0, 72.0, 72.0]), np.array([144.0, 144.0, np.nan])]
    t2 = [np.array([72.0, 72.0, 150.0]), np.array([144.0, 72.0, 144.0])]
    k = la_courbe_et_la_tenue(t2, v2, [np.isfinite(x) for x in v2], 1.0)
    v("★★★★ sur les deux points notés à chaque saut : juste, puis juste et raté", k["sur_les_points_notes_a_chaque_saut"]
      == {"les_points": 2, "la_chaine": [1.0, 0.5], "le_temoin_sans_lecture": [1.0, 1.0]}, str(k["sur_les_points_notes_a_chaque_saut"]))
    v("★★★ la tenue d'affilée est celle de 248", k["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"] == 0.5)

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
