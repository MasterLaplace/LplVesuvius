"""Sur les graines 4 à 8, la part des points posés de chaque surface qui le sont sur le tour attendu, pour les sauts sains, à cheval et faux, selon que le compte de 345 et le seuil de 50 points à zéro les tiennent ou non.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, un point par surface, rangée par rangée ; le trait est 90 %. Les surfaces à
cheval tenues sont la rangée qui décide. À droite, les médianes de chaque rangée, et la part de tous les points posés de ce que le critère
tient qui le sont sur le tour attendu.

  uv run python src/figures/figure_les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.py \\
      --sortie docs/images/353_les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.png

⚠ Tout vient de la mesure de `353`.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (glyphes_manquants, police,  # noqa: E402
                            textes_debordants, textes_hors_cadre, textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LA_MESURE = RACINE / "docs" / "mesures" / "les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
GRIS_POINT = (150, 153, 158)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_RANGEES = (("les_sains_tenus", "sains, tenus", BLEU), ("les_sains_refuses", "sains, refusés", GRIS_POINT),
               ("les_a_cheval_tenus", "à cheval, tenus", ALERTE), ("les_a_cheval_refuses", "à cheval, refusés", GRIS_POINT),
               ("les_faux_tenus", "faux, tenus", ENCRE), ("les_faux_refuses", "faux, refusés", GRIS_POINT))
PG, PD = 220, 660
LE_BAS_DE_LECHELLE = 0.1


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return (f"à cheval et tenues : {round(100 * v['la_mediane_des_tenues'])} % sur le tour attendu en médiane ; refusées : "
            f"{round(100 * v['la_mediane_des_refusees'])} %").upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    t = d["les_parts"]["tout_ce_qui_est_tenu"]
    s = d["les_parts"]["les_sains_tenus"]
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : sur tout ce que le critère tient, {t['sur_le_tour_attendu']} des {t['les_points_poses']} "
            f"points posés sont sur le tour attendu ; les {len(s)} surfaces saines tenues le sont à {round(100 * min(s))} % au moins")
    trois = "⚠ ce qui n'est PAS établi : où, sur une surface, sont les points hors du tour attendu, ni ce que vaut tout ceci sur PHerc0358."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "lignes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "la part des points posés de chaque surface qui le sont sur le tour attendu", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "surface par surface, graines 4 à 8", moyen, ENCRE)
    X = lambda p: PG + (p - LE_BAS_DE_LECHELLE) / (1 - LE_BAS_DE_LECHELLE) * (PD - PG)  # noqa: E731
    haut, bas = y0 + 44, y1 - 70
    traces["zone"] = (haut, bas)
    art.line([X(0.9), haut, X(0.9), bas], fill=ALERTE, width=2)
    for p in (0.1, 0.25, 0.5, 0.75, 0.9, 1.0):
        ecrire(int(X(p)) - 10, bas + 4, f"{int(round(100 * p))} %", 0, ALERTE if p == 0.9 else GRIS)
    ecrire(PG, y1 - 44, "sur le tour attendu, en part des points posés", 0, ENCRE)
    ys = {k: haut + 25 + 50 * i for i, (k, _, _) in enumerate(LES_RANGEES)}
    for k, nom, couleur in LES_RANGEES:
        ecrire(x0 + 12, ys[k] - 7, nom, 0, ENCRE)
        art.line([PG, ys[k], PD, ys[k]], fill=TRAIT)
        for i, p in enumerate(d["les_parts"][k]):
            cx, cy = X(p), ys[k] + ((i * 37) % 21 - 10)
            art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=couleur)
            traces["points"].append((k, p, cx))
            traces["rectangles"].append((0, cx - 4, cx + 4, cy - 4, cy + 4))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les médianes, rangée par rangée", moyen, ENCRE)
    cols = (x0 + 12, x0 + 200, x0 + 300, x0 + 400)
    for c, t in zip(cols, ("rangée", "surfaces", "médiane", "plus basse")):
        ecrire(c, y0 + 44, t, 0, GRIS)
    y = y0 + 68
    for k, nom, _ in LES_RANGEES:
        xs = d["les_parts"][k]
        cel = (nom, str(len(xs)), f"{round(100 * statistics.median(xs))} %" if xs else "-", f"{round(100 * min(xs))} %" if xs else "-")
        for c, t in zip(cols, cel):
            ecrire(c, y, t, 0, ALERTE if k == "les_a_cheval_tenus" else ENCRE)
        traces["lignes"].append((k, cel))
        y += 22
    t = d["les_parts"]["tout_ce_qui_est_tenu"]
    ecrire(x0 + 12, y + 24, "sur tout ce que le critère tient :", 0, ENCRE)
    ecrire(x0 + 12, y + 42, f"{t['sur_le_tour_attendu']} des {t['les_points_poses']} points posés sur le tour attendu, "
                            f"soit {round(100 * t['la_part'])} %", 0, ENCRE)

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
    tmp = sortie.parent / ".sonde_353.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"].update({"la_mediane_des_tenues": 0.5, "la_mediane_des_refusees": 0.25})
    v("★★★ le titre LIT la mesure", le_titre(autre) == "À CHEVAL ET TENUES : 50 % SUR LE TOUR ATTENDU EN MÉDIANE ; REFUSÉES : 25 %",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ un point par surface de chaque rangée, et aucun autre",
      all(sorted(p for k2, p, _ in traces["points"] if k2 == k) == sorted(d["les_parts"][k]) for k, _, _ in LES_RANGEES)
      and len(traces["points"]) == sum(len(d["les_parts"][k]) for k, _, _ in LES_RANGEES))
    v("★★★★ chaque point est à sa part", all(abs(cx - (PG + (p - 0.1) / 0.9 * (PD - PG))) < 0.5 for _, p, cx in traces["points"]))
    v("★★★★ aucune part n'est sous le bas de l'échelle", all(p >= LE_BAS_DE_LECHELLE for _, p, _ in traces["points"]))
    t_, r_ = d["les_parts"]["les_a_cheval_tenus"], d["les_parts"]["les_a_cheval_refuses"]
    v("★★★★ les médianes des surfaces à cheval sont celles du verdict",
      not d["le_verdict"].get("decidable") or (abs(statistics.median(t_) - d["le_verdict"]["la_mediane_des_tenues"]) < 1e-4
                                               and abs(statistics.median(r_) - d["le_verdict"]["la_mediane_des_refusees"]) < 1e-4))
    v("★★★★ le tableau porte le nombre, la médiane et la plus basse de chaque rangée, recomptés",
      all(cel == (dict((k2, n) for k2, n, _ in LES_RANGEES)[k], str(len(d["les_parts"][k])),
                  f"{round(100 * statistics.median(d['les_parts'][k]))} %" if d["les_parts"][k] else "-",
                  f"{round(100 * min(d['les_parts'][k]))} %" if d["les_parts"][k] else "-") for k, cel in traces["lignes"]))
    t = d["les_parts"]["tout_ce_qui_est_tenu"]
    v("★★★★ la bande rapporte à côté tout ce qui est tenu, recompté",
      f"{t['sur_le_tour_attendu']} des {t['les_points_poses']} points posés sont sur le tour attendu" in " ".join(la_bande(d))
      and abs(t["la_part"] - t["sur_le_tour_attendu"] / t["les_points_poses"]) < 1e-4)
    s_ = d["les_parts"]["les_sains_tenus"]
    v("★★★ la bande donne la plus basse part des surfaces saines tenues, recomptée",
      f"les {len(s_)} surfaces saines tenues le sont à {round(100 * sorted(s_)[0])} % au moins" in " ".join(la_bande(d)))
    haut, bas = traces["zone"]
    v("★★★★ chaque point est dans la zone du graphe", all(haut < r[3] and r[4] < bas for r in traces["rectangles"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t2, font=f) for x, y, t2, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucun point ne passe sous un texte", not sous, str(sous[:3]))
    txt = " ".join(t2 for _, _, t2, _ in poses)
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
                   / "353_les_surfaces_a_cheval_tenues_sont_elles_presque_entierement_sur_leur_tour.png")
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
