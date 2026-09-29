"""Le pas médian du premier saut qui croît, côté par côté, avec le départ de 306 et avec le départ pris à la médiane, sur PHerc0358 et sur PHercParis4.

⚠⚠ **Ce que cette figure doit rendre évident.** Chaque côté a deux marques sur l'échelle des pas : un cercle gris pour le saut de
`306`, un disque pour le saut parti de la médiane, reliés quand ils diffèrent. La bande verte pâle est « au pas ». Si les disques
entrent dans la bande là où les cercles en sortaient, le départ faisait poser loin ; s'ils restent où étaient les cercles, c'est `m7`
qui montre la feuille suivante loin. Les côtés d'une nappe refusée, parce que posée dans un bloc, sont marqués d'une croix.

  uv run python src/figures/figure_un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.py \\
      --sortie docs/images/327_un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 620
LA_BANDE = 530
LES_ROULEAUX = (("PHerc0358", ALERTE), ("PHercParis4", BON))
LE_PAS_MAX = 3.0


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"LE DÉPART PRIS À LA MÉDIANE : {v['lissue'].split(' ; ')[-1]} ; {v['k']} graines contre {v['k0']} sur PHercParis4, "
            f"{v['m']} côtés contre {v['m0']} sur PHerc0358").upper()


def les_marques_attendues(d: dict) -> list:
    return [(r, g["le_rang"], c, g["les_sauts"]["le_temoin"]["les_cotes"][c]["le_pas_median_en_pas"],
             g["les_sauts"]["parti_de_la_mediane"]["les_cotes"][c]["le_pas_median_en_pas"])
            for r, _ in LES_ROULEAUX for g in d["les_graines"][r] for c in ("plus", "moins")]


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"marques": [], "ecretes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "le pas médian du premier saut qui croît, par côté ; cercle gris : le départ de 306 ; disque : le départ pris à la "
                   "médiane ; croix : nappe refusée, posée dans un bloc de m7", petit, GRIS)
    for k, (r, col) in enumerate(LES_ROULEAUX):
        x0, y0 = 50 + k * 640, 76
        x1, y1 = x0 + 620, 510
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 12, y0 + 8, r, moyen, ENCRE)
        py0, py1 = y0 + 40, y1 - 50
        px0, px1 = x0 + 60, x1 - 16
        Y = lambda q: py1 - q / LE_PAS_MAX * (py1 - py0)  # noqa: E731
        art.rectangle([px0, Y(1.5), px1, Y(0.5)], fill=PALE)
        for q in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            art.line([px0, Y(q), px1, Y(q)], fill=TRAIT)
            ecrire(x0 + 8, int(Y(q)) - 7, f"{q:g} pas".replace(".", ","), 0, GRIS)
        cotes = [(g, c) for g in d["les_graines"][r] for c in ("plus", "moins")]
        pw = (px1 - px0) / max(1, len(cotes))
        for n, (g, c) in enumerate(cotes):
            xc = px0 + (n + 0.5) * pw
            qt = g["les_sauts"]["le_temoin"]["les_cotes"][c]["le_pas_median_en_pas"]
            qm = g["les_sauts"]["parti_de_la_mediane"]["les_cotes"][c]["le_pas_median_en_pas"]
            for q in (qt, qm):
                if q is not None and not 0.0 <= q <= LE_PAS_MAX:
                    traces["ecretes"] += 1
            if qt is not None and qm is not None and qt != qm:
                art.line([xc, Y(min(LE_PAS_MAX, qt)), xc, Y(min(LE_PAS_MAX, qm))], fill=GRIS, width=2)
            if qt is not None:
                yt = Y(min(LE_PAS_MAX, max(0.0, qt)))
                art.ellipse([xc - 7, yt - 7, xc + 7, yt + 7], outline=GRIS, width=2)
            if g["refusee"]:
                art.line([xc - 5, py1 - 12, xc + 5, py1 - 2], fill=ALERTE, width=2)
                art.line([xc - 5, py1 - 2, xc + 5, py1 - 12], fill=ALERTE, width=2)
            elif qm is not None:
                ym = Y(min(LE_PAS_MAX, max(0.0, qm)))
                art.ellipse([xc - 4, ym - 4, xc + 4, ym + 4], fill=col)
            traces["marques"].append((r, g["le_rang"], c, qt, qm))
            if c == "plus":
                ecrire(int(xc - 4), py1 + 8, f"g{g['le_rang']}", 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : sur quelle feuille tombent les spires posées au pas de PHerc0358.", moyen,
           ALERTE)

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
    tmp = sortie.parent / ".sonde_327.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; il tombe moins souvent", "k": 2, "k0": 4, "m": 7, "m0": 5}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE DÉPART PRIS À LA MÉDIANE : IL TOMBE MOINS SOUVENT ; 2 GRAINES CONTRE 4 SUR "
      "PHERCPARIS4, 7 CÔTÉS CONTRE 5 SUR PHERC0358", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ deux marques par côté, aux pas mesurés", traces["marques"] == les_marques_attendues(d))
    v("★★★ aucune marque n'est écrêtée", traces["ecretes"] == 0, str(traces["ecretes"]))
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
                   / "327_un_saut_parti_de_la_mediane_tombe_t_il_plus_souvent_au_pas.png")
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
