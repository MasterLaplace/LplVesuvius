"""La cohérence creuse-t-elle à la frontière ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, les cohérences elles-mêmes : plate
au rasoir, creusée dès qu'il y a du recouvrement, et le creux tombe SUR les frontières construites.
En haut à droite, ce que le recouvrement doit valoir pour que ça marche à tous les décalages, avec le
contrôle vide à un pli. En bas à gauche, le domaine de bruit et le prix de la liberté de choisir une
largeur. En bas à droite, l'échange de `178` relu par les deux lecteurs.

  uv run python src/figures/figure_la_coherence_creuse_t_elle_a_la_frontiere.py \\
      --json docs/mesures/la_coherence_creuse_t_elle_a_la_frontiere.json \\
      --sortie docs/images/179_la_coherence_creuse_t_elle_a_la_frontiere.png
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
    « 9 », le zéro des dizaines rogné comme s'il était décimal. Défaut payé par `177`, vu en
    REGARDANT l'image et par aucune garde.
    """
    if x is None:
        return "—"
    t = f"{float(x):.{n}f}"
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t.replace(".", ",")


def lire(chemin: Path) -> dict:
    """Le JSON de `la_coherence_creuse_t_elle_a_la_frontiere.py`.

    ⚠⚠ Refuse une mesure sans son CONTRÔLE VIDE ou sans ses profils. Dessiner des creux sans la
    matière à un seul pli ferait lire « le creux trouve la frontière » comme une propriété du
    lecteur, alors que la moitié de l'énoncé est qu'il ne trouve rien là où il n'y a rien.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("la_fixture", "le_pli_unique", "les_profils", "le_domaine", "le_bruit",
                "lechange", "lencadrement", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    if not d["le_verdict"].get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if len(d["les_profils"]) < 3:
        raise ValueError(f"{chemin} : il faut le rasoir, un échec et la borne")
    return d


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

    def segment(x1, y1, x2, y2, coul, largeur=2):
        art.line([x1, y1, x2, y2], fill=coul, width=largeur)
        points.append((x1, y1))
        points.append((x2, y2))
        traits.append((min(x1, x2), (y1 + y2) / 2.0, max(x1, x2)))

    def barre(x, y, largeur_max, part, hauteur, coul):
        """Une barre, et RIEN quand la part est nulle.

        ⚠ Un rectangle de largeur zéro se dessine quand même, en un trait vertical d'un pixel qui
        se lit comme un glyphe au milieu d'une colonne de chiffres. Vu en REGARDANT l'image, par
        aucune garde : les gardes comptent les débordements, pas les barres vides.
        """
        bout = x + largeur_max * max(0.0, min(1.0, float(part)))
        if bout > x:
            art.rectangle([x, y, bout, y + hauteur], fill=coul)
        barres.append((bout, x + largeur_max))
        points.append((bout, y + hauteur))

    v = d["le_verdict"]
    n, pli, vx = int(d["couches"]), int(d["pli_en_couches"]), float(d["voxel_um"])

    ecrire(28, 20, "La cohérence creuse-t-elle à la frontière ? — oui, et il faut un demi-pli de "
                   "recouvrement", gros, ENCRE)
    ecrire(28, 46, f"{n} couches · un pli {pli} couches · voxel {_fr(vx, 1)} µm · "
                   f"{d['decalages']} décalages · {d['permutations']} permutations · la fenêtre "
                   f"porte {_fr(d['tour_porte_deg'], 3)}° à {d['plis_grossiers']} plis comme à "
                   f"{d['plis_fins']}", petit, GRIS)

    # ---- panneau 1 : les cohérences elles-mêmes
    x0, y0, pw, ph = 56, 122, 620, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la cohérence couche par couche — un rasoir ne creuse pas", moyen, ENCRE)
    gx, gy, gw, gh = x0 + 52, y0 + 20, 526, 118
    art.line([gx, gy, gx, gy + gh], fill=TRAIT, width=1)
    art.line([gx, gy + gh, gx + gw, gy + gh], fill=TRAIT, width=1)
    couleurs = (BON, CONTRE, ALERTE)
    for k, prof in enumerate(d["les_profils"][:3]):
        coul = couleurs[k]
        c = list(prof["coherences"])
        prec = None
        for i, val in enumerate(c):
            xi = gx + gw * float(i) / float(max(1, len(c) - 1))
            yi = gy + gh - gh * max(0.0, min(1.0, float(val)))
            if prec is not None:
                segment(prec[0], prec[1], xi, yi, coul, 2)
            prec = (xi, yi)
    for f_ in d["les_profils"][-1]["frontieres_construites"]:
        xf = gx + gw * float(f_) / float(n - 1)
        art.line([xf, gy + gh, xf, gy + gh + 7], fill=ENCRE, width=2)
        points.append((xf, gy + gh + 7))
        ecrire(xf - 8, gy + gh + 10, str(f_), 0, ENCRE)
    ecrire(gx - 22, gy - 6, "1", 0, GRIS)
    ecrire(gx - 22, gy + gh - 8, "0", 0, GRIS)
    ecrire(gx, gy + gh + 28, "couche · ▲ frontière construite", 0, GRIS)
    yy = y0 + 180
    for k, prof in enumerate(d["les_profils"][:3]):
        coul = couleurs[k]
        etat = ("★ creux lu couche " + str(prof["frontiere_lue"])
                if prof["gagnant"] == "empilement" else "✗ aucun creux")
        ecrire(x0 + 14, yy, f"— recouvrement {_fr(prof['transition_um'], 1)} µm "
                            f"({_fr(prof['transition_en_couches'], 2)} couches)", 0, coul)
        ecrire(x0 + 300, yy, etat, 0, coul)
        yy += 18
    ecrire(x0 + 14, y0 + 248,
           "⚠⚠⚠ La prémisse était FAUSSE sur la matière que le dépôt lisait : le tenseur de",
           petit, ALERTE)
    ecrire(x0 + 14, y0 + 264,
           "structure vit DANS une couche, et aucune couche ne contient deux plis.", petit, ALERTE)

    # ---- panneau 2 : ce que le recouvrement doit valoir
    x0, y0, pw, ph = 712, 122, 592, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "combien de recouvrement, et le contrôle vide", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "recouvrement", petit, GRIS)
    ecrire(x0 + 188, y0 + 10, "sur frontière", petit, ENCRE)
    ecrire(x0 + 408, y0 + 10, "1 pli", petit, CONTRE)
    ecrire(x0 + 486, y0 + 10, "profondeur", petit, GRIS)
    vides = {x["transition_um"]: x for x in d["le_pli_unique"]["lignes"]}
    for k, x in enumerate(d["la_fixture"]["lignes"]):
        yy = y0 + 34 + k * 20
        tot = max(1, int(x["decalages"]))
        ecrire(x0 + 14, yy, f"{_fr(x['transition_um'], 1)} µm · "
                            f"{_fr(x['transition_en_couches'], 2)} c.", 0, ENCRE)
        coul = BON if x["lue_a_tous_les_decalages"] else (
            GRIS if x["creux_sur_une_frontiere"] == 0 else ALERTE)
        ecrire(x0 + 188, yy, f"{x['creux_sur_une_frontiere']}/{tot}", 0, coul)
        barre(x0 + 232, yy + 3, 160, float(x["creux_sur_une_frontiere"]) / float(tot), 9, coul)
        w = vides.get(x["transition_um"])
        ecrire(x0 + 408, yy, f"{w['creux_trouves']}/{w['decalages']}" if w else "—", 0, CONTRE)
        ecrire(x0 + 486, yy, _fr(x["profondeur_mediane"], 4), 0, GRIS)
    ecrire(x0 + 14, y0 + 218,
           f"★  il faut {_fr(v['le_recouvrement_juste_suffisant_um'], 1)} µm, encadré entre "
           f"{_fr(v['encadre_entre_um'][0], 1)} et {_fr(v['encadre_entre_um'][1], 1)} µm", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 242,
           f"     soit {_fr(v['il_vaut_le_voxel_fois'], 1)} voxels, ou "
           f"{_fr(v['il_vaut_le_pli_fois'], 4)} fois l'épaisseur d'un pli", moyen, ALERTE)
    ecrire(x0 + 14, y0 + 266,
           "⚠ Une feuille d'un seul pli ne creuse à AUCUN recouvrement : le creux n'est pas "
           "un artefact du mélange.", petit, GRIS)

    # ---- panneau 3 : le bruit, et le prix de la largeur
    x0, y0, pw, ph = 56, 460, 620, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le domaine de bruit, et ce que coûte le choix d'une largeur", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 10, "bruit de `156`", petit, GRIS)
    ecrire(x0 + 160, y0 + 10, "sur frontière", petit, ENCRE)
    ecrire(x0 + 400, y0 + 10, "profondeur", petit, GRIS)
    for k, x in enumerate(d["le_domaine"]["lignes"]):
        yy = y0 + 34 + k * 22
        tot = max(1, int(x["decalages"]))
        coul = BON if x["lue_a_tous_les_decalages"] else ALERTE
        ecrire(x0 + 14, yy, f"{_fr(x['bruit'], 1)}", 0, ENCRE)
        ecrire(x0 + 160, yy, f"{x['creux_sur_une_frontiere']}/{tot}", 0, coul)
        barre(x0 + 204, yy + 3, 170, float(x["creux_sur_une_frontiere"]) / float(tot), 10, coul)
        ecrire(x0 + 400, yy, _fr(x["profondeur_mediane"], 4), 0, GRIS)
        ecrire(x0 + 486, yy, "★ tenu" if x["lue_a_tous_les_decalages"] else "✗ perdu", 0, coul)
    b = d["le_bruit"]
    ecrire(x0 + 14, y0 + 116,
           f"sur {b['tirages']} cohérences tirées au hasard, une frontière est « lue » :", petit,
           ENCRE)
    for k, (nom, cle, coul) in enumerate(
            (("en payant la largeur", "taux_mesure", BON),
             ("sans la payer (règle réfutée)", "taux_sans_payer_la_largeur", ALERTE),
             ("ce que la permutation garantit", "ce_que_la_permutation_garantit", CONTRE))):
        yy = y0 + 138 + k * 20
        ecrire(x0 + 24, yy, nom, 0, coul)
        ecrire(x0 + 244, yy, _fr(b[cle], 4), 0, coul)
        barre(x0 + 300, yy + 3, 240, float(b[cle]) / 0.2, 9, coul)
    ecrire(x0 + 14, y0 + 204,
           "★ Le creux tient au bruit 16, là où `156` perd trois marches. ⚠ Et la liberté de", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 220,
           "choisir une largeur TRIPLE le taux de fausses frontières tant qu'on ne la paie pas.",
           petit, GRIS)

    # ---- panneau 4 : l'échange, relu par les deux lecteurs
    x0, y0, pw, ph = 712, 460, 592, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'échange de `178`, relu par les deux lecteurs", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "largeur · bruit", petit, GRIS)
    ecrire(x0 + 168, y0 + 10, "tour seul", petit, CONTRE)
    ecrire(x0 + 300, y0 + 10, "les deux", petit, BON)
    ecrire(x0 + 440, y0 + 10, "verdict", petit, GRIS)
    for k, x in enumerate(d["lechange"]):
        yy = y0 + 32 + k * 19
        tot = max(1, int(x["lectures_par_matiere"]))
        ecrire(x0 + 14, yy, f"{x['largeur']} c. ({x['en_plis']} pli) · {_fr(x['bruit'], 1)}", 0,
               ENCRE)
        ecrire(x0 + 168, yy, f"{x['empilement_par_le_tour']}/{x['rotation_par_le_tour']}"
                             f" sur {tot}", 0,
               BON if x["le_tour_seul_donne_les_deux"] else GRIS)
        ecrire(x0 + 300, yy, f"{x['empilement_par_les_deux']}/{x['rotation_par_les_deux']}"
                             f" sur {tot}", 0,
               BON if x["les_deux_lecteurs_donnent_les_deux"] else GRIS)
        ecrire(x0 + 440, yy,
               "★ les deux" if x["les_deux_lecteurs_donnent_les_deux"]
               else ("★ tour seul" if x["le_tour_seul_donne_les_deux"] else "✗"),
               0, BON if (x["les_deux_lecteurs_donnent_les_deux"]
                          or x["le_tour_seul_donne_les_deux"]) else ALERTE)
    ecrire(x0 + 14, y0 + 206,
           f"★ {len(v['cellules_gagnees_par_le_creux'])} cases gagnées, "
           f"✗ {len(v['cellules_perdues_par_le_creux'])} perdue — ce n'est pas un gain pur.",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 222,
           f"⚠ Sans bruit, un escalier FIN porte {v['faux_creux_sur_un_escalier_fin_sans_bruit']} "
           f"faux creux ; bruité, {v['faux_creux_sur_un_escalier_fin_bruite']}.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           "★  La cohérence CREUSE à une frontière de pli, et le creux y tombe — un observable "
           "que rien n'exploitait.", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     Profondeur {_fr(v['profondeur_du_creux_a_la_borne'], 4)} sur "
           f"{v['largeur_du_creux_a_la_borne']} couches, écart médian "
           f"{v['ecart_median_a_la_borne']} couche à la frontière construite, et il tient "
           f"jusqu'au bruit {_fr(v['le_plus_grand_bruit_tenu'], 0)} — là où `156` perd trois "
           "marches.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"✗  Mais un RASOIR ne creuse pas : il faut que les deux plis se recouvrent sur "
           f"{_fr(v['le_recouvrement_juste_suffisant_um'], 1)} µm, soit "
           f"{_fr(v['il_vaut_le_pli_fois'], 4)} fois un pli.", moyen, ALERTE)
    ecrire(78, y + 106,
           "     Rien ne dit que deux feuilles de papyrus s'interpénètrent sur plus d'un demi-pli, "
           "et la fixture ne peut pas le dire non plus.", moyen, ALERTE)
    ecrire(78, y + 138,
           "⚠⚠⚠ Sur matière BRUITÉE, le tour accumulé seul ne donne jamais les deux lectures, et "
           "les deux lecteurs ensemble les donnent :", moyen, ENCRE)
    ecrire(78, y + 166,
           "     "
           + " · ".join(f"{int(a)} couches au bruit {_fr(bb, 0)}"
                        for a, bb in v["sur_matiere_bruitee_les_deux_donnent_les_deux"])
           + ". L'échange de `178` est levé là où la matière n'est pas parfaite.", petit, GRIS)
    ecrire(78, y + 190,
           "     ⚠ Et il coûte la seule case que le tour seul tenait, "
           + " et ".join(f"{int(a)} couches au bruit {_fr(bb, 0)}"
                         for a, bb in v["cellules_perdues_par_le_creux"])
           + " : sans bruit, un escalier fin porte des micro-creux qu'aucun mélange ne reproduit.",
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
      (_fr(90.0, 0), _fr(16.0, 0), _fr(45.6, 1)) == ("90", "16", "45,6"),
      f"{(_fr(90.0, 0), _fr(16.0, 0), _fr(45.6, 1))}")
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

    def _boite(x, y, texte, f):
        b = f.getbbox(texte)
        return (x + b[0], y + b[1], x + b[2], y + b[3])

    traverses = [(t, round(x1), round(x2)) for x1, ty, x2 in traits
                 for (px, py, t, f) in poses
                 if (lambda bb: bb[0] < x2 and bb[2] > x1 and bb[1] <= ty <= bb[3])(
                     _boite(px, py, t, f))]
    v("★★★★ aucun trait ne traverse un texte", not traverses,
      f"{len(traits)} traits, {traverses}"[:200])

    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415
    tous = [t for _x, _y, t, _f in poses]

    # ★★★★ LA COHERENCE DESSINEE VIENT DE LA MESURE : une courbe recalculee par la figure
    # dessinerait une autre matiere que celle que le document publie.
    faux = copy.deepcopy(d)
    faux["les_profils"][-1]["coherences"] = [0.5] * len(faux["les_profils"][-1]["coherences"])
    _c, _p, _cd, pt2, _b, _t = dessiner(faux, sortie)
    v("★★★★ les profils dessinés sont ceux de la mesure", pt2 != points)

    # ★★★★ LA BORNE EST LUE DES DEUX COTES : sans elle, « le creux marche » n'a pas de prix.
    faux2 = copy.deepcopy(d)
    faux2["le_verdict"]["le_recouvrement_juste_suffisant_um"] = 61.7
    _c, p3, _cd, _pt, _b, _t = dessiner(faux2, sortie)
    v("★★★★ le recouvrement juste suffisant est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p3 if "61,7" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p3 if '61,7' in t)} mentions")

    # ★★★★ ET SON RAPPORT AU PLI AUSSI : c'est lui qui dit si la matiere peut le fournir.
    faux3 = copy.deepcopy(d)
    faux3["le_verdict"]["il_vaut_le_pli_fois"] = 0.9137
    _c, p4, _cd, _pt, _b, _t = dessiner(faux3, sortie)
    v("★★★★ le rapport à l'épaisseur d'un pli est lu des DEUX côtés",
      sum(1 for _x, _y, t, _f in p4 if "0,9137" in t) >= 2,
      f"{sum(1 for _x, _y, t, _f in p4 if '0,9137' in t)} mentions")

    # ★★★ LE CONTROLE VIDE EST DESSINE : sans lui, le panneau 2 ne montre qu'une moitie.
    # ⚠ LA COMPARAISON PORTE SUR UN COMPTE, PAS SUR UNE PRESENCE : « 7/12 » apparait deja dans le
    # panneau de l'echange, donc une sonde qui cherchait cette chaine passait au vert sans que le
    # controle vide soit dessine du tout.
    faux4 = copy.deepcopy(d)
    faux4["le_pli_unique"]["lignes"][-1]["creux_trouves"] = 3
    _c, p5, _cd, _pt, _b, _t = dessiner(faux4, sortie)
    v("★★★ le contrôle vide à un pli est dessiné",
      sum(1 for _x, _y, t, _f in p5 if t == "3/12") > sum(1 for x in tous if x == "3/12"),
      f"{sum(1 for _x, _y, t, _f in p5 if t == '3/12')} contre "
      f"{sum(1 for x in tous if x == '3/12')}")

    # ★★★ LES DEUX TAUX SONT LUS, ET PAS SEULEMENT CELUI QUI ARRANGE.
    faux5 = copy.deepcopy(d)
    faux5["le_bruit"]["taux_sans_payer_la_largeur"] = 0.1875
    _c, p6, _cd, _pt, b6, _t = dessiner(faux5, sortie)
    v("★★★ le taux de la règle réfutée est lu, barre comprise",
      any("0,1875" in t for _x, _y, t, _f in p6) and b6 != barres)

    # ★★★★ LA CASE PERDUE EST DITE : ne publier que les cases gagnees ferait lire un echange
    # comme un gain, ce qui est exactement le reproche que `178` adresse a la voie precedente.
    faux6 = copy.deepcopy(d)
    faux6["le_verdict"]["cellules_perdues_par_le_creux"] = [[72, 16.0]]
    _c, p7, _cd, _pt, _b, _t = dessiner(faux6, sortie)
    v("★★★★ la case que le creux COÛTE est écrite",
      any("72 couches au bruit 16" in t for _x, _y, t, _f in p7)
      and any("couches au bruit" in t for t in tous))

    creux = copy.deepcopy(d)
    creux.pop("le_pli_unique")
    json_tmp = json_path.with_name(json_path.stem + "_creux.json")
    try:
        lire_ok = False
        json_tmp.write_text(json.dumps(creux, ensure_ascii=False))
        lire(json_tmp)
    except ValueError:
        lire_ok = True
    finally:
        json_tmp.unlink(missing_ok=True)
    v("une mesure sans son contrôle vide est REFUSÉE", lire_ok)

    dessiner(d, sortie)
    print()
    if echecs:
        print(f"ÉCHEC ({echecs} failures, {faits} checks)")
    else:
        print(f"ALL PASS (0 failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_coherence_creuse_t_elle_a_la_frontiere.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "179_la_coherence_creuse_t_elle_a_la_frontiere.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
