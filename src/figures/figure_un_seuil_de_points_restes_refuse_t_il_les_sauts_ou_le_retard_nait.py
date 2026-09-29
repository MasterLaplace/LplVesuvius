"""Sur les graines 4 à 8, le nombre de points que le compte de 345 dit à zéro feuille, saut par saut, pour les naissances du retard, les sauts justes sains, les sauts à cheval hérités et les sauts faux ; et la part refusée selon le seuil.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, un point par saut, groupe par groupe, à son nombre de points à zéro ; le trait
est le seuil de 50 : à sa droite, le saut est refusé. À droite, la part refusée de chaque groupe pour des seuils de 10 à 150 points.

  uv run python src/figures/figure_un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.py \\
      --sortie docs/images/351_un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.png

⚠ Tout vient de la mesure de `351`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
GRIS_POINT = (150, 153, 158)
VIOLET = (150, 110, 150)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_GROUPES = (("les_naissances", "naissances du retard", ALERTE), ("les_sains", "sauts justes sains", BLEU),
               ("les_herites", "sauts à cheval hérités", GRIS_POINT), ("les_faux", "sauts faux", VIOLET))
LE_MAX = 320
PG, PD = 250, 660
CG, CD = 790, 1270


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    b, s = d["les_bilans"], d["les_constantes"]["le_seuil"]
    return (f"{s} points à zéro refusent {b['les_naissances']['les_refuses']} des {b['les_naissances']['les_sauts']} naissances et "
            f"{b['les_sains']['les_refuses']} des {b['les_sains']['les_sauts']} sauts sains").upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    b = d["les_bilans"]
    r = d["les_restes_des_naissances"]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : il refuse {b['les_herites']['les_refuses']} des {b['les_herites']['les_sauts']} sauts à "
            f"cheval hérités et {b['les_faux']['les_refuses']} des {b['les_faux']['les_sauts']} sauts faux ; aux naissances, "
            f"{r['a_zero']} des {r['les_points']} points restés sont à zéro")
    trois = "⚠ ce qui n'est PAS établi : ce que vaut ce seuil sur PHerc0358, où une surface peut être plus grande ou plus petite."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "courbes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    seuil = d["les_constantes"]["le_seuil"]
    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "un saut est refusé si au moins 50 de ses points ne franchissent aucune feuille pour le compte de 345", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les points à zéro, saut par saut", moyen, ENCRE)
    X = lambda z: PG + min(z, LE_MAX) / LE_MAX * (PD - PG)  # noqa: E731
    haut, bas = y0 + 50, y1 - 70
    traces["zone"] = (haut, bas)
    art.line([X(seuil), haut, X(seuil), bas], fill=ALERTE, width=2)
    for z in (0, 50, 100, 150, 200, 250, 300):
        ecrire(int(X(z)) - 8, bas + 4, str(z), 0, ALERTE if z == seuil else GRIS)
    ecrire(PG, y1 - 44, "les points que le compte dit à zéro feuille", 0, ENCRE)
    ys = {k: haut + 40 + 75 * i for i, (k, _, _) in enumerate(LES_GROUPES)}
    for k, nom, couleur in LES_GROUPES:
        ecrire(x0 + 12, ys[k] - 7, nom, 0, ENCRE)
        art.line([PG, ys[k], PD, ys[k]], fill=TRAIT)
        for i, z in enumerate(d["les_zeros"][k]):
            cx, cy = X(z), ys[k] + ((i * 37) % 41 - 20)
            art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=couleur)
            traces["points"].append((k, z, cx))
            traces["rectangles"].append((0, cx - 4, cx + 4, cy - 4, cy + 4))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part refusée, selon le seuil", moyen, ENCRE)
    seuils = sorted(int(t) for t in d["par_seuil"])
    Xs = lambda t: CG + (t - seuils[0]) / (seuils[-1] - seuils[0]) * (CD - CG)  # noqa: E731
    Y = lambda p: bas - p * (bas - haut)  # noqa: E731
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        art.line([CG, Y(p), CD, Y(p)], fill=TRAIT)
        ecrire(CG - 40, int(Y(p)) - 7, f"{int(p * 100)} %", 0, GRIS)
    for t in seuils:
        ecrire(int(Xs(t)) - 8, bas + 4, str(t), 0, ALERTE if t == seuil else GRIS)
    art.line([Xs(seuil), haut, Xs(seuil), bas], fill=ALERTE, width=1)
    for k, nom, couleur in LES_GROUPES:
        pts = [(Xs(t), Y(d["par_seuil"][str(t)][k]["la_part"])) for t in seuils]
        art.line(pts, fill=couleur, width=3 if k in ("les_naissances", "les_sains") else 1)
        traces["courbes"].append((k, [d["par_seuil"][str(t)][k]["la_part"] for t in seuils], pts))
    ecrire(CG, y1 - 44, "le seuil, en points à zéro", 0, ENCRE)
    lx = x0 + 12
    for k, nom, couleur in LES_GROUPES:
        art.rectangle([lx, y1 - 22, lx + 10, y1 - 14], fill=couleur)
        traces["rectangles"].append((1, lx, lx + 10, y1 - 22, y1 - 14))
        ecrire(lx + 14, y1 - 25, nom, 0, ENCRE)
        lx += 14 + int(art.textlength(nom, font=petit)) + 18

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
    tmp = sortie.parent / ".sonde_351.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["les_bilans"]["les_naissances"].update({"les_refuses": 3, "les_sauts": 9})
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("50 POINTS À ZÉRO REFUSENT 3 DES 9 NAISSANCES"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ un point par saut de chaque groupe, et aucun autre",
      all(sorted(z for k2, z, _ in traces["points"] if k2 == k) == sorted(d["les_zeros"][k]) for k, _, _ in LES_GROUPES)
      and len(traces["points"]) == sum(len(v_) for v_ in d["les_zeros"].values()))
    v("★★★★ chaque point est à son nombre de points à zéro",
      all(abs(cx - (PG + min(z, LE_MAX) / LE_MAX * (PD - PG))) < 0.5 for _, z, cx in traces["points"]))
    s = d["les_constantes"]["le_seuil"]
    v("★★★★ à droite du seuil, autant de points que le bilan refuse, groupe par groupe",
      all(sum(1 for k2, z, _ in traces["points"] if k2 == k and z >= s) == d["les_bilans"][k]["les_refuses"] for k, _, _ in LES_GROUPES))
    v("★★★★ aucun saut n'a plus de points à zéro que l'échelle n'en montre", max(z for _, z, _ in traces["points"]) <= LE_MAX)
    v("★★★★ chaque courbe passe par les parts refusées recomptées",
      all(parts == [round(sum(1 for z in d["les_zeros"][k] if z >= int(t)) / len(d["les_zeros"][k]), 4)
                    for t in sorted(d["par_seuil"], key=int)] for k, parts, _ in traces["courbes"]))
    h_, b_ = traces["zone"]
    v("★★★★ chaque courbe est dessinée à ses parts", all(abs(y - (b_ - p * (b_ - h_))) < 0.5 for _, parts, pts in traces["courbes"]
                                                        for p, (_, y) in zip(parts, pts)) and len(traces["courbes"]) == 4)
    b = d["les_bilans"]
    v("★★★★ la bande rapporte à côté les hérités et les faux, recomptés",
      f"il refuse {b['les_herites']['les_refuses']} des {len(d['les_zeros']['les_herites'])} sauts à cheval hérités et "
      f"{b['les_faux']['les_refuses']} des {len(d['les_zeros']['les_faux'])} sauts faux" in " ".join(la_bande(d)))
    haut, bas = traces["zone"]
    v("★★★★ chaque point est dans la zone du graphe", all(haut < r[3] and r[4] < bas for r in traces["rectangles"] if r[0] == 0))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucun point ne passe sous un texte", not sous, str(sous[:3]))
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
                   / "351_un_seuil_de_points_restes_refuse_t_il_les_sauts_ou_le_retard_nait.png")
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
