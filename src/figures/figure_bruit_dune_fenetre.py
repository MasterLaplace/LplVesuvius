#!/usr/bin/env python3
"""Ce qui sépare deux fragments, et ce qui sépare deux tuiles du même fragment.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le résultat de
[`64`](../../docs/archive/64_la_dispersion_netait_pas_un_effet.md) est un rapport entre deux
dispersions, et un rapport se raconte mal en prose : « 0,2243 contre 0,0391 » se lit comme
deux nombres alors que c'est **six fois**. Le panneau de gauche le montre sans qu'aucun
chiffre soit nécessaire — les nuages de tuiles d'un même fragment sont plus larges que
l'écart entre les fragments eux-mêmes.

⭐ Deux questions, pas une. À gauche : « les trois fragments sont-ils séparés ? » — non, les
intervalles se recouvrent. À droite : « de combien de tuiles aurait-on eu besoin ? » — le
compte, contre celui qu'on avait. La seconde est celle qui rend le résultat utile : elle
transforme une déception en règle de campagne.

⚠ Les nombres sont LUS dans `docs/mesures/bruit_dune_fenetre.json`, jamais retapés.

Usage :
    uv run python src/figures/figure_bruit_dune_fenetre.py --verifier
    uv run python src/figures/figure_bruit_dune_fenetre.py \\
        --mesure docs/mesures/bruit_dune_fenetre.json \\
        --sortie docs/images/64_bruit_dune_fenetre.png
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)

PLANCHER_MAX, HAUT = 0.30, 1.00
"""Les bornes de l'axe des AUC.

⚠⚠ Le HAUT est fixe à 1,0 et le plancher **descend si les données descendent**, jamais
l'inverse. Un axe ajusté des deux côtés ferait paraître énorme n'importe quelle dispersion,
y compris une dispersion nulle — c'est la façon la plus courante de faire mentir un
graphique sans écrire un seul chiffre faux. Un plancher qui ne descend jamais a le défaut
opposé, payé ici à la première image : **quatre tuiles tombaient hors du cadre**, dont celle
qui porte l'AUC la plus basse du jeu. Laisser une donnée dehors est pire que la montrer.

⭐ Étendre le plancher ne peut que **rétrécir** la dispersion apparente, donc cette
souplesse-là ne flatte jamais le résultat. Et 0,5, la valeur du hasard, reste toujours
visible : c'est la seule graduation qui a un sens hors de ce jeu.
"""


def lire(chemin: Path) -> dict:
    """Charge la mesure de bruit de fenêtre et valide sa structure minimale.

    Refuse si le fichier manque ou ne porte pas les fragments ou la variance.
    """
    if not chemin.is_file():
        raise FileNotFoundError(f"mesure absente : {chemin}")
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("fragments"):
        raise ValueError(f"{chemin} ne porte aucun fragment")
    if "variance" not in d:
        raise ValueError(f"{chemin} ne porte pas de données de variance")
    return d


def echelle(valeur: float, lo: float, hi: float, pixels: int) -> int:
    """Une valeur de l'axe, en pixels depuis son origine."""
    if hi <= lo:
        return 0
    return int(round((valeur - lo) / (hi - lo) * pixels))


def bornes(mesure: dict) -> tuple[float, float]:
    """Le plancher de l'axe : au plus 0,30, plus bas si une tuile descend plus bas."""
    valeurs = [t["auc"] for f in mesure["fragments"].values() for t in f["tuiles"]]
    valeurs += [f["auc_groupee"] for f in mesure["fragments"].values()]
    valeurs += [f["bootstrap"]["ic_bas"] for f in mesure["fragments"].values()
                if f.get("bootstrap", {}).get("exploitable")]
    plancher = min([PLANCHER_MAX] + valeurs) if valeurs else PLANCHER_MAX
    return (int(plancher * 20) / 20.0 - 0.05, HAUT)


def prose(mesure: dict) -> list[str]:
    """Ce que la figure dit en toutes lettres, pour qu'un lecteur pressé ne devine pas."""
    v = mesure["variance"]
    return [
        f"la dispersion DANS un fragment vaut {v['ecart_type_intra']:.3f},",
        f"celle ENTRE fragments {v['ecart_type_inter']:.3f} : "
        f"{v['ecart_type_intra'] / max(v['ecart_type_inter'], 1e-9):.1f} fois moins.",
        f"savoir de quel fragment vient une tuile explique {v['icc'] * 100:.0f} % de l'ecart.",
    ]


def dessiner(mesure: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import ImageDraw

    gros, moyen, petit = police(16, 13, 12)
    frags = mesure.get("fragments") or {}
    if not frags:
        raise ValueError("aucun fragment à dessiner")
    v = mesure["variance"]

    bas, haut = bornes(mesure)

    L, H = 1180, 560
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    # ---- PANNEAU GAUCHE : chaque tuile, un point --------------------------------------
    gx, gy, gw, gh = 90, 96, 470, 340
    ecrire(70, 34, "une tuile, un point", gros, TEXTE)
    ecrire(70, 56, "AUC de chaque tuile de 256 px, par fragment", moyen, DISCRET)
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=(60, 60, 60))
    # ⚠ Les graduations tombent sur des dixiemes ronds, pas sur `bas + 0,05` : la premiere
    # version partait du plancher et rendait « 0.8 » deux fois de suite avec « 0.4 » manquant,
    # parce que `{:.1f}` arrondit deux graduations distantes de 0,1 au meme libelle quand
    # elles sont decalees d'un demi-dixieme.
    val = round(bas + (0.1 - bas % 0.1) % 0.1, 10)
    if val <= bas + 1e-9:
        val = round(val + 0.1, 10)
    while val < HAUT:
        yy = gy + gh - echelle(val, bas, haut, gh)
        couleur = (70, 70, 70) if abs(val - 0.5) < 1e-9 else (36, 36, 36)
        d.line([gx, yy, gx + gw, yy], fill=couleur)
        ecrire(gx - 42, yy - 7, f"{val:.1f}", petit, DISCRET)
        val = round(val + 0.1, 10)
    # ⚠ « hasard » va DANS le panneau, a droite : place dans la marge il recouvrait la
    # graduation 0,5 elle-meme, c'est-a-dire la seule que le lecteur doit pouvoir lire.
    ecrire(gx + gw - 50, gy + gh - echelle(0.5, bas, haut, gh) - 16, "hasard",
           petit, DISCRET)

    colonne = gw // max(len(frags), 1)
    for i, (nom, f) in enumerate(frags.items()):
        cx = gx + colonne * i + colonne // 2
        b = f.get("bootstrap", {})
        # ⚠ L'intervalle est dessine AVANT les points : recouvert par eux, il donnerait
        # l'impression d'une barre d'erreur ajoutee apres coup sur des donnees choisies.
        if b.get("exploitable"):
            y1 = gy + gh - echelle(b["ic_haut"], bas, haut, gh)
            y2 = gy + gh - echelle(b["ic_bas"], bas, haut, gh)
            d.rectangle([cx - 26, y1, cx + 26, y2], fill=(34, 30, 24))
            d.line([cx - 26, y1, cx + 26, y1], fill=AMBRE)
            d.line([cx - 26, y2, cx + 26, y2], fill=AMBRE)
        # ⚠ Les tuiles sont decalees horizontalement par leur rang, jamais au hasard :
        # une figure doit rendre les memes pixels a chaque execution.
        for j, t in enumerate(f["tuiles"]):
            px = cx - 20 + (j % 5) * 10
            py = gy + gh - echelle(t["auc"], bas, haut, gh)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GRIS)
        yg = gy + gh - echelle(f["auc_groupee"], bas, haut, gh)
        d.line([cx - 34, yg, cx + 34, yg], fill=ROUGE, width=2)
        ecrire(cx - 30, gy + gh + 10, nom, moyen, TEXTE)
        ecrire(cx - 30, gy + gh + 28, f"{len(f['tuiles'])} tuiles", petit, DISCRET)

    d.line([gx + 8, gy + 14, gx + 28, gy + 14], fill=ROUGE, width=2)
    ecrire(gx + 34, gy + 7, "AUC groupee publiee", petit, ROUGE)
    d.rectangle([gx + 8, gy + 32, gx + 28, gy + 42], fill=(34, 30, 24), outline=AMBRE)
    ecrire(gx + 34, gy + 30, "IC 95 %, bootstrap par tuiles", petit, AMBRE)

    # ---- PANNEAU DROIT : les deux dispersions, puis le compte qu'il fallait ------------
    bx, by, bw = 660, 96, 430
    ecrire(650, 34, "ce que la dispersion mesure vraiment", gros, TEXTE)
    ecrire(650, 56, "ecart-type des AUC de tuiles", moyen, DISCRET)
    pire = max(v["ecart_type_intra"], v["ecart_type_inter"]) * 1.25
    for i, (nom, valeur, couleur) in enumerate(
            (("DANS un fragment, de tuile a tuile", v["ecart_type_intra"], AMBRE),
             ("ENTRE fragments", v["ecart_type_inter"], GRIS))):
        yy = by + 34 + i * 84
        largeur = echelle(valeur, 0.0, pire, bw)
        d.rectangle([bx, yy, bx + max(largeur, 2), yy + 34], fill=couleur)
        ecrire(bx, yy - 20, nom, moyen, TEXTE)
        ecrire(bx + max(largeur, 2) + 10, yy + 10, f"{valeur:.4f}", moyen, couleur)

    ecrire(bx, by + 210, f"part attribuable au fragment : {v['icc'] * 100:.0f} %",
           gros, ROUGE)
    for k, ligne in enumerate(prose(mesure)):
        ecrire(bx, by + 240 + k * 20, ligne, moyen, TEXTE)

    besoin = mesure.get("tuiles_pour_distinguer", 0)
    if besoin:
        ecrire(bx, by + 320, "combien de tuiles il aurait fallu", gros, TEXTE)
        ecrire(bx, by + 346,
               f"pour etablir l'ecart observe de {mesure['ecart_observe']:.3f} : "
               f"{besoin} par fragment", moyen, AMBRE)
        eus = ", ".join(str(len(f["tuiles"])) for f in frags.values())
        ecrire(bx, by + 366, f"on en avait {eus}.", moyen, ROUGE)
        ecrire(bx, by + 386, "et c'est un minorant : deux tuiles voisines",
               moyen, DISCRET)
        ecrire(bx, by + 406, "ne sont pas independantes.", moyen, DISCRET)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    cadres = [(gx, gy, gx + gw, gy + gh), (bx, by, bx + bw, by + 440)]
    return sortie, poses, cadres


def verifier() -> int:
    """Auto-test HORS LIGNE : les axes, la prose, la figure et les sondes."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # -- echelle : bornes, monotonie, et le cas degenere.
    v("le bas de l'axe est a zero pixel", echelle(0.3, 0.3, HAUT, 300) == 0)
    v("le haut de l'axe est en butee", echelle(HAUT, 0.3, HAUT, 300) == 300)
    v("le milieu est au milieu", echelle(0.65, 0.3, HAUT, 300) == 150)
    v("un axe degenere ne divise pas par zero", echelle(0.5, 0.5, 0.5, 300) == 0)

    faux = {
        "variance": {"exploitable": True, "ecart_type_intra": 0.2243,
                     "ecart_type_inter": 0.0391, "icc": 0.030},
        "ecart_observe": 0.171,
        "tuiles_pour_distinguer": 27,
        "fragments": {
            "a": {"auc_groupee": 0.75, "tuiles": [{"auc": 0.6}, {"auc": 0.8}],
                  "bootstrap": {"exploitable": True, "ic_bas": 0.55, "ic_haut": 0.85}},
            "b": {"auc_groupee": 0.60, "tuiles": [{"auc": 0.5}, {"auc": 0.7}],
                  "bootstrap": {"exploitable": True, "ic_bas": 0.45, "ic_haut": 0.75}},
        },
    }
    # ⚠⚠ LES CONTROLES QUI PORTENT LA FIGURE, et le premier vient d'un vrai defaut :
    # la premiere image laissait QUATRE tuiles hors du cadre, dont la plus basse du jeu.
    bas_faux, haut_faux = bornes(faux)
    v("l'axe englobe la valeur du hasard", bas_faux < 0.5 < haut_faux,
      f"[{bas_faux} ; {haut_faux}]")
    v("... et une AUC parfaite", haut_faux >= 1.0)
    v("... et aucune tuile ne tombe hors du cadre",
      all(bas_faux <= t["auc"] <= haut_faux
          for f in faux["fragments"].values() for t in f["tuiles"]))
    bas_faux2 = dict(faux)
    bas_faux2["fragments"] = {"a": {"auc_groupee": 0.5, "tuiles": [{"auc": 0.12}],
                                    "bootstrap": {"exploitable": False}}}
    b2, h2 = bornes(bas_faux2)
    v("une tuile tres basse fait descendre le plancher", b2 <= 0.12, f"{b2}")
    v("... et le haut ne bouge pas pour autant", h2 == HAUT, f"{h2}")
    # ⚠ Le plancher ne REMONTE jamais au-dessus de 0,30, sinon un jeu tres resserre
    # occuperait tout le cadre et paraitrait disperse.
    haut_perche = dict(faux)
    haut_perche["fragments"] = {"a": {"auc_groupee": 0.9, "tuiles": [{"auc": 0.91}],
                                      "bootstrap": {"exploitable": False}}}
    v("un jeu resserre ne fait pas remonter le plancher",
      bornes(haut_perche)[0] <= PLANCHER_MAX, str(bornes(haut_perche)[0]))

    # ⚠⚠ ET LE CONTROLE DU DEFAUT REELLEMENT PAYE : deux graduations ne doivent jamais
    # porter le meme libelle. La premiere image affichait « 0.8 » deux fois.
    for plancher in (0.0, 0.05, 0.12, 0.3, 0.47):
        val, libelles = round(plancher + (0.1 - plancher % 0.1) % 0.1, 10), []
        if val <= plancher + 1e-9:
            val = round(val + 0.1, 10)
        while val < HAUT:
            libelles.append(f"{val:.1f}")
            val = round(val + 0.1, 10)
        v(f"les graduations sont distinctes depuis un plancher de {plancher}",
          len(libelles) == len(set(libelles)), str(libelles))

    lignes = prose(faux)
    v("la prose est tracable", prose_tracable(lignes), str(lignes))
    v("... et elle dit le rapport, pas seulement les deux nombres",
      any("fois moins" in l for l in lignes), str(lignes))
    # ⚠ Le rapport est recalcule ici a la main : 0,2243 / 0,0391 = 5,7. Ecrire le nombre
    # attendu ailleurs que dans le code teste est ce qui rend le controle capable d'echouer.
    v("... et le rapport vaut bien 5,7", any("5.7 fois moins" in l for l in lignes),
      str(lignes))
    v("... et le pourcentage est arrondi a l'entier",
      any("3 %" in l for l in lignes), str(lignes))

    # -- une mesure sans dispersion inter ne doit pas faire diviser par zero.
    plat = json.loads(json.dumps(faux))
    plat["variance"]["ecart_type_inter"] = 0.0
    v("une dispersion inter nulle ne casse pas la prose", len(prose(plat)) == 3)

    with tempfile.TemporaryDirectory() as d:
        rac = Path(d)
        f_mesure = rac / "m.json"
        f_mesure.write_text(json.dumps(faux), encoding="utf-8")

        lu = lire(f_mesure)
        v("le JSON complet est lu", len(lu["fragments"]) == 2 and "variance" in lu)

        out_img, poses, cadres = dessiner(lu, rac / "f.png")
        v("l'image est écrite", out_img.is_file())
        v("... et elle n'est pas vide", out_img.stat().st_size > 1000)

        im = Image.open(out_img).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0] == 1180)
        v("... et sa hauteur est celle annoncée", im.size[1] == 560)

        pixels = list(im.getdata())
        v("... et elle porte les couleurs requises",
          AMBRE in pixels and ROUGE in pixels)

        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]) == [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres) == [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses) == [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]] == [])

        # ⚠ Sonde : un fichier manquant est refusé
        try:
            lire(rac / "inexistant.json")
            v("sonde : un fichier manquant est refusé", False)
        except FileNotFoundError:
            v("sonde : un fichier manquant est refusé", True)

        # ⚠ Sonde : un JSON sans fragments est refusé
        f_invalide = rac / "invalide.json"
        f_invalide.write_text(json.dumps({"variance": {}}), encoding="utf-8")
        try:
            lire(f_invalide)
            v("sonde : un JSON sans fragments est refusé", False)
        except ValueError:
            v("sonde : un JSON sans fragments est refusé", True)

        # ⚠ Sonde : un JSON sans fragments est refusé par dessiner
        try:
            dessiner({"fragments": {}, "variance": {}}, rac / "vide.png")
            v("sonde : dessiner sans fragments est refusé", False)
        except ValueError:
            v("sonde : dessiner sans fragments est refusé", True)

        # ⚠ Sonde : la garde attrape un texte débordant simulé
        trop_long = [(1100, 50, "Texte debordant de la toile de onze cents pixels", police(16))]
        v("sonde : textes_debordants détecte le dépassement",
          len(textes_debordants(trop_long, 1180)) > 0)

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--mesure", type=Path,
                   default=RACINE / "docs" / "mesures" / "bruit_dune_fenetre.json")
    # ⚠ Chemin en UNE chaine, comme le reste du depot : `fraicheur_des_figures` lit la
    # declaration par expression reguliere, et la forme segmentee lui echappait -- la figure
    # passait alors pour « sans sortie declaree », donc pour non jugeable, en silence.
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs/images/64_bruit_dune_fenetre.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    mesure = lire(a.mesure)
    out, _, _ = dessiner(mesure, a.sortie)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"écrit : {cible}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
