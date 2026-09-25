"""La procédure sans juge de 265, sur tous les blocs candidats du segment : ce qu'elle rend juste, ce qu'elle rend raté.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, la carte des blocs du segment : chacun coloré par ce que la procédure
y fait à la part sur la bonne spire, les neuf blocs déjà publiés cerclés. À droite, les blocs rangés par leur gain net, et ce
que le segment entier devient.

  uv run python src/figures/figure_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.py \\
      --sortie docs/images/275_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"
LES_NEUF = {(16, 176), (160, 144), (32, 128), (112, 192), (160, 160), (208, 176), (256, 128), (304, 128), (352, 128)}

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
IMMOBILE = (206, 208, 211)
NON_DECIDE = (238, 226, 214)
L_, H_ = 1360, 760
LE_BLOC = 16


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


def le_sens(b: dict) -> int | None:
    """+1, −1 ou 0 selon ce que la procédure fait à la part du bloc ; None s'il n'est pas décidé."""
    if not b.get("decidable"):
        return None
    x = (b["apres"]["la_part_sur_la_bonne_spire"] or 0) - (b["avant"]["la_part_sur_la_bonne_spire"] or 0)
    return (x > 0) - (x < 0)


def le_gain(b: dict) -> int:
    return b["les_rates_rendus_justes"] - b["les_justes_rendus_rates"]


def le_titre(d: dict) -> str:
    g = d["les_reunis"]
    return (f"SUR LES {g['les_blocs']} BLOCS DÉCIDÉS DU SEGMENT, LA PROCÉDURE SANS JUGE REND {g['les_rates_rendus_justes']} "
            f"RATÉS JUSTES ET {g['les_justes_rendus_rates']} JUSTES RATÉS : UN GAIN NET DE {_fr(g['le_gain_net'])}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"cases": {1: 0, -1: 0, 0: 0, None: 0}, "barres": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    g = d["les_reunis"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"20230702185753 · m7, côté plus · la procédure de 265, une passe · {d['les_candidats']} blocs candidats "
                   f"· le juge ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · LA CARTE DES BLOCS ────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 640, 640, "CE QUE LA PROCÉDURE FAIT À CHAQUE BLOC")
    blocs = d["les_blocs"]
    rs = sorted({b["la_rangee"] for b in blocs})
    cs = sorted({b["la_colonne"] for b in blocs})
    r0, c0 = rs[0], cs[0]
    nr, nc = (rs[-1] - r0) // LE_BLOC + 1, (cs[-1] - c0) // LE_BLOC + 1
    cote = int(min(500 / max(nc, 1), 470 / max(nr, 1)))
    gx0, gy0 = 70, 140
    for b in blocs:
        i, j = (b["la_rangee"] - r0) // LE_BLOC, (b["la_colonne"] - c0) // LE_BLOC
        x, y = gx0 + j * cote, gy0 + i * cote
        s = le_sens(b)
        coul = {1: BON, -1: ALERTE, 0: IMMOBILE, None: NON_DECIDE}[s]
        art.rectangle([x + 1, y + 1, x + cote - 2, y + cote - 2], fill=coul)
        if (b["la_rangee"], b["la_colonne"]) in LES_NEUF:
            art.rectangle([x, y, x + cote - 1, y + cote - 1], outline=ENCRE, width=2)
        traces["cases"][s] += 1
        points.append((x + cote, y + cote))
    lx, ly = gx0 + nc * cote + 16, 150
    for k, (coul, texte) in enumerate(((BON, f"la part monte · {g['les_blocs_qui_montent']}"),
                                       (ALERTE, f"elle descend · {g['les_blocs_qui_descendent']}"),
                                       (IMMOBILE, f"elle ne bouge pas · {g['les_blocs_immobiles']}"),
                                       (NON_DECIDE, f"non décidé · {len(d['les_non_decides'])}"))):
        art.rectangle([lx, ly + 22 * k, lx + 12, ly + 22 * k + 12], fill=coul)
        ecrire(lx + 18, ly + 22 * k - 1, texte, 0, ENCRE)
    art.rectangle([lx, ly + 92, lx + 12, ly + 104], outline=ENCRE, width=2)
    ecrire(lx + 18, ly + 91, "publié par 265 et 270", 0, ENCRE)
    ecrire(70, gy0 + nr * cote + 10, "rangée de blocs vers le bas, colonne vers la droite, un bloc = 16 × 16 chunks", 0, GRIS)

    # ── PANNEAU 2 · LES BLOCS RANGÉS PAR LEUR GAIN ──────────────────────────────────────────────────────────────────
    panneau(660, 80, 1310, 640, "LES BLOCS DÉCIDÉS, RANGÉS PAR LEUR GAIN NET")
    ok = sorted((b for b in blocs if b.get("decidable")), key=le_gain)
    bx0, bx1, by0, by1 = 700, 1290, 150, 470
    gmax = max([abs(le_gain(b)) for b in ok] + [1])
    zero = (by0 + by1) / 2
    art.line([bx0, zero, bx1, zero], fill=GRIS)
    larg = (bx1 - bx0) / max(len(ok), 1)
    for k, b in enumerate(ok):
        h = le_gain(b) / gmax * (by1 - by0) / 2
        x = bx0 + k * larg
        if h:
            art.rectangle([x, min(zero, zero - h), x + max(larg - 1, 1), max(zero, zero - h)],
                          fill=BON if h > 0 else ALERTE)
        traces["barres"] += 1
        points.append((x, zero - h))
    ecrire(bx0, by0 - 18, f"+{gmax} points", 0, GRIS)
    ecrire(bx0, by1 + 4, f"−{gmax} points", 0, GRIS)
    s_ = d["le_segment_entier"]
    lignes = [
        (f"réunis : la part sur la bonne spire passe de {_fr(g['avant'])} à {_fr(g['apres'])}, "
         f"{g['les_points_notes']} points notés", ENCRE),
        (f"les blocs couvrent {_fr(d['la_part_des_points_notes_du_segment_dans_les_blocs'])} des points notés du segment",
         GRIS),
        (f"le segment entier : de {_fr(s_['avant']['la_part_sur_la_bonne_spire'])} à "
         f"{_fr(s_['apres']['la_part_sur_la_bonne_spire'])}, {s_['avant']['les_points_notes']} points notés", ENCRE),
    ]
    for k, (t, c) in enumerate(lignes):
        ecrire(700, 520 + 26 * k, t, 0, c)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    m = d["le_controle_du_miroir"]["les_piles"]
    rp = d["la_reproduction"]["les_voisinages"]
    ecrire(50, 690, f"rendu depuis le miroir local : {sum(1 for x in m.values() if x.get('les_voxels_differents') == 0)} "
                    f"piles sur {len(m)} identiques au rendu à distance ; {sum(1 for x in rp.values() if x['reproduit'])} "
                    f"voisinages publiés sur {len(rp)} redonnent leurs comptes", moyen, ENCRE)
    ecrire(50, 714, "⚠ ce qui n'est PAS établi : la spire suivante, transférée depuis celle-ci ; un autre côté, une autre "
                    "prédiction ; une seconde passe.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_275.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    g = d["les_reunis"]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(g['le_gain_net'])}" in le_titre(d)
      and f"LES {g['les_blocs']} BLOCS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    c = traces["cases"]
    v("★★★★ une case par bloc candidat, et ses couleurs redonnent les comptes de la réunion",
      sum(c.values()) == d["les_candidats"] == len(d["les_blocs"]) and c[1] == g["les_blocs_qui_montent"]
      and c[-1] == g["les_blocs_qui_descendent"] and c[0] == g["les_blocs_immobiles"]
      and c[None] == len(d["les_non_decides"]), str(c))
    v("★★★★ une barre par bloc décidé, et leurs gains font le gain net",
      traces["barres"] == g["les_blocs"]
      and sum(le_gain(b) for b in d["les_blocs"] if b.get("decidable")) == g["le_gain_net"], str(traces["barres"]))
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
                   default=RACINE / "docs" / "images" / "275_la_procedure_sans_juge_tient_elle_sur_le_segment_entier.png")
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
