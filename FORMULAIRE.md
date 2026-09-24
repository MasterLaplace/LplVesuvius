# Le formulaire

*Généré par `vesuve formules --markdown` depuis `vesuve/formulaire.py` : ne pas éditer à la main.*

Chaque équation que le logiciel applique, l'étage du pipeline où elle sert, le fait du registre de LplVesuvius qui la porte (`docs/rapports/REGISTRE_*.tsv`), et ce qui la calcule. Une équation marquée **noyau C** est une fonction de `noyau/include/vesuve.h`, vérifiée contre la fonction même du producteur de recherche ; les autres sont des règles de la procédure, en Python.

## E2 — l'échelle

### [E2] le demi-feuillet

$$
\delta = \mathrm{round}\!\left(\frac{s}{2\,v}\right)
$$

La moitié du pas inter-feuilles, en voxels : la plage de recalage du pas et le seuil du certificat.

*Fait* `R4-F14` · *source* `que_montrent_ces_deux_vues.py:60`, pas publié s = 173 µm à v = 2,4 µm · **noyau C**

## B — le budget de la nappe

### [N2] la dispersion de k rangées

$$
\sigma_k = \sqrt{\sigma_p^2 + \sigma_b^2 / k}
$$

Moyenner k rangées ne divise que leur bruit propre, jamais la part qu'elles partagent.

*Fait* `R4-F328` · *source* `213` [N2], `210` · **noyau C**

### [N5] la longueur tenable

$$
n_{\max} = \left(\frac{\delta}{\sigma}\right)^2
$$

Une nappe de pas de dispersion σ quitte son feuillet au bout de n_max coutures.

*Fait* `R4-F340` · *source* `213` [N5], `src/nappe/le_budget_de_la_nappe.py:120` · **noyau C**

### [N7] le triangle des bruits propres

$$
\sigma_{b,i}^2 = \frac{\sigma_\Delta^2(i,j) + \sigma_\Delta^2(i,k) - \sigma_\Delta^2(j,k)}{2}
$$

Trois désaccords donnent trois bruits propres ; une variance négative réfuterait le modèle.

*Fait* `R4-F343` · *source* `213` [N7], `212` · **noyau C**

### [D1] l'erreur d'une dispersion

$$
\mathrm{se}(\hat\sigma) = \frac{\hat\sigma}{\sqrt{2n}}
$$

Sans elle, une inégalité stricte contre une borne ne passe que par chance.

*Fait* `R5-L21` · *source* `213` [D1] · **noyau C**

### [D2] le compte décisif

$$
m = \left\lceil \frac{9\,(1-g)}{g} \right\rceil
$$

Le nombre de réplicats qui met trois erreurs d'échantillonnage dans la marge d'une garantie g.

*Fait* `R5-L21` · *source* `213` [D2] ; 171 à g = 0,05 · **noyau C**

## E4 — le treillis

### [F4] le pas d'une coupe

$$
s = -\left(\arg\max_{|k| \le \delta} \frac{\sum a_{t+k}\, b_t}{\sqrt{\sum a_{t+k}^2 \sum b_t^2}} - \delta\right)
$$

Le décalage en profondeur qui aligne le bord d'un chunk sur celui de son voisin, profils centrés, corrélation normalisée par l'énergie des deux fenêtres.

*Fait* `R4-F293` · *source* `src/nappe/la_derive_saccumule_t_elle.py:99` (`un_pas`) · **noyau C**

### [F4c] le pas d'une couture

$$
\hat s = \frac{1}{n}\sum_{i=1}^{n} s_i, \qquad d = \bar s_{\mathrm{pairs}} - \bar s_{\mathrm{impairs}}
$$

La moyenne des pas de seize coupes, et le désaccord de ses rangs pairs et impairs, qui mesure l'aléa.

*Fait* `R4-F293` · *source* `combien_de_rangees_faut_il_pour_lire_le_pas.py:120` · **noyau C**

## E5 — les trous

### [C2] le trou franchi

$$
c(s) = 0 \quad \text{pour chaque couture d'un trou de longueur} \le 17
$$

Un trou de majorité d'au plus dix-sept coutures se franchit à pas nul ; plus long, la boucle est ouverte.

*Fait* `R4-F389` · *source* `quest_ce_qui_franchit_le_trou_de_majorite.py:243`, règle « le maillage » · **règle de procédure**

## E6 — le certificat

### [C1] le consensus

$$
c(s) = \mathrm{m\acute ediane}\{\hat s_\ell(s)\} \ \text{si}\ \#\{\ell\} \ge \lfloor k/2 \rfloor + 1
$$

À chaque couture, la médiane des lignes présentes d'une bande, s'il y en a une majorité.

*Fait* `R4-F378` · *source* `le_consensus_traverse_t_il_la_rangee.py:94` · **règle de procédure**

### [L] la fermeture d'une boucle

$$
L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)
$$

L'écart entre les deux chemins d'un coin à l'autre ; une géométrie la ferme exactement.

*Fait* `R4-F393` · *source* `deux_chemins_arrivent_ils_sur_la_meme_spire.py:38` · **règle de procédure**

### [P] le profil d'une boucle

$$
P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j
$$

La fermeture cumulée coupe après coupe : une boucle tient si son profil reste sous le demi-feuillet partout.

*Fait* `R4-F403` · *source* `ou_laile_de_droite_se_separe.py:236` · **règle de procédure**

### [S] la portée qui voit

$$
p = \max_{\text{coupes hors traversée}} (y_{j+1} - y_j) - 1 = 29
$$

Deux coupes voisines à 29 rangées au plus voient toute traversée comme celles du segment.

*Fait* `R4-F409` · *source* `la_portee_voit_elle_sa_traversee.py:131` · **règle de procédure**

### [B0] le nul par blocs

$$
b = \max\!\left(1, \min\!\left(\lceil n^{1/3}\rceil, n\right)\right)
$$

La longueur des blocs qui tirent le nul d'une boucle, pour départager deux lignes.

*Fait* `R4-L22` · *source* `pourquoi_lerreur_declaree_est_trop_petite.py:375` · **noyau C**

### [M] la marge de départage

$$
\mu_n = |L_n| - \min_m |L_m| - \mathrm{m\acute ediane}\,|L_n^{\mathrm{nul}}|
$$

La ligne qui dérive est celle qu'évite la plus serrée des trois boucles, si chaque autre la dépasse de plus que son propre bruit.

*Fait* `R4-F401` · *source* `laquelle_des_deux_colonnes_derive.py:234` · **règle de procédure**

### [K] la couverture

$$
\kappa = \frac{|A \wedge \bigcup_b M_b|}{|A|}
$$

La part des chunks présents qu'entoure une boucle qui tient.

*Fait* `R4-F410` · *source* `une_aile_plus_etroite_tient_elle.py:163` · **règle de procédure**

## E7 — juger sans vérité terrain

### [F25] le test de convergence

$$
\alpha = \frac{\log(e_1/e_0)}{\log(n_1/n_0)}
$$

α ≈ 0 : la surface converge, une feuille est à portée ; α ≈ 1 : l'écart suit la fenêtre.

*Fait* `R3-F10` · *source* `src/commun/test_convergence.py:145` · **noyau C**

### [F17] la cohérence corrigée

$$
c' = \max\!\left(0, \frac{c - 1/\sqrt n}{1 - 1/\sqrt n}\right)
$$

Zéro sur du bruit pur, un sur une rotation parfaite.

*Fait* `R4-F100` · *source* `151` [F17] · **noyau C**

## E8 — l'encre, la règle graduée

### [F31] le nombre de Fresnel

$$
F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}
$$

La largeur de la première frange en pixels : 0,39 pour les rouleaux du prix, 0,74 en production.

*Fait* `R6-F08` · *source* `src/encre/nombre_de_fresnel.py:142` · **noyau C**

### [F29] l'aire sous la courbe

$$
\mathrm{AUC} = \frac{R_+ - n_+(n_+ + 1)/2}{n_+\, n_-}
$$

Mann-Whitney aux rangs moyens ; le contrôle par mélange doit rendre 0,500.

*Fait* `R1-F01` · *source* `src/volume/evaluate_segment.py:72` · **noyau C**
