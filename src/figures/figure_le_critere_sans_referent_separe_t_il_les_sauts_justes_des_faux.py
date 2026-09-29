"""Sur les graines 4 à 8 de PHercParis4, chaque saut que la lecture stricte juge, placé par son pas médian et la part du plan qu'il pose, contre la boîte du critère sans référent de 328 ; et, chaîne par chaîne, la part des sauts justes et des sauts faux que le critère dit tenir.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, les sauts justes (gris) et faux (orange) des quatre chaînes, et la boîte où le
critère dit qu'un saut tient : si les points orange étaient hors de la boîte et les gris dedans, le critère séparerait les sauts ; s'ils
sont dedans les uns comme les autres, il ne les sépare pas. À droite, la part tenue des justes et des faux pour chaque chaîne, pour les
quatre ensemble, et, à côté, sur les graines 1 à 3, avec les deux bornes de la règle.

  uv run python src/figures/figure_le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.py \\
      --sortie docs/images/344_le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.png

⚠ Tout vient de la mesure de `344`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
GRIS_POINT = (150, 153, 158)
L_, H_ = 1360, 600
LA_BANDE = 510
LE_MAX_PAS, LE_MAX_PART = 2.5, 0.8
LES_GRAINES_PROPRES = (4, 5, 6, 7, 8)
LES_GROUPES = (("sans relance", "sans relance"), ("relancée depuis un point", "depuis un point"),
               ("relancée depuis la spire", "depuis la spire"), ("bornée", "bornée"), (None, "les quatre"), ("1 à 3", "graines 1 à 3"))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_sauts_juges(d: dict) -> list[tuple]:
    """Les sauts jugés des graines 4 à 8 : (chaîne, graine, côté, saut, pas médian, part du plan, faux)."""
    return [(n, g["le_rang"], c, s["le_saut"], s["le_pas_median_en_pas"], s["la_part_du_plan"], s["la_justesse"].startswith("faux"))
            for n, ch in d["les_chaines"].items() for g in ch["les_graines"] if g["le_rang"] in LES_GRAINES_PROPRES
            for c, x in g["les_cotes"].items() for s in x["les_sauts"] if s["la_justesse"] != "non jugé"]


def le_bilan_du_groupe(d: dict, cle) -> dict:
    if cle is None:
        return d["le_verdict"]
    if cle == "1 à 3":
        return d["les_bilans"]["graines_1_a_3"]
    return d["les_bilans"]["par_chaine"][cle]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    p = lambda x: f"{round(100 * x)} %"  # noqa: E731
    return (f"sur les graines 4 à 8, le critère sans référent tient {p(v['tj'])} des sauts justes et {p(v['tf'])} des sauts "
            f"faux").upper()


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "barres": [], "ecretes": 0, "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "gris : les sauts que la lecture stricte dit justes ; orange : ceux qu'elle dit faux ; les quatre chaînes de 340",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "chaque saut jugé des graines 4 à 8 : son pas médian et la part du plan qu'il pose", moyen, ENCRE)
    gx0, gx1, gy0, gy1 = x0 + 60, x1 - 20, y0 + 50, y1 - 45
    X = lambda p: gx0 + p / LE_MAX_PAS * (gx1 - gx0)  # noqa: E731
    Y = lambda q: gy1 - q / LE_MAX_PART * (gy1 - gy0)  # noqa: E731
    for q in (0.0, 0.2, 0.4, 0.6, 0.8):
        art.line([gx0, Y(q), gx1, Y(q)], fill=TRAIT)
        ecrire(x0 + 12, int(Y(q)) - 7, f"{int(q * 100)} %", 0, GRIS)
    for p in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5):
        ecrire(int(X(p)) - 8, gy1 + 6, f"{p:g}".replace(".", ","), 0, GRIS)
    ecrire(gx0 + 150, gy1 + 22, "le pas médian du saut, en pas du rouleau", 0, ENCRE)
    art.rectangle([X(0.5), Y(LE_MAX_PART), X(1.5), Y(0.1)], outline=ALERTE, width=2)
    ecrire(int(X(1.5)) + 8, int(Y(LE_MAX_PART)) + 4, "le critère : le saut tient", 0, ALERTE)
    ecrire(int(X(1.5)) + 8, int(Y(LE_MAX_PART)) + 18, "(10 % du plan, un demi à un pas et demi)", 0, ALERTE)
    sauts = les_sauts_juges(d)
    for faux in (False, True):
        for n, r, c, h, p, q, f in sauts:
            if f != faux:
                continue
            if not (0 <= p <= LE_MAX_PAS and 0 <= q <= LE_MAX_PART):
                traces["ecretes"] += 1
            cx, cy = X(min(p, LE_MAX_PAS)), Y(min(q, LE_MAX_PART))
            rr = 6 if f else 3
            art.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=ALERTE if f else GRIS_POINT, outline=ENCRE if f else None)
            traces["points"].append((n, r, c, h, p, q, f))
            traces["rectangles"].append((0, cx - rr, cx + rr, cy - rr, cy + rr))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des sauts que le critère dit tenir", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 28, "lignes : 75 % pour les justes et 25 % pour les faux (il les sépare)", 0, ALERTE)
    by0, by1 = y0 + 60, y1 - 70
    B = lambda q: by1 - q * (by1 - by0)  # noqa: E731
    for q in (0.0, 0.25, 0.5, 0.75, 1.0):
        art.line([x0 + 50, B(q), x1 - 10, B(q)], fill=TRAIT)
        ecrire(x0 + 10, int(B(q)) - 7, f"{int(q * 100)} %", 0, GRIS)
    for q in (0.25, 0.75):
        art.line([x0 + 50, B(q), x1 - 10, B(q)], fill=ALERTE, width=2)
    for k, (cle, nom) in enumerate(LES_GROUPES):
        b = le_bilan_du_groupe(d, cle)
        xa = x0 + 62 + k * 88
        for dx, n_, t_, col, genre in ((0, b["les_justes"], b["les_justes_qui_tiennent"], GRIS_POINT, "justes"),
                                       (26, b["les_faux"], b["les_faux_qui_tiennent"], ALERTE, "faux")):
            part = t_ / n_ if n_ else 0.0
            art.rectangle([xa + dx, B(part), xa + dx + 24, by1], fill=col)
            traces["barres"].append((nom, genre, t_, n_))
            traces["rectangles"].append((1, xa + dx, xa + dx + 24, B(part), by1))
        ecrire(xa, by1 + 6, f"{b['les_justes_qui_tiennent']}/{b['les_justes']}", 0, GRIS)
        ecrire(xa, by1 + 20, f"{b['les_faux_qui_tiennent']}/{b['les_faux']}", 0, ALERTE)
        for m, mot in enumerate(nom.split(" ", 1)):
            ecrire(xa, by1 + 38 + 14 * m, mot, 0, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    tete, _, suite = d["le_verdict"]["lissue"].rpartition(" ; ")
    ecrire(50, LA_BANDE + 10, f"LE VERDICT DÉCLARÉ : {tete} ;", petit, ENCRE)
    ecrire(50, LA_BANDE + 26, suite, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, "⚠ ce qui n'est PAS établi : ce que vaut le critère sur PHerc0358 ; six sauts faux seulement, et des chaînes "
           "parties des mêmes nappes.", moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_344.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"]["tj"], autre["le_verdict"]["tf"] = 0.5, 0.25
    v("★★★ le titre LIT la mesure", le_titre(autre).endswith("TIENT 50 % DES SAUTS JUSTES ET 25 % DES SAUTS FAUX"), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    juges = [(n, g["le_rang"], c, s["le_saut"]) for n, ch in d["les_chaines"].items() for g in ch["les_graines"]
             for c, x in g["les_cotes"].items() for s in x["les_sauts"] if g["le_rang"] >= 4 and s["la_justesse"] != "non jugé"]
    v("★★★★ un point par saut jugé des graines 4 à 8, et aucun autre", sorted(p[:4] for p in traces["points"]) == sorted(juges),
      f"{len(traces['points'])} points pour {len(juges)} sauts")
    v("★★★★ autant de points orange que de sauts faux dans le verdict",
      sum(p[6] for p in traces["points"]) == d["le_verdict"]["les_faux"], str(sum(p[6] for p in traces["points"])))
    def compte(chaines, graines):
        ss = [s for n, ch in d["les_chaines"].items() if n in chaines for g in ch["les_graines"] if g["le_rang"] in graines
              for x in g["les_cotes"].values() for s in x["les_sauts"]]
        j = [s["tient"] for s in ss if s["la_justesse"] == "juste"]
        f = [s["tient"] for s in ss if s["la_justesse"].startswith("faux")]
        return [("justes", sum(j), len(j)), ("faux", sum(f), len(f))]
    quatre = tuple(d["les_chaines"])
    attendues = [(nom, *b) for cle, nom in LES_GROUPES
                 for b in compte((cle,) if cle not in (None, "1 à 3") else quatre, (1, 2, 3) if cle == "1 à 3" else (4, 5, 6, 7, 8))]
    v("★★★★ chaque barre est la part tenue comptée à part dans la mesure, chaîne par chaîne, les quatre ensemble, et les graines 1 à 3",
      traces["barres"] == attendues, str([b for b, a in zip(traces["barres"], attendues) if b != a][:3]))
    v("★★★ les points orange sont posés après tous les gris, pour n'être cachés par aucun",
      [p[6] for p in traces["points"]] == sorted(p[6] for p in traces["points"]))
    v("★★★ rien n'est écrêté", traces["ecretes"] == 0, str(traces["ecretes"]))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
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
                   / "344_le_critere_sans_referent_separe_t_il_les_sauts_justes_des_faux.png")
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
