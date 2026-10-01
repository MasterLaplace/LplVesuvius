"""Sur la graine 8 de PHerc0358 : couple par couple, l'écart des comptes de m7 sur les paires même feuille, dans l'ordre des sauts, et la paire où le couple se met à se contredire.

⚠⚠ **Ce que cette figure doit rendre évident.** Six panneaux, un par couple des deux côtés de la graine 8 ; dans chacun, un point par paire
même feuille, à l'écart des comptes des deux surfaces (zéro : même compte, donc accord), dans l'ordre des sauts ; en titre, la paire où le
couple naît à la contradiction et si c'est au premier saut.

  uv run python src/figures/figure_les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.py \\
      --sortie docs/images/386_les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.png

⚠ Tout vient de la mesure de `386`.
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
LA_MESURE = (RACINE / "docs" / "mesures"
             / "les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.json")

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1300, 660
LA_BANDE = 560
LARGEUR_P, HAUTEUR_P = 390, 220
GAUCHE, HAUT_P, ECART_X, ECART_Y = 50, 90, 25, 20
Y_MIN, Y_MAX = -6, 6
RAYON = 5


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_cadre(i: int) -> tuple[int, int, int, int]:
    """Le cadre du panneau `i` : trois par rangée, le côté plus en haut, le côté moins en bas."""
    x0 = GAUCHE + (i % 3) * (LARGEUR_P + ECART_X)
    y0 = HAUT_P + (i // 3) * (HAUTEUR_P + ECART_Y)
    return x0, y0, x0 + LARGEUR_P, y0 + HAUTEUR_P


def en_y(cadre: tuple, e: int) -> int:
    x0, y0, x1, y1 = cadre
    haut, bas = y0 + 40, y1 - 20
    return bas - round((e - Y_MIN) / (Y_MAX - Y_MIN) * (bas - haut))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"graine 8 : {b['au_premier_saut']} couples sur {b['avec_une_naissance']} se contredisent dès le premier saut, "
            f"{b['apres_un_saut_de_deux']} après un saut de deux feuilles").upper()


def la_naissance_dite(c: dict) -> str:
    n = c["la_naissance"]
    if n is None:
        return "aucune contradiction"
    return (f"naît en ({n['le_saut_suivi']}, {n['le_saut_compagnon']})" + (", au premier saut" if n["au_premier_saut"] else "")
            + (", après un saut de deux" if n["apres_un_saut_de_deux"] else ""))


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    tot = sum(c["contredisent"] for c in d["les_couples"])
    n = sum(c["les_paires"] for c in d["les_couples"])
    deux = f"rapporté à côté, qui ne décide rien : {tot} des {n} paires des six couples se contredisent aux comptes de m7"
    trois = "⚠ ce qui n'est PAS établi : laquelle des chaînes se trompe, ni si les feuilles de la graine 8 se touchent."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [le_cadre(i) for i in range(len(d["les_couples"]))]
    traces = {"points": [], "titres": [], "zeros": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par couple, l'écart des comptes de m7 sur chaque paire même feuille, dans l'ordre des sauts ; zéro : même compte",
           petit, GRIS)
    for i, c in enumerate(d["les_couples"]):
        cadre = cadres[i]
        x0, y0, x1, y1 = cadre
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        ecrire(x0 + 10, y0 + 6, f"{c['le_cote']} · {c['le_couple'].replace('|', ' et ')}", moyen, ENCRE)
        dite = la_naissance_dite(c)
        ecrire(x0 + 10, y0 + 24, dite, petit, ALERTE if c["la_naissance"] else GRIS)
        traces["titres"].append((c["le_cote"], c["le_couple"], dite))
        yz = en_y(cadre, 0)
        art.line([x0 + 10, yz, x1 - 10, yz], fill=GRIS)
        traces["zeros"].append(yz)
        es = c["les_ecarts_ensuite"]
        pas = (x1 - x0 - 40) / max(1, len(es))
        for j, (h, k, e) in enumerate(es):
            x = round(x0 + 25 + j * pas)
            y = en_y(cadre, max(Y_MIN, min(Y_MAX, e)))
            couleur = BLEU if e == 0 else ORANGE
            art.ellipse([x - RAYON, y - RAYON, x + RAYON, y + RAYON], fill=couleur)
            traces["points"].append((c["le_cote"], c["le_couple"], h, k, e, x, y, couleur))

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
    tmp = sortie.parent / ".sonde_386.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"au_premier_saut": 2, "avec_une_naissance": 5, "apres_un_saut_de_deux": 1})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; ni l'un ni l'autre partout"}
    v("★★★ le titre LIT la mesure",
      le_titre(autre) == "GRAINE 8 : 2 COUPLES SUR 5 SE CONTREDISENT DÈS LE PREMIER SAUT, 1 APRÈS UN SAUT DE DEUX FEUILLES", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(c["le_cote"], c["le_couple"], h, k, e) for c in d["les_couples"] for h, k, e in c["les_ecarts_ensuite"]]
    v("★★★★ un point par paire même feuille, dans l'ordre de la mesure", [t[:5] for t in traces["points"]] == attendu, str(traces["points"][:2]))
    v("★★★★ un point d'accord en bleu, un point d'écart en orange", all(f == (BLEU if e == 0 else ORANGE) for *_, e, _, _, f in traces["points"]))
    v("★★★★ chaque point est à la hauteur de son écart dans son panneau",
      all(y == en_y(cadres[[(c["le_cote"], c["le_couple"]) for c in d["les_couples"]].index((s, k))], max(Y_MIN, min(Y_MAX, e)))
          for s, k, _, _, e, _, y, _ in traces["points"]))
    v("★★★★ aucun écart ne sort de l'échelle", all(Y_MIN <= e <= Y_MAX for *_, e, _, _, _ in traces["points"]))
    v("★★★★ chaque point est dans son panneau",
      all(cadres[[(c["le_cote"], c["le_couple"]) for c in d["les_couples"]].index((s, k))][0] < x
          < cadres[[(c["le_cote"], c["le_couple"]) for c in d["les_couples"]].index((s, k))][2] for s, k, _, _, _, x, _, _ in traces["points"]))
    v("★★★★ chaque panneau dit sa naissance", [t[2] for t in traces["titres"]] == [la_naissance_dite(c) for c in d["les_couples"]])
    v("★★★★ la naissance dite porte la paire et le premier saut",
      la_naissance_dite({"la_naissance": {"le_saut_suivi": 1, "le_saut_compagnon": 2, "au_premier_saut": True, "apres_un_saut_de_deux": True}})
      == "naît en (1, 2), au premier saut, après un saut de deux" and la_naissance_dite({"la_naissance": None}) == "aucune contradiction")
    tot = sum(c["contredisent"] for c in d["les_couples"])
    v("★★★★ la bande compte les paires qui se contredisent", f"{tot} des {sum(c['les_paires'] for c in d['les_couples'])} paires" in la_bande(d)[1])
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
                   / "386_les_contradictions_de_la_graine_8_naissent_elles_au_premier_saut_ou_a_un_saut_de_deux_feuilles.png")
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
