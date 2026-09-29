"""Côté intérieur, surface par surface, le tour publié que la chaîne qui croît de PHercParis4 retrouve, de 5753_0 à 5753_-7, avec la part du plan que chaque spire pose.

⚠⚠ **Ce que cette figure doit rendre évident.** Chaque ligne est une graine, chaque colonne une surface de la chaîne côté moins, la nappe
puis huit sauts. La case porte le ou les tours publiés que la surface retrouve (« — » si aucun) et, dessous, la part du plan posée ; elle
est verte quand la surface retrouve le tour que la descente attend. À droite, le nombre de tours descendus et ce qui arrête la descente.
Si les diagonales vertes descendent de 0 à −6, la chaîne tirée de `m7` traverse six tours publiés d'affilée.

  uv run python src/figures/figure_jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.py \\
      --sortie docs/images/330_jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
PALE_BON = (214, 232, 222)
L_, H_ = 1360, 620
LA_BANDE = 530
LES_COLONNES = 9


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].split(" ; ")[0].upper()


def les_cases(g: dict) -> list:
    """Pour chaque surface côté moins : les tours retrouvés, la part posée (None pour la nappe), et si c'est le tour attendu."""
    c = g["les_cotes"]["moins"]
    surfaces = [(g["la_nappe"], None)] + [(sp["les_tours"], sp["la_part_du_plan"]) for sp in c["les_spires"]]
    out, attendu, en_route, restant = [], None, False, c["la_descente"]
    for lect, part in surfaces:
        r = sorted((int(t) for t, x in lect.items() if x["la_lecture"] == "retrouve"), reverse=True)
        juste = False
        if not en_route and c["le_tour_de_depart"] is not None and len(r) == 1 and r[0] == c["le_tour_de_depart"] and attendu is None:
            juste, en_route, attendu = True, True, r[0] - 1
        elif en_route and restant > 0 and attendu in r:
            juste, restant, attendu = True, restant - 1, attendu - 1
        elif en_route:
            en_route = False
        out.append((tuple(r), part, juste))
    return out


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": [], "descentes": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "côté moins : le ou les tours publiés que chaque surface retrouve (« — » : aucun) et la part du plan posée ; vert : le "
                   "tour que la descente attend", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 1310, 510
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    cx0, cw, rh = x0 + 60, 112, 50
    for j in range(LES_COLONNES):
        ecrire(int(cx0 + j * cw + 8), y0 + 10, "la nappe" if j == 0 else f"saut {j}", 0, GRIS)
    ecrire(x1 - 190, y0 + 10, "descente, et ce qui l'arrête", 0, GRIS)
    for n, g in enumerate(d["les_graines"]):
        yy = y0 + 32 + n * rh
        ecrire(x0 + 12, yy + 16, f"g{g['le_rang']}", 0, ENCRE)
        for j, (r, part, juste) in enumerate(les_cases(g)[:LES_COLONNES]):
            bx = cx0 + j * cw
            art.rectangle([bx, yy, bx + cw - 8, yy + rh - 6], fill=PALE_BON if juste else FOND, outline=TRAIT)
            texte = "/".join(f"{t}".replace("-", "−") for t in r) if r else "—"
            ecrire(int(bx + 8), yy + 5, texte, 0, BON if juste else ENCRE)
            if part is not None:
                ecrire(int(bx + 8), yy + 23, f"{part * 100:.1f} %".replace(".", ","), 0, GRIS)
            traces["cases"].append((g["le_rang"], j, r, juste))
        c = g["les_cotes"]["moins"]
        ecrire(x1 - 190, yy + 5, str(c["la_descente"]), moyen, BON if c["la_descente"] >= 4 else ALERTE)
        ecrire(x1 - 165, yy + 7, c["larret"], 0, GRIS)
        traces["descentes"].append((g["le_rang"], c["la_descente"], sum(1 for x in les_cases(g) if x[2]) - 1))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : ce que valent les tours 5753_k comme vérité ; ni la chaîne au-delà de 5753_-7.",
           moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_330.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x 2 ; y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "X 2", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ les cases vertes de chaque graine sont sa descente, plus son départ",
      all(dsc == verts for _, dsc, verts in traces["descentes"]), str(traces["descentes"]))
    v("★★★ autant de colonnes que la plus longue chaîne a de surfaces",
      LES_COLONNES == 1 + max(len(g["les_cotes"]["moins"]["les_spires"]) for g in d["les_graines"]))
    v("★★★ une case par surface, jusqu'à la neuvième", len(traces["cases"]) == sum(min(LES_COLONNES, 1 + len(g["les_cotes"]["moins"]["les_spires"]))
                                                                       for g in d["les_graines"]))
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
                   / "330_jusqua_quel_tour_publie_la_chaine_qui_croit_descend_elle.png")
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
