# 103 — Le cube lu moins cher : l'économie est réfutée par le corpus, et par ma propre sonde

> ⛔⛔⛔ **Aucune économie ne passe : le cube se lit au voxel près.** Échantillonner un voxel sur
> deux coûterait **1,72 fois moins** — mais **7,3 %** des cellules s'en écartent de plus de dix
> degrés, et comme `102` **enchaîne** les pas, cela abîme **36,5 %** des marches de six pas.
>
> ⚠⚠⚠ **Et c'est ma propre sonde qui était tombée dans le piège** : sur **2** bandes j'avais mesuré
> **0 %** et j'allais l'adopter ; sur les **28**, c'est **7,3 %**. *Un bord se compte sur le corpus
> entier, pas sur les bandes qu'on a sondées.*

![le cube lu moins cher](images/103_le_cube_lu_moins_cher.png)

## 1. Pourquoi ce fichier, et c'est `102` qui l'impose

`102` a mesuré que la matière porte **au moins** deux pas, et sa portée est **censurée** : 17 bandes
sur 28 butent sur un plafond de six pas. Relever ce plafond est la marche suivante — mais un cube
coûte **15,4 s** de lecture réseau, donc trente pas demanderaient **quatorze heures**. Avant de
subir ce coût, il faut savoir s'il est réductible.

⭐ Une économie existait **en principe**, et elle est propre : **rétrécir** le cube changerait la
structure vue, mais l'**échantillonner** plus grossièrement — un voxel sur deux, **même portée** de
98,4 µm — change seulement combien on paie pour la regarder. La portée physique est identique à
tous les pas, et c'est asserté.

## 2. ⭐⭐⭐ La garde, sur un empilement dont la réponse est connue

Chaque finesse est jugée contre la barre du nul de **sa propre forme** — un cube plus grossier a
moins de points, donc un nul différent, et réutiliser la barre d'une autre forme comparerait deux
choses.

| pas | points | angle lu | désaccord des moitiés | barre de sa forme | marge | garde |
|---|---|---|---|---|---|---|
| 1 | 68 921 | 7,96° | 9,72° | 8,91° | **−0,81°** | **NON** |
| 2 | 9 261 | 4,41° | 3,60° | 11,21° | **+7,61°** | TIENT |
| 3 | 2 744 | 7,27° | 5,86° | 7,54° | +1,68° | TIENT |
| 4 | 1 331 | 4,49° | 9,21° | 6,00° | **−3,21°** | **NON** |

⚠ **La première ligne surprend** : à ce niveau de bruit (σ = 15 pour une amplitude de 40), le cube
**pleine résolution** ne tient pas sa propre garde, là où un pas de 2 la passe avec sept degrés de
marge. C'est cohérent avec le balayage de bruit de `101` — dériver sur une base plus longue moyenne
le bruit par voxel.

⚠⚠ **Mais ce n'est pas une raison de ne pas lire le cube en entier.** Le pas de référence n'est
**pas** une économie à juger, c'est le statu quo ; le compter parmi les candidats produisait la
ligne absurde *« pas 1 — la garde ne tient pas »*, qui se lit comme un refus de lire le cube
entier. Il est désormais **décrit** à côté du verdict, jamais jugé.

## 3. ⛔⛔ Le contrôle apparié sur le vrai volume, et il réfute

**55 cellules**, **28 bandes**, chacune lue **une fois par pas** — comparer deux populations
différentes ferait dire au résultat ce qu'on veut, et ce dépôt l'a déjà payé.

| pas | rangées | s/cube | gain | écart médian | p90 | **> 10°** | marches de 6 pas abîmées |
|---|---|---|---|---|---|---|---|
| 1 | 1681 | 14,40 | ×1,00 | — | — | — | — |
| 2 | 441 | 8,37 | **×1,72** | 2,09° | 6,18° | **7,3 %** | **36,5 %** |
| 3 | 196 | 4,82 | ×2,99 | 4,39° | 10,87° | 10,9 % | 50,0 % |
| 4 | 121 | 3,76 | ×3,83 | 5,77° | 16,36° | 29,1 % | 87,3 % |

> ⛔ **Aucun pas grossier ne satisfait les deux conditions.** Le moins grossier écarte déjà 7,3 %
> des cellules de plus de dix degrés du pas le plus fin.

⭐⭐⭐ **Et c'est la conséquence ENCHAÎNÉE qui décide.** Pris **un** pas à la fois, 7,3 % n'a l'air
de rien. Mais `102` **enchaîne** les pas, et la part de marches touchées vaut `1 − (1 − p)^k` : à
six pas, **36,5 %** des marches sont abîmées. Publier le taux par pas sans sa conséquence
enchaînée laisserait croire l'économie inoffensive.

⚠ La tolérance de **10°** n'est pas un réglage : c'est moins d'un tiers des **34°** que `101` a
mesurés entre la matière et le rayon. Une direction qui bouge de plus que ça en changeant de
finesse ne mesure plus la même chose.

## 4. ⚠⚠⚠ Ma propre sonde disait l'inverse, sur deux bandes

Le premier contrôle apparié, sur **2 bandes** et 20 cellules, donnait **0 %** de cellules au-delà
de dix degrés au pas 2. J'allais adopter l'économie sur cette base.

> ⚠⚠ **Sur les 28 bandes, c'est 7,3 %.** *Un bord se compte sur le corpus entier, pas sur les
> bandes qu'on a sondées* — la faute que `93` a payée, que `95` a réécrite, et que je viens de
> repayer.

⭐ Ce qui l'a attrapée n'est pas une relecture : c'est d'avoir relancé sur le corpus **avant** de
publier, parce que la règle était écrite.

## 5. ⚠⚠⚠ Et le gain de temps n'est pas le gain de points

| pas | gain **prédit** par le comptage de points | gain **mesuré** |
|---|---|---|
| 2 | **×7,44** | ×1,72 |
| 3 | ×25,12 | ×2,99 |
| 4 | ×51,78 | ×3,83 |

Une lecture distante est dominée par le nombre de **plages d'octets** — `voxel_distant` recolle une
plage par rangée `(z, y)` — et par un **fixe par cube**, pas par le nombre de points : un cube
sous-échantillonné touche toujours une plage par rangée. **Le coût se mesure, il ne se modélise
pas.**

⚠ Et le rapport de points lui-même n'est **pas** huit : un pas de 2 sur 41 points en laisse **21**,
pas 20,5, donc il vaut `(41/21)³ = 7,44` et non `2³`. Le supposer rond était une erreur.

## 6. ⚠⚠ Ce que la tranche ne débloque pas, et ce qu'elle laisse quand même

- **La portée de `102` reste à quatorze heures** pour trente pas. L'économie l'aurait divisée par
  deux ; elle est réfutée, donc la borne de `102` se lèvera en payant le prix plein, ou pas du tout.
- ⭐ **Mais le coût est désormais MESURÉ et non supposé** : **15,4 s** par cube, un **plancher de
  3,76 s** qui ne descend jamais quelle que soit la finesse, et un temps qui suit les **rangées**.
  C'est ce qui permet de chiffrer d'avance ce que coûte chaque nouvelle mesure au lieu de le
  découvrir après sept heures.
- ⚠ Le verdict porte sur **ce cube-ci** (98,4 µm, demi = 20) et sur **ce fragment**. Un cube plus
  grand aurait plus de points par rangée et un rapport différent.
- ⚠ La garde du fabriqué est évaluée à **un** niveau de bruit (σ = 15). Ce n'est pas le bruit
  mesuré du volume, qui n'est pas connu ici — c'est un cas dur choisi pour que la garde soit
  éprouvée, pas un modèle du réel.

## Reproduire

```
uv run python src/nappe/le_sens_du_rang.py --telecharger
uv run python src/nappe/le_cube_lu_moins_cher.py --verifier
uv run python src/nappe/le_cube_lu_moins_cher.py --cellules 2 --bandes 28 \
    --json docs/mesures/le_cube_lu_moins_cher.json      # ~25 min de lectures reseau
uv run python src/nappe/le_cube_lu_moins_cher.py --reagreger \
    --json docs/mesures/le_cube_lu_moins_cher.json      # rederive le verdict, sans reseau
uv run python src/figures/figure_le_cube_lu_moins_cher.py --verifier
```
