#!/usr/bin/env python3
"""Treize spires publiées de `PHerc0500P2` : s'empilent-elles comme des feuilles voisines ?

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET C'EST UN ANGLE MORT DU DÉPÔT. L'index connaît **39**
segments pour ce fragment, dont **treize nommés `wrap01` à `wrap13`**, chacun publiant sa surface
en `tifxyz` **sur les trois volumes**. Aucune mesure du dépôt ne les a jamais ouverts : tout le
travail sur la chaîne, la spire et l'écart inter-feuilles a été fait en reconstruisant depuis le
volume brut, alors qu'une **vérité de terrain du déroulement** était publiée à côté.

⭐⭐⭐ **C'est la cinquième fois que cet angle mort coûte quelque chose** — le référent avait été
déclaré absent faute d'avoir interrogé un serveur, et ici c'est un dossier de l'index qu'on n'a
jamais énuméré. La leçon est la même : *ce qu'on croit absent doit être cherché avant d'être
reconstruit*.

⚠⚠ ET LA QUESTION SE POSE AVANT DE SE RÉJOUIR : ces treize surfaces sont-elles vraiment des
spires **consécutives** ? Le nom le dit, la mesure doit le montrer. Deux spires voisines sont
séparées d'**un** écart inter-feuilles ; deux spires distantes de deux rangs, d'environ le
double. Si l'écart ne croît pas avec le rang, « wrap » n'est qu'une étiquette.

⚠ L'attendu vient d'une mesure déjà publiée du dépôt — **147,4 µm** sur `PHerc0172`
(`la_surface_et_la_feuille`), 142,8 et 172,8 ailleurs — et non d'un seuil choisi ici.

Usage :
    uv run python src/nappe/les_wraps_publies.py --verifier
    uv run python src/nappe/les_wraps_publies.py --json docs/mesures/les_wraps_publies.json
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "encre"))

FRAGMENT = "PHerc0500P2"
VOLUME = "20250526151718"
VOXEL_UM = 2.215

RANG = re.compile(r"wrap(\d+)")


def wraps_du_fragment(fragment: str = FRAGMENT) -> list[dict]:
    """Les segments « wrap » de l'index, **dans l'ordre de leur rang**.

    ⚠⚠⚠ L'ORDRE VIENT DU NUMÉRO, PAS DE L'IDENTIFIANT, et la différence est réelle : `wrap11`
    porte l'horodatage `20250922024644` quand `wrap12` et `wrap13` portent `20250920…`. Trier
    par identifiant mettrait donc la onzième spire **après** la treizième, et toute mesure
    « entre spires consécutives » comparerait des voisines qui ne le sont pas.
    """
    import la_case_vide as cv  # noqa: PLC0415

    vus, out = set(), []
    for _, fiche in cv._charger().items():
        for sid, seg in fiche.get("segments", {}).items():
            nom = seg.get("long_id", sid)
            m = RANG.search(nom)
            if m is None or nom in vus:
                continue
            vus.add(nom)
            out.append(dict(nom=nom, rang=int(m.group(1)), horodatage=nom.split("-")[0]))
    return sorted(out, key=lambda e: e["rang"])


def surface(wrap: dict, volume: str = VOLUME, fragment: str = FRAGMENT,
            pas: int = 1) -> np.ndarray | None:
    """Les points 3D de la surface d'une spire, en voxels du volume, sans les invalides.

    ⚠ Les cellules invalides sont marquées par des coordonnées nulles ou négatives — c'est ce
    que le format écrit hors de la découpe — et les garder placerait une feuille entière à
    l'origine du volume, ce qui rendrait toute distance absurde sans rien lever.
    """
    from PIL import Image  # noqa: PLC0415

    from zarr_depth import BUCKET, get  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None
    base = (f"{BUCKET}/{fragment}/segments/{wrap['nom']}/mesh/"
            f"{wrap['horodatage']}-on-{volume}-{VOXEL_UM}um.tifxyz")
    canaux = []
    for c in "xyz":
        brut = get(f"{base}/{c}.tif", 300)
        if brut is None:
            return None
        canaux.append(np.asarray(Image.open(io.BytesIO(brut)), dtype=np.float64))
    a = np.stack(canaux, axis=-1)[::pas, ::pas]
    ok = np.all(np.isfinite(a), axis=-1) & np.all(a > 0, axis=-1)
    return a[ok]


def ecart(a: np.ndarray, b: np.ndarray, voxel_um: float = VOXEL_UM) -> dict:
    """La distance de chaque point de `a` à la surface `b`, en micromètres.

    ⚠⚠ Rendue par PERCENTILES et pas seulement en médiane : deux spires qui se touchent sur un
    bord et s'écartent ailleurs ont une médiane trompeuse, et c'est exactement la forme d'un
    fragment enroulé dont les spires ne se recouvrent qu'en partie.

    ⚠ La distance est celle de `a` **vers** `b`, donc asymétrique : `b` peut s'étendre là où `a`
    n'existe pas. L'appelant mesure les deux sens quand la symétrie compte.
    """
    from scipy.spatial import cKDTree  # noqa: PLC0415

    if a.size == 0 or b.size == 0:
        return {}
    d = cKDTree(b).query(a, k=1)[0] * voxel_um
    return dict(points=int(a.shape[0]),
                mediane_um=round(float(np.median(d)), 1),
                p10_um=round(float(np.percentile(d, 10)), 1),
                p90_um=round(float(np.percentile(d, 90)), 1))


def attendu_publie() -> dict:
    """L'écart inter-feuilles déjà mesuré ailleurs dans le dépôt — LU, jamais retapé.

    ⚠⚠ L'attendu ne peut pas venir d'ici : un fichier qui choisirait sa propre cible la
    trouverait. Il vient de `la_surface_et_la_feuille`, mesuré sur un autre rouleau, donc c'est
    une prédiction extérieure — et c'est ce qui rend l'accord informatif.
    """
    chemin = RACINE / "docs" / "mesures" / "la_surface_et_la_feuille.json"
    if not chemin.is_file():
        return {}
    d = json.loads(chemin.read_text())
    return {k: v for k, v in d.items() if k == "ecart_inter_feuilles_um"}


def mesurer(pas: int = 1, volume: str = VOLUME) -> dict:
    """Les treize spires, leurs voisines, et le contrôle du rang."""
    liste = wraps_du_fragment()
    if len(liste) < 3:
        raise SystemExit(f"trop peu de spires publiées : {len(liste)}")
    surfaces, absentes = {}, []
    for w in liste:
        s = surface(w, volume, pas=pas)
        if s is None or s.size == 0:
            absentes.append(w["nom"])
            continue
        surfaces[w["rang"]] = s
    rangs = sorted(surfaces)

    def serie(saut: int) -> list[dict]:
        out = []
        for r in rangs:
            if r + saut not in surfaces:
                continue
            e = ecart(surfaces[r], surfaces[r + saut])
            if e:
                out.append(dict(de=r, vers=r + saut, **e))
        return out

    # ⚠ Une trace projetée par spire est publiée pour la figure : la recalculer là-bas voudrait
    # dire re-télécharger treize surfaces, donc dessiner autre chose que ce qui est jugé ici.
    traces = {}
    for r in rangs:
        pts = surfaces[r]
        k = max(1, pts.shape[0] // 400)
        traces[str(r)] = [[round(float(x), 1), round(float(z), 1)]
                          for x, _, z in pts[::k][:400]]
    sauts = {str(k): serie(k) for k in (1, 2, 3)}
    medianes = {k: [e["mediane_um"] for e in v] for k, v in sauts.items()}
    resume = {k: dict(paires=len(v),
                      mediane_um=round(float(np.median(v)), 1) if v else None)
              for k, v in medianes.items()}
    return dict(fragment=FRAGMENT, volume=volume, voxel_um=VOXEL_UM, pas=pas,
                spires_publiees=len(liste), spires_lues=len(surfaces),
                spires_absentes=absentes,
                rangs=rangs,
                points_par_spire={str(r): int(surfaces[r].shape[0]) for r in rangs},
                attendu_publie=attendu_publie(),
                traces_xz=traces, sauts=sauts, resume=resume,
                # ⚠⚠ LE CONTRÔLE QUI DIT SI « CONSÉCUTIF » VEUT DIRE QUELQUE CHOSE : l'écart doit
                # CROÎTRE avec le rang. S'il est plat, les treize surfaces ne sont pas empilées,
                # et le mot « wrap » n'est qu'une étiquette de nommage.
                croit_avec_le_rang=bool(
                    resume["1"]["mediane_um"] is not None
                    and resume["2"]["mediane_um"] is not None
                    and resume["3"]["mediane_um"] is not None
                    and resume["1"]["mediane_um"] < resume["2"]["mediane_um"]
                    < resume["3"]["mediane_um"]))


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠⚠ L'ORDRE PAR RANG CONTRE L'ORDRE PAR IDENTIFIANT, sur le cas RÉEL qui les sépare :
    # `wrap11` est horodaté après `wrap12` et `wrap13`. Un tri par identifiant mettrait donc la
    # onzième spire après la treizième, et « spires consécutives » comparerait des étrangères.
    faux = ["20250920020223-0500P2-wrap12_0919", "20250922024644-0500P2-wrap11_0919",
            "20250920020224-0500P2-wrap13_0919"]
    rangs = [int(RANG.search(n).group(1)) for n in faux]
    v("le rang se lit dans le nom", rangs == [12, 11, 13], str(rangs))
    tries = [n for _, n in sorted(zip(rangs, faux))]
    v("... et trier par rang diffère de trier par identifiant",
      tries != sorted(faux), f"{[t[-14:] for t in tries]}")
    v("... l'ordre par rang met bien 11 avant 12",
      tries[0].endswith("wrap11_0919"), tries[0][-14:])

    # --- l'écart, sur des plans dont la distance est connue ---
    xx, yy = np.meshgrid(np.arange(0, 40, 2.0), np.arange(0, 40, 2.0))
    plat = np.stack([xx.ravel(), yy.ravel(), np.zeros(xx.size)], axis=1)
    for d_vx in (10.0, 40.0):
        e = ecart(plat, plat + np.array([0.0, 0.0, d_vx]), voxel_um=2.0)
        v(f"deux plans à {d_vx:.0f} voxels sont mesurés à {d_vx * 2:.0f} µm",
          abs(e["mediane_um"] - d_vx * 2.0) < 1e-6, str(e["mediane_um"]))
    v("les percentiles encadrent la médiane",
      (lambda e: e["p10_um"] <= e["mediane_um"] <= e["p90_um"])(
          ecart(plat, plat + np.array([3.0, 0.0, 10.0]), voxel_um=2.0)))
    v("une surface vide ne rend rien", ecart(np.zeros((0, 3)), plat) == {})

    # ⚠⚠⚠ LE CONTRÔLE QUI DONNE SON SENS À TOUT : sur une pile de plans, l'écart doit CROÎTRE
    # avec le rang. Sans lui, une mesure qui rendrait toujours la distance au plan le plus proche
    # passerait, et « les spires sont empilées » serait invérifiable.
    pile = [plat + np.array([0.0, 0.0, k * 12.0]) for k in range(4)]
    e1 = float(np.median([ecart(pile[k], pile[k + 1], 2.0)["mediane_um"] for k in range(3)]))
    e2 = float(np.median([ecart(pile[k], pile[k + 2], 2.0)["mediane_um"] for k in range(2)]))
    v("sur une pile, l'écart croît avec le rang", e1 < e2, f"{e1:.0f} puis {e2:.0f} µm")
    # ⚠ Et le cas où il ne croît PAS : quatre copies du même plan. Une mesure qui ne saurait pas
    # le dire ne saurait rien dire.
    tas = [plat.copy() for _ in range(4)]
    f1 = float(np.median([ecart(tas[k], tas[k + 1], 2.0)["mediane_um"] for k in range(3)]))
    f2 = float(np.median([ecart(tas[k], tas[k + 2], 2.0)["mediane_um"] for k in range(2)]))
    v("... et il ne croît pas quand les surfaces sont confondues", f1 == f2 == 0.0)

    a = attendu_publie()
    v("l'attendu est LU dans une mesure du dépôt, pas écrit ici",
      "ecart_inter_feuilles_um" in a, str(a))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pas", type=int, default=1, help="sous-échantillonnage de la grille")
    p.add_argument("--volume", default=VOLUME)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.pas, a.volume)
    print(f"{r['spires_lues']} spires lues sur {r['spires_publiees']} publiées "
          f"(volume {r['volume']}, {r['voxel_um']} µm/voxel)")
    if r["spires_absentes"]:
        print(f"  absentes : {', '.join(x[-14:] for x in r['spires_absentes'])}")
    att = r["attendu_publie"].get("ecart_inter_feuilles_um")
    print(f"\nattendu publié ailleurs dans le dépôt : {att} µm\n")
    print(f"{'saut de rang':>14} {'paires':>8} {'écart médian':>14}")
    print("-" * 40)
    for k in ("1", "2", "3"):
        e = r["resume"][k]
        print(f"{k:>14} {e['paires']:>8} "
              f"{(e['mediane_um'] if e['mediane_um'] is not None else float('nan')):>13.1f} µm")
    print(f"\nl'écart croît avec le rang : {'OUI' if r['croit_avec_le_rang'] else 'NON'}")
    print(f"\n{'de':>4} {'vers':>5} {'médiane µm':>12} {'p10':>9} {'p90':>9}")
    print("-" * 44)
    for e in r["sauts"]["1"]:
        print(f"{e['de']:>4} {e['vers']:>5} {e['mediane_um']:>12.1f} "
              f"{e['p10_um']:>9.1f} {e['p90_um']:>9.1f}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
