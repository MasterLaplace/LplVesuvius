"""La chaîne de la bande `w028-037` repartie du deuxième saut corrigé, recalé sur son rayon : ce qu'elle change, saut par saut.

⚠⚠ **Ce que cette figure doit rendre évident.** Pour le deuxième saut recalé et pour les deux sauts qui en repartent, les ratés
que la reprise rend justes et les justes qu'elle rend ratés, contre le témoin reparti du deuxième saut non corrigé. À droite, à quelle
distance de la feuille, sur le rayon du saut, les points sont posés avant et après la correction.

  uv run python src/figures/figure_recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.py \\
      --sortie docs/images/285_recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.png
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
             / "recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
L_, H_ = 1360, 560


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


def les_colonnes(d: dict) -> list[tuple[str, dict]]:
    return ([("le deuxième saut, recalé sur son rayon", d["le_deuxieme_saut"]["recale_contre_temoin"])]
            + [(f"le {'troisième' if s['le_saut'] == 3 else 'quatrième'} saut", s) for s in d["les_sauts"]])


def le_titre(d: dict) -> str:
    s = d["les_sauts"][0]
    return (f"RECALÉ SUR SON RAYON, LE DEUXIÈME SAUT CORRIGÉ REND AU TROISIÈME SAUT {s['les_rates_rendus_justes']} RATÉS "
            f"JUSTES ET {s['les_justes_rendus_rates']} JUSTES RATÉS : UN GAIN NET DE {_fr(s['le_gain_net'])}")


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
    ecrire(50, 52, "20260623142658-w028-037 · m7, côté plus · le témoin repart du deuxième saut non corrigé · le juge, les "
                   "couches de la bande, ne sert qu'à noter", petit, GRIS)

    # ── PANNEAU 1 · SAUT PAR SAUT ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 860, 440, "CE QUE LA REPRISE CHANGE, SAUT PAR SAUT, CONTRE LE TÉMOIN")
    cols = les_colonnes(d)
    vmax = max([max(c["les_rates_rendus_justes"], c["les_justes_rendus_rates"]) for _, c in cols] + [1])
    base, haut = 380, 200
    for k, (nom, c) in enumerate(cols):
        x0 = 110 + k * 250
        for j, (cle, coul) in enumerate((("les_rates_rendus_justes", BON), ("les_justes_rendus_rates", ALERTE))):
            h = c[cle] / vmax * haut
            x = x0 + j * 60
            art.rectangle([x, base - h, x + 44, base], fill=coul)
            traces["barres"].append((nom, cle, c[cle]))
            points.append((x + 44, base - h))
            ecrire(x + 4, int(base - h) - 18, str(c[cle]), 0, ENCRE)
        art.line([x0 - 10, base, x0 + 120, base], fill=GRIS)
        ecrire(x0, base + 8, nom, 0, ENCRE)
        ecrire(x0, base + 26, f"gain net {_fr(c['le_gain_net'])} · {c['les_points_notes']} notés", 0, GRIS)
    ecrire(110, 118, "■ ratés rendus justes", 0, BON)
    ecrire(290, 118, "■ justes rendus ratés", 0, ALERTE)

    # ── PANNEAU 2 · LE RECALAGE ───────────────────────────────────────────────────────────────────────────────────────
    panneau(876, 80, 1310, 440, "SUR LE RAYON DU SAUT, LA FEUILLE LA PLUS PROCHE")
    dd = d["la_distance_a_la_feuille_sur_le_rayon_du_saut"]
    tout, avant, apres = (dd[k] for k in ("le_deuxieme_saut_non_corrige_partout",
                                          "le_deuxieme_saut_non_corrige_aux_points_deplaces",
                                          "le_deuxieme_saut_corrige_aux_points_deplaces"))
    rc = d["le_deuxieme_saut"]["recale_contre_corrige"]
    lignes = (f"non corrigé, partout : médiane {_fr(tout['la_mediane_voxels'])} voxel,",
              f"    {tout['au_dela_dun_demi_feuillet']} des {tout['les_points']} au-delà d'un demi-feuillet",
              f"non corrigé, aux {avant['les_points']} points déplacés : médiane {_fr(avant['la_mediane_voxels'])}, "
              f"{avant['au_dela_dun_demi_feuillet']} au-delà",
              f"corrigé, aux mêmes points : médiane {_fr(apres['la_mediane_voxels'])} voxels, "
              f"{apres['au_dela_dun_demi_feuillet']} au-delà",
              f"recalés sur une feuille de m7 : {d['les_points_recales']} des {d['les_points_deplaces_par_283']}",
              f"recalé contre corrigé : {rc['les_rates_rendus_justes']} ratés justes pour {rc['les_justes_rendus_rates']} "
              f"{'juste raté' if rc['les_justes_rendus_rates'] == 1 else 'justes ratés'}")
    for k, t in enumerate(lignes):
        ecrire(896, 124 + 30 * k, t, 0, ENCRE)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 456, L_, H_], fill=BANDE)
    ecrire(50, 468, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 490, "la reprise partie du deuxième saut non corrigé redonne les normales et les sauts 3 et 4 de 248, compte "
                    "pour compte", moyen, ENCRE)
    ecrire(50, 514, "⚠ ce qui n'est PAS établi : une correction du troisième saut ; un autre côté, une autre prédiction.",
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
    tmp = sortie.parent / ".sonde_285.png"
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
    attendu = [(n, c_, col[c_]) for n, col in les_colonnes(d) for c_ in ("les_rates_rendus_justes", "les_justes_rendus_rates")]
    v("★★★★ une barre par compte, et chacune porte le compte mesuré", traces["barres"] == attendu and len(attendu) == 6)
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
                   / "285_recaler_le_deuxieme_saut_sur_son_rayon_rend_il_le_troisieme_saut_plus_juste.png")
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
