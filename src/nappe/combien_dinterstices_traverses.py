#!/usr/bin/env python3
"""Combien d'interstices entre une cellule et son point de fermeture ? Le critere que la MATIERE
tranche.

⚠⚠⚠ POURQUOI CE FICHIER, ET C'EST `97` QUI L'A IMPOSE. Quatre tranches ont ferme la question du
signal de confiance : le pli (`94`) et la pose sur la matiere (`95`) sont ANTI-predictifs, la
fermeture d'un tour (`96`) a le bon signe mais aucun etalon, et `97` a mesure pourquoi — deux
traces humains INDEPENDANTS de la meme matiere divergent de plus d'une DEMI-feuille partout, et
de plus d'une feuille entiere sur un tiers des points. Donc **aucun signal mesure contre un
maillage humain ne peut etre calibre**, parce que le maillage humain n'a pas de valeur unique.

⭐⭐⭐ IL FAUT DONC UN CRITERE QUE LA MATIERE TRANCHE, ET IL S'ENONCE EN UNE PHRASE. Une feuille
de papyrus est un ruban BRILLANT et l'espace entre deux feuilles est SOMBRE. Entre une cellule et
son point de fermeture un pas de feuille plus loin, le profil d'intensite doit donc valoir
**brillant – sombre – brillant** : exactement UN interstice. Zero voudrait dire qu'on est revenu
sur la meme feuille, deux qu'on en a saute une. Aucun maillage n'entre dans cet enonce, aucun
oracle, aucune supervision.

⭐⭐⭐ ET L'INSTRUMENT EST UN FILTRE ADAPTE, PAS UN COMPTEUR DE MINIMA. La correlation normalisee
du profil a un gabarit `brillant-sombre-...-brillant` est **invariante en amplitude ET en
decalage**, donc il n'y a RIEN a adapter — ni au rouleau, ni a la bande, ni au profil. Mesure sur
modeles nuls fabriques : le filtre choisit le bon nombre d'interstices **100 % du temps**, de
sigma = 2 jusqu'a sigma = 40, c'est-a-dire pour un bruit EGAL a l'amplitude du signal ; et sur du
bruit PUR son score tombe a **0,111** contre 0,579 au pire cas reel.

⚠⚠ CE QUI REPOND A LA QUESTION DE L'AUTEUR — « il faut etre adaptatif par rapport au rouleau
teste ? » — ET LA REND PLUS FORTE. La mesure montre d'abord qu'un seuil absolu est sans espoir :
dans UNE SEULE bande du bord, l'etendue du profil varie d'un facteur **146** (p10 = 0,
p90 = 146 niveaux), et d'un facteur 2,4 au milieu. Une constante par ROULEAU serait donc deja un
parametre ajuste. Mais la bonne reponse n'est pas d'adapter le seuil : c'est de choisir une
quantite qui n'en a pas besoin. Une correlation normalisee est cette quantite.

⛔⛔ ET LE COMPTEUR DE MINIMA EST REFUTE, GARDE, PARCE QUE SON ECHEC A UNE RAISON QUI SE
GENERALISE. Compter les minima PROEMINENTS ne discrimine pas : a la proeminence qui rejette le
bruit pur (×6) un interstice reel n'est vu que 12,5 % du temps, et a basse proeminence le bruit
passe a 87,5 %. Lisser le profil fait monter la detection a 0,95 mais ne change RIEN aux faux
positifs (0,6 a 1,0), et la raison est structurelle : **une proeminence exprimee en unites du
bruit propre au profil est invariante d'echelle, donc lisser abaisse le bruit ET le seuil
ensemble**. La discrimination ne peut pas venir de la profondeur ; elle vient de la FORME.

⚠ Et la matiere peut se taire : un profil dont le meilleur accord n'atteint pas ce qu'un bruit
pur atteint deja n'est pas « zero interstice », c'est « on ne sait pas ». Deux faits opposes
qu'un compte unique melangerait.

Usage :
    uv run python src/nappe/combien_dinterstices_traverses.py --verifier
    uv run python src/nappe/combien_dinterstices_traverses.py \\
        --json docs/mesures/combien_dinterstices_traverses.json
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

ALIGNEMENT = RACINE / "docs" / "mesures" / "deux_modes_dechec_du_transfert.json"
CONTINUITE = RACINE / "docs" / "mesures" / "la_continuite_des_transferts.json"

OBJET = "PHercParis4"
VOLUME_DU_MAILLAGE = "20260310170716"
VOLUME_FIN = "20260411134726"
ZARR_FIN = f"{OBJET}/volumes/{VOLUME_FIN}-2.400um-0.2m-78keV-masked.zarr"
VOXEL_FIN_UM = 2.4
VOXEL_MAILLAGE_UM = 45.532
PAS_UM = 173.0

# ⚠ Le segment est echantillonne au voxel FIN : 173 µm de pas de feuille pour 2,4 µm de voxel
# font 73 echantillons. Plus fin ne lirait que du bruit, plus grossier pourrait enjamber un
# interstice entier — ce qui est precisement l'evenement qu'on compte.
ECHANTILLONS = 73
# ⚠⚠ LA PROEMINENCE EST EN UNITES DU BRUIT PROPRE AU PROFIL, ET C'EST TOUT L'INSTRUMENT. Trois
# fois le bruit est le defaut, et le BALAYAGE est publie : un verdict qui ne tiendrait qu'a une
# valeur serait un nombre choisi pour qu'il passe.
PROEMINENCE = 3.0
PROEMINENCES_BALAYEES = (2.0, 3.0, 4.0, 6.0)
CELLULES_PAR_BANDE = 200


def gabarit(interstices_attendus: int, sur_la_feuille: bool = True,
            echantillons: int = ECHANTILLONS) -> np.ndarray:
    """Le profil ATTENDU, centre et normalise, pour `k` interstices sur un pas de feuille.

    ⭐⭐ LA FORME VIENT DE LA MATIERE ET DE RIEN D'AUTRE. Le segment part de la cellule du
    maillage et arrive un pas de feuille plus loin, radialement. Si la cellule est SUR une
    feuille, il commence brillant, finit brillant, et traverse `k` creux entre les deux : c'est
    `+cos(2πkt)`. Si elle est dans un INTERSTICE, tout est decale d'un demi-pas et le profil
    commence sombre : c'est `-cos(2πkt)`.

    ⚠⚠⚠ ET LE SIGNE EST UNE CORRECTION, TROUVEE EN LISANT LES COMPTES. Ma premiere famille etait
    `-cos(2π(k+1)t)`, qui commence et finit SOMBRE : elle appariait 40 % des profils reels a un
    gabarit dont la lecture correcte est « la cellule est dans un interstice », et je publiais ce
    compte sous le nom « zero interstice ». Deux etats differents sous une seule etiquette.

    ⚠⚠ Et « zero interstice » n'est PAS exprimable en cosinus normalise : un segment qui reste
    sur la meme feuille est brillant de bout en bout, donc plat, donc de norme nulle apres
    centrage. C'est le cas SANS ACCORD, et il est deja couvert par le modele nul — le confondre
    avec un gabarit aurait fabrique une reponse la ou la matiere n'en donne pas.
    """
    if interstices_attendus < 1:
        raise ValueError("un gabarit demande au moins un interstice ; zero est le cas sans accord")
    t = np.linspace(0.0, 1.0, echantillons)
    g = np.cos(2 * np.pi * interstices_attendus * t)
    if not sur_la_feuille:
        g = -g
    g = g - g.mean()
    return g / np.linalg.norm(g)


INTERSTICES_TESTES = (1, 2, 3)
GABARITS = {(k, sur): gabarit(k, sur)
            for k in INTERSTICES_TESTES for sur in (True, False)}
CLEFS = sorted(GABARITS)


def accord(v: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Le nombre d'interstices du gabarit le mieux accorde, s'il part SUR la feuille, et le score.

    ⭐⭐⭐ C'EST L'INSTRUMENT DU FICHIER, ET IL N'A AUCUN PARAMETRE A REGLER. Le profil est centre
    et normalise, donc le score ne depend ni de la brillance locale ni du contraste : deux
    profils de meme FORME et d'amplitudes differentes rendent le meme score. C'est cette double
    invariance qui dispense d'adapter quoi que ce soit au rouleau — la question de l'auteur — et
    la mesure montre qu'un seuil absolu serait de toute facon sans espoir, l'etendue du profil
    variant d'un facteur 146 a l'interieur d'une seule bande du bord.

    ⚠ Le score EST le juge de « la matiere a-t-elle repondu » : un profil dont le meilleur accord
    n'atteint pas ce qu'un bruit pur atteint deja n'a rien dit, et son compte ne doit pas etre lu.
    """
    v = np.atleast_2d(np.asarray(v, dtype=np.float64))
    z = v - v.mean(axis=1, keepdims=True)
    z = z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
    scores = np.stack([z @ GABARITS[c] for c in CLEFS], axis=1)
    meilleur = scores.argmax(axis=1)
    combien = np.array([CLEFS[i][0] for i in meilleur])
    sur = np.array([CLEFS[i][1] for i in meilleur])
    # ⭐⭐⭐ LA MARGE ENTRE LES DEUX POLARITES EST RENDUE, ET SANS ELLE LE VERDICT DE POLARITE EST
    # ILLISIBLE. « La cellule part sur la feuille » ressort a 0,49 sur le reel, soit exactement
    # le hasard — et deux lectures opposees donnent ce nombre : soit le maillage est reellement
    # dans un interstice une fois sur deux, soit les deux gabarits sont a egalite et l'argmax est
    # un tirage. Seule la MARGE les distingue, donc la publier est ce qui empeche de lire un
    # tirage comme une mesure.
    idx_sur = [i for i, c in enumerate(CLEFS) if c[1]]
    idx_dans = [i for i, c in enumerate(CLEFS) if not c[1]]
    marge = scores[:, idx_sur].max(axis=1) - scores[:, idx_dans].max(axis=1)
    return combien, sur, scores.max(axis=1), marge


# ⚠⚠⚠ LE PLANCHER DE `accord`, ET C'EST `104` QUI L'A MESURE. La famille de gabarits est
# {1, 2, 3}, donc `combien` ne peut JAMAIS valoir moins de un : un segment qui ne franchit que
# 0,82 feuille rend « 1 interstice » avec un score de 0,781, tres au-dessus de la barre du bruit
# pur (0,331). Le compteur voit donc un SAUT (2 ou 3) et il est AVEUGLE A UN RETARD. Enchaine,
# un retard systematique est bien pire qu'une chute : une chute se voit, un retard s'accumule en
# silence. C'est pour ca que la famille CONTINUE ci-dessous existe.
F_MIN = 0.35
F_MAX = 3.2
PAS_DE_F = 0.005


def feuilles_franchies(v: np.ndarray, f_min: float = F_MIN, f_max: float = F_MAX,
                       pas: float = PAS_DE_F
                       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """La fraction de feuille que le segment a franchie, le score de l'ajustement, et la butee.

    ⭐⭐⭐ ELLE REMPLACE `accord` POUR LA QUANTITE, ET ELLE EXISTE PARCE QUE LE COMPTEUR ENTIER NE
    SAIT PAS DIRE « MOINS D'UNE FEUILLE ». La famille est continue, donc la reponse est un reel :
    0,82 se lit 0,82 au lieu de 1. Sur une pile fabriquee oblique la valeur rendue est cos(theta)
    a trois decimales pres pour quatre obliquites — c'est la calibration, et elle est ce qui
    transforme cette fonction d'une idee en un instrument.

    ⚠⚠⚠ SON SCORE PORTE LA BARRE DE SA PROPRE FORME, ET C'EST UNE CORRECTION DE CE QUE J'AVAIS
    ECRIT ICI. J'avais affirme qu'une famille continue « trouve toujours une frequence qui colle,
    donc son score reste haut sur du bruit », donc qu'il ne pouvait pas servir de garde. La mesure
    dit autre chose : sur du bruit pur son p99 vaut 0,396 contre 0,349 pour la famille a trois
    gabarits — plus haut, comme mille cent quarante-deux gabarits doivent l'etre, mais de treize
    pour cent seulement. Son score EST donc utilisable, a condition de prendre la barre de SA
    forme et non celle de `accord` (0,331), qui serait trop permissive. C'est exactement la regle
    que `103` a deja ecrite pour le nul du tenseur.

    ⚠⚠ ET LA BUTEE EST RENDUE, PAS AVALEE. Une fraction qui tombe sur `f_min` ou `f_max` dit « au
    plus » ou « au moins », jamais « exactement » : sur du bruit pur la valeur sature en haut de
    la fenetre une fois sur deux. La publier comme une mesure ferait passer une limite de FENETRE
    pour une limite de MATIERE, ce que ce depot a deja paye en `99`.

    ⚠⚠ ELLE REFUSE SOUS `f_min` PLUTOT QUE D'ECRETER. Sous un tiers de periode un segment n'a
    plus la forme d'une oscillation mais celle d'une pente, et la fraction n'y est pas mesurable :
    la borne rend donc NaN, qui se lit « injugeable », et non `f_min`, qui se lirait comme une
    mesure. Un ecretage y ferait passer un segment sans forme pour un tiers de feuille.
    """
    v = np.atleast_2d(np.asarray(v, dtype=np.float64))
    z = v - v.mean(axis=1, keepdims=True)
    n = np.linalg.norm(z, axis=1, keepdims=True)
    z = z / np.maximum(n, 1e-12)
    t = np.linspace(0.0, 1.0, v.shape[1])
    fs = np.arange(f_min, f_max + 1e-9, pas)
    g = np.cos(2 * np.pi * fs[:, None] * t[None, :])
    g = g - g.mean(axis=1, keepdims=True)
    g = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    # ⚠ Les DEUX polarites, comme `accord` : un segment qui part d'un interstice a le profil
    # oppose, et n'en essayer qu'une rendrait la moitie des segments injugeables.
    sc = np.maximum(z @ g.T, z @ (-g.T))
    i = sc.argmax(axis=1)
    f = fs[i]
    meilleur = sc[np.arange(len(z)), i]
    # ⚠ Un profil plat n'a pas de fraction : sa norme est nulle apres centrage, donc toute
    # correlation est arbitraire. Il est declare injugeable au lieu de recevoir un argmax.
    plat = (n[:, 0] <= 1e-12)
    f = np.where(plat, np.nan, f)
    meilleur = np.where(plat, np.nan, meilleur)
    en_butee = (~plat) & ((i == 0) | (i == len(fs) - 1))
    return f, meilleur, en_butee


def nul_de_lestimateur_continu(tirages: int = 400, graine: int = 57) -> dict:
    """Ce que la famille CONTINUE rend sur du bruit pur, a cote de ce que rend celle a trois.

    ⭐⭐⭐ ELLE EXISTE PARCE QUE MA PREMIERE VERSION DE CE FICHIER AFFIRMAIT UNE DIRECTION SANS LA
    MESURER. J'avais ecrit que le score continu etait inutilisable comme garde ; la comparaison
    des deux nuls, p99 contre p99, dit qu'il l'est a 13 % pres. Ce qui compte n'est donc pas
    d'ecarter ce score mais de lui donner la barre de SA forme.

    ⚠ La fraction rendue sur du bruit est publiee aussi, et pour une raison precise : si elle se
    concentrait autour de UN, l'estimateur serait biaise vers la reponse attendue, ce qui est le
    pire defaut possible pour un instrument dont tout l'objet est de detecter un ecart a un.
    """
    r = np.random.default_rng(graine)
    out = {}
    for sigma in (2.0, 10.0, 40.0):
        v = r.normal(100.0, sigma, size=(tirages, ECHANTILLONS))
        f, sc, bu = feuilles_franchies(v)
        _, _, sd, _ = accord(v)
        out[f"sigma_{sigma:.0f}"] = {
            "continue_median": round(float(np.median(sc)), 4),
            "continue_p99": round(float(np.percentile(sc, 99)), 4),
            "trois_gabarits_median": round(float(np.median(sd)), 4),
            "trois_gabarits_p99": round(float(np.percentile(sd, 99)), 4),
            "fraction_mediane": round(float(np.median(f)), 3),
            "part_en_butee": round(float(np.mean(bu)), 3),
        }
    pires = [x for k, x in out.items() if k.startswith("sigma_")]
    out["barre_de_la_famille_continue"] = round(max(x["continue_p99"] for x in pires), 4)
    out["barre_de_la_famille_a_trois"] = round(max(x["trois_gabarits_p99"] for x in pires), 4)
    # ⭐⭐ LE VERDICT EST UNE COMPARAISON, PAS UNE AFFIRMATION : la barre de `98` est-elle trop
    # permissive pour ce score-la ? Si oui, chaque famille porte la barre de sa forme.
    out["la_barre_a_trois_gabarits_serait_trop_permissive"] = bool(
        out["barre_de_la_famille_continue"] > out["barre_de_la_famille_a_trois"])
    out["de_combien_en_pourcent"] = round(
        100.0 * (out["barre_de_la_famille_continue"] / out["barre_de_la_famille_a_trois"] - 1.0), 1)
    # ⚠ Un estimateur biaise vers un serait pire qu'un estimateur bruyant.
    out["sa_fraction_nest_pas_biaisee_vers_un"] = bool(
        not any(0.9 <= x["fraction_mediane"] <= 1.1 for x in pires))
    return out


def accord_du_bruit_pur(tirages: int = 400, graine: int = 91) -> dict:
    """Ce que le filtre rend sur du BRUIT PUR : le modele nul, fabrique.

    ⭐⭐⭐ C'EST LUI QUI DONNE LE SEUIL, ET IL NE VIENT PAS DES DONNEES. Un accord qu'un bruit
    blanc atteint deja ne dit rien ; le percentile haut du nul est donc la barre, et elle est
    calculable sans regarder le rouleau. C'est la seule facon d'avoir un seuil que ni un maillage
    humain ni un reglage n'ont fixe — et `97` a montre qu'un maillage humain ne peut pas le fixer.

    ⚠ Le nul est independant de l'ecart-type du bruit, ce qui est le CONTROLE de l'invariance
    d'echelle : si le score du nul dependait de sigma, le filtre aurait un parametre cache.
    """
    r = np.random.default_rng(graine)
    out = {}
    for sigma in (2.0, 10.0, 40.0):
        v = r.normal(100.0, sigma, size=(tirages, ECHANTILLONS))
        _, _, sc, _ = accord(v)
        out[f"sigma_{sigma:.0f}"] = {
            "median": round(float(np.median(sc)), 4),
            "p95": round(float(np.percentile(sc, 95)), 4),
            "p99": round(float(np.percentile(sc, 99)), 4),
        }
    return out


def bruit_du_profil(v: np.ndarray) -> np.ndarray:
    """Le grain du scan, estime par les differences SECONDES et non premieres.

    ⭐⭐ C'EST CE QUI REND LE CRITERE ADAPTATIF SANS AUCUNE CONSTANTE : le bruit est mesure par
    profil, et non par bande ni par rouleau, ce qui est la granularite la plus fine disponible —
    l'etendue du profil varie d'un facteur 146 a l'interieur d'une seule bande du bord.

    ⚠⚠⚠ ET LA DIFFERENCE SECONDE EST UNE CORRECTION, PAS UN RAFFINEMENT. Ma premiere version
    prenait la difference PREMIERE, qui lit aussi la PENTE de la structure qu'on cherche a
    compter : un interstice d'amplitude 40 sur 73 echantillons a des differences successives de
    ~6,9 niveaux, donc l'estimateur confondait le signal avec le grain. Mesure du defaut : il
    n'existait AUCUN point de fonctionnement — a la proeminence qui rejette le bruit pur (×6),
    un interstice reel n'etait vu que 12,5 % du temps, et a basse proeminence le bruit passait
    a 87,5 %.

    ⭐ Une difference seconde est insensible a une pente : pour une structure lisse d'amplitude
    40 elle vaut ~0,3 niveau, quand pour du bruit blanc d'ecart-type sigma elle vaut sigma·√6.
    Le facteur √6 est divise pour que le nombre rendu soit comparable a un ecart-type.
    """
    d2 = np.diff(v, n=2, axis=-1)
    return np.median(np.abs(d2), axis=-1) / np.sqrt(6.0)


def profil_muet(v: np.ndarray, bruit: np.ndarray, facteur: float = 4.0) -> np.ndarray:
    """Les profils ou la matiere ne repond pas : trop plats pour porter un interstice.

    ⚠⚠⚠ LE CAS DEGENERE EST TRAITE A PART, ET C'EST UN DEFAUT QUE LA SONDE A ATTRAPE. Un profil
    EXACTEMENT constant a une etendue nulle ET un bruit nul, donc `etendue < facteur * bruit`
    vaut `0 < 0`, c'est-a-dire FAUX : il ressortait « non muet » et son compte d'interstices
    valait zero, ce qui se lit comme « meme feuille » au lieu de « on ne sait pas ». Deux faits
    opposes confondus par une comparaison qui ne peut pas les distinguer.
    """
    etendue = v.max(axis=-1) - v.min(axis=-1)
    return (etendue <= 0) | (etendue < facteur * bruit)


def interstices(v: np.ndarray, bruit: np.ndarray,
                proeminence: float = PROEMINENCE) -> np.ndarray:
    """Combien de minima PROEMINENTS le profil traverse, par profil.

    ⭐⭐⭐ UN MINIMUM N'EST COMPTE QUE S'IL REMONTE DES DEUX COTES de plus que la proeminence
    demandee. C'est ce qui distingue un interstice d'un creux de bruit sans qu'aucun seuil
    d'intensite absolue n'entre : la proeminence est mesuree en unites du bruit PROPRE au profil,
    donc le critere s'adapte a chaque profil et non au rouleau.

    ⚠ Les extremites sont EXCLUES : un profil qui descend jusqu'a son dernier echantillon n'a
    pas montre qu'il remonte, donc l'appeler un interstice serait deviner ce qui vient apres.
    C'est la meme raison qui interdit d'extrapoler une fermeture au-dela d'un rang.
    """
    v = np.atleast_2d(v)
    bruit = np.atleast_1d(bruit)
    seuil = np.maximum(proeminence * bruit, 1e-9)
    compte = np.zeros(len(v), dtype=np.int64)
    for k in range(len(v)):
        y = v[k]
        n = len(y)
        for i in range(1, n - 1):
            if not (y[i] <= y[i - 1] and y[i] <= y[i + 1]):
                continue
            # ⚠ La remontee se cherche de part et d'autre JUSQU'A un maximum local, pas sur une
            # fenetre fixe : une fenetre fixe couperait la remontee d'un interstice large et
            # laisserait passer celle d'un creux etroit.
            g = y[i]
            j = i
            while j > 0 and y[j - 1] >= y[j]:
                j -= 1
                g = max(g, y[j])
            d = y[i]
            j = i
            while j < n - 1 and y[j + 1] >= y[j]:
                j += 1
                d = max(d, y[j])
            if min(g, d) - y[i] >= seuil[k]:
                compte[k] += 1
    return compte


def segments(a: np.ndarray, ok: np.ndarray, bords: np.ndarray, cx: np.ndarray,
             cy: np.ndarray, indices: np.ndarray,
             pas_um: float = PAS_UM) -> np.ndarray:
    """Les points a lire : de chaque cellule choisie jusqu'a UN PAS DE FEUILLE plus loin, radial.

    ⚠⚠ LE SEGMENT EST RADIAL ET A z CONSTANT. Le suivre le long de la spire au lieu de
    radialement mesurerait la feuille et non l'espace entre deux feuilles.

    ⛔⛔⛔ CORRECTION D'UNE AFFIRMATION QUI ETAIT ECRITE ICI ET QUI EST MESUREE FAUSSE. Cette
    docstring disait « donc il traverse l'empilement perpendiculairement ». `100` a mesure que non :
    la normale de la nappe est a **16 a 38°** du rayon, la ou une spirale de ce pas en predirait
    **0,06 a 0,35°**, et deux estimateurs sans hypothese commune s'accordent dessus. Le segment
    radial coupe donc l'empilement DE BIAIS.

    ⭐⭐⭐ ET CE QUI SAUVE LA MESURE N'EST PAS CE QUI ETAIT ECRIT, C'EST UN AUTRE RESULTAT DE `100` :
    le pas lu le long de la NORMALE egale le pas lu radialement (rapports 0,91 a 1,19 disperses
    autour de 1,00, aucun 1/cos systematique), sur un instrument dont le controle montre qu'il VOIT
    l'obliquite quand elle existe. La direction du segment ne change donc pas ce qui est mesure —
    mais pour une raison qui reste inexpliquee, pas parce que le segment serait perpendiculaire.

    ⚠⚠⚠ ET LE CENTRE EST INTERPOLE EN z, PAS PRIS PAR TRANCHE — c'est le defaut que `96` a paye :
    `axe_par_tranche` rend un centre constant par tranche et l'axe derive de 12,6 mm, donc deux
    cellules qui enjambent une frontiere de tranche voient des centres ecartes de centaines de
    micrometres, et l'ecart tombe dans la direction du segment.
    """
    milieux = (bords[:-1] + bords[1:]) / 2.0
    bon = np.isfinite(cx) & np.isfinite(cy)
    ccx = np.interp(a[..., 2], milieux[bon], cx[bon])
    ccy = np.interp(a[..., 2], milieux[bon], cy[bon])
    r = indices[:, 0], indices[:, 1]
    p0 = a[r]
    c0 = np.stack([ccx[r], ccy[r]], axis=-1)
    rayon = np.linalg.norm(p0[:, :2] - c0, axis=-1)
    theta = np.arctan2(p0[:, 1] - c0[:, 1], p0[:, 0] - c0[:, 0])
    pas_vx = pas_um / VOXEL_MAILLAGE_UM
    p1 = np.stack([c0[:, 0] + (rayon + pas_vx) * np.cos(theta),
                   c0[:, 1] + (rayon + pas_vx) * np.sin(theta),
                   p0[:, 2]], axis=-1)
    t = np.linspace(0.0, 1.0, ECHANTILLONS)
    del ok
    return p0[:, None, :] + (p1 - p0)[:, None, :] * t[None, :, None]


def echantillonner(bon: np.ndarray, combien: int, graine: int) -> np.ndarray:
    """Des cellules valides tirees uniformement."""
    ou = np.argwhere(bon)
    if len(ou) == 0 or len(ou) <= combien:
        return ou
    r = np.random.default_rng(graine)
    return ou[r.choice(len(ou), size=combien, replace=False)]


def correlation(x, y) -> float:
    """Le coefficient de Pearson, ou 0 si l'un des deux ne varie pas."""
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def mesurer(cellules: int = CELLULES_PAR_BANDE, graine: int = 23,
            bandes_max: int | None = None, fils: int = 32) -> dict:
    import laxe_est_une_courbe as A  # noqa: PLC0415
    import le_pas_lu_sur_les_transferts as P  # noqa: PLC0415
    import le_sens_du_rang as R  # noqa: PLC0415
    from transformations_de_volume import appliquer, echelle, matrice  # noqa: PLC0415
    from voxel_distant import BUCKET, VolumeZarr  # noqa: PLC0415

    al = ({(x["de"], x["a"]): x for x in json.loads(ALIGNEMENT.read_text())["lignes"]}
          if ALIGNEMENT.is_file() else {})
    co = ({(x["de"], x["a"]): x for x in json.loads(CONTINUITE.read_text())["lignes"]}
          if CONTINUITE.is_file() else {})
    m = matrice(OBJET, VOLUME_DU_MAILLAGE, VOLUME_FIN)
    if m is None:
        return {"message": "transformation vers le volume fin absente des métadonnées"}
    try:
        vol = VolumeZarr(f"{BUCKET}/{ZARR_FIN}")
    except RuntimeError as e:
        return {"message": f"volume fin injoignable : {e}"}

    nul = accord_du_bruit_pur()
    # ⭐⭐⭐ LA BARRE VIENT DU MODELE NUL, PAS DES DONNEES : le p99 du bruit pur, pris sur le
    # sigma le plus defavorable. Un accord en dessous est un accord qu'un bruit blanc atteint,
    # donc il ne dit rien — et le seuil n'a ete fixe ni par un maillage humain ni par un reglage.
    barre = max(x["p99"] for x in nul.values())

    bandes = R.bandes_du_fragment()[:bandes_max]
    nuages = [n for n in (R.points(x["recente"]) for x in bandes) if n is not None and len(n)]
    if len(nuages) < 2:
        return {"message": "cache incomplet : lancer `le_sens_du_rang --telecharger`"}
    bords, cx, cy, _, _ = A.axe_par_tranche(np.concatenate(nuages))

    lignes = []
    for x in bandes:
        cle = (x["de"], x["a"])
        g = P.grille(x["recente"])
        if g is None:
            continue
        a, ok = g
        ind = echantillonner(ok, cellules, graine + x["de"])
        if len(ind) < 30:
            continue
        seg = segments(a, ok, bords, cx, cy, ind)
        zyx = np.rint(appliquer(m, seg)).astype(np.int64)
        dedans = vol.dans_le_volume(zyx.reshape(-1, 3)).reshape(zyx.shape[:2]).all(axis=1)
        if int(dedans.sum()) < 20:
            lignes.append(dict(de=x["de"], a=x["a"], rayon_mm=al.get(cle, {}).get("rayon_mm"),
                               mesurable=False, cellules=0))
            continue
        v = vol.lire(zyx[dedans].reshape(-1, 3), fils=fils).reshape(int(dedans.sum()),
                                                                    ECHANTILLONS)
        fini = np.isfinite(v).all(axis=1)
        if int(fini.sum()) < 20:
            lignes.append(dict(de=x["de"], a=x["a"], rayon_mm=al.get(cle, {}).get("rayon_mm"),
                               mesurable=False, cellules=int(fini.sum())))
            continue
        v = v[fini]
        n_choisi, sur_la_feuille, score, marge = accord(v)
        # ⚠⚠ « LA MATIERE A REPONDU » EST UNE QUESTION SEPAREE DE « COMBIEN D'INTERSTICES », et
        # les melanger ferait lire un profil illisible comme « zero interstice », c'est-a-dire
        # comme « meme feuille » — l'inverse d'une absence de mesure.
        lu = score > barre
        # ⛔ L'ESTIMATEUR REFUTE, GARDE : le compteur de minima proeminents, dont la mesure sur
        # modeles nuls montre qu'il n'a AUCUN point de fonctionnement.
        br = bruit_du_profil(v)
        compte_minima = interstices(v, br)
        d = dict(
            de=x["de"], a=x["a"], mesurable=True,
            rayon_mm=al.get(cle, {}).get("rayon_mm"),
            desalignement=al.get(cle, {}).get("rapport_au_plancher"),
            continuite=co.get(cle, {}).get("rapport_interieur"),
            cellules=int(len(v)),
            part_lue=round(float(lu.mean()), 3),
            accord_median=round(float(np.median(score)), 4),
        )
        if int(lu.sum()) >= 10:
            n = n_choisi[lu]
            sur = sur_la_feuille[lu]
            d.update({
                # ⭐⭐⭐ LA QUANTITE PORTEUSE : la part des cellules dont la matiere dit
                # EXACTEMENT un interstice, c'est-a-dire « la feuille voisine est bien la ».
                "part_un_interstice": round(float(np.mean(n == 1)), 3),
                "part_deux_ou_plus": round(float(np.mean(n >= 2)), 3),
                "interstices_median": int(np.median(n)),
                # ⭐⭐ ET UN SECOND VERDICT QUE LA MEME LECTURE DONNE GRATUITEMENT : la cellule
                # part-elle SUR une feuille ou dans un interstice ? C'est `95` mesure autrement,
                # et par la matiere seule.
                "part_partant_sur_la_feuille": round(float(np.mean(sur)), 3),
                "part_un_interstice_et_sur_la_feuille": round(
                    float(np.mean((n == 1) & sur)), 3),
                # ⚠⚠⚠ LA MARGE, SANS LAQUELLE LA POLARITE EST UN TIRAGE ET NON UNE MESURE.
                "marge_de_polarite_mediane": round(float(np.median(np.abs(marge[lu]))), 4),
                "part_polarite_tranchee": round(
                    float(np.mean(np.abs(marge[lu]) > barre / 2.0)), 3),
            })
        else:
            d["part_un_interstice"] = None
        # ⛔ Le refute, a cote.
        d["minima_proeminents_median"] = int(np.median(compte_minima))
        lignes.append(d)

    mesurees = [x for x in lignes if x["mesurable"] and x.get("part_un_interstice") is not None]
    if not mesurees:
        return {"message": "aucune bande lisible dans le volume fin"}

    ray = [x["rayon_mm"] for x in mesurees if x["rayon_mm"] is not None]
    un = [x["part_un_interstice"] for x in mesurees if x["rayon_mm"] is not None]
    rup = [x["continuite"] for x in mesurees if x["continuite"] is not None]
    unc = [x["part_un_interstice"] for x in mesurees if x["continuite"] is not None]

    tri = sorted([x for x in mesurees if x["rayon_mm"] is not None],
                 key=lambda z: z["rayon_mm"])
    t = max(1, len(tri) // 3)
    tiers = {"coeur": tri[:t], "milieu": tri[t:2 * t], "bord": tri[2 * t:]}
    med = lambda v, k: round(float(np.median([y[k] for y in v])), 3)  # noqa: E731
    return {
        "fragment": OBJET, "volume_fin": ZARR_FIN.rsplit("/", 1)[-1],
        "voxel_fin_um": VOXEL_FIN_UM, "pas_um": PAS_UM,
        "echelle_de_la_transformation": round(echelle(m), 3),
        "echantillons_par_segment": ECHANTILLONS,
        "bandes": len(lignes), "bandes_lisibles": len(mesurees),
        "cellules_par_bande": cellules,
        # ⭐⭐⭐ LE MODELE NUL EST PUBLIE AVEC LA BARRE QU'IL FIXE : sans lui, « accord > 0,31 »
        # serait un seuil choisi. Et son independance en sigma est le controle de l'invariance
        # d'echelle — si le nul dependait du bruit, le filtre aurait un parametre cache.
        "accord_du_bruit_pur": nul,
        "barre_du_nul": round(float(barre), 4),
        "lignes": lignes,
        "correlations": {
            "un_interstice_contre_rayon": correlation(un, ray),
            "un_interstice_contre_continuite": correlation(unc, rup),
        },
        "par_tiers": {k: {"bandes": len(v),
                          "part_lue": med(v, "part_lue"),
                          "accord_median": med(v, "accord_median"),
                          "part_un_interstice": med(v, "part_un_interstice"),
                          "part_partant_sur_la_feuille": med(
                              v, "part_partant_sur_la_feuille"),
                          "marge_de_polarite_mediane": med(v, "marge_de_polarite_mediane"),
                          "part_polarite_tranchee": med(v, "part_polarite_tranchee"),
                          "part_un_interstice_et_sur_la_feuille": med(
                              v, "part_un_interstice_et_sur_la_feuille"),
                          "part_deux_ou_plus": med(v, "part_deux_ou_plus"),
                          "continuite": med(v, "continuite")}
                      for k, v in tiers.items() if v},
    }


def afficher(r: dict) -> int:
    """L'affichage, séparé pour que la batterie puisse le lancer — la leçon de `93`."""
    if "message" in r:
        print(f"⚠ {r['message']}")
        return 0
    print(f"{r['fragment']} · volume à {r['voxel_fin_um']} µm · pas de feuille {r['pas_um']} µm "
          f"· {r['bandes_lisibles']}/{r['bandes']} bandes lisibles")
    print(f"  barre du modèle NUL (p99 du bruit pur) : {r['barre_du_nul']} — "
          f"un accord en dessous n'a rien dit\n")
    print(f"{'bande':>10} {'rayon':>6} {'lue':>6} {'accord':>7} {'1 inter.':>9} "
          f"{'2+':>6} {'sur feuille':>12} {'1 ET sur':>9} {'minima ⛔':>9}")
    for x in r["lignes"]:
        if not x["mesurable"] or x.get("part_un_interstice") is None:
            print(f"  w{x['de']:03d}-{x['a']:03d} "
                  f"{(x['rayon_mm'] or float('nan')):>6.1f} {'ILLISIBLE PAR LA MATIÈRE':>52}")
            continue
        print(f"  w{x['de']:03d}-{x['a']:03d} {(x['rayon_mm'] or float('nan')):>6.1f} "
              f"{x['part_lue']:>6.3f} {x['accord_median']:>7.3f} "
              f"{x['part_un_interstice']:>9.3f} {x['part_deux_ou_plus']:>6.3f} "
              f"{x['part_partant_sur_la_feuille']:>12.3f} "
              f"{x['part_un_interstice_et_sur_la_feuille']:>9.3f} "
              f"{x['minima_proeminents_median']:>9d}")
    p, c = r["par_tiers"], r["correlations"]
    print(f"\n{'':>16} {'lue':>7} {'accord':>8} {'1 inter.':>9} {'2+':>7} "
          f"{'sur feuille':>12} {'continuité':>11}")
    for k in ("coeur", "milieu", "bord"):
        if k in p:
            print(f"{k:>16} {p[k]['part_lue']:>7.3f} {p[k]['accord_median']:>8.3f} "
                  f"{p[k]['part_un_interstice']:>9.3f} {p[k]['part_deux_ou_plus']:>7.3f} "
                  f"{p[k]['part_partant_sur_la_feuille']:>12.3f} "
                  f"{p[k]['continuite']:>11.1f}")
    print(f"\n{'':>34} {'rayon':>8} {'continuité':>12}")
    print(f"{'part à UN interstice':>34} {c['un_interstice_contre_rayon']:>+8.3f} "
          f"{c['un_interstice_contre_continuite']:>+12.3f}")
    # ⭐⭐⭐ CE QUE LE MODELE NUL ACHETE, ET C'EST TOUT LE FICHIER.
    print(f"\n★★★ LE SEUIL NE VIENT NI D'UN MAILLAGE NI D'UN RÉGLAGE : il est le p99 de ce qu'un")
    print(f"   BRUIT PUR atteint ({r['barre_du_nul']}), donc il est calculable sans regarder le")
    print("   rouleau. `97` a montré qu'un maillage humain ne peut PAS le fixer, deux tracés")
    print("   indépendants de la même matière divergeant de plus d'une demi-feuille.")
    nul = r["accord_du_bruit_pur"]
    print(f"\n★★ ET LE NUL EST INDÉPENDANT DU BRUIT — médianes "
          + ", ".join(f"{v['median']}" for v in nul.values())
          + " pour σ = 2, 10, 40 :")
    print("   c'est le contrôle de l'invariance d'échelle. Si le nul dépendait de σ, le filtre")
    print("   aurait un paramètre caché, et il faudrait l'adapter au rouleau.")
    print("\n⚠⚠ UN SEUIL ABSOLU DE « SOMBRE » SERAIT DE TOUTE FAÇON SANS ESPOIR : l'étendue du")
    print("   profil varie d'un facteur 146 à l'intérieur d'UNE SEULE bande du bord, et de 2,4")
    print("   au milieu. Une constante par rouleau serait déjà un paramètre ajusté.")
    print("\n⛔⛔ ET LE COMPTEUR DE MINIMA EST RÉFUTÉ, gardé en dernière colonne : il n'a AUCUN")
    print("   point de fonctionnement — à la proéminence qui rejette le bruit pur un interstice")
    print("   réel n'est vu que 12,5 % du temps. Lisser fait monter la détection à 0,95 sans")
    print("   changer les faux positifs, parce qu'une proéminence en unités du bruit PROPRE au")
    print("   profil est invariante d'échelle : lisser abaisse le bruit ET le seuil ensemble.")
    return 0


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    t = np.linspace(0.0, 1.0, ECHANTILLONS)

    def fabrique(k, sur, sigma, graine, amp=40.0):
        base = 100.0 + amp * (1 if sur else -1) * np.cos(2 * np.pi * k * t)
        return base + np.random.default_rng(graine).normal(0.0, sigma, ECHANTILLONS)

    # --- les gabarits, et le sens de leur signe -------------------------------------------
    g1 = gabarit(1, sur_la_feuille=True)
    v("un gabarit part BRILLANT quand la cellule est sur la feuille", g1[0] > 0 and g1[-1] > 0,
      f"{g1[0]:.3f} et {g1[-1]:.3f}")
    v("... et SOMBRE quand elle est dans un interstice",
      gabarit(1, sur_la_feuille=False)[0] < 0)
    # ⚠⚠⚠ LE CONTROLE QUI ATTRAPE L'ERREUR DE SIGNE QUE J'AI FAITE : le creux d'un gabarit à un
    # interstice doit tomber au MILIEU du segment, pas a ses bouts.
    v("... et son creux tombe au MILIEU du segment, pas à ses bouts",
      int(np.argmin(g1)) == ECHANTILLONS // 2, str(int(np.argmin(g1))))
    v("un gabarit à deux interstices en a deux, à l'intérieur",
      int(np.sum((np.diff(np.sign(np.diff(gabarit(2)))) > 0))) == 2)
    v("les gabarits sont centrés et de norme un",
      all(abs(float(GABARITS[c].mean())) < 1e-12
          and abs(float(np.linalg.norm(GABARITS[c])) - 1.0) < 1e-12 for c in CLEFS))
    # ⚠⚠ ZERO N'EST PAS UN GABARIT, ET LE REFUS EST EXPLICITE : un segment qui reste sur la meme
    # feuille est plat, donc de norme nulle apres centrage. C'est le cas SANS ACCORD.
    leve = False
    try:
        gabarit(0)
    except ValueError:
        leve = True
    v("zéro interstice est REFUSÉ comme gabarit, pas fabriqué", leve)

    # --- le filtre, sur des profils dont on connait la reponse ----------------------------
    for k in INTERSTICES_TESTES:
        for sur in (True, False):
            y = np.stack([fabrique(k, sur, 10.0, 500 + j) for j in range(120)])
            n, su, sc, _ = accord(y)
            v(f"le filtre retrouve k={k} et le côté {'sur' if sur else 'dans'} "
              f"à un bruit du quart de l'amplitude",
              float(np.mean(n == k)) == 1.0 and float(np.mean(su == sur)) == 1.0,
              f"k {float(np.mean(n == k)):.3f}, côté {float(np.mean(su == sur)):.3f}")
    # ⭐⭐⭐ LE CONTROLE QUI PORTE LE FICHIER : il tient encore quand le bruit EGALE l'amplitude.
    y = np.stack([fabrique(1, True, 40.0, 800 + j) for j in range(200)])
    n, su, sc, _ = accord(y)
    v("... et il tient à un bruit ÉGAL à l'amplitude du signal",
      float(np.mean(n == 1)) == 1.0 and float(np.mean(su)) == 1.0,
      f"k {float(np.mean(n == 1)):.3f}, médiane d'accord {float(np.median(sc)):.3f}")
    # ⚠⚠ L'INVARIANCE D'ECHELLE EST ASSERTEE, pas supposee : c'est elle qui dispense d'adapter
    # le seuil au rouleau, et c'est la reponse a la question de l'auteur.
    # ⚠⚠⚠ ET LE CONTROLE A DU ETRE REFORMULE. J'affirmais d'abord que le score ne depend pas de
    # l'AMPLITUDE a bruit fixe — c'est faux, et le controle a eu raison de tomber : a amplitude 3
    # pour un bruit de 1, le rapport signal/bruit vaut 3, donc le score est legitimement plus bas
    # (0,908 contre 1,000). L'invariance porte sur l'ECHELLE : multiplier signal ET bruit par le
    # meme facteur ne doit rien changer, et c'est bien ca qui dispense d'un seuil par rouleau.
    for facteur in (0.05, 1.0, 50.0):
        y = np.stack([fabrique(1, True, 10.0 * facteur, 900 + j, amp=40.0 * facteur)
                      for j in range(80)])
        _, _, sc_f, _ = accord(y)
        if facteur == 1.0:
            reference = float(np.median(sc_f))
    for facteur in (0.05, 50.0):
        y = np.stack([fabrique(1, True, 10.0 * facteur, 900 + j, amp=40.0 * facteur)
                      for j in range(80)])
        _, _, sc_f, _ = accord(y)
        v(f"le score est inchangé quand tout est mis à l'échelle ×{facteur:g}",
          abs(float(np.median(sc_f)) - reference) < 1e-9,
          f"{float(np.median(sc_f)):.6f} contre {reference:.6f}")
    # ⚠ Et l'invariance au DECALAGE : ajouter une constante ne change rien.
    _, _, s0, _ = accord(np.stack([fabrique(1, True, 5.0, 950 + j) for j in range(60)]))
    _, _, s1, _ = accord(np.stack([fabrique(1, True, 5.0, 950 + j) + 500.0 for j in range(60)]))
    v("... ni du décalage", abs(float(np.median(s0)) - float(np.median(s1))) < 1e-9)
    # ⭐⭐⭐ LA MARGE DE POLARITE DOIT ETRE FRANCHE SUR FIXTURE, sinon son effondrement sur le
    # reel ne pourrait pas se lire : « le maillage est dans un interstice une fois sur deux » et
    # « l'instrument ne sait pas trancher » donnent le meme 0,49, et seule la marge les separe.
    _, _, _, mg3 = accord(np.stack([np.random.default_rng(1500 + j).normal(
        100.0, 5.0, ECHANTILLONS) for j in range(200)]))
    nul_marge = float(np.median(np.abs(mg3)))
    _, _, _, mg = accord(np.stack([fabrique(1, True, 10.0, 1400 + j) for j in range(120)]))
    _, _, _, mg2 = accord(np.stack([fabrique(1, False, 10.0, 1400 + j) for j in range(120)]))
    # ⚠⚠ LA BARRE EST CELLE DU NUL, PAS UN NOMBRE CHOISI. Ma premiere version exigeait une marge
    # supérieure à 1,0 — un seuil pris au hasard, et la fixture rendait 0,952, donc le controle
    # tombait pour une raison qui n'etait pas un defaut. Ce qui compte est le RAPPORT a ce qu'un
    # bruit pur atteint, exactement comme pour le score d'accord.
    v("la marge de polarité est FRANCHE sur une fixture au bon signe",
      float(np.median(mg)) > 5.0 * nul_marge,
      f"{float(np.median(mg)):.3f} contre {nul_marge:.3f} au nul")
    v("... et franchement NÉGATIVE quand la cellule est dans un interstice",
      float(np.median(mg2)) < -5.0 * nul_marge, f"{float(np.median(mg2)):.3f}")
    v("... donc la marge EST le juge de la polarité, et le nul la borne",
      nul_marge < 0.3, f"{nul_marge:.3f} au nul")

    # --- le modele nul, qui donne la barre ------------------------------------------------
    nul = accord_du_bruit_pur(tirages=300)
    v("le modèle nul est publié pour trois écarts-types", len(nul) == 3)
    medianes = [x["median"] for x in nul.values()]
    # ⭐⭐⭐ SI LE NUL DEPENDAIT DE SIGMA, LE FILTRE AURAIT UN PARAMETRE CACHE.
    v("... et il ne dépend PAS de l'écart-type, donc le filtre n'a aucun paramètre caché",
      max(medianes) - min(medianes) < 0.02, str(medianes))
    barre = max(x["p99"] for x in nul.values())
    v("la barre du nul laisse passer un vrai interstice bruité",
      float(np.median(sc)) > 1.5 * barre, f"{float(np.median(sc)):.3f} contre {barre:.3f}")
    v("... et rejette le bruit pur", barre < 0.4, f"{barre:.3f}")

    # --- le compteur de minima, refute et garde -------------------------------------------
    # ⛔⛔ SON ECHEC EST MESURE, PAS AFFIRME : a la proeminence qui rejette le bruit pur, il ne
    # voit presque plus l'interstice reel. Sans ce controle, le garder ressemblerait a un choix.
    bruit_pur = np.stack([np.random.default_rng(1100 + j).normal(100.0, 5.0, ECHANTILLONS)
                          for j in range(200)])
    br = bruit_du_profil(bruit_pur)
    faux = float(np.mean(interstices(bruit_pur, br, proeminence=3.0) > 0))
    v("le compteur de minima prend du BRUIT PUR pour des interstices", faux > 0.5,
      f"{faux:.3f} de faux positifs à proéminence 3")
    vrai = np.stack([fabrique(1, True, 5.0, 1200 + j) for j in range(200)])
    brv = bruit_du_profil(vrai)
    detecte = float(np.mean(interstices(vrai, brv, proeminence=6.0) == 1))
    v("... et à la proéminence qui rejette ce bruit, il ne voit plus l'interstice réel",
      detecte < 0.3, f"{detecte:.3f} de détection à proéminence 6")
    # ⚠ Le bruit est mesure par differences SECONDES, donc insensible a la pente du signal.
    v("le bruit est mesuré par différences secondes, donc le signal ne le contamine pas",
      abs(float(np.median(bruit_du_profil(
          np.stack([fabrique(1, True, 5.0, 1300 + j) for j in range(60)]))))
          - float(np.median(bruit_du_profil(
              np.stack([np.random.default_rng(1300 + j).normal(100.0, 5.0, ECHANTILLONS)
                        for j in range(60)]))))) < 0.5)
    # ⚠⚠⚠ ET LE CAS DEGENERE : un profil EXACTEMENT constant doit ressortir muet.
    plat = np.full((1, ECHANTILLONS), 90.0)
    v("un profil exactement constant ressort MUET, pas « zéro interstice »",
      bool(profil_muet(plat, bruit_du_profil(plat))[0]))

    # === LE PLANCHER DU COMPTEUR ENTIER, ET L'ESTIMATEUR CONTINU QUI LE LEVE ================
    # ⚠⚠⚠ LE PLANCHER EST MESURE, PAS LU. La famille est {1, 2, 3}, donc un segment qui ne
    # franchit qu'une FRACTION de feuille ne peut pas etre compte comme tel — et pire, il passe
    # la barre du bruit. Ce controle est ce qui a fait naitre `feuilles_franchies`.
    t = np.linspace(0.0, 1.0, ECHANTILLONS)
    partiel = (100.0 + 40.0 * np.cos(2 * np.pi * 0.82 * t)).reshape(1, -1)
    combien, _, score, _ = accord(partiel)
    barre = max(x["p99"] for x in accord_du_bruit_pur().values())
    v("le compteur entier ne sait pas dire « moins d'une feuille »",
      int(combien[0]) == 1, f"{int(combien[0])} pour 0,82 feuille franchie")
    v("... et ce segment PASSE quand même la barre du bruit pur",
      float(score[0]) > barre, f"score {float(score[0]):.3f} contre une barre de {barre:.3f}")
    # ⭐⭐⭐ L'ESTIMATEUR CONTINU, LUI, REND LA FRACTION — a trois decimales sur un profil propre.
    frac, _, _ = feuilles_franchies(partiel)
    v("l'estimateur continu rend la fraction au lieu de l'arrondir à un",
      abs(float(frac[0]) - 0.82) < 0.01, f"{float(frac[0]):.3f} pour 0,82")
    # ⭐⭐⭐ ET IL EST CALIBRE SUR UNE PREDICTION EXTERIEURE : avancer du pas nominal le long du
    # rayon sur une pile a theta franchit cos(theta) feuille. Quatre obliquites, pas une.
    ecarts = []
    for th in (0.0, 20.0, 35.0, 50.0):
        c = float(np.cos(np.deg2rad(th)))
        fr, _, _ = feuilles_franchies(
            (100.0 + 40.0 * np.cos(2 * np.pi * c * t)).reshape(1, -1))
        ecarts.append(abs(float(fr[0]) - c))
    v("... et il reproduit cos θ sur quatre obliquités fabriquées",
      max(ecarts) < 0.005, f"écart maximal {max(ecarts):.4f}")
    # ⚠⚠ IL REFUSE SOUS LA BORNE PLUTOT QUE D'ECRETER : un profil plat n'a pas de fraction.
    fr, sc, bu = feuilles_franchies(np.full((1, ECHANTILLONS), 90.0))
    v("un profil plat est déclaré injugeable, pas ramené à la borne",
      not np.isfinite(fr[0]) and not np.isfinite(sc[0]) and not bool(bu[0]), f"{fr[0]}")
    # ⚠⚠⚠ ET LA BUTEE EST RENDUE : une fraction posee sur le bord de la fenetre dit « au plus »,
    # jamais « exactement ». La lire comme une mesure serait la butee de `99`.
    fr, _, bu = feuilles_franchies(
        (100.0 + 40.0 * np.cos(2 * np.pi * 3.5 * t)).reshape(1, -1))
    v("une fraction au-delà de la fenêtre est signalée en butée",
      bool(bu[0]) and abs(float(fr[0]) - F_MAX) < 1e-9,
      f"{float(fr[0]):.3f} en butée {bool(bu[0])}")
    # ⭐⭐⭐ ET C'EST DU COTE BAS QUE LA BUTEE EST LA SEULE GARDE, ce qui est le controle qui
    # compte : un segment ne franchissant que 0,20 feuille ressort a 0,350 avec un score de
    # 0,996 — parfait. Le score ne l'attrape PAS ; seul le drapeau de butee le dit. Un appelant
    # qui ignorerait ce drapeau publierait un tiers de feuille pour un cinquieme, en confiance.
    fr, sc, bu = feuilles_franchies(
        (100.0 + 40.0 * np.cos(2 * np.pi * 0.20 * t)).reshape(1, -1))
    v("... et sous la fenêtre le SCORE ne garde rien : seule la butée le dit",
      bool(bu[0]) and float(sc[0]) > 0.9 and abs(float(fr[0]) - F_MIN) < 1e-9,
      f"{float(fr[0]):.3f} au score {float(sc[0]):.3f}, en butée {bool(bu[0])}")
    # ⚠⚠ LOIN AU-DELA, C'EST L'INVERSE : l'ajustement n'accroche plus rien, donc l'argmax est
    # arbitraire et n'est PAS en butee — c'est le SCORE qui doit l'ecarter. Deux pannes, deux
    # gardes, et aucune des deux ne couvre l'autre.
    fr, sc, bu = feuilles_franchies(
        (100.0 + 40.0 * np.cos(2 * np.pi * 6.0 * t)).reshape(1, -1))
    v("loin au-delà de la fenêtre, c'est le score qui écarte et non la butée",
      float(sc[0]) < 0.15 and not bool(bu[0]),
      f"score {float(sc[0]):.3f}, en butée {bool(bu[0])}")
    # ⚠⚠⚠ CHAQUE FAMILLE PORTE LA BARRE DE SA FORME, et c'est une CORRECTION de ce que j'avais
    # affirme : j'avais ecrit que le score continu ne pouvait pas garder, en comparant une
    # mediane a un p99. Compare p99 a p99, il garde — a 13 % pres.
    nc = nul_de_lestimateur_continu(tirages=300)
    v("la barre de la famille continue est PLUS HAUTE que celle à trois gabarits",
      nc["la_barre_a_trois_gabarits_serait_trop_permissive"] is True,
      f"{nc['barre_de_la_famille_continue']} contre {nc['barre_de_la_famille_a_trois']} "
      f"(+{nc['de_combien_en_pourcent']} %)")
    v("... mais du même ordre, donc son score reste utilisable comme garde",
      nc["de_combien_en_pourcent"] < 50.0, f"+{nc['de_combien_en_pourcent']} %")
    # ⚠ Et sa fraction sur du bruit ne doit PAS se concentrer sur un : un estimateur biaise vers
    # la reponse attendue serait le pire defaut possible ici.
    v("... et sa fraction sur du bruit n'est pas biaisée vers la réponse attendue",
      nc["sa_fraction_nest_pas_biaisee_vers_un"] is True,
      f"médiane {nc['sigma_10']['fraction_mediane']}")

    r = mesurer(cellules=40, bandes_max=2)
    if "message" in r:
        print(f"  ⚠ {r['message']} — contrôles sur données réelles sautés")
        print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, "
              f"{controles} checks)")
        return 1 if echecs else 0
    v("la mesure atteint le volume fin", r["bandes_lisibles"] >= 1,
      f"{r['bandes_lisibles']}/{r['bandes']}")
    v("la barre publiée est celle du nul", r["barre_du_nul"] > 0.2)
    v("chaque bande dit si la matière a répondu",
      all(("part_lue" in x) or not x["mesurable"] for x in r["lignes"]))
    v("l'estimateur réfuté est publié à côté",
      all("minima_proeminents_median" in x for x in r["lignes"] if x["mesurable"]))
    v("l'affichage tourne sur ce résultat", afficher(r) == 0)

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--cellules", type=int, default=CELLULES_PAR_BANDE)
    p.add_argument("--bandes", type=int, default=None)
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer(cellules=a.cellules, bandes_max=a.bandes)
    afficher(r)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False))
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
