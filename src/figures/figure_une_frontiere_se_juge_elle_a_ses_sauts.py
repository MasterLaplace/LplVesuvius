"""L'escalier après le jugement des frontières : l'entier de chaque chunk, et ce que la correction fait de chaque bloc.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, l'escalier JUGÉ de chaque voisinage : sur celui de `259` la grande
région de `267` est revenue à la référence, et avec elle tout le reste ; sur celui de `257` une marche reste sous le bloc
central. En dessous, le bloc `(160, 160)` marché seul, où une marche que ses sauts disent vraie couvre des chunks que le juge
tient pour justes. À droite, bloc par bloc, la part sur la bonne spire avant et après.

  uv run python src/figures/figure_une_frontiere_se_juge_elle_a_ses_sauts.py \\
      --sortie docs/images/268_une_frontiere_se_juge_elle_a_ses_sauts.png
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
from figure_lescalier_porte_t_il_le_choix_de_la_spire import LES_ENTIERS, VIDE, _fr  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "une_frontiere_se_juge_elle_a_ses_sauts.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 760
LE_BLOC_SEUL = "160_160"


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_plus_grande_fausse(d: dict) -> dict:
    """La frontière jugée fausse qui a ramené le plus de chunks, sur l'un ou l'autre voisinage."""
    return max((f for v in d["les_voisinages"].values() for f in v["le_journal"]),
               key=lambda f: (f["les_chunks_decales"], f["les_aretes"]))


def le_titre(d: dict) -> str:
    t = " ; ".join(f"LE BLOC DE {n[-3:]} DE {_fr(v['le_centre']['avant']['la_part_sur_la_bonne_spire'], 4)} À "
                   f"{_fr(v['le_centre']['apres']['la_part_sur_la_bonne_spire'], 4)}" for n, v in d["les_voisinages"].items())
    return f"LES FRONTIÈRES JUGÉES À LEURS SAUTS : {t}"


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

    def carte(k, x0, y0, cote, cadre_central):
        n = len(k)
        px = cote / n
        for r in range(n):
            for c in range(n):
                e = k[r][c]
                coul = VIDE if e is None else LES_ENTIERS.get(max(-2, min(2, e)), ENCRE)
                art.rectangle([x0 + c * px, y0 + r * px, x0 + (c + 1) * px - 1, y0 + (r + 1) * px - 1], fill=coul)
        if cadre_central:
            t = n // 3
            art.rectangle([x0 + t * px, y0 + t * px, x0 + 2 * t * px, y0 + 2 * t * px], outline=ENCRE, width=2)
        points.append((x0 + cote, y0 + cote))
        traces["cartes"] += 1

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · l'escalier de 267, puis chaque frontière dont la médiane des sauts ne "
                   "dit pas l'écart d'entiers ramenée, la plus fausse d'abord · une passe", petit, GRIS)

    # ── PANNEAU 1 · LES ESCALIERS JUGÉS ────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 640, "L'ESCALIER, UNE FOIS LES FRONTIÈRES JUGÉES")
    for i, (nom, v) in enumerate(d["les_voisinages"].items()):
        x0, y0 = 70 + 315 * i, 150
        carte(v["lescalier"], x0, y0, 288, True)
        ecrire(x0, y0 - 24, f"le voisinage du bloc de {nom[-3:]}", 0, ENCRE)
        conv = "sans frontière fausse à la fin" if not v["reste_fausse"] else "arrêté par la garde : une fausse reste"
        ecrire(x0, y0 + 300, f"{v['les_frontieres_fausses_corrigees']} frontières ramenées", 0, GRIS)
        ecrire(x0, y0 + 318, conv, 0, GRIS if not v["reste_fausse"] else ALERTE)
        ecrire(x0, y0 + 336, "chunks par entier : " + ", ".join(
            f"{_fr(int(a), 0)} : {b}" for a, b in sorted(v["les_marches"].items(), key=lambda kv: int(kv[0]))), 0, GRIS)
    b = d["les_blocs"][LE_BLOC_SEUL]
    carte(b["lescalier"], 70, 510, 96, False)
    ecrire(180, 512, f"le bloc ({LE_BLOC_SEUL.replace('_', ', ')}), marché seul : {len(b['le_journal'])} frontière ramenée",
           0, ENCRE)
    ecrire(180, 530, f"sa part : {_fr(b['le_bloc']['avant']['la_part_sur_la_bonne_spire'], 4)} → "
                     f"{_fr(b['le_bloc']['apres']['la_part_sur_la_bonne_spire'], 4)}, "
                     f"{b['le_bloc']['les_justes_rendus_rates']} justes rendus ratés", 0, ALERTE)
    ecrire(180, 548, "une marche que ses sauts disent vraie, sur des chunks que le juge tient pour justes", 0, GRIS)
    for j, e in enumerate((-2, -1, 0, 1, 2)):
        art.rectangle([180 + 60 * j, 580, 194 + 60 * j, 594], fill=LES_ENTIERS[e], outline=TRAIT)
        ecrire(200 + 60 * j, 580, _fr(e, 0), 0, GRIS)

    # ── PANNEAU 2 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 640, "LA PART SUR LA BONNE SPIRE, AVANT ○ ET APRÈS ●")
    gx0, gx1 = 960, 1180
    xx = lambda v_: gx0 + (gx1 - gx0) * v_  # noqa: E731
    y = 150
    for v_ in (0.0, 0.5, 1.0):
        art.line([xx(v_), y - 18, xx(v_), y + 9 * 26 + 60], fill=TRAIT)
        ecrire(xx(v_) - 8, y - 36, _fr(v_, 1), 0, GRIS)
    for nom, v in d["les_voisinages"].items():
        ecrire(736, y - 7, f"voisinage de {nom[-3:]}", 0, ENCRE)
        y += 22
        for j, (bn, x) in enumerate(v["les_blocs"].items()):
            a, z = x["avant"]["la_part_sur_la_bonne_spire"], x["apres"]["la_part_sur_la_bonne_spire"]
            ecrire(750, y - 7, f"{'le bloc' if j == 0 else 'voisin'} ({bn.replace('_', ', ')}) : "
                               f"{x['les_rates_rendus_justes']} / {x['les_justes_rendus_rates']}", 0, ENCRE if j == 0 else GRIS)
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
    f = la_plus_grande_fausse(d)
    ecrire(736, y + 48, f"la plus grande frontière fausse : {f['les_aretes']} arêtes, saut médian "
                        f"{_fr(f['le_saut_median_voxels'], 2)} voxels,", 0, ENCRE)
    ecrire(736, y + 66, f"{f['les_chunks_decales']} chunks ramenés à la référence", 0, ENCRE)
    ecrire(736, 616, "à gauche des parts : ratés rendus justes / justes rendus ratés", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    j9 = d["les_voisinages"]["le_bloc_de_259"]["le_journal"]
    sm = sorted(abs(x["le_saut_median_voxels"]) for x in j9)
    ecrire(50, 690, f"★ juger une frontière à ses sauts défait la fausse frontière de 267, et avec elle toutes les marches "
                    f"de 259, dont les sauts médians vont de {_fr(sm[0], 1)} à {_fr(sm[-1], 1)} voxels.", moyen, ENCRE)
    ecrire(50, 716, "⚠ ce qui n'est PAS établi : pourquoi la marche seule voit une vraie marche sur (160, 160) ; un "
                    "jugement qui converge sur 257 ; une boucle.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_268.png"
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
    v("★★★★ chaque voisinage et le bloc seul ont leur carte, chaque bloc sa ligne",
      traces == {"cartes": 3, "lignes": n}, str(traces))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ un jugement arrêté par la garde est écrit comme tel",
      ("arrêté par la garde" in txt) == any(x["reste_fausse"] for x in d["les_voisinages"].values()))
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
                   default=RACINE / "docs" / "images" / "268_une_frontiere_se_juge_elle_a_ses_sauts.png")
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
