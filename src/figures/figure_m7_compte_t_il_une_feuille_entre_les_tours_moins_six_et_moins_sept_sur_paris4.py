"""Sur PHercParis4 : les feuilles de m7 comptées entre deux tours publiés consécutifs, pour le témoin et pour la cible des graines 4 à 6.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, le témoin : pour chaque saut d'une feuille jugé juste, la part de ses points où
`m7` compte une feuille entre les deux tours publiés ; presque tous sont à droite. À droite, la cible, un saut par rangée : la part de ses
points à zéro, une et deux feuilles entre les tours −6 et −7. Là où le gris domine, `m7` ne voit qu'une feuille sous les deux tours.

  uv run python src/figures/figure_m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.py \
      --sortie docs/images/407_m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.png

⚠ Tout vient de la mesure de `407`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
CLAIR = (196, 199, 204)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BLEU = (58, 88, 120)
ORANGE = (214, 150, 76)
L_, H_ = 1200, 640
LA_BANDE = 520
A = (50, 70, 500, 500, 110, 480, 140, 420)
B = (520, 70, 1150, 500, 820, 1130, 140, 420)
LES_CASES = 10
LES_TEINTES = {"0": CLAIR, "1": BLEU, "2": ORANGE}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_nombre(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def la_cible(d: dict) -> list[dict]:
    g = d["les_constantes"]["les_graines_de_la_cible"]
    return [x for x in d["les_sauts_de_moins_six"] if x["le_nombre_de_feuilles"] == 1 and x["le_rang"] in g
            and x["au_depart"]["lue"] and x["au_depart"]["sur_son_tour"]]


def la_part(c: dict, k: str) -> float:
    n = sum(c.values())
    return c.get(k, 0) / n if n else 0.0


def les_cases(d: dict) -> list[tuple[int, int]]:
    """Le témoin lu, par dixième de la part de ses points à une feuille : combien disent une feuille, combien une autre."""
    out = [[0, 0] for _ in range(LES_CASES)]
    for x in d["les_sauts_justes"]:
        e = x["entre_les_tours"]
        if e["le_nombre_de_feuilles"] is None:
            continue
        i = min(int(la_part(e["les_comptes"], "1") * LES_CASES), LES_CASES - 1)
        out[i][0 if e["le_nombre_de_feuilles"] == 1 else 1] += 1
    return [tuple(c) for c in out]


def le_titre(d: dict) -> str:
    cible = [x for x in la_cible(d) if x["entre_les_tours"]["le_nombre_de_feuilles"] is not None]
    t = [x for x in d["les_sauts_justes"] if x["entre_les_tours"]["le_nombre_de_feuilles"] is not None]
    un = lambda xs: sum(x["entre_les_tours"]["le_nombre_de_feuilles"] == 1 for x in xs)  # noqa: E731
    return (f"une feuille de m7 entre les tours −6 et −7 : {un(cible)} sur {len(cible)} ; témoin : "
            f"{un(t)} sur {len(t)} ; {d['le_verdict']['lissue'].rpartition(' ; ')[2]}").upper()


def la_bande(d: dict) -> tuple[str, ...]:
    un = f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}"
    deux = ("rapporté à côté, qui ne décide rien : un compte à zéro dit que les deux tours publiés sont sur la même feuille de m7 ; "
            "un compte non lu a moins de 50 points mesurés")
    trois = "⚠ ce qui n'est PAS établi : pourquoi m7 ne compte qu'une feuille sur un saut qui va au-delà du tour −7, là où il en voit une entre eux."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [A[:4], B[:4]]
    traces = {"cases": [], "rangees": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "en bleu une feuille de m7 entre les deux tours publiés, en gris aucune, en orange deux", petit, GRIS)
    for x0, y0, x1, y1 in cadres:
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)

    _, _, _, _, ax0, ax1, ay0, ay1 = A
    ecrire(62, 78, "le témoin, entre tours consécutifs", moyen, ENCRE)
    ecrire(62, 100, "sauts jugés justes, par part de leurs points à une feuille", petit, GRIS)
    cases = les_cases(d)
    haut = max((a + b for a, b in cases), default=1) or 1
    larg = (ax1 - ax0) / LES_CASES
    art.rectangle([ax0, ay0, ax1, ay1], outline=GRIS)
    for i, (a, b) in enumerate(cases):
        x0 = ax0 + i * larg + 3
        hb, ha = (ay1 - ay0) * b / haut, (ay1 - ay0) * a / haut
        if b:
            art.rectangle([x0, ay1 - hb, x0 + larg - 6, ay1], fill=CLAIR)
        if a:
            art.rectangle([x0, ay1 - hb - ha, x0 + larg - 6, ay1 - hb], fill=BLEU)
        traces["cases"].append((a, b, ay1 - hb - ha))
        if a + b:
            ecrire(int(x0 + larg / 2 - 10), int(ay1 - hb - ha - 16), str(a + b), petit, ENCRE)
    for i in range(0, LES_CASES + 1, 2):
        ecrire(int(ax0 + i * larg - 6), ay1 + 6, le_nombre(i / LES_CASES), petit, GRIS)
    ecrire(ax0, ay1 + 28, "part des points à une feuille ; bleu si le compte dit une feuille", petit, ENCRE)

    _, _, _, _, bx0, bx1, by0, by1 = B
    ecrire(532, 78, "la cible, entre les tours −6 et −7", moyen, ENCRE)
    ecrire(532, 100, "graines 4 à 6, sauts d'une feuille dont le départ est sur le tour −6", petit, GRIS)
    cible = sorted(la_cible(d), key=lambda x: (x["le_rang"], x["la_chaine"], x["les_familles"]))
    pas = (by1 - by0) / max(1, len(cible))
    for i, x in enumerate(cible):
        e = x["entre_les_tours"]
        y = by0 + i * pas
        nom = f"graine {x['le_rang']}, {x['la_chaine']} ({'+'.join('rognée' if f == 'rognees' else f for f in x['les_familles'])})"
        ecrire(532, int(y + pas / 2 - 7), nom, petit, ENCRE)
        x0 = bx0
        for k in ("0", "1", "2"):
            w = (bx1 - bx0) * la_part(e["les_comptes"], k)
            if w > 0:
                art.rectangle([x0, y + 4, x0 + w, y + pas - 4], fill=LES_TEINTES[k])
            x0 += w
        dit = e["le_nombre_de_feuilles"]
        etiquette = "non lu" if dit is None else f"{dit} : {sum(e['les_comptes'].values())} points"
        ecrire(bx0 - 88, int(y + pas / 2 - 7), etiquette, petit, ALERTE if dit == 0 else ENCRE)
        traces["rangees"].append((x["le_rang"], dit, x0))
    art.rectangle([bx0, by0, bx1, by1], outline=GRIS)
    ecrire(bx0, by1 + 28, "part des points à zéro, une et deux feuilles", petit, ENCRE)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un_, deux_, trois_ = la_bande(d)
    ecrire(50, LA_BANDE + 10, un_, petit, ENCRE)
    ecrire(50, LA_BANDE + 28, deux_, petit, ENCRE)
    ecrire(50, LA_BANDE + 56, trois_, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_407.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    e_ = lambda n, c: {"le_rang": 4, "le_nombre_de_feuilles": 1, "au_depart": {"lue": True, "sur_son_tour": True},  # noqa: E731
                       "entre_les_tours": {"le_nombre_de_feuilles": n, "les_comptes": c}}
    autre = {"les_constantes": d["les_constantes"], "le_verdict": {"lissue": "x ; oui"},
             "les_sauts_justes": [e_(1, {"1": 9})] * 3, "les_sauts_de_moins_six": [e_(1, {"1": 9}), e_(0, {"0": 9})]}
    v("★★★ le titre LIT la mesure", le_titre(autre)
      == "UNE FEUILLE DE M7 ENTRE LES TOURS −6 ET −7 : 1 SUR 2 ; TÉMOIN : 3 SUR 3 ; OUI", le_titre(autre))
    melange = {"les_sauts_justes": [{"entre_les_tours": {"le_nombre_de_feuilles": 1, "les_comptes": {"0": 40, "1": 45, "2": 30}}},
                                    {"entre_les_tours": {"le_nombre_de_feuilles": None, "les_comptes": {"1": 9}}}]}
    v("★★★★ la couleur d'une case vient du compte que dit le saut, pas de sa part à une feuille ; un compte non lu n'y est pas",
      les_cases(melange)[3] == (1, 0) and sum(a + b for a, b in les_cases(melange)) == 1, str(les_cases(melange)))
    lus = [x for x in d["les_sauts_justes"] if x["entre_les_tours"]["le_nombre_de_feuilles"] is not None]
    v("★★★★ les cases du témoin somment à ses comptes lus, et le bleu à ceux d'une feuille",
      sum(a + b for a, b, _ in traces["cases"]) == len(lus)
      and sum(a for a, _, _ in traces["cases"]) == sum(x["entre_les_tours"]["le_nombre_de_feuilles"] == 1 for x in lus))
    v("★★★★ les comptes de la figure sont ceux du verdict",
      f"témoin : {sum(a for a, _, _ in traces['cases'])} sur {len(lus)}" in d["le_verdict"]["lissue"]
      and f"{sum(r[1] == 1 for r in traces['rangees'])} comptes sur {sum(r[1] is not None for r in traces['rangees'])} à une feuille"
      in d["le_verdict"]["lissue"])
    v("★★★★ une rangée par saut de la cible, et rien d'autre",
      len(traces["rangees"]) == len(la_cible(d)) and all(r[0] in d["les_constantes"]["les_graines_de_la_cible"] for r in traces["rangees"]))
    v("★★★★ chaque barre de la cible fait toute la largeur quand elle a des points",
      all(abs(r[2] - B[5]) < 1e-6 for r, x in zip(traces["rangees"], sorted(la_cible(d), key=lambda x: (x["le_rang"], x["la_chaine"],
                                                                                                      x["les_familles"])))
          if sum(x["entre_les_tours"]["les_comptes"].values())))
    v("★★★★ aucune case ne monte au-dessus du graphe", all(y >= A[6] - 1e-6 for _, _, y in traces["cases"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t_, _ in poses for x in glyphes_manquants(t_)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ la bande porte le verdict entier", la_bande(d)[0] == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t_ for _, _, t_, _ in poses))
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "407_m7_compte_t_il_une_feuille_entre_les_tours_moins_six_et_moins_sept_sur_paris4.png")
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
