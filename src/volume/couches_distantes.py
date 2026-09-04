#!/usr/bin/env python3
"""Lire une FENÊTRE d'une pile de couches distante, sans télécharger les 30 Go.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UNE QUESTION DE L'AUTEUR QUI L'A OUVERT. `77` §10
mesure l'écart entre une surface publiée et la feuille qu'elle suit, et voulait l'appliquer à
la chaîne de spires de `44`. J'ai écrit que c'était impossible : *« aucun volume de surface de
son segment de référence n'est publié »*. L'auteur a demandé **« t'es vraiment sûr que c'est
pas stocké quelque part ? »**.

**C'est stocké.** Le segment vit sur `dl.ash2txt.org` avec un dossier `layers/` de 65 couches —
et j'avais interrogé **un seul serveur**, ce qui est l'angle mort que ce dépôt a déjà payé trois
fois (`59`, `laxe_nest_pas_une_ligne`, `lombilic_publie`). Quatrième fois, et c'est l'auteur qui
l'a vue, pas moi.

⭐ CE QUI REND LA LECTURE PAR FENÊTRE POSSIBLE, et c'est une propriété du fichier, pas une
astuce : ces couches sont des TIFF **non compressés à une seule bande** (13513 × 17381, uint16,
`compression 1`, `rowsperstrip` = toute la hauteur). L'octet d'une ligne se calcule donc, et une
fenêtre de lignes est une **plage contiguë** — une requête `Range` par couche au lieu de 469 Mo.

⚠ La fenêtre est en LIGNES entières : on lit toutes les colonnes d'une bande de lignes puis on
tranche. Découper en colonnes ferait une requête par ligne, soit des milliers d'aller-retours
pour économiser une bande passante qui n'est pas le facteur limitant.

⚠⚠ Et le coût est ANNONCÉ avant d'être payé : `--estimer` dit combien d'octets la fenêtre
demandée va transférer. Sans ça, `--hauteur 4096` sur 65 couches télécharge silencieusement
18 Gio — le même genre de panne que la pile de 12,9 Gio qui a fait tomber la machine.

Usage :
    uv run python src/volume/couches_distantes.py <url du dossier layers/> \\
        --sortie data/couches/X --haut 6000 --gauche 8000 --hauteur 640 --largeur 640
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np

DELAI = 120
"""Secondes avant d'abandonner une requête. ⚠ Généreux : une plage de 20 Mo sur un serveur
d'archive n'est pas rapide, et un délai court transformerait une lenteur en absence."""


class _FichierHttp(io.RawIOBase):
    """
    @brief Un fichier distant lisible par `seek`/`read`, servi par des requêtes `Range`.
    """

    def __init__(self, url: str, taille: int) -> None:
        self.url, self.taille, self.pos = url, taille, 0
        self.octets_lus = 0

    def seek(self, decalage: int, depuis: int = 0) -> int:
        self.pos = (decalage if depuis == 0
                    else self.pos + decalage if depuis == 1
                    else self.taille + decalage)
        return self.pos

    def tell(self) -> int:
        return self.pos

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def readinto(self, tampon) -> int:
        if self.pos >= self.taille:
            return 0
        fin = min(self.pos + len(tampon), self.taille) - 1
        requete = urllib.request.Request(self.url,
                                         headers={"Range": f"bytes={self.pos}-{fin}"})
        donnees = urllib.request.urlopen(requete, timeout=DELAI).read()
        tampon[:len(donnees)] = donnees
        self.pos += len(donnees)
        self.octets_lus += len(donnees)
        return len(donnees)


def _taille(url: str) -> int:
    requete = urllib.request.Request(url, method="HEAD")
    return int(urllib.request.urlopen(requete, timeout=DELAI).headers["content-length"])


def lister_couches(dossier: str) -> list[str]:
    """
    @brief Les URL des couches d'un dossier `layers/`, dans l'ordre.
    """
    page = urllib.request.urlopen(dossier, timeout=DELAI).read().decode("utf-8", "replace")
    noms = sorted(set(re.findall(r'href="(\d+\.tif)"', page)))
    return [dossier.rstrip("/") + "/" + n for n in noms]


def forme(url: str) -> tuple[int, int, int, int]:
    """
    @brief (hauteur, largeur, octets par pixel, décalage du premier octet de données).

    ⚠ Le décalage est lu dans la structure du TIFF (`dataoffsets`), pas supposé : un en-tête
    n'a pas de taille fixe, et deviner ferait lire l'image avec quelques octets de décalage —
    ce qui produit une image **plausible** et fausse.
    """
    import tifffile
    fichier = io.BufferedReader(_FichierHttp(url, _taille(url)), buffer_size=1 << 20)
    with tifffile.TiffFile(fichier) as tif:
        page = tif.pages[0]
        if page.is_tiled or len(page.dataoffsets) != 1:
            raise SystemExit(
                f"{url} : cette couche n'est pas une bande unique non compressée — "
                "la lecture par fenêtre ne s'applique pas.")
        h, w = page.shape
        return h, w, page.dtype.itemsize, int(page.dataoffsets[0])


def cout_en_octets(couches: list[str], hauteur: int, largeur_image: int,
                   octets: int) -> int:
    """
    @brief Ce qu'une fenêtre va transférer, AVANT de le transférer.
    """
    return len(couches) * hauteur * largeur_image * octets


def lire_fenetre(couches: list[str], haut: int, gauche: int,
                 hauteur: int, largeur: int) -> np.ndarray:
    """
    @brief La fenêtre demandée, couche par couche, par une plage contiguë chacune.
    """
    h, w, octets, debut = forme(couches[0])
    haut = max(0, min(haut, h - 1))
    hauteur = min(hauteur, h - haut)
    gauche = max(0, min(gauche, w - 1))
    largeur = min(largeur, w - gauche)

    pile = np.empty((len(couches), hauteur, largeur), dtype=np.float32)
    for i, url in enumerate(couches):
        premier = debut + haut * w * octets
        dernier = premier + hauteur * w * octets - 1
        requete = urllib.request.Request(url, headers={"Range": f"bytes={premier}-{dernier}"})
        brut = urllib.request.urlopen(requete, timeout=DELAI).read()
        lignes = np.frombuffer(brut, dtype=f"<u{octets}").reshape(hauteur, w)
        pile[i] = lignes[:, gauche:gauche + largeur]
    return pile


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dossier", help="URL d'un dossier layers/")
    p.add_argument("--sortie", type=Path, required=True)
    p.add_argument("--haut", type=int, default=0)
    p.add_argument("--gauche", type=int, default=0)
    p.add_argument("--hauteur", type=int, default=640)
    p.add_argument("--largeur", type=int, default=640)
    p.add_argument("--estimer", action="store_true",
                   help="annoncer le coût du transfert sans le payer")
    a = p.parse_args()

    couches = lister_couches(a.dossier)
    if not couches:
        raise SystemExit(f"aucune couche sous {a.dossier}")
    h, w, octets, _ = forme(couches[0])
    cout = cout_en_octets(couches, a.hauteur, w, octets)
    print(f"{len(couches)} couches de {h} × {w} ({octets} o/px)")
    print(f"  fenêtre {a.hauteur} × {a.largeur} à ({a.haut}, {a.gauche}) → "
          f"transfert {cout / 1024**3:.2f} Gio "
          f"(les lignes entières sont lues, puis tranchées)")
    if a.estimer:
        return 0

    import tifffile
    pile = lire_fenetre(couches, a.haut, a.gauche, a.hauteur, a.largeur)
    a.sortie.mkdir(parents=True, exist_ok=True)
    for i in range(pile.shape[0]):
        tifffile.imwrite(a.sortie / f"{i:02d}.tif", pile[i].astype(np.uint16))
    part = float((pile.max(0) > 0).mean())
    print(f"écrit : {a.sortie} · {pile.shape[0]} couches · {part * 100:.1f} % de matière")
    if part < 0.2:
        print("  ⚠ fenêtre presque vide — en choisir une autre avec --haut/--gauche",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
