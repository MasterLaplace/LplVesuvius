"""Les boucles se ferment-elles : la boucle, le nuage, le nul, les variances, les trois surfaces.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LA BOUCLE : quatre chunks, deux pas
horizontaux, deux verticaux, et ce que leur somme doit valoir. En haut à droite, LE NUAGE, et c'est le
panneau qui conclut : chaque boucle complète est un point `(A, B)` ; des boucles qui se ferment
s'alignent sur la diagonale `B = -A`, des pas sans rapport font un nuage rond. En bas à gauche, LE NUL :
le rapport de fermeture observé parmi ceux de la moitié verticale décalée. Au milieu, LES VARIANCES
contre leur plancher de lecture. À droite, LES TROIS SURFACES sur le plus long tronçon.

  uv run python src/figures/figure_les_boucles_se_ferment_elles.py \\
      --json docs/mesures/les_boucles_se_ferment_elles.json \\
      --sortie docs/images/222_les_boucles_se_ferment_elles.png
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
LEGER = (196, 204, 222)


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `les_boucles_se_ferment_elles.py`.

    ⚠⚠⚠ SANS LES BOUCLES PUBLIÉES, le nuage serait un résumé ; sans le nul entier, un rapport se
    lirait sans ce à quoi il se compare.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("les_boucles", "lepreuve", "le_plancher", "letalon", "les_trois_surfaces",
                "les_boucles_qui_sautent", "le_verdict", "la_lecture", "la_reproduction",
                "le_detail_aux_colonnes_fortes"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    if not d["lepreuve"].get("les_rapports_du_nul"):
        raise SystemExit("le nul n'est pas publié")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer — et la part expliquée, qui dit combien.

    ⚠⚠ La première version disait « le pas vertical rend compte du désaccord », sans dire de quelle
    part : sur la mesure, c'est une petite part de l'excès, et un titre qui ne la chiffre pas la
    gonfle.
    """
    issue = d["le_verdict"].get("lissue")
    if issue == "les_boucles_se_ferment":
        part = (d.get("le_plancher") or {}).get("la_part_expliquee_de_lexces")
        if part is None:
            return "LES BOUCLES SE FERMENT MIEUX QUE LE HASARD"
        return (f"LES BOUCLES SE FERMENT MIEUX QUE LE HASARD, MAIS LE PAS VERTICAL N'EXPLIQUE QUE "
                f"{round(100 * float(part))} % DE L'EXCÈS DU DÉSACCORD")
    if issue == "elles_ne_se_ferment_pas":
        return "LES BOUCLES NE SE FERMENT PAS MIEUX QUE LE HASARD"
    return "L'ÉTALON NE TIENT PAS : AUCUN VERDICT"


def la_rangee_montree(d: dict) -> str:
    """La rangée de boucles dont le tronçon est le plus long — la première à égalité."""
    ts = {r: x for r, x in d["les_trois_surfaces"].items() if x.get("decidable")}
    return max(sorted(ts), key=lambda r: ts[r]["combien_de_boucles"])


def dessiner(d: dict, sortie: Path):
    L, H = 1360, 1000
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

    ep, pl, et, lec = d["lepreuve"], d["le_plancher"], d["letalon"], d["la_lecture"]
    demi = float(d["les_boucles_qui_sautent"]["le_demi_feuillet"])

    ecrire(50, 28, le_titre(d), gros, ENCRE)
    ecrire(50, 56,
           f"les cinq rangées de 219 relues dans les deux sens · {lec['combien_de_pas_verticaux']} pas "
           f"verticaux · {ep['combien_de_boucles']} boucles complètes · pas horizontaux retombés sur "
           f"ceux de 219", petit, GRIS)

    # ── PANNEAU 1 · LA BOUCLE ───────────────────────────────────────────────────────────────
    panneau(50, 88, 420, 440, "LA BOUCLE · quatre chunks")
    x0, y0, c = 110, 150, 120
    noms = {(0, 0): "(r, c)", (0, 1): "(r, c+1)", (1, 0): "(r+1, c)", (1, 1): "(r+1, c+1)"}
    for (i, j), nom in noms.items():
        art.rectangle([x0 + j * c + 6, y0 + i * c + 6, x0 + (j + 1) * c - 6, y0 + (i + 1) * c - 6],
                      outline=GRIS, width=1)
        ecrire(x0 + j * c + 30, y0 + i * c + 50, nom, 0, GRIS)

    def fleche(a, b, coul):
        art.line([a, b], fill=coul, width=3)
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = max(1.0, (dx * dx + dy * dy) ** 0.5)
        ux, uy = dx / n, dy / n
        art.polygon([b, (b[0] - 10 * ux + 5 * uy, b[1] - 10 * uy - 5 * ux),
                     (b[0] - 10 * ux - 5 * uy, b[1] - 10 * uy + 5 * ux)], fill=coul)
    mx, my = x0 + c, y0 + c
    fleche((x0 + c // 2, y0 + 20), (x0 + c + c // 2, y0 + 20), CONTRE)
    fleche((x0 + c + c // 2 + 40, y0 + c // 2), (x0 + c + c // 2 + 40, y0 + c + c // 2), BON)
    fleche((x0 + c + c // 2, y0 + 2 * c - 20), (x0 + c // 2, y0 + 2 * c - 20), CONTRE)
    fleche((x0 - 20, y0 + c + c // 2), (x0 - 20, y0 + c // 2), BON)
    art.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=ENCRE)
    ecrire(x0 + c - 22, y0 + 26, "h(r)", 0, CONTRE)
    ecrire(x0 + 2 * c + 26, y0 + c - 34, "v(c+1)", 0, BON)
    ecrire(x0 + c - 30, y0 + 2 * c - 42, "h(r+1)", 0, CONTRE)
    ecrire(x0 - 56, y0 + c - 34, "v(c)", 0, BON)
    ecrire(66, 404, "L = h(r) + v(c+1) - h(r+1) - v(c) = A + B", 0, ENCRE)
    ecrire(66, 420, "une surface cohérente : L = 0 au bruit près", 0, BON)

    # ── PANNEAU 2 · LE NUAGE ────────────────────────────────────────────────────────────────
    panneau(440, 88, 1310, 440, f"LE NUAGE · chaque boucle complète, désaccord A contre variation "
                                f"verticale B")
    bo = [(a, b) for s in d["les_boucles"].values() for a, b in s.values()]
    gx0, gx1, gy0, gy1 = 530, 850, 132, 408
    borne = max(1.0, max(max(abs(a), abs(b)) for a, b in bo) * 1.05)

    def px(a):
        return gx0 + (gx1 - gx0) * (float(a) + borne) / (2.0 * borne)

    def py(b):
        return gy0 + (gy1 - gy0) * (borne - float(b)) / (2.0 * borne)

    art.line([px(0), gy0, px(0), gy1], fill=TRAIT, width=1)
    art.line([gx0, py(0), gx1, py(0)], fill=TRAIT, width=1)
    art.line([px(-borne), py(borne), px(borne), py(-borne)], fill=BON, width=2)
    art.rectangle([gx0, gy0, gx1, gy1], outline=TRAIT)
    for a, b in bo:
        x, y = px(a), py(b)
        art.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=CONTRE)
        points.append((x, y))
    traces["les_boucles"] = len(bo)
    ecrire(gx1 - 110, gy1 + 4, f"A de -{_fr(borne, 0)} à +{_fr(borne, 0)} vx", 0, GRIS)
    ecrire(gx0 - 64, gy0, "B (vx)", 0, GRIS)
    ecrire(gx0 + 6, gy1 - 18, "diagonale B = -A : boucles fermées", 0, BON)
    tx = 890
    ecrire(tx, 136, f"{ep['combien_de_boucles']} boucles", 0, ENCRE)
    ecrire(tx, 160, f"rapport de fermeture ρ = {_fr(ep['le_rapport_de_fermeture'], 4)}", 0, ENCRE)
    ecrire(tx, 178, "un : aucun rapport · zéro : fermées", 0, GRIS)
    ecrire(tx, 208, f"var A = {_fr(pl['la_variance_de_A'], 4)} vx²", 0, ENCRE)
    ecrire(tx, 226, f"var B = {_fr(pl['la_variance_de_B'], 4)} vx²", 0, ENCRE)
    ecrire(tx, 244, f"var L = {_fr(pl['la_variance_de_L'], 4)} vx²", 0, ENCRE)
    ecrire(tx, 262, f"part géométrique -cov(A, B) = {_fr(pl['la_part_geometrique'], 4)} vx²", 0, BON)
    q = d["les_boucles_qui_sautent"]
    ecrire(tx, 298, f"boucles qui sautent un feuillet : {q['combien_sautent']} sur "
                    f"{q['combien_de_boucles']}", 0, ALERTE if q["combien_sautent"] else GRIS)
    ecrire(tx, 316, f"|L| ≥ {int(demi)} vx : deux chemins, deux spires", 0, GRIS)
    ecrire(tx, 352, f"dispersion des pas horizontaux {_fr(lec['la_dispersion_des_pas_horizontaux'], 4)} vx",
           0, GRIS)
    ecrire(tx, 370, f"dispersion des pas verticaux {_fr(lec['la_dispersion_des_pas_verticaux'], 4)} vx",
           0, GRIS)
    fo = d["le_detail_aux_colonnes_fortes"]
    ecrire(tx, 400, f"aux {len(fo['les_colonnes'])} colonnes fortes de 219 : "
                    f"{fo['combien_ont_la_forme_dune_erreur']} ont la forme d'une erreur,", 0, ENCRE)
    ecrire(tx, 416, f"{fo['combien_se_ferment']} se ferment, {fo['combien_mixtes']} mixte"
                    f"{'s' if fo['combien_mixtes'] > 1 else ''}", 0, ENCRE)

    # ── PANNEAU 3 · LE NUL ──────────────────────────────────────────────────────────────────
    panneau(50, 460, 480, 792, "LE NUL · la moitié verticale décalée")
    nul = [float(x) for x in ep["les_rapports_du_nul"]]
    rho = float(ep["le_rapport_de_fermeture"])
    lo = min(min(nul), rho) - 0.02
    hi = max(max(nul), rho) + 0.02
    hx0, hx1, hy0, hy1 = 80, 450, 510, 690
    casiers = 30
    comptes = [0] * casiers
    for x in nul:
        comptes[min(casiers - 1, int((x - lo) / (hi - lo) * casiers))] += 1
    cmax = max(comptes)
    w = (hx1 - hx0) / casiers
    for i, k in enumerate(comptes):
        if k:
            art.rectangle([hx0 + i * w + 1, hy1 - (hy1 - hy0) * k / cmax, hx0 + (i + 1) * w - 1, hy1],
                          fill=LEGER)
    art.line([hx0, hy1, hx1, hy1], fill=GRIS, width=1)
    xr = hx0 + (hx1 - hx0) * (rho - lo) / (hi - lo)
    art.line([xr, hy0 - 4, xr, hy1], fill=BON if ep["se_ferment"] else ALERTE, width=3)
    points.append((xr, hy0 - 4))
    traces["le_nul"] = len(nul)
    ecrire(hx0, hy1 + 6, _fr(lo, 2), 0, GRIS)
    ecrire(hx1 - 30, hy1 + 6, _fr(hi, 2), 0, GRIS)
    ecrire(66, 718, f"{ep['combien_de_decalages']} décalages d'au moins {ep['le_plus_petit_decalage']} "
                    f"coutures · médiane {_fr(ep['le_rapport_median_du_nul'], 4)}", 0, GRIS)
    ecrire(66, 736, f"au moins aussi fermés : {ep['decalages_au_moins_aussi_fermes']} · P = "
                    f"{_fr(ep['la_valeur_p'], 4)}", 0, ENCRE)
    if et.get("replicats"):
        ecrire(66, 758, f"étalon, {et['replicats']} matières : voit {_fr(et['le_taux_sur_la_matiere_coherente'], 4)}, "
                        f"faux {_fr(et['le_taux_de_faux'], 4)}, chunk {_fr(et['le_taux_sur_lerreur_de_chunk'], 4)}",
               0, GRIS)
    else:
        ecrire(66, 758, f"étalon : {et.get('raison')}", 0, ALERTE)

    # ── PANNEAU 4 · LES VARIANCES ───────────────────────────────────────────────────────────
    panneau(500, 460, 880, 792, "CONTRE LE BRUIT DE LECTURE")
    vals = [("A · désaccord", pl["la_variance_de_A"], pl["le_plancher_de_A"]),
            ("B · vertical", pl["la_variance_de_B"], pl["le_plancher_de_B"]),
            ("L · boucle", pl["la_variance_de_L"], pl["le_plancher_de_L"])]
    ech = max(max(v, f) for _, v, f in vals) * 1.1
    bx, bw, yy = 620, 180, 510
    for nom, v_, f_ in vals:
        ecrire(516, yy, nom, 0, ENCRE)
        barre(bx, yy, bw, v_ / ech, 10, CONTRE)
        barre(bx, yy + 14, bw, f_ / ech, 6, GRIS)
        ecrire(bx + bw + 8, yy - 1, f"{_fr(v_, 2)}", 0, ENCRE)
        ecrire(bx + bw + 8, yy + 12, f"{_fr(f_, 2)}", 0, GRIS)
        yy += 48
    ecrire(516, yy + 4, "en bleu la variance, en gris son plancher", 0, GRIS)
    ecrire(516, yy + 22, "de lecture (deux demi-moyennes)", 0, GRIS)
    ecrire(516, 718, f"excès du désaccord : {_fr(pl['lexces_de_A_sur_son_plancher'], 4)} vx²", 0, ENCRE)
    ecrire(516, 736, f"dont géométrique : {_fr(pl['la_part_geometrique'], 4)} vx²", 0, BON)

    # ── PANNEAU 5 · LES TROIS SURFACES ──────────────────────────────────────────────────────
    r0 = la_rangee_montree(d)
    s0 = d["les_trois_surfaces"][r0]
    panneau(900, 460, 1310, 792, f"TROIS SURFACES · boucles {r0}-{int(r0) + 1}, colonnes "
                                 f"{s0['le_troncon'][0]}–{s0['le_troncon'][1]}")
    sx0, sx1, sy0, sy1 = 960, 1290, 500, 640
    cum = s0["les_cumuls"]
    bs = max(demi * 1.15, max(abs(x) for y in cum.values() for x in y) * 1.1)

    def qy(v):
        return sy0 + (sy1 - sy0) * (bs - float(v)) / (2.0 * bs)
    for yv in (demi, 0.0, -demi):
        art.line([sx0, qy(yv), sx1, qy(yv)], fill=ALERTE if yv else TRAIT, width=1)
    ecrire(sx0 - 50, qy(demi) - 7, f"+{int(demi)}", 0, ALERTE)
    ecrire(sx0 - 50, qy(-demi) - 7, f"-{int(demi)}", 0, ALERTE)
    styles = (("sigma_A", ALERTE, 1, "ΣA · chaque rangée, vertical constant"),
              ("sigma_B", CONTRE, 2, "ΣB · pas commun, vertical lu"),
              ("sigma_A_plus_B", BON, 3, "Σ(A+B) · deux chemins"))
    for k, coul, wd, _lab in styles:
        s = cum[k]
        pts = [(sx0 + (sx1 - sx0) * j / (len(s) - 1), qy(v)) for j, v in enumerate(s)]
        art.line(pts, fill=coul, width=wd)
        points.extend(pts)
        traces[k] = len(s)
    yy = 652
    for k, coul, _wd, lab in styles:
        ecrire(916, yy, lab, 0, coul)
        yy += 16
    yy += 6
    ecrire(916, yy, "séparations ΣA · ΣB · Σ(A+B), en vx", 0, ENCRE)
    yy += 16
    for r_, x_ in sorted(d["les_trois_surfaces"].items()):
        if not x_.get("decidable"):
            continue
        ecrire(916, yy, f"{r_}-{int(r_) + 1} : {_fr(x_['la_separation_sigma_A'], 2)} · "
                        f"{_fr(x_['la_separation_sigma_B'], 2)} · {_fr(x_['la_separation_sigma_A_plus_B'], 2)}",
               0, GRIS)
        yy += 15

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 810, L, H], fill=BANDE)
    ecrire(50, 830, f"CE QUI RESTE : {d['le_verdict']['ce_qui_reste']}", moyen, ENCRE)
    ecrire(50, 866, "⚠ ce qui n'est PAS établi : une boucle est aveugle à ce qu'un chunk entier porte — "
                    "une erreur de chunk la ferme comme une géométrie.", moyen, ALERTE)
    ecrire(50, 890, "⚠ ni qu'un pas soit juste : un pas lu à un feuillet près ferme sa boucle comme un pas "
                    "juste. La fermeture dit la cohérence, pas la justesse.", moyen, ALERTE)
    ecrire(50, 924, "★ une lecture neuve : les bords haut et bas des chunks des cinq rangées de 219, par le "
                    "même lecteur et le même filtre.", moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_222.png"
    _, poses, cadres, barres, points, traces = dessiner(d, tmp)

    issues = ("les_boucles_se_ferment", "elles_ne_se_ferment_pas", "letalon_ne_tient_pas")
    v("★★★★ les trois titres possibles sont distincts",
      len({le_titre({"le_verdict": {"lissue": i}}) for i in issues}) == 3)
    v("★★★★ le titre chiffre la part expliquée quand les boucles se ferment",
      d["le_verdict"]["lissue"] != "les_boucles_se_ferment"
      or f"{round(100 * float(d['le_plancher']['la_part_expliquee_de_lexces']))} %" in le_titre(d))
    v("★★★ le titre LIT le verdict",
      le_titre(d).startswith(le_titre({"le_verdict": {"lissue": d["le_verdict"]["lissue"]}})))
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
      all(0 <= x <= 1360 and 0 <= y <= 1000 for x, y in points))
    nb = sum(len(s) for s in d["les_boucles"].values())
    v("★★★★ chaque boucle complète est un point du nuage, aucune n'est résumée",
      traces.get("les_boucles") == nb == d["lepreuve"]["combien_de_boucles"],
      f"{traces.get('les_boucles')} {nb} {d['lepreuve']['combien_de_boucles']}")
    v("★★★★ chaque rapport du nul est dans l'histogramme",
      traces.get("le_nul") == len(d["lepreuve"]["les_rapports_du_nul"])
      == d["lepreuve"]["combien_de_decalages"])
    s0 = d["les_trois_surfaces"][la_rangee_montree(d)]
    v("★★★★ les trois cumuls du tronçon montré sont tracés ENTIERS",
      all(traces.get(k) == len(s0["les_cumuls"][k]) == s0["combien_de_boucles"] + 1
          for k in ("sigma_A", "sigma_B", "sigma_A_plus_B")))
    txt = " ".join(t for _, _, t, _ in poses)
    ep, pl, et = d["lepreuve"], d["le_plancher"], d["letalon"]
    v("★★★★ elle porte le rapport de fermeture, sa valeur P et la médiane du nul",
      _fr(ep["le_rapport_de_fermeture"], 4) in txt and _fr(ep["la_valeur_p"], 4) in txt
      and _fr(ep["le_rapport_median_du_nul"], 4) in txt)
    v("★★★★ elle porte les variances, les planchers et la part géométrique",
      all(_fr(pl[k], 4) in txt for k in ("la_variance_de_A", "la_variance_de_B",
                                          "la_variance_de_L", "la_part_geometrique",
                                          "lexces_de_A_sur_son_plancher")))
    v("★★★★ elle porte l'étalon, et l'erreur de chunk à côté",
      not et.get("replicats") or all(_fr(et[k], 4) in txt for k in (
          "le_taux_sur_la_matiere_coherente", "le_taux_de_faux", "le_taux_sur_lerreur_de_chunk")))
    v("★★★★ elle porte les trois séparations de chaque rangée de boucles",
      all(f"{_fr(x['la_separation_sigma_A'], 2)} · {_fr(x['la_separation_sigma_B'], 2)} · "
          f"{_fr(x['la_separation_sigma_A_plus_B'], 2)}" in txt
          for x in d["les_trois_surfaces"].values() if x.get("decidable")))
    v("★★★★ elle dit ce qui n'est PAS établi — l'erreur de chunk et le pas lu à un feuillet près",
      "n'est PAS établi" in txt and "chunk entier" in txt and "feuillet près" in txt)
    v("★★★ elle dit que la lecture est neuve", "une lecture neuve" in txt)
    fo = d["le_detail_aux_colonnes_fortes"]
    v("★★★★ elle porte les formes aux colonnes fortes",
      f"{fo['combien_ont_la_forme_dune_erreur']} ont la forme d'une erreur" in txt
      and f"{fo['combien_se_ferment']} se ferment" in txt)
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
                   default=RACINE / "docs" / "mesures" / "les_boucles_se_ferment_elles.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "222_les_boucles_se_ferment_elles.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
