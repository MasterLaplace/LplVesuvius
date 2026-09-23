"""Le consensus traverse-t-il la hauteur : la traversée, les colonnes seules, l'extrapolation, la couverture.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LA TRAVERSÉE OBSERVÉE DE LA HAUTEUR, et c'est le
panneau qui conclut : sur le même tronçon et depuis le même départ, le consensus des colonnes voisines
reste dans le feuillet quand une colonne seule en sort. En bas à gauche, LES COLONNES SEULES sur leur
plus long tronçon. En bas au milieu, L'EXTRAPOLATION et son étalon. En bas à droite, LA COUVERTURE : où
le consensus existe, et où il n'y a pas de majorité pour voter. C'est la figure de `221`, transposée.

  uv run python src/figures/figure_le_consensus_traverse_t_il_la_hauteur.py \\
      --json docs/mesures/le_consensus_traverse_t_il_la_hauteur.json \\
      --sortie docs/images/223_le_consensus_traverse_t_il_la_hauteur.png
"""
from __future__ import annotations

import argparse
import json
import re
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
CONTRE = (92, 108, 150)


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `le_consensus_traverse_t_il_la_hauteur.py`.

    ⚠⚠⚠ SANS LES MARCHES PUBLIÉES, la figure tracerait un résumé ; sans l'étalon, une extrapolation
    se lirait comme une mesure.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    if not d.get("letalon_de_lextrapolation"):
        raise SystemExit("l'étalon de l'extrapolation manque")
    for cle in ("les_marches_du_troncon_retenu_en_voxels", "la_traversee_du_consensus",
                "lextrapolation_du_consensus", "les_colonnes_seules_sur_leur_plus_long_troncon",
                "les_troncons_par_colonne", "le_verdict"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v["la_traversee_observee_reste_sous_le_demi_pli"]:
        return "LE CONSENSUS DES COLONNES QUITTE LE FEUILLET, MÊME SUR CE QU'IL LIT"
    if not v["lextrapolation_tient"]:
        return "LE CONSENSUS DES COLONNES TRAVERSE CE QU'IL LIT, PAS LA HAUTEUR ENTIÈRE"
    return "LE CONSENSUS DES COLONNES VOISINES TRAVERSE LA HAUTEUR SANS QUITTER LE FEUILLET"


def dessiner(d: dict, sortie: Path):
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ve, ob, ex = d["le_verdict"], d["la_traversee_du_consensus"], d["lextrapolation_du_consensus"]
    et, ma, tr = d["letalon_de_lextrapolation"], d["les_marches_du_troncon_retenu_en_voxels"], \
        d["le_troncon_retenu"]
    demi = float(d["le_demi_pli_en_voxels"])

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"médiane des colonnes présentes, au moins {d['le_minimum_de_colonnes']} sur "
           f"{len(d['les_colonnes'])} · {d['les_coutures_avec_consensus']} coutures verticales sur "
           f"{d['les_coutures_dune_colonne']} ont un consensus · une lecture neuve, retombée sur 222 "
           f"en {d['la_reproduction']['combien_de_coutures_relues']} coutures", petit, GRIS)

    # ── PANNEAU 1 · LA TRAVERSEE OBSERVEE ───────────────────────────────────────────────────
    panneau(50, 88, 1310, 420, f"LA TRAVERSÉE OBSERVÉE DE LA HAUTEUR · coutures {tr[0]} à {tr[1]}, "
                               f"{tr[2]} coutures verticales, même départ pour tous")
    gx0, gx1, gy0, gy1 = 120, 1150, 130, 390
    borne = max(demi * 1.25, max(abs(x) for s in ma.values() for x in s) * 1.1)

    def py(v):
        return gy0 + (gy1 - gy0) * (borne - float(v)) / (2.0 * borne)

    for yv, lab in ((demi, f"+{int(demi)} vx"), (0.0, "départ"), (-demi, f"-{int(demi)} vx")):
        art.line([gx0, py(yv), gx1, py(yv)], fill=(ALERTE if yv else TRAIT), width=1)
        ecrire(gx0 - 64, py(yv) - 7, lab, 0, ALERTE if yv else GRIS)
    styles = [("le_consensus", BON, 3, "consensus des colonnes"), ("la_moyenne", CONTRE, 1,
                                                                   "moyenne (contrôle)")]
    styles += [(k, ALERTE, 1, f"colonne {k.split('_')[-1]} seule") for k in sorted(ma)
               if k.startswith("la_colonne_")]
    for i, (k, coul, w, lab) in enumerate(styles):
        s = ma[k]
        pts = [(gx0 + (gx1 - gx0) * j / (len(s) - 1), py(v)) for j, v in enumerate(s)]
        art.line(pts, fill=coul, width=w)
        traces[k] = len(s)
        points.extend(pts)
        ecrire(1165, 150 + 22 * i, lab, 0, coul)
    ecrire(1165, 150 + 22 * len(styles) + 10, "demi-feuillet", 0, ALERTE)
    ecrire(1165, 150 + 22 * len(styles) + 28, f"± {int(demi)} vx", 0, ALERTE)
    ecrire(1165, 340, f"consensus : {_fr(ob['la_distance_au_depart_en_voxels'], 2)} vx", 0, BON)
    for j, (k, x) in enumerate(sorted(d["les_colonnes_seules_sur_le_meme_troncon"].items())):
        ecrire(1165, 358 + 18 * j, f"colonne {k} : {_fr(x['la_distance_au_depart_en_voxels'], 2)} vx",
               0, ALERTE)

    # ── PANNEAU 2 · LES RANGEES SEULES ──────────────────────────────────────────────────────
    panneau(50, 444, 480, 772, "LA HAUTEUR ENTIÈRE · marche médiane par blocs")
    se = d["les_colonnes_seules_sur_leur_plus_long_troncon"]
    vals = [x["la_marche_mediane_par_blocs_en_voxels"] for x in se.values()]
    ech = max(max(vals), ex["la_marche_mediane_par_blocs_en_voxels"], demi) * 1.15
    bx, bw = 170, 200
    yy = 484
    for k, x in sorted(se.items()):
        ecrire(66, yy, f"colonne {k} seule", 0, ENCRE)
        barre(bx, yy, bw, x["la_marche_mediane_par_blocs_en_voxels"] / ech, 10, ALERTE)
        ecrire(bx + bw + 8, yy - 1, f"{_fr(x['la_marche_mediane_par_blocs_en_voxels'], 2)} vx", 0, GRIS)
        yy += 26
    ecrire(66, yy, "consensus", 0, ENCRE)
    barre(bx, yy, bw, ex["la_marche_mediane_par_blocs_en_voxels"] / ech, 10, BON)
    ecrire(bx + bw + 8, yy - 1, f"{_fr(ex['la_marche_mediane_par_blocs_en_voxels'], 2)} vx", 0, BON)
    xl = bx + bw * demi / ech
    art.line([xl, 476, xl, yy + 16], fill=ALERTE, width=2)
    ecrire(xl - 40, yy + 20, f"demi-feuillet {int(demi)}", 0, ALERTE)
    ecrire(66, 716, f"{d['les_coutures_dune_colonne']} coutures, pas centrés, blocs de "
                    f"{ex['la_longueur_de_bloc']}", 0, GRIS)
    tiennent = sum(1 for x in se.values() if x["la_marche_mediane_par_blocs_en_voxels"] < demi)
    ecrire(66, 734, ("aucune colonne seule ne tiendrait la hauteur" if not tiennent else
                     f"{tiennent} colonne(s) seule(s) tiendrai(en)t la hauteur"), 0, ENCRE)

    # ── PANNEAU 3 · L'EXTRAPOLATION ET SON ETALON ───────────────────────────────────────────
    panneau(500, 444, 900, 772, "L'EXTRAPOLATION · et son étalon")
    ecrire(516, 484, f"par blocs : {_fr(ex['la_marche_mediane_par_blocs_en_voxels'], 2)} vx, "
                     f"{ex['les_marches_sous_le_demi_pli_par_blocs']}/{ex['tirages']} sous", 0, BON)
    ecrire(516, 502, f"pas à pas : {_fr(ex['la_marche_mediane_pas_a_pas_en_voxels'], 2)} vx, "
                     f"{ex['les_marches_sous_le_demi_pli_pas_a_pas']}/{ex['tirages']} sous", 0, GRIS)
    ecrire(516, 540, f"autocorrélation au premier décalage : {_fr(d['lautocorrelation_au_premier_decalage'], 4)}",
           0, ENCRE)
    ecrire(516, 558, f"donc θ = {_fr(et['le_theta'], 4)}", 0, ENCRE)
    ecrire(516, 594, f"sur {et['les_replicats']} tronçons de {et['les_coutures_du_troncon']} coutures,",
           0, GRIS)
    ecrire(516, 612, f"contre la vérité connue de {et['les_verites']} hauteurs :", 0, GRIS)
    ecrire(516, 636, f"par blocs, rapport {_fr(et['le_rapport_median_par_blocs'], 4)}", 0, BON)
    ecrire(516, 654, f"pas à pas, rapport {_fr(et['le_rapport_median_pas_a_pas'], 4)}", 0, GRIS)
    ecrire(516, 690, f"l'instrument retenu s'écarte de la vérité de "
                     f"{_fr(ve['lecart_des_blocs_a_la_verite'], 4)}", 0, ENCRE)
    ecrire(516, 708, "⚠ l'extrapolation se juge sur les blocs,", 0, ALERTE)
    ecrire(516, 726, "qui gardent la dépendance courte", 0, ALERTE)

    # ── PANNEAU 4 · LA COUVERTURE ───────────────────────────────────────────────────────────
    panneau(920, 444, 1310, 772, "LA COUVERTURE · où il y a une majorité")
    cx0, cx1 = 1016, 1290
    n = int(d["les_coutures_dune_colonne"])

    def pxc(c):
        return cx0 + (cx1 - cx0) * float(c) / n

    yy = 488
    for r, tr_ in sorted(d["les_troncons_par_colonne"].items()):
        ecrire(936, yy - 2, f"colonne {r}", 0, GRIS)
        art.line([cx0, yy + 5, cx1, yy + 5], fill=TRAIT, width=1)
        for a_, b_, _n in tr_:
            art.rectangle([pxc(a_), yy + 1, pxc(b_ + 1), yy + 9], fill=CONTRE)
            points.append((pxc(b_ + 1), yy + 9))
        yy += 24
    ecrire(936, yy - 2, "consensus", 0, ENCRE)
    art.line([cx0, yy + 5, cx1, yy + 5], fill=TRAIT, width=1)
    for a_, b_, _n in d["les_troncons_du_consensus"]:
        art.rectangle([pxc(a_), yy + 1, pxc(b_ + 1), yy + 9], fill=BON)
    yy += 36
    ecrire(936, yy, f"tronçons du consensus : " + ", ".join(f"{a_}–{b_}" for a_, b_, _n in
                                                        d["les_troncons_du_consensus"]), 0, ENCRE)
    ecrire(936, yy + 18, f"{d['les_coutures_avec_consensus']} coutures sur {n}", 0, GRIS)
    ecrire(936, 716, "le consensus franchit les trous d'une", 0, ENCRE)
    ecrire(936, 734, "colonne tant que la majorité est là", 0, ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 790, L, H], fill=BANDE)
    ecrire(50, 812, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", moyen, ENCRE)
    ecrire(50, 842,
           "★ ce qui remplace l'humain d'une rangée de chunks à la suivante est aussi un consensus : "
           "celui des colonnes voisines, à chaque couture verticale.", moyen, ENCRE)
    ecrire(50, 876,
           "⚠ ce qui n'est PAS établi : que la part PARTAGÉE du pas soit la matière et non une erreur "
           "commune — aucun consensus ne la retire.", moyen, ALERTE)
    milieu = len(d["les_troncons_du_consensus"]) - 1
    ecrire(50, 900,
           ("⚠ ni que la hauteur soit franchie de bout en bout : aux bords seulement, il n'y a pas de "
            "majorité pour voter." if not milieu else
            f"⚠ ni que la hauteur soit franchie de bout en bout : aux bords, et à {milieu} endroit(s) au "
            f"milieu, il n'y a pas de majorité pour voter."), moyen, ALERTE)
    ecrire(50, 934,
           "★ la suite : une surface entière — deux chemins de consensus vers le même chunk "
           "arrivent-ils sur la même spire ?", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, barres, points, traces


def verifier(json_path: Path, sortie: Path) -> int:
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

    d = lire(json_path)
    tmp = sortie.parent / ".sonde_223.png"
    _, poses, cadres, barres, points, traces = dessiner(d, tmp)

    def _v(a, b):
        return {"le_verdict": {"la_traversee_observee_reste_sous_le_demi_pli": a,
                               "lextrapolation_tient": b}}

    v("★★★★ les trois titres possibles sont distincts, et sortir sur ce qu'on lit prime",
      len({le_titre(_v(a, b)) for a in (True, False) for b in (True, False)}) == 3
      and le_titre(_v(False, True)) == le_titre(_v(False, False)))
    v("★★★ le titre LIT le verdict",
      ("SANS QUITTER" in le_titre(d)) == (d["le_verdict"]["la_traversee_observee_reste_sous_le_demi_pli"]
                                          and d["le_verdict"]["lextrapolation_tient"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, 1360),
      str(textes_debordants(poses, 1360))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★★ aucune barre ne déborde de sa piste", all(b <= p + 1e-6 for b, p in barres),
      str([x for x in barres if x[0] > x[1] + 1e-6])[:160])
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= 1360 and 0 <= y <= 980 for x, y in points))
    ma = d["les_marches_du_troncon_retenu_en_voxels"]
    v("★★★★ chaque marche publiée est tracée ENTIÈRE, pas un résumé",
      set(traces) == set(ma) and all(traces[k] == len(ma[k]) == d["le_troncon_retenu"][2] + 1
                                     for k in ma))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte la distance au départ du consensus ET celle de la rangée seule appariée",
      f"{_fr(d['la_traversee_du_consensus']['la_distance_au_depart_en_voxels'], 2)} vx" in txt
      and all(f"{_fr(x['la_distance_au_depart_en_voxels'], 2)} vx" in txt
              for x in d["les_colonnes_seules_sur_le_meme_troncon"].values()))
    v("★★★★ elle porte la marche médiane de chaque rangée seule et celle du consensus",
      all(f"{_fr(x['la_marche_mediane_par_blocs_en_voxels'], 2)} vx" in txt
          for x in d["les_colonnes_seules_sur_leur_plus_long_troncon"].values())
      and f"{_fr(d['lextrapolation_du_consensus']['la_marche_mediane_par_blocs_en_voxels'], 2)} vx" in txt)
    et = d["letalon_de_lextrapolation"]
    v("★★★★ elle porte l'étalon : le θ dérivé et les deux rapports à la vérité",
      _fr(et["le_theta"], 4) in txt and _fr(et["le_rapport_median_par_blocs"], 4) in txt
      and _fr(et["le_rapport_median_pas_a_pas"], 4) in txt)
    v("★★★★ elle porte les tronçons du consensus",
      all(f"{a}–{b}" in txt for a, b, _n in d["les_troncons_du_consensus"]))
    v("★★★★ elle dit ce qui n'est PAS établi — la part partagée, et les coutures sans majorité",
      "n'est PAS établi" in txt and "PARTAGÉE" in txt and "majorité" in txt)
    v("★★★ elle dit que la lecture est neuve et retombe sur `222`",
      f"une lecture neuve, retombée sur 222 en {d['la_reproduction']['combien_de_coutures_relues']} "
      f"coutures" in txt)
    v("★★★★ aucun nombre dessiné ne porte de point décimal",
      not re.search(r"\d\.\d", txt), str(re.findall(r"\S*\d\.\d\S*", txt))[:160])

    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e in echecs:
        print(f"  ÉCHEC {e}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "le_consensus_traverse_t_il_la_hauteur.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "223_le_consensus_traverse_t_il_la_hauteur.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
