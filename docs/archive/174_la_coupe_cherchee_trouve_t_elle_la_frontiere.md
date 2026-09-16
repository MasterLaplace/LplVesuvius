# 174 — La coupe cherchée trouve-t-elle la frontière ?

> ✗ **NON. ELLE TROUVE LE DÉSÉQUILIBRE.** Sur une marche de **109** couches dont la frontière est
> **construite** à la couche **37**, la recette de `173` coupe à la couche **8** — écart **29** — et
> rend pourtant **90,0°**. Les huit premières couches sont pures, donc leur moyenne est franche ;
> tout le reste est un mélange presque équilibré dont la résultante vaut **0,089**, c'est-à-dire une
> moyenne **sans direction** mais parfaitement définie. L'écart à une direction arbitraire est
> arbitrairement grand, et il vaut souvent un quart de tour.
>
> ⚠⚠⚠ **ET LE CONTRÔLE PAR PERMUTATION NE LA RATTRAPE PAS.** Mélanger les couches conserve le
> multiensemble des angles, donc une part pure et un mélange restent trouvables : l'écart réel vaut
> **90,0°** et le maximum de **19** permutations vaut **90,0°** aussi.
>
> ⭐⭐⭐⭐ **LA RÉPARATION A DEUX PIÈCES, ET AUCUNE N'EST UN SEUIL.** Une moyenne sans résultante
> n'est pas une direction — la borne se **dérive**, `n` directions tirées au hasard rendent de
> l'ordre de **1/√n** — et la coupe s'obtient en **ajustant deux segments**, pas en maximisant
> l'écart. Elle tombe alors sur **37 pour 37**, résultantes **1,0** et **1,0**, part atteinte
> **1,0** contre **0,321** au mélange. Du bruit est **refusé**.
>
> ⭐⭐⭐⭐ **ET LE DOUZE SUR DOUZE DE `173` ÉTAIT JUSTE ET VIDE.** Relue sur la même fixture, sa
> recette est bien fiable à six longueurs — mais la liste « fiables **et sur la frontière** » est
> **VIDE**, et la recette réparée n'est fiable qu'à **0,75** feuille.
>
> ⚠⚠ **DONC ON NE POSE TOUJOURS RIEN SUR LE VRAI ROULEAU.** On ne pointe pas un instrument qui
> n'est fiable qu'à une longueur sur huit. `R4-P30` reste ouverte, resserrée.

## 1. Pourquoi ce fichier, et c'est le contrôle qui l'a déclenché

`173` conclut qu'une coupe **cherchée** lit la bascule là où la coupe aveugle échoue, et `R4-P30`
demande de la poser sur le vrai rouleau — en exigeant qu'elle porte **son propre contrôle**, parce
que *maximiser un écart trouve toujours quelque chose*. Cette tranche devait faire les deux. Le
contrôle a réfuté l'instrument avant qu'il n'atteigne la matière.

⚠ Le réseau répond et la donnée est là : le volume de surface à 2,4 µm rend un chunk en une
seconde, et sa profondeur **est** de 109 couches — la fenêtre de la campagne n'était donc pas un
choix. Rien de cela n'a été mesuré : on ne pointe pas un instrument réfuté sur le rouleau.

## 2. ⭐⭐⭐⭐ Où chaque recette coupe

La marche de référence a **109** couches et sa frontière est **construite** à la couche **37**.
Comparer une coupe à une frontière connue ne demande aucun seuil : on compare deux entiers.

| recette | coupe | écart | bascule | témoin |
|---|---:|---:|---:|---:|
| **aveugle** — celle de la campagne | 54 | **17** | 90,0° | 90,0° |
| **meilleure** — celle de `173` | **8** | **29** | **90,0°** | 0,0° |
| **ajustée** — réparée | **37** | **0** ★ | 90,0° | 0,0° |

⚠⚠⚠ **La fixture a dû être corrigée avant de servir.** Une première version posait la frontière à la
couche **54**, qui est exactement là où la coupe **aveugle** coupe une fenêtre de 109 couches : la
fixture donnait alors raison à la recette qu'elle devait mettre à l'épreuve, et la ligne « aveugle »
se lisait comme une réussite. Une fixture complaisante est une vérification incapable d'échouer ; la
batterie exige désormais que la frontière soit ailleurs que sous la coupe aveugle.

![La coupe de `173` tombe à huit quand la frontière est à trente-sept, et rend quand même un quart de tour](../images/174_la_coupe_cherchee_trouve_t_elle_la_frontiere.png)

## 3. ⚠⚠⚠ Ce que le mélange laisse

Mélanger les couches détruit l'ordre en profondeur et **ne touche à rien d'autre** : chaque couche
garde son angle et sa cohérence, donc la liberté de choisir une coupe est exactement la même.

| | réel | mélanges (max sur 19) | dépasse toutes |
|---|---:|---:|---|
| l'**écart** maximisé (`173`) | **90,0°** | **90,0°** | ✗ |
| l'**ajustement** (réparé) | **1,0** | **0,321** | ★ |

⭐ L'écart survit au mélange, donc **il ne mesure pas l'ordre en profondeur**. L'ajustement n'y
survit pas : sans ordre, aucune coupe ne laisse deux parts dirigées.

## 4. La réparation, pièce par pièce

**(1) Une moyenne sans résultante n'est pas une direction.** C'est l'avertissement que
`fiber_orientation` porte déjà couche par couche — *« un angle calculé sur une zone sans texture est
un angle aléatoire mais bien défini »* — posé un étage plus haut, sur la moyenne d'une **tranche**.
⚠⚠ La borne se **dérive** : `n` directions tirées au hasard rendent une résultante de l'ordre de
**1/√n**, donc une tranche qui n'y arrive pas n'a rien à dire. Deux directions perpendiculaires en
nombre égal s'annulent **exactement** en angle double, et c'est par ce trou que `173` est passée.

**(2) La coupe s'obtient en ajustant deux segments.** On retient la coupe qui rend la résultante
**totale** la plus grande — celle qui laisse les deux parts aussi dirigées que possible — au lieu de
celle qui maximise leur écart. Sur une marche, elle tombe sur la frontière.

**(3) Le témoin se lit des DEUX côtés.** ⚠⚠⚠ Et c'est une **sonde passée au vert** qui l'a exigé :
neutraliser le second côté laissait la batterie verte, parce que sur une marche et sur une dérive
franche les deux côtés disent la même chose. Sur une **marche suivie d'une dérive**, la première
part est homogène — un témoin d'un seul côté y rend **0,0°** et déclare une marche propre là où
celui des deux côtés rend **60,845°**.

## 5. ⚠⚠ La limite, dite plutôt que tue

| matière | coupe | bascule | témoin | part atteinte |
|---|---:|---:|---:|---:|
| **marche** | 37 | 90,0° | **0,0°** | **1,0** |
| **dérive** | 54 | 85,787° | **43,287°** | 0,666 |
| **marche puis dérive** | 88 | 35,562° | 40,669° | 0,618 |
| **bruit** | — | — | — | **refusée** |

⚠⚠ **Une dérive n'est PAS séparée d'une marche par un verdict.** Ce qui les distingue est le témoin,
un nombre à lire — **zéro** sur une marche, **43,287°** sur une dérive — et le prétendre un verdict
serait choisir un seuil. Il faut le dire plutôt que le taire.

## 6. ⭐⭐⭐⭐ La relecture de `173`

Même fixture, mêmes **12** décalages par longueur, avec une **troisième** condition : la coupe doit
tomber sur la **frontière**, que la fixture connaît.

| longueur | aveugle | meilleure (`173`) | ajustée | **sur la frontière** |
|---:|---|---|---|---|
| 0,25 f | 4/12 | 7/12 | 3/12 | **0/12** |
| 0,5 | 9/12 | 10/12 | 7/12 | 3/12 |
| **0,75** | 8/12 | **12/12** | **12/12** | 6/12 |
| 1 | 8/12 | **12/12** | 10/12 | 4/12 |
| 1,25 | 6/12 | **12/12** | 4/12 | 1/12 |
| 1,5 | 4/12 | **12/12** | 2/12 | **0/12** |
| 2 | 0/12 | **12/12** | 11/12 | 4/12 |
| 3 | 8/12 | **12/12** | 6/12 | 3/12 |

⭐ `173` publie **six** longueurs « fiables » et la relecture les reproduit exactement. Mais
**aucune** ne met la coupe sur la frontière à tous les décalages : la liste « fiables **et** sur la
frontière » est **vide**.

⚠⚠ **Ce qui de `173` reste debout** : la coupe **aveugle** n'atteint jamais douze sur douze, et cela
ne dépend d'aucune maximisation. Ce qui est **borné** est tout ce que `173` a conclu **avec** la
coupe cherchée — donc `R4-F177` et `R4-F178` passent au statut *borné*.

## 7. Les sondes

Cinq, toutes vérifiées **en cassant le code** : la règle de la résultante retirée (**4** échecs) ;
la borne abaissée à zéro (**3**) ; l'ajustement qui maximise l'**écart** au lieu de la résultante
totale (**4**) ; le témoin d'un seul côté ; et le libellé ramené **sur** le trait pointillé.

⚠⚠⚠ **La quatrième est passée au vert la première fois** — deuxième tranche de suite. Le témoin des
deux côtés n'était asserté par rien, parce que les matières disponibles disaient la même chose des
deux côtés. La matière qui manquait est une **marche suivie d'une dérive**, et elle fait tomber la
sonde.

⚠⚠ **Et la figure a payé une classe de défaut déjà connue sous une autre forme** : un trait
pointillé traversait le libellé d'une ligne. `textes_qui_se_recouvrent` ne voit que du texte contre
du texte — c'est la leçon de la barre qui débordait dans `167`. Chaque trait est désormais
**enregistré avec son étendue**, et un contrôle exige qu'aucun ne traverse un texte.

## 8. Ce que cette tranche laisse

- ⚠⚠⚠ **`R4-P30` reste ouverte et se resserre** : l'instrument qu'elle annonçait prêt est réfuté,
  la réparation est livrée, et elle n'est fiable qu'à **une longueur sur huit**. Ce qui manque est
  de savoir pourquoi l'ajustement décroche aux autres.
- ⚠⚠ **Rien n'a été posé sur le vrai rouleau**, délibérément. Le réseau répond, la donnée est là,
  et c'est précisément pour ça qu'il fallait le contrôle d'abord.
- ⚠ **`173` n'est pas rétractée, elle est bornée** : sa moitié qui ne dépend d'aucune maximisation
  tient.
- ⚠ **Ce qui reste ouvert ailleurs est intact** : `167` mesure que la pince échoue à réparer
  **0,309859** des contradictions qu'elle rencontre, et rien ne dit de quoi elles sont faites.

## 9. Reproduire

```
uv run python src/nappe/la_coupe_cherchee_trouve_t_elle_la_frontiere.py --verifier
uv run python src/nappe/la_coupe_cherchee_trouve_t_elle_la_frontiere.py \
    --json docs/mesures/la_coupe_cherchee_trouve_t_elle_la_frontiere.json
uv run python src/figures/figure_la_coupe_cherchee_trouve_t_elle_la_frontiere.py --verifier
```
