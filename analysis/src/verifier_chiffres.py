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

    def ajoute(nom: str, valeur: float, n: int, source: str, signe: bool = False):
        s = "+" if (signe and valeur >= 0) else ""
        out.append((nom, [s + fr(valeur, n), s + en(valeur, n)], source))

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
                         f"{d['planarite_au_plafond']} sur {d['rouleaux']} butent"],
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
    p = racine / "docs" / "temoins.json"
    if p.exists():
        d = json.loads(p.read_text())
        out.append(("batteries de temoins",
                    [f"{d['batteries_all_pass']} batteries, {d['controles']} controles",
                     f"{d['batteries_all_pass']} batteries, {d['controles']} contrôles"],
                    p.name))

    p = racine / "docs" / "cout_echelle.json"
    if p.exists():
        d = json.loads(p.read_text())
        for ligne in (d if isinstance(d, list) else d.get("rouleaux", [])):
            if ligne.get("rouleaux") == 800:
                ajoute("heures pour 800 rouleaux, 16 fils",
                       ligne["heures_1_fil"] / 8.35, 1, p.name)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifier que les chiffres d'un document viennent bien de leurs fichiers.")
    parser.add_argument("documents", type=Path, nargs="+")
    parser.add_argument("--racine", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--soumission", type=Path,
                        help="document qui PART : les chiffres de "
                             "CITES_PAR_LA_SOUMISSION doivent apparaitre dans CELUI-LA, "
                             "et pas seulement quelque part dans le depot")
    parser.add_argument("--minimum", type=int, default=8,
                        help="nombre minimal de chiffres recalculables ET DISCRIMINANTS. "
                             "⚠ Le plancher porte sur les discriminants, sinon il se "
                             "laisserait satisfaire par des controles incapables "
                             "d'echouer. En dessous, on "
                             "REFUSE au lieu de passer au vert : un fichier de resultat "
                             "absent ferait sinon un controle qui ne verifie rien")
    args = parser.parse_args()

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
    for nom, ecritures, source in attendus:
        trouve = [d.name for d, t in textes.items()
                  if any(normaliser(e) in t for e in ecritures)]
        if trouve:
            print(f"{nom:>32} {ecritures[0]:>16} {source:>28}  ✅ {', '.join(trouve)}")
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
            print(f"{nom:>32} {ecritures[0]:>16} {source:>28}  ⚠ ABSENT "
                  f"(ou perime){suffixe}")

    if faibles:
        print(f"\n⚠ {len(faibles)} chiffre(s) NON VERIFIABLES par recherche litterale — "
              f"trop courts pour etre absents d'un texte en prose, donc ni reussite ni "
              f"echec. Les ecrire AVEC leur contexte les rendrait verifiables :")
        for nom, ecritures, source in faibles:
            print(f"    {nom:>40} = {ecritures[0]:<8} ({source})")

    if args.soumission:
        cible = args.soumission.resolve()
        t = normaliser(cible.read_text()) if cible.is_file() else None
        if t is None:
            print(f"\n⚠ document de soumission introuvable : {cible}", file=sys.stderr)
            manquants += 1
        else:
            connus = {nom for nom, _, _ in attendus}
            # ⚠ Une entree nommee qui n'existe plus est un controle mort : le nom se
            # renomme et la liste cesse silencieusement de garder quoi que ce soit.
            orphelines = [n for n in CITES_PAR_LA_SOUMISSION if n not in connus]
            if orphelines:
                print(f"\n⚠ {len(orphelines)} entrée(s) de CITES_PAR_LA_SOUMISSION ne "
                      f"correspondent à aucun chiffre recalculé — la liste est périmée :")
                for n in orphelines:
                    print(f"    {n}")
                manquants += len(orphelines)
            print(f"\n{len(CITES_PAR_LA_SOUMISSION) - len(orphelines)} chiffre(s) que le "
                  f"corps de {cible.name} cite, cherchés DANS CE DOCUMENT :")
            for nom, ecritures, source in attendus:
                if nom not in CITES_PAR_LA_SOUMISSION:
                    continue
                if any(normaliser(e) in t for e in ecritures):
                    print(f"    {nom:>36}  ✅")
                else:
                    manquants += 1
                    print(f"    {nom:>36}  ⚠ ABSENT de la soumission — "
                          f"accepte {', '.join('« ' + e + ' »' for e in ecritures)}")

    print()
    if manquants:
        print(f"⚠ {manquants} chiffre(s) recalcule(s) n'apparaissent nulle part. "
              f"Soit le document est perime, soit il ne cite pas ce chiffre — "
              f"les deux demandent un coup d'oeil.")
    else:
        print("TOUS LES CHIFFRES RECALCULES APPARAISSENT DANS LES DOCUMENTS")
    return 1 if manquants else 0


if __name__ == "__main__":
    sys.exit(main())
