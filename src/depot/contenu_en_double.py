#!/usr/bin/env python3
"""Combien d'octets de `data/` sont du contenu DÉJÀ présent ailleurs — par hachage, pas par nom.

⚠⚠ POURQUOI CE FICHIER EXISTE. Le plan de ménage (`56`) annonçait « 17,4 Go de doublons » sur
la foi d'un proxy *même nom + même taille*, en écrivant lui-même que ce proxy **surcompte** :
ce sont des chunks zarr nommés `40`, `41`… de 2 Mio, qui portent le même nom dans des volumes
différents **sans être le même contenu**. Un effacement fondé là-dessus détruirait des données
qu'aucun téléchargement ne rendrait à l'identique.

  ⭐ La règle : deux fichiers ne sont déclarés identiques que si leur CONTENU l'est. Jamais
    leur nom, jamais leur taille, jamais leur date.

⚠ Ce fichier **ne supprime rien**. Il mesure et il nomme. Un effacement n'est pas réversible,
et la décision d'effacer appartient à qui a téléchargé les données — pas à l'outil qui les
compte.

⭐ Trois étages, du moins cher au plus cher, parce que hacher 177 Gio sans cela est absurde :

  1. la **taille** : un fichier dont la taille est unique dans tout l'arbre ne peut avoir aucun
     doublon, et il n'est jamais lu ;
  2. un **hachage partiel** (les premiers 64 Kio) qui casse les gros groupes de même taille ;
  3. le **hachage complet**, sur ce qui reste seulement.

⚠⚠ L'étage 2 ne conclut JAMAIS à lui seul. Deux fichiers qui partagent leurs premiers 64 Kio
et diffèrent ensuite existent réellement ici — un rendu et sa variante partagent leur en-tête.
S'arrêter au hachage partiel déclarerait identiques deux images différentes, et c'est
exactement la classe de faux positifs que ce fichier remplace.

⚠ Deux chemins vers le MÊME inode ne sont pas un doublon : ils partagent déjà leurs octets.
Les compter ferait annoncer une économie déjà réalisée (cf. `poids_recuperable.py`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
TETE = 65536
"""Octets lus pour le hachage partiel. Assez pour casser un groupe, trop peu pour conclure."""

IGNORES = (".git", ".venv", "__pycache__")


FENETRE = re.compile(r"rendu_(\d+)/(\d+)\.tif$")


def motif_du_groupe(chemins: list[str]) -> str:
    """Pourquoi ces fichiers sont identiques — « fenetres_imbriquees » ou « autre ».

    ⭐⭐ LA DÉCOUVERTE QUE CE CLASSEMENT EXISTE POUR NOMMER. Une fenêtre de 31 couches est le
    CENTRE d'une fenêtre de 81 couches rendue au même endroit : la tranche `i` de l'une est la
    tranche `i + (81-31)/2` de l'autre, **le même fichier**. Mesuré sur `data/` : 2232 groupes
    pour la paire (31, 81), 861 pour (41, 161) — c'est-à-dire exactement la série de
    convergence du dépôt.

    ⚠ La conséquence n'est pas un gain de disque, c'est un gain de TEMPS : rendre n=161
    produit déjà n=81 et n=41. Un cache indexé sur (surface, niveau, N) ne peut pas le voir,
    puisque N diffère ; seul un cache par TRANCHE le verrait.

    La règle testée : deux tranches sont la même quand leur distance au centre de leur propre
    fenêtre est la même. `i - (n-1)//2`.
    """
    ms = [FENETRE.search(c) for c in chemins]
    if not all(ms):
        return "autre"
    centres = {int(m.group(2)) - (int(m.group(1)) - 1) // 2 for m in ms}
    largeurs = {int(m.group(1)) for m in ms}
    if len(centres) != 1:
        return "autre"
    return "fenetres_imbriquees" if len(largeurs) > 1 else "meme_fenetre"


def _marcher(racine: Path) -> list[Path]:
    """Les fichiers réguliers, en élaguant à la traversée."""
    out, pile = [], [racine]
    while pile:
        d = pile.pop()
        try:
            entrees = list(d.iterdir())
        except OSError:
            continue
        for e in entrees:
            if e.name in IGNORES:
                continue
            try:
                if e.is_symlink():
                    continue
                if e.is_dir():
                    pile.append(e)
                elif e.is_file():
                    out.append(e)
            except OSError:
                continue
    return out


def empreinte(chemin: Path, octets: int | None = None) -> str:
    """SHA-256 du fichier, ou de ses `octets` premiers octets."""
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        if octets is None:
            for bloc in iter(lambda: f.read(1 << 20), b""):
                h.update(bloc)
        else:
            h.update(f.read(octets))
    return h.hexdigest()


def doublons(racine: Path, taille_min: int = 4096) -> dict:
    """Les groupes de fichiers au contenu identique, et ce qu'ils coûtent.

    `taille_min` écarte la poussière : un `meta.json` de trois cents octets répété mille fois
    pèse moins qu'une seule image, et le signaler noie ce qui compte.
    """
    par_taille: dict[int, list[tuple[Path, int, int]]] = defaultdict(list)
    vus_inodes: set[tuple[int, int]] = set()
    lus = partiels = complets = 0
    for f in _marcher(racine):
        try:
            st = f.stat()
        except OSError:
            continue
        lus += 1
        if st.st_size < taille_min:
            continue
        cle = (st.st_dev, st.st_ino)
        if cle in vus_inodes:
            continue                      # deuxième nom du même inode : déjà partagé
        vus_inodes.add(cle)
        par_taille[st.st_size].append((f, st.st_size, st.st_nlink))

    groupes = []
    for taille, entrees in par_taille.items():
        if len(entrees) < 2:
            continue                      # taille unique : jamais lu
        par_tete: dict[str, list] = defaultdict(list)
        for f, t, n in entrees:
            try:
                par_tete[empreinte(f, TETE)].append((f, t, n))
                partiels += 1
            except OSError:
                continue
        for candidats in par_tete.values():
            if len(candidats) < 2:
                continue                  # la tête suffit à les séparer
            par_complet: dict[str, list] = defaultdict(list)
            for f, t, n in candidats:
                try:
                    par_complet[empreinte(f)].append((f, t, n))
                    complets += 1
                except OSError:
                    continue
            for h, memes in par_complet.items():
                if len(memes) < 2:
                    continue
                groupes.append({
                    "empreinte": h[:16],
                    "taille": taille,
                    "copies": len(memes),
                    "recuperable": taille * (len(memes) - 1),
                    "chemins": sorted(str(f) for f, _, _ in memes),
                    "motif": motif_du_groupe(sorted(str(f) for f, _, _ in memes)),
                })

    groupes.sort(key=lambda g: -g["recuperable"])
    return {
        "fichiers_vus": lus,
        "hachages_partiels": partiels,
        "hachages_complets": complets,
        "groupes": len(groupes),
        "recuperable": sum(g["recuperable"] for g in groupes),
        "par_motif": {m: sum(g["recuperable"] for g in groupes if g["motif"] == m)
                      for m in sorted({g["motif"] for g in groupes})},
        "detail": groupes,
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
    (d / "a").mkdir()
    (d / "b").mkdir()

    # deux fichiers vraiment identiques, dans deux campagnes differentes
    contenu = os.urandom(200000)
    (d / "a" / "rendu.png").write_bytes(contenu)
    (d / "b" / "rendu.png").write_bytes(contenu)

    # ⚠⚠ Le cas que le proxy « meme nom + meme taille » declare identique A TORT : meme nom,
    # meme taille, contenu different. C'est le chunk zarr `40` de deux volumes.
    (d / "a" / "40").write_bytes(b"X" * 300000)
    (d / "b" / "40").write_bytes(b"Y" * 300000)

    # ⚠⚠ Et le cas que le hachage PARTIEL declare identique a tort : meme en-tete, fin
    # differente. Un rendu et sa variante partagent leur en-tete.
    tete = os.urandom(TETE)
    (d / "a" / "variante.png").write_bytes(tete + b"A" * 100000)
    (d / "b" / "variante.png").write_bytes(tete + b"B" * 100000)

    # deja partages : un seul inode, deux noms
    (d / "a" / "lie.bin").write_bytes(b"Z" * 150000)
    os.link(d / "a" / "lie.bin", d / "b" / "lie.bin")

    # une taille unique : ne doit jamais etre lue
    (d / "a" / "seul.bin").write_bytes(b"S" * 77777)

    r = doublons(d)
    chemins = {c for g in r["detail"] for c in g["chemins"]}
    v("deux fichiers au contenu identique sont trouvés",
      any(g["copies"] == 2 and g["taille"] == 200000 for g in r["detail"]))
    v("... et ce qu'ils coûtent est UNE copie, pas deux",
      sum(g["recuperable"] for g in r["detail"] if g["taille"] == 200000) == 200000)
    v("même nom + même taille + contenu DIFFÉRENT n'est PAS un doublon",
      not any(c.endswith("/40") for c in chemins))
    v("même en-tête + fin différente n'est PAS un doublon",
      not any("variante" in c for c in chemins))
    v("deux noms d'un même inode ne comptent pas", not any("lie.bin" in c for c in chemins))
    v("un fichier de taille unique n'est jamais lu", not any("seul.bin" in c for c in chemins))

    # ⭐ Le contrôle des étages : la taille unique n'est jamais hachée, et le hachage complet
    # ne porte que sur ce que la tête n'a pas su séparer.
    v("le hachage partiel ne touche pas les tailles uniques", r["hachages_partiels"] == 6)
    v("le hachage complet est plus rare que le partiel",
      r["hachages_complets"] < r["hachages_partiels"])
    v("le compte de fichiers vus inclut tout", r["fichiers_vus"] >= 9)

    # --- le MOTIF : pourquoi ces fichiers sont identiques ---
    # ⭐⭐ Le fait mesuré que ce classement existe pour nommer : une fenetre de 31 couches est
    # le CENTRE d'une fenetre de 81, donc la tranche i de l'une est la tranche i+25 de l'autre.
    v("deux tranches a la meme distance du centre sont des fenetres imbriquees",
      motif_du_groupe(["a/rendu_31/30.tif", "a/rendu_81/55.tif"]) == "fenetres_imbriquees")
    v("... et la regle tient sur une autre paire de la serie",
      motif_du_groupe(["a/rendu_41/05.tif", "a/rendu_161/65.tif"]) == "fenetres_imbriquees")
    # ⚠ Le controle qui empeche le classement de tout avaler : deux tranches a des distances
    # DIFFERENTES du centre sont un doublon, mais pas celui-la.
    v("deux tranches a des distances differentes ne le sont PAS",
      motif_du_groupe(["a/rendu_31/30.tif", "a/rendu_81/56.tif"]) == "autre")
    v("la meme largeur de fenetre est un doublon de campagne, pas d'imbrication",
      motif_du_groupe(["a/rendu_81/55.tif", "b/rendu_81/55.tif"]) == "meme_fenetre")
    v("ce qui n'est pas un rendu de fenetre est « autre »",
      motif_du_groupe(["a/meta.json", "b/meta.json"]) == "autre")
    v("un melange rendu / non-rendu est « autre »",
      motif_du_groupe(["a/rendu_31/30.tif", "b/meta.json"]) == "autre")

    # la poussiere est ecartee, et le seuil est un ARGUMENT
    (d / "a" / "petit.json").write_bytes(b"{}" * 10)
    (d / "b" / "petit.json").write_bytes(b"{}" * 10)
    v("sous le seuil, un doublon est ignoré",
      not any("petit" in c for g in doublons(d)["detail"] for c in g["chemins"]))
    v("... mais un seuil plus bas le trouve",
      any("petit" in c for g in doublons(d, taille_min=1)["detail"] for c in g["chemins"]))

    v("le total par motif est le total tout court",
      sum(r["par_motif"].values()) == r["recuperable"])
    v("le total récupérable est la somme des groupes",
      r["recuperable"] == sum(g["recuperable"] for g in r["detail"]))
    v("les groupes sortent du plus coûteux au moins coûteux",
      [g["recuperable"] for g in r["detail"]] == sorted(
          (g["recuperable"] for g in r["detail"]), reverse=True))

    shutil.rmtree(d, ignore_errors=True)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("racine", nargs="?", type=Path, default=RACINE / "data")
    p.add_argument("--taille-min", type=int, default=4096,
                   help="octets en dessous desquels un doublon est de la poussière (défaut : 4096)")
    p.add_argument("--montrer", type=int, default=12, help="groupes les plus coûteux à lister")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.racine.is_dir():
        print(f"absent : {a.racine}", file=sys.stderr)
        return 1

    r = doublons(a.racine, a.taille_min)
    G = 1073741824
    print(f"{a.racine}  ·  {r['fichiers_vus']} fichiers vus  ·  "
          f"{r['hachages_partiels']} hachages partiels, {r['hachages_complets']} complets")
    print(f"  {r['groupes']} groupe(s) de contenu identique  ·  "
          f"récupérable {r['recuperable'] / G:.2f} Gio")
    for m, o in sorted(r["par_motif"].items(), key=lambda kv: -kv[1]):
        print(f"    {o / G:7.2f} Gio  {m}")
    for g in r["detail"][:a.montrer]:
        print(f"    {g['recuperable'] / G:6.3f} Gio  ×{g['copies']}  {g['chemins'][0]}")
        for c in g["chemins"][1:4]:
            print(f"                          = {c}")
    print("  ⚠ rien n'est supprimé : cet outil mesure et nomme.")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
