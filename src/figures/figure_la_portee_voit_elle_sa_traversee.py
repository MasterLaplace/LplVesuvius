"""La portée voit-elle sa traversée : le profil de `235` à ses coupes, et chaque découpage publié contre la portée qui voit.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LE PROFIL de `235` coupe par coupe, contre le demi-feuillet :
les coupes au-delà, les traversées d'un seul tenant et leur durée possible, et la suite de coupes qui les évite toutes —
son plus grand écart est la portée qu'il ne faut pas atteindre. En bas, LES DÉCOUPAGES publiés : le plus grand écart de
chacun, contre la portée qui voit et contre la portée de `239` — c'est le panneau qui conclut.

  uv run python src/figures/figure_la_portee_voit_elle_sa_traversee.py \\
      --json docs/mesures/la_portee_voit_elle_sa_traversee.json \\
      --sortie docs/images/245_la_portee_voit_elle_sa_traversee.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURES = RACINE / "docs" / "mesures"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
TEINTE = (240, 222, 208)
L_, H_ = 1360, 1000


def _fr(x, n: int = 4) -> str:
    """Un nombre en français, le moins en signe typographique."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_portee_voit_elle_sa_traversee.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("le_verdict", "le_profil_de_235", "les_traversees", "les_decoupages", "le_demi_feuillet"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not d["les_traversees"]:
        return "LE PROFIL DE 235 N'A AUCUNE TRAVERSÉE"
    if v["la_portee_qui_voit"] is None:
        return "LA DERNIÈRE COUPE DE 235 EST AU-DELÀ : TOUTE PORTÉE LA VOIT"
    if v["la_portee_voit"]:
        return f"À LA PORTÉE DE {v['la_portee_de_239']}, TOUTE SUITE DE COUPES DE 235 VOIT SA TRAVERSÉE"
    return (f"À LA PORTÉE DE {v['la_portee_de_239']}, ON PEUT COUPER LE PROFIL DE 235 SANS VOIR SA TRAVERSÉE : IL FAUT "
            f"{v['la_portee_qui_voit']} RANGS")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    v = d["le_verdict"]
    demi = float(d["le_demi_feuillet"])
    prof = d["le_profil_de_235"]
    debut = int(d["le_debut_de_laile"])
    fin = int(prof[-1]["la_coupe"])
    au_dela = [p for p in prof if abs(float(p["le_cumul_en_voxels"])) >= demi]
    permises = [debut] + [int(p["la_coupe"]) for p in prof if abs(float(p["le_cumul_en_voxels"])) < demi]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"la portée de 239 est tirée de la première à la dernière coupe de 235 au-delà du demi-feuillet ; "
                   f"entre les deux, le cumul repasse en deçà", petit, GRIS)

    # ── PANNEAU 1 · LE PROFIL DE 235 ────────────────────────────────────────────────────────
    panneau(50, 84, 1310, 520, f"LE PROFIL DE 235 · le cumul coupe après coupe, depuis la rangée {debut}")
    AX0, AX1 = 130, 1270

    def AX(r):
        return AX0 + (AX1 - AX0) * (float(r) - debut) / max(1.0, float(fin - debut))
    VM = max([abs(float(p["le_cumul_en_voxels"])) for p in prof] + [demi]) + 6.0
    YM, YH = 220, 110

    def AY(x):
        return YM - YH * float(x) / VM
    for t in d["les_traversees"]:
        art.rectangle([AX(t["avant"]), AY(VM), AX(t["jusqua"]), AY(-VM)], fill=TEINTE)
    for x_ in (-demi, demi):
        art.line([AX0 - 6, AY(x_), AX1 + 6, AY(x_)], fill=ALERTE, width=1)
    art.line([AX0 - 6, AY(0), AX1 + 6, AY(0)], fill=GRIS, width=1)
    ecrire(72, AY(demi) - 7, f"{_fr(demi)}", 0, ALERTE)
    ecrire(72, AY(0) - 7, "0", 0, GRIS)
    ecrire(72, AY(-demi) - 7, f"−{_fr(demi)}", 0, ALERTE)
    pts = [(AX(debut), AY(0.0))] + [(AX(p["la_coupe"]), AY(p["le_cumul_en_voxels"])) for p in prof]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        for j in range(0, 20, 2):
            art.line([xa + (xb - xa) * j / 20, ya + (yb - ya) * j / 20,
                      xa + (xb - xa) * (j + 1) / 20, ya + (yb - ya) * (j + 1) / 20], fill=CONTRE, width=2)
    n_p = 0
    for p, (x_, y_) in zip(prof, pts[1:]):
        coul = ALERTE if p in au_dela else CONTRE
        r_ = 5 if p in au_dela else 3
        art.ellipse([x_ - r_, y_ - r_, x_ + r_, y_ + r_], fill=coul)
        points.append((x_, y_))
        n_p += 1
    traces["profil"] = n_p
    for p in au_dela:
        ecrire(AX(p["la_coupe"]) - 18, AY(p["le_cumul_en_voxels"]) + 8, _fr(p["le_cumul_en_voxels"]), 0, ALERTE)
    # la suite de coupes qui évite toutes les traversées
    YS = 378
    ecrire(72, YS - 30, "la suite de coupes de 235 qui évite toute coupe au-delà :", 0, GRIS)
    art.line([AX(debut), YS, AX(fin), YS], fill=TRAIT, width=1)
    pire = max(zip(permises[:-1], permises[1:]), key=lambda ab: ab[1] - ab[0])
    art.line([AX(pire[0]), YS, AX(pire[1]), YS], fill=ALERTE, width=4)
    for c in permises:
        art.line([AX(c), YS - 7, AX(c), YS + 7], fill=CONTRE, width=2)
    traces["permises"] = len(permises)
    ecrire((AX(pire[0]) + AX(pire[1])) / 2 - 60, YS + 12, f"son plus grand écart : {pire[1] - pire[0]} rangées", 0,
           ALERTE)
    YT = 448
    ecrire(72, YT - 30, "chaque traversée : au moins de sa première à sa dernière coupe, au plus d'une voisine à l'autre",
           0, GRIS)
    for t in d["les_traversees"]:
        art.line([AX(t["avant"]), YT, AX(t["jusqua"]), YT], fill=TEINTE, width=8)
        art.line([AX(t["de"]), YT, max(AX(t["a"]), AX(t["de"]) + 3), YT], fill=ALERTE, width=8)
    for c in sorted({debut, fin} | {int(p["la_coupe"]) for p in au_dela}):
        ecrire(AX(c) - 9, 478, f"{c}", 0, ALERTE if c in {int(p["la_coupe"]) for p in au_dela} else GRIS)

    # ── PANNEAU 2 · LES DÉCOUPAGES ──────────────────────────────────────────────────────────
    panneau(50, 536, 1310, 800, "LES DÉCOUPAGES PUBLIÉS · le plus grand écart entre deux coupes voisines")
    dcs = d["les_decoupages"]
    BX0, BX1 = 330, 1200
    EM = max([int(x["le_plus_grand_ecart"]) for x in dcs] + [int(v["la_portee_de_239"])]) + 5

    def BX(e):
        return BX0 + (BX1 - BX0) * float(e) / EM
    y0, pas_ = 590, 34
    for i, x in enumerate(dcs):
        y = y0 + i * pas_
        coul = BON if x["voit"] else ALERTE
        art.rectangle([BX(0), y, BX(x["le_plus_grand_ecart"]), y + 18], fill=coul)
        ecrire(72, y + 2, f"{x['la_tranche']} · {x['la_boucle']}", 0, ENCRE)
        ecrire(BX(x["le_plus_grand_ecart"]) - 26, y + 2, f"{x['le_plus_grand_ecart']}", 0, FOND)
        points.append((BX(x["le_plus_grand_ecart"]), y + 18))
    traces["decoupages"] = len(dcs)
    yb = y0 + len(dcs) * pas_
    if v["la_portee_qui_voit"] is not None:
        art.line([BX(v["la_portee_qui_voit"]), y0 - 12, BX(v["la_portee_qui_voit"]), yb], fill=BON, width=2)
        ecrire(BX(v["la_portee_qui_voit"]) - 70, yb + 6, f"la portée qui voit : {v['la_portee_qui_voit']}", 0, BON)
    art.line([BX(v["la_portee_de_239"]), y0 - 12, BX(v["la_portee_de_239"]), yb], fill=ALERTE, width=2)
    ecrire(BX(v["la_portee_de_239"]) + 6, yb + 6, f"la portée de 239 : {v['la_portee_de_239']}", 0, ALERTE)
    ecrire(72, 772, "vert : ne laisse pas passer une traversée comme celles de 235 ; brun : peut la laisser passer",
           0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {v['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    tr = d["les_traversees"]
    if tr:
        la = max(tr, key=lambda t: t["au_plus"])
        ecrire(50, 856, f"★ {len(tr)} traversées d'un seul tenant, et non une : la plus longue dure au plus "
                        f"{la['au_plus']} rangées, des coupes {la['avant']} à {la['jusqua']}.", moyen, ENCRE)
    aveugles = [f"{x['la_tranche']} ({x['le_plus_grand_ecart']})" for x in dcs if not x["voit"]]
    if aveugles:
        ecrire(50, 882, f"★ coupent trop large pour voir une traversée comme celles de 235 : {', '.join(aveugles)}.",
               moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : si ces boucles restent dessous à la portée qui voit, ni une traversée "
                    "plus brève ailleurs.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(json_path: Path, sortie: Path) -> int:
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

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_245.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    base = {"le_verdict": {"la_portee_de_239": 40, "la_portee_qui_voit": 29, "la_portee_voit": False}}
    tous = [le_titre({**base, "les_traversees": []}),
            le_titre({**base, "les_traversees": [1], "le_verdict": {**base["le_verdict"], "la_portee_qui_voit": None}}),
            le_titre({**base, "les_traversees": [1], "le_verdict": {**base["le_verdict"], "la_portee_voit": True}}),
            le_titre({**base, "les_traversees": [1]})]
    v("★★★★ les quatre titres possibles sont distincts", len(set(tous)) == 4)
    v("★★★ le titre LIT le verdict", ("SANS VOIR" in le_titre(d)) == (not d["le_verdict"]["la_portee_voit"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque coupe de 235 a son point, et chaque découpage sa barre",
      traces.get("profil") == len(d["le_profil_de_235"]) and traces.get("decoupages") == len(d["les_decoupages"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le verdict, la portée qui voit, la portée de 239, et ce qui n'est PAS établi",
      d["le_verdict"]["ce_qui_reste_a_mesurer"] in txt
      and f"la portée qui voit : {d['le_verdict']['la_portee_qui_voit']}" in txt
      and f"la portée de 239 : {d['le_verdict']['la_portee_de_239']}" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path, default=MESURES / "la_portee_voit_elle_sa_traversee.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "245_la_portee_voit_elle_sa_traversee.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
