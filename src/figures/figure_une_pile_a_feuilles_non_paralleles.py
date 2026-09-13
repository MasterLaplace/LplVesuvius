#!/usr/bin/env python3
"""Des feuilles non parallèles font-elles virer le marcheur comme le rouleau ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** Six piles froissées
ont reçu, par bissection, l'amplitude qui reproduit le **désaccord des deux moitiés du cube** mesuré
sur le vrai rouleau — sans jamais regarder le virage du marcheur. Le panneau de GAUCHE montre que
la calibration tient : le désaccord rencontré le long de la marche tombe sur la cible réelle. Le
panneau de DROITE montre ce que le marcheur fait alors : combien il vire par pas, contre la
fourchette réelle. Une pile dont le désaccord est celui du rouleau et dont le virage ne l'est pas
dit que le désaccord n'est pas ce qui fait virer.

  ⭐⭐⭐ Deux froissements : le même sur toutes les feuilles (« en phase »), ou un par feuille. Trois
  longueurs d'onde dérivées du cube de lecture : une, deux et quatre fois son côté.

  uv run python src/figures/figure_une_pile_a_feuilles_non_paralleles.py \\
      --json docs/mesures/une_pile_a_feuilles_non_paralleles.json \\
      --sortie docs/images/134_des_feuilles_non_paralleles.png
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
REEL = (60, 110, 90)
BANDE_REELLE = (214, 232, 222)
EN_PHASE = (86, 104, 132)
PAR_FEUILLE = (196, 140, 60)
CONTROLE = (160, 162, 166)
MEMOIRE = (176, 62, 62)


def lire(chemin: Path) -> dict:
    """Le JSON de `une_pile_a_feuilles_non_paralleles.py`.

    ⚠⚠ Refuse un JSON sans désaccord réel ou sans pile : dessiner une fourchette absente ou un
    panneau vide produirait une image juste au pixel près au sujet de rien.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    r = d.get("desaccord_reel", {})
    if not r.get("n") or not r.get("virage_par_pas", {}).get("n"):
        raise ValueError(f"{chemin} : pas de désaccord réel, ou pas de virage réel")
    if not d.get("par_longueur_donde"):
        raise ValueError(f"{chemin} ne porte aucune pile")
    for x in d["par_longueur_donde"]:
        if not any(m["memoire"] == 0.0 for m in x["marche"]["par_memoire"]):
            raise ValueError(f"{chemin} : une pile n'a pas de marche à mémoire nulle")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres."""
    reel = d["desaccord_reel"]
    vr = reel["virage_par_pas"]
    ctrl = d["controle_pile_plane"]
    piles = d["par_longueur_donde"]
    L, H = 1180, 640
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    def coul(x):
        return PAR_FEUILLE if x.get("variante") == "par_feuille" else EN_PHASE

    def nom(x):
        return (f"{'par feuille' if x.get('variante') == 'par_feuille' else 'en phase'} · "
                f"λ {x['longueur_donde_um']:.0f} µm · A {x['calibration']['amplitude_um']:.1f}")

    ecrire(28, 20, "Des feuilles non parallèles font-elles virer le marcheur comme le rouleau ?",
           gros, ENCRE)
    ecrire(28, 46, f"{len(piles)} piles calibrées sur le désaccord réel ({reel['source']}, "
                   f"{reel['n']} pas voyants) · {d.get('pas')} pas · {len(d.get('graines', []))} "
                   f"graines", petit, GRIS)

    lignes = ["réel", "pile plane (contrôle)"] + [nom(x) for x in piles]
    n = len(lignes)
    y0, hl = 112, 40
    ph = n * hl + 24

    # ── Gauche : le désaccord des moitiés ────────────────────────────────────
    x0, pw = 40, 520
    ecrire(x0, y0 - 26, "le désaccord des deux moitiés du cube, en degrés", moyen, ENCRE)
    maxd = max(25.0, reel["p90"] + 2.0,
               max(m["desaccord_rencontre_median_deg"] for x in piles
                   for m in x["marche"]["par_memoire"]) + 2.0)
    # ⚠ La dernière graduation tient DANS le panneau : `pw - 220` laisse la place du « 25° ».
    ex = (pw - 220) / maxd
    gx = x0 + 190

    def xg(v):
        return gx + v * ex

    art.rectangle([xg(reel["p25"]), y0, xg(reel["p75"]), y0 + ph], fill=BANDE_REELLE)
    art.line([xg(reel["mediane"]), y0, xg(reel["mediane"]), y0 + ph], fill=REEL, width=1)
    for i, txt in enumerate(lignes):
        y = y0 + 12 + i * hl
        ecrire(x0, y + 6, txt, petit, ENCRE if i >= 2 else GRIS)
        if i == 0:
            art.line([xg(reel["p25"]), y + 12, xg(reel["p75"]), y + 12], fill=REEL, width=3)
            art.ellipse([xg(reel["mediane"]) - 4, y + 8, xg(reel["mediane"]) + 4, y + 16], fill=REEL)
        elif i == 1:
            q = ctrl["desaccord"]
            art.line([xg(q["p25"]), y + 12, xg(q["p75"]), y + 12], fill=CONTROLE, width=3)
            art.ellipse([xg(q["mediane"]) - 4, y + 8, xg(q["mediane"]) + 4, y + 16], fill=CONTROLE)
        else:
            x = piles[i - 2]
            c = x["calibration"]
            m0 = next(m for m in x["marche"]["par_memoire"] if m["memoire"] == 0.0)
            # la cible atteinte par la calibration (cubes au hasard) : un trait fin ; le désaccord
            # RENCONTRÉ le long de la marche : le point. Les deux doivent tomber sur la bande.
            art.line([xg(c["mediane_deg"]) - 6, y + 12, xg(c["mediane_deg"]) + 6, y + 12],
                     fill=coul(x), width=2)
            art.ellipse([xg(m0["desaccord_rencontre_median_deg"]) - 4, y + 8,
                         xg(m0["desaccord_rencontre_median_deg"]) + 4, y + 16], fill=coul(x))
            if not c.get("atteint", True):
                ecrire(int(xg(c["mediane_deg"])) + 10, y + 6, "cible non atteinte", petit, MEMOIRE)
    art.line([gx, y0 + ph, xg(maxd), y0 + ph], fill=TRAIT, width=1)
    for v in (0, 5, 10, 15, 20, 25):
        if v <= maxd:
            ecrire(int(xg(v)) - 6, y0 + ph + 6, f"{v}°", petit, GRIS)
    ecrire(x0, y0 + ph + 26, "trait : cible calibrée sur des cubes au hasard · point : rencontré "
                             "le long de la marche", petit, GRIS)
    ecrire(x0, y0 + ph + 44, f"bande : p25–p75 réel [{reel['p25']} ; {reel['p75']}], "
                             f"médiane {reel['mediane']}°", petit, REEL)

    # ── Droite : le virage par pas ───────────────────────────────────────────
    x1, pw2 = x0 + pw + 60, L - (x0 + pw + 60) - 30
    ecrire(x1, y0 - 26, "le virage du marcheur par pas, mémoire nulle", moyen, ENCRE)
    maxv = max(20.0, vr["p90"] + 2.0,
               max(m["virage_median_deg"] for x in piles for m in x["marche"]["par_memoire"]) + 2.0)
    # ⚠ Les étiquettes vivent dans une COLONNE à droite de l'axe, pas au bout de chaque barre :
    # au bout d'une barre longue elles sortaient du panneau (la sonde de cadre l'a dit).
    ex2 = (pw2 - 250) / maxv
    gx2 = x1

    def xv(v):
        return gx2 + v * ex2

    art.rectangle([xv(vr["p25"]), y0, xv(vr["p75"]), y0 + ph], fill=BANDE_REELLE)
    art.line([xv(vr["mediane"]), y0, xv(vr["mediane"]), y0 + ph], fill=REEL, width=1)
    for i, txt in enumerate(lignes):
        y = y0 + 12 + i * hl
        if i == 0:
            art.line([xv(vr["p25"]), y + 12, xv(vr["p75"]), y + 12], fill=REEL, width=3)
            art.ellipse([xv(vr["mediane"]) - 4, y + 8, xv(vr["mediane"]) + 4, y + 16], fill=REEL)
            ecrire(int(xv(maxv)) + 8, y + 6, f"réel {vr['mediane']}° [{vr['p25']} ; {vr['p75']}]",
                   petit, REEL)
        elif i == 1:
            v = ctrl["marche"]["virage_median_deg"]
            art.rectangle([gx2, y + 6, xv(v), y + 18], fill=CONTROLE)
            ecrire(int(xv(maxv)) + 8, y + 6, f"{v}° · rectitude "
                                              f"{ctrl['marche']['rectitude_mediane']:.3f}", petit, GRIS)
        else:
            x = piles[i - 2]
            m0 = next(m for m in x["marche"]["par_memoire"] if m["memoire"] == 0.0)
            art.rectangle([gx2, y + 6, xv(m0["virage_median_deg"]), y + 18], fill=coul(x))
            etiquette = (f"{m0['virage_median_deg']}° · rectitude {m0['rectitude_mediane']:.3f}"
                         + (f" · cos {m0['cos_virages_median']:+.2f}"
                            if m0.get("cos_virages_median") is not None else ""))
            ecrire(int(xv(maxv)) + 8, y + 6, etiquette, petit, ENCRE)
            # la mémoire 0,75 : un point d'alerte, là où elle ramène le virage
            m1 = next((m for m in x["marche"]["par_memoire"] if m["memoire"] > 0.0), None)
            if m1 is not None:
                art.ellipse([xv(m1["virage_median_deg"]) - 3, y + 9,
                             xv(m1["virage_median_deg"]) + 3, y + 15], fill=MEMOIRE)
    art.line([gx2, y0 + ph, xv(maxv), y0 + ph], fill=TRAIT, width=1)
    for v in range(0, int(maxv) + 1, 5):
        ecrire(int(xv(v)) - 6, y0 + ph + 6, f"{v}°", petit, GRIS)
    ecrire(x1, y0 + ph + 26, "barre : mémoire nulle · point rouge : mémoire 0,75 · cos : "
                             "persistance du virage", petit, GRIS)
    if reel.get("cos_virages_median") is not None:
        ecrire(x1, y0 + ph + 44, f"sur le rouleau le virage alterne : cos "
                                 f"{reel['cos_virages_median']:+.4f} (`132`)", petit, REEL)

    # ── Le verdict ───────────────────────────────────────────────────────────
    pv = d.get("par_variante", {})
    yv = H - 52
    for k, lib, c in (("en_phase", "en phase", EN_PHASE), ("par_feuille", "par feuille", PAR_FEUILLE)):
        if k in pv:
            x = pv[k]
            mot = ("vire comme le rouleau à une longueur d'onde au moins"
                   if x["une_longueur_donde_vire_comme_le_rouleau"]
                   else "vire moins que le rouleau à toutes les longueurs d'onde"
                   if x["toutes_virent_moins"] else "ne tombe dans la fourchette réelle à aucune "
                                                     "longueur d'onde")
            ecrire(28, yv, f"{lib} : {mot} · virages {x['virages_deg']}", moyen, c)
            yv += 22

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0 - 30, x0 + pw, y0 + ph + 60), (x1 - 4, y0 - 30, L - 4, y0 + ph + 60)]


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et des sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def pile(variante, ld, amp, virage0, virage1, rect, atteint=True):
        return {"variante": variante, "longueur_donde_um": ld,
                "calibration": {"amplitude_um": amp, "mediane_deg": 8.2, "atteint": atteint,
                                "inclinaison_max_deg": 25.0},
                "marche": {"par_memoire": [
                    {"memoire": 0.0, "virage_median_deg": virage0, "rectitude_mediane": rect,
                     "desaccord_rencontre_median_deg": 8.5, "cos_virages_median": -0.31,
                     "erreur_mediane_deg": 3.0, "taux_median": 1.0},
                    {"memoire": 0.75, "virage_median_deg": virage1, "rectitude_mediane": 0.999,
                     "desaccord_rencontre_median_deg": 8.4, "cos_virages_median": -0.2,
                     "erreur_mediane_deg": 9.0, "taux_median": 1.0}]},
                "verdict": {"decidable": True}}

    faux = {"pas": 112, "graines": [3, 11, 29],
            "desaccord_reel": {"n": 1043, "mediane": 8.19, "p25": 4.84, "p75": 13.58, "p90": 23.23,
                               "source": "c.json", "cos_virages_median": -0.2061,
                               "virage_par_pas": {"n": 16, "mediane": 13.59, "p25": 13.28,
                                                  "p75": 14.54, "p90": 16.0}},
            "controle_pile_plane": {"desaccord": {"mediane": 2.81, "p25": 1.9, "p75": 4.0, "p90": 6.6},
                                    "marche": {"virage_median_deg": 2.46, "rectitude_mediane": 0.9994}},
            "par_longueur_donde": [pile("en_phase", 98.4, 6.8, 3.1, 0.55, 0.999),
                                   pile("en_phase", 196.8, 16.1, 5.57, 0.69, 0.996),
                                   pile("en_phase", 393.6, 47.5, 4.67, 0.65, 0.996),
                                   pile("par_feuille", 98.4, 7.2, 2.94, 0.58, 0.999),
                                   pile("par_feuille", 196.8, 15.3, 7.18, 1.75, 0.991),
                                   pile("par_feuille", 393.6, 47.5, 14.72, 3.2, 0.964)],
            "par_variante": {"en_phase": {"une_longueur_donde_vire_comme_le_rouleau": False,
                                          "toutes_virent_moins": True, "virages_deg": [3.1, 5.57, 4.67]},
                             "par_feuille": {"une_longueur_donde_vire_comme_le_rouleau": False,
                                             "toutes_virent_moins": False,
                                             "virages_deg": [2.94, 7.18, 14.72]}}}
    with tempfile.TemporaryDirectory() as dtmp:
        r = Path(dtmp)
        j = r / "p.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["par_longueur_donde"]), 6)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
            else list(im.getdata())
        v("les deux froissements ont deux couleurs",
          pixels.count(EN_PHASE) > 200 and pixels.count(PAR_FEUILLE) > 200)
        v("la fourchette réelle est peinte", pixels.count(BANDE_REELLE) > 500)
        v("la mémoire 0,75 est marquée", pixels.count(MEMOIRE) > 30)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])
        v("le verdict des deux variantes est écrit",
          any(t.startswith("en phase :") for _, _, t, _ in poses)
          and any(t.startswith("par feuille :") for _, _, t, _ in poses))
        # ⚠⚠ Une cible non atteinte doit se LIRE sur l'image, sinon une calibration ratée passe
        # pour une calibration.
        rate = json.loads(json.dumps(faux))
        rate["par_longueur_donde"][0]["calibration"]["atteint"] = False
        j.write_text(json.dumps(rate), encoding="utf-8")
        _, poses2, _ = dessiner(lire(j), r / "g.png")
        v("sonde : une cible non atteinte est écrite sur l'image",
          any("cible non atteinte" in t for _, _, t, _ in poses2))
        for nom_, bris in (("sans pile", lambda x: x.update(par_longueur_donde=[])),
                           ("sans désaccord réel", lambda x: x.update(desaccord_reel={"n": 0})),
                           ("sans marche à mémoire nulle", lambda x: x["par_longueur_donde"][0]
                            ["marche"].update(par_memoire=[{"memoire": 0.75}]))):
            c = json.loads(json.dumps(faux))
            bris(c)
            j.write_text(json.dumps(c), encoding="utf-8")
            try:
                lire(j)
                v(f"sonde : un JSON {nom_} est refusé", False)
            except ValueError:
                v(f"sonde : un JSON {nom_} est refusé", True)
        j.write_text(json.dumps(faux), encoding="utf-8")
        dessiner(lire(j), r / "h.png")
        v("deux rendus du même JSON sont identiques au bit",
          (r / "f.png").read_bytes() == (r / "h.png").read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "une_pile_a_feuilles_non_paralleles.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "134_des_feuilles_non_paralleles.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
