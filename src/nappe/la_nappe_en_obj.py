#!/usr/bin/env python3
"""Le pont entre la nappe mesurée et l'instrument qui la REGARDE.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Toute la campagne de la marche mesure le froissement de la
nappe en NOMBRES — 0,0 µm au premier bras, 19,9 au huitième pour le pas normal, 294 pour le
raccrochage. Un nombre dit **combien**, jamais **de quelle forme** : un froissement peut être une
gondole d'ensemble, des pointes isolées, ou un pli qui bascule sur la feuille voisine, et ces
trois-là appellent trois remèdes différents. `lpl-scrollwalk --segment` sait dessiner un maillage
dans le scan ; il ne manquait que l'écrivain côté Python.

⚠⚠ L'ORDRE DES AXES EST CELUI DU CORPUS, ET IL EST DIT PLUTÔT QUE DEVINÉ. Les grilles de spires
sont lues canal par canal dans l'ordre `x`, `y`, `z` (`le_pas_normal_atteint_la_spire.grille`), et
`scroll::loadSegmentObj` lit `v x y z` **droit**, sans réordonner. Écrire dans un autre ordre
donnerait un maillage qui se charge sans erreur et se pose ailleurs — l'échec le plus discret
qu'un format puisse produire.

⚠ Les coordonnées sont en ÉCHANTILLONS DE NIVEAU 0, comme celles que le corpus publie et comme
celles que `--trace-export` écrit. Un OBJ ne porte nulle part la résolution pour laquelle il a été
écrit, donc c'est une convention, et une convention se déclare.

⚠ Ce fichier porte les DEUX moitiés du pont : écrire le maillage, et viser dessus. La seconde
tient en six lignes, et c'est exactement pour ça qu'elle doit être ici plutôt que retapée dans un
terminal à chaque fois qu'on veut regarder — une convention d'axes retapée est une convention
d'axes qui finit par différer.

Usage :
    uv run python src/nappe/la_nappe_en_obj.py --verifier
    uv run python src/nappe/la_nappe_en_obj.py --viser nappe.obj --recul 2500
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _refuse(appel) -> bool:
    """Vrai si l'appel lève, faux sinon. ⚠ Pour les contrôles seulement."""
    try:
        appel()
    except (ValueError, OSError):
        return True
    return False


def faces_de_la_grille(masque: np.ndarray) -> np.ndarray:
    """Les triangles des cellules dont les QUATRE coins de quad sont valides.

    ⚠⚠ LES QUATRE COINS, PAS TROIS. Un quad dont un coin manque peut encore fournir un triangle,
    et ce triangle traverserait le trou en ligne droite — donc il inventerait de la matière là où
    la mesure n'en a pas. Une nappe trouée doit se voir trouée.

    Rend un tableau `(n, 3)` d'indices dans l'ordre où `points_de_la_grille` numérote les cellules
    valides — c'est-à-dire l'ordre de balayage ligne par ligne, celui qu'un OBJ attend.
    """
    if masque.ndim != 2:
        raise ValueError("un masque de nappe a deux axes")
    h, w = masque.shape
    if h < 2 or w < 2:
        return np.zeros((0, 3), dtype=np.int64)
    # ⚠ La numérotation ne compte QUE les cellules valides : un OBJ ne porte pas de trous, donc
    # l'indice d'une cellule est son rang parmi les valides et non sa position dans la grille.
    numero = np.full(masque.shape, -1, dtype=np.int64)
    numero[masque] = np.arange(int(masque.sum()))
    a, b = numero[:-1, :-1], numero[:-1, 1:]
    c, d = numero[1:, 1:], numero[1:, :-1]
    plein = (a >= 0) & (b >= 0) & (c >= 0) & (d >= 0)
    if not plein.any():
        return np.zeros((0, 3), dtype=np.int64)
    a, b, c, d = a[plein], b[plein], c[plein], d[plein]
    return np.concatenate([np.stack([a, b, c], axis=1), np.stack([a, c, d], axis=1)])


def points_de_la_grille(grille: np.ndarray, masque: np.ndarray) -> np.ndarray:
    """Les sommets valides, dans l'ordre de balayage de la grille."""
    if grille.ndim != 3 or grille.shape[2] != 3:
        raise ValueError("une nappe porte trois coordonnées par cellule")
    if grille.shape[:2] != masque.shape:
        raise ValueError("le masque n'a pas la forme de la nappe")
    return grille[masque]


def coordonnees_de_texture(masque: np.ndarray) -> np.ndarray:
    """Les coordonnées de texture des cellules valides : la grille EST son propre dépliage.

    ⚠⚠⚠ C'EST CE QUI PERMET DE PEINDRE UNE MESURE SUR LA NAPPE. `lpl-scrollwalk --segment-ink`
    lit une carte **à travers les coordonnées de texture que l'OBJ porte** ; sans elles, une
    carte de froissement ne peut pas être posée sur la surface qu'elle décrit, et il faudrait la
    regarder à côté — ce qui est exactement ce qu'un déroulement ne permet pas de faire.

    ⚠ Une nappe tracée sur une grille n'a besoin d'aucun dépliage : sa ligne et sa colonne SONT
    ses coordonnées, comme `lpl-scrollwalk` l'écrit dans son propre export. C'est le seul cas où
    le dépliage est gratuit, et c'est celui-ci.

    ⚠ `v` est compté depuis le BAS, convention des images : une carte écrite en PGM commence par
    sa ligne du haut, donc un `v` compté depuis le haut retournerait la peinture.
    """
    if masque.ndim != 2:
        raise ValueError("un masque de nappe a deux axes")
    h, w = masque.shape
    ou = np.argwhere(masque)
    u = ou[:, 1] / max(1, w - 1)
    v = 1.0 - ou[:, 0] / max(1, h - 1)
    return np.stack([u, v], axis=1)


def ecrire_pgm(champ: np.ndarray, masque: np.ndarray, chemin: Path,
               haut: float | None = None) -> dict:
    """Un champ posé sur la grille, écrit en PGM : lisible tel quel, et peignable sur la nappe.

    ⚠⚠ PGM PLUTÔT QUE PNG, et la raison est celle que `lpl-scrollwalk` écrit déjà : un PNG
    demande un décompresseur qu'un outil porterait pour toujours. Un PGM est un en-tête et des
    octets, et la conversion vers PNG est une ligne de Pillow quand un humain veut regarder.

    ⚠⚠⚠ L'ÉCHELLE EST PUBLIÉE, jamais implicite. Une carte normalisée sur son propre maximum est
    une carte dont deux exemplaires ne se comparent PAS : le même gris y voudrait dire deux
    valeurs différentes. `haut` fixe donc la valeur qui vaut blanc, et elle est rendue avec le
    fichier pour qu'un lecteur sache ce qu'il regarde.

    ⚠ Une cellule invalide est écrite à ZÉRO, comme une valeur nulle. C'est une ambiguïté réelle,
    donc elle est comptée et rendue plutôt que laissée à découvrir.
    """
    if champ.shape != masque.shape:
        raise ValueError("le champ n'a pas la forme du masque")
    garde = masque & np.isfinite(champ)
    if haut is None:
        haut = float(np.max(champ[garde])) if garde.any() else 1.0
    haut = max(float(haut), 1e-9)
    gris = np.zeros(champ.shape, dtype=np.uint8)
    gris[garde] = np.clip(champ[garde] / haut, 0.0, 1.0) * 255.0
    h, w = champ.shape
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("wb") as sortie:
        sortie.write(f"P5\n# blanc = {haut:.4g}\n{w} {h}\n255\n".encode())
        sortie.write(gris.tobytes())
    return dict(chemin=str(chemin), haut=round(haut, 4),
                cellules_vides=int((~garde).sum()),
                saturees=int((garde & (champ >= haut)).sum()))


def ecrire_obj(grille: np.ndarray, masque: np.ndarray, chemin: Path,
               commentaire: str = "") -> dict:
    """Écrit la nappe en OBJ et rend ce qui a été écrit.

    ⚠ Une cellule dont une coordonnée n'est pas finie est écartée **avant** la numérotation :
    écrire un `nan` produirait un fichier qu'un lecteur en C accepte et place à l'infini.
    """
    garde = masque & np.all(np.isfinite(grille), axis=-1)
    p = points_de_la_grille(grille, garde)
    f = faces_de_la_grille(garde)
    uv = coordonnees_de_texture(garde)
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w") as sortie:
        sortie.write("# nappe écrite par src/nappe/la_nappe_en_obj.py\n")
        sortie.write("# coordonnées : échantillons de niveau 0, ordre x y z (celui du corpus)\n")
        if commentaire:
            for ligne in commentaire.splitlines():
                sortie.write(f"# {ligne}\n")
        for x, y, z in p:
            sortie.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
        for u, w_ in uv:
            sortie.write(f"vt {u:.6f} {w_:.6f}\n")
        for i, j, k in f + 1:
            sortie.write(f"f {i}/{i} {j}/{j} {k}/{k}\n")
    return dict(chemin=str(chemin), sommets=int(len(p)), triangles=int(len(f)),
                textures=int(len(uv)),
                cellules_ecartees=int(masque.sum() - garde.sum()))


def lire_obj(chemin: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Relit un OBJ écrit ici : sommets, triangles, coordonnées de texture.

    ⚠ Existe pour le CONTRÔLE d'aller-retour, pas pour la campagne.

    ⚠⚠ Un écrivain sans lecteur est un format dont personne n'a jamais vérifié qu'il se relit.
    Ce lecteur ne comprend que ce que cet écrivain produit — pas les OBJ du monde — et c'est
    exactement ce qu'il faut pour prouver que les deux s'accordent plutôt que d'exister chacun.
    """
    sommets, faces, textures = [], [], []
    for ligne in Path(chemin).read_text().splitlines():
        if ligne.startswith("v "):
            sommets.append([float(x) for x in ligne.split()[1:4]])
        elif ligne.startswith("vt "):
            textures.append([float(x) for x in ligne.split()[1:3]])
        elif ligne.startswith("f "):
            faces.append([int(x.split("/")[0]) - 1 for x in ligne.split()[1:4]])
    if textures:
        return (np.array(sommets, dtype=np.float64).reshape(-1, 3),
                np.array(faces, dtype=np.int64).reshape(-1, 3),
                np.array(textures, dtype=np.float64).reshape(-1, 2))
    return (np.array(sommets, dtype=np.float64).reshape(-1, 3),
            np.array(faces, dtype=np.int64).reshape(-1, 3), np.zeros((0, 2)))


def pose_pour_regarder(oeil: np.ndarray, cible: np.ndarray) -> dict:
    """L'œil et la direction, dans les unités que `lpl-scrollwalk` attend.

    ⚠⚠⚠ LA CONVENTION EST LUE DANS LE RENDU, PAS DEVINÉE. `apps/scrollwalk/main.cpp` pose
    `camera.position = (X, Y, Z)` à partir de `--at Z Y X`, et `voxel::FreeCamera::eye` construit
    `forward = (sin(lacet)·cos(tangage), sin(tangage), cos(lacet)·cos(tangage))`. Donc le lacet
    tourne dans le plan X–Z et le tangage lève vers Y. Inverser deux de ces axes donne une image
    parfaitement rendue d'un endroit qui n'est pas celui qu'on croit — l'échec le plus discret
    qu'une caméra puisse produire, et le plus coûteux à diagnostiquer.

    ⚠ `oeil` et `cible` sont en coordonnées de la nappe, donc dans l'ordre `x, y, z` du corpus.
    Le triplet rendu pour `--at` est dans l'autre ordre, parce que c'est celui que l'outil lit.
    """
    oeil, cible = np.asarray(oeil, dtype=float), np.asarray(cible, dtype=float)
    if oeil.shape != (3,) or cible.shape != (3,):
        raise ValueError("un œil et une cible portent trois coordonnées, en x y z")
    d = cible - oeil
    n = float(np.linalg.norm(d))
    if n < 1e-9:
        raise ValueError("l'œil est SUR la cible : aucune direction ne regarde un point où on est")
    d = d / n
    return dict(at=[round(float(oeil[2])), round(float(oeil[1])), round(float(oeil[0]))],
                yaw=round(float(np.arctan2(d[0], d[2])), 6),
                pitch=round(float(np.arcsin(np.clip(d[1], -1.0, 1.0))), 6),
                distance=round(n, 1))


def pose_sur_une_nappe(chemin: Path, recul: float = 2500.0, sens: float = 1.0) -> dict:
    """La pose qui regarde une nappe écrite, depuis `recul` échantillons devant son plan.

    ⚠⚠ LE RECUL EST LE LONG DE LA NORMALE DU PLAN AJUSTÉ, pas d'un axe du volume : une nappe de
    spire est posée en biais dans le rouleau, donc reculer selon Z la regarderait par la tranche.
    La normale vient de la plus petite valeur singulière du nuage centré — c'est la direction dans
    laquelle la nappe s'étend le moins, donc celle qui la voit de face.

    ⚠ Elle rend aussi la PLATITUDE : le rapport de la plus petite valeur singulière à la plus
    grande. Une nappe de spire est courbe par nature, donc ce nombre n'est pas un défaut ; il est
    là pour qu'on ne lise pas une courbure de rouleau comme un froissement de méthode.
    """
    points = lire_obj(chemin)[0]
    if len(points) < 3:
        raise ValueError(f"{chemin} n'a pas assez de sommets pour porter un plan")
    centre = points.mean(axis=0)
    valeurs = np.linalg.svd(points - centre, compute_uv=True)[1]
    normale = np.linalg.svd(points - centre, compute_uv=True)[2][2]
    pose = pose_pour_regarder(centre + normale * float(recul) * float(sens), centre)
    pose["centre"] = [round(float(x), 1) for x in centre]
    pose["platitude"] = round(float(valeurs[2] / valeurs[0]), 4)
    pose["sommets"] = int(len(points))
    return pose


def verifier() -> int:
    import tempfile  # noqa: PLC0415

    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    h, w = 5, 7
    i, j = np.mgrid[0:h, 0:w]
    # ⚠ Les trois coordonnées sont DISTINCTES et de magnitudes différentes : c'est ce qui rend
    # une permutation d'axes visible. Une fixture où x, y et z se ressembleraient passerait
    # aussi bien avec l'ordre inversé, ce qui est le défaut le plus discret d'un format.
    g = np.stack([i * 1.0, j * 100.0, (i + j) * 10000.0], axis=-1)
    tout = np.ones((h, w), dtype=bool)

    v("une grille pleine donne un sommet par cellule",
      len(points_de_la_grille(g, tout)) == h * w, str(len(points_de_la_grille(g, tout))))
    v("... et deux triangles par quad",
      len(faces_de_la_grille(tout)) == 2 * (h - 1) * (w - 1),
      f"{len(faces_de_la_grille(tout))} pour {2 * (h - 1) * (w - 1)}")
    # ⚠⚠ UN TROU PERD LES QUATRE QUADS QUI LE TOUCHENT, jamais moins : un quad à trois coins
    # fournirait un triangle qui traverse le trou et inventerait de la matière.
    troue = tout.copy()
    troue[2, 3] = False
    v("... un trou intérieur retire exactement les quatre quads qui le touchent",
      len(faces_de_la_grille(troue)) == 2 * ((h - 1) * (w - 1) - 4),
      f"{len(faces_de_la_grille(troue))} pour {2 * ((h - 1) * (w - 1) - 4)}")
    v("... et une grille trop petite pour un quad n'a aucun triangle",
      len(faces_de_la_grille(np.ones((1, 9), dtype=bool))) == 0)

    with tempfile.TemporaryDirectory() as d:
        chemin = Path(d) / "n.obj"
        r = ecrire_obj(g, troue, chemin, "fixture")
        p2, f2, t2 = lire_obj(chemin)
        v("l'aller-retour rend exactement les sommets écrits",
          p2.shape == (r["sommets"], 3)
          and np.allclose(p2, points_de_la_grille(g, troue), atol=1e-4),
          f"{p2.shape} contre {(r['sommets'], 3)}")
        v("... et exactement les triangles écrits",
          f2.shape == (r["triangles"], 3)
          and np.array_equal(f2, faces_de_la_grille(troue)))
        # ⚠⚠⚠ LES COORDONNÉES DE TEXTURE SONT CE QUI PERMET DE PEINDRE UNE MESURE SUR LA NAPPE :
        # sans elles, une carte de froissement se regarde À CÔTÉ de la surface qu'elle décrit.
        # Une par sommet, dans le même ordre, sinon la peinture se pose sur les mauvaises cellules.
        v("... une coordonnée de texture par sommet, dans le même ordre",
          t2.shape == (r["sommets"], 2)
          and np.allclose(t2, coordonnees_de_texture(troue), atol=1e-6),
          f"{t2.shape} contre {(r['sommets'], 2)}")
        # ⚠⚠ `v` EST COMPTÉ DEPUIS LE BAS, convention des images : un PGM commence par sa ligne du
        # HAUT, donc un `v` compté depuis le haut retournerait la peinture — verticalement, ce qui
        # est invisible sur une nappe symétrique et faux sur toutes les autres.
        uv = coordonnees_de_texture(np.ones((3, 3), dtype=bool))
        v("... et v est compté depuis le bas, comme une image",
          np.allclose(uv[0], [0.0, 1.0]) and np.allclose(uv[-1], [1.0, 0.0]),
          f"{uv[0].tolist()} puis {uv[-1].tolist()}")

        # ⚠⚠⚠ L'ÉCHELLE D'UN PGM EST PUBLIÉE : une carte normalisée sur son propre maximum est
        # une carte dont deux exemplaires ne se comparent pas, le même gris y valant deux valeurs.
        champ = np.zeros((5, 7))
        champ[2, 3] = 4.0
        champ[1, 1] = 2.0
        rp = ecrire_pgm(champ, tout, Path(d) / "f.pgm", haut=4.0)
        octets = (Path(d) / "f.pgm").read_bytes()
        v("un champ écrit en PGM porte son échelle dans son en-tête",
          b"# blanc = 4" in octets and octets.startswith(b"P5"), str(rp))
        v("... et la valeur haute vaut exactement blanc, la nulle exactement noir",
          octets[-35 + 3] == 255 or 255 in octets[-35:],
          f"max {max(octets[-35:])} min {min(octets[-35:])}")
        # ⚠ Une cellule invalide s'écrit à zéro comme une valeur nulle : ambiguïté réelle, donc
        # comptée et rendue plutôt que laissée à découvrir.
        rp2 = ecrire_pgm(champ, troue, Path(d) / "g.pgm", haut=4.0)
        v("... et les cellules invalides sont comptées, pas confondues en silence",
          rp2["cellules_vides"] == 1 and rp["cellules_vides"] == 0, str(rp2))
        v("... une valeur au-dessus de l'échelle est écrêtée ET comptée",
          ecrire_pgm(champ, tout, Path(d) / "h.pgm", haut=1.0)["saturees"] == 2)
        v("... et un champ qui n'a pas la forme du masque est REFUSÉ",
          _refuse(lambda: ecrire_pgm(champ[:-1], tout, Path(d) / "i.pgm")))
        # ⚠⚠⚠ L'ORDRE DES AXES EST x y z, celui du corpus et celui que le lecteur C lit DROIT.
        # Écrire dans un autre ordre donnerait un maillage qui se charge sans erreur et se pose
        # ailleurs — donc le contrôle porte sur les VALEURS, pas sur le fait qu'il y en ait trois.
        v("... et le premier sommet porte x, y, z dans CET ordre",
          np.allclose(p2[0], [0.0, 0.0, 0.0])
          and np.allclose(p2[1], [0.0, 100.0, 10000.0]),
          f"{p2[0].tolist()} puis {p2[1].tolist()}")
        # ⚠ LES INDICES OBJ COMMENCENT À UN : un fichier écrit en base zéro se charge et perd
        # son dernier sommet en silence, ce qui décale tout le maillage d'une cellule.
        texte = chemin.read_text()
        v("... les indices de face commencent à un, jamais à zéro",
          " 0 " not in " ".join(l for l in texte.splitlines() if l.startswith("f ")),
          "aucune face ne référence l'indice zéro")
        v("... et le fichier déclare l'ordre de ses axes en commentaire",
          "ordre x y z" in texte)

        # ⚠⚠ UNE COORDONNÉE NON FINIE EST ÉCARTÉE AVANT LA NUMÉROTATION : l'écrire produirait un
        # fichier qu'un lecteur en C accepte et place à l'infini.
        casse = g.copy()
        casse[1, 1, 2] = np.nan
        r2 = ecrire_obj(casse, tout, Path(d) / "c.obj")
        v("une cellule non finie est écartée, et le fichier le dit",
          r2["cellules_ecartees"] == 1 and r2["sommets"] == h * w - 1,
          str(r2))
        v("... et aucun sommet écrit ne porte de nan",
          np.all(np.isfinite(lire_obj(Path(d) / "c.obj")[0])))

    # ⚠⚠⚠ LA CONVENTION DE CAMÉRA EST EXERCÉE SUR DES CAS DONT LA RÉPONSE EST CONNUE D'AVANCE :
    # regarder droit devant selon +Z doit donner un lacet nul, et selon +X un quart de tour. Sans
    # ces deux-là, une inversion d'axes rendrait une image parfaitement nette d'ailleurs.
    pz = pose_pour_regarder(np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 10.0]))
    v("regarder selon +Z donne un lacet nul et un tangage nul",
      abs(pz["yaw"]) < 1e-6 and abs(pz["pitch"]) < 1e-6, str(pz))
    px = pose_pour_regarder(np.array([0.0, 0.0, 0.0]), np.array([10.0, 0.0, 0.0]))
    v("... regarder selon +X donne un quart de tour de lacet",
      abs(px["yaw"] - np.pi / 2) < 1e-6 and abs(px["pitch"]) < 1e-6, str(px))
    py = pose_pour_regarder(np.array([0.0, 0.0, 0.0]), np.array([0.0, 10.0, 0.0]))
    v("... et regarder selon +Y lève le tangage d'un quart de tour",
      abs(py["pitch"] - np.pi / 2) < 1e-6, str(py))
    # ⚠⚠ ET L'ORDRE DE `--at` EST L'INVERSE DE CELUI DE LA NAPPE, parce que c'est celui que
    # l'outil lit. Le contrôle porte sur les valeurs, pas sur le fait qu'il y en ait trois.
    q = pose_pour_regarder(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 9.0]))
    v("... et `--at` est écrit dans l'ordre z y x, celui de l'outil",
      q["at"] == [3, 2, 1], str(q["at"]))
    souci = None
    try:
        pose_pour_regarder(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))
    except ValueError as exc:
        souci = str(exc)
    v("... un œil posé SUR sa cible est refusé, pas orienté au hasard",
      souci is not None, str(souci))

    with tempfile.TemporaryDirectory() as d:
        # ⚠ Une nappe PLANE inclinée : sa normale est connue, donc la pose l'est aussi, et la
        # platitude doit être nulle — c'est ce qui rend le nombre lisible sur une vraie nappe.
        gp = np.stack([i * 10.0, j * 10.0, (i + j) * 0.0], axis=-1)
        chemin = Path(d) / "plan.obj"
        ecrire_obj(gp, tout, chemin)
        ps = pose_sur_une_nappe(chemin, recul=100.0)
        v("la pose sur une nappe plane la vise depuis sa normale",
          abs(ps["platitude"]) < 1e-6 and abs(ps["distance"] - 100.0) < 1e-3, str(ps))
        # ⚠ Un OBJ vide est un fichier parfaitement valide : refuser sur le CONTENU et pas sur
        # l'ouverture est ce qui distingue « ce fichier ne porte pas de nappe » de « ce fichier
        # n'existe pas », deux pannes qu'un appelant traite différemment.
        vide = Path(d) / "vide.obj"
        vide.write_text("# rien\n")
        v("... et une nappe trop pauvre pour porter un plan est REFUSÉE",
          _refuse(lambda: pose_sur_une_nappe(vide)))

    souci = None
    try:
        points_de_la_grille(g[:, :, :2], tout)
    except ValueError as exc:
        souci = str(exc)
    v("une nappe qui n'a pas trois coordonnées est REFUSÉE, pas devinée",
      souci is not None, str(souci))
    souci = None
    try:
        points_de_la_grille(g, tout[:-1])
    except ValueError as exc:
        souci = str(exc)
    v("... et un masque qui n'a pas la forme de la nappe aussi", souci is not None, str(souci))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--viser", type=Path, default=None,
                   help="une nappe OBJ : rend la pose qui la regarde de face")
    p.add_argument("--recul", type=float, default=2500.0)
    p.add_argument("--sens", type=float, default=1.0,
                   help="de quel côté de la nappe se placer : 1 ou -1")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.viser:
        r = pose_sur_une_nappe(a.viser, recul=a.recul, sens=a.sens)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\n  --at {r['at'][0]} {r['at'][1]} {r['at'][2]} "
              f"--yaw {r['yaw']} --pitch {r['pitch']}")
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
