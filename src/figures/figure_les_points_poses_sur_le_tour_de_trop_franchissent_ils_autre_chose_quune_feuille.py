"""Sous chaque surface à deux tours des graines 4 à 8, ce que le compte de 345 dit des points posés sur le tour attendu et de ceux posés sur le tour de trop : une feuille, zéro, deux ou plus, ou pas compté.

⚠⚠ **Ce que cette figure doit rendre évident.** À gauche, deux barres par surface, celle des points du tour attendu et celle des points du
tour de trop ; la part foncée à gauche de chaque barre est celle qui franchit exactement une feuille, et les deux traits sont le quart et
les trois quarts. Le compte voit le changement quand la barre du tour de trop s'arrête avant le quart et celle du tour attendu passe les
trois quarts. À droite, les surfaces une par ligne, avec ce que dit la lecture.

  uv run python src/figures/figure_les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.py \\
      --sortie docs/images/347_les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.png

⚠ Tout vient de la mesure de `347`.
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
LA_MESURE = RACINE / "docs" / "mesures" / "les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.json"

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
L_, H_ = 1360, 600
LA_BANDE = 510
LES_SEUILS = (0.25, 0.75)
LE_GAUCHE, LA_DROITE = 300, 660
LE_PAS_DES_RANGEES = 56
LES_GENRES = (("une feuille", lambda k: k == "1", (58, 88, 120)),
              ("zéro", lambda k: k == "0", (176, 92, 42)),
              ("deux ou plus", lambda k: k not in ("0", "1", "non compté"), (150, 110, 150)),
              ("pas compté", lambda k: k == "non compté", (212, 210, 205)))
LES_NOMS = {"sans relance": "sans relance", "relancée depuis un point": "depuis un point", "relancée depuis la spire": "depuis la spire",
            "bornée": "bornée"}


def lire(chemin: Path = LA_MESURE) -> dict:
    return json.loads(chemin.read_text())


def les_surfaces(d: dict) -> list[dict]:
    return [s for s in d["les_surfaces"] if s["le_rang"] >= 4 and s["la_surface"] is not None]


def le_titre(d: dict) -> str:
    v = d["le_verdict"]
    if not v.get("decidable"):
        return v["lissue"].upper()
    return f"le compte voit le changement de tour sous {v['k']} des {v['n']} surfaces tenues à tort qui sont lues".upper()


def les_segments(groupe: dict) -> list[tuple[str, int]]:
    """Les comptes d'un groupe de points, rangés par genre : une feuille, zéro, deux ou plus, pas compté."""
    return [(nom, sum(v for k, v in groupe["les_comptes"].items() if garde(k))) for nom, garde, _ in LES_GENRES]


def f2(x) -> str:
    return "non lue" if x is None else f"{x:.2f}".replace(".", ",")


def la_bande(d: dict) -> tuple[str, str, str]:
    v, b = d["le_verdict"], d["sur_tous_les_points"]["graines_4_a_8"]
    un = f"LE VERDICT DÉCLARÉ : {v['lissue']}"
    deux = (f"rapporté à côté, qui ne décide rien : sur tous les points du compte, et non sur les seuls comptés, un saut tient "
            f"{b['les_justes_qui_tiennent']} des {b['les_justes']} justes et {b['les_faux_qui_tiennent']} des {b['les_faux']} faux")
    trois = "⚠ ce qui n'est PAS établi : pourquoi, sous la surface bornée, les points posés sur le tour d'où part le saut en franchissent une."
    return un, deux, trois


def dessiner(d: dict, sortie: Path):
    img = Image.new("RGB", (L_, H_), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(16, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    cadres: list[tuple[int, int, int, int]] = []
    traces = {"barres": [], "lignes": [], "rectangles": []}

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    ecrire(50, 20, le_titre(d), gros, ENCRE)
    ecrire(50, 46, "ce que le compte de 345 dit des points posés sur chaque tour que la surface retrouve", petit, GRIS)
    x0, y0, x1, y1 = 50, 76, 690, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les points de chaque surface, par tour", moyen, ENCRE)
    gx0, gx1 = LE_GAUCHE, LA_DROITE
    X = lambda p: gx0 + p * (gx1 - gx0)  # noqa: E731
    haut, bas = y0 + 44, y1 - 70
    for p in LES_SEUILS:
        art.line([X(p), haut, X(p), bas], fill=ALERTE, width=2)
        ecrire(int(X(p)) - 12, bas + 4, f"{int(p * 100)} %", 0, ALERTE)
    ecrire(gx0 - 6, bas + 4, "0", 0, GRIS)
    ecrire(gx1 - 14, bas + 4, "100 %", 0, GRIS)
    y = haut + 12
    for s in les_surfaces(d):
        a = s["la_surface"]
        tenue = "tenue" if s["tient_par_345"] else "refusée"
        ecrire(x0 + 12, y, f"{LES_NOMS[s['la_chaine']]}, graine {s['le_rang']}, saut {s['le_saut']} ; 345 : {tenue}", 0,
               ALERTE if s["tient_par_345"] else ENCRE)
        for k, (cle, etiquette) in enumerate((("sur_le_tour_attendu", f"le tour attendu, {a['le_tour_attendu']}"),
                                             ("sur_un_tour_de_trop",
                                              "le tour de trop, " + ", ".join(str(t) for t in a["les_tours_de_trop"])))):
            g = a[cle]
            yb = y + 16 + k * 16
            ecrire(x0 + 24, yb, etiquette, 0, ENCRE)
            total = g["les_points"]
            gauche = float(gx0)
            segs = []
            for (nom, n), (_, _, couleur) in zip(les_segments(g), LES_GENRES):
                if not total or not n:
                    segs.append((nom, 0.0))
                    continue
                w = n / total * (gx1 - gx0)
                art.rectangle([gauche, yb + 2, gauche + w, yb + 13], fill=couleur)
                segs.append((nom, w))
                gauche += w
            traces["barres"].append((s["la_chaine"], s["le_rang"], s["le_saut"], cle, total, segs))
            traces["rectangles"].append((0, gx0, gauche, yb + 2, yb + 13))
        y += LE_PAS_DES_RANGEES
    lx = x0 + 12
    for nom, _, couleur in LES_GENRES:
        art.rectangle([lx, y1 - 26, lx + 12, y1 - 16], fill=couleur)
        traces["rectangles"].append((0, lx, lx + 12, y1 - 26, y1 - 16))
        ecrire(lx + 18, y1 - 28, nom, 0, ENCRE)
        lx += 18 + int(art.textlength(nom, font=petit)) + 24
    ecrire(gx0, y1 - 48, "la part des points de la barre", 0, GRIS)

    x0, y0, x1, y1 = 720, 76, 1310, 490
    art.rectangle([x0, y0, x1, y1], outline=TRAIT)
    cadres.append((x0, y0, x1, y1))
    ecrire(x0 + 12, y0 + 8, "les surfaces à deux tours des graines 4 à 8", moyen, ENCRE)
    cols = (x0 + 12, x0 + 115, x0 + 190, x0 + 250, x0 + 310, x0 + 370, x0 + 430)
    for x, t in zip(cols, ("chaîne", "graine", "tours", "345", "attendu", "de trop", "lecture")):
        ecrire(x, y0 + 44, t, 0, GRIS)
    y = y0 + 66
    for s in les_surfaces(d):
        a = s["la_surface"]
        tours = ", ".join(str(t) for t in sorted([a["le_tour_attendu"], *a["les_tours_de_trop"]], reverse=True))
        lecture = {"le compte voit le changement": "il voit", "le compte ne le voit pas": "il ne voit pas"}.get(a["la_lecture"], a["la_lecture"])
        cellules = (LES_NOMS[s["la_chaine"]], f"{s['le_rang']}, saut {s['le_saut']}", tours,
                    "tenue" if s["tient_par_345"] else "refusée", f2(a["sur_le_tour_attendu"]["la_part_dune_feuille"]),
                    f2(a["sur_un_tour_de_trop"]["la_part_dune_feuille"]), lecture)
        for x, t in zip(cols, cellules):
            ecrire(x, y, t, 0, ALERTE if s["tient_par_345"] else ENCRE)
        traces["lignes"].append(cellules)
        y += 22
    ecrire(x0 + 12, y + 16, "attendu, de trop : la part des points posés sur ce tour qui franchissent", 0, GRIS)
    ecrire(x0 + 12, y + 32, "exactement une feuille ; un point pas compté n'en franchit pas une", 0, GRIS)

    art.rectangle([0, LA_BANDE, L_, H_], fill=BANDE)
    un, deux, trois = la_bande(d)
    ecrire(50, LA_BANDE + 10, un, petit, ENCRE)
    ecrire(50, LA_BANDE + 26, deux, petit, ENCRE)
    ecrire(50, LA_BANDE + 48, trois, moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, traces


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
    tmp = sortie.parent / ".sonde_347.png"
    try:
        _, poses, cadres, traces = dessiner(d, tmp)
    except Exception as exc:  # noqa: BLE001
        print(f"  ÉCHEC ★★★★ le rendu lève {type(exc).__name__}: {exc}")
        print(f"{Path(__file__).name}   DES SONDES ONT ÉCHOUÉ (1 failures, 1 checks)")
        return 1
    autre = json.loads(json.dumps(d))
    autre["le_verdict"] = {"decidable": True, "k": 1, "n": 4, "lissue": "x ; y"}
    v("★★★ le titre LIT la mesure", le_titre(autre).startswith("LE COMPTE VOIT LE CHANGEMENT DE TOUR SOUS 1 DES 4"), le_titre(autre))
    autre["le_verdict"] = {"decidable": False, "lissue": "indécidable : une lecture a échoué (x)"}
    v("★★★ un titre indécidable LIT son issue", le_titre(autre) == "INDÉCIDABLE : UNE LECTURE A ÉCHOUÉ (X)", le_titre(autre))
    v("★★★★ aucun texte ne déborde de la toile", not textes_debordants(poses, L_), str(textes_debordants(poses, L_))[:200])
    v("★★★★ aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("★★★★ aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses), str(textes_qui_se_recouvrent(poses))[:200])
    v("★★★★ aucun cadre ne passe sous la bande du verdict", all(y1 < LA_BANDE for _, _, _, y1 in cadres))
    manquants = sorted({x for _, _, t, _ in poses for x in glyphes_manquants(t)})
    v("★★★★ aucun glyphe n'est absent de la police déployée", not manquants, str(manquants))
    surf = les_surfaces(d)
    v("★★★★ deux barres par surface à deux tours des graines 4 à 8, et aucune autre",
      sorted(b[:4] for b in traces["barres"]) == sorted((s["la_chaine"], s["le_rang"], s["le_saut"], c) for s in surf
                                                         for c in ("sur_le_tour_attendu", "sur_un_tour_de_trop")))
    largeur = LA_DROITE - LE_GAUCHE
    faux_ = []
    for chaine, rang, saut, cle, total, segs in traces["barres"]:
        g = next(s["la_surface"][cle] for s in surf if (s["la_chaine"], s["le_rang"], s["le_saut"]) == (chaine, rang, saut))
        n1 = g["les_comptes"].get("1", 0)
        nz = g["les_comptes"].get("0", 0)
        npc = g["les_comptes"].get("non compté", 0)
        nplus = sum(v_ for k, v_ in g["les_comptes"].items() if k not in ("0", "1", "non compté"))
        attendu = [n1, nz, nplus, npc]
        if total != g["les_points"] or sum(attendu) != total:
            faux_.append((chaine, rang, saut, cle, "total"))
            continue
        if any(abs(w - n / total * largeur) > 0.5 for (_, w), n in zip(segs, attendu)):
            faux_.append((chaine, rang, saut, cle, [round(w, 1) for _, w in segs], attendu))
    v("★★★★ chaque segment porte sa part des points, recomptée sur les comptes", not faux_, str(faux_[:2]))
    part1 = [(b[5][0][1] / largeur, next(s["la_surface"][b[3]]["la_part_dune_feuille"] for s in surf
                                         if (s["la_chaine"], s["le_rang"], s["le_saut"]) == b[:3])) for b in traces["barres"]]
    v("★★★★ le segment d'une feuille s'arrête à la part que lit la mesure",
      all(p is None or abs(w - p) < 0.002 for w, p in part1), str(part1[:3]))
    v("★★★ une ligne du tableau par surface, à ses parts et sa lecture",
      [(x[1], x[4], x[5]) for x in traces["lignes"]]
      == [(f"{s['le_rang']}, saut {s['le_saut']}", f2(s["la_surface"]["sur_le_tour_attendu"]["la_part_dune_feuille"]),
           f2(s["la_surface"]["sur_un_tour_de_trop"]["la_part_dune_feuille"])) for s in surf])
    tenues_voient = sum(1 for s in surf if s["tient_par_345"] and s["la_surface"]["la_lecture"] == "le compte voit le changement")
    tenues_lues = sum(1 for s in surf if s["tient_par_345"] and s["la_surface"]["la_lecture"] != "non lue")
    v("★★★★ le tableau compte autant de tenues vues et lues que le verdict",
      not d["le_verdict"].get("decidable") or (tenues_voient, tenues_lues) == (d["le_verdict"]["k"], d["le_verdict"]["n"]),
      str((tenues_voient, tenues_lues)))
    b = d["sur_tous_les_points"]["graines_4_a_8"]
    v("★★★★ la bande rapporte à côté les comptes sur tous les points",
      f"{b['les_justes_qui_tiennent']} des {b['les_justes']} justes et {b['les_faux_qui_tiennent']} des {b['les_faux']} faux"
      in " ".join(la_bande(d)))
    dehors = [r for r in traces["rectangles"] if not (cadres[r[0]][0] < r[1] and r[2] < cadres[r[0]][2]
                                                      and cadres[r[0]][1] < r[3] and r[4] < cadres[r[0]][3])]
    v("★★★★ rien ne sort de son cadre", not dehors, str(dehors[:3]))
    mesureur = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    boites = [mesureur.textbbox((x, y), t, font=f) for x, y, t, f in poses]
    sous = [r for r in traces["rectangles"] if any(bb[0] < r[2] and r[1] < bb[2] and bb[1] < r[4] and r[3] < bb[3] for bb in boites)]
    v("★★★★ aucune barre ne passe sous un texte", not sous, str(sous[:3]))
    rr = traces["rectangles"]
    chevauchent = [(a, b) for i, a in enumerate(rr) for b in rr[i + 1:] if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]]
    v("★★★★ aucune barre n'en recouvre une autre", not chevauchent, str(chevauchent[:2]))
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
                   / "347_les_points_poses_sur_le_tour_de_trop_franchissent_ils_autre_chose_quune_feuille.png")
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
