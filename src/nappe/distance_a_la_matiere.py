#!/usr/bin/env python3
"""À quelle distance de ce point commence la matière scannée ? — le préalable, chiffré.

⚠⚠ POURQUOI CE FICHIER EXISTE. [`54`](../../docs/archive/54_cinq_rendus_vides.md) écrit le préalable :
*sonder la graine avant de payer le tracé*. `matiere_au_point.py` répond **oui ou non**, et
c'est déjà ce qui aurait arrêté treize rendus noirs. Mais « non » recouvre deux situations que
rien ne distinguait, et qui ne demandent pas la même chose :

  - la graine est **à côté** de la feuille — quelques centaines de micromètres, une erreur
    d'arrondi ou de repère, et la corriger est un calcul ;
  - la graine est **dans le vide** — des centimètres de rien autour, et aucune correction ne
    la sauve : c'est l'endroit qui est faux.

  ⭐ Un nombre sépare les deux, et il coûte quelques requêtes : la distance au premier bloc
    publié. Sur un volume MASQUÉ, un bloc absent veut dire « rien de scanné ici », donc la
    présence d'un bloc EST la présence de matière.

⚠ La recherche se fait en **espace de blocs**, par coquilles de distance de Tchebychev
croissante. C'est ce qui la rend bornée et arrêtable : on demande d'abord les 26 blocs qui
touchent, puis les 98 suivants, et on s'arrête au premier trouvé. Une recherche en espace de
voxels demanderait des millions de requêtes pour la même réponse.

⚠⚠ Le lecteur de blocs est **injecté**. Ce n'est pas de l'élégance : c'est ce qui rend
l'algorithme vérifiable **hors ligne**, sans réseau et sans S3. Le dépôt a déjà payé qu'une
mesure ne soit testable qu'en présence de ce qu'elle mesure.

⚠ La distance est rendue en blocs ET en micromètres, parce que « trois blocs » ne dit rien
tant qu'on ne sait pas ce que vaut un bloc au niveau demandé : un bloc de 128 voxels à
2,4 µm/voxel fait 307 µm au niveau 0, et **1,2 mm** au niveau 2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


def coquille(rayon: int):
    """Les décalages de blocs à distance de Tchebychev exactement `rayon`, ordre déterministe.

    ⚠ L'ordre doit être stable : deux exécutions qui trouvent des blocs différents à la même
    distance rendraient deux réponses pour une même question.
    """
    if rayon == 0:
        yield (0, 0, 0)
        return
    for dz in range(-rayon, rayon + 1):
        for dy in range(-rayon, rayon + 1):
            for dx in range(-rayon, rayon + 1):
                if max(abs(dz), abs(dy), abs(dx)) == rayon:
                    yield (dz, dy, dx)


def distance_a_la_matiere(lire, centre: tuple[int, int, int], rayon_max: int = 6) -> dict:
    """Le premier bloc publié autour de `centre`, en blocs.

    `lire(cz, cy, cx)` rend vrai si ce bloc existe. `centre` est en **coordonnées de bloc**.

    ⚠ Rend `trouve=False` plutôt que d'élargir indéfiniment : une recherche sans borne sur un
    volume masqué finirait par trouver le rouleau à l'autre bout et rendrait un nombre qui ne
    veut rien dire. Le rayon atteint est dit, pour qu'on sache ce qui a été regardé.
    """
    demandes = 0
    for r in range(rayon_max + 1):
        for d in coquille(r):
            bloc = (centre[0] + d[0], centre[1] + d[1], centre[2] + d[2])
            if min(bloc) < 0:
                continue
            demandes += 1
            if lire(*bloc):
                return {"trouve": True, "distance_blocs": r, "bloc": list(bloc),
                        "decalage": list(d), "demandes": demandes, "rayon_regarde": r}
    return {"trouve": False, "distance_blocs": None, "bloc": None, "decalage": None,
            "demandes": demandes, "rayon_regarde": rayon_max}


def en_micrometres(distance_blocs: int, cote_bloc: int, voxel_um: float, niveau: int) -> float:
    """La distance en µm. ⚠ Un bloc ne vaut pas la même chose selon le niveau."""
    return distance_blocs * cote_bloc * voxel_um * (2 ** niveau)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- les coquilles ---
    v("la coquille 0 est le centre seul", list(coquille(0)) == [(0, 0, 0)])
    v("la coquille 1 a 26 blocs", len(list(coquille(1))) == 26)
    v("la coquille 2 a 98 blocs", len(list(coquille(2))) == 98)
    # ⚠ Une coquille ne doit contenir QUE des blocs a sa distance : un doublon avec la
    # coquille precedente ferait redemander ce qu'on vient de demander, et un manque ferait
    # rater la matiere la plus proche.
    v("aucun bloc d'une coquille n'est a une autre distance",
      all(max(abs(a), abs(b), abs(c)) == r for r in (1, 2, 3) for a, b, c in coquille(r)))
    v("les coquilles ne se recouvrent pas",
      not (set(coquille(1)) & set(coquille(2))))
    v("l'ordre d'une coquille est stable", list(coquille(2)) == list(coquille(2)))

    # --- la recherche ---
    v("un bloc au centre donne une distance nulle",
      distance_a_la_matiere(lambda z, y, x: True, (10, 10, 10))["distance_blocs"] == 0)
    # ⭐ Le controle qui compte : la distance rendue est la PLUS PETITE, pas la premiere vue.
    plein = {(12, 10, 10), (10, 11, 10)}
    r = distance_a_la_matiere(lambda z, y, x: (z, y, x) in plein, (10, 10, 10))
    v("... et sinon la PLUS PETITE distance, pas la premiere rencontree",
      r["distance_blocs"] == 1 and tuple(r["bloc"]) == (10, 11, 10))
    v("le nombre de requetes est compte", r["demandes"] > 1)

    vide = distance_a_la_matiere(lambda z, y, x: False, (10, 10, 10), rayon_max=2)
    v("un vide complet rend trouve=False", vide["trouve"] is False)
    v("... et DIT jusqu'ou il a regarde", vide["rayon_regarde"] == 2)
    v("... sans pretendre une distance", vide["distance_blocs"] is None)

    # ⚠ Un bloc de coordonnee negative n'existe pas : le demander gaspillerait une requete et,
    # sur certains stockages, rendrait une erreur qu'on lirait comme « absent ».
    vu = []
    distance_a_la_matiere(lambda z, y, x: vu.append((z, y, x)) or False, (0, 0, 0), rayon_max=1)
    v("aucun bloc de coordonnee negative n'est demande", all(min(b) >= 0 for b in vu))

    # ⭐ Le nombre de requetes est BORNE, et c'est ce qui rend la question payable : 1 + 26 + 98.
    compte = distance_a_la_matiere(lambda z, y, x: False, (50, 50, 50), rayon_max=2)["demandes"]
    v("le cout est borne et connu : 1 + 26 + 98", compte == 125)

    # --- les micrometres ---
    v("un bloc de 128 a 2,4 µm fait 307 µm au niveau 0",
      abs(en_micrometres(1, 128, 2.4, 0) - 307.2) < 1e-9)
    # ⚠⚠ Le meme bloc vaut QUATRE FOIS PLUS au niveau 2. Confondre les deux est exactement le
    # defaut qui a produit treize rendus noirs.
    v("... et 1228,8 µm au niveau 2", abs(en_micrometres(1, 128, 2.4, 2) - 1228.8) < 1e-9)
    v("une distance nulle vaut zero µm", en_micrometres(0, 128, 2.4, 2) == 0.0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--volume", default="PHercParis4/volumes/"
                                       "20260411134726-2.400um-0.2m-78keV-masked.zarr")
    p.add_argument("--niveau", type=int, default=0)
    p.add_argument("--point", nargs=3, type=int, metavar=("Z", "Y", "X"))
    p.add_argument("--rayon", type=int, default=4, help="rayon maximal, en blocs")
    p.add_argument("--voxel-um", type=float, default=2.4)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.point:
        p.error("--point Z Y X est requis")

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tracecheck"))
    import tracecheck as tc
    url = f"{BUCKET}/{a.volume}"
    meta = tc.array_meta(url, a.niveau, 30.0)
    cz, cy, cx = meta["chunks"][0], meta["chunks"][1], meta["chunks"][2]
    centre = (a.point[0] // cz, a.point[1] // cy, a.point[2] // cx)
    forme = meta["shape"]
    bornes = (forme[0] // cz, forme[1] // cy, forme[2] // cx)

    def lire(bz, by, bx) -> bool:
        if bz > bornes[0] or by > bornes[1] or bx > bornes[2]:
            return False
        bloc, _, _ = None, None, None
        try:
            from matiere_au_point import lire_bloc
            bloc, _, _ = lire_bloc(url, a.niveau, bz * cz, by * cy, bx * cx, 30.0, meta)
        except Exception:
            return False
        return bloc is not None

    r = distance_a_la_matiere(lire, centre, a.rayon)
    r["point"] = a.point
    r["niveau"] = a.niveau
    r["bloc_centre"] = list(centre)
    r["cote_bloc"] = cz
    if r["trouve"]:
        um = en_micrometres(r["distance_blocs"], cz, a.voxel_um, a.niveau)
        r["distance_um"] = um
        print(f"{tuple(a.point)} niveau {a.niveau} : matière au bloc {r['bloc']}, "
              f"à {r['distance_blocs']} bloc(s) — au plus {um:.0f} µm — "
              f"en {r['demandes']} requête(s)")
    else:
        um = en_micrometres(a.rayon, cz, a.voxel_um, a.niveau)
        print(f"{tuple(a.point)} niveau {a.niveau} : ⚠⚠ AUCUNE matière dans un rayon de "
              f"{a.rayon} bloc(s) — soit {um:.0f} µm — après {r['demandes']} requête(s)")
    if a.json:
        a.json.write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
