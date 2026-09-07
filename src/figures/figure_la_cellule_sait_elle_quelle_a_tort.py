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

    def ec(nom: str, f: float) -> float:
        return next(v["ecart_median_um"] for v in m["verdicts"]
                    if v["marcheur"] == nom and abs(v["fraction"] - f) < 1e-9)

    ri, ra, li = par("rien"), par("raccroche"), par("rien_lisse")
    return [
        "le PLI d'une cellule est son ecart a la mediane de ses voisins : une quantite qu'un "
        "marcheur observe sur sa PROPRE nappe, sans jamais regarder la cible. ⚠⚠ aucun seuil "
        "n'est choisi ici : les cellules sont CLASSEES par leur pli et la fraction gardee est "
        "balayee, donc c'est la courbe entiere qui est livree et le point ou l'on se place "
        "appartient a l'auteur.",
        f"⚠⚠⚠ et la courbe ne veut rien dire sans son TEMOIN : garder la moitie d'un echantillon "
        f"AU HASARD deplace deja sa mediane. le panneau A superpose les deux a chaque fraction, "
        "et ce qui compte est l'ecart entre elles.",
        f"⚠⚠ PANNEAU A : le pli predit fortement chez le RACCROCHAGE — {ec('raccroche', 0.5):+.1f} "
        f"um a moitie gardee, {ec('raccroche', 0.1):+.1f} a un dixieme, et il gagne sur 8 bras "
        f"sur 8. il predit faiblement chez le PAS NORMAL ({ec('rien', 0.75):+.1f} um a trois "
        f"quarts) et PAS DU TOUT chez le pas normal lisse ({ec('rien_lisse', 0.35):+.1f} um, donc "
        "PIRE que le hasard).",
        "⚠⚠ et cette derniere ligne est le fait le plus interessant des trois : le lissage retire "
        "les plis, donc il retire AUSSI le signal qui permettait de savoir ou l'on se trompe. la "
        "meme operation qui ameliore la nappe aveugle le marcheur sur ses propres cellules — "
        "c'est un arbitrage a connaitre, pas un defaut.",
        f"⚠⚠⚠ PANNEAU B PORTE LE SEUL CHIFFRE ACTIONNABLE : « predire » et « sauver » sont deux "
        f"affirmations. un gain de cinquante micrometres sur une nappe a trois cents en est "
        f"encore a trois cents. un bras n'est SAUVE que s'il etait perdu a couverture pleine et "
        f"passe sous la demi-feuille en classant : le pas normal en sauve "
        f"{ri['bras_sauves']}/{ri['bras_perdus']}, le raccrochage {ra['bras_sauves']}/"
        f"{ra['bras_perdus']}, le pas normal lisse {li['bras_sauves']}/{li['bras_perdus']}.",
        f"⚠⚠ et le temoin au hasard n'en sauve AUCUN. mieux : la fraction qui suffit est "
        f"{ri['fractions_qui_sauvent'][0]:.0%} — jeter les dix pour cent de cellules les plus "
        "pliees. a comparer aux 45 pour cent que garde le marcheur qui refuse ses plis a un "
        "SEUIL : classer coute cinq fois moins de couverture pour le meme bras.",
    ]


def panneau_courbes(art, x0, y0, pw, ph, m, petit) -> None:
    """L'erreur mediane selon la fraction gardee, classee contre le hasard."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), "trait plein : classe par le pli · pointille : au hasard",
             fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + 19), "ecart median sur les bras, en um (negatif = le pli predit)",
             fill=DISCRET, font=petit)
    fr = m["fractions"]
    gauche, droite = x0 + 54, x0 + pw - 62
    base, sommet = y0 + ph - 40, y0 + 42
    tous = [v["ecart_median_um"] for v in m["verdicts"]]
    lo, hi = min(tous + [0.0]) * 1.15, max(tous + [0.0]) * 1.2 + 1.0

    def px(i: int) -> float:
        return gauche + (droite - gauche) * i / max(1, len(fr) - 1)

    def py(v: float) -> float:
        return base - (base - sommet) * (v - lo) / (hi - lo)

    art.rectangle([gauche - 8, py(0.0), droite + 8, base], fill=PALE)
    art.line([gauche - 8, py(0.0), droite + 8, py(0.0)], fill=TEXTE)
    art.text((gauche - 50, py(0.0) - 6), "   0", fill=TEXTE, font=petit)
    art.text((gauche + 4, py(0.0) + 4), "sous la ligne : le pli predit", fill=VERT, font=petit)
    for g in (-50, -25, 25):
        if lo < g < hi:
            art.text((gauche - 50, py(g) - 6), f"{g:>4}", fill=DISCRET, font=petit)
    for x in m["lignes"]:
        vs = [v for v in m["verdicts"] if v["marcheur"] == x["marcheur"]]
        if not vs:
            continue
        coul = COULEUR.get(x["marcheur"], DISCRET)
        pts = [(px(i), py(v["ecart_median_um"])) for i, v in enumerate(vs)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            art.line([ax, ay, bx, by], fill=coul, width=2)
        for cx, cy in pts:
            art.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=coul)
        art.text((droite + 6, pts[-1][1] - 6), x["marcheur"], fill=coul, font=petit)
    for i, f in enumerate(fr):
        art.text((px(i) - 12, base + 8), f"{f:.0%}", fill=DISCRET, font=petit)
    art.text((x0 + 8, y0 + ph - 18), "abscisse : la part de nappe GARDEE",
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
        art.rectangle([gauche, y + haut_l * 0.22, gauche + (droite - gauche)
                       * x["bras_perdus"] / plafond, y + haut_l * 0.68], outline=DISCRET)
        art.rectangle([gauche, y + haut_l * 0.30, gauche + (droite - gauche)
                       * x["bras_sauves"] / plafond, y + haut_l * 0.60], fill=coul)
        f = next((g for g in x["fractions_qui_sauvent"] if g is not None), None)
        art.text((droite + 6, y + haut_l / 2 - 6),
                 f"{x['bras_sauves']}/{x['bras_perdus']}"
                 + (f" a {f:.0%}" if f else ""), fill=coul, font=petit)
    art.text((x0 + 8, y0 + ph - 30), "contour : bras perdus · plein : bras sauves en classant",
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
    titres = ("A · classer par le pli contre jeter au hasard",
              "B · le seul chiffre actionnable : les bras SAUVES")
    for j, t in enumerate(titres):
        art.text((marge + j * (pw + ecart), 76), t, fill=TEXTE, font=moyen)
    panneau_courbes(art, marge, 104, pw, ph, m, petit)
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
      all(x["bras_sauves"] <= x["bras_perdus"] for x in m["lignes"]),
      str({x["marcheur"]: (x["bras_sauves"], x["bras_perdus"]) for x in m["lignes"]}))
    # ⚠⚠ ET LE TÉMOIN EST CE QUI REND LE COMPTE LISIBLE : s'il sauvait autant, le classement ne
    # servirait à rien et la figure annoncerait un gain qui vient de la réduction d'échantillon.
    v("... et le témoin au hasard est publié à côté",
      all("bras_sauves_au_hasard" in x for x in m["lignes"]),
      str({x["marcheur"]: x["bras_sauves_au_hasard"] for x in m["lignes"]}))
    # ⚠ LA FRACTION QUI SAUVE EST PUBLIÉE AVEC LE BRAS : « sauvé » sans « en gardant quoi » se
    # lirait comme un sauvetage gratuit.
    v("la fraction qu'il faut garder pour sauver un bras est publiée avec lui",
      all(len(x["fractions_qui_sauvent"]) == x["bras_perdus"] for x in m["lignes"]),
      str({x["marcheur"]: x["fractions_qui_sauvent"][:2] for x in m["lignes"]}))

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
