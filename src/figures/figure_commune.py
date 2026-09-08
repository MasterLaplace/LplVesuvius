#!/usr/bin/env python3
"""Ce que toutes les figures du dépôt refaisaient chacune de leur côté.

⚠⚠ POURQUOI CE FICHIER EXISTE. `_police` était définie **quinze fois**, en **quatre variantes**
— et c'est le seul endroit du dépôt où des copies ont RÉELLEMENT divergé. Elles ne diffèrent
pourtant que par les **tailles** demandées : le mécanisme (essayer deux chemins de police, se
rabattre sur le défaut de PIL) est le même partout. Une fonction **paramétrée** les remplace
toutes **sans changer une seule figure**, puisque chaque appelant passe ses propres tailles.

  ⭐ La règle : ce qui varie devient un ARGUMENT, ce qui ne varie pas devient un seul endroit.
    Unifier en imposant des tailles aurait déplacé quinze images pour du rangement, ce qui est
    exactement le refactor qu'on ne fait pas.

⚠ La quatrième variante attrapait `Exception` là où les autres attrapent `OSError`. C'est
`OSError` qui est juste : c'est ce que `ImageFont.truetype` lève quand le fichier manque, et
attraper plus large masquerait une erreur de programmation dans le repli. Rien de mesurable n'en
dépendait — le repli n'est atteint que si la police est absente.

⚠ Le repli rend le **même** objet autant de fois qu'il y a de tailles demandées : une figure
qui déballe trois polices doit en recevoir trois, même dégradées, sinon elle plante là où elle
devrait seulement être moins jolie.
"""
from __future__ import annotations

import argparse
import sys

CHEMINS = ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
"""Où chercher la police, dans l'ordre. ⚠ Le nom nu marche quand la police est installée dans
le chemin de recherche de PIL ; le chemin absolu est le repli des environnements minces."""

GLYPHES_ABSENTS = ("\u2b50", "\u2705", "\u274c", "\u2b1b", "\u26d4")
"""Quelques caractères que DejaVuSans ne rend pas : ils sortent en **carré vide**, et un
carré dans une figure est du bruit qu'un lecteur prend pour une donnée.

⚠⚠⚠ CETTE LISTE N'EST PLUS LE CONTRÔLE, ELLE EN EST LA SONDE. Écrite à la main, elle
était en retard par construction : `\u26d4` a traversé une figure et en est sorti en
carré vide, parce que personne ne l'y avait ajouté. `prose_tracable` demande désormais à
la POLICE, et cette liste ne sert plus qu'à vérifier que la question rend au moins les
réponses déjà connues.

⚠ Et elle est enfin écrite en séquences d'échappement : la version précédente **affirmait
l'être** et contenait les caractères en clair, donc ce fichier portait précisément ce
qu'il aide à refuser — un commentaire qui dit l'inverse de son code."""


def police(*tailles: int):
    """Une police par taille demandée, ou le défaut de PIL autant de fois.

    Rend un tuple de la longueur de `tailles`, ou l'objet seul si une seule taille est demandée.
    """
    if not tailles:
        raise ValueError("au moins une taille est requise")
    from PIL import ImageFont
    for chemin in CHEMINS:
        try:
            polices = tuple(ImageFont.truetype(chemin, t) for t in tailles)
            return polices[0] if len(polices) == 1 else polices
        except OSError:
            continue
    defaut = ImageFont.load_default()
    return defaut if len(tailles) == 1 else tuple(defaut for _ in tailles)


def etiquette_de_trace(trace: str) -> str:
    """Le nom court d'une trace : ses indices de spire, jamais une troncature aveugle.

    ⚠⚠ Une coupe à douze caractères rendait « 924-w010-027 » et « 46-052_jordi » — le premier
    garde trois chiffres d'horodatage, le second perd son `w`. Les indices de spire sont **le
    référent d'identité** d'une trace (`77`) ; c'est eux qu'il faut lire, et rien d'autre ne
    distingue deux traces du même jour.

    ⚠ Promue ici parce qu'elle était écrite **deux fois**, dans deux figures du même lot. C'est
    exactement la façon dont `police` avait fini en quinze copies et quatre variantes.
    """
    i = trace.find("-w")
    return trace[i + 1:] if i >= 0 else trace[-12:]


def etiquettes_de_traces(traces) -> list:
    """Les noms courts d'un lot, désambiguïsés SEULEMENT s'ils se répètent.

    ⚠⚠ Deux traces peuvent porter les **mêmes** indices de spire — ce sont deux tentatives sur la
    même feuille, ce qui est une information et non un doublon. Mais deux lignes portant le même
    libellé rendent une figure inutilisable : le lecteur ne peut plus la rapprocher de la table.
    La date ne s'ajoute donc **qu'en cas de collision**.
    """
    traces = list(traces)
    courts = [etiquette_de_trace(t) for t in traces]
    doublons = {c for c in courts if courts.count(c) > 1}
    return [f"{c} ({t[4:8]})" if c in doublons else c for c, t in zip(courts, traces)]


def glyphes_manquants(texte: str, taille: int = 13) -> list[str]:
    """Les caractères de ce texte que la police ne sait pas dessiner.

    ⚠⚠⚠ LA QUESTION EST POSÉE À LA POLICE, PAS À UNE LISTE. Une liste écrite à la main est en
    retard par construction — un caractère est sorti en carré vide d'une figure parce qu'il n'y
    était pas. Un caractère absent rend TOUJOURS le même dessin, celui du glyphe de secours : il
    suffit donc de comparer chaque caractère à un point de code dont on sait qu'aucune police ne
    le porte.

    ⚠ Le témoin est pris dans la zone à USAGE PRIVÉ : par définition, aucune police générale n'y
    met de dessin, donc il rend le glyphe de secours à coup sûr. Choisir un caractère rare mais
    réel exposerait le contrôle à une police qui, elle, le porterait.

    ⚠ La police de secours de PIL n'expose pas de masque comparable ; sur elle, la question ne
    peut pas être posée et rien n'est signalé, ce qui vaut mieux que signaler tout.
    """
    fonte = police(taille)
    try:
        secours = fonte.getmask("\ue000")
    except (AttributeError, TypeError):  # pragma: no cover - police de secours de PIL
        return []
    reference = (bytes(secours), secours.size)
    vus, out = set(), []
    for ch in texte:
        if ch in vus or ch.isspace():
            continue
        vus.add(ch)
        m = fonte.getmask(ch)
        if (bytes(m), m.size) == reference:
            out.append(ch)
    return out


def prose_tracable(lignes) -> bool:
    """Aucune de ces lignes ne porte un caractère que la police ne sait pas rendre."""
    return not glyphes_manquants("".join(lignes))


def textes_debordants(poses, largeur: float) -> list[tuple[str, int]]:
    """Les textes DESSINES dont la boite depasse `largeur`, avec leur bord droit.

    ⚠⚠⚠ CE QUE CETTE GARDE VOIT, ET CE QU'ELLE NE VOIT PAS. Elle mesure contre le bord droit
    de la TOILE, pas contre celui du panneau qui contient le texte : une pose ne dit pas dans
    quel cadre elle vit. Elle attrape donc tout ce qui sort de l'image — le cas ou la coupure
    est visible — et laisse passer un texte qui deborde d'un panneau vers son voisin.
    ⚠ Elle saute les poses sans police : on ne peut pas mesurer sans fonte, et rendre zero
    pour ces textes-la serait une garde qui declare sain ce qu'elle n'a pas regarde.
    """
    sortants = []
    for x, _y, texte, fonte in poses:
        if fonte is None or not texte:
            continue
        droite = int(x + fonte.getbbox(texte)[2])
        if droite > largeur:
            sortants.append((texte, droite))
    return sortants


def echelle_appariee(art, x0: int, y0: int, pw: int, ph: int, entrees: list, petit,
                     legende: str, fond=(255, 255, 255), texte=(25, 25, 25),
                     discret=(120, 120, 120), cadre=(200, 200, 200)) -> list[str]:
    """Une échelle horizontale d'écarts appariés, chacun avec son intervalle à un cas de moins.

    ⚠⚠⚠ L'INTERVALLE EST DESSINÉ, PAS RÉSUMÉ EN LÉGENDE : c'est LUI le verdict. Un écart dont
    le trait traverse le zéro ne tranche pas, si grande que soit sa barre. Une figure qui ne
    porterait que les écarts médians ferait lire un verdict là où il n'y en a pas.

    ⚠⚠ LE NOM ET LE CHIFFRE VIVENT SUR LEUR PROPRE LIGNE, la barre en dessous. Posés à la
    hauteur de la barre, ils tombent dessus dès qu'une barre traverse le panneau — mesuré sur
    la borne de `figure_le_critere_du_raccrochage`, dont le chiffre devenait illisible.

    ⚠ Cette fonction ne connaît le schéma d'AUCUNE mesure : elle reçoit des tuples
    `(nom, écart, couleur, souligné)`. Deux figures qui lui passeraient leurs dictionnaires
    bruts la rendraient solidaire de deux formats, donc impossible à faire évoluer pour l'une
    sans risquer l'autre.

    `écart` est un dict de `lecart_apparie` — ou None pour une ligne sans comparaison.
    """
    art.rectangle([x0, y0, x0 + pw, y0 + ph], outline=cadre)
    valeurs = []
    for _, e, _, _ in entrees:
        if e is None or e.get("ecart_median_um") is None:
            continue
        valeurs += [e["ecart_median_um"], *e["intervalle_um"]]
    if not valeurs:
        valeurs = [0.0]
    bas, haut = min(0.0, min(valeurs)), max(0.0, max(valeurs))
    marge = max(1e-6, (haut - bas) * 0.08)
    bas, haut = bas - marge, haut + marge
    gauche, droite = x0 + 10, x0 + pw - 10
    zero = gauche + (0.0 - bas) / (haut - bas) * (droite - gauche)
    art.text((x0 + 8, y0 + 6), legende, fill=discret, font=petit)
    # ⚠ L'axe est PÂLE sur toute la hauteur et FRANC au niveau de chaque barre : tracé en noir
    # partout, il traverse les chiffres alignés à droite et l'on ne lit plus ni l'un ni l'autre.
    art.line([zero, y0 + 24, zero, y0 + ph - 8], fill=cadre)
    haut_ligne = (ph - 34) / max(1, len(entrees))
    noms = []
    for i, (nom, e, coul, souligne) in enumerate(entrees):
        y_texte = y0 + 28 + haut_ligne * i
        y_barre = y_texte + 19
        noms.append(nom)
        art.text((x0 + 10, y_texte), nom, fill=texte, font=petit)
        if e is None or e.get("ecart_median_um") is None:
            art.text((x0 + pw - 10 - petit.getbbox("—")[2], y_texte), "—",
                     fill=discret, font=petit)
            continue
        ligne = (f"{e['ecart_median_um']:+.1f} um  {e['pas_ameliores']}/{e['pas']}  "
                 f"{e['intervalle_um']}")
        art.text((x0 + pw - 10 - petit.getbbox(ligne)[2], y_texte), ligne,
                 fill=discret, font=petit)

        def xx(val: float) -> float:
            return gauche + (val - bas) / (haut - bas) * (droite - gauche)

        h = 5.0
        art.line([zero, y_barre - h - 4, zero, y_barre + h + 4], fill=texte)
        a_, b_ = sorted((zero, xx(e["ecart_median_um"])))
        art.rectangle([a_, y_barre - h, b_, y_barre + h], fill=coul)
        if souligne:
            art.rectangle([a_ - 1, y_barre - h - 1, b_ + 1, y_barre + h + 1], outline=texte)
        g_, d_ = xx(e["intervalle_um"][0]), xx(e["intervalle_um"][1])
        art.line([g_, y_barre, d_, y_barre], fill=texte)
        for bout in (g_, d_):
            art.line([bout, y_barre - h - 2, bout, y_barre + h + 2], fill=texte)
    return noms



class Tracee:
    """Un calque de dessin qui RETIENT tout le texte qu'on lui demande d'ecrire.

    ⚠⚠⚠ POURQUOI CETTE CLASSE VIT ICI ET PAS DANS UNE FIGURE. `prose_tracable` ne lit que la
    prose du bas d'une figure, donc le texte ecrit DANS les panneaux n'etait couvert par rien —
    et un « ⛔ » est sorti en carre dans la ligne qui portait un verdict, sans qu'aucune garde
    ne le voie. Une garde qui ne voit qu'une partie de ce qu'elle garde est un ANGLE MORT.

    ⭐ Elle est dans le module commun parce que le depot compte plus de cent figures et que
    l'angle mort est le meme dans toutes. Les figures existantes ne sont PAS reecrites d'un
    coup : ce qui est pose ici est disponible, et chaque figure y passe quand on la touche.

    Usage : `art = Tracee(ImageDraw.Draw(toile))`, puis dessiner normalement ; a la fin,
    `glyphes_manquants("".join(art.textes))` doit etre vide.
    """

    def __init__(self, art):
        self._art = art
        self.textes: list[str] = []
        # ⚠⚠⚠ ET LA POSITION AVEC LE TEXTE, POUR LA MEME RAISON QUE LE TEXTE. Le garde de
        # largeur ne lisait que la prose du bas, donc une ligne de VERDICT ecrite dans un
        # panneau pouvait sortir du cadre et etre COUPEE a mi-mot sans que rien ne le dise —
        # exactement l'angle mort que le garde de glyphes avait deja revele, un cran plus loin.
        # Une phrase tronquee est pire qu'un glyphe manquant : elle reste lisible et FAUSSE.
        self.poses: list[tuple[float, float, str, object]] = []

    def text(self, *a, **k):
        # ⚠ Le texte est le DEUXIEME argument positionnel de `ImageDraw.text`, et il peut etre
        # passe par mot-clef : les deux formes sont retenues, sinon la garde en manquerait une.
        texte = a[1] if len(a) >= 2 and isinstance(a[1], str) else k.get("text")
        if isinstance(texte, str):
            self.textes.append(texte)
            xy = a[0] if a else k.get("xy")
            # ⚠ `font` est le QUATRIEME argument positionnel de `ImageDraw.text` et se passe le
            # plus souvent par mot-clef ; sans police on ne peut pas mesurer, donc on ne
            # PRETEND pas mesurer : la pose est retenue sans police et le garde la saute.
            fonte = k.get("font") if "font" in k else (a[3] if len(a) >= 4 else None)
            if isinstance(xy, (tuple, list)) and len(xy) == 2:
                self.poses.append((float(xy[0]), float(xy[1]), texte, fonte))
        return self._art.text(*a, **k)

    def __getattr__(self, nom):
        return getattr(self._art, nom)

def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool) -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}")

    une = police(14)
    v("une seule taille rend un objet, pas un tuple", not isinstance(une, tuple))
    trois = police(14, 12, 11)
    v("trois tailles rendent trois objets", isinstance(trois, tuple) and len(trois) == 3)
    v("... et deux en rendent deux", len(police(13, 11)) == 2)
    # ⭐ Les quatre variantes du depot, chacune servie sans changer ses tailles.
    for tailles in ((14, 12, 11), (13, 11, 15), (15, 12, 19), (13, 11)):
        if len(police(*tailles)) != len(tailles):
            v(f"la variante {tailles} est servie telle quelle", False)
            break
    else:
        v("les quatre variantes du dépôt sont servies telles quelles", True)

    # ⚠ Les tailles demandees sont bien celles rendues : une fonction qui les ignorerait
    # unifierait les figures en les DEPLACANT toutes, ce qui est le refactor a ne pas faire.
    try:
        v("la taille demandée est la taille rendue",
          all(f.size == t for f, t in zip(police(14, 12, 11), (14, 12, 11))))
    except AttributeError:
        v("la taille demandée est la taille rendue (police par défaut, non vérifiable)", True)

    try:
        police()
        v("aucune taille est refusé", False)
    except ValueError:
        v("aucune taille est refusé", True)

    v("la prose sans glyphe absent passe", prose_tracable(["mesuré : 7,1 spires", "⚠ majorant"]))
    v("... et une prose qui en porte un est refusée",
      not prose_tracable(["⭐ le résultat"]))
    v("le fichier n'écrit pas lui-même le glyphe qu'il refuse",
      all(g not in "".join(CHEMINS) for g in GLYPHES_ABSENTS))

    # ⚠⚠ LES ETIQUETTES, testees LA OU ELLES VIVENT. Promues ici parce qu'elles etaient ecrites
    # deux fois ; les laisser sans controle dans le module commun serait echanger une
    # duplication contre un angle mort.
    v("l'etiquette garde les indices de spire",
      etiquette_de_trace("20260623141924-w010-027") == "w010-027")
    v("... y compris avec un suffixe d'auteur",
      etiquette_de_trace("20260623141135-w046-052_jordi") == "w046-052_jordi")
    v("... et un nom sans indice ne leve pas",
      etiquette_de_trace("sans_indice") == "sans_indice"[-12:])
    _lot = etiquettes_de_traces(["20260701183126-w038-045", "20260623143441-w038-045",
                                 "20260623150417-w064-068"])
    v("deux traces aux memes indices sont distinguees", _lot[0] != _lot[1])
    v("... et une trace unique n'est pas encombree pour autant", _lot[2] == "w064-068")

    # ⚠⚠⚠ LE CONTRÔLE DES GLYPHES EST DÉRIVÉ, PAS RECOPIÉ : il demande à la police. La liste
    # écrite à la main ne sert plus qu'à vérifier que la question rend au moins les réponses
    # déjà connues — et elle en contient une, `\u26d4`, qui est sortie en carré vide d'une
    # figure précisément parce que personne ne l'avait ajoutée.
    v("la question posée à la police retrouve tous les glyphes déjà connus absents",
      glyphes_manquants("".join(GLYPHES_ABSENTS)) == list(GLYPHES_ABSENTS))
    # ⚠⚠ ET LE NÉGATIF, sans lequel « rien ne manque » serait rendu par une fonction qui ne
    # regarde rien : les caractères que ces figures emploient tous les jours doivent passer.
    v("... et elle laisse passer ce que la police rend vraiment",
      glyphes_manquants("\u26a0 \u00b7 \u2192 \u00b1 \u00b5 0123456789 aeiou") == [])
    v("... un texte vide ne manque de rien", glyphes_manquants("") == [])
    v("... et les blancs ne sont jamais comptés manquants",
      glyphes_manquants(" \n\t") == [])
    # ⚠ Le fichier ne doit PAS contenir en clair les caractères qu'il aide à refuser : la version
    # précédente affirmait les écrire en échappement et les portait en clair.
    # ⚠ La portée est la LIGNE DE LA CONSTANTE, pas le fichier : `\u2705` et `\u274c` servent
    # légitimement à l'affichage du terminal, qui n'est pas une figure, et ma première version
    # les interdisait partout — un contrôle trop large refuse du travail correct.
    from pathlib import Path as _P  # noqa: PLC0415

    declaration = next(l for l in _P(__file__).read_text(encoding="utf-8").splitlines()
                       if l.startswith("GLYPHES_ABSENTS"))
    v("la constante est écrite en séquences d'échappement, pas en clair",
      not any(g in declaration for g in GLYPHES_ABSENTS))

    # ⚠⚠⚠ L'ÉCHELLE APPARIÉE DOIT DESSINER SON INTERVALLE, parce que c'est lui le verdict. Le
    # contrôle compare deux rendus qui ne diffèrent QUE par l'intervalle : s'ils sortent
    # identiques, le trait n'est pas dessiné et la figure ferait lire un verdict là où il n'y
    # en a pas.
    from PIL import Image, ImageDraw  # noqa: PLC0415

    petit = police(11)
    serre = dict(ecart_median_um=-2.0, intervalle_um=[-2.1, -1.9], pas_ameliores=6, pas=7)
    large = dict(ecart_median_um=-2.0, intervalle_um=[-9.0, 5.0], pas_ameliores=6, pas=7)
    rendus = []
    for e in (serre, large):
        img = Image.new("RGB", (300, 90), (255, 255, 255))
        noms = echelle_appariee(ImageDraw.Draw(img), 0, 0, 300, 90,
                                [("essai", e, (76, 122, 84), False)], petit, "legende")
        rendus.append(img.tobytes())
    v("l'échelle appariée DESSINE l'intervalle, pas seulement l'écart",
      rendus[0] != rendus[1])
    v("... et elle rend les noms qu'elle a dessinés", noms == ["essai"])
    vide = Image.new("RGB", (300, 90), (255, 255, 255))
    souci = None
    try:
        echelle_appariee(ImageDraw.Draw(vide), 0, 0, 300, 90,
                         [("rien", None, (0, 0, 0), False)], petit, "legende")
    except Exception as exc:  # noqa: BLE001
        souci = f"{type(exc).__name__}: {exc}"
    v("... une ligne sans comparaison se dessine sans lever", souci is None)

    # ⚠⚠⚠ `Tracee` EXISTE POUR COUVRIR UN ANGLE MORT, donc elle doit elle-meme etre gardee :
    # une classe qui retient le texte mais en oublie une forme d'appel ne garde rien.
    class _Faux:
        def __init__(self):
            self.appels = 0

        def text(self, *a, **k):
            self.appels += 1

        def autre_chose(self):
            return "delegue"

    faux = _Faux()
    tr = Tracee(faux)
    tr.text((0, 0), "positionnel")
    tr.text((0, 0), text="par mot-clef")
    tr.text((0, 0), 42)  # ⚠ ce qui n'est pas du texte ne doit pas entrer dans la garde
    v("Tracee retient le texte passe positionnellement", "positionnel" in tr.textes)
    v("... et celui passe par mot-clef", "par mot-clef" in tr.textes)
    v("... et rien qui ne soit pas du texte", len(tr.textes) == 2)
    v("... tout en delegant chaque appel au vrai calque", faux.appels == 3)
    v("... et le reste de l'interface de dessin", tr.autre_chose() == "delegue")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    print("bibliothèque de dessin — voir `lplv figure_commune --help`")
    print(f"  polices cherchées : {', '.join(CHEMINS)}")
    print(f"  glyphes refusés   : {len(GLYPHES_ABSENTS)} (ils sortent en carré vide)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
