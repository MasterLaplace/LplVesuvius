#!/usr/bin/env python3
"""Une pince tient-elle une feuille autour d'un tour ?

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** En haut à gauche, la
pince elle-même, à ses vraies proportions : deux mâchoires posées sur les deux interstices d'une
feuille, chacune à trois appuis — c'est leur largeur qui donne l'orientation, et c'est l'écart entre
elles qui donne l'épaisseur. Une seule mâchoire doit la SUPPOSER. En haut à droite, ce que ça coûte
quand la matière devient difficile à lire : sur l'écrasement mesuré, la dérive d'une mâchoire
explose pendant que celle de la pince reste plate. En bas à gauche, la carte honnête — la pince ne
gagne pas partout, et là où elle perd c'est parce qu'un froissement lui cache un de ses deux
interstices. En bas à droite, la largeur de mâchoire, balayée.

  uv run python src/figures/figure_la_pince_tient_elle_la_feuille.py \\
      --json docs/mesures/la_pince_tient_elle_la_feuille.json \\
      --sortie docs/images/142_la_pince.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

from figure_commune import (police, textes_debordants, textes_hors_cadre,  # noqa: E402
                            textes_qui_se_recouvrent)

from PIL import Image, ImageDraw  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
FEUILLE = (196, 176, 140)
VIDE = (232, 230, 224)
UNE = (176, 92, 42)
DEUX = (86, 104, 132)
PINCE = (60, 110, 90)
PERD = (176, 92, 42)
RIEN = (170, 172, 176)
BRAS = ("une machoire", "deux machoires libres", "la pince")
COULEURS = {"une machoire": UNE, "deux machoires libres": DEUX, "la pince": PINCE}
NOMS = {"une machoire": "une mâchoire", "deux machoires libres": "deux mâchoires libres",
        "la pince": "la pince"}


def lire(chemin: Path) -> dict:
    """Le JSON de `la_pince_tient_elle_la_feuille.py`.

    ⚠⚠ Refuse une mesure sans les trois bras ou sans la case qui sépare : l'image est une
    comparaison, et une comparaison à laquelle il manque un terme affirme au lieu de montrer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    cases = d.get("sur_les_matieres", {}).get("cases", [])
    if not cases:
        raise ValueError(f"{chemin} : aucune case mesurée")
    for c in cases:
        manquants = set(BRAS) - set(c.get("bras", {}))
        if manquants:
            raise ValueError(f"{chemin} : bras absent(s) {sorted(manquants)}")
    if not d.get("juger", {}).get("decidable"):
        raise ValueError(f"{chemin} : le jugement est indécidable")
    if d["juger"].get("la_case_qui_separe") is None:
        raise ValueError(f"{chemin} : aucune case ne sépare, il n'y a rien à montrer")
    return d


def _cases_de(d: dict, ecrasement: float, amplitude_um: float) -> list[dict]:
    return sorted((c for c in d["sur_les_matieres"]["cases"]
                   if c["ecrasement"] == ecrasement and c["amplitude_um"] == amplitude_um),
                  key=lambda c: c["bruit"])


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1300, 906
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    b = d["sur_les_matieres"]
    j = d["juger"]
    tete = j["la_case_qui_separe"]
    cas_tete = [c for c in b["cases"]
                if c["ecrasement"] == tete["ecrasement"]
                and c["amplitude_um"] == tete["amplitude_um"]
                and c["bruit"] == tete["bruit"]][0]
    ecrire(28, 20, "Une pince tient la feuille que la sonde lâche", gros, ENCRE)
    ecrire(28, 46, f"un tour entier, {b['departs']} départs par case, mâchoire de "
                   f"{cas_tete['largeur_um']:g} µm, avance {cas_tete['avance_um']:g} µm · "
                   f"la vérité est connue : sur une spirale, suivre la feuille de phase k sur un "
                   f"tour y ramène exactement", petit, GRIS)

    # ── Haut gauche : la pince, à ses proportions ────────────────────────────
    x0, y0, pw, ph = 60, 122, 540, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la pince, à ses proportions mesurées", moyen, ENCRE)
    ep = cas_tete["bras"]["la pince"].get("epaisseur_mediane_um") or 173.0
    lar, av = cas_tete["largeur_um"], cas_tete["avance_um"]
    # ⚠ L'échelle vient de CE QUI EST DESSINÉ : la plus grande longueur du schéma tient dans le
    # panneau, et toutes les autres en découlent — pas de facteur choisi.
    # ⚠⚠ L'ECHELLE DOIT TENIR DANS LES DEUX SENS. Ma première version ne regardait que la largeur,
    # et les trois bandes débordaient du panneau par le haut et par le bas — la garde des cadres ne
    # voit que les textes, donc c'est l'œil qui l'a attrapé.
    gauche, droite = x0 + 26, x0 + pw - 26
    ech = min((droite - gauche - 150.0) / (2.0 * lar + av), (ph - 128.0) / (3.0 * ep))
    cx_, cy_ = gauche + 40 + lar * ech, y0 + 128
    # ⚠ La matière de la fixture est un COSINUS de la phase, pas des bandes franches : la dessiner
    # en dégradé est ce qui montre que les mâchoires reposent dans les CREUX et non sur des bords.
    import math  # noqa: PLC0415

    hb = 1.5 * ep * ech
    for k in range(int(2 * hb) + 1):
        yy = cy_ - hb + k
        w = 0.5 + 0.5 * math.cos(2.0 * math.pi * (yy - cy_) / (ep * ech))
        art.line([gauche, yy, droite, yy],
                 fill=tuple(int(VIDE[i] + (FEUILLE[i] - VIDE[i]) * w) for i in range(3)))
    for sens in (-1.0, 1.0):
        art.line([gauche, cy_ + sens * 0.5 * ep * ech, droite, cy_ + sens * 0.5 * ep * ech],
                 fill=GRIS, width=1)
    for sens in (-1.0, 1.0):
        yy = cy_ + sens * 0.5 * ep * ech
        for u in (-lar, 0.0, lar):
            ax = cx_ + u * ech
            art.ellipse([ax - 4, yy - 4, ax + 4, yy + 4], fill=PINCE)
            points.append((ax, yy))
        art.line([cx_ - lar * ech, yy, cx_ + lar * ech, yy], fill=PINCE, width=3)
    art.line([cx_, cy_ - 0.5 * ep * ech, cx_, cy_ + 0.5 * ep * ech], fill=PINCE, width=2)
    ecrire(int(cx_) + 8, int(cy_) - 7, f"{ep:.1f} µm mesurés", petit, PINCE)
    ecrire(int(cx_ - lar * ech), int(cy_ - 0.5 * ep * ech) - 19, "mâchoire, 3 appuis", petit, PINCE)
    ecrire(int(cx_ - lar * ech), int(cy_ + 0.5 * ep * ech) + 6, "l'autre interstice", petit, PINCE)
    ax0 = cx_ + lar * ech + 16
    ay = cy_ - 0.9 * ep * ech
    art.line([ax0, ay, ax0 + av * ech, ay], fill=ENCRE, width=2)
    art.line([ax0 + av * ech, ay, ax0 + av * ech - 7, ay - 4], fill=ENCRE, width=2)
    art.line([ax0 + av * ech, ay, ax0 + av * ech - 7, ay + 4], fill=ENCRE, width=2)
    ecrire(int(ax0), int(ay) - 19, f"avance {av:g} µm", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 56, "l'épaisseur est MESURÉE par l'écart des mâchoires ;", petit,
           ENCRE)
    ecrire(x0 + 12, y0 + ph - 40, "une seule mâchoire ne peut que la supposer, et c'est", petit,
           ENCRE)
    ecrire(x0 + 12, y0 + ph - 24, "toute la différence entre les deux premiers bras.", petit, ENCRE)

    # ── Haut droite : la dérive contre le bruit, sur la matière de tête ──────
    x1, y1, pw1, ph1 = 680, 122, L - 680 - 60, 300
    art.rectangle([x1, y1, x1 + pw1, y1 + ph1], outline=TRAIT, width=1)
    cadres.append((x1, y1, x1 + pw1, y1 + ph1))
    ecrire(x1, y1 - 24, f"la dérive en feuilles, sur {tete['nom']}", moyen, ENCRE)
    serie = _cases_de(d, tete["ecrasement"], tete["amplitude_um"])
    brs = [float(c["bruit"]) for c in serie]
    toutes = [c["bras"][k].get("derive_mediane") for c in serie for k in BRAS
              if c["bras"][k].get("derive_mediane") is not None]
    hi = max(toutes) * 1.18 if toutes else 1.0

    def bx(v):
        return x1 + 54 + (float(v) / max(brs)) * (pw1 - 96)

    def by(v):
        return y1 + ph1 - 44 - (float(v) / hi) * (ph1 - 78)

    for k in range(5):
        vv = hi * k / 4.0
        art.line([x1 + 50, by(vv), x1 + pw1 - 12, by(vv)], fill=TRAIT, width=1)
        ecrire(x1 + 8, int(by(vv)) - 7, f"{vv:.2f}", petit, GRIS)
    for c in serie:
        ecrire(int(bx(c["bruit"])) - 4, y1 + ph1 - 34, f"{c['bruit']:g}", petit, GRIS)
    ecrire(x1 + 54, y1 + ph1 - 18, "bruit de la matière", petit, GRIS)
    for k in BRAS:
        xy = [(bx(c["bruit"]), by(c["bras"][k]["derive_mediane"])) for c in serie
              if c["bras"][k].get("derive_mediane") is not None]
        if len(xy) > 1:
            art.line([p for q in xy for p in q], fill=COULEURS[k], width=2)
        for a_, b_ in xy:
            art.ellipse([a_ - 4, b_ - 4, a_ + 4, b_ + 4], fill=COULEURS[k])
            points.append((a_, b_))
    art.rectangle([x1 + 96, y1 + 6, x1 + pw1 - 10, y1 + 78], fill=FOND)
    c = serie[-1]
    ecrire(x1 + 102, y1 + 8, f"au bruit {c['bruit']:g} — bonne feuille, puis tours bouclés, "
                             f"sur {c['departs']} départs :", petit, GRIS)
    yl = y1 + 25
    for k in BRAS:
        m_ = c["bras"][k].get("memes_feuilles")
        t_ = c["bras"][k].get("tours_boucles")
        ecrire(x1 + 102, yl, f"{NOMS[k]} — {m_}/{c['departs']} et {t_}/{c['departs']}",
               petit, COULEURS[k])
        yl += 17

    # ── Bas gauche : la carte honnête ───────────────────────────────────────
    x2, y2, pw2, ph2 = 60, 480, 700, 286
    art.rectangle([x2, y2, x2 + pw2, y2 + ph2], outline=TRAIT, width=1)
    cadres.append((x2, y2, x2 + pw2, y2 + ph2))
    ecrire(x2, y2 - 24, "où la pince gagne, et où elle perd", moyen, ENCRE)
    mats, vus = [], set()
    for c in b["cases"]:
        cle = (c["ecrasement"], c["amplitude_um"])
        if cle not in vus:
            vus.add(cle)
            mats.append((cle, c["nom"]))
    bruits = sorted({c["bruit"] for c in b["cases"]})
    cw, chh = 58, 34
    gx, gy = x2 + 210, y2 + 46
    for i, bb in enumerate(bruits):
        ecrire(int(gx + i * cw + 14), gy - 22, f"{bb:g}", petit, GRIS)
    ecrire(gx, gy - 40, "bruit de la matière", petit, GRIS)
    par = {(x["ecrasement"], x["amplitude_um"], x["bruit"]): x for x in j["par_case"]}
    for r, (cle, nom) in enumerate(mats):
        ecrire(x2 + 12, gy + r * chh + 9, nom.replace("spirale ", ""), petit, ENCRE)
        for i, bb in enumerate(bruits):
            x_ = par.get((cle[0], cle[1], bb))
            if x_ is None:
                continue
            tous = x_["poses"]
            # ⚠ Le témoin est celui que la MESURE déclare ; la figure ne le redécide pas.
            coul = RIEN if x_["rien_a_separer"] else (PINCE if x_["la_pince_gagne"] else PERD)
            ax, ay = gx + i * cw, gy + r * chh
            art.rectangle([ax, ay, ax + cw - 8, ay + chh - 8], fill=coul)
            points.append((ax, ay))
            m_ = x_["memes_la_pince"]
            ecrire(int(ax) + 12, int(ay) + 7, f"{m_}/{tous}" if m_ is not None else "—",
                   petit, FOND)
    # ⚠ La légende tient sur DEUX lignes et dans son panneau : la première version courait
    # jusqu'au panneau voisin, et la garde des cadres l'a dit avant que l'œil ne le voie.
    yl = gy + len(mats) * chh + 8
    lx = x2 + 12
    for coul, nom in ((PINCE, "la pince gagne"), (PERD, "elle perd"),
                      (RIEN, "personne ne dérive")):
        art.rectangle([lx, yl + 3, lx + 14, yl + 13], fill=coul)
        ecrire(lx + 20, yl, nom, petit, coul)
        lx += 160
    ecrire(x2 + 12, yl + 18, "le chiffre d'une case dit combien de départs finissent sur la BONNE "
                             "feuille ; une case grise est le témoin", petit, GRIS)

    # ── Bas droite : la largeur de mâchoire ─────────────────────────────────
    x3, y3, pw3, ph3 = 800, 480, L - 800 - 60, 286
    art.rectangle([x3, y3, x3 + pw3, y3 + ph3], outline=TRAIT, width=1)
    cadres.append((x3, y3, x3 + pw3, y3 + ph3))
    ecrire(x3, y3 - 24, "la largeur de mâchoire, balayée", moyen, ENCRE)
    lar_ = j.get("par_largeur") or []
    if lar_:
        hi3 = max(x["derive_une_machoire"] or 0.0 for x in lar_) * 1.2 or 1.0
        pas_x = (pw3 - 90) / max(len(lar_), 1)
        for i, x_ in enumerate(lar_):
            ax = x3 + 66 + (i + 0.5) * pas_x
            for k, cle in (("la pince", "derive_la_pince"),
                           ("une machoire", "derive_une_machoire")):
                vv = x_.get(cle)
                if vv is None:
                    continue
                hh = (vv / hi3) * (ph3 - 148)
                dx = -11 if k == "la pince" else 3
                art.rectangle([ax + dx, y3 + ph3 - 56 - hh, ax + dx + 8, y3 + ph3 - 56],
                              fill=COULEURS[k])
                points.append((ax + dx, y3 + ph3 - 56 - hh))
            ecrire(int(ax) - 26, y3 + ph3 - 48, f"{x_['largeur_um']:.1f} µm", petit, GRIS)
            ecrire(int(ax) - 18, y3 + ph3 - 32, f"{x_['tours_la_pince']} tours", petit, PINCE)
        for k in range(4):
            vv = hi3 * k / 3.0
            yy = y3 + ph3 - 56 - (vv / hi3) * (ph3 - 148)
            art.line([x3 + 60, yy, x3 + pw3 - 10, yy], fill=TRAIT, width=1)
            ecrire(x3 + 10, int(yy) - 7, f"{vv:.2f}", petit, GRIS)
        # ⚠ Bande réservée : la garde compare texte à texte, pas texte à une barre.
        art.rectangle([x3 + 62, y3 + 4, x3 + pw3 - 8, y3 + 58], fill=FOND)
        ecrire(x3 + 68, y3 + 6, "dérive médiane en feuilles", petit, GRIS)
        ecrire(x3 + 68, y3 + 23, "la pince", petit, PINCE)
        ecrire(x3 + 68, y3 + 40, "une mâchoire", petit, UNE)

    # ── Bande de conclusion ─────────────────────────────────────────────────
    by0 = 792
    art.rectangle([28, by0, L - 28, H - 22], fill=BANDE)
    cadres.append((28, by0, L - 28, H - 22))
    ecrire(44, by0 + 10, f"★ sur {tete['nom']} à bruit {tete['bruit']:g}, une mâchoire finit sur "
                         f"la BONNE feuille {tete['memes_une_machoire']} fois sur "
                         f"{tete['poses']} ; la pince {tete['memes_la_pince']} fois sur "
                         f"{tete['poses']}, et elle boucle {tete['tours_la_pince']} tours contre "
                         f"{tete['tours_une_machoire']}.", moyen, ENCRE)
    ecrire(44, by0 + 34, f"la seconde mâchoire divise la dérive par "
                         f"{tete['gain_de_la_seconde_machoire']}, la contrainte par "
                         f"{tete['gain_de_la_contrainte']} de plus — {tete['gain_total']} en tout, "
                         f"et la pince boucle PLUS de tours, pas moins.", petit, ENCRE)
    ecrire(44, by0 + 52, f"⚠ elle ne gagne pas partout : {j['gagne_parmi_celles_qui_separent']} "
                         f"des {j['cases_qui_separent']} cases qui séparent quelque chose (les "
                         f"{j['cases_ou_personne_ne_derive']} autres sont le témoin). Une pince "
                         f"exige de voir ses DEUX interstices, et un froissement assez raide lui "
                         f"en cache un.", petit, ENCRE)
    ecrire(44, by0 + 74, "⚠ la matière que `140` retient (écrasée et froissée à 100 µm) ne laisse "
                         "aucun bras boucler un tour : la pince est démontrée sur l'écrasement, "
                         "pas sur toute la matière.", petit, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier() -> int:
    echecs = controles = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile  # noqa: PLC0415

    from figure_commune import glyphes_manquants  # noqa: PLC0415

    src = RACINE / "docs" / "mesures" / "la_pince_tient_elle_la_feuille.json"
    v("la mesure existe", src.exists(), str(src))
    if not src.exists():
        print(f"\nÉCHEC ({echecs + 1} failures, {controles + 1} checks)")
        return 1
    d = lire(src)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for nom, contenu in (
                ("message", {"message": "fixture injoignable"}),
                ("sans case", {"sur_les_matieres": {"cases": []}, "juger": {"decidable": True}}),
                ("bras absent", {"sur_les_matieres": {"cases": [
                    {"bras": {"la pince": {}}, "nom": "x"}]}, "juger": {"decidable": True}}),
                ("jugement indécidable", {"sur_les_matieres": d["sur_les_matieres"],
                                          "juger": {"decidable": False}}),
                ("rien ne sépare", {"sur_les_matieres": d["sur_les_matieres"],
                                    "juger": {"decidable": True, "la_case_qui_separe": None}})):
            p = tmp / "x.json"
            p.write_text(json.dumps(contenu), encoding="utf-8")
            try:
                lire(p)
                ok = False
            except ValueError:
                ok = True
            v(f"une mesure « {nom} » est refusée, jamais dessinée à moitié", ok)

        v("les cases d'une matière sortent triées par bruit",
          [c["bruit"] for c in _cases_de(d, 0.0, 0.0)]
          == sorted(c["bruit"] for c in _cases_de(d, 0.0, 0.0)))

        sortie = tmp / "142.png"
        chemin, poses, cadres, points = dessiner(d, sortie)
        v("l'image est écrite", chemin.exists() and chemin.stat().st_size > 0)
        v("un cadre par panneau, plus celui de la bande de conclusion", len(cadres) == 5,
          f"{len(cadres)}")
        deb = textes_debordants(poses, 1300)
        v("aucun texte ne déborde de la toile", not deb, str(deb[:2]))
        hors = textes_hors_cadre(poses, cadres)
        v("aucun texte ne sort de son panneau", not hors, str(hors[:2]))
        rec = textes_qui_se_recouvrent(poses)
        v("aucun texte n'en recouvre un autre", not rec, str(rec[:3]))
        manquants = sorted({g for _x, _y, t, _f in poses for g in glyphes_manquants(t)})
        v("aucun glyphe absent de la police déployée", not manquants, str(manquants))
        v("tous les points tracés tombent dans la toile",
          all(0 <= x <= 1300 and 0 <= y <= 906 for x, y in points), f"{len(points)} points")
        v("il y a bien de quoi regarder", len(points) > 40, f"{len(points)} points")

        autre = tmp / "142_bis.png"
        dessiner(d, autre)
        v("⭐ deux rendus de la même vue sont identiques au bit",
          sortie.read_bytes() == autre.read_bytes())

        # ---- ⭐ la figure LIT la mesure : la changer change l'image
        d2 = json.loads(json.dumps(d))
        d2["juger"]["la_case_qui_separe"]["gain_total"] = 999.0
        troisieme = tmp / "142_ter.png"
        dessiner(d2, troisieme)
        v("⭐ la bande de conclusion lit la mesure, elle n'est pas figée",
          troisieme.read_bytes() != sortie.read_bytes())
        d3 = json.loads(json.dumps(d))
        for x in d3["juger"]["par_case"]:
            x["la_pince_gagne"] = True
        quatrieme = tmp / "142_qua.png"
        dessiner(d3, quatrieme)
        v("⭐ la carte lit la mesure elle aussi", quatrieme.read_bytes() != sortie.read_bytes())

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs/mesures/la_pince_tient_elle_la_feuille.json")
    p.add_argument("--sortie", type=Path, default=RACINE / "docs/images/142_la_pince.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    chemin, _poses, _cadres, _points = dessiner(lire(a.json), a.sortie)
    print(f"→ {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
