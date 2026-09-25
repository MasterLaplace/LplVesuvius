"""Le bloc et ses voisins marchés d'un seul tenant : la carte des niveaux, l'ancre prise dehors, et ce que la décision fait.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, POUR CHAQUE BLOC DE `262`, la différence des marches sur le bloc
et ses voisins, centrée sur l'ancre du voisinage : on voit quel niveau les voisins portent, et quelle partie du bloc est à
une glissade de lui. À droite, les écarts du bloc à cette ancre, avec l'ancre du bloc à côté, et la part sur la bonne spire
avant, puis après la décision avec l'une et l'autre ancre.

  uv run python src/figures/figure_le_voisinage_dit_il_quel_niveau_est_le_bon.py \\
      --sortie docs/images/265_le_voisinage_dit_il_quel_niveau_est_le_bon.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (200, 205, 212)
VIDE = (232, 230, 225)
L_, H_ = 1360, 760
LA_PORTEE = 100.0


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
    """Divergente : bleu sous l'ancre, ocre au-dessus, blanc cassé sur elle ; saturée à `LA_PORTEE`."""
    t = max(-1.0, min(1.0, v / LA_PORTEE))
    a, b = (92, 108, 150), (176, 120, 42)
    c = b if t > 0 else a
    return tuple(int(round(245 + (ci - 245) * abs(t))) for ci in c)


def la_part(b: dict, ancre: str | None) -> float | None:
    return b["avant"]["la_part_sur_la_bonne_spire"] if ancre is None else \
        b[ancre]["la_decision"]["apres"]["la_part_sur_la_bonne_spire"]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la part de chaque bloc avant, et après la décision avec l'ancre du voisinage."""
    t = " ; ".join(f"LE BLOC DE {n[-3:]} DE {_fr(la_part(b, None), 4)} À {_fr(la_part(b, 'lancre_du_voisinage'), 4)}"
                   for n, b in d["les_blocs"].items())
    return f"L'ANCRE PRISE CHEZ LES VOISINS : {t}"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"cartes": 0, "barres": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · le bloc et ses voisins candidats marchés d'un seul tenant · l'ancre : "
                   "la médiane de la différence sur les voisins seuls · la décision de 264 · une passe", petit, GRIS)
    blocs = list(d["les_blocs"].items())

    # ── PANNEAU 1 · LES NIVEAUX ────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 620, "LA DIFFÉRENCE DES MARCHES, CENTRÉE SUR L'ANCRE DU VOISINAGE")
    for i, (nom, b) in enumerate(blocs):
        x0, y0, cote = 70 + 315 * i, 150, 288
        diff = np.array([[np.nan if v is None else v for v in r] for r in b["la_difference"]], dtype=float)
        anc = b["lancre_du_voisinage"]["lancre_voxels"]
        n = diff.shape[0]
        px = cote / n
        for r in range(n):
            for c in range(n):
                v = diff[r, c]
                coul = VIDE if not np.isfinite(v) else la_couleur(v - anc)
                art.rectangle([x0 + c * px, y0 + r * px, x0 + (c + 1) * px - 1, y0 + (r + 1) * px - 1], fill=coul)
        traces["cartes"] += 1
        k = n // 3
        art.rectangle([x0 + k * px, y0 + k * px, x0 + 2 * k * px, y0 + 2 * k * px], outline=ENCRE, width=2)
        points.append((x0 + cote, y0 + cote))
        ecrire(x0, y0 - 24, f"le bloc de {nom[-3:]} ({b['la_rangee']}, {b['la_colonne']}), {len(b['les_voisins'])} voisins",
               0, ENCRE)
        y = y0 + cote + 12
        for vn, vj in b["les_voisins_juges"].items():
            ecrire(x0, y, f"voisin ({vn.replace('_', ', ')}) : {_fr(vj['la_part_sur_la_bonne_spire'], 4)} juste", 0, GRIS)
            y += 18
    lx0, ly = 70, 580
    for j, v in enumerate(np.linspace(-LA_PORTEE, LA_PORTEE, 21)):
        art.rectangle([lx0 + 14 * j, ly, lx0 + 14 * j + 13, ly + 12], fill=la_couleur(float(v)))
    ecrire(lx0, ly + 18, f"de −{_fr(LA_PORTEE, 0)} à +{_fr(LA_PORTEE, 0)} voxels autour de l'ancre ; "
                                       "le cadre noir est le bloc", 0, GRIS)

    # ── PANNEAU 2 · LES ÉCARTS DU BLOC, ET LES PARTS ───────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 620, "LES ÉCARTS DU BLOC À L'ANCRE DU VOISINAGE")
    g = d["la_glissade_voxels"]
    for i, (nom, b) in enumerate(blocs):
        hx0, hx1 = 760, 1280
        hy1 = 320 + 250 * i
        hy0 = hy1 - 130
        diff = np.array([[np.nan if v is None else v for v in r] for r in b["la_difference"]], dtype=float)
        n = diff.shape[0] // 3
        x = (diff[n:2 * n, n:2 * n] - b["lancre_du_voisinage"]["lancre_voxels"]).ravel()
        x = x[np.isfinite(x)]
        bords = np.arange(-150, 151, 10)
        comptes, _ = np.histogram(np.clip(x, -149.9, 149.9), bords)
        hmax = max(1, int(comptes.max()))
        vx = lambda v: hx0 + (hx1 - hx0) * (v + 150) / 300  # noqa: E731
        vy = lambda c: hy1 - (hy1 - hy0) * c / hmax  # noqa: E731
        for c0, c in zip(bords[:-1], comptes):
            if c:
                art.rectangle([vx(c0) + 1, vy(c), vx(c0 + 10) - 1, hy1], fill=PALE)
                traces["barres"] += 1
        art.line([hx0, hy1, hx1, hy1], fill=GRIS)
        for v in (-g, g):
            art.line([vx(v), hy0, vx(v), hy1], fill=BON)
        art.line([vx(0), hy0 - 4, vx(0), hy1], fill=ENCRE, width=2)
        mb = b["lancre_du_bloc"]["lancre_voxels"] - b["lancre_du_voisinage"]["lancre_voxels"]
        art.line([vx(mb), hy0 - 4, vx(mb), hy1], fill=ALERTE, width=2)
        points.append((vx(mb), hy0))
        for v in (-150, -69, 0, 69, 150):
            ecrire(vx(v) - 12, hy1 + 8, _fr(v, 0), 0, GRIS)
        ecrire(hx0, hy0 - 60, f"le bloc de {nom[-3:]} : avant {_fr(la_part(b, None), 4)}", 0, ENCRE)
        dv, db = b["lancre_du_voisinage"]["la_decision"], b["lancre_du_bloc"]["la_decision"]
        ecrire(hx0, hy0 - 42, f"décision, ancre du voisinage : {_fr(la_part(b, 'lancre_du_voisinage'), 4)} "
                              f"({dv['les_rates_rendus_justes']} rendus justes, {dv['les_justes_rendus_rates']} rendus ratés)",
               0, ENCRE)
        ecrire(hx0, hy0 - 24, f"décision, ancre du bloc : {_fr(la_part(b, 'lancre_du_bloc'), 4)} "
                              f"({db['les_rates_rendus_justes']} rendus justes, {db['les_justes_rendus_rates']} rendus ratés)",
               0, ALERTE)
    ecrire(736, 596, "noir : l'ancre du voisinage · orange : l'ancre du bloc · vert : une glissade de part et d'autre", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 636, L_, H_], fill=BANDE)
    ecrire(50, 648, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 670, "★ l'ancre prise hors du bloc, avec la même décision et la même marche : c'est le seul changement "
                    "entre les deux lignes de droite.", moyen, ENCRE)
    vu = d["les_derivees"]["vu_apres_coup"]
    ecrire(50, 696, f"⚠ vu après coup : les voisins de 259, que le juge voit à "
                    f"{_fr(vu['letendue_des_erreurs_jugees_des_voisins_voxels']['le_bloc_de_259'], 1)} voxels près, sont dans "
                    f"la marche à {_fr(vu['letendue_des_niveaux_des_voisins_voxels']['le_bloc_de_259'], 1)} voxels les uns des "
                    "autres : la marche dérive d'un bloc à l'autre.", moyen, ALERTE)
    ecrire(50, 722, "⚠ ce qui n'est PAS établi : des blocs réguliers ; un voisinage lui-même glissé ; une boucle ; le segment "
                    "entier.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_265.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", all(f"DE {_fr(la_part(b, None), 4)} À {_fr(la_part(b, 'lancre_du_voisinage'), 4)}"
                                         in le_titre(d) for b in d["les_blocs"].values()))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque bloc a sa carte et son histogramme",
      traces["cartes"] == len(d["les_blocs"]) and traces["barres"] >= 2 * len(d["les_blocs"]), str(traces))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ chaque voisin est écrit avec sa part jugée",
      all(f"voisin ({vn.replace('_', ', ')})" in txt for b in d["les_blocs"].values() for vn in b["les_voisins_juges"]))
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
                   default=RACINE / "docs" / "images" / "265_le_voisinage_dit_il_quel_niveau_est_le_bon.png")
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
