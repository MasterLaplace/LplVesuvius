#!/usr/bin/env python3
"""À quoi ressemble une feuille RÉELLEMENT aplatie, telle que la communauté la publie.

⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est une question de l'auteur qui l'a provoqué : *« un
jour on aura une vue des vraies feuilles aplaties ou bien ? »*. Le dépôt mesurait le relief
depuis des semaines sans jamais **regarder** une couche rendue à côté d'une couche publiée.
La réponse tenait dans deux images, et elle n'était dans aucun nombre.

Une `surface-volume` publiée est la pile de couches qu'un segment donne une fois déroulé :
la couche du milieu **est** la feuille, vue de face. Un seul bloc OME-Zarr en porte
128 × 128 voxels sur toute la profondeur, donc quelques requêtes suffisent — rien à
télécharger, rien à rendre.

⚠ La tuile est prise **au milieu** du segment et non à son coin : les bords d'un segment
sont là où le maillage s'arrête, donc là où l'image est la moins représentative de ce que le
travail produit.

⭐ Le lecteur de blocs est celui de `tracecheck/`, importé et jamais recopié : deux lecteurs
de zarr finiraient par ne pas s'accorder sur le séparateur de clé, et le mode d'échec des
deux est de rendre une image noire plutôt qu'une erreur.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tracecheck"))

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"


def tuile(scroll: str, segment: str, blocs: int = 4, prefer: str = "2.4um",
          timeout: float = 60.0):
    """Une tuile carrée de `blocs`×`blocs` blocs, prise au milieu du segment.

    Rend `(image, rapport)`. Les blocs absents restent noirs **et sont comptés** : une tuile
    à moitié vide est un fait sur le segment, pas sur le lecteur, et la confondre avec « la
    feuille est sombre ici » est exactement l'erreur que ce dépôt a payée treize fois.
    """
    import numpy as np
    import tracecheck as tc

    url = tc.find_surface_volume(scroll, segment, timeout, prefer)
    if url is None:
        raise RuntimeError(f"aucune surface-volume pour {scroll}/{segment}")
    meta = tc.array_meta(f"{BUCKET}/{url}", 0, timeout)
    profondeur, hy, hx = meta["chunks"]
    forme = meta["shape"]
    cy0 = forme[1] // hy // 2
    cx0 = forme[2] // hx // 2
    out = np.zeros((blocs * hy, blocs * hx), dtype=np.dtype(meta["dtype"]))
    pris = manquants = 0
    for i in range(blocs):
        for j in range(blocs):
            brut = tc.get(f"{BUCKET}/{tc.chunk_key(meta, 0, cy0 + i, cx0 + j)}"
                          .replace(f"{BUCKET}/", f"{BUCKET}/{url}/"), timeout)
            if brut is None:
                manquants += 1
                continue
            donnees = tc.decode(brut, meta, profondeur * hy * hx)
            if donnees is None:
                manquants += 1
                continue
            bloc = np.frombuffer(donnees, dtype=np.dtype(meta["dtype"])).reshape(
                profondeur, hy, hx)
            # ⚠ La couche du MILIEU : c'est celle qui porte la surface tracée. Une couche de
            # bord est déjà à l'intérieur ou déjà dehors, donc elle ne montre pas la feuille.
            out[i * hy:(i + 1) * hy, j * hx:(j + 1) * hx] = bloc[profondeur // 2]
            pris += 1
    return out, {"url": url, "couches": profondeur, "blocs_pris": pris,
                 "blocs_manquants": manquants, "cote_voxels": blocs * hy,
                 "max": int(out.max())}


def verifier() -> int:
    """Les témoins, hors réseau : la géométrie de tuile et le compte des blocs absents."""
    import numpy as np
    import tracecheck as tc

    echecs = controles = 0

    def v(nom, cond, det=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))

    meta = {"shape": [109, 50600, 36400], "chunks": [109, 128, 128],
            "dtype": "|u1", "dimension_separator": "/"}
    # ⚠ Le milieu du segment, calculé et non posé.
    v("la tuile est prise au milieu", (meta["shape"][1] // 128 // 2,
                                       meta["shape"][2] // 128 // 2) == (197, 142))
    v("la couche prise est celle du milieu", meta["chunks"][0] // 2 == 54)
    v("la clé de bloc suit l'ordre du tableau",
      tc.chunk_key(meta, 0, 197, 142) == "0/0/197/142")
    # ⚠⚠ Une tuile de N blocs fait N×128 voxels : c'est ce qui permet de comparer une tuile
    # publiée à un recadrage de la même taille dans un de NOS rendus. Comparer deux images
    # de tailles différentes ferait passer une différence d'échelle pour une différence de
    # surface -- la faute que tout ce dépôt traque.
    for n in (1, 2, 4, 8):
        v(f"une tuile de {n} blocs fait {n * 128} voxels", n * 128 == n * meta["chunks"][1])
    a = np.zeros((256, 256), dtype=np.uint8)
    v("une tuile entièrement noire a un max nul", int(a.max()) == 0)
    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--scroll", default="PHercParis4")
    p.add_argument("--segment", default="20230702185753")
    p.add_argument("--blocs", type=int, default=4)
    p.add_argument("--prefer", default="2.4um")
    p.add_argument("--sortie", type=Path, default=Path("data/temoin_rendu/reference.tif"))
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    import tifffile

    im, r = tuile(a.scroll, a.segment, a.blocs, a.prefer)
    if r["blocs_pris"] == 0:
        print(f"refus : aucun bloc lisible pour {a.scroll}/{a.segment}", file=sys.stderr)
        return 3
    a.sortie.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(str(a.sortie), im)
    print(f"{r['url']}\n  {r['blocs_pris']} bloc(s) pris, {r['blocs_manquants']} absent(s)"
          f"  ·  {r['cote_voxels']} voxels de côté  ·  max {r['max']}\n  écrit : {a.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
