"""Le scan en travers des sauts d'un demi-pas des nappes de m7, et en travers d'une nappe à sa spire suivante.

⚠⚠ **Ce que cette figure doit rendre évident.** Nappe par nappe, le profil moyen du scan du côté bas du saut (u = 0) au côté haut
(u = 1) : un creux au milieu dit deux feuilles, de la matière dit une seule vue par ses deux faces ; et, à côté, le même profil entre
la nappe et sa spire suivante.

  uv run python src/figures/figure_les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.py \\
      --sortie docs/images/304_les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
L_, H_ = 1360, 600


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
    points: list[tuple[float, float]] = []
    traces = {"profils": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 10, y0 + 8, titre, moyen, ENCRE)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "profil moyen du scan brut, chaque profil normé, du côté bas du saut (u = 0) au côté haut (u = 1) ; le témoin "
                   "va de la nappe (u = 0) à sa spire suivante (u = 1)", petit, GRIS)
    U = d["les_u"]
    for k, n in enumerate(d["les_nappes"]):
        x0, y0, x1, y1 = 50 + k * 254, 76, 50 + k * 254 + 244, 470
        panneau(x0, y0, x1, y1, f"graine {n['le_rang']}")
        gx0, gx1, gy0, gy1 = x0 + 14, x1 - 14, y0 + 90, y1 - 60
        ym = (gy0 + gy1) / 2

        def xu(u):
            return gx0 + (u - U[0]) / (U[-1] - U[0]) * (gx1 - gx0)

        art.line([gx0, ym, gx1, ym], fill=TRAIT)
        for u in (0.0, 0.5, 1.0):
            art.line([xu(u), gy0, xu(u), gy1], fill=TRAIT)
        for cle, coul in (("le_profil_en_travers_des_sauts", BON), ("le_profil_du_temoin", BLEU)):
            p = n[cle]
            traces["profils"].append((n["le_rang"], cle, len(p)))
            if len(p) > 1:
                xy = [(xu(u), ym - max(-1.6, min(1.6, v)) * (gy1 - gy0) / 3.4) for u, v in zip(U, p)]
                art.line(xy, fill=coul, width=2)
                points.extend(xy)
        ecrire(x0 + 10, y0 + 30, f"{n['les_sauts_lus']} sauts, {_fr(n['la_taille_mediane_des_sauts_voxels'])} voxels", 0, BON)
        ecrire(x0 + 10, y0 + 46, f"sauts : {n['la_forme']}", 0, BON if n["la_forme"] == "un creux" else GRIS)
        ecrire(x0 + 10, y0 + 62, f"témoin : {n['la_forme_du_temoin']}, pas {_fr(n['le_pas_median_du_temoin_voxels'])}", 0,
               BLEU)
        ecrire(int(xu(0.0)) - 10, gy1 + 6, "u 0", 0, GRIS)
        ecrire(int(xu(1.0)) - 10, gy1 + 6, "u 1", 0, GRIS)
    ecrire(50, 480, "— en travers des sauts", 0, BON)
    ecrire(250, 480, "— de la nappe à sa spire suivante (témoin)", 0, BLEU)

    art.rectangle([0, 500, L_, H_], fill=BANDE)
    ecrire(50, 512, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 534, "⚠ ce qui n'est PAS établi : ce que vaut chaque saut pris seul ; ce que sont les sauts d'un pas entier ; que "
                    "m7 marque bien les faces des feuilles, l'hypothèse qui donne un sens au test.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_304.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "les sauts passent quelque part"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LES SAUTS PASSENT QUELQUE PART", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★ deux profils par nappe, à la longueur mesurée",
      traces["profils"] == [(n["le_rang"], c, len(n[c])) for n in d["les_nappes"]
                            for c in ("le_profil_en_travers_des_sauts", "le_profil_du_temoin")])
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
                   / "304_les_sauts_dun_demi_pas_passent_ils_dune_feuille_a_lautre.png")
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
