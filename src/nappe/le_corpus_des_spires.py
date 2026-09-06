#!/usr/bin/env python3
"""Le corpus des spires : la matière que lisent tous les dérouleurs, vraie ou fabriquée.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. Cinq modules de `src/nappe/` ouvraient chacun la même chose —
l'index des spires publiées, leur grille, l'écart inter-feuilles — avec cinq copies de la même
boucle. Deux implémentations d'un même geste ne restent pas égales, et ici la conséquence serait
que deux dérouleurs comparés ne marcheraient pas sur la même matière : leur écart mesurerait leur
désaccord de lecture.

⭐ Et la seconde moitié est celle qui compte : la lecture vit désormais **hors** de la mesure,
donc le chemin qui produit le nombre publié peut tourner **hors ligne** sur une matière
fabriquée. Sans ça, le seul chemin non testé d'un module était celui qui produit son nombre — le
défaut mesuré dans [`80`], et payé le 2026-09-05 par un patch à moitié appliqué que la batterie
n'a pas vu.

Usage :
    uv run python src/nappe/le_corpus_des_spires.py --verifier
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
for _d in ("commun", "nappe", "encre"):
    sys.path.insert(0, str(RACINE / "src" / _d))

WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"

# ⚠ La fixture hors ligne emprunte la géométrie du fragment — 2,215 µm de voxel, 135,5 µm entre
# spires — plutôt que des nombres ronds : un corpus dont le pas ne ressemble pas au vrai ferait
# marcher le dérouleur à une longueur qu'il ne rencontre jamais, et une marche calibrée sur une
# autre échelle ne prouve rien sur celle-ci.
VOXEL_UM_FIXTURE = 2.215
ECART_UM_FIXTURE = 135.5


def corpus_publie() -> dict:
    """La matière que la mesure lit : l'écart entre spires, et la grille de chaque spire publiée.

    ⚠⚠⚠ POURQUOI CETTE LECTURE EST SÉPARÉE DE `mesurer`, ET C'EST UNE DETTE DU DÉPÔT ENTIER.
    Tant qu'elle vivait DANS la mesure, le chemin qui produit le nombre publié ne pouvait pas
    tourner hors ligne — donc la batterie ne testait que les briques, jamais leur assemblage.
    Une batterie verte sur un module dont le seul chemin non testé est celui qui produit le
    nombre publié est une batterie qui ne peut pas échouer là où ça compte : le 2026-09-05, un
    patch à moitié appliqué a laissé l'enregistrement référencer des variables inexistantes, et
    la batterie est restée verte parce qu'elle n'appelait pas `mesurer`.

    ⚠⚠ CE QUI EST INJECTABLE EST LA MATIÈRE, PAS LE DÉCOUPAGE. La boîte, le seuil de cellules,
    le choix des encadrements, la marche et tout l'enregistrement restent dans `mesurer`, donc
    restent couverts par une fixture. Injecter un corpus déjà découpé ferait sortir du test la
    moitié même de ce qu'on voulait tester.

    ⚠ L'écart entre spires et la taille du voxel voyagent AVEC les grilles plutôt qu'à côté :
    une fixture dont la géométrie ne s'accorderait pas avec le pas mesurerait un dérouleur qu'on
    a fait marcher à la mauvaise longueur, ce qui ressemble à un dérouleur mauvais.
    """
    from le_pas_normal_atteint_la_spire import grille  # noqa: PLC0415
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415

    if not WRAPS.is_file():
        raise RuntimeError(f"mesure absente : {WRAPS}")
    grilles = {}
    for w in wraps_du_fragment():
        g = grille(w, VOLUME, VOXEL_UM)
        if g is None:
            continue
        grilles[w["rang"]] = g
    return dict(volume=VOLUME, voxel_um=VOXEL_UM,
                ecart_um=float(json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]),
                grilles=grilles)


def corpus_fabrique(spires: int = 6, cellules: int = 14, ondulation: float = 3.0,
                    rayon_vx: float = 4000.0, creuse: int | None = None,
                    decalage_vx: float = 0.0) -> dict:
    """Un corps de spires concentriques fabriqué de toutes pièces, sans rien lire.

    ⚠⚠⚠ CE QUE CETTE FIXTURE EXISTE POUR EXERCER : le chemin qui produit le nombre publié, dans
    son entier — le découpage par la boîte, le seuil de cellules, le choix des encadrements, le
    signe de la normale, la marche, la combinaison, la pondération et l'enregistrement. Ce qui
    est vérifié dessus n'est jamais une VALEUR : la fixture n'est pas le fragment, donc ses
    micromètres ne veulent rien dire. Ce qui est vérifié, ce sont les invariants que la mesure
    revendique et les clés qu'elle promet à ses lecteurs.

    ⚠⚠ LES SPIRES SONT ONDULÉES, ET C'EST LE POINT LE PLUS FACILE À RATER. Des cylindres
    parfaitement décalés de `pas_vx` sont atteints EXACTEMENT par un pas normal : toutes les
    erreurs vaudraient zéro, la division du gain lèverait, et le verdict « l'encadrement bat les
    deux branches » serait décidé par des zéros. Une fixture sur laquelle la mesure ne peut rien
    trouver est le cas le plus pur d'un contrôle satisfait pour la mauvaise raison.

    ⚠ La phase de l'ondulation TOURNE d'une spire à l'autre. Une ondulation en phase serait, elle
    aussi, un décalage exact : la marche retomberait juste et on aurait fabriqué le même
    dégénéré, une fonction plus loin.

    ⚠ Le rayon est grand devant la boîte, donc la courbure est douce et les cellules restent
    dans la découpe. Une spire trop courbée sortirait de la boîte par ses bords et la fixture
    mesurerait le découpage plutôt que la marche.

    ⚠⚠ `creuse` et `decalage_vx` existent pour que les deux REFUS de la mesure puissent être
    exercés, et pas seulement son chemin heureux : une spire dont il ne reste presque rien doit
    être écartée — sans quoi le seuil de cellules serait un nombre que rien ne fait respecter —
    et un corpus posé hors de la boîte ne doit rendre AUCUN triplet, sans quoi le découpage
    serait décoratif.
    """
    from le_raccrochage_a_la_matiere import BOITE_CENTRE  # noqa: PLC0415

    voxel_um, ecart_um = VOXEL_UM_FIXTURE, ECART_UM_FIXTURE
    pas_vx = ecart_um / voxel_um
    centre = np.array(BOITE_CENTRE, dtype=np.float64)
    # Le centre de courbure est posé à `rayon_vx` de la boîte, sur x : la spire du milieu passe
    # donc par le centre de la boîte, et les autres se rangent de part et d'autre.
    foyer = centre - np.array([rayon_vx - decalage_vx, 0.0, 0.0])
    milieu = (spires + 1) / 2.0
    demi = (cellules - 1) / 2.0
    # Le pas angulaire donne une maille tangentielle du même ordre que la maille en z : une
    # grille très allongée rendrait des normales dominées par un seul axe.
    dtheta = 10.0 / rayon_vx
    tau = 2.0 * np.pi
    grilles = {}
    for k in range(1, spires + 1):
        rayon = rayon_vx + (k - milieu) * pas_vx
        a = np.empty((cellules, cellules, 3), dtype=np.float64)
        for i in range(cellules):
            th = (i - demi) * dtheta
            for j in range(cellules):
                # L'ondulation dépend des DEUX axes de la grille : une surface qui n'ondulerait
                # que le long d'un axe laisserait la seconde tangente exacte, donc n'exercerait
                # qu'une moitié du calcul de normale.
                r = (rayon
                     + ondulation * np.sin(tau * i / cellules + 0.7 * k)
                     + 0.5 * ondulation * np.cos(tau * j / cellules - 0.4 * k))
                a[i, j] = foyer + np.array([r * np.cos(th), r * np.sin(th),
                                            (j - demi) * 10.0])
        ok = np.ones((cellules, cellules), dtype=bool)
        if k == creuse:
            # Il en reste trois cellules : de quoi prouver que la spire est LUE et écartée pour
            # ce qu'elle porte, alors qu'une spire absente de la table ne prouverait que sa
            # propre absence.
            ok[:] = False
            ok[0, :3] = True
        grilles[k] = (a, ok)
    return dict(volume="fixture", voxel_um=voxel_um, ecart_um=ecart_um, grilles=grilles)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    c = corpus_fabrique()
    # ⚠⚠ LA FIXTURE DOIT AVOIR EXACTEMENT LA FORME DU VRAI LECTEUR, sinon elle exerce une forme
    # qui n'arrive jamais. Les clés du corpus publié sont lues dans l'arbre plutôt que recopiées :
    # une clé ajoutée là-bas et oubliée ici ferait passer toutes les batteries sur un corpus
    # périmé, en silence.
    retour = next(n for n in ast.walk(ast.parse(Path(__file__).read_text(encoding="utf-8")))
                  if isinstance(n, ast.FunctionDef) and n.name == "corpus_publie")
    promises = {k.arg for n in ast.walk(retour) if isinstance(n, ast.Call)
                and getattr(n.func, "id", None) == "dict" for k in n.keywords}
    v("le corpus fabriqué a exactement la forme du corpus publié",
      set(c) == promises, f"{sorted(promises)}")
    v("... et il porte le nombre de spires demandé", len(c["grilles"]) == 6,
      str(sorted(c["grilles"])))
    v("... chaque spire est une grille carrée de points en trois dimensions",
      all(a.shape == (14, 14, 3) and ok.shape == (14, 14) for a, ok in c["grilles"].values()))

    # ⚠⚠⚠ LA PROPRIÉTÉ QUI REND LA FIXTURE UTILISABLE : les spires sont ESPACÉES du pas, donc un
    # dérouleur qui marche droit avance d'une spire par tour. Sans elle, la fixture mesurerait un
    # dérouleur qu'on aurait fait marcher à la mauvaise longueur.
    # ⚠ L'écart se mesure entre cellules de MÊME indice : deux spires partagent leur
    # paramétrage, donc leur différence est purement radiale et n'a besoin d'aucun centre de
    # courbure. Le redériver ici en écrirait une seconde fois, et deux descriptions d'une même
    # géométrie finissent par ne pas s'accorder.
    pas_vx = c["ecart_um"] / c["voxel_um"]
    centres = {k: a[7, 7] for k, (a, _) in c["grilles"].items()}
    ecarts = [float(np.linalg.norm(centres[k + 1] - centres[k]))
              for k in sorted(centres)[:-1]]
    v("les spires sont espacées du pas, à l'ondulation près",
      all(abs(e - pas_vx) < 2 * 3.0 for e in ecarts),
      f"{[round(e, 1) for e in ecarts]} contre {pas_vx:.1f}")
    # ⚠⚠ ET ELLES NE SONT PAS DES DÉCALAGES EXACTS : des spires parfaitement décalées sont
    # atteintes EXACTEMENT par un pas normal, donc toute erreur mesurée dessus vaudrait zéro et
    # toute comparaison serait satisfaite par des zéros. C'est la garde qui doit rougir si
    # l'ondulation disparaît un jour.
    v("... mais aucune n'est un décalage exact de sa voisine",
      all(abs(e - pas_vx) > 1e-6 for e in ecarts),
      f"écarts au pas : {[round(e - pas_vx, 2) for e in ecarts]}")

    # ⚠ Les deux refus que les mesures doivent pouvoir exercer.
    creux = corpus_fabrique(creuse=3)
    v("une spire creuse ne garde que trois cellules valides",
      int(creux["grilles"][3][1].sum()) == 3, str(int(creux["grilles"][3][1].sum())))
    v("... et les autres restent entières",
      all(int(ok.sum()) == 196 for k, (_, ok) in creux["grilles"].items() if k != 3))
    loin = corpus_fabrique(decalage_vx=5000.0)
    v("un corpus décalé s'éloigne vraiment de la boîte",
      float(np.linalg.norm(loin["grilles"][1][0][7, 7] - c["grilles"][1][0][7, 7])) > 4000.0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    c = corpus_publie()
    print(json.dumps(dict(volume=c["volume"], voxel_um=c["voxel_um"], ecart_um=c["ecart_um"],
                          spires=sorted(c["grilles"])), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
