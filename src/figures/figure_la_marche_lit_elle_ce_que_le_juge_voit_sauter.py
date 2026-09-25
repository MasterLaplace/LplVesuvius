"""D'un chunk juste à son voisin raté : ce que le juge voit sauter, et ce que la marche en lit.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, CHAQUE PAIRE qui franchit la frontière du juge, `ΔD` contre `ΔE`,
pour les deux voisinages : les points sont serrés autour de trente voxels d'écart jugé, loin des soixante-douze d'une spire
entière, et sous la droite d'une marche qui lirait tout. À droite, la part lue et le saut jugé médian, famille par famille.

  uv run python src/figures/figure_la_marche_lit_elle_ce_que_le_juge_voit_sauter.py \\
      --sortie docs/images/269_la_marche_lit_elle_ce_que_le_juge_voit_sauter.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_marche_lit_elle_ce_que_le_juge_voit_sauter.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
L_, H_ = 1360, 700
LES_COULEURS = {"le_bloc_de_257": BON, "le_bloc_de_259": CONTRE}
LA_PORTEE = 150.0


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
    f = d["dun_seul_tenant"]["franchit"]
    return (f"D'UN CHUNK JUSTE À SON VOISIN RATÉ, LE JUGE VOIT SAUTER {_fr(f['le_saut_juge_median_voxels'], 1)} VOXELS EN "
            f"MÉDIANE, ET LA MARCHE EN LIT {_fr(f['la_part_lue'], 2)}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"paires": 0, "lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · m7, côté plus · paires de chunks qui se touchent, l'un juste et l'autre raté selon le "
                   "juge, orientées du juste vers le raté · la pente passe par zéro", petit, GRIS)

    # ── PANNEAU 1 · LES PAIRES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 700, 560, "ΔD CONTRE ΔE, POUR CHAQUE PAIRE QUI FRANCHIT")
    gx0, gx1, gy0, gy1 = 110, 670, 120, 500
    xx = lambda v: gx0 + (gx1 - gx0) * (v + LA_PORTEE) / (2 * LA_PORTEE)  # noqa: E731
    yy = lambda v: gy1 - (gy1 - gy0) * (v + LA_PORTEE) / (2 * LA_PORTEE)  # noqa: E731
    for v in (-150, -72, -36, 0, 36, 72, 150):
        art.line([xx(v), gy0, xx(v), gy1], fill=GRIS if v == 0 else TRAIT)
        art.line([gx0, yy(v), gx1, yy(v)], fill=GRIS if v == 0 else TRAIT)
        ecrire(xx(v) - 10, gy1 + 6, _fr(v, 0), 0, GRIS)
        ecrire(gx0 - 36, yy(v) - 7, _fr(v, 0), 0, GRIS)
    ecrire(gx0, gy1 + 24, "ΔE, l'écart jugé, en voxels ; en ordonnée ΔD, l'écart de la marche", 0, GRIS)
    p0 = d["la_pente_de_la_rampe"]
    art.line([xx(-LA_PORTEE), yy(-p0 * LA_PORTEE), xx(LA_PORTEE), yy(p0 * LA_PORTEE)], fill=ALERTE, width=2)
    ecrire(xx(60), yy(p0 * 150) + 4, "une marche qui lirait tout", 0, ALERTE)
    for k, (nom, v) in enumerate(d["les_voisinages"].items()):
        coul = LES_COULEURS[nom]
        for e, dd in v["les_paires_qui_franchissent"]:
            x, y = xx(max(-LA_PORTEE, min(LA_PORTEE, e))), yy(max(-LA_PORTEE, min(LA_PORTEE, dd)))
            art.ellipse([x - 2, y - 2, x + 2, y + 2], fill=coul)
            points.append((x, y))
            traces["paires"] += 1
        pe = v["franchit"]["la_pente"]
        art.line([xx(-LA_PORTEE), yy(-pe * LA_PORTEE), xx(LA_PORTEE), yy(pe * LA_PORTEE)], fill=coul, width=2)
        ecrire(gx0 + 10, gy0 + 6 + 18 * k, f"voisinage de {nom[-3:]} : {v['franchit']['les_paires']} paires, pente "
                                           f"{_fr(pe, 2)}", 0, coul)

    # ── PANNEAU 2 · FAMILLE PAR FAMILLE ────────────────────────────────────────────────────────────────────────────
    panneau(720, 80, 1310, 560, "CE QUE LE JUGE VOIT SAUTER, ET CE QUE LA MARCHE EN LIT")
    lignes = [("d'un seul tenant, les deux voisinages", d["dun_seul_tenant"]),
              ("   le voisinage de 257", d["les_voisinages"]["le_bloc_de_257"]),
              ("   le voisinage de 259", d["les_voisinages"]["le_bloc_de_259"]),
              ("bloc par bloc, les dix blocs", d["bloc_par_bloc"])]
    ecrire(736, 130, "saut jugé médian", 0, GRIS)
    ecrire(880, 130, "part lue", 0, GRIS)
    ecrire(960, 130, "0", 0, GRIS)
    ecrire(1236, 130, "1", 0, GRIS)
    y = 160
    bx0, bx1 = 962, 1240
    for titre, fam in lignes:
        for cle, nom in (("franchit", "qui franchissent"), ("justes", "justes, le témoin")):
            q = fam[cle]
            ecrire(736, y - 14, f"{titre}, {nom} ({q['les_paires']})", 0, ENCRE if cle == "franchit" else GRIS)
            ecrire(736, y + 2, f"{_fr(q['le_saut_juge_median_voxels'], 1)} voxels", 0, GRIS)
            pl = q["la_part_lue"] or 0.0
            coul = BON if cle == "franchit" else TRAIT
            art.rectangle([bx0, y + 2, bx0 + (bx1 - bx0) * max(0.0, min(1.0, pl)), y + 12], fill=coul)
            points.append((bx0 + (bx1 - bx0) * max(0.0, min(1.0, pl)), y + 12))
            ecrire(880, y + 2, _fr(q["la_part_lue"], 4), 0, ENCRE)
            traces["lignes"] += 1
            y += 44
        y += 4
    ecrire(736, 536, "part lue : la pente de ΔD contre ΔE, rapportée à celle de la rampe, " + _fr(p0, 4), 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 576, L_, H_], fill=BANDE)
    ecrire(50, 588, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 610, "★ les ratés se font en pente, d'un chunk à l'autre, et la marche ne lit qu'une partie de cette pente : "
                    "il n'y a presque pas de marche franche à trouver.", moyen, ENCRE)
    ecrire(50, 636, "⚠ ce qui n'est PAS établi : l'erreur du juge, qui tire la pente vers zéro ; si le juge a raison sur ces "
                    "ratés.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_269.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    f = d["dun_seul_tenant"]["franchit"]
    v("★★★ le titre LIT la mesure", f"EN LIT {_fr(f['la_part_lue'], 2)}" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    n = sum(len(x["les_paires_qui_franchissent"]) for x in d["les_voisinages"].values())
    v("★★★★ chaque paire qui franchit a son point, chaque famille ses deux lignes",
      traces == {"paires": n, "lignes": 8}, str(traces))
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
                   default=RACINE / "docs" / "images" / "269_la_marche_lit_elle_ce_que_le_juge_voit_sauter.png")
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
