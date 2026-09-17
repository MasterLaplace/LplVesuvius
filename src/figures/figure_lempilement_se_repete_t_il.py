"""L'empilement se répète-t-il, ou est-ce la même feuille ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon : une matière construite
pour se répéter le dit, une matière construite pour dériver le dit aussi. En haut à droite, la courbe
du rouleau — un transfert porté de plus en plus loin, contre ses couches mélangées. En bas à gauche,
la remontée et où elle commence. En bas à droite, les deux portées : celle d'un CHEMIN et celle d'un
SAUT.

  uv run python src/figures/figure_lempilement_se_repete_t_il.py \\
      --json docs/mesures/lempilement_se_repete_t_il.json \\
      --sortie docs/images/189_lempilement_se_repete_t_il.png
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
    """Le JSON de `lempilement_se_repete_t_il.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES DEUX FACES. Un instrument qui rendrait la
    même réponse à une matière construite pour se répéter et à une matière construite pour dériver
    lirait sa propre échelle, et rien de ce qu'il rend du rouleau ne se lit.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "les_segments", "le_verdict"):
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
    if v.get("lempilement_se_repete"):
        queue = "il SE RÉPÈTE au pas d'une feuille"
    elif v.get("la_texture_decroit_partout"):
        queue = "NI l'un NI l'autre : la texture décroît sans jamais revenir"
    else:
        queue = "NON, et ce qui porte est la CONTIGUÏTÉ"
    return f"L'empilement se répète-t-il ? — {queue}"


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
    exc = v["lexcedent"]
    coul_v = BON if v.get("lempilement_se_repete") else ALERTE
    signe = "★" if v.get("lempilement_se_repete") else "✗"
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46, f"{d['departs_par_couche']} départs par couche · {v['chunks_lus']} chunks · "
                   f"échelle au pas de {d['sommet_relu_de_188']} couches (le sommet de `188`) · "
                   f"le pas vaut {v['le_pas_en_couches']} couches · voxel "
                   f"{_fr(d['voxel_um'], 1)} µm", petit, GRIS)

    # ---- panneau 1 : l'étalon
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — deux matières dont la réponse est CONNUE", moyen, ENCRE)
    for k, x in enumerate(e["lignes"]):
        yy = y0 + 14 + k * 92
        ecrire(x0 + 14, yy, x["matiere"], moyen, ENCRE)
        ecrire(x0 + 14, yy + 22, f"attendu « {x['attendu']} »", 0, GRIS)
        if not x.get("decidable"):
            ecrire(x0 + 200, yy + 22, str(x.get("raison")), 0, ALERTE)
            continue
        ok = (x["lempilement_se_repete"] if x["attendu"] == "se répète"
              else x["la_texture_decroit_partout"])
        ecrire(x0 + 200, yy + 22,
               f"{'★' if ok else '✗'} se répète {x['lempilement_se_repete']} · décroît partout "
               f"{x['la_texture_decroit_partout']}", 0, BON if ok else ALERTE)
        ecrire(x0 + 14, yy + 42,
               f"remontée {_fr(x['lexcedent'].get('la_remontee_maximale'), 2)} depuis le creux de "
               f"{_fr(x['lexcedent'].get('le_creux'), 2)} à "
               f"{x['lexcedent'].get('le_creux_en_couches')} couches,", 0, ENCRE)
        ecrire(x0 + 14, yy + 58,
               f"et elle commence à {x['lexcedent'].get('elle_commence_a')} couches.", 0, ENCRE)
        haut = max([float(b["pas_median"] or 0.0) for b in x["barreaux"]] + [1.0])
        for j, b in enumerate(x["barreaux"]):
            barre(x0 + 14 + j * 48, yy + 78, 44,
                  float(b["pas_median"] or 0.0) / haut, 8,
                  BON if int(b["montee"]) == int(v["le_pas_en_couches"]) else CONTRE)
    ecrire(x0 + 14, y0 + 226,
           "⚠⚠ Une périodicité de plis rend un PLATEAU de retour, pas un pic : la matière", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 242,
           "redevient semblable sur toute l'épaisseur d'un pli, pas sur une seule couche.", petit,
           GRIS)

    # ---- panneau 2 : la courbe
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau — un transfert porté de plus en plus loin", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 8, "écart", petit, GRIS)
    ecrire(x0 + 140, y0 + 8, "vraie", petit, BON)
    ecrire(x0 + 210, y0 + 8, "mélangée", petit, GRIS)
    ecrire(x0 + 300, y0 + 8, "excédent", petit, ALERTE)
    hautc = max([float(b["pas_median"] or 0.0) for b in v["courbe"]] + [1.0]) * 1.05
    for k, b in enumerate(v["courbe"]):
        yy = y0 + 26 + k * 17
        au_pas = int(b["montee"]) == int(v["le_pas_en_couches"])
        ecrire(x0 + 14, yy, f"{b['montee']:>3} c · {_fr(b['montee_um'], 1)} µm", 0,
               ENCRE if au_pas else GRIS)
        ecrire(x0 + 140, yy, _fr(b["pas_median"], 2), 0, BON)
        ecrire(x0 + 210, yy, _fr(b["pas_median_melange"], 2), 0, GRIS)
        ecrire(x0 + 300, yy, _fr(b["excedent"], 2), 0, ALERTE)
        barre(x0 + 360, yy + 2, 210, float(b["pas_median"] or 0.0) / hautc, 7,
              ENCRE if au_pas else BON)
    ecrire(x0 + 14, y0 + 236,
           f"⚠ La ligne foncée est le pas entre deux feuilles, à "
           f"{_fr(v['la_bosse_tombe_a_um'], 1)} µm.", petit, GRIS)

    # ---- panneau 3 : la remontée
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "la remontée, et où elle commence", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14,
           "Une matière qui se répète voit sa lecture CHUTER puis REVENIR au pas. La", petit, ENCRE)
    ecrire(x0 + 14, y0 + 30,
           "remontée maximale doit donc commencer AU pas, et pas ailleurs.", petit, ENCRE)
    for k, (nom, val, coul) in enumerate(
            (("le creux de la courbe", exc.get("le_creux_en_couches"), CONTRE),
             ("la remontée commence à", exc.get("elle_commence_a"), ALERTE),
             ("le pas entre deux feuilles", v.get("le_pas_en_couches"), ENCRE))):
        yy = y0 + 60 + k * 32
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 240, yy, f"{val} couches", 0, coul)
        barre(x0 + 350, yy + 2, 230,
              float(val or 0.0) / (float(v["le_pas_en_couches"]) * 1.25), 12, coul)
    ecrire(x0 + 14, y0 + 164,
           f"{signe} la remontée maximale vaut "
           f"{_fr(exc.get('la_remontee_maximale'), 2)} et commence à "
           f"{exc.get('elle_commence_a')} couches,", moyen, coul_v)
    ecrire(x0 + 14, y0 + 186,
           f"     pas à {v['le_pas_en_couches']} : l'empilement ne se répète pas au pas d'une "
           f"feuille." if not v.get("lempilement_se_repete")
           else f"     c'est-à-dire AU pas : l'empilement se répète.", moyen, coul_v)
    ecrire(x0 + 14, y0 + 216,
           f"⚠⚠ Le mélange remonte de {_fr(v['le_melange'].get('la_remontee_maximale'), 2)} au même "
           f"barreau : c'est ce que la", petit, GRIS)
    ecrire(x0 + 14, y0 + 232,
           "quantification et la marche rapportent toutes seules, et il price la matière.", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 252,
           f"⚠ {v['chunks_qui_se_repetent']} chunks sur {v['chunks_lus']} se répètent pris "
           f"séparément ; la courbe médiane, non.", petit, GRIS)

    # ---- panneau 4 : les deux portées
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "un CHEMIN contre un SAUT — et c'est le résultat", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 14,
           "`188` mesurait un RUBAN, qui traverse toute la matière intermédiaire.", petit, ENCRE)
    ecrire(x0 + 14, y0 + 30,
           "Ici le transfert SAUTE d'une couche à l'autre sans rien lire entre.", petit, ENCRE)
    hautp = max(float(v.get("la_portee_du_chemin_um") or 0.0),
                float(v.get("la_portee_du_transfert_um") or 0.0)) * 1.2
    for k, (nom, val, coul) in enumerate(
            ((f"un chemin (`188`), au moins", v.get("la_portee_du_chemin_um"), BON),
             ("un saut direct", v.get("la_portee_du_transfert_um"), ALERTE))):
        yy = y0 + 62 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 210, yy, f"{_fr(val, 1)} µm", 0, coul)
        barre(x0 + 300, yy + 2, 260, float(val or 0.0) / hautp, 13, coul)
    ecrire(x0 + 14, y0 + 140,
           f"★ le chemin porte {_fr(v.get('le_chemin_porte_plus_loin_fois'), 4)} fois plus loin "
           f"que le saut :", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 162,
           "     ce que l'ordre en profondeur porte est la CONTIGUÏTÉ,", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 184,
           "     et non la ressemblance à distance.", moyen, ENCRE)
    for k, (nom, ok) in enumerate(
            (("l'étalon sépare ses deux faces", v.get("letalon_separe_les_deux")),
             ("l'empilement se répète au pas", v.get("lempilement_se_repete")),
             ("la contiguïté porte plus loin",
              v.get("la_contiguite_porte_plus_loin_que_la_ressemblance")))):
        yy = y0 + 214 + k * 20
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           "★  L'ÉTALON SÉPARE SES DEUX FACES : une matière dont chaque feuille copie la précédente "
           "est lue « se répète », une matière qui tourne lentement est lue « décroît", moyen, ENCRE)
    ecrire(78, y + 46,
           f"     partout ». ⚠⚠ Et il a fallu deux réparations pour ça : une périodicité de plis rend "
           f"un PLATEAU de retour et non un pic, et la remontée doit COMMENCER au pas.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  L'EMPILEMENT DU ROULEAU NE SE RÉPÈTE PAS AU PAS D'UNE FEUILLE : sa remontée "
           f"maximale vaut {_fr(exc.get('la_remontee_maximale'), 2)} et commence à "
           f"{exc.get('elle_commence_a')} couches, pas à {v['le_pas_en_couches']}.", moyen, coul_v)
    ecrire(78, y + 106,
           f"     L'information que `188` mesurait n'est donc PAS « une spire ressemble à la "
           f"suivante ».", moyen, coul_v)
    ecrire(78, y + 138,
           f"★  ET CE QUI PORTE EST LA CONTIGUÏTÉ : un CHEMIN porte au moins "
           f"{_fr(v.get('la_portee_du_chemin_um'), 1)} µm (`188`) quand un SAUT direct meurt à "
           f"{_fr(v.get('la_portee_du_transfert_um'), 1)} µm — "
           f"{_fr(v.get('le_chemin_porte_plus_loin_fois'), 4)} fois plus loin.", moyen, ENCRE)
    ecrire(78, y + 166,
           "     Deux couches voisines se ressemblent, et cette ressemblance CHAÎNE le long d'un "
           "parcours ; deux couches éloignées sont aussi étrangères que deux au hasard.", moyen,
           ENCRE)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche ne dit pas : que ce chaînage suffise à poser une surface. Il dit "
           "qu'une surface doit avancer PAS À PAS en profondeur, et qu'aucun saut ne la rattrape.",
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

    # ★★★★ CHAQUE BARREAU DE LA COURBE EST DESSINE AVEC SES TROIS LECTURES.
    for k in range(len(d["le_verdict"]["courbe"])):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["courbe"][k]["pas_median"] = 11.0 + k
        faux["le_verdict"]["courbe"][k]["pas_median_melange"] = 31.0 + k
        faux["le_verdict"]["courbe"][k]["excedent"] = 51.0 + k
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (11.0 + k, 31.0 + k, 51.0 + k)
                if any(_fr(m, 2) in t for _x, _y, t, _f in p2))
        v(f"★★★ le barreau {k} est dessiné avec ses trois lectures", n == 3, f"{n} sur 3")

    # ★★★★ LES DEUX PORTEES SONT LUES DES DEUX COTES : c'est leur ECART qui est le resultat.
    # ⚠⚠ LES VALEURS DE SONDE SURVIVENT A L'ARRONDI DU RENDU : la figure ecrit UNE decimale pour
    # les portees, donc une sonde a deux n'apparaitrait nulle part et la verification serait rouge
    # pour une raison de mise en forme et non de contenu.
    for cle, val, dec in (("la_portee_du_chemin_um", 211.2, 1),
                          ("la_portee_du_transfert_um", 47.5, 1),
                          ("le_chemin_porte_plus_loin_fois", 6.1234, 4)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if _fr(val, dec) in t)
        v(f"★★★★ {cle} est lue des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET OU LA REMONTEE COMMENCE EST LU DES DEUX COTES : c'est l'enonce de la tranche.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["lexcedent"]["elle_commence_a"] = 41
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p4 if "41" in t)
    v("★★★★ l'endroit où la remontée commence est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET UN ETALON QUI NE SEPARE PAS FAIT REFUSER LA MESURE.
    rouge = copy.deepcopy(d)
    rouge["le_verdict"]["letalon_separe_les_deux"] = False
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
    v("★★★★ un étalon qui ne sépare pas fait REFUSER la mesure", refuse)

    # ★★★ CHAQUE MATIERE DE L'ETALON EST DESSINEE.
    for k in range(len(d["letalon"]["lignes"])):
        faux = copy.deepcopy(d)
        faux["letalon"]["lignes"][k]["lexcedent"]["la_remontee_maximale"] = 71.0 + k
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p5 if _fr(71.0 + k, 2) in t)
        v(f"★★★ la matière {k} de l'étalon est dessinée", n >= 1, f"{n} mentions")

    # ★★★★ LES TROIS BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for rep, dec, attendu in ((True, False, "SE RÉPÈTE"), (False, True, "NI l'un NI l'autre"),
                              (False, False, "CONTIGUÏTÉ")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["lempilement_se_repete"] = rep
        faux["le_verdict"]["la_texture_decroit_partout"] = dec
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p6, 1360) and not textes_hors_cadre(p6, cadres)
          and not textes_qui_se_recouvrent(p6))
    v("★★★★ les trois branches sont distinctes", len(set(branches)) == 3, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_lempilement_se_repete_t_il.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "lempilement_se_repete_t_il.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "189_lempilement_se_repete_t_il.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
