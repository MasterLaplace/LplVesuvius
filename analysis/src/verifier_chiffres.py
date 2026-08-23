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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from carte_segments import MEME_FEUILLE_UM, VOISINES_UM  # noqa: E402


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


def collecter(racine: Path) -> list[tuple[str, list[str], str]]:
    """(ce que c'est, écritures acceptables, d'où ça vient).

    ⚠ Plusieurs écritures par chiffre, parce qu'un même nombre s'écrit `+0,381` en
    français et `+0.381` en anglais, et que refuser l'une des deux ferait échouer le
    contrôle sur un document parfaitement juste.
    """
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

    p = racine / "docs" / "decision_avec_matiere.json"
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

    p = racine / "docs" / "croisement_encre.json"
    if p.exists():
        d = json.loads(p.read_text())
        for c in d.get("correlations", []):
            if c["trace"] == "avec_matiere" and c["encre"] == "encre_contraste_p90_p50":
                ajoute("rho avec_matiere x encre", c["rho"], 3, p.name, signe=True)
        for c in d.get("partielles", []):
            if c["trace"] == "ecart_a_la_trace" and c["encre"] == "encre_contraste_p90_p50":
                ajoute("partielle ecart x encre", c["rho_partiel"], 3, p.name, signe=True)

    p = racine / "docs" / "table_champ.json"
    if p.exists():
        d = json.loads(p.read_text())
        # ⚠ Avec son contexte : « 21,7 » nu est trop court pour etre absent d'un texte.
        out.append(("part rigide Scroll 1",
                    [f"{fr(d['part_rigide_mediane']*100,1)} %",
                     f"{en(d['part_rigide_mediane']*100,1)} %"], p.name))
        out.append(("segments du champ",
                    [f"{d['segments']} segments", f"{d['segments']} published"], p.name))

    p = racine / "docs" / "robustesse_material.json"
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("accord des grilles", d["rho"], 3, p.name, signe=True)
        ajoute("temoin p95 des grilles", d["temoin_p95"], 3, p.name)

    p = racine / "docs" / "prediction_50um.json"
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

    p = racine / "docs" / "table_graines.json"
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
    p = racine / "docs" / "table_tirages.json"
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

    p = racine / "docs" / "comparaison_cartes.json"
    if p.exists():
        d = json.loads(p.read_text())
        ajoute("rho entre les deux campagnes", d["rho"], 3, p.name, signe=True)
        out.append(("rangs changes",
                    [f"{d['rangs_changes']}/{len(d['lignes'])} rouleaux",
                     f"{d['rangs_changes']} of {len(d['lignes'])} scrolls",
                     f"{d['rangs_changes']} rouleaux changent"], p.name))

    p = racine / "docs" / "incertitude_carte.json"
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

    p = racine / "docs" / "sensibilite_maillage.json"
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
    p = racine / "docs" / "chaine_spires.json"
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
    p = racine / "docs" / "chaine_pas025_convergence.json"
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
    p = racine / "docs" / "geometrie_extension.json"
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
    verdicts = sorted((racine / "docs").glob("spire_*.json"))
    if verdicts:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tc", racine / "analysis" / "src" / "test_convergence.py")
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
    p = racine / "docs" / "comparaison_pas_rayon.json"
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
    p = racine / "docs" / "geometrie_pas025.json"
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
    p = racine / "docs" / "juge_a_un_rendu.json"
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
    p = racine / "docs" / "convergence.json"
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
    p = racine / "docs" / "mosaique_PHerc0172.json"
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
    p = racine / "docs" / "segments_PHerc1447.json"
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
    p = racine / "docs" / "comparaison_plafond.json"
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
    p = racine / "docs" / "typographie.json"
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
        q = racine / "docs" / f"second_axe_{prof}.json"
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
        q = racine / "docs" / fichier
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

    p = racine / "docs" / "paris4_2x2.json"
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
    for f in sorted(racine.glob("docs/resolution_g*.json")):
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
    pv = racine / "docs" / "plafond_ps256_c2_niv1.json"
    if pv.exists():
        d = json.loads(pv.read_text())
        for cle, nom in (("variation", "variation du plafond"),
                         ("bruit_de_tirage", "bruit de tirage du plafond")):
            if isinstance(d.get(cle), (int, float)):
                ajoute(nom, d[cle], 2, pv.name, signe=(cle == "variation"))

    # ⚠⚠ Le test du critere relatif. Le nombre qui compte n est pas un beta mais le COMPTE
    # de grandeurs lisibles en absolu : s il montait sans qu on ait ajoute de mesure, c est
    # qu un refus aurait cesse de refuser.
    p = racine / "docs" / "critere_relatif.json"
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

    p = racine / "docs" / "appui_de_pente.json"
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
        # ⚠⚠ Le chiffre qui porte tout `51` : combien de series rendent l IDENTITE de leur
        # couple de fenetres. Sans garde, il vieillirait en silence a la prochaine campagne.
        if d.get("series_sur_une_identite") is not None:
            out.append(("series sur l identite du couple de fenetres",
                        [str(d["series_sur_une_identite"])], p.name))
        for x in d.get("identites_du_couple_de_fenetres") or []:
            if x.get("colle_a_l_identite"):
                ajoute(f"alpha d identite {x['couches'][0]}c/{x['couches'][1]}c",
                       x["alpha"], 4, p.name)

    p = racine / "docs" / "fenetre_utilisable.json"
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

    p = racine / "docs" / "etalon_rendu.json"
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

    p = racine / "docs" / "paris4_candidats.json"
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

    p = racine / "docs" / "audit_profils.json"
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

    p = racine / "docs" / "excision_resume.json"
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

    p = racine / "docs" / "eligibilite_aval.json"
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

    p = racine / "docs" / "derive_profondeur.json"
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

    p = racine / "docs" / "temoin_negatif.json"
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

    p = racine / "docs" / "temoins.json"
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("batteries de temoins",
                    [f"{d['batteries_all_pass']} batteries, {d['controles']} controles",
                     f"{d['batteries_all_pass']} batteries, {d['controles']} contrôles"],
                    p.name))
        if d.get("chiffres_recalcules"):
            out.append(("chiffres recalcules par le garde-fou",
                        [f"{d['chiffres_recalcules']} chiffres",
                         f"**{d['chiffres_recalcules']} chiffres**"], p.name))

    p = racine / "docs" / "cout_echelle.json"
    if p.exists():
        d = json.loads(p.read_text())
        for ligne in (d if isinstance(d, list) else d.get("rouleaux", [])):
            if ligne.get("rouleaux") == 800:
                ajoute("heures pour 800 rouleaux, 16 fils",
                       ligne["heures_1_fil"] / 8.35, 1, p.name)
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

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


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
