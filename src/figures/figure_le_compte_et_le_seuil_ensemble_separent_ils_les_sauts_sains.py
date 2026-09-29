"""Sur les graines 4 à 8, la part des sauts justes sains et la part des autres (sauts à cheval et sauts faux) que tiennent le compte de 345 et le seuil de 50 points à zéro, ensemble et chacun seul.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, pour chaque critère, deux barres : les sauts sains tenus, les autres tenus ; le
trait haut est les trois quarts, que les sains doivent atteindre, le trait bas le quart, sous lequel les autres doivent rester. À droite,
les comptes, groupe par groupe.

  uv run python src/figures/figure_le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.py \\
      --sortie docs/images/352_le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.png

⚠ Tout vient de la mesure de `352`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_CRITERES = (("les_deux", "le compte et le seuil"), ("345_seul", "le compte de 345 seul"), ("le_seuil_seul", "le seuil seul"))
HAUT, BAS = 140, 400


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b = d["les_bilans"]["graines_4_a_8"]["les_deux"]
    return (f"ensemble, ils tiennent {b['les_sains']['les_tenus']} des {b['les_sains']['les_sauts']} sauts sains et "
            f"{b['les_autres']['les_tenus']} des {b['les_autres']['les_sauts']} autres").upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    b = d["les_bilans"]
    s1, s3 = b["graines_4_a_8"]["345_seul"], b["graines_1_a_3"]["les_deux"]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : le compte de 345 seul tient {s1['les_autres']['les_tenus']} des "
            f"{s1['les_autres']['les_sauts']} autres ; sur les graines 1 à 3, les deux ensemble tiennent {s3['les_faux']['les_tenus']} des "
            f"{s3['les_faux']['les_sauts']} sauts faux")
    trois = "⚠ ce qui n'est PAS établi : ce que vaut ce critère sur PHerc0358, ni ce qu'une chaîne qui refuse ces sauts ferait ensuite."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "lignes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "un saut tient si 345 le tient et s'il a moins de 50 points à zéro ; les autres : les sauts à cheval et les sauts faux",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des sauts tenus, graines 4 à 8", moyen, ENCRE)
    Y = lambda p: BAS - p * (BAS - HAUT)  # noqa: E731
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        art.line([x0 + 60, Y(p), x1 - 20, Y(p)], fill=ALERTE if p in (0.25, 0.75) else TRAIT, width=2 if p in (0.25, 0.75) else 1)
        ecrire(x0 + 16, int(Y(p)) - 7, f"{int(p * 100)} %", 0, ALERTE if p in (0.25, 0.75) else GRIS)
    b48 = d["les_bilans"]["graines_4_a_8"]
    x = x0 + 100
    for cle, nom in LES_CRITERES:
        for k, (groupe, couleur) in enumerate((("les_sains", BLEU), ("les_autres", ALERTE))):
            p = b48[cle][groupe]["la_part"]
            bx = x + k * 56
            art.rectangle([bx, Y(p), bx + 44, BAS], fill=couleur)
            traces["barres"].append((cle, groupe, p, Y(p)))
            traces["rectangles"].append((0, bx, bx + 44, Y(p), BAS))
        ecrire(x, BAS + 8, nom, 0, ENCRE)
        x += 185
    art.rectangle([x0 + 100, y1 - 30, x0 + 112, y1 - 20], fill=BLEU)
    ecrire(x0 + 118, y1 - 32, "sauts justes sains", 0, ENCRE)
    art.rectangle([x0 + 260, y1 - 30, x0 + 272, y1 - 20], fill=ALERTE)
    ecrire(x0 + 278, y1 - 32, "autres : à cheval et faux", 0, ENCRE)
    traces["rectangles"] += [(0, x0 + 100, x0 + 112, y1 - 30, y1 - 20), (0, x0 + 260, x0 + 272, y1 - 30, y1 - 20)]

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les sauts tenus, groupe par groupe", moyen, ENCRE)
    cols = (x0 + 12, x0 + 200, x0 + 310, x0 + 420)
    for c, t in zip(cols, ("graines 4 à 8", "ensemble", "345 seul", "seuil seul")):
        ecrire(c, y0 + 44, t, 0, GRIS)
    y = y0 + 68
    for graines, titre in (("graines_4_a_8", None), ("graines_1_a_3", "graines 1 à 3, à côté")):
        if titre:
            y += 12
            ecrire(cols[0], y, titre, 0, GRIS)
            y += 22
        for groupe, nom in (("les_sains", "sauts justes sains"), ("les_a_cheval", "sauts justes à cheval"), ("les_faux", "sauts faux")):
            b = d["les_bilans"][graines]
            cellules = [nom] + [f"{b[c][groupe]['les_tenus']} sur {b[c][groupe]['les_sauts']}" for c, _ in LES_CRITERES]
            for c, t in zip(cols, cellules):
                ecrire(c, y, t, 0, ENCRE)
            traces["lignes"].append((graines, groupe, cellules[1:]))
            y += 22

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
    tmp = sortie.parent / ".sonde_352.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["les_bilans"]["graines_4_a_8"]["les_deux"]["les_sains"]["les_tenus"] = 11
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("ENSEMBLE, ILS TIENNENT 11 DES"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    b48 = d["les_bilans"]["graines_4_a_8"]
    recompte = {(c, g): (b48[c][g]["les_tenus"] / b48[c][g]["les_sauts"]) for c, _ in LES_CRITERES for g in ("les_sains", "les_autres")}
    v("★★★★ chaque barre monte à la part tenue, recomptée", len(traces["barres"]) == 6
      and all(abs(y - (BAS - recompte[(c, g)] * (BAS - HAUT))) < 0.5 for c, g, _, y in traces["barres"]), str(traces["barres"]))
    v("★★★★ les autres sont les sauts à cheval et les faux ensemble",
      all(b48[c]["les_autres"]["les_tenus"] == b48[c]["les_a_cheval"]["les_tenus"] + b48[c]["les_faux"]["les_tenus"]
          and b48[c]["les_autres"]["les_sauts"] == b48[c]["les_a_cheval"]["les_sauts"] + b48[c]["les_faux"]["les_sauts"]
          for c, _ in LES_CRITERES))
    v("★★★★ le tableau porte les comptes de chaque groupe et de chaque critère",
      all(cel == [f"{d['les_bilans'][g][c][gr]['les_tenus']} sur {d['les_bilans'][g][c][gr]['les_sauts']}" for c, _ in LES_CRITERES]
          for g, gr, cel in traces["lignes"]) and len(traces["lignes"]) == 6)
    v("★★★★ les barres des deux ensemble portent ce que dit le verdict", not d["le_verdict"].get("decidable")
      or (f"tiennent {b48['les_deux']['les_sains']['les_tenus']} des {b48['les_deux']['les_sains']['les_sauts']} sauts justes sains et "
          f"{b48['les_deux']['les_autres']['les_tenus']} des {b48['les_deux']['les_autres']['les_sauts']} autres") in d["le_verdict"]["lissue"])
    v("★★★★ la bande rapporte à côté les comptes recomptés",
      f"le compte de 345 seul tient {b48['345_seul']['les_autres']['les_tenus']} des {b48['345_seul']['les_autres']['les_sauts']} autres"
      in " ".join(la_bande(d)))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucune barre ne passe sous un texte", not sous, str(sous[:3]))
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
                   / "352_le_compte_et_le_seuil_ensemble_separent_ils_les_sauts_sains.png")
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
