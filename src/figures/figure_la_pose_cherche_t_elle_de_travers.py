#!/usr/bin/env python3
"""La mâchoire n'échoue pas parce qu'elle est large, elle échoue parce qu'elle cherche de travers.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'hypothèse réfutée : la pose
réussit à toutes les largeurs de mâchoire, y compris sur la matière du rouleau. En haut à droite, ce
qui la fait réellement échouer — l'inclinaison de la normale le long de laquelle elle cherche, avec
l'angle que `148` mesure vraiment tracé en repère. En bas à gauche, ce que la réparation change
matière par matière. En bas à droite, le seul verdict qui compte : le MÊME départ sous les deux
poses.

  uv run python src/figures/figure_la_pose_cherche_t_elle_de_travers.py \\
      --json docs/mesures/la_pose_cherche_t_elle_de_travers.json \\
      --sortie docs/images/150_la_pose_cherche_t_elle_de_travers.png
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
ALERTE = (176, 92, 42)
TEMOIN = (140, 143, 148)
LECTURE = (60, 110, 90)
COURBES = ((150, 152, 156), (120, 124, 130), (196, 160, 60), (176, 120, 60), (176, 60, 42))


def lire(chemin: Path) -> dict:
    """Le JSON de `la_pose_cherche_t_elle_de_travers.py`.

    ⚠⚠ Refuse une mesure dont le TÉMOIN INTERNE n'est pas vert, et une mesure dont les poses ne
    sont pas décidables : les deux panneaux du haut n'existent que par elles.
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
    for cle in ("la_pose_resiste_t_elle", "la_largeur_est_elle_en_cause",
                "linclinaison_est_elle_en_cause", "poser_sur_la_lecture_repare"):
        if not j.get(cle, {}).get("decidable"):
            raise ValueError(f"{chemin} : « {cle} » est indécidable")
    if not j["poser_sur_la_lecture_repare"].get("apparie", {}).get("decidable"):
        raise ValueError(f"{chemin} : le solde apparié est indécidable")
    if "ce_que_148_mesure" not in j["linclinaison_est_elle_en_cause"]:
        raise ValueError(f"{chemin} : le lien à l'angle que `148` mesure est absent")
    if len(j.get("par_variante", [])) < 2:
        raise ValueError(f"{chemin} : il faut les deux poses à comparer")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
            .replace("pose sur le mélange", "mélange").replace("pose sur la ", ""))


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
    p_, lg, inc = (j["la_pose_resiste_t_elle"], j["la_largeur_est_elle_en_cause"],
                   j["linclinaison_est_elle_en_cause"])
    e_ = j["poser_sur_la_lecture_repare"]
    ap = e_["apparie"]
    c148 = inc["ce_que_148_mesure"]

    ecrire(28, 20, "La pose cherche de travers", gros, ENCRE)
    ecrire(28, 46, f"{p_['poses_par_case']} poses par case, à un départ recalé sur une feuille · "
                   f"puis {g['departs']} départs par case sur un tour · témoin interne vert : "
                   f"`144` se reproduit", petit, GRIS)

    def courbes(x0, y0, pw, ph, titre, cle_x, cle_v, fmt, sous, repere=None):
        art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
        cadres.append((x0, y0, x0 + pw, y0 + ph))
        ecrire(x0, y0 - 24, titre, moyen, ENCRE)
        xs = p_[cle_x]
        n = max(len(xs) - 1, 1)

        def px(i):
            return x0 + 60 + i * (pw - 190) / n

        def py(v):
            return y0 + ph - 56 - (v / 1000.0) * (ph - 96)

        for k in range(3):
            vv = 1000 * k / 2
            art.line([x0 + 52, py(vv), x0 + pw - 122, py(vv)], fill=TRAIT, width=1)
            ecrire(x0 + 12, int(py(vv)) - 7, f"{vv:.0f}", petit, GRIS)
        art.rectangle([x0 + pw - 120, y0 + 6, x0 + pw - 6, y0 + 12 + 17 * len(p_["par_matiere"])],
                      fill=FOND)
        for k, m in enumerate(p_["par_matiere"]):
            coul = COURBES[k % len(COURBES)]
            serie = m["par_largeur" if cle_x == "largeurs" else "par_inclinaison"]
            xy = [(px(i), py(x[cle_v])) for i, x in enumerate(serie)]
            if len(xy) > 1:
                art.line([p for q in xy for p in q], fill=coul, width=2)
            for a_, b_ in xy:
                art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
                points.append((a_, b_))
            ecrire(x0 + pw - 116, y0 + 8 + k * 17, _court(m["nom"]), petit, coul)
        for i, val in enumerate(xs):
            ecrire(int(px(i)) - 14, y0 + ph - 44, fmt.format(val), petit, ENCRE)
        if repere is not None:
            # ⚠ Le repere se place sur l'axe REEL, pas sur un axe suppose lineaire depuis zero :
            # les abscisses sont les valeurs mesurees, et elles ne commencent pas forcement a zero.
            bas, haut = float(xs[0]), float(xs[-1])
            rx = px(0) + ((float(repere) - bas) / max(haut - bas, 1e-9)) * (px(n) - px(0))
            art.line([rx, y0 + 14, rx, y0 + ph - 50], fill=ALERTE, width=2)
        ecrire(x0 + 12, y0 + ph - 24, sous, petit, GRIS)

    courbes(60, 122, 600, 262, "poses réussies pour mille, selon la LARGEUR de la mâchoire",
            "largeurs", "part_pour_mille", "{0:g}",
            "la pose tient à toutes les largeurs : ce n'est pas elle qui empêche")
    courbes(700, 122, L - 700 - 60, 262,
            "… et selon l'INCLINAISON de la normale où elle cherche",
            "inclinaisons_deg", "part_pour_mille", "{0:g}°",
            f"la barre est l'angle que `148` mesure vraiment : {c148['inclinaison_deg']}°",
            repere=c148["inclinaison_deg"])

    # ── Bas gauche : les deux poses, matière par matière ────────────────────
    x2, y2, pw2, ph2 = 60, 450, 600, 300
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "réussites et arrêts des deux poses, matière par matière", moyen, ENCRE)
    ecrire(x2 + 264, y2 + 12, "réussites", petit, GRIS)
    ecrire(x2 + 430, y2 + 12, "arrêtées", petit, ALERTE)
    mats = [m["nom"] for m in pv[0]["par_matiere"]]
    for k, nom in enumerate(mats):
        yy = y2 + 40 + k * 44
        dure = "100" in nom
        ecrire(x2 + 8, yy + 6, _court(nom), petit, ALERTE if dure else ENCRE)
        for i, x in enumerate(pv):
            m = next(z for z in x["par_matiere"] if z["nom"] == nom)
            coul = LECTURE if x["lecture"] else TEMOIN
            yyy = yy + i * 15
            art.rectangle([x2 + 264, yyy, x2 + 264 + (m["la pince"] / 36.0) * 120, yyy + 12],
                          fill=coul)
            points.append((x2 + 264 + (m["la pince"] / 36.0) * 120, yyy))
            ecrire(x2 + 392, yyy, f"{m['la pince']:>2d}", petit, coul)
            art.rectangle([x2 + 430, yyy, x2 + 430 + (m["arretees"] / 36.0) * 110, yyy + 12],
                          fill=coul)
            points.append((x2 + 430 + (m["arretees"] / 36.0) * 110, yyy))
            ecrire(x2 + 548, yyy, f"{m['arretees']:>2d}", petit, coul)
    ecrire(x2 + 8, y2 + ph2 - 42, "en gris la pose sur le mélange, en vert la pose sur la lecture.",
           petit, GRIS)
    ecrire(x2 + 8, y2 + ph2 - 22, "en orange, la matière que `140` retient.", petit, ALERTE)

    # ── Bas droite : le solde apparié ───────────────────────────────────────
    x3, y3, pw3, ph3 = 700, 450, L - 700 - 60, 300
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "le MÊME départ, sous les deux poses", moyen, ENCRE)
    hi3 = max(ap["gains"], ap["pertes"], 1) * 1.5
    mil = x3 + pw3 * 0.5
    art.line([mil, y3 + 56, mil, y3 + 136], fill=TRAIT, width=1)
    ecrire(int(mil) - 56, y3 + 32, "perdues", petit, ALERTE)
    ecrire(int(mil) + 10, y3 + 32, "gagnées", petit, LECTURE)
    yy = y3 + 74
    art.rectangle([mil - (ap["pertes"] / hi3) * (pw3 * 0.4), yy, mil, yy + 22], fill=ALERTE)
    art.rectangle([mil, yy, mil + (ap["gains"] / hi3) * (pw3 * 0.4), yy + 22], fill=LECTURE)
    points.append((mil - (ap["pertes"] / hi3) * (pw3 * 0.4), yy))
    points.append((mil + (ap["gains"] / hi3) * (pw3 * 0.4), yy))
    ecrire(int(mil - (ap["pertes"] / hi3) * (pw3 * 0.4)) - 18, yy + 4, f"{ap['pertes']}",
           petit, ALERTE)
    ecrire(int(mil + (ap["gains"] / hi3) * (pw3 * 0.4)) + 6, yy + 4, f"{ap['gains']}",
           petit, LECTURE)
    ecrire(x3 + 8, y3 + 154, f"solde {ap['solde']:+d} sur {ap['paires']} départs appariés",
           petit, ENCRE)
    ecrire(x3 + 8, y3 + 178, f"réussites : {e_['reussites_de_la_reparation']} contre "
                             f"{e_['reussites_du_temoin']}", petit, ENCRE)
    ecrire(x3 + 8, y3 + 202, f"arrêtées : {e_['arretees_de_la_reparation']} contre "
                             f"{e_['arretees_du_temoin']}", petit, ENCRE)
    ecrire(x3 + 8, y3 + 226, f"la normale employée penche de "
                             f"{e_['inclinaison_de_la_reparation_deg']}° contre "
                             f"{e_['inclinaison_du_temoin_deg']}°", petit, ENCRE)
    ecrire(x3 + 8, y3 + ph3 - 26,
           "un solde positif obtenu en perdant ailleurs DÉPLACE", petit, GRIS)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 786
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    dure = next(m for m in p_["par_matiere"] if m["amplitude_um"] == 100.0)
    etroite = dure["par_largeur"][0]
    large = next(x for x in dure["par_largeur"]
                 if x["largeur_en_pas"] == p_["largeur_de_reference"])
    ecrire(44, by0 + 12,
           f"{'★' if lg['la_largeur_est_en_cause'] else '✗'} la LARGEUR de la mâchoire est-elle "
           f"en cause ? {lg['la_largeur_est_en_cause']} — sur la matière du rouleau la pose "
           f"réussit {large['part_pour_mille']} ‰ à {large['largeur_en_pas']:g} pas contre "
           f"{etroite['part_pour_mille']} ‰ à {etroite['largeur_en_pas']:g}.", moyen, ENCRE)
    ecrire(44, by0 + 36,
           f"{'★' if inc['pencher_fait_echouer_la_pose'] else '✗'} l'INCLINAISON, elle, l'est : "
           f"{inc['pencher_fait_echouer_la_pose']} — à {inc['inclinaison_forte_deg']:g}° la pose "
           f"y tombe à "
           f"{next(x['penchee_pour_mille'] for x in inc['par_matiere'] if '100' in x['nom'])} ‰ "
           f"contre "
           f"{next(x['droite_pour_mille'] for x in inc['par_matiere'] if '100' in x['nom'])} ‰ à "
           f"normale droite.", petit, ENCRE)
    ecrire(44, by0 + 54,
           f"★ et c'est ce qui relie `148` à `149` : le cap incline la normale employée de "
           f"{c148['inclinaison_deg']}° sur cette matière, et la pose y réussit déjà "
           f"{c148['pose_a_cet_angle_pour_mille']} ‰ contre "
           f"{c148['pose_a_normale_droite_pour_mille']} ‰ — la marche meurt de ses refus de pose.",
           petit, ENCRE)
    ecrire(44, by0 + 72,
           f"{'★' if e_['elle_repare'] else '✗'} poser sur la LECTURE plutôt que sur le mélange "
           f"répare-t-il ? {e_['elle_repare']} — {e_['reussites_de_la_reparation']} réussites "
           f"contre {e_['reussites_du_temoin']}, {ap['gains']} gagnées pour {ap['pertes']} "
           f"perdues.", petit, ENCRE)
    ecrire(44, by0 + 90,
           "⚠ la lecture a un pas d'âge, et l'avance vaut un quart de longueur d'onde : la feuille "
           "a déjà tourné quand la mâchoire s'y pose.", petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "la_pose_cherche_t_elle_de_travers.json"
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
        sans = json.loads(json.dumps(d))
        sans["juger"]["la_pose_resiste_t_elle"] = {"decidable": False}
        muet = json.loads(json.dumps(d))
        muet["juger"]["poser_sur_la_lecture_repare"]["apparie"] = {"decidable": False}
        delie = json.loads(json.dumps(d))
        del delie["juger"]["linclinaison_est_elle_en_cause"]["ce_que_148_mesure"]
        court = json.loads(json.dumps(d))
        court["juger"]["par_variante"] = court["juger"]["par_variante"][:1]
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoin ROUGE", rouge),
                ("poses indécidables", sans),
                ("solde apparié indécidable", muet),
                ("lien à `148` absent", delie),
                ("une seule pose", court)):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except (ValueError, KeyError, StopIteration):
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "150.png"
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
        n_ = len(j["la_pose_resiste_t_elle"]["par_matiere"])
        attendus = (n_ * len(j["la_pose_resiste_t_elle"]["largeurs"])
                    + n_ * len(j["la_pose_resiste_t_elle"]["inclinaisons_deg"])
                    + 4 * len(j["par_variante"][0]["par_matiere"]) + 2)
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "150_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["linclinaison_est_elle_en_cause"]["ce_que_148_mesure"][
            "pose_a_cet_angle_pour_mille"] += 300
        troisieme = tmp / "150_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/la_pose_cherche_t_elle_de_travers.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/150_la_pose_cherche_t_elle_de_travers.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
