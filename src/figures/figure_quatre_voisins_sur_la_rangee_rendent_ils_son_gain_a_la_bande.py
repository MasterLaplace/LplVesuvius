"""Quatre voisins sur la rangée, deux de chaque côté : ce qu'ils font à la procédure, sur le segment et sur la bande.

⚠⚠ **Ce que cette figure doit rendre évident.** Pour le segment `20230702185753` et pour la bande `w028-037`, les ratés rendus
justes et les justes rendus ratés, avec les voisins de la procédure publiée (`275`, `281`) puis avec quatre voisins sur la rangée.

  uv run python src/figures/figure_quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.py \\
      --sortie docs/images/294_quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.png
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
LES_MESURES = RACINE / "docs" / "mesures"
LA_MESURE = LES_MESURES / "quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.json"
LES_PUBLIEES = {"le_segment": ("275", "la_procedure_sans_juge_tient_elle_sur_le_segment_entier.json"),
                "la_bande": ("281", "la_procedure_sans_juge_tient_elle_sur_la_bande.json")}

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 540


def _fr(x, n: int = 4) -> str:
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    for cle, (_, f) in LES_PUBLIEES.items():
        d[cle]["la_publiee"] = json.loads((LES_MESURES / f).read_text())["les_reunis"]
    return d


def le_titre(d: dict) -> str:
    s = d["le_segment"]["avec_quatre_voisins_sur_la_rangee"]["les_reunis"]
    b = d["la_bande"]["avec_quatre_voisins_sur_la_rangee"]["les_reunis"]
    return (f"AVEC QUATRE VOISINS SUR LA RANGÉE, LE GAIN NET VAUT {_fr(s['le_gain_net'])} SUR LE SEGMENT, "
            f"CONTRE {_fr(d['le_segment']['la_publiee']['le_gain_net'])}, ET {_fr(b['le_gain_net'])} SUR LA BANDE")


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
    ecrire(50, 52, "premier saut · la marche sur cinq blocs d'une rangée, l'ancre sur sa rangée · aucune pile rendue · "
                   "test du signe de 290 · le juge ne sert qu'à noter", petit, GRIS)
    vmax = max([max(r["les_rates_rendus_justes"], r["les_justes_rendus_rates"])
                for cle in LES_PUBLIEES for r in (d[cle]["la_publiee"], d[cle]["avec_quatre_voisins_sur_la_rangee"]
                                                  ["les_reunis"])] + [1])
    for k, (cle, titre) in enumerate((("le_segment", "LE SEGMENT 20230702185753"), ("la_bande", "LA BANDE W028-037"))):
        x0p = 50 + k * 640
        panneau(x0p, 80, x0p + 620, 420, titre)
        tranche = LES_PUBLIEES[cle][0]
        for j, (nom, r, t) in enumerate(((f"les voisins de {tranche}", d[cle]["la_publiee"], None),
                                         ("quatre sur la rangée", d[cle]["avec_quatre_voisins_sur_la_rangee"]["les_reunis"],
                                          d[cle]["avec_quatre_voisins_sur_la_rangee"]["le_test"]))):
            x0 = x0p + 90 + j * 270
            base, haut = 340, 190
            for m, (c, coul) in enumerate((("les_rates_rendus_justes", BON), ("les_justes_rendus_rates", ALERTE))):
                h = r[c] / vmax * haut
                x = x0 + m * 60
                art.rectangle([x, base - h, x + 48, base], fill=coul)
                traces["barres"].append((cle, j, c, r[c]))
                points.append((x + 48, base - h))
                ecrire(x + 4, int(base - h) - 18, str(r[c]), 0, ENCRE)
            art.line([x0 - 8, base, x0 + 120, base], fill=GRIS)
            ecrire(x0, base + 8, nom, 0, ENCRE)
            ecrire(x0, base + 26, f"gain net {_fr(r['le_gain_net'])} · {r['les_points_corriges']} corrigés", 0, GRIS)
        ecrire(x0p + 90, 118, "■ ratés rendus justes", 0, BON)
        ecrire(x0p + 270, 118, "■ justes rendus ratés", 0, ALERTE)

    art.rectangle([0, 436, L_, H_], fill=BANDE)
    ecrire(50, 448, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 470, "avec un bloc de chaque côté et leurs voisins publiés, le calcul redonne 275 et 281 bloc par bloc", moyen,
           ENCRE)
    ecrire(50, 494, "⚠ ce qui n'est PAS établi : pourquoi une marche plus longue sur la rangée perd ; le deuxième saut.", moyen,
           ALERTE)

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
    tmp = sortie.parent / ".sonde_294.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    b = d["la_bande"]["avec_quatre_voisins_sur_la_rangee"]["les_reunis"]
    v("★★★ le titre LIT la mesure", le_titre(d).endswith(f"ET {_fr(b['le_gain_net'])} SUR LA BANDE"))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(cle, j, c, r[c]) for cle in ("le_segment", "la_bande")
               for j, r in enumerate((d[cle]["la_publiee"], d[cle]["avec_quatre_voisins_sur_la_rangee"]["les_reunis"]))
               for c in ("les_rates_rendus_justes", "les_justes_rendus_rates")]
    v("★★★★ une barre par compte, chacune au compte mesuré ou publié", traces["barres"] == attendu)
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
                   / "294_quatre_voisins_sur_la_rangee_rendent_ils_son_gain_a_la_bande.png")
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
