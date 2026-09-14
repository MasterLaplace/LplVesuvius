"""Rejeter un appui qui a sauté d'interstice, plutôt qu'élargir ou rétrécir.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la réfutation : élargir la fenêtre
fait monter l'erreur à toutes les largeurs, donc les deux contraintes ne se compensent pas. En haut à
droite, ce qu'il y a à rejeter — l'étalement des appuis contre la demi-épaisseur, et le compte des
aberrants. En bas à gauche, ce que le rejet répare, bras par bras. En bas à droite, le seul chiffre
qui dit de combien l'instrument s'est rapproché de sa matière : son rapport à l'échelle de `154`.

  uv run python src/figures/figure_rejeter_un_appui_qui_a_saute.py \\
      --json docs/mesures/rejeter_un_appui_qui_a_saute.json \\
      --sortie docs/images/155_rejeter_un_appui_qui_a_saute.png
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
    """Le JSON de `rejeter_un_appui_qui_a_saute.py`.

    ⚠⚠ Refuse une mesure sans la case décisive : les quatre panneaux en dépendent, et une figure
    dessinée sur un verdict absent ressemble exactement à une figure dessinée sur un verdict présent.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    for cle in ("grille", "recensement", "rejet"):
        if not d.get(cle, {}).get("decidable"):
            raise ValueError(f"{chemin} : « {cle} » est indécidable")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if "sur_la_matiere_du_rouleau" not in j:
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

    g, rc, rj, j = d["grille"], d["recensement"], d["rejet"], d["juger"]
    dur = j["sur_la_matiere_du_rouleau"]

    ecrire(28, 20, "Rejeter un appui qui a sauté, plutôt qu'élargir ou rétrécir", gros, ENCRE)
    ecrire(28, 46, f"{g['poses_par_case']} poses par case, départs recalés · le rejet écarte tout "
                   f"appui à plus d'une DEMI-ÉPAISSEUR ({rc['demi_epaisseur_um']} µm) de la "
                   f"médiane de sa mâchoire", petit, GRIS)

    # ---- panneau 1 : la grille largeur x marge sur la matiere du rouleau
    x0, y0, pw, ph = 60, 122, 600, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "élargir la fenêtre, à chaque largeur de mâchoire", moyen, ENCRE)
    mat = next(m for m in g["par_matiere"] if m["amplitude_um"] == 100.0)
    marges = g["marges_um"]
    n = max(len(marges) - 1, 1)
    vals = [c["erreur_mediane_deg"] for c in mat["cases"] if c["erreur_mediane_deg"] is not None]
    emax = max(vals) if vals else 1.0

    def px1(i):
        return x0 + 54 + i * (pw - 186) / n

    def py1(v):
        return y0 + ph - 54 - (v / max(emax, 1e-9)) * (ph - 100)

    for k in range(3):
        vv = emax * k / 2
        art.line([x0 + 46, py1(vv), x0 + pw - 126, py1(vv)], fill=TRAIT, width=1)
        ecrire(x0 + 8, int(py1(vv)) - 7, f"{vv:.0f}", petit, GRIS)
    art.rectangle([x0 + pw - 124, y0 + 6, x0 + pw - 6, y0 + 12 + 17 * len(g["largeurs"])],
                  fill=FOND)
    for k, lg in enumerate(g["largeurs"]):
        coul = COURBES[k % len(COURBES)]
        col = [c for c in mat["cases"] if abs(c["largeur_en_pas"] - lg) < 1e-12]
        xy = [(px1(i), py1(c["erreur_mediane_deg"])) for i, c in enumerate(col)
              if c["erreur_mediane_deg"] is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=coul, width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 3, b_ - 3, a_ + 3, b_ + 3], fill=coul)
            points.append((a_, b_))
        ecrire(x0 + pw - 120, y0 + 8 + k * 17, f"largeur {lg:g}", petit, coul)
    for i, val in enumerate(marges):
        ecrire(int(px1(i)) - 12, y0 + ph - 42, f"{val:g}", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 24, "marge ajoutée de chaque côté de la fenêtre, en µm · "
                                  "toutes les courbes MONTENT", petit, ALERTE)

    # ---- panneau 2 : le recensement
    x0, y0, pw, ph = 700, 122, 580, 268
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalement des appuis, contre la demi-épaisseur", moyen, ENCRE)
    demi = rc["demi_epaisseur_um"]
    mx = max(max(m["etalement_max_um"] or 0.0 for m in rc["par_matiere"]), demi) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 224
    # ⚠ L'interligne laisse la place a l'etiquette de la demi-epaisseur SOUS les barres : ecrite
    # a l'ancienne hauteur, elle tombait EN BLANC SUR LA DERNIERE BARRE, lisible mais pas voulu —
    # et `textes_qui_se_recouvrent` ne le voit pas, il compare TEXTE a TEXTE.
    for k, m in enumerate(rc["par_matiere"]):
        yy = y0 + 26 + k * 40
        for dec, val, coul in ((0, m["etalement_median_um"], GRIS),
                               (15, m["etalement_max_um"], ALERTE)):
            if val is None:
                continue
            w = (val / mx) * barre_max
            if w > 0.5:
                art.rectangle([x_barre, yy + dec, x_barre + w, yy + dec + 13], fill=coul)
                points.append((x_barre + w, yy + dec + 6))
            else:
                art.line([x_barre, yy + dec, x_barre, yy + dec + 13], fill=ENCRE, width=2)
        ecrire(x_nom, yy + 6, _court(m["nom"]), petit, ENCRE)
        ecrire(x_barre + 6, yy - 12,
               f"méd {m['etalement_median_um']:.2f}  max {m['etalement_max_um']:.2f} µm  ·  "
               f"{m['aberrants']} aberrants / {m['appuis']}", petit,
               ALERTE if m["aberrants"] else GRIS)
    xd = x_barre + (demi / mx) * barre_max
    art.line([xd, y0 + 14, xd, y0 + ph - 46], fill=ENCRE, width=2)
    ecrire(int(xd) - 96, y0 + ph - 42, f"demi-épaisseur {demi:g} µm", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 24, "gris : l'étalement médian · ambre : le maximum", petit, GRIS)

    # ---- panneau 3 : ce que le rejet repare
    x0, y0, pw, ph = 60, 446, 600, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'écart à la vraie normale, sans puis avec rejet", moyen, ENCRE)
    lignes = [x for x in j["par_bras"] if x["erreur_sans_rejet_deg"] is not None]
    ymax = max(x["erreur_sans_rejet_deg"] for x in lignes) or 1.0
    ecrire(x0 + 14, y0 + 12, f"{'matière':<18}{'bras':>8}{'sans':>9}{'avec':>9}"
                             f"{'touch.':>8}{'mieux':>7}{'pire':>6}", petit, GRIS)
    # ⚠ Dix lignes a vingt pixels touchaient la legende du bas ; l'interligne se DERIVE de la
    # place disponible plutot que d'etre pose, sinon il redevient faux au premier bras ajoute.
    pas_ligne = min(20, (ph - 96) // max(len(lignes), 1))
    for k, x in enumerate(lignes):
        yy = y0 + 36 + k * pas_ligne
        coul = BON if x["poses_touchees"] and x["mieux"] else ENCRE
        ecrire(x0 + 14, yy, f"{_court(x['nom']):<18}{x['bras']:>8}"
                            f"{x['erreur_sans_rejet_deg']:>8.2f}°{x['erreur_avec_rejet_deg']:>8.2f}°"
                            f"{x['poses_touchees']:>8}{x['mieux']:>7}{x['pire']:>6}", petit, coul)
    ecrire(x0 + 14, y0 + ph - 26,
           "vert : le rejet a touché des poses · les autres n'avaient rien à rejeter",
           petit, GRIS)

    # ---- panneau 4 : le rapport a l'echelle de `154`
    x0, y0, pw, ph = 700, 446, 580, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "de combien l'instrument se rapproche de son échelle (`154`)",
           moyen, ENCRE)
    duo = [x for x in j["par_bras"]
           if x["avec_rejet_au_dessus_de_lechelle"] is not None and x["amplitude_um"] > 0.0]
    rmax = max(max(x["sans_rejet_au_dessus_de_lechelle"],
                   x["avec_rejet_au_dessus_de_lechelle"]) for x in duo) if duo else 1.0
    x_nom, x_barre = x0 + 12, x0 + 150
    barre_max = pw - 236
    un = x_barre + barre_max / max(rmax, 1e-9)
    for k, x in enumerate(duo):
        yy = y0 + 24 + k * 31
        for dec, cle, coul in ((0, "sans_rejet_au_dessus_de_lechelle", GRIS),
                               (13, "avec_rejet_au_dessus_de_lechelle", None)):
            val = x[cle]
            w = (val / max(rmax, 1e-9)) * barre_max
            c = coul if coul is not None else (BON if val < 1.0 else ALERTE)
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 11], fill=c)
            points.append((x_barre + w, yy + dec + 5))
        ecrire(x_nom, yy + 6, f"{_court(x['nom'])[:10]} {x['bras'][:3]}", petit, ENCRE)
        ecrire(x_barre + 4, yy - 10,
               f"{x['sans_rejet_au_dessus_de_lechelle']:.2f}× → "
               f"{x['avec_rejet_au_dessus_de_lechelle']:.2f}×", petit,
               BON if x["avec_rejet_au_dessus_de_lechelle"] < 1.0 else ALERTE)
    art.line([un, y0 + 16, un, y0 + ph - 48], fill=ENCRE, width=1)
    ecrire(x0 + 14, y0 + ph - 42, "le trait vertical est UN : à gauche l'instrument bat la "
                                  "variation qu'il couvre", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 24, "gris : sans rejet · couleur : avec", petit, GRIS)

    # ---- la bande de conclusion, sur son propre cadre RESERVE
    by = 724
    art.rectangle([0, by, L, H], fill=BANDE)
    cadres.append((0, by, L, H))
    ecrire(28, by + 18, "Un appui qui a sauté d'interstice se rejette, et l'énoncé n'a aucun seuil",
           moyen, ENCRE)
    ecrire(28, by + 46,
           f"Élargir la fenêtre fait poser plus souvent et PLUS FAUX, à chacune des "
           f"{len(g['largeurs'])} largeurs : les deux contraintes ne se compensent pas, elles "
           f"s'additionnent, et la meilleure case de la grille est sans marge.", petit, ENCRE)
    ecrire(28, by + 68,
           f"Les appuis aberrants sont rares et n'existent que là où la matière porte les deux "
           f"causes. Les rejeter fait passer la croix de {dur['erreur_sans_rejet_deg']}° à "
           f"{dur['erreur_avec_rejet_deg']}° sur la matière du rouleau, en touchant "
           f"{dur['poses_touchees']} poses.", petit, ENCRE)
    ecrire(28, by + 90,
           f"Rapporté à l'échelle que `154` mesure, cela fait "
           f"{dur['sans_rejet_au_dessus_de_lechelle']}× → "
           f"{dur['avec_rejet_au_dessus_de_lechelle']}× : l'instrument se rapproche de sa matière "
           f"sans changer ni de taille ni de dimension.", petit, BON)
    ecrire(28, by + 112,
           "Les interstices sont espacés d'une épaisseur, donc « à plus d'une demi-épaisseur de la "
           "médiane » et « sur un autre interstice » sont le même énoncé.", petit, ENCRE)

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

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["sur_la_matiere_du_rouleau"]["avec_rejet_au_dessus_de_lechelle"] = 5.55
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer le rapport à l'échelle change ce que la bande DIT",
      any("5.55" in t for _x, _y, t, _f in p2)
      and not any("5.55" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["sur_la_matiere_du_rouleau"]["poses_touchees"] = 777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer le compte des poses touchées aussi",
      any("777" in t for _x, _y, t, _f in p3))

    sans = copy.deepcopy(d)
    del sans["juger"]["sur_la_matiere_du_rouleau"]
    tmp = sortie.parent / "_sans_rouleau_155.json"
    tmp.write_text(json.dumps(sans, ensure_ascii=False))
    try:
        lire(tmp)
        ok = False
    except ValueError:
        ok = True
    finally:
        tmp.unlink(missing_ok=True)
    v("⚠ une mesure sans la case décisive est REFUSÉE, jamais dessinée à moitié", ok)

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures" / "rejeter_un_appui_qui_a_saute.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images" / "155_rejeter_un_appui_qui_a_saute.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
