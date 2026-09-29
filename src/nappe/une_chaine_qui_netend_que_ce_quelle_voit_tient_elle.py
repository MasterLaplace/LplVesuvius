"""Une chaîne de m7 qui ne pose que ce que m7 voit, et fait croître chaque saut depuis toutes les régions où m7 voit la feuille suivante, tient-elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UN SEUL SAUT À PLUSIEURS DÉPARTS NE SOIT TIRÉ. Ce qui était vu avant d'écrire : tout ce que `303` à
`317` publient, dont `R4-F498` (les points que le vote pose sans `m7` ne sont au cœur d'aucune feuille) et `R4-F487` (la chaîne
croissante de `306`, partie d'un seul point par saut, ne couvre que 0,1 à 19 % du plan et sort du cœur dès le premier saut sur ses
quatre côtés).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P115`. La chaîne du vote tient loin par des morceaux appuyés sur `m7` reliés par un
vote qui ne suit pas l'empilement ; la chaîne croissante de `306` ne pose que ce que `m7` voit, mais depuis un seul départ, qu'un
trou de `m7` suffit à isoler. Entre les deux : ne poser que ce que `m7` voit, mais faire croître chaque saut depuis chaque région où
`m7` voit une feuille après la sienne.

## Ce qui est fait

- **Les départs** : les nappes du vote de `301` qui suivent l'empilement (graines 3, 4, 6, 7 et 8), retirées de `m7` à l'identique et
  réduites à leurs points appuyés sur `m7`.
- **Le saut à plusieurs départs** : le long de la normale de chaque point posé, les plages de `m7` sur trois pas ; tant qu'il reste un
  point non posé qui voit une plage après la sienne, le plus proche du centre de la grille part de cette plage-là, et la croissance de
  `305` (5 voxels de la médiane des voisins posés) pose sa région, sans entrer dans les régions déjà posées ; une région de moins de
  20 points n'est pas gardée.
- **La chaîne** : douze sauts de chaque côté, chacun parti de ce que le précédent a posé.
- **La lecture, à chaque saut** : la part posée des points du saut précédent, le nombre de régions, le pas médian, la cohérence (la part
  des points posés dont le pas est à 5 voxels du pas médian), et le plus dense du profil moyen du scan.

## Les issues

Un saut **tient** s'il pose au moins la moitié des points du saut précédent, avec une cohérence d'au moins 90 %, et que son plus dense
est à au plus 5 voxels ; par côté, le dernier saut h tel que les sauts 1 à h tiennent. **L'issue** : la chaîne qui n'étend que ce
qu'elle voit tient jusqu'au saut H sur au moins la moitié des dix côtés.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : que les régions d'un même saut soient sur la même spire, au-delà de leur pas commun ; ni que les
spires soient consécutives.

Usage :
    uv run python src/nappe/une_chaine_qui_netend_que_ce_quelle_voit_tient_elle.py --verifier
    uv run python src/nappe/une_chaine_qui_netend_que_ce_quelle_voit_tient_elle.py --preparer
    uv run python src/nappe/une_chaine_qui_netend_que_ce_quelle_voit_tient_elle.py --lire 4
    uv run python src/nappe/une_chaine_qui_netend_que_ce_quelle_voit_tient_elle.py \\
        --json docs/mesures/une_chaine_qui_netend_que_ce_quelle_voit_tient_elle.json
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

import la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille as m298  # noqa: E402
import lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille as m299  # noqa: E402
import une_nappe_tiree_de_m7_suit_elle_sa_feuille as m300  # noqa: E402
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402
import la_chaine_tiree_de_m7_suit_elle_sa_feuille_au_dela_du_premier_saut as m303  # noqa: E402
import une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille as m305  # noqa: E402
import le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille as m309  # noqa: E402

LE_DOSSIER = RACINE / "data" / "chaine_qui_voit"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_SAUTS = 12
LA_PLUS_PETITE_REGION = 20
LE_MAXIMUM_DE_REGIONS = 200
LA_COHERENCE = 0.9


def les_regions(centres: list[np.ndarray], suivante: np.ndarray, forme: tuple, tolerance: float = m305.LA_TOLERANCE,
                plus_petite: int = LA_PLUS_PETITE_REGION, maximum: int = LE_MAXIMUM_DE_REGIONS) -> tuple[np.ndarray, np.ndarray, int]:
    """Les régions posées l'une après l'autre : chaque départ est le point non essayé le plus proche du centre qui voit une plage
    après la sienne ; une région n'entre pas dans une région déjà posée. Rend les décalages, le masque posé, le nombre de régions
    gardées."""
    h, w = forme
    dec = np.full(forme, np.nan)
    pose = np.zeros(forme, dtype=bool)
    essaye = ~np.isfinite(suivante.reshape(forme))
    ii, jj = np.mgrid[0:h, 0:w]
    distance = (ii - (h - 1) / 2.0) ** 2 + (jj - (w - 1) / 2.0) ** 2
    gardees = 0
    for _ in range(maximum):
        libre = ~essaye & ~pose
        if not libre.any():
            break
        k = int(np.argmin(np.where(libre, distance, np.inf)))
        i0, j0 = divmod(k, w)
        essaye[i0, j0] = True
        restants = [c if not pose.ravel()[m] else np.empty(0) for m, c in enumerate(centres)]
        d, p = m305.croitre(restants, forme, (i0, j0), tolerance, demi_portee=tolerance,
                            cible_de_depart=float(suivante[k]))
        p &= ~pose
        if p.sum() >= plus_petite:
            dec[p], pose[p] = d[p], True
            gardees += 1
        essaye |= p
    return dec, pose, gardees


def le_saut(surface: np.ndarray, valide: np.ndarray, cote: float, lire_valeurs) -> dict:
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    forme = valide.shape
    nn, nok = les_normales(surface, valide)
    q, nq = surface.reshape(-1, 3), nn.reshape(-1, 3)
    ts = cote * np.arange(0.0, 3.0 * m300.LE_PAS_0358 + 1.0)
    idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
    vu = (lire_valeurs(idx) > 0) & (nok & valide).reshape(-1)[:, None]
    suivante = m300.la_feuille_apres_la_sienne(ts, vu)
    dec, pose, n = les_regions(m300.les_plages(vu, ts), suivante, forme)
    spire = (q + np.nan_to_num(dec.ravel())[:, None] * nq).reshape(forme + (3,))
    return {"la_spire": spire, "valide": pose, "le_pas": dec, "les_regions": n}


def la_coherence(pas_: np.ndarray, pose: np.ndarray, tolerance: float = m305.LA_TOLERANCE) -> tuple[float | None, float | None]:
    a = np.abs(pas_[pose & np.isfinite(pas_)])
    if not len(a):
        return None, None
    m = float(np.median(a))
    return round(m, 2), round(float((np.abs(a - m) <= tolerance).mean()), 4)


def tient(s: dict, quart: int) -> bool:
    return (s["la_part_posee"] is not None and s["la_part_posee"] >= 0.5 and s["la_coherence"] is not None
            and s["la_coherence"] >= LA_COHERENCE and s["le_plus_dense"] is not None and abs(s["le_plus_dense"]) <= quart)


def le_dernier_qui_tient(sauts: list[dict], quart: int) -> int:
    h = 0
    for s in sauts:
        if not tient(s, quart):
            break
        h += 1
    return h


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    derniers = [c["le_dernier_saut_qui_tient"] for c in d["les_cotes"]]
    if not derniers:
        return {"decidable": False, "lissue": "indécidable : aucun côté"}
    n = len(derniers)
    H = max((h for h in range(1, LES_SAUTS + 1) if sum(1 for x in derniers if x >= h) * 2 >= n), default=0)
    return {"decidable": True, "H": H, "les_derniers": derniers,
            "lissue": (f"la chaîne qui n'étend que ce qu'elle voit tient jusqu'au saut {H} sur au moins la moitié des {n} côtés"
                       if H else f"la chaîne qui n'étend que ce qu'elle voit ne tient pas dès le premier saut sur plus de la "
                                 f"moitié des {n} côtés")}


def preparer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta

    t0 = time.monotonic()
    pred = array_meta(f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}", 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    r302, identiques = m302.retirer()
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    tous = set()
    plan = {"les_cotes": [], "les_surfaces": {}}
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    for rang, r in r302["les_nappes"].items():
        for nom, cote in m303.LES_COTES:
            surf, ok = r["la_nappe"], r["valide"] & r["appui"]
            e = {"le_rang": rang, "le_cote": nom, "les_points_de_depart": int(ok.sum()), "les_sauts": []}
            for h in range(1, LES_SAUTS + 1):
                avant = int(ok.sum())
                s = le_saut(surf, ok, cote, lv)
                pose = s["valide"]
                med, coh = la_coherence(s["le_pas"], pose)
                e["les_sauts"].append({"le_saut": h, "les_regions": s["les_regions"], "les_points_poses": int(pose.sum()),
                                       "la_part_posee": round(float(pose.sum() / avant), 4) if avant else None,
                                       "le_pas_median_voxels": med, "la_coherence": coh})
                sn, snok = les_normales(s["la_spire"], pose)
                mm = pose & snok
                pts, nrm = s["la_spire"][mm], sn[mm]
                cle = f"g{rang}_{nom}_{h}"
                f = LES_SURFACES_PREPAREES / f"PHerc0358__{cle}.npz"
                np.savez_compressed(f, points=pts, normales=nrm, groupe=np.zeros(len(pts), dtype=int),
                                    juge=np.full(len(pts), np.nan), groupes=np.array([json.dumps([rang, nom, h])]))
                if len(pts):
                    c = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                    tous |= m298.les_morceaux_complets(c[m298.dans_le_volume(c, vol.forme)], vol.taille)
                plan["les_surfaces"][cle] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
                surf, ok = s["la_spire"], pose
                if not pose.any():
                    break
            plan["les_cotes"].append(e)
            print(json.dumps({"le_rang": rang, "le_cote": nom, "poses": [x["les_points_poses"] for x in e["les_sauts"]],
                              "coh": [x["la_coherence"] for x in e["les_sauts"]]}), flush=True)
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan.update(les_nappes_se_redonnent=identiques, les_pannes=list(stats["pannes"]) + list(r302["les_pannes"]),
                les_morceaux={"combien": len(cles)}, les_secondes=round(time.monotonic() - t0, 1))
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return {k: v_ for k, v_ in plan.items() if k not in ("les_cotes", "les_surfaces")}


def lire(ouvriers: int = 4) -> dict:
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    cles = [tuple(c) for c in json.loads((LE_DOSSIER / "morceaux.json").read_text())]
    comptes = {"deja": 0, "tire": 0, "absent": 0}
    with ThreadPoolExecutor(ouvriers) as ex:
        for r in ex.map(lambda c: vol.tirer(*c), cles):
            comptes[r] += 1
    return dict(comptes, combien=len(cles))


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    quart = m309.le_quart_de_pas("PHerc0358")
    cotes = []
    for c in plan["les_cotes"]:
        e = dict(c, les_sauts=[])
        for s in c["les_sauts"]:
            info = plan["les_surfaces"][f"g{c['le_rang']}_{c['le_cote']}_{s['le_saut']}"]
            r = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
            e["les_sauts"].append(dict(s, le_plus_dense=m309.le_plus_dense(r[0]["le_profil_moyen"]) if r else None,
                                       les_points_juges=r[0]["les_points_juges"] if r else 0))
        e["le_dernier_saut_qui_tient"] = le_dernier_qui_tient(e["les_sauts"], quart)
        cotes.append(e)
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_sauts": LES_SAUTS, "la_plus_petite_region": LA_PLUS_PETITE_REGION,
                            "la_coherence_minimale": LA_COHERENCE, "la_tolerance_voxels": m305.LA_TOLERANCE,
                            "le_quart_de_pas_voxels": quart},
         "les_nappes_se_redonnent": plan["les_nappes_se_redonnent"], "les_pannes": plan["les_pannes"],
         "les_cotes": cotes, "les_morceaux": plan["les_morceaux"]}
    d["le_verdict"] = le_verdict(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


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

    h, w = 12, 12
    # Deux îlots où m7 voit la feuille suivante à 20 voxels, séparés par une colonne où il ne voit rien.
    centres, suivante = [], np.full(h * w, np.nan)
    for k in range(h * w):
        j = k % w
        if j == 6:
            centres.append(np.empty(0))
        else:
            centres.append(np.array([0.0, 20.0]))
            suivante[k] = 20.0
    dec, pose, n = les_regions(centres, suivante, (h, w), plus_petite=5)
    v("★★★★ deux régions séparées par un trou de m7 sont posées toutes deux, depuis deux départs",
      n == 2 and pose[:, :6].all() and pose[:, 7:].all() and not pose[:, 6].any() and np.allclose(dec[pose], 20.0), str(n))
    dec1, pose1, n1 = les_regions(centres, suivante, (h, w), plus_petite=5, maximum=1)
    v("★★★ avec un seul départ, une seule région : ce que faisait 306", n1 == 1 and pose1.sum() < pose.sum())
    petit = [np.array([0.0, 20.0]) if k in (0, 1) else np.empty(0) for k in range(h * w)]
    sv = np.full(h * w, np.nan)
    sv[[0, 1]] = 20.0
    v("★★★ une région trop petite n'est pas gardée", les_regions(petit, sv, (h, w), plus_petite=5)[2] == 0)
    deux = [np.array([0.0, 20.0]) if (k % w) < 6 else np.array([0.0, 32.0]) for k in range(h * w)]
    sv2 = np.array([20.0 if (k % w) < 6 else 32.0 for k in range(h * w)])
    d2, p2, n2 = les_regions(deux, sv2, (h, w), plus_petite=5)
    v("★★★★ une région ne passe pas dans une autre : la frontière entre 20 et 32 voxels reste une frontière",
      n2 == 2 and np.allclose(d2[:, :6], 20.0) and np.allclose(d2[:, 6:], 32.0), str(n2))
    zc, zs = [], np.full(h * w, np.nan)
    for k in range(h * w):
        j = k % w
        if j < 4:
            zc.append(np.array([0.0, 32.0]))
            zs[k] = 32.0
        elif j < 8:
            zc.append(np.array([0.0, 20.0, 32.0]))
            zs[k] = 20.0
        else:
            zc.append(np.array([0.0, 32.0]))
    d3, p3, n3 = les_regions(zc, zs, (h, w), plus_petite=5)
    v("★★★★ une région ne traverse pas une région déjà posée pour atteindre ce qui est derrière",
      n3 == 2 and np.allclose(d3[:, 4:8], 20.0) and np.allclose(d3[:, :4], 32.0) and not p3[:, 8:].any(), str(n3))
    trois = np.where(np.arange(w)[None, :].repeat(h, 0) < 9, 20.0, 32.0)
    v("★★★★ la cohérence : la part des points à 5 voxels du pas médian",
      la_coherence(d2, p2) == (26.0, 0.0) and la_coherence(trois, np.ones((h, w), dtype=bool)) == (20.0, 0.75),
      f"{la_coherence(d2, p2)} {la_coherence(trois, np.ones((h, w), dtype=bool))}")
    bon = {"la_part_posee": 0.8, "la_coherence": 0.95, "le_plus_dense": -1}
    v("★★★★ un saut tient : assez posé, cohérent, au cœur", tient(bon, 5))
    v("★★★ trop peu posé, il ne tient pas", not tient(dict(bon, la_part_posee=0.4), 5))
    v("★★★ incohérent, il ne tient pas", not tient(dict(bon, la_coherence=0.8), 5))
    v("★★★ hors du cœur, il ne tient pas", not tient(dict(bon, le_plus_dense=9), 5))
    v("★★★ le dernier qui tient s'arrête au premier qui lâche",
      le_dernier_qui_tient([bon, dict(bon, la_coherence=0.1), bon], 5) == 1)
    vd = le_verdict({"les_cotes": [{"le_dernier_saut_qui_tient": x} for x in (12, 5, 0, 7)]})
    v("★★★ l'issue : le plus grand saut tenu sur au moins la moitié des côtés", vd["H"] == 7, str(vd))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.preparer:
        print(json.dumps(preparer(), ensure_ascii=False, indent=1))
        return 0
    if a.lire is not None:
        print(json.dumps(lire(a.lire), ensure_ascii=False, indent=1))
        return 0
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
