#!/usr/bin/env python3
"""Deux intervalles qui contiennent leur point nul — et pourquoi c'est le résultat.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. [`65`](../../docs/archive/65_ce_que_sigma_ne_dit_pas.md) tient en
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
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


def lire(lisible_path: Path, transport_path: Path) -> tuple[dict, dict]:
    """Charge les deux mesures nécessaires et valide leur structure minimale."""
    for nom, p in (("lisible", lisible_path), ("transport", transport_path)):
        if not p.is_file():
            raise FileNotFoundError(f"mesure {nom} absente : {p}")
    lisible = json.loads(lisible_path.read_text(encoding="utf-8"))
    transport = json.loads(transport_path.read_text(encoding="utf-8"))
    if not lisible.get("echelles"):
        raise ValueError(f"{lisible_path} ne porte aucune échelle")
    if not transport.get("correlations"):
        raise ValueError(f"{transport_path} ne porte aucune corrélation")
    return lisible, transport


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


def dessiner(lisible: dict, transport: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import ImageDraw

    gros, moyen, petit = police(16, 13, 12)
    L, H = 1180, 560
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    # ---- GAUCHE : la lisibilité par échelle, contre le trait du hasard -----------------
    gx, gy, gw, gh = 90, 100, 430, 300
    ecrire(70, 34, "à quelle résolution la lisibilité est établie", gros, TEXTE)
    ecrire(70, 56, "AUC moyenne des tuiles, intervalle à 95 %", moyen, DISCRET)
    bas, haut = 0.35, 0.85
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=(60, 60, 60))
    for val in (0.4, 0.5, 0.6, 0.7, 0.8):
        yy = gy + gh - echelle(val, bas, haut, gh)
        d.line([gx, yy, gx + gw, yy], fill=(70, 70, 70) if val == 0.5 else (36, 36, 36))
        ecrire(gx - 42, yy - 7, f"{val:.1f}", petit, DISCRET)
    y5 = gy + gh - echelle(0.5, bas, haut, gh)
    # ⚠ « hasard » va a GAUCHE dans le cadre : colle au bord droit, il debordait et
    # s'affichait « asard » -- une figure se regarde avant d'etre publiee.
    ecrire(gx + 8, y5 - 17, "hasard", petit, DISCRET)

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
        ecrire(cx - 26, gy + gh + 10, f"{e['voxel_um']:.2f} µm", moyen, TEXTE)
        ecrire(cx - 26, gy + gh + 28, "établie" if ok else "non établie",
               petit, couleur)

    # ---- DROITE : les corrélations, contre le zéro -------------------------------------
    bx, by, bw, bh = 660, 100, 400, 300
    ecrire(650, 34, "ce qui prédit la qualité sans étiquettes", gros, TEXTE)
    ecrire(650, 56, "corrélation de rang avec l'AUC de tuile, intervalle à 95 %",
           moyen, DISCRET)
    lo, hi = -0.85, 0.75
    d.rectangle([bx, by, bx + bw, by + bh], outline=(60, 60, 60))
    for val in (-0.8, -0.4, 0.0, 0.4):
        xx = bx + echelle(val, lo, hi, bw)
        d.line([xx, by, xx, by + bh], fill=(70, 70, 70) if val == 0.0 else (36, 36, 36))
        ecrire(xx - 12, by + bh + 8, f"{val:+.1f}", petit, DISCRET)
    x0 = bx + echelle(0.0, lo, hi, bw)
    ecrire(x0 - 12, by - 20, "zéro", petit, DISCRET)

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
        ecrire(bx - 4 - 7 * len(etiquette), yy - 7, etiquette, petit, couleur)

    for k, ligne in enumerate(prose(lisible, transport)):
        ecrire(650, by + bh + 46 + k * 20, ligne, moyen,
               ROUGE if k == 0 else TEXTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def verifier() -> int:
    """Auto-test HORS LIGNE : les axes, le verdict, la prose et la figure avec sondes."""
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

    # ---- Validation de lire() et dessiner() hors-ligne avec sondes ----
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        pl = tmp / "lisible.json"
        pt = tmp / "transport.json"
        pl.write_text(json.dumps(faux_l), encoding="utf-8")
        pt.write_text(json.dumps(faux_t), encoding="utf-8")

        l_lu, t_lu = lire(pl, pt)
        v("lire charge les échelles", len(l_lu.get("echelles", [])) == 3)
        v("lire charge les corrélations", len(t_lu.get("correlations", {})) == 2)

        # Sonde 1 : fichier absent
        sonde_manquant = False
        try:
            lire(tmp / "absent.json", pt)
        except FileNotFoundError:
            sonde_manquant = True
        v("sonde : fichier manquant lève FileNotFoundError", sonde_manquant)

        # Sonde 2 : schéma invalide (sans echelles)
        pl_invalide = tmp / "invalide_l.json"
        pl_invalide.write_text(json.dumps({"aucun": 1}), encoding="utf-8")
        sonde_invalide = False
        try:
            lire(pl_invalide, pt)
        except ValueError:
            sonde_invalide = True
        v("sonde : schéma sans échelles lève ValueError", sonde_invalide)

        # Tracé réel de la figure témoin
        cible = tmp / "figure.png"
        out, poses, cadres = dessiner(l_lu, t_lu, cible)
        v("dessiner rend le chemin demandé", out == cible)
        v("le fichier png est produit", cible.is_file() and cible.stat().st_size > 0)
        im = Image.open(cible)
        v("au moins 15 textes sont posés", len(poses) >= 15, f"{len(poses)} textes")
        v("tous les textes sont dans le cadre", textes_hors_cadre(poses, cadres) == [])
        v("aucun texte ne déborde", textes_debordants(poses, im.size[0]) == [])
        v("aucun chevauchement critique", textes_qui_se_recouvrent(poses) == [])

        # Sonde 3 : texte débordant artificiel
        gros, _, _ = police(16, 13, 12)
        poses_trop_larges = poses + [(1150, 50, "texte qui sort largement de l'image a droite", gros)]
        debord = textes_debordants(poses_trop_larges, im.size[0])
        v("sonde : un texte débordant est bien intercepté", len(debord) > 0)

        # Sonde 4 : texte hors cadre
        poses_hors = poses + [(1150, 100, "texte qui sort largement du cadre vers la droite", gros)]
        hors = textes_hors_cadre(poses_hors, cadres)
        v("sonde : un texte hors cadre est bien intercepté", len(hors) > 0)

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
    lisible, transport = lire(a.lisible, a.transport)
    out, _, _ = dessiner(lisible, transport, a.sortie)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"écrit : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
