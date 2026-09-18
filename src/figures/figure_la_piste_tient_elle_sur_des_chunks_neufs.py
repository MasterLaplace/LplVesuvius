"""La piste de `191` tient-elle sur des chunks qu'elle n'a jamais vus ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'hypothèse telle que `191` l'a
publiée, et le changement de prix : dix-neuf observables cherchés là, UN seul déclaré ici. En haut à
droite, l'étalon à trois faces — elle porte l'étiquette, elle la porte à l'envers, elle n'est que du
bruit. En bas à gauche, les chunks neufs et l'écart observé posé au milieu de ses mélanges. En bas à
droite, chercher contre confirmer, planchers côte à côte.

  uv run python src/figures/figure_la_piste_tient_elle_sur_des_chunks_neufs.py \\
      --json docs/mesures/la_piste_tient_elle_sur_des_chunks_neufs.json \\
      --sortie docs/images/192_la_piste_tient_elle_sur_des_chunks_neufs.png
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

LES_FACES = (("elle porte l'étiquette", "elle_porte_letiquette"),
             ("elle la porte à l'ENVERS", "elle_la_porte_a_lenvers"),
             ("elle n'est que du bruit", "elle_nest_que_du_bruit"))


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
    """Le JSON de `la_piste_tient_elle_sur_des_chunks_neufs.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES TROIS FACES. La face à l'ENVERS est celle
    qui compte : un instrument qui la tiendrait prendrait la valeur absolue sans le dire, donc la
    direction publiée par `191` ne servirait à rien et le test ne serait pas celui qu'on annonce.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "le_verdict", "la_piste_de_191"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("letalon_separe_les_trois"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses trois faces")
    # ⚠⚠⚠ ET REFUSE UN COMPTE OU L'INSTRUMENT EST AVEUGLE. Un premier essai a rendu vingt-trois
    # chunks dont trois retiennent : une colonne portant l'etiquette n'y survivait pas a la
    # permutation, donc son silence n'aurait rien voulu dire.
    if not v.get("le_compte_suffit"):
        raise ValueError(f"{chemin} : le compte ne suffit pas pour que l'étalon voie")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if v.get("la_piste_tient"):
        return ("La piste de `191` tient-elle sur des chunks neufs ? — OUI, sur une matière "
                "qu'elle n'avait jamais vue")
    return ("La piste de `191` tient-elle sur des chunks neufs ? — NON, ce qu'elle avait nommé ne "
            "se retrouve pas")


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

    v, e, p = d["le_verdict"], d["letalon"], d["la_piste_de_191"]
    tient = bool(v.get("la_piste_tient"))
    coul_v = BON if tient else ALERTE
    signe = "★" if tient else "✗"
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46,
           f"{d['segments_neufs']} segments neufs après les {d['segments_deja_vus']} déjà vus · "
           f"{v['chunks_neufs']} chunks dont {v['chunks_neufs_qui_retiennent']} retiennent · "
           f"UN seul observable déclaré, donc {d['tirages']} mélanges le paient · part des "
           f"réplicats où l'étalon voit sa porteuse : "
           f"{_fr(v.get('letalon_voit_a_ce_compte'), 4)}", petit, GRIS)

    # ---- panneau 1 : l'hypothèse
    x0, y0, pw, ph = 56, 122, 620, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'hypothèse, telle que `191` l'a publiée", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 12, f"« {p.get('nom', '—')} »", moyen, CONTRE)
    for k, (nom, val) in enumerate(
            (("son aire, chez `191`", _fr(p.get("aire"), 4)),
             ("sa séparation, chez `191`", _fr(p.get("separation"), 4)),
             ("le plancher qu'elle devait franchir", _fr(p.get("le_plancher_de_la_recherche"), 4)),
             ("les observables que `191` cherchait", str(p.get("observables_de_la_recherche"))),
             ("les chunks sur lesquels elle l'a nommée", str(p.get("chunks_de_la_recherche"))))):
        yy = y0 + 42 + k * 20
        ecrire(x0 + 14, yy, nom, 0, GRIS)
        ecrire(x0 + 330, yy, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 154,
           "★ `191` CHERCHAIT, donc elle avait le droit de regarder dix-neuf colonnes et", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 170,
           "elle a payé dix-neuf. Ce fichier ne cherche plus : UN observable, fixé et", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 186,
           "publié avant de voir la donnée, donc il paie UN.", petit, ENCRE)
    ecrire(x0 + 14, y0 + 210,
           "⚠⚠⚠ Et la confirmation se fait sur des chunks NEUFS : rejouer le test sur la", petit,
           GRIS)
    ecrire(x0 + 14, y0 + 226,
           "matière qui a servi à choisir ne mesurerait que le choix qu'on y a fait.", petit, GRIS)

    # ---- panneau 2 : l'étalon
    x0, y0, pw, ph = 712, 122, 592, 250
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — trois colonnes, mêmes chunks, même étiquette", moyen, ENCRE)
    hautE = max([abs(float((e.get(c) or {}).get("lecart_dans_le_sens_declare") or 0.0))
                 for _n, c in LES_FACES]
                + [float((e.get(c) or {}).get("le_plancher_de_detection") or 0.0)
                   for _n, c in LES_FACES] + [0.01]) * 1.2
    for k, (nom, cle) in enumerate(LES_FACES):
        x = e.get(cle) or {}
        yy = y0 + 12 + k * 72
        ecrire(x0 + 14, yy, nom, moyen, ENCRE)
        if not x.get("decidable"):
            ecrire(x0 + 14, yy + 20, str(x.get("raison")), 0, ALERTE)
            continue
        ok = bool(x["la_piste_tient"]) == bool(x["attendu"])
        ecrire(x0 + 14, yy + 20,
               f"attendu « {'tient' if x['attendu'] else 'ne tient pas'} »", 0, GRIS)
        ecrire(x0 + 250, yy + 20, f"{'★' if ok else '✗'} tient {x['la_piste_tient']}", 0,
               BON if ok else ALERTE)
        ecrire(x0 + 14, yy + 38,
               f"écart    {_fr(x['lecart_dans_le_sens_declare'], 4)}", 0, CONTRE)
        barre(x0 + 200, yy + 40, 350,
              max(0.0, float(x["lecart_dans_le_sens_declare"])) / hautE, 8, CONTRE)
        ecrire(x0 + 14, yy + 54,
               f"plancher {_fr(x['le_plancher_de_detection'], 4)}", 0, GRIS)
        barre(x0 + 200, yy + 56, 350, float(x["le_plancher_de_detection"]) / hautE, 8, GRIS)
    ecrire(x0 + 14, y0 + 228,
           "⚠⚠⚠ La face à l'ENVERS est celle qui compte : le test est UNILATÉRAL.", petit, GRIS)

    # ---- panneau 3 : les chunks neufs
    x0, y0, pw, ph = 56, 424, 620, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les chunks neufs — l'écart observé au milieu de ses mélanges", moyen,
           ENCRE)
    ecarts = sorted((v.get("le_nul") or {}).get("les_ecarts") or [], reverse=True)
    hautN = max([abs(x) for x in ecarts]
                + [abs(float(v.get("lecart_dans_le_sens_declare") or 0.0)), 0.01]) * 1.2
    for k, m in enumerate(ecarts):
        yy = y0 + 14 + k * 7
        barre(x0 + 130, yy, 300, max(0.0, float(m)) / hautN, 5, GRIS)
        if k == 0:
            ecrire(x0 + 14, yy - 3, "les mélanges", 0, GRIS)
    yy = y0 + 14 + len(ecarts) * 7 + 12
    ecrire(x0 + 14, yy - 3, "l'observé", 0, CONTRE)
    barre(x0 + 130, yy, 300, max(0.0, float(v.get("lecart_dans_le_sens_declare") or 0.0)) / hautN,
          9, CONTRE)
    for k, (nom, val) in enumerate(
            (("l'aire sur les chunks neufs", _fr(v.get("laire"), 4)),
             ("l'écart dans le sens déclaré", _fr(v.get("lecart_dans_le_sens_declare"), 4)),
             ("le plancher d'UN observable", _fr(v.get("le_plancher_de_detection"), 4)),
             ("l'aire qu'il fallait dépasser", _fr(v.get("laire_a_depasser"), 4)))):
        yy2 = y0 + 186 + k * 18
        ecrire(x0 + 14, yy2, nom, 0, GRIS)
        ecrire(x0 + 300, yy2, val, 0, ENCRE)
    ecrire(x0 + 14, y0 + 262,
           f"{signe} l'aire vaut {_fr(v.get('laire'), 4)} pour un seuil de "
           f"{_fr(v.get('laire_a_depasser'), 4)}.", moyen, coul_v)

    # ---- panneau 4 : chercher contre confirmer
    x0, y0, pw, ph = 712, 424, 592, 288
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "chercher contre confirmer — ce que le prix change", moyen, ENCRE)
    hautP = max(float(p.get("le_plancher_de_la_recherche") or 0.0),
                float(v.get("le_plancher_de_detection") or 0.0),
                float(p.get("separation") or 0.0),
                abs(float(v.get("lecart_dans_le_sens_declare") or 0.0)), 0.01) * 1.2
    for k, (nom, val, coul) in enumerate(
            ((f"`191` cherchait {p.get('observables_de_la_recherche')} observables — son plancher",
              p.get("le_plancher_de_la_recherche"), ALERTE),
             ("     et son meilleur écart y atteignait", p.get("separation"), GRIS),
             ("`192` en confirme UN — son plancher",
              v.get("le_plancher_de_detection"), BON),
             ("     et l'écart observé y atteint", v.get("lecart_dans_le_sens_declare"), CONTRE))):
        yy = y0 + 14 + k * 34
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 380, yy, _fr(val, 4), 0, coul)
        barre(x0 + 14, yy + 14, 430, max(0.0, float(val or 0.0)) / hautP, 9, coul)
    ecrire(x0 + 14, y0 + 158,
           "★ Le même observable, la même étiquette, la même règle de permutation :", petit,
           ENCRE)
    ecrire(x0 + 14, y0 + 174,
           "seule la LIBERTÉ change, et c'est elle qui fixe le plancher.", petit, ENCRE)
    for k, (nom, ok) in enumerate(
            (("l'étalon sépare ses trois faces", v.get("letalon_separe_les_trois")),
             ("le compte suffit pour VOIR", v.get("le_compte_suffit")),
             ("les chunks sont neufs", int(d.get("segments_neufs") or 0) > 0),
             ("le sens était déclaré avant", int(d.get("le_sens_declare") or 0) > 0),
             ("la piste tient sur des chunks neufs", v.get("la_piste_tient")))):
        yy = y0 + 200 + k * 16
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  CHERCHER ET CONFIRMER NE COÛTENT PAS LE MÊME PRIX, ET C'EST LA PREMIÈRE FOIS QUE LA "
           f"CHAÎNE LE PAIE SÉPARÉMENT. `191` avait le droit de regarder",
           moyen, ENCRE)
    ecrire(78, y + 46,
           f"     {p.get('observables_de_la_recherche')} colonnes, donc son plancher valait "
           f"{_fr(p.get('le_plancher_de_la_recherche'), 4)} ; ce fichier n'en regarde qu'UNE, fixée "
           f"et publiée avant de voir la donnée, donc le sien vaut "
           f"{_fr(v.get('le_plancher_de_detection'), 4)}.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  SUR {v['chunks_neufs']} CHUNKS QUE `191` N'AVAIT JAMAIS VUS, l'aire du plafond "
           f"lu dans la matière vaut {_fr(v.get('laire'), 4)} là où `191` publiait "
           f"{_fr(p.get('aire'), 4)} — il en fallait {_fr(v.get('laire_a_depasser'), 4)}.",
           moyen, coul_v)
    ecrire(78, y + 106,
           f"     {'La piste tient : ce que `191` avait nommé se retrouve sur une matière neuve.'
                  if tient else
                  'La piste ne tient pas : ce que `191` avait nommé ne se retrouve pas ailleurs.'}",
           moyen, coul_v)
    ecrire(78, y + 138,
           "★  ET L'ÉTALON SÉPARE SES TROIS FACES, dont celle qui compte vraiment : une colonne qui "
           "porte l'étiquette À L'ENVERS ne tient PAS. Le test est", moyen, ENCRE)
    ecrire(78, y + 166,
           "     unilatéral, dans la direction que `191` avait publiée, et un instrument qui "
           "tiendrait aussi l'envers prendrait la valeur absolue sans le dire.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ La campagne s'est DIMENSIONNÉE sur l'étalon : on collecte segment par segment "
           f"jusqu'à ce qu'une colonne portant l'étiquette survive à TOUS les réplicats — part "
           f"atteinte ici : {_fr(v.get('letalon_voit_a_ce_compte'), 4)}.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(0.5, 1), _fr(0.5654, 4)) == ("90", "0,5", "0,5654"),
      f"{(_fr(90.0, 0), _fr(0.5, 1), _fr(0.5654, 4))}")
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
    # sous un cadre. Defaut vu en REGARDANT l'image de `190`.
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    import copy  # noqa: PLC0415

    # ★★★★ L'AIRE OBSERVEE ET CELLE QU'IL FALLAIT SONT LUES DES DEUX COTES : c'est leur COMPARAISON
    # qui est le resultat, et l'une sans l'autre ne dirait rien.
    for cle, val in (("laire", 0.5151), ("laire_a_depasser", 0.7373),
                     ("lecart_dans_le_sens_declare", 0.1212),
                     ("le_plancher_de_detection", 0.1919)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, 4) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ CE QUE `191` AVAIT PUBLIE EST LU DES DEUX COTES : sans lui, on ne verrait pas que l'aire
    # a CHUTE.
    for cle, val in (("aire", 0.9191), ("le_plancher_de_la_recherche", 0.4545),
                     ("separation", 0.4191)):
        faux = copy.deepcopy(d)
        faux["la_piste_de_191"][cle] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if _fr(val, 4) in t)
        v(f"★★★★ « {cle} » de `191` est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★ LES TROIS FACES DE L'ETALON SONT DESSINEES AVEC LEURS DEUX LECTURES.
    for nom, cle in LES_FACES:
        faux = copy.deepcopy(d)
        faux["letalon"][cle]["lecart_dans_le_sens_declare"] = 0.6161
        faux["letalon"][cle]["le_plancher_de_detection"] = 0.7171
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (0.6161, 0.7171) if any(_fr(m, 4) in t for _x, _y, t, _f in p4))
        v(f"★★★ la face « {nom} » est dessinée avec ses deux lectures", n == 2, f"{n} sur 2")

    # ★★★ CHAQUE MELANGE EST DESSINE : c'est la distribution qui rend le plancher lisible.
    faux = copy.deepcopy(d)
    n_av = len(dessiner(faux, sortie)[4])
    faux["le_verdict"]["le_nul"]["les_ecarts"] = (
        list(faux["le_verdict"]["le_nul"]["les_ecarts"]) + [0.1111])
    n_ap = len(dessiner(faux, sortie)[4])
    v("★★★ un mélange de plus est une barre de plus", n_ap == n_av + 1, f"{n_av} puis {n_ap}")

    # ★★★★ UN ETALON QUI NE SEPARE PAS, OU UN COMPTE AVEUGLE, FONT REFUSER LA MESURE.
    import tempfile  # noqa: PLC0415

    for cle in ("letalon_separe_les_trois", "le_compte_suffit"):
        rouge = copy.deepcopy(d)
        rouge["le_verdict"][cle] = False
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
        v(f"★★★★ « {cle} » à faux fait REFUSER la mesure", refuse)

    # ★★★★ LES DEUX BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for tient, attendu in ((True, "OUI"), (False, "NON")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["la_piste_tient"] = tient
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p5, 1360) and not textes_hors_cadre(p5, cadres)
          and not textes_qui_se_recouvrent(p5))
    v("★★★★ les deux branches sont distinctes", len(set(branches)) == 2, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_la_piste_tient_elle_sur_des_chunks_neufs.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_piste_tient_elle_sur_des_chunks_neufs.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "192_la_piste_tient_elle_sur_des_chunks_neufs.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
