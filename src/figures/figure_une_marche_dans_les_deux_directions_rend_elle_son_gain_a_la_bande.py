"""Une marche qui s'étend au nord et au sud : ce qu'elle fait à la procédure sur la tranche haute de la bande.

⚠⚠ **Ce que cette figure doit rendre évident.** Sur les blocs de la rangée 32 qui ont leurs quatre voisins, les ratés rendus
justes et les justes rendus ratés, avec tous leurs voisins puis avec les seuls voisins est et ouest ; et, bloc par bloc le long
de la rangée, le gain net des deux façons.

  uv run python src/figures/figure_une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.py \\
      --sortie docs/images/295_une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.json"
LES_FACONS = (("avec_tous_leurs_voisins", "tous leurs voisins"),
              ("avec_les_seuls_voisins_est_et_ouest", "est et ouest seulement"))

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
L_, H_ = 1360, 560


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def _p(x) -> str:
    return f"{float(x):.3g}".replace(".", ",").replace("e-0", "e-").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def les_gains_par_bloc(d: dict) -> list[tuple[int, int, int]]:
    """Pour chaque bloc à quatre voisins, dans l'ordre des colonnes : sa colonne, son gain net avec tous ses voisins, puis
    avec les seuls voisins est et ouest."""
    eo = {b["la_colonne"]: b for b in d["les_blocs_avec_les_seuls_voisins_est_et_ouest"] if b.get("decidable")}
    gain = lambda b: b["les_rates_rendus_justes"] - b["les_justes_rendus_rates"]  # noqa: E731
    quatre = set(d["le_plan"]["les_blocs_a_quatre_voisins"])
    return [(b["la_colonne"], gain(b), gain(eo[b["la_colonne"]])) for b in sorted(d["les_blocs"], key=lambda b: b["la_colonne"])
            if b.get("decidable") and f"{b['la_rangee']}_{b['la_colonne']}" in quatre and b["la_colonne"] in eo]


def le_titre(d: dict) -> str:
    q = d["les_blocs_a_quatre_voisins"]
    t, e = (q[k]["le_test"]["sur_les_points"] for k, _ in LES_FACONS)
    return (f"AVEC SES VOISINS DU NORD ET DU SUD, LA PROCÉDURE GAGNE {_fr(t['le_gain_net'])} POINTS SUR LA BANDE, "
            f"CONTRE {_fr(e['le_gain_net'])} AVEC LES SEULS VOISINS EST ET OUEST")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "gains": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    q = d["les_blocs_a_quatre_voisins"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"premier saut · tranche {_fr(d['le_plan']['la_tranche'][0], 2)} à {_fr(d['le_plan']['la_tranche'][1], 2)}"
                   f" · les {q['avec_tous_leurs_voisins']['les_reunis']['les_blocs']} blocs de la rangée 32 qui ont leurs "
                   "quatre voisins · test du signe de 290 · le juge ne sert qu'à noter", petit, GRIS)

    panneau(50, 80, 560, 440, "LES POINTS DES BLOCS À QUATRE VOISINS")
    vmax = max([max(q[k]["les_reunis"]["les_rates_rendus_justes"], q[k]["les_reunis"]["les_justes_rendus_rates"])
                for k, _ in LES_FACONS] + [1])
    for j, (cle, nom) in enumerate(LES_FACONS):
        r, t = q[cle]["les_reunis"], q[cle]["le_test"]["sur_les_points"]
        x0, base, haut = 110 + j * 230, 350, 190
        for m, (c, coul) in enumerate((("les_rates_rendus_justes", BON), ("les_justes_rendus_rates", ALERTE))):
            h = r[c] / vmax * haut
            x = x0 + m * 60
            art.rectangle([x, base - h, x + 48, base], fill=coul)
            traces["barres"].append((cle, c, r[c]))
            points.append((x + 48, base - h))
            ecrire(x + 4, int(base - h) - 18, str(r[c]), 0, ENCRE)
        art.line([x0 - 8, base, x0 + 120, base], fill=GRIS)
        ecrire(x0, base + 8, nom, 0, ENCRE)
        ecrire(x0, base + 26, f"gain net {_fr(t['le_gain_net'])} · p = {_p(t['la_probabilite'])}", 0, GRIS)
    ecrire(110, 118, "■ ratés rendus justes", 0, BON)
    ecrire(290, 118, "■ justes rendus ratés", 0, ALERTE)

    panneau(580, 80, 1310, 440, "LE GAIN NET, BLOC PAR BLOC LE LONG DE LA RANGÉE 32")
    gains = les_gains_par_bloc(d)
    gx0, gx1, gy0, gy1 = 640, 1280, 140, 380
    vals = [g for _, a, b in gains for g in (a, b)] + [1, -1]
    gm = max(abs(v) for v in vals)
    y_de = lambda v: gy0 + (gy1 - gy0) * (0.5 - v / (2 * gm))  # noqa: E731
    art.line([gx0, y_de(0), gx1, y_de(0)], fill=GRIS)
    ecrire(gx0 - 44, int(y_de(gm)) - 6, f"+{gm}", 0, GRIS)
    ecrire(gx0 - 44, int(y_de(-gm)) - 6, f"−{gm}", 0, GRIS)
    pas = (gx1 - gx0) / max(len(gains), 1)
    for k, (col, a, b) in enumerate(gains):
        x = gx0 + pas * (k + 0.5)
        for v, coul, dx in ((a, BLEU, -3), (b, GRIS, 3)):
            art.ellipse([x + dx - 4, y_de(v) - 4, x + dx + 4, y_de(v) + 4], fill=coul)
            points.append((x + dx, y_de(v)))
        traces["gains"].append((col, a, b))
    ecrire(gx0, gy1 + 16, f"colonnes {gains[0][0]} à {gains[-1][0]}" if gains else "aucun bloc", 0, GRIS)
    ecrire(gx0 + 220, gy1 + 16, "● tous leurs voisins", 0, BLEU)
    ecrire(gx0 + 400, gy1 + 16, "● est et ouest seulement", 0, GRIS)

    art.rectangle([0, 456, L_, H_], fill=BANDE)
    ecrire(50, 468, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 490, "les deux façons lisent les mêmes piles rendues ; seuls changent les voisins que la marche et l'ancre "
                    "lisent", moyen, ENCRE)
    ecrire(50, 514, "⚠ ce qui n'est PAS établi : la bande entière ; le deuxième saut ; les autres colonnes.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_295.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    q = d["les_blocs_a_quatre_voisins"]
    # ⚠ Sur une mesure dont les gains sont changés : la mesure publiée vaut 2 contre 0, et un titre qui écrirait « 0 » en
    # dur passerait contre elle.
    autre = json.loads(json.dumps(d))
    for k, g in (("avec_tous_leurs_voisins", 17), ("avec_les_seuls_voisins_est_et_ouest", 23)):
        autre["les_blocs_a_quatre_voisins"][k]["le_test"]["sur_les_points"]["le_gain_net"] = g
    v("★★★ le titre LIT la mesure", "GAGNE 17 POINTS" in le_titre(autre) and le_titre(autre).endswith(
        "CONTRE 23 AVEC LES SEULS VOISINS EST ET OUEST"), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(k, c, q[k]["les_reunis"][c]) for k, _ in LES_FACONS
               for c in ("les_rates_rendus_justes", "les_justes_rendus_rates")]
    v("★★★★ une barre par compte, chacune au compte mesuré", traces["barres"] == attendu)
    somme = [sum(g[i] for g in traces["gains"]) for i in (1, 2)]
    v("★★★★ les gains des blocs somment au gain réuni, des deux façons",
      somme == [q[k]["les_reunis"]["le_gain_net"] for k, _ in LES_FACONS], str(somme))
    v("★★★ un point par bloc à quatre voisins",
      len(traces["gains"]) == q["avec_tous_leurs_voisins"]["les_reunis"]["les_blocs"])
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "295_une_marche_dans_les_deux_directions_rend_elle_son_gain_a_la_bande.png")
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
