"""La spire que le transfert produit porte-t-elle le texte que le segment porte, là où il repasse sur elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT APRÈS UNE PREMIÈRE MESURE, ET C'EST DIT. Le 28 septembre au soir, un prototype hors de ce dépôt a lu
l'encre de la spire produite de `20230702185753` sur six blocs de la rangée 176, colonnes 64 à 144, choisis À L'ŒIL parce que
la carte d'encre publiée y montre une ligne de lettres nette. Il a trouvé 0,96 entre notre lecture de la référence et la carte
publiée sur le bloc 176_144, puis, sur la spire produite, 0,89 là où le segment repasse à moins d'un demi-feuillet, 0,38
ailleurs, et 0,16 contre le texte de la spire de départ. Le demi-feuillet comme frontière a été choisi APRÈS avoir vu la couture
du champ de correspondance. Ce qui est vu avant d'écrire est donc toute la partie A.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. Le segment fait plus d'un tour (`247` §1, `R4-F411`) : en face de la plupart de ses points, un
tour plus loin, passe un autre de ses propres points. Là où ce point est à moins d'un demi-feuillet de la spire produite, c'est
la même feuille, et la carte d'encre publiée du segment dit, à cet endroit, le texte que la spire produite doit porter. C'est un
juge d'encre sans main, qui ne sait rien du transfert, et il tient là où le juge de `247` tient.

## Ce qui est fait

- Le modèle d'encre est celui qui a fait la carte publiée : `scrollprize/ink_canonical_2um`, par le code d'inférence de `villa`,
  en tuiles de 256 au pas de 128 (les réglages que porte le nom de la carte), sur les 62 couches 23 à 84 : placées autour de
  la surface (couche 54) comme la fenêtre 1 à 62 de l'équipe l'est autour de la couche 32 d'un volume de 65.
- Les piles sont celles que `275` a rendues pour ses tables de pas, sur les deux surfaces : rien n'est rendu à neuf.
- Pour chaque point du maillage de la spire produite, le vis-à-vis est le point du segment le plus proche en 3D parmi ceux à plus
  de 30 mailles de lui sur la surface. La carte publiée, réduite 8 fois, est lue au vis-à-vis ; notre lecture est réduite à la
  même échelle ; la mesure est la corrélation de Pearson sur les pixels communs.
- La lecture est d'abord étalonnée sur la référence : le bloc 176_144, lu par nous, contre la carte publiée au même endroit.

## Partie B, déclarée avant de lire la moindre encre sur ses blocs

- Les blocs sont les six blocs rendus, hors de la bande de la partie A, où la part des points de la spire produite dont le
  vis-à-vis est à moins d'un demi-feuillet est la plus grande. Ils sont choisis sur les seuls maillages (`--choisir`).
- Deux témoins, sur les mêmes pixels : la carte publiée sous le bloc lui-même (le texte de la spire de départ, que la spire
  produite ne doit pas recopier), et la carte au vis-à-vis décalé de 64 pixels de carte (1,2 mm, plus qu'une lettre).

## Les issues, pour la partie B, exclusives

- là où le segment repasse à moins d'un demi-feuillet, la corrélation dépasse ses deux témoins : la spire produite porte le
  texte du segment là où il repasse ;
- sinon : elle ne le porte pas ;
- indécidable si l'étalonnage ne tient pas (corrélation sous 0,8, seuil posé après avoir vu 0,96) ou si moins de 10 000 pixels de
  carte sont jugés.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : la spire produite là où le segment ne repasse pas ; les autres spires ; un autre rouleau ;
la lecture du texte, qu'aucune corrélation ne fait. Le modèle d'encre n'est pas le nôtre, et un modèle d'encre peut inventer des
formes : c'est ce que les deux témoins sont là pour attraper.

Usage :
    uv run python src/nappe/le_tour_produit_porte_t_il_le_texte_du_segment.py --verifier
    uv run python src/nappe/le_tour_produit_porte_t_il_le_texte_du_segment.py --choisir
    uv run --project src/xpu --with albumentations --with zarr --with tqdm --with numcodecs --with imagecodecs \\
        python src/nappe/le_tour_produit_porte_t_il_le_texte_du_segment.py --encre
    uv run python src/nappe/le_tour_produit_porte_t_il_le_texte_du_segment.py \\
        --json docs/mesures/le_tour_produit_porte_t_il_le_texte_du_segment.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
LE_DOSSIER = RACINE / "data" / "rendu_spire_voisine"
LES_SURFACES = ("le_segment_reduit", "la_spire_produite")   # la référence, la produite
LE_DOSSIER_ENCRE = RACINE / "data" / "encre_du_tour_voisin"
LE_PLAN = LE_DOSSIER_ENCRE / "plan.json"
LE_MODELE = RACINE / "data" / "models" / "ink_canonical_2um" / "r152_3ddec_v2_l5_epoch13.ckpt"
VILLA = RACINE / "data" / "repos" / "villa" / "ink-detection" / "optimized_inference"
LA_CARTE = LE_DOSSIER_ENCRE / "carte_publiee_ds8.jpg"
LA_CLE_DE_LA_CARTE = ("PHercParis4/segments/20230702185753/ink-detection/downsampled/PHercParis4-20230702185753-2.4um-0.22m-"
                      "78keV-volume-20260411134726-20260417190342-new_canon_autoresearch_recipe-tile256-stride128-ds8.jpg")

LE_CHUNK, LE_BLOC = 128, 16
LA_REDUCTION = 8                  # la carte publiée est réduite 8 fois : un chunk y fait 16 pixels
LA_BANDE = (176, 64, 6)           # partie A : rangée de blocs, première colonne, nombre de blocs
LE_BLOC_ETALON = (176, 144)
LES_COUCHES = (23, 85)            # 31 couches sous la surface (54), elle et 30 au-dessus, comme 1 à 62 autour de 32
LA_TUILE, LE_PAS_DE_TUILE = 256, 128
LOIN_SUR_LA_SURFACE = 30          # en mailles : un vis-à-vis plus proche serait la même feuille, un peu plus loin
LE_DEMI_FEUILLET = 36.0           # voxels
LE_DECALAGE = 64                  # pixels de carte, pour le second témoin
LES_BLOCS_B = 6
LE_SEUIL_DETALONNAGE = 0.8
LE_MINIMUM_DE_PIXELS = 10_000


# ── Les maillages et les vis-à-vis ─────────────────────────────────────────────────────────────────────────────────

def les_maillages():
    """La référence et la spire produite : points (h, w, 3), validité, espacement de la grille en pixels de rendu."""
    sys.path.insert(0, str(RACINE / "src" / "nappe"))
    from la_spire_voisine_est_elle_a_un_pas import lire_tifxyz

    ref, ref_ok, espacement = lire_tifxyz(LE_DOSSIER / LES_SURFACES[0] / "maillage")
    pro, pro_ok, _ = lire_tifxyz(LE_DOSSIER / LES_SURFACES[1] / "maillage")
    return ref, ref_ok, pro, pro_ok, espacement


def les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes, loin: float = LOIN_SUR_LA_SURFACE, k: int = 64):
    """Pour chaque point produit des `lignes` × `colonnes`, le point de référence le plus proche en 3D, pris à plus de `loin`
    mailles sur la surface ; son indice de ligne, de colonne, et son écart en voxels (NaN s'il n'y en a pas)."""
    from scipy.spatial import cKDTree

    ri, ci = np.nonzero(ref_ok)
    arbre = cKDTree(ref[ref_ok])
    fl = np.full((len(lignes), len(colonnes)), np.nan)
    fc, ecart = fl.copy(), fl.copy()
    for a, i in enumerate(lignes):
        for b, j in enumerate(colonnes):
            if not pro_ok[i, j]:
                continue
            d, idx = arbre.query(pro[i, j], k=min(k, len(ri)))
            loin_ = np.hypot(ri[idx] - i, ci[idx] - j) > loin
            if not loin_.any():
                continue
            m = int(np.argmax(loin_))
            fl[a, b], fc[a, b], ecart[a, b] = ri[idx[m]], ci[idx[m]], d[m]
    return fl, fc, ecart


def les_mailles_dune_bande(rangee: int, colonne: int, combien: int, espacement: float):
    """Les indices de maillage qui couvrent `combien` blocs à partir de (rangee, colonne), bords compris."""
    r0, r1 = rangee * LE_CHUNK / espacement, (rangee + LE_BLOC) * LE_CHUNK / espacement
    c0, c1 = colonne * LE_CHUNK / espacement, (colonne + LE_BLOC * combien) * LE_CHUNK / espacement
    return (np.arange(int(np.floor(r0)), int(np.ceil(r1)) + 1), np.arange(int(np.floor(c0)), int(np.ceil(c1)) + 1))


def la_part_proche(ecart: np.ndarray, demi: float = LE_DEMI_FEUILLET) -> float:
    """La part des points qui ont un vis-à-vis et dont il est à moins d'un demi-feuillet."""
    connu = np.isfinite(ecart)
    return float((ecart[connu] < demi).mean()) if connu.any() else 0.0


def les_blocs_de_la_partie_b(parts: dict, exclus: set, combien: int = LES_BLOCS_B) -> list[tuple[int, int]]:
    """Les `combien` blocs à la plus grande part proche, hors des exclus ; à égalité, dans l'ordre des blocs."""
    return [b for b, _ in sorted(((b, p) for b, p in parts.items() if b not in exclus),
                                 key=lambda t: (-t[1], t[0]))[:combien]]


def les_blocs_rendus() -> list[tuple[int, int]]:
    """Les blocs dont les deux piles sont complètes."""
    sys.path.insert(0, str(RACINE / "src" / "nappe"))
    from la_spire_produite_se_lit_elle_dans_le_treillis import la_pile_est_complete

    blocs = []
    for d in sorted((LE_DOSSIER / LES_SURFACES[0]).glob("bloc_*")):
        parts = d.name.split("_")
        if len(parts) != 3 or not d.is_dir():
            continue
        b = (int(parts[1]), int(parts[2]))
        if all(la_pile_est_complete(LE_DOSSIER / s / d.name) for s in LES_SURFACES):
            blocs.append(b)
    return sorted(blocs)


def choisir() -> dict:
    """La partie B, choisie sur les seuls maillages, avant toute lecture d'encre sur ses blocs."""
    ref, ref_ok, pro, pro_ok, esp = les_maillages()
    a_rangee, a_colonne, a_combien = LA_BANDE
    exclus = {(a_rangee, a_colonne + LE_BLOC * k) for k in range(a_combien)}
    parts = {}
    for b in les_blocs_rendus():
        lignes, colonnes = les_mailles_dune_bande(b[0], b[1], 1, esp)
        parts[b] = la_part_proche(les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes)[2])
    choisis = les_blocs_de_la_partie_b(parts, exclus)
    plan = {"les_blocs_de_la_partie_b": [list(b) for b in choisis],
            "leurs_parts_proches": [round(parts[b], 4) for b in choisis],
            "les_blocs_examines": len(parts), "la_part_proche_mediane": round(float(np.median(list(parts.values()))), 4),
            "la_regle": f"les {LES_BLOCS_B} plus grandes parts de points à moins de {LE_DEMI_FEUILLET:g} voxels de leur "
                        "vis-à-vis, hors de la bande de la partie A, sur les seuls maillages"}
    LE_DOSSIER_ENCRE.mkdir(parents=True, exist_ok=True)
    LE_PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    return plan


# ── L'encre ────────────────────────────────────────────────────────────────────────────────────────────────────────

def lencre(surface: str, rangee: int, colonne: int, combien: int, sortie: Path) -> dict:
    """Le modèle de l'équipe sur `combien` blocs de `surface` mis côte à côte, par le code d'inférence de `villa`."""
    import tifffile
    import torch
    import zarr

    sys.path.insert(0, str(VILLA))
    import inference as inf
    from model_resnet3d_3d_decoder import load_model

    z0, z1 = LES_COUCHES
    inf.CFG.in_chans, inf.CFG.tile_size, inf.CFG.size, inf.CFG.stride = z1 - z0, LA_TUILE, LA_TUILE, LE_PAS_DE_TUILE
    inf.CFG.batch_size, inf.CFG.workers = 4, 0
    inf.CFG.zarr_output_dir = str(sortie.parent / f"zarr_{sortie.stem}")
    appareil = torch.device("xpu" if hasattr(torch, "xpu") and torch.xpu.is_available() else "cpu")
    noms = [sorted((LE_DOSSIER / surface / f"bloc_{rangee}_{colonne + LE_BLOC * k}").glob("*.tif")) for k in range(combien)]
    couches = np.stack([np.concatenate([tifffile.imread(n[z]) for n in noms], axis=1) for z in range(z0, z1)], axis=-1)
    modele = load_model(str(LE_MODELE), appareil, num_frames=z1 - z0)
    t0 = time.monotonic()
    chemins = inf.run_inference(couches, modele, appareil)
    somme = zarr.open(chemins["mask_pred"], mode="r")[:]
    poids = zarr.open(chemins["mask_count"], mode="r")[:]
    encre = np.where(poids > 0, somme / np.maximum(poids, 1e-9), np.nan).astype(np.float32)
    np.save(sortie, encre)
    return {"surface": surface, "bloc": [rangee, colonne], "blocs": combien, "appareil": str(appareil),
            "les_secondes": round(time.monotonic() - t0, 1), "la_forme": list(encre.shape)}


def les_lectures(plan: dict) -> list[tuple[str, tuple[int, int, int], Path]]:
    """Ce que `--encre` lit : l'étalon sur la référence, la bande de la partie A et chaque bloc de la partie B, produits."""
    out = [(LES_SURFACES[0], (*LE_BLOC_ETALON, 1), LE_DOSSIER_ENCRE / "etalon_reference.npy"),
           (LES_SURFACES[1], LA_BANDE, LE_DOSSIER_ENCRE / "bande_produite.npy")]
    out += [(LES_SURFACES[1], (by, bx, 1), LE_DOSSIER_ENCRE / f"partie_b_produite_{by}_{bx}.npy")
            for by, bx in plan["les_blocs_de_la_partie_b"]]
    return out


# ── La mesure ──────────────────────────────────────────────────────────────────────────────────────────────────────

def reduire(a: np.ndarray, facteur: int = LA_REDUCTION) -> np.ndarray:
    """La moyenne par carré de `facteur` × `facteur`, les NaN écartés ; un reste de bord est laissé de côté."""
    h, w = a.shape[0] // facteur, a.shape[1] // facteur
    with np.errstate(invalid="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore", RuntimeWarning)
        return np.nanmean(a[:h * facteur, :w * facteur].reshape(h, facteur, w, facteur), axis=(1, 3))


def la_carte_publiee() -> np.ndarray:
    """La carte publiée, en niveaux de gris, téléchargée une fois."""
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    if not LA_CARTE.exists():
        sys.path.insert(0, str(RACINE / "src" / "tracecheck"))
        from tracecheck import BUCKET, get_with_reason

        corps, raison = get_with_reason(f"{BUCKET}/{LA_CLE_DE_LA_CARTE}", 120.0)
        if corps is None:
            raise RuntimeError(f"la carte publiée ne se télécharge pas : {raison}")
        LE_DOSSIER_ENCRE.mkdir(parents=True, exist_ok=True)
        LA_CARTE.write_bytes(corps)
    return np.asarray(Image.open(LA_CARTE).convert("L"), dtype=np.float32)


def la_carte_sous(carte: np.ndarray, rangee: int, colonne: int, combien: int) -> np.ndarray:
    """La carte publiée sous `combien` blocs, telle quelle."""
    p = LE_CHUNK * LE_BLOC // LA_REDUCTION
    y0, x0 = rangee * LE_CHUNK // LA_REDUCTION, colonne * LE_CHUNK // LA_REDUCTION
    return carte[y0:y0 + p, x0:x0 + p * combien]


def la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, rangee, colonne, combien, espacement, decalage: int = 0):
    """La carte publiée lue au vis-à-vis de chaque pixel de carte de la bande ; NaN là où il n'y en a pas."""
    from scipy.ndimage import map_coordinates

    p = LE_CHUNK * LE_BLOC // LA_REDUCTION
    py, px = np.mgrid[0:p, 0:p * combien].astype(float)
    mr = (rangee * LE_CHUNK + (py + 0.5) * LA_REDUCTION) / espacement - lignes[0]
    mc = (colonne * LE_CHUNK + (px + 0.5) * LA_REDUCTION) / espacement - colonnes[0]
    connu = np.isfinite(fl)
    r = map_coordinates(np.where(connu, fl, -1e6), [mr, mc], order=1)
    c = map_coordinates(np.where(connu, fc, -1e6), [mr, mc], order=1)
    ok = (r >= 0) & (c >= 0)
    par_maille = espacement / LA_REDUCTION
    lu = map_coordinates(carte, [r * par_maille, c * par_maille + decalage], order=1, cval=np.nan)
    lu[~ok] = np.nan
    return lu


def lecart_au_pixel(ecart, lignes, colonnes, rangee, colonne, combien, espacement) -> np.ndarray:
    """L'écart du vis-à-vis au plus proche point de maillage, pour chaque pixel de carte de la bande."""
    from scipy.ndimage import map_coordinates

    p = LE_CHUNK * LE_BLOC // LA_REDUCTION
    py, px = np.mgrid[0:p, 0:p * combien].astype(float)
    mr = (rangee * LE_CHUNK + (py + 0.5) * LA_REDUCTION) / espacement - lignes[0]
    mc = (colonne * LE_CHUNK + (px + 0.5) * LA_REDUCTION) / espacement - colonnes[0]
    return map_coordinates(np.where(np.isfinite(ecart), ecart, 1e6), [mr, mc], order=0)


def correlation(a: np.ndarray, b: np.ndarray, masque: np.ndarray | None = None,
                minimum: int = LE_MINIMUM_DE_PIXELS) -> tuple[float | None, int]:
    """La corrélation de Pearson sur les pixels où les deux sont connus (et le masque vrai) ; None sous `minimum` pixels."""
    ok = np.isfinite(a) & np.isfinite(b)
    if masque is not None:
        ok &= masque
    n = int(ok.sum())
    if n < minimum or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return None, n
    return round(float(np.corrcoef(a[ok], b[ok])[0, 1]), 4), n


def mesurer_une_bande(encre, carte, maillages, rangee, colonne, combien) -> dict:
    """Notre lecture de la spire produite contre la carte au vis-à-vis, et ses deux témoins, séparés par le demi-feuillet."""
    ref, ref_ok, pro, pro_ok, esp = maillages
    lignes, colonnes = les_mailles_dune_bande(rangee, colonne, combien, esp)
    fl, fc, ecart = les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes)
    petite = reduire(encre)
    au_vis_a_vis = la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, rangee, colonne, combien, esp)
    decale = la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, rangee, colonne, combien, esp, LE_DECALAGE)
    dessous = la_carte_sous(carte, rangee, colonne, combien)
    h, w = min(petite.shape[0], au_vis_a_vis.shape[0]), min(petite.shape[1], au_vis_a_vis.shape[1])
    petite, au_vis_a_vis, decale, dessous = (x[:h, :w] for x in (petite, au_vis_a_vis, decale, dessous))
    proche = lecart_au_pixel(ecart, lignes, colonnes, rangee, colonne, combien, esp)[:h, :w] < LE_DEMI_FEUILLET
    out = {"la_part_proche": round(la_part_proche(ecart), 4),
           "lecart_median_voxels": round(float(np.nanmedian(ecart)), 2) if np.isfinite(ecart).any() else None}
    for nom, masque in (("a_moins_dun_demi_feuillet", proche), ("au_dela", ~proche)):
        c, n = correlation(petite, au_vis_a_vis, masque)
        t1, _ = correlation(petite, dessous, masque)
        t2, _ = correlation(petite, decale, masque)
        out[nom] = {"les_pixels": n, "au_vis_a_vis": c, "temoin_sous_le_bloc": t1, "temoin_decale": t2}
    return out, (petite, au_vis_a_vis, proche)


def le_verdict(d: dict) -> dict:
    """L'issue déclarée, sur la partie B."""
    e = d.get("letalonnage", {}).get("la_correlation")
    b = d.get("la_partie_b", {}).get("reunie", {}).get("a_moins_dun_demi_feuillet", {})
    if e is None or e < LE_SEUIL_DETALONNAGE:
        return {"lissue": "indécidable : la lecture ne retrouve pas la carte publiée sur la référence", "decidable": False}
    c, t1, t2 = b.get("au_vis_a_vis"), b.get("temoin_sous_le_bloc"), b.get("temoin_decale")
    if c is None or t1 is None or t2 is None or b.get("les_pixels", 0) < LE_MINIMUM_DE_PIXELS:
        return {"lissue": "indécidable : trop peu de pixels jugés là où le segment repasse", "decidable": False}
    if c > t1 and c > t2:
        return {"lissue": "la spire produite porte le texte du segment là où il repasse", "decidable": True}
    return {"lissue": "la spire produite ne porte pas le texte du segment là où il repasse", "decidable": True}


def mesurer() -> dict:
    t0 = time.monotonic()
    plan = json.loads(LE_PLAN.read_text())
    carte = la_carte_publiee()
    maillages = les_maillages()
    etalon = reduire(np.load(LE_DOSSIER_ENCRE / "etalon_reference.npy"))
    publiee = la_carte_sous(carte, *LE_BLOC_ETALON, 1)[:etalon.shape[0], :etalon.shape[1]]
    c, n = correlation(etalon, publiee)
    d = {"letalonnage": {"le_bloc": list(LE_BLOC_ETALON), "la_correlation": c, "les_pixels": n}}
    LE_DOSSIER_ENCRE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(LE_DOSSIER_ENCRE / "etalon_pour_la_figure.npz", lue=etalon, publiee=publiee)
    a, (petite, au_vis_a_vis, proche) = mesurer_une_bande(np.load(LE_DOSSIER_ENCRE / "bande_produite.npy"), carte, maillages,
                                                          *LA_BANDE)
    d["la_partie_a"] = {"la_bande": list(LA_BANDE), **a}
    np.savez_compressed(LE_DOSSIER_ENCRE / "partie_a_pour_la_figure.npz", lue=petite, au_vis_a_vis=au_vis_a_vis,
                        proche=proche)
    blocs, reunis = [], {k: [] for k in ("petite", "vis", "dessous", "decale", "proche")}
    ref, ref_ok, pro, pro_ok, esp = maillages
    for by, bx in plan["les_blocs_de_la_partie_b"]:
        encre = np.load(LE_DOSSIER_ENCRE / f"partie_b_produite_{by}_{bx}.npy")
        m, _ = mesurer_une_bande(encre, carte, maillages, by, bx, 1)
        blocs.append({"le_bloc": [by, bx], **m})
        lignes, colonnes = les_mailles_dune_bande(by, bx, 1, esp)
        fl, fc, ecart = les_vis_a_vis(ref, ref_ok, pro, pro_ok, lignes, colonnes)
        p = reduire(encre)
        v_ = la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, by, bx, 1, esp)
        dc = la_carte_au_vis_a_vis(carte, fl, fc, lignes, colonnes, by, bx, 1, esp, LE_DECALAGE)
        ds = la_carte_sous(carte, by, bx, 1)
        pr = lecart_au_pixel(ecart, lignes, colonnes, by, bx, 1, esp) < LE_DEMI_FEUILLET
        h, w = min(p.shape[0], v_.shape[0]), min(p.shape[1], v_.shape[1])
        for k, x in (("petite", p), ("vis", v_), ("dessous", ds), ("decale", dc), ("proche", pr)):
            reunis[k].append(x[:h, :w].ravel())
    r = {k: np.concatenate(x) for k, x in reunis.items()}
    reunie = {}
    for nom, masque in (("a_moins_dun_demi_feuillet", r["proche"]), ("au_dela", ~r["proche"])):
        c, n = correlation(r["petite"], r["vis"], masque)
        reunie[nom] = {"les_pixels": n, "au_vis_a_vis": c, "temoin_sous_le_bloc": correlation(r["petite"], r["dessous"],
                                                                                               masque)[0],
                       "temoin_decale": correlation(r["petite"], r["decale"], masque)[0]}
    d["la_partie_b"] = {"le_plan": plan, "les_blocs": blocs, "reunie": reunie}
    d["le_verdict"] = le_verdict(d)
    d["decidable"] = d["le_verdict"]["decidable"]
    d["le_modele"] = {"nom": "scrollprize/ink_canonical_2um", "sha256": hashlib.sha256(LE_MODELE.read_bytes()).hexdigest(),
                      "les_couches": list(LES_COUCHES), "la_tuile": LA_TUILE, "le_pas": LE_PAS_DE_TUILE}
    d["les_constantes"] = {"loin_sur_la_surface_mailles": LOIN_SUR_LA_SURFACE, "le_demi_feuillet_voxels": LE_DEMI_FEUILLET,
                           "le_decalage_pixels_de_carte": LE_DECALAGE, "la_reduction": LA_REDUCTION}
    d["les_secondes"] = round(time.monotonic() - t0, 1)
    return d


# ── La batterie ────────────────────────────────────────────────────────────────────────────────────────────────────

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

    # Un segment qui fait deux tours : deux nappes planes, à 73 voxels l'une de l'autre, portées par des colonnes éloignées.
    h, w = 10, 80
    ref = np.zeros((h, w, 3))
    ref_ok = np.zeros((h, w), dtype=bool)
    for i in range(h):
        for j in range(20):
            ref[i, j] = (j * 20.0, i * 20.0, 0.0)
            ref[i, j + 50] = (j * 20.0, i * 20.0, 73.0)
    ref_ok[:, :20] = True
    ref_ok[:, 50:70] = True
    pro = ref.copy()
    pro[..., 2] += 73.0
    pro_ok = ref_ok.copy()
    pro_ok[:, 50:] = False
    fl, fc, ecart = les_vis_a_vis(ref, ref_ok, pro, pro_ok, range(h), range(20), loin=30)
    v("★★★★ le vis-à-vis de la spire produite est le second tour du segment, à écart nul",
      np.nanmax(ecart) < 1e-9 and np.all(fc == np.arange(20)[None, :] + 50) and np.all(fl == np.arange(h)[:, None]),
      f"{np.nanmax(ecart)} {fc[0, :4]}")
    fl2, fc2, ecart2 = les_vis_a_vis(ref, ref_ok, pro, pro_ok, range(h), range(20), loin=1000)
    v("★★★★ sans point loin sur la surface, il n'y a pas de vis-à-vis", np.isnan(ecart2).all())
    seul = ref_ok.copy()
    seul[:, 50:] = False
    _, _, e3 = les_vis_a_vis(ref, seul, pro, pro_ok, range(h), range(20), loin=3)
    v("★★★ la même feuille, prise plus loin, est à une feuille entière : hors du demi-feuillet",
      np.nanmin(e3) > LE_DEMI_FEUILLET, str(np.nanmin(e3)))
    rate = ref.copy()
    rate[..., 2] += 10.0
    _, fc4, e4 = les_vis_a_vis(ref, ref_ok, rate, pro_ok, range(h), range(20), loin=30)
    v("★★★★ un transfert raté, retombé près de sa propre feuille, n'est pas jugé contre elle : son vis-à-vis est l'autre tour",
      np.all(fc4 >= 50) and np.nanmin(e4) > LE_DEMI_FEUILLET, f"{fc4[0, :3]} {np.nanmin(e4)}")
    v("★★★ la part proche compte les points à moins d'un demi-feuillet, parmi ceux qui ont un vis-à-vis",
      la_part_proche(np.array([1.0, 50.0, np.nan, 10.0])) == 2 / 3)
    parts = {(16, 0): 0.2, (16, 16): 0.9, (32, 0): 0.9, (32, 16): 0.5, (48, 0): 0.95}
    v("★★★★ la partie B : les plus grandes parts, hors des exclus, à égalité dans l'ordre des blocs",
      les_blocs_de_la_partie_b(parts, {(48, 0)}, 3) == [(16, 16), (32, 0), (32, 16)])
    x = np.arange(64, dtype=float).reshape(8, 8)
    v("★★★ la réduction est une moyenne par carré", np.allclose(reduire(x, 4), [[13.5, 17.5], [45.5, 49.5]]))
    y = x.copy()
    y[0, 0] = np.nan
    v("★★ la réduction écarte les NaN", np.isclose(reduire(y, 4)[0, 0], (13.5 * 16 - 0) / 15))
    a_ = np.random.default_rng(0).random((200, 200))
    v("★★★★ deux cartes égales sont corrélées à 1", correlation(a_, a_)[0] == 1.0)
    v("★★★ sous le minimum de pixels, la corrélation n'est pas rendue", correlation(a_[:10, :10], a_[:10, :10])[0] is None)
    v("★★★ un masque restreint les pixels comptés", correlation(a_, a_, a_ > 0.5, minimum=1)[1] == int((a_ > 0.5).sum()))
    esp = 160.0
    lignes, colonnes = les_mailles_dune_bande(176, 64, 2, esp)
    v("★★★★ les mailles d'une bande couvrent ses pixels de rendu, bords compris",
      lignes[0] * esp <= 176 * 128 and lignes[-1] * esp >= 192 * 128 and colonnes[0] * esp <= 64 * 128
      and colonnes[-1] * esp >= 96 * 128, f"{lignes[[0, -1]]} {colonnes[[0, -1]]}")
    carte = np.add.outer(np.arange(6400.0), np.arange(4600.0) * 0.001)
    gl, gc = np.meshgrid(lignes.astype(float), colonnes.astype(float), indexing="ij")
    lu = la_carte_au_vis_a_vis(carte, gl, gc, lignes, colonnes, 176, 64, 2, esp)
    sous = la_carte_sous(carte, 176, 64, 2)
    v("★★★★ un vis-à-vis qui est le point lui-même relit la carte sous la bande",
      lu.shape == sous.shape and np.nanmax(np.abs(lu - sous)) < 0.51, f"{lu.shape} {sous.shape} {np.nanmax(np.abs(lu - sous))}")
    dec = la_carte_au_vis_a_vis(carte, gl, gc, lignes, colonnes, 176, 64, 2, esp, LE_DECALAGE)
    v("★★★ le témoin décalé lit la carte 64 pixels plus loin en colonne",
      np.nanmax(np.abs((dec - lu) - LE_DECALAGE * 0.001)) < 1e-6)
    v("★★★ la carte sous un bloc fait 256 pixels de côté", la_carte_sous(carte, 176, 144, 1).shape == (256, 256))
    v("★★ la fenêtre de couches est celle de l'équipe, 1 à 62 autour de la couche 32, portée autour de la couche 54",
      LES_COUCHES == (54 - (32 - 1), 54 + (63 - 32)))
    ok_ = {"letalonnage": {"la_correlation": 0.95}, "la_partie_b": {"reunie": {"a_moins_dun_demi_feuillet": {
        "les_pixels": 20000, "au_vis_a_vis": 0.8, "temoin_sous_le_bloc": 0.1, "temoin_decale": 0.3}}}}
    non = json.loads(json.dumps(ok_))
    non["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"]["temoin_decale"] = 0.85
    mal = json.loads(json.dumps(ok_))
    mal["letalonnage"]["la_correlation"] = 0.5
    peu = json.loads(json.dumps(ok_))
    peu["la_partie_b"]["reunie"]["a_moins_dun_demi_feuillet"]["les_pixels"] = 100
    v("★★★★ les issues : porte, ne porte pas si un témoin l'égale, indécidable sans étalon ou sans pixels",
      le_verdict(ok_)["lissue"].endswith("porte le texte du segment là où il repasse")
      and "ne porte pas" in le_verdict(non)["lissue"] and "indécidable" in le_verdict(mal)["lissue"]
      and "indécidable" in le_verdict(peu)["lissue"])
    lec = les_lectures({"les_blocs_de_la_partie_b": [[32, 48]]})
    v("★★★ --encre lit l'étalon sur la référence, puis la bande et la partie B sur la spire produite",
      [s for s, _, _ in lec] == [LES_SURFACES[0], LES_SURFACES[1], LES_SURFACES[1]] and lec[2][1] == (32, 48, 1))

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--choisir", action="store_true", help="la partie B, sur les seuls maillages")
    p.add_argument("--encre", action="store_true", help="le modèle de l'équipe sur l'étalon, la bande et la partie B")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.choisir:
        print(json.dumps(choisir(), ensure_ascii=False, indent=1))
        return 0
    if a.encre:
        os.environ.setdefault("PYTORCH_ENABLE_XPU_FALLBACK", "0")
        for surface, (r, c, n), sortie in les_lectures(json.loads(LE_PLAN.read_text())):
            if sortie.exists():
                print(f"déjà lu : {sortie.name}", flush=True)
                continue
            print(json.dumps(lencre(surface, r, c, n, sortie), ensure_ascii=False), flush=True)
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
