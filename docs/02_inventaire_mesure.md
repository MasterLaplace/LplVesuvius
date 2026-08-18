# Inventaire mesuré : ce qu'il y a, et ce qu'on peut se permettre

2026-08-16. Tous les chiffres de cette page ont été **mesurés**, pas repris d'une
page de doc. L'outil qui les produit est `tools/s3_size.py` (sortie `--json` pour
rejouer). Rien n'a été téléchargé pour les obtenir.

---

## 1. Le fait qui décide de tout : un volume ne tient pas sur cette machine

```
PHerc0332/segments/          ->  219,1 Mio  (14 objets)
PHerc0332/representations/   ->   19,6 Gio  (308 416 objets)   <- predictions nnUNet
PHerc0332/volumes/           ->    2,1 Tio  (1 081 602 objets)
```

Trois échelles, séparées par deux ordres de grandeur chacune, et c'est cette
hiérarchie qui dicte le plan de travail :

| étage | poids (un rouleau) | dans le budget 100 Go ? |
|---|---|---|
| **surfaces** (`segments/`, tifxyz) | ~220 Mio | oui, largement — 450 rouleaux tiendraient |
| **prédictions** (`representations/`) | ~19,6 Gio | oui, mais un seul rouleau à la fois |
| **volume brut** (`volumes/`, OME-Zarr) | ~2,1 Tio | **pas en entier à pleine résolution** |

### ⚠ Correction : « 2,1 Tio » ne veut PAS dire « pas de 3D »

Formuler l'étage volume comme un mur était une erreur de cadrage, et elle aurait
fait renoncer à toute la 3D pour une mauvaise raison. Un OME-Zarr est
**multi-échelle** : ce dépôt en publie **six niveaux**, et `.zattrs` donne leurs
facteurs exacts (puissances de deux, lus et non supposés). Mesuré sur PHerc0332,
voxel de base 2,399 µm :

| niveau | voxel | poids | tient dans 100 Go ? |
|---|---|---|---|
| 0 | 2,4 µm | ~1,8 Tio | non |
| 1 | 4,8 µm | ~260 Gio | non |
| **2** | **9,6 µm** | **33,0 Gio** | **oui** |
| **3** | **19,2 µm** | **4,9 Gio** | **oui, confortablement** |
| 4 | 38,4 µm | 810 Mio | oui |
| 5 | 76,8 µm | 178 Mio | oui |

**Le niveau 2 est le point d'équilibre** : le rouleau **entier**, en 3D, comme un
seul modèle autonome, pour 33 Gio — un tiers du budget.

Et il est exploitable, pas seulement stockable. Aux échelles physiques du problème
(feuille ≈ 40 µm d'épaisseur, spire voisine à 300 µm et plus) :

| niveau | feuille | écart entre spires | usage |
|---|---|---|---|
| 2 (9,6 µm) | ~4 voxels | ~31 voxels | **géométrie et séparation des spires : oui** |
| 3 (19,2 µm) | ~2 voxels | ~16 voxels | structure grossière, limite basse |
| 4 (38,4 µm) | ~1 voxel | ~8 voxels | **trop grossier** : deux feuilles ne se séparent plus |

Donc : tout ce qui relève de **la forme** — séparer les spires, suivre une feuille,
juger un enroulement, mailler — est faisable sur un modèle 3D complet tenant dans le
budget. Seule la **détection d'encre** exige la pleine résolution, parce qu'elle lit
un contraste de quelques microns ; et c'est précisément l'étage déjà résolu par
d'autres.

> Le mur n'était pas la 3D, c'était la pleine résolution **sur tout le rouleau à la
> fois**. La pyramide sépare les deux, et le travail géométrique tombe du bon côté.

**Un seul volume d'un seul rouleau pèse 2,1 Tio.** Le budget disque est de 100 Go.
La question « quel rouleau télécharger » n'a donc pas de réponse : *aucun*.

Ce n'est pas une contrainte subie, c'est la contrainte qui **désigne le bon plan de
travail**. `windcheck` l'écrit noir sur blanc : *« No GPU, no volume download and no
ML model is involved: the analysis reads only the `tifxyz` surface itself. »* Et
`herculaneum-scroll-tools` comme `vesuvius-automesh` streament depuis S3 sans copie
locale, sur un portable.

> **Règle de travail** : on travaille sur les **surfaces**, pas sur les volumes. Une
> surface tracée pèse ~10 Mio, un volume ~2 Tio — cinq ordres de grandeur. Tout ce
> qui exige le volume entier est hors de portée, et tout ce qui se juge sur la
> surface est à portée de main. C'est la même discipline que le catalogue de
> LplKnowledge : indexer sans rapatrier.

⭐ **Confirmée à un troisième niveau le 2026-08-18** — et c'est elle qui a débloqué la
campagne sur corpus de `12`. Les **volumes de surface** sont publiés en OME-Zarr avec
des chunks `[109, 128, 128]` **non compressés** : un chunk contient toute la colonne de
profondeur d'une fenêtre de 128×128, pour **1,78 Mo et 1,03 s**. La même mesure, faite
en téléchargeant les couches rendues, coûte **32 Go par segment**. Le rapport est de
**18 000**, et il transforme « valider un instrument sur une population » de plusieurs
jours en quelques minutes.

⚠ Le corollaire pratique : avant de télécharger, **chercher si la donnée existe sous une
forme qui se lit par morceaux**. Ici la réponse était oui et personne ne l'avait
regardée.

## 2. Où sont les surfaces déjà tracées

45 échantillons publiés — 35 rouleaux, 10 fragments — et **310 segments** au total.
Mais ils sont extrêmement concentrés :

| échantillon | type | segments | résolution la plus fine |
|---|---|---:|---|
| PHercParis4 | rouleau | **81** | 1,129 µm |
| PHerc0172 | rouleau | **53** | 7,91 µm |
| PHerc0139 | rouleau | **38** | 1,129 µm |
| PHerc0500P2 | fragment | **38** | 0,55 µm |
| PHerc1667 | rouleau | 20 | 1,129 µm |
| PHerc0814 | rouleau | 19 | 1,129 µm |
| PHerc0009B | fragment | 19 | 2,401 µm |
| PHerc1447 | rouleau | 15 | 8,64 µm |
| PHercMANBp | fragment | 11 | 1,129 µm |
| PHerc0343P | fragment | 8 | 2,215 µm |
| PHerc0800 | rouleau | 6 | 8,64 µm |
| PHerc0332 | rouleau | 2 | 2,399 µm |
| **33 autres** | — | **0** | 8,64 à 9,362 µm |

⚠ **33 échantillons sur 45 n'ont aucune surface tracée.** Les quatre premiers en
concentrent 210 sur 310, soit deux tiers.

### Correction d'une hypothèse de travail

L'hypothèse de départ était que les **petits** échantillons sont plus friables, donc
plus durs à dérouler. Les données ne la soutiennent pas, et ce qu'elles montrent est
plus utile : **ce qui sépare un échantillon tracé d'un échantillon vierge est la
résolution de son scan**, pas sa taille ni son état.

Tous les échantillons à 0 segment sont scannés à **8,64 ou 9,362 µm** — des scans de
survol. Tous ceux qui portent beaucoup de segments sont à **1,129 µm** ou mieux.
Aucun échantillon fin n'est à zéro ; aucun échantillon grossier n'est bien tracé.

Ça inverse la lecture du problème : le goulot n'est pas « quel rouleau est le plus
dur », c'est que **presque tout le corpus n'a jamais été touché**, faute d'un scan
assez fin ou faute de temps humain. Et c'est cohérent avec ce que dit le concours :
le coût est l'intervention humaine, pas la difficulté intrinsèque d'un rouleau
particulier.

⚠ À ne pas surinterpréter : la corrélation ne dit pas le sens. Il est tout aussi
plausible qu'on ait **choisi de rescanner finement** les rouleaux jugés prometteurs.
Les deux lectures conduisent au même plan de travail, donc trancher n'est pas
urgent — mais l'écrire évite de croire plus tard qu'on l'avait établi.

## 3. Conséquence sur la couverture de `windcheck`

`windcheck` annonce **284 traces** recensées et terminalement statuées, 274 avec
référence propre. Le corpus publié en compte **310**. Autrement dit son recensement
couvre l'essentiel de ce qui existe — ce n'est pas un échantillon, c'est presque
l'exhaustif.

**Conséquence directe pour nous** : il n'y a rien à gagner à refaire ce recensement.
Ce qui n'est pas fait, et que son README nomme lui-même, c'est de savoir si
**corriger** les défauts recensés change quoi que ce soit en aval.

## 4. Budget retenu

| poste | volume | justification |
|---|---|---|
| Miroir du site | 228 Mio | fait |
| Dépôts | 2,4 Gio | fait |
| Surfaces `tifxyz` (échantillon `windcheck`) | ~409 Mio | 212 fichiers, épinglés par SHA-256 |
| **Total à ce stade** | **~3 Gio** | soit **3 %** du plafond de 100 Go |

On est deux ordres de grandeur sous le budget, et c'est le bon endroit où être : la
première question ne demande pas de données massives, elle demande un instrument.
