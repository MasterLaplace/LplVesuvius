"""Sur PHerc0358, saut par saut et côté par côté, ce que le compte de 345 et le seuil de 50 points à zéro disent de la chaîne relancée : tenu, tenu par 345 seul, ou refusé, avec la part d'une feuille et les points à zéro ; et la suite que tient 328 à côté.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une rangée par côté suivi, une case par saut : foncée si le critère le tient,
claire s'il est refusé, ambre si `345` le tient mais que le seuil le refuse ; dans chaque case, la part d'une feuille et les points à zéro.
À droite, pour chaque côté, la suite que tient le critère et celle que tient `328`.

  uv run python src/figures/figure_le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.py \\
      --sortie docs/images/354_le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.png

⚠ Tout vient de la mesure de `354`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
CLAIR = (226, 224, 219)
AMBRE = (214, 170, 110)
L_, H_ = 1360, 600
LA_BANDE = 510
CG, CL, CH = 200, 58, 44
LES_SAUTS = 8


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_genre(s: dict) -> str:
    return "tenu" if s["tient"] else "345 seul" if s["tient_345"] else "refusé"


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"sur PHerc0358, le critère tient le premier saut de {v['k']} des {v['n']} côtés, et jamais le suivant".upper() \
        if all(c["la_suite"] <= 1 for c in d["les_cotes"]) else \
        f"sur PHerc0358, le critère tient le premier saut de {v['k']} des {v['n']} côtés".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    cotes = d["les_cotes"]
    tous = [s for c in cotes for s in c["les_sauts"] if s["a_une_surface"]]
    moitie = sum(1 for s in tous if s["les_feuilles"]["les_mesures"] and s["les_zeros"] * 2 >= s["les_feuilles"]["les_mesures"])
    t328 = sum(1 for s in tous if s["tient_328"])
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : {t328} des {len(tous)} sauts qui ont une surface sont tenus par 328 ; sous {moitie} "
            f"d'entre eux, la moitié au moins des points comptés ne franchissent aucune feuille")
    trois = "⚠ ce qui n'est PAS établi : si les surfaces tenues sur PHerc0358 sont sur leur feuille ; les 92 % de Paris4 sont un étalon."
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
    ecrire(50, 46, "un saut tient si 345 le tient et s'il a moins de 50 points à zéro ; dans chaque case : la part d'une feuille, et z, les points à zéro",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 790, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les sauts de chaque côté suivi", moyen, ENCRE)
    for h in range(LES_SAUTS):
        ecrire(CG + h * (CL + 6) + 16, y0 + 40, f"saut {h + 1}", 0, GRIS)
    couleurs = {"tenu": BLEU, "345 seul": AMBRE, "refusé": CLAIR}
    y = y0 + 62
    for c in d["les_cotes"]:
        ecrire(x0 + 12, y + 18, f"graine {c['le_rang']}, côté {c['le_cote']}", 0, ENCRE)
        for h, s in enumerate(c["les_sauts"]):
            cx = CG + h * (CL + 6)
            g = le_genre(s)
            art.rectangle([cx, y, cx + CL, y + CH], fill=couleurs[g])
            traces["rectangles"].append((0, cx, cx + CL, y, y + CH))
            texte_couleur = FOND if g == "tenu" else ENCRE
            p = s["les_feuilles"]["la_part_dune_feuille"]
            ecrire(cx + 6, y + 8, "-" if p is None else f"{round(100 * p)} %", 0, texte_couleur)
            ecrire(cx + 6, y + 24, f"z = {s['les_zeros']}", 0, texte_couleur)
            traces["cases"].append((c["le_rang"], c["le_cote"], h + 1, g))
        y += CH + 12
    lx = x0 + 12
    for nom in ("tenu", "345 seul", "refusé"):
        art.rectangle([lx, y1 - 26, lx + 12, y1 - 14], fill=couleurs[nom])
        traces["rectangles"].append((0, lx, lx + 12, y1 - 26, y1 - 14))
        libelle = {"tenu": "tenu par le critère", "345 seul": "tenu par 345, refusé par le seuil", "refusé": "refusé par 345"}[nom]
        ecrire(lx + 18, y1 - 28, libelle, 0, ENCRE)
        lx += 18 + int(art.textlength(libelle, font=petit)) + 24

    x0, y0, x1, y1 = 820, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les sauts tenus à la suite", moyen, ENCRE)
    cols = (x0 + 12, x0 + 190, x0 + 300)
    for c_, t in zip(cols, ("côté", "le critère", "328")):
        ecrire(c_, y0 + 44, t, 0, GRIS)
    y = y0 + 68
    for c in d["les_cotes"]:
        cel = (f"graine {c['le_rang']}, {c['le_cote']}", str(c["la_suite"]), str(c["la_suite_de_328"]))
        for c_, t in zip(cols, cel):
            ecrire(c_, y, t, 0, ALERTE if c["la_suite"] >= 1 else ENCRE)
        traces["lignes"].append(cel)
        y += 22
    ecrire(x0 + 12, y + 20, "328 : le saut pose au pas et sa nappe", 0, GRIS)
    ecrire(x0 + 12, y + 36, "n'est pas dans un bloc de m7", 0, GRIS)

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
    tmp = sortie.parent / ".sonde_354.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update({"k": 3, "n": 7})
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("SUR PHERC0358, LE CRITÈRE TIENT LE PREMIER SAUT DE 3 DES 7 CÔTÉS"),
      le_titre(autre))
    autre["les_cotes"][0]["la_suite"] = 2
    v("★★★ le titre ne dit « jamais le suivant » que si aucune suite ne dépasse un saut", "JAMAIS" not in le_titre(autre)
      and ("JAMAIS" in le_titre(d)) == all(c["la_suite"] <= 1 for c in d["les_cotes"]))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_rang"], c["le_cote"], h, "tenu" if s["tient"] else "345 seul" if s["tient_345"] else "refusé")
               for c in d["les_cotes"] for h, s in enumerate(c["les_sauts"], 1)]
    v("★★★★ une case par saut, de la couleur que disent le critère et 345", traces["cases"] == attendu, str(traces["cases"][:3]))
    v("★★★★ aucun côté n'a plus de sauts que la grille n'a de colonnes", all(len(c["les_sauts"]) <= LES_SAUTS for c in d["les_cotes"]))
    premiers = sum(1 for c in d["les_cotes"] if c["les_sauts"] and c["les_sauts"][0]["tient"])
    v("★★★★ les premières cases tenues sont autant que les côtés du verdict", not d["le_verdict"].get("decidable")
      or premiers == d["le_verdict"]["k"], str(premiers))
    v("★★★★ la suite de chaque côté est recomptée sur ses cases",
      all(int(cel[1]) == next((i for i, s in enumerate(c["les_sauts"]) if not s["tient"]), len(c["les_sauts"]))
          for cel, c in zip(traces["lignes"], d["les_cotes"])) and len(traces["lignes"]) == len(d["les_cotes"]))
    tous = [s for c in d["les_cotes"] for s in c["les_sauts"] if s["a_une_surface"]]
    v("★★★★ la bande rapporte à côté les sauts de 328 et les sauts à moitié à zéro, recomptés",
      f"{sum(s['tient_328'] for s in tous)} des {len(tous)} sauts qui ont une surface sont tenus par 328 ; sous "
      f"{sum(1 for s in tous if s['les_feuilles']['les_mesures'] and 2 * s['les_zeros'] >= s['les_feuilles']['les_mesures'])} d'entre eux"
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
                   / "354_le_compte_et_le_seuil_tiennent_ils_une_premiere_surface_sur_pherc0358.png")
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
