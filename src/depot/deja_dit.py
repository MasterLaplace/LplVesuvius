#!/usr/bin/env python3
"""Une idée déjà écrite ailleurs dans le dépôt — le garde-fou contre le radotage.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, et c'est une remarque de l'auteur, deux fois.
*« On commence à accumuler franchement pas mal de docs dans tous les sens, je ne sais pas
quand tu finiras par radoter comme un vieux pépé juste parce que tu auras oublié ce que tu as
déjà fait. »* Puis, une heure plus tard, la démonstration : j'ai présenté trois fois comme une
trouvaille un cadrage — *« on n'a rien découvert, on a fait des instruments »* — que
`docs/article/article.typ` écrit depuis longtemps (« *This paper is about the judging step […]
It does not read any text. **It measures.*** »).

  ⭐⭐ Ce dépôt garde ses **chiffres** (`verifier_chiffres`, 333 recalculés) et ses **tâches**
     (`taches_ouvertes`). Il ne gardait pas ses **idées**. C'est le même trou que l'antériorité
     externe de [`66`](../../docs/66_audit_danteriorite.md), tourné vers l'intérieur.

⚠⚠ CE QUE CE FICHIER NE FAIT PAS, et c'est ce qui le rend utilisable : il ne signale PAS une
phrase qui renvoie explicitement ailleurs. La forme normale de ce dépôt est de **redire avec un
pointeur** (« → `57` §1.2 », « voir [`64`] »), et c'est une qualité, pas un défaut. Une garde
qui compterait ces lignes désignerait des centaines de faux positifs, donc n'aurait aucun
lecteur — le mode d'échec de toute alerte trop bavarde.

⚠ Il ne juge pas non plus la vérité de la répétition : deux documents peuvent affirmer la même
chose parce qu'elle est vraie. Ce qu'il signale est qu'elle a **déjà été écrite**, pour qu'on
la cite au lieu de la re-annoncer.

Usage :
    uv run python src/depot/deja_dit.py --verifier
    uv run python src/depot/deja_dit.py --seuil 0.6
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

CIBLES = ("docs/*.md", "HANDOFF.md", "README.md", "docs/article/*.typ")
"""Ce qui est comparé. Les relevés de `docs/mesures/` sont exclus : ce sont des données."""

POINTEUR = re.compile(
    r"→|->|\bvoir\b|\bcf\.|\[`\d+`\]|\bsee\b|§|#link|@\w+2\d{3}", re.I)
"""Ce qui marque un renvoi explicite.

⚠⚠ Une ligne qui en porte un est **exemptée**, parce que redire en pointant est la forme
normale de ce dépôt. Sans cette exemption, la garde signale les centaines de rappels
délibérés — et une alerte qui désigne tout ne désigne rien.
"""

COMMANDE = re.compile(r"^\s*(?:[$>]\s*)?(?:\./|uv run|python3?\s|bash\s|git\s|curl\s|"
                      r"xmake|make\s|cd\s|src/|docs/mesures/)")
"""Ce qui ressemble a une COMMANDE plutot qu'a une idee.

⚠⚠ Elles sont exemptees, et il le fallait : le carnet de bord republie deliberement les
commandes des documents, donc au premier essai la garde a rendu **172 paires** dont la
majorite etaient des lignes `python3 src/...` identiques — du bruit qui aurait fait ignorer
l'alerte. Une commande qui se repete n'est pas un radotage, c'est un index.
"""

BRUIT = re.compile(r"[`*_~>|#\[\]()]+")
NOMBRE = re.compile(r"\d+[\d,.\s]*")
ESPACES = re.compile(r"\s+")

MOTS_VIDES = frozenset("""
le la les un une des du de d a à au aux et ou ni mais donc or car que qui quoi dont ou
ce cet cette ces son sa ses leur leurs il elle ils elles on nous vous je tu me te se
est sont etait etaient a ont avait avaient etre avoir fait faire dans sur sous par pour
avec sans plus moins tres bien deja encore aussi meme si ne pas n y en la le
the a an of to in is are was were and or but not this that it its for with on at by
""".split())


def normaliser(ligne: str) -> str:
    """Une ligne réduite à ses mots porteurs.

    ⚠⚠ Les NOMBRES sont retirés, et c'est délibéré : deux formulations de la même idée
    diffèrent souvent par leurs chiffres (« σ = 0,6558 » et « σ = 0,7111 »), et les garder
    ferait manquer exactement la répétition qu'on cherche. Les chiffres ont déjà leur propre
    garde-fou, `verifier_chiffres`.
    """
    t = BRUIT.sub(" ", ligne.lower())
    t = NOMBRE.sub(" ", t)
    return ESPACES.sub(" ", t).strip()


def mots_porteurs(ligne: str) -> frozenset[str]:
    """Les mots d'une ligne, sans les mots vides ni les mots trop courts."""
    return frozenset(m for m in normaliser(ligne).split()
                     if len(m) > 3 and m not in MOTS_VIDES)


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    """Le recouvrement de deux ensembles de mots."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def phrases(racine: Path = RACINE, minimum_mots: int = 7) -> list[tuple[str, int, str]]:
    """(document, ligne, texte) pour chaque ligne assez longue et SANS renvoi.

    ⚠ Une ligne courte ne porte pas une idée : « ⚠ Vérifié. » se répète légitimement partout,
    et la signaler noierait le signal.
    """
    out = []
    for motif in CIBLES:
        for f in sorted(racine.glob(motif)):
            if not f.is_file():
                continue
            rel = str(f.relative_to(racine))
            for n, l in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if POINTEUR.search(l) or COMMANDE.search(l):
                    continue
                if len(mots_porteurs(l)) < minimum_mots:
                    continue
                out.append((rel, n, l.strip()))
    return out


def redites(lignes, seuil: float = 0.6) -> list[dict]:
    """Les paires de lignes de DOCUMENTS DIFFÉRENTS qui disent la même chose.

    ⚠⚠ De documents différents seulement. Une répétition à l'intérieur d'un document est
    presque toujours un rappel voulu — un résumé en tête, une reprise en conclusion — et la
    signaler ferait du bruit là où l'auteur a choisi de se répéter.

    ⚠ Le balayage est indexé par mot, pas quadratique sur toutes les paires : sur des milliers
    de lignes, comparer chacune à chacune coûte des minutes pour un résultat identique.
    """
    porteurs = [(d, n, t, mots_porteurs(t)) for d, n, t in lignes]
    index: dict[str, list[int]] = {}
    for i, (_, _, _, mots) in enumerate(porteurs):
        for m in mots:
            index.setdefault(m, []).append(i)

    vus, out = set(), []
    for i, (d1, n1, t1, m1) in enumerate(porteurs):
        candidats = {j for m in m1 for j in index.get(m, ()) if j > i}
        for j in candidats:
            d2, n2, t2, m2 = porteurs[j]
            if d1 == d2:
                continue
            s = jaccard(m1, m2)
            if s < seuil:
                continue
            cle = (d1, n1, d2, n2)
            if cle in vus:
                continue
            vus.add(cle)
            out.append({"score": s, "a": {"doc": d1, "ligne": n1, "texte": t1[:150]},
                        "b": {"doc": d2, "ligne": n2, "texte": t2[:150]}})
    return sorted(out, key=lambda x: -x["score"])


def rapporter(lot: list[dict], limite: int = 25) -> None:
    """La sortie lisible : la paire, et où la citer plutôt que la réécrire."""
    for r in lot[:limite]:
        print(f"  {r['score']:.2f}  {r['a']['doc']}:{r['a']['ligne']}  ↔  "
              f"{r['b']['doc']}:{r['b']['ligne']}")
        print(f"        A  {r['a']['texte']}")
        print(f"        B  {r['b']['texte']}")
    if len(lot) > limite:
        # ⚠ Un plafond d'affichage doit DIRE ce qu'il cache : une liste tronquee en silence
        # se lit comme une liste complete.
        print(f"  … et {len(lot) - limite} autre(s) paire(s) non affichee(s)")
    print(f"\n{len(lot)} paire(s) de lignes qui redisent la meme chose sans se citer")


def verifier() -> int:
    """L'instrument peut-il rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    import tempfile

    # -- normaliser : les nombres partent, la casse et le balisage aussi.
    v("le balisage est retire", "sigma" in normaliser("**`sigma`** vaut"))
    v("les nombres sont retires", "0" not in normaliser("sigma vaut 0,6558"))
    # ⚠⚠ LA PROPRIETE QUI PORTE LE FICHIER : deux formulations qui ne different QUE par leurs
    # chiffres doivent se ressembler. Garder les nombres ferait manquer la redite cherchee.
    a = mots_porteurs("le modele rend une dispersion sigma de 0,6558 sur ce rouleau")
    b = mots_porteurs("le modele rend une dispersion sigma de 0,7111 sur ce rouleau")
    v("deux phrases qui ne different que par leurs chiffres se ressemblent",
      jaccard(a, b) == 1.0, f"{jaccard(a, b):.2f}")

    # -- mots vides et mots courts ecartes.
    v("les mots vides sont ecartes", "dans" not in mots_porteurs("dans le rouleau carbonise"))
    v("... et les mots courts aussi", "vaut" in mots_porteurs("le seuil vaut quelque chose")
      and "le" not in mots_porteurs("le seuil vaut quelque chose"))

    # -- jaccard : bornes et cas degeneres.
    v("deux ensembles identiques valent 1", jaccard(frozenset("ab"), frozenset("ab")) == 1.0)
    v("deux ensembles disjoints valent 0", jaccard(frozenset("ab"), frozenset("cd")) == 0.0)
    v("un ensemble vide ne correle avec rien", jaccard(frozenset(), frozenset("ab")) == 0.0)

    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "docs").mkdir()
        (r / "docs" / "01_a.md").write_text(
            "Cette chaine mesure la geometrie tracee sans jamais lire aucune lettre ecrite.\n"
            "court.\n", encoding="utf-8")
        (r / "docs" / "02_b.md").write_text(
            "Cette chaine mesure la geometrie tracee sans jamais lire aucune lettre ecrite.\n",
            encoding="utf-8")
        # ⚠⚠⚠ LE CONTROLE QUI REND LA GARDE UTILISABLE : la MEME phrase, mais portant un
        # renvoi, doit etre EXEMPTEE. Redire en pointant est la forme normale de ce depot.
        (r / "docs" / "03_c.md").write_text(
            "→ Cette chaine mesure la geometrie tracee sans jamais lire aucune lettre ecrite.\n",
            encoding="utf-8")
        (r / "docs" / "04_d.md").write_text(
            "Le traceur produit des surfaces completement differentes selon sa graine initiale.\n",
            encoding="utf-8")

        lot = phrases(r)
        v("une ligne trop courte est ignoree",
          all("court" not in t for _, _, t in lot), str(lot))
        # ⚠⚠ Le second cas d'exemption, paye au premier essai : une COMMANDE republiee dans
        # le carnet de bord n'est pas un radotage. Sans cette regle, la garde rendait 172
        # paires dont la majorite etaient des lignes de commande identiques.
        (r / "docs" / "06_f.md").write_text(
            "python3 src/graine/derive_avec_profondeur.py --docs docs/mesures --json sortie.json\n",
            encoding="utf-8")
        (r / "docs" / "07_g.md").write_text(
            "python3 src/graine/derive_avec_profondeur.py --docs docs/mesures --json sortie.json\n",
            encoding="utf-8")
        v("une commande republiee n'est pas signalee",
          all("06_f" not in x["a"]["doc"] for x in redites(phrases(r), 0.6)),
          str([x["a"]["doc"] for x in redites(phrases(r), 0.6)]))

        v("une ligne avec renvoi est exemptee",
          all(not d.endswith("03_c.md") for d, _, _ in lot), str([x[0] for x in lot]))

        red = redites(lot, 0.6)
        v("deux documents qui redisent la meme chose sont apparies", len(red) == 1, str(red))
        v("... avec un score de 1", red and red[0]["score"] == 1.0, str(red))
        v("... et les deux bons documents",
          red and {red[0]["a"]["doc"], red[0]["b"]["doc"]}
          == {"docs/01_a.md", "docs/02_b.md"}, str(red))
        # ⚠ La sonde inverse : deux phrases differentes ne doivent PAS etre appariees.
        v("deux phrases differentes ne sont pas appariees",
          all("04_d" not in x["a"]["doc"] and "04_d" not in x["b"]["doc"] for x in red))

        # -- une repetition INTERNE a un document n'est pas signalee.
        (r / "docs" / "05_e.md").write_text(
            "Une phrase parfaitement identique repetee deux fois dans le meme document ici.\n"
            "Une phrase parfaitement identique repetee deux fois dans le meme document ici.\n",
            encoding="utf-8")
        red2 = redites(phrases(r), 0.6)
        v("une repetition interne a un document n'est pas signalee",
          all("05_e" not in x["a"]["doc"] or "05_e" not in x["b"]["doc"] for x in red2),
          str([x for x in red2 if "05_e" in x["a"]["doc"]]))

        # -- le seuil : monter le seuil ne peut que reduire le lot.
        v("un seuil plus haut ne rend jamais plus de paires",
          len(redites(lot, 0.9)) <= len(redites(lot, 0.5)))

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--seuil", type=float, default=0.6)
    p.add_argument("--limite", type=int, default=25)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    lot = redites(phrases(), a.seuil)
    rapporter(lot, a.limite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
