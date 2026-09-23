"""Où est l'erreur de la boucle en haut à gauche : les quatre boucles fines, leur bruit, et la règle qui désigne.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LE QUADRANT COUPÉ EN QUATRE : chaque boucle fine
et sa fermeture, le trou franchi par la règle de `225`, et la boucle en haut à gauche qui est leur somme. À
droite en haut, CE QUE LE BRUIT SEUL DONNERAIT : pour chaque boucle fine, la part des tirages indépendants
qui ferment moins qu'elle, contre le seuil de la règle — c'est le panneau qui conclut. À droite en bas, LA
MESURE TELLE QUE DÉCLARÉE, sans franchir, et L'ÉTALON de la règle.

  uv run python src/figures/figure_ou_est_lerreur_de_la_boucle_en_haut_a_gauche.py \\
      --json docs/mesures/ou_est_lerreur_de_la_boucle_en_haut_a_gauche.json \\
      --sortie docs/images/227_ou_est_lerreur_de_la_boucle_en_haut_a_gauche.png
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
MOYEN = (196, 150, 70)
CONTRE = (92, 108, 150)
BRUIT = (222, 220, 214)
LES_FINES = ("haut_gauche", "haut_droite", "bas_gauche", "bas_droite")
LES_NOMS = {"haut_gauche": "en haut à gauche", "haut_droite": "en haut à droite",
            "bas_gauche": "en bas à gauche", "bas_droite": "en bas à droite"}
L_, H_ = 1360, 1000


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
    """Le JSON de `ou_est_lerreur_de_la_boucle_en_haut_a_gauche.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("lanalyse_du_treillis_fin", "sans_franchir", "letalon_de_la_designation", "le_verdict",
                "le_seuil_de_sortie", "le_treillis_fin", "la_reproduction"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v["la_regle_tient"]:
        return "LA RÈGLE DE DÉSIGNATION NE TIENT PAS SA GARANTIE : ELLE NE DÉSIGNE RIEN"
    if not v["les_boucles_qui_sortent"]:
        return "AUCUNE BOUCLE FINE NE SORT DU BRUIT : RIEN NE LOCALISE L'ERREUR AU-DELÀ DU BRUIT"
    if len(v["les_boucles_qui_sortent"]) == 1:
        return f"UNE BOUCLE FINE SORT DU BRUIT : {LES_NOMS.get(v['les_boucles_qui_sortent'][0], '').upper()}"
    return "PLUSIEURS BOUCLES FINES SORTENT DU BRUIT : L'ERREUR N'EST PAS UNE"


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

    a, ve, et = d["lanalyse_du_treillis_fin"], d["le_verdict"], d["letalon_de_la_designation"]
    B, pr = a["les_boucles"], a["lepreuve"]["par_rectangle"]
    Rf, Cf = d["le_treillis_fin"]["rangees"], d["le_treillis_fin"]["colonnes"]
    seuil = float(d["le_seuil_de_sortie"])
    tf = d.get("le_trou_franchi")

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"le quadrant en haut à gauche coupé en quatre par la rangée {Rf[1]} et la colonne {Cf[1]}, lues "
                   f"pour cette tranche et retombées sur 219, 223 et 224 en {d['la_reproduction']['combien_de_coutures_relues']} "
                   f"coutures · l'analyse est celle de 224, appelée", petit, GRIS)

    # ── PANNEAU 1 · LE QUADRANT COUPE EN QUATRE ─────────────────────────────────────────────
    panneau(50, 84, 560, 780, "LE QUADRANT · quatre boucles fines")
    x0, x1, y0, y1 = 110, 500, 150, 640
    xm = x0 + (x1 - x0) * (Cf[1] - Cf[0]) / (Cf[2] - Cf[0])
    ym = y0 + (y1 - y0) * (Rf[1] - Rf[0]) / (Rf[2] - Rf[0])
    boites = {"haut_gauche": (x0, y0, xm, ym), "haut_droite": (xm, y0, x1, ym),
              "bas_gauche": (x0, ym, xm, y1), "bas_droite": (xm, ym, x1, y1)}
    for n, (a0, b0, a1, b1) in boites.items():
        part = float(pr[n]["la_part_du_nul_sous_la_fermeture"])
        coul = ALERTE if part >= seuil else (MOYEN if part >= 0.75 else BON)
        art.rectangle([a0 + 3, b0 + 3, a1 - 3, b1 - 3], outline=coul, width=3)
        ecrire((a0 + a1) / 2 - 52, (b0 + b1) / 2 - 16, f"L = {_signe(B[n]['la_fermeture_en_voxels'])} vx", 0, coul)
        ecrire((a0 + a1) / 2 - 52, (b0 + b1) / 2 + 2, f"bruit : {_fr(part, 4)} dessous", 0, GRIS)
        traces[n] = 1
        points.append((a1, b1))
    if tf:
        for band, seams in tf["les_coutures_remplies"].items():
            for sc in seams:
                yy = y0 + (y1 - y0) * (int(sc) - Rf[0]) / (Rf[2] - Rf[0])
                art.rectangle([xm - 6, yy, xm + 6, yy + 4], fill=CONTRE)
    ecrire(x0 - 44, y0 - 7, f"r. {Rf[0]}", 0, ENCRE)
    ecrire(x0 - 44, ym - 7, f"r. {Rf[1]}", 0, ENCRE)
    ecrire(x0 - 44, y1 - 7, f"r. {Rf[2]}", 0, ENCRE)
    ecrire(x0 - 14, y0 - 26, f"col. {Cf[0]}", 0, ENCRE)
    ecrire(xm - 18, y0 - 26, f"col. {Cf[1]}", 0, ENCRE)
    ecrire(x1 - 30, y0 - 26, f"col. {Cf[2]}", 0, ENCRE)
    g = B["le_grand_rectangle"]
    ecrire(66, 666, f"leur somme, la boucle en haut à gauche de 224 : L = {_signe(g['la_fermeture_en_voxels'])} vx", 0, ENCRE)
    if tf:
        ecrire(66, 690, f"en bleu : le trou de la colonne {Cf[1]}, coutures "
                        + " et ".join(str(s_) for s_ in sorted(int(k) for v_ in tf["les_coutures_remplies"].values() for k in v_))
                        + ", franchi par le maillage (225)", 0, CONTRE)
    ecrire(66, 714, "vert : sous les trois quarts du bruit · ocre : au-delà · rouge : au-delà du seuil", 0, GRIS)

    # ── PANNEAU 2 · CE QUE LE BRUIT SEUL DONNERAIT ──────────────────────────────────────────
    panneau(580, 84, 1310, 430, "CE QUE LE BRUIT SEUL DONNERAIT · la part des tirages qui ferment moins")
    ax0, ax1 = 760, 1180

    def ax(v):
        return ax0 + (ax1 - ax0) * max(0.0, min(1.0, float(v)))
    art.line([ax(seuil), 124, ax(seuil), 360], fill=ALERTE, width=2)
    ecrire(ax(seuil) - 80, 366, f"seuil {_fr(seuil, 4)}", 0, ALERTE)
    ecrire(ax0 - 4, 366, "0", 0, GRIS)
    ecrire(ax1 - 4, 382, "1", 0, GRIS)
    yy = 150
    for n in LES_FINES:
        part = float(pr[n]["la_part_du_nul_sous_la_fermeture"])
        coul = ALERTE if part >= seuil else (MOYEN if part >= 0.75 else BON)
        ecrire(596, yy - 7, LES_NOMS[n], 0, ENCRE)
        art.rectangle([ax0, yy - 6, ax1, yy + 6], outline=TRAIT)
        art.rectangle([ax0, yy - 6, ax(part), yy + 6], fill=coul)
        points.append((ax(part), yy + 6))
        ecrire(ax1 + 12, yy - 7, f"{_fr(part, 4)}", 0, coul)
        yy += 52
    ecrire(596, 396, f"une boucle sort du bruit au-delà de 1 − 0,05 / {len(pr)} : la garantie partagée entre les "
                     "boucles fines", 0, GRIS)

    # ── PANNEAU 3 · SANS FRANCHIR, ET L'ETALON ──────────────────────────────────────────────
    panneau(580, 450, 1310, 780, "LA MESURE TELLE QUE DÉCLARÉE, ET L'ÉTALON DE LA RÈGLE")
    sf = d["sans_franchir"]["les_boucles"]
    yy = 494
    ecrire(596, yy, "sans franchir le trou :", 0, ENCRE)
    yy += 22
    for n in LES_FINES:
        b = sf[n]
        if b["fermable"]:
            ecrire(612, yy, f"{LES_NOMS[n]} : L = {_signe(b['la_fermeture_en_voxels'])} vx, bruit "
                            f"{_fr(b['la_part_du_nul_sous_la_fermeture'], 4)} dessous", 0, ENCRE)
        else:
            ecrire(612, yy, f"{LES_NOMS[n]} : ouverte", 0, ALERTE)
        yy += 20
    ecrire(596, yy + 10, "aucune des deux boucles fermées ne sort du bruit" if not d["sans_franchir"]["les_boucles_qui_sortent"]
           else "des boucles sortent du bruit sans franchir", 0, ENCRE)
    ecrire(596, 660, f"étalon : sur des demi-côtés indépendants, au θ dérivé {_fr(et['le_theta'], 4)}, la règle "
                     f"désigne {et['combien_designent']} fois sur {et['les_replicats']}", 0, ENCRE)
    ecrire(596, 680, f"soit {_fr(et['le_taux'], 4)}, sous sa borne {_fr(et['la_borne'], 4)} : "
                     f"{'elle tient sa garantie' if et['elle_tient_sa_garantie'] else 'elle ne la tient pas'}", 0,
           BON if et["elle_tient_sa_garantie"] else ALERTE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 798, L_, H_], fill=BANDE)
    ecrire(50, 812, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    hg = B["haut_gauche"]
    ecrire(50, 836, f"★ la boucle fine en haut à gauche porte {_signe(hg['la_fermeture_en_voxels'])} vx des "
                    f"{_signe(g['la_fermeture_en_voxels'])} de la boucle de 224, et la moitié basse ferme à quelques voxels —",
           moyen, ENCRE)
    ecrire(50, 856, f"   mais le bruit seul la dépasse encore dans une part des tirages : elle ne sort pas du bruit "
                    f"({_fr(pr['haut_gauche']['la_part_du_nul_sous_la_fermeture'], 4)} contre {_fr(seuil, 4)}).",
           moyen, ENCRE)
    ecrire(50, 884, "⚠ ajouté après la lecture : la déclaration n'avait pas prévu de trou dans les bandes fines ; il est "
                    "franchi par la règle de 225, et la mesure déclarée est publiée à côté.", moyen, ALERTE)
    ecrire(50, 912, "⚠ ce qui n'est PAS établi : qu'une erreur de lecture soit là plutôt qu'un bruit qui s'y est "
                    "accumulé — rien ici ne sépare les deux.", moyen, ALERTE)
    ecrire(50, 940, "★ la suite : l'erreur du consensus est un bruit qui s'accumule ; une bande plus large le réduit-elle "
                    "assez pour fermer le grand rectangle ?", moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_227.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(s_, t_):
        return {"le_verdict": {"les_boucles_qui_sortent": s_, "la_regle_tient": t_}}
    titres = {le_titre(_v(s_, t_)) for s_ in ([], ["haut_gauche"], ["haut_gauche", "bas_droite"]) for t_ in (True, False)}
    v("★★★★ les quatre titres possibles sont distincts, et une règle qui ne tient pas prime",
      len(titres) == 4 and le_titre(_v(["haut_gauche"], False)) == le_titre(_v([], False)))
    v("★★★ le titre LIT le verdict",
      ("AUCUNE" in le_titre(d)) == (not d["le_verdict"]["les_boucles_qui_sortent"] and d["le_verdict"]["la_regle_tient"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque boucle fine est tracée", all(traces.get(n) for n in LES_FINES))
    txt = " ".join(t for _, _, t, _ in poses)
    a = d["lanalyse_du_treillis_fin"]
    v("★★★★ elle porte la fermeture et la part du bruit de chaque boucle fine, et la somme de 224",
      all(f"L = {_signe(a['les_boucles'][n]['la_fermeture_en_voxels'])} vx" in txt
          and _fr(a["lepreuve"]["par_rectangle"][n]["la_part_du_nul_sous_la_fermeture"], 4) in txt for n in LES_FINES)
      and _signe(a["les_boucles"]["le_grand_rectangle"]["la_fermeture_en_voxels"]) in txt)
    v("★★★★ elle porte la mesure déclarée, sans franchir, et le seuil",
      "sans franchir le trou" in txt and f"seuil {_fr(d['le_seuil_de_sortie'], 4)}" in txt)
    et = d["letalon_de_la_designation"]
    v("★★★★ elle porte l'étalon de la règle", f"{et['combien_designent']} fois sur {et['les_replicats']}" in txt
      and _fr(et["la_borne"], 4) in txt and _fr(et["le_theta"], 4) in txt)
    v("★★★★ elle dit ce qui a été ajouté après la lecture et ce qui n'est PAS établi",
      "ajouté après la lecture" in txt and "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "mesures" / "ou_est_lerreur_de_la_boucle_en_haut_a_gauche.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "227_ou_est_lerreur_de_la_boucle_en_haut_a_gauche.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
