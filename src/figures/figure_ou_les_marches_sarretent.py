#!/usr/bin/env python3
"""Où les marches s'arrêtent, et pourquoi la fenêtre ne pouvait pas les en empêcher.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le compte qui déplace le travail :
les marches de `148` meurent d'ARRÊT, pas de dérive. En haut à droite, la raison, et elle est
géométrique — le déplacement que le froissement impose à l'interstice, contre la demi-épaisseur
au-delà de laquelle la fenêtre de `142` ne peut plus le contenir. En bas à gauche, ce qu'élargir la
fenêtre change, matière par matière. En bas à droite, le seul verdict qui compte : le MÊME départ
sous les deux fenêtres.

  uv run python src/figures/figure_ou_les_marches_sarretent.py \\
      --json docs/mesures/ou_les_marches_sarretent.json \\
      --sortie docs/images/149_ou_les_marches_sarretent.png
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
ARRET = (176, 92, 42)
AILLEURS = (196, 160, 60)
REUSSI = (60, 110, 90)
NOMINALE = (140, 143, 148)
ELARGIE = (60, 110, 90)


def lire(chemin: Path) -> dict:
    """Le JSON de `ou_les_marches_sarretent.py`.

    ⚠⚠ Refuse une mesure dont le TÉMOIN INTERNE n'est pas vert : c'est la preuve que le module
    partagé n'a rien déplacé de publié en gagnant sa fenêtre élargie.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    t = j.get("les_temoins_internes", {})
    if not t.get("decidable") or not t.get("le_protocole_est_le_meme"):
        raise ValueError(f"{chemin} : le témoin interne est absent ou ROUGE")
    for cle in ("ou_les_marches_sarretent", "la_fenetre_contient_elle_linterstice",
                "elargir_repare_t_il"):
        if not j.get(cle, {}).get("decidable"):
            raise ValueError(f"{chemin} : « {cle} » est indécidable")
    e = j["elargir_repare_t_il"]
    if not e.get("par_regle") or not all(y.get("apparie", {}).get("decidable")
                                         for y in e["par_regle"]):
        raise ValueError(f"{chemin} : un solde apparié est indécidable")
    if not e.get("toutes_selargissent_vraiment"):
        raise ValueError(f"{chemin} : une fenêtre annoncée élargie ne s'élargit pas")
    if len(j.get("par_variante", [])) < 3:
        raise ValueError(f"{chemin} : il faut les trois fenêtres à comparer")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
            .replace("fenêtre ", ""))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1340, 920
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    g, j = d["sur_la_grille"], d["juger"]
    pv = j["par_variante"]
    o, f_, e_ = (j["ou_les_marches_sarretent"], j["la_fenetre_contient_elle_linterstice"],
                 j["elargir_repare_t_il"])

    def couleur(x):
        if not x["elargie"]:
            return NOMINALE
        return ELARGIE if x["elargie"] == "mesuree" else AILLEURS

    ecrire(28, 20, "Où les marches s'arrêtent", gros, ENCRE)
    ecrire(28, 46, f"fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour, la pince · "
                   f"témoin interne vert : `144` se reproduit à travers le module partagé",
           petit, GRIS)

    # ── Haut gauche : de quoi les marches meurent ───────────────────────────
    x0, y0, pw, ph = 60, 122, 600, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "de quoi meurent les marches de `148`", moyen, ENCRE)
    total = max(o["marches"], 1)
    parts = ((o["bouclees_sur_la_bonne_feuille"], REUSSI, "réussies"),
             (o["arretees"], ARRET, "ARRÊTÉES"),
             (o["sur_une_autre_feuille"], AILLEURS, "sur une autre feuille"))
    xx = x0 + 14
    for n_, c_, _t in parts:
        w = (n_ / total) * (pw - 28)
        art.rectangle([xx, y0 + 18, xx + w, y0 + 48], fill=c_)
        points.append((xx + w, y0 + 18))
        xx += w
    for i, (n_, c_, t_) in enumerate(parts):
        ecrire(x0 + 14, y0 + 60 + i * 18, f"{n_:>3}  {t_}", petit, c_)
    a_, b_ = o["une_marche_arretee"], o["une_marche_bouclee"]
    ecrire(x0 + 300, y0 + 60, "une marche arrêtée :", petit, ARRET)
    ecrire(x0 + 300, y0 + 78, f"{a_['part_du_tour_atteinte']} de tour, {a_['poses_refusees']:.0f} "
                              f"refus de POSE", petit, ARRET)
    ecrire(x0 + 300, y0 + 96, f"et {a_['refus_de_contrainte']:.0f} refus de CONTRAINTE", petit,
           ARRET)
    ecrire(x0 + 300, y0 + 120, "une marche bouclée :", petit, REUSSI)
    ecrire(x0 + 300, y0 + 138, f"{b_['part_du_tour_atteinte']} de tour, {b_['poses_refusees']:.0f} "
                               f"refus de POSE", petit, REUSSI)
    ecrire(x0 + 14, y0 + ph - 60, "c'est la POSE qui échoue, pas la contrainte de `142` :", petit,
           GRIS)
    ecrire(x0 + 14, y0 + ph - 42, "la mâchoire ne trouve plus d'interstice encadré, et la marche",
           petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 24, "s'arrête à six pour cent du tour.", petit, GRIS)

    # ── Haut droite : la fenêtre contient-elle l'interstice ─────────────────
    x1, y1, pw1, ph1 = 700, 122, L - 700 - 60, 262
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, "de combien le froissement déplace l'interstice", moyen, ENCRE)
    demi = f_["demi_epaisseur_um"]
    hi = max([x["deplacement_max_um"] for x in f_["par_matiere"]] + [demi]) * 1.35
    for k, m in enumerate(f_["par_matiere"]):
        yy = y1 + 20 + k * 33
        coul = ARRET if not m["la_fenetre_la_contient"] else GRIS
        ecrire(x1 + 8, yy, _court(m["nom"]), petit, coul)
        lx = x1 + 200 + (m["deplacement_max_um"] / hi) * (pw1 - 300)
        art.rectangle([x1 + 200, yy + 2, max(lx, x1 + 201), yy + 14], fill=coul)
        points.append((lx, yy + 2))
        ecrire(int(lx) + 6, yy, f"{m['deplacement_max_um']:.1f} µm", petit, coul)
    ref = x1 + 200 + (demi / hi) * (pw1 - 300)
    art.line([ref, y1 + 14, ref, y1 + ph1 - 62], fill=ARRET, width=2)
    ecrire(x1 + 8, y1 + ph1 - 58, f"la barre est la DEMI-épaisseur, {demi} µm : au-delà, une "
                                  f"fenêtre", petit, ARRET)
    ecrire(x1 + 8, y1 + ph1 - 42, "large d'une épaisseur ne contient plus l'interstice.", petit,
           ARRET)
    ecrire(x1 + 8, y1 + ph1 - 22,
           f"hors d'atteinte : {', '.join(_court(n) for n in f_['matieres_hors_datteinte'])} "
           f"({[x['part_hors_fenetre_pour_mille'] for x in f_['par_matiere'] if not x['la_fenetre_la_contient']]} ‰)",
           petit, GRIS)

    # ── Bas gauche : ce qu'élargir change ───────────────────────────────────
    x2, y2, pw2, ph2 = 60, 450, 600, 300
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "réussites et arrêts, matière par matière", moyen, ENCRE)
    ecrire(x2 + 264, y2 + 12, "réussites", petit, GRIS)
    ecrire(x2 + 430, y2 + 12, "arrêtées", petit, ARRET)
    mats = [m["nom"] for m in pv[0]["par_matiere"]]
    for k, nom in enumerate(mats):
        yy = y2 + 32 + k * 45
        dure = "100" in nom
        ecrire(x2 + 8, yy + 12, _court(nom), petit, ARRET if dure else ENCRE)
        for i, x in enumerate(pv):
            m = next(z for z in x["par_matiere"] if z["nom"] == nom)
            yyy = yy + i * 13
            art.rectangle([x2 + 264, yyy, x2 + 264 + (m["la pince"] / 36.0) * 120, yyy + 10],
                          fill=couleur(x))
            points.append((x2 + 264 + (m["la pince"] / 36.0) * 120, yyy))
            ecrire(x2 + 392, yyy - 1, f"{m['la pince']:>2d}", petit, couleur(x))
            art.rectangle([x2 + 430, yyy, x2 + 430 + (m["arretees"] / 36.0) * 110, yyy + 10],
                          fill=couleur(x))
            points.append((x2 + 430 + (m["arretees"] / 36.0) * 110, yyy))
            ecrire(x2 + 548, yyy - 1, f"{m['arretees']:>2d}", petit, couleur(x))
    ecrire(x2 + 8, y2 + ph2 - 38, "de haut en bas : nominale, élargie sur la mesurée, élargie sur "
                                  "la nominale.", petit, GRIS)
    ecrire(x2 + 8, y2 + ph2 - 20, "en orange, la matière que `140` retient.", petit, ARRET)

    # ── Bas droite : le solde apparié ───────────────────────────────────────
    x3, y3, pw3, ph3 = 700, 450, L - 700 - 60, 300
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "le MÊME départ, sous chaque fenêtre élargie", moyen, ENCRE)
    reg = e_["par_regle"]
    hi3 = max([max(y["apparie"]["gains"], y["apparie"]["pertes"]) for y in reg] + [1]) * 1.5
    mil = x3 + pw3 * 0.5
    art.line([mil, y3 + 42, mil, y3 + 42 + 56 * len(reg)], fill=TRAIT, width=1)
    ecrire(int(mil) - 56, y3 + 18, "perdues", petit, ARRET)
    ecrire(int(mil) + 10, y3 + 18, "gagnées", petit, ELARGIE)
    for i, y in enumerate(reg):
        ap_ = y["apparie"]
        yy = y3 + 54 + i * 56
        ecrire(x3 + 8, yy - 16, _court(y["nom"]), petit, couleur(
            {"elargie": y["elargie"]}))
        art.rectangle([mil - (ap_["pertes"] / hi3) * (pw3 * 0.4), yy, mil, yy + 18], fill=ARRET)
        art.rectangle([mil, yy, mil + (ap_["gains"] / hi3) * (pw3 * 0.4), yy + 18], fill=ELARGIE)
        points.append((mil - (ap_["pertes"] / hi3) * (pw3 * 0.4), yy))
        points.append((mil + (ap_["gains"] / hi3) * (pw3 * 0.4), yy))
        ecrire(int(mil - (ap_["pertes"] / hi3) * (pw3 * 0.4)) - 18, yy + 2, f"{ap_['pertes']}",
               petit, ARRET)
        ecrire(int(mil + (ap_["gains"] / hi3) * (pw3 * 0.4)) + 6, yy + 2,
               f"{ap_['gains']}   {y['reussites']} réussites, {y['arretees']} arrêts", petit,
               ELARGIE)
    t_ = e_["le_temoin"]
    ecrire(x3 + 8, y3 + ph3 - 76, f"le témoin « {_court(t_['nom'])} » : {t_['reussites']} "
                                  f"réussites, {t_['arretees']} arrêts", petit, ENCRE)
    d140 = e_["par_regle"][0]["sur_la_matiere_de_140"]
    ecrire(x3 + 8, y3 + ph3 - 54, f"sur la matière de `140`, la part du tour atteinte passe de "
                                  f"{t_['sur_la_matiere_de_140']['part_du_tour']}", petit, ARRET)
    ecrire(x3 + 8, y3 + ph3 - 36, f"à {d140['part_du_tour']} — la marche cesse de s'arrêter tout "
                                  f"de suite", petit, ARRET)
    ecrire(x3 + 8, y3 + ph3 - 14, "un solde positif obtenu en perdant ailleurs DÉPLACE",
           petit, GRIS)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 786
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    ecrire(44, by0 + 12,
           f"{'★' if o['les_arrets_dominent'] else '✗'} la pince ne meurt pas de dérive : "
           f"{o['arretees']} marches ARRÊTÉES contre {o['sur_une_autre_feuille']} sur une autre "
           f"feuille. Quatre échecs sur cinq sont d'une autre nature que celle qu'on traitait.",
           moyen, ENCRE)
    ecrire(44, by0 + 36,
           f"⚠ et c'est la POSE qui échoue ({o['cest_la_pose_qui_echoue']}) : "
           f"{o['une_marche_arretee']['poses_refusees']:.0f} refus de pose contre "
           f"{o['une_marche_arretee']['refus_de_contrainte']:.0f} refus de contrainte, à "
           f"{o['une_marche_arretee']['part_du_tour_atteinte']} de tour.", petit, ENCRE)
    ecrire(44, by0 + 54,
           f"★ la raison est géométrique : une fenêtre large d'une épaisseur ne contient "
           f"l'interstice que s'il n'a pas bougé de plus d'une demi-épaisseur "
           f"({demi} µm), et le froissement du rouleau le déplace de "
           f"{max(x['deplacement_max_um'] for x in f_['par_matiere'])} µm.", petit, ENCRE)
    meilleure = next(y for y in e_["par_regle"] if y["nom"] == e_["la_meilleure"])
    ecrire(44, by0 + 72,
           f"{'★' if e_['une_fenetre_elargie_repare'] else '✗'} élargir la fenêtre répare-t-il ? "
           f"{e_['une_fenetre_elargie_repare']} — la meilleure, « {_court(e_['la_meilleure'])} », "
           f"rend {meilleure['reussites']} réussites contre {e_['le_temoin']['reussites']}, "
           f"{meilleure['apparie']['gains']} gagnées pour {meilleure['apparie']['pertes']} "
           f"perdues.", petit, ENCRE)
    ecrire(44, by0 + 90,
           f"⚠ et elle n'arrête pas moins ({e_['une_fenetre_elargie_arrete_moins']}) : la fenêtre "
           f"élargie attrape l'interstice VOISIN, ce que la fenêtre d'une épaisseur existait "
           f"précisément pour interdire.", petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "ou_les_marches_sarretent.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        j = d["juger"]
        rouge = json.loads(json.dumps(d))
        rouge["juger"]["les_temoins_internes"]["le_protocole_est_le_meme"] = False
        fige = json.loads(json.dumps(d))
        fige["juger"]["elargir_repare_t_il"]["toutes_selargissent_vraiment"] = False
        sans = json.loads(json.dumps(d))
        sans["juger"]["la_fenetre_contient_elle_linterstice"] = {"decidable": False}
        muet = json.loads(json.dumps(d))
        for y_ in muet["juger"]["elargir_repare_t_il"]["par_regle"]:
            y_["apparie"] = {"decidable": False}
        court = json.loads(json.dumps(d))
        court["juger"]["par_variante"] = court["juger"]["par_variante"][:1]
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoin ROUGE", rouge),
                ("fenêtre qui ne s'élargit pas", fige),
                ("géométrie indécidable", sans),
                ("solde apparié indécidable", muet),
                ("une seule fenêtre", court)):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except (ValueError, KeyError, StopIteration):
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "149.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1340)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g_ for _x, _y, t_, _f in poses for g_ in glyphes_manquants(t_)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1340 and 0 <= y <= 920 for x, y in points), f"{len(points)} points")
        attendus = (3 + len(j["la_fenetre_contient_elle_linterstice"]["par_matiere"])
                    + 4 * len(j["par_variante"][0]["par_matiere"]) + 2)
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "149_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["ou_les_marches_sarretent"]["arretees"] += 7
        troisieme = tmp / "149_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/ou_les_marches_sarretent.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/149_ou_les_marches_sarretent.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
