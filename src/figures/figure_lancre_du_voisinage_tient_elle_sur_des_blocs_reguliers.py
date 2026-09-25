"""La décision de 264 avec l'ancre des voisins, sur les blocs réguliers et, en repère, sur les deux blocs choisis de 265.

⚠⚠ **Ce que cette figure doit rendre évident.** Bloc par bloc, la part sur la bonne spire avant, après la décision avec l'ancre
des voisins, et après la même décision avec l'ancre du bloc, sur la même marche. En tête, les deux blocs choisis de `265` ; en
dessous, les blocs pris à pas réguliers, qui n'avaient jamais vu cette procédure. À droite, ce que chaque ancre y change : le
poids que le mélange donne aux spires glissées.

  uv run python src/figures/figure_lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.py \\
      --sortie docs/images/270_lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.png
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
M = RACINE / "docs" / "mesures"
LA_MESURE = M / "lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.json"
DE_265 = M / "le_voisinage_dit_il_quel_niveau_est_le_bon.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (200, 205, 212)
L_, H_ = 1360, 620


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
    d["_265"] = json.loads(DE_265.read_text())
    return d


def les_lignes(d: dict) -> list[tuple[str, dict, bool]]:
    """Les deux blocs choisis de 265 d'abord, puis les réguliers dans l'ordre de leur part avant."""
    choisis = [(f"le bloc de {n[-3:]}, choisi", b, True) for n, b in d["_265"]["les_blocs"].items()]
    reg = sorted(((le_nom(d, b), b, False) for b in d["les_blocs"].values()),
                 key=lambda t: (t[1]["avant"]["la_part_sur_la_bonne_spire"], t[0]))
    return choisis + reg


def le_nom(d: dict, b: dict) -> str:
    """Un bloc régulier, et le bloc choisi qu'il touche s'il en touche un : lu dans ses voisins, pas écrit à la main."""
    touche = [n[-3:] for n, c in d["_265"]["les_blocs"].items() if [c["la_rangee"], c["la_colonne"]] in b["les_voisins"]]
    return f"({b['la_rangee']}, {b['la_colonne']})" + "".join(f", voisin du bloc de {t}" for t in touche)


def les_abimes(d: dict) -> list[tuple[str, int]]:
    """Les blocs réguliers où l'ancre des voisins rend des justes ratés, avec leur nombre."""
    return [(le_nom(d, b), b["lancre_du_voisinage"]["la_decision"]["les_justes_rendus_rates"])
            for b in d["les_blocs"].values() if b["lancre_du_voisinage"]["la_decision"]["les_justes_rendus_rates"]]


def la_part(b: dict, ancre: str | None) -> float:
    return b["avant"]["la_part_sur_la_bonne_spire"] if ancre is None else \
        b[ancre]["la_decision"]["apres"]["la_part_sur_la_bonne_spire"]


def le_titre(d: dict) -> str:
    g = d["les_reunis"]
    v = g["lancre_du_voisinage"]
    return (f"SUR LES BLOCS RÉGULIERS, L'ANCRE DES VOISINS : DE {_fr(g['avant'], 4)} À {_fr(v['apres'], 4)}, "
            f"{v['les_rates_rendus_justes']} RATÉS RENDUS JUSTES ET {v['les_justes_rendus_rates']} JUSTES RENDUS RATÉS")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {"lignes": 0}

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
                   "la médiane sur les voisins seuls · la décision de 264 · une passe", petit, GRIS)
    lignes = les_lignes(d)

    # ── PANNEAU 1 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 820, 510, "LA PART SUR LA BONNE SPIRE : AVANT ○, ANCRE DES VOISINS ●, ANCRE DU BLOC ◆")
    gx0, gx1, gy0, pas, lo = 330, 600, 150, 36, 0.4
    xx = lambda v: gx0 + (gx1 - gx0) * (v - lo) / (1.0 - lo)  # noqa: E731
    for v in (0.4, 0.7, 1.0):
        art.line([xx(v), gy0 - 18, xx(v), gy0 + pas * len(lignes) - 16], fill=TRAIT)
        ecrire(xx(v) - 8, gy0 - 36, _fr(v, 1), 0, GRIS)
    ecrire(630, gy0 - 36, "rendus justes / rendus ratés", 0, GRIS)
    for k, (nom, b, choisi) in enumerate(lignes):
        y = gy0 + pas * k
        ecrire(66, y - 7, f"{nom} · {b['avant']['les_points_notes']} points", 0, ENCRE if choisi else GRIS)
        a, z, w = la_part(b, None), la_part(b, "lancre_du_voisinage"), la_part(b, "lancre_du_bloc")
        coul = BON if z > a else ALERTE if z < a else GRIS
        art.line([xx(a), y, xx(z), y], fill=coul, width=3)
        art.ellipse([xx(a) - 5, y - 5, xx(a) + 5, y + 5], outline=GRIS, width=2)
        art.polygon([(xx(w), y - 6), (xx(w) + 6, y), (xx(w), y + 6), (xx(w) - 6, y)], fill=PALE)
        art.ellipse([xx(z) - 4, y - 4, xx(z) + 4, y + 4], fill=coul)
        points += [(xx(a), y), (xx(z), y), (xx(w), y)]
        traces["lignes"] += 1
        dv = b["lancre_du_voisinage"]["la_decision"]
        ecrire(630, y - 7, f"{dv['les_rates_rendus_justes']} / {dv['les_justes_rendus_rates']}", 0, coul)
    g = d["les_reunis"]
    y = gy0 + pas * len(lignes) + 4
    ecrire(66, y, f"réguliers, réunis : {_fr(g['avant'], 4)} → ancre des voisins {_fr(g['lancre_du_voisinage']['apres'], 4)}, "
                  f"ancre du bloc {_fr(g['lancre_du_bloc']['apres'], 4)}", 0, ENCRE)

    # ── PANNEAU 2 · CE QUE L'ANCRE CHANGE ──────────────────────────────────────────────────────────────────────────
    panneau(840, 80, 1310, 510, "CE QUE L'ANCRE CHANGE AU MÉLANGE")
    ecrire(856, 112, "le poids des spires glissées, ancre des voisins · ancre du bloc", 0, GRIS)
    ecrire(856, 126, "· puis l'écart des deux ancres, voxels", 0, GRIS)
    for k, (nom, b, choisi) in enumerate(lignes):
        y = gy0 + pas * k
        mv, mb = b["lancre_du_voisinage"]["le_melange"], b["lancre_du_bloc"]["le_melange"]
        gv = mv["glissee_au_dessus"] + mv["glissee_au_dessous"]
        gb = mb["glissee_au_dessus"] + mb["glissee_au_dessous"]
        ea = b["lancre_du_voisinage"]["lancre_voxels"] - b["lancre_du_bloc"]["lancre_voxels"]
        ecrire(856, y - 7, f"{nom.split(', voisin')[0]} : "
               f"{_fr(100 * gv, 1)} % · {_fr(100 * gb, 1)} % · {_fr(ea, 1)}", 0,
               ENCRE if choisi else GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 526, L_, H_], fill=BANDE)
    ecrire(50, 538, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    v = g["lancre_du_voisinage"]
    ecrire(50, 560, f"★ sur {g['les_blocs']} blocs qu'elle n'avait jamais vus, {v['les_points_corriges']} points corrigés ; "
                    f"les justes rendus ratés : " + " ; ".join(f"{n}, {k}" for n, k in les_abimes(d)) + ".", moyen, ENCRE)
    ecrire(50, 586, "⚠ ce qui n'est PAS établi : une boucle ; d'autres blocs ; une seconde passe.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_270.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", f"À {_fr(d['les_reunis']['lancre_du_voisinage']['apres'], 4)}," in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque bloc a sa ligne, les deux choisis compris",
      traces["lignes"] == len(d["les_blocs"]) + len(d["_265"]["les_blocs"]), str(traces))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ la bande nomme chaque bloc abîmé, et leurs justes rendus ratés font le total réuni",
      all(f"{n}, {k}" in txt for n, k in les_abimes(d)) and sum(k for _, k in les_abimes(d))
      == d["les_reunis"]["lancre_du_voisinage"]["les_justes_rendus_rates"], str(les_abimes(d)))
    # ⚠ Le contact se recompte ici par les coordonnées, à un bloc de distance, et non par la liste des voisins que la
    # figure lit : relire la même liste des deux côtés passerait même si la figure ne l'écrivait jamais.
    contacts = {(b["la_rangee"], b["la_colonne"]): [n[-3:] for n, c in d["_265"]["les_blocs"].items()
                                                    if abs(c["la_rangee"] - b["la_rangee"])
                                                    + abs(c["la_colonne"] - b["la_colonne"]) == 16]
                for b in d["les_blocs"].values()}
    v("★★★★ un bloc régulier qui touche un bloc choisi le dit",
      all((f"({y}, {x}), voisin du bloc de {t}" in txt) for (y, x), ts in contacts.items() for t in ts)
      and sum(len(ts) for ts in contacts.values()) > 0, str(contacts))
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
                   default=RACINE / "docs" / "images" / "270_lancre_du_voisinage_tient_elle_sur_des_blocs_reguliers.png")
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
