"""Le pas lu d'un centre de chunk à l'autre, contre le pas lu à la couture : ce que chacun retrouve d'une rampe.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LES DEUX RAMPES : la numérique, qui décale la même matière, et la
rendue, qui pousse la surface sur d'autres feuilles ; pour chacune, la part retrouvée par le pas à la couture et par le pas
de centre à centre, avec le seuil déclaré. En bas à gauche, les cartes du bloc : l'erreur jugée, et la marche de la spire
produite moins celle du segment, lue des deux façons. En bas à droite, l'accord des paires.

  uv run python src/figures/figure_le_pas_de_centre_a_centre_voit_il_la_rampe.py \\
      --sortie docs/images/258_le_pas_de_centre_a_centre_voit_il_la_rampe.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_pas_de_centre_a_centre_voit_il_la_rampe.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
VIDE = (228, 226, 220)
L_, H_ = 1360, 900
LA_PORTEE = 108.0


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


def la_couleur(v) -> tuple[int, int, int]:
    if v is None:
        return VIDE
    t = max(-1.0, min(1.0, float(v) / LA_PORTEE))
    loin = CONTRE if t < 0 else ALERTE
    a = abs(t)
    return tuple(int(round(255 * (1 - a) + c * a)) for c in loin)


def les_pentes(d: dict) -> list[tuple[str, str, float]]:
    n = d["la_rampe_numerique"]
    return [("la rampe numérique, 24 voxels", "à la couture", n["a_la_couture"]["la_pente"]),
            ("la rampe numérique, 24 voxels", "de centre à centre", n["de_centre_a_centre"]["la_pente"]),
            ("la rampe rendue, un pas", "à la couture", d["ce_que_la_marche_des_coutures_en_retrouvait"]["la_pente"]),
            ("la rampe rendue, un pas", "de centre à centre", d["ce_que_la_marche_retrouve_de_la_rampe"]["la_pente"])]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : le pas de centre à centre voit-il la rampe numérique, et la rendue ?"""
    n = d["la_rampe_numerique"]["de_centre_a_centre"]["la_pente"]
    r = d["ce_que_la_marche_retrouve_de_la_rampe"]["la_pente"]
    c = d["la_rampe_numerique"]["a_la_couture"]["la_pente"]
    if n >= 0.5 and r < 0.5:
        return (f"DE CENTRE À CENTRE, LE PAS RETROUVE {_fr(n, 4)} D'UNE DÉRIVE, CONTRE {_fr(c, 4)} À LA COUTURE ; D'UNE "
                f"RAMPE RENDUE, {_fr(r, 4)}")
    return f"DE CENTRE À CENTRE, LE PAS RETROUVE {_fr(n, 4)} DE LA RAMPE NUMÉRIQUE ET {_fr(r, 4)} DE LA RAMPE RENDUE"


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

    b = d["le_bloc"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"20230702185753 · le bloc de 257 : {b['le_cote']} × {b['le_cote']} chunks à la rangée "
                   f"{b['la_rangee']}, colonne {b['la_colonne']} · la pente de la marche moins celle du segment, contre "
                   f"l'écart posé", petit, GRIS)

    # ── PANNEAU 1 · LES DEUX RAMPES ────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 330, "CE QUE CHAQUE PAS RETROUVE D'UNE RAMPE : UN, TOUT ; ZÉRO, RIEN")
    bx0, bx1, P = 470, 1180, 1.4
    y = 124
    for k, (rampe, pas, pente) in enumerate(les_pentes(d)):
        if k % 2 == 0:
            ecrire(66, y, rampe, 0, ENCRE)
        ecrire(250, y, pas, 0, GRIS)
        w = (bx1 - bx0) * max(0.0, min(P, pente)) / P
        art.rectangle([bx0, y + 2, bx0 + w, y + 14], fill=BON if pas.startswith("de centre") else ALERTE)
        points.append((bx0 + w, y + 14))
        ecrire(bx0 + w + 8, y, _fr(pente, 4), 0, ENCRE)
        traces["barres"] += 1
        y += 26 if k % 2 == 0 else 46
    for val, lib in ((0.5, "le seuil déclaré"), (1.0, "tout")):
        x = bx0 + (bx1 - bx0) * val / P
        art.line([x, 118, x, y - 30], fill=GRIS, width=1)
        ecrire(x - 24, y - 26, lib, 0, GRIS)
    ecrire(66, 300, "la rampe numérique décale la même matière ; la rendue pousse la surface sur la feuille voisine, qui "
                    "a sa propre forme", 0, GRIS)

    # ── PANNEAU 2 · LES CARTES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 344, 1000, 640, "L'ERREUR JUGÉE, ET LA MARCHE DE LA SPIRE PRODUITE MOINS CELLE DU SEGMENT")
    cell = 9
    cartes = (("l'erreur du juge", "lerreur"), ("différence, à la couture", "la_difference_des_coutures"),
              ("différence, de centre à centre", "la_difference"), ("le segment, de centre à centre", "le_segment_reduit"))
    for k, (nom, cle) in enumerate(cartes):
        x0, y0 = 66 + k * 232, 400
        ecrire(x0, 378, nom, 0, ENCRE)
        grille = d["les_cartes"][cle]
        n_cell = 0
        for i, r in enumerate(grille):
            for j, v in enumerate(r):
                art.rectangle([x0 + j * cell, y0 + i * cell, x0 + (j + 1) * cell - 1, y0 + (i + 1) * cell - 1],
                              fill=la_couleur(v))
                n_cell += 1
        points.append((x0 + len(grille[0]) * cell, y0 + len(grille) * cell))
        traces["cellules"][cle] = n_cell
        traces["cartes"] += 1
    ecrire(66, 560, f"bleu et ocre : ±{_fr(LA_PORTEE, 0)} voxels ; blanc : zéro ; gris : non noté ou non relié", 0, GRIS)
    s = d["les_piles"]["le_segment_reduit"]
    sc = [x for r in d["les_cartes"]["le_segment_reduit_des_coutures"] for x in r if x is not None]
    ecrire(66, 580, f"la marche du segment, de centre à centre, s'étend sur {_fr(s['letendue_de_la_marche_voxels'], 1)} "
                    f"voxels ; à la couture, sur {_fr(max(sc) - min(sc), 1)}", 0, GRIS)
    c = d["la_difference_des_marches"]["contre_lerreur_jugee"]
    ecrire(66, 600, f"la différence, de centre à centre, suit l'erreur jugée avec une pente de {_fr(c['la_pente'], 4)} "
                    f"et une corrélation de {_fr(d['la_difference_des_marches']['laccord_des_paires']['la_correlation'], 4)}",
           0, GRIS)

    # ── PANNEAU 3 · LES PAIRES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(1020, 344, 1310, 640, "L'ACCORD DES PAIRES")
    lignes = (("le témoin plat", d["le_temoin_plat"]),
              ("à la couture", d["la_difference_des_marches_des_coutures"]["laccord_des_paires"]),
              ("de centre à centre", d["la_difference_des_marches"]["laccord_des_paires"]))
    y = 384
    for nom, a in lignes:
        ecrire(1036, y, nom, 0, ENCRE)
        for m, (lib, cle, coul) in enumerate((("sépare", "la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe", ALERTE),
                                              ("réunit", "la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit", BON))):
            val = a.get(cle)
            yy = y + 18 + m * 18
            ecrire(1046, yy, lib, 0, GRIS)
            if val is not None:
                art.rectangle([1100, yy + 2, 1100 + 150 * float(val), yy + 12], fill=coul)
                points.append((1100 + 150 * float(val), yy + 12))
                traces["barres"] += 1
            ecrire(1258, yy, _fr(val, 4), 0, ENCRE)
        y += 76

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 660, L_, H_], fill=BANDE)
    ecrire(50, 676, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 700, "★ lu de centre à centre, le treillis voit une dérive que la couture ne voit pas ; sur la spire produite, "
                    "il suit l'erreur jugée à un tiers.", moyen, ENCRE)
    ecrire(50, 726, "⚠ ce qui n'est PAS établi : la rampe numérique et la pente contre l'erreur ont été ajoutées après la "
                    "première mesure ;", moyen, ALERTE)
    ecrire(50, 748, "  un seul bloc, où le segment passe entre deux feuilles ; et la marche du segment de centre à centre "
                    "dérive, sans qu'on sache encore si c'est lui ou le pas.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.crop((0, 0, L_, 780)).save(sortie)
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
    tmp = sortie.parent / ".sonde_258.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", "DE CENTRE À CENTRE" in le_titre(d) and _fr(les_pentes(d)[1][2], 4) in le_titre(d))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans l'image", all(0 <= x <= L_ and 0 <= y <= 780 for x, y in points))
    cote = d["le_bloc"]["le_cote"]
    v("★★★★ chaque carte a une cellule par chunk du bloc",
      traces["cartes"] == 4 and all(n == cote * cote for n in traces["cellules"].values()), str(traces["cellules"]))
    v("★★★★ quatre pentes et six parts ont leur barre", traces["barres"] == 10, str(traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le témoin, le seuil déclaré et ce qui n'est PAS établi",
      "témoin plat" in txt and "seuil déclaré" in txt and "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "images" / "258_le_pas_de_centre_a_centre_voit_il_la_rampe.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
