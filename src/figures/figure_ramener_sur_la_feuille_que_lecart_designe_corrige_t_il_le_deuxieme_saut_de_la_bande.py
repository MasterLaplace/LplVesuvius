"""Au deuxième saut de la bande, la décision de `264` contre la correction qui pose le point sur la feuille que l'écart désigne.

⚠⚠ **Ce que cette figure doit rendre évident.** Pour les deux choix, pris sur le même écart lu, les ratés rendus justes et les
justes rendus ratés sur les blocs notés ; à droite, combien de points chacun déplace, et parmi eux combien de ratés que l'écart
répare et de justes qu'il casse.

  uv run python src/figures/figure_ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.py \\
      --sortie docs/images/289_ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.png
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
LA_MESURE = (RACINE / "docs" / "mesures"
             / "ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 520


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


def les_choix(d: dict) -> list[tuple[str, int, int]]:
    p, r = d["la_decision_de_283_publiee"], d["les_blocs_notes_reunis"]
    return [("la décision de 264 (283)", p["des_reparables"], p["des_cassables"]),
            ("la feuille que l'écart désigne", r["les_rates_rendus_justes"], r["les_justes_rendus_rates"])]


def le_titre(d: dict) -> str:
    r = d["les_blocs_notes_reunis"]
    return (f"POSÉS SUR LA FEUILLE QUE L'ÉCART DÉSIGNE, {d['les_points_qui_bougent']} POINTS DU DEUXIÈME SAUT RENDENT "
            f"{r['les_rates_rendus_justes']} RATÉS JUSTES ET {r['les_justes_rendus_rates']} JUSTES RATÉS : "
            f"UN GAIN NET DE {_fr(r['le_gain_net'])}")


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
    ecrire(50, 52, f"20260623142658-w028-037 · {d['les_blocs_notes']} blocs notés de 283 · le même écart lu · une feuille est "
                   "reconnue à moins de 12 voxels · le juge ne sert qu'à noter", petit, GRIS)
    panneau(50, 80, 700, 400, "SUR LES BLOCS NOTÉS, SELON LE CHOIX")
    choix = les_choix(d)
    vmax = max([max(a, b) for _, a, b in choix] + [1])
    base, haut = 330, 180
    for k, (nom, rj, jr) in enumerate(choix):
        x0 = 110 + k * 290
        for j, (val, coul) in enumerate(((rj, BON), (jr, ALERTE))):
            h = val / vmax * haut
            x = x0 + j * 60
            art.rectangle([x, base - h, x + 48, base], fill=coul)
            traces["barres"].append((nom, j, val))
            points.append((x + 48, base - h))
            ecrire(x + 4, int(base - h) - 18, str(val), 0, ENCRE)
        art.line([x0 - 8, base, x0 + 120, base], fill=GRIS)
        ecrire(x0, base + 8, nom, 0, ENCRE)
        ecrire(x0, base + 26, f"gain net {_fr(rj - jr)}", 0, GRIS)
    ecrire(110, 118, "■ ratés rendus justes", 0, BON)
    ecrire(290, 118, "■ justes rendus ratés", 0, ALERTE)

    panneau(716, 80, 1310, 400, "CE QUE CHAQUE CHOIX DÉPLACE")
    p, e, r = d["la_decision_de_283_publiee"], d["parmi_eux"], d["le_deuxieme_saut_entier"]
    lignes = (f"écart lu sur {d['les_points_ou_lecart_est_lu']} points des blocs notés",
              f"ratés que l'écart répare : {e['les_reparables_en_tout']} · justes qu'il casse : {e['les_cassables_en_tout']}",
              f"la décision de 264 déplace {p['en_tout']} points",
              f"la feuille désignée en déplace {d['les_points_qui_bougent']}, dont {e['des_reparables']} réparables et "
              f"{e['des_cassables']} cassables",
              f"deuxième saut entier : de {_fr(r['le_temoin'])} à {_fr(r['partie_de_la_spire_corrigee'])}")
    for k, t in enumerate(lignes):
        ecrire(736, 124 + 30 * k, t, 0, ENCRE)

    art.rectangle([0, 416, L_, H_], fill=BANDE)
    ecrire(50, 428, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 450, f"l'écart relu redonne la décision de 283 sur ses {d['les_blocs_notes']} blocs notés, "
                    f"{p['des_reparables']} pour {p['des_cassables']}", moyen, ENCRE)
    ecrire(50, 474, "⚠ ce qui n'est PAS établi : le troisième saut, reparti de cette correction ; le premier saut ; le segment "
                    "20230702185753.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_289.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    r = d["les_blocs_notes_reunis"]
    v("★★★ le titre LIT la mesure", f"GAIN NET DE {_fr(r['le_gain_net'])}" in le_titre(d)
      and f"{d['les_points_qui_bougent']} POINTS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    attendu = [(nom, j, val) for nom, a, b in les_choix(d) for j, val in enumerate((a, b))]
    v("★★★★ une barre par compte et par choix, chacune au compte mesuré", traces["barres"] == attendu and len(attendu) == 4)
    v("★★★★ le gain dessiné de la feuille désignée est celui de la mesure",
      les_choix(d)[1][1] - les_choix(d)[1][2] == r["le_gain_net"])
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
                   / "289_ramener_sur_la_feuille_que_lecart_designe_corrige_t_il_le_deuxieme_saut_de_la_bande.png")
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
