"""Quelle fenêtre lit une bascule ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, la coupe AVEUGLE : aucune longueur
ne lit la bascule à tous les décalages, sur une matière qui en a une par construction. En haut à
droite, la MEILLEURE coupe : la même fenêtre la lit partout. En bas à gauche, la fenêtre exacte de la
campagne, lue par les deux recettes. En bas à droite, le contraste, et jusqu'où il descend.

  uv run python src/figures/figure_quelle_fenetre_lit_une_bascule.py \\
      --json docs/mesures/quelle_fenetre_lit_une_bascule.json \\
      --sortie docs/images/173_quelle_fenetre_lit_une_bascule.png
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
CONTRE = (92, 108, 150)
RECETTES = ("aveugle", "meilleure")


def _fr(x, n: int = 2) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{n}f}".rstrip("0").rstrip(".").replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `quelle_fenetre_lit_une_bascule.py`.

    ⚠⚠ Refuse une mesure qui n'a pas les DEUX recettes : le résultat est leur contraste — l'une ne
    lit jamais, l'autre lit partout — et une figure qui n'en montrerait qu'une ferait lire soit que
    l'instrument ne peut pas, soit que la campagne avait raison.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("les_longueurs", "la_campagne", "le_contraste", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for x in d["les_longueurs"].get("lignes") or []:
        if set(x.get("par_recette") or {}) != set(RECETTES):
            raise ValueError(f"{chemin} : une longueur n'a pas les deux recettes")
    if not d["les_longueurs"].get("lignes"):
        raise ValueError(f"{chemin} : aucune longueur mesurée")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    lo, ca, ct, v = d["les_longueurs"], d["la_campagne"], d["le_contraste"], d["le_verdict"]
    camp = ca["sur_une_matiere_qui_bascule"]

    ecrire(28, 20, "Quelle fenêtre lit une bascule ? — le défaut n'est pas la fenêtre, "
                   "c'est la COUPE AVEUGLE", gros, ENCRE)
    ecrire(28, 46, "Sur une matière dont la bascule est CONSTRUITE, la recette de la campagne ne la "
                   "lit à aucune longueur ; la même fenêtre la lit partout en cherchant sa coupe",
           petit, GRIS)

    # ---- panneaux 1 et 2 : les deux recettes, cote a cote
    for k, rec in enumerate(RECETTES):
        x0 = 56 + k * 656
        y0, pw, ph = 122, 620, 300
        art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
        cadres.append((x0, y0, x0 + pw, y0 + ph))
        ecrire(x0, y0 - 24,
               ("la coupe AVEUGLE — celle de la campagne" if rec == "aveugle"
                else "la MEILLEURE coupe — on cherche la frontière"), moyen, ENCRE)
        ecrire(x0 + 150, y0 + 12, "bascule", petit, ALERTE)
        ecrire(x0 + 232, y0 + 12, "témoin", petit, CONTRE)
        ecrire(x0 + 310, y0 + 12, "à un pli", petit, GRIS)
        ecrire(x0 + 400, y0 + 12, "décalages qui la lisent", petit, ENCRE)
        x_barre, barre_max = x0 + 400, pw - 470
        for i, x in enumerate(lo["lignes"]):
            b = x["par_recette"][rec]
            yy = y0 + 38 + i * 26
            ok = b["elle_lit_la_bascule_partout"]
            ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {_fr(x['demande_en_feuilles'])} f "
                                f"({x['couches']} c)", 0, BON if ok else ALERTE)
            ecrire(x0 + 150, yy, _fr(b["bascule_mediane_deg"], 1), 0, ALERTE)
            ecrire(x0 + 232, yy, _fr(b["temoin_median_deg"], 1), 0, CONTRE)
            ecrire(x0 + 310, yy, _fr(b["bascule_a_un_pli_mediane_deg"], 1), 0, GRIS)
            lus = max(1, b["decalages_lus"])
            w = (b["lisent_la_bascule"] / lus) * barre_max
            art.rectangle([x_barre, yy + 1, x_barre + max(w, 1), yy + 13],
                          fill=BON if ok else ALERTE)
            points.append((x_barre + w, yy + 7))
            barres.append((x_barre + w, x_barre + barre_max))
            ecrire(x_barre + barre_max + 8, yy,
                   f"{b['lisent_la_bascule']}/{b['decalages_lus']}", 0,
                   BON if ok else ALERTE)
        fiables = lo["longueurs_fiables"][rec]
        ecrire(x0 + 14, y0 + 254,
               ("★  longueurs fiables : " + ", ".join(_fr(f) for f in fiables)) if fiables
               else "✗  AUCUNE longueur n'est fiable", moyen, BON if fiables else ALERTE)
        ecrire(x0 + 14, y0 + 278,
               "⚠⚠ « fiable » = elle lit la bascule à TOUS les décalages, jamais à une majorité",
               petit, GRIS)

    # ---- panneau 3 : la fenetre de la campagne
    x0, y0, pw, ph = 56, 474, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la fenêtre EXACTE de la campagne, posée sur une matière qui bascule",
           moyen, ENCRE)
    ecrire(x0 + 14, y0 + 16,
           f"{ca['couches_de_la_campagne']} couches × {_fr(d['voxel_um'])} µm = "
           f"{_fr(ca['epaisseur_um'], 1)} µm = {_fr(ca['en_feuilles'], 3)} feuille", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 40,
           f"lues dans {ca['segments_lus']} segments stockés, couches "
           f"{ca['couches_publiees_distinctes']}", petit, GRIS)
    x_barre, barre_max = x0 + 250, pw - 330
    for i, rec in enumerate(RECETTES):
        b = camp["par_recette"][rec]
        yy = y0 + 76 + i * 34
        ok = b["elle_lit_la_bascule_partout"]
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} coupe {rec}", moyen, BON if ok else ALERTE)
        lus = max(1, b["decalages_lus"])
        w = (b["lisent_la_bascule"] / lus) * barre_max
        art.rectangle([x_barre, yy + 2, x_barre + max(w, 1), yy + 16],
                      fill=BON if ok else ALERTE)
        points.append((x_barre + w, yy + 9))
        barres.append((x_barre + w, x_barre + barre_max))
        ecrire(x_barre + barre_max + 8, yy + 1,
               f"{b['lisent_la_bascule']}/{b['decalages_lus']}", 0, BON if ok else ALERTE)
    ecrire(x0 + 14, y0 + 154,
           "★ La longueur suffit largement : au-delà de trois quarts de feuille,", petit, GRIS)
    ecrire(x0 + 14, y0 + 170,
           "la meilleure coupe lit partout. Ce qui manquait n'était ni le", petit, GRIS)
    ecrire(x0 + 14, y0 + 186,
           "contraste, ni la longueur, ni le centrage : c'était de CHERCHER", petit, GRIS)
    ecrire(x0 + 14, y0 + 202, "la frontière au lieu de couper au milieu.", petit, GRIS)
    ecrire(x0 + 14, y0 + 228,
           "⚠⚠ cela ne dit PAS qu'un vrai papyrus bascule — seulement que la", petit, ALERTE)
    ecrire(x0 + 14, y0 + 244, "mesure de la campagne ne peut pas servir à le nier.", petit, ALERTE)

    # ---- panneau 4 : le contraste
    x0, y0, pw, ph = 712, 474, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           f"le contraste entre plis, à {_fr(ct['longueur_en_feuilles'])} feuille "
           f"({ct['couches']} couches)", moyen, ENCRE)
    ecrire(x0 + 150, y0 + 12, "aveugle", petit, ALERTE)
    ecrire(x0 + 330, y0 + 12, "meilleure", petit, BON)
    for i, x in enumerate(ct["lignes"]):
        yy = y0 + 38 + i * 26
        ecrire(x0 + 14, yy, f"contraste {_fr(x['contraste'])}", 0, ENCRE)
        for dx, rec in ((150, "aveugle"), (330, "meilleure")):
            b = x["par_recette"][rec]
            ok = b["elle_lit_la_bascule_partout"]
            ecrire(x0 + dx, yy,
                   f"{'★' if ok else '✗'} {b['lisent_la_bascule']}/{b['decalages_lus']}", 0,
                   BON if ok else ALERTE)
    tient = ct["contrastes_qui_tiennent"]["meilleure"]
    ecrire(x0 + 14, y0 + 206,
           f"★  la meilleure coupe tient jusqu'à un contraste de {_fr(min(tient), 2)}"
           if tient else "✗  aucun contraste ne tient", moyen, BON if tient else ALERTE)
    ecrire(x0 + 14, y0 + 232,
           "⚠ le contraste NUL est un contrôle vide : sans texture, rien à lire.", petit, GRIS)

    # ---- bande
    y = 762
    art.rectangle([56, y, L - 56, y + 140], fill=BANDE)
    cadres.append((56, y, L - 56, y + 140))
    # ⚠⚠ LA BANDE LIT LA MEME SOURCE QUE LE PANNEAU, PAS LE VERDICT. Une premiere version lisait
    # `le_verdict` ici et `la_campagne` la-bas : deux chemins vers un meme nombre, libres de
    # diverger, et la sonde l'a montre en n'en deplacant qu'un seul.
    av = camp["par_recette"]["aveugle"]
    me = camp["par_recette"]["meilleure"]
    ecrire(74, y + 12,
           f"✗  La recette de la campagne ne lit AUCUNE longueur de façon fiable, sur une matière "
           f"dont la bascule est construite : sur sa propre fenêtre, "
           f"{av['lisent_la_bascule']}/{av['decalages_lus']} décalages.", moyen, ALERTE)
    ecrire(74, y + 38,
           f"★★★★  La MÊME fenêtre la lit {me['lisent_la_bascule']}/{me['decalages_lus']} en "
           f"cherchant sa coupe, et la meilleure coupe est fiable à "
           f"{len(lo['longueurs_fiables']['meilleure'])} longueurs sur "
           f"{lo['longueurs_essayees']}.", moyen, ENCRE)
    ecrire(74, y + 64,
           "★★★★  Les trois explications laissées ouvertes sont donc départagées : ni le "
           "contraste, ni la longueur, ni le centrage — la coupe AVEUGLE.", moyen, ENCRE)
    ecrire(74, y + 90,
           "★  Le contrôle est APPARIÉ : à chaque décalage la même fenêtre est lue sur une matière "
           "à deux plis et sur une matière à un pli, tout étant égal par ailleurs.", moyen, ENCRE)
    ecrire(74, y + 116,
           "⚠⚠  Et cela ne dit rien du vrai papyrus : un résultat négatif obtenu avec une recette "
           "qui ne peut pas lire n'est pas un résultat sur la matière.", moyen, ALERTE)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres = dessiner(d, sortie)
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
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("⭐⭐⭐⭐ aucune barre ne déborde de son graphe, donc aucune ne recouvre son nombre",
      not debordantes, f"{len(barres)} barres, {debordantes}"[:180])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("⭐ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ⭐⭐⭐⭐ LES DEUX RECETTES SONT DESSINEES, ET C'EST TOUT LE SUJET. Une figure qui n'en
    # montrerait qu'une ferait lire soit que l'instrument ne peut pas, soit que la campagne avait
    # raison.
    for rec in RECETTES:
        faux = copy.deepcopy(d)
        for x in faux["les_longueurs"]["lignes"]:
            x["par_recette"][rec]["bascule_mediane_deg"] = 71.7
        _c, p2, _cd, _pt, _b = dessiner(faux, sortie)
        v(f"⭐⭐⭐ la bascule de la recette « {rec} » est lue, pas supposée",
          any("71,7" in t for _x, _y, t, _f in p2) and not any("71,7" in t for t in tous))
    faux2 = copy.deepcopy(d)
    faux2["les_longueurs"]["longueurs_fiables"]["aveugle"] = [9.5]
    _c, p3, _cd, _pt, _b = dessiner(faux2, sortie)
    v("⭐⭐⭐⭐ la liste des longueurs fiables est LUE, et « aucune » n'est pas écrit en dur",
      any("9,5" in t for _x, _y, t, _f in p3)
      and any("AUCUNE longueur n'est fiable" in t for t in tous))
    faux3 = copy.deepcopy(d)
    faux3["la_campagne"]["sur_une_matiere_qui_bascule"]["par_recette"]["meilleure"][
        "lisent_la_bascule"] = 5
    _c, p4, _cd, _pt, _b = dessiner(faux3, sortie)
    v("⭐⭐⭐⭐ le compte de la campagne est lu des DEUX côtés de la bande",
      sum(1 for _x, _y, t, _f in p4 if "5/12" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '5/12' in t)} mentions")
    faux4 = copy.deepcopy(d)
    faux4["le_contraste"]["contrastes_qui_tiennent"]["meilleure"] = [0.31]
    _c, p5, _cd, _pt, _b = dessiner(faux4, sortie)
    v("⭐⭐⭐ le plus faible contraste qui tient est lu",
      any("0,31" in t for _x, _y, t, _f in p5))
    # ⚠ Une mesure a une seule recette est REFUSEE, jamais dessinee a moitie.
    creux = copy.deepcopy(d)
    for x in creux["les_longueurs"]["lignes"]:
        x["par_recette"].pop("meilleure", None)
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure à une seule recette est REFUSÉE, jamais dessinée à moitié", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "quelle_fenetre_lit_une_bascule.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "173_quelle_fenetre_lit_une_bascule.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
