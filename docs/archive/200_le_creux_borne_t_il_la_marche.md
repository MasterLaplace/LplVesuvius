# `200` — Le creux de cohérence borne-t-il la marche ?

*Le repère absolu existe et se lit presque partout — mais il dit qu'il y a une frontière, jamais laquelle.*

![Le creux borne-t-il la marche ?](../images/200_le_creux_borne_t_il_la_marche.png)

## 0. Pourquoi cette tranche

`199` a établi que les pas d'une couture à l'autre **se compensent** — aucun biais à retirer — et
que la marche au hasard qui en résulte perd pourtant un **demi-feuillet en seize millimètres**. Une
correction **différentielle** ne peut donc rien : de proche en proche, elle n'a rien à corriger
localement. Il faut quelque chose qui dise, en **chaque** chunk et **sans regarder ses voisins**, où
est le feuillet.

⭐⭐⭐⭐ **Or `180` l'a déjà mesuré** : la cohérence du tenseur de structure **creuse** à une frontière
de pli, et vingt-sept chunks sur vingt-sept y dépassent toutes leurs permutations. C'est un repère
**absolu** — il ne se déduit d'aucun voisin — et rien dans la chaîne ne l'avait encore utilisé pour
**borner** une marche.

## 1. La ligne — la MÊME que `199`

| | |
|---|---:|
| segment | `20230702185753` |
| rangée **médiane** | **198** |
| chunks demandés | **285 colonnes** |
| chunks lus | **251 colonnes** |
| chunks sans surface au dépôt | **28 colonnes** |
| chunks écartés par le filtre du producteur | **6 colonnes** |
| cube | **109 couches** · plancher de cohérence **0,15** |

⚠⚠ **Le filtre est celui de `14` et de `176`, relu et non choisi** : un chunk est retenu quand au
moins un quart de ses couches dépasse le plancher de cohérence. Un filtre plus large ferait entrer
des chunks que le producteur n'a jamais lus.

## 2. Le repère existe, et il est lisible presque partout

★ **245 repères lisibles sur 251 chunks lus.**

⭐ C'était la **première moitié** de ce que `R4-P48` demandait — un repère qui manque dans un chunk
sur deux ne bornerait rien — **et elle tient**.

## 3. Mais sa couche est presque aussi dispersée qu'un tirage au hasard

| | |
|---|---:|
| couche médiane du creux | la **62e couche** |
| écart-type observé | **29,1153 voxels** (**0,403912** pli) |
| écart-type si la couche était **tirée au hasard** dans 109 couches | **31,4656 voxels** |
| **rapport à l'uniforme** | **0,9253** |
| excursion de la trace | **100 voxels**, soit **1,387283** pli |

⚠⚠⚠ **Le repère porte la PRÉSENCE d'une frontière, essentiellement pas sa POSITION.** Sans la borne
de l'uniforme, « écart-type 29,1153 voxels » ne se lirait pas : une couche tirée au hasard dans `n`
couches donne `n/√12`, et la comparaison dit d'un seul coup ce que le repère contient.

## 4. Et il ne borne pas la marche

| | |
|---|---:|
| excursion **absolue** (ce fichier) | **1,387283** pli |
| excursion **différentielle** (`199`) | **1,304046** pli |
| rapport | **1,0638** |

✗ **Le creux ne borne pas la marche.** Il fait même **légèrement pire** que le recalage de proche en
proche.

⚠⚠ **Ce qui est comparé est l'EXCURSION, pas le pas** : un repère absolu n'a pas de « pas » au sens
de `199`, chaque point étant indépendant des autres. La seule quantité qui se compare entre les deux
lectures est jusqu'où la surface s'éloigne de son départ. Et les deux nombres viennent de leurs
producteurs respectifs — celui de `199` est **relu**, jamais recalculé.

## 5. La raison est mesurée, pas supposée

| | |
|---|---:|
| sauts de plus d'un **demi-pli** | **92** |
| sur des paires voisines | **244** |
| soit une part de | **0,377049** |
| pas quadratique de la trace | **38,0986 voxels** |

⚠⚠⚠ **Un creux désigne UNE frontière, pas LAQUELLE.** Plus d'un tiers des paires voisines se calent
sur deux frontières séparées d'un pli. Ces sauts sont **comptés, jamais lissés** : les replier modulo
un pli inventerait une continuité que la mesure ne voit pas.

⭐⭐⭐⭐ **Ce qui manque n'est donc pas un repère EN PROFONDEUR — il est là.** C'est de savoir
**compter les plis** : un **ordinal**, pas une position.

## 6. L'étalon

| bruit posé sur la courbe | part des **20 réplicats** où la frontière est retrouvée |
|---|---:|
| **0,02** | **1** |
| **0,05** | **1** |
| **0,1** | **1** |
| **0,2** | **0,85** |

| | |
|---|---:|
| bruit **tenu** à tous les réplicats | **0,02 de bruit** |
| taux de faux sur une courbe **sans** frontière | **0,05 de faux** |
| garantie | **0,05 garantis** |

★ **L'étalon sépare ses deux faces**, et les **deux** sont mesurées sur réplicats — la leçon de
`198` et `199`.

## 7. Les sondes, et les onze bris

Le module rend **39** contrôles, la figure **32**. Onze bris ont été posés et **les onze ont viré au
rouge**. Mais un vrai défaut a été trouvé **avant** eux, par la mesure elle-même :

⚠⚠⚠ **La profondeur du cube était lue dans une clef que le lecteur ne porte pas**, et la mesure a
rendu **zéro couche** — donc une borne de l'uniforme indéfinie. ⚠⚠ **Mes sondes ne l'avaient pas vu
parce que leurs fixtures fournissaient le champ elles-mêmes** : elles testaient la fixture, pas le
lecteur. Réparé en lisant la longueur de la **courbe** elle-même, qui ne peut pas manquer, et en
ajoutant une sonde qui porte sur ce que `le_repere_dun_chunk` rend vraiment.

## 8. Ce que cette tranche ne dit pas

⚠ Elle porte sur **une** rangée d'**un** segment, la médiane, jamais choisie — la même que `199`,
pour que la comparaison en soit une. ⚠⚠ Et elle ne dit pas que le creux est inutile : elle dit qu'il
est **défini modulo un pli**, ce qui est une information réelle et insuffisante **seule**.

## 9. La porte

`R4-P48` est **répondue**, et `R4-P49` **s'ouvre**.
