"""Sous la marche de `275`, sur le segment `20230702185753` : l'ancre de `275`, l'ancre nord-sud et l'ancre est-ouest.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, sur les points : les ratés rendus justes et les justes rendus ratés,
pour les trois ancres, sur les mêmes blocs décidés. À droite, bloc par bloc : les blocs qui montent et ceux qui descendent. Sous chaque paire, le gain net
et la probabilité du test du signe de `290`.

  uv run python src/figures/figure_lancre_nord_sud_garde_t_elle_le_gain_du_segment.py \\
      --sortie docs/images/293_lancre_nord_sud_garde_t_elle_le_gain_du_segment.png
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
LA_MESURE = (RACINE / "docs" / "mesures"
             / "lancre_nord_sud_garde_t_elle_le_gain_du_segment.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 540
LES_VOISINAGES = (("avec_lancre_de_275_sur_les_memes_blocs", "l'ancre de 275"), ("avec_lancre_nord_sud", "l'ancre nord-sud"),
                  ("avec_lancre_est_ouest_sur_les_memes_blocs", "l'ancre est-ouest"))


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def _p(x: float) -> str:
    return f"{x:.3g}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def le_titre(d: dict) -> str:
    t, n, e = (d[k]["le_test"]["sur_les_points"]["le_gain_net"] for k in (
        "avec_lancre_de_275_sur_les_memes_blocs", "avec_lancre_nord_sud", "avec_lancre_est_ouest_sur_les_memes_blocs"))
    return (f"SOUS LA MARCHE DE 275, LE GAIN NET SUR LES POINTS VAUT {_fr(t)} AVEC L'ANCRE DE 275, {_fr(n)} AVEC L'ANCRE "
            f"NORD-SUD ET {_fr(e)} AVEC L'ANCRE EST-OUEST")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"20230702185753 · premier saut · les blocs de 275 où l'ancre nord-sud existe · aucune pile rendue · "
                   "test du signe de 290, seuil 0,05 · le juge ne sert qu'à noter", petit, GRIS)
    panneaux = ((50, "SUR LES POINTS", "sur_les_points", ("les_rates_rendus_justes", "les_justes_rendus_rates"),
                 ("ratés rendus justes", "justes rendus ratés")),
                (690, "BLOC PAR BLOC", "sur_les_blocs", ("les_blocs_qui_montent", "les_blocs_qui_descendent"),
                 ("blocs qui montent", "blocs qui descendent")))
    for x0p, titre, cle, (c1, c2), (l1, l2) in panneaux:
        panneau(x0p, 80, x0p + 620, 420, titre)
        vmax = max([d[v]["le_test"][cle][c] for v, _ in LES_VOISINAGES for c in (c1, c2)] + [1])
        base, haut = 340, 190
        for k, (v, nom) in enumerate(LES_VOISINAGES):
            t = d[v]["le_test"][cle]
            x0 = x0p + 50 + k * 190
            for j, (c, coul) in enumerate(((c1, BON), (c2, ALERTE))):
                h = t[c] / vmax * haut
                x = x0 + j * 60
                art.rectangle([x, base - h, x + 48, base], fill=coul)
                traces["barres"].append((cle, v, c, t[c]))
                points.append((x + 48, base - h))
                ecrire(x + 4, int(base - h) - 18, str(t[c]), 0, ENCRE)
            art.line([x0 - 8, base, x0 + 120, base], fill=GRIS)
            ecrire(x0, base + 8, nom, 0, ENCRE)
            ecrire(x0, base + 26, f"probabilité {_p(t['la_probabilite'])}", 0, ENCRE if t["sous_le_seuil"] else GRIS)
        ecrire(x0p + 90, 118, f"■ {l1}", 0, BON)
        ecrire(x0p + 250, 118, f"■ {l2}", 0, ALERTE)

    art.rectangle([0, 436, L_, H_], fill=BANDE)
    ecrire(50, 448, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    n_, e_ = d["avec_lancre_nord_sud"]["les_reunis"], d["avec_lancre_est_ouest_sur_les_memes_blocs"]["les_reunis"]
    ecrire(50, 470, f"le calcul avec l'ancre de 275 redonne 275 bloc par bloc ; les ancres nord-sud et est-ouest corrigent "
                    f"{n_['les_points_corriges']} et {e_['les_points_corriges']} points au lieu de "
                    f"{d['avec_lancre_de_275_sur_les_memes_blocs']['les_reunis']['les_points_corriges']}", moyen, ENCRE)
    ecrire(50, 494, "⚠ ce qui n'est PAS établi : une ancre pour la bande ; pourquoi une direction serait pire que l'autre.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_293.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    n = d["avec_lancre_nord_sud"]["le_test"]["sur_les_points"]["le_gain_net"]
    e = d["avec_lancre_est_ouest_sur_les_memes_blocs"]["le_test"]["sur_les_points"]["le_gain_net"]
    v("★★★ le titre LIT la mesure", f"{_fr(n)} AVEC L'ANCRE NORD-SUD ET {_fr(e)} AVEC L'ANCRE EST-OUEST" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ une barre par compte, chacune au compte mesuré", len(traces["barres"]) == 12 and all(
        val == d[vv]["le_test"][cle][c] for cle, vv, c, val in traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "293_lancre_nord_sud_garde_t_elle_le_gain_du_segment.png")
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
