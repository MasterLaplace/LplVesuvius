"""Où est le plus dense du profil moyen, par rapport à la surface : le tracé humain de PHercParis4, décalé ou non, et les surfaces de m7 sur PHerc0358.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, bloc par bloc, où tombe le plus dense du profil moyen du tracé humain à
sa place, dans la bande d'un quart de pas ou hors d'elle : c'est ce qui dit si le juge peut s'étalonner sur lui. À droite, la même
lecture sur chaque surface de `m7` de PHerc0358.

  uv run python src/figures/figure_le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.py \\
      --sortie docs/images/309_le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.png

⚠ Tout vient de la mesure.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (226, 236, 230)
L_, H_ = 1360, 700
LA_BANDE = 600
LA_PORTEE = 21


def _fr(x, n: int = 1) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].split(" : ")[0].upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def colonne(x0, y0, x1, y1, titre, lignes, quart):
        """Une ligne par surface : une barre du centre (la surface) au plus dense, sur ±21 voxels."""
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 10, y0 + 8, titre, moyen, ENCRE)
        gx0, gx1 = x0 + 190, x1 - 20
        xm = (gx0 + gx1) / 2

        def xu(u):
            return xm + u / LA_PORTEE * (gx1 - gx0) / 2

        top, pas_ = y0 + 34, (y1 - y0 - 60) / max(1, len(lignes))
        art.rectangle([xu(-quart), top, xu(quart), top + pas_ * len(lignes)], fill=PALE)
        art.line([xm, top, xm, top + pas_ * len(lignes)], fill=GRIS)
        for k, (nom, u, ok) in enumerate(lignes):
            y = top + pas_ * k + pas_ / 2
            ecrire(x0 + 10, int(y - 7), nom, 0, ENCRE if u is not None else GRIS)
            if u is not None:
                art.line([xm, y, xu(u), y], fill=BON if ok else ALERTE, width=3)
                art.ellipse([xu(u) - 3, y - 3, xu(u) + 3, y + 3], fill=BON if ok else ALERTE)
            traces["barres"].append((titre, nom, u))
        for u in (-LA_PORTEE, -quart, 0, quart, LA_PORTEE):
            ecrire(int(xu(u)) - 8, int(top + pas_ * len(lignes)) + 4, _fr(float(u), 0), 0, GRIS)

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "barre : de la surface au plus dense de son profil moyen, en voxels le long de la normale ; bande claire : un "
                   "quart de pas de part et d'autre, ce que le juge appelle posée sur sa feuille", petit, GRIS)
    q = d["les_constantes"]["les_quarts_de_pas_voxels"]
    blocs = [(f"bloc {b['le_bloc'][0]}_{b['le_bloc'][1]}", b["le_plus_dense"]["p0"], b["posee"]["p0"])
             for b in d["paris4"]["les_blocs"]]
    colonne(50, 72, 660, 586, "PHercParis4 : le tracé humain à sa place, 24 blocs neufs", blocs, q["PHercParis4"])
    surf = [(s["la_surface"].replace("_", " "), s["le_plus_dense"], s["posee"]) for s in d["phercs0358"]["les_surfaces"]]
    colonne(700, 72, 1310, 586, "PHerc0358 : les surfaces de m7", surf, q["PHerc0358"])

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : quelle face de sa feuille une surface suit, ni si deux feuilles collées se "
                              "lisent comme une.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


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
    tmp = sortie.parent / ".sonde_309.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "le juge juge : oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LE JUGE JUGE", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [b["le_plus_dense"]["p0"] for b in d["paris4"]["les_blocs"]] + [s["le_plus_dense"]
                                                                           for s in d["phercs0358"]["les_surfaces"]]
    v("★★★ une barre par surface, au plus dense mesuré", [u for _, _, u in traces["barres"]] == attendu)
    v("★★★ aucune barre ne sort de la portée du profil",
      all(u is None or abs(u) <= LA_PORTEE for _, _, u in traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "309_le_plus_dense_dit_il_si_une_surface_est_sur_sa_feuille.png")
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
