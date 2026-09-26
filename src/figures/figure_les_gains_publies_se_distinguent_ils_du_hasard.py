"""Les gains nets publiés de `275` à `289`, contre le hasard : le test du signe, sur les points et sur les blocs.

⚠⚠ **Ce que cette figure doit rendre évident.** Une ligne par tranche testée : le gain net, et la probabilité du test du signe,
en barre sur les points et en carré sur les blocs quand ils sont publiés, sur une échelle logarithmique. Le trait vertical est
le seuil de 0,05 : à droite de lui, le gain se distingue du hasard au seuil déclaré.

  uv run python src/figures/figure_les_gains_publies_se_distinguent_ils_du_hasard.py \\
      --sortie docs/images/290_les_gains_publies_se_distinguent_ils_du_hasard.png
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_gains_publies_se_distinguent_ils_du_hasard.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (196, 200, 204)
L_, H_ = 1360, 640
LE_MAX = 6.0   # l'axe s'arrête à une chance sur un million ; au-delà, la barre touche le bord


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_hauteur(p: float) -> float:
    return min(LE_MAX, -math.log10(max(p, 1e-300)))


def le_titre(d: dict) -> str:
    t = next(x for x in d["les_tranches"] if x["la_tranche"] == "283")
    b = t["sur_les_blocs"]
    return (f"AU DEUXIÈME SAUT DE LA BANDE, {b['les_blocs_qui_montent']} BLOCS MONTENT ET {b['les_blocs_qui_descendent']} "
            f"DESCENDENT : LE HASARD SEUL FERAIT UN ÉCART AU MOINS AUSSI GRAND UNE FOIS SUR {round(1 / b['la_probabilite'])}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"lignes": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "test du signe, binomial exact à une chance sur deux, bilatéral · seuil 0,05 fixé avant le calcul · "
                   "les points d'un bloc ne sont pas indépendants : le test par blocs est celui qui compte", petit, GRIS)
    panneau(50, 80, 1310, 540, "LA PROBABILITÉ QUE LE HASARD SEUL FASSE UN ÉCART AU MOINS AUSSI GRAND, TRANCHE PAR TRANCHE")
    x0, x1 = 560, 1270
    echelle = (x1 - x0) / LE_MAX
    for k in range(int(LE_MAX) + 1):
        x = x0 + k * echelle
        art.line([x, 120, x, 510], fill=TRAIT)
        ecrire(int(x) - 12, 514, "1" if k == 0 else f"10^−{k}", 0, GRIS)
    xs = x0 + -math.log10(d["le_seuil"]) * echelle
    art.line([xs, 116, xs, 510], fill=ALERTE, width=2)
    ecrire(int(xs) + 6, 108, "seuil 0,05", 0, ALERTE)
    for i, t in enumerate(d["les_tranches"]):
        y = 130 + i * 34
        p = t["sur_les_points"]
        ecrire(70, y, f"{t['la_tranche']} · {t['ce_quelle_mesure']}", 0, ENCRE)
        ecrire(420, y, f"{p['les_rates_rendus_justes']} pour {p['les_justes_rendus_rates']}, gain {_fr(p['le_gain_net'])}",
               0, GRIS)
        hp = la_hauteur(p["la_probabilite"])
        art.rectangle([x0, y + 2, x0 + hp * echelle, y + 12], fill=BON if p["sous_le_seuil"] else PALE)
        points.append((x0 + hp * echelle, y + 12))
        hb = None
        if "sur_les_blocs" in t:
            b = t["sur_les_blocs"]
            hb = la_hauteur(b["la_probabilite"])
            xb = x0 + hb * echelle
            art.rectangle([xb - 5, y + 14, xb + 5, y + 24], fill=ENCRE if b["sous_le_seuil"] else GRIS)
            points.append((xb + 5, y + 24))
        traces["lignes"].append((t["la_tranche"], round(hp, 6), None if hb is None else round(hb, 6)))
    ecrire(70, 486, "barre : sur les points, verte sous le seuil · carré : sur les blocs, noir sous le seuil", 0, GRIS)

    art.rectangle([0, 556, L_, H_], fill=BANDE)
    ecrire(50, 568, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 590, "sur le segment 20230702185753, les gains de 275, 276, 279 et 280 se distinguent du hasard ; sur la "
                    "bande, aucun bloc par bloc", moyen, ENCRE)
    ecrire(50, 614, "⚠ ce qui n'est PAS établi : ce qu'une correction vaut au-delà des points notés.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_290.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    t = next(x for x in d["les_tranches"] if x["la_tranche"] == "283")["sur_les_blocs"]
    v("★★★ le titre LIT la mesure", le_titre(d).endswith(f"UNE FOIS SUR {round(1 / t['la_probabilite'])}")
      and f"{t['les_blocs_qui_montent']} BLOCS MONTENT" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(x["la_tranche"], round(la_hauteur(x["sur_les_points"]["la_probabilite"]), 6),
                None if "sur_les_blocs" not in x else round(la_hauteur(x["sur_les_blocs"]["la_probabilite"]), 6))
               for x in d["les_tranches"]]
    v("★★★★ une ligne par tranche, chacune à la probabilité mesurée", traces["lignes"] == attendu)
    passent = {x["la_tranche"] for x in d["les_tranches"] if x["sur_les_points"]["sous_le_seuil"]
               and x["la_tranche"] in ("275", "276", "279", "280")}
    v("★★★★ la phrase du segment dit ce que la mesure dit", passent == {"275", "276", "279", "280"})
    v("★★★★ la phrase de la bande dit ce que la mesure dit", not any(
        x["sur_les_blocs"]["sous_le_seuil"] for x in d["les_tranches"] if "sur_les_blocs" in x
        and x["la_tranche"] in ("281", "283")))
    txt = " ".join(t_ for _, _, t_, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "images" / "290_les_gains_publies_se_distinguent_ils_du_hasard.png")
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
