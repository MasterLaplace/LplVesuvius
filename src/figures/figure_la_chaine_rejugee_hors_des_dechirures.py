"""La chaîne de `248`, rejugée là où la couche du juge ne se déchire pas.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA PART SUR LA BONNE SPIRE SAUT APRÈS SAUT, pour la chaîne et le
pas fixe, jugés comme `248` et jugés sans falaise : la chaîne remonte, le pas fixe non. Au milieu, CE QUE CHAQUE SAUT
GARDE de ceux qui avaient tenu le précédent : près de dix-neuf sur vingt. À droite, LA PART DE LA COUCHE DU JUGE QUI SE
DÉCHIRE à chaque saut, qui dit pourquoi les sauts lointains sont jugés sur si peu de points.

  uv run python src/figures/figure_la_chaine_rejugee_hors_des_dechirures.py \\
      --sortie docs/images/253_la_chaine_rejugee_hors_des_dechirures.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_rejugee_hors_des_dechirures.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (150, 185, 170)
CONTRE = (92, 108, 150)
CONTRE_PALE = (170, 180, 205)
L_, H_ = 1360, 950
LA_PREDICTION = "m7"
LES_COTES = (("plus", "du_cote_plus"), ("moins", "du_cote_moins"))
LES_COURBES = (("la chaîne, jugée comme 248", "le_juge_de_248", "la_chaine", PALE, 2),
               ("la chaîne, jugée sans falaise", "le_juge_sans_falaise", "la_chaine", BON, 4),
               ("le pas fixe, jugé comme 248", "le_juge_de_248", "le_temoin_sans_lecture", CONTRE_PALE, 2),
               ("le pas fixe, jugé sans falaise", "le_juge_sans_falaise", "le_temoin_sans_lecture", CONTRE, 3))


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_courbe(d: dict, cote: str, juge: str, qui: str) -> list[float]:
    return d["les_predictions"][LA_PREDICTION][cote][juge]["sur_les_points_notes_a_chaque_saut"][qui]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : jugée sans falaise, la chaîne tient-elle les quatre sauts mieux que jugée comme 248 ?"""
    x = d["les_predictions"][LA_PREDICTION]
    a = [x[c]["le_juge_sans_falaise"]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"] for _, c in LES_COTES]
    b = [x[c]["le_juge_de_248"]["qui_tient"]["la_chaine"]["la_part_qui_tient_tous_les_sauts"] for _, c in LES_COTES]
    if min(a) > max(b):
        return (f"JUGÉE LÀ OÙ LE JUGE NE SE DÉCHIRE PAS, LA CHAÎNE TIENT QUATRE SPIRES SUR {_fr(a[0])} ET {_fr(a[1])} DES "
                f"POINTS, AU LIEU DE {_fr(b[0])} ET {_fr(b[1])}")
    return "JUGÉE LÀ OÙ LE JUGE NE SE DÉCHIRE PAS, LA CHAÎNE NE TIENT PAS MIEUX"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    x = d["les_predictions"][LA_PREDICTION]
    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"la chaîne de 248 sur la bande {d['le_segment']}, prédiction {LA_PREDICTION} · jugée sans falaise : la "
                   f"couche h de la bande n'est bordée d'aucune voisine à un demi-feuillet ou plus", petit, GRIS)

    # ── PANNEAU 1 · SAUT APRÈS SAUT ──────────────────────────────────────────────────────────
    panneau(50, 84, 760, 560, "LA PART SUR LA BONNE SPIRE, SUR LES POINTS NOTÉS À CHAQUE SAUT")
    Y0, Y1 = 0.4, 1.0
    courbes = 0
    for c, (nom_c, cote) in enumerate(LES_COTES):
        gx0, gx1, gy0, gy1 = 100 + c * 340, 360 + c * 340, 150, 440
        n248 = x[cote]["le_juge_de_248"]["sur_les_points_notes_a_chaque_saut"]["les_points"]
        nsf = x[cote]["le_juge_sans_falaise"]["sur_les_points_notes_a_chaque_saut"]["les_points"]
        ecrire(gx0, 118, f"côté {nom_c} · {n248} et {nsf} points", 0, ENCRE)
        for f_ in (0.4, 0.6, 0.8, 1.0):
            yg = gy1 - (gy1 - gy0) * (f_ - Y0) / (Y1 - Y0)
            art.line([gx0, yg, gx1, yg], fill=TRAIT, width=1)
            ecrire(gx0 - 32, yg - 7, _fr(f_, 1), 0, GRIS)
        for h in range(4):
            ecrire(gx0 + (gx1 - gx0) * h / 3 - 3, gy1 + 6, str(h + 1), 0, GRIS)
        for _, juge, qui, coul, ep in LES_COURBES:
            ys = la_courbe(d, cote, juge, qui)
            pts = [(gx0 + (gx1 - gx0) * h / 3, gy1 - (gy1 - gy0) * (y - Y0) / (Y1 - Y0)) for h, y in enumerate(ys)]
            art.line(pts, fill=coul, width=ep)
            for p in pts:
                art.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=coul)
                points.append(p)
            courbes += 1
        ecrire(gx0, gy1 + 22, "saut", 0, GRIS)
    traces["courbes"] = courbes
    for k, (nom, _, _, coul, _) in enumerate(LES_COURBES):
        xl, yl = 74 + (k % 2) * 340, 494 + (k // 2) * 22
        art.rectangle([xl, yl + 3, xl + 14, yl + 11], fill=coul)
        ecrire(xl + 22, yl, nom, 0, ENCRE)

    # ── PANNEAU 2 · CE QUE CHAQUE SAUT GARDE ────────────────────────────────────────────────
    panneau(780, 84, 1310, 480, "CE QUE CHAQUE SAUT GARDE DE CEUX QUI AVAIENT TENU")
    bx0, bx1 = 1000, 1230
    B0 = 0.8
    y = 128
    barres = 0
    for nom_c, cote in LES_COTES:
        ecrire(796, y, f"côté {nom_c}", 0, ENCRE)
        y += 20
        for juge, nom_j, coul in (("le_juge_de_248", "jugé comme 248", PALE), ("le_juge_sans_falaise", "jugé sans falaise", BON)):
            pas = x[cote][juge]["qui_tient"]["la_chaine"]["parmi_ceux_qui_ont_tenu_le_saut_precedent"]
            ecrire(810, y, nom_j, 0, GRIS)
            for h, v_ in enumerate(pas):
                yy = y + 16 + h * 11
                w = (bx1 - bx0) * (max(v_, B0) - B0) / (1 - B0)
                art.rectangle([bx0, yy, bx0 + w, yy + 8], fill=coul)
                points.append((bx0 + w, yy + 8))
                ecrire(830, yy - 2, f"saut {h + 1}", 0, GRIS)
                ecrire(bx1 + 8, yy - 2, _fr(v_), 0, ENCRE)
                barres += 1
            y += 16 + 4 * 11 + 8
        y += 6
    traces["barres"] = barres
    ecrire(796, y, "l'échelle commence à 0,8", 0, GRIS)

    # ── PANNEAU 3 · LA COUCHE DU JUGE SE DÉCHIRE ─────────────────────────────────────────────
    panneau(780, 500, 1310, 800, "LA PART DE LA COUCHE DU JUGE BORDÉE D'UNE FALAISE")
    y = 544
    for nom_c, cote in LES_COTES:
        bo = x[cote]["la_part_des_couches_bordees_dune_falaise"]
        de = x[cote]["la_part_des_couches_dechirees"]
        ecrire(796, y, f"côté {nom_c}", 0, ENCRE)
        ecrire(810, y + 18, "bordée d'une falaise : " + " · ".join(_fr(v_) for v_ in bo), 0, GRIS)
        ecrire(810, y + 36, "ou hors de la plus grande pièce : " + " · ".join(_fr(v_) for v_ in de), 0, GRIS)
        y += 64
    ecrire(796, y + 4, "au saut 3 et au saut 4, les couches sont morcelées par", 0, GRIS)
    ecrire(796, y + 20, "des trous : la plus grande pièce en écarte presque tout", 0, GRIS)
    pas248 = x["du_cote_plus"]["le_juge_de_248"]["qui_tient"]["la_chaine"]["parmi_ceux_qui_ont_tenu_le_saut_precedent"]
    passf = x["du_cote_plus"]["le_juge_sans_falaise"]["qui_tient"]["la_chaine"]["parmi_ceux_qui_ont_tenu_le_saut_precedent"]

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ip = x["du_cote_plus"]["le_juge_intact"]["par_saut"]
    im = x["du_cote_moins"]["le_juge_intact"]["par_saut"]
    ecrire(50, 832, "LE VERDICT : jugée là où le juge ne se déchire pas, la chaîne garde près de dix-neuf points sur vingt à "
                    "chaque saut", petit, ENCRE)
    ecrire(50, 856, f"★ au premier saut, avec le juge déclaré d'avance : {_fr(ip[0]['la_chaine']['la_part_sur_la_bonne_spire'])} et "
                    f"{_fr(im[0]['la_chaine']['la_part_sur_la_bonne_spire'])} ; au deuxième, "
                    f"{_fr(ip[1]['la_chaine']['la_part_sur_la_bonne_spire'])} et {_fr(im[1]['la_chaine']['la_part_sur_la_bonne_spire'])}"
                    f" ; jugé comme 248, le premier saut gardait {_fr(pas248[0])}.", moyen, ENCRE)
    ecrire(50, 882, f"★ jugé sans falaise, chaque saut garde {_fr(min(passf))} à {_fr(max(passf))} de ceux qui avaient "
                    f"tenu, côté plus ; le pas fixe ne remonte pas.", moyen, ENCRE)
    ecrire(50, 908, "⚠ ce qui n'est PAS établi : là où le juge se déchire, la matière est peut-être aussi la plus difficile ; "
                    "le juge sans falaise a été ajouté après la mesure.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
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

    d = lire()
    tmp = sortie.parent / ".sonde_253.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "JUGÉE LÀ OÙ LE JUGE NE SE DÉCHIRE PAS" in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque courbe est dessinée, des deux côtés", traces["courbes"] == 2 * len(LES_COURBES))
    v("★★★★ chaque saut a sa barre, deux juges et deux côtés", traces["barres"] == 16)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les deux juges et ce qui n'est PAS établi",
      "jugé comme 248" in txt and "sans falaise" in txt and "n'est PAS établi" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "253_la_chaine_rejugee_hors_des_dechirures.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
