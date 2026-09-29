"""La chaîne de m7 de 303 prolongée à seize sauts : saut par saut, tient-elle, et quelle part de ses points m7 appuie encore.

⚠⚠ **Ce que cette figure doit rendre évident.** Côté par côté, seize cases : vertes quand le saut tient (au cœur d'une feuille,
d'une surface de `m7` à la suivante), orange sinon ; dans chaque case, la part des points que `m7` appuie. Ce qui se voit d'un coup :
jusqu'où les côtés tiennent, et que ce qui tient loin est de moins en moins lu dans `m7`.

  uv run python src/figures/figure_la_chaine_tient_elle_au_dela_de_quatre_sauts.py \\
      --sortie docs/images/315_la_chaine_tient_elle_au_dela_de_quatre_sauts.png

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
LA_MESURE = RACINE / "docs" / "mesures" / "la_chaine_tient_elle_au_dela_de_quatre_sauts.json"
sys.path.insert(0, str(RACINE / "src" / "nappe"))

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
VERT = (214, 232, 221)
ORANGE = (244, 222, 205)
L_, H_ = 1360, 640
LA_BANDE = 540


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return v["lissue"].upper()


def les_parts_au_dernier_saut(d: dict) -> tuple[int, int]:
    """La plus petite et la plus grande part appuyée, en %, au dernier saut des côtés qui tiennent jusqu'au bout."""
    xs = [round(100 * c["les_sauts"][-1]["la_part_appuyee"]) for c in d["les_cotes"]
          if c["le_dernier_saut_qui_tient"] == d["les_constantes"]["les_sauts"]]
    return (min(xs), max(xs)) if xs else (0, 0)


def dessiner(d: dict, sortie: Path):
    from la_chaine_tient_elle_au_dela_de_quatre_sauts import tient

    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": []}
    quart = d["les_constantes"]["le_quart_de_pas_voxels"]

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "case verte : le saut tient (au plus dense à 5 voxels près, d'une surface de m7 à la suivante) ; orange : non ; "
                   "chiffre : la part des points de la spire appuyée sur m7, en %", petit, GRIS)
    x0, y0, x1, y1 = 50, 72, 1310, 526
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    cx0 = x0 + 170
    lw = (x1 - cx0 - 10) / d["les_constantes"]["les_sauts"]
    for h in range(d["les_constantes"]["les_sauts"]):
        ecrire(int(cx0 + h * lw + lw / 2 - 6), y0 + 8, str(h + 1), 0, GRIS)
    rh = (y1 - y0 - 34) / max(1, len(d["les_cotes"]))
    for r, c in enumerate(d["les_cotes"]):
        y = y0 + 28 + r * rh
        ecrire(x0 + 10, int(y + rh / 2 - 7), f"graine {c['le_rang']}, {c['le_cote']} : {c['le_dernier_saut_qui_tient']}", 0, ENCRE)
        for h, s in enumerate(c["les_sauts"]):
            xa = cx0 + h * lw
            ok = tient(s, quart)
            art.rectangle([xa + 2, y + 3, xa + lw - 3, y + rh - 3], fill=VERT if ok else ORANGE)
            ecrire(int(xa + 8), int(y + rh / 2 - 7), f"{round(100 * s['la_part_appuyee'])}", 0, ENCRE)
            traces["cases"].append((c["le_rang"], c["le_cote"], s["le_saut"], ok))

    lo, hi = les_parts_au_dernier_saut(d)
    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    ecrire(50, LA_BANDE + 12, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, LA_BANDE + 36, "⚠ ce qui n'est PAS établi : que les spires soient consécutives, ni que ce qui tient loin soit lu dans m7 : "
                              f"au dernier saut des côtés qui tiennent, m7 n'en appuie plus que {lo} à {hi} %.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
    from la_chaine_tient_elle_au_dela_de_quatre_sauts import tient

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
    tmp = sortie.parent / ".sonde_315.png"
    _, poses, cadres, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "la chaîne tient"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA CHAÎNE TIENT", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    q = d["les_constantes"]["le_quart_de_pas_voxels"]
    v("★★★ une case par saut, à la couleur de sa mesure", traces["cases"] == [
        (c["le_rang"], c["le_cote"], s["le_saut"], tient(s, q)) for c in d["les_cotes"] for s in c["les_sauts"]])
    txt = " ".join(t for _, _, t, _ in poses)
    lo, hi = les_parts_au_dernier_saut(d)
    v("★★★ la mise en garde porte les parts appuyées mesurées au dernier saut des côtés qui tiennent",
      f"plus que {lo} à {hi} %" in txt and lo > 0, f"{lo} {hi}")
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
                   / "315_la_chaine_tient_elle_au_dela_de_quatre_sauts.png")
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
