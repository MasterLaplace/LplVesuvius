#!/usr/bin/env python3
"""« Consistent with » — la version quantifiée, celle que le papier fondateur ne construit pas.

⚠⚠ **Pourquoi ce fichier existe.** Sur les couches cachées d'un rouleau il n'y a, par
définition, aucune vérité terrain. L'unique argument du papier fondateur d'EduceLab pour
défendre ce qu'il y lit est celui-ci, cité mot pour mot :

> *« Crucially, the scale, line separation, and script of the revealed characters are
> consistent with those observed on the fragment surfaces. »*

⭐ **La forme est exactement la bonne** : on possède une région vérifiable et une région qui
ne l'est pas, et on transporte la confiance en montrant que les statistiques de second
ordre coïncident. C'est un transport de calibration, et c'est ce qu'il faut faire quand la
vérité manque.

⚠ **Mais il est laissé au jugement de l'œil.** Ni l'échelle, ni l'interligne, ni le trait
ne sont mesurés. Or les quatre sont mesurables **sans jamais connaître le contenu** — sans
lire une lettre, sans modèle de langue, sans alphabet. Ce fichier les mesure.

| grandeur | comment, ici |
|---|---|
| interligne | autocorrélation du profil de densité projeté perpendiculairement aux lignes |
| échelle de caractère | distribution des tailles de composantes connexes |
| taux de couverture | fraction de la surface de papyrus prédite « encre » |
| épaisseur de trait | pic de la transformée de distance à l'intérieur de l'encre |

⚠⚠ **Ce que l'instrument NE fait pas, et il faut le dire avant de le lire** : il ne dit pas
qu'un texte est du grec, ni qu'il veut dire quelque chose. Il dit qu'une prédiction a la
**statistique typographique** d'une page écrite — des traits d'une épaisseur donnée,
groupés en composantes d'une taille donnée, alignés à une période donnée. Une prédiction
qui échoue le test n'est certainement pas du texte ; une qui le passe **peut** être un
artefact périodique. C'est un contrôle nécessaire, jamais suffisant — exactement comme
l'absence d'auto-intersection l'est pour une trace.

Usage :
    uv run python src/encre/typographie.py data/encre \\
        --json docs/mesures/typographie.json
    python3 src/encre/typographie.py --verifier
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# ⚠ L'orientation des lignes n'est pas connue d'avance : une carte d'encre est une surface
# aplatie, et l'aplatissement ne redresse pas l'écriture. On balaie donc un petit éventail
# d'angles et on garde le plus net. Au-delà de ±12° la ligne d'écriture sortirait du champ
# de la fenêtre, et une carte à ce point tournée relève d'un autre problème.
ANGLES_DEG = tuple(range(-12, 13, 2))

# ⚠ Bornes de recherche de la période, en pixels. En dessous de 8 px on mesurerait la
# texture du papyrus ; au-dessus du quart de la hauteur on n'aurait pas quatre lignes, donc
# pas de périodicité à parler.
PERIODE_MIN = 8
PERIODE_MAX_PART = 0.25

# ⚠⚠ **Le seuil de périodicité n'est pas choisi, il est DÉRIVÉ.** L'autocorrélation d'un
# profil de bruit blanc de n points a, à un décalage donné, un écart-type de 1/√n ; le
# maximum sur k décalages candidats vaut donc environ √(2 ln k)/√n. Un pic doit dépasser
# ce plancher pour vouloir dire quelque chose, et le facteur de sécurité est la seule
# chose qu'on choisisse ici.
#
# ⭐ C'est ce qui rend le critère transportable : sur une carte deux fois plus petite le
# plancher monte tout seul. Un nombre écrit en dur — la première version disait 0,15 —
# aurait été calibré sur la taille des cartes qu'on avait sous la main.
FACTEUR_BRUIT = 2.0

# ⚠⚠ Au-dessus de quelle PART de fenêtres périodiques une carte « ressemble à une page
# écrite » ? Une carte porte des déchirures, des marges et des zones illisibles, donc
# exiger toutes ses fenêtres n'aurait aucun sens ; en exiger une seule non plus, une
# fenêtre pouvant être périodique par accident. La moitié est le point où la majorité de
# la surface porte la statistique.
#
# ⚠ Ce seuil-là, contrairement au plancher de bruit, est CHOISI. On le dit, et la mesure
# publie la part elle-même à côté du verdict, pour qu'un lecteur puisse en juger autrement.
PART_ECRITE_MIN = 0.5


def _np():
    import numpy as np
    return np


def masque_papyrus(img) -> "object":
    """La région qui EST du papyrus, par opposition au fond.

    ⚠⚠ Sans ce masque, le taux de couverture serait une fraction de l'image et non de la
    surface : une carte d'encre publiée est un fragment posé sur un fond noir, et sa
    proportion de fond dépend du recadrage, pas du papyrus. Deux cartes du même rouleau
    donneraient alors deux couvertures différentes pour une raison qui n'a rien à voir avec
    l'encre.
    """
    np = _np()
    return img > 0


def binariser_encre(img, masque) -> "object":
    """Sépare l'encre du support, par la méthode d'Otsu sur les seuls pixels de papyrus.

    ⚠ Otsu sur l'image ENTIÈRE trouverait la frontière entre le fond noir et le fragment,
    pas celle entre le support et l'encre — le seuil tomberait à quelques unités et
    presque tout le papyrus passerait pour de l'encre. Le masque n'est donc pas un détail
    de propreté : il change ce que le seuil sépare.
    """
    np = _np()
    vals = img[masque]
    if vals.size < 64:
        return np.zeros_like(masque)
    hist = np.bincount(vals.astype(np.int64), minlength=256)[:256].astype(float)
    total = hist.sum()
    if total == 0:
        return np.zeros_like(masque)
    niveaux = np.arange(256, dtype=float)
    poids0 = np.cumsum(hist)
    poids1 = total - poids0
    somme = np.cumsum(hist * niveaux)
    total_somme = somme[-1]
    ok = (poids0 > 0) & (poids1 > 0)
    sur0 = np.maximum(poids0, 1.0)
    sur1 = np.maximum(poids1, 1.0)
    moy0 = np.where(ok, somme / sur0, 0.0)
    moy1 = np.where(ok, (total_somme - somme) / sur1, 0.0)
    variance = np.where(ok, poids0 * poids1 * (moy0 - moy1) ** 2, -1.0)
    seuil = int(np.argmax(variance))
    return masque & (img > seuil)


def _profil(binaire, masque, angle_deg: float):
    """Densité d'encre par rangée, après rotation, rapportée à la surface de papyrus.

    ⚠ Rapportée à la surface : sur un fragment déchiqueté, une rangée qui traverse peu de
    papyrus a peu d'encre pour une raison géométrique. Un profil brut y verrait un creux
    et l'autocorrélation prendrait la forme du fragment pour une période d'écriture.
    """
    np = _np()
    from scipy import ndimage
    if abs(angle_deg) > 1e-9:
        b = ndimage.rotate(binaire.astype(np.float32), angle_deg, order=0,
                           reshape=False, mode="constant", cval=0.0)
        m = ndimage.rotate(masque.astype(np.float32), angle_deg, order=0,
                           reshape=False, mode="constant", cval=0.0)
    else:
        b, m = binaire.astype(np.float32), masque.astype(np.float32)
    surf = m.sum(axis=1)
    encre = b.sum(axis=1)
    # ⚠⚠ Le seuil de garde etait a 0,25 et le temoin a montre pourquoi c'est trop bas :
    # une rangee qui ne traverse qu'un quart de papyrus porte un rapport encre/surface
    # bruite, et deux rangees de bord suffisent a fabriquer un pic d'autocorrelation. Du
    # BRUIT PUR sortait « periodique » avec une nettete de 0,91. A 0,60 les rangees
    # retenues traversent toutes une largeur comparable, et le rapport redevient une
    # densite plutot qu'un quotient de petits nombres.
    garde = surf > (0.60 * max(surf.max(), 1.0))
    if garde.sum() < 4 * PERIODE_MIN:
        return None
    return encre[garde] / surf[garde]


def plancher_de_bruit(n: int, k: int) -> float:
    """Au-dessus de quelle proéminence un pic cesse d'être explicable par le hasard ?

    ⭐ L'autocorrélation d'un bruit blanc de `n` points a, à un décalage donné, un
    écart-type de 1/√n. Le maximum sur `k` décalages candidats vaut donc de l'ordre de
    √(2 ln k)/√n. Le plancher est ce nombre, multiplié par un facteur de sécurité — et
    c'est la seule quantité choisie à la main dans tout ce critère.

    ⚠ Il DÉPEND de la taille de la carte, et c'est le point : un seuil écrit en dur serait
    calibré sur les cartes qu'on avait sous la main le jour où on l'a écrit, et deviendrait
    faux sur un corpus de cartes plus petites.
    """
    if n < 4 or k < 2:
        return float("inf")
    return FACTEUR_BRUIT * math.sqrt(2.0 * math.log(k)) / math.sqrt(n)


def _detendancer(profil, largeur: int):
    """Retire la tendance lente du profil : une moyenne glissante soustraite.

    ⚠⚠ **Sans ça l'instrument rate la plupart des vraies pages, et le corpus l'a montré.**
    Une carte d'encre a des variations à grande échelle — le fragment s'élargit, la
    prédiction est plus dense d'un côté — qui dominent l'autocorrélation et la font
    décroître de façon monotone. Le pic de la période disparaît sous cette pente. Mesuré :
    **64 des 80 cartes** du premier rouleau n'avaient aucun maximum intérieur avant ce
    filtre, alors que plusieurs portent une écriture parfaitement lignée à l'œil.

    ⚠ La largeur du filtre est la plus grande période cherchée : plus étroit, il mangerait
    la période elle-même ; plus large, il laisserait passer la tendance.
    """
    np = _np()
    largeur = max(3, int(largeur) | 1)
    if profil.size <= largeur:
        return profil - profil.mean()
    noyau = np.ones(largeur) / largeur
    tendance = np.convolve(profil, noyau, mode="same")
    # ⚠ Les bords d'une convolution « same » sont divises par une fenetre tronquee, donc
    # biaises vers zero. On les recale sur la moyenne locale reelle plutot que de les
    # laisser fabriquer deux marches aux extremites.
    demi = largeur // 2
    if demi:
        tendance[:demi] = profil[:largeur].mean()
        tendance[-demi:] = profil[-largeur:].mean()
    return profil - tendance


def _autocorrelation(profil):
    np = _np()
    x = profil - profil.mean()
    n = x.size
    if n < 4 * PERIODE_MIN or float(np.dot(x, x)) <= 0:
        return None
    ac = np.correlate(x, x, mode="full")[n - 1:]
    return ac / ac[0]


def interligne(binaire, masque) -> dict:
    """La période d'écriture, et la NETTETÉ du pic qui la donne.

    ⭐ La netteté compte autant que la période. Une carte sans texte a toujours *une*
    période — celle du plus grand pic d'une autocorrélation de bruit — et la rendre seule
    ferait passer du bruit pour de l'écriture. C'est le couple (période, netteté) qui est
    la mesure, et la netteté seule qui décide.
    """
    np = _np()
    meilleur = {"periode_px": None, "nettete": 0.0, "angle_deg": None}
    for angle in ANGLES_DEG:
        prof = _profil(binaire, masque, angle)
        if prof is None:
            continue
        haut = max(PERIODE_MIN + 1, int(len(prof) * PERIODE_MAX_PART))
        ac = _autocorrelation(_detendancer(prof, haut))
        if ac is None:
            continue
        fenetre = ac[PERIODE_MIN:haut]
        if fenetre.size < 3:
            continue
        i = int(np.argmax(fenetre))
        # ⚠⚠ LE PIC DOIT ETRE INTERIEUR, avec un creux de chaque cote. C'est le controle
        # qui separe une PERIODE d'une MARCHE, et le temoin a montre qu'il manquait : une
        # zone ecrite entouree d'une marge vierge donne un profil qui monte puis redescend,
        # dont l'autocorrelation DECROIT de façon monotone -- son maximum tombe donc au
        # bord gauche de la fenetre (i = 0), et la premiere version le declarait
        # « periodique » avec une nettete de 0,88. Elle prenait le bord du fragment pour
        # de l'ecriture.
        if i == 0 or i >= fenetre.size - 1:
            continue
        # La PROEMINENCE : la hauteur du pic au-dessus du plus haut de ses deux creux.
        # C'est ce qu'un pic a de reellement propre, par opposition a un fond eleve.
        creux = max(float(fenetre[:i].min()), float(fenetre[i:].min()))
        nettete = float(fenetre[i]) - creux
        if nettete > meilleur["nettete"]:
            meilleur = {"periode_px": int(i + PERIODE_MIN), "nettete": nettete,
                        "plancher": plancher_de_bruit(len(prof), fenetre.size),
                        "angle_deg": float(angle)}
    meilleur.setdefault("plancher", None)
    meilleur["periodique"] = bool(meilleur["plancher"] is not None
                                  and meilleur["nettete"] >= meilleur["plancher"])
    return meilleur


def composantes(binaire) -> dict:
    """Taille et hauteur médianes des taches d'encre — l'échelle du caractère.

    ⚠ Une composante connexe n'est pas une lettre : deux lettres qui se touchent en font
    une, et une lettre brisée en fait deux. C'est une échelle, pas un comptage, et le nom
    de la fonction le dit.
    """
    np = _np()
    from scipy import ndimage
    lab, n = ndimage.label(binaire)
    if n == 0:
        return {"composantes": 0, "aire_mediane_px": None, "hauteur_mediane_px": None}
    aires = np.bincount(lab.ravel())[1:]
    # ⚠ Les taches d'un ou deux pixels sont du bruit de seuillage, pas des caracteres.
    # Les garder ecraserait la mediane vers 1 et rendrait la mesure inutilisable.
    grandes = np.where(aires >= 4)[0] + 1
    if grandes.size == 0:
        return {"composantes": 0, "aire_mediane_px": None, "hauteur_mediane_px": None}
    tranches = ndimage.find_objects(lab)
    hauteurs = [tranches[i - 1][0].stop - tranches[i - 1][0].start for i in grandes]
    return {"composantes": int(grandes.size),
            "aire_mediane_px": float(np.median(aires[grandes - 1])),
            "hauteur_mediane_px": float(np.median(hauteurs))}


def couverture(binaire, masque) -> float:
    """Fraction de la surface de PAPYRUS prédite « encre »."""
    np = _np()
    s = float(masque.sum())
    return float(binaire.sum()) / s if s else 0.0


def epaisseur_trait(binaire) -> float | None:
    """Épaisseur médiane d'un trait, par la transformée de distance.

    ⭐ La distance au bord, à l'intérieur d'un trait, vaut la moitié de son épaisseur au
    centre. On prend donc la médiane des maxima locaux plutôt que la médiane de toute la
    distance, qui serait tirée vers zéro par les bords.

    ⚠ Sans squelettisation : `skimage` est absent de cet environnement, et une
    squelettisation écrite à la main serait un second algorithme à garder juste pour un
    gain de précision dont rien ici ne dépend.
    """
    np = _np()
    from scipy import ndimage
    if not binaire.any():
        return None
    d = ndimage.distance_transform_edt(binaire)
    crete = d[d >= np.maximum(ndimage.maximum_filter(d, size=3) - 1e-9, 1.0)]
    if crete.size == 0:
        return None
    return float(2.0 * np.median(crete))


def par_fenetres(binaire, masque, taille: int = 512, part_min: float = 0.5):
    """L'interligne FENÊTRE PAR FENÊTRE, et non sur la carte entière.

    ⚠⚠ **La carte entière est le mauvais domaine, et le corpus l'a montré.** Une carte
    d'encre publiée contient souvent deux blocs de texte côte à côte — deux morceaux du
    même rouleau, dont les lignes ne sont pas à la même hauteur. Un profil de densité pris
    sur toute la largeur MOYENNE ces deux blocs : deux signaux de même période mais
    déphasés s'annulent en partie, et la période disparaît. Mesuré sur `PHercParis4` :
    64 cartes sur 80 ne rendaient aucun maximum intérieur, alors que plusieurs portent une
    écriture parfaitement lignée à l'œil.

    ⭐ Et l'interligne est de toute façon une propriété **locale** : c'est une fenêtre qui
    a un interligne, pas un fragment. Ce que la carte a, c'est une *distribution*
    d'interlignes et une *part* de sa surface qui ressemble à de l'écriture.
    """
    np = _np()
    h, w = binaire.shape
    for y in range(0, h - taille // 2, taille):
        for x in range(0, w - taille // 2, taille):
            mb = masque[y:y + taille, x:x + taille]
            if mb.size < taille * taille // 4:
                continue
            if float(mb.mean()) < part_min:
                continue
            yield interligne(binaire[y:y + taille, x:x + taille], mb)


def signature(img, taille_fenetre: int = 512) -> dict:
    """Les quatre grandeurs d'une carte d'encre en niveaux de gris.

    ⚠ Le seuil d'encre est calculé UNE FOIS sur toute la carte, puis appliqué fenêtre par
    fenêtre. Un seuil par fenêtre serait instable là où il n'y a rien à séparer : sur une
    fenêtre vierge, Otsu coupe le bruit du support en deux et fabrique de l'encre.
    """
    np = _np()
    masque = masque_papyrus(img)
    binaire = binariser_encre(img, masque)
    d = {"surface_px": int(masque.sum()), "couverture": couverture(binaire, masque),
         "epaisseur_trait_px": epaisseur_trait(binaire)}
    d.update(composantes(binaire))

    fen = list(par_fenetres(binaire, masque, taille_fenetre))
    per = [f for f in fen if f["periodique"]]
    d["fenetres"] = len(fen)
    d["fenetres_periodiques"] = len(per)
    d["part_periodique"] = (len(per) / len(fen)) if fen else 0.0
    periodes = sorted(f["periode_px"] for f in per)
    d["periode_px"] = periodes[len(periodes) // 2] if periodes else None
    # ⚠ L'ECART entre les fenetres compte autant que la mediane : une page ecrite a un
    # interligne CONSTANT. Des fenetres qui rendent des periodes eparpillees sont des
    # fenetres qui trouvent chacune un pic different, c'est-a-dire du bruit.
    d["periode_ecart_px"] = (float(periodes[3 * len(periodes) // 4] - periodes[len(periodes) // 4])
                             if len(periodes) >= 4 else None)
    d["nettete_mediane"] = (float(sorted(f["nettete"] for f in per)[len(per) // 2])
                            if per else 0.0)
    return d


def _page_synthetique(largeur=400, hauteur=400, periode=30, epaisseur=4, marge=40):
    """Une page d'écriture FABRIQUÉE, dont on connaît la période et l'épaisseur.

    ⚠⚠ C'est ce qui rend l'instrument falsifiable. Mesurer un vrai corpus ne dit jamais si
    la mesure est juste — il n'y a rien à quoi la comparer. Sur une page dont on a choisi
    l'interligne, on sait ce que l'instrument DOIT rendre.
    """
    np = _np()
    img = np.full((hauteur, largeur), 40, dtype=np.uint8)     # papyrus
    img[:marge, :] = img[-marge:, :] = 0                      # fond
    img[:, :marge] = img[:, -marge:] = 0
    rng = np.random.default_rng(0)
    for y in range(marge + periode, hauteur - marge, periode):
        x = marge + 6
        while x < largeur - marge - 12:
            w = int(rng.integers(6, 12))
            img[y:y + epaisseur, x:x + w] = 220               # un trait horizontal
            img[y:y + max(epaisseur, 8), x:x + epaisseur] = 220   # un jambage
            x += w + int(rng.integers(4, 9))
    return img


def verifier() -> int:
    np = _np()
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⭐ Le seuillage : sur une page synthetique, l'encre doit sortir de l'encre.
    page = _page_synthetique()
    m = masque_papyrus(page)
    b = binariser_encre(page, m)
    v("le masque exclut le fond", int(m.sum()) < page.size)
    v("... et garde tout le papyrus", int(m.sum()) == int((page > 0).sum()))
    v("le seuillage trouve l'encre et pas le support",
      0.02 < couverture(b, m) < 0.40, f"{couverture(b, m):.3f}")
    # ⚠⚠ LA sonde du masque, et la premiere version la posait A L'ENVERS. J'affirmais que
    # sans masque « presque tout le papyrus passe pour de l'encre » : mesure, c'est faux
    # sur cette page (0,066). Le vrai defaut est ailleurs et il est plus grave — sans
    # masque, la couverture est une fraction de l'IMAGE, donc elle depend du RECADRAGE.
    # Deux vues du meme papyrus rendent alors deux couvertures differentes pour une raison
    # qui n'a rien a voir avec l'encre.
    large = np.zeros((page.shape[0] * 2, page.shape[1] * 2), dtype=np.uint8)
    large[:page.shape[0], :page.shape[1]] = page
    ml = masque_papyrus(large)
    c_serre = couverture(binariser_encre(page, m), m)
    c_large = couverture(binariser_encre(large, ml), ml)
    v("la couverture ne dépend PAS du recadrage, grâce au masque",
      abs(c_serre - c_large) < 0.01, f"{c_serre:.3f} contre {c_large:.3f}")
    tout_s, tout_l = np.ones_like(m), np.ones_like(ml)
    sans_serre = couverture(binariser_encre(page, tout_s), tout_s)
    sans_large = couverture(binariser_encre(large, tout_l), tout_l)
    v("... alors que sans masque elle en dépend d'un facteur trois",
      sans_serre > 3 * sans_large, f"{sans_serre:.3f} contre {sans_large:.3f}")

    # ⭐⭐ La periode : on la CONNAIT, donc on peut dire si la mesure est juste.
    for periode in (20, 30, 45):
        r = interligne(*(lambda p: (binariser_encre(p, masque_papyrus(p)),
                                    masque_papyrus(p)))(_page_synthetique(periode=periode)))
        v(f"l'interligne de {periode} px est retrouvé",
          r["periodique"] and abs(r["periode_px"] - periode) <= 2,
          f"{r['periode_px']} (netteté {r['nettete']:.3f})")

    # ⚠⚠ Les controles negatifs, sans lesquels « periodique » ne voudrait rien dire.
    #
    # (a) LA MARCHE. Une zone ecrite entouree d'une marge vierge : le profil monte d'un
    # coup et redescend. La premiere version la declarait periodique avec une nettete de
    # 0,88 -- elle prenait le bord du fragment pour de l'ecriture. C'est ce cas qui a fait
    # ajouter le controle d'harmonique.
    rng = np.random.default_rng(1)
    marche = np.full((400, 400), 40, dtype=np.uint8)
    marche[40:-40, 40:-40] = rng.integers(0, 255, size=(320, 320), dtype=np.uint8)
    mm = masque_papyrus(marche)
    rm = interligne(binariser_encre(marche, mm), mm)
    v("une marge vierge autour d'une zone dense n'est PAS une période",
      not rm["periodique"],
      f"netteté {rm['nettete']:.3f}, plancher {rm['plancher']}")

    # (b) DU BRUIT, sur toute la surface, sans marge : rien ne doit s'y repeter.
    bruit = rng.integers(0, 255, size=(400, 400), dtype=np.uint8)
    mb = masque_papyrus(bruit)
    rb = interligne(binariser_encre(bruit, mb), mb)
    v("du bruit n'est PAS déclaré périodique", not rb["periodique"],
      f"netteté {rb['nettete']:.3f}, plancher {rb['plancher']}")

    vide = np.full((400, 400), 40, dtype=np.uint8)
    vide[:40, :] = vide[-40:, :] = vide[:, :40] = vide[:, -40:] = 0
    mv = masque_papyrus(vide)
    rv = interligne(binariser_encre(vide, mv), mv)
    v("une carte vide n'est pas périodique non plus", not rv["periodique"],
      f"netteté {rv['nettete']:.3f}")

    # ⭐ L'epaisseur du trait, elle aussi connue.
    for ep in (3, 5, 8):
        p = _page_synthetique(epaisseur=ep, periode=40)
        e = epaisseur_trait(binariser_encre(p, masque_papyrus(p)))
        v(f"l'épaisseur de trait de {ep} px est retrouvée", e is not None and abs(e - ep) <= 2,
          f"{e}")

    # ⭐ L'echelle des composantes.
    c = composantes(b)
    v("les composantes sont comptées", c["composantes"] > 20, str(c["composantes"]))
    v("... et leur hauteur médiane est celle d'un caractère",
      c["hauteur_mediane_px"] is not None and 4 <= c["hauteur_mediane_px"] <= 20,
      str(c["hauteur_mediane_px"]))
    v("le bruit d'un pixel ne compte pas comme composante",
      composantes(np.zeros((50, 50), dtype=bool))["composantes"] == 0)

    # ⚠ Une carte tournee doit rendre la MEME periode : sinon l'instrument mesurerait
    # l'orientation du fragment plutot que l'ecriture.
    from scipy import ndimage
    droite = _page_synthetique(periode=30)
    penchee = ndimage.rotate(droite, 6, order=0, reshape=False, mode="constant", cval=0)
    r1 = interligne(*(lambda p: (binariser_encre(p, masque_papyrus(p)),
                                 masque_papyrus(p)))(droite))
    r2 = interligne(*(lambda p: (binariser_encre(p, masque_papyrus(p)),
                                 masque_papyrus(p)))(penchee))
    v("une page inclinée rend la même période",
      r2["periodique"] and abs(r2["periode_px"] - r1["periode_px"]) <= 3,
      f"{r1['periode_px']} contre {r2['periode_px']}")

    # ⭐ La sonde du plancher lui-meme : il doit MONTER quand la carte retrecit, sinon il
    # ne serait qu'un nombre ecrit en dur avec une formule autour.
    # ⚠ L'attendu de la premiere version demandait STRICTEMENT plus du double, alors que
    # la loi est en 1/√n : quatre fois moins de points font exactement le double. C'est
    # l'attendu qui avait tort. On asserte donc la LOI plutot qu'une inegalite molle.
    v("le plancher suit la loi en 1/√n — quatre fois moins de points, deux fois plus haut",
      abs(plancher_de_bruit(100, 20) - 2 * plancher_de_bruit(400, 20)) < 1e-9,
      f"{plancher_de_bruit(100, 20):.3f} contre {plancher_de_bruit(400, 20):.3f}")
    v("... et il monte aussi avec le nombre de décalages testés",
      plancher_de_bruit(400, 90) > plancher_de_bruit(400, 20))
    v("... et une carte trop petite n'a pas de plancher franchissable",
      plancher_de_bruit(2, 20) == float("inf"))

    s = signature(page)
    v("la signature porte les quatre grandeurs",
      all(s.get(k) is not None for k in
          ("couverture", "epaisseur_trait_px", "hauteur_mediane_px", "periode_px")),
      str({k: s.get(k) for k in
           ("couverture", "epaisseur_trait_px", "hauteur_mediane_px", "periode_px")}))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # --- LE TEST DECLARE AVANT LA CAMPAGNE, et son refus ------------------------------
    # ⚠⚠ Ces controles portent sur la borne autant que sur le calcul : avec 2 fenetres
    # contre 2, le plus petit p atteignable vaut 1/6, donc un test lance la rendrait un
    # nombre qui ne pouvait PAS etre significatif. Refuser est le seul comportement honnete.
    petit = fisher_periodicite({"fenetres_periodiques": 2, "fenetres": 2},
                               {"fenetres_periodiques": 0, "fenetres": 2})
    v("sous huit fenetres, le test REFUSE au lieu de rendre un p", petit["p"] is None)
    v("... et il dit pourquoi", "puissance" in (petit.get("raison") or ""))
    v("... en rendant quand meme le tableau, pour qu'on puisse le refaire",
      petit["table"] == [2, 0, 0, 2])

    net = fisher_periodicite({"fenetres_periodiques": 10, "fenetres": 10},
                             {"fenetres_periodiques": 0, "fenetres": 10})
    v("une separation franche a n suffisant rend un p petit", net["p"] is not None and net["p"] < 0.01)
    nul = fisher_periodicite({"fenetres_periodiques": 5, "fenetres": 10},
                             {"fenetres_periodiques": 5, "fenetres": 10})
    v("... et l'absence d'effet un p grand", nul["p"] is not None and nul["p"] > 0.4)
    # ⚠⚠ Le controle qui verifie que le test est bien UNILATERAL dans la direction declaree :
    # une carte MOINS periodique que son melange ne doit pas ressortir significative.
    envers = fisher_periodicite({"fenetres_periodiques": 0, "fenetres": 10},
                                {"fenetres_periodiques": 10, "fenetres": 10})
    v("l'effet inverse n'est pas declare significatif", envers["p"] is not None and envers["p"] > 0.99)

    # ⚠⚠⚠ Cette ligne imprimait « ALL PASS » et rendait 0 **inconditionnellement** : la
    # batterie ne pouvait pas échouer, quoi que disent ses contrôles, et `temoins.sh` la
    # comptait verte depuis toujours. Trouvé le 2026-08-27 en sondant un tout autre
    # correctif — la sonde a rendu « ALL PASS (2 failures, 28 checks) », une phrase qui se
    # contredit elle-même.
    # --- LES CARTES ABSENTES, nommees plutot que fatales -------------------------------
    # ⚠⚠ La campagne accumule les quatre chemins AVANT de savoir si chaque rendu a abouti :
    # une carte manquante tuait l'analyse finale apres trois heures de rendu.
    from pathlib import Path as _P
    ici, la = cartes_presentes([_P(__file__), _P("/tmp/absente_xyz_123.npy")])
    v("une carte presente est gardee", ici == [_P(__file__)])
    v("... et l'absente est nommee a part", la == [_P("/tmp/absente_xyz_123.npy")])
    v("l'ordre recu est conserve",
      cartes_presentes([_P(__file__), _P(__file__)])[0] == [_P(__file__)] * 2)
    # ⚠ Et l'ensemble vide doit rester DISTINGUABLE : analyser rien ne doit pas ressembler
    # a analyser tout. C'est `main` qui refuse, sur ce predicat.
    v("aucune carte presente se voit", cartes_presentes([_P("/tmp/x_absent.npy")])[0] == [])
    # --- LE TEST GROUPE, declare avant la quatrieme carte ------------------------------
    # ⚠⚠⚠ Declare le 2026-08-28 AVANT tout resultat : trois des quatre surfaces ne peuvent
    # pas atteindre le seuil de 8, et cela se calcule depuis leurs dimensions seules.
    # ⚠⚠ Une carte de deux fenetres ne peut pas etre testee seule (2 + 2 = 4 < 8), et
    # DEUX telles cartes groupees font 4 + 4 = 8, soit exactement le seuil. Ce n'est pas
    # une faille : a 4 contre 4, le plus petit p qu'un Fisher unilateral puisse rendre vaut
    # 1/C(8,4) = 0,0143, donc sous 0,05 — la raison meme pour laquelle le seuil vaut 8.
    une_petite = {"fenetres_periodiques": 2, "fenetres": 2}
    v("une carte de deux fenetres ne se teste pas seule",
      fisher_periodicite(une_petite, {"fenetres_periodiques": 0, "fenetres": 2})["p"]
      is None)
    petites_r = [une_petite, {"fenetres_periodiques": 1, "fenetres": 2}]
    petites_m = [{"fenetres_periodiques": 0, "fenetres": 2},
                 {"fenetres_periodiques": 0, "fenetres": 2}]
    groupees = fisher_periodicite_groupee(petites_r, petites_m)
    v("... mais deux d'entre elles groupees atteignent exactement le seuil",
      groupees["p"] is not None and sum(groupees["table"]) == 8)
    # ⚠ Et le seuil garde son sens : a cette taille, un p sous 0,05 reste ATTEIGNABLE.
    v("... et a cette taille un p sous 0,05 reste atteignable",
      fisher_periodicite_groupee(
          [une_petite, une_petite],
          [{"fenetres_periodiques": 0, "fenetres": 2}] * 2)["p"] < 0.05)
    v("une seule carte trop petite le reste une fois « groupee »",
      fisher_periodicite_groupee([une_petite],
                                 [{"fenetres_periodiques": 0, "fenetres": 2}])["p"]
      is None)
    grandes_r = [{"fenetres_periodiques": 2, "fenetres": 2},
                 {"fenetres_periodiques": 20, "fenetres": 24}]
    grandes_m = [{"fenetres_periodiques": 0, "fenetres": 2},
                 {"fenetres_periodiques": 1, "fenetres": 24}]
    g = fisher_periodicite_groupee(grandes_r, grandes_m)
    v("le groupement somme les fenetres des cartes", g["table"] == [22, 4, 1, 25])
    v("... et dit combien de cartes il a groupees", g["cartes"] == 2)
    v("un groupement franchissant le seuil rend un p", g["p"] is not None)
    # ⚠ Le groupement ne doit pas RENVERSER le sens : plus periodique en reel reste plus
    # periodique une fois somme.
    v("le p groupe est petit quand la separation est nette", g["p"] < 0.001)
    v("aucune carte a grouper le dit plutot que de lever",
      fisher_periodicite_groupee([], [])["p"] is None)
    # ⚠⚠ Et le controle qui empeche de le prendre pour le test principal : groupe une
    # SEULE carte, il doit rendre exactement le test de cette carte.
    seule = fisher_periodicite_groupee([grandes_r[1]], [grandes_m[1]])
    v("groupe sur une seule carte, il rend le test de cette carte",
      seule["table"] == fisher_periodicite(grandes_r[1], grandes_m[1])["table"])
    # --- LE GROUPEMENT NE DOIT PAS AVALER SON TEMOIN -----------------------------------
    # ⚠⚠⚠ Panne reelle du 2026-08-28 : la campagne a groupe nos quatre surfaces AVEC le
    # temoin Scroll 1, et la moitie du signal groupe venait de lui.
    sujet = {"fenetres_periodiques": 2, "fenetres": 3}
    temoin = {"fenetres_periodiques": 8, "fenetres": 12}
    vide = {"fenetres_periodiques": 0, "fenetres": 3}
    vide_t = {"fenetres_periodiques": 0, "fenetres": 12}
    avec = fisher_periodicite_groupee([sujet] * 4 + [temoin], [vide] * 4 + [vide_t])
    sans = fisher_periodicite_groupee([sujet] * 4, [vide] * 4)
    v("grouper le temoin change la table", avec["table"] != sans["table"])
    v("... et le temoin apporte la moitie du signal",
      avec["table"][0] == 2 * sans["table"][0])
    v("le groupement des seuls sujets tient debout",
      sans["p"] is not None and sans["table"] == [8, 4, 0, 12])
    # ⚠ Et il faut que le groupe SANS temoin soit encore significatif : sinon exclure le
    # temoin reviendrait a perdre le resultat, ce qui n'est pas la meme chose que le
    # rendre honnete.
    v("... et reste sous 0,05 une fois le temoin retire", sans["p"] < 0.05)



    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def croiser_encre(cartes: list[dict], segments: list[dict], cle: str) -> dict:
    """Le test de TRANSPORT : la statistique typographique sépare-t-elle les cartes que
    l'on sait lisibles de celles que l'on sait presque vides ?

    ⚠⚠ **C'est le seul contrôle disponible, et il faut dire pourquoi.** Aucune de ces
    cartes n'a de vérité terrain au sens des lettres — ce sont toutes des sorties d'un
    modèle. Ce qu'on possède, c'est une classe **connue comme presque vide**, identifiée
    indépendamment par le contraste d'encre publié. Si la mesure typographique, qui ne
    lit rien, retrouve cette classe, alors elle mesure bien quelque chose de l'écriture.
    Si elle ne la retrouve pas, elle ne mesure rien d'utile — et il faudra le dire.

    ⚠ Le contraste d'encre n'est PAS une vérité terrain non plus : c'est une autre sortie
    du même pipeline. L'accord de deux mesures indépendantes du même objet est plus faible
    qu'une vérification, et plus fort que rien.
    """
    par_id = {c["carte"]: c for c in cartes}
    paires = [(par_id[s["segment"]], s) for s in segments
              if s["segment"] in par_id and s.get(cle) is not None]
    if len(paires) < 8:
        return {"n": len(paires), "raison": "trop peu de segments appariés"}
    contrastes = sorted(s[cle] for _, s in paires)
    # ⚠ La mediane comme partage, plutot qu'un seuil choisi : elle ne peut pas etre
    # ajustee pour que le resultat sorte, et elle rend deux groupes de taille egale.
    seuil = contrastes[len(contrastes) // 2]
    med = lambda xs: (sorted(xs)[len(xs) // 2] if xs else None)  # noqa: E731

    def aire_sous_courbe(prendre):
        """Mann-Whitney U par les rangs, rendu en AUC. 0,50 = aucune association.

        ⚠ Sans scipy et sans hypothese de forme : c'est un test de RANGS, donc il vaut
        pour des grandeurs qui n'ont ni la meme unite ni la meme distribution -- une
        couverture, une epaisseur en pixels et une part de fenetres.
        """
        faible = [prendre(t) for t, s in paires if s[cle] <= seuil]
        fort = [prendre(t) for t, s in paires if s[cle] > seuil]
        if not faible or not fort:
            return None, None, None
        tous = sorted(faible + fort)
        rang: dict = {}
        for i, v in enumerate(tous):
            rang.setdefault(v, []).append(i + 1)
        moyrang = {v: sum(r) / len(r) for v, r in rang.items()}
        u = sum(moyrang[v] for v in fort) - len(fort) * (len(fort) + 1) / 2
        return u / (len(fort) * len(faible)), med(faible), med(fort)

    # ⚠⚠ TOUTES les grandeurs, pas seulement celle qu'on espere. La premiere version ne
    # croisait que la part de fenetres periodiques, sortait AUC 0,31 -- une association
    # INVERSE -- et il aurait ete facile d'en conclure que l'instrument ne vaut rien. Les
    # trois autres tracent le contraste franchement. Ne regarder qu'une grandeur, c'est
    # choisir sa conclusion avant de mesurer.
    grandeurs = {
        "couverture": lambda t: t["couverture"],
        "epaisseur_trait_px": lambda t: t["epaisseur_trait_px"] or 0.0,
        "nettete_mediane": lambda t: t["nettete_mediane"],
        "hauteur_mediane_px": lambda t: t["hauteur_mediane_px"] or 0.0,
        "composantes": lambda t: float(t["composantes"]),
        "part_periodique": lambda t: t["part_periodique"],
    }
    out = {"n": len(paires), "cle": cle, "seuil": seuil,
           "n_faible": sum(1 for _, s in paires if s[cle] <= seuil),
           "n_fort": sum(1 for _, s in paires if s[cle] > seuil),
           "grandeurs": {}}
    for nom, f in grandeurs.items():
        a, mf, mF = aire_sous_courbe(f)
        out["grandeurs"][nom] = {"auc": a, "mediane_faible": mf, "mediane_forte": mF}

    # ⚠⚠ Les COUPLES appariés voyagent dans le résultat, et pas seulement les résumés.
    # Une figure qui prétend montrer « pourquoi » doit tracer les données SUR LESQUELLES
    # l'AUC est calculé. La première version traçait la couverture des 190 cartes des
    # quatre rouleaux contre l'AUC calculé sur le contraste de 80 cartes d'un seul —
    # deux variables et deux corpus différents — et le nuage montait là où l'AUC dit que
    # ça descend. Une figure qui contredit son propre tableau est pire qu'aucune figure.
    out["couples"] = [{"segment": s["segment"], "contraste": s[cle],
                       **{n: f(t) for n, f in grandeurs.items()}}
                      for t, s in paires]

    # ⭐ Et le rang de Spearman, parce que l'AUC dit « il y a une association » sans dire
    # si elle est monotone. Ici elle ne l'est pas : la séparabilité chute du premier au
    # troisième quartile puis se stabilise, et un lecteur doit pouvoir le voir.
    def rangs(xs):
        ordre = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        for k, i in enumerate(ordre):
            r[i] = k + 1
        return r
    for nom, f in grandeurs.items():
        x = rangs([s[cle] for _, s in paires])
        y = rangs([f(t) for t, _ in paires])
        n = len(x)
        mx, my = sum(x) / n, sum(y) / n
        num = sum((a - mx) * (b - my) for a, b in zip(x, y))
        den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
        out["grandeurs"][nom]["rho"] = (num / den) if den else None
    return out


def carte_npy_en_gris(chemin, reduire: int = 1):
    """Une de NOS cartes de prédiction (`.npy` de logits) en niveaux de gris comparables.

    ⚠⚠ Les 190 cartes publiées sont des JPEG uint8 ; les nôtres sont des logits flottants.
    Pour que la signature typographique soit comparable, il faut la MÊME transformation que
    celle qui sert à les regarder — un étirement sur les percentiles 2 et 98 — et non un
    étirement sur min/max, qu'un seul pixel aberrant écraserait.

    ⚠ Les pixels non couverts sortent à zéro, comme un bord de segment sur une carte
    publiée : ils ne sont pas de l'encre absente, ils sont hors surface, et
    `masque_papyrus` les écarte de la même façon dans les deux cas.
    """
    np = _np()
    from PIL import Image

    a = np.load(chemin)
    m = np.isfinite(a) & (a > -9e9)
    if not m.any():
        raise ValueError(f"{chemin} : aucun pixel couvert")
    lo, hi = np.percentile(a[m], [2, 98])
    img = np.clip((a - lo) / max(hi - lo, 1e-9), 0.0, 1.0)
    img[~m] = 0.0
    im = Image.fromarray((img * 255).astype(np.uint8), "L")
    if reduire > 1:
        im = im.reduce(reduire)
    return np.asarray(im, dtype=np.uint8)


def cartes_presentes(chemins):
    """Sépare les cartes qui existent de celles qui manquent, dans l'ordre reçu.

    ⚠ Extrait de `main` pour être sondable : un tri qui décide si une analyse tourne ou
    refuse, et qui n'est atteignable que par la ligne de commande, ne peut pas être vérifié.
    """
    return ([c for c in chemins if c.exists()],
            [c for c in chemins if not c.exists()])


N_MINIMAL_POUR_TESTER = 8
"""Sous ce nombre de fenêtres, on NE TESTE PAS.

⚠⚠ Ce n'est pas une prudence de style : avec 2 fenêtres contre 2, le p le plus petit
qu'un Fisher unilatéral puisse rendre vaut 1/6, donc le test ne peut PAS descendre sous
0,05 même si la séparation est parfaite. Lancer le test quand même produirait un nombre
qui ressemble à un résultat et qui ne pouvait pas en être un. La borne est déclarée dans
`60` avant que la campagne ne rende.
"""


def fisher_periodicite(reel: dict, melange: dict) -> dict:
    """La part périodique observée est-elle distinguable de celle du mélange ?

    ⚠ Unilatéral, et la direction est déclarée d'avance : une carte réelle devrait être
    **plus** périodique que ses propres pixels mélangés, jamais moins. Un test bilatéral
    saluerait aussi l'effet inverse, ce qui reviendrait à n'avoir pas eu d'hypothèse.

    ⚠⚠ Et il REFUSE sous `N_MINIMAL_POUR_TESTER`, en disant pourquoi, plutôt que de rendre
    un p que la taille de l'échantillon rendait inatteignable.
    """
    from math import comb

    a, na = reel["fenetres_periodiques"], reel["fenetres"]
    c, nc = melange["fenetres_periodiques"], melange["fenetres"]
    if na + nc < N_MINIMAL_POUR_TESTER:
        return {"p": None, "table": [a, na - a, c, nc - c],
                "raison": f"{na + nc} fenêtres en tout, moins que {N_MINIMAL_POUR_TESTER} : "
                          "le test n'a pas la puissance de descendre sous 0,05"}
    b, d = na - a, nc - c
    n = a + b + c + d
    lignes, colonnes = a + b, a + c
    total = comb(n, colonnes)
    if total == 0:
        return {"p": None, "table": [a, b, c, d], "raison": "tableau vide"}
    p = sum(comb(lignes, k) * comb(n - lignes, colonnes - k) / total
            for k in range(a, min(lignes, colonnes) + 1))
    return {"p": p, "table": [a, b, c, d]}


def fisher_periodicite_groupee(reels: list[dict], melanges: list[dict]) -> dict:
    """Le même test, sur la SOMME des fenêtres de plusieurs cartes du même rouleau.

    ⚠⚠⚠ DÉCLARÉ LE 2026-08-28, AVANT que la quatrième carte n'existe et donc avant tout
    résultat. Ce n'est pas une précaution de style : au réglage calibré (réduction 8, fenêtre
    256) les quatre surfaces publiées de `PHerc1447` donnent **4, 2 et 24 fenêtres** — trois
    d'entre elles ne peuvent PAS atteindre le seuil de 8 déclaré, et cela se calcule depuis
    leurs seules dimensions, sans rien mesurer. Ajouter ce test après avoir vu que trois
    cartes sur quatre restent muettes serait ajuster l'analyse aux données ; l'ajouter pendant
    que la quatrième se télécharge ne l'est pas.

    ⭐ Ce que le groupement change, et il faut le dire : il répond à « **ce rouleau** porte-t-il
    une structure périodique » là où le test par carte répond à « peut-on dire quelque chose de
    **cette surface** ». Les deux questions sont légitimes et ne sont pas la même. **Le test par
    carte reste le principal** ; celui-ci est secondaire et déclaré comme tel.

    ⚠ Le groupement suppose que les surfaces sont des observations distinctes du même rouleau.
    C'est vrai ici — quatre segments différents, non recouvrants — et ce serait FAUX si l'on
    groupait deux rendus de la même surface, qui ne compteraient alors qu'une fois.
    """
    if not reels or not melanges:
        return {"p": None, "table": [0, 0, 0, 0], "cartes": 0,
                "raison": "aucune carte à grouper"}
    somme_reel = {
        "fenetres_periodiques": sum(l["fenetres_periodiques"] for l in reels),
        "fenetres": sum(l["fenetres"] for l in reels),
    }
    somme_melange = {
        "fenetres_periodiques": sum(l["fenetres_periodiques"] for l in melanges),
        "fenetres": sum(l["fenetres"] for l in melanges),
    }
    resultat = fisher_periodicite(somme_reel, somme_melange)
    resultat["cartes"] = len(reels)
    return resultat


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dossier", nargs="?", type=Path,
                    help="racine des cartes d'encre, un sous-dossier par rouleau")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--reduire", type=int, default=4,
                    help="facteur de réduction avant mesure (défaut 4)")
    ap.add_argument("--encre", type=Path,
                    help="croiser avec un fichier de segments portant un contraste "
                         "d'encre (docs/mesures/croisement_encre.json)")
    ap.add_argument("--cle-encre", default="encre_contraste_p90_p50")
    ap.add_argument("--taille-fenetre", type=int, default=512,
                    help="côté de la fenêtre d'analyse, en pixels APRÈS réduction. ⚠ Il "
                         "borne la plus petite carte mesurable : à réduction 8 sur un scan "
                         "à 8 µm, 512 px valent 35 mm de papyrus")
    ap.add_argument("--controle-melange", action="store_true",
                    help="mesurer AUSSI la même carte pixels mélangés : même distribution, "
                         "aucune structure. Sans ce contrôle, « 2 fenêtres sur 2 » n'a pas "
                         "d'échelle — c'est un tirage à pile ou face")
    ap.add_argument("--graine", type=int, default=0)
    ap.add_argument("--temoin", type=Path, nargs="*", default=[],
                    help="cartes mesurées et testées INDIVIDUELLEMENT mais EXCLUES du "
                         "groupement : un témoin d'un autre rouleau, dont on sait déjà "
                         "qu'il porte du texte, gonflerait le test groupé de son propre "
                         "signal")
    ap.add_argument("--npy", type=Path, nargs="*",
                    help="mesurer NOS cartes de prédiction (.npy) au lieu d'un dossier "
                         "d'images publiées — même signature, même réduction")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.npy:
        import json as _json

        import numpy as np
        lignes = []
        # ⚠⚠ UNE CARTE ABSENTE NE DOIT PAS TUER L'ANALYSE. La campagne qui appelle cet
        # outil accumule les quatre chemins AVANT de savoir si chaque rendu a abouti : un
        # pont zarr qui échoue sur le dernier segment faisait donc mourir l'analyse finale
        # après trois heures de rendu, et le run entier ne rendait rien. Mesuré le
        # 2026-08-28 : `FileNotFoundError`, code 1, aucun résultat écrit.
        #
        # ⚠ Sauter n'est PAS silencieux : chaque absente est nommée et comptée. Une carte
        # manquante est un livrable manquant, et un saut discret la ferait passer pour une
        # analyse complète.
        presentes, absentes = cartes_presentes(a.npy)
        for c in absentes:
            print(f"  ⚠ carte absente, écartée : {c}")
        # ⚠⚠ Et si AUCUNE n'existe, on refuse : analyser l'ensemble vide sortirait en zéro
        # avec un JSON bien formé, c'est-à-dire qu'un run qui n'a rien mesuré ressemblerait
        # à un run réussi.
        if not presentes:
            print(f"erreur : aucune des {len(a.npy)} cartes nommées n'existe",
                  file=sys.stderr)
            return 2
        for c in presentes:
            gris = carte_npy_en_gris(c, a.reduire)
            s = signature(gris, a.taille_fenetre)
            s.update({"rouleau": "nos_cartes", "carte": c.stem, "reduction": a.reduire,
                      "taille_fenetre": a.taille_fenetre})
            lignes.append(s)
            def dire(etiquette, d):
                print(f"  {etiquette:44} surface {d['surface_px']:>9}  "
                      f"couverture {d['couverture']:.3f}  "
                      f"périodiques {d['fenetres_periodiques']}/{d['fenetres']} "
                      f"({d['part_periodique']:.0%})  "
                      f"période {d['periode_px']}  netteté {d['nettete_mediane']:.3f}")

            dire(c.stem, s)
            if a.controle_melange:
                # ⚠⚠ Le mélange garde la DISTRIBUTION et détruit la STRUCTURE. C'est le seul
                # contrôle qui donne une échelle à « n fenêtres sur n » quand n est petit :
                # si la carte mélangée est périodique elle aussi, le compte ne dit rien.
                # ⚠ Le mélange ne touche QUE les pixels de surface : mélanger le fond
                # déplacerait la forme du segment, donc changerait `masque_papyrus`, et on
                # comparerait deux surfaces au lieu de deux structures.
                melange = gris.copy()
                dedans = melange > 0
                valeurs = melange[dedans]
                np.random.default_rng(a.graine).shuffle(valeurs)
                melange[dedans] = valeurs
                t = signature(melange, a.taille_fenetre)
                t.update({"rouleau": "controle_melange", "carte": c.stem,
                          "reduction": a.reduire, "taille_fenetre": a.taille_fenetre})
                lignes.append(t)
                dire(f"  ↳ contrôle, pixels mélangés", t)
        tests = {}
        if a.controle_melange:
            reels = {l["carte"]: l for l in lignes if l["rouleau"] == "nos_cartes"}
            melanges = {l["carte"]: l for l in lignes if l["rouleau"] == "controle_melange"}
            for nom in sorted(reels):
                if nom not in melanges:
                    continue
                t = fisher_periodicite(reels[nom], melanges[nom])
                tests[nom] = t
                if t["p"] is None:
                    print(f"  {nom:44} pas de test — {t['raison']}")
                else:
                    print(f"  {nom:44} Fisher unilatéral {t['table']} : p = {t['p']:.4f}")
            # ⚠⚠ Le test GROUPÉ est déclaré avant la quatrième carte, et il est SECONDAIRE :
            # le test par carte reste le principal. Voir `fisher_periodicite_groupee`.
            #
            # ⚠⚠⚠ ET IL EXCLUT LES TÉMOINS, faute de quoi il se trompe de sujet. Le
            # 2026-08-28 la campagne a groupé nos quatre surfaces de `PHerc1447` AVEC le
            # témoin Scroll 1 — dont on sait déjà qu'il porte du texte — et a sorti
            # `[16, 8, 0, 24]`, dont la MOITIÉ du signal venait du témoin. La docstring de
            # `fisher_periodicite_groupee` disait « du même rouleau » et rien ne le
            # vérifiait : une précondition écrite est une précondition que quelqu'un
            # violera. C'est l'appelant qui sait lequel est un témoin, donc c'est lui qui
            # le nomme.
            temoins = {t.stem for t in a.temoin}
            sujets = [n for n in sorted(reels) if n in melanges and n not in temoins]
            ecartes = [n for n in sorted(reels) if n in temoins]
            for n in ecartes:
                print(f"  {'':44} ↳ {n} écarté du groupement (témoin)")
            groupe = fisher_periodicite_groupee([reels[n] for n in sujets],
                                                [melanges[n] for n in sujets])
            groupe["temoins_ecartes"] = ecartes
            tests["_groupe"] = groupe
            if groupe["p"] is None:
                print(f"  {'GROUPÉ (secondaire)':44} pas de test — {groupe['raison']}")
            else:
                print(f"  {'GROUPÉ (secondaire)':44} Fisher unilatéral {groupe['table']} "
                      f"sur {groupe['cartes']} cartes : p = {groupe['p']:.4f}")
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(_json.dumps({"cartes": lignes, "tests": tests},
                                          indent=2, ensure_ascii=False) + "\n")
            print(f"  écrit : {a.json}")
        return 0
    if not a.dossier:
        ap.error("nommer le dossier des cartes, --npy, ou --verifier")

    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None

    lignes = []
    for rouleau in sorted(p for p in a.dossier.iterdir() if p.is_dir()):
        cartes = sorted(list(rouleau.glob("*.jpg")) + list(rouleau.glob("*.png")))
        print(f"== {rouleau.name}  ({len(cartes)} cartes)")
        for c in cartes:
            try:
                im = Image.open(c).convert("L")
            except OSError:
                print(f"   ⚠ illisible : {c.name}")
                continue
            # ⚠ La reduction n'est pas une economie : a pleine resolution la texture du
            # papyrus domine l'autocorrelation et la periode d'ecriture disparait sous
            # elle. Le facteur est un PARAMETRE parce qu'il depend de la resolution du
            # scan, et il voyage dans le resultat.
            if a.reduire > 1:
                im = im.reduce(a.reduire)
            s = signature(np.asarray(im, dtype=np.uint8))
            s.update({"rouleau": rouleau.name, "carte": c.stem, "reduction": a.reduire})
            lignes.append(s)
        ls = [l for l in lignes if l["rouleau"] == rouleau.name]
        n = sum(1 for l in ls if l["part_periodique"] >= PART_ECRITE_MIN)
        print(f"   {n}/{len(ls)} cartes dont au moins "
              f"{PART_ECRITE_MIN:.0%} des fenêtres sont périodiques")

    if not lignes:
        print("aucune carte lue", file=sys.stderr)
        return 1

    print(f"\n  {'rouleau':<14} {'n':>3} {'écrites':>12} {'interligne méd.':>16} "
          f"{'trait méd.':>11} {'couverture méd.':>16}")
    print("  " + "-" * 78)
    par_rouleau: dict[str, list] = {}
    for l in lignes:
        par_rouleau.setdefault(l["rouleau"], []).append(l)
    resume = {}
    med = lambda xs: (sorted(xs)[len(xs) // 2] if xs else None)  # noqa: E731
    for r, ls in par_rouleau.items():
        ecrites = [l for l in ls if l["part_periodique"] >= PART_ECRITE_MIN]
        d = {"n": len(ls), "cartes_ecrites": len(ecrites),
             "part_periodique_mediane": med([l["part_periodique"] for l in ls]),
             "interligne_median_px": med([l["periode_px"] for l in ecrites
                                          if l["periode_px"]]),
             "trait_median_px": med([l["epaisseur_trait_px"] for l in ls
                                     if l["epaisseur_trait_px"]]),
             "couverture_mediane": med([l["couverture"] for l in ls]),
             "hauteur_mediane_px": med([l["hauteur_mediane_px"] for l in ls
                                        if l["hauteur_mediane_px"]])}
        resume[r] = d
        print(f"  {r:<14} {d['n']:>3} {len(ecrites):>7}/{len(ls):<4} "
              f"{str(d['interligne_median_px']):>16} {d['trait_median_px'] or 0:>11.1f} "
              f"{d['couverture_mediane']:>16.3f}")

    croisement = None
    if a.encre and a.encre.is_file():
        segs = json.loads(a.encre.read_text()).get("segments", [])
        croisement = croiser_encre(lignes, segs, a.cle_encre)
        if croisement.get("grandeurs"):
            print(f"\n  ⭐ TRANSPORT — chaque grandeur typographique retrouve-t-elle le "
                  f"classement du contraste d'encre publié ?")
            print(f"     {croisement['n']} segments appariés, partagés à la médiane du "
                  f"contraste ({croisement['seuil']:.3f}) : "
                  f"{croisement['n_faible']} faibles, {croisement['n_fort']} forts\n")
            print(f"     {'grandeur':<22} {'AUC':>6}  {'méd. faible':>12} "
                  f"{'méd. forte':>11}")
            for nom, g in sorted(croisement["grandeurs"].items(),
                                 key=lambda kv: -(kv[1]["auc"] or 0)):
                marque = ("  ⭐" if (g["auc"] or 0) >= 0.75 else
                          "  ⚠ INVERSE" if (g["auc"] or 1) <= 0.35 else "")
                print(f"     {nom:<22} {g['auc']:>6.3f}  {g['mediane_faible']:>12.3f} "
                      f"{g['mediane_forte']:>11.3f}{marque}")
            print("     (0,50 = la grandeur ne dit rien du contraste ; "
                  "sous 0,50 = elle dit le contraire)")
        else:
            print(f"\n  ⚠ croisement impossible : {croisement.get('raison')}")

    if a.json:
        a.json.write_text(json.dumps({"reduction": a.reduire, "resume": resume,
                                      "croisement_encre": croisement,
                                      "cartes": lignes}, indent=2, ensure_ascii=False)
                          + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
