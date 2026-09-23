"""Un détour sépare-t-il l'erreur de la rangée 99 : la boucle étroite de la rangée, son bruit, et ce qu'elle fait de `229`.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LA MOITIÉ HAUTE DU TREILLIS DE `229` COUPÉE PAR LE
DÉTOUR DE LA RANGÉE : les lignes qui votent pour les rangées 99 et 148, celles du détour, qui n'en partagent
aucune, et les quatre boucles avec leur fermeture — la boucle étroite de la rangée en haut à droite, son
témoin en haut à gauche. À droite en haut, LE SEUL TEST, contre le seuil de la garantie entière — c'est le
panneau qui conclut. À droite en bas, CE QUE LE DÉTOUR FAIT DES DEUX BOUCLES DU HAUT DE `229`, et l'étalon.

  uv run python src/figures/figure_un_detour_separe_t_il_lerreur_de_la_rangee_99.py \\
      --json docs/mesures/un_detour_separe_t_il_lerreur_de_la_rangee_99.json \\
      --sortie docs/images/230_un_detour_separe_t_il_lerreur_de_la_rangee_99.png
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
VOTE = (226, 214, 196)
DETOUR = (206, 218, 230)
LES_BOUCLES = ("haut_droite", "haut_gauche", "bas_droite", "bas_gauche")
LES_NOMS = {"haut_droite": "la boucle étroite de la rangée", "haut_gauche": "le témoin, en haut à gauche",
            "bas_droite": "sous le détour, à droite", "bas_gauche": "sous le détour, à gauche"}
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
    """Le JSON de `un_detour_separe_t_il_lerreur_de_la_rangee_99.py`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("lanalyse_du_treillis_de_la_rangee", "le_test", "letalon_du_test", "le_verdict", "le_treillis",
                "le_detour", "la_reproduction", "les_boucles_de_229_recomposees", "les_bandes_declarees",
                "les_lignes_de_la_rangee", "les_lignes_de_la_rangee_interieure", "les_fermetures_de_229"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if not v["letalon_tient"]:
        return "LE TEST NE TIENT PAS SA GARANTIE SUR SON ÉTALON : IL NE DÉSIGNE RIEN"
    if v["la_boucle_etroite_sort_du_bruit"]:
        return "LA BOUCLE ÉTROITE DE LA RANGÉE SORT DU BRUIT : LA RANGÉE 99 PORTE UNE ERREUR QUE LE DÉTOUR NE PARTAGE PAS"
    return "LA BOUCLE ÉTROITE DE LA RANGÉE NE SORT PAS DU BRUIT : LE DÉTOUR NE SÉPARE PAS LA RANGÉE 99 DU BRUIT"


def _plage(lignes) -> str:
    return f"{min(lignes)} à {max(lignes)}"


def LA_BANDE(d: dict) -> list[tuple[str, tuple]]:
    """Les phrases de la bande, écrites APRÈS la mesure — chacune lit ses nombres dans le JSON."""
    B = d["lanalyse_du_treillis_de_la_rangee"]["les_boucles"]
    t, et, C = d["le_test"], d["letalon_du_test"], d["le_treillis"]["colonnes"]
    return [
        (f"★ la boucle étroite de la rangée ferme à {_signe(t['la_fermeture_en_voxels'])} vx : "
         f"{_fr(t['la_part_du_nul_sous_la_fermeture'], 4)} des tirages ferment moins, au seuil {_fr(t['le_seuil'], 4)}, "
         f"et l'étalon tient à {_fr(et['le_taux'], 4)} sous {_fr(et['la_borne'], 4)}.", ENCRE),
        (f"⚠ de justesse, des deux côtés : {_fr(t['la_part_du_nul_sous_la_fermeture'], 4)} contre le seuil "
         f"{_fr(t['le_seuil'], 4)}, et {_fr(et['le_taux'], 4)} contre la borne {_fr(et['la_borne'], 4)}.", ALERTE),
        (f"★ elle porte une part de {_fr(d['la_part_de_229_portee_par_la_boucle_etroite'], 4)} des "
         f"{_signe(d['les_fermetures_de_229']['haut_droite'])} de 229 entre les colonnes {C[1]} et {C[2]} ; l'autre "
         f"moitié, {_signe(B['bas_droite']['la_fermeture_en_voxels'])} vx, reste sous le détour.", ENCRE),
        (f"⚠ ce qui n'est PAS établi : lequel de ses côtés porte l'erreur — la rangée {d['le_treillis']['rangees'][0]}, "
         f"le détour, ou les coutures des colonnes {C[1]} et {C[2]} qui la ferment.", ALERTE),
        ("★ la suite : la suite des détours peut-elle se dérouler sans main ?", ENCRE)]


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

    a, ve, t, et = d["lanalyse_du_treillis_de_la_rangee"], d["le_verdict"], d["le_test"], d["letalon_du_test"]
    B, pr = a["les_boucles"], a["lepreuve"]["par_rectangle"]
    R, C = d["le_treillis"]["rangees"], d["le_treillis"]["colonnes"]
    seuil = float(t["le_seuil"])
    L99, Lint, Ld = d["les_lignes_de_la_rangee"], d["les_lignes_de_la_rangee_interieure"], \
        d["les_bandes_declarees"][0]["les_lignes"]
    rc, f229 = d["les_boucles_de_229_recomposees"], d["les_fermetures_de_229"]

    def couleur(n):
        part = float(pr[n]["la_part_du_nul_sous_la_fermeture"])
        if n in t["les_boucles_testees"] and t["elle_sort_du_bruit"]:
            return ALERTE
        return MOYEN if part >= 0.75 else BON

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"le détour : la rangée {d['le_detour']}, lignes {_plage(Ld)}, dont aucune ne vote pour la rangée "
                   f"{R[0]} ({_plage(L99)}) ni pour la rangée {R[2]} ({_plage(Lint)}) · lu des colonnes {C[0]} à {C[2]}, "
                   f"retombé sur les lectures publiées en {d['la_reproduction']['combien_de_coutures_relues']} coutures",
           petit, GRIS)

    # ── PANNEAU 1 · LA MOITIÉ HAUTE DU TREILLIS DE 229, COUPÉE PAR LE DÉTOUR DE LA RANGÉE ──────
    panneau(50, 84, 560, 780, "LE DÉTOUR DE LA RANGÉE · quatre boucles")
    r_min, r_max = min(L99) - 2, max(Lint) + 2
    c_min, c_max = C[0] - 2, C[2] + 2
    x0, x1, y0, y1 = 110, 520, 160, 500

    def X(c):
        return x0 + (x1 - x0) * (float(c) - c_min) / (c_max - c_min)

    def Y(r):
        return y0 + (y1 - y0) * (float(r) - r_min) / (r_max - r_min)
    for lignes, coul in ((L99, VOTE), (Lint, VOTE), (Ld, DETOUR)):
        art.rectangle([x0, Y(min(lignes) - 0.5), x1, Y(max(lignes) + 0.5)], fill=coul)
    boites = {"haut_gauche": (C[0], R[0], C[1], R[1]), "haut_droite": (C[1], R[0], C[2], R[1]),
              "bas_gauche": (C[0], R[1], C[1], R[2]), "bas_droite": (C[1], R[1], C[2], R[2])}
    for n, (ca, ra, cb, rb) in boites.items():
        art.rectangle([X(ca), Y(ra), X(cb), Y(rb)], outline=couleur(n), width=4 if n == "haut_droite" else 2)
        traces[n] = 1
        points.append((X(cb), Y(rb)))
    ecrire(X(C[1]) + 10, (Y(R[0]) + Y(R[1])) / 2 - 7, "la boucle étroite", 0, couleur("haut_droite"))
    for band, seams in (a.get("les_coutures_remplies") or {}).items():
        sens, centre = band.split("_")
        for sc in seams:
            if sens == "colonnes":
                art.rectangle([X(int(centre)) - 6, Y(int(sc)), X(int(centre)) + 6, Y(int(sc)) + 4], fill=CONTRE)
            else:
                art.rectangle([X(int(sc)), Y(int(centre)) - 6, X(int(sc)) + 4, Y(int(centre)) + 6], fill=CONTRE)
    for r in R:
        ecrire(x0 - 50, Y(r) - 7, f"r. {r}", 0, ENCRE)
    for c in C:
        ecrire(X(c) - 16, y0 - 22, f"col. {c}", 0, ENCRE)
    yy = 520
    for n in LES_BOUCLES:
        ecrire(66, yy, LES_NOMS[n], 0, ENCRE)
        ecrire(280, yy, f"L = {_signe(B[n]['la_fermeture_en_voxels'])} vx", 0, couleur(n))
        ecrire(400, yy, f"bruit : {_fr(pr[n]['la_part_du_nul_sous_la_fermeture'], 4)} dessous", 0, GRIS)
        yy += 22
    ecrire(66, 628, f"en beige : les lignes qui votent pour les rangées {R[0]} et {R[2]} à une largeur de 218", 0, GRIS)
    ecrire(66, 648, "en bleu clair : les cinq lignes du détour, qui n'en partagent aucune", 0, GRIS)
    remplies = a.get("les_coutures_remplies") or {}
    if remplies:
        ecrire(66, 668, "en bleu : sans majorité, franchies par le maillage (225) : "
                        + " ; ".join(f"{b_.replace('colonnes_', 'col. ').replace('rangees_', 'r. ')} en "
                                     + " et ".join(str(s_) for s_ in sorted(int(k) for k in v_))
                                     for b_, v_ in sorted(remplies.items())), 0, CONTRE)
    ecrire(66, 740, "vert : sous les trois quarts du bruit · ocre : au-delà · rouge : sortie du bruit", 0, GRIS)

    # ── PANNEAU 2 · LE SEUL TEST ────────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 430, "LE SEUL TEST · la part des tirages indépendants qui ferment moins")
    ax0, ax1 = 870, 1180

    def ax(v):
        return ax0 + (ax1 - ax0) * max(0.0, min(1.0, float(v)))
    art.line([ax(seuil), 124, ax(seuil), 360], fill=ALERTE, width=2)
    ecrire(ax(seuil) - 70, 366, f"seuil {_fr(seuil, 4)}", 0, ALERTE)
    ecrire(ax0 - 4, 366, "0", 0, GRIS)
    ecrire(ax1 - 4, 384, "1", 0, GRIS)
    yy = 150
    for n in LES_BOUCLES:
        part = float(pr[n]["la_part_du_nul_sous_la_fermeture"])
        testee = n in t["les_boucles_testees"]
        coul = (ALERTE if (testee and t["elle_sort_du_bruit"]) else (ENCRE if testee else TRAIT))
        ecrire(596, yy - 7, LES_NOMS[n] + ("" if testee else " (non testée)"), 0, ENCRE if testee else GRIS)
        art.rectangle([ax0, yy - 6, ax1, yy + 6], outline=TRAIT)
        art.rectangle([ax0, yy - 6, ax(part), yy + 6], fill=coul if testee else BANDE)
        points.append((ax(part), yy + 6))
        ecrire(ax1 + 12, yy - 7, f"{_fr(part, 4)}", 0, ENCRE if testee else GRIS)
        yy += 52
    ecrire(596, 396, "une seule boucle testée, la boucle étroite de la rangée, à la garantie entière : 1 − 0,05", 0,
           GRIS)

    # ── PANNEAU 3 · CE QUE LE DÉTOUR FAIT DE 229, ET L'ÉTALON ───────────────────────────────
    panneau(580, 450, 1310, 780, "CE QUE LE DÉTOUR FAIT DES BOUCLES DU HAUT DE 229")
    yy = 494
    ecrire(596, yy, f"la boucle de 229 entre les colonnes {C[1]} et {C[2]}, L = {_signe(f229['haut_droite'])} vx, "
                    f"recomposée à {_signe(rc['haut_droite'])} :", 0, ENCRE)
    ecrire(612, yy + 22, f"la boucle étroite de la rangée {_signe(B['haut_droite']['la_fermeture_en_voxels'])} + sous le "
                         f"détour {_signe(B['bas_droite']['la_fermeture_en_voxels'])}", 0, ENCRE)
    ecrire(612, yy + 44, f"la boucle étroite de la rangée en porte "
                         f"{_fr(d['la_part_de_229_portee_par_la_boucle_etroite'], 4)}", 0, ENCRE)
    ecrire(596, yy + 80, f"la boucle étroite de 229, entre les colonnes {C[0]} et {C[1]}, L = "
                         f"{_signe(f229['haut_gauche'])} vx, recomposée à {_signe(rc['haut_gauche'])} :", 0, ENCRE)
    ecrire(612, yy + 102, f"le témoin {_signe(B['haut_gauche']['la_fermeture_en_voxels'])} + sous le détour "
                          f"{_signe(B['bas_gauche']['la_fermeture_en_voxels'])}", 0, ENCRE)
    ecrire(596, 660, f"étalon : sur des demi-côtés indépendants, au θ dérivé {_fr(et['le_theta'], 4)}, le test "
                     f"désigne {et['combien_designent']} fois sur {et['les_replicats']}", 0, ENCRE)
    ecrire(596, 680, f"soit {_fr(et['le_taux'], 4)}, sous sa borne {_fr(et['la_borne'], 4)} : "
                     f"{'il tient sa garantie' if et['elle_tient_sa_garantie'] else 'il ne la tient pas'}", 0,
           BON if et["elle_tient_sa_garantie"] else ALERTE)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 798, L_, H_], fill=BANDE)
    ecrire(50, 812, f"LE VERDICT : {ve['ce_qui_reste_a_mesurer']}", petit, ENCRE)
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
    tmp = sortie.parent / ".sonde_230.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(s_, t_):
        return {"le_verdict": {"la_boucle_etroite_sort_du_bruit": s_, "letalon_tient": t_}}
    titres = {le_titre(_v(s_, t_)) for s_ in (True, False) for t_ in (True, False)}
    v("★★★★ les trois titres possibles sont distincts, et un étalon qui ne tient pas prime",
      len(titres) == 3 and le_titre(_v(True, False)) == le_titre(_v(False, False)))
    v("★★★ le titre LIT le verdict",
      ("NE SORT PAS" in le_titre(d)) == (not d["le_verdict"]["la_boucle_etroite_sort_du_bruit"]
                                          and d["le_verdict"]["letalon_tient"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ chaque boucle du treillis de la rangée est tracée", all(traces.get(n) for n in LES_BOUCLES))
    txt = " ".join(t for _, _, t, _ in poses)
    a = d["lanalyse_du_treillis_de_la_rangee"]
    v("★★★★ elle porte la fermeture et la part du bruit de chaque boucle",
      all(f"L = {_signe(a['les_boucles'][n]['la_fermeture_en_voxels'])} vx" in txt
          and _fr(a["lepreuve"]["par_rectangle"][n]["la_part_du_nul_sous_la_fermeture"], 4) in txt
          for n in LES_BOUCLES))
    v("★★★★ elle porte le seuil du seul test, et dit que les autres boucles ne sont pas testées",
      f"seuil {_fr(d['le_test']['le_seuil'], 4)}" in txt and "(non testée)" in txt)
    v("★★★★ elle porte les boucles de 229, publiées et recomposées, et la part portée par la boucle étroite",
      all(_signe(d["les_fermetures_de_229"][n]) in txt and _signe(d["les_boucles_de_229_recomposees"][n]) in txt
          for n in ("haut_gauche", "haut_droite"))
      and _fr(d["la_part_de_229_portee_par_la_boucle_etroite"], 4) in txt)
    v("★★★★ elle porte les lignes de la rangée, celles du détour, et le détour",
      _plage(d["les_lignes_de_la_rangee"]) in txt and _plage(d["les_bandes_declarees"][0]["les_lignes"]) in txt
      and f"rangée {d['le_detour']}" in txt)
    et = d["letalon_du_test"]
    v("★★★★ elle porte l'étalon du test", f"{et['combien_designent']} fois sur {et['les_replicats']}" in txt
      and _fr(et["la_borne"], 4) in txt and _fr(et["le_theta"], 4) in txt)
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
                   default=RACINE / "docs" / "mesures" / "un_detour_separe_t_il_lerreur_de_la_rangee_99.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "230_un_detour_separe_t_il_lerreur_de_la_rangee_99.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
