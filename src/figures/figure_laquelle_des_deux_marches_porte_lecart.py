"""Les deux marches d'un voisinage, séparées, sous les chunks que la décision corrige.

⚠⚠ **Ce que cette figure doit rendre évident.** Pour `(160, 160)` et, en dessous, pour le bloc de `259`, trois cartes du
voisinage : la marche de la spire produite, celle du segment réduit, et leur différence, chacune moins son ancre prise sur les
voisins seuls. Le bloc central est encadré, et chaque chunk que la décision dit glissé y est cerné. On voit laquelle des deux
marches porte ce que la différence montre sous ces chunks. À droite, les médianes famille par famille.

  uv run python src/figures/figure_laquelle_des_deux_marches_porte_lecart.py \\
      --sortie docs/images/272_laquelle_des_deux_marches_porte_lecart.png
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "laquelle_des_deux_marches_porte_lecart.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
FROID = (52, 88, 150)
BLANC = (246, 245, 241)
VIDE = (222, 222, 222)
L_, H_ = 1360, 760
LA_SATURATION = 80.0
LE_BLOC = 16
LES_LIGNES = (("160_160", "(160, 160)"), ("le_bloc_de_259", "le bloc de 259"))
LES_CARTES = (("la_marche_de_la_spire_produite", "la_spire_produite", "la spire produite"),
              ("la_marche_du_segment_reduit", "le_segment_reduit", "le segment réduit"),
              (None, "la_difference", "la différence"))


def _fr(x, n: int = 2) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_teinte(v: float) -> tuple[int, int, int]:
    """Orangé au-dessus de l'ancre, bleu au-dessous, saturé à 80 voxels ; gris là où la marche n'a rien."""
    if not np.isfinite(v):
        return VIDE
    t = max(-1.0, min(1.0, v / LA_SATURATION))
    cible = ALERTE if t > 0 else FROID
    return tuple(int(round(BLANC[k] + abs(t) * (cible[k] - BLANC[k]))) for k in range(3))


def les_cartes(vois: dict) -> dict[str, np.ndarray]:
    """Les trois cartes du voisinage, chacune moins son ancre."""
    f = lambda a: np.array([[np.nan if x is None else float(x) for x in r] for r in a])  # noqa: E731
    p, r = f(vois["la_marche_de_la_spire_produite"]), f(vois["la_marche_du_segment_reduit"])
    a = vois["les_ancres_voxels"]
    return {"la_spire_produite": p - a["la_spire_produite"], "le_segment_reduit": r - a["le_segment_reduit"],
            "la_difference": (p - r) - a["la_difference"]}


def le_titre(d: dict) -> str:
    f = d["les_voisinages"]["160_160"]["juges_justes"]
    return (f"SUR (160, 160), SOUS LES {f['les_chunks']} CHUNKS CORRIGÉS QUE LE JUGE TIENT POUR JUSTES : SPIRE PRODUITE "
            f"{_fr(f['la_part_de_la_spire_produite_mediane_voxels'])}, SEGMENT RÉDUIT "
            f"{_fr(f['la_part_du_segment_reduit_mediane_voxels'])} VOXELS")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cartes": 0, "cernes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · les deux marches d'un seul tenant refaites, leur différence égale "
                   "la publiée · chaque carte moins son ancre prise sur les voisins seuls", petit, GRIS)
    cel = 5
    for k, (cle, nom) in enumerate(LES_LIGNES):
        y0 = 84 + 300 * k
        panneau(50, y0, 880, y0 + 290, f"LE VOISINAGE DE {nom.upper()}")
        vois = d["les_voisinages"][cle]
        cartes = les_cartes(vois)
        for m, (_, cle_c, titre) in enumerate(LES_CARTES):
            x0, yy = 70 + 270 * m, y0 + 50
            ecrire(x0, yy - 16, titre, 0, ENCRE)
            a = cartes[cle_c]
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    art.rectangle([x0 + j * cel, yy + i * cel, x0 + (j + 1) * cel - 1, yy + (i + 1) * cel - 1],
                                  fill=la_teinte(a[i, j]))
            b0, b1 = LE_BLOC * cel, 2 * LE_BLOC * cel
            art.rectangle([x0 + b0 - 1, yy + b0 - 1, x0 + b1, yy + b1], outline=ENCRE)
            for i, j in vois["les_chunks_decides"]:
                cx, cy = x0 + (LE_BLOC + j) * cel, yy + (LE_BLOC + i) * cel
                art.rectangle([cx, cy, cx + cel - 1, cy + cel - 1], outline=ENCRE)
                traces["cernes"] += 1
            traces["cartes"] += 1

    # ── LES MÉDIANES ───────────────────────────────────────────────────────────────────────────────────────────────
    panneau(900, 84, 1310, 674, "LES PARTS, MÉDIANES, VOXELS")
    y = 124
    for cle, nom in (("160_160", "(160, 160)"), ("le_bloc_de_257", "le bloc de 257"), ("le_bloc_de_259", "le bloc de 259")):
        vois = d["les_voisinages"][cle]
        ecrire(916, y, f"{nom} · {vois['les_chunks_corriges']} chunks corrigés", 0, ENCRE)
        y += 20
        for fam, lib in (("juges_justes", "jugés justes"), ("juges_rates", "jugés ratés")):
            f = vois[fam]
            if not f.get("les_chunks"):
                ecrire(930, y, f"{lib} : aucun", 0, GRIS)
            else:
                ecrire(930, y, f"{lib} · {f['les_chunks']} · écart {_fr(f['lecart_median_voxels'])}", 0, GRIS)
                y += 16
                ecrire(944, y, f"spire produite {_fr(f['la_part_de_la_spire_produite_mediane_voxels'])} · "
                               f"segment réduit {_fr(f['la_part_du_segment_reduit_mediane_voxels'])}", 0, ENCRE)
            y += 22
        y += 16
    ecrire(916, y + 10, "une part : ce que cette marche apporte", 0, GRIS)
    ecrire(916, y + 26, "à l'écart, comptée du côté de l'écart", 0, GRIS)
    for s, (lib, v) in enumerate((("−80", -80.0), ("0", 0.0), ("+80", 80.0))):
        xs = 916 + 90 * s
        art.rectangle([xs, y + 56, xs + 24, y + 70], fill=la_teinte(v), outline=TRAIT)
        ecrire(xs + 30, y + 56, lib, 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 690, L_, H_], fill=BANDE)
    ecrire(50, 700, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 722, "⚠ ce qui n'est PAS établi : pourquoi une marche glisse ; si la spire produite est juste là où sa marche "
                    "porte l'écart.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_272.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    f = d["les_voisinages"]["160_160"]["juges_justes"]
    v("★★★ le titre LIT la mesure", f"SPIRE PRODUITE {_fr(f['la_part_de_la_spire_produite_mediane_voxels'])}," in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ chaque chunk corrigé est cerné sur chacune des trois cartes de sa ligne",
      traces["cernes"] == 3 * sum(len(d["les_voisinages"][c]["les_chunks_decides"]) for c, _ in LES_LIGNES)
      and traces["cartes"] == 3 * len(LES_LIGNES), str(traces))
    c = les_cartes(d["les_voisinages"]["160_160"])
    ecart = np.nanmax(np.abs(c["la_spire_produite"] - c["le_segment_reduit"] - c["la_difference"]
                             - (d["les_voisinages"]["160_160"]["les_ancres_voxels"]["la_difference"]
                                - d["les_voisinages"]["160_160"]["les_ancres_voxels"]["la_spire_produite"]
                                + d["les_voisinages"]["160_160"]["les_ancres_voxels"]["le_segment_reduit"])))
    v("★★★★ la carte de la différence est bien celle des deux marches, aux ancres près", ecart < 0.02, str(ecart))
    v("★★★ la teinte sature à 80 voxels et garde son signe",
      la_teinte(200.0) == la_teinte(80.0) == ALERTE and la_teinte(-80.0) == FROID and la_teinte(float("nan")) == VIDE)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "272_laquelle_des_deux_marches_porte_lecart.png")
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
