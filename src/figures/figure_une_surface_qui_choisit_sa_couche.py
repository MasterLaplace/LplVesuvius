"""Une surface qui choisit sa couche reste-t-elle sur sa feuille ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut à gauche, l'étalon : sur une frontière POSÉE
le critère tient, sur une frontière FICTIVE il ne tient rien. En haut à droite, l'échelle des écarts
de direction — de celui de la fixture à celui du rouleau, puis zéro. En bas à gauche, le rouleau : le
compte de chunks où le choix retient, contre ce qu'un chunk sur vingt donnerait. En bas à droite, ce
que le choix ACHÈTE (de la longueur) et ce qu'il COÛTE (sa feuille).

  uv run python src/figures/figure_une_surface_qui_choisit_sa_couche.py \\
      --json docs/mesures/une_surface_qui_choisit_sa_couche.json \\
      --sortie docs/images/190_une_surface_qui_choisit_sa_couche.png
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
    """Le JSON de `une_surface_qui_choisit_sa_couche.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT L'ÉTALON NE SÉPARE PAS SES DEUX FACES, ET UNE ÉCHELLE QUI NE
    DISCRIMINE PAS. Un critère qui « retiendrait » aussi bien sur une frontière posée que sur une
    frontière fictive lirait sa propre marche ; une échelle dont tous les barreaux tiennent ne dit
    rien de l'écart de direction, et c'est très exactement ce qu'une échelle qui ne mesure rien
    donne.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ("letalon", "lechelle_des_directions", "les_segments", "le_verdict"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    v = d["le_verdict"]
    if not v.get("decidable"):
        raise ValueError(f"{chemin} : verdict indécidable")
    if not v.get("letalon_separe_les_deux"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    if not v.get("lechelle_discrimine"):
        raise ValueError(f"{chemin} : l'échelle des directions ne discrimine pas")
    return d


def le_titre(v: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas.

    ⚠⚠⚠ ET IL A TROIS BRANCHES PARCE QUE LA MESURE A DEUX LECTURES QUI PEUVENT DIVERGER. Le compte
    de chunks dit si une minorité retient au-delà du hasard ; la médiane dit ce que la marche fait
    en général. Les faire tenir dans un seul mot publierait un nombre juste sous un mauvais nom.
    """
    retient = v.get("le_choix_retient_la_marche")
    ensemble = v.get("la_mediane_va_dans_le_meme_sens")
    if retient and ensemble:
        queue = "OUI — elle quitte sa feuille moins souvent que le hasard"
    elif retient:
        queue = "DANS UNE MINORITÉ DE CHUNKS SEULEMENT, pas en général"
    else:
        queue = "NON — ce que le critère lit ne dit pas où est la feuille"
    return f"Une surface qui choisit sa couche reste-t-elle sur sa feuille ? — {queue}"


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

    v, e, ech = d["le_verdict"], d["letalon"], d["lechelle_des_directions"]
    # ⚠⚠ LE SIGNE SUIT LA CONJONCTION DES DEUX LECTURES, ET NON LE SEUL COMPTE. Une minorite qui
    # retient pendant que la mediane va dans l'autre sens n'est pas une reponse affirmative, et la
    # marquer d'une etoile la lirait comme telle.
    franc = bool(v.get("le_choix_retient_la_marche")
                 and v.get("la_mediane_va_dans_le_meme_sens"))
    coul_v = BON if franc else ALERTE
    signe = "★" if franc else "✗"
    ecrire(28, 20, le_titre(v), gros, ENCRE)
    ecrire(28, 46,
           f"{d['departs_par_couche']} départs par couche · {v['chunks_lus']} chunks · pas FORCÉ "
           f"d'une couche ({_fr(v['le_pas_de_la_marche_um'], 1)} µm), soit "
           f"{_fr(v.get('le_pas_est_sous_la_borne_fois'), 4)} fois sous la borne de `189` "
           f"({_fr(v.get('la_borne_du_pas_relue_de_189_um'), 1)} µm) · nul de "
           f"{v.get('les_tirages_du_nul')} tirages", petit, GRIS)

    # ---- panneau 1 : l'étalon
    x0, y0, pw, ph = 56, 122, 620, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — une frontière POSÉE, puis une frontière FICTIVE", moyen, ENCRE)
    haut = max([float(x.get("celle_qui_choisit", {}).get("part_qui_franchit") or 0.0)
                for x in e["lignes"]]
               + [float(x.get("le_hasard", {}).get("part_qui_franchit") or 0.0)
                  for x in e["lignes"]] + [0.01]) * 1.15
    for k, x in enumerate(e["lignes"]):
        yy = y0 + 14 + k * 74
        ecrire(x0 + 14, yy, x["matiere"], moyen, ENCRE)
        if not x.get("decidable"):
            ecrire(x0 + 14, yy + 22, str(x.get("raison")), 0, ALERTE)
            continue
        ok = (x["le_choix_retient_la_marche"] if x["attendu"] == "le choix retient"
              else not x["le_choix_retient_la_marche"])
        ecrire(x0 + 14, yy + 20, f"attendu « {x['attendu'] } »", 0, GRIS)
        ecrire(x0 + 270, yy + 20,
               f"{'★' if ok else '✗'} retient {x['le_choix_retient_la_marche']}", 0,
               BON if ok else ALERTE)
        ecrire(x0 + 14, yy + 38,
               f"en choisissant {_fr(x['celle_qui_choisit']['part_qui_franchit'], 4)}", 0, ENCRE)
        barre(x0 + 200, yy + 40, 170,
              float(x["celle_qui_choisit"]["part_qui_franchit"] or 0.0) / haut, 8, CONTRE)
        ecrire(x0 + 14, yy + 54,
               f"au hasard      {_fr(x['le_hasard']['part_qui_franchit'], 4)}", 0, GRIS)
        barre(x0 + 200, yy + 56, 170,
              float(x["le_hasard"]["part_qui_franchit"] or 0.0) / haut, 8, GRIS)
        ecrire(x0 + 400, yy + 46,
               f"règle brute {_fr(x['la_regle_brute']['part_qui_franchit'], 4)}", 0, ALERTE)
    ecrire(x0 + 14, y0 + 238,
           "⚠⚠ La troisième porte les MÊMES frontières déclarées, et aucun changement de direction.",
           petit, GRIS)

    # ---- panneau 2 : l'échelle des écarts de direction
    x0, y0, pw, ph = 712, 122, 592, 262
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "de quel changement de direction le critère a-t-il besoin ?", moyen, ENCRE)
    ecrire(x0 + 14, y0 + 8, "écart", petit, GRIS)
    ecrire(x0 + 106, y0 + 8, "franchit", petit, CONTRE)
    ecrire(x0 + 186, y0 + 8, "la plus basse des nuls", petit, GRIS)
    hautE = max([float(x.get("part_qui_franchit") or 0.0) for x in ech["lignes"]] + [0.01]) * 1.15
    rouleau = float(d["les_bascules_relues_de_176"]["du_rouleau_deg"])
    for k, x in enumerate(ech["lignes"]):
        yy = y0 + 28 + k * 25
        est_rouleau = abs(float(x["ecart_deg"]) - rouleau) < 1e-6
        est_zero = float(x["ecart_deg"]) == 0.0
        coul = ENCRE if est_rouleau else (ALERTE if est_zero else GRIS)
        ecrire(x0 + 14, yy, f"{_fr(x['ecart_deg'], 4):>8}°", 0, coul)
        if not x.get("plafond_du_ruban"):
            ecrire(x0 + 106, yy, str(x.get("raison")), 0, ALERTE)
            continue
        ecrire(x0 + 106, yy, _fr(x["part_qui_franchit"], 4), 0, CONTRE)
        ecrire(x0 + 186, yy, _fr(x["la_plus_basse_des_parts_du_hasard"], 4), 0, GRIS)
        barre(x0 + 290, yy + 2, 160, float(x["part_qui_franchit"] or 0.0) / hautE, 8,
              CONTRE if x["le_choix_retient_la_marche"] else ALERTE)
        ecrire(x0 + 462, yy, "★ retient" if x["le_choix_retient_la_marche"] else "✗ rien", 0,
               BON if x["le_choix_retient_la_marche"] else ALERTE)
    ecrire(x0 + 14, y0 + 234,
           f"★ Le critère tient jusqu'à {_fr(v.get('le_critere_tient_jusqua_deg'), 4)}° et ne lâche "
           f"qu'à {_fr(v.get('le_critere_lache_a_partir_de_deg'), 4)}°, où il n'y a RIEN à lire.",
           petit, ENCRE)
    ecrire(x0 + 14, y0 + 248,
           f"⚠ L'écart du rouleau vaut {_fr(v.get('la_bascule_du_rouleau_deg'), 3)}° (`176`), son "
           f"témoin {_fr(v.get('le_temoin_du_rouleau_deg'), 2)}°.", petit, GRIS)

    # ---- panneau 3 : le rouleau
    x0, y0, pw, ph = 56, 436, 620, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "le rouleau — segment par segment, puis le compte", moyen, ENCRE)
    hautS = max([float(s.get("part_qui_franchit_en_choisissant") or 0.0)
                 for s in d["les_segments"] if s.get("decidable")]
                + [float(s.get("part_qui_franchit_au_hasard") or 0.0)
                   for s in d["les_segments"] if s.get("decidable")] + [0.01]) * 1.15
    for k, s in enumerate(d["les_segments"]):
        yy = y0 + 12 + k * 44
        if not s.get("decidable"):
            ecrire(x0 + 14, yy, f"segment {s['segment']} — illisible", 0, ALERTE)
            continue
        ecrire(x0 + 14, yy, f"segment {s['segment']} · {s['chunks_lus']} chunks", 0, ENCRE)
        ecrire(x0 + 14, yy + 16,
               f"en choisissant {_fr(s['part_qui_franchit_en_choisissant'], 4)}", 0, CONTRE)
        barre(x0 + 200, yy + 18, 160,
              float(s["part_qui_franchit_en_choisissant"] or 0.0) / hautS, 7, CONTRE)
        ecrire(x0 + 14, yy + 30, f"au hasard      "
                                 f"{_fr(s['part_qui_franchit_au_hasard'], 4)}", 0, GRIS)
        barre(x0 + 200, yy + 32, 160, float(s["part_qui_franchit_au_hasard"] or 0.0) / hautS, 7,
              GRIS)
        ecrire(x0 + 390, yy + 24,
               f"retient dans {s['chunks_ou_le_choix_retient']}/{s['chunks_lus']}", 0, ENCRE)
    hautC = max(float(v["chunks_lus"]), 1.0)
    for k, (nom, val, coul) in enumerate(
            (("chunks où le choix retient", v.get("chunks_ou_le_choix_retient"), CONTRE),
             ("attendus par hasard (un sur vingt)", v.get("les_chunks_attendus_par_hasard"),
              GRIS))):
        yy = y0 + 156 + k * 30
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 262, yy, _fr(val, 4), 0, coul)
        barre(x0 + 330, yy + 2, 250, float(val or 0.0) / hautC, 12, coul)
    ecrire(x0 + 14, y0 + 224,
           f"{signe} {v['chunks_ou_le_choix_retient']} chunks sur {v['chunks_lus']} retiennent, "
           f"contre {_fr(v.get('les_chunks_attendus_par_hasard'), 4)} attendus (taux MESURÉ "
           f"{_fr(v.get('le_taux_de_faux_mesure'), 4)}),", moyen, coul_v)
    ecrire(x0 + 14, y0 + 246,
           f"     mais la médiane va dans l'autre sens : "
           f"{_fr(v.get('la_part_qui_franchit_en_choisissant'), 4)} contre "
           f"{_fr(v.get('la_part_qui_franchit_au_hasard'), 4)}."
           if not v.get("la_mediane_va_dans_le_meme_sens")
           else "     et la médiane va dans le même sens.", moyen, coul_v)

    # ---- panneau 4 : ce que le choix achète et ce qu'il coûte
    x0, y0, pw, ph = 712, 436, 592, 276
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "ce que le choix ACHÈTE, et ce qu'il COÛTE", moyen, ENCRE)
    hautL = max(float(v.get("la_longueur_en_choisissant") or 0.0),
                float(v.get("la_longueur_a_plat") or 0.0), 1.0) * 1.2
    for k, (nom, val, coul) in enumerate(
            (("la longueur en choisissant", v.get("la_longueur_en_choisissant"), CONTRE),
             ("la longueur à plat (`185`)", v.get("la_longueur_a_plat"), GRIS))):
        yy = y0 + 14 + k * 28
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 214, yy, f"{_fr(val, 2)} pas", 0, coul)
        barre(x0 + 300, yy + 2, 260, float(val or 0.0) / hautL, 11, coul)
    ecrire(x0 + 14, y0 + 76,
           f"★ le choix achète {_fr(v.get('ce_que_le_choix_coute_en_longueur'), 2)} pas de "
           f"longueur — et `186` a montré", petit, ENCRE)
    ecrire(x0 + 14, y0 + 90,
           "qu'optimiser en trouve sur n'importe quelle image. Ce gain ne prouve rien.", petit,
           ENCRE)
    for k, (nom, val, coul) in enumerate(
            (("l'excursion en choisissant",
              f"{_fr(v.get('lexcursion_en_couches'), 2)} couches, "
              f"{_fr(v.get('lexcursion_um'), 2)} µm", CONTRE),
             ("l'excursion au hasard",
              f"{_fr(v.get('lexcursion_au_hasard_en_couches'), 2)} couches", GRIS),
             ("les pas vivants, des deux côtés",
              f"{_fr(v.get('les_pas_vivants_en_choisissant'), 2)} contre "
              f"{_fr(v.get('les_pas_vivants_au_hasard'), 2)}", ENCRE),
             ("la règle BRUTE franchit",
              f"{_fr(v.get('la_part_qui_franchit_a_la_regle_brute'), 4)}", ALERTE))):
        yy = y0 + 112 + k * 20
        ecrire(x0 + 14, yy, nom, 0, coul)
        ecrire(x0 + 262, yy, val, 0, coul)
    for k, (nom, ok) in enumerate(
            (("l'étalon sépare ses deux faces", v.get("letalon_separe_les_deux")),
             ("l'échelle discrimine, et zéro lâche",
              v.get("lechelle_discrimine") and v.get("le_barreau_zero_lache")),
             ("le critère tient à l'écart du rouleau",
              v.get("le_critere_tient_a_lecart_du_rouleau")),
             ("les deux marches vivent autant", v.get("les_deux_marches_vivent_autant")),
             ("le choix retient au-delà du hasard", v.get("le_choix_retient_la_marche")),
             ("et la médiane va dans le même sens",
              v.get("la_mediane_va_dans_le_meme_sens")))):
        yy = y0 + 196 + k * 13
        ecrire(x0 + 14, yy, f"{'★' if ok else '✗'} {nom}", 0, BON if ok else ALERTE)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"★  L'INSTRUMENT MARCHE, ET L'ÉTALON LE PROUVE DES DEUX CÔTÉS : sur une frontière posée "
           f"à 90° il retient, sur des frontières FICTIVES il ne retient rien, et l'échelle",
           moyen, ENCRE)
    ecrire(78, y + 46,
           f"     des directions le montre tenir jusqu'à "
           f"{_fr(v.get('le_critere_tient_jusqua_deg'), 4)}° — donc bien en-deçà de l'écart du "
           f"rouleau, {_fr(v.get('la_bascule_du_rouleau_deg'), 3)}°, qui est lui-même un barreau. "
           f"Il ne lâche qu'à {_fr(v.get('le_critere_lache_a_partir_de_deg'), 4)}°, où il n'y a "
           f"rien à lire.", moyen, ENCRE)
    ecrire(78, y + 78,
           f"{signe}  SUR LE ROULEAU IL NE TIENT QUE DANS UNE MINORITÉ : "
           f"{v['chunks_ou_le_choix_retient']} chunks sur {v['chunks_lus']} retiennent contre "
           f"{_fr(v.get('les_chunks_attendus_par_hasard'), 4)} attendus — un taux de faux MESURÉ "
           f"({_fr(v.get('le_taux_de_faux_mesure'), 4)}) et non supposé.", moyen, coul_v)
    ecrire(78, y + 106,
           f"     Mais EN GÉNÉRAL la marche quitte sa feuille "
           f"{_fr(v.get('la_part_qui_franchit_en_choisissant'), 4)} du temps contre "
           f"{_fr(v.get('la_part_qui_franchit_au_hasard'), 4)} en choisissant AU HASARD parmi les "
           f"mêmes voisines. Les deux vivent autant de pas.", moyen, coul_v)
    ecrire(78, y + 138,
           f"★  ET CE N'EST PAS FAUTE DE SIGNAL : le critère achète "
           f"{_fr(v.get('ce_que_le_choix_coute_en_longueur'), 2)} pas de longueur suivable "
           f"({_fr(v.get('la_longueur_en_choisissant'), 2)} contre "
           f"{_fr(v.get('la_longueur_a_plat'), 2)} à plat). Il lit donc quelque chose, mais ce "
           f"qu'il lit", moyen, ENCRE)
    ecrire(78, y + 166,
           "     ne dit pas où est la feuille — et `186` avait déjà mesuré qu'optimiser trouve de "
           "la longueur jusque dans du bruit pur.", moyen, ENCRE)
    ecrire(78, y + 198,
           "⚠ Ce que la tranche ne dit pas : ce qui distingue les chunks où le critère tient de "
           "ceux où il ne tient pas. Rien ici ne le mesure.", petit, GRIS)

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
      (_fr(90.0, 0), _fr(2.4, 1), _fr(0.0359, 4)) == ("90", "2,4", "0,0359"),
      f"{(_fr(90.0, 0), _fr(2.4, 1), _fr(0.0359, 4))}")
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
    # ⚠⚠⚠ UNE GARDE QUE `textes_hors_cadre` NE DONNE PAS, ET C'EST EN REGARDANT L'IMAGE QUE LE
    # DEFAUT EST APPARU : elle ne signale pas un texte qui COMMENCE sous un cadre. Une ligne posee
    # six pixels sous le bas d'un panneau tombe alors dans la bande et s'y fait manger, sans qu'une
    # seule verification ne rougisse.
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

    # ★★★ CHAQUE MATIERE DE L'ETALON EST DESSINEE AVEC SES DEUX LECTURES.
    for k in range(len(d["letalon"]["lignes"])):
        faux = copy.deepcopy(d)
        faux["letalon"]["lignes"][k]["celle_qui_choisit"]["part_qui_franchit"] = 0.7101 + k / 1e4
        faux["letalon"]["lignes"][k]["le_hasard"]["part_qui_franchit"] = 0.8201 + k / 1e4
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (0.7101 + k / 1e4, 0.8201 + k / 1e4)
                if any(_fr(m, 4) in t for _x, _y, t, _f in p2))
        v(f"★★★ la matière {k} de l'étalon est dessinée avec ses deux lectures", n == 2,
          f"{n} sur 2")

    # ★★★★ CHAQUE BARREAU DE L'ECHELLE EST DESSINE AVEC SES DEUX LECTURES.
    for k in range(len(d["lechelle_des_directions"]["lignes"])):
        faux = copy.deepcopy(d)
        faux["lechelle_des_directions"]["lignes"][k]["part_qui_franchit"] = 0.6101 + k / 1e4
        faux["lechelle_des_directions"]["lignes"][k]["la_plus_basse_des_parts_du_hasard"] = (
            0.9101 + k / 1e4)
        _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for m in (0.6101 + k / 1e4, 0.9101 + k / 1e4)
                if any(_fr(m, 4) in t for _x, _y, t, _f in p3))
        v(f"★★★ le barreau {k} de l'échelle est dessiné avec ses deux lectures", n == 2,
          f"{n} sur 2")

    # ★★★★ LE COMPTE OBSERVE ET L'ATTENDU PAR HASARD SONT LUS DES DEUX COTES : c'est la statistique
    # de la tranche, et un seul des deux ne dit rien.
    # ⚠⚠ LES VALEURS DE SONDE SURVIVENT A L'ARRONDI DU RENDU : le compte s'ecrit entier et l'attendu
    # a quatre decimales, donc une sonde mal arrondie serait rouge pour une raison de mise en forme.
    for cle, val, dec in (("chunks_ou_le_choix_retient", 17, 0),
                          ("les_chunks_attendus_par_hasard", 3.1416, 4),
                          ("la_part_qui_franchit_en_choisissant", 0.5151, 4),
                          ("la_part_qui_franchit_au_hasard", 0.6161, 4)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p4 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ LE TAUX DE FAUX MESURE EST LU DES DEUX COTES : c'est lui qui fait l'attendu, et publier
    # l'attendu sans lui laisserait croire a la garantie theorique.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["le_taux_de_faux_mesure"] = 0.1234
    _c, p8, _cd, _pt, _b, _t = dessiner(faux, sortie)
    n = sum(1 for _x, _y, t, _f in p8 if _fr(0.1234, 4) in t)
    v("★★★★ le taux de faux MESURÉ est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ ET LES DEUX LONGUEURS AUSSI : ce que le choix ACHETE est la moitie du resultat.
    for cle, val in (("la_longueur_en_choisissant", 51.25), ("la_longueur_a_plat", 41.75)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p5, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n = sum(1 for _x, _y, t, _f in p5 if _fr(val, 2) in t)
        v(f"★★★★ {cle} est lue des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ L'ECART OU LE CRITERE TIENT ENCORE EST LU DES DEUX COTES : c'est ce qui REFUTE
    # l'explication par la petitesse de la bascule du rouleau.
    for cle, val in (("le_critere_tient_jusqua_deg", 3.1416),
                     ("le_critere_lache_a_partir_de_deg", 1.2345),
                     ("la_bascule_du_rouleau_deg", 7.531)):
        faux = copy.deepcopy(d)
        faux["le_verdict"][cle] = val
        _c, p6, _cd, _pt, _b, _t = dessiner(faux, sortie)
        dec = 3 if cle == "la_bascule_du_rouleau_deg" else 4
        n = sum(1 for _x, _y, t, _f in p6 if _fr(val, dec) in t)
        v(f"★★★★ {cle} est lu des DEUX côtés", n >= 2, f"{n} mentions")

    # ★★★★ UN ETALON QUI NE SEPARE PAS, OU UNE ECHELLE QUI NE DISCRIMINE PAS, FONT REFUSER.
    import tempfile  # noqa: PLC0415

    for cle in ("letalon_separe_les_deux", "lechelle_discrimine"):
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

    # ★★★★ LES TROIS BRANCHES DU TITRE SONT EXERCEES.
    branches = []
    for ret, ens, attendu in ((True, True, "OUI"), (True, False, "MINORITÉ"), (False, True, "NON")):
        faux = copy.deepcopy(d)
        faux["le_verdict"]["le_choix_retient_la_marche"] = ret
        faux["le_verdict"]["la_mediane_va_dans_le_meme_sens"] = ens
        branches.append(le_titre(faux["le_verdict"]))
        v(f"★★★ le titre dit « {attendu} » quand la mesure le dit", attendu in branches[-1],
          branches[-1])
        _c, p7, _cd, _pt, _b, _t = dessiner(faux, sortie)
        v(f"★★★ la figure se dessine entièrement dans la branche « {attendu} »",
          not textes_debordants(p7, 1360) and not textes_hors_cadre(p7, cadres)
          and not textes_qui_se_recouvrent(p7))
    v("★★★★ les trois branches sont distinctes", len(set(branches)) == 3, str(branches))

    dessiner(d, sortie)
    # ⚠⚠ LA SORTIE REND LE COMPTE D'ECHECS, PAS UN LITTERAL.
    nom = "figure_une_surface_qui_choisit_sa_couche.py"
    if echecs:
        print(f"{nom}   {echecs} ÉCHECS sur {faits}")
    else:
        print(f"{nom:<46} ALL PASS (0 failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "une_surface_qui_choisit_sa_couche.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "190_une_surface_qui_choisit_sa_couche.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
