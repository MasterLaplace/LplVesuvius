# `215` — Le résidu suit-il ce que la rangée a lu ? Non, et l'ajustement dit pourquoi il ne pouvait presque pas le voir

*Ce qui rompt l'additivité n'est pas dans ce que les rangées ont lu — et la moitié de la raison est que l'ajustement absorbe d'avance tout ce qui agit additivement.*

![Le résidu suit-il ce que la rangée a lu](../images/215_le_residu_suit_il_ce_que_la_rangee_a_lu.png)

## 0. Pourquoi cette tranche

`214` a posé une question et en a refermé une autre. La question posée était celle de `R4-P59` : le
désaccord par couture de deux rangées croît-il avec leur **écartement** sur le treillis ? La réponse
est **non** — tendance de rangs **-0,1024**, **16** rebrassages sur **19** au moins aussi forts, et
les extrêmes du nuage ne tombent pas aux extrêmes de l'échelle.

Mais le contrôle gratuit que `212` avait posé s'est retourné. À **neuf** rangées le triangle porte
**36 équations pour 9 inconnues**, et un système sur-déterminé peut refuser le modèle sans qu'aucun
seuil n'entre là : sous l'additivité ses résidus sont nuls aux erreurs d'échantillonnage près. Ils ne
le sont pas — **3,6279 erreurs** sur la paire `197-198` contre un résidu médian de **0,8039**.

La hauteur d'une bande cesse donc d'être gratuite **sans que la distance y soit pour rien**, et
`R4-P60` demande ce qui la rend payante. Cette tranche prend la **piste A** de la porte : celle qui
ne demande **aucune lecture neuve du volume**, parce que tout ce dont elle a besoin est déjà publié
par `214`.

## 1. ⚠⚠⚠ La statistique est déclarée d'avance, et ce n'est pas celle que la porte prescrivait

`R4-P60` proposait une forme précise : agréger les résidus **par rangée** — une rangée entre dans
**huit** des trente-six paires — et prendre le maximum sur les neuf comme statistique de famille. Ce
n'est **pas** la statistique déclarée de cette tranche, et les deux raisons se disent :

1. **elle répond « QUELLE rangée », jamais « QUOI ».** Savoir que le résidu se concentre sur `198`
   ne nomme pas ce que `198` a de particulier. Cette forme ne peut donc pas fermer la porte ; au
   mieux elle en ouvre une plus étroite ;
2. ⚠⚠ **elle a été REGARDÉE pendant la conception de cette tranche.** Une statistique vue puis
   déclarée est une statistique **choisie**, et c'est exactement ce que `214` a refusé de faire
   lorsqu'il a écarté sa propre règle plus puissante.

Elle est donc portée comme **contrôle nommé**, avec son compte de rebrassages — le précédent est
celui de `214`, qui porte de la même façon la règle qu'il avait refusée. Le §7 la rend.

Et la contrainte qui reste est la seule qui compte ici. `214` a **mesuré** que le nul par permutation
d'étiquettes tient sa garantie sur des résidus — **9/171 = 0,0526** contre **0,05** — donc aucun nul
paramétrique n'est requis, et en construire un serait payer un outil dont la mesure dit qu'on n'a pas
besoin. Ce qui coûte, c'est de **déclarer la statistique avant de la voir**.

## 2. ⚠⚠⚠ L'agrégat évident est interdit par le modèle lui-même

Avant de choisir un agrégat, il faut en éliminer un, et ce n'est pas une mesure : c'est une identité.

L'ajustement au moindre carré annule la dérivée de la somme des carrés par rapport à chaque inconnue.
Pour la rangée $i$, cette dérivée vaut

$$\frac{\partial}{\partial \hat\sigma^{2}_{b,i}} \sum_{(j,k)} r(j,k)^{2} \;=\; -2 \sum_{j \neq i} r(i,j) \;=\; 0$$

donc la **somme des huit résidus bruts d'une rangée est nulle**, quoi qu'il arrive, sur n'importe
quelle matière — y compris une matière qui casse l'additivité de toutes les façons possibles.

Mesuré sur ce que `214` publie : la plus grande somme signée par rangée vaut **0,0002** vx² pour une
borne d'arrondi **dérivée** de **0,0004** — huit résidus publiés à quatre décimales, donc au pire
huit demi-unités du dernier chiffre.

⚠⚠⚠ **Deux conséquences, et la seconde est la plus importante.** D'abord, un agrégat de **position**
est ici une vérification **incapable d'échouer** : c'est le péché nommé en tête de ce dépôt, et il
fallait le publier sous cette forme pour empêcher qu'on le réécrive. Ensuite, et c'est le fait de
fond : **un effet de rangée UNIFORME est absorbé dans la variance ajustée de cette rangée et ne
laisse aucune trace.** Seul un effet **non uniforme** — bien s'accorder avec certaines partenaires et
mal avec d'autres — survit dans les résidus.

L'agrégat doit donc être une **dispersion**. C'est forcé, pas choisi.

## 3. La famille déclarée : trois covariables, deux formes

Les neuf rangées de `214` n'ont pas lu la même chose, et c'est publié :

| rangée | colonnes lues | refusées faute de texture | pas rendus |
|---:|---:|---:|---:|
| 182 | **260** / 285 | **0** | **259** |
| 190 | **246** / 285 | **7** | **240** |
| 194 | **253** / 285 | **2** | **250** |
| 197 | **255** / 285 | **1** | **253** |
| 198 | **251** / 285 | **6** | **243** |
| 199 | **254** / 285 | **3** | **250** |
| 202 | **254** / 285 | **3** | **250** |
| 206 | **252** / 285 | **4** | **247** |
| 214 | **258** / 285 | **8** | **250** |

⚠ La porte nomme les deux premières. La troisième est ajoutée par `215`, **avant** tout calcul, parce
que les pas rendus sont la troisième façon dont une rangée peut manquer de matière ; l'ajouter après
coup n'aurait pas été légitime.

Une propriété de **rangée** doit devenir une propriété de **paire**, et aucune des deux façons n'est
évidente : « elles n'ont pas lu la même chose » est l'**écart** $|c_i - c_j|$, « la plus pauvre des
deux commande » est le **minimum** $\min(c_i, c_j)$. Les deux sont déclarées.

La famille est donc le produit : **six membres**. Son maximum est comparé au maximum du **même** nul,
donc le choix d'un candidat parmi six est **payé** au lieu d'être fait après les avoir vus — c'est le
remède que `179` a dû inventer pour la largeur de son creux.

La statistique déclarée, en une ligne : le **maximum sur les six membres** de la corrélation de rangs
entre la covariable de paire et le **résidu signé** de l'ajustement additif. Le signe est déclaré
parce que `214` l'a **mesuré** : sa sonde a montré que la règle signée voit 6/6 là où l'amplitude
n'en voit que 1/6. Ce n'est pas un choix, c'est une mesure antérieure.

⚠⚠ **Le nul rebrasse l'attache rangée↔lecture, jamais les résidus.** C'est la seule façon de détruire
le lien qu'on teste en gardant intacte la structure qui le porte : chaque rangée reste dans ses huit
paires, chaque paire garde son résidu, seul ce que la rangée a lu se déplace. Rebrasser les résidus
casserait la contrainte que l'ajustement leur impose — leur somme par rangée est nulle, §2 — donc
produirait des configurations que l'ajustement ne peut **pas** produire.

⚠⚠ **Et une symétrie structurelle se calcule au lieu de se découvrir par tirage.** Les rangées **199**
et **202** portent **les mêmes valeurs sur les trois covariables** : 254 colonnes lues, 3 refus de
texture, 250 pas. Les échanger laisse la famille entière inchangée, donc ce rebrassage-là refait
l'observé et ne doit pas compter comme une face du nul. Sur neuf rangées il vaut **deux** tirages sur
**neuf factorielle**, donc l'échantillonnage ne le rencontrerait presque jamais — le publier le rend
vérifiable.

## 4. ⭐⭐⭐⭐ La limite structurelle : ce qu'un ajustement additif laisse passer

C'est la pièce sans laquelle un négatif ne veut rien dire, et elle **se calcule**.

Un résidu d'ajustement est, par construction, **orthogonal** à l'espace que l'ajustement sait
représenter : ici toutes les grandeurs par paire de la forme $f(i) + f(j)$. Une covariable dont
l'effet est **additif** est donc absorbée en entier dans les variances ajustées et ne laisse
**rien** dans les résidus.

La part qui survit se mesure en projetant la covariable centrée sur l'espace additif et en regardant
ce qui reste :

| membre | part non additive |
|---|---:|
| `refus_faute_de_texture · lecart` | **0,7955** |
| `pas_rendus · lecart` | **0,5024** |
| `colonnes_lues · lecart` | **0,5017** |
| `refus_faute_de_texture · le_minimum` | **0,4505** |
| `pas_rendus · le_minimum` | **0,2785** |
| `colonnes_lues · le_minimum` | **0,2576** |

⚠⚠⚠ **Une covariable absorbée n'est PAS une covariable inactive : elle n'agit pas NON
additivement.** Et c'est cohérent avec la question posée — `R4-P60` demande ce qui **rompt**
l'additivité ; une covariable qui agit additivement ne la rompt pas, par définition. Mais sans cette
table, une borne se lirait « cette covariable n'agit pas » au lieu de « pas non additivement », ce
qui est une affirmation bien plus large que ce que la mesure porte.

⚠ Les formes en **minimum** sont les plus absorbées, et c'est structurel : $\min(a,b)$ est proche
d'une somme quand les valeurs sont proches, ce qu'elles sont ici. Les formes en **écart** passent
mieux. La plus visible de toutes est `refus_faute_de_texture · lecart`, dont l'ajustement ne mange
que **deux dixièmes**.

## 5. Le résultat : non

| membre | corrélation de rangs au résidu signé |
|---|---:|
| `pas_rendus · lecart` | **-0,0972** |
| `colonnes_lues · lecart` | **-0,0823** |
| `colonnes_lues · le_minimum` | **0,0584** |
| `pas_rendus · le_minimum` | **0,0385** |
| `refus_faute_de_texture · lecart` | **0,0173** |
| `refus_faute_de_texture · le_minimum` | **0,0093** |

Le maximum de la famille vaut **0,0972**, porté par `pas_rendus · lecart`. Le nul rend une famille
médiane de **0,1628** et une famille la plus forte de **0,4015**, et **16** rebrassages sur **19**
font au moins aussi fort.

⚠ **L'observé est sous le médian du nul.** Ce n'est pas un détail de présentation : une famille de
six candidats produit mécaniquement un maximum d'une certaine taille même quand rien ne se passe, et
l'observé n'atteint même pas ce niveau-là. Le négatif n'est pas serré, il est franc.

**Ce que les neuf rangées ont lu n'explique pas ce qui casse l'additivité.**

## 6. ⭐⭐⭐⭐ Le négatif est une borne, parce que l'étalon dit jusqu'où la règle voit

Un négatif sans étalon est un silence. Ce qui le transforme en borne est de savoir ce que la règle
**aurait** vu.

La matière fabriquée porte l'additivité **exactement vraie**, plus un lien connu à une covariable
nommée, plus le bruit d'échantillonnage **dérivé** $\mathrm{se}(V) = V\sqrt{2/(n-1)}$ — la même
formule que l'ajustement emploie pour standardiser ses résidus, donc l'étalon et la mesure parlent de
la même erreur. L'ajustement qui la lit est **celui de `214`**, importé et non réécrit : deux
implémentations d'un ajustement additif finiraient par ne pas s'accorder sur le `rcond` ou sur
l'ordre des équations.

⚠⚠ Le lien est compté **en erreurs d'échantillonnage** et non en voxels carrés : un facteur quatre
veut dire « quatre erreurs d'écart d'un bout à l'autre de la covariable ». Et il est injecté sur le
membre **le plus visible** — injecter sur un membre que l'ajustement absorbe presque entièrement
mesurerait la **projection** et non la règle.

| facteur | vu par la règle déclarée | vu par la règle que la porte prescrivait |
|---:|---:|---:|
| ×1 | **2/12** | 1/12 |
| ×2 | **5/12** | 0/12 |
| ×3 | **9/12** | 0/12 |
| ×4 | **12/12** | 1/12 |
| ×6 | **12/12** | 0/12 |

La suite est **monotone**, et le plus petit facteur vu par tous les réplicats est **4**.

- taux de **faux** : **9/171 = 0,0526** contre une garantie de **0,05** — la règle tient sa garantie ;
- taux **aveugle** : **8/171 = 0,0468** — il la tient aussi ;
- **0** variance négative rencontrée sur les **60** courses de l'échelle, donc le contrôle gratuit de
  `212` n'a jamais été violé par la matière fabriquée.

⚠⚠⚠ **Le contrôle aveugle ne peut pas être propre sur neuf rangées, et ça se diagnostique au lieu de
se subir.** Rebrasser neuf étiquettes ne détruit pas le lien : une permutation tirée au hasard garde
avec l'identité une corrélation de rangs dont l'écart-type vaut $1/\sqrt{8}$, soit environ un tiers.
Une part des tirages aveugles est donc une version **affaiblie** du vrai lien, pas une matière sans
lien. Mesuré : les aveugles qui **tirent** ressemblent à l'identité à **0,5462** en médiane, ceux qui
**se taisent** à **0,2521**. Le taux aveugle non nul est donc entièrement expliqué par les
permutations qui ont conservé le lien, et non par une règle qui tirerait sur n'importe quoi.

**La borne** : un lien de **4** erreurs d'échantillonnage sur la covariable la **mieux** vue aurait
été trouvé douze fois sur douze. Rien de tel n'est là.

## 7. La règle que la porte prescrivait, et la rangée `198` n'est pas payée

`214` avait relevé deux lectures post hoc et écrit qu'aucune n'était payée : les trois plus gros
résidus sont tous **négatifs**, et la rangée **198** est dans deux des trois. La seconde se paie ici.

L'agrégat est une **dispersion**, forcé par le §2 : l'énergie d'une rangée est la somme des carrés de
ses huit résidus standardisés.

| rangée | énergie |
|---:|---:|
| 194 | **4,3756** |
| 182 | **4,6947** |
| 202 | **5,1684** |
| 190 | **6,9991** |
| 197 | **17,4701** |
| 199 | **17,8354** |
| 206 | **17,9932** |
| 214 | **21,0343** |
| **198** | **32,3057** |

La rangée **198** porte bien le maximum, **32,3057** contre un médian de **17,4701**. Mais le nul
rend une énergie médiane de **29,5784** et une plus forte de **42,8961**, et **3** rebrassages sur
**19** font au moins aussi fort.

⚠⚠⚠ **La lecture post hoc de `214` n'est donc PAS payée.** Le maximum sur neuf rangées est
mécaniquement grand, et `32,3057` n'atteint pas ce que le hasard produit couramment. Le chiffre qui
le dit le plus clairement est le médian du nul : **29,5784**, presque l'observé.

⚠ **Le nul de cette règle rebrasse les ARÊTES, pas les étiquettes de rangée**, et la raison est une
vérification incapable d'échouer évitée de justesse. Le treillis est **complet** : renommer les
rangées permute les énergies sans en changer aucune, donc le maximum sur les neuf est **rigoureusement
invariant**. Un nul par étiquettes aurait rendu `19/19` sur toute matière possible. Ce qui doit
bouger, c'est **quelles paires** portent les gros résidus.

⚠ Et la limite de ce rebrassage se dit : il ne préserve pas la contrainte de somme nulle par rangée,
donc il explore des configurations plus libres que celles qu'un ajustement peut produire. Le sens de
l'écart n'est pas raisonné mais **mesuré** — c'est le taux de faux de l'étalon, et la colonne de
droite du tableau du §6 montre d'ailleurs que cette règle-ci est **beaucoup moins puissante** que la
déclarée : elle ne voit jamais plus de 1/12, même à ×6.

## 8. Les deux pièges, et l'un dément la dérivation qui l'a posé

**Le piège nommé.** L'erreur d'une variance vaut $V\sqrt{2/(n-1)}$, donc elle croît avec la
**valeur**. Une rangée de grande variance propre a de grands désaccords avec tout le monde, donc de
grandes erreurs, donc des résidus standardisés plus **petits**. Le sens **attendu** de la corrélation
énergie↔variance propre est donc **négatif**.

⚠⚠ **Mesuré, il est POSITIF : 0,4.** La dérivation est démentie par la matière. Les deux se publient
côte à côte plutôt que l'attendu réécrit après coup — c'est le motif que ce dépôt attrape en boucle,
un commentaire qui dit l'inverse de ce que la mesure rend. Le rebrassage ajoute que **4** tirages sur
**19** font au moins aussi fort, donc à neuf rangées ce `0,4` ne se distingue pas du hasard non plus :
la bonne lecture est que **le piège n'est ni confirmé ni actif**, pas qu'il pousse dans l'autre sens.

**Le piège des covariables.** C'est la moitié qui rend le premier actionnable : une covariable
orthogonale à la variance propre ne peut pas hériter de l'artefact.

| covariable | corrélation à la variance propre ajustée |
|---|---:|
| `refus_faute_de_texture` | **0,1255** |
| `colonnes_lues` | **0,1088** |
| `pas_rendus` | **0,0174** |

La plus forte vaut **0,1255**, et **18** rebrassages sur **19** font au moins aussi fort. ⭐ **Aucune
des trois covariables déclarées ne suit la variance propre**, donc l'artefact du piège nommé ne
pouvait porter aucune d'elles. Le négatif du §5 est un négatif sur la lecture, pas un négatif
masqué par un artefact.

⚠ Aucun de ces deux verdicts ne tient à un seuil. Une première écriture demandait $|\rho| \geq 0{,}6$
— un nombre choisi pour que le réglage du jour passe — et elle a été remplacée par le même rebrassage
que l'épreuve déclarée. La batterie porte une lecture **cherchée exprès** dont la corrélation à la
variance dépasse ce seuil et où le nul fait pourtant aussi fort, sur **cinq** graines. ⚠ Sa valeur
n'est pas publiée ici : un nombre qui sort d'une sonde et non d'une mesure n'est pas publiable.

## 9. Ce que cette tranche ne dit pas

- Elle ne dit **pas** que ce que les rangées ont lu n'a aucun effet. Elle dit que cet effet, s'il
  existe, n'est pas **non additif** au-delà de 4 erreurs d'échantillonnage sur la covariable la mieux
  vue. Le §4 est ce qui empêche la confusion.
- Elle ne dit **pas** que la rangée `198` est ordinaire. Elle dit que son excès n'est **pas payé** par
  un test qui prend le maximum sur neuf rangées.
- Elle ne dit **rien** de la **piste B** de `R4-P60`, le **feuillet**. ⚠ Et la porte a déjà établi
  pourquoi : le treillis du serpentement de `198` n'échantillonne qu'une rangée de loin en loin et
  n'en contient **aucune** des neuf que `214` a lues — les deux plus proches encadrent la bande sans
  en faire partie, et `R4-P60` porte leurs numéros. Mesurer le feuillet sur ces rangées-là demande
  donc une **lecture neuve**, et c'est ce qui sépare les deux pistes par leur coût.
- Elle ne dit rien d'une covariable **par paire** qui ne serait pas dérivée d'une propriété de rangée
  — les coutures communes, par exemple, sont une propriété de la paire elle-même. ⚠ Elles n'entrent
  pas dans la famille déclarée, et les y ajouter après avoir vu ce résultat serait exactement le choix
  que la famille existe pour payer.
- ⚠⚠⚠ Elle ne recommence **pas** `214` : elle **relit** ce que `214` a publié. Si le JSON de `214`
  changeait, celui-ci changerait avec lui, et le lecteur refuse par son nom dès qu'une pièce manque.

## 10. Les sondes, et les bris

La batterie du module compte **65 contrôles**, celle de la figure **21**. Aucune n'a été écrite pour
passer : **treize bris** ont été appliqués un par un au code et **les treize rougissent**, sans
qu'aucun ne tue la batterie ni ne lui fasse perdre un contrôle.

⚠ Les treize bris, et ce que chacun attaque :

| ce qu'on casse | ce que ça ferait si personne ne le voyait |
|---|---|
| le minimum devient le maximum | la famille poserait une autre question sous le même nom |
| une forme inconnue se replie sur l'écart | une forme jamais déclarée entrerait dans la famille |
| l'énergie somme des amplitudes au lieu des carrés | l'agrégat cesserait d'être une dispersion |
| la somme signée n'exige plus ses huit paires | une paire comptée une fois passerait pour une somme non nulle |
| le nul des rangées rebrasse les ÉTIQUETTES | une vérification rigoureusement incapable d'échouer |
| la famille prend le premier membre au lieu du plus fort | le choix parmi six cesserait d'être payé |
| la part non additive ne centre pas la covariable | la limite structurelle serait mal mesurée |
| les jumelles ne regardent qu'une covariable | le nul se rétrécirait en écartant des faces légitimes |
| le piège réécrit son attendu depuis son rendu | une dérivation démentie passerait pour confirmée |
| l'étalon injecte sur un membre fixe, pas le plus visible | la borne parlerait de la projection, pas de la règle |
| le lecteur accepte une rangée qui ne dit pas ce qu'elle a lu | une covariable manquante serait comptée pour zéro |
| les membres plats disparaissent en silence | le maximum porterait sur moins de candidats que déclaré |
| le piège des covariables tranche par un seuil choisi | un nombre choisi pour que le réglage du jour passe |

⚠ Le compte de sondes que chaque bris fait rougir n'est pas publié : il sort d'un harnais de bris
et non d'une mesure, et ce dépôt ne publie pas un nombre qu'un producteur versionné ne rend pas.

⚠⚠⚠ **Quatre de mes propres sondes ne pouvaient pas échouer, et seuls les bris l'ont dit.** Elles
sont corrigées, et chacune valait la peine d'être écrite :

1. **le minimum** n'était distingué que de l'écart, pas **épinglé par sa valeur** — or deux formes
   fausses restent différentes l'une de l'autre. La sonde exige maintenant `lecart(10,4) = 6` et
   `le_minimum(10,4) = 4` ;
2. **l'énergie** passait toutes les sondes en sommant des amplitudes, parce que mes deux matières
   plaçaient le maximum sur la même rangée dans les deux cas. Il a fallu une matière où les deux
   agrégats **nomment des rangées différentes** : la rangée `182` porte huit résidus moyens, la
   rangée `214` en porte un gros. La somme d'amplitudes nomme `182`, l'énergie nomme `214` ;
3. **les jumelles** étaient trouvées même en ne regardant qu'une covariable, parce que ma matière de
   test avait deux rangées identiques sur les trois. Une matière où deux rangées s'accordent sur
   **une seule** covariable sépare les deux versions ;
4. **le piège des covariables** passait avec un seuil codé en dur. Il a fallu **chercher** une
   lecture dont la corrélation à la variance dépasse ce seuil et où le rebrassage fait pourtant
   aussi fort ; elle tient sur **cinq** graines, donc la sonde est déterministe. ⚠ Sa valeur reste
   dans la batterie et n'est pas publiée : un nombre issu d'une sonde n'est pas un nombre mesuré.

⚠⚠ **Et un bris a tué la batterie avant son verdict.** Retirer la garde du lecteur faisait lever une
`TypeError` au milieu de la batterie, qui mourait sans dire quelle sonde avait échoué ni combien
avaient seulement tourné — vue de l'extérieur, une batterie morte ressemble à un défaut de la
batterie et non du code. Corrigé : une sonde accepte désormais un appelable, et une levée **rougit la
sonde en nommant l'exception** au lieu d'interrompre le reste.

La mesure a été **reproduite à l'identique quatre fois**, sur tous les nombres publiés.

## 11. Ce qui reste

> ⚠⚠⚠⚠ **`216` A RETIRÉ SA PRÉMISSE À LA QUESTION QUE CETTE TRANCHE PARCOURAIT.** `R4-P60` demandait
> ce qui rompt l'additivité en tenant la rupture pour établie ; `216` mesure que les résidus de
> `214` portent **2,2325** fois le budget de ses erreurs déclarées, donc qu'il n'est pas établi que
> quoi que ce soit la rompe. ⭐ Ce que cette tranche a mesuré reste vrai et reste utile, y compris
> pour toute reprise : la somme par rangée est identiquement nulle, un ajustement absorbe ce qui agit
> additivement, et la rangée `198` n'est pas payée — `216` explique d'ailleurs pourquoi elle ne
> pouvait pas l'être.

La piste A est **close par la négative**, avec sa borne. Ce qui rompt l'additivité des neuf rangées
n'est ni leur **distance** (`214`), ni ce qu'elles ont **lu** (`215`), et l'excès de la rangée `198`
n'est pas payé.

Il reste `R4-P61` : ⚠ **le feuillet**, qui est la piste B et qui demande une lecture neuve du volume
sur les neuf rangées de `214` ; et la question que le §4 a rendue précise — **existe-t-il seulement
une covariable non additive à trouver**, ou le résidu de `197-198` est-il le bruit d'une paire courte
plutôt qu'une structure ? ⭐ La seconde a une forme bon marché : la paire `197-198` est la plus
**serrée** du treillis, et une matière où l'on relit deux rangées voisines plusieurs fois dirait si
un désaccord de cette taille se reproduit ou s'il se déplace.
