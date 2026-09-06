#!/usr/bin/env python3
"""Le raccrochage gagne un pas et perd la marche — son gain ne survit pas à UN tour.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Le tableau des six marches est illisible en chiffres : cinq
d'entre elles montent et une descend, et c'est **laquelle descend** qui est le résultat. Tracées
ensemble contre la demi-épaisseur d'une feuille, elles disent d'un coup d'œil ce que quatre
lignes de nombres cachent — le raccrochage par point est le MEILLEUR au premier tour et le
PIRE au quatrième.

⭐⭐ Le panneau de la rugosité porte le mécanisme, et il est le même que celui que ce dépôt a
déjà payé sur l'encre : un « champ » estimé point par point n'était qu'une **constante** noyée
dans son propre bruit. Ici la constante est un décalage par tour, la rugosité du champ par
point monte de 5 à 25 µm, et celle du décalage global vaut zéro par construction.

⚠ Les six marches sont dessinées, y compris celles qui échouent, et la marche au hasard avec.
Une figure qui n'aurait montré que la gagnante serait un argument, pas une mesure.

Usage :
    uv run python src/figures/figure_derouler_en_raccrochant.py --verifier
    uv run python src/figures/figure_derouler_en_raccrochant.py \\
        --sortie docs/images/75_derouler_en_raccrochant.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "derouler_en_raccrochant.json"
BALAYAGE = RACINE / "docs" / "mesures" / "derouler_en_raccrochant_balayage.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
BLEU = (54, 88, 132)
VERT = (60, 128, 84)
VIOLET = (118, 78, 140)
CADRE = (200, 200, 200)

# ⚠ L'ordre et les couleurs sont déclarés UNE fois : trois panneaux les partagent, et deux
# légendes qui divergeraient feraient lire une courbe sous le mauvais nom.
MARCHES = [
    ("marche_aveugle", "aveugle — aucun raccrochage", BLEU, 4),
    ("marche_normales_lissees", "raccroché, NORMALES lissées", AMBRE, 3),
    ("marche_accordee", "raccroché, décalages accordés", VIOLET, 2),
    ("marche_raccrochee", "raccroché, par point", VERT, 2),
    ("marche_globale", "raccroché, un décalage par tour", DISCRET, 2),
    ("marche_hasard", "gabarit mélangé (témoin)", ROUGE, 2),
]


def prose(m: dict) -> list[str]:
    """Les cinq phrases que la figure porte, et pas une de plus.

    ⚠ Une prose qui grossit à chaque tranche finit par faire une image plus haute que large,
    donc illisible d'un coup d'œil. Ce qui est retiré est ce que les panneaux montrent déjà.
    """
    vi = m["le_gain_vieillit"]
    d = m["derive_par_tour_um"]
    b = m.get("_balayage")
    out = [
        f"depuis la spire {m['depuis']}, {m['cellules_au_depart']} cellules, pas nominal "
        f"{m['ecart_lu_um']} um, un seul bit de supervision (le sens).",
        f"panneau A : le raccrochage par point derive de {d['raccroche']:+.1f} um par tour "
        f"contre {d['aveugle']:+.1f} pour l'aveugle. ni l'accord des voisins "
        f"({d['accorde']:+.1f}) ni une fenetre deux fois plus etroite ({d['etroite']:+.1f}) "
        "ne le rattrapent.",
        f"panneau C, LA REPONSE : un pas raccroche gagne {vi[0]['gain_um']:+.1f} um depuis une "
        f"spire PUBLIEE et {vi[1]['gain_um']:+.1f} um des qu'UN tour aveugle a ete fait ; "
        f"ensuite la mediane vaut {m['gain_median_apres_le_premier_pas_um']:+.1f} um et le "
        "signe change. le raccrochage ne raccroche que ce qui est deja a sa place.",
        f"panneau B : elargir le support de la derivee fait tomber la dispersion des normales "
        f"de {m['au_premier_tour_par_support'][0]['dispersion_deg']:.2f}° a "
        f"{m['au_premier_tour_par_support'][-1]['dispersion_deg']:.2f}° et laisse l'erreur du "
        f"pas ou elle est ({m['au_premier_tour_par_support'][0]['erreur_um']:.1f} um contre "
        f"{m['au_premier_tour_par_support'][-1]['erreur_um']:.1f}). la dispersion est donc un "
        "SYMPTOME, pas la cause : quatre soupcons testes, quatre ecartes.",
        f"panneau A : lisser les NORMALES avant le pas fait tomber la derive "
        f"du raccrochage de {d['raccroche']:+.1f} a {d['normales']:+.1f} um par tour, et ne "
        f"fait RIEN pour l'aveugle ({d['aveugle']:+.1f} contre {d['aveugle_normales']:+.1f}). "
        "c'est la preuve que le degat etait celui du raccrochage : il ride la nappe, la nappe "
        "gate ses normales, et la mauvaise normale gate le pas suivant.",
    ]
    if b:
        out.append(
            "panneau D, RETRACTATION : a 191 cellules le decalage unique rendait une derive "
            "NEGATIVE et etait publie comme le seul tenant la feuille ; a "
            f"{b['points'][-1]['cellules_au_depart']} cellules il derive de "
            f"{b['points'][-1]['derive_par_tour_um']['globale']:+.1f} um par tour. un resultat "
            "qui s'inverse quand l'echantillon grandit n'etait pas un resultat.")
        out.append(
            "ce qui SURVIT au balayage : le raccrochage par point derive plus que l'aveugle "
            "aux trois tailles, et aucun contendant ne tient la feuille a la fin sur les deux "
            "plus larges.")
    return out


def _cadre(art, x0, y0, w, h):
    art.rectangle([x0, y0, x0 + w, y0 + h], outline=CADRE)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    marge = 40
    pw, ph = 400, 220
    ecart = 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 106 + ph + 138 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18),
             "Le raccrochage gagne un pas et perd la marche : son gain ne survit pas a UN tour",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"depart spire {m['depuis']}, {m['cellules_au_depart']} cellules, "
             f"{m['tours_mesures']} tours, pas nominal {m['ecart_lu_um']} um",
             fill=DISCRET, font=moyen)

    tours = [e["tours"] for e in m["marche_raccrochee"]]
    demi = m["demi_epaisseur_um"]

    def axe_x(x0, k):
        return x0 + (k - tours[0]) / max(1, tours[-1] - tours[0]) * pw

    # ---------- A : les six marches ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · l'erreur a chaque tour, contre la demi-epaisseur d'une feuille",
             fill=TEXTE, font=moyen)
    _cadre(art, ax, ay, pw, ph)
    top = max(e["erreur_um"] for cle, _, _, _ in MARCHES for e in m[cle]) * 1.05
    yd = ay + ph - demi / top * ph
    art.line([ax, yd, ax + pw, yd], fill=TEXTE)
    # ⚠ Le libellé va à DROITE : à gauche il tombait sur la courbe globale, et une légende
    # posée sur la courbe qu'elle commente est une légende qu'on lit de travers.
    art.text((ax + pw - 96, yd - 14), f"demi-feuille {demi:.0f}µ", fill=TEXTE, font=petit)
    # ⚠ Les extrêmes de l'axe sont écrits : une courbe sans échelle est un dessin.
    art.text((ax + 4, ay + 2), f"{top:.0f}µ", fill=DISCRET, font=petit)
    art.text((ax + 4, ay + ph - 30), "0µ", fill=DISCRET, font=petit)
    # ⚠ Le mot « tour » va SOUS les graduations, au milieu : à gauche il tombait sur le « 1 »,
    # à droite sur le dernier tour. Un axe dont le nom recouvre une graduation fait lire un
    # numéro de tour de travers.
    art.text((ax + pw / 2 - 12, ay + ph + 17), "tour", fill=DISCRET, font=petit)
    # ⚠ La note de couleurs va SOUS l'axe, à côté du mot « tour » : en haut à gauche elle
    # tombait sur la graduation de l'échelle, en haut à droite sur la courbe du témoin.
    art.text((ax + pw / 2 + 26, ay + ph + 17), "· couleurs : legende sous les panneaux",
             fill=DISCRET, font=petit)
    for cle, _, coul, ep in MARCHES:
        pts = [(axe_x(ax, e["tours"]), ay + ph - e["erreur_um"] / top * ph) for e in m[cle]]
        for a_, b_ in zip(pts, pts[1:]):
            art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=ep)
        for x_, y_ in pts:
            art.ellipse([x_ - ep, y_ - ep, x_ + ep, y_ + ep], fill=coul)
    for k in tours:
        art.text((axe_x(ax, k) - 4, ay + ph + 3), str(k), fill=DISCRET, font=petit)

    # ---------- B : la dispersion tombe, l'erreur ne suit pas ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20),
             "B · support elargi : la dispersion tombe, l'erreur non",
             fill=TEXTE, font=moyen)
    _cadre(art, bx, by, pw, ph)
    prem = m["au_premier_tour_par_support"]
    e_max = max(e["erreur_um"] for e in prem) * 1.35
    d_max = max(e["dispersion_deg"] for e in prem) * 1.35
    lgb = pw / (len(prem) * 2 + 1)
    for k, e_ in enumerate(prem):
        x_ = bx + lgb * (2 * k + 1)
        he = e_["erreur_um"] / e_max * (ph - 44)
        hd = e_["dispersion_deg"] / d_max * (ph - 44)
        art.rectangle([x_ - lgb * 0.44, by + ph - he, x_ - 2, by + ph], fill=BLEU)
        art.rectangle([x_ + 2, by + ph - hd, x_ + lgb * 0.44, by + ph], fill=ROUGE)
        # ⚠ Les deux étiquettes sont décalées VERTICALEMENT : côte à côte, elles se touchaient
        # dès que les deux barres avaient presque la même hauteur — c'est-à-dire au premier
        # support, celui qui sert de référence.
        art.text((x_ - lgb * 0.44, by + ph - he - 28), f"{e_['erreur_um']:.0f}µ",
                 fill=BLEU, font=petit)
        art.text((x_ + 2, by + ph - hd - 14), f"{e_['dispersion_deg']:.1f}°",
                 fill=ROUGE, font=petit)
        art.text((x_ - 24, by + ph + 3), f"pas {e_['pas_de_normale']}", fill=DISCRET,
                 font=petit)
    art.text((bx + 6, by + 6), "bleu : l'erreur du premier pas", fill=BLEU, font=petit)
    art.text((bx + 6, by + 22), "rouge : la dispersion des normales", fill=ROUGE, font=petit)
    art.text((bx + 6, by + ph + 17),
             f"au premier tour seulement : de {prem[0]['cellules']} a "
             f"{prem[-1]['cellules']} cellules, donc comparable", fill=DISCRET, font=petit)

    # ---------- C : le gain qui vieillit ----------
    cx, cy = marge, 96 + ph + 106
    art.text((cx, cy - 20),
             "C · le gain d'UN pas, depuis une surface qui vieillit",
             fill=TEXTE, font=moyen)
    _cadre(art, cx, cy, pw, ph)
    vieil = m["le_gain_vieillit"]
    gmax = max(abs(e["gain_um"]) for e in vieil) * 1.25
    zero = cy + ph / 2
    art.line([cx, zero, cx + pw, zero], fill=TEXTE)
    # ⚠ Le libellé du zéro se pose SOUS le cadre : sur la ligne, il tombait en travers des
    # barres qu'il commente.
    art.text((cx + 6, cy + ph + 49), "la ligne du milieu : 0, aucun gain",
             fill=TEXTE, font=petit)
    lg2 = pw / (len(vieil) * 2 + 1)
    for k, e_ in enumerate(vieil):
        x_ = cx + lg2 * (2 * k + 1)
        h_ = e_["gain_um"] / gmax * (ph / 2 - 16)
        coul = VERT if e_["gain_um"] > 0 else ROUGE
        art.rectangle([x_ - lg2 * 0.44, zero - max(h_, 0.0) - (0 if h_ > 0 else -h_) * 0,
                       x_ + lg2 * 0.44, zero] if h_ > 0 else
                      [x_ - lg2 * 0.44, zero, x_ + lg2 * 0.44, zero - h_], fill=coul)
        art.text((x_ - 18, zero - h_ + (-16 if h_ > 0 else 4)),
                 f"{e_['gain_um']:+.0f}µ", fill=coul, font=petit)
        art.text((x_ - 4, cy + ph + 3), str(e_["tours_de_vieillissement"]),
                 fill=DISCRET, font=petit)
    # ⚠ Les deux legendes vont SOUS l'axe des ages : posees en haut a gauche elles tombaient
    # sur la premiere barre, qui est justement la seule qui compte.
    art.text((cx + 6, cy + ph + 17),
             "age de la surface de depart, en tours deroules en aveugle", fill=DISCRET,
             font=petit)
    art.text((cx + 6, cy + ph + 33),
             f"age 0 = une spire PUBLIEE : {vieil[0]['gain_um']:+.1f} um", fill=VERT, font=petit)

    # ---------- D : la derive contre la taille de la boite ----------
    dx, dy = marge + pw + ecart, 96 + ph + 106
    art.text((dx, dy - 20),
             "D · la derive par tour, contre la TAILLE du morceau de nappe",
             fill=TEXTE, font=moyen)
    _cadre(art, dx, dy, pw, ph)
    b = m.get("_balayage")
    if b:
        cotes = [pt["cote_voxels"] for pt in b["points"]]
        vals = [v for pt in b["points"] for v in pt["derive_par_tour_um"].values()
                if v is not None]
        bas, haut = min(vals + [0.0]), max(vals)
        etendue = max(1e-9, haut - bas)

        def yv(v_):
            return dy + ph - (v_ - bas) / etendue * (ph - 24) - 12

        def xc(k):
            return dx + 40 + k / max(1, len(cotes) - 1) * (pw - 80)

        y0_ = yv(0.0)
        art.line([dx, y0_, dx + pw, y0_], fill=TEXTE)
        art.text((dx + 4, y0_ + 3), "0 — l'erreur n'augmente plus", fill=TEXTE, font=petit)
        for cle, nom, coul, ep in MARCHES:
            # ⚠ Le nom d'une marche dans le résultat et sa clé de dérive ne coïncident pas
            # toujours ; la table est écrite ICI plutôt que devinée par des remplacements
            # successifs, qui rendaient une clé plausible pour une marche qui n'existe pas.
            k_ = {"marche_raccrochee": "raccroche", "marche_accordee": "accorde",
                  "marche_fenetre_etroite": "etroite", "marche_globale": "globale",
                  "marche_gabarit_fige": "fige", "marche_normales_lissees": "normales",
                  "marche_aveugle_normales_lissees": "aveugle_normales",
                  "marche_les_deux_remedes": "les_deux",
                  "marche_aveugle": "aveugle", "marche_hasard": "hasard"}[cle]
            pts = [(xc(i), yv(pt["derive_par_tour_um"][k_]))
                   for i, pt in enumerate(b["points"])
                   if pt["derive_par_tour_um"].get(k_) is not None]
            for a_, b_ in zip(pts, pts[1:]):
                art.line([a_[0], a_[1], b_[0], b_[1]], fill=coul, width=ep)
            for x_, y_ in pts:
                art.ellipse([x_ - ep, y_ - ep, x_ + ep, y_ + ep], fill=coul)
        for i, c_ in enumerate(cotes):
            art.text((xc(i) - 24, dy + ph + 3),
                     f"{c_:.0f} vx / {b['points'][i]['cellules_au_depart']} cell.",
                     fill=DISCRET, font=petit)
        # ⚠⚠ Ce libellé nomme la courbe par sa COULEUR, donc il devient faux dès qu'on
        # réordonne `MARCHES`. Il est écrit depuis la table plutôt que recopié : une légende
        # qui désigne la mauvaise courbe est pire que pas de légende.
        gris_ = next(n for c_, n, k_, _ in MARCHES if c_ == "marche_globale")
        art.text((dx + 4, dy + ph + 17),
                 f"« {gris_} » est le seul dont le verdict S'INVERSE", fill=DISCRET,
                 font=petit)

    # ---------- legende, sous les panneaux ----------
    ly = 96 + ph + 106 + ph + 68
    for k, (cle, nom, coul, _) in enumerate(MARCHES):
        col = k % 2
        art.rectangle([marge + col * (pw + ecart), ly + (k // 2) * 17,
                       marge + col * (pw + ecart) + 14, ly + (k // 2) * 17 + 10], fill=coul)
        art.text((marge + col * (pw + ecart) + 20, ly + (k // 2) * 17 - 2), nom,
                 fill=coul, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"marches": len(MARCHES), "tours": len(tours),
            "points_de_balayage": len(m.get("_balayage", {}).get("points", [])),
            "tient": list(m["tient_la_feuille_a_la_fin"]),
            "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    if not MESURE.is_file():
        print("  ⚠ mesure absente : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    if BALAYAGE.is_file():
        m["_balayage"] = json.loads(BALAYAGE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ LES TROIS FAITS QUE LA FIGURE PORTE. Le raccrochage par point gagne au premier tour,
    # il perd au dernier, et un décalage unique par tour est le seul qui descende. Sans les
    # trois, le dessin ne dit rien de plus qu'un tableau.
    v("le raccrochage par point gagne au premier tour",
      m["marche_raccrochee"][0]["erreur_um"] < m["marche_aveugle"][0]["erreur_um"],
      f"{m['marche_raccrochee'][0]['erreur_um']} contre {m['marche_aveugle'][0]['erreur_um']}")
    v("... et perd au dernier",
      m["marche_raccrochee"][-1]["erreur_um"] > m["marche_aveugle"][-1]["erreur_um"],
      f"{m['marche_raccrochee'][-1]['erreur_um']} contre {m['marche_aveugle'][-1]['erreur_um']}")
    # ⚠⚠⚠ LA REVENDICATION DU 2026-09-06 EST RETIRÉE, ET C'EST LE PANNEAU D QUI LA RETIRE.
    # « Le décalage global est le seul dont la dérive descende » était vrai à 191 cellules et
    # faux dès 494 : la figure asserte donc ce qui SURVIT au balayage, pas ce qu'un point
    # isolé disait.
    b = m.get("_balayage")
    v("le balayage porte au moins deux tailles de boîte", b and len(b["points"]) >= 2,
      str(len(b["points"]) if b else 0))
    # ⚠⚠⚠ LE FAIT DU PANNEAU B, ET IL FAUT SES DEUX MOITIÉS : la dispersion baisse avec le
    # support ET l'erreur ne suit pas. La première seule dirait « ça marche », la seconde seule
    # « ça ne sert à rien » ; ensemble elles disent que la dispersion est un symptôme.
    v("élargir le support fait tomber la dispersion des normales",
      m["la_dispersion_baisse_avec_le_support"],
      str([e["dispersion_deg"] for e in m["au_premier_tour_par_support"]]))
    v("... et l'erreur du pas ne suit pas", not m["lerreur_suit_la_dispersion"],
      str([e["erreur_um"] for e in m["au_premier_tour_par_support"]]))
    v("... donc la dispersion est un symptôme", m["la_dispersion_est_un_symptome"])
    # ⚠ Et la comparaison n'est valable qu'au PREMIER tour : au-delà, un support large a mangé
    # le bord et les marches ne sont plus jugées sur la même population.
    v("les supports comparés partent de populations du même ordre",
      max(e["cellules"] for e in m["au_premier_tour_par_support"])
      < 2 * min(e["cellules"] for e in m["au_premier_tour_par_support"]),
      str([e["cellules"] for e in m["au_premier_tour_par_support"]]))
    v("le raccrochage par point dérive plus que l'aveugle à TOUTES les tailles",
      all(pt["derive_par_tour_um"]["raccroche"] > pt["derive_par_tour_um"]["aveugle"]
          for pt in b["points"]),
      str([(pt["derive_par_tour_um"]["raccroche"], pt["derive_par_tour_um"]["aveugle"])
           for pt in b["points"]]))
    v("... et le verdict du décalage global, lui, CHANGE avec la taille",
      "globale" in b["contendants_au_verdict_instable"],
      str(b["contendants_au_verdict_instable"]))
    # ⚠ Le mécanisme doit être visible : la rugosité du champ par point MONTE.
    rug = [x for x in m["rugosite_um"]["raccroche"] if x is not None]
    v("la rugosité du champ par point monte au fil des tours", rug[-1] > rug[0], str(rug))
    # ⚠⚠⚠ LE MÉCANISME, ET IL FAUT SES DEUX MOITIÉS : lisser les normales répare le
    # raccrochage et ne fait RIEN pour l'aveugle. La seconde moitié est celle qui prouve que
    # le dégât venait du raccrochage — sans elle, « ça aide » pourrait juste vouloir dire que
    # les normales sont mauvaises pour tout le monde.
    d_ = m["derive_par_tour_um"]
    v("lisser les normales répare la moitié de ce que le raccrochage coûte",
      d_["normales"] < (d_["raccroche"] + d_["aveugle"]) / 2,
      f"{d_['normales']} contre {d_['raccroche']} et {d_['aveugle']}")
    v("... et ne fait rien pour l'aveugle, qui ne ride rien",
      abs(d_["aveugle_normales"] - d_["aveugle"]) < 3.0,
      f"{d_['aveugle_normales']} contre {d_['aveugle']}")
    # ⚠⚠ ET AUCUN RACCROCHAGE NE BAT L'AVEUGLE, même réparé : c'est le verdict de la tranche.
    v("aucun raccrochage ne bat l'aveugle",
      min(v_ for k_, v_ in d_.items() if k_ not in ("aveugle", "aveugle_normales")
          and v_ is not None) > d_["aveugle"],
      str(d_))
    # ⚠⚠⚠ LE PANNEAU C PORTE LA RÉPONSE : le gain existe depuis une spire publiée et pas
    # depuis une surface d'un tour. Sans les deux moitiés, le dessin ne dirait rien.
    vi = m["le_gain_vieillit"]
    v("le raccrochage gagne depuis une spire publiée", vi[0]["gain_um"] > 5.0,
      str(vi[0]["gain_um"]))
    v("... et ne gagne plus dès qu'un tour aveugle a été fait",
      m["le_gain_nexiste_quau_premier_pas"],
      f"{[e['gain_um'] for e in vi]}")
    # ⚠⚠ Et le témoin qui rend la marche capable d'échouer : le gabarit mélangé doit être pire
    # que tout le reste au dernier tour.
    fins = {c: m["feuille_tenue_a_la_fin"][c]["erreur_um"]
            for c in m["feuille_tenue_a_la_fin"] if m["feuille_tenue_a_la_fin"][c]}
    v("le gabarit mélangé est le pire au dernier tour",
      max(fins, key=fins.get) == "hasard", str(fins))
    v("aucun contendant ne tient la feuille à la plus grande boîte",
      not b["points"][-1]["tient_la_feuille_a_la_fin"],
      str(b["points"][-1]["tient_la_feuille_a_la_fin"]))
    # ⚠⚠ LE FAIT QUI FERME L'AUTRE LECTURE : un décalage global toujours du même signe ne
    # serait qu'une longueur de pas corrigée, et ce dépôt a déjà mesuré ce que celle-là vaut
    # (54,1 µm sur des paires réservées). Il change de signe, donc il corrige tour par tour.
    v("le décalage global change de signe", m["le_global_change_de_signe"],
      str(m["decalage_global_signe_um"]))
    # ⚠⚠⚠ ET UNE SECONDE RÉTRACTATION, plus discrète que la première : à 191 cellules la
    # longueur équivalente du décalage global tombait à 114,7 µm, « à six micromètres de la
    # longueur ajustée sur les cibles ». À 906 cellules elle vaut 161,3. Ce rapprochement
    # était une coïncidence de boîte, pas un fait sur la nappe, et il n'est plus asséré.
    v("toutes les marches ont le même nombre de tours",
      len({len(m[c]) for c, _, _, _ in MARCHES}) == 1,
      str({c: len(m[c]) for c, _, _, _ in MARCHES}))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("les six marches sont dessinées", r["marches"] == 6)
        v("le balayage est dessiné", r["points_de_balayage"] == len(b["points"]),
          str(r["points_de_balayage"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        # ⚠ Une figure à quatre panneaux tient sur deux rangées : elle a donc le droit d'être
        # un peu plus haute que large à cause de la prose, mais pas de devenir une colonne —
        # au-delà, les panneaux ne se comparent plus d'un coup d'œil.
        v("l'image reste une grille, pas une colonne", img.height < img.width * 1.25,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--balayage", type=Path, default=BALAYAGE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_derouler_en_raccrochant.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    m = json.loads(a.mesure.read_text())
    if a.balayage.is_file():
        m["_balayage"] = json.loads(a.balayage.read_text())
    print(json.dumps(dessiner(m, a.sortie), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
