"""La chaîne de 248 repartie de la spire corrigée de 275 : ce que chaque saut devient.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, saut par saut, la part des points notés sur la bonne spire, pour la
chaîne partie du segment (le témoin) et pour celle partie de la spire corrigée. À droite, ce que la spire corrigée change à
chaque saut, et ce que deviennent au deuxième saut les points dont elle a rendu le premier juste.

  uv run python src/figures/figure_repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.py \\
      --sortie docs/images/276_repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
TEMOIN = (190, 192, 196)
L_, H_ = 1360, 760


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
    s = d["les_sauts"][1]
    return (f"AU DEUXIÈME SAUT, REPARTIR DE LA SPIRE CORRIGÉE REND {s['les_rates_rendus_justes']} RATÉS JUSTES ET "
            f"{s['les_justes_rendus_rates']} JUSTES RATÉS : UN GAIN NET DE {_fr(s['le_gain_net'])}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "lignes": 0}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"{d['le_segment']} · {d['la_prediction']}, côté plus · la chaîne de 248, {d['les_sauts_de_la_chaine']} "
                   f"sauts · le juge est la couche du segment, il ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · LA PART SUR LA BONNE SPIRE, SAUT PAR SAUT ────────────────────────────────────────────────────────
    panneau(50, 80, 640, 640, "À CHAQUE SAUT, LA PART DES POINTS NOTÉS SUR LA BONNE SPIRE")
    gx0, gx1, gy0, gy1 = 100, 610, 170, 540
    art.line([gx0, gy1, gx1, gy1], fill=GRIS)
    art.line([gx0, gy0, gx0, gy1], fill=GRIS)
    ecrire(gx0 - 30, gy0 - 8, "1", 0, GRIS)
    ecrire(gx0 - 30, gy1 - 8, "0", 0, GRIS)
    n = len(d["les_sauts"])
    pas = (gx1 - gx0) / max(n, 1)
    for h, s in enumerate(d["les_sauts"]):
        x = gx0 + h * pas + pas * 0.18
        w = pas * 0.28
        for k, (cle, coul) in enumerate((("le_temoin", TEMOIN), ("partie_de_la_spire_corrigee", BON))):
            v_ = s[cle] if s[cle] is not None else 0.0
            y = gy1 - v_ * (gy1 - gy0)
            xa = x + k * (w + 6)
            art.rectangle([xa, y, xa + w, gy1], fill=coul)
            points.append((xa + w, y))
            traces["barres"].append(round(v_, 4))
            ecrire(int(xa), int(y) - 16, _fr(v_), 0, ENCRE)
        ecrire(int(x), gy1 + 8, f"saut {h + 1}", 0, ENCRE)
        ecrire(int(x), gy1 + 24, f"{s['les_points_notes']} notés", 0, GRIS)
    for k, (coul, texte) in enumerate(((TEMOIN, "partie du segment, comme 248 : le témoin"),
                                       (BON, "partie de la spire corrigée de 275"))):
        art.rectangle([gx0, 590 + 20 * k, gx0 + 12, 602 + 20 * k], fill=coul)
        ecrire(gx0 + 18, 589 + 20 * k, texte, 0, ENCRE)

    # ── PANNEAU 2 · CE QUE LA SPIRE CORRIGÉE CHANGE ──────────────────────────────────────────────────────────────────
    panneau(660, 80, 1310, 640, "CE QUE LA SPIRE CORRIGÉE CHANGE, SAUT PAR SAUT")
    colonnes = [(690, "saut"), (760, "notés"), (850, "différents"), (960, "ratés rendus justes"),
                (1110, "justes rendus ratés"), (1250, "net")]
    for x, t in colonnes:
        ecrire(x, 140, t, 0, GRIS)
    for h, s in enumerate(d["les_sauts"]):
        y = 170 + 30 * h
        for (x, _), t in zip(colonnes, (str(h + 1), str(s["les_points_notes"]),
                                        str(s["les_points_ou_les_deux_chaines_different"]),
                                        str(s["les_rates_rendus_justes"]), str(s["les_justes_rendus_rates"]),
                                        _fr(s["le_gain_net"]))):
            ecrire(x, y, t, moyen, ENCRE if h == 1 else GRIS)
        traces["lignes"] += 1
    r = d["la_reprise"]
    ecrire(690, 330, f"les {r['les_points']} points notés aux deux premiers sauts dont la spire corrigée rend le premier",
           0, ENCRE)
    ecrire(690, 348, "juste : ce que devient leur deuxième saut", 0, ENCRE)
    for k, (cle, coul, nom) in enumerate((("le_temoin", TEMOIN, "témoin"),
                                          ("partie_de_la_spire_corrigee", BON, "spire corrigée"))):
        v_ = r[cle] if r[cle] is not None else 0.0
        y = 385 + 44 * k
        art.rectangle([790, y, 790 + v_ * 460, y + 26], fill=coul)
        points.append((790 + v_ * 460, y + 26))
        ecrire(690, y + 6, nom, 0, ENCRE)
        ecrire(int(790 + v_ * 460) + 8, y + 6, f"{_fr(v_)} sur la bonne spire", 0, ENCRE)
    ecrire(690, 500, f"la spire corrigée diffère de la produite en {d['les_points_ou_la_spire_corrigee_differe_de_la_produite']}"
                     f" points, sur {d['les_points']}", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    rp = d["la_reproduction"]["les_sauts"]
    ecrire(50, 690, f"le témoin redonne 248 à {sum(1 for x in rp if x['reproduit'])} sauts sur {len(rp)}, et son premier saut "
                    f"est la spire produite à {_fr(d['le_premier_saut_du_temoin_contre_la_spire_produite_ecart_max_voxels'])} "
                    f"voxel près ; {d['la_lecture']['combien_de_pannes']} panne de lecture", moyen, ENCRE)
    ecrire(50, 714, "⚠ ce qui n'est PAS établi : une correction du deuxième saut ; l'autre côté, l'autre prédiction ; la bande "
                    "de 248.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_276.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    s2 = d["les_sauts"][1]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(s2['le_gain_net'])}" in le_titre(d)
      and f"REND {s2['les_rates_rendus_justes']} RATÉS JUSTES" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [round(s[c] or 0.0, 4) for s in d["les_sauts"] for c in ("le_temoin", "partie_de_la_spire_corrigee")]
    v("★★★★ deux barres par saut, et leurs hauteurs sont les parts mesurées", traces["barres"] == attendu,
      f"{traces['barres']} contre {attendu}")
    v("★★★★ une ligne par saut, et son gain net est la différence de ses deux comptes",
      traces["lignes"] == len(d["les_sauts"])
      and all(s["le_gain_net"] == s["les_rates_rendus_justes"] - s["les_justes_rendus_rates"] for s in d["les_sauts"]))
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
                   default=RACINE / "docs" / "images" / "276_repartir_de_la_spire_corrigee_rend_il_le_saut_suivant_plus_juste.png")
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
