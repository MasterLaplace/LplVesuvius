#!/usr/bin/env python3
"""Jusqu'où la chaîne reste-t-elle DANS le segment publié — donc en territoire connu ?

⚠⚠ POURQUOI CETTE MESURE DÉCIDE. Tout ce qu'on sait de la chaîne tangentielle dit
« elle est sur DU papyrus » — la matière répond, franchement au-dessus du hasard, sur
5,76 mm ([`44`](../../docs/44_ou_la_chaine_se_trouve.md)). Aucune de ces mesures ne dit
qu'elle est sur la **BONNE** feuille, celle qui prolonge le texte. Seule l'**encre** le
dirait, et l'encre publiée n'existe que là où quelqu'un est déjà passé.

⭐ Donc la première question n'est pas « rendre » — un rendu de maillon est une opération
**réseau** de plusieurs heures, et `54` raconte cinq rendus vides — mais **où s'arrête la
vérité terrain**. Ce fichier le mesure sans lire un seul voxel du volume :

- si la chaîne reste DANS le segment publié sur toute sa longueur, alors son encre est
  **déjà connue** et la question se répond en comparant des cartes qui existent ;
- si elle en sort au maillon N, alors N est exactement l'endroit où la découverte commence,
  et c'est là qu'un rendu vaut son prix.

⚠ La tolérance n'est pas choisie, elle est **dérivée** : c'est le pas d'échantillonnage du
maillage publié lui-même, mesuré sur sa propre grille. « Être sur ce maillage » n'a pas de
sens plus fin que la maille qui le décrit, et un seuil réglé à la main serait un nombre
choisi pour que le résultat du jour passe.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import tifffile
from scipy.spatial import cKDTree

RACINE = Path(__file__).resolve().parents[2]
UM_PAR_VOXEL = 2.4
"""⚠ La convention de `chainer_tangentiel.sh` (`UM_BASE`), pas une supposition : le maillon 20
rapporte `parcouru_vox = 800` et le document lit 1 920 µm."""


def points_et_cases(dossier: Path) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    """Les points valides, LEUR CASE dans la grille, et la forme de la grille.

    ⚠⚠ La case est ce qui distingue « à une feuille de distance » de « sorti par le bord ».
    Une distance au plus proche voisin confond les deux : dès qu'un point sort de l'emprise
    du maillage, son plus proche voisin est sur la BORDURE, et la distance devient une
    distance latérale qu'on lirait comme une profondeur. Le morceau de départ est découpé à
    l'origine `[29, 319]` d'une grille de 2 530 × 1 820, donc à **29 cases du bord** — soit
    1,4 mm — pendant que la chaîne en parcourt 5,76. L'hypothèse du bord n'est pas exotique,
    c'est la première à écarter.
    """
    x = tifffile.imread(dossier / "x.tif")
    y = tifffile.imread(dossier / "y.tif")
    z = tifffile.imread(dossier / "z.tif")
    m = x > 0
    return (np.stack([x[m], y[m], z[m]], axis=1).astype(np.float64),
            bord_du_valide(m)[m], x.shape)


def bord_du_valide(masque: np.ndarray) -> np.ndarray:
    """Les cases valides qui touchent une case INVALIDE — le vrai bord du maillage.

    ⚠⚠ Cette fonction existe parce que ma première version définissait le bord par la
    FORME de la grille, et ce contrôle **ne pouvait pas se déclencher** : le maillage publié
    laisse une marge vide de cinq cases sur ses quatre côtés, donc aucune case valide n'était
    à moins d'une case du bord déclaré, et « 0 % au bord » était vrai par construction, pas
    par mesure. C'est la sonde qui l'a dit, pas la relecture.

    ⭐ Le bord d'un maillage à trous n'est pas un rectangle : c'est là où le valide s'arrête,
    trous intérieurs compris. Un voisin manquant suffit à le définir, et il n'y a alors
    aucune marge à choisir.
    """
    p = np.pad(masque, 1, mode="constant", constant_values=False)
    voisins = (p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    return masque & ~voisins


def points(dossier: Path) -> tuple[np.ndarray, tuple[int, int]]:
    """Les points valides d'un maillage tifxyz, et la forme de sa grille.

    ⚠ `x > 0` est le masque de validité du format : une case sans surface porte zéro. Le
    prendre pour une coordonnée mettrait tous les trous à l'origine du volume, c'est-à-dire
    très loin de la feuille, et gonflerait toutes les distances.
    """
    x = tifffile.imread(dossier / "x.tif")
    y = tifffile.imread(dossier / "y.tif")
    z = tifffile.imread(dossier / "z.tif")
    m = x > 0
    return np.stack([x[m], y[m], z[m]], axis=1).astype(np.float64), x.shape


def pas_du_maillage(dossier: Path, echantillon: int = 20000) -> float:
    """Le pas d'échantillonnage du maillage, en voxels — la distance MÉDIANE entre deux
    cases voisines de sa propre grille.

    ⭐ C'est la tolérance : au-delà, « ce point est sur ce maillage » cesse d'avoir un sens,
    puisque le maillage lui-même ne décrit rien de plus fin.

    ⚠ La médiane, pas la moyenne : un maillage tifxyz a des trous, donc des paires voisines
    séparées par tout un trou. La moyenne en hériterait, la médiane non.
    """
    x = tifffile.imread(dossier / "x.tif").astype(np.float64)
    y = tifffile.imread(dossier / "y.tif").astype(np.float64)
    z = tifffile.imread(dossier / "z.tif").astype(np.float64)
    valide = x > 0
    paire = valide[:, :-1] & valide[:, 1:]
    if not paire.any():
        return float("nan")
    d = np.sqrt((x[:, :-1] - x[:, 1:]) ** 2 + (y[:, :-1] - y[:, 1:]) ** 2
                + (z[:, :-1] - z[:, 1:]) ** 2)[paire]
    if d.size > echantillon:
        d = d[:: max(1, d.size // echantillon)]
    return float(np.median(d))


def normales_de(dossier: Path) -> tuple[np.ndarray, np.ndarray]:
    """Les normales unitaires du maillage de référence, aux mêmes cases que ses points.

    ⚠ Réutilise `recaler_sur_la_matiere.normales`, qui réutilise lui-même les tangentes de
    `projeter_tangentiel` : une seconde définition de « la normale d'un tifxyz » finirait par
    ne pas s'accorder avec celle qui a construit la chaîne, et c'est précisément l'accord
    entre les deux qu'on mesure ici.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import recaler_sur_la_matiere as rm

    plans = {n: tifffile.imread(dossier / f"{n}.tif") for n in ("x", "y", "z")}
    n, ok = rm.normales(plans)
    m = plans["x"] > 0
    return n[m], ok[m]


def ecart_signe(pts: np.ndarray, pts_ref: np.ndarray, normales_ref: np.ndarray,
                ok_ref: np.ndarray, idx: np.ndarray) -> dict:
    """L'écart PROJETÉ sur la normale du maillage de référence — donc signé.

    ⚠⚠ C'est ce qui distingue deux pannes que la distance seule confond. Une nappe
    **gauchie** s'écarte des deux côtés, donc ses signes sont mélangés ; une nappe qui a
    **changé de feuille** s'écarte toujours du même côté. La première se corrige par un
    gauchissement, la seconde par un décalage d'une spire le long de la normale — deux
    remèdes qui n'ont rien à voir.
    """
    bon = ok_ref[idx]
    if not bon.any():
        return {"points_avec_normale": 0}
    delta = pts[bon] - pts_ref[idx[bon]]
    proj = np.einsum("ij,ij->i", delta, normales_ref[idx[bon]])
    return {
        "points_avec_normale": int(bon.sum()),
        "ecart_signe_median_vox": float(np.median(proj)),
        "ecart_signe_p10_vox": float(np.percentile(proj, 10)),
        "ecart_signe_p90_vox": float(np.percentile(proj, 90)),
        "part_du_meme_cote": float(max((proj > 0).mean(), (proj < 0).mean())),
    }


def distances(pts: np.ndarray, arbre: cKDTree) -> np.ndarray:
    """La distance de chaque point au point le plus proche du maillage de référence."""
    d, _ = arbre.query(pts, k=1)
    return d


def couverture(pts: np.ndarray, arbre: cKDTree, tolerance: float,
               bord_ref: np.ndarray | None = None,
               pts_ref: np.ndarray | None = None,
               normales_ref: np.ndarray | None = None,
               ok_ref: np.ndarray | None = None) -> dict:
    """Quelle part de ces points tombe SUR le maillage de référence, et à quelle distance.

    ⚠ `part_au_bord` est la moitié qui rend le reste lisible : c'est la part des points dont
    le plus proche voisin est sur la BORDURE du maillage de référence, donc pour lesquels la
    distance mesure une sortie latérale et non un écart de feuille.
    """
    d, idx = arbre.query(pts, k=1)
    out = {
        "points": int(pts.shape[0]),
        "part_sur_le_maillage": float((d <= tolerance).mean()),
        "distance_mediane_vox": float(np.median(d)),
        "distance_p90_vox": float(np.percentile(d, 90)),
        "distance_max_vox": float(d.max()),
    }
    if bord_ref is not None:
        bord = bord_ref[idx]
        out["part_au_bord"] = float(bord.mean())
        loin = d > tolerance
        out["part_au_bord_parmi_les_loin"] = (
            float(bord[loin].mean()) if loin.any() else 0.0)
    if normales_ref is not None and pts_ref is not None and ok_ref is not None:
        out.update(ecart_signe(pts, pts_ref, normales_ref, ok_ref, idx))
    return out


def verifier() -> int:
    """Le classement se garde lui-même, sur des maillages fabriqués."""
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    def ecrire(dossier: Path, xx, yy, zz):
        dossier.mkdir(parents=True, exist_ok=True)
        for nom, a in (("x", xx), ("y", yy), ("z", zz)):
            tifffile.imwrite(dossier / f"{nom}.tif", a.astype(np.float32))

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        # Un plan regulier de pas 3, avec un trou : le pas mesure doit valoir 3 malgre lui.
        n = 40
        u, w = np.meshgrid(np.arange(n) * 3.0, np.arange(n) * 3.0, indexing="ij")
        base = np.full_like(u, 100.0)
        xx = u + 1000.0
        yy = w + 2000.0
        zz = base
        xx[10:14, 10:14] = 0.0  # un trou : x == 0 marque l invalidite
        ecrire(r / "ref", xx, yy, zz)

        pas = pas_du_maillage(r / "ref")
        v("le pas du maillage est celui de sa grille", abs(pas - 3.0) < 1e-6, str(pas))

        pts_ref, forme = points(r / "ref")
        v("la forme de la grille est rendue", forme == (n, n), str(forme))
        v("... et le trou n'est pas compté", pts_ref.shape[0] == n * n - 16,
          str(pts_ref.shape))
        # ⚠⚠ Le trou ne doit pas devenir un point a l origine : sinon toutes les distances
        # seraient calculees contre un point situe a mille voxels de la feuille.
        v("... ni ramené à l'origine", float(pts_ref[:, 0].min()) >= 1000.0,
          str(pts_ref[:, 0].min()))

        arbre = cKDTree(pts_ref)
        # Une copie posee exactement dessus.
        ecrire(r / "sur", xx, yy, zz)
        c = couverture(points(r / "sur")[0], arbre, pas)
        v("un maillage posé sur la référence est couvert à 100 %",
          c["part_sur_le_maillage"] == 1.0, str(c))
        v("... et sa distance médiane est nulle", c["distance_mediane_vox"] == 0.0)

        # Le meme, decale d une demi-maille : encore sur le maillage.
        # ⚠⚠ Le decalage ne s applique QU AUX CASES VALIDES. Ma premiere version faisait
        # `xx + 1.0` sur toute la grille, donc les trous passaient de 0 a 1 -- ils
        # devenaient valides au sens du format et apparaissaient comme des points a mille
        # voxels de la feuille. C est exactement le piege que la docstring de `points()`
        # decrit, tombe dans ma propre fixture, et c est le controle qui l a dit.
        xx_proche = np.where(xx > 0, xx + 1.0, 0.0)
        ecrire(r / "proche", xx_proche, yy, zz)
        c = couverture(points(r / "proche")[0], arbre, pas)
        v("un décalage sous le pas reste couvert", c["part_sur_le_maillage"] == 1.0, str(c))

        # Decale de dix mailles en PROFONDEUR : plus du tout dessus.
        ecrire(r / "loin", xx, yy, zz + 30.0)
        c = couverture(points(r / "loin")[0], arbre, pas)
        v("un décalage de dix mailles n'est plus couvert",
          c["part_sur_le_maillage"] == 0.0, str(c))
        v("... et la distance le dit", abs(c["distance_mediane_vox"] - 30.0) < 1e-6,
          str(c["distance_mediane_vox"]))

        # ⚠ La moitie dessus, la moitie loin : la part doit valoir 1/2, pas 0 ni 1. Sans ce
        # controle, une fonction qui rend toujours 0 ou toujours 1 passerait les deux
        # precedents.
        zz2 = zz.copy()
        zz2[n // 2:, :] += 30.0
        ecrire(r / "moitie", xx, yy, zz2)
        c = couverture(points(r / "moitie")[0], arbre, pas)
        v("une moitié dessus donne une part intermédiaire",
          0.4 < c["part_sur_le_maillage"] < 0.6, str(c["part_sur_le_maillage"]))

        # ⚠⚠ Le discriminant de bord doit POUVOIR se declencher. Ma premiere version le
        # definissait par la FORME de la grille, et le maillage publie laisse une marge vide
        # de cinq cases : « 0 % au bord » etait alors vrai par construction. Les deux sens
        # sont donc sondes, et sur un plan SANS trou le bord est exactement son perimetre.
        masque = xx > 0
        b = bord_du_valide(masque)
        # Le perimetre de la grille (n² moins l interieur) PLUS l anneau qui entoure le
        # trou 4x4 : deux rangees de 4 et deux colonnes de 4, soit 16 cases.
        attendu = n * n - (n - 2) * (n - 2) + 16
        v("le bord d un plan plein est son perimetre, trou compris",
          int(b.sum()) == attendu, f"{int(b.sum())} contre {attendu}")
        _, bord_ref, _ = points_et_cases(r / "ref")
        v("... et un maillage a trous en a un, mesurable", bord_ref.any())

        # Une nappe posee au CENTRE ne touche pas le bord ; une nappe posee DEHORS n a que
        # lui comme plus proche voisin.
        centre = slice(n // 3, 2 * n // 3)
        ecrire(r / "dedans", xx[centre, centre], yy[centre, centre], zz[centre, centre])
        c = couverture(points(r / "dedans")[0], arbre, pas, bord_ref)
        v("une nappe au centre ne touche pas le bord", c["part_au_bord"] < 0.35,
          str(c["part_au_bord"]))
        ecrire(r / "dehors", xx + n * 3.0 + 50.0, yy, zz)
        c = couverture(points(r / "dehors")[0], arbre, pas, bord_ref)
        v("... une nappe sortie par le côté n'a QUE lui", c["part_au_bord"] == 1.0,
          str(c["part_au_bord"]))
        v("... et elle n'est plus couverte", c["part_sur_le_maillage"] == 0.0)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # ⚠⚠⚠ Le verdict imprimait « ALL PASS » et rendait 0 INCONDITIONNELLEMENT :
    # cette batterie était verte quoi que disent ses contrôles. Trente-neuf
    # fichiers du dépôt portaient le même défaut, corrigé le 2026-08-27.
    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference", type=Path,
                   default=RACINE / "data/temoin_rendu/publie_20230702185753",
                   help="le maillage publié qui sert de territoire connu")
    p.add_argument("--chaine", type=Path,
                   default=RACINE / "data/chaine_deux_fixes",
                   help="le dossier de la chaîne (maillon_N/)")
    p.add_argument("--maillons", type=int, nargs="*",
                   help="les indices à mesurer (défaut : tous ceux présents)")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    if not (a.reference / "x.tif").is_file():
        print(f"REFUS : {a.reference} n'est pas un maillage tifxyz", file=sys.stderr)
        return 2

    pas = pas_du_maillage(a.reference)
    pts_ref, bord_ref, forme = points_et_cases(a.reference)
    norm_ref, ok_ref = normales_de(a.reference)
    arbre = cKDTree(pts_ref)
    print(f"référence : {a.reference.name}  ·  grille {forme[0]}×{forme[1]}  ·  "
          f"{pts_ref.shape[0]} points  ·  pas mesuré {pas:.2f} vox "
          f"({pas * UM_PAR_VOXEL:.1f} µm) — c'est la tolérance")

    indices = a.maillons
    if not indices:
        indices = sorted(int(d.name.split("_")[1]) for d in a.chaine.glob("maillon_*")
                         if d.is_dir() and d.name.split("_")[1].isdigit())
    lignes = []
    print(f"\n{'maillon':>8} {'parcouru':>10} {'sur le maillage':>16} "
          f"{'d médiane':>11} {'au bord':>9} {'écart signé':>13} {'même côté':>11}")
    for i in indices:
        d = a.chaine / f"maillon_{i}"
        if not (d / "x.tif").is_file():
            continue
        pts, _ = points(d)
        c = couverture(pts, arbre, pas, bord_ref, pts_ref, norm_ref, ok_ref)
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").is_file() else {}
        parcouru = meta.get("parcouru_vox", 0.0) * UM_PAR_VOXEL
        c["maillon"] = i
        c["parcouru_um"] = parcouru
        lignes.append(c)
        print(f"{i:>8} {parcouru:>9.0f} µm {c['part_sur_le_maillage'] * 100:>15.1f}% "
              f"{c['distance_mediane_vox']:>10.1f} "
              f"{c.get('part_au_bord', 0) * 100:>8.1f}% "
              f"{c.get('ecart_signe_median_vox', float('nan')):>12.1f} "
              f"{c.get('part_du_meme_cote', float('nan')) * 100:>10.1f}%")

    if a.json:
        a.json.write_text(json.dumps(
            {"reference": a.reference.name, "tolerance_vox": pas,
             "tolerance_um": pas * UM_PAR_VOXEL, "um_par_voxel": UM_PAR_VOXEL,
             "maillons": lignes}, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
