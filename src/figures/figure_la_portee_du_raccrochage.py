#!/usr/bin/env python3
"""Jusqu'ou la marche va avant d'etre plus pres de la mauvaise feuille.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Sept tranches ont mesure ce que coute UN pas. Le but n'est pas
un pas mais le DEROULEMENT : une marche qui traverse plusieurs feuilles en partant de sa seule
spire d'ancrage, en recalculant tout sur ses propres predictions. Un gain sur un pas et une
portee sont deux quantites differentes, et rien ne dit d'avance qu'elles vont dans le meme sens.

⚠⚠⚠ ET ELLES N'Y VONT PAS. C'est le resultat que cette figure porte, et il contredit sept
tranches lues trop vite : le raccrochage aide sur les deux premiers bras, puis coute, et sa
portee est PLUS COURTE que celle du pas normal seul. Une erreur qui se compose ne se lit pas
sur un pas.

Panneau A : l'erreur bras par bras et le seuil qui perd la marche. Panneau B : ce que chaque
bras DEMANDE, mesure sur le corpus seul — un bras que le corpus fait sauter de huit feuilles
n'est pas une methode qui echoue. Panneau C : la couverture, identique pour les quatre
marcheurs, donc une perte qui n'explique aucune difference entre eux.

Usage :
    uv run python src/figures/figure_la_portee_du_raccrochage.py --verifier
    uv run python src/figures/figure_la_portee_du_raccrochage.py \\
        --sortie docs/images/75_la_portee_du_raccrochage.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import police, prose_tracable  # noqa: E402
from figure_le_residu_est_une_translation import couper  # noqa: E402
from lecart_apparie import tranche  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_portee_du_raccrochage.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
PALE = (243, 231, 227)
BLEU_PALE = (222, 231, 240)
CADRE = (200, 200, 200)

BLEU = (54, 88, 132)
COULEUR = {"rien": (70, 70, 70), "raccroche": VERT, "raccroche_lisse": BLEU,
           "melange": AMBRE, "oracle": ROUGE}
MARQUE = {"raccroche": "le chemin deploye", "raccroche_lisse": "+ nappe lissee entre deux bras",
          "rien": "le pas normal seul", "melange": "le temoin melange",
          "oracle": "la borne (elle regarde la cible)"}


def prose(m: dict) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["lignes"] if x["marcheur"] == nom)

    e, inv = m["ecart_au_pas_normal"], m["ecart_du_pas_normal"]
    el = m["ecart_du_lissage_au_raccrochage"]
    epn = m["ecart_du_lissage_au_pas_normal"]
    dep = next(x for x in m["lignes"] if x["deploye"])
    gl_txt = " ".join(f"{g:.0f}" for g in dep["glissements_um"])
    hors = m["bras_hors_du_pas_nominal"]
    return [
        f"la marche part de la spire {m['ancre']} et vise {m['spires_visees']}. ⚠ elle ne "
        f"connait QUE sa spire de depart : a chaque bras elle repart de sa PROPRE prediction, "
        f"y recalcule ses normales, y relit son gabarit. relire les spires publiees en chemin "
        "serait se re-ancrer a chaque pas, et la portee mesurerait les ancres au lieu de la "
        "marche.",
        f"⚠⚠ le seuil vient de la MATIERE : une marche est perdue quand son erreur depasse la "
        f"demi-feuille ({m['demi_feuille_um']} um), parce qu'au-dela le point predit est plus "
        f"pres de la feuille VOISINE que de la sienne — et rien en aval ne peut le savoir. la "
        "portee s'arrete au premier echec : repasser sous le seuil apres l'avoir franchi n'est "
        "pas rattraper, c'est batir sur une erreur."
        + (f" ⚠ la borne, elle, va jusqu'a {m['portee_de_loracle']} — soit exactement les "
           f"{m['bras_au_pas_nominal']} bras que le corpus demande au pas nominal (panneau B) : "
           "ce qui l'arrete est la matiere."
           if m["portee_de_loracle"] == m["bras_au_pas_nominal"] else ""),
        f"⚠⚠⚠ PORTEE : le chemin deploye traverse {m['portee_du_deploye']} spires, le pas "
        f"normal seul {m['portee_sans_rien_faire']}, le temoin melange {m['portee_du_temoin']}, "
        f"la borne {m['portee_de_loracle']}. le raccrochage porte plus loin que le pas normal : "
        f"{'OUI' if m['le_raccrochage_porte_plus_loin'] else 'NON'}.",
        (f"⚠⚠⚠ LE CINQUIEME MARCHEUR n'ajoute AUCUN reglage : il applique a la NAPPE le voisinage "
         f"deja deploye sur le champ de decalage — meme demi-largeur, meme regle de majorite — "
         f"et garde le meme masque, donc les colonnes restent appariables. portee "
         f"{m['portee_de_la_nappe_lissee']}, ecart au raccrochage "
         f"{el['ecart_median_um']:+.1f} um sur {el['pas_ameliores']}/{el['pas']} bras, "
         f"intervalle {el['intervalle_um']} : "
         f"{'IL AIDE' if m['le_lissage_de_la_nappe_aide'] else 'il ne tranche pas'}. et "
         f"face au PAS NORMAL SEUL il revient a parite : {epn['ecart_median_um']:+.1f} um sur "
         f"{epn['pas_ameliores']}/{epn['pas']} bras, intervalle {epn['intervalle_um']} — aucun "
         "des deux sens ne tranche. le lissage de la nappe reprend donc PRESQUE TOUT ce que le "
         "raccrochage coute a une marche, en n'ajoutant aucun reglage."
         if el and epn else "⚠ le cinquieme marcheur n'a pas de bras commun avec le raccrochage."),
        (f"⚠⚠⚠ et l'ecart apparie tranche DANS L'AUTRE SENS : le pas normal seul est a "
         f"{inv['ecart_median_um']:+.1f} um du raccrochage sur {inv['pas_ameliores']}/"
         f"{inv['pas']} bras, intervalle {inv['intervalle_um']} — trois conditions sans seuil, "
         f"les trois tenues. le raccrochage gagne les deux premiers bras "
         f"({par('raccroche')['erreurs_um'][0]:.1f} contre "
         f"{par('rien')['erreurs_um'][0]:.1f} um) puis les perd tous. aucune mesure sur UN pas "
         "ne pouvait le voir : l'erreur d'un bras devient la surface sur laquelle le suivant "
         "estime ses normales et relit son gabarit, donc elle se compose. ⚠⚠ et le glissement "
         f"que la correlation peut proposer vaut au plus ±{m['glissement_maximal_um']:.0f} um, "
         f"soit {m['glissement_en_demi_feuilles']:.2f} demi-feuille EXACTEMENT : un seul "
         "raccrochage ne peut donc PAS poser la cellule sur la feuille voisine. ce qui derive "
         f"n'est pas un pas mais leur somme — {gl_txt} um bras par bras. ⚠ que les signes "
         "soient correles d'un bras a l'autre n'est PAS mesure : l'affirmer serait refaire la "
         "faute que ce module a deja eu a corriger."
         if inv else "⚠ aucun bras commun : l'ecart apparie n'est pas calculable."),
        (f"⚠⚠ panneau B : le corpus demande a chaque bras un ecart qui lui est propre, et le "
         f"bras {hors[0] if hors else '—'} en demande "
         f"{max(b['ecart_um'] for b in m['bras_du_corpus']):.0f} um, soit "
         f"{max(b['ecart_um'] for b in m['bras_du_corpus']) / m['pas_nominal_um']:.1f} fois le "
         "pas nominal. ce qui s'y arrete s'arrete sur la MATIERE et non sur la methode — et "
         "c'est pourquoi la borne elle-meme y echoue."
         if hors else "⚠ panneau B : tous les bras demandent le pas nominal a une demi-feuille "
         "pres, donc rien de ce tableau ne s'explique par un trou du corpus."),
        f"⚠⚠ panneau C : la marche PERD DES CELLULES — {m['cellules_au_premier_bras']} au "
        f"premier bras, {m['cellules_au_dernier_bras']} au dernier, soit "
        f"{m['part_de_nappe_gardee']} de la nappe. et comme deux marcheurs divergent, leurs "
        "masques divergent : chaque ecart apparie est donc pris sur les cellules COMMUNES aux "
        "deux, jamais sur deux medianes publiees separement. exiger des couvertures identiques "
        "serait exiger que les marcheurs ne divergent pas, c'est-a-dire qu'il n'y ait rien a "
        "mesurer.",
    ]


ANNOTATIONS: list = []


def ecrire(art, xy, texte: str, fill, font, borne: tuple | None = None) -> None:
    """Écrit, et retient où le texte finit — un débordement doit être un échec, pas un regard.

    ⚠⚠ Une annotation qui sort de son panneau atterrit dans le panneau voisin et y ment : la
    note du panneau B se lisait comme un titre du panneau C. Le contrôle ne peut l'attraper que
    si le dessin dit ce qu'il a écrit et où.
    """
    art.text(xy, texte, fill=fill, font=font)
    if borne is not None:
        ANNOTATIONS.append((texte, xy[0] + font.getbbox(texte)[2], borne[0], borne[1]))


def _cadre(art, x0: int, y0: int, pw: int, ph: int, legende: str, petit) -> tuple:
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    if legende:
        ecrire(art, (x0 + 8, y0 + 6), legende, DISCRET, petit, (x0, x0 + pw))
    return x0 + 54, x0 + pw - 22, y0 + ph - 40, y0 + 32


def _abscisse(art, gauche: int, droite: int, base: int, n: int, petit, titre: str) -> None:
    art.line([gauche, base, droite, base], fill=TEXTE)
    for i in range(n):
        x = gauche + (droite - gauche) * i / max(1, n - 1)
        art.line([x, base, x, base + 3], fill=DISCRET)
        art.text((x - 4, base + 8), str(i + 1), fill=DISCRET, font=petit)
    art.text((gauche - 44, base + 8), titre, fill=DISCRET, font=petit)


def _log(bas: float, haut: float, base: int, sommet: int):
    """Une échelle logarithmique, parce que les erreurs vont de 17 à 1100 µm.

    ⚠ Une échelle linéaire écrase les six premiers bras contre l'axe et la figure ne montre
    plus que le trou du corpus au bras sept — c'est-à-dire justement pas le résultat.
    """
    import math  # noqa: PLC0415

    lb, lh = math.log10(bas), math.log10(haut)

    def py(val: float) -> float:
        return base - (base - sommet) * (math.log10(max(val, 1e-3)) - lb) / (lh - lb)

    graduations = [g for g in (20, 50, 100, 200, 500, 1000) if bas <= g <= haut]
    return py, graduations


def panneau_erreurs(art, x0, y0, pw, ph, m, petit) -> list[str]:
    """Les quatre courbes, la bande qui perd la marche, et la portée cerclée sur la courbe."""
    gauche, droite, base, sommet = _cadre(art, x0, y0, pw, ph, "", petit)
    n = len(m["spires_visees"])
    seuil = m["demi_feuille_um"]
    toutes = [v for x in m["lignes"] for v in x["erreurs_um"]] + [seuil]
    py, grad = _log(min(toutes) * 0.8, max(toutes) * 1.25, base, sommet)

    def px(i: float) -> float:
        return gauche + (droite - gauche) * i / max(1, n - 1)

    # ⚠⚠ LA BANDE DU SEUIL EST DESSINÉE, PAS ANNOTÉE : ce qui se lit d'un coup d'œil est
    # quelle courbe y entre et à quel bras, pas un nombre écrit en légende.
    art.rectangle([gauche - 10, sommet, droite + 10, py(seuil)], fill=PALE)
    art.line([gauche - 10, py(seuil), droite + 10, py(seuil)], fill=ROUGE)
    ecrire(art, (x0 + 8, y0 + 6), "au-dessus : plus pres de la MAUVAISE feuille",
           ROUGE, petit, (x0, x0 + pw))
    for g in grad:
        art.text((gauche - 46, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
        art.line([gauche - 4, py(g), gauche, py(g)], fill=DISCRET)
    art.text((gauche - 46, py(seuil) - 6), f"{seuil:>4.0f}", fill=ROUGE, font=petit)
    noms = []
    for x in m["lignes"]:
        if not x["erreurs_um"]:
            continue
        noms.append(MARQUE[x["marcheur"]])
        coul = COULEUR[x["marcheur"]]
        pts = [(px(i), py(v)) for i, v in enumerate(x["erreurs_um"])]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        # ⭐ LA PORTÉE EST CERCLÉE SUR LA COURBE, au premier bras qui échoue : c'est là que la
        # figure répond à la question du but, et un entier écrit en légende ne se voit pas.
        k = x["portee"]
        if k < len(pts):
            fx, fy = pts[k]
            art.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], outline=coul, width=2)
    _abscisse(art, gauche, droite, base, n, petit, "bras :")
    ecrire(art, (x0 + 8, y0 + ph - 18), "um", DISCRET, petit, (x0, x0 + pw))
    return noms


def panneau_corpus(art, x0, y0, pw, ph, m, petit) -> None:
    """Ce que chaque bras demande, mesure sur le corpus et sans aucun marcheur."""
    gauche, droite, base, sommet = _cadre(
        art, x0, y0, pw, ph, "mesure sur les spires publiees, aucun marcheur", petit)
    bras = m["bras_du_corpus"]
    nom, demi = m["pas_nominal_um"], m["demi_feuille_um"]
    vals = [b["ecart_um"] for b in bras] + [nom + demi]
    py, grad = _log(min(min(vals), nom - demi) * 0.7, max(vals) * 1.3, base, sommet)
    larg = (droite - gauche) / max(1, len(bras)) * 0.58
    art.rectangle([gauche - 10, py(nom + demi), droite + 10, py(max(1.0, nom - demi))],
                  fill=BLEU_PALE)
    art.line([gauche - 10, py(nom), droite + 10, py(nom)], fill=(90, 120, 150))
    for g in grad:
        art.text((gauche - 46, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
    for i, b in enumerate(bras):
        cx = gauche + (droite - gauche) * i / max(1, len(bras) - 1)
        coul = ROUGE if not b["au_pas_nominal"] else (100, 130, 160)
        art.rectangle([cx - larg / 2, py(b["ecart_um"]), cx + larg / 2, base], fill=coul)
        art.text((cx - 12, py(b["ecart_um"]) - 14), f"{b['ecart_um']:.0f}",
                 fill=coul if not b["au_pas_nominal"] else DISCRET, font=petit)
    ecrire(art, (x0 + 8, y0 + 20), f"bande bleue : {nom:.0f} um a une demi-feuille pres",
           (90, 120, 150), petit, (x0, x0 + pw))
    _abscisse(art, gauche, droite, base, len(bras), petit, "bras :")
    ecrire(art, (x0 + 8, y0 + ph - 18), "um", DISCRET, petit, (x0, x0 + pw))


def panneau_couverture(art, x0, y0, pw, ph, m, petit) -> None:
    """La couverture, une seule courbe parce que les quatre marcheurs gardent les memes."""
    gauche, droite, base, sommet = _cadre(
        art, x0, y0, pw, ph, "une cellule sortie du volume est perdue pour de bon", petit)
    serie = next(x["cellules_par_bras"] for x in m["lignes"] if x["deploye"])
    haut = max(serie) * 1.18

    def py(v: float) -> float:
        return base - (base - sommet) * v / haut

    pts = [(gauche + (droite - gauche) * i / max(1, len(serie) - 1), py(v))
           for i, v in enumerate(serie)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        art.polygon([(ax, ay), (bx, by), (bx, base), (ax, base)], fill=(232, 238, 233))
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        art.line([ax, ay, bx, by], fill=VERT, width=2)
    for cx, cy in pts:
        art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=VERT)
    art.text((pts[0][0] + 6, pts[0][1] + 4), str(serie[0]), fill=VERT, font=petit)
    art.text((pts[-1][0] - 30, pts[-1][1] - 16), str(serie[-1]), fill=VERT, font=petit)
    for v in (500, 1000, 1500):
        if v < haut:
            art.text((gauche - 46, py(v) - 6), f"{v:>4}", fill=DISCRET, font=petit)
    ecrire(art, (x0 + 8, y0 + 20), "chaque ecart apparie est pris sur les cellules",
           DISCRET, petit, (x0, x0 + pw))
    ecrire(art, (x0 + 8, y0 + 33), f"COMMUNES aux deux ; il en reste "
           f"{m['part_de_nappe_gardee']} au dernier bras", DISCRET, petit, (x0, x0 + pw))
    _abscisse(art, gauche, droite, base, len(serie), petit, "bras :")
    ecrire(art, (x0 + 8, y0 + ph - 18), "cellules", DISCRET, petit, (x0, x0 + pw))


def panneau_rugosite(art, x0, y0, pw, ph, m, petit) -> None:
    """De combien le champ de decalage s'ecarte de son propre voisinage, bras par bras.

    ⚠⚠ C'EST LA PRÉMISSE DU DIAGNOSTIC. « La marche froisse la surface qu'elle laisse » reste
    une histoire tant que ce nombre n'est pas mesuré ; s'il ne monte pas, l'explication tombe et
    il faut en chercher une autre.
    """
    gauche, droite, base, sommet = _cadre(
        art, x0, y0, pw, ph, "ecart median au voisinage, en voxels", petit)
    series = [(x["marcheur"], x["rugosites_vx"]) for x in m["lignes"]
              if any(g for g in x["rugosites_vx"])]
    toutes = [g for _, ser in series for g in ser if g]
    if not toutes:
        return
    haut = max(toutes) * 1.2
    n = len(m["spires_visees"])
    for nom, ser in series:
        coul = COULEUR[nom]
        pts = [(gauche + (droite - gauche) * i / max(1, n - 1),
                base - (base - sommet) * (g or 0.0) / haut) for i, g in enumerate(ser)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
    for g in (0.5, 1.0, 1.5, 2.0, 3.0):
        if g < haut:
            art.text((gauche - 46, base - (base - sommet) * g / haut - 6), f"{g:>4.1f}",
                     fill=DISCRET, font=petit)
    ecrire(art, (x0 + 8, y0 + 20), "le pas normal seul ne glisse pas, donc il est absent",
           DISCRET, petit, (x0, x0 + pw))
    _abscisse(art, gauche, droite, base, n, petit, "bras :")
    ecrire(art, (x0 + 8, y0 + ph - 18), "voxels", DISCRET, petit, (x0, x0 + pw))


def legende(art, x0: int, y: int, petit) -> None:
    """Qui est quelle couleur, dit une seule fois pour toute la figure.

    ⚠ Sans elle un lecteur voit quatre courbes et ne peut pas savoir laquelle est celle qui
    tourne — c'est-a-dire ne peut pas lire le resultat.
    """
    x = x0
    for nom in ("raccroche", "raccroche_lisse", "rien", "melange", "oracle"):
        art.rectangle([x, y + 3, x + 16, y + 9], fill=COULEUR[nom])
        art.text((x + 22, y), MARQUE[nom], fill=TEXTE, font=petit)
        x += 26 + petit.getbbox(MARQUE[nom])[2] + 24


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 34, 344, 22, 250
    largeur_utile = pw * 4 + ecart * 3
    for coupe in (150, 140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 110 + ph + 44 + len(lignes) * 19
    ANNOTATIONS.clear()
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Jusqu'ou la marche va avant d'etre plus pres de la mauvaise feuille",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"ancre : spire {m['ancre']} · {len(m['spires_visees'])} bras · seuil = "
             f"demi-feuille {m['demi_feuille_um']} um · le cercle marque la portee",
             fill=DISCRET, font=moyen)
    legende(art, marge, 62, petit)
    titres = ("A · l'erreur bras par bras et le seuil",
              "B · ce que chaque bras demande",
              "C · la couverture perdue en chemin",
              "D · le froissement du champ de decalage")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 86), t, fill=TEXTE, font=moyen)
    eta = panneau_erreurs(art, marge, 110, pw, ph, m, petit)
    panneau_corpus(art, marge + pw + ecart, 110, pw, ph, m, petit)
    panneau_couverture(art, marge + 2 * (pw + ecart), 110, pw, ph, m, petit)
    panneau_rugosite(art, marge + 3 * (pw + ecart), 110, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"marcheurs": len(m["lignes"]), "etiquettes": sorted(set(eta)),
            "annotations": list(ANNOTATIONS),
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes], "titres": titres,
            "largeur_utile": largeur_utile, "panneau": pw, "sortie": str(sortie)}


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
    v("la prose est traçable", prose_tracable(prose(m)))

    def par(nom: str) -> dict:
        return next(x for x in m["lignes"] if x["marcheur"] == nom)

    # ⚠⚠ LE SEUIL VIENT DE LA MATIÈRE, et la figure le dessine plutôt que de l'annoter.
    v("le seuil est la demi-feuille, dérivée du pas nominal",
      abs(m["demi_feuille_um"] - m["pas_nominal_um"] / 2) < 1e-6,
      f"{m['demi_feuille_um']} pour {m['pas_nominal_um']}")
    # ⚠⚠⚠ LA COMPARAISON PORTE SUR UNE SEULE POPULATION : si les marcheurs gardaient des
    # cellules différentes, une différence de médianes pourrait n'être qu'une différence de
    # qui est compté. La figure l'affirme dans sa prose, donc un contrôle le vérifie.
    # ⚠⚠⚠ DEUX MARCHEURS DIVERGENT, DONC LEURS MASQUES DIVERGENT : ce qui doit tenir n'est pas
    # l'égalité des couvertures mais que chaque écart apparié soit pris sur l'INTERSECTION, et
    # qu'il publie combien de cellules elle contient.
    v("chaque écart apparié publie les cellules communes sur lesquelles il est pris",
      all(m[c] and all(x > 0 for x in m[c])
          for c in ("cellules_communes_par_bras", "cellules_communes_lissage_raccrochage",
                    "cellules_communes_lissage_pas_normal")),
      str(m["cellules_communes_lissage_raccrochage"]))
    # ⚠⚠ ET UNE INTERSECTION NE PEUT PAS ÊTRE PLUS GRANDE QUE LE PLUS PETIT DES DEUX MASQUES.
    lis = par("raccroche_lisse")
    v("... et aucune intersection ne dépasse le plus petit des deux masques",
      all(c <= min(a, b) for c, a, b in zip(m["cellules_communes_lissage_raccrochage"],
                                            lis["cellules_par_bras"],
                                            par("raccroche")["cellules_par_bras"])))
    v("... et la couverture ne remonte jamais en chemin",
      all(all(b <= a for a, b in zip(x["cellules_par_bras"], x["cellules_par_bras"][1:]))
          for x in m["lignes"]),
      str(par("raccroche")["cellules_par_bras"]))
    # ⚠⚠⚠ LE PLANCHER EST UNE BORNE INFÉRIEURE : la distance à un nuage est 1-lipschitzienne.
    # S'il dépassait l'erreur d'un bras, la figure lirait un « irréductible » qui ne l'est pas.
    hors = [(x["marcheur"], b["bras"]) for x in m["lignes"] for b in x["bras"]
            if b["plancher_um"] > b["erreur_um"] + 1e-6]
    v("le plancher d'un bras ne dépasse jamais l'erreur mesurée sur ce bras", not hors,
      str(hors[:3]))
    # ⭐⭐⭐ LE RÉSULTAT QUE LA FIGURE PORTE, ET IL A DEUX MOITIÉS : la portée, et la marge.
    v("la portée du chemin déployé est publiée avec celles de ses trois témoins",
      all(isinstance(m[c], int) for c in ("portee_du_deploye", "portee_sans_rien_faire",
                                          "portee_du_temoin", "portee_de_loracle")),
      f"déployé {m['portee_du_deploye']} · rien {m['portee_sans_rien_faire']} · témoin "
      f"{m['portee_du_temoin']} · borne {m['portee_de_loracle']}")
    # ⚠⚠⚠ LA QUESTION EST POSÉE DANS LES DEUX SENS, avec le même instrument et sans seuil
    # ajouté : `tranche` répond « en faveur du premier », donc un faux ne veut pas dire « les
    # deux se valent ». Sans la moitié renversée, un raccrochage qui COÛTE se lirait comme un
    # raccrochage qui n'apporte rien — ce qui est un tout autre verdict.
    v("les deux sens de l'écart apparié sont publiés, et jamais vrais ensemble",
      m["ecart_du_pas_normal"] is not None
      and not (m["le_raccrochage_bat_le_pas_normal"] and m["le_pas_normal_bat_le_raccrochage"]),
      f"raccrochage {m['le_raccrochage_bat_le_pas_normal']} · "
      f"pas normal {m['le_pas_normal_bat_le_raccrochage']}")
    v("... et l'écart apparié bras par bras l'accompagne, avec son intervalle",
      m["ecart_au_pas_normal"] is not None
      and m["ecart_au_pas_normal"]["intervalle_um"] is not None,
      str(m["ecart_au_pas_normal"]))
    # ⚠⚠ LES DEUX VERDICTS DOIVENT DIRE LA MÊME CHOSE : une portée plus courte ET un écart
    # apparié positif sont deux lectures d'un seul fait. Si elles divergeaient, la figure
    # publierait un verdict que sa propre autre mesure contredit.
    e = m["ecart_au_pas_normal"]
    v("... la portée et l'écart apparié ne se contredisent pas",
      not (m["le_raccrochage_porte_plus_loin"] and e and e["ecart_median_um"] > 0
           and e["intervalle_um"][0] > 0),
      f"porte plus loin {m['le_raccrochage_porte_plus_loin']} · écart "
      f"{e['ecart_median_um'] if e else None}")
    # ⚠ CE QUE LE CORPUS DEMANDE EST DESSINÉ : sans le panneau B, un bras que la matière rend
    # impossible se lirait comme une méthode qui échoue.
    v("le corpus publie l'écart qu'il demande à chaque bras",
      len(m["bras_du_corpus"]) == len(m["spires_visees"]),
      str([b["ecart_um"] for b in m["bras_du_corpus"]]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les marcheurs sont dessinés", r["marcheurs"] == len(m["lignes"]),
          str(r["marcheurs"]))
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"]))
        _, _, pt_ = police(17, 13, 11)
        trop = [(t, pt_.getbbox(t)[2]) for t in r["titres"] if pt_.getbbox(t)[2] >= r["panneau"]]
        # ⚠⚠ UNE ANNOTATION QUI SORT DE SON PANNEAU ATTERRIT DANS LE VOISIN et s'y lit comme
        # une de ses légendes. Le contrôle porte sur ce que le dessin a réellement écrit.
        sortent = [(t[:34], int(fin - x1)) for t, fin, _, x1 in r["annotations"] if fin > x1 - 4]
        v("aucune annotation ne déborde de son panneau", not sortent and r["annotations"],
          str(sortent[:3]) if sortent else f"{len(r['annotations'])} annotations mesurées")
        v("chaque titre de panneau tient dans son panneau", not trop,
          str(trop) if trop else f"le plus large fait "
          f"{max(pt_.getbbox(t)[2] for t in r['titres'])} px pour {r['panneau']}")
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_la_portee_du_raccrochage.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    print(json.dumps(dessiner(json.loads(a.mesure.read_text()), a.sortie),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
