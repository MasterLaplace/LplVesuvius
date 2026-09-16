# 169 — La fixture penche-t-elle du même côté que le rouleau ?

> ⭐⭐⭐⭐ **OUI, AUX DEUX CAPS — ET ELLE SUIT LE RENVERSEMENT.** Le rouleau ne penche pas du même côté
> selon que le marcheur porte un cap ou non : **sans cap** il penche **azimutalement** (**0,348**
> d'axial contre **0,405**), **avec cap** il penche **axialement** (**0,334** contre **0,193**). La
> fixture calibrée fait **la même chose aux deux** : **0,318** contre **0,34** sans cap, **0,19**
> contre **0,117** avec.
>
> ⭐⭐⭐ **ET SON GLISSEMENT AXIAL COLLE AUX DEUX** : **65,8 µm** par pas contre **57,5** sans cap,
> **44,7 µm** contre **43,2** avec.
>
> ✗ **CE QU'ELLE NE REPRODUIT PAS EST LE SUIVI, ET À AUCUN DES DEUX CAPS.** Cohérence **0,332**
> contre **0,719** sans cap, **0,696** contre **0,925** avec. Elle glisse autant, dans le bon sens,
> et pas toujours du même côté.
>
> ⭐⭐⭐⭐ **C'EST `134` UNE SECONDE FOIS, PAR UN AUTRE CHEMIN.** `134` mesure qu'un froissement propre
> à chaque feuille fait virer **autant** que le rouleau mais **alterne deux fois plus** — rectitude
> **0,9642** contre **0,8563**. Cinq tranches plus loin, la même forme : **les grandeurs y sont, la
> persistance non.** Ce qu'aucune fixture du dépôt ne fabrique est un penchant **suivi**.
>
> ⭐ **LE CONTRÔLE TIENT, ET IL EN PORTE DEUX.** Ni la spirale nue ni l'**écrasement seul** ne
> glissent le long de l'axe : **0,0 µm** dans les deux cas. Le glissement axial ne vient donc pas de
> l'aplatissement, il vient du **froissement**, et il croît avec lui — **19,6**, **24,6**,
> **50,5 µm**.
>
> ⚠⚠⚠ **ET LA PREMIÈRE VERSION DE CETTE TRANCHE A PUBLIÉ LE CONTRAIRE, PARCE QU'ELLE AGRÉGEAIT SUR
> LE CAP.** Le §6 raconte comment, et pourquoi la mesure portait déjà la réponse.

## 1. Pourquoi ce fichier, et un fait établi le désignait

`R4-F87` établit que l'écrasement mesuré **plus** un froissement approche le rouleau à **5,5 %** sur
**trois** grandeurs : le **rapport** des axes, le **penchant** et la **cohérence**. C'est cette
matière-là que la chaîne `161`–`168` emploie.

⭐⭐⭐⭐ **La direction du penchant n'est pas dans ces trois grandeurs.** Or `R4-F79` mesure sur le vrai
rouleau que le penchant est plus **axial** qu'azimutal — **0,334** contre **0,193** — et que le
marcheur glisse de **43,2 µm** le long de la longueur du rouleau à chaque pas. Personne n'avait
vérifié que la fixture penche du même côté, et la mesure existait déjà : `penchant()`, la fonction
qui a produit `R4-F79`, publie exactement ces deux parts.

## 2. Comment la comparaison est faite sans être truquée

⚠⚠ **Le même instrument et le même marcheur, deux matières.** La décomposition est `penchant()`,
celle de `R4-F79`, et le marcheur est `marcher`, celui de `100` — jamais `suivre`. Employer un autre
marcheur comparerait deux instruments en croyant comparer deux matières.

⚠⚠⚠ **Et CAP PAR CAP, jamais sur leur mélange.** `R4-F79` publie **deux** courses du rouleau, et
elles ne disent pas la même chose : le cap **renverse** le sens du penchant. Comparer une fixture à
une seule de ces courses, ou à un mélange des deux, compare deux choses différentes.

⚠⚠ **Les chiffres du vrai rouleau sont RELUS, jamais recalculés.** Ils sont publiés et leur course
coûte des heures ; le module les relit dans la mesure stockée et **refuse de conclure** si elle est
absente.

⚠ **Deux questions, deux énoncés exacts, aucun seuil.** Le **côté** : la part axiale dépasse-t-elle
l'azimutale ? — et ce qui doit s'accorder est la **réponse**, pas la valeur. Le **suivi** : la
cohérence, c'est-à-dire le déplacement tangentiel **net** divisé par le chemin tangentiel
**parcouru**.

## 3. ⭐⭐⭐⭐ La réponse, cap par cap

![La fixture suit le renversement du rouleau d'un cap à l'autre, et sa cohérence reste sous la sienne aux deux](../images/169_la_fixture_penche_t_elle_du_meme_cote.png)

| cap | | part axiale | part azimutale | penche | glissement | cohérence |
|---|---|---|---|---|---|---|
| **0,0** | la fixture | 0,318 | **0,34** | azimutalement | 65,8 µm | **0,332** |
| **0,0** | le rouleau | 0,348 | **0,405** | azimutalement | 57,5 µm | 0,719 |
| **0,75** | la fixture | **0,19** | 0,117 | axialement | 44,7 µm | **0,696** |
| **0,75** | le rouleau | **0,334** | 0,193 | axialement | 43,2 µm | 0,925 |

⭐⭐⭐⭐ **Le côté s'accorde aux deux, et c'est plus qu'un accord : c'est un SUIVI de renversement.**
Une fixture qui pencherait d'un côté par construction tomberait juste à un cap et raterait l'autre.
Celle-ci change de sens quand le rouleau change de sens.

✗ **Le suivi ne s'accorde à aucun des deux**, et toujours dans la même direction : la fixture est
**moins** cohérente que le rouleau, de **0,387** sans cap et de **0,229** avec.

## 4. ⭐⭐⭐ Le glissement axial vient du froissement, pas de l'écrasement

C'est le second contrôle, et il est exact : l'**écrasement seul** rend **0,0 µm** de glissement
axial, exactement comme la spirale nue. Aplatir une spirale ne fait donc pas glisser le marcheur le
long de l'axe — c'est le froissement qui le fait, et la quantité croît avec son amplitude.

| matière | marches | axial | azimutal | glissement axial | cohérence |
|---|---|---|---|---|---|
| spirale nue | 6 | 0,0 | 0,002 | **0,0 µm** | 1,0 |
| spirale écrasée | 6 | 0,0 | 0,009 | **0,0 µm** | 1,0 |
| spirale froissée 42.4 µm | 6 | 0,117 | 0,084 | 19,6 µm | 0,627 |
| spirale écrasée et froissée 42.4 µm | 6 | 0,116 | 0,126 | 24,6 µm | 0,659 |
| spirale écrasée et froissée 100 µm | 6 | 0,222 | 0,235 | **50,5 µm** | 0,558 |

⚠⚠⚠ **Ce tableau MÊLE LES DEUX CAPS**, et le cap renverse le sens : la ligne de la matière calibrée
n'est donc **pas** un verdict, c'est un mélange. Il est publié pour ce qu'il montre — que le
glissement naît du froissement et croît avec lui, ce qui est vrai à tout cap — et le verdict se lit
au §3.

⚠ Sur la spirale nue et sur l'écrasée les deux parts valent quasiment zéro : c'est pourquoi le
contrôle exige une **absence de glissement** et non un sens.

## 5. ⭐⭐⭐⭐ Ce que cela dit, et c'est `134` une seconde fois

`134` a mesuré qu'un froissement propre à chaque feuille fait virer le marcheur **autant** que le
rouleau — **14,72°** par pas — mais que les virages **alternent deux fois plus** (cosinus
**−0,4624** contre **−0,2061**) et que la rectitude reste à **0,9642** contre **0,8563**.

⭐ Cinq tranches plus loin, par un instrument différent et sur une autre quantité, la même forme :
la fixture **glisse autant** et **ne suit pas**. Deux mesures indépendantes disent que ce qui manque
aux fixtures du dépôt n'est pas une **grandeur** mais une **persistance**.

⚠ Ce que cela ne borne PAS : la chaîne `161`–`168` n'exploite pas la persistance du penchant, elle
exploite le fait qu'une pose se contredise — et cette propriété-là est bien sur cette matière.

## 6. ⚠⚠⚠ Ce que la première version de cette tranche a publié de faux

Elle a conclu que la fixture penche **azimutalement** là où le rouleau penche **axialement**, et que
le côté ne s'accorde **pas**. C'était faux, et l'erreur est d'une seule sorte : **le verdict
agrégeait les deux caps**.

- La fixture y était comparée à la **seule** course capée du rouleau — `courses[0]` — pendant que son
  propre chiffre venait d'une médiane sur **cap 0 et cap 0,75 ensemble**.
- Or le cap **renverse** le sens : à cap 0 la fixture rend 0,318 contre 0,34, à cap 0,75 **0,19
  contre 0,117**. La médiane des six cases tombe à 0,222 contre 0,235, qui n'est le chiffre
  d'aucun des deux régimes.
- Le compte « 3 axial contre 3 azimutal » que j'avais lu comme *« rien de systématique »* était en
  fait **1 sur 3 à cap 0 et 2 sur 3 à cap 0,75** : deux régimes, pas un partage.

⚠⚠ **La mesure portait déjà la réponse, et je suis passé à côté.** Le module publiait un tableau
`par_cap`, la figure le dessinait, et il annonçait **0,698** de cohérence à cap 0 contre **0,911** à
cap 0,75 — un écart qui criait que le cap n'est pas un détail d'agrégation. C'est **moyenner sur
l'axe où vit la différence**, le péché que ce dépôt nomme depuis `161`, commis sur un axe que
j'avais moi-même mesuré et affiché.

⭐ Ce qui l'a attrapé : en cherchant une cause au désaccord entre les **deux** cohérences publiées
sur la même matière — **0,942** dans `R4-F87` et **0,558** ici — j'ai trouvé que les définitions sont
**identiques**, donc que la différence devait venir du **protocole**. Elle en venait.

⚠ Le module **refuse désormais** une comparaison sans verdict cap par cap, et la figure aussi.

## 7. Les sondes

⚠ Six sondes, toutes vérifiées **en cassant le code** : le nombre du **rouleau** affiché sous
l'étiquette **fixture** ; l'énoncé qui **moyenne** au lieu de compter ; le côté et le suivi
**confondus** ; conclure **sans** la course du rouleau ; un accord obtenu à **un seul** cap ; et une
comparaison qui **mêle** les caps.

⚠⚠⚠ **Et un défaut de ce module a été trouvé par une sonde, pas par une relecture.** `afficher`
imprimait la part du **rouleau** sous l'étiquette **fixture**, et la batterie passait **des deux
côtés** — aucun contrôle n'attrape un nombre juste sous un mauvais nom. Ce qui l'attrape n'est pas de
relire : c'est de changer la valeur de la fixture et d'**exiger que la sortie change**.

## 8. Ce que cette tranche laisse

- **`R4-P27` se resserre**, et pas là où je l'avais d'abord écrit : ce que les fixtures ne savent pas
  fabriquer n'est ni la grandeur du penchant ni son sens — c'est sa **persistance**.
- ⚠ **`134` (le vrillage) se rouvre avec une raison mesurée deux fois** : le rouleau penche de façon
  **suivie**, et aucune fixture du dépôt ne fabrique ce suivi.
- ⚠ **Ce qui reste ouvert ailleurs est intact** : `167` mesure que la pince échoue à réparer
  **0,309859** des contradictions qu'elle rencontre, et rien ne dit de quoi elles sont faites.

## 9. Reproduire

```
uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py --verifier
uv run python src/nappe/la_fixture_penche_t_elle_du_meme_cote.py \
    --json docs/mesures/la_fixture_penche_t_elle_du_meme_cote.json
uv run python src/figures/figure_la_fixture_penche_t_elle_du_meme_cote.py --verifier
```
