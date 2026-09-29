"""Les écarts entre plages consécutives de m7 le long des rayons des plans de 301, graine par graine.

⚠⚠ **Ce que cette figure doit rendre évident.** L'histogramme des écarts, avec le pas du rouleau (20 voxels) en repère et les
bandes court, au pas, long : une surface par spire ferait un pic au pas, deux surfaces par spire deux pics dont la somme vaut le pas.

  uv run python src/figures/figure_m7_marque_t_il_une_ou_deux_surfaces_par_spire.py \\
      --sortie docs/images/312_m7_marque_t_il_une_ou_deux_surfaces_par_spire.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "m7_marque_t_il_une_ou_deux_surfaces_par_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 700
LA_BANDE = 600
LE_MAX_VOXELS = 60.0


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"histogrammes": []}
    pas = d["les_constantes"]["le_pas_voxels"]
    cl = d["les_constantes"]["la_classe_de_lhistogramme_voxels"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "histogramme des écarts entre centres de plages consécutives de m7, le long des rayons, de 0 à 60 voxels ; bande "
                   "claire : au pas (15 à 25 voxels) ; trait : le pas, 20 voxels", petit, GRIS)
    for k, g in enumerate(d["les_graines"]):
        col, lig = k % 4, k // 4
        x0, y0 = 50 + col * 318, 72 + lig * 262
        x1, y1 = x0 + 300, y0 + 248
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 8, y0 + 6, f"graine {g['le_rang']}", moyen, ENCRE)
        ecrire(x0 + 8, y0 + 26, f"{g['la_lecture']}, {g['les_ecarts']} écarts", 0, GRIS)
        gx0, gx1, gy0, gy1 = x0 + 12, x1 - 12, y0 + 64, y1 - 30

        def xu(u):
            return gx0 + u / LE_MAX_VOXELS * (gx1 - gx0)

        art.rectangle([xu(0.75 * pas), gy0, xu(1.25 * pas), gy1], fill=PALE)
        art.line([xu(pas), gy0, xu(pas), gy1], fill=ALERTE)
        h = [x for i, x in enumerate(g.get("lhistogramme", [])) if i * cl < LE_MAX_VOXELS]
        haut = max(h) if h else 0
        for i, x in enumerate(h):
            if haut:
                art.rectangle([xu(i * cl) + 1, gy1 - x / haut * (gy1 - gy0), xu((i + 1) * cl) - 1, gy1], fill=BON)
        traces["histogrammes"].append((g["le_rang"], len(h)))
        for u in (0, 20, 40, 60):
            ecrire(int(xu(u)) - 6, gy1 + 4, str(u), 0, GRIS)
        if g.get("lecart_median") is not None:
            ecrire(x0 + 8, y0 + 42, f"médian {_fr(g['lecart_median'])} voxels, au pas {_fr(100 * g['au_pas'], 0)} %", 0, GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que sont les surfaces que m7 marque entre deux spires, ni si le scan les "
                              "voit comme m7 les voit.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_312.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "m7 marque"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "M7 MARQUE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    cl = d["les_constantes"]["la_classe_de_lhistogramme_voxels"]
    v("★★★ un histogramme par graine, sur les classes de 0 à 60 voxels",
      traces["histogrammes"] == [(g["le_rang"], sum(1 for i in range(len(g.get("lhistogramme", []))) if i * cl < LE_MAX_VOXELS))
                                 for g in d["les_graines"]])
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
                   / "312_m7_marque_t_il_une_ou_deux_surfaces_par_spire.png")
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
