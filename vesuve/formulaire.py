"""Le formulaire : chaque équation que le logiciel applique, avec le fait qui la porte et ce qui la calcule.

Une équation est une ENTRÉE de ce module, jamais une phrase dans un document : `vesuve formules` la rend,
le rapport d'un pipeline cite son identifiant avec ses entrées et sa valeur, et un test exige que chaque
équation qui porte un calcul le fasse. Les identifiants sont ceux de `docs/archive/151` §5 et `213` §4
quand ils existent ([F…], [N…], [D…]) ; les autres sont nommés ici.

⚠ Correction d'un document archivé, dite et non faite en silence : `151` [F31] écrit le nombre de Fresnel
a²/(λD). Le producteur (`src/encre/nombre_de_fresnel.py:142`) calcule √(λD)/p, l'inverse de la racine de
la forme classique, et c'est cette forme-ci qui rend F = 0,39 pour les treize rouleaux du prix. Le
formulaire suit le producteur.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from vesuve import noyau


@dataclass(frozen=True)
class Equation:
    id: str
    etage: str      # l'étage du pipeline où elle sert : E2, B, E4, E5, E6, E7, E8
    nom: str
    latex: str
    enonce: str     # ce qu'elle dit, en une phrase
    fait: str       # l'identifiant du registre qui la porte
    source: str     # où elle a été établie, et son producteur
    calcul: Callable | None = None  # la fonction qui la calcule ; None quand elle est une règle de procédure


_E = Equation
LE_FORMULAIRE: dict[str, Equation] = {e.id: e for e in [
    _E("E2", "E2", "le demi-feuillet", r"\delta = \mathrm{round}\!\left(\frac{s}{2\,v}\right)",
       "La moitié du pas inter-feuilles, en voxels : la plage de recalage du pas et le seuil du certificat.",
       "R4-F14", "`que_montrent_ces_deux_vues.py:60`, pas publié s = 173 µm à v = 2,4 µm",
       noyau.demi_feuillet_voxels),
    _E("N2", "B", "la dispersion de k rangées", r"\sigma_k = \sqrt{\sigma_p^2 + \sigma_b^2 / k}",
       "Moyenner k rangées ne divise que leur bruit propre, jamais la part qu'elles partagent.",
       "R4-F328", "`213` [N2], `210`", noyau.dispersion_de_k_rangees),
    _E("N5", "B", "la longueur tenable", r"n_{\max} = \left(\frac{\delta}{\sigma}\right)^2",
       "Une nappe de pas de dispersion σ quitte son feuillet au bout de n_max coutures.",
       "R4-F340", "`213` [N5], `src/nappe/le_budget_de_la_nappe.py:120`", noyau.longueur_tenable),
    _E("N7", "B", "le triangle des bruits propres",
       r"\sigma_{b,i}^2 = \frac{\sigma_\Delta^2(i,j) + \sigma_\Delta^2(i,k) - \sigma_\Delta^2(j,k)}{2}",
       "Trois désaccords donnent trois bruits propres ; une variance négative réfuterait le modèle.",
       "R4-F343", "`213` [N7], `212`", noyau.bruit_propre_du_triangle),
    _E("D1", "B", "l'erreur d'une dispersion", r"\mathrm{se}(\hat\sigma) = \frac{\hat\sigma}{\sqrt{2n}}",
       "Sans elle, une inégalité stricte contre une borne ne passe que par chance.",
       "R5-L21", "`213` [D1]", noyau.erreur_dune_dispersion),
    _E("D2", "B", "le compte décisif", r"m = \left\lceil \frac{9\,(1-g)}{g} \right\rceil",
       "Le nombre de réplicats qui met trois erreurs d'échantillonnage dans la marge d'une garantie g.",
       "R5-L21", "`213` [D2] ; 171 à g = 0,05", noyau.compte_decisif),
    _E("F4", "E4", "le pas d'une coupe",
       r"s = -\left(\arg\max_{|k| \le \delta} \frac{\sum a_{t+k}\, b_t}{\sqrt{\sum a_{t+k}^2 \sum b_t^2}} - \delta\right)",
       "Le décalage en profondeur qui aligne le bord d'un chunk sur celui de son voisin, profils centrés, "
       "corrélation normalisée par l'énergie des deux fenêtres.",
       "R4-F293", "`src/nappe/la_derive_saccumule_t_elle.py:99` (`un_pas`)", noyau.pas_dune_coupe),
    _E("F4c", "E4", "le pas d'une couture",
       r"\hat s = \frac{1}{n}\sum_{i=1}^{n} s_i, \qquad d = \bar s_{\mathrm{pairs}} - \bar s_{\mathrm{impairs}}",
       "La moyenne des pas de seize coupes, et le désaccord de ses rangs pairs et impairs, qui mesure l'aléa.",
       "R4-F293", "`combien_de_rangees_faut_il_pour_lire_le_pas.py:120`", noyau.pas_dune_couture),
    _E("C1", "E6", "le consensus", r"c(s) = \mathrm{m\acute ediane}\{\hat s_\ell(s)\} \ \text{si}\ \#\{\ell\} \ge \lfloor k/2 \rfloor + 1",
       "À chaque couture, la médiane des lignes présentes d'une bande, s'il y en a une majorité.",
       "R4-F378", "`le_consensus_traverse_t_il_la_rangee.py:94`"),
    _E("C2", "E5", "le trou franchi", r"c(s) = 0 \quad \text{pour chaque couture d'un trou de longueur} \le 17",
       "Un trou de majorité d'au plus dix-sept coutures se franchit à pas nul ; plus long, la boucle est ouverte.",
       "R4-F389", "`quest_ce_qui_franchit_le_trou_de_majorite.py:243`, règle « le maillage »"),
    _E("L", "E6", "la fermeture d'une boucle",
       r"L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)",
       "L'écart entre les deux chemins d'un coin à l'autre ; une géométrie la ferme exactement.",
       "R4-F393", "`deux_chemins_arrivent_ils_sur_la_meme_spire.py:38`"),
    _E("P", "E6", "le profil d'une boucle", r"P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j",
       "La fermeture cumulée coupe après coupe : une boucle tient si son profil reste sous le demi-feuillet partout.",
       "R4-F403", "`ou_laile_de_droite_se_separe.py:236`"),
    _E("S", "E6", "la portée qui voit", r"p = \max_{\text{coupes hors traversée}} (y_{j+1} - y_j) - 1 = 29",
       "Deux coupes voisines à 29 rangées au plus voient toute traversée comme celles du segment.",
       "R4-F409", "`la_portee_voit_elle_sa_traversee.py:131`"),
    _E("B0", "E6", "le nul par blocs", r"b = \max\!\left(1, \min\!\left(\lceil n^{1/3}\rceil, n\right)\right)",
       "La longueur des blocs qui tirent le nul d'une boucle, pour départager deux lignes.",
       "R4-L22", "`pourquoi_lerreur_declaree_est_trop_petite.py:375`", noyau.longueur_de_bloc),
    _E("M", "E6", "la marge de départage",
       r"\mu_n = |L_n| - \min_m |L_m| - \mathrm{m\acute ediane}\,|L_n^{\mathrm{nul}}|",
       "La ligne qui dérive est celle qu'évite la plus serrée des trois boucles, si chaque autre la dépasse "
       "de plus que son propre bruit.", "R4-F401", "`laquelle_des_deux_colonnes_derive.py:234`"),
    _E("K", "E6", "la couverture", r"\kappa = \frac{|A \wedge \bigcup_b M_b|}{|A|}",
       "La part des chunks présents qu'entoure une boucle qui tient.", "R4-F410",
       "`une_aile_plus_etroite_tient_elle.py:163`"),
    _E("F25", "E7", "le test de convergence",
       r"\alpha = \frac{\log(e_1/e_0)}{\log(n_1/n_0)}",
       "α ≈ 0 : la surface converge, une feuille est à portée ; α ≈ 1 : l'écart suit la fenêtre.",
       "R3-F10", "`src/commun/test_convergence.py:145`", noyau.alpha_de_convergence),
    _E("F17", "E7", "la cohérence corrigée",
       r"c' = \max\!\left(0, \frac{c - 1/\sqrt n}{1 - 1/\sqrt n}\right)",
       "Zéro sur du bruit pur, un sur une rotation parfaite.", "R4-F100", "`151` [F17]",
       noyau.coherence_corrigee),
    _E("F31", "E8", "le nombre de Fresnel", r"F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}",
       "La largeur de la première frange en pixels : 0,39 pour les rouleaux du prix, 0,74 en production.",
       "R6-F08", "`src/encre/nombre_de_fresnel.py:142`", noyau.nombre_de_fresnel),
    _E("F29", "E8", "l'aire sous la courbe", r"\mathrm{AUC} = \frac{R_+ - n_+(n_+ + 1)/2}{n_+\, n_-}",
       "Mann-Whitney aux rangs moyens ; le contrôle par mélange doit rendre 0,500.", "R1-F01",
       "`src/volume/evaluate_segment.py:72`", noyau.aire_sous_la_courbe),
]}


def equation(ident: str) -> Equation:
    try:
        return LE_FORMULAIRE[ident]
    except KeyError:
        raise KeyError(f"équation inconnue {ident!r} ; le formulaire porte : {sorted(LE_FORMULAIRE)}") from None
