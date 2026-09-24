"""La spire voisine du segment publié est-elle à un pas inter-feuilles, et le segment la porte-t-il ?

⭐⭐⭐⭐ POURQUOI CE FICHIER. Tout ce que la chaîne a construit depuis `198` juge un segment tracé par
d'autres. La tranche suivante en PRODUIT un : la spire voisine de `20230702185753`, un pas inter-feuilles
plus loin le long de sa normale, recalée sur la matière. Avant de l'écrire, deux choses doivent être
mesurées, et ce fichier les mesure :

1. **le témoin existe-t-il ?** Le dépôt public porte une famille de segments nommés `5753_-1` à `5753_-7`
   (juin 2026), dont le nom dit qu'ils sont à une, deux, … sept spires de `20230702185753`. Un nom n'est
   pas une mesure : ce fichier vérifie, point par point, à quelle distance ils sont vraiment ;
2. **un décalage fixe suffit-il ?** Si la spire voisine est partout à 72 voxels, prédire suffit. Si
   l'écart varie, il faut recaler, et la dispersion mesurée ici dit dans quelle fenêtre chercher. La
   fenêtre prévue est de +36 à +108 voxels (un demi-feuillet de part et d'autre du pas) : ce fichier
   dit quelle part du témoin y tombe.

3. **le segment porte-t-il sa propre spire voisine ?** Un segment qui fait plus d'un tour se recouvre
   lui-même : en face de chacun de ses points, à un pas, il y a un autre de ses points, sur le tour
   d'avant ou d'après. C'est la vérité de terrain la plus propre qui soit pour un transfert : elle vient
   du même traceur, sur la même feuille, et elle n'exige aucun témoin tiers. Ce fichier la relève.

⚠⚠ LA MESURE EST SIGNÉE, ET C'EST CE QUI LA REND DISCRIMINANTE. La distance d'un point du segment au
témoin est projetée sur la normale du SEGMENT (orientée par sa grille, donc la même partout), pas prise
en valeur absolue. Une spire voisine donne un écart d'un seul signe ; deux spires, le double, du même
signe ; le même segment retracé, zéro. Une distance non signée ne distinguerait pas une spire vers
l'intérieur d'une spire vers l'extérieur, et rendrait « un pas » pour les deux.

⚠⚠ UN POINT N'EST COMPARÉ QUE S'IL A LE TÉMOIN EN FACE. Le point du témoin le plus proche d'un point
du segment n'est son pied sur la normale que si les deux surfaces se recouvrent là. Hors du recouvrement,
le plus proche est au bord du témoin, loin sur le côté. Le critère est DÉRIVÉ, pas choisi : l'écart
latéral doit rester sous l'espacement de la grille du témoin (1 / scale, 20 voxels à 2,4 µm). Deux
surfaces parallèles échantillonnées à ce pas ont toujours un point à moins d'une maille du pied.

Usage :
    uv run python src/nappe/la_spire_voisine_est_elle_a_un_pas.py --verifier
    uv run python src/nappe/la_spire_voisine_est_elle_a_un_pas.py \\
        --json docs/mesures/la_spire_voisine_est_elle_a_un_pas.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "tracecheck"))

from que_montrent_ces_deux_vues import DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS  # noqa: E402
from tracecheck import get_with_reason  # noqa: E402
from zarr_depth import BUCKET  # noqa: E402

LE_SEGMENT = "20230702185753"
LE_VOLUME = "20260411134726-2.4um"
# ⚠ Ce que le NOM de chaque témoin annonce, en spires depuis le segment. C'est l'hypothèse testée,
# jamais une donnée d'entrée du calcul : la mesure ne lit ce nombre que pour le comparer.
LES_TEMOINS = {
    "20260602230115-20230702185753_v14": 0,
    "20260602225659-5753_0": 0,
    "20260603005223-5753_-1": 1,
    "20260603024952-5753_-2": 2,
}
LE_CACHE = RACINE / "data" / "spire_voisine"
# La maille du segment où l'on compare : un point sur huit de la grille, soit un tous les 160 voxels.
# Ce n'est pas un seuil, c'est un sous-échantillonnage ; il est publié avec le nombre de points lus.
LA_MAILLE = 8
LA_FENETRE = (PAS_EN_VOXELS - DEMI_PAS_EN_VOXELS, PAS_EN_VOXELS + DEMI_PAS_EN_VOXELS)
DELAI = 120.0


def la_cle_du_maillage(segment: str) -> str:
    horodatage = segment.split("-")[0]
    return f"PHercParis4/segments/{segment}/mesh/{horodatage}-on-{LE_VOLUME}.tifxyz"


def telecharger(segment: str, cache: Path = LE_CACHE, delai: float = DELAI) -> Path | str:
    """Le dossier tifxyz local du segment ; une chaîne qui nomme la cause si un fichier manque."""
    dossier = cache / segment
    dossier.mkdir(parents=True, exist_ok=True)
    for nom in ("meta.json", "x.tif", "y.tif", "z.tif"):
        cible = dossier / nom
        if cible.exists() and cible.stat().st_size > 0:
            continue
        corps, raison = get_with_reason(f"{BUCKET}/{la_cle_du_maillage(segment)}/{nom}", delai)
        if corps is None:
            return f"{segment}/{nom} : {raison}"
        tmp = cible.with_suffix(cible.suffix + ".tmp")
        tmp.write_bytes(corps)
        tmp.replace(cible)
    return dossier


def lire_tifxyz(dossier: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Les points (h, w, 3), leur validité, et l'espacement de la grille en voxels (1 / scale)."""
    import tifffile

    x, y, z = (tifffile.imread(dossier / f"{c}.tif").astype(np.float64) for c in "xyz")
    points = np.stack([x, y, z], axis=-1)
    valide = np.isfinite(points).all(axis=-1) & (x != -1.0) & (y != -1.0) & (z != -1.0)
    meta = json.loads((dossier / "meta.json").read_text())
    return points, valide, 1.0 / float(meta["scale"][0])


def les_normales(points: np.ndarray, valide: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La normale unitaire de chaque point intérieur, par différences centrées sur la grille.

    L'orientation est celle de la grille (du × dv), donc la même sur toute la surface : c'est elle qui
    rend un écart signé comparable d'un point à l'autre.
    """
    n = np.zeros_like(points)
    ok = np.zeros(valide.shape, dtype=bool)
    du = points[1:-1, 2:] - points[1:-1, :-2]
    dv = points[2:, 1:-1] - points[:-2, 1:-1]
    c = np.cross(du, dv)
    norme = np.linalg.norm(c, axis=-1)
    interieur = (valide[1:-1, 1:-1] & valide[1:-1, 2:] & valide[1:-1, :-2] & valide[2:, 1:-1]
                 & valide[:-2, 1:-1] & (norme > 0))
    n[1:-1, 1:-1][interieur] = c[interieur] / norme[interieur][:, None]
    ok[1:-1, 1:-1] = interieur
    return n, ok


def comparer(ref: np.ndarray, ref_valide: np.ndarray, temoin: np.ndarray, temoin_valide: np.ndarray,
             espacement: float, maille: int = LA_MAILLE) -> dict:
    """L'écart signé du témoin au segment, le long de la normale du segment, là où il lui fait face."""
    from scipy.spatial import cKDTree

    normales, ok = les_normales(ref, ref_valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    lus = ok & grille
    p, n = ref[lus], normales[lus]
    nuage = temoin[temoin_valide]
    if len(p) == 0 or len(nuage) == 0:
        return {"decidable": False, "la_raison": "aucun point comparable"}
    _, idx = cKDTree(nuage).query(p)
    delta = nuage[idx] - p
    t = np.einsum("ij,ij->i", delta, n)
    lateral = np.linalg.norm(delta - t[:, None] * n, axis=-1)
    en_face = lateral <= espacement
    carte = np.full(ok.shape, np.nan)[::maille, ::maille]
    ii, jj = np.nonzero(lus)
    carte[ii // maille, jj // maille] = np.where(en_face, t, np.nan)
    if not en_face.any():
        return {"decidable": False, "la_raison": "le témoin ne fait face au segment nulle part",
                "les_points_lus": int(len(p)), "la_carte": carte}
    te = t[en_face]
    q = np.percentile(te, [5, 25, 50, 75, 95])
    lo, hi = LA_FENETRE
    return {
        "decidable": True,
        "les_points_lus": int(len(p)),
        "les_points_en_face": int(en_face.sum()),
        "le_recouvrement": round(float(en_face.mean()), 4),
        "lecart_median_voxels": round(float(q[2]), 4),
        "lecart_median_en_pas": round(float(q[2] / PAS_EN_VOXELS), 4),
        "les_quantiles_voxels": {k: round(float(v), 4) for k, v in zip(("q05", "q25", "q50", "q75", "q95"), q)},
        "la_part_du_meme_signe": round(float(max((te > 0).mean(), (te < 0).mean())), 4),
        "la_part_dans_la_fenetre": round(float(((np.abs(te) >= lo) & (np.abs(te) <= hi)).mean()), 4),
        "la_part_sous_le_demi_feuillet": round(float((np.abs(te) < DEMI_PAS_EN_VOXELS).mean()), 4),
        "la_carte": carte,
    }


def les_couches_du_segment(ref: np.ndarray, valide: np.ndarray, espacement: float,
                           maille: int = LA_MAILLE, pas_du_nuage: int = 2,
                           rayon: float = 3.5 * PAS_EN_VOXELS, temoins=()) -> dict:
    """Les autres couches tracées en face de chacun des points du segment, de chaque côté.

    Sans `temoins`, seulement celles du segment lui-même. Avec, celles des segments témoins aussi : un
    tour que le segment n'a pas tracé peut l'avoir été par un autre, et sans lui la couche la plus proche
    serait le tour d'après. ⚠ Un point témoin à moins d'un demi-feuillet est sur la MÊME feuille que le
    segment (un retracé), jamais une couche voisine : il est écarté par cette borne, qui est celle de la
    chaîne, et non par une distance sur une surface qui n'est pas la sienne.

    ⚠⚠ UNE COUCHE N'EST PAS LE MORCEAU DE FEUILLE AUTOUR DU POINT. Tout point du voisinage immédiat est
    à moins de `rayon` en 3D ; il est aussi à moins de `rayon / espacement` mailles sur la grille. Un
    point n'est donc une autre couche que s'il est plus loin que cela SUR LA SURFACE (distance L1 en
    mailles, bornée par √2 fois la distance euclidienne) tout en étant en face. Les deux bornes sont
    dérivées du rayon et de l'espacement, aucune n'est choisie. Le rayon lui-même est trois pas et demi :
    assez pour voir trois tours, et pas davantage.
    """
    from scipy.spatial import cKDTree

    normales, ok = les_normales(ref, valide)
    grille = np.zeros_like(ok)
    grille[::maille, ::maille] = True
    ii, jj = np.nonzero(ok & grille)
    p, n = ref[ii, jj], normales[ii, jj]
    ni, nj = np.nonzero(valide[::pas_du_nuage, ::pas_du_nuage])
    ni, nj = ni * pas_du_nuage, nj * pas_du_nuage
    nuage = ref[ni, nj]
    temoin = np.zeros(len(nuage), dtype=bool)
    for pts, val in temoins:
        ti, tj = np.nonzero(val[::pas_du_nuage, ::pas_du_nuage])
        nuage = np.concatenate([nuage, pts[ti * pas_du_nuage, tj * pas_du_nuage]])
        ni = np.concatenate([ni, np.full(len(ti), -10 ** 9)])
        nj = np.concatenate([nj, np.full(len(ti), -10 ** 9)])
        temoin = np.concatenate([temoin, np.ones(len(ti), dtype=bool)])
    lateral_max = espacement * pas_du_nuage
    loin_min = int(np.ceil(rayon * np.sqrt(2.0) / espacement)) + 1
    plus = np.full(len(p), np.nan)
    moins = np.full(len(p), np.nan)
    arbre = cKDTree(nuage)
    for k, lst in enumerate(arbre.query_ball_point(p, r=rayon)):
        if not lst:
            continue
        lst = np.asarray(lst)
        d = nuage[lst] - p[k]
        t = d @ n[k]
        lat = np.linalg.norm(d - t[:, None] * n[k], axis=1)
        loin = np.where(temoin[lst], np.abs(t) >= DEMI_PAS_EN_VOXELS,
                        (np.abs(ni[lst] - ii[k]) + np.abs(nj[lst] - jj[k])) > loin_min)
        garde = (lat <= lateral_max) & loin
        tp, tm = t[garde & (t > 0)], t[garde & (t < 0)]
        if len(tp):
            plus[k] = tp.min()
        if len(tm):
            moins[k] = tm.max()
    lo, hi = LA_FENETRE

    def cote(v):
        f = v[np.isfinite(v)]
        if not len(f):
            return {"la_part_des_points": 0.0}
        a = np.abs(f)
        return {"la_part_des_points": round(float(len(f) / len(v)), 4),
                "lecart_median_voxels": round(float(np.median(a)), 4),
                "lecart_median_en_pas": round(float(np.median(a) / PAS_EN_VOXELS), 4),
                "les_quantiles_voxels": {k: round(float(x), 4) for k, x in
                                         zip(("q05", "q25", "q50", "q75", "q95"), np.percentile(a, [5, 25, 50, 75, 95]))},
                "la_part_dans_la_fenetre": round(float(((a >= lo) & (a <= hi)).mean()), 4)}

    cartes = {}
    for nom, v in (("plus", plus), ("moins", moins)):
        c = np.full(ok.shape, np.nan)[::maille, ::maille]
        c[ii // maille, jj // maille] = v
        cartes[nom] = c
    return {"decidable": bool(len(p)), "les_points_lus": int(len(p)), "le_rayon_voxels": round(rayon, 4),
            "lecart_lateral_max": lateral_max, "la_distance_sur_la_surface_min_mailles": loin_min,
            "la_part_avec_une_couche": round(float((np.isfinite(plus) | np.isfinite(moins)).mean()), 4)
            if len(p) else 0.0,
            "du_cote_plus": cote(plus), "du_cote_moins": cote(moins), "les_cartes": cartes}


def mesurer(cache: Path = LE_CACHE, delai: float = DELAI, maille: int = LA_MAILLE) -> dict:
    d = telecharger(LE_SEGMENT, cache, delai)
    if isinstance(d, str):
        return {"decidable": False, "la_raison": d}
    ref, ref_valide, esp_ref = lire_tifxyz(d)
    soi = les_couches_du_segment(ref, ref_valide, esp_ref, maille)
    for cote, carte in soi.pop("les_cartes").items():
        np.save(cache / f"carte_soi_{cote}.npy", carte)
    out = {"le_segment_lui_meme": soi, "le_segment": LE_SEGMENT, "le_volume": LE_VOLUME, "le_pas_en_voxels": round(PAS_EN_VOXELS, 4),
           "le_demi_feuillet": DEMI_PAS_EN_VOXELS, "la_fenetre_voxels": [round(v, 4) for v in LA_FENETRE],
           "la_maille": maille, "les_temoins": {}}
    for temoin, annonce in LES_TEMOINS.items():
        dt = telecharger(temoin, cache, delai)
        if isinstance(dt, str):
            out["les_temoins"][temoin] = {"decidable": False, "la_raison": dt, "le_nom_annonce": annonce}
            continue
        pts, val, esp = lire_tifxyz(dt)
        r = comparer(ref, ref_valide, pts, val, esp, maille)
        carte = r.pop("la_carte", None)
        if carte is not None:
            np.save(cache / f"carte_{temoin}.npy", carte)
        r.update({"le_nom_annonce": annonce, "lespacement_du_temoin": esp})
        if r.get("decidable"):
            r["le_nom_est_tenu"] = bool(round(abs(r["lecart_median_voxels"]) / PAS_EN_VOXELS) == annonce)
        out["les_temoins"][temoin] = r
    out["decidable"] = all(v.get("decidable") for v in out["les_temoins"].values())
    return out


def afficher(r: dict) -> None:
    if not r.get("les_temoins"):
        print(f"indécidable : {r.get('la_raison')}")
        return
    soi = r["le_segment_lui_meme"]
    print(f"le segment lui-même : {soi['la_part_avec_une_couche']:.3f} de ses points ont une autre couche en face")
    for cote in ("du_cote_plus", "du_cote_moins"):
        c = soi[cote]
        if "lecart_median_voxels" in c:
            print(f"  {cote:14s} part {c['la_part_des_points']:.3f}  médiane {c['lecart_median_voxels']:.2f} vx "
                  f"({c['lecart_median_en_pas']:.3f} pas)  q05..q95 {c['les_quantiles_voxels']['q05']:.1f}.."
                  f"{c['les_quantiles_voxels']['q95']:.1f}  fenêtre {c['la_part_dans_la_fenetre']:.3f}")
    print(f"segment {r['le_segment']}, pas {r['le_pas_en_voxels']} voxels, fenêtre {r['la_fenetre_voxels']}")
    for nom, t in r["les_temoins"].items():
        if not t.get("decidable"):
            print(f"  {nom:36s} indécidable : {t.get('la_raison')}")
            continue
        print(f"  {nom:36s} annonce {t['le_nom_annonce']}  médiane {t['lecart_median_voxels']:+9.2f} vx "
              f"({t['lecart_median_en_pas']:+.3f} pas)  q05..q95 {t['les_quantiles_voxels']['q05']:+.1f}"
              f"..{t['les_quantiles_voxels']['q95']:+.1f}  recouvrement {t['le_recouvrement']:.3f}  "
              f"même signe {t['la_part_du_meme_signe']:.3f}  fenêtre {t['la_part_dans_la_fenetre']:.3f}")


# ---------------------------------------------------------------------------------------------------
def _plan(h: int, w: int, esp: float, decalage: float, pente: float = 0.0) -> np.ndarray:
    """Une grille plane à `esp` voxels de maille, décalée de `decalage` le long de z."""
    j, i = np.meshgrid(np.arange(w) * esp, np.arange(h) * esp)
    return np.stack([j, i, decalage + pente * j], axis=-1).astype(np.float64)


def _cylindre(h: int, w: int, esp: float, rayon: float) -> np.ndarray:
    """Une grille sur un cylindre d'axe y : les colonnes font le tour, les rangées montent."""
    arc = np.arange(w) * esp / rayon
    j, i = np.meshgrid(arc, np.arange(h) * esp)
    return np.stack([rayon * np.cos(j), i, rayon * np.sin(j)], axis=-1)


def _spirale(tours: float, hauteur: int, esp: float, rayon0: float) -> tuple[np.ndarray, np.ndarray]:
    """Une feuille enroulée en spirale d'Archimède, au pas inter-feuilles, étirée le long de y.

    Les colonnes suivent la feuille à `esp` voxels d'arc, les rangées montent le long de l'axe : c'est la
    forme d'un segment qui fait plusieurs tours.
    """
    b = PAS_EN_VOXELS / (2 * np.pi)
    thetas = [0.0]
    while thetas[-1] < 2 * np.pi * tours:
        r = rayon0 + b * thetas[-1]
        thetas.append(thetas[-1] + esp / np.hypot(r, b))
    th = np.asarray(thetas)
    r = rayon0 + b * th
    j, i = np.meshgrid(th, np.arange(hauteur) * esp)
    rr = rayon0 + b * j
    pts = np.stack([rr * np.cos(j), i, rr * np.sin(j)], axis=-1)
    return pts, np.ones(pts.shape[:2], dtype=bool)


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        if not ok:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    esp = 20.0
    ref = _plan(60, 60, esp, 0.0)
    val = np.ones(ref.shape[:2], dtype=bool)
    # ⭐⭐⭐⭐ LA SPIRE VOISINE, À UN PAS : l'écart signé rend le pas, d'un seul signe.
    un = comparer(ref, val, _plan(60, 60, esp, PAS_EN_VOXELS), val, esp, 4)
    v("★★★★ un plan à un pas rend un pas", abs(un.get("lecart_median_voxels", float("nan")) - PAS_EN_VOXELS) < 1e-3,
      str(un.get("lecart_median_voxels")))
    v("★★★★ et d'un seul signe", un.get("la_part_du_meme_signe", float("nan")) == 1.0)
    v("★★★ il tombe tout entier dans la fenêtre", un.get("la_part_dans_la_fenetre", float("nan")) == 1.0)
    # ⚠⚠⚠ LE SIGNE : de l'autre côté, le même écart change de signe. Une distance non signée rendrait
    # « un pas » pour les deux, et ne saurait pas dire de quel côté est la spire voisine.
    moins = comparer(ref, val, _plan(60, 60, esp, -PAS_EN_VOXELS), val, esp, 4)
    v("★★★★ la spire de l'autre côté rend le même écart, de signe opposé",
      abs(moins.get("lecart_median_voxels", float("nan")) + PAS_EN_VOXELS) < 1e-3, str(moins.get("lecart_median_voxels")))
    deux = comparer(ref, val, _plan(60, 60, esp, 2 * PAS_EN_VOXELS), val, esp, 4)
    v("★★★ deux spires rendent deux pas, hors de la fenêtre",
      abs(deux.get("lecart_median_en_pas", float("nan")) - 2.0) < 1e-3 and deux.get("la_part_dans_la_fenetre", float("nan")) == 0.0)
    zero = comparer(ref, val, _plan(60, 60, esp, 0.0), val, esp, 4)
    v("★★★★ le même segment retracé rend zéro, sous le demi-feuillet",
      zero.get("lecart_median_voxels", float("nan")) == 0.0 and zero.get("la_part_sous_le_demi_feuillet", float("nan")) == 1.0)
    # ⭐⭐⭐ LA COURBURE : deux cylindres concentriques à un pas d'écart. Le pied n'est plus à l'aplomb
    # d'un point de grille, mais il reste à moins d'une maille, donc le point est en face.
    cyl = comparer(_cylindre(40, 120, esp, 3000.0), np.ones((40, 120), bool),
                   _cylindre(40, 130, esp, 3000.0 + PAS_EN_VOXELS), np.ones((40, 130), bool), esp, 4)
    v("★★★ sur deux feuilles courbes concentriques, l'écart reste d'un pas à un voxel près",
      abs(abs(cyl.get("lecart_median_voxels", float("nan"))) - PAS_EN_VOXELS) < 1.0, str(cyl.get("lecart_median_voxels")))
    # ⚠⚠ LE RECOUVREMENT : un témoin qui ne couvre que la moitié ne fait face qu'à la moitié, et l'autre
    # moitié n'est pas comptée comme un écart immense au bord du témoin.
    moitie = _plan(60, 30, esp, PAS_EN_VOXELS)
    demi = comparer(ref, val, moitie, np.ones((60, 30), bool), esp, 4)
    v("★★★★ un témoin qui couvre la moitié fait face à la moitié", 0.4 < demi.get("le_recouvrement", float("nan")) < 0.6,
      str(demi.get("le_recouvrement")))
    v("★★★★ et les points hors du recouvrement ne tirent pas la médiane",
      abs(demi.get("lecart_median_voxels", float("nan")) - PAS_EN_VOXELS) < 1e-3, str(demi.get("lecart_median_voxels")))
    # ⚠⚠ UN POINT INVALIDE (-1 dans le tifxyz) N'EST NI UN POINT NI UN VOISIN.
    trou = _plan(60, 60, esp, PAS_EN_VOXELS)
    trou[20:40, 20:40] = -1.0
    tv = np.ones((60, 60), bool)
    tv[20:40, 20:40] = False
    avec_trou = comparer(ref, val, trou, tv, esp, 4)
    v("★★★ un trou du témoin réduit le recouvrement sans fausser l'écart",
      avec_trou.get("le_recouvrement", float("nan")) < 1.0 and abs(avec_trou.get("lecart_median_voxels", float("nan")) - PAS_EN_VOXELS) < 1e-3)
    # ⚠ LA NORMALE NE DÉPEND QUE DU SEGMENT : retourner la grille du TÉMOIN ne change rien.
    retourne = comparer(ref, val, _plan(60, 60, esp, PAS_EN_VOXELS)[:, ::-1], val, esp, 4)
    v("★★★ retourner la grille du témoin ne change pas le signe",
      abs(retourne.get("lecart_median_voxels", float("nan")) - PAS_EN_VOXELS) < 1e-3)
    # ⚠⚠ UN TÉMOIN INCLINÉ : l'écart varie, et la mesure le rend variable au lieu de le lisser.
    incline = comparer(ref, val, _plan(60, 60, esp, PAS_EN_VOXELS, pente=0.02), val, esp, 4)
    v("★★★ un témoin incliné rend un écart qui varie, et le dit dans ses quantiles",
      (incline.get("les_quantiles_voxels") or {}).get("q95", float("nan")) - (incline.get("les_quantiles_voxels") or {}).get("q05", float("nan")) > 10.0,
      str(incline.get("les_quantiles_voxels")))

    # ⭐⭐⭐⭐ LE SEGMENT QUI FAIT PLUS D'UN TOUR PORTE SA PROPRE SPIRE VOISINE, à un pas, des deux côtés.
    spirale, sv = _spirale(2.6, 40, esp, 3000.0)
    soi = les_couches_du_segment(spirale, sv, esp, 4)
    v("★★★★ une spirale de deux tours et demi a une autre couche en face de la plupart de ses points",
      soi.get("la_part_avec_une_couche", 0.0) > 0.6, str(soi.get("la_part_avec_une_couche")))
    for cote in ("du_cote_plus", "du_cote_moins"):
        m = soi.get(cote, {}).get("lecart_median_voxels", float("nan"))
        v(f"★★★★ et cette couche est à un pas, {cote}", abs(m - PAS_EN_VOXELS) < 1.0, str(m))
    # ⚠⚠⚠ LE MORCEAU DE FEUILLE AUTOUR DU POINT N'EST PAS UNE COUCHE : un plan seul n'en a aucune.
    seul = les_couches_du_segment(ref, val, esp, 4)
    v("★★★★ un plan seul n'a aucune autre couche", seul.get("la_part_avec_une_couche", 1.0) == 0.0,
      str(seul.get("la_part_avec_une_couche")))
    # ⚠⚠ UN SEUL TOUR N'EN A PAS NON PLUS, même courbé : c'est la courbure qui piège un critère mal borné.
    un_tour, ut = _spirale(0.9, 40, esp, 3000.0)
    tour = les_couches_du_segment(un_tour, ut, esp, 4)
    v("★★★ un seul tour de spirale n'a aucune autre couche", tour.get("la_part_avec_une_couche", 1.0) == 0.0,
      str(tour.get("la_part_avec_une_couche")))

    # ⚠⚠⚠ UN TOUR QUE LE SEGMENT N'A PAS TRACÉ : sa couche la plus proche est alors le tour d'après, à deux
    # pas. Un témoin qui trace le tour manquant ramène la couche à un pas ; un retracé du segment lui-même,
    # à zéro, n'est jamais pris pour une couche.
    trois, tv3 = _spirale(2.6, 40, esp, 3000.0)
    b = PAS_EN_VOXELS / (2 * np.pi)
    th = np.arctan2(trois[..., 2], trois[..., 0]) % (2 * np.pi)
    rr = np.hypot(trois[..., 0], trois[..., 2])
    tour = np.floor((rr - 3000.0 - b * th) / PAS_EN_VOXELS + 0.5)
    troue = tv3 & (tour != 1)
    sans = les_couches_du_segment(trois, troue, esp, 4)
    avec = les_couches_du_segment(trois, troue, esp, 4, temoins=[(trois, tv3 & (tour == 1)), (trois, tv3)])
    m_sans = sans.get("du_cote_plus", {}).get("lecart_median_voxels", float("nan"))
    m_avec = avec.get("du_cote_plus", {}).get("lecart_median_voxels", float("nan"))
    v("★★★★ sans le tour manquant, la couche la plus proche est à deux pas", abs(m_sans - 2 * PAS_EN_VOXELS) < 2.0, str(m_sans))
    v("★★★★ le témoin qui trace le tour manquant la ramène à un pas", abs(m_avec - PAS_EN_VOXELS) < 1.0, str(m_avec))
    rien = comparer(ref, val, _plan(60, 60, esp, 0.0) + 1e5, val, esp, 4)
    v("★★ un témoin qui ne fait face nulle part est indécidable, pas un écart", not rien.get("decidable", True))
    v("★★ la fenêtre est un demi-feuillet de part et d'autre du pas",
      abs(LA_FENETRE[1] - LA_FENETRE[0] - 2 * DEMI_PAS_EN_VOXELS) < 1e-9)
    v("★★ la clé du maillage est celle du dépôt public",
      la_cle_du_maillage("20260603005223-5753_-1")
      == "PHercParis4/segments/20260603005223-5753_-1/mesh/20260603005223-on-20260411134726-2.4um.tifxyz")

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
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(LE_CACHE, a.delai, a.maille)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
