#!/usr/bin/env python3
"""Cinq objets ont des fibres, un seul a des spires, et ce n'est pas le meme.

⚠⚠ POURQUOI CETTE FIGURE EXISTE. Six tranches ont ferme les portes de la lecture, et il ne
restait qu'une piste : faire lire au raccrochage une ORIENTATION plutot qu'une intensite. Elle se
decide par une question de donnee, pas de methode — et cette question se pose a TOUTES les
sources, parce que ce depot a deja ete mordu trois fois pour avoir interroge une seule vue du
corpus et conclu sur le corpus.

⭐⭐⭐ Le panneau A donne la reponse : les deux ensembles sont DISJOINTS. Les cinq objets qui
publient un champ de fibres ne publient pas de spires, et le seul qui publie des spires n'a pas de
fibres. La voie de l'orientation est donc fermee par la DONNEE.

⚠⚠ Et le panneau B porte le fait de methode : les deux serveurs ne partagent AUCUN mot de
vocabulaire. Demander a l'un ce que l'autre range est une erreur de categorie — la premiere
version de cette mesure l'a commise et rapportait trente-huit absences qui etaient des erreurs
d'adresse.

Usage :
    uv run python src/figures/figure_ou_vit_le_champ_de_fibres.py --verifier
    uv run python src/figures/figure_ou_vit_le_champ_de_fibres.py \\
        --sortie docs/images/75_ou_vit_le_champ_de_fibres.png
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
MESURE = RACINE / "docs" / "mesures" / "ou_vit_le_champ_de_fibres.json"

FOND = (255, 255, 255)
TEXTE = (25, 25, 25)
DISCRET = (120, 120, 120)
AMBRE = (185, 110, 25)
BLEU = (54, 88, 132)
VERT = (76, 122, 84)
ROUGE = (188, 68, 52)
PALE = (238, 233, 224)
CADRE = (200, 200, 200)


def prose(m: dict) -> list[str]:
    return [
        f"{m['objets']} objets interroges sur DEUX sources : le bucket open-data et le serveur "
        f"de donnees, ce dernier dans ses DEUX arborescences ({', '.join(m['layouts'])}). la "
        f"question est de donnee, pas de methode : un champ d'orientation ne sert a cette "
        f"campagne que sur un objet qui publie AUSSI des spires, puisque c'est sur elles que la "
        "marche s'appuie et entre elles que l'erreur se mesure.",
        f"⚠⚠ les deux ensembles sont DISJOINTS. {len(m['objets_avec_fibres'])} objets publient un "
        f"champ de fibres — {', '.join(m['objets_avec_fibres'])} — et "
        f"{len(m['objets_avec_spires'])} publie des spires : {', '.join(m['objets_avec_spires'])}. "
        f"l'intersection est VIDE, donc la voie de l'orientation est fermee par la DONNEE et non "
        "par la methode.",
        f"⚠⚠ et le panneau B porte un fait de methode. le bucket range sous "
        f"representations/predictions/<genre> ({', '.join(m['genres_du_bucket'])}) ; le serveur "
        f"range sous {', '.join(m['dossiers_du_serveur'][:6])}… ⚠ comparer ces deux listes "
        "serait comparer deux ETAGES de l'arbre, ce qui ne peut que rendre « aucun mot commun » "
        "et ne dit rien.",
        f"⚠⚠ la question posee au MEME niveau : {len(m['objets_comparables'])} objet du corpus a "
        f"un dossier representations/ sur le serveur ({', '.join(m['objets_comparables'])}), et "
        f"il n'y a AUCUN etage predictions/ dessous. l'absence de fibres sur le serveur parle "
        "donc de son RANGEMENT, pas du corpus — et c'est le bucket qui repond a la question des "
        "fibres.",
        f"⚠⚠⚠ la premiere version de cette mesure l'a commise : elle demandait a tous les objets "
        f"l'adresse fragments/<objet>, y compris aux rouleaux, qui vivent sous "
        f"full-scrolls/<Scroll>/<objet>.volpkg. elle rapportait trente-huit desaccords sur "
        "trente-huit — un artefact de construction d'URL presente comme un fait sur le corpus, "
        "c'est-a-dire exactement le mode de panne que ce fichier existe pour eviter.",
        f"⚠ portee : {m['portee']}. {len(m['objets_absents_du_serveur'])} objets sur "
        f"{m['objets']} n'ont pas d'adresse connue sur le serveur, ce qui ne dit rien de leur "
        "existence ailleurs.",
    ]


def ensembles(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, moyen,
              legende: str) -> list:
    """Les deux ensembles et leur intersection, avec les noms plutôt que des comptes.

    ⚠⚠ LES NOMS SONT ÉCRITS, PAS COMPTÉS. « 5 et 1, intersection vide » se lit comme une
    statistique ; les noms rendent le fait vérifiable d'un coup d'œil — et c'est le genre de
    fait qu'on va rouvrir dans six mois pour demander « et celui-là ? ».
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    demi = pw // 2
    art.rectangle([x0 + 14, y0 + 30, x0 + demi - 10, y0 + ph - 40], fill=PALE)
    art.rectangle([x0 + demi + 10, y0 + 30, x0 + pw - 14, y0 + ph - 40], fill=PALE)
    art.text((x0 + 22, y0 + 38), "champ de FIBRES", fill=AMBRE, font=moyen)
    art.text((x0 + demi + 18, y0 + 38), "des SPIRES", fill=BLEU, font=moyen)
    noms = []
    for i, nom in enumerate(m["objets_avec_fibres"]):
        noms.append(nom)
        art.text((x0 + 26, y0 + 62 + 18 * i), nom, fill=TEXTE, font=petit)
    for i, nom in enumerate(m["objets_avec_spires"]):
        noms.append(nom)
        art.text((x0 + demi + 22, y0 + 62 + 18 * i), nom, fill=TEXTE, font=petit)
    art.line([x0 + demi, y0 + 30, x0 + demi, y0 + ph - 40], fill=CADRE)
    milieu = "INTERSECTION VIDE" if not m["objets_avec_les_deux"] else ", ".join(
        m["objets_avec_les_deux"])
    coul = ROUGE if not m["objets_avec_les_deux"] else VERT
    art.text((x0 + demi - moyen.getbbox(milieu)[2] // 2, y0 + ph - 32), milieu,
             fill=coul, font=moyen)
    return noms


def vocabulaires(art, x0: int, y0: int, pw: int, ph: int, m: dict, petit, moyen,
                 legende: str) -> list:
    """Les deux vocabulaires côte à côte, et le vide entre eux."""
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=CADRE)
    art.text((x0 + 8, y0 + 6), legende, fill=DISCRET, font=petit)
    demi = pw // 2
    art.text((x0 + 22, y0 + 34), "le BUCKET range sous", fill=VERT, font=moyen)
    art.text((x0 + demi + 18, y0 + 34), "le SERVEUR range sous", fill=AMBRE, font=moyen)
    noms = []
    for i, nom in enumerate(m["genres_du_bucket"]):
        noms.append(nom)
        art.text((x0 + 26, y0 + 58 + 17 * i), nom, fill=TEXTE, font=petit)
    for i, nom in enumerate(m["dossiers_du_serveur"][:12]):
        noms.append(nom)
        art.text((x0 + demi + 22, y0 + 58 + 17 * i), nom, fill=TEXTE, font=petit)
    art.line([x0 + demi, y0 + 30, x0 + demi, y0 + ph - 34], fill=CADRE)
    # ⚠⚠⚠ LA PHRASE DU BAS DIT LE FAIT PRÉCIS, PAS LE FAIT TRIVIAL. Comparer les genres du
    # bucket aux dossiers de premier niveau du serveur ne peut que rendre « aucun mot commun » :
    # ce sont deux étages différents de l'arbre. Ce qui se demande vraiment est si le serveur a
    # lui aussi un étage `predictions/`, et la réponse est mesurée.
    dit = ("le serveur n'a AUCUN etage predictions/"
           if not m["le_serveur_a_un_etage_predictions"]
           else "genres du serveur : " + ", ".join(m["genres_du_serveur"]))
    art.text((x0 + 22, y0 + ph - 26), dit,
             fill=ROUGE if not m["le_serveur_a_un_etage_predictions"] else VERT, font=moyen)
    return noms


def dessiner(m: dict, sortie: Path) -> dict:
    from PIL import Image, ImageDraw

    gros, moyen, petit = police(17, 13, 11)
    marge, pw, ecart = 40, 440, 46
    largeur_utile = pw * 2 + ecart
    for coupe in (128, 120, 112, 104, 96, 88):
        lignes = couper(prose(m), coupe)
        if max(moyen.getbbox(x)[2] for x in lignes) <= largeur_utile:
            break
    ph = 90 + 18 * max(len(m["objets_avec_fibres"]), 12)
    L = marge * 2 + pw * 2 + ecart
    H = 96 + ph + 42 + len(lignes) * 19
    toile = Image.new("RGB", (L, H), FOND)
    art = ImageDraw.Draw(toile)
    art.text((marge, 18), "Les fibres et les spires ne sont pas sur le meme objet",
             fill=TEXTE, font=gros)
    art.text((marge, 42),
             f"{m['objets']} objets · deux sources · deux arborescences",
             fill=DISCRET, font=moyen)
    art.text((marge, 76), "A · qui publie quoi, et l'intersection qui decide",
             fill=TEXTE, font=moyen)
    eta = ensembles(art, marge, 96, pw, ph, m, petit, moyen,
                    "les noms, pas les comptes : le fait doit se verifier d'un coup d'oeil")
    bx = marge + pw + ecart
    art.text((bx, 76), "B · les deux sources ne rangent pas pareil", fill=TEXTE, font=moyen)
    eta += vocabulaires(art, bx, 96, pw, ph, m, petit, moyen,
                        "demander a l'un ce que l'autre range est une erreur de categorie")
    debut = H - len(lignes) * 19 - 12
    for j, l in enumerate(lignes):
        art.text((marge, debut + j * 19), l, fill=TEXTE, font=moyen)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie)
    return {"objets": m["objets"], "etiquettes": eta,
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
    # ⭐⭐⭐ LE RÉSULTAT : les deux ensembles sont disjoints, donc la voie est fermée par la
    # donnée. Sans ce contrôle, la prose pourrait cesser de le dire.
    v("les deux ensembles sont DISJOINTS",
      not m["objets_avec_les_deux"] and not m["la_voie_de_lorientation_est_ouverte"],
      f"fibres {m['objets_avec_fibres']} · spires {m['objets_avec_spires']}")
    v("... et les deux ensembles sont non vides, sinon il n'y aurait rien à disjoindre",
      m["objets_avec_fibres"] and m["objets_avec_spires"])
    # ⚠⚠ LE FAIT DE MÉTHODE : les deux sources ne partagent aucun vocabulaire.
    # ⚠⚠⚠ LE FAIT PRÉCIS, PAS LE FAIT TRIVIAL : comparer les genres du bucket aux dossiers de
    # premier niveau du serveur compare deux étages de l'arbre. Ce qui se demande est si le
    # serveur a lui aussi un étage `predictions/`.
    v("la question est posée au MÊME niveau d'arbre, et le serveur n'a pas d'étage predictions/",
      m["objets_comparables"] and not m["le_serveur_a_un_etage_predictions"],
      f"comparables {m['objets_comparables']} · genres du serveur {m['genres_du_serveur']}")
    v("... donc c'est le bucket qui répond à la question des fibres",
      all(e["genres_du_bucket"] is not None for e in m["lignes"]
          if e["objet"] in m["objets_avec_fibres"]))
    # ⚠ Le serveur a bien été interrogé dans ses deux arborescences, sinon « absent du serveur »
    # ne voudrait rien dire.
    v("... et le serveur a été interrogé dans ses DEUX arborescences",
      len(m["layouts"]) == 2 and len(m["objets_absents_du_serveur"]) < m["objets"],
      f"{m['objets'] - len(m['objets_absents_du_serveur'])} objets trouvés sur "
      f"{m['objets']}")
    v("la portée de l'absence voyage avec la mesure",
      "sources interrogées" in m["portee"])

    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as d:
        r = dessiner(m, Path(d) / "t.png")
        debord = [(t[:40], w) for t, w in r["prose"] if w > r["largeur_utile"]]
        v("aucune ligne de prose ne déborde de l'image", not debord,
          str(debord) if debord else
          f"la plus large fait {max(w for _, w in r['prose'])} px pour {r['largeur_utile']}")
        v("toutes les étiquettes dessinées sont rendues par la police",
          prose_tracable(r["etiquettes"]), str(r["etiquettes"][:3]))
        v("les noms des deux ensembles sont tous dessinés",
          all(n in r["etiquettes"] for n in m["objets_avec_fibres"] + m["objets_avec_spires"]))
        from PIL import Image  # noqa: PLC0415

        img = Image.open(Path(d) / "t.png")
        v("l'image a du relief", img.convert("L").getextrema()[0] < 90)
        v("l'image est plus large que haute", img.width > img.height,
          f"{img.width}x{img.height}")
        _, _, pt_ = police(17, 13, 11)
        for titre in ("A · qui publie quoi, et l'intersection qui decide",
                      "B · les deux sources ne rangent pas pareil"):
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
                   default=RACINE / "docs" / "images" / "75_ou_vit_le_champ_de_fibres.png")
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
