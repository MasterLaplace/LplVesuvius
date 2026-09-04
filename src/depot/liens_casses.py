#!/usr/bin/env python3
"""Un lien d'un document mène-t-il quelque part ?

⚠⚠ Pourquoi ce fichier existe. `docs/00_carnet_de_bord.md` écrit ses liens en
`docs/61_…md` — un chemin depuis la RACINE — alors qu'il vit lui-même dans `docs/`. Un
lecteur les résout donc en `docs/docs/61_…md`, et **aucun de ses 87 liens ne mène nulle
part**, images comprises. Signalé par l'auteur le 2026-08-27, en ouvrant simplement le
document.

⭐ La cause est datée : le grand ménage a déplacé 522 fichiers de la racine vers `docs/`
([`56`](../../docs/56_le_grand_menage.md)), et un lien écrit depuis la racine reste
syntaxiquement valide après le déplacement — il pointe seulement ailleurs. Rien ne lève,
rien ne manque, et le lien s'affiche normalement jusqu'à ce qu'on clique.

⚠ La symétrique existe aussi : un document de `docs/` qui cite `src/x.py` le résout en
`docs/src/x.py`. Vingt-six liens du dépôt sont dans ce cas.

## Ce qui est corrigé et ce qui ne l'est pas

Une correction n'est proposée que si **la cible corrigée existe**. Deux règles, et rien
d'autre : retirer un préfixe `docs/` quand le fichier est déjà dans `docs/`, et préfixer
`../` quand la cible est à la racine. Un lien qu'aucune des deux ne répare est **signalé
sans être touché** — deviner mieux serait fabriquer une cible.

Usage :
    uv run python src/depot/liens_casses.py            # l'inventaire
    uv run python src/depot/liens_casses.py --corriger  # applique ce qui est sûr
    uv run python src/depot/liens_casses.py --verifier
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

LIEN = re.compile(r'!?\[[^\]]*\]\(([^)\s]+?)(?:\s+"[^"]*")?\)')
"""Un lien markdown, image comprise. Le titre optionnel est toléré.

⚠⚠ L'ancre fait partie de la capture et n'est coupée qu'ENSUITE. Une première version
l'excluait de la classe de caractères, donc un lien `x.md#section` ne matchait pas du tout —
et ces liens-là échappaient au contrôle en silence. Trouvé par le cas négatif de la batterie,
qui existait justement pour ça."""

ELAGUES = (".venv", "node_modules", ".git", "repos", "site", "store", "__pycache__")
"""⚠ `site/` et `store/` sont hors du dépôt versionné ou générés, `repos/` est du code tiers.
Les traverser ferait signaler des liens qui ne sont pas les nôtres."""


CITATION = re.compile(r"«[^»]*»")
"""Une citation verbatim, en guillemets français.

⚠⚠⚠ POURQUOI CETTE REGLE EXISTE. `docs/registres/fiches_de_lecture.md` **transcrit** des lignes
d'autres documents, guillemets compris, et sa garde `verifier_citations.py` retrouve chacune à sa
ligne d'origine. Les liens relatifs qu'elles contiennent sont valides **depuis `docs/`**, pas
depuis `docs/registres/` — donc ce contrôle les signalait, et il avait tort deux fois : ce ne
sont pas les liens de ce document, et les « corriger » réécrirait un texte cité, ce qui
falsifierait la citation **et** casserait sa garde.

⭐ La réponse du dépôt à ce genre de cas est toujours la même : **distinguer plutôt que
confondre**. Un lien cité est compté et affiché à part, jamais effacé — confondre les deux est
précisément ce qui enterre les rares liens réellement cassés.
"""


def positions_citees(texte: str) -> list[tuple[int, int]]:
    """
    @brief Les intervalles de caractères couverts par une citation verbatim.
    """
    return [(m.start(), m.end()) for m in CITATION.finditer(texte)]


def est_cite(position: int, intervalles: list[tuple[int, int]]) -> bool:
    """
    @brief Ce lien tombe-t-il à l'intérieur d'une citation ?
    """
    return any(a <= position < b for a, b in intervalles)


def est_externe(cible: str) -> bool:
    """Un lien qu'on ne peut pas résoudre sur le disque n'est pas jugé."""
    return cible.startswith(("http://", "https://", "mailto:", "#", "/"))


def corrections(fichier: Path, cible: str, racine: Path) -> list[str]:
    """Les cibles corrigées qui, elles, EXISTENT — dans l'ordre où on les essaie.

    ⚠ La liste peut être vide, et c'est un résultat : le lien est cassé et aucune règle
    simple ne le répare. Le signaler sans le toucher vaut mieux qu'inventer une cible.
    """
    nu = cible.split("#")[0]
    essais = []
    # 1. Le fichier est dans `docs/` et le lien part de la racine : « docs/x » → « x ».
    if fichier.parent.name == "docs" and nu.startswith("docs/"):
        essais.append(nu[len("docs/"):])
    # 2. La cible est un chemin de racine (`src/`, `data/`) vu depuis un sous-dossier.
    profondeur = len(fichier.parent.relative_to(racine).parts)
    if profondeur and not nu.startswith(".."):
        essais.append("../" * profondeur + nu)
    return [e for e in essais if (fichier.parent / e).exists()]


def liens_casses(racine: Path, cites: list | None = None
                 ) -> list[tuple[Path, str, list[str]]]:
    """(fichier, cible cassée, corrections possibles) pour chaque lien qui ne mène nulle part.

    ⚠ `cites` recueille, s'il est fourni, les liens qui tombent DANS une citation verbatim :
    ils sont rapportés à part et ne comptent pas comme cassés. Sans lui ils sont simplement
    ignorés — un appelant qui ne veut que les liens du document n'a rien à passer.
    """
    out = []
    cites = cites if cites is not None else []
    for f in sorted(racine.rglob("*.md")):
        if any(p in f.parts for p in ELAGUES):
            continue
        texte = f.read_text(encoding="utf-8", errors="replace")
        citees = positions_citees(texte)
        for m in LIEN.finditer(texte):
            cible = m.group(1)
            if est_externe(cible):
                continue
            if (f.parent / cible.split("#")[0]).exists():
                continue
            # ⚠ Un lien cite n'est PAS propose a la correction : `appliquer` reecrirait le
            # texte transcrit. La liste vide de remedes est donc obligatoire ici.
            if est_cite(m.start(), citees):
                cites.append((f, cible))
                continue
            out.append((f, cible, corrections(f, cible, racine)))
    return out


def appliquer(casses: list[tuple[Path, str, list[str]]]) -> tuple[int, int]:
    """Réécrit ce qui est sûr. Rend (corrigés, laissés)."""
    par_fichier: dict[Path, list[tuple[str, str]]] = {}
    laisses = 0
    for f, cible, propositions in casses:
        if not propositions:
            laisses += 1
            continue
        nu, ancre = (cible.split("#") + [""])[:2]
        neuf = propositions[0] + (f"#{ancre}" if ancre else "")
        par_fichier.setdefault(f, []).append((cible, neuf))
    corriges = 0
    for f, paires in par_fichier.items():
        texte = f.read_text(encoding="utf-8")
        for vieux, neuf in paires:
            # ⚠ On remplace « (cible) » et non « cible » : un nom de fichier apparaît aussi
            # en prose, et le réécrire là changerait un texte au lieu d'un lien.
            texte = texte.replace(f"]({vieux})", f"]({neuf})")
            corriges += 1
        f.write_text(texte, encoding="utf-8")
    return corriges, laisses


def verifier() -> int:
    """Auto-test HORS LIGNE, sur une arborescence fabriquée."""
    import tempfile

    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs").mkdir()
        (r / "docs" / "images").mkdir()
        (r / "src" / "x").mkdir(parents=True)
        (r / "docs" / "cible.md").write_text("cible\n")
        (r / "docs" / "images" / "f.png").write_bytes(b"")
        (r / "src" / "x" / "outil.py").write_text("x\n")
        doc = r / "docs" / "a.md"
        doc.write_text(
            "[un doc](docs/cible.md)\n"          # préfixe docs/ de trop
            "![img](docs/images/f.png)\n"        # idem, sur une image
            "[un outil](src/x/outil.py)\n"       # chemin de racine vu depuis docs/
            "[juste](cible.md)\n"                # déjà correct
            "[dehors](https://exemple.org)\n"    # externe
            "[ancre](docs/cible.md#section)\n"   # ancre à préserver
            "[perdu](docs/jamais_ecrit.md)\n"    # irréparable
        )

        casses = liens_casses(r)
        cibles = {c for _, c, _ in casses}
        v("un lien déjà correct n'est pas signalé", "cible.md" not in cibles)
        v("un lien externe n'est pas signalé", not any(est_externe(c) for c in cibles))
        v("le préfixe docs/ de trop est signalé", "docs/cible.md" in cibles)
        v("... sur une image aussi", "docs/images/f.png" in cibles)
        v("un chemin de racine vu depuis docs/ est signalé", "src/x/outil.py" in cibles)
        v("une cible qui n'existe nulle part est signalée", "docs/jamais_ecrit.md" in cibles)

        prop = {c: p for _, c, p in casses}
        # ⚠ C'est la PREMIÈRE proposition qui est appliquée, donc c'est elle qu'on juge :
        # `../docs/cible.md` mène au même fichier et reste dans la liste, mais l'ordre est le
        # contrat, et le plus court est celui qu'un lecteur reconnaît.
        v("le préfixe de trop se corrige en le retirant", prop["docs/cible.md"][0] == "cible.md")
        v("un chemin de racine se corrige avec ../",
          prop["src/x/outil.py"][0] == "../src/x/outil.py")
        # ⚠⚠ Le contrôle qui empêche d'inventer : sans cible existante, aucune proposition.
        v("un lien irréparable ne reçoit AUCUNE proposition", prop["docs/jamais_ecrit.md"] == [])

        corriges, laisses = appliquer(casses)
        v("les liens sûrs sont corrigés, les autres laissés", (corriges, laisses) == (4, 1))
        texte = doc.read_text()
        v("l'ancre est préservée", "(cible.md#section)" in texte)
        v("le lien irréparable est intact", "(docs/jamais_ecrit.md)" in texte)
        v("plus aucun lien réparable n'est cassé",
          [c for _, c, p in liens_casses(r) if p] == [])

    # ⚠⚠ LE CAS DE LA CITATION, dans SON PROPRE arbre. Le mettre dans celui d'au-dessus
    # appliquait les corrections trop tot et cassait les controles suivants -- defaut paye une
    # fois, d'ou l'isolement.
    with tempfile.TemporaryDirectory() as d2:
        r2 = Path(d2)
        (r2 / "docs" / "registres").mkdir(parents=True)
        fiches = r2 / "docs" / "registres" / "fiches.md"
        # ⚠⚠⚠ LA MEME CIBLE, une fois CITEE et une fois NUE. Si la regle etait trop large elle
        # avalerait les deux ; inerte, elle n'en attraperait aucune. Une seule doit passer.
        fiches.write_text(
            "  - ligne 82 : \u00ab voir [`38`](docs/jamais_ecrit.md) pour la suite \u00bb\n"
            "et hors citation : [`38`](docs/jamais_ecrit.md)\n"
        )
        cites2: list = []
        casses2 = liens_casses(r2, cites2)
        v("un lien DANS une citation verbatim n'est pas compte comme casse", len(cites2) == 1)
        v("... et le MEME lien hors citation l'est toujours", len(casses2) == 1)
        v("une position hors de toute citation est lue non citee",
          not est_cite(0, positions_citees("abc \u00ab def \u00bb ghi")))
        v("... et une position dedans est lue citee",
          est_cite(6, positions_citees("abc \u00ab def \u00bb ghi")))
        # ⚠⚠ LA PROPRIETE QUI COMPTE : `appliquer` ne doit pas toucher au texte cite. Mes deux
        # premieres redactions de ce controle etaient incapables d'echouer (un `or True`, puis
        # un generateur vide) -- dans le lot qui corrige exactement ce peche. La forme qui teste
        # ne raisonne pas sur des listes : elle APPLIQUE, puis compare la ligne octet pour octet.
        avant_c = fiches.read_text().splitlines()[0]
        appliquer(casses2)
        v("... et `appliquer` laisse la ligne citee intacte, octet pour octet",
          fiches.read_text().splitlines()[0] == avant_c)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corriger", action="store_true", help="appliquer ce qui est sûr")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    cites: list = []
    casses = liens_casses(RACINE, cites)
    if a.corriger:
        corriges, laisses = appliquer(casses)
        print(f"{corriges} lien(s) corrigé(s), {laisses} laissé(s) faute de cible sûre")
        cites = []
        casses = liens_casses(RACINE, cites)

    par_fichier: dict[str, int] = {}
    sans_remede = []
    for f, cible, prop in casses:
        rel = str(f.relative_to(RACINE))
        par_fichier[rel] = par_fichier.get(rel, 0) + 1
        if not prop:
            sans_remede.append((rel, cible))
    for rel, n in sorted(par_fichier.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>3}  {rel}")
    for rel, cible in sans_remede:
        print(f"  ⚠ sans remède : {rel} → {cible}")
    if cites:
        par_cite: dict[str, int] = {}
        for f, _ in cites:
            rel = str(f.relative_to(RACINE))
            par_cite[rel] = par_cite.get(rel, 0) + 1
        for rel, n in sorted(par_cite.items(), key=lambda kv: -kv[1]):
            print(f"  {n:>3}  {rel}  (liens DANS une citation verbatim — texte transcrit, "
                  "pas un lien de ce document)")
    print(f"{len(casses)} lien(s) relatif(s) cassé(s) dans {len(par_fichier)} fichier(s)"
          + (f", plus {len(cites)} lien(s) cité(s) verbatim" if cites else ""))
    return 1 if casses else 0


if __name__ == "__main__":
    sys.exit(main())
