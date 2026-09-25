"""La spire produite corrigée par la seule marche de fenêtre en fenêtre : avant, après, et ce que le juge en dit.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LE SIGNE DE LA CORRECTION, fixé par la rampe rendue de `257` et non
par le juge : de fenêtre en fenêtre, la marche en retrouve presque tout. Au milieu, sur chaque bloc, l'erreur jugée et la
différence des marches, avant et après la correction. En bas, la part des points sur la bonne spire avant et après, les
ratés trouvés et les justes accusés.

  uv run python src/figures/figure_la_marche_corrige_t_elle_la_spire_produite.py \\
      --sortie docs/images/261_la_marche_corrige_t_elle_la_spire_produite.png
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
LA_MESURE = M / "la_marche_corrige_t_elle_la_spire_produite.json"
DE_257 = M / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
DE_258 = M / "le_pas_de_centre_a_centre_voit_il_la_rampe.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE = (150, 185, 170)
CONTRE = (92, 108, 150)
VIDE = (228, 226, 220)
L_, H_ = 1360, 960
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
    if not d.get("decidable") or not d.get("les_blocs"):
        raise SystemExit("mesure indécidable")
    d["_257"], d["_258"] = json.loads(DE_257.read_text()), json.loads(DE_258.read_text())
    return d


def la_couleur(v) -> tuple[int, int, int]:
    if v is None:
        return VIDE
    t = max(-1.0, min(1.0, float(v) / LA_PORTEE))
    loin = CONTRE if t < 0 else ALERTE
    a = abs(t)
    return tuple(int(round(255 * (1 - a) + c * a)) for c in loin)


def les_parts(d: dict) -> list[tuple[str, float, float]]:
    return [("257" if n.endswith("257") else "259", b["avant"]["la_part_sur_la_bonne_spire"],
             b["apres"]["la_part_sur_la_bonne_spire"]) for n, b in d["les_blocs"].items()]


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : la correction sans le juge relève-t-elle la part juste sur les deux blocs ?"""
    p = les_parts(d)
    if all(ap > av for _, av, ap in p):
        return ("SANS LE JUGE, LA MARCHE CORRIGE LA SPIRE PRODUITE : " +
                " ET ".join(f"DE {_fr(av, 4)} À {_fr(ap, 4)}" for _, av, ap in p) + " DES POINTS SUR LA BONNE SPIRE")
    return "SANS LE JUGE, LA MARCHE NE RELÈVE PAS PARTOUT LA PART DES POINTS SUR LA BONNE SPIRE"


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
    ecrire(50, 52, "20230702185753 · m7, côté plus · signalé : à un demi-feuillet ou plus de la médiane du bloc · ramené de "
                   "cet écart · le juge ne sert qu'à juger", petit, GRIS)

    # ── PANNEAU 1 · LE SIGNE ───────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 230, "LE SIGNE DE LA CORRECTION : CE QUE CHAQUE MARCHE RETROUVE DE LA RAMPE RENDUE D'UN PAS")
    ramp = (("à la couture", d["_257"]["ce_que_la_marche_retrouve_de_la_rampe"]["la_pente"], ALERTE),
            ("de centre à centre", d["_258"]["ce_que_la_marche_retrouve_de_la_rampe"]["la_pente"], PALE),
            ("de fenêtre en fenêtre", d["le_signe"]["la_pente"], BON))
    bx0, bx1, P = 330, 1150, 1.2
    for k, (nom, val, coul) in enumerate(ramp):
        y = 118 + k * 24
        ecrire(66, y, nom, 0, ENCRE)
        w = (bx1 - bx0) * max(0.0, min(P, val)) / P
        art.rectangle([bx0, y + 2, bx0 + w, y + 14], fill=coul)
        points.append((bx0 + w, y + 14))
        ecrire(bx0 + w + 8, y, _fr(val, 4), 0, ENCRE)
        traces["barres"] += 1
    x1 = bx0 + (bx1 - bx0) / P
    art.line([x1, 112, x1, 190], fill=GRIS, width=1)
    ecrire(x1 - 10, 196, "tout", 0, GRIS)

    # ── PANNEAU 2 · LES CARTES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 246, 1310, 520, "L'ERREUR JUGÉE ET LA DIFFÉRENCE DES MARCHES, AVANT ET APRÈS LA CORRECTION, CHUNK PAR CHUNK")
    cell = 8
    k = 0
    for n, b in d["les_blocs"].items():
        lib = "257" if n.endswith("257") else "259"
        for titre, cle in ((f"{lib} : l'erreur, avant", "lerreur_avant"), (f"{lib} : la marche, avant", "la_difference_avant"),
                           (f"{lib} : l'erreur, après", "lerreur_apres"), (f"{lib} : la marche, après", "la_difference_apres")):
            x0, y0 = 66 + k * 155, 300
            ecrire(x0, 278, titre, 0, ENCRE)
            grille = b["les_cartes"][cle]
            nn = 0
            for i, r in enumerate(grille):
                for j, v in enumerate(r):
                    art.rectangle([x0 + j * cell, y0 + i * cell, x0 + (j + 1) * cell - 1, y0 + (i + 1) * cell - 1],
                                  fill=la_couleur(v))
                    nn += 1
            points.append((x0 + len(grille[0]) * cell, y0 + len(grille) * cell))
            traces["cellules"][f"{lib}_{cle}"] = nn
            traces["cartes"] += 1
            k += 1
    ecrire(66, 446, f"bleu et ocre : ±{_fr(LA_PORTEE, 0)} voxels ; blanc : zéro ; gris : non noté ou non relié. La marche est "
                    f"celle de la spire moins celle du segment, à une constante près.", 0, GRIS)
    y = 468
    for n, b in d["les_blocs"].items():
        lib = "257" if n.endswith("257") else "259"
        r = b["relue"]
        ecrire(66, y, f"bloc {lib} : l'écart type de la différence des marches passe de {_fr(r['lecart_type_de_la_difference_avant'], 2)} "
                      f"à {_fr(r['lecart_type_de_la_difference_apres'], 2)} voxels ; ancre {_fr(b['lancre_voxels'], 2)}", 0, GRIS)
        y += 20

    # ── PANNEAU 3 · AVANT, APRÈS ───────────────────────────────────────────────────────────────────────────────────
    panneau(50, 536, 1310, 840, "CE QUE LE JUGE EN DIT : LA PART SUR LA BONNE SPIRE, ET CE QUE LE SIGNALEMENT A TOUCHÉ")
    for col, (n, b) in enumerate(d["les_blocs"].items()):
        lib = "257" if n.endswith("257") else "259"
        x0 = 66 + col * 630
        ecrire(x0, 570, f"le bloc de {lib} : {b['avant']['les_points_notes']} points notés, {b['les_points_signales']} "
                        f"signalés", 0, ENCRE)
        s = b["le_signalement"]
        lignes = (("sur la bonne spire, avant", b["avant"]["la_part_sur_la_bonne_spire"], PALE),
                  ("sur la bonne spire, après", b["apres"]["la_part_sur_la_bonne_spire"], BON),
                  ("des ratés, signalés", s["la_part_des_rates_signales"], BON),
                  ("des justes, signalés", s["la_part_des_justes_signales"], ALERTE))
        for m, (nom, val, coul) in enumerate(lignes):
            yy = 598 + m * 30
            ecrire(x0, yy, nom, 0, GRIS)
            art.rectangle([x0 + 180, yy + 2, x0 + 180 + 330 * float(val), yy + 14], fill=coul)
            points.append((x0 + 180 + 330 * float(val), yy + 14))
            ecrire(x0 + 520, yy, _fr(val, 4), 0, ENCRE)
            traces["barres"] += 1
        ecrire(x0, 730, f"{b['les_rates_rendus_justes']} ratés rendus justes, {b['les_justes_rendus_rates']} justes rendus "
                        f"ratés", 0, ENCRE)
        ecrire(x0, 752, f"{s['les_rates']} ratés et {s['les_justes']} justes notés dans le bloc", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 856, L_, H_], fill=BANDE)
    ecrire(50, 868, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 890, "★ le scan seul, rendu le long de la spire produite et du segment, désigne où la chaîne a glissé et l'y "
                    "ramène.", moyen, ENCRE)
    ecrire(50, 914, "⚠ ce qui n'est PAS établi : deux blocs, cent cinquante points chacun ; une passe ; l'ancre suppose que la "
                    "majorité est juste ; une boucle.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_261.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure", ("LA MARCHE CORRIGE" in le_titre(d)) == all(ap > av for _, av, ap in les_parts(d)))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ huit cartes, une cellule par chunk", traces["cartes"] == 8 and all(n == 256 for n in traces["cellules"].values()),
      str(traces["cellules"]))
    v("★★★★ trois pentes et huit parts ont leur barre", traces["barres"] == 11, str(traces["barres"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi, et que le juge ne sert qu'à juger",
      "n'est PAS établi" in txt and "ne sert qu'à juger" in txt)
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
                   default=RACINE / "docs" / "images" / "261_la_marche_corrige_t_elle_la_spire_produite.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
