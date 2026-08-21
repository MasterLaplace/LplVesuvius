# La boucle de correction tourne — et 318 points ne suffisent pas

2026-08-21. Reproductible : `./tools/lancer.sh --fond tools/boucle_de_correction.sh`.
Verdicts : `docs/boucle_temoin.json`, `docs/boucle_corrige_gen5.json`.

---

## 1. Ce qui est fait pour la première fois

Les maillons de [`39`](39_le_seam_de_correction.md) existaient séparément. Ils sont
désormais **bout à bout** :

```
tracer → marcher la prédiction → écrire les points → --resume --rewind-gen --correct → juger
```

Et le seam **fonctionne mécaniquement** : la reprise corrigée lit le fichier, en tient
compte, et produit une surface différente. Ce n'est pas rien — c'était l'inconnue de `39`.

## 2. Le résultat, apparié

Témoin et corrigé partagent graine (`5842 5839 7386`), volume, paramètres et générations.
**Seuls les points de passage diffèrent.**

| | aire | auto-intersections | écart 41 c | écart 161 c | **α** |
|---|---:|---:|---:|---:|---:|
| témoin | 19,82 cm² | **0** | 187,2 µm | 711,5 µm | **+0,98** |
| corrigé, 318 points | 20,65 cm² | **11 753** | 168,5 µm | 692,8 µm | **+1,03** |
| *segment officiel* | — | — | *17,3 µm* | *17,3 µm* | ***+0,00*** |

![les trois surfaces, la même mesure](images/42_boucle_convergence.png)

⚠⚠ **La correction a changé la trace et n'a pas changé sa nature.** L'aire bouge, les
auto-intersections passent de 0 à 11 753, les écarts baissent d'une dizaine de pour cent —
et **α reste à 1**. La surface suit toujours la fenêtre de rendu : elle est encore posée en
travers de l'empilement.

## 3. Pourquoi — et c'est un rapport de forces, pas un bug

**318 points de passage contre 56 630 points de grille.** Mesuré des deux côtés
(`correction.json` d'une part, la dernière ligne `-> done N` du journal de trace de l'autre) :
la correction porte sur **0,56 %** de la surface, avec un `correction_weight` qui vaut
**1,0 par défaut** — le même ordre que `DIST`, qui s'applique partout.

> Une correction de 318 points est un **coup de pouce local**, pas une réorientation.

⭐ Et ça désigne **deux** leviers sans avoir à deviner, tous deux ajoutés à
`tools/boucle_de_correction.sh` :

1. **`correction_weight`** (`POIDS`, défaut `1 100`) — une clé JSON que `applyJsonWeights`
   accepte (`GrowPatch.cpp:1311`) et qui n'avait jamais été réglée ici ;
2. ⭐⭐ **plus de points** (`SEMIS`, défaut `ligne nappe`). `suivre_nappe.py` gagne un mode
   `--nappe` : une **échine et ses côtes**, chaque côte marchant dans la direction tangente
   perpendiculaire (le produit vectoriel de la normale locale et de la direction d'échine,
   donc encore dans le plan de la nappe). Mesuré sur `PHerc0358`, au même point de départ :

| semis | points | collections | part des 56 630 points de grille |
|---|---:|---:|---:|
| ligne (`--deux-sens`) | 318 | 1 | **0,56 %** |
| **nappe** (échine + 48 côtes) | **5 695** | 49 | **10,1 %** |

⚠ Chaque côte est sa **propre collection**, pas la suite de la précédente :
`PointCorrection` traite une collection comme un chemin et ancre sur son premier point, donc
concaténer les côtes ferait un chemin qui saute d'un bord à l'autre à chaque rangée.

![un morceau de nappe : une echine et ses cotes](images/42_morceau_de_nappe.png)

⚠ Et la couverture est **vérifiée**, pas supposée : sur un cylindre de contrôle, tous les
points restent à moins de 0,32 voxel de la nappe, et les côtes explorent 89 voxels le long
de l'axe que l'échine ne parcourt pas (0,0). Une « couverture 2D » qui recopierait l'échine
serait une ligne épaissie.

### ⚠⚠ Un seuil juste dans une unité, faux dans l'autre — trouvé par la figure

Sur l'image ci-dessus, les côtes ont l'air de **couper les nappes en diagonale**, comme un
peigne. Vérifié plutôt que cru — les chemins voyagent surtout dans le troisième axe, donc la
projection ment encore, exactement comme dans [`41`](41_marcher_le_long_dune_nappe.md) §6bis.
Mais la mesure a trouvé **autre chose** :

| plancher de valeur | côtes traversant un vide | minimum des minima |
|---|---:|---:|
| `0,15` (calibré pour une probabilité) | **4 sur 48** | 0,15 |
| **`1,0` (un voxel de matière)** | **0 sur 48** | **1,01** |

`valeur_min = 0,15` avait été réglé pour une prédiction ramenée dans `[0, 1]`, où il veut
dire « il y a un peu de matière ». Sur une **transformée de distance en voxels**, il veut
dire « je suis à un sixième de voxel du vide » — c'est-à-dire **collée au bord**. La marche
traversait donc des filaments au lieu de s'arrêter, et quatre côtes sur quarante-huit
partaient sur la nappe voisine.

⭐ `plancher_pour(bloc)` choisit désormais le plancher d'après les **unités du champ** (au-delà
de 1,5 de crête, c'est une distance, pas une probabilité). Coût de la correction : 12 points
sur 5 707. Même famille que la borne de lag choisie pour la commodité — **un seuil est
attaché à une unité, et changer le champ change l'unité.**

## 4. ⚠ Ce que ce résultat retire à une hypothèse séduisante

[`38`](38_ce_qui_bouge_avec_la_fenetre.md) posait qu'une coupe radiale **ne peut pas** se
croiser elle-même, et donc que nos traces propres étaient peut-être les mauvaises. Ici, une
trace passe de **0 à 11 753 auto-intersections** et son α **ne s'améliore pas** (+0,98 →
+1,03).

⚠ Beaucoup de croisements n'est donc **ni** un symptôme de bon suivi **ni** son contraire :
c'est une propriété indépendante. L'hypothèse qui inverse perd son dernier appui indirect —
il restait `essai_ng2` (α = +0,65 avec 112 139 croisements), et un seul point ne fait pas
une tendance.

## 5. Ce que ça ne dit pas

- **Que les points de passage soient faux.** [`41`](41_marcher_le_long_dune_nappe.md) mesure
  que la marche suit une nappe sur ≈ 2,4 mm **sans traverser un seul vide**. Ce sont des
  points sur une feuille ; ils sont simplement trop peu nombreux et trop peu pondérés.
- **Que `--rewind-gen 5` soit le bon rembobinage** — et la mesure penche déjà dans l'autre
  sens. Rembobiner **moins** dérange moins et fait mieux :

| | croisements | écart 41 c | écart 161 c | **α** |
|---|---:|---:|---:|---:|
| témoin | 0 | 187,2 µm | 711,5 µm | +0,98 |
| corrigé, `--rewind-gen 5` | 11 753 | 168,5 µm | 692,8 µm | +1,03 |
| corrigé, **`--rewind-gen 40`** | **18** | **154,5 µm** | **519,6 µm** | **+0,89** |

  ⚠ α passe de 0,98 à 0,89 et l'écart à 161 couches baisse de **27 %** — le plus grand
  mouvement qu'un levier ait produit ici. Mais deux fenêtres et 0,09 d'écart en α, ça ne
  fait pas une tendance : à confirmer par le balayage, pas à annoncer.
- **Que la cause soit trouvée.** Trois leviers de données restent éteints chez nous
  (`41` §6ter), et un quatrième existe dont je ne sais pas dire s'il tire.

---

## Reproduire

```bash
./tools/lancer.sh --fond tools/boucle_de_correction.sh      # la boucle entière, appariée

# la figure, depuis les verdicts eux-mêmes — jamais des nombres recopiés
cd experiments && uv run python ../analysis/src/test_convergence.py \
  --serie "31:17.28,81:17.30" --nom "segment officiel (bonne surface)" \
  --depuis "../docs/boucle_temoin.json=témoin, sans correction" \
  --depuis "../docs/boucle_corrige_gen5.json=corrigé, 318 points de passage" \
  --json ../docs/boucle_convergence.json
cd ../inference && uv run python ../analysis/src/figure_convergence.py \
  --entree ../docs/boucle_convergence.json --sortie ../docs/images/42_boucle_convergence.png
```
