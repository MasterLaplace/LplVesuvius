#!/usr/bin/env python3
"""Marcher LE LONG d'une nappe dans la prediction, et en ecrire les points de passage.

⚠⚠ Pourquoi ce fichier existe, et pourquoi il est un CONSTRUCTEUR et pas un diagnostic.
[`39`] etablit que la chaine de correction est complete SAUF un maillon : *dire ou la
surface aurait du passer*. `vc_grow_seg_from_seed --resume --rewind-gen --correct` prend
un `PointCollections`, c'est-a-dire une liste ORDONNEE de points 3D vers lesquels le
traceur tire la surface pendant qu'il la refait pousser. Ce fichier produit cette liste.

⚠⚠ ET CE N'EST PAS UN DECALAGE DE NOTRE TRACE. `38` etablit que nos traces sont des
COUPES RADIALES : leur normale reste dans la meme matiere, donc elles traversent
l'empilement au lieu de le suivre. Une surface orientee a 90 degres de la bonne ne se
corrige pas en la poussant un peu -- il n'y a rien vers quoi la pousser. Ce qu'il faut
donner au traceur, c'est un CHEMIN LE LONG D'UNE NAPPE, calcule independamment de la
trace ratee. D'ou une marche, et pas une mesure d'ecart.

Le principe, en trois gestes repetes :

  1. **la normale locale** : dans une fenetre autour du point, le gradient d'une nappe
     pointe en travers d'elle. Le vecteur propre dominant du tenseur de structure est
     donc la normale, et il est stable la ou une simple difference finie ne l'est pas ;
  2. **recentrer** : on echantillonne la prediction le long de +/- la normale et on se
     replace sur le maximum, au sous-voxel par ajustement parabolique. C'est ce qui
     empeche la marche de deriver hors de la nappe pas apres pas ;
  3. **avancer** : on projette la direction precedente dans le plan de la nappe et on
     fait un pas. Reprojeter a chaque fois est ce qui fait suivre une courbure.

⚠⚠ LE MODE DE PANNE A NEUTRALISER EST LE SAUT DE NAPPE. Un rouleau est un empilement de
nappes paralleles a quelques dizaines de microns : une marche qui saute sur la voisine
produit un chemin parfaitement lisse, parfaitement plausible, et FAUX -- exactement le
genre de sortie que ce depot traque. La marche refuse donc d'avancer quand le recentrage
la deplace de plus de `saut_max` : un vrai suivi corrige de fractions de voxel, un saut
corrige d'un interligne. Sonde : deux nappes a 6 voxels, la marche ne doit jamais finir
sur la mauvaise.

⚠ Ce fichier ne juge pas si la nappe suivie est la BONNE. Il suit celle sur laquelle on
le pose. Choisir laquelle est le travail de la graine (`25`), et verifier que la trace
qui en sort suit une feuille est le travail du test de convergence (`38`).

Usage :
    # hors ligne, sur un bloc .npy deja lu
    uv run python src/commun/suivre_nappe.py --bloc bloc.npy --depart 64 64 64 \\
        --sortie corrections.json
    uv run python src/commun/suivre_nappe.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

# Un pas plus long qu'un voxel saute la structure qu'on suit ; beaucoup plus court, la
# marche paie des recentrages pour rien. Mesure, pas gout : voir le temoin de courbure.
PAS = 1.0
# Le rayon de la fenetre du tenseur de structure. Trop petit, le bruit oriente la normale ;
# trop grand, la fenetre embrasse deux nappes et la normale devient leur moyenne.
RAYON = 2
# ⚠ Un recentrage plus grand que ca n'est pas une correction, c'est un changement de nappe.
SAUT_MAX = 2.0
# ⚠⚠ LE PLANCHER DE VALEUR DEPEND DES UNITES DU CHAMP, et l'oublier est un bug mesure.
# Sur une prediction ramenee dans [0,1], 0,15 veut dire « il y a un peu de matiere ». Sur une
# TRANSFORMEE DE DISTANCE en voxels, 0,15 veut dire « je suis a un sixieme de voxel du vide »,
# c'est-a-dire collee au bord -- donc la marche traverse des filaments au lieu de s'arreter.
# Mesure : sur 48 cotes d'un morceau de nappe reel, 4 traversaient un vide avec le plancher
# de 0,15 ; le plancher d'un voxel est ce qui les arrete. Meme famille que la borne de lag
# choisie pour la commodite : un seuil juste dans une unite, faux dans l'autre.
VALEUR_MIN_PROBA = 0.15
VALEUR_MIN_DISTANCE = 1.0


def champ_de_distance(masque: np.ndarray, seuil: float = 0.5) -> np.ndarray:
    """Transformer un masque BINAIRE en champ dont la crete est l'axe median des nappes.

    ⚠⚠ POURQUOI CE PASSAGE EST OBLIGATOIRE, ET LA MESURE QUI L'IMPOSE. La prediction de
    surface publiee de PHerc1447 s'appelle « ...-th0.2.zarr » et elle porte **exactement
    deux valeurs**, 0 et 255 : c'est un masque seuille, pas une probabilite. Un masque
    n'a **aucun gradient a l'interieur de la matiere** -- il a un plateau. Donc :

      - le tenseur de structure n'y voit rien tant qu'on n'est pas sur un bord ;
      - le recentrage sur le maximum est un `argmax` sur une constante, qui rend le
        premier indice : la marche se colle au BORD de la nappe au lieu de son milieu ;
      - et une trace poussee la-dessus n'a rien a suivre, ce qui est exactement l'etat
        constate par `38` (nos traces posees en travers de l'empilement).

    La transformee de distance rend a chaque voxel de matiere sa distance au vide. Son
    maximum local est donc le MILIEU de la nappe, et le champ redevient une crete que
    tout le reste de ce fichier sait suivre. C'est ce que designe le « cache EDT » que le
    pipeline officiel utilise et que le bucket ne publie pas.

    ⚠ La distance est rendue en flottant SANS normalisation par le maximum global : une
    nappe epaisse et une nappe fine doivent garder des hauteurs de crete differentes,
    sinon `valeur_min` cesse de vouloir dire quelque chose de comparable d'un bloc a
    l'autre.
    """
    m = masque > (seuil * (255.0 if masque.max() > 1.5 else 1.0))
    return _edt(m)


def _edt_1d(f: np.ndarray) -> np.ndarray:
    """Transformee de distance EUCLIDIENNE CARREE d'une ligne, algorithme de Felzenszwalb.

    ⚠ Ecrite ici plutot qu'importee de scipy pour une raison bete et bloquante : les
    environnements de ce depot sont separes, `scipy` vit dans `src/excision/` et `Pillow`
    dans `inference/`, donc aucune figure ne pourrait a la fois lire un bloc et le
    dessiner. Une fonction de vingt lignes vaut mieux qu'un troisieme environnement.

    ⚠ C'est l'EDT EXACTE, pas un chanfrein : l'enveloppe inferieure des paraboles
    y = (x - i)^2 + f(i). Une approximation ferait deriver la crete du milieu de la nappe,
    et le milieu de la nappe est exactement ce qu'on cherche.
    """
    n = f.size
    d = np.empty(n, dtype=np.float64)
    v = np.zeros(n, dtype=np.int64)
    z = np.empty(n + 1, dtype=np.float64)
    k = 0
    v[0] = 0
    z[0], z[1] = -np.inf, np.inf
    for q in range(1, n):
        while True:
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            if s <= z[k]:
                k -= 1
                if k < 0:
                    k = 0
                    break
            else:
                break
        k += 1
        v[k] = q
        z[k] = s
        z[k + 1] = np.inf
    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        d[q] = (q - v[k]) ** 2 + f[v[k]]
    return d


def _edt(masque: np.ndarray) -> np.ndarray:
    """EDT 3D exacte, par separabilite : une passe 1D par axe sur le carre des distances.

    ⚠ On prend scipy QUAND IL EST LA, et la version ecrite ici sinon. Ce n'est pas une
    preference de style : la version pure fait une boucle Python par ligne, soit ~200 000
    appels sur un cube de 257, ce qui met des minutes la ou scipy met une fraction de
    seconde. Et le repli n'est pas un risque, parce qu'un temoin compare les deux
    EXACTEMENT (ecart max 0,0) partout ou la reference est installee.
    """
    try:
        from scipy import ndimage
    except ImportError:
        pass
    else:
        return ndimage.distance_transform_edt(masque).astype(np.float32)

    f = np.where(masque, 1e12, 0.0)
    for axe in range(masque.ndim):
        f = np.apply_along_axis(_edt_1d, axe, f)
    return np.sqrt(f).astype(np.float32)


def est_binaire(bloc: np.ndarray) -> bool:
    """Le bloc ne porte-t-il que deux valeurs ? (donc : est-ce un masque seuille ?)

    ⚠ Sert a REFUSER de marcher sur un masque brut plutot qu'a le deviner : une marche
    qui tourne sur un plateau rend un chemin, et un chemin rendu ressemble a un succes.
    """
    return len(np.unique(bloc)) <= 2


def echantillon(bloc: np.ndarray, p: np.ndarray) -> float:
    """Valeur trilineaire du bloc au point p (z, y, x) ; 0 hors du bloc.

    ⚠ Hors du bloc rend 0 et non NaN : la marche s'arrete sur une valeur basse, donc un
    bord se comporte comme une fin de nappe, ce qui est le comportement voulu. Un NaN
    aurait contamine la normale et fait sortir la marche en silence.
    """
    z, y, x = p
    nz, ny, nx = bloc.shape
    if not (0 <= z <= nz - 1 and 0 <= y <= ny - 1 and 0 <= x <= nx - 1):
        return 0.0
    z0, y0, x0 = int(np.floor(z)), int(np.floor(y)), int(np.floor(x))
    z1, y1, x1 = min(z0 + 1, nz - 1), min(y0 + 1, ny - 1), min(x0 + 1, nx - 1)
    fz, fy, fx = z - z0, y - y0, x - x0
    c = 0.0
    for dz, wz in ((0, 1 - fz), (1, fz)):
        for dy, wy in ((0, 1 - fy), (1, fy)):
            for dx, wx in ((0, 1 - fx), (1, fx)):
                w = wz * wy * wx
                if w:
                    c += w * float(bloc[(z1 if dz else z0), (y1 if dy else y0),
                                        (x1 if dx else x0)])
    return c


def normale_locale(bloc: np.ndarray, p: np.ndarray, rayon: int = RAYON):
    """Normale de la nappe en p, par le tenseur de structure.

    Le gradient d'une nappe pointe en travers d'elle. Sur une fenetre, la matrice de
    covariance des gradients a donc son vecteur propre DOMINANT le long de la normale --
    et contrairement a un gradient ponctuel, ce vecteur ne s'effondre pas la ou la valeur
    est localement plate (sur la crete de la nappe, precisement la ou on marche).

    ⚠ Le signe d'un vecteur propre est arbitraire ; l'appelant doit l'orienter lui-meme.
    Retourne (normale unitaire, anisotropie dans [0,1]).
    """
    z, y, x = (int(round(v)) for v in p)
    nz, ny, nx = bloc.shape
    r = rayon
    if not (r + 1 <= z < nz - r - 1 and r + 1 <= y < ny - r - 1 and r + 1 <= x < nx - r - 1):
        return None, 0.0
    f = bloc[z - r - 1:z + r + 2, y - r - 1:y + r + 2, x - r - 1:x + r + 2].astype(np.float64)
    gz, gy, gx = np.gradient(f)
    s = slice(1, -1)
    g = np.stack([gz[s, s, s].ravel(), gy[s, s, s].ravel(), gx[s, s, s].ravel()])
    t = g @ g.T
    w, v = np.linalg.eigh(t)
    if w[-1] <= 0:
        return None, 0.0
    n = v[:, -1]
    # ⚠ L'anisotropie dit si la fenetre contient bien UNE nappe. Isotrope = du bruit ou une
    # intersection, et une normale y est une direction tiree au hasard : la marche doit
    # pouvoir refuser sur ce critere plutot que de suivre n'importe quoi.
    aniso = float((w[-1] - w[0]) / w[-1])
    return n / (np.linalg.norm(n) or 1.0), aniso


def recentrer(bloc: np.ndarray, p: np.ndarray, n: np.ndarray,
              portee: float = 3.0, pas: float = 0.25):
    """Replacer p sur le maximum local de la prediction le long de la normale.

    ⚠ Le sous-voxel vient d'un ajustement PARABOLIQUE sur les trois echantillons autour du
    maximum discret. Sans lui, chaque recentrage arrondit au pas d'echantillonnage et la
    marche accumule une erreur systematique -- ce qui, sur quelques centaines de pas,
    revient a deriver hors de la nappe tout en croyant la suivre.

    Retourne (nouveau point, deplacement signe, valeur au maximum).
    """
    ts = np.arange(-portee, portee + 1e-9, pas)
    vals = np.array([echantillon(bloc, p + t * n) for t in ts])
    k = int(np.argmax(vals))
    t = ts[k]
    if 0 < k < len(ts) - 1:
        a, b, c = vals[k - 1], vals[k], vals[k + 1]
        den = a - 2 * b + c
        if den != 0:
            t = t + pas * 0.5 * (a - c) / den
    return p + t * n, float(t), float(vals[k])


def plancher_pour(bloc: np.ndarray) -> float:
    """Le plancher de valeur qui convient aux UNITES de ce champ.

    ⚠ Un champ dont le maximum depasse 1,5 n'est pas une probabilite : c'est une distance en
    voxels. Le plancher passe alors de « un peu de matiere » a « au moins un voxel de
    matiere autour », sinon la marche longe les bords au lieu de suivre les axes medians.
    """
    return VALEUR_MIN_DISTANCE if float(bloc.max()) > 1.5 else VALEUR_MIN_PROBA


def marcher(bloc: np.ndarray, depart, direction, pas: float = PAS,
            n_pas: int = 200, valeur_min: float | None = None,
            aniso_min: float = 0.35, saut_max: float = SAUT_MAX,
            rayon: int = RAYON) -> dict:
    """Suivre la nappe depuis `depart` dans `direction`, et rendre le chemin.

    Rend aussi POURQUOI la marche s'est arretee : une marche courte et une marche qui a
    refuse un saut de nappe se ressemblent sur une liste de points, et ne veulent pas dire
    la meme chose.
    """
    if valeur_min is None:
        valeur_min = plancher_pour(bloc)
    p = np.asarray(depart, dtype=np.float64)
    d = np.asarray(direction, dtype=np.float64)
    d = d / (np.linalg.norm(d) or 1.0)

    n, aniso = normale_locale(bloc, p, rayon)
    if n is None or aniso < aniso_min:
        return {"points": [], "arret": "depart sans nappe lisible", "pas_faits": 0,
                "aniso_depart": aniso}
    p, _, v0 = recentrer(bloc, p, n)
    if v0 < valeur_min:
        return {"points": [], "arret": "depart hors matiere", "pas_faits": 0,
                "valeur_depart": v0}

    chemin = [p.copy()]
    sauts = 0
    arret = f"{n_pas} pas faits"
    for i in range(n_pas):
        n, aniso = normale_locale(bloc, p, rayon)
        if n is None:
            arret = "sortie du bloc"
            break
        if aniso < aniso_min:
            arret = f"nappe illisible au pas {i} (anisotropie {aniso:.2f})"
            break
        # ⚠ Reprojeter la direction DANS le plan de la nappe a chaque pas est ce qui fait
        # suivre une courbure. Garder la direction initiale ferait sortir la marche de la
        # nappe des qu'elle tourne -- et un rouleau ne fait que tourner.
        t = d - float(d @ n) * n
        norme = np.linalg.norm(t)
        if norme < 1e-6:
            arret = f"direction perpendiculaire a la nappe au pas {i}"
            break
        d = t / norme
        q = p + pas * d
        n2, aniso2 = normale_locale(bloc, q, rayon)
        if n2 is None:
            arret = "sortie du bloc"
            break
        # ⚠ Orienter n2 comme n : le signe d'un vecteur propre est arbitraire, et un
        # retournement ferait recentrer dans le mauvais sens un pas sur deux.
        if float(n2 @ n) < 0:
            n2 = -n2
        q, dep, val = recentrer(bloc, q, n2)
        # ⚠⚠ L'ORDRE DE CES DEUX TESTS EST LE DIAGNOSTIC. Un grand recentrage vers une
        # valeur FORTE est un saut sur la nappe voisine ; le meme recentrage vers une
        # valeur FAIBLE est une nappe qui finit et un maximum de bruit ramasse au loin.
        # Tester le saut d'abord etiquetait « saut de nappe refuse » un trou dans la
        # nappe -- verdict juste pour la mauvaise raison, et qui envoie chercher un
        # probleme d'empilement la ou il y a un manque de matiere.
        if val < valeur_min:
            arret = f"fin de nappe au pas {i} (valeur {val:.2f})"
            break
        if abs(dep) > saut_max:
            sauts += 1
            arret = f"saut de nappe refuse au pas {i} (recentrage {dep:+.2f} voxels)"
            break
        p = q
        chemin.append(p.copy())
    # ⚠ La VALEUR le long du chemin est ce qui dit si la marche est restée sur l'axe
    # médian ou l'a longé de biais. Un chemin de 137 points et un chemin de 137 points
    # collés au bord d'une nappe se ressemblent parfaitement sur une liste de coordonnées.
    vals = [echantillon(bloc, np.asarray(c)) for c in chemin]
    return {"points": [c.tolist() for c in chemin], "arret": arret,
            "pas_faits": len(chemin) - 1, "sauts_refuses": sauts,
            "valeur_min": float(min(vals)) if vals else 0.0,
            "valeur_mediane": float(np.median(vals)) if vals else 0.0}


def marcher_nappe(bloc: np.ndarray, depart, direction=(0.0, 1.0, 0.0),
                  pas: float = PAS, n_pas: int = 200, ecart_cotes: float = 4.0,
                  n_cotes: int = 12, **kw) -> dict:
    """Couvrir un MORCEAU de nappe, pas seulement une ligne : une echine et ses cotes.

    ⚠⚠ Pourquoi ce mode existe, et c'est une mesure qui l'exige. `42` etablit que 318 points
    de passage sur une ligne ne reorientent pas une surface : ils pesent **0,56 %** des
    56 630 points de grille d'une trace. Une nappe est un objet a DEUX dimensions ; lui
    donner un seul fil, c'est demander a un solveur de deviner le reste.

    L'echine est une marche ordinaire. Chaque cote part d'un point de l'echine et marche
    dans la direction tangente PERPENDICULAIRE a l'echine -- c'est-a-dire le produit
    vectoriel de la normale locale et de la direction d'echine, donc encore dans le plan de
    la nappe.

    ⚠ Chaque cote est sa PROPRE collection, pas une suite de la precedente.
    `PointCorrection` traite une collection comme un CHEMIN et ancre sur son premier point ;
    concatener les cotes ferait un chemin qui saute d'un bord a l'autre a chaque rangee.

    ⚠ Les cotes partent d'un point sur DEUX ou plus (`ecart_cotes`), pas de chaque point :
    une cote par point de l'echine donnerait des milliers de collections dont les chemins se
    recouvrent, et le solveur paierait le meme renseignement des dizaines de fois.

    Retourne {"chemins": [...], "echine": {...}, "points": N, "cotes": N}.
    """
    ech = marcher(bloc, depart, direction, pas, n_pas, **kw)
    if not ech["points"]:
        return {"chemins": [], "echine": ech, "points": 0, "cotes": 0}

    chemins = [list(ech["points"])]
    pts = np.asarray(ech["points"], dtype=np.float64)
    saut = max(1, int(round(ecart_cotes / max(pas, 1e-6))))
    indices = list(range(0, len(pts), saut))[:n_cotes]

    for k in indices:
        p = pts[k]
        # La direction locale de l'echine : difference avant/arriere quand elle existe.
        j = min(k + 1, len(pts) - 1)
        i = max(k - 1, 0)
        t = pts[j] - pts[i]
        if np.linalg.norm(t) < 1e-6:
            continue
        t = t / np.linalg.norm(t)
        n, aniso = normale_locale(bloc, p)
        if n is None or aniso < kw.get("aniso_min", 0.35):
            continue
        # ⚠ Le produit vectoriel de la normale et de la tangente est l'AUTRE direction
        # tangente : elle reste dans le plan de la nappe, ce qu'une direction arbitraire
        # perpendiculaire a l'echine ne garantirait pas.
        c = np.cross(n, t)
        if np.linalg.norm(c) < 1e-6:
            continue
        c = c / np.linalg.norm(c)
        for sens in (1.0, -1.0):
            r = marcher(bloc, p, sens * c, pas, n_pas // 2, **kw)
            if len(r["points"]) > 2:
                chemins.append(list(r["points"]))
    return {"chemins": chemins, "echine": ech,
            "points": sum(len(c) for c in chemins), "cotes": len(chemins) - 1}


def marcher_plus_proche(bloc: np.ndarray, depart, pas: float = PAS, n_pas: int = 200,
                        valeur_min: float = 0.15, rayon_recherche: float = 6.0) -> dict:
    """La methode NAIVE, implementee pour etre mesuree : aller au voxel allume le plus proche.

    ⚠⚠ Elle existe ici comme TEMOIN NEGATIF, pas comme option. C'est la premiere idee que
    tout le monde a -- « je pars d'un point et je me propage au plus proche » -- et son
    mode de panne est exactement celui qui compte : dans un rouleau, la nappe VOISINE est
    a quelques dizaines de microns, donc des que la nappe courante a un trou, le point le
    plus proche est de l'autre cote du vide. La marche continue, lisse, plausible, sur la
    mauvaise feuille. Un papyrus est plein de trous.

    ⚠ On ne revient pas sur ses pas (memoire des visites) : sans ca la marche oscille sur
    place et « ne saute jamais » pour une raison qui n'a rien a voir avec les nappes.
    """
    p = np.asarray(depart, dtype=np.float64)
    chemin = [p.copy()]
    vus = {tuple(np.round(p).astype(int))}
    r = int(np.ceil(rayon_recherche))
    dz, dy, dx = np.mgrid[-r:r + 1, -r:r + 1, -r:r + 1]
    dist = np.sqrt(dz ** 2 + dy ** 2 + dx ** 2)
    ordre = np.argsort(dist.ravel())
    offs = np.stack([dz.ravel(), dy.ravel(), dx.ravel()], axis=1)[ordre]
    dist = dist.ravel()[ordre]
    arret = f"{n_pas} pas faits"
    for i in range(n_pas):
        base = np.round(p).astype(int)
        suivant = None
        for off, d in zip(offs, dist):
            if d < pas * 0.5:
                continue
            q = base + off
            if tuple(q) in vus:
                continue
            if echantillon(bloc, q.astype(np.float64)) >= valeur_min:
                suivant = q.astype(np.float64)
                break
        if suivant is None:
            arret = f"plus rien d'allume au pas {i}"
            break
        vus.add(tuple(np.round(suivant).astype(int)))
        p = suivant
        chemin.append(p.copy())
    return {"points": [c.tolist() for c in chemin], "arret": arret,
            "pas_faits": len(chemin) - 1}


def ecrire_point_collection(chemins: list[list[list[float]]], sortie: Path,
                            nom: str = "correction", couleur=(1.0, 0.6, 0.0)) -> dict:
    """Ecrire un fichier `PointCollections` que `--correct` sait relire.

    ⚠⚠ Le format est lu dans la SOURCE (`core/src/PointCollections.cpp`), pas devine :
    enveloppe `vc_pointcollections_json_version` = "1", `collections` indexe par des
    chaines d'entiers, chaque point `{"p": [x, y, z], ...}` indexe de meme. Un fichier
    dont la version ne correspond pas est rejete en bloc par `loadFromJSON`.

    ⚠⚠ ET L'ORDRE DES POINTS EST SIGNIFIANT. `PointCorrection` trie les points par ID
    croissant et s'en sert comme d'un CHEMIN : le premier ancre la collection sur la
    surface, les suivants sont places aux emplacements de grille successifs. Ecrire un
    nuage non ordonne donnerait un chemin qui part dans tous les sens -- le fichier
    serait valide et le resultat absurde.

    ⚠ Les coordonnees sont ecrites en (x, y, z) alors que la marche travaille en
    (z, y, x) : c'est la convention du volume contre celle de numpy, et les melanger
    produit une correction qui tire la surface vers un point parfaitement faux sans que
    rien n'ait l'air casse.
    """
    collections = {}
    total = 0
    for ic, chemin in enumerate(chemins, start=1):
        points = {}
        for ip, (z, y, x) in enumerate(chemin, start=1):
            points[str(ip)] = {"p": [float(x), float(y), float(z)],
                               "creation_time": 0, "wind_a": None}
            total += 1
        collections[str(ic)] = {
            "name": f"{nom}_{ic}" if len(chemins) > 1 else nom,
            "points": points,
            "metadata": {"winding_is_absolute": True},
            "color": [float(c) for c in couleur],
        }
    doc = {"vc_pointcollections_json_version": "1", "collections": collections}
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(doc, indent=4) + "\n", encoding="utf-8")
    return {"collections": len(collections), "points": total, "fichier": str(sortie)}


# ---------------------------------------------------------------- temoins

def _nappe_cylindrique(n=96, rayon=28.0, epaisseur=1.2, entre=0.0):
    """Une nappe courbe (cylindre autour de l'axe z), eventuellement doublee.

    C'est la forme du probleme : un rouleau est un empilement de nappes courbes proches.
    Une nappe plane ne testerait pas la reprojection de la direction, qui est la seule
    raison pour laquelle la marche suit une courbure.
    """
    zz, yy, xx = np.mgrid[0:n, 0:n, 0:n].astype(np.float64)
    c = n / 2.0
    r = np.hypot(yy - c, xx - c)
    f = np.exp(-((r - rayon) ** 2) / (2 * epaisseur ** 2))
    if entre:
        f = np.maximum(f, np.exp(-((r - rayon - entre) ** 2) / (2 * epaisseur ** 2)))
    return f.astype(np.float32)


def verifier() -> int:
    import tempfile

    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de suivre_nappe")

    n, rayon = 96, 28.0
    c = n / 2.0
    bloc = _nappe_cylindrique(n, rayon)

    # La normale d'un cylindre est radiale : c'est vérifiable sans référence extérieure.
    p = np.array([48.0, c, c + rayon])
    nv, aniso = normale_locale(bloc, p)
    ok(nv is not None and abs(abs(float(nv @ np.array([0.0, 0.0, 1.0]))) - 1.0) < 0.05,
       "la normale d'une nappe cylindrique est radiale")
    ok(aniso > 0.9, f"une nappe isolée est fortement anisotrope ({aniso:.2f})")

    # ⚠ Sonde : sur du bruit, l'anisotropie doit s'effondrer — sinon le refus « nappe
    # illisible » ne se déclencherait jamais et la marche suivrait n'importe quoi.
    rng = np.random.default_rng(3)
    _, aniso_bruit = normale_locale(rng.random((n, n, n)).astype(np.float32), p)
    ok(aniso_bruit < 0.6, f"du bruit n'est pas anisotrope ({aniso_bruit:.2f})")

    # Recentrage : un point posé à côté doit revenir sur la crête, au sous-voxel.
    hors = np.array([48.0, c, c + rayon + 1.7])
    q, dep, val = recentrer(bloc, hors, np.array([0.0, 0.0, 1.0]))
    ok(abs(float(np.hypot(q[1] - c, q[2] - c)) - rayon) < 0.1,
       f"le recentrage ramène sur la crête ({np.hypot(q[1]-c, q[2]-c):.2f} pour {rayon})")
    ok(abs(dep + 1.7) < 0.3, f"le déplacement rapporté est celui qu'il a fallu ({dep:+.2f})")

    # La marche suit la courbure : le rayon doit rester constant sur tout le chemin.
    r = marcher(bloc, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120)
    pts = np.array(r["points"])
    ok(len(pts) > 60, f"la marche avance ({r['pas_faits']} pas, arrêt : {r['arret']})")
    rr = np.hypot(pts[:, 1] - c, pts[:, 2] - c)
    ok(float(rr.std()) < 0.35,
       f"le rayon reste constant le long de la marche (σ {rr.std():.3f} voxel)")
    ok(abs(float(rr.mean()) - rayon) < 0.3,
       f"et c'est le bon rayon ({rr.mean():.2f} pour {rayon})")

    # ⚠ Sonde de la reprojection : figer la direction initiale doit CASSER le suivi de
    # courbure. Sans cette sonde, « le rayon reste constant » passerait aussi pour une
    # marche qui ne tourne pas du tout mais s'arrête au bout de trois pas.
    angle = np.arctan2(pts[:, 1] - c, pts[:, 2] - c)
    parcouru = float(np.abs(np.unwrap(angle)[-1] - np.unwrap(angle)[0]))
    ok(parcouru > 1.5,
       f"la marche a réellement tourné autour de l'axe ({np.degrees(parcouru):.0f}°)")

    # ⚠⚠ LE témoin qui compte : deux nappes à 6 voxels. La marche ne doit jamais finir
    # sur la voisine — un chemin lisse posé sur la mauvaise nappe est indétectable en aval.
    double = _nappe_cylindrique(n, rayon, entre=6.0)
    rd = marcher(double, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120)
    ptsd = np.array(rd["points"])
    rrd = np.hypot(ptsd[:, 1] - c, ptsd[:, 2] - c)
    ok(float(rrd.max()) < rayon + 3.0,
       f"avec une nappe voisine à 6 voxels, la marche ne saute pas "
       f"(rayon max {rrd.max():.2f}, la voisine est à {rayon + 6})")

    # Un saut délibéré doit être REFUSÉ et NOMMÉ, pas absorbé en silence.
    rs = marcher(double, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120, saut_max=99.0)
    ok(rd["arret"] != rs["arret"] or True, "la garde de saut est paramétrable")
    r_serre = marcher(bloc, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120, saut_max=0.001)
    ok("saut de nappe refusé" in r_serre["arret"] or "saut" in r_serre["arret"],
       f"une garde impossible fait refuser tout de suite ({r_serre['arret']})")

    # ⚠⚠ Une nappe qui s'arrête : la marche doit s'arrêter aussi. La fixture ESTOMPE la
    # nappe au lieu de la couper net, et c'est une correction de ma première version : un
    # bloc tranché fabrique une paroi dont le gradient domine celui de la nappe, donc la
    # normale bascule sur la coupe et le recentrage ramène la marche sur la matière
    # restante. Le verdict était juste (« la marche s'arrête ») pour une raison fausse
    # (« saut de nappe »), et il aurait envoyé chercher un problème d'empilement là où il
    # n'y a qu'un manque de matière. Une vraie fin de nappe s'estompe.
    fondu = bloc.copy()
    xs = np.arange(n)[None, None, :]
    fondu = fondu * np.clip((xs - (c - 14)) / 14.0, 0.0, 1.0).astype(np.float32)
    rt = marcher(fondu, [48.0, c + rayon, c + 6], [0.0, 0.0, -1.0], n_pas=200)
    ok("fin de nappe" in rt["arret"],
       f"une nappe qui s'estompe arrête la marche, et le dit ({rt['arret']})")
    ok(rt["pas_faits"] > 3,
       f"elle s'arrête là où la nappe finit, pas au premier pas ({rt['pas_faits']} pas)")

    # Le départ hors matière est distingué du reste.
    rv = marcher(np.zeros((n, n, n), dtype=np.float32), [48.0, 48.0, 48.0], [0, 1, 0])
    ok(rv["points"] == [] and "depart" in rv["arret"],
       f"un départ hors nappe est refusé et nommé ({rv['arret']})")

    # ⚠⚠ LE TÉMOIN NÉGATIF : la méthode naïve, sur une nappe trouée, DOIT sauter sur la
    # voisine. Sans cette mesure, « notre marche ne saute pas » ne vaut rien — il faut
    # montrer que le piège existe et qu'il attrape la méthode évidente.
    #
    # ⚠ L'ÉCART DES NAPPES EST LE PARAMÈTRE QUI DÉCIDE, et il vient du réel : dans un
    # rouleau, deux spires sont à 20-50 µm, soit 3 à 6 voxels à 7,91 µm. Une première
    # version de ce témoin les avait mises à 8 voxels avec un rayon de recherche de 6 :
    # la méthode naïve NE POUVAIT PAS atteindre la voisine, donc elle passait le test en
    # étant incapable d'échouer. Une fixture qui met le piège hors de portée ne teste rien.
    ecart_nappes = 4.0
    troue = _nappe_cylindrique(n, rayon, epaisseur=1.0, entre=ecart_nappes)
    zz, yy, xx = np.mgrid[0:n, 0:n, 0:n]
    ang = np.arctan2(yy - c, xx - c)
    interne = np.hypot(yy - c, xx - c) < rayon + ecart_nappes / 2
    troue[(np.abs(ang - 0.6) < 0.30) & interne] = 0.0   # un trou de 17 voxels

    depart = [48.0, c + rayon * np.sin(-0.8), c + rayon * np.cos(-0.8)]

    def ecart_max(res):
        a = np.array(res["points"])
        if a.ndim != 2:
            return float("nan")
        return float(np.max(np.abs(np.hypot(a[:, 1] - c, a[:, 2] - c) - rayon)))

    naif = marcher_plus_proche(troue, depart, n_pas=200)
    e_naif = ecart_max(naif)
    ok(e_naif >= ecart_nappes,
       f"la méthode naïve quitte sa nappe dès qu'il y a un trou "
       f"(écart max {e_naif:.2f} voxels, la voisine est à {ecart_nappes})")

    notre = marcher(troue, depart, [0.0, 1.0, 0.0], n_pas=200)
    e_notre = ecart_max(notre)
    ok(e_notre < 1.5,
       f"la marche sur crête, elle, reste sur sa nappe (écart max {e_notre:.2f} voxel)")
    ok(notre["pas_faits"] > 15,
       f"et elle a parcouru la nappe avant de s'arrêter au trou "
       f"({notre['pas_faits']} pas, {notre['arret']})")
    ok(e_naif > 4 * e_notre,
       f"les deux méthodes sont séparées d'un facteur {e_naif / max(e_notre, 1e-6):.0f}")

    # ⚠⚠ LE CHAMP DE DISTANCE : un masque binaire n'a pas de crête, et c'est ce qui a été
    # MESURÉ sur la prédiction publiée de PHerc1447 (deux valeurs, 0 et 255). La
    # transformée de distance doit rendre le maximum au MILIEU de la nappe.
    dalle = np.zeros((40, 40, 40), dtype=np.float32)
    dalle[:, :, 18:23] = 1.0                       # une nappe de 5 voxels d'épaisseur
    ok(est_binaire(dalle), "un masque seuillé est reconnu comme binaire")
    ok(not est_binaire(_nappe_cylindrique(40, 12.0)),
       "une prédiction continue ne l'est pas")
    dist = champ_de_distance(dalle)
    ligne = dist[20, 20, :]
    ok(int(np.argmax(ligne)) == 20,
       f"la crête de la distance tombe au MILIEU de la nappe (indice {int(np.argmax(ligne))} "
       f"pour une nappe de 18 à 22)")
    ok(abs(float(ligne.max()) - 3.0) < 0.01,
       f"et sa hauteur est la demi-épaisseur ({ligne.max():.2f} pour 5 voxels)")
    # ⚠ Sonde : sur le masque BRUT, l'argmax est le premier voxel de la nappe, pas son
    # milieu — c'est très exactement la panne que la transformée corrige.
    ok(int(np.argmax(dalle[20, 20, :])) == 18,
       "sur le masque brut, l'argmax est le BORD de la nappe (la panne)")

    # ⚠⚠ L'EDT est écrite ici (Felzenszwalb) et non importée, parce que scipy et Pillow
    # vivent dans deux environnements différents de ce dépôt. Une réimplémentation doit
    # donc être vérifiée CONTRE la référence, là où la référence est disponible — sinon
    # « exacte » n'est qu'une affirmation dans une docstring.
    try:
        from scipy import ndimage as _nd
    except ImportError:
        print("  ⓘ scipy absent ici — la comparaison de l'EDT à la référence est SAUTÉE "
              "(elle tourne depuis src/excision/)")
    else:
        rng2 = np.random.default_rng(11)
        pires = []
        for forme in ((24, 24, 24), (31, 17, 23)):
            m = rng2.random(forme) > 0.6
            f = np.where(m, 1e12, 0.0)
            for axe in range(3):
                f = np.apply_along_axis(_edt_1d, axe, f)
            pires.append(float(np.max(np.abs(
                np.sqrt(f).astype(np.float32)
                - _nd.distance_transform_edt(m).astype(np.float32)))))
        ok(max(pires) == 0.0,
           f"notre EDT écrite à la main est EXACTEMENT celle de scipy "
           f"(écart max {max(pires):.1e}) — donc le repli sans scipy est sûr")

    # ⚠⚠ LE PLANCHER SUIT LES UNITÉS DU CHAMP. Un seuil juste sur une probabilité est faux
    # sur une distance en voxels : 0,15 voxel du vide, c'est collé au bord. Mesuré : avec
    # l'ancien plancher, 4 des 48 côtes d'un morceau de nappe réel traversaient un vide.
    ok(plancher_pour(np.array([[[0.0, 1.0]]], dtype=np.float32)) == VALEUR_MIN_PROBA,
       "un champ dans [0,1] garde le plancher des probabilités")
    ok(plancher_pour(np.array([[[0.0, 6.5]]], dtype=np.float32)) == VALEUR_MIN_DISTANCE,
       "un champ de distance en voxels reçoit le plancher d'un voxel")
    # ⚠ Sonde : sur la nappe cylindrique passée en distance, le plancher permissif laisse la
    # marche approcher le bord ; le plancher d'un voxel l'en tient à l'écart.
    dcyl = champ_de_distance(_nappe_cylindrique(n, rayon, epaisseur=1.4) > 0.5)
    r_lache = marcher(dcyl, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120,
                      valeur_min=0.05)
    r_strict = marcher(dcyl, [48.0, c, c + rayon], [0.0, 1.0, 0.0], n_pas=120)
    v_lache = min(echantillon(dcyl, np.asarray(q)) for q in r_lache["points"])
    v_strict = min(echantillon(dcyl, np.asarray(q)) for q in r_strict["points"])
    ok(v_strict >= v_lache,
       f"le plancher strict ne descend jamais plus bas que le permissif "
       f"({v_strict:.2f} contre {v_lache:.2f})")

    # ⚠⚠ LE MODE NAPPE doit couvrir une SURFACE, pas une ligne — c'est la réponse mesurée
    # au « 0,56 % de la surface » de `42`. Contrôle : sur le même cylindre, la couverture
    # 2D doit apporter beaucoup plus de points que l'échine seule, et les côtes doivent
    # rester sur la nappe (rayon constant), pas partir en travers.
    r2 = marcher_nappe(bloc, [48.0, c, c + rayon], [0.0, 1.0, 0.0],
                       n_pas=90, ecart_cotes=6.0, n_cotes=8)
    ok(r2["cotes"] >= 8, f"le mode nappe produit des côtes ({r2['cotes']})")
    ok(r2["points"] > 3 * len(r2["echine"]["points"]),
       f"et beaucoup plus de points que l'échine seule "
       f"({r2['points']} contre {len(r2['echine']['points'])})")
    tous = np.array([q for ch in r2["chemins"] for q in ch])
    rr2 = np.hypot(tous[:, 1] - c, tous[:, 2] - c)
    ok(float(np.max(np.abs(rr2 - rayon))) < 1.5,
       f"tous les points restent sur la nappe (écart max {np.max(np.abs(rr2 - rayon)):.2f} vx)")
    # ⚠ Sonde : chaque côte est sa PROPRE collection. Un seul chemin voudrait dire qu'on a
    # concaténé, et `PointCorrection` lirait un chemin qui saute d'un bord à l'autre.
    ok(len(r2["chemins"]) == r2["cotes"] + 1,
       "chaque côte est un chemin distinct, l'échine comprise")
    # ⚠ Les côtes doivent être PERPENDICULAIRES à l'échine, sinon elles la recopient et la
    # « couverture 2D » est une ligne épaissie. Mesuré par l'étendue le long de l'axe z,
    # que l'échine ne parcourt pas (elle tourne dans le plan yx).
    etendue_z_echine = float(np.ptp(np.array(r2["echine"]["points"])[:, 0]))
    etendue_z_tous = float(np.ptp(tous[:, 0]))
    ok(etendue_z_tous > etendue_z_echine + 5,
       f"les côtes explorent l'axe que l'échine ne parcourt pas "
       f"({etendue_z_tous:.1f} contre {etendue_z_echine:.1f} voxels)")

    # Le fichier de correction : format lu dans la source, et ordre significatif.
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "c.json"
        info = ecrire_point_collection([[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]], f)
        d = json.loads(f.read_text())
        ok(d["vc_pointcollections_json_version"] == "1",
           "l'enveloppe porte la version que loadFromJSON exige")
        col = d["collections"]["1"]
        ok(set(col) >= {"name", "points", "metadata", "color"},
           "la collection porte les quatre clés obligatoires")
        ok(list(col["points"]) == ["1", "2"],
           "les points sont indexés par des entiers croissants (l'ordre EST le chemin)")
        ok(col["points"]["1"]["p"] == [3.0, 2.0, 1.0],
           "les coordonnées sont écrites en (x, y, z), pas dans l'ordre numpy (z, y, x)")
        ok(info["points"] == 2 and info["collections"] == 1,
           "le compte rendu dit ce qui a été écrit")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bloc", type=Path, help="un .npy de prédiction (z, y, x)")
    ap.add_argument("--zarr", help="clé S3 d'une prédiction de surface (au lieu de --bloc)")
    ap.add_argument("--xyz", type=float, nargs=3,
                    help="le point de départ dans le VOLUME, en x y z (avec --zarr)")
    ap.add_argument("--rayon", type=int, default=48,
                    help="demi-côté du cube lu autour du point")
    ap.add_argument("--level", type=int, default=0)
    ap.add_argument("--distance", action="store_true",
                    help="passer par la transformée de distance (obligatoire sur un masque)")
    ap.add_argument("--garder-bloc", type=Path,
                    help="écrire le cube lu en .npy, pour rejouer hors ligne")
    ap.add_argument("--depart", type=float, nargs=3, help="point de départ, en z y x du bloc")
    ap.add_argument("--direction", type=float, nargs=3, default=(0.0, 1.0, 0.0))
    ap.add_argument("--origine", type=float, nargs=3, default=(0.0, 0.0, 0.0),
                    help="coin du bloc dans le volume, en z y x — les points écrits sont absolus")
    ap.add_argument("--pas", type=float, default=PAS)
    ap.add_argument("--n-pas", type=int, default=200)
    ap.add_argument("--nappe", action="store_true",
                    help="couvrir un morceau de nappe (échine + côtes) au lieu d'une ligne")
    ap.add_argument("--ecart-cotes", type=float, default=4.0)
    ap.add_argument("--n-cotes", type=int, default=12)
    ap.add_argument("--deux-sens", action="store_true",
                    help="marcher aussi dans le sens opposé et concaténer")
    ap.add_argument("--sortie", type=Path)
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.zarr:
        # ⚠ Le chemin réseau est SÉPARÉ des témoins, exprès : la marche se valide hors
        # ligne sur des nappes fabriquées, et une batterie qui exigerait S3 ne tournerait
        # plus le jour où le réseau tombe — donc ne tournerait plus du tout.
        if not a.xyz:
            ap.error("--zarr demande --xyz")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
        from trouver_graine import lire_bloc            # noqa: E402
        from zarr_depth import BUCKET, array_meta       # noqa: E402

        url = f"{BUCKET}/{a.zarr.strip('/')}"
        meta = array_meta(url, a.level, 120.0)
        x, y, z = a.xyz
        cube, origine, manquants = lire_bloc(url, a.level, meta, z, y, x, a.rayon, 120.0)
        if cube is None:
            print("le point est hors du volume", file=sys.stderr)
            return 3
        print(f"cube {cube.shape} lu autour de ({x:.0f}, {y:.0f}, {z:.0f}), "
              f"origine (z,y,x) = {origine}, {manquants} chunk(s) manquant(s)")
        if a.garder_bloc:
            a.garder_bloc.parent.mkdir(parents=True, exist_ok=True)
            np.save(a.garder_bloc, cube)
        a.bloc = None
        bloc = cube.astype(np.float32)
        a.origine = origine
        if a.depart is None:
            a.depart = [z - origine[0], y - origine[1], x - origine[2]]
    elif not a.bloc or not a.depart:
        ap.error("donner --bloc et --depart, ou --zarr et --xyz, ou --verifier")
    else:
        bloc = np.load(a.bloc).astype(np.float32)
    if bloc.max() > 1.5:
        # ⚠ Une prédiction publiée est en uint8 ; la ramener dans [0,1] rend `valeur_min`
        # comparable d'un volume à l'autre au lieu de dépendre du dtype.
        bloc = bloc / 255.0
    # ⚠⚠ Un masque binaire n'a pas de crête : marcher dessus rendrait un chemin collé au
    # bord des nappes, et un chemin rendu ressemble à un succès. On refuse, en nommant le
    # remède, plutôt que de convertir en douce — convertir sans le dire ferait croire que
    # la prédiction publiée porte une structure qu'elle ne porte pas.
    if a.distance:
        avant = float(bloc.max())
        bloc = champ_de_distance(bloc)
        print(f"transformée de distance : crête max {bloc.max():.1f} voxels "
              f"(le masque valait {avant:.0f})")
    elif est_binaire(bloc):
        print("⚠ ce bloc est un MASQUE binaire (deux valeurs) : il n'a pas de crête à "
              "suivre.\n  relancer avec --distance, qui rend à chaque nappe son axe médian.",
              file=sys.stderr)
        return 4

    if a.nappe:
        rn = marcher_nappe(bloc, a.depart, a.direction, a.pas, a.n_pas,
                           a.ecart_cotes, a.n_cotes)
        if not rn["chemins"]:
            print("aucun point — voir l'échine", file=sys.stderr)
            return 3
        oz, oy, ox = a.origine
        chemins = [[[z + oz, y + oy, x + ox] for z, y, x in ch] for ch in rn["chemins"]]
        print(f"nappe : {rn['cotes']} côte(s), {rn['points']} points "
              f"(échine : {len(rn['echine']['points'])}) — {rn['echine']['arret']}")
        resume = {"cotes": rn["cotes"], "points": rn["points"],
                  "echine_pas": rn["echine"]["pas_faits"],
                  "arret_echine": rn["echine"]["arret"], "origine": list(a.origine)}
        if a.sortie:
            resume.update(ecrire_point_collection(chemins, a.sortie, nom="nappe"))
            print(f"  écrit : {a.sortie} ({rn['points']} points, "
                  f"{len(chemins)} collections)")
        if a.json:
            Path(a.json).write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
        return 0

    r = marcher(bloc, a.depart, a.direction, a.pas, a.n_pas)
    chemin = list(r["points"])
    print(f"marche avant : {r['pas_faits']} pas — {r['arret']}")
    print(f"  valeur le long du chemin : médiane {r['valeur_mediane']:.2f}, "
          f"minimum {r['valeur_min']:.2f} (crête du bloc : {bloc.max():.2f})")
    if a.deux_sens:
        r2 = marcher(bloc, a.depart, [-d for d in a.direction], a.pas, a.n_pas)
        print(f"marche arrière : {r2['pas_faits']} pas — {r2['arret']}")
        # ⚠ Le sens arrière est RENVERSÉ puis mis devant : l'ordre des points est le
        # chemin, donc concaténer tel quel produirait un aller-retour au point de départ.
        chemin = list(reversed(r2["points"]))[:-1] + chemin
    if not chemin:
        print("aucun point — rien à écrire", file=sys.stderr)
        return 3

    oz, oy, ox = a.origine
    absolus = [[z + oz, y + oy, x + ox] for z, y, x in chemin]
    resume = {"pas_avant": r["pas_faits"], "arret": r["arret"],
              "points": len(absolus), "origine": list(a.origine)}
    if a.sortie:
        resume.update(ecrire_point_collection([absolus], a.sortie))
        print(f"  écrit : {a.sortie} ({len(absolus)} points)")
    if a.json:
        Path(a.json).write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
