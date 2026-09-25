"""La correction sans juge, répétée : passe par passe, la part sur la bonne spire, les points signalés, la dispersion.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA PART DES POINTS SUR LA BONNE SPIRE, avant toute correction puis
après chaque passe, sur les deux blocs : elle monte, puis se fige. À droite, LES POINTS SIGNALÉS à chaque passe, qui tombent
à zéro, et l'écart type de la différence des marches lue au départ de chaque passe : c'est ce zéro qui arrête la procédure,
sans le juge.

  uv run python src/figures/figure_la_correction_repetee_converge_t_elle.py \\
      --sortie docs/images/262_la_correction_repetee_converge_t_elle.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_correction_repetee_converge_t_elle.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 620
LES_COULEURS = {"le_bloc_de_257": BON, "le_bloc_de_259": CONTRE}


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_courbe(b: dict) -> list[float]:
    return [b["les_passes"][0]["la_part_avant"]] + [p["la_part_sur_la_bonne_spire_apres"] for p in b["les_passes"]]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : où la part finit, et quand la procédure s'arrête d'elle-même."""
    c = {n: la_courbe(b) for n, b in d["les_blocs"].items()}
    arret = all(b["les_passes"][-1]["les_points_signales"] == 0 for b in d["les_blocs"].values())
    t = " ET ".join(f"DE {_fr(v[0], 4)} À {_fr(v[-1], 4)}" for v in c.values())
    if arret:
        return f"RÉPÉTÉE, LA CORRECTION SANS JUGE S'ARRÊTE D'ELLE-MÊME, ET LA PART SUR LA BONNE SPIRE VA {t}"
    return f"RÉPÉTÉE QUATRE FOIS, LA CORRECTION SANS JUGE SIGNALE ENCORE ; LA PART VA {t}"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"points": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · à chaque passe : l'ancre à la médiane, les points à un demi-feuillet "
                   "ramenés, la spire rendue et relue · arrêt quand plus rien n'est signalé", petit, GRIS)
    n_max = max(len(b["les_passes"]) for b in d["les_blocs"].values())

    # ── PANNEAU 1 · LA PART ────────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 500, "LA PART DES POINTS SUR LA BONNE SPIRE, PASSE PAR PASSE")
    gx0, gx1, gy0, gy1, lo, hi = 110, 660, 130, 440, 0.4, 0.8
    xx = lambda k: gx0 + (gx1 - gx0) * k / max(1, n_max)  # noqa: E731
    yy = lambda v: gy1 - (gy1 - gy0) * (v - lo) / (hi - lo)  # noqa: E731
    for v in (0.4, 0.5, 0.6, 0.7, 0.8):
        art.line([gx0, yy(v), gx1, yy(v)], fill=TRAIT)
        ecrire(gx0 - 36, yy(v) - 7, _fr(v, 1), 0, GRIS)
    for k in range(n_max + 1):
        ecrire(xx(k) - 20, gy1 + 12, "avant" if k == 0 else f"passe {k}", 0, GRIS)
    for m, (nom, b) in enumerate(d["les_blocs"].items()):
        c = la_courbe(b)
        coul = LES_COULEURS[nom]
        pts = [(xx(k), yy(v)) for k, v in enumerate(c)]
        art.line(pts, fill=coul, width=3)
        for x, y in pts:
            art.ellipse([x - 4, y - 4, x + 4, y + 4], fill=coul)
            points.append((x, y))
            traces["points"] += 1
        x, y = pts[-1]
        ecrire(x - 120, y + (10 if m else -24), f"bloc {nom[-3:]} : {_fr(c[-1], 4)}", 0, coul)

    # ── PANNEAU 2 · CE QUI ARRÊTE ──────────────────────────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 500, "LES POINTS SIGNALÉS, ET LA DISPERSION DE LA DIFFÉRENCE LUE")
    y = 124
    for nom, b in d["les_blocs"].items():
        ecrire(736, y, f"le bloc de {nom[-3:]}", 0, LES_COULEURS[nom])
        y += 22
        for p in b["les_passes"]:
            ecrire(750, y, f"passe {p['la_passe']} : {p['les_points_signales']} points signalés, écart type lu "
                           f"{_fr(p['lecart_type_de_la_difference_lue_voxels'], 2)} voxels, ancre {_fr(p['lancre_voxels'], 2)}",
                   0, GRIS)
            y += 20
        y += 18
    ecrire(736, y + 4, "une passe sans point signalé arrête la procédure :", 0, ENCRE)
    ecrire(736, y + 22, "c'est elle, et non le juge, qui dit que c'est fini", 0, ENCRE)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 516, L_, H_], fill=BANDE)
    ecrire(50, 528, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 550, "★ la procédure corrige, se relit, et s'arrête seule : rien d'humain ne décide ni la correction ni la fin.",
           moyen, ENCRE)
    ecrire(50, 576, "⚠ ce qui n'est PAS établi : deux blocs ; les ratés qui restent, le juge les voit et la marche non ; une "
                    "boucle.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
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

    d = lire()
    tmp = sortie.parent / ".sonde_262.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    arret = all(b["les_passes"][-1]["les_points_signales"] == 0 for b in d["les_blocs"].values())
    v("★★★ le titre LIT la mesure", ("S'ARRÊTE D'ELLE-MÊME" in le_titre(d)) == arret)
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = sum(len(b["les_passes"]) + 1 for b in d["les_blocs"].values())
    v("★★★★ chaque passe de chaque bloc a son point, avant compris", traces["points"] == attendu, f"{traces['points']} / {attendu}")
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ chaque passe est écrite avec ses points signalés",
      all(f"passe {p['la_passe']} : {p['les_points_signales']} points signalés" in txt
          for b in d["les_blocs"].values() for p in b["les_passes"]))
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
                   default=RACINE / "docs" / "images" / "262_la_correction_repetee_converge_t_elle.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
