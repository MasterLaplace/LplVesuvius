#!/usr/bin/env python3
"""Deux maillages qui prétendent au même endroit y sont-ils ?

⚠⚠ POURQUOI. Une chaîne de projections et un bond direct de même longueur totale sont deux
manières d'atteindre le même point. Les comparer par leur **profil** demande deux rendus, et
[`44`](../docs/44_ou_la_chaine_se_trouve.md) a mesuré que ce chemin échoue quand la distance
est assez grande pour que les deux soient déjà sorties de leur feuille : on oppose alors
« mauvais » à « irrendable ». La question « les deux atterrissent-elles au même endroit ? »
est plus élémentaire, et elle ne coûte **aucun rendu**.

⭐ Ce qui rend la comparaison possible : deux `tifxyz` issus d'une même source partagent leur
**paramétrisation**. Le point de grille (i, j) désigne le même point de la nappe de départ des
deux côtés, donc les apparier est légitime — et c'est la SEULE raison pour laquelle ça l'est.
Deux maillages de provenances différentes ne s'apparient pas par indice, et ce fichier
**refuse** de le faire (formes différentes ⇒ erreur).

⚠⚠ Un écart nu ne veut rien dire. « 4 voxels » est énorme si les deux maillages n'ont bougé
que de 4 voxels, et négligeable s'ils en ont parcouru 120. Le nombre qui porte le sens est donc
le **rapport à la longueur du déplacement** — d'où l'argument `--depuis`, qui nomme la source
commune. Sans elle, ce script imprime la distance et refuse d'en tirer un verdict.

⭐ Et l'écart se **décompose**, parce que deux échecs différents s'y cachent :

  - **le long** du déplacement : la chaîne avance un peu plus, ou un peu moins, loin que le
    bond. C'est un réglage de pas, pas une divergence — la feuille suivie est la même.
  - **en travers** : la chaîne a dérivé de côté. C'est le cisaillement, et c'est ce qui fait
    changer de feuille.

Les confondre ferait passer un décalage de calibration pour une perte de nappe, et l'inverse.

Usage :
    uv run python analysis/src/ecart_de_maillages.py A B --depuis SOURCE [--voxel-um 2.4]
    uv run python analysis/src/ecart_de_maillages.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INVALIDE = 0.0


def lire(dossier: Path):
    """Les trois plans et la métadonnée d'un `tifxyz`."""
    import tifffile

    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    if len({a.shape for a in plans.values()}) != 1:
        raise ValueError(f"{dossier} : les trois images n'ont pas la même forme")
    return plans, meta


def valide(plans):
    return (plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE)


def ecart(a_plans, b_plans, source_plans=None) -> dict:
    """L'écart point à point entre deux maillages appariés par indice de grille.

    ⚠⚠ Seuls les points valides **des deux** côtés comptent. Un point absent d'un maillage
    n'est pas un accord à écart nul : c'est une absence, et la compter comme un zéro tirerait
    la médiane vers le bas d'autant plus fort que le maillage est troué — soit exactement la
    mauvaise direction.
    """
    import numpy as np

    formes = {a_plans["x"].shape, b_plans["x"].shape}
    if len(formes) != 1:
        raise ValueError(f"grilles de formes différentes : {formes} — non appariables")

    bon = valide(a_plans) & valide(b_plans)
    if source_plans is not None:
        if source_plans["x"].shape != a_plans["x"].shape:
            raise ValueError("la source n'a pas la forme des maillages comparés")
        bon = bon & valide(source_plans)
    n = int(bon.sum())
    if n == 0:
        raise ValueError("aucun point valide des deux côtés — rien à comparer")

    d = np.stack([b_plans[c][bon].astype(np.float64) - a_plans[c][bon].astype(np.float64)
                  for c in ("x", "y", "z")], axis=1)
    norme = np.linalg.norm(d, axis=1)
    r = {
        "points_compares": n,
        "points_grille": int(bon.size),
        "ecart_median_vox": float(np.median(norme)),
        "ecart_p90_vox": float(np.percentile(norme, 90)),
        "ecart_max_vox": float(norme.max()),
    }

    if source_plans is None:
        return r

    # ⭐ Le déplacement commun : de la source vers le premier maillage. C'est l'échelle à
    # laquelle l'écart doit être lu, et c'est ce qui transforme une distance en verdict.
    dep = np.stack([a_plans[c][bon].astype(np.float64) - source_plans[c][bon].astype(np.float64)
                    for c in ("x", "y", "z")], axis=1)
    longueur = np.linalg.norm(dep, axis=1)
    r["deplacement_median_vox"] = float(np.median(longueur))
    med_dep = r["deplacement_median_vox"]
    r["rapport_median"] = float(r["ecart_median_vox"] / med_dep) if med_dep > 0 else None

    # ⚠⚠ La décomposition. `axe` est la direction du déplacement en chaque point, donc la
    # projection de l'écart dessus est « la chaîne va-t-elle aussi loin » et le reste est
    # « la chaîne part-elle de côté ». Là où le déplacement est nul la direction n'existe
    # pas : ces points sont EXCLUS de la décomposition plutôt que projetés sur un axe
    # arbitraire, ce qui inventerait une dérive ou l'effacerait selon l'axe choisi.
    utile = longueur > 0
    if int(utile.sum()) == 0:
        return r
    axe = dep[utile] / longueur[utile][:, None]
    le_long = np.einsum("ij,ij->i", d[utile], axe)
    en_travers = np.linalg.norm(d[utile] - le_long[:, None] * axe, axis=1)
    r["points_decomposes"] = int(utile.sum())
    r["le_long_median_vox"] = float(np.median(le_long))
    r["en_travers_median_vox"] = float(np.median(en_travers))
    r["en_travers_p90_vox"] = float(np.percentile(en_travers, 90))
    return r


def en_micrometres(r: dict, voxel_um: float, spire_um: float | None = None) -> dict:
    """⚠ Un nombre appartient à sa géométrie de lecture. Les unités voyagent ensemble.

    ⭐ Et `spire_um` ajoute la seule unité qui rende un écart LISIBLE : la **spire**. « 8 µm »
    ne dit pas si deux maillages sont sur la même feuille ; « 0,05 spire » le dit. L'écart
    inter-spires est mesuré par `analysis/src/espacement_spires.py` et publié rouleau par
    rouleau dans [`16`](../docs/16_carte_difficulte_rouleaux_du_prix.md).

    ⚠⚠ Il n'a AUCUN défaut, et c'est délibéré : une spire appartient à son rouleau — 150 µm
    pour `PHerc0125`, 225 pour `PHerc1667`. En défauter un attribuerait la géométrie d'un
    rouleau aux mesures d'un autre, silencieusement, et c'est exactement la classe d'erreur
    que ce dépôt paie le plus cher.
    """
    out = dict(r)
    out["voxel_um"] = voxel_um
    for cle in list(r):
        if cle.endswith("_vox"):
            out[cle[:-4] + "_um"] = r[cle] * voxel_um
    if spire_um:
        out["spire_um"] = spire_um
        for cle in list(r):
            if cle.endswith("_vox"):
                out[cle[:-4] + "_spires"] = r[cle] * voxel_um / spire_um
    return out


def verifier() -> int:
    """Les témoins, sur des maillages fabriqués dont on connaît l'écart exact."""
    import shutil
    import tempfile

    import numpy as np
    import tifffile

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    lignes, colonnes = 7, 11
    gx = np.zeros((lignes, colonnes), dtype=np.float32)
    gy = np.zeros_like(gx)
    gz = np.full_like(gx, 500.0)
    for r_ in range(lignes):
        for c in range(colonnes):
            gx[r_, c] = 1000.0 + 10.0 * c
            gy[r_, c] = 2000.0 + 10.0 * r_
    src = {"x": gx, "y": gy, "z": gz}

    def decale(dx, dy, dz):
        return {"x": gx + dx, "y": gy + dy, "z": gz + dz}

    # Deux maillages IDENTIQUES : écart nul, partout.
    r = ecart(decale(30, 0, 0), decale(30, 0, 0), src)
    v("deux maillages identiques ont un écart nul", r["ecart_median_vox"] == 0.0)
    v("... et un écart maximal nul aussi", r["ecart_max_vox"] == 0.0)
    v("... et un rapport nul au déplacement", r["rapport_median"] == 0.0)
    v("tous les points sont comparés", r["points_compares"] == lignes * colonnes)

    # Un écart PUREMENT LE LONG : les deux ont avancé sur x, l'un de 30, l'autre de 34.
    r = ecart(decale(30, 0, 0), decale(34, 0, 0), src)
    v("un écart le long vaut sa différence", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("... et le déplacement vaut 30", abs(r["deplacement_median_vox"] - 30.0) < 1e-9)
    v("... et le rapport vaut 4/30", abs(r["rapport_median"] - 4.0 / 30.0) < 1e-9)
    v("... la composante le long porte tout", abs(r["le_long_median_vox"] - 4.0) < 1e-9)
    v("... et il n'y a AUCUNE dérive", abs(r["en_travers_median_vox"]) < 1e-9)
    # ⚠ Le signe compte : aller moins loin n'est pas aller plus loin.
    r2 = ecart(decale(30, 0, 0), decale(26, 0, 0), src)
    v("aller moins loin donne un le-long NÉGATIF", r2["le_long_median_vox"] < 0,
      str(r2["le_long_median_vox"]))

    # Un écart PUREMENT EN TRAVERS : même avance sur x, mais l'un a dérivé sur z.
    r = ecart(decale(30, 0, 0), decale(30, 0, 5), src)
    v("un écart en travers vaut sa dérive", abs(r["ecart_median_vox"] - 5.0) < 1e-9)
    v("... la composante le long est nulle", abs(r["le_long_median_vox"]) < 1e-9)
    v("... et la dérive porte tout", abs(r["en_travers_median_vox"] - 5.0) < 1e-9)

    # ⚠⚠ Le contrôle qui compte le plus : un point invalide n'est PAS un accord.
    a = decale(30, 0, 0)
    b = {k: arr.copy() for k, arr in decale(34, 0, 0).items()}
    for c in ("x", "y", "z"):
        b[c][0, 0] = INVALIDE
    r = ecart(a, b, src)
    v("un point invalide est EXCLU, pas compté à zéro",
      r["points_compares"] == lignes * colonnes - 1, str(r["points_compares"]))
    v("... et il ne tire pas la médiane vers zéro", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("la grille entière reste rapportée", r["points_grille"] == lignes * colonnes)

    # Des grilles de formes différentes ne s'apparient pas.
    autre = {c: np.zeros((3, 3), dtype=np.float32) + 1.0 for c in ("x", "y", "z")}
    try:
        ecart(a, autre)
        v("deux formes différentes sont refusées", False)
    except ValueError:
        v("deux formes différentes sont refusées", True)

    # Aucun point valide des deux côtés.
    vide = {c: np.zeros((lignes, colonnes), dtype=np.float32) for c in ("x", "y", "z")}
    try:
        ecart(a, vide)
        v("aucun point commun est refusé", False)
    except ValueError:
        v("aucun point commun est refusé", True)

    # Sans source, pas de verdict — la distance seule ne dit rien.
    r = ecart(a, decale(34, 0, 0))
    v("sans source, l'écart est mesuré", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    v("... mais AUCUN rapport n'est annoncé", "rapport_median" not in r)
    v("... et aucune décomposition non plus", "le_long_median_vox" not in r)

    # ⚠ Un déplacement nul n'a pas de direction : la décomposition doit s'abstenir.
    r = ecart(src, decale(0, 0, 3), src)
    v("un déplacement nul ne fabrique pas d'axe", "le_long_median_vox" not in r,
      str(r.get("le_long_median_vox")))

    # Les deux unités voyagent ensemble.
    u = en_micrometres({"ecart_median_vox": 4.0, "points_compares": 7}, 2.4)
    v("l'écart est converti en µm", abs(u["ecart_median_um"] - 9.6) < 1e-9)
    v("... la valeur en voxels reste", u["ecart_median_vox"] == 4.0)
    v("... la taille du voxel est écrite", u["voxel_um"] == 2.4)
    v("... et un compte n'est PAS converti", "points_compares_um" not in u)

    # ⭐ La lecture en SPIRES, la seule qui dise si deux maillages sont sur la même feuille.
    u = en_micrometres({"ecart_median_vox": 4.0, "points_compares": 7}, 2.4, spire_um=173.0)
    v("l'écart est aussi lu en spires",
      abs(u["ecart_median_spires"] - 9.6 / 173.0) < 1e-12, str(u.get("ecart_median_spires")))
    v("... et la spire employée est écrite", u["spire_um"] == 173.0)
    # ⚠⚠ Sans spire déclarée, AUCUNE lecture en spires. Un rouleau a la sienne — 150 µm pour
    # PHerc0125, 225 pour PHerc1667 — et en défauter une attribuerait la géométrie d'un
    # rouleau aux mesures d'un autre.
    u = en_micrometres({"ecart_median_vox": 4.0}, 2.4)
    v("sans spire déclarée, aucune lecture en spires", "ecart_median_spires" not in u)
    u = en_micrometres({"ecart_median_vox": 4.0}, 2.4, spire_um=0.0)
    v("une spire nulle n'invente pas de division", "ecart_median_spires" not in u)

    # Le tour complet par le disque, sur de vrais fichiers.
    racine = Path(tempfile.mkdtemp(prefix="ecart_temoins_"))
    for nom, plans in (("src", src), ("a", decale(30, 0, 0)), ("b", decale(34, 0, 0))):
        d = racine / nom
        d.mkdir()
        for c in ("x", "y", "z"):
            tifffile.imwrite(str(d / f"{c}.tif"), plans[c].astype(np.float32))
        (d / "meta.json").write_text(json.dumps({"scale": [0.05, 0.05], "uuid": nom}),
                                     encoding="utf-8")
    pa, _ = lire(racine / "a")
    pb, _ = lire(racine / "b")
    ps, _ = lire(racine / "src")
    r = ecart(pa, pb, ps)
    v("le tour par le disque donne le même écart", abs(r["ecart_median_vox"] - 4.0) < 1e-9)
    shutil.rmtree(racine, ignore_errors=True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("a", nargs="?", type=Path, help="premier maillage (tifxyz)")
    p.add_argument("b", nargs="?", type=Path, help="second maillage (tifxyz)")
    p.add_argument("--depuis", type=Path,
                   help="la source commune — sans elle, aucun rapport n'est annoncé")
    p.add_argument("--voxel-um", type=float, default=2.4,
                   help="taille du voxel du maillage (défaut : niveau 0 du scan)")
    p.add_argument("--spire-um", type=float,
                   help="l'écart inter-spires du rouleau (docs/16) — sans lui, aucune "
                        "lecture en spires n'est annoncée")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()

    if a.verifier:
        return verifier()
    if not a.a or not a.b:
        p.error("deux maillages sont requis")

    pa, _ = lire(a.a)
    pb, _ = lire(a.b)
    ps = lire(a.depuis)[0] if a.depuis else None
    r = en_micrometres(ecart(pa, pb, ps), a.voxel_um, a.spire_um)
    r["a"] = a.a.name
    r["b"] = a.b.name
    r["depuis"] = a.depuis.name if a.depuis else None

    print(f"{a.a.name}  contre  {a.b.name}"
          + (f"   (depuis {a.depuis.name})" if a.depuis else ""))
    print(f"  points comparés     {r['points_compares']} / {r['points_grille']}")
    print(f"  écart médian        {r['ecart_median_vox']:.3f} vox   "
          f"{r['ecart_median_um']:.1f} µm")
    print(f"  écart p90           {r['ecart_p90_vox']:.3f} vox   {r['ecart_p90_um']:.1f} µm")
    print(f"  écart max           {r['ecart_max_vox']:.3f} vox   {r['ecart_max_um']:.1f} µm")
    if "deplacement_median_vox" in r:
        print(f"  déplacement médian  {r['deplacement_median_vox']:.3f} vox   "
              f"{r['deplacement_median_um']:.1f} µm")
        print(f"  ⭐ rapport           {r['rapport_median'] * 100:.2f} % du déplacement")
    if "ecart_median_spires" in r:
        print(f"  ⭐ en spires         médian {r['ecart_median_spires']:.3f}   "
              f"p90 {r['ecart_p90_spires']:.3f}   max {r['ecart_max_spires']:.3f}"
              f"   (spire = {r['spire_um']:.0f} µm)")
    if "le_long_median_vox" in r:
        print(f"  le long             {r['le_long_median_vox']:+.3f} vox   "
              f"{r['le_long_median_um']:+.1f} µm")
        print(f"  en travers          {r['en_travers_median_vox']:.3f} vox   "
              f"{r['en_travers_median_um']:.1f} µm   "
              f"(p90 {r['en_travers_p90_um']:.1f} µm)")
    else:
        print("  ⚠ aucun rapport : la source commune n'a pas été donnée (--depuis)")

    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
