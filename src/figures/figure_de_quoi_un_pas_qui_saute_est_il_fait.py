"""De quoi un pas qui saute est-il fait ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle, et il est VIDE :
sur la spirale nue aucun pas ne saute, donc il n'y a rien à comparer et la figure le dit au lieu de
dessiner des zéros. En haut à droite, le fait central : bras par bras, dans combien de marches
chaque moitié du pas sépare les pas qui sautent des autres — et combien de fois la part tangente
est EXACTEMENT égale des deux côtés. En bas à gauche, de combien elle sépare, matière par matière.
En bas à droite, le verdict par bras, et ce qu'un verdict global aurait effacé.

  uv run python src/figures/figure_de_quoi_un_pas_qui_saute_est_il_fait.py \\
      --json docs/mesures/de_quoi_un_pas_qui_saute_est_il_fait.json \\
      --sortie docs/images/161_de_quoi_un_pas_qui_saute_est_il_fait.png
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
    """Le JSON de `de_quoi_un_pas_qui_saute_est_il_fait.py`.

    ⚠⚠ Refuse une mesure sans le contrôle de la spirale nue : c'est lui qui autorise à lire le
    reste, et une figure dessinée sans lui ressemble exactement à une figure qui l'aurait.

    ⚠⚠ Refuse AUSSI un jugement sans verdict par bras. Une figure qui retomberait sur un verdict
    global dessinerait précisément l'effacement que la mesure a mis au jour.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_matiere") or not j.get("par_regle"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_vide") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if not j.get("le_verdict_par_bras"):
        raise ValueError(f"{chemin} : le verdict par bras est absent")
    return d


def _court(nom: str) -> str:
    return (nom.replace("spirale ", "").replace("écrasée et froissée", "écr+fro")
            .replace("froissée", "fro").replace("écrasée", "écr")
            .replace("la pince de `144`", "la pince").replace("une mâchoire avec rejet",
                                                              "mâchoire seule"))


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list]:
    """Dessine, et rend AUSSI les poses de texte, les cadres et les points tracés."""
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    j = d["juger"]
    mat, reg = j["par_matiere"], j["par_regle"]
    c = j["le_controle_de_la_spirale_nue"]

    ecrire(28, 20, "De quoi un pas qui saute est-il fait ? La question que `160` laisse ouverte",
           gros, ENCRE)
    ecrire(28, 46, "un pas a DEUX moitiés et une seule est bornée : l'avance commandée le long de "
                   "la tangente, et le recentrage des mâchoires le long de la normale, qui va où "
                   "l'interstice se trouve", petit, GRIS)

    # ---- panneau 1 : le controle, et il est VIDE
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle : là où rien ne saute, il n'y a RIEN à comparer", moyen, ENCRE)
    marque = "★" if c["il_est_vide"] else "✗"
    ecrire(x0 + 14, y0 + 24, f"{marque}  {c['nom']}", moyen, BON if c["il_est_vide"] else ALERTE)
    ecrire(x0 + 14, y0 + 56, f"cases appariables : {c['cases_appariables']}", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 82,
           f"marches sans un pas qui saute : {c['marches_sans_pas_qui_sautent']} "
           f"sur {c['decidables']}", moyen, ENCRE)
    ecrire(x0 + 14, y0 + ph - 100,
           "`R4-F145` y mesure zéro pas qui saute, donc la comparaison n'y est", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 84,
           "pas NULLE : elle n'y est pas. Rendre zéro ferait lire « les deux", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 68,
           "moitiés se valent » là où il n'y a aucune des deux populations.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 40,
           f"sur la grille entière : {j['marches_appariables']} marches appariables", petit, ENCRE)

    # ---- panneau 2 : les deux moities, bras par bras
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "dans combien de marches chaque moitié sépare", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 96
    barre_max = pw - 216
    for k, g in enumerate(reg):
        base = y0 + 22 + k * 74
        app = max(int(g.get("marches_appariables", 0)), 1)
        ecrire(x_nom, base, f"{_court(g['nom'])} — {g.get('marches_appariables', 0)} marches",
               petit, ENCRE)
        for dec, quoi in ((22, "normale"), (46, "tangente")):
            sep = int(g.get(f"la_{quoi}_separe", 0))
            ega = int(g.get(f"la_{quoi}_est_egale", 0))
            env = int(g.get(f"la_{quoi}_separe_a_lenvers", 0))
            ecrire(x_nom, base + dec + 2, quoi, petit, GRIS)
            gauche = x_barre
            for val, coul in ((sep, ALERTE), (ega, TEMOIN), (env, CONTRE)):
                w = (val / app) * barre_max
                if val:
                    art.rectangle([gauche, base + dec, gauche + max(w, 1), base + dec + 13],
                                  fill=coul)
                points.append((gauche + w, base + dec + 6))
                gauche += w
            ecrire(x_barre + barre_max + 8, base + dec + 2, f"{sep} · {ega} · {env}", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 56, "ambre : la moitié est plus GRANDE du côté qui saute · "
                                  "gris : EXACTEMENT égale", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 38, "bleu : plus PETITE du côté qui saute", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20, "sur la pince, la tangente est égale des deux côtés : "
                                  "l'avance est commandée", petit, ENCRE)

    # ---- panneau 3 : de combien elle separe, matiere par matiere
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "de combien — rapport médian des deux moitiés, apparié par marche",
           moyen, ENCRE)
    rs = [m.get("rapport_normal_median") or 0.0 for m in mat]
    rmax = max(rs) or 1.0
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 296
    for k, m in enumerate(mat):
        yy = y0 + 26 + k * 40
        ecrire(x_nom, yy + 6, _court(m["nom"]), petit, ENCRE)
        if not m.get("cases_appariables"):
            ecrire(x_barre, yy + 6, "aucun pas ne saute — rien à comparer", petit, BON)
            continue
        for dec, cle, coul in ((0, "rapport_normal_median", ALERTE),
                               (15, "rapport_tangent_median", TEMOIN)):
            val = m.get(cle) or 0.0
            w = (val / rmax) * barre_max
            art.rectangle([x_barre, yy + dec, x_barre + max(w, 1), yy + dec + 12], fill=coul)
            points.append((x_barre + w, yy + dec + 6))
        ecrire(x_barre + barre_max + 8, yy + 6,
               f"×{m['rapport_normal_median']:g} / ×{m['rapport_tangent_median']:g}", petit,
               ALERTE)
    ecrire(x0 + 12, y0 + ph - 40, "ambre : le RECENTRAGE · gris : l'AVANCE", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 22,
           "le recentrage sépare davantage sur toutes les matières qui sautent", petit, ENCRE)

    # ---- panneau 4 : le verdict par bras, et ce qu'un verdict global effacerait
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le verdict, bras par bras", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 96
    barre_max = pw - 216
    for k, g in enumerate(reg):
        base = y0 + 24 + k * 68
        app = max(int(g.get("marches_appariables", 0)), 1)
        ecrire(x_nom, base, _court(g["nom"]), petit, ENCRE)
        gauche = x_barre
        for cle, coul in (("seule_la_normale_separe", ALERTE), ("les_deux_separent", TEMOIN),
                          ("seule_la_tangente_separe", CONTRE)):
            val = int(g.get(cle, 0))
            w = (val / app) * barre_max
            if val:
                art.rectangle([gauche, base + 18, gauche + max(w, 1), base + 32], fill=coul)
            points.append((gauche + w, base + 25))
            gauche += w
        ecrire(x_barre + barre_max + 8, base + 20,
               f"{g.get('seule_la_normale_separe', 0)} · {g.get('les_deux_separent', 0)} · "
               f"{g.get('seule_la_tangente_separe', 0)}", petit, ENCRE)
        ecrire(x_nom, base + 40, f"→ {j['le_verdict_par_bras'].get(g['nom'])}", petit,
               ALERTE if j["le_verdict_par_bras"].get(g["nom"]) == "le recentrage" else GRIS)
    ecrire(x0 + 12, y0 + ph - 76, "ambre : seule la NORMALE sépare · gris : les DEUX · "
                                  "bleu : seule la TANGENTE", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 56,
           f"les deux bras s'accordent : {j['les_deux_bras_saccordent']}", petit, ENCRE)
    ecrire(x0 + 12, y0 + ph - 36,
           f"un verdict pris sur les cases CONFONDUES — {j['seule_la_normale_separe']} seule N, "
           f"{j['les_deux_separent']} les deux —", petit, ALERTE)
    ecrire(x0 + 12, y0 + ph - 18, "aurait effacé la réponse de la pince, l'instrument livré.",
           petit, ALERTE)

    # ---- bande de conclusion
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = reg[0]
    ecrire(74, y + 12,
           f"★★★★  Pour la pince, la part TANGENTE est exactement égale des deux côtés dans "
           f"{pince.get('la_tangente_est_egale', 0)} marches sur "
           f"{pince.get('marches_appariables', 0)} : l'avance est commandée.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★★  Ce qui sépare est le RECENTRAGE, seul, dans "
           f"{pince.get('seule_la_normale_separe', 0)} marches sur "
           f"{pince.get('marches_appariables', 0)}, d'un facteur médian "
           f"×{pince.get('rapport_normal_median')}.", moyen, ALERTE)
    ecrire(74, y + 64,
           "★★★  Donc un pas saute quand les mâchoires se raccrochent LOIN : elles s'accrochent "
           "au mauvais interstice À LA POSE, et `155` ne traite ce défaut qu'aux APPUIS.",
           moyen, BON)
    ecrire(74, y + 90,
           f"⚠  Et les deux bras ne disent pas la même chose : la mâchoire seule n'a rien qui "
           f"commande son avance, donc ses deux moitiés séparent ensemble dans "
           f"{reg[1].get('les_deux_separent', 0)} marches.", moyen, ENCRE)

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
    v("aucun texte ne sort de son cadre", not textes_hors_cadre(poses, cadres),
      str(textes_hors_cadre(poses, cadres))[:180])
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
    # ⚠⚠ UNE VALEUR D'ÉPREUVE DOIT ÊTRE DISCRIMINANTE : « 88 » se trouve déjà dans « 0.88 » ou
    # dans un compte, donc l'épreuve porte sur un nombre que la mesure ne produit pas.
    faux = copy.deepcopy(d)
    faux["juger"]["le_controle_de_la_spirale_nue"]["cases_appariables"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_est_vide"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    for g in faux2["juger"]["par_regle"]:
        g["la_tangente_est_egale"] = 7777
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐ ... et le compte des tangentes EXACTEMENT égales est LU, pas supposé",
      any("7777" in t for _x, _y, t, _f in p3))
    faux3 = copy.deepcopy(d)
    for g in faux3["juger"]["par_regle"]:
        g["rapport_normal_median"] = 66.66
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐ ... et le facteur médian du recentrage aussi",
      any("66.66" in t for _x, _y, t, _f in p4))
    # ⚠⚠⚠ DEUX CALCULS D'UN MÊME VERDICT NE S'ACCORDENT PAS : la figure LIT `le_verdict_par_bras`,
    # elle ne le recalcule jamais depuis les comptes.
    faux4 = copy.deepcopy(d)
    faux4["juger"]["le_verdict_par_bras"] = {k: "une troisième moitié"
                                             for k in d["juger"]["le_verdict_par_bras"]}
    _c, p5, _cd, _pt = dessiner(faux4, sortie)
    v("⭐⭐⭐⭐ le verdict par bras est LU du jugement, jamais recalculé par la figure",
      any("une troisième moitié" in t for _x, _y, t, _f in p5)
      and not any("une troisième moitié" in t for _x, _y, t, _f in poses))

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_161.json"
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
    v("⚠⚠ une mesure sans verdict PAR BRAS est REFUSÉE, jamais retombée sur un verdict global",
      refuse(lambda x: x["juger"].pop("le_verdict_par_bras")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "de_quoi_un_pas_qui_saute_est_il_fait.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "161_de_quoi_un_pas_qui_saute_est_il_fait.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
