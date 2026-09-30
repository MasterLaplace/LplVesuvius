"""Sur PHerc0358 : côté par côté, combien des surfaces des trois chaînes l'accord valide, confirme une fois, contredit ou laisse sans témoin.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté, quatre barres : les surfaces validées en bleu, confirmées par une seule autre
chaîne en bleu clair, contredites en orange, sans témoin en gris clair ; sous chaque côté, le plus grand compte d'une surface validée.

  uv run python src/figures/figure_quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.py \\
      --sortie docs/images/374_quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.png

⚠ Tout vient de la mesure de `374`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
PALE = (150, 172, 196)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 130, 370
LARGEUR = 28
LES_BARRES = (("validée", BLEU), ("confirmée une fois", PALE), ("contredite", ORANGE), ("sans témoin", CLAIR))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_comptes(c: dict) -> dict:
    """Les surfaces d'un côté par statut, et le plus grand compte d'une surface validée."""
    n = {k: sum(s["le_statut"] == k for s in c["les_surfaces"]) for k, _ in LES_BARRES}
    n["le_plus_loin"] = max((s["le_compte"] for s in c["les_surfaces"] if s["le_statut"] == "validée"), default=None)
    return n


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"{b['validees']} surfaces sur {b['les_surfaces']} validées, jusqu'à {b['le_plus_loin']} tours : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b = d["le_bilan"]
    ctl = ", ".join(f"graine {k.split()[0]}, {k.split()[1]} : {'tenu' if v else 'échoué'}" for k, v in b["les_controles"].items())
    deux = (f"rapporté à côté, qui ne décide rien : {b['par_statut']['contredite']} surfaces contredites, "
            f"{b['par_statut']['sans témoin']} sans témoin ; contrôle sur la chaîne désignée : {ctl or 'aucun'}")
    trois = "⚠ ce qui n'est PAS établi : si une surface validée est sur la bonne feuille, ni si trois chaînes peuvent glisser ensemble."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": [], "cotes": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par côté, les surfaces des trois chaînes : validées (bleu), confirmées une fois (bleu clair), contredites (orange), "
                   "sans témoin (gris)", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 30, BAS, x1 - 30, BAS], fill=GRIS, width=1)
    comptes = [(c["le_rang"], c["le_cote"], les_comptes(c)) for c in d["les_cotes"]]
    plus = max((n[k] for _, _, n in comptes for k, _ in LES_BARRES), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(comptes))
    for i, (rang, cote, n) in enumerate(comptes):
        gauche = x0 + 50 + i * pas
        traces["cotes"].append((rang, cote, n["le_plus_loin"]))
        for j, (cle, couleur) in enumerate(LES_BARRES):
            g = gauche + j * (LARGEUR + 4)
            sommet = BAS - round(n[cle] / plus * (BAS - HAUT))
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((rang, cote, cle, n[cle], sommet, couleur))
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            ecrire(g + 6, sommet - 18, str(n[cle]), petit, ENCRE)
        ecrire(gauche, BAS + 8, f"graine {rang}, {cote}", moyen, ENCRE)
        loin = f"validées jusqu'à {n['le_plus_loin']} tours" if n["le_plus_loin"] is not None else "aucune validée"
        ecrire(gauche, BAS + 30, loin, petit, GRIS)

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
    tmp = sortie.parent / ".sonde_374.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"validees": 9, "les_surfaces": 10, "le_plus_loin": 3})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "9 SURFACES SUR 10 VALIDÉES, JUSQU'À 3 TOURS : EN PARTIE", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    statuts = ("validée", "confirmée une fois", "contredite", "sans témoin")
    attendu = [(c["le_rang"], c["le_cote"], k, sum(s["le_statut"] == k for s in c["les_surfaces"])) for c in d["les_cotes"] for k in statuts]
    v("★★★★ quatre barres par côté, dans l'ordre des statuts, recomptées sur les surfaces",
      [b_[:4] for b_ in traces["barres"]] == attendu, str(traces["barres"][:4]))
    b = d["le_bilan"]
    somme = {k: sum(n for _, _, c, n, _, _ in traces["barres"] if c == k) for k in statuts}
    v("★★★★ les barres somment au bilan par statut", somme == b["par_statut"] and sum(somme.values()) == b["les_surfaces"], str(somme))
    v("★★★★ validées en bleu, confirmées une fois en bleu clair, contredites en orange, sans témoin en gris clair",
      all(f == {"validée": BLEU, "confirmée une fois": PALE, "contredite": ORANGE, "sans témoin": CLAIR}[c]
          for _, _, c, _, _, f in traces["barres"]))
    plus = max(n for _, _, _, n, _, _ in traces["barres"])
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, _, _, n, s, _ in traces["barres"]))
    loin = [(c["le_rang"], c["le_cote"], max((s["le_compte"] for s in c["les_surfaces"] if s["le_statut"] == "validée"), default=None))
            for c in d["les_cotes"]]
    v("★★★★ sous chaque côté, le plus grand compte d'une surface validée", traces["cotes"] == loin, str(traces["cotes"]))
    v("★★★ le plus loin des côtés est celui du bilan", max(x for _, _, x in loin if x is not None) == b["le_plus_loin"])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte les contredites et le contrôle", f"{b['par_statut']['contredite']} surfaces contredites" in la_bande(d)[1]
      and all(f"{k.split()[1]} : {'tenu' if v_ else 'échoué'}" in la_bande(d)[1] for k, v_ in b["les_controles"].items()))
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
                   / "374_quelles_surfaces_laccord_de_trois_chaines_valide_t_il_sur_pherc0358.png")
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
