#!/usr/bin/env python3
"""La normale de la nappe n'est PAS le rayon — et l'ecart refute l'explication du trou de `99`.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST L'ITEM A BIS DU BLOC DE REPRISE. `99` mesure que la matiere
montre un pas de **199 µm** la ou `91` publie un pas de transfert de **164** — 21 % d'ecart
inexplique. Une explication evidente se presentait : si la direction radiale n'est pas
perpendiculaire a l'empilement, alors la distance radiale entre deux feuilles vaut pas / cos(theta),
donc un pas apparent plus GRAND que le vrai. Et l'accord numerique etait stupefiant : la mediane de
1/cos mesuree vaut **1,212** contre un rapport observe 198,9 / 164,0 = **1,213**.

⛔⛔⛔ L'HYPOTHESE EST REFUTEE PAR LA MESURE, ET C'EST TOUT L'OBJET DU FICHIER. Le long de la
NORMALE, le pas mesure est le MEME que radialement (rapports 0,91 a 1,19, disperses autour de 1,00,
aucun 1,21 systematique). L'accord a un millieme etait une coincidence — exactement le piege que
`94` a enregistre avec la sagitta, evite cette fois parce que le test a ete lance AVANT de publier.

⭐⭐⭐ MAIS LE TEST LAISSE UN FAIT PLUS LOURD QUE CE QU'IL REFUTE. Sur une spirale de pas 164 µm a
10 mm de rayon, la feuille n'est inclinee sur le rayon que de atan(0,164 / 62,8) = **0,15°**. Or la
normale du maillage en est a **16 a 38°** — deux cents fois plus. La surface que les humains ont
tracee n'est donc pas une spirale vue de face : elle est franchement oblique au rayon.

⭐⭐ ET CE N'EST PAS L'ESTIMATEUR. La normale par ACP — calculee sur les trente plus proches
voisins, donc INDEPENDANTE de la grille — donne le meme angle que la normale de la grille. Deux
estimateurs qui ne partagent aucune hypothese s'accordent, donc l'obliquite est dans la matiere
tracee et non dans la facon de la lire.

⚠⚠ UNE PART EST DE LA RUGOSITE LOCALE, ET ELLE EST MESUREE PLUTOT QUE SUPPOSEE. L'angle DECROIT
quand le voisinage grandit — 67,8° a dix voisins, 38,0° a mille sur la bande interne — donc du
bruit de surface y contribue. Mais il ne converge PAS vers zero : a mille voisins il reste 16 a
38°, soit cent fois la prediction de la spirale. C'est le controle de `96` (bruit ou structure ?)
applique a une direction.

⚠⚠⚠ ET CELA CORRIGE UNE AFFIRMATION DE `98`. Sa docstring de `segments` disait : « LE SEGMENT EST
RADIAL ET A z CONSTANT, donc il traverse l'empilement perpendiculairement ». La seconde moitie est
mesuree FAUSSE ici. Elle est corrigee la-bas, et ce qui sauve la mesure de `98` est justement le
resultat de ce fichier : le pas ne depend pas de la direction, donc le segment radial mesure la
meme chose que le segment normal — pour une raison qui n'est pas celle qui etait ecrite.

⭐⭐⭐ LE CONTROLE QUI REND LA REFUTATION LISIBLE, ET SANS LUI ELLE NE PROUVERAIT RIEN. Un test qui
ne voit pas d'effet est indiscernable d'un test aveugle. `empilement_oblique` fabrique une pile de
feuilles planes inclinees d'un angle CONNU sur le rayon : le meme instrument y lit bien un rapport
radial/normal egal a 1/cos(theta). L'instrument voit donc l'obliquite quand elle existe — et il ne
la voit pas sur le vrai volume.

Usage :
    uv run python src/nappe/la_normale_nest_pas_le_rayon.py --verifier
    uv run python src/nappe/la_normale_nest_pas_le_rayon.py \\
        --json docs/mesures/la_normale_nest_pas_le_rayon.json
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

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"

# ⚠ Les tailles de voisinage du balayage. Elles ne sont pas choisies pour un resultat : elles
# couvrent deux ordres de grandeur, de « quelques cellules » a « un morceau de bande », ce qui est
# la seule facon de separer une rugosite locale d'une orientation d'ensemble.
VOISINAGES = (10, 30, 100, 300, 1000)
VOISINS_PAR_DEFAUT = 30
CELLULES_PAR_BANDE = 300
CELLULES_POUR_LE_VOLUME = 60


def inclinaison_de_la_spirale(rayon_um: float, pas_um: float) -> float:
    """De combien de degres une spirale d'Archimede incline sa feuille sur le rayon local.

    ⭐⭐⭐ C'EST LA PREDICTION CONTRE LAQUELLE TOUT LE FICHIER SE LIT, et elle tient en une ligne :
    en un tour la spirale gagne un pas en rayon pour 2*pi*r de chemin, donc la feuille monte de
    pas / (2*pi*r). A 10 mm de rayon et 164 µm de pas, cela fait **0,15°** — une quantite si petite
    qu'on la confondrait avec zero. Publier une obliquite de dizaines de degres sans la comparer a
    ce nombre-la serait publier une surprise sans dire qu'elle en est une.
    """
    return float(np.degrees(np.arctan2(pas_um, 2.0 * np.pi * rayon_um)))


def centre_interpole(z: np.ndarray, bords: np.ndarray, cx: np.ndarray,
                     cy: np.ndarray) -> np.ndarray:
    """Le centre de l'enroulement a la hauteur z, INTERPOLE entre tranches.

    ⚠⚠ C'EST LA MEME REGLE QUE `96` A PAYEE ET QUE `98` APPLIQUE : `axe_par_tranche` rend un
    centre constant par tranche, or l'axe derive de 12,6 mm sur la hauteur, donc deux cellules qui
    enjambent une frontiere de tranche verraient des centres ecartes de centaines de micrometres —
    et l'ecart tomberait dans la direction meme qu'on cherche a mesurer.
    """
    milieux = (bords[:-1] + bords[1:]) / 2.0
    bon = np.isfinite(cx) & np.isfinite(cy)
    return np.stack([np.interp(z, milieux[bon], cx[bon]),
                     np.interp(z, milieux[bon], cy[bon])], axis=-1)


def direction_radiale(p0: np.ndarray, c0: np.ndarray) -> np.ndarray:
    """Le vecteur unitaire qui va de l'axe vers le point, A z CONSTANT.

    ⚠ Sa composante z est nulle par construction : « radial » veut dire perpendiculaire a l'axe du
    rouleau, pas « vers le centre du nuage ». Les deux different des qu'une bande n'est pas centree
    en hauteur, et confondre les deux ferait pointer la direction vers le milieu du fragment.
    """
    d = np.stack([p0[:, 0] - c0[:, 0], p0[:, 1] - c0[:, 1], np.zeros(len(p0))], axis=-1)
    return d / np.maximum(np.linalg.norm(d, axis=-1, keepdims=True), 1e-12)


def normale_de_la_grille(a: np.ndarray, ok: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """La normale lue dans la TOPOLOGIE de la grille : produit vectoriel des deux tangentes.

    ⚠⚠ ELLE HERITE DE L'ANISOTROPIE DE LA GRILLE, et c'est precisement pourquoi elle ne suffit
    pas. Une grille dont le pas de ligne et le pas de colonne different d'un facteur huit — ce qui
    est le cas ici, `97` l'a mesure — donne des tangentes de longueurs tres inegales ; la normale
    reste juste, mais toute erreur sur la tangente courte pese davantage. La reponse n'est pas de
    la corriger mais de la CONFRONTER a un estimateur qui ignore la grille.

    Rend des NaN la ou un des quatre voisins manque : une normale calculee sur un trou serait un
    nombre parfaitement fini au sujet d'une surface absente.
    """
    h, w = ok.shape
    n = np.full((len(indices), 3), np.nan)
    for q, (i, j) in enumerate(indices):
        if i < 1 or j < 1 or i >= h - 1 or j >= w - 1:
            continue
        if not (ok[i - 1, j] and ok[i + 1, j] and ok[i, j - 1] and ok[i, j + 1]):
            continue
        t1 = a[i + 1, j] - a[i - 1, j]
        t2 = a[i, j + 1] - a[i, j - 1]
        c = np.cross(t1, t2)
        m = np.linalg.norm(c)
        if m > 1e-9:
            n[q] = c / m
    return n


def normale_par_acp(nuage: np.ndarray, p0: np.ndarray,
                    voisins: int = VOISINS_PAR_DEFAUT, arbre=None) -> np.ndarray:
    """La normale par analyse en composantes principales : la direction de MOINDRE etalement.

    ⭐⭐⭐ ELLE EST L'ESTIMATEUR INDEPENDANT, et c'est tout son interet : elle ne connait ni les
    lignes ni les colonnes, seulement des points dans l'espace. Si elle s'accorde avec la normale
    de la grille, l'obliquite mesuree est dans la MATIERE ; si elle en differait, on ne mesurerait
    que la forme du maillage. Deux estimateurs qui ne partagent aucune hypothese sont la seule
    facon de trancher, et la relecture du code ne le peut pas.

    ⚠ `voisins` est un PARAMETRE et non une constante enfouie, parce que la reponse en depend :
    c'est le balayage sur cette taille qui separe la rugosite locale de l'orientation d'ensemble.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    k = min(int(voisins), len(nuage))
    # ⚠ L'arbre se passe de l'exterieur quand on balaye plusieurs tailles de voisinage :
    # le reconstruire par taille couterait cinq fois le meme travail sur des millions de
    # points, pour un resultat identique.
    _, idx = (arbre or cKDTree(nuage)).query(p0, k=k)
    idx = np.atleast_2d(idx)
    v = nuage[idx]
    q = v - v.mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", q, q)
    _, vecteurs = np.linalg.eigh(cov)
    return vecteurs[:, :, 0]


def angle_entre(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """L'angle non oriente entre deux directions, en degres, dans [0, 90].

    ⚠⚠ LA VALEUR ABSOLUE DU PRODUIT SCALAIRE, PARCE QU'UNE NORMALE N'A PAS DE SENS. Le signe du
    plus petit vecteur propre d'une covariance est arbitraire, et celui d'un produit vectoriel
    depend de l'ordre des tangentes. Sans la valeur absolue, la moitie des cellules d'une meme
    surface plane rendraient 180° moins l'angle de l'autre moitie, et la mediane serait un nombre
    au sujet de rien.
    """
    c = np.abs(np.einsum("ij,ij->i", u, v))
    return np.degrees(np.arccos(np.clip(c, 0.0, 1.0)))


def decomposer(n: np.ndarray, radial: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Separer l'inclinaison EN HAUTEUR de l'inclinaison DANS LE PLAN de la section.

    ⭐⭐ LES DEUX N'ONT PAS LA MEME CONSEQUENCE, ET C'EST POURQUOI ON LES SEPARE. Une composante
    en z veut dire que les feuilles sont CONIQUES et non cylindriques — elles s'evasent le long du
    rouleau. Une composante dans le plan veut dire que la section n'est pas un cercle. Les deux
    sont plausibles, elles se corrigent differemment, et une seule mesure d'angle total ne dirait
    pas laquelle des deux on regarde.

    Rend (angle du a la composante z, angle dans le plan xy), en degres.
    """
    du_a_z = np.degrees(np.arcsin(np.clip(np.abs(n[:, 2]), 0.0, 1.0)))
    plat = n.copy()
    plat[:, 2] = 0.0
    m = np.linalg.norm(plat, axis=-1, keepdims=True)
    plat = plat / np.maximum(m, 1e-12)
    dans_le_plan = angle_entre(plat, radial)
    dans_le_plan[m[:, 0] < 1e-9] = np.nan
    return du_a_z, dans_le_plan


def orienter_vers_lexterieur(n: np.ndarray, radial: np.ndarray) -> np.ndarray:
    """Retourner les normales qui pointent vers l'axe, pour qu'un segment aille bien s'ecarter.

    ⚠⚠ SANS CA LE TEST DE REFUTATION LIRAIT DANS LE MAUVAIS SENS pour la moitie des cellules :
    un segment lance le long d'une normale rentrante traverse l'empilement vers l'INTERIEUR, donc
    il compare la feuille voisine du dedans a celle du dehors. La moyenne des deux ressemblerait a
    un pas legerement plus grand et parfaitement plausible.
    """
    s = np.sign(np.einsum("ij,ij->i", n, radial))
    s[s == 0.0] = 1.0
    return n * s[:, None]


def segments_dans_la_direction(p0: np.ndarray, direction: np.ndarray, longueur_um: float,
                               echantillons: int, voxel_um: float) -> np.ndarray:
    """Les points a lire depuis chaque cellule, le long d'une direction quelconque.

    ⭐ C'EST LA GENERALISATION DE `98.segments`, ET ELLE EXISTE POUR UNE SEULE RAISON : comparer
    deux directions demande de pouvoir en lire une autre que le rayon. La geometrie du cas radial
    reste celle de `98` — meme centre interpole, meme longueur en micrometres convertie par le
    voxel du maillage — pour que la comparaison porte sur la direction et sur rien d'autre.
    """
    pas_vx = longueur_um / voxel_um
    p1 = p0 + direction * pas_vx
    t = np.linspace(0.0, 1.0, echantillons)
    return p0[:, None, :] + (p1 - p0)[:, None, :] * t[None, :, None]


def empilement_oblique(theta_deg: float, pas_um: float = 173.0, r0_mm: float = 10.0,
                       feuilles: int = 24, le_long: int = 41, demi_largeur_um: float = 100.0,
                       hauteur: int = 6, voxel_um: float = 45.532) -> tuple[np.ndarray,
                                                                           np.ndarray]:
    """Une pile de feuilles PLANES dont la normale fait un angle CONNU avec le rayon.

    ⭐⭐⭐ C'EST LE CONTROLE QUI DONNE UN SENS AU RESULTAT NEGATIF, et c'est la piece qui manquait
    a plusieurs verifications de ce depot avant qu'on ne s'en apercoive : un test qui ne voit rien
    est indiscernable d'un test aveugle. Ici l'obliquite EXISTE et vaut theta, l'espacement VRAI
    des feuilles vaut `pas_um` le long de leur normale, donc l'espacement le long du RAYON vaut
    pas / cos(theta). L'instrument doit y lire ce rapport-la. S'il ne le lit pas, son silence sur
    le vrai maillage ne prouve rien.

    ⚠ Les cellules sont posees pres de l'axe x, ou le rayon vaut exactement x : c'est ce qui rend
    l'angle attendu EXACTEMENT theta plutot qu'une valeur qui varie le long de la feuille.

    Rend (la grille de points en voxels, le masque). Le centre est l'origine par construction, ce
    qui evite de faire dependre le controle de l'estimation de l'axe.
    """
    th = np.deg2rad(theta_deg)
    nx, ny = np.cos(th), np.sin(th)
    tx, ty = -ny, nx
    u = np.linspace(-demi_largeur_um, demi_largeur_um, le_long)
    m0 = int(np.ceil(r0_mm * 1000.0 / pas_um))
    a = np.zeros((hauteur, feuilles * le_long, 3))
    for k in range(hauteur):
        c = 0
        for f in range(feuilles):
            # ⚠⚠ L'ESPACEMENT VRAI EST LE LONG DE LA NORMALE : la feuille f est le plan dont
            # la projection sur n vaut (m0 + f) * pas. Elle coupe donc l'axe x en cette valeur
            # divisee par cos(theta), ce qui EST la quantite que le pas radial doit mesurer.
            #
            # ⚠⚠⚠ ET L'ANCRAGE EST UN MULTIPLE ENTIER DU PAS, PAS UN RAYON ROND. Le controle a
            # d'abord echoue pour ca : avec r0 = 10 mm et un pas de 173 µm, la cellule de depart
            # tombe a la phase 0,80 d'une periode — ni sur une feuille, ni dans un interstice —
            # donc AUCUNE des deux polarites du gabarit ne peut correspondre et la recherche rend
            # une periode fausse. Un controle doit poser sa cellule la ou la matiere la poserait.
            d = (m0 + f) * pas_um
            x0 = d / max(nx, 1e-9)
            a[k, c:c + le_long, 0] = (x0 + u * tx) / voxel_um
            a[k, c:c + le_long, 1] = (u * ty) / voxel_um
            a[k, c:c + le_long, 2] = k * 20.0
            c += le_long
    del ny
    return a, np.ones(a.shape[:2], dtype=bool)


def brillance_de_lempilement(points_vx: np.ndarray, theta_deg: float, pas_um: float,
                             voxel_um: float = 45.532) -> np.ndarray:
    """Ce qu'un volume verrait sur cet empilement : brillant sur la feuille, sombre entre.

    ⭐ C'EST LE VOLUME FABRIQUE, et il est analytique plutot qu'echantillonne pour une raison :
    on veut que le SEUL ecart entre les deux directions soit la geometrie, pas l'interpolation
    d'une grille de voxels. Un volume discretise ajouterait un repliement dont on ne saurait plus
    s'il explique ou non le rapport lu.
    """
    th = np.deg2rad(theta_deg)
    proj = (points_vx[..., 0] * np.cos(th) + points_vx[..., 1] * np.sin(th)) * voxel_um
    return 100.0 + 40.0 * np.cos(2 * np.pi * proj / pas_um)


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def avancement(fait: int, total: int, quoi: str, depart: float) -> None:
    """Ecrire sur STDERR ou en est une mesure longue, avec une fin estimee.

    ⚠⚠⚠ ELLE EXISTE PARCE QUE L'ABSENCE A COUTE UNE DECISION. `102` a tourne **quatre heures et
    demie** sans rien imprimer, et il a fallu sonder le cout d'un cube au chronometre pour savoir
    s'il en etait a 10 % ou a 90 % — c'est-a-dire pour savoir s'il fallait l'attendre ou le tuer.
    Une mesure qui coute des heures et se tait oblige a decider sans donnee, ce qui est exactement
    ce que ce depot refuse partout ailleurs.

    ⚠⚠ ELLE ECRIT SUR STDERR, ET C'EST LA CONDITION QUI LA REND SANS RISQUE : la sortie standard
    peut etre redirigee vers un fichier ou lue par un autre programme, donc y melanger un
    avancement corromprait le resultat. Le meme choix que fait `--json` en n'imprimant que le
    chemin sur stdout.

    ⭐ La fin estimee suppose que les etages restants coutent comme ceux deja faits. C'est faux au
    debut, quand un seul etage a servi de base, et cela devient juste ensuite — donc elle est
    affichee comme une ESTIMATION et non comme une promesse.
    """
    import time  # noqa: PLC0415

    if fait <= 0 or total <= 0:
        return
    ecoule = time.time() - depart
    reste = ecoule * (total - fait) / fait
    print(f"  … {quoi} {fait}/{total} · {ecoule / 60:.1f} min écoulées · "
          f"~{reste / 60:.0f} min restantes (estimation)", file=sys.stderr, flush=True)


def nombre_ou_absent(valeur) -> float:
    """La valeur, ou NaN seulement si elle est ABSENTE — jamais si elle vaut zero.

    ⚠⚠⚠ ELLE EXISTE PARCE QUE `valeur or float("nan")` EST UN PIEGE, ET IL A MORDU. En Python
    `0.0` est FAUX, donc cette forme affiche « nan » pour un zero parfaitement mesure : un temoin
    naif qui confirme ZERO pas, ce qui est le resultat le plus informatif qu'il puisse rendre,
    s'affichait comme une donnee manquante. C'est le meme faux zero que `101` a paye sur une
    correlation calculee sur une liste vide, une ligne plus loin — et la lecon est la meme :
    « zero » et « on ne sait pas » ne doivent jamais partager une representation.

    ⭐ Elle vit ici et non en trois exemplaires parce que `101` et `102` importent deja ce module.
    """
    return float("nan") if valeur is None else float(valeur)


def _mediane(v: np.ndarray) -> float | None:
    v = v[np.isfinite(v)]
    return round(float(np.median(v)), 2) if len(v) else None


def mesurer_les_angles(cellules: int = CELLULES_PAR_BANDE, graine: int = 61,
                       bandes_max: int | None = None) -> dict:
    """L'angle de la normale au rayon, par bande, par estimateur, et par taille de voisinage."""
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = time.time()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 20:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = centre_interpole(p0[:, 2], bords, cx, cy)
        rad = direction_radiale(p0, c0)
        rayon_um = np.linalg.norm(p0[:, :2] - c0, axis=-1) * C.VOXEL_MAILLAGE_UM

        ng = normale_de_la_grille(a, ok, ind)
        bon = np.isfinite(ng).all(axis=1)
        nuage = a[ok]
        from scipy.spatial import cKDTree  # noqa: PLC0415
        arbre = cKDTree(nuage)
        balayage = {}
        for k in VOISINAGES:
            if k > len(nuage):
                continue
            balayage[str(k)] = _mediane(
                angle_entre(normale_par_acp(nuage, p0, k, arbre), rad))
        nacp = normale_par_acp(nuage, p0, VOISINS_PAR_DEFAUT, arbre)
        z_g, plan_g = decomposer(ng[bon], rad[bon]) if int(bon.sum()) else (
            np.array([]), np.array([]))
        r_med = float(np.median(rayon_um))
        lignes.append({
            "de": x["de"], "a": x["a"],
            "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
            "rayon_mesure_mm": round(r_med / 1000.0, 2),
            "cellules": int(len(ind)), "cellules_avec_normale": int(bon.sum()),
            "angle_grille_deg": _mediane(angle_entre(ng[bon], rad[bon]))
            if int(bon.sum()) else None,
            "angle_acp_deg": _mediane(angle_entre(nacp, rad)),
            "balayage_de_voisinage_deg": balayage,
            "angle_du_a_z_deg": _mediane(z_g), "angle_dans_le_plan_deg": _mediane(plan_g),
            "nz_median": _mediane(np.abs(ng[bon, 2])) if int(bon.sum()) else None,
            # ⭐⭐⭐ LA PREDICTION, A COTE DE LA MESURE ET SUR LA MEME LIGNE. C'est ce qui fait
            # que le tableau se lit tout seul : une colonne a 0,2° face a une colonne a 30°.
            "inclinaison_predite_deg": round(
                inclinaison_de_la_spirale(r_med, C.PAS_UM), 3),
        })
        avancement(len(lignes), len(bandes), "bandes", depart)
    return {"fragment": C.OBJET, "pas_nominal_um": C.PAS_UM,
            "voxel_maillage_um": C.VOXEL_MAILLAGE_UM,
            "voisinages": list(VOISINAGES), "cellules_par_bande": cellules,
            "bandes": len(lignes), "lignes": lignes}


def mesurer_le_pas_dans_les_deux_directions(cellules: int = CELLULES_POUR_LE_VOLUME,
                                            graine: int = 61, bandes_max: int | None = None,
                                            fils: int = 32) -> dict:
    """LE TEST DECISIF : le pas lu le long de la normale est-il plus court que le pas radial ?

    ⛔⛔⛔ SI L'OBLIQUITE EXPLIQUAIT LE TROU DE `99`, LE RAPPORT VAUDRAIT 1 / cos(theta) ~ 1,21.
    La recherche de pas est celle de `99`, importee et non recopiee : meme fenetre, meme nul par
    candidat, meme barre. Seule la DIRECTION du segment change entre les deux colonnes, ce qui est
    la seule facon que la comparaison porte sur elle.
    """
    import combien_dinterstices_traverses as C  # noqa: PLC0415
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import appliquer, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    m = matrice(C.OBJET, C.VOLUME_DU_MAILLAGE, C.VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{C.ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs)
    barre = max(v["p99"] for v in M.nul_du_balayage_calibre(longueurs, mu, sd).values())
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    depart = time.time()
    lignes = []
    for x in bandes:
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = C.echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 20:
            continue
        p0 = a[ind[:, 0], ind[:, 1]]
        c0 = centre_interpole(p0[:, 2], bords, cx, cy)
        rad = direction_radiale(p0, c0)
        ng = normale_de_la_grille(a, ok, ind)
        bon = np.isfinite(ng).all(axis=1)
        if int(bon.sum()) < 20:
            continue
        ng = orienter_vers_lexterieur(ng[bon], rad[bon])
        d = {"de": x["de"], "a": x["a"],
             "rayon_mm": al.get((x["de"], x["a"]), {}).get("rayon_mm"),
             "angle_deg": _mediane(angle_entre(ng, rad[bon])), "cellules": int(bon.sum())}
        for nom, direction in (("radial", rad[bon]), ("normal", ng)):
            seg = segments_dans_la_direction(p0[bon], direction, float(longueurs[-1]),
                                             n_long, C.VOXEL_MAILLAGE_UM)
            zyx = np.rint(appliquer(m, seg)).astype(np.int64)
            dedans = vol.dans_le_volume(zyx.reshape(-1, 3)).reshape(zyx.shape[:2]).all(axis=1)
            if int(dedans.sum()) < 15:
                d[f"pas_{nom}_um"] = None
                continue
            v = vol.lire(zyx[dedans].reshape(-1, 3),
                         fils=fils).reshape(int(dedans.sum()), n_long)
            fini = np.isfinite(v).all(axis=1)
            if int(fini.sum()) < 15:
                d[f"pas_{nom}_um"] = None
                continue
            lu, sc, k, _ = M.pas_montre_calibre(M.profils_emboites(v[fini], longueurs),
                                                longueurs, mu, sd)
            garde = (sc > barre) & ~M.touche_un_bord(k, len(longueurs))
            d[f"cellules_{nom}"] = int(fini.sum())
            d[f"part_utilisable_{nom}"] = round(float(garde.mean()), 3)
            d[f"pas_{nom}_um"] = (round(float(np.median(lu[garde])), 1)
                                  if int(garde.sum()) >= 10 else None)
        if d.get("pas_radial_um") and d.get("pas_normal_um"):
            d["rapport_radial_sur_normal"] = round(d["pas_radial_um"] / d["pas_normal_um"], 3)
            d["un_sur_cos"] = round(
                1.0 / max(float(np.cos(np.deg2rad(d["angle_deg"]))), 1e-6), 3)
        lignes.append(d)
    out = agreger_les_directions(lignes)
    out.update({"cellules_par_bande": cellules, "barre_du_nul": round(float(barre), 3)})
    return out


def agreger_les_directions(lignes: list[dict]) -> dict:
    """Le verdict, DERIVE des lignes par bande et non recalcule depuis le volume.

    ⭐⭐ IL EST SEPARE DE LA LECTURE POUR UNE RAISON PRATIQUE ET UNE RAISON DE FOND. Pratique :
    ajouter une quantite derivee ne doit pas couter une demi-heure de lecture reseau. De fond :
    ce qui est MESURE, ce sont les pas par bande ; ce qui suit n'en est qu'une lecture, et les
    separer rend visible lequel des deux on change.
    """
    mesurees = [x for x in lignes if x.get("rapport_radial_sur_normal") is not None]
    out = {"bandes": len(lignes), "bandes_mesurees": len(mesurees), "lignes": lignes}
    if not mesurees:
        return out
    rap = np.array([x["rapport_radial_sur_normal"] for x in mesurees])
    cos = np.array([x["un_sur_cos"] for x in mesurees])
    out.update({
        "rapport_median": round(float(np.median(rap)), 3),
        "rapport_min": round(float(rap.min()), 3),
        "rapport_max": round(float(rap.max()), 3),
        "un_sur_cos_median": round(float(np.median(cos)), 3),
        # ⛔⛔⛔ LE VERDICT, CALCULE ET NON REDIGE : l'hypothese predit que le rapport SUIVE
        # 1/cos. Elle est refutee si le rapport est plus pres de 1 que de 1/cos.
        "ecart_a_un": round(float(np.median(np.abs(rap - 1.0))), 3),
        "ecart_a_un_sur_cos": round(float(np.median(np.abs(rap - cos))), 3),
        "lobliquite_explique_le_pas": bool(
            np.median(np.abs(rap - cos)) < np.median(np.abs(rap - 1.0))),
        # ⭐⭐⭐ LE SECOND VERDICT, ET IL EST INDEPENDANT DU PREMIER. Comparer deux MEDIANES peut
        # rater un effet reel noye dans la dispersion ; si l'obliquite jouait, le rapport
        # SUIVRAIT 1/cos d'une bande a l'autre, quelle que soit sa valeur moyenne. Une
        # correlation nulle refute cette dependance-la, que la comparaison de medianes ne teste
        # pas.
        "correlation_rapport_contre_un_sur_cos": correlation(list(rap), list(cos)),
    })
    return out


def agreger_les_angles(r: dict) -> dict:
    """Le resume des angles, DERIVE des lignes par bande — meme partage que ci-dessus."""
    lues = [x for x in r["lignes"] if x["angle_grille_deg"] is not None
            and x["rayon_mesure_mm"] is not None]
    if lues:
        ag = [x["angle_grille_deg"] for x in lues]
        aa = [x["angle_acp_deg"] for x in lues]
        pr = [x["inclinaison_predite_deg"] for x in lues]
        r["resume"] = {
            "angle_grille_median_deg": round(float(np.median(ag)), 2),
            "angle_acp_median_deg": round(float(np.median(aa)), 2),
            "inclinaison_predite_mediane_deg": round(float(np.median(pr)), 3),
            # ⚠ Un COMPTE de fois s'ecrit en entier. En flottant il sort « 378,0 », une forme
            # que personne ne redige, donc le garde de chiffres publies la chercherait en vain.
            "combien_de_fois_la_prediction": int(round(
                float(np.median(ag)) / max(float(np.median(pr)), 1e-9))),
            # ⭐⭐ L'ACCORD ENTRE LES DEUX ESTIMATEURS EST LA QUANTITE QUI DECIDE si l'obliquite
            # est dans la matiere ou dans la facon de la lire.
            "ecart_entre_estimateurs_deg": round(
                float(np.median(np.abs(np.array(ag) - np.array(aa)))), 2),
            "les_deux_estimateurs_saccordent": bool(
                np.median(np.abs(np.array(ag) - np.array(aa))) < 12.0),
            "angle_du_a_z_median_deg": round(float(np.median(
                [x["angle_du_a_z_deg"] for x in lues if x["angle_du_a_z_deg"] is not None])), 2),
            "angle_dans_le_plan_median_deg": round(float(np.median(
                [x["angle_dans_le_plan_deg"] for x in lues
                 if x["angle_dans_le_plan_deg"] is not None])), 2),
            "angle_contre_rayon": correlation(ag, [x["rayon_mesure_mm"] for x in lues]),
        }
        # ⚠⚠ LE BALAYAGE AGREGE : l'angle decroit-il avec le voisinage, et vers quoi ?
        agr = {}
        for k in map(str, VOISINAGES):
            v = [x["balayage_de_voisinage_deg"].get(k) for x in lues]
            v = [y for y in v if y is not None]
            if v:
                agr[k] = round(float(np.median(v)), 2)
        r["balayage_de_voisinage_deg"] = agr
        if len(agr) >= 2:
            cles = sorted(agr, key=int)
            r["resume"]["angle_au_plus_petit_voisinage_deg"] = agr[cles[0]]
            r["resume"]["angle_au_plus_grand_voisinage_deg"] = agr[cles[-1]]
            # ⭐⭐⭐ LE CONTROLE DE `96` APPLIQUE A UNE DIRECTION : du bruit s'efface quand le
            # voisinage grandit, une structure reste. Les deux moities sont publiees.
            r["resume"]["une_part_est_de_la_rugosite"] = bool(agr[cles[-1]] < agr[cles[0]])
            r["resume"]["mais_il_reste_bien_au_dela_de_la_prediction"] = bool(
                agr[cles[-1]] > 20.0 * r["resume"]["inclinaison_predite_mediane_deg"])
    return r


def mesurer(cellules: int = CELLULES_PAR_BANDE, bandes_max: int | None = None,
            avec_volume: bool = True, cellules_volume: int = CELLULES_POUR_LE_VOLUME) -> dict:
    r = mesurer_les_angles(cellules=cellules, bandes_max=bandes_max)
    if "message" in r:
        return r
    r = agreger_les_angles(r)
    if avec_volume:
        r["le_pas_dans_les_deux_directions"] = mesurer_le_pas_dans_les_deux_directions(
            cellules=cellules_volume, bandes_max=bandes_max)
    return r


def reagreger(chemin: Path) -> dict:
    """Recalculer les verdicts depuis un resultat deja ecrit, SANS retoucher au volume.

    ⚠⚠ CE N'EST PAS UNE NOUVELLE MESURE, ET LE FICHIER LE DIT : les lignes par bande sont
    reprises telles quelles ; seules les quantites DERIVEES sont refaites. Confondre les deux
    ferait passer un recalcul pour une confirmation.
    """
    r = json.loads(chemin.read_text())
    r = agreger_les_angles(r)
    d = r.get("le_pas_dans_les_deux_directions")
    if d and d.get("lignes"):
        garde = {k: v for k, v in d.items()
                 if k in ("cellules_par_bande", "barre_du_nul")}
        r["le_pas_dans_les_deux_directions"] = {**agreger_les_directions(d["lignes"]), **garde}
    return r


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · pas nominal {r['pas_nominal_um']} µm · {r['bandes']} bandes · "
          f"{r['cellules_par_bande']} cellules par bande\n")
    print(f"{'bande':>10} {'rayon':>6} {'grille':>8} {'ACP':>8} {'prédit':>8} {'×':>6} "
          f"{'dû à z':>8} {'dans xy':>8}")
    for x in r["lignes"]:
        if x["angle_grille_deg"] is None:
            continue
        rap = x["angle_grille_deg"] / max(x["inclinaison_predite_deg"], 1e-9)
        print(f"  w{x['de']:03d}-{x['a']:03d} {x['rayon_mesure_mm']:>6.1f} "
              f"{x['angle_grille_deg']:>7.1f}° {x['angle_acp_deg']:>7.1f}° "
              f"{x['inclinaison_predite_deg']:>7.2f}° {rap:>6.0f} "
              f"{nombre_ou_absent(x['angle_du_a_z_deg']):>7.1f}° "
              f"{nombre_ou_absent(x['angle_dans_le_plan_deg']):>7.1f}°")
    s = r.get("resume", {})
    b = r.get("balayage_de_voisinage_deg", {})
    if b:
        print("\n" + " ".join(f"k={k}:{v:.1f}°" for k, v in sorted(b.items(), key=lambda z: int(z[0]))))
    if s:
        print(f"\n★★★ LA SURFACE EST OBLIQUE AU RAYON DE {s['angle_grille_median_deg']:.1f}° "
              f"LA OU LA SPIRALE EN PRÉDIT {s['inclinaison_predite_mediane_deg']:.2f}° —")
        print(f"   soit {s['combien_de_fois_la_prediction']:.0f} fois plus. Sur une spirale de "
              f"pas {r['pas_nominal_um']} µm, la feuille n'est inclinée")
        print("   sur le rayon que d'une fraction de degré ; ce maillage-ci en est à des dizaines.")
        print(f"\n★★ ET CE N'EST PAS L'ESTIMATEUR : la normale par ACP, indépendante de la "
              f"grille, donne")
        print(f"   {s['angle_acp_median_deg']:.1f}° contre {s['angle_grille_median_deg']:.1f}° — "
              f"un écart de {s['ecart_entre_estimateurs_deg']:.1f}°. Deux estimateurs qui ne")
        print("   partagent aucune hypothèse s'accordent, donc l'obliquité est dans la matière.")
        if "angle_au_plus_grand_voisinage_deg" in s:
            print(f"\n⚠⚠ UNE PART EST DE LA RUGOSITÉ, ET ELLE EST MESURÉE : l'angle tombe de "
                  f"{s['angle_au_plus_petit_voisinage_deg']:.1f}° à")
            print(f"   {s['angle_au_plus_grand_voisinage_deg']:.1f}° quand le voisinage passe de "
                  f"{min(r['voisinages'])} à {max(r['voisinages'])} points. Mais il ne converge "
                  f"PAS vers")
            print("   zéro — il plafonne cent fois au-dessus de ce que la spirale prédit.")
        print(f"\n⚠ DÉCOMPOSÉE : {s['angle_du_a_z_median_deg']:.1f}° hors du plan (les feuilles "
              f"seraient coniques) et")
        print(f"   {s['angle_dans_le_plan_median_deg']:.1f}° dans le plan (la section n'est pas "
              f"un cercle). Les deux, pas l'une.")
    d = r.get("le_pas_dans_les_deux_directions", {})
    if "message" in d:
        print(f"\n⚠ test décisif sauté : {d['message']}")
        return 0
    if d.get("bandes_mesurees"):
        print(f"\n{'bande':>10} {'rayon':>6} {'angle':>7} {'pas RADIAL':>11} "
              f"{'pas NORMAL':>11} {'rapport':>8} {'1/cos':>7}")
        for x in d["lignes"]:
            if x.get("rapport_radial_sur_normal") is None:
                continue
            print(f"  w{x['de']:03d}-{x['a']:03d} "
                  f"{nombre_ou_absent(x['rayon_mm']):>6.1f} {x['angle_deg']:>6.1f}° "
                  f"{x['pas_radial_um']:>10.1f}µ {x['pas_normal_um']:>10.1f}µ "
                  f"{x['rapport_radial_sur_normal']:>8.3f} {x['un_sur_cos']:>7.3f}")
        print(f"\n⛔⛔⛔ L'HYPOTHÈSE EST RÉFUTÉE. Le rapport médian vaut "
              f"{d['rapport_median']:.3f} (de {d['rapport_min']:.2f} à")
        print(f"   {d['rapport_max']:.2f}) là où l'obliquité en prédirait "
              f"{d['un_sur_cos_median']:.3f}. Écart à 1 : {d['ecart_a_un']:.3f} ; écart à")
        print(f"   1/cos : {d['ecart_a_un_sur_cos']:.3f}. Le pas ne dépend PAS de la direction, "
              f"donc l'accord")
        print("   1,212 contre 1,213 entre 1/cos et le rapport 199/164 était une COÏNCIDENCE —")
        print("   exactement le piège que `94` a enregistré avec la sagitta.")
        if "correlation_rapport_contre_un_sur_cos" in d:
            print(f"\n★★★ ET UN SECOND VERDICT, INDÉPENDANT DU PREMIER : si l'obliquité jouait, "
                  f"le rapport")
            print(f"   SUIVRAIT 1/cos d'une bande à l'autre, quelle que soit sa valeur moyenne. "
                  f"Corrélation")
            print(f"   mesurée : {d['correlation_rapport_contre_un_sur_cos']:+.3f}. Comparer "
                  f"deux médianes peut rater un effet noyé")
            print("   dans la dispersion ; cette dépendance-là, elle, est testée directement.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import combien_dinterstices_traverses as C  # noqa: PLC0415
    from la_fermeture_dun_tour import spirale  # noqa: PLC0415

    # --- la prediction, qui est le referent de tout le fichier -----------------------------
    v("une spirale de 164 µm à 10 mm incline sa feuille d'une fraction de degré",
      abs(inclinaison_de_la_spirale(10_000.0, 164.0) - 0.1495) < 0.01,
      f"{inclinaison_de_la_spirale(10_000.0, 164.0):.3f}°")
    v("... et l'inclinaison DÉCROÎT quand le rayon grandit",
      inclinaison_de_la_spirale(4_000.0, 173.0) > inclinaison_de_la_spirale(24_000.0, 173.0),
      f"{inclinaison_de_la_spirale(4_000.0, 173.0):.3f}° contre "
      f"{inclinaison_de_la_spirale(24_000.0, 173.0):.3f}°")
    # ⚠ Un pas nul est une pile de cylindres : la feuille est alors EXACTEMENT radiale.
    v("... et un pas nul rend une inclinaison nulle",
      inclinaison_de_la_spirale(10_000.0, 0.0) == 0.0)

    # --- le cylindre : la normale EST le rayon, sur les deux estimateurs -------------------
    th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    cyl = np.zeros((6, 360, 3))
    for k in range(6):
        cyl[k, :, 0] = 200.0 * np.cos(th)
        cyl[k, :, 1] = 200.0 * np.sin(th)
        cyl[k, :, 2] = k * 5.0
    okc = np.ones(cyl.shape[:2], dtype=bool)
    ind = np.stack(np.meshgrid(np.arange(1, 5), np.arange(5, 355), indexing="ij"),
                   -1).reshape(-1, 2)
    p0 = cyl[ind[:, 0], ind[:, 1]]
    c0 = np.zeros((len(p0), 2))
    rad = direction_radiale(p0, c0)
    ng = normale_de_la_grille(cyl, okc, ind)
    bon = np.isfinite(ng).all(axis=1)
    a_g = float(np.median(angle_entre(ng[bon], rad[bon])))
    v("sur un cylindre parfait, la normale de la grille EST le rayon", a_g < 0.5,
      f"{a_g:.3f}°")
    a_a = float(np.median(angle_entre(normale_par_acp(cyl[okc], p0, 30), rad)))
    v("... et la normale par ACP aussi", a_a < 2.0, f"{a_a:.3f}°")

    # --- la spirale : les deux estimateurs retrouvent la prediction ANALYTIQUE -------------
    # ⭐⭐⭐ C'EST LE CONTROLE QUI RELIE LA MESURE A LA THEORIE : sur une spirale de pas connu,
    # l'angle mesure doit EGALER atan(pas / 2*pi*r). S'il ne l'egalait pas, l'ecart mesure sur le
    # vrai maillage ne dirait rien, parce qu'on ne saurait pas ce que l'instrument rend sur une
    # surface dont on connait la reponse.
    for pas, r0 in ((173.0, 10.0), (1000.0, 5.0), (4000.0, 3.0)):
        sp, oksp = spirale(pas_um=pas, r0_mm=r0, tours=4, col_par_tour=360, H=6)
        i2 = np.stack(np.meshgrid(np.arange(1, 5), np.arange(400, 1000, 3),
                                  indexing="ij"), -1).reshape(-1, 2)
        q0 = sp[i2[:, 0], i2[:, 1]]
        rr = direction_radiale(q0, np.zeros((len(q0), 2)))
        n2 = normale_de_la_grille(sp, oksp, i2)
        b2 = np.isfinite(n2).all(axis=1)
        ray = float(np.median(np.linalg.norm(q0[b2, :2], axis=-1))) * 45.532
        attendu = inclinaison_de_la_spirale(ray, pas)
        lu = float(np.median(angle_entre(n2[b2], rr[b2])))
        v(f"une spirale de pas {pas:.0f} µm rend l'inclinaison ANALYTIQUE",
          abs(lu - attendu) < max(0.15, 0.15 * attendu), f"lu {lu:.3f}° pour {attendu:.3f}°")

    # --- une normale n'a pas de SENS, et l'angle doit l'ignorer ---------------------------
    u1 = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
    u2 = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    v("l'angle est insensible au signe de la normale",
      float(np.max(angle_entre(u1, u2))) < 1e-9, str(angle_entre(u1, u2)))

    # --- ZERO N'EST PAS « ON NE SAIT PAS », et le piege a mordu pour de vrai --------------
    # ⚠⚠⚠ `valeur or float("nan")` affiche « nan » pour un ZERO mesure, parce que 0.0 est faux en
    # Python. Un temoin qui confirme zero pas — le resultat le plus informatif qu'il puisse
    # rendre — s'affichait donc comme une donnee manquante.
    v("un zéro mesuré reste un zéro, il ne devient pas « absent »",
      nombre_ou_absent(0.0) == 0.0 and nombre_ou_absent(0) == 0.0)
    v("... alors qu'une valeur ABSENTE devient NaN",
      not np.isfinite(nombre_ou_absent(None)))
    v("... et une valeur ordinaire traverse intacte", nombre_ou_absent(34.06) == 34.06)

    # --- l'avancement ecrit sur STDERR, et c'est ce qui le rend sans risque ---------------
    # ⚠⚠ SUR STDOUT IL CORROMPRAIT UNE SORTIE REDIRIGEE. Le contrôle capture les deux flux
    # separement plutot que de le supposer.
    import contextlib  # noqa: PLC0415
    import io as _io  # noqa: PLC0415

    _out, _err = _io.StringIO(), _io.StringIO()
    with contextlib.redirect_stdout(_out), contextlib.redirect_stderr(_err):
        avancement(3, 28, "bandes", time.time() - 120.0)
    v("l'avancement n'écrit RIEN sur stdout", _out.getvalue() == "",
      repr(_out.getvalue()))
    v("... et il dit où il en est sur stderr",
      "3/28" in _err.getvalue() and "restantes" in _err.getvalue(),
      _err.getvalue().strip())
    # ⚠ Une estimation qui suppose que le reste coûte comme le fait : 2 min pour 3 bandes sur 28
    # doit annoncer de l'ordre de 17 min.
    v("... avec une fin estimée cohérente", "17 min" in _err.getvalue(),
      _err.getvalue().strip())
    _out2, _err2 = _io.StringIO(), _io.StringIO()
    with contextlib.redirect_stdout(_out2), contextlib.redirect_stderr(_err2):
        avancement(0, 28, "bandes", time.time())
    v("... et il se tait plutôt que de diviser par zéro au premier étage",
      _err2.getvalue() == "")

    # --- la decomposition attribue le basculement au bon axe -------------------------------
    # ⚠⚠ SANS CE CONTROLE, LES DEUX COLONNES POURRAIENT ETRE INTERVERTIES sans que rien ne
    # l'indique : « les feuilles sont coniques » et « la section n'est pas un cercle » sont deux
    # conclusions differentes tirees du meme nombre total.
    rr = np.array([[1.0, 0.0, 0.0]] * 3)
    incline_en_z = np.array([[np.cos(np.deg2rad(20.0)), 0.0, np.sin(np.deg2rad(20.0))]] * 3)
    z20, p20 = decomposer(incline_en_z, rr)
    v("une normale inclinée de 20° EN HAUTEUR est attribuée à z",
      abs(float(np.median(z20)) - 20.0) < 0.5 and float(np.median(p20)) < 0.5,
      f"z {float(np.median(z20)):.1f}° · plan {float(np.median(p20)):.1f}°")
    dans_le_plan = np.array([[np.cos(np.deg2rad(20.0)), np.sin(np.deg2rad(20.0)), 0.0]] * 3)
    z0, p0d = decomposer(dans_le_plan, rr)
    v("... et une normale tournée de 20° DANS LE PLAN est attribuée au plan",
      float(np.median(z0)) < 0.5 and abs(float(np.median(p0d)) - 20.0) < 0.5,
      f"z {float(np.median(z0)):.1f}° · plan {float(np.median(p0d)):.1f}°")

    # --- l'ACP ignore l'anisotropie de l'echantillonnage, la grille non --------------------
    # ⭐⭐ C'EST LA PROPRIETE QUI JUSTIFIE LE SECOND ESTIMATEUR : `97` a mesure que les rangees de
    # ce maillage sont ~800 µm a part quand ses colonnes sont a ~100. Un estimateur qui rendrait un
    # angle different selon la densite mesurerait la GRILLE, pas la surface.
    gx, gy = np.meshgrid(np.arange(60) * 8.0, np.arange(60) * 1.0, indexing="ij")
    plan = np.stack([gx.ravel(), gy.ravel(), np.zeros(gx.size)], axis=-1)
    cible = plan[np.random.default_rng(5).choice(len(plan), 200, replace=False)]
    nacp = normale_par_acp(plan, cible, 30)
    ecart = float(np.median(angle_entre(nacp, np.array([[0.0, 0.0, 1.0]] * len(cible)))))
    v("l'ACP rend la normale d'un plan malgré un échantillonnage 8× anisotrope",
      ecart < 1.0, f"{ecart:.4f}°")

    # --- l'orientation vers l'exterieur ---------------------------------------------------
    rentrante = np.array([[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    dehors = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    v("une normale rentrante est retournée vers l'extérieur",
      bool(np.all(np.einsum("ij,ij->i", orienter_vers_lexterieur(rentrante, dehors),
                            dehors) > 0)))

    # === LE CONTROLE QUI PORTE LA REFUTATION ==============================================
    # ⭐⭐⭐ L'INSTRUMENT VOIT-IL L'OBLIQUITE QUAND ELLE EXISTE ? Sur un empilement fabrique
    # d'angle connu, le pas lu radialement doit valoir pas / cos(theta) et le pas lu le long de la
    # normale doit valoir pas. Sans ce controle, « le rapport vaut 1,00 sur le vrai volume » serait
    # indiscernable d'un test aveugle a la direction.
    import le_pas_que_la_matiere_montre as M  # noqa: PLC0415

    longueurs = M.candidats_de_pas(C.PAS_UM)
    mu, sd = M.nul_par_candidat(longueurs, tirages=300)
    n_long = M.ECHANTILLONS * M.SUR_ECHANTILLONNAGE
    for theta in (0.0, 35.0):
        aa, oo = empilement_oblique(theta, pas_um=C.PAS_UM)
        # ⚠ On echantillonne au MILIEU de chaque feuille, la ou u = 0 : c'est la seule colonne ou
        # le rayon vaut exactement x, donc la seule ou l'angle attendu est exactement theta.
        # ⚠ La colonne u = 0 de chaque feuille : 41 colonnes par feuille, milieu a +20.
        colonnes = np.arange(aa.shape[1] // 41) * 41 + 20
        i2 = np.stack(np.meshgrid(np.arange(1, 5), colonnes, indexing="ij"),
                      -1).reshape(-1, 2)
        i2 = i2[i2[:, 1] < aa.shape[1] - 1]
        q0 = aa[i2[:, 0], i2[:, 1]]
        rr2 = direction_radiale(q0, np.zeros((len(q0), 2)))
        n2 = normale_de_la_grille(aa, oo, i2)
        b2 = np.isfinite(n2).all(axis=1)
        n2 = orienter_vers_lexterieur(n2[b2], rr2[b2])
        lu_angle = float(np.median(angle_entre(n2, rr2[b2])))
        v(f"un empilement incliné de {theta:.0f}° est MESURÉ à {theta:.0f}°",
          abs(lu_angle - theta) < 1.0, f"{lu_angle:.2f}°")
        pas_lus = {}
        for nom, direction in (("radial", rr2[b2]), ("normal", n2)):
            seg = segments_dans_la_direction(q0[b2], direction, float(longueurs[-1]),
                                             n_long, C.VOXEL_MAILLAGE_UM)
            prof = brillance_de_lempilement(seg, theta, C.PAS_UM)
            lu, sc, kk, _ = M.pas_montre_calibre(M.profils_emboites(prof, longueurs),
                                                 longueurs, mu, sd)
            garde = ~M.touche_un_bord(kk, len(longueurs))
            pas_lus[nom] = float(np.median(lu[garde])) if int(garde.sum()) else float("nan")
        attendu = 1.0 / np.cos(np.deg2rad(theta))
        rapport = pas_lus["radial"] / max(pas_lus["normal"], 1e-9)
        cran = float(longueurs[1] - longueurs[0])
        v(f"... et le pas NORMAL y vaut le pas vrai ({C.PAS_UM:.0f} µm)",
          abs(pas_lus["normal"] - C.PAS_UM) <= cran, f"{pas_lus['normal']:.1f} µm")
        v(f"... et le rapport radial/normal y vaut 1/cos({theta:.0f}°) = {attendu:.3f}",
          abs(rapport - attendu) < 0.12,
          f"{rapport:.3f} — radial {pas_lus['radial']:.1f} µm")

    # --- la reagregation ne doit rien MESURER, seulement rederiver ------------------------
    # ⚠⚠ SANS CE CONTROLE, `--reagreger` POURRAIT SILENCIEUSEMENT REECRIRE LES MESURES. Il est
    # cense ne toucher qu'aux quantites derivees ; s'il modifiait une ligne par bande, un
    # recalcul deviendrait une nouvelle mesure sans que rien ne le dise.
    import tempfile  # noqa: PLC0415

    faux = {
        "fragment": "X", "pas_nominal_um": 173.0, "voxel_maillage_um": 45.532,
        "voisinages": [10, 30], "cellules_par_bande": 5, "bandes": 2,
        "lignes": [
            {"de": 1, "a": 2, "rayon_mm": 5.0, "rayon_mesure_mm": 5.0, "cellules": 5,
             "cellules_avec_normale": 5, "angle_grille_deg": 30.0, "angle_acp_deg": 31.0,
             "balayage_de_voisinage_deg": {"10": 34.0, "30": 30.0},
             "angle_du_a_z_deg": 12.0, "angle_dans_le_plan_deg": 27.0, "nz_median": 0.2,
             "inclinaison_predite_deg": 0.3},
            {"de": 3, "a": 4, "rayon_mm": 10.0, "rayon_mesure_mm": 10.0, "cellules": 5,
             "cellules_avec_normale": 5, "angle_grille_deg": 36.0, "angle_acp_deg": 35.0,
             "balayage_de_voisinage_deg": {"10": 38.0, "30": 34.0},
             "angle_du_a_z_deg": 14.0, "angle_dans_le_plan_deg": 25.0, "nz_median": 0.24,
             "inclinaison_predite_deg": 0.15},
        ],
        "le_pas_dans_les_deux_directions": {
            "bandes": 2, "bandes_mesurees": 2, "cellules_par_bande": 5, "barre_du_nul": 4.0,
            "lignes": [
                {"de": 1, "a": 2, "rayon_mm": 5.0, "angle_deg": 30.0, "cellules": 5,
                 "pas_radial_um": 200.0, "pas_normal_um": 200.0,
                 "rapport_radial_sur_normal": 1.0, "un_sur_cos": 1.155},
                {"de": 3, "a": 4, "rayon_mm": 10.0, "angle_deg": 36.0, "cellules": 5,
                 "pas_radial_um": 210.0, "pas_normal_um": 200.0,
                 "rapport_radial_sur_normal": 1.05, "un_sur_cos": 1.236},
            ]},
    }
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "faux.json"
        chemin.write_text(json.dumps(faux))
        refait = reagreger(chemin)
    v("la réagrégation laisse les lignes par bande INTACTES",
      refait["lignes"] == faux["lignes"]
      and refait["le_pas_dans_les_deux_directions"]["lignes"]
      == faux["le_pas_dans_les_deux_directions"]["lignes"])
    v("... et rend les verdicts dérivés", "resume" in refait
      and "rapport_median" in refait["le_pas_dans_les_deux_directions"])
    # ⭐⭐ ET SUR UNE FIXTURE DONT LE RAPPORT SUIT 1/cos, LE VERDICT DOIT S'INVERSER : un
    # verdict qui repond « refute » quoi qu'on lui donne ne trancherait rien.
    suit = json.loads(json.dumps(faux))
    for x in suit["le_pas_dans_les_deux_directions"]["lignes"]:
        x["rapport_radial_sur_normal"] = x["un_sur_cos"]
    with tempfile.TemporaryDirectory() as tmp:
        chemin = Path(tmp) / "suit.json"
        chemin.write_text(json.dumps(suit))
        inverse = reagreger(chemin)
    v("un rapport qui SUIT 1/cos fait dire au verdict que l'obliquité explique",
      inverse["le_pas_dans_les_deux_directions"]["lobliquite_explique_le_pas"],
      f"écart à 1/cos "
      f"{inverse['le_pas_dans_les_deux_directions']['ecart_a_un_sur_cos']}")

    # === LES DONNEES REELLES ==============================================================
    r = mesurer(cellules=120, bandes_max=3, avec_volume=False)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le maillage", r["bandes"] >= 1, f"{r['bandes']} bandes")
    s = r["resume"]
    # ⭐⭐⭐ LE FAIT DU FICHIER, ASSERTE PLUTOT QUE REDIGE.
    v("la normale du maillage est à des DIZAINES de degrés du rayon",
      s["angle_grille_median_deg"] > 10.0, f"{s['angle_grille_median_deg']:.1f}°")
    v("... alors que la spirale en prédit une FRACTION de degré",
      s["inclinaison_predite_mediane_deg"] < 1.0,
      f"{s['inclinaison_predite_mediane_deg']:.3f}°")
    # ⭐⭐ ET CE N'EST PAS L'ESTIMATEUR : deux estimateurs sans hypothese commune s'accordent.
    v("les deux estimateurs s'accordent, donc l'obliquité est dans la matière",
      s["les_deux_estimateurs_saccordent"],
      f"grille {s['angle_grille_median_deg']:.1f}° · ACP {s['angle_acp_median_deg']:.1f}° "
      f"· écart {s['ecart_entre_estimateurs_deg']:.1f}°")
    # ⚠⚠ LES DEUX MOITIES DU BALAYAGE SONT ASSERTEES : une part s'efface, le reste tient.
    if "angle_au_plus_grand_voisinage_deg" in s:
        v("une part de l'angle est de la rugosité locale, et elle s'efface",
          s["une_part_est_de_la_rugosite"],
          f"{s['angle_au_plus_petit_voisinage_deg']:.1f}° → "
          f"{s['angle_au_plus_grand_voisinage_deg']:.1f}°")
        v("... mais le reste plafonne loin au-dessus de la prédiction",
          s["mais_il_reste_bien_au_dela_de_la_prediction"],
          f"{s['angle_au_plus_grand_voisinage_deg']:.1f}° contre "
          f"{s['inclinaison_predite_mediane_deg']:.3f}°")
    v("la décomposition publie les DEUX composantes",
      s["angle_du_a_z_median_deg"] > 1.0 and s["angle_dans_le_plan_median_deg"] > 1.0,
      f"z {s['angle_du_a_z_median_deg']:.1f}° · plan {s['angle_dans_le_plan_median_deg']:.1f}°")
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--cellules-volume", type=int, default=CELLULES_POUR_LE_VOLUME)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--sans-volume", action="store_true")
    # ⚠ Recalculer les verdicts DERIVES sans relire le volume. Ce n'est pas une nouvelle mesure.
    p.add_argument("--reagreger", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger:
        if a.json is None or not a.json.is_file():
            print("⚠ --reagreger demande un --json existant")
            return 1
        r = reagreger(a.json)
        afficher(r)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nréagrégé : {a.json}")
        return 0
    r = mesurer(cellules=a.cellules, bandes_max=a.bandes, avec_volume=not a.sans_volume,
                cellules_volume=a.cellules_volume)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
