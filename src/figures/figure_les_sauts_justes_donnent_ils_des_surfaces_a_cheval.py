"""Sur les graines 4 à 8, chaîne par chaîne, combien de sauts justes donnent une surface à cheval sur le tour attendu et son voisin, et, sous chacune, la part de ses points restés ou partis au-delà que le compte de 345 compte comme leur place le veut.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, une barre par chaîne : la part foncée est celle des sauts justes qui donnent
une surface à cheval. À droite, un point par surface à cheval, à la part que le compte voit ; le trait est les trois quarts, et les points
orange sont les surfaces sous lesquelles le compte voit le changement.

  uv run python src/figures/figure_les_sauts_justes_donnent_ils_des_surfaces_a_cheval.py \\
      --sortie docs/images/349_les_sauts_justes_donnent_ils_des_surfaces_a_cheval.png

⚠ Tout vient de la mesure de `349`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_sauts_justes_donnent_ils_des_surfaces_a_cheval.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
CLAIR = (212, 210, 205)
GRIS_POINT = (150, 153, 158)
L_, H_ = 1360, 600
LA_BANDE = 510
LE_SEUIL = 0.75
LES_CHAINES = ("sans relance", "relancée depuis un point", "relancée depuis la spire", "bornée")
BG, BD = 250, 650
PG, PD = 900, 1270


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_justes(d: dict) -> list[dict]:
    return [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_justesse"] == "juste"]


def a_cheval(s: dict) -> bool:
    return s["la_surface"] is not None and s["la_surface"]["a_cheval"]


def la_part_vue(a: dict) -> float:
    """La plus petite part vue des groupes d'au moins 50 points : celle qui décide si le compte voit le changement."""
    return min(g["la_part_vue"] for g in (a["restes"], a["au_dela"]) if g["la_part_vue"] is not None)


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"{v['n']} des {v['N']} sauts justes donnent une surface à cheval ; le compte en voit {v['k']}".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    v = d["le_verdict"]
    comptes: dict[str, int] = {}
    for s in les_justes(d):
        if a_cheval(s):
            for k, n in s["la_surface"]["restes"]["les_comptes"].items():
                comptes[k] = comptes.get(k, 0) + n
    total = sum(comptes.values())
    un = f"LE VERDICT DÉCLARÉ : {v['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : des {total} points restés sous ces surfaces, {comptes.get('1', 0)} franchissent une "
            f"feuille, {comptes.get('0', 0)} aucune, et {comptes.get('non compté', 0)} ne sont pas comptés")
    trois = "⚠ ce qui n'est PAS établi : si le retard naît au saut qui le montre, ou s'il vient d'une surface de départ déjà restée en arrière."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "points": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "à cheval : au moins 50 points restés sur le tour de départ, ou partis au-delà du tour attendu", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les sauts justes, chaîne par chaîne", moyen, ENCRE)
    justes = les_justes(d)
    y = y0 + 70
    for n in LES_CHAINES:
        js = [s for s in justes if s["la_chaine"] == n]
        k = sum(1 for s in js if a_cheval(s))
        ecrire(x0 + 12, y + 1, n, 0, ENCRE)
        w = (BD - BG) * (k / len(js) if js else 0.0)
        art.rectangle([BG, y, BD, y + 16], fill=CLAIR)
        if w:
            art.rectangle([BG, y, BG + w, y + 16], fill=BLEU)
        traces["rectangles"].append((0, BG, BD, y, y + 16))
        traces["barres"].append((n, k, len(js), w))
        ecrire(BG, y + 20, f"{k} à cheval sur {len(js)}", 0, GRIS)
        y += 80
    ecrire(x0 + 12, y1 - 28, "foncé : la surface est à cheval ; clair : elle ne l'est pas", 0, GRIS)

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "sous chaque surface à cheval, ce que voit le compte", moyen, ENCRE)
    X = lambda p: PG + p * (PD - PG)  # noqa: E731
    haut, bas = y0 + 60, y1 - 70
    traces["zone"] = (haut, bas)
    art.line([X(LE_SEUIL), haut, X(LE_SEUIL), bas], fill=ALERTE, width=2)
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        ecrire(int(X(p)) - 10, bas + 4, f"{int(p * 100)} %", 0, ALERTE if p == LE_SEUIL else GRIS)
    ecrire(PG, y1 - 44, "la part comptée comme la place le veut", 0, ENCRE)
    ys = {n: haut + 30 + 75 * i for i, n in enumerate(LES_CHAINES[1:])}
    for n, yr in ys.items():
        ecrire(x0 + 12, yr - 7, n, 0, ENCRE)
        art.line([PG, yr, PD, yr], fill=TRAIT)
    k_ = {n: 0 for n in ys}
    for s in justes:
        if not a_cheval(s) or s["la_chaine"] not in ys:
            continue
        p = la_part_vue(s["la_surface"])
        vu = bool(s["la_surface"]["vu"])
        cx, cy = X(p), ys[s["la_chaine"]] + ((k_[s["la_chaine"]] * 37) % 41 - 20)
        k_[s["la_chaine"]] += 1
        rr = 6 if vu else 4
        art.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=ALERTE if vu else GRIS_POINT, outline=ENCRE if vu else None)
        traces["points"].append((s["la_chaine"], s["le_rang"], s["le_saut"], p, vu))
        traces["rectangles"].append((1, cx - rr, cx + rr, cy - rr, cy + rr))

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
    tmp = sortie.parent / ".sonde_349.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "n": 7, "N": 9, "k": 2, "lissue": "x ; y"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "7 DES 9 SAUTS JUSTES DONNENT UNE SURFACE À CHEVAL ; LE COMPTE EN VOIT 2",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : une lecture a échoué (x)"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : UNE LECTURE A ÉCHOUÉ (X)", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    justes = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_justesse"] == "juste"]
    par = {n: (sum(1 for s in justes if s["la_chaine"] == n and s["la_surface"] is not None and s["la_surface"]["a_cheval"]),
               sum(1 for s in justes if s["la_chaine"] == n)) for n in LES_CHAINES}
    v("★★★★ chaque barre porte ses sauts justes à cheval, recomptés, à leur part",
      all(par[n] == (k, t) and abs(w - (BD - BG) * k / t) < 0.5 for n, k, t, w in traces["barres"]) and len(traces["barres"]) == 4,
      str(traces["barres"]))
    v("★★★★ les barres somment au verdict", not d["le_verdict"].get("decidable")
      or (sum(b[1] for b in traces["barres"]), sum(b[2] for b in traces["barres"])) == (d["le_verdict"]["n"], d["le_verdict"]["N"]))
    attendus = sorted((s["la_chaine"], s["le_rang"], s["le_saut"]) for s in justes
                      if s["la_surface"] is not None and s["la_surface"]["a_cheval"] and s["la_chaine"] != "sans relance")
    v("★★★★ un point par surface à cheval des chaînes relancées, et aucun autre", sorted(p[:3] for p in traces["points"]) == attendus,
      str(len(traces["points"])))
    v("★★★★ les points orange sont les surfaces que le compte voit, autant que le verdict en compte",
      sum(p[4] for p in traces["points"]) == d["le_verdict"].get("k", -1)
      and all(p[4] == (p[3] >= LE_SEUIL) for p in traces["points"]), str([p for p in traces["points"] if p[4]]))
    v("★★★ aucune surface à cheval n'est dans la chaîne sans relance, qui n'a pas de rangée", par["sans relance"][0] == 0)
    parts = {(s["la_chaine"], s["le_rang"], s["le_saut"]): sorted(g["la_part_vue"] for g in (s["la_surface"]["restes"], s["la_surface"]["au_dela"])
                                                                  if g["les_points"] >= 50)[0]
             for s in justes if s["la_surface"] is not None and s["la_surface"]["a_cheval"]}
    v("★★★★ chaque point est à la plus petite part de ses groupes, celle qui décide",
      all(abs(p[3] - parts[p[:3]]) < 1e-9 for p in traces["points"]), str([p for p in traces["points"] if abs(p[3] - parts[p[:3]]) >= 1e-9][:2]))
    tot = {}
    for s in justes:
        if s["la_surface"] is not None and s["la_surface"]["a_cheval"]:
            for k, n in s["la_surface"]["restes"]["les_comptes"].items():
                tot[k] = tot.get(k, 0) + n
    v("★★★★ la bande rapporte à côté les points restés, recomptés",
      f"des {sum(tot.values())} points restés sous ces surfaces, {tot.get('1', 0)} franchissent une feuille, {tot.get('0', 0)} aucune"
      in " ".join(la_bande(d)))
    haut, bas = traces["zone"]
    v("★★★★ chaque point est dans la zone du graphe", all(haut < r[3] and r[4] < bas for r in traces["rectangles"] if r[0] == 1))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucune barre ni aucun point ne passe sous un texte", not sous, str(sous[:3]))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images" / "349_les_sauts_justes_donnent_ils_des_surfaces_a_cheval.png")
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
