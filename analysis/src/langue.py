#!/usr/bin/env python3
"""Écrire une figure dans une autre langue sans réécrire la figure.

⚠⚠ **Pourquoi ce fichier existe.** Les figures de ce dépôt sont en français, comme ses
documents. Un article destiné à la littérature du domaine est en anglais — et une figure
française dans un texte anglais est exactement ce qu'un relecteur signale. La réponse
évidente, ajouter un paramètre de langue à chaque `g.text(...)`, demanderait de toucher
une soixantaine d'appels dans six fichiers : soixante occasions d'en oublier un, et
soixante endroits où la traduction pourrait diverger du texte réel.

⭐ Le remède tient en une observation : **tout ce qui s'affiche passe par `ImageDraw.text`**.
Il suffit donc d'envelopper l'objet de dessin. Un fichier de figure change d'**une ligne**,
et sa table de traduction vit à un seul endroit.

⚠ La traduction est faite par **remplacement de fragments**, pas par correspondance exacte :
les libellés sont des f-strings qui contiennent des nombres calculés, donc aucune table de
chaînes entières ne pourrait les couvrir. Les fragments sont appliqués **du plus long au
plus court**, sinon « aire » remplacerait le début de « aire utile » et laisserait un
résidu.

⚠⚠ **Et le silence est le vrai danger.** Une phrase oubliée dans la table sort en français
au milieu d'un texte anglais, sans qu'aucune erreur ne soit levée — le défaut se voit à
l'œil, sur une figure, une fois le PDF compilé. `Traduisant` **compte** donc ce qu'il n'a
pas su traduire et le rend par `intraduits()`, et les figures échouent plutôt que de rendre
une image à moitié traduite.
"""
from __future__ import annotations

import re
import unicodedata

# ⚠ Un mot français survivant se détecte à peu de frais : soit il porte un accent, soit il
# appartient à cette liste courte de mots fréquents et sans accent. Ce n'est pas un
# détecteur de langue — c'est un garde-fou qui doit attraper les oublis ordinaires.
MOTS_TEMOINS = (
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "sur", "sous",
    "dans", "par", "pour", "avec", "sans", "plus", "moins", "que", "qui", "est",
    "sont", "aire", "trace", "traces", "rouleau", "rouleaux", "tirage", "tirages",
    "nappe", "nappes", "seuil", "plafond", "graine", "graines", "fenetre", "spire",
    "couches", "ecart", "ecarts", "paire", "paires", "voisinage", "meme", "toujours",
    # ⚠⚠ LES CONNECTEURS, ajoutes le 2026-08-22 apres une fuite reelle. Un libelle compose
    # par f-string — « rendu {pb} contre {ph} couches » — a ses MORCEAUX dans la table, donc
    # « rendu » et « couches » etaient traduits, et « contre » est passe tel quel : la
    # figure anglaise disait « depth 21 contre 41 layers ». Le garde ne l'a pas vu parce
    # qu'aucun connecteur n'etait dans la liste. Ceux-ci n'ont pas d'homographe anglais,
    # donc ils ne peuvent pas faire crier le garde sur une legende correcte.
    "contre", "chaque", "entre", "vers", "cette", "cet", "ces", "leur", "leurs",
    "ainsi", "donc", "mais", "alors", "aussi", "encore", "depuis", "selon", "chez",
    "tres", "peu", "beaucoup", "hauteur", "largeur", "profondeur", "niveau", "niveaux",
)

# ⚠⚠ Ces mots existent DANS LES DEUX LANGUES, donc ils ne discriminent rien — les garder
# ferait crier le garde sur une legende parfaitement anglaise, et un garde qui crie au loup
# finit ignore. Trouve des le premier essai : « the trace self-intersects » etait signale
# comme du francais a cause de « trace ».
AMBIGUS = frozenset({"trace", "traces", "point", "points", "orange", "figure", "plus",
                     "distance", "surface", "surfaces", "note", "on", "or", "son"})


def _sans_accent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def reste_du_francais(s: str) -> bool:
    """Cette chaîne contient-elle encore du français ?

    ⚠ Volontairement grossier, et c'est ce qui le rend utile : il vaut mieux un garde qui
    signale une fois de trop qu'un garde qui laisse passer une légende non traduite dans
    un article. Les faux positifs se règlent en ajoutant le fragment à la table.
    """
    if any(unicodedata.category(c) == "Mn"
           for c in unicodedata.normalize("NFD", s)):
        return True
    mots = re.findall(r"[A-Za-z]+", _sans_accent(s).lower())
    return any(m in MOTS_TEMOINS and m not in AMBIGUS for m in mots)


class Traduisant:
    """Un `ImageDraw` qui traduit ce qu'on lui demande d'écrire.

    Tout ce qui n'est pas `text` est délégué tel quel : les traits, les disques et les
    rectangles n'ont pas de langue.
    """

    def __init__(self, dessin, table: dict[str, str] | None, point_decimal: bool = True):
        self._d = dessin
        # Du plus long au plus court : sinon un fragment court mange le début d'un long.
        self._table = sorted((table or {}).items(), key=lambda kv: -len(kv[0]))
        self._rates: list[str] = []
        # ⚠ Le séparateur décimal fait partie de la langue, et aucune table de fragments ne
        # peut l'atteindre : il vit entre deux chiffres CALCULÉS. On le réécrit par motif,
        # et seulement là — « 0,3 % » devient « 0.3 % », « PHerc1447 » ne bouge pas.
        self._point = point_decimal and bool(table)

    def __getattr__(self, nom):
        return getattr(self._d, nom)

    def traduire(self, s: str) -> str:
        """Traduire en UNE passe : ce qui vient d'être traduit ne se retraduit pas.

        ⚠⚠ La version séquentielle — une boucle de `str.replace` — laissait la SORTIE d'un
        remplacement être reprise par une clé plus courte. Mesuré le 2026-08-22 :
        « 0 parmi celles qui convergent » devenait « 0 among those that converge », puis la
        clé « converge » → « converges » repassait dessus et rendait **« that converges »**.
        Le libellé était juste dans la table et faux à l'écran, et le garde de langue ne
        pouvait pas le voir puisque le résultat est de l'anglais.

        ⭐ Une alternation unique, les clés les plus longues d'abord, remplace chaque
        portion du texte SOURCE exactement une fois. C'est la même règle que le tri du
        constructeur voulait déjà obtenir — il la rendait seulement probable.
        """
        if not self._table:
            return s
        motif = re.compile("|".join(re.escape(fr) for fr, _ in self._table))
        table = dict(self._table)
        out = motif.sub(lambda m: table[m.group(0)], s)
        if self._point:
            out = re.sub(r"(?<=\d),(?=\d)", ".", out)
        if reste_du_francais(out):
            self._rates.append(out)
        return out

    def text(self, xy, s, *args, **kw):
        self._d.text(xy, self.traduire(str(s)), *args, **kw)

    def intraduits(self) -> list[str]:
        """Les chaînes écrites qui contiennent encore du français."""
        return list(dict.fromkeys(self._rates))


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    class FauxDessin:
        def __init__(self):
            self.ecrit = []

        def text(self, xy, s, *a, **k):
            self.ecrit.append(s)

        def line(self, *a, **k):
            self.ecrit.append("LIGNE")

    d = FauxDessin()
    g = Traduisant(d, {"aire utile": "useful area", "aire": "area", "par tour": "per turn"})
    g.text((0, 0), "aire utile 12,97 cm²")
    # ⚠ « 12.97 » et non « 12,97 » : le séparateur décimal fait partie de la langue et il
    # est réécrit en même temps que les mots. L'attendu de la première version disait
    # « 12,97 » — il datait d'avant cette règle.
    v("un fragment est remplacé dans une f-string", d.ecrit[-1] == "useful area 12.97 cm²",
      d.ecrit[-1])
    # ⚠⚠ LA sonde : sans le tri du plus long au plus court, « aire » mangerait le debut de
    # « aire utile » et laisserait « area utile », qui a l'air traduit et ne l'est pas.
    v("... et le fragment le plus long gagne", "utile" not in d.ecrit[-1], d.ecrit[-1])
    g.text((0, 0), "aire par tour")
    v("plusieurs fragments dans une même chaîne", d.ecrit[-1] == "area per turn",
      d.ecrit[-1])
    g.line((0, 0, 1, 1))
    v("ce qui n'est pas du texte est délégué tel quel", d.ecrit[-1] == "LIGNE")

    v("une table vide ne touche à rien",
      Traduisant(FauxDessin(), None).traduire("aire utile") == "aire utile")

    # ⭐ Le detecteur de residu, dans les deux sens.
    v("un accent trahit du français", reste_du_francais("écart médian"))
    v("un mot outil aussi, même sans accent", reste_du_francais("aire par tour"))
    v("une phrase anglaise passe", not reste_du_francais("median gap per turn"))
    v("un nom propre n'est pas du français", not reste_du_francais("PHerc1447 gap"))
    # ⚠⚠ LA fuite reelle, epinglee. Un libelle compose par f-string a ses morceaux dans la
    # table de traduction et son CONNECTEUR nulle part : « rendu {a} contre {b} couches »
    # sortait « depth 21 contre 41 layers », et le garde le laissait passer. Le remede n'est
    # pas de mieux relire, c'est que le connecteur soit un mot temoin.
    # ⚠⚠ LA CASCADE, epinglee. Deux cles dont l'une apparait dans la VALEUR de l'autre : la
    # boucle sequentielle repassait sur sa propre sortie et rendait « that converges ».
    dc = FauxDessin()
    casc = Traduisant(dc, {"celles qui convergent": "those that converge",
                           "converge": "converges"})
    casc.text((0, 0), "0 parmi celles qui convergent")
    v("une traduction n'est pas retraduite",
      dc.ecrit[-1] == "0 parmi those that converge", dc.ecrit[-1])
    # ⚠ Et le controle : chacune des deux cles doit encore fonctionner seule, sinon le
    # remede aurait casse la traduction au lieu de la reparer.
    casc.text((0, 0), "le verdict converge ici")
    v("... et la clé courte s'applique quand elle est seule",
      dc.ecrit[-1] == "le verdict converges ici", dc.ecrit[-1])
    # ⚠ La cle la PLUS LONGUE gagne quand les deux matchent au meme endroit.
    dl = FauxDessin()
    Traduisant(dl, {"aire utile": "useful area", "aire": "area"}).text(
        (0, 0), "aire utile et aire")
    v("la clé la plus longue gagne", dl.ecrit[-1] == "useful area et area", dl.ecrit[-1])

    v("un connecteur français resté dans une phrase anglaise est vu",
      reste_du_francais("depth 21 contre 41 layers"))
    v("... et les autres connecteurs aussi",
      all(reste_du_francais(f"one {m} two") for m in
          ("contre", "entre", "vers", "chaque", "selon", "depuis")))
    # ⚠ Et le controle du controle : ces mots ne doivent pas faire crier le garde sur une
    # legende anglaise ordinaire. Un garde qui crie au loup finit ignore.
    for phrase in ("depth 21 against 41 layers", "median drift per trace",
                   "share at the profile edge", "the ceiling of THIS trace",
                   "area reached (cm²) — log scale", "one dot per run"):
        v(f"« {phrase} » passe", not reste_du_francais(phrase))
    # ⚠ « la » est un mot temoin ; « plafond » aussi. Sans eux, une legende sans accent
    # passerait pour traduite.
    v("une légende oubliée est signalée", reste_du_francais("plafond de generations"))

    g2 = Traduisant(FauxDessin(), {"aire": "area"})
    g2.text((0, 0), "aire par tour")
    v("ce qui n'a pas pu être traduit est COMPTÉ", g2.intraduits() == ["area par tour"],
      str(g2.intraduits()))
    g3 = Traduisant(FauxDessin(), {"aire par tour": "area per turn"})
    g3.text((0, 0), "aire par tour")
    v("... et une traduction complète ne compte rien", g3.intraduits() == [])

    # ⭐ Le separateur decimal : entre deux chiffres, et nulle part ailleurs.
    d4 = FauxDessin()
    g4 = Traduisant(d4, {"aire": "area"})
    g4.text((0, 0), "aire 12,97 cm2")
    v("la virgule décimale devient un point", d4.ecrit[-1] == "area 12.97 cm2", d4.ecrit[-1])
    g4.text((0, 0), "area, then more")
    v("... mais pas une virgule de phrase", d4.ecrit[-1] == "area, then more", d4.ecrit[-1])
    d5 = FauxDessin()
    Traduisant(d5, None).text((0, 0), "aire 12,97")
    v("... et pas du tout sans table", d5.ecrit[-1] == "aire 12,97", d5.ecrit[-1])

    # ⚠⚠ La sonde du garde-fou lui-meme : sans la liste AMBIGUS, cette phrase anglaise
    # serait signalee comme du francais et la figure refuserait de s'ecrire.
    v("un mot commun aux deux langues ne déclenche pas le garde",
      not reste_du_francais("red = the trace self-intersects"))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(verifier())
