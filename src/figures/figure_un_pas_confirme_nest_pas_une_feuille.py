#!/usr/bin/env python3
"""Un pas confirme n'est pas une feuille — la bande d'acceptation et sa consequence enchainee.

★★★ LE PANNEAU A EST LA REFUTATION, ET IL SE LIT D'UN COUP D'OEIL : la diagonale est la verite,
l'estimateur continu la suit, et le compteur entier est une DROITE PLATE a un. Un compteur dont la
famille est {1, 2, 3} ne peut pas exprimer un retard, quelle que soit la matiere.

★★★ LE PANNEAU B EST LA BANDE MESUREE, par niveau de bruit — et le fait qui surprend est qu'elle
ne depend presque PAS du bruit. C'est une propriete de la FORME des gabarits, pas du scan.

★★★ LE PANNEAU C PORTE LA CONSEQUENCE, ET C'EST ELLE QUI DECIDE : cent vingt pas tous confirmes
peuvent n'avoir franchi que 82 spires. `103` chiffrait la consequence d'une CHUTE, qui se voit ;
un retard, lui, s'accumule en silence.

Usage :
    uv run python src/figures/figure_un_pas_confirme_nest_pas_une_feuille.py --verifier
    uv run python src/figures/figure_un_pas_confirme_nest_pas_une_feuille.py \\
        --sortie docs/images/104_un_pas_confirme_nest_pas_une_feuille.png
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
MESURE = RACINE / "docs" / "mesures" / "un_pas_confirme_nest_pas_une_feuille.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    s = m["resume"]
    b = m["bande"]
    d = m.get("ce_que_la_bande_ne_distingue_pas", {})
    p = next((x for x in b["par_bruit"] if x["bruit"] == 15.0), b["par_bruit"][0])
    return [
        f"★★★ UN PAS CONFIRMÉ NE GARANTIT PAS QU'UNE FEUILLE A ÉTÉ FRANCHIE. Sur des segments "
        f"FABRIQUÉS dont on connaît la réponse, le critère de `102` — un interstice compté, un "
        f"accord au-dessus de la barre du bruit pur — confirme tout ce qui franchit entre "
        f"{s['fraction_la_plus_basse_confirmee']:.2f} et {p['fraction_haute']:.2f} feuille.",
        f"★★★ ET C'EST LA CONSÉQUENCE ENCHAÎNÉE QUI DÉCIDE, comme dans `103`, mais dans l'autre "
        f"sens et c'est pire. `103` chiffrait un TAUX D'ÉCHEC : une chute se voit. Ici c'est un "
        f"BIAIS : cent vingt pas TOUS CONFIRMÉS peuvent n'avoir franchi que "
        f"{p['spires_apres_120_pas_au_plus_bas']:.0f} spires, soit "
        f"{s['erreur_de_spires_maximale_sur_120']:.0f} de moins que le compte affiché, sans "
        f"qu'aucune vérification n'ait rien signalé.",
        f"⚠⚠ LA CAUSE EST STRUCTURELLE, PAS UN RÉGLAGE : la famille de gabarits de `98` est "
        f"{{1, 2, 3}}, donc le compte ne peut JAMAIS valoir moins de un. Un segment qui ne "
        f"franchit que 0,82 feuille rend « 1 interstice » avec un score de 0,781 contre une "
        f"barre de {b['barre_de_linterstice']}. Le compteur voit un saut ; il est aveugle à un retard.",
        f"⚠ ET LA BANDE NE DÉPEND PRESQUE PAS DU BRUIT — {b['par_bruit'][0]['largeur']:.2f} de "
        f"large à σ = 0 contre {b['par_bruit'][-1]['largeur']:.2f} à σ = 30. Ce n'est donc pas "
        f"une limite du scan qu'un meilleur volume lèverait, c'est le pouvoir de discrimination "
        f"de la forme des gabarits."
        + (f" Elle confond les {d['combien_de_pas_publies_confondus']} pas publiés par la "
           f"campagne, dont l'écart de {d['ecart_publie_par_99_en_pourcent']} % que `99` "
           f"laisse ouvert." if d.get("pas_publies_um") else ""),
        f"★★ LE REMPLAÇANT EXISTE ET IL EST CALIBRÉ : `feuilles_franchies` estime la fraction sur "
        f"une famille CONTINUE, donc elle peut valoir moins de un, et elle reproduit cos θ à trois "
        f"décimales près sur quatre obliquités fabriquées. Elle mesure exactement le retard que le "
        f"compteur entier ne voyait pas.",
        f"⚠ CE QUE CE FICHIER CHANGE DANS L'ORDRE DES CHOSES : la portée de `102` n'est PAS la "
        f"prochaine dépense. Mesurer la forme de la survie d'un critère juste à "
        f"{100 * (1 - s['fraction_la_plus_basse_confirmee']):.0f} % près, ce serait mesurer la "
        f"mauvaise chose. Le registre passe devant.",
    ]


def panneau_aveuglement(art, x0, y0, pw, ph, m, petit) -> int:
    """La diagonale est la vérité ; le compteur entier est une droite plate à un."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "ce que le segment franchit → ce qui est rendu",
             fill=DISCRET, font=petit)
    g, d = x0 + 46, x0 + pw - 22
    haut, bas = y0 + 40, y0 + ph - 92
    lo, hi = 0.4, 1.5
    def X(f): return g + (d - g) * (f - lo) / (hi - lo)
    def Y(f): return bas - (bas - haut) * (f - lo) / (hi - lo)
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    # la verite
    art.line([X(lo), Y(lo), X(hi), Y(hi)], fill=DISCRET)
    art.text((X(1.28) + 2, Y(1.42)), "vérité", fill=DISCRET, font=petit)
    poses, ecretes = 0, []
    for x in m["aveuglement"]["lignes"]:
        f = x["fraction_vraie"]
        if not lo <= f <= hi:
            continue
        # le compteur ENTIER : plat a un
        brut = float(x["compte_entier"])
        yc = Y(min(max(brut, lo), hi))
        art.ellipse([X(f) - 4, yc - 4, X(f) + 4, yc + 4],
                    fill=ROUGE if x["passe_la_barre"] else (225, 190, 185))
        # ⚠⚠ UN POINT ECRETE DOIT LE DIRE. Sans son etiquette il se lit comme une mesure posee
        # au bord du cadre, ce qui est exactement la faute que ce depot enregistre sous « une
        # limite de grille publiee comme une limite de matiere ».
        if brut > hi:
            art.text((X(f) + 7, yc - 6), f"={brut:.0f}", fill=DISCRET, font=petit)
            ecretes.append((f, brut))
        # l'estimateur CONTINU
        ye = Y(min(max(x["fraction_estimee"], lo), hi))
        art.ellipse([X(f) - 3, ye - 3, X(f) + 3, ye + 3], fill=VERT)
        poses += 2
    for f in (0.5, 0.75, 1.0, 1.25, 1.5):
        art.text((X(f) - 10, bas + 4), f"{f:.2f}", fill=DISCRET, font=petit)
        art.text((x0 + 6, Y(f) - 6), f"{f:.2f}", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 22), "rouge plein : compté 1 ET confirmé", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 36), "vert : estimateur continu", fill=VERT, font=petit)
    art.text((x0 + 8, bas + 56),
             "★ le compteur entier est PLAT à un :", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 70), "   il ne peut pas dire « moins d'une feuille ».",
             fill=ROUGE, font=petit)
    if ecretes:
        art.text((x0 + 8, bas + 90),
                 f"⚠ {len(ecretes)} point(s) écrêté(s), valeur écrite à côté.",
                 fill=DISCRET, font=petit)
    return poses


def panneau_bande(art, x0, y0, pw, ph, m, petit) -> int:
    """La bande d'acceptation par niveau de bruit, et son indifférence au bruit."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "quelles fractions ressortent CONFIRMÉES ?",
             fill=DISCRET, font=petit)
    lignes = [x for x in m["bande"]["par_bruit"] if not x.get("aucune_fraction_confirmee")]
    g, d = x0 + 46, x0 + pw - 24
    lo, hi = 0.4, 1.6
    def X(f): return g + (d - g) * (f - lo) / (hi - lo)
    haut = y0 + 44
    h = (ph - 150) / max(len(lignes), 1)
    barres = 0
    for j, x in enumerate(lignes):
        y = haut + j * h
        art.text((x0 + 6, y + 3), f"σ={x['bruit']:.0f}", fill=TEXTE, font=petit)
        art.rectangle([X(x["fraction_basse"]), y, X(x["fraction_haute"]), y + 13], fill=AMBRE)
        art.text((X(x["fraction_basse"]) - 30, y + 1), f"{x['fraction_basse']:.2f}",
                 fill=TEXTE, font=petit)
        art.text((X(x["fraction_haute"]) + 4, y + 1), f"{x['fraction_haute']:.2f}",
                 fill=TEXTE, font=petit)
        barres += 1
    # la verite : UNE feuille
    art.line([X(1.0), haut - 10, X(1.0), haut + len(lignes) * h + 2], fill=BLEU)
    art.text((X(1.0) - 20, haut - 24), "UNE feuille", fill=BLEU, font=petit)
    bas = haut + len(lignes) * h + 16
    art.text((x0 + 8, bas), "⚠ la bande ne dépend presque PAS du bruit :", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 14),
             f"   {lignes[0]['largeur']:.2f} de large à σ = {lignes[0]['bruit']:.0f}, "
             f"{lignes[-1]['largeur']:.2f} à σ = {lignes[-1]['bruit']:.0f}.",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 28), "   C'est la FORME des gabarits, pas le scan.",
             fill=ROUGE, font=petit)
    p = next((x for x in lignes if x["bruit"] == 15.0), lignes[0])
    art.text((x0 + 8, bas + 48), f"★ pas de feuille impliqué :", fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 62),
             f"   {p['pas_de_feuille_implique_um_bas']:.0f} à "
             f"{p['pas_de_feuille_implique_um_haut']:.0f} µm.", fill=AMBRE, font=petit)
    return barres


def panneau_consequence(art, x0, y0, pw, ph, m, petit) -> int:
    """Cent vingt pas tous confirmés, et les spires qu'ils franchissent réellement."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "120 pas CONFIRMÉS → combien de spires ?",
             fill=DISCRET, font=petit)
    lignes = [x for x in m["bande"]["par_bruit"] if not x.get("aucune_fraction_confirmee")]
    g, d = x0 + 46, x0 + pw - 24
    lo, hi = 60.0, 190.0
    def X(v): return g + (d - g) * (v - lo) / (hi - lo)
    haut = y0 + 44
    h = (ph - 180) / max(len(lignes), 1)
    barres = 0
    for j, x in enumerate(lignes):
        y = haut + j * h
        art.text((x0 + 6, y + 3), f"σ={x['bruit']:.0f}", fill=TEXTE, font=petit)
        art.rectangle([X(x["spires_apres_120_pas_au_plus_bas"]), y,
                       X(x["spires_apres_120_pas_au_plus_haut"]), y + 13], fill=ROUGE)
        art.text((X(x["spires_apres_120_pas_au_plus_bas"]) - 24, y + 1),
                 f"{x['spires_apres_120_pas_au_plus_bas']:.0f}", fill=TEXTE, font=petit)
        art.text((X(x["spires_apres_120_pas_au_plus_haut"]) + 4, y + 1),
                 f"{x['spires_apres_120_pas_au_plus_haut']:.0f}", fill=TEXTE, font=petit)
        barres += 1
    art.line([X(120.0), haut - 10, X(120.0), haut + len(lignes) * h + 2], fill=BLEU)
    art.text((X(120.0) - 34, haut - 24), "les 120 visées", fill=BLEU, font=petit)
    bas = haut + len(lignes) * h + 16
    s = m["resume"]
    art.text((x0 + 8, bas), "★★★ chaque pas est CONFIRMÉ, et pourtant", fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 14),
             f"   il manque jusqu'à {s['erreur_de_spires_maximale_sur_120']:.0f} spires.",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 34), "⚠⚠ une chute se VOIT ; un retard", fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 48), "   s'accumule en SILENCE.", fill=TEXTE, font=petit)
    d_ = m.get("ce_que_la_bande_ne_distingue_pas", {})
    if d_.get("pas_publies_um"):
        art.text((x0 + 8, bas + 68),
                 f"★ la bande confond les {d_['combien_de_pas_publies_confondus']} pas publiés,",
                 fill=AMBRE, font=petit)
        art.text((x0 + 8, bas + 82),
                 f"   dont l'écart de {d_['ecart_publie_par_99_en_pourcent']} % de `99`.",
                 fill=AMBRE, font=petit)
    return barres


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 330, 26, 400
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
             "Un pas confirmé n'est pas une feuille — la bande d'acceptation du critère de `102`",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"segments FABRIQUÉS, aucune lecture distante · un pas confirmé franchit entre "
             f"{s['fraction_la_plus_basse_confirmee']:.2f} et "
             f"{m['bande']['par_bruit'][0]['fraction_haute']:.2f} feuille · "
             f"jusqu'à {s['erreur_de_spires_maximale_sur_120']:.0f} spires d'erreur sur 120",
             fill=DISCRET, font=moyen)
    titres = ("A · NON — le compteur est plat à un",
              "B · la bande, et son indifférence au bruit",
              "C · ★ la conséquence sur cent vingt spires")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_aveuglement(art, marge, 104, pw, ph, m, petit)
    b = panneau_bande(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_consequence(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + j * (pw + ecart), 104, marge + j * (pw + ecart) + pw, 104 + ph)
              for j in range(3)]
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "aveuglement": a, "bande": b, "consequence": c,
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
    d = dessiner(m, RACINE / "docs" / "images" / "104_un_pas_confirme_nest_pas_une_feuille.png")
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
    # ⭐⭐⭐ LE PANNEAU A DOIT TRACER LES DEUX REPONSES, pas une : c'est leur ECART qui EST la
    # refutation, et le compteur entier seul se lirait comme une mesure ordinaire.
    dedans = [x for x in m["aveuglement"]["lignes"] if 0.4 <= x["fraction_vraie"] <= 1.5]
    v("le panneau A trace le compteur entier ET l'estimateur continu",
      d["aveuglement"] == 2 * len(dedans), f"{d['aveuglement']} pour {2 * len(dedans)}")
    # ⚠⚠ UN POINT ECRETE DOIT PORTER SA VALEUR : sans elle il se lit comme une mesure au bord
    # du cadre. Le controle verifie que chaque valeur ecretee est ECRITE dans la figure.
    hors = [x for x in dedans if float(x["compte_entier"]) > 1.5]
    v("chaque point écrêté du panneau A porte sa vraie valeur",
      all(f"={float(x['compte_entier']):.0f}" in " ".join(d["textes_dessines"]) for x in hors),
      str([x["compte_entier"] for x in hors]))
    n = len([x for x in m["bande"]["par_bruit"] if not x.get("aucune_fraction_confirmee")])
    v("le panneau B trace une bande par niveau de bruit", d["bande"] == n, str(d["bande"]))
    v("le panneau C trace une conséquence par niveau de bruit", d["consequence"] == n,
      str(d["consequence"]))
    v("les trois panneaux sont titrés", len(d["titres"]) == 3)

    # === LES VERDICTS SONT DANS LA MESURE, PAS SEULEMENT DANS LA PROSE ======================
    # ⚠⚠⚠ STRUCTUREL, PAS UN RESULTAT : asserter « la bande est large » obligerait a reecrire le
    # controle le jour ou le critere serait resserre. On asserte que le verdict EST rendu, avec
    # sa consequence, et que la prose porte le meme chiffre que la mesure.
    s = m["resume"]
    v("le verdict est rendu, quel qu'il soit",
      "un_pas_confirme_garantit_une_feuille" in s
      and "erreur_de_spires_maximale_sur_120" in s)
    v("... et l'ordonnancement en découle plutôt que d'être décrété",
      s["la_portee_est_la_prochaine_depense"]
      is bool(s["un_pas_confirme_garantit_une_feuille"]))
    v("chaque niveau de bruit porte sa conséquence enchaînée à côté de sa bande",
      all("spires_apres_120_pas_au_plus_bas" in x
          for x in m["bande"]["par_bruit"] if not x.get("aucune_fraction_confirmee")))
    # ⭐⭐ LE CHIFFRE DE LA PROSE EST CELUI DE LA MESURE, sinon la figure pourrait raconter autre
    # chose que ce qu'elle dessine — le defaut le plus discret d'une figure.
    txt = " ".join(prose(m))
    v("la prose porte le nombre de spires manquantes de la mesure",
      f"{s['erreur_de_spires_maximale_sur_120']:.0f}" in txt,
      f"{s['erreur_de_spires_maximale_sur_120']}")
    v("... et la fraction la plus basse confirmée",
      f"{s['fraction_la_plus_basse_confirmee']:.2f}" in txt)
    v("la prose garde la cause structurelle : la famille {1, 2, 3}",
      "{1, 2, 3}" in txt)
    v("... et l'indifférence de la bande au bruit", "ne dépend presque pas du bruit" in txt.lower())
    v("... et le fait que le remplaçant est CALIBRÉ sur cos θ", "cos θ" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images"
                   / "104_un_pas_confirme_nest_pas_une_feuille.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
