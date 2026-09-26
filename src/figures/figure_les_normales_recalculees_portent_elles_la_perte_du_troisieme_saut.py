"""Le troisième saut de la bande, reparti du deuxième saut corrigé avec les normales recalculées, puis avec celles du témoin.

⚠⚠ **Ce que cette figure doit rendre évident.** Au troisième saut, les ratés rendus justes et les justes rendus ratés, rangés
par la distance en mailles au plus proche point déplacé : à gauche avec les normales recalculées (`286`), à droite avec
celles du témoin.

  uv run python src/figures/figure_les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.py \\
      --sortie docs/images/287_les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.json"
CE_QUE_286_A_PUBLIE = RACINE / "docs" / "mesures" / "les_pertes_du_troisieme_saut_viennent_elles_des_points_corriges.json"

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
LES_SAUTS = (("dans_286", "NORMALES RECALCULÉES"), ("avec_les_normales_du_temoin", "NORMALES DU TÉMOIN"))


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    d["dans_286"] = json.loads(CE_QUE_286_A_PUBLIE.read_text())["le_troisieme_saut"]
    d["avec_les_normales_du_temoin"] = d["le_troisieme_saut_range"]
    return d


def le_titre(d: dict) -> str:
    a = d["les_justes_perdus_autour"]
    return (f"AU TROISIÈME SAUT, AVEC LES NORMALES DU TÉMOIN, LA REPRISE PERD {a['avec_les_normales_du_temoin']} JUSTES "
            f"AUTOUR DES POINTS CORRIGÉS, CONTRE {a['dans_285']}")


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
    ecrire(50, 52, f"20260623142658-w028-037 · le deuxième saut recalé de 285 · {d['les_points_deplaces']} points déplacés · "
                   "au troisième saut, distance en mailles au plus proche d'entre eux · le juge ne sert qu'à noter", petit, GRIS)
    vmax = max([max(c["les_rates_rendus_justes"], c["les_justes_rendus_rates"])
                for cle, _ in LES_SAUTS for c in d[cle]["les_classes"].values()] + [1])
    for k, (cle, titre) in enumerate(LES_SAUTS):
        x0 = 50 + k * 640
        s = d[cle]
        panneau(x0, 80, x0 + 620, 440, f"{titre} · {s['ou_les_deux_chaines_different']} POINTS NOTÉS CHANGENT")
        base, haut = 370, 200
        for j, (cc, nom) in enumerate(LES_CLASSES):
            c = s["les_classes"][cc]
            xj = x0 + 40 + j * 145
            for m, (cle_c, coul) in enumerate((("les_rates_rendus_justes", BON), ("les_justes_rendus_rates", ALERTE))):
                h = c[cle_c] / vmax * haut
                x = xj + m * 48
                art.rectangle([x, base - h, x + 38, base], fill=coul)
                traces["barres"].append((cle, cc, cle_c, c[cle_c]))
                points.append((x + 38, base - h))
                ecrire(x + 4, int(base - h) - 18, str(c[cle_c]), 0, ENCRE)
            art.line([xj - 6, base, xj + 92, base], fill=GRIS)
            ecrire(xj, base + 8, nom, 0, ENCRE)
            ecrire(xj, base + 26, f"{c['ou_les_deux_chaines_different']} changent", 0, GRIS)
        ecrire(x0 + 40, 118, "■ ratés rendus justes", 0, BON)
        ecrire(x0 + 220, 118, "■ justes rendus ratés", 0, ALERTE)

    art.rectangle([0, 456, L_, H_], fill=BANDE)
    ecrire(50, 468, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    c3, s3 = d["les_comptes_de_285_refaits"]["au_troisieme"], d["les_sauts"][0]
    ecrire(50, 490, f"les reprises de 285 redonnent ses comptes, {c3[0]} pour {c3[1]} ; avec les normales du témoin, "
                    f"{s3['les_rates_rendus_justes']} pour {s3['les_justes_rendus_rates']}", moyen, ENCRE)
    ecrire(50, 514, "⚠ ce qui n'est PAS établi : le vote, isolé à son tour ; si garder les normales du témoin est une bonne reprise.",
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
    tmp = sortie.parent / ".sonde_287.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    a = d["les_justes_perdus_autour"]
    v("★★★ le titre LIT la mesure", f"PERD {a['avec_les_normales_du_temoin']} JUSTES" in le_titre(d)
      and f"CONTRE {a['dans_285']}" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(s, c, k, d[s]["les_classes"][c][k]) for s, _ in LES_SAUTS for c, _ in LES_CLASSES
               for k in ("les_rates_rendus_justes", "les_justes_rendus_rates")]
    v("★★★★ une barre par compte et par classe, chacune au compte mesuré", traces["barres"] == attendu)
    v("★★★★ les classes redonnent les comptes du saut",
      all(sum(c[k] for c in d[s]["les_classes"].values()) == d[s][k] for s, _ in LES_SAUTS
          for k in ("les_rates_rendus_justes", "les_justes_rendus_rates")))
    txt = " ".join(t_ for _, _, t_, _ in poses)
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
                   / "287_les_normales_recalculees_portent_elles_la_perte_du_troisieme_saut.png")
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
