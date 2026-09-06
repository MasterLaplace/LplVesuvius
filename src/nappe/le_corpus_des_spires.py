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
TAU = 2.0 * np.pi


def geometrie_fabriquee(spires: int = 6, cellules: int = 14, ondulation: float = 3.0,
                        rayon_vx: float = 4000.0, decalage_vx: float = 0.0,
                        ecart_um: float = ECART_UM_FIXTURE) -> dict:
    """Où sont les feuilles de l'objet fabriqué — **la seule description**, et c'est le point.

    ⚠⚠⚠ DEUX VUES D'UN MÊME OBJET, PAS DEUX OBJETS. Un dérouleur lit les spires comme des
    **surfaces** (une grille de points) et le volume comme une **intensité** (des feuilles
    brillantes). Décrire l'objet deux fois ferait un corpus dont les feuilles ne sont pas là où
    le volume les met : le raccrochage snapperait alors sur de la matière qui contredit ses
    propres ancres, et la mesure rendrait des nombres parfaitement stables et absurdes. La
    géométrie est donc dite ici, et les deux vues la lisent.

    ⚠ Le centre de courbure est posé à `rayon_vx` de la boîte, sur x : la spire du milieu passe
    par le centre de la boîte, et les autres se rangent de part et d'autre.

    ⚠⚠ `ecart_um` existe pour un contrôle précis, et pas pour du réglage : donner au VOLUME un
    autre écart que celui du corpus permet de demander si une lecture suit la matière ou la
    fenêtre de recherche. Une lecture qui rendrait toujours le nominal passerait le premier
    contrôle et échouerait celui-là.
    """
    from le_raccrochage_a_la_matiere import BOITE_CENTRE  # noqa: PLC0415

    centre = np.array(BOITE_CENTRE, dtype=np.float64)
    return dict(
        voxel_um=VOXEL_UM_FIXTURE, ecart_um=ecart_um,
        pas_vx=ecart_um / VOXEL_UM_FIXTURE,
        foyer=centre - np.array([rayon_vx - decalage_vx, 0.0, 0.0]),
        rayon_vx=rayon_vx, spires=spires, cellules=cellules, ondulation=ondulation,
        milieu=(spires + 1) / 2.0, demi=(cellules - 1) / 2.0,
        # ⚠ Le pas angulaire donne une maille tangentielle du même ordre que la maille en z :
        # une grille très allongée rendrait des normales dominées par un seul axe.
        maille=10.0, dtheta=10.0 / rayon_vx)


def rayon_de_spire(g: dict, k, theta, z_local):
    """Le rayon de la spire `k` à l'angle `theta` et à la cote `z_local`, depuis le foyer.

    ⚠⚠ L'ondulation dépend des DEUX coordonnées : une surface qui n'ondulerait que le long d'un
    axe laisserait la seconde tangente exacte, donc n'exercerait qu'une moitié du calcul de
    normale. Et sa phase TOURNE d'une spire à l'autre — en phase, les spires resteraient des
    décalages exacts les unes des autres, donc un pas normal les atteindrait pile et toute
    erreur mesurée dessus vaudrait zéro.
    """
    i = np.asarray(theta) / g["dtheta"] + g["demi"]
    j = np.asarray(z_local) / g["maille"] + g["demi"]
    return (g["rayon_vx"] + (k - g["milieu"]) * g["pas_vx"]
            + g["ondulation"] * np.sin(TAU * i / g["cellules"] + 0.7 * k)
            + 0.5 * g["ondulation"] * np.cos(TAU * j / g["cellules"] - 0.4 * k))


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
    g = geometrie_fabriquee(spires, cellules, ondulation, rayon_vx, decalage_vx)
    foyer, demi = g["foyer"], g["demi"]
    grilles = {}
    for k in range(1, spires + 1):
        a = np.empty((cellules, cellules, 3), dtype=np.float64)
        for i in range(cellules):
            th = (i - demi) * g["dtheta"]
            for j in range(cellules):
                z_local = (j - demi) * g["maille"]
                r = rayon_de_spire(g, k, th, z_local)
                a[i, j] = foyer + np.array([r * np.cos(th), r * np.sin(th), z_local])
        ok = np.ones((cellules, cellules), dtype=bool)
        if k == creuse:
            # Il en reste trois cellules : de quoi prouver que la spire est LUE et écartée pour
            # ce qu'elle porte, alors qu'une spire absente de la table ne prouverait que sa
            # propre absence.
            ok[:] = False
            ok[0, :3] = True
        grilles[k] = (a, ok)
    return dict(volume="fixture", voxel_um=g["voxel_um"], ecart_um=g["ecart_um"],
                grilles=grilles)


def meta_fabriquee(bloc_vx: int = 64) -> dict:
    """Les métadonnées du volume fabriqué, dans la forme que le lecteur attend.

    ⚠ La FORME déclarée est celle du vrai volume : les points des spires vivent autour de
    (10615, 10571, 19831), donc un tableau plus petit les mettrait hors bornes et le lecteur
    répondrait « rien à cet endroit » — ce qui ressemble à un trou dans le scan. Rien n'est
    alloué : seuls les blocs réellement demandés sont fabriqués.

    ⚠⚠ Le bloc est plus PETIT que celui du dépôt (64 au lieu de 128) pour une raison mesurable
    et pas esthétique : un bloc fabriqué coûte son volume en calcul, et 128³ est huit fois
    2 097 152 voxels pour une ligne qui en traverse soixante. Ce que la mesure exerce est le
    GROUPEMENT par bloc, pas la taille du bloc du dépôt.
    """
    return dict(shape=[28096, 18209, 18209], chunks=[bloc_vx, bloc_vx, bloc_vx],
                dtype="|u1", compressor=None, dimension_separator="/")


def volume_fabrique(g: dict | None = None, bloc_vx: int = 64, portee_vx: float = 400.0,
                    pannes: int = 0, essais: int = 4):
    """Le volume de scan de l'objet fabriqué : ses feuilles vues comme une intensité.

    ⚠⚠⚠ C'EST LA SECONDE VUE DU MÊME OBJET, et l'intensité est dérivée de la géométrie plutôt
    que dessinée : un voxel vaut d'autant plus qu'il est proche de la feuille la plus proche.
    Un volume dessiné à part mettrait ses feuilles ailleurs que le corpus, et le raccrochage
    snapperait sur de la matière qui contredit ses propres ancres — en rendant des nombres
    parfaitement stables.

    ⚠⚠ Les blocs LOIN de l'objet sont déclarés ABSENTS, pas noirs. C'est ce que fait le vrai
    dépôt hors du masque, et c'est le seul moyen d'exercer la mémorisation d'une absence : un
    volume qui répondrait partout ne distinguerait jamais « rien ici » de « pas encore lu ».

    ⚠ `pannes` injecte des échecs de réseau TRANSITOIRES, comptés et réessayés. Cette logique a
    été écrite après un incident réel — un délai dépassé a jeté deux cent trente-deux blocs
    déjà téléchargés — et rien ne pouvait l'exercer tant que la requête vivait dans le lecteur.
    """
    from le_raccrochage_a_la_matiere import CacheDisque, Volume  # noqa: PLC0415

    g = geometrie_fabriquee() if g is None else g
    meta = meta_fabriquee(bloc_vx)
    foyer = g["foyer"]
    # ⚠ L'épaisseur d'une feuille est DÉRIVÉE du pas, pas choisie : un sixième de l'écart
    # inter-feuilles laisse entre deux crêtes un creux qui descend au bruit, ce qui est la
    # condition pour qu'un détecteur de pics en trouve deux et non un plateau.
    sigma = g["pas_vx"] / 6.0
    restant = {"pannes": int(pannes)}
    compte = {"blocs": 0, "absents": 0}

    def chercher(adresse: str) -> tuple[bytes | None, str | None]:
        if restant["pannes"] > 0:
            restant["pannes"] -= 1
            # ⚠ « le réseau n'a pas répondu » n'est PAS « absent du dépôt » : seul le second
            # autorise à mémoriser un trou, et les confondre graverait une absence qui n'existe
            # pas. Le lecteur doit réessayer celui-ci.
            return None, "reseau"
        cz, cy, cx = (int(x) for x in adresse.rsplit("/", 3)[1:])
        z0, y0, x0 = cz * bloc_vx, cy * bloc_vx, cx * bloc_vx
        coin = np.array([x0 + bloc_vx / 2, y0 + bloc_vx / 2, z0 + bloc_vx / 2])
        rayon_bloc = bloc_vx * np.sqrt(3.0) / 2.0
        if float(np.linalg.norm(coin - (foyer + np.array([g["rayon_vx"], 0.0, 0.0])))) \
                > portee_vx + rayon_bloc:
            compte["absents"] += 1
            return None, "absent"
        zz, yy, xx = np.meshgrid(np.arange(z0, z0 + bloc_vx, dtype=np.float64),
                                 np.arange(y0, y0 + bloc_vx, dtype=np.float64),
                                 np.arange(x0, x0 + bloc_vx, dtype=np.float64),
                                 indexing="ij")
        dx, dy, dz = xx - foyer[0], yy - foyer[1], zz - foyer[2]
        r = np.hypot(dx, dy)
        theta = np.arctan2(dy, dx)
        # La feuille la plus proche se trouve par le rayon seul : l'ondulation vaut quelques
        # voxels contre soixante d'écart, donc elle ne peut pas changer de voisine.
        k = np.rint((r - g["rayon_vx"]) / g["pas_vx"] + g["milieu"])
        ecart = r - rayon_de_spire(g, k, theta, dz)
        val = 255.0 * np.exp(-(ecart / sigma) ** 2)
        compte["blocs"] += 1
        return val.astype(np.uint8).tobytes(), None

    vol = Volume("fabrique://volume", meta, CacheDisque(actif=False), essais=essais,
                 chercher=chercher)
    vol.fabrique = compte
    return vol

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

    # ---- le volume fabriqué : la seconde vue du même objet ----
    from le_raccrochage_a_la_matiere import lisser, pas_entre_pics  # noqa: PLC0415

    g = geometrie_fabriquee()
    vol = volume_fabrique(g)
    axe = np.array([1.0, 0.0, 0.0])
    coeur = g["foyer"] + g["rayon_vx"] * axe
    t = np.arange(-160.0, 160.0, 1.0)
    profil, lus = vol.lire(coeur[None, :] + t[:, None] * axe[None, :])
    v("une ligne radiale traverse le volume fabriqué sans trou",
      bool(lus.all()), f"{int(lus.sum())} sur {len(t)} · {vol.fabrique['blocs']} blocs")
    v("... et elle y trouve du contraste, pas un plat",
      profil.max() > 200 and profil.min() < 20, f"{profil.min():.0f} à {profil.max():.0f}")
    # ⚠⚠⚠ LE CONTRÔLE QUI LIE LES DEUX VUES, et sans lui rien ne dirait qu'elles décrivent le
    # même objet : un volume décalé d'un demi-pas laisserait passer tout le reste. La tolérance
    # est DÉRIVÉE de l'ondulation — deux spires voisines peuvent glisser chacune de son
    # amplitude et demie, donc leur écart lu vaut le pas à trois amplitudes près.
    pic = pas_entre_pics(lisser(profil, 3), t)
    v("le pas entre crêtes du volume est celui qui sépare les spires du corpus",
      pic is not None and abs(pic - g["pas_vx"]) <= 3 * g["ondulation"],
      f"{pic} contre {g['pas_vx']:.1f} voxels, tolérance {3 * g['ondulation']:.0f}")
    # ⚠⚠ ET AU POINT PRÈS, pas seulement au pas : une feuille du corpus doit tomber sur une
    # crête du volume, et le milieu entre deux feuilles dans un creux. Un volume décalé aurait
    # le bon pas et la mauvaise phase.
    a_, ok_ = corpus_fabrique()["grilles"][3]
    pts = a_[ok_][:40]
    radial = pts - g["foyer"]
    radial[:, 2] = 0.0
    radial /= np.linalg.norm(radial, axis=1, keepdims=True)
    sur, _ = vol.lire(pts)
    entre, _ = vol.lire(pts + radial * (g["pas_vx"] / 2.0))
    v("une feuille du corpus tombe sur une crête du volume",
      float(np.median(sur)) > 200, f"{np.median(sur):.0f}")
    v("... et le milieu entre deux feuilles tombe dans un creux",
      float(np.median(entre)) < 20, f"{np.median(entre):.0f}")

    # ⚠⚠ LES TROIS RÉPONSES DU LECTEUR, qu'aucune batterie ne pouvait exercer tant que la
    # requête vivait dedans : une absence se mémorise, un incident se réessaie, un incident qui
    # persiste LÈVE. Les confondre fait soit jeter un balayage pour un hoquet, soit marteler le
    # dépôt pour des blocs qui n'existent pas.
    loin = volume_fabrique(g)
    _, ok_loin = loin.lire((coeur + np.array([2000.0, 0.0, 0.0]))[None, :])
    v("un bloc loin de l'objet est déclaré absent, et l'absence est mémorisée",
      not ok_loin.any() and loin.absents > 0 and loin.reprises == 0,
      f"absents {loin.absents} · reprises {loin.reprises}")
    hoquet = volume_fabrique(g, pannes=2)
    _, ok_h = hoquet.lire(coeur[None, :])
    v("un incident de réseau est réessayé et compté",
      bool(ok_h.all()) and hoquet.reprises == 2, str(hoquet.reprises))
    tetu = volume_fabrique(g, pannes=10 ** 6, essais=2)
    leve = None
    try:
        tetu.lire(coeur[None, :])
    except RuntimeError as exc:
        leve = str(exc)
    v("... mais un incident qui persiste LÈVE, il ne devient pas une absence",
      leve is not None and tetu.absents == 0, str(leve)[:60])

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
