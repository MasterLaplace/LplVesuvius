"""Une nappe de m7 qui croît depuis sa graine en refusant de passer à la feuille voisine suit-elle encore sa feuille ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE NAPPE CROISSANTE NE SOIT TIRÉE. Ce qui était vu avant d'écrire : tout ce que `300` à
`304` publient, dont les nappes du vote de `247` qui passent à la feuille voisine sur un carré de voisins sur dix (`304`).

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P104`. Le vote de `247` fait viser à chaque point la médiane de ses neuf voisins,
partout à la fois, et prend la feuille de `m7` la plus proche à moins d'un demi-pas : là où les feuilles sont serrées à 12 voxels,
un demi-pas de 10 laisse passer à la voisine, et `304` montre que la nappe le fait. Une nappe qui croît depuis sa graine, point par
point, et qui refuse tout point dont la feuille est à plus d'un quart de pas de celle de ses voisins déjà posés, ne peut plus passer
à la voisine en un pas de grille : là où il faudrait sauter, elle laisse un trou.

## Ce qui est fait

- **Les graines** : les huit de `301`, dans leur ordre, avec leur plan (65 × 65 points au pas de 10 voxels) et les feuilles de `m7`
  que chaque point voit sur ±30 voxels, exactement comme `300`.
- **La croissance** : le point le plus proche de la graine prend la feuille de `m7` la plus proche du plan. Puis, en largeur
  d'abord, chaque point voisin (huit voisins) d'un point posé vise la médiane des décalages de ses voisins déjà posés, et prend la
  feuille de `m7` la plus proche de cette cible **à au plus 5 voxels** (un quart de pas) ; s'il n'y en a pas, il attend, et il
  est réévalué chaque fois qu'un voisin de plus est posé. Aucun point n'est posé sans être appuyé sur `m7`, et aucun n'est
  posé deux fois.
- **Le juge** : celui de `301`, sans rien y changer (Z ≥ 3 contre huit rampes), sur les points posés.

## Les issues

Pour chaque graine, la nappe croissante est jugée par la règle de `300` telle quelle : **suit sa feuille** si Z ≥ 3 sur au moins
100 points jugés, **ne la suit pas** si Z < 3, **non jugée** sinon. L'issue de la tranche : **sur k des huit graines, la nappe qui refuse de changer de
feuille suit encore sa feuille**.

## Rapporté à côté, qui ne décide rien

La part du plan posée ; les déchirures et les boucles qui ne ferment pas (les relevés de `302`), là où deux voisins posés depuis
deux côtés se retrouvent ; pour les graines de `301` dont la nappe suivait sa feuille, la part de ses points que la nappe croissante
garde à moins d'un quart de pas.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : qu'une nappe croissante reste sur une seule feuille là où deux feuilles se touchent sans
écart ; ni ce que vaut une croissance d'un point à la fois sur un rouleau entier.

Usage :
    uv run python src/nappe/une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py --verifier
    uv run python src/nappe/une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py --preparer
    uv run python src/nappe/une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py --lire 12
    uv run python src/nappe/une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.py \\
        --json docs/mesures/une_nappe_qui_refuse_de_changer_de_feuille_suit_elle_encore_sa_feuille.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
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
import les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves as m301  # noqa: E402
import les_nappes_de_m7_tiennent_elles_sur_une_seule_feuille as m302  # noqa: E402

LE_DOSSIER = RACINE / "data" / "nappes_croissantes"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
CE_QUE_301_A_PUBLIE = RACINE / "docs" / "mesures" / "les_nappes_de_m7_suivent_elles_leur_feuille_sur_des_graines_neuves.json"
LA_TOLERANCE = 5.0                 # voxels : un quart de pas


# ── La croissance ──────────────────────────────────────────────────────────────────────────────────────────────────

def croitre(centres: list[np.ndarray], forme: tuple, depart: tuple, tolerance: float = LA_TOLERANCE,
            demi_portee: float = m300.LA_DEMI_PORTEE, cible_de_depart: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """La croissance en largeur depuis `depart` : chaque point prend la feuille la plus proche de la médiane de ses voisins
    posés, à au plus `tolerance` ; sinon il est réévalué quand un voisin de plus est posé. Le départ prend la feuille la plus
    proche de `cible_de_depart`, à au plus `demi_portee`. Rend les décalages (NaN hors des points posés) et le masque des points
    posés."""
    h, w = forme
    dec = np.full(forme, np.nan)
    pose = np.zeros(forme, dtype=bool)
    i0, j0 = depart
    c0 = centres[i0 * w + j0]
    if not len(c0):
        return dec, pose
    k = int(np.argmin(np.abs(c0 - cible_de_depart)))
    if abs(c0[k] - cible_de_depart) > demi_portee:
        return dec, pose
    dec[i0, j0], pose[i0, j0] = c0[k], True
    return etendre(centres, forme, dec, pose, tolerance)


def etendre(centres: list[np.ndarray], forme: tuple, dec: np.ndarray, pose: np.ndarray,
            tolerance: float = LA_TOLERANCE, permis: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """La croissance en largeur de `croitre`, depuis tous les points déjà posés à la fois, pris dans l'ordre de la grille ; écrit
    pour `333`, qui la fait partir d'une spire entière. Avec `permis`, écrit pour `335`, elle ne pose que les points permis. Modifie
    et rend `dec` et `pose`."""
    h, w = forme
    file = deque((int(a), int(b)) for a, b in zip(*np.nonzero(pose)))
    voisins = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while file:
        i, j = file.popleft()
        for di, dj in voisins:
            a, b = i + di, j + dj
            if not (0 <= a < h and 0 <= b < w) or pose[a, b] or (permis is not None and not permis[a, b]):
                continue
            poses = [dec[a + x, b + y] for x, y in voisins
                     if 0 <= a + x < h and 0 <= b + y < w and pose[a + x, b + y]]
            cible = float(np.median(poses))
            c = centres[a * w + b]
            if not len(c):
                continue
            m = int(np.argmin(np.abs(c - cible)))
            if abs(c[m] - cible) <= tolerance:
                dec[a, b], pose[a, b] = c[m], True
                file.append((a, b))
    return dec, pose


def la_nappe_croissante(graine_xyz, normale_xyz, lire_valeurs, tolerance: float = LA_TOLERANCE,
                        demi_portee: float | None = None) -> dict:
    """Le plan de `300`, les feuilles de `m7` de chaque point, puis la croissance depuis le point central. `tolerance` et
    `demi_portee`, données par `322` pour le pas de PHercParis4, valent par défaut celles de PHerc0358."""
    grille, n = m300.le_plan(graine_xyz, normale_xyz)
    forme = grille.shape[:2]
    p = grille.reshape(-1, 3)
    t = np.arange(-np.floor(m300.LA_DEMI_PORTEE), np.floor(m300.LA_DEMI_PORTEE) + 1.0)
    idx = np.floor((p[:, None, :] + t[None, :, None] * n[None, None, :])[..., ::-1]).astype(np.int64)
    centres = m300.les_plages(lire_valeurs(idx) > 0, t)
    kw = {"tolerance": tolerance} if demi_portee is None else {"tolerance": tolerance, "demi_portee": demi_portee}
    dec, pose = croitre(centres, forme, (forme[0] // 2, forme[1] // 2), **kw)
    nappe = (p + np.nan_to_num(dec.ravel())[:, None] * n[None, :]).reshape(forme + (3,))
    return {"la_nappe": nappe, "valide": pose, "le_decalage": dec}


def la_part_gardee(dec_croissante: np.ndarray, pose: np.ndarray, dec_vote: np.ndarray, ok_vote: np.ndarray) -> float | None:
    """La part des points de la nappe du vote que la nappe croissante garde à au plus un quart de pas."""
    m = ok_vote & np.isfinite(dec_vote)
    if not m.any():
        return None
    with np.errstate(invalid="ignore"):
        g = pose & m & (np.abs(dec_croissante - dec_vote) <= LA_TOLERANCE)
    return round(float(g.sum() / m.sum()), 4)


def la_pente(decalage: np.ndarray, masque: np.ndarray, tolerance: float = LA_TOLERANCE,
             demi: float = m300.LE_PAS_0358 / 2.0) -> dict:
    """Entre voisins de la grille tous deux dans le masque et sans déchirure, l'écart de décalage : sa médiane, et la part des
    paires qu'une croissance à `tolerance` ne peut pas suivre (au-delà de la tolérance, en deçà d'un demi-pas)."""
    d = np.where(masque, decalage, np.nan)
    e = np.concatenate([x[np.isfinite(x)] for x in (np.abs(d[:, 1:] - d[:, :-1]), np.abs(d[1:, :] - d[:-1, :]))])
    e = e[e <= demi]
    if not len(e):
        return {"la_mediane_voxels": None, "la_part_au_dela_de_la_tolerance": None}
    return {"la_mediane_voxels": round(float(np.median(e)), 2),
            "la_part_au_dela_de_la_tolerance": round(float((e > tolerance).mean()), 4)}


def la_carte(decalage: np.ndarray, masque: np.ndarray) -> list:
    """Le décalage de chaque point au demi-voxel, None hors du masque ; pour la figure."""
    d = np.where(masque & np.isfinite(decalage), np.round(decalage * 2.0) / 2.0, np.nan)
    return [[None if not np.isfinite(x) else float(x) for x in ligne] for ligne in d]


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    g = d["les_graines"]
    k = sum(1 for x in g if x["la_nappe"] == "suit sa feuille")
    return {"decidable": True, "k": k, "n": len(g),
            "lissue": f"sur {k} des {len(g)} graines, la nappe qui refuse de changer de feuille suit encore sa feuille"}


# ── Les étapes ─────────────────────────────────────────────────────────────────────────────────────────────────────

def preparer() -> dict:
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot, lire_les_valeurs
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    from zarr_depth import array_meta

    t0 = time.monotonic()
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire_, stats = lecteur_du_depot(pred, m300.LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    lv = lambda idx: lire_les_valeurs(idx, pred, lire_)  # noqa: E731
    d301 = {tuple(g["la_graine"]): g for g in json.loads(CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    vote = {}
    r302, _ = m302.retirer()
    for rang, x in r302["les_nappes"].items():
        vote[rang] = x
    plan = {"les_graines": [], "les_surfaces": {}}
    surfaces = {}
    for g in m301.les_graines_neuves():
        cle = (g["x"], g["y"], g["z"])
        rang = d301[cle]["le_rang"]
        nz, ny, nx = g["normale_zyx"]
        r = la_nappe_croissante(cle, (nx, ny, nz), lv)
        e = {"le_rang": rang, "la_graine": list(cle), "les_points_poses": int(r["valide"].sum()),
             "la_part_du_plan": round(float(r["valide"].mean()), 4),
             "les_dechirures": m300.les_dechirures(r["le_decalage"], r["valide"], m300.LE_PAS_0358 / 2.0),
             "les_boucles": m302.les_boucles_qui_ne_ferment_pas(r["le_decalage"], r["valide"], m300.LE_PAS_0358),
             "la_nappe_du_vote_suivait": d301[cle]["la_nappe"]}
        if rang in vote:
            e["la_part_du_vote_gardee"] = la_part_gardee(r["le_decalage"], r["valide"], vote[rang]["le_decalage"],
                                                         vote[rang]["valide"])
            e["la_pente_du_vote"] = la_pente(vote[rang]["le_decalage"], vote[rang]["appui"])
        e["la_pente"] = la_pente(r["le_decalage"], r["valide"])
        print(json.dumps(e, ensure_ascii=False), flush=True)
        e["la_carte"] = la_carte(r["le_decalage"], r["valide"])
        if rang in vote:
            e["la_carte_du_vote"] = la_carte(vote[rang]["le_decalage"], vote[rang]["appui"])
        nn, nok = les_normales(r["la_nappe"], r["valide"])
        for nom, (p, m, nr) in m300.la_famille(f"g{rang}", r["la_nappe"], r["valide"], nn, nok, m300.LE_PAS_0358,
                                               m300.LE_PAS_DU_PLAN).items():
            surfaces[nom] = [{"la_piece": [rang], "points": p[m], "normales": nr[m]}]
        plan["les_graines"].append(e)
    v = m298.LES_VOLUMES["PHerc0358"]
    vol = m298.LesMorceaux("PHerc0358", v["url"], v["niveau"])
    T = m298.la_demi_fenetre("PHerc0358")
    tous = set()
    LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
    for nom, morceaux in surfaces.items():
        f = LES_SURFACES_PREPAREES / f"PHerc0358__{nom}.npz"
        pts = np.concatenate([m["points"] for m in morceaux])
        nrm = np.concatenate([m["normales"] for m in morceaux])
        np.savez_compressed(f, points=pts, normales=nrm, groupe=np.zeros(len(pts), dtype=int), juge=np.full(len(pts), np.nan),
                            groupes=np.array([json.dumps(morceaux[0]["la_piece"])]))
        if len(pts):
            coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
            tous |= m298.les_morceaux_complets(coords[m298.dans_le_volume(coords, vol.forme)], vol.taille)
        plan["les_surfaces"][nom] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": len(pts)}
    cles = sorted(tous)
    (LE_DOSSIER / "morceaux.json").write_text(json.dumps(cles))
    plan.update(les_pannes=list(stats["pannes"]), les_morceaux={"combien": len(cles)},
                les_secondes=round(time.monotonic() - t0, 1))
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
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
    res = {nom: m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T) for nom, info in plan["les_surfaces"].items()}
    d301 = {g["le_rang"]: g for g in json.loads(CE_QUE_301_A_PUBLIE.read_text())["le_rouleau"]["les_graines"]}
    graines = []
    for g in plan["les_graines"]:
        g = dict(g, le_z_de_la_nappe_du_vote=d301[g["le_rang"]].get("le_detail", {}).get("nappe", {}).get("le_z"))
        base = f"g{g['le_rang']}"
        if base not in res or not res[base]:
            graines.append(dict(g, le_z=None, lalignement=None, les_points_juges=0, la_nappe="non jugée"))
            continue
        a = res[base][0]
        tem = [res[f"{base}__{r}_{ph:g}"][0]["lalignement"] for r in m298.LES_PENTES for ph in m300.LES_PHASES]
        z = m300.le_z(a["lalignement"], tem)
        graines.append(dict(g, le_z=z, lalignement=a["lalignement"], les_points_juges=a["les_points_juges"],
                            sans_matiere=a["sans_matiere"], la_nappe=m300.la_piece(z, a["les_points_juges"])))
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"la_tolerance_voxels": LA_TOLERANCE, "le_z_minimum": m300.LE_Z_MINIMUM,
                            "le_minimum_de_points_juges": m298.LE_MINIMUM_DE_POINTS_PAR_PIECE},
         "les_pannes": plan["les_pannes"], "les_graines": graines, "les_morceaux": plan["les_morceaux"]}
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

    h, w = 9, 9
    # Deux feuilles, à 0 et à 12 voxels partout ; la graine au centre, sur celle de 0.
    deux = [np.array([0.0, 12.0])] * (h * w)
    dec, pose = croitre(deux, (h, w), (4, 4))
    v("★★★★ entre deux feuilles serrées, la croissance reste sur celle de la graine",
      pose.all() and np.allclose(dec, 0.0))
    # Une feuille qui monte en pente douce (2 voxels par pas de grille) : la croissance la suit.
    pente = [np.array([2.0 * (k % w) - 8.0, 2.0 * (k % w) - 8.0 + 12.0]) for k in range(h * w)]
    dec, pose = croitre(pente, (h, w), (4, 4))
    v("★★★★ une feuille en pente douce est suivie d'un bout à l'autre, sans passer à sa voisine",
      pose.all() and np.allclose(dec, np.tile(2.0 * np.arange(w) - 8.0, (h, 1))))
    # Une moitié de grille où la feuille de la graine disparaît, seule la voisine reste : refusée.
    trou = [np.array([0.0, 12.0]) if (k % w) < 5 else np.array([12.0]) for k in range(h * w)]
    dec, pose = croitre(trou, (h, w), (4, 4))
    v("★★★★ là où seule la feuille voisine reste, la croissance laisse un trou au lieu d'y passer",
      pose[:, :5].all() and not pose[:, 5:].any())
    coin = [np.array([v]) for v in (0.0, 4.0, 8.0, 4.0, 0.0, 4.0, 8.0, 12.0, 12.0)]
    dec, pose = croitre(coin, (3, 3), (1, 1))
    v("★★★★ un point que ses premiers voisins refusent est repris quand d'autres voisins s'y posent",
      pose[0].all() and dec[0, 2] == 8.0 and not pose[2, 1:].any())
    percee = [np.empty(0) if (k % w) == 6 and k // w < 7 else np.array([0.0]) for k in range(h * w)]
    dec, pose = croitre(percee, (h, w), (4, 4))
    v("★★★★ un point sans feuille de m7 n'est jamais posé, et la croissance le contourne",
      not pose[:7, 6].any() and np.isnan(dec[:7, 6]).all() and pose[:, 7:].all() and pose[7:, 6].all())
    vide = [np.empty(0)] * (h * w)
    v("★★★ sans feuille à la graine, rien n'est posé", not croitre(vide, (h, w), (4, 4))[1].any())
    loin = [np.array([40.0])] * (h * w)
    v("★★★ une feuille au-delà de la portée n'est pas prise à la graine", not croitre(loin, (h, w), (4, 4))[1].any())
    dec, pose = croitre(deux, (h, w), (4, 4), demi_portee=LA_TOLERANCE, cible_de_depart=11.0)
    v("★★★ un départ donné prend la feuille la plus proche de sa cible, et la croissance y reste",
      pose.all() and np.allclose(dec, 12.0))
    dv = np.zeros((h, w))
    okv = np.ones((h, w), dtype=bool)
    dc = np.zeros((h, w))
    dc[:, 6:] = 12.0
    pc = np.ones((h, w), dtype=bool)
    pc[:, :1] = False
    v("★★★ la part gardée : les points du vote que la croissance pose à au plus un quart de pas",
      la_part_gardee(dc, pc, dv, okv) == round(45 / 81, 4))
    pt = la_pente(np.array([[0.0, 2.0, 9.0, 30.0]]), np.ones((1, 4), dtype=bool))
    v("★★★ la pente : médiane des écarts sans les déchirures, et la part au-delà de la tolérance",
      pt == {"la_mediane_voxels": 4.5, "la_part_au_dela_de_la_tolerance": 0.5}, str(pt))
    c = la_carte(np.array([[0.26, np.nan], [-3.74, 5.0]]), np.array([[True, True], [True, False]]))
    v("★★★ la carte : au demi-voxel, None hors du masque et là où rien n'est posé", c == [[0.5, None], [-3.5, None]], str(c))
    vd = le_verdict({"les_graines": [{"la_nappe": "suit sa feuille"}, {"la_nappe": "non jugée"},
                                     {"la_nappe": "suit sa feuille"}]})
    v("★★★ l'issue : k graines sur n", vd["k"] == 2 and vd["lissue"].startswith("sur 2 des 3 graines"))
    v("★★★ l'issue : indécidable si une lecture a échoué", not le_verdict({"les_pannes": ["x"], "les_graines": []})["decidable"])

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
    print(texte)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
