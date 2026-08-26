#!/usr/bin/env python3
"""Ou chaque spire d'une chaine se trouve DANS le rouleau -- rayon, angle balaye, espacement.

⚠⚠ Cet instrument est ne d'un soupcon sur la tache « coller les spires en une surface ».
Une chaine `gen_neighbor` avance RADIALEMENT : la spire N+1 est la spire N projetee d'une
nappe vers l'exterieur. Les deux occupent donc la MEME fenetre angulaire, a une nappe l'une
de l'autre. Or dans un rouleau deroule, deux nappes consecutives sont separees par une
circonference entiere de papyrus -- celle qu'on ne possede pas. Recoller une chaine radiale
bout a bout donnerait donc une bande continue qui n'existe pas.

⭐ Le test est axe-libre, et c'est ce qui le rend utilisable sans verite terrain : une ligne
de grille qui court le long de la circonference TOURNE, une ligne qui court le long de l'axe
du rouleau est DROITE. On n'a donc pas besoin de savoir ou est l'axe pour savoir laquelle des
deux directions de grille est laquelle -- il suffit de regarder laquelle courbe.

Ce qu'il mesure, par spire :
  - le rayon de la nappe (par ajustement de cercle dans le plan perpendiculaire a l'axe) ;
  - l'angle balaye, donc la FRACTION DE TOUR que la fenetre couvre ;
  - la hauteur le long de l'axe ;
  - l'espacement a la spire precedente (distance mediane au plus proche voisin, en 3D).

⚠ L'espacement mesure est le seul chiffre qui dise si `neighbor_step` a reellement atterri
UNE nappe plus loin. Un pas trop grand saute une nappe sans que rien d'autre le signale : la
surface converge toujours, elle converge juste sur la mauvaise feuille.

Usage :
    cd experiments && uv run python src/nappe/geometrie_chaine.py \\
        data/spires_pas025 --voxel-um 8.64 --json docs/mesures/geometrie_pas025.json \\
        --figure docs/images/44_geometrie_chaine.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

import numpy as np

# ⚠ Sous ce nombre de points valides une ligne de grille ne porte pas d'information de
# courbure : trois points ajustent un cercle exactement, donc son rayon ne veut rien dire.
MIN_POINTS_LIGNE = 12
# Une ligne qui ne tourne pas de plus que ca est DROITE -- c'est la direction de l'axe.
# Valeur choisie tres bas expres : on ne veut separer que « tourne » de « ne tourne pas ».
TOURNE_MIN_RAD = 0.02


def lire_tifxyz(dossier: Path) -> np.ndarray | None:
    """Rendre un tableau (H, W, 3) de coordonnees volume, NaN aux sommets invalides."""
    import tifffile

    try:
        x = tifffile.imread(dossier / "x.tif").astype(np.float64)
        y = tifffile.imread(dossier / "y.tif").astype(np.float64)
        z = tifffile.imread(dossier / "z.tif").astype(np.float64)
    except (FileNotFoundError, OSError):
        return None
    p = np.stack([x, y, z], axis=-1)
    # ⚠⚠ J'ai d'abord suppose que la sentinelle d'invalidite etait (0,0,0), et le temoin
    # testait donc ma propre hypothese : sur les vrais maillages elle vaut **-1**, si bien
    # que 100 % des sommets passaient pour valides et la mesure rendait « surface plane ».
    # La convention est ecrite noir sur blanc par l'outil de vc lui-meme, dans la note de
    # son rapport de self-intersection : « z <= 0 invalid ». On la reprend telle quelle,
    # plus les composantes negatives, parce que les deux se rencontrent dans l'arbre.
    invalide = (z <= 0) | (x < 0) | (y < 0) | ((x == 0) & (y == 0) & (z == 0))
    p[invalide] = np.nan
    return p


def maillage_de_spire(spire: Path, prefere: str = "trace") -> tuple[Path | None, str]:
    """Choisir le maillage d'une spire, et DIRE lequel.

    ⚠ Une spire porte deux maillages et ils n'ont pas les memes dimensions de grille :
    `trace/neighbor_out_*` est celui que la chaine a fait pousser -- c'est lui que le
    rapport de self-intersection mesure, donc lui dont viennent les aires publiees --
    tandis que `plat/` est une reparametrisation pour le rendu. La surface 3D est la meme,
    la grille non ; melanger les deux fait comparer des aires a des geometries qui ne
    portent pas sur le meme echantillonnage.
    """
    # ⚠ On cherche des `z.tif`, PAS des `meta.json` : un maillage est defini par ses TIFF
    # de coordonnees, et le meta est optionnel (le pas de grille a un defaut). La premiere
    # version globait les metas, si bien qu'un maillage sans meta etait invisible -- une
    # panne trouvee par le temoin, qui n'en ecrit pas.
    dir_trace = spire / "trace"
    pousses = sorted(z.parent for z in dir_trace.glob("*/z.tif")) if dir_trace.is_dir() else []
    aplati = [spire / "plat"] if (spire / "plat" / "z.tif").is_file() else []
    candidats = pousses + aplati if prefere == "trace" else aplati + pousses
    for c in candidats:
        return c, ("aplati" if c.name == "plat" else "poussé")
    return None, "absent"


def pas_de_grille(maillage: Path, defaut: float = 20.0) -> float:
    """Le pas de grille en voxels, lu dans le `scale` du meta -- jamais suppose.

    ⚠ Meme raison que dans `table_chaine.py` : une echelle supposee rend des aires fausses
    d'un facteur (rapport des echelles)². Le meta la porte, on la lit.
    """
    meta = maillage / "meta.json"
    if not meta.is_file():
        return defaut
    try:
        sc = json.loads(meta.read_text(encoding="utf-8")).get("scale")
    except (json.JSONDecodeError, OSError):
        return defaut
    if isinstance(sc, list) and sc and float(sc[0]) > 0:
        return 1.0 / float(sc[0])
    return defaut


def ajuster_cercle(xy: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Centre, rayon et residu quadratique d'un cercle ajuste sur des points 2D.

    ⚠⚠ J'ai d'abord justifie le raffinement par le biais de Kasa « sur un arc court ». La
    mesure a corrige la raison : sur un arc EXACT de 0,05 a 0,60 rad, Kasa est juste au
    millieme de pourcent. Ce qui le casse, c'est le BRUIT -- a 1 voxel d'ecart-type il tire
    le rayon de -8 %, a 3 voxels de -42 %, quand l'ajustement geometrique reste a -0,6 %.
    Sur une nappe de papyrus reelle le bruit est de cet ordre, donc le raffinement n'est pas
    un raffinement : c'est la mesure, et Kasa n'est que l'amorce qui la fait converger.
    """
    from scipy.optimize import least_squares

    x, y = xy[:, 0], xy[:, 1]
    # Amorce algebrique : x^2 + y^2 + a x + b y + c = 0.
    A = np.column_stack([x, y, np.ones_like(x)])
    b = -(x**2 + y**2)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c0 = np.array([-sol[0] / 2.0, -sol[1] / 2.0])

    def residu(c):
        d = np.hypot(x - c[0], y - c[1])
        return d - d.mean()

    r = least_squares(residu, c0, method="lm")
    centre = r.x
    d = np.hypot(x - centre[0], y - centre[1])
    return centre, float(d.mean()), float(np.sqrt(np.mean((d - d.mean()) ** 2)))


def normale_de_plan(pts: np.ndarray) -> np.ndarray:
    """Normale du plan des moindres carres d'un nuage 3D (plus petite direction propre)."""
    c = pts - pts.mean(axis=0)
    _, _, vt = np.linalg.svd(c, full_matrices=False)
    return vt[2]


def lignes_de(p: np.ndarray, axe: int):
    """Enumerer les lignes de grille qui VARIENT le long de `axe` (0 = colonnes, 1 = rangees)."""
    n = p.shape[1 - axe]
    for i in range(n):
        ligne = p[i, :, :] if axe == 1 else p[:, i, :]
        bons = ligne[~np.isnan(ligne[:, 0])]
        if len(bons) >= MIN_POINTS_LIGNE:
            yield bons


def mesures_de_lignes(p: np.ndarray, axe: int) -> tuple[float, float]:
    """Angle balaye (par la FLECHE) et longueur d'arc, medianes des lignes le long de `axe`.

    ⭐ La fleche est le discriminant axe-libre : sur un cylindre, les lignes
    circonferentielles tournent plus que les lignes axiales, ou que soit l'axe.

    ⚠⚠ La premiere version ajustait un cercle sur chaque ligne et divisait la longueur par
    le rayon. Le temoin l'a refutee : sur une ligne DROITE l'ajustement est singulier, il
    rend un rayon minuscule, et l'angle sort a 3,9 rad -- donc la direction axiale passait
    pour la plus courbe et une surface plane pour un rouleau. La fleche ne peut pas exploser.

    Pour un arc de demi-angle phi : corde = 2R sin(phi), fleche = R(1 - cos(phi)), donc
    phi = 2 atan(2 x fleche / corde) exactement -- aucune approximation petit-angle.

    ⚠ SENS DU BIAIS, mesure sur les vraies nappes : une nappe de papyrus est gondolee, et
    le gondolement s'ajoute a la fleche. L'angle rendu est donc un MAJORANT de l'angle
    reellement balaye, ce qui fait de « combien de fenetres pour fermer un tour » un
    MINORANT. La conclusion structurelle n'en est que renforcee.
    """
    angles, longueurs = [], []
    for ligne in lignes_de(p, axe):
        corde = ligne[-1] - ligne[0]
        lc = float(np.linalg.norm(corde))
        if lc < 1e-9:
            continue
        u = corde / lc
        d = ligne - ligne[0]
        fleche = float(np.linalg.norm(d - np.outer(d @ u, u), axis=1).max())
        angles.append(4.0 * math.atan2(2.0 * fleche, lc))
        longueurs.append(float(np.sum(np.linalg.norm(np.diff(ligne, axis=0), axis=1))))
    if not angles:
        return 0.0, 0.0
    return float(np.median(angles)), float(np.median(longueurs))


def tourne_le_long(p: np.ndarray, axe: int) -> float:
    """Angle median balaye par les lignes qui varient le long de `axe`."""
    return mesures_de_lignes(p, axe)[0]


def axe_circonferentiel_de(p: np.ndarray) -> tuple[int, float, float]:
    """Quelle direction de grille court le long de la circonference, et de combien.

    ⚠⚠ Ceci se decide PAR SPIRE et jamais une fois pour la chaine. Mesure sur la chaine
    reelle : la spire de depart a sa circonference en COLONNES et les huit suivantes en
    RANGEES, parce que `gen_neighbor` rend une grille transposee par rapport au segment
    source. Decider une fois faisait mesurer huit spires le long du mauvais axe, et rendait
    des rayons de plusieurs centaines de metres sans que rien ne signale l'erreur.
    """
    a0, l0 = mesures_de_lignes(p, 0)
    a1, l1 = mesures_de_lignes(p, 1)
    return (0, a0, l0) if a0 >= a1 else (1, a1, l1)


def etendue_angulaire(theta: np.ndarray) -> float:
    """Ouverture angulaire d'un nuage d'angles, en trouvant le plus grand trou.

    ⚠ Un simple max-min est faux des que l'arc franchit -pi : il rend presque 2*pi pour un
    arc etroit pose sur la coupure. Le complement du plus grand intervalle vide est correct
    partout.
    """
    t = np.sort(theta)
    trous = np.diff(t)
    trou_max = max(float(trous.max()) if len(trous) else 0.0,
                   float(2 * math.pi - (t[-1] - t[0])))
    return float(2 * math.pi - trou_max)


def mesurer_spire(p: np.ndarray, axe: np.ndarray) -> dict:
    """Ce qu'on peut mesurer d'une spire -- et ce qu'on refuse de mesurer.

    ⭐⭐ Ce qui est SOLIDE ici ne depend d'aucun modele : la longueur d'arc (une polyligne),
    la hauteur (une projection), l'angle balaye (une fleche). Le RAYON, lui, suppose que la
    nappe est un morceau de cylindre -- et sur les vraies nappes elle ne l'est pas. Deux
    estimateurs independants sont donc calcules, et quand ils se contredisent le rayon est
    declare INDETERMINE au lieu d'etre publie.

    ⚠ Mesure sur la chaine reelle : residu d'ajustement 1,1 a 1,6 mm pour un espacement de
    nappes de 113 µm. Le gondolement de la feuille est DIX FOIS la distance entre feuilles,
    donc un cercle unique n'explique pas la nappe, et les deux estimateurs se separent d'un
    facteur deux. Publier l'un des deux aurait ete publier un chiffre au hasard.
    """
    ax, dtheta, arc = axe_circonferentiel_de(p)
    pts = p.reshape(-1, 3)
    pts = pts[~np.isnan(pts[:, 0])]
    r: dict = {"points": int(len(pts)), "axe_circonferentiel": int(ax),
               "angle_rad": dtheta, "arc_vox": arc,
               "fraction_de_tour": dtheta / (2 * math.pi) if dtheta > 0 else 0.0}
    if len(pts) < MIN_POINTS_LIGNE or dtheta <= 0:
        return r

    # Estimateur 1 : geometrique pur, R = longueur d'arc / angle balaye.
    r_fleche = arc / dtheta
    # La fleche que ce rayon implique -- l'echelle du SIGNAL circulaire.
    sagitta = r_fleche * (1.0 - math.cos(dtheta / 2.0))

    # Estimateur 2 : ajustement de cercle dans le plan perpendiculaire a l'axe du rouleau.
    u = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(u, axe)) > 0.9:
        u = np.array([0.0, 1.0, 0.0])
    u = u - np.dot(u, axe) * axe
    u /= np.linalg.norm(u)
    v = np.cross(axe, u)
    xy = np.column_stack([pts @ u, pts @ v])
    try:
        centre, r_cercle, residu = ajuster_cercle(xy)
    except (np.linalg.LinAlgError, ValueError):
        centre, r_cercle, residu = np.array([0.0, 0.0]), float("nan"), float("inf")
    theta = np.arctan2(xy[:, 1] - centre[1], xy[:, 0] - centre[0])
    h = pts @ axe

    # ⭐ Le critere de determination : l'ecart au cercle doit etre PETIT devant la fleche
    # que le cercle implique. Sinon le « signal » circulaire est du meme ordre que le bruit
    # de forme, et le centre est place par ce bruit.
    part_de_bruit = residu / sagitta if sagitta > 0 else float("inf")
    accord = (abs(r_cercle - r_fleche) / r_fleche
              if np.isfinite(r_cercle) and r_fleche > 0 else float("inf"))
    r.update({
        "rayon_fleche_vox": r_fleche,
        "rayon_cercle_vox": float(r_cercle) if np.isfinite(r_cercle) else None,
        "residu_vox": float(residu) if np.isfinite(residu) else None,
        "sagitta_vox": sagitta,
        "residu_sur_sagitta": part_de_bruit if math.isfinite(part_de_bruit) else None,
        "desaccord_relatif": accord if math.isfinite(accord) else None,
        # ⭐ Deux conditions, et il faut les DEUX. Les seuils viennent de la mesure : sur
        # un cylindre exact ou bruite a 3 voxels, desaccord < 1 % et residu/fleche < 0,3 ;
        # sur les vraies nappes, desaccord 118 % et residu/fleche 0,8 a 2,2.
        "rayon_determine": bool(accord < 0.2 and part_de_bruit < 1.0),
        "angle_plan_rad": etendue_angulaire(theta),
        "hauteur_vox": float(h.max() - h.min()),
        "theta_milieu": float(np.arctan2(np.sin(theta).mean(), np.cos(theta).mean())),
    })
    return r


def espacement(a: np.ndarray, b: np.ndarray) -> float:
    """Distance mediane de chaque point de `b` au plus proche point de `a`, en voxels."""
    from scipy.spatial import cKDTree

    pa = a.reshape(-1, 3)
    pa = pa[~np.isnan(pa[:, 0])]
    pb = b.reshape(-1, 3)
    pb = pb[~np.isnan(pb[:, 0])]
    if len(pa) < 1 or len(pb) < 1:
        return float("nan")
    d, _ = cKDTree(pa).query(pb, k=1)
    return float(np.median(d))


def analyser_chaine(dossier: Path, voxel_um: float, prefere: str = "trace",
                    tours: int | None = None) -> dict:
    """Mesurer une chaine, eventuellement TRONQUEE a ses `tours` premiers tours.

    ⚠⚠ La troncature existe pour une raison precise : comparer deux campagnes de longueurs
    differentes sur un taux « par tour » est faux. Le taux est une moyenne geometrique sur
    toute la chaine, et l'erosion s'accelere avec la profondeur -- donc une chaine plus
    longue affiche un taux plus eleve pour la seule raison qu'elle est allee plus loin.
    C'est le meme confondant que celui qui a demasque « la rupture est une erosion » : deux
    grandeurs qui croissent avec le rang ne se comparent qu'a rang egal.
    """
    spires = sorted(d for d in dossier.iterdir() if d.is_dir())
    if tours is not None:
        spires = spires[:max(tours, 0)]
    maillages, noms, genres, chemins = [], [], [], []
    for s in spires:
        m, genre = maillage_de_spire(s, prefere)
        if m is None:
            continue
        p = lire_tifxyz(m)
        if p is None:
            continue
        maillages.append(p)
        noms.append(s.name)
        genres.append(genre)
        chemins.append(m)
    if not maillages:
        return {"spires": [], "raison": "aucun maillage lisible"}

    # ⚠ L'axe circonferentiel se decide PAR SPIRE (voir axe_circonferentiel_de) ; ce qui
    # est commun a la chaine, c'est l'axe du ROULEAU.
    axes_circ = [axe_circonferentiel_de(m)[0] for m in maillages]
    tournes = [max(mesures_de_lignes(m, 0)[0], mesures_de_lignes(m, 1)[0])
               for m in maillages]
    if max(tournes) < TOURNE_MIN_RAD:
        return {"spires": [], "raison": f"aucune direction ne tourne (max {max(tournes):.4f} "
                                        "rad) — surface plane, il n'y a pas d'axe de rouleau "
                                        "à trouver",
                "tourne": tournes}

    # Axe du rouleau : normale mediane des plans des lignes circonferentielles de TOUTES
    # les spires, chacune le long de SON axe.
    normales = []
    for m, ac in zip(maillages, axes_circ):
        for ligne in lignes_de(m, ac):
            normales.append(normale_de_plan(ligne))
    N = np.array(normales)
    # ⚠ Une normale de moindres carres n'a pas de sens de signe : sans realignement la
    # mediane de deux moities opposees est proche de zero et l'axe sort au hasard.
    N[N @ N[0] < 0] *= -1
    axe = np.median(N, axis=0)
    axe /= np.linalg.norm(axe)

    out = []
    for i, (nom, m) in enumerate(zip(noms, maillages)):
        r = mesurer_spire(m, axe)
        r["nom"] = nom
        r["maillage"] = genres[i]
        r["grille"] = [int(m.shape[1]), int(m.shape[0])]
        r["sommets"] = int(m.shape[0] * m.shape[1])
        # ⭐⭐ La fraction de sommets qui portent reellement de la matiere. Sans elle, une
        # aire de grille est un majorant dont on ne connait pas le facteur -- et il vaut
        # ici presque deux au depart, plus de quatre a la fin.
        r["fraction_valide"] = r["points"] / r["sommets"] if r["sommets"] else 0.0
        pas = pas_de_grille(chemins[i])
        # ⚠ Approximation assumee : une cellule demande QUATRE coins valides, on compte un
        # sommet pour une cellule. Le biais est d'un liseré sur le bord du trou, d'un autre
        # ordre que le facteur deux entre aire de grille et aire utile.
        r["aire_valide_cm2"] = r["points"] * (pas * voxel_um / 10000.0) ** 2
        if i > 0:
            r["espacement_vox"] = espacement(maillages[i - 1], m)
            r["espacement_um"] = r["espacement_vox"] * voxel_um
        if r.get("angle_rad", 0.0) > 0:
            r["arc_mm"] = r["arc_vox"] * voxel_um / 1000.0
            r["hauteur_mm"] = r["hauteur_vox"] * voxel_um / 1000.0
            r["rayon_fleche_mm"] = r["rayon_fleche_vox"] * voxel_um / 1000.0
            rc = r.get("rayon_cercle_vox")
            r["rayon_cercle_mm"] = rc * voxel_um / 1000.0 if rc else None
            r["spires_par_tour_min"] = 2 * math.pi / r["angle_rad"]
        out.append(r)
    return {"spires": out, "axe": [float(a) for a in axe],
            "axes_circonferentiels": [int(a) for a in axes_circ],
            "tourne": tournes, "voxel_um": voxel_um, "maillage_prefere": prefere}


def cylindre_synthetique(rayon: float, angle: float, hauteur: float,
                         n_theta: int = 40, n_h: int = 30, theta0: float = 0.3,
                         circ_en_colonnes: bool = False, bruit: float = 0.0,
                         graine: int = 7, gondolement: float = 0.0,
                         n_ondes: float = 2.0) -> np.ndarray:
    """Une plaque de cylindre de rayon et d'ouverture connus, pour le temoin.

    ⚠ `gondolement` ondule le rayon LE LONG DE LA CIRCONFERENCE, et pas le long de l'axe.
    C'est la forme du defaut mesure sur les vraies nappes : une ondulation circonferentielle
    gonfle la fleche de chaque ligne -- donc l'angle qu'on en deduit -- sans changer la
    longueur d'arc, si bien que l'estimateur `arc/angle` tombe pendant que l'ajustement de
    cercle sur le nuage entier reste pres du vrai rayon. Les deux se separent d'un facteur
    deux, exactement comme sur la chaine reelle. Une ondulation AXIALE, plus intuitive, ne
    separe pas les deux estimateurs et n'aurait donc rien teste.
    """
    # Axe volontairement oblique : un axe aligne sur X, Y ou Z laisserait passer un
    # instrument qui suppose que le rouleau est droit dans le volume.
    a = np.array([0.3, 0.5, 0.81])
    a /= np.linalg.norm(a)
    u = np.cross(a, [0.0, 0.0, 1.0])
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    th = theta0 + np.linspace(0, angle, n_theta)
    hs = np.linspace(-hauteur / 2, hauteur / 2, n_h)
    rr = rayon + gondolement * np.sin(2 * math.pi * n_ondes * (th - th[0]) / max(angle, 1e-9))
    C = np.array([3000.0, 2500.0, 12000.0])
    pts = (C
           + rr[None, :, None] * (np.cos(th)[None, :, None] * u
                                  + np.sin(th)[None, :, None] * v)
           + hs[:, None, None] * a)
    if bruit > 0:
        pts = pts + np.random.default_rng(graine).normal(0.0, bruit, pts.shape)
    return np.transpose(pts, (1, 0, 2)) if circ_en_colonnes else pts


def plaque_plane(n_h: int = 30, n_w: int = 40) -> np.ndarray:
    """Un morceau de plan : aucun axe de rouleau a trouver."""
    p = np.zeros((n_h, n_w, 3))
    gx, gy = np.meshgrid(np.arange(float(n_w)), np.arange(float(n_h)))
    p[..., 0] = 3000 + gx * 20
    p[..., 1] = 2500 + gy * 20
    p[..., 2] = 12000.0
    return p


def ecrire_chaine(racine: Path, maillages: list[np.ndarray],
                  sous: str = "plat") -> None:
    """Ecrire des maillages comme une chaine de spires sur le disque, au format tifxyz.

    ⚠ Le temoin passe par le DISQUE et non par un appel direct : `analyser_chaine` decouvre
    ses spires en listant un dossier et en lisant des TIFF, et c'est justement ce chemin-la
    qui a echoue en vrai (un dossier mal nomme, un sentinelle d'invalidite mal lu). Un
    temoin qui court-circuite la lecture ne peut pas attraper ces pannes.
    """
    import tifffile

    for i, m in enumerate(maillages):
        d = racine / f"spire{i:02d}" / sous
        d.mkdir(parents=True, exist_ok=True)
        for k, nom in enumerate("xyz"):
            tifffile.imwrite(d / f"{nom}.tif", m[..., k].astype(np.float32))


def verifier() -> int:
    """Temoin hors ligne. Les briques ET la chaine entiere, lue depuis le disque."""
    import tempfile

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    R, A, H = 1000.0, 0.30, 400.0
    m = cylindre_synthetique(R, A, H)
    axe = np.array([0.3, 0.5, 0.81]); axe /= np.linalg.norm(axe)

    # ---- La fleche : le discriminant de direction ---------------------------------------
    t_col, t_rang = tourne_le_long(m, 0), tourne_le_long(m, 1)
    v("la direction circonférentielle tourne plus que l'axiale",
      t_rang > 10 * max(t_col, 1e-9), f"colonnes {t_col:.4f}  rangées {t_rang:.4f}")
    v("la flèche retrouve l'angle balayé à 2 %", abs(t_rang - A) < 0.02 * A,
      f"{t_rang:.4f} au lieu de {A}")
    ax, dth, arc = axe_circonferentiel_de(m)
    v("l'axe circonférentiel est trouvé", ax == 1, str(ax))
    v("la longueur d'arc est celle du cylindre", abs(arc - R * A) < 0.01 * R * A,
      f"{arc:.1f} au lieu de {R * A:.1f}")
    mt = cylindre_synthetique(R, A, H, circ_en_colonnes=True)
    v("une grille transposée est reconnue (la circonférence est en colonnes)",
      axe_circonferentiel_de(mt)[0] == 0, str(axe_circonferentiel_de(mt)[0]))
    plat = plaque_plane()
    v("une surface plane ne tourne pas",
      max(tourne_le_long(plat, 0), tourne_le_long(plat, 1)) < TOURNE_MIN_RAD,
      f"{max(tourne_le_long(plat, 0), tourne_le_long(plat, 1)):.4f} rad")

    # ---- Le rayon : deux estimateurs, et le refus quand ils se contredisent -------------
    r = mesurer_spire(m, axe)
    v("les deux estimateurs de rayon trouvent le bon, à 2 %",
      abs(r["rayon_fleche_vox"] - R) < 0.02 * R
      and abs(r["rayon_cercle_vox"] - R) < 0.02 * R,
      f"flèche {r['rayon_fleche_vox']:.1f}  cercle {r['rayon_cercle_vox']:.1f}")
    v("sur un cylindre exact le rayon est déclaré déterminé", r["rayon_determine"],
      f"désaccord {r['desaccord_relatif']:.4f}  résidu/flèche {r['residu_sur_sagitta']:.4f}")
    v("l'ouverture angulaire est retrouvée à 5 %", abs(r["angle_rad"] - A) < 0.05 * A,
      f"{r['angle_rad']:.4f} au lieu de {A}")
    v("la hauteur le long de l'axe est retrouvée", abs(r["hauteur_vox"] - H) < 0.02 * H,
      f"{r['hauteur_vox']:.1f} au lieu de {H}")

    rb = mesurer_spire(cylindre_synthetique(R, A, H, bruit=3.0), axe)
    v("3 voxels de bruit ne cassent ni le rayon ni le verdict",
      abs(rb["rayon_cercle_vox"] - R) < 0.03 * R and rb["rayon_determine"],
      f"cercle {rb['rayon_cercle_vox']:.1f}  déterminé {rb['rayon_determine']}  "
      f"désaccord {rb['desaccord_relatif']:.4f}  résidu/flèche {rb['residu_sur_sagitta']:.3f}")

    # ⭐⭐ Le controle qui fait exister le drapeau : une nappe GONDOLEE comme les vraies.
    # Sans lui, `rayon_determine` pourrait etre toujours vrai et le refus ne servirait a rien.
    rg = mesurer_spire(cylindre_synthetique(R, A, H, gondolement=35.0), axe)
    v("une nappe gondolée fait DIVERGER les deux estimateurs",
      rg["desaccord_relatif"] > 0.4,
      f"désaccord {rg['desaccord_relatif']:.3f}  flèche {rg['rayon_fleche_vox']:.0f}  "
      f"cercle {rg['rayon_cercle_vox']:.0f}")
    v("... et le rayon est alors déclaré INDÉTERMINÉ", not rg["rayon_determine"],
      f"désaccord {rg['desaccord_relatif']:.3f}  résidu/flèche {rg['residu_sur_sagitta']:.3f}")
    v("le gondolement fait SURESTIMER l'angle, donc sous-estimer les tours nécessaires",
      rg["angle_rad"] > r["angle_rad"],
      f"{rg['angle_rad']:.4f} contre {r['angle_rad']:.4f}")

    # ---- L'ouverture angulaire, testee LA OU la coupure tombe ---------------------------
    droit = np.linspace(0.2, 0.5, 50)
    v("un arc ordinaire garde son ouverture",
      abs(etendue_angulaire(droit) - 0.3) < 1e-6, f"{etendue_angulaire(droit):.6f}")
    a_cheval = np.concatenate([np.linspace(math.pi - 0.15, math.pi, 25),
                               np.linspace(-math.pi, -math.pi + 0.15, 25)])
    v("un arc à cheval sur la coupure ±π garde son ouverture",
      abs(etendue_angulaire(a_cheval) - 0.3) < 0.02,
      f"{etendue_angulaire(a_cheval):.4f} au lieu de 0.30")

    # ---- L'espacement entre nappes -----------------------------------------------------
    m2 = cylindre_synthetique(R + 20.0, A, H)
    e = espacement(m, m2)
    v("l'espacement de deux nappes concentriques est l'écart de rayon",
      abs(e - 20.0) < 1.0, f"{e:.2f} au lieu de 20")
    # ⚠ Temoin du temoin : deux nappes CONFONDUES doivent donner zero, sinon la mesure
    # ci-dessus pourrait etre satisfaite par n'importe quelle distance de grille.
    v("deux nappes confondues ont un espacement nul", espacement(m, m) < 1e-6,
      f"{espacement(m, m):.4f}")

    # ---- ⭐⭐ La chaine ENTIERE, lue depuis le disque ------------------------------------
    # C'est ce qui manquait au premier jet : les controles ci-dessus exercent les briques,
    # pas la fonction qui choisit les axes, aligne les normales et assemble.
    with tempfile.TemporaryDirectory() as tmp:
        racine = Path(tmp) / "chaine"
        # ⚠⚠ La spire 0 est TRANSPOSEE et les suivantes non -- c'est exactement ce que la
        # chaine reelle fait, et c'est la panne qui rendait des rayons de 300 km.
        chaine = [cylindre_synthetique(R + 20.0 * i, A, H, bruit=1.0, graine=11 + i,
                                       circ_en_colonnes=(i == 0))
                  for i in range(4)]
        ecrire_chaine(racine, chaine)
        res = analyser_chaine(racine, voxel_um=1.0)
        v("la chaîne entière est lue depuis le disque", len(res["spires"]) == 4,
          f"{len(res['spires'])} spires")
        if len(res["spires"]) == 4:
            v("chaque spire a son PROPRE axe circonférentiel",
              res["axes_circonferentiels"] == [0, 1, 1, 1],
              str(res["axes_circonferentiels"]))
            rayons = [s["rayon_cercle_vox"] for s in res["spires"]]
            v("les quatre rayons sont retrouvés à 3 % malgré la transposition",
              all(abs(x - (R + 20.0 * i)) < 0.03 * R for i, x in enumerate(rayons)),
              " ".join(f"{x:.0f}" for x in rayons))
            v("les rayons CROISSENT le long de la chaîne",
              all(b > a for a, b in zip(rayons, rayons[1:])),
              " ".join(f"{x:.0f}" for x in rayons))
            esp = [s["espacement_vox"] for s in res["spires"][1:]]
            v("l'espacement mesuré est celui qu'on a construit",
              all(abs(x - 20.0) < 2.0 for x in esp), " ".join(f"{x:.1f}" for x in esp))
            v("la fraction de tour est celle de l'ouverture construite",
              abs(res["spires"][0]["fraction_de_tour"] - A / (2 * math.pi)) < 0.05 * A,
              f"{res['spires'][0]['fraction_de_tour']:.4f}")
            # ⚠ On asserte la PROPRIETE de minorant, pas une valeur serree : le bruit et
            # le gondolement gonflent la fleche, donc l'angle, donc ce nombre est
            # systematiquement BAS. Exiger 20,9 a 1,5 pres reviendrait a nier ce biais --
            # le temoin echouait justement la, a 19,2, ce qui est le biais et non un defaut.
            n_vrai = 2 * math.pi / A
            v("le nombre de fenêtres par tour est un MINORANT du vrai",
              res["spires"][0]["spires_par_tour_min"] <= n_vrai + 0.2,
              f"{res['spires'][0]['spires_par_tour_min']:.1f} contre {n_vrai:.1f}")
            v("... et il reste du bon ordre de grandeur",
              res["spires"][0]["spires_par_tour_min"] > 0.6 * n_vrai,
              f"{res['spires'][0]['spires_par_tour_min']:.1f} contre {n_vrai:.1f}")
            v("l'aire utile est calculée pour chaque spire",
              all("aire_valide_cm2" in s for s in res["spires"]))

            # ⭐ La troncature : comparer deux campagnes de longueurs differentes sur un
            # taux « par tour » est faux, donc l'outil doit savoir s'arreter au meme rang.
            rt2 = analyser_chaine(racine, voxel_um=1.0, tours=2)
            v("une chaîne peut être tronquée à ses N premiers tours",
              len(rt2["spires"]) == 2, f"{len(rt2['spires'])} spires")
            v("... et les tours gardés sont bien les PREMIERS",
              [x["nom"] for x in rt2["spires"]] == ["spire00", "spire01"],
              str([x["nom"] for x in rt2["spires"]]))
            v("... et leurs mesures sont identiques à celles de la chaîne entière",
              abs(rt2["spires"][1]["espacement_vox"]
                  - res["spires"][1]["espacement_vox"]) < 1e-9)
            v("tronquer à plus long que la chaîne la rend entière",
              len(analyser_chaine(racine, 1.0, tours=99)["spires"]) == 4)

        # Une chaine plane doit etre REFUSEE, avec sa raison, et non mesuree.
        racine2 = Path(tmp) / "plate"
        ecrire_chaine(racine2, [plaque_plane(), plaque_plane()])
        res2 = analyser_chaine(racine2, voxel_um=1.0)
        v("une chaîne plane est refusée", res2["spires"] == [], str(len(res2["spires"])))
        v("... et le refus dit pourquoi", "tourne" in res2.get("raison", ""),
          res2.get("raison", "(aucune raison)"))

        # ⚠⚠ La sentinelle REELLE est -1, pas (0,0,0) : c'est l'erreur qui a fait rendre
        # « surface plane » sur une chaine parfaitement courbe. Les deux sont testees.
        for nom_s, valeur in (("zéro", 0.0), ("-1", -1.0)):
            rac = Path(tmp) / f"troue_{valeur}"
            troue = cylindre_synthetique(R, A, H, bruit=1.0, graine=5)
            troue[8:20, 10:26, :] = valeur
            ecrire_chaine(rac, [troue, cylindre_synthetique(R + 20.0, A, H, bruit=1.0)])
            rt = analyser_chaine(rac, voxel_um=1.0)
            v(f"la sentinelle {nom_s} est écartée du compte",
              bool(rt["spires"]) and rt["spires"][0]["points"] == 40 * 30 - 12 * 16,
              f"{rt['spires'][0]['points'] if rt['spires'] else 0} au lieu de "
              f"{40 * 30 - 12 * 16}")
            v(f"une chaîne trouée par des {nom_s} reste courbe",
              bool(rt["spires"]) and abs(rt["spires"][0]["rayon_cercle_vox"] - R) < 0.03 * R,
              f"{rt['spires'][0]['rayon_cercle_vox']:.1f}" if rt["spires"] else "aucune")
            v(f"la fraction valide est rapportée avec la sentinelle {nom_s}",
              bool(rt["spires"])
              and abs(rt["spires"][0]["fraction_valide"] - (1 - 192 / 1200)) < 1e-9,
              f"{rt['spires'][0]['fraction_valide']:.4f}" if rt["spires"] else "aucune")

        # ⭐ Le maillage POUSSE est prefere a l'aplati, et les deux sont distingues : une
        # spire porte les deux, avec des grilles differentes.
        racine5 = Path(tmp) / "deux_maillages"
        ecrire_chaine(racine5, [cylindre_synthetique(R, A, H, n_theta=40, n_h=30)],
                      sous="trace/neighbor_out_1")
        ecrire_chaine(racine5, [cylindre_synthetique(R, A, H, n_theta=24, n_h=18)],
                      sous="plat")
        r_pousse = analyser_chaine(racine5, 1.0, prefere="trace")
        r_plat = analyser_chaine(racine5, 1.0, prefere="plat")
        v("le maillage poussé est choisi par défaut",
          r_pousse["spires"][0]["grille"] == [40, 30],
          str(r_pousse["spires"][0]["grille"]))
        v("... et l'aplati quand on le demande",
          r_plat["spires"][0]["grille"] == [24, 18], str(r_plat["spires"][0]["grille"]))
        v("le maillage mesuré est nommé dans le résultat",
          r_pousse["spires"][0]["maillage"] == "poussé"
          and r_plat["spires"][0]["maillage"] == "aplati",
          f"{r_pousse['spires'][0]['maillage']} / {r_plat['spires'][0]['maillage']}")

        # Un dossier sans maillage lisible doit etre refuse, pas plante.
        (Path(tmp) / "vide").mkdir()
        v("un dossier sans maillage est refusé",
          analyser_chaine(Path(tmp) / "vide", 1.0)["spires"] == [])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


# ⚠ La figure vit dans ce fichier et non dans un `figure_*.py` separe, contrairement a la
# convention du depot : elle a exactement UN producteur et UN consommateur, et l'isoler
# creerait un second fichier dont la seule fonction serait de relire un JSON que celui-ci
# vient d'ecrire. Le depot a deja assez de scripts qui se relisent entre eux.
# ⚠ La table de traduction de la figure. Les cles matchent le texte SOURCE.
ANGLAIS = {
    "Où la chaîne se trouve dans le rouleau": "Where the chain sits inside the scroll",
    " nappes — ce qui est mesurable, et ce qui ne l'est pas":
        " sheets — what is measurable, and what is not",
    "Rayon de la nappe — deux estimateurs indépendants":
        "Sheet radius — two independent estimators",
    "arc / angle (flèche)": "arc / angle (sagitta)",
    "ajustement de cercle": "circle fit",
    " nappes sur ": " sheets out of ",
    " ont un rayon INDÉTERMINÉ : les deux estimateurs se contredisent.":
        " have an UNDETERMINED radius: the two estimators contradict each other.",
    "écart": "gap",
    "Un tour déroulé — ce que la chaîne couvre":
        "One unrolled turn — what the chain covers",
    "largeur du cadre = un tour complet de papyrus":
        "frame width = one full turn of papyrus",
    "chaque fenêtre en couvre ": "each window covers ",
    " — il en faudrait ": " of it — one would need ",
    "AU MOINS ": "AT LEAST ",
    ", côte à côte,": ", side by side,",
    "pour fermer UN seul tour. Une chaîne radiale est une colonne, ":
        "to close ONE turn. A radial chain is a column, ",
    "pas une bande.": "not a strip.",
    "L'écart entre nappes, lui, ne suppose aucun modèle : ":
        "The sheet-to-sheet gap assumes no model at all: ",
    "médiane ": "median ",
    "spire": "sheet",
    "nappe ": "sheet ",
}


def dessiner(res: dict, sortie: Path, anglais: bool = False) -> None:
    """Deux panneaux : l'incertitude du rayon, puis ce que la chaine couvre d'un tour.

    ⚠⚠ Le panneau de gauche montre les DEUX estimateurs de rayon, pas une moyenne. Sur les
    vraies nappes ils se separent d'un facteur deux, et une courbe unique aurait laisse
    croire a une mesure. Une figure doit montrer l'incertitude qu'elle a, sinon elle en
    fabrique une certitude.

    ⭐ Le panneau de droite ne depend d'AUCUN modele de rayon : l'angle balaye vient de la
    fleche, donc la couverture est mesuree et non deduite. C'est le panneau qui porte la
    conclusion -- une chaine radiale est une colonne, pas une bande.
    """
    from PIL import Image, ImageDraw, ImageFont
    from langue import Traduisant

    spires = [s for s in res["spires"] if s.get("angle_rad", 0.0) > 0]
    if not spires:
        return
    L, H = 1180, 640
    img = Image.new("RGB", (L, H), (255, 255, 255))
    # ⭐ Envelopper l'objet de dessin suffit a traduire la figure entiere.
    art = Traduisant(ImageDraw.Draw(img), ANGLAIS if anglais else None)
    try:
        f_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        f_n = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        f_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        f_t = f_n = f_p = ImageFont.load_default()

    AMBRE, ENCRE, GRIS, PALE = (196, 116, 24), (30, 30, 30), (150, 150, 150), (222, 222, 222)
    art.text((28, 20), "Où la chaîne se trouve dans le rouleau", fill=ENCRE, font=f_t)
    art.text((28, 42), f"{len(spires)} nappes — ce qui est mesurable, et ce qui ne l'est pas",
             fill=(110, 110, 110), font=f_n)

    # ---- Panneau gauche : les deux estimateurs de rayon ---------------------------------
    X0, X1, Y0, Y1 = 90, 520, 560, 110
    art.text((28, 84), "Rayon de la nappe — deux estimateurs indépendants",
             fill=ENCRE, font=f_n)
    vals = [x for s in spires for x in (s["rayon_fleche_mm"], s.get("rayon_cercle_mm"))
            if x and math.isfinite(x)]
    # ⚠ Echelle logarithmique : les deux estimateurs se separent d'un facteur, pas d'un
    # ecart, et sur une echelle lineaire l'un des deux ecraserait l'autre contre l'axe.
    lo, hi = max(min(vals) * 0.7, 1.0), max(vals) * 1.4
    def ypos(mm):
        return Y0 + (Y1 - Y0) * (math.log(max(mm, lo)) - math.log(lo)) / (math.log(hi) - math.log(lo))
    art.line([X0, Y0, X1, Y0], fill=GRIS)
    art.line([X0, Y0, X0, Y1], fill=GRIS)
    for mm in (10, 20, 50, 100, 200, 500, 1000):
        if lo < mm < hi:
            y = ypos(mm)
            art.line([X0 - 4, y, X1, y], fill=(240, 240, 240))
            art.text((X0 - 46, y - 7), f"{mm} mm", fill=(140, 140, 140), font=f_p)
    n = len(spires)
    for i, sp in enumerate(spires):
        x = X0 + 24 + i * ((X1 - X0 - 40) / max(n - 1, 1))
        rf, rc = sp["rayon_fleche_mm"], sp.get("rayon_cercle_mm")
        if rc and math.isfinite(rc):
            art.line([x, ypos(rf), x, ypos(rc)], fill=(232, 210, 186), width=5)
            art.ellipse([x - 4, ypos(rc) - 4, x + 4, ypos(rc) + 4], outline=GRIS, width=2)
        art.ellipse([x - 4, ypos(rf) - 4, x + 4, ypos(rf) + 4], fill=AMBRE)
        art.text((x - 8, Y0 + 8), sp["nom"][-2:], fill=(140, 140, 140), font=f_p)
    yl = Y0 + 26
    art.ellipse([X0 + 6, yl, X0 + 14, yl + 8], fill=AMBRE)
    art.text((X0 + 20, yl - 2), "arc / angle (flèche)", fill=(110, 110, 110), font=f_p)
    art.ellipse([X0 + 176, yl, X0 + 184, yl + 8], outline=GRIS, width=2)
    art.text((X0 + 190, yl - 2), "ajustement de cercle", fill=(110, 110, 110), font=f_p)
    indet = sum(1 for s in spires if not s.get("rayon_determine"))
    art.text((28, 600), f"{indet} nappes sur {len(spires)} ont un rayon INDÉTERMINÉ : les deux "
                        f"estimateurs se contredisent.", fill=(120, 120, 120), font=f_p)
    esp = [s["espacement_um"] for s in spires
           if s.get("espacement_um") and math.isfinite(s["espacement_um"])]
    if esp:
        art.text((28, 617), f"L'écart entre nappes, lui, ne suppose aucun modèle : "
                            f"médiane {sorted(esp)[len(esp) // 2]:.0f} µm.",
                 fill=(120, 120, 120), font=f_p)

    # ---- Panneau droit : un tour deroule ------------------------------------------------
    A0, A1 = 640, 1108
    B0 = 120
    hb = min(38, int((520 - B0) / max(len(spires), 1)))
    art.text((A0, 84), "Un tour déroulé — ce que la chaîne couvre", fill=ENCRE, font=f_n)
    for i, sp in enumerate(spires):
        y = B0 + i * hb
        art.rectangle([A0, y, A1, y + hb - 6], outline=PALE)
        frac = sp["fraction_de_tour"]
        # ⚠ Position horizontale = position angulaire MESUREE, pas un decalage decoratif :
        # une chaine radiale reste dans la meme fenetre, et c'est le fait a montrer.
        centre = ((sp.get("theta_milieu", 0.0) + math.pi) % (2 * math.pi)) / (2 * math.pi)
        w = max(2.0, frac * (A1 - A0))
        xa = A0 + centre * (A1 - A0) - w / 2
        art.rectangle([xa, y, xa + w, y + hb - 6], fill=AMBRE)
        art.text((A0 - 62, y + 4), sp["nom"], fill=(140, 140, 140), font=f_p)
        e = sp.get("espacement_um")
        if e is not None and math.isfinite(e):
            art.text((A1 + 6, y + 4), f"{e:.0f} µm", fill=GRIS, font=f_p)
    y = B0 + len(spires) * hb + 16
    moy = sum(s["fraction_de_tour"] for s in spires) / len(spires)
    nmin = min(s["spires_par_tour_min"] for s in spires)
    art.text((A0, y), "largeur du cadre = un tour complet de papyrus", fill=(120, 120, 120),
             font=f_p)
    art.text((A0, y + 17), f"chaque fenêtre en couvre {moy * 100:.0f} % — il en faudrait "
                           f"AU MOINS {nmin:.0f}, côte à côte,", fill=(120, 120, 120), font=f_p)
    art.text((A0, y + 34), "pour fermer UN seul tour. Une chaîne radiale est une colonne, "
                           "pas une bande.", fill=(120, 120, 120), font=f_p)
    art.text((A1 + 6, B0 - 16), "écart", fill=GRIS, font=f_p)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    # ⚠⚠ Une figure a moitie traduite a l'air traduite. On REFUSE de l'ecrire.
    if anglais and art.intraduits():
        print("des libellés n'ont pas de traduction :", file=sys.stderr)
        for _t in art.intraduits():
            print(f"    « {_t} »", file=sys.stderr)
        raise SystemExit(1)
    img.save(sortie)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", type=Path)
    ap.add_argument("--voxel-um", type=float, default=8.64)
    ap.add_argument("--tours", type=int, default=None,
                    help="ne mesurer que les N premières spires — pour comparer deux "
                         "campagnes de longueurs différentes à profondeur ÉGALE")
    ap.add_argument("--maillage", choices=("trace", "plat"), default="trace",
                    help="lequel des deux maillages d'une spire mesurer (défaut : celui "
                         "que la chaîne a fait pousser)")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--figure", type=Path)
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--anglais", action="store_true",
                    help="écrire la figure en anglais (pour l'article)")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.dossier is None:
        ap.error("donner un dossier de chaîne, ou --verifier")
    if not a.dossier.is_dir():
        print(f"absent : {a.dossier}", file=sys.stderr)
        return 1

    res = analyser_chaine(a.dossier, a.voxel_um, a.maillage, a.tours)
    if not res["spires"]:
        print(f"⚠ {res.get('raison', 'rien à mesurer')}", file=sys.stderr)
        return 1

    ac = res["axes_circonferentiels"]
    mix = "colonnes" if all(x == 0 for x in ac) else \
          "rangées" if all(x == 1 for x in ac) else \
          "MIXTE — la grille est transposée d'une spire à l'autre"
    print(f"  axe du rouleau : [{res['axe'][0]:+.3f} {res['axe'][1]:+.3f} "
          f"{res['axe'][2]:+.3f}]   circonférence le long de : {mix}")
    print(f"  {'spire':9s} {'grille':>9s} {'valide':>7s} {'aire':>8s} {'arc':>8s} "
          f"{'tour':>7s} {'haut.':>7s} {'écart':>8s} {'R flèche':>10s} {'R cercle':>10s} "
          f"{'rayon':>10s}")
    for s in res["spires"]:
        if s.get("angle_rad", 0.0) <= 0:
            print(f"  {s['nom']:9s}  — {s['points']} points valides, rien à mesurer")
            continue
        e = s.get("espacement_um")
        rc = s.get("rayon_cercle_mm")
        print(f"  {s['nom']:9s} {s['grille'][0]}x{s['grille'][1]:<5} "
              f"{s['fraction_valide'] * 100:6.1f}% {s['aire_valide_cm2']:6.2f}cm² "
              f"{s['arc_mm']:6.1f}mm {s['fraction_de_tour'] * 100:6.1f}% "
              f"{s['hauteur_mm']:5.1f}mm "
              f"{(f'{e:6.0f}µm' if e is not None and math.isfinite(e) else '     —'):>8s} "
              f"{s['rayon_fleche_mm']:8.1f}mm "
              f"{(f'{rc:8.1f}mm' if rc and math.isfinite(rc) else '       —'):>10s} "
              f"{'déterminé' if s.get('rayon_determine') else 'INDÉTERM.':>10s}")

    bons = [s for s in res["spires"] if s.get("angle_rad", 0.0) > 0]
    if len(bons) >= 2:
        a0, a1 = bons[0]["aire_valide_cm2"], bons[-1]["aire_valide_cm2"]
        n = len(bons) - 1
        if a0 > 0 and a1 > 0:
            print(f"\n  ⭐ érosion UTILE : {a0:.2f} → {a1:.2f} cm² sur {n} tours "
                  f"({100 * (1 - a1 / a0):.0f} % au total, "
                  f"{100 * (1 - (a1 / a0) ** (1 / n)):.1f} % par tour)")
            print(f"     part de sommets valides : {bons[0]['fraction_valide'] * 100:.0f} % "
                  f"→ {bons[-1]['fraction_valide'] * 100:.0f} % — la grille se creuse "
                  f"autant qu'elle rétrécit,\n     donc une érosion calculée sur l'aire de "
                  f"GRILLE ignore précisément la moitié qui disparaît")
    total = sum(s["aire_valide_cm2"] for s in bons)
    print(f"     aire utile TOTALE de la chaîne : {total:.1f} cm² sur {len(bons)} nappes")
    esp = [s["espacement_um"] for s in bons
           if s.get("espacement_um") is not None and math.isfinite(s["espacement_um"])]
    if esp:
        t = sorted(esp)
        print(f"\n  ⭐ écart entre nappes : médiane {t[len(t) // 2]:.0f} µm "
              f"(de {t[0]:.0f} à {t[-1]:.0f}) — aucun modèle, une distance au plus proche "
              f"voisin.\n     C'est le seul chiffre qui dise que la chaîne avance d'UNE "
              f"nappe à la fois.")
    moy = sum(s["fraction_de_tour"] for s in bons) / len(bons)
    nmin = min(s["spires_par_tour_min"] for s in bons)
    print(f"\n  ⭐ chaque fenêtre couvre {moy * 100:.1f} % d'un tour — il en faudrait AU "
          f"MOINS {nmin:.0f} côte à côte\n     pour fermer UN tour (minorant : le "
          f"gondolement gonfle la flèche, donc l'angle)")
    indet = [s["nom"] for s in bons if not s.get("rayon_determine")]
    if indet:
        print(f"\n  ⚠⚠ rayon INDÉTERMINÉ sur {len(indet)}/{len(bons)} nappes : les deux "
              f"estimateurs se contredisent.\n     Une nappe de papyrus gondole de "
              f"{bons[0]['residu_vox'] * res['voxel_um'] / 1000:.1f} mm quand les nappes "
              f"sont à {(sorted(esp)[len(esp) // 2] / 1000 if esp else 0):.3f} mm l'une de "
              f"l'autre :\n     un cercle unique n'est pas un modèle de cette surface, "
              f"donc « le rayon de la spire » n'est pas\n     une quantité que ce maillage "
              f"détermine. On refuse de la publier.")
    print("\n  ⚠ une chaîne radiale est une COLONNE de nappes dans une même fenêtre "
          "angulaire,\n    pas une bande de papyrus déroulé : deux nappes voisines sont "
          "séparées,\n    le long du papyrus, par la circonférence entière qu'on ne "
          "possède pas.")

    if a.json:
        a.json.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    if a.figure:
        dessiner(res, a.figure, a.anglais)
        print(f"  figure : {a.figure}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
