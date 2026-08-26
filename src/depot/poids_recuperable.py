#!/usr/bin/env python3
"""Ce qu'un dossier libère VRAIMENT quand on le supprime — `du` ne sait pas répondre.

⚠⚠ POURQUOI CE FICHIER EXISTE. `du -sh` a compté 16,6 Go dans `htr/`, `inference/` et
`src/xpu/`, et le plan de ménage (`56`) a publié ce chiffre. Il est **faux d'un facteur
quatre**, pour une raison que `du` ne peut pas voir : `uv` installe ses paquets en **liens
durs** vers `~/.cache/uv`. Un fichier de venv n'est donc pas une copie, c'est un nom de plus
sur des octets déjà là. Supprimer le nom ne libère rien tant qu'il en reste un autre.

⭐ La règle, et elle se lit dans le compte de liens :

  nlink = 1                 exclusif au dossier      -> libéré tout de suite
  nlink = 2                 le cache + CE venv       -> libéré après `uv cache prune`
  nlink >= 3                le cache + d'autres venvs -> reste pris, quoi qu'on fasse

⚠ Un inode n'est compté qu'UNE fois même s'il apparaît sous plusieurs noms dans le périmètre :
sans ça, un paquet partagé entre deux dossiers examinés ensemble serait compté deux fois, ce
qui est exactement l'erreur de `du` invoqué séparément par dossier.

⚠ Ce que ce fichier ne prétend PAS savoir : si `uv cache prune` sera effectivement lancé, ni
si un venv hors du dépôt tient l'un de ces paquets. Le compte de liens est un fait local ; ce
qui tient les autres liens n'est pas nommable d'ici, donc c'est dit et pas deviné.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

GIO = 1073741824


def peser(chemins) -> dict:
    """Réparti les octets d'un périmètre selon leur nombre de liens durs.

    Rend les trois quantités qui décident, plus le détail par compte de liens.
    """
    vus: set[tuple[int, int]] = set()
    octets: dict[int, int] = {}
    fichiers: dict[int, int] = {}
    liens_symboliques = introuvables = 0
    for base in chemins:
        base = Path(base)
        if not base.exists():
            introuvables += 1
            continue
        for racine, _, noms in os.walk(base):
            for n in noms:
                p = Path(racine) / n
                try:
                    st = p.lstat()
                except OSError:
                    continue
                if os.path.islink(p):
                    liens_symboliques += 1
                    continue
                if not os.path.isfile(p):
                    continue
                cle = (st.st_dev, st.st_ino)
                if cle in vus:
                    continue
                vus.add(cle)
                octets[st.st_nlink] = octets.get(st.st_nlink, 0) + st.st_size
                fichiers[st.st_nlink] = fichiers.get(st.st_nlink, 0) + 1
    return {
        "immediat": octets.get(1, 0),
        "apres_prune": octets.get(2, 0),
        "jamais": sum(v for k, v in octets.items() if k >= 3),
        "inodes": len(vus),
        "par_liens": {str(k): {"octets": octets[k], "fichiers": fichiers[k]}
                      for k in sorted(octets)},
        "liens_symboliques": liens_symboliques,
        "chemins_introuvables": introuvables,
    }


def verifier() -> int:
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
    (d / "cache").mkdir()
    (d / "venvA").mkdir()
    (d / "venvB").mkdir()

    seul = d / "venvA" / "seul.bin"
    seul.write_bytes(b"x" * 1000)                       # nlink 1
    partage1 = d / "cache" / "p1.bin"
    partage1.write_bytes(b"y" * 2000)
    os.link(partage1, d / "venvA" / "p1.bin")           # nlink 2
    partage2 = d / "cache" / "p2.bin"
    partage2.write_bytes(b"z" * 4000)
    os.link(partage2, d / "venvA" / "p2.bin")
    os.link(partage2, d / "venvB" / "p2.bin")           # nlink 3

    r = peser([d / "venvA"])
    v("l'exclusif est libéré tout de suite", r["immediat"] == 1000)
    v("le partagé avec le seul cache attend le prune", r["apres_prune"] == 2000)
    v("le partagé avec un autre venv ne sera jamais libéré", r["jamais"] == 4000)
    v("trois inodes, pas quatre", r["inodes"] == 3)

    # ⚠ Le contrôle qui distingue ce fichier de `du` : deux dossiers examinés ENSEMBLE ne
    # doivent pas compter deux fois l'inode qu'ils partagent.
    r2 = peser([d / "venvA", d / "venvB"])
    v("un inode partagé n'est compté qu'une fois", r2["inodes"] == 3)
    v("... et ses octets non plus", r2["jamais"] == 4000)

    # Un lien symbolique est un nom, pas des octets : le suivre compterait sa cible en plus.
    os.symlink(seul, d / "venvA" / "raccourci")
    r3 = peser([d / "venvA"])
    v("un lien symbolique ne pèse rien", r3["immediat"] == 1000)
    v("... et il est compté à part", r3["liens_symboliques"] == 1)

    r4 = peser([d / "nexiste_pas"])
    v("un chemin absent est signalé, pas une erreur", r4["chemins_introuvables"] == 1)
    v("... et ne pèse rien", r4["immediat"] == 0 and r4["inodes"] == 0)

    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("chemins", nargs="*", type=Path)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.chemins:
        p.error("au moins un chemin est requis")
    r = peser(a.chemins)
    print(f"{' '.join(str(c) for c in a.chemins)}  ·  {r['inodes']} inode(s) distincts")
    print("  nlink  fichiers      octets")
    for n, d in r["par_liens"].items():
        print(f"  {n:>5}  {d['fichiers']:>8}  {d['octets'] / GIO:>8.2f} Gio")
    print(f"\n  libéré immédiatement      {r['immediat'] / GIO:.2f} Gio")
    print(f"  libéré après `uv cache prune`  {r['apres_prune'] / GIO:.2f} Gio")
    print(f"  ⚠ jamais (tenu ailleurs)  {r['jamais'] / GIO:.2f} Gio")
    if r["chemins_introuvables"]:
        print(f"  ⚠ {r['chemins_introuvables']} chemin(s) introuvable(s)")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
