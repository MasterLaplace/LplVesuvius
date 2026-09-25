"""La procédure de 265, sans et avec la garde de la marche du segment réduit, bloc par bloc.

⚠⚠ **Ce que cette figure doit rendre évident.** Pour chacun des neuf blocs, la part sur la bonne spire avant, après la procédure
sans la garde, et après la procédure avec elle. À droite, ce que la garde retient : les points qu'elle empêche de corriger, et
parmi eux ceux qui auraient été rendus justes et ceux qui auraient été rendus ratés.

  uv run python src/figures/figure_la_marche_du_segment_dit_elle_ou_ne_pas_corriger.py \\
      --sortie docs/images/274_la_marche_du_segment_dit_elle_ou_ne_pas_corriger.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_marche_du_segment_dit_elle_ou_ne_pas_corriger.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (200, 205, 212)
L_, H_ = 1360, 640


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


def le_court(nom: str, b: dict) -> str:
    return f"le bloc de {nom[-3:]}" if nom.startswith("le_bloc_de_") else f"({b['la_rangee']}, {b['la_colonne']})"


def le_nom(nom: str, b: dict) -> str:
    return f"{le_court(nom, b)}, choisi" if nom.startswith("le_bloc_de_") else le_court(nom, b)


def les_lignes(d: dict) -> list[tuple[str, dict, bool]]:
    return [(le_nom(n, b), b, n.startswith("le_bloc_de_")) for n, b in d["les_voisinages"].items()]


def les_retenus(d: dict) -> dict:
    """Ce que la garde retient, réuni sur les neuf blocs, et les blocs où chaque part tombe."""
    r = {"les_rates_rendus_justes": 0, "les_justes_rendus_rates": 0, "ou_rj": [], "ou_jr": []}
    for n, b in d["les_voisinages"].items():
        t = b["retenus_par_la_garde"]
        r["les_rates_rendus_justes"] += t["les_rates_rendus_justes"]
        r["les_justes_rendus_rates"] += t["les_justes_rendus_rates"]
        if t["les_rates_rendus_justes"]:
            r["ou_rj"].append(le_court(n, b))
        if t["les_justes_rendus_rates"]:
            r["ou_jr"].append(le_court(n, b))
    return r


def le_titre(d: dict) -> str:
    g = d["les_reunis"]["les_neuf"]
    r = les_retenus(d)
    return (f"AVEC LA GARDE, LE GAIN NET DES NEUF BLOCS PASSE DE {g['sans_la_garde']['le_gain_net']} À "
            f"{g['avec_la_garde']['le_gain_net']} : ELLE ÉVITE {r['les_justes_rendus_rates']} DES "
            f"{g['sans_la_garde']['les_justes_rendus_rates']} DOMMAGES ET PERD {r['les_rates_rendus_justes']} DES "
            f"{g['sans_la_garde']['les_rates_rendus_justes']} RÉPARATIONS")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"20230702185753 · m7, côté plus · la procédure de 265 · la garde : ne corriger que là où la marche du "
                   f"segment réduit, moins son ancre, est à moins de {_fr(d['le_seuil_voxels'])} voxels", petit, GRIS)
    lignes = les_lignes(d)

    # ── PANNEAU 1 · BLOC PAR BLOC ──────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 820, 530, "LA PART SUR LA BONNE SPIRE : AVANT ○, SANS LA GARDE ◆, AVEC ELLE ●")
    gx0, gx1, gy0, pas, lo = 330, 600, 150, 36, 0.4
    xx = lambda v: gx0 + (gx1 - gx0) * (v - lo) / (1.0 - lo)  # noqa: E731
    for v in (0.4, 0.7, 1.0):
        art.line([xx(v), gy0 - 18, xx(v), gy0 + pas * len(lignes) - 16], fill=TRAIT)
        ecrire(xx(v) - 8, gy0 - 36, _fr(v, 1), 0, GRIS)
    ecrire(630, gy0 - 36, "justes / ratés, sans → avec", 0, GRIS)
    for k, (nom, b, choisi) in enumerate(lignes):
        y = gy0 + pas * k
        ecrire(66, y - 7, f"{nom} · {b['avant']['les_points_notes']} points", 0, ENCRE if choisi else GRIS)
        a = b["avant"]["la_part_sur_la_bonne_spire"]
        s = b["sans_la_garde"]["apres"]["la_part_sur_la_bonne_spire"]
        g = b["avec_la_garde"]["apres"]["la_part_sur_la_bonne_spire"]
        coul = BON if g > a else ALERTE if g < a else GRIS
        art.line([xx(a), y, xx(g), y], fill=coul, width=3)
        art.ellipse([xx(a) - 5, y - 5, xx(a) + 5, y + 5], outline=GRIS, width=2)
        art.polygon([(xx(s), y - 6), (xx(s) + 6, y), (xx(s), y + 6), (xx(s) - 6, y)], fill=PALE)
        art.ellipse([xx(g) - 4, y - 4, xx(g) + 4, y + 4], fill=coul)
        points += [(xx(a), y), (xx(s), y), (xx(g), y)]
        traces["lignes"] += 1
        bs, bg = b["sans_la_garde"], b["avec_la_garde"]
        ecrire(630, y - 7, f"{bs['les_rates_rendus_justes']} / {bs['les_justes_rendus_rates']} → "
                           f"{bg['les_rates_rendus_justes']} / {bg['les_justes_rendus_rates']}", 0, coul)
    r = d["les_reunis"]["les_reguliers"]
    y = gy0 + pas * len(lignes) + 4
    ecrire(66, y, f"réguliers, réunis : {_fr(r['avant'])} → sans la garde {_fr(r['sans_la_garde']['apres'])}, "
                  f"avec elle {_fr(r['avec_la_garde']['apres'])}", 0, ENCRE)

    # ── PANNEAU 2 · CE QUE LA GARDE RETIENT ────────────────────────────────────────────────────────────────────────
    panneau(840, 80, 1310, 530, "CE QUE LA GARDE RETIENT")
    ecrire(856, 112, "points retenus · dont ratés qui auraient été rendus", 0, GRIS)
    ecrire(856, 126, "justes · dont justes qui auraient été rendus ratés", 0, GRIS)
    for k, (n, b) in enumerate(d["les_voisinages"].items()):
        y = gy0 + pas * k
        t = b["retenus_par_la_garde"]
        choisi = n.startswith("le_bloc_de_")
        ecrire(856, y - 7, f"{le_court(n, b)} : {t['les_points_corriges']} · {t['les_rates_rendus_justes']} · "
                           f"{t['les_justes_rendus_rates']}", 0, ENCRE if choisi else GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 546, L_, H_], fill=BANDE)
    ecrire(50, 558, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    rr = les_retenus(d)
    ecrire(50, 580, f"les dommages évités sont tous sur {', '.join(rr['ou_jr'])} ; les réparations perdues, tous sur "
                    f"{', '.join(rr['ou_rj'])}. La garde ne demande ni juge ni humain.", moyen, ENCRE)
    ecrire(50, 604, "⚠ ce qui n'est PAS établi : d'autres blocs ; un autre seuil ; une seconde passe.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_274.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    g = d["les_reunis"]["les_neuf"]
    v("★★★ le titre LIT la mesure", f"PASSE DE {g['sans_la_garde']['le_gain_net']} À" in le_titre(d))
    r = les_retenus(d)
    v("★★★★ ce que le titre dit évité et perdu redonne les comptes réunis",
      g["avec_la_garde"]["les_justes_rendus_rates"] + r["les_justes_rendus_rates"] == g["sans_la_garde"]["les_justes_rendus_rates"]
      and g["avec_la_garde"]["les_rates_rendus_justes"] + r["les_rates_rendus_justes"]
      == g["sans_la_garde"]["les_rates_rendus_justes"], str(r))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque bloc a sa ligne", traces["lignes"] == len(d["les_voisinages"]) == 9, str(traces))
    v("★★★★ ce que la garde retient, plus ce qu'elle laisse, redonne la procédure sans elle, bloc par bloc",
      all(b["retenus_par_la_garde"][k] + b["avec_la_garde"][k] == b["sans_la_garde"][k]
          for b in d["les_voisinages"].values() for k in ("les_rates_rendus_justes", "les_justes_rendus_rates")))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    v("★★★★ chaque nom de bloc dessiné est entier, parenthèses fermées",
      all(le_court(n, b) in txt for n, b in d["les_voisinages"].items()) and txt.count("(") == txt.count(")"),
      str([le_court(n, b) for n, b in d["les_voisinages"].items() if le_court(n, b) not in txt]))
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
                   default=RACINE / "docs" / "images" / "274_la_marche_du_segment_dit_elle_ou_ne_pas_corriger.png")
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
