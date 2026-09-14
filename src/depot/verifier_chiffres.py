#!/usr/bin/env python3
"""Chaque chiffre de la soumission est-il encore celui que son fichier de résultat dit ?

⚠⚠ **Ce fichier existe parce que `docs/21` porte une tâche qu'un humain ne tiendra pas :**
*« revérifier chaque chiffre contre son fichier de sortie, le jour de l'envoi »*. Une
intention n'est pas une vérification. Ce dépôt a déjà payé la version douce du problème —
deux cartouches embarquées dont la fraîcheur était *contrôlée* alors que **rien ne pouvait
les rafraîchir**, et qui avaient dérivé vers deux mises en forme différentes.

Le principe est délibérément grossier, et c'est ce qui le rend robuste : chaque chiffre
est **recalculé depuis son JSON**, formaté comme la prose l'écrit, puis **cherché
littéralement** dans le document. Pas de balise à poser dans le texte, donc rien à
maintenir en double.

⚠ Ce que ça NE vérifie pas : qu'un chiffre présent soit au bon endroit, ni que la phrase
autour dise vrai. Un contrôle qui prétendrait ça mentirait sur sa portée.

⚠⚠ **Et une écriture trop courte ne vérifie rien du tout.** Chercher « 80 » ou « 10 » dans
un document en prose le trouve toujours — le contrôle passe alors au vert sans pouvoir
échouer, ce qui est exactement le défaut que ce fichier existe pour empêcher ailleurs.
Trouvé en ajoutant les chiffres de `25`, et il touchait **deux entrées antérieures**. Une
écriture est donc jugée **discriminante** ou non, et les non-discriminantes sont
**rapportées à part** : elles ne comptent ni comme réussite ni comme échec. Le remède pour
en faire de vraies vérifications est d'écrire le chiffre **avec son contexte** — « 10 fois
sur 12 » plutôt que « 10 ».
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
from carte_segments import MEME_FEUILLE_UM, VOISINES_UM  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]


# ⚠⚠ **Le document qui PART merite son propre controle.** Les chiffres du dossier sont
# recopies a l'anglaise (`12.97`) depuis une prose francaise (`12,97`), donc chacun traverse
# une transcription a la main que rien ne relisait : la recherche « le chiffre apparait
# quelque part » est satisfaite par le document source, et une faute de frappe dans le
# dossier passe. Les entrees nommees ici doivent apparaitre DANS le document de soumission,
# pas seulement dans un document du depot.
CITES_PAR_LA_SOUMISSION = (
    "aire utile de l'extension",
    "arc de l'extension",
    "sommets valides de l'extension",
    "segments publies du rouleau",
    "paires qui se recouvrent",
    "paires de la meme feuille",
    "paires de nappes voisines",
    "ecart de la paire la plus proche",
)


# ⚠⚠ **Et l'article aussi.** Il recopie ses chiffres a l'anglaise depuis une prose
# francaise, exactement comme le dossier de soumission, et il part vers un lectorat qui ne
# peut pas les recouper. Sa section « Reproducibility » affirme que chaque nombre du texte
# est recalcule depuis son fichier et cherche litteralement dans la source : cette liste
# est ce qui rend l'affirmation vraie plutot que flatteuse.
CITES_PAR_L_ARTICLE = (
    "gain a 20 %",
    "p de la decision",
    "rho avec_matiere x encre",
    "part rigide Scroll 1",
    "p du test des signes sur l'aire",
    "paires informatives du test des signes",
    "p des paires informatives",
    "rouleaux qui basculent",
    "sommets valides de l'extension",
    "alpha de officiel",
    "alpha de notre trace",
    "segments publies du rouleau",
    "dispersion aux deux plafonds",
    "traces de planarite au plafond",
    "AUC de la epaisseur de trait",
    "AUC de la nettete du pic",
    "AUC de la separabilite des lignes",
    "rho de la separabilite des lignes",
    # ⚠⚠ Ajoutes le 2026-08-22 avec la section 3.5 de l'article. Un lecteur de preprint ne
    # peut pas recouper : si l'article cite un chiffre, ce chiffre doit etre cherche DANS
    # l'article et pas seulement quelque part dans le depot. Ces deux-la portent toute la
    # moitie rassurante de `49` -- si un jour ils se croisaient, une serie convergente
    # deviendrait indiscernable de son plafond.
    "plus petit alpha indiscernable",
    "plus grand alpha convergent",
    # ⚠⚠ Ajoutes le 2026-09-03 avec la section 6.2. Elle est ce qui tient la promesse que
    # la section 2.4 faisait deja -- « Section 6.2 shows what that costs » -- et qui restait
    # en l'air : l'article ARGUMENTAIT pour des barres d'erreur sans en montrer une seule.
    "AUC groupee du fragment, frag1",
    "AUC groupee du fragment, frag2",
    "AUC groupee du fragment, frag3",
    "erreur type par tuiles, frag1",
    "erreur type par tuiles, frag2",
    "erreur type par tuiles, frag3",
    "facteur contre Hanley-McNeil, frag1",
    "facteur contre Hanley-McNeil, frag2",
    "facteur contre Hanley-McNeil, frag3",
    "dispersion des AUC DANS un fragment",
    "dispersion des AUC ENTRE fragments",
    "part attribuable au fragment",
    "tuiles necessaires par fragment",
    "rho du transport, aire_mediane_px",
    "p de Holm, aire_mediane_px",
    "p de Holm, sigma",
    # ⚠⚠ Ajoutes le 2026-09-03 avec la section 6.6. Elle tient la troisieme promesse de
    # la section 2.4 -- « a judge with a control condition » -- qui etait annoncee comme un
    # apport du papier et n'avait aucune section derriere elle.
    # ⚠ Ajoutes le 2026-09-03 avec le caveat de la section 6.1.
    "paires de rouleaux separees",
    "rouleaux distinguables apres Holm",
    "puissance a 25 fenetres",
    "puissance a 50 fenetres",
    "rho entre carte creuse et carte dense",
    "rouleaux qui changent de rang",
    "estimations denses dans l'intervalle creux",
    "panneaux montres au juge",
    "fabrications du juge",
    "lisibilite maximale d'un panneau vierge",
    "lisibilite minimale d'un panneau de texte",
    # ⚠ Et ceux du temoin negatif, meme raison : ils portent la these etroite de `46`.
    "accord pixel des deux cartes",
    "sigma du controle positif",
    # ⚠⚠ Ajoutes le 2026-08-23 avec la limitation sur le cout d un rendu. Ce sont les
    # DEUX bornes de la memoire : celle qu on paie sans le savoir (le pic au defaut) et
    # celle qu on choisit (le pic plafonne). Un lecteur qui voudrait refaire la mesure
    # sur sa machine a besoin des deux, et de rien d autre.
    "pic RSS le plus bas",
    "pic RSS le plus haut",
)


def normaliser(t: str) -> str:
    """Aplatit ce qui diffère typographiquement sans rien dire de la valeur.

    ⚠⚠ **Un garde-fou qui crie au loup finit ignoré**, et celui-ci l'a fait à sa première
    exécution : la prose écrit le signe moins **typographique** (U+2212, « − ») là où
    `f"{x}"` produit le trait d'union ASCII. Il a donc annoncé « −0,382 absent » sur un
    document qui le contenait. Le remède n'est pas de relâcher la comparaison — c'est de
    normaliser exactement ce qui n'a pas de sens numérique : signes moins, espaces
    insécables, séparateur décimal.
    """
    return (t.replace("\u2212", "-").replace("\u2013", "-")
             .replace("\u00a0", " ").replace("\u202f", " "))


def discriminante(ecriture: str) -> bool:
    """Une écriture peut-elle être absente d'un document en prose ?

    Un nombre de trois caractères ou moins se rencontre par accident dans n'importe quel
    texte : un numéro de section, une taille d'échantillon, une année tronquée. On exige
    donc soit un séparateur décimal, soit un signe explicite, soit une longueur suffisante.
    """
    e = ecriture.strip()
    # ⚠⚠ Un separateur decimal NE SUFFIT PAS quand le nombre est court. Le 2026-08-20,
    # « 5,6 » a ete declare trouve dans un document ou il designait la part d'un tout autre
    # rouleau : dans un texte plein de pourcentages, trois caracteres et une virgule se
    # rencontrent par accident. Une ecriture doit donc etre longue ASSEZ, separateur ou pas.
    if len(e) >= 5:
        return True
    return (e[:1] in "+-") and len(e) >= 5


def ou_trouve(ecritures, textes: dict) -> list[str]:
    """Les documents qui contiennent l'une des écritures acceptées de ce chiffre.

    ⚠ Extrait de `main` pour être testable. Un garde-fou dont le cœur n'est appelable que
    par la ligne de commande ne peut pas être sondé, et c'est lui qui protège tous les
    chiffres publiés du dépôt.
    """
    return [d.name for d, t in textes.items()
            if any(normaliser(e) in t for e in ecritures)]


def documents_sans_garde(attendus, textes: dict) -> list[str]:
    """Les documents qui citent des nombres dont AUCUN n'est recalculé.

    ⚠ Un document SANS chiffre n'est pas concerné : il n'a rien à garder, et le lister
    ferait crier le garde sur une page de prose qui a raison.
    """
    gardes = set()
    for _, ecritures, _ in attendus:
        gardes.update(ou_trouve(ecritures, textes))
    return sorted(d.name for d in textes
                  if d.name not in gardes and any(c.isdigit() for c in textes[d]))


def perimee(attendu: str, textes: dict) -> list[str]:
    """Où vit l'ANCIENNE valeur de ce chiffre ?

    ⚠⚠ « ABSENT » et « périmé » sont deux diagnostics très différents, et la première
    version ne disait que le premier. Un chiffre absent demande de l'écrire ; un chiffre
    périmé demande de le REMPLACER, et il faut savoir où. Le compte de témoins de ce dépôt
    a fait payer cette différence trois fois dans une même journée : le garde disait
    « 45 batteries, 1322 controles ABSENT » et il fallait grep soi-même les trois documents
    qui citaient l'ancien.

    ⭐ On cherche la même phrase avec d'autres chiffres : c'est ce qui distingue « personne
    n'en parle » de « quelqu'un en parle et se trompe ».

    ⚠ Refuse les motifs trop peu spécifiques. Une chaîne qui n'est QUE des chiffres
    matcherait n'importe quel nombre du dépôt, et signalerait périmé un document qui parle
    d'autre chose — un garde qui crie à tort finit ignoré.
    """
    import re as _re
    # ⚠⚠ Il faut au moins une LETTRE. Ma premiere version exigeait seulement un caractere
    # non numerique, ce qui laisse passer « 0 / 4 » -- et « 0 / 1 » a exactement la meme
    # forme, donc le garde a accuse un document de citer une valeur perimee alors qu'il
    # parlait d'autre chose. Un garde qui crie a tort finit ignore, et c'est la deuxieme
    # fois que ce fichier le paie.
    if not _re.search(r"[A-Za-zÀ-ÿ]", attendu):
        return []
    # ⚠⚠⚠ IL FAUT UN MOT QUI NOMME LA QUANTITE, PAS SEULEMENT UNE LETTRE — et c'est la
    # QUATRIEME occurrence du meme mode d'echec dans ce fichier ; les deux premieres sont
    # nommees juste au-dessus, la troisieme etait celle des unites.
    #
    # Une fois les chiffres remplaces par un joker, `**276,9 µm**` devient `**<nombre> µm**`,
    # et `0,55 % a 86,00 %` devient `<nombre> % a <nombre> %`. Des dizaines de quantites
    # differentes partagent ces formes, donc le motif ne peut designer personne. Mesure du
    # defaut : sur un seul document, SIX accusations, dont DEUX portaient sur un bloc
    # fraichement ecrit et correct — le garde reprochait au HANDOFF une valeur du tiers MILIEU
    # alors qu'il citait celle du COEUR, et une etendue de mosaique alors qu'il ecrivait une
    # demi-feuille « de 82 a 91 ».
    #
    # ⭐ CE QUI DISCRIMINE EST LE NOM DE LA QUANTITE. Une unite (`µm`, `%`) et un connecteur
    # (`a`, `fois`, `partout`, `sur`) sont STRUCTURELS : ils apparaissent dans toutes les
    # phrases de mesure du depot. Si rien d'autre ne reste apres les avoir retires, l'ecriture
    # attendue ne nomme pas ce dont elle parle, et accuser serait tirer au sort un coupable.
    STRUCTURELS = (
        # unites
        "µm", "mm", "cm²", "cm", "px", "µs", "ms", "octets", "voxels", "voxel",
        "feuilles", "feuille", "tours", "tour", "bandes", "bande", "points", "point",
        # connecteurs et quantificateurs
        "partout", "environ", "jusqu", "contre", "entre", "fois", "sur", "de", "du",
        "des", "la", "le", "les", "et", "ou", "en", "au", "aux", "un", "une", "a",
        "paires", "paire", "cellules", "cellule", "lignes", "ligne",
    )
    reste = attendu.lower()
    for u in sorted(STRUCTURELS, key=len, reverse=True):
        reste = _re.sub(rf"(?<![a-zà-ÿ]){_re.escape(u)}(?![a-zà-ÿ])", " ", reste)
    reste = _re.sub(r"[^a-zà-ÿ]+", " ", reste)
    # ⚠ Un reste de moins de trois lettres ne nomme rien : `s`, `h`, `x` sont des unites ou
    # des symboles, pas des quantites.
    nommants = [mot for mot in reste.split() if len(mot) >= 3]
    # ⚠⚠⚠ ET IL EN FAUT DEUX, ce qui est la cinquieme et derniere forme du meme mode d'echec.
    # Un motif d'UN SEUL nom de quantite est partage par des quantites differentes : `79
    # segments` (le compte de la table du champ, tous corpus confondus) accusait le HANDOFF de
    # citer une valeur perimee alors qu'il ecrivait, correctement, les `80 segments` de
    # `Scroll1` que `52` publie. Aucun apparieur purement textuel ne peut les distinguer.
    # ⭐ Deux noms suffisent a lever l'ambiguite en pratique — « 45 batteries, 1322 controles »
    # en a deux, « 79 segments » un seul — et une ecriture attendue qui n'en porte qu'un peut
    # etre RENDUE plus specifique a l'enregistrement, ce que le mecanisme permet deja.
    if len(nommants) < 2:
        return []
    motif = _re.escape(attendu)
    # ⚠ `re.escape` protege les chiffres tels quels ; on les rouvre un par un.
    motif = _re.sub(r"(?:\\?[0-9])+(?:[.,](?:\\?[0-9])+)?", r"[-+0-9  .,]+", motif)
    try:
        rx = _re.compile(motif)
    except _re.error:
        return []
    out = []
    for d, t in textes.items():
        for i, ligne in enumerate(t.splitlines(), 1):
            m = rx.search(ligne)
            if m and m.group(0).strip() != attendu.strip():
                out.append(f"{d.name}:{i} dit « {m.group(0).strip()} »")
                break
    return out


def fr(x: float, n: int = 3) -> str:
    """Écrit un nombre à la française — la prose du dépôt utilise la virgule."""
    return f"{x:.{n}f}".replace(".", ",")


def en(x: float, n: int = 3) -> str:
    """Et à l'anglaise — le corps de la soumission est en anglais."""
    return f"{x:.{n}f}"


DOSSIER_MESURES = "docs/mesures"
"""⭐ Le SEUL endroit de ce fichier qui dit OÙ vivent les mesures.

⚠⚠ Il était écrit **quarante-quatre fois**, en `_source(racine, "x.json")`. Deux littéraux
séparés : aucune réécriture textuelle de `docs/<nom>.json` ne peut les voir, donc ranger
`docs/`
aurait fait manquer les quarante-quatre sources **sans un mot** — et chaque lecture est gardée
par `if p.exists():`, donc le contrôle serait resté vert en ne vérifiant plus rien. C'est la
« vérification incapable d'échouer » à l'échelle de tous les chiffres publiés du dépôt.
"""

_SOURCES: list[tuple[str, bool]] = []
"""Ce que le dernier `collecter()` a CHERCHÉ, et trouvé ou non. ⚠ Une liste écrite ailleurs
serait une seconde description de ce que ce fichier lit, libre de diverger de la première."""


def _source(racine: Path, nom: str) -> Path:
    """Le chemin d'une mesure, ENREGISTRÉ au passage.

    ⚠ L'enregistrement est le point : un `if p.exists():` qui échoue ne produit aucun symptôme,
    donc une mesure disparue rend le contrôle plus vert, pas plus rouge.
    """
    p = racine / DOSSIER_MESURES / nom
    _SOURCES.append((nom, p.exists()))
    return p


def sources_manquantes() -> list[str]:
    """Les mesures que le dernier `collecter()` a cherchées sans les trouver."""
    return sorted(n for n, vu in _SOURCES if not vu)


CARTES_ATTENDUES = (
    ("ink_segment_complet", "Scroll 1"),
    ("ink_20250702235910", "PHerc1447 s1"),
    ("ink_20250703025628", "PHerc1447 s2"),
    ("ink_20250703034159", "PHerc1447 s3"),
    ("ink_20251105093211", "PHerc1447 s4"),
)
"""Les cartes que `typographie_de_nos_cartes.json` DOIT contenir.

⚠⚠ La liste est écrite plutôt que déduite du fichier, et c'est tout l'intérêt : un garde-fou
qui garde « ce qu'il trouve » ne peut pas remarquer qu'il ne trouve plus rien. Une carte
renommée ou disparue doit faire ÉCHOUER, pas réduire le compte en silence.

⚠⚠⚠ CONSÉQUENCE À CONNAÎTRE : le compte de chiffres gardés est **auto-référent**. Il est
écrit dans `docs/mesures/temoins.json`, cité dans les documents, et ce garde-fou vérifie la
citation. Allonger cette liste change donc le compte, ce qui périme la citation — et il faut
**deux exécutions** pour que l'ensemble se stabilise : la première écrit le nouveau compte,
la seconde le vérifie. Ce n'est pas un clignotement, c'est un point fixe, et le savoir évite
de croire à une régression.
"""


def collecter(racine: Path) -> list[tuple[str, list[str], str]]:
    """(ce que c'est, écritures acceptables, d'où ça vient).

    ⚠ Plusieurs écritures par chiffre, parce qu'un même nombre s'écrit `+0,381` en
    français et `+0.381` en anglais, et que refuser l'une des deux ferait échouer le
    contrôle sur un document parfaitement juste.
    """
    _SOURCES.clear()
    out = []

    def ajoute(nom: str, valeur: float, n: int, source: str, signe: bool = False,
               unites: tuple[str, ...] = ()):
        """Enregistre un chiffre, avec ses deux écritures et, s'il le faut, son unité.

        ⚠⚠ **Pourquoi `unites` existe.** Un nombre de moins de cinq caractères est écarté
        par `discriminante` — « 5,6 » avait déjà été déclaré trouvé dans un document où il
        désignait un tout autre rouleau. Mais un chiffre COURT peut être exigé dans
        l'article, et alors les deux règles se contredisent : il est *requis* et
        *incontrôlable*, donc l'échec devient irréparable — écrire le nombre ne le répare
        pas. Le remède est celui que ce fichier conseille déjà ailleurs : **l'écrire avec
        son contexte**. « 1,81 Go » se cherche, « 1,81 » non.
        """
        s = "+" if (signe and valeur >= 0) else ""
        ecritures = [s + fr(valeur, n), s + en(valeur, n)]
        for u in unites:
            ecritures += [f"{s}{fr(valeur, n)} {u}", f"{s}{en(valeur, n)} {u}"]
        out.append((nom, ecritures, source))

    p = _source(racine, "decision_avec_matiere.json")
    if p.exists():
        d = json.loads(p.read_text())
        vingt = next((x for x in d["decisions"] if abs(x["part_ecartee"] - 0.20) < 1e-9), None)
        if vingt:
            ajoute("gain a 20 %", vingt["gain"], 3, p.name, signe=True)
            ajoute("p de la decision", vingt["p_permutation"], 4, p.name)
        # ⚠ Avec leur contexte : « 80 » nu se trouve dans n'importe quel texte.
        out.append(("n de la decision",
                    [f"n = {d['n']}", f"{d['n']} segments", f"{d['n']} published"],
                    p.name))

    p = _source(racine, "croisement_encre.json")
    if p.exists():
        d = json.loads(p.read_text())
        for c in d.get("correlations", []):
            if c["trace"] == "avec_matiere" and c["encre"] == "encre_contraste_p90_p50":
                ajoute("rho avec_matiere x encre", c["rho"], 3, p.name, signe=True)
        for c in d.get("partielles", []):
            if c["trace"] == "ecart_a_la_trace" and c["encre"] == "encre_contraste_p90_p50":
                ajoute("partielle ecart x encre", c["rho_partiel"], 3, p.name, signe=True)

    p = _source(racine, "table_champ.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠ Avec son contexte : « 21,7 » nu est trop court pour etre absent d'un texte.
        out.append(("part rigide Scroll 1",
                    [f"{fr(d['part_rigide_mediane']*100,1)} %",
                     f"{en(d['part_rigide_mediane']*100,1)} %"], p.name))
        out.append(("segments du champ",
                    [f"{d['segments']} segments", f"{d['segments']} published"], p.name))
        # ⚠⚠ Le seul rho ETOILE de `20` §6, et il n'etait garde par rien. C'est le
        # chiffre sur lequel un lecteur agit — « la seule grandeur qui predit » — donc
        # c'est celui dont la tracabilite compte. Les trois autres correlations du meme
        # tableau disent « rien ici » : leur derive ne change aucune decision, et les
        # enregistrer ferait quatre chiffres a garder pour un seul qui pese.
        rho_bord = d.get("correlations_encre", {}).get("part_au_bord")
        if rho_bord:
            ajoute("rho part_au_bord x encre", rho_bord["rho"], 3, p.name, signe=True)

    p = _source(racine, "robustesse_material.json")
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("accord des grilles", d["rho"], 3, p.name, signe=True)
        ajoute("temoin p95 des grilles", d["temoin_p95"], 3, p.name)

    p = _source(racine, "prediction_50um.json")
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("p du seuil de 50 um", d["p_seuil_propose"], 3, p.name)
        # ⚠ Les deux moyennes d'encre encadrent le seuil : c'est leur PAIRE qui est le
        # resultat, et l'ecrire comme une paire la rend verifiable là où chaque moitie,
        # a quatre caracteres, ne l'etait pas.
        out.append(("encre de part et d'autre du seuil",
                    [f"{fr(d['encre_au_dessus'],2)} contre {fr(d['encre_au_dessous'],2)}",
                     f"{fr(d['encre_au_dessus'],2)} vs {fr(d['encre_au_dessous'],2)}",
                     f"{en(d['encre_au_dessus'],2)} vs {en(d['encre_au_dessous'],2)}"],
                   p.name))

    p = _source(racine, "table_graines.json")
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("p du test des signes sur l'aire", d["signes_aire"]["p_signes"], 4, p.name)
        out.append(("planarite contre voisinage sur l'aire",
                    [f"planéité {d['signes_aire']['pour_planarite']}, voisinage "
                     f"{d['signes_aire']['pour_voisinage']}"], p.name))
        # ⚠⚠ Le partage informatif/tronque est ce qui rend le tableau lisible, et il
        # repose sur des COMPTES. Le premier jet en publiait 5 la ou il y en a 7, parce
        # qu'il cherchait le plafond dans les aires — un seuil qui n'a de sens qu'a une
        # seule resolution. Un compte faux qui a l'air plausible ne se relit pas.
        if d.get("budget_generations_atteint"):
            out.append(("traces de planarite au plafond",
                        [f"{d['planarite_au_plafond']} traces de planéité sur "
                         f"{d['rouleaux']}",
                         f"{d['planarite_au_plafond']} sur {d['rouleaux']} butent",
                         f"{d['planarite_au_plafond']} of the {d['rouleaux']} planarity"],
                        p.name))
            info = d.get("signes_aire_informatives") or {}
            if info:
                out.append(("paires informatives du test des signes",
                            [f"{info['n_paires']} paires informatives",
                             f"{info['n_paires']} informative pairs"], p.name))
                ajoute("p des paires informatives", info["p_signes"], 4, p.name)
        out.append(("rouleaux de la campagne",
                    [f"{d['rouleaux']} rouleaux du prix", f"sur {d['rouleaux']} rouleaux"],
                    p.name))
        # ⚠ Le zero cumule est le chiffre qui a CORRIGE la revendication : le « 240 -> 0 »
        # ne replique pas, les deux criteres rendent zero partout. Un garde-fou qui ne
        # tiendrait que les chiffres flatteurs ne garderait rien.
        out.append(("auto-intersections cumulees des deux criteres",
                    [f"{d['croisements_cumules']['planarite'] + d['croisements_cumules']['voisinage']} partout"],
                    p.name))

    # ⚠ Les chiffres du 2026-08-20. Chacun est ecrit AVEC son contexte : « 72 » ou « 240 »
    # nus se trouvent dans n'importe quel texte, donc `discriminante()` les rapporterait a
    # part au lieu de les verifier -- ce qui est le contraire d'un garde-fou.
    p = _source(racine, "table_tirages.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("tirages de la campagne",
                    [f"{d['tirages_total']} tirages", f"{d['tirages_total']} draws"], p.name))
        out.append(("rouleaux qui basculent",
                    [f"{len(d['rouleaux_bascule'])} rouleaux sur {d['rouleaux']}",
                     f"{len(d['rouleaux_bascule'])} of {d['rouleaux']} scrolls",
                     f"{len(d['rouleaux_bascule'])} sur {d['rouleaux']}"], p.name))
        # ⚠ Avec leur contexte : « 5,6 » nu a deja ete trouve par accident (cf.
        # `discriminante`). C'est la forme comptee qui est sans ambiguite.
        out.append(("taux de mauvais tirages",
                    [f"{d['mauvais']} / {d['tirages_total']} = {fr(d['taux_mauvais']*100,1)} %",
                     f"{d['mauvais']}/{d['tirages_total']} = {fr(d['taux_mauvais']*100,1)} %",
                     f"{d['mauvais']} mauvais tirages sur {d['tirages_total']}"], p.name))
        out.append(("intervalle du taux",
                    [f"{fr(d['ic95_bas']*100,1)} % – {fr(d['ic95_haut']*100,1)} %",
                     f"{fr(d['ic95_bas']*100,1)} % - {fr(d['ic95_haut']*100,1)} %"], p.name))

    p = _source(racine, "comparaison_cartes.json")
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("rho entre les deux campagnes", d["rho"], 3, p.name, signe=True)
        out.append(("rangs changes",
                    [f"{d['rangs_changes']}/{len(d['lignes'])} rouleaux",
                     f"{d['rangs_changes']} of {len(d['lignes'])} scrolls",
                     f"{d['rangs_changes']} rouleaux changent"], p.name))

    p = _source(racine, "incertitude_carte.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("paires separees",
                    [f"{d['paires_separees']} des {d['paires']} paires",
                     f"{d['paires_separees']} of the {d['paires']} pairs",
                     f"{d['paires_separees']} sur {d['paires']}"], p.name))
        out.append(("intervalle du temoin",
                    [f"{fr(d['temoin']['ic95'][0]*100,1)} % – "
                     f"{fr(d['temoin']['ic95'][1]*100,1)} %",
                     f"jusqu'à {fr(d['temoin']['ic95'][1]*100,1)} %"], p.name))

    p = _source(racine, "sensibilite_maillage.json")
    if p.exists():
        d = json.loads(p.read_text())
        brut = [l["brut"]["transverse"] for l in sorted(d["lignes"], key=lambda l: l["facteur"])]
        if len(brut) >= 4:
            out.append(("perte de sensibilite du detecteur",
                        [" → ".join(str(x) for x in brut[:4]),
                         " -> ".join(str(x) for x in brut[:4]),
                         ", ".join(str(x) for x in brut[:4])], p.name))

    # ⚠⚠ La chaine des spires : le compte de spires qui convergent, l'erosion par tour et
    # l'alpha de la spire qui casse sont TOUTE la revendication de `43`. Si l'un bouge et
    # que le document ne bouge pas, le document annonce une chaine qui n'existe plus.
    p = _source(racine, "chaine_spires.json")
    if p.exists():
        d = json.loads(p.read_text())
        if d:
            conv = sum(1 for l in d if l["verdict"] == "converge")
            out.append(("spires qui convergent",
                        [f"**{conv} spires sur {len(d)} convergent",
                         f"{conv} spires sur {len(d)}",
                         f"{conv} sur {len(d)}"], p.name))
            a0, a1 = d[0]["aire_grille_cm2"], d[-1]["aire_grille_cm2"]
            tours = len(d) - 1
            if a0 and tours:
                par = 100 * (1 - a1 / a0) / tours
                out.append(("erosion par tour",
                            [f"{fr(par, 1)} % par tour", f"{par:.1f} % par tour"], p.name))
                out.append(("aires de la chaine",
                            [f"{fr(a0, 2)} → {fr(a1, 2)} cm²",
                             f"{a0:.2f} → {a1:.2f} cm²"], p.name))
            casse = [l for l in d if l["verdict"] == "suit la fenêtre"]
            if casse:
                out.append(("alpha de la spire qui casse",
                            [f"**{casse[0]['alpha']:+.3f}**",
                             f"{fr(casse[0]['alpha'], 3)}",
                             f"{casse[0]['alpha']:+.3f}"], p.name))

    # ⚠⚠ La chaine a pas 0,25 (`43` §6quinquies) : le compte de convergences et les alphas
    # des spires qui cassent sont la revendication entiere de la section -- « halver le pas
    # repousse la rupture d'un tour » n'a de sens que si ces nombres sont ceux-la.
    p = _source(racine, "chaine_pas025_convergence.json")
    if p.exists():
        d = json.loads(p.read_text()).get("series", [])
        if d:
            conv = sum(1 for x in d if x.get("verdict") == "converge")
            out.append(("convergences a pas 0,25",
                        [f"**{conv}/{len(d)}", f"{conv}/{len(d)}",
                         f"{conv} sur {len(d)}"], p.name))
            for x in d:
                if x.get("verdict") == "suit la fenêtre":
                    a = x["alpha"]
                    out.append((f"alpha de {x['nom']} a pas 0,25",
                                [f"**+{fr(a, 3)}**", f"+{fr(a, 3)}",
                                 f"{a:+.3f}"], p.name))

    # ⚠⚠ L'EXTENSION TANGENTIELLE (`44`) : ces chiffres sont la revendication la plus forte
    # du depot -- la premiere surface que nous produisons qui GAGNE de l'aire sans quitter sa
    # feuille -- et ils sont publies dans trois documents. En cablant cette garde j'ai
    # d'ailleurs trouve deux erreurs a moi : « 13,02 cm2 d'aire utile » melangeait l'aire du
    # meta avec l'aire utile (12,97), et « le rayon devient determine » venait du tirage NON
    # deterministe alors que le run reproductible le laisse indetermine.
    p = _source(racine, "geometrie_extension.json")
    if p.exists():
        d = json.loads(p.read_text())
        bons = [x for x in d.get("spires", []) if x.get("angle_rad", 0.0) > 0]
        if bons:
            e = bons[0]
            out.append(("aire utile de l'extension",
                        [f"**{fr(e['aire_valide_cm2'], 2)} cm²**",
                         f"{fr(e['aire_valide_cm2'], 2)} cm²",
                         f"{en(e['aire_valide_cm2'], 2)} cm²"], p.name))
            out.append(("arc de l'extension",
                        [f"**{fr(e['arc_mm'], 1)} mm**", f"{fr(e['arc_mm'], 1)} mm",
                         f"{en(e['arc_mm'], 1)} mm"], p.name))
            out.append(("sommets valides de l'extension",
                        [f"**{e['fraction_valide'] * 100:.0f} %**",
                         f"{e['fraction_valide'] * 100:.0f} %"], p.name))
            out.append(("fraction de tour de l'extension",
                        [f"**{fr(e['fraction_de_tour'] * 100, 1)} %**",
                         f"{fr(e['fraction_de_tour'] * 100, 1)} %"], p.name))
            # ⚠ Le rayon est-il determine ? La reponse est publiee, donc elle est gardee.
            out.append(("verdict de rayon de l'extension",
                        ["déterminé"] if e.get("rayon_determine") else ["indéterminé"],
                        p.name))
        if len(bons) >= 2 and bons[1].get("espacement_um") is not None:
            # ⭐ Le controle de reproductibilite, mesure par un second instrument.
            out.append(("écart entre les deux répétitions",
                        [f"**{bons[1]['espacement_um']:.0f} µm**",
                         f"écart de {bons[1]['espacement_um']:.0f} µm"], p.name))

    # ⚠⚠ Le recensement de FRAGILITE. Ce chiffre est publie dans DEUX documents (`44` §8bis
    # et la section 12 de la soumission) et c'est lui qui justifie de ne jamais comparer des
    # comptes de verdicts. Il se recalcule depuis les series, pas depuis un champ stocke : un
    # verdict ecrit hier a ete rendu par les seuils d'hier.
    # ⚠ Un GLOB ne peut pas être manquant : il rend ce qu il trouve. Il passe donc
    # par le même dossier, mais il n entre pas au registre des sources.
    verdicts = sorted((racine / DOSSIER_MESURES).glob("spire_*.json"))
    if verdicts:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tc", racine / "src" / "commun" / "test_convergence.py")
        tc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tc)
        # ⚠⚠ DEDOUBLONNER PAR CONTENU. Deux campagnes peuvent produire des maillages
        # identiques octet pour octet -- c'est arrive le 2026-08-22, `spires_pic025` et
        # `spires_pas0125_compense` ne differant que par un parametre INERTE. Compter leurs
        # verdicts deux fois gonfle le denominateur d'un recensement avec dix mesures qui
        # sont la meme mesure. La cle est la SERIE, parce que c'est la donnee ; deux series
        # egales sont le meme verdict, quel que soit le dossier qui les porte.
        vus: set = set()
        n = fragiles = doublons = 0
        pire = None
        for f in verdicts:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for serie in d.get("series", []):
                r = tc.analyser([tuple(x) for x in serie["serie"]])
                if "fragile" not in r:
                    continue
                cle = tuple(tuple(x) for x in serie["serie"])
                if cle in vus:
                    doublons += 1
                    continue
                vus.add(cle)
                n += 1
                if r["fragile"]:
                    fragiles += 1
                    if pire is None or r["marge_au_seuil"] < pire:
                        pire = r["marge_au_seuil"]
        if doublons:
            out.append(("verdicts en double ecartes du recensement",
                        [f"**{doublons} verdicts** identiques",
                         f"{doublons} verdicts identiques",
                         f"{doublons} en double"], "spire_*.json"))
        if n:
            out.append(("verdicts fragiles",
                        [f"**{fragiles} verdicts fragiles sur {n}**",
                         f"{fragiles} verdicts fragiles sur {n}",
                         f"{fragiles} verdicts sur {n}", f"{fragiles} sur {n}",
                         f"{fragiles} of our {n} wrap verdicts"], "spire_*.json"))
        if pire is not None:
            out.append(("marge du verdict le plus fragile",
                        [f"**{fr(pire, 3)}**", f"{fr(pire, 3)} du seuil",
                         f"{pire:.3f}"], "spire_*.json"))

    # ⚠⚠ La comparaison des campagnes A PROFONDEUR EGALE (`43` §6quinquies) : l'optimum du
    # pas du rayon EST la revendication de la section, et c'est un α, pas un compte. Si l'un
    # de ces nombres bouge sans que la page bouge, la page annonce un optimum qui a change
    # de place.
    p = _source(racine, "comparaison_pas_rayon.json")
    if p.exists():
        d = json.loads(p.read_text())
        for c in d.get("campagnes", []):
            pr = c.get("pas_du_rayon")
            if pr is None:
                continue
            out.append((f"alpha moyen a pas {pr:g}",
                        [f"**{fr(c['alpha_moyen'], 3)}**", f"+{fr(c['alpha_moyen'], 3)}",
                         f"{c['alpha_moyen']:+.3f}"], p.name))
            out.append((f"alpha du pire tour a pas {pr:g}",
                        [f"**{fr(c['alpha_max'], 3)}**", f"+{fr(c['alpha_max'], 3)}",
                         f"{c['alpha_max']:+.3f}"], p.name))
        # ⭐ L'optimum lui-meme : lequel des pas gagne, et de combien.
        bons = [c for c in d.get("campagnes", []) if c.get("pas_du_rayon")]
        if bons:
            best = min(bons, key=lambda c: c["alpha_moyen"])
            pv = f"{best['pas_du_rayon']:g}".replace(".", ",")
            out.append(("pas du rayon optimal",
                        [f"**pas {pv}**", f"pas {pv}", f"optimum … {pv}",
                         f"{best['pas_du_rayon']:g}"], p.name))
            out.append(("profondeur commune de comparaison",
                        [f"les {d['profondeur_commune']} premiers tours",
                         f"{d['profondeur_commune']} premiers tours"], p.name))

    # ⚠⚠ La geometrie de la chaine (`44`) : ces cinq chiffres SONT la page. L'ecart entre
    # nappes est le seul qui dise que la chaine avance d'une feuille a la fois ; l'erosion
    # utile CORRIGE un chiffre publie dans `43` (4,0 % contre 15,6 %) ; et le nombre de
    # fenetres par tour porte la conclusion structurelle. Si l'un bouge sans que la page
    # bouge, la page annonce une chaine qui n'existe plus.
    p = _source(racine, "geometrie_pas025.json")
    if p.exists():
        d = json.loads(p.read_text())
        bons = [x for x in d.get("spires", []) if x.get("angle_rad", 0.0) > 0]
        if len(bons) >= 2:
            esp = sorted(x["espacement_um"] for x in bons
                         if x.get("espacement_um") is not None)
            if esp:
                med = esp[len(esp) // 2]
                out.append(("ecart median entre nappes",
                            [f"**{med:.0f} µm**", f"{med:.0f} µm",
                             f"médiane {med:.0f} µm"], p.name))
                out.append(("plage des ecarts",
                            [f"de {esp[0]:.0f} à {esp[-1]:.0f}",
                             f"{esp[0]:.0f} à {esp[-1]:.0f}"], p.name))
            a0, a1 = bons[0]["aire_valide_cm2"], bons[-1]["aire_valide_cm2"]
            tours = len(bons) - 1
            if a0 > 0 and a1 > 0 and tours:
                par = 100 * (1 - (a1 / a0) ** (1 / tours))
                out.append(("erosion UTILE par tour",
                            [f"**{fr(par, 1)} % par tour**", f"{fr(par, 1)} % par tour",
                             f"{par:.1f} % par tour"], p.name))
                out.append(("aires utiles de la chaine",
                            [f"{fr(a0, 2)} → {fr(a1, 2)} cm²",
                             f"{a0:.2f} → {a1:.2f} cm²"], p.name))
            f0 = bons[0]["fraction_valide"] * 100
            f1 = bons[-1]["fraction_valide"] * 100
            out.append(("part de sommets valides",
                        [f"de {f0:.0f} % à {f1:.0f} %", f"{f0:.0f} % à {f1:.0f} %",
                         f"{f0:.0f} % → {f1:.0f} %"], p.name))
            nmin = min(x["spires_par_tour_min"] for x in bons)
            out.append(("fenetres par tour (minorant)",
                        [f"au moins **{nmin:.0f}**", f"au moins {nmin:.0f}",
                         f"AU MOINS {nmin:.0f}"], p.name))
            indet = sum(1 for x in bons if not x.get("rayon_determine"))
            out.append(("nappes au rayon indetermine",
                        [f"**{indet} nappes sur {len(bons)}**",
                         f"{indet} nappes sur {len(bons)}",
                         f"{indet} sur {len(bons)}"], p.name))
            total = sum(x["aire_valide_cm2"] for x in bons)
            out.append(("aire utile totale de la chaine",
                        [f"**{fr(total, 1)} cm²**", f"{fr(total, 1)} cm²",
                         f"{total:.1f} cm²"], p.name))

    # ⚠⚠ Le CONTROLE de `44` §8 : si le rho de l'indice de spire cesse de battre les
    # candidats, la page dit l'inverse de ce qui est mesure. C'est le seul chiffre de ce
    # depot dont la valeur REFUTE une conclusion plutot que de la porter.
    # ⚠⚠ Le juge, ajoute le 2026-09-03 avec la section 6.6 de l'article. Les chiffres sont
    # RECALCULES depuis les reponses brutes plutot que recopies du document, et le critere
    # est ecrit ici parce que j'en ai d'abord pris un faux : une FABRICATION est un panneau
    # vierge ou le juge rapporte des LETTRES, pas un panneau ou il omet de refuser en mots.
    # Avec le mauvais critere le fichier rendait « 2 fabrications » sur un juge qui n'en a
    # commis aucune -- une accusation publiee aurait ete indefendable.
    # ⚠⚠ La carte de difficulte, ajoutee le 2026-09-03 avec le caveat de la section 6.1.
    # C'est la demonstration la moins chere de la these de l'article -- une barre d'erreur
    # annule un classement -- et elle porte sur NOTRE propre conclusion publiee, donc ses
    # chiffres doivent etre gardes comme les autres.
    ic = _source(racine, "incertitude_carte.json")
    if ic.exists():
        d = json.loads(ic.read_text())
        out.append(("paires de rouleaux separees",
                    [f"{d['paires_separees']} of {d['paires']} pairs",
                     f"{d['paires_separees']} sur {d['paires']} paires"], ic.name))
        out.append(("rouleaux distinguables apres Holm",
                    [f"{len(d['distinguables_holm'])} of {len(d['lignes'])}",
                     f"{len(d['distinguables_holm'])} sur {len(d['lignes'])}"], ic.name))
        # ⚠ Seules les deux valeurs que l'article CITE sont enregistrees. Collecter les
        # quatre faisait rapporter « 99 % » et « 100 % » comme perimes a chaque execution :
        # un chiffre que personne ne cite est un chiffre que le garde-fou signale pour
        # toujours, et un signal permanent cesse d'etre lu.
        for e in d.get("puissance", []):
            if e["n"] not in (25, 50):
                continue
            out.append((f"puissance a {e['n']} fenetres",
                        [f"{e['puissance'] * 100:.0f} % power",
                         f"{e['puissance'] * 100:.0f} % de puissance"], ic.name))
    cc = _source(racine, "comparaison_cartes.json")
    if cc.exists():
        d = json.loads(cc.read_text())
        ajoute("rho entre carte creuse et carte dense", d["rho"], 3, cc.name, signe=True)
        out.append(("rouleaux qui changent de rang",
                    [f"{d['rangs_changes']} of {len(d['lignes'])} scrolls change rank",
                     f"{d['rangs_changes']}/{len(d['lignes'])} rouleaux changent de rang"],
                   cc.name))
        dans = sum(1 for l in d["lignes"] if l["dense_dans_ic_creux"])
        out.append(("estimations denses dans l'intervalle creux",
                    [f"{dans} of the {len(d['lignes'])}", f"{dans} des {len(d['lignes'])}"],
                    cc.name))

    jr = _source(racine, "juge_resultats.json")
    if jr.exists():
        d = json.loads(jr.read_text())
        vierges, textes, fabrications, panneaux = [], [], 0, 0
        for r in d.get("records", []):
            for cote in ("gauche", "droite"):
                panneaux += 1
                verite, rep = r["truth"][cote], r["parsed"][cote]
                if verite == "vierge":
                    if rep.get("glyphs", 0) > 0:
                        fabrications += 1
                    vierges.append(rep.get("legibility") or 0)
                else:
                    textes.append(rep.get("legibility") or 0)
        out.append(("panneaux montres au juge",
                    [f"{panneaux} panels", f"{panneaux} panneaux"], jr.name))
        out.append(("fabrications du juge",
                    [f"{fabrications} fabrications", f"zero fabrication",
                     f"no fabrication"], jr.name))
        if vierges and textes:
            out.append(("lisibilite maximale d'un panneau vierge",
                        [f"{max(vierges)} on a blank", f"{max(vierges)} sur un vierge"],
                        jr.name))
            out.append(("lisibilite minimale d'un panneau de texte",
                        [f"{min(textes)} on a text panel", f"{min(textes)} sur un texte"],
                        jr.name))

    p = _source(racine, "juge_a_un_rendu.json")
    if p.exists():
        d = json.loads(p.read_text())
        for clef, j in (d.get("juges") or {}).items():
            if not j.get("assez"):
                continue
            # ⚠ La prose francaise ecrit « +0,445 » : signe ET virgule. Les variantes ne
            # portaient que « 0,445 » et « +0.445 », donc AUCUNE ne matchait le document et
            # six chiffres justes etaient rapportes absents. Un garde-fou qui crie au loup
            # sur des chiffres corrects finit ignore.
            signe = "+" if j["rho"] >= 0 else "−"
            out.append((f"rho de {clef} contre alpha",
                        [f"{signe}{fr(abs(j['rho']), 3)}", f"**{fr(j['rho'], 3)}**",
                         f"ρ = {fr(j['rho'], 3)}", f"{j['rho']:+.3f}"], p.name))

    # ⚠⚠ Le test de convergence : les deux α sont la revendication ENTIERE de la section 11
    # de la soumission. Si l'un bouge et que le texte ne bouge pas, le texte annonce une
    # separation qui n'existe plus — et c'est la seule chose que cette section apporte.
    p = _source(racine, "convergence.json")
    if p.exists():
        d = json.loads(p.read_text())
        for s_ in d.get("series", []):
            court = "officiel" if "officiel" in s_["nom"] else "notre trace"
            a = s_["alpha"]
            out.append((f"alpha de {court}",
                        [f"**{a:+.2f}**", f"α = {a:+.2f}", f"{a:+.2f}"], p.name))
            serie = s_["serie"]
            out.append((f"serie de {court}",
                        [f"{serie[0][1]:.2f} µm → {serie[-1][1]:.2f} µm",
                         f"{fr(serie[0][1], 2)} µm", f"{serie[0][1]:.2f} µm"], p.name))

    # ⚠ La mosaique : les trois chiffres qui font sa revendication. « 44 spires sans
    # trou » est ce que l'image PRETEND etre ; si une spire venait a manquer, le document
    # dirait toujours 44 et l'image ressemblerait toujours a un rouleau.
    p = _source(racine, "mosaique_PHerc0172.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("spires de la mosaique",
                    [f"{d['bandes']} spires", f"**{d['bandes']} spires"], p.name))
        out.append(("etendue de la mosaique",
                    [f"{d['spire_min']:03d} à {d['spire_max']:03d}",
                     f"{d['spire_min']:03d} → {d['spire_max']:03d}",
                     f"de la {d['spire_min']:03d} à la {d['spire_max']:03d}"], p.name))
        out.append(("spires manquantes",
                    ["sans un trou" if not d["trous"] else
                     f"{len(d['trous'])} spire(s) manquante(s)"], p.name))
        ecart = round(100 * (1 - d["largeur_min_bande"] / d["largeur_max_bande"]))
        out.append(("ecart de largeur des bandes",
                    [f"{d['largeur_min_bande']} à {d['largeur_max_bande']} px, soit {ecart} %",
                     f"{ecart} %"], p.name))
        out.append(("taille de la mosaique",
                    [f"{d['largeur_px']} × {d['hauteur_px']} px"], p.name))

    # ⚠⚠ La carte des segments publies : la conclusion « il n'y a rien a raccorder »
    # repose entierement sur des COMPTES, et un compte est ce qui derive le plus
    # silencieusement. Le premier jet du document publiait « 49 paires eloignees » la ou
    # 45 avaient ete mesurees — les 4 autres etant hors de portee, donc eloignees pour une
    # raison que le tableau ne disait pas. Personne ne relit une somme de trois nombres.
    p = _source(racine, "segments_PHerc1447.json")
    if p.exists():
        d = json.loads(p.read_text())
        segs, paires = d["segments"], d["paires"]
        n = len(segs)
        mes = sorted((x for x in paires if x.get("ecart_um") is not None),
                     key=lambda x: x["ecart_um"])
        hors = [x for x in paires if x.get("raison") == "hors_portee"]
        proches = [x for x in mes if x["ecart_um"] < MEME_FEUILLE_UM]
        voisines = [x for x in mes if MEME_FEUILLE_UM <= x["ecart_um"] < VOISINES_UM]
        loin = [x for x in mes if x["ecart_um"] >= VOISINES_UM]
        out.append(("segments publies du rouleau",
                    [f"{n} segments", f"{n} published segments"], p.name))
        out.append(("paires qui se recouvrent",
                    [f"{len(paires)} paires sur {n * (n - 1) // 2}",
                     f"{len(paires)} of {n * (n - 1) // 2}",
                     f"{len(paires)} of their {n * (n - 1) // 2} pairs"], p.name))
        out.append(("paires de la meme feuille",
                    [f"{len(proches)} paire sous {MEME_FEUILLE_UM:.0f} µm",
                     f"{len(proches)} pair under {MEME_FEUILLE_UM:.0f} µm",
                     f"{len(proches)} pairs under {MEME_FEUILLE_UM:.0f} µm"], p.name))
        out.append(("paires de nappes voisines",
                    [f"{len(voisines)} paires entre {MEME_FEUILLE_UM:.0f} et "
                     f"{VOISINES_UM:.0f} µm",
                     f"{len(voisines)} pairs between {MEME_FEUILLE_UM:.0f} and "
                     f"{VOISINES_UM:.0f} µm",
                     f"{len(voisines)} between {MEME_FEUILLE_UM:.0f} and "
                     f"{VOISINES_UM:.0f} µm"], p.name))
        out.append(("paires eloignees et hors de portee",
                    [f"{len(loin)} mesurées et {len(hors)} hors de portée",
                     f"{len(loin)} measured and {len(hors)} out of reach"], p.name))
        if mes:
            # ⚠ « 79 µm » nu se rencontre dans deux autres documents qui parlent d'autre
            # chose : l'ecriture doit porter son contexte, sinon le controle passe au vert
            # sur un chiffre homonyme — exactement le defaut que `discriminante` traque.
            out.append(("ecart de la paire la plus proche",
                        [f"encore à {mes[0]['ecart_um']:.0f} µm",
                         f"still {mes[0]['ecart_um']:.0f} µm apart"], p.name))

    # ⚠⚠ Le depot se compte lui-meme. `README` annoncait « 18 batteries, 741 controles »
    # alors qu'il y en avait 24 et 1092 : le chiffre avait ete recopie a la main et n'avait
    # aucun producteur, donc rien ne pouvait le rafraichir ni le contredire. C'est le meme
    # defaut que les deux cartouches embarquees qui avaient derive, un etage plus haut.
    # ⚠⚠ La mesure de `35` §3bis : la stabilite des rouleaux plafonnes etait-elle une
    # troncature ? Le verdict tient dans deux dispersions medianes, donc dans deux
    # nombres — et un nombre qui porte un verdict est le premier a deriver.
    p = _source(racine, "comparaison_plafond.json")
    if p.exists():
        d = json.loads(p.read_text())
        if d.get("dispersion_mediane_avant") is not None:
            out.append(("dispersion aux deux plafonds",
                        [f"{d['dispersion_mediane_avant']*100:.2f} % à "
                         f"{d['dispersion_mediane_apres']*100:.2f} %".replace(".", ","),
                         f"{d['dispersion_mediane_avant']*100:.2f}% to "
                         f"{d['dispersion_mediane_apres']*100:.2f}%",
                         f"{d['dispersion_mediane_avant']*100:.2f} % to "
                         f"{d['dispersion_mediane_apres']*100:.2f} %"], p.name))
        out.append(("plafonds confrontes",
                    [f"{d['plafond_avant']} générations contre {d['plafond_apres']}",
                     f"{d['plafond_avant']} contre {d['plafond_apres']}"], p.name))

    # ⚠⚠ La typographie (`45`) : son resultat tient dans un tableau d'AUC, donc dans des
    # nombres, et le plus important d'entre eux est celui qui va A CONTRE-SENS. Un chiffre
    # inattendu est le premier qu'on est tente d'arrondir dans le bon sens.
    p = _source(racine, "typographie.json")
    if p.exists():
        d = json.loads(p.read_text())
        cr = d.get("croisement_encre") or {}
        for nom, court in (("epaisseur_trait_px", "epaisseur de trait"),
                           ("nettete_mediane", "nettete du pic"),
                           ("part_periodique", "separabilite des lignes")):
            g = (cr.get("grandeurs") or {}).get(nom)
            if g and g.get("auc") is not None:
                ajoute(f"AUC de la {court}", g["auc"], 3, p.name)
                if g.get("rho") is not None:
                    ajoute(f"rho de la {court}", g["rho"], 3, p.name, signe=True)
        r = d.get("resume") or {}
        if r.get("PHercParis4"):
            x = r["PHercParis4"]
            out.append(("cartes ecrites du premier rouleau",
                        [f"{x['cartes_ecrites']}/{x['n']}"], p.name))

    # ⚠⚠ `37` publiait « 0/4 d'accord » et « 1 accord sur 8 » sans qu'aucun producteur ne les
    # recalcule -- c'est-a-dire des anecdotes au sens de la regle du depot, alors que les
    # deux JSON les portent en clair. L'inventaire des documents non gardes l'a nomme.
    vus = []
    for prof in (21, 41, 81, 161):
        q = _source(racine, f"second_axe_{prof}.json")
        if not q.exists():
            continue
        d = json.loads(q.read_text())
        a, n = d.get("accords") or {}, d.get("rouleaux_testables")
        # ⚠ Un balayage a UN seul rouleau testable n'est pas une comparaison : `37` porte sur
        # les rendus 21 et 41, les seuls qui en aient plusieurs. Garder les autres publierait
        # des chiffres qu'aucun document ne cite -- du bruit dans un tableau dont toute la
        # valeur est que chaque ligne compte.
        if n and n >= 2:
            # ⚠ Un accord par AXE mesure : l'ecart a la trace et la part au bord sont deux
            # jugements, et `37` les rapporte separement. Les additionner ici perdrait la
            # distinction que le document tient.
            for cle in ("ecart_um", "au_bord"):
                if a.get(cle) is not None:
                    out.append((f"accords {cle}, rendu {prof}",
                                [f"{a[cle]} / {n}", f"{a[cle]}/{n}"], q.name))
            vus.append(prof)
    # ⚠⚠ PAS de total croise. `37` met en avant « 1 accord sur 8 » ; ma reconstruction donnait
    # « 1 sur 16 », parce que je ne sais pas comment le document agrege ses deux criteres --
    # quatre tirages fois deux fenetres, ou fois deux axes ? Re-deriver une agregation avec
    # une hypothese produit un nombre qui a l'air autorise et qui CONTREDIT sa source. Les
    # quatre chiffres par balayage, eux, sont exacts et verifies ; ils suffisent.

    # ⚠⚠ Les PLANCHERS DE DETECTION des quatre corpus du tri a distance. Sans eux, « trois
    # corpus non positifs » se lit comme trois refutations -- alors qu'aucun des trois
    # n'avait la puissance de voir l'effet mesure sur le premier. Un zero se rapporte avec
    # sa puissance, ou il ne se rapporte pas.
    for nom, fichier in (("Scroll 1", "croisement_encre.json"),
                         ("PHerc0139", "croisement_encre_PHerc0139.json"),
                         ("PHerc1667", "croisement_encre_PHerc1667.json"),
                         ("PHerc0172", "croisement_encre_0172.json")):
        q = _source(racine, fichier)
        if not q.exists():
            continue
        d = json.loads(q.read_text())
        if d.get("rho_detectable") is not None:
            ajoute(f"plancher detectable, {nom}", d["rho_detectable"], 3, q.name)
        c = [x for x in (d.get("correlations") or [])
             if x.get("trace") == "avec_matiere"
             and x.get("encre") == "encre_contraste_p90_p50"]
        if c:
            ajoute(f"rho du tri, {nom}", c[0]["rho"], 3, q.name, signe=True)

    p = _source(racine, "paris4_2x2.json")
    if p.exists():
        d = json.loads(p.read_text())
        for t in d.get("cases") or []:
            if t.get("alpha_median") is not None:
                ajoute(f"alpha, {t['prediction']} sur graine {t['graine']}",
                       t["alpha_median"], 2, p.name, signe=True)
        e = d.get("effet_prediction") or {}
        if e.get("max") is not None:
            ajoute("ecart des deux predictions", e["max"], 2, p.name)
        if d.get("bruit_retenu") is not None:
            ajoute("bruit retenu du 2x2", d["bruit_retenu"], 2, p.name)

    # ⚠ Les deux alphas du controle de resolution : c est LA revendication de `50` §7, et
    # si un jour ils s ecartaient de plus de la resolution declaree, la fenetre profonde
    # cesserait d etre mesurable sans que rien d autre ne le dise.
    alphas = {}
    for f in sorted(racine.glob("docs/mesures/resolution_g*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        niv = f.stem.split("g")[-1]
        for x in (d.get("series") or ([d] if "alpha" in d else [])):
            if isinstance(x.get("alpha"), (int, float)):
                alphas[niv] = x["alpha"]
                ajoute(f"alpha au niveau {niv}", x["alpha"], 2, f.name, signe=True)
    if len(alphas) >= 2:
        v = sorted(alphas.values())
        ajoute("ecart entre niveaux de pyramide", v[-1] - v[0], 2, "resolution_g*.json")

    # ⚠⚠ Le verdict du plafond de generations : deux alphas, leur variation et le bruit
    # auquel on la compare. Si le bruit baissait sans que la variation baisse, la
    # conclusion « stable » basculerait -- et rien d autre ne le dirait.
    for f in sorted(racine.glob("docs/plafond_ps256_c2_g*_niv*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        for x in (d.get("series") or ([d] if "alpha" in d else [])):
            if isinstance(x.get("alpha"), (int, float)):
                m = re.search(r"_g(\d+)_niv(\d+)", f.stem)
                if m:
                    ajoute(f"alpha du budget {m.group(1)} au niveau {m.group(2)}",
                           x["alpha"], 2, f.name, signe=True)
    pv = _source(racine, "plafond_ps256_c2_niv1.json")
    if pv.exists():
        d = json.loads(pv.read_text())
        for cle, nom in (("variation", "variation du plafond"),
                         ("bruit_de_tirage", "bruit de tirage du plafond")):
            if isinstance(d.get(cle), (int, float)):
                ajoute(nom, d[cle], 2, pv.name, signe=(cle == "variation"))

    # ⚠⚠ Le test du critere relatif. Le nombre qui compte n est pas un beta mais le COMPTE
    # de grandeurs lisibles en absolu : s il montait sans qu on ait ajoute de mesure, c est
    # qu un refus aurait cesse de refuser.
    p = _source(racine, "critere_relatif.json")
    if p.exists():
        d = json.loads(p.read_text())
        lis = [g for g in d.get("grandeurs") or []
               if g.get("verdict") == "lisible en absolu"]
        out.append(("grandeurs lisibles en absolu", [str(len(lis))], p.name))
        out.append(("series a deux profondeurs", [str(d.get("series_utilisables"))], p.name))
        for g in d.get("grandeurs") or []:
            if g.get("saturees", 0) >= 50:
                out.append((f"series saturees sur {g['grandeur']}",
                            [str(g["saturees"])], p.name))

    p = _source(racine, "appui_de_pente.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("series jugeables par leurs appuis", [str(d.get("series_jugees"))],
                    p.name))
        for cle, nom in (("exacte", "series a deux appuis mesures"),
                         ("majorant", "series dont alpha est un majorant"),
                         ("minorant", "series dont alpha est un minorant"),
                         ("aucune", "series sans appui qui porte")):
            v = (d.get("par_borne") or {}).get(cle)
            if v is not None:
                out.append((nom, [str(v)], p.name))
        out.append(("series dont le verdict tombe",
                    [str(len(d.get("series_qui_tombent") or []))], p.name))
        out.append(("series sauvees par le signe",
                    [str(len(d.get("series_sauvees_par_le_signe") or []))], p.name))
        out.append(("series convergentes", [str(d.get("convergents"))], p.name))
        # ⚠⚠ LE CONTRASTE, qui est le constat le plus fort du document : aucune serie
        # convergente n a de fenetre etroite plate. Un contre-exemple futur doit etre
        # bruyant, donc les quatre comptes sont gardes.
        # ⚠⚠ Ecrits en PAIRE, jamais nus. « 0 » et « 34 » font un et deux caracteres : le
        # garde ne peut pas les chercher, et un ✅ dessus ne voudrait rien dire. C est le
        # conseil que ce fichier donne ailleurs, applique au constat le plus fort de `51`.
        c = d.get("contraste_des_appuis") or {}
        for a, b, nom in (("convergentes_appui_etroit_plat", "convergentes",
                           "convergentes a fenetre etroite plate"),
                          ("condamnees_appui_etroit_plat", "condamnees",
                           "condamnees a fenetre etroite plate")):
            if c.get(a) is not None and c.get(b) is not None:
                out.append((nom, [f"{c[a]} / {c[b]}", f"{c[a]}/{c[b]}"], p.name))
        # ⚠⚠ Les DEUX signaux compares : c est ce qui dit que l outil PUBLIC publie le
        # moins bon des deux. Ecrits en paire, jamais nus -- « 0 » et « 34 » ne se cherchent
        # pas dans un texte en prose.
        for nom, cle in (("amplitude sous le plancher", "amplitude_sous_le_plancher"),
                         ("pic au bord sur 90 pourcent", "au_bord_au_moins_90_pourcent")):
            g = ((c.get("signaux_compares") or {}).get(cle)) or {}
            for pop in ("convergentes", "condamnees"):
                x = g.get(pop)
                if x:
                    out.append((f"{nom}, {pop}",
                                [f"{x['compte']} / {x['sur']}", f"{x['compte']}/{x['sur']}"],
                                p.name))
        # ⚠⚠ Le chiffre qui porte tout `51` : combien de series rendent l IDENTITE de leur
        # couple de fenetres. Sans garde, il vieillirait en silence a la prochaine campagne.
        if d.get("series_sur_une_identite") is not None:
            out.append(("series sur l identite du couple de fenetres",
                        [str(d["series_sur_une_identite"])], p.name))
        for x in d.get("identites_du_couple_de_fenetres") or []:
            if x.get("colle_a_l_identite"):
                ajoute(f"alpha d identite {x['couches'][0]}c/{x['couches'][1]}c",
                       x["alpha"], 4, p.name)

    p = _source(racine, "calibration_scroll1.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("segments du balayage", [str(d.get("corpus"))], p.name))
        out.append(("geometries de lecture du corpus",
                    [str(d.get("geometries"))], p.name))
        for g in d.get("groupes") or []:
            geo = g.get("geometrie") or {}
            n = geo.get("layers")
            # ⚠ Seul le groupe PRINCIPAL est garde : un groupe d un seul segment n a pas de
            # distribution a laisser vieillir, et le garder ferait du bruit a chaque
            # balayage.
            if (g.get("relief") or {}).get("n", 0) < 10:
                continue
            for cle, nom in (("min", "relief minimal du corpus"),
                             ("mediane", "relief median du corpus"),
                             ("max", "relief maximal du corpus")):
                v = (g.get("relief") or {}).get(cle)
                if v is not None:
                    ajoute(f"{nom} a {n} couches", v, 3, p.name)
            out.append((f"segments du corpus a {n} couches",
                        [str((g.get("relief") or {}).get("n"))], p.name))
            if g.get("sous_le_plancher") is not None:
                out.append((f"segments sous le plancher a {n} couches",
                            [str(g["sous_le_plancher"])], p.name))
            if g.get("au_bord_90") is not None:
                out.append((f"segments a edge_pinned 90 a {n} couches",
                            [str(g["au_bord_90"])], p.name))

    p = _source(racine, "situer_notre_trace.json")
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("relief de notre trace a la geometrie du corpus", d["relief"], 4, p.name)
        out.append(("rang de notre trace dans le corpus",
                    [f"{d['rang']}ᵉʳ sur {d['corpus_n']}",
                     f"{d['rang']} sur {d['corpus_n']}"], p.name))
        if d.get("rapport_a_la_mediane") is not None:
            out.append(("rapport de notre trace a la mediane publiee",
                        [f"×{fr(d['rapport_a_la_mediane'], 2)}",
                         f"x{fr(d['rapport_a_la_mediane'], 2)}"], p.name))

    p = _source(racine, "situer_nos_traces.json")
    if p.exists():
        d = json.loads(p.read_text())
        for cle, nom in (("n", "candidats situes dans le corpus"),
                         ("plates_a_la_geometrie_du_corpus",
                          "candidats plats a la geometrie du corpus"),
                         ("sous_tout_le_corpus", "candidats sous tout le corpus"),
                         ("au_premier_rang", "candidats au premier rang")):
            if d.get(cle) is not None:
                out.append((nom, [str(d[cle])], p.name))
        # ⚠ Les bornes du groupe qui MESURE : ce sont elles qui disent que la coupure entre
        # les deux predictions est nette, et elles doivent vieillir bruyamment.
        mesurent = [x["relief"] for x in d.get("traces") or [] if x["relief"] > 0]
        if mesurent:
            ajoute("relief minimal des candidats qui mesurent", min(mesurent), 3, p.name)
            ajoute("relief maximal des candidats qui mesurent", max(mesurent), 4, p.name)

    p = _source(racine, "effet_taille_fenetre.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠⚠ Ces chiffres ont RETIRE un repere du README public. Ils doivent vieillir
        # bruyamment : si l effet de la taille de fenetre s averait plus petit qu annonce,
        # la mise en garde publiee changerait de force.
        if d.get("exposant_taille") is not None:
            ajoute("exposant du relief contre la taille de fenetre",
                   d["exposant_taille"], 3, p.name, signe=True)
        if d.get("rapport_extreme") is not None:
            # ⚠ Ecrit AVEC son signe multiplicatif et jamais nu : « 3,16 » fait quatre
            # caracteres et se rencontre partout, donc un ✅ dessus ne voudrait rien dire.
            out.append(("rapport de relief entre 1024 et 256 px",
                        [f"×{fr(d['rapport_extreme'], 2)}",
                         f"x{fr(d['rapport_extreme'], 2)}",
                         f"×{en(d['rapport_extreme'], 2)}"], p.name))
        for m in d.get("mesures") or []:
            if m.get("amplitude") is not None:
                ajoute(f"relief a {m['taille']} px", m["amplitude"], 3, p.name)

    p = _source(racine, "fenetre_utilisable.json")
    if p.exists():
        d = json.loads(p.read_text())
        for etat, nom in (("couple confortable disponible", "series a couple confortable"),
                          ("couple disponible, sans marge", "series a couple sans marge"),
                          ("il faut rendre une fenêtre plus profonde",
                           "series demandant une fenetre plus profonde")):
            v = (d.get("par_etat") or {}).get(etat)
            if v is not None:
                out.append((nom, [str(v)], p.name))
        # ⚠ La profondeur cible des candidats : c est le chiffre sur lequel le prochain
        # rendu sera dimensionne, donc il doit vieillir bruyamment.
        for k, j in sorted((d.get("detail") or {}).items()):
            if "paris4_candidats/ps256" not in k:
                continue
            pr = j.get("prediction") or {}
            if pr.get("profondeur_cible") is not None:
                ajoute(f"profondeur cible {k.rsplit('/', 1)[-1]}",
                       pr["profondeur_cible"], 1, p.name)
        # ⚠⚠ L ecart d amplitude entre deux niveaux de pyramide : c est le chiffre qui
        # autorise (ou non) a rendre la fenetre suivante moins cher. Sans garde, il
        # vieillirait au premier rendu supplementaire.
        for x in d.get("amplitude_entre_niveaux") or []:
            if x.get("ecart_relatif") is None:
                continue
            # ⚠⚠ Ecritures SIGNEES ET UNITEES seulement, jamais la forme nue. « 0,4 » fait
            # trois caracteres : mesure, il apparait dans 36 documents du depot, donc un
            # ✅ dessus ne veut rien dire. C'est le conseil que ce fichier donne deja
            # ailleurs -- « 1,81 Go » se cherche, « 1,81 » non -- applique ici.
            pc = x["ecart_relatif"] * 100.0
            signe = "+" if pc >= 0 else "-"
            out.append((f"ecart d amplitude a {x['profondeur_um']:g} um",
                        [f"{signe}{fr(abs(pc), 1)} %", f"{signe}{en(abs(pc), 1)} %"],
                        p.name))

    p = _source(racine, "etalon_rendu.json")
    if p.exists():
        d = json.loads(p.read_text())
        r = d.get("resume") or {}
        # ⚠ Le pic de memoire par valeur : c est la colonne du tableau de `50`, et c est
        # elle qui autorise a plafonner le cache dans le chemin commun.
        par = {}
        for e in d.get("essais") or []:
            par.setdefault(e["cache_gb"], []).append(e["pic_rss_kio"] / 1048576.0)
        for gb, v in sorted(par.items()):
            x = sorted(v)
            med = x[len(x) // 2] if len(x) % 2 else (x[len(x)//2 - 1] + x[len(x)//2]) / 2
            ajoute(f"pic RSS a --cache-gb {gb}", med, 2, p.name, unites=("Go", "GB"))
        for cle, nom, n in (("pic_min_go", "pic RSS le plus bas", 2),
                            ("pic_max_go", "pic RSS le plus haut", 2),
                            ("etendue_intra_max_s", "etendue intra maximale", 1),
                            ("ecart_inter_s", "ecart entre valeurs de cache", 1),
                            ("marge_temps", "marge du temps", 2)):
            if r.get(cle) is not None:
                # ⚠ Les pics portent leur unite : sans elle « 1,81 » fait quatre caracteres
                # et `discriminante` l ecarte, alors que l article DOIT le citer.
                ajoute(nom, r[cle], n, p.name,
                       unites=("Go", "GB") if cle.endswith("_go") else ("s",))
        if r.get("recommande") is not None:
            out.append(("cache recommande", [str(r["recommande"])], p.name))
        out.append(("essais d etalonnage", [str(len(d.get("essais") or []))], p.name))

    p = _source(racine, "paris4_candidats.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠ L alpha de chaque candidat, garde individuellement : c est la ligne du tableau
        # de `48`, et un seul chiffre qui bouge sans que la campagne soit relancee est
        # exactement ce que ce fichier existe pour attraper.
        for l in d.get("lignes") or []:
            if isinstance(l.get("alpha"), (int, float)):
                ajoute(f"alpha du candidat {l['prediction']} c{l['candidat']}",
                       l["alpha"], 2, p.name, signe=True)
            # ⚠ Le NOMBRE DE DECIMALES gardees doit etre celui que le document ecrit,
            # pas le plus precis disponible. Garder l occupation a quatre decimales
            # forcerait « 0,7500 » dans un tableau ou trois suffisent a identifier la
            # valeur -- c est le garde qui imposerait sa mise en forme au texte, alors
            # qu il est la pour verifier le texte.
            for cle, n in (("planarite", 4), ("occupation", 3)):
                if isinstance(l.get(cle), (int, float)):
                    ajoute(f"{cle} de {l['prediction']} c{l['candidat']}",
                           l[cle], n, p.name)
        for cle, nom in (("candidats", "candidats traces"), ("avec_alpha", "candidats avec alpha"),
                         ("indecidables", "candidats indecidables"),
                         ):
            if d.get(cle) is not None:
                out.append((nom, [str(d[cle])], p.name))
        # ⚠ « convergents » est une LISTE de noms, pas un nombre : la garder telle quelle
        # afficherait « = [] », ce qui ne se cherche dans aucun texte et ne verifie rien.
        # C est son COMPTE que les documents citent.
        if isinstance(d.get("convergents"), list):
            out.append(("candidats convergents", [str(len(d["convergents"]))], p.name))
        # ⚠⚠ Le plancher de detection : c est LUI qui justifie le refus de conclure sur une
        # correlation. S il baissait sans qu on ajoute de points, le refus deviendrait faux.
        if d.get("rho_detectable") is not None:
            ajoute("plancher de correlation a huit points", d["rho_detectable"], 2, p.name)
        if d.get("etendue_relative_aires") is not None:
            ajoute("etendue relative des aires au plafond",
                   d["etendue_relative_aires"] * 100, 2, p.name)

    p = _source(racine, "audit_profils.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠⚠ Les deux nombres qui portent la conclusion de `49` sont les BORNES des deux
        # populations : si un jour elles se croisaient, une serie convergente deviendrait
        # indiscernable de son plafond et la moitie rassurante tomberait.
        for cle, nom, n in (("alpha_min_indiscernable", "plus petit alpha indiscernable", 4),
                            ("alpha_max_convergent", "plus grand alpha convergent", 4)):
            if d.get(cle) is not None:
                ajoute(nom, d[cle], n, p.name, signe=True)
        for cle, nom in (("profils", "profils lus"), ("series", "series de profils"),
                         ("plats", "profils plats"), ("au_plafond", "profils au plafond"),
                         ("series_jugees", "series jugees")):
            if d.get(cle) is not None:
                out.append((nom, [str(d[cle])], p.name))
        # ⚠ Les series que `42` CITE nommement, gardees parce qu'il les tabule. La liste est
        # tenue a la main et c'est assume : « les series qu'un document cite » n'est pas
        # derivable, et garder les 111 noierait le tableau dans du bruit. Si une entree
        # disparait, le garde le dit -- une entree nommee qui n'existe plus est un controle
        # mort, et `exiger` a deja ce reflexe.
        for cle in ("data/boucle/temoin", "data/boucle/corrige_gen5",
                    "data/boucle/corrige_gen5_poids100", "data/boucle/corrige_gen40"):
            j = (d.get("jugees") or {}).get(cle)
            if j and j.get("alpha_mesure") is not None:
                ajoute(f"alpha mesure, {cle.split('/')[-1]}", j["alpha_mesure"], 3, p.name,
                       signe=True)
        if d.get("series_utilisables_pour_un_critere_relatif") is not None:
            # ⚠ Ce compte contredit un « deux » ecrit dans `47`, qui portait en fait sur une
            # AUTRE population. Le garder sous garde evite que la correction se reperde.
            out.append(("series utilisables pour un critere relatif",
                        [str(len(d["series_utilisables_pour_un_critere_relatif"]))],
                        p.name))
        for cle, nom in (("series_entierement_plates", "series entierement plates"),
                         ("series_indiscernables_du_plafond", "series indiscernables"),
                         ("convergents_indiscernables", "convergents indiscernables")):
            if d.get(cle) is not None:
                out.append((nom, [str(len(d[cle]))], p.name))

    p = _source(racine, "excision_resume.json")
    if p.exists():
        d = json.loads(p.read_text())
        mw = d.get("mann_whitney") or {}
        mz = d.get("mann_whitney_sans_vide") or {}
        if mw.get("u"):
            # ⚠ U est un entier a onze chiffres : on l'ecrit avec les espaces fines que la
            # prose francaise utilise, ET sans, parce que les deux lectures existent.
            u = int(round(mw["u"]))
            out.append(("U de Mann-Whitney", [f"{u:,}".replace(",", " "), str(u)], p.name))
        for cle, nom, n in ((mw.get("p"), "p de l'excision", 3),
                            (mw.get("cliff_delta"), "delta de Cliff", 4),
                            (mz.get("p"), "p sans le vide", 3),
                            (mz.get("cliff_delta"), "delta de Cliff sans le vide", 4)):
            if cle is not None:
                ajoute(nom, cle, n, p.name, signe=(n == 4))
        for cote in ("excisees", "temoins"):
            if (d.get(cote) or {}).get("n"):
                # ⚠ La prose francaise groupe les milliers par une espace : « 75 810 ». La
                # premiere version ne cherchait que « 75810 » et rapportait absent un
                # chiffre present dans le document -- un garde qui crie a tort finit ignore.
                n_ = d[cote]["n"]
                out.append((f"cellules {cote}",
                            [f"{n_:,}".replace(",", " "), str(n_)], p.name))
            v_ = (d.get("part_vide") or {}).get(cote)
            if v_ is not None:
                out.append((f"part de vide, {cote}",
                            [f"{fr(v_ * 100, 1)} %", f"{fr(v_ * 100, 1)}%"], p.name))
        if d.get("niveaux_differents") is not None:
            out.append(("niveaux qui different",
                        [f"{d['niveaux_differents']}/{d['niveaux_vus']}"], p.name))

    p = _source(racine, "eligibilite_aval.json")
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("rouleaux tracables", [f"**{len(d['tracables'])}**",
                                           f"{len(d['tracables'])} rouleaux"], p.name))
        for nom, x in (d.get("lisibles") or {}).items():
            v_ = x["part_ecrite"] * 100
            out.append((f"part ecrite de {nom}",
                        [f"{fr(v_, 0)} %", f"{fr(v_, 0)}%", f"{en(v_, 0)} %"], p.name))
        if d.get("premier_candidat"):
            out.append(("premier candidat", [d["premier_candidat"]], p.name))

    p = _source(racine, "derive_profondeur.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠⚠ Les censures d'abord : c'est le chiffre qui porte la conclusion de `47`, et
        # le seul qui dise si un seuil absolu compare des surfaces ou des reglages.
        out.append(("traces au plafond, rendu bas",
                    [f"{d['censurees_en_bas']}/{d['lignes_en_bas']}"], p.name))
        out.append(("traces au plafond, rendu haut",
                    [f"{d['censurees_en_haut']}/{d['lignes_en_haut']}"], p.name))
        for cle, nom in (("plafond_bas_um", "plafond du rendu bas"),
                         ("plafond_haut_um", "plafond du rendu haut")):
            if d.get(cle) is not None:
                ajoute(nom, d[cle], 2, p.name)
        if d.get("rapport_plafonds") is not None:
            ajoute("rapport des plafonds", d["rapport_plafonds"], 2, p.name)
        for x in d.get("derives", []):
            for c, nom in (("derive_mediane", "derive mediane"), ("derive_max", "derive max")):
                if x.get(c) is not None:
                    ajoute(f"{nom} de {x['critere']}", x[c], 3, p.name)
            out.append((f"traces comparees de {x['critere']}",
                        [f"{x['n_compare']}"], p.name))
        if d.get("rho_au_bord_part_plates") is not None:
            ajoute("rho au_bord / part_plates", d["rho_au_bord_part_plates"], 3, p.name,
                   signe=True)
        for cle in ("plafonds_bas_um", "plafonds_haut_um"):
            for v_ in d.get(cle) or []:
                ajoute(f"plafond present ({cle})", v_, 2, p.name)

    p = _source(racine, "temoin_negatif.json")
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠⚠ Les chiffres qui portent la conclusion de `46`, et la PORTEE avec eux : sans
        # elle, le tableau se lirait comme la these forte, qui est hors de portee.
        if d.get("accord_pixel") is not None:
            ajoute("accord pixel des deux cartes", d["accord_pixel"], 4, p.name, signe=True)
        # ⚠⚠ Ces cinq-la sont des POURCENTAGES a une decimale, donc des chaines de trois
        # caracteres : trop courtes pour qu'une recherche litterale veuille dire quelque
        # chose dans un texte en prose. On les cherche AVEC leur signe, ce qui les rend
        # verifiables au lieu de les laisser dans la zone grise « ni reussite ni echec ».
        for cle, nom in (("ecart_median_en_variation_interne", "ecart des deux cartes"),
                         ("ecart_attendu_si_independantes", "ecart si etrangeres"),
                         ("part_du_modele_qui_marche", "sigma du positif rapporte au modele"),
                         ("ecart_relatif_sigma_entree", "ecart des deux entrees")):
            if d.get(cle) is not None:
                v = d[cle] * 100
                out.append((nom, [f"{fr(v, 1)} %", f"{fr(v, 1)}%",
                                  f"{en(v, 1)} %", f"{en(v, 1)}%"], p.name))
        for cote in ("positif", "negatif"):
            if d.get(cote, {}).get("sigma") is not None:
                ajoute(f"sigma du controle {cote}", d[cote]["sigma"], 4, p.name)
            e = d.get(f"entree_{cote}") or {}
            if e.get("sigma") is not None:
                ajoute(f"sigma de l'entree {cote}", e["sigma"], 2, p.name)
                v = e["part_non_nulle"] * 100
                out.append((f"part non nulle de l'entree {cote}",
                            [f"{fr(v, 1)} %", f"{fr(v, 1)}%",
                             f"{en(v, 1)} %", f"{en(v, 1)}%"], p.name))
        if d.get("porte"):
            out.append(("portee du temoin negatif", [d["porte"]], p.name))

    # ⚠⚠ Les piles VIDES, gardees parce que ce sont des chiffres de CORRECTION : ils disent
    # que treize rendus publies ne mesuraient rien. Un chiffre de correction qui derive en
    # silence laisserait la correction se defaire toute seule.
    vides = 0
    # ⚠ L'audit du depot entier est garde a part : ses deux comptes (piles vides, piles
    # lues) sont ce qui borne le rayon de souffle, et un rayon de souffle qui derive en
    # silence est pire qu'un rayon de souffle inconnu.
    f = _source(racine, "matiere_des_piles_toutes.json")
    if f.exists():
        d = json.loads(f.read_text())
        piles = d.get("piles", [])
        n_vides = sum(1 for r in piles if r.get("vide"))
        out.append(("piles vides sur tout le depot",
                    [f"{n_vides} piles", f"**{n_vides} piles", f"{n_vides} sur {len(piles)}"],
                    f.name))
        out.append(("piles lues par l'audit",
                    [f"{len(piles)} piles", f"**{len(piles)} piles**",
                     f"sur {len(piles)}"], f.name))
    for nom in ("matiere_des_piles.json", "matiere_des_piles_croise.json"):
        f = _source(racine, nom)
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        piles = d.get("piles", [])
        vides += sum(1 for r in piles if r.get("vide"))
        # ⚠ La part allumee la plus forte : c'est elle qui donne son sens au zero d'en face.
        parts = [r["part_allumee"] for r in piles if r.get("part_allumee")]
        if parts:
            v = max(parts) * 100
            out.append((f"part allumee la plus forte ({nom})",
                        [f"{fr(v, 1)} %", f"{fr(v, 1)}%", f"{en(v, 1)} %", f"{en(v, 1)}%"],
                        nom))
    if vides:
        out.append(("piles entierement noires",
                    [f"{vides} rendus", f"**{vides} rendus**",
                     f"{vides} piles", f"**{vides} piles**"], "matiere_des_piles*.json"))

    # ⚠⚠⚠ LES COMPTES DE LA SUITE NE SONT PLUS GARDES ICI — retires le 2026-09-03, et la
    # raison vaut d'etre ecrite parce qu'elle contredit la regle par defaut de ce fichier.
    #
    # `temoins.json` porte « N batteries, M controles » et « K chiffres recalcules ». Ce
    # sont des proprietes de la SUITE, pas des resultats sur le monde : elles changent a
    # chaque batterie ajoutee. Les garder revenait a exiger qu'un humain recopie trois
    # nombres dans quatre documents chaque fois qu'il ecrit un controle -- et l'obligation
    # s'est declenchee le jour meme, sur cinq batteries ajoutees.
    #
    # ⚠ Le mode de panne est celui que le docstring de CARTES_ATTENDUES nomme deja :
    # « le compte de chiffres gardes est AUTO-REFERENT ». Un garde-fou qui se compte
    # lui-meme perime sa propre citation en grandissant, donc il finit par crier a chaque
    # execution -- et un signal permanent cesse d'etre lu, ce qui est pire que pas de
    # signal du tout.
    #
    # ⭐ Le remede n'est pas de mieux recopier : c'est que la prose PONTE vers le fichier
    # au lieu de le citer. Les quatre sites concernes disent desormais ou lire le compte,
    # et `temoins.sh` l'imprime a chaque execution. Les RESULTATS, eux, restent gardes :
    # ce sont eux qui ne doivent pas deriver en silence.

    # ⚠⚠ M1ter — l'ecart aux conditions de la cible, et ce que la resolution peut couter.
    # Chaque chiffre du document 58 est RECALCULE ici depuis les quatre rapports, jamais
    # recopie : ce sont des rapports entre barreaux, donc exactement le genre de nombre
    # qu'on croit se rappeler et qu'on ecrit a l'envers. Et le pivot du document est le
    # rapport 1,092 -- tant qu'il etait cru a 3,6, « la resolution » etait une cause plausible.
    plan = _source(racine, "m1ter_resolution_en_plan.json")
    if plan.exists():
        d = json.loads(plan.read_text())
        natif = d["barreaux"][0]["sigma"]
        gros = d["barreaux"][-1]
        c = d["comparaison_a_la_cible"]
        ajoute("sigma au barreau le plus grossier de Scroll 1", gros["sigma"], 4, plan.name)
        ajoute("ecart aux conditions de la cible", c["rapport_tuile"], 3, plan.name)
        out.append(("ce qu'une tuile couvre a 7,91 µm",
                    [f"{fr(c['tuile_um'], 1)} µm", f"{en(c['tuile_um'], 1)} µm"], plan.name))
        out.append(("... et ce qu'elle couvre sur la cible",
                    [f"{fr(c['cible_tuile_um'], 1)} µm", f"{en(c['cible_tuile_um'], 1)} µm"], plan.name))
        out.append(("profondeur de 26 couches a 7,91 µm",
                    [f"{fr(c['profondeur_um'], 1)} µm", f"{en(c['profondeur_um'], 1)} µm"], plan.name))
        out.append(("... et sur la cible",
                    [f"{fr(c['cible_profondeur_um'], 1)} µm",
                     f"{en(c['cible_profondeur_um'], 1)} µm"], plan.name))
        out.append(("part de sigma perdue au barreau le plus grossier",
                    [f"{fr((1 - gros['sigma'] / natif) * 100, 1)} %",
                     f"{en((1 - gros['sigma'] / natif) * 100, 1)} %"], plan.name))
        out.append(("cout d'un doublement en plan sur Scroll 1",
                    [f"{fr((1 - d['barreaux'][1]['sigma'] / natif) * 100, 1)} %",
                     f"{en((1 - d['barreaux'][1]['sigma'] / natif) * 100, 1)} %"], plan.name))

    pc1 = _source(racine, "m1ter_croise_pc1.json")
    pc2 = _source(racine, "m1ter_croise_pc2.json")
    if pc1.exists() and pc2.exists():
        a = json.loads(pc1.read_text())["barreaux"]
        b = json.loads(pc2.read_text())["barreaux"]
        base = a[0]["sigma"]
        r_plan, r_prof, r_croise = a[1]["sigma"] / base, b[0]["sigma"] / base, b[1]["sigma"] / base
        out.append(("perte du doublement en profondeur",
                    [f"{fr((1 - r_prof) * 100, 1)} %", f"{en((1 - r_prof) * 100, 1)} %"], pc2.name))
        out.append(("perte du doublement en plan, fenetre juste",
                    [f"{fr((1 - r_plan) * 100, 2)} %", f"{en((1 - r_plan) * 100, 2)} %"], pc1.name))
        out.append(("... le meme doublement sur une fenetre deja doublee",
                    [f"{fr((1 - b[1]['sigma'] / b[0]['sigma']) * 100, 1)} %",
                     f"{en((1 - b[1]['sigma'] / b[0]['sigma']) * 100, 1)} %"], pc2.name))
        ajoute("prediction d'independance des deux axes", r_plan * r_prof, 3, pc2.name)
        ajoute("le croise reellement mesure", r_croise, 3, pc2.name)
        out.append(("de combien le croise est pire que l'independance",
                    [f"{fr(r_plan * r_prof / r_croise, 3)} fois",
                     f"{en(r_plan * r_prof / r_croise, 3)} fois"], pc2.name))

        # ⭐ Le compte le plus GENEREUX qu'on puisse faire pour l'hypothese qu'on ecarte :
        # la perte la plus forte mesuree sur chaque axe, plus la penalite d'interaction. Il
        # croise deux objets, ce qui est dit dans `58` §7 -- et c'est ce qui le rend
        # indiscutable, puisqu'il favorise la these qu'il refute.
        pl = json.loads(plan.read_text())["barreaux"] if plan.exists() else None
        if pl:
            r_plan_s1 = pl[1]["sigma"] / pl[0]["sigma"]
            ajoute("le compte le plus genereux pour la resolution",
                   r_plan_s1 * r_prof / (r_plan * r_prof / r_croise), 3, pc2.name)
            out.append(("... en facteur, contre les 45 a expliquer",
                        [f"{fr(1.0 / (r_plan_s1 * r_prof / (r_plan * r_prof / r_croise)), 1)}",
                         f"**{fr(1.0 / (r_plan_s1 * r_prof / (r_plan * r_prof / r_croise)), 1)}**"],
                        pc2.name))

    neuf = _source(racine, "m1ter_encre_a_9um.json")
    if neuf.exists():
        d = json.loads(neuf.read_text())
        out.append(("facteur de sigma qu'il faut expliquer",
                    [f"{fr(d['rapport_sigma'], 1)}", f"{en(d['rapport_sigma'], 1)}",
                     f"**{fr(d['rapport_sigma'], 1)}**"], neuf.name))
        ajoute("ce que la resolution doit expliquer, en facteur de sigma",
               1.0 / d["rapport_sigma"], 3, neuf.name)

    # ⚠⚠ La campagne de scan — et surtout le chiffre qui la REFUTE. Le meme corpus rend
    # p = 0,0081 ou p = 0,50 selon qu'on range « jamais trace » avec « pas d'encre » ou a
    # part, donc les deux p sont gardes : publier le premier sans le second serait publier
    # exactement l'erreur que ce document raconte.
    camp = _source(racine, "campagnes_de_scan.json")
    if camp.exists():
        d = json.loads(camp.read_text())
        g = d["groupes"]
        for etat, libelle in (("aucun_segment", "rouleaux jamais traces"),
                              ("segments_sans_encre", "rouleaux traces sans encre"),
                              ("encre_publiee", "rouleaux dont l'encre est publiee")):
            e = g["par_etat"][etat]
            out.append((libelle, [f"| **{e['n']}** |", f"| {e['n']} |",
                                  f"{e['n']} rouleaux", f"**{e['n']}** rouleaux"], camp.name))
            out.append((f"... part avec un scan fin ({etat})",
                        [f"{e['part_scan_fin']*100:.0f} %", f"**{e['part_scan_fin']*100:.0f} %**",
                         f"({e['part_scan_fin']*100:.0f} %)"], camp.name))
        ajoute("p du partage a deux groupes", g["fisher"]["p"], 4, camp.name)
        ajoute("p du partage restreint aux rouleaux tentes", g["fisher_traces"]["p"], 4, camp.name)
        pr = g["rouleaux_du_prix"]
        out.append(("rouleaux du prix jamais traces",
                    [f"{len(pr['jamais_traces'])} des treize",
                     f"**{len(pr['jamais_traces'])}** des treize",
                     f"dix des treize"], camp.name))

    # ⚠⚠⚠ La correction d'echelle, et les DEUX chiffres qu'il faut garder ensemble : celui
    # qui a ete publie (0,0171) et celui que la meme pile rend une fois lue correctement.
    # Publier le second sans le premier effacerait la trace de l'erreur.
    corr = _source(racine, "m1ter_apres_correction_echelle.json")
    if corr.exists():
        d = json.loads(corr.read_text())
        ajoute("sigma de PHerc1447 apres correction d'echelle", d["cible"]["sigma"], 4, corr.name)
        av = (d.get("contexte") or {}).get("avant") or {}
        if av.get("sigma"):
            ajoute("sigma de PHerc1447 tel qu'il avait ete publie", av["sigma"], 4, corr.name)
        # ⚠ Le rapport est celui que `comparer_encre` ECRIT (temoin / cible), jamais un
        # rapport recalcule ici : deux definitions du meme rapport finiraient par s'inverser,
        # et c'est exactement ce qui vient d'arriver.
        out.append(("PHerc1447 contre le temoin, apres correction",
                    [f"{fr(d['rapport_sigma'], 1)}×", f"**{fr(d['rapport_sigma'], 1)}×**"],
                    corr.name))

    ent = _source(racine, "PHerc1447_surface_entiere.json")
    if ent.exists():
        d = json.loads(ent.read_text())
        ajoute("sigma sur la surface entiere de PHerc1447", d["cible"]["sigma"], 4, ent.name)
        out.append(("la surface entiere contre le temoin",
                    [f"{fr(d['rapport_sigma'], 1)}×", f"**{fr(d['rapport_sigma'], 1)}×**"],
                    ent.name))

    # ⚠ Le contre-controle du reglage : les 190 cartes PUBLIEES, mesurees a la reduction 4,
    # rendent bien de la periodicite. C'est ce qui distingue « le defaut est casse » de
    # « nos cartes vivent a une autre echelle », et la difference change la lecture de `60`.
    corpus = _source(racine, "typographie.json")
    if corpus.exists():
        d = json.loads(corpus.read_text())
        cartes = d.get("cartes", [])
        avec = sum(1 for x in cartes if x.get("fenetres_periodiques"))
        if cartes:
            out.append(("cartes publiees avec au moins une fenetre periodique",
                        [f"**{avec}** ont au moins une fenêtre périodique",
                         f"{avec} ont au moins une fenêtre périodique"], corpus.name))

    typo = _source(racine, "typographie_de_nos_cartes.json")
    if typo.exists():
        d = json.loads(typo.read_text())
        par = {(l["rouleau"], l["carte"]): l for l in d.get("cartes", [])}
        # ⚠⚠⚠ CES NOMS SONT ATTENDUS, pas cherchés au hasard, et l'absence de l'un est un
        # DÉFAUT. Le 2026-08-28 le garde-fou cherchait `ink_PHerc1447_complet`, que la
        # campagne avait renommé en quatre segments : il a cessé de garder ses chiffres sur
        # un `continue` silencieux, le compte est passé de 254 à 253, et **rien n'a
        # échoué**. Un garde-fou qui cesse de garder sans le dire est pire qu'un garde-fou
        # absent, parce qu'on continue de lui faire confiance.
        for carte, libelle in CARTES_ATTENDUES:
            l = par.get(("nos_cartes", carte))
            if not l or not l.get("fenetres"):
                # ⚠ L'ecriture cherchee est une phrase qu'aucun document ne contiendra,
                # donc le controle echoue toujours — et elle est LISIBLE, contrairement a
                # une sentinelle a octet nul, que `grep` ne rend pas : l'echec doit NOMMER
                # la carte manquante, sinon il envoie deviner.
                out.append((f"carte attendue absente de {typo.name}",
                            [f"CARTE ATTENDUE ABSENTE DU RESULTAT : {carte}"], typo.name))
                continue
            out.append((f"fenetres periodiques, {libelle}",
                        [f"{l['fenetres_periodiques']}/{l['fenetres']}"], typo.name))
            if l.get("periode_px"):
                out.append((f"periode typographique, {libelle}",
                            [f"{l['periode_px']} px"], typo.name))
        # ⚠ Le controle par melange est ce qui donne une echelle au compte : sans lui,
        # « 2 fenetres sur 2 » n'est pas distinguable d'un tirage.
        for carte, libelle in CARTES_ATTENDUES:
            l = par.get(("controle_melange", carte))
            if l:
                out.append((f"controle melange, {libelle}",
                            [f"{l['fenetres_periodiques']}/{l['fenetres']}"], typo.name))

    gen = _source(racine, "generalisation_PHerc0172.json")
    if gen.exists():
        d = json.loads(gen.read_text())
        ajoute("sigma de PHerc0172, echelle corrigee", d["cible"]["sigma"], 4, gen.name)
        out.append(("PHerc0172 contre le temoin",
                    [f"{fr(d['rapport_sigma'], 1)}×", f"**{fr(d['rapport_sigma'], 1)}×**"],
                    gen.name))

    p = _source(racine, "cout_echelle.json")
    if p.exists():
        d = json.loads(p.read_text())
        for ligne in (d if isinstance(d, list) else d.get("rouleaux", [])):
            if ligne.get("rouleaux") == 800:
                ajoute("heures pour 800 rouleaux, 16 fils",
                       ligne["heures_1_fil"] / 8.35, 1, p.name)

    # ⚠⚠ LES PREMIERES AUC CONTRE DE VRAIES ETIQUETTES de ce depot, et elles n'etaient
    # gardees par rien : `63` les cite, `64` les compare, et un rendu refait aurait pu les
    # deplacer sans qu'aucun controle ne bronche. Le domaine est dans le nom parce que les
    # trois domaines d'un meme fragment donnent trois nombres differents -- c'est meme le
    # sujet de `63` §2 ter.
    for frag in ("frag1", "frag2", "frag3"):
        vt = _source(racine, f"{frag}_verite_terrain.json")
        if not vt.exists():
            continue
        d = json.loads(vt.read_text())
        for dom in d.get("domaines", []):
            nom = dom.get("domaine", "")
            if nom.startswith("CONTROLE"):
                continue
            ajoute(f"AUC {frag}, {nom}", dom["auc"], 3, vt.name)

    # ⚠⚠ LE SECOND TEMOIN NEGATIF, produit le 2026-08-28. Son alpha est ce qui en fait un
    # temoin plutot qu'une surface quelconque : si un rendu futur le deplacait sous le seuil,
    # tout ce qui s'appuie dessus tomberait, et rien ne le dirait.
    t2 = _source(racine, "temoin_2.json")
    if t2.exists():
        d = json.loads(t2.read_text())
        serie = (d.get("series") or [{}])[0]
        if serie.get("alpha") is not None:
            ajoute("alpha du second temoin", serie["alpha"], 2, t2.name, signe=True)
            ajoute("marge du second temoin au seuil", serie["marge_au_seuil"], 2, t2.name)
        for couches, ecart in serie.get("serie", []):
            ajoute(f"ecart du second temoin a {couches} couches", ecart, 1, t2.name,
                   unites=("µm",))

    # ⚠⚠ Les correlations du transport (residu M7). Le p BRUT et le p de HOLM sont gardes
    # tous les deux, exprès : publier le brut seul est precisement la faute que la correction
    # existe pour empecher, et un lecteur doit pouvoir verifier les deux.
    tdc = _source(racine, "transport_de_calibration.json")
    if tdc.exists():
        d = json.loads(tdc.read_text())
        for nom, c in d.get("correlations", {}).items():
            if not c.get("exploitable"):
                continue
            ajoute(f"rho du transport, {nom}", c["rho"], 3, tdc.name, signe=True)
        for nom, pr in d.get("permutation", {}).items():
            if pr.get("exploitable"):
                ajoute(f"p de permutation, {nom}", pr["p"], 4, tdc.name)
        for nom, h in d.get("holm", {}).items():
            ajoute(f"p de Holm, {nom}", h, 3, tdc.name)

    # ⚠⚠ La lisibilite par echelle. L'INTERVALLE est garde autant que la moyenne : c'est lui
    # qui distingue « 0,686 » de « lisible », et publier la moyenne seule est exactement la
    # faute que `65` corrige.
    lnm = _source(racine, "lisible_a_neuf_microns.json")
    if lnm.exists():
        d = json.loads(lnm.read_text())
        for e in d.get("echelles", []):
            um = f"{e['voxel_um']:.2f}".replace(".", ",")
            ajoute(f"AUC groupee a {um} um", e["auc_groupee"], 3, lnm.name)
            ic = e.get("intervalle", {})
            if ic.get("exploitable"):
                ajoute(f"moyenne des tuiles a {um} um", ic["moyenne"], 3, lnm.name)
                ajoute(f"borne basse de l'IC a {um} um", ic["ic_bas"], 3, lnm.name)
                ajoute(f"borne haute de l'IC a {um} um", ic["ic_haut"], 3, lnm.name)
            for b in e.get("balayage_de_maille", []):
                if b.get("largeur") is not None:
                    ajoute(f"largeur de l'IC a {um} um, maille {b['cotes']}x{b['cotes']}",
                           b["largeur"], 3, lnm.name)

    # ⚠⚠ Le compte qui porte la conclusion structurelle de `59` : ZERO rouleau mesurable. Un
    # jour ou quelqu'un publierait des etiquettes sur un rouleau, ce chiffre bougerait et le
    # garde-fou signalerait le document devenu perime -- ce qui est exactement le service
    # attendu.
    ove = _source(racine, "ou_la_verite_existe.json")
    if ove.exists():
        d = json.loads(ove.read_text())
        c = d.get("compte", {})
        out.append(("rouleaux mesurables",
                    [f"**{c.get('rouleaux_mesurables', 0)}** rouleau",
                     f"{c.get('rouleaux_mesurables', 0)} rouleau"], ove.name))
        out.append(("fragments mesurables",
                    [f"**{c.get('fragments_mesurables', 0)} fragments**",
                     f"{c.get('fragments_mesurables', 0)} fragments"], ove.name))

    # ⚠⚠ LE CONTROLE DUR, et sa FRAGILITE gardee avec lui. Publier le p sans les deux p de
    # bascule le ferait lire comme un resultat solide, alors qu'une seule fenetre le renverse.
    tcc = _source(racine, "temoin_contre_nos_cartes.json")
    if tcc.exists():
        d = json.loads(tcc.read_text())
        if d.get("p") is not None:
            ajoute("p du controle dur", d["p"], 4, tcc.name)
        for nom, val in (d.get("fragilite") or {}).items():
            ajoute(f"p si {nom.replace('_', ' ')}", val, 4, tcc.name)
        out.append(("fenetres periodiques du rouleau",
                    [f"**{d['rouleau']['periodiques']} / {d['rouleau']['fenetres']}**",
                     f"{d['rouleau']['periodiques']}/{d['rouleau']['fenetres']}"], tcc.name))
        out.append(("fenetres periodiques du temoin",
                    [f"**{d['temoin_negatif']['periodiques']} / {d['temoin_negatif']['fenetres']}**",
                     f"{d['temoin_negatif']['periodiques']}/{d['temoin_negatif']['fenetres']}"],
                   tcc.name))

    # ⭐⭐⭐ Le referent d'IDENTITE, releve par `73` §4 et recompte par `74` §3. Garde parce que
    # le compte publie par `73` -- 57 segments, deux rouleaux -- est faux d'un facteur ~1,8, et
    # qu'un compte faux qui circule dans un plan choisit le mauvais rouleau (cf. `74` §4).
    lis = _source(racine, "les_indices_de_spire.json")
    if lis.exists():
        d = json.loads(lis.read_text())
        out.append(("segments portant un indice de spire",
                    [f"**{d['total_segments_indexes']} segments indexes**",
                     f"{d['total_segments_indexes']} segments indexés sur "
                     f"{len(d['rouleaux_indexes'])} rouleaux",
                     f"{d['total_segments_indexes']} segments, pas "
                     f"{d['annonce_73']['segments']}"], lis.name))
        # ⚠ Ce compte-la est celui qui rend H1' testable : « consecutif entre deux spires
        # consecutives » n'est une question que la ou deux spires consecutives sont publiees.
        out.append(("spires consecutives sans trou",
                    [f"**{d['total_spires_sans_trou']} spires consécutives**",
                     f"{d['total_spires_sans_trou']} spires consécutives"], lis.name))
        inv = d["inventaire"]
        for rouleau in ("PHerc0139", "PHerc0172"):
            v = inv.get(rouleau, {})
            if v.get("indexes_uniques"):
                out.append((f"course indexee de {rouleau}",
                            [f"`w{v['premiere']:03d}`–`w{v['derniere']:03d}`",
                             f"w{v['premiere']:03d}`–`w{v['derniere']:03d}"], lis.name))
    # ⭐⭐⭐ Le SENS des indices de spire (`76`), et l'ecart inter-feuilles qu'il rend au
    # passage. Garde parce que c'est le premier ecart inter-feuilles du depot qui ne depende
    # d'AUCUN parametre de traceur -- l'article a deja publie 113 um, qui bouge avec
    # `neighbor_step`, et une prose qui derive de sa mesure recommencerait la meme erreur.
    sdi = _source(racine, "le_sens_des_indices.json")
    if sdi.exists():
        d = json.loads(sdi.read_text())
        ajoute("voxel decode de l'aire", d["voxel_um"], 4, sdi.name)
        # ⚠ Les deux ecritures decimales : la prose du depot est en francais (virgule), le
        # JSON et l'article en anglais (point). Un garde-fou qui n'accepte qu'une des deux
        # signale « ABSENT » sur un chiffre parfaitement cite.
        def _deux(v: float, n: int, suffixe: str = "") -> list[str]:
            point = f"{v:.{n}f}{suffixe}"
            return [f"**{point}**", point, f"**{point.replace('.', ',')}**",
                    point.replace(".", ",")]

        out.append(("sens des indices de spire",
                    _deux(d["part_vers_l_exterieur"] * 100, 1, " %"), sdi.name))
        out.append(("ecart inter-feuilles sans traceur",
                    _deux(d["ecart_median_um"], 1, " µm"), sdi.name))
        out.append(("cellules comparees",
                    [f"**{d['cellules_comparees']:,}**".replace(",", "\u202f"),
                     f"{d['cellules_comparees']}",
                     f"{d['cellules_comparees']:,}".replace(",", " ")], sdi.name))
        # ⚠ Les DEFAUTS du referent sont gardes comme les autres chiffres : ils sont ce qui
        # empeche un test d'identite de compter un defaut de referent comme un echec de
        # predicteur, donc les perdre couterait plus cher que de perdre une mediane.
        for x in d["defauts_du_referent"]:
            out.append((f"defaut du referent w{x['de']:03d}/w{x['vers']:03d}",
                        [f"w{x['de']:03d} → w{x['vers']:03d}",
                         f"w{x['de']:03d}/w{x['vers']:03d}"], sdi.name))
        a = d["aire_par_spire_cm2"]
        # ⚠ `unites` est OBLIGATOIRE ici : ces trois chiffres font moins de cinq caracteres,
        # donc `discriminante` les ecarterait -- « 6,4 » nu se trouve dans n'importe quel
        # document. Ecrits avec leur unite, ils redeviennent cherchables.
        ajoute("aire mediane d'une spire publiee", a["median"], 1, sdi.name,
               unites=(" cm²",))
        ajoute("aire de la plus petite spire publiee", a["min"], 1, sdi.name,
               unites=(" cm²",))
        # ⚠ Ecrit AVEC son contexte, pas nu : « ×6,4 » fait quatre caracteres et serait
        # ecarte par `discriminante`, exactement le cas que sa docstring decrit.
        out.append(("facteur sur le point fixe de l'extension",
                    [f"**×{d['facteur_sur_le_point_fixe']:.1f}**".replace(".", ","),
                     f"×{d['facteur_sur_le_point_fixe']:.1f} le point fixe".replace(".", ","),
                     f"soit ×{d['facteur_sur_le_point_fixe']:.1f}".replace(".", ",")],
                   sdi.name))
        for pas in d["par_pas"]:
            out.append((f"ecart pour un saut de {pas['saut']}",
                        _deux(pas["median_vx"] * d["voxel_um"], 1, " µm"), sdi.name))
    # ⭐⭐⭐ Le PREDICAT D'IDENTITE (`77`) : la moitie que le pinceau peint. Garde parce que la
    # non-recouvrance des deux populations est ce qui en fait un predicat plutot qu'une
    # tendance -- et qu'une prose qui deriverait de la mesure transformerait un predicat en
    # opinion sans que rien ne l'attrape.
    cde = _source(racine, "le_champ_denroulement.json")
    if cde.exists():
        d = json.loads(cde.read_text())

        def _deux2(v: float, n: int, suffixe: str = "", signe: bool = False) -> list[str]:
            s_ = "+" if (signe and v >= 0) else ""
            point = f"{s_}{v:.{n}f}{suffixe}"
            return [f"**{point}**", point, f"**{point.replace('.', ',')}**",
                    point.replace(".", ",")]

        out.append(("avance par tour d'une vraie spire",
                    _deux2(d["avance_par_tour_mediane"], 3, "", signe=True), cde.name))
        out.append(("borne haute d'une vraie spire",
                    _deux2(d["avance_p90"], 3, "", signe=True), cde.name))
        for saut, t in sorted(d["temoins_en_travers"].items()):
            out.append((f"avance d'un saut fabrique de {saut}",
                        _deux2(t["median"], 3), cde.name))
            if saut == "1":
                out.append(("borne basse d'un saut d'une feuille",
                            _deux2(t["p10"], 3), cde.name))
        ajoute("erreur d'indice a spire exclue", d["erreur_mediane"], 4, cde.name)
        # ⚠⚠ L'ECHELLE du predicat : `42` disait « des regions, pas des points » ; ce chiffre
        # en donne la taille. Garde parce qu'une prose qui l'oublierait redonnerait au
        # predicat une resolution qu'il n'a pas.
        sep = d.get("separation", {})
        if sep.get("tranches_necessaires"):
            out.append(("tranches a agreger pour separer",
                        [f"**{sep['tranches_necessaires']}** tranches",
                         f"{sep['tranches_necessaires']} tranches de hauteur"], cde.name))
        # ⚠ La derive de l'axe : la piste la plus seduisante, et sa refutation. Gardee pour
        # que la prose ne puisse pas la presenter comme la cause -- ce qu'elle n'est pas.
        der = d.get("derive_de_l_axe", {})
        if der.get("median_feuilles"):
            ajoute("derive de l'axe par tranche, en feuilles",
                   der["median_feuilles"], 2, cde.name, unites=(" feuilles",))
            out.append(("derive maximale de l'axe",
                        [f"**{der['max_feuilles']:.1f}**",
                         f"{der['max_feuilles']:.1f} feuilles",
                         f"{der['max_feuilles']:.1f}".replace(".", ",")], cde.name))
        for pal in sep.get("paliers", []):
            if pal["tranches"] in (1, 2, 16):
                out.append((f"palier {pal['tranches']} tranche(s) : vraie p90",
                            _deux2(pal["vraie_p90"], 3, "", signe=True), cde.name))
                out.append((f"palier {pal['tranches']} tranche(s) : saut p10",
                            _deux2(pal["saut_p10"], 3, "", signe=True), cde.name))
    # ⭐⭐⭐ Le MASQUE D'APPROBATION (`77` §6). Garde parce que le bras qui mord est le
    # demi-pas : c'est LUI qui separe un masque utile d'un masque qui approuve tout, et une
    # prose qui deriverait de sa mesure ne serait plus verifiable par personne.
    mda = _source(racine, "le_masque_dapprobation.json")
    if mda.exists():
        d = json.loads(mda.read_text())

        def _pc(v: float) -> list[str]:
            point = f"{v * 100:.1f} %"
            return [f"**{point}**", point, f"**{point.replace('.', ',')}**",
                    point.replace(".", ",")]

        for nom, clef in (("spire lue par son propre champ", "spire, champ complet"),
                          ("quart de pas approuve", "quart de pas"),
                          ("spire a spire exclue", "spire, à spire exclue"),
                          ("demi-pas approuve", "demi-pas"),
                          ("saut d'une feuille approuve", "saut d'une feuille")):
            if clef in d["bras"]:
                out.append((nom, _pc(d["bras"][clef]["part_mediane"]), mda.name))
    # ⭐⭐⭐ L'OMBILIC PUBLIE (`78`) : la correction de « un seul rouleau », et surtout la
    # validation croisee de tout `76`/`77` contre un axe independant. Garde parce que le
    # couple (biais reel, verdict inchange) ne vaut QUE si les deux chiffres restent lies :
    # publier le second sans le premier serait publier une immunite sans sa mise a l'epreuve.
    omb = _source(racine, "lombilic_publie.json")
    if omb.exists():
        d = json.loads(omb.read_text())
        out.append(("rouleaux publiant un ombilic",
                    [f"**{len(d['axes_publies'])}** rouleaux",
                     f"{len(d['axes_publies'])} rouleaux en publient un",
                     f"et **{len(d['axes_publies'])}** rouleaux"], omb.name))
        c = d.get("comparaison")
        if c:
            ajoute("biais median entre les deux axes, en mm",
                   c["biais_median_um"] / 1000.0, 2, omb.name, unites=(" mm",))
            out.append(("biais maximal en feuilles",
                        [f"**{c['biais_max_en_feuilles']:.0f}** écarts",
                         f"{c['biais_max_en_feuilles']:.0f} écarts inter-feuilles",
                         f"{c['biais_max_en_feuilles']:.0f} feuilles"], omb.name))
            for nom, x in (("axe ajuste", c["axe_ajuste"]), ("axe publie", c["axe_publie"])):
                pc = f"{x['part_vers_l_exterieur'] * 100:.1f} %"
                out.append((f"{nom} : sens", [f"**{pc}**", pc, pc.replace(".", ",")],
                            omb.name))
                um = f"{x['ecart_um']:.1f} µm"
                out.append((f"{nom} : ecart", [f"**{um}**", um, um.replace(".", ",")],
                            omb.name))
    # ⭐⭐⭐ Le resultat NEGATIF de `78` §2 : l'axe et le pas ne suffisent pas. Garde parce que
    # ce fichier chiffre ce qu'un champ derive du volume devra RETROUVER -- un plan futur qui
    # citerait un mauvais facteur se dimensionnerait sur un mauvais objectif.
    ans = _source(racine, "laxe_ne_suffit_pas.json")
    if ans.exists():
        d = json.loads(ans.read_text())
        ajoute("dispersion radiale d'une seule spire, en feuilles",
               d["dispersion_intra_spire_feuilles"], 1, ans.name, unites=(" feuilles",))
        ajoute("erreur du modele d'Archimede, en feuilles",
               d["archimede"]["erreur_mediane"], 2, ans.name, unites=(" feuilles",))
        if d.get("facteur_de_la_forme"):
            out.append(("ce que la forme des spires vaut",
                        [f"**×{d['facteur_de_la_forme']:.0f}**",
                         f"facteur **{d['facteur_de_la_forme']:.0f}**",
                         f"vaut : ×{d['facteur_de_la_forme']:.0f}"], ans.name))
    # ⚠⚠ Le balayage des tranches (`77` §7) : la refutation de la piste « derive de l'axe ».
    # Garde parce que ces trois chiffres ont d'abord ete publies depuis un TERMINAL, et que
    # `chiffres_sans_record` les a attrapes -- exactement ce pour quoi il existe.
    bal = _source(racine, "balayage_tranches_PHerc0172.json")
    if bal.exists():
        d = json.loads(bal.read_text())
        for pal in d["paliers"]:
            out.append((f"balayage TRANCHES_Z={pal['tranches_z']} : vraie p90",
                        [f"**{pal['vraie_p90']:+.3f}**", f"{pal['vraie_p90']:+.3f}",
                         f"{pal['vraie_p90']:+.3f}".replace(".", ",")], bal.name))
    # ⭐⭐⭐ LE TROU ANGULAIRE (`77` §8) : la cause trouvee en regardant. Gardee parce que le couple
    # (concentration, temoin a compte egal) est ce qui distingue « ecarter la couture » de
    # « ecarter six secteurs », et que j'ai deja publie la mauvaise version.
    for nom, fic in (("0172", "le_trou_angulaire.json"),
                     ("0139", "le_trou_angulaire_PHerc0139.json")):
        cou = _source(racine, fic)
        if not cou.exists():
            continue
        d = json.loads(cou.read_text())
        out.append((f"concentration de la violation, {nom}",
                    [f"**×{d['concentration']:.2f}**", f"×{d['concentration']:.2f}",
                     f"×{d['concentration']:.2f}".replace(".", ",")], cou.name))
        out.append((f"part portee par les pires secteurs, {nom}",
                    [f"**{d['part_des_pires'] * 100:.1f} %**",
                     f"{d['part_des_pires'] * 100:.1f} %",
                     f"{d['part_des_pires'] * 100:.1f} %".replace(".", ",")], cou.name))
        # ⚠⚠ Les DEUX chiffres qui ont refute mon explication par une « couture ». Gardes parce
        # qu'une prose qui les perdrait pourrait reraconter l'histoire refutee sans que rien ne
        # l'attrape -- et elle est plausible, c'est bien le probleme.
        dn = d.get("densite") or {}
        if dn:
            out.append((f"densite dans le trou, {nom}",
                        [f"**{dn['median_dedans']:.0f} points/cellule contre "
                         f"{dn['median_dehors']:.0f}**",
                         f"{dn['median_dedans']:.0f} points par cellule contre "
                         f"{dn['median_dehors']:.0f}"], cou.name))
        sp = d.get("par_spire") or {}
        if sp:
            out.append((f"spires intactes dans le trou, {nom}",
                        [f"**{sp['spires_intactes']} spires sur "
                         f"{sp['spires_mesurees']}**",
                         f"{sp['spires_intactes']} spires sur {sp['spires_mesurees']}"],
                       cou.name))
            out.append((f"correlation du trou avec l'indice, {nom}",
                        [f"**{sp['correlation_avec_lindice']:.3f}**",
                         f"{sp['correlation_avec_lindice']:.3f}".replace(".", ",")],
                       cou.name))
    # ⭐⭐ La PORTEE du champ (`77` §9) et la structure angulaire de l'ecart. Gardees ensemble
    # parce que « l'ecart varie de 74 um avec l'angle » invite a croire qu'on peut l'exploiter,
    # et la mesure dit non : publier la premiere sans la seconde serait une invitation fausse.
    ext = _source(racine, "extraire_la_spire_suivante.json")
    if ext.exists():
        d = json.loads(ext.read_text())
        vox = 9.362
        for x in d["series"]["sans_reinjection"][:3]:
            um = f"{x['erreur_vx'] * vox:.0f} µm"
            out.append((f"portee du champ, {x['au_dela']} feuille(s)",
                        [f"**{um}**", um, f"{x['erreur_feuilles']:.2f} feuille".replace(".", ",")],
                        ext.name))
        st = d.get("structure") or {}
        if st:
            out.append(("amplitude angulaire de l'ecart",
                        [f"**{st['amplitude_angle_um']:.0f} µm**",
                         f"{st['amplitude_angle_um']:.0f} µm d'amplitude"], ext.name))
        out.append(("modele retenu pour l'extrapolation",
                    [f"`{d['modele']}`", f"pas {d['modele']}"], ext.name))
    # ⭐⭐⭐ L'ecart de la spire PUBLIEE a la feuille (`77` §10). Garde parce que c'est un
    # PLANCHER sur toute erreur mesuree contre ces spires -- y compris les 47 um du champ.
    # Publier l'un sans l'autre ferait passer l'erreur du referent pour la mienne.
    # ⭐⭐⭐ LE PAS QUE LA MATIERE MONTRE (`99`), ET LES TROIS BARRES DOIVENT VOYAGER ENSEMBLE.
    # Le verdict n'a de sens que si l'on voit l'ecart entre la barre d'un seul essai, celle du
    # balayage, et celle du balayage CALIBRE : c'est cet ecart qui mesure l'ampleur des deux
    # corrections. Et la comparaison au nul est gardee entiere, parce que sans elle la longueur
    # rendue serait indiscernable du biais de la recherche.
    pmm = _source(racine, "le_pas_que_la_matiere_montre.json")
    if pmm.exists():
        d = json.loads(pmm.read_text())
        for cle, nom in (("barre_du_nul", "barre du nul calibre"),
                         ("barre_dun_seul_essai", "barre d'un seul essai")):
            val = d[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], pmm.name))
        cn = d["la_longueur_differe_du_nul"]
        for cle, nom in (("mediane_reelle_um", "pas montre, mediane reelle"),
                         ("mediane_du_nul_um", "pas montre, mediane du nul"),
                         ("kolmogorov_smirnov_D", "Kolmogorov-Smirnov D du pas montre")):
            val = cn[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], pmm.name))
        npc = d["nul_par_candidat"]
        for cle, nom in (("le_plus_court", "nul du candidat le plus court"),
                         ("le_plus_long", "nul du candidat le plus long"),
                         ("rapport", "rapport du biais par candidat")):
            val = npc[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], pmm.name))
        for tiers in ("coeur", "milieu", "bord"):
            t = d["par_tiers"].get(tiers)
            if not t:
                continue
            for cle, nom in (("pas_median_um", "pas montre au"),
                             ("part_utilisable", "part utilisable au"),
                             ("part_a_plus_dun_dixieme_du_nominal",
                              "part a plus d'un dixieme du nominal au")):
                val = t[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {tiers}", [f"**{txt}**", txt, f"{val}"], pmm.name))
        val = d["correlations"]["part_utilisable_contre_continuite"]
        txt = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
        out.append(("part utilisable contre la continuite",
                    [f"**{txt}**", txt, f"{val:.3f}"], pmm.name))

    # ⛔⛔ LE CUBE LU MOINS CHER (`103`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le taux par pas ne voyage jamais sans sa CONSEQUENCE ENCHAINEE : « 7,3 % des cellules »
    # paraissent inoffensifs, « 36,5 % des marches de six pas » est le fait qui refute l'economie.
    # (2) Et le gain MESURE ne voyage jamais sans le gain PREDIT : le premier seul se lit comme une
    # mesure de cout, alors que c'est leur ECART qui porte la lecon — le cout se mesure, il ne se
    # modelise pas.
    cub = _source(racine, "le_cube_lu_moins_cher.json")
    if cub.exists():
        d = json.loads(cub.read_text())
        for cle, nom in (("cote_um_du_cube", "cote du cube lu"),
                         ("demi_cube_voxels", "demi-largeur du cube en voxels")):
            if cle not in d:
                continue
            val = d[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], cub.name))
        for x in d.get("sur_le_vrai_volume", {}).get("lignes", []):
            pe = x["pas_echantillon"]
            for cle, nom in (("secondes_par_cube", "secondes par cube au pas"),
                             ("gain_de_temps", "gain de temps mesure au pas"),
                             ("ecart_median_au_plus_fin_deg", "ecart median au pas"),
                             ("ecart_p90_deg", "ecart p90 au pas"),
                             ("part_au_dela_de_dix_degres", "part au-dela de dix degres au pas")):
                val = x[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                if isinstance(val, float) and cle == "part_au_dela_de_dix_degres":
                    # ⚠ Une part se redige souvent en pourcentage : les deux formes sont acceptees,
                    # sinon le garde accuserait un texte correct.
                    pc = f"{100 * val:.1f}".replace(".", ",")
                    formes = [f"**{pc} %**", f"{pc} %", f"{pc}%"] + formes
                out.append((f"{nom} {pe}", formes, cub.name))
        for x in d.get("sur_empilement_fabrique", {}).get("lignes", []):
            pe = x["pas_echantillon"]
            for cle, nom in (("marge_sous_la_barre_deg", "marge sous la barre au pas"),
                             ("barre_de_sa_forme_deg", "barre de la forme au pas")):
                val = x.get(cle)
                if val is None:
                    continue
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                if cle.startswith("marge"):
                    signe = f"{val:+.2f}".replace(".", ",").replace("-", "\u2212")
                    formes = [f"**{signe}**", signe] + formes
                out.append((f"{nom} {pe}", formes, cub.name))
        pr = d.get("le_pas_retenu", {})
        for x in pr.get("verdicts", []):
            val = x.get("part_de_marches_de_six_pas_touchees")
            if val is None:
                continue
            pc = f"{100 * val:.1f}".replace(".", ",")
            out.append((f"marches de six pas abimees au pas {x['pas_echantillon']}",
                        [f"**{pc} %**", f"{pc} %", f"{pc}%",
                         f"{val}".replace(".", ","), f"{val}"], cub.name))
        if "tolere_deg" in pr:
            val = pr["tolere_deg"]
            out.append(("tolerance angulaire du controle apparie",
                        [f"**{val:.0f}**", f"{val:.0f}", f"{val}"], cub.name))
        v = d.get("sur_le_vrai_volume", {})
        if "cellules" in v:
            out.append(("cellules appariees lues a tous les pas",
                        [f"**{v['cellules']}**", f"{v['cellules']}"], cub.name))

    # ⛔⛔⛔ LE MARCHEUR AVEC LE BON PAS (`107`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le mode HAUT ne voyage jamais sans le mode BAS : « dix trajets comptent juste » est un
    # nombre nu, « dix contre quatorze qui ne mesurent rien » EST le resultat, et leur mediane
    # commune serait un choix de mode qui s'ignore.
    # (2) Et le risque tardif ne voyage jamais sans sa consequence enchainee : 0,105 par pas se lit
    # comme un petit nombre alors que (1-0,105)^120 vaut deux millionniemes.
    mar = _source(racine, "le_marcheur_avec_le_bon_pas.json")
    if mar.exists():
        d = json.loads(mar.read_text())
        s107 = d.get("resume", {})
        for cle, nom in (("cellules", "cellules du marcheur"),
                         ("bandes", "bandes du marcheur"),
                         ("plafond_de_pas", "plafond de pas du marcheur"),
                         ("pas_confirmes_calibre", "pas confirmes par le selecteur de 102"),
                         ("pas_confirmes_corrige", "pas confirmes par le selecteur corrige"),
                         ("gain_en_pas", "gain en pas du selecteur corrige"),
                         ("trajets_lisibles", "trajets lisibles"),
                         ("part_des_trajets_au_compte_attendu",
                          "part des trajets au compte attendu"),
                         ("feuilles_par_pas_du_mode_haut", "feuilles par pas du mode haut"),
                         ("feuilles_par_pas_du_mode_bas", "feuilles par pas du mode bas"),
                         ("ecart_des_scores_entre_modes", "ecart des scores entre modes"),
                         ("feuilles_par_pas_du_trajet_corrige",
                          "feuilles par pas du trajet corrige"),
                         ("feuilles_par_pas_du_trajet_calibre",
                          "feuilles par pas du trajet calibre"),
                         ("spires_du_trajet_corrige", "spires du trajet corrige"),
                         ("spires_du_trajet_calibre", "spires du trajet calibre"),
                         ("feuilles_par_pas_corrige", "fraction par pas du corrige"),
                         ("feuilles_par_pas_calibre", "fraction par pas du calibre"),
                         ("virage_median_deg", "virage median entre pas"),
                         ("virage_p90_deg", "virage p90 entre pas"),
                         ("heures_si_un_cube_sur_deux", "heures si un cube sur deux"),
                         ("risque_precoce", "risque precoce du marcheur"),
                         ("risque_tardif", "risque tardif du marcheur"),
                         ("survie_a_120_spires_au_risque_tardif",
                          "survie a cent vingt spires au risque tardif")):
            if cle not in s107 or s107[cle] is None:
                continue
            val = s107[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if cle.startswith("part_"):
                pc = f"{100 * val:.1f}".replace(".", ",")
                formes = [f"**{pc} %**", f"{pc} %", f"{pc}%"] + formes
            if cle.startswith("ecart_des_scores"):
                formes += [f"**+{txt}**", f"+{txt}"]
            if isinstance(val, float):
                for n_dec in (1, 2, 3):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
            if cle.startswith("survie"):
                formes += ["**0,000002**", "0,000002", "2e-06"]
            out.append((nom, formes, mar.name))
        for sel in ("calibre", "deux_roles"):
            b = d.get(sel, {})
            for cle, nom in (("cellules_au_plafond", "cellules au plafond du selecteur"),
                             ("part_censuree", "part censuree du selecteur"),
                             ("pas_lu_median_um", "pas lu median du selecteur"),
                             ("cellules_qui_ont_porte", "cellules qui ont porte du selecteur")):
                if cle not in b or b[cle] is None:
                    continue
                val = b[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                if cle == "part_censuree":
                    pc = f"{100 * val:.1f}".replace(".", ",")
                    formes = [f"**{pc} %**", f"{pc} %", f"{pc}%"] + formes
                out.append((f"{nom} {sel}", formes, mar.name))
            md = b.get("modes_du_trajet", {})
            for nom_m in ("mode_haut", "mode_bas"):
                if nom_m not in md:
                    continue
                for cle, nom in (("trajets", "trajets du"), ("feuilles_median", "feuilles du"),
                                 ("score_median", "score du")):
                    val = md[nom_m][cle]
                    txt = f"{val}".replace(".", ",")
                    out.append((f"{nom} {nom_m} {sel}", [f"**{txt}**", txt, f"{val}"], mar.name))
            if "seuil_feuilles" in md:
                val = md["seuil_feuilles"]
                txt = f"{val}".replace(".", ",")
                out.append((f"seuil des modes {sel}",
                            [f"**{txt}**", txt, f"{val}", f"**{val:.0f}**", f"{val:.0f}"],
                            mar.name))
        v_ = d.get("deux_roles", {}).get("le_risque_baisse", {})
        for cle, nom in (("rapport", "rapport des risques"),
                         ("p_sous_risque_constant", "p sous un risque constant"),
                         ("en_risque_precoce", "pas en risque precoce"),
                         ("en_risque_tardif", "pas en risque tardif")):
            if cle not in v_:
                continue
            val = v_[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], mar.name))
        for x in d.get("cout_par_etape", {}).get("mesures", []):
            val = x["secondes"]
            txt = f"{val}".replace(".", ",")
            out.append((f"cout par etape mesure {txt}",
                        [f"**{txt}**", txt, f"{val}"], mar.name))
        if "secondes" in d:
            h = round(d["secondes"] / 3600.0, 2)
            out.append(("heures de la course du marcheur",
                        [f"**{h}**".replace(".", ","), f"{h}".replace(".", ","), f"{h}"],
                        mar.name))
        p_ = d.get("prix_projete", {})
        for cle, nom in (("etapes", "etapes de la course du marcheur"),
                         ("heures", "heures projetees de la course")):
            if cle not in p_:
                continue
            val = p_[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], mar.name))

    # ⭐⭐⭐ POURQUOI LE REMEDE NE DESCEND PAS AU PAS (`112`), TROIS APPARIEMENTS OBLIGATOIRES.
    # (1) « f_lo » ne voyage jamais sans la LISTE DES MODES qu'il implique : un nombre seul ne dit
    # pas qu'a un pas la liste est vide, qui est tout le resultat. (2) Ce qu'une base absorbe ne
    # voyage jamais sans ce que les DEUX autres absorbent — c'est leur ECART qui designe la bonne.
    # (3) Et le gain sur les fenetres longues ne voyage jamais sans la part au-dessus de la barre
    # au PAS SEUL : sans elle, six points de mieux se lisent comme une amelioration nette alors
    # qu'une fenetre longue confirme moins souvent.
    rem = _source(racine, "pourquoi_le_remede_ne_descend_pas_au_pas.json")
    if rem.exists():
        d = json.loads(rem.read_text())
        for cle, nom in (("lambda_max_um", "lambda max de 112"),
                         ("avance_mediane_um", "avance mediane de 112")):
            if cle in d and d[cle] is not None:
                val = d[cle]
                out.append((nom, [f"**{val}**", f"{val}",
                                  f"**{val}**".replace(".", ","),
                                  f"{val}".replace(".", ",")], rem.name))
        a = d.get("a_partir_de_quelle_fenetre", {})
        for cle, nom in (("premiere_fenetre_nettoyable", "premiere fenetre nettoyable"),
                         ("seuil_en_micrometres", "seuil en micrometres"),
                         ("seuil_en_pas", "seuil en pas")):
            if cle not in a or a[cle] is None:
                continue
            val = a[cle]
            out.append((nom, [f"**{val}**", f"{val}"], rem.name))
        for x in a.get("par_fenetre", []):
            out.append((f"f lo a {x['pas']} pas", [f"**{x['f_lo']}**", f"{x['f_lo']}"], rem.name))
            out.append((f"longueur a {x['pas']} pas",
                        [f"**{x['longueur_um']:.0f}**", f"{x['longueur_um']:.0f}"], rem.name))
        c = d.get("la_contamination_est_irreductible", {})
        for cle, nom in (("accord_sans_derive", "accord sans derive"),
                         ("contamination_max", "contamination maximale")):
            if cle not in c or c[cle] is None:
                continue
            val = c[cle]
            out.append((nom, [f"**{val}**", f"{val}"], rem.name))
        for x in c.get("par_derive", []):
            for cle, nom in (("longueur_donde_um", "longueur donde de la derive"),
                             ("accord_brut", "accord brut a un pas"),
                             ("accord_apres_retrait", "accord apres retrait a un pas"),
                             ("gain", "gain du retrait a un pas")):
                val = x[cle]
                out.append((f"{nom} f={x['derive_en_periodes_par_fenetre']}",
                            [f"**{val}**", f"{val}"], rem.name))
        b = d.get("pourquoi_les_autres_bases_echouent", {})
        for x in b.get("polynomial", []):
            for deg in (1, 2, 3):
                val = x[f"degre_{deg}"]
                out.append((f"polynome degre {deg} a {x['pas']} pas",
                            [f"**{val}**", f"{val}"], rem.name))
        for x in b.get("harmonique_non_entiere", []):
            out.append((f"harmonique non entiere a {x['pas']} pas",
                        [f"**{x['part']}**", f"{x['part']}"], rem.name))
        for x in b.get("fourier_de_la_fenetre", []):
            out.append((f"fourier a {x['pas']} pas",
                        [f"**{x['part']}**", f"{x['part']}"], rem.name))
        if "part_absorbee_par_fourier" in b:
            val = b["part_absorbee_par_fourier"]
            out.append(("part absorbee par fourier", [f"**{val}**", f"{val}"], rem.name))
        o = d.get("lorthogonalite_est_elle_exacte", {})
        for cle, nom in (("pire_sur_la_grille_incluse", "pire recouvrement grille incluse"),
                         ("pire_sur_la_grille_dft", "pire recouvrement grille dft")):
            if cle not in o or o[cle] is None:
                continue
            val = o[cle]
            out.append((nom, [f"**{val}**", f"{val}"], rem.name))
        for x in o.get("par_fenetre", []):
            for cle, nom in (("recouvrement_grille_incluse", "recouvrement incluse a"),
                             ("recouvrement_grille_dft", "recouvrement dft a")):
                val = x[cle]
                out.append((f"{nom} {x['pas']} pas", [f"**{val}**", f"{val}"], rem.name))
        s_ = d.get("sur_les_segments_reels", {})
        for x in s_.get("par_fenetre", []):
            for cle, nom in (("fenetres", "fenetres a"),
                             ("accord_median_brut", "accord median brut a"),
                             ("accord_median_apres_retrait", "accord median apres retrait a"),
                             ("gain_median", "gain median a"),
                             ("barre_brute", "barre brute a"),
                             ("barre_apres_retrait", "barre apres retrait a"),
                             ("part_au_dessus_brut", "part au dessus brut a"),
                             ("part_au_dessus_apres_retrait", "part au dessus apres a")):
                val = x[cle]
                out.append((f"{nom} {x['pas']} pas", [f"**{val}**", f"{val}"], rem.name))

    # ⛔⛔ LE COUT QUI CONNAIT LA SPIRE (`114`), UN APPARIEMENT OBLIGATOIRE ET IL PORTE TOUT.
    # Le chiffre du CHAMP ne voyage JAMAIS sans celui du champ TOURNE. « 99,12 -> 96,14 » se lit
    # comme un succes ; c'est la troisieme variante — un champ faux par construction, qui obtient
    # 83 % de la descente — qui dit que ce qui travaille est l'existence d'une penalite et non
    # l'identite qu'elle porte. Publier l'un sans l'autre inverserait le verdict de la tranche.
    cts = _source(racine, "le_cout_qui_connait_la_spire.json")
    if cts.exists():
        d = json.loads(cts.read_text())
        for cle, nom in (("z", "z de la polaire de 114"),
                         ("colonnes", "colonnes angulaires de 114"),
                         ("secteurs_repondus", "secteurs repondus de 114")):
            if cle in d and d[cle] is not None:
                val = d[cle]
                out.append((nom, [f"**{val}**", f"{val}",
                                  f"**{val}**".replace(".", ","),
                                  f"{val}".replace(".", ",")], cts.name))
        # ⚠ Le compte de murs est un FLOTTANT dans la mesure (une mediane) et un ENTIER dans la
        # prose. Ne l'enregistrer que sous sa forme brute le declarait absent d'un document qui
        # le cite — un faux « perime » vaut un vrai, puisque les deux envoient relire.
        if d.get("murs_par_colonne") is not None:
            val = d["murs_par_colonne"]
            out.append(("murs par colonne de 114",
                        [f"**{val:.0f}**", f"{val:.0f}", f"**{val}**", f"{val}",
                         f"**{val}**".replace(".", ","), f"{val}".replace(".", ",")],
                        cts.name))
        for k in ("temoin", "champ", "constant", "tourne"):
            x = d.get("variantes", {}).get(k)
            if not x:
                continue
            val = x["morceaux_par_mur"]
            out.append((f"morceaux par mur, {k}",
                        [f"**{val:.2f}**", f"{val:.2f}",
                         f"**{val:.2f}**".replace(".", ","), f"{val:.2f}".replace(".", ",")],
                        cts.name))
        pas = d.get("pas_dindice", {})
        for cle, nom, fmt in (("pas", "pas d indice mesures de 114", "{:d}"),
                              ("feuilles_par_indice", "feuilles par pas d indice", "{:.3f}"),
                              ("negatifs", "pas d indice negatifs", "{:d}"),
                              ("pas_median_vx", "pas d indice median en voxels", "{:.1f}")):
            if cle not in pas or pas[cle] is None:
                continue
            val = fmt.format(pas[cle])
            out.append((nom, [f"**{val}**", val,
                              f"**{val}**".replace(".", ","), val.replace(".", ",")], cts.name))
        w = d.get("verdict", {})
        for cle, nom, fmt in (("gain_specifique", "part specifique de l identite", "{:.2f}"),
                              ("reste_a_couvrir", "morceaux restant a supprimer", "{:.1f}"),
                              ("gain_du_champ", "gain du champ de 114", "{:.2f}"),
                              ("gain_du_champ_tourne", "gain du champ tourne", "{:.2f}")):
            if cle not in w or w[cle] is None:
                continue
            val = fmt.format(w[cle])
            out.append((nom, [f"**{val}**", val,
                              f"**{val}**".replace(".", ","), val.replace(".", ",")], cts.name))

    # ⭐⭐⭐⭐ UNE BANDE QUI NE BOUGE PAS AVEC LA FENETRE (`111`), TROIS APPARIEMENTS OBLIGATOIRES.
    # (1) Le compte de la bande bornee ne voyage JAMAIS sans son SCORE et sa BARRE : une bande
    # etroite ne peut plus dire « pas de periodicite » par son compte, donc un compte seul se
    # lirait comme une feuille la ou il n'y en a pas. (2) La falaise AVANT ne voyage jamais sans
    # la falaise APRES — c'est leur ecart qui est le resultat. (3) Et le controle sur une DERIVE
    # SEULE ne voyage jamais sans celui sur une periodicite pure : un seul des deux laisserait
    # croire que l'instrument ne sait que trouver, ou que refuser.
    bnd = _source(racine, "une_bande_qui_ne_bouge_pas_avec_la_fenetre.json")
    if bnd.exists():
        d = json.loads(bnd.read_text())
        for cle, nom in (("marches_lues", "marches relues par 111"),
                         ("lectures", "lectures de 111"),
                         ("secondes", "secondes de 111"),
                         ("lambda_min_um", "lambda min de la bande"),
                         ("lambda_max_um", "lambda max de la bande")):
            if cle not in d or d[cle] is None:
                continue
            val = d[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], bnd.name))
        cf = d.get("controle_fabrique", {})
        for cle, nom in (("score_max_sur_une_derive_seule", "score max sur une derive seule"),
                         ("score_min_sur_une_periodicite_pure",
                          "score min sur une periodicite pure")):
            if cle not in cf or cf[cle] is None:
                continue
            val = cf[cle]
            out.append((nom, [f"**{val}**", f"{val}",
                              f"**{val}**".replace(".", ","),
                              f"{val}".replace(".", ",")], bnd.name))
        for c in cf.get("cas", []):
            for x in c["par_longueur"]:
                if not x.get("decidable"):
                    continue
                for quoi in ("ancien", "borne"):
                    for cle, nom in (("feuilles_par_pas", "compte"), ("score", "score")):
                        val = x[quoi][cle]
                        out.append((f"{nom} {quoi} de {c['cas']} a {x['pas']} pas",
                                    [f"**{val}**", f"{val}"], bnd.name))
        n_ = d.get("nul_de_la_bande", {})
        for x in n_.get("par_longueur", []):
            for cle, nom in (("p99_du_score", "barre de la bande a"),
                             ("f_min", "f min de la bande a"),
                             ("f_max", "f max de la bande a")):
                val = x[cle]
                out.append((f"{nom} {x['longueur_um']:.0f} um",
                            [f"**{val}**", f"{val}"], bnd.name))
            out.append((f"longueur de fenetre {x['longueur_um']:.0f}",
                        [f"**{x['longueur_um']:.0f}**", f"{x['longueur_um']:.0f}"], bnd.name))
        if "pente_de_la_barre" in n_ and n_["pente_de_la_barre"] is not None:
            val = n_["pente_de_la_barre"]
            out.append(("pente de la barre",
                        [f"**{val}**", f"{val}", f"**{val:+.4f}**", f"{val:+.4f}"], bnd.name))
        pm = d.get("par_mode", {})
        for nom_m in ("mode_haut", "mode_bas"):
            b = pm.get(nom_m) or {}
            if not b.get("decidable"):
                continue
            for cle, nom in (("derive_de_lancien", "derive de lancien du"),
                             ("derive_du_borne", "derive du borne du"),
                             ("ancien_au_plus_court", "ancien au plus court du"),
                             ("ancien_au_plus_long", "ancien au plus long du"),
                             ("borne_au_plus_court", "borne au plus court du"),
                             ("borne_au_plus_long", "borne au plus long du")):
                val = b[cle]
                formes = [f"**{val}**", f"{val}"]
                if cle.startswith("derive"):
                    formes += [f"**{val:+.3f}**", f"{val:+.3f}"]
                out.append((f"{nom} {nom_m}", formes, bnd.name))
            for x in b.get("par_longueur", []):
                for cle, nom in (("ancien_median", "ancien du"), ("borne_median", "borne du"),
                                 ("score_borne_median", "score borne du"),
                                 ("barre_du_score_borne", "barre du"),
                                 ("part_au_dessus_de_la_barre", "part au dessus du")):
                    if cle not in x or x[cle] is None:
                        continue
                    val = x[cle]
                    formes = [f"**{val}**", f"{val}"]
                    if cle == "part_au_dessus_de_la_barre":
                        pc = f"{100 * val:.1f}".replace(".", ",")
                        formes += [f"**{pc} %**", f"{pc} %", f"{pc}%",
                                   f"**{100 * val:.1f} %**", f"{100 * val:.1f} %",
                                   f"{100 * val:.1f}%"]
                    out.append((f"{nom} {nom_m} a {x['pas']} pas", formes, bnd.name))
        for cle, nom in (("ecart_entre_modes_au_plus_long_ancien",
                          "ecart entre modes au plus long ancien"),
                         ("ecart_entre_modes_au_plus_long_borne",
                          "ecart entre modes au plus long borne"),
                         ("falaise_de_lancien_dans_le_mode_bas", "falaise de lancien"),
                         ("falaise_du_borne_dans_le_mode_bas", "falaise du borne")):
            if cle not in pm or pm[cle] is None:
                continue
            val = pm[cle]
            out.append((nom, [f"**{val}**", f"{val}", f"**{val:+.3f}**", f"{val:+.3f}"],
                        bnd.name))
        cp = d.get("comparaison", {})
        for cle, nom in (("derive_de_lancien", "derive de lancien sur lensemble"),
                         ("derive_du_borne", "derive du borne sur lensemble")):
            if cle not in cp or cp[cle] is None:
                continue
            val = cp[cle]
            out.append((nom, [f"**{val}**", f"{val}", f"**{val:+.3f}**", f"{val:+.3f}"],
                        bnd.name))

    # ⭐⭐⭐ LE COMPTE SUIT-IL LE PAS (`110`), ET TROIS APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le biais de l'ENSEMBLE ne voyage jamais sans le partage PAR MODE : la mediane d'un
    # melange dont les proportions changent avec la longueur se lit comme une derive de la matiere
    # alors que le mode qui compte ne derive pas. (2) L'ecart entre les modes au plus court ne
    # voyage jamais sans celui au plus long, parce que c'est leur DIFFERENCE qui dit que la
    # bimodalite nait apres. (3) Et la falaise observee ne voyage jamais sans le controle
    # d'instrument qui la reproduit sur une periodicite intacte.
    cpt = _source(racine, "le_compte_suit_il_le_pas.json")
    if cpt.exists():
        d = json.loads(cpt.read_text())
        for cle, nom in (("marches_lues", "marches relues par 110"),
                         ("marches_verifiees", "marches verifiees par 110"),
                         ("lectures", "lectures de 110"),
                         ("secondes", "secondes de 110"),
                         ("graine_de_107", "graine de la re-derivation"),
                         ("ecart_max_de_verification", "ecart max de verification")):
            if cle not in d or d[cle] is None:
                continue
            val = d[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if cle == "marches_verifiees":
                formes += [f"**{val}/{d.get('marches_lues')}**",
                           f"{val}/{d.get('marches_lues')}"]
            out.append((nom, formes, cpt.name))
        cf = d.get("controle_fabrique", {})
        if "ecart_max_sur_fabrique" in cf:
            val = cf["ecart_max_sur_fabrique"]
            out.append(("ecart max sur fabrique de 110",
                        [f"**{val}**", f"{val}", f"**{val}**".replace(".", ","),
                         f"{val}".replace(".", ",")], cpt.name))
        for e in cf.get("empilements", []):
            for x in e["par_longueur"]:
                out.append((f"fabrique bruit {e['bruit']} a {x['pas']} pas",
                            [f"**{x['feuilles']}**", f"{x['feuilles']}"], cpt.name))
        s_ = d.get("le_compte_suit_il_le_pas", {})
        for x in s_.get("par_longueur", []):
            for cle, nom in (("feuilles_par_pas_median", "taux de lensemble a"),
                             ("score_median", "score median a"),
                             ("marches", "marches a")):
                val = x[cle]
                out.append((f"{nom} {x['pas']} pas",
                            [f"**{val}**", f"{val}"], cpt.name))
        if "derive_du_taux" in s_:
            val = s_["derive_du_taux"]
            out.append(("derive du taux de lensemble",
                        [f"**{val}**", f"{val}", f"**{val:+.3f}**", f"{val:+.3f}"], cpt.name))
        pm = d.get("par_mode", {})
        for nom_m in ("mode_haut", "mode_bas"):
            b = pm.get(nom_m) or {}
            if not b.get("marches"):
                continue
            for cle, nom in (("marches", "marches du"), ("derive", "derive du"),
                             ("au_plus_court", "taux au plus court du"),
                             ("au_plus_long", "taux au plus long du"),
                             ("marches_dont_le_taux_baisse", "marches qui baissent du")):
                val = b[cle]
                formes = [f"**{val}**", f"{val}"]
                if cle == "derive":
                    formes += [f"**{val:+.3f}**", f"{val:+.3f}"]
                if cle == "marches_dont_le_taux_baisse":
                    formes += [f"**{val}**/{b['marches']}", f"{val}/{b['marches']}"]
                out.append((f"{nom} {nom_m}", formes, cpt.name))
            for x in b.get("par_longueur", []):
                out.append((f"taux du {nom_m} a {x['pas']} pas",
                            [f"**{x['feuilles_par_pas_median']}**",
                             f"{x['feuilles_par_pas_median']}"], cpt.name))
        for cle, nom in (("ecart_au_plus_court", "ecart entre modes au plus court"),
                         ("ecart_au_plus_long", "ecart entre modes au plus long")):
            if cle not in pm:
                continue
            val = pm[cle]
            out.append((nom, [f"**{val}**", f"{val}", f"**{val:+.3f}**", f"{val:+.3f}"],
                        cpt.name))
        fa = d.get("la_falaise_est_elle_celle_de_linstrument", {})
        for cle, nom in (("falaises", "cas de falaise fabriquee"),
                         ("cas_essayes", "cas essayes de falaise"),
                         ("valeur_effondree_mediane", "valeur effondree mediane")):
            if cle not in fa or fa[cle] is None:
                continue
            val = fa[cle]
            out.append((nom, [f"**{val}**", f"{val}",
                              f"**{val}**".replace(".", ","),
                              f"{val}".replace(".", ",")], cpt.name))
        for x in fa.get("cas", []):
            if not (x.get("correct_au_plus_court") and x.get("effondre_ensuite")):
                continue
            for y in x["par_longueur"]:
                out.append((f"falaise lam {x['longueur_donde_en_pas']} ampl "
                            f"{x['amplitude_de_la_derive']} a {y['pas']} pas",
                            [f"**{y['feuilles_par_pas']}**", f"{y['feuilles_par_pas']}"],
                            cpt.name))
        bj = d.get("biais_ou_jitter", {})
        for cle, nom in (("biais_par_pas", "biais par pas de 110"),
                         ("jitter_par_racine_de_pas", "jitter par racine de pas"),
                         ("spires_derivees_a_120_pas_si_biais", "spires si biais"),
                         ("spires_derivees_a_120_pas_si_jitter", "spires si jitter")):
            if cle not in bj or bj[cle] is None:
                continue
            val = bj[cle]
            formes = [f"**{val}**", f"{val}", f"**{val}**".replace(".", ","),
                      f"{val}".replace(".", ",")]
            if cle.startswith("spires") or cle.startswith("biais"):
                formes += [f"**{val:+.2f}**", f"{val:+.2f}",
                           f"**{val:+.3f}**", f"{val:+.3f}"]
            out.append((nom, formes, cpt.name))
        for x in bj.get("par_longueur", []):
            for cle, nom in (("ecart_moyen", "ecart moyen a"),
                             ("ecart_type", "ecart type a")):
                val = x[cle]
                out.append((f"{nom} {x['pas']} pas",
                            [f"**{val}**", f"{val}", f"**{val:+.3f}**", f"{val:+.3f}"],
                            cpt.name))

    # ⚠⚠⚠ LA TRANCHE 125 : LA FENETRE LOCALE S'EMBALLE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) L'echelle maximale ne voyage JAMAIS sans la part en butee des deux fenetres. Seule,
    # « 32,66 » se lit comme une curiosite ; avec « 0,2202 contre 0,1649 », elle se lit pour ce
    # qu'elle est : la fenetre etait ecrite pour retirer la butee et elle en ajoute.
    # (2) Et le rho de circularite ne voyage jamais sans le mot « garanti par construction » : un
    # rho de +0,89 se lit comme une decouverte, alors que c'est une demonstration.
    sem = _source(racine, "la_fenetre_locale_semballe.json")
    if sem.exists():
        d = json.loads(sem.read_text())
        e = d.get("lechelle_semballe_t_elle", {})
        for cle, nom, dec in (("echelle_au_depart", "echelle au depart de 125", 3),
                              ("echelle_max", "echelle max de 125", 4),
                              ("echelle_min", "echelle min de 125", 4),
                              ("amplitude", "amplitude de 125", 1),
                              ("pas_um_max", "pas le plus long de 125", 1),
                              ("pas_um_en_feuilles", "pas en feuilles de 125", 1)):
            if e.get(cle) is not None:
                ajoute(nom, e[cle], dec, sem.name,
                       unites=("µm",) if cle == "pas_um_max" else ())
        a = d.get("la_fenetre_locale_a_t_elle_aide", {})
        for cle, nom, dec in (("part_en_butee", "part en butee de 125", 4),
                              ("taux", "taux de 125", 4),
                              ("reference_part_en_butee", "part en butee de reference de 125", 4),
                              ("reference_taux", "taux de reference de 125", 4)):
            if a.get(cle) is not None:
                ajoute(nom, a[cle], dec, sem.name)
        for cle, nom in (("pas", "pas de 125"), ("en_butee", "butees de 125"),
                         ("reference_pas_voyants", "pas voyants de reference de 125")):
            if a.get(cle) is not None:
                v_ = a[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], sem.name))
        b = d.get("la_boucle_est_elle_circulaire", {})
        if b.get("rho_echelle_espacement") is not None:
            ajoute("rho de circularite de 125", b["rho_echelle_espacement"], 4, sem.name,
                   signe=True)
        if b.get("pas_deductibles") is not None:
            v_ = b["pas_deductibles"]
            out.append(("pas deductibles de 125", [f"**{v_}**", f"{v_}"], sem.name))
        if d.get("plafond") is not None:
            v_ = d["plafond"]
            out.append(("plafond de 125", [f"**{v_}**", f"{v_}"], sem.name))

    # ⭐⭐⭐⭐ LA TRANCHE 129 : CE QUE LA GARDE REFUSE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) La part refusee ne voyage JAMAIS sans les deux taux confirmes. « 42 % des pas voyants
    # sont refuses » se lit comme un defaut du marcheur ; c'est « 0,7511 contre 0,7764 » qui dit
    # que le probleme est dans le PREDICAT PUBLIE, qui ne les distingue pas.
    # (2) Et le prix de l'arret ne voyage jamais sans le compte de pas CONFIRMES jetes : « 443 pas
    # sur 560 » se lit comme un budget, « dont 276 confirmes » dit ce qu'on detruirait.
    grd = _source(racine, "ce_que_la_garde_refuse.json")
    if grd.exists():
        d = json.loads(grd.read_text())
        c = d.get("combien_la_garde_refuse", {})
        for cle, nom, dec in (("part_des_voyants_refusee", "part refusee de 129", 4),
                              ("barre_deg", "barre des moities de 129", 2),
                              ("desaccord_median_des_refuses", "desaccord median de 129", 2),
                              ("desaccord_p75_des_refuses", "desaccord p75 de 129", 2),
                              ("desaccord_p90_des_refuses", "desaccord p90 de 129", 2),
                              ("desaccord_p99_des_refuses", "desaccord p99 de 129", 2),
                              ("desaccord_maximal", "desaccord maximal de 129", 1)):
            if c.get(cle) is not None:
                ajoute(nom, c[cle], dec, grd.name)
        for cle, nom in (("pas", "pas de 129"), ("aveugles", "aveugles de 129"),
                         ("voyants", "voyants de 129"),
                         ("voyants_desorientes", "voyants refuses de 129"),
                         ("marches", "marches de 129"),
                         ("marches_concernees", "marches concernees de 129")):
            if c.get(cle) is not None:
                v_ = c[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], grd.name))
        t = d.get("le_taux_distingue_t_il", {})
        for cle, nom, dec in (("taux_des_orientes", "taux des orientes de 129", 4),
                              ("taux_des_refuses", "taux des refuses de 129", 4),
                              ("ecart_median_par_marche", "ecart par marche de 129", 4),
                              ("p_appariee", "p apparie de 129", 4)):
            if t.get(cle) is not None:
                ajoute(nom, t[cle], dec, grd.name, signe=(cle == "ecart_median_par_marche"))
        for cle, nom in (("pas_orientes", "pas orientes de 129"),
                         ("pas_refuses", "pas refuses de 129"),
                         ("marches_avec_les_deux_etats", "marches appariees de 129")):
            if t.get(cle) is not None:
                v_ = t[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], grd.name))
        a = d.get("le_desaccord_est_il_absorbant", {})
        if a.get("part_de_retour_apres_un_refus") is not None:
            ajoute("part de retour de 129", a["part_de_retour_apres_un_refus"], 4, grd.name)
        if a.get("retours_attendus_au_hasard_median") is not None:
            ajoute("retours au hasard de 129", a["retours_attendus_au_hasard_median"], 1,
                   grd.name)
        for cle, nom in (("marches_ou_lorientation_revient", "retours de 129"),
                         ("marches_avec_occasion", "occasions de 129")):
            if a.get(cle) is not None:
                v_ = a[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], grd.name))
        for k_, v_ in (a.get("transitions") or {}).items():
            out.append((f"transition {k_} de 129", [f"**{v_}**", f"{v_}"], grd.name))
        g_ = d.get("le_refus_depend_il_du_rang", {})
        # ⚠ Trois decimales et non quatre : le JSON porte 0,625, et publier « 0,6250 » ferait
        # diverger le document de son producteur sur une decimale qui n'existe pas.
        for cle, nom, dec in (("part_refusee_au_rang_0", "part refusee au rang 0 de 129", 3),
                              ("part_refusee_aux_rangs_suivants",
                               "part refusee aux rangs suivants de 129", 4),
                              ("facteur_du_premier_rang", "facteur du premier rang de 129", 3),
                              ("p_du_premier_rang", "p du premier rang de 129", 4)):
            if g_.get(cle) is not None:
                ajoute(nom, g_[cle], dec, grd.name)
        q = d.get("ce_que_couterait_larret", {})
        if q.get("part_des_pas_jetes") is not None:
            ajoute("part des pas jetes de 129", q["part_des_pas_jetes"], 4, grd.name)
        if q.get("micrometres_jetes") is not None:
            ajoute("micrometres jetes de 129", q["micrometres_jetes"], 1, grd.name)
        for cle, nom in (("pas_jetes", "pas jetes de 129"),
                         ("pas_confirmes_jetes", "pas confirmes jetes de 129"),
                         ("marches_tronquees", "marches tronquees de 129")):
            if q.get(cle) is not None:
                v_ = q[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], grd.name))

    # ⭐⭐⭐⭐ LA TRANCHE 128 : LA FAILLE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le « 0,000000 » d'une faille d'une feuille ne voyage JAMAIS sans l'ecart d'une
    # demi-feuille. Seul, un zero se lit comme une panne du lecteur ; a cote de 79,999989 il se lit
    # pour ce qu'il est, une propriete de l'objet.
    # (2) Et les degres du desaccord ne voyagent jamais sans la BARRE du nul : « 88,52° » ne veut
    # rien dire tant qu'on ne sait pas qu'un cube sans structure descend sous 10,06° une fois sur
    # cent.
    fai = _source(racine, "la_faille_se_dit_elle_dans_la_lecture.json")
    if fai.exists():
        d = json.loads(fai.read_text())
        for x in d.get("la_faille_existe_t_elle", []):
            nom = f"saut {x['saut_en_feuilles']:.2f} de 128"
            ajoute(f"ecart de matiere du {nom}", x["ecart_maximal"], 6, fai.name)
        s_ = d.get("le_signal_par_distance", {})
        if s_.get("barre_daccord_des_moities_deg") is not None:
            ajoute("barre des moities de 128", s_["barre_daccord_des_moities_deg"], 2, fai.name)
        for bloc_ in s_.get("par_saut", []):
            for dd in bloc_.get("par_distance", []):
                w = dd.get("desaccord_des_moities_deg_pire")
                if not w:
                    continue
                nom = (f"pire desaccord a {dd['distance_vx']} vx, saut "
                       f"{bloc_['saut_en_feuilles']:.2f} de 128")
                for cle, suffixe, dec in (("intacte", " (intacte)", 2),
                                          ("rompue", " (rompue)", 2),
                                          ("ecart_median", " (ecart)", 4)):
                    ajoute(nom + suffixe, w[cle], dec, fai.name,
                           signe=(cle == "ecart_median"))
                if w.get("p") is not None:
                    ajoute(nom + " (p)", w["p"], 4, fai.name)
        q = d.get("ou_tombe_le_pas_refuse", {})
        if q:
            for cle, nom, dec in (("excursion_laterale_mediane_vx", "excursion rompue de 128", 2),
                                  ("excursion_laterale_intacte_mediane_vx",
                                   "excursion intacte de 128", 2),
                                  ("excursion_laterale_intacte_max_vx",
                                   "excursion intacte maximale de 128", 2),
                                  ("part_au_premier_rang", "part au premier rang de 128", 2)):
                if q.get(cle) is not None:
                    ajoute(nom, q[cle], dec, fai.name)
            for cle, nom in (("refus", "refus de 128"), ("marches", "marches de 128"),
                             ("au_premier_rang", "refus au premier rang de 128"),
                             ("marches_qui_sortent_du_cube", "marches qui sortent de 128"),
                             ("demi_cube_voxels", "demi-cube de 128")):
                if q.get(cle) is not None:
                    v_ = q[cle]
                    out.append((nom, [f"**{v_}**", f"{v_}"], fai.name))
            pp = q.get("au_premier_pas", {})
            for cle, nom, dec in (("desaccord_deg", "desaccord au premier pas de 128", 2),
                                  ("desaccord_deg_intact",
                                   "desaccord au premier pas intact de 128", 2),
                                  ("avance_um", "avance au premier pas de 128", 1),
                                  ("avance_um_intacte",
                                   "avance au premier pas intacte de 128", 1),
                                  ("part_perpendiculaire_au_plan",
                                   "part perpendiculaire de 128", 4),
                                  ("part_perpendiculaire_au_plan_intacte",
                                   "part perpendiculaire intacte de 128", 4)):
                if pp.get(cle) is not None:
                    ajoute(nom, pp[cle], dec, fai.name)

    # ⭐⭐⭐⭐ LA TRANCHE 127 : LE LIEN LATERAL, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le compte de dechirures evitees ne voyage JAMAIS sans l'ecart a la verite du temoin.
    # « 6 sur 6 a 0 sur 6, sans cout » se lit comme une solution ; le fait est que la MEME force
    # fausse un decrochement reel de 2,60 feuilles la ou l'absence de lien se trompait de 0,15.
    # (2) Et les chiffres de lambda = 0,25 ne voyagent jamais sans ceux de 0,50 : une seule force
    # se lit comme un bouton a regler, alors que la mesure est qu'elle N'EST PAS MONOTONE.
    lien = _source(racine, "un_lien_lateral_entre_marches.json")
    if lien.exists():
        d = json.loads(lien.read_text())
        n = d.get("le_lien_tient_il_la_nappe", {})
        for x in n.get("par_lien", []):
            lam = f"lien {x['lien']:.2f} de 127"
            for cle, nom, dec in (("saut_median", "saut median", 4),
                                  ("saut_max", "saut max", 4),
                                  ("taux_median", "taux median", 4),
                                  ("cout_en_taux", "cout en taux", 4)):
                if x.get(cle) is not None:
                    ajoute(f"{nom} du {lam}", x[cle], dec, lien.name,
                           signe=(cle == "cout_en_taux"))
            for cle, nom in (("se_dechirent", "lots qui se dechirent"),
                             ("lots", "lots"), ("dechirures_evitees", "dechirures evitees")):
                if x.get(cle) is not None:
                    v_ = x[cle]
                    out.append((f"{nom} du {lam}", [f"**{v_}**", f"{v_}"], lien.name))
        for t in d.get("temoin_par_lien", []):
            lam = f"temoin {t['avec_lien']['lien']:.2f} de 127"
            for cle, nom, dec in (("saut_injecte_en_feuilles", "decrochement injecte", 3),
                                  ("saut_vrai_en_feuilles", "verite", 4),
                                  ("ecart_a_la_verite_sans_lien", "ecart sans lien", 4),
                                  ("ecart_a_la_verite_avec_lien", "ecart avec lien", 4)):
                if t.get(cle) is not None:
                    ajoute(f"{nom} du {lam}", t[cle], dec, lien.name)
            for nom, cle in (("saut sans lien", "sans_lien"), ("saut avec lien", "avec_lien")):
                if t.get(cle, {}).get("saut") is not None:
                    ajoute(f"{nom} du {lam}", t[cle]["saut"], 4, lien.name)

    # ⭐⭐⭐⭐ LA TRANCHE 124 : LA NAPPE SE DECHIRE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le saut median ne voyage JAMAIS sans le compte de lots qui se dechirent : « 1,02 feuille »
    # est une mediane d'une distribution a deux bosses, donc elle ne decrit aucune des deux ; c'est
    # « 9 sur 12 » qui dit ce qui se passe.
    # (2) Et le rho du pas 16 ne voyage jamais sans son p : « +0,4545 » seul se lit comme un lien,
    # alors que le fait est qu'il n'est PAS etabli sur douze lots.
    nap = _source(racine, "la_nappe_se_dechire_t_elle.json")
    if nap.exists():
        d = json.loads(nap.read_text())
        # ⚠ Quatre décimales : le JSON en porte quatre, et en publier trois ferait diverger le
        # document de son producteur sur la dernière — le genre d'écart qui se lit comme une
        # coquille alors que c'est une troncature.
        for cle, nom, dec in (("saut_median_entre_voisines", "saut median de 124", 4),
                              ("saut_min", "saut min de 124", 4),
                              ("saut_max", "saut max de 124", 4),
                              ("part_des_lots_qui_se_dechirent", "part des lots de 124", 3)):
            if d.get(cle) is not None:
                ajoute(nom, d[cle], dec, nap.name)
        for cle, nom in (("lots_qui_se_dechirent", "lots qui se dechirent de 124"),
                         ("lots", "lots de 124"), ("lots_couples", "lots couples de 124"),
                         ("marches_par_lot", "marches par lot de 124")):
            if d.get(cle) is not None:
                v_ = d[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], nap.name))
        for r_ in d.get("repetitions", []):
            ajoute(f"saut de la graine {r_['graine']} de 124",
                   r_["saut_maximal_entre_voisines"], 3, nap.name)
        e = d.get("le_dechirement_se_voit_il_tot", {})
        if e.get("decidable"):
            ajoute("rho precoce de 124", e["rho"], 4, nap.name, signe=True)
            ajoute("p precoce de 124", e["p"], 4, nap.name)

    # ⭐⭐⭐⭐ LA TRANCHE 123 : LE MARCHEUR RESTE VERROUILLE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Les ecarts des quatre conditions ne voyagent JAMAIS sans ceux du TEMOIN. Seuls, deux
    # nombres qui ne bougent pas se lisent comme « le test ne voit rien » ; avec « 0,2287 ->
    # 0,2713, p 0,0005 » sur le pas nominal impose, ils se lisent pour ce qu'ils sont.
    # (2) Et l'avance par pas ne voyage jamais sans le plafond de 112 : « 1,0067 feuille » ne veut
    # rien dire tant qu'on ne sait pas sur combien de pas l'exces se cumule.
    ver = _source(racine, "le_marcheur_reste_t_il_verrouille.json")
    if ver.exists():
        d = json.loads(ver.read_text())
        for c in d.get("conditions", []):
            if not c.get("decidable"):
                continue
            nom = f"{c['obliquite_deg']:.0f} deg bruit {c['bruit']:.0f} de 123"
            for cle, suffixe in (("ecart_median_premier_tiers", " (1er tiers)"),
                                 ("ecart_median_dernier_tiers", " (dernier tiers)")):
                ajoute(nom + suffixe, c[cle], 4, ver.name)
            if c.get("p_appariee") is not None:
                ajoute(nom + " (p)", c["p_appariee"], 4, ver.name)
            if c.get("avance_par_pas_mediane") is not None:
                ajoute(nom + " (avance)", c["avance_par_pas_mediane"], 4, ver.name)
        w = d.get("temoin_le_pas_impose_derive", {})
        if w.get("decidable"):
            for cle, nom, dec in (("ecart_median_premier_tiers", "temoin 1er tiers de 123", 4),
                                  ("ecart_median_dernier_tiers", "temoin dernier tiers de 123", 4),
                                  ("p_appariee", "temoin p de 123", 4),
                                  ("avance_attendue_par_pas", "temoin avance de 123", 4)):
                if w.get(cle) is not None:
                    ajoute(nom, w[cle], dec, ver.name)
        if d.get("marches_par_condition") is not None:
            v_ = d["marches_par_condition"]
            out.append(("marches par condition de 123", [f"**{v_}**", f"{v_}"], ver.name))

    # ⭐⭐⭐⭐ LA TRANCHE 122 : LA FENETRE LOCALE RETIRE LA BUTEE, ET DEUX APPARIEMENTS LE DISENT.
    # (1) Le « 0 en butee » de la fenetre locale ne voyage JAMAIS sans le « 3 » de la fixe : seul,
    # zero se lit comme « rien ne se passe », alors que le fait est l'ECART entre les deux
    # fenetres sur la MEME pile.
    # (2) Et le pas minimal de la locale ne voyage jamais sans le bout court de la fenetre fixe :
    # « 50,0 µm » n'est un resultat que parce que la fenetre fixe s'arrete a 86,5.
    dem = _source(racine, "la_fenetre_locale_sur_une_pile_connue.json")
    if dem.exists():
        d = json.loads(dem.read_text())
        for cle, nom, dec in (("pas_nominal_um", "pas nominal de 122", 1),
                              ("bout_court_um", "bout court de 122", 1),
                              ("bout_long_um", "bout long de 122", 1)):
            if d.get(cle) is not None:
                ajoute(nom, d[cle], dec, dem.name, unites=("µm",))
        if d.get("pas_par_um") is not None:
            ajoute("pente du pas de 122", d["pas_par_um"], 2, dem.name)
        for nom_m, m in d.get("marches", {}).items():
            for cle, etiquette in (("pas", "pas"), ("en_butee", "en butee"),
                                   ("confirmes", "confirmes")):
                if m.get(cle) is not None:
                    v_ = m[cle]
                    out.append((f"{nom_m} {etiquette} de 122", [f"**{v_}**", f"{v_}"], dem.name))
            if m.get("pas_um_min") is not None:
                ajoute(f"{nom_m} pas minimal de 122", m["pas_um_min"], 1, dem.name,
                       unites=("µm",))
            if m.get("echelle_min") is not None:
                ajoute(f"{nom_m} echelle minimale de 122", m["echelle_min"], 3, dem.name)

    # ⭐⭐⭐⭐ LA TRANCHE 121 : RECENTRER EST GRATUIT, ELARGIR NON, ET DEUX APPARIEMENTS LE DISENT.
    # (1) L'invariance au recentrage ne voyage JAMAIS sans l'ecart a l'elargissement. Seule,
    # « 2,6e-16 » se lit comme « le nul ne depend de rien », ce qui viderait la mesure ; avec
    # « 1,2 sigma quand la largeur change », elle se lit pour ce qu'elle est, une propriete des
    # RAPPORTS.
    # (2) Et aucun des deux ne voyage sans l'amplitude du nul : un nul plat rendrait zero partout,
    # donc c'est « 0,1582 -> 0,0925 » qui donne au zero son sens.
    rof = _source(racine, "recentrer_ou_elargir_la_fenetre.json")
    if rof.exists():
        d = json.loads(rof.read_text())
        c = d.get("le_nul_a_t_il_quelque_chose_a_dire", {})
        for cle, nom, dec in (("mu_du_plus_court", "nul du plus court de 121", 4),
                              ("mu_du_plus_long", "nul du plus long de 121", 4),
                              ("amplitude", "amplitude du nul de 121", 4),
                              ("sd_median", "sigma du nul de 121", 5),
                              ("amplitude_en_erreurs_types", "amplitude en erreurs-types de 121", 1),
                              ("amplitude_en_sigma", "amplitude en sigma de 121", 2)):
            if c.get(cle) is not None:
                ajoute(nom, c[cle], dec, rof.name)
        if c.get("tirages") is not None:
            v_ = c["tirages"]
            out.append(("tirages du nul de 121", [f"**{v_}**", f"{v_}"], rof.name))
        r_ = d.get("le_nul_survit_il_au_recentrage", {})
        for x in r_.get("par_nominal", []):
            ajoute(f"centre {x['nominal_um']:.0f} de 121", x["nominal_um"], 0, rof.name,
                   unites=("µm",))
        e_ = d.get("le_nul_survit_il_a_lelargissement", {})
        for x in e_.get("par_fenetre", []):
            if x["ecart_max"]:
                ajoute(f"ecart de la fenetre [{x['bas']} ; {x['haut']}] de 121",
                       x["ecart_max"], 5, rof.name)
                ajoute(f"ecart en sigma de la fenetre [{x['bas']} ; {x['haut']}] de 121",
                       x["ecart_en_sigma"], 1, rof.name)

    # ⭐⭐⭐⭐ LA TRANCHE 130 : LE BUDGET N'ACHETE PLUS DE PORTEE, ET TROIS APPARIEMENTS L'IMPOSENT.
    # (1) Le net ne voyage JAMAIS sans le chemin. « 3 726,5 µm » seul se lit comme une petite
    # marche ; a cote de « 20 389,8 µm parcourus » il se lit pour ce qu'il est, un retour.
    # (2) Le compte des marches qui culminent avant le plafond ne voyage jamais sans celui de la
    # course de vingt pas : « 2 sur 3 » seul pourrait etre le regime ordinaire, « contre 0 sur
    # 17 » dit que c'est le plafond qui a change.
    # (3) Et le rho de la rectitude contre la longueur ne voyage jamais sans celui a LONGUEUR
    # EGALE : le premier est un confondant mecanique, le second est ce qui reste quand on l'ote.
    for nom_, fichier_ in (("130", "le_marcheur_derive_sur_la_re_course.json"),
                           ("131", "le_marcheur_derive_sur_la_course_large.json"),
                           ("119", "le_marcheur_derive_t_il.json")):
        src = _source(racine, fichier_)
        if not src.exists():
            continue
        d = json.loads(src.read_text())
        q = d.get("la_rectitude_decroit_elle_avec_la_longueur", {})
        for cle, nom, dec, signe in (("rectitude_mediane", "rectitude mediane", 4, False),
                                     ("rectitude_min", "rectitude min", 4, False),
                                     ("rectitude_max", "rectitude max", 4, False),
                                     ("net_median_um", "net median", 1, False),
                                     ("chemin_median_um", "chemin median", 1, False),
                                     ("rho_de_spearman", "rho rectitude-longueur", 4, True),
                                     ("p", "p rectitude-longueur", 4, False),
                                     ("rho_a_longueur_egale", "rho a longueur egale", 4, True),
                                     ("p_a_longueur_egale", "p a longueur egale", 4, False)):
            if q.get(cle) is not None:
                ajoute(f"{nom} de {nom_}", q[cle], dec, src.name, signe=signe)
        if q.get("plancher_de_troncature") is not None:
            v_ = q["plancher_de_troncature"]
            out.append((f"plancher de troncature de {nom_}", [f"**{v_}**", f"{v_}"], src.name))
        j = d.get("jusquou_le_net_progresse_t_il", {})
        if j.get("decidable"):
            for cle, nom, dec in (("net_maximum_median_um", "net maximum median", 1),
                                  ("net_au_plafond_median_um", "net au plafond median", 1)):
                if j.get(cle) is not None:
                    ajoute(f"{nom} de {nom_}", j[cle], dec, src.name)
            for cle, nom in (("plafond", "plafond"), ("marches", "marches au plafond"),
                             ("marches_de_la_course", "marches de la course"),
                             ("k_du_maximum_median", "pas du maximum"),
                             ("marches_dont_le_net_culmine_avant_le_plafond",
                              "marches qui culminent avant")):
                if j.get(cle) is not None:
                    v_ = j[cle]
                    out.append((f"{nom} de {nom_}", [f"**{v_}**", f"{v_}"], src.name))
            for x in j.get("par_marche", []):
                ajoute(f"net maximum au rayon {x['rayon_mm']} de {nom_}",
                       x["net_maximum_um"], 1, src.name)
                ajoute(f"net au plafond au rayon {x['rayon_mm']} de {nom_}",
                       x["net_au_plafond_um"], 1, src.name)
            for x in j.get("courbe", []):
                ajoute(f"net au pas {x['pas']} de {nom_}", x["net_median_um"], 1, src.name)
                ajoute(f"chemin au pas {x['pas']} de {nom_}", x["chemin_median_um"], 1, src.name)

    # ⭐⭐⭐⭐ LA TRANCHE 132 : LE CAP, ET TROIS APPARIEMENTS L'IMPOSENT.
    # (1) Le virage VRAI ne voyage JAMAIS sans celui du marcheur. « 0,0103° par pas » seul se lit
    # comme une precision d'instrument ; a cote de « 2,83° », il dit que le marcheur tourne 274
    # fois plus que la matiere ne demande.
    # (2) Le cosinus entre virages ne voyage jamais sans son p ET son compte de marches : un
    # « -0,21 » seul se lit comme un effet faible, alors que 14 marches sur 14 negatives en font
    # un fait.
    # (3) Et la rectitude de la pile plane ne voyage jamais sans celles du vrai rouleau : 0,9994
    # seul se lit comme un bon marcheur, a cote de 0,183 et 0,078 il dit que la fixture est trop
    # facile.
    cap = _source(racine, "un_cap_a_memoire.json")
    if cap.exists():
        d = json.loads(cap.read_text())
        w = d.get("combien_de_virage_la_matiere_demande", {})
        if w.get("decidable"):
            for cle, nom, dec in (# ⚠ Le rayon de depart est un rond : le publier a la decimale le ferait diverger
                                  # du document sur un zero qui ne veut rien dire.
                                  ("rayon_depart_um", "rayon de depart de 132", 0),
                                  ("rayon_arrivee_um", "rayon d arrivee de 132", 1),
                                  ("angle_parcouru_deg", "angle parcouru de 132", 4),
                                  ("virage_vrai_total_deg", "virage vrai total de 132", 4),
                                  ("virage_vrai_median_deg", "virage vrai par pas de 132", 4),
                                  ("virage_vrai_max_deg", "virage vrai max de 132", 4),
                                  ("virage_du_marcheur_median_deg",
                                   "virage du marcheur de 132", 2),
                                  ("virage_du_marcheur_max_deg",
                                   "virage du marcheur max de 132", 2),
                                  ("facteur", "facteur de 132", 1)):
                if w.get(cle) is not None:
                    ajoute(nom, w[cle], dec, cap.name)
        a_ = d.get("le_virage_reel_persiste_t_il", {})
        if a_.get("decidable"):
            for cle, nom, dec, signe in (("cos_median", "cos median de 132", 4, True),
                                         ("cos_min", "cos min de 132", 3, True),
                                         ("cos_max", "cos max de 132", 4, True),
                                         ("p_contre_zero", "p du cos de 132", 6, False)):
                if a_.get(cle) is not None:
                    ajoute(nom, a_[cle], dec, cap.name, signe=signe)
            for cle, nom in (("marches", "marches du cos de 132"),
                             ("marches_negatives", "marches negatives de 132")):
                if a_.get(cle) is not None:
                    v_ = a_[cle]
                    out.append((nom, [f"**{v_}**", f"{v_}"], cap.name))
        for x in d.get("ce_que_la_memoire_change", {}).get("par_memoire", []):
            nom = f"memoire {x['memoire']:.2f} de 132"
            for cle, quoi, dec in (("erreur_mediane_deg", "erreur mediane", 3),
                                   ("erreur_max_deg", "erreur max", 3),
                                   ("taux_median", "taux", 3),
                                   ("gain_en_erreur_deg", "gain", 3),
                                   ("cout_en_taux", "cout", 1)):
                if x.get(cle) is not None:
                    ajoute(f"{quoi} de la {nom}", x[cle], dec, cap.name)
        pl = d.get("la_pile_plane_derive_t_elle", {})
        if pl.get("decidable"):
            for cle, nom, dec in (("rectitude_mediane", "rectitude de la pile plane de 132", 4),
                                  ("virage_median_deg", "virage de la pile plane de 132", 1),
                                  ("taux_median", "taux de la pile plane de 132", 3),
                                  ("obliquite_deg", "obliquite de 132", 0),
                                  ("bruit", "bruit de 132", 0)):
                if pl.get(cle) is not None:
                    ajoute(nom, pl[cle], dec, cap.name)

    # ⭐⭐⭐⭐ LA TRANCHE 138 : LES JUMELLES, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) La derive du ROULEAU ne voyage jamais sans celles des DEUX piles : « 3,045 feuilles » seul
    # est un nombre, entre « 0,255 sur une matiere qui ne distingue pas ses feuilles » et « 0,705
    # sur une matiere qui les distingue » il devient une lecture.
    # (2) Et la derive LUE ne voyage jamais sans la VRAIE la ou celle-ci existe : sur la pile
    # periodique le compteur lit 0,255 pour une verite de 0,05, donc son plancher est publie a cote
    # de ce qu'il mesure.
    # ⚠⚠ SEUL CE QUE LE DOCUMENT PUBLIE EST ENREGISTRE, et ma premiere version enregistrait tout ce
    # que le JSON porte — cinquante nombres que le document resume expres, donc cinquante alertes
    # « chiffre recalcule qui n'apparait nulle part », et une alerte permanente est une alerte qu'on
    # cesse de lire.
    jum = _source(racine, "deux_marches_jumelles.json")
    if jum.exists():
        d = json.loads(jum.read_text())

        def dec138(v, plafond):
            s_ = repr(float(v))
            return min(plafond, len(s_.split(".")[1]) if "." in s_ and "e" not in s_ else plafond)

        for cle, nom in (("la_pile_periodique", "pile periodique"),
                         ("la_pile_par_feuille", "pile par feuille"),
                         ("le_rouleau", "rouleau")):
            bloc_ = d.get(cle) or {}
            r_ = bloc_.get("resume", {})
            if not r_.get("decidable"):
                continue
            ajoute(f"paires de 138 {nom}", r_["paires"], 0, jum.name)
            for c_, n_, dd in (("derive_lue_mediane", "derive lue", 3),
                               ("derive_vraie_mediane", "derive vraie", 3),
                               ("erreur_de_comptage_mediane", "erreur de comptage", 3),
                               ("traversee_mediane", "traversee", 2),
                               ("part_des_paires_au_dela_dune_feuille", "part au-dela dune feuille",
                                3),
                               ("max_sur_finale_median", "max sur finale", 2)):
                if r_.get(c_) is not None:
                    ajoute(f"{n_} de 138 {nom}", r_[c_], dec138(r_[c_], dd), jum.name)
            # ⚠ Le p90 n'est publie que la ou le document s'en sert : le PLANCHER de la pile
            # periodique et la queue du rouleau.
            if cle in ("la_pile_periodique", "le_rouleau") and r_.get("derive_lue_p90") is not None:
                ajoute(f"derive lue p90 de 138 {nom}", r_["derive_lue_p90"],
                       dec138(r_["derive_lue_p90"], 3), jum.name)
            # ⚠ Le tableau du §4 publie la derive LUE par ecart, et rien d'autre par ecart.
            for b_ in r_.get("par_ecart", []):
                e_ = int(b_["ecart_vx"])
                if b_.get("derive_lue_mediane") is not None:
                    ajoute(f"derive lue a {e_} vx de 138 {nom}", b_["derive_lue_mediane"],
                           dec138(b_["derive_lue_mediane"], 3), jum.name)
        # ⚠ Le decalage de phase au depart n'est cite qu'aux DEUX bouts, sur la pile periodique.
        per = ((d.get("la_pile_periodique") or {}).get("resume") or {}).get("par_ecart", [])
        for b_ in per:
            if int(b_["ecart_vx"]) in (min(int(x["ecart_vx"]) for x in per),
                                       max(int(x["ecart_vx"]) for x in per)) \
                    and b_.get("decalage_au_depart_median") is not None:
                ajoute(f"decalage au depart a {int(b_['ecart_vx'])} vx de 138",
                       b_["decalage_au_depart_median"],
                       dec138(b_["decalage_au_depart_median"], 4), jum.name)
        for cle, nom in (("sur_la_pile_periodique", "pile periodique"),
                         ("sur_la_pile_par_feuille", "pile par feuille")):
            c_ = (d.get("le_compteur_voit_il_la_separation") or {}).get(cle, {})
            if not c_.get("decidable") or c_.get("aucune_variation"):
                continue
            # ⚠⚠ `p_du_rang` n'est PAS enregistre, et les `p_de_rang` des comparaisons non plus :
            # ils valent 1,4e-05 ou 8,82e-07, et le garde les rendrait « 0,000014 » ou
            # « 0,00000088 » — une forme decimale tronquee qui n'est PLUS le meme nombre. Le
            # document les cite dans la notation du producteur. C'est le choix que `136` a deja
            # fait pour son p de 2e-08.
            for k_, n_, dd, sg in (("rho_de_spearman", "rho du compteur", 4, True),
                                   ("p_apparie", "p apparie du compteur", 5, False)):
                if c_.get(k_) is not None:
                    ajoute(f"{n_} de 138 {nom}", c_[k_], dec138(c_[k_], dd), jum.name, signe=sg)
        # ⚠ Le diagnostic « d'ou vient la derive » n'est publie QUE pour le rouleau : c'est la seule
        # matiere dont le document en tire un verdict.
        o_ = (d.get("dou_vient_la_derive") or {}).get("sur_le_rouleau", {})
        if o_.get("decidable"):
            for k_, n_, dd, sg in (("rho_ecart_lateral", "rho de l ecart lateral de 138", 4, True),
                                   ("p_ecart_lateral", "p de l ecart lateral de 138", 5, False),
                                   ("rho_desaccord_au_depart", "rho du desaccord de 138", 4, True),
                                   ("p_desaccord_au_depart", "p du desaccord de 138", 5, False),
                                   ("derive_a_lecart_le_plus_petit",
                                    "derive au plus petit ecart de 138", 3, False)):
                if o_.get(k_) is not None:
                    ajoute(n_, o_[k_], dec138(o_[k_], dd), jum.name, signe=sg)
        j_ = d.get("juger", {})
        if j_.get("decidable"):
            for k_, n_, dd in (("combien_de_fois_plus", "combien de fois plus de 138", 1),
                               ("plancher_du_bruit_p90_periodique", "plancher du bruit de 138", 3)):
                if j_.get(k_) is not None:
                    ajoute(n_, j_[k_], dec138(j_[k_], dd), jum.name)

    # ⭐⭐⭐⭐ LA TRANCHE 137 : LE PENCHANT DU CHEMIN, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) L'angle lu sur le ROULEAU ne voyage jamais sans celui lu sur la FIXTURE : « 25,48° » seul
    # est un nombre, a cote de « 0,22° sur une spirale a 0,394° » il dit que l'instrument lit le
    # penchant au lieu de le fabriquer.
    # (2) Et la COHERENCE ne voyage jamais sans l'ANGLE : 0,925 seul ne dit rien, a cote de 25,48°
    # il dit que le chemin penche au lieu de serpenter — deux marches de meme angle rendent 1 et 0.
    # ⚠ Seul le lot AVEC CAP porte l'ecart cylindrique / spherique et l'etendue du maillage : le
    # document ne publie ces nombres que pour lui, et enregistrer ceux du lot sans cap ferait crier
    # « chiffre recalcule qui n'apparait nulle part » sur des nombres que le document resume expres.
    penche = _source(racine, "le_chemin_penche_t_il_ou_serpente_t_il.json")
    if penche.exists():
        d = json.loads(penche.read_text())

        def dec137(v, plafond):
            s_ = repr(float(v))
            return min(plafond, len(s_.split(".")[1]) if "." in s_ and "e" not in s_ else plafond)

        a_ = d.get("laxe", {})
        if a_.get("decidable"):
            ajoute("radiaux de l axe de 137", a_["radiaux"], 0, penche.name)
            for c_, n_ in (("angle_au_plan_perpendiculaire_a_z_median_deg", "angle a l axe de 137"),
                           ("angle_max_deg", "angle max a l axe de 137")):
                ajoute(n_, a_[c_], dec137(a_[c_], 3), penche.name)
        for c_ in d.get("par_course", []):
            nom_c = "avec cap" if c_["memoire_du_cap"] else "sans cap"
            f_ = c_.get("la_forme_du_penchant", {})
            if f_.get("decidable"):
                for cle, nom in (("marches", "marches arrivees"), ("pas", "pas"),
                                 ("pas_au_dela_de_90_deg", "retours vers l axe"),
                                 ("bandes_qui_glissent_vers_les_z_croissants", "bandes vers les z croissants")):
                    ajoute(f"{nom} de 137 {nom_c}", f_[cle], 0, penche.name)
                for cle, nom, dd in (("angle_median_deg", "penchant median", 2),
                                     ("angle_q1_deg", "penchant q1", 2),
                                     ("angle_q3_deg", "penchant q3", 2),
                                     ("angle_p90_deg", "penchant p90", 2),
                                     ("part_des_pas_au_dela_de_90", "part des retours", 4),
                                     ("coherence_mediane", "coherence", 3),
                                     ("coherence_min", "coherence min", 3),
                                     ("axial_absolu_median", "part axiale", 3),
                                     ("azimutal_absolu_median", "part azimutale", 3),
                                     ("glissement_axial_median_um", "glissement axial", 1),
                                     ("p_du_signe_axial", "p du signe axial", 4)):
                    if f_.get(cle) is not None:
                        ajoute(f"{nom} de 137 {nom_c}", f_[cle], dec137(f_[cle], dd), penche.name)
                if c_["memoire_du_cap"]:
                    for cle, nom in (("le_rayon_spherique_surestime_letendue_de", "surestimation spherique de 137"),
                                     ("et_au_plus_de", "surestimation spherique max de 137")):
                        if f_.get(cle) is not None:
                            ajoute(nom, f_[cle], dec137(f_[cle], 4), penche.name)
            m_ = c_.get("le_penchant_saccorde_t_il_au_maillage", {})
            if m_.get("decidable"):
                for cle, nom, dd, sg in (("penchant_median_deg", "penchant apparie", 2, False),
                                         ("maillage_median_deg", "maillage", 2, False),
                                         ("ecart_median_deg", "ecart au maillage", 2, True),
                                         ("p_apparie", "p apparie du maillage", 5, False),
                                         ("rho_de_spearman", "rho du maillage", 4, True),
                                         ("p_du_rang", "p du rang du maillage", 5, False)):
                    if m_.get(cle) is not None:
                        ajoute(f"{nom} de 137 {nom_c}", m_[cle], dec137(m_[cle], dd), penche.name,
                               signe=sg)
                if c_["memoire_du_cap"]:
                    for cle, nom in (("etendue_du_maillage_deg", "etendue du maillage de 137"),
                                     ("etendue_du_penchant_deg", "etendue du penchant de 137")):
                        for k_, b_ in zip(("bas", "haut"), m_.get(cle, ())):
                            ajoute(f"{nom} {k_}", b_, dec137(b_, 2), penche.name)
        fx = d.get("la_fixture_tranche_t_elle", {})
        for sp in fx.get("spirales", []):
            r_ = sp["rayon_mm"]
            ajoute(f"inclinaison analytique a {r_} de 137", sp["inclinaison_analytique_deg"],
                   dec137(sp["inclinaison_analytique_deg"], 3), penche.name)
            for c2 in sp.get("par_cap", []):
                if c2.get("angle_median_deg") is not None:
                    ajoute(f"spirale a {r_} lue a {c2['memoire_du_cap']} de 137",
                           c2["angle_median_deg"], dec137(c2["angle_median_deg"], 2), penche.name)
                fin_ = c2.get("inclinaison_analytique_a_larrivee_deg")
                if fin_ is not None:
                    ajoute(f"inclinaison a l arrivee a {r_} de 137", fin_, dec137(fin_, 3),
                           penche.name)
        for pi in fx.get("piles", []):
            for c2 in pi.get("par_cap", []):
                for cle, nom, dd in (("angle_median_deg", "penchant", 2),
                                     ("coherence_tangentielle", "coherence", 3)):
                    if c2.get(cle) is not None:
                        ajoute(f"pile {pi['amplitude_um']} {nom} a {c2['memoire_du_cap']} de 137",
                               c2[cle], dec137(c2[cle], dd), penche.name)

    # ⭐⭐⭐⭐ LA TRANCHE 136 : LE COMPTE DE FEUILLES, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) L'espacement implique par le CHEMIN ne voyage jamais sans celui du RAYON : « 166,4 µm,
    # d'accord avec 164 » se lit comme un succes, a cote de « 140,3 par le rayon » il dit que les
    # deux comptes ne sont pas le meme et que l'un des deux est une erreur.
    # (2) Et le compte sur l'EPAISSEUR ne voyage jamais sans le compte sur le CHEMIN : 1,018 seul
    # ne dit rien, a cote de 0,654 il dit lequel des deux l'instrument suit.
    cfm = _source(racine, "combien_de_feuilles_le_marcheur_croit_franchir.json")
    if cfm.exists():
        d = json.loads(cfm.read_text())

        def dec136(v, plafond):
            s = repr(float(v))
            return min(plafond, len(s.split(".")[1]) if "." in s and "e" not in s else plafond)

        for cle, nom in (("lecart_au_compte_geometrique", "136"), ("avec_cap", "136 avec cap"),
                         ("sans_cap", "136 sans cap")):
            g = d.get(cle, {})
            if not g.get("decidable"):
                continue
            champs = [("espacement_implique_par_le_rayon_um", "espacement par le rayon"),
                      ("espacement_implique_par_le_chemin_um", "espacement par le chemin")]
            # ⚠ Les MIN et MAX ne sont enregistres que pour le lot COMPLET : le document publie
            # l'etendue de l'ensemble, pas celle de chaque sous-lot. Enregistrer les autres
            # ferait crier « chiffre recalcule qui n'apparait nulle part » sur des nombres que le
            # document resume expres, et une alerte permanente est une alerte qu'on cesse de lire.
            if cle == "lecart_au_compte_geometrique":
                champs += [("espacement_implique_par_le_rayon_min", "espacement rayon min"),
                           ("espacement_implique_par_le_rayon_max", "espacement rayon max"),
                           ("espacement_implique_par_le_chemin_min", "espacement chemin min"),
                           ("espacement_implique_par_le_chemin_max", "espacement chemin max")]
            for c_, n_ in champs:
                if g.get(c_) is not None:
                    ajoute(f"{n_} de {nom}", g[c_], dec136(g[c_], 1), cfm.name)
            if g.get("traversees") is not None:
                ajoute(f"traversees de {nom}", g["traversees"], 0, cfm.name)
            # ⚠ Idem : l'erreur en spires du lot SANS CAP est resumee par le §5 sous la forme
            # « 11,6 → 5,3 », qui est l'ecart apparie et non l'erreur du lot — deux nombres
            # differents, et c'est le second que le document publie.
            if cle != "sans_cap":
                for e in g.get("par_espacement", []):
                    ajoute(f"erreur a {e['espacement_um']} de {nom}", e["erreur_mediane_spires"],
                           dec136(e["erreur_mediane_spires"], 1), cfm.name, signe=True)
        o = d.get("le_surcomptage_est_il_lobliquite", {})
        if o.get("decidable"):
            for c_, n_, dd, sg in (("obliquite_mediane", "obliquite du chemin de 136", 3, False),
                                   ("sur_comptage_median", "sur-comptage de 136", 3, False),
                                   ("ecart_median", "ecart obliquite de 136", 4, True),
                                   ("rho_de_spearman", "rho de 136", 4, True),
                                   ("p_apparie", "p apparie de l obliquite de 136", 4, False),
                                   ("feuilles_par_espacement_de_chemin",
                                    "feuilles par espacement de chemin de 136", 4, False)):
                if o.get(c_) is not None:
                    ajoute(n_, o[c_], dec136(o[c_], dd), cfm.name, signe=sg)
        c_ = d.get("le_cap_reduit_il_lerreur", {})
        if c_.get("decidable"):
            for k_, n_, dd in (("erreur_mediane_sans_cap", "erreur sans cap de 136", 1),
                               ("erreur_mediane_avec_cap", "erreur avec cap de 136", 1),
                               ("p_apparie", "p du cap de 136", 5)):
                if c_.get(k_) is not None:
                    ajoute(n_, c_[k_], dec136(c_[k_], dd), cfm.name)
            for k_, n_ in (("paires", "paires du cap de 136"),
                           ("marches_ou_le_cap_se_trompe_moins", "bandes ou le cap gagne de 136")):
                if c_.get(k_) is not None:
                    ajoute(n_, c_[k_], 0, cfm.name)
        f_ = d.get("la_fixture_tranche_t_elle", {})
        if f_.get("decidable"):
            for x in f_.get("lots", []):
                a_ = x["angle_a_la_normale_deg"]
                for k_, n_ in (("compte_sur_epaisseur", "compte sur epaisseur"),
                               ("compte_sur_chemin", "compte sur chemin"),
                               ("chemin_um", "chemin"), ("epaisseur_um", "epaisseur"),
                               ("feuilles_comptees", "comptees")):
                    if x.get(k_) is not None:
                        ajoute(f"{n_} a {a_} de 136", x[k_], dec136(x[k_], 3), cfm.name)
            for k_, n_ in (("compte_sur_epaisseur_median", "compte sur epaisseur median de 136"),
                           ("compte_sur_chemin_median", "compte sur chemin median de 136")):
                if f_.get(k_) is not None:
                    ajoute(n_, f_[k_], dec136(f_[k_], 3), cfm.name)
        z_ = d.get("un_zigzag_compte_t_il_double", {})
        if z_.get("decidable"):
            for x in z_.get("paires", []):
                for k_, n_ in (("droit", "zigzag droit"), ("zigzag", "zigzag alterne"),
                               ("ecart", "zigzag ecart")):
                    ajoute(f"{n_} a {x['angle_deg']} de 136", x[k_], dec136(x[k_], 3), cfm.name,
                           signe=(k_ == "ecart"))
            if z_.get("ecart_median_oblique") is not None:
                ajoute("ecart median du zigzag de 136", z_["ecart_median_oblique"],
                       dec136(z_["ecart_median_oblique"], 3), cfm.name, signe=True)

    # ⭐⭐⭐⭐ LA TRANCHE 135 : LA SURFACE DU ROULEAU, ET UN APPARIEMENT L'IMPOSE.
    # Le compte d'arrets sortis ne voyage jamais sans l'ECART median a la surface : « 14/14 » seul
    # se lit comme un verdict, a cote de « 0,3 mm » il dit que la surface a ete LUE et pas supposee.
    cesse = _source(racine, "ou_la_matiere_cesse_de_se_lire.json")
    if cesse.exists():
        d = json.loads(cesse.read_text())

        def dec135(v, plafond):
            s = repr(float(v))
            return min(plafond, len(s.split(".")[1]) if "." in s and "e" not in s else plafond)

        for c_ in d.get("par_course", []):
            nom_c = c_["source"].replace(".json", "").replace("_", " ")
            r_ = c_.get("resume", {})
            for cle, nom in (("plus_rien_a_lire", "arrets"), ("sortis_du_rouleau", "sortis"),
                             ("a_la_surface", "a la surface"), ("au_dela_de_la_surface", "au-dela"),
                             ("dans_un_vide_interieur", "dans un vide"), ("decidables", "decidables")):
                if r_.get(cle) is not None:
                    ajoute(f"{nom} de {nom_c} de 135", r_[cle], 0, cesse.name)
            for cle, nom in (("ecart_a_la_surface_median_mm", "ecart median"),
                             ("rayon_exterieur_median_mm", "rayon exterieur median"),
                             ("rayon_arret_median_mm", "rayon d arret median")):
                if r_.get(cle) is not None:
                    ajoute(f"{nom} de {nom_c} de 135", r_[cle], dec135(r_[cle], 2), cesse.name)
            for x in c_.get("arrets", []):
                # ⚠ Seules les marches qui NE sont PAS sorties sont enregistrees arret par arret :
                # ce sont celles que le document tabule (§4). Enregistrer les vingt-cinq sorties
                # ferait crier « chiffre recalcule qui n'apparait nulle part » sur des nombres que
                # le document resume exprès, et une alerte permanente est une alerte qu'on cesse
                # de lire.
                if x.get("fin") == "plus rien a lire":
                    continue
                r0 = x["rayon_mm"]
                ajoute(f"rayon d arret {r0} de {nom_c} de 135", x["rayon_arret_mm"], dec135(x["rayon_arret_mm"], 2), cesse.name)
                if x.get("surface", {}).get("rayon_exterieur_mm") is not None:
                    ajoute(f"surface {r0} de {nom_c} de 135", x["surface"]["rayon_exterieur_mm"],
                           dec135(x["surface"]["rayon_exterieur_mm"], 2), cesse.name)
                if x.get("verdict", {}).get("ecart_a_la_surface_mm") is not None:
                    ajoute(f"ecart {r0} de {nom_c} de 135", x["verdict"]["ecart_a_la_surface_mm"],
                           dec135(x["verdict"]["ecart_a_la_surface_mm"], 2), cesse.name, signe=True)
        if d.get("secondes") is not None:
            ajoute("secondes de 135", d["secondes"], 1, cesse.name)

    # ⭐⭐⭐⭐ LA TRANCHE 134 : LES FEUILLES NON PARALLELES, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le virage d'une pile ne voyage jamais sans le virage REEL et sa fourchette : 14,72° seul
    # se lit comme un succes, a cote de [13,28 ; 14,54] il dit « juste au-dessus ».
    # (2) Et il ne voyage jamais sans le COSINUS des virages : tourner autant que le rouleau sans
    # deriver comme lui, c'est le cosinus qui le dit (−0,4624 contre −0,2061).
    pfnp = _source(racine, "une_pile_a_feuilles_non_paralleles.json")
    if pfnp.exists():
        d = json.loads(pfnp.read_text())

        def dec_(v, plafond):
            # ⚠ Les decimales sont celles que le PRODUCTEUR a ecrites, jamais un compte fixe : le
            # JSON porte 0.999 et non 0.9990, et exiger « 0,9990 » d'un document qui recopie
            # « 0,999 » ferait se contredire ce controle et `chiffres_sans_record`.
            s = repr(float(v))
            return min(plafond, len(s.split(".")[1]) if "." in s and "e" not in s else plafond)
        r_ = d.get("desaccord_reel", {})
        for cle, nom, dec in (("mediane", "desaccord reel de 134", 2), ("p25", "desaccord reel p25 de 134", 2),
                              ("p75", "desaccord reel p75 de 134", 2), ("p90", "desaccord reel p90 de 134", 2)):
            if r_.get(cle) is not None:
                ajoute(nom, r_[cle], dec, pfnp.name)
        if r_.get("n") is not None:
            ajoute("pas voyants du desaccord reel de 134", r_["n"], 0, pfnp.name)
        if r_.get("cos_virages_median") is not None:
            ajoute("cos reel de 134", r_["cos_virages_median"], 4, pfnp.name, signe=True)
        vr = r_.get("virage_par_pas", {})
        for cle, nom in (("mediane", "virage reel de 134"), ("p25", "virage reel p25 de 134"),
                         ("p75", "virage reel p75 de 134")):
            if vr.get(cle) is not None:
                ajoute(nom, vr[cle], 2, pfnp.name)
        c_ = d.get("controle_pile_plane", {})
        if c_.get("desaccord", {}).get("mediane") is not None:
            ajoute("desaccord de la pile plane de 134", c_["desaccord"]["mediane"], 2, pfnp.name)
        for cle, nom, dec in (("virage_median_deg", "virage de la pile plane de 134", 2),
                              ("rectitude_mediane", "rectitude de la pile plane de 134", 4)):
            if c_.get("marche", {}).get(cle) is not None:
                ajoute(nom, c_["marche"][cle], dec, pfnp.name)
        for x in d.get("par_longueur_donde", []):
            v_ = x.get("variante", "en_phase").replace("_", " ")
            ld = x["longueur_donde_um"]
            cal = x.get("calibration", {})
            for cle, nom, dec in (("amplitude_um", "amplitude", 3), ("inclinaison_max_deg", "inclinaison", 2),
                                  ("mediane_deg", "desaccord obtenu", 2)):
                if cal.get(cle) is not None:
                    ajoute(f"{nom} {v_} {ld} de 134", cal[cle], dec, pfnp.name)
            for m in x.get("marche", {}).get("par_memoire", []):
                lam = f"memoire {m['memoire']:.2f}"
                for cle, nom, dec, sg in (("virage_median_deg", "virage", 2, False),
                                          ("rectitude_mediane", "rectitude", 4, False),
                                          ("erreur_mediane_deg", "erreur", 3, False),
                                          ("desaccord_rencontre_median_deg", "desaccord rencontre", 2, False),
                                          ("taux_median", "taux", 4, False),
                                          ("cos_virages_median", "cos", 4, True)):
                    if m.get(cle) is not None:
                        ajoute(f"{nom} {v_} {ld} {lam} de 134", m[cle], dec_(m[cle], dec), pfnp.name,
                               signe=sg)
        if d.get("secondes") is not None:
            ajoute("secondes de 134", d["secondes"], 1, pfnp.name)

    # ⭐⭐⭐⭐ LA TRANCHE 133 : LE LECTEUR, LE COUT D'UN PAS, ET LE CAP COURU.
    # (1) Le facteur du lecteur ne voyage jamais sans « identiques au bit » : un lecteur plus
    # rapide qui rendrait un autre octet n'est pas plus rapide, il est faux.
    # (2) Le cout d'un pas de 131 ne voyage jamais sans celui de 133 ET sans la mention qu'il
    # est une borne haute : 144 s seul se lit comme un fait, a cote de 2,34 il dit que la
    # planification de 131 est perimee, et sans « borne haute » il surestime le rapport.
    # (3) Les deux verdicts du cap voyagent ensemble : « 15/16 plus droites » seul se lit comme
    # un succes, a cote de « 2/16 plus longues » il dit ce que le cap coute.
    lect = _source(racine, "le_lecteur_par_plage.json")
    if lect.exists():
        d = json.loads(lect.read_text())
        for x in d.get("lectures", []):
            ajoute(f"secondes a {x['fils']} fils de 133", x["secondes"], 3, lect.name)
            ajoute(f"points par seconde a {x['fils']} fils de 133", x["points_par_seconde"], 1,
                   lect.name)
        if d.get("facteur_du_plus_rapide") is not None:
            ajoute("facteur du lecteur de 133", d["facteur_du_plus_rapide"], 1, lect.name)
        c_ = d.get("concurrence", {})
        for cle, nom, dec in (("secondes_mur", "mur de la concurrence de 133", 3),
                              ("secondes_seule", "seule de la concurrence de 133", 3),
                              ("mur_sur_seule", "rapport de la concurrence de 133", 2)):
            if c_.get(cle) is not None:
                ajoute(nom, c_[cle], dec, lect.name)
    for nom_, fichier_ in (("133", "la_course_a_cap.json"), ("131", "la_re_course_large.json")):
        src = _source(racine, fichier_)
        if not src.exists():
            continue
        d = json.loads(src.read_text())
        r_ = d.get("resume", {})
        if d.get("secondes") is not None:
            ajoute(f"secondes de la course de {nom_}", d["secondes"], 1, src.name)
        for cle, nom, dec in (("secondes_par_pas", "secondes par pas", 2),
                              ("pas_marches_dans_cette_course", "pas marches", 0)):
            if r_.get(cle) is not None:
                ajoute(f"{nom} de {nom_}", r_[cle], dec, src.name)
    cmp_ = _source(racine, "un_cap_change_t_il_la_course.json")
    if cmp_.exists():
        d = json.loads(cmp_.read_text())
        v_ = d.get("verdict", {})
        if v_.get("decidable"):
            for cle, nom, dec in (("rectitude_mediane_sans_cap", "rectitude sans cap de 133", 4),
                                  ("rectitude_mediane_avec_cap", "rectitude avec cap de 133", 4),
                                  ("p_rectitude", "p de la rectitude de 133", 5),
                                  ("pas_voyants_median_sans_cap", "pas voyants sans cap de 133", 1),
                                  ("pas_voyants_median_avec_cap", "pas voyants avec cap de 133", 1),
                                  ("p_longueur", "p de la longueur de 133", 5),
                                  ("taux_sans_cap", "taux sans cap de 133", 4),
                                  ("taux_avec_cap", "taux avec cap de 133", 4)):
                if v_.get(cle) is not None:
                    ajoute(nom, v_[cle], dec, cmp_.name)
            for cle, nom in (("marches_plus_droites_avec_cap", "marches plus droites de 133"),
                             ("marches_plus_longues_avec_cap", "marches plus longues de 133"),
                             ("au_plafond_sans_cap", "au plafond sans cap de 133"),
                             ("au_plafond_avec_cap", "au plafond avec cap de 133"),
                             ("plus_rien_a_lire_sans_cap", "plus rien a lire sans cap de 133"),
                             ("plus_rien_a_lire_avec_cap", "plus rien a lire avec cap de 133"),
                             ("paires", "paires de 133")):
                if v_.get(cle) is not None:
                    ajoute(nom, v_[cle], 0, cmp_.name)
        k_ = d.get("cout", {})
        if k_.get("decidable") and k_.get("rapport") is not None:
            ajoute("rapport des couts de 133", k_["rapport"], 1, cmp_.name)
    der = _source(racine, "le_marcheur_derive_sur_la_course_a_cap.json")
    if der.exists():
        d = json.loads(der.read_text())
        g_ = d.get("le_virage_grandit_il", {})
        for cle, nom in (("virage_premier_tiers_deg", "virage du premier tiers avec cap de 133"),
                         ("virage_dernier_tiers_deg", "virage du dernier tiers avec cap de 133")):
            if g_.get(cle) is not None:
                ajoute(nom, g_[cle], 1, der.name)
        l_ = d.get("la_rectitude_decroit_elle_avec_la_longueur", {})
        for cle, nom, dec, signe in (("rho_a_longueur_egale", "rho a longueur egale de 133", 4, True),
                                     ("p_a_longueur_egale", "p a longueur egale de 133", 4, False)):
            if l_.get(cle) is not None:
                ajoute(nom, l_[cle], dec, der.name, signe=signe)
        w_ = d.get("temoin_les_virages_se_compensent", {})
        for cle, nom, dec in (("rectitude_reelle", "rectitude reelle du temoin de 133", 3),
                              ("rectitude_simulee", "rectitude simulee du temoin de 133", 3),
                              ("p_appariee", "p du temoin de 133", 5)):
            if w_.get(cle) is not None:
                ajoute(nom, w_[cle], dec, der.name)
        n_ = d.get("jusquou_le_net_progresse_t_il", {})
        for cle, nom, dec in (("k_du_maximum_median", "pas du maximum de net de 133", 0),
                              ("net_maximum_median_um", "net maximum de 133", 1),
                              ("net_au_plafond_median_um", "net au plafond de 133", 1)):
            if n_.get(cle) is not None:
                ajoute(nom, n_[cle], dec, der.name)

    # ⭐⭐⭐⭐ LA TRANCHE 131 : DOUBLER LES BANDES, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le compte de marches au plafond ne voyage JAMAIS sans celui des bandes. « 4 marches »
    # se lit comme un progres ; « 4 sur 16, contre 3 sur 8 » dit que le budget de bandes n'achete
    # pas ce qu'on croyait.
    # (2) Et le p du temoin ne voyage jamais sans la PROPORTION. Un p qui tombe de 0,375 a 0,194
    # se lit comme « la puissance arrivait » ; a cote de « 0,714 contre 0,714 », il dit que la
    # proportion n'a pas bouge, donc que l'effet lui-meme est plus faible.
    for nom_, fichier_ in (("131", "la_re_course_large.json"),):
        src = _source(racine, fichier_)
        if not src.exists():
            continue
        d = json.loads(src.read_text())
        r_ = d.get("resume", {})
        for cle, nom, dec in (("taux_de_confirmation_global", "taux global", 4),
                              ("part_au_plafond", "part au plafond", 2),
                              ("longueur_mediane_um", "longueur mediane", 1),
                              ("longueur_max_um", "longueur max", 1),
                              ("pas_parcourus_median", "pas medians", 1)):
            if r_.get(cle) is not None:
                ajoute(f"{nom} de {nom_}", r_[cle], dec, src.name)
        for cle, nom in (("marches", "marches"), ("plafond", "plafond"),
                         ("marches_au_plafond", "marches au plafond"),
                         ("sorties_du_volume", "sorties")):
            if r_.get(cle) is not None:
                v_ = r_[cle]
                out.append((f"{nom} de {nom_}", [f"**{v_}**", f"{v_}"], src.name))
        t_ = d.get("le_taux_baisse_avec_la_profondeur", {})
        for cle, nom, dec in (("taux_precoce", "taux precoce", 3),
                              ("taux_tardif", "taux tardif", 3),
                              ("p_sous_un_taux_constant", "p de profondeur", 4)):
            if t_.get(cle) is not None:
                ajoute(f"{nom} de {nom_}", t_[cle], dec, src.name)
        y_ = d.get("le_taux_suit_il_le_rayon", {})
        if y_.get("rho_de_spearman") is not None:
            ajoute(f"rho du rayon de {nom_}", y_["rho_de_spearman"], 3, src.name, signe=True)
        if y_.get("p") is not None:
            ajoute(f"p du rayon de {nom_}", y_["p"], 4, src.name)
        if d.get("secondes") is not None:
            ajoute(f"secondes de {nom_}", d["secondes"], 1, src.name)
        for L in d.get("lignes", []):
            c_ = (L.get("detail") or [{}])[0]
            if c_.get("longueur_um") is not None:
                ajoute(f"chemin au rayon {L.get('rayon_mm')} de {nom_}",
                       c_["longueur_um"], 1, src.name)

    # ⭐⭐⭐⭐ LA RE-COURSE DE `130` : le resume d'une traversee complete.
    rec = _source(racine, "la_re_course.json")
    if rec.exists():
        d = json.loads(rec.read_text())
        r_ = d.get("resume", {})
        for cle, nom, dec in (("taux_de_confirmation_global", "taux global de 130", 4),
                              ("part_au_plafond", "part au plafond de 130", 3),
                              ("longueur_mediane_um", "longueur mediane de 130", 1),
                              ("longueur_max_um", "longueur max de 130", 1)):
            if r_.get(cle) is not None:
                ajoute(nom, r_[cle], dec, rec.name)
        # ⚠ Le compte median de pas est un NOMBRE a une decimale, pas un compte entier : le
        # publier comme « **85.0** » le rendrait inappariable dans un document francais.
        if r_.get("pas_parcourus_median") is not None:
            ajoute("pas medians de 130", r_["pas_parcourus_median"], 1, rec.name)
        for cle, nom in (("marches", "marches de 130"), ("plafond", "plafond de 130"),
                         ("marches_au_plafond", "marches au plafond de 130"),
                         ("sorties_du_volume", "sorties de 130")):
            if r_.get(cle) is not None:
                v_ = r_[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], rec.name))
        t_ = d.get("le_taux_baisse_avec_la_profondeur", {})
        for cle, nom, dec in (("taux_precoce", "taux precoce de 130", 3),
                              ("taux_tardif", "taux tardif de 130", 3),
                              ("p_sous_un_taux_constant", "p de profondeur de 130", 4)):
            if t_.get(cle) is not None:
                ajoute(nom, t_[cle], dec, rec.name)
        y_ = d.get("le_taux_suit_il_le_rayon", {})
        if y_.get("rho_de_spearman") is not None:
            ajoute("rho du rayon de 130", y_["rho_de_spearman"], 4, rec.name, signe=True)
        if y_.get("p") is not None:
            ajoute("p du rayon de 130", y_["p"], 4, rec.name)
        for L in d.get("lignes", []):
            c_ = (L.get("detail") or [{}])[0]
            if c_.get("longueur_um") is not None:
                ajoute(f"chemin au rayon {L.get('rayon_mm')} de 130",
                       c_["longueur_um"], 1, rec.name)

    # ⭐⭐⭐⭐ LA TRANCHE 119 : LE MARCHEUR NE DERIVE PAS, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) La rectitude reelle ne voyage JAMAIS sans celle du tirage de memes virages. Seule,
    # « 0,928 » se lit comme « la marche est droite », ce qu'une marche qui ne vire pas obtient
    # aussi ; avec « 0,811 sous un tirage de memes virages », elle se lit pour ce qu'elle est,
    # une compensation.
    # (2) Les deux moities ne voyagent jamais sans leur p apparie : « 0,944 puis 0,942 » sans
    # « p 0,8906 » serait un ecart lu comme un effet, et c'est exactement l'inverse du resultat.
    mdt = _source(racine, "le_marcheur_derive_t_il.json")
    if mdt.exists():
        d = json.loads(mdt.read_text())
        g = d.get("la_trajectoire_est_elle_celle_de_la_course", {})
        for cle, nom, dec in (("ecart_max_um", "ecart de reconstruction de 119", 1),
                              ("tolerance_um", "tolerance de 119", 1)):
            if g.get(cle) is not None:
                ajoute(nom, g[cle], dec, mdt.name, unites=("µm",))
        deg = d.get("la_marche_se_degrade_t_elle", {})
        if deg.get("marches") is not None:
            v_ = deg["marches"]
            out.append(("marches de 119", [f"**{v_}**", f"{v_}"], mdt.name))
        for cle, nom, dec in (("rectitude_premiere_moitie", "rectitude 1re moitie de 119", 3),
                              ("rectitude_seconde_moitie", "rectitude 2e moitie de 119", 3),
                              ("p_appariee", "p des deux moities de 119", 4)):
            if deg.get(cle) is not None:
                ajoute(nom, deg[cle], dec, mdt.name)
        for cle, nom in (("angle_entre_les_deux_moities_deg", "angle des deux moities de 119"),
                         ("angle_max_deg", "angle max de 119")):
            if deg.get(cle) is not None:
                ajoute(nom, deg[cle], 1, mdt.name, unites=("°",))
        vg = d.get("le_virage_grandit_il", {})
        for cle, nom in (("virage_premier_tiers_deg", "virage du 1er tiers de 119"),
                         ("virage_dernier_tiers_deg", "virage du dernier tiers de 119")):
            if vg.get(cle) is not None:
                ajoute(nom, vg[cle], 1, mdt.name, unites=("°",))
        if vg.get("p_appariee") is not None:
            ajoute("p du virage de 119", vg["p_appariee"], 4, mdt.name)
        s_ = d.get("le_virage_a_t_il_un_sens", {})
        for cle, nom, signe in (("rotation_cumulee_mediane_deg", "rotation mediane de 119", True),
                                ("rotation_min_deg", "rotation min de 119", True),
                                ("rotation_max_deg", "rotation max de 119", True)):
            if s_.get(cle) is not None:
                ajoute(nom, s_[cle], 1, mdt.name, signe=signe, unites=("°",))
        if s_.get("p_contre_zero") is not None:
            ajoute("p de la rotation de 119", s_["p_contre_zero"], 4, mdt.name)
        w_ = d.get("temoin_les_virages_se_compensent", {})
        for cle, nom, dec in (("rectitude_reelle", "rectitude reelle de 119", 3),
                              ("rectitude_simulee", "rectitude simulee de 119", 3),
                              ("p_appariee", "p du temoin de 119", 5)):
            if w_.get(cle) is not None:
                ajoute(nom, w_[cle], dec, mdt.name)
        for cle, nom in (("marches_ou_le_reel_est_plus_droit", "marches plus droites de 119"),
                         ("tirages", "tirages du temoin de 119")):
            if w_.get(cle) is not None:
                v_ = w_[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], mdt.name))
        a_ = d.get("langle_au_radial_initial", {})
        for cle, nom in (("angle_premier_tiers_deg", "angle radial du 1er tiers de 119"),
                         ("angle_dernier_tiers_deg", "angle radial du dernier tiers de 119")):
            if a_.get(cle) is not None:
                ajoute(nom, a_[cle], 1, mdt.name, unites=("°",))
        if a_.get("p_appariee") is not None:
            ajoute("p de l'angle radial de 119", a_["p_appariee"], 4, mdt.name)

    # ⭐⭐⭐⭐ LA TRANCHE 118 : LA FENETRE EXCLUT DE VRAIS PAS, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Un espacement deduit ne voyage JAMAIS sans le bout de fenetre qu'il conteste : « 80,7 µm »
    # seul est une longueur, « 80,7 contre une borne a 86,5 » est un refus d'instrument.
    # (2) Et il ne voyage jamais sans le rapport apparie du controle : sans « 1,015 sur 287 pas
    # libres », rien ne dit que la fraction franchie veut dire quelque chose, donc les deux bouts
    # seraient deux nombres tires d'un estimateur non verifie.
    fgl = _source(racine, "la_fenetre_est_globale_lespacement_est_local.json")
    if fgl.exists():
        d = json.loads(fgl.read_text())
        c = d.get("le_deduit_saccorde_t_il_au_choisi", {})
        if c.get("pas_libres_deductibles") is not None:
            v_ = c["pas_libres_deductibles"]
            out.append(("pas libres deductibles de 118", [f"**{v_}**", f"{v_}"], fgl.name))
        for cle, nom, dec in (("rapport_median", "rapport median de 118", 3),
                              ("rapport_q1", "rapport q1 de 118", 3),
                              ("rapport_q3", "rapport q3 de 118", 3)):
            if c.get(cle) is not None:
                ajoute(nom, c[cle], dec, fgl.name)
        if c.get("rho") is not None:
            ajoute("rho du controle de 118", c["rho"], 4, fgl.name, signe=True)
        e = d.get("ce_que_la_fenetre_exclut", {})
        for cle, nom in (("bout_court_um", "bout court de 118"),
                         ("bout_long_um", "bout long de 118")):
            if e.get(cle) is not None:
                ajoute(nom, e[cle], 1, fgl.name, unites=("µm",))
        for bout in ("court", "long"):
            b = e.get(f"bout_{bout}", {})
            if not b.get("decidable"):
                continue
            if b.get("pas_deductibles") is not None:
                v_ = b["pas_deductibles"]
                out.append((f"pas deductibles du bout {bout} de 118",
                            [f"**{v_}**", f"{v_}"], fgl.name))
            for cle, suffixe in (("espacement_median_um", ""), ("q1_um", " (q1)"),
                                 ("q3_um", " (q3)")):
                if b.get(cle) is not None:
                    ajoute(f"espacement du bout {bout} de 118{suffixe}", b[cle], 1, fgl.name,
                           unites=("µm",))
        r_ = d.get("la_variation_est_elle_radiale", {})
        if r_.get("marches") is not None:
            v_ = r_["marches"]
            out.append(("marches exploitables de 118", [f"**{v_}**", f"{v_}"], fgl.name))
        if r_.get("rho_espacement_rayon") is not None:
            ajoute("rho radial de 118", r_["rho_espacement_rayon"], 4, fgl.name, signe=True)
        for cle, nom, dec in (("p", "p radial de 118", 4),
                              ("p_court_contre_long", "p court contre long de 118", 4)):
            if r_.get(cle) is not None:
                ajoute(nom, r_[cle], dec, fgl.name)
        for cle, nom in (("rayon_median_bout_court_mm", "rayon median du bout court de 118"),
                         ("rayon_median_bout_long_mm", "rayon median du bout long de 118")):
            if r_.get(cle) is not None:
                ajoute(nom, r_[cle], 2, fgl.name, unites=("mm",))

    # ⭐⭐⭐⭐ LA TRANCHE 117 : CE QUI REFUSE UN PAS VOYANT, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le « 0,9122 » ne voyage JAMAIS sans le compte de pas refuses par la MATIERE. Seul, il se
    # lit comme le taux du marcheur ; avec « 28 sur 382 », il se lit pour ce qu'il est, une borne
    # superieure qu'une re-course seule peut confirmer.
    # (2) Les 62 refus en butee seule ne voyagent jamais sans les deux bouts de la fenetre : sans
    # « 43 au bout court, 20 au bout long, 0 entre les deux », « en butee » n'est qu'un drapeau,
    # et rien ne dit que c'est une limite d'instrument.
    qrf = _source(racine, "qui_refuse_un_pas_voyant.json")
    if qrf.exists():
        d = json.loads(qrf.read_text())
        q = d.get("qui_refuse", {})
        for cle, nom in (("voyants", "pas voyants de 117"),
                         ("voyants_confirmes", "voyants confirmes de 117"),
                         ("voyants_refuses", "voyants refuses de 117"),
                         ("butee_seule", "butee seule de 117"),
                         ("refuses_par_la_matiere_seule", "refuses par la matiere de 117")):
            if q.get(cle) is not None:
                v_ = q[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], qrf.name))
        if q.get("taux_au_plus_si_la_fenetre_ne_bornait_pas") is not None:
            ajoute("taux au plus de 117", q["taux_au_plus_si_la_fenetre_ne_bornait_pas"], 4,
                   qrf.name)
        g = d.get("le_predicat_est_il_bien_reconstruit", {})
        if g.get("pas") is not None:
            out.append(("pas du predicat de 117", [f"**{g['pas']}**", f"{g['pas']}"], qrf.name))
        f_ = d.get("les_bouts_de_la_fenetre", {})
        for cle, nom in (("pas_en_butee", "pas en butee de 117"),
                         ("au_bout_court", "au bout court de 117"),
                         ("au_bout_long", "au bout long de 117"),
                         ("entre_les_deux", "entre les deux de 117")):
            if f_.get(cle) is not None:
                v_ = f_[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], qrf.name))
        for cle, nom in (("bout_court_um", "bout court de 117"),
                         ("bout_long_um", "bout long de 117"),
                         ("pas_nominal_um", "pas nominal de 117")):
            if f_.get(cle) is not None:
                ajoute(nom, f_[cle], 1, qrf.name, unites=("µm",))
        prof = d.get("le_taux_baisse_t_il_chez_les_voyants", {})
        for bloc_, nom in (("sur_les_voyants", "profondeur voyante de 117"),
                           ("sur_tous_les_pas", "profondeur totale de 117")):
            b = prof.get(bloc_, {})
            for cle, suffixe, dec in (("taux_precoce", " (precoce)", 2),
                                      ("taux_tardif", " (tardif)", 2),
                                      ("p_sous_un_taux_constant", " (p)", 4)):
                if b.get(cle) is not None:
                    ajoute(nom + suffixe, b[cle], dec, qrf.name)

    # ⭐⭐⭐⭐ LA TRANCHE 116 : LE MARCHEUR AVAIT SON ARRET, ET TROIS APPARIEMENTS L'IMPOSENT.
    # (1) Le « 0 retour de vue » ne voyage JAMAIS sans la mediane sous permutation. Seul, zero se
    # lit comme « on n'a rien trouve » ; avec « 7 sous permutation », il se lit pour ce qu'il est,
    # un ecart extreme. C'est la meme forme que le rho de 115 : le fait est l'ECART, pas la valeur.
    # (2) La portee mesuree ne voyage jamais sans le compte de marches ENCORE CENSUREES. Seule,
    # « 579,5 um » se lit comme la portee du marcheur, alors que dix-sept marches n'ont pas
    # d'arret du tout et restent une borne inferieure.
    # (3) Les huit plages ne voyagent jamais sans les deux d'une frontiere : « 8 » ne veut rien
    # dire sans ce qu'une frontiere aurait rendu.
    cec = _source(racine, "la_cecite_est_elle_absorbante.json")
    if cec.exists():
        d = json.loads(cec.read_text())
        a = d.get("la_cecite_est_elle_absorbante", {})
        for cle, nom in (("marches_avec_un_pas_aveugle", "marches avec un pas aveugle de 116"),
                         ("marches_ou_la_vue_revient", "retours de vue de 116"),
                         ("marches_avec_occasion", "marches avec occasion de 116")):
            if a.get(cle) is not None:
                v_ = a[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], cec.name))
        for cle, nom in (("aveugle_puis_aveugle", "transitions aveugle-aveugle de 116"),
                         ("aveugle_puis_voyant", "transitions aveugle-voyant de 116"),
                         ("voyant_puis_aveugle", "transitions voyant-aveugle de 116"),
                         ("voyant_puis_voyant", "transitions voyant-voyant de 116")):
            if a.get("transitions", {}).get(cle) is not None:
                v_ = a["transitions"][cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], cec.name))
        w = d.get("temoin", {})
        for cle, nom in (("retours_medians_sous_permutation", "retours medians de 116"),
                         ("retours_min_sous_permutation", "retours min de 116"),
                         ("tirages", "tirages du temoin de 116")):
            if w.get(cle) is not None:
                v_ = int(w[cle])
                out.append((nom, [f"**{v_}**", f"{v_}"], cec.name))
        po = d.get("la_portee_quand_on_sarrete_a_laveugle", {})
        for cle, nom in (("marches_qui_sarretent_pour_une_raison", "marches arretees de 116"),
                         ("marches_encore_censurees", "marches censurees de 116"),
                         ("marches_arretees_des_le_premier_pas", "marches nulles de 116")):
            if po.get(cle) is not None:
                v_ = po[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], cec.name))
        for bloc_, nom in (("portee_mesuree", "portee mesuree de 116"),
                           ("portee_encore_censuree", "portee censuree de 116")):
            b = po.get(bloc_, {})
            if b.get("longueur_mediane_um") is not None:
                ajoute(nom, b["longueur_mediane_um"], 1, cec.name, unites=("µm",))
            if b.get("longueur_max_um") is not None:
                ajoute(nom + " (max)", b["longueur_max_um"], 1, cec.name, unites=("µm",))
        fr_ = d.get("le_vide_est_il_une_frontiere", {})
        for cle, nom in (("plages_observees", "plages de 116"),
                         ("plages_sous_une_frontiere", "plages sous frontiere de 116"),
                         ("marches_aveugles", "marches aveugles de 116")):
            if fr_.get(cle) is not None:
                v_ = int(fr_[cle])
                out.append((nom, [f"**{v_}**", f"{v_}"], cec.name))
        if fr_.get("plages_medianes_sous_permutation") is not None:
            v_ = int(fr_["plages_medianes_sous_permutation"])
            out.append(("plages medianes de 116", [f"**{v_}**", f"{v_}"], cec.name))
        if fr_.get("part_des_permutations_aussi_peu_de_plages") is not None:
            ajoute("p des plages de 116", fr_["part_des_permutations_aussi_peu_de_plages"],
                   4, cec.name)
        for cle, nom in (("rayon_de_la_premiere_aveugle_mm", "rayon de la premiere aveugle de 116"),
                         ("rayon_de_la_derniere_voyante_mm", "rayon de la derniere voyante de 116")):
            if fr_.get(cle) is not None:
                ajoute(nom, fr_[cle], 2, cec.name, unites=("mm",))

    # ⭐⭐⭐⭐ LA TRANCHE 115 : LE RAYON N'EST PAS LA CAUSE, ET DEUX APPARIEMENTS L'IMPOSENT.
    # (1) Le rho des VOYANTES ne voyage jamais sans celui de TOUTES : « -0,19, p 0,46 » seul se
    # lit comme « on n'a rien trouve », alors que le resultat est qu'un -0,72 tres significatif
    # DISPARAIT quand on retire les marches qui n'ont rien lu. C'est l'ecart qui est le fait.
    # (2) Le taux voyant ne voyage jamais sans le compte de pas aveugles : « 0,7618 » seul se lit
    # comme le taux du marcheur, alors que c'est le taux sur les deux tiers ou il lit.
    cpt2 = _source(racine, "ce_qui_porte_le_taux.json")
    if cpt2.exists():
        d = json.loads(cpt2.read_text())
        o = d.get("le_vide_est_il_declare_oriente", {})
        for cle, nom in (("pas", "pas relus par 115"),
                         ("pas_aveugles", "pas aveugles de 115"),
                         ("aveugles_confirmes", "aveugles confirmes de 115"),
                         ("voyants_confirmes", "voyants confirmes de 115"),
                         ("aveugles_declares_orientes", "aveugles declares orientes de 115")):
            if o.get(cle) is not None:
                v_ = o[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], cpt2.name))
        if o.get("taux_voyant") is not None:
            ajoute("taux voyant de 115", o["taux_voyant"], 4, cpt2.name)
        if o.get("part_aveugle") is not None:
            ajoute("part aveugle de 115", o["part_aveugle"] * 100.0, 1, cpt2.name, unites=("%",))
        w = d.get("le_rayon_survit_il_aux_marches_voyantes", {})
        for cle, nom in (("marches_voyantes", "marches voyantes de 115"),
                         ("marches", "marches relues par 115")):
            if w.get(cle) is not None:
                v_ = w[cle]
                out.append((nom, [f"**{v_}**", f"{v_}"], cpt2.name))
        for cle, nom, dec in (("rho_sur_toutes", "rho sur toutes de 115", 4),
                              ("rho_sur_les_voyantes", "rho sur les voyantes de 115", 4)):
            if w.get(cle) is not None:
                ajoute(nom, w[cle], dec, cpt2.name, signe=True)
        for cle, nom, dec in (("p_sur_les_voyantes", "p des voyantes de 115", 4),
                              ("taux_median_voyantes_interieur", "taux median interieur de 115", 3),
                              ("taux_median_voyantes_exterieur", "taux median exterieur de 115", 3),
                              ("p_interieur_contre_exterieur", "p interieur contre exterieur de 115", 4)):
            if w.get(cle) is not None:
                ajoute(nom, w[cle], dec, cpt2.name)
        if d.get("marches_aveugles_des_le_depart") is not None:
            v_ = d["marches_aveugles_des_le_depart"]
            out.append(("marches aveugles des le depart de 115", [f"**{v_}**", f"{v_}"], cpt2.name))

    # ⭐⭐⭐ LA TRANCHE 113 : LE PLAFOND EST ENCORE LA MESURE, ET DEUX APPARIEMENTS LE DISENT.
    # (1) La longueur mediane ne voyage JAMAIS sans la part au plafond. Seule, « 3 966 um » se
    # lit comme une portee mesuree ; avec « 28 marches sur 28 au plafond », elle se lit pour ce
    # qu'elle est — une BORNE INFERIEURE, et la borne du reglage, pas celle de la matiere.
    # C'est exactement la faute que 107 a payee en publiant 1 250 um sous un plafond de six.
    # (2) L'ecart precoce/tardif ne voyage jamais sans son p : un ecart de -0,06 sans son
    # 0,3253 se lit comme une baisse, alors que le nul n'est pas rejete.
    jus = _source(racine, "jusquou_va_t_il_si_on_le_laisse.json")
    if jus.exists():
        d = json.loads(jus.read_text())
        r = d.get("resume", {})
        for cle, nom, dec in (("marches", "marches de 113", 0),
                              ("plafond", "plafond de 113", 0),
                              ("marches_au_plafond", "marches de 113 au plafond", 0),
                              ("sorties_du_volume", "sorties de volume de 113", 0),
                              ("pas_confirmes_max", "run maximum de 113", 0)):
            if r.get(cle) is not None:
                v = r[cle]
                out.append((nom, [f"**{v}**", f"{v}"], jus.name))
        for cle, nom, dec in (("longueur_mediane_um", "longueur mediane de 113", 1),
                              ("longueur_max_um", "longueur maximum de 113", 1),
                              ("taux_de_confirmation_global", "taux de confirmation de 113", 4)):
            if r.get(cle) is not None:
                ajoute(nom, r[cle], dec, jus.name)
        b = d.get("le_taux_baisse_avec_la_profondeur", {})
        for cle, nom, dec in (("taux_precoce", "taux precoce de 113", 2),
                              ("taux_tardif", "taux tardif de 113", 2),
                              ("p_sous_un_taux_constant", "p du taux constant de 113", 4)):
            if b.get(cle) is not None:
                ajoute(nom, b[cle], dec, jus.name)
        if b.get("ecart") is not None:
            ajoute("ecart precoce-tardif de 113", b["ecart"], 3, jus.name, signe=True)
        # ⚠⚠ Les VINGT taux par pas ne sont PAS enregistres, et c'est une decision. Ils vivent
        # dans la figure, pas dans un document — les enregistrer creerait vingt obligations de
        # citation pour une courbe qu'aucune prose n'epellera jamais valeur par valeur, donc
        # vingt echecs permanents. Une garde rouge en permanence cesse d'etre lue (`57` §3).
        # Ce qui est enregistre est ce qu'un document AFFIRME : les deux bouts et le p.
        # ⭐⭐⭐ LE RESULTAT DE 113, ET SON APPARIEMENT OBLIGATOIRE. Le rho ne voyage JAMAIS sans
        # son p ni sans l'etendue de rayons qui le porte : « -0,719 » seul se lit comme une loi
        # du rouleau alors que c'est une correlation sur vingt-huit bandes de UN objet. Et
        # l'indice de dispersion ne voyage jamais sans le taux global qu'il corrige — publier
        # 0,5196 sans lui, c'est publier la moyenne de deux populations comme si c'en etait une.
        dsp = d.get("le_taux_depend_il_de_la_marche", {})
        for cle, nom, dec in (("taux_min", "taux minimum par marche de 113", 2),
                              ("taux_max", "taux maximum par marche de 113", 2),
                              ("indice_de_dispersion", "indice de dispersion de 113", 3),
                              ("khi2", "khi2 de 113", 2),
                              ("taux_premiere_moitie", "taux de la premiere moitie de 113", 4),
                              ("taux_seconde_moitie", "taux de la seconde moitie de 113", 4)):
            if dsp.get(cle) is not None:
                ajoute(nom, dsp[cle], dec, jus.name)
        ry = d.get("le_taux_suit_il_le_rayon", {})
        if ry.get("rho_de_spearman") is not None:
            ajoute("rho du taux et du rayon de 113", ry["rho_de_spearman"], 4, jus.name,
                   signe=True)
        for cle, nom, dec in (("rayon_min_mm", "rayon minimum de 113", 2),
                              ("rayon_max_mm", "rayon maximum de 113", 2)):
            if ry.get(cle) is not None:
                ajoute(nom, ry[cle], dec, jus.name, unites=("mm",))

    # ⭐⭐⭐ UN PAS MANQUE N'EST PAS UNE CHUTE (`109`), ET TROIS APPARIEMENTS SONT OBLIGATOIRES.
    # (1) La mediane des pas CONFIRMES ne voyage jamais sans celle du RUN : publier la premiere
    # seule remplacerait un nombre trompeur par un autre, et c'est leur ECART qui est le resultat.
    # (2) Le verdict du groupement ne voyage jamais sans le TAUX de son jeu, parce que le nul est
    # conservateur — « non groupe » a taux moyen veut surtout dire « pas de puissance ».
    # (3) Et la survie « si un manque est une chute » ne voyage jamais sans sa jumelle : un seul
    # des deux nombres se lit comme un fait de la matiere alors qu'il depend d'une hypothese.
    chu = _source(racine, "un_pas_manque_nest_pas_une_chute.json")
    if chu.exists():
        d = json.loads(chu.read_text())
        for cle, nom in (("marches", "marches lues par 109"),
                         ("portee_publiee_par_107", "portee publiee par 107")):
            if cle in d and d[cle] is not None:
                val = d[cle]
                txt = f"{val}".replace(".", ",")
                out.append((nom, [f"**{txt}**", txt, f"{val}"], chu.name))
        j = d.get("ce_que_la_lecture_consecutive_jette", {})
        for cle, nom in (("confirment_presque_tout", "marches presque completes"),
                         ("... et sont creditees de zero ou un", "presque completes jetees"),
                         ("confirmes_median", "mediane des pas confirmes"),
                         ("run_median", "mediane du run")):
            if cle not in j or j[cle] is None:
                continue
            val = j[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], chu.name))
        for quoi, serie in (("confirmes", j.get("distribution_des_confirmes") or []),
                            ("run", j.get("distribution_du_run") or [])):
            for k, val in enumerate(serie):
                out.append((f"marches a {k} {quoi}", [f"**{val}**", f"{val}"], chu.name))
        pa = d.get("paraphrase", {})
        for cle, nom in (("taux_de_confirmation", "taux de confirmation global"),
                         ("run_moyen_observe", "run moyen observe"),
                         ("run_moyen_si_les_manques_sont_independants",
                          "run moyen sous lindependance"),
                         ("ecart_en_pas", "ecart du run en pas")):
            if cle not in pa or pa[cle] is None:
                continue
            val = pa[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if cle.startswith("ecart"):
                formes += [f"**{val:+.3f}**".replace(".", ","), f"{val:+.3f}".replace(".", ",")]
            out.append((nom, formes, chu.name))
        jeux = [("toutes", d.get("groupement", {}), d.get("paraphrase", {}))]
        for nom_m in ("mode_haut", "mode_bas"):
            b = (d.get("par_mode") or {}).get(nom_m) or {}
            if b.get("marches"):
                jeux.append((nom_m, b.get("groupement", {}), b))
        for nom_j, g, ctx in jeux:
            for cle, nom in (("rafale_moyenne_observee", "rafale observee"),
                             ("rafale_moyenne_sous_lindependance", "rafale sous lindependance"),
                             ("p_les_manques_sont_groupes", "p du groupement"),
                             ("p95_du_nul", "p95 du nul du groupement")):
                if cle not in g or g[cle] is None:
                    continue
                val = g[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {nom_j}", [f"**{txt}**", txt, f"{val}"], chu.name))
            for cle, nom in (("taux_de_confirmation", "taux du jeu"),
                             ("confirmes_median", "confirmes median du jeu"),
                             ("run_median", "run median du jeu"),
                             ("marches", "marches du jeu")):
                if cle not in ctx or ctx[cle] is None:
                    continue
                val = ctx[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {nom_j}", [f"**{txt}**", txt, f"{val}"], chu.name))
        nc = d.get("nul_a_taux_commun", {})
        if "p_avec_un_nul_a_taux_commun" in nc:
            val = nc["p_avec_un_nul_a_taux_commun"]
            txt = f"{val}".replace(".", ",")
            out.append(("p du groupement a taux commun",
                        [f"**{txt}**", txt, f"{val}"], chu.name))
        c = d.get("un_manque_coute_t_il_des_feuilles", {})
        for cle, nom in (("marches_completes", "marches entierement confirmees"),
                         ("marches_avec_manque", "marches avec manque"),
                         ("feuilles_par_pas_des_completes", "feuilles par pas des completes"),
                         ("feuilles_par_pas_des_manquantes", "feuilles par pas des manquantes"),
                         ("ecart_a_un_des_completes", "ecart a un des completes"),
                         ("ecart_a_un_des_manquantes", "ecart a un des manquantes"),
                         ("difference_des_ecarts", "difference des ecarts a un"),
                         ("p_bilaterale", "p de la difference des ecarts"),
                         ("le_depassement_des_completes", "depassement des completes")):
            if cle not in c or c[cle] is None:
                continue
            val = c[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if isinstance(val, float) and cle in ("difference_des_ecarts",
                                                  "le_depassement_des_completes"):
                formes += [f"**{val:+.3f}**".replace(".", ","),
                           f"{val:+.3f}".replace(".", ",")]
            out.append((nom, formes, chu.name))
        for cle, titre in (("survie", "toutes"), ("survie_du_mode_haut", "mode haut")):
            sv = d.get(cle) or {}
            for k2, nom in (("taux_de_confirmation", "taux de la survie"),
                            ("pas_enchaines", "pas enchaines"),
                            ("manques_attendus_si_un_manque_est_un_manque",
                             "manques attendus")):
                if k2 not in sv or sv[k2] is None:
                    continue
                val = sv[k2]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {titre}", [f"**{txt}**", txt, f"{val}"], chu.name))
            if "survie_si_un_manque_est_une_chute" in sv:
                val = float(sv["survie_si_un_manque_est_une_chute"])
                # ⚠ Le depot ecrit ses decimales avec une VIRGULE ; sans cette forme, un
                # chiffre correctement publie serait compte absent.
                brut = f"{val:.2e}"
                out.append((f"survie si chute {titre}",
                            [f"**{brut}**", brut,
                             f"**{brut.replace('.', ',')}**", brut.replace(".", ","),
                             f"**{brut.replace('e-0', 'e-')}**", brut.replace("e-0", "e-")],
                            chu.name))

    # ⭐⭐⭐ CE QUI SEPARE LES DEUX POPULATIONS (`108`), ET TROIS APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Une FORCE ne voyage jamais sans son SENS : « le score separe » se lit comme un critere
    # utilisable, et le temoin negatif prouve qu'un seuil de score du TRAJET ecarterait le bon
    # mode. (2) Une p BRUTE ne voyage jamais sans sa p CORRIGEE, parce qu'un test par candidat
    # sans correction declare un gagnant sur du bruit pur quatre fois sur dix. (3) Et le taux
    # juste hors echantillon ne voyage jamais sans le NIVEAU DE CHANCE MESURE : le comparer au
    # taux du mode majoritaire lui offrirait l'optimisme residuel de la validation.
    sep = _source(racine, "ce_qui_separe_les_deux_populations.json")
    if sep.exists():
        d = json.loads(sep.read_text())
        e = d.get("ensemble", {})
        for cle, nom in (("trajets_lisibles", "trajets lisibles de 108"),):
            if cle in d:
                val = d[cle]
                out.append((nom, [f"**{val}**", f"{val}"], sep.name))
        for cle, nom in (("mode_haut", "trajets du mode haut de 108"),
                         ("mode_bas", "trajets du mode bas de 108"),
                         ("candidats_declares", "candidats declares de 108")):
            if cle in e:
                val = e[cle]
                out.append((nom, [f"**{val}**", f"{val}"], sep.name))
        v_ = d.get("vide_entre_les_modes", {})
        for cle, nom in (("dernier_du_mode_bas", "dernier trajet du mode bas"),
                         ("premier_du_mode_haut", "premier trajet du mode haut"),
                         ("vide_au_seuil", "vide au seuil des modes"),
                         ("seuil_feuilles_par_pas", "seuil en feuilles par pas")):
            if cle not in v_ or v_[cle] is None:
                continue
            val = v_[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], sep.name))
        fg = d.get("faux_gagnants_sans_correction", {})
        if "part_de_faux_gagnants" in fg:
            val = fg["part_de_faux_gagnants"]
            pc = f"{100 * val:.1f}".replace(".", ",")
            out.append(("part de faux gagnants sans correction",
                        [f"**{pc} %**", f"{pc} %", f"{pc}%",
                         f"**{100 * val:.0f} %**", f"{100 * val:.0f} %"], sep.name))
        n_ = e.get("nul", {})
        for cle, nom in (("force_max_du_nul_p95", "95e centile de la plus grande force"),
                         ("tirages", "tirages de la permutation de 108")):
            if cle not in n_:
                continue
            val = n_[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], sep.name))
        for x in e.get("par_candidat", []):
            if not x.get("decidable"):
                continue
            txt = f"{x['force']}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{x['force']}"]
            for n_dec in (2, 3):
                q = f"{x['force']:.{n_dec}f}".replace(".", ",")
                formes += [f"**{q}**", q]
            out.append((f"force de {x['cle']}", formes, sep.name))
            if "p_corrigee" in x:
                q = f"{x['p_corrigee']}".replace(".", ",")
                formes = [f"**{q}**", q, f"{x['p_corrigee']}"]
                for n_dec in (3, 4):
                    r = f"{x['p_corrigee']:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{r}**", r]
                out.append((f"p corrigee de {x['cle']}", formes, sep.name))
            for cote in ("mediane_mode_haut", "mediane_mode_bas"):
                if x.get(cote) is None:
                    continue
                val = x[cote]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                for n_dec in (1, 2, 3):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                out.append((f"{cote} de {x['cle']}", formes, sep.name))
        c_ = e.get("cout_dun_seuil", {})
        for cle, nom in (("seuil", "seuil sur le score du balayage"),
                         ("bonnes_marches_jetees", "bonnes marches jetees"),
                         ("bonnes_marches", "bonnes marches de 108"),
                         ("mauvaises_marches_gardees", "mauvaises marches gardees"),
                         ("mauvaises_marches", "mauvaises marches de 108")):
            if cle not in c_:
                continue
            val = c_[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], sep.name))
        for cle, nom in (("part_juste_hors_echantillon", "part juste hors echantillon"),
                         ("niveau_de_chance_mesure", "niveau de chance mesure"),
                         ("part_juste_du_mode_majoritaire", "part juste du mode majoritaire")):
            if cle not in c_:
                continue
            val = c_[cle]
            pc = f"{100 * val:.1f}".replace(".", ",")
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{pc} %**", f"{pc} %", f"{pc}%",
                              f"**{txt}**", txt, f"{val}"], sep.name))
        h_ = e.get("ce_que_le_hasard_obtient", {})
        for cle, nom in (("part_sous_le_hasard", "part des tirages sous le hasard"),):
            if cle not in h_:
                continue
            val = h_[cle]
            pc = f"{100 * val:.1f}".replace(".", ",")
            out.append((nom, [f"**{pc} %**", f"{pc} %", f"{pc}%"], sep.name))
        ap = d.get("apres_combien_de_pas", {})
        for cle, nom in (("force_au_premier_pas", "force au premier pas"),
                         ("p_corrigee_au_premier_pas", "p corrigee au premier pas")):
            if cle not in ap or ap[cle] is None:
                continue
            val = ap[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            for n_dec in (3, 4):
                q = f"{val:.{n_dec}f}".replace(".", ",")
                formes += [f"**{q}**", q]
            out.append((nom, formes, sep.name))
        for x in ap.get("par_longueur", []):
            for cle, nom in (("force", "force apres"), ("p_corrigee", "p corrigee apres")):
                val = x[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                for n_dec in (3, 4):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                out.append((f"{nom} {x['pas_vus']} pas", formes, sep.name))
            lo = (x.get("cout") or {}).get("part_juste_hors_echantillon")
            if lo is not None:
                txt = f"{lo}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{lo}"]
                for n_dec in (3,):
                    q = f"{lo:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                out.append((f"juste hors echantillon apres {x['pas_vus']} pas", formes,
                            sep.name))
        cm = d.get("combien_de_marches_pour_decider", {})
        for cle, nom in (("force_observee", "force observee du prix"),
                         ("trajets_pour_quatre_chances_sur_cinq",
                          "trajets pour quatre chances sur cinq")):
            if cle not in cm or cm[cle] is None:
                continue
            val = cm[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], sep.name))
        for x in cm.get("par_effectif", []):
            for cle, nom in (("force_critique", "force critique a"),
                             ("part_ou_le_meilleur_est_retenu", "meilleur retenu a"),
                             ("part_ou_un_candidat_est_retenu", "un candidat retenu a")):
                val = x[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                for n_dec in (3, 4):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                out.append((f"{nom} {x['trajets']} trajets", formes, sep.name))
        c2 = cm.get("course_qui_deciderait", {})
        for cle, nom in (("etapes", "etapes de la course qui deciderait"),
                         ("cellules_par_bande", "cellules par bande de la course qui deciderait"),
                         ("bandes", "bandes de la course qui deciderait"),
                         ("heures_projetees", "heures projetees de la course qui deciderait"),
                         ("secondes_par_etape_retenue", "cout retenu de la course qui deciderait"),
                         ("heures_au_rythme_reel_de_107", "heures au rythme reel de 107"),
                         ("secondes_par_etape_reelle_de_107", "cout reel par etape de 107")):
            if cle not in c2 or c2[cle] is None:
                continue
            val = c2[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if isinstance(val, float):
                for n_dec in (1, 2):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
            out.append((nom, formes, sep.name))
        for sel in ("calibre", "deux_roles"):
            b = d.get("par_selecteur", {}).get(sel, {})
            for cle, nom in (("mode_haut", "mode haut du selecteur"),
                             ("mode_bas", "mode bas du selecteur"),
                             ("trajets", "trajets du selecteur"),
                             ("force_du_meilleur", "force du meilleur du selecteur")):
                if cle not in b or b[cle] is None:
                    continue
                val = b[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                if isinstance(val, float):
                    for n_dec in (3,):
                        q = f"{val:.{n_dec}f}".replace(".", ",")
                        formes += [f"**{q}**", q]
                out.append((f"{nom} {sel}", formes, sep.name))

    # ⛔⛔⛔ LE PAS SELON LA DIRECTION (`106`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le residu sur la MATIERE ne voyage jamais sans celui sur la pile FABRIQUEE : « 19,3 µm »
    # est un nombre nu, « 19,3 contre 0,72 sur du connu, soit x22,3 » EST le resultat.
    # (2) Et la mediane SIGNEE du minimum ne voyage jamais sans la mediane ABSOLUE : la premiere
    # seule se lit comme un accord avec `101` alors qu'elle n'est que la symetrie de la dispersion,
    # et c'est la faute que cette tranche a payee.
    dirn = _source(racine, "le_pas_selon_la_direction.json")
    if dirn.exists():
        d = json.loads(dirn.read_text())
        s106 = d.get("resume", {})
        for cle, nom in (("cellules", "cellules de l'eventail"),
                         ("bandes", "bandes de l'eventail"),
                         ("cellules_sans_direction", "cellules sans direction"),
                         ("residu_sur_pile_fabriquee_um", "residu sur la pile fabriquee"),
                         ("combien_de_fois_pire_que_la_pile_fabriquee",
                          "combien de fois pire que la pile fabriquee"),
                         ("seuil_de_description_um", "seuil de description de la courbe"),
                         ("rapport_avec_le_selecteur_de_100",
                          "rapport avec le selecteur de 100"),
                         ("rapport_avec_le_selecteur_corrige",
                          "rapport avec le selecteur corrige"),
                         ("un_sur_cos_attendu", "un sur cos attendu par l'eventail"),
                         ("de_combien_le_selecteur_deplace_le_rapport",
                          "deplacement du rapport par le selecteur"),
                         ("ecart_restant_a_la_prediction", "ecart restant a la prediction"),
                         ("resolution_du_rapport", "resolution du rapport"),
                         ("ecart_absolu_median_du_minimum_deg",
                          "ecart absolu median du minimum"),
                         ("pas_de_leventail_deg", "pas de l'eventail")):
            if cle not in s106 or s106[cle] is None:
                continue
            val = s106[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if isinstance(val, float):
                for n_dec in (1, 2, 3):
                    q = f"{val:.{n_dec}f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                if cle.startswith("ecart_restant") or cle.startswith("de_combien"):
                    q = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
                    formes += [f"**{q}**", q]
            out.append((nom, formes, dirn.name))
        for nom_s in ("calibre", "deux_roles"):
            b = d.get(nom_s, {})
            for cle, nom in (("part_ou_le_parallele_gagne", "part ou le parallele gagne"),
                             ("gain_median_du_modele_parallele", "gain median du parallele"),
                             ("residu_parallele_median_um", "residu parallele median"),
                             ("residu_isotrope_median_um", "residu isotrope median"),
                             ("amplitude_mediane_um", "amplitude mediane de la courbe"),
                             ("pas_du_modele_parallele_median_um", "pas du modele parallele"),
                             ("angle_du_minimum_median_deg", "angle median du minimum"),
                             ("cellules_decidables", "cellules decidables de l'eventail"),
                             ("cellules_dont_le_rayon_est_hors_de_leventail",
                              "cellules dont le rayon est hors de l'eventail")):
                if cle not in b or b[cle] is None:
                    continue
                val = b[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                if cle == "part_ou_le_parallele_gagne":
                    pc = f"{100 * val:.1f}".replace(".", ",")
                    formes = [f"**{pc} %**", f"{pc} %", f"{pc}%"] + formes
                if isinstance(val, float):
                    q = f"{val:.1f}".replace(".", ",")
                    formes += [f"**{q}**", q]
                out.append((f"{nom} {nom_s}", formes, dirn.name))
        for e in d.get("controle_fabrique", {}).get("empilements", []):
            j = e.get("ajustement_juste", {})
            if not j.get("decidable"):
                continue
            th = f"{e['obliquite_deg']:.0f}"
            for val, nom in ((j["gain_du_modele_parallele"],
                              f"gain de la pile fabriquee a {th} degres"),
                             (e.get("ecart_median_a_la_prediction_um"),
                              f"ecart a la prediction a {th} degres")):
                if val is None:
                    continue
                txt = f"{val}".replace(".", ",")
                out.append((nom, [f"**{txt}**", txt, f"{val}",
                                  f"**{val:.1f}**".replace(".", ",")], dirn.name))
        for t in d.get("controle_fabrique", {}).get("tournantes", []):
            r_ = f"{t['rotation_deg_par_100um']:.0f}"
            for cle, nom in (("rapport", "rapport de la pile tournante a"),
                             ("le_long_de_la_normale", "pas le long de la normale tournante a"),
                             ("a_trente_quatre_degres", "pas a trente quatre degres tournante a"),
                             ("rotation_sur_la_sonde_deg", "rotation sur la sonde a")):
                val = t[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {r_}",
                            [f"**{txt}**", txt, f"{val}",
                             f"**{val:.0f}**", f"{val:.0f}"], dirn.name))
        if "secondes" in d:
            val = int(round(d["secondes"]))
            out.append(("secondes de la mesure par direction",
                        [f"**{val}**", f"{val}", f"{d['secondes']}"], dirn.name))

    # ⛔⛔⛔ LE BALAYAGE REND-IL LE PAS INJECTE (`105`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le pas lu par le BRUT ne voyage jamais sans celui lu par le CALIBRE : « 164,3 µm » est un
    # nombre nu, « 164,3 contre 194,6 sur les MEMES lectures » EST le resultat, et c'est leur ecart
    # qui dit que le sélecteur derive.
    # (2) Et le pas du marcheur ne voyage jamais sans la BANDE de `104` : sans elle, « 1,184 feuille
    # par pas » se lirait comme un ecart qu'une verification attraperait, alors que le fait est
    # qu'aucune ne l'attrape.
    bal = _source(racine, "le_balayage_rend_il_le_pas_injecte.json")
    if bal.exists():
        d = json.loads(bal.read_text())
        s105 = d.get("resume", {})
        for cle, nom in (("ecart_calibre_moins_brut_um", "ecart entre les deux selecteurs"),
                         ("ecart_relatif", "ecart relatif entre les deux selecteurs"),
                         ("bandes_lues", "bandes appariees du balayage")):
            if cle not in s105:
                continue
            val = s105[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if cle == "ecart_relatif":
                pc = f"{100 * val:.1f}".replace(".", ",")
                formes = [f"**{pc} %**", f"{pc} %", f"{pc}%"] + formes
            out.append((nom, formes, bal.name))
        for nom_s, val in s105.get("pas_median_par_selecteur_um", {}).items():
            if val is None:
                continue
            txt = f"{val}".replace(".", ",")
            out.append((f"pas lu par le selecteur {nom_s}", [f"**{txt}**", txt, f"{val}"],
                        bal.name))
        for nom_t, par in d.get("par_tiers", {}).items():
            for nom_s, val in par.items():
                if val is None:
                    continue
                txt = f"{val}".replace(".", ",")
                out.append((f"pas au {nom_t} par le selecteur {nom_s}",
                            [f"**{txt}**", txt, f"{val}"], bal.name))
        for nom_s, b in d.get("biais_fabrique", {}).items():
            for cle, nom in (("biais_relatif_median", "biais median fabrique du selecteur"),
                             ("biais_relatif_max", "biais maximal fabrique du selecteur")):
                val = b[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}", f"{val:+.4f}".replace(".", ",")]
                pc = f"{100 * val:.1f}".replace(".", ",")
                formes += [f"**{pc} %**", f"+{pc} %", f"+{pc}%", f"{pc} %"]
                out.append((f"{nom} {nom_s}", formes, bal.name))
        mec = d.get("mecanisme", {})
        for cle, nom in (("mu_le_plus_court", "mu du nul au plus court"),
                         ("mu_le_plus_long", "mu du nul au plus long"),
                         ("sd_le_plus_court", "sigma du nul au plus court"),
                         ("sd_le_plus_long", "sigma du nul au plus long"),
                         ("choix_brut_um", "candidat retenu par le brut"),
                         ("choix_calibre_um", "candidat retenu par le calibre"),
                         ("accord_brut_du_choix_brut", "accord brut du choix brut"),
                         ("accord_brut_du_choix_calibre", "accord brut du choix calibre")):
            if cle not in mec:
                continue
            val = mec[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], bal.name))
        for nom_s, c in d.get("la_longueur_differe_du_nul", {}).items():
            if "kolmogorov_smirnov_D" not in c:
                continue
            for cle, nom in (("mediane_reelle_um", "mediane reelle du selecteur"),
                             ("mediane_du_nul_um", "mediane du nul du selecteur"),
                             ("kolmogorov_smirnov_D", "D de Kolmogorov-Smirnov du selecteur")):
                val = c[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {nom_s}", [f"**{txt}**", txt, f"{val}"], bal.name))
        w = d.get("consequence_pour_le_marcheur", {})
        for cle, nom in (("pas_du_marcheur_um", "pas du marcheur"),
                         ("pas_vrai_indique_um", "pas vrai indique"),
                         ("feuilles_franchies_par_pas", "feuilles franchies par pas"),
                         ("spires_apres_120_pas", "spires apres cent vingt pas"),
                         ("spires_en_trop_sur_120", "spires en trop sur cent vingt")):
            if cle not in w:
                continue
            val = w[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if isinstance(val, float) and abs(val) >= 10.0:
                formes = [f"**{val:.0f}**", f"{val:.0f}"] + formes
            out.append((nom, formes, bal.name))
        c99 = d.get("ce_que_ca_change_pour_99", {})
        for cle, nom in (("periode_vraie_indiquee_um", "periode vraie indiquee par l'inversion"),
                         ("ecart_publie_en_pourcent", "ecart publie en pourcent"),
                         ("ecart_indique_en_pourcent", "ecart indique en pourcent")):
            if cle not in c99:
                continue
            val = c99[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if "pourcent" in cle:
                formes = [f"**{txt} %**", f"{txt} %", f"{txt}%"] + formes
            out.append((nom, formes, bal.name))
        if "part_de_lecart_imputable_a_linstrument" in c99:
            val = c99["part_de_lecart_imputable_a_linstrument"]
            pc = f"{100 * val:.1f}".replace(".", ",")
            out.append(("part de l'ecart imputable a l'instrument",
                        [f"**{pc} %**", f"{pc} %", f"{pc}%",
                         f"{val}".replace(".", ","), f"{val}"], bal.name))
        if "cran_du_balayage_um" in d:
            val = d["cran_du_balayage_um"]
            txt = f"{val}".replace(".", ",")
            out.append(("cran du balayage apparie", [f"**{txt}**", txt, f"{val}"], bal.name))

    # ⛔⛔⛔ UN PAS CONFIRME N'EST PAS UNE FEUILLE (`104`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) La fraction basse ne voyage JAMAIS sans sa consequence enchainee : « 0,68 feuille »
    # parait inoffensif, « 38 spires manquantes sur 120 » EST le fait qui refute le critere.
    # (2) Et elle ne voyage jamais sans la fraction HAUTE : une bande n'est une bande que par ses
    # deux bords, et la seule basse se lirait comme un biais mesure alors que c'est une TOLERANCE.
    pcf = _source(racine, "un_pas_confirme_nest_pas_une_feuille.json")
    if pcf.exists():
        d = json.loads(pcf.read_text())
        for x in d.get("bande", {}).get("par_bruit", []):
            if x.get("aucune_fraction_confirmee"):
                continue
            b = f"{x['bruit']:.0f}"
            for cle, nom in (("fraction_basse", "fraction basse confirmee a sigma"),
                             ("fraction_haute", "fraction haute confirmee a sigma"),
                             ("largeur", "largeur de la bande a sigma"),
                             ("spires_apres_120_pas_au_plus_bas",
                              "spires apres 120 pas au plus bas a sigma"),
                             ("spires_apres_120_pas_au_plus_haut",
                              "spires apres 120 pas au plus haut a sigma"),
                             ("pas_de_feuille_implique_um_bas",
                              "pas de feuille implique bas a sigma"),
                             ("pas_de_feuille_implique_um_haut",
                              "pas de feuille implique haut a sigma")):
                val = x[cle]
                txt = f"{val}".replace(".", ",")
                formes = [f"**{txt}**", txt, f"{val}"]
                # ⚠ Un compte de spires se redige aussi arrondi a l'entier, et une fraction en
                # pourcentage : accepter les deux evite d'accuser un texte correct, ce que le
                # garde a deja fait une fois.
                if "spires" in cle:
                    formes = [f"**{val:.0f}**", f"{val:.0f}"] + formes
                if cle.startswith("pas_de_feuille"):
                    formes = [f"**{val:.0f}**", f"{val:.0f}"] + formes
                out.append((f"{nom} {b}", formes, pcf.name))
        s104 = d.get("resume", {})
        for cle, nom in (("fraction_la_plus_basse_confirmee", "fraction la plus basse confirmee"),
                         ("erreur_de_spires_maximale_sur_120",
                          "spires manquantes sur cent vingt"),
                         ("largeur_maximale_de_la_bande", "largeur maximale de la bande"),
                         ("combien_de_pas_publies_confondus", "pas publies confondus")):
            if cle not in s104 or s104[cle] is None:
                continue
            val = s104[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            # ⚠⚠⚠ L'ECRITURE ARRONDIE N'EST ACCEPTEE QUE SI ELLE RESTE DISCRIMINANTE. Arrondir
            # 0,68 a l'entier donne « 1 », qu'on trouve dans n'importe quel document : le garde
            # passerait alors pour la mauvaise raison, ce qui est pire qu'un garde absent. Au-dela
            # de dix l'arrondi garde l'identite du nombre, en-deca il la detruit.
            if isinstance(val, float) and abs(val) >= 10.0:
                formes = [f"**{val:.0f}**", f"{val:.0f}"] + formes
            out.append((nom, formes, pcf.name))
        for x in d.get("aveuglement", {}).get("lignes", []):
            # ⚠ Surtout PAS `fr` : ce nom est celui de la fonction de formatage du module, et
            # l'affecter ici en ferait une locale de `collecter` — donc non liee pour la closure
            # `ajoute`, qui casse alors des CENTAINES de lignes PLUS HAUT que cette boucle.
            frv = f"{x['fraction_vraie']}".replace(".", ",")
            for cle, nom in (("compte_entier", "compte entier pour la fraction"),
                             ("score_entier", "score du compteur pour la fraction"),
                             ("fraction_estimee", "fraction estimee pour la fraction")):
                val = x[cle]
                txt = f"{val}".replace(".", ",")
                out.append((f"{nom} {frv}", [f"**{txt}**", txt, f"{val}"], pcf.name))
        cbd = d.get("ce_que_la_bande_ne_distingue_pas", {})
        for cle, nom in (("ecart_publie_par_99_en_pourcent", "ecart publie par 99 en pourcent"),
                         ("largeur_de_la_bande_en_pourcent", "largeur de la bande en pourcent")):
            if cle not in cbd:
                continue
            val = cbd[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt} %**", f"{txt} %", f"{txt}%", f"**{txt}**", txt], pcf.name))
        c102 = d.get("ce_que_102_pouvait_dire_de_la_forme", {})
        for cle, nom in (("risque_par_pas_compatible_de", "risque par pas compatible de"),
                         ("risque_par_pas_compatible_a", "risque par pas compatible a"),
                         ("largeur_maximale", "largeur de la borne tiree des lignes de 102")):
            if cle not in c102:
                continue
            val = c102[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], pcf.name))
        for cle, x in d.get("prix_de_la_mesure_de_portee", {}).items():
            out.append((f"heures de la mesure de portee {cle}",
                        [f"**{x['heures']}**".replace(".", ","),
                         f"{x['heures']}".replace(".", ","), f"{x['heures']}"], pcf.name))

    # ⭐⭐⭐ COMBIEN DE PAS LA MATIERE PORTE (`102`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES.
    # (1) Le nombre de pas de la MATIERE ne voyage jamais sans celui du NAIF : « 2,00 pas » est un
    # nombre nu, « 2,00 contre 0,00 » EST le resultat, et c'est leur ecart qui dit que la voie
    # sert a quelque chose.
    # (2) Et il ne voyage jamais sans la CENSURE : 17 bandes sur 28 ont une cellule au plafond,
    # donc publier la mediane sans dire qu'elle est tronquee ferait passer un budget de lecture
    # pour une limite de matiere — la butee de `99`.
    prt = _source(racine, "combien_de_pas_la_matiere_porte.json")
    if prt.exists():
        d = json.loads(prt.read_text())
        s102 = d.get("resume", {})
        for cle, nom in (("pas_confirmes_median_matiere", "pas confirmes par la matiere"),
                         ("pas_confirmes_median_naif", "pas confirmes par l'automate naif"),
                         ("avantage_en_pas", "avantage en pas de la matiere"),
                         ("distance_portee_mediane_um", "distance mediane portee"),
                         ("bandes_dont_une_cellule_atteint_le_plafond",
                          "bandes dont une cellule atteint le plafond"),
                         ("plafond_de_pas", "plafond de pas de la marche"),
                         ("bandes_lues", "bandes marchees")):
            if cle not in s102:
                continue
            val = s102[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if isinstance(val, float):
                court = f"{val:.2f}".replace(".", ",")
                formes = [f"**{court}**", court, f"{val:.2f}"] + formes
            out.append((nom, formes, prt.name))
        for cle, nom in (("pas_confirmes_contre_rayon",
                          "pas confirmes contre le rayon"),
                         ("pas_confirmes_contre_continuite",
                          "pas confirmes contre la continuite")):
            if cle not in s102:
                continue
            val = s102[cle]
            signe = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{signe}**", signe, f"{val:+.3f}",
                              f"{val}".replace(".", ","), f"{val}"], prt.name))
        # ⭐⭐ LE CONTROLE FABRIQUE VOYAGE ENTIER : « le naif fait 1 » ne veut rien dire sans
        # « et il fait 6 quand il a raison » — sans quoi il se lirait comme un homme de paille.
        for e in d.get("controle_fabrique", {}).get("empilements", []):
            th = f"{e['obliquite_deg']:.0f}"
            for cle, nom in (("pas_confirmes_matiere", "pas de la matiere a"),
                             ("pas_confirmes_naif", "pas du naif a")):
                val = e[cle]
                out.append((f"{nom} {th} degres",
                            [f"**{val}**", f"{val}"], prt.name))

    # ⭐⭐⭐ LA DIRECTION QUE LA MATIERE MONTRE (`101`), ET L'APPARIEMENT EST OBLIGATOIRE ICI
    # AUSSI. L'angle de la matiere au MAILLAGE ne voyage jamais sans celui au RAYON : « la matiere
    # est a 13° du maillage » est un nombre nu, « 13° du maillage contre 35° du rayon » EST le
    # verdict — c'est leur ECART qui distingue les deux lectures que `100` laissait ouvertes.
    # Et les deux residus du modele d'axe voyagent ensemble pour la meme raison : un residu seul
    # ne dit pas s'il est bon ou mauvais, c'est sa comparaison a l'autre modele qui tranche.
    dir_ = _source(racine, "la_direction_que_la_matiere_montre.json")
    if dir_.exists():
        d = json.loads(dir_.read_text())
        s101 = d.get("resume", {})
        for cle, nom in (("angle_matiere_maillage_median_deg",
                          "angle de la matiere au maillage"),
                         ("angle_matiere_rayon_median_deg",
                          "angle de la matiere au rayon"),
                         ("ecart_entre_les_deux_lectures_deg",
                          "ecart entre les deux lectures de l'obliquite"),
                         ("part_orientee_mediane", "part de cellules orientees"),
                         ("planarite_mediane", "planarite mediane de la matiere")):
            if cle not in s101:
                continue
            val = s101[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            if cle.endswith("_deg") and isinstance(val, float):
                court = f"{val:.1f}".replace(".", ",")
                formes = [f"**{court}**", court, f"{val:.1f}"] + formes
            out.append((nom, formes, dir_.name))
        for cle, nom in (("part_orientee_contre_continuite",
                          "part orientee contre la continuite"),
                         ("part_orientee_contre_continuite_a_rayon_tenu",
                          "part orientee contre la continuite a rayon tenu"),
                         ("ecart_a_la_matiere_contre_continuite",
                          "ecart a la matiere contre la continuite"),
                         ("part_orientee_contre_rayon", "part orientee contre le rayon"),
                         ("continuite_contre_rayon", "continuite contre le rayon")):
            if cle not in s101:
                continue
            val = s101[cle]
            signe = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{signe}**", signe, f"{val:+.3f}",
                              f"{val}".replace(".", ","), f"{val}"], dir_.name))
        ax = d.get("un_axe_decale_est_il_lexplication", {})
        for cle, nom in (("residu_du_modele_daxe_deg", "residu du modele d'axe decale"),
                         ("residu_du_modele_constant_deg",
                          "residu du modele d'obliquite constante"),
                         ("decalage_qui_explique_le_coeur_mm",
                          "decalage qui explique le coeur"),
                         ("angle_predit_au_bord_par_ce_decalage_deg",
                          "angle predit au bord par ce decalage"),
                         ("decalage_qui_explique_le_bord_mm",
                          "decalage qui explique le bord"),
                         ("angle_predit_au_coeur_par_ce_decalage_deg",
                          "angle predit au coeur par ce decalage")):
            if cle not in ax:
                continue
            val = ax[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], dir_.name))
        n101 = d.get("nul_du_tenseur", {})
        for cle, nom in (("accord_des_moities_median_deg",
                          "desaccord des moities sur du bruit pur"),
                         ("accord_des_moities_p1_deg", "barre d'accord des moities"),
                         ("planarite_mediane", "planarite du bruit pur")):
            if cle not in n101:
                continue
            val = n101[cle]
            txt = f"{val}".replace(".", ",")
            out.append((nom, [f"**{txt}**", txt, f"{val}"], dir_.name))
        if "defaut_de_similitude_deg" in d:
            val = d["defaut_de_similitude_deg"]
            txt = f"{val}".replace(".", ",")
            out.append(("defaut de similitude de la transformation",
                        [f"**{txt}**", txt, f"{val}"], dir_.name))

    # ⭐⭐⭐ L'OBLIQUITE DE LA NAPPE (`100`), ET DEUX APPARIEMENTS SONT OBLIGATOIRES ICI.
    # (1) L'angle MESURE ne voyage jamais sans l'angle PREDIT : « la normale est a 31° du rayon »
    # est un nombre nu, « 31° la ou une spirale en predit 0,25 » EST le resultat. Publier le
    # premier seul serait publier une surprise sans dire qu'elle en est une.
    # (2) Le rapport radial/normal ne voyage jamais sans 1/cos : le rapport seul se lit comme une
    # egalite banale, alors que c'est une REFUTATION — et une refutation sans ce qu'elle refute
    # n'est pas verifiable.
    obl = _source(racine, "la_normale_nest_pas_le_rayon.json")
    if obl.exists():
        d = json.loads(obl.read_text())
        s100 = d.get("resume", {})
        for cle, nom in (("angle_grille_median_deg", "angle de la normale de grille au rayon"),
                         ("angle_acp_median_deg", "angle de la normale ACP au rayon"),
                         ("inclinaison_predite_mediane_deg",
                          "inclinaison predite par la spirale"),
                         ("combien_de_fois_la_prediction",
                          "combien de fois la prediction de la spirale"),
                         ("ecart_entre_estimateurs_deg", "ecart entre les deux estimateurs"),
                         ("angle_du_a_z_median_deg", "part de l'obliquite due a z"),
                         ("angle_dans_le_plan_median_deg",
                          "part de l'obliquite dans le plan"),
                         ("angle_au_plus_petit_voisinage_deg",
                          "angle au plus petit voisinage"),
                         ("angle_au_plus_grand_voisinage_deg",
                          "angle au plus grand voisinage")):
            if cle not in s100:
                continue
            val = s100[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            # ⚠⚠ UN ANGLE SE REDIGE AU DIXIEME DE DEGRE, ET C'EST CE QUE LE MODULE IMPRIME
            # LUI-MEME. Exiger la forme a deux decimales ferait accuser un texte correct de
            # citer un chiffre perime — la faute que ce garde a deja payee, et il n'y a pas
            # d'ambiguite ici : 34,1 et 34,06 sont le meme nombre a la precision affichee.
            if cle.endswith("_deg") and isinstance(val, float):
                court = f"{val:.1f}".replace(".", ",")
                formes = [f"**{court}**", court, f"{val:.1f}"] + formes
            out.append((nom, formes, obl.name))
        dd = d.get("le_pas_dans_les_deux_directions", {})
        for cle, nom in (("rapport_median", "rapport pas radial sur pas normal"),
                         ("rapport_min", "rapport radial/normal, minimum"),
                         ("rapport_max", "rapport radial/normal, maximum"),
                         ("un_sur_cos_median", "1/cos median de l'obliquite"),
                         ("ecart_a_un", "ecart du rapport a un"),
                         ("ecart_a_un_sur_cos", "ecart du rapport a 1/cos"),
                         ("correlation_rapport_contre_un_sur_cos",
                          "correlation du rapport contre 1/cos")):
            if cle not in dd:
                continue
            val = dd[cle]
            txt = f"{val}".replace(".", ",")
            formes = [f"**{txt}**", txt, f"{val}"]
            # ⚠ Une correlation se publie AVEC SON SIGNE : « 0,153 » et « +0,153 » sont le meme
            # nombre, et le depot ecrit le second — sans cette forme le garde le croirait absent.
            if cle.startswith("correlation"):
                signe = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
                formes = [f"**{signe}**", signe, f"{val:+.3f}"] + formes
            out.append((nom, formes, obl.name))

    # ⭐⭐⭐ LES INTERSTICES TRAVERSES (`98`), LE PREMIER CRITERE DONT LE SEUIL VIENT DE LA
    # MATIERE. Garde parce que le verdict n'a de sens qu'avec la BARRE DU NUL a cote : « accord
    # 0,353 » est un nombre nu, « 0,353 pour une barre de 0,331 » dit que la matiere est presque
    # muette. Publier l'un sans l'autre serait publier un accord sans son etalon.
    cit = _source(racine, "combien_dinterstices_traverses.json")
    if cit.exists():
        d = json.loads(cit.read_text())
        txt = f"{d['barre_du_nul']:.4f}".replace(".", ",")
        out.append(("barre du modele nul",
                    [f"**{txt}**", txt, f"{d['barre_du_nul']}"], cit.name))
        for tiers in ("coeur", "milieu", "bord"):
            t = d["par_tiers"].get(tiers)
            if not t:
                continue
            for cle, nom in (("part_un_interstice", "part a un interstice au"),
                             ("accord_median", "accord median au"),
                             ("part_lue", "part ou la matiere repond au"),
                             ("part_partant_sur_la_feuille", "part partant sur la feuille au"),
                             ("marge_de_polarite_mediane", "marge de polarite au")):
                val = t[cle]
                txt = f"{val:.3f}".replace(".", ",")
                out.append((f"{nom} {tiers}", [f"**{txt}**", txt, f"{val}"], cit.name))
        for cle, nom in (("un_interstice_contre_rayon", "interstices contre le rayon"),
                         ("un_interstice_contre_continuite",
                          "interstices contre la continuite")):
            val = d["correlations"][cle]
            txt = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{txt}**", txt, f"{val:.3f}"], cit.name))

    # ⭐⭐⭐ LE DESACCORD ENTRE DEUX TRACES HUMAINS (`97`), ET C'EST UN PLANCHER. Garde parce que
    # les DEUX estimateurs doivent voyager ensemble : le plus proche voisin rend deux a trois
    # fois plus et mesure l'espacement des rangs de l'autre revision, donc publier l'un sans
    # l'autre laisserait croire le choix d'estimateur indifferent.
    dhm = _source(racine, "deux_humains_sur_la_meme_matiere.json")
    if dhm.exists():
        d = json.loads(dhm.read_text())
        for tiers in ("coeur", "milieu", "bord"):
            t = d["par_tiers"].get(tiers)
            if not t:
                continue
            for cle, nom in (("desaccord_median_um", "desaccord au plan au"),
                             ("au_plus_proche_voisin_um", "desaccord au plus proche voisin au"),
                             ("part_au_dela_dune_feuille", "part au-dela d'une feuille au")):
                val = t[cle]
                txt = (f"{val:.1f}" if cle.endswith("_um") else f"{val:.3f}").replace(".", ",")
                out.append((f"{nom} {tiers}",
                            [f"**{txt} µm**", f"**{txt}**", f"{txt} µm", txt, f"{val}"],
                            dhm.name))
        for cle, nom in (("desaccord_contre_rayon", "desaccord contre le rayon"),
                         ("desaccord_contre_fermeture", "desaccord contre la fermeture")):
            val = d["correlations"][cle]
            txt = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{txt}**", txt, f"{val:.3f}"], dhm.name))

    # ⭐⭐⭐ LA FERMETURE D'UN TOUR (`96`), LE PREMIER SIGNAL DONT LE SIGNE SOIT LE BON. Garde
    # parce que son verdict tient a DEUX choses qui doivent voyager ensemble : le signe positif,
    # et le plancher au coeur qui l'empeche de certifier. Publier le premier sans le second
    # ferait passer un signal non calibrable pour une confiance par cellule.
    fdt = _source(racine, "la_fermeture_dun_tour.json")
    if fdt.exists():
        d = json.loads(fdt.read_text())
        for tiers in ("coeur", "milieu", "bord"):
            t = d["par_tiers"].get(tiers)
            if not t:
                continue
            for cle, nom in (("part_hors_demi_feuille", "part hors demi-feuille au"),
                             ("fermeture_en_feuilles", "fermeture en feuilles au")):
                txt = f"{t[cle]:.3f}".replace(".", ",")
                out.append((f"{nom} {tiers}",
                            [f"**{txt}**", txt, f"{t[cle]}"], fdt.name))
        for cle, nom in (("hors_demi_feuille_contre_rayon", "fermeture contre le rayon"),
                         ("hors_demi_feuille_contre_continuite",
                          "fermeture contre la continuite")):
            val = d["correlations"][cle]
            txt = f"{val:+.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{txt}**", txt, f"{val:.3f}"], fdt.name))
        # ⚠⚠ LE BALAYAGE EST GARDE ENTIER, REEL ET FIXTURE : c'est la comparaison des deux qui
        # etablit « structure et non bruit », donc citer l'un sans l'autre serait perime.
        for b in d["balayage_reel"]:
            if "part_hors_demi_feuille_mediane" not in b:
                continue
            txt = f"{b['part_hors_demi_feuille_mediane']:.3f}".replace(".", ",")
            out.append((f"fermeture reelle a {b['tours']} tour(s)",
                        [f"**{txt}**", txt, f"{b['part_hors_demi_feuille_mediane']}"],
                        fdt.name))
        for b in d["balayage_des_fixtures"]:
            for cle, nom in (("bruit_seul", "fixture bruit seul a"),
                             ("avec_une_feuille_sautee", "fixture avec saut a")):
                txt = f"{b[cle]:.3f}".replace(".", ",")
                out.append((f"{nom} {b['tours']} tour(s)",
                            [f"**{txt}**", txt, f"{b[cle]}"], fdt.name))

    # ⭐⭐⭐ LE MEME ECART, MAIS A TRAVERS LES RAYONS (`95`). Garde parce que c'est le SECOND
    # candidat de signal de confiance a echouer, et que son verdict ne tient que si le
    # confondant du masque est publie a cote : sans lui, « la surface est mieux posee au bord »
    # et « le volume s'arrete au bord » sont la meme observation.
    sfr = _source(racine, "la_surface_et_la_feuille_par_rayon.json")
    if sfr.exists():
        d = json.loads(sfr.read_text())
        for tiers in ("coeur", "milieu", "bord"):
            t = d["par_tiers"].get(tiers)
            if not t:
                continue
            out.append((f"dispersion surface/feuille au {tiers}",
                        [f"**{t['dispersion_um']} µm**", f"{t['dispersion_um']} µm",
                         f"{t['dispersion_um']}".replace(".", ",") + " µm",
                         f"{t['dispersion_um']}".replace(".", ",")], sfr.name))
        c, q = d["correlations"], d["une_fois_le_masque_retire"]
        for nom, val in (("dispersion contre le rayon", c["dispersion_contre_rayon"]),
                         ("dispersion contre la continuite", c["dispersion_contre_continuite"]),
                         ("part au remplissage contre le rayon", c["part_au_zero_contre_rayon"]),
                         ("contraste contre le rayon", c["contraste_contre_rayon"]),
                         ("dispersion/rayon masque retire", q["dispersion_contre_rayon"]),
                         ("dispersion/continuite masque retire",
                          q["dispersion_contre_continuite"])):
            txt = f"{val:.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((nom, [f"**{txt}**", txt, f"{val:.3f}"], sfr.name))
        # ⚠⚠ LE BALAYAGE EST GARDE ENTIER : c'est lui qui rend « le seuil n'est pas regle »
        # verifiable, donc un document qui n'en citerait qu'une valeur serait perime sans
        # qu'on le voie.
        for b in d["balayage_du_seuil"]:
            if "dispersion_contre_rayon" not in b:
                continue
            v = b["dispersion_contre_rayon"]
            txt = f"{v:.3f}".replace(".", ",").replace("-", "\u2212")
            out.append((f"balayage a {int(b['seuil'] * 100)} % de remplissage",
                        [f"**{txt}**", txt, f"{v}".replace(".", ",").replace("-", "\u2212"),
                         f"{v}"], sfr.name))
        out.append(("cellules perdues au reseau",
                    [f"**{d['cellules_perdues']}**", str(d["cellules_perdues"])], sfr.name))

    sef = _source(racine, "la_surface_et_la_feuille.json")
    if sef.exists():
        d = json.loads(sef.read_text())
        # ⭐⭐ La correction de budget apportee a la chaine de `44`, avec son statut. Gardee
        # parce que le couple (valeur, « conjecture ») ne vaut que s'il reste lie : publier
        # 64,7 sans « conjecture » en ferait une mesure.
        # ⚠⚠ Les micrometres de la derive de `44` NE SONT PLUS gardes : `77` §10 etablit que
        # son voxel n'a pas de provenance reconstructible, donc composer ses micrometres avec
        # les notres serait exactement ce que le fichier refuse de faire. Ce qui est garde a la
        # place est le referent en FEUILLES, qui lui voyage.
        cb = d.get("correction_du_budget") or {}
        if cb.get("referent_en_feuilles_min"):
            out.append(("referent en feuilles, etendue sur les rouleaux",
                        [f"**{cb['referent_en_feuilles_min']:.3f}** à "
                         f"**{cb['referent_en_feuilles_max']:.3f}**",
                         f"{cb['referent_en_feuilles_min']:.3f} à "
                         f"{cb['referent_en_feuilles_max']:.3f}",
                         f"0,16 à 0,25"], sef.name))
            out.append(("rouleau de la chaine de 44",
                        [f"**{cb['rouleau_de_la_chaine']}**",
                         f"`{cb['rouleau_de_la_chaine']}`"], sef.name))
        # ⚠ L'ETENDUE de la dispersion brute, pas six valeurs : c'est ce que la prose dit, et
        # garder six chiffres obligerait a les ecrire tous les six pour rien.
        bruts = [sp["brut_ecart_type_feuilles"] for sp in d["spires"]]

        # ⚠⚠ Des PLAGES PAR ROULEAU, pas une valeur par pile : le document dit « 23,3 a
        # 27,7 um sur PHerc0172 », et garder onze valeurs individuelles obligerait a les
        # ecrire toutes les onze pour rien -- puis a les reecrire a chaque pile ajoutee.
        par_rouleau: dict[str, list[dict]] = {}
        for sp in d["spires"]:
            par_rouleau.setdefault(sp["rouleau"], []).append(sp)
        for rouleau, lot in sorted(par_rouleau.items()):
            um = [x["ecart_type_um"] for x in lot]
            fe = [x["ecart_type_feuilles"] for x in lot]
            if len(lot) == 1:
                out.append((f"ecart a la feuille, {rouleau}",
                            [f"**{um[0]:.1f} µm**", f"{um[0]:.1f} µm",
                             f"**{um[0]:.1f} µm**".replace(".", ",")], sef.name))
                out.append((f"ecart en feuilles, {rouleau}",
                            [f"**{fe[0]:.3f}**", f"{fe[0]:.3f}",
                             f"**{fe[0]:.3f}**".replace(".", ",")], sef.name))
            else:
                plage_um = f"{min(um):.1f} – {max(um):.1f} µm"
                plage_fe = f"{min(fe):.3f} – {max(fe):.3f}"
                out.append((f"ecart a la feuille, {rouleau}",
                            [plage_um, plage_um.replace(".", ","),
                             plage_um.replace(" – ", " - ")], sef.name))
                out.append((f"ecart en feuilles, {rouleau}",
                            [f"**{plage_fe}**", plage_fe,
                             f"**{plage_fe.replace('.', ',')}**"], sef.name))
    # ⚠ L'ETENDUE de la dispersion brute, pas six valeurs : c'est ce que la prose dit, et
        # garder six chiffres obligerait a les ecrire tous les six pour rien.
        bruts = [sp["brut_ecart_type_feuilles"] for sp in d["spires"]]
        out.append(("dispersion brute, etendue",
                    [f"**{min(bruts):.3f}** à **{max(bruts):.3f}**",
                     f"{min(bruts):.3f} à {max(bruts):.3f}".replace(".", ","),
                     f"de {min(bruts):.3f} à {max(bruts):.3f}"], sef.name))

    # ⚠⚠ Le NEGATIF de B2 : α ne se calcule pas sur un volume de surface. Garde parce qu'un
    # futur lecteur relira « on pourrait tester le placement sans rien rendre » et doit trouver
    # tout de suite pourquoi non, avec le compte qui le dit.
    aep = _source(racine, "alpha_et_le_placement.json")
    if aep.exists():
        d = json.loads(aep.read_text())
        m = d.get("mesures") or []
        refuses = sum(1 for x in m if x.get("alpha") is None)
        if m:
            out.append(("cas indecidables de alpha sur volume de surface",
                        [f"**{refuses} refusés sur {len(m)}**",
                         f"{refuses} refusés sur {len(m)}",
                         f"{refuses} sur {len(m)}"], aep.name))
    # ⭐⭐⭐ La reparation contre la proximite, sur la population que `07` croyait absente.
    # Garde parce que le SIGNE est le resultat : publier « +398 % » sans « -17 % » ferait de
    # l'instabilite une tendance.
    rep = _source(racine, "reparation_et_proximite_scroll1.json")
    if rep.exists():
        d = json.loads(rep.read_text())
        out.append(("traces eligibles de Scroll 1",
                    [f"**{d['eligibles']} traces**", f"{d['eligibles']} traces"], rep.name))
        for x in d.get("paires", []):
            if x.get("variation_pct") is None:
                continue
            court = x["trace"].split("-", 1)[-1]
            out.append((f"variation de proximite, {court}",
                        [f"**{x['variation_pct']:+.1f} %**",
                         f"{x['variation_pct']:+.1f} %",
                         f"{x['variation_pct']:+.1f} %".replace(".", ",")], rep.name))
    bdf = _source(racine, "bruit_dune_fenetre.json")
    if bdf.exists():
        d = json.loads(bdf.read_text())
        v = d.get("variance", {})
        if v.get("exploitable"):
            ajoute("dispersion des AUC DANS un fragment", v["ecart_type_intra"], 4, bdf.name)
            ajoute("dispersion des AUC ENTRE fragments", v["ecart_type_inter"], 4, bdf.name)
            ajoute("part attribuable au fragment", v["icc"], 3, bdf.name)
        # ⚠ Ce compte est le seul de ce fichier qui soit ACTIONNABLE : il dit combien de
        # tuiles une campagne future doit rendre. Le perdre reviendrait a relancer la meme
        # experience sous-dimensionnee.
        if d.get("tuiles_pour_distinguer"):
            out.append(("tuiles necessaires par fragment",
                        [f"**{d['tuiles_pour_distinguer']} tuiles par fragment**",
                         f"{d['tuiles_pour_distinguer']} tuiles par fragment",
                         f"{d['tuiles_pour_distinguer']} tiles per fragment"], bdf.name))
        # ⚠⚠ Ces deux-la sont ce qu'une campagne FUTURE lira avant de se dimensionner, et
        # ils sont gardes parce que j'ai deja publie l'un des deux faux : « 63 » etait juste
        # pour un ecart-type de 0,2 et faux pour le notre, qui vaut 0,2243.
        for cle, ecart in (("tuiles_pour_un_ecart_de_0_05", "0,05"),
                           ("tuiles_pour_un_ecart_de_0_10", "0,10")):
            if d.get(cle):
                out.append((f"tuiles pour un ecart de {ecart}",
                            [f"{d[cle]} par condition", f"en demande {d[cle]}"], bdf.name))
        out.append(("tuiles sous le hasard",
                    [f"**{d['tuiles_sous_le_hasard']} tuiles sur {d['tuiles_totales']}**",
                     f"{d['tuiles_sous_le_hasard']} tuiles sur {d['tuiles_totales']}",
                     f"{d['tuiles_sous_le_hasard']} sur {d['tuiles_totales']}"], bdf.name))
        ajoute("AUC de la tuile la plus basse", d["auc_de_tuile_minimale"], 3, bdf.name)
        # ⚠⚠ Ajoutes le 2026-09-03 avec la section 6.2 de l'article. Elle publie l'AUC de
        # chaque fragment, son erreur-type par tuiles, et le FACTEUR entre celle-ci et
        # Hanley-McNeil -- et c'est le facteur qui porte l'argument, pas les deux erreurs
        # prises separement. Il est recalcule ici plutot que lu : un rapport publie sans son
        # calcul est exactement ce que la section reproche a la litterature.
        for frag, f in d.get("fragments", {}).items():
            ajoute(f"AUC groupee du fragment, {frag}", f["auc_groupee"], 3, bdf.name)
            b = f.get("bootstrap", {})
            hm = f.get("se_hanley_mcneil")
            if b.get("exploitable") and hm:
                ajoute(f"erreur type par tuiles, {frag}", b["erreur_type"], 3, bdf.name)
                fact = round(b["erreur_type"] / hm)
                out.append((f"facteur contre Hanley-McNeil, {frag}",
                            [f"{fact} times", f"{fact} fois", f"{fact}$times$",
                             f"{fact}×"], bdf.name))
        for frag, f in d.get("fragments", {}).items():
            st = f.get("destriage", {})
            if st.get("exploitable"):
                ajoute(f"cout de l'alignement des niveaux, {frag}", st["gain"], 3, bdf.name,
                       signe=True)
    return out


def verifier() -> int:
    """Le garde-fou se garde lui-même.

    ⚠⚠ Il n'en avait aucun. Ce fichier protège 140 chiffres publiés répartis sur 28
    fichiers de résultat, et rien ne vérifiait qu'il sait encore les trouver — ni, surtout,
    qu'il sait ÉCHOUER. Une vérification qu'on ne vérifie pas est de la même famille qu'une
    vérification incapable d'échouer.
    """
    from pathlib import Path as _P
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # ⚠⚠ `normaliser` replie la typographie SANS SENS NUMERIQUE, et rien d'autre. Le signe
    # moins typographique que la prose ecrit (U+2212) et le trait d'union ASCII que
    # `f"{x}"` produit designent le meme nombre ; la virgule et le point, eux, sont deux
    # ECRITURES d'un meme nombre et c'est la liste des ecritures acceptees qui s'en occupe.
    # Mes trois premiers temoins supposaient l'inverse, et c'est l'auto-test qui a corrige
    # ma lecture de la fonction plutot que la fonction.
    v("le moins typographique devient un moins ASCII",
      normaliser("−0,382") == "-0,382", normaliser("−0,382"))
    v("le tiret demi-cadratin aussi", normaliser("–5") == "-5")
    v("l'espace insécable devient une espace", normaliser("75\u00a0810") == "75 810")
    v("l'espace fine insécable aussi", normaliser("75\u202f810") == "75 810")
    # ⚠ Et la propriete qu'il ne faut PAS avoir : virgule et point ne sont pas confondus
    # ici, sinon « 0,859 » matcherait un document qui dit « 0.859 » ET un qui dit autre
    # chose de la meme forme. Le partage des roles est ce qui garde le garde precis.
    v("la virgule et le point restent distincts",
      normaliser("12,97") != normaliser("12.97"))
    v("fr écrit à la française", fr(0.859, 3) == "0,859")
    v("en écrit à l'anglaise", en(0.859, 3) == "0.859")

    doc = {_P("bon.md"): normaliser("le taux vaut 6,4 % sur 78 tirages")}
    v("un chiffre présent est trouvé", ou_trouve(["6,4 %"], doc) == ["bon.md"])
    v("... et les deux écritures fournies suffisent",
      ou_trouve(["6.4 %", "6,4 %"], doc) == ["bon.md"])
    v("... alors qu'une seule, la mauvaise, ne trouve rien",
      ou_trouve(["6.4 %"], doc) == [])
    # ⚠⚠ LA sonde qui compte : le garde doit ECHOUER sur un chiffre faux. Sans elle, un
    # garde qui rendrait toujours « trouve » passerait pour une protection.
    v("un chiffre FAUX n'est pas trouvé", ou_trouve(["6,5 %"], doc) == [])
    v("... ni un chiffre absent", ou_trouve(["99,9 %"], doc) == [])
    v("aucun document, aucune trouvaille", ou_trouve(["6,4 %"], {}) == [])

    vieux = {_P("perime.md"): normaliser("on a 43 batteries, 1272 controles ici")}
    d_ = perimee("45 batteries, 1322 controles", vieux)
    v("une valeur PÉRIMÉE est localisée", len(d_) == 1 and "perime.md:1" in d_[0], str(d_))
    # ⚠⚠⚠ ET LE CONTROLE DE LA TROISIEME OCCURRENCE : un motif qui n'est qu'un nombre et une
    # UNITE ne peut accuser personne, parce que des dizaines de quantites partagent cette forme.
    # Payé sur le HANDOFF, qui se voyait reprocher une valeur du tiers MILIEU alors qu'il citait
    # correctement celle du tiers COEUR.
    unites = {_P("u.md"): normaliser("le plus proche voisin rend **270,8 µm** au coeur")}
    v("un motif qui n'est qu'un nombre et une unité n'accuse personne",
      perimee("**276,9 µm**", unites) == [], str(perimee("**276,9 µm**", unites)))
    v("... ni en pourcentage", perimee("**42,0 %**", {_P("u.md"): normaliser("il en reste 17,5 %")})
      == [])
    # ⚠⚠⚠ NI UN CONNECTEUR, ce qui est la forme qui a accuse un bloc fraichement ecrit : « X a
    # Y », « N fois », « N partout », « N paires sur M » sont des formes que toutes les phrases
    # de mesure du depot partagent.
    for forme, texte in (("0,55 % à 86,00 %", "de 5 % à 30 % de remplissage toléré"),
                         ("1,195 fois", "il est 77 fois plus grand"),
                         ("0 partout", "on lit 404 partout"),
                         ("51 paires sur 105", "il reste 2 paires sur 3"),
                         ("052 à 095", "une demi-feuille de 82 à 91")):
        v(f"... ni « {forme} », qui ne nomme aucune quantité",
          perimee(forme, {_P("c.md"): normaliser(texte)}) == [],
          str(perimee(forme, {_P("c.md"): normaliser(texte)})))
    # ⭐ Mais un motif qui porte le NOM de la quantité accuse toujours, sinon la garde serait
    # devenue incapable de signaler ce qu'elle existe pour signaler.
    # ⚠⚠⚠ ET UN SEUL NOM DE QUANTITE NE SUFFIT PAS : `N segments` est partage par le compte de
    # la table du champ et par celui des segments de `Scroll1`, et aucun apparieur textuel ne
    # peut les distinguer. Payé sur le HANDOFF, accusé à tort.
    # ⚠⚠⚠ ET L'ARBITRAGE EST MESURE ET PUBLIE, POUR QU'IL NE SOIT PAS RE-DESSERRE PAR ACCIDENT.
    # Resserrer la specificite tue presque le diagnostic PERIME : mesure sur les chiffres
    # enregistres, SEULS 15 SUR 568 portent un motif capable d'accuser. Deux lectures s'opposent
    # et il faut choisir la bonne :
    #
    #   - avant : le diagnostic tirait sur ~97 % des chiffres, et sur un seul document les SIX
    #     accusations etaient FAUSSES ;
    #   - apres : il tire sur 3 %, et aucune n'est fausse.
    #
    # ⭐ CE QUI TRANCHE EST QU'« ABSENT » EST LA DETECTION, ET IL EST INTACT. Un document qui ne
    # cite pas la valeur courante est signale ABSENT quoi qu'il arrive ; PERIME n'ajoute que OU
    # vit l'ancienne valeur, c'est-a-dire une commodite. Perdre cette commodite sur 97 % des
    # chiffres coute du confort ; garder six fausses accusations coute la CREDIBILITE du garde,
    # et ce fichier l'a deja paye deux fois — « un garde qui crie a tort finit ignore ».
    # ⚠ Donc : ne PAS assouplir `perimee` en constatant son silence. Le silence est le prix
    # choisi, et le compte ci-dessous le rend visible plutot qu'a redecouvrir.
    tous = collecter(_P("."))
    peut_accuser = 0
    for _n, ecr, _s in tous:
        faux = re.sub(r"[0-9]", "9", ecr[0])
        if faux == ecr[0]:
            continue
        if perimee(ecr[0], {_P("x.md"): normaliser(faux)}):
            peut_accuser += 1
    v("le prix du resserrement est MESURÉ et publié, pas subi",
      peut_accuser < len(tous) // 4,
      f"{peut_accuser} motifs sur {len(tous)} peuvent accuser — ABSENT, lui, reste intact")
    v("... et le diagnostic n'est pas mort pour autant", peut_accuser >= 5,
      f"{peut_accuser} motifs restent capables d'accuser")

    v("un motif d'un SEUL nom de quantité n'accuse personne",
      perimee("79 segments", {_P("s.md"): normaliser("sur Scroll1, 80 segments à 128 px")})
      == [])
    nomme = {_P("n.md"): normaliser("le desaccord au plan vaut 99,9 µm au coeur")}
    d2 = perimee("le desaccord au plan vaut 121,7 µm au coeur", nomme)
    v("... alors qu'un motif qui NOMME la quantité accuse encore",
      len(d2) == 1 and "n.md:1" in d2[0], str(d2))
    v("... et l'ancienne valeur est citée", "43 batteries" in d_[0])
    # ⚠ Un motif qui n'est QUE des chiffres matcherait n'importe quel nombre du depot.
    v("un chiffre nu ne déclenche pas de diagnostic périmé", perimee("1322", vieux) == [])
    # ⚠⚠ Ni un motif sans LETTRE : « 0 / 4 » et « 0 / 1 » ont la meme forme, et le garde a
    # accuse un document qui parlait d'autre chose. Deuxieme faux positif du meme fichier.
    v("un motif sans lettre non plus",
      perimee("0 / 4", {_P("x.md"): normaliser("accords 0 / 1 ici")}) == [])
    # ⚠⚠⚠ CE CONTROLE A DU ETRE RESSERRE, ET C'EST UNE CORRECTION DE SA PREMISSE. Il exigeait
    # qu'une SEULE lettre suffise a accuser — c'etait la lecon de la deuxieme occurrence, et la
    # cinquieme a montre qu'elle etait trop faible : un motif d'un seul nom de quantite
    # (« accords N », « N segments », « N fois ») est partage par des quantites differentes, et
    # produisait CINQ fausses accusations sur un seul document. L'intention du controle est
    # conservee — un motif specifique doit encore accuser — mais la barre est desormais DEUX
    # noms, ce qui est ce que la mesure impose.
    v("... alors qu'avec deux mots nommants le diagnostic revient",
      len(perimee("accords mesures 0 / 4",
                  {_P("x.md"): normaliser("accords mesures 0 / 1 ici")})) == 1)
    v("... mais un seul mot nommant ne suffit plus, et c'est mesuré",
      perimee("accords 0 / 4", {_P("x.md"): normaliser("accords 0 / 1 ici")}) == [])
    v("un document qui n'en parle pas n'est pas accusé",
      perimee("45 batteries, 1322 controles", {_P("autre.md"): "rien"}) == [])
    # ⚠ Et le controle du controle : la meme valeur presente ne doit PAS etre dite perimee.
    memes = {_P("a.md"): normaliser("45 batteries, 1322 controles")}
    v("une valeur À JOUR n'est pas signalée périmée",
      perimee("45 batteries, 1322 controles", memes) == [])

    # ⚠⚠ L'inventaire des documents non gardes. Sa sonde porte sur le cas qui n'est pas
    # evident : un document SANS chiffre ne doit pas y figurer, sinon le garde crie sur des
    # pages de prose qui ont raison -- et un garde qui crie a tort finit ignore.
    att = [("x", ["6,4 %"], "src.json")]
    trois = {_P("garde.md"): normaliser("le taux vaut 6,4 %"),
             _P("nu.md"): normaliser("on a mesuré 999 choses"),
             _P("prose.md"): normaliser("aucun nombre ici")}
    sg = documents_sans_garde(att, trois)
    v("un document dont un chiffre est gardé n'est pas listé", "garde.md" not in sg)
    v("un document qui cite des nombres non gardés est listé", "nu.md" in sg)
    v("... et un document SANS chiffre ne l'est pas", "prose.md" not in sg, str(sg))
    # ⚠⚠ La contradiction que `unites` resout : un chiffre court est ecarte par
    # `discriminante` (« 5,6 » avait ete faussement trouve), mais l article peut EXIGER
    # ce chiffre -- et alors il est requis et incontrolable a la fois, donc l echec ne se
    # repare pas en ecrivant le nombre. Avec son unite il redevient cherchable.
    v("un chiffre court n'est pas discriminant", not discriminante("1,81"))
    v("... mais il l'est avec son unité", discriminante("1,81 Go"))
    v("... et l'écriture anglaise aussi", discriminante("1.81 GB"))

    v("sans aucun chiffre attendu, tout document chiffré est listé",
      documents_sans_garde([], trois) == ["garde.md", "nu.md"])

    # ⚠⚠ Le registre des sources : sans lui, une mesure rangée ailleurs rend ce contrôle
    # PLUS VERT, puisque chaque lecture est gardée par `if p.exists():`. La sonde doit donc
    # prouver les deux sens — qu'il compte ce qu'il cherche, et qu'il sait dire « absente ».
    with tempfile.TemporaryDirectory() as d:
        vide = _P(d)
        collecter(vide)
        cherchees, absentes = len(_SOURCES), sources_manquantes()
    v("collecter enregistre les mesures qu'il cherche", cherchees >= 40, str(cherchees))
    v("... et sur un arbre vide, il les dit TOUTES absentes",
      len(absentes) == cherchees, f"{len(absentes)} sur {cherchees}")
    reel = collecter(RACINE)
    v("... alors que sur ce dépôt il les trouve", sources_manquantes() == [],
      ", ".join(sources_manquantes()[:4]))
    v("... et le registre est remis à zéro entre deux appels", len(_SOURCES) == cherchees,
      f"{len(_SOURCES)} contre {cherchees}")
    v("le dépôt fournit bien des chiffres à vérifier", len(reel) > 100, str(len(reel)))

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    # ⚠⚠⚠ Le verdict imprimait « ALL PASS » et rendait 0 INCONDITIONNELLEMENT :
    # cette batterie était verte quoi que disent ses contrôles. Trente-neuf
    # fichiers du dépôt portaient le même défaut, corrigé le 2026-08-27.
    print(f"{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifier que les chiffres d'un document viennent bien de leurs fichiers.")
    parser.add_argument("documents", type=Path, nargs="*")
    parser.add_argument("--verifier", action="store_true",
                        help="le garde-fou se garde lui-même, hors ligne")
    parser.add_argument("--racine", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--soumission", type=Path,
                        help="document qui PART : les chiffres de "
                             "CITES_PAR_LA_SOUMISSION doivent apparaitre dans CELUI-LA, "
                             "et pas seulement quelque part dans le depot")
    parser.add_argument("--article", type=Path,
                        help="l'article : les chiffres de CITES_PAR_L_ARTICLE doivent "
                             "apparaitre dans CELUI-LA")
    # ⚠⚠ Mode ARBRE RESTREINT. Sur la branche de release, la plupart des documents citants
    # ne sont pas livres : sans ce drapeau le controle echouerait pour la seule raison
    # qu il s agit d une release, et un controle qui ne peut pas passer cesse d etre lu.
    # ⚠ Les listes exigees par la soumission et l article restent DURES.
    parser.add_argument("--hors-perimetre", action="store_true",
                        help="arbre restreint : un chiffre dont le document citant n'est "
                             "pas livre est compte hors perimetre, pas en echec")
    parser.add_argument("--minimum", type=int, default=8,
                        help="nombre minimal de chiffres recalculables ET DISCRIMINANTS. "
                             "⚠ Le plancher porte sur les discriminants, sinon il se "
                             "laisserait satisfaire par des controles incapables "
                             "d'echouer. En dessous, on "
                             "REFUSE au lieu de passer au vert : un fichier de resultat "
                             "absent ferait sinon un controle qui ne verifie rien")
    args = parser.parse_args()
    if args.verifier:
        return verifier()
    if not args.documents:
        parser.error("donner au moins un document, ou --verifier")

    attendus = collecter(args.racine)
    # ⚠⚠ Le dire AVANT le reste : une mesure absente ne fait pas échouer ce contrôle, elle
    # lui retire des chiffres à vérifier. Sans cette ligne, ranger un fichier de mesure rend
    # la sortie plus verte.
    absentes = sources_manquantes()
    if absentes:
        print(f"⚠ {len(absentes)} mesure(s) cherchée(s) et NON TROUVÉE(S) dans "
              f"{DOSSIER_MESURES}/ — les chiffres qu'elles portent ne sont vérifiés par "
              f"personne :")
        for n in absentes:
            print(f"    {n}")
        print()
    # ⚠⚠ LE TROU QU'IL FAUT BOUCHER : si un fichier de résultat manque, `collecter` le
    # saute en silence et le contrôle passe au vert en n'ayant presque rien vérifié.
    # C'est exactement la vérification incapable d'échouer que ce dépôt a déjà payée
    # (`validate.sh` enregistrait « no new warnings » sur un build mort avant sa première
    # compilation). Un plancher explicite transforme l'absence en échec.
    faibles = [a for a in attendus if not any(discriminante(e) for e in a[1])]
    attendus = [a for a in attendus if any(discriminante(e) for e in a[1])]
    if len(attendus) < args.minimum:
        print(f"seulement {len(attendus)} chiffres recalculables (plancher "
              f"{args.minimum}) — un fichier de resultat manque, donc ce controle "
              f"ne verifierait presque rien", file=sys.stderr)
        return 2

    textes = {d: normaliser(d.read_text()) for d in args.documents if d.exists()}
    if not textes:
        print("aucun document lisible", file=sys.stderr)
        return 1

    print(f"{len(attendus)} chiffres recalcules et DISCRIMINANTS, cherches dans "
          f"{len(textes)} document(s)\n")
    print(f"{'chiffre':>32} {'attendu':>16} {'source':>28}  ou")
    manquants = 0
    hors = 0
    hors_perimetre = args.hors_perimetre
    for nom, ecritures, source in attendus:
        trouve = ou_trouve(ecritures, textes)
        if trouve:
            print(f"{nom:>32} {ecritures[0]:>16} {source:>28}  ✅ {', '.join(trouve)}")
        else:
            # ⚠⚠ Sur un arbre RESTREINT (la branche de release), un chiffre recalcule dont le
            # document citant n est pas livre n est pas une panne : il est HORS PERIMETRE.
            # Sans cette distinction, la release echouerait pour la seule raison qu elle est
            # une release -- et un controle qui ne peut pas passer cesse d etre lu.
            # ⚠ Les listes `exiger` (soumission, article) restent DURES : ce que le document
            # livre cite doit y etre, sinon la promesse « chaque nombre est verifiable »
            # tombe precisement la ou elle compte.
            if hors_perimetre:
                hors += 1
            else:
                manquants += 1
            # ⚠⚠ Le chemin d'ERREUR supposait toujours DEUX ecritures et levait un
            # IndexError sur une entree qui n'en a qu'une -- donc le garde-fou plantait
            # exactement au moment ou il avait quelque chose a signaler, et n'imprimait
            # jamais le reste de la table. Trouve le 2026-08-20 en lui ajoutant des
            # chiffres a ecriture unique.
            autres = ecritures[1:]
            suffixe = (f" — accepte aussi {', '.join('« ' + e + ' »' for e in autres)}"
                       if autres else "")
            vieilles = perimee(ecritures[0], textes)
            etat = "PERIME" if vieilles else "ABSENT"
            print(f"{nom:>32} {ecritures[0]:>16} {source:>28}  ⚠ {etat}{suffixe}")
            # ⭐ Dire OU vit l'ancienne valeur transforme une chasse au grep en un
            # remplacement. C'est la difference entre « ce chiffre manque » et « ce
            # document se trompe, ligne 353 ».
            for v in vieilles[:3]:
                print(f"{'':>32} {'':>16} {'':>28}    → {v}")

    # ⚠⚠ QUELS DOCUMENTS N'ONT AUCUN CHIFFRE SOUS GARDE. Le tableau ci-dessus dit ce qui
    # est verifie ; il ne dit rien de ce qui ne l'est pas. Un document plein de nombres dont
    # AUCUN n'est recalcule depuis un fichier de resultat publie des anecdotes au sens de la
    # regle de ce depot -- et rien ne le signalait. C'est ainsi que `04` a garde son
    # « U = 11 489 329 924 » sans producteur pendant des semaines.
    #
    # ⚠ « Aucun chiffre garde » n'est pas « mauvais document ». Une feuille de route, une
    # revue de litterature ou un registre de taches n'ont pas de mesure a garder. Le compte
    # est donc une LISTE a regarder, jamais un echec -- un garde qui echouerait la-dessus
    # crierait sur des documents qui ont raison.
    sans_garde = documents_sans_garde(attendus, textes)
    if sans_garde:
        print(f"\n⚠ {len(sans_garde)} document(s) citent des nombres dont AUCUN n'est "
              f"recalcule depuis un fichier de resultat — a regarder, pas un echec :")
        for n in sans_garde:
            print(f"    {n}")

    # ⚠⚠ Le TOTAL, imprime par l'outil et non compte a la main. `21` citait « 85 chiffres »,
    # un nombre exact le jour ou il a ete ecrit et faux depuis -- et le compter au grep
    # aurait produit un second nombre a la main, donc un second nombre a laisser vieillir.
    # Un chiffre publie dont le calcul n'est pas dans l'arbre est une anecdote.
    sources = {source for _, _, source in attendus}
    print(f"\n{len(attendus)} chiffres recalcules depuis {len(sources)} fichiers de resultat")

    if faibles:
        print(f"\n⚠ {len(faibles)} chiffre(s) NON VERIFIABLES par recherche litterale — "
              f"trop courts pour etre absents d'un texte en prose, donc ni reussite ni "
              f"echec. Les ecrire AVEC leur contexte les rendrait verifiables :")
        for nom, ecritures, source in faibles:
            print(f"    {nom:>40} = {ecritures[0]:<8} ({source})")

    def exiger(cible: Path, noms, quoi: str) -> int:
        """Ces chiffres-la doivent etre DANS ce document, pas seulement quelque part."""
        manque = 0
        cible = cible.resolve()
        t = normaliser(cible.read_text()) if cible.is_file() else None
        if t is None:
            print(f"\n⚠ {quoi} introuvable : {cible}", file=sys.stderr)
            return 1
        connus = {nom for nom, _, _ in attendus}
        # ⚠ Une entree nommee qui n'existe plus est un controle mort : le nom se
        # renomme et la liste cesse silencieusement de garder quoi que ce soit.
        orphelines = [n for n in noms if n not in connus]
        if orphelines:
            print(f"\n⚠ {len(orphelines)} entrée(s) nommée(s) ne correspondent à aucun "
                  f"chiffre recalculé — la liste est périmée :")
            for n in orphelines:
                print(f"    {n}")
            manque += len(orphelines)
        print(f"\n{len(noms) - len(orphelines)} chiffre(s) que {quoi} cite, cherchés "
              f"DANS {cible.name} :")
        for nom, ecritures, source in attendus:
            if nom not in noms:
                continue
            if any(normaliser(e) in t for e in ecritures):
                print(f"    {nom:>38}  ✅")
            else:
                manque += 1
                print(f"    {nom:>38}  ⚠ ABSENT — "
                      f"accepte {', '.join('« ' + e + ' »' for e in ecritures)}")
        return manque

    if args.soumission:
        manquants += exiger(args.soumission, CITES_PAR_LA_SOUMISSION, "le dossier")
    if args.article:
        manquants += exiger(args.article, CITES_PAR_L_ARTICLE, "l'article")

    print()
    if hors:
        print(f"ℹ {hors} chiffre(s) recalculé(s) n'apparaissent dans aucun document LIVRÉ. "
              f"Hors périmètre : leur document n'est pas dans cet arbre.")
    if manquants:
        print(f"⚠ {manquants} chiffre(s) recalcule(s) n'apparaissent nulle part. "
              f"Soit le document est perime, soit il ne cite pas ce chiffre — "
              f"les deux demandent un coup d'oeil.")
    elif hors:
        # ⚠ Le verdict doit dire SUR QUOI il porte. « Tous apparaissent » serait faux ici :
        # cent n apparaissent pas, ils sont hors perimetre. Un controle qui arrondit son
        # propre enonce apprend au lecteur a ne plus le lire.
        print(f"TOUS LES CHIFFRES DU PERIMETRE LIVRE APPARAISSENT "
              f"({hors} hors perimetre, non verifiables ici)")
    else:
        print("TOUS LES CHIFFRES RECALCULES APPARAISSENT DANS LES DOCUMENTS")
    return 1 if manquants else 0


if __name__ == "__main__":
    sys.exit(main())
