"""Sur PHerc0358, la chaîne mixte, qui garde la spire quand le critère de 352 la tient et ne relance que sinon : saut par saut, ce qu'elle garde, spire ou nappe relancée, et si le critère le tient ; et, côté par côté, sa suite contre celle de la chaîne relancée de 354.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une rangée par côté, une case par saut : foncée si le critère tient la surface
gardée, claire sinon ; S si le saut a gardé sa spire, R s'il a relancé une nappe, avec les points de la surface gardée. À droite, les deux
suites côte à côte.

  uv run python src/figures/figure_une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.py \\
      --sortie docs/images/356_une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.png

⚠ Tout vient de la mesure de `356`.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
CLAIR = (226, 224, 219)
L_, H_ = 1360, 600
LA_BANDE = 510
CG, CL, CH = 200, 62, 44
LES_SAUTS = 8
LES_LETTRES = {"la spire": "S", "la relance": "R", None: "-"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    f_ = lambda x: f"{x:g}".replace(".", ",")  # noqa: E731
    return f"la chaîne mixte tient {f_(v['m'])} sauts à la suite en médiane, la chaîne relancée {f_(v['r'])}".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    s = [x for c in d["les_cotes"] for x in c["les_sauts"]]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : {sum(x['tenu'] for x in s)} des {len(s)} sauts de la chaîne mixte sont tenus ; "
            f"{sum(x['depuis'] == 'la spire' for x in s)} ont gardé leur spire, {sum(x['depuis'] == 'la relance' for x in s)} ont relancé")
    trois = "⚠ ce qui n'est PAS établi : si les surfaces qu'elle tient sont sur leur feuille ; c'est ce que Paris4 peut dire."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"cases": [], "lignes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "S : le saut garde sa spire, tenue par le critère de 352 ; R : il relance une nappe depuis elle ; en dessous, les points "
                   "de la surface gardée", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 790, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la chaîne mixte, saut par saut", moyen, ENCRE)
    for h in range(LES_SAUTS):
        ecrire(CG + h * (CL + 6) + 14, y0 + 40, f"saut {h + 1}", 0, GRIS)
    y = y0 + 62
    for c in d["les_cotes"]:
        ecrire(x0 + 12, y + 16, f"graine {c['le_rang']}, côté {c['le_cote']}", 0, ENCRE)
        for h, s in enumerate(c["les_sauts"]):
            cx = CG + h * (CL + 6)
            fond = BLEU if s["tenu"] else CLAIR
            art.rectangle([cx, y, cx + CL, y + CH], fill=fond)
            traces["rectangles"].append((0, cx, cx + CL, y, y + CH))
            couleur = FOND if s["tenu"] else ENCRE
            ecrire(cx + 6, y + 6, LES_LETTRES[s["depuis"]], 0, couleur)
            ecrire(cx + 6, y + 24, f"{s['les_points']} pts", 0, couleur)
            traces["cases"].append((c["le_rang"], c["le_cote"], h + 1, s["tenu"], LES_LETTRES[s["depuis"]], s["les_points"], fond))
        y += CH + 12
    art.rectangle([x0 + 12, y1 - 26, x0 + 24, y1 - 14], fill=BLEU)
    ecrire(x0 + 30, y1 - 28, "surface gardée tenue par le critère", 0, ENCRE)
    art.rectangle([x0 + 280, y1 - 26, x0 + 292, y1 - 14], fill=CLAIR)
    ecrire(x0 + 298, y1 - 28, "refusée", 0, ENCRE)
    traces["rectangles"] += [(0, x0 + 12, x0 + 24, y1 - 26, y1 - 14), (0, x0 + 280, x0 + 292, y1 - 26, y1 - 14)]

    x0, y0, x1, y1 = 820, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les sauts tenus à la suite", moyen, ENCRE)
    cols = (x0 + 12, x0 + 200, x0 + 320)
    for c_, t in zip(cols, ("côté", "chaîne mixte", "chaîne relancée")):
        ecrire(c_, y0 + 44, t, 0, GRIS)
    y = y0 + 68
    for c, r in zip(d["les_cotes"], d["les_suites_relancees"]):
        cel = (f"graine {c['le_rang']}, {c['le_cote']}", str(c["la_suite"]), str(r))
        for c_, t in zip(cols, cel):
            ecrire(c_, y, t, 0, ALERTE if c["la_suite"] > r else ENCRE)
        traces["lignes"].append(cel)
        y += 22
    m = statistics.median(c["la_suite"] for c in d["les_cotes"])
    r = statistics.median(d["les_suites_relancees"])
    cel = ("médiane", f"{m:g}".replace(".", ","), f"{r:g}".replace(".", ","))
    for c_, t in zip(cols, cel):
        ecrire(c_, y + 8, t, 0, ENCRE)
    traces["lignes"].append(cel)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 26, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_356.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update({"m": 2, "r": 1})
    v("★★★ le titre LIT la mesure", le_titre(autre) == "LA CHAÎNE MIXTE TIENT 2 SAUTS À LA SUITE EN MÉDIANE, LA CHAÎNE RELANCÉE 1", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_rang"], c["le_cote"], h, s["tenu"], {"la spire": "S", "la relance": "R"}.get(s["depuis"], "-"), s["les_points"])
               for c in d["les_cotes"] for h, s in enumerate(c["les_sauts"], 1)]
    v("★★★★ une case par saut, à sa tenue, à ce qu'il garde et à ses points", [x[:6] for x in traces["cases"]] == attendu)
    v("★★★★ une case est foncée si et seulement si le critère tient la surface gardée",
      all((x[6] == BLEU) == x[3] for x in traces["cases"]))
    v("★★★★ aucun côté n'a plus de sauts que la grille n'a de colonnes", all(len(c["les_sauts"]) <= LES_SAUTS for c in d["les_cotes"]))
    suites = [next((i for i, s in enumerate(c["les_sauts"]) if not s["tenu"]), len(c["les_sauts"])) for c in d["les_cotes"]]
    v("★★★★ la suite de chaque côté est recomptée sur ses cases", [int(x[1]) for x in traces["lignes"][:-1]] == suites == [c["la_suite"] for c in d["les_cotes"]])
    v("★★★★ la colonne relancée est celle que 354 publie, dans le même ordre de côtés",
      [int(x[2]) for x in traces["lignes"][:-1]] == d["les_suites_relancees"])
    v("★★★★ les médianes sont celles du verdict", not d["le_verdict"].get("decidable")
      or (float(traces["lignes"][-1][1].replace(",", ".")), float(traces["lignes"][-1][2].replace(",", "."))) == (d["le_verdict"]["m"], d["le_verdict"]["r"]))
    s = [x for c in d["les_cotes"] for x in c["les_sauts"]]
    v("★★★★ la bande rapporte à côté les sauts tenus et gardés, recomptés",
      f"{sum(x['tenu'] for x in s)} des {len(s)} sauts de la chaîne mixte sont tenus ; {sum(x['depuis'] == 'la spire' for x in s)} ont gardé"
      in " ".join(la_bande(d)))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "356_une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.png")
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
