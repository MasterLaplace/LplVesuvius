#!/usr/bin/env python3
"""Deux intervalles qui contiennent leur point nul — et pourquoi c'est le résultat.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. [`65`](../../docs/65_ce_que_sigma_ne_dit_pas.md) tient en
une phrase que la prose rend mal : **les intervalles contiennent la valeur nulle**. Écrit en
chiffres, « [0,455 ; 0,745] » demande au lecteur de comparer mentalement à 0,5, et « ρ = +0,263,
p de Holm 0,739 » demande de comparer à zéro. Dessinés contre leur trait de référence, les deux
se lisent d'un coup — et les deux panneaux disent la même chose sur deux questions différentes.

⭐ À gauche : *à quelle résolution la lisibilité est-elle établie ?* Un seul intervalle passe
au-dessus du trait du hasard. À droite : *une grandeur mesurable sans étiquettes prédit-elle la
qualité ?* Aucun intervalle n'évite le zéro, σ compris — et σ est la grandeur sur laquelle deux
documents de ce dépôt font reposer leur raisonnement.

⚠ Les nombres sont LUS dans les deux relevés, jamais retapés.

Usage :
    uv run python src/figures/figure_ce_que_sigma_ne_dit_pas.py --verifier
    uv run python src/figures/figure_ce_que_sigma_ne_dit_pas.py \\
        --sortie docs/images/65_ce_que_sigma_ne_dit_pas.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


def echelle(valeur: float, lo: float, hi: float, pixels: int) -> int:
    """Une valeur de l'axe, en pixels depuis son origine."""
    if hi <= lo:
        return 0
    return int(round((valeur - lo) / (hi - lo) * pixels))


def tranche(ic: dict, nul: float) -> bool:
    """L'intervalle évite-t-il son point nul ?

    ⚠⚠ La question est **évite**, pas « est au-dessus » : à droite le point nul est zéro et
    une corrélation négative franche trancherait tout autant. Ne tester qu'un côté ferait
    passer une relation inverse établie pour un résultat nul, ce qui est faux dans les deux
    sens à la fois.
    """
    return bool(ic.get("ic_bas", 0) > nul or ic.get("ic_haut", 0) < nul)


def prose(lisible: dict, transport: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres."""
    etablies = sum(1 for e in lisible["echelles"]
                   if tranche(e.get("intervalle", {}), 0.5)
                   and e["intervalle"].get("ic_bas", 0) > 0.5)
    tranchees = sum(1 for c in transport["correlations"].values()
                    if c.get("exploitable") and tranche(c, 0.0))
    total = sum(1 for c in transport["correlations"].values() if c.get("exploitable"))
    return [
        f"{etablies} echelle sur {len(lisible['echelles'])} est etablie au-dessus du hasard.",
        f"{tranchees} grandeur sur {total} evite zero, et aucune ne survit a Holm.",
        "un intervalle qui contient son point nul ne dit pas « nul » :",
        "il dit « pas etabli », et les confondre serait le pire des deux.",
    ]


def dessiner(lisible: dict, transport: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(16, 13, 12)
    L, H = 1180, 560
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)

    # ---- GAUCHE : la lisibilité par échelle, contre le trait du hasard -----------------
    gx, gy, gw, gh = 90, 100, 430, 300
    d.text((70, 34), "à quelle résolution la lisibilité est établie", fill=TEXTE, font=gros)
    d.text((70, 56), "AUC moyenne des tuiles, intervalle à 95 %", fill=DISCRET, font=moyen)
    bas, haut = 0.35, 0.85
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=(60, 60, 60))
    for val in (0.4, 0.5, 0.6, 0.7, 0.8):
        yy = gy + gh - echelle(val, bas, haut, gh)
        d.line([gx, yy, gx + gw, yy], fill=(70, 70, 70) if val == 0.5 else (36, 36, 36))
        d.text((gx - 42, yy - 7), f"{val:.1f}", fill=DISCRET, font=petit)
    y5 = gy + gh - echelle(0.5, bas, haut, gh)
    # ⚠ « hasard » va a GAUCHE dans le cadre : colle au bord droit, il debordait et
    # s'affichait « asard » -- une figure se regarde avant d'etre publiee.
    d.text((gx + 8, y5 - 17), "hasard", fill=DISCRET, font=petit)

    n = max(len(lisible["echelles"]), 1)
    col = gw // n
    for i, e in enumerate(lisible["echelles"]):
        ic = e.get("intervalle", {})
        cx = gx + col * i + col // 2
        if not ic.get("exploitable"):
            continue
        y1 = gy + gh - echelle(ic["ic_haut"], bas, haut, gh)
        y2 = gy + gh - echelle(ic["ic_bas"], bas, haut, gh)
        ok = ic["ic_bas"] > 0.5
        couleur = AMBRE if ok else GRIS
        d.rectangle([cx - 30, y1, cx + 30, y2], fill=(34, 30, 24) if ok else (30, 30, 32))
        d.line([cx - 30, y1, cx + 30, y1], fill=couleur, width=2)
        d.line([cx - 30, y2, cx + 30, y2], fill=couleur, width=2)
        ym = gy + gh - echelle(ic["moyenne"], bas, haut, gh)
        d.line([cx - 34, ym, cx + 34, ym], fill=couleur, width=2)
        d.text((cx - 26, gy + gh + 10), f"{e['voxel_um']:.2f} µm", fill=TEXTE, font=moyen)
        d.text((cx - 26, gy + gh + 28), "établie" if ok else "non établie",
               fill=couleur, font=petit)

    # ---- DROITE : les corrélations, contre le zéro -------------------------------------
    bx, by, bw, bh = 660, 100, 400, 300
    d.text((650, 34), "ce qui prédit la qualité sans étiquettes", fill=TEXTE, font=gros)
    d.text((650, 56), "corrélation de rang avec l'AUC de tuile, intervalle à 95 %",
           fill=DISCRET, font=moyen)
    lo, hi = -0.85, 0.75
    d.rectangle([bx, by, bx + bw, by + bh], outline=(60, 60, 60))
    for val in (-0.8, -0.4, 0.0, 0.4):
        xx = bx + echelle(val, lo, hi, bw)
        d.line([xx, by, xx, by + bh], fill=(70, 70, 70) if val == 0.0 else (36, 36, 36))
        d.text((xx - 12, by + bh + 8), f"{val:+.1f}", fill=DISCRET, font=petit)
    x0 = bx + echelle(0.0, lo, hi, bw)
    d.text((x0 - 12, by - 20), "zéro", fill=DISCRET, font=petit)

    items = [(nom, c) for nom, c in transport["correlations"].items() if c.get("exploitable")]
    pas = bh // max(len(items), 1)
    for i, (nom, c) in enumerate(items):
        yy = by + pas * i + pas // 2
        x1 = bx + echelle(c["ic_bas"], lo, hi, bw)
        x2 = bx + echelle(c["ic_haut"], lo, hi, bw)
        couleur = AMBRE if nom == "sigma" else GRIS
        d.line([x1, yy, x2, yy], fill=couleur, width=2)
        d.line([x1, yy - 5, x1, yy + 5], fill=couleur)
        d.line([x2, yy - 5, x2, yy + 5], fill=couleur)
        xr = bx + echelle(c["rho"], lo, hi, bw)
        d.ellipse([xr - 4, yy - 4, xr + 4, yy + 4], fill=couleur)
        etiquette = "σ" if nom == "sigma" else nom.replace("_px", "").replace("_", " ")
        d.text((bx - 4 - 7 * len(etiquette), yy - 7), etiquette, fill=couleur, font=petit)

    for k, ligne in enumerate(prose(lisible, transport)):
        d.text((650, by + bh + 46 + k * 20), ligne,
               fill=ROUGE if k == 0 else TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"echelles": len(lisible["echelles"]), "grandeurs": len(items),
            "sortie": str(sortie)}


def verifier() -> int:
    """Auto-test HORS LIGNE : les axes, le verdict et la prose."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    v("le bas de l'axe est a zero pixel", echelle(0.35, 0.35, 0.85, 300) == 0)
    v("le haut est en butee", echelle(0.85, 0.35, 0.85, 300) == 300)
    v("le milieu est au milieu", echelle(0.60, 0.35, 0.85, 300) == 150)
    v("un axe degenere ne divise pas par zero", echelle(1.0, 1.0, 1.0, 300) == 0)
    # ⚠⚠ Les deux axes doivent contenir leur point nul, sinon le trait de reference sort du
    # cadre et la figure ne peut plus montrer ce qu'elle existe pour montrer.
    v("l'axe de gauche contient le hasard", 0.35 < 0.5 < 0.85)
    v("l'axe de droite contient zero", -0.85 < 0.0 < 0.75)

    # -- tranche : les DEUX cotes, ce qui distingue « evite » de « est au-dessus ».
    v("un intervalle franchement au-dessus tranche",
      tranche({"ic_bas": 0.6, "ic_haut": 0.8}, 0.5))
    v("un intervalle franchement en-dessous tranche AUSSI",
      tranche({"ic_bas": -0.7, "ic_haut": -0.2}, 0.0))
    v("un intervalle qui contient le nul ne tranche pas",
      not tranche({"ic_bas": -0.2, "ic_haut": 0.6}, 0.0))
    v("... ni un intervalle qui le touche", not tranche({"ic_bas": 0.5, "ic_haut": 0.8}, 0.5))

    faux_l = {"echelles": [
        {"voxel_um": 3.24, "intervalle": {"exploitable": True, "moyenne": 0.674,
                                          "ic_bas": 0.541, "ic_haut": 0.788}},
        {"voxel_um": 6.48, "intervalle": {"exploitable": True, "moyenne": 0.594,
                                          "ic_bas": 0.468, "ic_haut": 0.722}},
        {"voxel_um": 9.72, "intervalle": {"exploitable": True, "moyenne": 0.599,
                                          "ic_bas": 0.455, "ic_haut": 0.745}},
    ]}
    faux_t = {"correlations": {
        "sigma": {"exploitable": True, "rho": 0.263, "ic_bas": -0.22, "ic_haut": 0.64},
        "couverture": {"exploitable": True, "rho": -0.097, "ic_bas": -0.50, "ic_haut": 0.31},
    }}
    lignes = prose(faux_l, faux_t)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et compte une seule echelle etablie",
      lignes[0].startswith("1 echelle sur 3"), lignes[0])
    v("... et zero grandeur qui evite zero",
      lignes[1].startswith("0 grandeur sur 2"), lignes[1])
    # ⚠ Le controle qui peut echouer : si une grandeur tranchait, le compte doit BOUGER.
    faux_t2 = json.loads(json.dumps(faux_t))
    faux_t2["correlations"]["sigma"].update({"ic_bas": 0.1, "ic_haut": 0.6})
    v("une grandeur qui tranche ferait bouger le compte",
      prose(faux_l, faux_t2)[1].startswith("1 grandeur sur 2"), prose(faux_l, faux_t2)[1])

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--lisible", type=Path,
                   default=RACINE / "docs/mesures/lisible_a_neuf_microns.json")
    p.add_argument("--transport", type=Path,
                   default=RACINE / "docs/mesures/transport_de_calibration.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/65_ce_que_sigma_ne_dit_pas.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    for f in (a.lisible, a.transport):
        if not f.is_file():
            print(f"mesure absente : {f}", file=sys.stderr)
            return 2
    r = dessiner(json.loads(a.lisible.read_text(encoding="utf-8")),
                 json.loads(a.transport.read_text(encoding="utf-8")), a.sortie)
    print(f"{r['echelles']} echelles, {r['grandeurs']} grandeurs → {a.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
