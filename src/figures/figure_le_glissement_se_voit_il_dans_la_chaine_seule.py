"""Sur PHerc0358 : côté par côté, les paires d'une chaîne suivie et de sa compagne, celles qui tiennent les comptes bruts et celles qui tiennent les comptes corrigés des sauts nuls et doubles.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté, trois barres : les paires en gris clair, celles qui tiennent les comptes bruts en
orange, celles qui tiennent les comptes corrigés en bleu ; sous chaque côté, les sauts nuls et doubles de ses deux chaînes.

  uv run python src/figures/figure_le_glissement_se_voit_il_dans_la_chaine_seule.py \\
      --sortie docs/images/369_le_glissement_se_voit_il_dans_la_chaine_seule.png

⚠ Tout vient de la mesure de `369`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_glissement_se_voit_il_dans_la_chaine_seule.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (205, 203, 197)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 130, 370
LARGEUR = 34
LES_BARRES = (("les_paires", CLAIR), ("brut", ORANGE), ("corrige", BLEU))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_comptes(c: dict) -> dict:
    """Les paires d'un côté, celles qui tiennent les comptes bruts, celles qui tiennent les comptes corrigés, et les sauts nuls et doubles de
    ses deux chaînes."""
    def corrige(p):
        ws = c["suivie"][p["le_saut_suivi"] - 1]["le_compte_corrige"]
        wc = c["compagne"][p["le_saut_compagnon"] - 1]["le_compte_corrige"]
        return p["meme_feuille"] == (ws == wc)
    sauts = [s for k in ("suivie", "compagne") for s in c[k]]
    return {"les_paires": len(c["les_paires"]), "brut": sum(p["tient_les_comptes"] for p in c["les_paires"]),
            "corrige": sum(corrige(p) for p in c["les_paires"]), "nuls": sum(s["le_genre"] == "nul" for s in sauts),
            "doubles": sum(s["le_genre"] == "double" for s in sauts)}


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"{b['tiennent_corrige']} paires sur {b['les_paires']} tiennent les comptes corrigés, contre {b['tiennent_brut']} : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    g = d["le_bilan"]["les_genres"]
    deux = (f"rapporté à côté, qui ne décide rien : {g['nul']} sauts nuls, {g['double']} double et {g['simple']} simples dans les deux "
            f"chaînes ; écart médian des sauts simples : {d['lecart_median_des_sauts_simples']} voxels")
    trois = "⚠ ce qui n'est PAS établi : si un saut simple est sur la bonne feuille, ni ce que valent ces seuils sur PHercParis4."
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
    ecrire(50, 46, "par côté : les paires (gris), celles qui tiennent les comptes bruts (orange) et les comptes corrigés (bleu)",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 30, BAS, x1 - 30, BAS], fill=GRIS, width=1)
    comptes = [(c["le_rang"], c["le_cote"], les_comptes(c)) for c in d["les_cotes"]]
    plus = max((n["les_paires"] for _, _, n in comptes), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(comptes))
    for i, (rang, cote, n) in enumerate(comptes):
        gauche = x0 + 50 + i * pas
        traces["cotes"].append((rang, cote, n["nuls"], n["doubles"]))
        for j, (cle, couleur) in enumerate(LES_BARRES):
            g = gauche + j * (LARGEUR + 6)
            sommet = BAS - round(n[cle] / plus * (BAS - HAUT))
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((rang, cote, cle, n[cle], sommet, couleur))
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            ecrire(g + 8, sommet - 18, str(n[cle]), petit, ENCRE)
        ecrire(gauche, BAS + 8, f"graine {rang}, {cote}", moyen, ENCRE)
        ecrire(gauche, BAS + 30, f"sauts nuls : {n['nuls']} · doubles : {n['doubles']}", petit, GRIS)

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
    tmp = sortie.parent / ".sonde_369.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"tiennent_corrige": 9, "tiennent_brut": 7, "les_paires": 10})
    autre["le_verdict"]["lissue"] = "x ; oui, le glissement se voit dans la chaîne seule"
    v("★★★ le titre LIT la mesure",
      le_titre(autre) == "9 PAIRES SUR 10 TIENNENT LES COMPTES CORRIGÉS, CONTRE 7 : OUI, LE GLISSEMENT SE VOIT DANS LA CHAÎNE SEULE",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    recompte = []
    for c in d["les_cotes"]:
        cs = {"les_paires": len(c["les_paires"]), "brut": 0, "corrige": 0}
        for p in c["les_paires"]:
            cs["brut"] += p["meme_feuille"] == (p["le_saut_suivi"] == p["le_saut_compagnon"])
            meme = (c["suivie"][p["le_saut_suivi"] - 1]["le_compte_corrige"] == c["compagne"][p["le_saut_compagnon"] - 1]["le_compte_corrige"])
            cs["corrige"] += p["meme_feuille"] == meme
        recompte += [(c["le_rang"], c["le_cote"], k, cs[k]) for k, _ in LES_BARRES]
    v("★★★★ trois barres par côté, dans l'ordre de la mesure, recomptées sur les paires",
      [b[:4] for b in traces["barres"]] == recompte, str(traces["barres"][:6]))
    b = d["le_bilan"]
    somme = {k: sum(n for _, _, c, n, _, _ in traces["barres"] if c == k) for k, _ in LES_BARRES}
    v("★★★★ les barres somment au bilan : paires, brutes et corrigées",
      somme == {"les_paires": b["les_paires"], "brut": b["tiennent_brut"], "corrige": b["tiennent_corrige"]}, str(somme))
    v("★★★★ les paires en gris clair, les comptes bruts en orange, les comptes corrigés en bleu",
      all(f == {"les_paires": CLAIR, "brut": ORANGE, "corrige": BLEU}[c] for _, _, c, _, _, f in traces["barres"]))
    plus = max(n for _, _, c, n, _, _ in traces["barres"] if c == "les_paires")
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté au plus grand côté",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, _, _, n, s, _ in traces["barres"]))
    sauts = [(c["le_rang"], c["le_cote"], sum(s["le_genre"] == "nul" for k in ("suivie", "compagne") for s in c[k]),
              sum(s["le_genre"] == "double" for k in ("suivie", "compagne") for s in c[k])) for c in d["les_cotes"]]
    v("★★★★ sous chaque côté, ses sauts nuls et doubles, recomptés sur les deux chaînes", traces["cotes"] == sauts, str(traces["cotes"]))
    v("★★★ les sauts nuls et doubles des côtés somment aux genres du bilan",
      (sum(n for _, _, n, _ in sauts), sum(n for _, _, _, n in sauts)) == (b["les_genres"]["nul"], b["les_genres"]["double"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte les genres et l'écart des sauts simples",
      f"{b['les_genres']['nul']} sauts nuls, {b['les_genres']['double']} double" in la_bande(d)[1]
      and f"{d['lecart_median_des_sauts_simples']} voxels" in la_bande(d)[1])
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "369_le_glissement_se_voit_il_dans_la_chaine_seule.png")
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
