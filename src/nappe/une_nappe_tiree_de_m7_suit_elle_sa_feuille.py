"""Une première surface tirée de la seule prédiction m7 suit-elle sa feuille sur un rouleau du prix, et la spire suivante aussi ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LA MOINDRE NAPPE NE SOIT TIRÉE DE `m7` SUR PHerc0358, ET AVANT QUE LES BLOCS D'ÉTALONNAGE NE
SOIENT LUS. Ce qui était vu avant d'écrire : tout ce que `298` et `299` publient, dont l'alignement des quatre surfaces du traceur
(celui de leurs rampes, en médiane) et les graines de `trouver_graine.py`, que cette tranche reprend.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P99` ET #17. `299` montre deux choses. Un témoin fait de deux rampes est trop maigre
pour qu'un seuil tienne bloc par bloc. Et les surfaces que le traceur pousse sur PHerc0358 ne s'alignent pas plus sur les
feuilles que leurs propres traversées. Le juge doit donc être refait avec un vrai hasard, et la première surface doit venir
d'ailleurs que du traceur. Sur le segment de PHercParis4, la chaîne de `248` passe d'une spire à la suivante en lisant `m7` le long
de la normale, avec un vote entre voisins ; la même lecture, partie d'un plan posé sur une graine, tire de `m7` une première
nappe, puis la spire suivante.

## Le juge : l'alignement contre huit traversées

L'alignement d'une pièce est celui de `299` : l'amplitude de la moyenne de ses profils le long de la normale, ±200 µm, chacun
ramené à moyenne nulle et écart un. Il est comparé à celui de huit rampes plantées dans les propres points de la pièce : pentes 1/4
et 1, amplitude deux pas, et quatre phases chacune, décalées d'un quart de la période de la dent de scie. Z = (alignement − moyenne
des huit) / écart des huit. Une pièce **suit sa feuille** si Z ≥ 3.

## L'étalonnage, sur PHercParis4 au niveau 2, sur six blocs encore neufs

Parmi les candidats de `257`, hors des six de `296` et des six de `299`, ceux de rang ⌊k(N − 1)/7⌉. Le juge sépare si, sur
chacun, le segment réduit et le premier saut ont Z ≥ 3, et les deux rampes de phase nulle plantées dans le segment, jugées
chacune contre ses propres huit rampes, Z < 3.

## La nappe, tirée de `m7` seule, sur PHerc0358 au niveau 0 (9,362 µm)

Pour chacune des quatre graines de `299` (`trouver_graine.py`, sa normale de tenseur de structure comprise) : un plan de 65 × 65
points au pas de 10 voxels (6 mm), perpendiculaire à la normale de la graine et centré sur elle. Chaque point lit `m7` le long de
la normale, de −30 à +30 voxels (un pas et demi), et les centres des plages allumées sont ses feuilles possibles. Tous visent
d'abord le plan ; puis, tour après tour, chaque point vise la médiane de ses neuf voisins et prend la feuille la plus proche à
moins d'un demi-pas (10 voxels), comme le vote de `247`. La nappe est le plan déplacé de ce qu'il a trouvé.

**La spire suivante**, des deux côtés : de chaque point de la nappe, le long de sa normale recalculée, la première feuille de `m7`
au-delà de la sienne (plus de 3 voxels), sur trois pas, puis le même vote. Le pas est celui de PHerc0358, 187,24 µm, 20 voxels.

## Les issues, exclusives

- l'étalonnage ne sépare pas : **au pas du prix, l'alignement contre huit traversées ne sépare pas une feuille d'une
  traversée**, et rien n'est jugé sur le rouleau ;
- sinon, pour chaque graine, la nappe suit sa feuille ou non, et chaque spire suivante aussi ; l'issue de la tranche : **sur k
  des quatre graines, la nappe tirée de m7 suit sa feuille, et sur j d'entre elles une spire suivante aussi** ;
- indécidable si une lecture de `m7` ou du scan échoue.

## Rapporté à côté, qui ne décide rien

- la part des points de la nappe appuyés sur une feuille de `m7`, et la part sans matière dans le scan ;
- les déchirures : la part des paires de voisins dont le décalage diffère de plus d'un demi-pas ;
- le pas de chaque spire suivante, en médiane, contre le pas du rouleau ;
- l'alignement et Z des quatre surfaces du traceur de `299`, sur leurs dix premières pièces jugées.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : sur quelle feuille la nappe est posée, ni si elle passe d'une feuille à la voisine, que
l'alignement ne voit pas si le passage garde la phase (les déchirures en sont un relevé, pas un juge) ; que la spire suivante soit
la voisine et non une plus lointaine ; ni ce que vaut une nappe de 6 mm pour un rouleau entier.

Usage :
    uv run python src/nappe/une_nappe_tiree_de_m7_suit_elle_sa_feuille.py --verifier
    uv run python src/nappe/une_nappe_tiree_de_m7_suit_elle_sa_feuille.py --tirer
    uv run python src/nappe/une_nappe_tiree_de_m7_suit_elle_sa_feuille.py --preparer
    uv run python src/nappe/une_nappe_tiree_de_m7_suit_elle_sa_feuille.py --lire 8
    uv run python src/nappe/une_nappe_tiree_de_m7_suit_elle_sa_feuille.py \\
        --json docs/mesures/une_nappe_tiree_de_m7_suit_elle_sa_feuille.json
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

LE_DOSSIER = RACINE / "data" / "nappe_de_m7"
LES_SURFACES_PREPAREES = LE_DOSSIER / "surfaces"
LE_PLAN = LE_DOSSIER / "plan.json"
LES_NAPPES = LE_DOSSIER / "nappes.npz"
LES_NAPPES_JSON = LE_DOSSIER / "nappes.json"
LE_CACHE_M7 = LE_DOSSIER / "m7"
CE_QUE_299_A_PUBLIE = RACINE / "docs" / "mesures" / "lalignement_des_profils_dit_il_si_une_premiere_surface_suit_sa_feuille.json"

LE_Z_MINIMUM = 3.0
LES_PHASES = (0.0, 0.5, 1.0, 1.5)      # en demi-périodes de la dent de scie : un quart de sa période
LE_COTE_DU_PLAN = 65
LE_PAS_DU_PLAN = 10.0                  # voxels du niveau 0 de PHerc0358
LE_PAS_0358 = 187.24 / 9.362          # 20 voxels
LA_DEMI_PORTEE = 1.5 * LE_PAS_0358     # la nappe cherche sa feuille sur un pas et demi de part et d'autre du plan
LE_CONTROLE = 3.0                      # la plage de sa propre feuille, en voxels (29 µm, comme les 12 voxels de 2,4 µm)
LES_TOURS = 30
LE_REPOS = 1e-3


# ── Le juge ────────────────────────────────────────────────────────────────────────────────────────────────────────

def les_huit_rampes(points, valide, normales, n_ok, pas, pas_de_grille) -> dict:
    """Huit rampes plantées dans une surface : deux pentes, quatre phases ; normales recalculées."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    ok = valide & n_ok
    x = np.arange(points.shape[1]) * pas_de_grille
    amp = m298.LAMPLITUDE_EN_PAS * pas
    out = {}
    for nom, pente in m298.LES_PENTES.items():
        for phase in LES_PHASES:
            dec = m298.la_dent_de_scie(x + phase * amp / pente, pente, amp)
            dp = points + dec[None, :, None] * normales
            nn, nok = les_normales(dp, ok)
            out[f"{nom}_{phase:g}"] = (dp, ok & nok, nn)
    return out


def le_z(a: float | None, temoins: list) -> float | None:
    """L'écart de l'alignement à la moyenne de ses traversées, en écarts de celles-ci ; None s'il en manque ou si elles ne
    varient pas."""
    t = [x for x in temoins if x is not None]
    if a is None or len(t) < len(temoins) or len(t) < 2:
        return None
    s = float(np.std(t, ddof=1))
    return round((a - float(np.mean(t))) / s, 3) if s > 1e-6 else None


def la_piece(z: float | None, n: int) -> str:
    if z is None or n < m298.LE_MINIMUM_DE_POINTS_PAR_PIECE:
        return "non jugée"
    return "suit sa feuille" if z >= LE_Z_MINIMUM else "ne la suit pas"


def letalonnage_separe(blocs: list[dict]) -> dict:
    raisons = []
    for b in blocs:
        for nom in ("le_segment", "saut_1"):
            if b[nom] is None or not b[nom] >= LE_Z_MINIMUM:
                raisons.append(f"bloc {b['le_bloc']} : le {nom} n'a pas Z ≥ 3 ({b[nom]})")
        for nom in ("rampe_douce", "rampe_raide"):
            if b[nom] is None or not b[nom] < LE_Z_MINIMUM:
                raisons.append(f"bloc {b['le_bloc']} : la {nom} a Z ≥ 3 ({b[nom]})")
    return {"separe": not raisons and len(blocs) == m299.LES_BLOCS, "les_raisons": raisons}


def le_verdict(d: dict) -> dict:
    if d.get("les_pannes"):
        return {"decidable": False, "lissue": f"indécidable : une lecture a échoué ({d['les_pannes'][0]})"}
    if not d["letalonnage"]["le_verdict"]["separe"]:
        return {"decidable": True, "separe": False,
                "lissue": "au pas du prix, l'alignement contre huit traversées ne sépare pas une feuille d'une traversée"}
    graines = d["le_rouleau"]["les_graines"]
    k = sum(1 for g in graines if g["la_nappe"] == "suit sa feuille")
    j = sum(1 for g in graines if g["la_nappe"] == "suit sa feuille"
            and any(g["les_sauts"][c] == "suit sa feuille" for c in ("plus", "moins")))
    return {"decidable": True, "separe": True, "k": k, "j": j,
            "lissue": f"sur {k} des {len(graines)} graines, la nappe tirée de m7 suit sa feuille, et sur {j} d'entre elles "
                      "une spire suivante aussi"}


# ── La nappe et son saut ───────────────────────────────────────────────────────────────────────────────────────────

def le_plan(graine_xyz, normale_xyz, cote: int = LE_COTE_DU_PLAN, pas: float = LE_PAS_DU_PLAN):
    """Un plan de cote × cote points, perpendiculaire à la normale, centré sur la graine ; et sa base."""
    n = np.asarray(normale_xyz, dtype=float)
    n /= np.linalg.norm(n)
    a = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    k = (np.arange(cote) - (cote - 1) / 2.0) * pas
    grille = (np.asarray(graine_xyz, dtype=float)[None, None, :] + k[:, None, None] * v[None, None, :]
              + k[None, :, None] * u[None, None, :])
    return grille, n


def les_plages(vu: np.ndarray, t: np.ndarray) -> list[np.ndarray]:
    """Les centres des plages allumées le long de chaque rayon."""
    out = []
    for m in vu:
        if not m.any():
            out.append(np.empty(0))
            continue
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        out.append(np.array([(t[a] + t[b - 1]) / 2.0 for a, b in zip(bords[::2], bords[1::2])]))
    return out


def la_feuille_apres_la_sienne(t: np.ndarray, vu: np.ndarray, controle: float = LE_CONTROLE) -> np.ndarray:
    """Le centre de la première plage après celle qui touche |t| ≤ `controle` ; sans elle, la première au-delà."""
    out = np.full(vu.shape[0], np.nan)
    at = np.abs(t)
    for k, m in enumerate(vu):
        if not m.any():
            continue
        bords = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(np.int8), [0]])))
        plages = list(zip(bords[::2], bords[1::2]))
        propre = [(a, b) for a, b in plages if at[a] <= controle or at[b - 1] <= controle
                  or (t[a] <= 0 <= t[b - 1]) or (t[b - 1] <= 0 <= t[a])]
        suivantes = [(a, b) for a, b in plages if at[a] > controle] if not propre else \
            [(a, b) for a, b in plages if a >= propre[0][1]]
        if suivantes:
            a, b = suivantes[0]
            out[k] = (t[a] + t[b - 1]) / 2.0
    return out


def le_consensus(carte: np.ndarray) -> np.ndarray:
    """La médiane d'un carré 3 × 3 autour de chaque point, si la majorité en a une valeur."""
    h, w = carte.shape
    bord = np.pad(carte, 1, constant_values=np.nan)
    pile = np.stack([bord[i:i + h, j:j + w] for i in range(3) for j in range(3)])
    vus = np.isfinite(pile).sum(axis=0)
    with np.errstate(all="ignore"):
        med = np.nanmedian(np.where(vus[None] > 0, pile, np.nan), axis=0)
    return np.where(vus >= 5, med, np.nan)


def le_vote(centres: list[np.ndarray], depart: np.ndarray, forme: tuple, demi: float,
            tours: int = LES_TOURS) -> tuple[np.ndarray, np.ndarray, int]:
    """Chaque point vise la médiane de ses voisins et prend la feuille la plus proche à moins d'un demi-pas ; sinon il garde
    sa cible. Rend le champ, le masque des points appuyés sur une feuille, et le nombre de tours."""
    courant = depart.copy()
    appui = np.zeros(len(courant), dtype=bool)
    n = 0
    for n in range(1, tours + 1):
        cible = le_consensus(courant.reshape(forme)).ravel()
        cible = np.where(np.isfinite(cible), cible, courant)
        neuf = cible.copy()
        appui = np.zeros(len(courant), dtype=bool)
        for k, c in enumerate(centres):
            if len(c) and np.isfinite(cible[k]):
                d = np.abs(c - cible[k])
                m = int(np.argmin(d))
                if d[m] < demi:
                    neuf[k], appui[k] = c[m], True
        with np.errstate(invalid="ignore"):
            change = int((np.abs(neuf - courant) > 0.5).sum())
        courant = neuf
        if change < LE_REPOS * len(courant):
            break
    return courant, appui, n


def les_dechirures(decalage: np.ndarray, valide: np.ndarray, demi: float) -> float | None:
    """La part des paires de voisins, sur la grille, dont le décalage diffère de plus d'un demi-pas."""
    d = np.where(valide, decalage, np.nan)
    paires = [np.abs(d[:, 1:] - d[:, :-1]), np.abs(d[1:, :] - d[:-1, :])]
    tout = np.concatenate([p[np.isfinite(p)] for p in paires])
    return round(float((tout > demi).mean()), 4) if len(tout) else None


def lire_m7(points_zyx_idx: np.ndarray, lecteur) -> np.ndarray:
    """La valeur de `m7` aux indices (…, 3) en (z, y, x), au niveau 0."""
    from le_transfert_retrouve_t_il_la_spire_voisine import lire_les_valeurs

    pred, lire = lecteur
    return lire_les_valeurs(points_zyx_idx, pred, lire)


def tirer_une_nappe(graine_xyz, normale_xyz, lecteur, lire_valeurs=None, cote: int = LE_COTE_DU_PLAN,
                    pas_du_plan: float = LE_PAS_DU_PLAN) -> dict:
    """La nappe de `m7` autour d'une graine, puis la spire suivante de chaque côté. `lire_valeurs(idx)` remplace la lecture
    du dépôt, pour la batterie."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales

    if lire_valeurs is None:
        lire_valeurs = lambda idx: lire_m7(idx, lecteur)  # noqa: E731

    grille, n = le_plan(graine_xyz, normale_xyz, cote, pas_du_plan)
    forme = grille.shape[:2]
    p = grille.reshape(-1, 3)
    t = np.arange(-np.floor(LA_DEMI_PORTEE), np.floor(LA_DEMI_PORTEE) + 1.0)
    idx = np.floor((p[:, None, :] + t[None, :, None] * n[None, None, :])[..., ::-1]).astype(np.int64)
    vu = lire_valeurs(idx) > 0
    centres = les_plages(vu, t)
    haut, appui, tours = le_vote(centres, np.zeros(len(p)), forme, LE_PAS_0358 / 2.0)
    nappe = (p + haut[:, None] * n[None, :]).reshape(forme + (3,))
    ok = np.isfinite(haut).reshape(forme)
    out = {"la_nappe": nappe, "valide": ok, "le_decalage": haut.reshape(forme), "appui": appui.reshape(forme),
           "les_tours": tours, "les_sauts": {}}
    nn, nok = les_normales(nappe, ok)
    q, nq = nappe.reshape(-1, 3), nn.reshape(-1, 3)
    tt = np.arange(0.0, 3.0 * LE_PAS_0358 + 1.0)
    for nom, cote in (("plus", 1.0), ("moins", -1.0)):
        ts = cote * tt
        idx = np.floor((q[:, None, :] + ts[None, :, None] * nq[:, None, :])[..., ::-1]).astype(np.int64)
        vu = lire_valeurs(idx) > 0
        suivante = la_feuille_apres_la_sienne(ts, vu)
        depart = np.where(np.isfinite(suivante), suivante, cote * LE_PAS_0358)
        pas_, appui_s, tours_s = le_vote(les_plages(vu, ts), depart, forme, LE_PAS_0358 / 2.0)
        spire = (q + pas_[:, None] * nq).reshape(forme + (3,))
        ok_s = (nok & np.isfinite(pas_).reshape(forme))
        out["les_sauts"][nom] = {"la_spire": spire, "valide": ok_s, "le_pas": pas_.reshape(forme),
                                 "appui": appui_s.reshape(forme), "les_tours": tours_s}
    return out


def tirer() -> dict:
    """Les quatre nappes de `m7` et leurs spires suivantes, rangées sur disque ; rien n'est lu du scan."""
    from le_transfert_retrouve_t_il_la_spire_voisine import lecteur_du_depot

    from zarr_depth import array_meta

    graines = json.loads((m299.LES_GRAINES).read_text())["candidats"]
    graines = m299.les_graines_retenues(graines)
    url = f"{m298.BUCKET}/{m299.LA_PREDICTION_0358}"
    pred = array_meta(url, 0, 120.0)
    lire, stats = lecteur_du_depot(pred, LE_CACHE_M7, "m7_L0", m299.LA_PREDICTION_0358, 0)
    tableaux, resume = {}, []
    for rang, g in enumerate(graines, 1):
        t0 = time.monotonic()
        nz, ny, nx = g["normale_zyx"]
        r = tirer_une_nappe((g["x"], g["y"], g["z"]), (nx, ny, nz), (pred, lire))
        tableaux[f"g{rang}_nappe"] = r["la_nappe"]
        tableaux[f"g{rang}_nappe_ok"] = r["valide"]
        tableaux[f"g{rang}_nappe_appui"] = r["appui"]
        tableaux[f"g{rang}_nappe_decalage"] = r["le_decalage"]
        e = {"le_rang": rang, "la_graine": [g["x"], g["y"], g["z"]], "la_normale_xyz": [nx, ny, nz],
             "la_part_appuyee": round(float(r["appui"].mean()), 4), "les_tours": r["les_tours"],
             "les_dechirures": les_dechirures(r["le_decalage"], r["valide"], LE_PAS_0358 / 2.0), "les_sauts": {}}
        for c, s in r["les_sauts"].items():
            tableaux[f"g{rang}_{c}"] = s["la_spire"]
            tableaux[f"g{rang}_{c}_ok"] = s["valide"]
            tableaux[f"g{rang}_{c}_appui"] = s["appui"]
            pas_ = s["le_pas"][s["valide"] & s["appui"]]
            e["les_sauts"][c] = {"la_part_appuyee": round(float(s["appui"].mean()), 4), "les_tours": s["les_tours"],
                                 "le_pas_median_des_appuyes_voxels": round(float(np.median(np.abs(pas_))), 2)
                                 if len(pas_) else None,
                                 "les_dechirures": les_dechirures(s["le_pas"], s["valide"], LE_PAS_0358 / 2.0)}
        e["les_secondes"] = round(time.monotonic() - t0, 1)
        resume.append(e)
        print(json.dumps(e, ensure_ascii=False), flush=True)
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(LES_NAPPES, **tableaux)
    d = {"les_nappes": resume, "la_lecture_de_m7": {k: (v if k != "pannes" else v[:20]) for k, v in stats.items()}}
    LES_NAPPES_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    return d


# ── Préparer, lire, mesurer ────────────────────────────────────────────────────────────────────────────────────────

def la_famille(nom, points, valide, normales, n_ok, pas, pas_de_grille) -> dict:
    """Une surface jugée et ses huit rampes."""
    fam = {nom: (points, valide & n_ok, normales)}
    for r, v in les_huit_rampes(points, valide, normales, n_ok, pas, pas_de_grille).items():
        fam[f"{nom}__{r}"] = v
    return fam


def les_surfaces_de_paris4() -> tuple[dict, list]:
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_procedure_sans_juge_tient_elle_sur_le_segment_entier import le_segment
    from la_spire_voisine_est_elle_a_un_pas import LE_CACHE, les_normales, lire_tifxyz
    from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS

    k = m298.LE_SURECHANTILLONNAGE["PHercParis4"]
    deja = (json.loads(j296.LE_PLAN.read_text())["les_blocs_de_la_partie_b"]
            + json.loads(CE_QUE_299_A_PUBLIE.read_text())["letalonnage"]["les_blocs"])
    deja = [b["le_bloc"] if isinstance(b, dict) else b for b in deja]
    _, _, _, candidats = le_segment(LE_CACHE)
    blocs = m299.les_blocs_neufs(sorted(candidats), deja)
    grilles = {"le_segment": lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage"),
               "saut_1": lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[1] / "maillage")}
    esp = grilles["le_segment"][2]
    out: dict = {}
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        for n, (pts, ok, _) in grilles.items():
            L, C = lignes[lignes < ok.shape[0]], colonnes[colonnes < ok.shape[1]]
            sp, sok = m298.surechantillonner(pts[np.ix_(L, C)], ok[np.ix_(L, C)], k)
            nn, nok = les_normales(sp, sok)
            fam = la_famille(n, sp, sok, nn, nok, float(PAS_EN_VOXELS), esp / k)
            if n == "le_segment":
                for dn, (dp, dok) in m298.les_defauts(sp, sok, nn, nok, float(DEMI_PAS_EN_VOXELS), float(PAS_EN_VOXELS),
                                                      esp / k).items():
                    if dn not in m298.LES_PENTES:
                        continue
                    rn, rok = les_normales(dp, dok)
                    fam.update(la_famille(dn, dp, dok, rn, rok, float(PAS_EN_VOXELS), esp / k))
            for nom, (p, m, nr) in fam.items():
                out.setdefault(nom, []).append({"le_bloc": list(b), "points": p[m], "normales": nr[m], "juge": None})
    return out, [list(b) for b in blocs]


def les_surfaces_de_0358() -> dict:
    """Les nappes, leurs spires suivantes, et les dix premières pièces jugées des surfaces du traceur de `299`."""
    from la_spire_voisine_est_elle_a_un_pas import les_normales, lire_tifxyz

    z = np.load(LES_NAPPES)
    out: dict = {}
    rangs = sorted({int(k[1:].split("_")[0]) for k in z.files})
    for r in rangs:
        for s in ("nappe", "plus", "moins"):
            pts, ok = z[f"g{r}_{s}"], z[f"g{r}_{s}_ok"]
            nn, nok = les_normales(pts, ok)
            for nom, (p, m, nr) in la_famille(f"g{r}_{s}", pts, ok, nn, nok, LE_PAS_0358, LE_PAS_DU_PLAN).items():
                out[nom] = [{"la_piece": [r, s], "points": p[m], "normales": nr[m], "juge": None}]
    d299 = json.loads(CE_QUE_299_A_PUBLIE.read_text())
    k = m298.LE_SURECHANTILLONNAGE["PHerc0358"]
    P = m298.LA_PIECE_EN_MAILLES * k
    for s in d299["le_rouleau"]["les_surfaces"]:
        t = next(x for x in d299["le_rouleau"]["les_traces"] if x["le_rang"] == s["le_rang"])
        pieces = [p["le_groupe"] for p in s["le_detail"] if p["la_piece"] != "non jugée"][:10]
        pts, ok, esp = lire_tifxyz(RACINE / t["la_surface"])
        sp, sok = m298.surechantillonner(pts, ok, k)
        for i0, j0 in pieces:
            a, b = i0 * k, j0 * k
            bp, bok = sp[a:a + P, b:b + P], sok[a:a + P, b:b + P]
            nn, nok = les_normales(bp, bok)
            for nom, (p, m, nr) in la_famille(f"trace{s['le_rang']}_{i0}_{j0}", bp, bok, nn, nok, LE_PAS_0358,
                                              esp / k).items():
                out[nom] = [{"la_piece": [s["le_rang"], i0, j0], "points": p[m], "normales": nr[m], "juge": None}]
    return out


def preparer() -> dict:
    t0 = time.monotonic()
    paris, blocs = les_surfaces_de_paris4()
    prix = les_surfaces_de_0358()
    plan = {"les_blocs": blocs, "les_surfaces": {}, "les_morceaux": {}}
    for volume, surfaces, cle in (("PHercParis4", paris, "le_bloc"), ("PHerc0358", prix, "la_piece")):
        v = m298.LES_VOLUMES[volume]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        tous = set()
        for nom, morceaux in surfaces.items():
            LES_SURFACES_PREPAREES.mkdir(parents=True, exist_ok=True)
            f = LES_SURFACES_PREPAREES / f"{volume}__{nom}.npz"
            np.savez_compressed(f, points=np.concatenate([m["points"] for m in morceaux]),
                                normales=np.concatenate([m["normales"] for m in morceaux]),
                                groupe=np.concatenate([np.full(len(m["points"]), i) for i, m in enumerate(morceaux)]),
                                juge=np.full(sum(len(m["points"]) for m in morceaux), np.nan),
                                groupes=np.array([json.dumps(m[cle]) for m in morceaux]))
            n = sum(len(m["points"]) for m in morceaux)
            if n:
                pts = np.concatenate([m["points"] for m in morceaux])
                nrm = np.concatenate([m["normales"] for m in morceaux])
                coords = m298.les_coordonnees(pts, nrm, v["facteur"], T)
                tous |= m298.les_morceaux_complets(coords[m298.dans_le_volume(coords, vol.forme)], vol.taille)
            plan["les_surfaces"][f"{volume}__{nom}"] = {"le_fichier": str(f.relative_to(RACINE)), "les_points": n}
        cles = sorted(tous)
        (LE_DOSSIER / f"morceaux_{volume}.json").write_text(json.dumps(cles))
        plan["les_morceaux"][volume] = {"combien": len(cles), "les_octets": int(len(cles) * np.prod(vol.taille))}
    plan["les_secondes"] = round(time.monotonic() - t0, 1)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


def lire(ouvriers: int = 8) -> dict:
    out = {}
    for volume, v in m298.LES_VOLUMES.items():
        t0 = time.monotonic()
        cles = [tuple(c) for c in json.loads((LE_DOSSIER / f"morceaux_{volume}.json").read_text())]
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        comptes = {"deja": 0, "tire": 0, "absent": 0}
        with ThreadPoolExecutor(ouvriers) as ex:
            for r in ex.map(lambda c: vol.tirer(*c), cles):
                comptes[r] += 1
        out[volume] = dict(comptes, combien=len(cles), les_secondes=round(time.monotonic() - t0, 1))
        print(json.dumps({volume: out[volume]}), flush=True)
    (LE_DOSSIER / "lire.json").write_text(json.dumps(out, indent=1))
    return out


def le_z_de(res: dict, nom: str) -> tuple[float | None, float | None, list, int]:
    """L'alignement d'une surface d'un seul groupe, ceux de ses huit rampes, Z et ses points jugés."""
    a = res[nom][0]
    temoins = [res[f"{nom}__{r}_{ph:g}"][0]["lalignement"] for r in m298.LES_PENTES for ph in LES_PHASES]
    return le_z(a["lalignement"], temoins), a["lalignement"], temoins, a["les_points_juges"]


def la_part_juste_par_bloc(blocs: list) -> list[dict]:
    """Rapporté, qui ne décide rien : sur chaque bloc, la part des mailles notées du premier saut que le juge géométrique de
    `248` dit sur la bonne spire. Le premier saut n'est pas un référent : il est juste à 0,9177 sur le segment entier."""
    import le_tour_produit_porte_t_il_le_texte_du_segment as j296
    from la_spire_voisine_est_elle_a_un_pas import lire_tifxyz

    J = np.load(RACINE / "data" / "encre_du_tour_voisin" / "la_chaine_juge_de_248_saut_1.npy")
    _, _, esp = lire_tifxyz(j296.LE_DOSSIER / j296.LES_SURFACES[0] / "maillage")
    out = []
    for b in blocs:
        lignes, colonnes = j296.les_mailles_dune_bande(*b, 1, esp)
        L, C = lignes[lignes < J.shape[0]], colonnes[colonnes < J.shape[1]]
        x = J[np.ix_(L, C)]
        notes = np.isfinite(x)
        out.append({"le_bloc": list(b), "les_mailles_notees": int(notes.sum()),
                    "la_part_juste": round(float(x[notes].mean()), 4) if notes.any() else None})
    return out


def les_releves(d: dict) -> dict:
    """Ce qui se lit de la mesure sans rien décider : les pièces du traceur, et les extrêmes de l'étalonnage."""
    z = [p["le_z"] for p in d["le_rouleau"]["les_pieces_du_traceur"] if p["le_z"] is not None]
    bons = [b[n] for b in d["letalonnage"]["les_blocs"] for n in ("le_segment", "saut_1") if b[n] is not None]
    rampes = [b[n] for b in d["letalonnage"]["les_blocs"] for n in ("rampe_douce", "rampe_raide") if b[n] is not None]
    seg = [b["le_segment"] for b in d["letalonnage"]["les_blocs"] if b["le_segment"] is not None]
    return {"les_pieces_du_traceur": {"combien": len(z), "au_moins_3": int(sum(x >= LE_Z_MINIMUM for x in z)),
                                      "le_z_median": round(float(np.median(z)), 3) if z else None,
                                      "le_z_min": min(z) if z else None, "le_z_max": max(z) if z else None},
            "letalonnage": {"les_surfaces_justes_au_moins_3": int(sum(x >= LE_Z_MINIMUM for x in bons)),
                            "les_surfaces_justes": len(bons), "le_plus_bas_des_justes": min(bons) if bons else None,
                            "le_plus_bas_du_trace": min(seg) if seg else None,
                            "les_rampes_au_moins_3": int(sum(x >= LE_Z_MINIMUM for x in rampes)),
                            "les_rampes": len(rampes), "le_plus_haut_des_rampes": max(rampes) if rampes else None}}


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    res: dict = {}
    for volume, v in m298.LES_VOLUMES.items():
        vol = m298.LesMorceaux(volume, v["url"], v["niveau"])
        T = m298.la_demi_fenetre(volume)
        for cle, info in plan["les_surfaces"].items():
            if cle.startswith(volume + "__"):
                res[cle] = m299.juger(vol, RACINE / info["le_fichier"], v["facteur"], T)
        print(f"{volume} ({time.monotonic() - t0:.0f} s)", flush=True)
    blocs = []
    for i, b in enumerate(plan["les_blocs"]):
        ligne = {"le_bloc": b, "lalignement": {}, "les_temoins": {}}
        for nom in ("le_segment", "saut_1", "rampe_douce", "rampe_raide"):
            base = f"PHercParis4__{nom}"
            a = res[base][i]["lalignement"]
            tem = [res[f"{base}__{r}_{ph:g}"][i]["lalignement"] for r in m298.LES_PENTES for ph in LES_PHASES]
            ligne[nom] = le_z(a, tem)
            ligne["lalignement"][nom] = a
            ligne["les_temoins"][nom] = [round(float(np.mean([x for x in tem if x is not None])), 3),
                                         round(float(np.std([x for x in tem if x is not None], ddof=1)), 3)]
        blocs.append(ligne)
    e = {"les_blocs": blocs, "le_verdict": letalonnage_separe(blocs),
         "la_part_juste_du_premier_saut_selon_248": la_part_juste_par_bloc(plan["les_blocs"])}
    nappes = json.loads(LES_NAPPES_JSON.read_text())
    graines = []
    for g in nappes["les_nappes"]:
        r = g["le_rang"]
        e_ = {"le_rang": r, "la_graine": g["la_graine"], "la_part_appuyee": g["la_part_appuyee"],
              "les_dechirures": g["les_dechirures"], "les_sauts": {}, "le_detail": {}}
        for s in ("nappe", "plus", "moins"):
            z, a, tem, n = le_z_de(res, f"PHerc0358__g{r}_{s}")
            sans = res[f"PHerc0358__g{r}_{s}"][0]["sans_matiere"]
            e_["le_detail"][s] = {"le_z": z, "lalignement": a, "la_moyenne_des_temoins": round(float(np.mean(
                [x for x in tem if x is not None])), 3) if any(x is not None for x in tem) else None,
                "les_points_juges": n, "sans_matiere": sans, "la_piece": la_piece(z, n)}
        e_["la_nappe"] = e_["le_detail"]["nappe"]["la_piece"]
        for c in ("plus", "moins"):
            e_["les_sauts"][c] = e_["le_detail"][c]["la_piece"]
            e_["le_detail"][c].update(g["les_sauts"][c])
        graines.append(e_)
    traces = []
    for cle in plan["les_surfaces"]:
        nom = cle.split("__", 1)[1]
        if nom.startswith("trace") and "__" not in nom:
            z, a, tem, n = le_z_de(res, cle)
            traces.append({"la_piece": nom, "le_z": z, "lalignement": a, "les_points_juges": n})
    d = {"la_question": __doc__.splitlines()[0], "les_constantes": {
        "le_z_minimum": LE_Z_MINIMUM, "les_phases": LES_PHASES, "les_pentes": m298.LES_PENTES,
        "le_cote_du_plan": LE_COTE_DU_PLAN, "le_pas_du_plan_voxels": LE_PAS_DU_PLAN, "le_pas_0358_voxels": LE_PAS_0358,
        "la_demi_portee_voxels": LA_DEMI_PORTEE, "le_controle_voxels": LE_CONTROLE},
        "letalonnage": e, "le_rouleau": {"les_graines": graines, "les_pieces_du_traceur": traces},
        "la_lecture_de_m7": nappes["la_lecture_de_m7"], "les_morceaux": plan["les_morceaux"],
        "les_pannes": list(nappes["la_lecture_de_m7"].get("pannes", []))}
    d["le_verdict"] = le_verdict(d)
    d["les_releves"] = les_releves(d)
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

def verifier() -> int:
    import tempfile

    from la_spire_voisine_est_elle_a_un_pas import les_normales

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

    tmp = Path(tempfile.mkdtemp())
    pas = 18.0

    def alignement_de(volume, pts, nrm, nom):
        meta = {"shape": list(volume.shape), "chunks": [16] * 3, "fill_value": 0, "compressor": None}
        vol = m298.LesMorceaux(nom, None, 0, meta=meta, source=m298._source_de(volume, 16), dossier=tmp)
        coords = m298.les_coordonnees(pts, nrm, 1.0, 21)
        dedans = m298.dans_le_volume(coords, vol.forme)
        for c in m298.les_morceaux_complets(coords[dedans], vol.taille):
            vol.tirer(*c)
        pr = m298.les_profils(vol, coords[dedans])
        return m299.lalignement(pr[~m298.sans_matiere(pr)])

    V = m298._feuillets((200, 150, 150), pas, 0, 3.0, bruit=6.0)
    G = np.zeros((40, 40, 3))
    for i in range(40):
        for j in range(40):
            G[i, j] = (40.0 + j * 2.0, 40.0 + i * 2.0, 5 * pas + 4.0)
    OK = np.ones(G.shape[:2], dtype=bool)
    N, NOK = les_normales(G, OK)
    fam = la_famille("s", G, OK, N, NOK, pas, 2.0)
    al = {n: alignement_de(V, p[m], nr[m], f"a_{n}") for n, (p, m, nr) in fam.items()}
    tem = [al[f"s__{r}_{ph:g}"] for r in m298.LES_PENTES for ph in LES_PHASES]
    z = le_z(al["s"], tem)
    v("★★★★ une surface sur le flanc de sa feuille : Z ≥ 3 contre ses huit rampes", lambda: z >= 3.0, f"{z} {al['s']} {tem}")
    rp, rm, rn = fam["s__rampe_douce_0"]
    fr_ = la_famille("r", rp, rm, rn, np.ones_like(rm), pas, 2.0)
    alr = {n: alignement_de(V, p[m], nr[m], f"b_{n}") for n, (p, m, nr) in fr_.items()}
    zr = le_z(alr["r"], [alr[f"r__{r}_{ph:g}"] for r in m298.LES_PENTES for ph in LES_PHASES])
    v("★★★★ une rampe, jugée contre ses huit rampes : Z < 3", lambda: zr < 3.0, str(zr))
    v("★★★ huit rampes : deux pentes, quatre phases, toutes différentes",
      len({n for n in fam if "__" in n}) == 8 and len({round(float(fam[n][0][5, 5, 2]), 3) for n in fam if "__" in n}) == 8)
    v("★★★ Z : sans témoin complet ou sans dispersion, pas de Z",
      le_z(1.0, [0.1, None]) is None and le_z(1.0, [0.2, 0.2, 0.2]) is None and le_z(None, [0.1, 0.2]) is None
      and le_z(0.5, [0.1, 0.3]) == round((0.5 - 0.2) / float(np.std([0.1, 0.3], ddof=1)), 3))
    v("★★★ une pièce : suit si Z ≥ 3, ne suit pas sinon, non jugée sous 100 points",
      la_piece(3.0, 500) == "suit sa feuille" and la_piece(2.99, 500) == "ne la suit pas" and la_piece(9.0, 99) == "non jugée")
    bl = {"le_bloc": [1, 1], "le_segment": 9.0, "saut_1": 5.0, "rampe_douce": 0.4, "rampe_raide": -1.0}
    v("★★★★ l'étalonnage sépare quand les six blocs ordonnent", letalonnage_separe([bl] * 6)["separe"])
    for casse, nom in ((dict(bl, saut_1=2.9), "le premier saut sous 3"), (dict(bl, rampe_douce=3.0), "une rampe à 3")):
        v(f"★★★★ l'étalonnage ne sépare pas si un seul bloc a {nom}", not letalonnage_separe([bl] * 5 + [casse])["separe"])

    # La nappe : un empilement synthétique de feuilles « m7 » perpendiculaires à z, un plan posé un peu à côté.
    M = np.zeros((120, 120, 120), dtype=np.uint8)
    for zz in range(10, 120, 20):
        M[zz:zz + 2] = 255

    def lecteur_synthetique(idx):
        dedans = np.all((idx >= 0) & (idx < 120), axis=-1)
        out = np.zeros(idx.shape[:-1], dtype=np.uint8)
        out[dedans] = M[idx[dedans][:, 0], idx[dedans][:, 1], idx[dedans][:, 2]]
        return out

    r = tirer_une_nappe((60.0, 60.0, 54.0), (0.0, 0.0, 1.0), None, lire_valeurs=lecteur_synthetique, cote=17,
                        pas_du_plan=4.0)
    zs = r["la_nappe"][..., 2][r["valide"]]
    v("★★★★ la nappe rejoint la feuille la plus proche du plan, et s'y tient", np.allclose(zs, 50.5, atol=0.01)
      and r["appui"].mean() > 0.5, f"{np.unique(np.round(zs, 2))[:5]} {r['appui'].mean()}")
    zp = r["les_sauts"]["plus"]["la_spire"][..., 2][r["les_sauts"]["plus"]["valide"]]
    zm = r["les_sauts"]["moins"]["la_spire"][..., 2][r["les_sauts"]["moins"]["valide"]]
    v("★★★★ la spire suivante est la feuille d'après, d'un côté et de l'autre",
      abs(float(np.median(np.abs(zp - 50.5))) - 20.0) < 0.6 and abs(float(np.median(np.abs(zm - 50.5))) - 20.0) < 0.6
      and float(np.median(zp - 50.5)) * float(np.median(zm - 50.5)) < 0, f"{np.median(zp)} {np.median(zm)}")
    loin, ap, _ = le_vote([np.array([15.0])] * 9, np.zeros(9), (3, 3), 10.0)
    v("★★★★ une feuille à plus d'un demi-pas de la cible n'est pas prise : le point garde sa cible, sans appui",
      np.allclose(loin, 0.0) and not ap.any(), f"{loin} {ap}")
    c = np.full((3, 3), np.nan)
    c[0, 0], c[2, 2] = 4.0, 6.0
    v("★★★ le consensus demande la majorité des neuf voisins", np.isnan(le_consensus(c)[1, 1])
      and le_consensus(np.arange(9.0).reshape(3, 3))[1, 1] == 4.0)
    v("★★★ une nappe sans déchirure a zéro déchirure", les_dechirures(r["le_decalage"], r["valide"], 10.0) == 0.0)
    marche = np.zeros((10, 10))
    marche[:, 5:] = 20.0
    v("★★★ une marche d'une feuille se compte comme déchirure", les_dechirures(marche, np.ones((10, 10), bool), 10.0)
      == round(10 / 180, 4))
    t = np.arange(-10.0, 11.0)
    vu = np.zeros((1, 21), dtype=bool)
    vu[0, 9:12] = True
    vu[0, 17:19] = True
    v("★★★ la feuille d'après la sienne : pas la sienne, la suivante", la_feuille_apres_la_sienne(t, vu)[0] == 7.5)
    vu2 = np.zeros((1, 21), dtype=bool)
    vu2[0, 17:19] = True
    v("★★★ sans la sienne, la première au-delà du contrôle", la_feuille_apres_la_sienne(t, vu2)[0] == 7.5)
    g, n = le_plan((0.0, 0.0, 0.0), (0.0, 0.0, 2.0), cote=5, pas=1.0)
    v("★★★ le plan est perpendiculaire à la normale, centré sur la graine, au pas déclaré",
      np.allclose((g.reshape(-1, 3) @ n), 0.0) and np.allclose(g[2, 2], 0.0)
      and np.isclose(np.linalg.norm(g[2, 3] - g[2, 2]), 1.0))
    base = {"letalonnage": {"le_verdict": {"separe": True}}, "le_rouleau": {"les_graines": [
        {"la_nappe": "suit sa feuille", "les_sauts": {"plus": "ne la suit pas", "moins": "suit sa feuille"}},
        {"la_nappe": "suit sa feuille", "les_sauts": {"plus": "ne la suit pas", "moins": "ne la suit pas"}},
        {"la_nappe": "ne la suit pas", "les_sauts": {"plus": "suit sa feuille", "moins": "suit sa feuille"}}]}}
    vd = le_verdict(base)
    v("★★★★ l'issue : k nappes qui suivent, et j d'entre elles avec une spire suivante qui suit",
      vd["k"] == 2 and vd["j"] == 1 and vd["lissue"].startswith("sur 2 des 3 graines"), str(vd))
    b2 = json.loads(json.dumps(base))
    b2["letalonnage"]["le_verdict"]["separe"] = False
    v("★★★★ l'issue : l'étalonnage qui ne sépare pas ne juge rien", le_verdict(b2)["separe"] is False)
    v("★★★ l'issue : indécidable si une lecture a échoué", not le_verdict(dict(base, les_pannes=["x"]))["decidable"])
    rl = les_releves({"le_rouleau": {"les_pieces_du_traceur": [{"le_z": 4.0}, {"le_z": 0.5}, {"le_z": None}, {"le_z": -1.0}]},
                      "letalonnage": {"les_blocs": [{"le_segment": 9.0, "saut_1": 2.5, "rampe_douce": 1.0, "rampe_raide": 3.1}]}})
    v("★★★ les relevés : les pièces du traceur sans les Z absents, et les extrêmes de l'étalonnage",
      rl["les_pieces_du_traceur"] == {"combien": 3, "au_moins_3": 1, "le_z_median": 0.5, "le_z_min": -1.0, "le_z_max": 4.0}
      and rl["letalonnage"]["le_plus_bas_des_justes"] == 2.5 and rl["letalonnage"]["les_rampes_au_moins_3"] == 1, str(rl))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--tirer", action="store_true", help="les nappes de m7 et leurs spires suivantes, sans lire le scan")
    p.add_argument("--preparer", action="store_true")
    p.add_argument("--lire", type=int, default=None, metavar="OUVRIERS")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--releves", type=Path, default=None, metavar="MESURE",
                   help="recalcule les relevés d'une mesure déjà faite, sans rien relire")
    a = p.parse_args()
    if a.releves is not None:
        d = json.loads(a.releves.read_text())
        d["les_releves"] = les_releves(d)
        a.releves.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        print(json.dumps(d["les_releves"], ensure_ascii=False, indent=1))
        return 0
    if a.verifier:
        return verifier()
    if a.tirer:
        print(json.dumps(tirer(), ensure_ascii=False, indent=1))
        return 0
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
