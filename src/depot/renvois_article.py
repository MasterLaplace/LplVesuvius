#!/usr/bin/env python3
"""Les renvois « Section N.M » de l'article disent-ils la bonne section ?

⚠⚠ **Un renvoi faux est pire qu'un renvoi absent.** Typst numérote les sections tout seul,
mais le texte d'un `#link` est écrit à la main : insérer une sous-section décale la
numérotation sans toucher un seul de ces textes, et rien ne le signale. Mesuré le
2026-08-23 sur l'article de ce dépôt : **cinq renvois sur seize** pointaient ailleurs,
dont un qui envoyait le lecteur du choix de graine (5.3) vers le témoin négatif (6.4) — une
autre section, un autre chapitre, et un texte parfaitement crédible.

⭐ Le remède n'est pas de relire : c'est de **recalculer** la numérotation depuis les titres
et de comparer. La numérotation est une fonction du document, donc elle se dérive.

⚠ Ce fichier ne réécrit rien. Un renvoi faux peut vouloir dire « le numéro a vieilli » *ou*
« le lien vise la mauvaise ancre », et seul l'auteur sait lequel.

Reproduire :

    python3 src/depot/renvois_article.py docs/article/article.typ
    python3 src/depot/renvois_article.py --verifier
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ⚠⚠ Un titre Typst est un `=` en DEBUT DE LIGNE suivi d'une espace. C'est `TITRE.match`
# qui l'impose, ligne par ligne -- le `^` du motif est redondant avec lui, et une sonde l'a
# montre : le retirer laisse la batterie verte. Ce qui la fait echouer, et donc ce qui
# protege reellement, c'est de passer a `search` : un `=` de formule au fil du texte serait
# alors pris pour un titre et decalerait toute la numerotation.
TITRE = re.compile(r"^(=+)\s+(.*)$")
ANCRE = re.compile(r"<([a-zA-Z][\w:-]*)>\s*$")
RENVOI = re.compile(r"#link\(<([a-zA-Z][\w:-]*)>\)\[\s*(?:Section|Sections)\s+([0-9.]+)\s*\]")


def numeroter(texte: str) -> dict[str, str]:
    """L'étiquette de chaque ancre de titre — « 3.6 », « 5 » — telle que Typst la rendra.

    ⚠ Seules les ancres posées **sur un titre** comptent. Une ancre de figure ou de tableau
    porte un numéro d'une autre suite (`fig:`, `tab:`), et lui attribuer un numéro de
    section ferait un contrôle qui se trompe de grandeur.
    """
    compteurs: list[int] = []
    out: dict[str, str] = {}
    for ligne in texte.splitlines():
        m = TITRE.match(ligne)
        if not m:
            continue
        niveau = len(m.group(1))
        while len(compteurs) < niveau:
            compteurs.append(0)
        del compteurs[niveau:]
        compteurs[niveau - 1] += 1
        a = ANCRE.search(m.group(2))
        if a:
            out[a.group(1)] = ".".join(str(c) for c in compteurs)
    return out


def verifier_renvois(texte: str) -> list[dict]:
    """Chaque renvoi, avec le numéro écrit et le numéro calculé."""
    nums = numeroter(texte)
    out = []
    for m in RENVOI.finditer(texte):
        ancre, ecrit = m.group(1), m.group(2)
        attendu = nums.get(ancre)
        out.append({"ancre": ancre, "ecrit": ecrit, "attendu": attendu,
                    "juste": (attendu is not None and ecrit == attendu),
                    "ancre_inconnue": attendu is None})
    return out


PAGES_PDF = re.compile(rb"/Type\s*/Pages\b")
COMPTE = re.compile(rb"/Count\s+(\d+)")
PAGES_README = re.compile(r"(\d+)\s+pages")


def pages_du_pdf(octets: bytes) -> int | None:
    """Le nombre de pages d'un PDF, ou None s'il n'en déclare aucun.

    ⚠⚠ **Compter les objets `/Type /Page` est faux**, et je l'ai fait avant de vérifier :
    sur l'article de ce dépôt la méthode rend *42* pour un document de *21* pages, parce que
    la chaîne apparaît ailleurs que dans les objets de page. C'est le `/Count` de la RACINE
    de l'arbre de pages qui fait foi ; un arbre imbriqué en déclare plusieurs, et la racine
    porte le plus grand — les sous-arbres comptent leurs propres feuilles, donc aucun ne peut
    dépasser le total.
    """
    if not PAGES_PDF.search(octets):
        return None
    comptes = [int(m.group(1)) for m in COMPTE.finditer(octets)]
    return max(comptes) if comptes else None


def pages_du_readme(texte: str) -> int | None:
    """Le nombre de pages annoncé en prose, ou None si le document n'en annonce pas."""
    m = PAGES_README.search(texte)
    return int(m.group(1)) if m else None


def _verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    doc = """= Un <a>
== Deux <b>
== Trois <c>
= Quatre <d>
== Cinq <e>
=== Six <f>
"""
    n = numeroter(doc)
    v("les sections se numérotent", n["a"] == "1" and n["d"] == "2", str(n))
    v("les sous-sections repartent à 1 dans chaque section",
      n["b"] == "1.1" and n["e"] == "2.1", str(n))
    v("un troisième niveau est numéroté", n["f"] == "2.1.1", str(n))
    # ⚠ Un `=` au fil du texte n'est pas un titre : sans l'ancrage en debut de ligne, une
    # formule ou un extrait de code decalerait toute la numerotation.
    v("un « = » au fil du texte n'est pas un titre",
      numeroter("= Un <a>\nsoit x = 3 et y = 4\n== Deux <b>")["b"] == "1.1")
    # ⚠ Une ancre de figure ne porte pas de numero de section.
    v("une ancre hors titre est ignorée",
      "fig:x" not in numeroter("= Un <a>" + chr(10) + "#figure() <fig:x>" + chr(10)))

    d2 = doc + "voir #link(<b>)[Section 1.1] et #link(<e>)[Section 9.9]\n"
    r = verifier_renvois(d2)
    v("un renvoi juste est reconnu", r[0]["juste"], str(r[0]))
    v("un renvoi faux est signalé", not r[1]["juste"], str(r[1]))
    v("... en donnant le numéro attendu", r[1]["attendu"] == "2.1", str(r[1]))
    # ⚠⚠ « L'ancre n'existe pas » et « le numero a vieilli » sont deux pannes differentes :
    # la premiere est un lien mort, la seconde un lien qui marche et ment. Les confondre
    # ferait chercher au mauvais endroit.
    r2 = verifier_renvois("= Un <a>\nvoir #link(<zz>)[Section 1]\n")
    v("une ancre inconnue est distinguée d'un numéro périmé",
      r2[0]["ancre_inconnue"] and not r2[0]["juste"], str(r2[0]))
    v("un lien sans « Section » n'est pas un renvoi de section",
      verifier_renvois("= Un <a>\nvoir #link(<a>)[plus haut]\n") == [])

    # --- le compte de pages -------------------------------------------------------------
    # ⚠ Un PDF minimal, ecrit a la main : la racine declare 3, un sous-arbre 2.
    pdf = b"1 0 obj<</Type /Pages /Count 3 /Kids[2 0 R]>>endobj\n" \
          b"2 0 obj<</Type /Pages /Count 2>>endobj\n" \
          b"3 0 obj<</Type /Page>>endobj\n"
    v("le compte de pages est celui de la RACINE", pages_du_pdf(pdf) == 3,
      str(pages_du_pdf(pdf)))
    # ⚠⚠ Le controle qui a manque : compter les objets `/Type /Page` rendrait 1 ici, et sur
    # le vrai article 42 pour 21 pages. La methode naive est plausible et fausse.
    v("... et non le compte des objets « /Type /Page »", pages_du_pdf(pdf) != 1)
    v("un fichier sans arbre de pages ne rend rien", pages_du_pdf(b"pas un pdf") is None)
    v("le compte annoncé en prose se lit", pages_du_readme("→ `a.pdf`, 21 pages, autonome")
      == 21)
    v("un document qui n'annonce pas de compte rend None",
      pages_du_readme("pas de compte ici") is None)

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("document", type=Path, nargs="?",
                    default=Path("docs/article/article.typ"))
    # ⚠ Le compte de pages annonce en prose vieillit en silence : mesure le 2026-08-23,
    # `docs/article/README.md` disait 18 pages pour un PDF qui en fait 21.
    ap.add_argument("--pdf", type=Path, help="le PDF, pour vérifier le compte de pages")
    ap.add_argument("--readme", type=Path, help="le document qui annonce ce compte")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return _verifier()
    if not a.document.is_file():
        print(f"absent : {a.document}", file=sys.stderr)
        return 2
    t = a.document.read_text(encoding="utf-8")
    r = verifier_renvois(t)
    if not r:
        print(f"aucun renvoi « Section N » dans {a.document}", file=sys.stderr)
        return 2
    faux = [x for x in r if not x["juste"]]
    print(f"\n  {len(r)} renvoi(s) de section dans {a.document}")
    for x in faux:
        if x["ancre_inconnue"]:
            print(f"    ⚠⚠ <{x['ancre']}> n'est l'ancre d'aucun titre — lien mort, "
                  f"écrit « Section {x['ecrit']} »")
        else:
            print(f"    ⚠ <{x['ancre']}> est la section {x['attendu']}, "
                  f"écrit « Section {x['ecrit']} »")
    code = 0
    if faux:
        print(f"\n  {len(faux)} renvoi(s) faux")
        code = 1
    else:
        print("  tous justes")

    if a.pdf and a.readme:
        if not a.pdf.is_file() or not a.readme.is_file():
            print("  ⚠ PDF ou README absent", file=sys.stderr)
            return 2
        n = pages_du_pdf(a.pdf.read_bytes())
        dit = pages_du_readme(a.readme.read_text(encoding="utf-8"))
        if n is None or dit is None:
            print(f"  ⚠ compte de pages introuvable (pdf={n}, prose={dit})")
            code = 1
        elif n != dit:
            print(f"  ⚠ {a.readme.name} annonce {dit} pages, le PDF en a {n}")
            code = 1
        else:
            print(f"  compte de pages : {n}, annoncé pareil")
    return code


if __name__ == "__main__":
    sys.exit(main())
