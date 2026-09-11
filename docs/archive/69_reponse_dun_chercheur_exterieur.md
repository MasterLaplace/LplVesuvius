# 69 — Réponse d'un chercheur extérieur : où est le goulot, et ce qui le débloque

> Rédigé le 2026-09-03 en réponse au prompt `docs/prompts/` (« chercheur senior »). Ce document
> ne contient ni code ni plan de projet : des hypothèses falsifiables, des formulations, des
> algorithmes décrits pour être implémentés, des mesures avec ce qu'elles discriminent, et des
> emprunts hors domaine avec leurs références réelles.
>
> **Convention de marquage**, parce que le prompt l'exige et que le dépôt l'a payée :
> **[établi]** = lu dans une source locale citée (page du papier, fichier du dépôt, JSON de
> mesure) ; **[calculé]** = arithmétique refaite dans un script jetable
> (`docs/mesures/69_arithmetique.py`, formule reproduite en clair ici) ; **[conjecture]** = ce que je crois
> sans l'avoir mesuré ; **[je ne sais pas]** = ce qu'il faudrait aller chercher.

---

## 0. Ce que j'ai vérifié moi-même avant d'écrire

Tout ce qui suit s'appuie sur des lectures faites dans l'arbre, pas sur le résumé du prompt :

| fait | où je l'ai lu |
|---|---|
| les volumes du prix sont **Paganin δ/β = 1000 + masque flou inverse c = 4, σ = 1,2 px** — le même réglage que la production, « *the production setting used for the unwrapping and ink-detection pipelines throughout the manuscript* » | `pdf/main.pdf` (texte extrait), Methods « Phase retrieval and contrast restoration », et Ext. Data Fig. 2d |
| **9,362 µm est un pas « effectif » : `binmean2` d'une acquisition à 4,681 µm** (PHerc. 139, PHerc. 500P2 « HA ») ; « *binning versions by factor 2 and 4 were calculated* » pour tous les volumes | même fichier, Ext. Data Fig. 2d–e, Supplementary Table, et le paragraphe « Reconstruction » |
| la **décohérence** telle que le papier l'entend est **induite par l'échantillon** (diffusion par le graphite et les lumens des fibres qui agissent comme des lentilles), pas par la source | Methods « Tomographic scanning » |
| les dépôts d'encre apparaissent, à 2,4 µm, comme des dépôts clairs **de 10–20 µm d'épaisseur apparente** sur la surface | section « Volumetric validation of ink recovery: PHerc. Paris 4 » |
| le pas d'enroulement est **invariant sur la collection** : médiane **187 µm**, IQR 181–193, 35/36 rouleaux entre 160 et 210 µm, indépendant de la taille et de la campagne | `data/repos/winding-ruler/docs/SUBMISSION_winding_evidence.md` (errata v2) |
| les 13 rouleaux du prix ont **60 à 129 spires** (médiane par rouleau) — PHerc0826 60, PHerc0125 82, PHerc0800 103, PHerc0268 129 — contre **31** pour PHerc. 1667 | `data/repos/winding-ruler/results/atlas_collection_v2.csv` |
| pour chacun des 13, le dépôt public porte déjà **une prédiction de surface recto** (`surface-m7-L0`), les **`normal-grids`** et un champ **`lasagna`** de niveau 0 | `data/metadata.min.json` (gzippé ; entrée `PHerc0826`, `volumes[...].data[]`) |
| le recto est **toujours enroulé vers l'intérieur** (face vers l'axe), fibres horizontales ; le verso vers l'extérieur, fibres verticales | `data/site/scrollprize.org/2026_open_problems.html`, § « Surface prediction » |
| le spiral fitting de Henderson est un **difféomorphisme** appliqué à une spirale canonique, qui « ne peut ni déchirer, ni recoller, ni replier », et « erre entre deux vraies spires » là où les prédictions se contredisent (WJF 3,20 %) | `docs/27` §2 |
| `villa/lasagna/approval_inpaint.py` existe : un masque d'approbation peut être **inpainté** autour d'une graine, pas seulement peint | `data/repos/villa/lasagna/approval_inpaint.py` |

⚠ Deux de ces faits **corrigent le cadrage du prompt** (§2 bis A) et j'y reviens au §1.1 : les
franges de Fresnel ne sont **pas** ce qu'on regarde dans les volumes publiés (Paganin les
supprime, le papier le dit sous sa Fig. 2d), et le pas de 9,362 µm est un **choix d'export**,
pas une limite du détecteur.

---

## 1. Diagnostic

### 1.1 Ce que $F$ mesure vraiment dans les volumes publiés — et ce qu'il ne mesure pas

Le prompt écrit que le contraste vient des franges de Fresnel et que $F = \sqrt{\lambda D}/p$
décide de leur visibilité. C'est vrai **des projections brutes**, et faux **des volumes
publiés** : tous sont reconstruits après récupération de phase de Paganin à δ/β = 1000, et la
Fig. 2d du papier montre, sur PHerc. 139 à 9,362 µm, que δ/β ≈ 0 laisse voir les franges tandis
que δ/β = 1000 « *suppresses the fringes and obtains higher SNR and contrast at the cost of
reduced apparent sharpness* » **[établi]**.

Pourquoi $F$ ordonne quand même les verdicts ? Parce qu'à δ/β **fixé**, la longueur du noyau de
Paganin est

$$ L_P = \sqrt{\frac{\lambda D}{4\pi}\,\frac{\delta}{\beta}} \qquad\Rightarrow\qquad \frac{L_P}{p} = F\cdot\sqrt{\frac{\delta/\beta}{4\pi}} \approx 8{,}92\,F . $$

**[calculé]** $L_P$ = 32,4 µm au régime du prix (113 keV, 1,2 m) contre 16,7 µm en production
(78 keV, 0,22 m) ; en pixels, **3,5 px contre 7,0 px**. Le rang est le même que celui de $F$ —
c'est le même nombre à une constante près — mais le **sens** change : $F$ n'est pas « la frange
est-elle résolue », c'est « **combien de pixels fait le noyau de récupération de phase** »,
autrement dit le facteur de sur-échantillonnage de la carte de δ restituée. Un volume à
$L_P/p = 3{,}5$ est limité par sa grille (« *pixel-limited* ») ; un volume à 7 est limité par
la récupération de phase (sur-échantillonné). Les deux verdicts du papier sont ceux-là.

⚠⚠ **Conséquence qui change la stratégie** : « 53 % du régime de production » se lit comme une
dégradation uniforme. Ce n'est pas ce que dit la physique. Dans le régime de champ proche,
le gain de contraste de phase à la fréquence spatiale $f$ vaut $2\pi\lambda D f^2$ (§3.1) ;
il est donc **3,8 fois plus élevé** au régime du prix qu'en production **à toute fréquence
que la grille de 9,362 µm résout** ($\lambda D$ : 1,32·10⁻¹¹ contre 3,50·10⁻¹² m²
**[calculé]**). Ce que le régime du prix perd, c'est **une bande** — les périodes de 4,8 à
19 µm, entre la coupure de Nyquist à 9,362 µm et celle à 2,4 µm — et ce que la décohérence
brouille, qui croît avec $D$. Un **filtre passe-bas**, pas une atténuation.

La différence n'est pas académique : si l'évidence d'encre vit surtout dans les dépôts de
10–20 µm et dans la « craquelure » fine, la bande perdue est le signal ; si elle vit dans un
dépôt lisse de quelques dizaines de µm sur des traits de 300 µm, le régime du prix la porte
**mieux** que la production. **C'est mesurable sur les cases vides (H1).**

### 1.2 Le pas de 9,362 µm est un export, et la décohérence est déjà payée à 1,2 m

**[établi]** PHerc. 139 et le fragment 500P2 « HA » à 9,362 µm sont des `binmean2`
d'acquisitions à 4,681 µm. Le papier dit que **toutes** les reconstructions ont des versions
binées ×2 et ×4. Et sur le même fragment 500P2 il rend deux verdicts pour le même bras de
1,2 m : à 4,317 µm « *haze-limited* », à 9,362 µm « *pixel-limited* ».

Ces deux verdicts décrivent **la même acquisition à deux échantillonnages** : à 1,2 m la
résolution physique est bornée par la décohérence quelque part entre 4,3 et 9,4 µm, donc le
binning ×2 a coûté peu, et c'est très probablement pourquoi il a été fait (le papier ne le dit
pas ainsi ; **[conjecture]**). Prédiction chiffrée : le débinage rendrait **au plus 1,3–1,5×**
de résolution effective, et l'AUC d'encre à 4,317 µm / 1,2 m sur 500P2 ne dépassera l'AUC à
9,362 µm que marginalement. **Cette prédiction est testable sur des données publiques (H2)**,
et si elle est fausse, la donnée manquante la plus précieuse du prix est une **demande à
l'ESRF** : les reconstructions non binées à 4,3–4,7 µm des treize rouleaux, qui existent.

### 1.3 Le goulot est géométrique, et il est dix fois plus large que dans le papier

Le papier compte 25 h d'annotation manuelle par spire sur 31 spires (775 h) pour un *midollo*
de **8 cm** de haut sur 2 cm de diamètre. Les treize rouleaux du prix ont **60 à 129 spires**
et un rouleau entier fait 19 à 24 cm de haut **[établi]**. À la cadence du papier, en
supposant le coût proportionnel à l'aire **[conjecture, l'hypothèse la plus favorable]** :

| rouleau | spires (médiane) | h à 8 cm de hauteur | h à 20 cm |
|---|---:|---:|---:|
| PHerc0826 | 60 | 1 500 | 3 750 |
| PHerc0125 | 82 | 2 050 | 5 125 |
| PHerc0800 | 103 | 2 575 | 6 440 |
| PHerc0268 | 129 | 3 225 | 8 060 |

**[calculé]** Deux à quatre années-personne **par rouleau** pour le seul pinceau d'approbation.
Le prix n'est donc pas gagné en améliorant la détection d'encre : il est gagné ou perdu sur
**ce qui remplace le pinceau**. Et les pièces amont sont déjà sur le dépôt public pour les
treize (prédiction de surface, normales, lasagna) : la chaîne est bloquée aux étapes 9–11 du
tableau du `68` §2 — traçage, approbation, aplatissement — pas à l'étape 8.

### 1.4 Ce que je déduis et ce que je conjecture

| énoncé | statut |
|---|---|
| les volumes du prix sont limités par leur grille, et le débinage existe à l'ESRF | **[établi]** |
| la perte au régime du prix est une bande 5–19 µm plus un flou ∝ D, pas une atténuation uniforme | **[calculé]** sous les hypothèses du §3.1 (objet de phase faible, TIE, pixel carré) |
| l'encre survit au régime du prix parce que son dépôt est plus épais que la bande perdue | **[conjecture]** — c'est H1 |
| le coût humain est proportionnel à l'aire | **[conjecture]** — il pourrait être proportionnel au nombre de régions ambiguës (H4), ce qui serait bien meilleur |
| la cohérence de spire est un problème de dépliage de phase avec résidus, et les résidus sont là où le pinceau travaille | **[conjecture]** — c'est H5 |
| le prior d'enroulement est universel | **[établi]** pour le pas (winding-ruler) ; **[conjecture]** pour le reste (H6) |

---

## 2. Hypothèses

Chacune : énoncé falsifiable, mesure, prédiction si vraie / si fausse, coût. Toutes se mesurent
avec des données publiques sauf mention.

### H1 — L'évidence d'encre survit à la bande perdue (spectre d'AUC)

**Énoncé.** Sur un fragment à vérité terrain IR, l'AUC d'un détecteur entraîné sur les couches à
2,215 µm ne dépend pas des périodes spatiales inférieures à ~20 µm : un passe-bas à 20 µm
appliqué **avant** inférence conserve ≥ 90 % de l'excès d'AUC sur le hasard.

**Mesure.** `PHerc0500P2`, segment `20250628074500-500P2_front`, couches à 2,215 µm, `inklabels`.
Balayer un passe-bas gaussien de coupure 5, 10, 15, 20, 30, 50 µm sur les couches (en plan
**et** en profondeur, séparément), inférer, mesurer l'AUC avec l'instrument existant
(`src/volume/evaluate_segment.py`), avec le contrôle par mélange à 0,500. Puis mesurer l'AUC
**sur les couches natives à 9,362 µm** du même segment (la case vide du `68` §4), avec un
détecteur ré-entraîné ou adapté à ce pas (tuile ~66 px).

**Si vraie.** La courbe AUC(coupure) est plate jusqu'à ~20 µm et l'AUC native à 9,362 µm est
du même ordre que celle du passe-bas équivalent (à la différence de bruit près). Le régime du
prix est alors un problème de **géométrie et de bruit**, pas de physique du contraste.
**Si fausse.** L'AUC s'effondre dès 10 µm de coupure : l'encre est une texture fine, la bande
perdue est le signal, et seule la demande de débinage (H2) ou un rescan peut la rendre.
**Coût.** Quelques heures de calcul, zéro annotation — les couches sont rendues.

⭐ **Le second volet, qui répond directement au critère des 70 %.** PHerc. 1667 a 22 colonnes
transcrites à 2,4 µm. Une fois l'opérateur de dégradation ajusté sur les paires recalées (A6),
appliquer cet opérateur aux couches de 1667, rendre, et faire lire **en aveugle, avec la
condition vierge** (le protocole de `juge par API` du dépôt, qui a le contrôle que le domaine
n'a pas) la fraction de lettres lisibles **par colonne**. C'est une **courbe dose-réponse de la
lisibilité** en fonction du niveau de dégradation, sur un texte connu. Elle dit si 70 % est
atteignable au régime du prix **avant** de dérouler quoi que ce soit.

### H2 — Le débinage ne rend presque rien, parce que la décohérence à 1,2 m a déjà pris la résolution

**Énoncé.** Sur 500P2, l'AUC d'encre sur les couches à 4,317 µm / 1,2 m dépasse celle des couches
à 9,362 µm / 1,2 m de moins de 0,03, tandis que celle à 2,215 µm / 0,4 m la dépasse de plus
de 0,05.

**Mesure.** Les trois piles sont rendues et recalées (`volume_transforms`, `68` §4). Trois AUC,
même segment, même vérité terrain, bootstrap par tuiles pour l'intervalle. En parallèle, la
**fonction d'étalement de bord** (ESF) d'une frontière de feuille sur les mêmes voxels recalés,
en µm, dans les trois piles — c'est la mesure directe du flou de décohérence.
**Si vraie.** Ne pas demander le débinage ; le régime du prix est ce qu'il est.
**Si fausse** (AUC 4,317 ≫ AUC 9,362). Écrire à l'ESRF : les volumes non binés des treize
existent (« *binning versions by factor 2 and 4 were calculated* ») et c'est la donnée manquante
la plus rentable du prix, sans faisceau.
**Coût.** Heures. ⚠ Donnée manquante pour aller plus loin : la paire 0,6 m / 1,2 m de PHerc. 268
(Ext. Data Fig. 2c) n'est pas publiée — `metadata` ne porte qu'un volume pour 268 et aucun
`volume_transforms`.

### H3 — La décohérence est un flou mesurable, local, et il suit une loi en D/E^α

**Énoncé.** Le flou de décohérence en pixels vaut $\kappa\, D / (E^{\alpha} p)$ avec un seuil
opérationnel unique qui reproduit les verdicts du papier, et $\kappa$ varie **localement** avec
la compression (le papier : « *the denser and larger it is, the higher the decoherence* »).

**[calculé]** Avec $\alpha = 2$ (la réfraction par des lentilles de δ ∝ λ² ∝ 1/E²), la grandeur
$D/(E^2 p)$ classe correctement les six verdicts que j'ai pu confronter : 0,78·10⁻⁵ (268 à
0,6 m, net), 1,00·10⁻⁵ (les 13 du prix, « pixel-limited »), 1,47–1,51·10⁻⁵ (500P2 à 0,4 m et la
production, nets), 1,57·10⁻⁵ (268 à 1,2 m, « starts to affect the resolution »), 2,01·10⁻⁵
(l'acquisition 4,681 µm / 1,2 m, binée), 2,26·10⁻⁵ (500P2 à 4,317 µm / 1,2 m, « haze-limited »).
⚠ **Mais $\alpha = 1$ les classe aussi.** Six points ne fixent pas un exposant ; ils fixent
seulement que le flou croît avec $D$ et décroît avec $E$. **[je ne sais pas]** quelle est la
loi ; c'est pourquoi la mesure ci-dessous est celle du flou lui-même, pas de la loi.

**Mesure.** ESF en µm sur les paires recalées (H2) et sur les 13 rouleaux **par région** : la
largeur de transition d'une frontière de feuille, estimée par la dérivée du profil le long de
la normale locale (le dépôt a le profil de profondeur et le champ de correction). Carte de
$\sigma_{dec}(x)$ par rouleau.
**Si vraie.** $\sigma_{dec}$ en µm est ~2,6 fois plus large au régime du prix qu'en production
($D/E^2$ : 9,4·10⁻⁵ contre 3,6·10⁻⁵ **[calculé]**) et **sous le pixel** de 9,362 µm hors des
régions comprimées ; sa carte co-localise avec les régions où le traçage échoue. Elle devient
la « scan-quality metric » que le tableau des goulots du site demande.
**Si fausse.** Le flou ne dépend pas de la région : la décohérence est un effet global, et la
difficulté des régions comprimées vient d'ailleurs (superposition des feuilles, pas du flou).
**Coût.** Jours ; instruments existants.

### H4 — Le coût humain n'est pas proportionnel à l'aire mais au nombre de régions ambiguës

**Énoncé.** Sur PHerc. 1667 (maillage publié, humainement approuvé), la fraction de la surface
où le test de convergence est ambigu ($\alpha$ ni ≈ 0 ni ≈ 1) et où la densité de résidus (H5)
est non nulle est **inférieure à 10 %** ; les 90 % restants sont « approuvables » par un
critère automatique sans désaccord avec le maillage publié.

**Mesure.** Calculer $\alpha$ et la carte de résidus sur tout 1667 ; produire `approval.tif`
automatiquement (A5) ; relancer la ré-optimisation (`GrowPatch`) sur une spire ; mesurer
l'écart de maillage (`nappe/`) contre la spire publiée ; recommencer avec le masque vide
(témoin bas) et le masque plein (témoin haut).
**Si vraie.** Le budget humain d'un rouleau du prix tombe de milliers d'heures à
**quelques centaines**, concentrées sur des régions nommées à l'avance. **Si fausse.** Les
régions ambiguës sont partout (≥ 30 %) : le pinceau ne se remplace pas, il s'accélère au mieux,
et il faut choisir le rouleau du prix par sa fraction ambiguë (H6 le permet).
**Coût.** Jours de calcul + le pipeline `villa` au commit épinglé. ⚠ Donnée manquante : les
masques d'approbation humains de 1667 ne semblent pas publiés (`68` §1). L'écart de maillage
est le substitut.

### H5 — Le rouleau est un champ de phase ; ses défauts sont des résidus ; les résidus sont là où le traçage saute

**Énoncé.** Le champ d'orientation publié (`lasagna` / `normal-grids`), intégré comme un
gradient de phase (§3.2), a des résidus (charges topologiques ±1) dont la densité prédit les
sauts de spire du spiral fitting (WJF 3,20 %) et les sauts mesurés par `nappe/` avec une AUC
> 0,8, et **sans vérité terrain**.

**Mesure.** Sur Scroll 1 (où `evaluate_wrt_gp` de `spiral-fitting` localise les traversées) :
carte de résidus au niveau 1 ; AUC de la densité de résidus comme prédicteur de « ce segment
traverse deux spires ». Sur 1667 : idem contre le maillage publié.
**Si vraie.** La carte de résidus est un masque d'approbation automatique **avec une raison
écrite pour chaque refus** (un résidu est un endroit précis, pas un score). **Si fausse.** Les
sauts se produisent à résidu nul : ils viennent d'une ambiguïté d'amplitude (deux feuilles
également probables) et non de topologie, et c'est la coupe à surfaces couplées (§3.3) qui
tranche, pas le dépliage.
**Coût.** Jours ; entrées publiques.

### H6 — Le prior d'enroulement est universel, donc un seul réglage sert les treize

**Énoncé.** Le pas est déjà universel **[établi]**. Je pose que le **spectre polaire local**
(le pic de Bragg du réseau 1D de feuilles, §3.5) a une distribution de finesse
$Q = f_0/\Delta f$ dont les quantiles sont les mêmes sur les 13 rouleaux à 10 % près, et que la
fraction de volume à $Q$ effondré (< 2) est le prédicteur de la fraction ambiguë de H4.

**Mesure.** Sur les 13 prédictions de surface publiées, au niveau 1 : dépliage polaire par
tranche autour de l'ombilic (le dépôt n'en a pas ; c'est l'étage que l'audit `67` dit absent
des 35 dépôts), spectre local par fenêtres, histogramme de $Q$ par rouleau.
**Si vraie.** On choisit le rouleau du prix par sa fraction à $Q$ effondré, et on n'ajuste les
hyperparamètres qu'une fois. **Si fausse.** Chaque rouleau est un cas ; le coût de réglage se
multiplie par treize.
**Coût.** Jours.

### H7 — Le verso est le témoin nul du recto, et il rend la détection testable

**Énoncé.** Sur la même colonne de voxels, la réponse du détecteur d'encre échantillonnée sur la
face **verso** (extérieure) de la feuille suit la distribution de sa réponse sur du recto
**sans encre** ; l'AUC verso-contre-IR est ≈ 0,5.

**Mesure.** Fragments 9B / 343P / 500P2 : rendre la pile centrée sur la face verso (l'offset est
connu, le dépôt a le profil de profondeur), inférer, AUC contre IR. Scroll 1, segments à carte
d'encre publiée : distribution des scores verso vs distribution des scores recto hors lettres.
**Si vraie.** Chaque tuile recto reçoit une **valeur p** contre sa propre nulle, corrigée par
FDR (§3.4), et « colonne visible » devient « amas de tuiles significatives de la forme d'une
colonne » — un énoncé statistique, avec un taux de fausses lettres attendu, ce que « *no ink*
vs *no ink recovered yet* » demande. **Si fausse** (AUC verso > 0,6) : l'encre est visible à
travers la feuille au régime considéré ; le verso reste un témoin, mais **affaibli**, et la
nulle doit venir des marges. **Coût.** Jours.

---

## 3. Mathématiques

### 3.1 Contraste de phase, pixel, Paganin : un modèle par fréquence, pas un nombre

Pour un objet de phase faible $\varphi$ et d'absorption faible $B$, l'intensité propagée à la
distance $D$ a pour spectre (Guigay 1977 ; Cloetens *et al.* 1999) :

$$ \tilde I(f) = \delta(f) + 2\sin(\pi\lambda D f^2)\,\tilde\varphi(f) - 2\cos(\pi\lambda D f^2)\,\tilde B(f). $$

En champ proche ($\pi\lambda D f^2 \ll 1$, ce qui est le cas jusqu'à Nyquist dès que $F<1$),
$\sin(\pi\lambda D f^2)\approx\pi\lambda D f^2$ : le **gain** de contraste de phase est
$2\pi\lambda D f^2$. À la fréquence de Nyquist $f = 1/(2p)$ il vaut $\sin(\pi F^2/4)$
**exactement** : 0,118 au régime du prix, 0,459 en production **[calculé]**. C'est la seule
place où $F$ apparaît comme tel.

Paganin (2002) divise le spectre mesuré par $1 + L_P^2 k^2$ ($k = 2\pi f$), ce qui, là où
$L_P^2k^2 \gg 1$, **inverse exactement** le gain $2\pi\lambda D f^2$ sous l'hypothèse
$\delta/\beta$ homogène : le signal restitué est l'épaisseur projetée, **sans atténuation**, à
toute fréquence. Ce que le filtre change est le **bruit** : blanc en intensité, il devient
$\propto 1/(1+L_P^2k^2)$ en épaisseur — écrasé aux hautes fréquences, entier aux basses. La
« blur » de Paganin est un fait sur le bruit et sur les endroits où l'hypothèse d'homogénéité
casse, pas sur le signal.

D'où le modèle du **rapport signal/bruit par fréquence** d'un dépôt d'épaisseur $T(f)$, avant
reconstruction, en ajoutant la décohérence (un flou gaussien de largeur $\sigma_{dec} = D\sigma_\theta$,
Nesterets 2008) et l'intégration pixel :

$$ \mathrm{SNR}(f) \;\propto\; \frac{2\pi\lambda D f^2 \; e^{-2\pi^2 D^2\sigma_\theta^2 f^2}\; \mathrm{sinc}(\pi p f)\; \tilde T(f)}{\sigma_I(p, \text{dose})}, \qquad 0 < f < \tfrac{1}{2p}. $$

Trois lectures **[calculé]** : (i) à $f$ physique fixé sous $1/(2\cdot 9{,}362\,\mu m)$, le
numérateur du régime du prix est **3,8×** celui de la production ($\lambda D$) ; (ii) la
bande $f > 53\ \mathrm{mm^{-1}}$ (périodes < 19 µm) est **absente** ; (iii) $\sigma_{dec}$ est
$\propto D\sigma_\theta$ — si $\sigma_\theta \propto E^{-2}$, 2,6× plus large qu'en production.
Le dénominateur n'est pas dans le papier : le **bruit par voxel** de chaque régime se mesure
(le dépôt a `bruit_dune_fenetre`), et sans lui aucune des deux lectures n'est un SNR.

En 3D, Bronnikov (2002) montre que la reconstruction par rétroprojection de projections en
champ proche donne, sans récupération de phase, $\mu(\mathbf x) - \frac{\lambda D}{2\pi}\nabla^2\delta(\mathbf x)$ ;
avec Paganin, on revient à $\delta(\mathbf x)$. Le volume publié est donc une **carte de δ**
(densité électronique) filtrée comme ci-dessus, puis binée ×2. L'encre y est un excès de δ de
10–20 µm d'épaisseur apparente sur la face recto — **un à deux voxels** à 9,362 µm. Ce n'est
pas rien ; c'est ce que H1 doit chiffrer.

### 3.2 Le rouleau comme champ de phase à vortex ; les défauts comme résidus

Soit un champ scalaire $\psi(\mathbf x)$ sur le volume, valant $2\pi k$ sur la $k$-ième spire.
En coordonnées polaires autour de l'ombilic, la spirale d'Archimède $r = a + b\theta/2\pi$ est
le **lieu de niveau** $\psi \equiv 0 \pmod{2\pi}$ de

$$ \psi(r,\theta) = \frac{2\pi}{b}(r - a) - \theta , $$

et l'ensemble $\{\psi \in 2\pi\mathbb Z\}$ est **une seule** surface connexe : toutes les
spires, recollées à travers la coupure. $\psi$ a un **vortex** sur la courbe de l'ombilic
(sa circulation vaut $2\pi$ par tour). Le rouleau déformé est le même objet : $\psi$ lisse,
$|\nabla\psi| = 2\pi/b(\mathbf x)$ avec $b$ le pas local, $\nabla\psi \parallel \mathbf n$ la
normale locale aux feuilles. **Le recto de chaque spire est le bord intérieur du ruban** (face
vers l'axe, `2026_open_problems`), c'est-à-dire le côté $\psi$ décroissant de chaque lieu de
niveau : l'identification du recto est gratuite.

Ce qu'on mesure, c'est $\mathbf g(\mathbf x) = \omega(\mathbf x)\,\mathbf n(\mathbf x)$ (normale
par tenseur de structure, pas local par spectre ; les `normal-grids` et `lasagna` publiés en
sont une estimation), avec **une ambiguïté de signe** sur $\mathbf n$ levée par « pointe vers
l'extérieur depuis l'ombilic » partout où ce sens est défini. Trouver $\psi$ tel que
$\nabla\psi \approx \mathbf g$ est un **dépliage de phase** : la forme aux moindres carrés

$$ \min_\psi \int w(\mathbf x)\,\|\nabla\psi - \mathbf g\|^2\,d\mathbf x \quad\Longleftrightarrow\quad \nabla\cdot(w\nabla\psi) = \nabla\cdot(w\,\mathbf g) $$

est une équation de Poisson pondérée (Ghiglia & Romero 1994), résoluble par FFT ou multigrille
en $O(N\log N)$. Sa limite est connue : elle **lisse** les discontinuités au lieu de les
localiser. Le champ $\mathbf g$ mesuré n'est pas irrotationnel : là où une feuille se termine,
se dédouble ou se déchire, la circulation de $\mathbf g$ sur une petite boucle vaut $\pm 2\pi$.
Ce sont les **résidus** de Goldstein *et al.* (1988) — en langage de cristal, des dislocations
de vecteur de Burgers égal au pas. Un dépliage correct doit relier les résidus par des
**coupures de branche** que $\psi$ traverse en sautant de $2\pi$ ; le choix des coupures de
coût minimal est un **flot à coût minimal sur le graphe dual** (Costantini 1998), exact et
polynomial, avec des coûts statistiques par arête (Chen & Zebker 2001, SNAPHU). L'extension
2D+1 le long de $z$ est celle de Hooper & Zebker (2007) pour les séries temporelles InSAR.

Ce que cela apporte que le spiral fitting n'a pas, et c'est le cœur de H5 : un difféomorphisme
**ne peut pas représenter une terminaison de feuille** (« ni déchirer, ni recoller, ni
replier »), donc là où la vérité a un défaut, la spirale de Henderson « erre » ; le champ de
phase **représente** le défaut comme un résidu et une coupure. Les deux formulations sont
complémentaires : la sienne garantit une nappe, celle-ci nomme où la nappe ne peut pas être
une. ⚠ **[je ne sais pas]** si l'étape « winding angle » de ThaumatoAnakalyptor (graphe
d'instances + marches aléatoires + propagation de croyances) est équivalente à un dépliage
discret ; c'est le voisin conceptuel à lire avant d'écrire une ligne — chercher le **concept**,
pas le nom.

### 3.3 Les spires comme $K$ surfaces couplées : une coupe minimale qui s'engage

Autour d'une spirale grossière $r_0(\theta,z)$ issue de §3.2, posons la coordonnée résiduelle
$\rho = r - r_0(\theta,z)$. Les spires sont alors $K$ surfaces « terrain »
$\rho_k(\theta,z)$, ordonnées, avec

$$ \Delta_{\min} \le \rho_{k+1}(\theta,z) - \rho_k(\theta,z) \le \Delta_{\max}, \qquad |\rho_k(\theta{+}1,z) - \rho_k(\theta,z)| \le s , $$

où $[\Delta_{\min},\Delta_{\max}]$ est **le prior de pas mesuré** (160–210 µm, soit 17–22 voxels
à 9,362 µm). Li, Wu, Chen & Sonka (2006) montrent que trouver simultanément les $K$ surfaces qui
minimisent $\sum_k \sum_{(\theta,z)} c(\theta,z,\rho_k)$ sous ces contraintes se ramène à
**une seule coupe minimale** dans un graphe à $K\cdot|\theta|\cdot|z|\cdot|\rho|$ nœuds, avec
optimalité globale. Le coût $c$ est le négatif de la log-vraisemblance de « feuille ici » (la
prédiction de surface, ou $\alpha$). C'est exactement le problème des couches rétiniennes en
OCT (Garvin *et al.* 2009 ; Chiu *et al.* 2010), où les couches sont fines, contrastées à
quelques pour cent, séparées par des distances bornées.

⭐ Ce que cette formulation règle et que Henderson diagnostique sans le résoudre : ses pertes en
L1 convergent vers la **médiane** quand deux spires se contredisent, d'où l'errance ; une coupe
est **discrète**, elle choisit une spire ou l'autre — *winner takes all* par construction.
**Ce qui la fait échouer** : un pli où la feuille n'est plus univoque en $\rho$ (elle repasse
sous elle-même). C'est pourquoi elle vient **après** le champ de phase, dans une bande étroite
autour d'une spirale déjà correcte, et pas à sa place.

### 3.4 Détection d'encre comme test statistique avec témoin dans l'image

Soit $s_i$ la réponse du détecteur sur la tuile recto $i$ (66 px à 9,362 µm, pour garder la
tuile sous la lettre), et $\{s^{v}_j\}$ les réponses sur les tuiles **verso** de la même
région. Sous H7, la nulle de $s_i$ est la loi empirique de $s^{v}$ ; la valeur p est
$p_i = \#\{j : s^v_j \ge s_i\}/n_v$. Sur $m$ tuiles, le contrôle du taux de fausses
découvertes de Benjamini & Hochberg (1995) déclare significatives les tuiles telles que
$p_{(i)} \le \frac{i}{m}q$ — ce qui fournit, pour une carte d'encre, **le nombre attendu de
fausses lettres** à un $q$ donné. C'est le *look-elsewhere effect* (Gross & Vitells 2010) que
l'audit `66` note absent de tout le domaine, et c'est ce qui manque à « tuile plus petite
qu'une lettre » : cette défense borne ce qu'un modèle peut *inventer*, pas combien de fois il
se trompe.

Pour « des colonnes visibles partout », le signal structuré est la **périodicité de
l'interligne** le long de $z$. Le *epoch folding* (Leahy *et al.* 1983) replie le profil de
réponse sur une période d'essai $P$ et teste l'uniformité des phases par un $\chi^2$ à $n_b-1$
degrés de liberté ; le rapport signal/bruit du profil replié croît comme $\sqrt{n_{lignes}}$.
Une colonne de 30 lignes gagne un facteur ~5,5 sur une ligne seule : on détecte **qu'il y a du
texte et où sont les lignes** bien avant de lire une lettre, avec une valeur p par fenêtre
(balayage de $P$ corrigé par le nombre de périodes essayées, Scargle 1982). ⚠ Ce test ne rend
pas de lettre ; il rend la **grille** dans laquelle un filtre adapté à l'échelle du trait
travaille ensuite, sans prior linguistique.

### 3.5 Le prior partagé : un cristal 1D déformé

Dans le dépliage polaire, les feuilles sont un réseau 1D de période $b$ ; sa transformée de
Fourier locale a un pic à $1/b$ dont la finesse $Q = f_0/\Delta f$ mesure la régularité de
l'enroulement dans la fenêtre. La déformation est un **champ de déformation** $\epsilon(\mathbf x)$ ;
les résidus de §3.2 sont ses dislocations. L'hypothèse H6 est que la loi de $(b, Q, \epsilon)$
est la même pour les treize — *le même objet physique treize fois* — ce qui est déjà vrai de
$b$ **[établi]**. Si c'est vrai de $Q$, la fraction de volume à $Q$ effondré est un **coût
d'annotation prédit** par rouleau, calculable avant de choisir lequel dérouler.

---

## 4. Algorithmes

Décrits pour être implémentés ; complexité et mode d'échec à chaque fois.

### A1 — Le spectre d'AUC (H1) et la dose-réponse de lisibilité

1. Charger les couches 2,215 µm de 500P2 (26 du milieu, comme `63`) et `inklabels`.
2. Pour chaque coupure $c \in \{5,10,15,20,30,50\}$ µm : filtrer en plan (gaussienne
   $\sigma = c/2{,}355$) ; séparément en profondeur ; inférer ; AUC + mélange.
3. Répéter avec le **bruit ajouté** mesuré au régime du prix (variance d'une fenêtre vierge
   des couches 9,362 µm), pour séparer bande perdue et bruit.
4. Inférer sur les couches natives 9,362 µm avec un modèle à tuile 66 px et pile réduite
   (~12 couches ≈ 110 µm ; 62 couches feraient 580 µm, six fois la feuille).
5. Dose-réponse : appliquer l'opérateur A6 aux couches de 1667, rendre, lecture en aveugle
   avec condition vierge, lisibilité par colonne.

Échec possible : le modèle à 2,215 µm a appris la craquelure et rien d'autre — alors l'étape 4
avec un modèle **ré-entraîné** au régime du prix est la seule mesure valable, et c'est pour ça
qu'elle est là. Coût : heures de GPU.

### A2 — Carte de résidus depuis les champs publiés (H5)

Entrées : `normal-grids` (ou `lasagna` : cos et gradient) et la prédiction de surface, niveau 1
(18,7 µm ; le pas fait 10 voxels — le niveau 2 à 5 voxels par pas est trop grossier pour
distinguer deux feuilles). Ombilic : le dépôt `spiral-fitting` a `scroll1_umbilicus.py`.

1. Orienter $\mathbf n$ vers l'extérieur (signe de $\mathbf n\cdot(\mathbf x - \mathbf o)$,
   $\mathbf o$ l'ombilic de la tranche) ; là où $|\mathbf n\cdot\hat{\mathbf r}| < 0{,}3$, poids nul.
2. Pas local $b(\mathbf x)$ par autocorrélation de la prédiction de surface le long de $\mathbf n$
   sur une fenêtre de 3 pas ; $\mathbf g = (2\pi/b)\,\mathbf n$.
3. Sur chaque tranche $z$, circulation discrète de $\mathbf g$ sur chaque plaquette de 4
   voxels ; résidu si $|\oint \mathbf g| \ge \pi$. Puis les plaquettes $(z,z{+}1)$ pour les résidus
   axiaux.
4. Sortie : densité de résidus par fenêtre, et la liste des résidus avec leur signe.
5. Contrôle : sur une spirale synthétique parfaite, zéro résidu hors de l'ombilic ; avec une
   feuille tronquée insérée, exactement deux résidus de signes opposés à ses bouts.

$O(N)$, mémoire d'une tranche. Échec : là où le champ d'orientation publié est lui-même faux
(régions comprimées), les résidus prolifèrent — mais c'est *l'information* qu'on cherche, à
condition de vérifier (étape 5 puis H5) qu'ils co-localisent avec les vrais sauts et non avec
le seul bruit du champ.

### A3 — Dépliage global par flot à coût minimal, niveau 1, par dalles en $z$

1. Coupure de branche imposée : le demi-plan $\theta = 0$ depuis l'ombilic (la spirale y saute
   de $2\pi$ par construction).
2. Résidus de A2 ; coûts d'arête $= 1/(w + \epsilon)$ avec $w$ la prédiction de surface
   (une coupure traverse de préférence le vide entre feuilles, jamais une feuille).
3. Flot à coût minimal (Costantini 1998) sur le graphe dual d'une tranche ; SNAPHU en est une
   implémentation publique (Chen & Zebker 2001–2002) ; taille $\sim 10^6$ nœuds par tranche
   au niveau 1, secondes.
4. Cohérence en $z$ : dalles de 64 tranches avec 8 de recouvrement ; les sauts de $2\pi$
   entre dalles sont résolus par vote sur le recouvrement (Hooper & Zebker 2007 pour la
   version 3D exacte si le vote échoue).
5. Sortie : $\psi$ entier par voxel = **numéro de spire**, et le lieu $\psi \in 2\pi\mathbb Z$
   contraint à la crête de la prédiction = surface initiale de **toutes** les spires d'un coup ;
   le recto est le bord $\psi$-décroissant.

Échec : l'ombilic n'est pas une courbe simple (rouleau écrasé en « S », ou deux noyaux). Il faut
alors un vortex par noyau et une coupure entre eux ; le résidu net autour de l'ensemble doit
valoir le nombre de tours — c'est vérifiable et c'est un test unitaire.

### A4 — Raffinement par $K$ surfaces couplées, dans une bande

1. Depuis A3, pour chaque dalle, la spirale grossière $r_0(\theta,z)$ et le numéro de spire.
2. Rééchantillonner le volume (niveau 0) en $(\theta, z, \rho)$ avec $\rho \in [-10, +10]$ voxels
   autour de chaque spire : $K$ bandes de 20 voxels.
3. Graphe de Li *et al.* (2006) : $K \times |\theta| \times |z| \times 20$ nœuds ; pour une dalle
   de 32 tranches, 2 000 $\theta$, $K = 80$ : $\sim 10^8$ nœuds — à la limite d'une coupe
   Boykov–Kolmogorov (2004) en mémoire ; découper en secteurs de $\theta$ avec recouvrement.
4. Contraintes : séparation $[17, 22]$ voxels entre $k$ et $k{+}1$, lissage $s = 1$ voxel par pas
   en $\theta$ et en $z$.
5. Sortie : $\rho_k$ sous-voxel par interpolation du coût autour de la coupe ; export
   `tifxyz` par spire (`lasagna` sait déjà écrire « one per winding »).

Échec : un pli ou une délamination où la feuille n'est pas univoque en $\rho$ ; la coupe
choisit une des deux branches et **le dit** (le coût résiduel y est élevé). Ces régions vont
au pinceau — et elles sont énumérées, ce qui est l'objet de H4.

### A5 — `approval.tif` automatique, et le contrôle qui le rend honnête

1. Pour un maillage `tifxyz`, calculer par sommet : $\alpha$ (convergence), la densité de
   résidus (A2) dans un rayon de 2 pas, le coût résiduel de A4, le saut de spire par la phase
   (`nappe/`).
2. Approuvé = $\alpha < 0{,}3$ **et** zéro résidu à portée **et** pas de saut. Tout le reste
   non approuvé, avec **la raison** dans un second canal.
3. Écrire `approval.tif` à côté de `x/y/z.tif` ; laisser `GrowPatch` ré-optimiser.
4. Contrôle à trois bras sur une spire de 1667 : masque automatique / masque vide / masque
   plein ; écart de maillage contre la spire publiée pour les trois. Si l'automatique n'est
   pas strictement entre les deux témoins, il ne fait rien.

Échec : `GrowPatch` ré-optimise vers ce que le masque approuve ; un masque qui approuve une
erreur la fige. D'où le seuil conservateur et le second canal : mieux vaut sous-approuver et
laisser au pinceau que sur-approuver.

### A6 — L'opérateur de dégradation ajusté, pas supposé

Le dépôt a déjà dégradé des fragments par sous-échantillonnage (`58`, `63`) et conclu que la
résolution n'explique pas l'écart. Mais un sous-échantillonnage n'est pas une acquisition au
régime du prix : il ne reproduit ni le noyau de Paganin à 32 µm, ni le flou de décohérence, ni
le bruit après le masque flou inverse. Les paires recalées permettent de **l'ajuster** :

1. Sur 500P2 (et 139, 814, 343P), les piles 2,215 µm / 0,4 m et 9,362 µm / 1,2 m recalées.
2. Modèle : $y = (h * x)\downarrow_4 + \eta$, avec $h$ un noyau 3D anisotrope (plan / normale)
   et $\eta$ un bruit de spectre libre ; ajuster $h$ par moindres carrés dans Fourier sur les
   régions communes, $\eta$ par le résidu.
3. Contrôle : sur le 4ᵉ objet non utilisé, le spectre de puissance de $y$ simulé égale celui
   de $y$ mesuré à 10 % près par bande.
4. Appliquer à toutes les couches étiquetées de 1667 (22 colonnes transcrites) et de Paris 4 :
   des milliers de lettres au régime du prix, **avec leur vérité**.
5. Entraîner le détecteur du prix dessus ; tester sur les couches **réelles** 9,362 µm de
   500P2 et 139 (les 103 cases vides deviennent 103 cas de test, pas des besoins
   d'annotation).

Échec : le déplacement de domaine fragment→rouleau (plat / enroulé, air / matière autour) que
l'opérateur ne modélise pas ; le papier l'a franchi avec des pseudo-étiquettes, et c'est le
même remède ici.

### A7 — Détection avec témoin verso, FDR, repliement d'interligne

1. Pour chaque colonne de voxels du maillage, deux piles : recto (bord intérieur, +0 à +20 µm)
   et verso (bord extérieur, −20 à 0 µm) — l'asymétrie est **physique**, l'encre est sur une
   face.
2. Scores par tuile 66 px des deux côtés ; nulle empirique = verso ; valeurs p ; BH à $q = 0{,}05$.
3. Repliement de la réponse recto le long de $z$ sur $P \in [P_{\min}, P_{\max}]$ (l'interligne
   par autocorrélation du dépôt donne la plage) ; $\chi^2$ de repliement ; correction par le
   nombre de $P$ essayés.
4. Sortie : carte de tuiles significatives, grille des lignes de base, et **le nombre attendu
   de fausses lettres** dans la carte.

Échec : si H7 est fausse (encre visible à travers la feuille), la nulle verso est décalée vers
le haut, le test devient **conservateur** — il manque des lettres, il n'en invente pas. C'est
le bon sens de l'erreur pour un critère « sans reconstruction papyrologique ».

---

## 5. Emprunts hors domaine, avec le transport

| domaine | référence réelle | ce qui se transporte, précisément |
|---|---|---|
| **InSAR** | Goldstein, Zebker & Werner, *Radio Science* 23(4):713–720, 1988 ; Ghiglia & Pritt, *Two-Dimensional Phase Unwrapping*, Wiley 1998 ; Costantini, *IEEE TGRS* 36(3):813–821, 1998 ; Chen & Zebker, *JOSA A* 18(2):338–351, 2001 ; Hooper & Zebker, *JOSA A* 24(9):2737–2747, 2007 | les **résidus** comme charge topologique du champ d'orientation, les coupures de branche par **flot à coût minimal** (exact), l'extension 2D+1 en $z$ (§3.2, A2, A3) |
| **sismique de réflexion** | Lomask *et al.*, « Flattening without picking », *Geophysics* 71(4):P13–P20, 2006 ; Stark, *The Leading Edge* 23(9):928–932, 2004 ; Wu & Zhong, *Geophysics* 77(4):O21–O34, 2012 ; Wu & Hale, *Geophysics* 80(2):IM21–IM33, 2015 ; Hale, *Geophysics* 78(2):S105–S115, 2013 ; Marfurt *et al.*, *Geophysics* 63(4):1150–1165, 1998 | le **volume de temps géologique relatif** = le volume de « numéro de spire continu » ; Wu & Zhong le calculent littéralement par *dépliage de phase par coupe de graphe avec contraintes de failles* — une faille est une déchirure de feuille ; l'aplatissement de Lomask est notre Poisson pondéré ; la **déformation dynamique** de Hale aligne deux spires adjacentes le long de $\theta$ et rend le pas sous-voxel ; la **cohérence** de Marfurt est un $\alpha$ sans vérité terrain |
| **OCT rétinienne** | Li, Wu, Chen & Sonka, *IEEE TPAMI* 28(1):119–134, 2006 ; Garvin *et al.*, *IEEE TMI* 28(9):1436–1447, 2009 ; Chiu *et al.*, *Optics Express* 18(18):19413–19428, 2010 | $K$ surfaces couplées à séparation bornée, **une** coupe minimale globalement optimale (§3.3, A4) ; le prior de pas 160–210 µm est la contrainte de séparation |
| **cryo-tomographie électronique** | Martinez-Sanchez *et al.*, *J. Struct. Biol.* 186(1):49–61, 2014 (TomoSegMemTV) ; Medioni, Lee & Tang, *A Computational Framework for Segmentation and Grouping*, Elsevier 2000 | le **vote tensoriel** propage la saillance de surface à travers les trous d'une membrane de 3–5 voxels dans un milieu non vide — exactement le ruban de 3–5 voxels du marcheur ; à essayer comme post-traitement de la prédiction m7 avant A2, mesuré par la métrique topologique du Kaggle « Surface Detection » |
| **analyse de franges optiques** | Takeda, Ina & Kobayashi, *JOSA* 72(1):156–160, 1982 ; Felsberg & Sommer, *IEEE TSP* 49(12):3136–3144, 2001 | le dépliage polaire est un **motif de franges à porteuse** $1/b$ : sa phase enroulée s'extrait par filtrage de la bande latérale (Takeda) ou par le **signal monogène** (orientation + phase locale en 3D) — la phase locale dit sur quel bord du ruban on est, donc **recto ou verso** au sous-voxel |
| **physique du contraste de phase** | Guigay, *Optik* 49:121–125, 1977 ; Wilkins *et al.*, *Nature* 384:335–338, 1996 ; Cloetens *et al.*, *APL* 75(19):2912, 1999 ; Paganin *et al.*, *J. Microsc.* 206(1):33–40, 2002 ; Bronnikov, *JOSA A* 19(3):472–480, 2002 ; Nesterets, *Opt. Commun.* 281(4):533–542, 2008 (« On the origins of decoherence… ») ; Weitkamp *et al.*, *J. Synchrotron Rad.* 18:617–629, 2011 | le modèle par fréquence du §3.1 ; Nesterets nomme et modélise la **décohérence par microstructure non résolue** exactement comme le papier la décrit ; Weitkamp (ANKAphase) est l'implémentation de référence du filtre pour refaire le calcul de $L_P$ |
| **encre carbonée en CT** | Mocella *et al.*, *Nat. Commun.* 6:5895, 2015 ; Bukreeva *et al.*, *Sci. Rep.* 6:27227, 2016 ; Parker *et al.*, *PLoS ONE* 14(5):e0215775, 2019 ; Angelotti *et al.*, arXiv 2603.27698, 2026 | l'encre est détectable par **contraste de phase** (Mocella) puis par **morphologie de surface** (Angelotti 2026) : les deux disent qu'elle est un fait de **frontière**, ce qui justifie l'asymétrie recto/verso d'A7 |
| **statistique de détection** | Benjamini & Hochberg, *JRSS B* 57(1):289–300, 1995 ; Gross & Vitells, *Eur. Phys. J. C* 70:525–530, 2010 ; Leahy *et al.*, *ApJ* 266:160–170, 1983 ; Scargle, *ApJ* 263:835–853, 1982 | FDR par tuile, *look-elsewhere*, **repliement d'époque** sur l'interligne (§3.4, A7) |
| **papyrologie** | Johnson, *Bookrolls and Scribes in Oxyrhynchus*, Toronto 2004 ; Cavallo, *Libri scritture scribi a Ercolano*, 1983 ; Turner, *Greek Papyri*, 1968 | les **priors de mise en page** (largeur de colonne, intercolonne, interligne, marges) qui bornent $P$ dans le repliement et dessinent la « forme d'une colonne » ; ⚠ **[je ne sais pas]** les valeurs numériques pour Herculanum de mémoire — à lire dans Cavallo, et à recouper avec l'interligne mesuré du dépôt sur Scroll 1 |

**Analogies que je rejette après y avoir réfléchi**, pour qu'on ne les repropose pas : les
*contact maps* Hi-C (elles décrivent des contacts entre régions d'un polymère, sans géométrie
d'enroulement régulière — le rouleau n'a pas ce problème, il a un pas) ; la théorie des nœuds
(le rouleau n'est pas noué, sa topologie est celle d'un disque ; le seul invariant utile est
le nombre d'enroulement, déjà dans $\psi$) ; la cristallographie au-delà du §3.5 (pas de
diffraction réelle ici, la « frange » de Bragg n'est qu'un spectre local).

---

## 6. Ce que je ferais en premier, avec vos instruments et dix mois

**Mois 1 — trancher la physique avant la géométrie.** A1 et H2 sur 500P2 : le spectre d'AUC,
l'AUC native à 9,362 µm, l'AUC à 4,317 µm / 1,2 m, les ESF, le bruit par régime. À la fin du
mois on sait si le régime du prix est un problème de **bande** (alors la suite est géométrique)
ou de **perte** (alors la lettre à l'ESRF part le jour même). Puis A6 et la dose-réponse de
lisibilité sur 1667 : le chiffre « fraction de lettres lisibles à ce régime » sur un texte
connu, **avant** d'investir dans un rouleau.

**Mois 2–3 — la carte de résidus et l'approbation automatique** (A2, A5, H4, H5) sur 1667 et
Scroll 1, où il y a de quoi comparer (maillage publié, WJF localisé). Livrable : `approval.tif`
avec raisons, et le contrôle à trois bras.

**Mois 3–6 — le dépliage global puis la coupe couplée** (A3, A4) sur **un** rouleau du prix.
Choix : **PHerc0826** (60 spires, le moins de spires des treize dans l'atlas) sauf si H6 lui
trouve une fraction à $Q$ effondré plus élevée que celle de **PHerc1447** (15 segments publiés,
le plus travaillé). ⚠ Peu de spires peut vouloir dire un *midollo* abîmé ; c'est H6 qui
départage, pas le compte.

**Mois 6–8 — l'encre au régime du prix** (A6, A7) : modèle entraîné sur la dégradation ajustée,
testé sur les cases vides réelles, cartes avec FDR et grille d'interligne.

**Mois 8–10 — VC3D, reproductibilité, soumission.** Le point de branchement est un fichier ;
le reste est de l'hygiène que ce dépôt sait faire (`depot/`).

---

## 7. Ce dont je doute

- **Le modèle du §3.1 suppose un objet de phase faible et l'homogénéité de δ/β.** Un rouleau
  de 5 cm de papyrus carbonisé n'est ni l'un ni l'autre ; la correction de premier ordre est la
  décohérence, mais il peut y avoir un terme que je ne vois pas (diffusion multiple, durcissement
  résiduel du faisceau que le papier dit négligeable). **Ce qui me ferait changer d'avis** : une
  ESF mesurée (H3) plus large que ce que $D\sigma_\theta$ prédit, ou un spectre d'AUC (H1) qui
  chute là où le modèle dit que rien n'est perdu.
- **« Le débinage ne rend presque rien » (H2) est une conjecture sur une phrase du papier**, et
  le verdict « haze-limited » du 4,317 µm pourrait tenir à un autre bras (le 4,317 µm / 1,2 m de
  500P2 est-il la même acquisition que le 9,362 µm « HA » ? le papier ne le dit pas). Si l'AUC
  à 4,317 dépasse nettement l'AUC à 9,362, je me trompe, et c'est la meilleure nouvelle possible.
- **Les résidus pourraient être partout où le champ d'orientation est bruité**, et nulle part
  ailleurs — c'est-à-dire mesurer la qualité de la prédiction m7, pas la topologie du rouleau.
  Le contrôle est H5 : co-localisation avec les vrais sauts. Sans elle, A2 est un détecteur de
  bruit avec un beau nom.
- **La coupe à $K$ surfaces suppose un ordre en $\rho$.** Dans les régions où le papier dépense
  ses 25 h par spire, c'est peut-être exactement là que l'ordre n'existe pas. Alors A4 énumère
  les régions et n'en résout aucune ; c'est encore utile, mais moins que je l'écris.
- **Le verso comme nulle (H7) suppose que l'encre ne traverse pas.** À 9,362 µm avec une feuille
  de 3–4 voxels et un dépôt de 1–2 voxels, la fuite est plausible. Le test est écrit ; s'il rend
  une AUC verso de 0,6, la nulle vient des marges et le repliement d'interligne devient la
  pièce principale.
- **Je ne connais pas la dose par voxel des scans du prix.** Tout le raisonnement en SNR est
  suspendu à $\sigma_I$, et un scan de repérage « optimisé pour le débit » (`68` §3) a pu être
  fait vite. Une seule mesure de bruit sur une fenêtre vierge par régime tranche.
- **Le voisin conceptuel que je n'ai pas lu** : l'assignation de « winding angle » de
  ThaumatoAnakalyptor. Si elle est déjà un dépliage avec résidus sous un autre nom, la
  contribution de §3.2 se réduit à l'exactitude du flot à coût minimal — ce qui reste vrai, mais
  plus petit. La règle du `66` s'applique à moi : chercher le concept, jamais le nom.

**Les données manquantes qui débloqueraient, par ordre de valeur** : (1) les volumes non binés
à 4,3–4,7 µm des treize rouleaux (ESRF, existent) ; (2) la paire 0,6 m / 1,2 m de PHerc. 268 ;
(3) les masques d'approbation humains de 1667 ; (4) le temps d'exposition et le nombre de
projections par scan (pour $\sigma_I$) ; (5) les étiquettes d'entraînement de `surface-m7`.

---

*Arithmétique dans `docs/mesures/69_arithmetique.py` ; formules et entrées
reproduites en clair ci-dessus pour qu'un instrument du dépôt puisse les reprendre.*
