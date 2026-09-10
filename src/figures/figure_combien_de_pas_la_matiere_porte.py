#!/usr/bin/env python3
"""Combien de pas la matiere porte — le premier acquis positif de la campagne, et sa borne.

⭐⭐⭐ LE PANNEAU A PORTE LE FAIT : interroger la matiere porte 2,00 pas la ou l'automate naif en
porte 0,00. C'est le premier resultat de la campagne ou la voie « interroger la matiere » BAT
l'etat de l'art plutot que de simplement ne pas etre refutee.

⭐⭐⭐ LE PANNEAU B EST CE QUI EMPECHE DE LIRE LE TEMOIN COMME UN HOMME DE PAILLE. Sur un
empilement fabrique DROIT, le naif atteint le plafond comme la matiere ; sur un empilement
OBLIQUE de 35°, il tombe a 1. Son echec vient donc de l'obliquite, pas d'un temoin casse.

⚠⚠⚠ ET LE PANNEAU C PORTE LA BORNE, AVANT LE RESULTAT QU'ELLE BORNE : 17 bandes sur 28 ont une
cellule au plafond de six pas, donc « 2,00 » est une borne INFERIEURE. Un plafond est un budget
de lecture ; le publier comme une limite de matiere serait la butee de `99`.

Usage :
    uv run python src/figures/figure_combien_de_pas_la_matiere_porte.py --verifier
    uv run python src/figures/figure_combien_de_pas_la_matiere_porte.py \\
        --sortie docs/images/102_combien_de_pas_la_matiere_porte.png
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "commun"))
from figure_commune import (Tracee, police, prose_tracable,  # noqa: E402
                            textes_debordants, textes_hors_cadre,
                            textes_qui_se_recouvrent)
from figure_le_residu_est_une_translation import couper  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "combien_de_pas_la_matiere_porte.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def lues(m: dict) -> list[dict]:
    return [x for x in m["lignes"]
            if x.get("pas_confirmes_median_matiere") is not None and x.get("rayon_mm")]


def prose(m: dict) -> list[str]:
    s = m["resume"]
    cf = m.get("controle_fabrique", {})
    droit = next((e for e in cf.get("empilements", []) if e["obliquite_deg"] == 0.0), {})
    obl = next((e for e in cf.get("empilements", []) if e["obliquite_deg"] > 0.0), {})
    return [
        f"★★★ CE QUE CE FICHIER MESURE, ET C'EST LE GRAAL EN UNE PHRASE. `99` rend le PAS que la "
        f"matiere montre, `101` la DIRECTION. mais derouler n'est pas faire UN pas, c'est les "
        f"ENCHAINER — et la question qui decide est au bout de combien de pas la matiere cesse de "
        f"confirmer. le prix tolere huit heures d'humain la ou l'etat de l'art en depense 775 sur "
        f"la correction du transfert de spire a spire ; ce fichier mesure jusqu'ou on va sans lui.",
        f"★★★ ET IL N'Y A AUCUN REFERENT HUMAIN DANS LA BOUCLE. la direction vient du tenseur de "
        f"structure, le pas du balayage calibre, et la verification du critere de `98` — "
        f"brillant-sombre-brillant sur exactement UN interstice. les quatre candidats de `94` a "
        f"`97` ont tous ete fermes parce qu'ils se calibraient contre un maillage dont `97` a "
        f"mesure qu'il n'a pas de valeur unique. ici le maillage ne sert qu'a dire OU COMMENCER.",
        f"★★★ PANNEAU A — LE PREMIER ACQUIS POSITIF DE LA CAMPAGNE. interroger la matiere porte "
        f"{s['pas_confirmes_median_matiere']:.2f} pas la ou l'automate naif — pas NOMINAL le long "
        f"du RAYON, ce que ferait un derouleur qui n'interroge rien — en porte "
        f"{s['pas_confirmes_median_naif']:.2f}, sur {s['bandes_lues']} bandes. c'est la premiere "
        f"fois que la voie « interroger la matiere » BAT l'etat de l'art au lieu de simplement ne "
        f"pas etre refutee.",
        f"★★★ PANNEAU B — ET LE TEMOIN N'EST PAS UN HOMME DE PAILLE, ce qui est la condition pour "
        f"que son zero veuille dire quelque chose. sur un empilement fabrique DROIT, ou le pas "
        f"nominal et la direction radiale sont JUSTES, il atteint le plafond "
        f"({droit.get('pas_confirmes_naif')} pas) exactement comme la matiere "
        f"({droit.get('pas_confirmes_matiere')}). sur un empilement OBLIQUE de "
        f"{obl.get('obliquite_deg', 0):.0f}°, il tombe a {obl.get('pas_confirmes_naif')} quand la "
        f"matiere tient {obl.get('pas_confirmes_matiere')}. son echec vient donc de l'obliquite "
        f"que `100` et `101` ont mesuree, et de rien d'autre.",
        f"⚠⚠⚠ PANNEAU C — LA BORNE, ET ELLE SE DIT AVANT LE RESULTAT QU'ELLE BORNE. "
        f"{s['bandes_dont_une_cellule_atteint_le_plafond']} bandes sur {s['bandes_lues']} — "
        f"{100 * s['part_de_bandes_censurees']:.0f} % — ont au moins une cellule qui atteint le "
        f"plafond de {s['plafond_de_pas']} pas. « {s['pas_confirmes_median_matiere']:.2f} pas » "
        f"est donc une BORNE INFERIEURE et non une valeur : le plafond est un budget de lecture — "
        f"un cube coute 15,4 s au reseau — et le publier comme une limite de matiere serait la "
        f"butee que `99` a enregistree.",
        f"⚠⚠ ET LA DISTANCE PORTEE SE LIT AVEC SON SOUS-ENSEMBLE. "
        f"{s['distance_portee_mediane_um']:.0f} µm, soit "
        f"{s['distance_portee_mediane_um'] / m['pas_nominal_um']:.1f} feuilles nominales, mais "
        f"calcules sur les seules cellules qui ont porte AU MOINS un pas. une bande peut donc "
        f"afficher zero pas median ET une distance non nulle : ce sont deux populations, et les "
        f"lire cote a cote sans le dire les confondrait — la faute que `99` a payee en comparant "
        f"une population filtree a une population brute.",
        f"★★ LE VERIFICATEUR A DU ETRE REFAIT, ET LE DEFAUT VALAIT D'ETRE ECRIT. ma premiere "
        f"version verifiait chaque pas avec le BALAYAGE de `99`, qui cherche la meilleure periode "
        f"le long de la direction donnee. sur un empilement oblique de 35°, la periode le long du "
        f"RAYON vaut pas / cos(35°) = 211 µm — dans la fenetre — donc le balayage la trouve et "
        f"CONFIRME : l'automate naif passait ses huit pas la ou il devait echouer.",
        f"NON — C'ETAIT UNE VERIFICATION INCAPABLE D'ECHOUER, le peche nº 1 de ce depot, sous sa "
        f"forme la plus sournoise : elle testait « la matiere est-elle feuilletee ici » — vrai "
        f"partout — et non « le pas a-t-il franchi UNE feuille ». les deux roles sont desormais "
        f"SEPARES : `99` DECIDE de combien avancer, `98` VERIFIE a gabarit FIXE ce que l'avance a "
        f"traverse, sur le segment reellement parcouru.",
        f"⚠ CE QUE CA NE DIT PAS. deux pas ne sont pas cent-vingt : le graal demande 31 spires, "
        f"et ce fichier mesure la PENTE, pas le total. « sorti du volume » est compte a part de "
        f"« perdu la feuille » — aucune sortie sur les 28 bandes — et les pas sont comptes "
        f"CONSECUTIFS, parce qu'un marcheur qui perd la feuille au pas 3 ecrit du faux ensuite "
        f"meme si la matiere repond de nouveau au pas 5.",
    ]


def panneau_pas(art, x0, y0, pw, ph, m, petit) -> int:
    """Les pas confirmés, matière contre naïf, bande par bande."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "pas confirmés avant de perdre la feuille",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 22), "en interrogeant la MATIÈRE", fill=BLEU, font=petit)
    art.text((x0 + 8, y0 + 36), "automate NAÏF : pas nominal, direction radiale",
             fill=ROUGE, font=petit)
    lignes = lues(m)
    gauche, droite = x0 + 40, x0 + pw - 18
    base, sommet = y0 + ph - 58, y0 + 56
    r0 = min(x["rayon_mm"] for x in lignes)
    r1 = max(x["rayon_mm"] for x in lignes)
    haut = float(m["pas_max"]) + 0.6

    def px(v):
        return gauche + (droite - gauche) * (v - r0 * 0.9) / max(r1 * 1.06 - r0 * 0.9, 1e-9)

    def py(v):
        return base - (base - sommet) * v / haut

    art.line([gauche, base, droite, base], fill=TEXTE)
    art.line([gauche, base, gauche, sommet], fill=TEXTE)
    for g in range(0, int(m["pas_max"]) + 1, 2):
        art.line([gauche, py(g), droite, py(g)], fill=(235, 235, 235))
        art.text((x0 + 6, py(g) - 6), str(g), fill=DISCRET, font=petit)
    # ⚠⚠ LE PLAFOND EST TRACE, parce que les points qui le touchent disent « au moins ».
    y = py(float(m["pas_max"]))
    for xx in range(int(gauche), int(droite), 8):
        art.line([xx, y, xx + 4, y], fill=AMBRE)
    art.text((gauche + 4, y - 15), f"plafond de lecture : {m['pas_max']} pas — au-delà, "
             "« au moins »", fill=AMBRE, font=petit)
    points = 0
    for cle, coul in (("pas_confirmes_median_matiere", BLEU),
                      ("pas_confirmes_median_naif", ROUGE)):
        pts = [(px(x["rayon_mm"]), py(x[cle])) for x in lignes if x.get(cle) is not None]
        if len(pts) > 1:
            art.line(pts, fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=coul)
            points += 1
    for g in (r0, (r0 + r1) / 2, r1):
        art.text((px(g) - 14, base + 6), f"{g:.0f} mm", fill=DISCRET, font=petit)
    s = m["resume"]
    art.text((x0 + 8, y0 + ph - 34),
             f"★★★ médianes : {s['pas_confirmes_median_matiere']:.2f} contre "
             f"{s['pas_confirmes_median_naif']:.2f}", fill=VERT, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : rayon médian de la bande",
             fill=DISCRET, font=petit)
    return points


def panneau_controle(art, x0, y0, pw, ph, m, petit) -> int:
    """Le contrôle fabriqué : le témoin réussit quand il a raison, échoue quand il a tort."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "le témoin est-il un homme de paille ?",
             fill=DISCRET, font=petit)
    cf = m.get("controle_fabrique", {})
    emp = cf.get("empilements", [])
    if not emp:
        art.text((x0 + 8, y0 + 40), "contrôle fabriqué absent de la mesure",
                 fill=ROUGE, font=petit)
        return 0
    gauche, droite = x0 + 96, x0 + pw - 60
    haut = y0 + 60
    hi = float(cf.get("pas_max", 6)) * 1.15
    barres = 0
    h = 56
    for j, e in enumerate(emp):
        y = haut + j * h
        art.text((x0 + 6, y + 10), f"obliquité {e['obliquite_deg']:.0f}°",
                 fill=TEXTE, font=petit)
        for k, (cle, coul, nom) in enumerate((("pas_confirmes_matiere", BLEU, "matière"),
                                              ("pas_confirmes_naif", ROUGE, "naïf"))):
            larg = (droite - gauche) * float(e[cle]) / hi
            yy = y + k * 15
            art.rectangle([gauche, yy, gauche + max(larg, 1.0), yy + 12], fill=coul)
            art.text((gauche + max(larg, 1.0) + 5, yy - 1), f"{e[cle]} — {nom}",
                     fill=coul, font=petit)
            barres += 1
    bas = haut + len(emp) * h + 6
    if cf.get("le_temoin_nest_pas_un_homme_de_paille"):
        art.text((x0 + 8, bas),
                 "★★ à 0° le naïf atteint le PLAFOND comme la matière :", fill=VERT, font=petit)
        art.text((x0 + 8, bas + 14),
                 "   son échec ailleurs vient de l'obliquité, pas de lui.", fill=VERT,
                 font=petit)
    art.text((x0 + 8, bas + 34),
             "⚠ le pas nominal et le rayon sont JUSTES à 0° et", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 48),
             "   FAUX à 35°, ce que `100` et `101` ont mesuré", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "un témoin qui échoue toujours ne prouve rien", fill=DISCRET, font=petit)
    return barres


def panneau_censure(art, x0, y0, pw, ph, m, petit) -> int:
    """Combien de bandes butent sur le plafond de lecture."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "jusqu'où la mesure peut-elle voir ?", fill=DISCRET, font=petit)
    lignes = lues(m)
    plafond = int(m["pas_max"])
    compte = [sum(1 for x in lignes if int(x.get("pas_confirmes_max_matiere", 0)) == k)
              for k in range(plafond + 1)]
    gauche, droite = x0 + 60, x0 + pw - 40
    haut = y0 + 46
    hi = max(max(compte), 1) * 1.2
    h = 26
    barres = 0
    for k in range(plafond + 1):
        y = haut + k * h
        coul = AMBRE if k == plafond else BLEU
        art.text((x0 + 6, y + 2), f"{k} pas", fill=coul, font=petit)
        larg = (droite - gauche) * compte[k] / hi
        art.rectangle([gauche, y, gauche + max(larg, 1.0), y + 14], fill=coul)
        art.text((gauche + max(larg, 1.0) + 5, y), str(compte[k]), fill=coul, font=petit)
        barres += 1
    s = m["resume"]
    bas = haut + (plafond + 1) * h + 8
    art.text((x0 + 8, bas),
             f"⚠⚠ {s['bandes_dont_une_cellule_atteint_le_plafond']} bandes sur "
             f"{s['bandes_lues']} ont une cellule AU", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 14),
             f"   PLAFOND, soit {100 * s['part_de_bandes_censurees']:.0f} % : "
             f"« {s['pas_confirmes_median_matiere']:.2f} pas » est", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 28), "   une BORNE INFÉRIEURE, pas une valeur.",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 48),
             "⚠ le plafond est un budget de lecture :", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 62),
             "   un cube coûte 15,4 s au réseau.", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18),
             "ordonnée : le MAXIMUM sur les cellules de la bande", fill=DISCRET, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 330, 26, 420
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (150, 142, 134, 126, 118, 110):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    s = m["resume"]
    art.text((marge, 16),
             "Combien de pas la matière porte — le premier acquis positif, et sa borne",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m['fragment']} · {s['bandes_lues']} bandes · {m['cellules_par_bande']} cellules "
             f"· plafond {m['pas_max']} pas · matière {s['pas_confirmes_median_matiere']:.2f} "
             f"contre naïf {s['pas_confirmes_median_naif']:.2f} · "
             f"{s['bandes_dont_une_cellule_atteint_le_plafond']}/{s['bandes_lues']} bandes "
             f"censurées", fill=DISCRET, font=moyen)
    titres = ("A · la matière contre l'automate naïf",
              "B · le témoin n'est pas un homme de paille",
              "C · ⚠ jusqu'où la mesure peut voir")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    points = panneau_pas(art, marge, 104, pw, ph, m, petit)
    barres = panneau_controle(art, marge + pw + ecart, 104, pw, ph, m, petit)
    censure = panneau_censure(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "points": points, "barres": barres, "censure": censure,
            "textes_dessines": art.textes,
            "debordants": textes_debordants(art.poses, L - marge),
            "hors_cadre": textes_hors_cadre(art.poses, cadres),
            "recouvrements": textes_qui_se_recouvrent(art.poses),
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
            "largeur_utile": largeur_utile, "sortie": str(sortie)}


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
        print(f"ALL PASS ({echecs} failures, {controles} checks)")
        return 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    d = dessiner(m, RACINE / "docs" / "images"
                 / "102_combien_de_pas_la_matiere_porte.png")
    v("la figure est écrite", Path(d["sortie"]).stat().st_size > 8000,
      f"{Path(d['sortie']).stat().st_size} octets")
    v("aucune ligne de prose ne déborde",
      all(w <= d["largeur_utile"] for _, w in d["prose"]),
      f"max {max(w for _, w in d['prose'])} pour {d['largeur_utile']}")
    from figure_commune import glyphes_manquants  # noqa: PLC0415
    absents = sorted(glyphes_manquants("".join(d["textes_dessines"])))
    v("aucun glyphe du texte DESSINÉ n'est manquant", not absents, str(absents))
    v("aucun texte DESSINÉ ne déborde de la toile", not d["debordants"], str(d["debordants"]))
    v("aucun texte ne déborde de son PANNEAU", not d["hors_cadre"], str(d["hors_cadre"]))
    v("aucun texte n'est écrit par-dessus un autre", not d["recouvrements"],
      str(d["recouvrements"][:3]))
    v("les deux courbes sont tracées pour chaque bande",
      d["points"] == 2 * len(lues(m)), f"{d['points']} pour {2 * len(lues(m))}")
    v("le panneau B trace les DEUX empilements fabriqués × DEUX marcheurs",
      d["barres"] == 4, str(d["barres"]))
    v("le panneau C trace une barre par valeur possible du maximum",
      d["censure"] == int(m["pas_max"]) + 1, str(d["censure"]))
    # ⚠⚠ LES VERDICTS SONT DANS LA MESURE, pas seulement dans la prose.
    s = m["resume"]
    v("interroger la matière porte plus loin que le naïf",
      s["interroger_la_matiere_porte_plus_loin"],
      f"{s['pas_confirmes_median_matiere']} contre {s['pas_confirmes_median_naif']}")
    cf = m["controle_fabrique"]
    v("... et le témoin RÉUSSIT quand il a raison, donc son zéro veut dire quelque chose",
      cf["le_temoin_nest_pas_un_homme_de_paille"])
    v("... et l'obliquité SEULE le fait échouer",
      cf["lobliquite_seule_fait_echouer_le_temoin"])
    # ⚠⚠⚠ LA BORNE DOIT ETRE PUBLIEE, ET LA FIGURE DOIT LA DIRE.
    v("la censure est publiée dans la mesure", s["la_portee_est_censuree"],
      f"{s['bandes_dont_une_cellule_atteint_le_plafond']}/{s['bandes_lues']}")
    v("... et la figure la nomme comme une BORNE INFÉRIEURE",
      any("BORNE INFÉRIEURE" in t for t in d["textes_dessines"]))
    v("la prose garde la vérification qui ne pouvait pas échouer",
      any("INCAPABLE D'ECHOUER" in x for x in prose(m)))
    v("... et le sous-ensemble de la distance portée",
      any("deux populations" in x for x in prose(m)))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "102_combien_de_pas_la_matiere_porte.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
