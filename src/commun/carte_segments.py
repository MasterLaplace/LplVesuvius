#!/usr/bin/env python3
"""Quels segments officiels d'un rouleau se RECOUVRENT ? -- lu dans leurs metas, sans rendu.

⚠⚠ POURQUOI. `44` ferme la piste de l'extension tangentielle : elle triple une nappe une fois,
puis le cycle rogner-etendre converge vers un point fixe autour de 6 cm2. La voie qui reste
nommee est de RACCORDER plusieurs segments — `vc_merge_tifxyz` sait le faire (recouvrement par
index de patchs, RANSAC, ajustement de faisceau conjoint, fusion EDT a N voies) mais il exige
des surfaces QUI SE RECOUVRENT.

⭐ Or le depot public de `PHerc1447` en publie QUINZE, et ce depot n'en a jamais utilise qu'un.
La question qui decide — se recouvrent-ils ? — se lit dans leurs `meta.json`, quelques kilo-
octets, sans telecharger un seul maillage ni payer un seul rendu.

⚠ Le meta utile n'est PAS a la racine du segment (elle est depouillee) mais dans
`mesh/intermediate/tifxyz_original/meta.json` — releve dans `43`, ou il porte aussi la graine,
le mode et les parametres du run qui a produit le segment.

⚠⚠ CE QUE LE RECOUVREMENT DE BOITES NE DIT PAS. Deux boites qui se croisent ne veulent pas dire
deux patchs de la MEME feuille : dans un rouleau, deux nappes voisines sont a 113 µm l'une de
l'autre et leurs boites se recouvrent presque entierement. Le recouvrement de boites est donc
un FILTRE — il elimine les paires qui ne peuvent pas se raccorder — jamais une preuve qu'une
paire le peut. C'est exactement pour ça qu'il est bon marche.

Usage :
    uv run python src/commun/carte_segments.py --rouleau PHerc1447 --json docs/segments.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

BASE = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
META = "mesh/intermediate/tifxyz_original/meta.json"

# ⚠⚠ Les deux seuils qui donnent son verdict a cet outil, nommes ici parce qu'ils sont
# lus DEUX fois : par l'affichage ci-dessous, et par `verifier_chiffres.py`, qui recompte
# les paires depuis le JSON pour garantir que la prose ne derive pas. Deux ecritures d'un
# meme seuil finiraient par ne pas s'accorder, et le desaccord porterait sur la phrase
# « aucun des quinze segments n'est un patch de la meme feuille » -- la conclusion entiere.
MEME_FEUILLE_UM = 40.0   # deux patchs d'une meme nappe : raccordables
VOISINES_UM = 250.0      # deux nappes distinctes mais adjacentes : a ne surtout pas fusionner


def lister(rouleau: str, delai: int = 30) -> list[str]:
    """Les noms de segments publies, lus dans le listing S3."""
    url = f"{BASE}/?list-type=2&prefix={rouleau}/segments/&delimiter=/"
    r = subprocess.run(["curl", "-s", "--max-time", str(delai), url],
                       capture_output=True, text=True)
    noms = [p.removeprefix(f"{rouleau}/segments/").rstrip("/")
            for p in re.findall(r"<Prefix>([^<]+)</Prefix>", r.stdout)]
    return [n for n in noms if n and n != "raw"]


def meta_de(rouleau: str, segment: str, delai: int = 30) -> dict | None:
    url = f"{BASE}/{rouleau}/segments/{segment}/{META}"
    r = subprocess.run(["curl", "-s", "--max-time", str(delai), url],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) and "bbox" in d else None


def recouvrement(a: list, b: list) -> tuple[float, list[float]]:
    """Volume d'intersection de deux boites, et sa fraction de la plus PETITE des deux.

    ⚠ Rapporte a la plus petite et non a l'union : deux patchs de tailles tres differentes
    peuvent se raccorder si le petit est entierement dans le grand, et une fraction d'union
    dirait alors « presque rien ne se recouvre ».
    """
    lo = [max(a[0][i], b[0][i]) for i in range(3)]
    hi = [min(a[1][i], b[1][i]) for i in range(3)]
    dims = [max(0.0, hi[i] - lo[i]) for i in range(3)]
    inter = dims[0] * dims[1] * dims[2]
    va = max(1e-9, (a[1][0] - a[0][0]) * (a[1][1] - a[0][1]) * (a[1][2] - a[0][2]))
    vb = max(1e-9, (b[1][0] - b[0][0]) * (b[1][1] - b[0][1]) * (b[1][2] - b[0][2]))
    return inter / min(va, vb), dims


def telecharger(rouleau: str, segment: str, dest: Path, delai: int = 120) -> Path | None:
    """Rapatrier les trois canaux d'un segment. Les maillages font ~0,1 Mo par canal.

    ⚠ On ne prend QUE x/y/z et le meta : le reste d'un segment publie (rendus, masques) pese
    des ordres de grandeur de plus et ne sert a rien pour mesurer un ecart entre surfaces.
    """
    dest.mkdir(parents=True, exist_ok=True)
    base = f"{BASE}/{rouleau}/segments/{segment}/mesh/intermediate/tifxyz_original"
    for f in ("x.tif", "y.tif", "z.tif", "meta.json"):
        cible = dest / f
        if cible.exists() and cible.stat().st_size > 0:
            continue
        r = subprocess.run(["curl", "-s", "-f", "--max-time", str(delai),
                            "-o", str(cible), f"{base}/{f}"], capture_output=True)
        if r.returncode != 0:
            return None
    return dest if (dest / "z.tif").is_file() else None


def ecart_entre(a: Path, b: Path,
                voxel_um: float = 8.64) -> tuple[float | None, str]:
    """Distance MEDIANE d'un point de `b` au plus proche point de `a`, en µm, ET pourquoi.

    ⚠⚠ **Rend une raison, parce qu'un `None` nu confondait TROIS faits differents** :
    un maillage illisible, un patch trop maigre pour qu'une mediane veuille dire quelque
    chose, et — le cas qui compte — *aucun point de `b` a moins de la marge de `a`*. Le
    dernier n'est pas une mesure manquante : c'est la mesure « ces deux nappes sont loin ».
    Les compter comme « inconnues » affaiblirait a tort la conclusion, les compter comme
    « eloignees » sans le dire la renforcerait a tort. Trouve en recomptant les bandes
    depuis le JSON : le document publiait 49 paires eloignees la ou 45 avaient ete
    mesurees, les 4 autres etant hors de portee — donc eloignees, mais pour une raison
    que le tableau ne disait pas.

    ⭐⭐ C'est le discriminant que le recouvrement de boites ne peut pas donner. Deux patchs de
    la MEME feuille qui se recouvrent ont un ecart proche de zero dans leur zone commune ;
    deux nappes VOISINES ont un ecart de l'ordre de l'espacement entre feuilles, mesure a
    113 µm sur ce rouleau (`44` §4). Les boites, elles, se recouvrent a 90-100 % dans les deux
    cas — c'est pourquoi il faut descendre aux points.

    ⚠ Mediane sur les points de `b` QUI TOMBENT dans la boite de `a`, pas sur tous : un patch
    qui deborde largement tirerait la mediane vers sa partie non commune, et deux patchs
    voisins mais decales passeraient pour eloignes.
    """
    import numpy as np
    from scipy.spatial import cKDTree
    import geometrie_chaine as g

    pa, pb = g.lire_tifxyz(a), g.lire_tifxyz(b)
    if pa is None or pb is None:
        return None, "illisible"
    pa = pa.reshape(-1, 3)[~np.isnan(g.lire_tifxyz(a).reshape(-1, 3)[:, 0])]
    pb = pb.reshape(-1, 3)
    pb = pb[~np.isnan(pb[:, 0])]
    if len(pa) < 10 or len(pb) < 10:
        return None, "trop_maigre"
    # ⚠⚠ La boite est ELARGIE d'une marge, et le temoin a montre pourquoi : une nappe est
    # plate, donc sa boite peut avoir une epaisseur quasi nulle dans une direction — et une
    # nappe VOISINE, celle qu'on veut justement mesurer a 113 µm, tombe alors entierement
    # dehors et le filtre la jette. Sans marge, le discriminant ne peut rendre que « meme
    # feuille » ou « rien ».
    # 50 voxels = 432 µm : grand devant l'espacement entre feuilles (113 µm), petit devant
    # l'etendue d'un patch (des milliers de voxels), donc le filtre garde son role lateral.
    MARGE = 50.0
    lo, hi = pa.min(axis=0) - MARGE, pa.max(axis=0) + MARGE
    dedans = np.all((pb >= lo) & (pb <= hi), axis=1)
    if dedans.sum() < 10:
        return None, "hors_portee"
    d, _ = cKDTree(pa).query(pb[dedans], k=1)
    return float(np.median(d) * voxel_um), "mesure"


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    A = [[0, 0, 0], [10, 10, 10]]
    v("deux boîtes identiques se recouvrent entièrement",
      abs(recouvrement(A, A)[0] - 1.0) < 1e-9)
    v("deux boîtes disjointes ne se recouvrent pas",
      recouvrement(A, [[20, 20, 20], [30, 30, 30]])[0] == 0.0)
    v("le contact par une face n'est pas un recouvrement",
      recouvrement(A, [[10, 0, 0], [20, 10, 10]])[0] == 0.0)
    # ⭐ Rapporte a la PLUS PETITE : une petite boite incluse dans une grande se recouvre a 100 %.
    petite = [[1, 1, 1], [2, 2, 2]]
    v("une petite boîte incluse dans une grande se recouvre à 100 %",
      abs(recouvrement(A, petite)[0] - 1.0) < 1e-9, f"{recouvrement(A, petite)[0]:.3f}")
    # ⚠ Sonde : rapporte a l'UNION, ce cas donnerait 0,001 et serait lu comme « rien ».
    v("... ce qu'une fraction d'union nierait", recouvrement(A, petite)[0] > 0.5)
    v("le recouvrement est symétrique",
      abs(recouvrement(A, petite)[0] - recouvrement(petite, A)[0]) < 1e-12)
    # ⭐ Le discriminant lui-meme, sur des nuages synthetiques.
    import numpy as np
    import tempfile
    import tifffile
    with tempfile.TemporaryDirectory() as t:
        def ecrire(nom, dz):
            d = Path(t) / nom
            d.mkdir()
            gx, gy = np.meshgrid(np.arange(40.0), np.arange(30.0))
            for c, arr in (("x", 3000 + gx * 20), ("y", 2500 + gy * 20),
                           ("z", np.full_like(gx, 12000.0 + dz))):
                tifffile.imwrite(d / f"{c}.tif", arr.astype(np.float32))
            return d
        m0, m1, m2 = ecrire("a", 0.0), ecrire("b", 0.0), ecrire("c", 13.1)
        e_meme, r_meme = ecart_entre(m0, m1)
        e_voisin, r_voisin = ecart_entre(m0, m2)
        v("une mesure reussie se declare comme telle",
          r_meme == "mesure" and r_voisin == "mesure", f"{r_meme}/{r_voisin}")
        # ⭐⭐ La sonde qui rend la raison utile : une nappe posee LOIN doit sortir
        # « hors_portee » et non « illisible ». Sans cette separation, une paire eloignee
        # et un fichier casse etaient le meme `None`, et le tableau publie a effectivement
        # compte les quatre paires hors de portee dans une bande mesuree.
        m3 = ecrire("d", 500.0)
        e_loin, r_loin = ecart_entre(m0, m3)
        v("une nappe hors de portee est nommee, pas confondue avec un fichier casse",
          e_loin is None and r_loin == "hors_portee", f"{e_loin}/{r_loin}")
        vide = Path(t) / "vide"
        vide.mkdir()
        e_nul, r_nul = ecart_entre(m0, vide)
        v("... et un maillage absent se declare illisible",
          e_nul is None and r_nul == "illisible", f"{e_nul}/{r_nul}")
        v("deux patchs confondus ont un écart nul", e_meme is not None and e_meme < 1.0,
          f"{e_meme}")
        # 13,1 voxels x 8,64 µm = 113 µm, l'espacement mesure entre nappes de ce rouleau.
        v("deux nappes voisines sont à ~113 µm",
          e_voisin is not None and abs(e_voisin - 113) < 5, f"{e_voisin}")
        v("... donc le discriminant les sépare de deux ordres de grandeur",
          e_meme is not None and e_voisin is not None and e_voisin > 50 * max(e_meme, 1e-6))

    r, dims = recouvrement(A, [[5, 5, 5], [15, 15, 15]])
    v("un recouvrement partiel est mesuré", abs(r - 0.125) < 1e-9, f"{r:.4f}")
    v("... et ses dimensions sont rendues", dims == [5.0, 5.0, 5.0], str(dims))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rouleau", default="PHerc1447")
    ap.add_argument("--voxel-um", type=float, default=8.64)
    ap.add_argument("--seuil", type=float, default=0.05,
                    help="fraction de recouvrement en dessous de laquelle une paire est "
                         "écartée")
    ap.add_argument("--telecharger", type=Path,
                    help="rapatrier les maillages ici et MESURER l'écart entre les paires "
                         "qui se recouvrent — c'est ce qui distingue « même feuille » de "
                         "« nappes voisines »")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    noms = lister(a.rouleau)
    print(f"  {len(noms)} segment(s) publié(s) pour {a.rouleau}")
    segs = []
    for n in noms:
        m = meta_de(a.rouleau, n)
        if m is None:
            print(f"    ⚠ {n[:40]} — pas de meta lisible")
            continue
        b = m["bbox"]
        d = [(b[1][i] - b[0][i]) * a.voxel_um / 1000.0 for i in range(3)]
        segs.append({"nom": n, "bbox": b, "taille_mm": d,
                     "aire_cm2": m.get("area_cm2"),
                     "generations": (m.get("vc_gsfs_params") or {}).get("generations")})
    print(f"  {len(segs)} meta(s) lisible(s)\n")
    print(f"  {'segment':<46}{'aire':>9}{'étendue mm (x,y,z)':>26}")
    for s in sorted(segs, key=lambda s: -(s["aire_cm2"] or 0)):
        ai = f"{s['aire_cm2']:.2f} cm²" if s["aire_cm2"] else "?"
        print(f"  {s['nom'][:44]:<46}{ai:>9}"
              f"{'  '.join(f'{x:5.1f}' for x in s['taille_mm']):>26}")

    paires = []
    for i, x in enumerate(segs):
        for y in segs[i + 1:]:
            f, dims = recouvrement(x["bbox"], y["bbox"])
            if f >= a.seuil:
                paires.append({"a": x["nom"], "b": y["nom"], "fraction": f,
                               "dims_mm": [d * a.voxel_um / 1000.0 for d in dims]})
    paires.sort(key=lambda p: -p["fraction"])
    print(f"\n  {len(paires)} paire(s) dont les boîtes se recouvrent d'au moins "
          f"{a.seuil * 100:.0f} % :")
    for p in paires[:12]:
        print(f"    {p['fraction'] * 100:5.1f} %  {p['a'][:26]} × {p['b'][:26]}"
              f"   ({'×'.join(f'{d:.0f}' for d in p['dims_mm'])} mm)")
    if not paires:
        print("    aucune — le raccordement de segments officiels n'a pas de candidat ici.")

    if a.telecharger:
        import sys as _s
        _s.path.insert(0, str(Path(__file__).resolve().parent))
        print(f"\n  téléchargement des {len(segs)} maillages…")
        chemins = {}
        for x in segs:
            d = telecharger(a.rouleau, x["nom"], a.telecharger / x["nom"])
            if d:
                chemins[x["nom"]] = d
        print(f"  {len(chemins)} maillage(s) sur place\n")
        print(f"  {'écart médian':>14}  paire")
        mesures, ailleurs = [], {}
        for pr in paires:
            if pr["a"] not in chemins or pr["b"] not in chemins:
                pr["raison"] = "absent"
                ailleurs["absent"] = ailleurs.get("absent", 0) + 1
                continue
            e, raison = ecart_entre(chemins[pr["a"]], chemins[pr["b"]], a.voxel_um)
            pr["raison"] = raison
            if e is None:
                ailleurs[raison] = ailleurs.get(raison, 0) + 1
                continue
            pr["ecart_um"] = e
            mesures.append(pr)
        mesures.sort(key=lambda p: p["ecart_um"])
        for pr in mesures[:14]:
            marque = "⭐ MEME FEUILLE" if pr["ecart_um"] < MEME_FEUILLE_UM else (
                "nappes voisines" if pr["ecart_um"] < VOISINES_UM else "éloignées")
            print(f"  {pr['ecart_um']:11.0f} µm  {pr['a'][:24]} × {pr['b'][:24]}  {marque}")
        # ⚠⚠ Les paires qu'on n'a PAS pu mesurer sont dites, pas tues. « hors_portee »
        # veut dire qu'aucun point de l'une n'approche l'autre a moins de la marge, soit
        # 432 µm — donc bien plus loin que le seuil de meme-feuille : ce sont des paires
        # eloignees, et les omettre du compte ferait un tableau dont les bandes ne
        # totalisent pas les paires.
        for raison, n in sorted(ailleurs.items()):
            print(f"  {'—':>11}     {n} paire(s) non mesurée(s) : {raison}"
                  + ("  (aucun point à moins de 432 µm : donc éloignées)"
                     if raison == "hors_portee" else ""))
        proches = [p for p in mesures if p["ecart_um"] < MEME_FEUILLE_UM]
        print(f"\n  ⭐ {len(proches)} paire(s) sous {MEME_FEUILLE_UM:.0f} µm — candidates à "
              f"un raccordement (deux patchs d'une même feuille).")
        print(f"     {sum(1 for p in mesures if MEME_FEUILLE_UM <= p['ecart_um'] < VOISINES_UM)}"
              f" paire(s) entre {MEME_FEUILLE_UM:.0f} et {VOISINES_UM:.0f} µm : des nappes "
              f"VOISINES, à ne surtout pas fusionner.")

    print("\n  ⚠ Un recouvrement de boîtes est un FILTRE, jamais une preuve : dans un rouleau,")
    print("    deux nappes VOISINES sont à 113 µm l'une de l'autre et leurs boîtes se")
    print("    recouvrent presque entièrement sans être la même feuille.")

    if a.json:
        a.json.write_text(json.dumps({"rouleau": a.rouleau, "segments": segs,
                                      "paires": paires}, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
