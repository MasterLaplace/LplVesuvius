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


def axe_a_ce_z(z_niveau: int, niveau: int) -> tuple[float, float] | None:
    """
    @brief Le centre du rouleau à cette tranche, dans les coordonnées du niveau demandé.

    ⚠⚠ L'axe publié est annoté dans le repère **plein** (`PHerc0139_2um_full`), donc en
    coordonnées de niveau 0 ; le champ, lui, n'est publié qu'aux niveaux 3 et 4. Comparer les
    deux sans diviser mettrait le centre du rouleau huit fois trop loin, et un rayon tiré depuis
    là ne traverserait rien — ce qui ressemble à un champ vide.

    ⚠ Les points sont `(x, y, z)` et la forme du volume est `(z, y, x)`. Ce dépôt a déjà payé un
    axe faux d'un facteur 3,9 pour avoir mélangé deux repères ; ici l'erreur serait un axe
    transposé, qui rend un rayon parfaitement plausible dans la mauvaise direction.
    """
    import sys as _sys  # noqa: PLC0415

    _sys.path.insert(0, str(RACINE / "src" / "excision"))
    from lombilic_publie import charger_axe  # noqa: PLC0415

    charge = charger_axe("PHerc0139")
    if charge is None:
        return None
    pts = charge[0]
    facteur = 2 ** niveau
    z0 = z_niveau * facteur
    # ⚠ Interpolation entre les deux points de contrôle qui encadrent la tranche : prendre le
    # plus proche ferait sauter le centre d'un point de contrôle à l'autre, et l'axe dérive de
    # plusieurs millimètres entre deux annotations (`78` : médiane 3,01 mm entre deux axes).
    ordre = np.argsort(pts[:, 2])
    zs, xs, ys = pts[ordre, 2], pts[ordre, 0], pts[ordre, 1]
    if z0 < zs[0] or z0 > zs[-1]:
        return None
    x = float(np.interp(z0, zs, xs)) / facteur
    y = float(np.interp(z0, zs, ys)) / facteur
    return x, y


def periodicite_radiale(niveau: int, cz: int, cy: int, cx: int,
                        seuil: int = 32) -> dict:
    """
    @brief Le long d'un rayon depuis l'axe, `presence` bat-elle au pas des feuilles ?

    ⚠⚠⚠ C'EST LA QUESTION QUI DÉCIDE SI CE CHAMP PEUT PORTER UN NOMBRE D'ENROULEMENT. Un nombre
    d'enroulement compte des feuilles ; si le champ ne les distingue pas radialement, il ne peut
    pas les compter, quelle que soit la qualité de son orientation.

    ⚠⚠ ET LE CONTRÔLE EST TANGENTIEL. Une périodicité radiale seule ne prouve rien : un bloc de
    volume compressé porte des motifs, et une autocorrélation trouve toujours **un** maximum.
    Une feuille est une surface, donc elle se répète **en travers** et pas **le long** — le même
    profil pris perpendiculairement doit être plat. Sans ce contrôle la mesure est satisfaite par
    n'importe quelle texture.

    ⚠ Le profil est pris au plus proche voisin : interpoler entre deux cellules lisserait
    justement la structure qu'on cherche à voir, et un lissage rend toute autocorrélation plus
    lisse — donc plus convaincante.
    """
    pr = lire_bloc("presence", niveau, cz, cy, cx)
    if pr is None:
        return {}
    n = pr.shape[0]
    centre_z = cz * n + n // 2
    axe = axe_a_ce_z(centre_z, niveau)
    if axe is None:
        return {}
    ax, ay = axe
    # ⚠ Le centre du bloc dans le repère du niveau, puis la direction radiale DEPUIS l'axe.
    by, bx = cy * n + n // 2, cx * n + n // 2
    dy, dx = by - ay, bx - ax
    rayon = math.hypot(dy, dx)
    if rayon < 1.0:
        return {}
    ur = (dy / rayon, dx / rayon)
    ut = (-ur[1], ur[0])

    def profil(u, tranches: int) -> np.ndarray:
        """
        @brief Une coupe du bloc le long de `u`, moyennée sur `tranches` plans z.

        ⚠⚠⚠ LE NOMBRE DE TRANCHES EST UN PARAMÈTRE PARCE QU'IL PEUT DÉTRUIRE LA MESURE. Un
        empilement de feuilles n'est parallèle à l'axe du volume que si le rouleau ne penche pas ;
        s'il penche, moyenner sur soixante-quatre plans mélange plusieurs feuilles dans chaque
        échantillon et **efface exactement la périodicité qu'on cherche**. Une seule tranche est
        plus bruitée et ne peut pas mentir dans ce sens-là. Les deux sont mesurées, et leur écart
        est le diagnostic.
        """
        pas = np.arange(-n // 2 + 1, n // 2)
        z0 = n // 2 - tranches // 2
        z1 = z0 + max(1, tranches)
        sortie = []
        for t in pas:
            iy = int(round(n // 2 + t * u[0]))
            ix = int(round(n // 2 + t * u[1]))
            if 0 <= iy < n and 0 <= ix < n:
                sortie.append(float(pr[z0:z1, iy, ix].mean()))
        return np.asarray(sortie, dtype=float)

    def periode(v: np.ndarray) -> tuple[int, float]:
        """
        @brief Le premier maximum LOCAL de l'autocorrélation après son passage sous zéro.

        ⚠⚠⚠ PAS LE MAXIMUM GLOBAL, et ma première version faisait cette faute. L'autocorrélation
        d'un signal lisse **décroît**, donc son plus grand décalage utile est toujours le plus
        petit : les trois fenêtres ont rendu « période 2 cellules » dans les deux directions,
        c'est-à-dire la largeur de lissage du champ et rien du tout sur les feuilles. Une mesure
        qui rend la même réponse quelle que soit la structure ne mesure pas la structure.

        ⚠ Le passage sous zéro est ce qui sépare « le signal se ressemble encore » de « il a
        changé de phase » : chercher un maximum après lui, c'est chercher un retour, ce qui est
        exactement la définition d'une période. Sans cette étape on retrouve la pente.
        """
        if v.size < 12:
            return 0, 0.0
        w = v - v.mean()
        denom = float((w * w).sum()) or 1.0
        limite = min(v.size - 4, 4 * int(cellules_par_pas(niveau)) + 6)
        auto = [float((w[:-k] * w[k:]).sum()) / denom for k in range(1, limite)]
        premier_negatif = next((i for i, a in enumerate(auto) if a < 0.0), None)
        if premier_negatif is None:
            # ⚠ Jamais négative : il n'y a pas de retour dans la fenêtre, donc pas de période
            # observable. Rendre le dernier décalage serait inventer une réponse.
            return 0, 0.0
        reste = auto[premier_negatif:]
        if not reste:
            return 0, 0.0
        i = int(np.argmax(reste))
        return premier_negatif + i + 1, float(reste[i])

    par_tranches = {}
    for tranches in (1, 8, n):
        k_rad, s_rad = periode(profil(ur, tranches))
        k_tan, s_tan = periode(profil(ut, tranches))
        par_tranches[str(tranches)] = dict(
            periode_radiale_cellules=k_rad, autocorrelation_radiale=s_rad,
            periode_radiale_um=k_rad * resolution_um(niveau),
            periode_tangentielle_cellules=k_tan, autocorrelation_tangentielle=s_tan)
    # ⚠ Le relevé principal reste celui d'UNE tranche : c'est le seul qui ne puisse pas avoir
    # effacé la structure par moyennage. Les autres sont gardés pour que l'écart se lise.
    un = par_tranches["1"]
    return dict(cz=cz, cy=cy, cx=cx, rayon_cellules=float(rayon),
                axe=[ax, ay], part_pleine=float((pr > seuil).mean()),
                par_tranches=par_tranches, **un,
                echantillons=int(profil(ur, 1).size))


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
            lots.append(dict(fenetre=trouve, norme=norme,
                             periodicite=periodicite_radiale(n, trouve["cz"], trouve["cy"],
                                                             trouve["cx"])))
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

        # ⚠⚠⚠ ET LA QUESTION QUI DÉCIDE POUR `A2 bis` : ce champ compte-t-il des feuilles ?
        # Un nombre d'enroulement compte des feuilles. Si le champ ne les sépare pas
        # radialement, il ne peut pas les compter, quelle que soit la qualité de son orientation.
        perios = [l["periodicite"] for l in lots if l.get("periodicite")]
        if perios:
            for q in perios:
                print(f"      chunk ({q['cz']:3d},{q['cy']:3d},{q['cx']:3d}) rayon "
                      f"{q['rayon_cellules']:6.0f} · radial "
                      f"{q['periode_radiale_um']:6.1f} µm (r={q['autocorrelation_radiale']:+.3f}) "
                      f"· tangentiel r={q['autocorrelation_tangentielle']:+.3f}")
            # ⚠⚠ LE CONTRÔLE TANGENTIEL EST CE QUI REND LA MESURE LISIBLE. Une feuille est une
            # surface : elle se répète EN TRAVERS et pas LE LONG. Une périodicité radiale n'est
            # une feuille que si la même mesure prise perpendiculairement est plus faible.
            # Mesuré : elle ne l'est pas sur deux fenêtres sur trois.
            separe = [q for q in perios
                      if q["autocorrelation_radiale"] > q["autocorrelation_tangentielle"] + 0.1]
            v("⚠ le radial ne bat pas le contrôle tangentiel sur toutes les fenêtres",
              len(separe) < len(perios),
              f"{len(separe)} fenêtre(s) sur {len(perios)} séparent — "
              + " · ".join(f"{q['autocorrelation_radiale']:+.3f} contre "
                           f"{q['autocorrelation_tangentielle']:+.3f}" for q in perios))
            # ⚠⚠ ET LÀ OÙ UNE PÉRIODE RADIALE APPARAÎT, ELLE VAUT DEUX À TROIS PAS DE FEUILLE.
            # C'est ce qu'on attend d'un champ dont la résolution effective est plus grossière
            # que sa grille : il voit des GROUPES de feuilles, pas des feuilles.
            um = [q["periode_radiale_um"] for q in perios if q["periode_radiale_cellules"]]
            v("... et la période radiale vaut 2 à 3 pas de feuille, jamais un",
              all(2.0 * PAS_DE_FEUILLE_UM < x < 3.5 * PAS_DE_FEUILLE_UM for x in um),
              " · ".join(f"{x:.0f} µm" for x in um)
              + f" contre un pas de {PAS_DE_FEUILLE_UM:.0f} µm")
            # ⚠ Et le moyennage en z est innocenté plutôt que soupçonné : une seule tranche
            # rend la même période que soixante-quatre, donc ce n'est pas le lissage qui a
            # effacé la structure.
            ecarts = [abs(q["par_tranches"]["1"]["periode_radiale_cellules"]
                          - q["par_tranches"][str(64)]["periode_radiale_cellules"])
                      for q in perios if "par_tranches" in q]
            v("... et le moyennage en z n'y est pour rien",
              all(e <= 2 for e in ecarts), " · ".join(str(e) for e in ecarts)
              + " cellules d'écart entre 1 tranche et 64")

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
