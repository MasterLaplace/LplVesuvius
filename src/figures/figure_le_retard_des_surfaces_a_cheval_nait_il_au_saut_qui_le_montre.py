"""Sous chaque surface juste à cheval des graines 4 à 8, la part des pieds de ses points restés qui sont sur le tour d'avant ; et, à côté, où sont ces pieds au premier saut à cheval de chaque chaîne et aux sauts suivants.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, un point par surface lue, chaîne par chaîne, à la part héritée ; les deux traits
sont le quart et les trois quarts : à droite du second le retard est hérité, à gauche du premier il est né ici. À droite, deux barres : les
pieds des points restés au premier saut à cheval de chaque chaîne et de chaque graine, et aux sauts suivants, sur le tour de départ ou sur
le tour d'avant.

  uv run python src/figures/figure_le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.py \\
      --sortie docs/images/350_le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.png

⚠ Tout vient de la mesure de `350`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.json"

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
LES_SEUILS = (0.25, 0.75)
LES_CHAINES = ("relancée depuis un point", "relancée depuis la spire", "bornée")
PG, PD = 280, 660
BG, BD = 900, 1270


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_cheval(d: dict) -> list[dict]:
    m = d["les_constantes"]["le_minimum"]
    return [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_justesse"] == "juste" and s["la_surface"] is not None
            and s["la_surface"]["les_restes"] >= m]


def premiers_et_suivants(d: dict) -> tuple[list[dict], list[dict]]:
    """Les surfaces à cheval au premier saut à cheval de leur chaîne et de leur graine, et les autres."""
    prem = {(p["la_chaine"], p["le_rang"], p["le_cote"]): p["le_premier_saut"] for p in d["les_premiers"]}
    c = les_cheval(d)
    p = [s for s in c if s["le_saut"] == prem[(s["la_chaine"], s["le_rang"], s["le_cote"])]]
    return p, [s for s in c if s not in p]


def les_pieds(surfaces: list[dict]) -> tuple[int, int]:
    return (sum(s["la_surface"]["pieds_sur_le_tour_de_depart"] for s in surfaces),
            sum(s["la_surface"]["pieds_sur_le_tour_davant"] for s in surfaces))


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    _, _, suite = v["lissue"].rpartition(" ; ")
    return f"hérité sous {v['h']} des {v['n']} surfaces lues, né ici sous {v['i']} ; {suite}".upper()


def la_bande(d: dict) -> tuple[str, str, str]:
    v = d["le_verdict"]
    p, a = premiers_et_suivants(d)
    (pd, pa), (ad, aa) = les_pieds(p), les_pieds(a)
    un = f"LE VERDICT DÉCLARÉ : {v['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : au premier saut à cheval de chaque chaîne, {pd} pieds sur le tour de départ contre "
            f"{pa} sur le tour d'avant ; aux sauts suivants, {ad} contre {aa}")
    trois = "⚠ ce qui n'est PAS établi : si le compte de 345 voit le retard au saut où il naît."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"points": [], "barres": [], "rectangles": [], "abscisses": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sous les surfaces justes à cheval : le pied d'un point resté est-il sur le tour de départ, ou sur le tour d'avant ?",
           petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "la part des pieds sur le tour d'avant, surface par surface", moyen, ENCRE)
    X = lambda p: PG + p * (PD - PG)  # noqa: E731
    haut, bas = y0 + 50, y1 - 70
    traces["zone"] = (haut, bas)
    for p in LES_SEUILS:
        art.line([X(p), haut, X(p), bas], fill=ALERTE, width=2)
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        ecrire(int(X(p)) - 10, bas + 4, f"{int(p * 100)} %", 0, ALERTE if p in LES_SEUILS else GRIS)
    ecrire(PG, y1 - 44, "à gauche du quart : né ici ; à droite des trois quarts : hérité", 0, ENCRE)
    ys = {n: haut + 50 + 100 * i for i, n in enumerate(LES_CHAINES)}
    for n, yr in ys.items():
        ecrire(x0 + 12, yr - 7, n, 0, ENCRE)
        art.line([PG, yr, PD, yr], fill=TRAIT)
    k_ = {n: 0 for n in ys}
    for s in les_cheval(d):
        p = s["la_surface"]["la_part_heritee"]
        if p is None:
            continue
        cx, cy = X(p), ys[s["la_chaine"]] + ((k_[s["la_chaine"]] * 37) % 41 - 20)
        k_[s["la_chaine"]] += 1
        art.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GRIS_POINT)
        traces["points"].append((s["la_chaine"], s["le_rang"], s["le_saut"], p))
        traces["abscisses"].append((p, cx))
        traces["rectangles"].append((0, cx - 4, cx + 4, cy - 4, cy + 4))

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "où sont les pieds, à la naissance et après", moyen, ENCRE)
    p, a = premiers_et_suivants(d)
    y = y0 + 90
    for nom, groupe in ((f"premier saut à cheval ({len(p)} surfaces)", p), (f"sauts suivants ({len(a)} surfaces)", a)):
        dep, av = les_pieds(groupe)
        ecrire(x0 + 12, y - 22, nom, 0, ENCRE)
        w = (BD - BG) * dep / (dep + av) if dep + av else 0.0
        art.rectangle([BG, y, BG + w, y + 18], fill=BLEU)
        art.rectangle([BG + w, y, BD, y + 18], fill=ALERTE)
        traces["rectangles"].append((1, BG, BD, y, y + 18))
        traces["barres"].append((nom, dep, av, w))
        ecrire(BG, y + 24, f"{dep} sur le tour de départ, {av} sur le tour d'avant", 0, GRIS)
        y += 110
    art.rectangle([x0 + 12, y1 - 60, x0 + 24, y1 - 50], fill=BLEU)
    ecrire(x0 + 30, y1 - 62, "pied sur le tour de départ : le retard naît à ce saut", 0, ENCRE)
    art.rectangle([x0 + 12, y1 - 40, x0 + 24, y1 - 30], fill=ALERTE)
    ecrire(x0 + 30, y1 - 42, "pied sur le tour d'avant : la surface de départ était déjà en arrière", 0, ENCRE)
    traces["rectangles"] += [(1, x0 + 12, x0 + 24, y1 - 60, y1 - 50), (1, x0 + 12, x0 + 24, y1 - 40, y1 - 30)]

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
    tmp = sortie.parent / ".sonde_350.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "h": 9, "i": 1, "n": 12, "N": 20, "lissue": "x ; le retard vient de plus haut"}
    v("★★★ le titre LIT la mesure", le_titre(autre) == "HÉRITÉ SOUS 9 DES 12 SURFACES LUES, NÉ ICI SOUS 1 ; LE RETARD VIENT DE PLUS HAUT",
      le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : une lecture a échoué (x)"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : UNE LECTURE A ÉCHOUÉ (X)", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    m = d["les_constantes"]["le_minimum"]
    lues = sorted((s["la_chaine"], s["le_rang"], s["le_saut"], s["la_surface"]["la_part_heritee"]) for s in d["les_surfaces"]
                  if s["le_rang"] >= 4 and s["la_justesse"] == "juste" and s["la_surface"] is not None
                  and s["la_surface"]["les_restes"] >= m and s["la_surface"]["la_lecture"] != "non lu")
    v("★★★★ un point par surface à cheval lue, à sa part héritée, et aucun autre", sorted(traces["points"]) == lues,
      f"{len(traces['points'])} contre {len(lues)}")
    v("★★★★ chaque point est posé à l'abscisse de sa part héritée",
      all(abs(cx - (PG + p * (PD - PG))) < 0.5 for p, cx in traces["abscisses"]) and len(traces["abscisses"]) == len(lues))
    v("★★★★ les points sont autant que les surfaces que le verdict lit", not d["le_verdict"].get("decidable")
      or len(traces["points"]) == d["le_verdict"]["n"])
    v("★★★★ à droite des trois quarts, autant de points que d'héritées au verdict ; à gauche du quart, autant que de nées ici",
      not d["le_verdict"].get("decidable") or (sum(p[3] >= 0.75 for p in traces["points"]), sum(p[3] <= 0.25 for p in traces["points"]))
      == (d["le_verdict"]["h"], d["le_verdict"]["i"]))
    prem = {(p["la_chaine"], p["le_rang"], p["le_cote"]): p["le_premier_saut"] for p in d["les_premiers"] if p["le_rang"] >= 4}
    cheval = [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_justesse"] == "juste" and s["la_surface"] is not None
              and s["la_surface"]["les_restes"] >= m]
    pr = [s for s in cheval if prem.get((s["la_chaine"], s["le_rang"], s["le_cote"])) == s["le_saut"]]
    su = [s for s in cheval if prem.get((s["la_chaine"], s["le_rang"], s["le_cote"])) != s["le_saut"]]
    somme = lambda L, k: sum(s["la_surface"][k] for s in L)  # noqa: E731
    attendu = [(somme(pr, "pieds_sur_le_tour_de_depart"), somme(pr, "pieds_sur_le_tour_davant")),
               (somme(su, "pieds_sur_le_tour_de_depart"), somme(su, "pieds_sur_le_tour_davant"))]
    v("★★★★ les deux barres portent les pieds recomptés, premier saut à cheval d'un côté, sauts suivants de l'autre",
      [(b[1], b[2]) for b in traces["barres"]] == attendu
      and all(abs(b[3] - (BD - BG) * b[1] / (b[1] + b[2])) < 0.5 for b in traces["barres"]), str(traces["barres"]))
    v("★★★ chaque surface à cheval est dans l'une des deux barres, et dans une seule", len(pr) + len(su) == len(cheval) and len(pr) == len(prem))
    v("★★★★ la bande rapporte à côté les mêmes pieds",
      f"{attendu[0][0]} pieds sur le tour de départ contre {attendu[0][1]} sur le tour d'avant ; aux sauts suivants, "
      f"{attendu[1][0]} contre {attendu[1][1]}" in " ".join(la_bande(d)))
    haut, bas = traces["zone"]
    v("★★★★ chaque point est dans la zone du graphe", all(haut < r[3] and r[4] < bas for r in traces["rectangles"] if r[0] == 0))
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
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "350_le_retard_des_surfaces_a_cheval_nait_il_au_saut_qui_le_montre.png")
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
