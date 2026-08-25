#!/usr/bin/env python3
"""L'empreinte d'une surface tifxyz — la clé d'un cache de rendu indexé par CONTENU.

⚠⚠ POURQUOI CE FICHIER EXISTE. Le cache de `profiler_une_surface.sh` est indexé par
**répertoire de destination** : deux campagnes qui profilent la même surface la rendent deux
fois. Mesuré le 2026-08-25 — `morceau_00` rendu et profilé dans `chaine_tangentielle` puis
dans `chaine_courte`, résultat **bit pour bit identique**, quinze minutes payées deux fois.
Une clé par contenu supprime la classe entière.

  ⭐ La règle : l'empreinte ne dépend QUE de ce qui change le résultat. Le contenu des
    fichiers et leur nom relatif, rien d'autre.

⚠⚠ Ce qui est délibérément EXCLU, et chacun est une panne évitée :
  - la **date de modification** : recopier une surface d'un disque à l'autre la change sans
    changer un octet, et le cache manquerait pour rien ;
  - le **chemin absolu** : la même surface sous deux racines est la même surface, sinon deux
    machines ne partagent jamais un cache ;
  - l'**ordre du système de fichiers** : `iterdir` ne promet aucun ordre, donc deux exécutions
    sur le même dossier donneraient deux empreintes. Le tri est ce qui rend la clé une clé.

⚠ Le nom RELATIF entre dans l'empreinte : deux surfaces dont les mêmes octets sont rangés sous
`x.tif` et `y.tif` ne sont pas la même surface, et les confondre rendrait un profil pour l'autre.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def empreinte_surface(racine: Path, longueur: int = 16) -> str:
    """Une empreinte stable du contenu d'un dossier de surface.

    Rend les `longueur` premiers caractères hexadécimaux d'un SHA-256 qui couvre, pour chaque
    fichier trié par chemin relatif : son chemin, sa taille et ses octets.
    """
    if not racine.is_dir():
        raise NotADirectoryError(f"{racine} n'est pas un dossier de surface")
    h = hashlib.sha256()
    fichiers = sorted((f for f in racine.rglob("*") if f.is_file() and not f.is_symlink()),
                      key=lambda f: f.relative_to(racine).as_posix())
    if not fichiers:
        raise ValueError(f"{racine} ne contient aucun fichier")
    for f in fichiers:
        rel = f.relative_to(racine).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(str(f.stat().st_size).encode("ascii"))
        h.update(b"\0")
        with f.open("rb") as fh:
            for bloc in iter(lambda: fh.read(1 << 20), b""):
                h.update(bloc)
    return h.hexdigest()[:longueur]


def cle_de_profil(empreinte: str, niveau: int, couches: int, voxel_um: float) -> str:
    """La clé complète d'un profil : la surface ET les réglages qui changent le résultat.

    ⚠⚠ Un réglage qui change le profil et n'entre pas dans la clé fait rendre le profil d'un
    AUTRE réglage, ce qui est pire qu'un cache absent : c'est un résultat faux qui a l'air
    d'un résultat. `--scale 1` et `--auto-crop` sont aujourd'hui des constantes de
    `profiler_une_surface.sh` ; le jour où l'un devient un paramètre, il entre ici.
    """
    return f"{empreinte}-g{niveau}-n{couches}-um{voxel_um:g}"


def verifier() -> int:
    import os
    import shutil
    import tempfile
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    d = Path(tempfile.mkdtemp())
    a = d / "a.tifxyz"
    (a / "sous").mkdir(parents=True)
    (a / "x.tif").write_bytes(b"XXXX" * 100)
    (a / "y.tif").write_bytes(b"YYYY" * 100)
    (a / "sous" / "meta.json").write_text('{"k": 1}', encoding="utf-8")

    e1 = empreinte_surface(a)
    v("une empreinte est stable d'un appel à l'autre", e1 == empreinte_surface(a))
    v("... et fait la longueur demandée", len(e1) == 16 and len(empreinte_surface(a, 8)) == 8)

    # ⭐ Une copie identique SOUS UN AUTRE CHEMIN a la même empreinte : c'est tout le but.
    b = d / "ailleurs" / "b.tifxyz"
    b.parent.mkdir()
    shutil.copytree(a, b)
    v("la même surface sous un autre chemin a la MÊME empreinte", empreinte_surface(b) == e1)

    # ⚠ La date de modification ne doit RIEN changer.
    os.utime(b / "x.tif", (0, 0))
    v("changer la date ne change pas l'empreinte", empreinte_surface(b) == e1)

    # ⚠⚠ Le contenu, lui, doit tout changer -- y compris d'un seul octet.
    c = d / "c.tifxyz"
    shutil.copytree(a, c)
    (c / "x.tif").write_bytes(b"XXXX" * 99 + b"XXXZ")
    v("un seul octet différent change l'empreinte", empreinte_surface(c) != e1)

    # ⚠⚠ Le NOM relatif compte : les mêmes octets rangés autrement ne sont pas la même
    # surface. ⚠ Le renommage doit PRÉSERVER L'ORDRE DE TRI, sinon le test passe pour la
    # mauvaise raison : `x.tif` → `z.tif` change aussi l'ordre des octets hachés, donc une
    # implémentation qui ignore le nom le réussirait quand même. Payé le 2026-08-25, une
    # sonde l'a montré en retirant le nom du hachage sans faire échouer un seul contrôle.
    # `x.tif` → `xx.tif` garde l'ordre (sous/… < x… < y…) et les deux fichiers font la même
    # taille, donc SEUL le nom peut faire la différence.
    e = d / "e.tifxyz"
    shutil.copytree(a, e)
    (e / "x.tif").rename(e / "xx.tif")
    v("les mêmes octets, dans le même ordre, sous un autre nom : AUTRE empreinte",
      empreinte_surface(e) != e1)

    # Un dossier absent ou vide est refusé, pas défauté : une empreinte de rien serait une clé
    # que toutes les surfaces vides partageraient.
    (d / "vide").mkdir()
    for cas, exc in ((d / "vide", ValueError), (d / "nexiste_pas", NotADirectoryError),
                     (a / "x.tif", NotADirectoryError)):
        try:
            empreinte_surface(cas)
            v(f"{cas.name} est refusé", False)
        except (ValueError, NotADirectoryError):
            v(f"« {cas.name} » est refusé plutôt que défauté", True)

    # --- la clé complète ---
    k = cle_de_profil("abc123", 0, 41, 7.91)
    v("la clé porte la surface et les trois réglages", k == "abc123-g0-n41-um7.91")
    v("un niveau différent donne une clé différente",
      cle_de_profil("abc123", 1, 41, 7.91) != k)
    v("un nombre de couches différent aussi",
      cle_de_profil("abc123", 0, 81, 7.91) != k)
    # ⭐ Le contrôle qui compte : un réglage qui change le profil DOIT changer la clé, sinon
    # le cache rend le profil d'un autre réglage -- un résultat faux qui a l'air d'un résultat.
    v("une taille de voxel différente aussi",
      cle_de_profil("abc123", 0, 41, 3.24) != k)
    v("la clé ne contient ni espace ni séparateur de chemin",
      " " not in k and "/" not in k)

    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("surface", nargs="?", type=Path, help="le dossier .tifxyz")
    p.add_argument("--niveau", type=int, help="avec --couches et --voxel-um : rend la clé complète")
    p.add_argument("--couches", type=int)
    p.add_argument("--voxel-um", type=float)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.surface:
        p.error("un dossier de surface est requis")
    try:
        e = empreinte_surface(a.surface)
    except (ValueError, NotADirectoryError) as err:
        print(f"erreur : {err}", file=sys.stderr)
        return 2
    if a.niveau is not None and a.couches is not None and a.voxel_um is not None:
        print(cle_de_profil(e, a.niveau, a.couches, a.voxel_um))
    else:
        print(e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
