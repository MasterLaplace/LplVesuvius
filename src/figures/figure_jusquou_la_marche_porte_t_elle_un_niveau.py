"""Jusqu'où la marche porte un niveau : l'écart de ce qu'elle ajoute, entre deux chunks, selon leur distance.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, σ(d) en échelles logarithmiques, bloc par bloc et d'un seul
tenant, contre le demi-feuillet : la courbe le traverse vers seize chunks, un bloc. À droite, CE QUE LA MARCHE AJOUTE sur le
voisinage du bloc de `259`, là où le juge tient les chunks pour justes : des plaques de plusieurs dizaines de voxels, d'un
bloc à l'autre.

  uv run python src/figures/figure_jusquou_la_marche_porte_t_elle_un_niveau.py \\
      --sortie docs/images/266_jusquou_la_marche_porte_t_elle_un_niveau.png
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

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "jusquou_la_marche_porte_t_elle_un_niveau.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
VIDE = (232, 230, 225)
L_, H_ = 1360, 700
LE_DEMI = 36.0
LA_PORTEE = 60.0


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_couleur(v: float):
    t = max(-1.0, min(1.0, v / LA_PORTEE))
    a, b = (92, 108, 150), (176, 120, 42)
    c = b if t > 0 else a
    return tuple(int(round(245 + (ci - 245) * abs(t))) for ci in c)


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la portée, et σ de part et d'autre."""
    p = d["la_portee_en_chunks"]
    cl = d["dun_seul_tenant"]
    if p is None:
        return "LA MARCHE PORTE UN NIVEAU À UN DEMI-FEUILLET PRÈS SUR TOUTE LA DISTANCE MESURÉE"
    avant = [c for c in cl if c["a"] <= p and c["sigma_voxels"] is not None][-1]
    ici = [c for c in cl if c["de"] == p][0]
    return (f"LA MARCHE PORTE UN NIVEAU À UN DEMI-FEUILLET PRÈS JUSQU'À {p} CHUNKS : σ VAUT "
            f"{_fr(avant['sigma_voxels'], 1)} VOXELS EN DEÇÀ, {_fr(ici['sigma_voxels'], 1)} AU-DELÀ")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"points": 0, "carte": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · r = D − " + _fr(d["la_pente"], 4) + " · E, là où le juge tient le chunk "
                   "pour juste · σ(d) : la racine de la moyenne de (r₁ − r₂)² entre chunks à la distance d", petit, GRIS)

    # ── PANNEAU 1 · σ(d) ───────────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 560, "CE QUE LA MARCHE PERD, SELON LA DISTANCE")
    gx0, gx1, gy0, gy1 = 120, 660, 130, 480
    lx = lambda v: gx0 + (gx1 - gx0) * np.log(v) / np.log(64)  # noqa: E731
    ly = lambda s: gy1 - (gy1 - gy0) * (np.log(s) - np.log(10)) / (np.log(80) - np.log(10))  # noqa: E731
    for s in (10, 20, 40, 80):
        art.line([gx0, ly(s), gx1, ly(s)], fill=TRAIT)
        ecrire(gx0 - 34, ly(s) - 7, _fr(s, 0), 0, GRIS)
    for v in (1, 2, 4, 8, 16, 32, 64):
        art.line([lx(v), gy0, lx(v), gy1], fill=TRAIT)
        ecrire(lx(v) - 6, gy1 + 8, _fr(v, 0), 0, GRIS)
    ecrire(gx0, gy1 + 26, "la distance entre les chunks, en chunks ; σ en voxels", 0, GRIS)
    art.line([gx0, ly(LE_DEMI), gx1, ly(LE_DEMI)], fill=ALERTE, width=2)
    ecrire(gx1 - 128, ly(LE_DEMI) - 20, "le demi-feuillet, 36", 0, ALERTE)
    for cle, coul, nom, dy in (("bloc_par_bloc", CONTRE, "bloc par bloc, les dix blocs", 0),
                               ("dun_seul_tenant", BON, "d'un seul tenant, les deux voisinages", 18)):
        pts = [(lx(np.sqrt(c["de"] * c["a"])), ly(c["sigma_voxels"])) for c in d[cle] if c["sigma_voxels"] is not None]
        art.line(pts, fill=coul, width=3)
        for x, y in pts:
            art.ellipse([x - 4, y - 4, x + 4, y + 4], fill=coul)
            points.append((x, y))
            traces["points"] += 1
        ecrire(gx0 + 14, gy0 + dy, f"{nom} · pente {_fr(d['la_pente_en_log'][cle], 2)}", 0, coul)
    ecrire(gx0 + 14, gy0 + 36, "une marche au hasard aurait une pente d'un demi", 0, GRIS)
    p = d["la_portee_en_chunks"]
    if p is not None:
        art.line([lx(p), gy0, lx(p), gy1], fill=ENCRE, width=2)
        ecrire(lx(p) + 6, gy1 - 22, f"la portée, {p} chunks", 0, ENCRE)

    # ── PANNEAU 2 · CE QUE LA MARCHE AJOUTE ────────────────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 560, "CE QUE LA MARCHE AJOUTE, SUR LE VOISINAGE DU BLOC DE 259")
    r = np.array([[np.nan if x is None else x for x in rr] for rr in d["les_voisinages"]["le_bloc_de_259"]["le_reste"]],
                 dtype=float)
    med = float(np.nanmedian(r))
    x0, y0, cote = 800, 130, 384
    n = r.shape[0]
    px = cote / n
    for i in range(n):
        for j in range(n):
            v = r[i, j]
            art.rectangle([x0 + j * px, y0 + i * px, x0 + (j + 1) * px - 1, y0 + (i + 1) * px - 1],
                          fill=VIDE if not np.isfinite(v) else la_couleur(v - med))
    traces["carte"] += 1
    k = n // 3
    art.rectangle([x0 + k * px, y0 + k * px, x0 + 2 * k * px, y0 + 2 * k * px], outline=ENCRE, width=2)
    points.append((x0 + cote, y0 + cote))
    lx0, ly0 = 800, 526
    for jj, v in enumerate(np.linspace(-LA_PORTEE, LA_PORTEE, 21)):
        art.rectangle([lx0 + 12 * jj, ly0, lx0 + 12 * jj + 11, ly0 + 10], fill=la_couleur(float(v)))
    ecrire(lx0 + 12 * 21 + 10, ly0 - 2, f"de −{_fr(LA_PORTEE, 0)} à +{_fr(LA_PORTEE, 0)} voxels autour de la médiane", 0,
           GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 576, L_, H_], fill=BANDE)
    ecrire(50, 588, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 610, "★ au-delà d'un bloc, entre deux chunks que le juge tient pour justes, ce que la marche ajoute diffère "
                    "de plus d'un demi-feuillet en moyenne quadratique.", moyen, ENCRE)
    ecrire(50, 636, "⚠ ce qui n'est PAS établi : la part du juge dans σ ; ce qu'une médiane sur beaucoup de chunks en retire ; "
                    "une boucle.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_266.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    p = d["la_portee_en_chunks"]
    v("★★★ le titre LIT la mesure", (f"JUSQU'À {p} CHUNKS" in le_titre(d)) if p is not None else "TOUTE" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n = sum(1 for k in ("bloc_par_bloc", "dun_seul_tenant") for c in d[k] if c["sigma_voxels"] is not None)
    v("★★★★ chaque classe mesurée a son point, et la carte est là", traces == {"points": n, "carte": 1}, str(traces))
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
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "266_jusquou_la_marche_porte_t_elle_un_niveau.png")
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
