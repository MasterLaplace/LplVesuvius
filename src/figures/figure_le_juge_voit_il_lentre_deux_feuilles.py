"""Le juge de 301 sur une surface décalée le long de ses normales, d'un pas entier en arrière à un pas entier en avant.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, sur PHercParis4 où la réponse est connue, la part des blocs dont le
tracé humain décalé passe le juge, décalage par décalage : un juge qui voit la feuille tombe au demi-pas et remonte au pas entier ;
un juge qui ne voit que l'empilement reste haut partout. À droite, le Z des nappes de PHerc0358 aux mêmes décalages.

  uv run python src/figures/figure_le_juge_voit_il_lentre_deux_feuilles.py \\
      --sortie docs/images/307_le_juge_voit_il_lentre_deux_feuilles.png

⚠ Tout vient de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_juge_voit_il_lentre_deux_feuilles.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
LES_COULEURS = ((58, 92, 150), (176, 92, 42), (60, 110, 90), (120, 80, 150), (140, 143, 148))
L_, H_ = 1360, 600
LA_BANDE = 500


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def le_nom(x: float) -> str:
    return ("m" if x < 0 else "p") + f"{abs(x):g}".replace(".", "_")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"courbes": []}
    decs = d["les_constantes"]["les_decalages_en_pas"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def axes(x0, y0, x1, y1, bas, haut, repere, etiquette):
        gx0, gx1, gy0, gy1 = x0 + 50, x1 - 20, y0 + 40, y1 - 50

        def xd(v):
            return gx0 + (v - decs[0]) / (decs[-1] - decs[0]) * (gx1 - gx0)

        def yv(v):
            return gy1 - (max(bas, min(haut, v)) - bas) / (haut - bas) * (gy1 - gy0)

        art.line([gx0, gy1, gx1, gy1], fill=TRAIT)
        art.line([gx0, yv(repere), gx1, yv(repere)], fill=ALERTE)
        for v in decs:
            art.line([xd(v), gy0, xd(v), gy1], fill=TRAIT)
            ecrire(int(xd(v)) - 14, gy1 + 6, _fr(v, 2), 0, GRIS)
        ecrire(gx0, gy1 + 24, etiquette, 0, GRIS)
        ecrire(x0 + 8, int(yv(haut)) - 6, _fr(haut, 0), 0, GRIS)
        ecrire(x0 + 8, int(yv(bas)) - 6, _fr(bas, 0), 0, GRIS)
        return xd, yv

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "le tracé ou la nappe décalé le long de ses normales, en pas ; le juge de 301 sans rien y changer, Z ≥ 3 contre "
                   "huit rampes plantées dans ses propres points", petit, GRIS)
    x0, y0, x1, y1 = 50, 72, 660, 486
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 10, y0 + 8, "PHercParis4 : part des 24 blocs dont le tracé décalé passe", moyen, ENCRE)
    xd, yv = axes(x0, y0, x1, y1, 0.0, 1.0, d["les_constantes"]["le_taux_entre_deux"], "décalage (pas)")
    c = d["paris4"]["la_courbe"]
    xy = [(xd(e["le_decalage_en_pas"]), yv(e["le_taux"] if e["le_taux"] is not None else 0.0)) for e in c]
    art.line(xy, fill=BON, width=2)
    for (x, y), e in zip(xy, c):
        art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=BON)
    points.extend(xy)
    traces["courbes"].append(("paris4", len(xy)))

    x0, y0, x1, y1 = 700, 72, 1310, 486
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 10, y0 + 8, "PHerc0358 : Z des nappes croissantes de 305, décalées", moyen, ENCRE)
    zs = [z for n in d["phercs0358"]["les_nappes"] for z in n["les_z"].values() if z is not None]
    bas, haut = min([-10.0] + [10.0 * ((z // 10.0)) for z in zs]), max([30.0] + [10.0 * (z // 10.0 + 1) for z in zs])
    traces["ecretes"] = sum(1 for z in zs if not bas <= z <= haut)
    xd, yv = axes(x0, y0, x1, y1, bas, haut, 3.0, "décalage (pas)")
    for k, n in enumerate(d["phercs0358"]["les_nappes"]):
        col = LES_COULEURS[k % len(LES_COULEURS)]
        xy = [(xd(v), yv(n["les_z"][le_nom(v)])) for v in decs if n["les_z"][le_nom(v)] is not None]
        if len(xy) > 1:
            art.line(xy, fill=col, width=2)
        points.extend(xy)
        traces["courbes"].append((n["le_rang"], len(xy)))
        ecrire(x0 + 70 + 110 * k, y0 + 30, f"graine {n['le_rang']}", 0, col)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que vaut le juge sur un empilement irrégulier, ni sur quelle feuille se "
                              "trouve une surface qui le passe.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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
    tmp = sortie.parent / ".sonde_307.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "le juge juge"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE JUGE JUGE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ aucune courbe n'est écrêtée : chaque Z mesuré tombe entre les bornes de son axe", traces["ecretes"] == 0,
      str(traces["ecretes"]))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [("paris4", len(d["paris4"]["la_courbe"]))] + [
        (n["le_rang"], sum(1 for x in n["les_z"].values() if x is not None)) for n in d["phercs0358"]["les_nappes"]]
    v("★★★ une courbe par surface, un point par décalage mesuré", traces["courbes"] == attendu)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "307_le_juge_voit_il_lentre_deux_feuilles.png")
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
