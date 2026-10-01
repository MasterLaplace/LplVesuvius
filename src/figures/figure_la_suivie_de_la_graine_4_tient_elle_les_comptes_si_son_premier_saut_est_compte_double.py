"""Sur la graine 4, côté plus, de PHerc0358 : avant et après le recompte du premier saut de la suivie, la part des paires qui tiennent les comptes dans chaque couple, et les surfaces par statut.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chacun des trois couples, deux barres : la part des paires qui tiennent les
comptes avant le recompte, en gris, et après, en bleu. À droite, les surfaces des trois chaînes par statut, avant en gris et après en bleu.

  uv run python src/figures/figure_la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.py \\
      --sortie docs/images/381_la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.png

⚠ Tout vient de la mesure de `381`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (190, 188, 182)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
L_, H_ = 1300, 560
LA_BANDE = 440
HAUT, BAS = 150, 350
LARGEUR = 34
LES_COUPLES = ("suivie|compagne", "suivie|tierce", "compagne|tierce")
LES_STATUTS = ("validée", "confirmée une fois", "contredite", "sans témoin")
LES_TEMPS = (("avant", CLAIR), ("apres", BLEU))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    a = d["apres"]
    return (f"premier saut compté double : la suivie tient {a['les_couples']['suivie|compagne']['tiennent']}/"
            f"{a['les_couples']['suivie|compagne']['les_paires']} et {a['les_couples']['suivie|tierce']['tiennent']}/"
            f"{a['les_couples']['suivie|tierce']['les_paires']} paires : {v['lissue'].rpartition(' ; ')[2].partition(',')[0]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    ctl = ", ".join(f"graine {k.split()[0]}, {k.split()[1]} : {'défait' if not any(v.values()) else 'tient encore'}"
                    for k, v in d["le_controle"].items())
    deux = (f"rapporté à côté, qui ne décide rien : {d['apres']['validees']} surfaces validées après le recompte, jusqu'à "
            f"{d['apres']['le_plus_loin']} tours ; contrôle, la suivie décalée d'un tour là où tout tenait : {ctl}")
    trois = "⚠ ce qui n'est PAS établi : si le premier saut de la suivie a réellement franchi deux feuilles."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 610, 420), (670, 70, 1250, 420)]
    traces = {"couples": [], "statuts": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, f"graine {d['le_cote'][0]}, côté {d['le_cote'][1]} : avant le recompte en gris, après en bleu ; premier saut de la "
                   f"suivie à {d['le_premier_saut_de_la_suivie']['en_pas']:g} pas".replace(".", ","), petit, GRIS)
    for (x0, y0, x1, y1), titre in zip(cadres, ("la part des paires qui tiennent les comptes", "les surfaces des trois chaînes")):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        art.line([x0 + 20, BAS, x1 - 20, BAS], fill=GRIS, width=1)
        ecrire(x0 + 16, y0 + 12, titre, moyen, ENCRE)
    x0 = cadres[0][0]
    for i, k in enumerate(LES_COUPLES):
        g0 = x0 + 50 + i * 175
        for j, (t, couleur) in enumerate(LES_TEMPS):
            c = d[t]["les_couples"][k]
            part = c["tiennent"] / c["les_paires"] if c["les_paires"] else 0.0
            g = g0 + j * (LARGEUR + 6)
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
            traces["couples"].append((k, t, c["tiennent"], c["les_paires"], sommet, couleur))
            traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            ecrire(g, sommet - 18, f"{c['tiennent']}/{c['les_paires']}", petit, ENCRE)
        ecrire(g0, BAS + 10, k.replace("|", " et "), petit, ENCRE)
    x0 = cadres[1][0]
    plus = max(d[t]["par_statut"][s] for t, _ in LES_TEMPS for s in LES_STATUTS) or 1
    for i, s in enumerate(LES_STATUTS):
        g0 = x0 + 40 + i * 135
        for j, (t, couleur) in enumerate(LES_TEMPS):
            n = d[t]["par_statut"][s]
            g = g0 + j * (LARGEUR + 6)
            sommet = BAS - round(n / plus * (BAS - HAUT))
            if n:
                art.rectangle([g, sommet, g + LARGEUR, BAS], fill=couleur)
                traces["rectangles"].append((g, g + LARGEUR, sommet, BAS))
            traces["statuts"].append((s, t, n, sommet, couleur))
            ecrire(g + 8, sommet - 18, str(n), petit, ENCRE)
        ecrire(g0, BAS + 10, s, petit, ENCRE)

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
    tmp = sortie.parent / ".sonde_381.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["apres"]["les_couples"]["suivie|compagne"].update({"tiennent": 3, "les_paires": 9})
    autre["le_verdict"] = {"decidable": True, "lissue": "x ; en partie"}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("PREMIER SAUT COMPTÉ DOUBLE : LA SUIVIE TIENT 3/9 ET ")
      and le_titre(autre).endswith(" PAIRES : EN PARTIE"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    attendu = [(k, t, d[t]["les_couples"][k]["tiennent"], d[t]["les_couples"][k]["les_paires"])
               for k in ("suivie|compagne", "suivie|tierce", "compagne|tierce") for t in ("avant", "apres")]
    v("★★★★ deux barres par couple, avant puis après, lues dans la mesure", [c[:4] for c in traces["couples"]] == attendu,
      str(traces["couples"][:2]))
    v("★★★★ la hauteur d'une barre de couple est sa part de paires qui tiennent",
      all(BAS - s == round(t / n * (BAS - HAUT)) for _, _, t, n, s, _ in traces["couples"]))
    st = [(s, t, d[t]["par_statut"][s]) for s in ("validée", "confirmée une fois", "contredite", "sans témoin") for t in ("avant", "apres")]
    v("★★★★ deux barres par statut, avant puis après, lues dans la mesure", [x[:3] for x in traces["statuts"]] == st, str(traces["statuts"][:2]))
    plus = max(n for _, _, n, _, _ in traces["statuts"])
    v("★★★★ la hauteur d'une barre de statut est son nombre, rapporté à la plus haute",
      all(BAS - s == round(n / plus * (BAS - HAUT)) for _, _, n, s, _ in traces["statuts"]))
    v("★★★★ les statuts de chaque temps somment aux surfaces des trois chaînes",
      all(sum(d[t]["par_statut"].values()) == len(d[t]["les_surfaces"]) for t in ("avant", "apres")))
    v("★★★★ avant en gris, après en bleu",
      all(f == {"avant": CLAIR, "apres": BLEU}[t] for _, t, *_, f in traces["couples"])
      and all(f == {"avant": CLAIR, "apres": BLEU}[t] for _, t, _, _, f in traces["statuts"]))
    dehors = [r for r in traces["rectangles"] if not any(x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1 for x0, y0, x1, y1 in cadres)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte les validées et le contrôle",
      f"{d['apres']['validees']} surfaces validées après le recompte, jusqu'à {d['apres']['le_plus_loin']} tours" in la_bande(d)[1]
      and all(f"graine {k.split()[0]}, {k.split()[1]} : {'défait' if not any(x.values()) else 'tient encore'}" in la_bande(d)[1]
              for k, x in d["le_controle"].items()))
    tenu = json.loads(json.dumps(d))
    tenu["le_controle"] = {"6 moins": {"suivie|compagne": True, "suivie|tierce": False}}
    v("★★★★ un contrôle qui tient encore est dit tel", "graine 6, moins : tient encore" in la_bande(tenu)[1], la_bande(tenu)[1])
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
                   / "381_la_suivie_de_la_graine_4_tient_elle_les_comptes_si_son_premier_saut_est_compte_double.png")
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
