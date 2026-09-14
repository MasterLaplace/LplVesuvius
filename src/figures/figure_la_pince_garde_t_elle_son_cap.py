#!/usr/bin/env python3
"""Une pince qui garde son cap.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En bas à gauche, le
résultat qui corrige ma prédiction : quand le cap monte, le refus de la pince tombe de 297 à zéro et
les deux bras finissent par marcher **exactement** pareil — le cap et la contrainte ne se complètent
pas, ils se remplacent. En haut à gauche, ce que le cap échange : des bonnes feuilles contre des
tours, avec un optimum réel. En haut à droite, les trois bras ensemble, où une seule mâchoire munie
d'un cap passe devant la pince. En bas à droite, la carte par matière, qui dit pourquoi : la pince
gagne sur l'écrasement, la mâchoire sur le froissement.

  uv run python src/figures/figure_la_pince_garde_t_elle_son_cap.py \\
      --json docs/mesures/la_pince_garde_t_elle_son_cap.json \\
      --sortie docs/images/143_la_pince_et_son_cap.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
UNE = (176, 92, 42)
DEUX = (86, 104, 132)
PINCE = (60, 110, 90)
REFUS = (150, 96, 176)
RIEN = (170, 172, 176)
BRAS = ("une machoire", "deux machoires libres", "la pince")
COULEURS = {"une machoire": UNE, "deux machoires libres": DEUX, "la pince": PINCE}
NOMS = {"une machoire": "une mâchoire", "deux machoires libres": "deux libres",
        "la pince": "la pince"}


def lire(chemin: Path) -> dict:
    """Le JSON de `la_pince_garde_t_elle_son_cap.py`.

    ⚠⚠ Refuse une mesure à laquelle il manque une des quatre choses que l'image montre : la pente,
    les trois bras, l'extinction de la contrainte et la barre. Une figure à laquelle il manque un
    terme affirme au lieu de montrer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    for cle in ("un_reglage_unique", "la_contrainte_tire_t_elle", "la_barre", "par_case"):
        if not j.get(cle):
            raise ValueError(f"{chemin} : « {cle} » absent")
    if len(j["un_reglage_unique"].get("par_memoire", [])) < 2:
        raise ValueError(f"{chemin} : une pente demande au moins deux mémoires")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1300, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    g = d["sur_la_grille"]
    j = d["juger"]
    pente = j["un_reglage_unique"]["par_memoire"]
    ct = j["la_contrainte_tire_t_elle"]
    mems = [x["memoire"] for x in pente]
    ecrire(28, 20, "Le cap et la contrainte ne se complètent pas : ils se remplacent", gros, ENCRE)
    ecrire(28, 46, f"{len(j['par_case'])} cases (matière × bruit), {g['departs']} départs chacune, "
                   f"un tour entier · une RÉUSSITE est jointe : boucler le tour ET revenir sur la "
                   f"même feuille", petit, GRIS)

    def axe_x(x0, pw, v):
        return x0 + 54 + (float(v) - min(mems)) / max(max(mems) - min(mems), 1e-9) * (pw - 78)

    # ── Haut gauche : ce que le cap échange, pour la pince ───────────────────
    x0, y0, pw, ph = 60, 122, 560, 290
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que le cap échange, pour la pince", moyen, ENCRE)
    series = (("reussites", "réussites", PINCE), ("memes_feuilles", "bonnes feuilles", DEUX),
              ("tours_boucles", "tours bouclés", UNE))
    # ⚠ L'échelle vient de CE QUI EST DESSINÉ et pas de zéro : l'échange que ce panneau montre se
    # joue entre 92 et 125, et une échelle partant de zéro l'écrase en trois traits confondus.
    hi = max(x["la pince"][k] for x in pente for k, _n, _c in series) * 1.06
    lo = min(x["la pince"][k] for x in pente for k, _n, _c in series) * 0.92

    def ay(v):
        return y0 + ph - 44 - ((float(v) - lo) / max(hi - lo, 1e-9)) * (ph - 108)

    for k in range(5):
        vv = lo + (hi - lo) * k / 4.0
        art.line([x0 + 50, ay(vv), x0 + pw - 12, ay(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 12, int(ay(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for m in mems:
        ecrire(int(axe_x(x0, pw, m)) - 11, y0 + ph - 34, f"{m:g}", petit, GRIS)
    ecrire(x0 + 54, y0 + ph - 18, "mémoire du cap", petit, GRIS)
    art.rectangle([x0 + 150, y0 + 6, x0 + pw - 10, y0 + 60], fill=FOND)
    yl = y0 + 8
    for cle, nom, coul in series:
        xy = [(axe_x(x0, pw, x["memoire"]), ay(x["la pince"][cle])) for x in pente]
        art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + 156, yl, nom, petit, coul)
        yl += 17
    u = j["un_reglage_unique"]["la pince"]
    mx = axe_x(x0, pw, u["memoire_unique"])
    art.line([mx, y0 + 66, mx, y0 + ph - 40], fill=PINCE, width=1)
    ecrire(int(mx) - 52, y0 + ph - 56, f"optimum {u['memoire_unique']:g}", petit, PINCE)

    # ── Haut droite : les trois bras ────────────────────────────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 290
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "les réussites des trois bras", moyen, ENCRE)
    hi1 = max(x[n]["reussites"] for x in pente for n in BRAS) * 1.14
    lo1 = min(x[n]["reussites"] for x in pente for n in BRAS) * 0.88

    def by(v):
        return y1 + ph1 - 44 - ((float(v) - lo1) / max(hi1 - lo1, 1e-9)) * (ph1 - 110)

    for k in range(5):
        vv = lo1 + (hi1 - lo1) * k / 4.0
        art.line([x1 + 50, by(vv), x1 + pw1 - 12, by(vv)], fill=TRAIT, width=1)
        ecrire(x1 + 12, int(by(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for m in mems:
        ecrire(int(axe_x(x1, pw1, m)) - 11, y1 + ph1 - 34, f"{m:g}", petit, GRIS)
    ecrire(x1 + 54, y1 + ph1 - 18, "mémoire du cap", petit, GRIS)
    art.rectangle([x1 + 150, y1 + 6, x1 + pw1 - 10, y1 + 62], fill=FOND)
    yl = y1 + 8
    for n in BRAS:
        xy = [(axe_x(x1, pw1, x["memoire"]), by(x[n]["reussites"])) for x in pente]
        art.line([p for q in xy for p in q], fill=COULEURS[n], width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=COULEURS[n])
            points.append((a_, b_))
        ecrire(x1 + 156, yl, f"{NOMS[n]} — {j['un_reglage_unique'][n]['reussites']} au mieux",
               petit, COULEURS[n])
        yl += 17

    # ── Bas gauche : la contrainte s'éteint ─────────────────────────────────
    x2, y2, pw2, ph2 = 60, 480, 560, 290
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "la contrainte s'éteint quand le cap monte", moyen, ENCRE)
    hi2 = max(x["refus"] for x in ct["par_memoire"]) or 1
    cases = max((x["cases"] for x in ct["par_memoire"]), default=1) or 1

    def cy_(v):
        return y2 + ph2 - 44 - (float(v) / hi2) * (ph2 - 110)

    for k in range(5):
        vv = hi2 * k / 4.0
        art.line([x2 + 50, cy_(vv), x2 + pw2 - 12, cy_(vv)], fill=TRAIT, width=1)
        ecrire(x2 + 12, int(cy_(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for m in mems:
        ecrire(int(axe_x(x2, pw2, m)) - 11, y2 + ph2 - 34, f"{m:g}", petit, GRIS)
    ecrire(x2 + 54, y2 + ph2 - 18, "mémoire du cap", petit, GRIS)
    art.rectangle([x2 + 150, y2 + 6, x2 + pw2 - 10, y2 + 62], fill=FOND)
    xy = [(axe_x(x2, pw2, x["memoire"]), cy_(x["refus"])) for x in ct["par_memoire"]]
    art.line([p for q in xy for p in q], fill=REFUS, width=2)
    for a_, b_ in xy:
        art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=REFUS)
        points.append((a_, b_))
    xy2 = [(axe_x(x2, pw2, x["memoire"]),
            cy_(hi2 * x["cases_marchees_a_lidentique"] / cases)) for x in ct["par_memoire"]]
    art.line([p for q in xy2 for p in q], fill=PINCE, width=2)
    for a_, b_ in xy2:
        art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=PINCE)
        points.append((a_, b_))
    ecrire(x2 + 156, y2 + 8, f"refus de la pince ({ct['refus_sans_cap']} sans cap)", petit, REFUS)
    ecrire(x2 + 156, y2 + 25, f"cases où elle marche comme un bras LIBRE, sur {cases}",
           petit, PINCE)
    if ct.get("memoire_ou_la_contrainte_devient_inerte") is not None:
        ecrire(x2 + 156, y2 + 42, f"inerte à partir de "
                                  f"{ct['memoire_ou_la_contrainte_devient_inerte']:g}",
               petit, ENCRE)

    # ── Bas droite : la carte par matière ───────────────────────────────────
    x3, y3, pw3, ph3 = 700, 480, L - 700 - 60, 290
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "qui gagne, matière par matière", moyen, ENCRE)
    ecrire(x3 + 10, y3 + 8, "au meilleur cap de chaque case, en réussites", petit, GRIS)
    yy = y3 + 34
    for b in j["par_case"]:
        gagnant = max(BRAS, key=lambda n: (b[n]["reussites"], -BRAS.index(n)))
        ex = all(b[n]["reussites"] == b[BRAS[0]]["reussites"] for n in BRAS)
        coul = RIEN if ex else COULEURS[gagnant]
        ecrire(x3 + 10, yy, f"{b['nom'].replace('spirale ', '')}", petit, ENCRE)
        ecrire(x3 + 204, yy, f"{b['bruit']:g}", petit, GRIS)
        for k, n in enumerate(BRAS):
            ecrire(x3 + 232 + k * 54, yy, f"{b[n]['reussites']:>2d}", petit,
                   COULEURS[n] if not ex else RIEN)
        art.rectangle([x3 + pw3 - 26, yy + 2, x3 + pw3 - 12, yy + 12], fill=coul)
        points.append((x3 + pw3 - 26, yy))
        yy += 16
    ecrire(x3 + 232, y3 + 18, "une", petit, UNE)
    ecrire(x3 + 286, y3 + 18, "deux", petit, DEUX)
    ecrire(x3 + 340, y3 + 18, "pince", petit, PINCE)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    t = j["la_case_ou_le_cap_change_le_plus"]
    b_ = j["la_barre"]
    ecrire(44, by0 + 10, f"★ le refus tombe de {ct['refus_sans_cap']} à zéro et les deux bras "
                         f"marchent à l'identique dans "
                         f"{ct['par_memoire'][-1]['cases_marchees_a_lidentique']} cases sur "
                         f"{cases} : un cap suffisant rend la contrainte inerte.", moyen, ENCRE)
    ecrire(44, by0 + 34, f"le cap échange des feuilles contre des tours, avec un optimum à "
                         f"{u['memoire_unique']:g} — et un réglage UNIQUE n'y coûte que "
                         f"{u['ce_que_coute_un_reglage_unique']} réussites sur "
                         f"{u['reussites_au_mieux_par_case']}.", petit, ENCRE)
    ecrire(44, by0 + 52, f"⚠ sur la grille entière, une seule mâchoire munie d'un cap passe devant "
                         f"la pince ({j['un_reglage_unique']['une machoire']['reussites']} contre "
                         f"{u['reussites']}) : la pince paie de voir ses deux interstices sur les "
                         f"matières froissées.", petit, ENCRE)
    ecrire(44, by0 + 74, f"✗ la barre de `140` n'est pas franchie : {b_['reussites_au_mieux']} "
                         f"réussite sur {b_['departs']} à toute mémoire — "
                         f"{b_['tours_boucles_au_mieux']} tour bouclé et "
                         f"{b_['memes_feuilles_au_mieux']} bonnes feuilles au mieux, jamais "
                         f"ensemble.", petit, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile  # noqa: PLC0415

    from figure_commune import glyphes_manquants  # noqa: PLC0415

    src = RACINE / "docs" / "mesures" / "la_pince_garde_t_elle_son_cap.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for nom, contenu in (
                ("message", {"message": "fixture injoignable"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("sans pente", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "par_case": d["juger"]["par_case"],
                    "un_reglage_unique": {"par_memoire": []},
                    "la_contrainte_tire_t_elle": d["juger"]["la_contrainte_tire_t_elle"],
                    "la_barre": d["juger"]["la_barre"]}}),
                ("sans barre", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "par_case": d["juger"]["par_case"],
                    "un_reglage_unique": d["juger"]["un_reglage_unique"],
                    "la_contrainte_tire_t_elle": d["juger"]["la_contrainte_tire_t_elle"]}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "143.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1300)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g for _x, _y, t_, _f in poses for g in glyphes_manquants(t_)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1300 and 0 <= y <= 900 for x, y in points), f"{len(points)} points")
        v("il y a bien de quoi regarder", len(points) > 50, f"{len(points)} points")

        autre = tmp / "143_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["la_contrainte_tire_t_elle"]["refus_sans_cap"] = 9999
        troisieme = tmp / "143_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())
        d3 = json.loads(json.dumps(d))
        for x in d3["juger"]["un_reglage_unique"]["par_memoire"]:
            x["la pince"]["reussites"] = 1
        quatrieme = tmp / "143_qua.png"
        dessiner(d3, quatrieme)
        v("⭐ la pente lit la mesure elle aussi", quatrieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/la_pince_garde_t_elle_son_cap.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/143_la_pince_et_son_cap.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
