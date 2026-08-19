# Écarter avant de payer — la première règle qui change une décision ✅ ⚠ *(à lire avec le §9)*

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

⚠ **Ce que ça ne fait pas** : ça n'améliore aucune trace, ça n'en déroule aucune. Une
règle de tri sépare ce qui va rater de ce qui va marcher ; elle ne répare rien. La
réparation est la voie J du batch (`18`), et son outil existe déjà.

## 8. Reproduire

```bash
cd inference_xpu
uv run python ../analysis/src/croiser_encre.py \
    ../docs/profondeur_corpus_2.4um.json ../data/encre/PHercParis4 \
    --grandeur avec_matiere --sens bas \
    --parts 0.05 0.10 0.15 0.20 0.25 0.30 0.40 0.50 \
    --out ../docs/decision_avec_matiere.json
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
