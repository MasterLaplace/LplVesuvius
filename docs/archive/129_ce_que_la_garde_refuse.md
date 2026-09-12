# 129 — La garde refuse deux pas voyants sur cinq, et le taux ne le voit pas

> ⭐⭐⭐⭐ **SUR LA VRAIE MATIÈRE, 161 PAS VOYANTS SUR 382 — SOIT 42,15 % — SONT PRIS DANS UNE
> DIRECTION QUE LA GARDE REFUSE**, sur **23 marches sur 28**. Le désaccord des deux moitiés du cube
> y vaut **14,56°** en médiane pour une barre de **8,88°**, et va jusqu'à **90,0°**, c'est-à-dire
> l'angle droit.
>
> ⭐⭐⭐⭐ **ET LE PRÉDICAT PUBLIÉ NE LES DISTINGUE PAS** : le taux confirmé vaut **0,7511** sur les
> pas orientés et **0,7764** sur les refusés. L'écart médian par marche est **−0,0202** et le test
> apparié rend **p 0,5861** sur 19 marches — il **échoue à rejeter**. « Le marcheur confirme trois
> pas sur quatre » compte donc à égalité des pas dont la direction est refusée par sa propre garde.
>
> ⚠⚠⚠ **ET CE DOCUMENT RÉFUTE LE REMÈDE QUE `128` SUGGÉRAIT.** J'y écrivais qu'un marcheur qui ne
> prend pas le pas que sa garde refuse n'irait pas se faire chasser. S'arrêter au premier refus
> jetterait **443 pas sur 560 (79,11 %)**, dont **276 étaient CONFIRMÉS**, et **87616,2 µm**
> parcourus.
>
> ⭐⭐⭐ **PARCE QUE LE DÉSACCORD N'EST PAS ABSORBANT, ALORS QUE LA CÉCITÉ L'EST.** Après un pas
> refusé, l'orientation revient une fois sur deux (**0,5033**), et dans les mêmes données un pas
> aveugle n'est jamais suivi d'autre chose qu'un pas aveugle (**167 sur 167**). Le remède de `116`
> ne se transporte pas.
>
> ⚠⚠ **ET IL RESTE UN RÉGIME RARE QUI RESSEMBLE À CE QUE `128` FABRIQUE** : le **p99** du désaccord
> des pas refusés vaut **89,11°**, contre **88,52°** pour une faille fabriquée. Environ un pas
> refusé sur cent lit ce que lit une rupture.
>
> ⭐ **Zéro lecture distante** : tout se calcule sur les 560 étapes que `113` a gardées.

## 1. Pourquoi ce fichier

`128` mesure qu'une faille fait crier la garde des moitiés — 88,52° pour une barre de 10,06° — et
que **le pas est pris quand même** : `oriente` est calculé, enregistré, et la boucle avance dans
cette direction. Restait à savoir ce que ça vaut sur la vraie matière, et la course de `113` le
sait déjà : elle a gardé ses 560 étapes.

⚠⚠⚠ **`oriente` est recalculé, jamais lu.** Le drapeau enregistré dans cette course date d'**avant**
la réparation de `120` : il déclarait `oriente` les **178** pas qui ne lisent rien, c'est-à-dire la
confiance maximale exactement là où le marcheur ne lit rien. Le lire ici rendrait une mesure de ce
bug et non de la garde. Il est reconstruit depuis le désaccord enregistré et la barre de la course,
de la même façon que `est_aveugle` reconstruit la cécité — et la batterie **asserte que le drapeau
enregistré est bien cassé**, donc elle échouera le jour où la course sera refaite avec le drapeau
réparé, ce qui est exactement quand il faudra cesser de le reconstruire.

⚠ Un pas aveugle n'est **pas** un pas désorienté : deux moitiés de rien ne peuvent pas être en
désaccord, leur angle vaut exactement 0,00° et passerait n'importe quelle barre. C'est `R4-L15`, et
les confondre remettrait le bug que `120` a fermé. Trois états, donc, là où `116` n'en voyait que
deux.

## 2. ⭐⭐⭐⭐ Combien la garde refuse

`PHercParis4`, 28 marches, 560 pas, barre du nul **8,88°**.

| | |
|---|---:|
| pas aveugles | 178 |
| pas voyants | **382** |
| dont **refusés** par la garde | **161** |
| part des voyants refusée | **0,4215** |
| marches concernées | **23 / 28** |

Le désaccord de ces 161 pas : médiane **14,56°**, p75 **21,34**, p90 **35,94**, p99 **89,11**,
maximum **90,0**.

⚠⚠ **La part est rapportée aux pas VOYANTS, pas à tous.** Un pas aveugle n'a pas de direction à
refuser ; le mettre au dénominateur diluerait la mesure d'un tiers et la ferait passer pour moins
grave qu'elle n'est.

⭐ **Ce n'est donc pas un incident, c'est le régime ordinaire.** Deux pas voyants sur cinq sont pris
dans une direction dont le marcheur a lui-même enregistré qu'il ne s'y fie pas.

## 3. ⭐⭐⭐⭐ Et le taux ne les distingue pas

| | orientés | refusés |
|---|---:|---:|
| pas | 221 | 161 |
| taux confirmé | **0,7511** | **0,7764** |

Écart médian **par marche** −0,0202, **p 0,5861** sur les 19 marches qui portent les deux états.

⚠⚠ **Le test est apparié par marche**, parce que 382 pas voyants sont 28 marches et non 382
tirages : c'est la réserve de grappe du dépôt, et l'unité décisive est la marche.

⚠ **Ce n'est pas une preuve d'égalité.** Le test **échoue à rejeter** à ce n-là, et le p est publié
pour qu'on le lise ainsi. Ce qui est établi est plus modeste et suffit : rien dans le taux publié ne
permet de séparer un pas orienté d'un pas refusé.

⭐ **Et les deux taux se recomposent exactement en celui de `115`** — 291 confirmés sur 382, soit
**0,7618** — ce que la batterie vérifie. Le nombre publié depuis `115` est donc bien celui-là, et il
ne dit pas ce qu'on lui fait dire.

⚠ La sonde qui rend le résultat lisible : sur un jeu fabriqué où les pas refusés ne sont **jamais**
confirmés, le même test **les distingue**. « Le taux ne distingue pas » n'est donc pas vrai de
n'importe quel jeu.

## 4. ⭐⭐⭐ Le désaccord n'est pas absorbant

| transition | compte |
|---|---:|
| aveugle → aveugle | **167** |
| aveugle → orienté | **0** |
| aveugle → refusé | **0** |
| orienté → orienté | 135 |
| orienté → refusé | 75 |
| orienté → aveugle | 2 |
| refusé → orienté | **77** |
| refusé → refusé | 71 |
| refusé → aveugle | 5 |

La part de retour après un refus vaut **0,5033**. L'orientation revient sur **19** des **23**
marches qui en avaient l'occasion — et le témoin de permutation, qui redistribue les positions
refusées **à l'intérieur de chaque marche à compte constant**, en attend **19,0** au hasard.
L'observé n'a donc rien de remarquable, ce qui est la façon honnête de dire qu'il n'y a pas
d'absorption à trouver.

⚠⚠ Seules les positions **voyantes** sont permutées entre elles. Mélanger les aveugles avec le
reste déplacerait un état que `116` a déjà montré absorbant, et le tirage ne répondrait plus à la
question posée.

⭐⭐ **Le contraste avec la cécité est dans les mêmes données, la même course, la même ligne de
code** : un pas aveugle n'est jamais suivi d'autre chose. `116` a raison, et sa raison ne s'étend
pas d'un état à l'autre.

⚠ La sonde : sur un jeu fabriqué où le refus ne se lève jamais, le même verdict rend **vrai**. Il
peut donc échouer.

## 5. ⚠⚠⚠ Ce que le remède de `128` coûterait

| | |
|---|---:|
| pas jetés | **443 / 560** |
| part | **0,7911** |
| dont **confirmés** | **276** |
| micromètres jetés | **87616,2** |
| marches tronquées | 23 |
| rang médian du premier refus | **0,0** |

⚠⚠ **C'est une correction de ce que j'ai écrit dans `128`**, et elle vient de la mesure et non d'une
relecture. Sur une pile fabriquée portant une faille, ne pas prendre le pas refusé aurait épargné au
marcheur 216 µm en travers de l'empilement. Sur la vraie matière, la même règle jetterait quatre
cinquièmes de la course et 276 pas que le dépôt compte comme réussis.

⚠ Le rang médian du premier refus vaut **0,0** : plus de la moitié des marches sont refusées dès
leur premier pas. Sur la pile fabriquée de `128`, c'était **12 marches sur 12**, et l'explication y
était un artefact de départ. Ici la part refusée au rang 0 vaut **0,625** contre **0,4078** aux
rangs suivants, soit un facteur **1,533** — mais sur 24 marches, Fisher exact rend **p 0,0529**.
**Ce n'est donc pas établi**, et le dire autrement serait lire un facteur comme un fait.

⚠⚠ Ma première version de ce verdict demandait un facteur supérieur à **1,5**, et la mesure a rendu
**1,533**. Un seuil posé à quelques millièmes du résultat est un seuil réglé sur ce qui passe, même
quand on ne l'a pas voulu : il est remplacé par un test, qui ne demande aucun choix — et le test
renverse la réponse.

## 6. Ce que ça change pour le graal

- ⭐⭐⭐⭐ **Le taux publié ne veut pas dire « le marcheur suit la matière ».** Il compte à égalité
  des pas dont la direction est refusée par la garde, et ils sont deux sur cinq. Tout ce qui est
  bâti sur ce nombre — la portée, la comparaison à l'humain — en hérite.
- ⭐⭐⭐ **`oriente` reste la meilleure gâchette disponible, mais pas pour arrêter.** Il est calculé
  au pas, il est là 42 % du temps, et le prendre comme règle d'arrêt jetterait 79 % de la course.
  En revanche **relâcher un lien latéral** là où le pas est refusé n'arrête rien : c'est ce que
  `R4-P25` cherche, et c'est la seule chose que le mécanisme sait déjà dire au bon moment.
- ⚠⚠ **Et il y a un régime rare qui ressemble à une rupture** : le p99 du désaccord des pas refusés
  vaut **89,11°**, contre **88,52°** pour la faille fabriquée de `128`. Environ un pas refusé sur
  cent lit ce que lit une rupture. Ce sont ceux-là qu'un lien devrait respecter — reste à savoir
  s'ils marquent une vraie discontinuité du rouleau ou un accident de lecture, ce qui est `R4-P26`.
- ⚠ **Et ce document ne tranche pas pourquoi les deux moitiés se désaccordent.** La course n'a gardé
  que la direction choisie, pas les candidates : savoir si une autre direction au même endroit
  aurait mis les moitiés d'accord demande une re-course, donc des lectures distantes.

## 7. Les registres

Faits `R4-F58` (deux pas voyants sur cinq sont pris contre la garde, et le taux ne les distingue
pas) et `R4-F59` (le désaccord n'est pas absorbant, contrairement à la cécité, donc s'arrêter
dessus coûterait quatre cinquièmes de la course). `R4-P25` gagne la gâchette disponible et ce
qu'elle ne peut pas faire. Aucune porte nouvelle.

## Reproduire

```bash
uv run python src/nappe/ce_que_la_garde_refuse.py --verifier   # 23 contrôles
uv run python src/nappe/ce_que_la_garde_refuse.py \
    --json docs/mesures/ce_que_la_garde_refuse.json
```

⚠ **Zéro lecture distante.** La cécité est importée de `115` par `est_aveugle`, la course est celle
de `113`, et la discipline du témoin de permutation est celle de `116`. Ce fichier n'ajoute que le
troisième état.
