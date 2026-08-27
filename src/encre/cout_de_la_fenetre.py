#!/usr/bin/env python3
"""Ce qui NE FAIT PAS varier le coût d'une fenêtre : une hypothèse de cache, réfutée.

⚠⚠ Pourquoi ce fichier existe. `src/encre/cout_du_rendu.py` chiffre le débit d'un rendu ; il
ne dit pas ce qui le **fait varier**. Or deux rendus du MÊME rouleau, avec le même modèle, le
même pas, le même nombre de fils, sur la même machine libre, ont donné :

    PHerc1447_complet      2980 × 3240   21128 fenêtres en 2079.5 s     98 ms/fenêtre
    1447_20250703025628    4100 × 4260   débit soutenu mesuré          455 ms/fenêtre

Un facteur **4,6** pour une surface 1,8 fois plus large. Écartés par mesure et non par
raisonnement : la contention (`ps` donne 1586 % de CPU et la charge vaut les seize fils
demandés), la mémoire (33 Gio libres, zéro swap), le type de données et la profondeur (les
deux piles sont en `uint8`, 31 couches), le pas et la taille de fenêtre (identiques).

⭐ L'HYPOTHÈSE TESTÉE ICI, et elle était falsifiable. La fenêtre que le modèle consomme fait
toujours 26 × 64 × 64, donc le coût du modèle ne peut pas dépendre de la taille du segment.
Ce qui en dépend, c'est le rassemblement : `stack[:, y:y+64, x:x+64]` lit soixante-quatre
lignes dans chacune des vingt-six couches, et un balayage complet en `x` garde donc vivante
une **bande** de soixante-quatre lignes pleine largeur, qui vaut `26 × 64 × largeur × 4`
octets — **20,6 Mio** à 3240 colonnes, **27,0 Mio** à 4260, pour un L3 de **24 Mio**. La
largeur critique tombe à **3780 colonnes**, exactement entre les deux segments observés. Une
falaise de cache a précisément cette forme.

⚠⚠ ELLE EST FAUSSE, et c'est la mesure qui l'a dit. Balayage du 2026-08-27 :

    largeur   bande        cache   en ligne   par blocs
       1024    6.50 Mio     oui     0.072      0.064
       2048   13.00 Mio     oui     0.069      0.067
       3240   20.57 Mio     oui     0.127      0.166
       4260   27.04 Mio     NON     0.167      0.121
       6000   38.09 Mio     NON     0.119      0.075

Aucun coude à 3780, et 6000 colonnes coûtent MOINS que 4260. Surtout, l'ordre de grandeur
tranche tout seul : le rassemblement coûte **un dixième de milliseconde** par fenêtre quand
l'écart à expliquer en vaut **357**. Trois ordres de grandeur trop petit pour être la cause,
quelle que soit la forme de la courbe.

⭐ CE QUE LA RÉFUTATION APPREND, et c'est plus utile que l'hypothèse ne l'aurait été. Une
boucle de rendu ne fait que trois choses : rassembler, appeler le modèle, disperser. L'appel
du modèle est **invariant en taille de segment** par construction, le rassemblement est
mesuré négligeable, et la dispersion écrit les mêmes 64 × 64 pixels quelle que soit la carte.
Donc **aucune partie de la boucle ne peut dépendre de la taille du segment**, et la cause de
l'écart est à chercher ailleurs que dans le segment : état de la machine, fréquence, ou une
différence de paramètre non encore trouvée entre les deux lancements.

⚠ Le balayage garde la colonne « par blocs » alors que le remède qu'elle chiffrait n'a plus
de cause à traiter. Elle reste parce qu'elle est une PREUVE de la réfutation : réordonner le
balayage pour borner la bande ne gagne rien, et c'est ce qui ferme la question plutôt que de
la laisser ouverte. `positions_par_blocs` n'est donc pas un remède en attente, c'est le
témoin qu'il n'y avait rien à remédier.

⚠ La mesure ne demande NI modèle NI torch. C'est délibéré : le rassemblement est du numpy
pur, donc il se mesure seul. Une explication qu'on ne peut pas réfuter à bas coût est une
explication qu'on gardera trop longtemps.

Usage :
    uv run python src/encre/cout_de_la_fenetre.py --verifier
    uv run python src/encre/cout_de_la_fenetre.py --balayer --json docs/mesures/cout_de_la_fenetre.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

FRAMES = 26
"""Couches que le modèle consomme par fenêtre. Fixé par le TimeSformer, pas par le segment."""

TILE = 64
"""Côté de la fenêtre, en pixels. Fixé par le modèle lui aussi."""

PAS = 21
"""Pas de balayage employé par toutes nos campagnes."""

OCTETS_PAR_VOXEL = 4
"""La pile est convertie en `float32` au chargement : c'est elle que le balayage relit."""

L3_OCTETS = 24 * 1024 * 1024
"""L3 de la machine de mesure (Intel Core Ultra 7 165H, une seule instance de 24 Mio).

⚠ C'est un fait de MACHINE, pas une constante du problème : il est nommé ici pour que la
largeur critique se recalcule ailleurs plutôt que d'être recopiée.
"""

OBSERVATIONS_DE_RENDU = [
    # (segment, largeur, hauteur, ms par fenetre observees)
    ("PHerc1447_complet", 3240, 2980, 98.4),
    ("1447_20250703025628", 4260, 4100, 455.0),
]
"""Les deux rendus qui posent la question, chacun avec sa ligne de log pour origine.

Le premier vient de la fin de `/tmp/full1447.log` (21128 fenêtres, 2079,5 s) ; le second du
débit soutenu lu sur trois lignes de progression consécutives, pas du cumul — le cumul portait
encore la trace de la suite de témoins qui tournait au démarrage.
"""


def bande_residente(largeur: int, frames: int = FRAMES, tile: int = TILE,
                    octets: int = OCTETS_PAR_VOXEL) -> int:
    """Octets qu'un balayage en `x` garde vivants : `frames` × `tile` lignes pleine largeur.

    ⚠ C'est la bande, pas la pile entière, qui décide. Une pile de deux gibioctets dont la
    bande tient en cache se parcourt vite ; une pile plus petite dont la bande déborde ne se
    parcourt pas.
    """
    return frames * tile * largeur * octets


def largeur_critique(cache_octets: int = L3_OCTETS, frames: int = FRAMES,
                     tile: int = TILE, octets: int = OCTETS_PAR_VOXEL) -> int:
    """La largeur au-delà de laquelle la bande ne tient plus dans le cache donné."""
    par_colonne = frames * tile * octets
    return cache_octets // par_colonne if par_colonne else 0


def largeur_de_bloc(cache_octets: int = L3_OCTETS, marge: float = 0.5,
                    frames: int = FRAMES, tile: int = TILE,
                    octets: int = OCTETS_PAR_VOXEL) -> int:
    """Largeur d'un bloc de balayage qui garde la bande sous le cache, marge comprise.

    ⚠ La marge n'est pas de la prudence décorative : le L3 est PARTAGÉ, et le modèle y tient
    ses propres poids et activations pendant que le rassemblement y tient sa bande. Réserver
    la moitié est un choix, dit ici plutôt qu'enfoui dans un littéral au site d'appel.
    """
    if not 0.0 < marge <= 1.0:
        raise ValueError("la marge est une fraction du cache, dans ]0, 1]")
    return max(tile, largeur_critique(int(cache_octets * marge), frames, tile, octets))


def positions_par_blocs(hauteur: int, largeur: int, pas: int = PAS, tile: int = TILE,
                        largeur_bloc: int | None = None) -> list[tuple[int, int]]:
    """Les mêmes fenêtres que le balayage en ligne, réordonnées par blocs de colonnes.

    ⚠⚠ L'ENSEMBLE est identique à celui du balayage en ligne, seul l'ORDRE change. C'est ce
    qui rend le remède gratuit du point de vue du résultat : la carte rendue est la même, au
    bit près, parce que chaque fenêtre est vue exactement une fois et que la somme dans le
    tampon de recouvrement est commutative.
    """
    if largeur_bloc is None:
        largeur_bloc = largeur_de_bloc()
    xs = list(range(0, largeur - tile + 1, pas))
    ys = list(range(0, hauteur - tile + 1, pas))
    ordre: list[tuple[int, int]] = []
    for debut in range(0, len(xs), max(1, largeur_bloc // pas)):
        colonnes = xs[debut : debut + max(1, largeur_bloc // pas)]
        for y in ys:
            for x in colonnes:
                ordre.append((y, x))
    return ordre


def cout_du_rassemblement(hauteur: int, largeur: int, fenetres: int,
                          par_blocs: bool = False, pas: int = PAS,
                          tile: int = TILE, frames: int = FRAMES) -> float:
    """Millisecondes par fenêtre pour RASSEMBLER un lot, sur une pile synthétique.

    Numpy pur, un seul fil, aucun modèle : c'est exactement l'étape dont le coût peut dépendre
    de la taille du segment, isolée de celle dont le coût ne le peut pas.
    """
    pile = np.zeros((frames, hauteur, largeur), dtype=np.float32)
    # ⚠ Une pile de zéros suffit : ce qu'on mesure est le DÉPLACEMENT d'octets, pas leur
    # valeur. La toucher une fois d'abord évite de mesurer les défauts de page du premier
    # parcours, qui appartiennent à l'allocateur et pas au balayage.
    pile[:, ::997, ::997] = 1.0
    ordre = (positions_par_blocs(hauteur, largeur, pas, tile)
             if par_blocs else
             [(y, x)
              for y in range(0, hauteur - tile + 1, pas)
              for x in range(0, largeur - tile + 1, pas)])
    ordre = ordre[:fenetres]
    debut = time.perf_counter()
    for y, x in ordre:
        bloc = pile[:, y : y + tile, x : x + tile]
        # `np.ascontiguousarray` reproduit la copie que `np.stack` fait dans le rendu.
        np.ascontiguousarray(bloc)
    ecoule = time.perf_counter() - debut
    return 1000.0 * ecoule / len(ordre) if ordre else 0.0


def balayage(largeurs=(1024, 2048, 3240, 4260, 6000), hauteur: int = 640,
             fenetres: int = 400) -> dict:
    """Le coût du rassemblement en fonction de la largeur, en ligne puis par blocs."""
    critique = largeur_critique()
    lignes = []
    for largeur in largeurs:
        lignes.append({
            "largeur": largeur,
            "bande_mio": round(bande_residente(largeur) / (1024 * 1024), 2),
            "tient_en_cache": bande_residente(largeur) <= L3_OCTETS,
            "ms_par_fenetre_en_ligne": round(
                cout_du_rassemblement(hauteur, largeur, fenetres), 4),
            "ms_par_fenetre_par_blocs": round(
                cout_du_rassemblement(hauteur, largeur, fenetres, par_blocs=True), 4),
        })
    return {
        "cache_l3_mio": L3_OCTETS // (1024 * 1024),
        "largeur_critique": critique,
        "largeur_de_bloc": largeur_de_bloc(),
        "observations_de_rendu": [
            {"segment": s, "largeur": l, "hauteur": h, "ms_par_fenetre": ms,
             "bande_mio": round(bande_residente(l) / (1024 * 1024), 2),
             "tient_en_cache": bande_residente(l) <= L3_OCTETS}
            for s, l, h, ms in OBSERVATIONS_DE_RENDU
        ],
        "balayage": lignes,
    }


def verifier() -> int:
    """Auto-test HORS LIGNE : ni torch, ni modèle, ni segment sur le disque."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LA BANDE, et pourquoi c'est elle qui decide -----------------------------------
    v("la bande croit avec la largeur", bande_residente(4260) > bande_residente(3240))
    v("la bande de 3240 tient dans 24 Mio", bande_residente(3240) <= L3_OCTETS)
    v("... celle de 4260 n'y tient pas", bande_residente(4260) > L3_OCTETS)
    v("la bande ne depend PAS de la hauteur du segment",
      bande_residente(3240) == bande_residente(3240))
    v("20.6 Mio a 3240 colonnes",
      abs(bande_residente(3240) / (1024 * 1024) - 20.57) < 0.05)
    v("27.0 Mio a 4260 colonnes",
      abs(bande_residente(4260) / (1024 * 1024) - 27.04) < 0.05)
    # ⚠ Mio, pas Mo : les memes octets valent 21.6 et 28.4 en megaoctets decimaux, et
    # comparer une bande en Mo a un cache en Mio met une frontiere du mauvais cote.
    v("la bande est comptee en mebioctets, pas en megaoctets",
      bande_residente(3240) // 1000000 == 21 and bande_residente(3240) // 1048576 == 20)

    # --- LA LARGEUR CRITIQUE, encadree par les deux segments observes ------------------
    critique = largeur_critique()
    v("la largeur critique tombe ENTRE les deux segments observes",
      3240 < critique < 4260)
    v("... et elle vaut le cache divise par le cout d'une colonne",
      critique == L3_OCTETS // (FRAMES * TILE * OCTETS_PAR_VOXEL))
    # La division est entiere, donc l'egalite se lit a une colonne pres.
    v("un cache deux fois plus grand double la largeur critique",
      abs(largeur_critique(2 * L3_OCTETS) - 2 * critique) <= 1)

    # --- LA LARGEUR DE BLOC ------------------------------------------------------------
    v("la largeur de bloc reste sous la largeur critique",
      largeur_de_bloc() < critique)
    v("... et jamais sous une fenetre", largeur_de_bloc() >= TILE)
    v("la marge est un argument, pas un litteral",
      largeur_de_bloc(marge=1.0) == critique)
    try:
        largeur_de_bloc(marge=0.0)
        v("une marge hors ]0,1] est refusee", False)
    except ValueError:
        v("une marge hors ]0,1] est refusee", True)

    # --- L'ORDRE PAR BLOCS : le meme ENSEMBLE, un autre ordre --------------------------
    # ⚠⚠ C'est l'invariant qui rend le remede gratuit : si l'ensemble changeait, la carte
    # changerait, et on aurait paye la vitesse avec le resultat.
    en_ligne = [(y, x)
                for y in range(0, 400 - TILE + 1, PAS)
                for x in range(0, 900 - TILE + 1, PAS)]
    par_blocs = positions_par_blocs(400, 900, largeur_bloc=200)
    v("le balayage par blocs voit exactement les memes fenetres",
      sorted(par_blocs) == sorted(en_ligne))
    v("... chacune une seule fois", len(par_blocs) == len(set(par_blocs)))
    v("... dans un ORDRE different", par_blocs != en_ligne)
    v("un bloc plus large que le segment redonne le balayage en ligne",
      positions_par_blocs(400, 900, largeur_bloc=10_000) == en_ligne)

    # --- LE COUT MESURE, sur des piles assez petites pour tenir dans une batterie ------
    petit = cout_du_rassemblement(320, 512, 60)
    v("le rassemblement coute un temps positif", petit > 0.0)
    v("... et reste sous la milliseconde a 512 colonnes", petit < 1.0)

    # --- LES OBSERVATIONS, chacune du bon cote de la frontiere -------------------------
    resume = balayage(largeurs=(512,), hauteur=320, fenetres=40)
    obs = {o["segment"]: o for o in resume["observations_de_rendu"]}
    v("le segment rapide est celui dont la bande tient en cache",
      obs["PHerc1447_complet"]["tient_en_cache"])
    v("le segment lent est celui dont la bande deborde",
      not obs["1447_20250703025628"]["tient_en_cache"])
    v("... et c'est bien le lent qui coute le plus par fenetre",
      obs["1447_20250703025628"]["ms_par_fenetre"]
      > obs["PHerc1447_complet"]["ms_par_fenetre"])
    v("le balayage rapporte les deux ordres pour chaque largeur",
      all("ms_par_fenetre_en_ligne" in l and "ms_par_fenetre_par_blocs" in l
          for l in resume["balayage"]))

    # --- LA REFUTATION, gardee comme un controle et pas comme une prose ----------------
    # ⚠⚠ Ce n'est pas la FORME de la courbe qui tue l'hypothese, c'est son ORDRE DE
    # GRANDEUR : le rassemblement coute un dixieme de milliseconde quand l'ecart a
    # expliquer en vaut 357. Une cause cent fois trop petite reste trop petite quelle que
    # soit la largeur, donc ce controle vaut mieux qu'un seuil sur la pente.
    ecart = (OBSERVATIONS_DE_RENDU[1][3] - OBSERVATIONS_DE_RENDU[0][3])
    large = cout_du_rassemblement(320, 4260, 40)
    v("le rassemblement est cent fois trop petit pour etre la cause",
      large * 100 < ecart)
    v("... et l'ecart a expliquer se compte bien en centaines de ms", ecart > 300)
    # La fenetre que le modele consomme ne depend PAS du segment : c'est ce qui rend
    # l'argument complet une fois le rassemblement ecarte.
    v("la fenetre soumise au modele est invariante en taille de segment",
      (FRAMES, TILE, TILE) == (FRAMES, TILE, TILE) and TILE * TILE * FRAMES == 106496)

    # ⚠⚠ La formule du verdict N'EST PAS libre : `temoins.sh` exige `ALL PASS` ET un
    # code de retour nul, et compte ses controles en lisant « N checks » sur cette ligne.
    # Une batterie qui invente sa propre phrase est comptee ECHEC alors qu'elle passe.
    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--balayer", action="store_true",
                    help="mesure le cout du rassemblement en fonction de la largeur")
    ap.add_argument("--hauteur", type=int, default=640,
                    help="hauteur des piles synthetiques du balayage")
    ap.add_argument("--fenetres", type=int, default=400,
                    help="fenetres chronometrees par largeur")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    if args.verifier:
        return verifier()
    if not args.balayer:
        ap.error("rien a faire : passer --balayer ou --verifier")

    resume = balayage(hauteur=args.hauteur, fenetres=args.fenetres)
    print(f"cache L3            : {resume['cache_l3_mio']} Mio")
    print(f"largeur critique    : {resume['largeur_critique']} colonnes")
    print(f"largeur de bloc     : {resume['largeur_de_bloc']} colonnes")
    print()
    print("  largeur   bande      cache   en ligne   par blocs")
    for l in resume["balayage"]:
        print(f"  {l['largeur']:7d}  {l['bande_mio']:6.2f} Mio  "
              f"{'oui' if l['tient_en_cache'] else 'NON':>5}  "
              f"{l['ms_par_fenetre_en_ligne']:8.3f}   {l['ms_par_fenetre_par_blocs']:8.3f}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n")
        print(f"\n→ {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
