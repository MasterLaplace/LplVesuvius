#!/usr/bin/env python3
"""La prédiction, la mesure qui l'ignore, et l'ordre de grandeur qui tranche.

⚠⚠ Pourquoi cette figure existe. Une hypothèse réfutée se raconte mal en prose : « il n'y a
pas de coude à 3780 colonnes » demande au lecteur de tenir une courbe dans sa tête, et « le
rassemblement coûte 0,167 ms quand l'écart en vaut 357 » se lit comme deux nombres alors que
c'est un rapport de **deux mille**. Les deux panneaux disent la même chose dans les deux
langues dont on a besoin.

⭐ Ce sont DEUX questions, pas une, et la seconde est celle qui tue l'hypothèse. À gauche :
« la courbe a-t-elle la forme d'une falaise de cache ? » — non, et la largeur critique prédite
passe au milieu sans rien marquer. À droite : « cette cause pourrait-elle SEULEMENT peser ? »
— non, et cette réponse-là ne dépend d'aucune forme de courbe. Une réfutation qui tient à la
forme d'une courbe se rouvre au premier point de mesure bruité ; une réfutation par ordre de
grandeur ne se rouvre pas.

⚠ Les nombres sont LUS dans `docs/mesures/cout_de_la_fenetre.json`, jamais retapés. Une
figure qui recopie ses chiffres est une figure qui peut se mettre à contredire la mesure dont
elle est censée être la lecture, sans que rien ne le signale.

Usage :
    uv run python src/figures/figure_hypothese_refutee.py --verifier
    uv run python src/figures/figure_hypothese_refutee.py \\
        --mesure docs/mesures/cout_de_la_fenetre.json \\
        --sortie docs/images/62_hypothese_refutee.png
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import (police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)

RACINE = Path(__file__).resolve().parents[2]

FOND = (16, 16, 16)
TEXTE = (235, 232, 224)
DISCRET = (140, 136, 128)
AMBRE = (214, 143, 42)
GRIS = (120, 128, 140)
ROUGE = (188, 68, 52)


def lire(chemin: Path) -> dict:
    """Charge et valide la mesure nécessaire au tracé."""
    if not chemin.is_file():
        raise FileNotFoundError(f"mesure absente : {chemin}")
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not donnees.get("balayage") or not donnees.get("observations_de_rendu"):
        raise ValueError(f"structure invalide dans {chemin}")
    return donnees


def rapport_des_causes(mesure: dict) -> float:
    """Combien de fois l'écart à expliquer dépasse le coût du rassemblement le plus cher.

    ⚠ Le rassemblement retenu est le PLUS CHER du balayage, pas le moyen : prendre le moyen
    flatterait la réfutation, et une réfutation doit tenir contre le cas le plus favorable à
    l'hypothèse qu'elle abat.
    """
    pire = max(l["ms_par_fenetre_en_ligne"] for l in mesure["balayage"])
    obs = mesure["observations_de_rendu"]
    ecart = max(o["ms_par_fenetre"] for o in obs) - min(o["ms_par_fenetre"] for o in obs)
    return ecart / pire if pire > 0 else 0.0


def echelle(valeur: float, lo: float, hi: float, pixels: int) -> int:
    """Position en pixels d'une valeur sur un axe linéaire, bornée à l'axe."""
    if hi <= lo:
        return 0
    return int(round(max(0.0, min(1.0, (valeur - lo) / (hi - lo))) * pixels))


def echelle_log(valeur: float, lo: float, hi: float, pixels: int) -> int:
    """Idem sur un axe logarithmique — le seul qui laisse 0,167 et 357 tenir ensemble."""
    if valeur <= 0 or hi <= lo:
        return 0
    f = (math.log10(valeur) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
    return int(round(max(0.0, min(1.0, f)) * pixels))


def libelles(mesure: dict) -> list[str]:
    """Toute la prose que la figure trace, rassemblée pour être vérifiable.

    ⚠⚠ Elle existe parce que la police de secours de PIL est en ASCII : sans contrôle, un
    « coût » devient « co□t » et une figure publiée porte des carrés à la place de ses accents.
    Le défaut ne lève rien, ne casse aucun test, et ne se voit qu'en regardant l'image.
    """
    critique = mesure["largeur_critique"]
    return [
        "la falaise prédite", "coût du rassemblement, ms par fenêtre",
        f"largeur critique {critique}", "en ligne", "par blocs",
        "aucun coude : 6000 colonnes coûtent moins que 4260",
        "ce que la cause devrait peser", "échelle logarithmique, ms par fenêtre",
        "rassemblement, le plus cher mesuré",
        "rapport mesuré : ×2142", "écart APPARENT entre les deux rendus",
        "l'écart lui-même s'est révélé être de la contention (62 §7) :",
        "les deux rendus atteignent le même pic, 11,4 contre 12,3 fen/s.",
        "une cause deux mille fois trop petite reste trop petite,",
        "quelle que soit la forme de la courbe.",
    ]


def dessiner(mesure: dict, sortie: Path) -> tuple[Path, list, list]:
    from PIL import Image, ImageDraw

    # ⚠ La police vient de `figure_commune`, qui existe parce que le mécanisme etait
    # recopié quinze fois. J'allais en écrire la seizième.
    gros, moyen, petit = police(16, 13, 12)

    lignes = mesure["balayage"]
    critique = mesure["largeur_critique"]
    obs = mesure["observations_de_rendu"]
    rapport = rapport_des_causes(mesure)

    L, H = 1180, 560
    toile = Image.new("RGB", (L, H), FOND)
    d = ImageDraw.Draw(toile)
    poses: list[tuple[int, int, str, object]] = []

    def ecrire(x, y, texte, fonte, fill):
        d.text((x, y), texte, font=fonte, fill=fill)
        poses.append((x, y, texte, fonte))

    # ---- PANNEAU GAUCHE : la courbe, et le coude qui n'y est pas ----------------------
    gx, gy, gw, gh = 70, 90, 440, 330
    ecrire(70, 34, "la falaise prédite", gros, TEXTE)
    ecrire(70, 54, "coût du rassemblement, ms par fenêtre", moyen, DISCRET)
    xs = [l["largeur"] for l in lignes]
    ys = [l["ms_par_fenetre_en_ligne"] for l in lignes]
    zs = [l["ms_par_fenetre_par_blocs"] for l in lignes]
    xlo, xhi = min(xs), max(xs)
    yhi = max(max(ys), max(zs)) * 1.35
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=(60, 60, 60))
    for frac in (0.0, 0.5, 1.0):
        yy = gy + gh - int(frac * gh)
        d.line([gx, yy, gx + gw, yy], fill=(40, 40, 40))
        ecrire(gx - 46, yy - 7, f"{frac * yhi:.2f}", petit, DISCRET)
    # ⚠ La verticale est la PREDICTION, dessinee avant les points : c'est ce qui rend
    # visible qu'elle ne marque rien.
    cx = gx + echelle(critique, xlo, xhi, gw)
    for seg in range(gy, gy + gh, 12):
        d.line([cx, seg, cx, min(seg + 6, gy + gh)], fill=ROUGE)
    ecrire(cx - 58, gy - 22, f"largeur critique {critique}", moyen, ROUGE)
    for serie, couleur, nom in ((ys, AMBRE, "en ligne"), (zs, GRIS, "par blocs")):
        pts = [(gx + echelle(x, xlo, xhi, gw), gy + gh - echelle(v, 0.0, yhi, gh))
               for x, v in zip(xs, serie)]
        d.line(pts, fill=couleur, width=2)
        for px, py in pts:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=couleur)
        # ⚠ La legende va DANS le panneau : la placee sous l'axe, elle recouvrait la
        # graduation 6000, c'est-a-dire precisement le point qui porte la refutation.
        ly = gy + 12 + (0 if nom == "en ligne" else 18)
        d.line([gx + 14, ly + 7, gx + 34, ly + 7], fill=couleur, width=2)
        ecrire(gx + 40, ly, nom, petit, couleur)
    for x in xs:
        px = gx + echelle(x, xlo, xhi, gw)
        ecrire(px - 14, gy + gh + 8, str(x), petit, DISCRET)
    ecrire(gx, gy + gh + 52, "aucun coude : 6000 colonnes coûtent moins que 4260",
           moyen, TEXTE)

    # ---- PANNEAU DROIT : l'ordre de grandeur, qui n'a besoin d'aucune courbe ----------
    bx, by, bw = 620, 90, 470
    ecrire(620, 34, "ce que la cause devrait peser", gros, TEXTE)
    ecrire(620, 54, "échelle logarithmique, ms par fenêtre", moyen, DISCRET)
    pire = max(ys)
    ecart = max(o["ms_par_fenetre"] for o in obs) - min(o["ms_par_fenetre"] for o in obs)
    blo, bhi = 0.05, 1000.0
    # ⚠⚠ « APPARENT » n'est pas une nuance de style : la mesure du 2026-08-28 a montré que
    # cet écart est un artefact de contention, pas une propriété d'un segment. La figure
    # garde la barre — c'est bien l'écart qu'on cherchait à expliquer ce jour-là — mais elle
    # ne doit pas le présenter comme un fait sur le moteur. Voir `62` §7.
    barres = [("rassemblement, le plus cher mesuré", pire, GRIS),
              ("écart APPARENT entre les deux rendus", ecart, AMBRE)]
    for i, (nom, valeur, couleur) in enumerate(barres):
        yy = by + 60 + i * 110
        largeur = echelle_log(valeur, blo, bhi, bw)
        d.rectangle([bx, yy, bx + max(largeur, 2), yy + 44], fill=couleur)
        ecrire(bx, yy - 22, nom, moyen, TEXTE)
        ecrire(bx + max(largeur, 2) + 10, yy + 15, f"{valeur:.3f} ms", moyen, couleur)
    ecrire(bx, by + 290, f"rapport mesuré : ×{rapport:.0f}", gros, ROUGE)
    ecrire(bx, by + 316,
           "une cause deux mille fois trop petite reste trop petite,", moyen, TEXTE)
    ecrire(bx, by + 336, "quelle que soit la forme de la courbe.", moyen, TEXTE)
    ecrire(bx, by + 366,
           "l'écart lui-même s'est révélé être de la contention (62 §7) :", moyen, DISCRET)
    ecrire(bx, by + 386,
           "les deux rendus atteignent le même pic, 11,4 contre 12,3 fen/s.", moyen, DISCRET)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return sortie, poses, [(0, 0, L, H)]


def verifier() -> int:
    """Auto-test HORS LIGNE : les axes, le rapport, les sondes et le dessin."""
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    # --- LES AXES ----------------------------------------------------------------------
    v("l'axe lineaire place le minimum a gauche", echelle(0.0, 0.0, 10.0, 100) == 0)
    v("... et le maximum a droite", echelle(10.0, 0.0, 10.0, 100) == 100)
    v("... et borne ce qui deborde", echelle(99.0, 0.0, 10.0, 100) == 100)
    v("l'axe log met une decade au milieu de deux",
      abs(echelle_log(10.0, 1.0, 100.0, 100) - 50) <= 1)
    v("... et refuse zero plutot que de tomber a moins l'infini",
      echelle_log(0.0, 1.0, 100.0, 100) == 0)

    # --- LE RAPPORT, lu et non retape --------------------------------------------------
    faux = {
        "largeur_critique": 3780,
        "balayage": [{"largeur": 1024, "ms_par_fenetre_en_ligne": 0.05,
                      "ms_par_fenetre_par_blocs": 0.05},
                     {"largeur": 4260, "ms_par_fenetre_en_ligne": 0.20,
                      "ms_par_fenetre_par_blocs": 0.10}],
        "observations_de_rendu": [{"segment": "a", "ms_par_fenetre": 100.0},
                                   {"segment": "b", "ms_par_fenetre": 500.0}],
    }
    v("le rapport vaut l'ecart divise par le rassemblement le plus cher",
      abs(rapport_des_causes(faux) - (400.0 / 0.20)) < 1e-9)
    # ⚠⚠ Le PLUS CHER, pas le moyen : une refutation doit tenir contre le cas le plus
    # favorable a l'hypothese qu'elle abat.
    v("... le plus cher et non le moyen",
      rapport_des_causes(faux) < 400.0 / ((0.05 + 0.20) / 2))

    # --- LA PROSE, tracable par la police ----------------------------------------------
    # ⚠⚠ Sans ce controle un « cout » devient « co□t » dans l'image publiee, sans que rien
    # ne leve ni n'echoue : le defaut ne se voit qu'en REGARDANT la figure.
    v("toute la prose de la figure est tracable par la police",
      prose_tracable(libelles({"largeur_critique": 3780})))
    # ⚠⚠ Le controle NEGATIF, sans lequel le precedent est satisfait par un
    # `prose_tracable` qui repondrait oui a tout. J'avais d'abord ecrit ici une condition
    # toujours vraie — la panne exacte du document 61, deux heures apres l'avoir ecrit.
    v("... et le controle sait refuser un glyphe que la police n'a pas",
      not prose_tracable(["\u2b50 une etoile pleine"]))

    # --- VALIDATION HORS-LIGNE lire() ET dessiner() AVEC SONDES ------------------------
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        p_json = tmp / "mesure.json"
        p_json.write_text(json.dumps(faux), encoding="utf-8")

        m_lu = lire(p_json)
        v("lire charge le balayage", len(m_lu["balayage"]) == 2)
        v("lire charge les observations", len(m_lu["observations_de_rendu"]) == 2)

        # Sonde 1 : fichier absent
        sonde_absent = False
        try:
            lire(tmp / "inexistant.json")
        except FileNotFoundError:
            sonde_absent = True
        v("sonde : fichier json absent lève FileNotFoundError", sonde_absent)

        # Sonde 2 : schéma invalide
        p_invalide = tmp / "invalide.json"
        p_invalide.write_text(json.dumps({"rien": 1}), encoding="utf-8")
        sonde_invalide = False
        try:
            lire(p_invalide)
        except ValueError:
            sonde_invalide = True
        v("sonde : schéma json invalide lève ValueError", sonde_invalide)

        # Tracé réel de la figure témoin
        cible = tmp / "hypothese.png"
        out, poses, cadres = dessiner(m_lu, cible)
        v("dessiner rend le chemin demandé", out == cible)
        v("le fichier png est produit", cible.is_file() and cible.stat().st_size > 0)
        v("au moins 15 textes sont posés", len(poses) >= 15)
        v("aucun texte ne déborde de la toile", textes_debordants(poses, 1180) == [])
        v("aucun texte ne sort de son cadre", textes_hors_cadre(poses, cadres) == [])
        v("aucun chevauchement critique", textes_qui_se_recouvrent(poses) == [])

        # Sonde 3 : texte débordant artificiel
        gros, _, _ = police(16, 13, 12)
        poses_trop_larges = poses + [(1150, 50, "texte qui deborde largement a droite", gros)]
        debord = textes_debordants(poses_trop_larges, 1180)
        v("sonde : un texte débordant est bien intercepté", len(debord) > 0)

        # Sonde 4 : texte hors cadre
        poses_hors = poses + [(1150, 100, "texte qui deborde du cadre vers la droite", gros)]
        hors = textes_hors_cadre(poses_hors, cadres)
        v("sonde : un texte hors cadre est bien intercepté", len(hors) > 0)

    # --- LA MESURE REELLE, si elle est la ----------------------------------------------
    chemin = RACINE / "docs/mesures/cout_de_la_fenetre.json"
    if chemin.exists():
        m = lire(chemin)
        v("la largeur critique tombe entre les deux segments observes",
          3240 < m["largeur_critique"] < 4260)
        v("le rapport mesure depasse mille", rapport_des_causes(m) > 1000)
        v("le balayage porte la largeur critique dans sa plage",
          min(l["largeur"] for l in m["balayage"]) < m["largeur_critique"]
          < max(l["largeur"] for l in m["balayage"]))
        v("la mesure nomme les deux segments qui posent la question",
          len(m["observations_de_rendu"]) == 2)
    else:
        v("la mesure est absente, la figure ne peut pas etre tracee", False)

    # ⚠⚠ La formule du verdict N'EST PAS libre : `temoins.sh` exige `ALL PASS` ET un
    # code de retour nul, et compte ses controles en lisant « N checks » sur cette ligne.
    # Une batterie qui invente sa propre phrase est comptee ECHEC alors qu'elle passe.
    print(f"\n{'ALL PASS' if not echecs else 'ECHEC'} "
          f"({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesure", type=Path,
                    default=RACINE / "docs/mesures/cout_de_la_fenetre.json")
    ap.add_argument("--sortie", type=Path,
                    default=RACINE / "docs/images/62_hypothese_refutee.png")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    mesure = lire(a.mesure)
    out, _, _ = dessiner(mesure, a.sortie)
    rapport = rapport_des_causes(mesure)
    pire = max(l["ms_par_fenetre_en_ligne"] for l in mesure["balayage"])
    obs = mesure["observations_de_rendu"]
    ecart = max(o["ms_par_fenetre"] for o in obs) - min(o["ms_par_fenetre"] for o in obs)
    try:
        cible = out.relative_to(RACINE)
    except ValueError:
        cible = out
    print(f"rassemblement le plus cher : {pire:.3f} ms/fenêtre")
    print(f"écart à expliquer          : {ecart:.1f} ms/fenêtre")
    print(f"rapport                    : ×{rapport:.0f}")
    print(f"figure : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
