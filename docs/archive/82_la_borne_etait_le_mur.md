# 82 — La borne qu'on publiait était le mur du corpus

> ⚠⚠⚠ **`la_portee_du_raccrochage` publie côte à côte « la borne (oracle) : 6 » et « ce que le
> corpus autorise : 6 ». Personne n'avait demandé si les deux 6 sont le même 6. Ils le sont — sur
> les CINQ ancres, sans exception.** Une portée égale au plafond du corpus est une observation
> **censurée à droite** : elle dit « au moins », jamais « vaut ».

Ce document est un audit du résultat le plus cité du dépôt, et il vient de
[`81`](81_le_rouleau_designe_ne_publie_rien.md) §3 bis, qui a trouvé le trou géométrique par
accident en croisant deux mesures pour une tout autre raison.

![la portée mesure-t-elle le marcheur, ou le mur du corpus](../images/82_le_mur_du_corpus.png)

## 1. Le mur, et pourquoi aucun marcheur ne peut le franchir

Le corpus publié de `PHerc0500P2` offre huit bras depuis l'ancre 4. Sept demandent entre 77 et
170 µm — le pas nominal vaut 135,5. Le huitième, non :

| bras | de → vers | ce que le corpus demande | hors du pas nominal |
|---:|---|---:|---:|
| 5 | 8 → 9 | 137,6 µm | 2,1 |
| 6 | 9 → 10 | 89,2 µm | 46,3 |
| **7** | **10 → 11** | **1000,6 µm** | **865,1** |
| 8 | 11 → 12 | 76,7 µm | 58,8 |

⭐⭐⭐ **Les spires 10 et 11 se suivent par leur numéro et sont à 7,4 feuilles l'une de l'autre.**
Et le décalage que cette famille de marcheurs sait appliquer est de **±67,8 µm** — une demi-feuille
exactement, la fenêtre déjà mesurée et déjà publiée. Le bras 7 demande donc **12,8 fois** ce que le
meilleur d'entre eux peut atteindre.

⚠⚠ **Ce n'est pas un échec de méthode, c'est une impossibilité de construction, et l'oracle est
dedans.** L'oracle regarde la cible, mais il *garde la longueur de son pas* — son en-tête le dit —
donc il ne peut pas non plus franchir 865 µm. Sa portée s'arrête au bras 6 pour la même raison que
tout le monde.

## 2. ⭐⭐⭐ La borne est censurée sur 5/5 ancres

| ancre | bras offerts | plafond du corpus | oracle | pouvoir de séparer |
|---:|---:|---:|---:|---:|
| 4 | 8 | **6** | **≥6** | 4 |
| 5 | 8 | **5** | **≥5** | 3 |
| 6 | 7 | **4** | **≥4** | 2 |
| 7 | 6 | **3** | **≥3** | **1** |
| 8 | 5 | **2** | **≥2** | **1** |

L'oracle touche le plafond **partout**. « La borne vaut 6 » n'est donc pas établi : la vraie borne
est **inconnue et ≥ 6**. C'est le péché numéro un de ce dépôt — *une limite de grille publiée comme
une limite matérielle* — présent dans son résultat le plus cité, et il aura fallu croiser deux
fichiers de mesure que rien ne croisait pour le voir.

## 3. ⚠⚠ Les cinq ancres ne sont pas cinq réplications

Le plafond de chaque ancre vaut exactement **10 − ancre** : 6, 5, 4, 3, 2. Les cinq meurent au
**même** saut, celui entre les spires 10 et 11. « Le signe tient sur 5/5 ancres » compte donc cinq
fois un seul défaut du corpus, et la dynamique disponible s'effondre linéairement à mesure que
l'ancre monte.

⛔ **Deux ancres ne séparent rien du tout.** À l'ancre 7 (plafond 3) les sept marcheurs aveugles
rendent tous **2** ; à l'ancre 8 (plafond 2), tous **1**. Une ancre dont le plafond vaut 2 offre
trois valeurs possibles dont une censurée : elle ne peut séparer aucune paire de méthodes, quelles
qu'elles soient. Les compter comme des confirmations, c'est **compter du silence**.

## 4. ★★ Ce qui tient, et il faut le dire aussi

⚠ Cet audit **ne rétracte pas** le résultat de portée. À l'ancre 4, le plafond vaut 6, quatre
valeurs distinctes sortent, et le pas normal (4) comme sa version lissée (5) sont **sous** le
plafond : cette comparaison-là mesure bien les marcheurs, et le gain d'un bras par le lissage n'est
pas touché. Ce qui tombe est la **borne**, pas le résultat.

⚠ Ce qui tombe aussi, c'est la lecture « il ne reste qu'un bras de marge avant la borne ». La marge
réelle entre le meilleur marcheur aveugle et la borne est **inconnue** — elle pourrait être bien
plus grande, ce qui serait une **bonne nouvelle pour l'objectif**, et la mesurer demande un corpus
sans ce trou.

## 5. Ce que ça change pour la suite

⭐⭐ **La question « jusqu'où un marcheur aveugle peut-il aller » n'a jamais été posée dans des
conditions où elle pouvait recevoir une réponse.** Toutes les portées publiées ont été mesurées
contre un plafond de 6 au mieux, 2 au pire, quand l'objectif en demande **31**.

⚠ Et ça recoupe [`81`](81_le_rouleau_designe_ne_publie_rien.md) par un chemin indépendant : le
corpus de `PHerc0500P2` ne borne pas seulement ce qu'on peut **prouver**, il borne ce qu'on peut
**apprendre**. Un objet à 120 spires consécutives ne rendrait pas la marche meilleure — il rendrait
la mesure capable de la juger.

> ⚠ **Ce document ne remesure rien.** Il relit deux artefacts versionnés,
> `la_portee_du_raccrochage.json` et `la_portee_tient_elle_ailleurs.json`, et croise ce que ni l'un
> ni l'autre ne croisait. Il tourne hors ligne, en une seconde.

## Reproduire

```
uv run python src/nappe/le_mur_du_corpus.py
uv run python src/nappe/le_mur_du_corpus.py --verifier
uv run python src/nappe/le_mur_du_corpus.py --json docs/mesures/le_mur_du_corpus.json
uv run python src/figures/figure_le_mur_du_corpus.py --verifier
```
