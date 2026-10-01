"""Sur PHerc0358 : L, le contraste des deux sens de lecture, de chaque nappe de départ, de chaque surface que le critère tient et de chaque surface qu'il refuse.

⚠⚠ **Ce que cette figure doit rendre évident.** Trois rangées sur un même axe de L, l'encre lue les couches croissant d'un côté moins
celle lue de l'autre, en valeur absolue, à la même place : les nappes de départ (le témoin T2), les surfaces tenues H, les surfaces
refusées R avec leur médiane. Un point plein est net, au-delà de deux erreurs types ; un point creux ne l'est pas. Si le critère dit
vrai, les points de H sont à droite de tous ceux de R. C'est la mesure qui décide depuis le second amendement de `410`.

  uv run python src/figures/figure_les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.py \\
      --sortie docs/images/410_les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.png

⚠ Écrite avant qu'une lecture d'encre de PHerc0358 n'existe ; tout ce qu'elle montre vient de la mesure de `410`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
TENUE = (40, 110, 70)
REFUSEE = (150, 60, 50)
DEPART = (60, 80, 150)
L_, H_ = 1200, 640
LA_BANDE = 520
LE_CADRE = (40, 76, 1160, 500)
X0, X1 = 330, 1120
LES_RANGEES = (("N", "nappes de départ, le témoin T2", DEPART, 130), ("H", "tenues par le critère, H", TENUE, 220),
               ("R", "refusées par le critère, R", REFUSEE, 310))
LAXE, LES_LISTES = 340, 384


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v) -> str:
    return "non lue" if v is None else f"{v:g}".replace(".", ",")


def les_d(d: dict, g: str) -> list[tuple[str, float | None]]:
    return [(x["la_surface"], x["la_valeur"]) for x in d["ce_qui_decide"]["les_lectures"][g]]


def les_nets(d: dict, g: str) -> dict[str, bool]:
    return {x["la_surface"]: bool(x.get("net")) for x in d["ce_qui_decide"]["les_lectures"][g]}


def lechelle(d: dict) -> tuple[float, float]:
    """Les bornes de l'axe : tous les D lus et zéro, avec une marge d'un dixième ; ±0,1 si rien n'est lu."""
    tous = [v for g in ("N", "H", "R") for _, v in les_d(d, g) if v is not None] + [0.0]
    lo, hi = min(tous), max(tous)
    if hi - lo < 1e-9:
        return -0.1, 0.1
    m = (hi - lo) / 10.0
    return lo - m, hi + m


def la_position(v: float, lo: float, hi: float) -> int:
    return int(round(X0 + (v - lo) / (hi - lo) * (X1 - X0)))


def le_titre(d: dict) -> str:
    return f"410 sur pherc0358 : {d['le_verdict']['lissue']}".upper()


def la_liste(d: dict, g: str) -> str:
    lus = sorted(((n, v) for n, v in les_d(d, g) if v is not None), key=lambda x: -x[1])
    manquent = [n for n, v in les_d(d, g) if v is None]
    t = " · ".join(f"{n[2:]} {le_nombre(v)}" for n, v in lus)
    return t + (f" · non lues : {len(manquent)}" if manquent else "") if lus else f"non lues : {len(manquent)}"


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    ch = d.get("le_choix_de_lencre") or {}
    issue = lambda k: (d.get(k) or {}).get("le_verdict", {}).get("lissue", "non lue").rpartition(" ; ")[2]  # noqa: E731
    deux = (f"rapporté à côté, qui ne décide rien : l'encre choisit le côté de la graine sur {ch.get('celui_de_la_graine', 0)} des "
            f"{ch.get('lues', 0)} surfaces ; D au jumeau dit, par la graine : {issue('la_regle_amendee_une_fois')}, "
            f"par chaque surface : {issue('la_regle_ecrite_dabord')}")
    trois = "⚠ ce qui n'est PAS établi : que des lettres soient lisibles ; ce que vaut le critère au-delà des deux premiers sauts."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(15, 13, 11)
    poses: list[tuple[int, int, str, object]] = []
    traces = {"points": [], "zero": None, "mediane": None, "rangees": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 18, le_titre(d), gros, ENCRE)
    ecrire(50, 44, "L = |encre lue d'un sens − encre lue de l'autre|, à la même place, loin du bord ; point plein : au-delà de deux erreurs types",
           petit, GRIS)
    art.rectangle(LE_CADRE, outline=TRAIT)
    lo, hi = lechelle(d)
    xz = la_position(0.0, lo, hi)
    traces["zero"] = xz
    art.line([xz, LE_CADRE[1] + 20, xz, LAXE], fill=GRIS, width=1)
    ecrire(xz - 4, LAXE + 6, "0", petit, GRIS)
    ecrire(X0 - 10, LAXE + 6, le_nombre(round(lo, 4)), petit, GRIS)
    ecrire(X1 - 40, LAXE + 6, le_nombre(round(hi, 4)), petit, GRIS)
    r_lus = [v for _, v in les_d(d, "R") if v is not None]
    for k, (g, nom, couleur, y) in enumerate(LES_RANGEES):
        traces["rangees"].append(g)
        ecrire(60, y - 30, nom, moyen, couleur)
        art.line([X0, y, X1, y], fill=TRAIT, width=1)
        nets = les_nets(d, g)
        for n, v in les_d(d, g):
            if v is None:
                continue
            x = la_position(v, lo, hi)
            art.ellipse([x - 6, y - 6, x + 6, y + 6], outline=couleur, fill=couleur if nets[n] else FOND, width=2)
            traces["points"].append((g, n, v, x))
            traces.setdefault("centres", {})[n] = (x, y)
        if g == "R" and r_lus:
            xm = la_position(float(np.median(r_lus)), lo, hi)
            traces["mediane"] = xm
            art.line([xm, y - 18, xm, y + 18], fill=REFUSEE, width=2)
        ecrire(60, LES_LISTES + 28 * k, f"{g} : {la_liste(d, g)}", petit, couleur)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un_, deux_, trois_ = la_bande(d)
    ecrire(50, LA_BANDE + 10, un_, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux_, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois_, moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, [LE_CADRE], traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    lu = lambda n, x, net=True: {"la_surface": n, "la_valeur": x, "net": net}  # noqa: E731
    essai = {"le_verdict": {"lissue": "D de H : 0,1 ; 0,09 ; D de R : de -0,02 à 0,05 ; T2 : 3 sur 3 ; oui"},
             "ce_qui_decide": {"les_lectures": {"N": [lu("N_6", 0.04), lu("N_7", 0.02, False), lu("N_8", -0.01)],
                              "H": [lu("H_6_moins_1", 0.1), lu("H_8_plus_1", 0.09)],
                              "R": [lu(f"R_{i}", x) for i, x in enumerate([-0.02, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, None])]}},
             "le_choix_de_lencre": {"celui_de_la_graine": 2, "lues": 3},
             "la_regle_ecrite_dabord": {"le_verdict": {"lissue": "D de H : 0,01 ; 0,02 ; D de R : de 0 à 0,05 ; T2 : 3 sur 3 ; non"}},
             "la_regle_amendee_une_fois": {"le_verdict": {"lissue": "x ; en partie"}}}
    mesures = [("l'essai", essai)] + ([("la mesure", lire(mesure))] if mesure.exists() else [])
    for quoi, d in mesures:
        tmp = sortie.parent / ".sonde_410.png"
        try:
            _, poses, cadres, traces = dessiner(d, tmp)
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"★★★★ le rendu de {quoi} lève {type(exc).__name__}: {exc}")
            continue
        pts = traces["points"]
        v(f"★★★★ ({quoi}) chaque point lu est dessiné, à droite de zéro si et seulement si son D est positif",
          len(pts) == sum(x is not None for g in ("N", "H", "R") for _, x in les_d(d, g))
          and all((x > traces["zero"]) == (val > 0) or val == 0 for _, _, val, x in pts))
        v(f"★★★★ ({quoi}) l'axe respecte l'ordre des D", all((a[3] - b[3]) * (a[2] - b[2]) >= 0 for a in pts for b in pts))
        v(f"★★★★ ({quoi}) trois rangées, dans l'ordre N, H, R", traces["rangees"] == ["N", "H", "R"])
        v(f"★★★★ ({quoi}) aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
        v(f"★★★★ ({quoi}) aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
        v(f"★★★★ ({quoi}) aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
        manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
        v(f"★★★★ ({quoi}) aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
        v(f"★★★★ ({quoi}) la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
        v(f"★★★★ ({quoi}) elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
        octets = tmp.read_bytes()
        dessiner(d, tmp)
        v(f"★★★★ ({quoi}) le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
        tmp.unlink(missing_ok=True)
    _, _, _, te = dessiner(essai, sortie.parent / ".sonde_410.png")
    pix = Image.open(sortie.parent / ".sonde_410.png").convert("RGB")
    (sortie.parent / ".sonde_410.png").unlink(missing_ok=True)
    v("★★★ le titre LIT la mesure", le_titre(essai) == "410 SUR PHERC0358 : D DE H : 0,1 ; 0,09 ; D DE R : DE -0,02 À 0,05 ; T2 : 3 SUR 3 ; OUI")
    v("★★★★ la médiane de R est au D médian des R lus", te["mediane"] == la_position(0.02, *lechelle(essai)), str(te["mediane"]))
    v("★★★★ une lecture qui manque est dite non lue", la_liste(essai, "R").endswith("· non lues : 1"))
    v("★★★★ la bande compte les choix de l'encre et dit la règle écrite d'abord",
      "sur 2 des 3 surfaces" in la_bande(essai)[1] and la_bande(essai)[1].endswith("par la graine : en partie, par chaque surface : non"),
      la_bande(essai)[1])
    v("★★★★ un point net est plein, un point qui ne l'est pas est creux, lu sur l'image",
      pix.getpixel(te["centres"]["N_7"]) == FOND and pix.getpixel(te["centres"]["N_6"]) == DEPART,
      f"{pix.getpixel(te['centres']['N_7'])} {pix.getpixel(te['centres']['N_6'])}")

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "410_les_premieres_surfaces_tenues_portent_elles_plus_dencre_sur_pherc0358.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
