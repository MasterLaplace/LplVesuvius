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
    v("... et l'ancienne valeur est citée", "43 batteries" in d_[0])
    # ⚠ Un motif qui n'est QUE des chiffres matcherait n'importe quel nombre du depot.
    v("un chiffre nu ne déclenche pas de diagnostic périmé", perimee("1322", vieux) == [])
    # ⚠⚠ Ni un motif sans LETTRE : « 0 / 4 » et « 0 / 1 » ont la meme forme, et le garde a
    # accuse un document qui parlait d'autre chose. Deuxieme faux positif du meme fichier.
    v("un motif sans lettre non plus",
      perimee("0 / 4", {_P("x.md"): normaliser("accords 0 / 1 ici")}) == [])
    v("... alors qu'avec une lettre le diagnostic revient",
      len(perimee("accords 0 / 4", {_P("x.md"): normaliser("accords 0 / 1 ici")})) == 1)
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
