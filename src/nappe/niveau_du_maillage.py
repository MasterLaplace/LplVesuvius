#!/usr/bin/env python3
"""À quel niveau de pyramide les coordonnées d'un maillage sont-elles écrites ?

⚠⚠ POURQUOI CE FICHIER EXISTE, et ce qu'il a coûté. Un `tifxyz` porte des **indices de
voxel**, et un indice ne veut rien dire sans le volume qui le numérote. Le même point de la
même feuille s'écrit `[2924, 5324, 9260]` au niveau 2 et `[11696, 21296, 37040]` au niveau 0.
Rien dans `meta.json` ne dit lequel : ni le format, ni `scale` (qui est le pas de la grille
dans le PLAN, pas la résolution du volume), ni le fichier de paramètres du traceur, qui
enregistre `voxelsize: 2.4` dans les deux cas.

Le prix : cinq traces `m7` ont été tracées dans le volume au niveau 2 puis **rendues contre
le volume au niveau 0**. Le moteur a échantillonné consciencieusement des coordonnées situées
au quart de leur vraie position, c'est-à-dire dans le vide, et a produit 161 images
**entièrement noires**. Lues par un instrument dont le seuil de matière était relatif au
maximum de la pile, ces images ont donné « relief 0,0000, platitude réelle » — et ce chiffre
a été publié comme une propriété des traces.

⭐ Le fait qui rend la détection possible : le traceur ET le moteur de rendu impriment tous
deux la forme du tableau zarr qu'ils ouvrent. Le rapport des deux formes EST le facteur, et
c'est une puissance de deux ou ce n'est pas une pyramide.

    traceur : zarr dataset size for scale group 0 [18946, 8174, 8174]
    rendu   : zarr dataset size for group 0       [75784 32693 32693]
    rapport : 4,000  4,000  4,000   ⇒  le maillage est au niveau 2 du volume rendu

⚠ Le rapport est vérifié sur les TROIS axes. Un volume peut être anisotrope, et un facteur
lu sur un seul axe passerait sans rien dire sur un recadrage qui n'est pas une pyramide.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

# ⚠ Les deux moteurs n'écrivent pas la même phrase, et la virgule non plus : le traceur
# sépare par des virgules, le rendu par des espaces. Un seul motif pour les deux serait un
# motif qui rate l'un des deux en silence.
FORME = re.compile(r"zarr dataset size for (?:scale )?group\s+\d+\s*\[([0-9,\s]+)\]")


def forme_du_log(texte: str) -> tuple[int, ...] | None:
    """La forme du tableau zarr annoncée par un journal, ou None.

    ⚠ On prend la PREMIÈRE annonce : un journal qui en contient plusieurs a ouvert plusieurs
    volumes, et deviner lequel a servi serait exactement l'erreur que ce fichier existe pour
    empêcher.
    """
    m = FORME.search(texte)
    if not m:
        return None
    return tuple(int(v) for v in re.split(r"[,\s]+", m.group(1).strip()) if v)


def niveau_entre(forme_maillage: tuple[int, ...],
                 forme_rendu: tuple[int, ...]) -> tuple[int | None, list[float]]:
    """Le niveau de pyramide séparant deux formes, et les rapports mesurés.

    Rend `(None, rapports)` quand ce n'est pas une pyramide : rapports différents d'un axe à
    l'autre, ou rapport qui n'est pas une puissance de deux.

    ⚠⚠ Le refus est aussi important que la réponse. Rendre « niveau 2 » sur des rapports
    (4, 4, 3,7) laisserait corriger un maillage par une mise à l'échelle qui ne le remettrait
    pas en place, et le résultat ressemblerait à une surface un peu de travers.
    """
    if len(forme_maillage) != len(forme_rendu) or not forme_maillage:
        return None, []
    rapports = [b / a if a else math.inf for a, b in zip(forme_maillage, forme_rendu)]
    if any(not math.isfinite(r) or r <= 0 for r in rapports):
        return None, rapports
    # ⚠ Tolérance de 1 % : une pyramide arrondit à l'entier supérieur à chaque niveau, donc
    # 75784/18946 tombe pile ici mais un autre volume peut donner 4,0002.
    if max(rapports) - min(rapports) > 0.01 * max(rapports):
        return None, rapports
    r = sum(rapports) / len(rapports)
    n = round(math.log2(r))
    if n < 0 or abs(2.0 ** n - r) > 0.01 * r:
        return None, rapports
    return n, rapports


def rebaser(source: Path, dest: Path, facteur: float) -> dict:
    """Réécrire un `tifxyz` avec ses coordonnées multipliées par `facteur`.

    ⚠⚠ Cela ne CRÉE aucun détail. Un maillage tracé au niveau 2 reste une description
    grossière de la feuille ; le remettre à l'échelle le place au bon endroit dans le volume
    fin, rien de plus. Ce qu'on mesurera ensuite est le relief de CETTE surface-là, ce qui
    est précisément la question.

    ⚠ Les points invalides restent invalides : multiplier −1 par 4 donnerait −4, qui n'est
    plus la sentinelle que tout le monde reconnaît.
    """
    import numpy as np
    import tifffile

    meta = json.loads((source / "meta.json").read_text(encoding="utf-8"))
    dest.mkdir(parents=True, exist_ok=True)
    bas = [math.inf] * 3
    haut = [-math.inf] * 3
    for i, nom in enumerate(("x", "y", "z")):
        a = tifffile.imread(str(source / f"{nom}.tif"))
        bon = a > 0
        b = a.copy()
        b[bon] = a[bon] * facteur
        tifffile.imwrite(str(dest / f"{nom}.tif"), b)
        if bon.any():
            bas[i] = float(b[bon].min())
            haut[i] = float(b[bon].max())
    sortie = dict(meta)
    # ⚠⚠ `scale` DOIT etre divise par le facteur, et l'oublier est un bug silencieux.
    # `scale` vaut « points de grille par voxel » : apres avoir multiplie les coordonnees
    # par 4, la MEME grille couvre quatre fois plus de voxels, donc sa densite en points par
    # voxel est divisee par 4. Le laisser tel quel fait croire au moteur de rendu que la
    # grille est quatre fois plus dense qu'elle ne l'est, et la sortie tombe a un seizieme
    # de sa taille. Mesure : le premier rebasage a rendu 591 x 586 px la ou il en fallait
    # 2400, et rien dans la sortie ne le disait -- l'image etait juste petite.
    ancienne = meta.get("scale", [0.05, 0.05])
    sortie["scale"] = [float(v) / facteur for v in ancienne]
    sortie["bbox"] = [bas, haut]
    sortie["uuid"] = dest.name
    sortie["rebase_facteur"] = facteur
    sortie["rebase_de"] = meta.get("uuid", "?")
    sortie.pop("area_vx2", None)  # ⚠ une aire en voxels change avec le facteur : la garder mentirait
    (dest / "meta.json").write_text(json.dumps(sortie, indent=4), encoding="utf-8")
    return sortie


def verifier() -> int:
    """Les témoins, avec le cas négatif de chaque refus."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {detail}" if detail else ""))

    # Les deux phrases réellement imprimées, virgules comprises.
    trace = "zarr dataset size for scale group 0 [18946, 8174, 8174]\nchunk shape [192,192,192]"
    rendu = "zarr dataset size for group 0 [75784 32693 32693 ]\nSource dtype: uint8"
    v("la phrase du traceur est lue", forme_du_log(trace) == (18946, 8174, 8174))
    v("... et celle du rendu aussi", forme_du_log(rendu) == (75784, 32693, 32693))
    v("un journal sans la phrase rend None", forme_du_log("rien ici") is None)

    n, r = niveau_entre((18946, 8174, 8174), (75784, 32693, 32693))
    v("le cas réel donne le niveau 2", n == 2, f"{n}, rapports {r}")
    v("... et les trois rapports valent 4", all(abs(x - 4.0) < 0.01 for x in r), str(r))

    v("deux formes identiques donnent le niveau 0",
      niveau_entre((100, 50, 50), (100, 50, 50))[0] == 0)
    v("un facteur 2 donne le niveau 1",
      niveau_entre((50, 25, 25), (100, 50, 50))[0] == 1)

    # ⚠⚠ LES REFUS, sans lesquels l'outil corrigerait un maillage vers une position fausse.
    v("un rapport anisotrope est refusé",
      niveau_entre((50, 25, 25), (100, 50, 60))[0] is None)
    v("un facteur qui n'est pas une puissance de deux est refusé",
      niveau_entre((50, 25, 25), (150, 75, 75))[0] is None)
    v("un maillage PLUS GRAND que le volume est refusé",
      niveau_entre((100, 50, 50), (50, 25, 25))[0] is None)
    v("une forme vide est refusée", niveau_entre((), ())[0] is None)
    v("des dimensions dépareillées sont refusées",
      niveau_entre((50, 25), (100, 50, 50))[0] is None)
    # ⚠ Une tolérance existe, mais elle est étroite : 4,05 n'est pas 4.
    v("un rapport à 1 % passe", niveau_entre((1000, 1000, 1000), (4000, 4002, 3998))[0] == 2)
    v("... mais pas à 5 %", niveau_entre((1000, 1000, 1000), (4000, 4200, 3800))[0] is None)

    # ⚠⚠ Le rebasage sur une vraie paire de fichiers : ce qui compte est que `scale` SUIVE.
    import shutil
    import tempfile

    import numpy as np
    import tifffile

    racine = Path(tempfile.mkdtemp(prefix="niveau_temoins_"))
    src = racine / "src"
    src.mkdir()
    g = np.zeros((6, 5), dtype=np.float32)
    for r in range(6):
        for c in range(5):
            g[r, c] = 100.0 + r * 10 + c
    g[2, 2] = -1.0  # un trou
    for nom in ("x", "y", "z"):
        tifffile.imwrite(str(src / f"{nom}.tif"), g)
    (src / "meta.json").write_text(json.dumps(
        {"format": "tifxyz", "scale": [0.05, 0.05], "uuid": "src",
         "area_vx2": 123.0, "bbox": [[0, 0, 0], [1, 1, 1]]}), encoding="utf-8")

    m = rebaser(src, racine / "dst", 4.0)
    v("le rebasage divise scale par le facteur",
      abs(m["scale"][0] - 0.0125) < 1e-9, str(m["scale"]))
    v("... sur les deux axes", m["scale"][0] == m["scale"][1])
    # ⚠ L'attendu est CALCULE depuis la fixture et non tape a la main : ma premiere version
    # disait 4 x 151 en visant le mauvais coin de la grille, et c'est l'assertion qui avait
    # tort. Un attendu ecrit a la main est une seconde implementation, et elle peut etre la
    # fausse des deux.
    attendu = 4.0 * float(g[g > 0].max())
    v("... et multiplie la bbox", abs(m["bbox"][1][0] - attendu) < 1e-3,
      f'{m["bbox"][1][0]} contre {attendu}')
    v("... et jette l'aire en voxels", "area_vx2" not in m)
    v("... et note le facteur", m["rebase_facteur"] == 4.0)
    relu = tifffile.imread(str(racine / "dst" / "x.tif"))
    v("un trou reste un trou", float(relu[2, 2]) == -1.0, str(relu[2, 2]))
    v("... et un point valide est multiplie", float(relu[0, 0]) == 400.0, str(relu[0, 0]))
    shutil.rmtree(racine, ignore_errors=True)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--trace-log", type=Path, help="journal du traceur")
    p.add_argument("--rendu-log", type=Path, help="journal du rendu")
    p.add_argument("--maillage", type=Path, help="tifxyz à rebaser")
    p.add_argument("--rebaser", type=Path, help="où écrire le tifxyz rebasé")
    p.add_argument("--facteur", type=float, help="facteur imposé, sinon déduit des journaux")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    facteur, niveau, rapports = a.facteur, None, []
    if a.trace_log and a.rendu_log:
        fa = forme_du_log(a.trace_log.read_text(errors="replace"))
        fb = forme_du_log(a.rendu_log.read_text(errors="replace"))
        if fa is None or fb is None:
            print("refus : au moins un journal n'annonce pas de forme zarr", file=sys.stderr)
            return 2
        niveau, rapports = niveau_entre(fa, fb)
        print(f"traceur {fa}\nrendu   {fb}\nrapports " +
              "  ".join(f"{x:.4f}" for x in rapports))
        if niveau is None:
            print("refus : ce n'est pas un rapport de pyramide — ne pas rebaser",
                  file=sys.stderr)
            return 3
        print(f"⇒ le maillage est au niveau {niveau} du volume rendu"
              + ("  ✅ même frame" if niveau == 0 else
                 f"  ⚠⚠ RENDU DANS LE VIDE si on le rend au niveau 0 : facteur {2 ** niveau}"))
        if facteur is None:
            facteur = float(2 ** niveau)

    if a.rebaser:
        if not a.maillage or facteur is None:
            p.error("--rebaser exige --maillage et un facteur (imposé ou déduit)")
        m = rebaser(a.maillage, a.rebaser, facteur)
        print(f"rebasé ×{facteur:g} → {a.rebaser}\n  bbox {m['bbox']}")

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(
            {"niveau": niveau, "rapports": rapports, "facteur": facteur}, indent=2),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
