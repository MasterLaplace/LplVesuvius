"""La décision qui pèse glissé contre juste, contre la règle fixe, sur les dix blocs : ce qu'elle corrige, et pourquoi.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, BLOC PAR BLOC, la part des points sur la bonne spire avant, après
la règle fixe de `261`, et après la décision : sur les blocs pris à pas réguliers la décision ne défait rien, sur les deux
blocs choisis elle ne fait rien. À droite, POURQUOI : les écarts de deux blocs aux centres des chunks, et le mélange que
chacun ajuste. Sur le bloc de `257`, vu après coup, deux bosses à une glissade l'une de l'autre, et l'ancre entre les deux.

  uv run python src/figures/figure_la_marche_sait_elle_ou_ne_pas_corriger.py \\
      --sortie docs/images/264_la_marche_sait_elle_ou_ne_pas_corriger.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_marche_sait_elle_ou_ne_pas_corriger.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (200, 205, 212)
L_, H_ = 1360, 700
LES_CHOISIS = ("le_bloc_de_257", "le_bloc_de_259")


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


def le_nom(n: str, b: dict) -> str:
    return f"le bloc de {n[-3:]}" if n in LES_CHOISIS else f"({b['la_rangee']}, {b['la_colonne']})"


def les_lignes(d: dict) -> list[tuple[str, dict]]:
    """Les blocs que le juge note : les deux choisis d'abord, puis les réguliers dans l'ordre de leur part avant."""
    ok = {n: b for n, b in d["les_blocs"].items() if b["avant"]["la_part_sur_la_bonne_spire"] is not None}
    choisis = [(n, ok[n]) for n in LES_CHOISIS if n in ok]
    reste = sorted(((n, b) for n, b in ok.items() if n not in LES_CHOISIS),
                   key=lambda nb: (nb[1]["avant"]["la_part_sur_la_bonne_spire"], nb[0]))
    return choisis + reste


def le_regulier_montre(d: dict) -> str:
    """Le bloc régulier où le mélange voit le plus de spires glissées."""
    reg = [n for n in d["les_blocs"] if n not in LES_CHOISIS]
    return max(reg, key=lambda n: (d["les_blocs"][n]["le_melange"]["glissee_au_dessus"]
                                   + d["les_blocs"][n]["le_melange"]["glissee_au_dessous"], n))


def les_ecarts(b: dict) -> np.ndarray:
    x = np.array([[np.nan if v is None else v for v in r] for r in b["la_difference"]], dtype=float) - b["lancre_voxels"]
    return x[np.isfinite(x)]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : ce que la décision fait sur les blocs réguliers et sur les deux choisis."""
    r, c = d["les_reguliers"]["la_decision"], d["les_choisis"]["la_decision"]
    fin = "RIEN" if c["les_points_corriges"] == 0 else f"{c['les_rates_rendus_justes']} RATÉS RENDUS JUSTES"
    return (f"PESER GLISSÉ CONTRE JUSTE : SUR LES BLOCS RÉGULIERS {r['les_rates_rendus_justes']} RATÉS RENDUS JUSTES ET "
            f"{r['les_justes_rendus_rates']} JUSTE RENDU RATÉ ; SUR LES DEUX BLOCS CHOISIS, {fin}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"avant": 0, "fixe": 0, "decision": 0, "barres": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · une passe · le bruit autour de zéro, une spire glissée autour de ± "
                   f"{_fr(d['la_glissade_voxels'], 3)} voxels, poids et largeur ajustés à chaque bloc · le juge ne sert "
                   "qu'à juger", petit, GRIS)
    lignes = les_lignes(d)

    # ── PANNEAU 1 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 800, 560, "LA PART SUR LA BONNE SPIRE : AVANT ○, RÈGLE FIXE ◆, DÉCISION ●")
    gx0, gx1, gy0 = 300, 560, 150
    pas = 36
    x_lo = 0.4
    xx = lambda v: gx0 + (gx1 - gx0) * (v - x_lo) / (1.0 - x_lo)  # noqa: E731
    for v in (0.4, 0.7, 1.0):
        art.line([xx(v), gy0 - 18, xx(v), gy0 + pas * len(lignes) - 16], fill=TRAIT)
        ecrire(xx(v) - 8, gy0 - 36, _fr(v, 1), 0, GRIS)
    ecrire(590, gy0 - 36, "le mélange : largeur, glissées", 0, GRIS)
    for k, (nom, b) in enumerate(lignes):
        y = gy0 + pas * k
        ecrire(66, y - 7, f"{le_nom(nom, b)} · {b['avant']['les_points_notes']} points", 0,
               ENCRE if nom in LES_CHOISIS else GRIS)
        a = b["avant"]["la_part_sur_la_bonne_spire"]
        f = b["la_regle_fixe"]["apres"]["la_part_sur_la_bonne_spire"]
        z = b["la_decision"]["apres"]["la_part_sur_la_bonne_spire"]
        art.line([xx(a), y, xx(f), y], fill=PALE, width=2)
        art.ellipse([xx(a) - 5, y - 5, xx(a) + 5, y + 5], outline=GRIS, width=2)
        points.append((xx(a), y))
        traces["avant"] += 1
        art.polygon([(xx(f), y - 6), (xx(f) + 6, y), (xx(f), y + 6), (xx(f) - 6, y)],
                    fill=BON if f > a else ALERTE if f < a else GRIS)
        points.append((xx(f), y))
        traces["fixe"] += 1
        art.ellipse([xx(z) - 4, y - 4, xx(z) + 4, y + 4], fill=ENCRE)
        points.append((xx(z), y))
        traces["decision"] += 1
        m = b["le_melange"]
        ecrire(590, y - 7, f"{_fr(m['la_largeur_voxels'], 1)} voxels, "
                           f"{_fr(100 * (m['glissee_au_dessus'] + m['glissee_au_dessous']), 1)} %", 0, GRIS)
    y = gy0 + pas * len(lignes) + 4
    for cle, titre in (("les_reguliers", "réguliers"), ("les_choisis", "choisis")):
        g = d[cle]
        ecrire(66, y, f"{titre}, réunis : {_fr(g['avant'], 4)} → règle fixe {_fr(g['la_regle_fixe']['apres'], 4)} "
                      f"({g['la_regle_fixe']['les_rates_rendus_justes']} rendus justes, "
                      f"{g['la_regle_fixe']['les_justes_rendus_rates']} rendus ratés), décision "
                      f"{_fr(g['la_decision']['apres'], 4)} ({g['la_decision']['les_rates_rendus_justes']}, "
                      f"{g['la_decision']['les_justes_rendus_rates']})", 0, ENCRE)
        y += 20

    # ── PANNEAU 2 · POURQUOI ───────────────────────────────────────────────────────────────────────────────────────
    panneau(820, 80, 1310, 560, "LES ÉCARTS AUX CENTRES DES CHUNKS, ET LE MÉLANGE")
    montres = ["le_bloc_de_257", le_regulier_montre(d)]
    for i, nom in enumerate(montres):
        b = d["les_blocs"][nom]
        x = les_ecarts(b)
        hx0, hx1 = 870, 1280
        hy1 = 300 + 200 * i
        hy0 = hy1 - 130
        bords = np.arange(-150, 151, 10)
        comptes, _ = np.histogram(np.clip(x, -149.9, 149.9), bords)
        hmax = max(1, int(comptes.max()))
        vx = lambda v: hx0 + (hx1 - hx0) * (v + 150) / 300  # noqa: E731
        vy = lambda c: hy1 - (hy1 - hy0) * c / hmax  # noqa: E731
        for c0, c in zip(bords[:-1], comptes):
            if c:
                art.rectangle([vx(c0) + 1, vy(c), vx(c0 + 10) - 1, hy1], fill=PALE)
                traces["barres"] += 1
        m = b["le_melange"]
        s, g = m["la_largeur_voxels"], m["la_glissade_voxels"]
        ws = (m["le_bruit"], m["glissee_au_dessus"], m["glissee_au_dessous"])
        xs = np.linspace(-150, 150, 301)
        dens = sum(w * np.exp(-0.5 * ((xs - c) / s) ** 2) / (s * np.sqrt(2 * np.pi)) for w, c in zip(ws, (0, g, -g)))
        dens = dens * len(x) * 10
        courbe = [(vx(a), max(hy0, vy(c))) for a, c in zip(xs, dens)]
        art.line(courbe, fill=ENCRE, width=2)
        points.extend(courbe[::30])
        art.line([hx0, hy1, hx1, hy1], fill=GRIS)
        for v in (-g, g):
            art.line([vx(v), hy0, vx(v), hy1], fill=BON)
        for v in (-36, 36):
            art.line([vx(v), hy1 - 8, vx(v), hy1 + 8], fill=ALERTE, width=2)
        for v in (-150, -69, 0, 69, 150):
            ecrire(vx(v) - 12, hy1 + 10, _fr(v, 0), 0, GRIS)
        ecrire(hx0, hy0 - 44, f"{le_nom(nom, b)} : le mélange y lit {_fr(100 * m['le_bruit'], 1)} % de bruit, "
                              f"large de {_fr(s, 1)} voxels", 0, ENCRE)
        bosses = b["vu_apres_coup"]["les_deux_bosses"]
        ecrire(hx0, hy0 - 26, f"vu après coup : deux bosses à {_fr(bosses['lecart_voxels'], 1)} voxels l'une de l'autre, "
                              f"{_fr(100 * bosses['les_poids'][0], 0)} % et {_fr(100 * bosses['les_poids'][1], 0)} %", 0,
               ALERTE)
        for cb in bosses["les_centres_voxels"]:
            art.polygon([(vx(cb) - 5, hy0 - 6), (vx(cb) + 5, hy0 - 6), (vx(cb), hy0 + 2)], fill=ALERTE)
            points.append((vx(cb), hy0))
    ecrire(836, 536, "vert : une spire glissée · orange : le seuil fixe, les deux bosses · noir : le mélange", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 576, L_, H_], fill=BANDE)
    ecrire(50, 588, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    reg = d["les_reguliers"]["la_decision"]
    b7 = d["les_blocs"]["le_bloc_de_257"]["vu_apres_coup"]["les_deux_bosses"]
    ecrire(50, 610, f"★ où la spire produite est juste, la décision corrige {reg['les_points_corriges']} points et n'en "
                    f"abîme aucun ; sur le bloc de 257, l'ancre tombe entre deux bosses à {_fr(b7['lecart_voxels'], 1)} "
                    "voxels, et elle n'en voit aucune.", moyen, ENCRE)
    ecrire(50, 636, "⚠ ce qui n'est PAS établi : laquelle des deux bosses est sur la bonne spire, ce que la marche seule ne "
                    "dit pas ; des blocs neufs ; une boucle.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def txt_vu(poses) -> bool:
    """Tout nombre de bosses tracé dans un panneau commence par « vu après coup »."""
    return all(t.startswith("vu après coup") for _, _, t, _ in poses if "bosses à" in t and not t.startswith("★"))


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
    tmp = sortie.parent / ".sonde_264.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    r = d["les_reguliers"]["la_decision"]
    v("★★★ le titre LIT la mesure", f"{r['les_rates_rendus_justes']} RATÉS RENDUS JUSTES ET" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n = len(les_lignes(d))
    v("★★★★ chaque bloc noté a son avant, sa règle fixe et sa décision",
      traces["avant"] == traces["fixe"] == traces["decision"] == n, str(traces))
    v("★★★ les deux histogrammes ont leurs barres", traces["barres"] >= 4, str(traces["barres"]))
    v("★★★★ ce qui est vu après coup est écrit comme tel", txt_vu(poses))
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
                   default=RACINE / "docs" / "images" / "264_la_marche_sait_elle_ou_ne_pas_corriger.png")
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
