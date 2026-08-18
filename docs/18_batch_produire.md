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
| I2 | corréler 5 grandeurs de trace × 4 grandeurs d'encre, n = 80 | 🔄 |
| I3 | le confond d'emprise mesuré à côté | ✅ dans l'outil |
| I4 | la décision, contre 2000 permutations | 🔄 |
| I5 | le seuil défendu par un **plateau**, pas par un pic | ⏳ |

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
| J3 | campagne sur les 80 segments de Scroll 1 | 🔄 |
| J4 | la même sur Scroll 4, dont `12` dit que la trace n'est sur aucune feuille | ⏳ |
| J5 | corréler `residuel` et `coherence` aux croisements publiés | ⏳ |
| J6 | **appliquer** la translation et re-mesurer : l'écart tombe-t-il ? | ⏳ |

## Voie K — l'échelle, réellement ⭐

Ferme `13` G3, qui disait « la structure le permet, rien ne le fait ».

| # | quoi | état |
|---|---|---|
| K1 | paralléliser le lecteur Zarr | ✅ **×8,35 mesuré** (21,80 s → 2,61 s), sortie **bit-pour-bit identique** au sérialisé |
| K2 | ⚠ le contrôle : `executor.map` rend dans l'ordre des **entrées** — c'est la seule propriété qui rend la version parallèle substituable | ✅ |
| K3 | rejouer le chiffrage de `13` §G avec la vitesse réelle | ⏳ |
| K4 | passer l'instrument sur un rouleau **jamais tracé** — le cas des 800 | ⏳ |

## Voie L — la phase, au niveau fin

`17` s'est conclu par un **échec** : l'effet fond quand n monte (+0,52 → +0,31 → +0,15
de n = 8 à 38). Une seule suspicion restait, et elle est testable : la campagne tournait
au **niveau 3**, où huit cellules de maillage partagent un voxel de phase — donc la
plupart des pas sont nuls **par construction**.

| # | quoi | état |
|---|---|---|
| L1 | rejouer une trace au niveau 1, comparer les marches | ⏳ |
| L2 | si les marches bougent : rejouer les 38 | ⏳ |
| L3 | sinon : l'échec est **définitif**, et c'est écrit | ⏳ |

## Voie M — les restes de géométrie

| # | quoi | état |
|---|---|---|
| M1 | vrai **ombilic** — ⚠ 404 à l'adresse notée dans `06` | ⏳ |
| M2 | plus de bandes **niveau 0** (2 faites : une migre, une non) | ⏳ |
| M3 | **ESRF 2,4 µm** sur les 4 sites (`06` §3.6) | ⏳ |

## Voie N — cohérence de la doc

| # | quoi | état |
|---|---|---|
| N1 | `00` §9.5 cite encore `+0,284` sans la correction par le rayon physique, et annonce une vérification « lancée » qui a rendu | ⏳ |
| N2 | `13` : voies A, C, G, H à clore | ⏳ |
| N3 | `HANDOFF` §7 : la table « ce qui reste » à refaire | ⏳ |
| N4 | `tools/temoins.sh` : un témoin pour l'ordre du parallélisme et un pour la passe de repérage | ⏳ |
