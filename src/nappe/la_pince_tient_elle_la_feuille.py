#!/usr/bin/env python3
"""Une PINCE tient-elle une feuille autour d'un tour, la ou une sonde la lache ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET POURQUOI C'EST LA QUESTION DU GRAAL. Le graal demande ce qui
remplace l'humain qui corrige le transfert de spire a spire. `138` a montre que deux sondes LIBRES
separees d'un seul voxel derivent de **2,743 feuilles**, et que l'ecart entre elles n'y change rien :
ce n'est pas la matiere qui les separe, c'est le marcheur qui amplifie. Il faut donc CONTRAINDRE le
marcheur, pas mieux le mesurer. `141` retire une exigence a cette contrainte : il n'y a **pas**
d'endroits ou le chemin part de travers qu'une alarme pourrait signaler, donc la piece manquante
n'a rien a DETECTER — elle doit seulement ne jamais lacher.

⭐⭐⭐⭐ L'IDEE EST CELLE DE L'AUTEUR, ET C'EST UN OBJET MECANIQUE : deux rouleaux compresseurs qui
tiennent UNE feuille. Transposee dans le volume, une MACHOIRE est un appui qui repose sur un
INTERSTICE, et une pince en a deux — une de chaque cote de la meme feuille. La feuille n'est plus
un point qu'on suit, c'est une epaisseur qu'on tient.

⭐⭐⭐ ET UNE MACHOIRE N'EST PAS UN POINT, C'EST UN SEGMENT. C'est ce qui la rend capable de donner
une orientation sans tenseur de structure : ses appuis lateraux tombent sur la surface de
l'interstice, donc la droite qui les joint EST une tangente de cette surface. Une machoire reduite
a un point ne peut pas le faire — deux points cherches le long d'une meme normale supposee sont
alignes sur cette normale par construction, donc ils ne la corrigent jamais. ⚠ Mesure faite avant
d'ecrire ce fichier : un gradient central bon marche rend **25°** d'erreur de normale a bruit 8,
donc il ne pouvait servir de rien ; et le tenseur de structure que `marcher` emploie coute un cube
de 41³ lectures par pas.

⚠⚠ CE QU'UNE MACHOIRE MESURE, ET CE QU'ELLE NE MESURE PAS. Une machoire de demi-largeur `w` suit
le plan MOYEN de la feuille sur `w`, jamais sa normale ponctuelle. Sur une feuille froissee les deux
different reellement, et les confondre m'a d'abord fait lire un echec la ou il n'y en avait pas. La
largeur est donc BALAYEE et jamais posee, comme `140` balaye l'ecrasement.

⭐⭐⭐ LES TROIS BRAS, ET CE QUE CHAQUE PASSAGE ISOLE. Un seul ingredient change d'un bras au
suivant, ce qui est la seule facon de dire lequel paie :
  1. **une machoire** — un appui sur l'interstice EXTERIEUR seulement. Elle doit alors SUPPOSER ou
     est la feuille : une demi-epaisseur sous son appui. C'est la sonde libre de `138`, rendue
     aussi capable qu'on peut la rendre.
  2. **deux machoires libres** — les deux interstices, donc l'epaisseur est MESUREE et non supposee,
     et le centre est leur milieu. Rien n'est refuse.
  3. **la pince** — le bras 2, plus le refus : un appui n'a pas le droit de CHANGER D'INTERSTICE en
     un pas. Le passage 1 → 2 dit ce que la seconde machoire achete, le passage 2 → 3 ce que la
     contrainte achete.

⚠⚠ LE REFUS N'EST PAS UN SEUIL CHOISI. Les interstices sont espaces d'un pas, donc l'appariement
au plus proche bascule exactement a **un demi-pas** : « c'est le meme interstice » et « le
deplacement est inferieur a un demi-pas » sont le MEME enonce, pas une tolerance reglee sur ce qui
passe. Et un pas refuse est HALVE puis retente, jusqu'a ce que l'avance tombe sous le voxel — en
dessous, un deplacement n'est plus exprimable par le lecteur, donc la pince s'arrete et le dit.

⚠⚠ LE VERDICT EST UNE PAIRE, ET C'EST CE QUI L'EMPECHE D'ETRE TAUTOLOGIQUE. Une pince qui refuse
tout ne derive jamais — et ne va nulle part. On mesure donc **jusqu'ou** chaque bras va ET **sur
quelle feuille** il finit. Un bras qui s'arrete au troisieme pas n'a rien demontre.

⚠ LA VERITE EST CONNUE, ET C'EST POURQUOI LA MESURE EST SUR FIXTURE. Sur une spirale d'Archimede,
suivre la feuille de phase `k` sur un tour entier ramene a la meme phase et un pas plus loin en
rayon : « est-on encore sur la meme feuille apres un tour » est donc une question a reponse EXACTE,
ce que le vrai rouleau ne peut pas offrir.

⚠ LA MARCHE EST TENUE DANS LE PLAN. La fixture est invariante selon `z`, donc une derive axiale y
serait une marche au hasard qui n'apprendrait rien sur le tour, et elle frapperait les trois bras
pareil. La contrainte est donnee aux trois, et elle est dite ici plutot que cachee.

Usage :
    uv run python src/nappe/la_pince_tient_elle_la_feuille.py --verifier
    uv run python src/nappe/la_pince_tient_elle_la_feuille.py \\
        --json docs/mesures/la_pince_tient_elle_la_feuille.json
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

Z = np.array([1.0, 0.0, 0.0])
RAYON_MM = 10.0
CENTRE_YX_VX = (16000.0, 16000.0)
FORME = (4000, 32000, 32000)
AMPLITUDE_UM = 100.0
LONGUEUR_DONDE_UM = 393.6
# ⚠ Balayes, jamais poses — c'est la pente qu'on regarde, pas un reglage qui tombe juste.
BRUITS = (0.0, 4.0, 8.0, 16.0)
# ⚠ En fractions du pas : une largeur en micrometres serait un nombre pose, une fraction du pas
# est une largeur RELATIVE a la matiere, et c'est elle qu'on balaie.
LARGEURS_EN_PAS = (0.125, 0.25, 0.5)
LARGEUR_DE_REFERENCE = 0.25
# ⚠ L'avance est une fraction de la LONGUEUR D'ONDE du froissement, pas du pas : ce que le suiveur
# doit echantillonner assez fin est l'ondulation qu'il suit. Mesure faite avant de fixer ce
# nombre : a une avance d'un pas (173 µm pour une longueur d'onde de 393,6) le suiveur
# sous-echantillonne son ondulation et part en vrille.
AVANCE_EN_LONGUEUR_DONDE = 0.25
DEPARTS = 12
APPUIS = 3
# ⚠ Un tour ENTIER : c'est le transfert de spire a spire, et rien de plus court ne le pose.
TOURS = 1.0
BRAS = ("une machoire", "deux machoires libres", "la pince")


def linterstice(vol, p_vx, direction, attendu_um: float, fenetre_um: float,
                voxel_um: float) -> float | None:
    """La distance du premier interstice le long de `direction`, cherche LA OU ON L'ATTEND.

    ⭐⭐ LA FENETRE EST CENTREE SUR L'ATTENTE ET LARGE D'UNE EPAISSEUR. Les interstices sont
    espaces d'une epaisseur, donc un intervalle d'une epaisseur autour de l'endroit attendu en
    contient exactement un, quel que soit le deplacement que le froissement lui a fait subir. Une
    fenetre qui partirait de zero manquerait un interstice pousse plus loin que le pas nominal —
    mesure : a l'amplitude que `140` retient, les appuis lateraux d'une machoire large sortent de
    la fenetre nominale et la pose echoue au depart.

    ⚠⚠ UN MINIMUM AU BORD DE LA FENETRE N'EST PAS UN MINIMUM ENCADRE, DONC CE N'EST PAS UN
    INTERSTICE. L'accepter est le defaut qui a fait s'effondrer ma premiere version : un centre qui
    derive SUR un interstice y trouve le plus petit echantillon au premier pas de la fenetre,
    l'epaisseur tombe a quelques micrometres, la fenetre suivante est batie dessus, et la pince se
    referme sur elle-meme. Refuser est honnete — c'est la pince qui dit qu'elle ne tient plus rien.

    ⚠ Le raffinement est parabolique sur les trois echantillons autour du minimum : le lecteur
    echantillonne au voxel, et sans lui la position d'un appui serait quantifiee a un voxel, soit
    un soixante-dixieme de pas de bruit ajoute a chaque pas de la marche.
    """
    bas = max(float(attendu_um) - 0.5 * float(fenetre_um), voxel_um)
    haut = float(attendu_um) + 0.5 * float(fenetre_um)
    t = np.arange(bas, haut + voxel_um, voxel_um)
    if t.size < 3:
        return None
    pts = np.asarray(p_vx, dtype=np.float64)[None, :] + \
        np.asarray(direction, dtype=np.float64)[None, :] * (t / voxel_um)[:, None]
    if not np.all(vol.dans_le_volume(pts)):
        return None
    v = np.asarray(vol.lire(pts), dtype=np.float64)
    i = int(np.argmin(v))
    if not (0 < i < v.size - 1):
        return None
    a, b, c = float(v[i - 1]), float(v[i]), float(v[i + 1])
    den = a - 2.0 * b + c
    if abs(den) <= 1e-12:
        return float(t[i])
    return float(t[i] + 0.5 * (a - c) / den * voxel_um)


def une_machoire(vol, centre_vx, normale, sens: float, largeur_um: float, epaisseur_um: float,
                 voxel_um: float, appuis: int = APPUIS) -> dict | None:
    """Un appui LARGE sur l'interstice de ce cote — sa position et sa tangente.

    ⭐⭐ C'est ici que la pince gagne son orientation sans rien acheter. Les appuis lateraux
    tombent sur la SURFACE de l'interstice, donc la direction de plus grande variance du nuage
    qu'ils forment est une tangente de cette surface, et la normale s'en deduit. Une machoire
    reduite a un point n'a pas de nuage, donc pas de tangente, donc pas de normale.

    ⚠ Trois appuis est le plus petit nombre qui laisse une redondance a l'ajustement : deux
    definissent une droite exactement, donc ne peuvent jamais la contredire.
    """
    # ⚠⚠ DEUX APPUIS AU MOINS, SINON CE N'EST PAS UNE MACHOIRE. Un seul appui ne forme aucun nuage,
    # donc il ne porte aucune direction : la machoire ne pourrait plus rendre d'orientation, ce qui
    # est precisement ce pour quoi elle a une largeur. Refuser vaut mieux que rendre la direction
    # qu'une decomposition d'une matrice nulle laisse tomber.
    if int(appuis) < 2:
        return None
    n = np.asarray(normale, dtype=np.float64)
    n = n / max(float(np.linalg.norm(n)), 1e-12)
    tan = np.cross(Z, n)
    norme = float(np.linalg.norm(tan))
    if norme < 1e-9:
        return None
    tan = tan / norme
    pts, ecarts = [], []
    for u in np.linspace(-float(largeur_um), float(largeur_um), int(appuis)):
        q = np.asarray(centre_vx, dtype=np.float64) + tan * (u / voxel_um)
        d = linterstice(vol, q, sens * n, 0.5 * float(epaisseur_um), float(epaisseur_um),
                        voxel_um)
        if d is None:
            return None
        pts.append(q + sens * n * (d / voxel_um))
        ecarts.append(d)
    P = np.asarray(pts, dtype=np.float64)
    milieu = P.mean(axis=0)
    Q = P - milieu
    # ⚠ La tangente est la direction de plus grande variance du nuage, pas la droite des moindres
    # carres sur un axe choisi : un ajustement « y en fonction de x » depend de l'axe qu'on a
    # nomme, et la machoire n'a aucune raison d'etre alignee sur l'un des trois.
    tangente = np.linalg.svd(Q, full_matrices=False)[2][0]
    nn = np.cross(tangente, Z)
    norme = float(np.linalg.norm(nn))
    if norme < 1e-9:
        return None
    nn = nn / norme
    if float(nn @ n) < 0.0:
        nn = -nn
    return {"milieu_vx": milieu, "normale": nn, "ecart_um": float(np.median(ecarts)),
            "ecarts_um": [float(x) for x in ecarts]}


def poser(vol, centre_vx, normale, largeur_um: float, epaisseur_um: float, voxel_um: float,
          deux: bool, appuis: int = APPUIS) -> dict | None:
    """L'etat d'un bras : une machoire, ou deux et l'epaisseur qu'elles MESURENT.

    ⚠⚠ C'est la seule difference de fond entre le premier bras et le second. Avec une machoire, ou
    est la feuille se SUPPOSE — une demi-epaisseur sous l'appui, c'est-a-dire un demi-pas, la valeur
    nominale. Avec deux, elle se MESURE, et le centre est le milieu de ce qu'on tient.
    """
    haut = une_machoire(vol, centre_vx, normale, +1.0, largeur_um, epaisseur_um, voxel_um,
                        appuis)
    if haut is None:
        return None
    if not deux:
        n = haut["normale"]
        return {"centre_vx": haut["milieu_vx"] - n * (0.5 * epaisseur_um / voxel_um),
                "normale": n, "haut": haut, "bas": None,
                "epaisseur_um": None, "suppose": True}
    bas = une_machoire(vol, centre_vx, normale, -1.0, largeur_um, epaisseur_um, voxel_um,
                       appuis)
    if bas is None:
        return None
    m = haut["normale"] + bas["normale"]
    norme = float(np.linalg.norm(m))
    n = m / norme if norme > 1e-9 else haut["normale"]
    return {"centre_vx": 0.5 * (haut["milieu_vx"] + bas["milieu_vx"]), "normale": n,
            "haut": haut, "bas": bas, "suppose": False,
            "epaisseur_um": float(np.linalg.norm(
                haut["milieu_vx"] - bas["milieu_vx"]) * voxel_um)}


def _tangente_du_tour(n) -> np.ndarray:
    t = np.cross(Z, np.asarray(n, dtype=np.float64))
    return t / max(float(np.linalg.norm(t)), 1e-12)


def suivre(vol, depart_vx, normale0, largeur_um: float, epaisseur_nominale_um: float, voxel_um: float,
           deux: bool, contrainte: bool, avance_um: float, axe_yx, tours: float = TOURS,
           pas_max: int = 4000) -> dict:
    """Suivre une feuille autour de l'axe, et dire sur laquelle on finit.

    ⚠⚠ LE REFUS HALVE L'AVANCE PLUTOT QUE D'ABANDONNER, et il s'arrete quand l'avance tombe sous le
    VOXEL : en dessous, le lecteur ne peut plus exprimer le deplacement, donc insister serait
    tourner en rond en pretendant avancer. C'est une borne du lecteur, pas un reglage.

    ⚠ Le tour se compte sur l'angle CUMULE et signe, jamais sur l'angle absolu : un suiveur qui
    ferait un aller-retour reviendrait a son angle de depart en ayant parcouru deux fois le chemin,
    et un compteur d'angle absolu lui donnerait raison.
    """
    etat = poser(vol, depart_vx, normale0, largeur_um, epaisseur_nominale_um, voxel_um, deux)
    if etat is None:
        return {"decidable": False, "raison": "la pince ne se pose pas au depart"}
    # ⭐⭐⭐ LA FENETRE DE RECHERCHE VIENT DE L'EPAISSEUR QU'ON TIENT, et c'est la seconde chose que
    # la seconde machoire achete. Le long d'une normale, le prochain interstice est a une demi
    # epaisseur et le suivant a une epaisseur et demie : une fenetre d'UNE epaisseur en contient
    # donc exactement un. Sur une feuille froissee l'espacement local s'ecarte fortement du pas
    # nominal, et une fenetre nominale attrape alors le mauvais minimum — mesure avant d'ecrire
    # ceci : a l'amplitude que `140` retient, le suiveur a fenetre nominale derive de plus de
    # QUARANTE feuilles sur un quart de tour. Une seule machoire n'a rien pour la regler : elle ne
    # mesure aucune epaisseur, donc elle garde le nominal, et c'est exactement son infirmite.
    axe = np.array([float(depart_vx[0]), float(axe_yx[0]), float(axe_yx[1])])

    def angle(p):
        return float(np.arctan2(p[1] - axe[1], p[2] - axe[2]))

    def rayon_um(p):
        return float(np.hypot(p[1] - axe[1], p[2] - axe[2])) * voxel_um

    phase0 = float(vol.phase(np.asarray(etat["centre_vx"]).reshape(1, 3))[0])
    tan = _tangente_du_tour(etat["normale"])
    th, cumul, chemin = angle(etat["centre_vx"]), 0.0, 0.0
    r0 = rayon_um(etat["centre_vx"])
    pas, refus, halts, ecarts, phases = 0, 0, 0, [], [phase0]
    fin = "tour bouclé"
    while abs(cumul) < 2.0 * np.pi * float(tours) and pas < int(pas_max):
        a, pris = float(avance_um), None
        fenetre = (float(etat["epaisseur_um"]) if etat.get("epaisseur_um") is not None
                   else float(epaisseur_nominale_um))
        while a >= voxel_um:
            cible = np.asarray(etat["centre_vx"]) + tan * (a / voxel_um)
            neuf = poser(vol, cible, etat["normale"], largeur_um, fenetre, voxel_um, deux)
            if neuf is None:
                a *= 0.5
                halts += 1
                continue
            if contrainte:
                n = np.asarray(etat["normale"])
                saut = max(
                    abs(float((np.asarray(neuf[c]["milieu_vx"])
                               - np.asarray(etat[c]["milieu_vx"])) @ n)) * voxel_um
                    for c in ("haut", "bas") if etat[c] is not None and neuf[c] is not None)
                ecarts.append(saut)
                # ⚠ « le meme interstice » et « moins d'un demi-pas » sont le meme enonce : les
                # interstices sont espaces d'un pas, donc l'appariement bascule exactement la.
                if saut >= 0.5 * fenetre:
                    a *= 0.5
                    refus += 1
                    continue
            pris = neuf
            break
        if pris is None:
            fin = "la pince ne peut plus avancer"
            break
        chemin += a
        th_neuf = angle(pris["centre_vx"])
        d = th_neuf - th
        d = (d + np.pi) % (2.0 * np.pi) - np.pi
        cumul += d
        th = th_neuf
        nouvelle_tan = _tangente_du_tour(pris["normale"])
        if float(nouvelle_tan @ tan) < 0.0:
            nouvelle_tan = -nouvelle_tan
        tan, etat = nouvelle_tan, pris
        phases.append(float(vol.phase(np.asarray(etat["centre_vx"]).reshape(1, 3))[0]))
        pas += 1
    else:
        if pas >= int(pas_max):
            fin = "plafond de pas"
    # ⚠⚠ LA PHASE SE DEROULE AVANT D'ETRE LUE. `VolumeFabriqueEnSpirale` le dit dans sa propre
    # docstring : en franchissant `theta = ±π` l'angle saute de 2π, donc la VALEUR de la phase saute
    # d'une feuille — alors que la matiere, elle, est identique. Sans deroulage, tout suiveur qui
    # fait un tour rend une derive de exactement 1,0000 feuille, et j'ai d'abord lu ce nombre comme
    # un echec de la pince. Les pas sont petits devant une feuille, donc un saut de plus d'une
    # demi-feuille entre deux pas consecutifs ne peut etre que la coupure.
    ph = np.asarray(phases, dtype=np.float64)
    if ph.size > 1:
        d = np.diff(ph)
        ph = ph[0] + np.concatenate(([0.0], np.cumsum(d - np.round(d))))
    return {"decidable": True, "pas": pas, "refus": refus, "poses_refusees": halts,
            "chemin_um": round(chemin, 1), "tour_boucle": bool(abs(cumul) >= 2.0 * np.pi * tours),
            "part_du_tour": round(float(abs(cumul) / (2.0 * np.pi)), 4), "fin": fin,
            "derive_en_feuilles": round(float(ph[-1] - ph[0]), 4),
            "derive_max_en_feuilles": round(float(np.max(np.abs(ph - ph[0]))), 4),
            "rayon_gagne_um": round(rayon_um(etat["centre_vx"]) - r0, 1),
            "epaisseur_um": (round(etat["epaisseur_um"], 1)
                             if etat.get("epaisseur_um") is not None else None),
            "saut_median_um": (round(float(np.median(ecarts)), 3) if ecarts else None),
            "lectures": int(vol.lectures)}


def un_depart(vol, angle_rad: float, rayon_mm: float, voxel_um: float, pas_um: float):
    """Un centre pose EXACTEMENT sur une feuille, et la normale que le suiveur recevra.

    ⚠ Le rayon est CIRCULAIRE, comme partout dans cette campagne : c'est ce qu'un derouleur mesure,
    et le rayon elliptique de la fixture n'est connu que d'elle.
    """
    cy, cx = vol.centre_yx_vx
    r_vx = float(rayon_mm) * 1000.0 / voxel_um
    radial = np.array([0.0, np.sin(angle_rad), np.cos(angle_rad)])
    p0 = np.array([2000.0, cy + r_vx * np.sin(angle_rad), cx + r_vx * np.cos(angle_rad)])
    ph = float(vol.phase(p0.reshape(1, 3))[0])
    depart = p0 + radial * ((round(ph) - ph) * pas_um / voxel_um)
    return depart, vol.normale_locale(depart).reshape(3)


def les_trois_bras(vol, depart_vx, normale0, largeur_um: float, epaisseur_nominale_um: float, voxel_um: float,
                   avance_um: float, axe_yx, tours: float = TOURS) -> dict:
    """Les trois bras sur le MEME depart — c'est ce qui rend la comparaison lisible."""
    out = {}
    for nom, deux, contrainte in (("une machoire", False, False),
                                  ("deux machoires libres", True, False),
                                  ("la pince", True, True)):
        vol.lectures = 0
        out[nom] = suivre(vol, depart_vx, normale0, largeur_um, epaisseur_nominale_um, voxel_um, deux,
                          contrainte, avance_um, axe_yx, tours)
    return out


def _matiere(vol_cls, ecrasement: float, amplitude_um: float, bruit: float,
             longueur_donde_um: float, rayon_mm: float, graine: int = 3):
    return vol_cls(_PAS(), amplitude_um=float(amplitude_um),
                   longueur_donde_um=float(longueur_donde_um), ecrasement=float(ecrasement),
                   r0_um=float(rayon_mm) * 1000.0, bruit=float(bruit),
                   centre_yx_vx=CENTRE_YX_VX, forme=FORME, graine=int(graine))


def _PAS() -> float:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    return float(C.PAS_UM)


def _VOXEL() -> float:
    import combien_dinterstices_traverses as C  # noqa: PLC0415

    return float(C.VOXEL_FIN_UM)


def _nom(ecrasement: float, amplitude_um: float) -> str:
    causes = []
    if ecrasement > 0.0:
        causes.append("écrasée")
    if amplitude_um > 0.0:
        causes.append(f"froissée {amplitude_um:g} µm")
    return "spirale nue" if not causes else "spirale " + " et ".join(causes)


def une_case(matiere, bruit: float, largeur_en_pas: float, departs: int = DEPARTS,
             rayon_mm: float = RAYON_MM, tours: float = TOURS,
             longueur_donde_um: float = LONGUEUR_DONDE_UM) -> dict:
    """Les trois bras sur une matiere, un niveau de bruit et une largeur — tous les departs.

    ⚠ Les trois bras partent du MEME point a chaque depart : une comparaison dont les bras ne
    partent pas du meme endroit compare des endroits.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415

    pas_um, voxel_um = _PAS(), _VOXEL()
    ecr, amp = matiere
    vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecr, amp, bruit, longueur_donde_um, rayon_mm)
    largeur_um = float(largeur_en_pas) * pas_um
    avance_um = AVANCE_EN_LONGUEUR_DONDE * float(longueur_donde_um)
    par_bras: dict = {b: [] for b in BRAS}
    for k in range(int(departs)):
        depart, n0 = un_depart(vol, 2.0 * np.pi * k / int(departs), rayon_mm, voxel_um, pas_um)
        trois = les_trois_bras(vol, depart, n0, largeur_um, pas_um, voxel_um, avance_um,
                               vol.centre_yx_vx, tours)
        for b, x in trois.items():
            par_bras[b].append({"depart_deg": round(360.0 * k / int(departs), 1), **x})
    bloc = {"ecrasement": float(ecr), "amplitude_um": float(amp), "bruit": float(bruit),
            "largeur_en_pas": float(largeur_en_pas), "largeur_um": round(largeur_um, 1),
            "avance_um": round(avance_um, 1), "nom": _nom(ecr, amp), "departs": int(departs),
            "bras": {}}
    for b in BRAS:
        bloc["bras"][b] = {"suivis": par_bras[b], **_resumer_un_bras(par_bras[b], int(departs))}
    return bloc


def _resumer_un_bras(suivis: list[dict], departs: int) -> dict:
    """Le couple qui empeche le verdict d'etre tautologique : JUSQU'OU, et SUR QUELLE FEUILLE.

    ⚠⚠ Une pince qui refuse tout ne derive jamais et ne va nulle part. Publier la derive sans la
    part du tour laisserait ce bras-la passer pour le meilleur.
    """
    bons = [x for x in suivis if x.get("decidable")]
    out = {"poses": len(bons), "poses_manquees": departs - len(bons)}
    if not bons:
        return out
    der = np.abs([x["derive_en_feuilles"] for x in bons])
    out.update({
        # ⭐⭐ LA QUESTION DU GRAAL, ET ELLE EST EXACTE. « Sur quelle feuille finit-on » se decide a
        # une DEMI-feuille : c'est la ou l'appariement au plus proche bascule, exactement comme le
        # demi-pas qui decide qu'un appui a change d'interstice. Ce n'est pas une tolerance reglee
        # sur ce qui passe, c'est l'enonce de la question. Une derive de 0,014 feuille et une de
        # 0,000 disent la MEME chose — on est sur la bonne feuille — et les departager serait
        # comparer du bruit.
        "memes_feuilles": int(np.sum(der < 0.5)),
        "derive_mediane": round(float(np.median(der)), 4),
        "derive_max": round(float(np.max(der)), 4),
        "part_du_tour_mediane": round(float(np.median([x["part_du_tour"] for x in bons])), 4),
        "tours_boucles": int(sum(1 for x in bons if x["tour_boucle"])),
        "refus_median": round(float(np.median([x["refus"] for x in bons])), 1),
        "pas_median": round(float(np.median([x["pas"] for x in bons])), 1),
        "lectures_medianes": int(np.median([x["lectures"] for x in bons])),
    })
    ep = [x["epaisseur_um"] for x in bons if x.get("epaisseur_um") is not None]
    if ep:
        out["epaisseur_mediane_um"] = round(float(np.median(ep)), 1)
    return out


MATIERES = ((0.0, 0.0), (0.2782, 0.0), (0.0, 42.4), (0.2782, 42.4), (0.2782, 100.0))
# ⚠ Le demi-cote du cube que `marcher` demande au tenseur de structure : son cout est (2d+1)³
# lectures par estimation, et il se DERIVE plutot que de se mesurer.
DEMI_DU_TENSEUR = 20


def le_prix_dune_normale(ecrasement: float = 0.2782, bruits=BRUITS, poses: int = 60,
                         largeur_en_pas: float = LARGEUR_DE_REFERENCE, rayon_mm: float = RAYON_MM,
                         graine: int = 11) -> dict:
    """Ce que coute une orientation, et ce qu'elle vaut — machoire contre gradient.

    ⭐⭐ C'EST L'ARGUMENT DU FICHIER, MESURE PLUTOT QU'AFFIRME. Une machoire rend une orientation
    parce qu'elle a une LARGEUR ; les deux solutions de rechange sont un gradient central, qui ne
    coute presque rien, et le tenseur de structure qu'emploie `marcher`, qui coute un cube.

    ⚠ La mesure est faite sur la spirale ECRASEE SEULE, sans froissement, et pour une raison : une
    machoire de demi-largeur `w` suit le plan MOYEN de la feuille sur `w`, jamais sa normale
    ponctuelle. Sur une feuille froissee les deux different reellement, et les comparer ferait lire
    un echec la ou il n'y en a pas. Sans froissement la feuille est lisse, donc les deux coincident
    et la comparaison porte sur l'estimateur.

    ⚠ Le cout du tenseur n'est pas mesure mais DERIVE de son demi-cote : il lit tout son cube.
    """
    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpiraleFroissee  # noqa: PLC0415

    pas_um, voxel_um = _PAS(), _VOXEL()
    largeur_um = float(largeur_en_pas) * pas_um
    out = []
    for bruit in bruits:
        vol = _matiere(VolumeFabriqueEnSpiraleFroissee, ecrasement, 0.0, bruit,
                       LONGUEUR_DONDE_UM, rayon_mm)
        tir = np.random.default_rng(int(graine))
        err = {"machoire": [], "gradient au voxel": [], "gradient au quart de pas": []}
        lect = {"machoire": 0, "gradient au voxel": 0, "gradient au quart de pas": 0}
        for _ in range(int(poses)):
            depart, _n = un_depart(vol, float(tir.uniform(0.0, 2.0 * np.pi)), rayon_mm, voxel_um,
                                   pas_um)
            vrai = vol.normale_locale(depart).reshape(3)
            vol.lectures = 0
            m = une_machoire(vol, depart, vrai, +1.0, largeur_um, pas_um, voxel_um)
            if m is not None:
                err["machoire"].append(_ecart_deg(m["normale"], vrai))
                lect["machoire"] = max(lect["machoire"], int(vol.lectures))
            for nom, h_um in (("gradient au voxel", voxel_um),
                              ("gradient au quart de pas", 0.25 * pas_um)):
                vol.lectures = 0
                g = []
                for ax in range(3):
                    d = np.zeros(3)
                    d[ax] = h_um / voxel_um
                    v = np.asarray(vol.lire(np.array([depart + d, depart - d])), dtype=np.float64)
                    g.append(float(v[0] - v[1]))
                gv = np.asarray(g)
                n_ = float(np.linalg.norm(gv))
                if n_ > 0.0:
                    err[nom].append(_ecart_deg(gv / n_, vrai))
                    lect[nom] = max(lect[nom], int(vol.lectures))
        bloc = {"bruit": float(bruit), "poses": int(poses)}
        for nom, xs in err.items():
            if xs:
                bloc[nom] = {"erreur_mediane_deg": round(float(np.median(xs)), 3),
                             "erreur_p90_deg": round(float(np.percentile(xs, 90)), 3),
                             "lectures": int(lect[nom])}
        bloc["tenseur de structure"] = {
            "lectures": (2 * DEMI_DU_TENSEUR + 1) ** 3,
            "demi": int(DEMI_DU_TENSEUR)}
        out.append(bloc)
    return {"ecrasement": float(ecrasement), "amplitude_um": 0.0, "poses": int(poses),
            "largeur_en_pas": float(largeur_en_pas), "largeur_um": round(largeur_um, 1),
            "par_bruit": out}


def _ecart_deg(a, b) -> float:
    """L'angle entre deux directions, au signe pres — une normale n'a pas de sens."""
    c = abs(float(np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def sur_les_matieres(matieres=MATIERES, bruits=BRUITS, largeur_en_pas: float = LARGEUR_DE_REFERENCE,
                     departs: int = DEPARTS, tours: float = TOURS) -> dict:
    """Le balayage principal : chaque matiere, chaque bruit, a la largeur de reference."""
    cases = [une_case(m, b, largeur_en_pas, departs, tours=tours)
             for m in matieres for b in bruits]
    return {"largeur_en_pas": float(largeur_en_pas), "departs": int(departs),
            "tours": float(tours), "bruits": [float(b) for b in bruits], "cases": cases}


def le_balayage_de_la_largeur(matiere, bruit: float, largeurs=LARGEURS_EN_PAS,
                              departs: int = DEPARTS, tours: float = TOURS) -> dict:
    """La largeur de machoire, balayee — jamais posee.

    ⚠ Une machoire large moyenne davantage de bruit et davantage de courbure : les deux tirent en
    sens contraire, donc il y a un compromis et il se mesure. La largeur de reference du balayage
    principal est au milieu de cet intervalle, et le lecteur voit ce que les bords donnent.
    """
    return {"ecrasement": float(matiere[0]), "amplitude_um": float(matiere[1]),
            "bruit": float(bruit), "nom": _nom(*matiere),
            "cases": [une_case(matiere, bruit, w, departs, tours=tours) for w in largeurs]}


def _gain(avant: dict, apres: dict) -> float | None:
    """De combien la derive est divisee — None quand il n'y a rien a diviser.

    ⚠ Une derive nulle n'a pas d'inverse, et une matiere ou personne ne derive ne dit rien sur ce
    que la pince achete. Rendre un gain infini y serait un chiffre qui ment.
    """
    a = avant.get("derive_mediane")
    b = apres.get("derive_mediane")
    if a is None or b is None or b <= 0.0 or a <= 0.0:
        return None
    return round(float(a / b), 3)


def juger(balayage: dict, largeurs: dict | None = None) -> dict:
    """Ou la pince gagne, de combien, et grace a quel ingredient.

    ⚠⚠ LE VERDICT EST UN COUPLE. Une pince qui refuse tout ne derive jamais : elle doit donc a la
    fois deriver le MOINS et boucler AU MOINS autant de tours que les deux autres bras. L'une des
    deux conditions seule se satisfait en ne bougeant pas.
    """
    cases = balayage.get("cases", [])
    if not cases:
        return {"decidable": False, "raison": "aucune case a juger"}
    par_case = []
    for c in cases:
        une, deux, pince = (c["bras"][b] for b in BRAS)
        # ⚠⚠ LE VERDICT PORTE SUR « LA BONNE FEUILLE », PAS SUR LA DERIVE. Departager 0,0138 de
        # 0,0143 feuille est un verdict sur du bruit : les deux finissent sur la meme feuille, donc
        # les deux ont reussi. Et le couple tient toujours — il faut AUSSI boucler autant de tours,
        # sinon un bras qui refuse tout serait declare le meilleur.
        gagne = (pince.get("memes_feuilles") is not None
                 and une.get("memes_feuilles") is not None
                 and deux.get("memes_feuilles") is not None
                 and pince["memes_feuilles"] >= max(une["memes_feuilles"], deux["memes_feuilles"])
                 and pince.get("tours_boucles", 0) >= max(une.get("tours_boucles", 0),
                                                          deux.get("tours_boucles", 0)))
        par_case.append({
            "nom": c["nom"], "ecrasement": c["ecrasement"], "amplitude_um": c["amplitude_um"],
            "bruit": c["bruit"],
            "derive_une_machoire": une.get("derive_mediane"),
            "derive_deux_libres": deux.get("derive_mediane"),
            "derive_la_pince": pince.get("derive_mediane"),
            "memes_une_machoire": une.get("memes_feuilles"),
            "memes_deux_libres": deux.get("memes_feuilles"),
            "memes_la_pince": pince.get("memes_feuilles"),
            "poses": c["departs"],
            "tours_une_machoire": une.get("tours_boucles"),
            "tours_deux_libres": deux.get("tours_boucles"),
            "tours_la_pince": pince.get("tours_boucles"),
            "gain_de_la_seconde_machoire": _gain(une, deux),
            "gain_de_la_contrainte": _gain(deux, pince),
            "gain_total": _gain(une, pince),
            # ⚠⚠ « CETTE CASE NE SEPARE RIEN » EST UN ENONCE DU PRODUCTEUR, PAS DE LA FIGURE. Une
            # figure qui le deciderait de son cote serait une seconde reponse a la meme question,
            # et les deux ont deja diverge une fois : le tableau en comptait deux quand l'image en
            # peignait cinq. Une case ne separe rien quand TOUS les bras trouvent la bonne feuille
            # a tous les departs ET bouclent tous leurs tours.
            "rien_a_separer": bool(
                all(x.get("memes_feuilles") == c["departs"]
                    and x.get("tours_boucles") == c["departs"] for x in (une, deux, pince))),
            "la_pince_gagne": bool(gagne)})
    out = {"decidable": True, "cases": len(par_case), "par_case": par_case,
           "cases_ou_la_pince_gagne": sum(1 for x in par_case if x["la_pince_gagne"])}
    # ⚠ La case de tete est DERIVEE — celle ou le gain total est le plus grand — et jamais choisie
    # parce qu'elle raconte bien.
    avec = [x for x in par_case if x["gain_total"] is not None]
    if avec:
        t = max(avec, key=lambda x: x["gain_total"])
        out["la_case_qui_separe"] = t
    # ⚠ Et la case ou PERSONNE ne derive est le controle : elle doit exister, sinon le balayage
    # n'a pas de matiere facile et « la pince gagne » n'a rien a quoi se comparer.
    out["cases_ou_personne_ne_derive"] = sum(1 for x in par_case if x["rien_a_separer"])
    # ⚠⚠ Un TEMOIN n'est pas une victoire. Dans une case ou les trois bras reussissent tout, la
    # pince « gagne » par egalite, et compter ces cases-la dans son score gonflerait le resultat
    # d'exactement ce que le temoin sert a exclure. Le nombre qui compte est celui des cases qui
    # separent quelque chose.
    out["cases_qui_separent"] = sum(1 for x in par_case if not x["rien_a_separer"])
    out["gagne_parmi_celles_qui_separent"] = sum(
        1 for x in par_case if x["la_pince_gagne"] and not x["rien_a_separer"])
    if largeurs:
        out["par_largeur"] = [{
            "largeur_en_pas": c["largeur_en_pas"], "largeur_um": c["largeur_um"],
            "derive_la_pince": c["bras"]["la pince"].get("derive_mediane"),
            "tours_la_pince": c["bras"]["la pince"].get("tours_boucles"),
            "derive_une_machoire": c["bras"]["une machoire"].get("derive_mediane")}
            for c in largeurs.get("cases", [])]
    return out


def reagreger(r: dict) -> dict:
    """Recalcule tout ce qui se derive des suivis ranges — sans remarcher quoi que ce soit."""
    for bloc in (r.get("sur_les_matieres"), r.get("le_balayage_de_la_largeur")):
        if not bloc:
            continue
        for c in bloc.get("cases", []):
            for nom in BRAS:
                suivis = c["bras"][nom]["suivis"]
                c["bras"][nom] = {"suivis": suivis,
                                  **_resumer_un_bras(suivis, int(c["departs"]))}
    r["juger"] = juger(r["sur_les_matieres"], r.get("le_balayage_de_la_largeur"))
    return r


def mesurer(matieres=MATIERES, bruits=BRUITS, departs: int = DEPARTS, tours: float = TOURS,
            largeurs=LARGEURS_EN_PAS) -> dict:
    balayage = sur_les_matieres(matieres, bruits, LARGEUR_DE_REFERENCE, departs, tours)
    verdict = juger(balayage)
    # ⚠ La matiere et le bruit du balayage de largeur sont DERIVES du balayage principal : c'est la
    # case ou la pince separe le plus, pas une case choisie pour illustrer.
    tete = verdict.get("la_case_qui_separe")
    lar = None
    if tete is not None:
        lar = le_balayage_de_la_largeur((tete["ecrasement"], tete["amplitude_um"]), tete["bruit"],
                                        largeurs, departs, tours)
    return {"le_prix_dune_normale": le_prix_dune_normale(), "sur_les_matieres": balayage,
            "le_balayage_de_la_largeur": lar, "juger": juger(balayage, lar)}


def afficher(r: dict) -> None:
    if "message" in r:
        print(f"⚠ {r['message']}")
        return
    pr = r.get("le_prix_dune_normale")
    if pr:
        print(f"ce que coûte une orientation, sur spirale écrasée seule, {pr['poses']} poses "
              f"(mâchoire de {pr['largeur_um']:g} µm) :")
        print(f"   {'bruit':>6} | {'mâchoire':>22} | {'gradient au voxel':>22} | "
              f"{'gradient au quart de pas':>26} | {'tenseur':>10}")
        for x in pr["par_bruit"]:
            ligne = f"   {x['bruit']:>6g} |"
            for k in ("machoire", "gradient au voxel", "gradient au quart de pas"):
                y = x.get(k)
                ligne += (f" {y['erreur_mediane_deg']:>9.3f}° {y['lectures']:>6d} lect |"
                          if y else f" {'—':>22} |")
            ligne += f" {x['tenseur de structure']['lectures']:>6d} lect"
            print(ligne)
        print()
    b = r["sur_les_matieres"]
    print(f"un tour entier, {b['departs']} départs, largeur de mâchoire {b['largeur_en_pas']:g} pas "
          f"— dérive médiane en feuilles, et tours bouclés sur {b['departs']} :")
    print(f"   {'matière':>26} {'bruit':>6} | {'une mâchoire':>21} | {'deux libres':>21} | "
          f"{'la pince':>21}")
    print(f"   {'':>26} {'':>6} | {'dérive  feuille tour':>21} | {'dérive  feuille tour':>21} | "
          f"{'dérive  feuille tour':>21}")
    for c in b["cases"]:
        ligne = f"   {c['nom']:>26} {c['bruit']:>6g} |"
        for nom in BRAS:
            x = c["bras"][nom]
            if x.get("derive_mediane") is None:
                ligne += f" {'aucune pose':>22} |"
            else:
                ligne += (f" {x['derive_mediane']:>8.4f} {x['memes_feuilles']:>2d}/"
                          f"{c['departs']:<2d} {x['tours_boucles']:>2d}/"
                          f"{c['departs']:<2d} |")
        print(ligne.rstrip("|"))
    j = r.get("juger", {})
    if not j.get("decidable"):
        print(f"\n⚠ {j.get('raison', 'indécidable')}")
        return
    if j.get("par_largeur"):
        l0 = r["le_balayage_de_la_largeur"]
        print(f"\n   la largeur de mâchoire, balayée sur {l0['nom']} à bruit {l0['bruit']:g} :")
        for x in j["par_largeur"]:
            print(f"     {x['largeur_en_pas']:>6.3f} pas ({x['largeur_um']:>6.1f} µm) : "
                  f"la pince dérive de {x['derive_la_pince']:.4f} et boucle "
                  f"{x['tours_la_pince']}, une mâchoire {x['derive_une_machoire']:.4f}")
    t = j.get("la_case_qui_separe")
    if t is not None:
        print(f"\n★★★★ là où la pince sépare le plus — {t['nom']}, bruit {t['bruit']:g} :")
        print(f"     une mâchoire finit sur la bonne feuille {t['memes_une_machoire']} fois sur "
              f"{t['poses']} (dérive {t['derive_une_machoire']:.4f}) et boucle "
              f"{t['tours_une_machoire']} tours ; deux libres {t['memes_deux_libres']} fois "
              f"({t['derive_deux_libres']:.4f}) et {t['tours_deux_libres']} ; la pince "
              f"{t['memes_la_pince']} fois ({t['derive_la_pince']:.4f}) et {t['tours_la_pince']}")
        print(f"     la seconde mâchoire divise la dérive par {t['gain_de_la_seconde_machoire']}, "
              f"la contrainte par {t['gain_de_la_contrainte']} de plus — "
              f"{t['gain_total']} en tout")
    print(f"\n   {j['cases_ou_personne_ne_derive']} cases sur {j['cases']} ne séparent rien — "
          f"c'est le témoin ; la pince gagne dans "
          f"{j['gagne_parmi_celles_qui_separent']} des {j['cases_qui_separent']} qui séparent")


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    from combien_de_pas_la_matiere_porte import VolumeFabriqueEnSpirale  # noqa: PLC0415

    pas_um, voxel_um = _PAS(), _VOXEL()
    nue = VolumeFabriqueEnSpirale(pas_um, r0_um=RAYON_MM * 1000.0, centre_yx_vx=CENTRE_YX_VX,
                                  forme=FORME, bruit=0.0, graine=3)
    depart, n0 = un_depart(nue, 0.0, RAYON_MM, voxel_um, pas_um)
    v("un départ tombe EXACTEMENT sur une feuille",
      abs(float(nue.phase(depart.reshape(1, 3))[0])) < 1e-9,
      f"phase {float(nue.phase(depart.reshape(1, 3))[0]):.2e}")

    # ---- l'interstice
    d = linterstice(nue, depart, n0, 0.5 * pas_um, pas_um, voxel_um)
    v("l'interstice suivant est à un DEMI-pas d'une feuille",
      d is not None and abs(d - 0.5 * pas_um) < 0.05, f"{d:.4f} contre {0.5 * pas_um}")
    v("⭐ le raffinement parabolique bat la maille du voxel",
      d is not None and abs(d - 0.5 * pas_um) < 0.2 * voxel_um,
      f"écart {abs(d - 0.5 * pas_um):.4f} µm pour un voxel de {voxel_um}")
    # ⚠ la sonde : une fenêtre qui exclut l'interstice ne doit rien rendre, jamais son bord
    v("⭐⭐ un minimum au BORD de la fenêtre est refusé, jamais rendu",
      linterstice(nue, depart, n0, 0.05 * pas_um, 0.05 * pas_um, voxel_um) is None,
      "sinon l'épaisseur s'effondre et la pince se referme sur elle-même")
    v("une fenêtre trop étroite pour trois échantillons est refusée",
      linterstice(nue, depart, n0, 0.5 * pas_um, voxel_um, voxel_um) is None)
    v("hors du volume, l'interstice est refusé et jamais deviné",
      linterstice(nue, np.array([2000.0, 1.0, 1.0]), np.array([0.0, -1.0, 0.0]),
                  0.5 * pas_um, pas_um, voxel_um) is None)

    # ---- la mâchoire
    m = une_machoire(nue, depart, n0, +1.0, 0.25 * pas_um, pas_um, voxel_um)
    vrai = nue.normale_locale(depart).reshape(3)
    ang = float(np.degrees(np.arccos(np.clip(abs(float(m["normale"] @ vrai)), -1.0, 1.0))))
    v("⭐⭐ une mâchoire rend l'orientation SANS tenseur de structure", ang < 0.05,
      f"{ang:.4f}° de la vraie normale")
    v("⭐ ... et elle le doit à sa LARGEUR : un appui unique est refusé, pas deviné",
      une_machoire(nue, depart, n0, +1.0, 0.25 * pas_um, pas_um, voxel_um, appuis=1) is None,
      "un point seul ne forme aucun nuage, donc il ne porte aucune direction")
    v("... et deux appuis suffisent à en porter une",
      une_machoire(nue, depart, n0, +1.0, 0.25 * pas_um, pas_um, voxel_um, appuis=2) is not None)

    # ---- poser : ce que la seconde mâchoire achète
    un = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, deux=False)
    deux = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, deux=True)
    v("avec une seule mâchoire, l'épaisseur est SUPPOSÉE et le dit",
      un["epaisseur_um"] is None and un["suppose"] is True)
    v("⭐ avec deux, elle est MESURÉE et vaut le pas",
      deux["epaisseur_um"] is not None and abs(deux["epaisseur_um"] - pas_um) < 0.1,
      f"{deux['epaisseur_um']} contre {pas_um}")
    v("... et le centre mesuré est celui du départ",
      float(np.linalg.norm(np.asarray(deux["centre_vx"]) - depart)) * voxel_um < 1.0)

    # ---- ⭐ le contrôle : sur une matière facile, personne ne dérive
    trois = les_trois_bras(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um,
                           0.25 * LONGUEUR_DONDE_UM, nue.centre_yx_vx, tours=0.25)
    v("⭐⭐ sur une spirale NUE les trois bras bouclent et ne dérivent pas",
      all(x["decidable"] and x["tour_boucle"] and abs(x["derive_en_feuilles"]) < 0.01
          for x in trois.values()),
      " · ".join(f"{k[:3]} {x['derive_en_feuilles']:+.4f}" for k, x in trois.items()))
    v("... donc les gains que la pince montre ailleurs ne sont pas automatiques",
      _gain(_resumer_un_bras([trois["une machoire"]], 1),
            _resumer_un_bras([trois["la pince"]], 1)) is None,
      "une dérive nulle n'a pas d'inverse, et le dire vaut mieux qu'un gain infini")

    # ---- ⭐⭐ la phase est DÉROULÉE : la coupure n'est pas une dérive
    tour = suivre(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True, False,
                  0.25 * LONGUEUR_DONDE_UM, nue.centre_yx_vx, tours=1.0)
    v("⭐⭐ un tour ENTIER sur une spirale nue ne dérive pas d'une feuille",
      tour["decidable"] and tour["tour_boucle"] and abs(tour["derive_en_feuilles"]) < 0.01,
      f"{tour['derive_en_feuilles']:+.4f} — sans déroulage la coupure angulaire en rendrait 1,0000")
    v("... et le rayon a bien bougé d'un pas sur le tour",
      abs(abs(tour["rayon_gagne_um"]) - pas_um) < 0.2 * pas_um,
      f"{tour['rayon_gagne_um']:+.1f} µm pour un pas de {pas_um}")

    # ---- le refus, et son énoncé exact
    e = {"normale": np.array([0.0, 1.0, 0.0]),
         "haut": {"milieu_vx": np.array([0.0, 10.0, 0.0])},
         "bas": {"milieu_vx": np.array([0.0, -10.0, 0.0])}}
    n = e["normale"]
    for saut_um, attendu in ((0.49 * pas_um, False), (0.51 * pas_um, True)):
        neuf = {"haut": {"milieu_vx": e["haut"]["milieu_vx"] + n * (saut_um / voxel_um)},
                "bas": {"milieu_vx": e["bas"]["milieu_vx"]}}
        saut = max(abs(float((np.asarray(neuf[c]["milieu_vx"])
                              - np.asarray(e[c]["milieu_vx"])) @ n)) * voxel_um
                   for c in ("haut", "bas"))
        v(f"un appui qui bouge de {saut_um / pas_um:.2f} pas est "
          f"{'refusé' if attendu else 'accepté'}",
          (saut >= 0.5 * pas_um) is attendu, f"saut {saut:.1f} µm")

    # ---- ⭐⭐ le jugement exige les DEUX conditions
    def case(m1, m2, m3, t1, t2, t3, d1=1.0, d2=0.5, d3=0.1):
        def bras(m, t, d):
            return {"memes_feuilles": m, "tours_boucles": t, "derive_mediane": d}
        return {"cases": [{"nom": "x", "ecrasement": 0.0, "amplitude_um": 0.0, "bruit": 0.0,
                           "departs": 12, "bras": {"une machoire": bras(m1, t1, d1),
                                                   "deux machoires libres": bras(m2, t2, d2),
                                                   "la pince": bras(m3, t3, d3)}}]}

    v("une pince qui finit sur la bonne feuille plus souvent ET boucle autant gagne",
      juger(case(6, 9, 12, 3, 5, 6))["par_case"][0]["la_pince_gagne"] is True)
    v("⭐⭐ une pince qui trouve la bonne feuille mais boucle MOINS ne gagne pas",
      juger(case(6, 9, 12, 3, 5, 1))["par_case"][0]["la_pince_gagne"] is False,
      "sinon un bras qui refuse tout serait déclaré le meilleur")
    v("⭐⭐ une dérive plus petite ne suffit PAS si la feuille n'est pas mieux trouvée",
      juger(case(12, 12, 11, 6, 6, 6, d3=0.0001))["par_case"][0]["la_pince_gagne"] is False,
      "0,014 feuille et 0,000 feuille disent la même chose : la bonne feuille")
    v("une pince qui trouve la feuille autant de fois et boucle autant gagne",
      juger(case(12, 12, 12, 6, 6, 6))["par_case"][0]["la_pince_gagne"] is True)
    v("les deux gains se décomposent",
      juger(case(6, 9, 12, 3, 5, 6))["par_case"][0]["gain_de_la_seconde_machoire"] == 2.0
      and juger(case(6, 9, 12, 3, 5, 6))["par_case"][0]["gain_de_la_contrainte"] == 5.0)
    v("un jugement sans case est indécidable", not juger({"cases": []})["decidable"])
    v("⭐ une case où les trois bras réussissent tout est le témoin, et c'est le PRODUCTEUR qui "
      "le dit",
      juger(case(12, 12, 12, 12, 12, 12))["cases_ou_personne_ne_derive"] == 1
      and juger(case(12, 12, 12, 12, 12, 12))["par_case"][0]["rien_a_separer"] is True)
    v("... et une case où un bras rate quelque chose n'en est pas un",
      juger(case(12, 12, 12, 11, 12, 12))["par_case"][0]["rien_a_separer"] is False)
    v("⭐⭐ un témoin n'est PAS compté comme une victoire de la pince",
      juger(case(12, 12, 12, 12, 12, 12))["gagne_parmi_celles_qui_separent"] == 0
      and juger(case(12, 12, 12, 12, 12, 12))["cases_qui_separent"] == 0,
      "sinon le score de la pince serait gonflé par les cases où elle n'a rien fait")

    # ---- une case : les trois bras partent du même point
    c = une_case((0.0, 0.0), 0.0, 0.25, departs=2, tours=0.1)
    parts = {b: [x["depart_deg"] for x in c["bras"][b]["suivis"]] for b in BRAS}
    v("les trois bras partent des MÊMES départs",
      parts[BRAS[0]] == parts[BRAS[1]] == parts[BRAS[2]], str(parts[BRAS[0]]))
    c2 = une_case((0.0, 0.0), 0.0, 0.25, departs=2, tours=0.1)
    v("une case est reproductible",
      c["bras"]["la pince"]["derive_mediane"] == c2["bras"]["la pince"]["derive_mediane"])

    # ---- ⭐ ce que coûte une orientation, et la sonde qui mord DANS LES DEUX SENS
    pr = le_prix_dune_normale(poses=12, bruits=(0.0, 8.0))
    v("le prix d'une normale se mesure sur une matière SANS froissement",
      pr["amplitude_um"] == 0.0,
      "sinon on comparerait le plan moyen d'une mâchoire à une normale ponctuelle")
    sans, avec = pr["par_bruit"][0], pr["par_bruit"][1]
    v("⭐⭐ sans bruit, c'est le GRADIENT qui gagne — et le dire est ce qui rend l'autre moitié "
      "crédible",
      sans["gradient au voxel"]["erreur_mediane_deg"] < sans["machoire"]["erreur_mediane_deg"],
      f"{sans['gradient au voxel']['erreur_mediane_deg']}° contre "
      f"{sans['machoire']['erreur_mediane_deg']}°")
    v("⭐⭐ avec du bruit, il s'effondre et la mâchoire tient",
      avec["gradient au voxel"]["erreur_mediane_deg"]
      > 5.0 * avec["machoire"]["erreur_mediane_deg"],
      f"{avec['gradient au voxel']['erreur_mediane_deg']}° contre "
      f"{avec['machoire']['erreur_mediane_deg']}°")
    v("... et l'élargir ne le sauve pas", avec["gradient au quart de pas"]["erreur_mediane_deg"]
      > avec["machoire"]["erreur_mediane_deg"])
    v("le coût du tenseur est DÉRIVÉ de son demi-côté, jamais mesuré",
      sans["tenseur de structure"]["lectures"]
      == (2 * sans["tenseur de structure"]["demi"] + 1) ** 3,
      f"{sans['tenseur de structure']['lectures']} lectures")
    v("⭐ une mâchoire coûte plus de cent fois moins que le tenseur",
      sans["machoire"]["lectures"] * 100 < sans["tenseur de structure"]["lectures"],
      f"{sans['machoire']['lectures']} contre {sans['tenseur de structure']['lectures']}")
    v("un écart de directions ne regarde pas leur signe",
      abs(_ecart_deg([0.0, 1.0, 0.0], [0.0, -1.0, 0.0])) < 1e-9)

    import contextlib  # noqa: PLC0415
    import io  # noqa: PLC0415

    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        afficher({"message": "fixture injoignable"})
    v("un message est dit, jamais dessiné", "⚠" in tampon.getvalue())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--departs", type=int, default=DEPARTS)
    p.add_argument("--tours", type=float, default=TOURS)
    p.add_argument("--verifier", action="store_true")
    # ⚠ Recalculer les resumes et le verdict depuis les suivis ranges, sans remarcher : une regle
    # de jugement qui change ne doit pas couter dix minutes de marche. C'est le `--reagreger` de
    # `138` et le `--rejuger` de `141`, sous le meme nom que le premier.
    p.add_argument("--reagreger", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.reagreger is not None:
        r = reagreger(json.loads(a.reagreger.read_text()))
        afficher(r)
        a.reagreger.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.reagreger}")
        return 0
    r = mesurer(departs=a.departs, tours=a.tours)
    afficher(r)
    if "message" in r:
        return 1
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
