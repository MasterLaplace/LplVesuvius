# Le seam de correction — où l'humain se branche, et donc où on le remplace

2026-08-20, soir. `31` §8 pose la question qui vaut le prix :

> *« Qu'est-ce qui remplace l'humain qui corrige le transfert de spire à spire ? »*

Elle a une réponse concrète, et elle était dans l'aide de l'outil depuis le début.

---

## 1. L'API existe, et elle est publique

```
vc_grow_seg_from_seed
  --resume arg               Path to a tifxyz surface to resume from
  --rewind-gen arg           Generation to rewind to
  --correct arg              JSON file with point-based corrections for resume mode
  --resume-opt arg           Resume optimization option (skip, local, global)
  --resume-generations arg   Number of additional generations to grow from current
```

C'est le *« wrap by wrap copy tool »* que le papier de juin 2026 décrit, et **c'est là que
ses ~25 heures par spire sont dépensées**. Trois faits lus dans la source
(`apps/src/vc_grow_seg_from_seed.cpp`, `core/src/GrowPatch.cpp`) :

- `--correct` charge un **`PointCollections`** — le format *point collection* de VC3D, celui
  que [`31`](31_roadmap.md) §4 nommait déjà comme la bonne sortie pour nos instruments ;
- une correction est **une liste de points 3D** (plus un ancrage 2D optionnel dans la
  grille), vers lesquels le traceur tire la surface pendant qu'il la refait pousser ;
- ⚠ `--correct` **exige** `--resume` : on ne corrige pas une trace, on la **re-pousse** en
  lui donnant des points de passage.

⚠ Et un détail qui dit la nature de l'outil : dès qu'il y a des corrections, la surface est
rechargée avec `SURF_LOAD_IGNORE_MASK`. Le masque d'une trace corrigée est donc jeté — ce
qui n'a de sens que si l'on considère qu'il porte des décisions qu'on est en train de
révoquer.

## 2. ⭐⭐ Ce que ça change pour nous

La chaîne complète devient nommable, et chaque maillon existe déjà **sauf un** :

| étage | ce qu'on a |
|---|---|
| tracer | ✅ `vc_grow_seg_from_seed` |
| **juger** | ✅ [`38`](38_ce_qui_bouge_avec_la_fenetre.md) — sans seuil, sans vérité terrain |
| **dire où la surface aurait dû passer** | ❌ **c'est le trou** |
| appliquer | ✅ `--resume --rewind-gen --correct` |
| revérifier | ✅ le même test de convergence |

⭐ **Le trou est étroit et bien défini** : produire, pour une trace donnée, une liste de
points 3D par lesquels elle aurait dû passer. Ce n'est plus « corriger une trace » — c'est
« écrire un fichier de points ».

## 3. ⚠⚠ Et pourquoi ce n'est pas fait ce soir

L'instrument de profondeur sait dire *où est la matière le long de la normale* — c'est
exactement la forme d'un point de correction. Mais sur nos traces il ne trouve **rien** :
`part_plates = 1,000`, c'est-à-dire **aucune structure de profondeur dans aucune fenêtre**,
et dans les deux sens de normale.

> Une surface couchée dans le plan des spires n'a pas de feuille « au-dessus » ni
> « en-dessous » : sa normale reste dans la même matière. **Il n'y a rien vers quoi tirer.**

⭐ La sortie possible est donc de **corriger depuis la prédiction et non depuis le volume** :
`src/nappe/sonder_point.py` mesure qu'au point de départ la prédiction publiée a une
planarité de **0,993** — elle sait parfaitement où sont les nappes, là où le volume brut ne
le dit qu'à qui est déjà proche. C'est le prochain lot, et c'est la première fois de la
journée qu'un lot est un **constructeur** et non un diagnostic.

```
uv run python src/nappe/sonder_point.py \
  PHerc1447/representations/predictions/surfaces/20250521151220-surface-20260413222639-surface-m7-L0-th0.2.zarr \
  --xyz 4682 2740 13350 --level 0 --bloc 8
```

⚠ Vérifié le 2026-09-05, la commande rend les mêmes chiffres :

| | valeur |
|---|---:|
| occupation de la cellule | 0,457 |
| **planarité de la cellule** | **0,993** |
| occupation du chunk, médiane | 0,156 — part saturée (> 0,80) **0,0 %** |
| planarité du chunk, médiane | 0,991 |

⚠⚠ **La planarité seule ne suffirait pas à conclure**, et c'est l'occupation qui le dit : à
1,000 tout serait « surface », donc il n'y aurait aucun gradient à suivre et un traceur y
partirait dans n'importe quelle direction. À 0,457 dans la cellule et 0,156 de médiane sur le
chunk, avec **aucune** fenêtre saturée, la prédiction porte une structure de feuille et non un
bloc plein. ⚠ Les deux seuils (0,02 et 0,80) sont ceux de `trouver_graine.py`, c'est-à-dire
ceux qui ont servi à **choisir** nos graines : en prendre d'autres ici introduirait une
troisième échelle et rendrait la sonde incomparable à la sélection.

## 4. ⚠ Ce que ce document ne dit pas

- **Il n'a rien fait tourner.** Aucune correction n'a été écrite ni appliquée ; ce document
  établit *que le seam existe et quelle forme il prend*, pas qu'il marche pour nous.
- **Il ne dit pas que les segments officiels sont hand-corrigés.** C'est plausible — l'API
  existe, le papier décrit 25 h par spire — mais leur métadonnée ne l'enregistre pas, et
  supposer une provenance est exactement ce que [`36`](36_lorigine_de_la_pile.md) a payé.
- ⚠ **`--rewind-gen` demande de choisir une génération**, donc de savoir *à partir d'où* la
  trace a divergé. Notre test de convergence rend un verdict sur une trace entière, pas une
  génération. C'est une deuxième pièce manquante, plus petite que la première.

## La boucle entière, écrite

Le chaînon manquant est construit ([`41`](41_marcher_le_long_dune_nappe.md)) et
`src/outils/boucle_de_correction.sh` met les maillons bout à bout pour la première fois :
tracer → marcher la prédiction → écrire les points → `--resume --rewind-gen --correct` →
juger au test de convergence, contre un témoin **apparié** (même graine, même volume,
mêmes paramètres, seuls les points de passage diffèrent).

⚠ `--rewind-gen` demande toujours de choisir une génération, et notre juge porte sur une
trace entière. On **balaie** donc quelques valeurs plutôt que d'en deviner une : une trace
de ce rouleau coûte une vingtaine de secondes, le balayage est moins cher que le
raisonnement.

⚠ Une reprise qui ne produit aucun maillage est rapportée comme **résultat sur le seam**,
pas comme panne du script — c'est précisément ce qu'il faut savoir.

## Reproduire

```bash
./src/outils/lancer.sh --fond src/outils/boucle_de_correction.sh   # la boucle entière, appariée
vc_grow_seg_from_seed --help          # les cinq options de reprise
grep -n "corrections" data/repos/villa/volume-cartographer/apps/src/vc_grow_seg_from_seed.cpp
sed -n '560,600p' data/repos/villa/volume-cartographer/core/src/GrowPatch.cpp   # PointCorrection
```
