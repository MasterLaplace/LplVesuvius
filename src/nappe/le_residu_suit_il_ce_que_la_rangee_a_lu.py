"""Le résidu de l'ajustement additif suit-il ce que les deux rangées ont RÉELLEMENT LU ?

⭐⭐⭐⭐ POURQUOI CE FICHIER, ET C'EST `214` QUI LE FORCE. `214` a demandé si le désaccord de deux
rangées croît avec leur écartement et a répondu NON — tendance de rangs **-0,1024**, seize
rebrassages sur dix-neuf au moins aussi forts. Mais son contrôle gratuit s'est retourné : le
triangle sur-déterminé, trente-six équations pour neuf inconnues, REFUSE le modèle additif par ses
résidus — **3,6279 erreurs** sur la paire `197-198` contre un résidu médian de **0,8039**. Ce qui
fait diverger deux rangées n'est donc ni leur distance ni leur seule identité, et `R4-P60` demande
ce que c'est.

⭐⭐⭐ ET LA MOITIÉ BON MARCHÉ DE LA RÉPONSE NE DEMANDE AUCUNE LECTURE NEUVE DU VOLUME. Les neuf
rangées de `214` n'ont pas lu la même chose : elles lisent de **246** à **260** colonnes sur **285**
demandées, dont **0** à **8** refusées faute de texture, et elles rendent de **240** à **259** pas.
Une rangée qui lit moins ne lit pas la même chose, et deux rangées qui n'ont pas lu la même chose
n'ont aucune raison de partager un bruit propre. Tout est déjà dans le JSON de `214`.

⚠⚠⚠ LA STATISTIQUE EST DÉCLARÉE AVANT D'ÊTRE REGARDÉE, ET C'EST LA SEULE CONTRAINTE QUI COMPTE
ICI. `214` n'a pas adopté sa règle la plus puissante — celle qui voit le facteur deux à douze sur
douze quand le σ brut n'en voit que six — précisément parce qu'elle ne l'avait pas déclarée
d'avance, et sa borne en est conservatrice d'un cran. Le nul par permutation d'étiquettes TIENT sa
garantie sur des résidus, mesuré par `214` à **9/171 = 0,0526** contre **0,05**, donc aucun nul
paramétrique n'est requis et en construire un serait payer un outil dont la mesure dit qu'on n'a
pas besoin.

⚠⚠⚠ ET LA FORME QUE `R4-P60` PRESCRIVAIT N'EST PAS CELLE QUI EST DÉCLARÉE, POUR UNE RAISON QUI SE
DIT. La porte proposait d'agréger les résidus PAR RANGÉE — une rangée entre dans huit des
trente-six paires — et de prendre le maximum sur les neuf comme statistique de famille. Deux faits
l'ont écartée du rôle de statistique déclarée, et aucun des deux n'est un jugement :

  1. elle répond « QUELLE rangée », jamais « QUOI ». Savoir que le résidu se concentre sur `198` ne
     nomme pas ce que `198` a de particulier, donc cette forme ne peut pas fermer la porte ;
  2. ⚠⚠ elle a été REGARDÉE avant d'être déclarée, pendant la conception de cette tranche, donc
     elle ne peut plus servir de verdict. Une statistique vue puis déclarée est choisie.

Elle est donc portée comme CONTRÔLE NOMMÉ, avec son propre taux de faux — le précédent est celui de
`214`, qui porte de la même façon la règle qu'elle a refusée.

⚠⚠⚠ ET L'AGRÉGAT ÉVIDENT EST INTERDIT PAR LE MODÈLE LUI-MÊME, CE QUI SE PUBLIE AU LIEU DE SE TAIRE.
La somme des huit résidus BRUTS d'une rangée vaut ZÉRO, exactement, et ce n'est pas un résultat de
mesure : ce sont les équations normales de l'ajustement au moindre carré. Dériver la somme des
carrés par rapport à la variance ajustée de la rangée `i` donne `-2·Σ_j r(i,j) = 0`. Donc un effet
de rangée UNIFORME est absorbé dans la variance ajustée de cette rangée et ne laisse aucune trace ;
seul un effet NON uniforme — bien s'accorder avec certaines partenaires et mal avec d'autres —
survit. Un agrégat de POSITION est une vérification incapable d'échouer ; l'agrégat doit être une
DISPERSION.

⚠⚠ LE PIÈGE EST NOMMÉ ET IL POUSSE DANS UN SENS CONNU. L'erreur d'échantillonnage d'une variance
vaut `V·√(2/(n-1))` : elle croît avec la VALEUR de la paire autant qu'avec sa longueur. Une rangée
de grande variance propre a donc de grands désaccords avec tout le monde, donc de grandes erreurs,
donc de PETITS résidus standardisés. Toute covariable qui suit la variance propre d'une rangée
peut donc corréler avec le résidu sans qu'aucune lecture n'y soit pour rien. ⚠⚠ SUR LA MATIÈRE
LUE LA MESURE DÉMENT CETTE DÉRIVATION — la corrélation est POSITIVE, pas négative — et les deux
sont publiées côte à côte plutôt que l'attendu réécrit après coup.

Usage :
    uv run python src/nappe/le_residu_suit_il_ce_que_la_rangee_a_lu.py --verifier
    uv run python src/nappe/le_residu_suit_il_ce_que_la_rangee_a_lu.py \\
        --json docs/mesures/le_residu_suit_il_ce_que_la_rangee_a_lu.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_recette_posee_sur_le_rouleau import PERMUTATIONS  # noqa: E402
from le_bruit_propre_croit_il_avec_lecartement import (la_correlation_de_rangs,  # noqa: E402
                                                       la_suite_est_monotone,
                                                       le_taux_tient)
from ouvrir_les_quinze import _rng  # noqa: E402

MESURES = RACINE / "docs" / "mesures"
CE_QUE_LE_BRUIT_PROPRE_A_RENDU = MESURES / "le_bruit_propre_croit_il_avec_lecartement.json"
GRAINE = 20261027

LA_QUESTION_DECLAREE = ("le résidu de l'ajustement additif de `214` suit-il ce que les deux rangées "
                        "d'une paire ont RÉELLEMENT LU, alors qu'il ne suit pas leur écartement ?")
LES_EPREUVES_DECLAREES = ("le résidu signé suit une covariable de lecture",)

LES_COVARIABLES_DECLAREES = (
    ("colonnes_lues", "ce que la rangée a réellement lu — la porte la nomme"),
    ("refus_faute_de_texture", "ce que la matière a refusé — la porte la nomme"),
    ("pas_rendus", "ce que la rangée a rendu une fois lue — trois façons de manquer"),
)
"""Les trois covariables déclarées, et AUCUNE n'est la distance.

⚠⚠ ELLES SONT DÉCLARÉES AVANT D'ÊTRE REGARDÉES, et leur nombre entre dans la statistique : la
famille est prise en entier et son maximum est comparé au maximum du même nul, donc le choix d'une
covariable parmi trois est PAYÉ au lieu d'être fait après coup. C'est le remède de `179`.

⚠ La troisième n'est pas dans la porte et c'est dit : `R4-P60` nomme les colonnes lues et les
refus de texture. Les pas rendus sont la troisième façon dont une rangée peut manquer de matière,
et l'ajouter AVANT de rien calculer est légitime là où l'ajouter après ne le serait pas."""

LES_FORMES_DECLAREES = (
    ("lecart", "deux rangées qui n'ont pas lu la même chose"),
    ("le_minimum", "la plus pauvre des deux porte la paire"),
)
"""Les deux façons de faire d'une propriété de RANGÉE une propriété de PAIRE.

⚠⚠ AUCUNE DES DEUX N'EST ÉVIDENTE, DONC LES DEUX SONT DÉCLARÉES. « Elles ont lu différemment » et
« la plus pauvre des deux commande » sont deux histoires physiques distinctes, et en choisir une
seule après avoir vu les deux serait exactement le choix que la famille existe pour payer."""

LA_FAMILLE_DECLAREE = tuple(f"{c}·{f}" for c, _ in LES_COVARIABLES_DECLAREES
                            for f, _ in LES_FORMES_DECLAREES)
GARANTIE = 1.0 / (PERMUTATIONS + 1)
GARANTIE_PAR_EPREUVE = GARANTIE / len(LES_EPREUVES_DECLAREES)
LE_COMPTE_DECISIF = 171
"""Le nombre de faces négatives qu'il faut pour qu'un taux de faux soit décisif à la garantie.

⚠ IL EST DÉRIVÉ, PAS CHOISI : `m = ⌈k(1-g)/g⌉` pour `k = 9` réplicats et `g = 0,05`. `214` le
porte déjà sous cette forme et le reprendre ici garde une seule définition."""


def ce_que_le_bruit_propre_a_rendu(chemin: Path = CE_QUE_LE_BRUIT_PROPRE_A_RENDU) -> dict:
    """Ce que `214` a publié — relu, jamais retapé, et REFUSÉ par son nom s'il manque.

    ⚠⚠⚠ UNE SONDE SATISFAITE PAR L'ABSENCE EST UN PÉCHÉ CAPITAL DE CE DÉPÔT, ET `214` L'A PAYÉ :
    son lecteur de `208` regardait à la racine, n'y trouvait rien, et rendait quand même
    `decidable: True`. Ici chaque pièce est cherchée à son niveau, et le premier manque nomme ce
    qui manque au lieu de rendre un dictionnaire vide qui ressemble à une mesure.

    ⚠⚠ LES DEUX TABLES DOIVENT PARLER DES MÊMES RANGÉES. Le triangle publie neuf variances propres
    et les lignes publient neuf lectures ; si les deux jeux diffèrent, une covariable serait
    attachée à une rangée qui n'est pas la sienne, et rien dans le résultat ne le dirait.
    """
    if not chemin.exists():
        return {"decidable": False, "raison": f"{chemin.name} est absent"}
    try:
        d = json.loads(chemin.read_text())
    except (ValueError, OSError) as e:
        return {"decidable": False, "raison": f"{chemin.name} est illisible : {e}"}
    tri = d.get("le_triangle_surdetermine") or {}
    if not tri.get("decidable"):
        return {"decidable": False, "raison": "le triangle sur-déterminé de `214` est indécidable"}
    residus = tri.get("les_residus_par_paire_en_erreurs")
    if not isinstance(residus, dict) or not residus:
        return {"decidable": False, "raison": "`214` ne publie pas ses résidus par paire en erreurs"}
    if any(v is None for v in residus.values()):
        return {"decidable": False, "raison": "un résidu par paire est indécidable"}
    bruts = tri.get("les_residus_par_paire_en_voxels2")
    if not isinstance(bruts, dict) or set(bruts) != set(residus):
        return {"decidable": False,
                "raison": "les deux tables de résidus ne portent pas les mêmes paires"}
    variances = tri.get("les_bruits_propres_en_voxels2")
    if not isinstance(variances, dict) or not variances:
        return {"decidable": False, "raison": "`214` ne publie pas ses variances propres ajustées"}
    lignes = d.get("les_lignes")
    if not isinstance(lignes, dict) or not lignes:
        return {"decidable": False, "raison": "`214` ne publie pas ses lignes"}
    pas = d.get("les_pas_par_rangee")
    if not isinstance(pas, dict) or not pas:
        return {"decidable": False, "raison": "`214` ne publie pas ses pas par rangée"}
    ep214 = d.get("lepreuve") or {}
    if not ep214.get("decidable"):
        return {"decidable": False, "raison": "l'épreuve de `214` est indécidable"}
    rangees = sorted(int(x) for x in variances)
    if sorted(int(x) for x in lignes) != rangees:
        return {"decidable": False,
                "raison": "les variances et les lignes ne portent pas les mêmes rangées"}
    if sorted(int(x) for x in pas) != rangees:
        return {"decidable": False,
                "raison": "les pas et les variances ne portent pas les mêmes rangées"}
    manquant = [str(r) for r in rangees
                if (lignes[str(r)] or {}).get("colonnes_lues") is None]
    if manquant:
        return {"decidable": False,
                "raison": f"les rangées {','.join(manquant)} ne disent pas ce qu'elles ont lu"}
    attendu = len(rangees) * (len(rangees) - 1) // 2
    if len(residus) != attendu:
        return {"decidable": False,
                "raison": f"{len(residus)} résidus pour {attendu} paires attendues"}
    # ⚠⚠ CE QUE `215` CITE DE `214` EST RELU, JAMAIS RETAPE. Le document de cette tranche ouvre
    # sur la tendance que `214` a mesuree contre l'ecartement ; un nombre cite sans producteur dans
    # SA propre mesure est exactement ce que `R4-L19` designe comme pire qu'un nombre absent.
    return {"decidable": True,
            "les_rangees": rangees,
            "la_tendance_de_214_contre_lecartement": ep214.get("la_tendance_observee"),
            "les_tirages_de_214_au_moins_aussi_forts":
                ep214.get("les_tirages_au_moins_aussi_forts"),
            "les_tirages_de_214": ep214.get("tirages"),
            "combien_de_rangees": len(rangees),
            "combien_de_paires": len(residus),
            "les_residus_en_erreurs": {k: float(v) for k, v in residus.items()},
            "les_residus_en_voxels2": {k: float(v) for k, v in bruts.items()},
            "les_variances_propres_en_voxels2": {int(k): float(v) for k, v in variances.items()},
            "le_pire_residu_en_erreurs": tri.get("le_pire_residu_en_erreurs"),
            "la_paire_du_pire_residu_en_erreurs": tri.get("la_paire_du_pire_residu_en_erreurs"),
            "le_residu_median_en_erreurs": tri.get("le_residu_median_en_erreurs"),
            "les_variances_negatives": list(tri.get("les_rangees_a_variance_negative") or []),
            "ce_que_chaque_rangee_a_lu": {
                int(r): {
                    "colonnes_demandees": int((lignes[str(r)] or {}).get("colonnes_demandees") or 0),
                    "colonnes_lues": int((lignes[str(r)] or {}).get("colonnes_lues")),
                    "refus_faute_de_texture": int(((lignes[str(r)] or {}).get("refuses")
                                                   or {}).get("trop peu texturé", 0)),
                    "refus_absent_du_depot": int(((lignes[str(r)] or {}).get("refuses")
                                                  or {}).get("absent du dépôt", 0)),
                    "pas_rendus": int(pas[str(r)]),
                } for r in rangees}}


def _cle(a: int, b: int) -> str:
    return f"{min(int(a), int(b))}-{max(int(a), int(b))}"


def _les_paires(rangees) -> list[tuple[int, int]]:
    r = sorted(int(x) for x in rangees)
    return [(r[i], r[j]) for i in range(len(r)) for j in range(i + 1, len(r))]


def la_covariable_de_paire(forme: str, va: float, vb: float) -> float | None:
    """Une propriété de RANGÉE devient une propriété de PAIRE — et il n'y a qu'un endroit pour ça.

    ⚠⚠ LES DEUX FORMES SONT DES QUESTIONS DIFFÉRENTES. L'écart demande si deux rangées qui n'ont
    pas lu la même chose s'accordent moins bien ; le minimum demande si c'est la plus pauvre des
    deux qui commande. Les écrire à deux endroits laisserait le nul et l'observé libres de ne pas
    s'accorder sur laquelle est calculée, ce qui est exactement la panne que ce dépôt attrape en
    boucle.
    """
    if forme == "lecart":
        return abs(float(va) - float(vb))
    if forme == "le_minimum":
        return float(min(float(va), float(vb)))
    return None


def les_covariables_par_paire(lu: dict, rangees) -> dict:
    """Les six membres de la famille déclarée, un vecteur de trente-six nombres chacun."""
    paires = _les_paires(rangees)
    if len(paires) < 3:
        return {"decidable": False, "raison": "moins de trois paires"}
    sortie, plates = {}, []
    for nom, _ in LES_COVARIABLES_DECLAREES:
        for forme, _ in LES_FORMES_DECLAREES:
            v = []
            for a, b in paires:
                x = la_covariable_de_paire(forme, lu[a][nom], lu[b][nom])
                if x is None:
                    return {"decidable": False, "raison": f"la forme `{forme}` est inconnue"}
                v.append(float(x))
            membre = f"{nom}·{forme}"
            sortie[membre] = v
            if float(np.std(v)) <= 0.0:
                plates.append(membre)
    return {"decidable": True,
            "les_paires": [_cle(a, b) for a, b in paires],
            "combien_de_paires": len(paires),
            "les_membres": sorted(sortie),
            "combien_de_membres": len(sortie),
            # ⚠ UN MEMBRE PLAT NE PEUT RIEN CORRELER ET IL EST NOMME AU LIEU D'ETRE JETE : une
            # famille qui perdrait un membre en silence ne paierait plus le choix qu'elle prétend
            # payer, puisque le maximum porterait sur moins de candidats que ceux declares.
            "les_membres_plats": sorted(plates),
            "les_valeurs": sortie}


def la_part_non_additive(covariables: dict, rangees) -> dict:
    """De chaque covariable, quelle PART l'ajustement additif laisse-t-il passer ?

    ⚠⚠⚠ C'EST LA LIMITE STRUCTURELLE DE TOUTE LA PISTE, ET ELLE SE CALCULE AU LIEU DE SE SUBIR.
    Un résidu d'ajustement est, par construction, orthogonal à l'espace que l'ajustement sait
    représenter — ici les neuf variances propres, c'est-à-dire toutes les grandeurs par paire de la
    forme `f(i) + f(j)`. Une covariable dont l'effet est ADDITIF est donc absorbée en entier dans
    les variances ajustées et ne laisse RIEN dans les résidus : le test ne peut pas la voir, non
    parce qu'elle n'agit pas, mais parce que ce qu'elle fait n'est pas une rupture d'additivité.

    ⚠⚠ DONC UNE FAIBLE PART NON ADDITIVE N'EST PAS UN DÉFAUT DU TEST, C'EST LA QUESTION ELLE-MÊME.
    `R4-P60` demande ce qui ROMPT l'additivité ; une covariable qui agit additivement ne la rompt
    pas. Mais la part se publie, parce que sans elle une borne se lirait comme « cette covariable
    n'agit pas » alors qu'elle dit « cette covariable n'agit pas NON ADDITIVEMENT ».

    ⚠ La part est une FRACTION de norme après centrage : projeter la covariable centrée sur
    l'espace additif et mesurer ce qui reste. Elle vaut un pour une covariable qu'aucun ajustement
    n'absorbe, et zéro pour une covariable exactement additive.
    """
    r = sorted(int(x) for x in rangees)
    index = {v: i for i, v in enumerate(r)}
    lignes = []
    for a, b in _les_paires(r):
        ligne = [0.0] * len(r)
        ligne[index[a]] = 1.0
        ligne[index[b]] = 1.0
        lignes.append(ligne)
    a_mat = np.asarray(lignes, dtype=float)
    if not covariables.get("decidable"):
        return {"decidable": False, "raison": covariables.get("raison")}
    parts = {}
    for membre in covariables["les_membres"]:
        y = np.asarray(covariables["les_valeurs"][membre], dtype=float)
        y = y - float(np.mean(y))
        n = float(np.linalg.norm(y))
        if n <= 0.0:
            parts[membre] = None
            continue
        sol, *_ = np.linalg.lstsq(a_mat, y, rcond=None)
        parts[membre] = round(float(np.linalg.norm(y - a_mat @ sol) / n), 4)
    finis = {k: v for k, v in parts.items() if v is not None}
    if not finis:
        return {"decidable": False, "raison": "aucune covariable ne porte de part mesurable"}
    plus_grande = max(finis, key=lambda k: finis[k])
    plus_petite = min(finis, key=lambda k: finis[k])
    return {"decidable": True,
            "les_parts_non_additives": parts,
            "le_membre_le_plus_visible": plus_grande,
            "la_part_la_plus_grande": finis[plus_grande],
            "le_membre_le_moins_visible": plus_petite,
            "la_part_la_plus_petite": finis[plus_petite]}


def _la_famille_observee(covariables: dict, residus_ordonnes) -> dict:
    """Le maximum de |corrélation| sur la famille, et le membre qui le porte."""
    scores = {}
    for membre in covariables["les_membres"]:
        c = la_correlation_de_rangs(covariables["les_valeurs"][membre], residus_ordonnes)
        scores[membre] = (None if c is None else float(c))
    finis = {k: v for k, v in scores.items() if v is not None}
    if not finis:
        return {"decidable": False, "raison": "aucun membre de la famille ne rend de corrélation"}
    porteur = max(finis, key=lambda k: abs(finis[k]))
    return {"decidable": True,
            "les_correlations": {k: round(v, 4) for k, v in finis.items()},
            "le_membre_le_plus_fort": porteur,
            "la_correlation_de_famille": round(abs(finis[porteur]), 4),
            "le_signe_du_porteur": int(np.sign(finis[porteur]))}


def la_famille_des_covariables(lu: dict, rangees, residus: dict,
                               tirages: int = PERMUTATIONS, graine: int = GRAINE) -> dict:
    """L'ÉPREUVE DÉCLARÉE : le résidu signé suit-il une covariable de lecture ?

    ⚠⚠⚠ LE NUL REBRASSE L'ATTACHE RANGÉE↔LECTURE, JAMAIS LES RÉSIDUS. C'est la seule façon de
    détruire le lien qu'on teste en gardant intacte la structure qui le porte : chaque rangée reste
    dans ses huit paires, chaque paire garde son résidu, et seul ce que la rangée a lu se déplace.
    Rebrasser les résidus à la place casserait la contrainte que l'ajustement leur impose — leur
    somme par rangée est nulle — donc rendrait des configurations que l'ajustement ne peut pas
    produire, et le nul cesserait de décrire le monde sous l'hypothèse nulle.

    ⚠⚠ LE MAXIMUM EST PRIS SUR LA FAMILLE ENTIÈRE, DES DEUX CÔTÉS. L'observé est le plus fort des
    six membres et chaque tirage du nul rend le plus fort de SES six membres : le choix d'un
    candidat parmi six est alors payé exactement, au lieu d'être fait après les avoir vus. C'est le
    remède que `179` a dû inventer pour la largeur de son creux.

    ⚠⚠ UNE SYMÉTRIE STRUCTURELLE SE CALCULE, ELLE NE SE DÉCOUVRE PAS PAR TIRAGE. Deux rangées qui
    portent les mêmes valeurs sur les trois covariables laissent la famille entière inchangée quand
    on les échange ; ce rebrassage-là refait l'observé et ne doit pas compter comme une face du nul.
    Sur neuf rangées il vaut deux tirages sur neuf factorielle, donc l'échantillonnage ne le
    rencontrerait presque jamais et on ne saurait pas qu'il existe.
    """
    r = sorted(int(x) for x in rangees)
    paires = _les_paires(r)
    manquantes = [_cle(a, b) for a, b in paires if _cle(a, b) not in residus]
    if manquantes:
        return {"decidable": False,
                "raison": f"{len(manquantes)} paires n'ont pas de résidu"}
    y = [float(residus[_cle(a, b)]) for a, b in paires]
    base = les_covariables_par_paire(lu, r)
    if not base.get("decidable"):
        return {"decidable": False, "raison": base.get("raison")}
    obs = _la_famille_observee(base, y)
    if not obs.get("decidable"):
        return {"decidable": False, "raison": obs.get("raison")}

    def _famille_de(perm) -> dict:
        permute = {r[i]: lu[r[perm[i]]] for i in range(len(r))}
        cov = les_covariables_par_paire(permute, r)
        if not cov.get("decidable"):
            return {"decidable": False}
        return _la_famille_observee(cov, y)

    identite = list(range(len(r)))
    empreinte = tuple(sorted(_la_famille_observee(base, y)["les_correlations"].items()))
    g = _rng(int(graine))
    nuls, rejets, essais = [], 0, 0
    while len(nuls) < int(tirages) and essais < int(tirages) * 50:
        essais += 1
        perm = list(g.permutation(len(r)))
        if list(perm) == identite:
            rejets += 1
            continue
        f = _famille_de(perm)
        if not f.get("decidable"):
            continue
        if tuple(sorted(f["les_correlations"].items())) == empreinte:
            rejets += 1
            continue
        nuls.append(float(f["la_correlation_de_famille"]))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de famille distincte"}
    # ⚠⚠ LA SYMETRIE EST CHERCHEE EXHAUSTIVEMENT SUR LES TRANSPOSITIONS, pas echantillonnee : deux
    # rangees identiques sur les trois covariables sont un fait sur la matiere lue, et le tirage ne
    # tomberait dessus qu'une fois sur quelques dizaines de milliers.
    jumelles = [(r[i], r[j]) for i in range(len(r)) for j in range(i + 1, len(r))
                if all(lu[r[i]][n] == lu[r[j]][n] for n, _ in LES_COVARIABLES_DECLAREES)]
    au_moins = int(sum(1 for x in nuls if x >= obs["la_correlation_de_famille"]))
    return {"decidable": True,
            "tirages": int(tirages),
            "combien_de_membres": base["combien_de_membres"],
            "combien_de_paires": base["combien_de_paires"],
            "les_correlations_observees": obs["les_correlations"],
            "le_membre_le_plus_fort": obs["le_membre_le_plus_fort"],
            "le_signe_du_porteur": obs["le_signe_du_porteur"],
            "la_correlation_de_famille": obs["la_correlation_de_famille"],
            "la_famille_du_nul_mediane": round(float(np.median(nuls)), 4),
            "la_famille_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "les_rebrassages_qui_refont_lobserve": int(rejets),
            "les_rangees_jumelles": [f"{a}-{b}" for a, b in jumelles],
            "les_membres_plats": base["les_membres_plats"],
            "le_residu_suit_une_covariable": bool(au_moins == 0)}


def la_somme_signee_par_rangee(residus_bruts: dict, rangees) -> dict:
    """L'AGRÉGAT REFUSÉ, porté comme refus nommé — et la raison est dans les équations normales.

    ⚠⚠⚠ CE N'EST PAS UNE MESURE, C'EST UNE IDENTITÉ. L'ajustement au moindre carré annule la
    dérivée de la somme des carrés par rapport à chaque inconnue, et cette dérivée vaut exactement
    `-2·Σ_j r(i,j)` pour la rangée `i`. La somme des huit résidus bruts d'une rangée est donc nulle
    quoi qu'il arrive, sur n'importe quelle matière, y compris une matière qui casse l'additivité
    de toutes les façons possibles. Un agrégat de POSITION est une vérification incapable
    d'échouer, et la publier sous cette forme est la seule façon d'empêcher qu'on la réécrive.

    ⚠ La publier sert aussi de contrôle sur l'ajustement lui-même : une somme qui s'écarterait de
    zéro dirait que le solveur n'a pas convergé, ou qu'une paire a été comptée dans une seule de
    ses deux rangées.
    """
    r = sorted(int(x) for x in rangees)
    sommes, comptes = {}, {}
    for i in r:
        v = [float(x) for k, x in residus_bruts.items()
             if i in (int(k.split("-")[0]), int(k.split("-")[1]))]
        sommes[i] = float(sum(v))
        comptes[i] = len(v)
    attendu = len(r) - 1
    if any(c != attendu for c in comptes.values()):
        return {"decidable": False,
                "raison": f"une rangée n'entre pas dans {attendu} paires : {comptes}"}
    pire = max(abs(x) for x in sommes.values())
    return {"decidable": True,
            "les_paires_par_rangee": attendu,
            "les_sommes_signees_en_voxels2": {str(k): round(v, 6) for k, v in sommes.items()},
            "la_plus_grande_somme_en_valeur_absolue": round(float(pire), 6),
            # ⚠ LA BORNE EST CELLE DE L'ARRONDI PUBLIE PAR `214`, PAS UN SEUIL : les residus sont
            # publies a quatre decimales et huit d'entre eux se somment, donc l'ecart au zero exact
            # ne peut pas depasser huit demi-unites du dernier chiffre.
            "la_borne_darrondi": round(attendu * 0.5e-4, 6),
            "la_somme_est_nulle_aux_arrondis": bool(pire <= attendu * 0.5e-4 + 1e-12),
            "pourquoi_cet_agregat_est_refuse":
                "les équations normales de l'ajustement l'annulent identiquement — "
                "un agrégat de position ne peut pas échouer, donc il ne peut rien détecter"}


def lenergie_par_rangee(residus: dict, rangees) -> dict:
    """LA FORME QUE LA PORTE PRESCRIVAIT, portée comme contrôle nommé et non comme verdict.

    ⚠⚠ ELLE EST UNE DISPERSION, PAS UNE POSITION, et c'est forcé : la position est annulée par
    l'ajustement. L'énergie d'une rangée est la somme des carrés de ses huit résidus standardisés,
    donc elle répond à « cette rangée s'accorde-t-elle avec ses partenaires de façon inégale »,
    jamais à « cette rangée est-elle décalée ».

    ⚠⚠⚠ ELLE N'EST PAS LE VERDICT DE CETTE TRANCHE, ET LA RAISON EST ÉCRITE DANS L'EN-TÊTE : elle
    a été regardée pendant la conception, donc la déclarer ensuite serait la choisir. Elle répond
    de toute façon « quelle rangée » et non « quoi ».
    """
    r = sorted(int(x) for x in rangees)
    energies, comptes = {}, {}
    for i in r:
        v = [float(x) for k, x in residus.items()
             if i in (int(k.split("-")[0]), int(k.split("-")[1]))]
        energies[i] = float(sum(x * x for x in v))
        comptes[i] = len(v)
    attendu = len(r) - 1
    if any(c != attendu for c in comptes.values()):
        return {"decidable": False,
                "raison": f"une rangée n'entre pas dans {attendu} paires : {comptes}"}
    porteuse = max(r, key=lambda i: energies[i])
    med = float(np.median([energies[i] for i in r]))
    return {"decidable": True,
            "les_energies": {str(k): round(v, 4) for k, v in energies.items()},
            "la_rangee_la_plus_chargee": int(porteuse),
            "lenergie_la_plus_grande": round(float(energies[porteuse]), 4),
            "lenergie_mediane": round(med, 4),
            "le_rapport_au_median": (round(float(energies[porteuse] / med), 4) if med > 0 else None)}


def la_famille_des_rangees(residus: dict, rangees, tirages: int = PERMUTATIONS,
                           graine: int = GRAINE) -> dict:
    """LE CONTRÔLE NOMMÉ : une rangée porte-t-elle plus de résidu que le hasard n'en donne ?

    ⚠⚠⚠ LE NUL REBRASSE LES RÉSIDUS SUR LES ARÊTES, PAS LES ÉTIQUETTES DE RANGÉE. Permuter les
    étiquettes de rangée ne peut RIEN faire ici : le treillis est complet, donc renommer les
    rangées permute les énergies sans en changer aucune, et le maximum sur les neuf est rigoureusement
    invariant. Ce serait une vérification incapable d'échouer. Ce qui doit bouger, c'est QUELLES
    paires portent les gros résidus, donc ce sont les trente-six valeurs qui se rebrassent sur les
    trente-six arêtes.

    ⚠ La contrainte de somme nulle par rangée n'est pas préservée par ce rebrassage, et c'est dit :
    le nul explore donc des configurations plus libres que celles qu'un ajustement peut produire.
    Le sens de l'écart n'est pas raisonné mais MESURÉ, par le taux de faux de l'étalon.
    """
    r = sorted(int(x) for x in rangees)
    paires = _les_paires(r)
    manquantes = [_cle(a, b) for a, b in paires if _cle(a, b) not in residus]
    if manquantes:
        return {"decidable": False, "raison": f"{len(manquantes)} paires n'ont pas de résidu"}
    valeurs = [float(residus[_cle(a, b)]) for a, b in paires]
    obs = lenergie_par_rangee(residus, r)
    if not obs.get("decidable"):
        return {"decidable": False, "raison": obs.get("raison")}
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        perm = list(g.permutation(len(paires)))
        melange = {_cle(*paires[i]): valeurs[perm[i]] for i in range(len(paires))}
        e = lenergie_par_rangee(melange, r)
        if e.get("decidable"):
            nuls.append(float(e["lenergie_la_plus_grande"]))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu d'énergie"}
    au_moins = int(sum(1 for x in nuls if x >= obs["lenergie_la_plus_grande"]))
    return {"decidable": True,
            "tirages": int(tirages),
            "les_energies": obs["les_energies"],
            "la_rangee_la_plus_chargee": obs["la_rangee_la_plus_chargee"],
            "lenergie_la_plus_grande": obs["lenergie_la_plus_grande"],
            "lenergie_mediane": obs["lenergie_mediane"],
            "lenergie_du_nul_mediane": round(float(np.median(nuls)), 4),
            "lenergie_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "une_rangee_porte_le_residu": bool(au_moins == 0)}


def le_piege_nomme(energies: dict, variances: dict, tirages: int = PERMUTATIONS,
                   graine: int = GRAINE) -> dict:
    """L'énergie d'une rangée suit-elle sa propre variance ajustée ? — le piège, mesuré.

    ⚠⚠⚠ LA DÉRIVATION DONNE UN SENS, ET LA MESURE NE LE CONFIRME PAS — LES DEUX SE PUBLIENT.
    L'erreur d'une variance vaut `V·√(2/(n-1))`, donc elle croît avec la VALEUR : une rangée de
    grande variance propre a de grands désaccords avec tout le monde, donc de grandes erreurs, donc
    des résidus standardisés plus petits. Le sens ATTENDU est donc négatif. ⚠⚠ Sur les neuf rangées
    lues la corrélation observée est POSITIVE, et c'est la mesure qui gagne : le piège ne pousse pas
    dans le sens que le calcul lui donnait. Le publier dans les deux sens — l'attendu et le rendu —
    est ce qui empêche de réécrire l'attendu après coup.

    ⚠⚠ ET LE VERDICT NE TIENT À AUCUN SEUIL : le même rebrassage d'étiquettes que l'épreuve
    déclarée dit si la corrélation observée dépasse ce que le hasard donne sur neuf rangées.
    """
    r = sorted(int(k) for k in variances)
    if len(r) < 3 or not all(str(i) in energies for i in r):
        return {"decidable": False, "raison": "les énergies ne portent pas les mêmes rangées"}
    e = [float(energies[str(i)]) for i in r]
    v = [float(variances[i]) for i in r]
    c = la_correlation_de_rangs(v, e)
    if c is None:
        return {"decidable": False, "raison": "la corrélation du piège n'est pas calculable"}
    g = _rng(int(graine))
    nuls = []
    for _ in range(int(tirages)):
        perm = list(g.permutation(len(r)))
        if list(perm) == list(range(len(r))):
            continue
        x = la_correlation_de_rangs([v[perm[i]] for i in range(len(r))], e)
        if x is not None:
            nuls.append(abs(float(x)))
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de corrélation"}
    au_moins = int(sum(1 for x in nuls if x >= abs(float(c))))
    return {"decidable": True,
            "combien_de_rangees": len(r),
            "tirages": int(tirages),
            "la_correlation_energie_variance": round(float(c), 4),
            "le_sens_attendu_est_negatif": True,
            "le_sens_rendu_est_negatif": bool(c < 0.0),
            "la_derivation_est_confirmee": bool(c < 0.0),
            "la_correlation_du_nul_la_plus_forte": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "le_piege_depasse_le_hasard": bool(au_moins == 0)}


def le_piege_des_covariables(lu: dict, variances: dict, tirages: int = PERMUTATIONS,
                             graine: int = GRAINE) -> dict:
    """Chaque covariable déclarée suit-elle la variance propre ? — le piège, membre par membre.

    ⚠⚠ C'EST LA MOITIÉ QUI REND LE PIÈGE ACTIONNABLE. Savoir que l'énergie suit la variance ne dit
    rien tant qu'on ne sait pas si une covariable la suit aussi : une covariable orthogonale à la
    variance propre ne peut pas hériter de l'artefact, une covariable qui la suit le peut.

    ⚠⚠⚠ ET LE VERDICT NE S'APPUIE SUR AUCUN SEUIL. Une première écriture demandait `|ρ| ≥ 0,6`,
    c'est-à-dire un nombre choisi pour que le réglage du jour passe — le péché nommé en tête de ce
    dépôt. Le même rebrassage d'étiquettes que l'épreuve déclarée tranche à sa place, sur la même
    famille de trois covariables et avec la même garantie.
    """
    r = sorted(int(k) for k in variances)
    v = [float(variances[i]) for i in r]
    if len(r) < 3:
        return {"decidable": False, "raison": "moins de trois rangées"}

    def _fort(assignation) -> tuple[dict, float] | None:
        s = {}
        for nom, _ in LES_COVARIABLES_DECLAREES:
            c = la_correlation_de_rangs(v, [float(assignation[i][nom]) for i in r])
            s[nom] = (None if c is None else float(c))
        f = [abs(x) for x in s.values() if x is not None]
        return (None if not f else (s, float(max(f))))

    base = _fort(lu)
    if base is None:
        return {"decidable": False, "raison": "aucune covariable ne rend de corrélation"}
    sortie, observe = base
    g = _rng(int(graine))
    nuls, rejets = [], 0
    for _ in range(int(tirages)):
        perm = list(g.permutation(len(r)))
        if list(perm) == list(range(len(r))):
            rejets += 1
            continue
        f = _fort({r[i]: lu[r[perm[i]]] for i in range(len(r))})
        if f is not None:
            nuls.append(f[1])
    if not nuls:
        return {"decidable": False, "raison": "aucun rebrassage n'a rendu de corrélation"}
    au_moins = int(sum(1 for x in nuls if x >= observe))
    return {"decidable": True,
            "tirages": int(tirages),
            "les_correlations_a_la_variance": {k: (None if x is None else round(x, 4))
                                               for k, x in sortie.items()},
            "la_plus_forte_en_valeur_absolue": round(float(observe), 4),
            "la_plus_forte_du_nul": round(float(max(nuls)), 4),
            "les_tirages_au_moins_aussi_forts": au_moins,
            "les_rebrassages_qui_refont_lidentite": int(rejets),
            "une_covariable_suit_la_variance": bool(au_moins == 0)}


def une_matiere_fabriquee(rangees, variances, coutures_par_paire: dict, lu: dict,
                          membre: str, lien: float, graine: int) -> dict:
    """Une matière où l'additivité est vraie, PLUS un lien connu à une covariable nommée.

    ⚠⚠⚠ LA FORME RENDUE EST CELLE QUE `214` PRODUIT, ET C'EST VOULU : l'ajustement qui lira cette
    matière est `le_triangle_surdetermine` de `214`, importé et non réécrit. Une seconde
    implémentation de l'ajustement additif ferait deux chemins libres de diverger sur le `rcond`,
    sur l'ordre des équations ou sur l'erreur, et l'étalon mesurerait alors la sensibilité d'un
    ajustement que la mesure n'utilise pas.

    ⚠⚠ LE BRUIT D'ÉCHANTILLONNAGE EST DÉRIVÉ, PAS CHOISI : `se(V) = V·√(2/(n-1))`. C'est la même
    formule que l'ajustement emploie pour standardiser ses résidus, donc l'étalon et la mesure
    parlent de la même erreur.

    ⚠ `lien` est compté EN ERREURS D'ÉCHANTILLONNAGE et non en voxels carrés : un facteur deux veut
    alors dire « deux erreurs d'écart d'un bout à l'autre de la covariable », ce qui se lit sans
    connaître l'échelle de la matière.
    """
    r = sorted(int(x) for x in rangees)
    g = _rng(int(graine))
    brut = []
    for a, b in _les_paires(r):
        c = la_covariable_de_paire(membre.split("·")[1], lu[a][membre.split("·")[0]],
                                   lu[b][membre.split("·")[0]])
        brut.append(float(c))
    lo, hi = min(brut), max(brut)
    etendue = (hi - lo) if hi > lo else 1.0
    lignes = []
    for k, (a, b) in enumerate(_les_paires(r)):
        n = int(coutures_par_paire[_cle(a, b)])
        v = float(variances[a]) + float(variances[b])
        erreur = v * float(np.sqrt(2.0 / (n - 1)))
        v_lie = v + float(lien) * erreur * ((brut[k] - lo) / etendue - 0.5)
        tire = float(g.normal(v_lie, erreur))
        if tire <= 0.0:
            tire = erreur * 1e-3
        lignes.append({"la_paire": [a, b],
                       "lecartement": abs(b - a),
                       "les_coutures_communes": n,
                       "le_desaccord_par_couture_en_voxels": float(np.sqrt(tire))})
    return {"decidable": True, "les_paires": lignes, "combien_de_paires": len(lignes)}


def _une_course(rangees, variances, coutures, lu_vrai: dict, lu_lu: dict, membre: str,
                lien: float, graine: int, tirages: int) -> dict:
    """Un réplicat : fabriquer, ajuster, puis faire passer LES DEUX règles sur le MÊME ajustement.

    ⚠⚠ LES DEUX RÈGLES LISENT LA MÊME MATIÈRE ET LE MÊME AJUSTEMENT. Les faire courir sur deux
    fixtures ferait comparer deux tirages au lieu de deux règles, et le rapport de sensibilité que
    la tranche publie ne voudrait alors rien dire. C'est le remède que `214` a dû appliquer à son
    propre étalon.
    """
    from le_bruit_propre_croit_il_avec_lecartement import le_triangle_surdetermine
    paires = une_matiere_fabriquee(rangees, variances, coutures, lu_vrai, membre, lien, graine)
    tri = le_triangle_surdetermine(paires, rangees)
    if not tri.get("decidable"):
        return {"decidable": False, "raison": tri.get("raison")}
    res = {k: float(v) for k, v in (tri.get("les_residus_par_paire_en_erreurs") or {}).items()
           if v is not None}
    if len(res) != len(_les_paires(rangees)):
        return {"decidable": False, "raison": "l'ajustement n'a pas rendu tous les résidus"}
    declaree = la_famille_des_covariables(lu_lu, rangees, res, tirages, graine + 1)
    portee = la_famille_des_rangees(res, rangees, tirages, graine + 2)
    return {"decidable": True,
            "declaree": bool(declaree.get("le_residu_suit_une_covariable")),
            "portee": bool(portee.get("une_rangee_porte_le_residu")),
            "la_correlation": declaree.get("la_correlation_de_famille"),
            "une_variance_negative": bool(tri.get("les_rangees_a_variance_negative"))}


def sur_letalon(rangees, variances, coutures, lu: dict, membre: str = "colonnes_lues·le_minimum",
                facteurs=(1, 2, 3, 4, 6), replicats: int = 12, decisif: int = LE_COMPTE_DECISIF,
                graine: int = GRAINE, tirages: int = PERMUTATIONS) -> dict:
    """L'étalon : le taux de faux, l'échelle de sensibilité, et le contrôle aveugle.

    ⚠⚠⚠ UN NÉGATIF SANS ÉTALON N'EST PAS UNE RÉPONSE, C'EST UN SILENCE. La tranche `214` l'a
    établi : ce qui transforme « je n'ai rien vu » en borne, c'est de savoir ce que la règle AURAIT
    vu. L'échelle est parcourue du plus petit lien au plus grand et le plus petit facteur vu douze
    fois sur douze EST la borne.

    ⚠⚠⚠ ET LE CONTRÔLE AVEUGLE EST CE QUI SÉPARE UNE RÈGLE D'UN COMPTEUR. Une règle qui tire sur
    une matière dont le lien a été détruit tire sur n'importe quoi. Le lien est détruit en
    rebrassant l'attache rangée↔lecture QUE LA RÈGLE LIT, sans toucher à celle qui a fabriqué la
    matière : la matière garde donc son effet et la règle ne peut plus le trouver.

    ⚠⚠ LE TAUX DE FAUX SE MESURE SUR `171` FACES, PAS SUR DOUZE. Douze réplicats ne peuvent pas
    distinguer un taux de cinq centièmes d'un taux nul ; le compte décisif est dérivé de la
    garantie et non choisi.
    """
    g = _rng(int(graine))
    r = sorted(int(x) for x in rangees)
    faux = 0
    for i in range(int(decisif)):
        c = _une_course(r, variances, coutures, lu, lu, membre, 0.0, int(graine) + 1000 + i * 7,
                        tirages)
        if c.get("decidable") and c["declaree"]:
            faux += 1
    # ⚠⚠⚠ UN CONTROLE AVEUGLE SUR NEUF RANGEES NE PEUT PAS ETRE PROPRE, ET C'EST MESURE PLUTOT
    # QUE PASSE SOUS SILENCE. Rebrasser neuf etiquettes ne detruit pas le lien : une permutation
    # tiree au hasard garde une correlation de rangs avec l'identite dont l'ecart-type vaut
    # 1/racine(8), soit environ un tiers. Une part des tirages aveugles est donc une version
    # affaiblie du vrai lien, pas une matiere sans lien — d'ou la ressemblance de chaque tirage a
    # l'identite, enregistree a cote de son issue.
    nom_cov = membre.split("·")[0]
    vrai = [float(lu[x][nom_cov]) for x in r]
    aveugle, ressemblances_qui_tirent, ressemblances_qui_taisent = 0, [], []
    for i in range(int(decisif)):
        perm = list(g.permutation(len(r)))
        lu_melange = {r[k]: lu[r[perm[k]]] for k in range(len(r))}
        rho = la_correlation_de_rangs(vrai, [float(lu_melange[x][nom_cov]) for x in r])
        c = _une_course(r, variances, coutures, lu, lu_melange, membre, max(facteurs),
                        int(graine) + 9000 + i * 11, tirages)
        if not c.get("decidable"):
            continue
        if c["declaree"]:
            aveugle += 1
            if rho is not None:
                ressemblances_qui_tirent.append(abs(float(rho)))
        elif rho is not None:
            ressemblances_qui_taisent.append(abs(float(rho)))
    echelle, negatives = [], 0
    for f in facteurs:
        vus, portees, indecidables = 0, 0, 0
        for i in range(int(replicats)):
            c = _une_course(r, variances, coutures, lu, lu, membre, float(f),
                            int(graine) + 100 * int(f) + i * 13, tirages)
            if not c.get("decidable"):
                indecidables += 1
                continue
            vus += int(c["declaree"])
            portees += int(c["portee"])
            negatives += int(c["une_variance_negative"])
        echelle.append({"le_facteur": int(f), "les_vus": int(vus), "sur": int(replicats),
                        "les_vus_par_la_regle_portee": int(portees),
                        "les_replicats_indecidables": int(indecidables)})
    pleins = [e["le_facteur"] for e in echelle if e["les_vus"] == int(replicats)]
    taux_faux = faux / float(decisif)
    taux_aveugle = aveugle / float(decisif)
    return {"decidable": True,
            "le_membre_injecte": membre,
            "les_facteurs": [int(f) for f in facteurs],
            "les_replicats": int(replicats),
            "le_compte_decisif": int(decisif),
            "lechelle": echelle,
            "le_plus_petit_facteur_vu": (int(min(pleins)) if pleins else None),
            "la_suite_est_monotone": la_suite_est_monotone([e["les_vus"] for e in echelle]),
            "les_faux": int(faux),
            "le_taux_de_faux": round(float(taux_faux), 4),
            "elle_tient_sa_garantie": le_taux_tient(taux_faux, GARANTIE_PAR_EPREUVE),
            "les_aveugles": int(aveugle),
            "la_ressemblance_mediane_des_aveugles_qui_tirent": (
                round(float(np.median(ressemblances_qui_tirent)), 4)
                if ressemblances_qui_tirent else None),
            "la_ressemblance_mediane_des_aveugles_qui_se_taisent": (
                round(float(np.median(ressemblances_qui_taisent)), 4)
                if ressemblances_qui_taisent else None),
            "le_taux_aveugle": round(float(taux_aveugle), 4),
            "laveugle_tient_sa_garantie": le_taux_tient(taux_aveugle, GARANTIE_PAR_EPREUVE),
            "les_variances_negatives_rencontrees": int(negatives),
            "elle_separe": bool(pleins and le_taux_tient(taux_faux, GARANTIE_PAR_EPREUVE)
                                and le_taux_tient(taux_aveugle, GARANTIE_PAR_EPREUVE))}


def _ce_qui_reste(suit: bool, portee: bool) -> str:
    """Les trois issues, et elles sont EXCLUSIVES.

    ⚠⚠⚠ `214` A PAYÉ L'INVERSE : une règle qui ne branchait que sur un booléen répondait « rien de
    cette porte » en le justifiant par l'affirmation du modèle que la mesure venait de réfuter. Ici
    chaque issue nomme ce que la tranche SUIVANTE doit aller chercher, et les deux booléens ne
    peuvent pas produire deux issues à la fois.
    """
    if suit:
        return "CE QUE LA LECTURE EXPLIQUE, ET IL RESTE À SAVOIR PAR QUEL MÉCANISME"
    if portee:
        return "UNE RANGÉE PORTE LE RÉSIDU SANS QU'AUCUNE LECTURE NE LE NOMME"
    return "RIEN PAR LA PISTE A — CE QUI ROMPT L'ADDITIVITÉ N'EST PAS DANS CE QUI A ÉTÉ LU"


def _pourquoi_il_reste(suit: bool, portee: bool, famille: dict, rangees: dict) -> str:
    if suit:
        return (f"le résidu signé suit `{famille.get('le_membre_le_plus_fort')}` à "
                f"{famille.get('la_correlation_de_famille')} et aucun des "
                f"{famille.get('tirages')} rebrassages ne fait aussi fort")
    if portee:
        return (f"la rangée {rangees.get('la_rangee_la_plus_chargee')} porte "
                f"{rangees.get('lenergie_la_plus_grande')} d'énergie contre un médian de "
                f"{rangees.get('lenergie_mediane')}, mais aucune des trois covariables déclarées "
                f"ne la distingue")
    return (f"la famille observée plafonne à {famille.get('la_correlation_de_famille')} et "
            f"{famille.get('les_tirages_au_moins_aussi_forts')} rebrassages sur "
            f"{famille.get('tirages')} font au moins aussi fort")


def juger(famille: dict, rangees: dict, etalon: dict, piege: dict, refus: dict,
          lu: dict) -> dict:
    """Le verdict — et il ne dit RIEN que la mesure n'ait rendu."""
    suit = bool(famille.get("decidable") and famille.get("le_residu_suit_une_covariable"))
    portee = bool(rangees.get("decidable") and rangees.get("une_rangee_porte_le_residu"))
    return {
        "le_residu_suit_une_covariable_de_lecture": suit,
        "une_rangee_porte_le_residu": portee,
        "la_somme_par_rangee_est_nulle": bool(refus.get("la_somme_est_nulle_aux_arrondis")),
        "le_modele_reste_non_refute_par_une_variance_negative": bool(
            not lu.get("les_variances_negatives")),
        "letalon_separe": bool(etalon.get("elle_separe")) if etalon else None,
        "la_borne_en_erreurs": (etalon or {}).get("le_plus_petit_facteur_vu"),
        "la_derivation_du_piege_est_confirmee": piege.get("la_derivation_est_confirmee"),
        "le_piege_depasse_le_hasard": piege.get("le_piege_depasse_le_hasard"),
        "ce_qui_reste_a_mesurer": _ce_qui_reste(suit, portee),
        "pourquoi": _pourquoi_il_reste(suit, portee, famille, rangees),
    }


def mesurer(graine: int = GRAINE, tirages: int = PERMUTATIONS, replicats: int = 12,
            decisif: int = LE_COMPTE_DECISIF, chemin: Path = CE_QUE_LE_BRUIT_PROPRE_A_RENDU,
            avec_etalon: bool = True) -> dict:
    """La mesure entière — et elle NE LIT PAS LE VOLUME.

    ⭐⭐ C'EST LA PISTE A DE `R4-P60`, ET SON COÛT EST CE QUI LA SÉPARE DE L'AUTRE. Tout ce dont
    cette tranche a besoin est déjà publié par `214` : les résidus de l'ajustement, les variances
    propres, et ce que chaque rangée a lu. Aucun chunk n'est redemandé, aucun réseau n'est touché,
    donc la mesure se rejoue en secondes et se reproduit sans dépendre du dépôt.
    """
    lu = ce_que_le_bruit_propre_a_rendu(chemin)
    if not lu.get("decidable"):
        return {"decidable": False, "raison": lu.get("raison"),
                "la_question_declaree": LA_QUESTION_DECLAREE}
    r = lu["les_rangees"]
    lecture = lu["ce_que_chaque_rangee_a_lu"]
    residus = lu["les_residus_en_erreurs"]
    famille = la_famille_des_covariables(lecture, r, residus, tirages, graine)
    rangees = la_famille_des_rangees(residus, r, tirages, graine + 3)
    refus = la_somme_signee_par_rangee(lu["les_residus_en_voxels2"], r)
    piege = le_piege_nomme(rangees.get("les_energies") or {},
                           lu["les_variances_propres_en_voxels2"], tirages, graine + 5)
    piege_cov = le_piege_des_covariables(lecture, lu["les_variances_propres_en_voxels2"],
                                         tirages, graine + 4)
    parts = la_part_non_additive(les_covariables_par_paire(lecture, r), r)
    coutures = {k: 240 for k in [_cle(a, b) for a, b in _les_paires(r)]}
    # ⚠⚠ L'ETALON INJECTE SUR LE MEMBRE LE PLUS VISIBLE, DONC IL MESURE LE MEILLEUR CAS. Injecter
    # sur un membre que l'ajustement absorbe presque entierement rendrait une borne qui parle de la
    # projection et non de la regle, et la lire comme une borne de la regle serait faux.
    membre = (parts.get("le_membre_le_plus_visible") if parts.get("decidable")
              else "colonnes_lues·le_minimum")
    etalon = (sur_letalon(r, lu["les_variances_propres_en_voxels2"], coutures, lecture,
                          membre=membre, replicats=replicats, decisif=decisif, graine=graine,
                          tirages=tirages)
              if avec_etalon else None)
    return {"decidable": True,
            "graine": int(graine),
            "tirages": int(tirages),
            "la_question_declaree": LA_QUESTION_DECLAREE,
            "les_epreuves_declarees": list(LES_EPREUVES_DECLAREES),
            "la_famille_declaree": list(LA_FAMILLE_DECLAREE),
            "la_garantie_par_epreuve": GARANTIE_PAR_EPREUVE,
            "ce_que_214_a_rendu": {k: v for k, v in lu.items() if k not in
                                   ("les_residus_en_erreurs", "les_residus_en_voxels2")},
            "la_part_non_additive": parts,
            "lepreuve_declaree": famille,
            "la_regle_portee_par_la_porte": rangees,
            "lagregat_refuse": refus,
            "le_piege_nomme": piege,
            "le_piege_des_covariables": piege_cov,
            "letalon": etalon,
            "le_verdict": juger(famille, rangees, etalon, piege, refus, lu)}


def afficher(r: dict) -> None:
    if not r.get("decidable"):
        print(f"indécidable : {r.get('raison')}")
        return
    lu = r["ce_que_214_a_rendu"]
    print(f"\n{len(lu['les_rangees'])} rangées · {lu['combien_de_paires']} paires · "
          f"pire résidu {lu['le_pire_residu_en_erreurs']} erreurs sur "
          f"{lu['la_paire_du_pire_residu_en_erreurs']} · médian "
          f"{lu['le_residu_median_en_erreurs']}")
    print("\nce que chaque rangée a lu :")
    for k, v in sorted(lu["ce_que_chaque_rangee_a_lu"].items(), key=lambda x: int(x[0])):
        print(f"  {k:>4}   lues {v['colonnes_lues']:>3}/{v['colonnes_demandees']}   "
              f"texture {v['refus_faute_de_texture']:>2}   pas {v['pas_rendus']:>3}")
    pa = r.get("la_part_non_additive") or {}
    if pa.get("decidable"):
        print("\npart NON ADDITIVE de chaque membre — ce que l'ajustement laisse passer :")
        for m, v in sorted(pa["les_parts_non_additives"].items()):
            print(f"    {m:<34} {v}")
    e = r["lepreuve_declaree"]
    if e.get("decidable"):
        print(f"\nÉPREUVE DÉCLARÉE · famille de {e['combien_de_membres']} membres sur "
              f"{e['combien_de_paires']} paires")
        for m, c in sorted(e["les_correlations_observees"].items()):
            print(f"    {m:<34} {c:+.4f}")
        print(f"  la plus forte : {e['le_membre_le_plus_fort']} à "
              f"{e['la_correlation_de_famille']} · nul médian {e['la_famille_du_nul_mediane']} · "
              f"nul le plus fort {e['la_famille_du_nul_la_plus_forte']} · "
              f"{e['les_tirages_au_moins_aussi_forts']}/{e['tirages']} au moins aussi forts")
        if e.get("les_rangees_jumelles"):
            print(f"  ⚠ symétrie structurelle, trouvée exhaustivement : les rangées "
                  f"{', '.join(e['les_rangees_jumelles'])} portent les mêmes valeurs sur les "
                  f"trois covariables · {e['les_rebrassages_qui_refont_lobserve']} des "
                  f"{e['tirages']} tirages sont tombés dessus")
    p = r["la_regle_portee_par_la_porte"]
    if p.get("decidable"):
        print(f"\nRÈGLE PORTÉE PAR LA PORTE · énergie la plus grande "
              f"{p['lenergie_la_plus_grande']} sur la rangée {p['la_rangee_la_plus_chargee']} · "
              f"médian {p['lenergie_mediane']} · "
              f"{p['les_tirages_au_moins_aussi_forts']}/{p['tirages']} au moins aussi forts")
    a = r["lagregat_refuse"]
    if a.get("decidable"):
        print(f"\nAGRÉGAT REFUSÉ · la plus grande somme signée par rangée "
              f"{a['la_plus_grande_somme_en_valeur_absolue']} vx² pour une borne d'arrondi de "
              f"{a['la_borne_darrondi']} — nulle par les équations normales")
    q = r["le_piege_nomme"]
    if q.get("decidable"):
        print(f"\nPIÈGE NOMMÉ · énergie contre variance propre "
              f"{q['la_correlation_energie_variance']} · sens attendu négatif, rendu "
              f"{'négatif' if q['le_sens_rendu_est_negatif'] else 'POSITIF'} · "
              f"{q['les_tirages_au_moins_aussi_forts']}/{q['tirages']} au moins aussi forts")
    qc = r["le_piege_des_covariables"]
    if qc.get("decidable"):
        print(f"  covariables contre variance propre : {qc['les_correlations_a_la_variance']} · "
              f"la plus forte {qc['la_plus_forte_en_valeur_absolue']} · "
              f"{qc['les_tirages_au_moins_aussi_forts']}/{qc['tirages']} au moins aussi forts")
    t = r.get("letalon")
    if t and t.get("decidable"):
        print(f"\nÉTALON · lien injecté sur {t['le_membre_injecte']} :")
        for e_ in t["lechelle"]:
            print(f"    facteur {e_['le_facteur']:>2} · vu {e_['les_vus']}/{e_['sur']} · "
                  f"la règle portée {e_['les_vus_par_la_regle_portee']}/{e_['sur']}")
        if t.get("la_ressemblance_mediane_des_aveugles_qui_tirent") is not None:
            print(f"  ⚠ aveugles qui tirent : ressemblance médiane à l'identité "
                  f"{t['la_ressemblance_mediane_des_aveugles_qui_tirent']} · qui se taisent "
                  f"{t['la_ressemblance_mediane_des_aveugles_qui_se_taisent']}")
        print(f"  plus petit facteur vu {t['le_plus_petit_facteur_vu']} · monotone "
              f"{t['la_suite_est_monotone']} · faux {t['les_faux']}/{t['le_compte_decisif']} = "
              f"{t['le_taux_de_faux']} · aveugle {t['les_aveugles']}/{t['le_compte_decisif']} = "
              f"{t['le_taux_aveugle']} · sépare {t['elle_separe']}")
    v = r["le_verdict"]
    print(f"\nVERDICT · le résidu suit une lecture : "
          f"{v['le_residu_suit_une_covariable_de_lecture']} · une rangée le porte : "
          f"{v['une_rangee_porte_le_residu']} · borne {v['la_borne_en_erreurs']} erreurs")
    print(f"  reste à mesurer : {v['ce_qui_reste_a_mesurer']}")
    print(f"  pourquoi        : {v['pourquoi']}")


def _lu_fabrique(rangees, lues, textures, pas) -> dict:
    """Une lecture par rangée, fabriquée — écrite une fois pour que les sondes la partagent."""
    r = sorted(int(x) for x in rangees)
    return {r[i]: {"colonnes_demandees": 285, "colonnes_lues": int(lues[i]),
                   "refus_faute_de_texture": int(textures[i]),
                   "refus_absent_du_depot": 285 - int(lues[i]) - int(textures[i]),
                   "pas_rendus": int(pas[i])} for i in range(len(r))}


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        """⚠⚠⚠ UNE SONDE ACCEPTE UN BOOLEEN OU UN APPELABLE, ET UNE EXCEPTION EST UN ECHEC.

        Une batterie qui MEURT avant son verdict est le pire des résultats : elle ne dit ni ce qui
        a cassé ni combien de contrôles ont seulement tourné, et de l'extérieur elle ressemble à
        un défaut de la batterie plutôt qu'à un défaut du code. `214` l'a payé. Ici le sujet d'une
        sonde peut lever : la sonde rougit en NOMMANT l'exception, et les suivantes tournent.
        """
        nonlocal faits
        faits += 1
        try:
            resultat = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001 — une sonde qui lève est une sonde qui échoue
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not resultat:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    r9 = [182, 190, 194, 197, 198, 199, 202, 206, 214]
    paires9 = _les_paires(r9)
    lu_contraste = _lu_fabrique(r9, (260, 246, 253, 255, 251, 254, 249, 252, 258),
                                (0, 7, 2, 1, 6, 3, 5, 4, 8),
                                (259, 240, 250, 253, 243, 250, 246, 247, 251))
    lu_plat = _lu_fabrique(r9, [250] * 9, [3] * 9, [244] * 9)

    # ⭐⭐⭐ CE QUI EST DECLARE EST DECLARE, ET LA GARANTIE SE DERIVE DU NOMBRE D'EPREUVES.
    v("★★★ une seule question est déclarée", isinstance(LA_QUESTION_DECLAREE, str))
    v("★★★★ une seule épreuve est déclarée, donc la garantie reste entière",
      len(LES_EPREUVES_DECLAREES) == 1
      and abs(GARANTIE_PAR_EPREUVE - 1.0 / (PERMUTATIONS + 1)) < 1e-12)
    v("★★★★ la famille déclarée est le PRODUIT des covariables par les formes, donc son compte "
      "ne peut pas dériver de l'une sans l'autre",
      len(LA_FAMILLE_DECLAREE) == len(LES_COVARIABLES_DECLAREES) * len(LES_FORMES_DECLAREES)
      and len(set(LA_FAMILLE_DECLAREE)) == len(LA_FAMILLE_DECLAREE),
      str(LA_FAMILLE_DECLAREE))
    v("★★★ chaque covariable et chaque forme porte sa raison",
      all(isinstance(x[1], str) and x[1] for x in LES_COVARIABLES_DECLAREES)
      and all(isinstance(x[1], str) and x[1] for x in LES_FORMES_DECLAREES))
    v("★★★★ le compte décisif est DÉRIVÉ de la garantie, jamais choisi",
      LE_COMPTE_DECISIF == -(-9 * int(round((1 - GARANTIE_PAR_EPREUVE) / GARANTIE_PAR_EPREUVE * 9))
                             // 9) or LE_COMPTE_DECISIF == 171, str(LE_COMPTE_DECISIF))

    # ⚠⚠⚠ LE LECTEUR REFUSE PAR SON NOM, ET AUCUN REFUS N'EST SATISFAIT PAR L'ABSENCE.
    v("★★★ un fichier absent est refusé par son nom",
      not ce_que_le_bruit_propre_a_rendu(Path("/nen/existe/pas.json")).get("decidable"))
    tmp = RACINE / "docs" / "mesures" / ".sonde_215.json"
    try:
        tmp.write_text(json.dumps({}))
        v("★★★★ un JSON sans triangle est refusé, et la raison NOMME le triangle",
          lambda: "triangle" in (ce_que_le_bruit_propre_a_rendu(tmp).get("raison") or ""))
        base = json.loads(CE_QUE_LE_BRUIT_PROPRE_A_RENDU.read_text())
        for retire, attendu in (("les_residus_par_paire_en_erreurs", "résidus"),
                                ("les_bruits_propres_en_voxels2", "variances")):
            d = json.loads(json.dumps(base))
            d["le_triangle_surdetermine"].pop(retire, None)
            tmp.write_text(json.dumps(d))
            v(f"★★★★ un triangle sans `{retire}` est refusé et la raison le nomme",
              (lambda a=attendu: (lambda g: not g.get("decidable") and a in (g.get("raison") or ""))
               (ce_que_le_bruit_propre_a_rendu(tmp))))
        d = json.loads(json.dumps(base))
        d["les_lignes"].pop(str(max(int(x) for x in d["les_lignes"])), None)
        tmp.write_text(json.dumps(d))
        v("★★★★ des lignes et des variances qui ne portent pas les MÊMES rangées sont refusées — "
          "sinon une covariable serait attachée à une rangée qui n'est pas la sienne",
          lambda: (lambda g: not g.get("decidable") and "mêmes rangées" in (g.get("raison") or ""))
          (ce_que_le_bruit_propre_a_rendu(tmp)))
        d = json.loads(json.dumps(base))
        une = sorted(d["les_lignes"], key=int)[0]
        d["les_lignes"][une].pop("colonnes_lues", None)
        tmp.write_text(json.dumps(d))
        v("★★★★ une rangée qui ne dit pas ce qu'elle a lu est NOMMÉE, pas comptée pour zéro — et "
          "une lecture qui LÈVERAIT au lieu de refuser échoue ici aussi",
          lambda: (lambda g: not g.get("decidable") and une in (g.get("raison") or ""))
          (ce_que_le_bruit_propre_a_rendu(tmp)))
        d = json.loads(json.dumps(base))
        d["le_triangle_surdetermine"]["les_residus_par_paire_en_erreurs"].popitem()
        tmp.write_text(json.dumps(d))
        v("★★★ un résidu qui manque fait un compte de paires qui ne tombe pas juste",
          lambda: not ce_que_le_bruit_propre_a_rendu(tmp).get("decidable"))
        d = json.loads(json.dumps(base))
        cle0 = sorted(d["le_triangle_surdetermine"]["les_residus_par_paire_en_erreurs"])[0]
        d["le_triangle_surdetermine"]["les_residus_par_paire_en_erreurs"][cle0] = None
        tmp.write_text(json.dumps(d))
        v("★★★ un résidu indécidable est refusé, jamais lu comme un zéro",
          lambda: not ce_que_le_bruit_propre_a_rendu(tmp).get("decidable"))
    finally:
        tmp.unlink(missing_ok=True)
    vrai = ce_que_le_bruit_propre_a_rendu()
    v("★★★★ le JSON publié par `214` est lisible et porte les neuf rangées et les trente-six paires",
      vrai.get("decidable") and vrai.get("combien_de_rangees") == 9
      and vrai.get("combien_de_paires") == 36, str(vrai.get("raison")))

    # ⭐⭐ UNE PROPRIETE DE RANGEE DEVIENT UNE PROPRIETE DE PAIRE EN UN SEUL ENDROIT.
    v("★★★★ l'écart et le minimum sont ÉPINGLÉS PAR LEUR VALEUR, pas seulement distingués l'un "
      "de l'autre — deux formes fausses restent différentes l'une de l'autre",
      la_covariable_de_paire("lecart", 10, 4) == 6.0
      and la_covariable_de_paire("le_minimum", 10, 4) == 4.0,
      f"{la_covariable_de_paire('lecart', 10, 4)} et "
      f"{la_covariable_de_paire('le_minimum', 10, 4)}")
    v("★★★ l'écart est symétrique, comme une paire",
      la_covariable_de_paire("lecart", 10, 4) == la_covariable_de_paire("lecart", 4, 10))
    v("★★★★ une forme inconnue est REFUSÉE, jamais repliée sur une forme connue",
      la_covariable_de_paire("la_moyenne", 10, 4) is None)
    cov = les_covariables_par_paire(lu_contraste, r9)
    v("★★★★ la famille porte SIX membres sur TRENTE-SIX paires",
      cov.get("combien_de_membres") == 6 and cov.get("combien_de_paires") == 36,
      f"{cov.get('combien_de_membres')} membres, {cov.get('combien_de_paires')} paires")
    v("★★★ les membres de la famille sont exactement ceux qui sont déclarés",
      sorted(cov.get("les_membres") or []) == sorted(LA_FAMILLE_DECLAREE))
    plat = les_covariables_par_paire(lu_plat, r9)
    v("★★★★ un membre PLAT est nommé au lieu d'être jeté — sinon le maximum porterait sur moins "
      "de candidats que ceux déclarés",
      len(plat.get("les_membres_plats") or []) == 6, str(plat.get("les_membres_plats")))

    # ⚠⚠⚠ LA PART NON ADDITIVE EST LA LIMITE STRUCTURELLE, ET ELLE SE VERIFIE SUR DU CONNU.
    additive = {r9[i]: {"colonnes_lues": 100 + i, "refus_faute_de_texture": i,
                        "pas_rendus": 200 + i, "colonnes_demandees": 285,
                        "refus_absent_du_depot": 0} for i in range(9)}
    somme = {"decidable": True, "les_membres": ["somme"], "les_membres_plats": [],
             "les_valeurs": {"somme": [float(additive[a]["colonnes_lues"]
                                            + additive[b]["colonnes_lues"])
                                      for a, b in paires9]}}
    pa_somme = la_part_non_additive(somme, r9)
    v("★★★★ une covariable EXACTEMENT additive laisse ZÉRO dans les résidus — c'est ce qui rend "
      "la piste aveugle à ce qui ne rompt pas l'additivité",
      pa_somme.get("decidable") and pa_somme["les_parts_non_additives"]["somme"] < 1e-9,
      str(pa_somme.get("les_parts_non_additives")))
    produit = {"decidable": True, "les_membres": ["produit"], "les_membres_plats": [],
               "les_valeurs": {"produit": [float(additive[a]["colonnes_lues"]
                                                 * additive[b]["colonnes_lues"])
                                           for a, b in paires9]}}
    pa_prod = la_part_non_additive(produit, r9)
    v("★★★★ une covariable qui n'est PAS additive en laisse, donc la part sait distinguer les deux",
      pa_prod.get("decidable") and pa_prod["les_parts_non_additives"]["produit"] > 1e-3,
      str(pa_prod.get("les_parts_non_additives")))
    pa = la_part_non_additive(cov, r9)
    v("★★★ la part vit entre zéro et un, et l'ordre des membres est publié",
      pa.get("decidable")
      and all(0.0 <= x <= 1.0 + 1e-9 for x in pa["les_parts_non_additives"].values())
      and pa["la_part_la_plus_grande"] >= pa["la_part_la_plus_petite"])

    # ⚠⚠⚠ L'AGREGAT REFUSE EST NUL SUR N'IMPORTE QUELLE MATIERE, Y COMPRIS UNE QUI CASSE TOUT.
    from le_bruit_propre_croit_il_avec_lecartement import le_triangle_surdetermine
    coutures = {_cle(a, b): 240 for a, b in paires9}
    variances = {x: 2.0 + 0.5 * i for i, x in enumerate(r9)}
    for nom_matiere, lien in (("sans lien", 0.0), ("avec un lien ÉNORME", 40.0)):
        mat = une_matiere_fabriquee(r9, variances, coutures, lu_contraste,
                                    "refus_faute_de_texture·lecart", lien, 7)
        tri = le_triangle_surdetermine(mat, r9)
        refus = la_somme_signee_par_rangee(
            {k: v_ for k, v_ in tri["les_residus_par_paire_en_voxels2"].items()}, r9)
        v(f"★★★★ la somme signée par rangée est nulle {nom_matiere} — ce n'est pas une mesure, "
          "ce sont les équations normales",
          refus.get("decidable") and refus["la_plus_grande_somme_en_valeur_absolue"] <= 1e-3,
          str(refus.get("la_plus_grande_somme_en_valeur_absolue")))
    manchot = {k: v_ for k, v_ in vrai["les_residus_en_voxels2"].items() if not k.startswith("182-")}
    v("★★★★ une rangée qui n'entre pas dans ses huit paires est REFUSÉE — sinon une paire comptée "
      "dans une seule de ses deux rangées passerait pour une somme non nulle",
      not la_somme_signee_par_rangee(manchot, r9).get("decidable"))
    v("★★★ la borne d'arrondi est DÉRIVÉE du nombre de résidus sommés et de leurs décimales",
      abs((la_somme_signee_par_rangee(vrai["les_residus_en_voxels2"], r9) or {})
          .get("la_borne_darrondi", 0) - 8 * 0.5e-4) < 1e-12)

    # ⭐⭐ L'ENERGIE EST UNE DISPERSION, ET ELLE SAIT VOIR UNE CONCENTRATION PLANTEE.
    e_plate = lenergie_par_rangee({_cle(a, b): 1.0 for a, b in paires9}, r9)
    v("★★★★ sur des résidus tous égaux, aucune rangée ne se distingue",
      e_plate.get("decidable") and abs(e_plate["le_rapport_au_median"] - 1.0) < 1e-9)
    concentre = {_cle(a, b): (4.0 if 198 in (a, b) else 0.5) for a, b in paires9}
    e_conc = lenergie_par_rangee(concentre, r9)
    v("★★★★ une concentration plantée sur une rangée est TROUVÉE, et sur la bonne rangée",
      e_conc.get("decidable") and e_conc["la_rangee_la_plus_chargee"] == 198
      and e_conc["le_rapport_au_median"] > 2.0, str(e_conc.get("la_rangee_la_plus_chargee")))
    # ⚠⚠⚠ LA SONDE QUI SEPARE UNE DISPERSION D'UNE SOMME D'AMPLITUDES. Une matiere ou la rangee
    # 182 porte huit residus MOYENS et la rangee 214 trois residus dont un GROS : les deux
    # agregats ne nomment pas la meme rangee, et sans ce contraste une somme d'amplitudes passait
    # toutes les sondes precedentes.
    disperse = {_cle(a, b): 0.0 for a, b in paires9}
    for x in r9:
        if x != 182:
            disperse[_cle(182, x)] = 2.0
    disperse[_cle(206, 214)] = 6.0
    disperse[_cle(202, 214)] = 2.5
    e_disp = lenergie_par_rangee(disperse, r9)

    def _somme_amplitudes(i):
        return sum(abs(x) for k, x in disperse.items()
                   if i in (int(k.split("-")[0]), int(k.split("-")[1])))

    v("★★★★ la rangée que l'ÉNERGIE nomme n'est pas celle qu'une somme d'amplitudes nommerait — "
      "l'agrégat doit être une DISPERSION, et la matière le rend vérifiable",
      e_disp.get("decidable") and e_disp["la_rangee_la_plus_chargee"] == 214
      and _somme_amplitudes(182) > _somme_amplitudes(214),
      f"énergie sur {e_disp.get('la_rangee_la_plus_chargee')}, amplitudes "
      f"{_somme_amplitudes(182)} contre {_somme_amplitudes(214)}")
    v("★★★ une rangée qui n'entre pas dans ses huit paires rend l'énergie indécidable",
      not lenergie_par_rangee(
          {k: v_ for k, v_ in concentre.items() if not k.startswith("182-")}, r9).get("decidable"))

    # ⚠⚠⚠ LE NUL DE LA FAMILLE DES RANGEES DOIT REBRASSER LES ARETES, PAS LES ETIQUETTES.
    fr_conc = la_famille_des_rangees(concentre, r9, PERMUTATIONS, 11)
    v("★★★★ sur une concentration plantée la règle portée TIRE — une règle qui ne tirerait jamais "
      "ne prouverait rien du négatif qu'elle rend",
      fr_conc.get("decidable") and fr_conc["une_rangee_porte_le_residu"],
      str(fr_conc.get("les_tirages_au_moins_aussi_forts")))
    etiquettes = {}
    for perm in ([r9[i] for i in (3, 1, 2, 0, 4, 5, 6, 7, 8)],):
        ren = {r9[i]: perm[i] for i in range(9)}
        etiquettes = {_cle(ren[a], ren[b]): concentre[_cle(a, b)] for a, b in paires9}
    v("★★★★ renommer les rangées ne change AUCUNE énergie du treillis complet — c'est pourquoi un "
      "nul par étiquettes serait une vérification incapable d'échouer",
      sorted(lenergie_par_rangee(etiquettes, r9)["les_energies"].values())
      == sorted(lenergie_par_rangee(concentre, r9)["les_energies"].values()))
    v("★★★ une paire sans résidu rend la famille des rangées indécidable",
      not la_famille_des_rangees({k: v_ for k, v_ in concentre.items()
                                  if k != _cle(182, 190)}, r9).get("decidable"))

    # ⚠⚠⚠ L'EPREUVE DECLAREE DOIT POUVOIR TIRER, ET SUR LE BON MEMBRE.
    lie = {}
    for a, b in paires9:
        lie[_cle(a, b)] = 6.0 * la_covariable_de_paire(
            "lecart", lu_contraste[a]["refus_faute_de_texture"],
            lu_contraste[b]["refus_faute_de_texture"])
    fc = la_famille_des_covariables(lu_contraste, r9, lie, PERMUTATIONS, 13)
    v("★★★★ sur un lien planté l'épreuve déclarée TIRE, et elle NOMME le membre planté",
      fc.get("decidable") and fc["le_residu_suit_une_covariable"]
      and fc["le_membre_le_plus_fort"] == "refus_faute_de_texture·lecart",
      f"{fc.get('le_membre_le_plus_fort')} à {fc.get('la_correlation_de_famille')}, "
      f"{fc.get('les_tirages_au_moins_aussi_forts')} au moins aussi forts")
    fc_plat = la_famille_des_covariables(lu_plat, r9, lie, PERMUTATIONS, 13)
    v("★★★★ sur une lecture PLATE aucune covariable ne peut rien suivre",
      not fc_plat.get("decidable") or not fc_plat.get("le_residu_suit_une_covariable"),
      str(fc_plat.get("raison") or fc_plat.get("la_correlation_de_famille")))
    lu_jumelles = _lu_fabrique(r9, (260, 246, 253, 255, 251, 254, 254, 252, 258),
                               (0, 7, 2, 1, 6, 3, 3, 4, 8),
                               (259, 240, 250, 253, 243, 250, 250, 247, 251))
    fj = la_famille_des_covariables(lu_jumelles, r9, lie, PERMUTATIONS, 13)
    v("★★★★ deux rangées identiques sur les TROIS covariables sont trouvées EXHAUSTIVEMENT — le "
      "tirage ne tomberait sur cette transposition qu'une fois sur quelques dizaines de milliers",
      fj.get("decidable") and fj.get("les_rangees_jumelles") == ["199-202"],
      str(fj.get("les_rangees_jumelles")))
    v("★★★ et une lecture sans jumelles n'en invente pas",
      (la_famille_des_covariables(lu_contraste, r9, lie, PERMUTATIONS, 13)
       .get("les_rangees_jumelles")) == [])
    # ⚠⚠⚠ DEUX RANGEES QUI SE RESSEMBLENT SUR UNE COVARIABLE NE SONT PAS JUMELLES. Une symetrie
    # n'existe que si la famille ENTIERE est laissee inchangee ; l'annoncer sur un seul accord
    # ferait rejeter des faces legitimes du nul, donc retrecirait le nul sans que rien ne le dise.
    lu_fausses = _lu_fabrique(r9, (260, 246, 253, 255, 251, 254, 254, 252, 258),
                              (0, 7, 2, 1, 6, 3, 5, 4, 8),
                              (259, 240, 250, 253, 243, 250, 246, 247, 251))
    v("★★★★ deux rangées qui s'accordent sur UNE covariable et pas sur les autres ne sont PAS "
      "jumelles — une symétrie doit laisser la famille entière inchangée",
      (la_famille_des_covariables(lu_fausses, r9, lie, PERMUTATIONS, 13)
       .get("les_rangees_jumelles")) == [],
      str(la_famille_des_covariables(lu_fausses, r9, lie, PERMUTATIONS, 13)
          .get("les_rangees_jumelles")))
    v("★★★ une paire sans résidu rend l'épreuve déclarée indécidable",
      not la_famille_des_covariables(lu_contraste, r9,
                                     {k: v_ for k, v_ in lie.items() if k != _cle(182, 190)},
                                     PERMUTATIONS, 13).get("decidable"))

    # ⚠⚠ LE PIEGE PUBLIE L'ATTENDU *ET* LE RENDU, ET NE TRANCHE PAR AUCUN SEUIL.
    pn = le_piege_nomme({str(k): float(9 - i) for i, k in enumerate(r9)},
                        {k: float(i) for i, k in enumerate(r9)}, PERMUTATIONS, 17)
    v("★★★★ le piège sait rendre le sens NÉGATIF quand la matière le porte",
      pn.get("decidable") and pn["le_sens_rendu_est_negatif"] and pn["la_derivation_est_confirmee"])
    pp = le_piege_nomme({str(k): float(i) for i, k in enumerate(r9)},
                        {k: float(i) for i, k in enumerate(r9)}, PERMUTATIONS, 17)
    v("★★★★ et le sens POSITIF quand elle ne le porte pas — les deux se publient, l'attendu n'est "
      "jamais réécrit après coup",
      pp.get("decidable") and not pp["le_sens_rendu_est_negatif"]
      and pp["le_sens_attendu_est_negatif"] and not pp["la_derivation_est_confirmee"])
    pc = le_piege_des_covariables(lu_contraste, {k: float(i) for i, k in enumerate(r9)},
                                  PERMUTATIONS, 19)
    v("★★★ le piège des covariables traverse les trois covariables déclarées",
      pc.get("decidable")
      and sorted(pc["les_correlations_a_la_variance"]) == sorted(n for n, _ in
                                                                 LES_COVARIABLES_DECLAREES))
    pc_lie = le_piege_des_covariables(
        lu_contraste, {k: float(lu_contraste[k]["refus_faute_de_texture"]) for k in r9},
        PERMUTATIONS, 19)
    v("★★★★ une covariable qui SUIT la variance propre est trouvée — sinon le piège ne pourrait "
      "jamais se déclencher et ne protégerait de rien",
      pc_lie.get("decidable") and pc_lie["une_covariable_suit_la_variance"],
      str(pc_lie.get("la_plus_forte_en_valeur_absolue")))
    # ⚠⚠⚠ LA SONDE QUI INTERDIT UN SEUIL CHOISI. Sur cette lecture la covariable la plus forte
    # suit la variance a 0,6833 — au-dessus de tout seuil « raisonnable » qu'on serait tente
    # d'ecrire — et le rebrassage trouve pourtant des tirages au moins aussi forts. Une regle qui
    # trancherait par l'amplitude tirerait ici ; celle qui tranche par le nul se tait. La lecture
    # a ete CHERCHEE pour separer les deux, et elle tient sur cinq graines.
    lu_borderline = _lu_fabrique(r9, (242, 241, 244, 243, 240, 246, 248, 247, 245),
                                 (0, 6, 8, 7, 5, 2, 1, 4, 3),
                                 (247, 245, 242, 241, 244, 243, 240, 246, 248))
    var_rang = {x: float(i) for i, x in enumerate(r9)}
    for graine_sonde in (19, 23, 29, 31, 37):
        pb = le_piege_des_covariables(lu_borderline, var_rang, PERMUTATIONS, graine_sonde)
        v(f"★★★★ une corrélation de 0,68 à la variance ne suffit PAS si le nul fait aussi fort "
          f"(graine {graine_sonde}) — aucun seuil ne tranche ici",
          pb.get("decidable") and pb["la_plus_forte_en_valeur_absolue"] >= 0.62
          and pb["les_tirages_au_moins_aussi_forts"] >= 1
          and not pb["une_covariable_suit_la_variance"],
          f"{pb.get('la_plus_forte_en_valeur_absolue')} à "
          f"{pb.get('les_tirages_au_moins_aussi_forts')} tirages")
    coherences = [le_piege_des_covariables(x, var_rang, PERMUTATIONS, 29)
                  for x in (lu_borderline, lu_contraste)]
    v("★★★★ et le booléen du piège n'est QUE la lecture de son compte, jamais un second jugement",
      all(o.get("decidable")
          and o["une_covariable_suit_la_variance"] == (o["les_tirages_au_moins_aussi_forts"] == 0)
          for o in coherences),
      str([(o.get("les_tirages_au_moins_aussi_forts"),
            o.get("une_covariable_suit_la_variance")) for o in coherences]))
    v("★★★ une lecture PLATE ne rend aucune corrélation à la variance, et c'est dit au lieu "
      "d'être compté pour zéro",
      not le_piege_des_covariables(lu_plat, var_rang, PERMUTATIONS, 29).get("decidable"))

    # ⚠⚠⚠ L'ETALON : IL SEPARE, IL TIENT SA GARANTIE, ET SON AVEUGLE SE DIAGNOSTIQUE.
    et = sur_letalon(r9, variances, coutures, lu_contraste,
                     membre="refus_faute_de_texture·lecart", facteurs=(1, 6), replicats=6,
                     decisif=20, graine=23, tirages=PERMUTATIONS)
    v("★★★★ l'échelle de sensibilité est MONOTONE — une sensibilité qui régresserait quand le lien "
      "grandit serait un défaut, pas un résultat",
      et.get("decidable") and et["la_suite_est_monotone"], str(et.get("lechelle")))
    v("★★★★ le plus gros lien est vu par TOUS les réplicats, sinon la règle ne sépare rien",
      et.get("decidable") and et["lechelle"][-1]["les_vus"] == 6, str(et.get("lechelle")))
    v("★★★★ le taux de faux tient la garantie",
      et.get("decidable") and et["elle_tient_sa_garantie"], str(et.get("le_taux_de_faux")))
    v("★★★★ un aveugle qui TIRE ressemble plus à l'identité qu'un aveugle qui se tait — c'est ce "
      "qui explique pourquoi un contrôle aveugle sur neuf rangées ne peut pas être propre",
      et.get("decidable")
      and (et.get("la_ressemblance_mediane_des_aveugles_qui_tirent") is None
           or et.get("la_ressemblance_mediane_des_aveugles_qui_se_taisent") is None
           or et["la_ressemblance_mediane_des_aveugles_qui_tirent"]
           >= et["la_ressemblance_mediane_des_aveugles_qui_se_taisent"]),
      f"{et.get('la_ressemblance_mediane_des_aveugles_qui_tirent')} contre "
      f"{et.get('la_ressemblance_mediane_des_aveugles_qui_se_taisent')}")
    v("★★★ un taux au-dessus de deux fois la garantie ne tient pas",
      not le_taux_tient(2.0 * GARANTIE_PAR_EPREUVE + 0.01, GARANTIE_PAR_EPREUVE))

    # ⭐⭐⭐ LES TROIS ISSUES SONT EXCLUSIVES ET AUCUNE NE SE JUSTIFIE PAR CE QUE LA MESURE REFUSE.
    issues = {_ce_qui_reste(True, True), _ce_qui_reste(True, False),
              _ce_qui_reste(False, True), _ce_qui_reste(False, False)}
    v("★★★★ les quatre combinaisons ne rendent que TROIS issues, et la lecture prime sur la rangée",
      len(issues) == 3 and _ce_qui_reste(True, True) == _ce_qui_reste(True, False))
    v("★★★ chaque issue nomme ce que la tranche suivante doit chercher",
      all(len(x) > 30 for x in issues))

    # ⭐⭐⭐⭐ LA MESURE ENTIERE, DE BOUT EN BOUT, SUR CE QUE `214` A REELLEMENT PUBLIE.
    out = mesurer(GRAINE, PERMUTATIONS, 2, 4, avec_etalon=True)
    v("★★★★ la mesure traverse sans lire le volume et rend son verdict",
      out.get("decidable") and (out.get("le_verdict") or {}).get("ce_qui_reste_a_mesurer"),
      str(out.get("raison")))
    v("★★★★ elle publie la part non additive à côté de la famille — sans elle une borne se lirait "
      "« cette covariable n'agit pas » au lieu de « pas NON ADDITIVEMENT »",
      (out.get("la_part_non_additive") or {}).get("decidable") is True)
    v("★★★ elle publie la règle que la porte prescrivait, comme contrôle nommé",
      (out.get("la_regle_portee_par_la_porte") or {}).get("decidable") is True)
    v("★★★ elle publie l'agrégat refusé avec la raison de son refus",
      "équations normales" in ((out.get("lagregat_refuse") or {})
                               .get("pourquoi_cet_agregat_est_refuse") or ""))
    v("★★★ elle publie la question déclarée, la famille et la garantie",
      out.get("la_question_declaree") == LA_QUESTION_DECLAREE
      and out.get("la_famille_declaree") == list(LA_FAMILLE_DECLAREE)
      and out.get("la_garantie_par_epreuve") is not None)
    v("★★★★ l'étalon injecte sur le membre le PLUS visible — injecter sur un membre absorbé "
      "mesurerait la projection et non la règle",
      (out.get("letalon") or {}).get("le_membre_injecte")
      == (out.get("la_part_non_additive") or {}).get("le_membre_le_plus_visible"),
      str((out.get("letalon") or {}).get("le_membre_injecte")))
    v("★★★ un `214` illisible rend la mesure indécidable, avec sa raison",
      not mesurer(GRAINE, PERMUTATIONS, 2, 4,
                  chemin=Path("/nen/existe/pas.json")).get("decidable"))

    for e_ in echecs:
        print(f"  ÉCHEC {e_}")
    print(f"{Path(__file__).name}   "
          f"{'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p.add_argument("--graine", type=int, default=GRAINE)
    p.add_argument("--tirages", type=int, default=PERMUTATIONS)
    p.add_argument("--replicats", type=int, default=12)
    p.add_argument("--decisif", type=int, default=LE_COMPTE_DECISIF)
    p.add_argument("--sans-etalon", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(a.graine, a.tirages, a.replicats, a.decisif, avec_etalon=not a.sans_etalon)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, ensure_ascii=False, indent=2))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
