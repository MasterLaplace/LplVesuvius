#!/usr/bin/env python3
"""Verte partout, sauf là où le nombre se fabrique.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. « 67 modules sur 140 » se lit comme une dette de couverture
ordinaire, et ce n'en est pas une : ce ne sont pas des lignes qui manquent, c'est **la branche
que le point d'entrée prend en premier**. Le panneau A montre que la dette n'est pas répartie
au hasard — deux familles sur trois y sont, et celle qui publie le plus de mesures est celle
qui en couvre le moins.

⭐ Le panneau B nomme ce qui n'est jamais exercé, et c'est le nom qui rend le fait lisible :
`mesurer` dans dix-sept modules, `dessiner` dans dix. Ce sont exactement les deux fonctions
qui produisent ce que le dépôt publie — le nombre et l'image.

Usage :
    uv run python src/figures/figure_le_chemin_du_nombre_publie.py --verifier
    uv run python src/figures/figure_le_chemin_du_nombre_publie.py \\
        --sortie docs/images/80_le_chemin_du_nombre_publie.png
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
MESURE = RACINE / "docs" / "mesures" / "le_chemin_du_nombre_publie.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    tetes = sorted(m["tetes_de_chemin"].items(), key=lambda kv: -kv[1])[:4]
    pire = max(m["par_famille"].items(),
               key=lambda kv: (kv[1]["en_dette"] / kv[1]["publient"], kv[1]["publient"]))
    return [
        f"{m['modules_qui_publient']} modules publient une mesure ; "
        f"{m['modules_en_dette']} d'entre eux ({m['part_en_dette']:.0%}) ont une batterie qui "
        f"n'atteint jamais le chemin produisant le nombre publie. "
        f"{m['fonctions_non_couvertes']} fonctions au total.",
        "ce n'est pas de la couverture qui manque au milieu : c'est la fonction que `main` "
        "appelle EN PREMIER. la batterie teste les briques, jamais l'assemblage — et "
        "l'assemblage est ce qui produit le chiffre.",
        "les branches jamais exercees, par nom : "
        + ", ".join(f"{n} dans {c} module(s)" for n, c in tetes)
        + ". ce sont les deux verbes qui publient : l'un rend le nombre, l'autre l'image.",
        f"la dette n'est pas uniforme : {pire[0]} en porte "
        f"{pire[1]['en_dette']} sur {pire[1]['publient']}.",
        "⚠ ce que ce balayage ne dit PAS : qu'une fonction atteinte soit TESTEE. il dit "
        "qu'une batterie la traverse, pas qu'elle y verifie quoi que ce soit. prendre "
        "l'un pour l'autre ferait de cet instrument la mesure trop confiante qu'il traque.",
        "⚠ et le graphe ne suit que les appels PAR NOM : un appel indirect n'est pas vu, donc "
        "une fonction peut etre comptee dehors alors qu'elle tourne. l'erreur va dans le sens "
        "prudent — la dette est surestimee, jamais cachee.",
    ]


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    lignes = couper(prose(m), 128)
    marge, pw, ph, ecart = 40, 400, 250, 56
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 90 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Verte partout, sauf la ou le nombre se fabrique",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['modules_en_dette']} modules sur {m['modules_qui_publient']} qui publient "
             f"une mesure · {m['fonctions_non_couvertes']} fonctions hors de portee",
             fill=DISCRET, font=moyen)

    # ---------- A : la dette par famille ----------
    ax, ay = marge, 96
    art.text((ax, ay - 20), "A · par famille : couvert contre en dette", fill=TEXTE, font=moyen)
    art.rectangle([ax, ay, ax + pw, ay + ph], outline=CADRE)
    fam = sorted(m["par_famille"].items(), key=lambda kv: -kv[1]["publient"])
    top = max(d["publient"] for _, d in fam) * 1.2
    larg = pw / (len(fam) + 0.6)
    for k, (nom, d) in enumerate(fam):
        x0 = ax + larg * (k + 0.55)
        h_tot = d["publient"] / top * (ph - 46)
        h_det = d["en_dette"] / top * (ph - 46)
        art.rectangle([x0 - larg * 0.3, ay + ph - h_tot, x0 + larg * 0.3, ay + ph], fill=BLEU)
        art.rectangle([x0 - larg * 0.3, ay + ph - h_det, x0 + larg * 0.3, ay + ph], fill=AMBRE)
        # ⚠ Les noms de famille sont ALTERNÉS sur deux lignes : neuf étiquettes sur quatre
        # cents pixels se chevauchent, et deux noms superposés ne se lisent ni l'un ni l'autre.
        art.text((x0 - petit.getbbox(nom)[2] / 2, ay + ph + 3 + 15 * (k % 2)), nom,
                 fill=DISCRET, font=petit)
        art.text((x0 - 14, ay + ph - h_tot - 13), f"{d['en_dette']}/{d['publient']}",
                 fill=TEXTE, font=petit)
    art.text((ax + 6, ay + 6), "bleu : modules qui publient une mesure", fill=BLEU, font=petit)
    art.text((ax + 6, ay + 22), "ambre : ceux dont la batterie n'atteint pas ce chemin",
             fill=AMBRE, font=petit)

    # ---------- B : ce qui n'est jamais exerce, par nom ----------
    bx, by = marge + pw + ecart, 96
    art.text((bx, by - 20), "B · la branche jamais exercee, par son nom",
             fill=TEXTE, font=moyen)
    art.rectangle([bx, by, bx + pw, by + ph], outline=CADRE)
    tetes = sorted(m["tetes_de_chemin"].items(), key=lambda kv: -kv[1])[:9]
    tmax = tetes[0][1] * 1.25 if tetes else 1
    haut = (ph - 40) / max(len(tetes), 1)
    for k, (nom, cpt) in enumerate(tetes):
        y0 = by + 30 + haut * k
        w = cpt / tmax * (pw - 150)
        coul = AMBRE if nom in ("mesurer", "dessiner") else BLEU
        art.rectangle([bx + 118, y0, bx + 118 + w, y0 + haut * 0.62], fill=coul)
        art.text((bx + 10, y0), nom[:16], fill=TEXTE, font=petit)
        art.text((bx + 124 + w, y0), str(cpt), fill=TEXTE, font=petit)
    art.text((bx + 6, by + 6),
             "en ambre les deux verbes qui PUBLIENT : le nombre, et l'image",
             fill=AMBRE, font=petit)
    art.text((bx + 6, by + ph + 3),
             "abscisse : nombre de modules ou cette branche n'est jamais atteinte",
             fill=DISCRET, font=petit)

    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    # ⚠⚠ Les bornes des étiquettes sont RENDUES pour que la batterie puisse vérifier qu'elles
    # ne se chevauchent pas : un contrôle qui relirait l'image ne saurait pas dire lequel des
    # deux noms superposés est dessous.
    bornes = [(ax + larg * (k + 0.55) - petit.getbbox(n)[2] / 2,
               ax + larg * (k + 0.55) + petit.getbbox(n)[2] / 2, k % 2)
              for k, (n, _) in enumerate(fam)]
    return {"familles": len(fam), "tetes": len(tetes),
            "etiquettes": bornes, "sortie": str(sortie)}


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
    # ⚠⚠ LE FAIT QUE LA FIGURE PORTE, et il doit être vérifié ici plutôt qu'affirmé dans la
    # légende : la dette est réelle et elle n'est pas marginale.
    v("la dette existe et n'est pas marginale", m["modules_en_dette"] > 0
      and m["part_en_dette"] > 0.1, f"{m['modules_en_dette']}/{m['modules_qui_publient']}")
    # ⚠⚠⚠ ET LE NÉGATIF QUI EMPÊCHE DE LIRE « LE DÉPÔT NE TESTE RIEN » : une majorité de
    # modules atteint bien sa mesure. Sans lui, la figure raconterait un dépôt sans batteries.
    v("... mais la majorité des modules atteint bien sa mesure",
      m["part_en_dette"] < 0.5, f"{m['part_en_dette']}")
    # ⚠⚠ CE QUI REND LE PANNEAU B LISIBLE : les deux verbes qui publient dominent réellement
    # la liste. Si un jour ce n'est plus vrai, la légende ambre devient une décoration.
    tetes = sorted(m["tetes_de_chemin"].items(), key=lambda kv: -kv[1])
    v("les deux verbes qui publient sont en tête de la liste",
      {n for n, _ in tetes[:2]} == {"mesurer", "dessiner"}, str(tetes[:3]))
    v("... et `mesurer` est la branche la plus souvent laissée dehors",
      tetes[0][0] == "mesurer", f"{tetes[0][1]} modules")
    # ⚠ Le compte de fonctions ne peut pas être plus petit que le compte de modules : chaque
    # module en dette en porte au moins une. Un total plus bas signalerait un décompte cassé.
    v("le total de fonctions couvre au moins un par module en dette",
      m["fonctions_non_couvertes"] >= m["modules_en_dette"],
      f"{m['fonctions_non_couvertes']} pour {m['modules_en_dette']}")
    # ⚠⚠ LA SOMME DES FAMILLES DOIT ÊTRE LE TOTAL. Un module rangé dans aucune famille — ou
    # dans deux — passerait inaperçu dans le panneau A tout en gonflant le titre.
    v("les familles se somment au total, sans reste",
      sum(d["publient"] for d in m["par_famille"].values()) == m["modules_qui_publient"]
      and sum(d["en_dette"] for d in m["par_famille"].values()) == m["modules_en_dette"])
    # ⚠⚠ ET L'INSTRUMENT NE DOIT PAS SE RANGER DANS SA PROPRE LISTE : une mesure de dette
    # portée par un module en dette serait la panne qu'elle décrit.
    dedans = [e for e in m["lignes"] if e["fichier"].endswith("le_chemin_du_nombre_publie.py")]
    v("l'instrument lui-même n'est pas en dette",
      len(dedans) == 1 and not dedans[0]["en_dette"], str(dedans and dedans[0]["non_couvert"]))

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        v("toutes les familles sont dessinées", r["familles"] == len(m["par_famille"]))
        # ⚠⚠ Deux étiquettes de la MÊME ligne ne doivent pas se recouvrir. Comparer toutes les
        # paires plutôt que les voisines : c'est l'alternance qui rend les voisines innocentes,
        # et un nom assez long pour sauter par-dessus son voisin ne serait pas vu autrement.
        chevauche = [(a_, b_) for i, a_ in enumerate(r["etiquettes"])
                     for b_ in r["etiquettes"][i + 1:]
                     if a_[2] == b_[2] and a_[1] > b_[0] and b_[1] > a_[0]]
        v("aucune étiquette de famille n'en recouvre une autre",
          not chevauche, f"{len(chevauche)} chevauchement(s)")
        v("le panneau B porte des barres", r["tetes"] > 0, str(r["tetes"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        # ⚠⚠ UN TITRE DE PANNEAU QUI DÉBORDE SE LIT TRONQUÉ, DONC FAUX. Le dépôt l'a payé une
        # fois : « en sens contraire » pour « contraires », ce qui change la phrase.
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · par famille : couvert contre en dette",
                      "B · la branche jamais exercee, par son nom"):
            v(f"le titre « {titre[:14]}… » tient dans son panneau",
              pt_.getbbox(titre)[2] < 400, f"{pt_.getbbox(titre)[2]} px pour 400")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mesure", type=Path, default=MESURE)
    p.add_argument("--sortie", type=Path,
                   default=RACINE / "docs" / "images" / "80_le_chemin_du_nombre_publie.png")
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
