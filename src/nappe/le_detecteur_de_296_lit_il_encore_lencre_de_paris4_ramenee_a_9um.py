"""Le détecteur d'encre de 296 lit-il encore l'encre de PHercParis4 quand son bloc étalon est ramené à 9,6 µm ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QUE LE DÉTECTEUR NE SOIT LU À UNE AUTRE RÉSOLUTION QUE 2,4 µm. Ce qui était vu avant d'écrire : tout ce
que `296` à `407` publient, dont **`R4-F477`** (`296` : sur le bloc étalon 176_144 du segment `20230702185753`, la lecture du détecteur
`ink_canonical_2um` s'accorde à 0,9593 avec la carte d'encre publiée), les faits **`R1-F18`** à **`R1-F20`** (le TimeSformer de 2023,
lisible à 3,24 µm, ne l'est pas établi à 6,48 ni 9,72 µm) et la règle de `58` : on réduit une résolution par moyenne de bloc, jamais par
décimation. Le détecteur de `296` n'a jamais été lu à une résolution plus grossière.

⭐⭐⭐⭐⭐ POURQUOI CETTE TRANCHE. C'est le premier pas de **`R4-P151`**, l'encre des surfaces que le critère tient sur PHerc0358, le
rouleau sans tracé humain : l'encre est le seul témoin indépendant du compte des feuilles qu'un tel rouleau offre. Mais PHerc0358 n'est
scanné qu'à 9,362 µm, et le détecteur est étalonné à 2,4 µm. S'il ne voit plus l'encre de PHercParis4 une fois ramenée à cette
résolution, sa lecture de PHerc0358 ne prouvera rien, et il faut le savoir avant de lire PHerc0358.

## Ce qui est fait

- **Le bloc étalon** de `296`, `le_segment_reduit/bloc_176_144` : 109 couches de 2048 × 2048 à 2,4 µm, la surface à la couche 54.
- **Le ramener à 9,6 µm** : la moyenne de chaque bloc de 4 × 4 × 4 voxels, 9,6 µm, un peu plus grossier que les 9,362 µm de PHerc0358.
  Puis le rééchantillonner, trilinéairement, sur la grille de 2,4 µm, pour que le détecteur reçoive l'entrée qu'il attend. C'est le chemin
  qu'une lecture de PHerc0358 prendrait.
- **Le détecteur**, tel que `296` le lit : `ink_canonical_2um`, les couches 23 à 84, des tuiles de 256 au pas de 128, sur l'iGPU. Jamais
  sur le processeur : sans iGPU, la tranche s'arrête.
- **La comparaison**, celle de l'étalonnage de `296` : la lecture réduite 8 fois contre la carte d'encre publiée sous le bloc, en
  corrélation de Pearson. **Le témoin** : la même lecture contre la carte décalée de 64 pixels de carte.
- **Le contrôle**, sans relancer le modèle : la lecture de `296` à 2,4 µm, gardée sur le disque, redonne 0,9593.
- **La règle** : à 9,6 µm, une corrélation d'au moins 0,8 (le seuil d'étalonnage de `296`) et plus haute que le témoin, **oui, le
  détecteur lit** ; sous 0,5, ou pas plus haute que le témoin, **non** ; sinon, **en partie**. Indécidable si le contrôle ne redonne pas
  0,9593.

## Les issues

L'issue de la tranche : **à 9,6 µm, corrélation c contre t pour le témoin ; à 2,4 µm, 0,9593**, puis ce que dit la règle.

## Rapporté à côté, qui ne décide rien

La même lecture à 4,8 µm (moyenne de 2 × 2 × 2) ; le temps de chaque lecture. ⚠ Ajoutée après la lecture à 9,6 µm, pour préparer la
lecture de PHerc0358, dont les normales n'ont pas d'orientation connue : la lecture à 9,6 µm les couches dans l'ordre inverse.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une moyenne de bloc n'est pas la réponse d'un scanner à 9,362 µm, et l'énergie de PHerc0358
(113 keV) n'est pas celle de PHercParis4 (78 keV) ; un seul bloc ; rien sur l'encre de PHerc0358.

Usage :
    uv run python src/nappe/le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.py --verifier
    uv run --project src/xpu --with albumentations --with zarr --with tqdm --with numcodecs --with imagecodecs \\
        python src/nappe/le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.py --encre
    uv run python src/nappe/le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.py \\
        --json docs/mesures/le_detecteur_de_296_lit_il_encore_lencre_de_paris4_ramenee_a_9um.json
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

import le_tour_produit_porte_t_il_le_texte_du_segment as m296  # noqa: E402

LE_BLOC = m296.LE_DOSSIER / m296.LES_SURFACES[0] / f"bloc_{m296.LE_BLOC_ETALON[0]}_{m296.LE_BLOC_ETALON[1]}"
LE_DOSSIER = RACINE / "data" / "encre_a_9um"
LES_FACTEURS = (4, 2)
LE_FACTEUR_QUI_DECIDE = 4
LE_CONTROLE = 0.9593
LE_SEUIL, LE_PLANCHER = m296.LE_SEUIL_DETALONNAGE, 0.5


def reduire_le_volume(couches: np.ndarray, f: int) -> np.ndarray:
    """La moyenne de chaque bloc de `f` × `f` × `f` voxels d'un volume (z, y, x) ; un bloc de bord incomplet est moyenné sur ce qu'il a."""
    z, y, x = couches.shape
    zp, yp, xp = -(-z // f) * f, -(-y // f) * f, -(-x // f) * f
    v = np.full((zp, yp, xp), np.nan, np.float32)
    v[:z, :y, :x] = couches
    with np.errstate(invalid="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore", RuntimeWarning)
        return np.nanmean(v.reshape(zp // f, f, yp // f, f, xp // f, f), axis=(1, 3, 5))


def les_coordonnees(n: int, f: int, depuis: int = 0, jusqua: int | None = None) -> np.ndarray:
    """Pour les voxels fins `depuis` à `jusqua`, leur place dans la grille grossière, centres alignés."""
    return (np.arange(depuis, n if jusqua is None else jusqua) + 0.5) / f - 0.5


def reechantillonner(grossier: np.ndarray, forme: tuple[int, int, int], f: int, z0: int, z1: int) -> np.ndarray:
    """Le volume grossier ramené, trilinéairement, sur la grille fine, pour les couches `z0` à `z1` ; en (y, x, couche), uint8."""
    from scipy.ndimage import map_coordinates

    zz = les_coordonnees(forme[0], f, z0, z1)
    yy, xx = les_coordonnees(forme[1], f), les_coordonnees(forme[2], f)
    out = np.empty((forme[1], forme[2], z1 - z0), np.uint8)
    gy, gx = np.meshgrid(yy, xx, indexing="ij")
    for k, z in enumerate(zz):
        v = map_coordinates(grossier, [np.full_like(gy, z), gy, gx], order=1, mode="nearest")
        out[..., k] = np.clip(np.rint(v), 0, 255).astype(np.uint8)
    return out


def le_bloc_ramene(f: int) -> np.ndarray:
    """Le bloc étalon ramené à `f` fois 2,4 µm puis rééchantillonné sur 2,4 µm, pour les couches que lit le détecteur."""
    import tifffile

    noms = sorted(LE_BLOC.glob("*.tif"))
    premiere = tifffile.imread(noms[0])
    grossier = np.concatenate([reduire_le_volume(np.stack([tifffile.imread(n) for n in noms[k:k + f]]).astype(np.float32), f)
                               for k in range(0, len(noms), f)])
    z0, z1 = m296.LES_COUCHES
    return reechantillonner(grossier, (len(noms), *premiere.shape), f, z0, z1)


def lencre(couches: np.ndarray, sortie: Path) -> dict:
    """Le détecteur de `296` sur une pile (y, x, couche), par le code d'inférence de `villa`, comme `m296.lencre` ; jamais sur le
    processeur."""
    import torch
    import zarr

    sys.path.insert(0, str(m296.VILLA))
    import inference as inf
    from model_resnet3d_3d_decoder import load_model

    if not (hasattr(torch, "xpu") and torch.xpu.is_available()):
        raise RuntimeError("pas d'iGPU : le détecteur ne tourne pas sur le processeur")
    z0, z1 = m296.LES_COUCHES
    inf.CFG.in_chans, inf.CFG.tile_size, inf.CFG.size, inf.CFG.stride = z1 - z0, m296.LA_TUILE, m296.LA_TUILE, m296.LE_PAS_DE_TUILE
    inf.CFG.batch_size, inf.CFG.workers = 4, 0
    inf.CFG.zarr_output_dir = str(sortie.parent / f"zarr_{sortie.stem}")
    appareil = torch.device("xpu")
    modele = load_model(str(m296.LE_MODELE), appareil, num_frames=z1 - z0)
    t0 = time.monotonic()
    chemins = inf.run_inference(couches, modele, appareil)
    somme = zarr.open(chemins["mask_pred"], mode="r")[:]
    poids = zarr.open(chemins["mask_count"], mode="r")[:]
    encre = np.where(poids > 0, somme / np.maximum(poids, 1e-9), np.nan).astype(np.float32)
    np.save(sortie, encre)
    return {"la_sortie": sortie.name, "appareil": str(appareil), "les_secondes": round(time.monotonic() - t0, 1),
            "la_forme": list(encre.shape)}


def la_carte_decalee(carte: np.ndarray, decalage: int = m296.LE_DECALAGE) -> np.ndarray:
    """La carte publiée sous le bloc étalon, décalée de `decalage` pixels de carte le long des colonnes."""
    p = m296.LE_CHUNK * m296.LE_BLOC // m296.LA_REDUCTION
    y0, x0 = m296.LE_BLOC_ETALON[0] * m296.LE_CHUNK // m296.LA_REDUCTION, m296.LE_BLOC_ETALON[1] * m296.LE_CHUNK // m296.LA_REDUCTION
    return carte[y0:y0 + p, x0 + decalage:x0 + decalage + p]


def la_lecture(encre: np.ndarray, carte: np.ndarray) -> dict:
    """La corrélation d'une lecture réduite 8 fois avec la carte sous le bloc, et avec la carte décalée."""
    lue = m296.reduire(encre)
    sous = m296.la_carte_sous(carte, *m296.LE_BLOC_ETALON, 1)
    dec = la_carte_decalee(carte)
    h, w = min(lue.shape[0], sous.shape[0], dec.shape[0]), min(lue.shape[1], sous.shape[1], dec.shape[1])
    c, n = m296.correlation(lue[:h, :w], sous[:h, :w])
    t, _ = m296.correlation(lue[:h, :w], dec[:h, :w])
    return {"la_correlation": c, "le_temoin": t, "les_pixels": n}


def le_verdict(d: dict) -> dict:
    if d["le_controle"]["la_correlation"] != LE_CONTROLE:
        return {"decidable": False, "lissue": f"indécidable : la lecture de 296 ne redonne pas {LE_CONTROLE}"}
    x = d["les_lectures"].get(str(LE_FACTEUR_QUI_DECIDE))
    if x is None or x["la_correlation"] is None:
        return {"decidable": False, "lissue": "indécidable : la lecture à 9,6 µm manque"}
    c, t = x["la_correlation"], x["le_temoin"]
    tete = f"à 9,6 µm, corrélation {c:g} contre {t:g} pour le témoin ; à 2,4 µm, {LE_CONTROLE:g}".replace(".", ",")
    if c < LE_PLANCHER or (t is not None and c <= t):
        return {"decidable": True, "lissue": f"{tete} ; non"}
    return {"decidable": True, "lissue": f"{tete} ; {'oui' if c >= LE_SEUIL else 'en partie'}"}


def encre(facteurs: tuple[int, ...] = LES_FACTEURS, inverse: bool = False) -> int:
    """Une lecture par facteur. ⚠ Un facteur par processus : un second modèle chargé dans le même processus a buté sur la garde de
    mémoire, le 2026-10-01, sans que le premier soit libéré."""
    LE_DOSSIER.mkdir(parents=True, exist_ok=True)
    for f in facteurs:
        t0 = time.monotonic()
        pile = le_bloc_ramene(f)[..., ::-1].copy() if inverse else le_bloc_ramene(f)
        print(json.dumps({"le_facteur": f, "ramene_en_secondes": round(time.monotonic() - t0, 1), "la_pile": list(pile.shape)}), flush=True)
        r = lencre(pile, LE_DOSSIER / f"etalon_ramene_{f}{'_inverse' if inverse else ''}.npy")
        with (LE_DOSSIER / "encre.out").open("a") as o:
            o.write(json.dumps({"le_facteur": f, "inverse": inverse, **r}, ensure_ascii=False) + "\n")
        print(json.dumps({"le_facteur": f, **r}, ensure_ascii=False), flush=True)
        del pile
    return 0


def mesurer() -> dict:
    carte = m296.la_carte_publiee()
    d = {"la_question": __doc__.splitlines()[0],
         "les_constantes": {"les_facteurs": list(LES_FACTEURS), "le_facteur_qui_decide": LE_FACTEUR_QUI_DECIDE, "le_controle": LE_CONTROLE,
                            "le_seuil": LE_SEUIL, "le_plancher": LE_PLANCHER, "le_decalage": m296.LE_DECALAGE,
                            "les_couches": list(m296.LES_COUCHES)},
         "le_controle": la_lecture(np.load(m296.LE_DOSSIER_ENCRE / "etalon_reference.npy"), carte),
         "les_lectures": {str(f): la_lecture(np.load(LE_DOSSIER / f"etalon_ramene_{f}.npy"), carte)
                          for f in LES_FACTEURS if (LE_DOSSIER / f"etalon_ramene_{f}.npy").exists()},
         "la_lecture_inverse": (la_lecture(np.load(LE_DOSSIER / f"etalon_ramene_{LE_FACTEUR_QUI_DECIDE}_inverse.npy"), carte)
                                if (LE_DOSSIER / f"etalon_ramene_{LE_FACTEUR_QUI_DECIDE}_inverse.npy").exists() else None),
         "les_temps": [json.loads(l) for l in (LE_DOSSIER / "encre.out").read_text().splitlines()] if (LE_DOSSIER / "encre.out").exists() else []}
    d["le_verdict"] = le_verdict(d)
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

    damier = np.indices((8, 8, 8)).sum(0) % 2 * 200.0
    v("★★★★ la moyenne de bloc rend la moyenne de chaque bloc", np.allclose(reduire_le_volume(damier, 2), 100.0))
    v("★★★★ un bloc de bord incomplet est moyenné sur ce qu'il a",
      np.allclose(reduire_le_volume(np.arange(5, dtype=np.float32)[:, None, None] * np.ones((5, 4, 4)), 4)[:, 0, 0], [1.5, 4.0]))
    v("★★★★ les centres sont alignés : le voxel fin 0 d'un facteur 4 est à −3/8 de la première maille grossière",
      np.allclose(les_coordonnees(8, 4), [-0.375, -0.125, 0.125, 0.375, 0.625, 0.875, 1.125, 1.375]))
    rampe = np.add.outer(np.add.outer(np.arange(16.0), np.arange(16.0)), np.arange(16.0)) * 2.0
    g = reduire_le_volume(rampe, 4)
    fin = reechantillonner(g, rampe.shape, 4, 4, 12)
    v("★★★★ une rampe ramenée puis rééchantillonnée est rendue loin des bords",
      np.abs(fin[4:12, 4:12, :].astype(float) - np.transpose(rampe[4:12, 4:12, 4:12], (1, 2, 0))).max() <= 1.0)
    v("★★★★ la pile rendue est (y, x, couche), des couches demandées seulement", fin.shape == (16, 16, 8) and fin.dtype == np.uint8)
    carte = np.tile(np.arange(4000, dtype=np.float32), (4000, 1))
    p = m296.LE_CHUNK * m296.LE_BLOC // m296.LA_REDUCTION
    y0, x0 = m296.LE_BLOC_ETALON[0] * m296.LE_CHUNK // m296.LA_REDUCTION, m296.LE_BLOC_ETALON[1] * m296.LE_CHUNK // m296.LA_REDUCTION
    v("★★★★ la carte décalée est la carte sous le bloc, 64 pixels plus loin",
      la_carte_decalee(carte).shape == (p, p) and np.array_equal(la_carte_decalee(carte), carte[y0:y0 + p, x0 + 64:x0 + 64 + p]))

    lu = lambda c, t: {"le_controle": {"la_correlation": LE_CONTROLE}, "les_lectures": {"4": {"la_correlation": c, "le_temoin": t}}}  # noqa: E731
    v("★★★★ la règle : 0,8 et au-dessus du témoin, oui ; sous 0,5 ou pas au-dessus du témoin, non ; sinon, en partie",
      le_verdict(lu(0.85, 0.1))["lissue"].endswith("; oui") and le_verdict(lu(0.45, 0.1))["lissue"].endswith("; non")
      and le_verdict(lu(0.7, 0.75))["lissue"].endswith("; non") and le_verdict(lu(0.7, 0.1))["lissue"].endswith("; en partie"))
    v("★★★★ l'issue dit la corrélation, le témoin et le contrôle",
      le_verdict(lu(0.7, 0.1))["lissue"] == "à 9,6 µm, corrélation 0,7 contre 0,1 pour le témoin ; à 2,4 µm, 0,9593 ; en partie")
    v("★★★ indécidable si le contrôle ne redonne pas 0,9593, ou si la lecture à 9,6 µm manque",
      not le_verdict({**lu(0.9, 0.1), "le_controle": {"la_correlation": 0.95}})["decidable"]
      and not le_verdict({"le_controle": {"la_correlation": LE_CONTROLE}, "les_lectures": {}})["decidable"])

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--encre", action="store_true", help="le détecteur sur le bloc étalon ramené, sur l'iGPU")
    p.add_argument("--facteur", type=int, choices=LES_FACTEURS, default=None, help="avec --encre, un seul facteur")
    p.add_argument("--inverse", action="store_true", help="avec --encre, les couches dans l'ordre inverse")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.encre:
        return encre(LES_FACTEURS if a.facteur is None else (a.facteur,), a.inverse)
    d = mesurer()
    texte = json.dumps(d, ensure_ascii=False, indent=1)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps(d["le_verdict"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
