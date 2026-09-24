"""La spire que la chaîne produit, rendue comme le segment l'est : ce que sa pile montre, et ce que la marche y lit.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, LA PILE COUPÉE EN TRAVERS à la même rangée du bloc : la publiée,
le segment réduit à la maille de la chaîne, et la spire produite. Une feuille qui suit la surface est une bande claire au
milieu de la coupe ; là où la spire produite s'en écarte, la bande s'éloigne du milieu. En bas à gauche, les cartes du bloc :
l'erreur que le juge donne au transfert, et la marche lue sur chaque pile, à la même échelle. En bas à droite, l'accord
des paires, avec le témoin plat.

  uv run python src/figures/figure_la_spire_produite_se_lit_elle_dans_le_treillis.py \\
      --sortie docs/images/257_la_spire_produite_se_lit_elle_dans_le_treillis.png
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
LA_MESURE = RACINE / "docs" / "mesures" / "la_spire_produite_se_lit_elle_dans_le_treillis.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
VIDE = (228, 226, 220)
L_, H_ = 1360, 1200
LES_PILES = (("la publiée", "la_publiee"), ("le segment réduit à la maille", "le_segment_reduit"),
             ("la spire produite", "la_spire_produite"))
LA_PORTEE = 108.0   # voxels : l'échelle commune des cartes, un pas et demi de part et d'autre


def _fr(x, n: int = 3) -> str:
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",").replace("-", "−")


def lire() -> dict:
    d = json.loads(LA_MESURE.read_text())
    if not d.get("decidable"):
        raise SystemExit("mesure indécidable")
    return d


def la_couleur(v) -> tuple[int, int, int]:
    """Une profondeur signée : bleu d'un côté, ocre de l'autre, blanc à zéro ; gris hors de la carte."""
    if v is None:
        return VIDE
    t = max(-1.0, min(1.0, float(v) / LA_PORTEE))
    loin = CONTRE if t < 0 else ALERTE
    a = abs(t)
    return tuple(int(round(255 * (1 - a) + c * a)) for c in loin)


def les_parts(d: dict, nom: str) -> tuple:
    a = d["les_piles"][nom]["laccord_des_paires"] if nom != "temoin" else d["le_temoin_plat"]
    return (a.get("la_part_que_la_marche_separe_parmi_celles_que_le_juge_separe"),
            a.get("la_part_que_la_marche_reunit_parmi_celles_que_le_juge_reunit"))


def le_titre(d: dict) -> str:
    """Le titre LIT la mesure : d'abord le contrôle positif, parce qu'il décide de ce que la suite veut dire."""
    z = d.get("ce_que_la_marche_retrouve_de_la_rampe") or {}
    if z.get("decidable") and z["la_pente"] < 0.5:
        return (f"LA MARCHE DES COUTURES NE RETROUVE QUE {_fr(z['lecart_retrouve_voxels'], 1)} DES "
                f"{_fr(z['lecart_pose_voxels'], 1)} VOXELS D'UNE RAMPE POSÉE : UNE DÉRIVE LENTE LUI ÉCHAPPE")
    sep, reu = les_parts(d, "la_spire_produite")
    if sep is not None and reu is not None and sep > 0.5 and sep + reu > 1.0:
        return (f"SUR LA SPIRE PRODUITE, LA MARCHE DU TREILLIS SÉPARE {_fr(sep, 4)} DES PAIRES QUE LE JUGE SÉPARE, ET EN "
                f"RÉUNIT {_fr(reu, 4)}")
    return (f"SUR LA SPIRE PRODUITE, LA MARCHE DU TREILLIS NE SÉPARE QUE {_fr(sep, 4)} DES PAIRES QUE LE JUGE SÉPARE")


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(18, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    points: list[tuple[float, float]] = []
    traces: dict[str, object] = {"coupes": 0, "cartes": 0, "cellules": {}}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def panneau(x0, y0, x1, y1, titre):
        art.rectangle([x0, y0, x1, y1], outline=TRAIT)
        cadres.append((x0, y0, x1, y1))
        ecrire(x0 + 14, y0 + 10, titre, moyen, ENCRE)

    b = d["le_bloc"]
    c = d["le_controle"]
    ecrire(50, 24, le_titre(d), gros, ENCRE)
    ecrire(50, 52, f"{d['le_segment']} · bloc de {b['le_cote']} × {b['le_cote']} chunks à la rangée {b['la_rangee']}, "
                   f"colonne {b['la_colonne']} · {d['la_prediction']}, côté plus · le rendu égale la pile publiée en "
                   f"{_fr(c['la_part_des_voxels_egaux'], 4)} des voxels, à un niveau près en {_fr(c['la_part_a_un_niveau_pres'], 4)}",
           petit, GRIS)

    # ── PANNEAU 1 · LES COUPES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 80, 1310, 612, f"LA PILE COUPÉE EN TRAVERS, À LA RANGÉE {d['les_coupes']['la_rangee_du_bloc']} DU BLOC : "
                               f"COUCHE CONTRE COLONNE (LE MILIEU, EN OCRE, EST LA SURFACE)")
    y = 112
    for nom, cle in LES_PILES + (("la rampe posée", "la_rampe_posee"),):
        coupe = d["les_coupes"].get(cle)
        ecrire(66, y + 44, nom, 0, ENCRE)
        f = (d.get("la_feuille_dans_la_pile") or {}).get(cle)
        if f:
            ecrire(66, y + 62, f"feuille à {_fr(f['lecart_median_voxels'], 1)} vx du milieu", 0, GRIS)
        if coupe:
            h, w = len(coupe), len(coupe[0])
            im = Image.new("L", (w, h))
            im.putdata([int(v) for r in coupe for v in r])
            im = im.resize((w * 4, h), Image.NEAREST)
            img.paste(im.convert("RGB"), (250, y))
            art.line([246, y + h // 2, 254 + w * 4, y + h // 2], fill=ALERTE, width=1)
            points.append((254 + w * 4, y + h))
            traces["coupes"] += 1
        y += 124

    # ── PANNEAU 2 · LES CARTES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 626, 1310, 872, "L'ERREUR JUGÉE, LA RAMPE POSÉE, ET LA MARCHE LUE SUR CHAQUE PILE, CHUNK PAR CHUNK")
    cell = 9
    cartes = (("l'erreur du juge", "lerreur"), ("marche, publiée", "la_publiee"), ("marche, segment réduit", "le_segment_reduit"),
              ("marche, spire produite", "la_spire_produite"), ("la rampe posée", "la_rampe"),
              ("marche, rampe posée", "la_rampe_posee"))
    for k, (nom, cle) in enumerate(cartes):
        x0, y0 = 66 + k * 205, 682
        ecrire(x0, 660, nom, 0, ENCRE)
        grille = d["les_cartes"][cle]
        n_cell = 0
        for i, r in enumerate(grille):
            for j, v in enumerate(r):
                art.rectangle([x0 + j * cell, y0 + i * cell, x0 + (j + 1) * cell - 1, y0 + (i + 1) * cell - 1],
                              fill=la_couleur(v))
                n_cell += 1
        points.append((x0 + len(grille[0]) * cell, y0 + len(grille) * cell))
        traces["cellules"][cle] = n_cell
        traces["cartes"] += 1
    ecrire(66, 834, f"bleu et ocre : ±{_fr(LA_PORTEE, 0)} voxels, un pas et demi ; blanc : zéro ; gris : non noté ou non "
                    f"relié. L'erreur et la rampe sont absolues ; une marche l'est à une constante près.", 0, GRIS)
    ecrire(66, 852, f"coutures lues : publiée {d['les_piles']['la_publiee']['la_marche']['les_coutures']}, réduite "
                    f"{d['les_piles']['le_segment_reduit']['la_marche']['les_coutures']}, produite "
                    f"{d['les_piles']['la_spire_produite']['la_marche']['les_coutures']}, rampe "
                    f"{d['les_piles']['la_rampe_posee']['la_marche']['les_coutures']}", 0, GRIS)

    # ── PANNEAU 3 · LES PAIRES ─────────────────────────────────────────────────────────────────────────────────────
    panneau(50, 886, 1310, 1090, "L'ACCORD DES PAIRES : LA MARCHE SÉPARE-T-ELLE CE QUE LE JUGE, OU LA RAMPE, SÉPARE ?")
    lignes = (("le témoin plat", "temoin"),) + LES_PILES + (("la rampe posée, contre elle-même", "la_rampe_posee"),)
    barres = 0
    for k, (nom, cle) in enumerate(lignes):
        col, rang = k % 3, k // 3
        x0, y = 66 + col * 415, 918 + rang * 84
        sep, reu = les_parts(d, cle)
        ecrire(x0, y, nom, 0, ENCRE)
        bx0, bx1 = x0 + 70, x0 + 320
        for m, (lib, val, coul) in enumerate((("sépare", sep, ALERTE), ("réunit", reu, BON))):
            yy = y + 18 + m * 18
            ecrire(x0 + 10, yy, lib, 0, GRIS)
            if val is not None:
                art.rectangle([bx0, yy + 2, bx0 + (bx1 - bx0) * float(val), yy + 12], fill=coul)
                points.append((bx0 + (bx1 - bx0) * float(val), yy + 12))
                barres += 1
            ecrire(bx1 + 8, yy, _fr(val, 4), 0, ENCRE)
    traces["barres"] = barres
    z = d["ce_que_la_marche_retrouve_de_la_rampe"]
    ecrire(896, 1004, f"ce que la marche retrouve de la rampe :", 0, ENCRE)
    ecrire(896, 1022, f"une pente de {_fr(z['la_pente'], 4)}, soit {_fr(z['lecart_retrouve_voxels'], 2)} voxels "
                      f"sur {_fr(z['lecart_pose_voxels'], 2)}", 0, ALERTE)
    ecrire(896, 1040, "un pas lu sur 16 colonnes de part et d'autre d'une couture", 0, GRIS)
    ecrire(896, 1058, "ne voit que ce qui saute à la couture", 0, GRIS)

    # ── BANDE ──────────────────────────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 1104, L_, H_], fill=BANDE)
    ecrire(50, 1116, f"LE VERDICT : {d['le_verdict']['lissue']}", petit, ENCRE)
    ecrire(50, 1138, "★ la spire produite a désormais un volume de surface ; mais la marche des coutures n'en jugera pas une "
                     "dérive lente.", moyen, ENCRE)
    ecrire(50, 1162, "⚠ ce qui n'est PAS établi : un seul bloc, où le segment lui-même est hors de sa feuille ; la rampe est "
                     "posée après la première mesure.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, traces


def verifier(sortie: Path) -> int:
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

    d = lire()
    tmp = sortie.parent / ".sonde_257.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)
    v("★★★ le titre LIT la mesure, contrôle positif d'abord",
      ("RAMPE POSÉE" in le_titre(d)) == (d["ce_que_la_marche_retrouve_de_la_rampe"]["la_pente"] < 0.5))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    v("★★★★ les quatre piles ont leur coupe", traces["coupes"] == 4)
    cote = d["le_bloc"]["le_cote"]
    v("★★★★ chaque carte a une cellule par chunk du bloc",
      traces["cartes"] == 6 and all(n == cote * cote for n in traces["cellules"].values()), str(traces["cellules"]))
    v("★★★★ chaque part a sa barre : le témoin, trois piles et la rampe, séparer et réunir", traces["barres"] == 10)
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte le témoin et ce qui n'est PAS établi", "témoin plat" in txt and "n'est PAS établi" in txt)
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
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "257_la_spire_produite_se_lit_elle_dans_le_treillis.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.sortie)
    chemin, *_ = dessiner(lire(), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
