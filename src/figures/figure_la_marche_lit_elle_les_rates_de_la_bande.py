"""Ce que la marche lit des ratés du premier saut, sur le segment `20230702185753` et sur la bande `w028-037`.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque surface, l'erreur que le juge donne (en abscisse)
contre l'écart que la marche lit (en ordonnée) : un point sur la diagonale est un point que l'écart ramène sur sa couche. À
droite, les parts réparables et cassables des deux surfaces, côte à côte, et ce que la décision en retient.

  uv run python src/figures/figure_la_marche_lit_elle_les_rates_de_la_bande.py \\
      --sortie docs/images/282_la_marche_lit_elle_les_rates_de_la_bande.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_marche_lit_elle_les_rates_de_la_bande.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
SEGMENT = (96, 112, 140)
L_, H_ = 1360, 700
LES_SURFACES = (("le_segment", "LE SEGMENT 20230702185753"), ("la_bande", "LA BANDE W028-037"))
LE_DEMI = 36.0


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def le_titre(d: dict) -> str:
    s, b = (d[k]["la_part_des_rates_que_la_marche_repare"] for k in ("le_segment", "la_bande"))
    return (f"LA MARCHE RÉPARE {_fr(b)} DES RATÉS DU PREMIER SAUT SUR LA BANDE, CONTRE {_fr(s)} SUR LE SEGMENT")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"cases": {}, "barres": {}}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"l'écart que la décision de 264 lit, relu sur les {d['le_segment']['le_controle']['les_blocs_lus']} blocs "
                   f"de 275 et les {d['la_bande']['le_controle']['les_blocs_lus']} de 281 · aucune pile rendue · "
                   "le juge ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · L'ERREUR CONTRE L'ÉCART LU ────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 760, 590, "L'ERREUR DU JUGE CONTRE L'ÉCART QUE LA MARCHE LIT")
    for k, (cle, nom) in enumerate(LES_SURFACES):
        h = d[cle]["lhistogramme"]
        bords, comptes = h["les_bords_voxels"], h["les_comptes"]
        n = len(comptes)
        cote = 12
        x0, y0 = 90 + k * 340, 150
        ecrire(x0, 118, nom, 0, ENCRE)
        vmax = max(max(r) for r in comptes) or 1
        total = 0
        for i in range(n):          # l'erreur, de gauche à droite
            for j in range(n):      # l'écart, de bas en haut
                c = comptes[i][j]
                total += c
                if not c:
                    continue
                t = math.log1p(c) / math.log1p(vmax)
                coul = tuple(int(FOND[q] + (ENCRE[q] - FOND[q]) * t) for q in range(3))
                x, y = x0 + i * cote, y0 + (n - 1 - j) * cote
                art.rectangle([x, y, x + cote - 1, y + cote - 1], fill=coul)
        traces["cases"][cle] = total
        lo, hi = bords[0], bords[-1]
        px = lambda v: x0 + (v - lo) / (hi - lo) * n * cote  # noqa: E731
        py = lambda v: y0 + (hi - v) / (hi - lo) * n * cote  # noqa: E731
        art.rectangle([x0, y0, x0 + n * cote, y0 + n * cote], outline=TRAIT)
        for dv in (-LE_DEMI, LE_DEMI):   # la bande où l'écart ramène le point sur sa couche
            art.line([px(lo), py(lo + dv), px(hi - dv), py(hi)] if dv > 0 else [px(lo - dv), py(lo), px(hi), py(hi + dv)],
                     fill=BON, width=1)
        for v in (-LE_DEMI, LE_DEMI):    # la colonne des justes
            art.line([px(v), y0, px(v), y0 + n * cote], fill=GRIS)
        points += [(x0 + n * cote, y0 + n * cote), (x0, y0)]
        ecrire(x0, y0 + n * cote + 6, f"erreur du juge, de {_fr(lo)} à {_fr(hi)} voxels", 0, GRIS)
    ecrire(90, 480, "en ordonnée, l'écart lu, sur la même échelle · entre les deux traits verts, l'écart ramène le point "
                    "sur sa couche", 0, GRIS)
    ecrire(90, 500, "entre les deux traits gris, les justes · une case par 12 voxels, plus sombre = plus de points (échelle "
                    "logarithmique)", 0, GRIS)

    # ── PANNEAU 2 · LES PARTS ─────────────────────────────────────────────────────────────────────────────────────────
    panneau(776, 80, 1310, 590, "CE QUE LA MARCHE SAIT, ET CE QUE LA DÉCISION EN RETIENT")
    lignes = (("la_part_des_rates_que_la_marche_repare", "des ratés, réparables"),
              ("la_part_reparable_des_rates_trop_loin", "des ratés trop loin, réparables"),
              ("la_part_reparable_des_rates_trop_pres", "des ratés trop près, réparables"),
              ("la_part_des_justes_que_la_marche_casse", "des justes, cassables"))
    bx0, bw = 1010, 280
    for r_, (cle, lib) in enumerate(lignes):
        y = 130 + r_ * 62
        ecrire(796, y + 6, lib, 0, ENCRE)
        for k, (surf, _) in enumerate(LES_SURFACES):
            val = d[surf][cle] or 0
            yy = y + k * 20
            art.rectangle([bx0, yy, bx0 + val * bw, yy + 14], fill=SEGMENT if k == 0 else ALERTE)
            traces["barres"][(surf, cle)] = val
            points.append((bx0 + val * bw, yy))
            ecrire(bx0 + int(val * bw) + 6, yy, _fr(val), 0, ENCRE)
    ecrire(796, 380, "■ segment", 0, SEGMENT)
    ecrire(880, 380, "■ bande", 0, ALERTE)
    for k, (surf, nom) in enumerate(LES_SURFACES):
        s = d[surf]
        dr = s["la_decision_retient"]
        ecrire(796, 420 + 46 * k, f"{nom.lower()} : {s['les_rates']} ratés, {s['les_justes']} justes", 0, ENCRE)
        ecrire(796, 438 + 46 * k, f"la décision retient {dr['des_reparables']} des {s['les_rates_reparables']} réparables et "
                                  f"{dr['des_cassables']} des {s['les_justes_cassables']} cassables", 0, GRIS)
    s_, b_ = d["le_segment"], d["la_bande"]
    ecrire(796, 512, f"ramener chaque point de son écart : {s_['les_rates_reparables']} pour {s_['les_justes_cassables']}, "
                     f"et {b_['les_rates_reparables']} pour {b_['les_justes_cassables']}", 0, ENCRE)
    ecrire(796, 540, f"corrélation de l'écart à l'erreur : {_fr(d['le_segment']['la_correlation_de_lecart_a_lerreur'])} "
                     f"et {_fr(d['la_bande']['la_correlation_de_lecart_a_lerreur'])}", 0, ENCRE)
    ecrire(796, 558, f"médiane de l'écart des justes : {_fr(d['le_segment']['la_mediane_de_lecart_des_justes_voxels'])} et "
                     f"{_fr(d['la_bande']['la_mediane_de_lecart_des_justes_voxels'])} voxels", 0, ENCRE)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 606, L_, H_], fill=BANDE)
    ecrire(50, 616, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    c1, c2 = d["le_segment"]["le_controle"], d["la_bande"]["le_controle"]
    ecrire(50, 638, f"l'écart relu redonne la décision publiée sur {c1['les_blocs_lus']} et {c2['les_blocs_lus']} blocs, et "
                    f"{c1['les_rates_rendus_justes_publies']} pour {c1['les_justes_rendus_rates_publies']}, "
                    f"{c2['les_rates_rendus_justes_publies']} pour {c2['les_justes_rendus_rates_publies']}", moyen, ENCRE)
    ecrire(50, 662, "⚠ ce qui n'est PAS établi : pourquoi la lecture ou le choix diffère ; une autre décision.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_282.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", _fr(d["la_bande"]["la_part_des_rates_que_la_marche_repare"]) in le_titre(d)
      and _fr(d["le_segment"]["la_part_des_rates_que_la_marche_repare"]) in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque carte compte tous les points notés de sa surface, une fois",
      all(traces["cases"][k] == d[k]["les_points_notes"] for k, _ in LES_SURFACES), str(traces["cases"]))
    v("★★★★ chaque barre porte la part mesurée",
      len(traces["barres"]) == 8 and all(v_ == (d[s][c] or 0) for (s, c), v_ in traces["barres"].items()))
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
                   default=RACINE / "docs" / "images" / "282_la_marche_lit_elle_les_rates_de_la_bande.png")
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
