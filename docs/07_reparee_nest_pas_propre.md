# La réparation ne déplace pas le défaut : une mesure qui le montre

2026-08-17. Résultat sur PHercParis4 (Scroll 1), 46 traces mesurées.
Rejouable : `experiments/src/excision/{proximity,correlate}.py`.

> **En une phrase** : la réparation d'auto-intersection ramène les contacts à zéro
> et **ne change pas** la proximité anormale entre régions non adjacentes. La mesure
> corrèle fortement avec les croisements (rho 0,77, y compris à longueur contrôlée)
> mais **ne sépare pas** proprement les traces saines des réparées — c'est un
> indicateur continu, pas un classifieur.

---

## 1. Le dispositif, et pourquoi il est honnête

Trois traces du **même rouleau**, de **longueur quasi identique** (7,66 / 7,82 /
7,92 tours), donc le confond longueur/qualité identifié en `05` §1 est neutralisé
par construction. Deux d'entre elles couvrent **la même région** (`w038-045`) et
diffèrent d'un facteur **8** en nombre de croisements.

| trace | tours | croisements publiés | rôle |
|---|---|---|---|
| `20231022170901` | 7,66 | **0** | témoin : long **et** propre |
| `20260623143441-w038-045` | 7,82 | 52 | même région, peu atteinte |
| `20260701183126-w038-045` | 7,92 | **408** | même région, très atteinte |

⚠ Données vérifiées **par leur comportement** et non par un manifeste de hashes
(perdu à l'arrêt du récupérateur) : les comptes de triangles concordent exactement
avec la publication (1 047 154 · 3 615 528 · 5 850 912), et les contacts sur la
diagonale publiée aussi (1 584 · 11 673). C'est une vérification plus forte qu'une
somme de contrôle — elle prouve que la donnée est *juste*, pas seulement *intacte*.

## 2. La métrique ordonne correctement, à longueur contrôlée

`fraction_below_third` = part des cellules dont la distance à une partie **non
adjacente** vaut moins du tiers de l'espacement **local**.

| trace | croisements | espacement médian | cellules sous ⅓ |
|---|---|---|---|
| témoin | 0 | 160 µm | **0,09 %** |
| `w038-045` peu atteinte | 52 | 140 µm | 0,15 % |
| `w038-045` très atteinte | 408 | 138 µm | **0,37 %** |

Monotone avec le nombre de croisements, à longueur égale. La métrique mesure donc
la **qualité**, pas la longueur.

## 3. ⭐ Le test qui tranche : elle survit à la réparation

L'objection sérieuse était qu'une métrique de proximité **re-détecte simplement les
croisements** — un site de croisement *est* une approche rapprochée. Ce serait alors
une version dégradée du recensement, sans valeur propre.

Le test : mesurer la trace **réparée**, celle dont le recensement dit désormais zéro.

| état | recensement | espacement | cellules sous ⅓ |
|---|---|---|---|
| avant | **11 673 contacts**, *NOT clean* | 138 µm | 0,37 % |
| **après réparation** | **0 contact**, *clean* | 138 µm | **0,38 %** |
| témoin jamais atteint | 0 contact, *clean* | 160 µm | **0,09 %** |

La réparation retire **3 689 quads** (0,12 % de l'aire), fait tomber les contacts de
11 673 à **zéro**, et la métrique **ne bouge pas** (0,37 → 0,38 %).

> **Passer le recensement d'auto-intersection ne change rien à cette mesure.** La
> réparation ramène les contacts à zéro et laisse la proximité intacte.

C'est le résultat de `05` §4 généralisé : autre rouleau, trace entière, et cette
fois sur un vrai maillage réparé plutôt que sur des sites de croisement isolés.

### ⚠⚠ Correction : « quatre fois au-dessus d'une trace saine » était faux

Cette section a d'abord conclu que la trace réparée (0,38 %) valait **quatre fois**
une trace saine (0,09 %). C'était une comparaison à **un seul** témoin, qui se
trouvait être bas. Mesuré ensuite sur les **7 traces à zéro croisement** de Scroll 1
(mesure `06` 3.9) :

| population | médiane | étendue |
|---|---|---|
| zéro croisement (n = 7) | 0,090 % | **0,020 – 0,372 %** |
| avec croisements (n = 39) | 0,230 % | 0,040 – … |

Une trace parfaitement propre peut donc atteindre **0,372 %**, et la réparée
(0,38 %) est **à peine au-dessus**, pas hors norme. Les distributions se recouvrent :
seules **36 %** des traces atteintes dépassent la pire des saines.

**L'énoncé qui survit** : la réparation **ne déplace pas** la mesure (0,37 → 0,38 %),
donc la métrique voit quelque chose que le recensement ne voit pas. **L'énoncé qui
tombe** : que cette mesure sépare proprement « réparée » de « saine ». Elle ne le
fait pas — c'est un indicateur continu corrélé, pas un classifieur.

## 4. Pourquoi la mesure est construite ainsi

Trois décisions, chacune imposée par une erreur payée avant elle :

1. **Non adjacent se juge dans la PARAMÉTRISATION**, pas dans l'espace. Deux
   cellules voisines dans l'image sont censées être voisines en 3D ; les compter
   noierait le signal sous la continuité ordinaire de la surface.
2. **Normalisation par l'espacement LOCAL**, jamais par une constante. Mesuré :
   l'espacement va de 101 µm (p5) à 303 µm (p90) selon l'endroit, et croît de
   **28 %** du cœur vers l'extérieur (`05` §4bis, `06` 1.11). Une constante
   empruntée à un autre rouleau avait déjà produit une conclusion fausse.
3. **La médiane, pas la moyenne**, pour la référence locale : la grandeur cherchée
   est une queue basse, et une moyenne se laisse tirer par ce qu'on veut détecter.

Ni volume, ni modèle, ni étiquette : la trace seule suffit. Arbre k-d, 0,4 s de
construction sur 1,6 M de points.

## 4bis. La corrélation, sur 46 traces

La §2 portait sur 3 traces. Étendu à **toutes** les traces mesurables de Scroll 1
(46 sur 55 ; les 9 restantes couvrent moins d'un tour, donc ne peuvent pas revenir
près d'elles-mêmes) :

| corrélation de Spearman | rho | p |
|---|---|---|
| proximité ~ **croisements** | **+0,769** | 4,3e-10 |
| proximité ~ **longueur** | −0,232 | 0,12 *(non significatif)* |
| longueur ~ croisements | +0,050 | *le confond, ici absent* |

⚠ **Le confond de `05` n'existe pas dans Scroll 1** (rho = 0,05 entre longueur et
croisements). C'était une particularité de Scroll 5, où les seules traces longues
étaient aussi les seules automatiques.

À longueur contrôlée, par tercile de couverture :

| tercile | couverture | n | rho |
|---|---|---|---|
| 1 | 0,26 – 2,03 tours | 16 | **+0,820** |
| 2 | 2,03 – 3,97 tours | 15 | **+0,944** |
| 3 | 3,98 – 18,03 tours | 15 | **+0,739** |

Fort et significatif dans les trois. La métrique porte donc sur la **qualité**.

Rangs de Spearman et non Pearson : quelques traces portent des centaines de
croisements et la plupart aucun, donc une corrélation linéaire mesurerait surtout
la queue.

## 5. ⚠ Ce que ça ne prouve pas encore

- **La corrélation est établie (46 traces), la séparation ne l'est pas.** La
  métrique est un indicateur continu, pas un classifieur : voir la correction du §3.
- Un seul rouleau, une seule campagne de scan. Scroll 5 se comporte différemment
  (le confond y existe), donc rien ne dit que ces chiffres voyagent.
- **Le seuil d'un tiers est arbitraire.** Il n'a pas été réglé pour que les chiffres
  sortent bien — c'est la première valeur essayée — mais il n'est pas non plus
  justifié. À remplacer par une grandeur sans seuil, ou à calibrer sur une
  population.
- **On ne sait pas si ces approches nuisent au texte.** C'est la même frontière que
  `04` : on mesure une anomalie géométrique, pas une perte de lisibilité. Le lien
  reste à établir.
- **Aucun plancher** : les 7 traces à zéro croisement s'étalent de 0,020 % à
  0,372 %, un facteur 18. Ce que la mesure attrape sur une trace sans croisement
  reste inexpliqué — vraies approches légitimes, ou bruit de la mesure.

## 6. Ce que ça vaut pour le concours

Les critères des Progress Prizes demandent une **amélioration quantitative sur
données réelles**, sur un problème de la *wishlist*. Les problèmes ouverts nº3
(« détecter et réparer trous, fusions et sauts de spire **sans inspection
humaine** ») et nº7 (« **métriques d'évaluation** ») sont exactement ceci.

Et le résultat a la forme utile : il ne dit pas « notre outil est meilleur », il dit
**« la vérification que tout le monde utilise laisse passer quelque chose, voici la
mesure et voici le contrôle »**.

⚠ En l'état ce n'est pas encore soumissionnable : il manque le seuil non arbitraire
(`06` 3.7) et un second rouleau. Ce qui est acquis, c'est la mesure et son contrôle
négatif — pas encore un outil que quelqu'un d'autre voudrait lancer.

---

## 6. ⚠⚠ La référence locale : le défaut est réel, le remède de principe est faux

2026-08-18. `06` §3.2 avait établi que la ligne de base « locale » de `proximity.py`
n'est pas locale : ±150 colonnes couvrent **96,9 % d'un tour**, et le rayon y varie de
**8,62 mm**, soit 59,5 % de l'étendue radiale. Le constat tient. Ce qui suit est ce
qu'on en fait.

### Le remède évident, et sa mesure

La grandeur mesurée est une **distance 3D**, donc son voisinage de référence devrait
l'être — une boule est locale en rayon par construction, et n'exige pas de connaître
l'axe du rouleau (que `06` §2.3 n'a toujours pas établi). Sur les mêmes 46 traces,
même grandeur, seule la définition de la référence change :

| référence | rho ~ croisements | p | couverture |
|---|---:|---:|---:|
| colonnes ±50 | **+0,805** | 1,6e-11 | 100 % |
| colonnes ±100 | +0,793 | 5,3e-11 | 100 % |
| **colonnes ±150** *(actuelle)* | **+0,769** | 4,3e-10 | 100 % |
| colonnes ±20 | +0,765 | 5,8e-10 | 100 % |
| colonnes ±10 | +0,755 | 1,4e-09 | 100 % |
| boule 400 vx | +0,560 | 5,3e-05 | 100 % |
| boule 200 vx | +0,474 | 8,8e-04 | 94 % |
| boule 100 vx | +0,206 | 0,17 | 24 % |

**Le remède de principe rend la métrique nettement pire**, et les fenêtres en colonnes
forment un **plateau** de ±10 à ±150 : la largeur n'est pas le facteur limitant. Un
gain de +0,036 en passant de 150 à 50 ne vaut pas qu'on retienne 50 — ce serait
retenir la valeur qui a le mieux marché sur ces 46 traces, exactement le piège que
`06` §3.7 évite pour le seuil.

### Deux mesures, et non deux explications

**(1) La non-localité est sans conséquence.** Rapport boule/bande sur les cellules
ordinaires : **1,003** en médiane sur 10 traces. Les deux références donnent le même
espacement typique — donc l'espacement ne varie pas assez avec le rayon pour que la
largeur de la fenêtre compte. Le rayon varie beaucoup dans la fenêtre ; l'espacement,
non. C'est cohérent avec l'invariant fort de `11` §3 (rayon / feuilles constant à
**cv 1,8 %**), même si celui-là est mesuré sur un autre rouleau et le long de *z*.

**(2) Et la boule détruit le contraste, spécifiquement là où il est.** Rapport
boule/bande **aux cellules signalées** : **0,875**, sur **9 traces sur 10**. Un site de
croisement est une région 3D **compacte** où les cellules sont anormalement proches ;
une boule centrée dessus est donc remplie d'autres cellules du même site, la médiane
tombe à la valeur anormale, et **l'anomalie normalise sa propre référence**.

⚠ La bande de colonnes n'a pas ce défaut pour une raison précise : elle est **étroite
en colonne mais entière en ligne**. Elle traverse tout le segment, donc l'essentiel de
son contenu vient de régions saines même quand son centre est sur une anomalie.

> ⚠⚠ **La leçon, et elle dépasse ce fichier : une référence locale doit être LARGE
> dans la direction où l'anomalie est PETITE.** Être local dans toutes les dimensions
> de l'anomalie, c'est mesurer l'anomalie contre elle-même.

⚠ Une trace sur dix va dans l'autre sens (`20231031143852`, 1,127). Et l'ampleur —
12,5 % de baisse de référence — explique la **direction** du résultat ; qu'elle
suffise à expliquer la chute de rho de 0,805 à 0,560 n'est pas établi par cette
mesure seule.

### Reproduire

```bash
cd experiments
uv run python src/excision/baseline_sweep.py \
    ../repos/windcheck/data/scroll1_tifxyz ../docs/baseline_sweep_scroll1.jsonl
uv run python src/excision/variant_correlate.py \
    ../docs/baseline_sweep_scroll1.jsonl ../repos/windcheck/results/index.json
```
