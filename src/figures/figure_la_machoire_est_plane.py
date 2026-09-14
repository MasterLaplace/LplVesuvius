#!/usr/bin/env python3
"""La mâchoire est un instrument plan, et la matière froissée ne l'est pas.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la cause : la vraie normale sort
du plan du tour exactement là où la matière froisse, et pas ailleurs — les deux barres des matières
lisses sont à zéro exact. En haut à droite et en bas à gauche, les deux réfutations : l'écart ne
tombe ni quand la mâchoire rétrécit sous le voxel, ni quand on lui ajoute des appuis. En bas à
droite, le remède et sa borne — la croix paie sur les froissements modérés et presque rien sur la
matière du rouleau.

  uv run python src/figures/figure_la_machoire_est_plane.py \\
      --json docs/mesures/la_machoire_est_plane_la_matiere_ne_lest_pas.json \\
      --sortie docs/images/153_la_machoire_est_plane.png
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
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
COURBES = ((150, 152, 156), (120, 124, 130), (196, 160, 60), (176, 120, 60), (176, 60, 42))


def lire(chemin: Path) -> dict:
    """Le JSON de `la_machoire_est_plane_la_matiere_ne_lest_pas.py`.

    ⚠⚠ Refuse une mesure dont le jugement est indécidable : les trois énoncés se lisent ensemble,
    et une figure qui en dessinerait deux ressemblerait exactement à une figure qui en dessine trois.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    for cle in ("hors_plan", "geometrie", "croix"):
        if not d.get(cle, {}).get("decidable"):
            raise ValueError(f"{chemin} : « {cle} » est indécidable")
    if not d.get("juger", {}).get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    if "sur_la_matiere_du_rouleau" not in d["juger"]:
        raise ValueError(f"{chemin} : la matière du rouleau est absente du jugement")
    return d


def _court(nom: str) -> str:
    return nom.replace("spirale ", "").replace("écrasée et froissée", "é+f")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1340, 900
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    h, g, c, j = d["hors_plan"], d["geometrie"], d["croix"], d["juger"]
    dur = j["sur_la_matiere_du_rouleau"]

    ecrire(28, 20, "La mâchoire est plane, la matière froissée ne l'est pas", gros, ENCRE)
    ecrire(28, 46, f"{h['poses_par_case']} poses par case, départs recalés sur une feuille, "
                   f"pose le long de la VRAIE normale · écart APPARIÉ sur le même départ",
           petit, GRIS)

    # ---- panneau 1 : la composante axiale de la vraie normale
    x0, y0, pw, ph = 60, 122, 600, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la VRAIE normale sort-elle du plan du tour ?  |n·z| médian", moyen, ENCRE)
    mx = max(m["axial_median"] for m in h["par_matiere"]) or 1e-6
    # ⚠⚠ LES COLONNES SONT RESERVEES : une etiquette ecrite APRES la barre sort du cadre des que
    # la barre est longue, et `textes_hors_cadre` l'a dit. Le nom, la valeur et la barre ont chacun
    # leur bande, donc la longueur de la barre ne deplace plus aucun texte.
    x_nom, x_val, x_barre = x0 + 12, x0 + 150, x0 + 344
    barre_max = pw - 364
    for k, m in enumerate(h["par_matiere"]):
        yy = y0 + 30 + k * 42
        w = (m["axial_median"] / mx) * barre_max
        coul = COURBES[k % len(COURBES)]
        if w > 0.5:
            art.rectangle([x_barre, yy, x_barre + w, yy + 18], fill=coul)
            points.append((x_barre + w, yy + 9))
        else:
            art.line([x_barre, yy, x_barre, yy + 18], fill=ENCRE, width=2)
        ecrire(x_nom, yy + 2, _court(m["nom"]), petit, ENCRE)
        ecrire(x_val, yy + 2, f"{m['axial_median']:.6f}  {m['hors_plan_median_deg']:.2f}°",
               petit, coul if w > 0.5 else ENCRE)
    ecrire(x0 + 12, y0 + ph - 26,
           "un trait sans barre est un ZÉRO EXACT : une mâchoire n'en perd alors rien",
           petit, GRIS)

    # ---- panneau 2 : l'ecart contre la largeur
    x0, y0, pw, ph = 700, 122, 580, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "écart à la vraie normale contre la LARGEUR de la mâchoire", moyen, ENCRE)
    largeurs = g["largeurs"]
    n = max(len(largeurs) - 1, 1)
    vals = [x["erreur_mediane_deg"] for m in g["par_matiere"] for x in m["par_largeur"]
            if x["erreur_mediane_deg"] is not None]
    emax = max(vals) if vals else 1.0

    def px2(i):
        return x0 + 54 + i * (pw - 176) / n

    def py2(v):
        return y0 + ph - 54 - (v / max(emax, 1e-9)) * (ph - 100)

    for k in range(3):
        vv = emax * k / 2
        art.line([x0 + 46, py2(vv), x0 + pw - 116, py2(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 8, int(py2(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    art.rectangle([x0 + pw - 114, y0 + 6, x0 + pw - 6, y0 + 12 + 17 * len(g["par_matiere"])],
                  fill=FOND)
    for k, m in enumerate(g["par_matiere"]):
        coul = COURBES[k % len(COURBES)]
        xy = [(px2(i), py2(x["erreur_mediane_deg"])) for i, x in enumerate(m["par_largeur"])
              if x["erreur_mediane_deg"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + pw - 110, y0 + 8 + k * 17, _court(m["nom"]), petit, coul)
    for i, val in enumerate(largeurs):
        if i % 2 == 0 or i == len(largeurs) - 1:
            ecrire(int(px2(i)) - 14, y0 + ph - 42, f"{val:g}", petit, ENCRE)
    ecrire(x0 + 10, y0 + ph - 24,
           "en pas · la première vaut 1,38 µm, SOUS le voxel, et l'écart y tient",
           petit, ALERTE)

    # ---- panneau 3 : l'ecart contre le nombre d'appuis
    x0, y0, pw, ph = 60, 446, 600, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "écart à la vraie normale contre le NOMBRE d'appuis", moyen, ENCRE)
    appuis = g["appuis"]
    na = max(len(appuis) - 1, 1)

    def px3(i):
        return x0 + 54 + i * (pw - 176) / na

    def py3(v):
        return y0 + ph - 52 - (v / max(emax, 1e-9)) * (ph - 96)

    for k in range(3):
        vv = emax * k / 2
        art.line([x0 + 46, py3(vv), x0 + pw - 116, py3(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 8, int(py3(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    for k, m in enumerate(g["par_matiere"]):
        coul = COURBES[k % len(COURBES)]
        xy = [(px3(i), py3(x["erreur_mediane_deg"])) for i, x in enumerate(m["par_appuis"])
              if x["erreur_mediane_deg"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
    for i, val in enumerate(appuis):
        ecrire(int(px3(i)) - 6, y0 + ph - 40, f"{val:d}", petit, ENCRE)
    ecrire(x0 + 10, y0 + ph - 22,
           "à la largeur de référence · de deux à dix-sept appuis, rien ne bouge", petit, GRIS)

    # ---- panneau 4 : la croix et sa borne
    x0, y0, pw, ph = 700, 446, 580, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que la CROIX récupère, écart apparié en degrés", moyen, ENCRE)
    ap = [m for m in c["par_matiere"] if m["ecart_apparie_deg"] is not None]
    amax = max(abs(m["ecart_apparie_deg"]) for m in ap) or 1e-6
    # ⚠ Meme regle qu'au panneau 1, plus de la place sous la derniere ligne : les deux legendes
    # du bas etaient recouvertes par la cinquieme barre.
    zero = x0 + pw - 96
    barre_max = pw - 336
    for k, m in enumerate(ap):
        yy = y0 + 22 + k * 31
        w = (m["ecart_apparie_deg"] / amax) * barre_max
        coul = BON if m["ecart_apparie_deg"] < 0 else ALERTE
        art.line([zero, yy - 3, zero, yy + 19], fill=ENCRE, width=1)
        if abs(w) > 0.5:
            art.rectangle([min(zero, zero + w), yy, max(zero, zero + w), yy + 16], fill=coul)
            points.append((zero + w, yy + 8))
        ecrire(x0 + 12, yy + 1, _court(m["nom"]), petit, ENCRE)
        ecrire(x0 + 150, yy + 1, f"{m['ecart_apparie_deg']:+.3f}°", petit,
               coul if abs(w) > 0.5 else GRIS)
    ecrire(x0 + 12, y0 + ph - 48,
           f"sur la matière du rouleau : {dur['ecart_apparie_deg']:+}° "
           f"({dur['mieux']} mieux contre {dur['pire']} pire sur {dur['appariees']})",
           petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 26,
           f"contre {dur['gain_median_sur_les_froissements_moderes_deg']:+}° sur les "
           f"froissements modérés · {dur['lectures_segment']} → {dur['lectures_croix']} lectures",
           petit, GRIS)

    # ---- la bande de conclusion, sur son propre cadre RESERVE
    by = 724
    art.rectangle([0, by, L, H], fill=BANDE)
    cadres.append((0, by, L, H))
    ecrire(28, by + 18, "Le biais n'est pas dans la géométrie de la mâchoire, il est dans sa "
                        "DIMENSION", moyen, ENCRE)
    lisses = [m for m in h["par_matiere"] if m["amplitude_um"] == 0.0]
    ecrire(28, by + 46,
           f"La vraie normale sort du plan du tour exactement là où ça froisse : "
           f"|n·z| vaut {lisses[0]['axial_max']:g} sur les {len(lisses)} matières lisses et "
           f"{max(m['axial_median'] for m in h['par_matiere'])} sur celle du rouleau, soit "
           f"{max(m['hors_plan_median_deg'] for m in h['par_matiere'])}°.", petit, ENCRE)
    ecrire(28, by + 68,
           "Or une mâchoire pose ses appuis sur une DROITE et rend n' = t' x z : sa sortie est "
           "perpendiculaire à l'axe par construction, donc cette composante lui est "
           "structurellement invisible.", petit, ENCRE)
    ecrire(28, by + 90,
           "C'est pourquoi ni rétrécir sous le voxel ni monter à dix-sept appuis n'y change rien : "
           "aucun des deux ne change ce que l'instrument PEUT exprimer.", petit, ENCRE)
    ecrire(28, by + 112,
           f"Une croix, qui ajuste un plan, récupère "
           f"{dur['gain_median_sur_les_froissements_moderes_deg']:+}° sur les froissements "
           f"modérés et seulement {dur['ecart_apparie_deg']:+}° sur la matière du rouleau : la "
           f"bonne famille, et elle ne suffit pas.", petit, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1340, 900), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ---- ⚠⚠ LES SONDES DÉPLACENT DES CHAMPS QUE LA BANDE LIT VRAIMENT.
    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["sur_la_matiere_du_rouleau"]["ecart_apparie_deg"] = -7.777
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer ce que la croix récupère change ce que la bande DIT",
      any("-7.777" in t for _x, _y, t, _f in p2)
      and not any("-7.777" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for m in faux2["hors_plan"]["par_matiere"]:
        m["hors_plan_median_deg"] = 66.66
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer la sortie du plan aussi",
      any("66.66" in t for _x, _y, t, _f in p3))

    sans = copy.deepcopy(d)
    del sans["juger"]["sur_la_matiere_du_rouleau"]
    tmp = sortie.parent / "_sans_rouleau.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans la matière du rouleau est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path, default=RACINE / "docs" / "mesures"
                    / "la_machoire_est_plane_la_matiere_ne_lest_pas.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "153_la_machoire_est_plane.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
