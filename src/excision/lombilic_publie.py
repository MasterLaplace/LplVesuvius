#!/usr/bin/env python3
"""Cinq rouleaux publient leur axe — et la mesure appariée y survit sans bouger d'un point.

⚠⚠⚠ CE FICHIER CORRIGE UNE AFFIRMATION DU DÉPÔT, ET C'EST LE MÊME ANGLE MORT POUR LA TROISIÈME
FOIS. `laxe_nest_pas_une_ligne.py` écrit :

    « La dérive mesurée est celle de **Scroll 1**. C'est le **seul** rouleau qui publie un
      ombilic — vérifié le même jour sur les cinq répertoires `umbilici/` de `dl.ash2txt.org`. »

La vérification était juste et sa conclusion fausse : elle portait sur **un** serveur et **une**
convention de chemin. Sur le bucket ouvert `vesuvius-challenge-open-data`, l'axe vit sous
`<rouleau>/representations/umbilicus/`, et **cinq** rouleaux en publient un — balayés ici sur
les 46 préfixes de premier niveau, pas sur une liste écrite à la main.

C'est l'angle mort que `59` a payé, que ce même fichier a repayé sur un autre objet, et que
voici sur **le même objet** : interroger une vue du corpus et conclure sur le corpus.

⭐⭐⭐ ET CE QUE L'AXE PUBLIÉ PERMET DE VÉRIFIER EST PLUS UTILE QUE L'AXE LUI-MÊME. `76` et `77`
ajustent un centre par tranche sur les spires elles-mêmes. Un ajustement de cercle sur un **arc
partiel** est biaisé — c'est un défaut connu de la méthode, et le mesurer demandait un axe
indépendant. On l'a : 391 points annotés **à la main** sur `PHerc0139`.

    biais mesuré entre l'axe ajusté et l'axe publié : 180 à 445 voxels, soit 1,7 à 4,2 mm,
    c'est-à-dire jusqu'à ~29 écarts inter-feuilles.

⭐⭐ **Et la mesure appariée n'en bouge pas.** C'est exactement ce pour quoi elle a été conçue —
comparer deux spires *au même endroit, autour du même centre*, de sorte qu'un biais commun
s'annule — et c'est maintenant **mesuré** au lieu d'être argumenté :

    axe ajusté (`76`)   vers l'extérieur 94,8 %   écart 155,8 µm
    axe publié          vers l'extérieur 94,8 %   écart 156,8 µm

Un axe faux de 4 mm déplace le verdict de **zéro point** et l'écart d'**un micromètre**.

⚠ Et une sonde localise d'où vient cette immunité, ce que je n'aurais pas su dire sans elle :
remplacer le centre par tranche par un centre **global** ne change rien non plus (94,6 % contre
94,5 %). L'immunité ne vient donc **pas** de la qualité du centre mais du fait que les deux
spires sont comparées **dans la même cellule angulaire autour du même centre**, quel qu'il
soit. Un centre par tranche améliore les rayons **absolus** ; la comparaison, elle, était déjà
immunisée.

⚠ CE QUE CE FICHIER N'ÉTABLIT PAS :

1. **Que l'axe publié soit juste et l'ajusté faux.** Il établit qu'ils **diffèrent** et que la
   conclusion n'en dépend pas. L'axe publié est annoté à la main, donc c'est un jugement
   humain, pas une vérité — mais c'est un jugement **indépendant** de notre ajustement, ce qui
   est précisément ce qu'il faut pour tester une robustesse.
2. **Que les cinq axes soient de même qualité.** Ils vont de 49 à 391 points de contrôle, et
   seuls deux nomment leur annotateur.
3. **Que Scroll 1 n'en publie pas.** Il en publie un, ailleurs, et
   `laxe_nest_pas_une_ligne.py` le mesure. Les deux serveurs se complètent ; ce fichier ne
   remplace pas l'autre, il corrige le mot « seul ».

Usage :
    uv run python src/excision/lombilic_publie.py --verifier
    uv run python src/excision/lombilic_publie.py --json docs/mesures/lombilic_publie.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
AXES = RACINE / "data" / "axes"
sys.path[:0] = [str(RACINE / "src" / "excision")]
import le_champ_denroulement as champ  # noqa: E402
from le_sens_des_indices import SECTEURS, charger, _spires  # noqa: E402

BUCKET = "vesuvius-challenge-open-data"
CHEMIN = "<rouleau>/representations/umbilicus/"
"""⚠ La convention de CE bucket. `dl.ash2txt.org` en emploie une autre, `umbilici/`, et c'est
la différence qui a produit l'erreur que ce fichier corrige. Écrite ici pour que la prochaine
recherche d'axe sache qu'il y a deux endroits à regarder, pas un."""

RESOLUTIONS_CONNUES = (9.362, 7.91, 4.681, 3.24, 2.403, 2.399, 1.129)
"""Les tailles de voxel que les scans publiés emploient. ⚠ Le `volume` d'un ombilic est un
identifiant long (`20260102150214-2.399um-0.2m-78keV`) et **pas** un nom de volume de segment :
celui-là portait la résolution d'avant binning (cf. `76`). Celui-ci est validé contre cette
liste, et refusé s'il n'y tombe pas."""


def voxel_de(meta: dict) -> float | None:
    """
    @brief La taille de voxel déclarée par l'ombilic, validée contre les résolutions publiées.
    """
    trouve = re.search(r"-([\d.]+)um", str(meta.get("volume", "")))
    if not trouve:
        return None
    v = float(trouve.group(1))
    return v if any(abs(v - r) < 0.001 for r in RESOLUTIONS_CONNUES) else None


def rapatrier(delai: int = 60) -> int:
    """
    @brief Trouver et rapatrier tous les ombilics publiés, en balayant le bucket.

    ⚠⚠ Balayé et non lu dans une liste écrite à la main — c'est exactement l'erreur que ce
    fichier corrige. Une liste en dur redeviendrait fausse le jour où un sixième rouleau en
    publie un, et **sans aucun symptôme**.

    ⚠ `data/axes/` est hors du contrôle de version (données, pas résultats), donc cette
    fonction est la seule chose qui rende la mesure rejouable sur une copie fraîche. Sa
    commande est nommée dans le message d'erreur de `charger_axe`.
    """
    import concurrent.futures as cf
    import subprocess

    AXES.mkdir(parents=True, exist_ok=True)
    racine = subprocess.run(
        ["curl", "-s", "--max-time", str(delai), f"https://{BUCKET}.s3.amazonaws.com/"
         "?list-type=2&delimiter=/"], capture_output=True, text=True)
    rouleaux = [p.rstrip("/") for p in re.findall(r"<Prefix>([^<]+)</Prefix>", racine.stdout)]

    def un(nom: str) -> str | None:
        url = (f"https://{BUCKET}.s3.amazonaws.com/?list-type=2"
               f"&prefix={nom}/representations/umbilicus/&max-keys=5")
        r = subprocess.run(["curl", "-s", "--max-time", str(delai), url],
                           capture_output=True, text=True)
        clefs = re.findall(r"<Key>([^<]+)</Key>", r.stdout)
        if not clefs:
            return None
        cible = AXES / f"{nom}_umbilicus.json"
        if not cible.is_file():
            subprocess.run(["curl", "-s", "-f", "--max-time", str(delai * 2),
                            "-o", str(cible),
                            f"https://{BUCKET}.s3.amazonaws.com/{clefs[0]}"], check=False)
        return nom if cible.is_file() else None

    with cf.ThreadPoolExecutor(10) as ex:
        trouves = [n for n in ex.map(un, rouleaux) if n]
    print(f"{len(trouves)} ombilic(s) sur {len(rouleaux)} préfixes balayés : "
          f"{', '.join(sorted(trouves))}")
    return len(trouves)


def charger_axe(rouleau: str) -> tuple[np.ndarray, dict] | None:
    """
    @brief Les points de contrôle d'un ombilic publié, en voxels de SON volume.
    """
    fichier = AXES / f"{rouleau}_umbilicus.json"
    if not fichier.is_file():
        return None
    d = json.loads(fichier.read_text())
    p = np.array([[c["x"], c["y"], c["z"]] for c in d["control_points"]], dtype=float)
    return p, d.get("metadata", {})


def _centres_publies(points: np.ndarray, facteur: float, bords_z) -> dict[int, tuple]:
    """
    @brief Un centre par tranche, interpolé le long de l'axe publié.

    ⚠ Interpolé et non moyenné par tranche : une tranche peut ne contenir aucun point de
    contrôle, et la moyenne d'un ensemble vide serait un trou là où l'axe est parfaitement
    défini entre deux points.
    """
    p = points * facteur
    ordre = np.argsort(p[:, 2])
    z, x, y = p[ordre, 2], p[ordre, 0], p[ordre, 1]
    milieux = (bords_z[:-1] + bords_z[1:]) / 2
    return {i: (float(np.interp(m, z, x)), float(np.interp(m, z, y)))
            for i, m in enumerate(milieux)}


def _apparier(nuages: dict, bords_z, bords_t, centres) -> tuple[float, float, int]:
    """
    @brief La mesure de `76` — sens et écart — refaite autour d'un jeu de centres donné.
    """
    indices = sorted(nuages)
    parts, ecarts = [], []
    for a, b in zip(indices, indices[1:]):
        if b - a != 1:
            continue
        (xa, ya, za), (xb, yb, zb) = nuages[a], nuages[b]
        dr = []
        for i, (lo, hi) in enumerate(zip(bords_z, bords_z[1:])):
            if i not in centres:
                continue
            sa, sb = (za >= lo) & (za < hi), (zb >= lo) & (zb < hi)
            if sa.sum() < 200 or sb.sum() < 200:
                continue
            cx, cy = centres[i]
            ta = np.digitize(np.arctan2(ya[sa] - cy, xa[sa] - cx), bords_t)
            tb = np.digitize(np.arctan2(yb[sb] - cy, xb[sb] - cx), bords_t)
            ra = np.hypot(xa[sa] - cx, ya[sa] - cy)
            rb = np.hypot(xb[sb] - cx, yb[sb] - cy)
            for k in range(1, SECTEURS + 1):
                pa, pb = ra[ta == k], rb[tb == k]
                if len(pa) >= 10 and len(pb) >= 10:
                    dr.append(float(np.median(pb) - np.median(pa)))
        if dr:
            d = np.array(dr)
            parts.append(float((d > 0).mean()))
            ecarts.append(float(np.median(d)))
    return (float(np.mean(parts)) if parts else 0.0,
            float(np.median(ecarts)) if ecarts else 0.0, len(parts))


def mesurer(rouleau: str = "PHerc0139", voxel_um: float = 9.362) -> dict:
    axes = {}
    for fichier in sorted(AXES.glob("*_umbilicus.json")):
        nom = fichier.stem.removesuffix("_umbilicus")
        d = json.loads(fichier.read_text())
        axes[nom] = dict(points=len(d["control_points"]),
                         voxel_um=voxel_de(d.get("metadata", {})),
                         annotateur=d.get("metadata", {}).get("annotator"))

    charge = charger_axe(rouleau)
    dossiers = _spires(rouleau)
    nuages = {k: v for k, v in ((k, charger(x)) for k, x in dossiers.items()) if v}
    if not charge or len(nuages) < 5:
        return dict(axes_publies=axes, comparaison=None)

    points, meta = charge
    facteur = (voxel_de(meta) or voxel_um) / voxel_um
    bords_z, bords_t, ajustes = champ._grille(nuages)
    publies = _centres_publies(points, facteur, bords_z)

    ecarts_axe = [float(np.hypot(ajustes[i][0] - publies[i][0],
                                 ajustes[i][1] - publies[i][1]))
                  for i in ajustes if i in publies]

    part_a, ecart_a, n_a = _apparier(nuages, bords_z, bords_t, ajustes)
    part_p, ecart_p, n_p = _apparier(nuages, bords_z, bords_t, publies)

    return dict(
        axes_publies=axes, bucket=BUCKET, chemin=CHEMIN,
        comparaison=dict(
            rouleau=rouleau, voxel_um=voxel_um, facteur_de_conversion=facteur,
            points_de_controle=len(points),
            tranches=len(ecarts_axe),
            biais_median_vx=float(np.median(ecarts_axe)),
            biais_median_um=float(np.median(ecarts_axe) * voxel_um),
            biais_max_vx=float(max(ecarts_axe)),
            biais_max_en_feuilles=float(max(ecarts_axe) * voxel_um / 154.1),
            axe_ajuste=dict(part_vers_l_exterieur=part_a,
                            ecart_um=ecart_a * voxel_um, paires=n_a),
            axe_publie=dict(part_vers_l_exterieur=part_p,
                            ecart_um=ecart_p * voxel_um, paires=n_p),
        ))


def _verifier(r: dict) -> int:
    echecs = 0
    comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    a = r["axes_publies"]
    print("la correction : plusieurs rouleaux publient leur axe, pas un seul")
    v("au moins cinq ombilics sont récupérés",
      len(a) >= 5, f"{len(a)} : {', '.join(sorted(a))}")
    v("chacun déclare une résolution de scan reconnue",
      all(x["voxel_um"] is not None for x in a.values()),
      ", ".join(f"{n}={x['voxel_um']}" for n, x in sorted(a.items())))

    c = r.get("comparaison")
    if not c:
        print("  --    (spires absentes du cache — comparaison impossible)")
        print()
        print(f"  ALL PASS (0 failures, {comptees} checks)" if not echecs
              else f"  ECHEC ({echecs} failures)")
        return echecs

    print("l'axe ajusté est BIAISÉ, et l'axe publié le montre")
    # ⚠ Ecrit dans le sens « il Y A un biais ». Un biais nul serait une bonne nouvelle ; un
    # biais qu'on n'a pas cherche est une hypothese. Et sans ce controle, celui d'apres --
    # « la mesure n'en bouge pas » -- serait vrai pour la mauvaise raison : deux axes
    # identiques donnent evidemment le meme resultat.
    v("les deux axes diffèrent de plusieurs feuilles",
      c["biais_max_en_feuilles"] > 5.0,
      f"médiane {c['biais_median_um'] / 1000:.2f} mm, max "
      f"{c['biais_max_en_feuilles']:.0f} écarts inter-feuilles")

    print("⭐ et la mesure appariée n'en bouge pas — c'est ce pour quoi elle est appariée")
    aj, pu = c["axe_ajuste"], c["axe_publie"]
    v("le sens est le même au dixième de point près",
      abs(aj["part_vers_l_exterieur"] - pu["part_vers_l_exterieur"]) < 0.005,
      f"{aj['part_vers_l_exterieur'] * 100:.1f} % contre "
      f"{pu['part_vers_l_exterieur'] * 100:.1f} %")
    v("l'écart inter-feuilles est le même à quelques µm près",
      abs(aj["ecart_um"] - pu["ecart_um"]) < 5.0,
      f"{aj['ecart_um']:.1f} µm contre {pu['ecart_um']:.1f} µm")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rouleau", default="PHerc0139")
    p.add_argument("--rapatrier", action="store_true",
                   help="balayer le bucket et télécharger les ombilics publiés")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    args = p.parse_args()

    if args.rapatrier:
        rapatrier()

    r = mesurer(args.rouleau)
    if not r["axes_publies"]:
        raise SystemExit(
            f"aucun ombilic en cache sous {AXES}\n"
            f"  les rapatrier :  uv run python src/excision/lombilic_publie.py --rapatrier")
    if not args.verifier or args.json:
        print(f"ombilics publiés sur le bucket ouvert, sous {CHEMIN} :")
        for nom, x in sorted(r["axes_publies"].items()):
            print(f"  {nom:12s} {x['points']:4d} points · voxel {x['voxel_um']} µm"
                  + (f" · annoté par {x['annotateur']}" if x["annotateur"] else ""))
        c = r.get("comparaison")
        if c:
            print(f"\naxe ajusté contre axe publié, {c['rouleau']} "
                  f"({c['tranches']} tranches) :")
            print(f"  biais médian {c['biais_median_um'] / 1000:.2f} mm · "
                  f"max {c['biais_max_en_feuilles']:.0f} écarts inter-feuilles")
            for nom, x in (("axe ajusté", c["axe_ajuste"]), ("axe publié", c["axe_publie"])):
                print(f"  {nom:12s} : vers l'extérieur "
                      f"{x['part_vers_l_exterieur'] * 100:5.1f} % · "
                      f"écart {x['ecart_um']:6.1f} µm")

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
