"""Ce que le juge voyait sous chaque point que la décision corrige, contre ce que la marche y lisait.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, chaque point corrigé : en abscisse l'erreur que le juge lui donnait
avant, en ordonnée l'écart que la marche lisait sous lui. Un point est juste avant dans la bande verticale, juste après dans la
bande diagonale. Les justes rendus ratés sont en haut, près de l'axe vertical : le juge ne les voyait presque pas décalés, la
marche lisait une glissade. À droite, le décalage jugé du côté où la marche corrige, famille par famille, contre le témoin.

  uv run python src/figures/figure_les_points_corriges_etaient_ils_decales.py \\
      --sortie docs/images/271_les_points_corriges_etaient_ils_decales.png
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
from les_points_corriges_etaient_ils_decales import LE_QUART_DE_PAS, le_decalage_juge  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_points_corriges_etaient_ils_decales.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (228, 232, 236)
SOMBRE = (90, 94, 100)
L_, H_ = 1360, 660
LES_CLASSES = (("rendu_juste", "ratés rendus justes", BON), ("rendu_rate", "justes rendus ratés", ALERTE),
               ("reste_rate", "ratés restés ratés", SOMBRE), ("reste_juste", "justes restés justes", GRIS))


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


def les_points(d: dict) -> list[tuple[str, dict]]:
    return [(n, p) for n, v in d["les_voisinages"].items() for p in v["les_points"]]


def le_titre(d: dict) -> str:
    f = d["les_reunis"]["rendu_rate"]
    return (f"LES {f['les_points']} JUSTES RENDUS RATÉS : LE JUGE LES VOYAIT À {_fr(f['le_decalage_juge_median_voxels'])} "
            f"VOXELS EN MÉDIANE, LA MARCHE LISAIT {_fr(f['lecart_lu_median_voxels'])} SOUS EUX")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    marques: list[tuple[float, float]] = []
    traces = {"points": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · les neuf voisinages de 265 et 270 · l'ancre des voisins et la décision "
                   "de 264, recalculées, redonnent leurs comptes publiés", petit, GRIS)
    demi = 36.0

    # ── PANNEAU 1 · CHAQUE POINT CORRIGÉ ───────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 560, "L'ERREUR JUGÉE AVANT, CONTRE L'ÉCART LU SOUS LE POINT, VOXELS")
    x0, x1, y0, y1 = 110, 670, 130, 500
    emin, emax, ey = -200.0, 100.0, 100.0
    X = lambda e: x0 + (x1 - x0) * (e - emin) / (emax - emin)  # noqa: E731
    Y = lambda c: y1 - (y1 - y0) * (c + ey) / (2 * ey)  # noqa: E731
    art.rectangle([X(-demi), y0, X(demi), y1], fill=PALE)
    haut = emax - demi   # la bande diagonale s'arrête là où son bord droit sort du cadre
    art.polygon([(X(-ey - demi), Y(-ey)), (X(-ey + demi), Y(-ey)), (X(haut + demi), Y(haut)), (X(haut - demi), Y(haut))],
                outline=TRAIT)
    art.line([X(-ey), Y(-ey), X(emax), Y(emax)], fill=TRAIT)
    art.line([X(0), y0, X(0), y1], fill=TRAIT)
    art.line([x0, Y(0), x1, Y(0)], fill=TRAIT)
    for t in (-144, -72, 0, 72):
        ecrire(X(t) - 10, y1 + 6, _fr(t), 0, GRIS)
    for t in (-72, 0, 72):
        ecrire(x0 - 34, Y(t) - 7, _fr(t), 0, GRIS)
    ecrire(X(-demi) + 4, y0 + 4, "juste avant", 0, GRIS)
    ecrire(X(-ey + demi) + 8, Y(-ey) - 16, "juste après : |e − c| < 36", 0, GRIS)
    couleur = {k: c for k, _, c in LES_CLASSES}
    for _, p in les_points(d):
        x, y = X(max(emin, min(emax, p["e"]))), Y(max(-ey, min(ey, p["c"])))
        art.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur[p["la_classe"]])
        marques.append((x, y))
        traces["points"] += 1
    yl = 522
    for k, (cle, nom, c) in enumerate(LES_CLASSES):
        xl = 66 + 160 * k
        art.ellipse([xl, yl + 3, xl + 8, yl + 11], fill=c)
        ecrire(xl + 14, yl, f"{nom} · {d['les_reunis'][cle]['les_points']}", 0, ENCRE)

    # ── PANNEAU 2 · LE DÉCALAGE JUGÉ, DU CÔTÉ OÙ LA MARCHE CORRIGE ─────────────────────────────────────────────────
    panneau(720, 80, 1310, 560, "LE DÉCALAGE JUGÉ, DU CÔTÉ OÙ LA MARCHE CORRIGE")
    gx0, gx1 = 900, 1280
    GX = lambda s: gx0 + (gx1 - gx0) * (max(-20.0, min(200.0, s)) + 20.0) / 220.0  # noqa: E731
    for t in (0, LE_QUART_DE_PAS, demi, 72, 144):
        art.line([GX(t), 140, GX(t), 470], fill=TRAIT)
        ecrire(GX(t) - 8, 474, _fr(t), 0, GRIS)
    ecrire(GX(LE_QUART_DE_PAS) + 4, 140, "le quart d'un pas", 0, GRIS)
    r = d["les_reunis"]
    for k, (cle, nom, c) in enumerate(LES_CLASSES[:3]):
        y = 190 + 80 * k
        f = r[cle]
        ecrire(736, y - 16, nom, 0, ENCRE)
        ecrire(736, y, f"médiane {_fr(f['le_decalage_juge_median_voxels'])} · lu {_fr(f['lecart_lu_median_voxels'])}",
               0, GRIS)
        for _, p in les_points(d):
            if p["la_classe"] == cle:
                xs = GX(le_decalage_juge(p))
                art.ellipse([xs - 3, y - 3, xs + 3, y + 3], fill=c)
                marques.append((xs, y))
        m = GX(f["le_decalage_juge_median_voxels"])
        art.line([m, y - 12, m, y + 12], fill=ENCRE, width=2)
    t_ = r["le_temoin"]
    y = 190 + 80 * 3
    ecrire(736, y - 16, f"le témoin : {t_['les_points']} justes", 0, ENCRE)
    ecrire(736, y, f"non corrigés, |e| médian {_fr(t_['le_decalage_juge_abs_median_voxels'])}", 0, GRIS)
    m = GX(t_["le_decalage_juge_abs_median_voxels"])
    art.line([m, y - 12, m, y + 12], fill=ENCRE, width=2)
    ecrire(736, 500, "la barre noire : la médiane de la famille", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 576, L_, H_], fill=BANDE)
    ecrire(50, 588, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 608, "⚠ ce qui n'est PAS établi : qui a raison, de la marche ou du juge ; neuf voisinages, une passe.",
           moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, marques, traces


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
    tmp = sortie.parent / ".sonde_271.png"
    _, poses, cadres, marques, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure",
      f"À {_fr(d['les_reunis']['rendu_rate']['le_decalage_juge_median_voxels'])} VOXELS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in marques))
    tous = [p for x in d["les_voisinages"].values() for p in x["les_points"]]
    v("★★★★ aucun point n'est écrasé contre un bord : les échelles couvrent toutes les valeurs",
      all(-200 < p["e"] < 100 and -100 < p["c"] < 100 and -20 < le_decalage_juge(p) < 200 for p in tous),
      str([p for p in tous if not (-200 < p["e"] < 100 and -100 < p["c"] < 100)]))
    n = sum(len(x["les_points"]) for x in d["les_voisinages"].values())
    v("★★★★ chaque point corrigé est posé, et les familles en font le compte",
      traces["points"] == n == sum(d["les_reunis"][k]["les_points"] for k, _, _ in LES_CLASSES), f"{traces} contre {n}")
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
                   default=RACINE / "docs" / "images" / "271_les_points_corriges_etaient_ils_decales.png")
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
