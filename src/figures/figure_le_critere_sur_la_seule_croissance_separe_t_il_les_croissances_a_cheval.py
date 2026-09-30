"""Sur PHercParis4, graines 4 à 8 : la part des croissances à cheval et des croissances saines que le critère de 352, lu sur la seule croissance, refuse ; et la part qu'il refuse faute de 50 points mesurés.

⚠⚠ **Ce que cette figure doit rendre évident.** Deux groupes de barres, les croissances à cheval et les saines ; dans chaque groupe, la
part refusée par le critère en orange, et la part refusée faute de mesures en gris. Un trait marque la moitié. Sous chaque barre, le compte.

  uv run python src/figures/figure_le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.py \\
      --sortie docs/images/359_le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.png

⚠ Tout vient de la mesure de `359`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
ORANGE = (214, 150, 76)
GRIS_BARRE = (170, 172, 176)
L_, H_ = 1100, 590
LA_BANDE = 470
HAUT, BAS = 150, 390
LARGEUR = 90
LES_GROUPES = (("a_cheval", "croissances à cheval", 330), ("saines", "croissances saines", 770))
LES_BARRES = (("les_refusees", "refusées par le critère", ORANGE), ("faute_de_mesures", "dont faute de 50 points mesurés", GRIS_BARRE))


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    s = d["la_separation"]
    return (f"sur la seule croissance, le critère refuse {s['a_cheval']['les_refusees']} des {s['a_cheval']['les_croissances']} "
            f"croissances à cheval et {s['saines']['les_refusees']} des {s['saines']['les_croissances']} saines : "
            f"{v['lissue'].rpartition(' ; ')[2]}").upper()


def les_croissances(d: dict) -> list[dict]:
    return [s for c in d["les_cotes"] if c["le_rang"] >= 4 for s in c["les_sauts"]
            if s["la_justesse"] == "juste" and s["depuis"] == "la croissance" and s.get("en_plus")]


def la_bande(d: dict) -> tuple[str, ...]:
    un, _, deux = d["le_verdict"]["lissue"].partition(" ; ")
    c = les_croissances(d)
    mailles = [s["en_plus"]["les_mailles"] for s in c]
    mesures = [s["en_plus"]["le_compte"]["les_mesures"] for s in c]
    trois = (f"rapporté à côté, qui ne décide rien : une croissance a {statistics.median(mailles):g} mailles en médiane, dont "
             f"{statistics.median(mesures):g} mesurées ; des {len(c)} croissances, {sum(s['en_plus']['mesuree'] for s in c)} ont 50 "
             f"points mesurés").replace(".", ",")
    quatre = "⚠ ce qui n'est PAS établi : si un autre juge, comme l'écart de la croissance au départ comparé à celui de sa spire, la séparerait."
    return f"LE VERDICT DÉCLARÉ : {un} ;", deux, trois, quatre


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(15, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres = [(50, 70, 1050, 440)]
    traces = {"barres": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "sur PHercParis4, graines 4 à 8 : les croissances gardées sous les sauts justes ; une barre est une part de son groupe",
           petit, GRIS)
    x0, y0, x1, y1 = cadres[0]
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    ecrire(x0 + 12, y0 + 8, "le critère de 352, lu sur la seule croissance", moyen, ENCRE)
    lx = x0 + 560
    for i, (_, nom, couleur) in enumerate(LES_BARRES):
        ly = y0 + 10 + i * 20
        art.rectangle([lx, ly + 2, lx + 12, ly + 14], fill=couleur)
        traces["rectangles"].append((lx, lx + 12, ly + 2, ly + 14))
        ecrire(lx + 20, ly, nom, petit, ENCRE)
    art.line([x0 + 40, BAS, x1 - 40, BAS], fill=GRIS, width=1)
    moitie = BAS - round(0.5 * (BAS - HAUT))
    for x in range(x0 + 40, x1 - 40, 12):
        art.line([x, moitie, x + 5, moitie], fill=GRIS, width=1)
    ecrire(x1 - 100, moitie - 16, "la moitié", petit, GRIS)
    traces["la_moitie"] = moitie
    for groupe, titre, centre in LES_GROUPES:
        g = d["la_separation"][groupe]
        for i, (cle, _, couleur) in enumerate(LES_BARRES):
            n = g["les_croissances"]
            part = g[cle] / n if n else 0.0
            gauche = centre - LARGEUR - 10 if i == 0 else centre + 10
            sommet = BAS - round(part * (BAS - HAUT))
            art.rectangle([gauche, sommet, gauche + LARGEUR, BAS], fill=couleur)
            traces["barres"].append((groupe, cle, g[cle], n, sommet, couleur))
            traces["rectangles"].append((gauche, gauche + LARGEUR, sommet, BAS))
            ecrire(gauche + 26, sommet - 18, f"{round(100 * part)} %", petit, ENCRE)
            ecrire(gauche + 20, BAS + 6, f"{g[cle]} sur {n}", petit, ENCRE)
        ecrire(centre - 80, BAS + 26, titre, moyen, ENCRE)
        traces.setdefault("titres", []).append((groupe, titre, centre))

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    for k, ligne in enumerate(la_bande(d)):
        if k < 3:
            ecrire(50, LA_BANDE + 10 + 18 * k, ligne, petit, ENCRE)
        else:
            ecrire(50, LA_BANDE + 10 + 18 * k + 8, ligne, moyen, ALERTE)

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
    tmp = sortie.parent / ".sonde_359.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"]["lissue"] = "x ; oui, il les sépare"
    autre["la_separation"] = {"a_cheval": {"les_croissances": 9, "les_refusees": 7}, "saines": {"les_croissances": 8, "les_refusees": 1}}
    v("★★★ le titre LIT la mesure", le_titre(autre) == ("SUR LA SEULE CROISSANCE, LE CRITÈRE REFUSE 7 DES 9 CROISSANCES À CHEVAL ET 1 DES "
                                                        "8 SAINES : OUI, IL LES SÉPARE"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : x"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : X", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    v("★★★★ la bande tient dans la toile", LA_BANDE + 10 + 18 * 3 + 8 + 18 < H_)
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    c = les_croissances(d)
    for groupe, a_cheval in (("a_cheval", True), ("saines", False)):
        g = [s for s in c if bool(s["a_cheval"]) == a_cheval]
        ref = [s for s in g if not s["en_plus"]["tenue"]]
        v(f"★★★★ la séparation des croissances {groupe} se recompte sur les sauts",
          (d["la_separation"][groupe]["les_croissances"], d["la_separation"][groupe]["les_refusees"],
           d["la_separation"][groupe]["faute_de_mesures"]) == (len(g), len(ref), sum(1 for s in ref if not s["en_plus"]["mesuree"])))
    attendu = [(g, k, d["la_separation"][g][k], d["la_separation"][g]["les_croissances"], f) for g, _, _ in LES_GROUPES for k, _, f in LES_BARRES]
    v("★★★★ deux barres par groupe, refusées puis faute de mesures, au compte et à la couleur voulus",
      [(g, k, a, n, f) for g, k, a, n, _, f in traces["barres"]] == attendu, str(traces["barres"]))
    v("★★★★ chaque groupe porte le nom de ses croissances",
      sorted(g for g, _, _ in traces["titres"]) == ["a_cheval", "saines"]
      and all({"a_cheval": "croissances à cheval", "saines": "croissances saines"}[g] == t_ for g, t_, _ in traces["titres"]),
      str(traces["titres"]))
    v("★★★★ les refusées en orange, celles faute de mesures en gris",
      all(f == {"les_refusees": ORANGE, "faute_de_mesures": GRIS_BARRE}[k] for _, k, _, _, _, f in traces["barres"]))
    v("★★★★ la hauteur de chaque barre est sa part", all(BAS - s == round(a / n * (BAS - HAUT)) for _, _, a, n, s, _ in traces["barres"]))
    v("★★★★ le trait de la moitié est à la moitié", BAS - traces["la_moitie"] == round(0.5 * (BAS - HAUT)))
    textes = {t for _, _, t, _ in poses}
    v("★★★★ sous chaque barre, le compte qui la fait", all(f"{a} sur {n}" in textes for _, _, a, n, _, _ in traces["barres"]))
    x0, y0, x1, y1 = cadres[0]
    dehors = [r for r in traces["rectangles"] if not (x0 < r[0] and r[1] < x1 and y0 < r[2] and r[3] < y1)]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    v("★★★★ la bande rapporte à côté les croissances qui ont 50 points mesurés, recomptées",
      f"des {len(c)} croissances, {sum(s['en_plus']['mesuree'] for s in c)} ont 50 points mesurés" in " ".join(la_bande(d)))
    v("★★★★ la bande porte le verdict entier", " ".join(la_bande(d)[:2]) == f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}")
    v("★★★★ elle porte ce qui n'est PAS établi", any("n'est PAS établi" in t for t in textes))
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
                   / "359_le_critere_sur_la_seule_croissance_separe_t_il_les_croissances_a_cheval.png")
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
