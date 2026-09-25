"""Trois façons de lire un pas, sur deux blocs : ce que chacune retrouve d'une rampe, et ce qu'elle voit de la spire produite.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LA MÊME RAMPE NUMÉRIQUE sur trois piles, lue à la couture, de
centre à centre et de fenêtre en fenêtre : seule la dernière la retrouve partout. Au milieu, les cartes des deux blocs :
l'erreur jugée, et la marche de fenêtre en fenêtre de la spire produite moins celle du segment. En bas, l'accord des paires,
avec le témoin plat.

  uv run python src/figures/figure_le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.py \\
      --sortie docs/images/260_le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.png
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
M = RACINE / "docs" / "mesures"
LA_MESURE = M / "le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.json"
DE_258 = M / "le_pas_de_centre_a_centre_voit_il_la_rampe.json"
DE_259 = M / "le_pas_de_centre_a_centre_la_ou_le_segment_tient_sa_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
VIDE = (228, 226, 220)
PALE = (150, 185, 170)
L_, H_ = 1360, 1000
LA_PORTEE = 108.0
LES_PAS = (("à la couture", ALERTE), ("de centre à centre", PALE), ("de fenêtre en fenêtre", BON))


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
    d["_258"], d["_259"] = json.loads(DE_258.read_text()), json.loads(DE_259.read_text())
    return d


def les_rampes(d: dict) -> list[tuple[str, list[float]]]:
    a, b, r = d["_258"]["la_rampe_numerique"], d["_259"], d["la_rampe_numerique"]
    return [("le bloc de 257, segment réduit", [a["a_la_couture"]["la_pente"], a["de_centre_a_centre"]["la_pente"],
                                                r["le_bloc_de_257_segment_reduit"]["la_pente"]]),
            ("le bloc de 259, segment réduit", [b["la_rampe_numerique"]["a_la_couture"]["la_pente"],
                                                b["la_rampe_numerique"]["de_centre_a_centre"]["la_pente"],
                                                r["le_bloc_de_259_segment_reduit"]["la_pente"]]),
            ("le bloc de 259, pile publiée", [b["la_pile_publiee"]["la_rampe_numerique"]["a_la_couture"]["la_pente"],
                                              b["la_pile_publiee"]["la_rampe_numerique"]["de_centre_a_centre"]["la_pente"],
                                              r["le_bloc_de_259_pile_publiee"]["la_pente"]])]


def les_paires(d: dict) -> list[tuple[str, list[tuple[str, dict]]]]:
    s8, s9 = d["_258"], d["_259"]["les_marches"]
    b7, b9 = d["les_blocs"]["le_bloc_de_257"], d["les_blocs"]["le_bloc_de_259"]
    return [("le bloc de 257", [("le témoin plat", b7["le_temoin_plat"]),
                                ("à la couture", s8["la_difference_des_marches_des_coutures"]["laccord_des_paires"]),
                                ("de centre à centre", s8["la_difference_des_marches"]["laccord_des_paires"]),
                                ("de fenêtre en fenêtre", b7["la_difference"]["laccord_des_paires"])]),
            ("le bloc de 259", [("le témoin plat", b9["le_temoin_plat"]),
                                ("à la couture", s9["a_la_couture"]["la_difference"]["laccord_des_paires"]),
                                ("de centre à centre", s9["de_centre_a_centre"]["la_difference"]["laccord_des_paires"]),
                                ("de fenêtre en fenêtre", b9["la_difference"]["laccord_des_paires"])])]


def la_couleur(v) -> tuple[int, int, int]:
    if v is None:
        return VIDE
    t = max(-1.0, min(1.0, float(v) / LA_PORTEE))
    loin = CONTRE if t < 0 else ALERTE
    a = abs(t)
    return tuple(int(round(255 * (1 - a) + c * a)) for c in loin)


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : le pas de fenêtre en fenêtre retrouve-t-il la rampe partout, et sépare-t-il ?"""
    f = [x[1][2] for x in les_rampes(d)]
    sep = [b["la_difference"]["laccord_des_paires"]["la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe"]
           for b in d["les_blocs"].values()]
    if min(f) >= 0.5:
        return (f"DE FENÊTRE EN FENÊTRE, LE PAS RETROUVE LA RAMPE SUR LES TROIS PILES, ET SÉPARE {_fr(min(sep), 4)} À "
                f"{_fr(max(sep), 4)} DES PAIRES QUE LE JUGE SÉPARE")
    return f"DE FENÊTRE EN FENÊTRE, LE PAS NE RETROUVE QUE {_fr(min(f), 4)} DE LA RAMPE SUR L'UNE DES PILES"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {"barres": 0, "cartes": 0, "cellules": {}}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, "20230702185753 · rampe numérique de 24 voxels, la même matière décalée · la marche de la spire produite "
                   "moins celle du segment, contre l'erreur jugée", petit, GRIS)

    # ── PANNEAU 1 · LES RAMPES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 360, "CE QUE CHAQUE PAS RETROUVE D'UNE MÊME RAMPE : UN, TOUT ; ZÉRO, RIEN")
    bx0, bx1, P = 520, 1150, 2.0
    y = 118
    for qui, pentes in les_rampes(d):
        ecrire(66, y, qui, 0, ENCRE)
        for k, ((pas, coul), pente) in enumerate(zip(LES_PAS, pentes)):
            yy = y + k * 20
            ecrire(300, yy, pas, 0, GRIS)
            w = (bx1 - bx0) * max(0.0, min(P, pente)) / P
            art.rectangle([bx0, yy + 2, bx0 + w, yy + 14], fill=coul)
            points.append((bx0 + w, yy + 14))
            ecrire(bx0 + w + 8, yy, _fr(pente, 4), 0, ENCRE)
            traces["barres"] += 1
        y += 76
    for val, lib in ((0.5, "le seuil déclaré"), (1.0, "tout")):
        x = bx0 + (bx1 - bx0) * val / P
        art.line([x, 114, x, y - 12], fill=GRIS, width=1)
        ecrire(x - 30, y - 8, lib, 0, GRIS)

    # ── PANNEAU 2 · LES CARTES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 376, 1310, 640, "L'ERREUR JUGÉE, LA MARCHE DE FENÊTRE EN FENÊTRE DU SEGMENT, ET CELLE DE LA SPIRE PRODUITE "
                                "MOINS CELLE DU SEGMENT")
    cell = 9
    k = 0
    for nom, b in d["les_blocs"].items():
        lib = "257" if nom.endswith("257") else "259"
        for titre, cle in ((f"bloc {lib} : l'erreur du juge", "lerreur"), (f"bloc {lib} : le segment", "le_segment"),
                           (f"bloc {lib} : la différence", "la_difference")):
            x0, y0 = 66 + k * 205, 430
            ecrire(x0, 408, titre, 0, ENCRE)
            grille = b["les_cartes"][cle]
            n = 0
            for i, r in enumerate(grille):
                for j, v in enumerate(r):
                    art.rectangle([x0 + j * cell, y0 + i * cell, x0 + (j + 1) * cell - 1, y0 + (i + 1) * cell - 1],
                                  fill=la_couleur(v))
                    n += 1
            points.append((x0 + len(grille[0]) * cell, y0 + len(grille) * cell))
            traces["cellules"][f"{lib}_{cle}"] = n
            traces["cartes"] += 1
            k += 1
    b7, b9 = d["les_blocs"]["le_bloc_de_257"], d["les_blocs"]["le_bloc_de_259"]
    ecrire(66, 592, f"bleu et ocre : ±{_fr(LA_PORTEE, 0)} voxels ; blanc : zéro ; gris : non noté ou non relié", 0, GRIS)
    ecrire(66, 612, f"la marche du segment s'étend sur {_fr(b7['le_segment']['letendue_voxels'], 1)} voxels (bloc 257) et "
                    f"{_fr(b9['le_segment']['letendue_voxels'], 1)} (bloc 259) ; résidu {_fr(b7['le_segment']['le_residu_rms'], 2)} "
                    f"et {_fr(b9['le_segment']['le_residu_rms'], 2)} voxels", 0, GRIS)

    # ── PANNEAU 3 · LES PAIRES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 656, 1310, 900, "L'ACCORD DES PAIRES AVEC LE JUGE : SÉPARE CE QU'IL SÉPARE, RÉUNIT CE QU'IL RÉUNIT")
    for col, (bloc, lignes) in enumerate(les_paires(d)):
        x0 = 66 + col * 630
        ecrire(x0, 688, bloc, 0, ENCRE)
        for m, (nom, a) in enumerate(lignes):
            y = 712 + m * 44
            ecrire(x0, y, nom, 0, GRIS)
            for q, (lib, cle, coul) in enumerate((("sépare", "la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe", ALERTE),
                                                  ("réunit", "la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit", BON))):
                val = a.get(cle)
                yy = y + q * 18
                ecrire(x0 + 150, yy, lib, 0, GRIS)
                if val is not None:
                    art.rectangle([x0 + 200, yy + 2, x0 + 200 + 300 * float(val), yy + 12], fill=coul)
                    points.append((x0 + 200 + 300 * float(val), yy + 12))
                    traces["barres"] += 1
                ecrire(x0 + 510, yy, _fr(val, 4), 0, ENCRE)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 916, L_, H_], fill=BANDE)
    ecrire(50, 926, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 948, "★ pour la première fois, une mesure qui ne lit que le scan, rendu sur la spire produite et sur le segment, "
                    "sépare ce que le juge sépare.", moyen, ENCRE)
    ecrire(50, 972, "⚠ ce qui n'est PAS établi : deux blocs ; le pas surestime la rampe jusqu'à 1,83 ; il réunit mal "
                    "(0,54 et 0,65) ; un côté ; m7.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_260.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", ("SUR LES TROIS PILES" in le_titre(d)) == (min(x[1][2] for x in les_rampes(d)) >= 0.5))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ six cartes, une cellule par chunk", traces["cartes"] == 6 and all(n == 256 for n in traces["cellules"].values()),
      str(traces["cellules"]))
    v("★★★★ neuf pentes et seize parts ont leur barre", traces["barres"] == 25, str(traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le témoin, le seuil déclaré et ce qui n'est PAS établi",
      "témoin plat" in txt and "seuil déclaré" in txt and "n'est PAS établi" in txt)
    v("★★★★ les nombres de la bande sont ceux de la mesure",
      _fr(max(x[1][2] for x in les_rampes(d)), 2) in txt
      and _fr(d["les_blocs"]["le_bloc_de_257"]["la_difference"]["laccord_des_paires"]["la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit"], 2) in txt)
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
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "260_le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
