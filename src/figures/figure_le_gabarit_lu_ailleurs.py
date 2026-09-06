#!/usr/bin/env python3
"""Le gabarit lui-même, mis en question : plus large, ailleurs, moyenné, ou parfait.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. La tranche précédente a désigné un chantier plutôt qu'une porte
close : le raccrochage lit, très peu, et il reste 16,7 µm entre lui et un oracle borné à la même
fenêtre. Ce qu'il cherche — le **gabarit** — n'avait jamais été mis en question : une seule
spire, une seule largeur, jamais comparé à rien.

⭐⭐ Les deux panneaux portent les deux critères, et il en faut deux. Le panneau A donne
l'**accord de rang** avec le décalage de l'oracle, c'est-à-dire ce que chaque forme CHOISIT ;
le panneau B donne l'**erreur de marche**, c'est-à-dire ce qu'elle COÛTE. Une forme peut mieux
choisir sans moins coûter, et publier un seul des deux ferait passer ce désaccord pour un accord.

⚠⚠ La fenêtre de recherche est la MÊME pour toutes les largeurs, et toutes sont jugées sur les
MÊMES cellules — sans ces deux propriétés, les barres compareraient des fenêtres et des
populations plutôt que des formes.

Usage :
    uv run python src/figures/figure_le_gabarit_lu_ailleurs.py --verifier
    uv run python src/figures/figure_le_gabarit_lu_ailleurs.py \\
        --sortie docs/images/75_le_gabarit_lu_ailleurs.png
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
MESURE = RACINE / "docs" / "mesures" / "le_gabarit_lu_ailleurs.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
CADRE = (200, 200, 200)

# ⚠ Une couleur par SOURCE, pas par largeur : la largeur est déjà portée par les groupes en
# abscisse, et coder deux fois la même chose ferait lire un motif là où il n'y en a qu'un.
COULEUR = {"depart": AMBRE, "ailleurs": BLEU, "moyennee": VERT, "arrivee": ROUGE}


def prose(m: dict) -> list[str]:
    ref, ma, me = m["variante_deployee"], m["meilleure_par_accord"], m["meilleure_par_erreur"]
    b = m["gabarit_borne"]

    def ap(v: dict, cle: str) -> str:
        e = v[cle]
        return (f"{e['ecart_median_um']:+.1f} um, {e['pas_ameliores']}/{e['pas']} pas, "
                f"intervalle {e['intervalle_um']}")

    return [
        f"{m['paires']} pas, {m['cellules']} cellules, {m['variantes_mesurees']} formes de "
        f"gabarit : {len(m['demi_largeurs_vx'])} demi-largeurs ({m['demi_largeurs_vx']} voxels, "
        f"derivees de la demi-feuille de {m['demi_feuille_vx']}) x 4 sources. ⚠ la fenetre de "
        "recherche est la MEME pour toutes, et toutes sont jugees sur les MEMES cellules — "
        "sinon les barres compareraient des fenetres et des populations plutot que des formes.",
        f"⚠⚠ le temoin LIT AUSSI : {m['melanges_qui_lisent']} des {m['variantes_mesurees']} "
        "gabarits MELANGES s'accordent deja positivement avec l'oracle. une ligne qui traverse "
        "des feuilles est PERIODIQUE, donc n'importe quel vecteur fixe trouve ses maxima aux "
        "memes phases. a demi-largeur 31 le melange fait meme MIEUX que la vraie forme. chaque "
        "forme est donc jugee sur son accord NET de son propre melange.",
        f"⚠⚠ et les erreurs sont comparees PAS PAR PAS : ici, ne rien faire coute de 32 a 74 um "
        f"selon le pas, soit quatre fois l'ecart entre deux methodes. chaque ecart porte donc "
        f"son intervalle a un pas de moins, et ne tranche que s'il reste negatif quand N'IMPORTE "
        f"QUEL pas sort. reperes, en medianes PAR PAS comme les barres : ne pas bouger "
        f"{m['erreur_sans_bouger_mediane_um']} um, oracle {m['erreur_oracle_mediane_um']} um "
        f"(sur toutes les cellules d'un coup : {m['erreur_sans_bouger_globale_um']} et "
        f"{m['erreur_oracle_globale_um']}).",
        f"en service (barre a contour noir) : demi-largeur {ref['demi_largeur_vx']} vx sur la "
        f"spire de DEPART, accord NET {ref['rho_net_median']}. ⚠⚠ contre NE PAS BOUGER il fait "
        f"{ap(ref, 'contre_sans_bouger')} — donc il ne tranche PAS : sur ces pas, le "
        "raccrochage en service est indistinguable de l'immobilite.",
        f"⚠⚠ UNE FORME FAIT MIEUX, ET CE N'EST PAS CELLE QUI LIT LE MIEUX. la meilleure LECTURE "
        f"est {ma['demi_largeur_vx']} vx / {ma['source']} (net {ma['rho_net_median']}), et elle "
        f"MARCHE plus mal que le deploye ({ap(ma, 'contre_le_deploye')}) : un accord de rang "
        f"est invariant d'echelle, donc mieux ORDONNER n'est pas mieux MARCHER. la meilleure "
        f"MARCHE est {me['demi_largeur_vx']} vx / {me['source']} — "
        f"{ap(me, 'contre_le_deploye')} contre le deploye, et {ap(me, 'contre_sans_bouger')} "
        "contre l'immobilite. c'est la seule des seize qui tranche sur les deux.",
        f"la BORNE (barres hachurees, hors production), le gabarit de la spire d'ARRIVEE, n'existe pas en "
        f"production. il ne lit pas mieux ({m['paires_ou_la_borne_lit_mieux']}/{m['paires']} "
        f"pas) et ne marche pas mieux de facon decidable ({ap(b, 'contre_le_deploye')}). meme "
        f"parfaite, la forme ne rend presque rien : le meilleur gain de la famille vaut "
        f"{abs(me['contre_le_deploye']['ecart_median_um'])} um sur les "
        f"{round(ref['erreur_globale_um'] - m['erreur_oracle_globale_um'], 1)} qui separent le "
        "deploye de l'oracle.",
        f"⚠⚠ le remede evident est mesure puis REFUTE : recaler l'amplitude par un facteur "
        f"unique, ajuste HORS ECHANTILLON, coute {-m['gain_du_recalage_um']} um. et la limite "
        f"est comptee plutot que deploree — pas complets par cote de boite : "
        + " · ".join(f"{int(x['cote_voxels'])} vx → {x['pas_complets']}"
                     for x in m["pas_par_cote"])
        + ". elargir la fenetre plafonne a huit pas : ce qui borne la campagne n'est pas la "
        "boite, c'est le nombre de spires segmentees.",
    ]


def barres(art, x0: int, y0: int, pw: int, ph: int, m: dict, cle: str, temoin: str | None,
           reperes: list[float], petit, legende: str) -> None:
    """Un groupe par demi-largeur, une barre par source — et, à côté, celle de son MÉLANGE.

    ⚠⚠⚠ LE TÉMOIN EST DESSINÉ CONTRE CHAQUE BARRE, PAS RÉSUMÉ EN LÉGENDE, et c'est ce que ce
    panneau existe pour montrer : à demi-largeur 31 voxels le gabarit mélangé s'accorde MIEUX
    avec l'oracle que le vrai. Une figure qui ne porterait que les accords bruts ferait lire un
    gabarit large comme une meilleure lecture, alors que c'est la périodicité des feuilles que
    n'importe quel vecteur fixe retrouve. La distance entre les deux barres EST le résultat.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    larg = m["demi_largeurs_vx"]
    vals = {(v["demi_largeur_vx"], v["source"]): v for v in m["variantes"]}
    plats = [v[cle] for v in m["variantes"] if v[cle] is not None] + [r for r in reperes]
    if temoin:
        plats += [v[temoin] for v in m["variantes"] if v[temoin] is not None]
    # ⚠⚠ L'AXE EST TIRÉ DES DONNÉES ET NON POSÉ AU MILIEU. Un zéro placé à mi-hauteur d'office
    # gaspille la moitié du panneau quand les valeurs négatives sont petites — c'est le cas de
    # l'accord d'un mélange — et écrase les barres qu'on est venu comparer.
    bas = min(0.0, min(plats)) if plats else 0.0
    haut = max(0.0, max(plats)) if plats else 1.0
    etendue = (haut - bas) * 1.12 or 1.0
    hmax = ph - 92
    base = y0 + ph - 30 - (0.0 - bas) / etendue * hmax
    echelle = hmax / etendue
    art.line([x0, base, x0 + pw, base], fill=TEXTE)
    for val in reperes:
        y = base - val * echelle
        for xx in range(x0 + 2, x0 + pw - 2, 7):
            art.line([xx, y, xx + 3, y], fill=DISCRET)
    pas_groupe = pw / (len(larg) + 0.4)
    demi = pas_groupe * 0.045 if temoin else pas_groupe * 0.085
    for i, dg in enumerate(larg):
        cx = x0 + pas_groupe * (i + 0.6)
        for k, nom in enumerate(m["sources"]):
            v = vals.get((dg, nom))
            if v is None:
                continue
            gx = cx + (k - 1.5) * 0.21 * pas_groupe
            traits = [(v[cle], COULEUR[nom], -demi if temoin else 0.0)]
            if temoin:
                traits.append((v[temoin], DISCRET, demi))
            for val, coul, dx in traits:
                if val is None:
                    continue
                # ⚠ Les deux ordonnées sont TRIÉES : PIL exige que le coin haut vienne en
                # premier, donc une barre NÉGATIVE — un accord de rang qui descend sous zéro,
                # ce que fait précisément un mélange — ferait lever au lieu de se dessiner.
                h = val * echelle
                y1, y2 = min(base, base - h), max(base, base - h)
                boite = [gx + dx - demi, y1, gx + dx + demi, y2]
                art.rectangle(boite, fill=coul)
                # ⚠⚠ LA FORME EN SERVICE ET LA BORNE SONT MARQUÉES PAR DU DESSIN, PAS PAR UN
                # CARACTÈRE. La police du dépôt ne rend ni ⭐ ni ⛔ — mesuré par la sonde de
                # `figure_commune`, pas supposé — et un glyphe absent se dessine en carré vide,
                # donc la marque la plus visible de la figure serait exactement celle qu'on ne
                # peut pas lire. Un contour et des hachures ne dépendent d'aucune police.
                if dx <= 0 and v["deployee"]:
                    art.rectangle(boite, outline=TEXTE)
                elif dx <= 0 and not v["disponible_en_production"]:
                    for yy in range(int(y1) + 2, int(y2), 4):
                        art.line([boite[0], yy, boite[2], yy], fill=FOND)
        art.text((cx - 10, y0 + ph - 15), f"{dg} vx", fill=DISCRET, font=petit)
    art.text((x0 + 6, y0 + 6), legende, fill=DISCRET, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ph, ecart = 40, 430, 262, 56
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    legendes = [
        "ambre DEPART · bleu AILLEURS · vert MOYENNEE · rouge ARRIVEE",
        "abscisse : demi-largeur · contour noir : la forme EN SERVICE",
        "hachures : la BORNE, qui n'existe pas en production",
        "gris a droite de chaque barre : le MEME gabarit MELANGE",
        "gris a droite : la meme forme, decalages RECALES hors echantillon",
        f"pointilles : ne pas bouger {m['erreur_sans_bouger_mediane_um']} um (haut), "
        f"oracle {m['erreur_oracle_mediane_um']} um (bas)",
    ]
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 106 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Le gabarit lui-meme : plus large, ailleurs, moyenne, ou parfait",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['variantes_mesurees']} formes · {m['paires']} pas · {m['cellules']} cellules · "
             f"meme fenetre, memes cellules", fill=DISCRET, font=moyen)

    # ---------- A : ce que chaque forme CHOISIT ----------
    art.text((marge, 76), "A · ce que chaque forme lit, et ce que son MELANGE lit deja",
             fill=TEXTE, font=moyen)
    barres(art, marge, 96, pw, ph, m, "rho_median", "rho_median_du_melange", [],
           petit, legendes[0])
    art.text((marge + 6, 96 + 22), legendes[3], fill=DISCRET, font=petit)
    art.text((marge + 6, 96 + ph + 6), legendes[1], fill=DISCRET, font=petit)
    art.text((marge + 6, 96 + ph + 21), legendes[2], fill=DISCRET, font=petit)

    # ---------- B : ce que chaque forme COÛTE ----------
    bx = marge + pw + ecart
    art.text((bx, 76), "B · ce que chaque forme COUTE (erreur de marche)", fill=TEXTE, font=moyen)
    barres(art, bx, 96, pw, ph, m, "erreur_mediane_um", "erreur_recalee_mediane_um",
           [m["erreur_sans_bouger_mediane_um"], m["erreur_oracle_mediane_um"]],
           petit, legendes[0])
    art.text((bx + 6, 96 + 22), legendes[4], fill=DISCRET, font=petit)
    art.text((bx + 6, 96 + 38), legendes[5], fill=DISCRET, font=petit)
    art.text((bx + 6, 96 + ph + 6), legendes[1], fill=DISCRET, font=petit)
    art.text((bx + 6, 96 + ph + 21), legendes[2], fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    etiquettes = [f"{d} vx" for d in m["demi_largeurs_vx"]]
    return {"variantes": len(m["variantes"]), "etiquettes": etiquettes,
            "legendes": [(t, petit.getbbox(t)[2]) for t in legendes],
            "prose": [(t, moyen.getbbox(t)[2]) for t in lignes],
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
    # ⚠⚠⚠ LES DEUX PROPRIÉTÉS QUI RENDENT LE BALAYAGE HONNÊTE, RELUES DEPUIS LA MESURE : sans
    # elles les barres compareraient des fenêtres et des populations plutôt que des formes.
    fen = {tuple(x["fenetre_vx"]) for e in m["lignes"] for x in e["essais"]}
    v("toutes les formes balayent la MÊME fenêtre", len(fen) == 1, str(sorted(fen)))
    v("... et toutes sont jugées sur les MÊMES cellules",
      all(len(e["essais"]) == m["variantes_mesurees"] for e in m["lignes"]),
      str([e["cellules"] for e in m["lignes"]]))
    v("la forme EN SERVICE est dans le balayage, et une seule",
      sum(1 for x in m["variantes"] if x["deployee"]) == 1,
      f"{m['variante_deployee']['demi_largeur_vx']} vx / "
      f"{m['variante_deployee']['source']}")
    # ⛔ La borne n'est pas une méthode : si elle passait pour disponible, la figure
    # annoncerait un remède qui n'existe pas.
    v("... et la BORNE est marquée comme indisponible en production",
      not m["gabarit_borne"]["disponible_en_production"]
      and m["meilleure_par_accord"]["disponible_en_production"])
    v("l'oracle des décalages reste une borne, à un voxel près",
      all(e["erreur_oracle_um"] <= min(x["erreur_um"] for x in e["essais"]) + m["voxel_um"]
          for e in m["lignes"]))
    # ⚠⚠ LES DEUX VERDICTS EXIGENT CHACUN SA MÉDIANE **ET** SON COMPTE PAR PAS.
    # ⚠⚠⚠ LE FAIT QUE LA FIGURE PORTE, ET LE PLUS FACILE À PERDRE EN RÉÉCRIVANT LA PROSE : le
    # témoin lit aussi. Sans lui, un gabarit large passerait pour une meilleure lecture alors
    # que c'est la périodicité des feuilles que son propre mélange retrouve.
    v("le témoin LIT aussi, et c'est pourquoi les accords sont publiés NETS",
      m["melanges_qui_lisent"] > 0
      and all(x["rho_net_median"] is None
              or abs(x["rho_net_median"]) <= 2.0 for x in m["variantes"]),
      f"{m['melanges_qui_lisent']} mélanges sur {m['variantes_mesurees']}")
    # ⭐⭐⭐ LES DEUX CRITÈRES SE CONTREDISENT, et c'est le résultat : la forme en service est
    # battue sur la LECTURE et invaincue sur la MARCHE. Perdre l'une des deux moitiés ferait
    # lire « le gabarit est le levier » ou « le gabarit est parfait », deux fois faux.
    v("une autre forme lit mieux que celle en service", m["une_autre_forme_lit_mieux"],
      f"{m['meilleure_par_accord']['demi_largeur_vx']} vx / "
      f"{m['meilleure_par_accord']['source']}, net "
      f"{m['meilleure_par_accord']['rho_net_median']} contre "
      f"{m['variante_deployee']['rho_net_median']}")
    # ⭐⭐⭐ ET CE N'EST PAS LA MÊME QUI MARCHE LE MIEUX. Un accord de rang est invariant
    # d'échelle : mieux ORDONNER les décalages n'est pas mieux MARCHER, et la figure porte les
    # deux critères précisément pour que ce désaccord soit visible plutôt que tranché d'office.
    v("... et ce n'est PAS la même forme qui marche le mieux",
      m["une_autre_forme_marche_mieux"]
      and (m["meilleure_par_erreur"]["demi_largeur_vx"],
           m["meilleure_par_erreur"]["source"])
      != (m["meilleure_par_accord"]["demi_largeur_vx"], m["meilleure_par_accord"]["source"]),
      f"lecture {m['meilleure_par_accord']['demi_largeur_vx']} vx / "
      f"{m['meilleure_par_accord']['source']} · marche "
      f"{m['meilleure_par_erreur']['demi_largeur_vx']} vx / "
      f"{m['meilleure_par_erreur']['source']}")
    # ⚠⚠⚠ ET LE FAIT LE PLUS DUR DE LA TRANCHE : la forme EN SERVICE ne bat pas l'immobilité.
    # C'est l'appariement qui le dit — la différence de médianes annonçait un gain.
    v("la forme EN SERVICE ne tranche PAS contre ne pas bouger",
      not m["le_raccrochage_en_service_bat_ne_pas_bouger"],
      str(m["variante_deployee"]["contre_sans_bouger"]))
    v("... alors que la meilleure forme, elle, tranche sur les DEUX comparaisons",
      m["meilleure_par_erreur"]["contre_sans_bouger"]["intervalle_um"][1] < 0
      and m["meilleure_par_erreur"]["contre_le_deploye"]["intervalle_um"][1] < 0,
      f"{m['meilleure_par_erreur']['contre_sans_bouger']} · "
      f"{m['meilleure_par_erreur']['contre_le_deploye']}")
    # ⛔ MÊME PARFAIT, LE GABARIT NE REND PRESQUE RIEN : la borne ne lit pas mieux et ne marche
    # pas mieux de façon décidable. C'est ce qui ferme la famille plutôt qu'une absence de gain.
    v("le gabarit PARFAIT ne lit pas mieux, et ne marche pas mieux de façon décidable",
      not m["le_gabarit_parfait_lirait_mieux"]
      and m["gabarit_borne"]["contre_le_deploye"]["intervalle_um"][1] >= 0,
      f"{m['paires_ou_la_borne_lit_mieux']}/{m['paires']} pas · "
      f"{m['gabarit_borne']['contre_le_deploye']}")
    # ⚠⚠ ET LA LIMITE EST COMPTÉE : élargir la boîte plafonne à huit pas, donc ce qui borne la
    # campagne n'est pas la fenêtre mais le nombre de spires segmentées.
    v("élargir la boîte plafonne, donc la limite n'est pas la fenêtre",
      max(x["pas_complets"] for x in m["pas_par_cote"])
      == m["pas_par_cote"][-1]["pas_complets"]
      and m["pas_par_cote"][-1]["pas_complets"] < 2 * m["paires"],
      str([(int(x["cote_voxels"]), x["pas_complets"]) for x in m["pas_par_cote"]]))
    # ⚠⚠⚠ LE REMÈDE MESURÉ PUIS REFUSÉ. Écrire « il suffirait de recaler l'amplitude » sans
    # l'avoir mesuré hors échantillon serait publier une piste comme un résultat.
    v("recaler l'amplitude par un facteur unique NE marche pas, hors échantillon",
      not m["le_recalage_de_la_forme_en_service_ameliore"] and m["gain_du_recalage_um"] < 0,
      f"{m['gain_du_recalage_um']} µm, amplitude "
      f"{m['variante_deployee']['amplitude_relative']}×")
    v("un verdict n'est rendu que si la médiane et le compte par pas s'accordent",
      (not m["une_autre_forme_lit_mieux"]
       or m["paires_ou_la_meilleure_lit_mieux"] > m["paires"] / 2)
      and (not m["une_autre_forme_marche_mieux"]
           or m["paires_ou_la_meilleure_marche_mieux"] > m["paires"] / 2),
      f"lit {m['paires_ou_la_meilleure_lit_mieux']}/{m['paires']} · "
      f"marche {m['paires_ou_la_meilleure_marche_mieux']}/{m['paires']}")

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les formes sont dessinées", r["variantes"] == m["variantes_mesurees"],
          str(r["variantes"]))
        trop = [(t, w) for t, w in r["legendes"] if w > r["panneau"] - 12]
        v("aucune ligne de légende ne déborde de son panneau", not trop,
          str(trop) if trop else f"la plus large fait {max(w for _, w in r['legendes'])} px")
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · ce que chaque forme lit, et ce que son MELANGE lit deja",
                      "B · ce que chaque forme COUTE (erreur de marche)"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < r["panneau"],
              f"{pt_.getbbox(titre)[2]} px pour {r['panneau']}")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "75_le_gabarit_lu_ailleurs.png")
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
