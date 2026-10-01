"""Sur PHercParis4 : les surfaces lues sur le bon tour et sur un mauvais tour, et les surfaces validées et contredites, pour les chaînes de 385, les chaînes rognées et les chaînes rognées comptées entières.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque façon, une barre des surfaces lues : la part sur le bon tour en bleu,
celle sur un mauvais tour en rouille ; à droite, les surfaces validées et contredites de chaque façon. Si le rognage fait tort, la rouille
apparaît dans ses barres.

  uv run python src/figures/figure_des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.py \\
      --sortie docs/images/400_des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.png

⚠ Tout vient de la mesure de `400`, et des surfaces que `385` publie.
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
LA_MESURE = RACINE / "docs" / "mesures" / "des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.json"
CE_QUE_385_A_PUBLIE = RACINE / "docs" / "mesures" / "laccord_aux_comptes_de_m7_valide_t_il_des_surfaces_sur_le_bon_tour_de_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 560
LA_BANDE = 440
LES_FACONS = (("385", "385, non rognées"), ("rognees", "rognées"), ("entieres", "rognées, comptées entières"))
LES_RANGEES = (150, 230, 310)
X0, X1 = 260, 560
Y0, Y1 = 760, 1060


def lire(chemin: Path = LA_MESURE, chemin385: Path = CE_QUE_385_A_PUBLIE) -> dict:
    return {"d": json.loads(chemin.read_text()), "d385": json.loads(chemin385.read_text())}


def les_comptes(m: dict) -> dict:
    """Par façon : les surfaces lues sur le bon tour et sur un mauvais tour, toutes statuts confondus, et les validées et contredites."""
    d, d385 = m["d"], m["d385"]
    t5 = [s for c in d385["les_cotes"] for s in c["les_surfaces_avec_m7"]]
    out = {"385": {"bon": sum(1 for s in t5 if s["lue"] and s["sur_le_bon_tour"]), "faux": sum(1 for s in t5 if s["lue"] and not s["sur_le_bon_tour"]),
                   "validees": sum(s["le_statut"] == "validée" for s in t5), "contredites": sum(s["le_statut"] == "contredite" for s in t5)}}
    for f in ("rognees", "entieres"):
        t = [s for c in d["les_cotes"] for s in c[f]["les_surfaces"]]
        out[f] = {"bon": sum(1 for s in t if s[4] and s[5]), "faux": sum(1 for s in t if s[4] and not s[5]),
                  "validees": sum(s[3] == "validée" for s in t), "contredites": sum(s[3] == "contredite" for s in t)}
    return out


def le_titre(m: dict) -> str:
    v = m["d"]["le_verdict"]
    return v["lissue"].rpartition(" ; ")[2].upper() if v.get("decidable") else v["lissue"].upper()


def la_bande(m: dict) -> tuple[str, ...]:
    d = m["d"]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    r = d["les_rognages"]
    deux = (f"rapporté à côté, qui ne décide rien : {r['rognees']} des {r['vues']} surfaces gardées sont rognées, et perdent "
            f"{format(r['mailles'], ',').replace(',', ' ')} mailles")
    trois = "⚠ ce qui n'est PAS établi : ce que le rognage vaut sur PHerc0358, dont les feuilles se touchent plus souvent."
    return un, deux, trois


def dessiner(m: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1150, 420)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, f"le rognage contre les tours publiés de PHercParis4 : {le_titre(m)}", gros, ENCRE)
    ecrire(50, 46, "à gauche, les surfaces lues, sur le bon tour en bleu et sur un mauvais tour en rouille ; à droite, validées et contredites",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cs = les_comptes(m)
    plus_l = max(c["bon"] + c["faux"] for c in cs.values()) or 1
    plus_v = max(max(c["validees"], c["contredites"]) for c in cs.values()) or 1
    ecrire(X0, 104, "surfaces lues", moyen, ENCRE)
    ecrire(Y0, 104, "validées et contredites", moyen, ENCRE)
    for (f, nom), y in zip(LES_FACONS, LES_RANGEES):
        c = cs[f]
        ecrire(70, y + 4, nom, petit, ENCRE)
        fb = X0 + round(c["bon"] / plus_l * (X1 - X0))
        ff = fb + round(c["faux"] / plus_l * (X1 - X0))
        if c["bon"]:
            art.rectangle([X0, y, fb, y + 22], fill=BLEU)
            traces["rectangles"].append((X0, fb, y, y + 22))
        if c["faux"]:
            art.rectangle([fb, y, ff, y + 22], fill=ALERTE)
            traces["rectangles"].append((fb, ff, y, y + 22))
        ecrire(ff + 8, y + 4, f"{c['bon']} + {c['faux']}", petit, ENCRE)
        traces["barres"].append((f, "lues", c["bon"], c["faux"]))
        for j, (cle, couleur) in enumerate((("validees", BLEU), ("contredites", ORANGE))):
            n = c[cle]
            yy = y + j * 14
            fin = Y0 + round(n / plus_v * (Y1 - Y0))
            art.rectangle([Y0, yy, fin, yy + 11], fill=couleur)
            traces["rectangles"].append((Y0, fin, yy, yy + 11))
            ecrire(fin + 6, yy - 1, str(n), petit, ENCRE)
            traces["barres"].append((f, cle, n, couleur))
    art.rectangle([Y0, 380, Y0 + 12, 392], fill=BLEU)
    ecrire(Y0 + 18, 380, "validées", petit, ENCRE)
    art.rectangle([Y0 + 110, 380, Y0 + 122, 392], fill=ORANGE)
    ecrire(Y0 + 128, 380, "contredites", petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(m)
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

    m = lire(mesure)
    d = m["d"]
    tmp = sortie.parent / ".sonde_400.png"
    try:
        _, poses, cadres, traces = dessiner(m, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(m))
    autre["d"]["le_verdict"] = {"decidable": True, "lissue": "x ; non"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "NON", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    b = d["le_bilan"]
    lues = {f: (bon, faux) for f, k, bon, faux in [t for t in traces["barres"] if t[1] == "lues"]}
    v("★★★★ les validées rognées et entières sont celles du bilan",
      [t[2] for t in traces["barres"] if t[1] == "validees"] == [d["la_reference_385"]["validees"], b["rognees"]["validees"], b["entieres"]["validees"]]
      and [t[2] for t in traces["barres"] if t[1] == "contredites"] == [d["la_reference_385"]["contredites"], b["rognees"]["contredites"],
                                                                         b["entieres"]["contredites"]])
    v("★★★★ les lues de 385 sont recomptées sur ses surfaces",
      lues["385"] == (sum(1 for c in m["d385"]["les_cotes"] for s in c["les_surfaces_avec_m7"] if s["lue"] and s["sur_le_bon_tour"]),
                      sum(1 for c in m["d385"]["les_cotes"] for s in c["les_surfaces_avec_m7"] if s["lue"] and not s["sur_le_bon_tour"])))
    v("★★★★ les lues rognées contiennent les validées lues du bilan", lues["rognees"][0] >= b["rognees"]["sur_le_bon_tour"]
      and lues["entieres"][0] >= b["entieres"]["sur_le_bon_tour"])
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande porte le verdict entier", la_bande(m)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    octets = tmp.read_bytes()
    dessiner(m, tmp)
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
                   / "400_des_chaines_rognees_lisent_elles_leurs_validees_sur_le_bon_tour_de_paris4.png")
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
