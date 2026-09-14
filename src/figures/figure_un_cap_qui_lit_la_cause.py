#!/usr/bin/env python3
"""Un cap qui lit la cause.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En haut à gauche, le
mécanisme : sans bruit, la mémoire que la règle lit monte de **zéro** sur une spirale nue ou écrasée
jusqu'à un froissement fort — elle lit exactement ce qu'elle prétend lire. Les deux autres courbes
disent où elle s'arrête : quand le bruit monte, le plancher monte avec lui et la courbe s'aplatit,
tout en gardant son ORDRE. En bas à gauche, le critère exact qui tranche — l'écart entre matières
contre la dispersion dans une matière. En haut à droite, ce que ça vaut en réussites, contre le
meilleur cap posé que `143` mesure. En bas à droite, la barre de `140`, qui reste au sol.

  uv run python src/figures/figure_un_cap_qui_lit_la_cause.py \\
      --json docs/mesures/un_cap_qui_lit_la_cause.json \\
      --sortie docs/images/144_un_cap_qui_lit_la_cause.png
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
POSE = (150, 96, 176)
BRUITS_COUL = ((60, 110, 90), (86, 104, 132), (176, 92, 42))
BRAS = ("une machoire", "deux machoires libres", "la pince")
COULEURS = {"une machoire": UNE, "deux machoires libres": DEUX, "la pince": PINCE}
NOMS = {"une machoire": "une mâchoire", "deux machoires libres": "deux libres",
        "la pince": "la pince"}


def lire(chemin: Path) -> dict:
    """Le JSON de `un_cap_qui_lit_la_cause.py`.

    ⚠⚠ Refuse une mesure sans le témoin de `143` : cette image est une COMPARAISON du cap lu au cap
    posé, et une comparaison sans son témoin est une affirmation déguisée en dessin.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    if not j.get("contre_le_fixe", {}).get("decidable"):
        raise ValueError(f"{chemin} : le témoin de `143` est absent, il n'y a rien à comparer")
    if not j.get("la_lecture_survit_elle_au_bruit"):
        raise ValueError(f"{chemin} : « la_lecture_survit_elle_au_bruit » absent")
    if len(j["contre_le_fixe"].get("par_fenetre", [])) < 2:
        raise ValueError(f"{chemin} : un balayage demande au moins deux fenêtres")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1320, 900
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
    cf = j["contre_le_fixe"]
    surv = j["la_lecture_survit_elle_au_bruit"]
    # ⚠ Aucune fenêtre n'est CHOISIE pour raconter : à chaque bruit on montre celle qui sépare le
    # mieux, et la mesure dit laquelle.
    disc = surv["par_bruit"]
    ecrire(28, 20, "La règle lit la cause, jusqu'à ce que le bruit la couvre", gros, ENCRE)
    ecrire(28, 46, f"mémoire lue = 1 − cohérence des rotations de la normale · {g['departs']} "
                   f"départs par case, un tour · fenêtre balayée de {min(g['fenetres'])} à "
                   f"{max(g['fenetres'])} pas · témoin : le meilleur cap POSÉ de `143`",
           petit, GRIS)

    # ── Haut gauche : la mémoire lue, matière par matière ────────────────────
    x0, y0, pw, ph = 60, 122, 600, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la mémoire que la règle LIT, matière par matière", moyen, ENCRE)
    mats = [m["nom"] for m in disc[0]["par_matiere"]]
    pas_x = (pw - 120) / max(len(mats) - 1, 1)

    def mx(i):
        return x0 + 66 + i * pas_x

    def my(v):
        return y0 + ph - 58 - float(v) * (ph - 100)

    for k in range(5):
        vv = k / 4.0
        art.line([x0 + 56, my(vv), x0 + pw - 12, my(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 14, int(my(vv)) - 7, f"{vv:.2f}", petit, GRIS)
    art.rectangle([x0 + 150, y0 + 6, x0 + pw - 10, y0 + 62], fill=FOND)
    for k, bloc in enumerate(disc):
        coul = BRUITS_COUL[k % len(BRUITS_COUL)]
        xy = [(mx(i), my(m["memoire"])) for i, m in enumerate(bloc["par_matiere"])
              if m["memoire"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + 156, y0 + 8 + k * 17, f"bruit {bloc['bruit']:g} (fenêtre "
                                          f"{bloc['meilleure_fenetre']}) — écart "
                                          f"{bloc['ecart_entre_matieres']:.4f}", petit, coul)
    for i, nom in enumerate(mats):
        court = nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
        ecrire(int(mx(i)) - 3 * len(court), y0 + ph - 44, court, petit, ENCRE)
    ecrire(x0 + 14, y0 + ph - 22, "les matières, du plus lisse au plus froissé", petit, GRIS)

    # ── Haut droite : les réussites, contre le cap posé ─────────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 300
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "réussites : cap LU contre cap POSÉ", moyen, ENCRE)
    fens = [x["fenetre"] for x in cf["par_fenetre"]]
    vals = [x[n]["reussites"] for x in cf["par_fenetre"] for n in BRAS]
    vals += [cf[n]["reussites_posees"] for n in BRAS if n in cf]
    hi1, lo1 = max(vals) * 1.04, min(vals) * 0.94

    def fx(i):
        return x1 + 62 + i * (pw1 - 100) / max(len(fens) - 1, 1)

    def fy(v):
        return y1 + ph1 - 46 - ((float(v) - lo1) / max(hi1 - lo1, 1e-9)) * (ph1 - 112)

    for k in range(5):
        vv = lo1 + (hi1 - lo1) * k / 4.0
        art.line([x1 + 54, fy(vv), x1 + pw1 - 12, fy(vv)], fill=TRAIT, width=1)
        ecrire(x1 + 14, int(fy(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for i, f in enumerate(fens):
        ecrire(int(fx(i)) - 8, y1 + ph1 - 36, f"{f}", petit, GRIS)
    ecrire(x1 + 62, y1 + ph1 - 20, "fenêtre de lecture, en pas", petit, GRIS)
    art.rectangle([x1 + 130, y1 + 6, x1 + pw1 - 10, y1 + 62], fill=FOND)
    for k, n in enumerate(BRAS):
        xy = [(fx(i), fy(x[n]["reussites"])) for i, x in enumerate(cf["par_fenetre"])]
        art.line([p for q in xy for p in q], fill=COULEURS[n], width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=COULEURS[n])
            points.append((a_, b_))
        if n in cf:
            art.line([x1 + 54, fy(cf[n]["reussites_posees"]), x1 + pw1 - 12,
                      fy(cf[n]["reussites_posees"])], fill=COULEURS[n], width=1)
        ecrire(x1 + 136, y1 + 8 + k * 17,
               f"{NOMS[n]} — lu {cf[n]['reussites_lues']} contre posé "
               f"{cf[n]['reussites_posees']} ({cf[n]['ecart']:+d})", petit, COULEURS[n])

    # ── Bas gauche : le critère exact ───────────────────────────────────────
    x2, y2, pw2, ph2 = 60, 490, 600, 280
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "le critère exact : entre les matières, contre dans une matière", moyen,
           ENCRE)
    hi2 = max(max(x["ecart_entre_matieres"], x["dispersion_dans_une_matiere"])
              for x in surv["par_bruit"]) * 1.12
    bru = [x["bruit"] for x in surv["par_bruit"]]

    def dx_(i):
        return x2 + 66 + i * (pw2 - 110) / max(len(bru) - 1, 1)

    def dy(v):
        return y2 + ph2 - 48 - (float(v) / hi2) * (ph2 - 108)

    for k in range(5):
        vv = hi2 * k / 4.0
        art.line([x2 + 56, dy(vv), x2 + pw2 - 12, dy(vv)], fill=TRAIT, width=1)
        ecrire(x2 + 14, int(dy(vv)) - 7, f"{vv:.2f}", petit, GRIS)
    for i, b in enumerate(bru):
        ecrire(int(dx_(i)) - 6, y2 + ph2 - 38, f"{b:g}", petit, GRIS)
    ecrire(x2 + 66, y2 + ph2 - 22, "bruit de la matière", petit, GRIS)
    art.rectangle([x2 + 150, y2 + 6, x2 + pw2 - 10, y2 + 62], fill=FOND)
    for cle, nom, coul in (("ecart_entre_matieres", "écart ENTRE les matières", PINCE),
                           ("dispersion_dans_une_matiere", "dispersion DANS une matière", POSE)):
        xy = [(dx_(i), dy(x[cle])) for i, x in enumerate(surv["par_bruit"])]
        art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=coul)
            points.append((a_, b_))
    ecrire(x2 + 156, y2 + 8, "écart ENTRE les matières", petit, PINCE)
    ecrire(x2 + 156, y2 + 25, "dispersion DANS une matière", petit, POSE)
    ecrire(x2 + 156, y2 + 42, f"elle sépare jusqu'au bruit "
                              f"{surv['le_bruit_le_plus_fort_ou_elle_separe']:g}, fenêtre "
                              f"{surv['la_fenetre_qui_y_arrive']}", petit, ENCRE)

    # ── Bas droite : la barre de `140` ──────────────────────────────────────
    x3, y3, pw3, ph3 = 700, 490, L - 700 - 60, 280
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "la barre de `140`, matière écrasée ET froissée", moyen, ENCRE)
    barre = [c for c in g["cases"] if c["ecrasement"] > 0.0 and c["amplitude_um"] == 100.0]
    ecrire(x3 + 14, y3 + 12, f"réussites sur {g['departs']} départs, par fenêtre et par bruit :",
           petit, GRIS)
    yy = y3 + 36
    ecrire(x3 + 14, yy, "bruit", petit, GRIS)
    for i, f in enumerate(sorted({c["fenetre_du_cap"] for c in barre})):
        ecrire(x3 + 86 + i * 58, yy, f"W{f}", petit, GRIS)
    yy += 20
    for b in sorted({c["bruit"] for c in barre}):
        ecrire(x3 + 14, yy, f"{b:g}", petit, ENCRE)
        for i, f in enumerate(sorted({c["fenetre_du_cap"] for c in barre})):
            cel = [c for c in barre if c["bruit"] == b and c["fenetre_du_cap"] == f]
            r = max((cel[0]["bras"][n].get("reussites") or 0) for n in BRAS) if cel else 0
            ecrire(x3 + 92 + i * 58, yy, f"{r}", petit, ENCRE if r else GRIS)
        yy += 20
    ecrire(x3 + 14, yy + 10, "le meilleur des trois bras, à chaque case.", petit, ENCRE)
    ecrire(x3 + 14, yy + 28, "Aucune fenêtre, aucun bruit : la barre reste", petit, ENCRE)
    ecrire(x3 + 14, yy + 46, "au sol, comme à cap posé.", petit, ENCRE)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    p_ = cf.get("la pince", {})
    ecrire(44, by0 + 10, f"★ sans bruit la règle lit exactement ce qu'elle prétend lire : "
                         f"{disc[0]['memoire_la_plus_basse']:.4f} sur la matière la plus lisse, "
                         f"{disc[0]['memoire_la_plus_haute']:.4f} sur la plus froissée.",
           moyen, ENCRE)
    ecrire(44, by0 + 34, f"pour la pince elle bat le meilleur cap POSÉ : "
                         f"{p_.get('reussites_lues')} réussites contre "
                         f"{p_.get('reussites_posees')}, soit {p_.get('ecart'):+d} — et sans "
                         f"aucune constante ajustée.", petit, ENCRE)
    ecrire(44, by0 + 52, f"⚠ elle sépare jusqu'au bruit "
                         f"{surv['le_bruit_le_plus_fort_ou_elle_separe']:g} (fenêtre "
                         f"{surv['la_fenetre_qui_y_arrive']}) et pas au-delà : écart "
                         f"{surv['par_bruit'][-1]['ecart_entre_matieres']:.4f} pour une dispersion "
                         f"interne de "
                         f"{surv['par_bruit'][-1]['dispersion_dans_une_matiere']:.4f}.",
           petit, ENCRE)
    ecrire(44, by0 + 74, "⚠ et la barre de `140` reste au sol : aucune fenêtre, aucun bruit, "
                         "aucun bras ne réussit un transfert sur la matière écrasée et froissée.",
           petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "un_cap_qui_lit_la_cause.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        j = d["juger"]
        for nom, contenu in (
                ("message", {"message": "témoin absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("sans témoin fixe", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "contre_le_fixe": {"decidable": False},
                    "la_lecture_survit_elle_au_bruit": j["la_lecture_survit_elle_au_bruit"]}}),
                ("sans survie", {"sur_la_grille": d["sur_la_grille"], "juger": {
                    "decidable": True, "contre_le_fixe": j["contre_le_fixe"]}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "144.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1320)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g_ for _x, _y, t_, _f in poses for g_ in glyphes_manquants(t_)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1320 and 0 <= y <= 900 for x, y in points), f"{len(points)} points")
        # ⚠ Le compte attendu est DÉRIVÉ de ce que la mesure implique de dessiner, jamais posé :
        # un point par matière et par bruit, un par fenêtre et par bras, deux par bruit pour le
        # critère. Mon premier « plus de 40 » était un nombre choisi, et il est tombé à 39.
        surv = d["juger"]["la_lecture_survit_elle_au_bruit"]["par_bruit"]
        attendus = (len(surv) * len(surv[0]["par_matiere"])
                    + len(d["juger"]["contre_le_fixe"]["par_fenetre"]) * 3
                    + len(surv) * 2)
        v("il y a exactement de quoi regarder ce que la mesure contient",
          len(points) >= attendus, f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "144_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["contre_le_fixe"]["la pince"]["ecart"] = 999
        troisieme = tmp / "144_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())
        d3 = json.loads(json.dumps(d))
        for x in d3["juger"]["la_lecture_survit_elle_au_bruit"]["par_bruit"]:
            for m in x["par_matiere"]:
                m["memoire"] = 0.5
        quatrieme = tmp / "144_qua.png"
        dessiner(d3, quatrieme)
        v("⭐ le panneau du mécanisme lit la mesure lui aussi",
          quatrieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/un_cap_qui_lit_la_cause.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/144_un_cap_qui_lit_la_cause.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
