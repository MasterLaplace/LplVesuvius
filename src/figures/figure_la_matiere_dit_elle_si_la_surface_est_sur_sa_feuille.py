"""La place d'une surface dans le profil de la matière : l'étalonnage au pas du prix, et la première surface de PHerc0358.

⚠⚠ **Ce que cette figure doit rendre évident.** Qu'au pas du prix, sur PHercParis4, le tracé humain et les sauts de la chaîne
sont notés loin au-dessus du hasard, ses trois défauts plantés non ; que le profil moyen montre le pas des feuilles ; ce que la
note voit, ou ne voit pas, d'une spire ratée ; et, sur PHerc0358, où la première surface est posée sur une feuille, pièce par
pièce, avec ses auto-intersections.

  uv run python src/figures/figure_la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.py \\
      --sortie docs/images/298_la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.png

⚠ Tout vient de la mesure : les barres, les profils et la carte des pièces.
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
BLEU = (58, 92, 150)
AMBRE = (206, 160, 60)
VIOLET = (120, 84, 150)
L_, H_ = 1360, 960
LE_BAS, LE_HAUT = 0.40, 0.62
LES_SURFACES = (("le_segment", "tracé humain", BON), ("saut_1", "saut 1", BLEU), ("saut_2", "saut 2", BLEU),
                ("saut_3", "saut 3", BLEU), ("saut_4", "saut 4", BLEU),
                ("decale_dun_demi_pas", "décalé ½ pas", ALERTE), ("rampe_douce", "rampe 14°", VIOLET),
                ("rampe_raide", "rampe 45°", VIOLET))
LES_PROFILS = (("le_segment", "tracé humain", BON), ("saut_1", "saut 1", BLEU),
               ("decale_dun_demi_pas", "décalé d'un demi-pas", ALERTE), ("rampe_douce", "rampe 14°", VIOLET),
               ("rampe_raide", "rampe 45°", AMBRE))
LES_PIECES = {"posée sur une feuille": BON, "en travers": AMBRE, "entre les feuilles": ALERTE, "non jugée": TRAIT}
LES_DEFAUTS_0358 = (("la_surface_de_24", "la surface de 24", BLEU), ("decale_dun_demi_pas", "décalée ½ pas", ALERTE),
                    ("rampe_douce", "rampe 14°", VIOLET), ("rampe_raide", "rampe 45°", VIOLET))


def _fr(x, n: int = 2) -> str:
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def _milliers(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    e = d["letalonnage"]["reunis"]
    if v.get("separe") is False:
        return (f"NON : AU PAS DU PRIX, LA PLACE DANS LE PROFIL NE SÉPARE PAS UNE FEUILLE D'UNE TRAVERSÉE "
                f"(TRACÉ {_fr(e['le_segment'])}, RAMPES {_fr(e['rampe_douce'])} ET {_fr(e['rampe_raide'])})")
    if not v.get("decidable"):
        return f"INDÉCIDABLE : {v['lissue']}".upper()
    return (f"LA PREMIÈRE SURFACE DE PHerc0358 EST POSÉE SUR UNE FEUILLE SUR {_fr(v['la_part_posee'])} DE SES POINTS, "
            f"PAR UN JUGE QUI SÉPARE AU PAS DU PRIX ({_fr(e['le_segment'])} CONTRE {_fr(e['rampe_raide'])} À 45°)")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces = {"barres": [], "profils": [], "pieces": [], "barres_0358": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    e = d["letalonnage"]
    tau = e["le_verdict"]["le_seuil"]
    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, f"le rang du scan au point parmi son profil le long de la normale, ±{_fr(d['les_constantes']['la_fenetre_um'], 0)}"
                   f" µm · 1/2 au hasard exactement · PHercParis4 au niveau 2 (9,6 µm), PHerc0358 au niveau 0 (9,362 µm) · "
                   f"τ = {_fr(tau, 3)}", petit, GRIS)

    panneau(50, 74, 700, 420, "L'ÉTALONNAGE, PHercParis4, SIX BLOCS DE 296")
    base, haut = 360, 220
    y_de = lambda val: base - (val - LE_BAS) / (LE_HAUT - LE_BAS) * haut  # noqa: E731
    art.line([90, base, 680, base], fill=GRIS)
    ecrire(58, base - 6, _fr(LE_BAS), 0, GRIS)
    ecrire(58, int(y_de(LE_HAUT)) - 6, _fr(LE_HAUT), 0, GRIS)
    y = y_de(0.5)
    art.line([90, y, 680, y], fill=GRIS)
    ecrire(58, int(y) - 6, "½", 0, GRIS)
    if tau is not None:
        art.line([90, y_de(tau), 680, y_de(tau)], fill=ENCRE)
        ecrire(640, int(y_de(tau)) - 16, f"τ {_fr(tau, 3)}", 0, ENCRE)
    for k, (cle, nom, coul) in enumerate(LES_SURFACES):
        val = e["reunis"].get(cle)
        x = 100 + k * 68
        if val is not None:
            art.rectangle([x, y_de(val), x + 44, base], fill=coul)
            points.append((x + 44, y_de(val)))
            ecrire(x + 4, int(y_de(max(val, max(b.get(cle) or 0 for b in e["les_blocs"])))) - 18, _fr(val), 0, ENCRE)
        for b in e["les_blocs"]:
            bv = b.get(cle)
            if bv is not None:
                art.ellipse([x + 20, y_de(bv) - 2, x + 24, y_de(bv) + 2], fill=ENCRE)
                points.append((x + 24, y_de(bv)))
        traces["barres"].append((cle, val))
        ecrire(x, base + 8 + 14 * (k % 2), nom, 0, ENCRE)
    ecrire(70, 100, "barre : les six blocs réunis · point : un bloc · ½ : le hasard exact", 0, GRIS)
    ecrire(70, 116, f"le juge {'SÉPARE' if e['le_verdict']['separe'] else 'NE SÉPARE PAS'} au pas du prix", 0,
           BON if e["le_verdict"]["separe"] else ALERTE)

    panneau(720, 74, 1310, 420, "LE PROFIL MOYEN, NORMÉ, LE LONG DE LA NORMALE (PHercParis4)")
    x0, x1, y0, y1 = 760, 1290, 150, 380
    ym = (y0 + y1) / 2
    art.line([x0, ym, x1, ym], fill=TRAIT)
    art.line([(x0 + x1) / 2, y0, (x0 + x1) / 2, y1], fill=TRAIT)
    ecrire(x0, y1 + 6, f"−{_fr(d['les_constantes']['la_fenetre_um'], 0)} µm", 0, GRIS)
    ecrire(x1 - 50, y1 + 6, f"+{_fr(d['les_constantes']['la_fenetre_um'], 0)} µm", 0, GRIS)
    ecrire(int((x0 + x1) / 2) - 30, y1 + 6, "la surface", 0, GRIS)
    for k, (cle, nom, coul) in enumerate(LES_PROFILS):
        p = e["les_details"][cle]["le_profil_moyen"]
        traces["profils"].append((cle, len(p)))
        if len(p) > 1:
            xy = [(x0 + i * (x1 - x0) / (len(p) - 1), ym - max(-0.5, min(0.5, v)) * (y1 - y0)) for i, v in enumerate(p)]
            art.line(xy, fill=coul, width=2)
            points.extend(xy)
        ecrire(740 + (k % 3) * 190, 100 + (k // 3) * 14, f"— {nom}", 0, coul)
    seg = e["les_details"]["le_segment"]["le_profil_moyen"]
    if seg:
        T = len(seg) // 2
        pic, creux = max(range(T, len(seg)), key=lambda i: seg[i]) - T, min(range(0, T + 1), key=lambda i: seg[i]) - T
        um = d["les_constantes"]["les_volumes"]["PHercParis4"]["le_voxel_um"]
        ecrire(740, 132, f"le tracé suit sa feuille, posé sur sa face : la densité culmine à {_fr(pic * um, 0)} µm, "
                         f"le creux à {_fr(creux * um, 0)} µm", 0, BON)

    panneau(50, 436, 700, 620, "CE QUE LA NOTE VOIT D'UNE SPIRE RATÉE (JUGE DE 248)")
    base, haut = 580, 100
    y_de2 = lambda val: base - (val - LE_BAS) / (LE_HAUT - LE_BAS) * haut  # noqa: E731
    k = 0
    for h in ("saut_1", "saut_2", "saut_3", "saut_4"):
        s = e["sous_le_juge_de_248"][h]
        ecrire(90 + k * 76, 462, h.replace("_", " "), 0, ENCRE)
        for cle, nom, coul in (("juste", "juste", BON), ("rate", "raté", ALERTE)):
            val, n = s[cle]["la_note"], s[cle]["les_points"]
            x = 90 + k * 76
            if val is not None:
                art.rectangle([x, y_de2(val), x + 50, base], fill=coul)
                points.append((x + 50, y_de2(val)))
                ecrire(x + 4, int(y_de2(val)) - 16, _fr(val), 0, ENCRE)
            ecrire(x, base + 4, nom, 0, ENCRE)
            ecrire(x, base + 18, _milliers(n), 0, GRIS)
            traces["barres"].append((f"{h}/{cle}", val))
            k += 1
    y = y_de2(0.5)
    art.line([80, y, 690, y], fill=GRIS)

    r = d["le_rouleau"]
    panneau(720, 436, 1310, 770, "PHerc0358 : LA PREMIÈRE SURFACE, PIÈCE PAR PIÈCE (16 × 16 MAILLES)")
    g = d["le_plan"]["PHerc0358"]["la_grille"]
    cote = 16
    n_i, n_j = (g[0] + cote - 1) // cote, (g[1] + cote - 1) // cote
    case = min(250 // n_i, 250 // n_j)
    ox, oy = 750, 480
    for i in range(n_i):
        for j in range(n_j):
            art.rectangle([ox + j * case, oy + i * case, ox + (j + 1) * case - 1, oy + (i + 1) * case - 1], fill=FOND,
                          outline=TRAIT)
    touchees = r["les_croisements_de_24"].get("par_piece", {}) if r["les_croisements_de_24"].get("lisible") else {}
    for p in r["les_pieces"]:
        i, j = p["la_piece_en_mailles"][0] // cote, p["la_piece_en_mailles"][1] // cote
        art.rectangle([ox + j * case, oy + i * case, ox + (j + 1) * case - 1, oy + (i + 1) * case - 1],
                      fill=LES_PIECES[p["la_piece"]])
        traces["pieces"].append((tuple(p["la_piece_en_mailles"]), p["la_piece"]))
        if f"{p['la_piece_en_mailles'][0]}_{p['la_piece_en_mailles'][1]}" in touchees:
            cx, cy = ox + j * case + case / 2, oy + i * case + case / 2
            art.line([cx - 5, cy - 5, cx + 5, cy + 5], fill=ENCRE, width=2)
            art.line([cx - 5, cy + 5, cx + 5, cy - 5], fill=ENCRE, width=2)
    points.append((ox + n_j * case, oy + n_i * case))
    for k, (nom, coul) in enumerate(LES_PIECES.items()):
        ecrire(1020, 470 + k * 16, f"■ {nom}", 0, coul)
    ecrire(1020, 470 + 4 * 16, "× auto-intersection de 24", 0, ENCRE)
    ecrire(750, 736, "non jugée : moins de 100 points", 0, GRIS)
    ecrire(750, 750, "qui voient de la matière", 0, GRIS)
    x0, x1, y0, y1 = 1020, 1290, 570, 660
    ym = (y0 + y1) / 2
    art.line([x0, ym, x1, ym], fill=TRAIT)
    for cle, nom, coul in LES_DEFAUTS_0358[:1]:
        p = r["les_details"][cle]["le_profil_moyen"]
        if len(p) > 1:
            xy = [(x0 + i * (x1 - x0) / (len(p) - 1), ym - max(-0.5, min(0.5, v)) * (y1 - y0)) for i, v in enumerate(p)]
            art.line(xy, fill=coul, width=2)
            points.extend(xy)
    ecrire(1020, 554, "son profil moyen, à la même échelle", 0, BLEU)
    base, haut = 740, 50
    y_de3 = lambda val: base - (val - LE_BAS) / (LE_HAUT - LE_BAS) * haut  # noqa: E731
    for k, (cle, nom, coul) in enumerate(LES_DEFAUTS_0358):
        val = r["reunis"].get(cle)
        x = 1020 + k * 70
        if val is not None:
            art.rectangle([x, y_de3(val), x + 46, base], fill=coul)
            points.append((x + 46, y_de3(val)))
            ecrire(x + 2, int(y_de3(val)) - 15, _fr(val), 0, ENCRE)
        traces["barres_0358"].append((cle, val))
    ecrire(1020, base + 4, "surface · décalée · rampes", 0, ENCRE)

    panneau(50, 636, 700, 770, "LES POINTS")
    d24 = r["les_details"]["la_surface_de_24"]
    txt = [f"PHercParis4 : {_milliers(e['les_details']['le_segment']['les_points_juges'])} points jugés par surface ; "
           f"{_milliers(sum(e['les_details'][c]['sans_matiere'] for c, _, _ in LES_SURFACES))} profils sans matière",
           f"PHerc0358 : {_milliers(d24['les_points_juges'])} points jugés ; {_milliers(d24['sans_matiere'])} sans matière "
           f"(dans le vide masqué du scan), {_milliers(d24['hors_du_volume'])} hors du volume",
           "le juge ne lit que le scan brut, jamais la prédiction m7 sur laquelle le traceur a poussé la surface"]
    for k, t in enumerate(txt):
        ecrire(70, 666 + k * 20, t, 0, ENCRE)

    art.rectangle([0, 790, L_, H_], fill=BANDE)
    ecrire(50, 802, f"LE VERDICT DÉCLARÉ : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 824, "une note de 1/2 est celle d'une surface dont la place par rapport aux feuilles est au hasard, ce qui "
                    "est le cas d'une surface qui traverse l'empilement", moyen, ENCRE)
    ecrire(50, 850, "⚠ ce qui n'est PAS établi : sur quelle feuille la surface est posée (une surface qui passe d'une feuille "
                    "à la voisine sans se croiser", moyen, ALERTE)
    ecrire(50, 872, "est posée sur une feuille partout) ; qu'elle soit le recto ; qu'elle se déroule ; ce que vaut ce juge "
                    "sur un autre rouleau.", moyen, ALERTE)
    ecrire(50, 904, "rapporté, qui ne décide rien : le profil moyen du tracé et des sauts se cale sur le pas des feuilles, ceux "
                    "des rampes et de PHerc0358 restent plats ;", moyen, ENCRE)
    ecrire(50, 926, "c'est l'alignement des profils, et non la place du point, qui distingue ici une surface qui suit sa "
                    "feuille : un juge à déclarer avant d'être mesuré.", moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path, mesure: Path = LA_MESURE) -> int:
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

    d = lire(mesure)
    tmp = sortie.parent / ".sonde_298.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "separe": False, "lissue": "x"}
    autre["letalonnage"]["reunis"].update(le_segment=0.61, rampe_douce=0.58, rampe_raide=0.57)
    v("★★★ le titre LIT la mesure", "TRACÉ 0,61, RAMPES 0,58 ET 0,57" in le_titre(autre), le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    e = d["letalonnage"]
    attendu = [(c, e["reunis"].get(c)) for c, _, _ in LES_SURFACES]
    attendu += [(f"{h}/{c}", e["sous_le_juge_de_248"][h][c]["la_note"])
                for h in ("saut_1", "saut_2", "saut_3", "saut_4") for c in ("juste", "rate")]
    v("★★★★ une barre par surface et par classe du juge de 248, chacune à la valeur mesurée", traces["barres"] == attendu)
    v("★★★★ une case par pièce jugée, à son verdict mesuré",
      traces["pieces"] == [(tuple(p["la_piece_en_mailles"]), p["la_piece"]) for p in d["le_rouleau"]["les_pieces"]])
    v("★★★ les barres de PHerc0358 sont celles de la mesure",
      traces["barres_0358"] == [(c, d["le_rouleau"]["reunis"].get(c)) for c, _, _ in LES_DEFAUTS_0358])
    v("★★★ chaque profil tracé a la longueur de la fenêtre",
      all(n in (0, 2 * round(d["les_constantes"]["la_fenetre_um"] / 9.6) + 1) for _, n in traces["profils"]))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte ce qui n'est PAS établi", "n'est PAS établi" in txt)
    octets = tmp.read_bytes()
    dessiner(d, tmp)
    v("★★★★ le rendu est reproductible bit pour bit", tmp.read_bytes() == octets)
    tmp.unlink(missing_ok=True)

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", type=Path, default=RACINE / "docs" / "images"
                   / "298_la_matiere_dit_elle_si_la_surface_est_sur_sa_feuille.png")
    p.add_argument("--mesure", type=Path, default=LA_MESURE)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie, a.mesure)
    chemin, *_ = dessiner(lire(a.mesure), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
