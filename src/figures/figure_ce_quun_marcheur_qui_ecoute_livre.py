"""Ce qu'un marcheur qui écoute livre.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, le contrôle et l'invariant : sur
la spirale nue l'oreille ne change rien, et toute marche qui écoute est un préfixe de celle qui
n'écoute pas. En haut à droite, ce qu'elle achète — les livraisons contaminées, avant et après. En
bas à gauche, la longueur UTILISABLE matière par matière. En bas à droite, ce qu'elle coûte.

  uv run python src/figures/figure_ce_quun_marcheur_qui_ecoute_livre.py \\
      --json docs/mesures/ce_quun_marcheur_qui_ecoute_livre.json \\
      --sortie docs/images/164_ce_quun_marcheur_qui_ecoute_livre.png
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
    """Le JSON de `ce_quun_marcheur_qui_ecoute_livre.py`.

    ⚠⚠ Refuse une mesure sans le contrôle, et sans l'invariant de préfixe : c'est lui qui interdit
    qu'une marche devienne fausse en s'arrêtant, donc qui rend toute la comparaison lisible.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if "message" in d:
        raise ValueError(f"{chemin} : {d['message']}")
    j = d.get("juger", {})
    if not j.get("decidable"):
        raise ValueError(f"{chemin} : {j.get('raison', 'le jugement est indécidable')}")
    if not j.get("par_bras") or not j.get("par_matiere"):
        raise ValueError(f"{chemin} : aucun groupe jugé")
    if j.get("le_controle_de_la_spirale_nue", {}).get("il_est_neutre") is None:
        raise ValueError(f"{chemin} : le contrôle de la spirale nue est absent")
    if "toute_marche_qui_ecoute_est_un_prefixe" not in j:
        raise ValueError(f"{chemin} : l'invariant de préfixe est absent")
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
    bras, mat = j["par_bras"], j["par_matiere"]
    c = j["le_controle_de_la_spirale_nue"]
    hors = j.get("ce_que_loreille_achete_par_bras_hors_controle", {})

    ecrire(28, 20, "Ce qu'un marcheur qui ÉCOUTE livre — la règle de `163`, branchée pour de bon",
           gros, ENCRE)
    ecrire(28, 46, "une trajectoire dont on ignore où elle a cessé d'être vraie n'est pas à moitié "
                   "bonne : elle est inutilisable EN ENTIER, faute de savoir où la couper",
           petit, GRIS)

    # ---- panneau 1 : le controle et l'invariant
    x0, y0, pw, ph = 56, 122, 620, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le contrôle, et l'invariant qui rend la comparaison lisible", moyen, ENCRE)
    marque = "★" if c["il_est_neutre"] else "✗"
    ecrire(x0 + 14, y0 + 22, f"{marque}  {c['nom']} — l'oreille n'y change RIEN", moyen,
           BON if c["il_est_neutre"] else ALERTE)
    ecrire(x0 + 14, y0 + 54,
           f"{c['livraisons_arretees_sur_la_pose']} marche arrêtée sur la pose", petit, ENCRE)
    ecrire(x0 + 14, y0 + 72,
           f"{c['pas_livres_sans']} pas livrés sans l'oreille, {c['pas_livres_avec']} avec",
           petit, ENCRE)
    inv = j["toute_marche_qui_ecoute_est_un_prefixe"]
    ecrire(x0 + 14, y0 + 104, f"{'★' if inv else '✗'}  toute marche qui écoute est un PRÉFIXE",
           moyen, BON if inv else ALERTE)
    ecrire(x0 + 14, y0 + ph - 96,
           "même fixture, même suiveur, arrêt plus tôt : une marche qui", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 80,
           "écoute ne peut donc pas devenir FAUSSE en s'arrêtant. Le gain", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 64,
           "en fiabilité est acquis par construction, donc le compter comme", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 48,
           "une victoire serait un contrôle incapable d'échouer.", petit, GRIS)
    ecrire(x0 + 14, y0 + ph - 22,
           "le seul axe qui puisse échouer est la LONGUEUR perdue", petit, ALERTE)

    # ---- panneau 2 : les livraisons contaminees
    x0, y0, pw, ph = 712, 122, 592, 256
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que l'oreille achète — les livraisons contaminées", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 120
    barre_max = pw - 240
    for k, g in enumerate(bras):
        base = y0 + 28 + k * 78
        ecrire(x_nom, base - 18, f"{_court(g['nom'])} — {g['apparies']} départs", petit, ENCRE)
        for i, (cle, coul, quoi) in enumerate(
                (("livraisons_qui_sautent_sans", ALERTE, "sans"),
                 ("livraisons_qui_sautent_avec", BON, "avec"))):
            yy = base + i * 22
            n = int(g[cle])
            w = (n / max(g["apparies"], 1)) * barre_max
            ecrire(x_nom, yy - 1, quoi, 0, GRIS)
            art.rectangle([x_barre, yy, x_barre + barre_max, yy + 14], fill=TRAIT)
            if n:
                art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 14], fill=coul)
            points.append((x_barre + w, yy + 7))
            ecrire(x_barre + barre_max + 8, yy - 1, f"{n}/{g['apparies']}", 0, coul)
    ecrire(x0 + 12, y0 + ph - 38,
           "ambre : ce qu'un marcheur SOURD remet sans le savoir", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "vert : ce qui reste contaminé malgré l'oreille", petit, ENCRE)

    # ---- panneau 3 : la longueur UTILISABLE
    x0, y0, pw, ph = 56, 444, 620, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la longueur UTILISABLE, matière par matière", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 250
    vmax = max(max(g["pas_utilisables_sans"], g["pas_utilisables_avec"]) for g in mat) or 1
    pas_bloc = max((ph - 72) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        base = y0 + 20 + k * pas_bloc
        ecrire(x_nom, base + 8, _court(g["nom"]), petit, ENCRE)
        for i, (cle, coul) in enumerate((("pas_utilisables_sans", TEMOIN),
                                         ("pas_utilisables_avec", BON))):
            yy = base + i * 16
            w = (int(g[cle]) / vmax) * barre_max
            if int(g[cle]):
                art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 13], fill=coul)
            points.append((x_barre + w, yy + 6))
        r_ = g["ce_que_loreille_achete"]
        ecrire(x_barre + barre_max + 8, base + 8,
               "—" if r_ is None else f"×{r_:g}", 0, BON if (r_ or 0) >= 1.0 else ALERTE)
    ecrire(x0 + 12, y0 + ph - 38,
           "gris : sans l'oreille · vert : avec — une livraison contaminée vaut ZÉRO", petit, GRIS)
    ecrire(x0 + 12, y0 + ph - 20,
           "sur la matière du rouleau, presque tout était contaminé : il ne restait rien",
           petit, ALERTE)

    # ---- panneau 4 : le prix
    x0, y0, pw, ph = 712, 444, 592, 300
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce qu'elle coûte — les départs raccourcis pour rien", moyen, ENCRE)
    x_nom, x_barre = x0 + 12, x0 + 128
    barre_max = pw - 270
    pas_bloc2 = max((ph - 96) // max(len(mat), 1), 36)
    for k, g in enumerate(mat):
        yy = y0 + 24 + k * pas_bloc2
        ecrire(x_nom, yy, _court(g["nom"]), petit, ENCRE)
        n = int(g["departs_raccourcis_pour_rien"])
        w = (n / max(g["apparies"], 1)) * barre_max
        art.rectangle([x_barre, yy, x_barre + barre_max, yy + 13], fill=TRAIT)
        if n:
            art.rectangle([x_barre, yy, x_barre + max(w, 1), yy + 13], fill=CONTRE)
        points.append((x_barre + w, yy + 6))
        # ⚠⚠⚠ LA MEDIANE DU COUT, pas celle de TOUS les arrets : ce panneau demande ce que
        # coutent les marches coupees POUR RIEN, et une marche sauvee n'a rien perdu.
        pe = g.get("pas_perdus_pour_rien_median")
        ecrire(x_barre + barre_max + 8, yy,
               f"{n}/{g['apparies']}" + ("" if pe is None else f"  -{pe}"), 0,
               CONTRE if n else BON)
    ecrire(x0 + 12, y0 + ph - 74, "et le rapport par bras, avec et sans le contrôle :", petit, GRIS)
    for k, g in enumerate(bras):
        ecrire(x0 + 26, y0 + ph - 56 + k * 18,
               f"{_court(g['nom'])} : ×{g['ce_que_loreille_achete']}  "
               f"hors contrôle ×{hors.get(g['nom'])}", 0, ENCRE)
    ecrire(x0 + 12, y0 + ph - 18,
           "la spirale nue livre autant des DEUX côtés : elle tire le rapport vers un",
           petit, ALERTE)

    # ---- bande
    y = 772
    art.rectangle([56, y, L - 56, y + 130], fill=BANDE)
    cadres.append((56, y, L - 56, y + 130))
    pince = bras[0]
    dure = mat[-1]
    ecrire(74, y + 12,
           f"★★★★  Sur la pince, les livraisons contaminées tombent de "
           f"{pince['livraisons_qui_sautent_sans']} à {pince['livraisons_qui_sautent_avec']} "
           f"sur {pince['apparies']} départs.", moyen, ENCRE)
    ecrire(74, y + 38,
           f"★★★★  Et sur la matière du ROULEAU, l'oreille multiplie la sortie utilisable par "
           f"{dure['ce_que_loreille_achete']} : de {dure['pas_utilisables_sans']} pas à "
           f"{dure['pas_utilisables_avec']}.", moyen, BON)
    ecrire(74, y + 64,
           f"✗  Elle le paie où il n'y avait rien à sauver : "
           f"{pince['departs_raccourcis_pour_rien']} départs raccourcis pour rien sur la pince, "
           f"médiane {pince['pas_perdus_median']} pas.", moyen, ALERTE)
    ecrire(74, y + 90,
           "⚠  Un marcheur SOURD ne livre pas une trajectoire à moitié bonne : il en livre une "
           "dont il ignore où elle a cessé d'être vraie.", moyen, ENCRE)
    ecrire(74, y + 110,
           "⚠⚠  C'est pour ça qu'une livraison contaminée compte ZÉRO, et c'est ce qui rend le "
           "gain sur la matière du rouleau si grand.", moyen, ENCRE)

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
    faux["juger"]["le_controle_de_la_spirale_nue"]["pas_livres_avec"] = 8888
    faux["juger"]["le_controle_de_la_spirale_nue"]["il_est_neutre"] = False
    _c, p2, _cd, _pt = dessiner(faux, sortie)
    v("⭐⭐⭐ un contrôle qui TOMBE change ce que la figure dit, et sa couleur",
      any("8888" in t for _x, _y, t, _f in p2)
      and not any("8888" in t for _x, _y, t, _f in poses))
    faux2 = copy.deepcopy(d)
    faux2["juger"]["toute_marche_qui_ecoute_est_un_prefixe"] = False
    _c, p3, _cd, _pt = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ l'invariant de préfixe est LU du jugement, et sa chute se voit",
      sum("★" in t for _x, _y, t, _f in p3) < sum("★" in t for _x, _y, t, _f in poses),
      "s'il tombe, l'arrêt a changé la marche au lieu de la couper")
    faux3 = copy.deepcopy(d)
    for g in faux3["juger"]["par_matiere"]:
        g["ce_que_loreille_achete"] = 77.77
    _c, p4, _cd, _pt = dessiner(faux3, sortie)
    v("⭐⭐⭐ ... et le rapport est LU, pas recalculé par la figure",
      any("77.77" in t for _x, _y, t, _f in p4))
    # ⚠⚠⚠ LE RAPPORT HORS CONTROLE EST DESSINE A COTE DE CELUI QUI L'INCLUT : les taire tous les
    # deux laisserait lire un rapport dilue par son propre controle.
    valeurs = [str(v_) for v_ in
               d["juger"]["ce_que_loreille_achete_par_bras_hors_controle"].values()
               if v_ is not None]
    tous = [t for _x, _y, t, _f in poses]
    v("⭐⭐⭐⭐ le rapport HORS CONTRÔLE est dessiné à côté de celui qui l'inclut",
      all(any(v_ in t for t in tous) for v_ in valeurs), f"{valeurs}")

    def refuse(mutation) -> bool:
        cassee = copy.deepcopy(d)
        mutation(cassee)
        tmp = sortie.parent / "_casse_164.json"
        tmp.write_text(json.dumps(cassee, ensure_ascii=False))
        try:
            lire(tmp)
            return False
        except ValueError:
            return True
        finally:
            tmp.unlink(missing_ok=True)

    v("⚠ une mesure sans le contrôle est REFUSÉE",
      refuse(lambda x: x["juger"].pop("le_controle_de_la_spirale_nue")))
    v("⚠⚠ une mesure sans l'invariant de préfixe est REFUSÉE",
      refuse(lambda x: x["juger"].pop("toute_marche_qui_ecoute_est_un_prefixe")))

    dessiner(d, sortie)
    print(f"\n{'ALL PASS' if not echecs else '⛔ ECHEC'} ({echecs} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path,
                    default=RACINE / "docs" / "mesures"
                    / "ce_quun_marcheur_qui_ecoute_livre.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs" / "images"
                    / "164_ce_quun_marcheur_qui_ecoute_livre.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, _p, _c, _pt = dessiner(lire(a.json), a.sortie)
    print(chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
