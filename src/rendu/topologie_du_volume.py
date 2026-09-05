#!/usr/bin/env python3
"""Ce qu'un seuil fait vraiment d'un chunk de rouleau : combien de morceaux, et lequel gagne.

⚠⚠ POURQUOI CE FICHIER EXISTE. `composantes` était écrite **deux fois** — `sonde_maillage.py`
et `sonde_exterieur.py` — et les deux copies avaient **déjà divergé** : l'une rend trois
valeurs et garde le cas vide, l'autre en rend deux et ne le garde qu'à moitié. C'est le même
union-find, sur la même question, dans le même dossier. `faces` aussi.

⭐⭐ **Et la question qu'elles servent commande tout le reste** : une isosurface ne vaut que si
un seuil **sépare** les feuilles. Si tout seuil rend un seul bloc, mailler une isosurface
affirme une frontière que le scan n'a jamais résolue, et aucune surface tirée de là ne suit
une feuille — elle suit le bord d'une motte.

⚠⚠⚠ **LE CONTRÔLE NE PEUT PAS ÊTRE UN SEUIL CHOISI**, sinon on juge un seuil par un seuil.
Il est **dérivé de la géométrie** : un chunk de côté @f$c@f$ voxels de @f$v@f$ µm traverse

$$n = \\frac{c \\times v}{p}$$

feuilles quand le pas inter-feuilles vaut @f$p@f$. Des feuilles **séparées** donnent donc
@f$n@f$ morceaux dont le plus gros pèse environ @f$1/n@f$ de la matière. Mesuré sur
`PHerc0172` à 7,91 µm : @f$n \\approx 6{,}7@f$, donc **15 %** attendus — et le plus gros pèse
**93 à 100 %** à tous les seuils de 100 à 144.

⚠ La connexité est à **6 voisins**, pas 26. Deux feuilles qui se touchent par un coin sont
deux feuilles ; les unir par la diagonale ferait fondre l'empilement entier en un seul morceau
et rendrait le contrôle incapable d'échouer.

⚠ Les faces comptent les interfaces **plein/vide**, bords du chunk compris : c'est ce qu'un
mailleur émet réellement, pas le pire cas théorique. Oublier les bords sous-estime d'autant
qu'un chunk est petit.

Usage :
    uv run python src/rendu/topologie_du_volume.py --verifier
    uv run python src/rendu/topologie_du_volume.py \\
        --json docs/mesures/le_seuil_ne_separe_rien.json \\
        --coupe docs/mesures/coupes_du_seuil/coupe.npy
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]

BUCKET = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
VOLUME = "PHerc0172/volumes/20241024131838-7.910um-53keV-masked.zarr"
COTE = 128
VOXEL_UM = 7.910
PAS_UM = 142.8
"""Pas inter-feuilles de `PHerc0172`, mesuré (`docs/mesures/table_champ_0172.json`).

⚠ C'est le pas de CE rouleau et il n'est pas transportable : emprunter celui d'un autre est
le piège nº 6 du dépôt, et `12` l'a payé une fois."""

SEUILS = (100, 110, 120, 128, 136, 144)
"""Le balayage. ⚠ Il encadre le creux du milieu (115–130) et la matière (145–160) : un
balayage qui resterait d'un seul côté ne pourrait pas montrer que le verdict ne dépend pas
du seuil, ce qui est précisément ce qu'on veut établir."""


def faces(solide: np.ndarray) -> int:
    """
    @brief Les interfaces plein/vide d'un volume booléen, bords du volume compris.

    ⚠ Les bords comptent : un mailleur ferme la surface au bord du chunk. Les omettre
    sous-estime d'autant plus que le chunk est petit, donc fausserait toute extrapolation
    de coût.
    """
    n = 0
    for axe in range(3):
        a = np.moveaxis(solide, axe, 0)
        n += int(np.count_nonzero(a[:-1] != a[1:]))
        n += int(np.count_nonzero(a[0])) + int(np.count_nonzero(a[-1]))
    return n


def composantes(solide: np.ndarray, mini: int = 64) -> dict:
    """
    @brief Les morceaux de matière connexes à 6 voisins, et le poids du plus gros.

    ⚠ `mini` écarte le poivre : un morceau de quelques voxels est du bruit de seuil, pas une
    feuille. Il ne change PAS `plus_grosse`, qui est la grandeur qui décide.
    """
    plat = np.flatnonzero(solide.ravel())
    if plat.size == 0:
        return {"grandes": 0, "plus_grosse": 0, "total": 0, "part_de_la_plus_grosse": 0.0}
    idx = -np.ones(solide.shape, dtype=np.int32)
    idx.ravel()[plat] = np.arange(plat.size, dtype=np.int32)
    parent = np.arange(plat.size, dtype=np.int32)

    def trouver(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for axe in range(3):
        a = np.moveaxis(idx, axe, 0)
        bas, haut = a[:-1], a[1:]
        m = (bas >= 0) & (haut >= 0)
        for u, v in zip(bas[m], haut[m]):
            ra, rb = trouver(int(u)), trouver(int(v))
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    racines = np.array([trouver(i) for i in range(plat.size)], dtype=np.int32)
    _, tailles = np.unique(racines, return_counts=True)
    plus_grosse = int(tailles.max())
    return {"grandes": int((tailles >= mini).sum()), "plus_grosse": plus_grosse,
            "total": int(tailles.size),
            "part_de_la_plus_grosse": plus_grosse / float(plat.size)}


def feuilles_attendues(cote: int = COTE, voxel_um: float = VOXEL_UM,
                       pas_um: float = PAS_UM) -> float:
    """Combien de feuilles un chunk traverse — la géométrie, pas un réglage."""
    return cote * voxel_um / pas_um


def part_attendue_si_separees(**kw) -> float:
    """Ce que pèserait le plus gros morceau si les feuilles étaient séparées : environ 1/n.

    ⚠⚠ C'est le contrôle, et il est **dérivé** : juger un seuil par un autre seuil choisi à
    la main ne dirait rien. Une valeur mesurée près de 1 contre une attente près de 1/n est
    un écart qu'aucun réglage ne rattrape.
    """
    return 1.0 / max(feuilles_attendues(**kw), 1e-9)


def balayer(volume: np.ndarray, seuils=SEUILS, mini: int = 64) -> list[dict]:
    """Le même chunk, à chaque seuil : matière, faces, morceaux, poids du plus gros."""
    out = []
    for s in seuils:
        solide = volume > s
        c = composantes(solide, mini)
        out.append({"seuil": int(s), "part_matiere": float(solide.mean()),
                    "faces": faces(solide), **c})
    return out


def un_seuil_separe(balayage: list[dict], attendue: float) -> bool:
    """Un seuil rend-il des morceaux de la taille qu'aurait une feuille ?

    ⚠ La condition porte sur le plus gros morceau et sur la matière **ensemble** : un seuil
    si haut qu'il ne garde presque rien rendrait aussi de petits morceaux, et ce serait du
    bruit et non des feuilles. Sans le second membre, le contrôle serait satisfait par la
    panne qu'il doit exclure.
    """
    return any(l["part_de_la_plus_grosse"] <= 2.0 * attendue and l["part_matiere"] > 0.05
               for l in balayage)


def lire_chunk(niveau: int, z: int, y: int, x: int, timeout: float = 90.0):
    """Un chunk du volume publié, décodé. Rend `None` si le bucket ne l'a pas."""
    import numcodecs
    r = subprocess.run(["curl", "-s", "--fail", "--max-time", str(int(timeout)),
                        f"{BUCKET}/{VOLUME}/{niveau}/{z}/{y}/{x}"], capture_output=True)
    if r.returncode != 0:
        return None
    return np.frombuffer(numcodecs.Blosc().decode(r.stdout),
                         dtype=np.uint8).reshape(COTE, COTE, COTE)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- faces ---
    un = np.zeros((5, 5, 5), dtype=bool)
    un[2, 2, 2] = True
    v("un voxel isolé a six faces", faces(un) == 6, str(faces(un)))
    barre = np.zeros((5, 5, 5), dtype=bool)
    barre[2, 2, 2:4] = True
    v("deux voxels collés en ont dix, pas douze", faces(barre) == 10, str(faces(barre)))
    # ⚠⚠ Le cas qui exige le terme de BORD : un volume plein n'a aucune interface interne,
    # donc une version qui oublie les bords rendrait zéro — c'est-à-dire « rien à mailler »
    # pour le chunk le plus plein possible.
    plein = np.ones((4, 4, 4), dtype=bool)
    v("un volume plein a la surface de sa boîte, pas zéro", faces(plein) == 6 * 16,
      str(faces(plein)))
    v("un volume vide n'a aucune face", faces(np.zeros((4, 4, 4), dtype=bool)) == 0)

    # --- composantes ---
    deux = np.zeros((9, 9, 9), dtype=bool)
    deux[1:3, 1:3, 1:3] = True
    deux[6:8, 6:8, 6:8] = True
    c = composantes(deux, mini=1)
    v("deux blocs disjoints font deux morceaux", c["total"] == 2, str(c))
    colles = np.zeros((9, 9, 9), dtype=bool)
    colles[1:3, 1:3, 1:5] = True
    v("... et deux blocs qui se touchent par une FACE n'en font qu'un",
      composantes(colles, mini=1)["total"] == 1)
    # ⚠⚠ LA CONNEXITÉ EST À 6 VOISINS. En 26-connexité deux feuilles qui se frôlent par un
    # coin fondraient en une, et le contrôle « un seuil sépare-t-il ? » deviendrait incapable
    # d'échouer : tout empilement serait toujours un seul morceau.
    coin = np.zeros((9, 9, 9), dtype=bool)
    coin[2, 2, 2] = True
    coin[3, 3, 3] = True
    v("... et deux voxels qui ne se touchent QUE par un coin restent deux",
      composantes(coin, mini=1)["total"] == 2)
    v("un volume vide rend zéro morceau et ne lève pas",
      composantes(np.zeros((4, 4, 4), dtype=bool))["total"] == 0)
    # ⚠ `mini` écarte le poivre sans toucher au poids du plus gros, qui est la grandeur
    # qui décide : les confondre ferait bouger le verdict avec un réglage de propreté.
    poivre = np.zeros((9, 9, 9), dtype=bool)
    poivre[1:5, 1:5, 1:5] = True
    poivre[8, 8, 8] = True
    cp = composantes(poivre, mini=64)
    v("mini écarte le poivre du compte des grandes",
      cp["grandes"] == 1 and cp["total"] == 2, str(cp))
    v("... sans changer le poids du plus gros",
      abs(cp["part_de_la_plus_grosse"] - 64 / 65) < 1e-9, str(cp))

    # --- l'attente, dérivée ---
    v("un chunk de 128 voxels de 7,91 µm traverse environ 6,7 feuilles à 142,8 µm",
      abs(feuilles_attendues() - 7.09) < 0.5, f"{feuilles_attendues():.2f}")
    v("... donc des feuilles séparées mettraient ~14 % dans le plus gros",
      0.10 < part_attendue_si_separees() < 0.20, f"{part_attendue_si_separees():.3f}")
    # ⭐ L'attente doit SUIVRE la géométrie : un pas deux fois plus serré double le compte.
    v("... et l'attente suit le pas, elle n'est pas écrite en dur",
      abs(feuilles_attendues(pas_um=PAS_UM / 2) - 2 * feuilles_attendues()) < 1e-9)

    # --- le verdict, dans les DEUX sens ---
    empile = np.zeros((64, 16, 16), dtype=np.uint8)
    for k in range(0, 64, 9):           # des feuilles réellement séparées
        empile[k:k + 2] = 200
    sep = balayer(empile, seuils=(100,), mini=1)
    v("un empilement RÉELLEMENT séparé est reconnu comme tel",
      un_seuil_separe(sep, part_attendue_si_separees()), str(sep))
    motte = np.full((64, 16, 16), 200, dtype=np.uint8)
    v("... et une motte pleine ne l'est pas",
      not un_seuil_separe(balayer(motte, seuils=(100,), mini=1),
                          part_attendue_si_separees()))
    # ⚠⚠ Le second membre de la condition : un seuil si haut qu'il ne garde presque rien
    # rend de petits morceaux, et ce serait du bruit pris pour des feuilles.
    poussiere = np.zeros((64, 16, 16), dtype=np.uint8)
    for k in range(0, 64, 3):
        poussiere[k, 0, 0] = 200          # 22 grains isolés : plus gros morceau = 1/22
    bal_p = balayer(poussiere, seuils=(100,), mini=1)
    v("... et du poivre éparpillé non plus, malgré des morceaux de la bonne TAILLE",
      not un_seuil_separe(bal_p, part_attendue_si_separees()),
      f"plus gros {bal_p[0]['part_de_la_plus_grosse']:.3f}, "
      f"matiere {bal_p[0]['part_matiere']:.5f}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--chunk", type=int, nargs=3, metavar=("Z", "Y", "X"), action="append",
                   help="clé d'un chunk au NIVEAU 0, à répéter "
                        "(défaut : le centre PUIS le bord de PHerc0172)")
    p.add_argument("--niveau", type=int, default=0)
    p.add_argument("--json", type=Path)
    p.add_argument("--coupe", type=Path,
                   help="écrit la coupe xy médiane de CHAQUE chunk, en .npy uint8 — 16 Ko "
                        "par région, ce qui rend la figure reproductible HORS LIGNE")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()

    chunks = a.chunk or [[82, 25, 33], [82, 25, 53]]
    attendue = part_attendue_si_separees()
    regions = []
    for cle in chunks:
        vol = lire_chunk(a.niveau, *cle)
        if vol is None:
            raise SystemExit(f"chunk absent du bucket : niveau {a.niveau} {cle}")
        bal = balayer(vol)
        nz = vol[vol > 0]
        if a.coupe:
            # ⚠ La coupe est écrite en uint8 BRUT, sans seuil ni normalisation : c'est le
            # volume tel que le scan le donne. Une coupe déjà binarisée n'illustrerait plus
            # le balayage, elle en illustrerait un seul point.
            a.coupe.parent.mkdir(parents=True, exist_ok=True)
            chemin = a.coupe.with_name(
                f"{a.coupe.stem}_{cle[0]}_{cle[1]}_{cle[2]}{a.coupe.suffix or '.npy'}")
            np.save(chemin, vol[COTE // 2])
            print(f"coupe écrite : {chemin}")
        regions.append({"chunk": cle,
                        "rayon_vox": abs(cle[2] * COTE - 4288),
                        "moyenne": float(nz.mean()) if nz.size else 0.0,
                        "ecart_type": float(nz.std()) if nz.size else 0.0,
                        "balayage": bal,
                        "un_seuil_separe": un_seuil_separe(bal, attendue)})
    r = {"volume": VOLUME, "niveau": a.niveau, "cote": COTE,
         "voxel_um": VOXEL_UM, "pas_um": PAS_UM,
         "feuilles_traversees": round(feuilles_attendues(), 2),
         "part_attendue_si_separees": round(attendue, 4),
         "regions": regions,
         "un_seuil_separe_quelque_part": any(x["un_seuil_separe"] for x in regions)}
    for reg in regions:
        print(f"\nchunk {reg['chunk']} — rayon {reg['rayon_vox']} vox "
              f"({reg['rayon_vox'] * VOXEL_UM / 1000:.1f} mm), moyenne {reg['moyenne']:.1f}, "
              f"ecart-type {reg['ecart_type']:.1f}")
        print(f"  {'seuil':>5} {'matiere':>8} {'faces':>9} {'morceaux':>9} {'plus grosse':>12}")
        print("  " + "-" * 48)
        for l in reg["balayage"]:
            print(f"  {l['seuil']:>5} {l['part_matiere'] * 100:7.1f}% {l['faces']:9d} "
                  f"{l['grandes']:9d} {l['part_de_la_plus_grosse'] * 100:11.1f}%")
    print(f"\nattendu si les feuilles étaient séparées : {attendue * 100:.1f} % "
          f"({feuilles_attendues():.1f} feuilles traversées)")
    print("un seuil sépare les feuilles quelque part : "
          + ("OUI" if r["un_seuil_separe_quelque_part"] else "NON"))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
