"""Sur la graine 6, côté moins, de PHerc0358 : chaque surface des chaînes rognées, selon qu'elle est sur une feuille des chaînes de 389, avec le même compte ou un autre.

⚠⚠ **Ce que cette figure doit rendre évident.** Une rangée par chaîne, une case par saut : bleue si la surface rognée est sur une feuille de
`389` au même compte, orange si elle y est à un autre compte, rouille si elle est hors de ses feuilles, grise si aucune paire ne la compare.
Dans la case, le compte rogné ; sous la case, les comptes de `389` de sa feuille. Si les cases sont orange et non rouille, le rognage a
changé les comptes, pas les feuilles.

  uv run python src/figures/figure_le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.py \\
      --sortie docs/images/398_le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.png

⚠ Tout vient de la mesure de `398`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
CLAIR = (210, 212, 216)
BLANC = (255, 255, 255)
LES_COULEURS = {"meme_feuille_meme_compte": BLEU, "meme_feuille_autre_compte": ORANGE, "hors_des_feuilles": ALERTE, None: CLAIR}
LES_NOMS = (("meme_feuille_meme_compte", "même feuille, même compte"), ("meme_feuille_autre_compte", "même feuille, autre compte"),
            ("hors_des_feuilles", "hors des feuilles de 389"), (None, "sans paire"))
L_, H_ = 1200, 600
LA_BANDE = 480
X0, COTE, PAS = 210, 44, 56
LES_RANGEES = (("suivie", 130), ("compagne", 230), ("tierce", 330))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    v = d["sur_les_validees_de_389"]
    meme = sum(1 for s in v if any(c == s["le_compte_de_389"] for _, c in s["les_rognees"]))
    autre = sum(1 for s in v if s["les_rognees"] and not any(c == s["le_compte_de_389"] for _, c in s["les_rognees"]))
    deux = (f"rapporté à côté, qui ne décide rien : des {len(v)} surfaces que 389 validait, {meme} ont une surface rognée sur leur feuille au "
            f"même compte, {autre} à un autre compte, {len(v) - meme - autre} aucune")
    trois = "⚠ ce qui n'est PAS établi : lequel des deux comptes est juste ; PHerc0358 n'a pas de tours publiés."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 460)]
    traces = {"cases": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"le rognage et les feuilles de la graine 6, côté moins : {le_titre(d)}", gros, ENCRE)
    ecrire(50, 46, "une case par surface rognée : dedans, son compte ; dessous, les comptes de 389 sur sa feuille", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    for h in range(1, 17):
        ecrire(X0 + (h - 1) * PAS + 14, 96, str(h), petit, GRIS)
    for x, y in LES_RANGEES:
        ecrire(70, y + 14, x, moyen, ENCRE)
        for s in d["les_classes"][x]:
            g = X0 + (s["le_saut"] - 1) * PAS
            couleur = LES_COULEURS[s["la_classe"]]
            art.rectangle([g, y, g + COTE, y + COTE], fill=couleur)
            texte = "–" if s["le_compte"] is None else str(s["le_compte"])
            ecrire(g + 14, y + 15, texte, moyen, BLANC if s["la_classe"] is not None else ENCRE)
            dessous = ",".join(str(c) for c in s["les_comptes_de_389"]) or "–"
            ecrire(g + 4, y + COTE + 4, dessous, petit, GRIS)
            traces["cases"].append((x, s["le_saut"], s["la_classe"], couleur, texte, dessous))
    gx = 70
    for cle, nom in LES_NOMS:
        art.rectangle([gx, 420, gx + 14, 434], fill=LES_COULEURS[cle])
        ecrire(gx + 20, 420, nom, petit, ENCRE)
        gx += 250

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_398.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; non, y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "NON, Y", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = {"meme_feuille_meme_compte": BLEU, "meme_feuille_autre_compte": ORANGE, "hors_des_feuilles": ALERTE, None: CLAIR}
    v("★★★★ une case par surface rognée, à la couleur de sa classe",
      [(x, h, c) for x, h, c, *_ in traces["cases"]] == [(x, s["le_saut"], s["la_classe"]) for x, _ in LES_RANGEES for s in d["les_classes"][x]]
      and all(f == attendu[c] for _, _, c, f, *_ in traces["cases"]))
    v("★★★★ dans la case, le compte rogné ; dessous, les comptes de 389", all(
        t == str(s["le_compte"]) and dd == (",".join(str(c) for c in s["les_comptes_de_389"]) or "–")
        for (x, h, _, _, t, dd) in traces["cases"] for s in d["les_classes"][x] if s["le_saut"] == h))
    b = d["le_bilan"]
    v("★★★★ les cases comptent le bilan", sum(1 for c in traces["cases"] if c[2] is not None) == b["comparees"]
      and sum(1 for c in traces["cases"] if c[2] == "meme_feuille_autre_compte") == b["autre_compte"]
      and sum(1 for c in traces["cases"] if c[2] == "hors_des_feuilles") == b["hors"])
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
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
                   / "398_le_rognage_fait_il_changer_de_feuille_les_chaines_de_la_graine_6.png")
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
