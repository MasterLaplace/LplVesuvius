"""Sur PHerc0358 : côté par côté, les paires d'une chaîne suivie et de sa compagne, celles qui tiennent les comptes corrigés de `369` et celles qui tiennent les comptes en tours.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté, trois barres : les paires en gris clair, celles qui tiennent les comptes
corrigés de `369` en orange, celles qui tiennent les comptes en tours en bleu ; sous chaque côté, les sauts comptés à deux tours et les
paires qui tiennent au seuil en pas.

  uv run python src/figures/figure_compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.py \\
      --sortie docs/images/371_compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.png

⚠ Tout vient de la mesure de `371`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.json"
LES_PAIRES = RACINE / "docs" / "mesures" / "le_glissement_se_voit_il_dans_la_chaine_seule.json"

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
LES_BARRES = (("les_paires", CLAIR), ("tiennent_369", ORANGE), ("tiennent", BLEU))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_comptes(c: dict) -> dict:
    """Les paires d'un côté, celles qui tiennent les comptes corrigés de `369`, celles qui tiennent les comptes en tours et au seuil en pas,
    et les sauts de ses deux chaînes comptés à deux tours ou plus."""
    return {"les_paires": c["les_paires"], "tiennent_369": c["tiennent_369"], "tiennent": c["tiennent"], "en_pas": c["tiennent_en_pas"],
            "doubles": sum(s["les_tours"] >= 2 for k in ("suivie", "compagne") for s in c[k])}


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["le_bilan"]
    return (f"{b['tiennent']} paires sur {b['les_paires']} tiennent les comptes en tours, contre {b['tiennent_369']} : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    b, s = d["le_bilan"], d["les_seuils"]
    deux = (f"rapporté à côté, qui ne décide rien : au seuil de 370 en pas, {s['deux_en_pas']:g} pas sans rapporter à la chaîne, "
            f"{b['tiennent_en_pas']} paires tiennent les comptes ; {b['les_sauts_par_tours']['2']} sauts comptés à deux tours").replace(".", ",")
    trois = "⚠ ce qui n'est PAS établi : si un saut compté à deux tours en franchit deux, ni laquelle des deux chaînes a raison ailleurs."
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
    ecrire(50, 46, "par côté : les paires (gris), celles qui tiennent les comptes corrigés de 369 (orange) et les comptes en tours (bleu)",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 30, BAS, x1 - 30, BAS], fill=GRIS, width=1)
    comptes = [(c["le_rang"], c["le_cote"], les_comptes(c)) for c in d["les_cotes"]]
    plus = max((n["les_paires"] for _, _, n in comptes), default=0) or 1
    pas = (x1 - x0 - 60) // max(1, len(comptes))
    for i, (rang, cote, n) in enumerate(comptes):
        gauche = x0 + 50 + i * pas
        traces["cotes"].append((rang, cote, n["doubles"], n["en_pas"]))
        for j, (cle, couleur) in enumerate(LES_BARRES):
            g = gauche + j * (LARGEUR + 6)
            sommet = BAS - round(n[cle] / plus * (BAS - HAUT))
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((rang, cote, cle, n[cle], sommet, couleur))
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            ecrire(g + 8, sommet - 18, str(n[cle]), petit, ENCRE)
        ecrire(gauche, BAS + 8, f"graine {rang}, {cote}", moyen, ENCRE)
        ecrire(gauche, BAS + 30, f"à deux tours : {n['doubles']} · en pas : {n['en_pas']}", petit, GRIS)

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
    tmp = sortie.parent / ".sonde_371.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"tiennent": 9, "tiennent_369": 7, "les_paires": 10})
    autre["le_verdict"]["lissue"] = "x ; non"
    v("★★★ le titre LIT la mesure", le_titre(autre) == "9 PAIRES SUR 10 TIENNENT LES COMPTES EN TOURS, CONTRE 7 : NON", le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    d369 = json.loads(LES_PAIRES.read_text())
    recompte = []
    for c, c9 in zip(d["les_cotes"], d369["les_cotes"]):
        cs = {"les_paires": len(c9["les_paires"]), "tiennent_369": 0, "tiennent": 0}
        for p in c9["les_paires"]:
            h, k = p["le_saut_suivi"] - 1, p["le_saut_compagnon"] - 1
            cs["tiennent_369"] += p["meme_feuille"] == (c9["suivie"][h]["le_compte_corrige"] == c9["compagne"][k]["le_compte_corrige"])
            cs["tiennent"] += p["meme_feuille"] == (c["suivie"][h]["le_compte"] == c["compagne"][k]["le_compte"])
        recompte += [(c["le_rang"], c["le_cote"], k, cs[k]) for k, _ in LES_BARRES]
    v("★★★★ trois barres par côté, dans l'ordre de la mesure, recomptées sur les paires que 369 publie",
      [b[:4] for b in traces["barres"]] == recompte, str(traces["barres"][:6]))
    b = d["le_bilan"]
    somme = {k: sum(n for _, _, c, n, _, _ in traces["barres"] if c == k) for k, _ in LES_BARRES}
    v("★★★★ les barres somment au bilan : paires, comptes corrigés de 369 et comptes en tours",
      somme == {"les_paires": b["les_paires"], "tiennent_369": b["tiennent_369"], "tiennent": b["tiennent"]}, str(somme))
    v("★★★★ les paires en gris clair, les comptes de 369 en orange, les comptes en tours en bleu",
      all(f == {"les_paires": CLAIR, "tiennent_369": ORANGE, "tiennent": BLEU}[c] for _, _, c, _, _, f in traces["barres"]))
    plus = max(n for _, _, c, n, _, _ in traces["barres"] if c == "les_paires")
    v("★★★★ la hauteur de chaque barre est son nombre, rapporté au plus grand côté",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, _, _, n, s, _ in traces["barres"]))
    sous = [(c["le_rang"], c["le_cote"], sum(s["les_tours"] >= 2 for k in ("suivie", "compagne") for s in c[k]), c["tiennent_en_pas"])
            for c in d["les_cotes"]]
    v("★★★★ sous chaque côté, ses sauts à deux tours, recomptés sur les deux chaînes, et ses paires au seuil en pas",
      traces["cotes"] == sous, str(traces["cotes"]))
    v("★★★ les sauts à deux tours et les paires en pas des côtés somment au bilan",
      (sum(n for _, _, n, _ in sous), sum(n for _, _, _, n in sous))
      == (b["les_sauts_par_tours"]["2"] + b["les_sauts_par_tours"]["3"], b["tiennent_en_pas"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte le seuil en pas et ses paires", f"{b['tiennent_en_pas']} paires tiennent les comptes" in la_bande(d)[1]
      and f"{d['les_seuils']['deux_en_pas']:g} pas".replace(".", ",") in la_bande(d)[1])
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
                   / "371_compter_les_sauts_en_tours_fait_il_voir_le_glissement_sur_pherc0358.png")
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
