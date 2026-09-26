"""Le troisième saut de la bande selon la façon dont la chaîne repart du deuxième saut corrigé, de `284` à `288`.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque reprise, les ratés rendus justes et les justes rendus ratés
au troisième saut, contre le même témoin. À droite, pour la reprise qui ne dérange pas les voisins, où tombent ses changements.

  uv run python src/figures/figure_une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.py \\
      --sortie docs/images/288_une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.png
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
LES_MESURES = RACINE / "docs" / "mesures"
LA_MESURE = LES_MESURES / "une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.json"
LES_REPRISES = (("284", "repartir_du_deuxieme_saut_corrige_rend_il_le_troisieme_saut_de_la_bande_plus_juste.json",
                 "recalé, rayon de la bande"),
                ("285", "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json",
                 "recalé, rayon du saut"),
                ("287", "les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.json", "normales du témoin"),
                ("288", LA_MESURE.name, "sans voter pour ses voisins"))

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 560
LES_CLASSES = (("le_point_lui_meme", "le point corrigé"), ("a_une_maille", "à une maille"),
               ("a_deux_ou_trois_mailles", "à deux ou trois"), ("a_quatre_mailles_ou_plus", "à quatre ou plus"))


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    d["les_reprises"] = [(t, nom, json.loads((LES_MESURES / f).read_text())["les_sauts"][0]) for t, f, nom in LES_REPRISES]
    return d


def le_titre(d: dict) -> str:
    s = d["les_sauts"][0]
    return (f"SANS VOTER POUR LEURS VOISINS, LES POINTS CORRIGÉS RENDENT AU TROISIÈME SAUT {s['les_rates_rendus_justes']} "
            f"RATÉS JUSTES ET {s['les_justes_rendus_rates']} JUSTES RATÉS : UN GAIN NET DE {_fr(s['le_gain_net'])}")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20260623142658-w028-037 · le deuxième saut corrigé de 283 · le même témoin, reparti du deuxième saut non "
                   "corrigé · le juge ne sert qu'à noter", petit, GRIS)

    panneau(50, 80, 860, 440, "AU TROISIÈME SAUT, SELON LA FAÇON DE REPARTIR")
    vmax = max([max(s["les_rates_rendus_justes"], s["les_justes_rendus_rates"]) for _, _, s in d["les_reprises"]] + [1])
    base, haut = 370, 200
    for k, (tranche, nom, s) in enumerate(d["les_reprises"]):
        x0 = 90 + k * 190
        for j, (cle, coul) in enumerate((("les_rates_rendus_justes", BON), ("les_justes_rendus_rates", ALERTE))):
            h = s[cle] / vmax * haut
            x = x0 + j * 50
            art.rectangle([x, base - h, x + 40, base], fill=coul)
            traces["barres"].append((tranche, cle, s[cle]))
            points.append((x + 40, base - h))
            ecrire(x + 4, int(base - h) - 18, str(s[cle]), 0, ENCRE)
        art.line([x0 - 8, base, x0 + 100, base], fill=GRIS)
        ecrire(x0, base + 8, tranche, 0, ENCRE)
        ecrire(x0, base + 24, nom, 0, ENCRE)
        ecrire(x0, base + 42, f"gain net {_fr(s['le_gain_net'])}", 0, GRIS)
    ecrire(90, 118, "■ ratés rendus justes", 0, BON)
    ecrire(270, 118, "■ justes rendus ratés", 0, ALERTE)

    panneau(876, 80, 1310, 440, "288 : OÙ TOMBENT SES CHANGEMENTS")
    for k, (cle, s) in enumerate((("le_troisieme_saut_range", "au troisième saut"), ("le_quatrieme_saut_range",
                                                                                     "au quatrième saut"))):
        r = d[cle]
        y0 = 124 + k * 150
        ecrire(896, y0, f"{s} : {r['ou_les_deux_chaines_different']} points notés changent, "
                        f"{r['les_rates_rendus_justes']} pour {r['les_justes_rendus_rates']}", 0, ENCRE)
        for j, (cc, lib) in enumerate(LES_CLASSES):
            c = r["les_classes"][cc]
            ecrire(912, y0 + 24 + 22 * j, f"{lib} : {c['ou_les_deux_chaines_different']} changent, "
                                          f"{c['les_rates_rendus_justes']} pour {c['les_justes_rendus_rates']}", 0, GRIS)

    art.rectangle([0, 456, L_, H_], fill=BANDE)
    ecrire(50, 468, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    c5, c7 = d["les_comptes_de_285"]["refaits"][0], d["les_comptes_de_287"]["refaits"][0]
    ecrire(50, 490, f"les reprises redonnent 285, {c5[0]} pour {c5[1]}, et 287, {c7[0]} pour {c7[1]}", moyen, ENCRE)
    ecrire(50, 514, "⚠ ce qui n'est PAS établi : la même reprise sur le segment 20230702185753 ; un autre côté, une autre "
                    "prédiction.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_288.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    s = d["les_sauts"][0]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(s['le_gain_net'])}" in le_titre(d)
      and f"{s['les_rates_rendus_justes']} RATÉS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(t, c, x[c]) for t, _, x in d["les_reprises"] for c in ("les_rates_rendus_justes", "les_justes_rendus_rates")]
    v("★★★★ une barre par compte et par reprise, chacune au compte publié par sa tranche", traces["barres"] == attendu
      and len(attendu) == 8)
    v("★★★★ la reprise de 288 est la mesure elle-même", d["les_reprises"][-1][2] == s)
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "288_une_reprise_qui_ne_derange_pas_les_voisins_rend_elle_le_troisieme_saut_plus_juste.png")
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
