"""Jusqu'où une surface peut-elle dériver avant que la matière cesse de se lire ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon : des matières dont la
vitesse de rotation en profondeur est posée, et dont la portée croît quand elles tournent plus
lentement. En haut à droite, la courbe du rouleau — la vraie matière contre ses couches mélangées, à
chaque barreau de l'échelle. En bas à gauche, les segments. En bas à droite, la seule comparaison qui
compte : la portée contre le pas entre deux feuilles.

  uv run python src/figures/figure_jusquou_une_surface_peut_elle_deriver.py \\
      --json docs/mesures/jusquou_une_surface_peut_elle_deriver.json \\
      --sortie docs/images/188_jusquou_une_surface_peut_elle_deriver.png
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
    """Le JSON de `jusquou_une_surface_peut_elle_deriver.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON N'ORDONNE PAS SES PORTÉES. Si l'instrument rend la même
    portée à des matières qui tournent à des vitesses différentes, il mesure sa propre échelle et
    rien de ce qu'il rend du rouleau ne se lit — c'est le précédent de `181`, où rien n'a été publié
    pendant que le contrôle était rouge.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "les_segments", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("letalon_ordonne_les_portees"):
        raise ValueError(f"{chemin} : l'étalon n'ordonne pas ses portées")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if not v.get("la_portee_se_lit_sur_le_rouleau") and not v.get("au_dela_de_lechelle"):
        queue = "la matière ne se sépare pas de son mélange"
    elif v.get("au_dela_de_lechelle"):
        queue = "au-delà de TOUTE l'échelle, donc au-delà d'un pas de feuille"
    elif v.get("elle_franchit_un_pas_entre_deux_feuilles"):
        queue = "au-delà d'un pas entre deux feuilles"
    else:
        queue = "en deçà d'un pas entre deux feuilles"
    return f"Jusqu'où une surface peut-elle dériver ? — {queue}"


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
    pas_um = float(v["le_pas_entre_deux_feuilles_um"])
    coul_v = BON if v.get("elle_franchit_un_pas_entre_deux_feuilles") else ALERTE
    signe = "★" if v.get("elle_franchit_un_pas_entre_deux_feuilles") else "✗"
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46, f"{d['departs_par_couche']} départs par couche · treillis "
                   f"{d['cote_du_treillis']}×{d['cote_du_treillis']} · {v['chunks_lus']} chunks · "
                   f"échelle {d['montees']} couches · plafond du ruban "
                   f"{v.get('plafond_du_ruban_median')} pas · voxel {_fr(d['voxel_um'], 1)} µm",
           petit, GRIS)

    # ---- panneau 1 : l'étalon, une échelle de vitesses
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — des matières dont la VITESSE de rotation est posée", moyen,
           ENCRE)
    ecrire(x0 + 14, y0 + 10, "la matière tourne de", petit, GRIS)
    ecrire(x0 + 200, y0 + 10, "portée lue", petit, ALERTE)
    ecrire(x0 + 360, y0 + 10, "excédent maximal", petit, ENCRE)
    hautp = max([float(x.get("excedent_maximal") or 0.0) for x in e["lignes"]] + [1.0]) * 1.2
    for k, x in enumerate(e["lignes"]):
        yy = y0 + 34 + k * 36
        ecrire(x0 + 14, yy, f"{_fr(x.get('degres_par_couche'), 4)} °/couche", 0, ENCRE)
        if not x.get("decidable"):
            ecrire(x0 + 200, yy, "ne se sépare jamais", 0, GRIS)
        elif x.get("au_dela_de_lechelle"):
            ecrire(x0 + 200, yy, "au-delà de l'échelle", 0, BON)
        else:
            ecrire(x0 + 200, yy, f"{x['portee_en_couches']} couches", 0, ALERTE)
        ecrire(x0 + 360, yy, f"{_fr(x.get('excedent_maximal'), 2)} pas", 0, ENCRE)
        barre(x0 + 440, yy + 2, 160, float(x.get("excedent_maximal") or 0.0) / hautp, 10, ENCRE)
    ecrire(x0 + 14, y0 + 182,
           f"★ la portée croît quand la matière tourne plus lentement : "
           f"{v.get('la_portee_la_plus_courte_de_letalon')} couches", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 204,
           f"     puis {v.get('la_portee_la_plus_longue_de_letalon')}, puis au-delà de l'échelle, "
           f"puis plus de séparation du tout.", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 230,
           "⚠⚠ Le même QUART DE TOUR étalé sur un doublement de couches : le tour total", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 246,
           "s'annule dans la comparaison, et ce qui reste est la vitesse.", petit, GRIS)

    # ---- panneau 2 : la courbe
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau — la vraie matière contre ses couches mélangées", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 8, "montée", petit, GRIS)
    ecrire(x0 + 130, y0 + 8, "vraie", petit, BON)
    ecrire(x0 + 200, y0 + 8, "mélangée", petit, GRIS)
    ecrire(x0 + 290, y0 + 8, "excédent", petit, ALERTE)
    hautc = max([float(b["pas_median"] or 0.0) for b in v["courbe"]] + [1.0]) * 1.1
    for k, b in enumerate(v["courbe"]):
        yy = y0 + 28 + k * 24
        ecrire(x0 + 14, yy, f"{b['montee']:>3} c · {_fr(b['montee_um'], 1)} µm", 0, ENCRE)
        ecrire(x0 + 130, yy, _fr(b["pas_median"], 2), 0, BON)
        ecrire(x0 + 200, yy, _fr(b["pas_median_melange"], 2), 0, GRIS)
        ecrire(x0 + 290, yy, _fr(b["excedent"], 2), 0, ALERTE)
        barre(x0 + 350, yy + 2, 220, float(b["excedent"] or 0.0) / hautc, 9, ALERTE)
    ecrire(x0 + 14, y0 + 244,
           f"⚠ L'excédent culmine à {v.get('sommet_en_couches')} couches et reste positif jusqu'à "
           f"{_fr(v.get('portee_minimale_um'), 2)} µm.", petit, GRIS)

    # ---- panneau 3 : les segments
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois segments", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 10, "segment", petit, GRIS)
    ecrire(x0 + 200, y0 + 10, "chunks", petit, GRIS)
    ecrire(x0 + 290, y0 + 10, "portée", petit, ALERTE)
    ecrire(x0 + 440, y0 + 10, "excédent max", petit, ENCRE)
    lus = [s for s in d["les_segments"] if s.get("decidable")]
    for k, s in enumerate(lus):
        yy = y0 + 34 + k * 30
        ecrire(x0 + 14, yy, s["segment"], 0, ENCRE)
        ecrire(x0 + 200, yy, str(s["chunks_lus"]), 0, ENCRE)
        ecrire(x0 + 290, yy, ("au-delà de l'échelle" if s.get("au_dela_de_lechelle")
                              else f"{s.get('portee_en_couches')} couches"), 0,
               BON if s.get("au_dela_de_lechelle") else ALERTE)
        ecrire(x0 + 440, yy, f"{_fr(s.get('excedent_maximal'), 2)} pas", 0, ENCRE)
    ecrire(x0 + 14, y0 + 134,
           "⚠⚠ Le nul est le mélange de l'ORDRE des couches : il garde chaque couche intacte —", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 150,
           "même texture, même direction de fibres — et ne détruit que le fait que deux", petit, GRIS)
    ecrire(x0 + 14, y0 + 166,
           "couches voisines appartiennent à la même feuille. Une décroissance qui lui", petit, GRIS)
    ecrire(x0 + 14, y0 + 182,
           "survivrait serait celle du ruban et non celle de la matière.", petit, GRIS)
    ecrire(x0 + 14, y0 + 210,
           "⚠⚠⚠ Ce que l'excédent NE dit pas : que ce soit la même feuille. Il dit que", petit,
           ALERTE)
    ecrire(x0 + 14, y0 + 226,
           "l'ORDRE en profondeur porte de l'information, ce qu'une périodicité de", petit, ALERTE)
    ecrire(x0 + 14, y0 + 242,
           "l'empilement produirait aussi.", petit, ALERTE)

    # ---- panneau 4 : la comparaison qui compte
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la seule comparaison qui compte pour le graal", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14,
           "Un transfert de spire à spire demande de franchir un PAS ENTRE DEUX", petit, ENCRE)
    ecrire(x0 + 14, y0 + 30,
           "FEUILLES en profondeur. La texture porte-t-elle jusque-là ?", petit, ENCRE)
    hautq = max(pas_um, float(v.get("portee_minimale_um") or 0.0)) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("la portée, au moins", v.get("portee_minimale_um"), BON),
             ("le pas entre deux feuilles", pas_um, ENCRE))):
        yy = y0 + 64 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 200, yy, f"{_fr(val, 2)} µm", 0, coul)
        barre(x0 + 290, yy + 2, 270, float(val or 0.0) / hautq, 13, coul)
    ecrire(x0 + 14, y0 + 144,
           f"{signe} soit {_fr(v.get('elle_vaut_le_pas_entre_deux_feuilles_fois'), 4)} fois "
           f"le pas, et c'est une BORNE", moyen, coul_v)
    ecrire(x0 + 14, y0 + 166,
           "     INFÉRIEURE : l'échelle s'arrête là, la matière non.", moyen, coul_v)
    for k, (nom, ok) in enumerate(
            (("l'étalon ordonne ses portées", v.get("letalon_ordonne_les_portees")),
             ("la portée tombe dans l'échelle", v.get("la_portee_se_lit_sur_le_rouleau")),
             ("elle franchit un pas de feuille",
              v.get("elle_franchit_un_pas_entre_deux_feuilles")))):
        yy = y0 + 186 + k * 21
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)
    ecrire(x0 + 14, y0 + 254,
           f"⚠ Le ruban plat atteint {_fr(v['courbe'][0]['pas_median'], 2)} pas ; à la fin de "
           f"l'échelle il n'en fait plus que {_fr(v['courbe'][-1]['pas_median'], 2)}.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  L'ÉTALON ORDONNE SES PORTÉES, DONC L'INSTRUMENT LIT LA MATIÈRE : un quart de tour "
           f"sur quatre couches porte {v.get('la_portee_la_plus_courte_de_letalon')} couches, sur "
           f"seize il en porte", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     {v.get('la_portee_la_plus_longue_de_letalon')}, sur soixante-quatre elle dépasse "
           f"l'échelle, et une matière qui ne tourne pas ne se sépare même pas de son mélange.",
           moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  ET LE ROULEAU PORTE AU-DELÀ DE TOUTE L'ÉCHELLE : l'excédent culmine à "
           f"{_fr(v['excedent_maximal'], 2)} pas à {v.get('sommet_en_couches')} couches "
           f"({_fr(v['courbe'][4]['montee_um'], 1)} µm) et reste positif jusqu'au dernier barreau,",
           moyen, coul_v)
    ecrire(78, y + 106,
           f"     à {_fr(v.get('portee_minimale_um'), 1)} µm — soit "
           f"{_fr(v.get('elle_vaut_le_pas_entre_deux_feuilles_fois'), 4)} fois le pas entre deux "
           f"feuilles. La texture du rouleau porte donc plus loin en profondeur qu'un transfert "
           f"n'en demande.", moyen, coul_v)
    ecrire(78, y + 138,
           f"⚠⚠  CE QUE ÇA NE DIT PAS : que ce soit la MÊME FEUILLE. Le mélange détruit l'ORDRE des "
           f"couches, donc l'excédent mesure que cet ordre porte de l'information — ce qu'une",
           moyen, ALERTE)
    ecrire(78, y + 166,
           f"     périodicité de l'empilement produirait tout autant. ⚠ Et la longueur suivable, "
           f"elle, tombe de {_fr(v['courbe'][0]['pas_median'], 2)} pas à plat à "
           f"{_fr(v['courbe'][-1]['pas_median'], 2)} au dernier barreau.", moyen, ALERTE)
    ecrire(78, y + 198,
           "⚠ La portée du rouleau n'est pas lue mais BORNÉE : l'échelle s'arrête au pas entre deux "
           "feuilles, qui est la distance dont la question dépend, et la matière porte au-delà.",
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
      (_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4)) == ("90", "173", "0,4855"),
      f"{(_fr(90.0, 0), _fr(173.0, 0), _fr(0.4855, 4))}")
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
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    # ★★★★ CHAQUE BARREAU DE L'ECHELLE EST DESSINE, AVEC SES TROIS LECTURES : une courbe dont il
    # manque un barreau ne montre plus OU l'excedent culmine ni jusqu'ou il reste positif.
    for k in range(len(d["le_verdict"]["courbe"])):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["courbe"][k]["pas_median"] = 11.0 + k
        faux["le_verdict"]["courbe"][k]["pas_median_melange"] = 31.0 + k
        faux["le_verdict"]["courbe"][k]["excedent"] = 51.0 + k
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (11.0 + k, 31.0 + k, 51.0 + k)
                if any(_fr(m, 2) in t for _x, _y, t, _f in p2))
        v(f"★★★ le barreau {k} est dessiné avec ses trois lectures", n == 3, f"{n} sur 3")

    # ★★★★ CHAQUE MATIERE DE L'ETALON EST DESSINEE : c'est leur ORDRE qui rend le rouleau lisible.
    for k in range(len(d["letalon"]["lignes"])):
        faux = copy.deepcopy(d)
        faux["letalon"]["lignes"][k]["excedent_maximal"] = 71.0 + k
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if _fr(71.0 + k, 2) in t)
        v(f"★★★ la matière {k} de l'étalon est dessinée", n >= 1, f"{n} mentions")

    # ★★★★ LA BORNE ET LE PAS SONT LUS DES DEUX COTES : une portee sans le pas auquel on la compare
    # ne dit rien, et un rapport sans la portee non plus.
    for cle, val in (("portee_minimale_um", 211.25),
                     ("elle_vaut_le_pas_entre_deux_feuilles_fois", 1.2213)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p4 if _fr(val, 4 if "fois" in cle else 2) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET UN ETALON QUI N'ORDONNE PAS FAIT REFUSER LA MESURE.
    rouge = copy.deepcopy(d)
    rouge["le_verdict"]["letalon_ordonne_les_portees"] = False
    refuse, tmp = False, None
    try:
        import tempfile  # noqa: PLC0415
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(rouge, fh, ensure_ascii=False)
            tmp = Path(fh.name)
        lire(tmp)
    except ValueError:
        refuse = True
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    v("★★★★ un étalon qui n'ordonne pas fait REFUSER la mesure", refuse)

    # ★★★★ LES QUATRE BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for lue, au_dela, franchit, attendu in (
            (False, True, True, "au-delà de TOUTE l'échelle"),
            (True, False, True, "au-delà d'un pas"),
            (True, False, False, "en deçà d'un pas"),
            (False, False, False, "ne se sépare pas")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["la_portee_se_lit_sur_le_rouleau"] = lue
        faux["le_verdict"]["au_dela_de_lechelle"] = au_dela
        faux["le_verdict"]["elle_franchit_un_pas_entre_deux_feuilles"] = franchit
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p5, 1360) and not textes_hors_cadre(p5, cadres)
          and not textes_qui_se_recouvrent(p5))
    v("★★★★ les quatre branches sont distinctes", len(set(branches)) == 4, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_jusquou_une_surface_peut_elle_deriver.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "jusquou_une_surface_peut_elle_deriver.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "188_jusquou_une_surface_peut_elle_deriver.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
