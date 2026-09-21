"""La transition fixe-t-elle l'erreur de chunk ?

⚠⚠ **Ce que cette figure doit rendre évident.** En haut, l'erreur de localisation en fonction de la
transition, avec la transition du rouleau marquée : la courbe est PLATE et minuscule, et c'est toute
la réponse. En bas à gauche, l'échelle et ses deux bouts dérivés. Au centre, l'épreuve. À droite,
l'étalon — qui montre que l'épreuve SAURAIT voir une erreur qui suit la transition.

  uv run python src/figures/figure_la_transition_fixe_t_elle_lerreur_de_chunk.py \\
      --json docs/mesures/la_transition_fixe_t_elle_lerreur_de_chunk.json \\
      --sortie docs/images/209_la_transition_fixe_t_elle_lerreur_de_chunk.png
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
    """Le JSON de `la_transition_fixe_t_elle_lerreur_de_chunk.py`.

    ⚠⚠⚠ REFUSE UNE MESURE DONT UN BARREAU N'A PAS SON COMPTE DE DÉCALAGES MUETS : une erreur
    calculée sur ce qui reste quand le lecteur se tait est une erreur mesurée sur les cas faciles.
    """
    d = json.loads(chemin.read_text(encoding="utf-8"))
    if not d.get("decidable", True):
        raise ValueError(f"{chemin} : mesure indécidable — {d.get('raison')}")
    for cle in ("la_courbe", "lepreuve", "le_verdict", "letalon",
                "lechelle_des_transitions", "les_bornes_de_179"):
        if not d.get(cle):
            raise ValueError(f"{chemin} : {cle} est absent")
    for cle in ("la_courbe", "lepreuve", "le_verdict", "letalon",
                "lechelle_des_transitions", "les_bornes_de_179"):
        if not d[cle].get("decidable"):
            raise ValueError(f"{chemin} : {cle} est indécidable")
    if not d["letalon"].get("letalon_separe"):
        raise ValueError(f"{chemin} : l'étalon ne sépare pas ses deux faces")
    n = len(d.get("les_epreuves_declarees") or [])
    if abs(float(d["la_garantie_par_epreuve"]) * n - 1.0 / (int(d["tirages"]) + 1)) > 1e-9:
        raise ValueError(f"{chemin} : la garantie n'est pas divisée par les {n} épreuves")
    for b in d["la_courbe"]["les_barreaux"]:
        if b.get("les_decalages_muets") is None:
            raise ValueError(f"{chemin} : le barreau {b.get('la_transition_en_voxels')} n'a pas "
                             f"son compte de décalages muets")
    if d["le_verdict"].get("lerreur_de_chunk_de_205_en_voxels") is None:
        raise ValueError(f"{chemin} : l'erreur de chunk de `205` est absente")
    return d


def le_titre(d: dict) -> str:
    """Le titre suit la mesure, il ne la précède pas."""
    ve = d["le_verdict"]
    if ve.get("lerreur_suit_la_transition"):
        return "La transition fixe-t-elle l'erreur de chunk ? — oui, l'erreur suit la transition"
    r = ve.get("le_rapport_a_lerreur_de_chunk")
    if r is not None and float(r) < 0.5:
        return ("La transition fixe-t-elle l'erreur de chunk ? — non, et de très loin : le creux "
                "situe au dixième de voxel")
    return "La transition fixe-t-elle l'erreur de chunk ? — non, l'erreur ne la suit pas"


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

    cb, ep, ve = d["la_courbe"], d["lepreuve"], d["le_verdict"]
    e, ec, bo = d["letalon"], d["lechelle_des_transitions"], d["les_bornes_de_179"]
    bar = [x for x in cb["les_barreaux"] if x.get("decidable")]
    t_rouleau = float(ec["la_transition_du_rouleau_en_voxels"])

    ecrire(28, 20, le_titre(d), gros, ENCRE)
    ecrire(28, 46,
           f"fixture de `179` · transitions {_fr(ec['le_plancher_en_voxels'], 4)} à "
           f"{_fr(ec['le_plafond_en_voxels'], 4)} voxels · celle du rouleau "
           f"{_fr(t_rouleau, 4)} · bruit {_fr(d['le_bruit_porte'], 4)} · "
           f"{d['les_decalages']} décalages · une seule épreuve, garantie "
           f"{_fr(d['la_garantie_par_epreuve'], 2)}", petit, GRIS)

    # ---- panneau 1 : l'erreur en fonction de la transition
    x0, y0, pw, ph = 56, 122, 1248, 286
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24,
           "avec quelle erreur le creux situe une frontière POSÉE, transition par transition",
           moyen, ENCRE)
    gx0, gy0, gw, gh = x0 + 56, y0 + 16, pw - 400, 214
    haut = max(float(x["lerreur_quadratique_en_voxels"]) for x in bar) * 1.25
    for k in range(5):
        yy = gy0 + gh * k / 4.0
        art.line([gx0, yy, gx0 + gw, yy], fill=TRAIT, width=1)
        traits.append((gx0, yy, gx0 + gw))
        ecrire(gx0 - 42, yy - 6, _fr(haut * (1.0 - k / 4.0), 2), 0, GRIS)
    tmin = min(float(x["la_transition_en_voxels"]) for x in bar)
    tmax = max(float(x["la_transition_en_voxels"]) for x in bar)
    etendue = max(1e-9, tmax - tmin)
    xr = gx0 + gw * (t_rouleau - tmin) / etendue
    art.line([xr, gy0, xr, gy0 + gh], fill=ALERTE, width=2)
    traits.append((xr, gy0, gy0 + gh))
    ecrire(xr + 6, gy0 + 2, f"la transition du rouleau : {_fr(t_rouleau, 4)} vx", 0, ALERTE)
    prec = None
    for b in bar:
        px = gx0 + gw * (float(b["la_transition_en_voxels"]) - tmin) / etendue
        py = gy0 + gh * (1.0 - float(b["lerreur_quadratique_en_voxels"]) / haut)
        if prec is not None:
            art.line([prec[0], prec[1], px, py], fill=CONTRE, width=2)
        art.ellipse([px - 3, py - 3, px + 3, py + 3], fill=CONTRE)
        points.append((px, py))
        prec = (px, py)
    for b in (bar[0], bar[len(bar) // 2], bar[-1]):
        px = gx0 + gw * (float(b["la_transition_en_voxels"]) - tmin) / etendue
        ecrire(px - 10, gy0 + gh + 8, _fr(b["la_transition_en_voxels"], 0), 0, GRIS)
    ecrire(gx0 + gw / 2 - 58, gy0 + gh + 26, "la transition, en voxels", 0, GRIS)
    lx = x0 + pw - 326
    ecrire(lx, y0 + 16,
           f"à la transition du rouleau, l'erreur vaut", petit, ENCRE)
    ecrire(lx, y0 + 30,
           f"{_fr(ve['lerreur_a_la_transition_du_rouleau_en_voxels'], 4)} voxel.", moyen, CONTRE)
    ecrire(lx, y0 + 54,
           f"`205` isolait {_fr(ve['lerreur_de_chunk_de_205_en_voxels'], 4)} voxels d'erreur",
           petit, ENCRE)
    ecrire(lx, y0 + 68,
           f"commune à un chunk — un rapport de", petit, ENCRE)
    ecrire(lx, y0 + 82, f"{_fr(ve['le_rapport_a_lerreur_de_chunk'], 4)}.", moyen, ALERTE)
    for k, (nom, val) in enumerate((
            ("les transitions varient de", _fr(ve["le_rapport_des_transitions"], 4)),
            ("les erreurs varient de", _fr(ve["le_rapport_des_erreurs"], 4)),
            ("aussi vite ?", _fr(ve["lerreur_croit_elle_aussi_vite"], 4)))):
        yy = y0 + 112 + k * 20
        ecrire(lx, yy, nom, 0, GRIS)
        ecrire(lx + 222, yy, val, 0, ENCRE)
    ecrire(lx, y0 + 184, "⚠⚠ LE BRUIT PORTÉ EST LE PLUS GRAND QUE `179`", petit, GRIS)
    ecrire(lx, y0 + 198, "ait tenu, pas zéro : son échelle avait été", petit, GRIS)
    ecrire(lx, y0 + 212, "balayée SANS bruit, et le rouleau en porte.", petit, GRIS)
    ecrire(lx, y0 + 230, "⚠⚠⚠ La fixture espace ses frontières de", petit, GRIS)
    ecrire(lx, y0 + 244,
           f"{bo['lespacement_des_frontieres_en_couches']} couches : ce qui se teste est la",
           petit, GRIS)
    ecrire(lx, y0 + 258, "PROPORTIONNALITÉ, pas l'égalité de deux", petit, GRIS)
    ecrire(lx, y0 + 272, "nombres pris sur deux matières.", petit, GRIS)

    # ---- panneau 2 : l'échelle
    x0, y0, pw, ph = 56, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'échelle, ses deux bouts dérivés de `179`", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("transition du rouleau", f"{_fr(t_rouleau, 4)} vx"),
            ("plancher, sa moitié", f"{_fr(ec['le_plancher_en_voxels'], 4)} vx"),
            ("plafond, l'espacement",
             f"{_fr(ec['le_plafond_en_voxels'], 4)} vx"),
            ("le voxel de `179`", f"{_fr(bo['le_voxel_en_um'], 4)} µm"),
            ("bruit porté", _fr(bo["le_plus_grand_bruit_tenu"], 4)),
            ("barreaux", f"{len(bar)} lisibles sur "
                         f"{len(cb['les_barreaux'])}"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 248, yy, val, 0, ENCRE)
    muets = sum(int(x.get("les_decalages_muets") or 0) for x in cb["les_barreaux"])
    tous = sum(int(x.get("les_decalages") or d["les_decalages"])
               for x in cb["les_barreaux"])
    ecrire(x0 + 12, y0 + 140, f"décalages muets : {muets} sur {tous}", 0, ENCRE)
    barre(x0 + 12, y0 + 158, 372, float(muets) / max(1.0, float(tous)), 10, ALERTE)
    ecrire(x0 + 12, y0 + 184,
           "⚠⚠⚠ Le compte de décalages MUETS voyage avec", petit, GRIS)
    ecrire(x0 + 12, y0 + 198,
           "chaque barreau : une transition où le lecteur", petit, GRIS)
    ecrire(x0 + 12, y0 + 212,
           "se tait presque partout rend une erreur mesurée", petit, GRIS)
    ecrire(x0 + 12, y0 + 226, "sur les cas FACILES.", petit, GRIS)

    # ---- panneau 3 : l'épreuve
    x0, y0, pw, ph = 480, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'épreuve de `202`, reprise", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("|r| observé", _fr(ep["la_correlation_absolue"], 4)),
            ("|r| médian du nul", _fr(ep["la_correlation_absolue_mediane_du_nul"], 4)),
            ("|r| maximal du nul", _fr(ep["la_correlation_absolue_maximale_du_nul"], 4)),
            ("mélanges aussi forts",
             f"{ep['les_melanges_au_moins_aussi_forts']} sur {ep['tirages']}"),
            ("valeur P", _fr(ep["la_valeur_p"], 4)))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 268, yy, val, 0, ENCRE)
    hautR = max(float(ep["la_correlation_absolue"]),
                float(ep["la_correlation_absolue_maximale_du_nul"]), 0.1) * 1.2
    barre(x0 + 12, y0 + 120, 372, float(ep["la_correlation_absolue"]) / hautR, 10, CONTRE)
    barre(x0 + 12, y0 + 136, 372,
          float(ep["la_correlation_absolue_maximale_du_nul"]) / hautR, 10, GRIS)
    suit = bool(ve["lerreur_suit_la_transition"])
    ecrire(x0 + 12, y0 + 158,
           f"{'★' if suit else '✗'} L'ERREUR SUIT LA TRANSITION : {suit}", moyen,
           BON if suit else ALERTE)
    ecrire(x0 + 12, y0 + 186,
           "★ Le mélange garde les deux lois marginales et ne", petit, GRIS)
    ecrire(x0 + 12, y0 + 200,
           "détruit que l'APPARIEMENT, qui est précisément ce", petit, GRIS)
    ecrire(x0 + 12, y0 + 214,
           "que la tranche mesure. La statistique est la valeur", petit, GRIS)
    ecrire(x0 + 12, y0 + 228,
           "ABSOLUE, parce que le sens n'est pas posé.", petit, GRIS)

    # ---- panneau 4 : l'étalon
    x0, y0, pw, ph = 904, 460, 400, 252
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=TRAIT, width=1)
    cadres.append((x0, y0, x0 + pw, y0 + ph))
    ecrire(x0, y0 - 24, "l'étalon — l'épreuve SAURAIT voir une pente", moyen, ENCRE)
    for k, (nom, val) in enumerate((
            ("pente posée", _fr(e["la_pente_posee"], 4)),
            ("bruit posé", _fr(e["le_bruit_pose"], 4)),
            ("trouvée dans", f"{e['les_vus']} des {e['replicats']} réplicats"),
            ("rapport, face positive", _fr(e["le_rapport_median_sur_la_face_positive"], 4)),
            ("rapport, face négative", _fr(e["le_rapport_median_sur_la_face_negative"], 4)),
            ("faux", f"{e['les_faux']} sur {e['les_replicats_du_refus']} réplicats"))):
        yy = y0 + 12 + k * 20
        ecrire(x0 + 12, yy, nom, 0, GRIS)
        ecrire(x0 + 248, yy, val, 0, ENCRE)
    barre(x0 + 12, y0 + 140, 372, float(e["la_part_trouvee"]), 10, BON)
    ecrire(x0 + 12, y0 + 158,
           f"★ sépare : {e['letalon_separe']} · taux de faux "
           f"{_fr(e['le_taux_de_faux'], 3)} pour {_fr(e['la_garantie'], 2)} garantis", 0, BON)
    ecrire(x0 + 12, y0 + 184,
           "⚠⚠⚠ C'est ce qui rend le refus LISIBLE : une épreuve", petit, GRIS)
    ecrire(x0 + 12, y0 + 198,
           "qui ne verrait rien nulle part refuserait aussi, et", petit, GRIS)
    ecrire(x0 + 12, y0 + 212,
           "ne dirait rien. Celle-ci voit une pente posée dans", petit, GRIS)
    ecrire(x0 + 12, y0 + 226, "tous ses réplicats.", petit, GRIS)

    # ---- la bande
    y = 738
    art.rectangle([56, y, L - 56, y + 226], fill=BANDE)
    cadres.append((56, y, L - 56, y + 226))
    ecrire(78, y + 18,
           f"✗  L'ERREUR DE CHUNK N'EST PAS CELLE DE LA TRANSITION : à la transition du rouleau "
           f"({_fr(t_rouleau, 4)} voxels), le creux situe une frontière posée à "
           f"{_fr(ve['lerreur_a_la_transition_du_rouleau_en_voxels'], 4)} voxel près,", moyen,
           ALERTE)
    ecrire(78, y + 46,
           f"     contre {_fr(ve['lerreur_de_chunk_de_205_en_voxels'], 4)} voxels d'erreur commune "
           f"mesurés sur le rouleau par `205` — un rapport de "
           f"{_fr(ve['le_rapport_a_lerreur_de_chunk'], 4)}.", moyen, ALERTE)
    ecrire(78, y + 78,
           f"✗  ET ELLE NE LA SUIT MÊME PAS : |r| = {_fr(ep['la_correlation_absolue'], 4)} contre "
           f"{_fr(ep['la_correlation_absolue_mediane_du_nul'], 4)} au mélange, "
           f"{ep['les_melanges_au_moins_aussi_forts']} sur {ep['tirages']} aussi forts, "
           f"P = {_fr(ep['la_valeur_p'], 4)}. Les transitions varient de", moyen, ENCRE)
    ecrire(78, y + 106,
           f"     {_fr(ve['le_rapport_des_transitions'], 4)} et les erreurs de "
           f"{_fr(ve['le_rapport_des_erreurs'], 4)} — soit "
           f"{_fr(ve['lerreur_croit_elle_aussi_vite'], 4)} fois aussi vite, donc pas du tout.",
           moyen, ENCRE)
    ecrire(78, y + 138,
           f"★  ET L'ÉPREUVE SAURAIT VOIR UNE PENTE : l'étalon la trouve dans "
           f"{e['les_vus']} de ses {e['replicats']} réplicats, avec "
           f"{e['les_faux']} faux sur {e['les_replicats_du_refus']}. Le refus est donc un "
           f"résultat, pas un silence.", moyen, BON)
    ecrire(78, y + 170,
           f"★ CE QUI RESTE : le creux situe au dixième de voxel sur une matière propre, au bruit "
           f"{_fr(d['le_bruit_porte'], 4)} que `179` avait tenu. L'erreur de chunk du rouleau ne "
           f"vient donc ni de la transition,", moyen, ENCRE)
    ecrire(78, y + 198,
           f"     ni du lecteur — elle vient de la MATIÈRE, et la fixture de `179` ne la porte "
           f"pas. C'est une exclusion, et elle ferme une voie plutôt que d'en ouvrir une.",
           moyen, ENCRE)

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

    def _refuse(base, out, casse):
        faux_ = copy.deepcopy(base)
        casse(faux_)
        tmp_ = out.with_name(out.stem + "_sonde.json")
        tmp_.write_text(json.dumps(faux_), encoding="utf-8")
        try:
            lire(tmp_)
            return False
        except ValueError:
            return True
        finally:
            tmp_.unlink(missing_ok=True)

    d = lire(json_path)
    chemin, poses, cadres, points, barres, traits = dessiner(d, sortie)
    img = Image.open(chemin)
    v("l'image est écrite et a la taille attendue", img.size == (1360, 980), f"{img.size}")
    v("★ un nombre rond n'est pas rogné par la mise en forme",
      (_fr(19.0, 0), _fr(0.05, 2), _fr(14.9372, 4)) == ("19", "0,05", "14,9372"),
      f"{(_fr(19.0, 0), _fr(0.05, 2), _fr(14.9372, 4))}")
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

    # ★★★★ LA COURBE VIENT DE LA MESURE, BARREAU PAR BARREAU.
    lisibles = [i for i, x in enumerate(d["la_courbe"]["les_barreaux"]) if x.get("decidable")]
    for k in (lisibles[0], lisibles[len(lisibles) // 2], lisibles[-1]):
        faux = copy.deepcopy(d)
        faux["la_courbe"]["les_barreaux"][k]["lerreur_quadratique_en_voxels"] = 3.3131
        _c, _p, _cd, ptk, _b, _t = dessiner(faux, sortie)
        v(f"★★★★ le barreau {k} de la courbe vient de la mesure",
          [(round(x, 2), round(y, 2)) for x, y in ptk]
          != [(round(x, 2), round(y, 2)) for x, y in points])
        dessiner(d, sortie)

    # ★★★★ LE TRAIT DE LA TRANSITION DU ROULEAU SUIT LA MESURE.
    faux = copy.deepcopy(d)
    faux["lechelle_des_transitions"]["la_transition_du_rouleau_en_voxels"] = 30.0
    _c, _p, _cd, _pt, _b, tr_c = dessiner(faux, sortie)
    v("★★★★ le trait de la transition du rouleau suit ce que `179` publie",
      [tuple(round(z, 2) for z in x) for x in tr_c]
      != [tuple(round(z, 2) for z in x) for x in traits],
      f"{len(tr_c)} traits")
    dessiner(d, sortie)

    # ★★★★ CHAQUE NOMBRE QUI PORTE LE VERDICT EST LU DES DEUX COTES.
    for chemin_cles, val, dec, combien in (
            (("le_verdict", "lerreur_a_la_transition_du_rouleau_en_voxels"), 7.4747, 4, 2),
            (("le_verdict", "lerreur_de_chunk_de_205_en_voxels"), 21.2121, 4, 2),
            (("le_verdict", "le_rapport_a_lerreur_de_chunk"), 0.8181, 4, 2),
            (("le_verdict", "le_rapport_des_transitions"), 9.6969, 4, 2),
            (("le_verdict", "le_rapport_des_erreurs"), 5.5151, 4, 2),
            (("le_verdict", "lerreur_croit_elle_aussi_vite"), 0.3131, 4, 2),
            (("lepreuve", "la_correlation_absolue"), 0.7171, 4, 2),
            (("lepreuve", "la_correlation_absolue_mediane_du_nul"), 0.1313, 4, 2),
            (("lepreuve", "la_correlation_absolue_maximale_du_nul"), 0.6161, 4, 1),
            (("lepreuve", "la_valeur_p"), 0.4141, 4, 2),
            (("letalon", "la_pente_posee"), 3.1313, 4, 1),
            (("letalon", "le_bruit_pose"), 4.1414, 4, 1),
            (("letalon", "le_rapport_median_sur_la_face_positive"), 6.1616, 4, 1),
            (("letalon", "le_rapport_median_sur_la_face_negative"), 2.4242, 4, 1),
            (("letalon", "le_taux_de_faux"), 0.111, 3, 1),
            (("lechelle_des_transitions", "le_plancher_en_voxels"), 5.1515, 4, 2),
            (("lechelle_des_transitions", "le_plafond_en_voxels"), 51.5151, 4, 2),
            (("les_bornes_de_179", "le_voxel_en_um"), 7.7171, 4, 1),
            (("les_bornes_de_179", "le_plus_grand_bruit_tenu"), 41.4141, 4, 1)):
        faux = copy.deepcopy(d)
        faux[chemin_cles[0]][chemin_cles[1]] = val
        _c, p2, _cd, _pt, _b, _t = dessiner(faux, sortie)
        n2 = sum(1 for _x, _y, t, _f in p2
                 if (str(val) if dec == 0 else _fr(val, dec)) in t)
        v(f"★★★★ {chemin_cles[0]}.{chemin_cles[1]} est lu autant de fois qu'il le faut",
          n2 >= combien, f"{n2} mentions pour {combien}")
    faux = copy.deepcopy(d)
    faux["les_bornes_de_179"]["lespacement_des_frontieres_en_couches"] = 414
    _c, p3, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ l'espacement des frontières de `179` est écrit",
      sum(1 for _x, _y, t, _f in p3 if "414" in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LES DECALAGES MUETS SONT DESSINES, PAS SEULEMENT STOCKES.
    # ⚠⚠ LA FIGURE ECRIT LA SOMME DES DECALAGES MUETS, PAS CELUI DE CHAQUE BARREAU : la sonde
    # casse donc UN barreau et verifie que la SOMME bouge, ce qui est ce que la figure montre.
    muets_avant = sum(int(x.get("les_decalages_muets") or 0)
                      for x in d["la_courbe"]["les_barreaux"])
    faux = copy.deepcopy(d)
    faux["la_courbe"]["les_barreaux"][0]["les_decalages_muets"] = 313
    _c, p4, _cd, _pt, _b, _t = dessiner(faux, sortie)
    v("★★★★ le compte de décalages muets est écrit, et il vient de la mesure",
      sum(1 for _x, _y, t, _f in p4
          if str(muets_avant + 313
                 - int(d["la_courbe"]["les_barreaux"][0].get("les_decalages_muets") or 0))
          in t) >= 1)
    dessiner(d, sortie)

    # ★★★★ LE TITRE SUIT LA MESURE, DANS SES TROIS ETATS.
    faux = copy.deepcopy(d)
    faux["le_verdict"]["lerreur_suit_la_transition"] = True
    v("★★★★ une erreur qui suit la transition change le titre",
      "oui, l'erreur suit la transition" in le_titre(faux), le_titre(faux))
    faux = copy.deepcopy(d)
    faux["le_verdict"]["lerreur_suit_la_transition"] = False
    faux["le_verdict"]["le_rapport_a_lerreur_de_chunk"] = 0.9
    v("★★★★ une erreur du même ordre le dit autrement",
      "non, l'erreur ne la suit pas" in le_titre(faux), le_titre(faux))
    v("★★★ et l'observé dit que le creux situe au dixième de voxel",
      "au dixième de voxel" in le_titre(d), le_titre(d))

    # ⚠⚠ UNE MESURE INCOMPLETE OU INCOHERENTE EST REFUSEE.
    for casse, quoi in (
            (lambda x: x["letalon"].__setitem__("letalon_separe", False),
             "dont l'étalon ne sépare pas"),
            (lambda x: x["la_courbe"].__setitem__("decidable", False),
             "à la courbe indécidable"),
            (lambda x: x["lepreuve"].__setitem__("decidable", False),
             "à l'épreuve indécidable"),
            (lambda x: x["lechelle_des_transitions"].__setitem__("decidable", False),
             "à l'échelle indécidable"),
            (lambda x: x["les_bornes_de_179"].__setitem__("decidable", False),
             "sans les bornes de `179`"),
            (lambda x: x.__setitem__("les_epreuves_declarees", ["a", "b"]),
             "qui déclare deux épreuves sans diviser la garantie"),
            (lambda x: x["la_courbe"]["les_barreaux"][0].__setitem__(
                "les_decalages_muets", None),
             "dont un barreau n'a pas son compte de décalages muets"),
            (lambda x: x["le_verdict"].__setitem__(
                "lerreur_de_chunk_de_205_en_voxels", None),
             "sans l'erreur de chunk de `205`"),
            (lambda x: x.__setitem__("decidable", False), "indécidable")):
        v(f"une mesure {quoi} est refusée", _refuse(d, sortie, casse))
    dessiner(d, sortie)

    print(f"figure_la_transition_fixe_t_elle_lerreur_de_chunk.py  "
          f"{'ALL PASS' if not echecs else str(echecs) + ' ÉCHECS'} "
          f"({echecs} failures, {faits} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", type=Path,
                   default=RACINE / "docs" / "mesures"
                   / "la_transition_fixe_t_elle_lerreur_de_chunk.json")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "209_la_transition_fixe_t_elle_lerreur_de_chunk.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier(a.json, a.sortie)
    chemin, *_ = dessiner(lire(a.json), a.sortie)
    print(f"écrit : {chemin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
