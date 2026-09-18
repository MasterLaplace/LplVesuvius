"""Là où le rouleau se laisse suivre — et le prix de la question.

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon : une liste qui PORTE
l'étiquette est retrouvée, une liste de bruit pur ne l'est pas. En haut à droite, les observables
déclarés, du plus séparant au moins, avec le plancher de détection en travers. En bas à gauche, ce
que coûte la liberté : le maximum observé posé au milieu des maxima que rendent les mélanges. En bas
à droite, la piste nommée et son prix.

  uv run python src/figures/figure_la_ou_le_rouleau_se_laisse_suivre.py \\
      --json docs/mesures/la_ou_le_rouleau_se_laisse_suivre.json \\
      --sortie docs/images/191_la_ou_le_rouleau_se_laisse_suivre.png
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


def _fr(x, n: int = 3) -> str:
    """Un nombre en français, sans zéros inutiles.

    ⚠⚠ LE `rstrip` NE S'APPLIQUE QU'EN PRÉSENCE D'UNE VIRGULE : sans ce garde, `_fr(90, 0)` rend
    « 9 ». Défaut payé par `177`.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_ou_le_rouleau_se_laisse_suivre.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES DEUX FACES. Un chercheur de séparation
    qui ne retrouverait pas une colonne PORTANT l'étiquette ne pourrait rien trouver du tout, donc
    son silence sur le rouleau ne voudrait rien dire ; et un qui trouverait quelque chose dans du
    bruit pur ne mesurerait que la liberté qu'on lui a donnée.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "le_verdict", "les_colonnes"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("letalon_separe_les_deux"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if v.get("un_observable_separe"):
        nom = (v.get("le_meilleur") or {}).get("nom", "un observable")
        return f"Là où le rouleau se laisse suivre — « {nom} » sépare"
    return (f"Là où le rouleau se laisse suivre — AUCUN des "
            f"{v.get('observables_declares')} observables déclarés ne sépare")


def dessiner(d: dict, sortie: Path) -> tuple[Path, list, list, list, list, list]:
    L, H = 1360, 980
    img = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(img)
    gros, moyen, petit = police(19, 14, 11)
    poses: list[tuple[int, int, str, object]] = []
    points: list[tuple[float, float]] = []
    cadres: list[tuple[int, int, int, int]] = []
    barres: list[tuple[float, float]] = []
    traits: list[tuple[float, float, float]] = []

    def ecrire(x, y, texte, fonte, fill):
        f = petit if fonte == 0 else fonte
        art.text((x, y), texte, font=f, fill=fill)
        poses.append((x, y, texte, f))

    def barre(x, y, largeur_max, part, hauteur, coul):
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    v, e = d["le_verdict"], d["letalon"]
    separe = bool(v.get("un_observable_separe"))
    coul_v = BON if separe else ALERTE
    signe = "★" if separe else "✗"
    meilleur = v.get("le_meilleur") or {}
    plancher = float(v.get("le_plancher_de_detection") or 0.0)
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46,
           f"{v['chunks_qui_retiennent']} chunks qui retiennent sur {v['chunks_etiquetes']} · "
           f"{v['observables_declares']} observables DÉCLARÉS, {v['observables_lus']} lus · "
           f"{d['tirages']} mélanges de l'étiquette · plancher de détection "
           f"{_fr(plancher, 4)}", petit, GRIS)

    # ---- panneau 1 : l'étalon
    x0, y0, pw, ph = 56, 122, 620, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — mêmes chunks, même étiquette, deux listes connues", moyen,
           ENCRE)
    hautE = max([float((e.get(c) or {}).get("la_separation_maximale") or 0.0)
                 for c in ("avec_lingredient", "rien_que_du_bruit")]
                + [float((e.get(c) or {}).get("le_plancher_de_detection") or 0.0)
                   for c in ("avec_lingredient", "rien_que_du_bruit")] + [0.01]) * 1.2
    for k, (nom, cle, attendu) in enumerate(
            (("la liste PORTE l'ingrédient de l'étiquette", "avec_lingredient", True),
             ("la liste n'est QUE du bruit", "rien_que_du_bruit", False))):
        x = e.get(cle) or {}
        yy = y0 + 14 + k * 96
        ecrire(x0 + 14, yy, nom, moyen, ENCRE)
        if not x.get("decidable"):
            ecrire(x0 + 14, yy + 22, str(x.get("raison")), 0, ALERTE)
            continue
        ok = bool(x["un_observable_separe"]) == attendu
        ecrire(x0 + 14, yy + 22,
               f"attendu « {'sépare' if attendu else 'ne sépare rien'} »", 0, GRIS)
        ecrire(x0 + 270, yy + 22,
               f"{'★' if ok else '✗'} sépare {x['un_observable_separe']}", 0,
               BON if ok else ALERTE)
        ecrire(x0 + 14, yy + 42,
               f"le maximum de la liste   {_fr(x['la_separation_maximale'], 4)}", 0, CONTRE)
        barre(x0 + 250, yy + 44, 340, float(x["la_separation_maximale"]) / hautE, 9, CONTRE)
        ecrire(x0 + 14, yy + 60,
               f"le plancher des mélanges {_fr(x['le_plancher_de_detection'], 4)}", 0, GRIS)
        barre(x0 + 250, yy + 62, 340, float(x["le_plancher_de_detection"]) / hautE, 9, GRIS)
        ecrire(x0 + 14, yy + 78, f"« {x['le_meilleur']['nom']} »", 0, ENCRE)
    ecrire(x0 + 14, y0 + 210,
           "⚠⚠ Les deux listes ont la MÊME longueur que la liste déclarée : le prix de la liberté "
           "dépend du nombre.", petit, GRIS)

    # ---- panneau 2 : les observables
    x0, y0, pw, ph = 712, 122, 592, 234
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les observables déclarés, du plus séparant au moins", moyen, ENCRE)
    tous = sorted(v.get("tous") or [], key=lambda y: -y["separation"])
    hautO = max([float(x["separation"]) for x in tous] + [plancher, 0.01]) * 1.12
    for k, x in enumerate(tous[:9]):
        yy = y0 + 10 + k * 20
        au_dessus = float(x["separation"]) > plancher
        ecrire(x0 + 10, yy, _fr(x["separation"], 4), 0, ENCRE if k == 0 else GRIS)
        barre(x0 + 66, yy + 2, 112, float(x["separation"]) / hautO, 8,
              BON if au_dessus else (ENCRE if k == 0 else CONTRE))
        ecrire(x0 + 188, yy, f"aire {_fr(x['aire'], 4)}", 0, GRIS)
        # ⚠ LE NOM EST ECRIT ENTIER, TAG DE TRANCHE COMPRIS : la PROVENANCE d'un observable est ce
        # qui le rend lisible, et une troncature la mangeait pile.
        ecrire(x0 + 272, yy, x["nom"][:45], 0, ENCRE if k == 0 else GRIS)
    art.line([(x0 + 66 + 112 * plancher / hautO, y0 + 6),
              (x0 + 66 + 112 * plancher / hautO, y0 + 10 + 9 * 20)], fill=ALERTE, width=2)
    traits.append((x0 + 66 + 112 * plancher / hautO, y0 + 6, y0 + 10 + 9 * 20))
    ecrire(x0 + 10, y0 + 212,
           f"⚠ La barre verticale est le PLANCHER de détection, {_fr(plancher, 4)} : rien "
           f"en-deçà ne peut être établi ici.", petit, ALERTE)
    ecrire(x0 + 10, y0 + 194,
           f"⚠ {len(tous)} observables lus ; muets : "
           f"{', '.join(v.get('observables_sans_lecture') or []) or 'aucun'}", petit, GRIS)

    # ---- panneau 3 : le prix de la liberté
    x0, y0, pw, ph = 56, 408, 620, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que coûte la liberté de choisir l'observable", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12,
           "Chaque mélange garde SIX chunks étiquetés et reprend le maximum sur TOUTE la",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 28,
           "liste. Ce qui est comparé est donc « le meilleur de dix-neuf observables » contre",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 44,
           "« le meilleur de dix-neuf observables quand il n'y a rien à trouver ».", petit, ENCRE)
    maxima = sorted((v.get("le_nul") or {}).get("les_maxima") or [], reverse=True)
    hautN = max(maxima + [float(v.get("la_separation_maximale") or 0.0), 0.01]) * 1.15
    for k, m in enumerate(maxima):
        yy = y0 + 66 + k * 8
        barre(x0 + 130, yy, 300, float(m) / hautN, 5, GRIS)
        if k == 0:
            ecrire(x0 + 14, yy - 3, "les mélanges", 0, GRIS)
    yy = y0 + 66 + len(maxima) * 8 + 14
    ecrire(x0 + 14, yy - 3, "l'observé", 0, CONTRE)
    barre(x0 + 130, yy, 300, float(v.get("la_separation_maximale") or 0.0) / hautN, 9, CONTRE)
    ecrire(x0 + 14, y0 + 254,
           f"{signe} le maximum observé vaut {_fr(v.get('la_separation_maximale'), 4)} et le "
           f"plancher {_fr(plancher, 4)} :", moyen, coul_v)
    ecrire(x0 + 14, y0 + 276,
           "     aucun observable déclaré ne sépare." if not separe
           else "     un observable sépare au-delà du hasard.", moyen, coul_v)

    # ---- panneau 4 : la piste, et son prix
    x0, y0, pw, ph = 712, 408, 592, 304
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la piste nommée, et ce qu'elle vaut", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, "le meilleur observable", 0, ENCRE)
    ecrire(x0 + 14, y0 + 30, f"« {meilleur.get('nom', '—')} »", moyen, CONTRE)
    for k, (nom, val) in enumerate(
            (("son aire sous la courbe", _fr(meilleur.get("aire"), 4)),
             ("sa séparation", _fr(meilleur.get("separation"), 4)),
             ("le plancher à dépasser", _fr(plancher, 4)),
             ("les chunks qu'il couvre", str(meilleur.get("chunks_couverts"))))):
        yy = y0 + 58 + k * 20
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 250, yy, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 148,
           "⚠⚠⚠ Une aire au-dessus d'une demie dit que les chunks qui retiennent ont", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 164,
           "cet observable plus GRAND — mais sous le plancher, ça ne s'établit pas.", petit, ENCRE)
    ecrire(x0 + 14, y0 + 190, "ce qui est EXCLU de la liste, et pourquoi", 0, ENCRE)
    for k, nom in enumerate(d.get("les_exclus") or []):
        ecrire(x0 + 14, y0 + 208 + k * 16, f"✗ {nom}", 0, ALERTE)
    ecrire(x0 + 14, y0 + 262,
           "Ce sont les INGRÉDIENTS de l'étiquette : les inclure ferait une vérification", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 278,
           "qui ne peut pas échouer. Ils servent de face POSITIVE à l'étalon.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  L'INSTRUMENT PEUT TROUVER, ET L'ÉTALON LE PROUVE DES DEUX CÔTÉS : une liste de "
           f"{v['observables_declares']} colonnes dont UNE porte l'étiquette bruitée est retrouvée "
           f"({_fr((e.get('avec_lingredient') or {}).get('la_separation_maximale'), 4)} contre un",
           moyen, ENCRE)
    ecrire(78, y + 46,
           f"     plancher de "
           f"{_fr((e.get('avec_lingredient') or {}).get('le_plancher_de_detection'), 4)}), et une "
           f"liste de même longueur qui n'est QUE du bruit ne rend rien "
           f"({_fr((e.get('rien_que_du_bruit') or {}).get('la_separation_maximale'), 4)}). "
           f"C'est ce qui rend son silence lisible.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  SUR LE ROULEAU, AUCUN DES {v['observables_declares']} OBSERVABLES DÉCLARÉS NE "
           f"SÉPARE : le meilleur atteint {_fr(v.get('la_separation_maximale'), 4)} quand les "
           f"mélanges de l'étiquette montent à {_fr(plancher, 4)}.", moyen, coul_v)
    ecrire(78, y + 106,
           f"     Avec {v['chunks_qui_retiennent']} chunks contre "
           f"{v['chunks_etiquetes'] - v['chunks_qui_retiennent']} et cette liberté-là, rien sous "
           f"une aire de {_fr(0.5 + plancher, 4)} n'est établissable — et c'est un fait sur le "
           f"COMPTE, pas sur la matière.", moyen, coul_v)
    ecrire(78, y + 138,
           f"★  CE QUI RESTE EST UNE PISTE NOMMÉE : « {meilleur.get('nom', '—')} » rend une aire "
           f"de {_fr(meilleur.get('aire'), 4)}, donc les chunks où la marche tient sont ceux",
           moyen, ENCRE)
    ecrire(78, y + 166,
           "     où une fibre se suit DÉJÀ plus loin à plat. Deux autres observables pointent dans "
           "le même sens, et aucun des trois ne franchit le plancher.", moyen, ENCRE)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche ne dit pas : que cette piste soit vraie. Elle dit qu'elle est la "
           "seule que vingt et un chunks laissent nommer, et ce qu'il faudrait pour la trancher.",
           petit, GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    img.save(sortie)
    return sortie, poses, cadres, points, barres, traits


def verifier(json_path: Path, sortie: Path) -> int:
    echecs, faits = 0, 0

    def v(nom, ok, detail=""):
        nonlocal echecs, faits
        faits += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '⛔'} {nom}" + (f"  — {detail}" if detail else ""))

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(90.0, 0), _fr(0.5, 1), _fr(0.4286, 4)) == ("90", "0,5", "0,4286"),
      f"{(_fr(90.0, 0), _fr(0.5, 1), _fr(0.4286, 4))}")
    v("aucun texte ne déborde de l'image", not textes_debordants(poses, img.size[0]),
      str(textes_debordants(poses, img.size[0]))[:200])
    v("aucun texte ne sort de son cadre, ni à droite ni EN BAS",
      not textes_hors_cadre(poses, cadres), str(textes_hors_cadre(poses, cadres))[:200])
    v("aucun texte n'en recouvre un autre", not textes_qui_se_recouvrent(poses),
      str(textes_qui_se_recouvrent(poses))[:200])
    manquants = sorted({x for _a, _b, txt, _f in poses for x in glyphes_manquants(txt)})
    v("aucun glyphe n'est absent de la police déployée", not manquants, str(manquants)[:200])
    v("il y a un cadre par panneau, plus la bande", len(cadres) == 5, f"{len(cadres)} cadres")
    debordantes = [(round(a, 1), round(b, 1)) for a, b in barres if a > b + 0.5]
    v("★★★★ aucune barre ne déborde de son graphe", not debordantes,
      f"{len(barres)} barres, {debordantes}"[:200])
    v("les points tracés restent dans l'image",
      all(0 <= x <= img.size[0] and 0 <= y <= img.size[1] for x, y in points),
      f"{len(points)} points")
    # ⚠⚠⚠ UNE GARDE QUE `textes_hors_cadre` NE DONNE PAS : elle ne signale pas un texte qui COMMENCE
    # sous un cadre, donc une ligne posee quelques pixels sous un panneau tombe dans la bande et s'y
    # fait manger sans qu'une seule verification ne rougisse. Defaut vu en REGARDANT l'image de
    # `190`.
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    v("★ le trait du plancher reste dans son panneau", all(
        712 <= x <= 1304 and 122 <= y0 <= y1 <= 356 for x, y0, y1 in traits),
      str(traits))
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    # ★★★★ LE MAXIMUM OBSERVE ET LE PLANCHER SONT LUS DES DEUX COTES : c'est leur COMPARAISON qui
    # est le resultat, et l'un sans l'autre ne dirait rien.
    for cle, val in (("la_separation_maximale", 0.3131), ("le_plancher_de_detection", 0.4646)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, 4) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★ LES DEUX FACES DE L'ETALON SONT DESSINEES AVEC LEURS DEUX LECTURES.
    for cle in ("avec_lingredient", "rien_que_du_bruit"):
        faux = copy.deepcopy(d)
        faux["letalon"][cle]["la_separation_maximale"] = 0.7171
        faux["letalon"][cle]["le_plancher_de_detection"] = 0.6161
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (0.7171, 0.6161)
                if any(_fr(m, 4) in t for _x, _y, t, _f in p3))
        v(f"★★★ la face « {cle} » est dessinée avec ses deux lectures", n == 2, f"{n} sur 2")

    # ★★★ CHAQUE MELANGE DU NUL EST DESSINE : c'est la distribution qui rend le plancher lisible.
    faux = copy.deepcopy(d)
    n_av = len(dessiner(faux, sortie)[4])
    faux["le_verdict"]["le_nul"]["les_maxima"] = (
        list(faux["le_verdict"]["le_nul"]["les_maxima"]) + [0.2222])
    n_ap = len(dessiner(faux, sortie)[4])
    v("★★★ un mélange de plus est une barre de plus", n_ap == n_av + 1, f"{n_av} puis {n_ap}")

    # ★★★★ LE MEILLEUR OBSERVABLE EST NOMME, ET SON AIRE AUSSI : la piste EST le resultat.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_meilleur"]["nom"] = "un observable de sonde"
    faux["le_verdict"]["le_meilleur"]["aire"] = 0.8181
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le meilleur observable est nommé des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "un observable de sonde" in t) >= 2)
    v("★★★★ et son aire est lue",
      any(_fr(0.8181, 4) in t for _x, _y, t, _f in p4))

    # ★★★ LES OBSERVABLES MUETS SONT NOMMES : declares, donc comptes dans la liberte.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["observables_sans_lecture"] = ["un observable muet de sonde"]
    _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★ un observable muet est nommé",
      any("un observable muet de sonde" in t for _x, _y, t, _f in p5))

    # ★★★★ UN ETALON QUI NE SEPARE PAS FAIT REFUSER LA MESURE.
    import tempfile  # noqa: PLC0415

    rouge = copy.deepcopy(d)
    rouge["le_verdict"]["letalon_separe_les_deux"] = False
    refuse, tmp = False, None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(rouge, fh, ensure_ascii=False)
            tmp = Path(fh.name)
        lire(tmp)
    except ValueError:
        refuse = True
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    v("★★★★ un étalon qui ne sépare pas fait REFUSER la mesure", refuse)

    # ★★★★ LES DEUX BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for sep, attendu in ((True, "sépare"), (False, "AUCUN")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["un_observable_separe"] = sep
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p6, 1360) and not textes_hors_cadre(p6, cadres)
          and not textes_qui_se_recouvrent(p6))
    v("★★★★ les deux branches sont distinctes", len(set(branches)) == 2, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_la_ou_le_rouleau_se_laisse_suivre.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_ou_le_rouleau_se_laisse_suivre.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "191_la_ou_le_rouleau_se_laisse_suivre.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
