#!/usr/bin/env python3
"""Les piles de surface publiées atteignent-elles la feuille voisine ? — la question qui décide du recalage.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET IL ÉVITE DE CONSTRUIRE LA MAUVAISE CHOSE. `la_derive_est_elle_
un_biais` a montré que quatre cinquièmes de la dérive sont **locaux** : seul un raccrochage à la
matière peut les tuer. Un raccrochage lit de l'intensité **autour de la position prédite**, et la
position prédite est à **une épaisseur de feuille** de la surface de départ. La question est donc
préalable et purement géométrique : *les piles de surface publiées vont-elles assez loin ?*

⭐⭐ **Chaque spire publie un `surface-volumes` en (couche, u, v)**, donc l'indice de couche EST
une distance signée le long de la normale — à condition de savoir **quelle couche porte la
surface**. Les métadonnées ne le disent pas : elles donnent `num_slices` et `slice_step`, et une
translation nulle. Ça se mesure.

⚠⚠ ET C'EST LE PIÈGE : sur quelques blocs, le pic d'intensité tombe n'importe où — 66, 78, 85 —
parce qu'un bloc de 128 × 128 colonnes ne voit qu'un morceau de feuille. Le profil doit être
cumulé sur assez de blocs pour que le pic soit celui de la **feuille** et non d'un accident local.

Usage :
    uv run python src/nappe/la_portee_des_piles_publiees.py --verifier
    uv run python src/nappe/la_portee_des_piles_publiees.py \\
        --json docs/mesures/la_portee_des_piles_publiees.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "commun"))
sys.path.insert(0, str(RACINE / "src" / "nappe"))

BASE = "https://vesuvius-challenge-open-data.s3.amazonaws.com"
WRAPS = RACINE / "docs" / "mesures" / "les_wraps_publies.json"


def profil_de_pile(prefixe: str, couches: int, cote: int, blocs: int = 40,
                   timeout: float = 300.0) -> tuple[np.ndarray, int]:
    """L'intensité moyenne par couche, cumulée sur plusieurs blocs.

    ⚠⚠⚠ CUMULÉE, ET C'EST TOUT LE CONTRÔLE. Sur un seul bloc de 128 × 128 colonnes, le pic tombe
    n'importe où — 66, 78, 85 sur trois blocs voisins — parce qu'un bloc ne voit qu'un morceau de
    feuille. Le pic n'a de sens qu'une fois assez de colonnes accumulées, et le compte de colonnes
    est rendu pour qu'un profil bâti sur trois d'entre elles ne passe pas pour une mesure.

    ⚠ Les blocs absents ne sont pas des zéros : une pile est **creuse**, le format n'écrit que
    là où la spire existe. Les compter comme du vide baisserait le profil partout de la même
    façon, donc déplacerait le pic vers les couches les mieux remplies.
    """
    from zarr_depth import get  # noqa: PLC0415

    xml = get(f"{BASE}/?list-type=2&prefix={prefixe}/0/&max-keys=400", timeout)
    if xml is None:
        return np.zeros(0), 0
    cles = [k for k in re.findall(r"<Key>([^<]+)</Key>", xml.decode())
            if not k.endswith(".zarray")]
    attendu = couches * cote * cote
    somme, poids = np.zeros(couches), 0
    for k in cles[:blocs]:
        brut = get(f"{BASE}/{k}", timeout)
        if brut is None or len(brut) != attendu:
            continue
        a = np.frombuffer(brut, dtype=np.uint8).reshape(couches, -1)
        col = (a > 0).any(axis=0)
        if not col.any():
            continue
        somme += a[:, col].sum(axis=1)
        poids += int(col.sum())
    return (somme / poids if poids else somme), poids


def couche_de_la_surface(profil: np.ndarray) -> dict:
    """La couche du pic, et sa distance au CENTRE de la pile.

    ⚠⚠ Le centre est l'hypothèse par défaut du format — une pile de `n` couches rendue autour
    d'un maillage a sa surface au milieu — et elle doit être **vérifiée**, pas supposée. L'écart
    du pic au centre est donc rendu : c'est lui qui dit si la convention tient.
    """
    if profil.size == 0:
        return {}
    pic = int(np.argmax(profil))
    centre = (profil.size - 1) / 2.0
    return dict(couches=int(profil.size), pic=pic, centre=centre,
                ecart_au_centre=round(float(pic - centre), 1),
                contraste=round(float(profil.max() / max(1e-9, profil.min())), 3))


def portee(couches: int, voxel_um: float, ecart_um: float, surface: float) -> dict:
    """Jusqu'où la pile va, en micromètres et en épaisseurs de feuille.

    ⚠⚠⚠ C'EST LE CHIFFRE QUI DÉCIDE. Un raccrochage lit l'intensité **autour de la position
    prédite**, qui est à une épaisseur de la surface. Si la pile s'arrête avant, elle ne peut pas
    servir — quelle que soit la qualité du raccrochage qu'on écrirait dessus.
    """
    vers_le_haut = (couches - 1 - surface) * voxel_um
    vers_le_bas = surface * voxel_um
    atteint = min(vers_le_haut, vers_le_bas)
    return dict(vers_le_haut_um=round(vers_le_haut, 1), vers_le_bas_um=round(vers_le_bas, 1),
                portee_um=round(atteint, 1),
                portee_en_feuilles=round(atteint / ecart_um, 3),
                atteint_la_voisine=bool(atteint >= ecart_um),
                manque_um=round(ecart_um - atteint, 1) if atteint < ecart_um else 0.0)


def mesurer(blocs: int = 40, spires: int = 3) -> dict:
    """Le profil, la couche de la surface et la portée, sur plusieurs spires."""
    from les_wraps_publies import VOLUME, VOXEL_UM, wraps_du_fragment  # noqa: PLC0415
    from zarr_depth import get  # noqa: PLC0415

    if not WRAPS.is_file():
        raise SystemExit("écart entre spires non mesuré : lancer les_wraps_publies d'abord")
    ecart_um = json.loads(WRAPS.read_text())["resume"]["1"]["mediane_um"]

    lignes = []
    for w in wraps_du_fragment()[:spires]:
        pref = (f"PHerc0500P2/segments/{w['nom']}/surface-volumes/"
                f"{VOXEL_UM}um-0.4m-111keV-volume-{VOLUME}.zarr")
        meta = get(f"{BASE}/{pref}/0/.zarray", 120)
        if meta is None:
            continue
        z = json.loads(meta)
        couches, cote = int(z["shape"][0]), int(z["chunks"][1])
        prof, poids = profil_de_pile(pref, couches, cote, blocs)
        if poids == 0:
            continue
        s = couche_de_la_surface(prof)
        lignes.append(dict(spire=w["rang"], colonnes=poids, forme=z["shape"],
                           profil=[round(float(x), 2) for x in prof], **s))
    if not lignes:
        raise SystemExit("aucune pile lisible")

    # ⚠⚠ La couche de surface retenue est le CENTRE, pas le pic : le pic la confirme (l'écart au
    # centre est rendu), mais prendre le pic ferait dépendre la géométrie de l'intensité, donc
    # d'un contraste local — et une pile un peu plus dense d'un côté déplacerait la surface.
    couches = lignes[0]["couches"]
    surface = (couches - 1) / 2.0
    p = portee(couches, VOXEL_UM, ecart_um, surface)
    ecarts = [l["ecart_au_centre"] for l in lignes]
    return dict(volume=VOLUME, voxel_um=VOXEL_UM, ecart_inter_feuilles_um=ecart_um,
                blocs_par_spire=blocs, spires=lignes,
                couche_de_surface=surface,
                ecart_median_du_pic_au_centre=round(float(np.median(ecarts)), 1),
                # ⚠ Le pic doit tomber près du centre pour que la convention tienne : la borne
                # est une DEMI-FEUILLE en couches, la même règle que la coïncidence ailleurs.
                demi_feuille_en_couches=round(ecart_um / 2.0 / VOXEL_UM, 1),
                convention_du_centre_tient=bool(
                    abs(float(np.median(ecarts))) <= ecart_um / 2.0 / VOXEL_UM),
                **p)


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    prof = np.array([1.0, 2.0, 9.0, 2.0, 1.0])
    s = couche_de_la_surface(prof)
    v("le pic d'un profil centré est au centre",
      s["pic"] == 2 and s["ecart_au_centre"] == 0.0, str(s))
    v("... et le contraste est rendu", s["contraste"] == 9.0)
    dec = couche_de_la_surface(np.array([1.0, 9.0, 2.0, 1.0, 1.0]))
    v("... et un pic décalé le dit", dec["ecart_au_centre"] == -1.0, str(dec))
    v("un profil vide ne rend rien", couche_de_la_surface(np.zeros(0)) == {})

    # --- la portée, dans les deux sens ---
    p = portee(couches=121, voxel_um=2.0, ecart_um=100.0, surface=60.0)
    v("une pile qui va plus loin qu'une feuille l'atteint",
      p["atteint_la_voisine"] and p["manque_um"] == 0.0, str(p))
    v("... et sa portée est comptée en feuilles", p["portee_en_feuilles"] == 1.2)
    # ⚠⚠⚠ LE CAS QUI DÉCIDE, ET IL DOIT POUVOIR TOMBER DES DEUX CÔTÉS : une pile trop courte doit
    # dire de combien elle manque, sinon « elle ne suffit pas » serait un jugement sans mesure.
    q = portee(couches=101, voxel_um=2.0, ecart_um=150.0, surface=50.0)
    v("une pile trop courte dit de combien elle manque",
      not q["atteint_la_voisine"] and q["manque_um"] == 50.0, str(q))
    # ⚠ Une surface décentrée raccourcit le côté long : la portée est le MINIMUM des deux sens,
    # parce qu'un raccrochage peut avoir à chercher d'un côté comme de l'autre.
    r = portee(couches=101, voxel_um=2.0, ecart_um=100.0, surface=10.0)
    v("une surface décentrée fait la portée du côté le plus court",
      r["portee_um"] == 20.0 and r["vers_le_haut_um"] == 180.0, str(r))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--blocs", type=int, default=40)
    p.add_argument("--spires", type=int, default=3)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.blocs, a.spires)
    print(f"{'spire':>6} {'colonnes':>10} {'couches':>9} {'pic':>6} {'écart au centre':>17} "
          f"{'contraste':>11}")
    print("-" * 64)
    for l in r["spires"]:
        print(f"{l['spire']:>6} {l['colonnes']:>10} {l['couches']:>9} {l['pic']:>6} "
              f"{l['ecart_au_centre']:>+17.1f} {l['contraste']:>11.3f}")
    print(f"\nsurface retenue : couche {r['couche_de_surface']:.1f} (le centre) ; "
          f"pic médian à {r['ecart_median_du_pic_au_centre']:+.1f} couches")
    print(f"convention du centre : "
          f"{'TIENT' if r['convention_du_centre_tient'] else 'NE TIENT PAS'} "
          f"(tolérance {r['demi_feuille_en_couches']} couches = une demi-feuille)")
    print(f"\nportée de la pile : {r['portee_um']:.1f} µm = "
          f"{r['portee_en_feuilles']:.3f} feuille")
    print(f"écart inter-feuilles : {r['ecart_inter_feuilles_um']:.1f} µm")
    print(f"\n→ la pile atteint la feuille voisine : "
          f"{'OUI' if r['atteint_la_voisine'] else 'NON'}"
          + (f", il manque {r['manque_um']:.1f} µm" if not r["atteint_la_voisine"] else ""))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
