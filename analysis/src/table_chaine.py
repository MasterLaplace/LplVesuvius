#!/usr/bin/env python3
"""Depouiller une chaine de spires : taille, ecarts, alpha, verdict, et l'EROSION.

⚠⚠ Pourquoi ce fichier existe plutot qu'une commande jetable : ce tableau part dans un
document, donc son calcul doit etre dans l'arbre. Un chiffre publie dont le calcul n'est pas
rejouable n'est pas un resultat, c'est une anecdote.

⚠⚠ ET POURQUOI L'AIRE EST CALCULEE ICI. Un maillage produit par `mode: gen_neighbor` n'a
PAS de `area_cm2` dans son `meta.json` -- verifie : il porte bbox, format, scale, source,
target_volume, type, uuid, vc_gsfs_*. Sans ce calcul, une campagne d'enchainement affiche
« ? cm² » a chaque spire, et on ne peut pas dire si les spires gardent leur taille. Or c'est
justement la question : **une chaine qui s'erode a une longueur maximale.**

L'aire vient de deux choses qui sont deja ecrites : `grid_cols`/`grid_rows` dans le rapport
de selfcross, et `scale` dans le meta du maillage. Un pas de grille vaut `1/scale` voxels,
donc une cellule vaut `(pas x voxel_um)²`.

⚠ C'est l'aire de la GRILLE, pas celle de la matiere : les sommets invalides comptent quand
meme. C'est un majorant, honnete comme mesure de taille, faux comme mesure de surface utile.
La distinction est imprimee.

Usage :
    uv run python analysis/src/table_chaine.py data/spires --voxel-um 8.64 \\
        --json docs/chaine_spires.json
    uv run python analysis/src/table_chaine.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
PAS_DEFAUT_VOXELS = 20.0        # 1 / 0,05, l'echelle que le traceur ecrit par defaut


def aire_grille_cm2(cols: int, rows: int, pas_voxels: float, voxel_um: float) -> float:
    """Aire de la grille, en cm², depuis son nombre de cellules et la taille d'une cellule.

    ⚠ `cols - 1` et non `cols` : N sommets font N-1 cellules. L'oublier surestime de
    quelques pour cent, ce qui est juste assez peu pour passer inapercu.
    """
    cote_um = pas_voxels * voxel_um
    return max(0, cols - 1) * max(0, rows - 1) * (cote_um ** 2) * 1e-8


def pas_du_maillage(dossier: Path) -> float:
    """Le pas de grille en voxels, lu dans le `scale` du meta du maillage.

    ⚠ Lu et non suppose : deux campagnes peuvent tracer a des echelles differentes, et un
    pas suppose ferait des aires fausses d'un facteur (rapport des echelles)².
    """
    for meta in sorted(dossier.glob("trace/*/meta.json")) + sorted(dossier.glob("*/meta.json")):
        try:
            d = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            continue
        sc = d.get("scale")
        if isinstance(sc, list) and sc and sc[0]:
            return 1.0 / float(sc[0])
    return PAS_DEFAUT_VOXELS


def etiquette_de(racine_spires: Path) -> str:
    """L'etiquette que `spire_suivante.sh` met dans le nom des verdicts d'une campagne."""
    base = racine_spires.name
    return "" if base == "spires" else base.removeprefix("spires_") + "_"


def depouiller(racine_spires: Path, voxel_um: float, docs: Path) -> list[dict]:
    etiquette = etiquette_de(racine_spires)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lire_selfcross import lire  # noqa: E402

    lignes = []
    for d in sorted(p for p in racine_spires.glob("spire*") if p.is_dir()):
        rapport = d / "selfcross.json"
        # ⚠ L'etiquette de campagne fait partie du nom du verdict : sans elle, depouiller
        # la campagne A rendrait les chiffres de la campagne B (paye le 2026-08-21).
        verdict = docs / f"spire_{etiquette}{d.name}.json"
        if not rapport.is_file() or not verdict.is_file():
            continue
        brut = json.loads(rapport.read_text(encoding="utf-8"))
        cols, rows = brut.get("grid_cols"), brut.get("grid_rows")
        if not cols or not rows:
            continue
        try:
            croisements = lire(rapport)["transverse_self_intersections"]
        except Exception:
            croisements = None
        s = json.loads(verdict.read_text(encoding="utf-8"))["series"][0]
        lignes.append({
            "spire": d.name,
            "grille": [cols, rows],
            "aire_grille_cm2": round(aire_grille_cm2(cols, rows,
                                                     pas_du_maillage(d), voxel_um), 2),
            "croisements": croisements,
            "ecart_31c_um": s["serie"][0][1],
            "ecart_81c_um": s["serie"][-1][1],
            "alpha": round(s["alpha"], 3),
            "verdict": s["verdict"],
        })
    return lignes


def verifier() -> int:
    echecs = 0

    def ok(cond, quoi):
        nonlocal echecs
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de table_chaine")

    # 2x2 sommets = 1 cellule de 20 voxels de côté à 8,64 µm = 172,8 µm => 2,985e-4 cm²
    a = aire_grille_cm2(2, 2, 20.0, 8.64)
    ok(abs(a - (172.8 ** 2) * 1e-8) < 1e-12,
       f"une cellule seule fait bien son côté au carré ({a:.3e} cm²)")
    # ⚠ Sonde du « cols - 1 » : compter les SOMMETS au lieu des cellules surestime de 4x ici.
    faux = 2 * 2 * (172.8 ** 2) * 1e-8
    ok(abs(faux / a - 4.0) < 1e-9,
       "compter les sommets au lieu des cellules surestimerait d'un facteur 4 (sonde)")
    ok(aire_grille_cm2(1, 50, 20.0, 8.64) == 0.0,
       "une grille d'une seule colonne n'a aucune cellule")
    ok(aire_grille_cm2(0, 0, 20.0, 8.64) == 0.0,
       "une grille vide ne casse pas le calcul")
    # L'aire doit doubler si le pas double dans une seule direction ? non : elle quadruple.
    ok(abs(aire_grille_cm2(3, 3, 40.0, 8.64) / aire_grille_cm2(3, 3, 20.0, 8.64) - 4.0) < 1e-9,
       "doubler le pas quadruple l'aire (c'est un carré, pas une longueur)")

    # ⚠⚠ L'etiquette est ce qui empeche deux campagnes d'ecraser leurs verdicts. Sans elle,
    # depouiller `spires` rendrait les chiffres de `spires_repousse`.
    ok(etiquette_de(Path("data/spires")) == "",
       "la campagne de base n'a pas d'etiquette")
    ok(etiquette_de(Path("data/spires_repousse")) == "repousse_",
       "une campagne nommee spires_<x> porte l'etiquette <x>_")
    ok(etiquette_de(Path("data/spires")) != etiquette_de(Path("data/spires_repousse")),
       "deux campagnes ne peuvent pas partager un nom de verdict (la sonde)")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        # ⚠ Un meta sans `scale` doit retomber sur le pas par défaut, pas lever.
        (t / "trace" / "m").mkdir(parents=True)
        (t / "trace" / "m" / "meta.json").write_text('{"format": "tifxyz"}')
        ok(pas_du_maillage(t) == PAS_DEFAUT_VOXELS,
           "un meta sans échelle retombe sur le pas par défaut")
        (t / "trace" / "m" / "meta.json").write_text('{"scale": [0.1, 0.1]}')
        ok(pas_du_maillage(t) == 10.0, "une échelle de 0,1 donne un pas de 10 voxels")

    print(f"\n{'tous les témoins passent' if not echecs else f'{echecs} échec(s)'}")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("racine", nargs="?", type=Path)
    ap.add_argument("--voxel-um", type=float, default=8.64)
    ap.add_argument("--docs", type=Path, default=RACINE / "docs")
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.racine:
        ap.error("donner la racine des spires, ou --verifier")

    lignes = depouiller(a.racine, a.voxel_um, a.docs)
    if not lignes:
        print("aucune spire jugée sous cette racine", file=sys.stderr)
        return 3

    print(f"{'spire':<9}{'grille':>10}{'aire*':>9}{'crois.':>8}"
          f"{'31c':>9}{'81c':>9}{'α':>8}  verdict")
    for l in lignes:
        c, r = l["grille"]
        print(f"{l['spire']:<9}{c}x{r:<6}{l['aire_grille_cm2']:>9.2f}"
              f"{('?' if l['croisements'] is None else l['croisements']):>8}"
              f"{l['ecart_31c_um']:>9.2f}{l['ecart_81c_um']:>9.2f}"
              f"{l['alpha']:>+8.3f}  {l['verdict']}")
    print("  * aire de la GRILLE (sommets invalides compris) — un majorant, pas la surface utile")

    conv = sum(1 for l in lignes if l["verdict"] == "converge")
    trav = sum(1 for l in lignes if l["verdict"] == "suit la fenêtre")
    print(f"\n  {conv}/{len(lignes)} convergent, {trav} suivent la fenêtre")
    if len(lignes) >= 2:
        a0, a1 = lignes[0]["aire_grille_cm2"], lignes[-1]["aire_grille_cm2"]
        if a0:
            perte = 100 * (1 - a1 / a0)
            par = perte / (len(lignes) - 1)
            print(f"  érosion : {a0:.2f} → {a1:.2f} cm² sur {len(lignes) - 1} tours "
                  f"({perte:.0f} % au total, {par:.1f} % par tour)")
            if par > 0:
                print(f"  ⚠ à ce rythme, la moitié de la surface est perdue en "
                      f"{int(round(50 / par))} tours")
    if a.json:
        Path(a.json).write_text(json.dumps(lignes, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
