#!/usr/bin/env python3
"""Les deux objets de M1ter, comparés sur les trois axes que leur scan porte.

⚠⚠ Pourquoi ce fichier existe. [`58`](../../docs/archive/58_resolution_ou_rouleau.md) élimine la
**résolution** comme cause de l'inertie du modèle sur `PHerc1447` : les deux objets sont à
**9 %** l'un de l'autre sur les deux axes de résolution, et dix fois cet écart ne rendrait
qu'un facteur 2,1 sur les 45 à expliquer. Il conclut qu'il reste « ce rouleau-ci ».

⭐⭐ Mais il a comparé les deux objets sur l'axe qu'il pouvait éliminer, et **jamais nommé
celui où ils diffèrent d'un facteur deux**. Le nom du volume public le porte :

    témoin qui MARCHE   PHercParis4, 7,91 µm, **54 keV**   (AUC 0,925)
    objet qui ÉCHOUE    PHerc1447,   8,64 µm, **116 keV**

Un rapport de **9 %** sur la résolution, de **115 %** sur l'énergie. « Ce rouleau-ci » n'est
donc pas le seul suspect restant : la **campagne de scan** en est un, et elle a l'avantage
d'être une propriété qu'on peut acheter alors qu'un rouleau ne change pas.

⚠⚠⚠ CE QUE ÇA N'ÉTABLIT PAS, et il faut le dire à chaque usage. `campagnes_de_scan.py` a
déjà mesuré que les trois grandeurs **co-varient par campagne** — un scan fin est aussi à
courte propagation et à basse énergie. Ce fichier ne les sépare pas ; il **chiffre l'écart**
sur chacune, ce que personne n'avait fait pour cette paire-ci. Isoler l'énergie demanderait
d'émuler une énergie plus haute sur l'objet qui marche, comme `58` a émulé une résolution
plus grossière — et une émulation d'énergie n'est PAS une décimation : elle change les
coefficients d'atténuation différemment selon le matériau. C'est le lot suivant, pas celui-ci.

⚠ Le mode par défaut lit un relevé déjà écrit. `--lister` est le seul qui touche au réseau,
et il écrit ce qu'il a lu, pour que la mesure se rejoue hors ligne.

Usage :
    uv run python src/encre/deux_objets.py --verifier
    uv run python src/encre/deux_objets.py --lister --json docs/mesures/deux_objets.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

OBJETS = {
    "temoin_qui_marche": {
        "rouleau": "Scroll1",
        "volpkg": "PHercParis4.volpkg",
        "volume": "20230205180739",
        "role": "le modèle y atteint AUC 0,925",
    },
    "objet_qui_echoue": {
        "rouleau": "PHerc1447",
        "nom_de_volume": "8.64um-1.2m-116keV-volume-20250521151220",
        "role": "le modèle y est inerte",
    },
}
"""Les deux objets que `58` compare, et rien d'autre.

⚠ Le premier est identifié par son UUID de volume et son `meta.json` ; le second par le NOM
de son volume de surface, qui porte les trois grandeurs. Deux sources différentes pour la
même question, parce que le dépôt public les expose différemment — et les mélanger ferait
croire à une mesure là où il y a deux lectures.
"""

TROIS_GRANDEURS = re.compile(r"([\d.]+)um-([\d.]+)m-(\d+)keV")
"""Pas de voxel, distance de propagation, énergie du faisceau — dans cet ordre, tels que le
dépôt public les écrit dans le nom d'un volume."""


def grandeurs_du_nom(nom: str) -> dict | None:
    """Les trois grandeurs lues dans un nom de volume, ou `None` s'il ne les porte pas."""
    m = TROIS_GRANDEURS.search(nom)
    if not m:
        return None
    return {"voxel_um": float(m.group(1)), "distance_m": float(m.group(2)),
            "energie_keV": int(m.group(3))}


def ecart_relatif(a: float, b: float) -> float:
    """L'écart entre deux valeurs, rapporté à la PLUS PETITE.

    ⚠⚠ Rapporté à la plus petite, et c'est un choix qui se dit : `58` écrit « les deux objets
    sont à 9 % l'un de l'autre », ce qui est 8,64/7,91 − 1. Rapporter à la plus grande
    donnerait 8 % pour le même fait, et comparer un 9 % à un 115 % calculés dans deux sens
    différents serait une comparaison qui ment.
    """
    petit, grand = min(a, b), max(a, b)
    return (grand - petit) / petit if petit else float("inf")


def comparer(temoin: dict, echoue: dict) -> dict:
    """Les trois écarts, chacun avec ses deux valeurs pour qu'on puisse recalculer."""
    lignes = []
    for cle, unite in (("voxel_um", "µm"), ("distance_m", "m"), ("energie_keV", "keV")):
        a, b = temoin.get(cle), echoue.get(cle)
        if a is None or b is None:
            continue
        lignes.append({"grandeur": cle, "unite": unite, "temoin": a, "echoue": b,
                       "ecart_relatif": round(ecart_relatif(a, b), 4)})
    return {"grandeurs": lignes,
            "axe_le_plus_ecarte": max(lignes, key=lambda l: l["ecart_relatif"])["grandeur"]
            if lignes else None}


def lire_en_ligne() -> dict:
    """Interroge le dépôt public. Le SEUL mode qui touche au réseau."""
    t = OBJETS["temoin_qui_marche"]
    url = (f"https://dl.ash2txt.org/full-scrolls/{t['rouleau']}/{t['volpkg']}"
           f"/volumes/{t['volume']}/meta.json")
    p = subprocess.run(["curl", "-s", "--max-time", "60", url],
                       capture_output=True, text=True)
    meta = json.loads(p.stdout)
    # ⚠ Le nom du volume du témoin porte l'énergie EN CLAIR mais pas dans la forme
    # `…keV-volume-…` : c'est « PHercParis4 54keV stitched_part_1 ». On lit donc l'énergie
    # dans le nom et le pas dans le champ `voxelsize`, qui est la valeur que le dépôt
    # déclare — jamais une valeur déduite du nom, qui l'arrondit.
    m = re.search(r"(\d+)\s*keV", meta.get("name", ""))
    temoin = {"voxel_um": float(meta["voxelsize"]),
              "energie_keV": int(m.group(1)) if m else None,
              "source": url, "nom": meta.get("name")}
    echoue = grandeurs_du_nom(OBJETS["objet_qui_echoue"]["nom_de_volume"]) or {}
    echoue["source"] = OBJETS["objet_qui_echoue"]["nom_de_volume"]
    return {"temoin": temoin, "echoue": echoue, **comparer(temoin, echoue)}


def verifier() -> int:
    """Auto-test HORS LIGNE : la lecture des noms et le sens de l'écart."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LES TROIS GRANDEURS DANS UN NOM DE VOLUME -------------------------------------
    g = grandeurs_du_nom("8.64um-1.2m-116keV-volume-20250521151220")
    v("le pas de voxel est lu", g and abs(g["voxel_um"] - 8.64) < 1e-9)
    v("la distance de propagation est lue", g and abs(g["distance_m"] - 1.2) < 1e-9)
    v("l'energie du faisceau est lue", g and g["energie_keV"] == 116)
    v("un nom qui ne les porte pas rend None",
      grandeurs_du_nom("PHercParis4 54keV stitched_part_1") is None)
    # ⚠ Ce dernier controle n'est PAS un detail : le temoin est justement dans ce cas, donc
    # sa lecture passe par `meta.json` et pas par son nom.

    # --- LE SENS DE L'ECART -------------------------------------------------------------
    v("l'ecart est rapporte a la plus petite valeur",
      abs(ecart_relatif(7.91, 8.64) - 0.0923) < 1e-3)
    v("... et il est symetrique dans ses arguments",
      ecart_relatif(7.91, 8.64) == ecart_relatif(8.64, 7.91))
    # ⚠⚠ Le fait qui donne son sens au fichier : l'ecart d'ENERGIE est plus de dix fois
    # celui de RESOLUTION entre ces deux objets-la.
    v("l'ecart d'energie (54 vs 116) depasse le double",
      ecart_relatif(54, 116) > 1.0)
    v("... et il vaut plus de dix fois celui de la resolution",
      ecart_relatif(54, 116) > 10 * ecart_relatif(7.91, 8.64))

    # --- LA COMPARAISON, sur des valeurs fabriquees -------------------------------------
    c = comparer({"voxel_um": 7.91, "energie_keV": 54},
                 {"voxel_um": 8.64, "distance_m": 1.2, "energie_keV": 116})
    v("une grandeur absente d'un cote est sautee", len(c["grandeurs"]) == 2)
    v("l'axe le plus ecarte est l'energie", c["axe_le_plus_ecarte"] == "energie_keV")
    # ⚠ Et le controle qui empeche de lire ce fichier comme une conclusion : si les deux
    # objets avaient la MEME energie, l'axe le plus ecarte serait la resolution.
    c2 = comparer({"voxel_um": 7.91, "energie_keV": 116},
                  {"voxel_um": 8.64, "energie_keV": 116})
    v("... et ce serait la resolution si les energies coincidaient",
      c2["axe_le_plus_ecarte"] == "voxel_um")

    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lister", action="store_true",
                    help="interroger le dépôt public (le seul mode qui touche au réseau)")
    ap.add_argument("--depuis", type=Path, help="re-dériver depuis un relevé déjà écrit")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if a.depuis:
        d = json.loads(a.depuis.read_text())
        d.update(comparer(d["temoin"], d["echoue"]))
    elif a.lister:
        d = lire_en_ligne()
    else:
        ap.error("donner --lister, --depuis ou --verifier")

    print(f"  témoin qui marche : {d['temoin'].get('nom', '?')}")
    print(f"  objet qui échoue  : {d['echoue'].get('source', '?')}\n")
    print("  grandeur          témoin      échoue      écart")
    for l in d["grandeurs"]:
        print(f"  {l['grandeur']:16s} {l['temoin']:>8} {l['unite']:<4} "
              f"{l['echoue']:>8} {l['unite']:<4} {100 * l['ecart_relatif']:7.1f} %")
    print(f"\n  axe le plus écarté : {d['axe_le_plus_ecarte']}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
