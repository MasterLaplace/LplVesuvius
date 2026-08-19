# Le batch « produire » — passer du jugement à la décision

2026-08-19. Le batch précédent (`13`) a fermé ce qui était ouvert. Ce qu'il a laissé
derrière lui n'est pas une liste de tâches, c'est **une remarque sur la nature de tout
ce qu'on a construit**, écrite dans `00` §9 :

> Tous nos instruments **jugent**. Aucun n'a encore **changé** quoi que ce soit.

La profondeur de surface dit qu'une trace est décalée de 63 µm. La séparabilité dit
qu'un scan résout mal. La proximité dit qu'une trace se recoupe mal. Trois verdicts,
zéro conséquence. Or le tableau des goulots du concours ne demande pas des verdicts, il
demande deux choses nommées :

| ce que le concours écrit | ce qu'on a | ce qui manque |
|---|---|---|
| *scan-quality metrics* | ✅ `separabilite_scan.py`, carte des 13 | — |
| *conservative failure detection* | ⚠ on **détecte**, on n'**écarte** pas | une règle, et la preuve qu'elle bat le hasard |

Et l'objectif de l'auteur — **le rouleau déroulé, pas le texte lu** — pointe encore plus
loin : au-delà d'écarter ce qui va rater, **réparer**.

---

## Voie I — l'instrument change une décision ⭐⭐

Ferme `00` §9.2. La décision la plus simple qui soit : *écarter les segments dont
l'écart pic↔trace est le plus grand améliore-t-il ce que le corpus rend ?*

⭐ **La cible est une carte d'encre PUBLIÉE**, donc la sortie d'un **autre** pipeline,
récupérée telle quelle. Rien de notre chaîne n'entre dedans : une corrélation ne peut
pas être un artefact partagé.

⚠ **Le confond est nommé, pas caché** : une carte vide peut vouloir dire « la trace a
raté la feuille » *ou* « ce papyrus est vierge ». Aucune mesure ne les sépare ici — donc
le résultat se lit comme un **tri de corpus**, jamais comme un diagnostic de segment.

⚠⚠ **Le témoin est une permutation.** Écarter un quart d'un corpus déplace presque
toujours une médiane ; la question est de savoir si ça la déplace **plus qu'un tirage au
hasard de même taille**. Sans lui, la vérification ne peut pas échouer.

| # | quoi | état |
|---|---|---|
| I1 | outil : `analysis/src/croiser_encre.py` | ✅ écrit |
| I2 | corréler 5 grandeurs de trace × 4 grandeurs d'encre, n = 80 | ✅ **`19`** — 5 couples tiennent Bonferroni, `avec_matiere` en tête (+0,539) |
| I3 | le confond d'emprise mesuré à côté | ✅ dans l'outil |
| I4 | la décision, contre 2000 permutations | ✅ **+0,381, p = 0,0005** en écartant 20 % |
| I5 | le seuil défendu par un **plateau**, pas par un pic | ✅ plateau contigu **15–25 %**, encadré par 5 % qui ne fait rien et 30 % qui se dégrade |

## Voie J — le champ de correction ⭐⭐ *(produire)*

Ferme `00` §9.3 et **remplace la voie D** (`13`), qui demandait la même chose pour le
seul Scroll 4.

⚠⚠ **La distinction que `12` ne pouvait pas faire.** Un segment à ±60 µm autour de 63 et
un segment uniformément à 63 rendent la **même médiane**. Le premier a sauté de feuille
et rien ne le rattrape ; le second est mal posé et une translation le répare. C'est cette
différence-là qui décide si on jette ou si on corrige.

Trois grandeurs, sur des **blocs contigus** de fenêtres :

- `decalage_median` — la translation qui minimise l'écart ;
- `residuel` — ce qui **reste après** cette translation, donc le vrai coût ;
- `coherence_voisins` — l'écart d'une fenêtre prédit-il celui de sa voisine.

⚠ Voisin *de grille* = voisin *sur la feuille*, parce qu'un volume de surface est déjà
paramétré. Et le témoin est un **mélange** des mêmes écarts : s'il ne s'effondre pas, la
cohérence vient de la façon de compter et pas de la géométrie.

| # | quoi | état |
|---|---|---|
| J1 | outil : `analysis/src/champ_correction.py` | ✅ écrit |
| J2 | ⚠ échantillonnage : **trouver la matière avant de la sonder** (6 fenêtres utiles sur 96 sans ça) | ✅ passe de repérage |
| J3 | campagne sur les 80 segments de Scroll 1 | ✅ **80/80** battent leur témoin (p = 1,3e-25). `20` |
| J4 | la même sur Scroll 4 | ✅ **19/19** (p = 7,4e-08). ⚠ Le segment `20231111135340`, celui des 61 % au bord, **n'a pas de volume de surface publié** — mesuré sur les 19 qui en ont un |
| J5 | corréler `residuel` et `coherence` aux croisements publiés | ✅ **résiduel +0,428** (p = 0,0012) contre les croisements, **−0,028** contre l'encre. Un défaut de la TRACE, pas du RÉSULTAT |
| J6 | **appliquer** la translation et re-mesurer | ❌ **écarté avec la raison** : la mesure dit qu'une translation n'enlèverait que **21,7 %** de l'erreur (35,3 % sur Scroll 4). Le bon remède est un **gauchissement**, pas une translation — l'implémenter aurait été construire le mauvais outil |

## Voie K — l'échelle, réellement ⭐

Ferme `13` G3, qui disait « la structure le permet, rien ne le fait ».

| # | quoi | état |
|---|---|---|
| K1 | paralléliser le lecteur Zarr | ✅ **×8,35 mesuré** (21,80 s → 2,61 s), sortie **bit-pour-bit identique** au sérialisé |
| K2 | ⚠ le contrôle : `executor.map` rend dans l'ordre des **entrées** — c'est la seule propriété qui rend la version parallèle substituable | ✅ |
| K3 | rejouer le chiffrage de `13` §G avec la vitesse réelle | ✅ **0,9 h pour les 800 rouleaux** (contre 0,5 h annoncé par un modèle qui divisait par 16) |
| K4 | passer l'instrument sur un rouleau **jamais tracé** | ✅ **déjà fait par `16`** : les 13 rouleaux du prix n'ont aucune trace, et la métrique de séparabilité les juge quand même |

## Voie L — la phase, au niveau fin

`17` s'est conclu par un **échec** : l'effet fond quand n monte (+0,52 → +0,31 → +0,15
de n = 8 à 38). Une seule suspicion restait, et elle est testable : la campagne tournait
au **niveau 3**, où huit cellules de maillage partagent un voxel de phase — donc la
plupart des pas sont nuls **par construction**.

| # | quoi | état |
|---|---|---|
| L1 | rejouer une trace au niveau 1 | ❌ **impossible** : le volume `cos` n'est publié qu'aux niveaux **3, 4, 5**. Le niveau 3 EST le plus fin |
| L2 | si les marches bougent : rejouer les 38 | ➡️ sans objet |
| L3 | l'échec est **définitif** | ✅ `17` §10, et mesuré : marche médiane **12,2 / 255**, **0 trace sur 38** à médiane nulle. La quantification n'écrase rien |

## Voie M — les restes de géométrie

| # | quoi | état |
|---|---|---|
| M1 | vrai **ombilic** | ❌ **le fichier n'existe pas** (zéro occurrence sur les 4 corpus). Remplacé par une **analyse de sensibilité** — 🔄 au niveau 0. ⚠ La version niveau 2 est **invalide** : les seuils y comptent 42 feuilles au lieu de 176 |
| M2 | plus de bandes **niveau 0** (2 faites : une migre, une non) | ⏳ |
| M3 | **ESRF 2,4 µm** sur les 4 sites (`06` §3.6) | ⏳ |

## Voie N — cohérence de la doc

| # | quoi | état |
|---|---|---|
| N1 | `00` §9.5 périmé | ✅ corrigé — et c'était **le rayon, pas la résolution** |
| N2 | `13` : voies A, C, G, H à clore | ✅ les **huit** voies closes |
| N3 | `HANDOFF` refait | 🔄 §2, §2bis, §3, §4 faits ; §5 et §7 restent |
| N4 | `tools/temoins.sh` | ✅ **13 contrôles de plus, 79 au total**, dont l'ordre du parallélisme et le cas négatif de la décision |


---

## Voie O — le contrôle de robustesse, et ce qu'il impose ⚠⚠

*(ouverte le 2026-08-19, après coup, parce que la mesure l'a réclamée)*

`19` §9 : le critère `avec_matiere` n'est que **modérément** reproductible d'une grille de
sondage à l'autre (rho **+0,280**, témoin 0,219). La règle survit en **direction** — dix
gains positifs sur dix, deux échantillonneurs — mais **le plateau qui défendait le seuil
de 20 % est une propriété de la grille, pas du phénomène**.

⚠ **Le remède qu'on s'interdit** : choisir la grille qui donne le meilleur p. Ce serait
exactement le sur-ajustement que ce dépôt refuse partout ailleurs.

| # | quoi | état |
|---|---|---|
| O1 | comparer les deux grilles existantes | ✅ rho +0,280 (p = 0,012) contre témoin 0,219 |
| O2 | rejouer la décision avec l'**autre** critère | ✅ direction tenue, **significativité divisée par ~10**, plateau perdu |
| O3 | mesurer `avec_matiere` avec un sondage **dense** (392 points au lieu de 72) | 🔄 campagne lancée |
| O4 | l'accord des grilles monte-t-il avec la densité ? | ⏳ c'est la prédiction que O3 teste |
| O5 | si oui, refaire la décision sur la mesure dense et **re-défendre** un seuil | ⏳ |

⭐ Ce qui rend O4 falsifiable : si l'accord ne monte **pas** avec la densité, alors ce
n'est pas de l'erreur d'échantillonnage — c'est que les deux grilles mesurent des choses
différentes, et il faudra dire lesquelles au lieu d'en moyenner.
