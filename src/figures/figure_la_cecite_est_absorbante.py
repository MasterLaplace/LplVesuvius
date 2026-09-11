#!/usr/bin/env python3
"""La cécité est absorbante — et c'est l'arrêt que le marcheur n'a jamais pris.

⚠⚠ **Ce que cette figure doit rendre évident, et qu'aucun tableau ne rend.** `113` a mesuré que
rien n'arrête une marche : 28 sur 28 au plafond. `115` a trouvé qu'un pas sur trois ne lit rien.
La question de `116` est de savoir si ces pas aveugles sont l'arrêt qui manquait.

  ⭐⭐⭐ Le panneau de GAUCHE le montre en une image : rangées par rayon, les cases aveugles ne
  sont jamais **au milieu** d'une marche, toujours **en queue**. Onze marches s'arrêtent de lire
  et aucune ne relit. Et la même image montre la seconde chose : les queues aveugles ne
  descendent pas d'un bloc — elles **alternent** avec des marches qui lisent leurs vingt pas,
  jusqu'à 22,17 mm. Ce n'est donc pas une frontière.

  ⭐⭐ Le panneau de DROITE est le témoin, sans lequel « zéro retour » ne dirait rien. Les
  positions aveugles sont permutées à l'intérieur de chaque marche, à compte constant : le hasard
  rend sept retours de vue, jamais moins de cinq sur deux mille tirages. L'observé est à zéro.

⚠ Les deux panneaux ne répondent pas à la même question et restent séparés : « où sont les pas
aveugles » et « le hasard les mettrait-il là ». Le second est ce qui rend le premier lisible.

  uv run python src/figures/figure_la_cecite_est_absorbante.py \\
      --json docs/mesures/la_cecite_est_elle_absorbante.json \\
      --sortie docs/images/116_la_cecite_est_absorbante.png
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
MARCHE = (86, 104, 132)
AVEUGLE = (176, 62, 62)
TEMOIN = (196, 140, 60)
OBSERVE = (60, 110, 90)


def lire(chemin: Path) -> dict:
    """Le JSON de `la_cecite_est_elle_absorbante.py`.

    ⚠⚠ Refuse un JSON dont les suites manquent plutôt que de dessiner une grille vide : une
    grille sans case a exactement l'air d'une grille où rien n'est aveugle, c'est-à-dire du
    résultat inverse de celui que la figure existe pour montrer.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("par_marche"):
        raise ValueError(f"{chemin} ne porte aucune marche")
    if not d.get("temoin", {}).get("distribution_des_retours"):
        raise ValueError(f"{chemin} ne porte pas la distribution du témoin")
    for m in d["par_marche"]:
        if len(m.get("aveugles", [])) != len(m.get("confirmes", [])):
            raise ValueError(f"{chemin} : une marche n'a pas autant de cécités que de pas")
    return d


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list]:
    """Dessine, et rend AUSSI les poses de texte et les cadres.

    ⚠⚠ Les rendre n'est pas un confort : les trois gardes de `figure_commune` ne jugent que ce
    qu'on leur donne, et une figure qui garde ses poses pour elle est une figure qu'aucune
    batterie ne peut relire.
    """
    ms = sorted(d["par_marche"], key=lambda m: m["rayon_mm"])
    pmax = max(len(m["aveugles"]) for m in ms)
    # ⚠ La hauteur est DÉRIVÉE du nombre de marches : une constante déborderait le jour où une
    # campagne en rend trente. Le panneau de droite garde la sienne, fixe, parce qu'elle ne
    # dépend pas des marches.
    HAUT_CASE, JEU, PH_DROITE = 10, 3, 300
    ph_gauche = max(len(ms) * (HAUT_CASE + JEU), 40)
    L = 1180
    H = 112 + max(ph_gauche, PH_DROITE) + 152
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        art.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    a = d["la_cecite_est_elle_absorbante"]
    f = d["le_vide_est_il_une_frontiere"]
    w = d["temoin"]

    ecrire(28, 20, "La cécité est absorbante, et elle vient par plaques", gros, ENCRE)
    ecrire(28, 46, f"{d['marches']} marches · {d['pas']} pas · plafond "
                   f"{d['plafond_de_la_course']} · source {d['source']}", petit, GRIS)

    # ── Panneau gauche : la grille, rangée par rayon ─────────────────────────
    x0, y0 = 108, 112
    case = 20
    pw, ph = pmax * case, ph_gauche
    ecrire(x0, y0 - 26, "chaque marche, pas par pas", moyen, ENCRE)
    ecrire(x0 + 226, y0 - 24, "bleu = confirmé · rouge = rien lu", petit, GRIS)
    for i, m in enumerate(ms):
        y = y0 + i * (HAUT_CASE + JEU)
        for k in range(pmax):
            x = x0 + k * case
            if k >= len(m["aveugles"]):
                continue
            if m["aveugles"][k]:
                art.rectangle([x, y, x + case - 4, y + HAUT_CASE - 2], fill=AVEUGLE)
            else:
                art.rectangle([x, y, x + case - 4, y + HAUT_CASE - 2],
                              fill=MARCHE if m["confirmes"][k] else None,
                              outline=MARCHE if m["confirmes"][k] else TRAIT)
        # ⚠⚠ Le rayon est écrit sur UNE ligne sur trois, et pas sur toutes : vingt-huit étiquettes
        # de onze pixels dans deux cent quatre-vingts pixels de haut se recouvrent, et la garde
        # `textes_qui_se_recouvrent` l'attrape — mais le lecteur, lui, verrait une bouillie.
        if i % 3 == 0 or i == len(ms) - 1:
            ecrire(28, y - 1, f"{m['rayon_mm']:>6.2f} mm", petit, GRIS)

    # ⚠ Les légendes tiennent dans la LARGEUR DU PANNEAU, en lignes courtes. Une seule ligne
    # longue ne déborde d'aucun cadre déclaré, donc aucune garde ne la refuse — et elle va
    # pourtant se poser à côté du texte du témoin, où l'œil lit les deux comme une phrase.
    ecrire(x0, y0 + ph + 8, "les cases rouges sont toujours en QUEUE :", petit, AVEUGLE)
    ecrire(x0, y0 + ph + 26, f"{a['marches_ou_la_vue_revient']} retour de vue sur "
                             f"{a['marches_avec_occasion']} marches qui en avaient l'occasion",
           petit, AVEUGLE)
    ecrire(x0, y0 + ph + 46, f"et elles alternent : {f['plages_observees']} plages contre "
                             f"{f['plages_sous_une_frontiere']} sous une frontière radiale",
           petit, ENCRE)

    # ── Panneau droit : le témoin ────────────────────────────────────────────
    x1 = x0 + pw + 132
    pw2, ph2 = L - x1 - 40, PH_DROITE
    ecrire(x1, y0 - 26, "témoin : la même cécité, replacée au hasard", moyen, ENCRE)
    dist = {int(k): v for k, v in w["distribution_des_retours"].items()}
    haut_val = max(dist) if dist else 1
    bornes = list(range(0, haut_val + 1))
    larg = max(8, int(pw2 / max(1, len(bornes))) - 6)
    pic = max(dist.values()) if dist else 1
    base = y0 + ph2
    for j, b in enumerate(bornes):
        x = x1 + j * (larg + 6)
        n = dist.get(b, 0)
        h = int((n / pic) * (ph2 - 44)) if pic else 0
        if b == w["retours_observes"]:
            art.rectangle([x, base - 18, x + larg, base], fill=OBSERVE)
        elif n:
            art.rectangle([x, base - h, x + larg, base], fill=TEMOIN)
        ecrire(x + 2, base + 6, str(b), petit, GRIS)
    art.line([x1, base, x1 + pw2, base], fill=TRAIT, width=1)
    ecrire(x1, base + 26, "retours de vue (marches où un pas voyant suit un aveugle)",
           petit, GRIS)
    ecrire(x1, base + 46, f"observé {w['retours_observes']} · médiane sous permutation "
                          f"{w['retours_medians_sous_permutation']:.0f} · jamais moins de "
                          f"{w['retours_min_sous_permutation']} en {w['tirages']} tirages",
           petit, ENCRE)
    ecrire(x1, base + 66, f"part des permutations aussi basse : "
                          f"{w['part_des_permutations_aussi_basse']}", petit, OBSERVE)

    p = d["la_portee_quand_on_sarrete_a_laveugle"]
    bas = y0 + max(ph, ph2) + 106
    ecrire(28, bas, f"s'arrêter au premier pas aveugle rend la première portée non censurée du "
                    f"dépôt : {p['marches_qui_sarretent_pour_une_raison']} marches s'arrêtent "
                    f"pour une raison", moyen, ENCRE)
    ecrire(28, bas + 22, f"médiane {p['portee_mesuree']['longueur_mediane_um']:.0f} µm "
                         f"(max {p['portee_mesuree']['longueur_max_um']:.0f}) · les "
                         f"{p['marches_encore_censurees']} autres touchent encore le plafond, "
                         f"donc restent une borne inférieure", petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    try:
        dit = sortie.relative_to(RACINE)
    except ValueError:
        dit = sortie
    print(f"écrit : {dit}  ({img.size[0]}×{img.size[1]})")
    return sortie, poses, [(x0, y0, x0 + pw, y0 + ph), (x1, y0, x1 + pw2, y0 + ph2)]


def verifier() -> int:
    """Des contrôles hors ligne, sur un JSON fabriqué — et trois sondes."""
    import tempfile
    echecs = controles = 0

    def v(nom, obtenu, attendu=True):
        nonlocal echecs, controles
        controles += 1
        if obtenu != attendu:
            echecs += 1
            print(f"  ECHEC  {nom} — attendu {attendu!r}, obtenu {obtenu!r}")

    def marche(r, voyants, total=20, taux=2):
        return {"rayon_mm": r,
                "aveugles": [k >= voyants for k in range(total)],
                "confirmes": [k < voyants and k % taux == 0 for k in range(total)]}

    faux = {
        "source": "m.json", "marches": 6, "pas": 120, "plafond_de_la_course": 20,
        "par_marche": [marche(4.0, 20), marche(8.0, 20), marche(12.0, 5),
                       marche(16.0, 20), marche(20.0, 0), marche(23.0, 3)],
        "la_cecite_est_elle_absorbante": {
            "decidable": True, "marches": 6, "marches_avec_un_pas_aveugle": 3,
            "marches_ou_la_vue_revient": 0, "marches_avec_occasion": 3,
            "la_cecite_est_absorbante": True},
        "temoin": {"decidable": True, "tirages": 2000, "graine": 1161, "retours_observes": 0,
                   "distribution_des_retours": {"1": 40, "2": 560, "3": 1400},
                   "retours_medians_sous_permutation": 3.0,
                   "retours_min_sous_permutation": 1,
                   "part_des_permutations_aussi_basse": 0.0},
        "la_portee_quand_on_sarrete_a_laveugle": {
            "decidable": True, "marches_qui_sarretent_pour_une_raison": 3,
            "marches_encore_censurees": 3,
            "portee_mesuree": {"longueur_mediane_um": 579.5, "longueur_max_um": 3312.9}},
        "le_vide_est_il_une_frontiere": {
            "decidable": True, "plages_observees": 4, "plages_sous_une_frontiere": 2},
    }
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        j = r / "m.json"
        j.write_text(json.dumps(faux), encoding="utf-8")
        lu = lire(j)
        v("le JSON est lu", len(lu["par_marche"]), 6)
        p, poses, cadres = dessiner(lu, r / "f.png")
        v("l'image est écrite", p.is_file())
        v("... et elle n'est pas vide", p.stat().st_size > 3000)
        im = Image.open(p).convert("RGB")
        v("... et sa largeur est celle annoncée", im.size[0], 1180)
        pixels = list(im.getdata())
        # ⚠⚠ Les trois états de case doivent être DISTINCTS à l'écran. S'ils ne l'étaient pas,
        # « rien lu » et « pas confirmé » seraient le même dessin — c'est-à-dire exactement la
        # confusion que `115` a trouvée dans le drapeau `oriente`, refaite dans une image.
        v("les cases aveugles sont dessinées", pixels.count(AVEUGLE) > 200)
        v("les cases confirmées aussi", pixels.count(MARCHE) > 200)
        v("les cases voyantes non confirmées aussi", pixels.count(TRAIT) > 200)
        v("le témoin est dessiné", pixels.count(TEMOIN) > 200)
        v("... et l'observé se distingue du témoin", pixels.count(OBSERVE) > 100)
        # ⚠⚠ Les trois gardes de `figure_commune`.
        v("aucun texte ne déborde de la toile", textes_debordants(poses, im.size[0]), [])
        v("aucun texte ne sort de son panneau", textes_hors_cadre(poses, cadres), [])
        v("aucun texte n'en recouvre un autre", textes_qui_se_recouvrent(poses), [])
        v("aucun texte n'est écrit sous le bord bas",
          [t for x, y, t, f in poses if f is not None and y + f.getbbox(t)[3] > im.size[1]], [])

        # ⚠⚠ LA sonde qui compte : une marche dont les suites ne s'accordent pas est REFUSÉE.
        # Sans elle, la grille dessinerait une cécité décalée d'un pas par rapport à ce que le
        # marcheur a confirmé, et rien n'aurait l'air faux.
        casse = json.loads(json.dumps(faux))
        casse["par_marche"][0]["confirmes"] = casse["par_marche"][0]["confirmes"][:-1]
        j.write_text(json.dumps(casse), encoding="utf-8")
        try:
            lire(j)
            v("sonde : des suites de longueurs différentes sont refusées", False)
        except ValueError:
            v("sonde : des suites de longueurs différentes sont refusées", True)

        sans = json.loads(json.dumps(faux))
        sans["par_marche"] = []
        j.write_text(json.dumps(sans), encoding="utf-8")
        try:
            lire(j)
            v("sonde : un JSON sans marche est refusé", False)
        except ValueError:
            v("sonde : un JSON sans marche est refusé", True)

        muet = json.loads(json.dumps(faux))
        muet["temoin"]["distribution_des_retours"] = {}
        j.write_text(json.dumps(muet), encoding="utf-8")
        try:
            lire(j)
            v("sonde : un JSON sans distribution de témoin est refusé", False)
        except ValueError:
            v("sonde : un JSON sans distribution de témoin est refusé", True)

        # ⚠ La toile grandit avec les marches : une hauteur figée déborderait.
        large = json.loads(json.dumps(faux))
        large["par_marche"] = [marche(4.0 + i, 20 - (i % 5)) for i in range(30)]
        j.write_text(json.dumps(large), encoding="utf-8")
        _, poses2, cadres2 = dessiner(lire(j), r / "g.png")
        im2 = Image.open(r / "g.png").convert("RGB")
        v("trente marches ne débordent pas", textes_debordants(poses2, im2.size[0]), [])
        v("... ni ne se recouvrent", textes_qui_se_recouvrent(poses2), [])
        v("... ni n'écrivent sous le bord bas",
          [t for x, y, t, f in poses2 if f is not None and y + f.getbbox(t)[3] > im2.size[1]], [])
        v("... et la toile a grandi", im2.size[1] > im.size[1])

    print(f"\n{'ALL PASS' if echecs == 0 else 'ÉCHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "la_cecite_est_elle_absorbante.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "116_la_cecite_est_absorbante.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    dessiner(lire(a.json), a.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
