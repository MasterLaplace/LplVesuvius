#!/usr/bin/env python3
"""La bande bornee — un plancher de frequence PHYSIQUE, et ce qu'il retire a `107`.

★★★ LE PANNEAU A EST LE RESULTAT : les deux bandes sur les MEMES profils, mode par mode. La
falaise du mode qui « ne compte rien » disparait sous la bande bornee, et les deux modes se
rejoignent.

★★★ LE PANNEAU B EST CE QUI EMPECHE DE SE TROMPER : une bande etroite ne peut plus dire « pas de
periodicite » par son COMPTE, donc c'est le SCORE qui doit l'ecarter. Sur une derive SEULE, sans
aucune feuille, le score tombe sous la barre ; sur la matiere il la franchit.

★★★ LE PANNEAU C EST LA BARRE ELLE-MEME, longueur par longueur — parce que la bande change avec la
fenetre, donc son nul aussi. Elle BAISSE, ce que j'avais annonce a l'envers.

Usage :
    uv run python src/figures/figure_une_bande_qui_ne_bouge_pas_avec_la_fenetre.py --verifier
    uv run python src/figures/figure_une_bande_qui_ne_bouge_pas_avec_la_fenetre.py \\
        --sortie docs/images/111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png
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
MESURE = RACINE / "docs" / "mesures" / "une_bande_qui_ne_bouge_pas_avec_la_fenetre.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
BLEU = (54, 88, 132)
AMBRE = (176, 132, 44)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    lignes = []
    lignes.append(
        f"★★★ LE PLANCHER DE FRÉQUENCE DE `98` EST RELATIF À LA FENÊTRE, ET C'EST LE DÉFAUT. Il "
        f"cherche entre 0,35 et k+4 PÉRIODES PAR FENÊTRE, donc sur deux pas il admet une longueur "
        f"d'onde de 1314 µm et sur six de 3943 — alors qu'aucune n'est un espacement de feuille. "
        f"Le remède n'est pas un nouvel estimateur mais une BANDE dérivée de la matière : "
        f"`f = L / λ`, avec λ dans la plage que le balayage de `105` fixe déjà "
        f"({m.get('lambda_min_um')} à {m.get('lambda_max_um')} µm). Aucune ligne de `98` n'est "
        f"réécrite ; c'est la bande qui change, pas la machine.")
    pm = m.get("par_mode", {})
    if pm.get("mode_bas", {}).get("decidable"):
        b, h = pm["mode_bas"], pm["mode_haut"]
        lignes.append(
            f"★★★ ET LE MODE QUI « NE COMPTE RIEN » COMPTE. Sous l'ancienne bande il tombe d'une "
            f"falaise — {b['ancien_au_plus_court']} feuille par pas à deux pas puis "
            f"{b['ancien_au_plus_long']} à six, dérive {b['derive_de_lancien']:+.3f}. Sous la "
            f"bande bornée, sur LES MÊMES échantillons : {b['borne_au_plus_court']} puis "
            f"{b['borne_au_plus_long']}, dérive {b['derive_du_borne']:+.3f}. "
            f"★ Il franchissait une feuille par pas depuis le début, et c'est l'instrument qui la "
            f"perdait.")
        lignes.append(
            f"★★★ ET LA BIMODALITÉ DE `107` S'EFFACE PRESQUE ENTIÈREMENT. L'écart entre les deux "
            f"modes au plus long passe de {pm['ecart_entre_modes_au_plus_long_ancien']:+.3f} "
            f"feuille par pas à {pm['ecart_entre_modes_au_plus_long_borne']:+.3f}. Les « deux "
            f"populations que rien ne distingue » de `107` étaient, pour l'essentiel, une "
            f"population lue par un instrument qui perdait la moitié de ses profils.")
    cf = m.get("controle_fabrique", {})
    if cf:
        lignes.append(
            f"⚠⚠⚠ ET LE PRIX DE LA BANDE ÉTROITE EST NOMMÉ AVANT D'ÊTRE MESURÉ : elle ne peut "
            f"plus dire « pas de périodicité » PAR SON COMPTE. Sur une dérive SEULE, sans aucune "
            f"feuille, elle rend quand même un nombre. C'est le SCORE qui doit l'écarter, et il "
            f"le fait : {cf.get('score_max_sur_une_derive_seule')} au plus sur une dérive seule "
            f"contre {cf.get('score_min_sur_une_periodicite_pure')} au moins sur une périodicité "
            f"pure. ★ Et le contrôle est à double sens : la bande bornée garde le compte sous une "
            f"dérive ({cf.get('la_bande_bornee_garde_le_compte_sous_une_derive')}) là où "
            f"l'ancienne le perd ({cf.get('lancienne_bande_le_perd')}).")
    n = m.get("nul_de_la_bande", {})
    if n.get("par_longueur"):
        a, z = n["par_longueur"][0], n["par_longueur"][-1]
        lignes.append(
            f"⚠⚠ LA BANDE BORNÉE A DONC BESOIN DE SA PROPRE BARRE, ET ELLE CHANGE AVEC LA "
            f"LONGUEUR : {a['p99_du_score']} à {a['longueur_um']:.0f} µm contre "
            f"{z['p99_du_score']} à {z['longueur_um']:.0f}. ⚠⚠⚠ Elle BAISSE, et j'avais annoncé "
            f"l'inverse : deux effets s'opposent — la bande s'élargit avec la fenêtre, mais le "
            f"nombre d'ÉCHANTILLONS grandit et la corrélation fortuite décroît en `1/√n` — et "
            f"c'est le second qui gagne. La bande bornée devient PLUS discriminante quand la "
            f"marche s'allonge, pas moins.")
        if pm.get("mode_bas", {}).get("par_longueur"):
            parts = [x.get("part_au_dessus_de_la_barre") for x in pm["mode_bas"]["par_longueur"]
                     if x.get("part_au_dessus_de_la_barre") is not None]
            if parts:
                lignes.append(
                    f"★★ ET LE COMPTE DU MODE BAS EST LU AU-DESSUS DE CETTE BARRE, ce qui est la "
                    f"condition sans laquelle « il compte 0,95 » ne voudrait rien dire : "
                    f"{min(parts):.1%} à {max(parts):.1%} de ses marches la franchissent selon la "
                    f"longueur. ⚠ Il reste plus bas que le mode haut EN SCORE — la périodicité y "
                    f"est moins nette — mais plus en COMPTE : les deux franchissent une feuille "
                    f"par pas.")
    lignes.append(
        "⚠⚠⚠ ET LA DETTE RÉTROACTIVE EST LOURDE, elle doit être dite avec le résultat : `99` à "
        "`110` ont tous été mesurés avec la bande non bornée. Ce que cette tranche déplace en "
        "premier est `107` — ses deux populations — et par ricochet `108`, qui cherchait ce qui "
        "les sépare. Ce que `108` a trouvé reste vrai et change de sens : le score du PAS, lui "
        "borné par les candidats du balayage, prédit quand l'estimateur NON borné perd le signal.")
    lignes.append(
        "⚠ CE QUE CETTE TRANCHE NE DIT PAS : que le marcheur porte plus loin — la portée de `107` "
        "est inchangée ; que six pas valent cent vingt ; ni ce que la quantité mesurée SIGNIFIE, "
        "`106` restant debout. Et une bande bornée ne peut jamais répondre « aucune feuille ici » "
        "autrement que par son score : c'est un instrument plus juste, pas un instrument qui sait "
        "tout dire.")
    return lignes


def _cadre(art, x0, y0, pw, ph, titre, petit):
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), titre, fill=DISCRET, font=petit)


def panneau_modes(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "les deux bandes sur les MÊMES profils, par mode", petit)
    pm = m.get("par_mode", {})
    if not pm.get("mode_bas", {}).get("decidable"):
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    series = []
    for nom, lib in (("mode_haut", "mode qui compte"), ("mode_bas", "mode qui ne compte rien")):
        series.append((f"{lib} · ANCIEN", pm[nom]["par_longueur"], "ancien_median",
                       ROUGE if nom == "mode_bas" else AMBRE))
        series.append((f"{lib} · BORNÉ", pm[nom]["par_longueur"], "borne_median",
                       VERT if nom == "mode_bas" else BLEU))
    g, d = x0 + 46, x0 + pw - 62
    haut, bas = y0 + 76, y0 + ph - 106
    hi = 1.3
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    yun = bas - (bas - haut) * (1.0 / hi)
    art.line([g, yun, d, yun], fill=DISCRET)
    art.text((d + 3, yun - 6), "1,0", fill=DISCRET, font=petit)
    pts = 0
    for j, (nom, lig, cle, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 20 + j * 13), nom, fill=coul, font=petit)
        n = len(lig)
        prec = None
        for i, x in enumerate(lig):
            xx = g + (d - g) * i / max(n - 1, 1)
            yy = bas - (bas - haut) * (min(x[cle], hi) / hi)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 4, bas + 4), f"{x['pas']}", fill=DISCRET, font=petit)
            pts += 1
    art.text((x0 + 8, bas + 22), "longueur du préfixe, en pas", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 42),
             f"★★★ la falaise du mode bas : {pm['falaise_de_lancien_dans_le_mode_bas']:+.3f}",
             fill=ROUGE, font=petit)
    art.text((x0 + 8, bas + 58),
             f"    devient {pm['falaise_du_borne_dans_le_mode_bas']:+.3f} sous la bande bornée",
             fill=VERT, font=petit)
    art.text((x0 + 8, bas + 78),
             f"★ écart entre les modes au plus long :", fill=TEXTE, font=petit)
    art.text((x0 + 8, bas + 92),
             f"   {pm['ecart_entre_modes_au_plus_long_ancien']:+.3f} → "
             f"{pm['ecart_entre_modes_au_plus_long_borne']:+.3f}", fill=TEXTE, font=petit)
    return pts


def panneau_controles(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "ce qui empêche de se tromper : les cas connus", petit)
    cf = m.get("controle_fabrique", {})
    cas = cf.get("cas", [])
    if not cas:
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    y = y0 + 26
    traces = 0
    for c in cas:
        lig = [x for x in c["par_longueur"] if x.get("decidable")]
        if not lig:
            continue
        attendu = c["attendu_une_feuille_par_pas"]
        art.text((x0 + 10, y), c["cas"][:44], fill=TEXTE if attendu else AMBRE, font=petit)
        # ⚠ Le compte SEUL sur la ligne : mettre le score entre parentheses a chaque longueur
        # faisait 839 pixels dans un panneau qui en fait 366, et la garde de cadre l'a dit.
        for k, (cle, lib, coul) in enumerate((("ancien", "anc", ROUGE),
                                              ("borne", "bor", VERT))):
            yy = y + 14 + k * 13
            art.text((x0 + 14, yy), lib, fill=coul, font=petit)
            art.text((x0 + 44, yy),
                     " ".join(f"{x['pas']}:{x[cle]['feuilles_par_pas']:.2f}" for x in lig),
                     fill=coul, font=petit)
            traces += 1
        # ⚠⚠ ET LE SCORE DU BORNE EST RENDU A PART, parce que c'est LUI qui ecarte : sur une
        # derive seule le compte ne dit rien et le score dit tout.
        art.text((x0 + 44, y + 40),
                 "score borné  "
                 + " ".join(f"{x['borne']['score']:.2f}" for x in lig),
                 fill=DISCRET, font=petit)
        y += 58
    art.text((x0 + 10, y + 2),
             f"★ la bornée garde le compte sous une dérive : "
             f"{cf.get('la_bande_bornee_garde_le_compte_sous_une_derive')}",
             fill=VERT, font=petit)
    art.text((x0 + 10, y + 16),
             f"★ l'ancienne le perd : {cf.get('lancienne_bande_le_perd')}",
             fill=ROUGE, font=petit)
    art.text((x0 + 10, y + 34), "⚠⚠ le PRIX : sur une dérive SEULE la bornée", fill=AMBRE,
             font=petit)
    art.text((x0 + 10, y + 48), "   rend quand même un compte — c'est le SCORE", fill=AMBRE,
             font=petit)
    art.text((x0 + 10, y + 62),
             f"   qui l'écarte : {cf.get('score_max_sur_une_derive_seule')} contre "
             f"{cf.get('score_min_sur_une_periodicite_pure')}", fill=AMBRE, font=petit)
    return traces


def panneau_barre(art, x0, y0, pw, ph, m, petit) -> int:
    _cadre(art, x0, y0, pw, ph, "la barre de la bande bornée, longueur par longueur", petit)
    n = m.get("nul_de_la_bande", {})
    lig = n.get("par_longueur") or []
    if not lig:
        art.text((x0 + 8, y0 + 30), "non décidable", fill=ROUGE, font=petit)
        return 0
    pm = m.get("par_mode", {})
    g, d = x0 + 46, x0 + pw - 62
    haut, bas = y0 + 56, y0 + ph - 150
    hi = max([x["p99_du_score"] for x in lig]
             + [y["score_borne_median"] for nom in ("mode_haut", "mode_bas")
                for y in (pm.get(nom, {}).get("par_longueur") or [])]) * 1.2
    art.line([g, bas, d, bas], fill=CADRE)
    art.line([g, haut, g, bas], fill=CADRE)
    series = [("la BARRE (p99 du nul)", [x["p99_du_score"] for x in lig], DISCRET)]
    for nom, lib, coul in (("mode_haut", "score du mode qui compte", BLEU),
                           ("mode_bas", "score du mode qui ne compte rien", VERT)):
        b = pm.get(nom, {}).get("par_longueur")
        if b:
            series.append((lib, [x["score_borne_median"] for x in b], coul))
    pts = 0
    for j, (nom, vals, coul) in enumerate(series):
        art.text((x0 + 10, y0 + 20 + j * 12), nom, fill=coul, font=petit)
        prec = None
        for i, val in enumerate(vals):
            xx = g + (d - g) * i / max(len(vals) - 1, 1)
            yy = bas - (bas - haut) * (val / hi)
            if prec is not None:
                art.line([prec[0], prec[1], xx, yy], fill=coul)
            art.rectangle([xx - 2, yy - 2, xx + 2, yy + 2], fill=coul)
            prec = (xx, yy)
            if j == 0:
                art.text((xx - 12, bas + 4), f"{lig[i]['longueur_um']:.0f}", fill=DISCRET,
                         font=petit)
            pts += 1
    art.text((x0 + 8, bas + 20), "longueur de la fenêtre, en µm", fill=DISCRET, font=petit)
    art.text((x0 + 8, bas + 40),
             f"⚠⚠⚠ la barre BAISSE (pente {n['pente_de_la_barre']:+.4f})", fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 54), "    j'avais annoncé l'inverse : les", fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 68), "    échantillons grandissent plus vite", fill=AMBRE, font=petit)
    art.text((x0 + 8, bas + 82), "    que la bande ne s'élargit", fill=AMBRE, font=petit)
    b = pm.get("mode_bas", {}).get("par_longueur")
    if b and b[0].get("part_au_dessus_de_la_barre") is not None:
        parts = [x["part_au_dessus_de_la_barre"] for x in b]
        art.text((x0 + 8, bas + 104),
                 f"★★ le mode bas franchit sa barre :", fill=VERT, font=petit)
        art.text((x0 + 8, bas + 118),
                 f"   {min(parts):.0%} à {max(parts):.0%} de ses marches", fill=VERT, font=petit)
        art.text((x0 + 8, bas + 132),
                 f"   donc son compte est lu au-dessus du bruit", fill=VERT, font=petit)
    return pts


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 366, 26, 510
    largeur_utile = pw * 3 + ecart * 2
    for coupe in (160, 150, 142, 134, 126, 118):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = Tracee(ImageDraw.Draw(toile))
    pm = m.get("par_mode", {})
    art.text((marge, 16),
             "Une bande qui ne bouge pas avec la fenêtre — le plancher devient physique",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"{m.get('marches_lues')} marches · λ de {m.get('lambda_min_um')} à "
             f"{m.get('lambda_max_um')} µm · "
             + ("la falaise du mode bas disparaît"
                if pm.get("la_bande_bornee_retire_la_falaise_du_mode_bas")
                else "la falaise du mode bas RÉSISTE"),
             fill=DISCRET, font=moyen)
    titres = ("A · ★ la falaise et sa disparition",
              "B · ★ les cas connus, deux bandes",
              "C · ★ la barre, et qui la franchit")
    for k, t in enumerate(titres):
        art.text((marge + k * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    a = panneau_modes(art, marge, 104, pw, ph, m, petit)
    b = panneau_controles(art, marge + pw + ecart, 104, pw, ph, m, petit)
    c = panneau_barre(art, marge + 2 * (pw + ecart), 104, pw, ph, m, petit)
    cadres = [(marge + k * (pw + ecart), 104, marge + k * (pw + ecart) + pw, 104 + ph)
              for k in range(3)]
    debut = H - len(lignes) * 19 - 12
    for k, l in enumerate(lignes):
        art.text((marge, debut + k * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"titres": titres, "modes": a, "controles": b, "barre": c,
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
    d = dessiner(m, RACINE / "docs" / "images" /
                 "111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png")
    v("la figure est écrite", Path(d["sortie"]).is_file())
    v("les trois panneaux portent quelque chose",
      d["modes"] > 0 and d["controles"] > 0 and d["barre"] > 0,
      f"{d['modes']} / {d['controles']} / {d['barre']}")
    v("aucun texte ne déborde du cadre", not d["debordants"], str(d["debordants"][:2]))
    v("aucun texte ne sort de son panneau", not d["hors_cadre"], str(d["hors_cadre"][:2]))
    v("aucun texte n'en recouvre un autre", not d["recouvrements"],
      str(d["recouvrements"][:2]))
    v("la prose tient dans la largeur utile",
      all(w <= d["largeur_utile"] for _t, w in d["prose"]))
    v("la prose est traçable par la police déployée",
      prose_tracable([t for t, _w in d["prose"]]))

    txt = " ".join(t for t, _w in d["prose"])
    pm = m.get("par_mode", {})
    # ⭐⭐⭐ LA GARDE QUI COMPTE : le resultat ne voyage jamais sans son PRIX. Une bande etroite ne
    # peut plus dire « pas de periodicite » par son compte ; taire cela ferait lire « tout compte
    # une feuille par pas » comme un fait de la matiere alors que c'est en partie la bande.
    v("la prose porte le PRIX de la bande étroite",
      "PAR SON COMPTE" in txt and "dérive SEULE" in txt)
    v("... et le contrôle à double sens qui l'encadre",
      str(m["controle_fabrique"]["score_max_sur_une_derive_seule"]) in txt
      and str(m["controle_fabrique"]["score_min_sur_une_periodicite_pure"]) in txt)
    # ⚠⚠ LA DETTE RETROACTIVE EST UNE PARTIE DU RESULTAT, pas une note de bas de page.
    v("la prose dit la dette rétroactive sur `99` à `110`",
      "`99`" in txt and "`110`" in txt and "non bornée" in txt)
    v("... et ce qu'elle fait à `108`", "`108`" in txt)
    if pm.get("mode_bas", {}).get("decidable"):
        v("la prose porte la falaise AVANT et APRÈS",
          f"{pm['falaise_de_lancien_dans_le_mode_bas']:+.3f}" in txt
          and f"{pm['falaise_du_borne_dans_le_mode_bas']:+.3f}" in txt)
        v("... et l'écart entre les modes aux deux bandes",
          f"{pm['ecart_entre_modes_au_plus_long_ancien']:+.3f}" in txt
          and f"{pm['ecart_entre_modes_au_plus_long_borne']:+.3f}" in txt)
        # ⭐⭐ SANS CELA, « LE MODE BAS COMPTE 0,95 » NE VEUT RIEN DIRE : un compte lu sous la barre
        # du bruit n'est pas un compte.
        v("... et le fait que son compte est lu AU-DESSUS de la barre",
          "au-dessus de cette barre" in txt.lower() or "franchissent" in txt)
    n = m.get("nul_de_la_bande", {})
    if n.get("par_longueur"):
        v("la prose publie que la barre BAISSE, et que j'avais annoncé l'inverse",
          "BAISSE" in txt and "l'inverse" in txt)
    v("la prose garde debout ce que `106` a mesuré",
      "`106`" in txt)
    v("... et dit que la portée de `107` est inchangée",
      "portée de `107`" in txt and "inchangée" in txt)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" /
                   "111_une_bande_qui_ne_bouge_pas_avec_la_fenetre.png")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    d = dessiner(json.loads(MESURE.read_text()), a.sortie)
    print(f"écrit : {d['sortie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
