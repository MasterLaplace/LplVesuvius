#!/usr/bin/env python3
"""Convertir une tranche de rendu en PNG regardable — et REFUSER si le résultat est vide.

⚠⚠ **Pourquoi ce fichier existe plutôt qu'un appel à `ffmpeg`.** Un `ffmpeg -i tranche.tif
sortie.png` a rendu une image entièrement NOIRE à partir d'un fichier dont la moyenne est de
66 sur 255 et dont 74,5 % des pixels sont non nuls. J'ai failli en conclure que le rendu
n'avait rien produit — c'est la mesure du fichier SOURCE qui l'a démenti.

⭐ La leçon générale : une conversion silencieuse qui rend du noir est indiscernable d'un
calcul qui n'a rien produit. Ce convertisseur **compare** les statistiques de la sortie à
celles de l'entrée et refuse de se taire si elles ne se ressemblent pas.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def stats(a: np.ndarray) -> dict:
    """Ce qu'on doit retrouver après conversion : de la variété, pas une valeur unique."""
    return {"min": int(a.min()), "max": int(a.max()),
            "moyenne": round(float(a.mean()), 2),
            "ecart_type": round(float(a.std()), 2),
            "part_non_nulle": round(float((a > 0).mean()), 4)}


def etirer(a: np.ndarray, bas: float = 0.5, haut: float = 99.5) -> np.ndarray:
    """Étirer le contraste sur les percentiles, en ignorant le fond.

    ⚠⚠ **Un scan tomographique n'utilise qu'une fraction de sa dynamique**, et le fond
    (le vide autour de la surface dépliée) est exactement zéro. Étirer sur `min`/`max`
    bruts laisserait donc le fond tirer la borne basse à 0 et une poussière isolée tirer
    la haute à 255 — c'est-à-dire ne rien étirer du tout. Les percentiles sont pris sur
    les pixels **non nuls** uniquement.
    """
    nz = a[a > 0]
    if nz.size == 0:
        return a
    lo, hi = np.percentile(nz, [bas, haut])
    if hi <= lo:
        return a
    out = np.clip((a.astype(np.float32) - lo) / (hi - lo), 0.0, 1.0) * 255.0
    # ⚠ Le fond reste NOIR : il n'y a pas de surface là, et l'éclaircir inventerait de la
    # matière là où le rendu dit qu'il n'y en a pas.
    out[a == 0] = 0
    return out.astype(np.uint8)


def convertir(source: Path, sortie: Path, etirement: bool = True) -> dict:
    a = np.array(Image.open(source))
    if a.ndim == 3:
        a = a[..., 0]
    avant = stats(a)
    b = etirer(a) if etirement else a
    apres = stats(b)

    # ⚠⚠ LE contrôle : une sortie sans variété n'est pas une image, c'est un rectangle.
    # Il attrape exactement le cas qui vient de se produire — une conversion muette qui
    # rend du noir à partir d'une source pleine.
    degenere = apres["ecart_type"] < 1.0 or apres["max"] == apres["min"]
    perdu = avant["ecart_type"] > 1.0 and apres["ecart_type"] < avant["ecart_type"] * 0.1

    if not (degenere or perdu):
        sortie.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(b).save(sortie)
    return {"source": str(source), "sortie": str(sortie), "avant": avant, "apres": apres,
            "degenere": degenere, "perdu": perdu, "ecrit": not (degenere or perdu)}


def _verifier() -> int:
    ech, ok = [], True

    def v(nom, cond, det=""):
        nonlocal ok
        ech.append((nom, bool(cond), det))
        ok = ok and bool(cond)

    import tempfile
    g = np.random.default_rng(0)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # ── Une image realiste : un fond noir, une zone de matiere a faible dynamique ──
        a = np.zeros((200, 200), np.uint8)
        a[40:170, 30:180] = g.integers(70, 110, (130, 150))
        src = d / "s.tif"; Image.fromarray(a).save(src)
        r = convertir(src, d / "s.png")
        v("l'image est écrite", r["ecrit"] and (d / "s.png").is_file())
        # ⭐ L etirement doit AUGMENTER le contraste : c est son seul travail.
        v("le contraste est étiré", r["apres"]["ecart_type"] > r["avant"]["ecart_type"],
          f"{r['avant']['ecart_type']} → {r['apres']['ecart_type']}")
        v("... et le fond reste noir",
          np.array(Image.open(d / "s.png"))[0, 0] == 0)
        v("... et la part de matière ne change pas",
          abs(r["apres"]["part_non_nulle"] - r["avant"]["part_non_nulle"]) < 0.02)

        # ⚠⚠ Le controle qui porte le fichier : une image VIDE doit etre REFUSEE, pas
        # ecrite. C est le cas qu un ffmpeg silencieux a produit sans rien dire.
        noir = d / "n.tif"; Image.fromarray(np.zeros((60, 60), np.uint8)).save(noir)
        rn = convertir(noir, d / "n.png")
        v("une image entièrement noire est refusée", rn["degenere"] and not rn["ecrit"])
        v("... et le png n'est PAS écrit", not (d / "n.png").exists())
        uni = d / "u.tif"; Image.fromarray(np.full((60, 60), 128, np.uint8)).save(uni)
        v("une image d'une seule teinte est refusée aussi",
          convertir(uni, d / "u.png")["degenere"])

        # ⚠ Et le controle inverse : une image pleine de variete NE doit PAS etre refusee,
        # sinon le garde bloquerait tout et ne distinguerait rien.
        varie = d / "v.tif"
        Image.fromarray(g.integers(0, 255, (80, 80)).astype(np.uint8)).save(varie)
        v("une image variée n'est pas refusée", convertir(varie, d / "v.png")["ecrit"])

        # ⚠⚠ Le percentile porte sur les pixels NON NULS : sinon un grand fond noir tire
        # la borne basse a zero et l etirement ne fait rien.
        gros_fond = np.zeros((300, 300), np.uint8)
        gros_fond[140:160, 140:160] = g.integers(100, 106, (20, 20))
        e = etirer(gros_fond)
        v("un grand fond noir n'empêche pas l'étirement",
          e[150, 150] != gros_fond[150, 150] or e.std() > gros_fond.std(),
          f"{gros_fond.std():.2f} → {e.std():.2f}")

    for nom, o, det in ech:
        if not o:
            print(f"  FAIL {nom}" + (f"  [{det}]" if det else ""))
    print(f"{'ALL PASS' if ok else 'FAILURES'} "
          f"({sum(1 for _, o, _ in ech if not o)} failures, {len(ech)} checks)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?", type=Path)
    ap.add_argument("sortie", nargs="?", type=Path)
    ap.add_argument("--brut", action="store_true", help="sans étirement de contraste")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if a.source is None or a.sortie is None:
        print("usage : tif_en_png.py <source.tif> <sortie.png>", file=sys.stderr)
        return 2
    r = convertir(a.source, a.sortie, etirement=not a.brut)
    av, ap_ = r["avant"], r["apres"]
    print(f"  source : min {av['min']} max {av['max']} moyenne {av['moyenne']} "
          f"écart-type {av['ecart_type']} · {av['part_non_nulle']:.1%} de matière")
    if not r["ecrit"]:
        raison = "la sortie n'a aucune variété" if r["degenere"] else \
                 "la conversion a détruit le contraste de la source"
        print(f"  ⚠⚠ REFUS : {raison} — rien n'est écrit", file=sys.stderr)
        return 3
    print(f"  sortie : écart-type {ap_['ecart_type']} → {a.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
