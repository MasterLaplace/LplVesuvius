"""Réessayer ailleurs plutôt que plus court.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les DEUX contrôles : la spirale nue
inchangée, et le compteur de détours qui ne fuit pas d'un marcheur à l'autre. En haut à droite, le
verdict — le détour ne l'emporte nulle part. En bas à gauche, ce qu'il récupère contre ce qu'il perd.
En bas à droite, le mur : les épuisements, qu'il franchit un peu plus souvent en acceptant une pose
qu'il ne devrait pas.

  uv run python src/figures/figure_reessayer_ailleurs_plutot_que_plus_court.py \\
      --json docs/mesures/reessayer_ailleurs_plutot_que_plus_court.json \\
      --sortie docs/images/166_reessayer_ailleurs_plutot_que_plus_court.png
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
FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
BANDE = (236, 234, 228)
ALERTE = (176, 92, 42)
BON = (60, 110, 90)
TEMOIN = (150, 152, 156)
CONTRE = (92, 108, 150)


def lire(chemin: Path) -> dict:
    """Le JSON de `reessayer_ailleurs_plutot_que_plus_court.py`.

    ⚠⚠ Refuse une mesure sans les DEUX contrôles : la spirale nue, et le fait que le compteur de
    détours ne fuit pas d'un marcheur à l'autre — sans quoi toute la comparaison serait illisible.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_identique") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if "le_plus_court_ne_detourne_jamais" not in j:
        raise ValueError(f"{chemin} : le contrôle de fuite du compteur est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince")
            .replace("une mâchoire avec rejet", "mâchoire seule"))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    j = d["juger"]
    bras, mat, tout = j["par_bras"], j["par_matiere"], j["tout"]
    c = j["le_controle_de_la_spirale_nue"]

    ecrire(28, 20, "Réessayer AILLEURS plutôt que plus court — l'hypothèse est RÉFUTÉE", gros,
           ENCRE)
    ecrire(28, 46, "`148` mesure que le cap incline la normale de plus de quarante degrés, `165` "
                   "que raccourcir s'y épuise : la direction semblait être en cause", petit, GRIS)

    # ---- panneau 1 : les deux controles
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les DEUX contrôles", moyen, ENCRE)
    m1 = "★" if c["il_est_identique"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{m1}  {c['nom']}", moyen, BON if c["il_est_identique"] else ALERTE)
    ecrire(x0 + 14, y0 + 52,
           f"{c['departs_identiques']}/{c['apparies']} départs identiques, "
           f"{c['detours']} détour tenté", petit, ENCRE)
    fuite = j["le_plus_court_ne_detourne_jamais"]
    ecrire(x0 + 14, y0 + 82, f"{'★' if fuite else '✗'}  le compteur ne FUIT pas", moyen,
           BON if fuite else ALERTE)
    ecrire(x0 + 14, y0 + 112,
           f"le marcheur de `165` compte {tout['detours_du_plus_court']} détour : il n'a pas",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 130, "cette faculté, donc un seul rendrait tout illisible", petit, ENCRE)
    ecrire(x0 + 14, y0 + ph - 74,
           "⚠ les populations appariées DIFFÈRENT d'une tranche à l'autre :", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 58,
           f"{bras[0]['apparies']} départs ici contre 149 dans `165`, parce que le", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 42,
           "troisième marcheur n'est pas le même. Un total absolu issu d'un", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 26,
           "plan apparié n'a de sens QU'AVEC sa population.", petit, ALERTE)

    # ---- panneau 2 : le verdict
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les deux livrables comparés — pas UTILISABLES", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 108
    barre_max = pw - 224
    vmax = max(max(g["plus_court"]["utilisable"], g["ailleurs"]["utilisable"])
               for g in bras) or 1
    for k, g in enumerate(bras):
        base = y0 + 30 + k * 78
        ecrire(x_nom, base - 18,
               f"{_court(g['nom'])} — {g['apparies']} départs appariés", petit, ENCRE)
        for i, (m, coul, lib) in enumerate((("plus_court", CONTRE, "plus court"),
                                            ("ailleurs", ALERTE, "ailleurs"))):
            yy = base + i * 22
            t = g[m]
            w = (t["utilisable"] / vmax) * barre_max
            ecrire(x_nom, yy - 1, lib, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            ecrire(x_barre + barre_max + 8, yy - 1,
                   f"{t['utilisable']} · {t['contaminees']}", 0, coul)
    ecrire(x0 + 12, y0 + ph - 38,
           "à droite : pas utilisables · livraisons contaminées", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "le détour livre autant et contamine DAVANTAGE", petit, ALERTE)

    # ---- panneau 3 : recupere contre perd
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce qu'il récupère, et ce qu'il perd", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 250
    nmax = max(max(g["le_detour_recupere"], g["le_detour_perd"]) for g in mat) or 1
    pas_bloc = max((ph - 84) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        base = y0 + 22 + k * pas_bloc
        ecrire(x_nom, base + 6, _court(g["nom"]), petit, ENCRE)
        for i, (cle, coul) in enumerate((("le_detour_recupere", BON),
                                         ("le_detour_perd", ALERTE))):
            yy = base + i * 15
            n = int(g[cle])
            w = (n / nmax) * barre_max
            if n:
                art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 12], fill=coul)
            points.append((x_barre + w, yy + 6))
        ecrire(x_barre + barre_max + 8, base + 6,
               f"{g['le_detour_recupere']} / {g['le_detour_perd']}", 0,
               BON if g["le_detour_perd"] == 0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 56,
           "vert : départs récupérés · ambre : départs perdus", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 38,
           "sur chaque matière qui se contredit, il perd plus qu'il ne récupère", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 20,
           "la victoire jointe n'est gagnée NULLE PART, sur aucun bras", petit, ALERTE)

    # ---- panneau 4 : le mur
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le mur — les épuisements sous le voxel", moyen, ENCRE)
    x_barre = x0 + 150
    barre_max = pw - 260
    emax = max(tout["epuisees_plus_court"], tout["epuisees_ailleurs"]) or 1
    for i, (cle, coul, lib) in enumerate(
            (("epuisees_plus_court", CONTRE, "en raccourcissant"),
             ("epuisees_ailleurs", ALERTE, "en détournant"))):
        yy = y0 + 34 + i * 30
        n = int(tout[cle])
        w = (n / emax) * barre_max
        ecrire(x0 + 12, yy - 1, lib, 0, GRIS)
        art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
        points.append((x_barre + w, yy + 7))
        ecrire(x_barre + barre_max + 8, yy - 1, str(n), 0, coul)
    ecrire(x0 + 12, y0 + 110,
           f"{tout['detours']} détours tentés en tout, pour "
           f"{tout['epuisees_plus_court'] - tout['epuisees_ailleurs']} épuisements de moins",
           petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 94,
           "le détour franchit donc le mur un peu plus souvent — mais il le", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 78,
           "franchit en acceptant une pose qu'il ne devrait pas. `162` mesure", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 62,
           "une précision de 0,397 : l'accord des mâchoires est NÉCESSAIRE,", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 46, "jamais suffisant.", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 22,
           "une direction où elles s'accordent peut être un FAUX accord", petit, ALERTE)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = bras[0]
    ecrire(74, y + 12,
           f"✗  L'hypothèse est RÉFUTÉE : sur le bras livré, le détour récupère "
           f"{pince['le_detour_recupere']} départs et en perd {pince['le_detour_perd']}, "
           f"pour {pince['detours']} détours tentés.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"✗  Et il CONTAMINE davantage : {pince['ailleurs']['contaminees']} livraisons "
           f"contre {pince['plus_court']['contaminees']} en raccourcissant seulement.",
           moyen, ALERTE)
    ecrire(74, y + 64,
           "★★★★  Ce que cela établit borne toute la ligne `162`–`165` : l'accord interne de la "
           "pose est une bonne ALARME et une mauvaise BOUSSOLE.", moyen, ENCRE)
    ecrire(74, y + 90,
           "★★★  Elle dit QUAND on se trompe, jamais OÙ aller. Chercher une direction où les "
           "mâchoires s'accordent, c'est chercher un accord qui peut être faux.", moyen, BON)
    ecrire(74, y + 110,
           f"⚠  Le mur recule à peine : {tout['epuisees_ailleurs']} épuisements contre "
           f"{tout['epuisees_plus_court']}, et ce recul se paie en livraisons fausses.",
           moyen, ENCRE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:180])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:180])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:180])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:180])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    faux = copy.deepcopy(d)
    faux["juger"]["tout"]["detours_du_plus_court"] = 8888
    faux["juger"]["le_plus_court_ne_detourne_jamais"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐⭐⭐ une FUITE du compteur change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses),
      "un détour compté chez qui n'en a pas la faculté rendrait tout illisible")
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_bras"]:
        g["ailleurs"]["contaminees"] = 7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐ ... et le compte des livraisons CONTAMINÉES est LU, pas supposé",
      any("7777" in t for _x, _y, t, _f in p3),
      "c'est lui qui refute l'hypothèse")
    # ⚠⚠ LA POPULATION APPARIEE EST ECRITE, parce qu'un total absolu d'un plan apparie n'a de sens
    # qu'avec elle — et elle DIFFERE de celle de `165`.
    tous = [t for _x, _y, t, _f in poses]
    v("⭐⭐⭐⭐ la population appariée est écrite à côté de chaque total",
      all(any(str(g["apparies"]) in t for t in tous) for g in d["juger"]["par_bras"]),
      f"{[g['apparies'] for g in d['juger']['par_bras']]}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_166.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle de la spirale nue est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans le contrôle de FUITE est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_plus_court_ne_detourne_jamais")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "reessayer_ailleurs_plutot_que_plus_court.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "166_reessayer_ailleurs_plutot_que_plus_court.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
