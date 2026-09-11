# 62 — Une hypothèse qui méritait d'être construite, et qui est fausse

> ⭐ **Ce document ne porte pas un résultat, il porte une élimination.** L'hypothèse était
> élégante, sa frontière tombait exactement entre les deux cas observés, et elle est
> **fausse**. Ce que la réfutation laisse derrière elle vaut mieux que ce que l'hypothèse
> aurait donné si elle avait été juste : elle ferme une **classe** de causes, pas un cas.
>
> ⚠⚠⚠ **Et le lendemain, la question elle-même s'est dissoute** : il n'y avait pas d'écart
> à expliquer. Le §7 le mesure et corrige le §1, qui affirmait à tort avoir écarté la
> contention. Le document est conservé dans cet ordre — l'hypothèse, sa réfutation, puis la
> dissolution de sa prémisse — parce que c'est l'ordre dans lequel on a appris, et qu'une
> version réécrite depuis la fin ferait passer trois erreurs pour un raisonnement droit.

## 1. La question

Deux rendus du **même rouleau**, avec le même modèle, le même pas de balayage, le même nombre
de fils, sur la même machine libre, ne coûtent pas le même prix :

| segment | taille | fenêtres | durée | ms par fenêtre |
|---|---|---|---|---|
| `PHerc1447_complet` | 2980 × 3240 | 21 128 | 2079,5 s | **98** |
| `1447_20250703025628` | 4100 × 4260 | débit soutenu | — | **455** |

Un facteur **4,6** pour une surface 1,8 fois plus large. Écartés d'emblée, **par mesure et non
par raisonnement** :

- ⚠⚠⚠ ~~la **contention** — `ps` donne 1586 % de CPU et `/proc/loadavg` vaut les seize fils
  demandés, donc le processus a bien la machine~~ **FAUX, et c'est l'erreur qui a tout
  déclenché** : 1586 % sur une machine qui en offre **2200** veut dire que **six cœurs
  faisaient autre chose**, c'est-à-dire exactement la contention que je déclarais écartée.
  Le chiffre était juste, la lecture était fausse. Voir le §7 ;
- la **mémoire** — 33 Gio libres, zéro swap, 2,4 Gio de RSS ;
- le **type de données et la profondeur** — les deux piles sont en `uint8`, 31 couches, lues
  avec `tifffile` ;
- le **pas et la fenêtre** — 21 et 64 dans les deux cas, vérifiés en recalculant les comptes de
  fenêtres depuis les dimensions (139 × 152 = 21 128 ; 193 × 200 = 38 600).

## 2. L'hypothèse, et pourquoi elle méritait d'être construite

La fenêtre que le modèle consomme fait **toujours** 26 × 64 × 64. Le coût du modèle ne *peut
donc pas* dépendre de la taille du segment. Ce qui en dépend, c'est le **rassemblement** :

```python
bloc = stack[:, y : y + TILE, x : x + TILE]
```

soixante-quatre lignes lues dans chacune des vingt-six couches. Un balayage complet en `x`
garde donc vivante une **bande** de soixante-quatre lignes pleine largeur :

$$
\text{bande} = 26 \times 64 \times \text{largeur} \times 4\ \text{octets}
$$

| largeur | bande | L3 de la machine |
|---|---|---|
| 3240 | **20,6 Mio** | 24 Mio — ça tient |
| 4260 | **27,0 Mio** | 24 Mio — ça ne tient plus |

⭐ La largeur critique vaut **3780 colonnes**, et elle tombe **exactement entre les deux
segments observés**. Une falaise de cache a précisément cette forme : un tiers de bande en
plus, plusieurs fois le temps. C'est ce qui rendait l'hypothèse digne d'être construite plutôt
que discutée.

⚠ Elle venait aussi avec un **remède** tout fait : réordonner le balayage par blocs de colonnes
assez étroits pour que la bande tienne. Le même *ensemble* de fenêtres, un autre *ordre*, donc
la même carte au bit près.

## 3. La mesure, qui l'ignore

![La falaise prédite, et l'ordre de grandeur qui tranche](../images/62_hypothese_refutee.png)

*À gauche, le coût du rassemblement en fonction de la largeur, dans les deux ordres de
balayage ; la verticale rouge est la largeur critique prédite. À droite, la même mesure mise
en regard de l'écart qu'elle prétendait expliquer, en échelle logarithmique.*

```
  largeur   bande        cache   en ligne   par blocs
     1024    6.50 Mio     oui     0.072      0.064
     2048   13.00 Mio     oui     0.069      0.067
     3240   20.57 Mio     oui     0.127      0.166
     4260   27.04 Mio     NON     0.167      0.121
     6000   38.09 Mio     NON     0.119      0.075
```

Deux constats, et le second est celui qui tue :

1. **Aucun coude à 3780.** La verticale prédite passe au milieu du graphe sans rien marquer, et
   6000 colonnes coûtent **moins** que 4260.
2. ⭐⭐ **L'ordre de grandeur.** Le rassemblement le plus cher coûte **0,167 ms** par fenêtre
   quand l'écart à expliquer en vaut **356,6**. Rapport mesuré : **×2142**.

⚠⚠ Le second constat est plus solide que le premier, et c'est une leçon de méthode à garder.
Une réfutation qui tient à la **forme d'une courbe** se rouvre au premier point de mesure
bruité — on peut toujours plaider que l'échantillonnage a raté le coude. Une réfutation par
**ordre de grandeur** ne se rouvre pas : une cause deux mille fois trop petite reste trop
petite quelle que soit la forme de la courbe.

## 4. Ce que la réfutation ferme

Une boucle de rendu ne fait que **trois** choses, et on peut les prendre une par une :

| étape | dépend de la taille du segment ? | pourquoi |
|---|---|---|
| rassembler | **non** | mesuré à 0,17 ms, deux mille fois trop petit |
| appeler le modèle | **non** | l'entrée fait 26 × 64 × 64 par construction |
| disperser | **non** | écrit les mêmes 64 × 64 pixels dans les deux cas |

⭐ Donc **aucune partie de la boucle ne peut dépendre de la taille du segment**, et la cause de
l'écart est nécessairement **hors du segment** : état de la machine, fréquence soutenue, ou une
différence de paramètre entre les deux lancements qui n'a pas encore été trouvée. Une classe
entière d'explications est éliminée, ce qu'aucune hypothèse *confirmée* n'aurait fait.

⚠ Le remède, lui, est mort avec sa cause. Le balayage par blocs reste **dans la mesure** — la
colonne « par blocs » du tableau — parce qu'il est la **preuve** qu'il n'y avait rien à
remédier : réordonner ne gagne rien. Ce n'est pas un correctif en attente, et le fichier le dit
à sa place, sinon quelqu'un le rebrancherait un jour en croyant réparer quelque chose.

## 5. Trois choses attrapées en chemin

⚠ **Une confusion Mio / Mo.** La première rédaction annonçait 21,6 et 28,4 — les mêmes octets
comptés en méga**octets décimaux**. La batterie l'a attrapée, et le slip est **gardé dans le
fichier** plutôt que corrigé en silence : comparer une bande en Mo à un cache en Mio est
exactement la façon dont une frontière se retrouve du mauvais côté.

⚠⚠ **Une vérification incapable d'échouer, deux heures après [`61`](61_les_batteries_qui_ne_pouvaient_pas_echouer.md).**
Le contrôle « la prose de la figure est traçable par la police » a d'abord été écrit avec une
condition toujours vraie à côté. Il est maintenant doublé de son **contrôle négatif** : la
fonction doit *refuser* un glyphe que DejaVu n'a pas. Sans cette moitié, le premier contrôle
est satisfait par une fonction qui répondrait oui à tout.

⚠⚠ **Et le cas symétrique de `61`, découvert en câblant ces deux batteries.** Elles
imprimaient `TOUS LES TEMOINS PASSENT` alors que `temoins.sh` exige `ALL PASS` : elles
seraient sorties **vertes** et auraient été comptées **ÉCHEC**, leurs quarante contrôles
perdus du total. La règle est maintenant dans le garde-fou, et il a fallu s'y reprendre à
deux fois — détail en [`61`](61_les_batteries_qui_ne_pouvaient_pas_echouer.md) §3 bis.

ⓘ **La seizième copie d'un même mécanisme, évitée de justesse.** J'allais écrire une fonction
`_police` dans la figure — `src/figures/figure_commune.py` existe précisément parce qu'elle
l'était **quinze fois**, en quatre variantes. Le premier barreau de l'échelle de décision
(« est-ce déjà dans le code du projet ? ») a mordu.

⭐ **Et une garde confirmée par accident.** Le coin supérieur gauche de
`1447_20250703025628` est **entièrement vide** : la garde de pile posée le matin même l'a
refusé en nommant ses deux causes possibles — pile vide, ou mauvais plafond de normalisation —
au lieu de rendre du bruit. C'est [`60`](60_la_constante_qui_rendait_le_modele_muet.md) qui
travaille.

## 7. ⚠⚠⚠ La question s'est dissoute : il n'y avait pas d'écart

Mesuré le 2026-08-28, et c'est une correction de ce document par lui-même.

### 7.1 L'A/B que la section 4 réclamait

`src/encre/ab_segments.py` prend le **même crop**, cherché sur la couche médiane comme le bloc
le **plus plein** de chaque segment, et le rend avec les mêmes fils, à la suite, dans les
mêmes conditions :

| segment | crop | remplissage | ms/fenêtre | fen/fil-s |
|---|---|---|---|---|
| `20250703025628` | (640, 2560) | 100 % | 432,1 | **0,5785** |
| `20250703034159` | (1920, 1280) | 100 % | 293,5 | **0,8518** |

⭐ Le rapport tombe à **×1,47**, et le chiffre qui compte est ailleurs : le crop du segment
« lent » rend à **0,5785** quand son run complet donnait **0,132**. **Le même segment, le
même code, 4,4 fois plus vite.** Ce n'est donc ni sa taille ni son contenu.

### 7.2 Ce qu'une moyenne cumulée cachait

`src/encre/allure_du_rendu.py` lit les lignes de progression déjà écrites et rend l'allure
**instantanée** au lieu du cumul :

| rendu | cumul | min / médiane / **max** | amplitude |
|---|---|---|---|
| `20250703025628` | 2,109 fen/s | 0,267 / 1,200 / **11,429** | **×42,9** |
| `20250703034159` | 7,675 fen/s | 3,200 / 7,355 / **12,267** | ×3,8 |

⭐⭐ **Les deux rendus atteignent le même pic** — 11,4 contre 12,3 fenêtres par seconde. Le
segment 2 n'était pas lent : il a passé la plus grande partie de son run **contendu**, avec
une médiane de 1,2 contre 7,4. Sa vitesse a varié d'un facteur **43 sur elle-même**, et une
moyenne prise sur un intervalle où les conditions changent n'est la vitesse de rien.

### 7.2 bis Le contre-point, mesuré le lendemain sur une machine libre

Le **même crop du même segment**, rejoué pendant que la campagne téléchargeait au lieu de
rendre :

| conditions | secondes | ms/fenêtre | fen/fil-s |
|---|---|---|---|
| pendant que le segment 3 rendait | 338,8 | 432,1 | 0,5785 |
| **machine libre** | **134,1** | **171,0** | **1,4616** |

⭐⭐ **×2,5 pour le même travail, le même code, le même crop.** Et le débit obtenu **dépasse**
la référence de `cout_du_rendu.py` étiquetée « machine libre » (0,635) — donc cette référence
était elle-même contendue, et la colonne binaire du tableau ne pouvait pas le dire.

⚠ La carte rendue est **identique au bit** entre les deux exécutions (écart maximal 0,0, mêmes
pixels non couverts). C'est ce qui permet d'attribuer l'écart au temps et à rien d'autre :
sans cette égalité, « deux fois et demie plus vite » pourrait vouloir dire « en faisant moins ».

### 7.3 Et c'est moi qui prenais la machine

Pendant les trois heures du segment 2 : la suite de témoins, le balayage de largeurs de la
section 3, deux rendus de figure, deux sondes A/B, et les gardes du dépôt. Pendant le segment
3 : presque rien. Le « segment lent » et le « segment rapide » sont le même moteur sur deux
machines différentes, et c'est moi qui faisais la différence.

### 7.4 Ce qui survit, et ce qui tombe

| | |
|---|---|
| ✅ **la réfutation de la section 3** | intacte : le rassemblement coûte 0,167 ms, et cela reste vrai qu'il y ait un écart à expliquer ou non |
| ✅ **l'argument de la section 4** | intact, et confirmé par un troisième point : le segment 3 est **plus grand** (3620 × 5220 contre 4100 × 4260) et rend plus vite |
| ❌ **le « facteur 4,6 » de la section 1** | c'est un artefact de contention, pas une propriété d'un segment |
| ❌ **« la contention est écartée par mesure »** | la mesure disait l'inverse et je l'ai mal lue |

⚠⚠ **La leçon transportable, et elle vaut plus que le diagnostic** : un débit ne se publie pas
depuis un **cumul**. Il se publie depuis un intervalle dont on peut dire ce qui tournait à
côté — ou depuis un intervalle où rien ne tournait. `cout_du_rendu.py` publie des cumuls ; ses
cinq observations sont donc à relire avec cette réserve, et la colonne « machine partagée »
qu'il porte déjà est exactement la bonne distinction, mais elle est **binaire** là où la
contention est continue.

⚠ Et un piège de mesure trouvé en écrivant l'instrument : la ligne de progression change de
grammaire au-delà de l'heure. `35m04` veut dire « 35 min 4 s » et `2h54` veut dire « 2 h
54 min ». Un motif qui lirait les deux comme « premier, second » compterait `2h54` pour
2 min 54 — soit une allure **soixante fois trop grande** sur toute la fin d'un long run, sans
que rien dans le résultat n'ait l'air faux. Attrapé par la batterie, qui exige les deux formes.

## 6. Ce qui reste ouvert

⚠⚠ **Section écrite avant le §7, et conservée pour ce qu'elle dit de la méthode.** L'écart de
×4,6 n'est plus « inexpliqué » : il n'existe pas. Ce qui suit reste juste sur le fond — chaque
ligne écarte une cause qui est effectivement écartée — mais la dernière était la bonne piste et
je l'avais rangée en dernier.

L'écart de ×4,6 **n'est pas expliqué**, et il est important de le dire ainsi plutôt que de
laisser une hypothèse morte tenir lieu de réponse. Ce qui est acquis :

- ce n'est **pas** le segment, et la section 4 le démontre par élimination exhaustive de la
  boucle ;
- ce n'est **pas** la contention, la mémoire, le type de données ni le pas, tous mesurés ;
- l'A/B décisif — le **même crop** de chaque segment, mêmes fils, à la suite — reste à faire
  sur une machine libre. ⚠ La première tentative n'a pas abouti : 47 fenêtres seulement, donc
  dominées par la mise en route, et la seconde moitié refusée parce que le crop choisi était
  vide. Un débit mesuré sur quarante-sept fenêtres n'est pas un débit.

⚠ Ce n'est pas bloquant pour le Graal : la campagne livre ses quatre cartes dans tous les cas.
C'est une dette de compréhension, pas une dette de résultat, et elle est notée comme telle.

---

**Instruments** : [`src/encre/cout_de_la_fenetre.py`](../../src/encre/cout_de_la_fenetre.py)
(27 contrôles), [`src/figures/figure_hypothese_refutee.py`](../../src/figures/figure_hypothese_refutee.py)
(13 contrôles), [`src/encre/ab_segments.py`](../../src/encre/ab_segments.py) (12 contrôles),
[`src/encre/allure_du_rendu.py`](../../src/encre/allure_du_rendu.py) (21 contrôles).
**Mesures** : [`cout_de_la_fenetre.json`](../mesures/cout_de_la_fenetre.json),
[`ab_segments.json`](../mesures/ab_segments.json),
[`allure_du_rendu.json`](../mesures/allure_du_rendu.json).
**Voir aussi** : [`59`](59_la_campagne_plutot_que_le_rouleau.md) pour le coût d'un rendu,
[`60`](60_la_constante_qui_rendait_le_modele_muet.md) pour la garde de pile,
[`61`](61_les_batteries_qui_ne_pouvaient_pas_echouer.md) pour les vérifications incapables
d'échouer.
