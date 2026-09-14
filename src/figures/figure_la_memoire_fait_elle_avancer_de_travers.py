#!/usr/bin/env python3
"""Ce que la mémoire coûte : elle fait avancer de travers.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le mécanisme : un cap fait PENCHER
la normale, et une normale penchée fait TRAVERSER la feuille — les deux quantités, côte à côte, pour
un bras sans cap, un bras avec, et le bras réparé. En haut à droite, ce que les mâchoires rattrapent :
la traversée dépasse de loin la dérive, donc le raccrochage paie. En bas à gauche, où ça se joue,
matière par matière. En bas à droite, le seul verdict qui compte : le MÊME départ sous les deux
règles, gains à droite et pertes à gauche.

  uv run python src/figures/figure_la_memoire_fait_elle_avancer_de_travers.py \\
      --json docs/mesures/la_memoire_fait_elle_avancer_de_travers.json \\
      --sortie docs/images/148_la_memoire_fait_elle_avancer_de_travers.png
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
LIBRE = (140, 143, 148)
CAP = (176, 92, 42)
REPARE = (60, 110, 90)


def lire(chemin: Path) -> dict:
    """Le JSON de `la_memoire_fait_elle_avancer_de_travers.py`.

    ⚠⚠ Refuse une mesure dont le TÉMOIN INTERNE n'est pas vert : il est la preuve que le module
    partagé n'a rien déplacé de publié en gagnant son instrumentation.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    t = j.get("les_temoins_internes", {})
    if not t.get("decidable"):
        raise ValueError(f"{chemin} : le témoin interne est indécidable")
    if not t.get("le_protocole_est_le_meme"):
        raise ValueError(f"{chemin} : le témoin interne est ROUGE, le module partagé a bougé")
    c = j.get("le_cap_fait_il_traverser", {})
    if not c.get("decidable"):
        raise ValueError(f"{chemin} : le diagnostic de la traversée est indécidable")
    a = j.get("avancer_sur_la_lecture_repare", {})
    if not a.get("decidable") or not a.get("apparie", {}).get("decidable"):
        raise ValueError(f"{chemin} : le solde apparié de la réparation est indécidable")
    if len(j.get("par_variante", [])) < 3:
        raise ValueError(f"{chemin} : il faut les trois règles à comparer")
    return d


def _mf(v) -> str:
    return "—" if v is None else f"{v:+.3f}"


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")
            .replace("cap statique (`144`)", "avec cap (`144`)"))


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
    c_, a_ = j["le_cap_fait_il_traverser"], j["avancer_sur_la_lecture_repare"]
    ap = a_["apparie"]

    def couleur(x):
        if not x["fenetre"]:
            return LIBRE
        return REPARE if x["avance_sur_la_lecture"] else CAP

    ecrire(28, 20, "La mémoire fait avancer de travers", gros, ENCRE)
    ecrire(28, 46, f"fenêtre {g['fenetre']}, {g['departs']} départs par case, un tour, la pince · "
                   f"deux témoins internes verts : `144` par `145`, et `143` à mémoire nulle sur "
                   f"neuf nombres", petit, GRIS)

    mats = c_["par_matiere"]
    pas_y = 44

    def bandeau(x0, y0, pw, ph, titre, cle_sans, cle_avec, hi, fmt, sous):
        art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
        cadres.append((x0, y0, x0 + pw, y0 + ph))
        ecrire(x0, y0 - 24, titre, moyen, ENCRE)
        ecrire(x0 + 232, y0 + 10, "sans cap", petit, LIBRE)
        ecrire(x0 + 300, y0 + 10, "avec cap", petit, CAP)
        for k, m in enumerate(mats):
            yy = y0 + 32 + k * pas_y
            coul = CAP if m["froissee"] else GRIS
            ecrire(x0 + 8, yy, _court(m["nom"]), petit, coul)
            for i, (cle, c_b) in enumerate(((cle_sans, LIBRE), (cle_avec, CAP))):
                val = m[cle] or 0.0
                yyy = yy + 14 + i * 9
                lx = x0 + 232 + (val / hi) * (pw - 320)
                art.rectangle([x0 + 232, yyy, max(lx, x0 + 233), yyy + 7], fill=c_b)
                points.append((lx, yyy))
            ecrire(x0 + pw - 78, yy + 14,
                   fmt.format(m[cle_sans] or 0.0, m[cle_avec] or 0.0),
                   petit, coul)
        ecrire(x0 + 8, y0 + ph - 24, sous, petit, GRIS)

    hi_t = max(max(m["avec_cap_feuilles"] or 0.0, m["sans_cap_feuilles"] or 0.0)
               for m in mats) * 1.30
    bandeau(60, 122, 600, 262, "feuilles traversées en chemin",
            "sans_cap_feuilles", "avec_cap_feuilles", hi_t, "{0:.0f} → {1:.0f}",
            "en orange les matières FROISSÉES, en gris les lisses")
    hi_i = max(max(m["avec_cap_deg"] or 0.0, m["sans_cap_deg"] or 0.0)
               for m in mats) * 1.30
    bandeau(700, 122, L - 700 - 60, 262, "de combien la normale employée penche",
            "sans_cap_deg", "avec_cap_deg", hi_i, "{0:.1f}° → {1:.1f}°",
            "c'est la cause : une normale penchée incline la tangente")

    # ── Bas gauche : l'échange, règle par règle ─────────────────────────────
    x2, y2, pw2, ph2 = 60, 450, 600, 300
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "ce que chaque règle fait, sur toute la grille", moyen, ENCRE)
    cols = (("réussites", "reussites", "{0}"), ("feuilles", "memes_feuilles", "{0}"),
            ("tours", "tours_boucles", "{0}"), ("traversé", "traversee_absolue_feuilles",
             "{0:.3f}"), ("dérivé", "derive_mediane_feuilles", "{0:.3f}"))
    for i, (titre, _cle, _f) in enumerate(cols):
        ecrire(x2 + 196 + i * 78, y2 + 14, titre, petit, GRIS)
    for k, x in enumerate(pv):
        yy = y2 + 46 + k * 42
        ecrire(x2 + 8, yy, x["nom"], petit, couleur(x))
        b = x["la pince"]
        for i, (_t, cle, f) in enumerate(cols):
            val = b[cle]
            if val is None:
                val = 0.0
            ax = x2 + 190 + i * 78
            art.rectangle([ax, yy - 2, ax + 70, yy + 14], fill=BANDE)
            points.append((ax, yy))
            ecrire(ax + 8, yy, f.format(val), petit, ENCRE)
    ecrire(x2 + 8, y2 + ph2 - 62,
           "⚠ la médiane de GRILLE dit l'inverse du mécanisme : elle moyenne", petit, CAP)
    ecrire(x2 + 8, y2 + ph2 - 44, "sur l'axe même où la différence vit.", petit, CAP)
    ecrire(x2 + 8, y2 + ph2 - 22,
           f"les mâchoires rattrapent : {_mf(c_['avec_cap']['traversee_absolue_feuilles'])} "
           f"feuille traversée pour {_mf(c_['avec_cap']['derive_mediane_feuilles'])} perdue",
           petit, GRIS)

    # ── Bas droite : le solde apparié ───────────────────────────────────────
    x3, y3, pw3, ph3 = 700, 450, L - 700 - 60, 300
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "le MÊME départ, avec cap et avec la réparation", moyen, ENCRE)
    hi3 = max(ap["gains"], ap["pertes"], 1) * 1.5
    mil = x3 + pw3 * 0.5
    art.line([mil, y3 + 56, mil, y3 + 136], fill=TRAIT, width=1)
    ecrire(int(mil) - 56, y3 + 32, "perdues", petit, CAP)
    ecrire(int(mil) + 10, y3 + 32, "gagnées", petit, REPARE)
    yy = y3 + 74
    art.rectangle([mil - (ap["pertes"] / hi3) * (pw3 * 0.4), yy, mil, yy + 22], fill=CAP)
    art.rectangle([mil, yy, mil + (ap["gains"] / hi3) * (pw3 * 0.4), yy + 22], fill=REPARE)
    points.append((mil - (ap["pertes"] / hi3) * (pw3 * 0.4), yy))
    points.append((mil + (ap["gains"] / hi3) * (pw3 * 0.4), yy))
    ecrire(int(mil - (ap["pertes"] / hi3) * (pw3 * 0.4)) - 18, yy + 4, f"{ap['pertes']}",
           petit, CAP)
    ecrire(int(mil + (ap["gains"] / hi3) * (pw3 * 0.4)) + 6, yy + 4, f"{ap['gains']}",
           petit, REPARE)
    ecrire(x3 + 8, y3 + 154, f"solde {ap['solde']:+d} sur {ap['paires']} départs appariés — "
                             f"même matière, même bruit, même angle", petit, ENCRE)
    ecrire(x3 + 8, y3 + 178, f"réussites : {a_['reussites_de_la_reparation']} contre "
                             f"{a_['reussites_du_temoin']}", petit, ENCRE)
    ecrire(x3 + 8, y3 + 202, f"et elle traverse {_mf(a_['traversee_de_la_reparation_feuilles'])} "
                             f"contre {_mf(a_['traversee_du_temoin_feuilles'])} feuille",
           petit, ENCRE)
    ecrire(x3 + 8, y3 + ph3 - 26,
           "tirer la tangente de la LECTURE ne répare donc rien : elle traverse davantage",
           petit, CAP)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 786
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    dure = next(m for m in mats if "100" in m["nom"])
    ecrire(44, by0 + 12,
           f"{'★' if c_['le_mecanisme_tient'] else '✗'} un cap fait-il AVANCER DE TRAVERS ? "
           f"{c_['le_mecanisme_tient']} — PLUS sur les {c_['matieres_froissees']} matières "
           f"froissées, MOINS sur les {c_['matieres_lisses']} lisses. Cinq matières sur cinq dans "
           f"le sens que le mécanisme prédit.", moyen, ENCRE)
    ecrire(44, by0 + 36,
           f"⚠ sur une matière lisse un cap ne supprime que le bruit de lecture, qui n'est pas la "
           f"forme de la feuille ; sur une froissée il supprime aussi sa rotation RÉELLE, et la "
           f"tangente cesse alors de la longer.", petit, ENCRE)
    ecrire(44, by0 + 54,
           f"⚠⚠ sur la matière que `140` retient, la normale employée penche de "
           f"{dure['avec_cap_deg'] or 0.0:.1f}° contre "
           f"{dure['sans_cap_deg'] or 0.0:.1f}° sans cap — et personne n'y réussit un "
           f"transfert.", petit, ENCRE)
    ecrire(44, by0 + 72,
           f"{'★' if a_['elle_repare'] else '✗'} avancer sur la LECTURE ne répare pas : "
           f"{a_['reussites_de_la_reparation']} réussites contre {a_['reussites_du_temoin']}, "
           f"{ap['gains']} gagnées pour {ap['pertes']} perdues, et elle traverse DAVANTAGE.",
           petit, ENCRE)
    ecrire(44, by0 + 90,
           f"⚠ les mâchoires rattrapent l'essentiel : "
           f"{_mf(c_['avec_cap']['traversee_absolue_feuilles'])} feuille traversée en chemin pour "
           f"{_mf(c_['avec_cap']['derive_mediane_feuilles'])} réellement perdue.", petit, ENCRE)

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

    src = RACINE / "docs" / "mesures" / "la_memoire_fait_elle_avancer_de_travers.json"
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
        sans["juger"]["le_cap_fait_il_traverser"] = {"decidable": False}
        muet = json.loads(json.dumps(d))
        muet["juger"]["avancer_sur_la_lecture_repare"]["apparie"] = {"decidable": False}
        court = json.loads(json.dumps(d))
        court["juger"]["par_variante"] = court["juger"]["par_variante"][:2]
        for nom, contenu in (
                ("message", {"message": "précédent absent"}),
                ("jugement indécidable", {"juger": {"decidable": False}}),
                ("témoin ROUGE", rouge),
                ("diagnostic indécidable", sans),
                ("solde apparié indécidable", muet),
                ("deux règles seulement", court)):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except (ValueError, KeyError, StopIteration):
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        sortie = tmp / "148.png"
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
        n_ = len(j["par_variante"])
        attendus = (4 * len(j["le_cap_fait_il_traverser"]["par_matiere"]) + 5 * n_ + 2)
        v("il y a de quoi regarder ce que la mesure contient", len(points) >= attendus,
          f"{len(points)} points pour {attendus} attendus")

        autre = tmp / "148_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        d2 = json.loads(json.dumps(d))
        d2["juger"]["avancer_sur_la_lecture_repare"]["apparie"]["pertes"] += 7
        troisieme = tmp / "148_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/la_memoire_fait_elle_avancer_de_travers.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/148_la_memoire_fait_elle_avancer_de_travers.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
