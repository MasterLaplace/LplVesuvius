#!/usr/bin/env python3
"""Le pas normal, RACCROCHÉ à la matière du volume brut — la marche qui manquait.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `la_portee_des_piles_publiees` a mesuré que les piles de
surface publiées s'arrêtent à **129,6 µm** autour de leur surface, soit 0,956 feuille : elles
manquent la feuille voisine de 5,9 µm, donc **aucun raccrochage ne peut se bâtir dessus**. La
conclusion y était écrite : il faut le **volume brut**. Ce fichier le lit.

⭐ L'étalon a été posé deux tranches plus tôt et il est chiffré : `la_derive_est_elle_un_biais`
mesure que la meilleure longueur de pas CONSTANTE laisse **50,5 µm** d'erreur sur des paires
réservées, et que ces quatre cinquièmes-là sont une **dispersion locale**. Un meilleur nombre
ne les enlèvera pas. Passer sous 50 µm demande de redemander à la donnée où la feuille est
réellement — c'est-à-dire exactement ce que fait un raccrochage.

⚠⚠ CE QUI EST CIRCULAIRE ET CE QUI NE L'EST PAS. Les treize spires publiées ont elles-mêmes
été segmentées dans ce volume, donc « le raccrochage me rapproche de leur surface » n'est pas
une découverte indépendante : c'est deux lectures d'une même matière qui tombent d'accord. Ce
que la mesure ajoute est ailleurs, et c'est un nombre : **quelle PART de l'erreur résiduelle du
pas géométrique un raccrochage local enlève**. Le pas, lui, ne lit rien du volume ; c'est donc
bien une capacité nouvelle qu'on chiffre, pas un accord recopié.

⚠⚠ LE VOLUME EST VÉRIFIÉ, PAS SUPPOSÉ. Lire les bonnes coordonnées dans le mauvais volume est
la panne qui a coûté treize rendus noirs (`54`) : le nom du zarr porte l'horodatage du volume
**et** sa taille de voxel, et les deux sont confrontés à ce que les spires déclarent. Un volume
dont le nom ne correspond pas est refusé, jamais lu « au cas où ».

⚠⚠ LA CONVENTION EST MESURÉE. Une spire publiée est-elle posée sur une CRÊTE de matière ou dans
un CREUX entre deux feuilles ? Rien ne le dit, et se tromper inverse le raccrochage — il irait
chercher l'air. Le profil d'intensité autour des spires est donc cumulé sur des centaines de
points avant qu'aucun raccrochage n'ait lieu, et le nombre de points est rendu : un profil bâti
sur trois lignes n'est pas un profil, c'est un dessin (payé sur `la_portee_des_piles_publiees`,
où trois blocs isolés donnaient trois pics incompatibles).

⛔⛔ ET CE N'EST PAS LA MATIÈRE LA PLUS PROCHE QUI RACCROCHE, C'EST LA FORME D'UNE FEUILLE.
Mesuré : aller au MAXIMUM D'INTENSITÉ le plus proche rend 46,1 µm là où le pas seul en laisse
46,7 — c'est-à-dire **rien**. La crête est large de trente voxels ; un maximum s'y pose n'importe
où, et sur une seule ligne le bruit domine le contraste. Ce qui travaille est la **corrélation
normalisée** de la ligne avec un GABARIT : le profil d'une feuille entière, crête et creux
compris. Les deux contendants sont gardés côte à côte, parce que sans le premier rien ne dirait
ce qui, dans le raccrochage, fait le travail.

⚠⚠⚠ LE GABARIT EST LU SUR LA SPIRE DE DÉPART, ET C'EST CE QUI REND LA MESURE HONNÊTE. On se
tient sur la spire `k`, donc son profil est une donnée qu'on **a** ; celui de la spire `k+1`
serait la réponse. Un gabarit tiré de l'ensemble du corpus ferait fuiter la position des cibles
dans l'outil censé les trouver.

⚠⚠ LA FENÊTRE EST DÉRIVÉE, JAMAIS CHOISIE : une demi-épaisseur de feuille. Plus large, le
raccrochage a le droit d'attraper la feuille VOISINE, et il le fait — c'est un des témoins.

⚠ Le coût est rendu (blocs téléchargés, mébioctets) : une mesure dont le prix n'est pas dit
n'est pas reproductible, et un bloc de ce volume fait 2 Mio non compressés.

Usage :
    uv run python src/nappe/le_raccrochage_a_la_matiere.py --verifier
    uv run python src/nappe/le_raccrochage_a_la_matiere.py \\
        --json docs/mesures/le_raccrochage_a_la_matiere.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre", "tracecheck"):
    sys.path.insert(0, str(RACINE / "src" / _d))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
FRAGMENT = "PHerc0500P2"
ZARR = "20250526151718-2.215um-0.4m-111keV-masked.zarr"
WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"
CACHE = Path.home() / ".cache" / "lplvesuvius" / "blocs"

# ⚠ La boîte est un CHOIX D'ÉCONOMIE, pas un choix de résultat : elle est posée là où le plus
# grand nombre de spires se croisent, ce qui se décide sur la géométrie seule (`boite_riche`).
# Sa valeur est figée ici pour que la mesure soit rejouable sans re-balayer, et le balayage qui
# la produit reste dans le fichier — sinon le nombre publié serait tombé du ciel.
BOITE_CENTRE = (10615.0, 10571.0, 19831.0)
BOITE_COTE = 384.0


def url_du_volume(fragment: str = FRAGMENT, zarr: str = ZARR) -> str:
    """L'adresse du volume de scan brut."""
    return f"{BUCKET}/{fragment}/volumes/{zarr}"


def volume_declare(zarr: str = ZARR) -> tuple[str, float]:
    """L'horodatage et la taille de voxel que le NOM du zarr annonce.

    ⚠⚠ Le nom est la seule chose qui relie un tableau d'octets à un scan. Le lire plutôt que
    de le supposer est ce qui permet de refuser le mauvais volume avant d'en lire un voxel :
    des coordonnées de niveau 2 lues au niveau 0 tombent dans le vide et rendent « pas de
    matière » avec le même aplomb qu'une vraie mesure.
    """
    m = re.match(r"^(\d{14})-([0-9.]+)um[-.]", zarr)
    if m is None:
        raise RuntimeError(f"nom de zarr illisible : {zarr}")
    return m.group(1), float(m.group(2))


def accorde_aux_spires(zarr: str = ZARR, volume: str | None = None,
                       voxel_um: float | None = None) -> bool:
    """Le volume nommé est-il celui sur lequel les spires sont paramétrées ?"""
    if volume is None or voxel_um is None:
        from les_wraps_publies import VOLUME, VOXEL_UM  # noqa: PLC0415
        volume = VOLUME if volume is None else volume
        voxel_um = VOXEL_UM if voxel_um is None else voxel_um
    h, um = volume_declare(zarr)
    return h == volume and abs(um - voxel_um) < 1e-9


class CacheDisque:
    """Un cache de blocs adossé au disque, avec l'interface d'un dictionnaire.

    ⚠⚠ Un bloc de ce volume n'est PAS compressé : 128³ octets, soit 2 Mio par requête. Sans
    cache persistant, rejouer la mesure retélécharge des centaines de mébioctets — donc le
    chiffre publié dépendrait de la patience de qui le rejoue. Le compte de blocs réellement
    demandés au réseau est tenu à part (`neufs`) de celui des blocs servis : « la mesure a lu
    quarante blocs » et « la mesure a téléchargé quarante blocs » sont deux faits différents.

    ⚠ Une absence est mémorisée comme une absence (`None` sur disque, fichier vide) : sans ça
    un trou du dépôt est redemandé à chaque point qui le touche.
    """

    def __init__(self, racine: Path = CACHE, actif: bool = True) -> None:
        self.racine = racine
        self.actif = actif
        self.memoire: dict[str, np.ndarray | None] = {}
        self.neufs = 0
        self.octets = 0

    def _chemin(self, cle: str) -> Path:
        return self.racine / (cle.replace("/", "_") + ".npy")

    def __contains__(self, cle: str) -> bool:
        if cle in self.memoire:
            return True
        if not self.actif:
            return False
        c = self._chemin(cle)
        if not c.is_file():
            return False
        self.memoire[cle] = None if c.stat().st_size == 0 else np.load(c)
        return True

    def __getitem__(self, cle: str):
        return self.memoire[cle]

    def __setitem__(self, cle: str, bloc) -> None:
        self.memoire[cle] = bloc
        self.neufs += 1
        if bloc is not None:
            self.octets += int(bloc.nbytes)
        if not self.actif:
            return
        self.racine.mkdir(parents=True, exist_ok=True)
        c = self._chemin(cle)
        if bloc is None:
            c.write_bytes(b"")
        else:
            np.save(c, bloc)

    def cout(self) -> dict:
        return dict(blocs_telecharges=self.neufs,
                    mebioctets=round(self.octets / (1024 * 1024), 1),
                    blocs_en_memoire=len(self.memoire))


class Volume:
    """Le volume de scan, lu bloc par bloc, avec interpolation trilinéaire.

    ⚠⚠ L'ordre des axes est `(z, y, x)` et il est **vérifié contre la forme du tableau**, pas
    supposé : les points des spires sont écrits en `(x, y, z)`. Intervertir ne lève rien — ça
    lit un autre endroit du rouleau et rend un profil parfaitement plausible.

    ⚠ Les lectures sont **groupées par bloc** : point par point, huit coins par échantillon et
    des dizaines de milliers d'échantillons feraient de la mesure une boucle Python de plusieurs
    minutes pour des octets déjà en mémoire.
    """

    def __init__(self, url: str, meta: dict, cache, essais: int = 4) -> None:
        self.url = url
        self.meta = meta
        self.cache = cache
        self.forme = tuple(meta["shape"])
        self.taille = tuple(meta["chunks"])
        if len(self.forme) != 3:
            raise RuntimeError(f"tableau à {len(self.forme)} axes, attendu 3")
        self.absents = 0
        # ⚠⚠ LES REPRISES SONT COMPTÉES, PAS SEULEMENT FAITES. Un balayage qui a demandé
        # quarante reprises est un balayage dont le lien était mauvais ce jour-là, et c'est un
        # fait sur les conditions de la mesure. Payé le 2026-09-06 : un seul délai dépassé a
        # jeté deux cent trente-deux blocs déjà téléchargés et des minutes de marche.
        self.essais = max(1, int(essais))
        self.reprises = 0

    def _bloc(self, cz: int, cy: int, cx: int):
        import tracecheck as tc  # noqa: PLC0415

        cle = tc.chunk_key(self.meta, 0, cy, cx, cz)
        if cle in self.cache:
            return self.cache[cle]
        brut = raison = None
        for tentative in range(self.essais):
            brut, raison = tc.get_with_reason(f"{self.url}/{cle}", 120.0)
            # ⚠⚠ « absent du dépôt » et « le réseau n'a pas répondu » sont deux faits
            # différents. Seul un 404/403 autorise à mémoriser une absence ; mémoriser un
            # incident de réseau graverait un trou qui n'existe pas. Et un incident se
            # RÉESSAIE — il ne dit rien du contenu, donc rien ne justifie d'abandonner.
            if brut is not None or raison == "absent":
                break
            self.reprises += 1
            if tentative + 1 < self.essais:
                time.sleep(2.0 * (tentative + 1))
        if brut is None:
            if raison != "absent":
                raise RuntimeError(f"lecture impossible ({raison}) pour {cle} "
                                   f"après {self.essais} tentatives")
            self.cache[cle] = None
            return None
        n = self.taille[0] * self.taille[1] * self.taille[2]
        donnees = tc.decode(brut, self.meta, n)
        if donnees is None:
            raise RuntimeError(f"bloc illisible : {cle}")
        bloc = np.frombuffer(donnees, dtype=np.dtype(self.meta["dtype"])).reshape(self.taille)
        self.cache[cle] = bloc
        return bloc

    def voxels(self, zyx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Les valeurs entières en `(z, y, x)`, et le masque de ce qui a été lu."""
        zyx = np.asarray(zyx, dtype=np.int64).reshape(-1, 3)
        dedans = np.ones(len(zyx), dtype=bool)
        for axe in range(3):
            dedans &= (zyx[:, axe] >= 0) & (zyx[:, axe] < self.forme[axe])
        vals = np.zeros(len(zyx), dtype=np.float64)
        if not dedans.any():
            return vals, dedans
        idx = np.flatnonzero(dedans)
        ch = zyx[idx] // np.array(self.taille)
        cles, inverse = np.unique(ch, axis=0, return_inverse=True)
        for k, (cz, cy, cx) in enumerate(cles):
            bloc = self._bloc(int(cz), int(cy), int(cx))
            ou = idx[inverse == k]
            if bloc is None:
                self.absents += len(ou)
                dedans[ou] = False
                continue
            loc = zyx[ou] % np.array(self.taille)
            vals[ou] = bloc[loc[:, 0], loc[:, 1], loc[:, 2]]
        return vals, dedans

    def lire(self, xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """L'intensité trilinéaire en des points `(x, y, z)` fractionnaires.

        ⚠ Le voisin entier suffirait pour dire « il y a de la matière » ; il ne suffit pas pour
        placer un maximum. Un pic échantillonné au voxel le plus proche se déplace par sauts de
        2,2 µm le long d'une direction oblique — un vingtième de l'écart qu'on cherche à
        mesurer, versé en bruit pour rien.
        """
        xyz = np.asarray(xyz, dtype=np.float64).reshape(-1, 3)
        zyx = xyz[:, ::-1]
        base = np.floor(zyx)
        frac = zyx - base
        base = base.astype(np.int64)
        out = np.zeros(len(xyz))
        bon = np.ones(len(xyz), dtype=bool)
        for dz in (0, 1):
            for dy in (0, 1):
                for dx in (0, 1):
                    w = ((frac[:, 0] if dz else 1 - frac[:, 0])
                         * (frac[:, 1] if dy else 1 - frac[:, 1])
                         * (frac[:, 2] if dx else 1 - frac[:, 2]))
                    v, ok = self.voxels(base + np.array([dz, dy, dx]))
                    out += w * v
                    bon &= ok
        return out, bon


def le_long(points: np.ndarray, directions: np.ndarray, decalages: np.ndarray,
            volume: Volume) -> tuple[np.ndarray, np.ndarray]:
    """L'intensité le long de chaque normale, aux décalages demandés (en voxels).

    Rend un tableau `(points, décalages)` et son masque : une ligne dont un seul échantillon
    manque est écartée entière, parce qu'un profil troué déplace son propre maximum.
    """
    points = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    directions = np.asarray(directions, dtype=np.float64).reshape(-1, 3)
    decalages = np.asarray(decalages, dtype=np.float64).reshape(-1)
    q = points[:, None, :] + directions[:, None, :] * decalages[None, :, None]
    v, ok = volume.lire(q.reshape(-1, 3))
    v = v.reshape(len(points), len(decalages))
    ok = ok.reshape(len(points), len(decalages))
    return v, ok.all(axis=1)


def profil_autour(valeurs: np.ndarray) -> np.ndarray:
    """Le profil CUMULÉ : la médiane de l'intensité à chaque décalage, sur toutes les lignes.

    ⚠⚠ La médiane et non la moyenne : une ligne qui traverse un éclat dense tire une moyenne
    et ne bouge pas une médiane. Et le cumul est le point — sur `la_portee_des_piles_publiees`,
    trois blocs pris isolément donnaient trois pics à 66, 78 et 85 couches parce qu'un bloc ne
    voit qu'un morceau de feuille.
    """
    if valeurs.size == 0:
        return np.zeros(0)
    return np.median(valeurs, axis=0)


def pics(profil: np.ndarray, decalages: np.ndarray) -> np.ndarray:
    """Les décalages des maxima locaux stricts du profil."""
    if profil.size < 3:
        return np.zeros(0)
    interieur = np.arange(1, len(profil) - 1)
    est = (profil[interieur] > profil[interieur - 1]) & (profil[interieur] > profil[interieur + 1])
    return decalages[interieur][est]


def pas_entre_pics(profil: np.ndarray, decalages: np.ndarray) -> float | None:
    """L'écart médian entre deux crêtes successives du profil, en voxels.

    ⚠ C'est la mesure qui dit si le volume brut porte bien UNE crête par feuille : si le pas
    des crêtes valait la moitié de l'écart inter-feuilles, une feuille en montrerait deux
    (ses deux faces), et une fenêtre d'une demi-feuille contiendrait alors deux candidats.
    """
    p = pics(profil, decalages)
    if len(p) < 2:
        return None
    return float(np.median(np.diff(np.sort(p))))


def sommet(valeurs: np.ndarray, decalages: np.ndarray, sens: int = +1) -> np.ndarray:
    """Le décalage du meilleur échantillon de chaque ligne, affiné par parabole.

    `sens = +1` cherche un maximum d'intensité, `-1` un minimum.

    ⚠⚠ L'affinage parabolique n'est pas une coquetterie : l'échantillonnage se fait au voxel,
    donc sans lui le raccrochage ne peut atterrir que sur une grille de 2,2 µm le long d'une
    direction oblique. Aux bords de la fenêtre il n'y a pas trois points, donc le sommet y est
    rendu **tel quel** plutôt qu'extrapolé — un sommet au bord veut dire que la fenêtre est
    trop étroite, et c'est un fait qu'il faut pouvoir compter, pas lisser.
    """
    if valeurs.size == 0:
        return np.zeros(0)
    v = valeurs * sens
    i = np.argmax(v, axis=1)
    t = decalages[i].astype(np.float64)
    inte = (i > 0) & (i < len(decalages) - 1)
    if inte.any():
        j = i[inte]
        y0 = v[inte, j - 1]
        y1 = v[inte, j]
        y2 = v[inte, j + 1]
        den = y0 - 2 * y1 + y2
        d = np.where(np.abs(den) > 1e-12, 0.5 * (y0 - y2) / np.where(den == 0, 1.0, den), 0.0)
        d = np.clip(d, -1.0, 1.0)
        pas = float(np.median(np.diff(decalages))) if len(decalages) > 1 else 1.0
        t[inte] = decalages[j] + d * pas
    return t


def au_bord(valeurs: np.ndarray, sens: int = +1) -> np.ndarray:
    """Quelles lignes ont leur sommet collé au bord de la fenêtre."""
    if valeurs.size == 0:
        return np.zeros(0, dtype=bool)
    i = np.argmax(valeurs * sens, axis=1)
    return (i == 0) | (i == valeurs.shape[1] - 1)


def lisser(profil: np.ndarray, largeur: int) -> np.ndarray:
    """Le profil lissé à l'échelle demandée, la ride d'un échantillon annulée exactement.

    ⚠⚠ CHERCHER UN PIC SUR UN PROFIL NON LISSÉ TROUVE DU BRUIT. Mesuré : la première version
    de ce fichier rapportait un pas de crêtes de **8,9 µm**, soit quatre voxels — c'est-à-dire
    l'ondulation de l'échantillonnage, pas une feuille. Un profil qui n'a pas été lissé à
    l'échelle de ce qu'on y cherche rend un chiffre parfaitement précis et parfaitement faux.

    ⚠⚠ ET UN CRÉNEAU SEUL NE SUFFIT PAS, ce que la batterie a montré avant l'usage réel : une
    ride qui alterne d'un échantillon à l'autre est **exactement la fréquence de Nyquist**, et
    un créneau de longueur IMPAIRE en laisse toujours un neuvième — assez pour recréer des
    crêtes sur un sommet plat. Le noyau `[1, 2, 1]` ajouté au créneau l'annule **exactement**
    (1 − 2 + 1 = 0) et garde le profil centré. Ce n'est pas un réglage : c'est la seule forme
    qui fait ce que la docstring promet.
    """
    if profil.size == 0:
        return profil.astype(np.float64)
    noyau = np.ones(max(1, int(largeur))) / float(max(1, int(largeur)))
    noyau = np.convolve(noyau, np.array([1.0, 2.0, 1.0]) / 4.0)
    pad = len(noyau) // 2
    etendu = np.pad(profil.astype(np.float64), pad, mode="edge")
    return np.convolve(etendu, noyau, mode="same")[pad:pad + len(profil)]


def correler(lignes: np.ndarray, gab: np.ndarray,
             decalages: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """La corrélation normalisée de chaque ligne avec le gabarit, à chaque position.

    ⚠⚠ NORMALISÉE, ET LES DEUX MOYENNES RETIRÉES. Sans ça la corrélation récompense
    l'endroit le plus BRILLANT plutôt que celui qui a la bonne FORME — donc elle rejoue le
    maximum brut, dont ce fichier mesure justement qu'il ne raccroche rien.

    Rend `(corrélations, décalages du centre du gabarit)`, en voxels et dans le repère du
    point prévu : un décalage nul veut dire « le gabarit se pose exactement là où le pas a
    laissé le point ».
    """
    n = len(gab)
    if n == 0 or lignes.ndim != 2 or lignes.shape[1] < n:
        return np.zeros((len(lignes), 0)), np.zeros(0)
    g = gab - gab.mean()
    ng = np.linalg.norm(g)
    depart = np.arange(lignes.shape[1] - n + 1)
    out = np.empty((len(lignes), len(depart)))
    for k, s in enumerate(depart):
        seg = lignes[:, s:s + n]
        seg = seg - seg.mean(axis=1, keepdims=True)
        den = np.linalg.norm(seg, axis=1) * ng
        out[:, k] = (seg @ g) / np.where(den > 1e-9, den, 1.0)
    centre = decalages[depart] + (n - 1) / 2.0 * float(np.median(np.diff(decalages)))
    return out, centre


def decalage_retenu(corr: np.ndarray, centres: np.ndarray) -> np.ndarray:
    """Le décalage qui maximise la corrélation, affiné par parabole.

    ⚠ Même règle que `sommet` : au bord il n'y a pas trois points, donc le décalage y est
    rendu tel quel. Un raccrochage qui bute sur le bord de sa fenêtre n'a pas trouvé sa
    feuille, il a trouvé la limite qu'on lui a donnée — et c'est comptable.
    """
    if corr.size == 0:
        return np.zeros(len(corr))
    i = np.argmax(corr, axis=1)
    t = centres[i].astype(np.float64)
    inte = (i > 0) & (i < corr.shape[1] - 1)
    if inte.any():
        j = i[inte]
        y0, y1, y2 = corr[inte, j - 1], corr[inte, j], corr[inte, j + 1]
        den = y0 - 2 * y1 + y2
        d = np.where(np.abs(den) > 1e-12, 0.5 * (y0 - y2) / np.where(den == 0, 1.0, den), 0.0)
        pas = float(np.median(np.diff(centres))) if len(centres) > 1 else 1.0
        t[inte] = centres[j] + np.clip(d, -1.0, 1.0) * pas
    return t


def accorder_les_voisins(t: np.ndarray, valide: np.ndarray,
                         minimum: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Chaque décalage remplacé par la médiane de son voisinage de grille 3×3.

    ⚠⚠ CE N'EST PAS UN RÉGLAGE, C'EST UN ÉNONCÉ SUR LA MATIÈRE : une feuille de papyrus est
    lisse à l'échelle de trois cellules de grille, donc deux voisins qui se raccrochent à
    quinze micromètres l'un de l'autre ne peuvent pas avoir raison tous les deux. La médiane
    est ce qui laisse la majorité corriger l'isolé — une moyenne se laisserait tirer par lui.

    ⚠ Une cellule dont moins de `minimum` voisins sont valides est **écartée**, pas accordée
    sur ce qui reste : au bord d'un trou, deux voisins ne font pas une majorité, et prendre
    leur médiane fabriquerait une confiance que le voisinage ne porte pas.

    ⚠ Le voisinage se prend dans la GRILLE, jamais dans l'espace : deux cellules voisines dans
    la grille sont voisines sur la feuille, alors que deux points proches dans le volume
    peuvent appartenir à deux spires différentes — c'est toute la difficulté du rouleau.
    """
    h, w = t.shape
    empile, masque = [], []
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            dec = np.full((h, w), np.nan)
            m = np.zeros((h, w), dtype=bool)
            su = slice(max(0, du), h + min(0, du))
            sv = slice(max(0, dv), w + min(0, dv))
            tu = slice(max(0, -du), h + min(0, -du))
            tv = slice(max(0, -dv), w + min(0, -dv))
            dec[su, sv] = t[tu, tv]
            m[su, sv] = valide[tu, tv]
            empile.append(np.where(m, dec, np.nan))
            masque.append(m)
    pile = np.stack(empile)
    combien = np.stack(masque).sum(axis=0)
    assez = valide & (combien >= minimum)
    out = np.full((h, w), np.nan)
    if assez.any():
        import warnings  # noqa: PLC0415
        with warnings.catch_warnings():
            # ⚠ Une colonne entièrement vide est un cas NORMAL (une cellule hors du masque) ;
            # elle est écartée par `assez` juste après. L'avertissement de numpy porterait
            # donc sur ce que la fonction traite déjà, et noierait ceux qui comptent.
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nanmedian(pile, axis=0)
        out[assez] = med[assez]
    return out, assez


def boite_riche(nuages: dict[int, np.ndarray], cote: float,
                reference: int = 7, essais: int = 40) -> tuple[np.ndarray, dict[int, int]]:
    """Où poser une boîte de ce côté pour qu'elle traverse le plus de spires possible.

    ⚠⚠ Ce balayage ne regarde QUE la géométrie — combien de points de chaque spire tombent
    dedans — et jamais une erreur de raccrochage. Choisir la boîte sur le résultat serait
    choisir l'endroit où la mesure est belle.
    """
    ref = nuages[reference]
    meilleur = None
    for i in range(0, len(ref), max(1, len(ref) // essais)):
        c = ref[i]
        lo, hi = c - cote / 2, c + cote / 2
        n = {r: int(((p >= lo) & (p <= hi)).all(axis=1).sum()) for r, p in nuages.items()}
        pres = sum(1 for v in n.values() if v >= 30)
        tot = sum(n.values())
        if meilleur is None or (pres, tot) > (meilleur[0], meilleur[1]):
            meilleur = (pres, tot, c, n)
    return meilleur[2], meilleur[3]


def _grilles(rangs: list[int] | None = None) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    from le_pas_normal_atteint_la_spire import grille  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    out = {}
    for w in wraps_du_fragment():
        if rangs is not None and w["rang"] not in rangs:
            continue
        g = grille(w, VOLUME, VOXEL_UM)
        if g is not None:
            out[w["rang"]] = g
    return out


def mesurer(echantillon: int = 2000, graine: int = 42, minimum_par_spire: int = 30,
            cache_actif: bool = True) -> dict:
    """Le pas normal, avec et sans raccrochage, jugé sur les spires publiées.

    ⚠⚠ UNE PAIRE N'EST RETENUE QUE SI LA CIBLE PASSE DANS LA BOÎTE, et le critère est
    **géométrique** : la spire d'arrivée doit y avoir au moins `minimum_par_spire` points.
    Sans lui, la paire 10→11 entrait avec une erreur de mille micromètres — non parce que le
    raccrochage échoue, mais parce que la spire 11 publiée ne couvre pas cette région. Écarter
    sur l'erreur aurait été choisir sur le résultat ; écarter sur la présence ne l'est pas.
    """
    from le_pas_normal_atteint_la_spire import distance_a, normales  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM  # noqa: PLC0415

    import tracecheck as tc  # noqa: PLC0415

    if not accorde_aux_spires():
        raise RuntimeError(f"le volume {ZARR} n'est pas celui des spires ({VOLUME})")
    if not WRAPS.is_file():
        raise RuntimeError(f"mesure absente : {WRAPS} — lancer les_wraps_publies d'abord")
    lu = json.loads(WRAPS.read_text())
    ecart_um = float(lu["resume"]["1"]["mediane_um"])
    pas_vx = ecart_um / VOXEL_UM
    # ⚠⚠ DÉRIVÉE, JAMAIS CHOISIE : une demi-épaisseur de feuille est la seule largeur où
    # exactement une feuille est à portée. Plus large, la voisine entre dans la fenêtre — et
    # c'est un des témoins.
    demi_vx = pas_vx / 2.0
    demi_gab = round(demi_vx / 2.0)

    url = url_du_volume()
    meta = tc.array_meta(url, 0, 120)
    cache = CacheDisque(actif=cache_actif)
    vol = Volume(url, meta, cache)

    grilles = _grilles()
    nuages = {r: a[ok] for r, (a, ok) in grilles.items()}
    centre = np.array(BOITE_CENTRE)
    lo, hi = centre - BOITE_COTE / 2, centre + BOITE_COTE / 2

    rng = np.random.default_rng(graine)
    t_gab = np.arange(-demi_gab, demi_gab + 1e-9, 1.0)
    t_ligne = np.arange(-(demi_vx + demi_gab), demi_vx + demi_gab + 1e-9, 1.0)
    t_large = np.arange(-(2 * demi_vx + demi_gab), 2 * demi_vx + demi_gab + 1e-9, 1.0)

    convention, lignes, ecartees = [], [], []
    for r in sorted(grilles):
        if r + 1 not in grilles:
            continue
        a, ok = grilles[r]
        n, bon = normales(a, ok)
        dans = bon & ((a >= lo) & (a <= hi)).all(axis=-1)
        idx = np.argwhere(dans)
        cible = nuages[r + 1]
        cible_dans = int(((cible >= lo) & (cible <= hi)).all(axis=1).sum())
        if len(idx) < minimum_par_spire or cible_dans < minimum_par_spire:
            ecartees.append(dict(de=r, vers=r + 1, source_dans_la_boite=int(len(idx)),
                                 cible_dans_la_boite=cible_dans))
            continue
        # ⚠⚠ LE SOUS-RECTANGLE, PAS UN TIRAGE. Un tirage aléatoire garde la même erreur
        # médiane et détruit le VOISINAGE — donc il rend l'accord entre voisins
        # inmesurable. Ce qui est prélevé ici est la portion de grille qui tombe dans la
        # boîte, cellules contiguës comprises.
        u0, u1 = int(idx[:, 0].min()), int(idx[:, 0].max()) + 1
        v0, v1 = int(idx[:, 1].min()), int(idx[:, 1].max()) + 1
        if echantillon and (u1 - u0) * (v1 - v0) > echantillon:
            # ⚠ Un pas de grille RÉDUIT le rectangle sans casser l'adjacence : des cellules
            # à deux pas restent des voisines sur la feuille, deux points tirés au hasard
            # ne le sont pas.
            k = int(np.ceil(np.sqrt((u1 - u0) * (v1 - v0) / echantillon)))
        else:
            k = 1
        sous = (slice(u0, u1, k), slice(v0, v1, k))
        forme = a[sous].shape[:2]
        m_sous = dans[sous]
        if int(m_sous.sum()) < minimum_par_spire:
            ecartees.append(dict(de=r, vers=r + 1, cellules_du_sous_rectangle=int(m_sous.sum())))
            continue
        cellules = np.argwhere(m_sous)
        p = a[sous][m_sous]
        d = n[sous][m_sous]

        # --- le gabarit : la forme d'une feuille, lue autour de la surface de DÉPART ---
        # ⚠⚠ IL NE SAIT RIEN DE LA CIBLE. On se tient sur la spire `r`, donc son profil est
        # une donnée qu'on a ; celui de la spire `r+1` serait la réponse.
        vg, okg = le_long(p, d, t_gab, vol)
        if okg.sum() < minimum_par_spire:
            ecartees.append(dict(de=r, vers=r + 1, lignes_lisibles=int(okg.sum())))
            continue
        gab = profil_autour(vg[okg])
        convention.append(dict(spire=r, lignes=int(okg.sum())))

        # --- le sens, unique bit de supervision, fixé une fois et déclaré ---
        sortant = float(np.median(distance_a(p + d * pas_vx, cible, VOXEL_UM)))
        rentrant = float(np.median(distance_a(p - d * pas_vx, cible, VOXEL_UM)))
        sens = 1.0 if sortant <= rentrant else -1.0
        gab_oriente = gab if sens > 0 else gab[::-1]
        prevu = p + d * (sens * pas_vx)
        dd = d * sens

        v, okv = le_long(prevu, dd, t_ligne, vol)
        vlarge, oklarge = le_long(prevu, dd, t_large, vol)
        garde = okv & oklarge
        if garde.sum() < minimum_par_spire:
            ecartees.append(dict(de=r, vers=r + 1, lignes_lisibles=int(garde.sum())))
            continue
        P, D = prevu[garde], dd[garde]
        L, Llarge = v[garde], vlarge[garde]
        cel = cellules[garde]

        def dist(q):
            return distance_a(q, cible, VOXEL_UM)

        corr, centres = correler(L, gab_oriente, t_ligne)
        t_racc = decalage_retenu(corr, centres)
        # --- témoin : le gabarit mélangé. Même géométrie, même fenêtre, même recherche ;
        #     seule la FORME cherchée est détruite. C'est le plancher de bruit.
        corr_m, _ = correler(L, rng.permuted(gab_oriente), t_ligne)
        t_mel = decalage_retenu(corr_m, centres)
        # --- témoin : la fenêtre d'une feuille entière, où la voisine est à portée ---
        corr_l, centres_l = correler(Llarge, gab_oriente, t_large)
        t_large_ret = decalage_retenu(corr_l, centres_l)
        # --- contendant : le maximum brut d'intensité, sans forme ---
        milieu = (len(t_ligne) - 1) // 2
        fen = slice(milieu - int(demi_vx), milieu + int(demi_vx) + 1)
        t_brut = sommet(L[:, fen], t_ligne[fen], +1)
        # --- témoin : raccrocher SANS avoir bougé doit ne rien déplacer ---
        vsp, oksp = le_long(p, d * sens, t_ligne, vol)
        corr_sp, _ = correler(vsp[oksp], gab_oriente, t_ligne)
        t_sur_place = decalage_retenu(corr_sp, centres)

        champ = np.full(forme, np.nan)
        champ[cel[:, 0], cel[:, 1]] = t_racc
        valide = np.zeros(forme, dtype=bool)
        valide[cel[:, 0], cel[:, 1]] = True
        accorde, assez = accorder_les_voisins(champ, valide)
        pris_acc = assez[cel[:, 0], cel[:, 1]]
        t_acc = accorde[cel[:, 0], cel[:, 1]]
        # ⚠ Le témoin de l'accord : mélanger le champ de décalages avant de l'accorder. La
        # médiane de neuf valeurs sans rapport reste une médiane — donc si l'accord aidait
        # par le seul fait de moyenner, ce témoin aiderait autant.
        melange_champ = champ.copy()
        vals = melange_champ[valide]
        melange_champ[valide] = rng.permutation(vals)
        acc_mel = accorder_les_voisins(melange_champ, valide)[0][cel[:, 0], cel[:, 1]]

        e_nul = dist(p)
        e_pas = dist(P)
        e_racc = dist(P + D * t_racc[:, None])
        e_mel = dist(P + D * t_mel[:, None])
        e_large = dist(P + D * t_large_ret[:, None])
        e_brut = dist(P + D * t_brut[:, None])
        e_acc = (dist(P[pris_acc] + D[pris_acc] * t_acc[pris_acc][:, None])
                 if pris_acc.any() else np.array([np.nan]))
        e_acc_mel = (dist(P[pris_acc] + D[pris_acc] * acc_mel[pris_acc][:, None])
                     if pris_acc.any() else np.array([np.nan]))

        lignes.append(dict(
            de=r, vers=r + 1, cellules=int(garde.sum()), sens="+" if sens > 0 else "-",
            sur_place_um=round(float(np.median(e_nul)), 1),
            pas_seul_um=round(float(np.median(e_pas)), 1),
            raccroche_um=round(float(np.median(e_racc)), 1),
            raccroche_p90_um=round(float(np.percentile(e_racc, 90)), 1),
            accorde_um=round(float(np.nanmedian(e_acc)), 1),
            accorde_p90_um=round(float(np.nanpercentile(e_acc, 90)), 1),
            accorde_cellules=int(pris_acc.sum()),
            temoin_accord_melange_um=round(float(np.nanmedian(e_acc_mel)), 1),
            temoin_accord_melange_p90_um=round(float(np.nanpercentile(e_acc_mel, 90)), 1),
            temoin_gabarit_melange_um=round(float(np.median(e_mel)), 1),
            temoin_fenetre_large_um=round(float(np.median(e_large)), 1),
            contendant_maximum_brut_um=round(float(np.median(e_brut)), 1),
            deplacement_median_um=round(float(np.median(np.abs(t_racc))) * VOXEL_UM, 1),
            deplacement_sur_place_um=round(float(np.median(np.abs(t_sur_place))) * VOXEL_UM, 1),
            decalages_au_bord=int(((np.argmax(corr, axis=1) == 0)
                                   | (np.argmax(corr, axis=1) == corr.shape[1] - 1)).sum()),
            profil_de_depart=[round(float(x), 2) for x in gab],
        ))

    if not lignes:
        raise RuntimeError("aucune paire mesurable dans la boîte")

    gabs = np.array([e["profil_de_depart"] for e in lignes])
    prof = np.median(gabs, axis=0)
    prof_lisse = lisser(prof, max(3, demi_gab // 2))
    i_max = int(np.argmax(prof_lisse))
    i_min = int(np.argmin(prof_lisse))

    def med(cle):
        return round(float(np.median([e[cle] for e in lignes])), 1)

    r = dict(
        fragment=FRAGMENT, volume=VOLUME, voxel_um=VOXEL_UM, zarr=ZARR, volume_accorde=True,
        boite=dict(centre=list(BOITE_CENTRE), cote_voxels=BOITE_COTE),
        ecart_lu_um=ecart_um, pas_en_voxels=round(pas_vx, 2),
        demi_fenetre_um=round(demi_vx * VOXEL_UM, 1),
        demi_gabarit_um=round(demi_gab * VOXEL_UM, 1),
        echantillon_par_paire=echantillon,
        paires=len(lignes), paires_ecartees=ecartees,
        convention=dict(
            lignes=int(sum(c["lignes"] for c in convention)), spires=len(convention),
            decalages_voxels=t_gab.tolist(),
            profil=[round(float(x), 2) for x in prof],
            profil_lisse=[round(float(x), 2) for x in prof_lisse],
            crete_um=round(float(t_gab[i_max]) * VOXEL_UM, 1),
            creux_um=round(float(t_gab[i_min]) * VOXEL_UM, 1),
            contraste=round(float(prof_lisse[i_max] - prof_lisse[i_min]), 1),
        ),
        lignes=lignes,
        sur_place_median_um=med("sur_place_um"),
        pas_seul_median_um=med("pas_seul_um"),
        raccroche_median_um=med("raccroche_um"),
        temoin_gabarit_melange_median_um=med("temoin_gabarit_melange_um"),
        temoin_fenetre_large_median_um=med("temoin_fenetre_large_um"),
        contendant_maximum_brut_median_um=med("contendant_maximum_brut_um"),
        accorde_median_um=med("accorde_um"),
        accorde_p90_median_um=med("accorde_p90_um"),
        raccroche_p90_median_um=med("raccroche_p90_um"),
        temoin_accord_melange_median_um=med("temoin_accord_melange_um"),
        temoin_accord_melange_p90_median_um=med("temoin_accord_melange_p90_um"),
        deplacement_sur_place_median_um=med("deplacement_sur_place_um"),
        cout=cache.cout() | dict(voxels_absents=vol.absents, reprises_reseau=vol.reprises),
    )
    r["paires_ameliorees"] = sum(1 for e in lignes if e["raccroche_um"] < e["pas_seul_um"])
    r["paires_ameliorees_accord"] = sum(1 for e in lignes if e["accorde_um"] < e["pas_seul_um"])
    r["bat_laccord_melange"] = bool(
        r["accorde_median_um"] < r["temoin_accord_melange_median_um"])
    r["laccord_ajoute"] = bool(r["accorde_median_um"] < r["raccroche_median_um"])
    r["laccord_bat_son_temoin_sur_la_queue"] = bool(
        r["accorde_p90_median_um"] < r["temoin_accord_melange_p90_median_um"])
    # ⚠ Diagnostic, PAS un filtre : une paire dont le pas seul dépasse déjà la demi-fenêtre a
    # sa feuille hors de portée du raccrochage, quoi qu'il lise. Le chiffre publié plus haut
    # ne les écarte pas — les écarter sur leur erreur serait choisir sur le résultat.
    r["paires_hors_de_portee"] = [e["de"] for e in lignes
                                  if e["pas_seul_um"] > r["demi_fenetre_um"]]
    r["gain_du_raccrochage_um"] = round(r["pas_seul_median_um"] - r["raccroche_median_um"], 1)
    r["part_de_lerreur_enlevee"] = (
        round(r["gain_du_raccrochage_um"] / r["pas_seul_median_um"], 4)
        if r["pas_seul_median_um"] else None)
    # ⚠⚠ L'ÉTALON N'EST PAS CHOISI : c'est l'erreur que laisse la MEILLEURE longueur de pas
    # constante sur des paires réservées (`la_derive_est_elle_un_biais`). Le battre veut dire
    # faire ce qu'aucun nombre transporté ne peut faire.
    r["etalon_um"] = _etalon_um()
    r["passe_sous_letalon"] = bool(r["raccroche_median_um"] < r["etalon_um"])
    r["bat_le_gabarit_melange"] = bool(
        r["raccroche_median_um"] < r["temoin_gabarit_melange_median_um"])
    r["bat_la_fenetre_large"] = bool(
        r["raccroche_median_um"] < r["temoin_fenetre_large_median_um"])
    r["bat_le_maximum_brut"] = bool(
        r["raccroche_median_um"] < r["contendant_maximum_brut_median_um"])
    return r


def _etalon_um(defaut: float = 50.5) -> float:
    """L'erreur que laisse la meilleure longueur de pas CONSTANTE, sur des paires réservées."""
    c = RACINE / "docs" / "mesures" / "la_derive_est_elle_un_biais.json"
    if not c.is_file():
        return defaut
    d = json.loads(c.read_text())
    return round(min(e["erreur_um"] for e in d["balayage_reserve"]), 1)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- le nom du volume, lu et confronté ---
    h, um = volume_declare(ZARR)
    v("le nom du zarr porte l'horodatage du volume", h == "20250526151718", h)
    v("... et sa taille de voxel", um == 2.215, str(um))
    v("le volume est celui sur lequel les spires sont paramétrées", accorde_aux_spires())
    # ⚠⚠ LE TÉMOIN QUI COMPTE : un autre volume du même fragment DOIT être refusé, sinon la
    # vérification est satisfaite par tout ce qu'on lui donne.
    v("un autre volume du même fragment est refusé",
      not accorde_aux_spires("20250528085330-4.317um-1.2m-111keV-masked.zarr"))
    v("... et un nom illisible lève au lieu de deviner",
      _leve(lambda: volume_declare("volume.zarr")))

    # --- le lecteur, sur un volume fabriqué dont on connaît chaque octet ---
    forme = (32, 32, 32)
    bloc = np.zeros(forme, dtype=np.uint8)
    zz, yy, xx = np.meshgrid(*[np.arange(n) for n in forme], indexing="ij")
    bloc[:] = (zz + 2 * yy + 3 * xx) % 251
    faux_meta = dict(shape=list(forme), chunks=[16, 16, 16], dtype="|u1",
                     dimension_separator="/", compressor=None)

    class VolumeFictif(Volume):
        def _bloc(self, cz, cy, cx):
            return bloc[cz * 16:(cz + 1) * 16, cy * 16:(cy + 1) * 16, cx * 16:(cx + 1) * 16]

    vf = VolumeFictif("", faux_meta, {})
    val, ok = vf.voxels(np.array([[1, 2, 3], [17, 18, 19]]))
    v("le lecteur rend la valeur du volume, bloc par bloc",
      ok.all() and val[0] == bloc[1, 2, 3] and val[1] == bloc[17, 18, 19],
      f"{val} contre {bloc[1, 2, 3]} {bloc[17, 18, 19]}")
    # ⚠⚠ L'ORDRE DES AXES : les points arrivent en (x, y, z) et le volume est indexé en
    # (z, y, x). Une inversion ne lève pas, elle lit ailleurs.
    lus, _ = vf.lire(np.array([[3.0, 2.0, 1.0]]))
    v("un point (x, y, z) est lu à (z, y, x)", abs(lus[0] - bloc[1, 2, 3]) < 1e-9,
      f"{lus[0]} contre {bloc[1, 2, 3]}")
    mi, _ = vf.lire(np.array([[3.5, 2.0, 1.0]]))
    v("... et l'interpolation trilinéaire rend le milieu de deux voxels",
      abs(mi[0] - 0.5 * (float(bloc[1, 2, 3]) + float(bloc[1, 2, 4]))) < 1e-9, str(mi[0]))
    hors, dedans = vf.voxels(np.array([[-1, 0, 0], [0, 0, 40]]))
    v("hors du volume n'est pas « pas de matière »", not dedans.any(), str(hors))

    # --- un profil dont on connaît le pic ---
    dec = np.arange(-20.0, 20.1, 1.0)
    lam = np.zeros((3, len(dec)))
    for k in range(3):
        lam[k] = 50 + 100 * np.exp(-((dec - 4.0) ** 2) / 8.0)
    prof = profil_autour(lam)
    v("le profil cumulé garde le pic de ses lignes", abs(dec[int(np.argmax(prof))] - 4.0) < 1e-9)
    t = sommet(lam, dec, +1)
    v("le sommet retrouve le pic", np.allclose(t, 4.0, atol=0.05), str(t[:1]))
    # ⚠⚠ L'AFFINAGE DOIT AJOUTER QUELQUE CHOSE : un pic entre deux échantillons doit être
    # rendu avec sa fraction, sinon la parabole ne sert à rien et personne ne le verrait.
    lam2 = 50 + 100 * np.exp(-((dec - 4.5) ** 2) / 8.0)[None, :]
    t2 = sommet(lam2, dec, +1)
    v("... y compris entre deux échantillons", 4.3 < float(t2[0]) < 4.7, str(t2[0]))
    v("le creux se cherche dans l'autre sens",
      abs(float(sommet(-lam2 + 200, dec, -1)[0]) - float(t2[0])) < 0.2)
    v("un sommet collé au bord est signalé",
      bool(au_bord(np.tile(np.linspace(0, 1, len(dec)), (2, 1)), +1).all()))
    v("... et un sommet intérieur ne l'est pas", not bool(au_bord(lam, +1).any()))

    # --- les crêtes et leur pas ---
    reg = 50 + 40 * np.cos(2 * np.pi * dec / 10.0)
    v("le pas des crêtes retrouve la période", abs(pas_entre_pics(reg, dec) - 10.0) < 1e-6,
      str(pas_entre_pics(reg, dec)))
    v("un profil plat n'a pas de pas de crêtes", pas_entre_pics(np.ones(len(dec)), dec) is None)

    # --- le long d'une direction, dans le volume fictif ---
    p = np.array([[8.0, 8.0, 8.0]])
    d = np.array([[1.0, 0.0, 0.0]])
    vv, okl = le_long(p, d, np.array([0.0, 1.0, 2.0]), vf)
    v("le parcours suit la direction demandée",
      okl.all() and np.allclose(vv[0], [bloc[8, 8, 8], bloc[8, 8, 9], bloc[8, 8, 10]]), str(vv))
    # ⚠ Une ligne qui sort du volume est écartée ENTIÈRE : un profil troué déplace son maximum.
    _, okd = le_long(np.array([[31.0, 8.0, 8.0]]), d, np.array([0.0, 4.0]), vf)
    v("une ligne qui sort du volume est écartée entière", not okd.any())

    # --- la reprise d'un incident de réseau ---
    # ⚠⚠⚠ CE QUI DOIT ÊTRE RÉESSAYÉ ET CE QUI NE DOIT PAS L'ÊTRE. Un délai dépassé ne dit
    # RIEN du contenu, donc il se réessaie ; une absence est une réponse, donc elle se
    # mémorise du premier coup. Confondre les deux fait soit jeter un balayage entier pour un
    # hoquet, soit marteler le dépôt pour des blocs qui n'existent pas.
    import tracecheck as tc_  # noqa: PLC0415

    vrai_get = tc_.get_with_reason
    vrai_decode = tc_.decode
    try:
        etat = {"n": 0}

        def faux_get(url, timeout):
            etat["n"] += 1
            return (None, "delai depasse") if etat["n"] < 3 else (b"x" * 8, None)

        tc_.get_with_reason = faux_get
        tc_.decode = lambda raw, meta, n: b"\x07" * n
        petitmeta = dict(shape=[16, 16, 16], chunks=[16, 16, 16], dtype="|u1",
                         dimension_separator="/", compressor=None)
        vr = Volume("", petitmeta, {}, essais=4)
        val, ok_ = vr.voxels(np.array([[0, 0, 0]]))
        v("un délai dépassé est réessayé, pas abandonné", bool(ok_.all()) and val[0] == 7,
          f"{val} après {vr.reprises} reprises")
        v("... et les reprises sont comptées", vr.reprises == 2, str(vr.reprises))
        etat["n"] = -10 ** 6
        vr2 = Volume("", petitmeta, {}, essais=2)
        v("... mais un délai qui persiste LÈVE, il ne devient pas une absence",
          _leve(lambda: vr2.voxels(np.array([[0, 0, 0]]))))
        etat["n"] = 0
        tc_.get_with_reason = lambda url, timeout: (None, "absent")
        vr3 = Volume("", petitmeta, {}, essais=4)
        _, ok3 = vr3.voxels(np.array([[0, 0, 0]]))
        v("une absence n'est PAS réessayée", vr3.reprises == 0 and not ok3.any(),
          str(vr3.reprises))
    finally:
        tc_.get_with_reason = vrai_get
        tc_.decode = vrai_decode

    # --- le cache : ce qu'il sert et ce qu'il a téléchargé sont deux comptes ---
    import tempfile  # noqa: PLC0415
    with tempfile.TemporaryDirectory() as tmp:
        c = CacheDisque(Path(tmp))
        v("un bloc inconnu n'est pas dans le cache", "0/0/0" not in c)
        c["0/0/0"] = bloc
        v("... puis il y est", "0/0/0" in c and np.array_equal(c["0/0/0"], bloc))
        c2 = CacheDisque(Path(tmp))
        v("un cache neuf relit le bloc depuis le disque",
          "0/0/0" in c2 and np.array_equal(c2["0/0/0"], bloc))
        v("... sans le compter comme téléchargé", c2.cout()["blocs_telecharges"] == 0)
        c["0/0/1"] = None
        c3 = CacheDisque(Path(tmp))
        v("une absence est mémorisée comme une absence",
          "0/0/1" in c3 and c3["0/0/1"] is None)

    # --- le lissage, et ce qu'il empêche ---
    td = np.arange(-20.0, 20.1, 1.0)
    bosse = 40 * np.exp(-(td ** 2) / 60.0)
    ride = bosse + 8.0 * (np.arange(len(td)) % 2)
    # ⚠⚠ CE QUE LE LISSAGE DOIT FAIRE, et c'est ce qui manquait à la première version : une
    # ride d'un échantillon met des crêtes partout et DÉPLACE le maximum. Lissé à l'échelle
    # de la bosse, il n'en reste qu'une, et elle est là où la bosse est.
    v("une ride d'un échantillon met des crêtes partout", len(pics(ride, td)) > 5,
      str(len(pics(ride, td))))
    v("... et déplace le maximum", abs(float(td[int(np.argmax(ride))])) > 0.5,
      str(td[int(np.argmax(ride))]))
    lis = lisser(ride, 9)
    v("lissé à l'échelle de la bosse, il ne reste qu'une crête", len(pics(lis, td)) == 1,
      str(len(pics(lis, td))))
    v("... et elle est là où la bosse est", abs(float(td[int(np.argmax(lis))])) <= 1.0,
      str(td[int(np.argmax(lis))]))
    # ⚠ Loin des bords, un lissage symétrique laisse une rampe intacte : s'il la déplaçait, il
    # déplacerait aussi le flanc d'une feuille, donc la crête qu'on va chercher dessus.
    rampe = np.arange(13.0)
    v("loin des bords, le lissage ne déplace pas une rampe",
      bool(np.allclose(lisser(rampe, 3)[3:-3], rampe[3:-3])), str(np.round(lisser(rampe, 3), 2)))
    v("une largeur de un lisse encore la ride de Nyquist",
      float(np.abs(np.diff(lisser(ride, 1))).max()) < float(np.abs(np.diff(ride)).max()),
      f"{np.abs(np.diff(lisser(ride, 1))).max():.2f} contre {np.abs(np.diff(ride)).max():.2f}")

    # --- la corrélation : elle trouve la FORME, pas la clarté ---
    tl = np.arange(-20.0, 20.1, 1.0)
    forme = np.array([0.0, 1.0, 4.0, 9.0, 4.0, 1.0, 0.0])
    ligne = np.zeros((1, len(tl)))
    pose = int(np.argmin(np.abs(tl - 6.0))) - 3
    ligne[0, pose:pose + len(forme)] = forme
    c, centres = correler(ligne, forme, tl)
    t = decalage_retenu(c, centres)
    v("la corrélation retrouve la forme là où elle est posée", abs(float(t[0]) - 6.0) < 0.51,
      str(t))
    # ⚠⚠ LE TÉMOIN QUI SÉPARE LA FORME DE LA CLARTÉ : un plateau DEUX FOIS plus brillant que
    # la bosse, mais sans sa forme. Le maximum brut y va, la corrélation non.
    piege = ligne.copy()
    piege[0, 2:9] = 18.0
    v("un plateau plus brillant ne détourne pas la corrélation",
      abs(float(decalage_retenu(*correler(piege, forme, tl))[0]) - 6.0) < 0.51)
    v("... alors que le maximum brut s'y jette",
      abs(float(sommet(piege, tl, +1)[0]) - 6.0) > 5.0, str(sommet(piege, tl, +1)))
    # ⚠ Un gabarit plus long que la ligne ne rend rien plutôt qu'un décalage inventé.
    v("un gabarit plus long que la ligne ne rend aucun décalage",
      correler(ligne, np.zeros(len(tl) + 4), tl)[0].size == 0)
    v("un gabarit mélangé ne retrouve pas la forme",
      abs(float(decalage_retenu(*correler(ligne, np.array(
          [4.0, 0.0, 9.0, 1.0, 0.0, 4.0, 1.0]), tl))[0]) - 6.0) > 0.51)

    # --- l'étalon vient d'une mesure publiée, pas d'un nombre écrit ici ---
    e = _etalon_um()
    v("l'étalon est celui de la meilleure longueur constante", 45.0 < e < 60.0, str(e))

    # --- l'accord des voisins ---
    champ = np.tile(np.array([10.0, 10.0, 10.0, 10.0, 10.0]), (5, 1))
    champ[2, 2] = -40.0
    val = np.ones((5, 5), dtype=bool)
    acc, assez = accorder_les_voisins(champ, val)
    v("la médiane du voisinage corrige l'isolé", abs(acc[2, 2] - 10.0) < 1e-9, str(acc[2, 2]))
    v("... et laisse ses voisins tranquilles", abs(acc[1, 1] - 10.0) < 1e-9)
    # ⚠⚠ ELLE NE DOIT PAS ÉCRASER UN VRAI GRADIENT : une feuille inclinée fait varier le
    # décalage d'une cellule à l'autre, et une médiane qui aplatirait ça remplacerait la
    # feuille par un plan.
    rampe = np.tile(np.arange(5.0) * 3.0, (5, 1))
    accr = accorder_les_voisins(rampe, val)[0]
    v("... mais elle n'aplatit pas une rampe",
      bool(np.allclose(accr[1:-1, 1:-1], rampe[1:-1, 1:-1])), str(np.round(accr[2], 2)))
    troue = np.ones((5, 5), dtype=bool)
    troue[0] = False
    troue[1] = False
    troue[:, 0] = False
    _, assez2 = accorder_les_voisins(champ, troue)
    v("une cellule sans majorité de voisins est écartée", not assez2[2, 1], str(assez2[2]))
    v("... et une cellule invalide ne devient jamais valide", not assez2[0].any())

    # --- la boîte : elle se choisit sur la géométrie ---
    faux = {1: np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]] * 30),
            7: np.array([[0.0, 0.0, 0.0]] * 30 + [[500.0, 500.0, 500.0]] * 30)}
    c, n = boite_riche(faux, 10.0, reference=7, essais=5)
    v("la boîte se pose là où deux spires se croisent", n[1] >= 30 and n[7] >= 30, str(n))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except Exception:  # noqa: BLE001
        return True
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--echantillon", type=int, default=2000)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.echantillon)
    c = r["convention"]
    print(f"volume brut : {r['zarr']}  ({r['voxel_um']} µm/voxel, accordé aux spires)")
    print(f"écart inter-feuilles lu : {r['ecart_lu_um']} µm = {r['pas_en_voxels']} voxels")
    print(f"fenêtre du raccrochage : ±{r['demi_fenetre_um']} µm (une demi-feuille)")
    print(f"gabarit : ±{r['demi_gabarit_um']} µm autour de la surface de DÉPART\n")
    print(f"la matière autour d'une spire publiée — {c['lignes']} lignes, {c['spires']} spires")
    print(f"  crête à {c['crete_um']:+.1f} µm · creux à {c['creux_um']:+.1f} µm · "
          f"contraste {c['contraste']}\n")
    print(f"{'de':>4} {'vers':>5} {'cell.':>6} {'sur place':>10} {'pas seul':>9} "
          f"{'raccroché':>10} {'max brut':>9} {'gab. mêlé':>10} {'fen. large':>11} {'bord':>5}")
    print("-" * 92)
    for e in r["lignes"]:
        print(f"{e['de']:>4} {e['vers']:>5} {e['cellules']:>6} {e['sur_place_um']:>9.0f}µ "
              f"{e['pas_seul_um']:>8.0f}µ {e['raccroche_um']:>9.0f}µ "
              f"{e['contendant_maximum_brut_um']:>8.0f}µ "
              f"{e['temoin_gabarit_melange_um']:>9.0f}µ "
              f"{e['temoin_fenetre_large_um']:>10.0f}µ {e['decalages_au_bord']:>5}")
    for e in r["paires_ecartees"]:
        print(f"{e['de']:>4} {e['vers']:>5}   écartée — " + ", ".join(
            f"{k} {v}" for k, v in e.items() if k not in ("de", "vers")))
    print(f"\nmédianes : sur place {r['sur_place_median_um']} µm · pas seul "
          f"{r['pas_seul_median_um']} µm · RACCROCHÉ {r['raccroche_median_um']} µm")
    print(f"témoins  : maximum brut {r['contendant_maximum_brut_median_um']} µm · "
          f"gabarit mélangé {r['temoin_gabarit_melange_median_um']} µm · "
          f"fenêtre large {r['temoin_fenetre_large_median_um']} µm")
    print(f"accordé aux voisins : {r['accorde_median_um']} µm "
          f"(p90 {r['accorde_p90_median_um']} contre {r['raccroche_p90_median_um']}), "
          f"témoin d'accord mélangé {r['temoin_accord_melange_median_um']} µm "
          f"(p90 {r['temoin_accord_melange_p90_median_um']}), "
          f"{r['paires_ameliorees_accord']} paires sur {r['paires']}")
    if r["paires_hors_de_portee"]:
        print(f"⚠ hors de portée du raccrochage (pas seul > demi-fenêtre) : "
              f"spires {r['paires_hors_de_portee']}")
    print(f"raccrocher sans avoir bougé déplace de {r['deplacement_sur_place_median_um']} µm")
    print(f"gain : {r['gain_du_raccrochage_um']} µm sur le pas seul "
          f"({100 * (r['part_de_lerreur_enlevee'] or 0):.1f} %), "
          f"{r['paires_ameliorees']} paires sur {r['paires']} améliorées")
    print(f"coût : {r['cout']['blocs_telecharges']} blocs téléchargés, "
          f"{r['cout']['mebioctets']} Mio")
    print(f"\n→ sous l'étalon de {r['etalon_um']} µm (meilleure longueur constante) : "
          f"{'OUI' if r['passe_sous_letalon'] else 'NON'}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
