"""L'escalier des marches : l'entier que chaque chunk reçoit, et ce que la correction en pas pleins fait de chaque bloc.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, POUR CHAQUE VOISINAGE, l'entier de chaque chunk par rapport à la
spire de référence : sur celui de `257` une marche sous une partie du bloc central, sur celui de `259` une grande région
mise à une spire de la référence. À droite, BLOC PAR BLOC, la part sur la bonne spire avant et après : la correction du
premier voisinage et l'effondrement du second.

  uv run python src/figures/figure_lescalier_porte_t_il_le_choix_de_la_spire.py \\
      --sortie docs/images/267_lescalier_porte_t_il_le_choix_de_la_spire.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "lescalier_porte_t_il_le_choix_de_la_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (200, 205, 212)
VIDE = (232, 230, 225)
LES_ENTIERS = {-2: (60, 72, 120), -1: (130, 145, 190), 0: (240, 238, 232), 1: (214, 170, 110), 2: (160, 100, 40)}
L_, H_ = 1360, 720


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


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : le centre de chaque voisinage, avant et après."""
    t = " ; ".join(f"LE BLOC DE {n[-3:]} DE {_fr(v['le_centre']['avant']['la_part_sur_la_bonne_spire'], 4)} À "
                   f"{_fr(v['le_centre']['apres']['la_part_sur_la_bonne_spire'], 4)}" for n, v in d["les_voisinages"].items())
    return f"L'ESCALIER, EN PAS PLEINS : {t}"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"cartes": 0, "lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · de proche en proche, l'entier qui garde le niveau le plus proche ; "
                   "marches de moins de quatre chunks reprises ; référence : l'entier le plus fréquent · une passe", petit,
           GRIS)

    # ── PANNEAU 1 · L'ESCALIER ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 580, "L'ENTIER DE CHAQUE CHUNK, CONTRE LA SPIRE DE RÉFÉRENCE")
    for i, (nom, v) in enumerate(d["les_voisinages"].items()):
        x0, y0, cote = 70 + 315 * i, 150, 288
        k = v["lescalier"]
        n = len(k)
        px = cote / n
        for r in range(n):
            for c in range(n):
                e = k[r][c]
                coul = VIDE if e is None else LES_ENTIERS.get(max(-2, min(2, e)), ENCRE)
                art.rectangle([x0 + c * px, y0 + r * px, x0 + (c + 1) * px - 1, y0 + (r + 1) * px - 1], fill=coul)
        traces["cartes"] += 1
        t = n // 3
        art.rectangle([x0 + t * px, y0 + t * px, x0 + 2 * t * px, y0 + 2 * t * px], outline=ENCRE, width=2)
        points.append((x0 + cote, y0 + cote))
        ecrire(x0, y0 - 24, f"le voisinage du bloc de {nom[-3:]}", 0, ENCRE)
        m = v["les_marches"]
        ecrire(x0, y0 + cote + 12, "chunks par entier : " + ", ".join(f"{_fr(int(a), 0)} : {b}" for a, b in sorted(
            m.items(), key=lambda kv: int(kv[0]))), 0, GRIS)
        ecrire(x0, y0 + cote + 30, f"{v['les_points_deplaces']} points de la maille déplacés", 0, GRIS)
    lx, ly = 70, 520
    for j, e in enumerate((-2, -1, 0, 1, 2)):
        art.rectangle([lx + 70 * j, ly, lx + 70 * j + 14, ly + 14], fill=LES_ENTIERS[e], outline=TRAIT)
        ecrire(lx + 70 * j + 20, ly, _fr(e, 0), 0, GRIS)
    ecrire(lx, ly + 24, "l'entier du chunk moins celui de la référence ; le cadre noir est le bloc de 262", 0, GRIS)

    # ── PANNEAU 2 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 580, "LA PART SUR LA BONNE SPIRE, AVANT ○ ET APRÈS ●")
    gx0, gx1 = 960, 1180
    xx = lambda v_: gx0 + (gx1 - gx0) * v_  # noqa: E731
    y = 150
    for v_ in (0.0, 0.5, 1.0):
        art.line([xx(v_), y - 18, xx(v_), y + 9 * 30 + 50], fill=TRAIT)
        ecrire(xx(v_) - 8, y - 36, _fr(v_, 1), 0, GRIS)
    groupes = [(n, list(v["les_blocs"].items())) for n, v in d["les_voisinages"].items()]
    for nom, blocs in groupes:
        ecrire(736, y - 7, f"voisinage de {nom[-3:]}", 0, ENCRE)
        y += 22
        for j, (b, x) in enumerate(blocs):
            a, z = x["avant"]["la_part_sur_la_bonne_spire"], x["apres"]["la_part_sur_la_bonne_spire"]
            ecrire(750, y - 7, f"{'le bloc' if j == 0 else 'voisin'} ({b.replace('_', ', ')}) : "
                               f"{x['les_rates_rendus_justes']} / {x['les_justes_rendus_rates']}", 0,
                   ENCRE if j == 0 else GRIS)
            coul = BON if z > a else ALERTE if z < a else GRIS
            art.line([xx(a), y, xx(z), y], fill=coul, width=3)
            art.ellipse([xx(a) - 5, y - 5, xx(a) + 5, y + 5], outline=GRIS, width=2)
            art.ellipse([xx(z) - 4, y - 4, xx(z) + 4, y + 4], fill=coul)
            points += [(xx(a), y), (xx(z), y)]
            traces["lignes"] += 1
            ecrire(1196, y - 7, f"{_fr(a, 2)} → {_fr(z, 2)}", 0, coul)
            y += 24
        y += 10
    r = d["les_reguliers_reunis"]
    ecrire(736, y, f"les {r['les_blocs']} blocs réguliers, marchés chacun seul : {_fr(r['avant'], 4)} → {_fr(r['apres'], 4)}",
           0, ENCRE)
    ecrire(736, y + 18, f"{r['les_rates_rendus_justes']} ratés rendus justes, {r['les_justes_rendus_rates']} justes rendus "
                        "ratés", 0, ENCRE)
    ecrire(736, 556, "à gauche des parts : ratés rendus justes / justes rendus ratés", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 596, L_, H_], fill=BANDE)
    ecrire(50, 608, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    v9 = d["les_voisinages"]["le_bloc_de_259"]
    ecrire(50, 630, f"★ un seul choix faux passe à toute une région : sur le voisinage de 259, "
                    f"{v9['les_marches'].get('1', 0)} chunks mis à une spire de la référence, "
                    f"{v9['les_voisins_reunis']['les_justes_rendus_rates']} justes des voisins rendus ratés.", moyen, ENCRE)
    ecrire(50, 656, "⚠ ce qui n'est PAS établi : quelle arête a porté le faux choix ; un glissement étalé sur plusieurs "
                    "chunks ; une boucle.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_267.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure",
      all(f"DE {_fr(x['le_centre']['avant']['la_part_sur_la_bonne_spire'], 4)} À "
          f"{_fr(x['le_centre']['apres']['la_part_sur_la_bonne_spire'], 4)}" in le_titre(d)
          for x in d["les_voisinages"].values()))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n = sum(len(x["les_blocs"]) for x in d["les_voisinages"].values())
    v("★★★★ chaque voisinage a sa carte, chaque bloc sa ligne", traces == {"cartes": 2, "lignes": n}, str(traces))
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
                   default=RACINE / "docs" / "images" / "267_lescalier_porte_t_il_le_choix_de_la_spire.png")
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
