# 95 — La surface humaine est MIEUX posée sur la feuille là où le transfert casse

> ⛔⛔⛔ **Deuxième observable, deuxième échec, et c'est le résultat.** `94` a tué le froissement
> parce qu'il est une propriété du **maillage**. Restait une observable de la **matière** : l'écart
> entre la surface publiée et le ruban de papyrus qu'elle suit. Mesuré à 2,4 µm sur les 28 bandes
> humaines de `PHercParis4` : la dispersion vaut **20,0 µm au cœur et 13,85 au bord**, donc la
> surface est **mieux posée** là où `92` mesure une continuité brisée (×31) et `93` des spires
> désalignées (×3,67 au même tiers).

![la surface et la feuille par rayon](../images/95_la_surface_et_la_feuille_par_rayon.png)

## 1. Pourquoi cette observable et pas une autre

`94` a laissé une contrainte : tout signal de confiance doit être **vérifié à travers les rayons**.
Et il a laissé une explication — au bord, les maillages humains sont plus **lisses** parce qu'ils
ont **enjambé** ce qu'ils ne pouvaient pas suivre. Une observable du maillage est donc disqualifiée
par construction ; il fallait une observable de la **matière**.

Le dépôt en avait déjà une : `la_surface_et_la_feuille` mesure l'écart entre la spire publiée et le
ruban qu'elle suit (30,8 µm d'écart-type sur `PHerc0172`). ⭐ Ce qui est neuf ici est **l'axe** :
cette mesure ne couvre `PHercParis4` que par **une seule bande**, `w010-027`, la plus interne.

## 2. ⭐⭐⭐ Ce qui a rendu les 28 bandes abordables

La mesure existante passe par des **couches rendues**, assez cher pour n'en faire qu'une bande.
Deux faits changent le coût :

- les chunks du dépôt sont écrits **sans compression**, donc l'octet d'un voxel est à un décalage
  **calculable** et une requête HTTP `Range` suffit — 20,7 Go de volume lus sans rien rapatrier ;
- la matrice `45,532 µm → 2,4 µm` est **publiée** dans `data/metadata.min.json`.

⚠⚠ **Et le volume fin n'est pas un luxe, c'est une nécessité mesurée.** À 45,532 µm, un demi-écart
inter-feuilles vaut **deux voxels** : on ne peut pas y mesurer un décalage de vingt micromètres, et
le faire publierait une **limite de grille** comme une limite de matière. La batterie l'assère.

## 3. ⛔⛔⛔ Le résultat

| tiers | dispersion | contraste | part au remplissage | continuité |
|---|---:|---:|---:|---:|
| cœur (9 bandes) | **20,0 µm** | 107,5 | 0,011 | ×1,7 |
| milieu (9) | 17,1 µm | 108,5 | 0,068 | ×5,9 |
| bord (10) | **13,85 µm** | 114,5 | 0,167 | **×31,0** |

Corrélations : **−0,702** avec le rayon, **−0,694** avec la rupture de continuité.

## 4. ⭐⭐ Le confondant, traité par trois chemins qui doivent s'accorder

Le volume est **masqué** : tout ce qui est hors du rouleau vaut zéro, et le bord du rouleau est
précisément là où l'on s'en approche. La part au remplissage monte à **+0,800** avec le rayon.
Sans la retirer, *« la surface est mieux posée au bord »* et *« le volume s'arrête au bord »*
seraient **la même observation**.

| chemin | dispersion / rayon | dispersion / continuité |
|---|---:|---:|
| brut | −0,702 | −0,694 |
| corrélation **partielle**, masque retiré | **−0,550** | **−0,533** |
| en **jetant** les bandes rongées (16 bandes) | −0,658 | −0,434 |

⭐ **Retirer un confondant par une formule et le retirer en jetant les cas concernés sont deux
gestes différents.** S'ils ne s'accordent pas, c'est la formule qui a tort — elle suppose une
relation linéaire que des bandes à 0,2 et 0,4 de remplissage ne respectent pas. Ici les trois
s'accordent sur le signe et l'ordre de grandeur.

## 5. ⭐⭐⭐ Le seuil n'est pas réglé, et c'est vérifiable plutôt qu'affirmé

| remplissage toléré | bandes | dispersion / rayon |
|---:|---:|---:|
| 5 % | 13 | −0,630 |
| 10 % | 16 | −0,658 |
| 15 % | 20 | −0,646 |
| 20 % | 25 | −0,738 |
| 30 % | 27 | −0,753 |

Le verdict tient **partout**, donc il ne vient pas du seuil. Un verdict qui ne tiendrait qu'à une
valeur serait un nombre choisi pour que le résultat passe — la faute nº 1 de ce dépôt.

## 6. ⚠⚠ Le contraste, lui, n'a aucune relation stable au rayon

**−0,276** brut, **+0,356** une fois le masque retiré, et le **signe change** selon le seuil du
balayage. Il n'y a donc rien à en tirer.

⚠⚠⚠ **Et c'est une erreur à moi, gardée.** Ma sonde exploratoire prenait **trois** bandes — cœur,
milieu, `w128-129` — et voyait le contraste tomber de **119 à 11**. Or `w128-129` est l'une des
**deux seules** bandes dont le contraste s'effondre, et celle dont le remplissage est le plus fort
(0,385).

> **Un bord se compte sur le corpus entier, pas sur les bandes qu'on a sondées.**

C'est exactement la faute que `93` avait déjà payée en comparant la bande 0 à la bande 7. Elle
s'est réécrite ici sous une forme différente, avec la mesure complète pour la corriger.

## 7. ⚠⚠ La dispersion ne se lit jamais sans son contraste

Sans relief, le centre de masse d'un profil de **bruit** se pose au **milieu** de la fenêtre, donc
il disperse peu. Lue seule, la colonne « dispersion » dirait *« la surface est la mieux placée au
bord »* pour une bande où il n'y a rien à mesurer. Le contraste est donc publié **à côté**, et la
batterie fixture le piège : une cellule plate dans une bande contrastée se centre exactement au
milieu, et son contraste vaut zéro.

## 8. ⚠⚠⚠ Un résultat qui bougeait entre deux exécutions du même calcul

Les deux premiers runs ont donné des médianes par tiers **différentes** — bord 13,85 puis 13,1 µm —
alors que toutes les valeurs par bande étaient identiques. Cause : la bande `w110-112` avait **65
cellules au lieu de 90**, vingt-cinq perdues par des coupures réseau passagères, **en silence**.

> **Un nombre publié dont la valeur dépend de l'humeur du réseau n'est pas un résultat.**

Deux remèdes, et il faut les **deux** : les lectures sont **réessayées** (trois fois, sur les
pannes réseau seulement — un code HTTP est une réponse, pas une panne, et un 404 est même une
valeur légitime du volume), ce qui rend la perte rare ; et le compte de cellules perdues est
**publié** par bande et en tête du rapport, ce qui la rend visible. Un réessai qui échoue quand
même laisserait sinon exactement le même trou muet.

## 9. ⭐⭐⭐ Ce que ça contraint pour le remplaçant de l'humain

**Deux observables locales indépendantes** — le pli du maillage (`94`) et la pose sur la matière
(ici) — disent toutes deux **« plus propre »** exactement là où le transfert échoue. Ce n'est plus
une coïncidence, c'est un motif, et sa raison est la même dans les deux cas :

> ⭐⭐⭐ **Au bord, l'humain qui ne peut pas suivre la vraie feuille en trace une autre,
> proprement. Le maillage épouse très bien UNE feuille — simplement pas la bonne.**

Donc ce qui échoue au bord n'est pas la **qualité locale** de la surface mais l'**identité** de la
feuille suivie. Une observable locale, par construction, ne peut pas la voir : elle mesure à quel
point on est bien posé sur ce qu'on suit, jamais si c'est ce qu'il fallait suivre.

⛔ **Conséquence directe** : un signal de confiance par cellule bâti sur l'une ou l'autre de ces
deux familles classera l'abandon comme une réussite. Le signal qu'il faut est **topologique** —
il doit porter sur l'identité de la feuille, donc être **global**, et c'est là qu'il faut chercher.

## Reproduire

```
uv run python src/commun/voxel_distant.py --verifier
uv run python src/commun/transformations_de_volume.py --verifier
uv run python src/nappe/la_surface_et_la_feuille_par_rayon.py --verifier
uv run python src/nappe/la_surface_et_la_feuille_par_rayon.py \
    --json docs/mesures/la_surface_et_la_feuille_par_rayon.json
uv run python src/figures/figure_la_surface_et_la_feuille_par_rayon.py --verifier
```
