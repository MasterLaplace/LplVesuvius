"""La spire corrigée recalée sur la feuille : où la correction pose ses points, et ce que le recalage change à chaque saut.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, à quelle distance de la feuille la plus proche la correction pose les
points qu'elle déplace, contre la spire produite partout ailleurs, avec le seuil de 12 voxels au-delà duquel le saut suivant ne
reconnaît plus sa feuille. À droite, saut par saut, ce que la chaîne repartie de la spire recalée gagne et perd sur celle
repartie de la spire corrigée, et les sauts qui retombent sur leur couche.

  uv run python src/figures/figure_recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.py \\
      --sortie docs/images/279_recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.png
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
LA_MESURE = (RACINE / "docs" / "mesures" /
             "recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (206, 208, 211)
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
    return (f"RECALÉE SUR LA FEUILLE, LA SPIRE CORRIGÉE REND AU DEUXIÈME SAUT {s['les_rates_rendus_justes']} RATÉS JUSTES ET "
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
    ecrire(50, 52, f"20230702185753 · m7, côté plus · {d['les_points_deplaces_par_la_correction']} points déplacés par la "
                   f"correction, {d['les_points_recales']} recalés · la chaîne de 248 · le juge ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · LA DISTANCE À LA FEUILLE ────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 640, 640, "À QUELLE DISTANCE DE LA FEUILLE LA SPIRE POSE SES POINTS")
    bx0, bx1 = 90, 600
    lignes = (("la_spire_corrigee_aux_points_deplaces", "la spire corrigée, aux points que la correction déplace"),
              ("la_spire_produite_ailleurs", "la spire produite, partout ailleurs"))
    for i, (cle, nom) in enumerate(lignes):
        r = d["la_distance_a_la_feuille"][cle]
        y = 150 + 190 * i
        ecrire(bx0, y - 26, f"{nom} : {r['les_points']} points", moyen, ENCRE)
        tot = max(r["les_points"], 1)
        pres = r["les_points"] - r["sans_feuille_sur_le_rayon"] - r["au_dela_de_la_reconnaissance"]
        loin = r["au_dela_de_la_reconnaissance"] - r["au_dela_dun_demi_feuillet"]
        x = bx0
        for n_, coul in ((pres, BON), (loin, ALERTE), (r["au_dela_dun_demi_feuillet"], (120, 60, 30)),
                         (r["sans_feuille_sur_le_rayon"], PALE)):
            w = n_ / tot * (bx1 - bx0)
            art.rectangle([x, y, x + w, y + 34], fill=coul)
            points.append((x + w, y + 34))
            traces["barres"].append((cle, n_))
            x += w
        ecrire(bx0, y + 42, f"médiane : {_fr(r['la_mediane_voxels'])} voxels", 0, ENCRE)
        ecrire(bx0, y + 60, f"au-delà de 12 voxels, le saut suivant ne reconnaît plus sa feuille : "
                            f"{r['au_dela_de_la_reconnaissance']}", 0, ENCRE)
        ecrire(bx0, y + 78, f"dont au-delà d'un demi-feuillet : {r['au_dela_dun_demi_feuillet']} · sans feuille sur le rayon : "
                            f"{r['sans_feuille_sur_le_rayon']}", 0, GRIS)
    for k, (coul, texte) in enumerate(((BON, "à moins de 12 voxels"), (ALERTE, "de 12 voxels à un demi-feuillet"),
                                       ((120, 60, 30), "au-delà d'un demi-feuillet"), (PALE, "sans feuille"))):
        lx, ly = bx0 + 250 * (k % 2), 588 + 22 * (k // 2)
        art.rectangle([lx, ly, lx + 12, ly + 12], fill=coul)
        ecrire(lx + 16, ly - 1, texte, 0, ENCRE)

    # ── PANNEAU 2 · SAUT PAR SAUT ────────────────────────────────────────────────────────────────────────────────────
    panneau(660, 80, 1310, 640, "DE LA SPIRE CORRIGÉE À LA SPIRE RECALÉE, SAUT PAR SAUT")
    colonnes = [(690, "saut"), (740, "notés"), (820, "corrigée"), (905, "recalée"), (990, "ratés rendus justes"),
                (1130, "justes rendus ratés"), (1260, "net")]
    for x, t in colonnes:
        ecrire(x, 140, t, 0, GRIS)
    for h, s in enumerate(d["les_sauts"]):
        y = 166 + 28 * h
        for (x, _), t in zip(colonnes, (str(h + 1), str(s["les_points_notes"]), _fr(s["partie_de_la_spire_corrigee"]),
                                        _fr(s["partie_de_la_spire_recalee"]), str(s["les_rates_rendus_justes"]),
                                        str(s["les_justes_rendus_rates"]), _fr(s["le_gain_net"]))):
            ecrire(x, y, t, 0, ENCRE if h == 1 else GRIS)
        traces["lignes"] += 1
    si = d["le_deuxieme_saut_sous_le_juge_intact"]
    ecrire(690, 290, f"sous le juge intact de 253, au deuxième saut : {si['les_rates_rendus_justes']} ratés rendus justes, "
                     f"{si['les_justes_rendus_rates']} justes rendus ratés", 0, ENCRE)
    ecrire(674, 330, "LES RATÉS PROPRES DU DEUXIÈME SAUT QUI RETOMBENT", moyen, ENCRE)
    colonnes2 = [(690, "juge"), (880, "chaîne"), (1060, "sur la 1re couche"), (1200, "n'avance pas")]
    for x, t in colonnes2:
        ecrire(x, 362, t, 0, GRIS)
    k = 0
    for kj, nj in (("le_juge_de_248", "le juge de 248"), ("le_juge_intact", "le juge intact de 253")):
        for kc, nc in (("partie_de_la_spire_corrigee", "spire corrigée"), ("partie_de_la_spire_recalee", "spire recalée")):
            p_ = d["le_rangement"][kj][kc]["parmi_les_propres"]
            y = 388 + 26 * k
            for (x, _), t in zip(colonnes2, (nj, nc, str(p_["retombes_sur_la_premiere_couche"]),
                                             str(p_["dun_saut_qui_navance_pas"]))):
                ecrire(x, y, t, 0, ENCRE)
            traces["lignes"] += 1
            k += 1

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 656, L_, H_], fill=BANDE)
    ecrire(50, 668, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 690, "les chaînes du témoin et de la spire corrigée redonnent le deuxième saut de 276 compte pour compte ; "
                    f"{d['la_lecture']['combien_de_pannes']} panne de lecture", moyen, ENCRE)
    ecrire(50, 714, "⚠ ce qui n'est PAS établi : un recalage sur une feuille que la prédiction ne voit pas ; une correction du "
                    "deuxième saut.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_279.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    s2 = d["les_sauts"][1]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(s2['le_gain_net'])}" in le_titre(d)
      and f"{s2['les_rates_rendus_justes']} RATÉS JUSTES" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    ok = True
    for cle in ("la_spire_corrigee_aux_points_deplaces", "la_spire_produite_ailleurs"):
        r = d["la_distance_a_la_feuille"][cle]
        ok &= sum(n_ for c_, n_ in traces["barres"] if c_ == cle) == r["les_points"]
    v("★★★★ les quatre segments d'une distance font tous ses points, et aucun n'est négatif",
      ok and all(n_ >= 0 for _, n_ in traces["barres"]), str(traces["barres"]))
    v("★★★★ une ligne par saut et par rangement, et chaque gain net est la différence de ses deux comptes",
      traces["lignes"] == len(d["les_sauts"]) + 4
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" /
                   "279_recaler_la_spire_corrigee_sur_la_feuille_rend_il_le_deuxieme_saut_plus_juste.png")
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
