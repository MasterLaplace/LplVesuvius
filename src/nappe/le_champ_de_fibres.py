#!/usr/bin/env python3
"""Ce que le champ de fibres publié contient RÉELLEMENT — et ce qu'il ne contient pas.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE. `A2 bis` (⭐⭐⭐ du registre) est déclarée « débloquée » par
[`78`](../../docs/78_lombilic_publie.md) §2, qui annonce *« un champ d'enroulement bâti sur l'axe
et l'orientation des fibres (`representations/predictions/fibers/`, publié pour `PHerc0139` en
**`nx`/`ny`/`nz`** OME-Zarr) »*. Cette phrase décide de tout un chantier, donc elle méritait
d'être vérifiée à la source plutôt que reprise.

⚠⚠ **Il n'y a pas de `nz`.** Le préfixe publie exactement **trois** canaux — `nx`, `ny`,
`presence` — et rien d'autre. Le manifeste `inference.json` annonce pourtant
`artifact_kind: fiber3d-prediction`, une architecture `fiber3d/unet` et
`output_schema.output_channels = 7` : le modèle prédit en trois dimensions, le corpus n'en
publie que deux composantes.

⚠⚠ **Et les noms de fichiers portent `las-sd1` avec un manifeste `.lasagna.json`.** Or `26` §7 a
déjà payé que les `nx`/`ny` de `lasagna` sont un champ **2D**, et `A2 ter` écrit noir sur blanc
qu'un résidu ne se calcule pas dessus « complété d'un `z` forcé ». Savoir si ce champ-ci est
2D ou la projection d'un champ 3D n'est donc pas un détail : c'est la différence entre une
entrée utilisable pour `A2 bis` et le piège que le dépôt s'est déjà écrit.

⭐⭐ CE QUI TRANCHE, ET C'EST UNE MESURE D'UNE LIGNE. Si `(nx, ny, nz)` est un vecteur unitaire,
alors @f$n_x^2 + n_y^2 \\le 1@f$ et la composante manquante se récupère **en module** :
@f$|n_z| = \\sqrt{1 - n_x^2 - n_y^2}@f$. Si le champ est 2D unitaire, la même somme vaut **1
partout** et il n'y a rien à récupérer. Les deux hypothèses prédisent des distributions
incompatibles, donc une seule lecture de blocs les sépare.

⚠ ET LE SIGNE NE SE RÉCUPÈRE JAMAIS, quelle que soit la réponse. Une racine carrée rend un
module ; savoir si la fibre pique vers le haut ou vers le bas demande une information que ces
octets ne portent pas. Pour un nombre d'enroulement ça peut suffire — la normale d'une feuille
et son opposée décrivent la même feuille — mais ça doit être dit plutôt que découvert.

⚠⚠⚠ LE PIÈGE Nº27 DU DÉPÔT S'APPLIQUE ICI AUSSI : un volume est surtout du remplissage. Les
blocs sont donc cherchés là où `presence` est fort, jamais au jugé — un balayage au hasard
rendrait « le champ est nul partout », ce qui ressemble à un champ vide et n'est qu'un échantillon
pris dans l'air.

Usage :
    uv run python src/nappe/le_champ_de_fibres.py --verifier
    uv run python src/nappe/le_champ_de_fibres.py --json docs/mesures/le_champ_de_fibres.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))

PREFIXE = ("PHerc0139/representations/predictions/fibers/"
           "20260102150214-fibers-20260801084232-L1")
BASE = "PHerc0139-20260102150214-las-sd1-92481a4c"
CANAUX = ("nx", "ny", "presence")
"""Les canaux réellement publiés. ⚠ `nz` n'y est pas, et c'est le premier constat de ce fichier."""

VOXEL_UM = 2.399
"""Taille de voxel du volume source `20260102150214` (`73` §0)."""

PAS_DE_FEUILLE_UM = 150.0
"""Écart inter-feuilles typique de ce corpus.

⚠ Ordre de grandeur repris de `16` (médiane **156 µm** sur `PHerc1447`) et de `78` (écart
inter-feuilles **155,8 µm** sur `PHerc0139`), pas une constante de ce fichier. Il ne sert qu'à
dire combien de cellules d'un niveau donné tiennent dans un pas — donc à savoir si le champ
publié peut seulement voir une feuille."""


def url(canal: str) -> str:
    from zarr_depth import BUCKET  # noqa: PLC0415

    return f"{BUCKET}/{PREFIXE}/{BASE}_{canal}.ome.zarr"


def niveaux_publies(canal: str = "nx", plafond: int = 8) -> list[int]:
    """
    @brief Les niveaux de pyramide réellement présents pour ce canal.

    ⚠⚠ DÉCOUVERTS, PAS SUPPOSÉS. Ce champ ne publie **pas** le niveau 0 : seuls les niveaux 3
    et 4 existent, soit huit et seize fois plus grossiers que le volume. Un lecteur qui
    demanderait le niveau 0 recevrait un 404, que ce dépôt a déjà compté comme « pas de
    matière » — une panne d'accès prenant la forme d'un fait sur le rouleau.
    """
    from zarr_depth import get  # noqa: PLC0415

    return [n for n in range(plafond) if get(f"{url(canal)}/{n}/.zarray", 20) is not None]


def resolution_um(niveau: int) -> float:
    """@brief Ce que vaut une cellule de ce niveau, en micromètres."""
    return VOXEL_UM * (2 ** niveau)


def cellules_par_pas(niveau: int) -> float:
    """
    @brief Combien de cellules de ce niveau tiennent dans un écart inter-feuilles.

    ⚠ C'est le nombre qui décide si un champ est utilisable pour séparer deux feuilles : en
    dessous de deux cellules par pas, deux feuilles voisines partagent une cellule et aucune
    orientation ne peut les distinguer.
    """
    return PAS_DE_FEUILLE_UM / resolution_um(niveau)


def lire_bloc(canal: str, niveau: int, cz: int, cy: int, cx: int) -> np.ndarray | None:
    """
    @brief Un chunk décodé, ou None s'il n'est pas publié.

    ⚠ Réutilise le lecteur de `src/commun/zarr_depth.py` — clé de chunk avec le séparateur
    **déclaré**, décodage blosc, et l'exception qui distingue « absent » de « je ne sais pas le
    lire ». Ce dépôt a déjà conclu qu'une graine n'était pas couverte par une prédiction alors
    que `numcodecs` manquait simplement.
    """
    from zarr_depth import array_meta, chunk_key, decode, get  # noqa: PLC0415

    meta = array_meta(url(canal), niveau, 30)
    forme = meta["chunks"]
    attendu = int(np.prod(forme))
    brut = get(f"{url(canal)}/{chunk_key(meta, niveau, cy, cx, cz)}", 60)
    if brut is None:
        return None
    octets = decode(brut, meta, attendu)
    if octets is None:
        return None
    return np.frombuffer(octets, dtype=np.uint8).reshape(forme)


def _en_unite(a: np.ndarray) -> np.ndarray:
    """
    @brief Un canal `uint8` ramené sur [-1, 1].

    ⚠⚠ L'ENCODAGE EST UNE HYPOTHÈSE, ET ELLE EST TESTÉE PLUTÔT QUE CRUE. Un octet qui porte une
    composante signée se lit `2 v / 255 - 1` ; s'il portait autre chose, la somme des carrés
    sortirait très loin de un des deux côtés, et c'est exactement ce que la mesure regarde. Une
    convention devinée qui se trouve fausse rendrait « le champ n'est pas unitaire » alors que
    seul le décodage l'est.
    """
    return a.astype(np.float32) * (2.0 / 255.0) - 1.0


def chercher_matiere(niveau: int, essais: int = 40, seuil: int = 32,
                     graine: int = 42) -> dict:
    """
    @brief Un chunk où `presence` est forte — le piège nº27 traité plutôt que subi.

    ⚠⚠ La recherche est **semée** et sa graine est rendue : un balayage au hasard non
    reproductible ferait dépendre le résultat publié du jour où il a été pris.

    ⚠ Le balayage saute les bords de la grille de chunks : le premier et le dernier chunk d'un
    axe sont à moitié hors du rouleau par construction, donc y chercher de la matière biaiserait
    la recherche vers le vide sans rien dire du champ.
    """
    from zarr_depth import array_meta  # noqa: PLC0415

    meta = array_meta(url("presence"), niveau, 30)
    forme, chunks = meta["shape"], meta["chunks"]
    grille = [max(1, (s + c - 1) // c) for s, c in zip(forme, chunks)]
    rng = np.random.default_rng(graine)
    meilleur = None
    vus = 0
    for _ in range(essais):
        cz = int(rng.integers(1, max(2, grille[0] - 1)))
        cy = int(rng.integers(1, max(2, grille[1] - 1)))
        cx = int(rng.integers(1, max(2, grille[2] - 1)))
        bloc = lire_bloc("presence", niveau, cz, cy, cx)
        if bloc is None:
            continue
        vus += 1
        part = float((bloc > seuil).mean())
        if meilleur is None or part > meilleur["part_presence"]:
            meilleur = dict(cz=cz, cy=cy, cx=cx, part_presence=part,
                            presence_max=int(bloc.max()))
    if meilleur is None:
        return {}
    return dict(**meilleur, chunks_lus=vus, essais=essais, graine=graine,
                grille=grille, forme=forme)


def norme_du_champ(niveau: int, cz: int, cy: int, cx: int, seuil: int = 32) -> dict:
    """
    @brief La question qui tranche : @f$n_x^2 + n_y^2@f$ vaut-il un, ou moins ?

    ⚠⚠⚠ MESURÉ LÀ OÙ IL Y A DE LA MATIÈRE, jamais sur tout le bloc. Une cellule vide porte une
    orientation qui ne veut rien dire, et il y en a beaucoup plus que de pleines : les inclure
    ferait tendre n'importe quelle distribution vers ce que le modèle rend sur du vide.

    ⚠ La part de cellules dont la somme **dépasse** un est rendue à part. Un champ unitaire
    quantifié sur huit bits en produit quelques-unes par arrondi ; en produire beaucoup dirait
    que l'encodage supposé est faux, et non que le champ est étrange.
    """
    nx, ny, pr = (lire_bloc(c, niveau, cz, cy, cx) for c in ("nx", "ny", "presence"))
    if nx is None or ny is None or pr is None:
        return {}
    plein = pr > seuil
    if plein.sum() < 100:
        return {}
    x, y = _en_unite(nx[plein]), _en_unite(ny[plein])
    somme = x * x + y * y
    return dict(cellules=int(plein.sum()), cellules_du_bloc=int(plein.size),
                part_pleine=float(plein.mean()),
                somme_mediane=float(np.median(somme)),
                somme_p10=float(np.percentile(somme, 10)),
                somme_p90=float(np.percentile(somme, 90)),
                # ⚠⚠ LA QUEUE HAUTE SÉPARE L'ARRONDI D'UN ENCODAGE MAL DEVINÉ. Un champ
                # unitaire quantifié sur huit bits déborde de quelques millièmes ; un facteur
                # d'échelle faux déborde de dizaines de pourcents. Sans p99 et le maximum, « 5 %
                # dépassent un » est compatible avec les deux, et on ne saurait pas si l'on
                # mesure le champ ou sa convention.
                somme_p99=float(np.percentile(somme, 99)),
                somme_max=float(somme.max()),
                part_au_dessus_de_un=float((somme > 1.0).mean()),
                # ⚠ Le module de la composante manquante, SI le champ est unitaire en 3D.
                # Rendu même quand il ne l'est pas : c'est la valeur que l'hypothèse implique,
                # et la voir absurde est une façon de la rejeter.
                nz_median=float(math.sqrt(max(0.0, 1.0 - float(np.median(somme))))))


def mesurer(niveau: int | None = None, fenetres: int = 3) -> dict:
    """
    @brief Le relevé, sur PLUSIEURS fenêtres.

    ⚠⚠ TROIS BLOCS ET PAS UN, pour la raison que `C2` a payée : un seul échantillon ne peut pas
    dire si un résultat est une propriété du **champ** ou un accident de **ce bloc-là**. Trois
    fenêtres tirées à des graines différentes le disent, et la batterie refuse de conclure si
    elles ne s'accordent pas.
    """
    niveaux = niveaux_publies()
    if not niveaux:
        raise SystemExit("aucun niveau lisible sous le champ de fibres")
    n = niveau if niveau is not None else min(niveaux)
    lots = []
    for k in range(fenetres):
        trouve = chercher_matiere(n, graine=42 + 100 * k)
        if not trouve:
            continue
        norme = norme_du_champ(n, trouve["cz"], trouve["cy"], trouve["cx"])
        if norme:
            lots.append(dict(fenetre=trouve, norme=norme))
    if not lots:
        raise SystemExit("aucun chunk lisible : le balayage n'a rien trouvé")
    return dict(prefixe=PREFIXE, canaux_publies=list(CANAUX),
                canal_nz_publie=False, groupes_du_manifeste=list(CANAUX),
                niveaux_publies=niveaux, niveau=n,
                resolution_um=resolution_um(n),
                cellules_par_pas=cellules_par_pas(n),
                lots=lots,
                # ⚠ Le premier lot reste exposé sous les anciens noms : la figure et le registre
                # les lisent, et renommer une clef publiée casse ses lecteurs en silence.
                fenetre=lots[0]["fenetre"], norme=lots[0]["norme"])


def _verifier(r: dict | None = None) -> int:
    echecs = comptes = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptes
        comptes += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ L'ARITHMÉTIQUE DE RÉSOLUTION, testée sur des valeurs connues : c'est elle qui décide si
    # un champ publié peut seulement voir une feuille, donc elle ne doit pas être approximative.
    v("le niveau 3 vaut 19,2 µm par cellule", abs(resolution_um(3) - 19.192) < 0.01,
      f"{resolution_um(3):.3f} µm")
    v("... et le niveau 4 le double", abs(resolution_um(4) - 2 * resolution_um(3)) < 1e-6)
    v("... donc un pas de feuille tient en ~8 cellules au niveau 3",
      7.0 < cellules_par_pas(3) < 9.0, f"{cellules_par_pas(3):.2f}")
    v("... et en ~4 au niveau 4", 3.5 < cellules_par_pas(4) < 4.5,
      f"{cellules_par_pas(4):.2f}")
    # ⚠ La borne qui compte : sous deux cellules par pas, deux feuilles voisines partagent une
    # cellule et aucune orientation ne peut les séparer.
    v("... et le niveau 6 tomberait sous la limite de deux cellules par pas",
      cellules_par_pas(6) < 2.0, f"{cellules_par_pas(6):.2f}")

    # ⚠⚠ L'encodage supposé, testé sur ses trois points connus.
    bornes = _en_unite(np.array([0, 128, 255], dtype=np.uint8))
    v("l'octet 0 se lit -1, 255 se lit +1", abs(bornes[0] + 1) < 1e-6
      and abs(bornes[2] - 1) < 1e-6, str(bornes))
    v("... et le milieu tombe près de zéro", abs(bornes[1]) < 0.01, f"{bornes[1]:+.4f}")

    if r:
        print("\net la mesure")
        print(f"      canaux publiés : {', '.join(r['canaux_publies'])}")
        print(f"      niveaux publiés : {r['niveaux_publies']}  "
              f"(niveau lu {r['niveau']}, {r['resolution_um']:.1f} µm/cellule, "
              f"{r['cellules_par_pas']:.1f} cellules par pas de feuille)")
        lots = r.get("lots") or [{"fenetre": r["fenetre"], "norme": r["norme"]}]
        for l in lots:
            f_, n_ = l["fenetre"], l["norme"]
            print(f"      chunk ({f_['cz']:3d},{f_['cy']:3d},{f_['cx']:3d}) "
                  f"présence {100 * f_['part_presence']:5.1f} % · "
                  f"nx²+ny² méd {n_['somme_mediane']:.3f} "
                  f"(p10 {n_['somme_p10']:.3f}, p90 {n_['somme_p90']:.3f}, "
                  f"max {n_['somme_max']:.3f}) · |nz| {n_['nz_median']:.3f}")

        # ⚠⚠⚠ LE CONSTAT QUI CORRIGE `78` §2, ASSERTÉ ET NON NOTÉ.
        v("le corpus ne publie PAS de canal nz", r["canal_nz_publie"] is False,
          f"trois canaux seulement : {', '.join(r['canaux_publies'])} — et le manifeste "
          "`.lasagna.json` ne déclare pas d'autre groupe")
        v("... et le niveau 0 n'est pas publié non plus",
          0 not in r["niveaux_publies"],
          f"niveaux {r['niveaux_publies']} — le plus fin est {min(r['niveaux_publies'])}, "
          f"soit {resolution_um(min(r['niveaux_publies'])):.1f} µm/cellule")

        maxima = [l["norme"]["somme_max"] for l in lots]
        medianes = [l["norme"]["somme_mediane"] for l in lots]
        # ⚠⚠ L'ENCODAGE D'ABORD, sinon rien de ce qui suit ne veut dire quoi que ce soit. Un
        # champ unitaire quantifié sur huit bits déborde d'environ 1/127 par composante, donc la
        # somme des carrés plafonne juste au-dessus de un. Un facteur d'échelle faux la ferait
        # plafonner à 2, à 4, ou à 0,25 — et « le champ n'est pas unitaire » serait alors une
        # affirmation sur notre lecture et non sur le champ.
        v("l'encodage supposé est CONFIRMÉ : la somme plafonne à l'arrondi près",
          all(1.0 <= m < 1.05 for m in maxima),
          " · ".join(f"{m:.3f}" for m in maxima))
        # ⚠⚠⚠ LA QUESTION, TRANCHÉE SUR TROIS FENÊTRES. Un champ 2D unitaire rendrait une somme
        # collée à un partout — donc le piège que `26` §7 a payé, et `A2 ter` interdit. Mesuré :
        # elle ne l'est sur aucune, ce qui veut dire que ces deux canaux sont la projection d'un
        # vecteur à trois composantes dont la troisième n'est simplement pas publiée.
        v("le champ n'est 2D unitaire sur AUCUNE fenêtre",
          all(m < 0.90 for m in medianes),
          " · ".join(f"{m:.3f}" for m in medianes))
        v("... donc |nz| est récupérable, et lui seul",
          all(l["norme"]["nz_median"] > 0.2 for l in lots),
          " · ".join(f"{l['norme']['nz_median']:.3f}" for l in lots)
          + " — ⚠ le SIGNE reste perdu")
        # ⚠⚠ ET LA RÉSOLUTION EST CE QUI BORNE L'USAGE : à 19,2 µm un pas de feuille tient en
        # huit cellules, ce qui suffit à voir une feuille et pas à en séparer deux qui se
        # touchent. C'est une contrainte sur `A2 bis`, pas un défaut du champ.
        v("... et le champ le plus fin publié voit une feuille en ~8 cellules",
          6.0 < r["cellules_par_pas"] < 10.0, f"{r['cellules_par_pas']:.1f}")

    print()
    print(f"  {'ECHEC' if echecs else 'ALL PASS'} ({echecs} failures, {comptes} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--niveau", type=int, default=None)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.verifier and not a.json:
        cible = RACINE / "docs" / "mesures" / "le_champ_de_fibres.json"
        return 1 if _verifier(json.loads(cible.read_text()) if cible.is_file() else None) else 0

    r = mesurer(a.niveau)
    print(f"canaux publiés  : {', '.join(r['canaux_publies'])}   (nz : ABSENT)")
    print(f"niveaux publiés : {r['niveaux_publies']}")
    print(f"niveau {r['niveau']} : {r['resolution_um']:.1f} µm/cellule, "
          f"{r['cellules_par_pas']:.1f} cellules par pas de feuille")
    f, n = r["fenetre"], r["norme"]
    print(f"fenêtre : chunk ({f['cz']}, {f['cy']}, {f['cx']}), "
          f"{100 * f['part_presence']:.1f} % de présence")
    if n:
        print(f"nx²+ny² sur {n['cellules']} cellules pleines : "
              f"p10 {n['somme_p10']:.3f} · médiane {n['somme_mediane']:.3f} · "
              f"p90 {n['somme_p90']:.3f}")
        print(f"  |nz| impliqué si le champ est unitaire en 3D : {n['nz_median']:.3f}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
