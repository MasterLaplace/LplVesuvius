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


def _garder_les_appuis(ecarts, epaisseur_um: float, minimum: int):
    """Quels appuis sont sur LE MEME interstice que la mediane de leur machoire ?

    ⭐⭐⭐⭐ L'ENONCE EST EXACT, PAS UN SEUIL. Les interstices sont espaces d'UNE epaisseur, donc
    « a plus d'une DEMI-epaisseur de la mediane » et « sur un AUTRE interstice » sont le MEME
    enonce — c'est le meme raisonnement que le refus de la pince, qui bascule exactement a un
    demi-pas. Aucune constante n'entre, et la regle ne se regle pas.

    ⚠⚠ LA MEDIANE PLUTOT QUE LA MOYENNE, et c'est ce qui rend la regle utilisable : un appui pose
    sur l'interstice voisin deplace une moyenne d'un tiers d'epaisseur sur trois appuis, donc il
    emporterait la reference qui doit le juger. C'est le motif « toute quantite que la correction
    enfle elle-meme est impropre a decider de cette correction », et la mediane y echappe.

    ⚠ Rend `None` s'il ne reste pas de quoi ajuster : refuser vaut mieux qu'ajuster sur un nuage
    qui ne porte plus la forme qu'on lui demande.
    """
    e = np.asarray(ecarts, dtype=np.float64)
    garde = np.abs(e - float(np.median(e))) < 0.5 * float(epaisseur_um)
    return None if int(garde.sum()) < int(minimum) else garde


def une_machoire(vol, centre_vx, normale, sens: float, largeur_um: float, epaisseur_um: float,
                 voxel_um: float, appuis: int = APPUIS, marge_um: float = 0.0,
                 rejeter: bool = False) -> dict | None:
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
        # ⭐⭐⭐ LA MARGE ELARGIT LA FENETRE SANS DEPLACER SON CENTRE. `142` la voulait large d'UNE
        # epaisseur parce que les interstices sont espaces d'une epaisseur : elle en contient alors
        # exactement un. Mais un froissement DEPLACE l'interstice, et une fenetre d'une epaisseur ne
        # le contient que si ce deplacement reste sous la DEMI-epaisseur. Au-dela, la machoire ne
        # trouve plus de minimum encadre et refuse — c'est un ARRET, pas une derive.
        d = linterstice(vol, q, sens * n, 0.5 * float(epaisseur_um),
                        float(epaisseur_um) + 2.0 * abs(float(marge_um)), voxel_um)
        if d is None:
            return None
        pts.append(q + sens * n * (d / voxel_um))
        ecarts.append(d)
    P = np.asarray(pts, dtype=np.float64)
    rejetes = 0
    if rejeter:
        # ⚠⚠ DEUX APPUIS SUFFISENT A PORTER UNE DROITE, donc c'est le minimum ici — et c'est deja
        # ce que `une_machoire` exige d'entree.
        garde = _garder_les_appuis(ecarts, epaisseur_um, 2)
        if garde is None:
            return None
        rejetes = int(P.shape[0] - int(garde.sum()))
        P = P[garde]
        ecarts = [x for x, g in zip(ecarts, garde) if bool(g)]
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
            "ecarts_um": [float(x) for x in ecarts], "rejetes": int(rejetes)}


def une_machoire_en_croix(vol, centre_vx, normale, sens: float, largeur_um: float,
                          epaisseur_um: float, voxel_um: float, appuis: int = APPUIS,
                          marge_um: float = 0.0, rejeter: bool = False) -> dict | None:
    """Une machoire a DEUX barres croisees — son nuage porte un PLAN, donc une normale hors du tour.

    ⭐⭐⭐⭐ POURQUOI ELLE EXISTE, ET C'EST UNE PANNE STRUCTURELLE DE `une_machoire`. Celle-ci pose
    ses appuis le long de `t = z x n`, donc sur UNE droite, et rend `n' = t' x z` — une normale
    qui est TOUJOURS perpendiculaire a l'axe, par construction. Or `153` mesure que la vraie
    normale d'une feuille FROISSEE sort du plan du tour : `|n.z|` vaut exactement 0,000000 sur les
    matieres lisses et 0,227922 sur celle du rouleau. Cette composante-la est donc invisible a une
    machoire en segment, et aucun reglage ne la rend visible : ni la largeur, ni le nombre
    d'appuis, ni la facon d'ajuster.

    ⚠⚠ UN NUAGE COLINEAIRE PORTE UNE DIRECTION, PAS UN PLAN. C'est toute la difference : trois
    points alignes definissent une droite et laissent une famille de plans qui la contiennent, donc
    le choix du plan doit venir d'ailleurs — et `une_machoire` le prend en imposant `z` dedans. Deux
    barres croisees suppriment le choix : le nuage n'est plus colineaire, et la normale devient la
    PLUS PETITE direction de sa decomposition, celle qui n'est portee par aucun appui.

    ⚠ La seconde barre est `n x t`, qui est DANS la feuille et porte l'axe : la prendre selon `z`
    tout court la ferait sortir de la feuille des que la normale penche, et les appuis chercheraient
    leur interstice depuis un point qui n'est plus sur la surface.
    """
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
    for axe in (tan, np.cross(n, tan)):
        for u in np.linspace(-float(largeur_um), float(largeur_um), int(appuis)):
            q = np.asarray(centre_vx, dtype=np.float64) + axe * (u / voxel_um)
            d = linterstice(vol, q, sens * n, 0.5 * float(epaisseur_um),
                            float(epaisseur_um) + 2.0 * abs(float(marge_um)), voxel_um)
            if d is None:
                return None
            pts.append(q + sens * n * (d / voxel_um))
            ecarts.append(d)
    P = np.asarray(pts, dtype=np.float64)
    rejetes = 0
    if rejeter:
        # ⚠⚠ TROIS APPUIS AU MOINS POUR UN PLAN : deux en definissent une infinite, donc la plus
        # petite direction d'un nuage colineaire ne veut rien dire. C'est la seule difference avec
        # le segment, et elle vient de ce qu'on ajuste.
        garde = _garder_les_appuis(ecarts, epaisseur_um, 3)
        if garde is None:
            return None
        rejetes = int(P.shape[0] - int(garde.sum()))
        P = P[garde]
        ecarts = [x for x, g in zip(ecarts, garde) if bool(g)]
    milieu = P.mean(axis=0)
    nn = np.linalg.svd(P - milieu, full_matrices=False)[2][-1]
    norme = float(np.linalg.norm(nn))
    if norme < 1e-9:
        return None
    nn = nn / norme
    if float(nn @ n) < 0.0:
        nn = -nn
    return {"milieu_vx": milieu, "normale": nn, "ecart_um": float(np.median(ecarts)),
            "ecarts_um": [float(x) for x in ecarts], "rejetes": int(rejetes)}


def poser(vol, centre_vx, normale, largeur_um: float, epaisseur_um: float, voxel_um: float,
          deux: bool, appuis: int = APPUIS, marge_um: float = 0.0,
          deux_temps: bool = False, en_croix: bool = False,
          rejeter: bool = False) -> dict | None:
    """L'etat d'un bras : une machoire, ou deux et l'epaisseur qu'elles MESURENT.

    ⚠⚠ C'est la seule difference de fond entre le premier bras et le second. Avec une machoire, ou
    est la feuille se SUPPOSE — une demi-epaisseur sous l'appui, c'est-a-dire un demi-pas, la valeur
    nominale. Avec deux, elle se MESURE, et le centre est le milieu de ce qu'on tient.

    ⭐⭐⭐⭐ `deux_temps` EST LA TROISIEME SOURCE DE DIRECTION, ET LA SEULE QUE `150` N'AIT PAS
    FERMEE. Les machoires ont besoin d'une direction DROITE et FRAICHE. Le melange du cap est frais
    et penche (40,569° sur la matiere du rouleau, ou la pose tombe a 633 ‰) ; la lecture precedente
    est droite et date d'un quart de periode (96 reussites contre 108). Poser DEUX FOIS n'emprunte
    ni l'une ni l'autre : la premiere pose sert a LIRE la normale ici et maintenant, la seconde est
    celle qu'on garde. Aucune constante n'entre — c'est deux appels au lieu d'un.

    ⚠⚠⚠ ET UNE POSE EN DEUX TEMPS NE PEUT PAS REUSSIR PLUS SOUVENT QU'UNE POSE SIMPLE. Le second
    temps n'a lieu que si le premier a rendu quelque chose, donc sa reussite est une CONJONCTION :
    `P(deux temps) <= P(un temps)`, par construction et non par mesure. Ce que le second temps peut
    acheter n'est donc pas un taux de pose — c'est la JUSTESSE de la normale rendue, qui decide de
    la pose SUIVANTE. Le dire ici evite de mesurer un theoreme.

    ⚠⚠ LE CENTRE NE BOUGE PAS ENTRE LES DEUX TEMPS, et c'est ce qui garde la mesure lisible. Repartir
    du centre que la premiere pose a trouve changerait DEUX choses a la fois — la direction et le
    point — et aucune des deux ne serait imputable. Le suiveur n'a pas avance entre les deux temps ;
    seule sa direction a ete relue.
    """
    if deux_temps:
        premier = poser(vol, centre_vx, normale, largeur_um, epaisseur_um, voxel_um, deux,
                        appuis, marge_um, en_croix=en_croix, rejeter=rejeter)
        if premier is None:
            return None
        return poser(vol, centre_vx, premier["normale"], largeur_um, epaisseur_um, voxel_um,
                     deux, appuis, marge_um, en_croix=en_croix, rejeter=rejeter)
    # ⚠ UN SEUL INGREDIENT CHANGE : la croix ne touche QUE la facon dont une machoire rend son
    # orientation. Tout le reste — la fenetre, le refus du bord, l'epaisseur mesuree, le centre —
    # est celui de `142`, sans quoi un gain ne serait imputable a rien.
    machoire = une_machoire_en_croix if en_croix else une_machoire
    haut = machoire(vol, centre_vx, normale, +1.0, largeur_um, epaisseur_um, voxel_um,
                    appuis, marge_um, rejeter)
    if haut is None:
        return None
    if not deux:
        n = haut["normale"]
        return {"centre_vx": haut["milieu_vx"] - n * (0.5 * epaisseur_um / voxel_um),
                "normale": n, "haut": haut, "bas": None,
                "rejetes": int(haut.get("rejetes", 0)),
                "epaisseur_um": None, "suppose": True}
    bas = machoire(vol, centre_vx, normale, -1.0, largeur_um, epaisseur_um, voxel_um,
                   appuis, marge_um, rejeter)
    if bas is None:
        return None
    m = haut["normale"] + bas["normale"]
    norme = float(np.linalg.norm(m))
    n = m / norme if norme > 1e-9 else haut["normale"]
    return {"centre_vx": 0.5 * (haut["milieu_vx"] + bas["milieu_vx"]), "normale": n,
            "haut": haut, "bas": bas, "suppose": False,
            # ⚠⚠ LE COMPTE D'APPUIS REJETES EST PUBLIE, et c'est ce qui remplace un seuil : « cette
            # pose a ete touchee » se lit alors EXACTEMENT, au lieu de comparer deux normales a
            # 1e-9 — une tolerance sous la reproductibilite de la decomposition, qui comptait du
            # bruit numerique comme un effet.
            "rejetes": int(haut.get("rejetes", 0) + bas.get("rejetes", 0)),
            "epaisseur_um": float(np.linalg.norm(
                haut["milieu_vx"] - bas["milieu_vx"]) * voxel_um)}


def _ecart_angulaire(avant, apres) -> float:
    """De combien la normale a tourne dans le plan, en radians signes.

    ⚠ Signe : deux normales opposees decrivent la meme feuille, mais ici les deux viennent d'une
    meme marche ou le signe est deja aligne, donc l'angle signe a un sens et c'est lui qui porte le
    fait qu'une rotation PERSISTE ou ALTERNE.
    """
    a = np.asarray(avant, dtype=np.float64)
    b = np.asarray(apres, dtype=np.float64)
    return float(np.arctan2(a[2] * b[1] - a[1] * b[2], a[1] * b[1] + a[2] * b[2]))


def _tourner(normale, phi: float) -> np.ndarray:
    """Tourner une normale de `phi` radians DANS LE PLAN DU TOUR, au signe de `_ecart_angulaire`.

    ⚠⚠ LE SIGNE EST LA SEULE CHOSE QUI COMPTE ICI, ET IL SE VERIFIE PLUTOT QU'IL NE SE RAISONNE :
    `_ecart_angulaire(n, _tourner(n, phi))` doit rendre `phi`. Une convention inversee ferait tourner
    le cap A CONTRESENS — ce qui ne ressemble pas a une faute de signe mais a « le cap tournant
    marche moins bien », un resultat parfaitement plausible et faux. La batterie l'exige.

    ⚠ La composante d'axe est laissee telle quelle : `_ecart_angulaire` ne lit que le plan du tour,
    donc la toucher ferait tourner la normale d'un angle que la mesure ne peut pas rendre.
    """
    n = np.asarray(normale, dtype=np.float64).astype(np.float64).copy()
    c, s_ = np.cos(float(phi)), np.sin(float(phi))
    y, z = float(n[1]), float(n[2])
    n[1] = y * c + z * s_
    n[2] = -y * s_ + z * c
    return n


def taux_du_cap(rotations, fenetre: int, enroulement: float, sens: float, regle: str) -> float:
    """De combien le cap doit TOURNER a ce pas — un enonce, pas un ajustement.

    ⭐⭐⭐⭐ UN CAP QUI NE TOURNE PAS COMBAT L'ENROULEMENT LUI-MEME. La memoire de `143` retient une
    ORIENTATION fixe : a memoire 0,8 le suiveur garde quatre cinquiemes de la direction precedente,
    donc il resiste aussi a la rotation que le tour lui IMPOSE — 2π sur un tour entier. C'est
    exactement l'echange que `143` mesure, fidelite contre distance (feuilles 121 → 105, tours
    93 → 125), et rien ne disait que cet echange etait une propriete de la matiere plutot qu'un
    defaut du cap.

    ⭐⭐⭐ TROIS REGLES, ET ELLES ISOLENT LES DEUX INGREDIENTS QUE `146` NOMME :
    - `enroulement` : le cap tourne de `avance / rayon`, la seule quantite ABSOLUE qu'un suiveur
      calcule seul. Aucune estimation, donc aucun risque de suivre son propre bruit.
    - `taux` : le cap tourne de la moyenne des increments lus sur la fenetre — la part COHERENTE de
      la rotation, celle qui persiste. Sur une spirale nue cette moyenne VAUT l'enroulement ; sur un
      ecrasement elle vaut davantage ; sur un froissement, dont les increments alternent, elle
      retombe sur l'enroulement toute seule.
    - `taux_planche` : les deux ensemble — la moyenne lue, mais jamais moins que l'enroulement, et
      jamais a contresens de la marche.

    ⚠⚠ CECI N'EST PAS LE PIEGE DE `144`. Retirer la MOYENNE des increments avant d'en lire la
    coherence detruit la persistance qu'on veut detecter, et la batterie de `144` l'a dit avant la
    mesure. Ici la moyenne n'est retiree de RIEN : la coherence se lit toujours sur les increments
    bruts, et la moyenne ne sert qu'a PREDIRE le pas suivant. Lire et predire ne sont pas le meme
    usage d'une meme quantite.

    ⚠ Le SENS de la marche est a la main du suiveur — c'est le signe de son propre angle parcouru,
    pas une propriete de la matiere. Une moyenne lue a CONTRESENS du tour ne peut pas etre une
    rotation que le tour impose, donc `taux_planche` retombe alors sur l'enroulement seul.
    """
    f = max(int(fenetre), 2)
    r = np.asarray(rotations[-f:], dtype=np.float64)
    if r.size < 2:
        return 0.0
    w = abs(float(enroulement))
    s_ = 1.0 if float(sens) >= 0.0 else -1.0
    moyenne = float(r.mean())
    if regle == "enroulement":
        return s_ * w
    if regle == "taux":
        return moyenne
    if regle == "taux_planche":
        return s_ * max(abs(moyenne), w) if moyenne * s_ > 0.0 else s_ * w
    return 0.0


def memoire_adaptee(rotations, fenetre: int, bloc: int = 1,
                    corrige_le_bruit: bool = False, enroulement: float | None = None) -> float:
    """La memoire que la rotation de la normale impose — un enonce, pas un ajustement.

    ⭐⭐⭐⭐ CE QUI SEPARE LES DEUX CAUSES EST UNE ECHELLE DE TEMPS, ET ELLE SE LIT SUR LE SIGNE.
    Un ecrasement fait tourner la normale LENTEMENT et TOUJOURS DANS LE MEME SENS — sa periode est
    d'un demi-tour. Un froissement la fait ALTERNER en quelques pas. La coherence des increments,
    `c = |somme| / somme des valeurs absolues`, vaut donc un sur une spirale nue comme sur un
    ecrasement, et tombe vers zero sur un froissement.

    ⭐⭐⭐ D'OU LA REGLE, SANS AUCUNE CONSTANTE AJUSTEE : `m = 1 - c`. Ce qui tourne franchement est
    lisible et le cap ne sert a rien ; ce qui alterne ne l'est pas et le cap doit tenir. Les deux
    extremes tombent sur les deux regimes que `143` a mesures.

    ⚠⚠ MA PREMIERE VERSION RETIRAIT LA MOYENNE DES INCREMENTS, ET C'ETAIT FAUX. L'intention etait
    d'oter l'enroulement, qui est le meme sur toute matiere ; mais une derive lente a, par
    construction, un residu de moyenne nulle, donc une coherence proche de zero — l'ecrasement
    recevait la memoire MAXIMALE, exactement l'inverse de ce que la regle veut dire. La batterie l'a
    dit avant la mesure. L'enroulement se GARDE : un cap ne doit pas combattre une rotation franche,
    et c'est precisement ce que la coherence des increments bruts exprime.

    ⚠⚠ LA BORNE EST DERIVEE, PAS CHOISIE : `m <= 1 - 1/fenetre`. On ne peut pas revendiquer une
    memoire plus longue que ce qu'on vient de mesurer, et une memoire de un figerait l'orientation —
    la batterie de `143` montre qu'un suiveur cesse alors de suivre.

    ⚠ Une rotation NULLE n'a rien a arbitrer, donc la memoire est nulle. C'est dit plutot que divise
    par zero.

    ⭐⭐ DEUX FACONS DE LIRE PLUS LOIN QUE LE BRUIT, ET UNE SEULE EST EXACTE. `144` mesure que la
    lecture cesse de separer les causes des que le bruit couvre la rotation. Le BLOC somme les
    increments par paquets de `k` : un bruit independant y croit comme la racine de `k` et une cause
    coherente comme `k`, donc le rapport s'ameliore — mais un froissement de periode `p` pas
    s'ANNULE dans un bloc de `p`, et il ne reste alors que l'enroulement, qui est coherent : la
    regle lirait « persistant » sur une matiere froissee. Le bloc est donc borne par la cause
    elle-meme. La CORRECTION, elle, retranche un plancher qui se calcule exactement.
    """
    f = int(fenetre)
    if f < 2:
        return 0.0
    r = np.asarray(rotations[-f:], dtype=np.float64)
    if r.size < 2:
        return 0.0
    if enroulement is not None:
        # ⭐⭐⭐⭐ LA REFERENCE ABSOLUE QU'UN SUIVEUR POSSEDE. Une coherence ne se lit que par
        # COMPARAISON, et un suiveur ne voit qu'une matiere : `145` montre qu'une spirale NUE
        # bruitee rend la meme lecture qu'une spirale a DEUX causes sans bruit, donc aucun seuil
        # absolu ne peut les separer. L'enroulement, lui, est un absolu que le suiveur CALCULE —
        # sa normale tourne de `avance / rayon` par pas, et il connait les deux. Ce qui excede
        # cette rotation-la n'est ni lisible ni voulu, et c'est exactement ce que le cap doit
        # supprimer.
        w = abs(float(enroulement))
        moyenne = float(np.abs(r).mean())
        if moyenne <= 0.0:
            return 0.0
        return float(min(1.0 - min(w / moyenne, 1.0), 1.0 - 1.0 / f))
    k = max(int(bloc), 1)
    if k > 1:
        # ⚠ Les blocs INCOMPLETS sont écartés : un bloc de trois pas parmi quatre porte moins de
        # bruit qu'un bloc plein, donc le mélanger aux autres fausserait exactement la quantité que
        # le bloc existe pour redresser.
        n_ = (r.size // k) * k
        if n_ < 2 * k:
            return 0.0
        r = r[-n_:].reshape(-1, k).sum(axis=1)
        if r.size < 2:
            return 0.0
    total = float(np.abs(r).sum())
    if total <= 0.0:
        return 0.0
    c = abs(float(r.sum())) / total
    if corrige_le_bruit:
        # ⭐⭐⭐ LE PLANCHER DU BRUIT EST EXACT ET SANS PARAMÈTRE. Pour `n` incréments indépendants de
        # moyenne nulle, `E|somme| = sigma.racine(2n/pi)` et `E[somme des |.|] = n.sigma.racine(2/pi)`,
        # donc la coherence attendue d'un bruit PUR vaut exactement `1/racine(n)`. Une coherence qui
        # vaut ce plancher ne dit rien ; la retrancher et renormaliser rend une lecture qui vaut zero
        # sur du bruit pur et un sur une rotation parfaite.
        #
        # ⚠ C'est le rapport des ESPERANCES, pas l'esperance du rapport — les deux se rejoignent
        # quand `n` grandit, et c'est dit plutot que tu.
        plancher = 1.0 / np.sqrt(float(r.size))
        c = max(0.0, (c - plancher) / max(1.0 - plancher, 1e-12))
    return float(min(1.0 - c, 1.0 - 1.0 / f))


def _tangente_du_tour(n) -> np.ndarray:
    t = np.cross(Z, np.asarray(n, dtype=np.float64))
    return t / max(float(np.linalg.norm(t)), 1e-12)


def suivre(vol, depart_vx, normale0, largeur_um: float, epaisseur_nominale_um: float,
           voxel_um: float, deux: bool, contrainte: bool, avance_um: float, axe_yx,
           tours: float = TOURS, pas_max: int = 4000, memoire_du_cap: float = 0.0,
           fenetre_du_cap: int = 0, bloc_du_cap: int = 1,
           corrige_le_bruit: bool = False, enroulement_du_cap: bool = False,
           cap_tournant: str = "", avance_sur_la_lecture: bool = False,
           fenetre_elargie: str = "", pose_sur_la_lecture: bool = False,
           pose_en_deux_temps: bool = False, en_croix: bool = False,
           rejeter: bool = False, derouler_exactement: bool = False,
           juger_le_deroulage: bool = False) -> dict:
    """Suivre une feuille autour de l'axe, et dire sur laquelle on finit.

    ⚠⚠ LE REFUS HALVE L'AVANCE PLUTOT QUE D'ABANDONNER, et il s'arrete quand l'avance tombe sous le
    VOXEL : en dessous, le lecteur ne peut plus exprimer le deplacement, donc insister serait
    tourner en rond en pretendant avancer. C'est une borne du lecteur, pas un reglage.

    ⚠ Le tour se compte sur l'angle CUMULE et signe, jamais sur l'angle absolu : un suiveur qui
    ferait un aller-retour reviendrait a son angle de depart en ayant parcouru deux fois le chemin,
    et un compteur d'angle absolu lui donnerait raison.

    ⭐⭐⭐ LE CAP AGIT SUR LA NORMALE, ET IL NE PEUT PAS AGIR AILLEURS. Dans le plan du tour, la
    direction perpendiculaire a la normale est UNIQUE au signe pres : une moyenne de deux tangentes
    reprojetee sur la normale courante rend exactement cette tangente, donc une memoire posee sur la
    tangente n'aurait aucun effet. Ce qu'un cap peut retenir est l'ORIENTATION — et c'est aussi ce
    que fait le rouleau physique dont vient l'idee : il a de l'inertie, il ne colle pas a chaque
    ondulation de la feuille.

    ⚠⚠ LA REGLE EST CELLE DE `marcher`, PAS UNE SECONDE. Moyenne exponentielle de la direction
    RETENUE, de taux `1 - memoire` ; a memoire nulle la matiere decide seule. Et le chemin du
    melange n'est pris QUE si la memoire est non nulle, ce qui garantit qu'une memoire nulle rend
    exactement le suiveur d'avant — jusqu'au bit, normalisation comprise.

    ⭐⭐⭐⭐ ET LA MEMOIRE PEUT SE LIRE PLUTOT QUE SE POSER. `fenetre_du_cap > 0` la fait DERIVER de
    ce que le suiveur vient de lire, par `memoire_adaptee` : la normale tourne pour deux raisons, et
    seul le RESIDU de sa rotation — une fois l'enroulement retire — distingue un ecrasement, qui
    derive lentement, d'un froissement, qui alterne. La regle est `m = 1 - c` ou `c` est la
    coherence de ce residu, et elle n'a aucune constante ajustee : residu coherent, la lecture est
    fiable et le cap ne sert a rien ; residu alternant, la lecture ne vaut rien et le cap doit tenir.
    Seule la LONGUEUR de la fenetre reste un parametre, et elle se balaie.

    ⚠ Les deux modes s'excluent : `memoire_du_cap` sert quand la fenetre est nulle, et `143` reste
    reproductible au bit.

    ⭐⭐⭐⭐ ET LA MARCHE PEUT ENFIN POSER L'INSTRUMENT QUE `153`, `154` ET `155` ONT REPARE.
    `en_croix` remplace la barre d'appuis par DEUX barres et un plan ajuste — la seule forme qui
    puisse exprimer une normale sortie du plan du tour, ce que `153` mesure sur la matiere du
    rouleau et nulle part ailleurs. `rejeter` ecarte les appuis tombes sur un AUTRE interstice,
    ce que `155` mesure comme le seul reglage qui RAPPROCHE la pose de l'echelle de sa matiere.
    Les deux etaient dans `poser` depuis `155` et aucune marche ne les avait payes.

    ⚠⚠⚠ ET LE DEROULAGE DE CETTE FONCTION SUPPOSE CE QU'ON VOUDRAIT LUI DEMANDER. `d - round(d)`
    choisit l'entier qui rend le pas le plus PETIT, donc il replie d'office tout pas franchissant
    plus d'une demi-feuille — et la question « un pas peut-il en franchir plus ? » recoit alors non
    par CONSTRUCTION. `derouler_exactement` publie A COTE le deroulage que l'ANGLE dicte, qui ne
    suppose rien, et le compte des pas ou les deux different. ⚠ Eteint, il ne change RIEN : meme
    calcul, meme sortie, jusqu'au bit, et `derive_en_feuilles` reste le nombre de toutes les
    tranches anterieures. `juger_le_deroulage` ajoute l'arbitre, qui coute cher et ne sert qu'a
    trancher.

    ⚠⚠ ET L'ATTENTE SE DIT AVANT LA MESURE. `149` mesure que la pince meurt d'ARRET et que c'est
    la POSE qui echoue — vingt et un refus de pose contre zero refus de contrainte — et `150`
    que la pose tombe a 633 ‰ a l'angle du cap. Une pose plus juste devrait donc faire ARRETER
    MOINS. « Elle arrete moins » n'est PAS « elle reussit plus », et les deux se comptent a part.
    """
    etat = poser(vol, depart_vx, normale0, largeur_um, epaisseur_nominale_um, voxel_um, deux,
                 en_croix=en_croix, rejeter=rejeter)
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
    # ⭐⭐⭐⭐ L'ANGLE QUE LA FIXTURE EMPLOIE DANS SA PHASE, et pas celui du compteur de tour. Sur une
    # section ECRASEE `cylindriques` rend un angle ELLIPTIQUE, et c'est lui qui porte la coupure de
    # la phase : reconstruire le deroulage avec l'angle CIRCULAIRE serait faux exactement sur la
    # matiere qui compte. Il est lu comme `phase` et `normale_locale`, donc ANALYTIQUEMENT et sans
    # aucune lecture de voxel, et seulement quand on le demande.
    angles_vrais = ([float(vol.cylindriques(
        np.asarray(etat["centre_vx"]).reshape(1, 3))[1][0])] if derouler_exactement else [])
    # ⚠⚠ ET LE CENTRE LUI-MEME, parce qu'un pas n'est PAS borne par l'avance : les machoires
    # RECENTRENT, et ce recentrage peut deplacer le centre bien plus loin que l'avance ne le fait.
    # Sans cette serie, « un pas peut-il franchir plus d'une demi-feuille ? » se raisonne au lieu de
    # se mesurer, et ce depot a paye trois fois qu'un raisonnement y perd contre un instrument.
    centres = ([np.asarray(etat["centre_vx"], dtype=np.float64).copy()]
               if derouler_exactement else [])
    # ⚠ Un repere PAR PAS, donc un de moins que de centres : c'est la direction le long de laquelle
    # le pas a ete fait, pas celle ou il arrive.
    reperes: list = []
    # ⭐⭐⭐⭐ LA COHERENCE INTERNE DE LA POSE, un nombre par pas. `161` conclut que les machoires
    # s'accrochent au MAUVAIS INTERSTICE a la pose ; si c'est vrai, leurs appuis doivent se
    # contredire ENTRE EUX au moment ou ca arrive. C'est une quantite que le marcheur possede
    # deja — l'etalement des profondeurs de ses propres appuis — et qui ne regarde pas du tout
    # ou le centre est alle. Deux axes independants, donc deux chances differentes de voir.
    etalements: list = []
    rotations: list[float] = []
    memoires: list[float] = []
    taux_lus: list[float] = []
    # ⚠⚠ DEUX DIAGNOSTICS QUE LE SUIVEUR NE VOIT JAMAIS. Ils lisent la VRAIE normale et la VRAIE
    # phase de la fixture — de quoi mesurer ce que le cap fait au marcheur, jamais de quoi le lui
    # dire. Et ni `normale_locale` ni `phase` ne comptent une lecture, donc `lectures` reste le
    # nombre que les tranches precedentes publient.
    inclinaisons: list[float] = []
    traversees: list[float] = []
    # ⭐⭐⭐ CE QUE LE SUIVEUR A DEJA VU DE LA MATIERE, ET RIEN D'AUTRE. Les appuis d'une machoire
    # tombent sur l'interstice a des distances differentes quand la surface ondule sous elle :
    # l'ECART entre ces distances est la seule mesure locale du deplacement que le froissement
    # impose, et elle est GRATUITE — la machoire les a deja lues.
    marges: list[float] = []
    marge = 0.0
    # ⚠⚠ LES APPUIS REJETES SE COMPTENT SUR LES POSES QUE LA MARCHE GARDE, jamais sur celles
    # qu'elle a essayees puis refusees : ce sont les seules dont la normale ait decide du pas
    # suivant. Et c'est un COMPTE, pas une comparaison de normales — `155` a paye qu'une
    # tolerance sous la reproductibilite de la decomposition compte du bruit comme un effet.
    rejetes_totaux = 0
    # ⭐⭐⭐ LA DERNIERE NORMALE QUE LA MATIERE A RENDUE, AVANT TOUT MELANGE. Au premier pas elle EST
    # la normale d'etat, puisque rien n'a encore ete melange — donc `pose_sur_la_lecture` ne change
    # rien tant que le cap ne s'est pas engage, et le temoin reste reproductible au bit.
    derniere_lecture = np.asarray(etat["normale"], dtype=np.float64)
    fin = "tour bouclé"
    while abs(cumul) < 2.0 * np.pi * float(tours) and pas < int(pas_max):
        a, pris = float(avance_um), None
        fenetre = (float(etat["epaisseur_um"]) if etat.get("epaisseur_um") is not None
                   else float(epaisseur_nominale_um))
        while a >= voxel_um:
            cible = np.asarray(etat["centre_vx"]) + tan * (a / voxel_um)
            # ⭐⭐⭐⭐ SUR QUOI LES MACHOIRES SE POSENT-ELLES ? Par defaut sur la normale MELANGEE,
            # donc sur ce que le cap a decide. Or `148` mesure que le cap incline cette normale de
            # plus de quarante degres sur la matiere du rouleau, et une pose le long d'une normale
            # si inclinee echoue une fois sur deux : la machoire cherche son interstice de travers.
            # `pose_sur_la_lecture` la fait chercher le long de la derniere normale que la MATIERE a
            # rendue, sans rien changer a la direction de marche. Le cap gouverne alors la marche et
            # rien d'autre — c'est la moitie que `148` n'avait pas essayee.
            neuf = poser(vol, cible,
                         derniere_lecture if pose_sur_la_lecture else etat["normale"],
                         largeur_um, fenetre, voxel_um, deux, marge_um=marge,
                         deux_temps=pose_en_deux_temps, en_croix=en_croix,
                         rejeter=rejeter)
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
        # ⚠ La rotation de la normale est mesuree AVANT le melange : le cap doit lire ce que la
        # matiere a rendu, pas ce que le cap precedent en a deja fait. Lire apres melange ferait
        # une boucle qui se confirme elle-meme.
        rejetes_totaux += int(pris.get("rejetes", 0))
        rotations.append(_ecart_angulaire(etat["normale"], pris["normale"]))
        # ⭐⭐⭐⭐ CE QUE LE PAS AURAIT TRAVERSE SI LES MACHOIRES NE SE RACCROCHAIENT PAS. Le cap
        # incline la normale, donc il incline aussi la TANGENTE le long de laquelle on avance :
        # une part du pas traverse la feuille au lieu de la longer. La mesure est exacte et sans
        # approximation de gradient — la phase du point vise moins celle du point courant, en
        # feuilles, deroulee comme partout ailleurs ici.
        depart_p = np.asarray(etat["centre_vx"], dtype=np.float64)
        vise = depart_p + np.asarray(tan, dtype=np.float64) * (a / voxel_um)
        dph = float(vol.phase(vise.reshape(1, 3))[0]) - float(vol.phase(depart_p.reshape(1, 3))[0])
        traversees.append(float(dph - np.round(dph)))
        inclinaisons.append(_ecart_deg(
            etat["normale"],
            np.asarray(vol.normale_locale(depart_p.reshape(1, 3))).reshape(3)))
        # ⚠ L'enroulement est calcule sur le rayon COURANT et l'avance REELLE du pas : les deux
        # sont a la main du suiveur, et un enroulement pose serait une constante de plus.
        rho = rayon_um(etat["centre_vx"])
        w_ = (a / rho) if rho > 0.0 else 0.0
        enr = w_ if enroulement_du_cap else None
        m_ = (memoire_adaptee(rotations, int(fenetre_du_cap), int(bloc_du_cap),
                              bool(corrige_le_bruit), enr) if int(fenetre_du_cap) > 0
              else float(memoire_du_cap))
        memoires.append(m_)
        # ⚠ Le taux n'est calcule que si une regle est demandee : sans elle `cible` EST la normale
        # precedente, donc le melange est celui d'avant jusqu'au bit, normalisation comprise.
        taux = (taux_du_cap(rotations, max(int(fenetre_du_cap), 2), w_,
                            (1.0 if cumul >= 0.0 else -1.0), cap_tournant)
                if cap_tournant else 0.0)
        taux_lus.append(taux)
        lecture = np.array(pris["normale"], dtype=np.float64)
        derniere_lecture = lecture
        if m_ > 0.0:
            cible = (_tourner(etat["normale"], taux) if taux != 0.0
                     else np.asarray(etat["normale"]))
            melange = ((1.0 - m_) * np.asarray(pris["normale"])
                       + m_ * cible)
            n_ = float(np.linalg.norm(melange))
            # ⚠ Un melange peut s'annuler si le cap est exactement oppose a la lecture. La lecture
            # GAGNE alors : inventer une orientation serait pire que d'oublier le cap.
            if n_ > 1e-9:
                pris["normale"] = melange / n_
        if fenetre_elargie:
            # ⭐⭐⭐ ELARGIR LA FENETRE DE CE QUE LE SUIVEUR A DEJA VU, ET LES DEUX FACONS DE LE
            # LIRE SONT CONTAMINEES CHACUNE A SA MANIERE — c'est ce que `149` mesure.
            #
            # « mesuree » : l'ecart a la demi-epaisseur MESUREE. ⚠⚠ Toute quantite que
            # l'elargissement enfle lui-meme est impropre a decider de cet elargissement :
            # l'epaisseur mesuree grandit des que la fenetre attrape un interstice trop loin, donc
            # l'ecart grandit, donc la fenetre s'elargit encore. RETROACTION POSITIVE.
            #
            # « nominale » : l'ecart a la demi-epaisseur NOMINALE. Le pas nominal ne peut pas
            # s'emballer, mais il n'est pas l'espacement LOCAL — sur une spirale ecrasee, sans
            # aucun froissement, l'ecart vaut deja une vingtaine de micrometres alors que rien
            # n'est deplace.
            #
            # ⚠ LE PLAFOND EST GEOMETRIQUE ET TOUJOURS NOMINAL : au-dela d'une demi-epaisseur, la
            # fenetre atteindrait l'interstice VOISIN, qui est a une epaisseur et demie. Et le
            # refus d'un minimum AU BORD, que `142` a paye, rend ce plafond exactement sur.
            demi_nominale = 0.5 * float(epaisseur_nominale_um)
            attendu = (0.5 * float(fenetre) if str(fenetre_elargie) == "mesuree"
                       else demi_nominale)
            e_ = [abs(float(pris[c]["ecart_um"]) - attendu)
                  for c in ("haut", "bas") if pris.get(c) is not None]
            marge = (min(max(e_), demi_nominale) if e_ else 0.0)
        marges.append(marge)
        chemin += a
        th_neuf = angle(pris["centre_vx"])
        d = th_neuf - th
        d = (d + np.pi) % (2.0 * np.pi) - np.pi
        cumul += d
        th = th_neuf
        # ⭐⭐⭐ LE CAP GOUVERNE-T-IL AUSSI LA DIRECTION DE MARCHE ? Par defaut oui : la tangente
        # sort de la normale MELANGEE. `avance_sur_la_lecture` la fait sortir de la normale que la
        # matiere vient de rendre, sans toucher a ce que les machoires emploient. C'est la seule
        # chose qui bouge, et elle separe « ce que le cap lisse » de « ou le marcheur va ».
        nouvelle_tan = _tangente_du_tour(lecture if avance_sur_la_lecture else pris["normale"])
        if float(nouvelle_tan @ tan) < 0.0:
            nouvelle_tan = -nouvelle_tan
        # ⭐⭐⭐⭐ DE QUOI CE PAS EST-IL FAIT ? Un pas a DEUX moities : l'AVANCE le long de la
        # tangente, bornee par `avance_um`, et le RECENTRAGE des machoires le long de la normale,
        # qui n'est borne par rien. `159` mesure un deplacement de centre de 219,79 µm la ou
        # l'avance en vaut 98,4 : la seconde moitie peut donc dominer, et c'est mesurable. Les deux
        # directions sont celles d'AVANT le pas — celles le long desquelles il a ete fait.
        if derouler_exactement:
            reperes.append((np.asarray(tan, dtype=np.float64).copy(),
                            np.asarray(etat["normale"], dtype=np.float64).copy()))
            # ⚠ L'etalement de la pose OU L'ON ARRIVE, jamais de celle d'ou l'on part : c'est
            # celle-la qu'un rejet refuserait. ⚠ Et une machoire absente ne compte pas comme un
            # etalement nul — elle ne contribue simplement pas.
            larges = [max(m["ecarts_um"]) - min(m["ecarts_um"])
                      for m in (pris.get("haut"), pris.get("bas"))
                      if m is not None and len(m.get("ecarts_um", ())) > 1]
            etalements.append(max(larges) if larges else None)
        tan, etat = nouvelle_tan, pris
        phases.append(float(vol.phase(np.asarray(etat["centre_vx"]).reshape(1, 3))[0]))
        if derouler_exactement:
            angles_vrais.append(float(vol.cylindriques(
                np.asarray(etat["centre_vx"]).reshape(1, 3))[1][0]))
            centres.append(np.asarray(etat["centre_vx"], dtype=np.float64).copy())
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
            # ⚠ La memoire REELLEMENT employee est publiee : une regle adaptative qui rendrait la
            # meme valeur partout serait un cap fixe deguise, et seul ce chiffre le dit.
            "memoire_mediane": (round(float(np.median(memoires)), 4) if memoires else None),
            # ⚠ Le taux REELLEMENT employe est publie pour la meme raison que la memoire : un cap
            # annonce tournant qui rendrait zero partout serait un cap statique deguise.
            "taux_median_rad": (round(float(np.median(taux_lus)), 6) if taux_lus else None),
            # ⚠ La marge REELLEMENT employee est publiee : une fenetre annoncee elargie qui rendrait
            # zero partout serait la fenetre d'avant, deguisee.
            "marge_mediane_um": (round(float(np.median(marges)), 3) if marges else None),
            # ⚠ En millidegres et en milli-feuilles ENTIERS : arrondis en degres ou en feuilles,
            # ces nombres tombent sous 1e-4 sur les matieres lisses et `json.dumps` les ecrit alors
            # en notation scientifique, introuvables dans leur propre record.
            "inclinaison_mediane_mdeg": (int(round(float(np.median(inclinaisons)) * 1000.0))
                                         if inclinaisons else None),
            "traversee_cumulee_mfeuilles": (int(round(float(np.sum(traversees)) * 1000.0))
                                            if traversees else None),
            "traversee_absolue_mfeuilles": (int(round(float(np.sum(np.abs(traversees))) * 1000.0))
                                            if traversees else None),
            "memoire_min": (round(float(np.min(memoires)), 4) if memoires else None),
            "memoire_max": (round(float(np.max(memoires)), 4) if memoires else None),
            "chemin_um": round(chemin, 1), "tour_boucle": bool(abs(cumul) >= 2.0 * np.pi * tours),
            "part_du_tour": round(float(abs(cumul) / (2.0 * np.pi)), 4), "fin": fin,
            "derive_en_feuilles": round(float(ph[-1] - ph[0]), 4),
            "derive_max_en_feuilles": round(float(np.max(np.abs(ph - ph[0]))), 4),
            "rayon_gagne_um": round(rayon_um(etat["centre_vx"]) - r0, 1),
            "epaisseur_um": (round(etat["epaisseur_um"], 1)
                             if etat.get("epaisseur_um") is not None else None),
            "saut_median_um": (round(float(np.median(ecarts)), 3) if ecarts else None),
            # ⚠ Le rejet REELLEMENT exerce est publie, pour la raison qui fait publier la
            # memoire et la marge : une regle annoncee qui n'ecarterait jamais rien serait la
            # marche d'avant, deguisee.
            "appuis_rejetes": int(rejetes_totaux),
            # ⚠ La serie DEROULEE, et jamais la brute : `VolumeFabriqueEnSpirale` saute d'une
            # feuille en franchissant `theta = ±π`, donc une serie non deroulee ferait voir un saut
            # de feuille la ou la matiere est identique. C'est le meme `ph` dont les bouts donnent
            # `derive_en_feuilles`, pas un second calcul.
            **(_le_deroulage_exact(phases, angles_vrais, centres, voxel_um,
                                   vol if juger_le_deroulage else None, reperes,
                                   epaisseur_nominale_um, etalements)
               if derouler_exactement else {}),
            "lectures": int(vol.lectures)}


def _le_chemin_du_pas(vol, a, b, echantillons: int) -> tuple[float, int]:
    """La phase franchie entre deux centres, en ECHANTILLONNANT le segment qui les joint.

    ⭐⭐⭐⭐ C'EST LA SEULE MESURE QUI NE SUPPOSE RIEN. Un deroulage a deux points doit choisir un
    entier ; un chemin echantillonne assez finement n'a aucun choix a faire, parce que chaque
    sous-pas change la phase de bien moins d'une demi-feuille et que son entier est alors sans
    ambiguite. Elle est ANALYTIQUE et ne coute AUCUNE lecture de voxel.

    ⚠⚠ Le segment droit n'est pas la trajectoire exacte du marcheur — il avance puis se recentre —
    mais aucun chemin court entre deux points voisins ne peut enrouler de `2π`, donc la difference
    de phase est la meme pour tous. C'est la multivalence en `theta` qui est en jeu, et elle ne se
    joue qu'a l'echelle du tour.
    """
    t = np.linspace(0.0, 1.0, int(echantillons) + 1).reshape(-1, 1)
    pts = np.asarray(a, dtype=np.float64) + t * (np.asarray(b, dtype=np.float64)
                                                 - np.asarray(a, dtype=np.float64))
    f = np.asarray(vol.phase(pts), dtype=np.float64).ravel()
    d = np.diff(f)
    # ⚠⚠ ET IL REND AUSSI COMBIEN DE SOUS-PAS ONT DU ETRE REPLIES. Un sous-pas replie est un
    # sous-pas que cet echantillonnage n'a PAS resolu : tant qu'il en reste, la somme suppose
    # encore quelque chose, et c'est exactement ce qu'un arbitre n'a pas le droit de faire.
    return float(np.sum(d - np.round(d))), int(np.count_nonzero(np.round(d)))


def _le_pas_mesure(vol, a, b) -> tuple[float, bool]:
    """La phase franchie par un pas, ECHANTILLONNEE jusqu'a ce que la reponse cesse de bouger.

    ⚠⚠⚠ ET LE CRITERE N'EST PAS « DEUX ECHANTILLONNAGES S'ACCORDENT », QUI EST FAUX. Paye ici :
    deux echantillonnages trop grossiers replient LE MEME sous-pas, rendent deux fois le meme
    nombre FAUX et se declarent d'accord. Un arbitre qui se verifie par son propre accord a le
    defaut exact de l'instrument qu'il juge. Le critere est donc qu'AUCUN sous-pas n'ait eu besoin
    d'etre replie : une somme dont aucun terme n'a ete choisi ne suppose rien.

    ⚠ Le plafond est DECLARE et son atteinte est RENDUE : un arbitre qui rendrait un nombre sans
    dire qu'il n'a pas conclu serait pire que pas d'arbitre. Un pas non tranche ne compte alors ni
    pour l'un ni pour l'autre.
    """
    n = 8
    somme, replis = _le_chemin_du_pas(vol, a, b, n)
    while replis and n < (1 << 24):
        n *= 2
        somme, replis = _le_chemin_du_pas(vol, a, b, n)
    return somme, not replis


def _les_deux_moities_du_pas(centres, reperes, voxel_um, saute,
                             epaisseur_nominale_um=None, etalements=None) -> dict:
    """La part du pas qui AVANCE et celle qui RECENTRE, sur les pas qui sautent et sur les autres.

    ⭐⭐⭐⭐ UN PAS A DEUX MOITIES ET UNE SEULE EST BORNEE. L'avance vaut au plus `avance_um` le long
    de la tangente ; le recentrage des machoires, lui, n'est borne par rien — il va ou l'interstice
    se trouve. Si les pas qui SAUTENT recentrent davantage, alors la machoire s'accroche au mauvais
    interstice A LA POSE, et `155` ne traite ce defaut qu'au niveau des APPUIS.

    ⚠⚠ LA COMPARAISON EST INTERNE A LA MARCHE. Deux medianes prises sur deux marches differentes ne
    se soustraient pas ; ici les deux populations viennent du MEME suiveur, sur la MEME matiere, et
    ce qui est publie est leur couple — jamais une difference entre marches.

    ⚠⚠ ET LES DEUX NOMBRES SONT DES PROJECTIONS, PAS « L'AVANCE » ET « LE RECENTRAGE ». Seule
    l'avance COMMANDEE est bornee par `avance_um` ; la projection du pas sur la tangente ne l'est
    pas, parce que le recentrage a sa propre composante le long de cette direction. Mesure a
    l'appui : une machoire seule rend 158 µm sur la tangente la ou l'avance en vaut 98,4. Les
    nommer « avance » aurait fait lire un depassement impossible.

    ⚠ Et une population vide se DIT : une marche ou rien ne saute n'a pas une projection normale
    nulle, elle n'en a pas.
    """
    if not reperes or len(reperes) != len(centres) - 1:
        return {}
    d = np.diff(np.asarray(centres, dtype=np.float64), axis=0) * float(voxel_um)
    t = np.asarray([r[0] for r in reperes], dtype=np.float64)
    n = np.asarray([r[1] for r in reperes], dtype=np.float64)
    avance = np.abs(np.einsum("ij,ij->i", d, t))
    recentrage = np.abs(np.einsum("ij,ij->i", d, n))
    out = {}
    # ⭐⭐⭐⭐ CE QUE LE MARCHEUR MESURE CONTRE CE QUE LA FIXTURE SAIT. Un marcheur ne peut pas lire
    # la phase : il ne connait que le deplacement de son centre. La question de `R4-P29` est donc
    # exactement celle-ci — ce deplacement, SEUL, suffit-il a voir qu'on vient de changer de
    # feuille ? Les quatre comptes ci-dessous sont une table de confusion, sans un seul seuil
    # choisi : « la pose a change d'interstice » veut dire « le centre a bouge de plus d'une DEMI
    # epaisseur le long de la normale », qui est l'enonce que le depot emploie deja pour dire que
    # deux appuis ne tiennent pas le meme interstice.
    # ⚠⚠ ET LA BORNE EST STRICTE, comme celle de la demi-feuille de `160` : un deplacement
    # d'exactement une demi-epaisseur n'a PAS change d'interstice.
    if epaisseur_nominale_um is not None:
        demi = 0.5 * float(epaisseur_nominale_um)
        # ⭐⭐⭐⭐ DEUX ENONCES EXACTS, ET LE DEPOT LES EMPLOIE DEJA TOUS LES DEUX.
        # L'ABSOLU est celui de `142`, `155` et `160` contre le NOMINAL : « plus d'une demi
        # epaisseur ». Le RELATIF est celui que `155` emploie pour un appui aberrant : « plus
        # d'une demi epaisseur de la MEDIANE de sa machoire » — ici, la mediane des pas de CETTE
        # marche. Aucun des deux n'est un seuil choisi ; ce sont deux façons de dire « le meme
        # interstice », l'une contre la geometrie nominale, l'autre contre ce que la marche fait
        # d'habitude.
        # ⚠⚠ ET LE RELATIF N'EST PAS CIRCULAIRE : il DETECTE, il ne corrige pas, donc la mediane
        # qu'il emploie n'est enflee par aucune de ses propres decisions. C'est precisement le
        # piege que `R4-P29` nomme, et c'est pourquoi il faut le dire ici plutot que l'esperer.
        # ⚠⚠ Les deux bornes sont STRICTES, comme la demi-feuille de `160`.
        regles = {"absolu": recentrage > demi}
        if recentrage.size:
            regles["relatif"] = recentrage > (float(np.median(recentrage)) + demi)
        # ⭐⭐⭐⭐ LE TROISIEME ENONCE, ET IL NE REGARDE PAS LE DEPLACEMENT DU TOUT : « les appuis
        # de cette pose ne tiennent pas le meme interstice », c'est-a-dire que l'etalement de
        # leurs profondeurs depasse une demi epaisseur. C'est l'enonce de `155`, applique a la
        # machoire ENTIERE au lieu d'un appui a la fois, et c'est la cohesion interne de la pose
        # plutot que son mouvement. ⚠ Une pose sans etalement lisible ne refuse RIEN : elle ne
        # peut pas se contredire, donc elle ne compte pas comme un refus.
        if etalements is not None and len(etalements) == saute.size:
            et = np.array([np.nan if e is None else float(e) for e in etalements],
                          dtype=np.float64)
            regles["etalement"] = np.where(np.isnan(et), False, et > demi)
            connus = ~np.isnan(et)
            out["poses_sans_etalement_lisible"] = int(np.count_nonzero(~connus))
            out["etalement_median_um"] = (round(float(np.median(et[connus])), 3)
                                          if np.any(connus) else None)
        out["pas_examines"] = int(saute.size)
        # ⭐⭐⭐⭐ OU CHAQUE CHOSE ARRIVE POUR LA PREMIERE FOIS. Un rappel dit COMBIEN une regle
        # voit ; il ne dit pas si elle voit A TEMPS. Or un refus ne peut qu'ARRETER la marche,
        # donc il n'allonge jamais rien : ce qu'il peut acheter, c'est de s'arreter AU bon
        # endroit, c'est-a-dire de dire ou la sortie cesse d'etre fiable. La comparaison des deux
        # premiers indices est donc la seule qui reponde a la question du prix.
        out["premier_saut"] = (int(np.argmax(saute)) if bool(np.any(saute)) else None)
        out["mediane_du_recentrage_um"] = (round(float(np.median(recentrage)), 3)
                                           if recentrage.size else None)
        for regle, change in regles.items():
            out.update({
                # ⚠⚠ UN PREMIER REFUS ABSENT N'EST PAS UN REFUS AU PAS ZERO : la regle ne s'est
                # jamais declenchee, et la marche est allee jusqu'au bout sans qu'elle dise rien.
                f"premier_refus_de_l_{regle}": (int(np.argmax(change))
                                                if bool(np.any(change)) else None),
                f"poses_refusees_par_l_{regle}": int(np.count_nonzero(change)),
                f"sauts_vus_par_l_{regle}": int(np.count_nonzero(saute & change)),
                f"sauts_manques_par_l_{regle}": int(np.count_nonzero(saute & ~change)),
                f"refus_a_tort_de_l_{regle}": int(np.count_nonzero(~saute & change))})
    for nom, masque in (("qui_sautent", saute), ("qui_ne_sautent_pas", ~saute)):
        if not np.any(masque):
            continue
        out[f"sur_la_tangente_um_des_pas_{nom}"] = round(float(np.median(avance[masque])), 3)
        out[f"sur_la_normale_um_des_pas_{nom}"] = round(float(np.median(recentrage[masque])), 3)
        # ⚠⚠ L'EFFECTIF SE PUBLIE A COTE DE SA MEDIANE — une mediane sans son compte ne dit pas
        # sur combien de pas elle porte. Et le nom est `effectif_...` et non `pas_qui_sautent`,
        # qui est DEJA la cle de `_le_deroulage_exact` : deux cles identiques dans un meme
        # dictionnaire, c'est la seconde qui gagne EN SILENCE, donc deux reponses a une question
        # dont une seule serait jamais lue.
        out[f"effectif_des_pas_{nom}"] = int(np.count_nonzero(masque))
    return out


def _le_deroulage_exact(phases, angles_vrais, centres=None, voxel_um=1.0, vol=None,
                        reperes=None, epaisseur_nominale_um=None, etalements=None) -> dict:
    """Le deroulage que l'ANGLE dicte, contre celui que la demi-feuille SUPPOSE.

    ⚠⚠⚠ LE DEROULAGE DE `suivre` SUPPOSE CE QU'ON VOUDRAIT LUI DEMANDER. `d - round(d)` choisit
    l'entier qui rend le pas le plus PETIT, donc il replie d'office tout pas qui franchirait plus
    d'une demi-feuille — et « un pas a-t-il franchi plus d'une demi-feuille ? » devient une question
    a laquelle sa propre reponse est non, par construction. Sa docstring le dit d'ailleurs comme une
    HYPOTHESE : « les pas sont petits devant une feuille ».

    ⭐⭐⭐⭐ ET L'HYPOTHESE N'EST PAS GARANTIE PAR LA GEOMETRIE. La phase vaut
    `(u - r0)/pas + froissement/pas - theta/2pi` : sa SEULE coupure est en `theta`, et le pas
    angulaire d'une marche vaut l'avance sur le rayon — de l'ordre du centieme de radian, donc
    parfaitement non ambigu. L'entier a ajouter se LIT donc sur l'angle, il ne se devine pas sur la
    phase. Les deux ne peuvent differer que la ou un pas franchit reellement plus d'une demi-feuille,
    et c'est exactement ce qu'on veut compter.

    ⚠ Rien n'est remplace : `derive_en_feuilles` reste le nombre de toutes les tranches anterieures,
    et l'exact est publie A COTE. Deux reponses a une question ne valent que si l'une des deux est
    DITE comme la mesure de l'autre.
    """
    if len(phases) < 2 or len(angles_vrais) != len(phases):
        return {}
    p_ = np.asarray(phases, dtype=np.float64)
    a_ = np.asarray(angles_vrais, dtype=np.float64)
    d_brut = np.diff(p_)
    dth = np.diff(a_)
    # ⚠ Le meme repliement que le compteur de tour, et pour la meme raison : un pas angulaire est
    # minuscule devant π, donc son entier est sans ambiguite.
    dth_u = (dth + np.pi) % (2.0 * np.pi) - np.pi
    n_angle = np.round((dth - dth_u) / (2.0 * np.pi))
    d_exact = d_brut + n_angle
    d_replie = d_brut - np.round(d_brut)
    # ⚠ Un pas est « replie a tort » quand les deux entiers different : c'est un ENONCE EXACT sur
    # des entiers, jamais une comparaison de flottants a une tolerance.
    desaccord = np.round(d_exact - d_replie).astype(np.int64)
    saut_um = (np.linalg.norm(np.diff(np.asarray(centres, dtype=np.float64), axis=0), axis=1)
               * float(voxel_um) if centres is not None and len(centres) == len(phases)
               else None)
    # ⭐⭐⭐⭐ ET LE JUGE : sur les pas ou les deux deroulages ne disent pas la meme chose, lequel
    # la MATIERE soutient-elle ? La question ne se raisonne pas — ce depot a paye trois fois qu'une
    # lecture du code y perde contre un instrument — donc elle se mesure, pas par pas, sur les seuls
    # pas litigieux.
    juge = {}
    if vol is not None and centres is not None and len(centres) == len(phases):
        litiges = np.nonzero(desaccord)[0]
        if litiges.size:
            paires = [_le_pas_mesure(vol, centres[i], centres[i + 1]) for i in litiges]
            mesures = np.array([m for m, _c in paires], dtype=np.float64)
            tranches = np.array([c for _m, c in paires], dtype=bool)
            # ⚠⚠ UN PAS QUE L'ARBITRE N'A PAS TRANCHE NE COMPTE NI POUR L'UN NI POUR L'AUTRE.
            pour_e = tranches & (np.abs(mesures - d_exact[litiges])
                                 < np.abs(mesures - d_replie[litiges]))
            pour_r = tranches & (np.abs(mesures - d_replie[litiges])
                                 < np.abs(mesures - d_exact[litiges]))
            juge = {
                "pas_litigieux": int(litiges.size),
                "litiges_non_tranches": int(np.count_nonzero(~tranches)),
                "litiges_que_le_chemin_donne_a_lexact": int(np.count_nonzero(pour_e)),
                "litiges_que_le_chemin_donne_au_replie": int(np.count_nonzero(pour_r)),
                "plus_grand_pas_mesure_en_feuilles": round(float(np.max(np.abs(mesures))), 6),
                # ⚠⚠ LES PAS QUE LE CHEMIN DONNE AU REPLIE SONT NOMMES, PAS SEULEMENT COMPTES. Un
                # refus sans son etat est un fait sans diagnostic attache, et c'est ce qui a permis
                # deux analyses fausses ailleurs dans ce depot. Ils sont rares par construction —
                # les lister ne peut pas grossir le record.
                "au_replie": [
                    {"pas": int(litiges[i]), "mesure": round(float(mesures[i]), 6),
                     # ⚠⚠ ET LA MEME MESURE A UN ECHANTILLONNAGE ECRASANT, parce qu'une
                     # convergence qui sort trop tot rend deux fois le meme nombre FAUX et se
                     # declare d'accord avec elle-meme. C'est le seul controle de l'arbitre.
                     "tranche": bool(tranches[i]),
                     "exact": round(float(d_exact[litiges[i]]), 6),
                     "replie": round(float(d_replie[litiges[i]]), 6)}
                    for i in range(litiges.size) if pour_r[i]]}
    # ⭐⭐⭐⭐ LA DECOMPOSITION QUE `158` DEMANDAIT ET QUE `159` A RENDUE POSSIBLE : un pas dont la
    # phase EXACTE franchit plus d'une DEMI-feuille a change de feuille. C'est le meme enonce que le
    # demi-pas de la contrainte et la demi-epaisseur du rejet, et il n'a aucun seuil — les feuilles
    # sont espacees d'une epaisseur, donc l'appariement au plus proche bascule exactement la.
    #
    # ⚠⚠ ET LA SOMME EST EXACTE, PAS APPROCHEE : `exacte = sauts + fluage`, terme a terme. Publier
    # l'une des deux parts sans l'autre laisserait croire a un reste negligeable.
    saute = np.abs(d_exact) > 0.5
    return {**juge,
            **(_les_deux_moities_du_pas(centres, reperes, voxel_um, saute,
                                        epaisseur_nominale_um, etalements)
               if centres is not None and reperes else {}),
            "pas_qui_sautent": int(np.count_nonzero(saute)),
            "derive_des_sauts_en_feuilles": round(float(np.sum(d_exact[saute])), 4),
            "derive_du_fluage_en_feuilles": round(float(np.sum(d_exact[~saute])), 4),
            # ⚠⚠ CE QU'UN PAS DEPLACE REELLEMENT LE CENTRE, en micrometres. C'est lui qui dit si
            # l'hypothese du deroulage est plausible, et il ne se raisonne pas : l'avance borne la
            # part TANGENTE du pas, jamais le recentrage des machoires.
            **({"plus_grand_deplacement_um": round(float(np.max(saut_um)), 2),
                "deplacement_median_um": round(float(np.median(saut_um)), 2)}
               if saut_um is not None and saut_um.size else {}),
            "derive_exacte_en_feuilles": round(float(np.sum(d_exact)), 4),
            "pas_replies_a_tort": int(np.count_nonzero(desaccord)),
            "feuilles_repliees_a_tort": round(float(np.sum(desaccord)), 4),
            # ⚠⚠ Le pas le plus grand que le deroulage EXACT rende : c'est lui qui dit si
            # l'hypothese « moins d'une demi-feuille » tient, et il ne peut pas etre lu sur la
            # serie repliee, qui le borne a 0,5 par construction.
            "plus_grand_pas_en_feuilles": round(float(np.max(np.abs(d_exact))), 6)}


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


def les_trois_bras(vol, depart_vx, normale0, largeur_um: float, epaisseur_nominale_um: float,
                   voxel_um: float, avance_um: float, axe_yx, tours: float = TOURS,
                   memoire_du_cap: float = 0.0, fenetre_du_cap: int = 0,
                   bloc_du_cap: int = 1, corrige_le_bruit: bool = False,
                   enroulement_du_cap: bool = False, cap_tournant: str = "",
                   avance_sur_la_lecture: bool = False,
                   fenetre_elargie: str = "", pose_sur_la_lecture: bool = False,
                   pose_en_deux_temps: bool = False, en_croix: bool = False,
                   rejeter: bool = False) -> dict:
    """Les trois bras sur le MEME depart — c'est ce qui rend la comparaison lisible."""
    out = {}
    for nom, deux, contrainte in (("une machoire", False, False),
                                  ("deux machoires libres", True, False),
                                  ("la pince", True, True)):
        vol.lectures = 0
        out[nom] = suivre(vol, depart_vx, normale0, largeur_um, epaisseur_nominale_um, voxel_um,
                          deux, contrainte, avance_um, axe_yx, tours,
                          memoire_du_cap=memoire_du_cap, fenetre_du_cap=fenetre_du_cap,
                          bloc_du_cap=bloc_du_cap, corrige_le_bruit=corrige_le_bruit,
                          enroulement_du_cap=enroulement_du_cap, cap_tournant=cap_tournant,
                          avance_sur_la_lecture=avance_sur_la_lecture,
                          fenetre_elargie=fenetre_elargie,
                          pose_sur_la_lecture=pose_sur_la_lecture,
                          pose_en_deux_temps=pose_en_deux_temps, en_croix=en_croix,
                          rejeter=rejeter)
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
             longueur_donde_um: float = LONGUEUR_DONDE_UM, memoire_du_cap: float = 0.0,
             fenetre_du_cap: int = 0, bloc_du_cap: int = 1,
             corrige_le_bruit: bool = False, enroulement_du_cap: bool = False,
             cap_tournant: str = "", avance_sur_la_lecture: bool = False,
             fenetre_elargie: str = "", pose_sur_la_lecture: bool = False,
             pose_en_deux_temps: bool = False, en_croix: bool = False,
             rejeter: bool = False) -> dict:
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
                               vol.centre_yx_vx, tours, memoire_du_cap=memoire_du_cap,
                               fenetre_du_cap=fenetre_du_cap, bloc_du_cap=bloc_du_cap,
                               corrige_le_bruit=corrige_le_bruit,
                               enroulement_du_cap=enroulement_du_cap,
                               cap_tournant=cap_tournant,
                               avance_sur_la_lecture=avance_sur_la_lecture,
                               fenetre_elargie=fenetre_elargie,
                               pose_sur_la_lecture=pose_sur_la_lecture,
                               pose_en_deux_temps=pose_en_deux_temps,
                               en_croix=en_croix, rejeter=rejeter)
        for b, x in trois.items():
            par_bras[b].append({"depart_deg": round(360.0 * k / int(departs), 1), **x})
    bloc = {"ecrasement": float(ecr), "amplitude_um": float(amp), "bruit": float(bruit),
            "largeur_en_pas": float(largeur_en_pas), "largeur_um": round(largeur_um, 1),
            "avance_um": round(avance_um, 1), "nom": _nom(ecr, amp), "departs": int(departs),
            "memoire_du_cap": float(memoire_du_cap),
            "fenetre_du_cap": int(fenetre_du_cap), "bloc_du_cap": int(bloc_du_cap),
            "corrige_le_bruit": bool(corrige_le_bruit),
            "enroulement_du_cap": bool(enroulement_du_cap),
            "cap_tournant": str(cap_tournant),
            "avance_sur_la_lecture": bool(avance_sur_la_lecture),
            "fenetre_elargie": str(fenetre_elargie),
            "pose_sur_la_lecture": bool(pose_sur_la_lecture),
            "en_croix": bool(en_croix), "rejeter": bool(rejeter), "bras": {}}
    for b in BRAS:
        bloc["bras"][b] = {"suivis": par_bras[b], **_resumer_un_bras(par_bras[b], int(departs))}
    return bloc


def une_reussite(x: dict) -> bool:
    """Un transfert reussi, et c'est un enonce JOINT — dit UNE fois, pour tous ses lecteurs.

    ⭐⭐⭐ Boucler le tour et revenir sur la meme feuille sont la MEME reussite. `143` l'a paye : sa
    barre a ete franchie par une marche qui bouclait son tour avec une feuille juste sur douze.

    ⚠ Ce predicat existe pour qu'un comptage APPARIE — le meme depart sous deux regles — n'ait pas
    a le reecrire. Deux ecritures d'une meme question divergent, et celle-ci decide tout.
    """
    return bool(x.get("decidable") and x.get("tour_boucle")
                and abs(float(x.get("derive_en_feuilles", 1e9))) < 0.5)


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
        # ⭐⭐⭐ LA REUSSITE D'UN TRANSFERT, ET ELLE EST JOINTE. Boucler le tour et revenir sur la
        # meme feuille sont la MEME reussite, et les compter separement laisse passer un suiveur qui
        # fait le tour en revenant sur une autre feuille. `143` l'a paye : sa barre a ete franchie
        # par une marche qui bouclait son tour avec une feuille juste sur douze. Un compte JOINT est
        # aussi la garde anti-tautologie que le couple assurait : un bras qui refuse tout n'a aucune
        # reussite, puisqu'il ne boucle rien.
        "reussites": int(sum(1 for x in bons if une_reussite(x))),
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
        # ⚠ Un compte est ENTIER, et il se somme plutot que de se mediane : la population est
        # bimodale — la plupart des marches n'ecartent rien — donc une mediane y vaut zero et
        # ne dirait rien. C'est le motif que `155` a paye sur les poses.
        "appuis_rejetes": int(sum(int(x.get("appuis_rejetes", 0)) for x in bons)),
        "marches_qui_rejettent": int(sum(1 for x in bons
                                        if int(x.get("appuis_rejetes", 0)) > 0)),
        # ⚠ « Elle arrete moins » est un enonce SEPARE de « elle reussit plus », donc il se
        # compte a part : `149` mesure que la pince meurt d'arret, pas de derive.
        "arrets": int(sum(1 for x in bons
                         if x.get("fin") == "la pince ne peut plus avancer")),
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

    # ---- ⭐⭐⭐⭐ LA POSE EN DEUX TEMPS (`152`)
    # ⚠⚠ Le premier controle est un THEOREME, pas une mesure : le second temps n'a lieu que si le
    # premier a rendu quelque chose. Une pose en deux temps ne peut donc jamais reussir la ou une
    # pose simple echoue, et l'ecrire ici evite d'aller le « mesurer » sur une grille.
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee as _VFF)
    froissee = _matiere(_VFF, 0.2782, 100.0, 0.0, LONGUEUR_DONDE_UM, RAYON_MM)
    d_f, n_f = un_depart(froissee, 0.0, RAYON_MM, voxel_um, pas_um)
    tordue = _tourner(n_f, np.radians(80.0))
    v("⭐⭐⭐ une pose en deux temps ne peut pas réussir là où une pose simple échoue",
      not (poser(froissee, d_f, tordue, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, True)
           is None
           and poser(froissee, d_f, tordue, LARGEUR_DE_REFERENCE * pas_um, pas_um, voxel_um, True,
                     deux_temps=True) is not None),
      "le second temps est conditionné par le premier, donc c'est une conjonction")

    # ⭐⭐ Le temoin qui MORD : sur une matiere lisse et une normale DEJA juste, le premier temps
    # rend deja la vraie normale, donc le second n'a rien a corriger et rend le MEME etat au bit.
    # Une implementation qui perturberait la pose sans raison echouerait ici.
    un_t = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True)
    deux_t = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True, deux_temps=True)
    v("⭐⭐ sur une normale déjà juste, le second temps ne déplace RIEN",
      un_t is not None and deux_t is not None
      and _ecart_deg(un_t["normale"], deux_t["normale"]) < 1e-6,
      f"{_ecart_deg(un_t['normale'], deux_t['normale']):.2e}°" if un_t and deux_t else "aucune pose")

    # ⭐⭐⭐ ... et sur une normale PENCHEE il deplace quelque chose, sinon le mecanisme est vide.
    penchee = _tourner(n0, np.radians(30.0))
    p1 = poser(nue, depart, penchee, 0.25 * pas_um, pas_um, voxel_um, True)
    p2 = poser(nue, depart, penchee, 0.25 * pas_um, pas_um, voxel_um, True, deux_temps=True)
    v("⭐⭐⭐ ... alors que sur une normale PENCHÉE il la redresse encore",
      p1 is not None and p2 is not None
      and _ecart_deg(p2["normale"], n0) < _ecart_deg(p1["normale"], n0),
      (f"{_ecart_deg(p1['normale'], n0):.4f}° → {_ecart_deg(p2['normale'], n0):.4f}°"
       if p1 and p2 else "aucune pose"))

    # ⚠⚠⚠ ET LA SONDE QUI MORD SUR LE CENTRE. Sur une spirale nue au depart recale, le centre
    # trouve EST le depart, donc « repartir du centre trouve » n'y change rien : une sonde posee
    # la ne peut pas echouer. Elle se pose donc sur la matiere froissee, ou le centre mesure bouge
    # reellement, et elle verifie que le second temps est celui du MEME centre — apres avoir
    # verifie que les deux choix different, sans quoi elle ne prouverait toujours rien.
    d_w, n_w = un_depart(froissee, 0.7, RAYON_MM, voxel_um, pas_um)
    graine_w = _tourner(n_w, np.radians(20.0))
    lg_w = LARGEUR_DE_REFERENCE * pas_um
    en_deux = poser(froissee, d_w, graine_w, lg_w, pas_um, voxel_um, True, deux_temps=True)
    t1 = poser(froissee, d_w, graine_w, lg_w, pas_um, voxel_um, True)
    meme_centre = (poser(froissee, d_w, t1["normale"], lg_w, pas_um, voxel_um, True)
                   if t1 is not None else None)
    centre_bouge = (poser(froissee, t1["centre_vx"], t1["normale"], lg_w, pas_um, voxel_um, True)
                    if t1 is not None else None)
    ecart_des_deux = (float(np.linalg.norm(np.asarray(meme_centre["centre_vx"])
                                           - np.asarray(centre_bouge["centre_vx"]))) * voxel_um
                      if meme_centre is not None and centre_bouge is not None else 0.0)
    v("⭐⭐ ... et les deux choix de centre donnent VRAIMENT deux poses différentes",
      ecart_des_deux > 1e-6, f"{ecart_des_deux:.4f} µm — sinon la sonde suivante ne prouve rien")
    v("⭐⭐⭐⭐ le second temps repart du MÊME centre, pas de celui que le premier a trouvé",
      en_deux is not None and meme_centre is not None
      and float(np.linalg.norm(np.asarray(en_deux["centre_vx"])
                               - np.asarray(meme_centre["centre_vx"]))) < 1e-9,
      "sinon deux choses changeraient à la fois, la direction ET le point")

    # ⚠ Le prix est publiable : deux temps lisent deux fois.
    nue.lectures = 0
    poser(nue, depart, penchee, 0.25 * pas_um, pas_um, voxel_um, True)
    l1 = int(nue.lectures)
    nue.lectures = 0
    poser(nue, depart, penchee, 0.25 * pas_um, pas_um, voxel_um, True, deux_temps=True)
    l2 = int(nue.lectures)
    v("⚠ et il coûte exactement deux poses, jamais une de plus",
      l1 > 0 and l2 == 2 * l1, f"{l1} puis {l2} lectures")

    # ---- ⭐⭐⭐⭐ LA MACHOIRE EN CROIX (`153`), et son contrôle structurel
    # ⚠⚠ L'enonce n'est pas « la croix est meilleure » mais « la croix peut sortir du plan du tour
    # et le segment ne le peut pas ». C'est une propriete de l'instrument, pas un gain, et elle se
    # verifie sur la SORTIE : la composante axiale de la normale rendue.
    d_c, n_c = un_depart(froissee, 1.3, RAYON_MM, voxel_um, pas_um)
    axial_vrai = abs(float(np.asarray(n_c)[0] / np.linalg.norm(n_c)))
    v("⭐⭐⭐ sur une matière froissée, la VRAIE normale sort du plan du tour",
      axial_vrai > 1e-3, f"|n·z| = {axial_vrai:.6f} — sans ça, il n'y a rien à récupérer")
    seg = une_machoire(froissee, d_c, n_c, +1.0, lg_w, pas_um, voxel_um)
    cro = une_machoire_en_croix(froissee, d_c, n_c, +1.0, lg_w, pas_um, voxel_um)
    v("⭐⭐⭐⭐ une mâchoire en SEGMENT n'en rend jamais rien, par construction",
      seg is not None and abs(float(seg["normale"][0])) < 1e-12,
      f"|n·z| rendu = {abs(float(seg['normale'][0])):.2e}" if seg else "aucune pose")
    v("⭐⭐⭐⭐ ... et la CROIX en rend quelque chose",
      cro is not None and abs(float(cro["normale"][0])) > 1e-3,
      f"|n·z| rendu = {abs(float(cro['normale'][0])):.6f}" if cro else "aucune pose")

    # ⚠⚠ ET LE CONTROLE QUI EMPECHE L'ENONCE D'ETRE VRAI POUR RIEN : sur une matiere LISSE, la
    # vraie normale ne sort PAS du plan, donc la croix ne doit rien inventer. Une croix qui
    # rendrait une composante axiale sur une spirale nue mesurerait son propre bruit.
    n_plate = une_machoire_en_croix(nue, depart, n0, +1.0, 0.25 * pas_um, pas_um, voxel_um)
    v("⚠⚠ sur une matière LISSE la croix n'invente aucune composante axiale",
      n_plate is not None and abs(float(n_plate["normale"][0])) < 1e-6,
      f"|n·z| = {abs(float(n_plate['normale'][0])):.2e}" if n_plate else "aucune pose")
    v("... et elle y rend la même normale que le segment",
      n_plate is not None
      and _ecart_deg(n_plate["normale"],
                     une_machoire(nue, depart, n0, +1.0, 0.25 * pas_um, pas_um,
                                  voxel_um)["normale"]) < 1e-6,
      "rien à corriger, donc rien de corrigé")

    # ⚠ Le prix : deux barres, donc deux fois les appuis.
    froissee.lectures = 0
    une_machoire(froissee, d_c, n_c, +1.0, lg_w, pas_um, voxel_um)
    ls = int(froissee.lectures)
    froissee.lectures = 0
    une_machoire_en_croix(froissee, d_c, n_c, +1.0, lg_w, pas_um, voxel_um)
    lc = int(froissee.lectures)
    v("⚠ la croix coûte exactement deux barres d'appuis", ls > 0 and lc == 2 * ls,
      f"{ls} puis {lc} lectures")

    # ---- ⭐⭐⭐⭐ LE REJET DES APPUIS ABERRANTS (`155`)
    # ⭐⭐⭐ LA SONDE QUI COMPTE : la MEDIANE et la MOYENNE ne rendent pas le meme verdict, et c'est
    # pourquoi la regle est ecrite avec la mediane. Sur trois appuis dont un est a 100 µm, la
    # mediane vaut 0 et l'ecarte ; la moyenne vaut 33,3 et le GARDE — l'aberrant aurait emporte la
    # reference qui devait le juger.
    ep = pas_um
    ecarts_faux = [0.0, 0.0, 100.0]
    garde = _garder_les_appuis(ecarts_faux, ep, 2)
    par_la_moyenne = np.abs(np.asarray(ecarts_faux)
                            - float(np.mean(ecarts_faux))) < 0.5 * ep
    v("⭐⭐⭐⭐ la MÉDIANE écarte un appui que la MOYENNE aurait gardé",
      garde is not None and int(garde.sum()) == 2 and int(par_la_moyenne.sum()) == 3,
      f"médiane garde {int(garde.sum())}/3, moyenne en garderait {int(par_la_moyenne.sum())}/3")
    v("⭐⭐ l'énoncé bascule EXACTEMENT à la demi-épaisseur, jamais à un seuil choisi",
      int(_garder_les_appuis([0.0, 0.0, 0.5 * ep - 0.01], ep, 2).sum()) == 3
      and int(_garder_les_appuis([0.0, 0.0, 0.5 * ep + 0.01], ep, 2).sum()) == 2,
      f"à {0.5 * ep} µm près, parce que les interstices sont espacés d'une épaisseur")
    v("⚠ et il refuse plutôt que d'ajuster sur ce qui reste quand il ne reste pas de quoi",
      _garder_les_appuis([0.0, 200.0, 400.0], ep, 2) is None,
      "trois appuis sur trois interstices différents ne portent aucune forme")

    # ⭐⭐ Sur une matiere LISSE il n'y a rien a rejeter, donc le rejet ne doit RIEN deplacer.
    sans_rejet = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True)
    avec_rejet = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True, rejeter=True)
    v("⭐⭐ sur une matière lisse le rejet ne déplace RIEN",
      sans_rejet is not None and avec_rejet is not None
      and _ecart_deg(sans_rejet["normale"], avec_rejet["normale"]) < 1e-9,
      "aucun appui n'y est à plus d'une demi-épaisseur de ses voisins")

    # ⭐⭐⭐ ... et sur la matiere du rouleau il deplace quelque chose, sinon la regle est vide.
    # ⚠ Le depart est cherche : la plupart des poses n'ont AUCUN aberrant, donc en prendre un au
    # hasard ferait une sonde qui passe pour la mauvaise raison — elle ne prouverait que le cas ou
    # il n'y a rien a faire.
    bouge = False
    for k in range(40):
        d_r, n_r = un_depart(froissee, 2.0 * np.pi * k / 40.0, RAYON_MM, voxel_um, pas_um)
        a_ = poser(froissee, d_r, n_r, lg_w, pas_um, voxel_um, True)
        b_ = poser(froissee, d_r, n_r, lg_w, pas_um, voxel_um, True, rejeter=True)
        if a_ is not None and b_ is not None \
                and _ecart_deg(a_["normale"], b_["normale"]) > 1e-6:
            bouge = True
            break
    v("⭐⭐⭐ ... et sur la matière du rouleau il déplace la normale sur au moins un départ",
      bouge, "sinon la règle serait écrite et sans effet")

    # ⚠⚠⚠ ET LE COMPTE D'APPUIS REJETES REMPLACE TOUTE TOLERANCE. Comparer deux normales a 1e-9
    # comptait du BRUIT NUMERIQUE : sur un masque tout-vrai, la decomposition d'un tableau RECOPIE
    # ne rend pas les memes derniers bits que celle de l'original, et « cette pose a ete touchee »
    # devenait vrai sans qu'aucun appui n'ait ete rejete. `rejetes` le dit exactement.
    sans_r = poser(nue, depart, n0, 0.25 * pas_um, pas_um, voxel_um, True, rejeter=True)
    v("⭐⭐⭐⭐ une pose publie COMBIEN d'appuis elle a rejetés, au lieu d'une tolérance",
      sans_r is not None and sans_r.get("rejetes") == 0,
      "sur une matière lisse il n'y a rien à rejeter, donc le compte est zéro et pas « presque »")
    combien = 0
    for k in range(40):
        d_x, n_x = un_depart(froissee, 2.0 * np.pi * k / 40.0, RAYON_MM, voxel_um, pas_um)
        e_x = poser(froissee, d_x, n_x, lg_w, pas_um, voxel_um, True, rejeter=True)
        if e_x is not None:
            combien += int(e_x.get("rejetes", 0))
    v("⭐⭐⭐ ... et sur la matière du rouleau ce compte n'est pas nul", combien > 0,
      f"{combien} appuis rejetés sur quarante poses")

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

    # ---- ⭐⭐ la mémoire qui se LIT plutôt que de se poser
    v("l'écart angulaire est signé et antisymétrique",
      abs(_ecart_angulaire([0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
          + _ecart_angulaire([0.0, 0.0, 1.0], [0.0, 1.0, 0.0])) < 1e-12)
    v("... et il vaut le quart de tour entre deux axes du plan",
      abs(abs(_ecart_angulaire([0.0, 1.0, 0.0], [0.0, 0.0, 1.0])) - np.pi / 2.0) < 1e-12)
    v("⭐⭐ une rotation FRANCHE ne demande aucune mémoire",
      abs(memoire_adaptee([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], 8)) < 1e-9,
      "tous les incréments du même signe : c = 1, donc m = 0")
    v("... y compris une rotation constante, qui est l'enroulement",
      abs(memoire_adaptee([0.37] * 12, 8)) < 1e-12,
      "sinon le cap combattrait la courbure que le suiveur doit suivre")
    alterne = [0.2, -0.2] * 6
    v("⭐⭐ une rotation qui ALTERNE demande la mémoire maximale que la fenêtre autorise",
      abs(memoire_adaptee(alterne, 8) - (1.0 - 1.0 / 8)) < 1e-9,
      f"{memoire_adaptee(alterne, 8)} pour une borne de {1.0 - 1.0 / 8}")
    v("⭐⭐ ... et une alternance POSÉE SUR une dérive demande moins qu'une alternance pure",
      memoire_adaptee([0.5 + 0.2 * (-1) ** k for k in range(8)], 8)
      < memoire_adaptee(alterne, 8),
      "c'est ce qui fait que les deux causes mélangées tombent entre les deux")
    v("⚠ la borne est DÉRIVÉE de la fenêtre, donc elle se resserre quand la fenêtre raccourcit",
      memoire_adaptee(alterne, 4) < memoire_adaptee(alterne, 16),
      f"{memoire_adaptee(alterne, 4)} contre {memoire_adaptee(alterne, 16)}")
    v("une fenêtre trop courte pour une rotation ne rend rien",
      memoire_adaptee([0.1, 0.2], 1) == 0.0 and memoire_adaptee([0.1], 8) == 0.0)
    v("une rotation nulle ne rend rien non plus, plutôt qu'une division par zéro",
      memoire_adaptee([0.0] * 8, 8) == 0.0)
    # ---- ⭐⭐ le bloc et la correction du plancher de bruit
    v("un bloc de un rend exactement la règle d'avant",
      memoire_adaptee(alterne, 8, bloc=1) == memoire_adaptee(alterne, 8))
    v("⭐⭐ un bloc qui ATTEINT la période d'une alternance la fait lire COHÉRENTE",
      memoire_adaptee([0.3, -0.3] * 8, 16, bloc=2) < 0.5 * memoire_adaptee([0.3, -0.3] * 8, 16),
      "le bloc annule la cause qu'il devait révéler, et c'est ce qui le borne")
    v("... alors qu'un bloc plus COURT que la période la garde",
      memoire_adaptee([0.3, 0.3, -0.3, -0.3] * 4, 16, bloc=2)
      > 0.5 * memoire_adaptee([0.3, 0.3, -0.3, -0.3] * 4, 16),
      "période de quatre pas, bloc de deux : l'alternance survit")
    v("un bloc trop grand pour la fenêtre ne rend rien plutôt qu'un bloc unique",
      memoire_adaptee([0.1] * 8, 8, bloc=8) == 0.0)
    # ⚠⚠ Le plancher est EXACT : pour n incréments indépendants la cohérence attendue vaut 1/√n.
    tir = np.random.default_rng(17)
    planchers = []
    for _ in range(200):
        x = tir.normal(size=64)
        planchers.append(abs(float(x.sum())) / float(np.abs(x).sum()))
    v("⭐⭐ la cohérence d'un bruit pur vaut bien 1/√n, ce que la correction retranche",
      abs(float(np.mean(planchers)) - 1.0 / np.sqrt(64)) < 0.02,
      f"mesuré {float(np.mean(planchers)):.4f} pour un plancher de {1.0 / np.sqrt(64):.4f}")
    bruit_pur = list(tir.normal(size=32))
    v("⭐⭐ corrigée, une suite de bruit PUR demande la mémoire maximale",
      memoire_adaptee(bruit_pur, 32, corrige_le_bruit=True)
      > memoire_adaptee(bruit_pur, 32),
      f"{memoire_adaptee(bruit_pur, 32, corrige_le_bruit=True):.4f} contre "
      f"{memoire_adaptee(bruit_pur, 32):.4f}")
    v("... et une rotation franche n'en demande toujours aucune",
      memoire_adaptee([0.37] * 32, 32, corrige_le_bruit=True) == 0.0,
      "la correction ne déplace pas ce qui est déjà parfaitement cohérent")
    v("la correction ne rend jamais une mémoire négative ni au-delà de sa borne",
      all(0.0 <= memoire_adaptee(list(np.random.default_rng(k).normal(size=32)), 32,
                                 corrige_le_bruit=True) <= 1.0 - 1.0 / 32 for k in range(5)))

    # ---- ⭐⭐ la règle ABSOLUE : ce qui excède l'enroulement
    w = 0.02
    v("⭐⭐ une rotation qui vaut EXACTEMENT l'enroulement ne demande aucune mémoire",
      memoire_adaptee([w] * 16, 16, enroulement=w) == 0.0,
      "le suiveur tourne comme il doit, il n'y a rien à supprimer")
    v("⭐⭐ ... une rotation DEUX fois plus grande en demande la moitié",
      abs(memoire_adaptee([2 * w] * 16, 16, enroulement=w) - 0.5) < 1e-9,
      f"{memoire_adaptee([2 * w] * 16, 16, enroulement=w)}")
    v("... et une rotation PLUS PETITE que l'enroulement n'en demande aucune",
      memoire_adaptee([0.5 * w] * 16, 16, enroulement=w) == 0.0,
      "la part de l'enroulement ne peut pas dépasser un")
    v("⭐ une alternance de même amplitude que l'enroulement n'en demande aucune non plus",
      memoire_adaptee([w, -w] * 8, 16, enroulement=w) == 0.0,
      "cette règle lit une AMPLITUDE, pas un signe — c'est ce qui la distingue de la cohérence")
    v("une rotation nulle ne rend rien plutôt qu'une division par zéro",
      memoire_adaptee([0.0] * 16, 16, enroulement=w) == 0.0)
    v("la règle absolue respecte la borne de la fenêtre",
      memoire_adaptee([1000.0 * w] * 8, 8, enroulement=w) == 1.0 - 1.0 / 8)

    v("la mémoire lue reste dans [0, 1[",
      all(0.0 <= memoire_adaptee(list(np.random.default_rng(k).normal(size=20)), 8) < 1.0
          for k in range(5)))

    # ---- ⭐⭐⭐⭐ LE CAP QUI TOURNE, et la sonde de SIGNE qui mord avant tout le reste
    n0_ = np.array([0.3, 0.8, -0.5])
    n0_ = n0_ / np.linalg.norm(n0_)
    v("⭐⭐ tourner puis mesurer rend EXACTEMENT l'angle demandé, signe compris",
      all(abs(_ecart_angulaire(n0_, _tourner(n0_, phi)) - phi) < 1e-12
          for phi in (0.01, -0.01, 0.4, -0.4, 1.2, -1.2)),
      "une convention inversée ferait tourner le cap à contresens, ce qui ressemble à « le cap "
      "tournant marche moins bien » et non à une faute de signe")
    v("tourner ne change ni la longueur de la normale ni sa composante d'axe",
      abs(np.linalg.norm(_tourner(n0_, 0.7)) - np.linalg.norm(n0_)) < 1e-12
      and abs(_tourner(n0_, 0.7)[0] - n0_[0]) < 1e-12)
    v("tourner de zéro ne touche rien", np.array_equal(_tourner(n0_, 0.0), n0_))

    v("⭐⭐ sur une spirale NUE les trois règles de taux tombent sur l'enroulement",
      all(abs(taux_du_cap([w] * 16, 16, w, +1.0, r_) - w) < 1e-12
          for r_ in ("enroulement", "taux", "taux_planche")),
      "la moyenne des incréments VAUT l'enroulement quand rien d'autre ne tourne")
    v("⭐⭐ sur un ÉCRASEMENT, le taux lu suit la rotation en plus, l'enroulement seul l'ignore",
      abs(taux_du_cap([3.0 * w] * 16, 16, w, +1.0, "taux") - 3.0 * w) < 1e-12
      and abs(taux_du_cap([3.0 * w] * 16, 16, w, +1.0, "enroulement") - w) < 1e-12,
      "c'est exactement la forme que `146` mesure comme devant être SUIVIE")
    v("⭐⭐⭐ sur un FROISSEMENT, le taux lu retombe sur l'enroulement TOUT SEUL",
      abs(taux_du_cap([w + 20.0 * w, w - 20.0 * w] * 8, 16, w, +1.0, "taux") - w) < 1e-12,
      "un cap qui tourne au taux moyen ne suit donc pas ce qui alterne — il le lisse")
    v("le taux planché ne descend jamais sous l'enroulement",
      abs(taux_du_cap([0.1 * w] * 16, 16, w, +1.0, "taux_planche") - w) < 1e-12
      and abs(taux_du_cap([0.1 * w] * 16, 16, w, +1.0, "taux") - 0.1 * w) < 1e-12)
    v("⚠ une moyenne lue à CONTRESENS de la marche ne peut pas être une rotation que le tour "
      "impose : le taux planché retombe sur l'enroulement",
      abs(taux_du_cap([-3.0 * w] * 16, 16, w, +1.0, "taux_planche") - w) < 1e-12
      and abs(taux_du_cap([-3.0 * w] * 16, 16, w, -1.0, "taux_planche") + 3.0 * w) < 1e-12)
    v("aucune règle nommée, aucun taux", taux_du_cap([w] * 16, 16, w, +1.0, "") == 0.0)
    v("une fenêtre qui ne porte rien ne prédit rien",
      taux_du_cap([w], 16, w, +1.0, "taux") == 0.0)
    v("⚠ la moyenne ne sert qu'à PRÉDIRE, jamais à corriger la cohérence — le piège de `144` "
      "n'est pas rejoué",
      memoire_adaptee([w] * 16, 16) == 0.0
      and abs(taux_du_cap([w] * 16, 16, w, +1.0, "taux") - w) < 1e-12,
      "la même suite rend une mémoire nulle ET un taux égal à l'enroulement")

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
    print("\n— le déroulage suppose-t-il ce qu'on lui demande ? —")
    # ⚠⚠⚠ UNE SERIE FABRIQUEE OU UN PAS FRANCHIT VRAIMENT PLUS D'UNE DEMI-FEUILLE. La phase perd
    # 0,8 feuille en un pas ; l'angle, lui, ne bouge presque pas, donc il ne dicte AUCUN entier.
    # Le repliement `d - round(d)` rend +0,2 et se trompe d'une feuille entiere.
    ph_ = [0.0, -0.8, -1.6]
    an_ = [0.0, 0.01, 0.02]
    ex = _le_deroulage_exact(ph_, an_)
    v("⭐⭐⭐⭐ le déroulage EXACT rend le pas que la phase a vraiment franchi",
      ex["derive_exacte_en_feuilles"] == -1.6 and ex["plus_grand_pas_en_feuilles"] == 0.8,
      f"{ex['derive_exacte_en_feuilles']} feuilles, plus grand pas "
      f"{ex['plus_grand_pas_en_feuilles']}")
    v("⭐⭐⭐ ... et il compte les pas que le repliement a pris à l'envers",
      ex["pas_replies_a_tort"] == 2 and ex["feuilles_repliees_a_tort"] == -2.0,
      f"{ex['pas_replies_a_tort']} pas, {ex['feuilles_repliees_a_tort']} feuilles")
    # ⚠ Et quand l'angle DICTE l'entier — un tour franchi entre deux pas — les deux s'accordent.
    ok_ = _le_deroulage_exact([0.0, 0.1, 0.2], [0.0, 0.01, 0.02])
    v("⚠ un pas sous la demi-feuille ne fait AUCUN litige",
      ok_["pas_replies_a_tort"] == 0
      and ok_["derive_exacte_en_feuilles"] == round(0.2, 4))
    v("⚠⚠ ... et sans série d'angles il n'y a pas de déroulage exact du tout, jamais un zéro",
      _le_deroulage_exact([0.0, 0.1], []) == {})
    # ⚠⚠ L'ARBITRE : sur la vraie fixture, un segment assez fin retrouve le pas que l'angle dicte.
    from combien_de_pas_la_matiere_porte import (  # noqa: PLC0415
        VolumeFabriqueEnSpiraleFroissee as _Spi)
    nue2 = _matiere(_Spi, 0.0, 0.0, 0.0, LONGUEUR_DONDE_UM, RAYON_MM)
    cy, cx = nue2.centre_yx_vx
    r_vx = RAYON_MM * 1000.0 / voxel_um
    a_ = np.array([2000.0, cy, cx + r_vx])
    b_ = a_ + np.array([0.0, 0.0, 1.6 * _PAS() / voxel_um])
    vrai = float(nue2.phase(b_.reshape(1, 3))[0]) - float(nue2.phase(a_.reshape(1, 3))[0])
    mesure, tranche = _le_pas_mesure(nue2, a_, b_)
    v("⭐⭐⭐⭐ l'arbitre retrouve un pas de plus d'une feuille, que le repliement écraserait",
      abs(mesure - vrai) < 1e-9 and abs(mesure) > 1.0 and tranche
      and abs(abs(vrai - round(vrai)) - abs(mesure)) > 0.5,
      f"{mesure:.6f} feuille, le repliement dirait {vrai - round(vrai):.6f}")
    # ⚠⚠ ET UN ECHANTILLONNAGE TROP GROSSIER REPLIE ENCORE : a DEUX sous-pas, chacun franchit 0,8
    # feuille et se replie, exactement comme le pas entier. C'est pour ca que le nombre se DOUBLE
    # jusqu'a l'accord plutot que de se poser — un nombre pose serait un seuil, et celui-ci se
    # verifie lui-meme.
    v("⚠⚠ le nombre d'échantillons se DOUBLE jusqu'à ce qu'AUCUN sous-pas ne soit replié",
      _le_chemin_du_pas(nue2, a_, b_, 4096) == (mesure, 0)
      and _le_chemin_du_pas(nue2, a_, b_, 2)[1] > 0
      and abs(_le_chemin_du_pas(nue2, a_, b_, 2)[0] - mesure) > 1e-9,
      f"à deux sous-pas le chemin replie {_le_chemin_du_pas(nue2, a_, b_, 2)[1]} sous-pas "
      f"et rend {_le_chemin_du_pas(nue2, a_, b_, 2)[0]:.6f}")
    # ⚠⚠⚠ ET LE CRITERE « DEUX ECHANTILLONNAGES S'ACCORDENT » EST FAUX, paye sur quatre vrais pas :
    # deux echantillonnages trop grossiers replient LE MEME sous-pas, rendent deux fois le meme
    # nombre faux, et se declarent d'accord. Ici, a 2 et a 4 sous-pas, la somme est la meme et
    # FAUSSE — seul le compte de replis le dit.
    # Douze feuilles en un segment : a 8 sous-pas chacun en franchit 1,5 et se replie a -0,5 ; a
    # 16 chacun en franchit 0,75 et se replie a -0,25. Les deux somment -4, et les deux ont tort.
    loin_ = a_ + np.array([0.0, 0.0, 12.0 * _PAS() / voxel_um])
    vrai_loin = float(nue2.phase(loin_.reshape(1, 3))[0]) - float(nue2.phase(a_.reshape(1, 3))[0])
    huit_, r8_ = _le_chemin_du_pas(nue2, a_, loin_, 8)
    seize_, r16_ = _le_chemin_du_pas(nue2, a_, loin_, 16)
    v("⭐⭐⭐⭐ deux échantillonnages peuvent s'ACCORDER sur un nombre FAUX — seul le compte de "
      "replis les dénonce",
      abs(huit_ - seize_) < 1e-9 and abs(huit_ - vrai_loin) > 1.0 and r8_ > 0 and r16_ > 0
      and abs(_le_pas_mesure(nue2, a_, loin_)[0] - vrai_loin) < 1e-9,
      f"{huit_:.6f} des deux côtés pour {r8_} et {r16_} replis, alors que le pas vaut "
      f"{vrai_loin:.6f}")

    # ⚠⚠ LA DECOMPOSITION EST EXACTE, TERME A TERME : `exacte = sauts + fluage`. Un pas
    # d'EXACTEMENT une demi-feuille n'a pas change de feuille — la borne est stricte, comme le
    # demi-pas de la contrainte et la demi-epaisseur du rejet.
    dec_ = _le_deroulage_exact([0.0, 0.8, 1.1, 2.5], [0.0, 0.01, 0.02, 0.03])
    v("⭐⭐⭐ la dérive exacte se décompose en SAUTS et FLUAGE, terme à terme",
      abs(dec_["derive_des_sauts_en_feuilles"] + dec_["derive_du_fluage_en_feuilles"]
          - dec_["derive_exacte_en_feuilles"]) < 1e-9 and dec_["pas_qui_sautent"] == 2,
      f"{dec_['derive_des_sauts_en_feuilles']} + {dec_['derive_du_fluage_en_feuilles']} = "
      f"{dec_['derive_exacte_en_feuilles']} sur {dec_['pas_qui_sautent']} sauts")
    v("⚠⚠ un pas d'exactement une demi-feuille ne SAUTE pas",
      _le_deroulage_exact([0.0, 0.5, 1.0], [0.0, 0.01, 0.02])["pas_qui_sautent"] == 0)

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
