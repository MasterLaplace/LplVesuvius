#!/usr/bin/env python3
"""Le résidu entre les deux aplatissements : une translation, et non un champ.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « Une constante bat tous les champs » est une phrase qu'on
croit ou qu'on ne croit pas. La **surface** de l'AUC en fonction d'un décalage constant se
regarde : si elle a un sommet net à l'intérieur du balayage, il y a bien un déplacement à
retrancher, et il est unique. Si elle n'en a pas, la phrase est fausse.

⭐⭐ **Le témoin est dessiné à la MÊME échelle de couleur, à côté.** La carte d'encre mélangée
doit rendre une surface plate à 0,5 : sans elle, un relief sur la première se lit comme un
résultat alors qu'il pourrait n'être que la forme de l'empreinte.

⭐⭐⭐ **Et le panneau qui tranche est le troisième** : ce que chaque fenêtre préfère, dans le
même plan. Si les préférences se serrent autour d'un point, le résidu est une translation ; les
cercles des deux champs candidats montrent d'un coup qu'ils déplacent de plus que ce que les
fenêtres demandent — donc qu'ils inventent un champ au lieu d'en corriger un.

⚠ Tous les nombres sont LUS dans `docs/mesures/le_residu_est_une_translation.json`.

Usage :
    uv run python src/figures/figure_le_residu_est_une_translation.py --verifier
    uv run python src/figures/figure_le_residu_est_une_translation.py \\
        --sortie docs/images/75_le_residu_est_une_translation.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_commune import police, prose_tracable  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "le_residu_est_une_translation.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
ROUGE = (188, 68, 52)
VERT = (52, 122, 72)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)

CASE = 24


def rampe(t: float) -> tuple[int, int, int]:
    """Ardoise → crème → ambre, monotone en clarté puis en chaleur.

    ⚠ Monotone est la seule propriété qui compte, et elle est vérifiée : une rampe qui
    reviendrait sur ses pas ferait lire deux AUC différentes de la même couleur, ce qui est la
    façon la plus discrète pour une figure de mentir.
    """
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    if t < 0.5:
        u = t * 2.0
        a, b = (38, 58, 84), (248, 244, 236)
    else:
        u = (t - 0.5) * 2.0
        a, b = (248, 244, 236), (168, 92, 12)
    return tuple(int(round(a[k] + (b[k] - a[k]) * u)) for k in range(3))


def bornes(*balayages: dict) -> tuple[float, float]:
    """L'étendue commune des AUC — PARTAGÉE entre la surface et son témoin.

    ⚠⚠ Partagée et non recalculée par panneau : une échelle par panneau rendrait toute surface
    contrastée, y compris celle du témoin, et le témoin cesserait de contrôler quoi que ce soit.
    """
    v = [c["auc"] for b in balayages for c in b.get("grille", [])]
    return (min(v), max(v)) if v else (0.0, 1.0)


def _plan(art, x0: int, y0: int, portee: int, pas: int, petit, case: int = CASE) -> None:
    """Le cadre et les graduations d'un plan de décalages, en cases."""
    n = 2 * portee // pas + 1
    art.rectangle([x0, y0, x0 + n * case, y0 + n * case], outline=CADRE)
    for k in (0, n // 2, n - 1):
        art.text((x0 + k * case, y0 + n * case + 4), f"{-portee + k * pas:+d}",
                 fill=DISCRET, font=petit)
        art.text((x0 - 26, y0 + k * case), f"{-portee + k * pas:+d}", fill=DISCRET, font=petit)


def _point(portee: int, pas: int, di: float, dj: float,
           case: int = CASE) -> tuple[float, float]:
    """Un décalage placé dans le plan, en pixels depuis le coin du plan.

    ⚠ La taille de case est un paramètre parce que le témoin est balayé plus grossièrement : à
    case fixe son plan serait deux fois plus petit que celui qu'il contrôle, et deux plans de
    tailles différentes ne se comparent pas d'un coup d'œil — or c'est tout ce qu'on lui demande.
    """
    return ((dj + portee) / pas * case + case / 2.0,
            (di + portee) / pas * case + case / 2.0)


def couper(lignes: list[str], largeur: int = 108) -> list[str]:
    """La prose repliée à une largeur fixe — une ligne qui sort du cadre n'est pas lisible."""
    out = []
    for l in lignes:
        mots, cour = l.split(), ""
        for m in mots:
            if cour and len(cour) + 1 + len(m) > largeur:
                out.append(cour)
                cour = "    " + m
            else:
                cour = f"{cour} {m}" if cour else m
        if cour:
            out.append(cour)
    return out


def etendue(grille: list[dict], cle: str) -> float:
    """L'écart entre le meilleur et le pire point d'un plan.

    ⚠⚠⚠ C'EST CE QUI DIT SI UN PLAN ARBITRE OU NON. Un sommet ne veut rien dire tant qu'on ne
    sait pas de combien il dépasse : le témoin de la carte mélangée a lui aussi un maximum, et
    son plan est plat à deux millièmes. Comparer les étendues est donc la seule façon de dire
    qu'un plan est informatif — et de mesurer **à quel point** il l'est moins qu'un autre.
    """
    v = [c[cle] for c in grille]
    return (max(v) - min(v)) if v else 0.0


def prose(m: dict) -> list[str]:
    b = m["balayage"]["meilleur"]
    o = m["optimum_par_fenetre"]
    sl = m["accord_des_silhouettes"]
    g = m["accord_global"]
    return [
        f"sur {m['constantes_partout']['_fenetres']} fenetres de l'empreinte, un decalage "
        f"CONSTANT de ({b['di']}, {b['dj']}) cases — {o['translation_um']:.0f} um — porte l'AUC "
        f"mediane de {m['constantes_partout']['_auc_du_champ_nul']:.3f} a {b['auc']:.3f}.",
        f"sur l'empreinte ENTIERE le meme decalage porte l'accord publie de "
        f"{g['champ_nul']['auc']:.4f} a {g['optimum_des_fenetres']['auc']:.4f} : le 0,756 de "
        "reference mesurait aussi un recalage.",
        f"chaque fenetre prefere ({o['di_median']:.0f}, {o['dj_median']:.0f}) a "
        f"{o['dispersion_di']:.0f} et {o['dispersion_dj']:.0f} cases pres, quand les champs "
        f"candidats deplacent de {m['norme_mediane_des_bords']:.0f} et "
        f"{m['norme_mediane_des_reperes']:.0f}.",
        f"et les silhouettes ne voient PAS la meme chose : leur plan s'etend sur "
        f"{etendue(sl['grille'], 'dice'):.3f} de Dice quand celui de l'encre s'etend sur "
        f"{etendue(m['balayage']['grille'], 'auc'):.3f} d'AUC, et leur sommet est "
        f"({sl['meilleur']['di']:+d}, {sl['meilleur']['dj']:+d}), pas celui de l'encre.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    bal, tem = m["balayage"], m["temoin_carte_melangee"]
    sil, opt = m["accord_des_silhouettes"], m["optimum_par_fenetre"]
    lo, hi = bornes(bal, tem)
    portee, pas = bal["portee"], bal["pas"]
    n = 2 * portee // pas + 1
    plan = n * CASE
    tp, tps = tem["portee"], tem["pas"]
    tn = 2 * tp // tps + 1
    # ⚠ Le témoin est balayé plus grossièrement ; sa case est agrandie pour que son plan fasse la
    # MÊME taille que celui qu'il contrôle. Deux plans de tailles différentes ne se comparent pas
    # d'un coup d'œil, or c'est tout ce qu'on demande à un témoin.
    tcase = plan // tn

    marge = 44
    xg, xd = marge + 34, marge + 34 + plan + 150
    y1 = 108
    y2 = y1 + plan + 152
    lignes = couper(prose(m))
    L = xd + plan + marge + 34
    H = y2 + plan + 116 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le residu est une translation, pas un champ", fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"chaque plan : un decalage CONSTANT applique aux etiquettes, de {-portee:+d} a "
             f"{portee:+d} cases (1 case = {m['cellule_um']:.1f} um)", fill=DISCRET, font=moyen)
    art.text((marge, 62),
             f"A et C : AUC mediane de la carte publiee sur "
             f"{m['constantes_partout']['_fenetres']} fenetres de {m['cote']} cases — "
             f"B : Dice du masque recale sur l'empreinte entiere", fill=DISCRET, font=moyen)

    def surface(x0, y0, grille, cle, bas, haut, prt, ps, case=CASE):
        for c in grille:
            cx, cy = (c["dj"] + prt) // ps, (c["di"] + prt) // ps
            t = (c[cle] - bas) / max(1e-9, haut - bas)
            art.rectangle([x0 + cx * case, y0 + cy * case,
                           x0 + (cx + 1) * case - 1, y0 + (cy + 1) * case - 1], fill=rampe(t))
        _plan(art, x0, y0, prt, ps, petit, case)

    def croix(x0, y0, di, dj, coul, prt, ps):
        px, py = _point(prt, ps, di, dj)
        x, y = x0 + px, y0 + py
        art.ellipse([x - 5, y - 5, x + 5, y + 5], outline=coul, width=2)
        art.line([x - 8, y, x + 8, y], fill=coul)
        art.line([x, y - 8, x, y + 8], fill=coul)

    def legende(x0, y0, entrees):
        for k, (coul, texte) in enumerate(entrees):
            art.ellipse([x0, y0 + k * 16 + 3, x0 + 8, y0 + k * 16 + 11], outline=coul, width=2)
            art.text((x0 + 14, y0 + k * 16), texte, fill=DISCRET, font=petit)

    # --- A : l'encre ---
    art.text((xg, y1 - 20), "A. l'encre : AUC de la carte publiee", fill=TEXTE, font=moyen)
    surface(xg, y1, bal["grille"], "auc", lo, hi, portee, pas)
    reperes = (("l'affine publiee (0, 0)", (0.0, 0.0), ROUGE),
               ("constante des bords", tuple(m["constante_des_bords"]), BLEU),
               ("constante des reperes", tuple(m["constante_des_reperes"]), VERT),
               ("optimum sur l'encre", (bal["meilleur"]["di"], bal["meilleur"]["dj"]), AMBRE))
    for _, (di, dj), coul in reperes:
        croix(xg, y1, di, dj, coul, portee, pas)
    legende(xg, y1 + plan + 26, [(c, nom) for nom, _, c in reperes])

    # --- B : les silhouettes, dans le MÊME plan ---
    art.text((xd, y1 - 20), "B. les silhouettes : Dice du masque recale", fill=TEXTE, font=moyen)
    sd = [c["dice"] for c in sil["grille"]]
    surface(xd, y1, sil["grille"], "dice", min(sd), max(sd), sil["portee"], sil["pas"])
    croix(xd, y1, 0.0, 0.0, ROUGE, sil["portee"], sil["pas"])
    croix(xd, y1, sil["meilleur"]["di"], sil["meilleur"]["dj"], AMBRE, sil["portee"], sil["pas"])
    croix(xd, y1, bal["meilleur"]["di"], bal["meilleur"]["dj"], BLEU, sil["portee"], sil["pas"])
    legende(xd, y1 + plan + 26,
            [(ROUGE, "l'affine publiee (0, 0)"),
             (AMBRE, f"optimum des silhouettes ({sil['meilleur']['di']:+d}, "
                     f"{sil['meilleur']['dj']:+d}) — Dice {sil['meilleur']['dice']:.4f}"),
             (BLEU, f"optimum de l'ENCRE, reporte ici ({bal['meilleur']['di']:+d}, "
                    f"{bal['meilleur']['dj']:+d})")])
    art.text((xd, y1 + plan + 78),
             f"etendue {etendue(sil['grille'], 'dice'):.4f} de Dice contre "
             f"{etendue(bal['grille'], 'auc'):.4f} d'AUC en A :", fill=DISCRET, font=petit)
    art.text((xd, y1 + plan + 92),
             "les deux arbitrent, l'encre bien plus fort, et pas", fill=DISCRET, font=petit)
    art.text((xd, y1 + plan + 106),
             "vers le meme point — echelle propre au Dice", fill=DISCRET, font=petit)

    # --- C : le témoin ---
    art.text((xg, y2 - 20), "C. temoin : la meme carte, valeurs melangees",
             fill=TEXTE, font=moyen)
    surface(xg, y2, tem["grille"], "auc", lo, hi, tp, tps, tcase)
    art.text((xg, y2 + plan + 26),
             f"plat a {tem['meilleur']['auc']:.3f} au mieux, etendue "
             f"{etendue(tem['grille'], 'auc'):.4f} — meme echelle que A",
             fill=DISCRET, font=petit)
    bx, by = xg, y2 + plan + 48
    for k in range(140):
        art.line([bx + k, by, bx + k, by + 11], fill=rampe(k / 139.0))
    art.text((bx, by + 14), f"{lo:.2f}", fill=DISCRET, font=petit)
    art.text((bx + 112, by + 14), f"{hi:.2f}", fill=DISCRET, font=petit)
    art.text((bx, by + 30), "AUC, echelle commune a A et C", fill=DISCRET, font=petit)

    # --- D : ce que chaque fenêtre préfère ---
    art.text((xd, y2 - 20), "D. ce que chaque fenetre prefere", fill=TEXTE, font=moyen)
    # ⚠⚠ Le panneau est dessiné à part puis collé : les cercles d'amplitude dépassent le plan
    # (60 cases contre 48 de portée), et un cercle qui déborde sur le panneau voisin se lit comme
    # une figure ratée. Le découpage est la mesure — ce qui sort du cadre n'a pas de sens.
    vue = Image.new("RGB", (plan, plan), FOND)
    va = ImageDraw.Draw(vue)
    comptes: dict[tuple[int, int], int] = {}
    for e in opt["optima"]:
        comptes[(e["di"], e["dj"])] = comptes.get((e["di"], e["dj"]), 0) + 1
    mx, my = _point(portee, pas, opt["di_median"], opt["dj_median"])
    disp = (opt["dispersion_di"] ** 2 + opt["dispersion_dj"] ** 2) ** 0.5
    cercles = ((disp, AMBRE, "dispersion des fenetres"),
               (m["norme_mediane_des_reperes"], VERT, "amplitude du champ des reperes"),
               (m["norme_mediane_des_bords"], BLEU, "amplitude du champ de bord"))
    for rayon, coul, _ in cercles:
        rp = rayon / pas * CASE
        va.ellipse([mx - rp, my - rp, mx + rp, my + rp], outline=coul, width=2)
    for (di, dj), k in comptes.items():
        px, py = _point(portee, pas, di, dj)
        r = 2.0 + 2.2 * (k ** 0.5)
        va.ellipse([px - r, py - r, px + r, py + r], fill=DISCRET)
    toile.paste(vue, (xd, y2))
    _plan(art, xd, y2, portee, pas, petit)
    art.text((xd, y2 + plan + 26),
             f"medianes ({opt['di_median']:.0f}, {opt['dj_median']:.0f}) ; "
             f"{opt['optima_au_bord']} sur {opt['fenetres']} touchent le bord",
             fill=DISCRET, font=petit)
    legende(xd, y2 + plan + 46,
            [(c, f"{nom} : {r:.0f} cases") for r, c, nom in cercles])

    bas = H - len(lignes) * 19 - 16
    for j, l in enumerate(lignes):
        art.text((marge, bas + j * 19), l, fill=TEXTE, font=moyen)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠ Rendu et non affirmé : la figure existe pour montrer que la dispersion est PLUS PETITE
    # que l'amplitude des champs, et que les deux plans n'ont pas le même sommet. Les deux faits
    # sont donc comptables ici, pas seulement dessinés.
    return {"cellules": len(bal["grille"]), "temoin": len(tem["grille"]),
            "silhouettes": len(sil["grille"]), "dispersion": round(disp, 2),
            "etendue_encre": round(etendue(bal["grille"], "auc"), 5),
            "etendue_silhouettes": round(etendue(sil["grille"], "dice"), 5),
            "etendue_temoin": round(etendue(tem["grille"], "auc"), 5),
            "sommets_distincts": bool((sil["meilleur"]["di"], sil["meilleur"]["dj"])
                                      != (bal["meilleur"]["di"], bal["meilleur"]["dj"])),
            "sous_les_deux_champs": bool(disp < m["norme_mediane_des_bords"]
                                         and disp < m["norme_mediane_des_reperes"]),
            "sortie": str(sortie)}


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ La rampe doit être monotone en LUMINANCE ou en chaleur, sans revenir sur ses pas : deux
    # AUC différentes de la même couleur, c'est une figure qui ment sans qu'on le voie.
    couleurs = [rampe(k / 40.0) for k in range(41)]
    croissante = all(sum(couleurs[k + 1]) >= sum(couleurs[k]) - 1 for k in range(20))
    chaude = all(couleurs[k + 1][0] - couleurs[k + 1][2]
                 >= couleurs[k][0] - couleurs[k][2] - 1 for k in range(20, 40))
    v("la rampe s'éclaircit puis se réchauffe, sans revenir", croissante and chaude)
    v("... et elle est bornée aux extrêmes", rampe(-5.0) == rampe(0.0)
      and rampe(5.0) == rampe(1.0))

    a = {"grille": [{"di": 0, "dj": 0, "auc": 0.4}, {"di": 8, "dj": 0, "auc": 0.9}]}
    b = {"grille": [{"di": 0, "dj": 0, "auc": 0.5}]}
    v("les bornes sont prises sur les DEUX plans", bornes(a, b) == (0.4, 0.9), str(bornes(a, b)))
    # ⚠⚠ Le contrôle qui rend l'échelle commune vérifiable : le témoin seul aurait une étendue
    # nulle, donc un panneau saturé — et il paraîtrait aussi contrasté que la vraie surface.
    v("... et le témoin seul aurait une étendue nulle", bornes(b) == (0.5, 0.5))

    v("un décalage se place au centre de sa case",
      _point(48, 8, -48, -48) == (CASE / 2.0, CASE / 2.0)
      and _point(48, 8, 0, 0) == (6 * CASE + CASE / 2.0, 6 * CASE + CASE / 2.0))

    if not MESURE.is_file():
        print(f"  ⚠ mesure absente ({MESURE.name}) : contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        bal = m["balayage"]
        n = 2 * bal["portee"] // bal["pas"] + 1
        v("la surface porte toutes ses cases", r["cellules"] == n * n,
          f"{r['cellules']} pour {n}×{n}")
        # ⚠⚠⚠ LE CONTRÔLE QUI VÉRIFIE QUE LE MARQUEUR EST AU BON ENDROIT : l'optimum dessiné
        # doit être la case de la grille où l'AUC est maximale. Un marqueur placé ailleurs
        # raconterait une autre mesure que celle qui est peinte sous lui.
        meilleure = max(bal["grille"], key=lambda c: c["auc"])
        v("le marqueur de l'optimum est sur la case la plus haute",
          (meilleure["di"], meilleure["dj"]) == (bal["meilleur"]["di"], bal["meilleur"]["dj"]),
          f"{(meilleure['di'], meilleure['dj'])} contre "
          f"{(bal['meilleur']['di'], bal['meilleur']['dj'])}")
        v("le témoin est dessiné, pas raconté", r["temoin"] > 0, str(r["temoin"]))
        v("le plan des silhouettes est dessiné, pas raconté",
          r["silhouettes"] == len(m["accord_des_silhouettes"]["grille"]), str(r["silhouettes"]))
        # ⚠⚠ La figure existe pour opposer les deux plans : si leurs sommets coïncidaient, elle
        # dirait le contraire de ce que sa prose annonce. Le fait est donc rendu et asserté ici
        # dans le sens que la mesure a trouvé, pas supposé.
        v("les deux plans ont bien des sommets distincts, comme la prose le dit",
          r["sommets_distincts"],
          f"encre {(m['balayage']['meilleur']['di'], m['balayage']['meilleur']['dj'])} "
          f"silhouettes {(m['accord_des_silhouettes']['meilleur']['di'], m['accord_des_silhouettes']['meilleur']['dj'])}")
        # ⚠⚠⚠ ET SANS CE CONTRÔLE, LE PRÉCÉDENT PASSERAIT POUR LA MAUVAISE RAISON. Un plan plat
        # a lui aussi un sommet — le témoin mélangé en a un — donc « les sommets diffèrent » ne
        # vaut que si les deux plans arbitrent réellement. Les trois étendues sont donc
        # comparées : celle du témoin est le plancher de bruit, et les deux autres doivent le
        # dépasser franchement.
        v("le témoin est plat, et c'est lui qui donne le plancher de bruit",
          r["etendue_temoin"] < 0.01, str(r["etendue_temoin"]))
        v("... les deux plans utiles le dépassent, donc ils arbitrent",
          r["etendue_silhouettes"] > 5.0 * r["etendue_temoin"]
          and r["etendue_encre"] > 5.0 * r["etendue_temoin"],
          f"silhouettes {r['etendue_silhouettes']}, encre {r['etendue_encre']}, "
          f"temoin {r['etendue_temoin']}")
        v("... et l'encre arbitre bien mieux que les silhouettes, comme la prose le dit",
          r["etendue_encre"] > 5.0 * r["etendue_silhouettes"],
          f"{r['etendue_encre']} contre {r['etendue_silhouettes']}")
        v("la dispersion des fenêtres est sous les deux amplitudes de champ",
          r["sous_les_deux_champs"],
          f"{r['dispersion']} contre {m['norme_mediane_des_bords']} et "
          f"{m['norme_mediane_des_reperes']}")
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png").convert("L")
        gris = img.getextrema()
        v("l'image a du relief, elle n'est ni blanche ni noire",
          gris[0] < 90 and gris[1] > 240, str(gris))

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_residu_est_une_translation.png")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.mesure.is_file():
        raise SystemExit(f"mesure absente : {a.mesure}")
    r = dessiner(json.loads(a.mesure.read_text()), a.sortie)
    print(f"écrit : {r['sortie']}  ({r['cellules']} cases, dispersion {r['dispersion']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
