"""Peut-on déplier la phase — l'absolu modulo un pli plus le différentiel qui dérive ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, la phase du creux le long de la rangée :
elle remplit le pli au lieu de le suivre. En bas à gauche, l'unique épreuve déclarée — le pas replié
observé contre ce que rendent les mélanges, et contre ce que `199` rendrait si le creux suivait
vraiment une frontière. En bas au centre, les trois excursions mises en regard, et l'angle mort
hérité. En bas à droite, l'étalon, avec le pas du rouleau placé sur sa propre échelle.

  uv run python src/figures/figure_peut_on_deplier_la_phase.py \\
      --json docs/mesures/peut_on_deplier_la_phase.json \\
      --sortie docs/images/201_peut_on_deplier_la_phase.png
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
    """Le JSON de `peut_on_deplier_la_phase.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS, ET UNE QUI DÉCLARE PLUS D'UNE ÉPREUVE SANS
    EN DIVISER LA GARANTIE : sans la première, le dépliage d'un lecteur aveugle passerait pour un
    résultat ; sans la seconde, une valeur `p` à la garantie se lirait comme un résultat alors
    qu'elle aurait été achetée par le nombre d'épreuves.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("ce_que_200_a_rendu", "ce_que_199_a_rendu", "la_condition_ditoh", "la_marginale",
                "le_depliage", "langle_mort", "laccord", "le_verdict", "letalon",
                "la_phase_en_voxels", "les_colonnes"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle, sous in (("laccord", "le_rapport_au_nul"),
                      ("le_verdict", "le_rapport_a_ce_que_199_rendrait")):
        if d[cle].get(sous) is None:
            raise ValueError(f"{chemin} : {cle}.{sous} est absent, donc le « oui » de l'épreuve "
                             "se lirait sans son ampleur")
    for cle in ("le_depliage", "laccord", "le_verdict", "letalon", "la_condition_ditoh"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n
           - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    if len(d["la_phase_en_voxels"]) != len(d["les_colonnes"]):
        raise ValueError(f"{chemin} : la phase et ses colonnes ne sont pas de même longueur")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    if d["le_verdict"].get("le_depliage_rend_un_ordinal"):
        return "Peut-on déplier la phase ? — OUI, et le dépliage borne ses deux moitiés"
    if d["laccord"].get("la_phase_se_suit"):
        return ("Peut-on déplier la phase ? — elle se suit À PEINE, et le dépliage dérive "
                "plus que ses deux moitiés")
    return "Peut-on déplier la phase ? — NON, la phase ne se suit pas du tout"


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

    c2, c1 = d["ce_que_200_a_rendu"], d["ce_que_199_a_rendu"]
    it, mg, dep = d["la_condition_ditoh"], d["la_marginale"], d["le_depliage"]
    am, ac, ve, e = d["langle_mort"], d["laccord"], d["le_verdict"], d["letalon"]
    pli = float(d["le_pas_dun_pli_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"rangée {c2['la_rangee']} · {c2['les_reperes']} repères de `200` · {c1['les_pas']} pas "
           f"de `199` · pli {_fr(pli, 4)} voxels · demi-période "
           f"{_fr(it['la_demi_periode_en_voxels'], 0)} · une seule épreuve déclarée, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)} · AUCUN téléchargement", petit, GRIS)

    # ---- panneau 1 : la phase le long de la rangée
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "la phase du creux — la couche ramenée MODULO UN PLI, colonne après colonne",
           moyen, ENCRE)
    cols, phases = d["les_colonnes"], d["la_phase_en_voxels"]
    gx0, gy0, gw, gh = x0 + 52, y0 + 16, pw - 98, 202
    cmin, cmax = float(min(cols)), float(max(cols))
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 46, yy - 6, f"{_fr(pli * (1.0 - k / 4.0), 1)}", 0, GRIS)
    for c, v_ in zip(cols, phases):
        px = gx0 + gw * (float(c) - cmin) / max(1.0, cmax - cmin)
        py = gy0 + gh * (1.0 - float(v_) / pli)
        art.ellipse([px - 2, py - 2, px + 2, py + 2], fill=CONTRE)
        points.append((px, py))
    ecrire(gx0, gy0 + gh + 8, f"colonne {int(cmin)}", 0, GRIS)
    ecrire(gx0 + gw - 80, gy0 + gh + 8, f"colonne {int(cmax)}", 0, GRIS)
    ecrire(x0 + 12, y0 + ph - 30,
           f"⚠⚠⚠ La phase REMPLIT le pli au lieu de le suivre : son écart-type vaut "
           f"{_fr(mg['lecart_type_en_voxels'], 4)} voxels quand une couche tirée au hasard DANS LE "
           f"CUBE puis repliée en donnerait {_fr(mg['lecart_type_du_nul_en_voxels'], 4)} — "
           f"rapport {_fr(mg['le_rapport_au_nul'], 4)}.", petit, ALERTE)

    # ---- panneau 2 : l'unique épreuve déclarée
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve : la phase se suit-elle ?", moyen, ENCRE)
    hautE = max(float(ac["le_pas_quadratique_median_du_nul_en_voxels"]),
                float(ac["le_pas_quadratique_observe_en_voxels"]), 1.0) * 1.15
    for k, (nom, val, coul) in enumerate(
            (("pas replié OBSERVÉ", ac["le_pas_quadratique_observe_en_voxels"], ALERTE),
             ("médiane des 19 mélanges",
              ac["le_pas_quadratique_median_du_nul_en_voxels"], GRIS),
             ("si le creux suivait (`199`)",
              it["le_pas_quadratique_de_199_en_voxels"], BON))):
        yy = y0 + 12 + k * 40
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 296, yy, f"{_fr(val, 4)} vx", 0, coul)
        barre(x0 + 12, yy + 16, 372, float(val) / hautE, 10, coul)
    ecrire(x0 + 12, y0 + 134,
           f"{ac['les_melanges_au_moins_aussi_serres']} mélange sur {ac['tirages']} est aussi "
           f"serré · P = {_fr(ac['la_valeur_p'], 2)}", 0, ENCRE)
    ecrire(x0 + 12, y0 + 152,
           f"rapport au nul {_fr(ac['le_rapport_au_nul'], 4)} · soit "
           f"{_fr(ve['le_rapport_a_ce_que_199_rendrait'], 4)} fois `199`", 0, ALERTE)
    suit = bool(ac["la_phase_se_suit"])
    ecrire(x0 + 12, y0 + 176,
           f"{'★' if suit else '✗'} LA PHASE SE SUIT : {suit}", moyen, BON if suit else ALERTE)
    ecrire(x0 + 12, y0 + 204,
           "⚠⚠⚠ ELLE SE SUIT À PEINE : l'épreuve se déclenche au", petit, ALERTE)
    ecrire(x0 + 12, y0 + 218,
           "plancher exact des dix-neuf mélanges, et l'écart au nul", petit, ALERTE)
    ecrire(x0 + 12, y0 + 232, "est de quelques pour cent.", petit, ALERTE)

    # ---- panneau 3 : le dépliage et l'angle mort
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "les trois excursions, et l'angle mort", moyen, ENCRE)
    hautV = max(float(ve["lexcursion_depliee_en_plis"]),
                float(ve["lexcursion_absolue_en_plis"]),
                float(ve["lexcursion_differentielle_en_plis"]), 0.1) * 1.15
    for k, (nom, val, coul) in enumerate(
            (("DÉPLIÉE (ce fichier)", ve["lexcursion_depliee_en_plis"], ALERTE),
             ("absolue (`200`)", ve["lexcursion_absolue_en_plis"], GRIS),
             ("différentielle (`199`)", ve["lexcursion_differentielle_en_plis"], CONTRE))):
        yy = y0 + 10 + k * 36
        ecrire(x0 + 12, yy, nom, 0, coul)
        ecrire(x0 + 286, yy, f"{_fr(val, 6)} pli", 0, coul)
        barre(x0 + 12, yy + 17, 372, float(val) / hautV, 8, coul)
    ecrire(x0 + 12, y0 + 118,
           f"rapport au différentiel {_fr(ve['le_rapport_au_differentiel'], 4)}", 0, ENCRE)
    for k, (nom, val) in enumerate((
            ("pas dépliés hors enveloppe",
             f"{am['les_pas_hors_enveloppe']} sur {am['les_pas']}"),
            ("au bord de l'alias", f"{am['les_pas_au_bord_de_lalias']} sur {am['les_pas']}"),
            ("marge médiane avant l'alias",
             f"{_fr(am['la_marge_mediane_en_voxels'], 4)} vx"),
            ("écarts certifiés au PIRE cas",
             f"{it['les_ecarts_certifies_au_pire']} sur {it['les_ecarts']}"))):
        yy = y0 + 140 + k * 18
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 252, yy, val, 0, ENCRE)
    ecrire(x0 + 12, y0 + 218,
           f"⚠⚠⚠ Pas maximal de `199` : {_fr(it['le_pas_maximal_de_199_en_voxels'], 0)} vx pour "
           f"une limite de", petit, ALERTE)
    ecrire(x0 + 12, y0 + 232,
           f"{_fr(it['la_demi_periode_en_voxels'], 0)} — marge "
           f"{_fr(it['la_marge_du_pas_maximal_en_voxels'], 0)} voxel. Un pas au-delà ALIASE.",
           petit, ALERTE)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — jusqu'où un dépliage tient", moyen, ENCRE)
    ecrire(x0 + 12, y0 + 10,
           f"pas posé → part des {e['replicats']} réplicats qui gardent le compte des plis",
           0, GRIS)
    for k, pt in enumerate(e["la_courbe"]):
        yy = y0 + 32 + k * 22
        part = float(pt["part_des_replicats"])
        ecrire(x0 + 12, yy, f"{_fr(pt['le_pas_pose_en_voxels'], 4)} vx", 0,
               BON if part >= 1.0 else GRIS)
        ecrire(x0 + 96, yy, _fr(part, 3), 0, BON if part >= 1.0 else GRIS)
        barre(x0 + 146, yy + 2, 232, part, 8, BON if part >= 1.0 else CONTRE)
    ecrire(x0 + 12, y0 + 150,
           f"tient jusqu'à {_fr(e['le_pas_qui_tient'], 4)} vx · casse à "
           f"{_fr(e['le_pas_qui_casse'], 4)} vx", 0, ENCRE)
    ecrire(x0 + 12, y0 + 172,
           f"★ sépare : {e['letalon_separe']} · faux {_fr(e['le_taux_de_faux'], 3)} pour "
           f"{_fr(e['la_garantie'], 2)} garantis", 0, BON)
    ecrire(x0 + 12, y0 + 198,
           f"⚠⚠⚠ LE ROULEAU EST À "
           f"{_fr(ac['le_pas_quadratique_observe_en_voxels'], 4)} VOXELS, donc", petit, ALERTE)
    ecrire(x0 + 12, y0 + 212,
           "au-delà du barreau où l'étalon ne garde plus AUCUN", petit, ALERTE)
    ecrire(x0 + 12, y0 + 226,
           "réplicat. Le dépliage y est mort, dans ses propres unités.", petit, ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  LA PHASE NE SE DÉPLIE PAS : l'excursion dépliée vaut "
           f"{_fr(ve['lexcursion_depliee_en_plis'], 6)} pli contre "
           f"{_fr(ve['lexcursion_absolue_en_plis'], 6)} pour `200` et "
           f"{_fr(ve['lexcursion_differentielle_en_plis'], 6)} pour `199` — soit "
           f"{_fr(ve['le_rapport_au_differentiel'], 4)} fois", moyen, ALERTE)
    ecrire(78, y + 46,
           "     PIRE que le différentiel seul. Composer les deux moitiés ne rend pas l'ordinal : "
           "elle ajoute du bruit à une marche qui en avait déjà.", moyen, ALERTE)
    ecrire(78, y + 78,
           f"★  ET POURTANT LA PHASE SE SUIT, TOUT JUSTE : pas replié "
           f"{_fr(ac['le_pas_quadratique_observe_en_voxels'], 4)} voxels contre "
           f"{_fr(ac['le_pas_quadratique_median_du_nul_en_voxels'], 4)} au mélange, "
           f"{ac['les_melanges_au_moins_aussi_serres']}/{ac['tirages']}, P = "
           f"{_fr(ac['la_valeur_p'], 2)}. Un creux qui SUIVRAIT", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     une frontière rendrait {_fr(ve['le_pas_que_199_rendrait_en_voxels'], 4)} "
           f"voxels — le pas que `199` mesure. Le rouleau en est à "
           f"{_fr(ve['le_rapport_a_ce_que_199_rendrait'], 4)} fois cela, et à "
           f"{_fr(ac['le_rapport_au_nul'], 4)} du nul : il REDÉSIGNE une frontière.", moyen, ENCRE)
    ecrire(78, y + 138,
           f"★★★★ LA CONDITION D'ITOH N'EST PAS RÉFUTABLE PAR CETTE MESURE, ET C'EST LE FAIT NEUF : "
           f"le plus grand pas que `199` ait lu vaut "
           f"{_fr(it['le_pas_maximal_de_199_en_voxels'], 0)} voxels pour une limite de "
           f"{_fr(it['la_demi_periode_en_voxels'], 0)},", moyen, ENCRE)
    ecrire(78, y + 166,
           f"     à {_fr(it['la_marge_du_pas_maximal_en_voxels'], 0)} voxel près. Or un pas au-delà "
           f"ALIASE au lieu de saturer, donc « {c1['les_pas_qui_saturent']} pas saturés » ne dit "
           f"rien du pas VRAI : un lecteur ne peut pas voir ce qu'il replie.", moyen, ENCRE)
    ecrire(78, y + 198,
           f"⚠ Et {c1['les_pas_sans_colonne']} pas de `199` n'ont aucune colonne — son cumul n'est "
           f"pas indexable — donc la composition terme à terme que la porte décrivait n'est pas "
           f"faisable sans deviner.", petit, GRIS)

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

    import copy  # noqa: PLC0415

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(36.0, 0), _fr(0.05, 2), _fr(18.3754, 4)) == ("36", "0,05", "18,3754"),
      f"{(_fr(36.0, 0), _fr(0.05, 2), _fr(18.3754, 4))}")
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
    bas_des_panneaux = max(b for _a, _b, _c, b in cadres if b < 730)
    haut_de_la_bande = min(b for _a, b, _c, _d in cadres if b > 700)
    dans_le_vide = [(t, y) for _x, y, t, _f in poses
                    if bas_des_panneaux < y < haut_de_la_bande]
    v("★★★★ aucun texte ne tombe entre le bas d'un panneau et la bande", not dans_le_vide,
      f"{bas_des_panneaux}..{haut_de_la_bande} : {dans_le_vide}"[:200])
    octets = chemin.read_bytes()
    dessiner(d, sortie)
    v("★ le re-rendu est bit-identique", chemin.read_bytes() == octets)

    # ★★★★ LA PHASE DESSINEE VIENT DE LA MESURE, POINT PAR POINT.
    for k in (0, 120, len(d["la_phase_en_voxels"]) - 1):
        faux = copy.deepcopy(d)
        faux["la_phase_en_voxels"][k] = 3.0
        dessiner(faux, sortie)
        v(f"★★★★ le point {k} de la phase vient de la mesure", chemin.read_bytes() != octets)
        dessiner(d, sortie)

    # ★★★★ LA PHASE EST TRACEE SUR L'ECHELLE DU PLI, PAS SUR CELLE DU CUBE : une phase de 71
    # voxels doit toucher le HAUT du graphe, ce qu'une echelle en 109 couches ne ferait pas.
    faux = copy.deepcopy(d)
    faux["la_phase_en_voxels"] = [float(d["le_pas_dun_pli_en_voxels"]) - 0.5] * len(
        d["la_phase_en_voxels"])
    _c, _p, cd2, pt2, _b, _t = dessiner(faux, sortie)
    haut_du_cadre = [c for c in cd2 if c[1] == 122][0][1]
    v("★★★★ une phase juste sous le pli se dessine tout en haut du graphe",
      min(y for _x, y in pt2) < haut_du_cadre + 24,
      f"{round(min(y for _x, y in pt2), 1)} contre {haut_du_cadre}")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("laccord", "le_pas_quadratique_observe_en_voxels"), 13.7575, 4, 3),
            (("laccord", "le_pas_quadratique_median_du_nul_en_voxels"), 41.4141, 4, 2),
            (("laccord", "la_valeur_p"), 0.03, 2, 2),
            (("le_verdict", "lexcursion_depliee_en_plis"), 7.474747, 6, 2),
            (("le_verdict", "lexcursion_absolue_en_plis"), 2.727272, 6, 2),
            (("le_verdict", "lexcursion_differentielle_en_plis"), 1.818181, 6, 2),
            (("le_verdict", "le_rapport_au_differentiel"), 9.6969, 4, 2),
            (("la_condition_ditoh", "le_pas_quadratique_de_199_en_voxels"), 31.3131, 4, 1),
            (("la_condition_ditoh", "le_pas_maximal_de_199_en_voxels"), 23.0, 0, 2),
            (("la_condition_ditoh", "la_demi_periode_en_voxels"), 47.0, 0, 3),
            (("la_condition_ditoh", "la_marge_du_pas_maximal_en_voxels"), 8.0, 0, 2),
            (("la_marginale", "lecart_type_en_voxels"), 55.5151, 4, 1),
            (("la_marginale", "lecart_type_du_nul_en_voxels"), 66.6161, 4, 1),
            (("la_marginale", "le_rapport_au_nul"), 0.4242, 4, 1),
            (("langle_mort", "la_marge_mediane_en_voxels"), 12.1212, 4, 1),
            (("laccord", "le_rapport_au_nul"), 0.7171, 4, 2),
            (("le_verdict", "le_rapport_a_ce_que_199_rendrait"), 8.1818, 4, 2),
            (("le_verdict", "le_pas_que_199_rendrait_en_voxels"), 27.2727, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p2 if _fr(val, dec) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n >= combien, f"{n} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★★ LES COMPTES DE L'ANGLE MORT ET DE L'ALIGNEMENT SONT DESSINES.
    for chemin_cles, val, combien in (
            (("langle_mort", "les_pas_hors_enveloppe"), 77, 1),
            (("langle_mort", "les_pas_au_bord_de_lalias"), 88, 1),
            (("la_condition_ditoh", "les_ecarts_certifies_au_pire"), 191, 1),
            (("ce_que_199_a_rendu", "les_pas_sans_colonne"), 73, 1),
            (("ce_que_199_a_rendu", "les_pas_qui_saturent"), 64, 1),
            (("laccord", "les_melanges_au_moins_aussi_serres"), 17, 2)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p3 if str(val) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est dessiné", n >= combien,
          f"{n} mentions pour {combien}")
    dessiner(d, sortie)

    # ★★★ CHAQUE BARREAU DE L'ETALON PORTE SA PART ET SON PAS POSE.
    for k in (0, 2, 4):
        faux = copy.deepcopy(d)
        faux["letalon"]["la_courbe"][k]["part_des_replicats"] = 0.6464 + k / 1e4
        faux["letalon"]["la_courbe"][k]["le_pas_pose_en_voxels"] = 13.1313 + k
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ le barreau {k} porte sa part et son pas posé",
          any(_fr(0.6464 + k / 1e4, 3) in t for _x, _y, t, _f in p4)
          and any(_fr(13.1313 + k, 4) in t for _x, _y, t, _f in p4))
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_depliage_rend_un_ordinal"] = True
    v("★★★★ un dépliage qui rend l'ordinal change le titre", "OUI, et le dépliage borne"
      in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["laccord"]["la_phase_se_suit"] = False
    v("★★★★ une phase qui ne se suit pas du tout le dit aussi",
      "NON, la phase ne se suit pas" in le_titre(faux), le_titre(faux))
    v("★★★ et l'observé dit « à peine »", "À PEINE" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["le_depliage"].__setitem__("decidable", False),
             "au dépliage indécidable"),
            (lambda x: x["laccord"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["les_colonnes"].pop(),
             "dont la phase et ses colonnes diffèrent"),
            (lambda x: x.__setitem__("la_condition_ditoh", None),
             "sans condition d'Itoh"),
            (lambda x: x["laccord"].__setitem__("le_rapport_au_nul", None),
             "sans rapport au nul"),
            (lambda x: x["le_verdict"].__setitem__(
                "le_rapport_a_ce_que_199_rendrait", None),
             "sans rapport à ce que `199` rendrait"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        faux = copy.deepcopy(d)
        casse(faux)
        tmp = sortie.with_name(sortie.stem + "_sonde.json")
        tmp.write_text(json.dumps(faux), encoding="utf-8")
        refuse = False
        try:
            lire(tmp)
        except ValueError:
            refuse = True
        v(f"une mesure {quoi} est refusée", refuse)
        tmp.unlink(missing_ok=True)
    dessiner(d, sortie)

    print(f"figure_peut_on_deplier_la_phase.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures" / "peut_on_deplier_la_phase.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "201_peut_on_deplier_la_phase.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
