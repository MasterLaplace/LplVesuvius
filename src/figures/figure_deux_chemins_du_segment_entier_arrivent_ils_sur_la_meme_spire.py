"""Deux chemins du segment entier : le rectangle dérivé des bords, ce qui s'y lit, et les trous qui le laissent ouvert.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, LE RECTANGLE SUR LA GRILLE : ses quatre côtés,
couture par couture, là où neuf lignes votent, là où un trou se franchit et là où un trou dépasse ce que
`225` a franchi — c'est le panneau qui conclut. En haut à droite, CE QUI MANQUE : les chunks de chaque
bande, lus, absents du dépôt ou trop peu texturés. En bas à droite, LES TROUS À NEUF LIGNES, côté par côté.

  uv run python src/figures/figure_deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.py \\
      --json docs/mesures/deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.json \\
      --sortie docs/images/232_deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.png
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
CE_QUE_224_A_RENDU = RACINE / "docs" / "mesures" / "deux_chemins_arrivent_ils_sur_la_meme_spire.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
CONTRE = (92, 108, 150)
FRANCHI = (214, 170, 80)
ABSENT = (206, 203, 196)
L_, H_ = 1360, 1000
LES_COTES = (("haut", "la rangée du haut"), ("droite", "la colonne de droite"), ("bas", "la rangée du bas"),
             ("gauche", "la colonne de gauche"))


def _fr(x, n: int = 3) -> str:
    """Un nombre en français. ⚠⚠ Le `rstrip` n'agit qu'en présence d'une virgule — défaut de `177`."""
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.py`, et la grille de `224`."""
    d = json.loads(chemin.read_text())
    if not d.get("decidable"):
        raise SystemExit(f"mesure indécidable : {d.get('raison')}")
    for cle in ("par_largeur", "le_rectangle", "le_verdict", "la_reproduction", "les_bandes", "les_bandes_declarees",
                "le_plus_long_trou_franchi_par_225"):
        if d.get(cle) is None:
            raise SystemExit(f"{cle} manque")
    d["la_grille"] = json.loads(CE_QUE_224_A_RENDU.read_text())["la_grille"]
    return d


def le_titre(d: dict) -> str:
    """Le titre LIT le verdict au lieu de le recalculer."""
    v = d["le_verdict"]
    if v["le_segment_entier_reste_ouvert"]:
        return "LE RECTANGLE DU SEGMENT ENTIER RESTE OUVERT : DEUX DE SES CÔTÉS SORTENT DE CE QUE LE DÉPÔT PORTE"
    if not v["le_segment_entier_se_ferme"]:
        return "À NEUF LIGNES, LES DEUX CHEMINS DU SEGMENT ENTIER ARRIVENT À UN DEMI-FEUILLET L'UN DE L'AUTRE"
    return "À NEUF LIGNES, LES DEUX CHEMINS DU SEGMENT ENTIER ARRIVENT SUR LA MÊME SPIRE"


def les_comptes(d: dict) -> dict:
    """Par bande, sommés sur ses lignes : les chunks demandés, lus, absents du dépôt, trop peu texturés."""
    out = {}
    for b in d["les_bandes_declarees"]:
        lec = d["les_bandes"][b["cle"]]["les_lectures"]
        dem = [int(v.get("colonnes_demandees", v.get("rangees_demandees"))) for v in lec.values()]
        lus = [int(v.get("colonnes_lues", v.get("rangees_lues"))) for v in lec.values()]
        ab = [int(v["refuses"].get("absent du dépôt", 0)) for v in lec.values()]
        tx = [int(v["refuses"].get("trop peu texturé", 0)) for v in lec.values()]
        out[b["cle"]] = {"demandes": sum(dem), "lus": sum(lus), "absents": sum(ab), "texture": sum(tx),
                         "absents_min": min(ab), "absents_max": max(ab), "lignes": len(lec)}
    return out


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

    gy, gx = [int(x) for x in d["la_grille"]]
    r0, r1, c0, c1 = [int(x) for x in d["le_rectangle"]["les_coins"]]
    er, ec = d["le_rectangle"]["letendue_en_rangees"], d["le_rectangle"]["letendue_en_colonnes"]
    plus_long = int(d["le_plus_long_trou_franchi_par_225"])
    k1 = str(d["le_verdict"]["la_largeur_jugee"])
    trous = d["par_largeur"][k1]["les_trous"]
    rp = d["la_reproduction"]

    ecrire(50, 26, le_titre(d), gros, ENCRE)
    ecrire(50, 54, f"quatre bandes de neuf lignes lues pour cette tranche, retombées sur 219 et 223 en "
                   f"{rp['combien_de_coutures_relues']} coutures à l'écart {_fr(rp['lecart_le_plus_grand'])} · le rectangle "
                   f"est dérivé des bords de la croix centrale que 225 publie : rangées {r0} et {r1}, colonnes {c0} et {c1}",
           petit, GRIS)

    # ── PANNEAU 1 · LE RECTANGLE SUR LA GRILLE ──────────────────────────────────────────────
    panneau(50, 84, 560, 800, "LE RECTANGLE SUR LA GRILLE DE CHUNKS")
    s = 1.45
    X0, Y0 = 90, 130

    def X(c):
        return X0 + s * float(c)

    def Y(r):
        return Y0 + s * float(r)
    art.rectangle([X(0), Y(0), X(gx), Y(gy)], outline=TRAIT, fill=(244, 243, 239))
    art.rectangle([X(ec[0]), Y(er[0]), X(ec[1] + 1), Y(er[1] + 1)], outline=GRIS)
    for c in (140, 145):
        art.line([X(c), Y(0), X(c), Y(gy)], fill=CONTRE, width=1)
    for r in (196, 201):
        art.line([X(0), Y(r), X(gx), Y(r)], fill=CONTRE, width=1)
    art.rectangle([X(71), Y(99), X(213), Y(297)], outline=GRIS)
    ecrire(X(71) + 4, Y(99) + 4, "224 · la moitié du segment", 0, GRIS)
    ecrire(X(146) + 2, Y(300), "223", 0, CONTRE)
    ecrire(X(2), Y(202), "219", 0, CONTRE)
    ecrire(X(ec[0]), Y(gy) + 6, f"en gris : l'étendue de la croix, rangées {er[0]} à {er[1]}, colonnes {ec[0]} à {ec[1]}",
           0, GRIS)

    def la_couleur(cote, seam):
        for t in trous:
            if t["le_cote"] == cote and t["le_debut"] <= seam < t["le_debut"] + t["la_longueur"]:
                return ALERTE if t["la_longueur"] > plus_long else FRANCHI
        return BON
    for cote, sens, centre, de, a in (("haut", "r", r0, c0, c1), ("bas", "r", r1, c0, c1),
                                      ("gauche", "c", c0, r0, r1), ("droite", "c", c1, r0, r1)):
        for seam in range(de, a):
            coul = la_couleur(cote, seam)
            if sens == "r":
                art.rectangle([X(seam), Y(centre - 4), X(seam + 1), Y(centre + 5)], fill=coul)
                points.append((X(seam + 1), Y(centre + 5)))
            else:
                art.rectangle([X(centre - 4), Y(seam), X(centre + 5), Y(seam + 1)], fill=coul)
                points.append((X(centre + 5), Y(seam + 1)))
        traces[cote] = a - de
    ecrire(X(c0) + 14, Y(r0) + 12, f"rangée {r0}", 0, ENCRE)
    ecrire(X(c0) + 14, Y(r1) - 22, f"rangée {r1}", 0, ENCRE)
    ecrire(X(c0) + 14, Y((r0 + r1) / 2) + 40, f"colonne {c0}", 0, ENCRE)
    ecrire(X(c1) - 76, Y((r0 + r1) / 2) + 40, f"colonne {c1}", 0, ENCRE)
    ly = Y(gy) + 28
    for i, (coul, lab) in enumerate(((BON, "neuf lignes votent : le consensus existe"),
                                    (FRANCHI, f"un trou de {plus_long} coutures au plus : 225 l'a franchi"),
                                    (ALERTE, f"un trou de plus de {plus_long} coutures : aucune règle éprouvée"))):
        art.rectangle([70, ly + 20 * i + 3, 84, ly + 20 * i + 13], fill=coul)
        ecrire(92, ly + 20 * i, lab, 0, coul if coul != FRANCHI else ENCRE)

    # ── PANNEAU 2 · CE QUI MANQUE ───────────────────────────────────────────────────────────
    panneau(580, 84, 1310, 470, "CE QUI MANQUE · les chunks des neuf lignes de chaque bande")
    comptes = les_comptes(d)
    yy = 132
    for b in d["les_bandes_declarees"]:
        k = comptes[b["cle"]]
        lib = f"la rangée {b['le_centre']}" if b["le_sens"] == "rangees" else f"la colonne {b['le_centre']}"
        ecrire(596, yy, f"{lib} · lignes {min(b['les_lignes'])} à {max(b['les_lignes'])} · {k['demandes']} chunks demandés",
               0, ENCRE)
        x_, w = 596, 560
        for cle, coul in (("lus", BON), ("absents", ABSENT), ("texture", ALERTE)):
            ww = w * k[cle] / k["demandes"]
            art.rectangle([x_, yy + 20, x_ + ww, yy + 34], fill=coul)
            x_ += ww
        points.append((x_, yy + 34))
        ecrire(596, yy + 40, f"lus {k['lus']} · absents du dépôt {k['absents']} (de {k['absents_min']} à "
                             f"{k['absents_max']} par ligne) · trop peu texturés {k['texture']}", 0, GRIS)
        traces[f"compte:{b['cle']}"] = 1
        yy += 80
    ecrire(596, 446, "vert : lus · gris : absents du dépôt · brun : trop peu texturés", 0, GRIS)

    # ── PANNEAU 3 · LES TROUS À NEUF LIGNES ─────────────────────────────────────────────────
    panneau(580, 490, 1310, 800, f"LES TROUS À NEUF LIGNES · contre les {plus_long} coutures que 225 a franchies")
    longueurs = {"haut": c1 - c0, "bas": c1 - c0, "gauche": r1 - r0, "droite": r1 - r0}
    yy = 536
    for cote, lib in LES_COTES:
        tc = [t for t in trous if t["le_cote"] == cote]
        manque = sum(t["la_longueur"] for t in tc)
        longs = [t for t in tc if t["la_longueur"] > plus_long]
        ecrire(596, yy, f"{lib} · {manque} coutures sans majorité sur {longueurs[cote]}", 0, ENCRE)
        n_ = longueurs[cote]
        art.rectangle([596, yy + 20, 596 + 400, yy + 30], fill=BON)
        for t in tc:
            xa = 596 + 400 * (t["le_debut"] - (c0 if cote in ("haut", "bas") else r0)) / n_
            xb = xa + 400 * t["la_longueur"] / n_
            art.rectangle([xa, yy + 20, xb, yy + 30], fill=ALERTE if t["la_longueur"] > plus_long else FRANCHI)
            points.append((xb, yy + 30))
        if longs:
            ecrire(1010, yy + 16, "trop longs : " + ", ".join(f"{t['la_longueur']} dès {t['le_debut']}" for t in longs),
                   0, ALERTE)
        else:
            ecrire(1010, yy + 16, "tous franchis", 0, BON)
        traces[f"trous:{cote}"] = 1
        yy += 62
    ecrire(596, 780, "⚠ un trou se compte en coutures le long du côté, depuis la rangée ou la colonne indiquée", 0, GRIS)

    # ── BANDE ────────────────────────────────────────────────────────────────────────────────
    art.rectangle([0, 818, L_, H_], fill=BANDE)
    ecrire(50, 832, f"LE VERDICT : {d['le_verdict']['ce_qui_reste_a_mesurer']}", petit, ENCRE)
    ab = comptes[f"colonnes_{c1}"]
    ecrire(50, 856, f"★ la colonne {c1} et la rangée {r0} sortent de ce que le dépôt porte : {ab['absents']} chunks absents "
                    f"sur {ab['demandes']} pour la colonne, {comptes[f'rangees_{r0}']['absents']} sur "
                    f"{comptes[f'rangees_{r0}']['demandes']} pour la rangée.", moyen, ENCRE)
    ecrire(50, 882, "⚠⚠ ce ne sont pas des chunks trop peu texturés : le recto qu'on lit n'est pas un rectangle, et les bords "
                    "de la croix centrale ne sont pas ceux du segment.", moyen, ALERTE)
    ecrire(50, 908, f"★ la colonne {c0} et la rangée {r1} se lisent presque entières : leurs trous sont tous plus courts que "
                    f"{plus_long} coutures.", moyen, ENCRE)
    ecrire(50, 936, "⚠ ce qui n'est PAS établi : la fermeture à l'échelle du segment entier, qu'aucun rectangle dérivé de la "
                    "croix ne mesure.", moyen, ALERTE)
    ecrire(50, 962, "★ la suite : une boucle qui suit le contour que dessine la présence des chunks dans le dépôt.",
           moyen, ENCRE)

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
    tmp = sortie.parent / ".sonde_232.png"
    _, poses, cadres, points, traces = dessiner(d, tmp)

    def _v(a, b):
        return {"le_verdict": {"le_segment_entier_reste_ouvert": a, "le_segment_entier_se_ferme": b}}
    v("★★★★ les trois titres possibles sont distincts, et un trou non franchi prime",
      len({le_titre(_v(a, b)) for a in (True, False) for b in (True, False)}) == 3
      and le_titre(_v(True, True)) == le_titre(_v(True, False)))
    v("★★★ le titre LIT le verdict",
      ("RESTE OUVERT" in le_titre(d)) == bool(d["le_verdict"]["le_segment_entier_reste_ouvert"]))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_),
      str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({g for _, _, t, _ in poses for g in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    v("★★★ tout ce qui est tracé reste dans la toile", all(0 <= x <= L_ and 0 <= y <= H_ for x, y in points))
    r0, r1, c0, c1 = d["le_rectangle"]["les_coins"]
    v("★★★★ chaque couture des quatre côtés est tracée",
      traces.get("haut") == c1 - c0 and traces.get("bas") == c1 - c0 and traces.get("gauche") == r1 - r0
      and traces.get("droite") == r1 - r0)
    v("★★★★ chaque bande a ses comptes, et chaque côté ses trous",
      all(traces.get(f"compte:{b['cle']}") for b in d["les_bandes_declarees"])
      and all(traces.get(f"trous:{c}") for c, _ in LES_COTES))
    comptes = les_comptes(d)
    v("★★★★ les comptes d'une bande couvrent tous ses chunks demandés",
      all(k["lus"] + k["absents"] + k["texture"] == k["demandes"] for k in comptes.values()), str(comptes))
    txt = " ".join(t for _, _, t, _ in poses)
    v("★★★★ elle porte les trous trop longs, les comptes d'absence, et ce qui n'est PAS établi",
      all(f"{t['la_longueur']} dès {t['le_debut']}" in txt
          for t in d["par_largeur"][str(d["le_verdict"]["la_largeur_jugee"])]["les_trous"]
          if t["la_longueur"] > int(d["le_plus_long_trou_franchi_par_225"]))
      and all(f"absents du dépôt {k['absents']}" in txt for k in comptes.values()) and "n'est PAS établi" in txt)
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
                   default=RACINE / "docs" / "mesures" / "deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "232_deux_chemins_du_segment_entier_arrivent_ils_sur_la_meme_spire.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
