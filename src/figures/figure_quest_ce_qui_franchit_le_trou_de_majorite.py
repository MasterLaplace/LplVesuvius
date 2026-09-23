"""Qu'est-ce qui franchit le trou de majorité : les règles sur des trous cachés, le grand rectangle, les boucles.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, LES RÈGLES SUR DES TROUS CACHÉS : pour
chaque longueur de trou que les bandes montrent, l'écart le plus grand de chaque règle au consensus, contre
le demi-feuillet. En haut à droite, LE GRAND RECTANGLE une fois le trou franchi : ses deux chemins et
l'écart à l'arrivée, c'est le panneau qui conclut. En bas, LES CINQ BOUCLES contre le bruit seul, et la
règle de contrôle.

  uv run python src/figures/figure_quest_ce_qui_franchit_le_trou_de_majorite.py \\
      --json docs/mesures/quest_ce_qui_franchit_le_trou_de_majorite.json \\
      --sortie docs/images/225_quest_ce_qui_franchit_le_trou_de_majorite.png
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
BRUIT = (222, 220, 214)
PALE = (170, 180, 205)

LES_BOUCLES = ("haut_gauche", "haut_droite", "bas_gauche", "bas_droite", "le_grand_rectangle")
LES_NOMS = {"haut_gauche": "en haut à gauche", "haut_droite": "en haut à droite",
            "bas_gauche": "en bas à gauche", "bas_droite": "en bas à droite",
            "le_grand_rectangle": "le grand rectangle"}
LES_REGLES_SIMULEES = (("le_maillage", "le maillage (pas nul)", BON),
                       ("deux_lignes", "deux lignes présentes", CONTRE),
                       ("une_ligne", "une ligne présente", ALERTE))
L_, H_ = 1360, 1040


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def _signe(x) -> str:
    return ("+" if float(x) > 0 else "") + _fr(x, 4)


def lire(chemin: Path) -> dict:
    """Le JSON de `quest_ce_qui_franchit_le_trou_de_majorite.py`.

    ⚠⚠⚠ SANS LE GRAND RECTANGLE EN DEUX CHEMINS, la figure tracerait un résumé ; sans l'étalon, l'épreuve
    se lirait comme si elle tenait sa garantie.
    """
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("la_simulation", "les_longueurs_observees", "la_regle_retenue", "les_franchissements",
                "les_trous_des_boucles", "le_verdict", "la_reproduction_de_224"):
        if not d.get(cle):
            raise SystemExit(f"{cle} manque")
    r = d["le_verdict"]["la_regle"]
    if r and not (d["les_franchissements"][r].get("le_grand_rectangle_en_deux_chemins")
                  and d["les_franchissements"][r].get("letalon_de_lepreuve")):
        raise SystemExit("le grand rectangle ou l'étalon de la règle retenue manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if v["la_regle"] is None:
        return "AUCUNE RÈGLE NE FRANCHIT TOUS LES TROUS DE MAJORITÉ SANS QUITTER LE FEUILLET"
    n = "LE MAILLAGE" if v["la_regle"] == "le_maillage" else "LES LIGNES PRÉSENTES"
    if v["les_boucles_qui_depassent"]:
        return f"{n} FRANCHIT LE TROU, ET LE GRAND RECTANGLE ATTEINT ALORS LE DEMI-FEUILLET"
    if not v["le_grand_rectangle_se_ferme"]:
        return f"{n} FRANCHIT LE TROU, MAIS LE GRAND RECTANGLE RESTE OUVERT"
    return f"{n} FRANCHIT LE TROU, ET LE GRAND RECTANGLE SE FERME SUR LA MÊME SPIRE"


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, int] = {}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    ve, sim, rr = d["le_verdict"], d["la_simulation"], d["la_regle_retenue"]
    demi = float(d["demi_pli_en_voxels"])
    ks = [int(k) for k in d["les_longueurs_observees"]]
    r = ve["la_regle"]
    fr_ = d["les_franchissements"].get(r) or {}
    autre = next((x for x in ("le_maillage", "les_lignes_presentes") if x != r), None)
    fa = d["les_franchissements"].get(autre) or {}
    trou = d["les_trous_des_boucles"][0]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"aucune lecture neuve · les six bandes de 224, rejouées à l'identique sur leurs "
                   f"{d['la_reproduction_de_224']['les_boucles_fermables']} boucles fermées · longueurs de trou "
                   f"observées : " + ", ".join(str(k) for k in ks) + " coutures", petit, GRIS)

    # ── PANNEAU 1 · LES REGLES SUR DES TROUS CACHES ─────────────────────────────────────────
    panneau(50, 84, 670, 470, "LES RÈGLES SUR DES TROUS CACHÉS · écart au consensus")
    gx0, gx1, gy0, gy1 = 110, 470, 140, 396
    haut = max(demi * 1.25, max(float(sim[str(k)][n_]["la_plus_grande"]) for k in ks
                                for n_, _l, _c in LES_REGLES_SIMULEES) * 1.1)

    def px(i):
        return gx0 + (gx1 - gx0) * i / max(1, len(ks) - 1)

    def py(v):
        return gy1 - (gy1 - gy0) * float(v) / haut
    art.line([gx0, py(demi), gx1, py(demi)], fill=ALERTE, width=1)
    ecrire(gx0 - 56, py(demi) - 7, f"{int(demi)} vx", 0, ALERTE)
    art.line([gx0, gy1, gx1, gy1], fill=TRAIT, width=1)
    ecrire(gx0 - 20, gy1 - 7, "0", 0, GRIS)
    for i, k in enumerate(ks):
        ecrire(px(i) - 6, gy1 + 6, str(k), 0, GRIS)
    ecrire(gx0 + 120, gy1 + 22, "longueur du trou, en coutures", 0, GRIS)
    for n_, lab, coul in LES_REGLES_SIMULEES:
        pts = [(px(i), py(sim[str(k)][n_]["la_plus_grande"])) for i, k in enumerate(ks)]
        art.line(pts, fill=coul, width=2)
        for x, y in pts:
            art.ellipse([x - 3, y - 3, x + 3, y + 3], fill=coul)
        med = [(px(i), py(sim[str(k)][n_]["la_mediane"])) for i, k in enumerate(ks)]
        art.line(med, fill=coul, width=1)
        traces[n_] = len(pts)
        points.extend(pts + med)
    yy = 150
    for n_, lab, coul in LES_REGLES_SIMULEES:
        dep = sum(sim[str(k)][n_]["combien_au_dela_du_demi_pli"] for k in ks)
        tot = sum(sim[str(k)][n_]["combien"] for k in ks)
        ecrire(490, yy, lab, 0, coul)
        ecrire(490, yy + 16, f"au plus {_fr(sim[str(ks[-1])][n_]['la_plus_grande'], 4)} vx à {ks[-1]}", 0, GRIS)
        ecrire(490, yy + 32, f"{dep} fenêtres sur {tot} au-delà", 0, ALERTE if dep else GRIS)
        yy += 62
    ecrire(490, 350, "trait épais : l'écart le plus grand", 0, GRIS)
    ecrire(490, 366, "trait fin : l'écart médian", 0, GRIS)
    ecrire(66, 436, "chaque fenêtre où la majorité existe, cachée puis franchie par chaque règle", 0, GRIS)
    ecrire(66, 452, f"retenue : {'le maillage' if r == 'le_maillage' else 'les lignes présentes' if r else 'aucune'}"
                    f", {_fr(rr.get('lecart_le_plus_grand_a_la_longueur_des_trous'), 4)} vx au plus à "
                    f"{trou['la_longueur']} coutures", 0, ENCRE)

    # ── PANNEAU 2 · LE GRAND RECTANGLE ──────────────────────────────────────────────────────
    panneau(690, 84, 1310, 470, "LE GRAND RECTANGLE · le trou franchi par la règle retenue")
    g = (fr_.get("les_boucles") or {}).get("le_grand_rectangle") or {}
    ch = fr_.get("le_grand_rectangle_en_deux_chemins") or {}
    if ch:
        a_, b_ = ch["par_la_rangee_dabord"], ch["par_la_colonne_dabord"]
        borne = max(demi * 1.1, max(abs(x) for x in a_ + b_) * 1.1, abs(a_[-1]) + demi * 1.05)
        hx0, hx1, hy0, hy1 = 740, 1210, 140, 420

        def qy(v):
            return hy0 + (hy1 - hy0) * (borne - float(v)) / (2.0 * borne)
        art.line([hx0, qy(0), hx1, qy(0)], fill=TRAIT, width=1)
        ecrire(hx0 - 16, qy(0) - 7, "0", 0, GRIS)
        for k_, serie, coul in (("par_la_rangee_dabord", a_, BON), ("par_la_colonne_dabord", b_, CONTRE)):
            pts = [(hx0 + (hx1 - hx0) * j / (len(serie) - 1), qy(v)) for j, v in enumerate(serie)]
            art.line(pts, fill=coul, width=2)
            traces[f"grand:{k_}"] = len(serie)
            points.extend(pts)
        art.line([hx1 + 10, qy(a_[-1] + demi), hx1 + 10, qy(a_[-1] - demi)], fill=ALERTE, width=2)
        for yv in (a_[-1] + demi, a_[-1] - demi):
            art.line([hx1 + 5, qy(yv), hx1 + 15, qy(yv)], fill=ALERTE, width=1)
        art.ellipse([hx1 + 6, qy(b_[-1]) - 4, hx1 + 14, qy(b_[-1]) + 4], fill=CONTRE)
        points += [(hx1 + 15, qy(a_[-1] - demi)), (hx1 + 15, qy(a_[-1] + demi))]
        ecrire(706, 110, "par la rangée d'abord", 0, BON)
        ecrire(856, 110, "par la colonne d'abord", 0, CONTRE)
        ecrire(1016, 110, f"± {int(demi)} vx autour de l'arrivée", 0, ALERTE)
        ecrire(1226, 150, "L =", 0, ENCRE)
        ecrire(1226, 166, f"{_signe(g['la_fermeture_en_voxels'])}", 0, ALERTE if not g["sous_le_demi_pli"] else BON)
        ecrire(1226, 182, "vx", 0, ENCRE)
        ecrire(706, 436, f"{len(a_) - 1} coutures par chemin · le trou de la "
                         f"{'rangée' if trou['le_sens'] == 'rangees' else 'colonne'} {trou['le_centre']}, "
                         f"coutures {trou['le_debut']} et {trou['le_debut'] + 1}, franchi par des pas "
                         f"{'nuls' if r == 'le_maillage' else 'lus'}", 0, GRIS)

    # ── PANNEAU 3 · LES CINQ BOUCLES CONTRE LE BRUIT SEUL ────────────────────────────────────
    panneau(50, 490, 1310, 800, "LES CINQ BOUCLES CONTRE LE BRUIT SEUL · |L| en voxels, le trou franchi")
    ax0, ax1 = 250, 780
    hautb = 75.0

    def ax(v):
        return ax0 + (ax1 - ax0) * min(float(v), hautb) / hautb
    yl0 = 530
    for v_, lab, coul in ((demi, f"demi-feuillet {int(demi)}", ALERTE),
                          (2 * demi, f"un feuillet {int(2 * demi)}", GRIS)):
        art.line([ax(v_), yl0 - 4, ax(v_), yl0 + 5 * 32 - 6], fill=coul, width=1)
        ecrire(ax(v_) - 30, yl0 + 5 * 32 - 2, lab, 0, coul)
    ecrire(ax0 - 4, yl0 + 5 * 32 - 2, "0", 0, GRIS)
    yy = yl0
    for n in LES_BOUCLES:
        b = (fr_.get("les_boucles") or {}).get(n) or {}
        ecrire(66, yy, LES_NOMS[n], 0, ENCRE)
        art.line([ax0, yy + 7, ax1, yy + 7], fill=TRAIT, width=1)
        if not b.get("fermable"):
            ecrire(ax0 + 8, yy, "ouverte", 0, ALERTE)
            yy += 32
            continue
        nl = b.get("le_nul") or {}
        if nl:
            art.rectangle([ax0, yy + 3, ax(nl["la_fermeture_mediane_du_nul_en_valeur_absolue"]), yy + 11], fill=BRUIT)
        ba = (fa.get("les_boucles") or {}).get(n) or {}
        if ba.get("fermable"):
            La = abs(float(ba["la_fermeture_en_voxels"]))
            art.ellipse([ax(La) - 4, yy + 3, ax(La) + 4, yy + 11], outline=CONTRE)
            points.append((ax(La) + 4, yy + 11))
        L = abs(float(b["la_fermeture_en_voxels"]))
        coul = BON if b["sous_le_demi_pli"] else ALERTE
        art.ellipse([ax(L) - 5, yy + 2, ax(L) + 5, yy + 12], fill=coul)
        points.append((ax(L) + 5, yy + 12))
        ecrire(800, yy, f"L = {_signe(b['la_fermeture_en_voxels'])} vx", 0, coul)
        if nl:
            ecrire(940, yy, f"bruit : médiane {_fr(nl['la_fermeture_mediane_du_nul_en_valeur_absolue'], 4)}, "
                            f"{_fr(nl['la_part_du_nul_sous_le_demi_pli'], 4)} dessous", 0, GRIS)
        yy += 32
    ecrire(66, 718, "gris : médiane du bruit seul (demi-côtés tirés indépendamment) · cercle creux : le trou "
                    "franchi par l'autre règle, contrôle nommé", 0, GRIS)
    ep, et = fr_.get("lepreuve") or {}, fr_.get("letalon_de_lepreuve") or {}
    if ep.get("decidable"):
        ecrire(66, 740, f"Σ L² sur les {len(ep['les_rectangles'])} rectangles : {_fr(ep['la_statistique'], 4)} contre "
                        f"{_fr(ep['la_statistique_mediane_du_nul'], 4)} pour des marches indépendantes · p = "
                        f"{_fr(ep['la_valeur_p'], 4)}", 0, ENCRE)
    if et:
        ecrire(66, 760, f"étalon : au θ dérivé {_fr(et['le_theta'], 4)}, {et['combien_concluent_mieux']} sur "
                        f"{et['les_replicats']} jeux de marches indépendantes concluent à tort « mieux » "
                        f"(borne {_fr(et['la_borne'], 4)})", 0, ENCRE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 834, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    s_last = sim[str(ks[-1])]
    ecrire(50, 858, f"★ à un trou de {ks[-1]} coutures, suivre le maillage s'écarte au plus de "
                    f"{_fr(s_last['le_maillage']['la_plus_grande'], 4)} vx du consensus ; deux lignes de "
                    f"{_fr(s_last['deux_lignes']['la_plus_grande'], 4)} ; une ligne quitte le feuillet "
                    f"{s_last['une_ligne']['combien_au_dela_du_demi_pli']} fois.", moyen, ENCRE)
    if ch:
        ecrire(50, 884, f"⚠ le trou franchi, les quatre rectangles restent sous le demi-feuillet, mais le grand "
                        f"rectangle ferme à {_signe(g['la_fermeture_en_voxels'])} vx :", moyen, ALERTE)
        ecrire(50, 904, f"   à deux fois la longueur, les deux chemins arrivent à un demi-feuillet l'un de "
                        f"l'autre, et le bruit seul n'y reste dessous que dans "
                        f"{_fr((g.get('le_nul') or {}).get('la_part_du_nul_sous_le_demi_pli'), 4)} des tirages.",
               moyen, ALERTE)
    ecrire(50, 934, "⚠ ce qui n'est PAS établi : que le consensus soit la vérité au trou — la référence des "
                    "trous cachés est le consensus lui-même.", moyen, ALERTE)
    ecrire(50, 964, "★ la suite : au-delà du quart de segment, qu'est-ce qui garde deux chemins sur la même "
                    "spire, quand l'erreur du consensus s'accumule comme une marche ?", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


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
    tmp = sortie.parent / ".sonde_225.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(regle, dep, grand):
        return {"le_verdict": {"la_regle": regle, "les_boucles_qui_depassent": dep,
                               "le_grand_rectangle_se_ferme": grand}}
    titres = {le_titre(_v("le_maillage", dp, gr)) for dp in ([], ["a"]) for gr in (True, False)}
    titres.add(le_titre(_v(None, [], True)))
    v("★★★★ les quatre titres possibles sont distincts, et dépasser prime",
      len(titres) == 4 and le_titre(_v("le_maillage", ["a"], False)) == le_titre(_v("le_maillage", ["a"], True)))
    v("★★★ le titre LIT le verdict",
      ("DEMI-FEUILLET" in le_titre(d)) == bool(d["le_verdict"]["les_boucles_qui_depassent"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile",
      all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    ks = d["les_longueurs_observees"]
    v("★★★★ chaque règle est tracée à chaque longueur observée",
      all(traces.get(n_) == len(ks) for n_, _l, _c in LES_REGLES_SIMULEES))
    r = d["le_verdict"]["la_regle"]
    ch = d["les_franchissements"][r]["le_grand_rectangle_en_deux_chemins"]
    v("★★★★ les deux chemins du grand rectangle sont tracés ENTIERS",
      traces.get("grand:par_la_rangee_dabord") == len(ch["par_la_rangee_dabord"])
      and traces.get("grand:par_la_colonne_dabord") == len(ch["par_la_colonne_dabord"]))
    txt = " ".join(t for _, _, t, _ in poses)
    fr_ = d["les_franchissements"][r]
    v("★★★★ elle porte la fermeture de chaque boucle, le trou franchi, et le bruit seul de chacune",
      all(f"L = {_signe(b['la_fermeture_en_voxels'])} vx" in txt
          and f"médiane {_fr(b['le_nul']['la_fermeture_mediane_du_nul_en_valeur_absolue'], 4)}" in txt
          for b in fr_["les_boucles"].values() if b.get("fermable")))
    sim = d["la_simulation"]
    v("★★★★ elle porte, pour chaque règle, l'écart le plus grand à la plus longue et ce qui passe au-delà",
      all(f"au plus {_fr(sim[str(ks[-1])][n_]['la_plus_grande'], 4)} vx à {ks[-1]}" in txt
          for n_, _l, _c in LES_REGLES_SIMULEES))
    ep, et = fr_["lepreuve"], fr_["letalon_de_lepreuve"]
    v("★★★★ elle porte l'épreuve et son étalon",
      _fr(ep["la_statistique"], 4) in txt and f"p = {_fr(ep['la_valeur_p'], 4)}" in txt
      and f"{et['combien_concluent_mieux']} sur {et['les_replicats']}" in txt and _fr(et["le_theta"], 4) in txt)
    v("★★★★ elle dit ce qui n'est PAS établi", "n'est PAS établi" in txt and "consensus lui-même" in txt)
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
                   default=RACINE / "docs" / "mesures" / "quest_ce_qui_franchit_le_trou_de_majorite.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "225_quest_ce_qui_franchit_le_trou_de_majorite.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
