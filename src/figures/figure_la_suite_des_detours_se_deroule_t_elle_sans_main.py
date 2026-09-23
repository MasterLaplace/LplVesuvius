"""La suite des détours sans main : les neuf cellules, le seuil de la famille, et ce que la procédure retrouve.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA BOUCLE FINE DE `227` CONTOURNÉE PAR SES QUATRE
CÔTÉS : les détours, les neuf cellules et leur fermeture. À droite en haut, LA PART DU BRUIT DE CHAQUE CELLULE
CONTRE LE SEUIL DE LA FAMILLE — et le seuil partagé déclaré d'abord, que son étalon ne tient pas — c'est le
panneau qui conclut. À droite en bas, CE QUE LA PROCÉDURE RETROUVE SANS MAIN : les détours de `229` et `230`
et leurs boucles, recomposées.

  uv run python src/figures/figure_la_suite_des_detours_se_deroule_t_elle_sans_main.py \\
      --json docs/mesures/la_suite_des_detours_se_deroule_t_elle_sans_main.json \\
      --sortie docs/images/231_la_suite_des_detours_se_deroule_t_elle_sans_main.png
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
DETOUR = (206, 218, 230)
LES_CELLULES = ("haut_gauche", "haut_milieu", "haut_droite", "milieu_gauche", "centre", "milieu_droite",
                "bas_gauche", "bas_milieu", "bas_droite")
LES_NOMS = {"haut_gauche": "en haut à gauche", "haut_milieu": "en haut au milieu", "haut_droite": "en haut à droite",
            "milieu_gauche": "au milieu à gauche", "centre": "le centre", "milieu_droite": "au milieu à droite",
            "bas_gauche": "en bas à gauche", "bas_milieu": "en bas au milieu", "bas_droite": "en bas à droite"}
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
    """Le JSON de `la_suite_des_detours_se_deroule_t_elle_sans_main.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("les_niveaux", "le_verdict", "la_reproduction", "les_boucles_publiees", "les_bandes"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    if not d["les_niveaux"] or not d["les_niveaux"][0].get("decidable"):
        raise SystemExit("le premier niveau manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    return d["le_verdict"]["ce_qui_reste_a_mesurer"].split(" : ")[0]


def LA_BANDE(d: dict) -> list[tuple[str, tuple]]:
    """Les phrases de la bande, écrites APRÈS la mesure — chacune lit ses nombres dans le JSON."""
    n = d["les_niveaux"][0]
    ce, sf, et, sp = n["les_cellules"], n["le_seuil_de_la_famille"], n["letalon"], n["le_seuil_partage_declare_dabord"]
    fort = max(ce, key=lambda k: ce[k]["la_part_du_nul_sous_la_fermeture"])
    return [
        (f"★ sans main, la procédure retrouve les détours de 229 et 230 et recompose leurs boucles exactement ; "
         f"elle lit {len(d['les_bandes'])} bandes de plus.", ENCRE),
        (f"★ aucune des neuf cellules ne sort du bruit : la plus forte, {LES_NOMS[fort]}, ferme à "
         f"{_signe(ce[fort]['la_fermeture_en_voxels'])} vx, {_fr(ce[fort]['la_part_du_nul_sous_la_fermeture'], 4)} "
         f"contre le seuil {_fr(sf['le_seuil'], 4)}.", ENCRE),
        (f"⚠ le seuil partagé déclaré d'abord, {_fr(sp['le_seuil'], 4)}, ne tenait pas sa garantie : "
         f"{sp['letalon']['combien_designent']} sur {sp['letalon']['les_replicats']} ; celui de la famille la tient, "
         f"{et['combien_designent']} sur {et['les_replicats']}.", ALERTE),
        ("⚠ ce qui n'est PAS établi : qu'il n'y ait pas d'erreur dans la boucle — seulement qu'une procédure qui ne "
         "choisit pas ne la sépare pas du bruit.", ALERTE)]


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

    n = d["les_niveaux"][0]
    R, C = n["le_treillis"]["rangees"], n["le_treillis"]["colonnes"]
    ce, sf, et, sp = n["les_cellules"], n["le_seuil_de_la_famille"], n["letalon"], n["le_seuil_partage_declare_dabord"]
    tau = sf["le_seuil"]

    def couleur(k):
        part = float(ce[k]["la_part_du_nul_sous_la_fermeture"])
        if k in n["les_cellules_qui_sortent"]:
            return ALERTE
        return MOYEN if part >= 0.75 else BON

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"la boucle fine en haut à gauche de 227, rangées {R[0]} à {R[-1]}, colonnes {C[0]} à {C[-1]}, "
                   f"contournée par ses quatre côtés à la fois · {len(d['les_bandes'])} bandes lues, retombées sur les "
                   f"lectures publiées en {d['la_reproduction']['combien_de_coutures_relues']} coutures", petit, GRIS)

    # ── PANNEAU 1 · LES NEUF CELLULES ───────────────────────────────────────────────────────
    panneau(50, 84, 560, 780, "LES QUATRE DÉTOURS · neuf cellules")
    x0, x1, y0, y1 = 110, 520, 170, 560

    def X(c):
        return x0 + (x1 - x0) * (float(c) - C[0]) / (C[-1] - C[0])

    def Y(r):
        return y0 + (y1 - y0) * (float(r) - R[0]) / (R[-1] - R[0])
    for c in C[1:3]:
        art.rectangle([X(c) - 4, y0, X(c) + 4, y1], fill=DETOUR)
    for r in R[1:3]:
        art.rectangle([x0, Y(r) - 4, x1, Y(r) + 4], fill=DETOUR)
    for k in LES_CELLULES:
        (ra, ca), (rb, cb) = ce[k]["les_coins"]
        art.rectangle([X(ca) + 2, Y(ra) + 2, X(cb) - 2, Y(rb) - 2], outline=couleur(k), width=2)
        traces[k] = 1
        points.append((X(cb), Y(rb)))
    (ra, ca), (rb, cb) = ce["centre"]["les_coins"]
    ecrire((X(ca) + X(cb)) / 2 - 40, (Y(ra) + Y(rb)) / 2 - 7, "le centre", 0, GRIS)
    for band, seams in (n.get("les_coutures_remplies") or {}).items():
        sens, centre = band.split("_")
        for sc in seams:
            if sens == "colonnes":
                art.rectangle([X(int(centre)) - 6, Y(int(sc)), X(int(centre)) + 6, Y(int(sc)) + 4], fill=CONTRE)
    for r in R:
        ecrire(x0 - 52, Y(r) - 7, f"r. {r}", 0, ENCRE)
    for i, c in enumerate(C):
        ecrire(X(c) - 16, y0 - 24 - (16 if i % 2 else 0), f"col. {c}", 0, ENCRE)
    yy = 580
    for k in LES_CELLULES:
        col = 66 if LES_CELLULES.index(k) % 2 == 0 else 310
        if LES_CELLULES.index(k) % 2 == 0 and k != LES_CELLULES[0]:
            yy += 20
        ecrire(col, yy, f"{LES_NOMS[k]} : L = {_signe(ce[k]['la_fermeture_en_voxels'])} vx", 0, couleur(k))
    ecrire(66, 700, "en bleu clair : les quatre détours, qui ne partagent aucune ligne de leur côté", 0,
           GRIS)
    remplies = n.get("les_coutures_remplies") or {}
    if remplies:
        ecrire(66, 720, "en bleu : sans majorité, franchies par le maillage (225) : "
                        + " ; ".join(f"{b_.replace('colonnes_', 'col. ').replace('rangees_', 'r. ')} en "
                                     + " et ".join(str(s_) for s_ in sorted(int(k_) for k_ in v_))
                                     for b_, v_ in sorted(remplies.items())), 0, CONTRE)
    ecrire(66, 750, "vert : sous les trois quarts du bruit · ocre : au-delà · rouge : sortie du bruit", 0, GRIS)

    # ── PANNEAU 2 · LE SEUIL DE LA FAMILLE ──────────────────────────────────────────────────
    panneau(580, 84, 1310, 560, "LA PART DU BRUIT DE CHAQUE CELLULE, CONTRE LE SEUIL DE LA FAMILLE")
    ax0, ax1 = 780, 1170

    def ax(v):
        return ax0 + (ax1 - ax0) * max(0.0, min(1.0, float(v)))
    if tau is not None:
        art.line([ax(tau), 122, ax(tau), 470], fill=ALERTE, width=2)
        ecrire(ax(tau) - 110, 478, f"seuil de la famille {_fr(tau, 4)}", 0, ALERTE)
    for yy_ in range(122, 470, 8):
        art.line([ax(sp["le_seuil"]), yy_, ax(sp["le_seuil"]), yy_ + 4], fill=GRIS, width=1)
    ecrire(ax(sp["le_seuil"]) - 150, 496, f"déclaré d'abord {_fr(sp['le_seuil'], 4)}", 0, GRIS)
    ecrire(ax0 - 4, 478, "0", 0, GRIS)
    yy = 140
    for k in LES_CELLULES:
        part = float(ce[k]["la_part_du_nul_sous_la_fermeture"])
        ecrire(596, yy - 7, LES_NOMS[k], 0, ENCRE)
        art.rectangle([ax0, yy - 6, ax1, yy + 6], outline=TRAIT)
        art.rectangle([ax0, yy - 6, ax(part), yy + 6], fill=couleur(k))
        points.append((ax(part), yy + 6))
        ecrire(ax1 + 14, yy - 7, _fr(part, 4), 0, ENCRE)
        yy += 36
    ecrire(596, 520, f"seuil de la famille : dérivé de {sf['les_calibrations']} calibrations, dont "
                     f"{_fr(sf['la_part_des_maxima_au_seuil'], 4)} l'atteignent", 0, GRIS)
    ecrire(596, 538, f"étalon indépendant : {et['combien_designent']} fois sur {et['les_replicats']}, soit "
                     f"{_fr(et['le_taux'], 4)} sous sa borne {_fr(et['la_borne'], 4)} · au seuil déclaré d'abord : "
                     f"{sp['letalon']['combien_designent']} fois", 0, BON if et["elle_tient_sa_garantie"] else ALERTE)

    # ── PANNEAU 3 · CE QUE LA PROCÉDURE RETROUVE ────────────────────────────────────────────
    panneau(580, 580, 1310, 780, "CE QUE LA PROCÉDURE RETROUVE SANS MAIN")
    dt = n["les_detours"]
    ecrire(596, 622, f"ses détours : colonnes {dt['gauche']} et {dt['droite']}, rangées {dt['haut']} et {dt['bas']} — "
                     f"la colonne {dt['gauche']} est celle de 229, la rangée {dt['haut']} celle de 230", 0, ENCRE)
    yy = 648
    for k_, L in d["les_boucles_publiees"].items():
        ecrire(612 + (330 if list(d["les_boucles_publiees"]).index(k_) % 2 else 0), yy,
               f"{k_.replace('_', ' ')} : {_signe(L)}, recomposée {_signe(n['les_recompositions'][k_])}", 0, ENCRE)
        if list(d["les_boucles_publiees"]).index(k_) % 2:
            yy += 20
    ecrire(596, 750, f"la procédure s'arrête après {len(d['les_niveaux'])} niveau : aucune cellule où descendre", 0,
           GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 798, L_, H_], fill=BANDE)
    ecrire(50, 812, f"LE VERDICT : {d['le_verdict']['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    for i, (texte, coul) in enumerate(LA_BANDE(d)):
        ecrire(50, 836 + 28 * i, texte, moyen, coul)

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
    tmp = sortie.parent / ".sonde_231.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT le verdict", d["le_verdict"]["ce_qui_reste_a_mesurer"].startswith(le_titre(d)))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chacune des neuf cellules est tracée", all(traces.get(k) for k in LES_CELLULES))
    txt = " ".join(t for _, _, t, _ in poses)
    n = d["les_niveaux"][0]
    v("★★★★ elle porte la fermeture et la part du bruit de chaque cellule",
      all(f"L = {_signe(n['les_cellules'][k]['la_fermeture_en_voxels'])} vx" in txt
          and _fr(n["les_cellules"][k]["la_part_du_nul_sous_la_fermeture"], 4) in txt for k in LES_CELLULES))
    v("★★★★ elle porte le seuil de la famille et le seuil déclaré d'abord, avec leurs deux étalons",
      f"seuil de la famille {_fr(n['le_seuil_de_la_famille']['le_seuil'], 4)}" in txt
      and f"déclaré d'abord {_fr(n['le_seuil_partage_declare_dabord']['le_seuil'], 4)}" in txt
      and f"{n['letalon']['combien_designent']} fois sur {n['letalon']['les_replicats']}" in txt
      and f"{n['le_seuil_partage_declare_dabord']['letalon']['combien_designent']} fois" in txt)
    v("★★★★ elle porte chaque boucle publiée et sa recomposition",
      all(f"{_signe(L)}, recomposée {_signe(n['les_recompositions'][k])}" in txt
          for k, L in d["les_boucles_publiees"].items()))
    v("★★★★ elle porte les quatre détours", all(str(x) in txt for x in n["les_detours"].values()))
    v("★★★★ elle dit ce qui n'est PAS établi", "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "mesures" / "la_suite_des_detours_se_deroule_t_elle_sans_main.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "231_la_suite_des_detours_se_deroule_t_elle_sans_main.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
