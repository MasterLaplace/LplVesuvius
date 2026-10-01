"""Sur PHerc0358 : côté par côté, la part des sauts lus des trois chaînes qui sont à cheval, la graine 8 contre les graines 6 et 7.

⚠⚠ **Ce que cette figure doit rendre évident.** Une barre par côté, à la part de ses sauts lus qui sont à cheval : les graines 6 et 7 en
bleu, la graine 8 en orange ; au-dessus de chaque barre, le nombre de sauts à cheval sur le nombre de sauts lus ; en trait gris, la part
des graines 6 et 7 réunies.

  uv run python src/figures/figure_les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.py \\
      --sortie docs/images/378_les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.png

⚠ Tout vient de la mesure de `378`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 560
LA_BANDE = 440
HAUT, BAS = 120, 350
LARGEUR = 80
X0, PAS_X = 200, 150


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_cotes(d: dict) -> list[tuple[int, str, int, int]]:
    """Chaque côté, le nombre de ses sauts lus qui sont à cheval et le nombre de ses sauts lus, dans l'ordre de la mesure."""
    out = []
    for c in d["les_cotes"]:
        lus = [s for v in c["les_chaines"].values() for s in v if s["a_cheval"] is not None]
        out.append((c["le_rang"], c["le_cote"], sum(s["a_cheval"] for s in lus), len(lus)))
    return out


def en_y(p: float) -> int:
    return BAS - round(p * (BAS - HAUT))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].partition(" et ")[0].upper()
    return f"les sauts de la graine 8 à cheval plus souvent : {v['lissue'].rpartition(' ; ')[2]}".upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    six = next((a, n) for r, c, a, n in les_cotes(d) if (r, c) == (6, "moins"))
    deux = (f"rapporté à côté, qui ne décide rien : la graine 6, côté moins, où les trois chaînes tiennent leurs comptes corrigés, a "
            f"{six[0]} de ses {six[1]} sauts lus à cheval")
    trois = "⚠ ce qui n'est PAS établi : ce qui fait s'écarter les comptes de la graine 8, ni si les sauts à cheval y sont les mêmes qu'ailleurs."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 410)]
    traces = {"barres": [], "seuils": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "part des sauts lus des trois chaînes dont un quart au moins des points s'éloignent de plus d'un demi-pas de l'écart médian",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([140, BAS, 980, BAS], fill=GRIS)
    for k in range(0, 11, 2):
        y = en_y(k / 10.0)
        art.line([136, y, 140, y], fill=GRIS)
        ecrire(90, y - 7, f"{10 * k} %", petit, GRIS)
    for i, (rang, cote, a, n) in enumerate(les_cotes(d)):
        xa = X0 + i * PAS_X
        couleur = ORANGE if rang == 8 else BLEU
        p = a / n if n else 0.0
        y = en_y(p)
        art.rectangle([xa, y, xa + LARGEUR, BAS], fill=couleur)
        traces["barres"].append((rang, cote, a, n, y, couleur))
        ecrire(xa + 18, y - 18, f"{a} / {n}", petit, ENCRE)
        ecrire(xa + 2, BAS + 10, f"graine {rang}, {cote}", petit, ENCRE)
    t = d["le_bilan"]["les_temoins"]
    pt = t["a_cheval"] / t["lus"]
    yt = en_y(pt)
    for x in range(140, 960, 10):
        art.line([x, yt, x + 5, yt], fill=GRIS)
    traces["seuils"].append(("les témoins", pt, yt))
    ecrire(890, yt - 18, "graines 6 et 7 réunies", petit, GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 54, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_378.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; oui"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LES SAUTS DE LA GRAINE 8 À CHEVAL PLUS SOUVENT : OUI", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : 9 sauts lus sur la graine 8 et 70 sur les graines 6 et 7"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : 9 SAUTS LUS SUR LA GRAINE 8", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendus = []
    for c in d["les_cotes"]:
        xs = [s["a_cheval"] for v_ in c["les_chaines"].values() for s in v_ if s["a_cheval"] is not None]
        attendus.append((c["le_rang"], c["le_cote"], sum(xs), len(xs)))
    v("★★★★ une barre par côté, ses sauts à cheval et ses sauts lus recomptés sur la mesure, dans son ordre",
      [(r, c, a, n) for r, c, a, n, _, _ in traces["barres"]] == attendus and len(attendus) == 5, str(traces["barres"]))
    v("★★★★ les sauts lus de la graine 8 et des témoins égaux au bilan",
      sum(n for r, _, _, n in attendus if r == 8) == d["le_bilan"]["la_graine_8"]["lus"]
      and sum(a for r, _, a, _ in attendus if r == 8) == d["le_bilan"]["la_graine_8"]["a_cheval"]
      and sum(n for r, _, _, n in attendus if r != 8) == d["le_bilan"]["les_temoins"]["lus"])
    v("★★★★ la graine 8 en orange, les graines 6 et 7 en bleu",
      all(f == ((214, 150, 76) if r == 8 else (58, 88, 120)) for r, _, _, _, _, f in traces["barres"]))
    v("★★★★ chaque barre à sa part, de 0 à 100 %",
      all(y == BAS - round(a / n * (BAS - HAUT)) for _, _, a, n, y, _ in traces["barres"]))
    t = d["le_bilan"]["les_temoins"]
    v("★★★★ la part des graines 6 et 7 réunies tracée à sa valeur, recomptée sur les côtés",
      traces["seuils"] == [("les témoins", t["a_cheval"] / t["lus"], en_y(t["a_cheval"] / t["lus"]))]
      and t["a_cheval"] == sum(a for r, _, a, _ in attendus if r != 8), str(traces["seuils"]))
    six = [(a, n) for r, c, a, n in attendus if (r, c) == (6, "moins")][0]
    v("★★★★ la bande rapporte la graine 6, côté moins, recomptée", f"a {six[0]} de ses {six[1]} sauts lus à cheval" in la_bande(d)[1])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    dessiner(d, tmp)
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
                   / "378_les_sauts_de_la_graine_8_sont_ils_a_cheval_plus_souvent.png")
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
