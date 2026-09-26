"""La procédure sans juge de 265 sur le deuxième saut de la bande w028-037 : ce qu'elle fait à chaque bloc noté.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, les blocs notés du deuxième saut, à leur place sur la bande,
colorés par ce que la procédure fait à leur part sur la bonne spire, les deux blocs du contrôle cerclés. En bas à gauche,
les blocs rangés par leur gain net. En bas à droite, le deuxième saut entier avant et après, et ce que la marche lit de ses
ratés.

  uv run python src/figures/figure_la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.py \\
      --sortie docs/images/283_la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
IMMOBILE = (206, 208, 211)
NON_DECIDE = (238, 226, 214)
L_, H_ = 1360, 680
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
    if not b.get("decidable"):
        return None
    x = (b["apres"]["la_part_sur_la_bonne_spire"] or 0) - (b["avant"]["la_part_sur_la_bonne_spire"] or 0)
    return (x > 0) - (x < 0)


def le_gain(b: dict) -> int:
    return b["les_rates_rendus_justes"] - b["les_justes_rendus_rates"]


def le_titre(d: dict) -> str:
    g = d["les_reunis"]
    return (f"AU DEUXIÈME SAUT DE LA BANDE, SUR {g['les_blocs']} BLOCS, LA PROCÉDURE REND {g['les_rates_rendus_justes']} "
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
    ecrire(50, 52, f"20260623142658-w028-037 · la tranche de 248 · m7, côté plus · la référence est le premier saut de 281 · "
                   f"{d['les_blocs_notes']} blocs notés · le juge, la deuxième couche, ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · LA CARTE DES BLOCS CANDIDATS ──────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 210, "CE QUE LA PROCÉDURE FAIT À CHAQUE BLOC NOTÉ, À SA PLACE SUR LA TRANCHE")
    blocs = d["les_blocs"]
    controle = {tuple(int(x) for x in s.split("_")) for s in d["le_controle_du_miroir"]["les_blocs"]}
    c0 = min(b["la_colonne"] for b in blocs)
    r0 = min(b["la_rangee"] for b in blocs)
    nc = (max(b["la_colonne"] for b in blocs) - c0) // LE_BLOC + 1
    nr = (max(b["la_rangee"] for b in blocs) - r0) // LE_BLOC + 1
    cote = max(4, int(min(1220 / max(nc, 1), 90 / max(nr, 1))))
    gx0, gy0 = 70, 120
    for b in blocs:
        i, j = (b["la_rangee"] - r0) // LE_BLOC, (b["la_colonne"] - c0) // LE_BLOC
        x, y = gx0 + j * cote, gy0 + i * cote
        s = le_sens(b)
        art.rectangle([x + 1, y + 1, x + cote - 2, y + cote - 2], fill={1: BON, -1: ALERTE, 0: IMMOBILE, None: NON_DECIDE}[s])
        if (b["la_rangee"], b["la_colonne"]) in controle:
            art.rectangle([x, y, x + cote - 1, y + cote - 1], outline=ENCRE, width=2)
        traces["cases"][s] += 1
        points.append((x + cote, y + cote))
    ly = gy0 + nr * cote + 20
    for k, (coul, texte) in enumerate(((BON, f"monte · {g['les_blocs_qui_montent']}"),
                                       (ALERTE, f"descend · {g['les_blocs_qui_descendent']}"),
                                       (IMMOBILE, f"immobile · {g['les_blocs_immobiles']}"),
                                       (NON_DECIDE, f"non décidé · {len(d['les_non_decides'])}"))):
        lx = 70 + 170 * k
        art.rectangle([lx, ly, lx + 12, ly + 12], fill=coul)
        ecrire(lx + 18, ly - 1, texte, 0, ENCRE)
    art.rectangle([750, ly, 762, ly + 12], outline=ENCRE, width=2)
    ecrire(768, ly - 1, "contrôle", 0, ENCRE)
    ecrire(70, 182, "colonne de blocs vers la droite, rangée vers le bas, un bloc = 16 × 16 chunks", 0, GRIS)

    # ── PANNEAU 2 · LES BLOCS RANGÉS PAR LEUR GAIN ──────────────────────────────────────────────────────────────────
    panneau(50, 226, 700, 560, "LES BLOCS DÉCIDÉS, RANGÉS PAR LEUR GAIN NET")
    ok = sorted((b for b in blocs if b.get("decidable")), key=le_gain)
    bx0, bx1, by0, by1 = 90, 680, 290, 520
    gmax = max([abs(le_gain(b)) for b in ok] + [1])
    zero = (by0 + by1) / 2
    art.line([bx0, zero, bx1, zero], fill=GRIS)
    larg = (bx1 - bx0) / max(len(ok), 1)
    for k, b in enumerate(ok):
        h = le_gain(b) / gmax * (by1 - by0) / 2
        x = bx0 + k * larg
        if h:
            art.rectangle([x, min(zero, zero - h), x + max(larg - 1, 1), max(zero, zero - h)], fill=BON if h > 0 else ALERTE)
        traces["barres"] += 1
        points.append((x, zero - h))
    ecrire(bx0, by0 - 18, f"+{gmax} points", 0, GRIS)
    ecrire(bx0, by1 + 4, f"−{gmax} points", 0, GRIS)

    # ── PANNEAU 3 · LA CHAÎNE ET LA BANDE ENTIÈRE ───────────────────────────────────────────────────────────────────
    panneau(716, 226, 1310, 560, "LE DEUXIÈME SAUT ENTIER, ET CE QUE LA MARCHE LIT")
    e = d["le_deuxieme_saut_entier"]
    lm = d["ce_que_la_marche_lit"]
    dr = lm["la_decision_retient"]
    for k, (texte, c) in enumerate((
            (f"deuxième saut entier : {e['avant']['les_points_notes']} points notés, de "
             f"{_fr(e['avant']['la_part_sur_la_bonne_spire'])} à {_fr(e['apres']['la_part_sur_la_bonne_spire'])}", ENCRE),
            (f"blocs décidés : {g['les_points_notes']} points notés, de {_fr(g['avant'])} à {_fr(g['apres'])}", ENCRE),
            (f"points corrigés : {g['les_points_corriges']} · glissade reprise de 261 : {_fr(d['la_glissade_voxels'])} voxels",
             GRIS),
            (f"la marche répare {_fr(lm['la_part_des_rates_que_la_marche_repare'])} des {lm['les_rates']} ratés, et casse "
             f"{_fr(lm['la_part_des_justes_que_la_marche_casse'])} des {lm['les_justes']} justes", ENCRE),
            (f"la décision retient {dr['des_reparables']} des {lm['les_rates_reparables']} réparables et "
             f"{dr['des_cassables']} des {lm['les_justes_cassables']} cassables", ENCRE))):
        ecrire(736, 270 + 30 * k, texte, 0, c)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 576, L_, H_], fill=BANDE)
    ecrire(50, 588, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    m = d["le_controle_du_miroir"]["les_piles"]
    ecrire(50, 610, f"rendu depuis le miroir : {sum(1 for x in m.values() if x == 0)} piles sur {len(m)} identiques au rendu à "
                    f"distance ; la chaîne redonne 248, et son premier saut celui de 281", moyen, ENCRE)
    ecrire(50, 634, "⚠ ce qui n'est PAS établi : le troisième saut, reparti du deuxième corrigé ; un recalage sur la feuille.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_283.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    g = d["les_reunis"]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(g['le_gain_net'])}" in le_titre(d)
      and f"SUR {g['les_blocs']} BLOCS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    c = traces["cases"]
    v("★★★★ une case par bloc noté, et ses couleurs redonnent les comptes de la réunion",
      sum(c.values()) == d["les_blocs_notes"] == len(d["les_blocs"]) and c[1] == g["les_blocs_qui_montent"]
      and c[-1] == g["les_blocs_qui_descendent"] and c[0] == g["les_blocs_immobiles"]
      and c[None] == len(d["les_non_decides"]), str(c))
    v("★★★★ une barre par bloc décidé, et leurs gains font le gain net",
      traces["barres"] == g["les_blocs"] and sum(le_gain(b) for b in d["les_blocs"] if b.get("decidable")) == g["le_gain_net"])
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
                   default=RACINE / "docs" / "images" / "283_la_procedure_sans_juge_corrige_t_elle_le_deuxieme_saut_de_la_bande.png")
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
