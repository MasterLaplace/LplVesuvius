"""Ce que la seconde mâchoire achète encore, une fois qu'un appui peut être rejeté.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le piège du total : la mâchoire
seule mène et perd des départs que la pince tenait. En haut à droite, ce qui les sépare vraiment —
la QUEUE de la dérive, p90 et maximum côte à côte, parce qu'ils ne disent pas la même chose. En bas
à gauche, la contrainte : elle refuse deux fois plus et n'achète plus rien. En bas à droite, la
matière du rouleau, où zéro réussite reste zéro pendant que le mur recule d'un facteur cinq.

  uv run python src/figures/figure_ce_que_la_seconde_machoire_achete_encore.py \\
      --json docs/mesures/ce_que_la_seconde_machoire_achete_encore.json \\
      --sortie docs/images/157_ce_que_la_seconde_machoire_achete_encore.png
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
TEMOIN = (150, 152, 156)


def lire(chemin: Path) -> dict:
    """Le JSON de `ce_que_la_seconde_machoire_achete_encore.py`.

    ⚠⚠ Refuse une mesure dont le verdict ne porte pas les quatre instruments : les quatre panneaux
    se lisent les uns contre les autres, et une figure dessinée sur un verdict partiel ressemble
    exactement à une figure dessinée sur un verdict entier.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if len(j.get("le_verdict", [])) < 2:
        raise ValueError(f"{chemin} : le verdict ne porte pas assez d'instruments")
    if not j.get("sur_la_matiere_du_rouleau"):
        raise ValueError(f"{chemin} : la matière du rouleau est absente du jugement")
    return d


def _bref(nom: str) -> str:
    return (nom.replace("la pince de ", "").replace("la croix et le rejet", "croix+rejet")
            .replace("la croix ", "croix ").replace("le rejet ", "rejet "))


def _bras(nom: str) -> str:
    return {"une machoire": "seule", "deux machoires libres": "libre",
            "la pince": "pince"}.get(nom, nom)


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 940
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    j = d["juger"]
    ver = j["le_verdict"]
    temoin = ver[0]

    ecrire(28, 20, "Ce que la seconde mâchoire achète encore, une fois qu'un appui peut être "
                   "rejeté", gros, ENCRE)
    ecrire(28, 46, f"la grille de `156` RELUE — {d['cases']} cases, {d['departs']} départs par "
                   f"case, fenêtre {d['fenetre']} — les trois bras partent du MÊME point, ce qui "
                   f"est ce qui rend l'appariement exact", petit, GRIS)

    # ---- panneau 1 : le total contre l'appariement
    x0, y0, pw, ph = 56, 122, 620, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le total mène, l'appariement dit ce qu'il a coûté", moyen, ENCRE)
    gmax = max(max(x["seule_gagne"], x["seule_perd"]) for x in ver) or 1
    x_zero = x0 + 262
    demi = 128
    art.line([x_zero, y0 + 20, x_zero, y0 + ph - 60], fill=TRAIT, width=1)
    for k, x in enumerate(ver):
        yy = y0 + 30 + k * 58
        wg = (x["seule_gagne"] / gmax) * demi
        wp = (x["seule_perd"] / gmax) * demi
        art.rectangle([x_zero, yy, x_zero + max(wg, 1), yy + 14], fill=BON)
        points.append((x_zero + wg, yy + 7))
        art.rectangle([x_zero - max(wp, 1), yy, x_zero, yy + 14], fill=ALERTE)
        points.append((x_zero - wp, yy + 7))
        ecrire(x0 + 12, yy + 2, f"{_bref(x['nom']):<17}", petit, ENCRE)
        ecrire(x0 + 12, yy + 20,
               f"seule {x['reussites_seule']}  contre pince {x['reussites_pince']}", petit, GRIS)
        ecrire(x_zero + demi + 14, yy + 2,
               f"{x['seule_gagne']:+d} gagnées / {-x['seule_perd']:+d} perdues", petit,
               BON if x["seule_gagne_jointement"] else ALERTE)
    ecrire(x0 + 12, y0 + ph - 50,
           "vert : la mâchoire SEULE gagne le départ · ambre : elle le PERD", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 34,
           "sous AUCUN des quatre instruments elle ne gagne jointement : elle ÉCHANGE",
           petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 18,
           f"et elle lit la MOITIÉ : {ver[2]['lectures_seule']} contre "
           f"{ver[2]['lectures_pince']} sous le rejet", petit, GRIS)

    # ---- panneau 2 : la queue
    x0, y0, pw, ph = 712, 122, 592, 296
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la QUEUE de la dérive, en feuilles — p90 et maximum", moyen, ENCRE)
    # ⚠ L'echelle est prise sur le p90 : le maximum de la machoire seule sous `144` (36,685) ecrase
    # tout le panneau, donc il est ECRIT plutot que dessine.
    pmax = max(max(x["p90_seule"], x["p90_pince"]) for x in ver) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 300
    for k, x in enumerate(ver):
        yy = y0 + 28 + k * 58
        ecrire(x_nom, yy + 12, _bref(x["nom"]), petit, ENCRE)
        for dec, val, coul, nom in ((0, x["p90_seule"], ALERTE, "seule"),
                                    (17, x["p90_pince"], BON, "pince")):
            w = (val / pmax) * barre_max
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 14], fill=coul)
            points.append((x_barre + w, yy + dec + 7))
            ecrire(x_barre + barre_max + 10, yy + dec + 1,
                   f"{nom} p90 {val:.3f}  max {x['derive_max_seule' if nom == 'seule' else 'derive_max_pince']:.1f}",
                   petit, coul)
    ecrire(x0 + 12, y0 + ph - 50,
           "la barre est le p90 · le maximum est ÉCRIT, parce qu'il écrase le panneau", petit,
           GRIS)
    ecrire(x0 + 12, y0 + ph - 34,
           f"la pince tient une queue plus courte sous les QUATRE instruments — "
           f"{temoin['p90_seule']:.3f} contre {temoin['p90_pince']:.3f} sous `144`,", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 18,
           f"{ver[2]['p90_seule']:.3f} contre {ver[2]['p90_pince']:.3f} sous le rejet : "
           f"l'écart se resserre sans se fermer", petit, ENCRE)

    # ---- panneau 3 : la contrainte
    x0, y0, pw, ph = 56, 474, 620, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la CONTRAINTE : une paire LIBRE contre la pince", moyen, ENCRE)
    rmax = max(x["refus_de_la_pince"] for x in ver) or 1
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 320
    for k, x in enumerate(ver):
        yy = y0 + 28 + k * 50
        w = (x["refus_de_la_pince"] / rmax) * barre_max
        coul = BON if x["la_contrainte_achete_quelque_chose"] else ALERTE
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_nom, yy + 2, _bref(x["nom"]), petit, ENCRE)
        ecrire(x_barre + barre_max + 10, yy + 2,
               f"{x['refus_de_la_pince']:>3d} refus  →  {x['libre_gagne']}/{x['libre_perd']}",
               petit, coul)
    ecrire(x0 + 12, y0 + ph - 48,
           "la barre : combien de fois la contrainte a REFUSÉ un pas", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 32,
           "à droite : ce que la paire libre gagne/perd contre la pince — donc ce que le refus "
           "ACHÈTE", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 16,
           f"elle refuse DEUX FOIS plus sous le rejet ({ver[2]['refus_de_la_pince']} contre "
           f"{temoin['refus_de_la_pince']}) et n'achète plus rien", petit, ALERTE)

    # ---- panneau 4 : la matiere du rouleau
    x0, y0, pw, ph = 712, 474, 592, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la matière du rouleau : jusqu'où on va, faute de réussir", moyen, ENCRE)
    dur = j["sur_la_matiere_du_rouleau"]
    parts = [{b["bras"]: b["part_du_tour_mediane"] for b in x["par_bras"] if b.get("decidable")}
             for x in dur]
    vmax = max(v for p in parts for v in p.values()) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 300
    for k, (x, p) in enumerate(zip(dur, parts)):
        yy = y0 + 28 + k * 50
        ecrire(x_nom, yy + 8, _bref(x["nom"]), petit, ENCRE)
        for i, b in enumerate(("une machoire", "la pince")):
            val = p.get(b, 0.0)
            w = (val / vmax) * barre_max
            coul = ALERTE if b == "une machoire" else BON
            art.rectangle([x_barre, yy + i * 15, x_barre + max(w, 1), yy + i * 15 + 12],
                          fill=coul)
            points.append((x_barre + w, yy + i * 15 + 6))
        ecrire(x_barre + barre_max + 10, yy + 8,
               f"seule {p.get('une machoire', 0.0):.4f}  pince {p.get('la pince', 0.0):.4f}",
               petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 48,
           "part du tour MÉDIANE parcourue · zéro réussite sous les quatre instruments", petit,
           GRIS)
    ecrire(x0 + 12, y0 + ph - 32,
           f"le rejet multiplie par CINQ ce que la pince parcourt "
           f"({parts[0].get('la pince', 0.0):.4f} → {parts[2].get('la pince', 0.0):.4f})",
           petit, BON)
    ecrire(x0 + 12, y0 + ph - 16,
           "et la croix y est PIRE que le rejet seul, sur les deux bras", petit, ALERTE)

    # ---- bande de conclusion
    y = 782
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    r_ = ver[2]
    ecrire(74, y + 12,
           f"✗  une mâchoire SEULE ne bat la pince JOINTEMENT sous aucun des quatre instruments : "
           f"{r_['reussites_seule']} contre {r_['reussites_pince']} sous le rejet, mais "
           f"{r_['seule_gagne']} gagnées pour {r_['seule_perd']} PERDUES.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★  Le rejet RÉDUIT ce que la seconde mâchoire achète sans le supprimer : la queue "
           f"au p90 passe de {temoin['p90_seule']:.3f} contre {temoin['p90_pince']:.3f} sous `144`",
           moyen, BON)
    ecrire(74, y + 60,
           # ⚠ Le rapport est LU du verdict, jamais recalculé ici : deux calculs d'un même
           # rapport finissent par ne pas s'accorder.
           f"        à {r_['p90_seule']:.3f} contre {r_['p90_pince']:.3f} — un facteur "
           f"{temoin['la_seconde_machoire_divise_la_queue_par']:g} ramené à "
           f"{r_['la_seconde_machoire_divise_la_queue_par']:g}.", moyen, BON)
    ecrire(74, y + 86,
           f"★★  La CONTRAINTE, elle, est REMPLACÉE : 0 gagnée et 0 perdue contre une paire libre, "
           f"pour {r_['refus_de_la_pince']} refus contre {temoin['refus_de_la_pince']}.",
           moyen, ENCRE)
    ecrire(74, y + 108,
           "⚠  Et le rapport des MAXIMA ne décide de rien : il dit la pince, le p90 dit la "
           "mâchoire seule. Un maximum est une seule marche.", moyen, ALERTE)

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
    v("l'image est écrite et a la taille attendue", img.size == (1360, 940), f"{img.size}")
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
    # ⚠ La valeur d'épreuve est DISCRIMINANTE : « 77 » apparaît déjà dans « 0.0776 », la part du
    # tour d'une mâchoire seule sur la matière du rouleau, donc la sonde passait des deux côtés.
    # C'est le défaut que `verifier_chiffres` nomme pour les chiffres courts, ici dans une figure.
    faux["juger"]["le_verdict"][2]["seule_perd"] = 7777
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ changer le nombre de départs PERDUS change ce que la bande DIT",
      any("7777 PERDUES" in t for _x, _y, t, _f in p2)
      and not any("7777" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["le_verdict"][2]["refus_de_la_pince"] = 555
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐ ... et changer le compte des refus aussi",
      any("555" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    for b in faux3["juger"]["sur_la_matiere_du_rouleau"][2]["par_bras"]:
        b["part_du_tour_mediane"] = 0.9999
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et la part du tour sur la matière du rouleau est LUE, pas supposée",
      any("0.9999" in t for _x, _y, t, _f in p4))

    sans = copy.deepcopy(d)
    del sans["juger"]["sur_la_matiere_du_rouleau"]
    tmp = sortie.parent / "_sans_rouleau_157.json"
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
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "ce_que_la_seconde_machoire_achete_encore.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "157_ce_que_la_seconde_machoire_achete_encore.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
