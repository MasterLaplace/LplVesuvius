#!/usr/bin/env python3
"""Écrire `approval.tif` — ce que le pinceau peint, calculé, avec ses quatre bras de contrôle.

⭐⭐⭐ CE QUE CE FICHIER PRODUIT. L'article §6.7 établit que l'intégration tient en un fichier :
le chargeur du pipeline de référence adopte **tout** `.tif` posé à côté de `x/y/z.tif` comme
canal nommé, et le canal `approval` est celui qui autorise la ré-optimisation du maillage.
Écrire `approval.tif` **est** l'intégration — pas de fork, pas d'appel à modifier.

Ce fichier l'écrit, à partir du champ d'enroulement de `77`. Deux des trois prédicats sortent du
**même** champ, et c'est ce qui rend la chose bon marché :

    placement  = la partie FRACTIONNAIRE de l'indice assigné
                 0,0 sur une feuille · 0,5 dans l'interstice
    identité   = l'AVANCE de l'indice sur un tour
                 0 pour une feuille · n pour n feuilles franchies

⚠⚠ Les deux sont vraiment différents, et je les avais confondus. Une copie translatée d'un
demi-pas a une avance **nulle** — elle suit parfaitement une feuille qui n'existe pas. C'est le
**placement** qui la refuse, pas l'identité. Un masque qui n'aurait que l'identité approuverait
une surface posée dans le vide entre deux feuilles.

Mesuré, et les deux populations ne se recouvrent sur aucun des deux axes :

    sur la feuille   fraction 0,001 [-0,137 ; +0,204]   avance -0,005 [-0,170 ; +0,230]
    quart de pas     fraction 0,252 [ 0,150 ;  0,441]
    demi-pas         fraction 0,502 [ 0,435 ;  0,640]
    saut d'1 feuille                                    avance  1,103 [ 0,753 ;  1,479]

⚠⚠⚠ LE QUATRIÈME BRAS EST CELUI SANS LEQUEL LE CONTRÔLE NE PEUT PAS ÉCHOUER. Approuver une
spire publiée, refuser un masque vide, refuser un masque plein : les trois se satisfont d'un
masque qui approuve tout. Le bras qui mord est la **copie translatée d'un demi-pas**, qui est
une surface lisse, plausible, et posée là où il n'y a pas de papyrus.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que le masque calculé vaille un masque humain.** Aucun `approval.tif` peint n'est publié
   — vérifié au listing S3 (`73` §0) — donc la comparaison qui trancherait n'est pas montable.
   Ce qui est mesuré est que le masque **approuve ce qui doit l'être et refuse ce qui ne doit
   pas**, sur des surfaces dont on connaît la faute parce qu'on l'a fabriquée.
2. **Qu'il vaille hors de la bande publiée.** Le champ interpole entre spires connues et
   **refuse** au-delà. Un point sans encadrement n'est pas approuvé — c'est voulu, et c'est la
   limite dure pour un déploiement.
3. ✅ **Que le canal soit écrit, et que `villa` l'accepte.** Cette ligne a longtemps dit
   *« le canal est écrit au bon nom et au bon format ; rien ici ne fait tourner `villa` »*, et
   **c'était faux** : jusqu'au 2026-09-05 ce fichier ne contenait **aucun `imwrite`**, son
   parseur n'avait **pas** le drapeau `--ecrire` que sa ligne d'usage documentait, et aucun
   `approval.tif` n'existait sur disque.

   ⭐ **Fait** : `--ecrire` porte le verdict du champ **(z, θ)** sur la grille **tifxyz** d'une
   trace et écrit `approval.tif` à côté de `x/y/z.tif`. Puis il le passe aux deux fonctions
   d'acceptation de `data/repos/villa/lasagna/approval_inpaint.py` — **importées, jamais
   recopiées** : le contrat est le leur, et une seconde version ici finirait par ne plus l'être.
   Mesuré sur `PHerc0139 / w040`, grille 615×431 : **`villa` accepte**.

   ⚠ Le bras négatif est là aussi, sans quoi le contrôle ne pourrait pas échouer : une forme
   fausse et un dossier incomplet doivent être **refusés**, et ils le sont (`ValueError`).
   « `villa` accepte notre masque » est satisfait par un lecteur qui accepte tout.

   ⚠ Reste hors de portée : que la **ré-optimisation** en tire quelque chose. Le contrat de
   fichier est honoré ; ce que `lasagna` fait ensuite du masque n'est pas exercé ici.

4. **Que le masque vaille un masque humain** — voir 1. Aucun `approval.tif` peint n'est publié,
   donc la comparaison reste non montable quoi qu'on écrive.

Usage :
    uv run python src/excision/le_masque_dapprobation.py --verifier
    uv run python src/excision/le_masque_dapprobation.py --json docs/mesures/le_masque_dapprobation.json
    uv run python src/excision/le_masque_dapprobation.py --ecrire /tmp/masque \\
        --json docs/mesures/le_masque_dapprobation_ecrit.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RACINE / "src" / "excision")]
import le_champ_denroulement as champ  # noqa: E402
from le_sens_des_indices import charger, _spires  # noqa: E402

TOLERANCE_PLACEMENT = 0.30
"""Une cellule est *sur* une feuille si sa partie fractionnaire d'indice est à moins de ça d'un
entier. ⚠ Le seuil est posé **entre les deux populations mesurées** et non choisi pour qu'un
réglage passe : une surface sur sa feuille monte à 0,204 au 9ᵉ décile, une translatée d'un
quart de pas descend à 0,150 — donc 0,30 sépare la feuille du demi-pas (0,435 au 1ᵉʳ décile) et
accepte délibérément le quart de pas, qui est encore du papyrus."""

TOLERANCE_IDENTITE = 0.45
"""Une tranche suit UNE feuille si son avance par tour est sous ça. ⚠ Posé entre +0,230 (le 9ᵉ
décile d'une vraie spire) et 0,753 (le 1ᵉʳ décile d'un saut d'une feuille). Les deux
populations ne se recouvrant pas, tout seuil de cet intervalle donne le même verdict — ce qui
est la propriété qu'on veut, et elle se vérifie."""


def _juger_cellules(cible: dict, autres: dict[int, dict]) -> dict[tuple[int, int], float]:
    """
    @brief L'indice assigné à chaque cellule (tranche, secteur) d'une surface.
    """
    out = {}
    for cellule, rayon in cible.items():
        table = sorted((autres[k][cellule], k) for k in autres if cellule in autres[k])
        v = champ._indice_interpole(rayon, table)
        if v is not None:
            out[cellule] = v
    return out


def _verdict(assignes: dict[tuple[int, int], float]) -> dict:
    """
    @brief Le masque : par cellule, approuvée ou non, et pourquoi.

    ⚠ Le verdict d'identité est porté par la **tranche** et non par la cellule : une avance est
    une pente sur un tour, donc elle n'existe pas au point. Le placement, lui, est local. Une
    cellule est approuvée si les deux tiennent — un ET, pas un OU : une surface bien placée
    dans le vide et une surface qui saute au bon endroit doivent toutes deux être refusées.
    """
    if not assignes:
        return dict(cellules=0)
    par_tranche: dict[int, list[tuple[int, float]]] = {}
    for (tranche, secteur), v in assignes.items():
        par_tranche.setdefault(tranche, []).append((secteur, v))

    avance_de: dict[int, float] = {}
    for tranche, points in par_tranche.items():
        if len(points) < champ.SECTEURS // 2:
            continue
        s = np.array([p[0] for p in points], dtype=float)
        w = np.array([p[1] for p in points], dtype=float)
        avance_de[tranche] = float(np.polyfit(s, w, 1)[0] * champ.SECTEURS)

    # ⚠⚠ L'ENSEMBLE D'ABORD, LES COMPTES ENSUITE. Écrire un `approval.tif` demande de savoir
    # QUELLES cellules sont approuvées, pas seulement combien ; recopier la règle dans une
    # seconde fonction en donnerait deux versions, libres de diverger — la duplication que ce
    # dépôt punit. Une règle, deux consommateurs.
    approuvees_set, placement_ok, identite_ok = set(), 0, 0
    for (tranche, secteur), v in assignes.items():
        p = abs(v - round(v)) <= TOLERANCE_PLACEMENT
        i = abs(avance_de.get(tranche, 9.0)) <= TOLERANCE_IDENTITE
        placement_ok += p
        identite_ok += i
        if p and i:
            approuvees_set.add((tranche, secteur))
    approuvees = len(approuvees_set)
    n = len(assignes)
    return dict(cellules=n, approuvees=approuvees, part_approuvee=approuvees / n,
                cellules_approuvees=approuvees_set,
                part_placement=placement_ok / n, part_identite=identite_ok / n,
                tranches_jugees=len(avance_de),
                fraction_mediane=float(np.median([abs(v - round(v))
                                                  for v in assignes.values()])))


VILLA = RACINE / "data" / "repos" / "villa" / "lasagna" if False else None


def _villa():
    """
    @brief Les deux fonctions d'acceptation de `villa`, importées depuis le dépôt cloné.

    ⚠⚠ IMPORTÉES, PAS RECOPIÉES. Le contrat est le leur — `required = ["x.tif", "y.tif",
    "z.tif", "meta.json", "approval.tif"]`, forme égale à la grille, *« any nonzero sample is
    approved »* — et une seconde version de ce contrat ici finirait par ne plus être le sien.
    Elles n'importent que `numpy` et `tifffile`, donc elles se chargent sans tirer l'optimiseur.
    """
    import importlib.util
    chemin = (Path(__file__).resolve().parents[2] / "data" / "repos" / "villa"
              / "lasagna" / "approval_inpaint.py")
    if not chemin.is_file():
        return None
    spec = importlib.util.spec_from_file_location("villa_approval", chemin)
    mod = importlib.util.module_from_spec(spec)
    # ⚠ Le module doit etre dans `sys.modules` AVANT d'etre execute : `approval_inpaint`
    # declare un `@dataclass`, et `dataclasses` remonte a `sys.modules[cls.__module__]` pour
    # resoudre ses annotations. Sans cette ligne, l'import echoue sur un `AttributeError` de
    # `NoneType` qui ne nomme ni le module ni la cause.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def ecrire_masque(trace: Path, sortie: Path, rouleau: str = "PHerc0139") -> dict:
    """
    @brief Écrire `approval.tif` à côté d'une copie de `x/y/z.tif`, et le faire accepter.

    ⚠⚠⚠ CE QUI MANQUAIT, ET POURQUOI ÇA N'ÉTAIT PAS UNE LIGNE. Le verdict vit sur la grille du
    **champ** — des cellules (tranche de hauteur, secteur d'angle) — et un `approval.tif` vit
    sur la grille **tifxyz** de la trace. Il faut donc porter chaque sommet de la trace dans le
    repère du champ, ce qui demande le même centre par tranche que `_grille` calcule sur
    l'union des spires publiées : un centre global mélangerait des feuilles (`76`).

    ⚠ La forme du masque est celle de la grille ENTIÈRE, pas celle des sommets valides : c'est
    ce que `villa` exige, et un masque de la taille des seuls valides passerait sa vérification
    de forme pour un tout autre objet.

    ⚠ Les cellules sans verdict — hors du champ, ou trop peu peuplées — sont **refusées**, pas
    approuvées par défaut. C'est la limite dure énoncée en tête de ce fichier : un point sans
    encadrement n'est pas approuvé.
    """
    import shutil

    import tifffile

    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    if not nuages:
        raise SystemExit(f"aucune spire chargeable pour {rouleau}")
    bords_z, bords_t, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}

    grilles = {c: tifffile.imread(trace / f"{c}.tif").astype(np.float64) for c in "xyz"}
    x, y, z = grilles["x"], grilles["y"], grilles["z"]
    if not (x.shape == y.shape == z.shape):
        raise SystemExit(f"grilles de formes différentes dans {trace}")
    valide = (x > -0.5) & (y > -0.5) & np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    if valide.sum() < 1000:
        raise SystemExit(f"trop peu de sommets valides dans {trace}")

    # La trace jugée est retirée du champ si elle en fait partie : sinon il la lit.
    autres = {k: v for k, v in rayons.items() if dossiers.get(k) != trace}
    cible = champ._rayons((x[valide], y[valide], z[valide]), bords_z, bords_t, centres)
    assignes = _juger_cellules(cible, autres)
    verdict = _verdict(assignes)
    approuvees = verdict.get("cellules_approuvees") or set()

    # Chaque sommet valide -> sa cellule (tranche, secteur), avec le centre de SA tranche.
    masque = np.zeros(x.shape, dtype=np.uint8)
    lignes, colonnes = np.nonzero(valide)
    tranche = np.digitize(z[valide], bords_z) - 1
    cx = np.array([centres.get(int(t), (np.nan, np.nan))[0] for t in tranche])
    cy = np.array([centres.get(int(t), (np.nan, np.nan))[1] for t in tranche])
    secteur = np.digitize(np.arctan2(y[valide] - cy, x[valide] - cx), bords_t)
    for li, co, t, sec in zip(lignes, colonnes, tranche, secteur):
        if (int(t), int(sec)) in approuvees:
            masque[li, co] = 1

    sortie.mkdir(parents=True, exist_ok=True)
    for nom in ("x.tif", "y.tif", "z.tif", "meta.json"):
        src = trace / nom
        if src.is_file():
            shutil.copy2(src, sortie / nom)
    tifffile.imwrite(sortie / "approval.tif", masque)

    # ⚠⚠⚠ ET ON LE FAIT ACCEPTER PAR `villa`, SUR-LE-CHAMP. Ecrire « au bon nom et au bon
    # format » est precisement l'affirmation que ce fichier a portee a tort pendant des mois ;
    # elle ne se re-ecrit pas, elle se verifie contre le lecteur qui la consomme.
    v = _villa()
    accepte, refus = None, None
    if v is not None:
        try:
            m = v.load_approval_mask(sortie / "approval.tif", expected_shape=x.shape)
            v._load_tifxyz_arrays(sortie)
            accepte = bool(m.shape == x.shape)
        except Exception as e:  # noqa: BLE001 — on RAPPORTE le refus, on ne le masque pas
            accepte, refus = False, f"{type(e).__name__}: {e}"
    return dict(trace=str(trace), sortie=str(sortie), forme=list(x.shape),
                sommets_valides=int(valide.sum()),
                cellules_jugees=verdict.get("cellules", 0),
                cellules_approuvees=len(approuvees),
                part_approuvee=verdict.get("part_approuvee"),
                sommets_approuves=int(masque.sum()),
                part_sommets=float(masque.sum() / max(1, valide.sum())),
                villa_accepte=accepte, villa_refus=refus)


def _melange(a: dict, b: dict, poids) -> dict:
    """
    @brief Une surface fabriquée entre deux spires — `poids` dit comment, par cellule.
    """
    return {c: (1 - poids(c)) * a[c] + poids(c) * b[c] for c in a if c in b}


def mesurer(rouleau: str = "PHerc0139") -> dict:
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(d)) for k, d in dossiers.items()) if v}
    bords_z, bords_t, centres = champ._grille(nuages)
    rayons = {k: champ._rayons(n, bords_z, bords_t, centres) for k, n in nuages.items()}
    rayons = {k: v for k, v in rayons.items() if len(v) > 50}
    indices = sorted(rayons)
    # ⚠ Les defauts connus du referent sont ecartes des SURFACES A JUGER, jamais du champ : ce
    # sont de mauvaises cibles (l'une est un doublon de l'autre), pas de mauvaises references.
    jugeables = [k for k in indices[1:-2] if k not in champ.DEFAUTS_CONNUS]

    bras: dict[str, list[dict]] = {
        "spire, champ complet": [], "spire, à spire exclue": [],
        "quart de pas": [], "demi-pas": [], "saut d'une feuille": []}
    for k in jugeables:
        if k + 1 not in rayons:
            continue
        autres = {j: v for j, v in rayons.items() if j != k}
        cibles = {
            "spire, champ complet": rayons[k],
            "spire, à spire exclue": rayons[k],
            "quart de pas": _melange(rayons[k], rayons[k + 1], lambda c: 0.25),
            "demi-pas": _melange(rayons[k], rayons[k + 1], lambda c: 0.5),
            "saut d'une feuille": _melange(
                rayons[k], rayons[k + 1],
                lambda c: (c[1] - 1) / max(1, champ.SECTEURS - 1)),
        }
        for nom, cible in cibles.items():
            # ⚠⚠⚠ LE CHAMP DOIT CONTENIR LES SPIRES QUI ENCADRENT LA SURFACE JUGEE. Ma
            # premiere version retirait `k+1` pour les surfaces fabriquees, en croyant eviter
            # une fuite -- et ca DETRUISAIT l'information qui detecte un interstice : une
            # translation d'un demi-pas passait de 2,8 % a 79,3 % d'approbation, c'est-a-dire
            # d'un refus net a une approbation nette. Sans la borne haute, le vide entre deux
            # feuilles n'est plus un vide, c'est le milieu d'un intervalle de trois feuilles.
            #
            # Le reglage juste est aussi le plus REALISTE : a l'usage, le champ est tout ce qui
            # est publie et la surface jugee est une trace neuve, absente du champ. Seule une
            # spire publiee doit etre retiree du champ qui la juge, sinon il la lit.
            reference = autres if nom == "spire, à spire exclue" else rayons
            r = _verdict(_juger_cellules(cible, reference))
            if r.get("cellules", 0) >= 20:
                r["spire"] = k
                bras[nom].append(r)

    resume = {}
    for nom, serie in bras.items():
        if serie:
            p = np.array([x["part_approuvee"] for x in serie])
            resume[nom] = dict(n=len(serie), part_mediane=float(np.median(p)),
                               p10=float(np.percentile(p, 10)),
                               p90=float(np.percentile(p, 90)))
    return dict(rouleau=rouleau, spires=len(rayons), jugeables=len(jugeables),
                tolerance_placement=TOLERANCE_PLACEMENT,
                tolerance_identite=TOLERANCE_IDENTITE,
                bras=resume, defauts_ecartes=list(champ.DEFAUTS_CONNUS))


def _verifier_contrat_villa(v) -> list[tuple[str, bool, str]]:
    """
    @brief Le contrat d'acceptation de `villa`, exercé dans LES DEUX SENS, hors ligne.

    ⚠⚠⚠ SANS LE BRAS NÉGATIF, LE CONTRÔLE NE PEUT PAS ÉCHOUER. « `villa` accepte notre masque »
    est satisfait par un lecteur qui accepte tout ; ce qui établit qu'il vérifie quelque chose,
    c'est qu'il **refuse** un masque de mauvaise forme et un dossier auquel il manque un fichier.
    C'est le même bras que la copie translatée d'un demi-pas joue pour le masque lui-même.
    """
    import tempfile

    import numpy as _np
    import tifffile as _tf

    out = []
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)
        forme = (7, 11)
        _tf.imwrite(t / "approval.tif", _np.ones(forme, dtype=_np.uint8))
        for nom in ("x.tif", "y.tif", "z.tif"):
            _tf.imwrite(t / nom, _np.zeros(forme, dtype=_np.float32))
        (t / "meta.json").write_text("{}")
        try:
            m = v.load_approval_mask(t / "approval.tif", expected_shape=forme)
            out.append(("un masque à la bonne forme est accepté", m.shape == forme, str(m.shape)))
        except Exception as e:  # noqa: BLE001
            out.append(("un masque à la bonne forme est accepté", False, str(e)[:80]))
        # ⚠ Bras negatif 1 : la FORME. Un masque de la taille des seuls sommets valides
        # passerait pour un objet valide s'il n'etait pas refuse ici.
        try:
            v.load_approval_mask(t / "approval.tif", expected_shape=(3, 3))
            out.append(("... et une forme fausse est REFUSÉE", False, "accepté à tort"))
        except Exception as e:  # noqa: BLE001
            out.append(("... et une forme fausse est REFUSÉE", True, type(e).__name__))
        # ⚠ Bras negatif 2 : le dossier INCOMPLET. C'est l'autre moitie du contrat.
        (t / "z.tif").unlink()
        try:
            v._load_tifxyz_arrays(t)
            out.append(("... et un dossier incomplet est REFUSÉ", False, "accepté à tort"))
        except Exception as e:  # noqa: BLE001
            out.append(("... et un dossier incomplet est REFUSÉ", True, type(e).__name__))
    return out


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    b = r["bras"]
    print("le masque sait approuver — contrôle de bon sens, pas témoin positif")
    # ⚠ Ce bras est CIRCULAIRE et c'est dit : le champ contient la spire qu'il juge, donc il la
    # lit. Il ne prouve qu'une chose, mais elle doit être prouvée : le masque approuve QUELQUE
    # CHOSE. Un masque qui refuserait tout passerait les trois bras négatifs.
    v("une spire lue par son propre champ est approuvée partout",
      "spire, champ complet" in b and b["spire, champ complet"]["part_mediane"] > 0.98,
      f"{b.get('spire, champ complet', {}).get('part_mediane', 0) * 100:.1f} %")

    print("le témoin POSITIF réaliste : une surface près d'une feuille connue, absente du champ")
    v("un quart de pas est approuvé sur l'essentiel de son aire",
      "quart de pas" in b and b["quart de pas"]["part_mediane"] > 0.80,
      f"{b.get('quart de pas', {}).get('part_mediane', 0) * 100:.1f} % médian "
      f"sur {b.get('quart de pas', {}).get('n', 0)} surfaces")

    # ⚠⚠⚠ LA PATHOLOGIE, NOMMEE PLUTOT QUE RAPPORTEE COMME UN RESULTAT. Une spire jugee a
    # spire exclue tombe EXACTEMENT au milieu de l'intervalle que son retrait vient de creer :
    # le champ la voit donc dans un interstice, par construction. C'est pourquoi une spire
    # publiee ne peut pas etre son propre temoin positif de PLACEMENT -- ni avec son champ
    # (circulaire), ni sans (pathologique). Mesure : 100 % contre 70 %.
    print("⚠ la pathologie : une spire exclue tombe dans l'interstice qu'elle creuse")
    v("... et elle est bien intermédiaire, ni approuvée ni refusée",
      "spire, à spire exclue" in b
      and 0.4 < b["spire, à spire exclue"]["part_mediane"] < 0.9,
      f"{b.get('spire, à spire exclue', {}).get('part_mediane', 0) * 100:.1f} % — "
      f"à ne pas lire comme une performance")

    print("et refuse ce qui ne doit pas l'être — les trois bras négatifs")
    # ⚠⚠⚠ LE BRAS QUI MORD. Sans lui, un masque qui approuve TOUT passe les trois autres.
    v("une copie translatée d'un DEMI-pas est refusée",
      "demi-pas" in b and b["demi-pas"]["part_mediane"] < 0.10,
      f"{b.get('demi-pas', {}).get('part_mediane', 1) * 100:.1f} % approuvé")
    saut = b.get("saut d'une feuille", {})
    v("une surface qui saute une feuille est refusée",
      bool(saut) and saut["part_mediane"] < 0.10,
      f"{saut.get('part_mediane', 1) * 100:.1f} % approuvé")

    # ⚠ Le quart de pas est encore du papyrus : le masque DOIT l'accepter, sinon il ne mesure
    # pas « il y a une feuille ici » mais « la surface est exactement celle que j'ai lue ».
    v("un quart de pas reste accepté — c'est encore du papyrus",
      "quart de pas" in b and b["quart de pas"]["part_mediane"] > 0.50,
      f"{b.get('quart de pas', {}).get('part_mediane', 0) * 100:.1f} % approuvé")

    print("la séparation est nette, pas marginale")
    if "quart de pas" in b and "demi-pas" in b:
        v("le pire cas approuvé bat le meilleur cas refusé",
          b["quart de pas"]["p10"] > b["demi-pas"]["p90"],
          f"quart de pas p10 {b['quart de pas']['p10'] * 100:.1f} % contre "
          f"demi-pas p90 {b['demi-pas']['p90'] * 100:.1f} %")

    print()
    v_mod = _villa()
    if v_mod is None:
        print("  (`villa` absent — le contrat d'acceptation n'est pas exercé)")
    else:
        print("le contrat d'acceptation de `villa`, dans les deux sens")
        for nom, ok, detail in _verifier_contrat_villa(v_mod):
            comptees += 1
            print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
            if not ok:
                echecs += 1

    # ⚠⚠ ET LE MASQUE REELLEMENT ECRIT, s'il l'a ete. `--ecrire` coute une lecture de toutes
    # les spires publiees, donc la batterie RELIT son resultat au lieu de le refaire -- une
    # batterie qui remesurerait est une batterie que personne ne lance.
    cache = RACINE / "docs" / "mesures" / "le_masque_dapprobation_ecrit.json"
    if cache.is_file():
        m = json.loads(cache.read_text())
        print("et le masque écrit")
        for nom, ok, detail in (
            ("`villa` accepte le masque que nous écrivons", bool(m.get("villa_accepte")),
             m.get("villa_refus") or "load_approval_mask + _load_tifxyz_arrays"),
            # ⚠ Un masque qui approuve TOUT passerait le bras precedent : la part doit etre
            # strictement entre 0 et 1, sinon le canal ne porte aucune information.
            ("... et il n'approuve ni rien ni tout",
             0.05 < (m.get("part_sommets") or 0) < 0.98,
             f"{100 * (m.get('part_sommets') or 0):.1f} % des sommets valides"),
        ):
            comptees += 1
            print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
            if not ok:
                echecs += 1

    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--ecrire", type=Path, metavar="SORTIE",
                   help="écrire approval.tif dans ce dossier, depuis --trace")
    p.add_argument("--trace", type=Path,
                   help="le tifxyz à juger (défaut : la première spire jugeable)")
    args = p.parse_args()

    if args.ecrire:
        trace = args.trace
        if trace is None:
            # ⚠ Le defaut est une spire PUBLIEE : c'est la seule surface dont on connaisse la
            # bonne reponse -- elle doit etre largement approuvee -- donc la seule sur laquelle
            # une premiere ecriture se relise.
            dossiers = _spires(args.rouleau)
            jugeables = [k for k in sorted(dossiers) if k not in champ.DEFAUTS_CONNUS]
            if not jugeables:
                raise SystemExit(f"aucune spire jugeable pour {args.rouleau}")
            trace = dossiers[jugeables[len(jugeables) // 2]]
        m = ecrire_masque(Path(trace), args.ecrire, args.rouleau)
        print(f"  trace   {m['trace']}")
        print(f"  grille  {m['forme'][0]}x{m['forme'][1]}  ·  "
              f"{m['sommets_valides']} sommets valides")
        print(f"  verdict {m['cellules_approuvees']}/{m['cellules_jugees']} cellules "
              f"approuvées ({100 * (m['part_approuvee'] or 0):.1f} %)")
        print(f"  masque  {m['sommets_approuves']} sommets à 1 "
              f"({100 * m['part_sommets']:.1f} %)  ->  {m['sortie']}/approval.tif")
        if m["villa_accepte"] is None:
            print("  villa   absent — le contrat n'a pas pu être vérifié")
        elif m["villa_accepte"]:
            print("  villa   ACCEPTE (load_approval_mask + _load_tifxyz_arrays)")
        else:
            print(f"  villa   REFUSE — {m['villa_refus']}")
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  écrit : {args.json}")
        return 0 if m["villa_accepte"] else 1

    r = mesurer(args.rouleau)
    if not args.verifier or args.json:
        print(f"{r['rouleau']} — masque sur {r['jugeables']} spires "
              f"(champ bâti sur {r['spires']})")
        print(f"  seuils : placement {r['tolerance_placement']}, "
              f"identité {r['tolerance_identite']}\n")
        print(f"  {'bras':22s} {'n':>3s} {'approuvé':>9s} {'p10':>7s} {'p90':>7s}")
        for nom, x in r["bras"].items():
            print(f"  {nom:22s} {x['n']:3d} {x['part_mediane'] * 100:8.1f} % "
                  f"{x['p10'] * 100:6.1f} % {x['p90'] * 100:6.1f} %")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {args.json}")
    if args.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
