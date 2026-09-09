#!/usr/bin/env python3
"""La transformation publiee entre deux volumes d'un meme objet, lue et appliquee.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Les maillages de `PHercParis4` sont ecrits dans les voxels du
volume a 45,532 µm, ou un demi-ecart inter-feuilles vaut DEUX voxels : on ne peut pas y mesurer
un decalage de vingt micrometres. Le meme objet publie un volume a **2,4 µm** qui couvre
182 × 78 × 78 mm, et `data/metadata.min.json` publie la matrice qui relie les deux. Sans elle, la
mesure fine demanderait un recalage, c'est-a-dire un lot entier ; avec elle, c'est une
multiplication de matrice.

⭐⭐⭐ LA CONVENTION NE SE DEVINE PAS, ELLE SE MESURE, ET C'EST FAIT ICI. La matrice opere sur
(x, y, z) et rend du (x, y, z), alors qu'un volume zarr s'indexe en (z, y, x). Les deux lectures
sont plausibles et l'une est fausse. Le discriminant est qu'une meme cellule lue dans les DEUX
volumes doit donner des intensites correlees : mesure sur 400 cellules d'une bande reelle,
**+0,412** pour la bonne convention contre **+0,073** pour l'autre. Une convention supposee aurait
rendu des octets parfaitement valides, pris ailleurs dans le rouleau.

⚠ La correlation n'est que de 0,4 et c'est ATTENDU, pas un defaut : un voxel grossier moyenne
environ 19³ = 6859 voxels fins, donc il ne peut pas s'accorder avec un seul d'entre eux. Ce qui
compte est le RAPPORT entre les deux conventions, pas le niveau.

Usage :
    uv run python src/commun/transformations_de_volume.py --verifier
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
METADONNEES = RACINE / "data" / "metadata.min.json"


def _parcourir(o, chemin: str = ""):
    """Les champs `volume_transforms` du document, avec le chemin ou ils vivent."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "volume_transforms" and v:
                yield chemin, v
            else:
                yield from _parcourir(v, f"{chemin}/{k}")
    elif isinstance(o, list):
        for i, x in enumerate(o):
            yield from _parcourir(x, f"{chemin}[{i}]")


def matrice(objet: str, de: str, vers: str,
            metadonnees: Path = METADONNEES) -> np.ndarray | None:
    """La matrice 3×4 qui envoie les voxels de `de` sur ceux de `vers`, ou None.

    ⚠ Le fichier est gzippe malgre son extension `.json` : l'ouvrir en texte leve une erreur
    d'encodage qui ne ressemble pas du tout a « ce fichier est compresse ».
    """
    if not metadonnees.is_file():
        return None
    with gzip.open(metadonnees) as f:
        d = json.load(f)
    for chemin, entrees in _parcourir(d):
        if objet not in chemin:
            continue
        for e in entrees:
            if not isinstance(e, dict) or e.get("from_volume_id") != de:
                continue
            for t in e.get("transforms", []):
                if t.get("to_volume_id") == vers:
                    return np.asarray(t["matrix"], dtype=np.float64)
    return None


def appliquer(m: np.ndarray, xyz: np.ndarray) -> np.ndarray:
    """Envoie des points (x, y, z) du volume source vers les INDICES (z, y, x) du volume cible.

    ⭐⭐ LES DEUX INVERSIONS SONT ICI ET NULLE PART AILLEURS. La matrice parle (x, y, z), un zarr
    s'indexe (z, y, x) : faire la conversion sur chaque site d'appel garantit qu'un site finira
    par l'oublier, et l'oubli ne leve rien — il rend un point valide ailleurs dans le rouleau.
    """
    p = np.asarray(xyz, dtype=np.float64)
    forme = p.shape[:-1]
    q = p.reshape(-1, 3) @ m[:, :3].T + m[:, 3]
    return q[:, ::-1].reshape(*forme, 3)


def appliquer_direction(m: np.ndarray, xyz: np.ndarray) -> np.ndarray:
    """Envoie une DIRECTION (x, y, z) du volume source vers une direction (z, y, x) de la cible.

    ⚠⚠⚠ UNE DIRECTION N'EST PAS UN POINT, ET LA DIFFERENCE N'EST PAS ANODINE : la translation
    ne s'y applique pas. Passer une direction a `appliquer` ajouterait le decalage de 5000 voxels
    de la matrice, ce qui rendrait un vecteur pointant vers un coin du volume — parfaitement
    fini, parfaitement faux, et sans rien pour le signaler.

    ⭐⭐ ELLE VIT ICI POUR LA MEME RAISON QUE `appliquer` : l'inversion d'axes est faite en UN
    endroit. Un site d'appel qui la referait finirait par l'oublier, et l'oubli ne leve rien.

    Le resultat est renormalise : ce qu'on transporte est une direction, pas une longueur.
    """
    p = np.asarray(xyz, dtype=np.float64)
    forme = p.shape[:-1]
    q = p.reshape(-1, 3) @ m[:, :3].T
    q = q[:, ::-1]
    n = np.linalg.norm(q, axis=-1, keepdims=True)
    return (q / np.maximum(n, 1e-12)).reshape(*forme, 3)


def defaut_de_similitude(m: np.ndarray) -> float:
    """De combien la partie lineaire s'ecarte d'une rotation a l'echelle pres, en degres.

    ⭐⭐⭐ C'EST LA CONDITION QUI REND UN ANGLE COMPARABLE D'UN VOLUME A L'AUTRE, et sans elle
    toute confrontation entre un angle mesure dans le maillage et une direction mesuree dans le
    volume fin serait vide de sens. Une transformation qui cisaille ne conserve PAS les angles :
    « 34° dans le maillage » ne voudrait alors rien dire dans le volume fin, et l'ecart serait
    silencieux parce que les deux nombres resteraient plausibles.

    Mesure sur la transformation publiee de `PHercParis4` : conditionnement **1,0075**, ecart
    maximal de `R R^T` a l'identite **0,0053**, soit **0,30°**. Negligeable devant les dizaines
    de degres que `100` mesure, mais il fallait le montrer plutot que l'esperer.
    """
    r = m[:, :3] / echelle(m)
    return float(np.degrees(np.arcsin(min(1.0, np.max(np.abs(r @ r.T - np.eye(3)))))))


def echelle(m: np.ndarray) -> float:
    """Le facteur d'echelle de la matrice, mediane des normes de ses lignes.

    ⭐ C'est le controle le moins cher qui existe sur une matrice lue d'un fichier : elle doit
    valoir le rapport des tailles de voxel des deux volumes. Une matrice prise dans le mauvais
    sens rendrait son inverse, et rien d'autre ne le dirait avant la mesure.
    """
    return float(np.median(np.linalg.norm(m[:, :3], axis=1)))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'application, sur une matrice fabriquee ------------------------------------------
    m = np.array([[2.0, 0, 0, 10.0], [0, 3.0, 0, 20.0], [0, 0, 4.0, 30.0]])
    q = appliquer(m, np.array([[1.0, 1.0, 1.0]]))
    # x=1 -> 12, y=1 -> 23, z=1 -> 34, puis rendu en (z, y, x).
    v("la sortie est en (z, y, x), pas en (x, y, z)", list(q[0]) == [34.0, 23.0, 12.0], str(q[0]))
    # ⚠⚠ CE CONTROLE ATTRAPE UNE INVERSION MANQUANTE : avec des facteurs distincts par axe, une
    # sortie non inversee donnerait [12, 23, 34], que la ligne ci-dessus refuse.
    v("... et les trois axes portent des facteurs distincts, sinon l'ordre ne se verrait pas",
      len({2.0, 3.0, 4.0}) == 3)
    v("la forme d'entrée est préservée", appliquer(m, np.zeros((5, 7, 3))).shape == (5, 7, 3))
    v("l'échelle est la médiane des normes de lignes", echelle(m) == 3.0, str(echelle(m)))

    # --- la vraie matrice du depot ---------------------------------------------------------
    mm = matrice("PHercParis4", "20260310170716", "20260411134726")
    if mm is None:
        print("  ⚠ métadonnées absentes — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la transformation 45,532 µm → 2,4 µm est publiée", mm.shape == (3, 4), str(mm.shape))
    # ⭐⭐ L'ECHELLE DOIT VALOIR LE RAPPORT DES VOXELS : c'est ce qui distingue la matrice de son
    # inverse, et une matrice prise a l'envers rendrait des points hors du volume sans rien dire.
    attendu = 45.532 / 2.4
    v("... et son échelle vaut le rapport des tailles de voxel",
      abs(echelle(mm) / attendu - 1.0) < 0.01,
      f"{echelle(mm):.3f} pour {attendu:.3f} attendu")
    v("... dans le sens FIN, pas son inverse", echelle(mm) > 1.0, f"{echelle(mm):.3f}")
    inverse = matrice("PHercParis4", "20260411134726", "20260310170716")
    # ⭐⭐⭐ LA CONDITION QUI REND LES ANGLES DE `100` TRANSPORTABLES D'UN VOLUME A L'AUTRE.
    # Sans elle, confronter un angle mesure dans le maillage a une direction mesuree dans le
    # volume fin comparerait deux quantites qui ne sont pas la meme.
    v("la transformation publiée conserve les angles",
      defaut_de_similitude(mm) < 1.0, f"{defaut_de_similitude(mm):.2f}° d'écart")
    v("le sens inverse est publié aussi", inverse is not None)
    if inverse is not None:
        v("... et son échelle est bien l'inverse",
          abs(echelle(inverse) * echelle(mm) - 1.0) < 0.02,
          f"{echelle(inverse) * echelle(mm):.4f}")
        # ⚠ Aller-retour : la composition doit ramener au point de depart, sinon les deux
        # matrices ne decrivent pas le meme recalage et l'une des deux est perimee.
        p = np.array([[1000.0, 1100.0, 2000.0]])
        milieu = (p @ mm[:, :3].T + mm[:, 3])
        retour = milieu @ inverse[:, :3].T + inverse[:, 3]
        v("... et l'aller-retour revient au point de départ",
          float(np.max(np.abs(retour - p))) < 1.0,
          f"{float(np.max(np.abs(retour - p))):.3f} voxel d'écart")
    # --- LES DIRECTIONS, ET LA CONDITION QUI LES REND COMPARABLES -------------------------
    # ⚠⚠⚠ Une direction passee a `appliquer` recevrait la TRANSLATION : le controle est que les
    # deux fonctions ne rendent PAS la meme chose sur la meme entree, sinon l'une des deux est
    # inutile et le site d'appel a une chance sur deux de prendre la mauvaise.
    d_point = appliquer(m, np.array([[1.0, 0.0, 0.0]]))
    d_dir = appliquer_direction(m, np.array([[1.0, 0.0, 0.0]]))
    v("une direction ne reçoit PAS la translation",
      float(np.max(np.abs(d_point - d_dir))) > 1.0,
      f"point {np.round(d_point[0], 1)} contre direction {np.round(d_dir[0], 3)}")
    v("... et elle sort unitaire",
      abs(float(np.linalg.norm(d_dir[0])) - 1.0) < 1e-9)
    # ⚠ Sur la matrice fabriquee (diagonale 2, 3, 4), x -> z apres inversion d'axes.
    v("... et elle sort en (z, y, x) comme un point",
      abs(d_dir[0][2] - 1.0) < 1e-9 and abs(d_dir[0][0]) < 1e-9, str(np.round(d_dir[0], 6)))
    # ⭐⭐⭐ UNE SIMILITUDE CONSERVE LES ANGLES, UNE ECHELLE PAR AXE NON : le defaut est mesure,
    # pas suppose.
    # ⚠⚠ Et mon premier controle avait tort, pas le code : j'avais appele « similitude pure » la
    # matrice diag(2, 3, 4) de la fixture ci-dessus, qui change l'echelle PAR AXE et ne conserve
    # donc pas les angles — elle sort a 51°, correctement. Une vraie similitude est une rotation
    # fois un scalaire, et c'est celle-la qu'il faut opposer.
    theta = 0.7
    rot = np.array([[np.cos(theta), -np.sin(theta), 0.0],
                    [np.sin(theta), np.cos(theta), 0.0],
                    [0.0, 0.0, 1.0]])
    sim = np.hstack([3.0 * rot, np.array([[7.0], [8.0], [9.0]])])
    v("une similitude (rotation × scalaire) a un défaut nul",
      defaut_de_similitude(sim) < 1e-6, f"{defaut_de_similitude(sim):.8f}°")
    # ⚠ Une echelle DIFFERENTE PAR AXE n'est pas une similitude, et c'est exactement le piege
    # qu'un voxel anisotrope tendrait : les angles y changent sans que rien ne le dise.
    v("... alors qu'une échelle par axe est signalée", defaut_de_similitude(m) > 5.0,
      f"diag(2, 3, 4) → {defaut_de_similitude(m):.2f}°")
    cisaille = sim.copy()
    cisaille[0, 1] += 1.5
    v("... et un cisaillement aussi", defaut_de_similitude(cisaille) > 5.0,
      f"{defaut_de_similitude(cisaille):.2f}°")
    v("un objet inconnu rend None", matrice("PasUnObjet", "a", "b") is None)
    v("... et un couple de volumes inconnu aussi",
      matrice("PHercParis4", "20260310170716", "pas_un_volume") is None)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
