#!/usr/bin/env python3
"""Découper un `tifxyz` en morceaux de la taille d'un autre, pour comparer ce qui est comparable.

⚠⚠ POURQUOI CE FICHIER EXISTE. Toute la lecture du corpus repose sur une hypothèse que rien
n'avait jamais mise à l'épreuve : que **notre** chaîne de rendu produit des piles comparables
à celles que la communauté publie. Si notre rendu écrase le relief, alors « nos traces sont
plates » ne dit rien sur nos traces — c'est une propriété de notre instrument, et le
classement des huit candidats est un artefact.

Le témoin est direct, et il est possible parce que **le maillage publié est dans le format
exact du nôtre** : `meta.json` + `x.tif`/`y.tif`/`z.tif`, `format: tifxyz`, `scale: 0.05`.
On prend donc une surface publiée, on la rend AVEC NOTRE CHAÎNE, et on lit son relief à la
géométrie du corpus. Si elle revient à la valeur publiée, notre chaîne est fidèle ; si elle
s'effondre, c'est elle qu'il faut réparer avant de juger quoi que ce soit d'autre.

⚠ Un segment publié fait 2530 × 1820 points de grille quand nos candidats en font 120 × 119.
On ne peut donc pas rendre le segment entier — et **on ne le voudrait pas** : le relief
dépend de l'étendue lue (exposant −0,830), donc le témoin doit avoir la taille de ce qu'il
contrôle. D'où le découpage, et d'où `--comme`, qui lit cette taille dans le candidat plutôt
que de la faire retaper.

Trois refus, chacun payé ailleurs dans ce dépôt :

  1. **La bbox est RECALCULÉE**, jamais recopiée. Une bbox de segment entier posée sur un
     morceau ferait chercher au moteur de rendu une région de volume qui n'a rien à voir
     avec la surface qu'il tient. Le rendu réussirait et serait vide.
  2. **Un morceau troué est refusé.** Un point invalide vaut −1 dans les trois images. Un
     morceau à moitié absent se rendrait quand même, et on comparerait alors le bouchage de
     trous, pas la surface.
  3. **`area_vx2` est OMIS et non recopié.** C'est l'aire du segment entier ; la garder sur
     un morceau serait un chiffre faux dans un fichier qui a l'air juste.

Le choix des morceaux n'a **aucun aléa** : on énumère les positions valides sur un pas
régulier, puis on en garde N réparties uniformément dans cette liste. Un tirage aurait
demandé une graine, donc une chose de plus à garder juste pour rejouer.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INVALIDE = 0.0  # ⚠ un point absent est <= 0 dans les trois images, pas NaN.


def lire_tifxyz(dossier: Path):
    """Les trois images et la métadonnée d'un `tifxyz`.

    ⚠ Les trois doivent avoir la MÊME forme : un x et un y de tailles différentes ne
    décrivent pas une grille, et l'erreur se lirait plus loin comme un décalage de surface.
    """
    import tifffile

    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    formes = {n: a.shape for n, a in plans.items()}
    if len(set(formes.values())) != 1:
        raise ValueError(f"les trois images n'ont pas la même forme : {formes}")
    return plans, meta


def masque_valide(plans) -> "any":
    """Vrai là où le point de grille porte une position de volume.

    ⚠ Les trois plans doivent être valides ENSEMBLE. Un point dont seul le z manque n'est
    pas un point : le rendre reviendrait à poser la surface sur z = −1.
    """
    return (plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE)


def bbox_du_morceau(plans, r0: int, c0: int, hauteur: int, largeur: int):
    """La bbox des points VALIDES du morceau, en coordonnées de volume.

    ⚠⚠ Recalculée et jamais recopiée : c'est le refus n°1 de l'en-tête. Et calculée sur les
    seuls points valides, sinon le −1 des trous tire le minimum à −1 sur les trois axes.
    """
    import numpy as np

    sous = {n: a[r0:r0 + hauteur, c0:c0 + largeur] for n, a in plans.items()}
    bon = masque_valide(sous)
    if not bon.any():
        raise ValueError("morceau entièrement vide")
    bas = [float(np.min(sous[n][bon])) for n in ("x", "y", "z")]
    haut = [float(np.max(sous[n][bon])) for n in ("x", "y", "z")]
    return [bas, haut]


def positions_pleines(plans, hauteur: int, largeur: int, pas: int) -> list[tuple[int, int]]:
    """Les coins haut-gauche des morceaux SANS AUCUN trou, énumérés sur un pas régulier.

    ⚠ « sans aucun trou » et non « peu de trous » : c'est le refus n°2. Un seuil de trous
    tolérés serait un nombre choisi pour que le tirage du jour passe.
    """
    import numpy as np

    bon = masque_valide(plans)
    # Somme intégrale : le compte de points valides d'un rectangle en quatre lectures.
    cumul = np.zeros((bon.shape[0] + 1, bon.shape[1] + 1), dtype=np.int64)
    cumul[1:, 1:] = np.cumsum(np.cumsum(bon.astype(np.int64), axis=0), axis=1)
    plein = hauteur * largeur
    out = []
    for r0 in range(0, bon.shape[0] - hauteur + 1, pas):
        for c0 in range(0, bon.shape[1] - largeur + 1, pas):
            n = (cumul[r0 + hauteur, c0 + largeur] - cumul[r0, c0 + largeur]
                 - cumul[r0 + hauteur, c0] + cumul[r0, c0])
            if n == plein:
                out.append((r0, c0))
    return out


def repartir(positions: list, combien: int) -> list:
    """`combien` éléments répartis uniformément dans la liste, extrêmes compris.

    ⚠ Prendre les `combien` premiers les entasserait tous en haut de la grille, donc le
    témoin porterait sur un seul endroit de la surface en ayant l'air d'en couvrir plusieurs.

    ⚠⚠ L'arrondi est `int(x + 0.5)` et PAS `round()`, pour la raison que
    `tools/profiler_une_surface.sh` a déjà écrite : `round()` arrondit au PAIR, donc un
    lecteur qui vérifie l'indice à la main obtient un autre nombre que le programme. Sur
    cinq morceaux d'une liste de cent, les deux tombent d'accord ; c'est justement le genre
    d'accord qui ne tient pas au cas suivant.
    """
    if combien <= 0 or not positions:
        return []
    if combien >= len(positions):
        return list(positions)
    if combien == 1:
        return [positions[len(positions) // 2]]
    pas = (len(positions) - 1) / (combien - 1)
    return [positions[int(i * pas + 0.5)] for i in range(combien)]


def ecrire_morceau(plans, meta, r0, c0, hauteur, largeur, dest: Path) -> dict:
    """Un `tifxyz` autonome pour un morceau, avec sa propre bbox."""
    import tifffile

    dest.mkdir(parents=True, exist_ok=True)
    for n, a in plans.items():
        tifffile.imwrite(str(dest / f"{n}.tif"), a[r0:r0 + hauteur, c0:c0 + largeur])
    sortie = {
        "bbox": bbox_du_morceau(plans, r0, c0, hauteur, largeur),
        "format": "tifxyz",
        # ⚠ `scale` est une propriété de la GRILLE et ne change pas au découpage : c'est le
        # pas entre deux points, pas une taille.
        "scale": meta.get("scale", [0.05, 0.05]),
        "type": meta.get("type", "seg"),
        "uuid": dest.name,
        # ⚠ La provenance voyage avec le morceau. Un tifxyz relu dans six mois n'a pas la
        # ligne de commande qui l'a produit à côté.
        "decoupe_de": meta.get("uuid", "?"),
        "decoupe_origine": [int(r0), int(c0)],
        "decoupe_taille": [int(hauteur), int(largeur)],
    }
    (dest / "meta.json").write_text(json.dumps(sortie, indent=4), encoding="utf-8")
    return sortie


def verifier() -> int:
    """Les témoins hors ligne, sur une grille fabriquée ici.

    ⚠⚠ Chacun a son cas NÉGATIF : une découpe qui accepterait un trou, une bbox recopiée,
    une répartition qui entasse. Sans eux la batterie serait verte pour la seule raison
    qu'elle ne demande rien.
    """
    import numpy as np

    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    grille = np.zeros((20, 30), dtype=np.float32)
    for r in range(20):
        for c in range(30):
            grille[r, c] = 1000.0 + r * 10 + c
    plans = {"x": grille.copy(), "y": grille.copy() + 5000.0, "z": grille.copy() + 9000.0}

    bon = masque_valide(plans)
    v("une grille pleine est pleine", bool(bon.all()))

    # Un trou : les trois plans à -1 au même point.
    for n in plans:
        plans[n][7, 11] = -1.0
    v("un point à -1 est invalide", not bool(masque_valide(plans)[7, 11]))
    v("... et lui seul", int(masque_valide(plans).sum()) == 20 * 30 - 1)

    # ⚠ Un point dont un SEUL plan manque n'est pas un point.
    p2 = {n: a.copy() for n, a in plans.items()}
    p2["z"][3, 3] = -1.0
    v("un z absent suffit à invalider", not bool(masque_valide(p2)[3, 3]))

    pos = positions_pleines(plans, 5, 5, 1)
    v("le trou exclut les morceaux qui le contiennent",
      all(not (r <= 7 < r + 5 and c <= 11 < c + 5) for r, c in pos))
    v("... et il en reste", len(pos) > 0)
    # Cas négatif : sans le trou, il y en a strictement plus.
    plein = positions_pleines({n: np.abs(a) for n, a in plans.items()}, 5, 5, 1)
    v("sans trou il y a plus de positions", len(plein) > len(pos),
      f"{len(plein)} contre {len(pos)}")

    v("le pas espace les positions", len(positions_pleines(plans, 5, 5, 4)) < len(pos))

    b = bbox_du_morceau(plans, 0, 0, 5, 5)
    v("la bbox du coin est celle du coin", b[0] == [1000.0, 6000.0, 10000.0])
    v("... et son haut aussi", b[1] == [1044.0, 6044.0, 10044.0])
    b2 = bbox_du_morceau(plans, 10, 10, 5, 5)
    # ⚠⚠ LE CAS NÉGATIF DU REFUS N°1 : deux morceaux différents DOIVENT avoir deux bboxes
    # différentes. Une bbox recopiée les rendrait identiques, et le rendu chercherait le
    # volume du segment entier pour une surface de 5 points de côté.
    v("deux morceaux ont deux bboxes", b != b2)
    v("... et le second est plus loin", b2[0][0] > b[0][0])

    # ⚠ La bbox ignore les trous : sinon le -1 tire le minimum à -1 sur les trois axes.
    b3 = bbox_du_morceau(plans, 5, 9, 5, 5)
    v("un trou ne tire pas la bbox à -1", min(b3[0]) > 0.0, f"{b3[0]}")

    v("un morceau vide est refusé", _leve(lambda: bbox_du_morceau(
        {n: np.full((5, 5), -1.0, dtype=np.float32) for n in "xyz"}, 0, 0, 5, 5)))

    liste = list(range(100))
    v("répartir prend les extrêmes", repartir(liste, 5)[0] == 0 and repartir(liste, 5)[-1] == 99)
    # ⚠⚠ Ma première version de ce contrôle attendait [0, 25, 50, 75, 99] et le programme
    # rendait 74 au milieu — l'assertion avait tort, pas le code : 74,25 est bien plus proche
    # de 74. Une valeur attendue tapée à la main est une seconde implémentation, et elle peut
    # être la fausse des deux. La PROPRIÉTÉ, elle, ne se tape pas : les écarts sont réguliers.
    ecarts = [b - a for a, b in zip(repartir(liste, 5), repartir(liste, 5)[1:])]
    v("... et espace le reste", max(ecarts) - min(ecarts) <= 1, f"{ecarts}")
    v("... exactement, quand ça tombe juste", repartir(list(range(9)), 5) == [0, 2, 4, 6, 8])
    v("répartir n'invente rien", len(repartir(liste, 200)) == 100)
    v("un seul morceau est pris au milieu", repartir(liste, 1) == [50])
    # ⚠ Cas négatif de la répartition : les cinq premiers seraient tous en tête de liste.
    v("répartir ne prend pas les premiers", repartir(liste, 5) != liste[:5])

    v("trois formes différentes sont refusées",
      _leve(lambda: _formes_incoherentes()))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def _formes_incoherentes():
    import numpy as np

    formes = {"x": (4, 4), "y": (4, 5), "z": (4, 4)}
    plans = {n: np.zeros(f, dtype=np.float32) for n, f in formes.items()}
    if len({a.shape for a in plans.values()}) != 1:
        raise ValueError("les trois images n'ont pas la même forme")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("source", nargs="?", help="dossier tifxyz à découper")
    p.add_argument("--dest", help="dossier où écrire les morceaux")
    p.add_argument("--comme", help="tifxyz dont on copie la taille de grille")
    p.add_argument("--taille", nargs=2, type=int, metavar=("LIGNES", "COLONNES"))
    p.add_argument("--nombre", type=int, default=4)
    p.add_argument("--pas", type=int, default=0,
                   help="pas d'énumération, 0 = un quart du côté du morceau")
    p.add_argument("--json", help="où écrire le compte rendu")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.source or not a.dest:
        p.error("source et --dest requis")

    plans, meta = lire_tifxyz(Path(a.source))
    if a.comme:
        import tifffile
        ref = tifffile.imread(str(Path(a.comme) / "x.tif"))
        hauteur, largeur = int(ref.shape[0]), int(ref.shape[1])
        print(f"taille lue dans {a.comme} : {hauteur} × {largeur}")
    elif a.taille:
        hauteur, largeur = a.taille
    else:
        p.error("--comme ou --taille requis")

    forme = plans["x"].shape
    if hauteur > forme[0] or largeur > forme[1]:
        print(f"refus : morceau {hauteur}×{largeur} plus grand que la grille "
              f"{forme[0]}×{forme[1]}", file=sys.stderr)
        return 2

    pas = a.pas or max(1, min(hauteur, largeur) // 4)
    pos = positions_pleines(plans, hauteur, largeur, pas)
    print(f"grille {forme[0]} × {forme[1]}  ·  {len(pos)} position(s) sans trou "
          f"pour un morceau {hauteur} × {largeur} (pas {pas})")
    if not pos:
        print("refus : aucun morceau de cette taille n'est plein", file=sys.stderr)
        return 3

    choisies = repartir(pos, a.nombre)
    dest = Path(a.dest)
    rendu = []
    for i, (r0, c0) in enumerate(choisies):
        d = dest / f"morceau_{i:02d}"
        m = ecrire_morceau(plans, meta, r0, c0, hauteur, largeur, d)
        etendue = [round(m["bbox"][1][k] - m["bbox"][0][k], 1) for k in range(3)]
        print(f"  {d.name}  origine ({r0}, {c0})  étendue {etendue} voxels")
        rendu.append({"dossier": str(d), "origine": [r0, c0], "bbox": m["bbox"]})

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps({
            "source": str(a.source), "grille": list(forme),
            "taille": [hauteur, largeur], "pas": pas,
            "positions_pleines": len(pos), "morceaux": rendu,
        }, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
