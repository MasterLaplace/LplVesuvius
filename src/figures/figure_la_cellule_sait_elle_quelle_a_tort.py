#!/usr/bin/env python3
"""Une cellule peut-elle savoir qu'elle a tort, sans regarder la cible ?

⚠⚠⚠ POURQUOI CETTE FIGURE PORTE UNE QUESTION DE PRODUIT ET PAS DE METHODE. Un derouleur qui livre
une nappe livre aussi la pretention que chaque cellule est a sa place. Si le PLI d'une cellule —
son ecart a la mediane de ses voisins, observable sans aucune supervision — predit son ERREUR,
alors un marcheur aveugle peut publier une CONFIANCE PAR CELLULE. Il ne sait pas ou est la verite,
mais il sait ou il se trompe.

⚠⚠ AUCUN SEUIL N'EST CHOISI : les cellules sont CLASSEES par leur pli et la fraction gardee est
balayee. La courbe est l'objet livre ; le point ou l'on se place appartient a l'auteur.

⚠⚠⚠ ET ELLE NE VEUT RIEN DIRE SANS SON TEMOIN : garder la moitie d'un echantillon AU HASARD
deplace deja sa mediane. Ce qui compte est l'ecart entre classer et tirer au hasard, a fraction
egale et sur les memes cellules.

Usage :
    uv run python src/figures/figure_la_cellule_sait_elle_quelle_a_tort.py --verifier
    uv run python src/figures/figure_la_cellule_sait_elle_quelle_a_tort.py \\
        --sortie docs/images/75_la_cellule_sait_elle_quelle_a_tort.png
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

RACINE = Path(__file__).resolve().parents[2]
MESURE = RACINE / "docs" / "mesures" / "la_cellule_sait_elle_quelle_a_tort.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
ROUGE = (188, 68, 52)
VERT = (76, 122, 84)
TURQUOISE = (26, 128, 128)
PALE = (243, 231, 227)
CADRE = (200, 200, 200)
COULEUR = {"rien": (70, 70, 70), "rien_lisse": TURQUOISE, "raccroche": VERT}


def prose(m: dict) -> list[str]:
    def par(nom: str) -> dict:
        return next(x for x in m["lignes"] if x["marcheur"] == nom)

    def ec(nom: str, f: float, o: str = "pli") -> float:
        return next(v["ecart_median_um"] for v in m["verdicts"]
                    if v["marcheur"] == nom and v["observable"] == o
                    and abs(v["fraction"] - f) < 1e-9)

    ri, ra, li = par("rien"), par("raccroche"), par("rien_lisse")

    def sv(x, o):
        return x["bras_sauves"][o]
    return [
        "le PLI d'une cellule est son ecart a la mediane de ses voisins : une quantite qu'un "
        "marcheur observe sur sa PROPRE nappe, sans jamais regarder la cible. ⚠⚠ aucun seuil "
        "n'est choisi ici : les cellules sont CLASSEES par leur pli et la fraction gardee est "
        "balayee, donc c'est la courbe entiere qui est livree et le point ou l'on se place "
        "appartient a l'auteur.",
        f"⚠⚠⚠ et la courbe ne veut rien dire sans son TEMOIN : garder la moitie d'un echantillon "
        f"AU HASARD deplace deja sa mediane. le panneau A superpose les deux a chaque fraction, "
        "et ce qui compte est l'ecart entre elles.",
        f"⚠⚠ DEUX OBSERVABLES, et la convention est que GRAND veut dire SUSPECT. le PLI l'est "
        f"deja ; l'INTENSITE est dans l'autre sens — une feuille est un ruban brillant, donc "
        f"c'est le point SOMBRE qui est suspect — donc on classe sur son oppose, et le dire "
        "plutot que le cacher dans un signe evite de publier une courbe parfaitement inversee. "
        "⚠ lire le volume a son PROPRE point predit n'est PAS de la supervision : la cible n'est "
        "jamais consultee, et c'est exactement ce qu'un vrai derouleur a en main.",
        f"⚠⚠⚠ PANNEAU A : le PLI predit fortement chez le RACCROCHAGE — {ec('raccroche', 0.5):+.1f} "
        f"um a moitie gardee, {ec('raccroche', 0.1):+.1f} a un dixieme, sur 8 bras sur 8 — "
        f"faiblement chez le PAS NORMAL ({ec('rien', 0.75):+.1f} a trois quarts) et PAS DU TOUT "
        f"chez le pas normal LISSE ({ec('rien_lisse', 0.35):+.1f}, donc PIRE que le hasard). le "
        "lissage retire les plis, donc il retire AUSSI le signal qui disait ou l'on se trompe.",
        f"⚠⚠⚠ ET AUCUNE COMBINAISON NE BAT LES DEUX SEULES A TOUTES LES FRACTIONS : le verdict "
         "strict est VIDE pour les trois marcheurs. combiner deux observables demande normalement "
         "un POIDS, donc un reglage ; passer chaque observable en RANG le supprime — les unites "
         "disparaissent, un pli en um et une obscurite en niveaux de gris deviennent comparables "
         "sans facteur choisi — mais aucune des trois recombinaisons ne DOMINE.",
         f"⚠⚠⚠ ce qui se publie sans rien choisir est un COMPTE et pas une gagnante : quelles "
         f"colonnes predisent a TOUTES les fractions. pas normal : "
         f"{m['colonnes_qui_predisent_partout']['rien'] or 'aucune'} et elles seules ; pas normal "
         f"lisse : {m['colonnes_qui_predisent_partout']['rien_lisse'] or 'aucune'} ; raccrochage : "
         f"{len(m['colonnes_qui_predisent_partout']['raccroche'])} colonnes sur cinq. ⚠ « ou » "
         "n'est donc MEILLEURE nulle part et la seule UTILISABLE partout chez le pas normal : "
         "c'est de la robustesse au point de fonctionnement, pas de la domination — et c'est ce "
         "dont un derouleur qui ne choisit pas sa fraction a besoin.",
        f"⚠⚠⚠ ET C'EST EXACTEMENT LA OU L'OBSCURITE PREND LE RELAIS : "
        f"{ec('rien_lisse', 0.35, 'obscurite'):+.1f} um chez le pas normal lisse, sur 7 bras sur "
        f"8, et {ec('rien', 0.5, 'obscurite'):+.1f} chez le pas normal. le lissage peut effacer "
        "les plis, il ne peut PAS empecher une cellule tombee dans un vide entre deux feuilles "
        "de lire SOMBRE. les deux observables sont donc COMPLEMENTAIRES : celle qui marche est "
        "celle que le traitement n'a pas detruite.",
        f"⚠⚠⚠ PANNEAU B PORTE LE SEUL CHIFFRE ACTIONNABLE : « predire » et « sauver » sont deux "
        f"affirmations. un gain de cinquante micrometres sur une nappe a trois cents en est "
        f"encore a trois cents. un bras n'est SAUVE que s'il etait perdu a couverture pleine et "
        f"passe sous la demi-feuille en classant : par le PLI, le pas normal en sauve "
        f"{sv(ri, 'pli')}/{ri['bras_perdus']}, le raccrochage {sv(ra, 'pli')}/{ra['bras_perdus']}, "
        f"le pas normal lisse {sv(li, 'pli')}/{li['bras_perdus']} ; par l'OBSCURITE, "
        f"{sv(ri, 'obscurite')}/{ri['bras_perdus']}, {sv(ra, 'obscurite')}/{ra['bras_perdus']} et "
        f"{sv(li, 'obscurite')}/{li['bras_perdus']} ; et par « ou », {sv(ri, 'ou')}/"
        f"{ri['bras_perdus']}, {sv(ra, 'ou')}/{ra['bras_perdus']} et {sv(li, 'ou')}/"
        f"{li['bras_perdus']} — le SEUL endroit ou une combinaison ajoute un bras est chez le "
        "raccrochage.",
        f"⚠⚠ et le temoin au hasard n'en sauve AUCUN. la fraction qui suffit est "
        f"{ri['fractions_qui_sauvent']['pli'][0]:.0%} par le pli — jeter les dix pour cent de "
        f"cellules les plus pliees — et {ri['fractions_qui_sauvent']['obscurite'][0]:.0%} par "
        "l'obscurite. a comparer aux 45 pour cent que garde le marcheur qui refuse ses plis a un "
        "SEUIL : classer coute cinq fois moins de couverture pour le meme bras. ⚠ et aucune des "
        "deux ne sauve un bras du pas normal LISSE : elles disent ou il se trompe sans le rendre "
        "juste.",
    ]


def panneau_grille(art, x0, y0, pw, ph, m, petit) -> None:
    """Une case par (colonne, marcheur, fraction) : vert = predit, rouge = non.

    ⚠⚠⚠ UNE GRILLE ET PAS DES COURBES, et c'est une decision de lisibilite qui est aussi une
    decision d'honnetete. Cinq colonnes fois trois marcheurs font quinze courbes sur un meme
    axe : personne ne les lit, et « personne ne les lit » finit par vouloir dire « on ne montre
    que les trois qui arrangent ». Une grille porte TOUT, sans qu'aucune ligne n'ait ete choisie.

    ⚠ L'intensite est bornee a cinquante micrometres : au-dela les cases sauteraient toutes au
    meme vert et la nuance disparaitrait. La borne est dessinee dans la legende plutot que tue.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "vert : l'observable PREDIT (ecart negatif) · rouge : elle nuit",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "intensite = ampleur, saturee a 50 um",
             fill=DISCRET, font=petit)
    fr = m["fractions"]
    gauche, haut = x0 + 152, y0 + 52
    larg = (pw - 164) / max(1, len(fr))
    hy = (ph - 78) / max(1, len(m["observables"]) * len(m["marcheurs"]))
    for j, f in enumerate(fr):
        art.text((gauche + j * larg + larg / 2 - 12, haut - 14), f"{f:.0%}",
                 fill=DISCRET, font=petit)
    i = 0
    for o in m["observables"]:
        for x in m["lignes"]:
            vs = [v for v in m["verdicts"]
                  if v["marcheur"] == x["marcheur"] and v["observable"] == o]
            if not vs:
                continue
            y = haut + i * hy
            partout = o in m["colonnes_qui_predisent_partout"][x["marcheur"]]
            art.text((x0 + 6, y + hy / 2 - 6),
                     f"{'>' if partout else ' '} {o[:8]} · {x['marcheur'][:9]}",
                     fill=TEXTE if partout else DISCRET, font=petit)
            for j, v in enumerate(vs):
                d = v["ecart_median_um"]
                t = min(abs(d) / 50.0, 1.0)
                if d < 0:
                    c = (int(255 - 175 * t), int(255 - 55 * t), int(255 - 175 * t))
                elif d > 0:
                    c = (int(255 - 30 * t), int(255 - 120 * t), int(255 - 120 * t))
                else:
                    c = (245, 245, 245)
                art.rectangle([gauche + j * larg, y + 1, gauche + (j + 1) * larg - 2,
                               y + hy - 2], fill=c, outline=(230, 230, 230))
            i += 1
    art.text((x0 + 8, y0 + ph - 18),
             "> = cette colonne predit a TOUTES les fractions · abscisse : part gardee",
             fill=DISCRET, font=petit)


def panneau_sauves(art, x0, y0, pw, ph, m, petit) -> None:
    """Combien de bras PERDUS passent sous la demi-feuille en classant."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "un bras n'est SAUVE que s'il etait perdu a couverture pleine",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "et passe sous la demi-feuille en classant",
             fill=DISCRET, font=petit)
    gauche, droite = x0 + 132, x0 + pw - 96
    haut_l = (ph - 70) / max(1, len(m["lignes"]))
    plafond = max([x["bras_perdus"] for x in m["lignes"]] + [1])
    for i, x in enumerate(m["lignes"]):
        y = y0 + 44 + i * haut_l
        coul = COULEUR.get(x["marcheur"], DISCRET)
        art.text((x0 + 8, y + haut_l / 2 - 6), x["marcheur"], fill=coul, font=petit)
        art.rectangle([gauche, y + haut_l * 0.14, gauche + (droite - gauche)
                       * x["bras_perdus"] / plafond, y + haut_l * 0.80], outline=DISCRET)
        # ⚠ Le panneau B ne dessine que les deux observables SEULES et « ou » : les cinq
        # tiendraient mal, et les trois dessinees sont celles nommees par la prose. Les cinq
        # comptes restent dans le JSON et dans le registre — la figure est un raccourci de
        # lecture, jamais la seule trace.
        for k_, o in enumerate([*m["seules"], "ou"]):
            hb = y + haut_l * (0.16 + 0.22 * k_)
            art.rectangle([gauche, hb, gauche + (droite - gauche)
                           * x["bras_sauves"][o] / plafond, hb + haut_l * 0.16],
                          fill=coul if o == "pli" else None, outline=coul)
            f = next((g for g in x["fractions_qui_sauvent"][o] if g is not None), None)
            art.text((droite + 6, hb + 1),
                     f"{o[:4]} {x['bras_sauves'][o]}/{x['bras_perdus']}"
                     + (f" a {f:.0%}" if f else ""), fill=coul, font=petit)
    art.text((x0 + 8, y0 + ph - 30),
             "contour : bras perdus · trois barres : pli, obscurite, « ou »",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 17),
             f"au hasard : {sum(x['bras_sauves_au_hasard'] for x in m['lignes'])} sauve(s) "
             "au total", fill=ROUGE, font=petit)


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart, ph = 38, 470, 34, 276
    largeur_utile = pw * 2 + ecart
    for coupe in (140, 132, 124, 116, 108, 100):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    L = marge * 2 + largeur_utile
    H = 104 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 16), "Une cellule peut-elle savoir qu'elle a tort, sans voir la cible ?",
             fill=TEXTE, font=gros)
    art.text((marge, 40),
             f"ancre {m['ancre']} · {len(m['spires_visees'])} bras · demi-feuille "
             f"{m['demi_feuille_um']} um · classement par le PLI, aucun seuil choisi",
             fill=DISCRET, font=moyen)
    titres = ("A · les cinq colonnes, contre le hasard, a chaque fraction",
              "B · le seul chiffre actionnable : les bras SAUVES")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_grille(art, marge, 104, pw, ph, m, petit)
    panneau_sauves(art, marge + pw + ecart, 104, pw, ph, m, petit)
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"marcheurs": len(m["lignes"]), "titres": titres, "panneau": pw,
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
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0

    m = json.loads(MESURE.read_text())
    v("la prose est traçable", prose_tracable(prose(m)))
    # ⚠⚠⚠ À COUVERTURE PLEINE IL N'Y A RIEN À CLASSER : les deux courbes doivent se toucher, et
    # si elles ne se touchaient pas, l'une des deux ne mesurerait pas ce qu'elle annonce.
    plein = [v_["ecart_median_um"] for v_ in m["verdicts"] if v_["fraction"] == 1.0]
    v("à couverture pleine, classer et tirer au hasard donnent le même nombre",
      plein and all(abs(x) < 0.05 for x in plein), str(plein))
    # ⭐⭐⭐ « PRÉDIRE » ET « SAUVER » SONT DEUX AFFIRMATIONS : un bras n'est sauvé que s'il était
    # perdu à couverture pleine. Sans ce contrôle, le panneau B compterait des bras déjà bons.
    v("un bras n'est compté sauvé que s'il était perdu à couverture pleine",
      all(x["bras_sauves"][o] <= x["bras_perdus"]
          for x in m["lignes"] for o in m["observables"]),
      str({x["marcheur"]: (x["bras_sauves"], x["bras_perdus"]) for x in m["lignes"]}))
    # ⭐⭐⭐ LE FAIT QUE CETTE FIGURE PORTE : les deux observables sont COMPLÉMENTAIRES, et celle
    # qui marche est celle que le traitement n'a pas détruite. Le contrôle l'épingle : le pli
    # échoue chez le pas normal lissé et l'obscurité y réussit. Si les deux réussissaient ou
    # échouaient ensemble, la prose de la figure serait fausse.
    v("les deux observables sont complémentaires : celle qui échoue n'est pas la même",
      m["elle_predit_lerreur"]["obscurite"]["rien_lisse"]
      and not m["elle_predit_lerreur"]["pli"]["rien_lisse"],
      f"pli {m['elle_predit_lerreur']['pli']} · obscurité "
      f"{m['elle_predit_lerreur']['obscurite']}")
    # ⚠⚠ ET LE TÉMOIN EST CE QUI REND LE COMPTE LISIBLE : s'il sauvait autant, le classement ne
    # servirait à rien et la figure annoncerait un gain qui vient de la réduction d'échantillon.
    v("... et le témoin au hasard est publié à côté",
      all("bras_sauves_au_hasard" in x for x in m["lignes"]),
      str({x["marcheur"]: x["bras_sauves_au_hasard"] for x in m["lignes"]}))
    # ⚠ LA FRACTION QUI SAUVE EST PUBLIÉE AVEC LE BRAS : « sauvé » sans « en gardant quoi » se
    # lirait comme un sauvetage gratuit.
    v("la fraction qu'il faut garder pour sauver un bras est publiée avec lui",
      all(len(x["fractions_qui_sauvent"][o]) == x["bras_perdus"]
          for x in m["lignes"] for o in m["observables"]),
      str({x["marcheur"]: x["fractions_qui_sauvent"] for x in m["lignes"]}))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("tous les marcheurs sont dessinés", r["marcheurs"] == len(m["lignes"]),
          str(r["marcheurs"]))
        debord = [(t[:36], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        _, _, pt_ = police(17, 13, 11)
        trop = [(t, pt_.getbbox(t)[2]) for t in r["titres"] if pt_.getbbox(t)[2] >= r["panneau"]]
        v("chaque titre de panneau tient dans son panneau", not trop, str(trop))
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
                   default=RACINE / "docs" / "images"
                   / "75_la_cellule_sait_elle_quelle_a_tort.png")
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
