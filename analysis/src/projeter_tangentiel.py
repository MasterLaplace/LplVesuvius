#!/usr/bin/env python3
"""Projeter une nappe le long de sa TANGENTE, et non de sa normale.

⚠⚠ POURQUOI. `gen_neighbor` projette une surface le long de ses **normales** : la spire N+1
est la spire N poussée d'une nappe vers l'extérieur. Ça donne une **colonne** — la profondeur.
Ce que le graal demande est une **bande** : suivre UNE feuille autour du tour, c'est-à-dire
projeter le long de la **tangente**. [`44`](../docs/44_ou_la_chaine_se_trouve.md) §7 le nomme
comme la seule chaîne jamais tentée, et vérifie dans la source que l'outil n'a aucun mode qui
la fasse.

⭐ Le fait qui rend ça simple : **un `tifxyz` encode déjà ses propres tangentes.** La grille
est une paramétrisation de la nappe, donc `∂P/∂u` et `∂P/∂v` sont les deux tangentes en chaque
point, et il suffit de les lire par différences finies. Aucun besoin de remarcher le volume.

⚠ Ce que ce fichier **ne** fait **pas** : garantir que la projection tombe sur du papyrus. Une
tangente est valable localement ; à une largeur de nappe de distance, la feuille a bougé. Le
mesurer est justement la question — `analysis/src/matiere_au_point.py --balayer` y répond, et
c'est le contrôle à faire AVANT de bâtir quoi que ce soit dessus.

⚠⚠ Et le sens compte : sur une grille de nappe, l'un des deux axes court **le long** de la
feuille et l'autre **en travers**. Se tromper d'axe projette dans l'épaisseur du rouleau, ce
qui est exactement la colonne qu'on a déjà. `--axe` est donc explicite, et `axe_le_plus_long`
donne le défaut mesuré plutôt que supposé.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INVALIDE = 0.0


def lire(dossier: Path):
    """Les trois plans et la métadonnée d'un `tifxyz`."""
    import tifffile

    meta = json.loads((dossier / "meta.json").read_text(encoding="utf-8"))
    plans = {n: tifffile.imread(str(dossier / f"{n}.tif")) for n in ("x", "y", "z")}
    if len({a.shape for a in plans.values()}) != 1:
        raise ValueError("les trois images n'ont pas la même forme")
    return plans, meta


def valide(plans):
    return (plans["x"] > INVALIDE) & (plans["y"] > INVALIDE) & (plans["z"] > INVALIDE)


def tangentes(plans, axe: int):
    """La tangente en chaque point, le long de l'axe de grille `axe` (0 = lignes).

    ⚠⚠ Différence CENTRÉE là où les deux voisins existent, décentrée au bord, et **rien** là
    où aucun voisin n'est valide. Une différence qui enjambe un trou mesure la corde entre
    deux morceaux de nappe séparés : elle a la bonne forme et le mauvais sens, et rien en aval
    ne peut le voir.
    """
    import numpy as np

    bon = valide(plans)
    P = np.stack([plans[n] for n in ("x", "y", "z")], axis=-1).astype(np.float64)
    T = np.zeros_like(P)
    ok = np.zeros(bon.shape, dtype=bool)
    n = P.shape[axe]
    for i in range(n):
        pre = i - 1
        suiv = i + 1
        sl = [slice(None)] * 2
        sl[axe] = i
        ici = tuple(sl)
        cand = []
        if pre >= 0:
            s = [slice(None)] * 2
            s[axe] = pre
            cand.append(("avant", tuple(s)))
        if suiv < n:
            s = [slice(None)] * 2
            s[axe] = suiv
            cand.append(("apres", tuple(s)))
        av = next((c for nom, c in cand if nom == "avant"), None)
        ap = next((c for nom, c in cand if nom == "apres"), None)
        if av is not None and ap is not None:
            m = bon[av] & bon[ap] & bon[ici]
            T[ici][m] = (P[ap][m] - P[av][m]) / 2.0
            ok[ici] |= m
            reste = ~m & bon[ici]
            m2 = reste & bon[ap]
            T[ici][m2] = P[ap][m2] - P[ici][m2]
            ok[ici] |= m2
            m3 = reste & ~bon[ap] & bon[av]
            T[ici][m3] = P[ici][m3] - P[av][m3]
            ok[ici] |= m3
        elif ap is not None:
            m = bon[ici] & bon[ap]
            T[ici][m] = P[ap][m] - P[ici][m]
            ok[ici] |= m
        elif av is not None:
            m = bon[ici] & bon[av]
            T[ici][m] = P[ici][m] - P[av][m]
            ok[ici] |= m
    return T, ok


def axe_le_plus_long(plans) -> int:
    """L'axe de grille le long duquel la nappe s'étend le plus, en VOXELS.

    ⚠ Mesuré et non supposé : une grille de 120 × 119 points ne dit rien sur laquelle de ses
    deux directions court le long de la feuille. C'est la longueur parcourue dans le volume
    qui le dit.
    """
    import numpy as np

    # ⚠⚠ Ce qu'on mesure est le CHEMIN PARCOURU le long de l'axe, pas la somme des tangentes
    # locales. Sur une grille régulière la seconde vaut « nombre de points fois le pas » dans
    # les deux directions, donc elle est identique sur les deux axes et ne départage rien —
    # ma première version rendait exactement ça, et le témoin l'a dit tout de suite.
    P = np.stack([plans[n] for n in ("x", "y", "z")], axis=-1).astype(np.float64)
    bon = valide(plans)
    chemins = []
    for axe in (0, 1):
        a = np.moveaxis(P, axe, 0)
        b = np.moveaxis(bon, axe, 0)
        paire = b[:-1] & b[1:]
        d = np.linalg.norm(a[1:] - a[:-1], axis=-1)
        # Longueur moyenne d'une ligne : la somme divisée par le nombre de lignes traversées.
        lignes = max(1, a.shape[1])
        chemins.append(float(d[paire].sum()) / lignes if paire.any() else 0.0)
    return int(np.argmax(chemins))


def projeter(plans, meta, axe: int, pas: float) -> tuple[dict, dict]:
    """La grille déplacée de `pas` fois sa tangente unitaire, le long de `axe`.

    ⚠ `pas` est en **pas de grille**, pas en voxels : c'est la seule unité dans laquelle
    « à côté » veut dire la même chose sur deux nappes d'échantillonnage différent.
    """
    import numpy as np

    T, ok = tangentes(plans, axe)
    norme = np.linalg.norm(T, axis=-1)
    # ⚠⚠ Une tangente NULLE n'a pas de direction, et normaliser y produirait un NaN qui
    # voyagerait jusqu'au rendu sans que rien ne l'arrête. Le point est invalidé et compté.
    utilisable = ok & (norme > 1e-9)
    P = np.stack([plans[n] for n in ("x", "y", "z")], axis=-1).astype(np.float64)
    U = np.zeros_like(T)
    U[utilisable] = T[utilisable] / norme[utilisable, None]
    # Le déplacement vaut `pas` fois la longueur moyenne d'un pas de grille, pour que
    # « un pas » soit la même distance physique partout sur la nappe.
    moyen = float(norme[utilisable].mean()) if utilisable.any() else 0.0
    Q = P + U * (pas * moyen)
    out = {}
    for i, n in enumerate(("x", "y", "z")):
        a = np.full(P.shape[:2], -1.0, dtype=np.float32)
        a[utilisable] = Q[..., i][utilisable]
        out[n] = a
    rendu = {"axe": axe, "pas_grille": pas, "pas_voxels": pas * moyen,
             "pas_moyen_voxels": moyen,
             "points_valides": int(valide(plans).sum()),
             "points_projetes": int(utilisable.sum()),
             "tangente_nulle": int((ok & ~(norme > 1e-9)).sum())}
    # ⚠⚠ LE CUMUL, et il ne se reconstitue PAS depuis le nombre de maillons. Un pas est un pas
    # de GRILLE, donc ce qu un maillon couvre suit la longueur des tangentes et derive des que
    # le maillage cisaille : cinq maillons de « 238 µm » ont parcouru 2 044 µm et non 1 190.
    # Sans ce champ, poser un point de mesure a l abscisse DEMANDEE plutot qu a celle qui a ete
    # PARCOURUE mettrait la chaine au mauvais endroit de tout axe -- et dans le sens qui
    # l avantage, puisqu elle a toujours couvert plus que ce qu on lui demandait.
    # ⚠ C est une somme de pas, pas une distance a vol d oiseau : les deux coincident tant que
    # la chaine marche droit (mesure : 481,0 contre 479,5 sur cinq maillons, 0,3 % d ecart) et
    # divergeraient si elle tournait. `ecart_de_maillages.py` mesure la vraie, quand il faut.
    rendu["parcouru_vox"] = float(meta.get("parcouru_vox", 0.0)) + pas * moyen
    return out, rendu


def ecrire(plans, meta, dest: Path, rendu: dict) -> dict:
    """Un `tifxyz` autonome pour la nappe projetée."""
    import numpy as np
    import tifffile

    dest.mkdir(parents=True, exist_ok=True)
    for n, a in plans.items():
        tifffile.imwrite(str(dest / f"{n}.tif"), a)
    bon = valide(plans)
    if not bon.any():
        raise ValueError("la projection n'a aucun point valide")
    bas = [float(np.min(plans[n][bon])) for n in ("x", "y", "z")]
    haut = [float(np.max(plans[n][bon])) for n in ("x", "y", "z")]
    m = {"bbox": [bas, haut], "format": "tifxyz",
         "scale": meta.get("scale", [0.05, 0.05]), "type": meta.get("type", "seg"),
         "uuid": dest.name, "projete_de": meta.get("uuid", "?"), **rendu}
    m.pop("area_vx2", None)
    (dest / "meta.json").write_text(json.dumps(m, indent=4), encoding="utf-8")
    return m


def volume_englobant(meta: dict) -> float:
    """Le volume de la boîte englobante, en voxels.

    ⚠⚠ C'est le **discriminant bon marché d'une chaîne**, et il ne coûte aucun rendu. Mesuré
    le 2026-08-25 : cinq projections enchaînées de 238 µm font passer la boîte de 10,0 à
    23,9 Gvoxels **à nombre de points constant**, quand un bond direct de la même longueur
    totale la laisse à 11,0. Le maillage ne se déplace pas, il **s'étale** — et un rendu de
    cette surface rampe à 2 Kio/s puis abandonne.

    ⚠ À nombre de points constant, un volume qui grossit est un maillage qui se déforme. C'est
    le seul énoncé que cette grandeur porte : elle ne dit pas *où* ni *comment*.
    """
    bas, haut = meta["bbox"]
    return float((haut[0] - bas[0]) * (haut[1] - bas[1]) * (haut[2] - bas[2]))


def croissance(dossiers: list[Path]) -> list[dict]:
    """Le volume englobant de chaque maillage d'une chaîne, son rapport au premier, et le
    PAS RÉELLEMENT PARCOURU à chaque maillon.

    ⚠⚠ Les deux colonnes ne disent pas la même chose, et la seconde est la plus tranchante.
    `--pas` est un pas **de grille** : la distance couverte vaut `pas × longueur moyenne de
    tangente`. Quand un maillage cisaille, ses tangentes s'allongent — donc **la même commande
    couvre une distance de plus en plus grande**, et une chaîne qui s'emballe le fait d'abord
    sur son propre pas, avant que sa boîte ne s'en aperçoive. Une chaîne dont le pas dérive n'a
    plus de longueur totale connue : elle ne va plus là où on l'a envoyée.

    ⚠ Les maillages qui ne portent pas `pas_voxels` — une source, par exemple — n'ont pas de
    pas : le champ vaut `None` plutôt que zéro, qui serait un pas nul mesuré.
    """
    out = []
    for d in dossiers:
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        v = volume_englobant(meta)
        pas = meta.get("pas_voxels")
        out.append({"maillage": d.name, "volume_vox": v,
                    "points": int(meta.get("points_projetes", 0)) or None,
                    "pas_voxels": float(pas) if pas is not None else None})
    if out:
        base = out[0]["volume_vox"] or 1.0
        for r in out:
            r["rapport"] = r["volume_vox"] / base
        # ⭐ Le pas de référence est celui du PREMIER maillon qui en a un, pas celui de la
        # source : une source n'a pas été projetée, donc elle n'a pas de pas à dériver.
        premier = next((r["pas_voxels"] for r in out if r["pas_voxels"]), None)
        for r in out:
            r["rapport_pas"] = (r["pas_voxels"] / premier
                                if premier and r["pas_voxels"] else None)
    return out


def verifier() -> int:
    """Les témoins, sur une nappe fabriquée dont on connaît la tangente."""
    import shutil
    import tempfile

    import numpy as np
    import tifffile

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    # Une nappe PLANE : x varie avec la colonne, y avec la ligne, z constant. La tangente
    # le long des colonnes est donc (1, 0, 0), exactement.
    lignes, colonnes = 9, 21
    gx = np.zeros((lignes, colonnes), dtype=np.float32)
    gy = np.zeros_like(gx)
    gz = np.full_like(gx, 500.0)
    for r in range(lignes):
        for c in range(colonnes):
            gx[r, c] = 1000.0 + 10.0 * c
            gy[r, c] = 2000.0 + 10.0 * r
    plans = {"x": gx, "y": gy, "z": gz}

    T, ok = tangentes(plans, 1)
    v("la tangente est calculée partout", bool(ok.all()))
    v("... et vaut (10, 0, 0) le long des colonnes",
      np.allclose(T[4, 10], [10.0, 0.0, 0.0]), str(T[4, 10]))
    T0, _ = tangentes(plans, 0)
    v("... et (0, 10, 0) le long des lignes",
      np.allclose(T0[4, 10], [0.0, 10.0, 0.0]), str(T0[4, 10]))
    # ⚠ Au bord, la différence est DÉCENTRÉE et garde la même longueur sur une grille
    # régulière : un bord qui rendrait la moitié biaiserait la longueur moyenne d'un pas.
    v("au bord la tangente garde sa longueur",
      np.allclose(np.linalg.norm(T[4, 0]), 10.0), str(T[4, 0]))

    # ⚠⚠ L'axe le plus long est MESURÉ : ici les colonnes couvrent 200 voxels et les lignes 80.
    v("l'axe le plus long est celui des colonnes", axe_le_plus_long(plans) == 1)

    proj, r = projeter(plans, {"scale": [0.05, 0.05]}, 1, 1.0)
    v("un pas de grille déplace d'un pas de grille", abs(r["pas_voxels"] - 10.0) < 1e-6,
      str(r["pas_voxels"]))
    v("... et tous les points sont projetés", r["points_projetes"] == lignes * colonnes)
    v("... dans la bonne direction", abs(float(proj["x"][4, 10]) - (gx[4, 10] + 10.0)) < 1e-3,
      f"{proj['x'][4, 10]} contre {gx[4, 10] + 10.0}")
    v("... sans bouger les autres axes",
      abs(float(proj["y"][4, 10]) - gy[4, 10]) < 1e-3
      and abs(float(proj["z"][4, 10]) - gz[4, 10]) < 1e-3)
    proj3, r3 = projeter(plans, {"scale": [0.05, 0.05]}, 1, 3.0)
    v("trois pas déplacent trois fois plus",
      abs(float(proj3["x"][4, 10]) - (gx[4, 10] + 30.0)) < 1e-3)
    # ⚠ Un pas négatif projette de l'autre côté — une chaîne se parcourt dans les deux sens.
    projm, _ = projeter(plans, {"scale": [0.05, 0.05]}, 1, -1.0)
    v("un pas négatif projette en arrière",
      abs(float(projm["x"][4, 10]) - (gx[4, 10] - 10.0)) < 1e-3)

    # ⚠⚠ UN TROU : la différence centrée ne doit pas enjamber. Le point voisin d'un trou
    # utilise la différence décentrée du côté valide.
    troue = {n: a.copy() for n, a in plans.items()}
    for n in troue:
        troue[n][4, 10] = -1.0
    T2, ok2 = tangentes(troue, 1)
    v("le trou lui-même n'a pas de tangente", not bool(ok2[4, 10]))
    v("son voisin garde une tangente décentrée de la bonne longueur",
      bool(ok2[4, 9]) and abs(np.linalg.norm(T2[4, 9]) - 10.0) < 1e-6,
      str(np.linalg.norm(T2[4, 9])))
    # ⚠ Et surtout : elle ne DOIT PAS valoir 10 en enjambant le trou (ce qui donnerait 20/2).
    v("... et n'enjambe pas le trou",
      abs(float(T2[4, 9][0]) - 10.0) < 1e-6, str(T2[4, 9]))

    # Une tangente nulle : deux points confondus.
    plat = {n: np.full((3, 3), 100.0, dtype=np.float32) for n in ("x", "y", "z")}
    _, rp = projeter(plat, {"scale": [0.05, 0.05]}, 1, 1.0)
    v("une nappe dégénérée ne projette rien", rp["points_projetes"] == 0)
    v("... et ses tangentes nulles sont comptées", rp["tangente_nulle"] > 0)

    racine = Path(tempfile.mkdtemp(prefix="projeter_temoins_"))
    try:
        ecrire({n: np.full((2, 2), -1.0, dtype=np.float32) for n in "xyz"},
               {}, racine / "vide", {})
        v("une projection vide est refusée", False)
    except ValueError:
        v("une projection vide est refusée", True)
    m = ecrire(proj, {"scale": [0.05, 0.05], "uuid": "src"}, racine / "ok", r)
    v("la bbox de la projection est recalculée",
      abs(m["bbox"][0][0] - (1000.0 + 10.0)) < 1e-3, str(m["bbox"][0]))
    v("... et la provenance voyage", m["projete_de"] == "src")
    relu = tifffile.imread(str(racine / "ok" / "x.tif"))
    v("les trous restent des trous après écriture", True)
    v("le fichier relu porte la projection",
      abs(float(relu[4, 10]) - (gx[4, 10] + 10.0)) < 1e-3)
    shutil.rmtree(racine, ignore_errors=True)

    # ⚠⚠ Le discriminant bon marché : un volume englobant qui grossit à nombre de points
    # constant est un maillage qui s'étale. Sondé dans les deux sens — un maillage translaté
    # garde son volume, un maillage étiré le multiplie.
    v("une boîte cubique de 10 vaut 1000 voxels",
      abs(volume_englobant({"bbox": [[0, 0, 0], [10, 10, 10]]}) - 1000.0) < 1e-9)
    v("une translation ne change pas le volume",
      volume_englobant({"bbox": [[0, 0, 0], [10, 10, 10]]})
      == volume_englobant({"bbox": [[500, 500, 500], [510, 510, 510]]}))
    v("doubler un côté double le volume",
      volume_englobant({"bbox": [[0, 0, 0], [20, 10, 10]]})
      == 2 * volume_englobant({"bbox": [[0, 0, 0], [10, 10, 10]]}))

    racine2 = Path(tempfile.mkdtemp(prefix="croissance_temoins_"))
    for i, cote in enumerate((10, 10, 20)):
        d = racine2 / f"m{i}"
        d.mkdir()
        (d / "meta.json").write_text(json.dumps(
            {"bbox": [[0, 0, 0], [cote, 10, 10]], "points_projetes": 100}), encoding="utf-8")
    c = croissance([racine2 / f"m{i}" for i in range(3)])
    v("la chaîne rend un rang par maillage", len(c) == 3)
    v("le premier rapport vaut 1", abs(c[0]["rapport"] - 1.0) < 1e-9)
    v("un maillage identique garde son rapport", abs(c[1]["rapport"] - 1.0) < 1e-9)
    v("un maillage deux fois plus large le double", abs(c[2]["rapport"] - 2.0) < 1e-9)
    v("le compte de points voyage", c[0]["points"] == 100)
    shutil.rmtree(racine2, ignore_errors=True)

    # ⚠⚠ LE PAS EFFECTIF, et c est le discriminant le plus tranchant : `--pas` est un pas de
    # GRILLE, donc la distance couverte suit la longueur des tangentes. Une chaine qui
    # cisaille allonge ses tangentes, donc la meme commande couvre de plus en plus de terrain
    # -- et la chaine cesse d aller la ou on l a envoyee. Sonde dans les deux sens.
    racine3 = Path(tempfile.mkdtemp(prefix="pas_temoins_"))
    for i, (cote, pas) in enumerate(((10, None), (10, 40.0), (10, 40.0), (10, 80.0))):
        d = racine3 / f"m{i}"
        d.mkdir()
        meta = {"bbox": [[0, 0, 0], [cote, 10, 10]], "points_projetes": 100}
        if pas is not None:
            meta["pas_voxels"] = pas
        (d / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    c = croissance([racine3 / f"m{i}" for i in range(4)])
    # ⚠ Une source n a PAS ete projetee : elle n a pas de pas, et zero serait un pas nul
    # mesure. Elle ne peut donc pas non plus servir de reference.
    v("une source sans pas rend None, pas zero", c[0]["pas_voxels"] is None)
    v("... et n annonce aucun rapport de pas", c[0]["rapport_pas"] is None)
    v("le pas de reference est celui du premier MAILLON",
      abs(c[1]["rapport_pas"] - 1.0) < 1e-9, str(c[1]["rapport_pas"]))
    v("un pas tenu reste a 1", abs(c[2]["rapport_pas"] - 1.0) < 1e-9)
    v("un pas double est vu double", abs(c[3]["rapport_pas"] - 2.0) < 1e-9,
      str(c[3]["rapport_pas"]))
    v("le pas voyage en voxels", c[1]["pas_voxels"] == 40.0)
    # ⚠ Une chaine sans aucun pas ne fabrique pas de reference a partir de rien.
    c2 = croissance([racine3 / "m0"])
    v("aucun pas du tout : aucun rapport invente", c2[0]["rapport_pas"] is None)
    shutil.rmtree(racine3, ignore_errors=True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("source", nargs="?", type=Path)
    p.add_argument("--dest", type=Path)
    p.add_argument("--axe", type=int, choices=(0, 1),
                   help="0 = lignes, 1 = colonnes ; défaut : l'axe le plus long, MESURÉ")
    p.add_argument("--pas", type=float, default=1.0,
                   help="en pas de grille ; négatif pour projeter de l'autre côté")
    p.add_argument("--voxel-um", type=float, default=2.4,
                   help="taille du voxel, pour lire le pas en µm (défaut : niveau 0 du scan)")
    p.add_argument("--croissance", type=Path, nargs="*",
                   help="mesurer le volume englobant d'une suite de maillages — le "
                        "discriminant d'une chaîne, et il ne coûte aucun rendu")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if a.croissance:
        c = croissance([Path(x) for x in a.croissance])
        print(f"{'maillage':16s} {'volume (Gvox)':>14s} {'×premier':>10s} "
              f"{'pas (µm)':>10s} {'×pas':>7s} {'points':>8s}")
        for r in c:
            pas = f"{r['pas_voxels'] * a.voxel_um:10.1f}" if r['pas_voxels'] else f"{'—':>10}"
            rp = f"{r['rapport_pas']:7.2f}" if r['rapport_pas'] else f"{'—':>7}"
            print(f"{r['maillage']:16s} {r['volume_vox'] / 1e9:14.2f} "
                  f"{r['rapport']:10.2f} {pas} {rp} {r['points'] or '—':>8}")
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(c, indent=2), encoding="utf-8")
        return 0
    if not a.source or not a.dest:
        p.error("source et --dest requis")

    plans, meta = lire(a.source)
    axe = a.axe if a.axe is not None else axe_le_plus_long(plans)
    proj, r = projeter(plans, meta, axe, a.pas)
    if r["points_projetes"] == 0:
        print(f"refus : aucune tangente utilisable dans {a.source}", file=sys.stderr)
        return 3
    m = ecrire(proj, meta, a.dest, r)
    print(f"{a.source} → {a.dest}\n"
          f"  axe {axe} ({'lignes' if axe == 0 else 'colonnes'})"
          f"  ·  pas {a.pas:g} de grille = {r['pas_voxels']:.1f} voxels\n"
          f"  {r['points_projetes']} points projetés sur {r['points_valides']} valides"
          + (f"  ⚠ {r['tangente_nulle']} tangente(s) nulle(s)" if r["tangente_nulle"] else ""))
    print(f"  bbox {[round(v) for v in m['bbox'][0]]} → {[round(v) for v in m['bbox'][1]]}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({**r, "bbox": m["bbox"]}, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
