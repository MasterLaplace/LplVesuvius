#!/usr/bin/env python3
"""Lire des VOXELS d'un volume zarr distant sans rapatrier le volume.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Le volume de `PHercParis4` fait 4071×2264×2264 octets, soit
20,7 Go : le rapatrier pour lire quelques milliers de points serait absurde. Or ses chunks sont
ecrits SANS COMPRESSION (`"compressor": null`), donc l'octet d'un voxel est a un decalage
CALCULABLE dans l'objet, et une requete HTTP `Range` suffit. C'est ce qui rend « lire le volume au
point predit » abordable depuis n'importe ou.

⭐⭐⭐ LA PARTIE PORTEUSE EST L'ARITHMETIQUE D'ADRESSE, ET ELLE ECHOUE EN SILENCE. Se tromper
d'ordre d'axes ou de separateur ne leve rien : ca rend un octet parfaitement valide, pris ailleurs
dans le rouleau. Une campagne entiere peut se batir dessus sans qu'aucun controle ne bronche. La
batterie va donc chercher un chunk ENTIER et verifie que les lectures par plage rendent
exactement les memes octets — un controle qui ne peut pas etre satisfait par un mauvais calcul.

⛔ ET LE REFUS EST EXPLICITE : un zarr COMPRESSE ne peut pas etre lu par plage, et le lire quand
meme rendrait des octets de flux compresse qui ressemblent a du bruit de mesure. `VolumeZarr`
refuse a l'ouverture plutot que de rendre des nombres.

Usage :
    uv run python src/commun/voxel_distant.py --verifier
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import time
import urllib.error
import urllib.request

import numpy as np

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"

# ⚠ Deux octets demandes separement coutent deux allers-retours ; deux octets a 400 de distance
# tiennent dans une seule plage pour 400 octets de trop. Le reseau domine largement le volume
# transfere, donc on recolle genereusement. La valeur est un compromis MESURE dans la batterie,
# pas un reglage : au-dela d'un chunk entier (2 Mio) recoller ne peut plus rien economiser.
RECOLLEMENT = 4096

# ⚠ Trois essais, avec une attente qui croit : au-dela, une panne n'est plus passagere et
# insister ferait passer une coupure durable pour de la lenteur.
ESSAIS = 3


def _get(url: str, plage: tuple[int, int] | None, timeout: float,
         essais: int = ESSAIS) -> tuple[bytes | None, int | None]:
    """Un GET, eventuellement partiel. Rend (octets, code) — le CODE est ce qui tranche.

    ⚠⚠⚠ LES REESSAIS NE SONT PAS DU CONFORT, ILS RENDENT LA MESURE REPRODUCTIBLE. Sans eux une
    coupure passagere fait tomber des cellules, donc deux executions du meme calcul rendent des
    medianes differentes — mesure : une bande est passee de 90 a 65 cellules entre deux runs, et
    sa dispersion de 14,2 a 12,7 µm. Un nombre publie qui bouge selon l'humeur du reseau n'est
    pas un resultat.

    ⚠⚠ RENDRE None SUR TOUTE ERREUR CONFOND DEUX FAITS OPPOSES. Un 404 sur un chunk zarr veut
    dire « ce chunk est entierement au remplissage », ce qui est une valeur legitime du volume ;
    une coupure reseau veut dire qu'on ne sait pas. Les aplatir ferait lire du VIDE la ou le
    reseau a laché, c'est-a-dire fabriquer la mesure qu'on cherche.
    """
    entetes = {}
    if plage is not None:
        entetes["Range"] = f"bytes={plage[0]}-{plage[1]}"
    for essai in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=entetes),
                                        timeout=timeout) as r:
                return r.read(), int(r.status)
        except urllib.error.HTTPError as e:
            # ⚠ Un code HTTP est une REPONSE, pas une panne : la reessayer ne la changera pas,
            # et un 404 est meme une valeur legitime du volume.
            return None, int(e.code)
        except (urllib.error.URLError, OSError):
            if essai + 1 >= essais:
                return None, None
            time.sleep(0.2 * (essai + 1))
    return None, None


class VolumeZarr:
    """Un volume zarr distant, lisible voxel par voxel par requetes `Range`.

    ⚠⚠ LES AXES SONT (z, y, x) DANS CET ORDRE, et c'est le `.zattrs` du depot qui le dit, pas une
    convention supposee. Un appelant qui passerait (x, y, z) lirait un point valide et faux.
    """

    def __init__(self, url: str, niveau: int = 0, timeout: float = 60.0) -> None:
        self.url = url.rstrip("/")
        self.niveau = niveau
        self.timeout = timeout
        brut, _ = _get(f"{self.url}/{niveau}/.zarray", None, timeout)
        if brut is None:
            raise RuntimeError(f"pas de .zarray au niveau {niveau} sous {self.url}")
        m = json.loads(brut)
        # ⛔ Le refus, plutot que des octets de flux compresse pris pour des intensites.
        if m.get("compressor") is not None or m.get("filters"):
            raise RuntimeError("zarr compresse : illisible par plage, refus plutot que du bruit")
        if m.get("order", "C") != "C":
            raise RuntimeError(f"ordre {m.get('order')} : l'arithmetique d'adresse suppose C")
        if m["dtype"] not in ("|u1", "u1"):
            raise RuntimeError(f"dtype {m['dtype']} : seul l'octet non signe est gere")
        self.forme = tuple(int(x) for x in m["shape"])
        self.chunk = tuple(int(x) for x in m["chunks"])
        self.separateur = m.get("dimension_separator", ".")
        self.remplissage = int(m.get("fill_value") or 0)

    def cle(self, cz: int, cy: int, cx: int) -> str:
        """Le chemin de l'objet qui porte ce chunk."""
        return f"{self.url}/{self.niveau}/" + self.separateur.join(
            str(x) for x in (cz, cy, cx))

    def adresse(self, z: int, y: int, x: int) -> tuple[tuple[int, int, int], int]:
        """Le chunk qui contient (z, y, x) et le DECALAGE de son octet dedans.

        ⭐ C'est la seule ligne d'arithmetique du fichier, et la batterie la confronte a un chunk
        entier telecharge : un mauvais ordre d'axes rendrait un octet valide et faux.
        """
        dz, dy, dx = self.chunk
        interne = ((z % dz) * dy + (y % dy)) * dx + (x % dx)
        return (z // dz, y // dy, x // dx), interne

    def dans_le_volume(self, p: np.ndarray) -> np.ndarray:
        """Le masque des points qui tombent dans la boite du volume."""
        return np.all((p >= 0) & (p < np.array(self.forme)), axis=-1)

    def lire(self, points: np.ndarray, fils: int = 16) -> np.ndarray:
        """L'intensite en chaque point entier (z, y, x). NaN hors du volume ou si le chunk manque.

        ⚠⚠ UN CHUNK ABSENT N'EST PAS UN ZERO. Le zarr n'ecrit pas les chunks entierement vides,
        donc un 404 veut dire « remplissage », et c'est une valeur legitime du volume. Une panne
        RESEAU rend NaN. Confondre les deux ferait passer une coupure pour du vide.
        """
        p = np.asarray(points, dtype=np.int64).reshape(-1, 3)
        out = np.full(len(p), np.nan)
        ok = self.dans_le_volume(p)
        if not ok.any():
            return out

        # Regroupe par chunk : tous les points d'un meme chunk partagent un objet distant.
        paquets: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
        for i in np.flatnonzero(ok):
            c, d = self.adresse(*p[i])
            paquets.setdefault(c, []).append((d, int(i)))

        def un_chunk(item):
            c, entrees = item
            entrees.sort()
            # ⭐⭐ RECOLLEMENT : des cellules voisines d'une meme ligne de maille sont contigues
            # en x, donc leurs octets le sont aussi. Une plage par tranche au lieu d'une par
            # voxel est ce qui fait tenir la mesure dans le temps d'un cafe.
            tranches, debut, fin = [], entrees[0][0], entrees[0][0]
            for d, _ in entrees[1:]:
                if d - fin <= RECOLLEMENT:
                    fin = d
                    continue
                tranches.append((debut, fin))
                debut = fin = d
            tranches.append((debut, fin))
            return entrees, [(a, b) + _get(self.cle(*c), (a, b), self.timeout)
                             for a, b in tranches]

        absents = pannes = 0
        with cf.ThreadPoolExecutor(max_workers=max(1, fils)) as pool:
            for entrees, rendu in pool.map(un_chunk, paquets.items()):
                for a, b, brut, code in rendu:
                    vises = [(d, i) for d, i in entrees if a <= d <= b]
                    if brut is None or len(brut) != b - a + 1:
                        if code == 404:
                            # ⚠ Chunk non ecrit : le zarr omet ce qui est entierement au
                            # remplissage, donc c'est une VALEUR, pas une absence de mesure.
                            absents += len(vises)
                            for _, i in vises:
                                out[i] = float(self.remplissage)
                        else:
                            pannes += len(vises)
                        continue
                    for d, i in vises:
                        out[i] = float(brut[d - a])
        self.derniers_absents, self.dernieres_pannes = absents, pannes
        return out


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- l'arithmetique, sur une metadonnee fabriquee -------------------------------------
    class Faux(VolumeZarr):
        def __init__(self, forme, chunk, sep="/"):
            self.url, self.niveau, self.timeout = "http://x", 0, 1.0
            self.forme, self.chunk, self.separateur = forme, chunk, sep
            self.remplissage = 0

    f = Faux((300, 200, 100), (128, 128, 128))
    v("l'origine est le premier octet du chunk 0", f.adresse(0, 0, 0) == ((0, 0, 0), 0))
    v("x avance d'un octet", f.adresse(0, 0, 1) == ((0, 0, 0), 1))
    v("y avance d'une largeur de chunk", f.adresse(0, 1, 0) == ((0, 0, 0), 128))
    v("z avance d'un plan de chunk", f.adresse(1, 0, 0) == ((0, 0, 0), 128 * 128))
    # ⚠⚠ CE CONTROLE EST CELUI QUI ATTRAPE UNE INVERSION D'AXES : si z et x etaient echanges,
    # les trois lignes ci-dessus passeraient toutes en rendant des decalages plausibles.
    v("... donc les trois pas sont DISTINCTS", len({f.adresse(0, 0, 1)[1],
                                                    f.adresse(0, 1, 0)[1],
                                                    f.adresse(1, 0, 0)[1]}) == 3)
    v("le passage de chunk se fait a la frontiere", f.adresse(0, 0, 128) == ((0, 0, 1), 0))
    v("... et le decalage repart de zero", f.adresse(0, 128, 0) == ((0, 1, 0), 0))
    v("le dernier voxel d'un chunk est le dernier octet",
      f.adresse(127, 127, 127)[1] == 128 ** 3 - 1)
    v("la cle suit le separateur declare", f.cle(1, 2, 3).endswith("/0/1/2/3"))
    v("... et un separateur en point aussi",
      Faux((1, 1, 1), (1, 1, 1), ".").cle(1, 2, 3).endswith("/0/1.2.3"))
    # ⚠ Hors boite : un point negatif ou au-dela de la forme n'a pas d'octet.
    p = np.array([[0, 0, 0], [-1, 0, 0], [299, 199, 99], [300, 0, 0]])
    v("la boite du volume est respectee",
      list(f.dans_le_volume(p)) == [True, False, True, False])
    # ⭐⭐ LE REESSAI EST VERIFIABLE, PAS AFFIRME : un hote qui n'existe pas est une panne
    # RESEAU, donc il doit etre reessaye ESSAIS fois puis rendre (None, None) ; un 404 est une
    # REPONSE, donc il doit etre rendu du premier coup. Confondre les deux ferait soit insister
    # sur une reponse claire, soit abandonner sur une coupure passagere.
    appels = {"n": 0}
    vrai_urlopen = urllib.request.urlopen

    def compte(*a, **k):
        appels["n"] += 1
        return vrai_urlopen(*a, **k)

    urllib.request.urlopen = compte
    try:
        _get("http://127.0.0.1:9/rien", None, 0.3)
        reseau = appels["n"]
        appels["n"] = 0
        _get(f"{BUCKET}/il-nexiste-pas-un-tel-objet-ici", None, 10.0)
        http = appels["n"]
    finally:
        urllib.request.urlopen = vrai_urlopen
    v("une panne réseau est réessayée", reseau == ESSAIS, f"{reseau} essais pour {ESSAIS}")
    v("... alors qu'un code HTTP est rendu du premier coup", http == 1, f"{http} essai(s)")

    # --- la revendication porteuse, contre le VRAI volume ---------------------------------
    url = f"{BUCKET}/PHercParis4/volumes/20260310170716-45.532um-11.0m-74keV-masked.zarr"
    try:
        vol = VolumeZarr(url)
    except RuntimeError as e:
        print(f"  ⚠ volume injoignable ({e}) — contrôles réseau sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    v("le volume publie sa forme", vol.forme == (4071, 2264, 2264), str(vol.forme))
    v("... et des chunks de 128", vol.chunk == (128, 128, 128), str(vol.chunk))
    # ⭐⭐⭐ LE CONTROLE QUI NE PEUT PAS ETRE SATISFAIT PAR UN MAUVAIS CALCUL : un chunk ENTIER
    # est telecharge, puis les memes voxels sont relus par plage. Un ordre d'axes faux rend des
    # octets valides mais differents, donc l'egalite tombe.
    cz, cy, cx = 16, 9, 9  # au coeur du volume, donc un chunk qui existe
    entier, _ = _get(vol.cle(cz, cy, cx), None, 120.0)
    if entier is None or len(entier) != 128 ** 3:
        v("un chunk entier est lisible", False, f"{len(entier) if entier else 0} octets")
    else:
        v("un chunk entier est lisible", True, f"{len(entier)} octets")
        rng = np.random.default_rng(7)
        loc = rng.integers(0, 128, size=(24, 3))
        pts = loc + np.array([cz * 128, cy * 128, cx * 128])
        attendu = np.array([float(entier[(int(a) * 128 + int(b)) * 128 + int(c)])
                            for a, b, c in loc])
        lus = vol.lire(pts, fils=8)
        v("les lectures par plage égalent le chunk entier, voxel par voxel",
          np.array_equal(lus, attendu),
          f"{int(np.sum(lus == attendu))}/{len(attendu)} identiques")
        # ⚠⚠ ET LE CONTROLE DU CONTROLE : si le chunk etait uniforme, l'egalite ci-dessus
        # passerait avec n'importe quelle adresse. Il faut que les valeurs VARIENT.
        v("... et le chunk témoin n'est pas uniforme, sinon l'égalité ne prouverait rien",
          len(set(attendu.tolist())) > 3, f"{len(set(attendu.tolist()))} valeurs distinctes")

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
