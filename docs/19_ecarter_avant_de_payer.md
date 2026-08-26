# Écarter avant de payer — la première règle qui change une décision ✅ *(§9 corrigé au §10)*

2026-08-19. `00` §9 nommait le manque : *tous nos instruments jugent, aucun n'a encore
changé quoi que ce soit*. Et le tableau des goulots du concours demande, mot pour mot,
de la **détection conservative d'échec**.

Voici la règle, et ce qu'elle vaut.

> **Écarter les 20 % de segments dont le volume de surface contient le moins de matière
> fait monter le contraste d'encre médian du corpus de +0,381, contre un tirage au
> hasard de même effectif : p = 0,0005 sur 2000 permutations.**

Elle coûte **36 requêtes HTTP par segment**, se calcule **avant** toute inférence, et ne
demande ni vérité terrain, ni modèle, ni juge.

---

## 1. Le montage, et pourquoi il ne peut pas être circulaire

| pièce | d'où elle vient |
|---|---|
| la mesure de trace | notre lecteur Zarr, 36 fenêtres par segment |
| la cible | les **cartes d'encre publiées** par le concours, récupérées telles quelles |
| le témoin | 2000 permutations de même effectif |

⭐ **La cible est la sortie d'un autre pipeline.** Rien de notre chaîne n'entre dedans :
une corrélation ne peut donc pas être un artefact partagé. C'est ce qui distingue ce
résultat de tous les précédents, où l'instrument et la cible se touchaient quelque part.

⚠ **Le confond qu'il faut nommer et qu'aucune mesure ne lève ici** : une carte d'encre
vide peut vouloir dire « la trace a raté la feuille » **ou** « ce morceau de papyrus est
vierge ». Le résultat se lit donc comme un **tri de corpus**, jamais comme un diagnostic
sur un segment isolé.

## 2. Les grandeurs, et le seul seuil qu'on s'autorise : aucun

L'encre publiée est un rendu 8 bits d'une carte de probabilité. Mesurer « combien
d'encre » avec un seuil en niveaux de gris ne se transporterait pas d'un rendu à
l'autre — c'est la règle nº 1 du dépôt. Les quatre grandeurs sont donc des **moments**
ou des **rapports de centiles** :

| grandeur d'encre | ce qu'elle dit |
|---|---|
| `encre_moyenne`, `encre_ecart_type` | niveau et dispersion dans l'emprise |
| `encre_contraste_p90_p50` | ⭐ le haut de la distribution est-il loin du milieu — c'est la différence entre une carte **bimodale** (des lettres) et une carte **plate** (rien) |
| `encre_contraste_p99_p50` | la même, sur la queue extrême |

⚠ Le remplissage (valeur exactement nulle) est exclu de l'emprise : sinon un segment
étroit dans un grand canevas paraît vide alors qu'il est plein.

## 3. Ce qui corrèle — 20 croisements, seuil de Bonferroni à p < 0,0025

n = 80 segments de Scroll 1, qui ont **à la fois** un volume de surface mesuré et une
carte d'encre publiée. ⚠ À n = 80, la mesure détecte un rho de **0,31** à 80 % de
puissance.

| trace | encre | rho | p | tient Bonferroni |
|---|---|---:|---:|---|
| **`avec_matiere`** | `encre_contraste_p90_p50` | **+0,539** | 0,00000 | ✅ |
| `avec_matiere` | `encre_ecart_type` | +0,534 | 0,00000 | ✅ |
| `avec_matiere` | `encre_moyenne` | +0,487 | 0,00000 | ✅ |
| `avec_matiere` | `encre_contraste_p99_p50` | +0,398 | 0,00026 | ✅ |
| `ecart_a_la_trace` | `encre_contraste_p99_p50` | **−0,344** | 0,00176 | ✅ |
| `ecart_a_la_trace` | `encre_contraste_p90_p50` | −0,315 | 0,0044 | ❌ *(nominal seulement)* |
| `au_bord` | `encre_contraste_p99_p50` | −0,298 | 0,0073 | ❌ |
| `tiers_central`, `iqr` | (toutes) | ≤ 0,15 | ≥ 0,19 | ❌ |

Les signes sont ceux qu'on attend : **plus la trace porte de matière, plus la carte
publiée est bimodale ; plus le pic est loin de la trace, moins elle l'est.**

## 4. ⚠⚠ Le confond de taille était RÉEL — et la partielle le montre

Un gros segment a plus de place pour porter de l'encre. Il fallait donc fermer le
triangle **des deux côtés**, pas d'un seul :

| branche mesurée | rho | p |
|---|---:|---:|
| emprise → `ecart_a_la_trace` | **+0,384** | 0,0004 |
| emprise → `encre_moyenne` | **+0,463** | 0,00000 |
| emprise → `encre_contraste_p90_p50` | +0,101 | 0,373 |
| emprise → `avec_matiere` | +0,189 | 0,093 |

**Les deux branches existent.** Une corrélation trace ↔ encre pouvait donc n'être qu'un
détour par la taille. La corrélation **partielle**, emprise retirée en rangs, tranche :

| couple | brut | **partiel** |
|---|---:|---:|
| `ecart_a_la_trace` × `encre_contraste_p90_p50` | −0,315 | **−0,382** (p = 0,0005) |
| `ecart_a_la_trace` × `encre_contraste_p99_p50` | −0,344 | −0,273 (p = 0,014) |
| `avec_matiere` × `encre_contraste_p90_p50` | +0,539 | **+0,561** (p < 1e-6) |

> ⭐ **Retirer le confond RENFORCE les deux relations principales au lieu de les
> dissoudre.** C'est le contraire de ce qu'on observe quand une corrélation n'est qu'un
> effet de taille — et c'est pour ça qu'il fallait la calculer plutôt que l'invoquer.

⚠ La seule qui s'affaiblit est `p99_p50` (−0,344 → −0,273), et sa raison est visible
dans le tableau ci-dessus : l'emprise la tire **négativement** (−0,257), donc elle
gonflait le brut. Elle reste significative, mais c'est `p90_p50` qu'il faut citer.

## 5. ⭐⭐ La décision, et sa forme

Écarter la pire fraction, mesurer le contraste d'encre médian de ce qui reste, comparer
à **2000 tirages au hasard de même effectif**. ⚠ Huit fractions testées, donc le seuil
qui compte est **0,05 / 8 = 0,0063**.

| écartés | gardés | avant | après | gain | témoin p95 | p |
|---:|---:|---:|---:|---:|---:|---:|
| 5 % | 76 | 5,061 | 5,178 | +0,117 | 5,178 | 0,054 |
| 10 % | 72 | 5,061 | 5,308 | +0,247 | 5,178 | 0,0075 |
| **15 %** | 68 | 5,061 | 5,361 | +0,300 | 5,260 | **0,0010** ✅ |
| **20 %** | 64 | 5,061 | **5,442** | **+0,381** | 5,260 | **0,0005** ✅ |
| **25 %** | 60 | 5,061 | **5,442** | **+0,381** | 5,308 | **0,0005** ✅ |
| 30 % | 56 | 5,061 | 5,361 | +0,300 | 5,333 | 0,0255 |
| 40 % | 48 | 5,061 | 5,480 | +0,419 | 5,361 | 0,0015 ✅ |
| 50 % | 40 | 5,061 | 5,456 | +0,395 | 5,402 | 0,0250 |

⭐ **C'est la FORME qui défend la règle, pas le meilleur chiffre.** Un plateau contigu à
15–25 %, encadré par une fraction trop faible qui ne fait rien (5 %, p = 0,054) et une
trop forte qui se dégrade (30 %). Un réglage sur-ajusté ferait un **pic** ; c'est le même
critère qui a défendu le seuil d'un tiers de `07` §8.

⚠⚠ **Et ce paragraphe ne tient plus tel quel — voir le §9.** Le contrôle de robustesse,
fait quelques heures plus tard, montre que **ce plateau est une propriété de la grille de
sondage** et non du phénomène : mesuré avec l'autre grille, il disparaît. Ce qui survit
est le **sens** de l'effet, pas le seuil. Le tableau ci-dessus reste exact ; c'est son
interprétation qui a été trop large.

### Le critère perdant, gardé parce qu'il informe

Avec `ecart_a_la_trace` comme critère, le gain **croît de façon monotone** avec la
fraction écartée (+0,199 → +0,500) et le p ne fait pas de plateau. C'est la signature de
« j'en jette plus, donc je garde les meilleurs », pas celle d'un point de coupure.
Avec `tiers_central`, la règle s'effondre au-delà de 25 % (p = 0,10 puis 0,14).

> **Trois critères, trois formes différentes.** Le seul qui produise un plateau est celui
> dont la corrélation partielle est la plus forte. Les deux faits sont indépendants et
> ils se répondent.

## 6. Pourquoi `avec_matiere` et pas l'écart, alors que `12` avait misé sur l'écart

`12` cherchait *à quelle profondeur* la matière est, en supposant qu'elle est là.
`avec_matiere` demande d'abord **s'il y en a**. Sur un volume de surface, une fenêtre
sans matière veut dire que la trace passe à travers du vide — et sur Scroll 4, `12` avait
déjà mesuré que **61 %** des fenêtres ont leur pic à un bord.

⚠ **Ce que cette grandeur pourrait être d'autre, dit franchement** : le nombre de
fenêtres non vides dépend aussi de la **forme de la bande dans son canevas**. Son confond
d'emprise n'est pas significatif (+0,189, p = 0,093), donc ce n'est pas « les gros
segments gagnent » — mais une bande très tordue échantillonne mal, et rien ici ne sépare
« tordue » de « hors feuille ». Les deux sont des difficultés de trace ; la règle les
traite pareil, et c'est assumé.

## 7. Ce que ça vaut pour le concours

| leur goulot | ce qu'on apporte |
|---|---|
| *conservative failure detection* | une règle **mesurée contre un témoin**, avec sa forme et son seuil |
| *scan-quality metrics* | `separabilite_scan.py` et la carte des 13 (`16`) |
| coût | **36 requêtes** par segment, ~2,6 s à 16 fils, **avant** l'inférence |

⚠ **Trois nombres circulent dans ce document pour des grandeurs voisines** — **36**
requêtes/fenêtres, **50** (`sondees` dans `docs/mesures/profondeur_corpus_2.4um.json`), et **72**
(le treillis 6 × 12 de la campagne **fibres**). Ils ne décrivent pas la même chose, et le
document ne le dit nulle part. ⏳ À démêler en une passe :
`src/graine/compter_corpus.py` donne les comptes réels par artefact.

⚠ **Ce que ça ne fait pas** : ça n'améliore aucune trace, ça n'en déroule aucune. Une
règle de tri sépare ce qui va rater de ce qui va marcher ; elle ne répare rien. La
réparation est la voie J du batch (`18`), et son outil existe déjà.

## 8. Reproduire

```bash
cd inference_xpu
uv run python ../src/encre/croiser_encre.py \
    ../docs/mesures/profondeur_corpus_2.4um.json ../data/encre/PHercParis4 \
    --grandeur avec_matiere --sens bas \
    --parts 0.05 0.10 0.15 0.20 0.25 0.30 0.40 0.50 \
    --out ../docs/mesures/decision_avec_matiere.json
```

⚠ `--depuis <rapport.json>` reprend un rapport déjà écrit au lieu de relire les images :
les cartes pèsent jusqu'à 99 Mpx et une relecture coûte dix minutes sans rien mesurer de
neuf.


---

## 9. ⚠⚠ Le contrôle de robustesse, et il affaiblit ce document

*(ajouté quelques heures après le reste, le 2026-08-19)*

La règle repose sur `avec_matiere` — la part de fenêtres **sondées** qui contiennent du
papyrus. Un relecteur posera immédiatement la bonne objection : **cette part dépend d'une
grille de sondage.** Si elle en dépendait beaucoup, la règle trierait des grilles et non
des traces.

Le test ne coûtait rien, parce que **deux échantillonneurs différents avaient déjà mesuré
les mêmes 80 segments**, sans que ce soit prévu :

| outil | grille | part de matière médiane |
|---|---|---:|
| `zarr_depth.py` | treillis 6 × 12, **72 points** | 48,0 % |
| `champ_correction.py` | repérage **10 × 20**, 200 points | 32,4 % |

### Ce que la comparaison dit

**Accord des classements : rho = +0,280** (p = 0,012), contre un témoin de 1000
permutations dont le |rho| p95 vaut **0,219**.

> ⭐ **La grandeur est bien une propriété du segment** — elle bat le hasard.
> ⚠ **Mais faiblement.** Un rho de 0,28 veut dire que les deux grilles sont largement en
> désaccord sur *quels* segments sont les pires.

### Et la question qui compte : la règle tient-elle avec l'AUTRE grille ?

Même corpus, même cible, même témoin de permutation — seul le **critère** change de
source :

| écartés | grille A (celle du §5) | **grille B** |
|---:|---:|---:|
| 10 % | +0,247 · p = **0,0075** | +0,199 · p = 0,0425 |
| 15 % | +0,300 · p = **0,0010** | +0,199 · p = 0,082 |
| 20 % | +0,381 · p = **0,0005** | +0,247 · p = 0,042 |
| 25 % | +0,381 · p = **0,0005** | +0,247 · p = 0,073 |
| 30 % | +0,300 · p = 0,026 | +0,300 · p = 0,026 |

> ⚠⚠ **La direction réplique, la force non.** Les **dix** gains sont positifs et tous les
> p sont sous 0,09 — mais la grille B perd **un ordre de grandeur** de significativité, et
> **aucun** de ses seuils ne survivrait à la correction de Bonferroni sur cinq fractions
> (p < 0,01).
>
> ⚠⚠ **Et le plateau de 15–25 % est une propriété de la grille A, pas du phénomène.**
> C'était l'argument principal du §5. Il ne tient plus tel quel.

### Ce qu'il faut donc dire, et ne pas dire

| ✅ soutenable | ❌ plus soutenable |
|---|---|
| écarter les segments les plus pauvres en matière **améliore** ce que le corpus rend | « le seuil de 20 % est le bon » |
| le sens de l'effet réplique sur deux échantillonneurs indépendants | « p = 0,0005 », sans dire lequel des deux critères |
| `avec_matiere` mesure une propriété du segment | qu'il la mesure **précisément** |

⚠ Une part de l'atténuation est **attendue** : les deux grilles n'ont ni le même nombre de
points (72 contre 200) ni la même couverture, donc chacune porte sa propre erreur
d'échantillonnage, et deux mesures bruitées corrèlent toujours moins que les grandeurs
qu'elles estiment. Ça explique une partie de +0,280 — **pas** le fait que le plateau
disparaisse.

### La suite que ça désigne

Ce n'est pas un échec, c'est un **cadrage** : la règle est réelle et son critère est
bruité. Le remède est de mesurer `avec_matiere` **mieux**, pas de choisir la grille qui
donne le meilleur p — ce dernier serait exactement le sur-ajustement que ce dépôt refuse
partout ailleurs. La voie évidente est un sondage plus dense, et son coût est connu :
200 fenêtres au lieu de 72, soit **~4 s de plus par segment** à 16 fils.


---

## 10. ⚠⚠ Le §9 était FAUX — je comparais deux grandeurs différentes

*(quelques heures plus tard, le 2026-08-19, une fois la campagne dense revenue)*

Le §9 concluait que le critère `avec_matiere` n'était que « modérément reproductible »
(rho **+0,280**) et que le plateau de 15–25 % était une propriété de la grille. **Les deux
affirmations sont fausses**, et l'erreur est la mienne.

### L'erreur

Je comparais `zarr_depth.avec_matiere / sondees` à `champ_correction.avec_matiere /
sondees`. Le second **n'est pas la même grandeur** : il mélange la passe de **repérage**
(répartie sur le canevas) et les **blocs**, qui sont posés *sur* la matière par
construction. Son dénominateur contient donc des points choisis pour toucher, et son
numérateur aussi. Ce n'est pas un échantillonnage neutre, c'est un mélange.

⚠ Rien dans les chiffres ne le criait : 48 % contre 32 % ressemble parfaitement à deux
grilles qui échantillonnent différemment.

### La comparaison propre

**Même outil, même définition, densité 5,4× différente** — 72 points contre 392 :

| | médiane | accord des classements |
|---|---:|---:|
| `zarr_depth`, 72 points | 48,0 % | — |
| `zarr_depth`, **392 points** | 73,3 % | **rho +0,841** (p = 1,7e-22) |

Témoin de permutation : |rho| p95 = 0,223. **+0,841 contre 0,223** — ce n'est pas
« modérément » reproductible, c'est très reproductible.

⚠ La médiane monte avec la densité (48 % → 73 %), et c'est **attendu** : un maillage plus
fin trouve la bande là où un maillage grossier passe à côté. La **valeur absolue** dépend
donc de la grille ; le **classement**, qui est ce que la règle utilise, non.

### Et la règle, rejouée sur la mesure dense

| écartés | grille 72 points (§5) | **dense, 392 points** |
|---:|---:|---:|
| 5 % | 0,054 | 0,054 |
| 10 % | 0,0075 | 0,0075 |
| **15 %** | **0,0010** | **0,0010** |
| **20 %** | **0,0005** | **0,0005** |
| **25 %** | **0,0005** | **0,0030** |
| 30 % | 0,0255 | 0,0255 |
| 40 % | 0,0015 | 0,0015 |
| 50 % | 0,0250 | 0,0010 |

> ⭐ **Le plateau de 15–25 % survit intact à un quintuplement de la densité de sondage.**
> Le §5 tenait ; c'est le §9 qui était de trop.

### Ce qui reste vrai du §9, et ce qui tombe

| ✅ garde | ❌ retire |
|---|---|
| qu'il fallait tester la dépendance à la grille | que le critère soit instable |
| que la mesure de `champ_correction` n'est pas comparable telle quelle | que le plateau soit un artefact de grille |
| ⚠ qu'un sampler d'un **autre genre** (aléatoire, non-treillis) reste non testé | — |

⚠ **La leçon, et elle vaut plus que la correction** : un contrôle de robustesse doit
d'abord prouver qu'il compare **la même grandeur**. J'ai passé une heure à affaiblir un
résultat juste, sur un contrôle faux — et l'affaiblir semblait être la position prudente,
ce qui est exactement ce qui l'a rendu difficile à voir. La prudence n'est pas une
méthode.

---

## 11. ⚠⚠ Ce que la règle sépare vraiment — et pourquoi elle ne réplique pas sur Scroll 5

*(2026-08-19, batch `22` voie P)* La règle reposait sur **un** corpus. Répliquée sur
PHerc0172 (53 segments, 7,91 µm, cartes d'encre publiées, même définition de
`avec_matiere`), elle **ne tient pas** :

| | Scroll 1 (n = 80) | Scroll 5 (n = 53) |
|---|---:|---:|
| `avec_matiere` × contraste d'encre | **+0,539** (p < 1e-6) | **−0,217** (p = 0,118) |
| décision, 20 % écartés | +0,381 · **p = 0,0005** | −0,020 · p = 0,84 |
| corrélations passant Bonferroni | 5 / 20 | **0 / 20** |

Le premier réflexe serait de dire que la règle est une propriété de Scroll 1. **Deux
mesures disent autre chose, et il faut les deux.**

### 11.1 La cible de Scroll 5 n'a presque rien à prédire

| corpus | contraste d'encre p10 → p90 | **étendue relative** |
|---|---|---:|
| Scroll 1 | 1,25 → 6,36 (facteur **5,1**) | **1,008** |
| Scroll 5 | 2,20 → 2,76 (facteur **1,25**) | **0,220** |

> **Les cartes d'encre publiées de Scroll 5 se ressemblent toutes.** L'étendue de la
> grandeur à expliquer y est **4,6 fois** plus petite. À n = 53 la mesure détecterait un
> rho de 0,37, et elle rend −0,217 : le résultat est **non concluant**, pas réfutant.

⚠ Et le prédicteur, lui, varie normalement (étendue relative 0,228 contre 0,333). C'est
bien la **cible** qui est plate, pas la mesure.

### 11.2 ⚠⚠ Et sur Scroll 1, la règle sépare une CLASSE, pas un gradient

C'est la mesure qui compte, et elle n'avait pas été faite. Sur Scroll 1, **14 segments
sur 80** ont un contraste d'encre sous 2,5 — c'est-à-dire une carte quasi plate. En les
retirant :

| corpus | rho `avec_matiere` × encre | p |
|---|---:|---:|
| les 80 | **+0,539** | < 1e-6 |
| les 66 au-dessus de 2,5 | +0,249 | 0,044 |
| les 64 au-dessus de 3,0 | **+0,190** | **0,132** |
| les 58 au-dessus de 4,0 | +0,157 | 0,239 |

> ⭐ **La corrélation est portée par une poignée de segments quasi vierges.** Parmi les
> segments qui portent réellement de l'encre, la relation est **faible et non
> significative**. Ce que `avec_matiere` détecte n'est pas « un peu plus ou un peu moins
> d'encre » — c'est **une classe d'échecs**.

### 11.3 Les deux mesures se répondent

Le corpus entier de Scroll 5 se tient entre 2,20 et 2,76, c'est-à-dire **dans la plage que
Scroll 1 appelle « quasi vierge »**. Il n'y a donc **aucune classe à séparer** : ni des
segments qui portent du texte, ni des segments qui n'en portent pas — tout y ressemble à
la seconde catégorie.

⚠ Deux lectures restent possibles et rien ici ne les départage : soit la détection d'encre
de ce corpus rend une sortie plate partout, soit le rendu 8 bits n'est pas comparable d'un
corpus à l'autre. **La seconde suffirait à interdire toute comparaison de contraste absolu
entre rouleaux** — ce que la règle nº 1 du dépôt dit déjà.

### 11.4 Ce qu'on a le droit d'affirmer, réécrit

| ✅ soutenable | ❌ plus soutenable |
|---|---|
| sur Scroll 1, `avec_matiere` **identifie une classe** de segments dont la carte d'encre publiée est quasi plate — 14 sur 80 | que la règle améliore un corpus **en général** |
| écarter les 20 % les plus pauvres retire des membres de cette classe, d'où le gain | qu'elle réplique sur un autre rouleau |
| c'est de la **détection conservative d'échec**, ce que le concours demande mot pour mot | que ce soit un gradient de qualité |
| ⚠ la relation **dans** les segments porteurs d'encre est faible (+0,19, ns) | — |

⭐ **Et c'est une meilleure revendication que la précédente**, pas une moins bonne : « je
repère une classe d'échecs avant que vous payiez l'inférence » est exactement le goulot
que le concours nomme, alors que « j'améliore une médiane » aurait toujours pu n'être
qu'un effet de tri.

### 11.5 Ce que ça n'a pas encore tranché

⚠ Scroll 5 est à **7,91 µm** quand Scroll 1 est à **2,4 µm** : la résolution est confondue
avec le rouleau. **PHerc1667 et PHerc0139 publient tous deux à 2,399 µm** — c'est le test
apparié qui sépare « la règle est propre à Scroll 1 » de « la règle demande une résolution
fine ». Les campagnes tournent.

---

## 12. ⚠⚠ Le test apparié RÉFUTE l'explication du §11 — et la règle est propre à Scroll 1

*(même jour, une heure plus tard)* Le §11.5 disait que la résolution restait confondue
avec le rouleau, et que PHerc0139 et PHerc1667 — tous deux à **2,399 µm** — trancheraient.
Ils ont tranché, et pas dans le sens que le §11 espérait.

| corpus | n | voxel | **étendue relative de la cible** | rho `avec_matiere` × encre | détectable |
|---|---:|---:|---:|---:|---:|
| **Scroll 1** | 80 | 2,4 µm | 1,008 | **+0,539** (p < 1e-6) | 0,31 |
| **PHerc0139** | 38 | **2,399 µm** | **1,628** | **−0,229** (p = 0,17) | 0,44 |
| PHerc1667 | 19 | 2,399 µm | 0,720 | +0,425 (p = 0,070) | 0,60 |
| PHerc0172 | 53 | 7,91 µm | 0,220 | −0,217 (p = 0,12) | 0,37 |

### Ce que ça détruit

Le §11 expliquait l'échec par un **effet de plancher** : la cible de Scroll 5 varie 4,6
fois moins, donc il n'y a rien à prédire. C'était vrai **pour Scroll 5 seulement**.

> ⚠⚠ **PHerc0139 a une étendue relative de 1,628 — plus GRANDE que celle de Scroll 1
> (1,008) — 17 de ses 38 segments sont sous un contraste de 2,5, et il rend quand même
> le signe OPPOSÉ.** L'effet de plancher n'explique rien là. Mon explication du §11
> couvrait un corpus sur trois et je l'avais écrite comme si elle les couvrait tous.

### Ce que ça laisse

Deux corpus à **la même résolution**, tous deux avec assez d'étendue, rendent **+0,539** et
**−0,229**. Aucun des trois négatifs n'est individuellement significatif — mais le motif
d'ensemble (un positif fort, trois non-positifs) est **exactement** celui des fibres
(+0,330 à n = 12, **−0,192** à n = 54) et du détecteur de phase.

> **La règle est une propriété du corpus publié de Scroll 1, pas du problème.**

⚠ Elle reste solide **sur Scroll 1** — elle y passe Bonferroni sur 20 croisements, survit
à un quintuplement de la densité de sondage, et bat 2000 permutations. Ce qui tombe n'est
pas la mesure, c'est sa **portée**.

### Pourquoi ça pouvait arriver, sans que ça excuse quoi que ce soit

Quatre corpus, quatre groupes de traceurs, quatre modèles d'encre, quatre états de
conservation. N'importe lequel suffirait. ⚠ Et c'est précisément le point : **une règle
qui dépend du corpus n'est pas une règle sur les traces.**

### Ce qu'il faut écrire dans la soumission

| ✅ | ❌ |
|---|---|
| sur les 80 segments de Scroll 1, `material` identifie une classe d'échecs (14 quasi vierges), p = 0,0005 contre permutation | que ce soit un instrument général |
| la mesure coûte 300 requêtes et se calcule avant l'inférence | qu'elle réplique — **elle ne réplique pas**, testé sur 110 segments de plus |
| ⭐ **et les trois corpus où elle échoue sont publiés avec le résultat** | de choisir le corpus qui marche |

⭐ Publier les quatre est ce qui rend la soumission utilisable : quelqu'un qui reprend la
mesure saura tout de suite qu'elle doit être re-validée sur son corpus, au lieu de le
découvrir après.
