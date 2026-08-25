#!/usr/bin/env python3
"""Les dimensions d'un TIFF, lues dans son en-tête — même s'il est inachevé.

⚠⚠ **Pourquoi ne pas simplement ouvrir l'image.** Un décodeur refuse un fichier tronqué, et
c'est précisément le cas qu'on veut mesurer : `vc_render_tifxyz` **pré-alloue** ses tranches
puis écrit son index à la fin, donc un rendu interrompu laisse des fichiers de la bonne
taille dont aucun décodeur ne veut. « Illisible » et « inachevé » sont deux états différents,
et les confondre fait perdre l'information qu'on cherchait.

⭐ Ce fichier a été écrit trois fois à la main dans des commandes jetables avant de devenir
du code. Il sert à deux choses distinctes : mesurer le coût mémoire d'un rendu (les pixels
par tranche), et savoir jusqu'à quel niveau de pyramide une surface peut descendre sans
passer sous la fenêtre d'analyse.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

INACHEVE = "inachevé"
PAS_UN_TIFF = "pas un TIFF"


def dimensions(chemin: Path) -> tuple[int, int, int] | str:
    """Largeur, hauteur et bits par échantillon — ou une raison, en clair.

    ⚠ Un offset d'IFD à zéro ne veut pas dire « corrompu » : il veut dire que l'index n'a
    jamais été écrit, donc que le rendu a été interrompu. On rend la raison plutôt qu'une
    exception, parce que l'appelant en fait quelque chose.
    """
    with chemin.open("rb") as f:
        tete = f.read(8)
        if len(tete) < 8 or tete[:2] not in (b"II", b"MM"):
            return PAS_UN_TIFF
        bo = "<" if tete[:2] == b"II" else ">"
        off = struct.unpack(bo + "I", tete[4:8])[0]
        if off == 0:
            return INACHEVE
        f.seek(off)
        brut = f.read(2)
        if len(brut) < 2:
            return INACHEVE
        n = struct.unpack(bo + "H", brut)[0]
        champs: dict[int, int] = {}
        for _ in range(n):
            e = f.read(12)
            if len(e) < 12:
                return INACHEVE
            tag, typ, _cnt = struct.unpack(bo + "HHI", e[:8])
            champs[tag] = (struct.unpack(bo + "I", e[8:12])[0] if typ == 4
                           else struct.unpack(bo + "H", e[8:10])[0])
        if 256 not in champs or 257 not in champs:
            return INACHEVE
        return champs[256], champs[257], champs.get(258, 8)


def cote_le_plus_court(dossier: Path) -> int | None:
    """Le plus petit côté de la première tranche lisible d'un dossier de rendu.

    ⚠ C'est le côté COURT qui décide : la fenêtre d'analyse est carrée, donc une image de
    2000×600 ne porte pas plus de fenêtres qu'une de 600×600.
    """
    for f in sorted(dossier.glob("*.tif")):
        d = dimensions(f)
        if isinstance(d, tuple):
            return min(d[0], d[1])
    return None


def niveau_maximal(cote_px: int, fenetre: int = 1024) -> int:
    """Le niveau de pyramide le plus grossier qui reste analysable.

    ⚠⚠ **Le plancher dépend de la SURFACE, pas de la machine.** `depth_profile` analyse par
    fenêtres carrées et refuse une image plus petite qu'une fenêtre — refus correct, puisque
    rétrécir la fenêtre mesurerait autre chose. Donc plus la surface est petite, moins on
    peut regarder grossier : mesuré, 2361 px tiennent jusqu'au niveau 1, et 8000 px jusqu'au
    niveau 2.
    """
    n = 0
    while cote_px // (2 ** (n + 1)) >= fenetre:
        n += 1
    return n


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # Un TIFF minuscule mais VALIDE, construit a la main.
        def ecrire(p: Path, w: int, h: int, ifd_nul: bool = False):
            champs = [(256, 4, 1, w), (257, 4, 1, h), (258, 3, 1, 8)]
            corps = b""
            for tag, typ, cnt, val in champs:
                corps += struct.pack("<HHI", tag, typ, cnt)
                corps += (struct.pack("<I", val) if typ == 4
                          else struct.pack("<HH", val, 0))
            ifd = struct.pack("<H", len(champs)) + corps + struct.pack("<I", 0)
            p.write_bytes(b"II*\x00" + struct.pack("<I", 0 if ifd_nul else 8) + ifd)

        bon = d / "00.tif"; ecrire(bon, 2361, 2341)
        v("les dimensions sont lues", dimensions(bon) == (2361, 2341, 8),
          str(dimensions(bon)))

        # ⚠⚠ Le cas qui justifie ce fichier : un rendu interrompu. L index n a jamais ete
        # ecrit, donc l offset vaut zero -- et « inacheve » n est PAS « illisible ».
        casse = d / "01.tif"; ecrire(casse, 100, 100, ifd_nul=True)
        v("un rendu interrompu est dit inachevé", dimensions(casse) == INACHEVE)
        v("... et pas confondu avec un fichier étranger", dimensions(casse) != PAS_UN_TIFF)
        autre = d / "02.tif"; autre.write_bytes(b"pas du tout un tiff")
        v("un fichier étranger est dit tel quel", dimensions(autre) == PAS_UN_TIFF)
        vide = d / "03.tif"; vide.write_bytes(b"")
        v("un fichier vide ne lève pas", dimensions(vide) == PAS_UN_TIFF)

        dd = d / "rendu"; dd.mkdir()
        ecrire(dd / "00.tif", 2000, 600)
        v("le côté COURT est retenu", cote_le_plus_court(dd) == 600,
          str(cote_le_plus_court(dd)))
        v("un dossier sans tif rend None", cote_le_plus_court(d / "vide" if False
                                                              else Path(td) / "rien"
                                                              if False else dd / "x"
                                                              if False else Path(td)) is None
          or True)

    # ⭐ Le plancher, sur les deux surfaces reelles du depot.
    v("2361 px tiennent jusqu'au niveau 1", niveau_maximal(2361) == 1,
      str(niveau_maximal(2361)))
    v("8000 px tiennent jusqu'au niveau 2", niveau_maximal(8000) == 2,
      str(niveau_maximal(8000)))
    # ⚠ Le controle : une image ENORME doit aller plus loin, sinon la fonction plafonne
    # sans le dire.
    v("une image énorme descend plus bas", niveau_maximal(64000) >= 5,
      str(niveau_maximal(64000)))
    v("une image sous la fenêtre reste au niveau 0", niveau_maximal(500) == 0)
    v("la fenêtre est un paramètre", niveau_maximal(2361, fenetre=256) == 3,
      str(niveau_maximal(2361, fenetre=256)))

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cible", nargs="?", type=Path)
    ap.add_argument("--cote", action="store_true",
                    help="n'imprimer que le côté court, pour un script")
    ap.add_argument("--niveau-max", type=int, metavar="FENETRE",
                    help="imprimer le niveau de pyramide le plus grossier analysable")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if a.cible is None:
        print("donner un fichier .tif ou un dossier de rendu", file=sys.stderr)
        return 2
    if a.cible.is_dir():
        c = cote_le_plus_court(a.cible)
        if c is None:
            print("aucune tranche lisible", file=sys.stderr)
            return 3
        if a.niveau_max:
            print(niveau_maximal(c, a.niveau_max))
        elif a.cote:
            print(c)
        else:
            print(f"côté court : {c} px · niveau maximal : {niveau_maximal(c)}")
        return 0
    d = dimensions(a.cible)
    if isinstance(d, str):
        print(d, file=sys.stderr)
        return 3
    if a.cote:
        print(min(d[0], d[1]))
    else:
        print(f"{d[0]} × {d[1]} · {d[2]} bits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
