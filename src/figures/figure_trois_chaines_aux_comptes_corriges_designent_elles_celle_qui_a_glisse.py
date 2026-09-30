"""Sur PHerc0358 : côté par côté, la part des paires qui tiennent les comptes corrigés pour chacun des trois couples de chaînes, et la chaîne que le vote désigne.

⚠⚠ **Ce que cette figure doit rendre évident.** Par côté, trois barres, une par couple : suivie et compagne, suivie et tierce, compagne et
tierce ; leur hauteur est la part des paires qui tiennent les comptes corrigés. Un couple qui tient en bleu, un couple qui compte sans
tenir en orange, un couple de moins de 5 paires en gris clair ; le trait des 90 %. Sous chaque côté, où la tierce est posée et la chaîne
désignée.

  uv run python src/figures/figure_trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.py \\
      --sortie docs/images/373_trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.png

⚠ Tout vient de la mesure de `373`, et des paires et des sauts que `368` et `369` publient.
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
LA_MESURE = RACINE / "docs" / "mesures" / "trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.json"
LES_SAUTS_DE_369 = RACINE / "docs" / "mesures" / "le_glissement_se_voit_il_dans_la_chaine_seule.json"
LES_PAIRES_DE_368 = RACINE / "docs" / "mesures" / "deux_chaines_voisines_comptent_elles_les_memes_tours_sur_pherc0358.json"

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
LES_COUPLES = ("suivie|compagne", "suivie|tierce", "compagne|tierce")
LES_NOMS = {"suivie|compagne": "S·C", "suivie|tierce": "S·T", "compagne|tierce": "C·T"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def la_part(c: dict) -> float:
    return c["tiennent"] / c["les_paires"] if c["les_paires"] else 0.0


def la_couleur(c: dict):
    return BLEU if c["tient"] else ORANGE if c["compte"] else CLAIR


def le_designe(cote: dict) -> str:
    if not cote["la_tierce"]:
        return "sans tierce"
    return f"{cote['ou']} · " + (f"désignée : {cote['le_vote']}" if cote["le_vote"] else "aucune désignée")


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"trois chaînes aux comptes corrigés : {v['lissue']}".upper()
    b = d["le_bilan"]
    return (f"le vote désigne l'une des deux sur {b['designent']} côté{'s' if b['designent'] > 1 else ''} sur {b['en_desaccord']} : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    votes = ", ".join(f"graine {k.split()[0]}, {k.split()[1]} : {v}" for k, v in d["le_bilan"]["les_votes"].items() if v)
    bruts = ", ".join(f"graine {k.split()[0]}, {k.split()[1]} : {v}" for k, v in d["le_bilan"]["les_votes_bruts"].items() if v)
    deux = (f"rapporté à côté, qui ne décide rien : S suivie, C compagne, T tierce ; désignées : {votes or 'aucune'} ; "
            f"sur les comptes bruts : {bruts or 'aucune'}")
    trois = "⚠ ce qui n'est PAS établi : si la chaîne désignée a glissé plutôt que les deux autres ensemble, ni où tombe son glissement."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": [], "cotes": [], "le_trait": None}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "par côté, la part des paires qui tiennent les comptes corrigés pour chaque couple ; bleu : tient, orange : compte sans "
                   "tenir, gris : moins de 5 paires", petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    art.line([x0 + 30, BAS, x1 - 30, BAS], fill=GRIS, width=1)
    y90 = BAS - round(d["les_constantes"]["la_part"] * (BAS - HAUT))
    for x in range(x0 + 30, x1 - 30, 10):
        art.line([x, y90, x + 5, y90], fill=GRIS)
    traces["le_trait"] = y90
    ecrire(x1 - 70, y90 - 16, "90 %", petit, GRIS)
    pas = (x1 - x0 - 60) // max(1, len(d["les_cotes"]))
    for i, cote in enumerate(d["les_cotes"]):
        gauche = x0 + 50 + i * pas
        for j, k in enumerate(LES_COUPLES):
            c = cote["les_couples"][k]
            g = gauche + j * (LARGEUR + 6)
            sommet = BAS - round(la_part(c) * (BAS - HAUT))
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=la_couleur(c))
            traces["barres"].append((cote["le_rang"], cote["le_cote"], k, c["tiennent"], c["les_paires"], sommet, la_couleur(c)))
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            ecrire(g + 2, sommet - 16, f"{c['tiennent']}/{c['les_paires']}", petit, ENCRE)
            ecrire(g + 6, BAS + 4, LES_NOMS[k], petit, GRIS)
        ecrire(gauche, BAS + 24, f"graine {cote['le_rang']}, {cote['le_cote']}", moyen, ENCRE)
        ecrire(gauche, BAS + 44, le_designe(cote), petit, GRIS)
        traces["cotes"].append((cote["le_rang"], cote["le_cote"], le_designe(cote)))

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
    tmp = sortie.parent / ".sonde_373.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_bilan"].update({"designent": 3, "en_desaccord": 4})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    un_cote = json.loads(json.dumps(autre))
    un_cote["le_bilan"]["designent"] = 1
    v("★★★ le titre LIT la mesure, au singulier pour un seul côté",
      le_titre(autre) == "LE VOTE DÉSIGNE L'UNE DES DEUX SUR 3 CÔTÉS SUR 4 : EN PARTIE"
      and le_titre(un_cote) == "LE VOTE DÉSIGNE L'UNE DES DEUX SUR 1 CÔTÉ SUR 4 : EN PARTIE", le_titre(un_cote))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "TROIS CHAÎNES AUX COMPTES CORRIGÉS : INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    d368, d369 = json.loads(LES_PAIRES_DE_368.read_text()), json.loads(LES_SAUTS_DE_369.read_text())
    attendu = []
    for c, c8, c9 in zip(d["les_cotes"], d368["les_cotes"], d369["les_cotes"]):
        comptes = {"suivie": c9["suivie"], "compagne": c9["compagne"], "tierce": c["les_sauts_de_la_tierce"]}
        for k in ("suivie|compagne", "suivie|tierce", "compagne|tierce"):
            p = c["les_paires"][k] if k in c["les_paires"] else c8["les_paires"]
            a, b = (comptes[x] for x in k.split("|"))
            t_ = sum(x["meme_feuille"] == (a[x["le_saut_suivi"] - 1]["le_compte_corrige"] == b[x["le_saut_compagnon"] - 1]["le_compte_corrige"])
                     for x in p)
            attendu.append((c["le_rang"], c["le_cote"], k, t_, len(p)))
    v("★★★★ trois barres par côté, une par couple, recomptées sur les comptes corrigés des paires publiées",
      [b[:5] for b in traces["barres"]] == attendu, str(traces["barres"][:4]))
    v("★★★★ la hauteur de chaque barre est sa part de paires qui tiennent, zéro sans paire",
      all(BAS - s == round((t / n if n else 0.0) * (BAS - HAUT)) for _, _, _, t, n, s, _ in traces["barres"]))
    couleurs = [BLEU if (n >= 5 and t >= 0.9 * n) else ORANGE if n >= 5 else CLAIR for _, _, _, t, n, _, _ in traces["barres"]]
    v("★★★★ bleu s'il tient, à 90 % et 5 paires, orange s'il compte sans tenir, gris sous 5 paires",
      [b[6] for b in traces["barres"]] == couleurs)
    v("★★★★ le trait des 90 %", traces["le_trait"] == BAS - round(0.9 * (BAS - HAUT)))
    designes = [(c["le_rang"], c["le_cote"], "sans tierce" if not c["la_tierce"] else
                 f"{c['ou']} · " + (f"désignée : {c['le_vote']}" if c["le_vote"] else "aucune désignée")) for c in d["les_cotes"]]
    v("★★★★ sous chaque côté, où la tierce est posée et la chaîne désignée, ou son absence dite", traces["cotes"] == designes,
      str(traces["cotes"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande nomme chaque chaîne désignée, sur les comptes corrigés puis bruts",
      all(f": {v_}" in la_bande(d)[1].split(" ; sur les comptes bruts")[0] for v_ in d["le_bilan"]["les_votes"].values() if v_)
      and all(f": {v_}" in la_bande(d)[1].split(" ; sur les comptes bruts")[1] for v_ in d["le_bilan"]["les_votes_bruts"].values() if v_))
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
                   / "373_trois_chaines_aux_comptes_corriges_designent_elles_celle_qui_a_glisse.png")
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
