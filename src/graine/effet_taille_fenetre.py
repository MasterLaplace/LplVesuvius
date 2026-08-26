#!/usr/bin/env python3
"""Le relief dépend de la taille de la FENÊTRE D'ANALYSE, pas seulement de la profondeur.

⚠⚠ **Ce fichier existe parce qu'une affirmation publiée était fausse pendant une heure.**
Le README de `tracecheck` offrait « 2,25 fois le plancher » comme repère bas d'une surface
qui suit une feuille. Ce nombre avait été mesuré dans des fenêtres d'analyse de **1024 px**
et il était offert à un outil qui lit des morceaux de **128 px**. Le seuil ne transportait
pas, pour une raison que la mise en garde d'à côté ne nommait pas : elle parlait de la
profondeur, pas de l'étendue dans le plan.

⭐ Mesuré ici sur une pile rendue inchangée, donc sur la même surface, la même profondeur et
les mêmes voxels — seule la fenêtre d'analyse change. Le relief **triple** en deux
divisions par deux, ce qui est du même ordre que l'effet de la profondeur (β ≈ +1). Un
seuil calibré sur un instrument ne veut donc rien dire sur un autre.

⚠ Ce n'est pas un défaut du relief : c'est une propriété de toute statistique de contraste
lue sur une moyenne de patch. Une fenêtre large moyenne plus, donc écrase les extrêmes qui
font l'amplitude. Ce qu'il faut en retenir n'est pas « la grandeur est mauvaise » mais
« la grandeur se compare à l'intérieur d'un instrument, jamais entre deux ».

Reproduire :

    python3 src/graine/effet_taille_fenetre.py data/paris4_candidats/ps256_c0/rendu_161 \\
        --tailles 1024 512 256 --couche-tracee 80 --json docs/mesures/effet_taille_fenetre.json
    python3 src/graine/effet_taille_fenetre.py --verifier
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]


def profil(dossier: Path, taille: int, couche_tracee: int, voxel_um: float,
           pas: int = 200) -> dict | None:
    """Le profil d'une pile rendue, à une taille de fenêtre d'analyse donnée.

    ⚠ Délégué à `depth_profile.py` par un sous-processus, jamais réimplémenté : c'est LUI
    qui définit l'amplitude, et une seconde définition dans le dépôt finirait par ne pas
    s'accorder avec les nombres qu'on lui compare. Le coût d'un sous-processus est
    négligeable devant la lecture de cent soixante et une images.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        sortie = Path(f.name)
    cmd = [sys.executable, str(Path(__file__).resolve().parent / "depth_profile.py"),
           str(dossier), "--grid", "--size", str(taille), "--step", str(pas),
           "--traced-layer", str(couche_tracee), "--voxel-um", str(voxel_um),
           "--out", str(sortie)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not sortie.is_file():
        return None
    d = json.loads(sortie.read_text(encoding="utf-8"))
    sortie.unlink(missing_ok=True)
    d = d[0] if isinstance(d, list) and d else d
    return d if isinstance(d, dict) else None


def exposant(mesures: list[dict]) -> float | None:
    """L'exposant du relief contre la taille de fenêtre, lu comme α et β le sont.

    ⚠ NÉGATIF par construction attendue : une fenêtre plus large moyenne davantage, donc
    écrase l'amplitude. Un exposant positif voudrait dire que l'effet va dans l'autre sens
    et mériterait d'être regardé plutôt que publié.
    """
    pts = sorted({(m["taille"], m["amplitude"]) for m in mesures
                  if m.get("amplitude") is not None and m["amplitude"] > 0})
    if len(pts) < 2:
        return None
    (t0, a0), (t1, a1) = pts[0], pts[-1]
    if t0 <= 0 or t1 <= t0 or a0 <= 0 or a1 <= 0:
        return None
    return math.log(a1 / a0) / math.log(t1 / t0)


def resumer(mesures: list[dict]) -> dict:
    ok = [m for m in mesures if m.get("amplitude") is not None]
    amplitudes = [m["amplitude"] for m in ok]
    return {"mesures": mesures, "exposant_taille": exposant(ok),
            "rapport_extreme": (max(amplitudes) / min(amplitudes)
                                if amplitudes and min(amplitudes) > 0 else None),
            "tailles": [m["taille"] for m in ok]}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠ Les valeurs REELLES mesurees sur `ps256_c0/rendu_161`, pile inchangee : seule la
    # fenetre d analyse change. Elles sont ecrites ici parce que ce sont elles qui ont
    # corrige le README, donc elles doivent vieillir bruyamment.
    reel = [{"taille": 1024, "amplitude": 0.0462, "fenetres": 49},
            {"taille": 512, "amplitude": 0.0813, "fenetres": 100},
            {"taille": 256, "amplitude": 0.1461, "fenetres": 121}]
    r = resumer(reel)
    v("le relief TRIPLE de 1024 px a 256 px",
      r["rapport_extreme"] is not None and abs(r["rapport_extreme"] - 3.16) < 0.05,
      f"{r['rapport_extreme']:.3f}" if r["rapport_extreme"] else "None")
    # ⚠⚠ L exposant doit etre NEGATIF : une fenetre plus large moyenne plus, donc ecrase
    # l amplitude. Positif, il faudrait aller regarder avant de publier quoi que ce soit.
    v("l exposant est negatif", r["exposant_taille"] is not None
      and r["exposant_taille"] < 0, f"{r['exposant_taille']}")
    v("... et proche de -0,83", abs(r["exposant_taille"] + 0.83) < 0.03,
      f"{r['exposant_taille']:.4f}")
    # ⚠ Comparable en ordre de grandeur a l effet de la PROFONDEUR (β ~ +1) : c est ce qui
    # justifie de retirer un repere transporte d un instrument a l autre.
    v("son ampleur est comparable a celle de la profondeur",
      abs(r["exposant_taille"]) > 0.5)

    v("une seule taille ne donne pas d exposant", exposant(reel[:1]) is None)
    v("une amplitude nulle est ecartee",
      exposant([{"taille": 256, "amplitude": 0.0},
                {"taille": 1024, "amplitude": 0.05}]) is None)
    v("deux tailles identiques ne donnent pas d exposant",
      exposant([{"taille": 256, "amplitude": 0.1},
                {"taille": 256, "amplitude": 0.2}]) is None)
    v("le resume garde les tailles mesurees", r["tailles"] == [1024, 512, 256]
      or sorted(r["tailles"]) == [256, 512, 1024], str(r["tailles"]))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pile", type=Path, nargs="?", help="répertoire de couches rendues")
    ap.add_argument("--tailles", type=int, nargs="+", default=[1024, 512, 256])
    ap.add_argument("--couche-tracee", type=int, default=80)
    ap.add_argument("--voxel-um", type=float, default=2.4)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.pile or not a.pile.is_dir():
        ap.error("donner un répertoire de couches, ou --verifier")

    mesures = []
    for taille in a.tailles:
        d = profil(a.pile, taille, a.couche_tracee, a.voxel_um)
        mesures.append({"taille": taille,
                        "amplitude": (float(d["amplitude_mediane"]) if d else None),
                        "fenetres": (int(d["windows"]) if d else None)})
        etat = (f"amplitude={mesures[-1]['amplitude']:.4f}  "
                f"fenetres={mesures[-1]['fenetres']}") if d else "⚠ profil non produit"
        print(f"  fenêtre {taille:4d} px : {etat}")

    r = resumer(mesures)
    if r["exposant_taille"] is not None:
        print(f"\n  exposant du relief contre la taille de fenêtre : "
              f"{r['exposant_taille']:+.3f}")
        print(f"  rapport entre les extrêmes : ×{r['rapport_extreme']:.2f}")
        print("  ⚠⚠ un seuil calibré sur une taille de fenêtre ne vaut pas pour une autre")
    if a.json:
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
