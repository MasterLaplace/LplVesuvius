"""Autour des graines 1 à 3, la longueur des plages de m7 sous les sommets où deux tours publiés se recouvrent et sous ceux où ils sont séparés : la répartition sur toutes les paires, et le rapport des médianes paire par paire.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque longueur de plage en voxels du niveau 2, la part des sommets
recouverts (orange) et séparés (gris) : si les barres orange étaient décalées vers les longueurs doubles, `m7` verrait deux feuilles collées
sous le recouvrement. À droite, le rapport des longueurs médianes de chaque paire, et les deux seuils de la règle.

  uv run python src/figures/figure_sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.py \\
      --sortie docs/images/342_sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.png

⚠ Tout vient de la mesure de `342`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
GRIS_BARRE = (170, 172, 176)
L_, H_ = 1360, 580
LA_BANDE = 490
LES_LONGUEURS = (1, 2, 3, 4, 5, 6, 7)
LE_MAX_PART = 0.8
LE_MAX_RAPPORT = 2.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_parts(d: dict, groupe: str) -> dict:
    """La part des sommets du groupe dont la plage a chaque longueur ; la dernière longueur regroupe toutes les plus longues."""
    c = {x: 0 for x in LES_LONGUEURS}
    for p in d["les_paires"]:
        for k, n in p[groupe]["les_longueurs_comptees"].items():
            c[min(int(k), LES_LONGUEURS[-1])] += n
    tot = sum(c.values())
    return {x: (n / tot if tot else 0.0) for x, n in c.items()}


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    r, s = les_parts(d, "les_recouverts"), les_parts(d, "les_separes")
    f_ = lambda x: f"{x * 100:.0f}"  # noqa: E731
    return (f"sous le recouvrement, {f_(r[3])} % des plages de m7 ont 3 voxels, contre {f_(s[3])} % où les tours sont "
            f"séparés").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "points": [], "ecretes": 0, "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "orange : les sommets où les deux tours publiés se recouvrent ; gris : ceux où ils sont séparés ; autour des graines 1 à 3",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 820, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des sommets selon la longueur de leur plage de m7 (voxels du niveau 2)", moyen, ENCRE)
    gy0, gy1 = y0 + 50, y1 - 40
    for q in (0.2, 0.4, 0.6, 0.8):
        yq = gy1 - q / LE_MAX_PART * (gy1 - gy0)
        art.line([x0 + 50, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, f"{int(q * 100)} %", 0, GRIS)
    r, s = les_parts(d, "les_recouverts"), les_parts(d, "les_separes")
    for n, x in enumerate(LES_LONGUEURS):
        xa = x0 + 80 + n * 100
        for dx, part, col, cle in ((0, r[x], ALERTE, "recouverts"), (32, s[x], GRIS_BARRE, "separes")):
            if not 0 <= part <= LE_MAX_PART:
                traces["ecretes"] += 1
            h = min(LE_MAX_PART, part)
            art.rectangle([xa + dx, gy1 - h / LE_MAX_PART * (gy1 - gy0), xa + dx + 28, gy1], fill=col)
            traces["barres"].append((cle, x, round(part, 6)))
            traces["rectangles"].append((0, xa + dx, xa + dx + 28))
        ecrire(int(xa + 20), gy1 + 8, f"{x}" if x < LES_LONGUEURS[-1] else f"{x} et +", 0, ENCRE)

    x0, y0, x1, y1 = 850, 76, 1310, 470
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "le rapport des longueurs médianes, paire par paire", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 28, "lignes : 1,2 (un tour mal posé) et 1,5 (deux feuilles collées)", 0, ALERTE)
    for q in (0.5, 1.0, 1.5, 2.0):
        yq = gy1 - q / LE_MAX_RAPPORT * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=TRAIT)
        ecrire(x0 + 10, int(yq) - 7, f"{q:g}".replace(".", ","), 0, GRIS)
    for q in (1.2, 1.5):
        yq = gy1 - q / LE_MAX_RAPPORT * (gy1 - gy0)
        art.line([x0 + 40, yq, x1 - 10, yq], fill=ALERTE, width=2)
    for n, p in enumerate(d["les_paires"]):
        if p["le_rapport"] is None:
            continue
        cx = x0 + 60 + n * 21
        cy = gy1 - min(LE_MAX_RAPPORT, p["le_rapport"]) / LE_MAX_RAPPORT * (gy1 - gy0)
        if p["le_rapport"] > LE_MAX_RAPPORT:
            traces["ecretes"] += 1
        art.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=ENCRE)
        traces["points"].append((p["le_rang"], tuple(p["les_tours"]), p["le_rapport"]))
        traces["rectangles"].append((1, cx - 5, cx + 5))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : que m7 sépare deux feuilles collées ; ses plages ont ici toutes 2 à 4 voxels.",
           moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_342.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    for p in autre["les_paires"]:
        p["les_recouverts"]["les_longueurs_comptees"] = {"7": 10}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("SOUS LE RECOUVREMENT, 0 % DES PLAGES"), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    tot = {g: sum(n for p in d["les_paires"] for n in p[g]["les_longueurs_comptees"].values()) for g in ("les_recouverts", "les_separes")}
    trois = {g: sum(p[g]["les_longueurs_comptees"].get("3", 0) for p in d["les_paires"]) / tot[g] for g in tot}
    v("★★★ la barre de 3 voxels est la part comptée dans la mesure",
      dict(((c, x), p) for c, x, p in traces["barres"])[("recouverts", 3)] == round(trois["les_recouverts"], 6)
      and dict(((c, x), p) for c, x, p in traces["barres"])[("separes", 3)] == round(trois["les_separes"], 6))
    long_ = {g: sum(n for p in d["les_paires"] for k, n in p[g]["les_longueurs_comptees"].items() if int(k) >= 7) / tot[g] for g in tot}
    v("★★★ la dernière barre regroupe toutes les plages de 7 voxels et plus",
      dict(((c, x), p) for c, x, p in traces["barres"])[("recouverts", 7)] == round(long_["les_recouverts"], 6)
      and dict(((c, x), p) for c, x, p in traces["barres"])[("separes", 7)] == round(long_["les_separes"], 6))
    v("★★★ les parts de chaque groupe somment à un", all(abs(sum(p for c, _, p in traces["barres"] if c == g) - 1.0) < 1e-4
                                                     for g in ("recouverts", "separes")))
    v("★★★ un point par paire mesurable, à son rapport", traces["points"] == [(p["le_rang"], tuple(p["les_tours"]), p["le_rapport"])
                                                                          for p in d["les_paires"] if p["le_rapport"] is not None])
    v("★★★ rien n'est écrêté", traces["ecretes"] == 0, str(traces["ecretes"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "342_sous_le_recouvrement_m7_voit_il_deux_feuilles_collees.png")
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
