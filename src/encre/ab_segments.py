#!/usr/bin/env python3
"""Deux segments, le même crop, les mêmes fils : lequel est lent, et l'est-il encore ?

⚠⚠ Pourquoi ce fichier existe. `src/encre/cout_de_la_fenetre.py` a réfuté l'explication par
la taille : le rassemblement est deux mille fois trop petit, et l'appel du modèle est
invariant en taille de segment par construction. Le 2026-08-28, un troisième point de mesure
a fermé la question pour de bon — le segment `20250703034159` fait **3620 × 5220**, donc
**plus grand** que `20250703025628` (4100 × 4260), et il rend à **0,486** fenêtre par
fil-seconde contre **0,135**. Plus grand et cinq fois plus rapide.

⭐ Ce qui reste à trancher n'est donc plus « la taille » mais : la lenteur tient-elle au
CONTENU du segment, ou l'exécution de cette nuit-là était-elle dégradée par autre chose ?
Les deux hypothèses font la même prédiction sur les logs passés et des prédictions opposées
sur une mesure prise MAINTENANT, dans les mêmes conditions. C'est ce que ce fichier fait.

⚠⚠ Et il existe parce que la première tentative a échoué pour une raison bête : le coin
supérieur gauche de `20250703025628` est **entièrement vide**, donc le crop choisi n'avait
aucune fenêtre à rendre et la garde de pile l'a refusé — correctement. Choisir un crop
« au coin » n'est pas neutre sur des volumes de surface à moitié pleins. Le crop est donc
**cherché**, sur la couche médiane, là où il y a le plus de matière.

⚠ Portée : cette mesure compare deux segments dans des conditions IDENTIQUES, pas dans des
conditions idéales. Une campagne peut tourner à côté ; c'est même le cas normal ici. Ce qui
se transporte est le RAPPORT entre les deux, pas la valeur absolue.

Usage :
    uv run python src/encre/ab_segments.py --verifier
    uv run python src/encre/ab_segments.py data/couches/1447_A data/couches/1447_B \\
        --cote 640 --fils 4 --json docs/mesures/ab_segments.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

COUCHE_SONDEE = 15
"""Couche du milieu de pile. ⚠ Une couche du BORD est souvent plus vide que le cœur du
volume : la chercher au milieu évite de conclure « ce segment n'a pas de matière » sur une
tranche qui n'en a effectivement pas, alors que le volume en a."""

DUREE = re.compile(r"duree\s*:\s*([\d.]+)\s*s")
FENETRES = re.compile(r"fenetres\s*:\s*(\d+)")


def densite_par_bloc(couche: np.ndarray, cote: int) -> np.ndarray:
    """Compte de pixels non nuls par bloc de `cote`, en une passe de somme cumulée.

    ⚠ Somme cumulée plutôt qu'une boucle : sur une couche de dix-neuf millions de pixels,
    une boucle Python sur les blocs prendrait plus longtemps que le rendu qu'on mesure.
    """
    plein = (couche > 0).astype(np.int64)
    h, w = plein.shape
    nh, nw = h // cote, w // cote
    if nh < 1 or nw < 1:
        return np.zeros((0, 0), dtype=np.int64)
    rogne = plein[: nh * cote, : nw * cote]
    return rogne.reshape(nh, cote, nw, cote).sum(axis=(1, 3))


def crop_avec_matiere(couche: np.ndarray, cote: int) -> tuple[int, int]:
    """Le coin `(top, left)` du bloc de `cote` × `cote` le plus plein.

    ⚠⚠ « Le plus plein », pas « le premier non vide » : deux segments comparés sur des crops
    de remplissage très différents ne comparent plus le même travail. Prendre le maximum de
    chacun est le choix qui rend les deux crops comparables entre eux.
    """
    blocs = densite_par_bloc(couche, cote)
    if blocs.size == 0:
        raise ValueError(f"aucun bloc de {cote} px ne tient dans {couche.shape}")
    i = int(np.argmax(blocs))
    return (i // blocs.shape[1]) * cote, (i % blocs.shape[1]) * cote


def meilleure_region(couche, cote: int, pas: int = 64) -> tuple[float, int, int]:
    """La densité de matière de la meilleure région carrée de `cote`, et son origine.

    ⚠⚠ Le critère est la MATIÈRE, jamais la sortie du modèle. Choisir une région sur ce que
    le modèle y répond serait choisir celle qui donne le résultat qu'on veut ; la densité se
    mesure sur une couche, avant tout rendu, et se déclare donc à l'avance.

    Rend `(densité, top, left)`. Sert à répondre « cette trace peut-elle porter plus de
    fenêtres ailleurs ? » sans dépenser une heure de rendu pour le découvrir.
    """
    plein = couche > 0
    h, w = plein.shape
    if h < cote or w < cote:
        raise ValueError(f"une région de {cote} ne tient pas dans {couche.shape}")
    best = None
    for top in range(0, h - cote + 1, pas):
        for left in range(0, w - cote + 1, pas):
            d = float(plein[top:top + cote, left:left + cote].mean())
            if best is None or d > best[0]:
                best = (d, top, left)
    return best


def rendre(couches: Path, modele: Path, top: int, left: int, cote: int,
           fils: int, sortie: Path) -> dict:
    """Lance le VRAI rendu sur le crop et lit sa durée. Aucun modèle n'est réécrit ici.

    ⚠ On pilote `infer_ink.py` plutôt que d'en recopier la boucle : deux chemins de rendu
    seraient libres de diverger, et c'est précisément la mesure du chemin réel qu'on veut.
    """
    cmd = [sys.executable, str(RACINE / "src/xpu/infer_ink.py"), str(couches),
           "--model", str(modele), "--start-layer", "3", "--threads", str(fils),
           "--top", str(top), "--left", str(left),
           "--height", str(cote), "--width", str(cote), "--out", str(sortie)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=RACINE)
    texte = p.stdout + p.stderr
    d, f = DUREE.search(texte), FENETRES.search(texte)
    if not (d and f):
        return {"erreur": texte.strip().splitlines()[-1] if texte.strip() else "muet"}
    secondes, fenetres = float(d.group(1)), int(f.group(1))
    return {"secondes": secondes, "fenetres": fenetres,
            "ms_par_fenetre": round(1000.0 * secondes / fenetres, 1) if fenetres else None,
            "debit_par_fil_seconde": round(fenetres / (secondes * fils), 4)
            if secondes > 0 else None}


def comparer(a: Path, b: Path, modele: Path, cote: int, fils: int) -> dict:
    import tifffile

    lignes = []
    for couches in (a, b):
        tif = couches / f"{COUCHE_SONDEE:02d}.tif"
        image = tifffile.imread(tif)
        top, left = crop_avec_matiere(image, cote)
        remplissage = float((image[top:top + cote, left:left + cote] > 0).mean())
        mesure = rendre(couches, modele, top, left, cote, fils,
                        Path("/tmp") / f"ab_{couches.name}.npy")
        lignes.append({"segment": couches.name, "forme": list(image.shape),
                       "top": top, "left": left, "remplissage": round(remplissage, 3),
                       **mesure})
    debits = [l.get("debit_par_fil_seconde") for l in lignes]
    rapport = None
    if all(debits) and min(debits) > 0:
        rapport = round(max(debits) / min(debits), 2)
    return {"cote": cote, "fils": fils, "lignes": lignes, "rapport_des_debits": rapport}


def _refuse(appel) -> bool:
    """L'appel lève-t-il `ValueError` ? Écrit une fois plutôt que trois try/except."""
    try:
        appel()
    except ValueError:
        return True
    return False


def verifier() -> int:
    """Auto-test HORS LIGNE : la recherche de crop, sans modèle ni rendu."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LA DENSITE PAR BLOC ------------------------------------------------------------
    couche = np.zeros((40, 60), dtype=np.uint8)
    couche[20:30, 40:50] = 7
    blocs = densite_par_bloc(couche, 10)
    v("la grille de blocs a la bonne forme", blocs.shape == (4, 6))
    v("le bloc plein est compte entier", blocs[2, 4] == 100)
    v("un bloc vide compte zero", blocs[0, 0] == 0)
    v("le total des blocs vaut le total des pixels non nuls",
      blocs.sum() == int((couche > 0).sum()))
    v("une couche plus petite que le bloc ne rend aucun bloc",
      densite_par_bloc(np.zeros((5, 5), dtype=np.uint8), 10).size == 0)

    # --- LE CROP CHOISI ------------------------------------------------------------------
    v("le crop tombe sur le bloc le plus plein", crop_avec_matiere(couche, 10) == (20, 40))
    # ⚠⚠ « Le plus plein » et non « le premier non vide » : c'est ce qui rend les deux
    # crops comparables entre eux.
    deux = np.zeros((40, 60), dtype=np.uint8)
    deux[0:10, 0:10] = 1          # un bloc a peine peuple, rencontre EN PREMIER
    deux[0, 0] = 0
    deux[30:40, 50:60] = 3        # le bloc reellement plein, rencontre en DERNIER
    v("... et non sur le premier bloc non vide rencontre",
      crop_avec_matiere(deux, 10) == (30, 50))
    try:
        crop_avec_matiere(np.zeros((5, 5), dtype=np.uint8), 10)
        v("un crop impossible est refuse plutot que devine", False)
    except ValueError:
        v("un crop impossible est refuse plutot que devine", True)

    # --- LA MEILLEURE REGION, pour savoir si un rendu ailleurs vaut la peine -----------
    carte = np.zeros((40, 40), dtype=np.uint8)
    carte[10:30, 10:30] = 1
    d, top, left = meilleure_region(carte, 20, pas=10)
    v("la meilleure region trouve le bloc plein", (top, left) == (10, 10))
    v("... et rend sa densite", abs(d - 1.0) < 1e-9)
    v("une region plus grande que la couche est refusee",
      _refuse(lambda: meilleure_region(carte, 100)))
    # ⚠ Sur une couche uniforme, TOUTE region se vaut : la premiere est rendue, et c'est
    # correct — il n'y a rien a gagner a se deplacer.
    d2, t2, l2 = meilleure_region(np.ones((40, 40), dtype=np.uint8), 20, pas=10)
    v("sur une couche uniforme la premiere region est rendue",
      (t2, l2) == (0, 0) and abs(d2 - 1.0) < 1e-9)
    # Une couche entierement vide rend quand meme un coin : c'est a l'appelant de voir le
    # remplissage nul, et la garde de pile d'`infer_ink` refusera le rendu en le disant.
    v("une couche vide rend un coin plutot que de lever",
      crop_avec_matiere(np.zeros((40, 60), dtype=np.uint8), 10) == (0, 0))

    # --- LA LECTURE DE LA SORTIE DU RENDU -----------------------------------------------
    faux = "pas de balayage   : 21\nfenetres          : 400\nduree             : 40.0 s  (100 ms/fenetre)\n"
    v("la duree est lue", float(DUREE.search(faux).group(1)) == 40.0)
    v("les fenetres sont lues", int(FENETRES.search(faux).group(1)) == 400)
    # ⚠ « fenetres sans matiere : … » precede la ligne « fenetres : … ». Le motif exige les
    # deux-points colles au mot, sinon il lirait le compte des fenetres SAUTEES.
    piege = "fenetres sans matiere : 16564 sur 38600 (43%) sautees\nfenetres          : 22036\n"
    v("le compte saute n'est pas pris pour le compte rendu",
      int(FENETRES.search(piege).group(1)) == 22036)

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("segments", nargs="*", type=Path)
    ap.add_argument("--modele", type=Path,
                    default=RACINE / "data/models/timesformer_GP_scroll1")
    ap.add_argument("--cote", type=int, default=640)
    ap.add_argument("--fils", type=int, default=4)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--densite", type=int, metavar="COTE",
                    help="ne rien rendre : dire quelle région carrée de COTE porte le plus "
                         "de matière, et si elle vaut mieux que le coin")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.densite:
        import tifffile
        for couches in a.segments:
            tif = couches / f"{COUCHE_SONDEE:02d}.tif"
            image = tifffile.imread(tif)
            d, top, left = meilleure_region(image, a.densite)
            coin = float((image[: a.densite, : a.densite] > 0).mean())
            print(f"  {couches.name}  couche {image.shape}")
            print(f"    coin (0,0)      {100 * coin:5.1f} % de matière")
            print(f"    meilleure       {100 * d:5.1f} % en ({top},{left})  "
                  f"gain {100 * (d - coin):+.2f} point(s)")
        return 0
    if len(a.segments) != 2:
        ap.error("donner exactement deux dossiers de couches, ou --verifier")

    resume = comparer(a.segments[0], a.segments[1], a.modele, a.cote, a.fils)
    for l in resume["lignes"]:
        if "erreur" in l:
            print(f"  {l['segment']:24s} ERREUR {l['erreur'][:90]}")
            continue
        print(f"  {l['segment']:24s} crop ({l['top']},{l['left']}) "
              f"rempli {l['remplissage']:.0%}  "
              f"{l['fenetres']:5d} fen  {l['ms_par_fenetre']:7.1f} ms/fen  "
              f"{l['debit_par_fil_seconde']:.4f} fen/fil-s")
    if resume["rapport_des_debits"]:
        print(f"\nrapport des débits : ×{resume['rapport_des_debits']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(resume, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
