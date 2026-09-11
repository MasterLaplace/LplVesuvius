# 116 — La cécité est absorbante : le marcheur avait son arrêt depuis le début

> ⭐⭐⭐⭐ **LE MARCHEUR AVAIT UN CRITÈRE D'ARRÊT ET NE S'EN SERVAIT PAS.** Sur les **11 marches**
> qui cessent de lire, **aucune ne relit** : 167 transitions aveugle → aveugle, **0** aveugle →
> voyant. Les positions aveugles permutées à l'intérieur de chaque marche rendent **7 retours de
> vue en médiane**, et **jamais moins de 5** sur 2 000 tirages. L'observé est à zéro.
>
> ⭐⭐⭐⭐ **DONC LA PREMIÈRE PORTÉE NON CENSURÉE DE CE DÉPÔT.** S'arrêter au premier pas aveugle,
> c'est **11 marches sur 28 qui s'arrêtent pour une raison** — médiane **579,5 µm**, max
> **3312,9 µm**. Les 17 autres touchent encore le plafond : leur longueur reste une borne
> inférieure, comme à `107` et `113`.
>
> ⭐⭐⭐ **ET LE VIDE N'EST PAS LE BORD DU ROULEAU.** Rangées par rayon, les marches aveugles font
> **8 plages** là où une frontière radiale en prédit **2** — et 14 sous permutation (p 0,0095). Une
> marche lit ses vingt pas à 22,17 mm pendant qu'une autre ne lit rien dès le premier à 21,26.
>
> ⭐ **Zéro lecture distante** : tout se calcule sur les 560 étapes que `113` a gardées.

![La cécité est absorbante](../images/116_la_cecite_est_absorbante.png)

## 1. Pourquoi ce fichier

`113` a levé le plafond de six pas à vingt et a mesuré que **rien n'arrête une marche** : 28 sur 28
au plafond, zéro sortie de volume. La portée est donc restée entièrement censurée — c'est le mur
que la porte `R4-P20` nomme, et un plafond que tout le monde atteint est un budget, pas une borne.
`115` a ensuite trouvé qu'un pas sur trois **ne lit rien**.

Les deux constats posent la même question : ces pas aveugles sont-ils l'arrêt qui manquait ?

⭐ Et la réponse décide de ce qu'on livre, parce que les deux issues n'ont pas le même remède. Si la
cécité est **absorbante**, s'arrêter dessus ne coûte rien et la portée devient mesurable. Si elle
est **transitoire**, s'arrêter tronquerait de bonnes marches et le remède est de traverser le vide,
pas de s'y arrêter.

## 2. ⭐⭐⭐⭐ Aucune marche ne relit

| transition | compte |
|---|---:|
| voyant → voyant | 358 |
| voyant → aveugle | **7** |
| aveugle → aveugle | 167 |
| **aveugle → voyant** | **0** |

Onze marches portent au moins un pas aveugle, et les onze avaient l'occasion de relire — leur
premier pas aveugle n'est jamais le dernier pas de la marche. Aucune ne l'a fait.

⚠ Une marche dont le seul pas aveugle serait le **dernier** n'a aucune occasion de relire, et elle
serait comptée à part plutôt que portée au crédit du résultat. Il n'y en a aucune ici, mais la
distinction est dans le code parce que sans elle un corpus qui n'a jamais pu montrer le retour de
la vue rendrait quand même « absorbante ».

⚠ En revanche une marche **entièrement** aveugle a bien des occasions : dix-neuf pas de suite où la
vue aurait pu revenir. C'est une preuve, pas une abstention.

## 3. ⭐⭐⭐ Le témoin, sans lequel « zéro » ne dit rien

Onze marches qui portent beaucoup de pas aveugles ont mécaniquement peu d'occasions de faire
revenir la vue : la contiguïté pourrait n'être qu'une conséquence de la fréquence. Les positions
aveugles sont donc **permutées à l'intérieur de chaque marche**, à compte constant — chaque marche
garde exactement son nombre de pas aveugles, seul leur ordre change.

| | retours de vue |
|---|---:|
| observé | **0** |
| médiane sous permutation | **7** |
| minimum sur 2 000 tirages | **5** |
| part des permutations aussi basse | **0,0** |

⚠ La permutation est **intra-marche** et non globale : mélanger tous les pas du corpus détruirait
aussi la concentration des aveugles dans certaines marches, donc testerait deux choses à la fois
sans dire laquelle a bougé.

⚠ Le test est **unilatéral à gauche**, et c'est écrit : l'hypothèse est que l'observé est plus bas
que le hasard. Un p bilatéral mélangerait ici deux questions dont une seule est posée.

## 4. ⭐⭐⭐ Le vide n'est pas une frontière

Si l'extérieur du rouleau n'avait plus de matière, alors rangées par rayon croissant les marches
voyantes viendraient toutes d'abord et les aveugles toutes ensuite : **deux plages**.

| | plages |
|---|---:|
| sous une frontière radiale | 2 |
| **observé** | **8** |
| médiane sous permutation | 14 |
| part des permutations aussi peu de plages | **0,0095** |

La première marche aveugle est à **16,93 mm** et la dernière voyante à **22,17 mm** : les deux
populations se **recouvrent** sur cinq millimètres et demi.

Les deux verdicts sont indépendants et tous les deux informatifs : la **frontière tombe** (8 ≠ 2)
et le **rayon organise quand même** quelque chose (8 ≪ 14, p 0,0095). Le détail le montre à l'œil
nu — à 20,69 mm et à 22,17 mm une marche lit ses vingt pas, pendant qu'à 21,26 · 21,75 · 23,03 et
23,31 mm le marcheur ne lit rien **dès le premier pas**.

⚠⚠ Ce qui tombe est la frontière nette, **pas** l'une des deux autres causes de `R4-P22` : « la
matière extérieure est elle-même en morceaux » et « des blocs manquent au chargement » prédisent
toutes les deux des plaques. Les séparer demande d'interroger le volume aux positions de départ,
donc une lecture distante.

## 5. ⭐⭐⭐⭐ La première portée non censurée

S'arrêter au premier pas aveugle sépare les 28 marches en deux populations qui **ne se mélangent
jamais dans une médiane commune** :

| | marches | longueur médiane | max |
|---|---:|---:|---:|
| **s'arrêtent pour une raison** | **11** | **579,5 µm** | 3312,9 µm |
| touchent encore le plafond | 17 | 3650,3 µm | — |

La seconde ligne reste une **borne inférieure**, exactement comme à `107` et à `113`. La première
est la première longueur de ce dépôt qui a une cause observée.

⚠ Quatre des onze s'arrêtent **dès le premier pas** : leur portée est nulle, et elles tirent la
médiane vers le bas. La médiane est donnée telle quelle plutôt que sur les sept qui avancent —
écarter les portées nulles serait choisir la population qui rend le nombre qu'on préfère.

⚠ La longueur retenue est celle du **dernier pas voyant** : compter le pas aveugle ferait entrer
dans la portée la distance parcourue dans le vide.

⚠⚠ **Et ce que cette portée mesure est « jusqu'où le volume répond », pas « jusqu'où la matière
porte ».** Tant que `R4-P22` n'est pas tranchée, un vide dû à des blocs manquants rendrait ces
579 µm plus courts que la matière réelle. Le nombre est une portée du **couple marcheur-volume**.

## 6. Ce que ça change pour le graal

- La question du graal est *qu'est-ce qui remplace l'humain qui corrige le transfert de spire à
  spire ?* Une partie de la réponse est ici et elle est **gratuite** : le marcheur doit **s'arrêter
  quand il ne lit rien**, et la signature est disponible avant le pas (`115`). Il ne perd rien à le
  faire, puisque aucune marche ne relit jamais.
- ⭐ Ce que ça retire de la feuille de route : chercher pourquoi le taux s'effondre au grand rayon.
  Il ne s'effondre pas — le volume cesse de répondre, par plaques, et le marcheur continuait à
  marcher dedans en déclarant `oriente`.
- ⚠ Ce que ça n'apporte pas : la portée des 17 marches qui lisent tout. Elles touchent encore le
  plafond de vingt pas, donc **la portée sur matière lisible reste censurée**. C'est ce que `R4-P20`
  demande encore, et le remède est le même qu'à `113` — un plafond plus haut, ou l'acceptation que
  rien ne l'arrête.

## 7. Les registres

Faits : `R4-F39` (la cécité est absorbante), `R4-F40` (la première portée non censurée),
`R4-F41` (le vide n'est pas une frontière radiale). Portes `R4-P20` et `R4-P22` **resserrées**,
aucune ouverte : ce lot répond à des questions déjà posées, il n'en pose pas de neuves.

## Reproduire

```bash
uv run python src/nappe/la_cecite_est_elle_absorbante.py --verifier           # 41 contrôles
uv run python src/nappe/la_cecite_est_elle_absorbante.py \
    --json docs/mesures/la_cecite_est_elle_absorbante.json                    # une seconde
uv run python src/figures/figure_la_cecite_est_absorbante.py --verifier       # 20 contrôles
uv run python src/figures/figure_la_cecite_est_absorbante.py
```

⚠ **Aucune lecture distante** : tout se calcule sur `docs/mesures/jusquou_va_t_il_si_on_le_laisse.json`,
dont `113` a gardé les 560 étapes. La définition d'un pas aveugle est **importée** de
`ce_qui_porte_le_taux.py` et jamais recopiée : deux définitions de « ce pas n'a rien lu »
publieraient deux comptes du même phénomène sans que rien ne le dise.
