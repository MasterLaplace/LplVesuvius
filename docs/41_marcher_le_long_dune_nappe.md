# Marcher le long d'une nappe — et pourquoi « au plus proche » ne marche pas

2026-08-20, nuit. Le maillon manquant de [`39`](39_le_seam_de_correction.md).
Instrument : `analysis/src/suivre_nappe.py` (24 témoins, dont un **témoin négatif**).
Figure : `analysis/src/figure_marche.py`.

---

## 1. La question, telle qu'elle a été posée

> *« Est-ce que tu comptes basiquement prendre un point de départ au centre et te propager
> au point le plus proche pour créer le maillage ? Ou bien t'as d'autres techniques ultra
> stylées ? »*

Réponse courte : **non, et c'est mesuré pourquoi.** « Au plus proche » est la première idée
que tout le monde a, et c'est aussi la manière la plus fiable de finir sur la mauvaise
feuille.

## 2. ⚠⚠ Pourquoi « au plus proche » échoue, sur une figure

![deux facons de suivre une nappe](images/41_deux_marches.png)

Deux spires à **4 voxels** l'une de l'autre — c'est l'écart réel d'un rouleau : 20 à 50 µm
à 7,91 µm le voxel. Un trou de 17 voxels dans la spire de départ, comme un papyrus en a
partout. Même coupe, même point de départ (le cercle blanc), deux méthodes.

| méthode | écart max à sa spire de départ | fin |
|---|---:|---|
| **au plus proche** | **5,94 voxels** — au-delà de la spire voisine | continue, 200 pas |
| **sur la crête** | **0,67 voxel** | **s'arrête au trou**, 31 pas |

**Facteur 9.** Et le point qui compte : le chemin rouge reste **connexe et plausible**. Rien
dans sa forme ne dit qu'il a changé de feuille — seul son rayon le dit. Un contrôle de
régularité ne l'attraperait pas.

⭐ La raison est géométrique et vaut d'être dite en une phrase : **dans un rouleau, le
voisin d'à côté est plus loin que le voisin d'en face.** Un pas le long de la spire fait un
voxel ; la spire suivante est à quatre. Dès qu'il y a un trou de plus de quatre voxels — et
il y en a partout — « le plus proche » est de l'autre côté du vide.

## 3. Ce qui est fait à la place : trois gestes, répétés

1. **la normale locale**, par le **tenseur de structure** — pas par une différence finie. Le
   gradient d'une nappe pointe en travers d'elle, donc le vecteur propre dominant de la
   covariance des gradients est la normale. ⚠ Et il reste défini *sur la crête*, là
   précisément où on marche et où un gradient ponctuel s'effondre ;
2. **recentrer** sur le maximum le long de cette normale, au **sous-voxel** par ajustement
   parabolique. Sans ça, chaque pas arrondit et la marche dérive hors de la nappe en croyant
   la suivre ;
3. **avancer** en reprojetant la direction dans le plan de la nappe. ⚠ Reprojeter à *chaque*
   pas est ce qui fait suivre une courbure — et un rouleau ne fait que tourner.

⭐⭐ **Et la garde qui fait tout le travail** : un recentrage de plus de 2 voxels est
**refusé**. Un vrai suivi corrige des fractions de voxel ; un saut corrige d'un interligne.
La marche s'arrête et **dit laquelle des deux choses lui est arrivée** — fin de nappe, ou
saut refusé.

⚠ **L'ordre de ces deux tests est le diagnostic, et je l'avais écrit à l'envers.** Un grand
recentrage vers une valeur *forte* est un saut sur la voisine ; le même recentrage vers une
valeur *faible* est une nappe qui finit. Tester le saut d'abord étiquetait « saut de nappe »
un simple trou — verdict juste pour une raison fausse, qui envoie chercher un problème
d'empilement là où il n'y a qu'un manque de matière.

## 4. Ce que ça produit : un fichier que l'outil sait relire

La sortie est un `PointCollections`, le format que `vc_grow_seg_from_seed --correct` charge.
⚠ Le format est **lu dans la source** (`core/src/PointCollections.cpp`), pas deviné : un
fichier dont la version ne correspond pas est rejeté en bloc.

⚠⚠ **Et l'ordre des points est signifiant.** `PointCorrection` (`core/src/GrowPatch.cpp`)
trie par identifiant croissant et s'en sert comme d'un **chemin** : le premier point ancre
la collection sur la surface, les suivants sont placés aux emplacements de grille successifs.
Un nuage non ordonné donnerait un fichier valide et un résultat absurde.

⚠ Les coordonnées sont écrites en `(x, y, z)` alors que la marche travaille en `(z, y, x)` :
convention du volume contre convention numpy. Les mélanger tire la surface vers un point
parfaitement faux sans que rien n'ait l'air cassé. Assertion dédiée.

## 5. ⭐⭐ Ce que le traceur fait déjà, et qu'il ne faut pas réécrire

En lisant la source pour le format, une chose s'est imposée : `vc_grow_seg_from_seed`
**n'est pas une propagation**. C'est un problème de **moindres carrés** résolu par Ceres, où
chaque point de la grille porte une famille de résidus (`GrowPatch.cpp:1244`) :

```
DIST · STRAIGHT · DIRECTION · SNAP · NORMAL · NORMAL3DLINE
SDIR · CORRECTION · REFERENCE_RAY · SURFACE_SDT · SPACELINE · PATCH_NORMAL
```

⭐ **`DIRECTION` est la partie « ultra stylée » de la réponse** : le tracer prend des
`DirectionField`, et il en existe trois genres — `horizontal`, `vertical`, `normal`. Un
résidu `FiberDirectionLoss` demande que **l'axe u de la grille suive les fibres
horizontales** et **l'axe v les fibres verticales**. Autrement dit :

> **le papyrus fournit son propre système de coordonnées.** Les deux familles de fibres
> *sont* les axes u, v de la feuille dépliée. On ne choisit pas une paramétrisation, on la lit.

Et `CORRECTION` est exactement le résidu que nos points de passage alimentent : nous
n'ajoutons pas une méthode à côté du solveur, nous **remplissons un terme qu'il attend déjà**.

## 6. ⚠ Ce que ce lot ne fait pas

- **Il n'a rien tracé.** La marche est validée sur des nappes **fabriquées** (cylindre
  courbe, doublé, troué, estompé) — pas encore sur une vraie prédiction. C'est le lot suivant,
  et il coûte du réseau, pas de la conception.
- **Il ne dit pas quelle nappe suivre.** Il suit celle sur laquelle on le pose. Choisir est
  le travail de la graine ([`25`](25_une_graine_choisie_sur_la_planeite.md)), vérifier que la
  trace obtenue suit bien une feuille est celui du test de convergence
  ([`38`](38_ce_qui_bouge_avec_la_fenetre.md)).
- **Il produit des chemins 1D, pas une surface.** Une nappe est 2D. La suite naturelle n'est
  *pas* d'empiler des marches parallèles à la main : c'est de laisser le solveur faire la
  grille, en lui donnant assez de points de passage pour qu'il ne parte pas en travers.
- ⚠ **Il ne résout pas le numéro de spire.** Savoir *sur quel tour* on est est un problème
  **global**, pas local — c'est pourquoi les segments publiés s'appellent `w052`, `w053`, et
  pourquoi `ColPoint` porte un champ `wind_a` et la collection un `winding_is_absolute`.
  Aucune marche locale ne peut y répondre.

---

## Reproduire

```bash
cd inference
uv run python ../analysis/src/suivre_nappe.py --verifier     # 24 témoins
uv run python ../analysis/src/figure_marche.py               # la figure
```
